"""Vercel function: GET /api/say?lang=xx&text=...
A WAV of one phrase in that language's voice. Synthesis is paid for once and
then held by the CDN - there is no cache/ directory on a serverless deployment.
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
        code, out = server.say_payload(
            server.query_arg(self.path, "lang"),
            server.query_arg(self.path, "text"),
        )
        if isinstance(out, bytes):
            return server.write_bytes(self, code, out, "audio/wav", cache=server.SAY_CACHE)
        server.write_json(self, code, out)
