"""
Prediction service — bridges the ML predictor and the recommendation engine,
and persists results to the database.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

# ── Make ml/ importable ───────────────────────────────────────────────────────
ML_DIR = Path(__file__).parent.parent / "ml"
sys.path.insert(0, str(ML_DIR))

from predict import SkinPredictor
from database import PredictionRecord

# ── Recommendation engine ─────────────────────────────────────────────────────

RECOMMENDATIONS: Dict[str, Dict] = {
    "acne": {
        "summary": "Acne detected",
        "tips": [
            "Use a salicylic acid or benzoyl peroxide cleanser twice daily.",
            "Apply a non-comedogenic moisturiser.",
            "Avoid touching your face and change pillowcases regularly.",
            "Consider a topical retinoid at night (retinol 0.025%).",
            "Consult a dermatologist if cysts or nodules are present.",
        ],
        "ingredients_to_use":  ["Salicylic acid", "Benzoyl peroxide", "Niacinamide", "Zinc"],
        "ingredients_to_avoid": ["Heavy oils", "Comedogenic ingredients", "Alcohol-based toners"],
    },
    "eczema": {
        "summary": "Eczema (Atopic Dermatitis) detected",
        "tips": [
            "Apply a fragrance-free, hypoallergenic moisturiser immediately after bathing.",
            "Use lukewarm (not hot) water during showers.",
            "Wear soft cotton clothing and avoid wool or synthetic fibres.",
            "Identify and avoid personal triggers (dust mites, certain foods, stress).",
            "Seek medical advice for prescription topical corticosteroids if needed.",
        ],
        "ingredients_to_use":  ["Ceramides", "Colloidal oatmeal", "Hyaluronic acid", "Shea butter"],
        "ingredients_to_avoid": ["Fragrance", "Essential oils", "Sodium lauryl sulfate", "Alcohol"],
    },
    "melanoma": {
        "summary": "Possible Melanoma — Seek medical attention immediately",
        "tips": [
            "⚠️ Consult a board-certified dermatologist or oncologist urgently.",
            "Do NOT use over-the-counter products on the affected area.",
            "Apply broad-spectrum SPF 50+ sunscreen and avoid sun exposure.",
            "Document the lesion (size, colour changes) with photos for your doctor.",
            "Early detection is critical — do not delay medical evaluation.",
        ],
        "ingredients_to_use":  ["SPF 50+ broad-spectrum sunscreen"],
        "ingredients_to_avoid": ["Any irritating actives until medically cleared"],
    },
    "psoriasis": {
        "summary": "Psoriasis detected",
        "tips": [
            "Moisturise thickened patches with rich emollients multiple times daily.",
            "Use medicated shampoos containing coal tar or salicylic acid for scalp psoriasis.",
            "Apply prescription-strength topical corticosteroids as directed by a doctor.",
            "Avoid scratching; keep nails short to reduce skin damage.",
            "Manage stress levels; psoriasis often flares with psychological stress.",
        ],
        "ingredients_to_use":  ["Coal tar", "Salicylic acid", "Calcipotriol", "Heavy emollients"],
        "ingredients_to_avoid": ["Harsh exfoliants", "Strong fragrance", "Hot water"],
    },
    "normal_skin": {
        "summary": "Skin appears healthy and normal",
        "tips": [
            "Continue your current routine — it's working!",
            "Cleanse gently morning and night with a balanced pH cleanser.",
            "Apply broad-spectrum SPF 30+ sunscreen every morning.",
            "Use a lightweight antioxidant serum (vitamin C) in the morning.",
            "Hydrate from within by drinking 8 glasses of water daily.",
        ],
        "ingredients_to_use":  ["Vitamin C", "SPF 30+", "Niacinamide", "Hyaluronic acid"],
        "ingredients_to_avoid": ["Over-exfoliating", "Heavy occlusive creams"],
    },
    "dark_spots": {
        "summary": "Hyperpigmentation / Dark Spots detected",
        "tips": [
            "Apply a vitamin C serum (10–20%) every morning on clean skin.",
            "Use a broad-spectrum SPF 50 sunscreen; UV exposure worsens dark spots.",
            "Introduce niacinamide (5%) to inhibit melanin transfer.",
            "Consider an alpha-arbutin or kojic acid serum at night.",
            "Be patient — fading takes 8–12 weeks of consistent use.",
        ],
        "ingredients_to_use":  ["Vitamin C", "Niacinamide", "Alpha-arbutin", "Kojic acid", "SPF 50+"],
        "ingredients_to_avoid": ["Unprotected sun exposure", "Harsh scrubs that cause inflammation"],
    },
    "dry_skin": {
        "summary": "Dry skin detected",
        "tips": [
            "Use a creamy, soap-free cleanser to avoid stripping natural oils.",
            "Apply hyaluronic acid serum to damp skin, then seal with a rich moisturiser.",
            "Use facial oil (rosehip, jojoba) as the final step in your PM routine.",
            "Run a humidifier at home, especially during winter months.",
            "Drink adequate water and eat omega-3 rich foods (salmon, walnuts).",
        ],
        "ingredients_to_use":  ["Hyaluronic acid", "Glycerin", "Ceramides", "Squalane", "Shea butter"],
        "ingredients_to_avoid": ["Alcohol-based toners", "Harsh exfoliating acids", "Foaming sulfate cleansers"],
    },
}

DEFAULT_RECOMMENDATION = {
    "summary": "Skin condition detected",
    "tips": ["Consult a certified dermatologist for a professional assessment."],
    "ingredients_to_use":  [],
    "ingredients_to_avoid": [],
}


def get_recommendation(skin_class: str) -> Dict:
    return RECOMMENDATIONS.get(skin_class, DEFAULT_RECOMMENDATION)


# ── Predictor singleton ───────────────────────────────────────────────────────

_predictor: Optional[SkinPredictor] = None

def get_predictor() -> SkinPredictor:
    global _predictor
    if _predictor is None:
        model_path = ML_DIR / "skin_cnn.pth"
        _predictor = SkinPredictor(model_path=str(model_path))
    return _predictor


# ── Service function ──────────────────────────────────────────────────────────

def run_prediction(image_bytes: bytes, filename: str, db: Session) -> Dict:
    """
    Run the full prediction pipeline:
      1. ML inference
      2. Recommendation lookup
      3. Persist to DB
      4. Return combined result
    """
    predictor = get_predictor()
    ml_result = predictor.predict_bytes(image_bytes)

    predicted_class = ml_result["predicted_class"]
    confidence      = ml_result["confidence"]
    all_scores      = ml_result["all_scores"]
    recommendation  = get_recommendation(predicted_class)

    # Persist
    record = PredictionRecord(
        filename        = filename,
        predicted_class = predicted_class,
        confidence      = confidence,
        recommendation  = recommendation["summary"],
        all_scores_json = json.dumps(all_scores),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "id":               record.id,
        "predicted_class":  predicted_class,
        "confidence":       confidence,
        "recommendation":   recommendation,
        "all_scores":       all_scores,
        "created_at":       record.created_at.isoformat(),
    }


def get_history(db: Session, limit: int = 50) -> List[Dict]:
    """Return the last `limit` predictions from the database."""
    records = (
        db.query(PredictionRecord)
        .order_by(PredictionRecord.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id":              r.id,
            "filename":        r.filename,
            "predicted_class": r.predicted_class,
            "confidence":      r.confidence,
            "recommendation":  r.recommendation,
            "created_at":      r.created_at.isoformat(),
        }
        for r in records
    ]
