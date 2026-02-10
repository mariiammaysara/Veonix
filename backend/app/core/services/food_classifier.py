from typing import Dict, Any
from app.core.services.food_analysis import FoodAnalyzer

class FoodClassifier:
    """Business logic layer for food classification."""
    def __init__(self) -> None:
        self.analyzer = FoodAnalyzer()

    async def classify_image(self, image_bytes: bytes, mime_type: str) -> Dict[str, Any]:
        """
        Triggers the image analysis via the vision model and returns 
        the structured nutritional data.
        """
        return await self.analyzer.analyze_food_image(image_bytes, mime_type)