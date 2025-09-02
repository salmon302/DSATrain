import os
from fastapi.testclient import TestClient

from src.api.main import app
from src.models.database import DatabaseConfig, Problem, UserSkillTreePreferences

client = TestClient(app)


def ensure_problem(db, pid: str, title: str):
    p = db.query(Problem).filter(Problem.id == pid).first()
    if not p:
        p = Problem(
            id=pid,
            platform="custom",
            platform_id=pid,
            title=title,
            difficulty="Easy",
            category="test",
            algorithm_tags=["arrays"],
        )
        db.add(p)
        db.commit()
    return p


def test_favorites_order_preserved(tmp_path):
    os.environ.setdefault("DSATRAIN_AUTO_CREATE_TABLES", "1")
    db = DatabaseConfig().get_session()
    try:
        # Ensure problems exist
        ensure_problem(db, "fav_1", "A")
        ensure_problem(db, "fav_2", "B")
        ensure_problem(db, "fav_3", "C")
        # Ensure user prefs row exists (not strictly necessary but mirrors other tests)
        prefs = db.query(UserSkillTreePreferences).filter(UserSkillTreePreferences.user_id=="fav_user").first()
        if not prefs:
            prefs = UserSkillTreePreferences(user_id="fav_user", bookmarked_problems=[])
            db.add(prefs)
            db.commit()
    finally:
        db.close()

    # Toggle favorites in a specific order
    for pid in ["fav_2", "fav_1", "fav_3"]:
        r = client.post("/favorites/toggle", json={
            "user_id": "fav_user",
            "problem_id": pid,
            "favorite": True,
        })
        assert r.status_code == 200, r.text

    # List favorites IDs (no details) and assert order preserved
    r2 = client.get("/favorites", params={"user_id": "fav_user", "include_details": False})
    assert r2.status_code == 200, r2.text
    data = r2.json()
    assert data.get("problem_ids") == ["fav_2", "fav_1", "fav_3"], data

    # Now un-favorite the middle one and ensure order updates without re-sorting others
    r3 = client.post("/favorites/toggle", json={
        "user_id": "fav_user",
        "problem_id": "fav_1",
        "favorite": False,
    })
    assert r3.status_code == 200, r3.text

    r4 = client.get("/favorites", params={"user_id": "fav_user", "include_details": False})
    assert r4.status_code == 200
    data2 = r4.json()
    assert data2.get("problem_ids") == ["fav_2", "fav_3"], data2
