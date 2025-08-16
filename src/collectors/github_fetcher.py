from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .acquisition_logger import AcquisitionLogger


@dataclass
class GitHubFetcher:
    data_dir: Path
    rate_limit_sleep: float = 6.0  # unauthenticated: ~10 req/min; be conservative

    @property
    def raw_dir(self) -> Path:
        p = self.data_dir / "raw" / "github"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def _get_token(self) -> Optional[str]:
        # 1) Environment variable
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            return token.strip()
        # 2) Secrets file fallback: data/secrets/github_token.txt
        secret_file = self.data_dir / "secrets" / "github_token.txt"
        if secret_file.exists():
            try:
                return secret_file.read_text(encoding="utf-8").strip()
            except Exception:
                return None
        return None

    def _request(self, url: str) -> Dict[str, Any]:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "DSATrain-DataFetcher",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        token = self._get_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                payload = resp.read().decode("utf-8")
                return json.loads(payload)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore") if hasattr(e, "read") else ""
            raise RuntimeError(f"GitHub API error {e.code}: {e.reason}. Body: {body[:500]}")

    def search_code(self, query: str, language: Optional[str] = None, per_page: int = 50, pages: int = 2) -> Dict[str, Any]:
        results: List[Dict[str, Any]] = []
        for page in range(1, pages + 1):
            q = query
            if language:
                q += f" language:{language}"
            params = urllib.parse.urlencode({"q": q, "per_page": per_page, "page": page})
            url = f"https://api.github.com/search/code?{params}"
            data = self._request(url)
            items = data.get("items", [])
            results.extend(items)
            time.sleep(self.rate_limit_sleep)
            if not items:
                break
        return {"total_items": len(results), "items": results}

    def run_search(self, query: str, language: Optional[str] = None, per_page: int = 50, pages: int = 2) -> Dict[str, Any]:
        logger = AcquisitionLogger(self.data_dir)
        try:
            data = self.search_code(query=query, language=language, per_page=per_page, pages=pages)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_query = urllib.parse.quote_plus(query)
            out_file = self.raw_dir / f"search_{safe_query}_{ts}.json"
            with out_file.open("w", encoding="utf-8") as f:
                json.dump({"query": query, "language": language, **data}, f, ensure_ascii=False, indent=2)
            meta = {"timestamp": datetime.now().isoformat(), "query": query, "language": language, "count": data["total_items"], "output_file": str(out_file)}
            logger.log("github", "api_search_code", records=data["total_items"], success=True, metadata=meta)
            return meta
        except Exception as e:
            logger.log("github", "api_search_code", records=0, success=False, error=str(e), metadata={"query": query, "language": language})
            raise 