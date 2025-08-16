from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_ai_status_endpoint_basic():
    # Enable local provider with small limits for deterministic behavior
    r = client.put("/settings", json={
        "enable_ai": True,
        "ai_provider": "local",
        "model": "ollama/llama3:8b-instruct",
        "rate_limit_per_minute": 2,
        "hint_budget_per_session": 3,
    })
    assert r.status_code == 200

    s = client.get("/ai/status")
    assert s.status_code == 200
    data = s.json()
    assert data["enabled"] is True
    assert data["provider"] == "local"
    assert data["rate_limit_per_minute"] == 2
    assert "rate_limit_used" in data
    assert "rate_limit_window_seconds" in data
    assert data["hint_budget_per_session"] == 3
    # Cleanup: restore defaults
    client.put("/settings", json={
        "enable_ai": False,
        "ai_provider": "none",
        "model": None,
        "rate_limit_per_minute": 30,
        "hint_budget_per_session": 5,
    })


def test_retry_after_header_on_rate_limit():
    # Configure very low limit
    client.put("/settings", json={
        "enable_ai": True,
        "ai_provider": "local",
        "model": "ollama/llama3:8b-instruct",
        "rate_limit_per_minute": 1,
        "hint_budget_per_session": 5,
    })
    # First review ok
    r1 = client.post("/ai/review", json={"code": "print('x')"})
    assert r1.status_code == 200
    # Second immediately should hit rate limit
    r2 = client.post("/ai/review", json={"code": "print('y')"})
    assert r2.status_code == 429
    # Retry-After header should be present and an integer string >= 1
    ra = r2.headers.get("Retry-After")
    assert ra is not None
    assert ra.isdigit()
    assert int(ra) >= 1
    # Cleanup: restore defaults
    client.put("/settings", json={
        "enable_ai": False,
        "ai_provider": "none",
        "model": None,
        "rate_limit_per_minute": 30,
        "hint_budget_per_session": 5,
    })
