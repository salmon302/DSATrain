import os
import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.models.database import DatabaseConfig, Problem

redis = pytest.importorskip("redis")

client = TestClient(app)


def _have_redis(url: str) -> bool:
    try:
        r = redis.StrictRedis.from_url(url)
        return bool(r.ping())
    except Exception:
        return False


def seed_problem(pid: str = "redis_test_1") -> str:
    db = DatabaseConfig().get_session()
    try:
        p = db.query(Problem).filter(Problem.id == pid).first()
        if not p:
            p = Problem(
                id=pid,
                platform="custom",
                platform_id="p1",
                title="Redis Test Problem",
                difficulty="Easy",
                category="test",
                algorithm_tags=["arrays"],
                google_interview_relevance=1.0,
                quality_score=1.0,
            )
            db.add(p)
            db.commit()
    finally:
        db.close()
    return pid


@pytest.mark.skipif(not _have_redis(os.getenv("DSATRAIN_REDIS_URL", "redis://localhost:6379/0")), reason="Redis not available")
def test_redis_rate_limit_and_reset(monkeypatch):
    # Enable Redis mode
    monkeypatch.setenv("DSATRAIN_USE_REDIS_RATE_LIMIT", "1")
    monkeypatch.setenv("DSATRAIN_REDIS_URL", os.getenv("DSATRAIN_REDIS_URL", "redis://localhost:6379/0"))

    # Configure local provider with low limit
    r = client.put(
        "/settings",
        json={
            "enable_ai": True,
            "ai_provider": "local",
            "model": "ollama/llama3:8b-instruct",
            "rate_limit_per_minute": 1,
            "rate_limit_window_seconds": 10,
            "hint_budget_per_session": 1,
        },
    )
    assert r.status_code == 200

    # First review ok, second 429 across same process (and across processes if scaled)
    r1 = client.post("/ai/review", json={"code": "print('x')"})
    assert r1.status_code == 200
    r2 = client.post("/ai/review", json={"code": "print('y')"})
    assert r2.status_code == 429
    assert r2.headers.get("Retry-After") is not None

    # Reset global in Redis
    rr = client.post("/ai/reset", json={"reset_global": True})
    assert rr.status_code == 200

    # Should be allowed again immediately
    r3 = client.post("/ai/review", json={"code": "print('z')"})
    assert r3.status_code == 200


@pytest.mark.skipif(not _have_redis(os.getenv("DSATRAIN_REDIS_URL", "redis://localhost:6379/0")), reason="Redis not available")
def test_redis_hint_budget_reset(monkeypatch):
    monkeypatch.setenv("DSATRAIN_USE_REDIS_RATE_LIMIT", "1")
    monkeypatch.setenv("DSATRAIN_REDIS_URL", os.getenv("DSATRAIN_REDIS_URL", "redis://localhost:6379/0"))

    pid = seed_problem()

    # Set low budget
    r = client.put(
        "/settings",
        json={
            "enable_ai": True,
            "ai_provider": "local",
            "model": "ollama/llama3:8b-instruct",
            "rate_limit_per_minute": 10,
            "rate_limit_window_seconds": 60,
            "hint_budget_per_session": 1,
        },
    )
    assert r.status_code == 200

    session_id = "sess-redis-1"
    h1 = client.post("/ai/hint", json={"problem_id": pid, "session_id": session_id})
    assert h1.status_code == 200
    h2 = client.post("/ai/hint", json={"problem_id": pid, "session_id": session_id})
    assert h2.status_code == 429

    # Reset just this session budget in Redis
    rr = client.post("/ai/reset", json={"session_id": session_id, "reset_global": False})
    assert rr.status_code == 200

    # One more should be allowed after reset
    h3 = client.post("/ai/hint", json={"problem_id": pid, "session_id": session_id})
    assert h3.status_code == 200
