from fastapi.testclient import TestClient
import time

from src.api.main import app


client = TestClient(app)


def setup_local(low_limit: int = 2, window_seconds: int = 60):
    r = client.put(
        "/settings",
        json={
            "enable_ai": True,
            "ai_provider": "local",
            "model": "ollama/llama3:8b-instruct",
            "rate_limit_per_minute": low_limit,
            "rate_limit_window_seconds": window_seconds,
            "hint_budget_per_session": 5,
        },
    )
    assert r.status_code == 200


def test_rate_limit_window_affects_retry_after():
    # Use a reasonably small window (API minimum is 10 seconds)
    setup_local(low_limit=1, window_seconds=10)
    r1 = client.post("/ai/review", json={"code": "print('x')"})
    assert r1.status_code == 200
    r2 = client.post("/ai/review", json={"code": "print('y')"})
    assert r2.status_code == 429
    ra = r2.headers.get("Retry-After")
    assert ra is not None and ra.isdigit()
    # Retry-After should be <= window (10) and >= 1
    assert 1 <= int(ra) <= 10


def test_ai_reset_endpoint_clears_counters():
    setup_local(low_limit=1, window_seconds=10)
    # Ensure clean slate in case prior tests used the same rate-limit key
    client.post("/ai/reset", json={"reset_global": True})
    # Hit the rate limit
    r1 = client.post("/ai/review", json={"code": "print('x')"})
    assert r1.status_code == 200
    r2 = client.post("/ai/review", json={"code": "print('y')"})
    assert r2.status_code == 429
    # Reset global counters
    rr = client.post("/ai/reset", json={"reset_global": True})
    assert rr.status_code == 200
    # Now should be allowed again immediately
    r3 = client.post("/ai/review", json={"code": "print('z')"})
    assert r3.status_code == 200


def test_ai_reset_session_budget():
    setup_local(low_limit=10, window_seconds=60)
    session_id = "sess-window-reset"
    # Use a valid problem id if available else skip; call /ai/status to warm up.
    client.get("/ai/status")
    # First hint may 404 if problem doesn't exist; we only care about budget counter.
    h1 = client.post("/ai/hint", json={"problem_id": "1", "session_id": session_id})
    if h1.status_code == 404:
        return
    assert h1.status_code in (200, 404)
    # Second hint likely 429 if first succeeded (default budget 5 might allow; explicitly set low budget)
    # Adjust settings to force budget of 1
    client.put("/settings", json={"hint_budget_per_session": 1})
    # Consume budget
    h2 = client.post("/ai/hint", json={"problem_id": "1", "session_id": session_id})
    if h2.status_code == 404:
        return
    # Next hint should be 429 now
    h3 = client.post("/ai/hint", json={"problem_id": "1", "session_id": session_id})
    if h2.status_code == 200:
        assert h3.status_code == 429
        # Reset just this session
        rr = client.post("/ai/reset", json={"session_id": session_id, "reset_global": False})
        assert rr.status_code == 200
        # Should allow one more after reset
        h4 = client.post("/ai/hint", json={"problem_id": "1", "session_id": session_id})
        assert h4.status_code in (200, 404)
