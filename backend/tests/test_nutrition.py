"""
Tests for USDA nutrition provider helpers.
No real API calls — tests pure logic only.
"""

import pytest
from src.helpers.prompts import build_usda_query
from src.providers.nutrition.usda_provider import USDAProvider


# ── build_usda_query tests ─────────────────────────────────

def test_removes_cuisine_descriptors():
    assert build_usda_query("Egyptian Grilled Chicken") == "grilled chicken"

def test_removes_homemade():
    assert build_usda_query("Homemade Caesar Salad") == "caesar salad"

def test_keeps_preparation_method():
    result = build_usda_query("Fried Eggs with Butter")
    assert "fried" in result
    assert "eggs" in result

def test_handles_simple_name():
    assert build_usda_query("White Rice") == "white rice"

def test_handles_mixed_case():
    result = build_usda_query("GRILLED SALMON")
    assert result == "grilled salmon"


# ── USDAProvider._pick_best tests ─────────────────────────

def test_pick_best_prefers_foundation():
    provider = USDAProvider()
    foods = [
        {"fdcId": 1, "description": "Rice", "dataType": "Survey (FNDDS)", "foodNutrients": []},
        {"fdcId": 2, "description": "Rice", "dataType": "Foundation", "foodNutrients": []},
        {"fdcId": 3, "description": "Rice", "dataType": "SR Legacy", "foodNutrients": []},
    ]
    best = provider._pick_best(foods)
    assert best["dataType"] == "Foundation"

def test_pick_best_falls_back_to_sr_legacy():
    provider = USDAProvider()
    foods = [
        {"fdcId": 1, "description": "Rice", "dataType": "Survey (FNDDS)", "foodNutrients": []},
        {"fdcId": 2, "description": "Rice", "dataType": "SR Legacy", "foodNutrients": []},
    ]
    best = provider._pick_best(foods)
    assert best["dataType"] == "SR Legacy"


# ── USDAProvider._scale tests ──────────────────────────────

def test_scale_100g_returns_same():
    provider = USDAProvider()
    per_100g = {"calories": 165.0, "protein": 31.0, "fat": 3.6, "carbs": 0.0, "fiber": 0.0, "sodium": 74.0}
    result = provider._scale(per_100g, 100)
    assert result["calories"] == 165.0

def test_scale_200g_doubles():
    provider = USDAProvider()
    per_100g = {"calories": 100.0, "protein": 10.0, "fat": 5.0, "carbs": 20.0, "fiber": 2.0, "sodium": 50.0}
    result = provider._scale(per_100g, 200)
    assert result["calories"] == 200.0
    assert result["protein"] == 20.0

def test_scale_280g_chicken():
    provider = USDAProvider()
    per_100g = {"calories": 165.0, "protein": 31.0, "fat": 3.6, "carbs": 0.0, "fiber": 0.0, "sodium": 74.0}
    result = provider._scale(per_100g, 280)
    assert result["calories"] == 462.0
    assert result["protein"] == 86.8
