from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from src.models.database import DatabaseConfig, Problem
from src.models.database import PracticeGateSession
from src.services.practice_engine import PracticeEngine
from src.services.gated_practice import GatedPractice

router = APIRouter(prefix="/practice", tags=["Practice"])

db_config = DatabaseConfig()

def get_db():
    db = db_config.get_session()
    try:
        yield db
    finally:
        db.close()


class SessionRequest(BaseModel):
    size: int = Field(5, ge=1, le=50)
    difficulty: Optional[str] = None
    focus_areas: Optional[List[str]] = None
    interleaving: bool = True


class AttemptRequest(BaseModel):
    problem_id: str
    status: str = Field(..., description="solved | attempted | failed")
    time_spent: int = Field(..., ge=0)
    code: Optional[str] = None
    language: Optional[str] = None
    reflection: Optional[str] = None
    test_results: Optional[Dict[str, Any]] = None
    mistakes: Optional[List[str]] = None


class ElaborativeRequest(BaseModel):
    problem_id: str
    why_questions: Optional[List[str]] = None
    how_questions: Optional[List[str]] = None
    responses: Optional[Dict[str, Any]] = None


@router.post("/session")
async def generate_session(payload: SessionRequest, db: Session = Depends(get_db)):
    try:
        engine = PracticeEngine(db)
        return engine.generate_session(
            size=payload.size,
            difficulty=payload.difficulty,
            focus_areas=payload.focus_areas,
            interleaving=payload.interleaving,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/attempt")
async def log_attempt(payload: AttemptRequest, db: Session = Depends(get_db)):
    try:
        # Validate problem exists
        prob = db.query(Problem).filter(Problem.id == payload.problem_id).first()
        if not prob:
            raise HTTPException(status_code=404, detail="Problem not found")
        engine = PracticeEngine(db)
        return engine.save_attempt(
            problem_id=payload.problem_id,
            status=payload.status,
            time_spent=payload.time_spent,
            code=payload.code,
            language=payload.language,
            reflection=payload.reflection,
            test_results=payload.test_results,
            mistakes=payload.mistakes,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/elaborative")
async def log_elaborative(payload: ElaborativeRequest, db: Session = Depends(get_db)):
    try:
        # Validate problem exists
        prob = db.query(Problem).filter(Problem.id == payload.problem_id).first()
        if not prob:
            raise HTTPException(status_code=404, detail="Problem not found")
        engine = PracticeEngine(db)
        return engine.create_elaborative_session(
            problem_id=payload.problem_id,
            why_questions=payload.why_questions,
            how_questions=payload.how_questions,
            responses=payload.responses,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class WorkingMemoryMetrics(BaseModel):
    metrics: Dict[str, Any]
    user_id: Optional[str] = "default_user"


@router.post("/working-memory-check")
async def working_memory_check(payload: WorkingMemoryMetrics, db: Session = Depends(get_db)):
    try:
        engine = PracticeEngine(db)
        return engine.assess_working_memory(metrics=payload.metrics, user_id=payload.user_id or "default_user")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- Gated practice endpoints ----
class GatesStart(BaseModel):
    problem_id: str
    session_id: Optional[str] = None


class GatesProgress(BaseModel):
    session_id: str
    gate: str
    value: bool = True


@router.post("/gates/start")
async def gates_start(payload: GatesStart, db: Session = Depends(get_db)):
    try:
            gp = GatedPractice(db=db, user_id="default_user")
            return gp.start(problem_id=payload.problem_id, session_id=payload.session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gates/progress")
async def gates_progress(payload: GatesProgress, db: Session = Depends(get_db)):
    try:
            gp = GatedPractice(db=db, user_id="default_user")
            return gp.progress(session_id=payload.session_id, gate=payload.gate, value=payload.value)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gates/status")
async def gates_status(session_id: str, db: Session = Depends(get_db)):
    try:
            gp = GatedPractice(db=db, user_id="default_user")
            return gp.status(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gates")
async def list_gates(problem_id: Optional[str] = None, db: Session = Depends(get_db)):
    try:
        gp = GatedPractice(db=db, user_id="default_user")
        return gp.list(problem_id=problem_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gates/{session_id}")
async def get_gate(session_id: str, db: Session = Depends(get_db)):
    try:
        gp = GatedPractice(db=db, user_id="default_user")
        return gp.get(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/gates/{session_id}")
async def delete_gate(session_id: str, db: Session = Depends(get_db)):
    try:
        gp = GatedPractice(db=db, user_id="default_user")
        return gp.delete(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
