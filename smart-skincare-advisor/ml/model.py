"""
CNN Model for Skin Condition Classification
Architecture: 2x Conv-ReLU-MaxPool blocks → Flatten → FC → Softmax
"""

import torch
import torch.nn as nn


class SkinCareCNN(nn.Module):
    """
    Convolutional Neural Network for skin disease classification.
    Input: (batch, 3, 224, 224) RGB image
    Output: (batch, num_classes) logits
    """

    NUM_CLASSES = 7
    CLASS_NAMES = [
        "acne",
        "dark_spots",
        "dry_skin",
        "eczema",
        "melanoma",
        "normal_skin",
        "psoriasis",
    ]

    def __init__(self, num_classes: int = NUM_CLASSES):
        super(SkinCareCNN, self).__init__()

        # ── Block 1 ──────────────────────────────────────────────────────────
        self.conv_block1 = nn.Sequential(
            nn.Conv2d(in_channels=3, out_channels=32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),   # 224 → 112
            nn.Dropout2d(p=0.1),
        )

        # ── Block 2 ──────────────────────────────────────────────────────────
        self.conv_block2 = nn.Sequential(
            nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),   # 112 → 56
            nn.Dropout2d(p=0.1),
        )

        # ── Block 3 ──────────────────────────────────────────────────────────
        self.conv_block3 = nn.Sequential(
            nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),   # 56 → 28
            nn.Dropout2d(p=0.2),
        )

        # ── Classifier Head ───────────────────────────────────────────────────
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * 28 * 28, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.5),
            nn.Linear(512, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.3),
            nn.Linear(128, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.conv_block1(x)
        x = self.conv_block2(x)
        x = self.conv_block3(x)
        x = self.classifier(x)
        return x  # raw logits; apply softmax externally for inference


def get_model(num_classes: int = SkinCareCNN.NUM_CLASSES, pretrained_path: str = None) -> SkinCareCNN:
    """Instantiate the model and optionally load saved weights."""
    model = SkinCareCNN(num_classes=num_classes)
    if pretrained_path:
        state = torch.load(pretrained_path, map_location="cpu")
        model.load_state_dict(state)
        print(f"[model] Loaded weights from {pretrained_path}")
    return model


if __name__ == "__main__":
    # Quick sanity check
    m = get_model()
    dummy = torch.randn(2, 3, 224, 224)
    out = m(dummy)
    print(f"Output shape: {out.shape}")  # → (2, 7)
    print("Model OK ✓")
