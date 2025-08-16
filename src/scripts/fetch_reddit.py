from __future__ import annotations

import argparse
from pathlib import Path

from src.collectors.reddit_fetcher import RedditFetcher


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch Reddit behavioral interview posts")
    parser.add_argument("--query", default="google interview behavioral", help="Search query")
    parser.add_argument("--subreddit", default="cscareerquestions", help="Subreddit to search (optional)")
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--pages", type=int, default=1)
    args = parser.parse_args()

    data_dir = Path(__file__).resolve().parents[2] / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    RedditFetcher(data_dir).run_search(query=args.query, subreddit=args.subreddit, limit=args.limit, pages=args.pages)


if __name__ == "__main__":
    main() 