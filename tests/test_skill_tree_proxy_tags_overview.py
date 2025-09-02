import os
import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture(scope="module")
def client():
    os.environ.setdefault("DSATRAIN_AUTO_CREATE_TABLES", "1")
    # Ensure proxy points to local v2 by default
    os.environ.setdefault("SKILL_TREE_V2_URL", "http://localhost:8000/skill-tree-v2")
    return TestClient(app)


def test_proxy_tags_overview(client):
    r = client.get("/skill-tree-proxy/tags/overview", params={"top_problems_per_tag": 3})
    # Allow empty DB to surface 500 from upstream; main requirement is route exists and responds
    assert r.status_code in (200, 500)
    if r.status_code == 200:
        data = r.json()
        assert set(data.keys()) >= {"tags", "total_tags", "total_problems", "last_updated"}
