"""
Module: response_parser
Layer:  Helpers

Parses and validates raw LLM JSON responses into typed VisionResult dataclasses.
Implements defensive parsing to handle probabilistic model output gracefully.

Author: Mariam Maysara
"""

import json
import logging
from src.providers.vision.base import VisionResult
from src.exceptions import VisionProviderError

logger = logging.getLogger(__name__)

# Valid sets for enum validation at the helper boundary
VALID_MEAL_TYPES   = {"breakfast", "lunch", "dinner", "snack", "drink", "dessert"}
VALID_PREP_METHODS = {"raw", "grilled", "fried", "baked", "boiled", "steamed", "mixed", "unknown"}


def parse_gemini_response(raw: str) -> VisionResult:
    """
    Transforms raw text from Gemini into a validated VisionResult.
    Handles common LLM formatting issues like markdown fences.

    Args:
        raw: The raw string response from the AI.

    Returns:
        A validated VisionResult object.

    Raises:
        VisionProviderError: If the JSON is unparseable or critical fields are missing.
    """
    try:
        # LLMs often wrap JSON in triple backticks even when told not to,
        # sometimes with a language tag (```json) and sometimes without (```).
        clean = raw.strip()
        if clean.startswith("```"):
            clean = clean.removeprefix("```json").removeprefix("```")
        clean = clean.removesuffix("```").strip()
        data = json.loads(clean)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse failed: {e} | Raw: {raw[:200]}")
        raise VisionProviderError(f"Invalid Gemini response: {e}")

    food_name = data.get("food_name", "").strip()
    if not food_name:
        raise VisionProviderError("Gemini did not return a food name")

    nutrition = data.get("nutrition", {})
    per_100g  = nutrition.get("per_100g", {})

    return VisionResult(
        food_name=food_name,
        # Clamping and default value fallbacks ensure system stability
        confidence=_safe_float(data.get("confidence"), 0.8, 0.0, 1.0),
        ingredients=_safe_list(data.get("ingredients")),
        estimated_weight_grams=_safe_int(data.get("estimated_weight_grams"), 200, 1, 5000),
        meal_type=_safe_enum(data.get("meal_type"), VALID_MEAL_TYPES, "unknown"),
        cuisine=str(data.get("cuisine", "unknown")).strip() or "unknown",
        preparation_method=_safe_enum(data.get("preparation_method"), VALID_PREP_METHODS, "unknown"),
        calories=_safe_float(nutrition.get("calories"), 0.0, 0.0, 10000.0),
        protein=_safe_float(nutrition.get("protein"), 0.0, 0.0, 1000.0),
        carbs=_safe_float(nutrition.get("carbs"), 0.0, 0.0, 1000.0),
        fat=_safe_float(nutrition.get("fat"), 0.0, 0.0, 1000.0),
        fiber=_safe_float(nutrition.get("fiber"), 0.0, 0.0, 1000.0),
        sodium=_safe_float(nutrition.get("sodium"), 0.0, 0.0, 100000.0),
        per_100g={
            "calories": _safe_float(per_100g.get("calories"), 0.0, 0.0, 10000.0),
            "protein":  _safe_float(per_100g.get("protein"),  0.0, 0.0, 1000.0),
            "carbs":    _safe_float(per_100g.get("carbs"),    0.0, 0.0, 1000.0),
            "fat":      _safe_float(per_100g.get("fat"),      0.0, 0.0, 1000.0),
            "fiber":    _safe_float(per_100g.get("fiber"),    0.0, 0.0, 1000.0),
            "sodium":   _safe_float(per_100g.get("sodium"),   0.0, 0.0, 100000.0),
        },
    )


def _safe_float(v, default, min_val, max_val):
    """Safely converts a value to float with range clamping."""
    try: return max(min_val, min(max_val, float(v)))
    except (TypeError, ValueError, AttributeError): return default

def _safe_int(v, default, min_val, max_val):
    """Safely converts a value to int with range clamping."""
    try: return max(min_val, min(max_val, int(float(v))))
    except (TypeError, ValueError, AttributeError): return default

def _safe_list(v) -> list[str]:
    """Ensures input is a list of strings, capped at 6 items."""
    return [str(i).strip() for i in v if i][:6] if isinstance(v, list) else []

def _safe_enum(v, valid_set, default):
    """Fallback mechanism for non-conforming model output."""
    return v.lower() if isinstance(v, str) and v.lower() in valid_set else default
