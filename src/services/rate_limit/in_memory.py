from __future__ import annotations

import time
import threading
from collections import deque, defaultdict
from typing import Optional, Dict, Tuple

from .common import RateLimitExceeded, BudgetExceeded, RateStatus


class InMemoryRateLimiter:
    """Process-local sliding window limiter and per-session budgets."""

    _requests = deque()  # timestamps (monotonic seconds)
    _rl_key: Optional[Tuple] = None
    _hints_by_session: Dict[str, int] = defaultdict(int)
    _lock = threading.RLock()

    def __init__(self, limit_per_minute: int, window_seconds: int, provider: Optional[str], model: Optional[str]):
        self.limit = int(limit_per_minute or 0)
        self.window = int(window_seconds or 60)
        self.key = (provider, model, self.limit, self.window)

    def check_and_increment(self):
        now = time.monotonic()
        with InMemoryRateLimiter._lock:
            if InMemoryRateLimiter._rl_key != self.key:
                InMemoryRateLimiter._requests = deque()
                InMemoryRateLimiter._rl_key = self.key
            q = InMemoryRateLimiter._requests
            # Evict outside-window timestamps
            while q and (now - q[0]) > self.window:
                q.popleft()
            if self.limit > 0 and len(q) >= self.limit:
                oldest = q[0]
                retry_after = max(1, int(self.window - (now - oldest))) if q else 1
                raise RateLimitExceeded("Rate limit exceeded. Try again later.", retry_after)
            q.append(now)

    def status(self) -> RateStatus:
        now = time.monotonic()
        with InMemoryRateLimiter._lock:
            q = InMemoryRateLimiter._requests
            used = 0
            reset = None
            if q:
                oldest_in_window = None
                for t in q:
                    age = now - t
                    if age <= self.window:
                        used += 1
                        if oldest_in_window is None:
                            oldest_in_window = t
                if oldest_in_window is not None:
                    reset = max(0, int(self.window - (now - oldest_in_window)))
            return RateStatus(used=used, limit=self.limit, window_seconds=self.window, reset_seconds=reset)

    def enforce_and_count_hint(self, session_id: Optional[str], budget_per_session: int):
        if not session_id or int(budget_per_session or 0) <= 0:
            return
        with InMemoryRateLimiter._lock:
            used = InMemoryRateLimiter._hints_by_session.get(session_id, 0)
            if used >= budget_per_session:
                raise BudgetExceeded("Hint budget exceeded for this session.")
            InMemoryRateLimiter._hints_by_session[session_id] = used + 1

    # New: split-phase budget control so we only decrement on success
    def check_hint_budget(self, session_id: Optional[str], budget_per_session: int) -> None:
        """Raise if this request would exceed the session budget; do not mutate state."""
        if not session_id or int(budget_per_session or 0) <= 0:
            return
        with InMemoryRateLimiter._lock:
            used = InMemoryRateLimiter._hints_by_session.get(session_id, 0)
            if used >= int(budget_per_session):
                raise BudgetExceeded("Hint budget exceeded for this session.")

    def commit_hint_usage(self, session_id: Optional[str]) -> None:
        """Commit one hint usage for the session after successful generation."""
        if not session_id:
            return
        with InMemoryRateLimiter._lock:
            InMemoryRateLimiter._hints_by_session[session_id] = InMemoryRateLimiter._hints_by_session.get(session_id, 0) + 1

    def get_hint_usage(self, session_id: Optional[str]) -> int:
        if not session_id:
            return 0
        with InMemoryRateLimiter._lock:
            return int(InMemoryRateLimiter._hints_by_session.get(session_id, 0))

    def reset(self, session_id: Optional[str] = None, reset_global: bool = True):
        with InMemoryRateLimiter._lock:
            if reset_global:
                InMemoryRateLimiter._requests = deque()
            if session_id:
                InMemoryRateLimiter._hints_by_session.pop(session_id, None)

