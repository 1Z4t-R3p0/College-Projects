# Cloud Support Ticket Classification System (Local Version)

A complete college-level project that automatically categorizes support tickets using Natural Language Processing (NLP) and Machine Learning. The system uses a FastAPI backend, an SQLite database, and a vanilla HTML/CSS/JS frontend without external UI frameworks. The entire application is containerized using Docker Compose for simple, one-command deployment.

## Features
- **Machine Learning Classification**: Automatically categorizes tickets into one of five categories (Network, Software, Hardware, Account, Security).
- **Automated Training**: The backend trains a scikit-learn Logistic Regression model using TF-IDF vectorization on startup using a provided sample dataset.
- **RESTful API**: FastAPI backend providing endpoints for ticket submission and retrieval.
- **Modern UI**: A responsive, premium frontend built with pure HTML, CSS (featuring glassmorphism and animations), and JavaScript.
- **Microservices Architecture**: Separate Docker containers for the frontend (Nginx) and backend (Python/Uvicorn).
- **Data Persistence**: Uses an SQLite database (stored locally in a Docker volume) to maintain ticket history safely.

## Prerequisites
- Docker
- Docker Compose

## Installation & Running

1. **Navigate to the project directory** where the `docker-compose.yml` file is located:
   ```bash
   cd /path/to/Ticking-system
   ```

2. **Build and start the services** using Docker Compose:
   ```bash
   docker compose up --build -d
   ```
   *The `-d` flag runs the containers in detached mode (in the background).*

3. **Access the Application**:
   - Open your web browser and go to: `http://localhost`
   - You should see the modern "Cloud Support Ticket System" interface.

## How to Work the System
1. On the main interface, locate the "Submit new ticket" section.
2. Enter an **Issue Title** (e.g., "Forgot my portal password").
3. Enter a **Detailed Description** outlining the problem explicitly.
4. Click **Submit Ticket**.
5. The frontend will send the text to the FastAPI backend, which will instantly run it through the pre-trained NLP model.
6. The ticket will appear under the "Recent Tickets" list with its auto-detected category tag (e.g., "Account").

## Project Structure
```
Ticking-system/
│
├── docker-compose.yml       # Orchestrates the backend and frontend containers
│
├── backend/                 # FastAPI and Machine Learning Code
│   ├── Dockerfile           # Python 3.11 environment setup
│   ├── requirements.txt     # Backend dependencies (fastapi, scikit-learn, etc.)
│   ├── main.py              # Application entry point and API routes
│   ├── ml_model.py          # TF-IDF + Logistic Regression classification logic
│   ├── models.py            # SQLAlchemy database models
│   ├── schemas.py           # Pydantic data validation schemas
│   ├── database.py          # SQLite connection and session maker
│   └── data/
│       └── sample_tickets.csv # Dataset used to train the ML model on startup
│
└── frontend/                # User Interface
    ├── Dockerfile           # Nginx environment setup
    ├── index.html           # Main page structure
    ├── style.css            # Custom styling and animations
    └── script.js            # Fetch API logic for backend communication
```

## Stopping the Application
To shut down the running containers, run:
```bash
docker compose down
```

To completely wipe the database and start fresh, run:
```bash
docker compose down -v
sudo rm -rf ./backend/data/tickets.db
```
*(Note: Be careful with the second command, as it permanently deletes ticket history.)*
