import os
import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.models.database import DatabaseConfig
from scripts.content_ingest_readings import ingest_path


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_collections_endpoint_and_toc_fallback(tmp_path, monkeypatch, client):
    # Use sqlite file DB shared across sessions
    db_file = tmp_path / "readings_e2e.db"
    db_url = f"sqlite:///{str(db_file).replace('\\\\', '/').replace('\\', '/')}"
    monkeypatch.setenv("DSATRAIN_DATABASE_URL", db_url)
    monkeypatch.setenv("DSATRAIN_AUTO_CREATE_TABLES", "1")

    # Create a markdown that lacks content_sections in frontmatter to force fallback
    md_dir = tmp_path / "md"
    md_dir.mkdir()
    md = md_dir / "toc_fallback.md"
    md.write_text(
        """---
id: toc-fallback
title: TOC Fallback Demo
content_type: guide
difficulty_level: beginner
estimated_read_time: 3
status: published
---
# Title

## Section One
text

## Section Two
text
""",
        encoding="utf-8",
    )

    result = ingest_path(str(md_dir), override_status=None, dry_run=False)
    assert result["errors"] == []

    # Create a tiny collection with this single item
    from src.models.reading_materials import ContentCollection
    db = DatabaseConfig(db_url)
    s = db.get_session()
    try:
        col = ContentCollection(id="test-col", name="Test Col", description="", collection_type="topic_guide")
        col.material_ids = ["toc-fallback"]
        s.add(col)
        s.commit()
    finally:
        s.close()

    # Use the injected TestClient fixture (do not call it directly)
    c = client
    r = c.get("/reading-materials/collections")
    assert r.status_code == 200
    data = r.json()
    assert any(c["id"] == "test-col" for c in data.get("collections", []))

    # Fetch material with content; expect content_sections to be present or parseable from markdown (handled in frontend)
    r2 = c.get("/reading-materials/material/toc-fallback", params={"include_content": True})
    assert r2.status_code == 200
    mat = r2.json()
    assert mat["content_markdown"].startswith("# Title")
    # Backend stores content_sections based on H2 extraction during ingest; verify it captured sections
    assert any(s.get("title") == "Section One" for s in (mat.get("content_sections") or []))


