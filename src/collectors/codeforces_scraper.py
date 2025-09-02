"""
Lightweight Codeforces problem scraper.

Fetches the statement HTML and extracts a plain-text description, time/memory limits,
and sample tests. Designed for targeted backfills where the DB lacks descriptions.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import httpx
from bs4 import BeautifulSoup


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0 Safari/537.36"
)


def _build_url(contest_id: str | int, index: str) -> str:
    return f"https://codeforces.com/contest/{contest_id}/problem/{index}"


def _clean_text(s: str) -> str:
    return "\n".join(line.rstrip() for line in s.replace('\r', '').splitlines()).strip()


def scrape_problem(contest_id: str | int, index: str, timeout: float = 20.0) -> Dict[str, Any]:
    """Scrape a Codeforces problem page and return structured fields.

    Returns dict keys:
      - description: str
      - constraints: { time_limit_ms?: int, memory_limit_kb?: int }
      - examples: [ { input: str, output: str } ]
      - source_url: str
    Raises on network or parsing failure.
    """
    url = _build_url(contest_id, index)
    headers = {"User-Agent": USER_AGENT}
    with httpx.Client(headers=headers, timeout=httpx.Timeout(timeout)) as client:
        resp = client.get(url)
        resp.raise_for_status()
        html = resp.text

    soup = BeautifulSoup(html, "html.parser")
    root = soup.select_one("div.problem-statement")
    if not root:
        # Some pages are localized under /problemset/problem/ as well; fallback fetch
        alt_url = f"https://codeforces.com/problemset/problem/{contest_id}/{index}"
        with httpx.Client(headers=headers, timeout=httpx.Timeout(timeout)) as client:
            resp = client.get(alt_url)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            root = soup.select_one("div.problem-statement")
        if not root:
            raise RuntimeError("Unable to locate problem-statement block")

    # Extract description content excluding sample tests section
    # Keep paragraphs and lists in simple text form
    # We'll remove input/output headers that are part of statement structure
    for tag in root.select(".input, .output, .sample-tests, .sample-test"):
        tag.extract()

    desc_text = _clean_text(root.get_text("\n"))

    # Extract limits (best effort)
    constraints: Dict[str, Any] = {}
    tlim = soup.select_one("div.time-limit")
    mlim = soup.select_one("div.memory-limit")
    if tlim:
        ttxt = _clean_text(tlim.get_text(" "))
        # e.g., "time limit per test 2 seconds"
        if "millisecond" in ttxt:
            try:
                num = int("".join(ch for ch in ttxt if ch.isdigit()))
                constraints["time_limit_ms"] = num
            except Exception:
                pass
        elif "second" in ttxt:
            try:
                # find first float/int number
                import re

                m = re.search(r"(\d+(?:\.\d+)?)", ttxt)
                if m:
                    sec = float(m.group(1))
                    constraints["time_limit_ms"] = int(sec * 1000)
            except Exception:
                pass
    if mlim:
        mtxt = _clean_text(mlim.get_text(" "))
        # e.g., "memory limit per test 256 megabytes"
        if "megabyte" in mtxt.lower():
            try:
                import re

                m = re.search(r"(\d+)", mtxt)
                if m:
                    constraints["memory_limit_kb"] = int(m.group(1)) * 1024
            except Exception:
                pass

    # Extract sample tests
    examples: List[Dict[str, str]] = []
    sample_root = soup.select_one("div.sample-test") or soup.select_one("div.sample-tests")
    if sample_root:
        inputs = sample_root.select("div.input > pre")
        outputs = sample_root.select("div.output > pre")
        count = max(len(inputs), len(outputs))
        for i in range(count):
            inp = _clean_text(inputs[i].get_text("\n")) if i < len(inputs) else ""
            out = _clean_text(outputs[i].get_text("\n")) if i < len(outputs) else ""
            examples.append({"input": inp, "output": out})

    return {
        "description": desc_text,
        "constraints": constraints or None,
        "examples": examples or None,
        "source_url": url,
    }
