"""
Tests for the /profile endpoint.
Verifies reading, updating, and seeding of settings profiles.
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_profile_lifecycle():
    """
    Verifies default profile seeding, retrieval, and updating.
    """
    # 1. Fetching profile for first time (should auto-seed default empty values)
    get_response = client.get("/profile")
    assert get_response.status_code == 200
    
    get_data = get_response.json()
    assert get_data["status"] == "success"
    assert get_data["data"]["user_id"] == "default"
    
    # 2. Update profile goal and allergies
    payload = {
        "dietary_goal": "Gain lean muscle mass",
        "allergies": ["peanut", "hazelnut"]
    }
    
    put_response = client.put("/profile", json=payload)
    assert put_response.status_code == 200
    
    put_data = put_response.json()
    assert put_data["status"] == "success"
    assert put_data["data"]["dietary_goal"] == "Gain lean muscle mass"
    assert "peanut" in put_data["data"]["allergies"]
    
    # 3. Retrieve again to confirm persistence
    verify_response = client.get("/profile")
    assert verify_response.status_code == 200
    
    verify_data = verify_response.json()
    assert verify_data["data"]["dietary_goal"] == "Gain lean muscle mass"
    assert "hazelnut" in verify_data["data"]["allergies"]
