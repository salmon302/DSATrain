from __future__ import annotations

import argparse
from pathlib import Path

from src.collectors.kaggle_leetcode_importer import KaggleLeetCodeImporter
from src.collectors.hackerrank_interview_kit_importer import HackerRankInterviewKitImporter
from src.collectors.codecomplex_importer import CodeComplexImporter
from src.processors.standardizer import DatasetStandardizer
from src.models.database import DatabaseConfig


def main() -> None:
	parser = argparse.ArgumentParser(description="Import external datasets and unify into DB")
	parser.add_argument("--data-dir", default=str(Path(__file__).resolve().parents[2] / "data"))
	parser.add_argument("--no-db", action="store_true", help="Do not upsert into DB; only write unified files")
	args = parser.parse_args()

	data_dir = Path(args.data_dir)
	data_dir.mkdir(parents=True, exist_ok=True)

	# Ensure DB exists
	db = DatabaseConfig()
	db.create_tables()

	# Load external datasets
	kaggle = KaggleLeetCodeImporter(data_dir)
	hackrank = HackerRankInterviewKitImporter(data_dir)
	cc = CodeComplexImporter(data_dir)

	problems_sources = [
		kaggle.load_problems(),
		hackrank.load_problems(),
	]

	solution_sources = [
		kaggle.load_solutions(),
		hackrank.load_solutions(),
		cc.load_samples(),  # Treated as generic code samples/solutions
	]

	standardizer = DatasetStandardizer(data_dir=data_dir, write_unified_files=True, upsert_to_db=(not args.no_db))
	stats = standardizer.run(problems_sources, solution_sources)

	print(f"Imported problems: {stats.get('problems', 0)} (created {stats.get('problems_created',0)}, updated {stats.get('problems_updated',0)})")
	print(f"Imported solutions: {stats.get('solutions', 0)} (created {stats.get('solutions_created',0)}, updated {stats.get('solutions_updated',0)})")


if __name__ == "__main__":
	main() 