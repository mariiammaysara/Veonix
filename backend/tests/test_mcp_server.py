"""
Integration tests for the Veonix MCP Server.
Tests standard MCP client/server stdio communication, listing/calling tools,
and reading resources.
"""

import os
import sys
import json
import pytest
from mcp import stdio_client, StdioServerParameters, ClientSession
from src.config import settings
from src.db.database import SessionLocal
from src.models.meal import Meal
from src.db.repository import MealRepository


@pytest.mark.asyncio
async def test_mcp_server_client_roundtrip():
    """
    Spawns the MCP server as a subprocess, initializes an MCP ClientSession,
    and asserts that the 'get_meal_history' tool and 'nutrition://stats' resource
    return the expected database outputs.
    """
    # 1. Setup mock meals in the test database
    db = SessionLocal()
    try:
        # Clear existing test meals
        db.query(Meal).filter(Meal.food_name.like("MCP Test Meal%")).delete()
        db.commit()

        repo = MealRepository(db)
        repo.save({
            "food_name": "MCP Test Meal Chicken",
            "cuisine": "American",
            "meal_type": "lunch",
            "preparation_method": "grilled",
            "weight_grams": 200,
            "confidence": 0.95,
            "calories": 400.0,
            "protein": 50.0,
            "carbs": 10.0,
            "fat": 8.0,
            "fiber": 2.0,
            "sodium": 300.0,
            "ingredients": ["chicken", "oil"],
            "per_100g": {},
            "nutrition_source": "Gemini",
            "is_estimated": 0,
        })
        repo.save({
            "food_name": "MCP Test Meal Salad",
            "cuisine": "French",
            "meal_type": "lunch",
            "preparation_method": "raw",
            "weight_grams": 150,
            "confidence": 0.90,
            "calories": 100.0,
            "protein": 2.0,
            "carbs": 15.0,
            "fat": 5.0,
            "fiber": 5.0,
            "sodium": 100.0,
            "ingredients": ["lettuce", "dressing"],
            "per_100g": {},
            "nutrition_source": "Gemini",
            "is_estimated": 0,
        })
        db.commit()

        # 2. Configure MCP stdio server parameters
        # Use sys.executable to run inside the exact same pytest virtual env
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["mcp_server/server.py"],
            env={
                "PYTHONPATH": ".",
                "DATABASE_URL": settings.DATABASE_URL,
                **{k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
            }
        )

        # 3. Connect to the MCP server
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # A. Verify listed tools
                tools_list = await session.list_tools()
                tool_names = [t.name for t in tools_list.tools]
                assert "get_meal_history" in tool_names

                # B. Call the 'get_meal_history' tool
                result = await session.call_tool(
                    "get_meal_history",
                    arguments={"limit": 5, "offset": 0}
                )
                
                # Check results contain our mock meals
                assert len(result.content) == 1
                history_json = json.loads(result.content[0].text)
                
                # Filter to only the test meals
                test_meals = [m for m in history_json if "MCP Test Meal" in m["food_name"]]
                assert len(test_meals) == 2
                
                # Sorted newest first (newest is Salad since saved second)
                assert test_meals[0]["food_name"] == "MCP Test Meal Salad"
                assert test_meals[1]["food_name"] == "MCP Test Meal Chicken"
                assert test_meals[0]["calories"] == 100.0
                assert test_meals[1]["protein"] == 50.0

                # C. Read the 'nutrition://stats' resource
                stats_res = await session.read_resource("nutrition://stats")
                stats_data = json.loads(stats_res.contents[0].text)
                assert "total_meals" in stats_data
                assert stats_data["total_meals"] >= 2

    finally:
        # DB Cleanup
        db.query(Meal).filter(Meal.food_name.like("MCP Test Meal%")).delete()
        db.commit()
        db.close()
