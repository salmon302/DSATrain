import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "src" / "api"
DOC = ROOT / "docs" / "API_REFERENCE.md"

ROUTE_RE = re.compile(r"@router\.(get|post|put|delete|patch)\(\s*\"([^\"]+)\"", re.I)
ALT_ROUTER_RE = re.compile(r"(APIRouter\(prefix=\"([^\"]+)\".*?\))", re.S)
APP_INCLUDE_RE = re.compile(r"include_router\(([^\)]+)\)")

# Fast heuristic: collect prefixes and match decorated paths

def collect_routes():
    routes = []
    for py in API_DIR.glob("*.py"):
        try:
            text = py.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        # Determine router prefix if present
        prefix = None
        m = re.search(r"APIRouter\(.*?prefix=\"([^\"]+)\"", text)
        if m:
            prefix = m.group(1)
        for mm in ROUTE_RE.finditer(text):
            method = mm.group(1).upper()
            path = mm.group(2)
            full = f"{prefix or ''}{path}"
            routes.append((method, full))
    # Normalize duplicates
    uniq = sorted(set(routes))
    return uniq


def read_doc_lines():
    try:
        return DOC.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        print(f"ERROR: Missing {DOC}")
        return []


def route_rendered_in_doc(method, path, doc_lines):
    needle = f"{method:6s} {path}".replace("  ", " ")
    # API_REFERENCE uses patterns like: "- GET    /path"
    for line in doc_lines:
        if line.strip().startswith(f"- {method}") and path in line:
            return True
    return False


def main():
    routes = collect_routes()
    doc_lines = read_doc_lines()
    if not doc_lines:
        sys.exit(1)

    missing = []
    # Limit to relevant prefixes we document
    allowed_prefixes = (
        "/ai", "/practice", "/interview", "/cognitive", "/learning-paths", "/enhanced-stats", "/settings"
    )
    for method, path in routes:
        if not any(path.startswith(p) for p in allowed_prefixes):
            continue
        if not route_rendered_in_doc(method, path, doc_lines):
            missing.append((method, path))

    if missing:
        print("The following routes were not found in docs/API_REFERENCE.md:")
        for m, p in missing:
            print(f"  - {m} {p}")
        sys.exit(2)

    print("API reference looks in sync with src/api routes.")


if __name__ == "__main__":
    main()
