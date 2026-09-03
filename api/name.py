"""Vercel function: GET /api/name?lang=xx&name=...
A Latin name written in Odia, Devanagari, Kannada or Telugu.
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
        code, body = server.name_payload(
            server.query_arg(self.path, "lang"),
            server.query_arg(self.path, "name"),
        )
        server.write_json(self, code, body, cache="public, max-age=600, s-maxage=604800")
