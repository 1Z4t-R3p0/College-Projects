# =============================================================================
# SOC Attack Simulation Script (PowerShell)
# File: scripts/simulate_attacks.ps1
# College Project: Real-Time SOC Monitoring & Incident Response
# Simulates: SSH Brute-Force + Privilege Escalation
# Run from: Windows machine or inside WSL/Linux via pwsh
# =============================================================================

param(
    [string]$TargetHost = "localhost",
    [int]$SSHPort = 22,
    [string]$TargetUser = "admin",
    [int]$BruteForceAttempts = 15
)

# ---- Color helpers ----
function Write-Info    { param($msg) Write-Host "[*] $msg" -ForegroundColor Cyan }
function Write-Attack  { param($msg) Write-Host "[ATTACK] $msg" -ForegroundColor Red }
function Write-Success { param($msg) Write-Host "[+] $msg" -ForegroundColor Green }
function Write-Warn    { param($msg) Write-Host "[!] $msg" -ForegroundColor Yellow }

function Show-Banner {
    Write-Host ""
    Write-Host "  ███████  ██████   ██████     ███████ ██ ███    ███ " -ForegroundColor Magenta
    Write-Host "  ██      ██    ██ ██          ██      ██ ████  ████ " -ForegroundColor Magenta
    Write-Host "  ███████ ██    ██ ██          ███████ ██ ██ ████ ██ " -ForegroundColor Magenta
    Write-Host "       ██ ██    ██ ██               ██ ██ ██  ██  ██ " -ForegroundColor Magenta
    Write-Host "  ███████  ██████   ██████     ███████ ██ ██      ██ " -ForegroundColor Magenta
    Write-Host ""
    Write-Host "  SOC Attack Simulator - College Demo " -ForegroundColor White
    Write-Host "  Target: $TargetHost | User: $TargetUser" -ForegroundColor DarkGray
    Write-Host ""
}

# =============================================================================
# SCENARIO 1: SSH Brute-Force
# =============================================================================
function Invoke-BruteForce {
    Write-Host ""
    Write-Host "══════════════════════════════════════════" -ForegroundColor DarkCyan
    Write-Info "SCENARIO 1: SSH Brute-Force Attack"
    Write-Host "══════════════════════════════════════════" -ForegroundColor DarkCyan

    Write-Attack "Sending $BruteForceAttempts failed SSH login attempts to ${TargetHost}:${SSHPort}..."
    Write-Warn "Each wrong password attempt logs to auth.log -> picked up by Wazuh"

    # Check if ssh/sshpass available
    $sshAvailable = Get-Command ssh -ErrorAction SilentlyContinue

    if ($sshAvailable) {
        for ($i = 1; $i -le $BruteForceAttempts; $i++) {
            Write-Host "  Attempt $i/$BruteForceAttempts..." -NoNewline -ForegroundColor DarkGray
            # SSH with wrong password - will fail, generating auth.log entry
            $proc = Start-Process -FilePath "ssh" `
                -ArgumentList "-o StrictHostKeyChecking=no -o ConnectTimeout=2 -o PasswordAuthentication=yes -p $SSHPort ${TargetUser}@${TargetHost}" `
                -PassThru -WindowStyle Hidden
            Start-Sleep -Milliseconds 800
            if (!$proc.HasExited) { $proc.Kill() }
            Write-Host " done" -ForegroundColor DarkGray
        }
    } else {
        Write-Warn "ssh not found on PATH. Simulating via logger (Linux/WSL mode)..."
        for ($i = 1; $i -le $BruteForceAttempts; $i++) {
            Write-Host "  Logging attempt $i/$BruteForceAttempts..." -ForegroundColor DarkGray
            & bash -c "logger -t sshd 'Failed password for $TargetUser from 192.168.99.1 port $((Get-Random -Min 40000 -Max 60000)) ssh2'"
            Start-Sleep -Milliseconds 300
        }
    }

    Write-Success "Brute-force simulation complete!"
    Write-Info "Expected Wazuh Alerts → Rule 5760 (SSH failure), Rule 5763 (Multiple failures)"
    Write-Info "Check dashboard: Security Events → search 'authentication_failure'"
}

# =============================================================================
# SCENARIO 2: Privilege Escalation
# =============================================================================
function Invoke-PrivilegeEscalation {
    Write-Host ""
    Write-Host "══════════════════════════════════════════" -ForegroundColor DarkCyan
    Write-Info "SCENARIO 2: Privilege Escalation Attempts"
    Write-Host "══════════════════════════════════════════" -ForegroundColor DarkCyan

    Write-Warn "Injecting privilege escalation event patterns into syslog..."

    # Check if we can run bash logger
    $bashAvailable = Get-Command bash -ErrorAction SilentlyContinue

    if ($bashAvailable) {
        Write-Attack "sudo su - root attempt..."
        & bash -c "logger -t sudo 'USER=student : TTY=pts/0 ; PWD=/home/student ; USER=root ; COMMAND=/bin/bash'"
        Start-Sleep -Milliseconds 500

        Write-Attack "sudo bash execution..."
        & bash -c "logger -t sudo 'USER=testuser : TTY=pts/1 ; PWD=/tmp ; USER=root ; COMMAND=/bin/bash'"
        Start-Sleep -Milliseconds 500

        Write-Attack "Logging setuid execution pattern..."
        & bash -c "logger -t exploit 'Detected setuid execution: /usr/bin/pkexec by user student (uid=1001)'"
        Start-Sleep -Milliseconds 500

        Write-Attack "Logging /etc/shadow read attempt..."
        & bash -c "logger -t attack 'Unauthorized read attempt on /etc/shadow by uid=1001'"
        Start-Sleep -Milliseconds 500

        Write-Success "Privilege escalation events injected!"
        Write-Info "Expected Wazuh Alerts → Rules 5402 (sudo), 100801 (sudo to root), 100400 (shadow access)"
        Write-Info "Check dashboard: Security Events → search 'sudo' or 'privilege'"
    } else {
        Write-Warn "bash not available - run this script from WSL or a Linux machine for full simulation."
        Write-Info "On the Wazuh agent container, you can run:"
        Write-Host "  docker exec -it wazuh.agent bash -c `"logger -t sudo 'USER=student : USER=root ; COMMAND=/bin/bash'`"" -ForegroundColor Yellow
    }
}

# =============================================================================
# Main
# =============================================================================
Show-Banner

Write-Info "Starting attack simulations against $TargetHost..."
Write-Info "Make sure Wazuh Dashboard is open at: https://localhost"
Write-Info "Login: admin / SecretPassword"
Write-Host ""

Read-Host "Press ENTER to start Scenario 1: SSH Brute-Force"
Invoke-BruteForce

Read-Host "Press ENTER to start Scenario 2: Privilege Escalation"
Invoke-PrivilegeEscalation

Write-Host ""
Write-Host "══════════════════════════════════════════════════════" -ForegroundColor Green
Write-Success "All simulations complete!"
Write-Host ""
Write-Info "View results in Wazuh Dashboard:"
Write-Host "  1. Open https://localhost" -ForegroundColor White
Write-Host "  2. Login: admin / SecretPassword" -ForegroundColor White
Write-Host "  3. Go to: Threat Hunting → Security Events" -ForegroundColor White
Write-Host "  4. Filter: rule.level >= 7" -ForegroundColor White
Write-Host "══════════════════════════════════════════════════════" -ForegroundColor Green
