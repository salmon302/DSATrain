"""
SettingsService: Local-first settings management for single-user DSATrain.

Responsibilities:
- Load/save settings from config/user_settings.json
- Provide safe (masked) view of API keys
- Validate basic structure of settings and optionally validate provider API key (stub)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, Optional, Any


DEFAULT_SETTINGS_PATH = Path("config/user_settings.json")


@dataclass
class CognitiveProfile:
    working_memory_capacity: Optional[int] = None  # 1-10 rough scale
    learning_style_preference: Optional[str] = None  # visual | verbal | balanced
    visual_vs_verbal: Optional[float] = None  # 0.0 verbal .. 1.0 visual
    processing_speed: Optional[str] = None  # slow | average | fast


@dataclass
class Settings:
    enable_ai: bool = False
    ai_provider: str = "none"  # openai | anthropic | openrouter | local | none
    model: Optional[str] = None
    api_keys: Dict[str, str] = field(default_factory=dict)  # provider -> key
    rate_limit_per_minute: int = 30
    monthly_cost_cap_usd: float = 10.0
    hint_budget_per_session: int = 5
    cognitive_profile: CognitiveProfile = field(default_factory=CognitiveProfile)


class SettingsService:
    def __init__(self, settings_path: Path = DEFAULT_SETTINGS_PATH):
        self.settings_path = settings_path
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)

    def _default_settings(self) -> Settings:
        return Settings()

    def load(self) -> Settings:
        if not self.settings_path.exists():
            # Initialize with defaults
            settings = self._default_settings()
            self.save(settings)
            return settings
        try:
            raw = json.loads(self.settings_path.read_text(encoding="utf-8"))
            # Backward/forward compatible load
            cognitive = raw.get("cognitive_profile", {}) or {}
            settings = Settings(
                enable_ai=raw.get("enable_ai", False),
                ai_provider=raw.get("ai_provider", "none"),
                model=raw.get("model"),
                api_keys=raw.get("api_keys", {}) or {},
                rate_limit_per_minute=raw.get("rate_limit_per_minute", 30),
                monthly_cost_cap_usd=raw.get("monthly_cost_cap_usd", 10.0),
                hint_budget_per_session=raw.get("hint_budget_per_session", 5),
                cognitive_profile=CognitiveProfile(
                    working_memory_capacity=cognitive.get("working_memory_capacity"),
                    learning_style_preference=cognitive.get("learning_style_preference"),
                    visual_vs_verbal=cognitive.get("visual_vs_verbal"),
                    processing_speed=cognitive.get("processing_speed"),
                ),
            )
            return settings
        except Exception:
            # On any error, fall back to defaults (do not overwrite the file automatically)
            return self._default_settings()

    def save(self, settings: Settings) -> None:
        data = asdict(settings)
        self.settings_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def get_masked(self, settings: Optional[Settings] = None) -> Dict[str, Any]:
        s = settings or self.load()
        data = asdict(s)
        # Mask API keys
        masked = {}
        for provider, key in (s.api_keys or {}).items():
            if not key:
                masked[provider] = None
            else:
                # Keep last 4 characters for identification
                masked[provider] = ("*" * max(0, len(key) - 4)) + key[-4:]
        data["api_keys"] = masked
        return data

    def update(self, patch: Dict[str, Any], validate_keys: bool = True) -> Settings:
        current = self.load()

        # Only allow specific fields to be updated
        allowed_fields = {
            "enable_ai",
            "ai_provider",
            "model",
            "api_keys",
            "rate_limit_per_minute",
            "monthly_cost_cap_usd",
            "hint_budget_per_session",
            "cognitive_profile",
        }
        for k in list(patch.keys()):
            if k not in allowed_fields:
                patch.pop(k)

        # Update simple fields
        for key in [
            "enable_ai",
            "ai_provider",
            "model",
            "rate_limit_per_minute",
            "monthly_cost_cap_usd",
            "hint_budget_per_session",
        ]:
            if key in patch:
                setattr(current, key, patch[key])

        # Update api keys
        if "api_keys" in patch and isinstance(patch["api_keys"], dict):
            for provider, key in patch["api_keys"].items():
                if key is None:
                    # Allow clearing a key
                    current.api_keys.pop(provider, None)
                else:
                    if validate_keys and not self._validate_api_key_format(provider, key):
                        raise ValueError(f"Invalid API key format for provider '{provider}'")
                    current.api_keys[provider] = key

        # Update cognitive profile
        if "cognitive_profile" in patch and isinstance(patch["cognitive_profile"], dict):
            cp = patch["cognitive_profile"]
            current.cognitive_profile = CognitiveProfile(
                working_memory_capacity=cp.get("working_memory_capacity", current.cognitive_profile.working_memory_capacity),
                learning_style_preference=cp.get("learning_style_preference", current.cognitive_profile.learning_style_preference),
                visual_vs_verbal=cp.get("visual_vs_verbal", current.cognitive_profile.visual_vs_verbal),
                processing_speed=cp.get("processing_speed", current.cognitive_profile.processing_speed),
            )

        self.save(current)
        return current

    def update_cognitive_profile(self, profile: Dict[str, Any]) -> Settings:
        current = self.load()
        current.cognitive_profile = CognitiveProfile(
            working_memory_capacity=profile.get("working_memory_capacity"),
            learning_style_preference=profile.get("learning_style_preference"),
            visual_vs_verbal=profile.get("visual_vs_verbal"),
            processing_speed=profile.get("processing_speed"),
        )
        self.save(current)
        return current

    def _validate_api_key_format(self, provider: str, key: str) -> bool:
        # Lightweight validation without external calls
        if not key or not isinstance(key, str):
            return False
        # Basic heuristic checks per provider (non-exhaustive, safe)
        provider = (provider or "").lower()
        if provider == "openai":
            # Typically starts with 'sk-' and length > 20
            return key.startswith("sk-") and len(key) >= 20
        if provider == "anthropic":
            # Often 'sk-ant-' style
            return key.startswith("sk-ant-") and len(key) >= 24
        if provider == "openrouter":
            return len(key) >= 20
        if provider == "local" or provider == "none":
            return True
        # Default minimal length check
        return len(key) >= 16
