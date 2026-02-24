# WebGuard: Automated Web Application Security Scanner

WebGuard is a professional, lightweight web security scanner designed to identify common vulnerabilities in web applications. It provides a modern dark-themed interface and real-time scanning capabilities.

## Features

- **SQL Injection Detection**: Error-based analysis for potential database leaks.
- **Cross-Site Scripting (XSS)**: Identification of reflected script payloads.
- **Security Headers Check**: Verification of critical headers like CSP, X-Frame-Options, and X-XSS-Protection.
- **Open Redirect Check**: Testing for insecure URL redirection parameters.
- **Private IP Blocking**: Built-in protection to prevent scanning of internal networks (localhost, private IP ranges).
- **Responsive Dark Theme**: A premium UI built with vanilla technologies.

## Tech Stack

- **Backend**: Python, FastAPI, BeautifulSoup4, Requests, Jinja2.
- **Frontend**: HTML5, CSS3 (Modern Vanilla), JavaScript (Vanilla).
- **Containerization**: Docker, Docker Compose.

## How to Run

### Option 1: Using Startup Scripts (Recommended)

- **Mac / Linux**:
  ```bash
  chmod +x scripts/setup_mac_linux.sh
  ./scripts/setup_mac_linux.sh
  ```
- **Windows**:
  Double-click `scripts/setup_windows.bat` or run it via CMD.

### Option 2: Direct Docker Commands
If you have Docker and Docker Compose installed:

1. Navigate to the project directory:
   ```bash
   cd scanner-project
   ```

2. Build and start the container:
   ```bash
   docker compose up --build -d
   ```

3. Access the application:
   Open `http://localhost:8000` in your web browser.

## Limitations

- **Scan Depth**: Currently limited to a depth of 1 (homepage only).
- **Complexity**: Does not support authenticated scanning or complex client-side rendered (SPA) applications without CSRF tokens handled.
- **Payloads**: Uses a basic set of payloads for demonstration; not intended for comprehensive penetration testing.

## Future Improvements

- Implement a multi-level crawler for deeper site analysis.
- Add support for DOM-based XSS detection using a headless browser.
- Include auto-generated PDF reports for scan results.
- Add a dashboard for historical scan comparisons.

---
*Developed as a Final Year Project.*
