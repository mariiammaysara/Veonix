"""
Module: database
Layer:  Infrastructure (DB)

SQLAlchemy engine and session management.
Provides the connection pool and declarative base for ORM models.

Author: Mariam Maysara
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from src.config import settings

# SQLite connection configuration.
# check_same_thread=False is essential for FastAPI's async execution model.
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# Factory for creating database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that yields a database session.
    Ensures that the connection is properly returned to the pool after the request lifecycle.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Synchronizes the database schema with the application's models.
    Called on application startup.
    """
    # Defensive import: ensures models are registered with Base before creation
    from src.models import meal  # noqa: F401
    Base.metadata.create_all(bind=engine)
