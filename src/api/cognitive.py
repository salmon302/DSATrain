from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from src.models.database import DatabaseConfig
from src.services.cognitive_service import CognitiveService

router = APIRouter(prefix="/cognitive", tags=["Cognitive"])

db_config = DatabaseConfig()

def get_db():
    db = db_config.get_session()
    try:
        yield db
    finally:
        db.close()


class AssessmentPayload(BaseModel):
    user_id: Optional[str] = "default_user"
    working_memory_quiz: Optional[float] = None
    style_preference: Optional[str] = None  # visual|verbal|balanced
    visual_vs_verbal: Optional[float] = None
    processing_speed_hint: Optional[str] = None


@router.get("/profile")
async def get_profile(user_id: str = Query("default_user"), db: Session = Depends(get_db)):
    try:
        service = CognitiveService(db)
        return service.get_profile(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assess")
async def assess_profile(payload: AssessmentPayload, db: Session = Depends(get_db)):
    try:
        service = CognitiveService(db)
        return service.assess(data=payload.model_dump(exclude_unset=True), user_id=payload.user_id or "default_user")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/adaptation")
async def get_adaptation(user_id: str = Query("default_user"), db: Session = Depends(get_db)):
    try:
        service = CognitiveService(db)
        return service.get_adaptation(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
