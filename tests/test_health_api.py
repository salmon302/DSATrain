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
    # Cache section
    assert "cache" in data
    cache = data["cache"]
    assert "serialization" in cache
    assert cache["serialization"] in ("pickle", "json")
    assert isinstance(cache.get("memory_cache_size", 0), int)
