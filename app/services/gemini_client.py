import json
import logging
from typing import Any, Dict, List, Optional

import google.generativeai as genai
from fastapi import HTTPException

from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiClient:
    """
    Updated client compatible with NEW Gemini API keys.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GEMINI_MODEL

        if not self.api_key:
            raise ValueError("Missing GEMINI_API_KEY")
        if not self.model_name:
            raise ValueError("Missing GEMINI_MODEL")

        # NEW authentication system
        genai.configure(api_key=self.api_key)

        # Pre-load model
        self.model = genai.GenerativeModel(self.model_name)

    def list_models(self) -> List[Dict[str, Any]]:
        """List available models."""
        try:
            models = genai.list_models()
            return [{"name": m.name} for m in models]
        except Exception as exc:
            raise HTTPException(
                status_code=502, detail=f"Failed to list models: {exc}"
            )

    def analyze_image_with_prompt(
        self, image_bytes: bytes, prompt: str, mime_type: str = "image/jpeg"
    ) -> Dict[str, Any]:

        try:
            response = self.model.generate_content(
                [
                    {"mime_type": mime_type, "data": image_bytes},
                    prompt,
                ]
            )

            raw = response.text or ""
            logger.warning(f"RAW GEMINI OUTPUT:\n{raw}")

            json_string = self._extract_json(raw)

            try:
                return json.loads(json_string)
            except json.JSONDecodeError:
                return self._attempt_repair(json_string)

        except Exception as exc:
            logger.exception("Gemini Vision API error")
            raise HTTPException(
                status_code=502,
                detail=str(exc)
            )

    # ---------------------
    # JSON Extraction Logic
    # ---------------------

    @staticmethod
    def _extract_json(text: str) -> str:
        """Extract JSON block from Gemini response."""
        import re

        if not isinstance(text, str):
            return str(text)

        text = text.strip()

        text = text.replace("```json", "").replace("```", "")

        # match first {...} block
        match = re.search(r"\{[\s\S]*\}", text)
        return match.group(0) if match else text

    def _attempt_repair(self, text: str) -> Dict[str, Any]:
        """Try to fix slightly invalid JSON."""
        try:
            fixed = text.replace(",}", "}").replace(",]", "]")
            return json.loads(fixed)
        except:
            raise HTTPException(
                status_code=502,
                detail="Gemini returned invalid JSON"
            )
