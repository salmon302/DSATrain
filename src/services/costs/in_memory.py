from __future__ import annotations

import threading
from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Optional, Dict


@dataclass
class CostStatus:
    month_key: str
    used_usd: float
    cap_usd: float


class InMemoryCostLedger:
    """Simple in-memory monthly cost tracker.

    Notes:
    - Process-local only. For multi-process deployments, use a shared store instead.
    - Thread safe within a process.
    - Tracks a single global cost bucket per month (not per-user).
    """

    _lock = threading.RLock()
    _usage_by_month: Dict[str, float] = {}

    def __init__(self, monthly_cap_usd: float):
        self.monthly_cap_usd = float(monthly_cap_usd or 0.0)

    def _month_key(self) -> str:
        # Use timezone-aware UTC timestamp for month key
        now = datetime.now(UTC)
        return f"{now.year:04d}-{now.month:02d}"

    def status(self) -> CostStatus:
        with InMemoryCostLedger._lock:
            key = self._month_key()
            used = float(InMemoryCostLedger._usage_by_month.get(key, 0.0))
            return CostStatus(month_key=key, used_usd=used, cap_usd=self.monthly_cap_usd)

    def can_spend(self, estimated_cost_usd: float) -> bool:
        with InMemoryCostLedger._lock:
            key = self._month_key()
            used = float(InMemoryCostLedger._usage_by_month.get(key, 0.0))
            return (used + float(estimated_cost_usd or 0.0)) <= self.monthly_cap_usd if self.monthly_cap_usd > 0 else True

    def precheck(self, estimated_cost_usd: float) -> None:
        if self.monthly_cap_usd <= 0:
            return
        if not self.can_spend(estimated_cost_usd):
            raise Exception("Monthly AI cost cap exceeded.")

    def commit(self, actual_cost_usd: float) -> None:
        if float(actual_cost_usd or 0.0) <= 0:
            return
        with InMemoryCostLedger._lock:
            key = self._month_key()
            current = float(InMemoryCostLedger._usage_by_month.get(key, 0.0))
            InMemoryCostLedger._usage_by_month[key] = round(current + float(actual_cost_usd), 6)

    def reset_month(self, month_key: Optional[str] = None) -> None:
        with InMemoryCostLedger._lock:
            key = month_key or self._month_key()
            InMemoryCostLedger._usage_by_month.pop(key, None)


