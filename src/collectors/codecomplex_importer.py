from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List


@dataclass
class CodeComplexImporter:
    data_dir: Path

    @property
    def base_path(self) -> Path:
        return self.data_dir / "raw" / "academic_datasets" / "codecomplex"

    def _read_csv_safe(self, path: Path) -> List[Dict[str, str]]:
        if not path.exists():
            return []
        rows: List[Dict[str, str]] = []
        with path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append({k: (v or "").strip() for k, v in row.items()})
        return rows

    def _read_json_safe(self, path: Path) -> List[Dict]:
        if not path.exists():
            return []
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []

    def load_samples(self) -> List[Dict]:
        # Expected formats:
        # - codecomplex_python.csv with columns: id,language,code,time_complexity,space_complexity
        # - or codecomplex.json with similar fields
        csv_rows = self._read_csv_safe(self.base_path / "codecomplex_python.csv")
        csv_rows += self._read_csv_safe(self.base_path / "codecomplex_java.csv")
        json_rows = self._read_json_safe(self.base_path / "codecomplex.json")

        rows: List[Dict] = []
        for r in csv_rows:
            rows.append({
                "id": r.get("id") or f"codecomplex_{len(rows)+1}",
                "problem_id": r.get("problem_id") or "",
                "language": (r.get("language") or "python").lower(),
                "code": r.get("code") or "",
                "time_complexity": r.get("time_complexity") or "",
                "space_complexity": r.get("space_complexity") or "",
                "collected_at": datetime.now().isoformat()
            })

        for r in json_rows:
            rows.append({
                "id": r.get("id") or f"codecomplex_{len(rows)+1}",
                "problem_id": r.get("problem_id") or "",
                "language": (r.get("language") or "python").lower(),
                "code": r.get("code") or "",
                "time_complexity": r.get("time_complexity") or "",
                "space_complexity": r.get("space_complexity") or "",
                "collected_at": datetime.now().isoformat()
            })
        return rows 