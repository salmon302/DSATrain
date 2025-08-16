from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from src.models.database import DatabaseConfig, Problem
from src.services.interview_service import InterviewService

router = APIRouter(prefix="/interview", tags=["Interview"])

db_config = DatabaseConfig()

def get_db():
    db = db_config.get_session()
    try:
        yield db
    finally:
        db.close()


class StartRequest(BaseModel):
    problem_id: str
    duration_minutes: int = Field(30, ge=10, le=120)
    constraints: Optional[Dict[str, Any]] = None


class SubmitRequest(BaseModel):
    session_id: str
    code: Optional[str] = None
    tests_count: Optional[int] = 0
    passed_tests: Optional[int] = 0
    reasoning_notes: Optional[str] = None
    time_spent_minutes: Optional[float] = 0


@router.post("/start")
async def start_interview(payload: StartRequest, db: Session = Depends(get_db)):
    try:
        # Validate problem exists
        prob = db.query(Problem).filter(Problem.id == payload.problem_id).first()
        if not prob:
            raise HTTPException(status_code=404, detail="Problem not found")
        svc = InterviewService(db)
        return svc.start_coding_session(
            problem_id=payload.problem_id,
            duration_minutes=payload.duration_minutes,
            constraints=payload.constraints,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/complete")
async def complete_interview(payload: SubmitRequest, db: Session = Depends(get_db)):
    try:
        svc = InterviewService(db)
        return svc.submit_coding_session(payload.session_id, payload.model_dump(exclude_unset=True))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
