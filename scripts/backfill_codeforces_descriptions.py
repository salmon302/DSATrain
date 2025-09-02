from __future__ import annotations

"""
Backfill Codeforces problem descriptions by scraping problem pages.

Usage (from project root):
  - This script is intended to be run manually in the dev environment.
  - It finds Codeforces problems with missing/very short descriptions and scrapes
    the statement, examples, and constraints, then updates the DB.
"""

import re
from typing import List

from src.models.database import DatabaseConfig, Problem
from src.collectors.codeforces_scraper import scrape_problem


def parse_cf_platform_id(pid: str) -> tuple[str, str] | None:
    m = re.match(r"cf_(\d+)_([A-Za-z0-9]+)", pid)
    if not m:
        return None
    return m.group(1), m.group(2)


def main(limit: int = 50) -> None:
    db = DatabaseConfig()
    session = db.get_session()
    try:
        # Pick candidates: Codeforces problems where description is null or very short
        candidates: List[Problem] = (
            session.query(Problem)
            .filter(Problem.platform == "codeforces")
            .filter((Problem.description == None) | (Problem.description == "") | (Problem.description.op('length')() < 60))  # type: ignore
            .limit(limit)
            .all()
        )
        print(f"Found {len(candidates)} Codeforces problems to backfill.")

        updated = 0
        for p in candidates:
            parsed = parse_cf_platform_id(p.platform_id or p.id)
            if not parsed:
                print(f"Skipping {p.id}: cannot parse platform_id={p.platform_id}")
                continue
            contest_id, index = parsed
            try:
                data = scrape_problem(contest_id, index)
                p.description = data.get("description") or p.description
                if data.get("constraints"):
                    p.constraints = data["constraints"]
                if data.get("examples"):
                    p.examples = data["examples"]
                session.add(p)
                updated += 1
                print(f"Updated {p.id} ({p.title})")
            except Exception as e:
                print(f"Failed to scrape {p.id}: {e}")

        if updated:
            session.commit()
            print(f"Committed {updated} updates.")
        else:
            print("No updates to commit.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
