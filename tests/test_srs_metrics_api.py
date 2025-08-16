from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from src.api.main import app
from src.models.database import DatabaseConfig, ReviewHistory

client = TestClient(app)

def test_srs_metrics_has_daily_and_weekly():
    # Seed a few review history entries spanning days and weeks
    db = DatabaseConfig().get_session()
    try:
        now = datetime.now()
        samples = [
            ReviewHistory(problem_id="p1", outcome="good", timestamp=now - timedelta(days=0)),
            ReviewHistory(problem_id="p1", outcome="good", timestamp=now - timedelta(days=1)),
            ReviewHistory(problem_id="p2", outcome="hard", timestamp=now - timedelta(days=2)),
            ReviewHistory(problem_id="p3", outcome="again", timestamp=now - timedelta(days=9)),
            ReviewHistory(problem_id="p4", outcome="easy", timestamp=now - timedelta(days=16)),
        ]
        for s in samples:
            db.add(s)
        db.commit()
    finally:
        db.close()

    r = client.get("/srs/metrics", params={"days": 7})
    assert r.status_code == 200
    data = r.json()
    assert "daily" in data and isinstance(data["daily"], list)
    assert len(data["daily"]) >= 5
    assert "weekly" in data and isinstance(data["weekly"], list)
    # total_last_{days} is a dynamic key; ensure avg_per_day exists
    assert "avg_per_day" in data
