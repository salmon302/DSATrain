from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .acquisition_logger import AcquisitionLogger


@dataclass
class CodeforcesFetcher:
    data_dir: Path
    rate_limit_seconds: float = 2.1

    @property
    def base_url(self) -> str:
        return "https://codeforces.com/api"

    @property
    def raw_dir(self) -> Path:
        p = self.data_dir / "raw" / "codeforces"
        p.mkdir(parents=True, exist_ok=True)
        (p / "contests").mkdir(parents=True, exist_ok=True)
        (p / "submissions").mkdir(parents=True, exist_ok=True)
        return p

    def _sleep(self) -> None:
        time.sleep(self.rate_limit_seconds)

    def _get(self, endpoint: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        query = f"?{urllib.parse.urlencode(params)}" if params else ""
        url = f"{self.base_url}/{endpoint}{query}"
        with urllib.request.urlopen(url, timeout=30) as resp:
            payload = resp.read().decode("utf-8")
            return json.loads(payload)

    # ===== Problems =====
    def fetch_problemset(self) -> Dict[str, Any]:
        return self._get("problemset.problems")

    def save_problemset(self) -> Dict[str, Any]:
        logger = AcquisitionLogger(self.data_dir)
        try:
            result = self.fetch_problemset()
            status = result.get("status")
            if status != "OK":
                raise RuntimeError(result.get("comment", "Unknown Codeforces API error"))
            problems = result.get("result", {}).get("problems", [])
            stats = result.get("result", {}).get("problemStatistics", [])

            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            out_file = self.raw_dir / f"problemset_{ts}.json"
            with out_file.open("w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            summary = {
                "timestamp": datetime.now().isoformat(),
                "total_problems": len(problems),
                "total_stats": len(stats),
                "output_file": str(out_file),
            }
            with (self.raw_dir / "collection_summary.json").open("w", encoding="utf-8") as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)

            logger.log("codeforces", "api_problemset", records=len(problems), success=True, metadata=summary)
            return summary
        except Exception as e:
            logger.log("codeforces", "api_problemset", records=0, success=False, error=str(e))
            raise

    # ===== Contests =====
    def fetch_contest_list(self, gym: bool = False) -> Dict[str, Any]:
        params = {"gym": str(gym).lower()}
        return self._get("contest.list", params)

    def save_contests(self, gym: bool = False) -> Dict[str, Any]:
        logger = AcquisitionLogger(self.data_dir)
        try:
            result = self.fetch_contest_list(gym=gym)
            if result.get("status") != "OK":
                raise RuntimeError(result.get("comment", "Unknown Codeforces API error"))
            contests = result.get("result", [])
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            out_file = self.raw_dir / "contests" / f"contests_{'gym_' if gym else ''}{ts}.json"
            with out_file.open("w", encoding="utf-8") as f:
                json.dump(contests, f, ensure_ascii=False, indent=2)
            meta = {"timestamp": datetime.now().isoformat(), "count": len(contests), "output_file": str(out_file), "gym": gym}
            logger.log("codeforces", "api_contest_list", records=len(contests), success=True, metadata=meta)
            return meta
        except Exception as e:
            logger.log("codeforces", "api_contest_list", records=0, success=False, error=str(e), metadata={"gym": gym})
            raise

    # ===== User submissions =====
    def fetch_user_status(self, handle: str, from_index: int = 1, count: int = 100) -> Dict[str, Any]:
        params = {"handle": handle, "from": from_index, "count": count}
        return self._get("user.status", params)

    def save_user_submissions(self, handle: str, page_size: int = 100, max_pages: int = 200) -> Dict[str, Any]:
        logger = AcquisitionLogger(self.data_dir)
        submissions: List[Dict[str, Any]] = []
        page = 0
        try:
            while page < max_pages:
                from_index = page * page_size + 1
                result = self.fetch_user_status(handle=handle, from_index=from_index, count=page_size)
                if result.get("status") != "OK":
                    raise RuntimeError(result.get("comment", "Unknown Codeforces API error"))
                items = result.get("result", [])
                if not items:
                    break
                submissions.extend(items)
                page += 1
                self._sleep()

            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            out_file = self.raw_dir / "submissions" / f"{handle}_submissions_{ts}.json"
            with out_file.open("w", encoding="utf-8") as f:
                json.dump({"handle": handle, "submissions": submissions}, f, ensure_ascii=False, indent=2)
            meta = {"timestamp": datetime.now().isoformat(), "handle": handle, "count": len(submissions), "output_file": str(out_file)}
            logger.log("codeforces", "api_user_status", records=len(submissions), success=True, metadata=meta)
            return meta
        except Exception as e:
            logger.log("codeforces", "api_user_status", records=len(submissions), success=False, error=str(e), metadata={"handle": handle})
            raise

    # ===== Orchestrations =====
    def run(self) -> None:
        # Backwards-compatible: fetch problemset only
        self.save_problemset() 