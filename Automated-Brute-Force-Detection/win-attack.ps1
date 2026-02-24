# ========================================================
#  Automated Brute Force Attack Simulation (Windows)
#  Simulates a brute force attack using Hydra
#  Triggers 429 Rate Limit after 5 attempts
#  Triggers 404 IP Block after 50 attempts
# ========================================================

param(
    [string]$Target = "localhost",
    [string]$Port   = "8080",
    [string]$User   = "admin",
    [string]$Wordlist = "wordlist.txt"
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "    Automated Brute Force Detection - Attack Simulation   " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Target  : $Target`:$Port"
Write-Host "Wordlist: $Wordlist"
Write-Host "User    : $User"
Write-Host "----------------------------------------------------------"

# 1. Check if Hydra is available
if (-not (Get-Command "hydra" -ErrorAction SilentlyContinue)) {
    Write-Host "[!] Hydra is not installed or not in PATH." -ForegroundColor Red
    Write-Host "[*] Install Hydra for Windows:" -ForegroundColor Yellow
    Write-Host "    https://github.com/vanhauser-thc/thc-hydra/releases" -ForegroundColor Yellow
    Write-Host "    Or use WSL: sudo apt install hydra" -ForegroundColor Yellow
    exit 1
}

# 2. Check wordlist exists
if (-not (Test-Path $Wordlist)) {
    Write-Host "[!] Wordlist file not found: $Wordlist" -ForegroundColor Red
    exit 1
}

Write-Host "[*] Starting Hydra attack..." -ForegroundColor Green
Write-Host ""

# 3. Run Hydra
# Syntax: hydra -l <user> -P <wordlist> <host> -s <port> http-post-form "<path>:<params>:<fail_string>"
hydra -l $User -P $Wordlist $Target -s $Port http-post-form "/login:username=^USER^&password=^PASS^:Invalid credentials"

Write-Host ""
Write-Host "----------------------------------------------------------"
Write-Host "[*] Attack completed." -ForegroundColor Green
Write-Host "[*] Expected behaviour:" -ForegroundColor Cyan
Write-Host "     - After 5 bad attempts  -> HTTP 429 (Rate Limited)"
Write-Host "     - After 50 bad attempts -> HTTP 404 (IP Blocked)"
Write-Host "[*] Check application logs to see detection events."
Write-Host "==========================================================" -ForegroundColor Cyan

# 4. Verify IP was blocked — try one final request and show HTTP status
Write-Host ""
Write-Host "[*] Verifying block status..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://$Target`:$Port/login" `
        -Method POST `
        -Body "username=$User&password=test" `
        -ErrorAction Stop
    Write-Host "[*] HTTP Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    $code = $_.Exception.Response.StatusCode.value__
    if ($code -eq 404) {
        Write-Host "[+] SUCCESS: HTTP 404 - IP is BLOCKED as expected!" -ForegroundColor Green
    } elseif ($code -eq 429) {
        Write-Host "[~] HTTP 429 - IP is rate limited (not yet fully blocked)." -ForegroundColor Yellow
    } else {
        Write-Host "[*] HTTP $code received." -ForegroundColor White
    }
}
