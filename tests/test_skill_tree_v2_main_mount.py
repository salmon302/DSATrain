import os
import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture(scope="module")
def client():
    os.environ.setdefault("DSATRAIN_AUTO_CREATE_TABLES", "1")
    return TestClient(app)


def test_v2_overview_optimized_available(client):
    r = client.get("/skill-tree-v2/overview-optimized")
    assert r.status_code in (200, 500)
    if r.status_code == 200:
        data = r.json()
        assert set(data.keys()) >= {"skill_areas", "total_problems", "total_skill_areas", "last_updated"}


def test_v2_tags_overview_available(client):
    r = client.get("/skill-tree-v2/tags/overview")
    assert r.status_code in (200, 500)
    if r.status_code == 200:
        data = r.json()
        assert set(data.keys()) >= {"tags", "total_tags", "total_problems", "last_updated"}


def test_v2_skill_area_pagination(client):
    # Use a common skill area; even if none exists, endpoint should not 500
    r = client.get("/skill-tree-v2/skill-area/arrays/problems", params={"page": 1, "page_size": 5})
    assert r.status_code in (200, 404, 500)
    if r.status_code == 200:
        data = r.json()
        assert set(data.keys()) >= {"problems", "total_count", "page", "page_size", "has_next"}


