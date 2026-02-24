# ========================================================
#  Automated Brute Force Detection Deployment (Windows)
# ========================================================

$REPO_URL = "https://github.com/1Z4t-R3p0/College-Projects.git"
$PROJECT_DIR = "$HOME\College-Projects"

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   Automated Brute Force Detection Setup" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# 1. Check and Install Git
if (-not (Get-Command "git" -ErrorAction SilentlyContinue)) {
    Write-Host "Git not found. Installing Git..." -ForegroundColor Yellow
    winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements
    $env:Path += ";C:\Program Files\Git\cmd"
}

# 2. Check and Install Docker
if (-not (Get-Command "docker" -ErrorAction SilentlyContinue)) {
    Write-Host "Docker not found. Installing Docker Desktop..." -ForegroundColor Yellow
    winget install --id Docker.DockerDesktop -e --source winget --accept-package-agreements --accept-source-agreements
    Write-Host "=======================================================" -ForegroundColor Red
    Write-Host " Please restart your computer/terminal to finish Docker" -ForegroundColor Red
    Write-Host " installation, then run this script again." -ForegroundColor Red
    Write-Host "=======================================================" -ForegroundColor Red
    exit
}

# Check if Docker daemon is running
docker info > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker is not running! Please start Docker Desktop and run this script again." -ForegroundColor Red
    exit
}

# 3. Clone or Update Project
if (-not (Test-Path $PROJECT_DIR)) {
    Write-Host "Cloning project repository..." -ForegroundColor Green
    git clone $REPO_URL $PROJECT_DIR
} else {
    Write-Host "Project exists at $PROJECT_DIR. Pulling latest changes..." -ForegroundColor Green
    Set-Location $PROJECT_DIR
    git pull
}

# 4. Run Docker Compose
Set-Location "$PROJECT_DIR\Automated-Brute-Force-Detection"
Write-Host "Starting Automated Brute Force Detection System..." -ForegroundColor Green
docker compose up -d

Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host " Deployment Complete!" -ForegroundColor Green
Write-Host " Access Application at: http://localhost:8080" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
