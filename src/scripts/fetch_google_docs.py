from __future__ import annotations

import argparse
from pathlib import Path

from src.collectors.google_docs_fetcher import GoogleDocsFetcher


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch Google's official hiring and engineering documentation")
    parser.add_argument("--data-dir", default=None, help="Override default data directory")
    args = parser.parse_args()

    if args.data_dir:
        data_dir = Path(args.data_dir)
    else:
        data_dir = Path(__file__).resolve().parents[2] / "data"
    
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print("Fetching Google's official documentation...")
    print("This includes hiring process, code review guidelines, and engineering practices.")
    
    GoogleDocsFetcher(data_dir).run_acquisition()


if __name__ == "__main__":
    main()
