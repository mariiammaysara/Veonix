from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from app.utils.image_processing import (
    load_image_bytes,
    pil_from_bytes,
    to_jpeg_bytes,
)

from app.services.gemini_client import GeminiClient
from app.services.food_classifier import FoodClassifier
from app.services.nutrition_normalizer import NutritionNormalizer
from app.services.nutrition import NUTRITION_PROMPT
from app.schemas.nutrition import NutritionResponse


router = APIRouter(prefix="/analyze", tags=["Analyze"])


def get_gemini_client() -> GeminiClient:
    return GeminiClient()

def get_food_classifier() -> FoodClassifier:
    return FoodClassifier()


@router.post("/", response_model=NutritionResponse)
async def analyze_image(
    file: UploadFile = File(...),
    gemini: GeminiClient = Depends(get_gemini_client),
    classifier: FoodClassifier = Depends(get_food_classifier),
):

    image_bytes = _safe("INVALID_IMAGE", lambda: load_image_bytes(file))
    pil_image = _safe("DECODE_ERROR", lambda: pil_from_bytes(image_bytes))
    jpeg_bytes = _safe("ENCODING_ERROR", lambda: to_jpeg_bytes(pil_image))

    food_type = _safe("CLASSIFICATION_ERROR",
                      lambda: classifier.detect_type(jpeg_bytes))

    raw_output = _safe(
        "GEMINI_FAILED",
        lambda: gemini.analyze_image_with_prompt(jpeg_bytes, NUTRITION_PROMPT)
    )

    raw_output["type"] = food_type

    normalized = _safe(
        "NORMALIZATION_ERROR",
        lambda: _normalize(raw_output)
    )

    return _safe("SCHEMA_ERROR", lambda: NutritionResponse(**normalized))


def _normalize(output: dict) -> dict:
    food_type = output.get("type", "fresh")

    if "items" in output:
        output["items"] = NutritionNormalizer.normalize_items(
            output["items"], food_type
        )

    return output


def _safe(error_code: str, func):
    try:
        return func()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={"error": error_code, "message": str(e)}
        )
