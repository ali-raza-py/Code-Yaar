#!/usr/bin/env python3
"""Measure the initial JavaScript a route actually ships.

Next.js 16 (Turbopack) no longer prints per-route JS sizes in `next build`.
This reads the prerendered HTML in `frontend/.next/server/app/`, collects the
unique `<script src>` chunks each route references, and sums their raw and
gzip-compressed sizes from `frontend/.next/`.

Usage (after `npm run build` in frontend/):
    python scripts/measure-route-js.py
    python scripts/measure-route-js.py /dashboard /learn /challenges
"""

from __future__ import annotations

import gzip
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NEXT = ROOT / "frontend" / ".next"
SERVER_APP = NEXT / "server" / "app"

DEFAULT_ROUTES = ["/", "/dashboard", "/learn", "/courses", "/tracks", "/challenges", "/leaderboard", "/admin/dashboard"]

SCRIPT_SRC = re.compile(r'<script[^>]+src="([^"]+\.js)"')


def route_html(route: str) -> Path | None:
    if route == "/":
        candidate = SERVER_APP / "index.html"
    else:
        candidate = SERVER_APP / f"{route.strip('/')}.html"
    return candidate if candidate.exists() else None


def measure(route: str) -> tuple[int, int, int] | None:
    html_path = route_html(route)
    if html_path is None:
        return None
    html = html_path.read_text(encoding="utf-8", errors="ignore")
    srcs = set(SCRIPT_SRC.findall(html))
    if not srcs:
        return None

    raw = 0
    zipped = 0
    for src in srcs:
        # "/_next/static/chunks/x.js" → frontend/.next/static/chunks/x.js
        path = NEXT / src.replace("/_next/", "", 1).lstrip("/")
        if not path.exists():
            continue
        data = path.read_bytes()
        raw += len(data)
        zipped += len(gzip.compress(data, 9))
    return raw, zipped, len(srcs)


def main(argv: list[str]) -> int:
    routes = argv[1:] or DEFAULT_ROUTES
    if not SERVER_APP.exists():
        print(f"No build found at {SERVER_APP}. Run `npm run build` in frontend/ first.")
        return 1

    print(f"{'route':<20}{'chunks':>7}{'JS raw (KB)':>14}{'JS gzip (KB)':>15}")
    for route in routes:
        result = measure(route)
        if result is None:
            print(f"{route:<20}{'n/a':>7}")
            continue
        raw, zipped, chunks = result
        print(f"{route:<20}{chunks:>7}{raw / 1024:>14.1f}{zipped / 1024:>15.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
