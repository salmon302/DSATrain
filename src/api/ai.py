from fastapi import APIRouter, HTTPException, Depends, Response
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from src.models.database import DatabaseConfig, Problem
from src.services.ai_service import AIService, AIForbidden, AIRateLimited

router = APIRouter(prefix="/ai", tags=["AI"])

db_config = DatabaseConfig()

def get_db():
    db = db_config.get_session()
    try:
        yield db
    finally:
        db.close()


class HintRequest(BaseModel):
    problem_id: str
    query: Optional[str] = None
    session_id: Optional[str] = None


class ReviewRequest(BaseModel):
    code: str
    rubric: Optional[Dict[str, Any]] = None
    problem_id: Optional[str] = None


class ElaborateRequest(BaseModel):
    problem_id: str


def _rate_headers(svc: AIService, session_id: Optional[str] = None) -> Dict[str, str]:
    st = svc.get_status(session_id=session_id)
    limit = int(st.get("rate_limit_per_minute") or 0)
    used = int(st.get("rate_limit_used") or 0)
    remaining = max(0, limit - used) if limit > 0 else 0
    reset = st.get("rate_limit_reset_seconds")
    headers = {
        "X-RateLimit-Limit": str(limit),
        "X-RateLimit-Remaining": str(remaining),
    }
    if reset is not None:
        headers["X-RateLimit-Reset"] = str(reset)
    return headers


@router.post("/hint")
async def get_hint(payload: HintRequest, db: Session = Depends(get_db), response: Response = None):
    try:
        # Validate problem exists
        if not db.query(Problem).filter(Problem.id == payload.problem_id).first():
            raise HTTPException(status_code=404, detail="Problem not found")
        svc = AIService(db)
        data = svc.generate_hint(problem_id=payload.problem_id, query=payload.query, session_id=payload.session_id)
        if response is not None:
            response.headers.update(_rate_headers(svc, payload.session_id))
        return data
    except AIForbidden as fe:
        raise HTTPException(status_code=403, detail=str(fe))
    except AIRateLimited as rl:
        # Map internal permission errors (rate limit / budget) to 429 Too Many Requests
        svc = AIService(db)
        headers = _rate_headers(svc, payload.session_id)
        if getattr(rl, "retry_after_seconds", None):
            headers["Retry-After"] = str(rl.retry_after_seconds)
        raise HTTPException(status_code=429, detail=str(rl), headers=headers)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/review")
async def review_code(payload: ReviewRequest, db: Session = Depends(get_db), response: Response = None):
    try:
        svc = AIService(db)
        data = svc.review_code(code=payload.code, rubric=payload.rubric, problem_id=payload.problem_id)
        if response is not None:
            response.headers.update(_rate_headers(svc))
        return data
    except AIForbidden as fe:
        raise HTTPException(status_code=403, detail=str(fe))
    except AIRateLimited as rl:
        svc = AIService(db)
        headers = _rate_headers(svc)
        if getattr(rl, "retry_after_seconds", None):
            headers["Retry-After"] = str(rl.retry_after_seconds)
        raise HTTPException(status_code=429, detail=str(rl), headers=headers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/elaborate")
async def elaborate(payload: ElaborateRequest, db: Session = Depends(get_db), response: Response = None):
    try:
        # Validate problem exists
        if not db.query(Problem).filter(Problem.id == payload.problem_id).first():
            raise HTTPException(status_code=404, detail="Problem not found")
        svc = AIService(db)
        data = svc.elaborate_prompts(problem_id=payload.problem_id)
        if response is not None:
            response.headers.update(_rate_headers(svc))
        return data
    except AIForbidden as fe:
        raise HTTPException(status_code=403, detail=str(fe))
    except AIRateLimited as rl:
        svc = AIService(db)
        headers = _rate_headers(svc)
        if getattr(rl, "retry_after_seconds", None):
            headers["Retry-After"] = str(rl.retry_after_seconds)
        raise HTTPException(status_code=429, detail=str(rl), headers=headers)


@router.get("/status")
async def get_ai_status(session_id: Optional[str] = None, db: Session = Depends(get_db)):
    """Return current AI enablement, provider/model, rate limit usage, and per-session hint usage.
    Use session_id to retrieve your current hint usage.
    """
    try:
        svc = AIService(db)
        return svc.get_status(session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ResetRequest(BaseModel):
    session_id: Optional[str] = None
    reset_global: bool = True


@router.post("/reset")
async def reset_ai(payload: ResetRequest, db: Session = Depends(get_db)):
    """Reset AI in-memory counters.
    - If session_id is provided, clears that session's hint usage.
    - If reset_global is true (default), clears the global rate limiter bucket.
    Returns the current status after reset.
    """
    try:
        svc = AIService(db)
        status = svc.reset(session_id=payload.session_id, reset_global=payload.reset_global)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
