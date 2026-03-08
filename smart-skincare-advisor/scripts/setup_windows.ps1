# =============================================================
# Smart Skin Care Advisor — Windows PowerShell Setup Script
# =============================================================
# Run from the project root:
#   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
#   .\scripts\setup_windows.ps1
# =============================================================

$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path "$PSScriptRoot\..").Path
$VenvDir     = Join-Path $ProjectRoot ".venv"

Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "  Smart Skin Care Advisor — Windows Setup"         -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "Project root: $ProjectRoot"

# ── 1. Python check ──────────────────────────────────────────
Write-Host "`n[1/5] Checking Python 3.9+ ..." -ForegroundColor Yellow
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Error "Python not found. Install Python 3.9+ from https://www.python.org/downloads/"
}
$pyVer = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
Write-Host "      Python $pyVer found → OK" -ForegroundColor Green

# ── 2. Create virtual environment ────────────────────────────
Write-Host "`n[2/5] Creating virtual environment ..." -ForegroundColor Yellow
if (Test-Path $VenvDir) {
    Write-Host "      .venv already exists — skipping." -ForegroundColor Gray
} else {
    python -m venv $VenvDir
    Write-Host "      .venv created." -ForegroundColor Green
}

# Activate
$ActivateScript = Join-Path $VenvDir "Scripts\Activate.ps1"
& $ActivateScript
Write-Host "      Virtual environment activated." -ForegroundColor Green

# ── 3. Install dependencies ──────────────────────────────────
Write-Host "`n[3/5] Installing Python dependencies ..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
python -m pip install -r (Join-Path $ProjectRoot "backend\requirements.txt")
Write-Host "      Dependencies installed." -ForegroundColor Green

# ── 4. Dataset placeholder structure ─────────────────────────
Write-Host "`n[4/5] Ensuring dataset folder structure ..." -ForegroundColor Yellow
$classes = @("acne","eczema","melanoma","psoriasis","normal_skin","dark_spots","dry_skin")
foreach ($cls in $classes) {
    $clsPath = Join-Path $ProjectRoot "dataset\$cls"
    if (-not (Test-Path $clsPath)) {
        New-Item -ItemType Directory -Path $clsPath | Out-Null
    }
}
Write-Host "      Dataset subfolders ready." -ForegroundColor Green

# ── 5. Start FastAPI server ───────────────────────────────────
Write-Host "`n[5/5] Starting FastAPI development server ..." -ForegroundColor Yellow
Write-Host "      Open http://localhost:8000 in your browser." -ForegroundColor Cyan
Write-Host "      Press Ctrl+C to stop.`n"

Set-Location (Join-Path $ProjectRoot "backend")
uvicorn main:app --reload --host 0.0.0.0 --port 8000
