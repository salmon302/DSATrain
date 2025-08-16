from __future__ import annotations

import argparse
from pathlib import Path

from src.collectors.academic_datasets_fetcher import AcademicDatasetsFetcher


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch academic code quality datasets")
    parser.add_argument("--data-dir", default=None, help="Override default data directory")
    args = parser.parse_args()

    if args.data_dir:
        data_dir = Path(args.data_dir)
    else:
        data_dir = Path(__file__).resolve().parents[2] / "data"
    
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print("Fetching academic code quality datasets...")
    print("This includes CodeComplex, py_ast, ml4code collection, and code metrics datasets.")
    print("Note: Some datasets require manual download due to academic licensing.")
    
    AcademicDatasetsFetcher(data_dir).run_acquisition()


if __name__ == "__main__":
    main()
