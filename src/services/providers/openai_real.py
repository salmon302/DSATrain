from __future__ import annotations

import os
from typing import Optional, Dict, Any

from src.models.database import Problem
from .base import ProviderBase, AIContext


class OpenAIRealProvider(ProviderBase):
    name = "openai-real"

    def __init__(self):
        # Lazy import to keep dependency optional
        try:
            import httpx  # noqa: F401
        except Exception:
            raise RuntimeError("httpx is required for OpenAIRealProvider")

    def _api_key(self) -> str:
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        return key

    def _client(self):
        import httpx
        return httpx.Client(timeout=10)

    def _model(self, ctx: AIContext) -> str:
        return ctx.model or "gpt-4o-mini"

    def generate_hint(self, problem: Problem, query: Optional[str], ctx: AIContext) -> Dict[str, Any]:
        # Placeholder: in real impl, call OpenAI responses API; return minimal stable shape
        # Keep as a safe fallback to avoid real calls while wiring
        return {
            "problem_id": problem.id,
            "provider": ctx.provider,
            "model": self._model(ctx),
            "hints": [
                {"level": "conceptual", "text": "Focus on the core pattern and constraints."},
                {"level": "structural", "text": "Outline inputs/outputs and invariants."},
                {"level": "concrete", "text": ("Walk through a small example." + (f" Query: {query}" if query else ""))},
            ],
        }

    def review_code(self, code: str, rubric: Optional[Dict[str, Any]], ctx: AIContext, problem: Optional[Problem] = None) -> Dict[str, Any]:
        return {
            "provider": ctx.provider,
            "model": self._model(ctx),
            "rubric": rubric or {"criteria": ["correctness", "readability", "efficiency", "tests"]},
            "strengths": ["Clear decomposition"],
            "suggestions": ["Consider edge cases and complexity tradeoffs"],
        }

    def elaborate_prompts(self, problem: Problem, ctx: AIContext) -> Dict[str, Any]:
        return {
            "problem_id": problem.id,
            "provider": ctx.provider,
            "model": self._model(ctx),
            "why_questions": ["Why does your approach handle worst-case inputs?"],
            "how_questions": ["How could you optimize memory usage?"],
        }


