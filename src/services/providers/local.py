from __future__ import annotations

import time
from typing import Optional, Dict, Any, List

from src.models.database import Problem
from .base import ProviderBase, AIContext


class LocalProvider(ProviderBase):
    name = "local"

    def generate_hint(self, problem: Problem, query: Optional[str], ctx: AIContext) -> Dict[str, Any]:
        tags = problem.algorithm_tags or []
        conceptual = f"Identify the core pattern first (e.g., {', '.join(tags[:2]) if tags else 'arrays/graphs'})."
        structural = "Outline inputs/outputs, invariants, and a step plan before coding."
        concrete = "Start with a small example; trace your steps and verify edge cases."
        if query:
            concrete += f" Consider: {query.strip()}"
        # No sleep: keep local provider fast
        return {
            "problem_id": problem.id,
            "provider": ctx.provider,
            "model": ctx.model,
            "hints": [
                {"level": "conceptual", "text": conceptual},
                {"level": "structural", "text": structural},
                {"level": "concrete", "text": concrete},
            ],
        }

    def review_code(self, code: str, rubric: Optional[Dict[str, Any]], ctx: AIContext, problem: Optional[Problem] = None) -> Dict[str, Any]:
        loc = len(code.splitlines()) if code else 0
        has_tests = "assert" in code.lower() or "unittest" in code.lower()
        strengths: List[str] = []
        suggestions: List[str] = []
        if loc >= 15:
            strengths.append("Sufficient code length for non-trivial logic.")
        else:
            suggestions.append("Expand solution with clear structure and helper functions if needed.")
        if has_tests:
            strengths.append("Includes tests or checks.")
        else:
            suggestions.append("Add basic tests or assertions to validate behavior.")
        suggestions.append("Document time/space complexity and main invariants.")
        return {
            "provider": ctx.provider,
            "model": ctx.model,
            "rubric": rubric or {"criteria": ["correctness", "readability", "efficiency", "tests"]},
            "strengths": strengths,
            "suggestions": suggestions,
        }

    def elaborate_prompts(self, problem: Problem, ctx: AIContext) -> Dict[str, Any]:
        why = [
            "Why does this approach ensure correctness across edge cases?",
            "Why is the chosen data structure appropriate here?",
        ]
        how = [
            "How would the algorithm change for streaming input?",
            "How can you verify the invariant holds after each step?",
        ]
        return {
            "problem_id": problem.id,
            "provider": ctx.provider,
            "model": ctx.model,
            "why_questions": why,
            "how_questions": how,
        }
