#!/usr/bin/env python3
"""List Cartesia voices for the languages the station needs.

    python3 find_voices.py            # summary per language
    python3 find_voices.py hi de      # just those languages, full list
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.parse
import urllib.request

ENV_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
    os.path.expanduser("~/Documents/digital-brain/.env"),
]
API = "https://api.cartesia.ai"
VERSION = "2025-04-16"

WANT = ["hi", "de", "es", "fr", "kn", "te", "or", "ta", "bn", "mr"]


def api_key() -> str:
    for path in ENV_CANDIDATES:
        try:
            for line in open(path, encoding="utf-8"):
                m = re.match(r"^CARTESIA_KEY=(.*)$", line.strip())
                if m:
                    return m.group(1).strip().strip("\"'")
        except FileNotFoundError:
            continue
    sys.exit("CARTESIA_KEY not found")


def get(path: str, key: str) -> dict:
    req = urllib.request.Request(API + path)
    req.add_header("X-API-Key", key)
    req.add_header("Cartesia-Version", VERSION)
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read())


def all_voices(key: str) -> list[dict]:
    """Page through the library. The embedding field is huge, so drop it."""
    out: list[dict] = []
    cursor = None
    for _ in range(60):
        q = {"limit": "100"}
        if cursor:
            q["starting_after"] = cursor
        page = get("/voices/?" + urllib.parse.urlencode(q), key)
        rows = page.get("data") or page.get("voices") or []
        if not rows:
            break
        for v in rows:
            out.append({k: v.get(k) for k in
                        ("id", "name", "language", "gender", "description", "is_public", "country")})
        if not page.get("has_more"):
            break
        cursor = rows[-1].get("id")
    return out


def main() -> None:
    key = api_key()
    voices = all_voices(key)
    print(f"{len(voices)} voices in the library\n")

    langs = [a.lower() for a in sys.argv[1:]] or WANT
    detail = bool(sys.argv[1:])

    for lang in langs:
        rows = [v for v in voices if (v.get("language") or "").lower() == lang]
        print(f"=== {lang}  ({len(rows)} voices) ===")
        if not rows:
            print("   none\n")
            continue
        show = rows if detail else rows[:8]
        for v in show:
            g = (v.get("gender") or "?")[:1]
            desc = (v.get("description") or "").split(".")[0][:74]
            print(f"   {v['id']}  {g}  {v['name'][:34]:<34} {desc}")
        if not detail and len(rows) > len(show):
            print(f"   ... {len(rows) - len(show)} more")
        print()


if __name__ == "__main__":
    main()
