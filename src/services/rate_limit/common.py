from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


class RateLimitExceeded(Exception):
    def __init__(self, message: str, retry_after_seconds: Optional[int] = None):
        super().__init__(message)
        self.retry_after_seconds = retry_after_seconds


class BudgetExceeded(Exception):
    pass


@dataclass
class RateStatus:
    used: int
    limit: int
    window_seconds: int
    reset_seconds: Optional[int]
