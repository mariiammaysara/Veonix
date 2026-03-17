"""
Tests for Gemini response parser.
No real API calls — tests pure parsing logic only.
"""

import pytest
from src.helpers.response_parser import parse_gemini_response
from src.exceptions import VisionProviderError


def test_parses_valid_gemini_response():
    raw = """
    {
      "food_name": "Grilled Chicken Breast",
      "confidence": 0.95,
      "ingredients": ["chicken", "salt", "pepper"],
      "estimated_weight_grams": 250,
      "meal_type": "lunch",
      "cuisine": "American",
      "preparation_method": "grilled",
      "nutrition": {
        "calories": 412,
        "protein": 75,
        "carbs": 0,
        "fat": 9,
        "fiber": 0,
        "sodium": 180,
        "per_100g": {
          "calories": 165,
          "protein": 31,
          "carbs": 0,
          "fat": 3.6,
          "fiber": 0,
          "sodium": 72
        }
      }
    }
    """
    result = parse_gemini_response(raw)
    assert result.food_name == "Grilled Chicken Breast"
    assert result.confidence == 0.95
    assert result.calories == 412.0
    assert result.per_100g["protein"] == 31.0


def test_strips_markdown_fences():
    raw = '```json\n{"food_name": "Rice", "confidence": 0.8, "ingredients": [], "estimated_weight_grams": 200, "meal_type": "lunch", "cuisine": "unknown", "preparation_method": "boiled", "nutrition": {}}\n```'
    result = parse_gemini_response(raw)
    assert result.food_name == "Rice"


def test_uses_defaults_for_missing_fields():
    raw = '{"food_name": "Pizza"}'
    result = parse_gemini_response(raw)
    assert result.confidence == 0.8
    assert result.estimated_weight_grams == 200
    assert result.calories == 0.0


def test_raises_on_invalid_json():
    with pytest.raises(VisionProviderError):
        parse_gemini_response("this is not json")


def test_raises_on_missing_food_name():
    with pytest.raises(VisionProviderError):
        parse_gemini_response('{"confidence": 0.9}')
