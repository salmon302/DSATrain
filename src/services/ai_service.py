"""
AIService: Provider-agnostic AI layer with local/mock providers.
No external network calls; respects SettingsService gating.
"""
from __future__ import annotations

from typing import Dict, Any, List, Optional, Tuple
import os
import time
from collections import deque, defaultdict
from dataclasses import dataclass
from sqlalchemy.orm import Session

from src.models.database import Problem
from src.services.settings_service import SettingsService
from src.services.providers.base import ProviderBase, AIContext as ProviderAIContext
from src.services.providers.local import LocalProvider
from src.services.providers.mock_openai import MockOpenAIProvider
from src.services.providers.mock_anthropic import MockAnthropicProvider
from src.services.providers.mock_openrouter import MockOpenRouterProvider
from src.services.rate_limit.in_memory import InMemoryRateLimiter
try:
    from src.services.rate_limit.redis_backed import RedisRateLimiter  # type: ignore
except Exception:
    RedisRateLimiter = None  # type: ignore
from src.services.metrics import Metrics
import logging

logger = logging.getLogger(__name__)


class AIForbidden(Exception):
    """Raised when AI features are disabled by settings or access is not allowed."""
    pass


class AIRateLimited(Exception):
    """Raised when global rate limits or per-session budgets are exceeded."""
    def __init__(self, message: str, retry_after_seconds: Optional[int] = None):
        super().__init__(message)
        self.retry_after_seconds = retry_after_seconds


@dataclass
class AIContext:
    enable_ai: bool
    provider: str
    model: Optional[str]


class AIService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = SettingsService()
        # In-memory global rate limiter and per-session hint budgets
        # Deques store timestamps (seconds) of recent requests
        if not hasattr(AIService, "_global_requests"):
            AIService._global_requests = deque()  # type: ignore[attr-defined]
        if not hasattr(AIService, "_hints_by_session"):
            AIService._hints_by_session = defaultdict(int)  # type: ignore[attr-defined]
        if not hasattr(AIService, "_rl_key"):
            AIService._rl_key = None  # type: ignore[attr-defined]
        # Rate limiter instance per process; keyed to settings
        if not hasattr(AIService, "_rate_limiter"):
            AIService._rate_limiter = None  # type: ignore[attr-defined]

    def _enforce_global_rate_limit(self):
        s = self.settings.load()
        window_secs = int(getattr(s, "rate_limit_window_seconds", 60) or 60)
        limit = int(s.rate_limit_per_minute or 0)
        use_redis = os.getenv("DSATRAIN_USE_REDIS_RATE_LIMIT", "0") in ("1", "true", "True")
        rl_key = (s.ai_provider, s.model, limit, window_secs, use_redis, os.getenv("DSATRAIN_REDIS_URL"))
        current_key = getattr(AIService, "_rl_key", None)  # type: ignore[attr-defined]
        if current_key != rl_key or getattr(AIService, "_rate_limiter", None) is None:  # type: ignore[attr-defined]
            if use_redis and RedisRateLimiter is not None:
                try:
                    AIService._rate_limiter = RedisRateLimiter(limit, window_secs, s.ai_provider, s.model, os.getenv("DSATRAIN_REDIS_URL"))  # type: ignore[attr-defined]
                except Exception as e:
                    # Fallback to in-memory if Redis not available
                    logger.warning("Redis rate limiter unavailable, falling back to in-memory: %s", e)
                    AIService._rate_limiter = InMemoryRateLimiter(limit, window_secs, s.ai_provider, s.model)  # type: ignore[attr-defined]
            else:
                AIService._rate_limiter = InMemoryRateLimiter(limit, window_secs, s.ai_provider, s.model)  # type: ignore[attr-defined]
            AIService._rl_key = rl_key  # type: ignore[attr-defined]
        limiter = AIService._rate_limiter  # type: ignore[attr-defined]
        try:
            limiter.check_and_increment()
        except Exception as e:
            # Map to AIRateLimited if RateLimitExceeded
            retry_after = getattr(e, "retry_after_seconds", None)
            Metrics.incr("ai.rate_limit_hits")
            raise AIRateLimited(str(e), retry_after_seconds=retry_after)

    def get_status(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Return current AI usage status: global rate limit window and per-session hint usage."""
        s = self.settings.load()
        limit = int(s.rate_limit_per_minute or 0)
        window_secs = int(getattr(s, "rate_limit_window_seconds", 60) or 60)
        limiter = getattr(AIService, "_rate_limiter", None)  # type: ignore[attr-defined]
        if limiter is None:
            # Initialize a temporary limiter to compute status
            limiter = InMemoryRateLimiter(limit, window_secs, s.ai_provider, s.model)
        st = limiter.status()
        used = st.used
        reset_secs = st.reset_seconds
        sess_used = None
        if session_id:
            # Prefer limiter-provided usage if available
            try:
                if hasattr(limiter, "get_hint_usage"):
                    sess_used = int(limiter.get_hint_usage(session_id))  # type: ignore[attr-defined]
                else:
                    sess_used = int(AIService._hints_by_session.get(session_id, 0))  # type: ignore[attr-defined]
            except Exception:
                sess_used = int(AIService._hints_by_session.get(session_id, 0))  # type: ignore[attr-defined]
        return {
            "enabled": s.enable_ai and s.ai_provider not in {None, "", "none"},
            "provider": s.ai_provider,
            "model": s.model,
            "rate_limit_per_minute": limit,
            "rate_limit_used": used,
            "rate_limit_window_seconds": window_secs,
            "rate_limit_reset_seconds": reset_secs,
            "hint_budget_per_session": int(s.hint_budget_per_session or 0),
            "hints_used_this_session": sess_used,
        }

    def reset(self, session_id: Optional[str] = None, reset_global: bool = True) -> Dict[str, Any]:
        """Reset in-memory counters. If session_id provided, reset that session's hint usage.
        When reset_global is True (default), also clear the global rate limiter bucket.
        Returns current status after reset.
        """
        limiter = getattr(AIService, "_rate_limiter", None)  # type: ignore[attr-defined]
        if limiter is not None:
            try:
                limiter.reset(session_id=session_id, reset_global=reset_global)
            except Exception:
                pass
        # Observability: count resets
        Metrics.incr("ai.resets")
        if session_id:
            Metrics.incr("ai.resets.session")
        return self.get_status(session_id=session_id)

    def _precheck_hint_budget(self, session_id: Optional[str]):
        """Check but do not decrement the session budget."""
        if not session_id:
            return
        s = self.settings.load()
        budget = int(s.hint_budget_per_session or 0)
        if budget <= 0:
            return
        limiter = getattr(AIService, "_rate_limiter", None)  # type: ignore[attr-defined]
        if limiter is None:
            limiter = InMemoryRateLimiter(s.rate_limit_per_minute, getattr(s, "rate_limit_window_seconds", 60), s.ai_provider, s.model)
        try:
            if hasattr(limiter, "check_hint_budget"):
                limiter.check_hint_budget(session_id, budget)  # type: ignore[attr-defined]
            else:
                # Backward-compat fallback uses enforce-and-count, but we don't want to decrement; emulate check
                if hasattr(limiter, "_hints_by_session"):
                    used = limiter._hints_by_session.get(session_id, 0)  # type: ignore[attr-defined]
                    if used >= budget:
                        raise Exception("Hint budget exceeded for this session.")
        except Exception as e:
            Metrics.incr("ai.hint_budget_exceeded")
            raise AIRateLimited(str(e))

    def _commit_hint_budget(self, session_id: Optional[str]):
        if not session_id:
            return
        s = self.settings.load()
        budget = int(s.hint_budget_per_session or 0)
        if budget <= 0:
            return
        limiter = getattr(AIService, "_rate_limiter", None)  # type: ignore[attr-defined]
        if limiter is None:
            limiter = InMemoryRateLimiter(s.rate_limit_per_minute, getattr(s, "rate_limit_window_seconds", 60), s.ai_provider, s.model)
        try:
            if hasattr(limiter, "commit_hint_usage"):
                limiter.commit_hint_usage(session_id)  # type: ignore[attr-defined]
            else:
                # Fallback to old behavior
                limiter.enforce_and_count_hint(session_id, budget)
        except Exception:
            # Do not surface commit errors; budgets are best-effort
            pass

    def _get_context(self) -> AIContext:
        s = self.settings.load()
        return AIContext(enable_ai=s.enable_ai, provider=s.ai_provider, model=s.model)

    def _provider_and_ctx(self) -> Tuple[ProviderBase, ProviderAIContext]:
        s = self.settings.load()
        prov = (s.ai_provider or "none").lower()
        # Provider selection: default to LocalProvider for 'local' or unknown
        if prov == "openai":
            provider: ProviderBase = MockOpenAIProvider()
        elif prov == "anthropic":
            provider = MockAnthropicProvider()
        elif prov == "openrouter":
            provider = MockOpenRouterProvider()
        elif prov == "local":
            provider = LocalProvider()
        else:
            provider = LocalProvider()
        ctx = ProviderAIContext(enable_ai=s.enable_ai, provider=prov, model=s.model)
        return provider, ctx

    def _ensure_enabled(self):
        ctx = self._get_context()
        if not ctx.enable_ai or ctx.provider in {None, "", "none"}:
            raise AIForbidden("AI is disabled in settings")
        return ctx

    def generate_hint(self, problem_id: str, query: Optional[str] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        ctx = self._ensure_enabled()
        self._enforce_global_rate_limit()
        problem = self.db.query(Problem).filter(Problem.id == problem_id).first()
        if not problem:
            raise ValueError("Problem not found")
        # Pre-check budget; only commit after successful generation
        self._precheck_hint_budget(session_id)
        Metrics.incr("ai.requests.hint")
        provider, pctx = self._provider_and_ctx()
        result = provider.generate_hint(problem=problem, query=query, ctx=pctx)
        # Observability: include optional session envelope for correlation
        if isinstance(result, dict) and session_id:
            result.setdefault("meta", {})
            try:
                # Reflect current usage after commit
                self._commit_hint_budget(session_id)
                hints_used = None
                limiter = getattr(AIService, "_rate_limiter", None)  # type: ignore[attr-defined]
                if limiter and hasattr(limiter, "get_hint_usage"):
                    hints_used = limiter.get_hint_usage(session_id)  # type: ignore[attr-defined]
                else:
                    hints_used = getattr(AIService, "_hints_by_session", {}).get(session_id, None)  # type: ignore[attr-defined]
                result["meta"].update({
                    "session_id": session_id,
                    "hints_used": int(hints_used) if hints_used is not None else None,
                })
            except Exception:
                # Even if budget commit fails, return the hint; rate limiter will still apply globally
                pass
        else:
            # No session id; nothing to commit
            pass
        return result

    def review_code(self, code: str, rubric: Optional[Dict[str, Any]] = None, problem_id: Optional[str] = None) -> Dict[str, Any]:
        ctx = self._ensure_enabled()
        self._enforce_global_rate_limit()
        Metrics.incr("ai.requests.review")
        provider, pctx = self._provider_and_ctx()
        # Optional: pass problem if supplied
        problem = None
        if problem_id:
            problem = self.db.query(Problem).filter(Problem.id == problem_id).first()
        return provider.review_code(code=code, rubric=rubric, ctx=pctx, problem=problem)

    def elaborate_prompts(self, problem_id: str) -> Dict[str, Any]:
        ctx = self._ensure_enabled()
        problem = self.db.query(Problem).filter(Problem.id == problem_id).first()
        if not problem:
            raise ValueError("Problem not found")
        Metrics.incr("ai.requests.elaborate")
        provider, pctx = self._provider_and_ctx()
        return provider.elaborate_prompts(problem=problem, ctx=pctx)
