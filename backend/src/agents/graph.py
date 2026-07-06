"""
Module: graph
Layer:  Agents

LangGraph-based orchestration graph for vision analysis.
Wraps the vision provider execution as a single-node graph.

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
    State schema for the food image analysis workflow.
    """
    image_bytes: bytes
    vision_result: Optional[VisionResult]
    error: Optional[Any]


async def vision_node(state: AnalysisState) -> dict:
    """
    A graph node that runs the Gemini provider image analysis.
    """
    try:
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


# Build the state graph with a single node
workflow = StateGraph(AnalysisState)

workflow.add_node("vision_node", vision_node)

workflow.add_edge(START, "vision_node")
workflow.add_edge("vision_node", END)

# Compile the workflow
graph = workflow.compile()


async def run_analysis_graph(image_bytes: bytes) -> AnalysisState:
    """
    Runs the compiled LangGraph workflow for vision analysis.

    Args:
        image_bytes: Raw binary image data.

    Returns:
        The final AnalysisState.
    """
    initial_state = {
        "image_bytes": image_bytes,
        "vision_result": None,
        "error": None
    }
    result_state = await graph.ainvoke(initial_state)
    return result_state
