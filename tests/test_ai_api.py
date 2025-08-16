from fastapi.testclient import TestClient

from src.api.main import app
from src.models.database import DatabaseConfig, Problem
from src.services.settings_service import SettingsService

client = TestClient(app)


def seed_problem() -> str:
    db = DatabaseConfig().get_session()
    try:
        p = db.query(Problem).filter(Problem.id == "ai_test_1").first()
        if not p:
            p = Problem(
                id="ai_test_1",
                platform="custom",
                platform_id="p1",
                title="AI Test Problem",
                difficulty="Easy",
                category="test",
                algorithm_tags=["two_pointers", "arrays"],
                google_interview_relevance=10.0,
                quality_score=10.0,
            )
            db.add(p)
            db.commit()
    finally:
        db.close()
    return "ai_test_1"


def enable_ai():
    s = SettingsService()
    s.update({
        "enable_ai": True,
        "ai_provider": "openai",
        "model": "gpt-4o-mini",
        "api_keys": {"openai": "sk-12345678901234567890"}
    })


def test_ai_endpoints_enabled():
    pid = seed_problem()
    enable_ai()

    # Hint
    r1 = client.post("/ai/hint", json={"problem_id": pid, "query": "edge cases?"})
    assert r1.status_code == 200, r1.text
    data1 = r1.json()
    assert "hints" in data1 and isinstance(data1["hints"], list)

    # Review
    r2 = client.post("/ai/review", json={"code": "def f():\n    return 1\n", "rubric": {"criteria": ["c", "r"]}})
    assert r2.status_code == 200, r2.text
    data2 = r2.json()
    assert "suggestions" in data2

    # Elaborate
    r3 = client.post("/ai/elaborate", json={"problem_id": pid})
    assert r3.status_code == 200, r3.text
    data3 = r3.json()
    assert "why_questions" in data3 and "how_questions" in data3


def test_ai_disabled_guard():
    # Disable AI
    s = SettingsService()
    s.update({
        "enable_ai": False,
        "ai_provider": "none",
        "model": None,
        "api_keys": {"openai": None}
    })

    pid = seed_problem()
    r = client.post("/ai/hint", json={"problem_id": pid})
    assert r.status_code == 403
