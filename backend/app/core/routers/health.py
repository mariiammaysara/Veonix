from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["system"])

@router.get("")
async def health_check():
    """
    Check if the API is alive. Used by Render for deployment health checks.
    """
    return {
        "status": "healthy",
        "service": "Veonix Backend",
        "version": "1.0.0"
    }