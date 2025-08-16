from __future__ import annotations

import argparse
import os
from pathlib import Path

from src.collectors.github_fetcher import GitHubFetcher


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch GitHub code search results")
    parser.add_argument("query", nargs="?", default=None, help="Search query, e.g. 'leetcode two sum solution' or 'codeforces 1A solution'")
    parser.add_argument("--language", default=None, help="Optional language filter, e.g. python, cpp")
    parser.add_argument("--per-page", type=int, default=50)
    parser.add_argument("--pages", type=int, default=2)
    args = parser.parse_args()

    query = args.query or os.environ.get("GITHUB_QUERY") or "leetcode two sum solution"

    data_dir = Path(__file__).resolve().parents[2] / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    GitHubFetcher(data_dir).run_search(query=query, language=args.language, per_page=args.per_page, pages=args.pages)


if __name__ == "__main__":
    main() 