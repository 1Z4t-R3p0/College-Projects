"""
FastAPI main application — serves the frontend, exposes prediction and history APIs,
and mounts static files.

Run:
    cd backend
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Optional

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

# ── Local imports ─────────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
from database import get_db, init_db
from prediction_service import get_history, run_prediction

# ── App setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Smart Skin Care Advisor API",
    description="AI-powered skin condition detection and personalised skincare recommendations.",
    version="1.0.0",
)

# Allow the HTML pages (served from any origin in dev mode) to reach the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (frontend)
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

if FRONTEND_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

# Initialise DB on startup
@app.on_event("startup")
async def startup_event():
    init_db()


# ── HTML page routes ──────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse, summary="Home page")
async def home():
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return index_path.read_text(encoding="utf-8")
    return HTMLResponse("<h1>Smart Skin Care Advisor</h1><p><a href='/upload'>Upload Image</a></p>")


@app.get("/upload", response_class=HTMLResponse, summary="Upload page")
async def upload_page():
    upload_path = FRONTEND_DIR / "upload.html"
    if upload_path.exists():
        return upload_path.read_text(encoding="utf-8")
    raise HTTPException(status_code=404, detail="upload.html not found")


@app.get("/result", response_class=HTMLResponse, summary="Result page")
async def result_page():
    result_path = FRONTEND_DIR / "result.html"
    if result_path.exists():
        return result_path.read_text(encoding="utf-8")
    raise HTTPException(status_code=404, detail="result.html not found")


# ── API routes ────────────────────────────────────────────────────────────────

@app.post("/predict", summary="Upload a skin image and get a prediction")
async def predict(
    file: UploadFile = File(...),
    db:   Session    = Depends(get_db),
):
    """
    Accept a skin image (JPEG / PNG) and return:
    - `predicted_class`  — detected skin condition
    - `confidence`       — confidence percentage (0–100)
    - `recommendation`   — tailored skincare advice
    - `all_scores`       — probability for every class
    """
    # Validate content type
    allowed = {"image/jpeg", "image/png", "image/jpg", "image/webp"}
    if file.content_type not in allowed:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported file type '{file.content_type}'. Upload JPEG or PNG.",
        )

    image_bytes = await file.read()
    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        result = run_prediction(image_bytes, filename=file.filename, db=db)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}")

    return result


@app.get("/history", summary="Retrieve past prediction results")
async def history(limit: int = 20, db: Session = Depends(get_db)):
    """Return the most recent skin condition predictions (newest first)."""
    return get_history(db, limit=limit)


@app.get("/health", summary="Health check")
async def health():
    return {"status": "ok", "message": "Smart Skin Care Advisor is running"}


@app.get("/classes", summary="List supported skin condition classes")
async def classes():
    from predict import CLASS_NAMES as CN
    return {"classes": CN}
