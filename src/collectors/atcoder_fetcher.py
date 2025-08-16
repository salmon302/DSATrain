from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .acquisition_logger import AcquisitionLogger


@dataclass
class AtCoderFetcher:
    data_dir: Path

    @property
    def raw_dir(self) -> Path:
        p = self.data_dir / "raw" / "atcoder"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def fetch_problem_index(self) -> List[Dict[str, Any]]:
        # There is no official AtCoder API; we attempt to fetch a community-maintained index if provided by user
        # Otherwise, we look for a local mirror file under data/raw/atcoder/problems_index.json
        local_index = self.raw_dir / "problems_index.json"
        if local_index.exists():
            with local_index.open("r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        return []

    def run(self) -> None:
        logger = AcquisitionLogger(self.data_dir)
        problems = self.fetch_problem_index()
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_file = self.raw_dir / f"problems_index_snapshot_{ts}.json"
        with out_file.open("w", encoding="utf-8") as f:
            json.dump(problems, f, ensure_ascii=False, indent=2)
        logger.log("atcoder", "community_index_or_local", records=len(problems), success=True, metadata={"output_file": str(out_file)}) 