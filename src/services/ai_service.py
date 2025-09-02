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
try:
    from src.services.providers.openai_real import OpenAIRealProvider  # type: ignore
except Exception:
    OpenAIRealProvider = None  # type: ignore
try:
    from src.services.providers.anthropic_real import AnthropicRealProvider  # type: ignore
except Exception:
    AnthropicRealProvider = None  # type: ignore
try:
    from src.services.providers.openrouter_real import OpenRouterRealProvider  # type: ignore
except Exception:
    OpenRouterRealProvider = None  # type: ignore
from src.services.rate_limit.in_memory import InMemoryRateLimiter
from src.services.costs.in_memory import InMemoryCostLedger
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


class AICostExceeded(Exception):
    """Raised when monthly cost cap would be exceeded."""
    pass


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
        if not hasattr(AIService, "_cost_ledger"):
            AIService._cost_ledger = None  # type: ignore[attr-defined]
        # Lightweight in-memory cache for idempotent responses (hints/elaboration)
        if not hasattr(AIService, "_cache_store"):
            AIService._cache_store = {}  # type: ignore[attr-defined]
        if not hasattr(AIService, "_cache_meta"):
            AIService._cache_meta = {"ttl_seconds": 60}  # type: ignore[attr-defined]

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

    def _enforce_cost_cap(self, estimated_cost_usd: float) -> None:
        s = self.settings.load()
        # Initialize ledger when settings change (cap included in key)
        cap = float(getattr(s, "monthly_cost_cap_usd", 0.0) or 0.0)
        key = (cap,)
        current_key = getattr(AIService, "_cost_key", None)  # type: ignore[attr-defined]
        if current_key != key or getattr(AIService, "_cost_ledger", None) is None:  # type: ignore[attr-defined]
            AIService._cost_ledger = InMemoryCostLedger(cap)  # type: ignore[attr-defined]
            AIService._cost_key = key  # type: ignore[attr-defined]
        ledger = AIService._cost_ledger  # type: ignore[attr-defined]
        try:
            ledger.precheck(estimated_cost_usd)
        except Exception as e:
            Metrics.incr("ai.cost_cap_blocked")
            raise AICostExceeded(str(e))

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
        hint_used = None
        review_used = None
        elaborate_used = None
        if session_id:
            # Prefer limiter-provided usage if available
            try:
                if hasattr(limiter, "get_hint_usage"):
                    sess_used = int(limiter.get_hint_usage(session_id))  # type: ignore[attr-defined]
                else:
                    sess_used = int(AIService._hints_by_session.get(session_id, 0))  # type: ignore[attr-defined]
            except Exception:
                sess_used = int(AIService._hints_by_session.get(session_id, 0))  # type: ignore[attr-defined]
            # Generic action usage
            try:
                if hasattr(limiter, "get_action_usage"):
                    hint_used = int(limiter.get_action_usage(session_id, "hint"))  # type: ignore[attr-defined]
                    review_used = int(limiter.get_action_usage(session_id, "review"))  # type: ignore[attr-defined]
                    elaborate_used = int(limiter.get_action_usage(session_id, "elaborate"))  # type: ignore[attr-defined]
            except Exception:
                pass
        # Cost status
        ledger = getattr(AIService, "_cost_ledger", None)  # type: ignore[attr-defined]
        if ledger is None:
            ledger = InMemoryCostLedger(float(getattr(s, "monthly_cost_cap_usd", 0.0) or 0.0))
        cost_status = ledger.status()
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
            "review_budget_per_session": int(getattr(s, "review_budget_per_session", 0) or 0),
            "reviews_used_this_session": int(review_used or 0) if session_id else None,
            "elaborate_budget_per_session": int(getattr(s, "elaborate_budget_per_session", 0) or 0),
            "elaborates_used_this_session": int(elaborate_used or 0) if session_id else None,
            "monthly_cost_cap_usd": float(getattr(s, "monthly_cost_cap_usd", 0.0) or 0.0),
            "monthly_cost_used_usd": float(cost_status.used_usd or 0.0),
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
            # Use real provider only if explicitly allowed by env flag
            allow_real = os.getenv("DSATRAIN_ENABLE_REAL_OPENAI", "0") in ("1", "true", "True")
            if allow_real and OpenAIRealProvider is not None:
                try:
                    provider = OpenAIRealProvider()
                except Exception:
                    provider = MockOpenAIProvider()
            else:
                provider = MockOpenAIProvider()
        elif prov == "anthropic":
            allow_real = os.getenv("DSATRAIN_ENABLE_REAL_ANTHROPIC", "0") in ("1", "true", "True")
            if allow_real and AnthropicRealProvider is not None:
                try:
                    provider = AnthropicRealProvider()
                except Exception:
                    provider = MockAnthropicProvider()
            else:
                provider = MockAnthropicProvider()
        elif prov == "openrouter":
            allow_real = os.getenv("DSATRAIN_ENABLE_REAL_OPENROUTER", "0") in ("1", "true", "True")
            if allow_real and OpenRouterRealProvider is not None:
                try:
                    provider = OpenRouterRealProvider()
                except Exception:
                    provider = MockOpenRouterProvider()
            else:
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
        # Rough estimated cost in USD per hint request (0 for local/mock by default)
        estimated_cost = self._estimate_cost(action="hint", provider=ctx.provider, model=ctx.model)
        self._enforce_cost_cap(estimated_cost)
        problem = self.db.query(Problem).filter(Problem.id == problem_id).first()
        if not problem:
            raise ValueError("Problem not found")
        # Cache lookup
        cache_key = ("hint", ctx.provider, ctx.model, problem_id, (query or "").strip().lower())
        now = time.monotonic()
        ttl = int(getattr(AIService, "_cache_meta", {}).get("ttl_seconds", 60))  # type: ignore[attr-defined]
        entry = getattr(AIService, "_cache_store", {}).get(cache_key)  # type: ignore[attr-defined]
        if entry and (now - entry[0]) <= ttl:
            result = entry[1]
            try:
                if isinstance(result, dict):
                    result.setdefault("meta", {})
                    result["meta"]["cached"] = True
            except Exception:
                pass
            Metrics.incr("ai.cache.hit")
            # Do not re-commit budgets/costs on cache hit; return as-is (with meta preserved)
            return result
        Metrics.incr("ai.cache.miss")
        # Pre-check budget; only commit after successful generation
        self._precheck_hint_budget(session_id)
        # Also enforce generic per-action budgets if configured
        self._precheck_action_budget(session_id, "hint")
        Metrics.incr("ai.requests.hint")
        provider, pctx = self._provider_and_ctx()
        result = provider.generate_hint(problem=problem, query=query, ctx=pctx)
        # Commit cost (prefer provider-reported cost if present)
        try:
            meta = result.get("meta") if isinstance(result, dict) else None
            actual_cost = float(meta.get("estimated_cost_usd")) if isinstance(meta, dict) and meta.get("estimated_cost_usd") is not None else estimated_cost
        except Exception:
            actual_cost = estimated_cost
        self._commit_cost(actual_cost)
        # Observability: include optional session envelope for correlation
        if isinstance(result, dict) and session_id:
            result.setdefault("meta", {})
            try:
                # Reflect current usage after commit
                self._commit_hint_budget(session_id)
                self._commit_action_usage(session_id, "hint")
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
        # Write-through cache
        try:
            getattr(AIService, "_cache_store", {})[cache_key] = (now, result)  # type: ignore[attr-defined]
        except Exception:
            pass
        # Ensure meta reflects cost
        try:
            if isinstance(result, dict):
                result.setdefault("meta", {})
                result["meta"]["estimated_cost_usd"] = actual_cost
        except Exception:
            pass
        return result

    def review_code(self, code: str, rubric: Optional[Dict[str, Any]] = None, problem_id: Optional[str] = None) -> Dict[str, Any]:
        ctx = self._ensure_enabled()
        self._enforce_global_rate_limit()
        estimated_cost = self._estimate_cost(action="review", provider=ctx.provider, model=ctx.model)
        self._enforce_cost_cap(estimated_cost)
        # Enforce per-session budget if a session is provided in rubric meta (optional)
        session_id = None
        try:
            if isinstance(rubric, dict):
                session_id = rubric.get("session_id")  # type: ignore[assignment]
        except Exception:
            session_id = None
        if session_id:
            self._precheck_action_budget(session_id, "review")
        Metrics.incr("ai.requests.review")
        provider, pctx = self._provider_and_ctx()
        # Optional: pass problem if supplied
        problem = None
        if problem_id:
            problem = self.db.query(Problem).filter(Problem.id == problem_id).first()
        result = provider.review_code(code=code, rubric=rubric, ctx=pctx, problem=problem)
        if session_id:
            self._commit_action_usage(session_id, "review")
        try:
            meta = result.get("meta") if isinstance(result, dict) else None
            actual_cost = float(meta.get("estimated_cost_usd")) if isinstance(meta, dict) and meta.get("estimated_cost_usd") is not None else estimated_cost
        except Exception:
            actual_cost = estimated_cost
        self._commit_cost(actual_cost)
        try:
            if isinstance(result, dict):
                result.setdefault("meta", {})
                result["meta"]["estimated_cost_usd"] = actual_cost
        except Exception:
            pass
        return result

    def elaborate_prompts(self, problem_id: str) -> Dict[str, Any]:
        ctx = self._ensure_enabled()
        self._enforce_global_rate_limit()
        estimated_cost = self._estimate_cost(action="elaborate", provider=ctx.provider, model=ctx.model)
        self._enforce_cost_cap(estimated_cost)
        problem = self.db.query(Problem).filter(Problem.id == problem_id).first()
        if not problem:
            raise ValueError("Problem not found")
        Metrics.incr("ai.requests.elaborate")
        provider, pctx = self._provider_and_ctx()
        # Cache lookup
        cache_key = ("elaborate", ctx.provider, ctx.model, problem_id)
        now = time.monotonic()
        ttl = int(getattr(AIService, "_cache_meta", {}).get("ttl_seconds", 60))  # type: ignore[attr-defined]
        entry = getattr(AIService, "_cache_store", {}).get(cache_key)  # type: ignore[attr-defined]
        if entry and (now - entry[0]) <= ttl:
            Metrics.incr("ai.cache.hit")
            result_cached = entry[1]
            try:
                if isinstance(result_cached, dict):
                    result_cached.setdefault("meta", {})
                    result_cached["meta"]["cached"] = True
            except Exception:
                pass
            return result_cached
        Metrics.incr("ai.cache.miss")
        # For elaborate, optionally read session_id from environment context later; for now budget only if provided via model
        result = provider.elaborate_prompts(problem=problem, ctx=pctx)
        # If response includes meta.session_id, commit usage. (Backward compatible: no-op if absent)
        try:
            session_id = None
            if isinstance(result, dict):
                meta = result.get("meta")
                if isinstance(meta, dict):
                    session_id = meta.get("session_id")
            if session_id:
                self._precheck_action_budget(session_id, "elaborate")
                self._commit_action_usage(session_id, "elaborate")
        except Exception:
            pass
        try:
            meta = result.get("meta") if isinstance(result, dict) else None
            actual_cost = float(meta.get("estimated_cost_usd")) if isinstance(meta, dict) and meta.get("estimated_cost_usd") is not None else estimated_cost
        except Exception:
            actual_cost = estimated_cost
        self._commit_cost(actual_cost)
        try:
            if isinstance(result, dict):
                result.setdefault("meta", {})
                result["meta"]["estimated_cost_usd"] = actual_cost
        except Exception:
            pass
        # Write-through cache
        try:
            getattr(AIService, "_cache_store", {})[cache_key] = (now, result)  # type: ignore[attr-defined]
        except Exception:
            pass
        return result

    def _precheck_action_budget(self, session_id: Optional[str], action: str) -> None:
        if not session_id:
            return
        s = self.settings.load()
        budget_map = {
            "hint": int(s.hint_budget_per_session or 0),
            "review": int(getattr(s, "review_budget_per_session", 0) or 0),
            "elaborate": int(getattr(s, "elaborate_budget_per_session", 0) or 0),
        }
        budget = budget_map.get(action, 0)
        if budget <= 0:
            return
        limiter = getattr(AIService, "_rate_limiter", None)  # type: ignore[attr-defined]
        if limiter is None:
            limiter = InMemoryRateLimiter(s.rate_limit_per_minute, getattr(s, "rate_limit_window_seconds", 60), s.ai_provider, s.model)
        if hasattr(limiter, "check_action_budget"):
            limiter.check_action_budget(session_id, budget, action)  # type: ignore[attr-defined]

    def _commit_action_usage(self, session_id: Optional[str], action: str) -> None:
        if not session_id:
            return
        s = self.settings.load()
        budget_map = {
            "hint": int(s.hint_budget_per_session or 0),
            "review": int(getattr(s, "review_budget_per_session", 0) or 0),
            "elaborate": int(getattr(s, "elaborate_budget_per_session", 0) or 0),
        }
        budget = budget_map.get(action, 0)
        if budget <= 0:
            return
        limiter = getattr(AIService, "_rate_limiter", None)  # type: ignore[attr-defined]
        if limiter is None:
            limiter = InMemoryRateLimiter(s.rate_limit_per_minute, getattr(s, "rate_limit_window_seconds", 60), s.ai_provider, s.model)
        if hasattr(limiter, "commit_action_usage"):
            try:
                limiter.commit_action_usage(session_id, action)  # type: ignore[attr-defined]
            except Exception:
                pass

    def _estimate_cost(self, action: str, provider: Optional[str], model: Optional[str]) -> float:
        # Heuristic estimates; prefer provider-reported costs when available.
        prov = (provider or "local").lower()
        if prov in {"none", "local"}:
            return 0.0
        # Simple per-action flat estimates by provider
        base = 0.0001
        if prov == "openai":
            base = 0.002 if action == "review" else 0.001
        elif prov == "anthropic":
            base = 0.0025 if action == "review" else 0.0012
        elif prov == "openrouter":
            base = 0.0015 if action == "review" else 0.0008
        return base

    def _commit_cost(self, actual_cost_usd: float) -> None:
        ledger = getattr(AIService, "_cost_ledger", None)  # type: ignore[attr-defined]
        if ledger is None:
            s = self.settings.load()
            AIService._cost_ledger = InMemoryCostLedger(float(getattr(s, "monthly_cost_cap_usd", 0.0) or 0.0))  # type: ignore[attr-defined]
            ledger = AIService._cost_ledger  # type: ignore[attr-defined]
        try:
            ledger.commit(actual_cost_usd)
        except Exception:
            # Do not fail user flows on cost commit errors
            pass
