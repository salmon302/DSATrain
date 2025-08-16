from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_effective_model_default_from_provider(monkeypatch):
    # No model set in settings, provider openai should default to first suggestion
    monkeypatch.setenv("OPENAI_API_KEY", "sk-aaaaaaaaaaaaaaaaaaaa")
    r = client.get("/settings/effective")
    assert r.status_code == 200
    data = r.json()
    # provider defaults to 'none' initially; set provider via update first
    r2 = client.put("/settings", json={"ai_provider": "openai"})
    assert r2.status_code == 200
    r3 = client.get("/settings/effective")
    assert r3.status_code == 200
    data2 = r3.json()
    assert data2.get("ai_provider") == "openai"
    assert data2.get("effective_model") is not None


def test_get_settings_includes_effective_model(monkeypatch):
    # Make sure inline flags include effective_model
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-aaaaaaaaaaaaaaaaaaaaaa")
    r = client.put("/settings", json={"ai_provider": "anthropic", "model": None})
    assert r.status_code == 200
    r2 = client.get("/settings", params={"include_effective_flags": True})
    assert r2.status_code == 200
    data = r2.json()
    assert "effective_model" in data
    assert data["effective_model"] is not None
