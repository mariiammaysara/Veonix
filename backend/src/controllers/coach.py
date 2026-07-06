"""
Module: coach
Layer:  Controllers

HTTP controller for interacting with the AI nutrition coach.
Exposes endpoints for asking questions about user meal history.

Author: Antigravity AI
"""

import logging
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.agents.graph import run_analysis_graph
from src.controllers.analyze import error_response
from src.enums.error_codes import ErrorCode

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
