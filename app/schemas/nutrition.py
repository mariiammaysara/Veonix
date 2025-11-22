from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator


# Allowed confidence options
Confidence = Literal["High", "Medium", "Low"]


class NutritionItem(BaseModel):
    food_name: Optional[str] = Field(None)
    serving_description: Optional[str] = Field(None)

    calories: Optional[float] = Field(None)
    protein_grams: Optional[float] = Field(None)
    carb_grams: Optional[float] = Field(None)
    fat_grams: Optional[float] = Field(None)

    confidence_level: Confidence = "Low"

    model_config = {
        "extra": "forbid"
    }

    @field_validator("calories", "protein_grams", "carb_grams", "fat_grams")
    @classmethod
    def validate_non_negative(cls, v):
        if v is None:
            return None
        v = float(v)
        if v < 0:
            raise ValueError("Nutrition values cannot be negative.")
        return v


class NutritionResponse(BaseModel):
    type: Literal["fresh", "packaged"] = Field(...)   # <-- ADDED HERE
    items: List[NutritionItem] = Field(..., min_length=1)
    overall_confidence: Confidence = "Low"

    model_config = {
        "extra": "forbid"
    }
