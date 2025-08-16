from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .acquisition_logger import AcquisitionLogger


@dataclass
class RedditFetcher:
    data_dir: Path
    rate_limit_sleep: float = 3.0  # conservative to respect reddit

    @property
    def raw_dir(self) -> Path:
        p = self.data_dir / "raw" / "reddit"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def _request(self, url: str) -> Dict[str, Any]:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "DSATrain-BehavioralFetcher/0.1 by dsatrain",
                "Accept": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = resp.read().decode("utf-8")
            return json.loads(payload)

    def search(self, query: str, subreddit: Optional[str] = None, limit: int = 50, pages: int = 2, sort: str = "new") -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        after: Optional[str] = None
        for _ in range(max(1, pages)):
            q = urllib.parse.quote_plus(query)
            path = "search.json"
            if subreddit:
                path = f"r/{subreddit}/search.json"
            params = {"q": query, "limit": str(limit), "sort": sort, "restrict_sr": str(bool(subreddit)).lower()}
            if after:
                params["after"] = after
            url = f"https://www.reddit.com/{path}?{urllib.parse.urlencode(params)}"
            data = self._request(url)
            children = data.get("data", {}).get("children", [])
            for ch in children:
                d = ch.get("data", {})
                results.append({
                    "id": d.get("id"),
                    "title": d.get("title"),
                    "selftext": d.get("selftext"),
                    "subreddit": d.get("subreddit"),
                    "author": d.get("author"),
                    "created_utc": d.get("created_utc"),
                    "permalink": f"https://reddit.com{d.get('permalink')}" if d.get("permalink") else None,
                    "score": d.get("score"),
                    "num_comments": d.get("num_comments"),
                    "url_overridden_by_dest": d.get("url_overridden_by_dest"),
                })
            after = data.get("data", {}).get("after")
            if not after:
                break
            time.sleep(self.rate_limit_sleep)
        return results

    def run_search(self, query: str, subreddit: Optional[str] = None, limit: int = 50, pages: int = 2, sort: str = "new") -> Dict[str, Any]:
        logger = AcquisitionLogger(self.data_dir)
        try:
            items = self.search(query=query, subreddit=subreddit, limit=limit, pages=pages, sort=sort)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_query = urllib.parse.quote_plus(query)
            fname = f"search_{safe_query}_{subreddit or 'all'}_{ts}.json"
            out_file = self.raw_dir / fname
            with out_file.open("w", encoding="utf-8") as f:
                json.dump({"query": query, "subreddit": subreddit, "items": items}, f, ensure_ascii=False, indent=2)
            meta = {"timestamp": datetime.now().isoformat(), "query": query, "subreddit": subreddit, "count": len(items), "output_file": str(out_file)}
            logger.log("reddit", "public_search", records=len(items), success=True, metadata=meta)
            return meta
        except Exception as e:
            logger.log("reddit", "public_search", records=0, success=False, error=str(e), metadata={"query": query, "subreddit": subreddit})
            raise 