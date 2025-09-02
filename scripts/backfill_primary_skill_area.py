"""Backfill primary_skill_area for existing problems.

Usage: Run once after migration 008. Uses the same mapping logic as skill_tree_api._determine_primary_skill_area.
"""
from src.models.database import DatabaseConfig, Problem
from src.api.skill_tree_api import _determine_primary_skill_area


def run():
    db = DatabaseConfig().get_session()
    try:
        problems = db.query(Problem).all()
        updated = 0
        for p in problems:
            try:
                if p.algorithm_tags and not p.primary_skill_area:
                    p.primary_skill_area = _determine_primary_skill_area(p.algorithm_tags)
                    updated += 1
            except Exception:
                # ignore malformed tags
                pass
        if updated:
            db.commit()
        print(f"Backfill complete. Updated {updated} rows.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
