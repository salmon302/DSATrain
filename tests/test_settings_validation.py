import pytest
from pathlib import Path

from src.services.settings_service import SettingsService, Settings


def test_ai_provider_validation(tmp_path: Path):
    svc = SettingsService(settings_path=tmp_path / 'user_settings.json')
    svc.save(Settings())

    # Valid providers
    for p in ["openai", "anthropic", "openrouter", "local", "none"]:
        updated = svc.update({"ai_provider": p})
        assert updated.ai_provider == p

    # Invalid provider
    with pytest.raises(ValueError):
        svc.update({"ai_provider": "bad-provider"})


essage = None

def test_api_keys_clear_and_type_guard(tmp_path: Path):
    svc = SettingsService(settings_path=tmp_path / 'user_settings.json')
    svc.save(Settings())

    # Set a key
    updated = svc.update({"api_keys": {"openai": "sk-12345678901234567890"}}, validate_keys=False)
    assert updated.api_keys.get("openai")

    # Clear the key by setting None
    updated2 = svc.update({"api_keys": {"openai": None}})
    assert "openai" not in updated2.api_keys

    # Type guard: api_keys must be dict or None
    with pytest.raises(ValueError):
        svc.update({"api_keys": "not-a-dict"})
