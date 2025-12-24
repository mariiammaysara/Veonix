from google import genai
from google.genai import types
import json
import io
import logging
from PIL import Image
from app.core.config import get_settings

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self) -> None:
        settings = get_settings()
        api_key = settings.gemini_api_key.strip().replace('"', '').replace("'", "")
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-3-flash-preview"

    async def analyze_food_image(self, image_bytes: bytes, mime_type: str):
        try:
            img = Image.open(io.BytesIO(image_bytes))
            img.thumbnail((512, 512))
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=75)
            img_data = buffer.getvalue()

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
            """

            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[
                    prompt,
                    types.Part.from_bytes(data=img_data, mime_type="image/jpeg")
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )

            if not response.text:
                raise ValueError("No response text")

            data = json.loads(response.text)

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
            logger.error(f"Gemini Error: {str(e)}")
            raise e