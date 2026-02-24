# Automated Brute Force Attack Detection and Prevention System using Hydra

A complete final year project demonstrating how brute force attacks occur and how modern web applications detect and mitigate them.

## Overview

This project implements a vulnerable login application built with Python (Flask) along with a robust detection and prevention system. It automatically identifies brute-force attacks based on IP activity, rates limit excessive requests, and completely blocks malicious actors from accessing the application for a set period.

## Architecture

```text
                      +-----------------------------+
                      |       Attacker (Hydra)      |
                      +-------------+---------------+
                                    |
                                    v (HTTP POST /login)
                      +-------------+---------------+
                      |        Docker Network       |
                      |                             |
                      |  +-----------------------+  |
                      |  |     Web Application   |  |
                      |  |       (Flask)         |  |
                      |  +-----------+-----------+  |
                      |              |              |
                      |              v              |
                      |  +-----------------------+  |
                      |  |    Rate Limiter &     |  |
                      |  |    IP Blocking Logic  |  |
                      |  +-----------+-----------+  |
                      |              |              |
                      |              v              |
                      |  +-----------------------+  |
                      |  |     Redis Store       |  |
                      |  |   (In-Memory State)   |  |
                      |  +-----------------------+  |
                      +-----------------------------+
```

## How It Works

### 1. The Attack (How Brute Force Works)
A brute force attack is a trial-and-error method used by attackers to obtain credentials like passwords. Automated tools like Hydra systematically check all possible passwords until the correct one is found.

**How Hydra works:**
Hydra performs rapid dictionary attacks against various protocols (including HTTP POST forms). It uses a wordlist (`wordlist.txt`) and attempts logins at high speeds.

### 2. Detection Logic
The system monitors login attempts per IP address using Redis as a high-speed data store.
- Every failed attempt increments a counter for that IP.
- The system logs all activity (IP, Timestamp, Username) to `logs/attack.log`.

### 3. Prevention Logic
The application employs two layers of defense:
- **Rate Limiting:** If an IP makes more than 5 requests within 1 minute, the application returns `HTTP 429 Too Many Requests`.
- **IP Blocking (Fail2Ban-like):** If an IP accumulates 50 failed login attempts, it is added to a permanent blocklist in Redis.
- **Access Denial:** Blocked IPs are completely denied access to the application (`HTTP 404/403 blocked page`) displaying a warning message: *"Access Permanently Restricted: Too many failed attempts detected."*
- **Auto-Unblock:** The block automatically expires after 15 minutes.

## Project Structure

```text
Automated-Brute-Force-Detection/
│
├── app/
│   ├── main.py                 # Core Flask application
│   ├── templates/              # HTML views (index, success, blocked, rate_limit)
│   ├── static/                 # CSS stylesheets
│   ├── middleware/             # Rate limiting and IP blocking logic
│   └── utils/                  # Logging configuration
│
├── logs/                       # Application and attack logs (host mapped)
│
├── redis/                      # Redis volumes
│
├── attack.sh                   # Automated Hydra attack simulation script (Bash)
├── attack.py                   # Automated concurrent simulation script (Python)
├── unblock.sh                  # Utility script to instantly unblock IPs
├── wordlist.txt                # Sample password dictionary
├── docker-compose.yml          # Container orchestration
├── Dockerfile                  # Application container definition
├── requirements.txt            # Python dependencies
└── README.md                   # This documentation
```

## Setup & Running

This project uses Docker for seamless deployment without manual dependency installation.

### Prerequisites
- Docker & Docker Compose
- Hydra (if using `attack.sh` instead of the pure Python `attack.py`)

### 🪟 Windows (PowerShell)
Run this command from an elevated PowerShell command prompt:

```powershell
irm https://raw.githubusercontent.com/1Z4t-R3p0/College-Projects/main/Automated-Brute-Force-Detection/win-setup.ps1 | iex
```

### 🐧 WSL / Linux
Run this command from your terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/1Z4t-R3p0/College-Projects/main/Automated-Brute-Force-Detection/linux-setup.sh | bash
```

### Manual Local Setup (Docker)
Clone the repository:
```bash
git clone https://github.com/1Z4t-R3p0/College-Projects.git
cd College-Projects/Automated-Brute-Force-Detection
```
Run with Docker Compose:
```bash
docker compose up -d --build
```
Access the app at `http://localhost:8080`.

### Running the Attack Simulation

You can simulate a brute force attempt using either the Bash script (which requires Hydra installed) or the pure Python script.

1. Ensure the application is running.
2. Execute the Python attack script:
   ```bash
   ./attack.py
   ```
   *(Or optionally specify wordlist and user: `./attack.py -w wordlist.txt -u admin`)*
3. Observe the output. The attack will eventually be blocked, and the application will return status `404 Blocked` or `429 Rate Limit`.
4. Try accessing `http://localhost:8080` from your browser to see the red "IP Blocked" screen.

### Unblocking your IP

If you block yourself and need to regain access to test again, use the unblock utility:

```bash
# Unblock all IPs instantly
./unblock.sh

# Unblock a specific IP
./unblock.sh 127.0.0.1
```

### Viewing Logs

The application logs are mapped directly from the container to your local `logs` folder. To see them:
```bash
cat logs/attack.log
```
Or check real-time container logs:
```bash
docker compose logs -f web
```

## UI Screenshots
*(Placeholder for UI screenshots. Add your own when deploying your project)*
- Login Page
- Success Dashboard
- Rate Limit Error (429)
- Blocked Message (403)
