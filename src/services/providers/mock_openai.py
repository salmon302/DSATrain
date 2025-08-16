from __future__ import annotations

import time
import random
from typing import Optional, Dict, Any

from src.models.database import Problem
from .base import ProviderBase, AIContext


class MockOpenAIProvider(ProviderBase):
    name = "openai"

    def _sleep(self):
        # Simulate realistic latency without slowing tests too much
        time.sleep(0.01)

    def generate_hint(self, problem: Problem, query: Optional[str], ctx: AIContext) -> Dict[str, Any]:
        self._sleep()
        return {
            "problem_id": problem.id,
            "provider": ctx.provider,
            "model": ctx.model or "gpt-4o-mini",
            "hints": [
                {"level": "conceptual", "text": "Focus on high-level reasoning steps first."},
                {"level": "structural", "text": "Draft an outline and break the problem into sub-problems."},
                {"level": "concrete", "text": ("Try a small example and iterate." + (f" Query: {query}" if query else ""))},
            ],
        }

    def review_code(self, code: str, rubric: Optional[Dict[str, Any]], ctx: AIContext, problem: Optional[Problem] = None) -> Dict[str, Any]:
        self._sleep()
        return {
            "provider": ctx.provider,
            "model": ctx.model or "gpt-4o-mini",
            "rubric": rubric or {"criteria": ["correctness", "readability", "efficiency", "tests"]},
            "strengths": ["Clear variable naming"],
            "suggestions": ["Consider edge cases and add unit tests"],
        }

    def elaborate_prompts(self, problem: Problem, ctx: AIContext) -> Dict[str, Any]:
        self._sleep()
        return {
            "problem_id": problem.id,
            "provider": ctx.provider,
            "model": ctx.model or "gpt-4o-mini",
            "why_questions": ["Why does this solution scale?"],
            "how_questions": ["How would you optimize memory usage?"],
        }
