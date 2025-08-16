from fastapi.testclient import TestClient

from src.api.main import app
from src.models.database import DatabaseConfig, Problem

client = TestClient(app)

def seed_problem() -> str:
    db = DatabaseConfig().get_session()
    try:
        p = db.query(Problem).filter(Problem.id == "practice_test_1").first()
        if not p:
            p = Problem(
                id="practice_test_1",
                platform="custom",
                platform_id="p1",
                title="Practice Test Problem",
                difficulty="Easy",
                category="test",
                algorithm_tags=["arrays"],
                google_interview_relevance=5.0,
                quality_score=5.0,
            )
            db.add(p)
            db.commit()
    finally:
        db.close()
    return "practice_test_1"


def test_practice_endpoints_basic():
    pid = seed_problem()

    # Generate a small session
    resp_session = client.post("/practice/session", json={"size": 1, "focus_areas": ["arrays"]})
    assert resp_session.status_code == 200, resp_session.text
    session_data = resp_session.json()
    assert session_data["count"] >= 0

    # Log attempt
    resp_attempt = client.post(
        "/practice/attempt",
        json={
            "problem_id": pid,
            "status": "attempted",
            "time_spent": 120,
            "reflection": "Thought process recorded.",
        },
    )
    assert resp_attempt.status_code == 200, resp_attempt.text
    attempt_data = resp_attempt.json()
    assert attempt_data["problem_id"] == pid

    # Log elaborative session
    resp_elab = client.post(
        "/practice/elaborative",
        json={
            "problem_id": pid,
            "why_questions": ["Why sliding window?Mar"],
            "responses": {"answer": "Because subarray pattern."},
        },
    )
    assert resp_elab.status_code == 200, resp_elab.text

    # Working memory check
    resp_wm = client.post(
        "/practice/working-memory-check",
        json={
            "metrics": {"mistakes_count": 2, "time_overrun": 0.1, "hints_used": 1, "cognitive_load_self_report": 6},
            "user_id": "default_user",
        },
    )
    assert resp_wm.status_code == 200, resp_wm.text
    data_wm = resp_wm.json()
    assert "load_score" in data_wm
