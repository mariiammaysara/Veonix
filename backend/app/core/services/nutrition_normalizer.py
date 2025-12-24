import logging

# Initialize logger
logger = logging.getLogger(__name__)

class NutritionNormalizer:
    """
    Service responsible for cleaning and validating nutritional data 
    returned by the AI model to ensure consistency with the application's schemas.
    """

    @staticmethod
    def normalize_analysis_result(raw_data: dict) -> dict:
        """
        Cleans and formats the raw JSON dictionary from Gemini.
        Ensures calories and macros are numeric values.
        """
        try:
            # 1. Normalize Food Name (Capitalize and strip whitespace)
            food_name = str(raw_data.get("food_name", "Unknown Food")).strip().title()

            # 2. Normalize Calories (Ensure it's a number, default to 0 if missing)
            calories = raw_data.get("calories", 0)
            calories = NutritionNormalizer._to_numeric(calories)

            # 3. Normalize Macros
            raw_macros = raw_data.get("macros", {})
            macros = {
                "protein": NutritionNormalizer._to_numeric(raw_macros.get("protein", 0)),
                "carbs": NutritionNormalizer._to_numeric(raw_macros.get("carbs", 0)),
                "fat": NutritionNormalizer._to_numeric(raw_macros.get("fat", 0))
            }

            return {
                "food_name": food_name,
                "calories": calories,
                "macros": macros
            }

        except Exception as e:
            logger.error(f"Normalization failed: {e}")
            # Return a safe fallback structure if parsing fails completely
            return {
                "food_name": "Analysis Failed",
                "calories": 0,
                "macros": {"protein": 0, "carbs": 0, "fat": 0}
            }

    @staticmethod
    def _to_numeric(value):
        """
        Helper method to convert potential strings (like '150g' or 'approx 200') 
        to a clean float/int.
        """
        if isinstance(value, (int, float)):
            return value
        
        if isinstance(value, str):
            # Extract only digits and decimal points
            cleaned = "".join(char for char in value if char.isdigit() or char == ".")
            try:
                return float(cleaned) if "." in cleaned else int(cleaned)
            except ValueError:
                return 0
        
        return 0