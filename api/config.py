"""Vercel function: GET /api/config
Every language, its words and the session timings - the whole screen.
The real work is in server.py at the repo root, which the local station shares.
@vercel/python bundles the whole project, so `import server` finds it - the
sys.path line below is what makes it importable from inside api/.
"""

import os
import sys
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import server  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        server.write_json(self, 200, server.config_payload(),
                          cache="public, max-age=60, s-maxage=86400")
