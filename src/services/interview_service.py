"""
InterviewService: Timed coding session scaffolding and rubric scoring (lightweight heuristics).
"""
from __future__ import annotations

from typing import Optional, Dict, Any
from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from src.models.database import Problem


class InterviewService:
    def __init__(self, db: Session):
        self.db = db

    def start_coding_session(self, problem_id: str, duration_minutes: int = 30, constraints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        problem = self.db.query(Problem).filter(Problem.id == problem_id).first()
        if not problem:
            raise ValueError("Problem not found")
        session_id = f"coding_{uuid4()}"
        return {
            "session_id": session_id,
            "problem": problem.to_dict(),
            "duration_minutes": duration_minutes,
            "constraints": constraints or {"no_ide": True, "require_tests": True},
            "started_at": datetime.now().isoformat(),
        }

    def submit_coding_session(self, session_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stateless scoring heuristic based on provided evidence:
        Inputs can include: code, tests_count, passed_tests, reasoning_notes, time_spent_minutes.
        Outputs rubric keys: algorithms_dsa, coding, communication, problem_solving (1..4).
        """
        # Basic defaults
        code = payload.get("code", "") or ""
        tests = int(payload.get("tests_count", 0) or 0)
        passed = int(payload.get("passed_tests", 0) or 0)
        notes = (payload.get("reasoning_notes") or "").lower()
        time_spent = float(payload.get("time_spent_minutes", 0) or 0)

        # Heuristic scoring
        coding = 1
        if len(code) > 50:
            coding = 2
        if tests > 0 and passed == tests and len(code) > 100:
            coding = 3
        if tests >= 3 and passed == tests and len(code) > 200:
            coding = 4

        algorithms = 2 if any(k in notes for k in ["complexity", "invariant", "recurrence", "big o"]) else 1
        if any(k in notes for k in ["tradeoff", "optimal", "space-time"]):
            algorithms = max(algorithms, 3)
        if any(k in notes for k in ["proof", "correctness", "invariant hold"]):
            algorithms = max(algorithms, 4)

        communication = 2 if any(k in notes for k in ["clarify", "plan", "edge case"]) else 1
        if any(k in notes for k in ["explain", "walkthrough", "examples"]):
            communication = max(communication, 3)
        if any(k in notes for k in ["structure", "verbalize", "summarize"]):
            communication = max(communication, 4)

        problem_solving = 2 if any(k in notes for k in ["brute", "optimize", "refactor"]) else 1
        if any(k in notes for k in ["pattern", "dp", "graph", "invariant"]):
            problem_solving = max(problem_solving, 3)
        if any(k in notes for k in ["decompose", "subproblem", "abstraction"]):
            problem_solving = max(problem_solving, 4)

        # Time handling: minor penalty or bonus
        if time_spent and time_spent > 45:
            communication = max(1, communication - 1)
        if time_spent and time_spent < 20 and coding >= 3:
            problem_solving = min(4, problem_solving + 1)

        summary = []
        if coding >= 3 and passed == tests and tests > 0:
            summary.append("Robust solution with tests passing.")
        if algorithms >= 3:
            summary.append("Good algorithmic reasoning and trade-off discussion.")
        if communication >= 3:
            summary.append("Clear communication and structure.")
        if problem_solving >= 3:
            summary.append("Strong problem-solving approach and pattern recognition.")
        if not summary:
            summary.append("Provide more reasoning notes and add tests for stronger evidence.")

        return {
            "session_id": session_id,
            "rubric": {
                "algorithms_dsa": algorithms,
                "coding": coding,
                "communication": communication,
                "problem_solving": problem_solving,
            },
            "summary": summary,
        }
