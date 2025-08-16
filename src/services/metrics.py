from __future__ import annotations

from collections import defaultdict
from typing import Dict
import threading
import logging

logger = logging.getLogger(__name__)


class Metrics:
    """Minimal in-process counter store with logging hooks."""

    _lock = threading.Lock()
    _counters: Dict[str, int] = defaultdict(int)

    @classmethod
    def incr(cls, name: str, amount: int = 1) -> None:
        with cls._lock:
            cls._counters[name] = cls._counters.get(name, 0) + amount
        # Lightweight log for visibility during development/tests
        logger.debug("metric %s += %d -> %d", name, amount, cls._counters[name])

    @classmethod
    def get(cls, name: str) -> int:
        with cls._lock:
            return int(cls._counters.get(name, 0))

    @classmethod
    def snapshot(cls) -> Dict[str, int]:
        with cls._lock:
            return dict(cls._counters)
