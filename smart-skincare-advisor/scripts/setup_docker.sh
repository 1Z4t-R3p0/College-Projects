#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "================================================="
echo "    Smart Skin Care Advisor - Docker Setup Script  "
echo "================================================="

# 1. Install Docker if it's missing
if ! command -v docker &> /dev/null; then
    echo "[!] Docker is not installed. Installing Docker now..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
    echo "[+] Docker installed successfully."
else
    echo "[+] Docker is already installed."
fi

# 2. Ensure Docker Compose is available
if ! docker compose version &> /dev/null; then
    echo "[!] Docker Compose plugin not found. Attempting to install..."
    sudo apt-get update && sudo apt-get install docker-compose-plugin -y
fi

# 3. Set up the dataset directory and fill it with sample images
echo "[+] Preparing the dataset folders and filling them with sample images..."
mkdir -p dataset/acne dataset/dark_spots dataset/dry_skin dataset/eczema dataset/melanoma dataset/normal_skin dataset/psoriasis

# Copy items from sample_img/ into the correct dataset folders (only if sample_img exists)
if [ -d "sample_img" ]; then
    cp sample_img/acne.png dataset/acne/sample.png 2>/dev/null || true
    cp sample_img/dark_spots.png dataset/dark_spots/sample.png 2>/dev/null || true
    cp sample_img/dry_skin.png dataset/dry_skin/sample.png 2>/dev/null || true
    cp sample_img/eczema.png dataset/eczema/sample.png 2>/dev/null || true
    cp sample_img/melanoma.png dataset/melanoma/sample.png 2>/dev/null || true
    cp sample_img/normal_skin.png dataset/normal_skin/sample.png 2>/dev/null || true
    cp sample_img/psoriasis.png dataset/psoriasis/sample.png 2>/dev/null || true
    echo "[+] Dataset populated with core sample images."
else
    echo "[!] Warning: 'sample_img' directory not found. Dataset folders created but remain empty."
fi

# 4. Build and run the app background container
echo "[+] Building and starting Docker containers..."
docker compose up -d --build

# 5. Training Instructions
echo ""
echo "================================================="
echo " ✅ Setup Complete!"
echo " 🌐 App is running at: http://localhost:8001"
echo ""
echo " If you add NEW images to 'dataset/' folders, "
echo " re-train the AI model by running:"
echo "   docker exec skincare-advisor python3 /app/ml/train.py --dataset /app/dataset --epochs 300 --output /app/ml/skin_cnn.pth"
echo " Then, restart the server:"
echo "   docker compose restart skincare-api"
echo "================================================="
