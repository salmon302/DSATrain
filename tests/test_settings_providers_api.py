from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_get_allowed_providers():
    r = client.get("/settings/providers")
    assert r.status_code == 200
    data = r.json()
    assert "allowed" in data and isinstance(data["allowed"], list)
    # Basic sanity: expected providers present
    for p in ["openai", "anthropic", "openrouter", "local", "none"]:
        assert p in data["allowed"]
    # Notes shape
    assert "notes" in data and all(k in data["notes"] for k in data["allowed"])  
