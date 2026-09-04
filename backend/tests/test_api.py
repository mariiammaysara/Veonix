"""
API integration smoke tests.
Run:  pytest tests/test_api.py -v
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_health_endpoint_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["vision"]["provider"] == "Gemini"
    assert "model" in data["vision"]


def test_analyze_rejects_bad_content_type():
    response = client.post(
        "/analyze/image",
        files={"file": ("test.txt", b"not an image", "text/plain")},
    )
    assert response.status_code == 415
    assert "JPEG" in response.json()["error"]["message"]
