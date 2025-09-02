"""
Ingest Markdown reading materials with YAML frontmatter into the database.
Idempotent upsert on ReadingMaterial by id.

Usage (Windows cmd.exe):
  .\.venv\Scripts\python.exe -m scripts.content_ingest_readings --path content\readings
Optional args:
  --publish-status published|draft (default respects frontmatter status)
  --dry-run (show what would be inserted/updated)
"""

import argparse
import os
import sys
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

# Ensure src is on path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.models.database import DatabaseConfig
from src.models.reading_materials import ReadingMaterial

try:
    import yaml
except ImportError:
    yaml = None

SEPARATOR = "---"


def parse_markdown_with_frontmatter(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    if not text.startswith(SEPARATOR):
        raise ValueError(f"File {path} missing YAML frontmatter starting with '---'")
    parts = text.split(SEPARATOR)
    if len(parts) < 3:
        raise ValueError(f"File {path} has malformed frontmatter")
    yaml_str = parts[1].strip()
    md_content = SEPARATOR.join(parts[2:]).lstrip("\n")
    if yaml is None:
        raise RuntimeError("PyYAML is required. Please pip install pyyaml.")
    meta = yaml.safe_load(yaml_str) or {}
    if not isinstance(meta, dict):
        raise ValueError(f"Frontmatter in {path} must be a YAML mapping")
    return {"meta": meta, "content": md_content}


def coerce_json_field(value, default):
    if value is None:
        return default() if callable(default) else default
    if isinstance(value, (list, dict)):
        return value
    # allow comma-separated strings for lists
    if isinstance(value, str) and isinstance(default, list):
        return [v.strip() for v in value.split(",") if v.strip()]
    return value


def upsert_material(session, meta: Dict[str, Any], content: str, override_status: Optional[str] = None) -> ReadingMaterial:
    required = ["id", "title", "content_type", "difficulty_level", "estimated_read_time"]
    missing = [k for k in required if meta.get(k) in (None, "")]
    if missing:
        raise ValueError(f"Missing required fields {missing} in material {meta.get('id')}")

    mat = session.query(ReadingMaterial).filter(ReadingMaterial.id == meta["id"]).first()
    is_new = mat is None
    if is_new:
        mat = ReadingMaterial(id=meta["id"])
        session.add(mat)

    # Simple field mapping
    mat.title = meta.get("title", mat.title)
    mat.subtitle = meta.get("subtitle")
    mat.author = meta.get("author", "DSATrain Team")
    mat.content_type = meta.get("content_type")
    mat.difficulty_level = meta.get("difficulty_level")
    mat.estimated_read_time = int(meta.get("estimated_read_time", 10))

    mat.concept_ids = coerce_json_field(meta.get("concept_ids"), [])
    mat.competency_ids = coerce_json_field(meta.get("competency_ids"), [])
    mat.prerequisite_materials = coerce_json_field(meta.get("prerequisite_materials"), [])
    mat.follow_up_materials = coerce_json_field(meta.get("follow_up_materials"), [])

    mat.target_personas = coerce_json_field(meta.get("target_personas"), [])
    mat.learning_objectives = coerce_json_field(meta.get("learning_objectives"), [])
    mat.skill_level_requirements = meta.get("skill_level_requirements") or {}

    mat.content_markdown = content
    # naive section extraction: H2s
    sections = []
    for line in content.splitlines():
        if line.startswith("## "):
            sections.append({"title": line[3:].strip()})
    mat.content_sections = sections

    mat.interactive_elements = meta.get("interactive_elements") or []
    mat.external_resources = meta.get("external_resources") or []

    mat.tags = coerce_json_field(meta.get("tags"), [])
    mat.keywords = coerce_json_field(meta.get("keywords"), [])
    mat.summary = meta.get("summary")
    mat.thumbnail_url = meta.get("thumbnail_url")

    # aggregates and counters left as-is unless new
    if is_new:
        mat.user_ratings = float(meta.get("user_ratings", 0.0))
        mat.total_ratings = int(meta.get("total_ratings", 0))
        mat.completion_rate = float(meta.get("completion_rate", 0.0))
        mat.effectiveness_score = float(meta.get("effectiveness_score", 0.0))
        mat.view_count = int(meta.get("view_count", 0))
        mat.completion_count = int(meta.get("completion_count", 0))
        mat.bookmark_count = int(meta.get("bookmark_count", 0))
        mat.share_count = int(meta.get("share_count", 0))

    status = override_status or meta.get("status") or "draft"
    mat.status = status
    mat.version = str(meta.get("version", mat.version or "1.0"))

    # dates: accept YYYY-MM-DD
    def parse_date(s):
        if not s:
            return None
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(s, fmt)
            except Exception:
                continue
        return None

    mat.last_reviewed = parse_date(meta.get("last_reviewed"))
    mat.published_at = parse_date(meta.get("published_at"))

    return mat


def ingest_path(path: str, override_status: Optional[str], dry_run: bool = False) -> Dict[str, Any]:
    # Use the current environment-configured DB explicitly to avoid stale globals
    db = DatabaseConfig(os.getenv("DSATRAIN_DATABASE_URL"))
    # Ensure tables exist for the active DB when flag is set (tests rely on this)
    if os.getenv("DSATRAIN_AUTO_CREATE_TABLES") == "1":
        # Import models to ensure SQLAlchemy sees all tables before create_all
        from src.models import reading_materials  # noqa: F401
        db.create_tables()
    session = db.get_session()
    created = 0
    updated = 0
    errors: List[Dict[str, Any]] = []

    try:
        for root, _, files in os.walk(path):
            for name in files:
                if not name.endswith(".md"):
                    continue
                full = os.path.join(root, name)
                try:
                    parsed = parse_markdown_with_frontmatter(full)
                    meta, content = parsed["meta"], parsed["content"]
                    existing = session.query(ReadingMaterial).filter(ReadingMaterial.id == meta.get("id")).first()
                    _ = upsert_material(session, meta, content, override_status)
                    if dry_run:
                        session.rollback()
                    else:
                        session.commit()
                    if existing is None:
                        created += 1
                    else:
                        updated += 1
                except Exception as e:
                    session.rollback()
                    errors.append({"file": full, "error": str(e)})
        return {"created": created, "updated": updated, "errors": errors}
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(description="Ingest reading materials from Markdown")
    parser.add_argument("--path", default=os.path.join("content", "readings"))
    parser.add_argument("--publish-status", dest="publish_status", default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    result = ingest_path(args.path, args.publish_status, args.dry_run)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
