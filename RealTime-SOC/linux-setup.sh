#!/bin/bash

# ========================================================
#  Real-Time SOC Monitoring & Incident Response System
#  One-Line Linux Setup (curl | bash)
# ========================================================

set -e

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}========================================================${NC}"
echo -e "${CYAN}   Real-Time SOC Monitoring & Incident Response System${NC}"
echo -e "${CYAN}   Automated Linux Setup${NC}"
echo -e "${CYAN}========================================================${NC}"
echo ""

# ── 1. Install Docker if missing ──────────────────────────
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}[*] Docker not found. Installing...${NC}"
    if grep -iq "kali" /etc/os-release 2>/dev/null; then
        echo -e "${YELLOW}[*] Detected Kali Linux. Installing via apt...${NC}"
        sudo apt-get update -qq && sudo apt-get install -y docker.io docker-compose
    else
        curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
        sh /tmp/get-docker.sh
    fi
    sudo usermod -aG docker "$USER"
    echo -e "${GREEN}[+] Docker installed.${NC}"
else
    echo -e "${GREEN}[+] Docker already installed.${NC}"
fi

# ── 2. Install Git if missing ─────────────────────────────
if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}[*] Git not found. Installing...${NC}"
    sudo apt-get update -qq && sudo apt-get install -y git
fi

# ── 3. Docker Compose check ───────────────────────────────
if docker compose version &> /dev/null; then
    COMPOSE="docker compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE="docker-compose"
else
    echo -e "${RED}[!] Docker Compose not found. Please install Docker Desktop or docker-compose.${NC}"
    exit 1
fi

echo -e "${GREEN}[+] Using: $COMPOSE${NC}"

# ── 4. Clone the repo ─────────────────────────────────────
REPO_URL="https://github.com/1Z4t-R3p0/College-Projects.git"
TARGET_DIR="$HOME/College-Projects"

if [ -d "$TARGET_DIR" ]; then
    echo -e "${YELLOW}[*] Repo already exists. Pulling latest...${NC}"
    git -C "$TARGET_DIR" pull --ff-only
else
    echo -e "${YELLOW}[*] Cloning repository...${NC}"
    git clone "$REPO_URL" "$TARGET_DIR"
fi

PROJECT_DIR="$TARGET_DIR/RealTime-SOC"

if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}[!] RealTime-SOC folder not found in repo. Please check the repository.${NC}"
    exit 1
fi

cd "$PROJECT_DIR"

# ── 5. Wipe existing containers & launch ──────────────────
echo -e "${YELLOW}[*] Stopping any previous deployment...${NC}"
$COMPOSE down -v 2>/dev/null || true

echo -e "${YELLOW}[*] Building and starting the SOC stack...${NC}"
$COMPOSE up -d --build

# ── 6. Wait ───────────────────────────────────────────────
echo -e "${YELLOW}[*] Waiting for services to initialize (30s)...${NC}"
for i in {1..10}; do echo -n "."; sleep 3; done
echo ""

# ── 7. Done ───────────────────────────────────────────────
echo ""
echo -e "${GREEN}========================================================${NC}"
echo -e "${GREEN}   Deployment Complete!${NC}"
echo -e "${GREEN}--------------------------------------------------------${NC}"
echo -e "${GREEN}   SOC Quick Monitor : http://localhost:8080${NC}"
echo -e "${GREEN}   Wazuh Dashboard   : http://localhost:443${NC}"
echo -e "${GREEN}   Attack Simulation : cd $PROJECT_DIR${NC}"
echo -e "${GREEN}                       ./scripts/simulate_attacks.sh${NC}"
echo -e "${GREEN}========================================================${NC}"
