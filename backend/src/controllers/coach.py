"""
Module: coach
Layer:  Controllers

HTTP controller for interacting with the AI nutrition coach.
Exposes endpoints for asking questions about user meal history.

Author: Antigravity AI
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.agents.graph import run_analysis_graph
from src.controllers.analyze import error_response
from src.enums.error_codes import ErrorCode

from langfuse import observe, propagate_attributes
from langfuse.langchain import CallbackHandler

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/coach", tags=["Coach"])


class AskRequest(BaseModel):
    """
    Request payload schema for asking the coach.
    """
    question: str


@router.post("/ask")
async def ask_coach(payload: AskRequest):
    """
    Submit a natural-language question about meal history to the AI coach.
    """
    question = payload.question.strip()
    if not question:
        return error_response(
            ErrorCode.INTERNAL_ERROR, 
            detail="Question cannot be empty or only whitespace."
        )

    try:
        # Invoke the LangGraph workflow in history-querying mode
        state = await run_analysis_graph(image_bytes=None, question=question)
        
        # Check for execution errors
        if state.get("error"):
            raise state["error"]

        return {
            "status": "success",
            "data": {
                "answer": state["history_answer"]
            }
        }

    except Exception as e:
        logger.exception(f"Error in ask_coach controller: {e}")
        return error_response(ErrorCode.INTERNAL_ERROR, detail=str(e))


class ConfirmRequest(BaseModel):
    action: str  # "approve", "reject"
    edits: Optional[dict] = None


@router.post("/confirm/{thread_id}")
@observe(name="veonix-confirm-recommendation")
async def confirm_recommendation(thread_id: str, payload: ConfirmRequest):
    """
    Resumes the graph after user approval/editing or discards if rejected.
    """
    from src.agents.supervisor import main_graph
    from src.providers.vision.base import VisionResult

    config = {"configurable": {"thread_id": thread_id}}
    state_info = await main_graph.aget_state(config)

    if not state_info.values:
        return error_response(ErrorCode.NOT_FOUND, detail="Thread not found or expired.")

    if payload.action == "reject":
        logger.info(f"Thread {thread_id} rejected by user. Discarding recommendation.")
        return {"status": "success", "data": {"message": "Recommendation discarded."}}

    if payload.action == "approve":
        if "persist_node" not in state_info.next:
            return error_response(ErrorCode.BAD_REQUEST, detail="Graph is not paused at persist_node breakpoint.")

        if payload.edits:
            current_result = state_info.values.get("vision_result")
            if current_result:
                import dataclasses

                updates = {}
                # Mapping of payload edits to VisionResult fields
                mapping = {
                    "food_name": ("food_name", str),
                    "ingredients": ("ingredients", list),
                    "weight_grams": ("estimated_weight_grams", int),
                    "meal_type": ("meal_type", str),
                    "cuisine": ("cuisine", str),
                    "preparation_method": ("preparation_method", str),
                    "calories": ("calories", float),
                    "protein": ("protein", float),
                    "carbs": ("carbs", float),
                    "fat": ("fat", float),
                    "fiber": ("fiber", float),
                    "sodium": ("sodium", float),
                }

                for src_key, (dest_key, cast_type) in mapping.items():
                    if src_key in payload.edits:
                        val = payload.edits[src_key]
                        if val is not None:
                            try:
                                updates[dest_key] = cast_type(val)
                            except (ValueError, TypeError):
                                pass

                if updates:
                    updated_result = dataclasses.replace(current_result, **updates)
                    await main_graph.aupdate_state(config, {"vision_result": updated_result}, as_node="vision_node")

        # Resume graph execution
        with propagate_attributes(
            session_id=thread_id,
            tags=["confirm"]
        ):
            langfuse_handler = CallbackHandler()
        config["callbacks"] = config.get("callbacks", []) + [langfuse_handler]

        resumed_state = await main_graph.ainvoke(None, config=config)
        if resumed_state.get("error"):
            raise resumed_state["error"]

        return {"status": "success", "data": {"message": "Meal persisted successfully."}}

    return error_response(ErrorCode.BAD_REQUEST, detail="Invalid action. Must be 'approve' or 'reject'.")


@router.get("/history/{thread_id}")
async def get_thread_history(thread_id: str):
    """
    Exposes the graph's checkpoint history for conversation debugging/time-travel.
    Gated behind settings.DEBUG=True.
    """
    from src.config import settings
    if not settings.DEBUG:
        raise HTTPException(status_code=403, detail="Debug history endpoint is disabled.")

    from src.agents.supervisor import main_graph
    config = {"configurable": {"thread_id": thread_id}}
    
    history = []
    async for checkpoint in main_graph.aget_state_history(config):
        res = checkpoint.values.get("vision_result")
        history.append({
            "checkpoint_id": checkpoint.config["configurable"].get("checkpoint_id"),
            "next": checkpoint.next,
            "values": {
                "vision_result": {
                    "food_name": res.food_name,
                    "calories": res.calories,
                    "protein": res.protein,
                    "carbs": res.carbs,
                    "fat": res.fat
                } if res else None,
                "question": checkpoint.values.get("question"),
                "history_answer": checkpoint.values.get("history_answer"),
                "error": str(checkpoint.values.get("error")) if checkpoint.values.get("error") else None
            }
        })
        
    return {"status": "success", "data": history}

