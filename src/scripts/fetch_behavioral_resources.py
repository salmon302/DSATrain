from __future__ import annotations

import argparse
from pathlib import Path

from src.collectors.behavioral_resources_fetcher import BehavioralResourcesFetcher


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch behavioral interview resources from universities")
    parser.add_argument("--data-dir", default=None, help="Override default data directory")
    args = parser.parse_args()

    if args.data_dir:
        data_dir = Path(args.data_dir)
    else:
        data_dir = Path(__file__).resolve().parents[2] / "data"
    
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print("Fetching behavioral interview resources from university career centers...")
    print("This includes behavioral question databases and STAR method rubrics.")
    
    BehavioralResourcesFetcher(data_dir).run_acquisition()


if __name__ == "__main__":
    main()
