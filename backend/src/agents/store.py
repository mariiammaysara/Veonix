"""
Module: store
Layer:  Agents (Memory Store)

LangGraph Store integration. Exposes schemas for reading/writing user profiles
and wrapping the meals table as a memory document collection.

Author: Antigravity AI
"""

import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from src.db.database import SessionLocal
from src.models.profile import UserProfile
from src.models.meal import Meal

logger = logging.getLogger(__name__)


class NutritionCoachingStore:
    """
    Manages persistent memory store.
    Provides read/write access to user_profiles and meal history documents.
    """
    def __init__(self, db: Optional[Session] = None):
        self.db = db or SessionLocal()
        self._owned_session = db is None

    def get_profile(self, user_id: str = "default") -> Dict[str, Any]:
        """
        Retrieves the user profile for the given user_id.
        """
        try:
            profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            if not profile:
                return {
                    "user_id": user_id,
                    "dietary_goal": "",
                    "allergies": []
                }
            return {
                "user_id": profile.user_id,
                "dietary_goal": profile.dietary_goal,
                "allergies": profile.allergies or []
            }
        except Exception as e:
            logger.error(f"Failed to fetch profile: {e}")
            return {
                "user_id": user_id,
                "dietary_goal": "",
                "allergies": []
            }
        finally:
            if self._owned_session:
                self.db.close()

    def save_profile(self, user_id: str, goal: str, allergies: List[str]) -> Dict[str, Any]:
        """
        Saves or updates the user profile details.
        """
        try:
            profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            if not profile:
                profile = UserProfile(
                    user_id=user_id,
                    dietary_goal=goal,
                    allergies=allergies
                )
                self.db.add(profile)
            else:
                profile.dietary_goal = goal
                profile.allergies = allergies
                
            self.db.commit()
            return {
                "user_id": user_id,
                "dietary_goal": goal,
                "allergies": allergies
            }
        except Exception as e:
            logger.error(f"Failed to save profile: {e}")
            self.db.rollback()
            raise e
        finally:
            if self._owned_session:
                self.db.close()

    def get_meal_documents(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Wraps the meals table as a memory document collection.
        Returns the last N meal records as documents.
        """
        try:
            meals = self.db.query(Meal).order_by(Meal.created_at.desc()).limit(limit).all()
            docs = []
            for m in meals:
                docs.append({
                    "id": m.id,
                    "food_name": m.food_name,
                    "cuisine": m.cuisine,
                    "meal_type": m.meal_type,
                    "preparation_method": m.preparation_method,
                    "weight_grams": m.weight_grams,
                    "calories": m.calories,
                    "protein": m.protein,
                    "carbs": m.carbs,
                    "fat": m.fat,
                    "ingredients": m.ingredients or [],
                    "created_at": m.created_at.isoformat()
                })
            return docs
        except Exception as e:
            logger.error(f"Failed to fetch meal documents: {e}")
            return []
        finally:
            if self._owned_session:
                self.db.close()
