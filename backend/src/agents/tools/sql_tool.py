"""
Module: sql_tool
Layer:  Agents (Tools)

A safe SQL-querying tool for analyzing user meal history.
Uses Gemini to parse natural language questions into safe aggregates,
which are executed programmatically using SQLAlchemy to avoid raw SQL injection.

Author: Antigravity AI
"""

import json
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy import func
from google import genai
from google.genai import types

from src.config import settings
from src.db.database import SessionLocal
from src.providers.vision.factory import get_gemini_client

logger = logging.getLogger(__name__)

# Strict allow-lists for query parsing validation
ALLOWED_QUERY_TYPES = {"sum", "average", "count", "list"}
ALLOWED_COLUMNS = {"calories", "protein", "carbs", "fat", "fiber", "sodium", "weight_grams", None}
ALLOWED_TIME_RANGES = {"today", "this_week", "this_month", "all_time"}

SYSTEM_PROMPT = """
You are an AI assistant that translates natural language questions about meal history into a structured query.
Analyze the user's question and map it to the following JSON structure:

{
  "query_type": "sum" | "average" | "count" | "list",
  "column": "calories" | "protein" | "carbs" | "fat" | "fiber" | "sodium" | "weight_grams" | null,
  "time_range": "today" | "this_week" | "this_month" | "all_time"
}

Allowed column names:
- "calories"
- "protein"
- "carbs"
- "fat"
- "fiber"
- "sodium"
- "weight_grams"
- Use null if the query type is "count" or "list".

Allowed query types:
- "sum" (total consumption of a metric)
- "average" (average consumption of a metric)
- "count" (number of meals logged)
- "list" (retrieve details of the meals)

Allowed time ranges:
- "today" (today's meals)
- "this_week" (this current week starting Monday)
- "this_month" (this current month)
- "all_time" (entire history, default if not specified)

Return ONLY the raw JSON object. No explanation, no markdown formatting.
"""


def _execute_history_query(query_type: str, column: str, time_range: str) -> str:
    from src.db.database import SessionLocal
    from src.models.meal import Meal
    
    with SessionLocal() as db:
        query = db.query(Meal)
        
        # Apply time range filter
        now = datetime.now(timezone.utc)
        if time_range == "today":
            start_date = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
            query = query.filter(Meal.created_at >= start_date)
        elif time_range == "this_week":
            # Monday is 0, Sunday is 6
            monday = now - timedelta(days=now.weekday())
            start_date = datetime(monday.year, monday.month, monday.day, tzinfo=timezone.utc)
            query = query.filter(Meal.created_at >= start_date)
        elif time_range == "this_month":
            start_date = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
            query = query.filter(Meal.created_at >= start_date)
            
        # Execute query based on type
        db_result_str = ""
        if query_type == "count":
            count = query.count()
            db_result_str = f"Count of meals: {count}"
        elif query_type == "sum":
            attr = getattr(Meal, column)
            val = query.with_entities(func.sum(attr)).scalar() or 0.0
            db_result_str = f"Sum of {column}: {val:.1f}"
        elif query_type == "average":
            attr = getattr(Meal, column)
            val = query.with_entities(func.avg(attr)).scalar() or 0.0
            db_result_str = f"Average of {column}: {val:.1f}"
        elif query_type == "list":
            meals = query.order_by(Meal.created_at.desc()).all()
            if not meals:
                db_result_str = "No meals logged."
            else:
                meal_list = []
                for m in meals:
                    created_local = m.created_at.strftime("%Y-%m-%d %H:%M")
                    meal_list.append(
                        f"- {m.food_name}: {m.calories} kcal, {m.protein}g protein, {m.carbs}g carbs, {m.fat}g fat ({created_local})"
                    )
                db_result_str = "Logged meals:\n" + "\n".join(meal_list)
        return db_result_str


async def query_meal_history(question: str) -> str:
    """
    Translates a natural language question about meal history into a safe, parameterized SQLAlchemy query,
    executes it, and returns a natural language response.
    """
    client = get_gemini_client()
    
    # 1. Ask Gemini to translate the question to structured JSON parameters
    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=[SYSTEM_PROMPT, f"Question: {question}"],
        config=types.GenerateContentConfig(
            temperature=0.0,
            response_mime_type="application/json",
        )
    )
    data = json.loads(response.text)

    # 2. Strict input validation
    query_type = data.get("query_type")
    column = data.get("column")
    time_range = data.get("time_range")
    
    if query_type not in ALLOWED_QUERY_TYPES:
        raise ValueError(f"Disallowed query type: {query_type}")
    if column not in ALLOWED_COLUMNS:
        raise ValueError(f"Disallowed column: {column}")
    if time_range not in ALLOWED_TIME_RANGES:
        raise ValueError(f"Disallowed time range: {time_range}")

    # 3. Build & execute SQLAlchemy query programmatically off-thread
    import asyncio
    db_result_str = await asyncio.to_thread(_execute_history_query, query_type, column, time_range)

    # 4. Use Gemini to format the final friendly answer
    db_summary = f"Query Type: {query_type}, Column: {column}, Time Range: {time_range}, Database Result: {db_result_str}"
    
    FORMAT_PROMPT = f"""
    You are a friendly AI nutrition coach. Answer the user's question about their meal history based on the provided database query results.
    
    User Question: "{question}"
    Database Query Details: {db_summary}
    
    Be concise, helpful, and direct. If there are no meals in the database, suggest logging their first meal.
    """
    
    try:
        format_response = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=[FORMAT_PROMPT],
            config=types.GenerateContentConfig(
                temperature=0.3,
            )
        )
        return format_response.text.strip()
    except Exception as e:
        logger.error(f"Failed to format coach answer via Gemini: {e}")
        return f"Based on your history, the result is: {db_result_str}"
