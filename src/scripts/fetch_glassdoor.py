from __future__ import annotations

import argparse
from pathlib import Path

from src.collectors.glassdoor_importer import GlassdoorImporter


def main() -> None:
    parser = argparse.ArgumentParser(description="Import Glassdoor interview data from local files")
    parser.add_argument("--data-dir", default=None, help="Override default data directory")
    args = parser.parse_args()

    if args.data_dir:
        data_dir = Path(args.data_dir)
    else:
        data_dir = Path(__file__).resolve().parents[2] / "data"
    
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print("Looking for Glassdoor files in:", data_dir / "raw" / "glassdoor")
    print("Expected files: google_interviews.json, tech_interviews.csv, apify_glassdoor_export.json")
    
    GlassdoorImporter(data_dir).run_import()


if __name__ == "__main__":
    main()
