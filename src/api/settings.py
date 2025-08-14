from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from src.services.settings_service import SettingsService

router = APIRouter(prefix="/settings", tags=["settings"])


class CognitiveProfileModel(BaseModel):
    working_memory_capacity: Optional[int] = Field(None, ge=1, le=10)
    learning_style_preference: Optional[str] = Field(None, description="visual | verbal | balanced")
    visual_vs_verbal: Optional[float] = Field(None, ge=0.0, le=1.0)
    processing_speed: Optional[str] = Field(None, description="slow | average | fast")


class SettingsUpdateModel(BaseModel):
    enable_ai: Optional[bool] = None
    ai_provider: Optional[str] = Field(None, description="openai | anthropic | openrouter | local | none")
    model: Optional[str] = None
    api_keys: Optional[Dict[str, Optional[str]]] = None
    rate_limit_per_minute: Optional[int] = Field(None, ge=1, le=120)
    monthly_cost_cap_usd: Optional[float] = Field(None, ge=0.0, le=1000.0)
    hint_budget_per_session: Optional[int] = Field(None, ge=0, le=100)
    cognitive_profile: Optional[CognitiveProfileModel] = None


_service = SettingsService()


@router.get("")
async def get_settings() -> Dict[str, Any]:
    try:
        return _service.get_masked()
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
