"""
Module: supervisor
Layer:  Agents

The main supervisor orchestrator node. Classifies incoming requests (based on presence
of image, keywords, and LLM intent) to route queries to Vision, History, or Knowledge subgraphs.

Author: Antigravity AI
"""

import logging
from typing import Optional
from google import genai
from google.genai import types
from langgraph.graph import StateGraph, START, END

from src.config import settings
from src.agents.graph import (
    AnalysisState,
    vision_graph,
    history_graph,
    knowledge_graph
)

logger = logging.getLogger(__name__)


async def route_request(image_bytes: Optional[bytes], question: Optional[str]) -> str:
    """
    Inspects request properties and routes execution:
    - If image_bytes is present: routes to vision_node.
    - If question is present: uses rule-based keywords and Gemini classification
      to route to history_node (personal SQL data) or knowledge_node (general RAG/Tavily search).
    """
    if image_bytes is not None:
        logger.info("Image bytes present. Supervisor routing to vision_node.")
        return "vision_node"
        
    if not question:
        logger.info("Empty request input. Supervisor routing to END.")
        return "END"
        
    question_lower = question.lower()
    
    # Fast check: queries explicitly requesting search engines or general news
    if any(kw in question_lower for kw in ["search", "latest", "tavily", "web", "current"]):
        logger.info(f"Keyword search match found in '{question}'. Supervisor routing to knowledge_node.")
        return "knowledge_node"
        
    # Classify with LLM for ambiguity resolution
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    CLASSIFY_PROMPT = f"""
    You are an AI supervisor routing queries to the correct expert.
    Analyze the user question and classify it:
    - "history_node": For questions about the user's personal logged meal history, personal calorie/protein consumption history, or personal food logs. (e.g., "what did I eat today?", "how many calories this week?")
    - "knowledge_node": For general nutrition questions, recipes, food ingredient details, or general information. (e.g., "how much protein in an egg?", "benefits of avocado")
    
    User Question: "{question}"
    
    Respond ONLY with "history_node" or "knowledge_node". No other text.
    """
    
    try:
        classify_resp = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=[CLASSIFY_PROMPT],
            config=types.GenerateContentConfig(temperature=0.0)
        )
        category = classify_resp.text.strip().lower()
        logger.info(f"Supervisor LLM classified query '{question}' as: {category}")
        
        if "history_node" in category:
            return "history_node"
        else:
            return "knowledge_node"
    except Exception as e:
        logger.error(f"Supervisor classification failed, defaulting to knowledge_node: {e}")
        return "knowledge_node"


# ── Subgraph Wrappers ────────────────────────────────────────────────────────

async def run_vision(state: AnalysisState) -> dict:
    """Wrapper node executing the compiled vision subgraph."""
    logger.info("Supervisor invoking Vision Subgraph...")
    return await vision_graph.ainvoke(state)


async def run_history(state: AnalysisState) -> dict:
    """Wrapper node executing the compiled history subgraph."""
    logger.info("Supervisor invoking History Subgraph...")
    return await history_graph.ainvoke(state)


async def run_knowledge(state: AnalysisState) -> dict:
    """Wrapper node executing the compiled knowledge subgraph."""
    logger.info("Supervisor invoking Knowledge Subgraph...")
    return await knowledge_graph.ainvoke(state)


# ── Supervisor Graph Definition ──────────────────────────────────────────────

async def route_supervisor(state: AnalysisState) -> str:
    """Conditional edge router executing state classification."""
    return await route_request(state.get("image_bytes"), state.get("question"))


async def run_persist(state: AnalysisState) -> dict:
    """
    Persist the approved/analyzed meal to the database.
    Called after user confirmation.
    """
    logger.info("Persist node invoked. Saving meal to database...")
    result = state.get("vision_result")
    if not result:
        logger.warning("No vision_result found in state to persist.")
        return {}
        
    # Import inside the node to avoid circular import issues
    from src.db.repository import MealRepository
    from src.db.database import SessionLocal
    
    db = SessionLocal()
    try:
        MealRepository(db).save({
            "food_name":          result.food_name,
            "cuisine":            result.cuisine,
            "meal_type":          result.meal_type,
            "preparation_method": result.preparation_method,
            "weight_grams":       result.estimated_weight_grams,
            "confidence":         result.confidence,
            "calories":           result.calories,
            "protein":            result.protein,
            "carbs":              result.carbs,
            "fat":                result.fat,
            "fiber":              result.fiber,
            "sodium":             result.sodium,
            "ingredients":        result.ingredients,
            "per_100g":           result.per_100g,
            "nutrition_source":   "Gemini",
            "is_estimated":       0,
        })
        logger.info("Meal saved successfully in persist_node.")
    except Exception as e:
        logger.error(f"Failed to save meal in persist_node: {e}")
        return {"error": e}
    finally:
        db.close()
        
    return {}


workflow = StateGraph(AnalysisState)
workflow.add_node("vision_node", run_vision)
workflow.add_node("history_node", run_history)
workflow.add_node("knowledge_node", run_knowledge)
workflow.add_node("persist_node", run_persist)

workflow.add_conditional_edges(
    START,
    route_supervisor,
    {
        "vision_node": "vision_node",
        "history_node": "history_node",
        "knowledge_node": "knowledge_node",
        "END": END
    }
)

workflow.add_edge("vision_node", "persist_node")
workflow.add_edge("persist_node", END)
workflow.add_edge("history_node", END)
workflow.add_edge("knowledge_node", END)

# In-memory checkpointer for LangGraph state persistence & time-travel
from langgraph.checkpoint.memory import MemorySaver
memory_saver = MemorySaver()

main_graph = workflow.compile(
    checkpointer=memory_saver,
    interrupt_before=["persist_node"]
)
