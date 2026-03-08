#!/usr/bin/env bash
# =============================================================
# Smart Skin Care Advisor — Linux/macOS Setup Script
# =============================================================
set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$PROJECT_ROOT/.venv"

echo "=================================================="
echo "  Smart Skin Care Advisor — Setup"
echo "=================================================="
echo "Project root: $PROJECT_ROOT"

# ── 1. Python check ──────────────────────────────────────────
echo ""
echo "[1/5] Checking Python 3.9+ ..."
if ! command -v python3 &>/dev/null; then
  echo "ERROR: python3 not found. Install Python 3.9 or higher first."
  exit 1
fi
PYTHON_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "      Python $PYTHON_VER found → OK"

# ── 2. Create virtual environment ────────────────────────────
echo ""
echo "[2/5] Creating virtual environment at $VENV_DIR ..."
if [ -d "$VENV_DIR" ]; then
  echo "      .venv already exists — skipping creation."
else
  python3 -m venv "$VENV_DIR"
  echo "      .venv created."
fi

# Activate
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
echo "      Virtual environment activated."

# ── 3. Install dependencies ──────────────────────────────────
echo ""
echo "[3/5] Installing Python dependencies ..."
pip install --upgrade pip --quiet
pip install -r "$PROJECT_ROOT/backend/requirements.txt"
echo "      Dependencies installed."

# ── 4. Create dataset placeholder structure ───────────────────
echo ""
echo "[4/5] Ensuring dataset folder structure ..."
for cls in acne eczema melanoma psoriasis normal_skin dark_spots dry_skin; do
  mkdir -p "$PROJECT_ROOT/dataset/$cls"
  # Create a README inside each class folder
  if [ ! -f "$PROJECT_ROOT/dataset/$cls/.gitkeep" ]; then
    touch "$PROJECT_ROOT/dataset/$cls/.gitkeep"
  fi
done
echo "      Dataset subfolders ready."

# ── 5. Start FastAPI server ───────────────────────────────────
echo ""
echo "[5/5] Starting FastAPI development server ..."
echo "      Open http://localhost:8000 in your browser."
echo "      Press Ctrl+C to stop."
echo ""
cd "$PROJECT_ROOT/backend"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
