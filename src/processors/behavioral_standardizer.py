from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


_PII_PATTERNS = [
    re.compile(r"\b[A-Z][a-z]+\s[A-Z][a-z]+\b"),  # simple First Last
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),  # email
    re.compile(r"\b\+?\d[\d\s().-]{7,}\b"),  # phone-like
]


def redact_pii(text: str) -> str:
    if not text:
        return text
    redacted = text
    for pat in _PII_PATTERNS:
        redacted = pat.sub("[REDACTED]", redacted)
    return redacted


@dataclass
class BehavioralStandardizer:
    data_dir: Path

    @property
    def processed_dir(self) -> Path:
        p = self.data_dir / "processed"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def unify_reddit_items(self, items: List[Dict]) -> List[Dict]:
        unified: List[Dict] = []
        for it in items:
            unified.append({
                "source": "reddit",
                "subsource": it.get("subreddit"),
                "id": it.get("id"),
                "title": redact_pii(it.get("title") or ""),
                "content": redact_pii(it.get("selftext") or ""),
                "author": "[REDACTED]",
                "url": it.get("permalink"),
                "score": it.get("score"),
                "num_comments": it.get("num_comments"),
                "created_utc": it.get("created_utc"),
            })
        return unified

    def unify_glassdoor_items(self, items: List[Dict]) -> List[Dict]:
        # Expect fields similar to Apify Glassdoor export
        unified: List[Dict] = []
        for it in items:
            unified.append({
                "source": "glassdoor",
                "subsource": it.get("companyName"),
                "id": it.get("id") or it.get("reviewId"),
                "title": redact_pii(it.get("title") or it.get("header") or ""),
                "content": redact_pii(it.get("review") or it.get("text") or ""),
                "author": "[REDACTED]",
                "url": it.get("url") or it.get("reviewUrl"),
                "score": it.get("ratingOverall") or it.get("rating"),
                "num_comments": None,
                "created_utc": it.get("date") or it.get("dateTime")
            })
        return unified

    def write_unified(self, entries: List[Dict]) -> Path:
        out = self.processed_dir / "behavioral_unified.json"
        with out.open("w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)
        return out 