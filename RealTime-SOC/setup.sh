#!/bin/bash

# ========================================================
#  Real-Time SOC Monitoring & Incident Response System
# ========================================================

echo -e "\e[36m========================================================\e[0m"
echo -e "\e[36m   Real-Time SOC Monitoring & Incident Response System\e[0m"
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
    echo -e "\e[31mPlease log out and back in to finish Docker installation.\e[0m"
    exit 1
fi

if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# 3. Project Initialization
echo -e "\e[32mInitializing project components...\e[0m"
chmod +x ./scripts/*.sh 2>/dev/null || true

# 4. Run Docker Compose
echo -e "\e[32mStarting Real-Time SOC Monitoring & Incident Response System...\e[0m"
$DOCKER_COMPOSE down -v 2>/dev/null || true
$DOCKER_COMPOSE up -d --build

echo -e "\e[33mWaiting for SOC Dashboard to initialize...\e[0m"
for i in {1..10}; do
    echo -n "."
    sleep 3
done
echo ""

echo -e "\e[32m========================================================\e[0m"
echo -e "\e[32m Deployment Complete!\e[0m"
echo -e "\e[32m Main Dashboard (Wazuh): http://localhost:443\e[0m"
echo -e "\e[32m Quick Monitor UI (Custom): http://localhost:8080\e[0m"
echo -e "\e[32m Simulation Suite: ./scripts/simulate_attacks.sh\e[0m"
echo -e "\e[32m========================================================\e[0m"
