from __future__ import annotations

import os
from typing import Optional, Dict, Any

from src.models.database import Problem
from .base import ProviderBase, AIContext


class OpenRouterRealProvider(ProviderBase):
    name = "openrouter-real"

    def __init__(self):
        try:
            import httpx  # noqa: F401
        except Exception:
            raise RuntimeError("httpx is required for OpenRouterRealProvider")

    def _api_key(self) -> str:
        key = os.getenv("OPENROUTER_API_KEY")
        if not key:
            raise RuntimeError("OPENROUTER_API_KEY is not set")
        return key

    def _model(self, ctx: AIContext) -> str:
        return ctx.model or "meta-llama/llama-3.1-8b-instruct:free"

    def generate_hint(self, problem: Problem, query: Optional[str], ctx: AIContext) -> Dict[str, Any]:
        # Placeholder; keep stable shape
        return {
            "problem_id": problem.id,
            "provider": ctx.provider,
            "model": self._model(ctx),
            "hints": [
                {"level": "conceptual", "text": "Focus on constraints and pattern selection."},
                {"level": "structural", "text": "Outline approach with base cases and transitions."},
                {"level": "concrete", "text": ("Test a small input-handcrafted case." + (f" Query: {query}" if query else ""))},
            ],
            "meta": {"estimated_cost_usd": 0.0008},
        }

    def review_code(self, code: str, rubric: Optional[Dict[str, Any]], ctx: AIContext, problem: Optional[Problem] = None) -> Dict[str, Any]:
        return {
            "provider": ctx.provider,
            "model": self._model(ctx),
            "rubric": rubric or {"criteria": ["correctness", "readability", "efficiency", "tests"]},
            "strengths": ["Clear variable naming"],
            "suggestions": ["Consider time/space tradeoffs and add boundary tests"],
            "meta": {"estimated_cost_usd": 0.0015},
        }

    def elaborate_prompts(self, problem: Problem, ctx: AIContext) -> Dict[str, Any]:
        return {
            "problem_id": problem.id,
            "provider": ctx.provider,
            "model": self._model(ctx),
            "why_questions": ["Why does your loop invariant ensure correctness?"],
            "how_questions": ["How would you optimize memory or precompute?"],
            "meta": {"estimated_cost_usd": 0.0008},
        }


