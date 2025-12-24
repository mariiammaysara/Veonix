import logging
from typing import Dict, Any
from app.core.services.gemini_client import GeminiClient
from app.core.services.nutrition_normalizer import NutritionNormalizer

# Initialize logger for service tracking
logger = logging.getLogger(__name__)

class NutritionService:
    def __init__(self):
        """
        Initializes the NutritionService by connecting the AI Client 
        and the Normalizer tool.
        """
        self.ai_client = GeminiClient()
        self.normalizer = NutritionNormalizer()

    async def get_nutritional_analysis(self, image_bytes: bytes, mime_type: str) -> Dict[str, Any]:
        """
        Orchestrates the flow: 
        1. Sends image to Gemini for raw AI analysis.
        2. Passes raw data to the Normalizer to ensure numeric consistency.
        3. Returns a clean, validated dictionary.
        """
        try:
            logger.info("Starting nutritional analysis process...")

            # Step 1: Get raw analysis from Gemini AI
            raw_analysis = await self.ai_client.analyze_food_image(image_bytes, mime_type)
            
            # Step 2: Normalize and clean the data (Fixing types, rounding numbers)
            # This ensures that '150g' becomes 150 (int) and names are formatted
            clean_data = self.normalizer.normalize_analysis_result(raw_analysis)
            
            logger.info(f"Analysis completed successfully for: {clean_data.get('food_name')}")
            
            return clean_data

        except Exception as e:
            logger.error(f"Error in NutritionService: {str(e)}")
            # Raise the exception to be handled by the Router's error handler
            raise e