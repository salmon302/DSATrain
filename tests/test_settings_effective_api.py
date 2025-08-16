from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_effective_settings_flags(monkeypatch):
    # Ensure at least one env key is set
    monkeypatch.setenv("OPENAI_API_KEY", "sk-aaaaaaaaaaaaaaaaaaaa")
    r = client.get("/settings/effective")
    assert r.status_code == 200
    data = r.json()
    assert "api_keys_present" in data and isinstance(data["api_keys_present"], dict)
    # Should show True for openai presence when env var is set
    assert data["api_keys_present"].get("openai") is True
    # Raw api_keys should not be present
    assert "api_keys" not in data
