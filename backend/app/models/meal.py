from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.core.database import Base

class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=True) # Required for user mapping
    # Added device_id to separate history for each user/device
    device_id = Column(String, index=True, nullable=True) 
    food_name = Column(String)
    calories = Column(Integer)
    protein = Column(Float)
    carbs = Column(Float)
    fat = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow) # Automatic timestamp