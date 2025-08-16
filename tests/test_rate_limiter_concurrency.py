import threading
from time import sleep

from src.services.rate_limit.in_memory import InMemoryRateLimiter
from src.services.rate_limit.common import RateLimitExceeded


def test_in_memory_rate_limiter_concurrent_window():
    # Limit 3 per 2-second window
    limiter = InMemoryRateLimiter(limit_per_minute=3, window_seconds=2, provider="local", model="test")

    successes = []
    failures = []

    def worker(idx):
        try:
            limiter.check_and_increment()
            successes.append(idx)
        except RateLimitExceeded:
            failures.append(idx)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # At most 3 should succeed within the window
    assert len(successes) <= 3
    assert len(failures) >= 7

    # After the window, more should succeed
    sleep(2.1)
    successes2 = 0
    for _ in range(3):
        try:
            limiter.check_and_increment()
            successes2 += 1
        except RateLimitExceeded:
            pass
    assert successes2 >= 1
