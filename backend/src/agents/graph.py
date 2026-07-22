"""
Module: graph
Layer:  Agents

LangGraph-based orchestration graph for food vision analysis, meal history querying, 
and nutrition knowledge search. Declares independent compiled subgraphs for each role.

Author: Antigravity AI
"""

import logging
import contextvars
from typing import TypedDict, Optional, Any, Union
from langgraph.graph import StateGraph, START, END
from google import genai
from google.genai import types

from src.config import settings
from src.providers.vision.base import VisionResult
from src.providers.vision.factory import get_vision_provider, get_gemini_client
from src.helpers.image_processor import compress_image
from src.helpers.prompts import build_vision_prompt, build_coach_prompt
from langfuse import observe, propagate_attributes
from langfuse.langchain import CallbackHandler
from src.enums.graph_errors import build_graph_error

logger = logging.getLogger(__name__)

# Context variable for passing raw image bytes across the execution flow without serializing in graph state
image_bytes_ctx = contextvars.ContextVar("image_bytes_ctx", default=None)


class AnalysisState(TypedDict):
    """
    State schema for the supervisor orchestration and subgraphs.
    """
    image_bytes: Optional[Union[bytes, dict]]
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
    Uses GEMINI_MODEL (strong multimodal) with a goal-aware prompt.
    """
    logger.info(f"vision_node using model={settings.GEMINI_MODEL}")
    try:
        raw_bytes = image_bytes_ctx.get()
        if not raw_bytes:
            state_bytes = state.get("image_bytes")
            if isinstance(state_bytes, bytes):
                raw_bytes = state_bytes
            else:
                raise ValueError("No image bytes provided in context or state for vision_node.")
            
        original_size = len(raw_bytes)
        # Preprocess/compress the image to optimize payload size
        compressed = compress_image(raw_bytes)
        compressed_size = len(compressed)
        ratio = round(compressed_size / original_size, 2) if original_size else None
        
        # Load profile for goal-aware prompt building and allergy checks
        from src.agents.store import NutritionCoachingStore
        import asyncio
        store = NutritionCoachingStore()
        profile = await asyncio.to_thread(store.get_profile)
        dietary_goal = profile.get("dietary_goal")
        
        # Build a goal-aware prompt - falls back to base GEMINI_PROMPT if no goal set
        prompt = build_vision_prompt(dietary_goal)
        if dietary_goal:
            logger.info(f"vision_node using goal-framed prompt for dietary_goal='{dietary_goal}'")
        
        provider = get_vision_provider()
        result = await provider.analyze(compressed, prompt=prompt)
        
        with propagate_attributes(
            metadata={
                "model": settings.GEMINI_MODEL,
                "confidence": str(result.confidence) if result else None,
                "image_size_bytes": str(original_size),
                "compressed_size_bytes": str(compressed_size),
                "compression_ratio": str(ratio) if ratio is not None else None,
            }
        ):
            logger.info(f"Gemini: {result.food_name} ({result.confidence:.0%}) - {result.calories} kcal")
            
            # Verify user allergies against ingredients
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
            "error": build_graph_error(e, provider="gemini")
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
    Uses GEMINI_MODEL_FAST — text-only SQL aggregation needs no vision capability.
    """
    logger.info(f"history_node using model={settings.GEMINI_MODEL_FAST}")
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
        # Classify provider dynamically: if it's API related, attribute it to gemini
        provider = "sqlite"
        err_str = str(e).lower()
        if "gemini" in err_str or "google" in err_str:
            provider = "gemini"
        return {
            "history_answer": None,
            "error": build_graph_error(e, provider=provider)
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
    Uses GEMINI_MODEL_FAST — formatting a text response needs no vision capability.
    """
    logger.info(f"knowledge_node using model={settings.GEMINI_MODEL_FAST}")
    try:
        question = state.get("question")
        if not question:
            raise ValueError("No question provided for knowledge_node.")
            
        client = get_gemini_client()
        
        # Load user profile and meal history memory from store
        from src.agents.store import NutritionCoachingStore
        import asyncio
        store = NutritionCoachingStore()
        profile = await asyncio.to_thread(store.get_profile)
        recent_meals = await asyncio.to_thread(store.get_meal_documents, limit=5)
        dietary_goal = profile.get("dietary_goal")
        
        profile_context = f"Dietary Goal: {dietary_goal or 'None'}\nAllergies: {', '.join(profile.get('allergies') or []) or 'None'}"
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
        
        # Build a goal-aware coaching prompt using the profile's dietary goal
        if dietary_goal:
            logger.info(f"knowledge_node using goal-adjusted coaching prompt for dietary_goal='{dietary_goal}'")
        format_prompt = build_coach_prompt(
            question=question,
            dietary_goal=dietary_goal,
            profile_context=profile_context,
            meals_context=meals_context,
            db_summary=db_summary,
        )
        
        # Use GEMINI_MODEL_FAST — text-only formatting is well within its capability
        format_resp = await client.aio.models.generate_content(
            model=settings.GEMINI_MODEL_FAST,
            contents=[format_prompt],
            config=types.GenerateContentConfig(temperature=0.3)
        )
        answer = format_resp.text.strip()
        
        return {
            "history_answer": answer,
            "error": None
        }
    except Exception as e:
        logger.error(f"Error in knowledge_node: {str(e)}")
        provider = "tavily"
        err_str = str(e).lower()
        if "gemini" in err_str or "google" in err_str or "embed" in err_str or "rag" in err_str:
            provider = "gemini"
        return {
            "history_answer": None,
            "error": build_graph_error(e, provider=provider)
        }


# Build and compile Knowledge Subgraph
knowledge_workflow = StateGraph(AnalysisState)
knowledge_workflow.add_node("knowledge_node", knowledge_node)
knowledge_workflow.add_edge(START, "knowledge_node")
knowledge_workflow.add_edge("knowledge_node", END)
knowledge_graph = knowledge_workflow.compile()


@observe(name="veonix-analysis-workflow")
async def run_analysis_graph(
    image_bytes: Optional[bytes] = None,
    question: Optional[str] = None,
    thread_id: Optional[str] = None,
    config: Optional[dict] = None,
    request_id: Optional[str] = None,
    vision_result: Optional[VisionResult] = None,
    allergies_warning: Optional[str] = None,
) -> AnalysisState:
    """
    Runs the main supervisor orchestrator graph.
    Matches the original API contract so controllers remain unchanged.

    Injects AgentTraceCallback as a LangGraph callback so every node start/end
    and tool start/end is emitted as a structured JSON log line, mirroring the
    HTTP-level RequestLoggerMiddleware/TimingMiddleware pattern at agent scope.

    Performance path: if vision_result is already computed (from the streaming
    endpoint), it is injected directly into the state so the supervisor skips
    vision_node and routes straight to persist_node, avoiding the redundant
    second Gemini call.
    """
    # Lazy import prevents compile-time circular dependencies
    from src.agents.supervisor import main_graph
    from src.middleware.agent_trace import AgentTraceCallback

    image_summary = None
    if image_bytes:
        image_summary = {
            "image_present": True,
            "image_size_bytes": len(image_bytes),
            "mime_type": "image/jpeg"
        }

    initial_state = {
        "image_bytes": image_summary,
        "vision_result": vision_result,
        "question": question,
        "history_answer": None,
        "error": None,
        "retry_count": 0,
        "retake_prompt": None,
        "allergies_warning": allergies_warning,
    }

    if not config:
        if thread_id:
            config = {"configurable": {"thread_id": thread_id}}
        else:
            config = {"configurable": {"thread_id": "default-test-thread"}}

    # Dynamic trace attributes
    is_vision = bool(image_bytes or vision_result)
    trace_name = "vision-analysis" if is_vision else "coach-question"
    tags = ["vision", "meal", "gemini"] if is_vision else ["coach", "rag", "nutrition"]
    
    metadata = {
        "model": settings.GEMINI_MODEL,
    }
    if vision_result:
        metadata["confidence"] = str(vision_result.confidence)

    token = None
    if image_bytes:
        token = image_bytes_ctx.set(image_bytes)

    try:
        # Wrap execution to propagate attributes to the Langfuse CallbackHandler and traces
        with propagate_attributes(
            trace_name=trace_name,
            session_id=thread_id or "default-thread",
            tags=tags,
            metadata=metadata
        ):
            langfuse_handler = CallbackHandler()
            
            # Inject agent-level trace callback - one instance per invocation
            trace_cb = AgentTraceCallback(request_id=request_id)
            config = {**config, "callbacks": [trace_cb, langfuse_handler]}

            result_state = await main_graph.ainvoke(initial_state, config=config)
            return result_state
    finally:
        if token is not None:
            image_bytes_ctx.reset(token)


