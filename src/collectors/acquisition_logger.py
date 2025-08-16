from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class AcquisitionLogger:
    data_dir: Path

    @property
    def log_path(self) -> Path:
        processed = self.data_dir / "processed"
        processed.mkdir(parents=True, exist_ok=True)
        return processed / "acquisition_logs.jsonl"

    def log(self, source: str, method: str, records: int, success: bool, error: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        entry = {
            "timestamp": datetime.now().isoformat(),
            "source": source,
            "method": method,
            "records": int(records),
            "success": bool(success),
            "error": error,
            "metadata": metadata or {},
        }
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n") 