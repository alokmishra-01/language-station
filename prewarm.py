#!/usr/bin/env python3
"""Warm a deployment so the first child of the day never waits.

`server.py warm` fills the local cache/ directory. A Vercel deployment has no
cache/ - it leans on the CDN instead, which only holds a phrase once somebody
has asked for it. This asks for all of them.

    python3 prewarm.py https://language-station.vercel.app
    python3 prewarm.py https://language-station.vercel.app hi de   # just those

Safe to re-run; it is only GETs. Run it once after each deployment.
"""

from __future__ import annotations

import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import languages

WORKERS = 6  # gentle: every miss is one Cartesia synthesis


def fetch(url: str) -> tuple[bool, int]:
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return True, len(r.read())
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code}  {urllib.parse.unquote(url.split('text=')[-1])[:40]}")
    except Exception as e:
        print(f"  {type(e).__name__}  {urllib.parse.unquote(url.split('text=')[-1])[:40]}")
    return False, 0


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    base = sys.argv[1].rstrip("/")
    codes = sys.argv[2:] or [l["code"] for l in languages.LANGUAGES]

    ok, bad, started = 0, 0, time.time()
    for code in codes:
        lang = languages.BY_CODE.get(code)
        if not lang:
            print(f"  ?? unknown language {code}")
            continue
        phrases = languages.spoken_rows(lang)
        urls = [f"{base}/api/say?lang={code}&text=" + urllib.parse.quote(p) for p in phrases]
        with ThreadPoolExecutor(WORKERS) as pool:
            got = sum(1 for good, _ in pool.map(fetch, urls) if good)
        ok += got
        bad += len(phrases) - got
        print(f"  {code}  {got}/{len(phrases)} warm")

    print(f"\n{ok} phrases warm, {bad} failed, {time.time() - started:.0f}s -> {base}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
