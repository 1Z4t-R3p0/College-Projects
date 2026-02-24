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
- **Rate Limiting:** If an IP makes more than 10 requests within 1 minute, the application returns `HTTP 429 Too Many Requests`.
- **IP Blocking (Fail2Ban-like):** If an IP accumulates 5 failed login attempts, it is added to a temporary blocklist in Redis.
- **Access Denial:** Blocked IPs are completely denied access to the application (`HTTP 403 Forbidden`) displaying a warning message: *"Your IP has been temporarily blocked due to suspicious activity."*
- **Auto-Unblock:** The block automatically expires after 10 minutes.

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
├── logs/                       # Application and attack logs
│
├── redis/                      # Redis volumes
│
├── attack.sh                   # Automated Hydra attack simulation script
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
- Hydra (for running the attack simulation)

### Running the Application

1. Clone or navigate to the project directory.
2. Start the services:
   ```bash
   docker compose up -d
   ```
3. The application will be available at `http://localhost:8080`.

### Running the Attack Simulation

The attack script uses `hydra` to simulate a brute force attempt.

1. Ensure the application is running.
2. Execute the attack script:
   ```bash
   ./attack.sh http://localhost:8080
   ```
   *(Or just `./attack.sh` to use the default localhost URL)*
3. Observe the output. Hydra will eventually be blocked, and the application will return status `403` or `429`.
4. Try accessing `http://localhost:8080` from your browser to see the block screen.

### Viewing Logs

To see the attack logs generated by the system:
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
# College-Projects
