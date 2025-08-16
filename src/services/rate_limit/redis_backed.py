from __future__ import annotations

import os
import time
from typing import Optional

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover - if redis not installed, module still importable
    redis = None  # type: ignore

from .common import RateLimitExceeded, BudgetExceeded, RateStatus


class RedisRateLimiter:
    """Redis-backed sliding window limiter and per-session budgets.

    Uses simple key patterns and expirations. Designed for horizontal scalability.
    """

    def __init__(self, limit_per_minute: int, window_seconds: int, provider: Optional[str], model: Optional[str], redis_url: Optional[str] = None):
        if redis is None:
            raise RuntimeError("redis-py is not installed; cannot enable Redis rate limiting")
        url = redis_url or os.getenv("DSATRAIN_REDIS_URL", "redis://localhost:6379/0")
        self.r = redis.StrictRedis.from_url(url)  # type: ignore[attr-defined]
        self.limit = int(limit_per_minute or 0)
        self.window = int(window_seconds or 60)
        prov = provider or "none"
        mdl = model or "default"
        self.bucket_key = f"dsatrain:rl:{prov}:{mdl}"
        self.hint_prefix = "dsatrain:hints:"

    def check_and_increment(self):
        now = int(time.time())
        pipe = self.r.pipeline()
        # Use a sorted set for timestamps within the window
        zkey = f"{self.bucket_key}:z"
        pipe.zremrangebyscore(zkey, 0, now - self.window)
        pipe.zcard(zkey)
        res = pipe.execute()
        used = int(res[1]) if len(res) >= 2 else 0
        if self.limit > 0 and used >= self.limit:
            # Compute retry-after as time until next item expires (approximate)
            oldest = self.r.zrange(zkey, 0, 0, withscores=True)
            retry_after = 1
            if oldest:
                oldest_ts = int(oldest[0][1])
                retry_after = max(1, (oldest_ts + self.window) - now)
            raise RateLimitExceeded("Rate limit exceeded. Try again later.", retry_after)
        # Record current request
        pipe = self.r.pipeline()
        pipe.zadd(zkey, {str(now): now})
        pipe.expire(zkey, self.window)
        pipe.execute()

    def status(self) -> RateStatus:
        now = int(time.time())
        zkey = f"{self.bucket_key}:z"
        self.r.zremrangebyscore(zkey, 0, now - self.window)
        used = int(self.r.zcard(zkey))
        oldest = self.r.zrange(zkey, 0, 0, withscores=True)
        reset = None
        if oldest:
            oldest_ts = int(oldest[0][1])
            reset = max(0, (oldest_ts + self.window) - now)
        return RateStatus(used=used, limit=self.limit, window_seconds=self.window, reset_seconds=reset)

    def enforce_and_count_hint(self, session_id: Optional[str], budget_per_session: int):
        if not session_id or int(budget_per_session or 0) <= 0:
            return
        key = f"{self.hint_prefix}{session_id}"
        used = self.r.get(key)
        count = int(used) if used else 0
        if count >= budget_per_session:
            raise BudgetExceeded("Hint budget exceeded for this session.")
        pipe = self.r.pipeline()
        pipe.incr(key)
        # Set a long TTL (e.g., 7 days) so session budgets are eventually cleaned
        pipe.expire(key, 7 * 24 * 3600)
        pipe.execute()

    # New: split-phase budget control so we only decrement on success
    def check_hint_budget(self, session_id: Optional[str], budget_per_session: int) -> None:
        if not session_id or int(budget_per_session or 0) <= 0:
            return
        key = f"{self.hint_prefix}{session_id}"
        used = self.r.get(key)
        count = int(used) if used else 0
        if count >= int(budget_per_session):
            raise BudgetExceeded("Hint budget exceeded for this session.")

    def commit_hint_usage(self, session_id: Optional[str]) -> None:
        if not session_id:
            return
        key = f"{self.hint_prefix}{session_id}"
        pipe = self.r.pipeline()
        pipe.incr(key)
        pipe.expire(key, 7 * 24 * 3600)
        pipe.execute()

    def get_hint_usage(self, session_id: Optional[str]) -> int:
        if not session_id:
            return 0
        key = f"{self.hint_prefix}{session_id}"
        used = self.r.get(key)
        return int(used) if used else 0

    def reset(self, session_id: Optional[str] = None, reset_global: bool = True):
        if reset_global:
            # Delete bucket keys (zset)
            zkey = f"{self.bucket_key}:z"
            try:
                self.r.delete(zkey)
            except Exception:
                pass
        if session_id:
            try:
                self.r.delete(f"{self.hint_prefix}{session_id}")
            except Exception:
                pass
