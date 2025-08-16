from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_health_endpoint():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    # Basic shape
    for key in ["status", "version", "db_ok", "timestamp"]:
        assert key in data
    assert data["status"] in ("ok", "degraded")
    assert isinstance(data["db_ok"], bool)
