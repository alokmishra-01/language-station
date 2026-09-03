#!/usr/bin/env python3
"""Place a silent probe call against a Cartesia agent and capture its greeting audio.

Verified protocol (docs/line/integrations/websocket-api, 2026-09):
  wss://api.cartesia.ai/v1/agents/websocket/{agent_id}?cartesia_version=2026-08-14
  browser auth -> &access_token=<tok>   |  server auth -> X-API-Key header
  client: session_create -> (wait session_ready) -> audio_input
  server: session_ready, audio_output, audio_output_clear,
          turn_started, turn_output_text_delta, turn_ended, error

Run:  uv run --with websockets python probe_call.py <agent_id> [seconds]
"""

import asyncio
import base64
import json
import os
import re
import struct
import sys
import urllib.request

ENV = os.path.expanduser("~/Documents/digital-brain/.env")
API = "https://api.cartesia.ai"
WS_VERSION = "2026-08-14"
REST_VERSION = "2025-04-16"
RATE = 44100  # pcm_44100, s16le mono
CHUNK_MS = 50


def api_key() -> str:
    for line in open(ENV, encoding="utf-8"):
        m = re.match(r"^CARTESIA_KEY=(.*)$", line.strip())
        if m:
            return m.group(1).strip().strip("\"'")
    sys.exit("CARTESIA_KEY not found")


def access_token(key: str) -> str:
    body = json.dumps({"grants": {"agent": True}, "expires_in": 900}).encode()
    req = urllib.request.Request(API + "/access-token", data=body, method="POST")
    req.add_header("X-API-Key", key)
    req.add_header("Cartesia-Version", REST_VERSION)
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["token"]


def write_wav(path: str, pcm: bytes, rate: int = RATE) -> None:
    with open(path, "wb") as f:
        f.write(b"RIFF" + struct.pack("<I", 36 + len(pcm)) + b"WAVE")
        f.write(b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, rate, rate * 2, 2, 16))
        f.write(b"data" + struct.pack("<I", len(pcm)) + pcm)


async def probe(agent_id: str, seconds: float = 20.0) -> None:
    import websockets

    key = api_key()
    tok = access_token(key)
    url = (
        f"wss://api.cartesia.ai/v1/agents/websocket/{agent_id}"
        f"?cartesia_version={WS_VERSION}&access_token={tok}"
    )
    print(f"connecting: agent={agent_id}")
    async with websockets.connect(url, open_timeout=15, max_size=8 << 20) as ws:
        await ws.send(
            json.dumps(
                {
                    "type": "session_create",
                    "audio": {"input_format": "pcm_44100", "output_delivery": "as_available"},
                }
            )
        )

        pcm = bytearray()
        text: list[str] = []
        ready = asyncio.Event()

        async def feed_silence() -> None:
            """The server closes after 120s without a client event, and ping frames
            do not count. Continuous audio (silence included) is the keepalive."""
            await ready.wait()
            frame = base64.b64encode(b"\x00" * int(RATE * 2 * CHUNK_MS / 1000)).decode()
            while True:
                await ws.send(json.dumps({"type": "audio_input", "audio": frame}))
                await asyncio.sleep(CHUNK_MS / 1000)

        pump = asyncio.create_task(feed_silence())
        try:
            while True:
                raw = await asyncio.wait_for(ws.recv(), timeout=seconds)
                msg = json.loads(raw)
                t = msg.get("type")
                if t == "audio_output":
                    pcm += base64.b64decode(msg.get("audio") or "")
                elif t == "session_ready":
                    ready.set()
                    print(f"  session_ready call_id={msg.get('call_id')}")
                    print(f"               agent_version_id={msg.get('agent_version_id')}")
                elif t == "turn_output_text_delta":
                    text.append(msg.get("delta") or msg.get("text") or "")
                elif t == "turn_ended":
                    who = msg.get("role") or msg.get("speaker") or "?"
                    print(f"  turn_ended [{who}]: {(msg.get('text') or '')[:220]}")
                elif t == "error":
                    print(f"  ERROR fatal={msg.get('fatal')}: {json.dumps(msg)[:300]}")
                elif t not in ("audio_output_clear", "turn_started"):
                    print(f"  <- {json.dumps(msg)[:220]}")
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            print(f"  closed: {type(e).__name__}: {str(e)[:160]}")
        finally:
            pump.cancel()

    secs = len(pcm) / 2 / RATE
    print(f"  agent audio: {len(pcm)} bytes = {secs:.2f}s")
    if text:
        print(f"  streamed text: {''.join(text)[:300]}")
    if pcm:
        out = f"/tmp/odia/greeting-{agent_id[-8:]}.wav"
        os.makedirs("/tmp/odia", exist_ok=True)
        write_wav(out, bytes(pcm))
        print(f"  wrote {out}   (afplay {out})")


if __name__ == "__main__":
    aid = sys.argv[1] if len(sys.argv) > 1 else sys.exit("usage: probe_call.py <agent_id> [secs]")
    asyncio.run(probe(aid, float(sys.argv[2]) if len(sys.argv) > 2 else 20.0))
