from __future__ import annotations

import time
from typing import Optional, Dict, Any

from src.models.database import Problem
from .base import ProviderBase, AIContext


class MockOpenRouterProvider(ProviderBase):
    name = "openrouter"

    def _sleep(self):
        time.sleep(0.01)

    def generate_hint(self, problem: Problem, query: Optional[str], ctx: AIContext) -> Dict[str, Any]:
        self._sleep()
        return {
            "problem_id": problem.id,
            "provider": ctx.provider,
            "model": ctx.model or "meta-llama/llama-3-8b-instruct",
            "hints": [
                {"level": "conceptual", "text": "Think in terms of known patterns first."},
                {"level": "structural", "text": "Outline a plan and decide on data structures early."},
                {"level": "concrete", "text": ("Run through a concrete example and edge cases." + (f" Query: {query}" if query else ""))},
            ],
        }

    def review_code(self, code: str, rubric: Optional[Dict[str, Any]], ctx: AIContext, problem: Optional[Problem] = None) -> Dict[str, Any]:
        self._sleep()
        return {
            "provider": ctx.provider,
            "model": ctx.model or "meta-llama/llama-3-8b-instruct",
            "rubric": rubric or {"criteria": ["correctness", "readability", "efficiency", "tests"]},
            "strengths": ["Good decomposition"],
            "suggestions": ["Consider memory-time tradeoffs"],
        }

    def elaborate_prompts(self, problem: Problem, ctx: AIContext) -> Dict[str, Any]:
        self._sleep()
        return {
            "problem_id": problem.id,
            "provider": ctx.provider,
            "model": ctx.model or "meta-llama/llama-3-8b-instruct",
            "why_questions": ["Why does your invariant imply correctness?"],
            "how_questions": ["How to parallelize or batch operations?"],
        }
