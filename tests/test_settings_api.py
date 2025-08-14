import json
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_get_settings_masked():
    resp = client.get("/settings")
    assert resp.status_code == 200
    data = resp.json()
    assert "api_keys" in data


def test_update_settings_and_cognitive_profile():
    # Update settings
    payload = {
        "enable_ai": True,
        "ai_provider": "openai",
        "model": "gpt-4o-mini",
        "api_keys": {"openai": "sk-12345678901234567890"},
        "rate_limit_per_minute": 15,
        "monthly_cost_cap_usd": 5.0,
        "hint_budget_per_session": 3
    }
    resp = client.put("/settings", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["enable_ai"] is True
    assert data["ai_provider"] == "openai"
    # Key should be masked
    assert data["api_keys"]["openai"].endswith("7890")
    assert set(data["api_keys"]["openai"]) == set("*7890")

    # Update cognitive profile
    profile = {
        "working_memory_capacity": 7,
        "learning_style_preference": "balanced",
        "visual_vs_verbal": 0.5,
        "processing_speed": "average"
    }
    resp2 = client.post("/settings/cognitive-profile", json=profile)
    assert resp2.status_code == 200, resp2.text
    data2 = resp2.json()
    assert data2["cognitive_profile"]["working_memory_capacity"] == 7
