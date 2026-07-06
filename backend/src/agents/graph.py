"""
Module: graph
Layer:  Agents

LangGraph-based orchestration graph for food vision analysis, meal history querying, 
and nutrition knowledge search. Declares independent compiled subgraphs for each role.

Author: Antigravity AI
"""

import logging
from typing import TypedDict, Optional, Any
from langgraph.graph import StateGraph, START, END
from google import genai
from google.genai import types

from src.config import settings
from src.providers.vision.base import VisionResult
from src.providers.vision.factory import get_vision_provider
from src.helpers.image_processor import compress_image

logger = logging.getLogger(__name__)


class AnalysisState(TypedDict):
    """
    State schema for the supervisor orchestration and subgraphs.
    """
    image_bytes: Optional[bytes]
    vision_result: Optional[VisionResult]
    question: Optional[str]
    history_answer: Optional[str]
    error: Optional[Any]
    retry_count: int
    retake_prompt: Optional[str]
    allergies_warning: Optional[str]


# ── Vision Subgraph Nodes & Edges ───────────────────────────────────────────

async def vision_node(state: AnalysisState) -> dict:
    """
    A graph node that runs the Gemini provider image analysis.
    """
    try:
        if not state.get("image_bytes"):
            raise ValueError("No image bytes provided for vision_node.")
            
        # Preprocess/compress the image to optimize payload size
        compressed = compress_image(state["image_bytes"])
        
        provider = get_vision_provider()
        result = await provider.analyze(compressed)
        
        logger.info(f"Gemini: {result.food_name} ({result.confidence:.0%}) — {result.calories} kcal")
        
        # Load profile from store and verify user allergies
        from src.agents.store import NutritionCoachingStore
        store = NutritionCoachingStore()
        profile = store.get_profile()
        
        allergies = [a.strip().lower() for a in profile.get("allergies", []) if a.strip()]
        food_lower = result.food_name.lower()
        ingredients = [i.lower() for i in (result.ingredients or [])]
        
        matched_allergies = []
        for allergy in allergies:
            if allergy in food_lower:
                matched_allergies.append(allergy)
            else:
                for ing in ingredients:
                    if allergy in ing:
                        matched_allergies.append(allergy)
                        break
                        
        warning = None
        if matched_allergies:
            warning = f"Warning: This meal may contain ingredients you are allergic to: {', '.join(matched_allergies)}."
            logger.warning(f"Allergy warning triggered: {warning}")
        
        return {
            "vision_result": result,
            "allergies_warning": warning,
            "error": None
        }
    except Exception as e:
        logger.error(f"Error in vision_node: {str(e)}")
        return {
            "vision_result": None,
            "allergies_warning": None,
            "error": e
        }


async def request_better_photo_node(state: AnalysisState) -> dict:
    """
    Node that is invoked when vision analysis returns low confidence.
    Increments retry count and sets the retake photo message.
    """
    current_retries = state.get("retry_count", 0)
    logger.info(f"Low confidence detected. Incrementing retry loop count from {current_retries}.")
    return {
        "retry_count": current_retries + 1,
        "retake_prompt": "Low confidence in photo analysis. Please retake the photo in better lighting."
    }


def check_vision_confidence(state: AnalysisState) -> str:
    """
    Conditional edge router checking confidence of vision result.
    Capped at 2 retries total.
    """
    result = state.get("vision_result")
    retry = state.get("retry_count", 0)
    
    if not result:
        return END
        
    if result.confidence >= 0.6:
        logger.info(f"High confidence image result received ({result.confidence:.0%}). Routing to END.")
        return END
        
    if retry < 2:
        logger.warning(f"Low confidence ({result.confidence:.0%}) and retry limit not reached ({retry}/2). Routing to retake prompt.")
        return "request_better_photo_node"
        
    logger.error(f"Low confidence ({result.confidence:.0%}) and retry limit reached ({retry}/2). Routing to END.")
    return END


# Build and compile Vision Subgraph
vision_workflow = StateGraph(AnalysisState)
vision_workflow.add_node("vision_node", vision_node)
vision_workflow.add_node("request_better_photo_node", request_better_photo_node)
vision_workflow.add_edge(START, "vision_node")
vision_workflow.add_conditional_edges(
    "vision_node",
    check_vision_confidence,
    {
        "request_better_photo_node": "request_better_photo_node",
        END: END
    }
)
vision_workflow.add_edge("request_better_photo_node", "vision_node")
vision_graph = vision_workflow.compile()


# ── History Subgraph Nodes & Edges ──────────────────────────────────────────

async def history_node(state: AnalysisState) -> dict:
    """
    A graph node that queries user meal history using safe database tool.
    """
    try:
        question = state.get("question")
        if not question:
            raise ValueError("No question provided for history_node.")
            
        from src.agents.tools.sql_tool import query_meal_history
        answer = await query_meal_history(question)
        
        return {
            "history_answer": answer,
            "error": None
        }
    except Exception as e:
        logger.error(f"Error in history_node: {str(e)}")
        return {
            "history_answer": None,
            "error": e
        }


# Build and compile History Subgraph
history_workflow = StateGraph(AnalysisState)
history_workflow.add_node("history_node", history_node)
history_workflow.add_edge(START, "history_node")
history_workflow.add_edge("history_node", END)
history_graph = history_workflow.compile()


# ── Knowledge Subgraph Nodes & Edges ────────────────────────────────────────

async def knowledge_node(state: AnalysisState) -> dict:
    """
    A graph node that retrieves nutrition references from RAG local knowledge
    or falls back to Tavily search, then formats with Gemini.
    """
    try:
        question = state.get("question")
        if not question:
            raise ValueError("No question provided for knowledge_node.")
            
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        # Load user profile and meal history memory from store
        from src.agents.store import NutritionCoachingStore
        store = NutritionCoachingStore()
        profile = store.get_profile()
        recent_meals = store.get_meal_documents(limit=5)
        
        profile_context = f"Dietary Goal: {profile.get('dietary_goal') or 'None'}\nAllergies: {', '.join(profile.get('allergies') or []) or 'None'}"
        meals_context = "\n".join([
            f"- {m['food_name']} ({m['calories']} kcal, P: {m['protein']}g, C: {m['carbs']}g, F: {m['fat']}g) logged at {m['created_at']}"
            for m in recent_meals
        ]) or "No recent meals logged."
        
        from src.agents.tools.rag_tool import search_nutrition_knowledge
        rag_result = await search_nutrition_knowledge(question)
        
        if rag_result:
            db_summary = f"Source: Local Knowledge Base Reference Document, Content: {rag_result}"
            logger.info("RAG Match: Found relevant local nutrition document.")
        else:
            from src.agents.tools.tavily_tool import search_tavily
            logger.info("RAG Miss: Local context unavailable. Routing web search fallback via Tavily.")
            web_result = await search_tavily(question)
            db_summary = f"Source: Web Search Result, Content: {web_result}"
            
        # Format the response in a coaching tone using Gemini
        FORMAT_PROMPT = f"""
        You are a friendly AI nutrition coach. Answer the user's question about nutrition/health using the provided information source.
        
        User Profile:
        {profile_context}
        
        Recent Meals Memory:
        {meals_context}
        
        User Question: "{question}"
        Information Source Details: {db_summary}
        
        Be concise, helpful, and direct. Translate the source information into a friendly response.
        Ensure you take the user's goal and allergies into consideration. If the information source contradicts their allergies, provide warning feedback.
        """
        
        format_resp = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=[FORMAT_PROMPT],
            config=types.GenerateContentConfig(temperature=0.3)
        )
        answer = format_resp.text.strip()
        
        return {
            "history_answer": answer,
            "error": None
        }
    except Exception as e:
        logger.error(f"Error in knowledge_node: {str(e)}")
        return {
            "history_answer": None,
            "error": e
        }


# Build and compile Knowledge Subgraph
knowledge_workflow = StateGraph(AnalysisState)
knowledge_workflow.add_node("knowledge_node", knowledge_node)
knowledge_workflow.add_edge(START, "knowledge_node")
knowledge_workflow.add_edge("knowledge_node", END)
knowledge_graph = knowledge_workflow.compile()


# ── Execution Delegation ────────────────────────────────────────────────────

async def run_analysis_graph(
    image_bytes: Optional[bytes] = None,
    question: Optional[str] = None
) -> AnalysisState:
    """
    Runs the main supervisor orchestrator graph.
    Matches the original API contract so controllers remain unchanged.
    """
    # Lazy import prevents compile-time circular dependencies
    from src.agents.supervisor import main_graph
    
    initial_state = {
        "image_bytes": image_bytes,
        "vision_result": None,
        "question": question,
        "history_answer": None,
        "error": None,
        "retry_count": 0,
        "retake_prompt": None
    }
    
    result_state = await main_graph.ainvoke(initial_state)
    return result_state
