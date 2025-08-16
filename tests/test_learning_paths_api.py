from fastapi.testclient import TestClient

from src.api.main import app
from src.models.database import DatabaseConfig, Problem

client = TestClient(app)


def seed_minimal_problems():
    db = DatabaseConfig().get_session()
    try:
        # Ensure a few problems exist to populate weekly plans
        for pid, title, tags in [
            ("lp_p1", "Arrays 101", ["arrays", "hashing"]),
            ("lp_p2", "Two Pointers Intro", ["two_pointers", "arrays"]),
            ("lp_p3", "Sliding Window Basics", ["sliding_window", "strings"]),
        ]:
            p = db.query(Problem).filter(Problem.id == pid).first()
            if not p:
                p = Problem(
                    id=pid,
                    platform="custom",
                    platform_id=pid,
                    title=title,
                    difficulty="Easy",
                    category="test",
                    algorithm_tags=tags,
                    google_interview_relevance=5.0,
                    quality_score=5.0,
                )
                db.add(p)
        db.commit()
    finally:
        db.close()


def test_generate_and_progress_and_adapt_learning_path():
    seed_minimal_problems()

    # Generate a path
    payload = {
        "user_id": "u1",
        "current_skill_levels": {"arrays": 0.4, "two_pointers": 0.3},
        "learning_goals": ["interview_prep"],
        "available_hours_per_week": 6,
        "preferred_difficulty_curve": "gradual",
        "target_completion_weeks": 4,
    }
    r = client.post("/learning-paths/generate", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    lp = data["learning_path"]

    # Weekly plan should be present and enriched with problem objects
    assert "weekly_plan" in lp and isinstance(lp["weekly_plan"], list)
    if lp["weekly_plan"]:
        wk = lp["weekly_plan"][0]
        assert isinstance(wk.get("problems", []), list)
        # Each problem should be object-like (have id/title)
        for pr in wk.get("problems", []):
            assert "id" in pr and "title" in pr

    path_id = lp.get("id") or lp.get("path_id")
    assert path_id, "Expected learning path to have an id"

    # Fetch path
    r_get = client.get(f"/learning-paths/{path_id}")
    assert r_get.status_code == 200
    details = r_get.json()
    # Milestones may be empty when first generated; ensure response shape
    assert isinstance(details, dict) and "id" in details

    # Next problems
    r_next = client.get(f"/learning-paths/{path_id}/next-problems", params={"count": 3})
    assert r_next.status_code == 200
    nxt = r_next.json()
    assert "problems" in nxt and isinstance(nxt["problems"], list)

    # Progress update (use one known problem id from our seeded set if present)
    known = None
    for wk in lp.get("weekly_plan", []):
        for pr in wk.get("problems", []):
            if isinstance(pr, dict) and pr.get("id"):
                known = pr["id"]
                break
        if known:
            break
    if not known:
        known = "lp_p1"

    r_prog = client.post(
        f"/learning-paths/{path_id}/progress",
        json={
            "problem_id": known,
            "success": True,
            "time_spent_seconds": 300,
            "additional_metrics": {"notes": "went well"},
        },
    )
    assert r_prog.status_code == 200
    upd = r_prog.json()
    assert "progress_update" in upd

    # Adapt path with a minimal payload
    r_adapt = client.post(
        f"/learning-paths/{path_id}/adapt",
        json={"recent_performance": {"success_rate": 0.7}},
    )
    assert r_adapt.status_code == 200
