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

To reduce portion estimation errors, you MUST perform step-by-step chain-of-thought reasoning inside the JSON object's "reasoning" field BEFORE committing to a weight estimate. Follow these guidelines:
1. Identify all visible food items in the image.
2. Detect portion size cues and reference objects for scale (e.g., plate size, cup size, utensils, hands, packaging, or table texture). If no size reference object is visible, you MUST honestly lower your "confidence" score (e.g. to 0.40 - 0.60) and note the lack of reference in the reasoning field.
3. Internally estimate a plausible low and high range for the portion weight (in grams) based on the scale cues, then select a realistic single point estimate within that range.
4. Scale all total nutritional values (calories, protein, carbs, fat, fiber, sodium) precisely to the estimated weight, keeping base per_100g values accurate.

Ensure the "reasoning" field is the first field in the returned JSON object.

---

### FEW-SHOT EXAMPLES

#### Example 1: Single item with clear scale reference (Red Apple next to a fork)
- Context: A medium red apple is sitting on a white plate next to a standard metal dinner fork.
- Expected JSON Output:
{
  "reasoning": "1. Visible items: One whole red apple. 2. Scale references: A standard dining plate (approx. 25cm) and a standard metal fork (approx. 20cm) are visible next to the apple, providing clear scale. 3. Portions: The apple is average-sized relative to the fork. Plausible weight range: 150g - 200g. Point estimate: 175g. 4. Confidence: High (0.95) due to clear utensil and plate size references. 5. Nutrition: Base apple per_100g is 52 kcal. Total calories scaled to 175g is 91 kcal.",
  "food_name": "Red Apple",
  "confidence": 0.95,
  "ingredients": ["apple"],
  "estimated_weight_grams": 175,
  "meal_type": "snack",
  "cuisine": "fruit",
  "preparation_method": "raw",
  "nutrition": {
    "calories": 91.0,
    "protein": 0.45,
    "carbs": 24.5,
    "fat": 0.35,
    "fiber": 4.2,
    "sodium": 1.75,
    "per_100g": {
      "calories": 52.0,
      "protein": 0.26,
      "carbs": 14.0,
      "fat": 0.2,
      "fiber": 2.4,
      "sodium": 1.0
    }
  }
}

#### Example 2: Mixed dish with overlapping ingredients (Chicken Salad Bowl with a hand for scale)
- Context: A salad bowl containing lettuce, diced tomatoes, grilled chicken pieces, and olive oil dressing. A human hand is holding the bowl.
- Expected JSON Output:
{
  "reasoning": "1. Visible items: Lettuce greens, tomatoes, cubed grilled chicken breast, and olive oil dressing. 2. Scale references: A human hand holding the bowl provides a reliable size context. The bowl diameter is approx. 18cm. 3. Portions: Lettuce (approx. 90g), tomato (approx. 60g), chicken (approx. 100g), olive oil (approx. 10g). Plausible weight range: 240g - 280g. Point estimate: 260g. 4. Confidence: High (0.90) as the hand and bowl diameter provide good scale indicators. 5. Nutrition: Scaled using composite ingredient macros to 260g total weight.",
  "food_name": "Grilled Chicken Salad",
  "confidence": 0.90,
  "ingredients": ["lettuce", "tomato", "chicken breast", "olive oil"],
  "estimated_weight_grams": 260,
  "meal_type": "lunch",
  "cuisine": "American",
  "preparation_method": "mixed",
  "nutrition": {
    "calories": 302.0,
    "protein": 32.2,
    "carbs": 4.8,
    "fat": 17.2,
    "fiber": 1.8,
    "sodium": 195.0,
    "per_100g": {
      "calories": 116.15,
      "protein": 12.38,
      "carbs": 1.85,
      "fat": 6.62,
      "fiber": 0.69,
      "sodium": 75.0
    }
  }
}

#### Example 3: Single item with NO visible scale reference (Chocolate Chip Cookie close-up)
- Context: A close-up photograph of a chocolate chip cookie on a neutral table. No plates, utensils, hands, or other recognizable objects are visible in the shot.
- Expected JSON Output:
{
  "reasoning": "1. Visible items: One chocolate chip cookie. 2. Scale references: None. No plates, utensils, hands, or other standard items are visible to establish scale. Table texture is plain. 3. Portions: Lack of reference makes size estimation highly uncertain. A cookie can range from a small 25g snack to a large 80g bakery style cookie. Without cues, we estimate a moderate size. Plausible range: 30g - 60g. Point estimate: 45g. 4. Confidence: Low (0.50) due to complete absence of size/scale references. 5. Nutrition: Scaled standard cookie macros to 45g.",
  "food_name": "Chocolate Chip Cookie",
  "confidence": 0.50,
  "ingredients": ["flour", "sugar", "butter", "chocolate chips"],
  "estimated_weight_grams": 45,
  "meal_type": "snack",
  "cuisine": "American",
  "preparation_method": "baked",
  "nutrition": {
    "calories": 220.0,
    "protein": 2.2,
    "carbs": 29.2,
    "fat": 11.2,
    "fiber": 1.1,
    "sodium": 130.0,
    "per_100g": {
      "calories": 489.0,
      "protein": 4.9,
      "carbs": 64.9,
      "fat": 24.9,
      "fiber": 2.4,
      "sodium": 289.0
    }
  }
}

---

Return ONLY the following JSON structure (with "reasoning" as the first key), no markdown formatting outside the JSON, no plain text explanation:

{
  "reasoning": "<your step-by-step reasoning details>",
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
