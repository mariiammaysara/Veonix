"""
Module: repository
Layer:  Infrastructure (DB)

Data Access Object (DAO) for the Meal model.
Centralizes all SQLAlchemy queries to prevent leaking persistence logic into Services.
This follows the Repository Pattern for cleaner unit testing and maintenance.

Author: Mariam Maysara
"""

import logging
from sqlalchemy.orm import Session
from src.models.meal import Meal

logger = logging.getLogger(__name__)


class MealRepository:
    """
    Handles all CRUD operations for the Meal model.

    Responsibilities:
        - Mapping dictionary payloads to SQLAlchemy entities.
        - Executing persistence operations (commit/refresh).
        - Performing aggregated nutrition calculations.

    Dependencies:
        - sqlalchemy.orm.Session
    """

    def __init__(self, db: Session):
        self.db = db

    def save(self, meal_data: dict) -> Meal:
        """
        Persists a new meal analysis result to the database.

        Args:
            meal_data: Dictionary containing validated meal attributes.

        Returns:
            The saved Meal instance with its generated ID.
        """
        meal = Meal(**meal_data)
        self.db.add(meal)
        self.db.commit()
        self.db.refresh(meal)
        logger.info(f"Saved meal id={meal.id} — {meal.food_name}")
        return meal

    def save_all(self, meals_data: list[dict]) -> list[Meal]:
        """
        Persists a batch of new meal analysis results in a single transaction.

        Args:
            meals_data: List of dictionaries containing validated meal attributes.

        Returns:
            List of saved Meal instances.
        """
        meals = [Meal(**data) for data in meals_data]
        self.db.add_all(meals)
        self.db.commit()
        for meal in meals:
            self.db.refresh(meal)
        logger.info(f"Batch saved {len(meals)} meals.")
        return meals

    def get_all(self, limit: int = 50, offset: int = 0) -> list[Meal]:
        """
        Retrieves meal history, newest first.

        Args:
            limit: Maximum number of records to return.
            offset: Number of records to skip.
        """
        return (
            self.db.query(Meal)
            .order_by(Meal.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_by_id(self, meal_id: int) -> Meal | None:
        """
        Retrieves a single meal record for detail views or deletion.
        """
        return self.db.query(Meal).filter(Meal.id == meal_id).first()

    def delete(self, meal_id: int) -> bool:
        """
        Deletes a specific meal record if it exists.

        Args:
            meal_id: Primary key of the target meal.

        Returns:
            True if deleted, False if record not found.
        """
        meal = self.get_by_id(meal_id)
        if not meal:
            return False
        self.db.delete(meal)
        self.db.commit()
        logger.info(f"Deleted meal id={meal_id}")
        return True

    def get_stats(self) -> dict:
        """
        Computes application-wide nutritional statistics.
        Calculated in-memory for SQLite; for larger datasets, migrate to SQL aggregation functions.

        Returns:
            Aggregated averages and counts.
        """
        meals = self.db.query(Meal).all()
        if not meals:
            return {"total_meals": 0, "avg_calories": 0, "avg_protein": 0}

        total = len(meals)
        return {
            "total_meals": total,
            "avg_calories": round(sum(m.calories for m in meals) / total, 1),
            "avg_protein": round(sum(m.protein for m in meals) / total, 1),
            "avg_carbs": round(sum(m.carbs for m in meals) / total, 1),
            "avg_fat": round(sum(m.fat for m in meals) / total, 1),
        }
