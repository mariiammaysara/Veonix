from fastapi import APIRouter, Depends
from app.core.config import settings
from app.services.gemini_client import GeminiClient

router = APIRouter(prefix="/status", tags=["Status"])

def get_gemini() -> GeminiClient:
    return GeminiClient()

@router.get("/")
def get_status():
    return {
        "status": "running",
        "model": settings.GEMINI_MODEL,
        "environment": settings.ENV
    }

@router.get("/models")
def list_available_models(gemini: GeminiClient = Depends(get_gemini)):
    return {
        "current_model": settings.GEMINI_MODEL,
        "available_models": gemini.list_models()
    }
