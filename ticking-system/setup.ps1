# Requires Docker Desktop on your Windows Machine

Write-Host "Creating Docker container definitions... Please wait..." -ForegroundColor Green
docker-compose down

Write-Host "Re-starting Docker stack..." -ForegroundColor Green
docker-compose up -d --build

Write-Host "Waiting for environment to load up... (FastAPI NLP modeling)" -ForegroundColor Green
Start-Sleep -Seconds 10
Write-Host "Environment Successfully Initialized!" -ForegroundColor Green

Write-Host "`nTest UI by navigating to: http://localhost in any modern browser.`n" -ForegroundColor Cyan
