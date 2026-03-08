# 🔬 Smart Skin Care Advisor

> An AI-powered skin condition detection system using a Convolutional Neural Network (CNN) built with PyTorch, FastAPI, and a modern glassmorphism web interface.

---

## 📋 Table of Contents
- [Overview](#overview)
- [How the CNN Works](#how-the-cnn-works)
- [Project Structure](#project-structure)
- [Dataset Format](#dataset-format)
- [How to Train the Model](#how-to-train-the-model)
- [How to Run Locally](#how-to-run-locally)
- [API Endpoints](#api-endpoints)
- [Skin Conditions Detected](#skin-conditions-detected)

---

## Overview

The Smart Skin Care Advisor analyses skin images uploaded by the user and predicts skin conditions using a CNN. It provides:

- **Condition detection** — identifies among 7 skin conditions
- **Confidence score** — probability percentage for each prediction
- **Personalised recommendations** — tailored skincare tips and ingredient advice
- **Prediction history** — stored locally in SQLite

---

## How the CNN Works

The model is a 3-block Convolutional Neural Network:

```
Input (224×224 RGB)
    ↓
Conv2D (3→32) + BatchNorm + ReLU + MaxPool2×2 + Dropout
    ↓
Conv2D (32→64) + BatchNorm + ReLU + MaxPool2×2 + Dropout
    ↓
Conv2D (64→128) + BatchNorm + ReLU + MaxPool2×2 + Dropout
    ↓
Flatten → Linear(512) → ReLU → Dropout
    ↓
Linear(128) → ReLU → Dropout
    ↓
Linear(7) → Softmax
    ↓
Output: Predicted class + confidence scores
```

**Input size:** 224 × 224 pixels  
**Optimizer:** Adam (lr=1e-3, weight_decay=1e-4)  
**Scheduler:** StepLR (step=10, gamma=0.5)  
**Augmentation:** Random flip, rotation, color jitter  

---

## Project Structure

```
smart-skincare-advisor/
│
├── frontend/               # HTML/CSS/JS user interface
│   ├── index.html          # Home page
│   ├── upload.html         # Image upload page
│   ├── result.html         # Prediction result page
│   ├── css/
│   │   └── style.css       # Global dark glassmorphism styles
│   └── js/
│       └── upload.js       # Drag-drop upload + API submission
│
├── backend/                # FastAPI Python backend
│   ├── main.py             # FastAPI app + routes
│   ├── prediction_service.py  # ML inference + recommendations + DB
│   ├── database.py         # SQLAlchemy SQLite ORM
│   └── requirements.txt    # Python dependencies
│
├── ml/                     # Machine learning module
│   ├── model.py            # CNN architecture (SkinCareCNN)
│   ├── train.py            # Training script
│   ├── predict.py          # Inference helper (SkinPredictor)
│   └── dataset_loader.py   # DataLoader with augmentation
│
├── dataset/                # Training images (add your own)
│   ├── acne/
│   ├── eczema/
│   ├── melanoma/
│   ├── psoriasis/
│   ├── normal_skin/
│   ├── dark_spots/
│   └── dry_skin/
│
├── notebooks/
│   └── training.ipynb      # Jupyter training + evaluation notebook
│
├── scripts/
│   ├── setup_linux.sh      # One-command Linux setup + launch
│   └── setup_windows.ps1   # One-command Windows setup + launch
│
└── README.md
```

---

## Dataset Format

Place skin images in the corresponding class folders under `dataset/`:

```
dataset/
  acne/
    img001.jpg
    img002.png
    ...
  eczema/
    img001.jpg
    ...
  (etc.)
```

- **Supported formats:** JPEG, PNG
- **Recommended images per class:** 200–1000
- **Recommended sources:** [ISIC Archive](https://www.isic-archive.com/), [DermNet](https://dermnetnz.org/), Kaggle skin datasets

---

## How to Train the Model

### Option 1 — Terminal (recommended)

```bash
cd smart-skincare-advisor/backend
pip install -r requirements.txt

cd ../ml
python train.py --dataset ../dataset --epochs 30 --batch_size 32 --lr 1e-3 --output skin_cnn.pth
```

The best model checkpoint is saved to `ml/skin_cnn.pth` automatically.

### Option 2 — Jupyter Notebook

```bash
pip install jupyter matplotlib seaborn
cd notebooks
jupyter notebook training.ipynb
```

Run all cells in order — the notebook includes:
- Dataset visualisation
- Full training loop with progress output
- Loss/accuracy curve plots
- Confusion matrix

---

## How to Run Locally

### Quick Start (Linux/macOS)

```bash
cd smart-skincare-advisor
bash scripts/setup_linux.sh
```

### Quick Start (Windows PowerShell)

```powershell
cd smart-skincare-advisor
.\scripts\setup_windows.ps1
```

### Manual Steps

```bash
# 1. Create and activate virtual environment
cd smart-skincare-advisor/backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 4. Open browser
#    http://localhost:8000
```

> **Note:** If `ml/skin_cnn.pth` does not exist, the model runs with random weights. Train the model first for meaningful predictions.

---

## API Endpoints

| Method | Endpoint   | Description                          |
|--------|------------|--------------------------------------|
| GET    | `/`        | Home page (HTML)                     |
| GET    | `/upload`  | Upload page (HTML)                   |
| GET    | `/result`  | Result page (HTML)                   |
| POST   | `/predict` | Upload image → JSON prediction       |
| GET    | `/history` | Last 20 predictions from SQLite      |
| GET    | `/health`  | Health check                         |
| GET    | `/classes` | List of supported condition classes  |

### 💻 Testing the API via Command Line

**Linux / macOS (curl):**
```bash
curl -X POST -F "file=@./sample_img/acne.png" http://localhost:8001/predict
```

**Windows (PowerShell):**
```powershell
Invoke-RestMethod -Uri "http://localhost:8001/predict" -Method Post -Form @{file=(Get-Item ".\sample_img\acne.png")} | ConvertTo-Json -Depth 5
```
*(Or if using Windows `curl.exe`):*
```powershell
curl.exe -X POST -F "file=@.\sample_img\acne.png" http://localhost:8001/predict
```

### Example `/predict` response

```json
{
  "id": 1,
  "predicted_class": "acne",
  "confidence": 87.34,
  "recommendation": {
    "summary": "Acne detected",
    "tips": ["Use a salicylic acid or benzoyl peroxide cleanser..."],
    "ingredients_to_use": ["Salicylic acid", "Niacinamide"],
    "ingredients_to_avoid": ["Heavy oils", "Comedogenic ingredients"]
  },
  "all_scores": [
    {"class": "acne", "confidence": 87.34},
    {"class": "normal_skin", "confidence": 5.12},
    ...
  ],
  "created_at": "2024-03-07T17:30:00"
}
```

---

## Skin Conditions Detected

| Class         | Description                                     |
|---------------|-------------------------------------------------|
| `acne`        | Inflammatory and non-inflammatory acne lesions  |
| `eczema`      | Atopic dermatitis patches                       |
| `melanoma`    | Suspicious pigmented lesions (urgent review)    |
| `psoriasis`   | Scaly plaque skin disease                       |
| `normal_skin` | No condition detected                           |
| `dark_spots`  | Hyperpigmentation / sun damage                  |
| `dry_skin`    | Moisture-depleted, flaking skin                 |

---

## Tech Stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Frontend   | HTML5 · CSS3 · Vanilla JavaScript |
| Backend    | Python · FastAPI · Uvicorn        |
| ML         | PyTorch · Torchvision             |
| Image Proc | OpenCV · Pillow                   |
| Database   | SQLite · SQLAlchemy               |

---

## ⚠️ Disclaimer

This tool is for **educational and informational purposes only**. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified dermatologist for skin concerns.

---

*Smart Skin Care Advisor — Final Year College Project*
