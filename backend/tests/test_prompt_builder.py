"""
Tests for the dynamic prompt builder functions in src/helpers/prompts.py.

Asserts that:
  - build_vision_prompt() returns the base GEMINI_PROMPT unchanged for None/unknown goals
  - Cutting-goal prompt contains calorie deficit language
  - Bulking-goal prompt contains surplus/protein language
  - Partial keyword matching works (e.g. "weight loss" → cutting footer)
  - build_coach_prompt() adjusts tone based on dietary goal
"""

import pytest
from src.helpers.prompts import (
    GEMINI_PROMPT,
    build_vision_prompt,
    build_coach_prompt,
)


# ── build_vision_prompt tests ──────────────────────────────────────────────────

def test_default_prompt_equals_base_for_none_goal():
    """
    build_vision_prompt(None) must return the exact base GEMINI_PROMPT unchanged.
    """
    result = build_vision_prompt(None)
    assert result == GEMINI_PROMPT


def test_default_prompt_equals_base_for_unknown_goal():
    """
    build_vision_prompt() with an unrecognized goal string falls back to base prompt.
    """
    result = build_vision_prompt("paleo")
    assert result == GEMINI_PROMPT
    result2 = build_vision_prompt("vegetarian")
    assert result2 == GEMINI_PROMPT


def test_cutting_prompt_contains_calorie_flag():
    """
    Cutting goal prompt must contain language about calorie density/deficit framing.
    """
    result = build_vision_prompt("cutting")
    assert result != GEMINI_PROMPT, "Cutting prompt should differ from base"
    prompt_lower = result.lower()
    assert "calorie" in prompt_lower
    assert "deficit" in prompt_lower or "calorie-dense" in prompt_lower or "calorie density" in prompt_lower


def test_cutting_prompt_partial_keyword_weight_loss():
    """
    Partial keyword 'weight loss' should map to the cutting footer.
    """
    result = build_vision_prompt("weight loss")
    assert result != GEMINI_PROMPT
    assert "calorie" in result.lower()


def test_cutting_prompt_partial_keyword_lean():
    """
    Partial keyword 'lean' should map to the cutting footer.
    """
    result = build_vision_prompt("lean body")
    assert result != GEMINI_PROMPT
    assert "calorie" in result.lower()


def test_bulking_prompt_contains_surplus_language():
    """
    Bulking goal prompt must contain calorie surplus and protein language.
    """
    result = build_vision_prompt("bulking")
    assert result != GEMINI_PROMPT, "Bulking prompt should differ from base"
    prompt_lower = result.lower()
    assert "protein" in prompt_lower
    assert "calorie" in prompt_lower
    assert "surplus" in prompt_lower or "muscle" in prompt_lower


def test_bulking_prompt_partial_keyword_muscle_gain():
    """
    Partial keyword 'muscle gain' should map to the bulking footer.
    """
    result = build_vision_prompt("muscle gain")
    assert result != GEMINI_PROMPT
    assert "protein" in result.lower()


def test_maintenance_prompt_contains_balance_language():
    """
    Maintenance goal prompt must contain balanced/precision language.
    """
    result = build_vision_prompt("maintenance")
    assert result != GEMINI_PROMPT, "Maintenance prompt should differ from base"
    prompt_lower = result.lower()
    # The maintenance footer text includes "balanced" and "precision"
    assert "balanced" in prompt_lower or "precision" in prompt_lower


def test_prompt_still_starts_with_base():
    """
    All goal-framed prompts must start with the base GEMINI_PROMPT content
    to ensure the JSON schema instructions are always included.
    """
    for goal in ["cutting", "bulking", "maintenance"]:
        result = build_vision_prompt(goal)
        # The base prompt must be a prefix (footer is appended, not prepended)
        assert result.startswith(GEMINI_PROMPT.rstrip()), (
            f"Goal '{goal}' prompt must start with base GEMINI_PROMPT"
        )


def test_prompt_case_insensitive():
    """
    Goal matching must be case-insensitive.
    """
    upper = build_vision_prompt("CUTTING")
    lower = build_vision_prompt("cutting")
    mixed = build_vision_prompt("CuTtInG")
    assert upper == lower == mixed


# ── build_coach_prompt tests ───────────────────────────────────────────────────

def make_coach_prompt(goal: str | None) -> str:
    """Helper to call build_coach_prompt with minimal boilerplate."""
    return build_coach_prompt(
        question="What should I eat for lunch?",
        dietary_goal=goal,
        profile_context=f"Dietary Goal: {goal or 'None'}\nAllergies: None",
        meals_context="No recent meals logged.",
        db_summary="Source: Local, Content: Chicken breast is a lean protein source.",
    )


def test_coach_prompt_cutting_tone():
    """
    Cutting coach prompt must mention deficit, satiety, or lean framing.
    """
    result = make_coach_prompt("cutting")
    result_lower = result.lower()
    assert "deficit" in result_lower or "satiety" in result_lower or "lean protein" in result_lower


def test_coach_prompt_bulking_tone():
    """
    Bulking coach prompt must mention surplus or calorie-dense options.
    """
    result = make_coach_prompt("bulking")
    result_lower = result.lower()
    assert "surplus" in result_lower or "calorie-dense" in result_lower or "muscle" in result_lower


def test_coach_prompt_maintenance_tone():
    """
    Maintenance coach prompt must mention balance or sustainable patterns.
    """
    result = make_coach_prompt("maintenance")
    result_lower = result.lower()
    # The maintenance tone text contains "body composition" and "sustainable"
    assert "body composition" in result_lower or "sustainable" in result_lower or "balanced" in result_lower


def test_coach_prompt_none_goal_is_generic():
    """
    build_coach_prompt(dietary_goal=None) must produce a valid prompt (no crash)
    with at least the user question embedded.
    """
    result = make_coach_prompt(None)
    assert "What should I eat for lunch?" in result
    assert len(result) > 100  # Non-trivially short


def test_coach_prompt_contains_user_question():
    """
    All coaching prompts must embed the original user question.
    """
    for goal in [None, "cutting", "bulking", "maintenance"]:
        result = make_coach_prompt(goal)
        assert "What should I eat for lunch?" in result


def test_coach_prompt_contains_db_summary():
    """
    All coaching prompts must include the source information.
    """
    for goal in [None, "cutting", "bulking"]:
        result = make_coach_prompt(goal)
        assert "Chicken breast is a lean protein source." in result


def test_coach_prompt_cutting_partial_keyword():
    """
    Partial keyword 'weight loss' in goal should produce cutting tone for coaching.
    """
    result = build_coach_prompt(
        question="Best snack?",
        dietary_goal="weight loss",
        profile_context="Dietary Goal: weight loss\nAllergies: None",
        meals_context="No recent meals.",
        db_summary="Source: Local, Content: Almonds are a satisfying snack.",
    )
    result_lower = result.lower()
    assert "deficit" in result_lower or "satiety" in result_lower or "lean" in result_lower
