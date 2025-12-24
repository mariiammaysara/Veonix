from pydantic import BaseModel
from typing import Optional

class Macros(BaseModel):
    protein: float
    carbs: float
    fat: float

class AnalyzeImageResponse(BaseModel):
    # Added id to enable deletion functionality
    id: Optional[int] = None
    food_name: str
    calories: float
    macros: Macros

    # Enable ORM mode to read data from SQLAlchemy models
    class Config:
        from_attributes = True