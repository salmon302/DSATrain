from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)

def test_models_full_mapping():
    r = client.get("/settings/models")
    assert r.status_code == 200
    data = r.json()
    assert "models" in data and isinstance(data["models"], dict)
    # Should include keys for all allowed providers
    for p in ["openai","anthropic","openrouter","local","none"]:
        assert p in data["models"]
        assert isinstance(data["models"][p], list)


def test_models_filtered_provider():
    r = client.get("/settings/models", params={"provider": "openai"})
    assert r.status_code == 200
    data = r.json()
    assert data["provider"] == "openai"
    assert isinstance(data["models"], list)


def test_models_invalid_provider():
    r = client.get("/settings/models", params={"provider": "badprov"})
    assert r.status_code == 400
    assert "Invalid provider" in r.text
