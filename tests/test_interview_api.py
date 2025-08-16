from fastapi.testclient import TestClient

from src.api.main import app
from src.models.database import DatabaseConfig, Problem

client = TestClient(app)

def seed_problem() -> str:
    db = DatabaseConfig().get_session()
    try:
        p = db.query(Problem).filter(Problem.id == "interview_test_1").first()
        if not p:
            p = Problem(
                id="interview_test_1",
                platform="custom",
                platform_id="p1",
                title="Interview Test Problem",
                difficulty="Medium",
                category="test",
                algorithm_tags=["arrays"],
                google_interview_relevance=20.0,
                quality_score=20.0,
            )
            db.add(p)
            db.commit()
    finally:
        db.close()
    return "interview_test_1"


def test_interview_flow():
    pid = seed_problem()

    # Start
    resp_start = client.post(
        "/interview/start",
        json={"problem_id": pid, "duration_minutes": 30, "constraints": {"no_ide": True}},
    )
    assert resp_start.status_code == 200, resp_start.text
    start_data = resp_start.json()
    assert "session_id" in start_data

    # Complete
    resp_complete = client.post(
        "/interview/complete",
        json={
            "session_id": start_data["session_id"],
            "code": "def solve():\n    pass\n" + ("#" * 120),
            "tests_count": 3,
            "passed_tests": 3,
            "reasoning_notes": "Clarify plan. Complexity O(n). Tradeoff chosen. Walkthrough examples. Structure steps.",
            "time_spent_minutes": 25,
        },
    )
    assert resp_complete.status_code == 200, resp_complete.text
    result = resp_complete.json()
    rubric = result["rubric"]
    assert set(["algorithms_dsa", "coding", "communication", "problem_solving"]) <= set(rubric.keys())
