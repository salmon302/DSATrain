import os
import json
from pathlib import Path
from fastapi.testclient import TestClient

from src.api.main import app
from src.services.settings_service import SettingsService, Settings

client = TestClient(app)


def test_env_keys_are_merged_and_masked(tmp_path: Path, monkeypatch):
    # Prepare temp settings file without any api_keys
    tmp_settings = tmp_path / "user_settings.json"
    svc = SettingsService(settings_path=tmp_settings)
    svc.save(Settings())

    # Set environment variables for API keys
    monkeypatch.setenv("OPENAI_API_KEY", "sk-aaaaaaaaaaaaaaaaaaaa")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-abcdefghijklmnopqrstu")

    data = svc.get_masked()

    # Env keys should appear even if not in file, and be masked
    assert data["api_keys"]["openai"].endswith("aaaa")
    assert set(data["api_keys"]["openai"]) == set("*aaaa")

    assert data["api_keys"]["anthropic"].endswith("rstu")
    assert set(data["api_keys"]["anthropic"]) == set("*rstu")

    # No persistence of env keys: re-load raw file and ensure api_keys empty
    raw = json.loads(tmp_settings.read_text())
    assert raw.get("api_keys", {}) == {}
