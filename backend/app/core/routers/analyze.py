from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Response
from sqlalchemy.orm import Session
from typing import List
import logging

from app.core.database import get_db
from app.models.meal import Meal
from app.core.services.gemini_client import GeminiClient 
from app.core.schemas.analyze import AnalyzeImageResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analyze", tags=["analyze"])

def get_gemini_client():
    return GeminiClient()

@router.post("/image", response_model=AnalyzeImageResponse)
async def analyze_food_image(
    file: UploadFile = File(...),
    client: GeminiClient = Depends(get_gemini_client),
    db: Session = Depends(get_db)
):
    if not file.content_type.startswith("image/"):
        logger.warning(f"Unsupported file type: {file.content_type}")
        raise HTTPException(status_code=400, detail="Invalid file type.")

    try:
        image_bytes = await file.read()
        result = await client.analyze_food_image(image_bytes, file.content_type)
        
        new_meal = Meal(
            food_name=result["food_name"],
            calories=result["calories"],
            protein=result["macros"]["protein"],
            carbs=result["macros"]["carbs"],
            fat=result["macros"]["fat"]
        )
        
        db.add(new_meal)
        db.commit()
        db.refresh(new_meal)
        
        return {
            "id": new_meal.id,
            "food_name": new_meal.food_name,
            "calories": new_meal.calories,
            "macros": {
                "protein": new_meal.protein,
                "carbs": new_meal.carbs,
                "fat": new_meal.fat
            }
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Router Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=List[AnalyzeImageResponse])
async def get_meal_history(limit: int = 10, db: Session = Depends(get_db)):
    try:
        meals = db.query(Meal).order_by(Meal.created_at.desc()).limit(limit).all()
        return [
            {
                "id": m.id,
                "food_name": m.food_name,
                "calories": m.calories,
                "macros": {
                    "protein": m.protein, 
                    "carbs": m.carbs, 
                    "fat": m.fat
                }
            } for m in meals
        ]
    except Exception as e:
        logger.error(f"History query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{meal_id}")
async def delete_meal(meal_id: int, db: Session = Depends(get_db)):
    meal_record = db.query(Meal).filter(Meal.id == meal_id).first()
    if not meal_record:
        raise HTTPException(status_code=404, detail="Meal not found")
    
    try:
        db.delete(meal_record)
        db.commit()
        return Response(status_code=204)
    except Exception as e:
        db.rollback()
        logger.error(f"Delete Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete meal")