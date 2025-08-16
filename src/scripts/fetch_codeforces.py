from __future__ import annotations

import argparse
from pathlib import Path

from src.collectors.codeforces_fetcher import CodeforcesFetcher


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch Codeforces data")
    sub = parser.add_subparsers(dest="cmd", required=False)
    sub.add_parser("problemset")
    p_contests = sub.add_parser("contests")
    p_contests.add_argument("--gym", action="store_true")
    p_sub = sub.add_parser("submissions")
    p_sub.add_argument("handle", help="Codeforces handle")
    p_sub.add_argument("--page-size", type=int, default=100)
    p_sub.add_argument("--max-pages", type=int, default=200)

    args = parser.parse_args()

    data_dir = Path(__file__).resolve().parents[2] / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    fetcher = CodeforcesFetcher(data_dir)

    if args.cmd == "contests":
        fetcher.save_contests(gym=bool(getattr(args, "gym", False)))
    elif args.cmd == "submissions":
        fetcher.save_user_submissions(handle=args.handle, page_size=args.page_size, max_pages=args.max_pages)
    else:
        fetcher.save_problemset()


if __name__ == "__main__":
    main() 