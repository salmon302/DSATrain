from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class KaggleLeetCodeImporter:
    data_dir: Path

    @property
    def base_path(self) -> Path:
        return self.data_dir / "raw" / "kaggle_leetcode"

    def _read_csv(self, file_path: Path) -> List[Dict[str, str]]:
        if not file_path.exists():
            return []
        rows: List[Dict[str, str]] = []
        with file_path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append({k: (v or "").strip() for k, v in row.items()})
        return rows

    def load_problems(self) -> List[Dict]:
        problems_csv = self.base_path / "problems.csv"
        rows = self._read_csv(problems_csv)
        problems: List[Dict] = []
        for r in rows:
            platform_id = r.get("question_id") or r.get("id") or ""
            title = r.get("title") or r.get("question_title") or ""
            difficulty = (r.get("difficulty") or "").capitalize() or "Medium"
            description = r.get("content") or r.get("description") or title
            tags = [t.strip().lower().replace(" ", "_") for t in (r.get("tags") or "").split(";") if t.strip()]
            companies = [c.strip() for c in (r.get("companies") or r.get("company_tags") or "").split(";") if c.strip()]
            acceptance = r.get("acceptance_rate") or r.get("acceptance") or ""
            try:
                acceptance_rate = float(acceptance.replace("%", "")) if acceptance else None
            except ValueError:
                acceptance_rate = None

            problems.append({
                "id": f"leetcode_{platform_id}" if platform_id else f"leetcode_{title.lower().replace(' ', '_')}",
                "platform": "leetcode",
                "platform_id": platform_id or title,
                "title": title,
                "difficulty": difficulty,
                "description": description,
                "algorithm_tags": tags,
                "data_structures": None,
                "constraints": None,
                "companies": companies,
                "acceptance_rate": acceptance_rate,
                "frequency_score": None,
                "collected_at": datetime.now().isoformat()
            })
        return problems

    def load_solutions(self) -> List[Dict]:
        solutions_csv = self.base_path / "solutions.csv"
        rows = self._read_csv(solutions_csv)
        solutions: List[Dict] = []
        for r in rows:
            problem_slug = r.get("question_slug") or r.get("title_slug") or r.get("title") or ""
            problem_id = r.get("question_id") or ""
            code = r.get("code") or r.get("solution") or ""
            language = (r.get("language") or "python").lower()
            approach = (r.get("approach") or r.get("method") or "").lower().replace(" ", "_") or "unknown"
            time_complexity = r.get("time_complexity") or ""
            space_complexity = r.get("space_complexity") or ""
            explanation = r.get("explanation") or r.get("notes") or None

            if not code:
                continue

            pid = f"leetcode_{problem_id}" if problem_id else f"leetcode_{problem_slug or 'unknown'}"
            solutions.append({
                "id": f"{pid}_sol_{len(solutions)+1}",
                "problem_id": pid,
                "code": code,
                "language": language,
                "approach_type": approach,
                "algorithm_tags": [approach] if approach else [],
                "time_complexity": time_complexity,
                "space_complexity": space_complexity,
                "explanation": explanation,
                "overall_quality_score": None,
                "collected_at": datetime.now().isoformat()
            })
        return solutions 