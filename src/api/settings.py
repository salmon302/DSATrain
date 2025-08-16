from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal

from src.services.settings_service import SettingsService, ALLOWED_AI_PROVIDERS
from src.api.error_handlers import ValidationAPIError, format_validation_error_response

router = APIRouter(prefix="/settings", tags=["settings"])


class CognitiveProfileModel(BaseModel):
    working_memory_capacity: Optional[int] = Field(None, ge=1, le=10)
    learning_style_preference: Optional[str] = Field(None, description="visual | verbal | balanced")
    visual_vs_verbal: Optional[float] = Field(None, ge=0.0, le=1.0)
    processing_speed: Optional[str] = Field(None, description="slow | average | fast")


class SettingsUpdateModel(BaseModel):
    enable_ai: Optional[bool] = None
    ai_provider: Optional[Literal["openai","anthropic","openrouter","local","none"]] = Field(
        None, description="openai | anthropic | openrouter | local | none"
    )
    model: Optional[str] = None
    api_keys: Optional[Dict[str, Optional[str]]] = None
    rate_limit_per_minute: Optional[int] = Field(None, ge=1, le=120)
    rate_limit_window_seconds: Optional[int] = Field(None, ge=10, le=3600)
    monthly_cost_cap_usd: Optional[float] = Field(None, ge=0.0, le=1000.0)
    hint_budget_per_session: Optional[int] = Field(None, ge=0, le=100)
    cognitive_profile: Optional[CognitiveProfileModel] = None


_service = SettingsService()

# Static suggested models per provider for UI selects (non-authoritative)
SUGGESTED_MODELS: Dict[str, list[str]] = {
    "openai": [
        "gpt-4o-mini",
        "gpt-4o",
        "gpt-4.1-mini",
    ],
    "anthropic": [
        "claude-3-5-sonnet",
        "claude-3-haiku",
    ],
    "openrouter": [
        "meta-llama/llama-3.1-8b-instruct",
        "mistralai/mistral-7b-instruct",
        "google/gemini-flash-1.5",
    ],
    "local": [
        "ollama/llama3:8b-instruct",
        "ollama/qwen2:7b-instruct",
    ],
    "none": [],
}


@router.get("")
async def get_settings(
    include_providers: bool = Query(False, description="Include allowed providers list and notes"),
    include_effective_flags: bool = Query(False, description="Include api_keys_present flags like /settings/effective"),
) -> Dict[str, Any]:
    try:
        base = _service.get_masked()
        if include_providers:
            base["providers"] = {
                "allowed": sorted(ALLOWED_AI_PROVIDERS),
                "notes": {
                    "openai": "Requires OPENAI_API_KEY or settings.api_keys.openai",
                    "anthropic": "Requires ANTHROPIC_API_KEY or settings.api_keys.anthropic",
                    "openrouter": "Requires OPENROUTER_API_KEY or settings.api_keys.openrouter",
                    "local": "Runs without external API",
                    "none": "Disables AI features",
                },
            }
        if include_effective_flags:
            eff = _service.get_effective()
            base["api_keys_present"] = eff.get("api_keys_present", {})
            base["provider_requires_key"] = eff.get("provider_requires_key")
            base["provider_has_key"] = eff.get("provider_has_key")
            base["ai_provider_ready"] = eff.get("ai_provider_ready")
            # Also include effective_model (explicit model or first suggestion)
            provider = eff.get("ai_provider")
            model = eff.get("model")
            if model:
                base["effective_model"] = model
            else:
                suggestions = SUGGESTED_MODELS.get(provider or "", [])
                base["effective_model"] = suggestions[0] if suggestions else None
        return base
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("")
async def update_settings(payload: SettingsUpdateModel) -> Dict[str, Any]:
    try:
        updated = _service.update(payload.model_dump(exclude_unset=True))
        return _service.get_masked(updated)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cognitive-profile")
async def update_cognitive_profile(payload: CognitiveProfileModel) -> Dict[str, Any]:
    try:
        updated = _service.update_cognitive_profile(payload.model_dump(exclude_unset=True))
        return _service.get_masked(updated)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers")
async def get_allowed_providers() -> Dict[str, Any]:
    """Return allowed AI providers and basic notes for UI selection."""
    return {
        "allowed": sorted(ALLOWED_AI_PROVIDERS),
        "notes": {
            "openai": "Requires OPENAI_API_KEY or settings.api_keys.openai",
            "anthropic": "Requires ANTHROPIC_API_KEY or settings.api_keys.anthropic",
            "openrouter": "Requires OPENROUTER_API_KEY or settings.api_keys.openrouter",
            "local": "Runs without external API",
            "none": "Disables AI features",
        },
    }


@router.get("/effective")
async def get_effective_settings() -> Dict[str, Any]:
    """Return the effective settings: runtime view with api_keys_present flags (no secrets)."""
    try:
        eff = _service.get_effective()
        provider = eff.get("ai_provider")
        model = eff.get("model")
        if model:
            eff["effective_model"] = model
        else:
            suggestions = SUGGESTED_MODELS.get(provider or "", [])
            eff["effective_model"] = suggestions[0] if suggestions else None
        return eff
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate")
async def validate_settings(payload: SettingsUpdateModel) -> Dict[str, Any]:
    """Validate a settings payload for readiness without persisting changes."""
    try:
        result = _service.validate_only(payload.model_dump(exclude_unset=True))
        # Map validation errors to 400 if invalid to help the UI
        if not result.get("valid", False):
            errors = result.get("errors", [])
            meta = {k: v for k, v in result.items() if k not in ["errors", "valid"]}
            content = format_validation_error_response(
                message="Settings validation failed",
                errors=errors,
                meta=meta
            )
            # Flatten selected meta into detail for convenience per tests
            content.update({
                "provider_requires_key": meta.get("provider_requires_key"),
                "provider_has_key": meta.get("provider_has_key"),
                "ai_provider_ready": meta.get("ai_provider_ready"),
            })
            # Return a JSONResponse with top-level 'detail' to satisfy tests
            return JSONResponse(status_code=400, content={"detail": content})
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def get_models(provider: Optional[str] = Query(None, description="Optional provider filter")) -> Dict[str, Any]:
    """Return suggested model identifiers for supported providers.
    This list is static and intended for UI convenience; it's not authoritative.
    """
    try:
        if provider is not None:
            if provider not in ALLOWED_AI_PROVIDERS:
                raise HTTPException(status_code=400, detail=f"Invalid provider '{provider}'. Allowed: {sorted(ALLOWED_AI_PROVIDERS)}")
            return {"provider": provider, "models": SUGGESTED_MODELS.get(provider, [])}
        # full mapping
        return {"models": {p: SUGGESTED_MODELS.get(p, []) for p in sorted(ALLOWED_AI_PROVIDERS)}}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
