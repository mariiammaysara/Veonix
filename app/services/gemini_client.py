import json
import logging
import re
from typing import Any, Dict, List, Optional

import google.generativeai as genai
from fastapi import HTTPException

from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiClient:
    """
    Clean wrapper around Gemini Vision API.
    Handles:
    - model setup
    - generating content from image + prompt
    - extracting JSON safely
    - repairing malformed JSON
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None
    ) -> None:

        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GEMINI_MODEL

        if not self.api_key:
            raise ValueError("Missing GEMINI_API_KEY.")
        if not self.model_name:
            raise ValueError("Missing GEMINI_MODEL.")

        genai.configure(api_key=self.api_key)

    # Public API
    def list_models(self) -> List[Dict[str, Any]]:
        """Return all available models."""
        try:
            models = genai.list_models()
            return [
                m.to_dict() if hasattr(m, "to_dict")
                else {"name": getattr(m, "name", str(m))}
                for m in models
            ]
        except Exception as exc:
            logger.exception("Failed to list models")
            raise HTTPException(
                status_code=502,
                detail=f"Failed to list models: {exc}"
            )

    def analyze_image_with_prompt(
        self,
        image_bytes: bytes,
        prompt: str,
        mime_type: str = "image/jpeg",
    ) -> Dict[str, Any]:

        try:
            model = genai.GenerativeModel(self.model_name)

            response = model.generate_content(
                [
                    {"mime_type": mime_type, "data": image_bytes},
                    prompt,
                ]
            )

            raw_text = getattr(response, "text", "") or ""
            logger.error(f"RAW GEMINI OUTPUT:\n{raw_text}")

            cleaned = self._extract_json(raw_text)
            logger.error(f"CLEANED JSON CANDIDATE:\n{cleaned}")

            # First attempt
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                pass

            # Attempt repair
            repaired = self._attempt_repair(cleaned)
            return repaired

        except HTTPException:
            raise

        except Exception as exc:
            logger.exception("Gemini Vision API error")
            raise HTTPException(
                status_code=502,
                detail=f"Gemini Vision API Error: {exc}"
            )

    # JSON Extractor 
    @staticmethod
    def _extract_json(text: str) -> str:
        """
        Robust JSON extractor.
        Removes ``` blocks and extracts the first valid {...} block.
        """

        if not isinstance(text, str):
            return str(text)

        text = text.strip()

        # Remove ```json and ``` fully
        text = text.replace("```json", "")
        text = text.replace("```", "").strip()

        # Extract the FIRST JSON object { ... }
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            return match.group(0).strip()

        return text

    # JSON Auto-Repair
    def _attempt_repair(self, text: str) -> Dict[str, Any]:
        """
        Simple repair attempts when JSON is almost valid.
        """

        # Fix missing closing brace
        if text.count("{") == text.count("}") + 1:
            candidate = text + "}"
            try:
                return json.loads(candidate)
            except Exception:
                pass

        # Remove trailing commas
        cleaned = text.replace(",}", "}").replace(",]", "]")
        try:
            return json.loads(cleaned)
        except Exception:
            pass

        logger.error("JSON repair failed")
        raise HTTPException(
            status_code=502,
            detail="Gemini returned invalid JSON (repair failed)."
        )
