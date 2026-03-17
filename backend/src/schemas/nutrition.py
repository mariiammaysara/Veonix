"""
Module: nutrition
Layer:  Schemas

Pydantic models for nutritional data structures.
Separated to allow reuse across analysis responses and detailed meal views.

Author: Mariam Maysara
"""

from pydantic import BaseModel


class NutritionResponse(BaseModel):
    """
    Detailed nutritional breakdown of a meal.
    Includes both the total values and the per-100g reference.
    """
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: float
    sodium: float
    per_100g: dict
    source: str
    # When True, the frontend should display an 'approximate' badge
    is_estimated: bool = False
