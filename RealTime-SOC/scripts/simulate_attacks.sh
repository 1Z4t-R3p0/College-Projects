#!/bin/bash
# =============================================================================
# SOC Attack Simulation Script
# File: scripts/simulate_attacks.sh
# College Project: Real-Time SOC Monitoring & Incident Response
# Simulates: SSH Brute-Force + Privilege Escalation
# Run from: Native Linux / WSL bash
# =============================================================================

TARGET_HOST="localhost"
SSH_PORT="22"
TARGET_USER="admin"
BRUTE_FORCE_ATTEMPTS=15

# ---- Color helpers ----
CYAN='\033[0;36m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
MAGENTA='\033[0;35m'
DK_GRAY='\033[1;30m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

info()    { echo -e "${CYAN}[*] $1${NC}"; }
attack()  { echo -e "${RED}[ATTACK] $1${NC}"; }
success() { echo -e "${GREEN}[+] $1${NC}"; }
warn()    { echo -e "${YELLOW}[!] $1${NC}"; }

show_banner() {
    echo -e "${CYAN}========================================================${NC}"
    echo -e "${CYAN}   Real-Time SOC Monitoring & Incident Response System${NC}"
    echo -e "${CYAN}========================================================${NC}"
    echo -e "${DK_GRAY}  Target Host: $TARGET_HOST | Port: $SSH_PORT${NC}"
    echo ""
}

# 0. Check Dependencies
if ! command -v sshpass &> /dev/null
then
    echo -e "${YELLOW}[!] sshpass not found. Installing for high-fidelity simulation...${NC}"
    sudo apt-get update && sudo apt-get install -y sshpass
fi

# =============================================================================
# SCENARIO 1: SSH Brute-Force
# =============================================================================
invoke_bruteforce() {
    echo ""
    echo -e "${CYAN}══════════════════════════════════════════${NC}"
    info "SCENARIO 1: SSH Brute-Force Attack"
    echo -e "${CYAN}══════════════════════════════════════════${NC}"

    attack "Sending $BRUTE_FORCE_ATTEMPTS failed SSH login attempts to ${TARGET_HOST}:${SSH_PORT}..."
    warn "Each wrong password attempt logs to auth.log -> picked up by Wazuh"

    if command -v sshpass &> /dev/null; then
        for (( i=1; i<=$BRUTE_FORCE_ATTEMPTS; i++ )); do
            echo -ne "${DK_GRAY}  Attempt $i/$BRUTE_FORCE_ATTEMPTS...${NC}"
            timeout 2 sshpass -p "wrongpassword$i" ssh -o StrictHostKeyChecking=no -o PasswordAuthentication=yes -p $SSH_PORT ${TARGET_USER}@${TARGET_HOST} exit 2>/dev/null || true
            sleep 0.8
            echo -e "${DK_GRAY} done${NC}"
        done
    else
        warn "sshpass not found. Simulating via logger (Linux/WSL mode)..."
        for (( i=1; i<=$BRUTE_FORCE_ATTEMPTS; i++ )); do
            echo -e "${DK_GRAY}  Logging attempt $i/$BRUTE_FORCE_ATTEMPTS...${NC}"
            logger -t sshd "Failed password for $TARGET_USER from 192.168.99.1 port $((40000 + RANDOM % 20000)) ssh2"
            sleep 0.3
        done
    fi

    success "Brute-force simulation complete!"
    info "Expected Wazuh Alerts → Rule 5760 (SSH failure), Rule 5763 (Multiple failures)"
    info "Check dashboard: Security Events → search 'authentication_failure'"
}

# =============================================================================
# SCENARIO 2: Privilege Escalation
# =============================================================================
invoke_privilege_escalation() {
    echo ""
    echo -e "${CYAN}══════════════════════════════════════════${NC}"
    info "SCENARIO 2: Privilege Escalation Attempts"
    echo -e "${CYAN}══════════════════════════════════════════${NC}"

    warn "Injecting privilege escalation event patterns into syslog..."

    attack "sudo su - root attempt..."
    logger -t sudo "USER=student : TTY=pts/0 ; PWD=/home/student ; USER=root ; COMMAND=/bin/bash"
    sleep 0.5

    attack "sudo bash execution..."
    logger -t sudo "USER=testuser : TTY=pts/1 ; PWD=/tmp ; USER=root ; COMMAND=/bin/bash"
    sleep 0.5

    attack "Logging setuid execution pattern..."
    logger -t exploit "Detected setuid execution: /usr/bin/pkexec by user student (uid=1001)"
    sleep 0.5

    attack "Logging /etc/shadow read attempt..."
    logger -t attack "Unauthorized read attempt on /etc/shadow by uid=1001"
    sleep 0.5

    success "Privilege escalation events injected!"
    info "Expected Wazuh Alerts → Rules 5402 (sudo), 100801 (sudo to root), 100400 (shadow access)"
    info "Check dashboard: Security Events → search 'sudo' or 'privilege'"
}

# =============================================================================
# Main
# =============================================================================
show_banner

info "Starting attack simulations against $TARGET_HOST..."
info "Make sure Wazuh Dashboard is open at: https://localhost"
info "Login: admin / SecretPassword"
echo ""

read -p "Press ENTER to start Scenario 1: SSH Brute-Force"
invoke_bruteforce

read -p "Press ENTER to start Scenario 2: Privilege Escalation"
invoke_privilege_escalation

echo ""
echo -e "${GREEN}══════════════════════════════════════════════════════${NC}"
success "All simulations complete!"
echo ""
info "View results in Wazuh Dashboard:"
echo -e "${WHITE}  1. Open https://localhost"
echo -e "  2. Login: admin / SecretPassword"
echo -e "  3. Go to: Threat Hunting → Security Events"
echo -e "  4. Filter: rule.level >= 7${NC}"
echo -e "${GREEN}══════════════════════════════════════════════════════${NC}"
