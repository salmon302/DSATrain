import math
from datetime import datetime, timedelta

from src.models.database import DatabaseConfig, ReviewHistory
from src.services.srs_service import SRSService


def test_srs_service_metrics_dynamic_key_and_shape():
    # Use in-memory DB which auto-creates tables per DatabaseConfig implementation
    db = DatabaseConfig('sqlite:///:memory:').get_session()
    try:
        now = datetime.now()
        # Seed reviews across last 10 days
        samples = [
            ReviewHistory(problem_id=f"p{i}", outcome="good", timestamp=now - timedelta(days=i))
            for i in range(0, 10)
        ]
        for s in samples:
            db.add(s)
        db.commit()

        svc = SRSService(db)
        days = 7
        metrics = svc.metrics(days=days)

        # Shape checks
        assert isinstance(metrics, dict)
        assert "daily" in metrics and isinstance(metrics["daily"], list)
        assert "weekly" in metrics and isinstance(metrics["weekly"], list)
        assert "avg_per_day" in metrics

        # Dynamic key must exist for the provided window
        total_key = f"total_last_{days}"
        assert total_key in metrics

        # Totals should match sum of daily counts in window
        window_total = sum(d.get("reviews", 0) for d in metrics["daily"])  # daily is exactly days+1 entries
        assert metrics[total_key] == window_total

        # avg_per_day should be consistent
        denom = max(len(metrics["daily"]), 1)
        expected_avg = round(window_total / denom, 2)
        assert math.isclose(metrics["avg_per_day"], expected_avg, rel_tol=0, abs_tol=1e-9)
    finally:
        db.close()
