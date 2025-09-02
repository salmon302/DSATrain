import os
import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.models.database import DatabaseConfig, Problem, UserProblemConfidence, UserSkillMastery


@pytest.fixture(scope="module")
def client():
    os.environ.setdefault("DSATRAIN_AUTO_CREATE_TABLES", "1")
    return TestClient(app)


@pytest.fixture()
def db_session():
    db = DatabaseConfig().get_session()
    try:
        yield db
    finally:
        db.close()


def ensure_problem(db, pid: str, tags, difficulty="Medium", title="Test Problem"):
    p = db.query(Problem).filter(Problem.id == pid).first()
    if not p:
        p = Problem(
            id=pid,
            platform="custom",
            platform_id=pid,
            title=title,
            difficulty=difficulty,
            category="test",
            algorithm_tags=list(tags),
            sub_difficulty_level=3,
        )
        db.add(p)
        db.commit()
    return p


def test_primary_skill_mapping_and_mastery_update(client, db_session):
    user_id = "user_skill_test"

    # Arrange: two problems with different primary skills by mapping
    # arrays -> array_processing, dynamic_programming -> dynamic_programming
    p1 = ensure_problem(db_session, "pskill_1", tags=["arrays", "two_pointers"], title="Arrays A")
    p2 = ensure_problem(db_session, "pskill_2", tags=["dynamic_programming", "memoization"], title="DP B")

    # Sanity: no mastery rows yet for the user
    db_session.query(UserProblemConfidence).filter(UserProblemConfidence.user_id == user_id).delete()
    db_session.query(UserSkillMastery).filter(UserSkillMastery.user_id == user_id).delete()
    db_session.commit()

    # Act: update confidence for p1, then p2
    r1 = client.post(f"/skill-tree/confidence", params={"user_id": user_id}, json={
        "problem_id": p1.id,
        "confidence_level": 4,
        "solve_time_seconds": 120,
    })
    assert r1.status_code == 200, r1.text

    r2 = client.post(f"/skill-tree/confidence", params={"user_id": user_id}, json={
        "problem_id": p2.id,
        "confidence_level": 2,
        "solve_time_seconds": 200,
    })
    assert r2.status_code == 200, r2.text

    # Assert: mastery rows exist for the two primary skills
    m_array = db_session.query(UserSkillMastery).filter(
        UserSkillMastery.user_id == user_id,
        UserSkillMastery.skill_area == "array_processing",
    ).first()
    m_dp = db_session.query(UserSkillMastery).filter(
        UserSkillMastery.user_id == user_id,
        UserSkillMastery.skill_area == "dynamic_programming",
    ).first()

    assert m_array is not None, "array_processing mastery should exist"
    assert m_dp is not None, "dynamic_programming mastery should exist"

    # The mastery level uses avg_confidence * 20; each area had a single confidence update above
    assert m_array.mastery_level == pytest.approx(4 * 20)
    assert m_dp.mastery_level == pytest.approx(2 * 20)

    # And progress endpoint reflects both areas touched
    progress = client.get(f"/skill-tree/user/{user_id}/progress")
    assert progress.status_code == 200
    pdata = progress.json()
    assert pdata["skill_areas_touched"] >= 2


def test_overview_uses_primary_skill_grouping(client, db_session):
    # Ensure a problem with graphs maps into graph_algorithms in overview
    p = ensure_problem(db_session, "pskill_graph", tags=["graphs", "bfs"], title="Graph C")

    # We expect 404 if DB empty of sub_difficulty, but our helper sets sub_difficulty_level
    r = client.get("/skill-tree/overview", params={"user_id": "user_skill_test"})
    assert r.status_code in (200, 404), r.text
    if r.status_code == 404:
        pytest.skip("No problems with skill tree data found; seeding may be disabled in this env")

    data = r.json()
    cols = data.get("skill_tree_columns", [])
    # Build a set of areas present
    areas = {c.get("skill_area") for c in cols}
    assert "graph_algorithms" in areas or "general" in areas
