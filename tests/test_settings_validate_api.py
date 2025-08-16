import os
import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_validate_missing_key_invalid(monkeypatch):
    # Ensure no env key
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    payload = {
        "enable_ai": True,
        "ai_provider": "openai",
        "model": "gpt-4o-mini"
    }
    resp = client.post("/settings/validate", json=payload)
    assert resp.status_code == 400
    data = resp.json()
    # error structure contains errors list
    assert "errors" in data["detail"]
    assert any("requires an API key" in e for e in data["detail"]["errors"])
    # readiness flags present
    assert data["detail"]["provider_requires_key"] is True
    assert data["detail"]["provider_has_key"] is False
    assert data["detail"]["ai_provider_ready"] is False


def test_validate_env_key_ok(monkeypatch):
    # Provide env key
    monkeypatch.setenv("OPENAI_API_KEY", "sk-" + "x" * 22)
    payload = {
        "enable_ai": True,
        "ai_provider": "openai",
    }
    resp = client.post("/settings/validate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is True
    assert data["provider_requires_key"] is True
    assert data["provider_has_key"] is True
    assert data["ai_provider_ready"] is True


def test_validate_bad_key_format(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    payload = {
        "enable_ai": True,
        "ai_provider": "anthropic",
        "api_keys": {"anthropic": "notvalid"}
    }
    resp = client.post("/settings/validate", json=payload)
    assert resp.status_code == 400
    data = resp.json()
    assert "errors" in data["detail"]
    assert any("Invalid API key format" in e for e in data["detail"]["errors"])


def test_validate_local_provider_needs_no_key(monkeypatch):
    payload = {
        "enable_ai": True,
        "ai_provider": "local"
    }
    resp = client.post("/settings/validate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is True
    assert data["provider_requires_key"] is False
    assert data["ai_provider_ready"] is True
