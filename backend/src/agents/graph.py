"""
Module: graph
Layer:  Agents

LangGraph-based orchestration graph for food vision analysis and meal history querying.
Handles routing requests to either vision processing or safe database aggregates.

Author: Antigravity AI
"""

import logging
from typing import TypedDict, Optional, Any
from langgraph.graph import StateGraph, START, END

from src.providers.vision.base import VisionResult
from src.providers.vision.factory import get_vision_provider
from src.helpers.image_processor import compress_image

logger = logging.getLogger(__name__)


class AnalysisState(TypedDict):
    """
    State schema for the food image analysis and history querying workflow.
    """
    image_bytes: Optional[bytes]
    vision_result: Optional[VisionResult]
    question: Optional[str]
    history_answer: Optional[str]
    error: Optional[Any]


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
        
        return {
            "vision_result": result,
            "error": None
        }
    except Exception as e:
        logger.error(f"Error in vision_node: {str(e)}")
        return {
            "vision_result": None,
            "error": e
        }


async def history_node(state: AnalysisState) -> dict:
    """
    A graph node that queries user meal history using safe database tool,
    or falls back to local RAG knowledge / Tavily web search for general nutrition questions.
    """
    try:
        question = state.get("question")
        if not question:
            raise ValueError("No question provided for history_node.")
            
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        # 1. Classify the user question into history vs knowledge
        CLASSIFY_PROMPT = f"""
        You are an AI assistant routing user queries to the correct tool.
        Analyze the user's question and classify it into one of these categories:
        - "history": If the user is asking about their logged meals, meal stats, history, calories consumed, protein consumed, etc. (e.g., "what did I eat today?", "how many calories did I eat this week?")
        - "knowledge": If the user is asking a general nutrition or health question not related to their personal logged history (e.g., "how much protein is in an egg?", "what are the benefits of hydration?", "how to calculate calorie deficit?")

        User Question: "{question}"

        Return ONLY "history" or "knowledge". No other text.
        """
        
        classify_resp = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=[CLASSIFY_PROMPT],
            config=types.GenerateContentConfig(temperature=0.0)
        )
        category = classify_resp.text.strip().lower()
        logger.info(f"Classified query '{question}' as category: {category}")
        
        if "history" in category:
            # Personal history query path
            from src.agents.tools.sql_tool import query_meal_history
            answer = await query_meal_history(question)
        else:
            # Nutrition knowledge path (RAG with Tavily Web Search fallback)
            from src.agents.tools.rag_tool import search_nutrition_knowledge
            rag_result = await search_nutrition_knowledge(question)
            
            if rag_result:
                db_summary = f"Source: Local Knowledge Base Reference Document, Content: {rag_result}"
                logger.info("Found relevant local RAG context.")
            else:
                from src.agents.tools.tavily_tool import search_tavily
                logger.info("Local RAG context missing or below threshold. Falling back to Tavily.")
                web_result = await search_tavily(question)
                db_summary = f"Source: Web Search Result, Content: {web_result}"
                
            # Use Gemini to construct a friendly, conversational coach response based on context
            FORMAT_PROMPT = f"""
            You are a friendly AI nutrition coach. Answer the user's question about nutrition/health using the provided information source.
            
            User Question: "{question}"
            Information Source Details: {db_summary}
            
            Be concise, helpful, and direct. Translate the source information into a friendly response.
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
        logger.error(f"Error in history_node: {str(e)}")
        return {
            "history_answer": None,
            "error": e
        }


def route_request(state: AnalysisState) -> str:
    """
    Routes the execution flow based on request inputs.
    """
    if state.get("image_bytes") is not None:
        return "vision_node"
    elif state.get("question") is not None:
        return "history_node"
    else:
        return END


# Build the state graph
workflow = StateGraph(AnalysisState)

workflow.add_node("vision_node", vision_node)
workflow.add_node("history_node", history_node)

# START transitions conditionally
workflow.add_conditional_edges(
    START,
    route_request,
    {
        "vision_node": "vision_node",
        "history_node": "history_node",
        END: END
    }
)

# Connect end points
workflow.add_edge("vision_node", END)
workflow.add_edge("history_node", END)

# Compile the workflow
graph = workflow.compile()


async def run_analysis_graph(
    image_bytes: Optional[bytes] = None,
    question: Optional[str] = None
) -> AnalysisState:
    """
    Runs the compiled LangGraph workflow.

    Args:
        image_bytes: Optional raw binary image data.
        question: Optional natural language question.

    Returns:
        The final AnalysisState.
    """
    initial_state = {
        "image_bytes": image_bytes,
        "vision_result": None,
        "question": question,
        "history_answer": None,
        "error": None
    }
    result_state = await graph.ainvoke(initial_state)
    return result_state
