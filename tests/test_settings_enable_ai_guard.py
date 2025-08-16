import pytest
from pathlib import Path

from src.services.settings_service import SettingsService, Settings


def test_enable_ai_requires_key(tmp_path: Path, monkeypatch):
    svc = SettingsService(settings_path=tmp_path / 'user_settings.json')
    svc.save(Settings())

    # Enabling AI with provider that requires keys without env or file should fail
    with pytest.raises(ValueError):
        svc.update({"enable_ai": True, "ai_provider": "openai"}, validate_keys=False)

    # With env key present, should pass
    monkeypatch.setenv("OPENAI_API_KEY", "sk-aaaaaaaaaaaaaaaaaaaa")
    updated = svc.update({"enable_ai": True, "ai_provider": "openai"}, validate_keys=False)
    assert updated.enable_ai is True and updated.ai_provider == "openai"

    # Also acceptable: set key via api_keys
    updated2 = svc.update({"api_keys": {"openai": "sk-12345678901234567890"}}, validate_keys=False)
    assert updated2.api_keys.get("openai")


def test_enable_ai_local_or_none(tmp_path: Path):
    svc = SettingsService(settings_path=tmp_path / 'user_settings.json')
    svc.save(Settings())

    # Local and none don't require keys
    updated_local = svc.update({"enable_ai": True, "ai_provider": "local"})
    assert updated_local.enable_ai and updated_local.ai_provider == "local"

    updated_none = svc.update({"enable_ai": True, "ai_provider": "none"})
    assert updated_none.enable_ai and updated_none.ai_provider == "none"
