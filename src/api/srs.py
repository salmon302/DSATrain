from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from src.models.database import DatabaseConfig, Problem, ReviewCard
from src.services.srs_service import SRSService

router = APIRouter(prefix="/srs", tags=["SRS"])

db_config = DatabaseConfig()

def get_db():
    db = db_config.get_session()
    try:
        yield db
    finally:
        db.close()


class ReviewRequest(BaseModel):
    problem_id: str
    outcome: str = Field(..., pattern="^(again|hard|good|easy)$")


class RetrievalLog(BaseModel):
    problem_id: str
    retrieval_type: str
    success_rate: float = Field(..., ge=0.0, le=1.0)
    retrieval_strength: float = Field(..., ge=0.0, le=1.0)


@router.get("/next")
async def get_next_cards(limit: int = Query(10, ge=1, le=50), deck: Optional[str] = None, db: Session = Depends(get_db)):
    try:
        service = SRSService(db)
        cards = service.get_due_cards(limit=limit, deck=deck)
        return {
            'count': len(cards),
            'cards': [
                {
                    'id': c.id,
                    'problem_id': c.problem_id,
                    'next_review_at': c.next_review_at.isoformat() if c.next_review_at else None,
                    'interval_days': c.interval_days,
                    'ease': c.ease,
                    'reps': c.reps,
                    'lapses': c.lapses,
                    'last_outcome': c.last_outcome,
                    'deck': c.deck,
                } for c in cards
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/review")
async def submit_review(payload: ReviewRequest, db: Session = Depends(get_db)):
    try:
        # Ensure problem exists for FK integrity
        problem = db.query(Problem).filter(Problem.id == payload.problem_id).first()
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")

        service = SRSService(db)
        result = service.review(problem_id=payload.problem_id, outcome=payload.outcome)
        return result
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def srs_stats(db: Session = Depends(get_db)):
    try:
        service = SRSService(db)
        return service.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def srs_metrics(days: int = 7, db: Session = Depends(get_db)):
    try:
        service = SRSService(db)
        return service.metrics(days=days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/retrieval-practice")
async def log_retrieval(payload: RetrievalLog, db: Session = Depends(get_db)):
    try:
        # Ensure problem exists
        problem = db.query(Problem).filter(Problem.id == payload.problem_id).first()
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")

        service = SRSService(db)
        return service.log_retrieval(
            problem_id=payload.problem_id,
            retrieval_type=payload.retrieval_type,
            success_rate=payload.success_rate,
            retrieval_strength=payload.retrieval_strength,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
