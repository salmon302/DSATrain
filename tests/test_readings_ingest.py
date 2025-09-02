import os
import json
from src.models.database import DatabaseConfig
from src.models.reading_materials import ReadingMaterial
from scripts.content_ingest_readings import ingest_path


def test_ingest_sample_readings(tmp_path, monkeypatch):
    # Use a file-backed SQLite DB so separate connections see the same data
    db_file = tmp_path / "test_readings.db"
    # Normalize Windows path to forward slashes for SQLAlchemy URL
    db_url = f"sqlite:///{str(db_file).replace('\\\\', '/').replace('\\', '/')}"
    monkeypatch.setenv("DSATRAIN_DATABASE_URL", db_url)
    monkeypatch.setenv("DSATRAIN_AUTO_CREATE_TABLES", "1")

    # Copy a couple of sample files into tmp dir
    samples_dir = tmp_path / "readings"
    samples_dir.mkdir()

    sample1 = samples_dir / "sample1.md"
    sample1.write_text("""---
id: sample-one
title: Sample One
author: Test
difficulty_level: beginner
content_type: guide
estimated_read_time: 5
status: published
---
# Sample One

Body
""", encoding="utf-8")

    sample2 = samples_dir / "sample2.md"
    sample2.write_text("""---
id: sample-two
title: Sample Two
content_type: tutorial
difficulty_level: intermediate
estimated_read_time: 7
status: published
---
# Sample Two

Body
""", encoding="utf-8")

    result = ingest_path(str(samples_dir), override_status=None, dry_run=False)
    assert result["errors"] == []
    assert result["created"] == 2

    # Verify rows exist
    db = DatabaseConfig(os.getenv("DSATRAIN_DATABASE_URL"))
    session = db.get_session()
    try:
        rows = session.query(ReadingMaterial).all()
        assert {r.id for r in rows} == {"sample-one", "sample-two"}
        for r in rows:
            assert r.content_markdown.startswith("# ")
            assert r.status == "published"
            assert r.estimated_read_time > 0
    finally:
        session.close()
