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
    A graph node that queries user meal history using safe database tool.
    """
    try:
        if not state.get("question"):
            raise ValueError("No question provided for history_node.")
            
        from src.agents.tools.sql_tool import query_meal_history
        answer = await query_meal_history(state["question"])
        
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
