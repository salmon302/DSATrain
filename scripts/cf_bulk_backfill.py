from __future__ import annotations

"""
Async bulk backfill for Codeforces problem statements.

Features:
- Finds Codeforces problems with empty/short descriptions
- Async HTTP with concurrency limit and polite rate limiting
- Batch DB commits
- Resumable via progress file (JSON)

Usage examples (from repo root):
  python scripts/cf_bulk_backfill.py --max 500 --concurrency 5 --delay 0.5
  python scripts/cf_bulk_backfill.py --resume
    # Optionally supply cookies to bypass 403 (env or flag):
    CF_COOKIE="__cf_bm=...; JSESSIONID=..." python scripts/cf_bulk_backfill.py --max 500
"""

import argparse
import asyncio
import json
import os
import re
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Tuple

import httpx
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
# Ensure repo root is on sys.path so `import src.*` works when running as a script
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.models.database import DatabaseConfig, Problem
from sqlalchemy import func

ROOT = Path(__file__).resolve().parents[1]
PROGRESS_FILE = ROOT / "data" / "processed" / "cf_backfill_progress.json"
PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def _find_browser_executable() -> Optional[str]:
    """Attempt to find an existing Chromium-based browser on Windows to avoid downloading.
    Checks common install locations for Chrome, Edge, and Brave.
    Returns an absolute path or None.
    """
    candidates: List[str] = []
    local_appdata = os.environ.get('LOCALAPPDATA')
    program_files = os.environ.get('ProgramFiles')
    program_files_x86 = os.environ.get('ProgramFiles(x86)')

    if local_appdata:
        candidates += [
            os.path.join(local_appdata, 'Google', 'Chrome', 'Application', 'chrome.exe'),
            os.path.join(local_appdata, 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
            os.path.join(local_appdata, 'BraveSoftware', 'Brave-Browser', 'Application', 'brave.exe'),
        ]
    if program_files:
        candidates += [
            os.path.join(program_files, 'Google', 'Chrome', 'Application', 'chrome.exe'),
            os.path.join(program_files, 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
            os.path.join(program_files, 'BraveSoftware', 'Brave-Browser', 'Application', 'brave.exe'),
        ]
    if program_files_x86:
        candidates += [
            os.path.join(program_files_x86, 'Google', 'Chrome', 'Application', 'chrome.exe'),
            os.path.join(program_files_x86, 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
            os.path.join(program_files_x86, 'BraveSoftware', 'Brave-Browser', 'Application', 'brave.exe'),
        ]

    for path in candidates:
        if path and os.path.isfile(path):
            return path
    # Also try environment PATH
    for name in ["chrome.exe", "msedge.exe", "brave.exe"]:
        exe = _which(name)
        if exe:
            return exe
    return None


def _which(cmd: str) -> Optional[str]:
    paths = os.environ.get("PATH", "").split(os.pathsep)
    for p in paths:
        candidate = os.path.join(p, cmd)
        if os.path.isfile(candidate):
            return candidate
    return None


def parse_cf_platform_id(pid: str) -> Optional[Tuple[str, str]]:
    m = re.match(r"cf_(\d+)_([A-Za-z0-9]+)", pid)
    if not m:
        return None
    return m.group(1), m.group(2)


async def fetch_html(client: httpx.AsyncClient, url: str, referer: Optional[str] = None, extra_headers: Optional[Dict[str, str]] = None) -> str:
    headers: Dict[str, str] = {}
    if referer:
        headers["Referer"] = referer
    if extra_headers:
        headers.update(extra_headers)
    resp = await client.get(url, headers=headers)
    resp.raise_for_status()
    return resp.text


def clean_text(s: str) -> str:
    return "\n".join(line.rstrip() for line in s.replace("\r", "").splitlines()).strip()


class BrowserPool:
    """Minimal pyppeteer browser/page pool for fallback fetching."""
    def __init__(self, max_pages: int = 2):
        self.max_pages = max_pages
        self.browser = None
        self.queue: Optional[asyncio.Queue] = None

    async def __aenter__(self):
        from pyppeteer import launch
        exec_path = _find_browser_executable()
        launch_kwargs = {
            "headless": True,
            "args": ['--no-sandbox', '--disable-dev-shm-usage']
        }
        if exec_path:
            launch_kwargs["executablePath"] = exec_path
        self.browser = await launch(**launch_kwargs)
        self.queue = asyncio.Queue()
        for _ in range(self.max_pages):
            page = await self.browser.newPage()
            await page.setUserAgent(USER_AGENT)
            await page.setExtraHTTPHeaders({
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "DNT": "1",
                "Upgrade-Insecure-Requests": "1",
            })
            await self.queue.put(page)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        try:
            if self.browser is not None:
                await self.browser.close()
        finally:
            self.browser = None
            self.queue = None

    async def fetch(self, url: str, referer: Optional[str] = None, wait_until: str = 'domcontentloaded') -> str:
        assert self.queue is not None
        page = await self.queue.get()
        try:
            if referer:
                await page.setExtraHTTPHeaders({"Referer": referer})
            await page.goto(url, waitUntil=wait_until, timeout=30000)
            html = await page.content()
            return html
        finally:
            # Remove referer after use to avoid bleeding into next request
            await page.setExtraHTTPHeaders({"Referer": ""})
            await self.queue.put(page)


def parse_problem_html(html: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    root = soup.select_one("div.problem-statement")
    if not root:
        raise RuntimeError("problem-statement block not found")

    # Remove samples from description extraction path
    for tag in root.select(".input, .output, .sample-tests, .sample-test"):
        tag.extract()

    description = clean_text(root.get_text("\n"))
    constraints: Dict[str, Any] = {}
    tlim = soup.select_one("div.time-limit")
    mlim = soup.select_one("div.memory-limit")
    if tlim:
        ttxt = clean_text(tlim.get_text(" "))
        try:
            if "millisecond" in ttxt.lower():
                num = int("".join(ch for ch in ttxt if ch.isdigit()))
                constraints["time_limit_ms"] = num
            else:
                import re as _re

                m = _re.search(r"(\d+(?:\.\d+)?)", ttxt)
                if m:
                    sec = float(m.group(1))
                    constraints["time_limit_ms"] = int(sec * 1000)
        except Exception:
            pass
    if mlim:
        mtxt = clean_text(mlim.get_text(" "))
        try:
            import re as _re

            m = _re.search(r"(\d+)", mtxt)
            if m and "megabyte" in mtxt.lower():
                constraints["memory_limit_kb"] = int(m.group(1)) * 1024
        except Exception:
            pass

    examples: List[Dict[str, str]] = []
    sample_root = soup.select_one("div.sample-test") or soup.select_one("div.sample-tests")
    if sample_root:
        inputs = sample_root.select("div.input > pre")
        outputs = sample_root.select("div.output > pre")
        count = max(len(inputs), len(outputs))
        for i in range(count):
            inp = clean_text(inputs[i].get_text("\n")) if i < len(inputs) else ""
            out = clean_text(outputs[i].get_text("\n")) if i < len(outputs) else ""
            examples.append({"input": inp, "output": out})

    return {
        "description": description,
        "constraints": constraints or None,
        "examples": examples or None,
    }


async def scrape_problem(client: httpx.AsyncClient, contest_id: str, index: str, proxy_base: Optional[str] = None) -> Dict[str, Any]:
    # Try several URL variants to avoid intermittent 403s or path differences
    variants = [
    (f"https://codeforces.com/contest/{contest_id}/problem/{index}?locale=en", f"https://codeforces.com/contest/{contest_id}"),
        (f"https://codeforces.com/problemset/problem/{contest_id}/{index}?locale=en", "https://codeforces.com/problemset"),
        (f"https://codeforces.com/problemset/problem/{contest_id}/{index}?mobile=1&locale=en", "https://codeforces.com/problemset"),
        (f"https://m1.codeforces.com/problemset/problem/{contest_id}/{index}?locale=en", "https://codeforces.com/problemset"),
        (f"https://m2.codeforces.com/problemset/problem/{contest_id}/{index}?locale=en", "https://codeforces.com/problemset"),
    ]

    last_exc: Optional[Exception] = None
    for url, ref in variants:
        try:
            html = await fetch_html(client, url, referer=ref)
            data = parse_problem_html(html)
            data["source_url"] = url
            return data
        except Exception as e:
            last_exc = e
            continue
    # Try proxy fallback if provided
    if proxy_base:
        for url, ref in variants:
            try:
                # Construct proxied URL; r.jina.ai expects http scheme in target
                if url.startswith("https://"):
                    proxied = proxy_base.rstrip('/') + "/http://" + url[len("https://"):]
                elif url.startswith("http://"):
                    proxied = proxy_base.rstrip('/') + "/" + url
                else:
                    proxied = proxy_base.rstrip('/') + "/http://" + url
                # Do NOT forward user Cookie header to the proxy service
                html = await fetch_html(client, proxied, referer=ref, extra_headers={"Cookie": ""})
                data = parse_problem_html(html)
                data["source_url"] = url
                return data
            except Exception as e:
                last_exc = e
                continue
    # If all variants failed, raise last
    assert last_exc is not None
    raise last_exc


def load_progress() -> Dict[str, Any]:
    if PROGRESS_FILE.exists():
        try:
            return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"completed": [], "failures": []}


def save_progress(data: Dict[str, Any]) -> None:
    PROGRESS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


async def worker(sem: asyncio.Semaphore, client: httpx.AsyncClient, task: Tuple[str, str, str], delay: float, browser: Optional["BrowserPool"] = None, proxy_base: Optional[str] = None) -> Tuple[str, Optional[Dict[str, Any]], Optional[str]]:
    """Return (problem_id, data_or_none, error_or_none)."""
    problem_id, contest_id, index = task
    async with sem:
        # polite delay per request
        await asyncio.sleep(delay)
        try:
            data = await scrape_problem(client, contest_id, index, proxy_base=proxy_base)
            return (problem_id, data, None)
        except Exception as e:
            # Optional browser fallback
            if browser is not None:
                try:
                    # Use problemset variant as default with referer.
                    url = f"https://codeforces.com/problemset/problem/{contest_id}/{index}?locale=en"
                    html = await browser.fetch(url, referer="https://codeforces.com/problemset")
                    data = parse_problem_html(html)
                    data["source_url"] = url
                    return (problem_id, data, None)
                except Exception as e2:
                    return (problem_id, None, f"{e}; fallback:{e2}")
            return (problem_id, None, str(e))


async def run_backfill(max_items: int, concurrency: int, delay: float, resume: bool, use_browser: bool) -> None:
    # Load candidates from DB synchronously
    db = DatabaseConfig()
    session = db.get_session()
    try:
        q = (
            session.query(Problem)
            .filter(Problem.platform == "codeforces")
            .filter((Problem.description == None) | (Problem.description == "") | (func.length(Problem.description) < 60))  # type: ignore
        )
        total = q.count()
        candidates: List[Problem] = q.limit(max_items).all() if max_items > 0 else q.all()

        progress = load_progress()
        completed = set(progress.get("completed", [])) if resume else set()

        tasks: List[Tuple[str, str, str]] = []
        for p in candidates:
            if p.id in completed:
                continue
            pid = p.platform_id or p.id
            parsed = parse_cf_platform_id(pid)
            if not parsed:
                continue
            tasks.append((p.id, parsed[0], parsed[1]))

        print(f"Backfill candidates: {len(tasks)} (of {total} total needing work).")

        sem = asyncio.Semaphore(concurrency)
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "DNT": "1",
            "Connection": "keep-alive",
        }
        # Optional cookie support via env CF_COOKIE
        cookie_env = os.getenv("CF_COOKIE")
        if cookie_env:
            headers["Cookie"] = cookie_env
        timeout = httpx.Timeout(30.0)
        results: List[Tuple[str, Optional[Dict[str, Any]], Optional[str]]] = []

        async with httpx.AsyncClient(headers=headers, timeout=timeout, follow_redirects=True) as client:
            # Preflight request to establish cookies/session
            try:
                await client.get("https://codeforces.com/", headers={"Referer": "https://codeforces.com/problemset"})
            except Exception:
                pass
            proxy_base = os.getenv("CF_PROXY_BASE")
            if use_browser:
                async with BrowserPool(max_pages=max(1, min(3, concurrency))) as browser:
                    coros = [worker(sem, client, t, delay, browser, proxy_base) for t in tasks]
                    async for res in _as_completed_stream(coros):
                        results.append(res)
                        if len(results) % 50 == 0:
                            _flush_progress(progress, results)
            else:
                coros = [worker(sem, client, t, delay, None, proxy_base) for t in tasks]
                for fut in asyncio.as_completed(coros):
                    res = await fut
                    results.append(res)
                    if len(results) % 50 == 0:
                        _flush_progress(progress, results)

        # Apply updates to DB in batches
        by_id: Dict[str, Dict[str, Any]] = {pid: data for pid, data, err in results if data is not None}
        failures = [(pid, err) for pid, data, err in results if err]
        print(f"Fetched OK: {len(by_id)} | Failures: {len(failures)}")

        updated = 0
        batch = 0
        for p in candidates:
            data = by_id.get(p.id)
            if not data:
                continue
            p.description = data.get("description") or p.description
            if data.get("constraints"):
                p.constraints = data["constraints"]
            if data.get("examples"):
                p.examples = data["examples"]
            session.add(p)
            updated += 1
            batch += 1
            if batch >= 100:
                session.commit()
                batch = 0
        if batch:
            session.commit()
        print(f"DB updated rows: {updated}")

        # Finalize progress
        _finalize_progress(progress, by_id, failures)
    finally:
        session.close()

def _flush_progress(progress: Dict[str, Any], results: List[Tuple[str, Optional[Dict[str, Any]], Optional[str]]]) -> None:
    done_ids = [pid for pid, data, err in results if data is not None]
    progress["completed"] = list(set(progress.get("completed", []) + done_ids))
    progress.setdefault("failures", [])
    for pid, data, err in results:
        if err:
            progress["failures"].append({"id": pid, "error": err})
    save_progress(progress)


def _finalize_progress(progress: Dict[str, Any], by_id: Dict[str, Dict[str, Any]], failures: List[Tuple[str, Optional[str]]]) -> None:
    done_ids = [pid for pid in by_id.keys()]
    progress["completed"] = list(set(progress.get("completed", []) + done_ids))
    progress.setdefault("failures", [])
    for pid, err in failures:
        progress["failures"].append({"id": pid, "error": err})
    save_progress(progress)


async def _as_completed_stream(coros):
    for fut in asyncio.as_completed(coros):
        yield await fut


def main() -> None:
    parser = argparse.ArgumentParser(description="Bulk backfill Codeforces problem statements")
    parser.add_argument("--max", type=int, default=1000, help="Max number of items to process (0 = all)")
    parser.add_argument("--concurrency", type=int, default=5, help="Concurrent requests")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between requests per worker (seconds)")
    parser.add_argument("--resume", action="store_true", help="Resume using progress file")
    parser.add_argument("--browser", action="store_true", help="Use headless browser fallback for 403s")
    parser.add_argument("--proxy", action="store_true", help="Enable proxy fallback via r.jina.ai (sets CF_PROXY_BASE)")
    parser.add_argument("--cookie", type=str, default=None, help="Explicit Cookie header value for codeforces.com requests")
    args = parser.parse_args()

    if args.proxy and not os.getenv("CF_PROXY_BASE"):
        os.environ["CF_PROXY_BASE"] = "https://r.jina.ai"

    # If cookie header provided via CLI or env, inject into default headers via env var usage in run_backfill
    cookie_header = args.cookie or os.getenv("CF_COOKIE")
    if cookie_header:
        # Store into env so run_backfill can pick it up (keeps signature simple)
        os.environ["CF_COOKIE"] = cookie_header

    asyncio.run(run_backfill(max_items=args.max, concurrency=args.concurrency, delay=args.delay, resume=args.resume, use_browser=args.browser))


if __name__ == "__main__":
    main()
