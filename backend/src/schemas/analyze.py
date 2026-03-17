"""
Module: analyze
Layer:  Schemas

Pydantic models for analysis-related request and response validation.
Defines the API contract for food identification, history, and statistics.

Author: Mariam Maysara
"""

from datetime import datetime
from pydantic import BaseModel
from src.schemas.nutrition import NutritionResponse


class AnalysisResponse(BaseModel):
    """
    Response schema for a successful meal analysis.
    Consolidates identity metadata with a nested nutrition breakdown.
    """
    food_name: str
    confidence: float
    ingredients: list[str]
    weight_grams: int
    meal_type: str
    cuisine: str
    nutrition: NutritionResponse


class MealHistoryItem(BaseModel):
    """
    Schema for a single record in the user's meal history.
    Maps directly from the SQLAlchemy 'Meal' model.
    """
    id: int
    food_name: str
    meal_type: str | None
    weight_grams: int
    calories: float
    protein: float
    carbs: float
    fat: float
    created_at: datetime

    class Config:
        # Enables automatic conversion from SQLAlchemy objects to Pydantic models
        from_attributes = True


class MealHistoryResponse(BaseModel):
    """
    Paginated response container for meal history.
    """
    total: int
    meals: list[MealHistoryItem]


class StatsResponse(BaseModel):
    """
    Response schema for aggregated nutritional statistics.
    Used for dashboard visualizations.
    """
    total_meals: int
    avg_calories: float
    avg_protein: float
    avg_carbs: float
    avg_fat: float
