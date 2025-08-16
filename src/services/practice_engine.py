"""
PracticeEngine: Session generation, attempt logging, elaborative interrogation, and working-memory checks.
"""
from __future__ import annotations

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from src.models.database import Problem, ProblemAttempt, ElaborativeSession, UserCognitiveProfile


class PracticeEngine:
    def __init__(self, db: Session):
        self.db = db

    def generate_session(
        self,
        size: int = 5,
        difficulty: Optional[str] = None,
        focus_areas: Optional[List[str]] = None,
        interleaving: bool = True,
    ) -> Dict[str, Any]:
        query = self.db.query(Problem)
        if difficulty:
            query = query.filter(Problem.difficulty == difficulty)
        if focus_areas:
            # any tag match
            for tag in focus_areas:
                query = query.filter(Problem.algorithm_tags.contains([tag]))
        problems = query.order_by(
            Problem.quality_score.desc(), Problem.google_interview_relevance.desc()
        ).limit(size).all()
        return {
            "count": len(problems),
            "interleaving": interleaving,
            "problems": [p.to_dict() for p in problems],
        }

    def save_attempt(
        self,
        problem_id: str,
        status: str,
        time_spent: int,
        code: Optional[str] = None,
        language: Optional[str] = None,
        reflection: Optional[str] = None,
        test_results: Optional[Dict[str, Any]] = None,
        mistakes: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        attempt = ProblemAttempt(
            problem_id=problem_id,
            code=code,
            language=language,
            status=status,
            time_spent=time_spent,
            test_results=test_results,
            mistakes=mistakes,
            reflection=reflection,
        )
        self.db.add(attempt)
        self.db.commit()
        return {
            "id": attempt.id,
            "problem_id": attempt.problem_id,
            "status": attempt.status,
            "time_spent": attempt.time_spent,
            "created_at": attempt.created_at.isoformat() if attempt.created_at else None,
        }

    def create_elaborative_session(
        self,
        problem_id: str,
        why_questions: Optional[List[str]] = None,
        how_questions: Optional[List[str]] = None,
        responses: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        session = ElaborativeSession(
            problem_id=problem_id,
            why_questions=why_questions,
            how_questions=how_questions,
            responses=responses,
        )
        self.db.add(session)
        self.db.commit()
        return {
            "id": session.id,
            "problem_id": session.problem_id,
            "timestamp": session.timestamp.isoformat() if session.timestamp else None,
        }

    def assess_working_memory(self, metrics: Dict[str, Any], user_id: str = "default_user") -> Dict[str, Any]:
        """
        Simple heuristic assessment.
        Inputs (optional): mistakes_count, time_overrun, hints_used, cognitive_load_self_report (0-10)
        Output: load_score (0..1) and basic recommendations.
        """
        mistakes = int(metrics.get("mistakes_count", 0) or 0)
        overrun = float(metrics.get("time_overrun", 0.0) or 0.0)  # fraction over target (e.g., 0.2 => 20%)
        hints = int(metrics.get("hints_used", 0) or 0)
        self_report = metrics.get("cognitive_load_self_report")
        if self_report is None:
            self_report = 5
        try:
            self_report = float(self_report)
        except Exception:
            self_report = 5.0
        self_report = max(0.0, min(10.0, self_report))

        # Normalize contributors roughly to 0..1 then average
        comp = [
            min(1.0, mistakes / 5.0),
            min(1.0, overrun),
            min(1.0, hints / 3.0),
            self_report / 10.0,
        ]
        load_score = sum(comp) / len(comp)

        recs: List[str] = []
        if load_score >= 0.7:
            recs.append("Break into subproblems and write pseudocode first.")
            recs.append("Switch to a simpler variant or review prerequisites.")
        elif load_score >= 0.4:
            recs.append("Use a checklist (e.g., DP states/recurrence/base cases).")
            recs.append("Try a related easier problem for interleaving.")
        else:
            recs.append("Proceed to implementation; set a timebox for productive struggle.")

        # Lightly update user cognitive profile
        profile = self.db.query(UserCognitiveProfile).filter(UserCognitiveProfile.user_id == user_id).first()
        if not profile:
            profile = UserCognitiveProfile(user_id=user_id)
            self.db.add(profile)
        # Map load score to processing speed hint
        if load_score >= 0.7:
            profile.processing_speed = "slow"
        elif load_score <= 0.3:
            profile.processing_speed = "fast"
        else:
            profile.processing_speed = "average"
        profile.updated_at = datetime.now()
        self.db.commit()

        return {
            "load_score": round(load_score, 2),
            "recommendations": recs,
            "updated_profile": {
                "user_id": profile.user_id,
                "processing_speed": profile.processing_speed,
            },
        }
