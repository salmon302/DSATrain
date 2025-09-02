from __future__ import annotations

import os
from typing import Optional, Dict, Any

from src.models.database import Problem
from .base import ProviderBase, AIContext


class AnthropicRealProvider(ProviderBase):
    name = "anthropic-real"

    def __init__(self):
        # Lazy import to keep dependency optional
        try:
            import httpx  # noqa: F401
        except Exception:
            raise RuntimeError("httpx is required for AnthropicRealProvider")

    def _api_key(self) -> str:
        key = os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        return key

    def _model(self, ctx: AIContext) -> str:
        # Reasonable default; UI controls effective model selection
        return ctx.model or "claude-3-haiku"

    def generate_hint(self, problem: Problem, query: Optional[str], ctx: AIContext) -> Dict[str, Any]:
        # Placeholder non-network implementation; returns stable shape
        return {
            "problem_id": problem.id,
            "provider": ctx.provider,
            "model": self._model(ctx),
            "hints": [
                {"level": "conceptual", "text": "Identify the core pattern and constraints."},
                {"level": "structural", "text": "Sketch inputs/outputs and key invariants."},
                {"level": "concrete", "text": ("Try a small example." + (f" Query: {query}" if query else ""))},
            ],
            "meta": {"estimated_cost_usd": 0.0012},
        }

    def review_code(self, code: str, rubric: Optional[Dict[str, Any]], ctx: AIContext, problem: Optional[Problem] = None) -> Dict[str, Any]:
        return {
            "provider": ctx.provider,
            "model": self._model(ctx),
            "rubric": rubric or {"criteria": ["correctness", "readability", "efficiency", "tests"]},
            "strengths": ["Good decomposition"],
            "suggestions": ["Clarify edge cases and add unit tests"],
            "meta": {"estimated_cost_usd": 0.0025},
        }

    def elaborate_prompts(self, problem: Problem, ctx: AIContext) -> Dict[str, Any]:
        return {
            "problem_id": problem.id,
            "provider": ctx.provider,
            "model": self._model(ctx),
            "why_questions": ["Why is your chosen data structure appropriate?"],
            "how_questions": ["How could you reduce worst-case time complexity?"],
            "meta": {"estimated_cost_usd": 0.0012},
        }


