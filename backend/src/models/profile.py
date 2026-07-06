"""
Module: profile
Layer:  Models

SQLAlchemy ORM model for the 'user_profiles' table.
Defines persistent memory schema for goals, allergies, and profile state.

Author: Antigravity AI
"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON
from src.db.database import Base


class UserProfile(Base):
    """
    Represents the user's persistent nutritional profile.
    Stores dietary goals and food allergies/intolerances as memory.
    """
    __tablename__ = "user_profiles"

    user_id = Column(String, primary_key=True, index=True)
    dietary_goal = Column(String, nullable=True)
    allergies = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
