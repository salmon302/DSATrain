from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List


@dataclass
class HackerRankInterviewKitImporter:
    data_dir: Path

    @property
    def base_path(self) -> Path:
        return self.data_dir / "raw" / "hackerrank" / "interview_kit"

    def _read_json(self, file_path: Path) -> List[Dict]:
        if not file_path.exists():
            return []
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                data = data.get("problems", [])
            return data if isinstance(data, list) else []

    def load_problems(self) -> List[Dict]:
        problems_file = self.base_path / "problems.json"
        items = self._read_json(problems_file)
        problems: List[Dict] = []
        for it in items:
            pid = it.get("id") or it.get("slug") or it.get("title") or ""
            difficulty = (it.get("difficulty") or "Medium").capitalize()
            topic_tags = [t.lower().replace(" ", "_") for t in it.get("topics", [])]
            problems.append({
                "id": f"hackerrank_{pid}",
                "platform": "hackerrank",
                "platform_id": str(pid),
                "title": it.get("title") or str(pid),
                "difficulty": difficulty,
                "description": it.get("description") or it.get("statement") or it.get("title") or "",
                "algorithm_tags": topic_tags,
                "data_structures": None,
                "constraints": it.get("constraints"),
                "companies": it.get("companies") or [],
                "acceptance_rate": None,
                "frequency_score": None,
                "collected_at": datetime.now().isoformat()
            })
        return problems

    def load_solutions(self) -> List[Dict]:
        # If the JSON includes editorial solutions, transform them
        editorials_file = self.base_path / "editorials.json"
        items = self._read_json(editorials_file)
        solutions: List[Dict] = []
        for it in items:
            pid = it.get("problem_id") or it.get("slug") or ""
            pid_std = f"hackerrank_{pid}"
            for sol in it.get("solutions", []) or []:
                code = sol.get("code") or ""
                if not code:
                    continue
                language = (sol.get("language") or "python").lower()
                approach = (sol.get("approach") or sol.get("method") or "").lower().replace(" ", "_") or "editorial"
                solutions.append({
                    "id": f"{pid_std}_sol_{len(solutions)+1}",
                    "problem_id": pid_std,
                    "code": code,
                    "language": language,
                    "approach_type": approach,
                    "algorithm_tags": [approach] if approach else [],
                    "time_complexity": sol.get("time_complexity") or "",
                    "space_complexity": sol.get("space_complexity") or "",
                    "explanation": sol.get("explanation") or None,
                    "overall_quality_score": None,
                    "collected_at": datetime.now().isoformat()
                })
        return solutions 