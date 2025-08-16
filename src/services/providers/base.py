"""
Provider interface for AI behaviors.

This abstraction allows swapping local heuristics with mock or real providers
without changing the public API. No external network I/O should occur in tests.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any

from src.models.database import Problem


@dataclass
class AIContext:
    enable_ai: bool
    provider: str
    model: Optional[str]


class ProviderBase:
    """Base class for provider plugins.

        Contract overview (keep responses stable for API callers):
        - Inputs:
            - problem: DB model for context when applicable
            - code/rubric/query: Optional user inputs
            - ctx: AIContext with enable_ai/provider/model flags

        - Outputs (dicts) should include at minimum the provider and model used
            when relevant, and follow these shapes:

            generate_hint(problem, query, ctx) -> Dict[str, Any]
                {
                    "problem_id": str,
                    "provider": str,      # ctx.provider
                    "model": Optional[str],
                    "hints": [
                        {"level": "conceptual"|"structural"|"concrete", "text": str},
                        ...
                    ]
                }

            review_code(code, rubric, ctx, problem) -> Dict[str, Any]
                {
                    "provider": str,
                    "model": Optional[str],
                    "rubric": Dict[str, Any],
                    "strengths": [str],
                    "suggestions": [str]
                }

            elaborate_prompts(problem, ctx) -> Dict[str, Any]
                {
                    "problem_id": str,
                    "provider": str,
                    "model": Optional[str],
                    "why_questions": [str],
                    "how_questions": [str]
                }

    Notes:
    - Implementations MUST avoid external I/O during unit tests.
    - If simulating latency, keep sleeps minimal (<20ms) to avoid slow tests.
    - Avoid leaking secrets; only return non-sensitive metadata.
    """

    name: str = "base"

    def generate_hint(self, problem: Problem, query: Optional[str], ctx: AIContext) -> Dict[str, Any]:
        raise NotImplementedError

    def review_code(self, code: str, rubric: Optional[Dict[str, Any]], ctx: AIContext, problem: Optional[Problem] = None) -> Dict[str, Any]:
        raise NotImplementedError

    def elaborate_prompts(self, problem: Problem, ctx: AIContext) -> Dict[str, Any]:
        raise NotImplementedError
