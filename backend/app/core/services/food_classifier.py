from typing import Dict, Any
from app.core.services.gemini_client import GeminiClient

class FoodClassifier:
    """Business logic layer for food classification."""
    def __init__(self) -> None:
        self.gemini = GeminiClient()

    async def classify_image(self, image_bytes: bytes, mime_type: str) -> Dict[str, Any]:
        """
        Triggers the image analysis via GeminiClient and returns 
        the structured nutritional data.
        """
        return await self.gemini.analyze_food_image(image_bytes, mime_type)