"""
SQLite database setup and ORM models using SQLAlchemy.
Stores prediction history for the /history endpoint.
"""

import os
from datetime import datetime
from pathlib import Path

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# ── Engine ────────────────────────────────────────────────────────────────────

DB_PATH = Path(__file__).parent / "predictions.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # required for SQLite + async
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ── ORM Model ─────────────────────────────────────────────────────────────────

class PredictionRecord(Base):
    __tablename__ = "predictions"

    id               = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename         = Column(String(255), nullable=True)
    predicted_class  = Column(String(64),  nullable=False)
    confidence       = Column(Float,        nullable=False)
    recommendation   = Column(Text,         nullable=True)
    all_scores_json  = Column(Text,         nullable=True)   # JSON string
    created_at       = Column(DateTime,     default=datetime.utcnow)


# ── Init ──────────────────────────────────────────────────────────────────────

def init_db():
    """Create tables if they don't exist yet."""
    Base.metadata.create_all(bind=engine)
    print(f"[db] Database initialised at {DB_PATH}")


# ── Dependency helper (FastAPI) ───────────────────────────────────────────────

def get_db():
    """Yield a database session and ensure it is closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
