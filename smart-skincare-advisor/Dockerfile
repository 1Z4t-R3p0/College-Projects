# ── Stage 1: base ────────────────────────────────────────────────────────────
FROM python:3.11-slim AS base

# System deps for OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libgl1 \
    && rm -rf /var/lib/apt/lists/*

# ── Stage 2: dependencies ─────────────────────────────────────────────────────
FROM base AS deps

WORKDIR /app

COPY backend/requirements.txt ./requirements.txt

# CPU-only torch is much smaller; override the index for the torch packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        torch==2.2.2 torchvision==0.17.2 \
        --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir \
        fastapi==0.110.0 \
        uvicorn[standard]==0.29.0 \
        python-multipart==0.0.9 \
        sqlalchemy==2.0.29 \
        opencv-python-headless==4.9.0.80 \
        pillow==10.3.0 \
        numpy==1.26.4 \
        scikit-learn==1.4.2

# ── Stage 3: final image ──────────────────────────────────────────────────────
FROM deps AS final

WORKDIR /app

# Copy all project source
COPY backend/   ./backend/
COPY ml/        ./ml/
COPY frontend/  ./frontend/

# Persistent volume mount point for the SQLite DB
RUN mkdir -p /app/data

# Expose FastAPI port
EXPOSE 8000

# Change into backend dir before starting so relative imports resolve correctly
WORKDIR /app/backend

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
