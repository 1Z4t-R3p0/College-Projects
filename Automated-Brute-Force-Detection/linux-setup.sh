#!/bin/bash

# ========================================================
#  Automated Brute Force Detection Deployment (Linux)
# ========================================================

REPO_URL="https://github.com/1Z4t-R3p0/College-Projects.git"
PROJECT_DIR="$HOME/College-Projects"

echo -e "\e[36m========================================================\e[0m"
echo -e "\e[36m   Automated Brute Force Detection Setup\e[0m"
echo -e "\e[36m========================================================\e[0m"

# 1. Check and Install Git
if ! command -v git &> /dev/null
then
    echo -e "\e[33mGit not found. Installing Git...\e[0m"
    sudo apt-get update
    sudo apt-get install -y git
fi

# 2. Check and Install Docker Compose
if ! command -v docker &> /dev/null
then
    echo -e "\e[33mDocker not found. Installing Docker...\e[0m"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo -e "\e[31m=======================================================\e[0m"
    echo -e "\e[31m Please log out and back in, or restart your terminal \e[0m"
    echo -e "\e[31m to finish Docker installation, then run this script again.\e[0m"
    echo -e "\e[31m=======================================================\e[0m"
    exit 1
fi

# Check if Docker daemon is running
if ! sudo docker info > /dev/null 2>&1; then
    echo -e "\e[31mDocker is not running! Please start Docker and run this script again.\e[0m"
    exit 1
fi

# 3. Clone or Update Project
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "\e[32mCloning project repository...\e[0m"
    git clone "$REPO_URL" "$PROJECT_DIR"
else
    echo -e "\e[32mProject exists at $PROJECT_DIR. Pulling latest changes...\e[0m"
    cd "$PROJECT_DIR"
    git pull
fi

# 4. Run Docker Compose
cd "$PROJECT_DIR/Automated-Brute-Force-Detection"
echo -e "\e[32mStarting Automated Brute Force Detection System...\e[0m"
sudo docker compose up -d

echo ""
echo -e "\e[32m========================================================\e[0m"
echo -e "\e[32m Deployment Complete!\e[0m"
echo -e "\e[32m Access Application at: http://localhost:8080\e[0m"
echo -e "\e[32m========================================================\e[0m"
