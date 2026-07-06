"""
Module: prompts
Layer:  Helpers

Centralized prompt management.
Contains all LLM system and user instructions to avoid inlining in provider code.
Uses explicit JSON schemas to minimize hallucinations and parsing failures.

Author: Mariam Maysara
"""

# ── Base Vision Prompt ────────────────────────────────────────────────────────
# Consolidated prompt for Gemini Vision.
# Requests food identity and nutrition in a single multimodal pass to reduce latency.
GEMINI_PROMPT = """
Analyze this food image and return a JSON object with food identification AND nutrition data.

Return ONLY this JSON structure, no markdown, no explanation:

{
  "food_name": "<name of the food you see>",
  "confidence": <0.0 to 1.0>,
  "ingredients": ["<ingredient1>", "<ingredient2>"],
  "estimated_weight_grams": <total weight as integer>,
  "meal_type": "<breakfast or lunch or dinner or snack or drink or dessert>",
  "cuisine": "<cuisine type>",
  "preparation_method": "<raw or grilled or fried or baked or boiled or steamed or mixed or unknown>",
  "nutrition": {
    "calories": <total kcal for the estimated weight>,
    "protein": <grams>,
    "carbs": <grams>,
    "fat": <grams>,
    "fiber": <grams>,
    "sodium": <milligrams>,
    "per_100g": {
      "calories": <kcal per 100g>,
      "protein": <g per 100g>,
      "carbs": <g per 100g>,
      "fat": <g per 100g>,
      "fiber": <g per 100g>,
      "sodium": <mg per 100g>
    }
  }
}

IMPORTANT:
- Nutrition values must be accurate and realistic
- Scale total nutrition to the estimated_weight_grams
- per_100g values are the base values before scaling
- Return ONLY the JSON object
"""


# ── Prompt Builders ───────────────────────────────────────────────────────────

# Goal-framing footers injected into the vision prompt.
# These do NOT change the JSON schema — they only add an advisory
# comment that nudges Gemini toward goal-relevant nutrition accuracy.
_VISION_GOAL_FOOTERS: dict[str, str] = {
    "cutting": (
        "\nNUTRITION ADVISORY (user goal: cutting/fat loss): "
        "Pay special attention to calorie density. "
        "Flag if the meal is calorie-dense. "
        "Emphasize accurate protein-to-calorie ratio in your estimates. "
        "Ensure carbs and fat values are not under-reported."
    ),
    "bulking": (
        "\nNUTRITION ADVISORY (user goal: bulking/muscle gain): "
        "Emphasize total calorie content and caloric surplus potential. "
        "Highlight protein content for muscle synthesis. "
        "Ensure calorie and carbohydrate values are not under-reported."
    ),
    "maintenance": (
        "\nNUTRITION ADVISORY (user goal: maintenance): "
        "Provide balanced and accurate estimates across all macros. "
        "No special emphasis needed — precision across all fields is key."
    ),
}

# Goal-framing instructions for the coaching response tone.
_COACH_GOAL_TONES: dict[str, str] = {
    "cutting": (
        "The user is focused on fat loss (cutting). "
        "Frame your response around staying in a calorie deficit, prioritizing satiety, "
        "lean protein sources, and avoiding excess carbs or fats. "
        "Mention calorie density and how this fits their deficit goal."
    ),
    "bulking": (
        "The user is focused on muscle gain (bulking). "
        "Frame your response around achieving a calorie surplus, "
        "prioritizing high-protein and calorie-dense options, "
        "and optimal nutrient timing for muscle synthesis."
    ),
    "maintenance": (
        "The user is focused on maintaining their current weight and body composition. "
        "Frame your response around balanced nutrition, "
        "hitting protein targets without excess calories, "
        "and sustainable eating patterns."
    ),
}


def build_vision_prompt(dietary_goal: str | None) -> str:
    """
    Builds a goal-aware vision analysis prompt.

    Appends a non-schema-breaking nutrition advisory footer to GEMINI_PROMPT
    based on the user's dietary goal. This influences Gemini's attention
    toward goal-relevant macro accuracy without changing the JSON output schema.

    Args:
        dietary_goal: The user's dietary goal string (e.g. "cutting", "bulking",
                      "maintenance"), or None for the default prompt.

    Returns:
        Full prompt string to pass to GeminiProvider.analyze().
    """
    if not dietary_goal:
        return GEMINI_PROMPT

    # Normalize to lowercase for case-insensitive matching
    goal_lower = dietary_goal.lower().strip()

    # Check for partial matches (e.g. "weight loss" → "cutting", "gain" → "bulking")
    if any(kw in goal_lower for kw in ["cut", "loss", "deficit", "lean"]):
        footer = _VISION_GOAL_FOOTERS["cutting"]
    elif any(kw in goal_lower for kw in ["bulk", "gain", "muscle", "surplus"]):
        footer = _VISION_GOAL_FOOTERS["bulking"]
    elif any(kw in goal_lower for kw in ["mainten", "balance"]):
        footer = _VISION_GOAL_FOOTERS["maintenance"]
    else:
        return GEMINI_PROMPT  # Unknown goal — return base prompt unchanged

    return GEMINI_PROMPT + footer


def build_coach_prompt(
    question: str,
    dietary_goal: str | None,
    profile_context: str,
    meals_context: str,
    db_summary: str,
) -> str:
    """
    Builds a profile-aware coaching prompt for the knowledge node.

    Adjusts the AI coach's tone and framing based on the user's dietary goal
    so that responses are contextually relevant to their specific nutrition objective.

    Args:
        question: The user's original nutrition question.
        dietary_goal: User's dietary goal string, or None.
        profile_context: Pre-formatted string of goal + allergies from profile.
        meals_context: Pre-formatted recent meal log string.
        db_summary: The source information (RAG chunk or Tavily result).

    Returns:
        Full prompt string ready to send to the coaching model.
    """
    if not dietary_goal:
        goal_lower = ""
    else:
        goal_lower = dietary_goal.lower().strip()

    if any(kw in goal_lower for kw in ["cut", "loss", "deficit", "lean"]):
        goal_tone = _COACH_GOAL_TONES["cutting"]
    elif any(kw in goal_lower for kw in ["bulk", "gain", "muscle", "surplus"]):
        goal_tone = _COACH_GOAL_TONES["bulking"]
    elif any(kw in goal_lower for kw in ["mainten", "balance"]):
        goal_tone = _COACH_GOAL_TONES["maintenance"]
    else:
        goal_tone = (
            "Provide a friendly, accurate, and helpful nutrition coaching response. "
            "Be concise and direct."
        )

    return f"""You are a friendly AI nutrition coach. Answer the user's question about nutrition/health using the provided information source.

User Profile:
{profile_context}

Recent Meals Memory:
{meals_context}

Coaching Tone Instruction:
{goal_tone}

User Question: "{question}"
Information Source Details: {db_summary}

Be concise, helpful, and direct. Translate the source information into a friendly response.
Ensure you take the user's goal and allergies into consideration. If the information source contradicts their allergies, provide warning feedback.
"""
