# Codeforces Backfill Guide

This guide explains how to populate missing Codeforces problem statements into the DSATrain database using `scripts/cf_bulk_backfill.py`.

## Overview

- Finds Codeforces problems with missing/very short descriptions
- Fetches statements via HTTP with multiple URL variants
- Anti-bot bypass options: proxy, Cookie header, headless browser
- Async with concurrency + per-worker delay
- Resumable via `data/processed/cf_backfill_progress.json`
- Batch commits to the DB

## Quick start

Use your repo's virtual environment.

- Tiny dry run (1 item):

```cmd
"%CD%\.venv\Scripts\python.exe" scripts\cf_bulk_backfill.py --max 1 --concurrency 1 --delay 1 --resume
```

- Tiny dry run with proxy + browser (recommended):

```cmd
"%CD%\.venv\Scripts\python.exe" scripts\cf_bulk_backfill.py --max 1 --concurrency 1 --delay 1 --resume --proxy --browser
```

If you have a valid Codeforces Cookie (from your browser session), you can add:

```cmd
"%CD%\.venv\Scripts\python.exe" scripts\cf_bulk_backfill.py --max 1 --concurrency 1 --delay 1 --resume --cookie "JSESSIONID=...; __cf_bm=..."
```

## Recommended scaling

- Start small and scale up gradually:
  - `--max 25 --concurrency 2 --delay 0.5 --resume --proxy --browser`
  - `--max 100 --concurrency 3 --delay 0.5 --resume --proxy` (if cookie is available, you can skip `--browser` for speed)
- Always keep `--resume` on; the script will update `data/processed/cf_backfill_progress.json` as it goes.
- Keep concurrency modest to avoid throttling. Typical safe range: 2–4 with 0.5–1.0s delay.

## CLI flags

- `--max`: Max number of items to process (0 = all)
- `--concurrency`: Number of parallel workers
- `--delay`: Polite delay (seconds) per worker before each fetch
- `--resume`: Resume using the progress file
- `--browser`: Use headless browser (pyppeteer) fallback when HTTP fails
- `--proxy`: Enable proxy fallback (defaults to r.jina.ai via `CF_PROXY_BASE`)
- `--cookie`: Set a Cookie header for `codeforces.com` requests (equivalent to env var `CF_COOKIE`)

## Environment variables

- `CF_COOKIE`: Same as `--cookie`. Example: `JSESSIONID=...; __cf_bm=...`.
- `CF_PROXY_BASE`: Proxy base URL. The `--proxy` flag sets this to `https://r.jina.ai` if not already set.

## How anti-bot bypass works

- Multiple URL variants are tried first (contest, problemset, mobile subdomains, `?locale=en`) with appropriate headers and referers
- If direct fetch fails, an optional proxy can be used
- If still blocked, an optional headless browser (pyppeteer) fallback renders the page and extracts the content
- The script uses realistic browser headers to reduce blocks

### Browser fallback on Windows

- The script will try to launch an already installed Chromium-based browser (Chrome, Edge, Brave)
- This avoids pyppeteer attempting to download its own Chromium, which often fails on Windows

## Progress file

- Located at `data/processed/cf_backfill_progress.json`
- Tracks `completed` IDs and `failures` with error messages
- Safe to re-run with `--resume` to keep making progress

## Troubleshooting

- 403 or empty fetches: Try adding `--proxy`, `--cookie`, and/or `--browser`; reduce `--concurrency` and increase `--delay`
- Browser download failure: Our script auto-detects installed browsers; if that still fails, ensure Chrome/Edge/Brave are installed
- SQLite locking: The script commits in batches; keep concurrency modest
- Parsing quirks: Rare pages might differ; failures are recorded for review

## Safety and etiquette

- Be polite: keep concurrency/delay reasonable
- Prefer running small batches repeatedly with `--resume`
- Use a valid Cookie only from your own session and keep it private

## Example sessions

- Medium batch:

```cmd
"%CD%\.venv\Scripts\python.exe" scripts\cf_bulk_backfill.py --max 100 --concurrency 3 --delay 0.5 --resume --proxy --browser
```

- Cookie-assisted (often faster, can skip browser):

```cmd
set CF_COOKIE=JSESSIONID=...; __cf_bm=...
"%CD%\.venv\Scripts\python.exe" scripts\cf_bulk_backfill.py --max 200 --concurrency 3 --delay 0.5 --resume --proxy
```
