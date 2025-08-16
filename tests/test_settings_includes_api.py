from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_get_settings_with_providers_and_flags(monkeypatch):
    # Ensure one env key present to set a flag true
    monkeypatch.setenv("OPENAI_API_KEY", "sk-aaaaaaaaaaaaaaaaaaaa")

    r = client.get("/settings", params={"include_providers": True, "include_effective_flags": True})
    assert r.status_code == 200
    data = r.json()

    assert "providers" in data
    assert sorted(data["providers"]["allowed"]) == sorted(["openai","anthropic","openrouter","local","none"]) 
    assert "notes" in data["providers"] and all(k in data["providers"]["notes"] for k in data["providers"]["allowed"]) 

    assert "api_keys_present" in data and isinstance(data["api_keys_present"], dict)
    assert data["api_keys_present"].get("openai") is True
