import json
import logging
from typing import Optional, Dict, Any

import google.generativeai as genai
from fastapi import HTTPException

from app.core.config import settings

logger = logging.getLogger(__name__)

CLASSIFIER_PROMPT = """
You are a food classification system.
Your task is to determine whether the food in the image is:

1. "packaged" → food inside a wrapper, bag, plastic container, box, or sealed packaging.
2. "fresh" → food served on a plate, bowl, tray, cup, or directly visible.

Return ONLY valid JSON in this structure:

{
  "type": "packaged" or "fresh"
}

Do NOT return any explanation.
"""


class FoodClassifier:
    """
    Robust classifier for fresh vs packaged foods.
    Cleans, extracts, and repairs JSON from model output.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GEMINI_MODEL

        if not self.api_key:
            raise ValueError("Missing GEMINI_API_KEY.")
        if not self.model_name:
            raise ValueError("Missing GEMINI_MODEL.")

        genai.configure(api_key=self.api_key)

    def detect_type(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
        try:
            model = genai.GenerativeModel(self.model_name)

            response = model.generate_content(
                [
                    {"mime_type": mime_type, "data": image_bytes},
                    CLASSIFIER_PROMPT,
                ]
            )

            raw_text = (getattr(response, "text", "") or "").strip()
            logger.error(f"[Classifier] RAW OUTPUT:\n{raw_text}")

            json_text = self._extract_json(raw_text)
            logger.error(f"[Classifier] CLEANED JSON:\n{json_text}")

            try:
                data = json.loads(json_text)
            except json.JSONDecodeError:
                data = self._attempt_repair(json_text)

            food_type = (data.get("type") or "").strip().lower()

            if food_type in {"fresh", "packaged"}:
                return food_type

            raise ValueError("Classifier returned an invalid type.")

        except Exception as exc:
            logger.exception("Type classification failed")
            raise HTTPException(
                status_code=502,
                detail=f"Failed to classify food type: {exc}"
            )

    @staticmethod
    def _extract_json(text: str) -> str:
        if not isinstance(text, str):
            return str(text)

        t = text.strip()

        # Remove markdown fences
        t = t.replace("```json", "").replace("```", "").strip()

        # Extract inside first { ... last }
        if "{" in t and "}" in t:
            try:
                start = t.index("{")
                end = t.rindex("}") + 1
                t = t[start:end]
            except Exception:
                pass

        if t.lower().startswith("json"):
            t = t[4:].strip()

        return t.strip()

    @staticmethod
    def _attempt_repair(text: str) -> Dict[str, Any]:
        # Missing closing brace
        if text.count("{") == text.count("}") + 1:
            try:
                return json.loads(text + "}")
            except Exception:
                pass

        # Remove trailing commas
        cleaned = text.replace(",}", "}").replace(",]", "]")
        try:
            return json.loads(cleaned)
        except Exception:
            pass

        logger.error("[Classifier] JSON repair failed")
        raise HTTPException(
            status_code=502,
            detail="Classifier returned invalid JSON (repair failed)."
        )
