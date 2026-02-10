
import json
import logging
import base64
import io
from PIL import Image
from app.core.services.vision import analyze_image

logger = logging.getLogger(__name__)

class FoodAnalyzer:
    def __init__(self) -> None:
        pass

    async def analyze_food_image(self, image_bytes: bytes, mime_type: str) -> dict:
        """
        Analyzes an image to determine if it contains food and extracts nutritional info.
        """
        try:
            # Optimize image (resize and convert to JPEG)
            img = Image.open(io.BytesIO(image_bytes))
            img.thumbnail((512, 512)) # Maintain aspect ratio, max 512x512
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=75)
            optimized_image_bytes = buffer.getvalue()
            mime_type = "image/jpeg" # Always JPEG after conversion

            # Convert bytes to base64 data URL
            base64_image = base64.b64encode(optimized_image_bytes).decode('utf-8')
            image_url = f"data:{mime_type};base64,{base64_image}"

            prompt = """
            Analyze the image and determine if it contains food.
            Return ONLY JSON with this structure:
            {
              "is_food": boolean,
              "food_name": "string",
              "calories": number,
              "macros": {
                "protein": number,
                "carbs": number,
                "fat": number
              }
            }
            If the image does not contain edible food, set is_food to false and values to 0.
            Response must be valid JSON without markdown formatting.
            """

            # Call the vision service
            response_text = await analyze_image(image_url, prompt)

            # Clean potential markdown formatting
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            data = json.loads(response_text)

            return {
                "is_food": bool(data.get("is_food", True)),
                "food_name": data.get("food_name", "Unknown Food"),
                "calories": float(data.get("calories", 0)),
                "macros": {
                    "protein": float(data.get("macros", {}).get("protein", 0)),
                    "carbs": float(data.get("macros", {}).get("carbs", 0)),
                    "fat": float(data.get("macros", {}).get("fat", 0))
                }
            }

        except Exception as e:
            logger.error(f"Food Analysis Error: {str(e)}")
            raise e
