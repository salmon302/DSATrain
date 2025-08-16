from __future__ import annotations

import argparse
from pathlib import Path

from src.collectors.system_design_fetcher import SystemDesignFetcher


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch system design interview scenarios")
    parser.add_argument("--data-dir", default=None, help="Override default data directory")
    args = parser.parse_args()

    if args.data_dir:
        data_dir = Path(args.data_dir)
    else:
        data_dir = Path(__file__).resolve().parents[2] / "data"
    
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print("Fetching system design interview scenarios...")
    print("This includes Reddit's famous 45 questions, GitHub collections, and expanded scenarios.")
    
    SystemDesignFetcher(data_dir).run_acquisition()


if __name__ == "__main__":
    main()
