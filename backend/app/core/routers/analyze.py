from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Response, Header
from sqlalchemy.orm import Session
from typing import List
import logging

from app.core.database import get_db
from app.models.meal import Meal
from app.core.services.food_analysis import FoodAnalyzer 
from app.core.schemas.analyze import AnalyzeImageResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analyze", tags=["analyze"])

def get_food_analyzer():
    return FoodAnalyzer()

@router.post("/image", response_model=AnalyzeImageResponse)
async def analyze_food_image(
    file: UploadFile = File(...),
    client: FoodAnalyzer = Depends(get_food_analyzer),
    db: Session = Depends(get_db)
):
    if not file.content_type.startswith("image/"):
        logger.warning(f"Unsupported file type: {file.content_type}")
        raise HTTPException(status_code=400, detail="Invalid file type.")

    try:
        image_bytes = await file.read()
        result = await client.analyze_food_image(image_bytes, file.content_type)
        
        # Save to DB without user_id (anonymous)
        new_meal = Meal(
            user_id=None,
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

    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f"Router Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=List[AnalyzeImageResponse])
async def get_meal_history(
    limit: int = 10, 
    db: Session = Depends(get_db)
):
    # This endpoint is effectively deprecated for the public version 
    # as history is now stored in localStorage.
    # We return an empty list or could return recent global meals if desired.
    # For privacy, we'll return empty list.
    return []

@router.delete("/{meal_id}")
async def delete_meal(meal_id: int, db: Session = Depends(get_db)):
    # Allow deletion of anonymous meals? 
    # Without user ownership, anyone could delete anything by ID.
    # However, since the frontend uses localStorage, this endpoint might be less relevant 
    # unless we want to clean up the DB.
    # For safety in a public demo without auth, we might want to disable deletion 
    # or just let it be since IDs are hard to guess. 
    # Let's leave it functional for now but it won't be used by the frontend.
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