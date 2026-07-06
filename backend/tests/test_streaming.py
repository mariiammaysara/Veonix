"""
Tests for SSE-based food analysis progress streaming.
Verifies that POST /analyze/image/stream returns Server-Sent Events in sequence,
correctly reports progress milestones, and handles final state routing.
"""

import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from src.main import app
from src.providers.vision.base import VisionResult

client = TestClient(app)


def make_mock_vision_result(confidence: float = 0.95) -> VisionResult:
    return VisionResult(
        food_name="Healthy Avocado Toast",
        confidence=confidence,
        calories=350.0,
        protein=12.0,
        carbs=35.0,
        fat=15.0,
        fiber=8.0,
        sodium=200.0,
        estimated_weight_grams=180.0,
        meal_type="breakfast",
        cuisine="american",
        preparation_method="toasted",
        ingredients=["bread", "avocado", "salt"],
        per_100g={}
    )


def test_streaming_endpoint_returns_events_in_sequence():
    """
    Asserts that POST /analyze/image/stream correctly emits the proper progress SSE
    events in chronological order, stopping at the HITL confirmation breakpoint.
    """
    mock_result = make_mock_vision_result(confidence=0.95)

    with patch("src.agents.graph.compress_image", lambda x: x), \
         patch("src.helpers.image_processor.compress_image", lambda x: x), \
         patch("src.providers.vision.gemini_provider.GeminiProvider.analyze", AsyncMock(return_value=mock_result)):

        # Post to the stream endpoint using fastapi test client
        response = client.post(
            "/analyze/image/stream",
            files={"file": ("test.jpg", b"fake-image-bytes", "image/jpeg")},
        )

        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]

        # Parse SSE stream line-by-line
        events = []
        for line in response.iter_lines():
            if not line:
                continue
            # HTTPX TestClient iter_lines yields str, not bytes
            decoded = line.strip()
            if decoded.startswith("data:"):
                event_data = json.loads(decoded[5:].strip())
                events.append(event_data)

        # Verify we captured progress events
        assert len(events) >= 6

        # Check sequence of events
        assert events[0]["event"] == "start"
        assert "thread_id" in events[0]
        
        assert events[1]["event"] == "profile"
        assert events[2]["event"] == "vision_start"
        assert events[3]["event"] == "vision_done"
        assert events[3]["food_name"] == "Healthy Avocado Toast"
        
        assert events[4]["event"] == "allergy_check"
        assert events[5]["event"] == "saving"
        
        # Verify the end of stream because it hits interrupt_before=["persist_node"] breakpoint
        # Thus it must be "pending_confirmation"
        assert events[-1]["event"] == "pending_confirmation"
        assert "result" in events[-1]
        assert events[-1]["result"]["food_name"] == "Healthy Avocado Toast"


def test_streaming_low_confidence_event():
    """
    Asserts that if the vision model returns low confidence,
    the stream reports the 'low_confidence' event and terminates early.
    """
    mock_result = make_mock_vision_result(confidence=0.45)

    with patch("src.agents.graph.compress_image", lambda x: x), \
         patch("src.helpers.image_processor.compress_image", lambda x: x), \
         patch("src.providers.vision.gemini_provider.GeminiProvider.analyze", AsyncMock(return_value=mock_result)):

        response = client.post(
            "/analyze/image/stream",
            files={"file": ("test.jpg", b"fake-image-bytes", "image/jpeg")},
        )

        assert response.status_code == 200
        events = []
        for line in response.iter_lines():
            if not line:
                continue
            decoded = line.strip()
            if decoded.startswith("data:"):
                event_data = json.loads(decoded[5:].strip())
                events.append(event_data)

        # It should end with 'low_confidence' and NOT hit allergy_check or saving
        assert events[-1]["event"] == "low_confidence"
        assert "low confidence" in events[-1]["message"].lower()
        # Verify events like allergy_check were bypassed
        assert not any(ev["event"] == "allergy_check" for ev in events)
