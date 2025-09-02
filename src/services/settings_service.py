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
import os


DEFAULT_SETTINGS_PATH = Path("config/user_settings.json")
ALLOWED_AI_PROVIDERS = {"openai", "anthropic", "openrouter", "local", "none"}


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
    rate_limit_window_seconds: int = 60
    monthly_cost_cap_usd: float = 10.0
    hint_budget_per_session: int = 5
    review_budget_per_session: int = 0
    elaborate_budget_per_session: int = 0
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
                rate_limit_window_seconds=raw.get("rate_limit_window_seconds", 60),
                monthly_cost_cap_usd=raw.get("monthly_cost_cap_usd", 10.0),
                hint_budget_per_session=raw.get("hint_budget_per_session", 5),
                review_budget_per_session=raw.get("review_budget_per_session", 0),
                elaborate_budget_per_session=raw.get("elaborate_budget_per_session", 0),
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
        # Merge environment-provided keys (do not persist to disk)
        merged_keys: Dict[str, str] = {}
        if s.api_keys:
            merged_keys.update(s.api_keys)
        for provider, key in self._env_api_keys().items():
            if provider not in merged_keys or not merged_keys.get(provider):
                merged_keys[provider] = key
        # Mask API keys
        masked = {}
        for provider, key in (merged_keys or {}).items():
            if not key:
                masked[provider] = None
            else:
                # Keep last 4 characters for identification
                masked[provider] = ("*" * max(0, len(key) - 4)) + key[-4:]
        data["api_keys"] = masked
        return data

    def get_effective(self, settings: Optional[Settings] = None) -> Dict[str, Any]:
        """Return effective settings without exposing secrets.
        Includes api_keys_present booleans and provider readiness flags.
        """
        s = settings or self.load()
        effective = asdict(s)

        # Merge settings and environment API keys (do not persist env keys)
        merged_keys: Dict[str, str] = {}
        if s.api_keys:
            merged_keys.update(s.api_keys)
        for k, v in self._env_api_keys().items():
            if v and not merged_keys.get(k):
                merged_keys[k] = v

        # Replace api_keys with presence booleans
        # Include all known key-based providers (exclude 'local' and 'none') with default False
        presence = {}
        for prov in sorted(ALLOWED_AI_PROVIDERS - {"local", "none"}):
            presence[prov] = bool(merged_keys.get(prov))
        effective["api_keys_present"] = presence

        # Readiness flags
        provider = s.ai_provider
        requires_key = provider not in {"local", "none", None}
        has_key = bool(merged_keys.get(provider)) if provider else False
        effective["provider_requires_key"] = requires_key
        effective["provider_has_key"] = has_key
        effective["ai_provider_ready"] = (not s.enable_ai) or (not requires_key) or has_key
        effective["rate_limit_window_seconds"] = s.rate_limit_window_seconds

        # Feature flags for Redis-backed rate limiting
        use_redis = os.getenv("DSATRAIN_USE_REDIS_RATE_LIMIT", "0") in ("1", "true", "True")
        effective["use_redis_rate_limit"] = use_redis
        effective["redis_url_present"] = bool(os.getenv("DSATRAIN_REDIS_URL"))

        # Remove raw api_keys from the effective payload to avoid confusion
        effective.pop("api_keys", None)
        return effective

    def validate_only(self, patch: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a settings patch without persisting.
        Returns a result dict with validity, any errors, and readiness flags.
        """
        errors = []
        # Start from current settings but do not persist
        current = self.load()
        candidate = Settings(**asdict(current))
        # Normalize nested dataclasses that were converted to dicts by asdict
        if isinstance(getattr(candidate, "cognitive_profile", None), dict):
            try:
                candidate.cognitive_profile = CognitiveProfile(**candidate.cognitive_profile)  # type: ignore[arg-type]
            except Exception:
                # Fall back to empty profile if structure is unexpected
                candidate.cognitive_profile = CognitiveProfile()
        # For validation, ignore any previously persisted API keys; only consider payload and env
        candidate.api_keys = {}

        # Only allow specific fields to be updated (mirror update())
        allowed_fields = {
            "enable_ai",
            "ai_provider",
            "model",
            "api_keys",
            "rate_limit_per_minute",
            "rate_limit_window_seconds",
            "monthly_cost_cap_usd",
            "hint_budget_per_session",
            "review_budget_per_session",
            "elaborate_budget_per_session",
            "cognitive_profile",
        }
        patch = {k: v for k, v in (patch or {}).items() if k in allowed_fields}

        # Update simple fields with validation
        if "ai_provider" in patch and patch["ai_provider"] is not None:
            if patch["ai_provider"] not in ALLOWED_AI_PROVIDERS:
                errors.append(
                    f"Invalid ai_provider '{patch['ai_provider']}'. Allowed: {sorted(ALLOWED_AI_PROVIDERS)}"
                )
            else:
                candidate.ai_provider = patch["ai_provider"]
        for key in [
            "enable_ai",
            "model",
            "rate_limit_per_minute",
            "rate_limit_window_seconds",
            "monthly_cost_cap_usd",
            "hint_budget_per_session",
            "review_budget_per_session",
            "elaborate_budget_per_session",
        ]:
            if key in patch:
                setattr(candidate, key, patch[key])

        # Update api keys (non-persisting)
        if "api_keys" in patch:
            incoming = patch["api_keys"]
            if incoming is None:
                pass
            elif isinstance(incoming, dict):
                # Start from a copy
                candidate.api_keys = dict(candidate.api_keys or {})
                for provider, key in incoming.items():
                    if key is None:
                        candidate.api_keys.pop(provider, None)
                    else:
                        if not self._validate_api_key_format(provider, key):
                            errors.append(f"Invalid API key format for provider '{provider}'")
                        else:
                            candidate.api_keys[provider] = key
            else:
                errors.append("api_keys must be a mapping of provider->key or null")

        # Apply cognitive profile
        if "cognitive_profile" in patch and isinstance(patch["cognitive_profile"], dict):
            cp = patch["cognitive_profile"]
            candidate.cognitive_profile = CognitiveProfile(
                working_memory_capacity=cp.get("working_memory_capacity", getattr(candidate.cognitive_profile, "working_memory_capacity", None)),
                learning_style_preference=cp.get("learning_style_preference", getattr(candidate.cognitive_profile, "learning_style_preference", None)),
                visual_vs_verbal=cp.get("visual_vs_verbal", getattr(candidate.cognitive_profile, "visual_vs_verbal", None)),
                processing_speed=cp.get("processing_speed", getattr(candidate.cognitive_profile, "processing_speed", None)),
            )

        # Compute readiness against env+candidate keys
        effective_view = self.get_effective(candidate)
        provider_requires_key = effective_view.get("provider_requires_key", False)
        provider_has_key = effective_view.get("provider_has_key", False)
        ai_provider_ready = effective_view.get("ai_provider_ready", False)

        # Heuristic provider/model compatibility
        model = candidate.model or ""
        prov = (candidate.ai_provider or "none").lower()
        if model.startswith("ollama/") and prov != "local":
            errors.append("Models with prefix 'ollama/' are only supported with provider 'local'.")

        # Enforce that if AI is enabled and provider requires a key, we have a key
        if candidate.enable_ai and provider_requires_key and not provider_has_key:
            errors.append(
                f"AI provider '{candidate.ai_provider}' requires an API key. Provide via environment variable "
                f"or settings.api_keys.{candidate.ai_provider}."
            )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "provider_requires_key": provider_requires_key,
            "provider_has_key": provider_has_key,
            "ai_provider_ready": ai_provider_ready,
            "api_keys_present": effective_view.get("api_keys_present", {}),
        }

    def update(self, patch: Dict[str, Any], validate_keys: bool = True) -> Settings:
        current = self.load()

        # Only allow specific fields to be updated
        allowed_fields = {
            "enable_ai",
            "ai_provider",
            "model",
            "api_keys",
            "rate_limit_per_minute",
            "rate_limit_window_seconds",
            "monthly_cost_cap_usd",
            "hint_budget_per_session",
            "review_budget_per_session",
            "elaborate_budget_per_session",
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
            "rate_limit_window_seconds",
            "monthly_cost_cap_usd",
            "hint_budget_per_session",
            "review_budget_per_session",
            "elaborate_budget_per_session",
        ]:
            if key in patch:
                if key == "ai_provider" and patch[key] is not None:
                    if patch[key] not in ALLOWED_AI_PROVIDERS:
                        raise ValueError(f"Invalid ai_provider '{patch[key]}'. Allowed: {sorted(ALLOWED_AI_PROVIDERS)}")
                setattr(current, key, patch[key])

    # Update api keys
        if "api_keys" in patch:
            incoming = patch["api_keys"]
            if incoming is None:
                # No change when explicit None is provided for the whole dict
                pass
            elif isinstance(incoming, dict):
                for provider, key in incoming.items():
                    if key is None:
                        # Allow clearing a key
                        current.api_keys.pop(provider, None)
                    else:
                        if validate_keys and not self._validate_api_key_format(provider, key):
                            raise ValueError(f"Invalid API key format for provider '{provider}'")
                        current.api_keys[provider] = key
            else:
                raise ValueError("api_keys must be a mapping of provider->key or null")

        # Update cognitive profile
        if "cognitive_profile" in patch and isinstance(patch["cognitive_profile"], dict):
            cp = patch["cognitive_profile"]
            current.cognitive_profile = CognitiveProfile(
                working_memory_capacity=cp.get("working_memory_capacity", current.cognitive_profile.working_memory_capacity),
                learning_style_preference=cp.get("learning_style_preference", current.cognitive_profile.learning_style_preference),
                visual_vs_verbal=cp.get("visual_vs_verbal", current.cognitive_profile.visual_vs_verbal),
                processing_speed=cp.get("processing_speed", current.cognitive_profile.processing_speed),
            )

        # Heuristic provider/model compatibility at update time
        if (current.model or "").startswith("ollama/") and (current.ai_provider or "none").lower() != "local":
            raise ValueError("Models with prefix 'ollama/' are only supported with provider 'local'.")

        # Enforce key presence if AI is enabled and provider requires external key
        if current.enable_ai and (current.ai_provider not in {"local", "none", None}):
            merged_keys: Dict[str, str] = {}
            if current.api_keys:
                merged_keys.update(current.api_keys)
            env_keys = self._env_api_keys()
            for prov, val in env_keys.items():
                if prov not in merged_keys or not merged_keys.get(prov):
                    merged_keys[prov] = val
            effective_has_key = bool(merged_keys.get(current.ai_provider))
            if not effective_has_key:
                raise ValueError(
                    f"AI provider '{current.ai_provider}' requires an API key. Provide via environment variable "
                    f"or settings.api_keys.{current.ai_provider}."
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

    def _env_api_keys(self) -> Dict[str, str]:
        """Read API keys from environment variables without persisting them.
        Supported env vars: OPENAI_API_KEY, ANTHROPIC_API_KEY, OPENROUTER_API_KEY
        Provider mapping: openai, anthropic, openrouter
        """
        env_map = {
            "openai": os.getenv("OPENAI_API_KEY"),
            "anthropic": os.getenv("ANTHROPIC_API_KEY"),
            "openrouter": os.getenv("OPENROUTER_API_KEY"),
        }
        # Filter out empty/None
        return {k: v for k, v in env_map.items() if v}
