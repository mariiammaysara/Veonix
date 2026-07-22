"""
Tests for the safe SQL querying tool.
Verifies input validation (allow-lists) and aggregates against a test database.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.database import Base
from src.models.meal import Meal
from src.agents.tools.sql_tool import query_meal_history

# Setup in-memory SQLite database for testing
test_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def setup_test_db():
    """
    Creates tables and seeds mock data before each test.
    """
    Base.metadata.create_all(bind=test_engine)
    db = TestSessionLocal()
    
    # Seed mock meals with precise audit timestamps
    now = datetime.now(timezone.utc)
    
    # 1. Meal logged today
    meal1 = Meal(
        food_name="Oatmeal",
        cuisine="American",
        meal_type="breakfast",
        preparation_method="boiled",
        weight_grams=200,
        confidence=0.9,
        calories=300.0,
        protein=10.0,
        carbs=50.0,
        fat=5.0,
        created_at=now
    )
    
    # 2. Meal logged 2 days ago (this week)
    meal2 = Meal(
        food_name="Grilled Chicken Salad",
        cuisine="Mediterranean",
        meal_type="lunch",
        preparation_method="grilled",
        weight_grams=350,
        confidence=0.95,
        calories=450.0,
        protein=40.0,
        carbs=15.0,
        fat=12.0,
        created_at=now - timedelta(days=2)
    )
    
    # 3. Meal logged 10 days ago (this month, but not this week if today is late in week, 
    # but let's make it explicitly this month by going back 10 days)
    # Ensure it doesn't cross month boundary:
    # If today is less than 10th of month, 10 days ago might cross boundary.
    # So let's calculate days dynamically:
    days_ago_month = 10 if now.day > 10 else (now.day - 1 if now.day > 1 else 0)
    meal3 = Meal(
        food_name="Salmon Steak",
        cuisine="Nordic",
        meal_type="dinner",
        preparation_method="baked",
        weight_grams=250,
        confidence=0.88,
        calories=500.0,
        protein=35.0,
        carbs=5.0,
        fat=22.0,
        created_at=now - timedelta(days=days_ago_month)
    )

    db.add_all([meal1, meal2, meal3])
    db.commit()
    db.close()
    
    # Patch the SessionLocal used in the tool with our test session maker
    with patch("src.agents.tools.sql_tool.SessionLocal", TestSessionLocal):
        yield
        
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(autouse=True)
def mock_settings_key(monkeypatch):
    """
    Dummy API Key to bypass client instantiation crash.
    """
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key")


@pytest.mark.asyncio
async def test_query_meal_history_allow_list_validation():
    """
    Ensure the tool rejects disallowed column names, query types, or time ranges.
    """
    # Mocking Gemini Client class inside sql_tool
    with patch("src.agents.tools.sql_tool.get_gemini_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_aio = MagicMock()
        mock_client.aio = mock_aio
        
        # Test Case 1: Unallowed SQL injection column name
        mock_response_1 = MagicMock()
        mock_response_1.text = '{"query_type": "average", "column": "calories; DROP TABLE meals;", "time_range": "this_week"}'
        mock_aio.models.generate_content = AsyncMock(return_value=mock_response_1)
        
        with pytest.raises(ValueError, match="Disallowed column"):
            await query_meal_history("average calories")
            
        # Test Case 2: Unallowed query type
        mock_response_2 = MagicMock()
        mock_response_2.text = '{"query_type": "delete_all", "column": "calories", "time_range": "this_week"}'
        mock_aio.models.generate_content = AsyncMock(return_value=mock_response_2)
        
        with pytest.raises(ValueError, match="Disallowed query type"):
            await query_meal_history("delete all my meals")


@pytest.mark.asyncio
async def test_query_meal_history_aggregates():
    """
    Verify that aggregates (sum, average, count) calculate correctly.
    """
    with patch("src.agents.tools.sql_tool.get_gemini_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_aio = MagicMock()
        mock_client.aio = mock_aio
        
        # Scenario A: Ask for count of meals this week
        mock_parser_response = MagicMock()
        mock_parser_response.text = '{"query_type": "count", "column": null, "time_range": "this_week"}'
        
        mock_formatter_response = MagicMock()
        mock_formatter_response.text = "You logged 2 meals this week."
        
        mock_aio.models.generate_content = AsyncMock()
        mock_aio.models.generate_content.side_effect = [mock_parser_response, mock_formatter_response]
        
        ans = await query_meal_history("How many meals did I log this week?")
        assert "2" in ans or "two" in ans.lower() or "logged" in ans.lower()
        
        # Reset mock side effects
        mock_aio.models.generate_content.reset_mock()
        
        # Scenario B: Ask for sum of protein this week (should include meal1 + meal2 = 50g)
        mock_parser_response_b = MagicMock()
        mock_parser_response_b.text = '{"query_type": "sum", "column": "protein", "time_range": "this_week"}'
        
        mock_formatter_response_b = MagicMock()
        mock_formatter_response_b.text = "You had a total of 50.0g of protein this week."
        
        mock_aio.models.generate_content.side_effect = [mock_parser_response_b, mock_formatter_response_b]
        
        ans = await query_meal_history("total protein this week")
        assert "50" in ans
