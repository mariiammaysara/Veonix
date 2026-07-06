"""
MCP Server for Veonix.
Exposes meal history retrieval and nutrition stats as an MCP interface.

Author: Antigravity AI
"""

from mcp.server.fastmcp import FastMCP
from src.db.database import SessionLocal
from src.db.repository import MealRepository
import json

# Initialize FastMCP server
mcp = FastMCP("Veonix")


@mcp.tool()
def get_meal_history(limit: int = 50, offset: int = 0) -> str:
    """
    Retrieve logged user meals sorted by creation date (newest first).
    Use this to inspect food names, calories, protein, carbs, and fat logs.
    """
    db = SessionLocal()
    try:
        repo = MealRepository(db)
        meals = repo.get_all(limit=limit, offset=offset)
        result = []
        for m in meals:
            result.append({
                "id": m.id,
                "food_name": m.food_name,
                "meal_type": m.meal_type,
                "calories": m.calories,
                "protein": m.protein,
                "carbs": m.carbs,
                "fat": m.fat,
                "created_at": m.created_at.isoformat() if m.created_at else None
            })
        return json.dumps(result, indent=2)
    finally:
        db.close()


@mcp.resource("nutrition://stats")
def get_nutrition_stats() -> str:
    """
    Exposes user's current nutrition stats as a resource.
    Provides aggregated daily averages for calories, protein, carbs, and fat.
    """
    db = SessionLocal()
    try:
        repo = MealRepository(db)
        stats = repo.get_stats()
        return json.dumps(stats, indent=2)
    finally:
        db.close()


if __name__ == "__main__":
    mcp.run()
