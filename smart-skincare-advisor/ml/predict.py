"""
Inference helper — loads the trained model and predicts a single image.

Usage (standalone):
    python predict.py path/to/image.jpg --model skin_cnn.pth
"""

import argparse
import io
import os
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image

# Local imports
import sys
sys.path.insert(0, str(Path(__file__).parent))
from model import get_model, SkinCareCNN
from dataset_loader import PREDICT_TRANSFORMS


# ── Constants ─────────────────────────────────────────────────────────────────

DEFAULT_MODEL_PATH = Path(__file__).parent / "skin_cnn.pth"
CLASS_NAMES        = SkinCareCNN.CLASS_NAMES   # sorted alphabetically


# ── Core predictor ────────────────────────────────────────────────────────────

class SkinPredictor:
    """Thread-safe predictor wrapper around the CNN model."""

    def __init__(self, model_path: str = None, device: str = None):
        self.device = torch.device(
            device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        )
        model_path = model_path or DEFAULT_MODEL_PATH

        self.model = get_model(num_classes=len(CLASS_NAMES))

        if Path(model_path).exists():
            state = torch.load(str(model_path), map_location=self.device)
            self.model.load_state_dict(state)
            print(f"[predict] Loaded weights: {model_path}")
        else:
            print(f"[predict] WARNING – model file not found at '{model_path}'. "
                  "Running with random weights (train the model first).")

        self.model.to(self.device)
        self.model.eval()

    # ── Public API ────────────────────────────────────────────────────────────

    def predict_pil(self, pil_image: Image.Image) -> Dict:
        """Run inference on a PIL image and return a structured result dict."""
        tensor = PREDICT_TRANSFORMS(pil_image.convert("RGB")).unsqueeze(0).to(self.device)

        with torch.no_grad():
            logits      = self.model(tensor)
            probs       = F.softmax(logits, dim=1).squeeze(0).cpu().numpy()

        top_idx        = int(np.argmax(probs))
        top_class      = CLASS_NAMES[top_idx]
        confidence     = float(probs[top_idx]) * 100

        all_scores: List[Dict] = [
            {"class": CLASS_NAMES[i], "confidence": round(float(probs[i]) * 100, 2)}
            for i in np.argsort(probs)[::-1]
        ]

        return {
            "predicted_class": top_class,
            "confidence":      round(confidence, 2),
            "all_scores":      all_scores,
        }

    def predict_bytes(self, image_bytes: bytes) -> Dict:
        """Run inference on raw image bytes (e.g. from file upload)."""
        pil_image = Image.open(io.BytesIO(image_bytes))
        return self.predict_pil(pil_image)

    def predict_path(self, image_path: str) -> Dict:
        """Run inference on an image file path."""
        pil_image = Image.open(image_path)
        return self.predict_pil(pil_image)


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="Skin condition predictor")
    p.add_argument("image",  type=str,              help="Path to image")
    p.add_argument("--model",type=str, default=None, help="Path to .pth weights")
    return p.parse_args()


if __name__ == "__main__":
    args      = parse_args()
    predictor = SkinPredictor(model_path=args.model)
    result    = predictor.predict_path(args.image)
    print(f"\nPrediction : {result['predicted_class']}")
    print(f"Confidence : {result['confidence']:.2f}%")
    print("\nAll scores:")
    for s in result["all_scores"]:
        bar = "█" * int(s["confidence"] / 5)
        print(f"  {s['class']:>12} : {s['confidence']:>6.2f}%  {bar}")
