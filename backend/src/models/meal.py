"""
Module: meal
Layer:  Models

SQLAlchemy ORM model for the 'meals' table.
Defines the persistent schema for food identification and nutritional data.

Author: Mariam Maysara
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from src.db.database import Base


class Meal(Base):
    """
    Represents a single analyzed meal event.
    Stores both the identified food metadata and the calculated nutritional total.
    """
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)

    # ── Food Identity ─────────────────────────────────────────
    food_name = Column(String, nullable=False)
    cuisine = Column(String, nullable=True)
    meal_type = Column(String, nullable=True)
    preparation_method = Column(String, nullable=True)

    # ── Analysis Metadata ─────────────────────────────────────
    weight_grams = Column(Integer, nullable=False)
    # AI confidence score (0.0 to 1.0)
    confidence = Column(Float, nullable=False)

    # ── Nutritional Totals (Scaled to weight_grams) ───────────
    calories = Column(Float, nullable=False)
    protein = Column(Float, nullable=False)
    carbs = Column(Float, nullable=False)
    fat = Column(Float, nullable=False)
    fiber = Column(Float, nullable=True, default=0.0)
    sodium = Column(Float, nullable=True, default=0.0)

    # ── Raw Data & Source ─────────────────────────────────────
    # List of ingredients identified by the vision AI
    ingredients = Column(JSON, nullable=True)
    # Original nutritional profile used for scaling
    per_100g = Column(JSON, nullable=True)
    nutrition_source = Column(String, default="Gemini")
    # Boolean equivalent stored as Integer for SQLite compatibility
    is_estimated = Column(Integer, default=0)

    # ── Audit Timestamps ──────────────────────────────────────
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
