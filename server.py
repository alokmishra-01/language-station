#!/usr/bin/env python3
"""Local server + CLI for the school language station.

Seven languages, one agent each (see languages.py and agents.json). Everything
runs on this machine: the Cartesia key stays here and the browser only ever gets
a short-lived access token from /api/token.

    python3 server.py serve            # start the station (default port 8777)
    python3 server.py check            # key, every agent, TTS, fonts
    python3 server.py warm             # pre-render all screen audio into cache/
    python3 server.py warm hi de       # ...just those languages
    python3 server.py say or "ନମସ୍କାର"  # speak a phrase through the speakers
    python3 server.py name hi Sophie   # transliterate + speak a name
    python3 server.py langs            # what is configured

Screen audio is cached under cache/ as WAV, so tapping a word still works when
the wifi does not. Only the live conversation needs the network.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import languages
from translit import to_script

HERE = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(HERE, ".env")
CACHE_DIR = os.environ.get("STATION_CACHE_DIR") or (
    # Vercel's filesystem is read-only apart from /tmp, which survives for the
    # life of a warm instance - good enough as a second-tier cache behind the CDN.
    "/tmp/station-cache" if os.environ.get("VERCEL") else os.path.join(HERE, "cache")
)
PORT = int(os.environ.get("STATION_PORT", "8777"))

API = "https://api.cartesia.ai"
REST_VERSION = "2025-04-16"
WS_VERSION = "2026-08-14"
V1_VERSION = "2026-03-01"

# sonic-3.6 is the only model with Odia, and it covers every other language here.
# sonic-3.5 and sonic-3 reject language "or" outright.
TTS_MODEL = "sonic-3.6"

SESSION_SECONDS = int(os.environ.get("STATION_SESSION_SECONDS", "210"))
IDLE_SECONDS = int(os.environ.get("STATION_IDLE_SECONDS", "35"))

_key_cache: str | None = None


# --------------------------------------------------------------------------- key


def api_key() -> str:
    global _key_cache
    if _key_cache:
        return _key_cache
    if os.environ.get("CARTESIA_KEY"):
        _key_cache = os.environ["CARTESIA_KEY"].strip()
        return _key_cache
    try:
        for line in open(ENV_FILE, encoding="utf-8"):
            m = re.match(r"^CARTESIA_KEY=(.*)$", line.strip())
            if m:
                _key_cache = m.group(1).strip().strip("\"'")
                return _key_cache
    except FileNotFoundError:
        pass
    raise RuntimeError(
        f"CARTESIA_KEY not found. Put it in {ENV_FILE}, or in the environment "
        "(Vercel: Project Settings -> Environment Variables).")


# ------------------------------------------------------------------- cartesia


def _post(path: str, body: dict, raw: bool = False, timeout: float = 40.0):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode(), method="POST")
    req.add_header("X-API-Key", api_key())
    req.add_header("Cartesia-Version", REST_VERSION)
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read() if raw else json.loads(r.read())


def mint_token(seconds: int = 900) -> dict:
    """Short-lived browser token. `agent` is the only grant it needs."""
    return _post("/access-token", {"grants": {"agent": True}, "expires_in": seconds})


def synth_wav(text: str, tts_language: str, voice: str) -> bytes:
    """A complete WAV, cached on disk by (model, language, voice, text)."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    stamp = hashlib.sha256(
        f"{TTS_MODEL}|{tts_language}|{voice}|{text}".encode()).hexdigest()[:20]
    path = os.path.join(CACHE_DIR, f"{stamp}.wav")
    if os.path.exists(path) and os.path.getsize(path) > 44:
        return open(path, "rb").read()
    audio = _post(
        "/tts/bytes",
        {
            "model_id": TTS_MODEL,
            "transcript": text,
            "language": tts_language,
            "voice": {"mode": "id", "id": voice},
            "output_format": {"container": "wav", "encoding": "pcm_s16le", "sample_rate": 24000},
        },
        raw=True,
    )
    tmp = path + ".part"
    with open(tmp, "wb") as fh:
        fh.write(audio)
    os.replace(tmp, path)
    return audio


def agent_state(agent_id: str) -> dict:
    req = urllib.request.Request(f"{API}/agents/v1/{agent_id}")
    req.add_header("X-API-Key", api_key())
    req.add_header("Cartesia-Version", V1_VERSION)
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read())


def resolve(code: str | None) -> dict:
    """Language record for a code, falling back to the default."""
    return languages.BY_CODE.get((code or "").lower()) or languages.BY_CODE[languages.DEFAULT]


# ----------------------------------------------------------------- routes
# The five routes live here as plain functions so that the local server below
# and the Vercel functions in api/ share one implementation each, rather than
# drifting apart. Each returns (status, payload).

# Unset (the default, and how the station runs at the event) means anyone who can
# reach the page can talk. Set it on a public deployment: /api/token spends real
# money against the Cartesia key, so an open one is an open tab.
PASSCODE = (os.environ.get("STATION_PASSCODE") or "").strip()

# Phrases are immutable for a given deployment, so let the CDN keep them and
# pay Cartesia once per phrase rather than once per child.
SAY_CACHE = "public, max-age=86400, s-maxage=31536000, immutable"


def passcode_ok(supplied: str | None) -> bool:
    if not PASSCODE:
        return True
    return hmac.compare_digest((supplied or "").strip(), PASSCODE)


def config_payload() -> dict:
    cfg = languages.as_json()
    cfg["ws_version"] = WS_VERSION
    cfg["session_seconds"] = SESSION_SECONDS
    cfg["idle_seconds"] = IDLE_SECONDS
    cfg["needs_passcode"] = bool(PASSCODE)
    return cfg


def token_payload(code: str | None, supplied: str | None = None) -> tuple[int, dict]:
    if not passcode_ok(supplied):
        return 401, {"error": "This station needs a passcode.", "need_passcode": True}
    lang = resolve(code)
    agent_id = languages.agent_ids().get(lang["code"])
    if not agent_id:
        return 503, {"error": f"no agent for {lang['code']} - run agent/create_agents.py"}
    try:
        tok = mint_token()
    except urllib.error.HTTPError as e:
        return 502, {"error": f"token mint failed: HTTP {e.code}",
                     "detail": e.read().decode(errors="replace")[:300]}
    except Exception as e:
        return 503, {"error": f"{type(e).__name__}: {e}"}
    return 200, {"token": tok.get("token"), "ws_version": WS_VERSION,
                 "agent_id": agent_id, "lang": lang["code"]}


def say_payload(code: str | None, text: str | None):
    """(status, WAV bytes) on success, (status, error dict) otherwise."""
    text = (text or "").strip()
    if not text:
        return 400, {"error": "text is required"}
    if len(text) > 400:
        return 400, {"error": "text too long"}
    lang = resolve(code)
    try:
        return 200, synth_wav(text, lang["code"], lang["voice"])
    except Exception as e:
        return 503, {"error": f"{type(e).__name__}: {e}"}


def name_payload(code: str | None, raw: str | None) -> tuple[int, dict]:
    raw = (raw or "").strip()[:40]
    if not raw:
        return 400, {"error": "name is required"}
    lang = resolve(code)
    script = lang["script"]
    return 200, {
        "input": raw,
        "script": script,
        # Latin-script languages have nothing to transliterate: the point
        # there is hearing the name said with that language's sounds.
        "rendered": to_script(raw, script) if script else raw,
        "lang": lang["code"],
    }


def health_payload() -> dict:
    return {"ok": True, "languages": sorted(languages.agent_ids())}


def write_bytes(h, code: int, body: bytes, ctype: str, cache: str = "no-store") -> None:
    """Reply on any BaseHTTPRequestHandler - ours below, or Vercel's in api/."""
    h.send_response(code)
    h.send_header("Content-Type", ctype)
    h.send_header("Content-Length", str(len(body)))
    h.send_header("Cache-Control", cache)
    h.end_headers()
    try:
        h.wfile.write(body)
    except (BrokenPipeError, ConnectionResetError):
        pass


def write_json(h, code: int, obj, cache: str = "no-store") -> None:
    write_bytes(h, code, json.dumps(obj, ensure_ascii=False).encode(),
                "application/json; charset=utf-8", cache)


def query_arg(path: str, key: str, default: str = "") -> str:
    return (parse_qs(urlparse(path).query).get(key) or [default])[0]


# ---------------------------------------------------------------------- server


class Handler(BaseHTTPRequestHandler):
    server_version = "LanguageStation"

    def log_message(self, fmt: str, *args) -> None:
        if "/api/" in (self.path or ""):
            sys.stderr.write(f"  {self.command} {self.path.split('?')[0]}\n")

    def _send(self, code: int, body: bytes, ctype: str, cache: str = "no-store") -> None:
        write_bytes(self, code, body, ctype, cache)

    def _json(self, obj, code: int = 200) -> None:
        write_json(self, code, obj)

    def do_GET(self) -> None:
        route = urlparse(self.path)
        path, qs = route.path, parse_qs(route.query)
        arg = lambda k, d="": (qs.get(k) or [d])[0]  # noqa: E731

        if path in ("/", "/index.html", "/station"):
            try:
                html = open(os.path.join(HERE, "station.html"), "rb").read()
            except FileNotFoundError:
                return self._send(500, b"station.html is missing", "text/plain")
            return self._send(200, html, "text/html; charset=utf-8")

        if path == "/api/config":
            return self._json(config_payload())

        if path == "/api/token":
            code, body = token_payload(arg("lang"), arg("pass"))
            return self._json(body, code)

        if path == "/api/say":
            code, out = say_payload(arg("lang"), arg("text"))
            if isinstance(out, bytes):
                return self._send(code, out, "audio/wav", cache=SAY_CACHE)
            return self._json(out, code)

        if path == "/api/name":
            code, body = name_payload(arg("lang"), arg("name"))
            return self._json(body, code)

        if path == "/api/health":
            return self._json(health_payload())

        return self._send(404, b"not found", "text/plain")


def serve() -> None:
    api_key()
    os.makedirs(CACHE_DIR, exist_ok=True)
    ids = languages.agent_ids()
    missing = [l["code"] for l in languages.LANGUAGES if l["code"] not in ids]
    httpd = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Language station -> http://127.0.0.1:{PORT}/")
    print(f"  languages {', '.join(l['code'] for l in languages.LANGUAGES)}"
          + (f"   MISSING AGENTS: {', '.join(missing)}" if missing else ""))
    print(f"  cache     {CACHE_DIR}")
    print(f"  session   {SESSION_SECONDS}s, idle reset {IDLE_SECONDS}s")
    print("  Ctrl-C to stop.\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


# ------------------------------------------------------------------------- cli


def cmd_langs() -> int:
    ids = languages.agent_ids()
    for lang in languages.LANGUAGES:
        secs = languages.sections_for(lang)
        print(f"  {lang['code']}  {lang['english']:<9} {lang['native']:<10} "
              f"{sum(len(s['rows']) for s in secs):>3} rows  "
              f"script={lang['script'] or '-':<3} "
              f"{ids.get(lang['code'], 'NO AGENT'):<28} {lang['voice_name']}")
    return 0


def cmd_check() -> int:
    ok = True
    print("key      ", end="")
    k = api_key()
    print(f"loaded ({len(k)} chars, {k[:4]}...)")

    print("token    ", end="")
    try:
        print("minted" if mint_token(120).get("token") else "unexpected reply")
    except Exception as e:
        print(f"FAILED {type(e).__name__}: {e}")
        ok = False

    ids = languages.agent_ids()
    print("agents")
    for lang in languages.LANGUAGES:
        code = lang["code"]
        aid = ids.get(code)
        if not aid:
            print(f"  BAD {code}  no agent - run agent/create_agents.py")
            ok = False
            continue
        try:
            a = agent_state(aid)
        except Exception as e:
            print(f"  BAD {code}  {type(e).__name__}: {e}")
            ok = False
            continue
        voice = ((a.get("audio") or {}).get("output") or {}).get("voice")
        kt = len(((a.get("audio") or {}).get("input") or {}).get("keyterms") or [])
        problems = []
        # `language` drives speech-to-text. "en" is load-bearing: set it to the
        # target language and the agent stops hearing anything at all.
        if a.get("language") != "en":
            problems.append(f"language={a.get('language')!r} must be 'en'")
        if voice != lang["voice"]:
            problems.append(f"voice={voice!r} != {lang['voice']!r}")
        if not (a.get("instructions") or ""):
            problems.append("no instructions")
        flag = "ok " if not problems else "BAD"
        print(f"  {flag} {code}  {a.get('name'):<12} keyterms={kt:<3} {lang['voice_name']}")
        for p in problems:
            print(f"        ^ {p}")
        ok = ok and not problems

    print("tts      ", end="")
    try:
        for lang in languages.LANGUAGES:
            synth_wav(lang["hello"], lang["code"], lang["voice"])
        print(f"ok (all {len(languages.LANGUAGES)} languages speak)")
    except Exception as e:
        print(f"FAILED {type(e).__name__}: {e}")
        ok = False

    print("fonts    ", end="")
    try:
        out = subprocess.run(["fc-list", ":lang=or", "family"], capture_output=True,
                             text=True, timeout=15).stdout
        fams = {f.split(",")[0] for f in out.strip().splitlines() if f.strip()}
        want = [f for f in ("Baloo Bhaina 2", "Noto Sans Oriya") if f in fams]
        print(", ".join(want) if want else "NO ODIA FONT FOUND")
        ok = ok and bool(want)
    except FileNotFoundError:
        print("fc-list not installed (skipped; macOS ships these fonts)")
    except Exception as e:
        print(f"skipped ({type(e).__name__})")

    print("\n" + ("all good" if ok else "something above needs fixing"))
    return 0 if ok else 1


def cmd_say(args: list[str]) -> int:
    if len(args) < 2:
        print('usage: server.py say <lang> "<text>"')
        return 1
    lang = resolve(args[0])
    text = " ".join(args[1:])
    wav = synth_wav(text, lang["code"], lang["voice"])
    path = os.path.join(CACHE_DIR, "_last.wav")
    os.makedirs(CACHE_DIR, exist_ok=True)
    open(path, "wb").write(wav)
    print(f"[{lang['code']}] {text}  ({len(wav)} bytes, {lang['voice_name']})")
    subprocess.run(["afplay", path], check=False)
    return 0


def cmd_name(args: list[str]) -> int:
    if len(args) < 2:
        print("usage: server.py name <lang> <name>")
        return 1
    lang = resolve(args[0])
    raw = " ".join(args[1:])
    rendered = to_script(raw, lang["script"]) if lang["script"] else raw
    print(f"{raw}  ->  {rendered}   ({lang['english']})")
    path = os.path.join(CACHE_DIR, "_name.wav")
    os.makedirs(CACHE_DIR, exist_ok=True)
    open(path, "wb").write(synth_wav(rendered, lang["code"], lang["voice"]))
    subprocess.run(["afplay", path], check=False)
    return 0


def cmd_warm(args: list[str]) -> int:
    codes = args or [l["code"] for l in languages.LANGUAGES]
    done = failed = 0
    for code in codes:
        lang = languages.BY_CODE.get(code)
        if not lang:
            print(f"  ?? unknown language {code}")
            continue
        phrases = languages.spoken_rows(lang)
        bad = 0
        for text in phrases:
            try:
                synth_wav(text, lang["code"], lang["voice"])
                done += 1
            except Exception as e:
                bad += 1
                failed += 1
                print(f"  FAIL {code} {text!r}  ({type(e).__name__}: {e})")
        print(f"  {code}  {len(phrases) - bad}/{len(phrases)} cached")
    print(f"\ncached {done}, failed {failed} -> {CACHE_DIR}")
    return 0 if not failed else 1


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "serve"
    rest = sys.argv[2:]
    if cmd == "serve":
        serve()
        return 0
    if cmd == "check":
        return cmd_check()
    if cmd == "langs":
        return cmd_langs()
    if cmd == "say":
        return cmd_say(rest)
    if cmd == "name":
        return cmd_name(rest)
    if cmd == "warm":
        return cmd_warm(rest)
    print(__doc__)
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RuntimeError as e:
        sys.exit(str(e))
