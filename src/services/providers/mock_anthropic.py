from __future__ import annotations

import time
from typing import Optional, Dict, Any

from src.models.database import Problem
from .base import ProviderBase, AIContext


class MockAnthropicProvider(ProviderBase):
    name = "anthropic"

    def _sleep(self):
        time.sleep(0.01)

    def generate_hint(self, problem: Problem, query: Optional[str], ctx: AIContext) -> Dict[str, Any]:
        self._sleep()
        return {
            "problem_id": problem.id,
            "provider": ctx.provider,
            "model": ctx.model or "claude-3-haiku",
            "hints": [
                {"level": "conceptual", "text": "Clarify constraints and invariants."},
                {"level": "structural", "text": "Enumerate cases and structure a robust approach."},
                {"level": "concrete", "text": ("Work a small case and test boundaries." + (f" Query: {query}" if query else ""))},
            ],
        }

    def review_code(self, code: str, rubric: Optional[Dict[str, Any]], ctx: AIContext, problem: Optional[Problem] = None) -> Dict[str, Any]:
        self._sleep()
        return {
            "provider": ctx.provider,
            "model": ctx.model or "claude-3-haiku",
            "rubric": rubric or {"criteria": ["correctness", "readability", "efficiency", "tests"]},
            "strengths": ["Readable structure"],
            "suggestions": ["Add comments and complexity analysis"],
        }

    def elaborate_prompts(self, problem: Problem, ctx: AIContext) -> Dict[str, Any]:
        self._sleep()
        return {
            "problem_id": problem.id,
            "provider": ctx.provider,
            "model": ctx.model or "claude-3-haiku",
            "why_questions": ["Why is this data structure appropriate?"],
            "how_questions": ["How to adapt to streaming inputs?"],
        }
