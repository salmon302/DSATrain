import os
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.models.database import DatabaseConfig
from src.models.reading_materials import ReadingMaterial, UserReadingProgress, MaterialRecommendation
from scripts.content_ingest_readings import ingest_path


@pytest.fixture(scope="module")
def client():
    os.environ.setdefault("DSATRAIN_AUTO_CREATE_TABLES", "1")
    return TestClient(app)


def _normalize_sqlite_url(path: str) -> str:
    return f"sqlite:///{path.replace('\\\\', '/').replace('\\', '/')}"


def test_readings_end_to_end_flow(tmp_path, monkeypatch, client):
    # Use isolated sqlite file DB
    db_file = tmp_path / "readings_flow.db"
    monkeypatch.setenv("DSATRAIN_DATABASE_URL", _normalize_sqlite_url(str(db_file)))
    monkeypatch.setenv("DSATRAIN_AUTO_CREATE_TABLES", "1")

    # Create a minimal published reading via ingestion
    md_dir = tmp_path / "md"
    md_dir.mkdir()
    md = md_dir / "flow.md"
    md.write_text(
        """---
id: flow-demo
title: Flow Demo
subtitle: End-to-end coverage
content_type: guide
difficulty_level: beginner
estimated_read_time: 4
status: published
summary: Demo material
---
# Flow Demo

## Part A
Text

## Part B
More
""",
        encoding="utf-8",
    )

    result = ingest_path(str(md_dir), override_status=None, dry_run=False)
    assert result["errors"] == []

    # Verify search with filters and personalization
    r = client.get(
        "/reading-materials/search",
        params={
            "query": "Flow",
            "content_type": "guide",
            "difficulty_level": "beginner",
            "user_id": "default_user",
        },
    )
    assert r.status_code == 200, r.text
    data = r.json()
    mats = data.get("materials", [])
    assert any(m["id"] == "flow-demo" for m in mats)

    # Fetch material and ensure content and view count updates
    r2 = client.get(
        "/reading-materials/material/flow-demo",
        params={"user_id": "default_user", "include_content": True},
    )
    assert r2.status_code == 200
    mat = r2.json()
    assert mat["title"] == "Flow Demo"
    assert mat.get("content_markdown", "").startswith("# Flow Demo")

    # Update progress and verify completion triggers completion_count increment on 100%
    r3 = client.post(
        "/reading-materials/material/flow-demo/progress",
        params={"user_id": "default_user"},
        json={
            "progress_percentage": 45.0,
            "reading_time_seconds": 30,
            "sections_read": ["part-a"],
        },
    )
    assert r3.status_code == 200, r3.text
    prog = r3.json()["progress"]
    assert prog["progress_percentage"] == 45.0

    # Complete it
    r4 = client.post(
        "/reading-materials/material/flow-demo/progress",
        params={"user_id": "default_user"},
        json={
            "progress_percentage": 100.0,
            "reading_time_seconds": 120,
        },
    )
    assert r4.status_code == 200

    # Rate material (create) then update rating path
    r5 = client.post(
        "/reading-materials/material/flow-demo/rating",
        params={"user_id": "default_user"},
        json={"user_rating": 4, "difficulty_rating": 2, "usefulness_rating": 4, "would_recommend": True},
    )
    assert r5.status_code == 200
    first_rating = r5.json()
    assert first_rating["total_ratings"] >= 1

    r6 = client.post(
        "/reading-materials/material/flow-demo/rating",
        params={"user_id": "default_user"},
        json={"user_rating": 5},
    )
    assert r6.status_code == 200

    # Recommendations: create a recommendation row then fetch and then dismiss
    db = DatabaseConfig(os.getenv("DSATRAIN_DATABASE_URL")).get_session()
    try:
        rec = MaterialRecommendation(
            user_id="default_user",
            material_id="flow-demo",
            recommendation_type="general",
            recommendation_reason="demo",
            recommendation_score=0.9,
            priority_level=1,
            recommended_at=datetime.now(),
        )
        db.add(rec)
        db.commit()
        rec_id = rec.id
    finally:
        db.close()

    r7 = client.get("/reading-materials/recommendations/default_user", params={"context": "general"})
    assert r7.status_code == 200
    payload = r7.json()
    assert any(m.get("id") == "flow-demo" for m in payload.get("recommendations", []))

    # Dismiss the recommendation
    r8 = client.post(f"/reading-materials/recommendation/{rec_id}/dismiss", params={"reason": "seen"})
    assert r8.status_code == 200

    # Analytics (expect no data message rather than error)
    r9 = client.get("/reading-materials/analytics/flow-demo", params={"period": "last_30_days"})
    assert r9.status_code == 200
    anal = r9.json()
    assert anal.get("material_id") == "flow-demo"
    # may be None with message on fresh DB
    assert "analytics" in anal
