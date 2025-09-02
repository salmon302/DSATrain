import os
import pytest
from fastapi.testclient import TestClient

# Ensure app import path
from src.api.skill_tree_server import app
from src.models.database import DatabaseConfig, UserSkillMastery

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

@pytest.fixture()
def db_session():
    db = DatabaseConfig().get_session()
    try:
        yield db
    finally:
        db.close()

@pytest.mark.parametrize("skill_area, expected", [
    ("dynamic_programming", 73.5),
])
def test_overview_optimized_mastery_reflected(client, db_session, skill_area, expected):
    # Arrange: upsert mastery for default_user
    user_id = "default_user"
    mastery = db_session.query(UserSkillMastery).filter(
        UserSkillMastery.user_id == user_id,
        UserSkillMastery.skill_area == skill_area,
    ).first()
    if not mastery:
        mastery = UserSkillMastery(user_id=user_id, skill_area=skill_area)
        db_session.add(mastery)
    mastery.mastery_level = expected
    db_session.commit()

    # Act
    resp = client.get(f"/skill-tree-v2/overview-optimized", params={"user_id": user_id})
    assert resp.status_code == 200, resp.text
    data = resp.json()

    # Assert: find the skill area summary and check mastery
    areas = {s["skill_area"]: s for s in data.get("skill_areas", [])}
    assert skill_area in areas, f"Skill area {skill_area} not found in overview"
    assert areas[skill_area]["mastery_percentage"] == pytest.approx(expected)
