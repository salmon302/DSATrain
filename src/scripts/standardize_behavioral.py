from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.processors.behavioral_standardizer import BehavioralStandardizer


def main() -> None:
    parser = argparse.ArgumentParser(description="Standardize and unify behavioral data from Reddit and Glassdoor")
    parser.add_argument("--data-dir", default=None, help="Override default data directory")
    args = parser.parse_args()

    if args.data_dir:
        data_dir = Path(args.data_dir)
    else:
        data_dir = Path(__file__).resolve().parents[2] / "data"
    
    standardizer = BehavioralStandardizer(data_dir)
    
    # Load Reddit data
    reddit_dir = data_dir / "raw" / "reddit"
    reddit_items = []
    if reddit_dir.exists():
        for file in reddit_dir.glob("*.json"):
            try:
                with file.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    items = data.get("items", [])
                    reddit_items.extend(items)
            except Exception as e:
                print(f"Warning: could not read {file}: {e}")
    
    # Load Glassdoor data  
    glassdoor_dir = data_dir / "raw" / "glassdoor"
    glassdoor_items = []
    if glassdoor_dir.exists():
        for file in glassdoor_dir.glob("*.json"):
            try:
                with file.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    items = data.get("items", [])
                    glassdoor_items.extend(items)
            except Exception as e:
                print(f"Warning: could not read {file}: {e}")
    
    # Standardize and combine
    unified_reddit = standardizer.unify_reddit_items(reddit_items)
    unified_glassdoor = standardizer.unify_glassdoor_items(glassdoor_items)
    
    all_entries = unified_reddit + unified_glassdoor
    
    # Write unified file
    out_path = standardizer.write_unified(all_entries)
    
    print(f"Standardized {len(unified_reddit)} Reddit items and {len(unified_glassdoor)} Glassdoor items")
    print(f"Unified behavioral data written to: {out_path}")
    print(f"Total entries: {len(all_entries)}")


if __name__ == "__main__":
    main()
