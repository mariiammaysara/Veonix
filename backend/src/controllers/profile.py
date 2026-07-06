"""
Module: profile
Layer:  Controllers

HTTP endpoints for managing the user profile (dietary goals and allergies).
Provides GET and PUT endpoints for persistent user settings.

Author: Antigravity AI
"""

import logging
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.models.profile import UserProfile

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/profile", tags=["Profile"])


# ── Pydantic Request/Response Schemas ────────────────────────────────────────

class ProfileUpdate(BaseModel):
    dietary_goal: Optional[str] = None
    allergies: Optional[List[str]] = None


class ProfileData(BaseModel):
    user_id: str
    dietary_goal: Optional[str]
    allergies: Optional[List[str]]


class ProfileResponse(BaseModel):
    status: str
    data: ProfileData


# ── Endpoints ───────────────────────────────────────────────────────────────

@router.get("", response_model=ProfileResponse)
def get_profile(db: Session = Depends(get_db)):
    """
    Retrieves the user profile. Creates a default profile if none exists.
    """
    profile = db.query(UserProfile).filter(UserProfile.user_id == "default").first()
    if not profile:
        logger.info("No profile found for 'default' user. Seeding default profile.")
        profile = UserProfile(user_id="default", dietary_goal="", allergies=[])
        db.add(profile)
        db.commit()
        db.refresh(profile)
        
    return {
        "status": "success",
        "data": {
            "user_id": profile.user_id,
            "dietary_goal": profile.dietary_goal,
            "allergies": profile.allergies or []
        }
    }


@router.put("", response_model=ProfileResponse)
def update_profile(payload: ProfileUpdate, db: Session = Depends(get_db)):
    """
    Updates or inserts the user's dietary goals and allergies.
    """
    profile = db.query(UserProfile).filter(UserProfile.user_id == "default").first()
    if not profile:
        logger.info("No profile found to update. Seeding new profile.")
        profile = UserProfile(
            user_id="default", 
            dietary_goal=payload.dietary_goal or "", 
            allergies=payload.allergies or []
        )
        db.add(profile)
    else:
        if payload.dietary_goal is not None:
            profile.dietary_goal = payload.dietary_goal
        if payload.allergies is not None:
            profile.allergies = payload.allergies
            
    db.commit()
    db.refresh(profile)
    
    logger.info(f"User profile updated successfully: goal='{profile.dietary_goal}', allergies={profile.allergies}")
    
    return {
        "status": "success",
        "data": {
            "user_id": profile.user_id,
            "dietary_goal": profile.dietary_goal,
            "allergies": profile.allergies or []
        }
    }
