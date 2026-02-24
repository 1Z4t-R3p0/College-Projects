@echo off
echo WebGuard Setup
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker is not installed.
    pause
    exit /b
)
docker compose up --build -d
if %errorlevel% equ 0 (
    echo WebGuard is now running at http://localhost:8000
) else (
    echo Error: Failed to start.
)
pause
