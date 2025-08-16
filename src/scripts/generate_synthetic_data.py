from __future__ import annotations

import argparse
from pathlib import Path

from src.collectors.synthetic_data_generator import SyntheticDataGenerator


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic interview data")
    parser.add_argument("--data-dir", default=None, help="Override default data directory")
    parser.add_argument("--behavioral", type=int, default=100, help="Number of behavioral scenarios to generate")
    parser.add_argument("--coding", type=int, default=50, help="Number of coding problems to generate")
    parser.add_argument("--system-design", type=int, default=20, help="Number of system design problems to generate")
    args = parser.parse_args()

    if args.data_dir:
        data_dir = Path(args.data_dir)
    else:
        data_dir = Path(__file__).resolve().parents[2] / "data"
    
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print("Generating synthetic interview data...")
    print(f"Behavioral scenarios: {args.behavioral}")
    print(f"Coding problems: {args.coding}")
    print(f"System design problems: {args.system_design}")
    print("\nThis creates proprietary training data using research-based templates.")
    
    generator = SyntheticDataGenerator(data_dir)
    generator.run_generation(
        behavioral_count=args.behavioral,
        coding_count=args.coding,
        system_design_count=args.system_design
    )


if __name__ == "__main__":
    main()
