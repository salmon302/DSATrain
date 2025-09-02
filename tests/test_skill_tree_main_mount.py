import os
import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture(scope="module")
def client():
    # Ensure tables auto-create for in-memory or when explicitly requested
    os.environ.setdefault("DSATRAIN_AUTO_CREATE_TABLES", "1")
    return TestClient(app)


def test_skill_tree_preferences_roundtrip(client):
    user_id = "default_user"

    # GET preferences should return defaults initially
    r = client.get(f"/skill-tree/preferences/{user_id}")
    assert r.status_code == 200, r.text
    data = r.json()
    assert set(data.keys()) >= {
        "preferred_view_mode",
        "show_confidence_overlay",
        "auto_expand_clusters",
        "highlight_prerequisites",
        "visible_skill_areas",
    }

    # Update preferences
    new_prefs = {
        "preferred_view_mode": "grid",
        "show_confidence_overlay": False,
        "auto_expand_clusters": True,
        "highlight_prerequisites": True,
        "visible_skill_areas": ["arrays", "graphs"],
    }
    r2 = client.post(f"/skill-tree/preferences/{user_id}", json=new_prefs)
    assert r2.status_code == 200, r2.text

    # Get again and verify persisted
    r3 = client.get(f"/skill-tree/preferences/{user_id}")
    assert r3.status_code == 200
    data3 = r3.json()
    assert data3["preferred_view_mode"] == "grid"
    assert data3["show_confidence_overlay"] is False
    assert data3["auto_expand_clusters"] is True
    assert data3["visible_skill_areas"] == ["arrays", "graphs"]


def test_skill_tree_overview_available(client):
    # Even if DB is empty, endpoint should respond (may 404 if no problems exist)
    r = client.get("/skill-tree/overview", params={"user_id": "default_user"})
    assert r.status_code in (200, 404)


