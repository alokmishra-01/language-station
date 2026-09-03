#!/usr/bin/env python3
"""Speak TO the agent using TTS-generated audio, to find out what its STT can hear.

This answers the design-critical question for the language station: the kids will
speak English, but can the agent understand Odia at all (e.g. from a parent)?

  uv run --with websockets python test_hearing.py <agent_id> en "How do you say thank you?"
  uv run --with websockets python test_hearing.py <agent_id> or "ମୁଁ ଓଡ଼ିଆ ଜାଣେ"

Watch for `turn_ended [user]` -- that is the STT transcript. Empty or absent means
the agent heard nothing.
"""

import asyncio
import base64
import json
import os
import re
import sys
import urllib.request

ENV = os.path.expanduser("~/Documents/digital-brain/.env")
API = "https://api.cartesia.ai"
WS_VERSION = "2026-08-14"
REST_VERSION = "2025-04-16"
RATE = 44100
CHUNK_MS = 50
ENGLISH_VOICE = "db6b0ed5-d5d3-463d-ae85-518a07d3c2b4"
ODIA_VOICE = "0046dfd7-171b-4442-9eb7-0712fa712a7a"


def api_key() -> str:
    for line in open(ENV, encoding="utf-8"):
        m = re.match(r"^CARTESIA_KEY=(.*)$", line.strip())
        if m:
            return m.group(1).strip().strip("\"'")
    sys.exit("CARTESIA_KEY not found")


def post(path: str, key: str, body: dict, raw: bool = False):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode(), method="POST")
    req.add_header("X-API-Key", key)
    req.add_header("Cartesia-Version", REST_VERSION)
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as r:
        return r.read() if raw else json.loads(r.read())


def synth(key: str, text: str, lang: str) -> bytes:
    """Raw pcm_s16le @44.1k, matching the agent's pcm_44100 input format."""
    return post(
        "/tts/bytes",
        key,
        {
            "model_id": "sonic-3.6",
            "transcript": text,
            "language": lang,
            "voice": {"mode": "id", "id": ODIA_VOICE if lang == "or" else ENGLISH_VOICE},
            "output_format": {"container": "raw", "encoding": "pcm_s16le", "sample_rate": RATE},
        },
        raw=True,
    )


async def run(agent_id: str, lang: str, text: str) -> None:
    import websockets

    key = api_key()
    utterance = synth(key, text, lang)
    print(f"utterance: {len(utterance)} bytes = {len(utterance)/2/RATE:.2f}s  [{lang}] {text!r}")

    tok = post("/access-token", key, {"grants": {"agent": True}, "expires_in": 900})["token"]
    url = (f"wss://api.cartesia.ai/v1/agents/websocket/{agent_id}"
           f"?cartesia_version={WS_VERSION}&access_token={tok}")

    async with websockets.connect(url, open_timeout=15, max_size=8 << 20) as ws:
        await ws.send(json.dumps({
            "type": "session_create",
            "audio": {"input_format": "pcm_44100", "output_delivery": "as_available"},
        }))

        step = int(RATE * 2 * CHUNK_MS / 1000)
        silence = base64.b64encode(b"\x00" * step).decode()
        ready = asyncio.Event()
        sent = asyncio.Event()

        async def talk() -> None:
            await ready.wait()
            # let the agent finish its greeting, then speak
            for _ in range(int(6000 / CHUNK_MS)):
                await ws.send(json.dumps({"type": "audio_input", "audio": silence}))
                await asyncio.sleep(CHUNK_MS / 1000)
            print("  >> speaking now")
            for off in range(0, len(utterance), step):
                frame = utterance[off:off + step].ljust(step, b"\x00")
                await ws.send(json.dumps(
                    {"type": "audio_input", "audio": base64.b64encode(frame).decode()}))
                await asyncio.sleep(CHUNK_MS / 1000)
            sent.set()
            # keep the stream alive so the turn can close and a reply arrive
            while True:
                await ws.send(json.dumps({"type": "audio_input", "audio": silence}))
                await asyncio.sleep(CHUNK_MS / 1000)

        pump = asyncio.create_task(talk())
        agent_audio = 0
        try:
            while True:
                msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=25))
                t = msg.get("type")
                if t == "audio_output":
                    agent_audio += len(base64.b64decode(msg.get("audio") or ""))
                elif t == "session_ready":
                    ready.set()
                    print(f"  session_ready version={msg.get('agent_version_id')}")
                elif t == "turn_ended":
                    role = msg.get("role") or msg.get("speaker") or "?"
                    print(f"  turn_ended [{role}]: {(msg.get('text') or '')!r}")
                elif t == "error":
                    print(f"  ERROR: {json.dumps(msg)[:300]}")
        except asyncio.TimeoutError:
            print("  (quiet 25s, stopping)")
        except Exception as e:
            print(f"  closed: {type(e).__name__}: {str(e)[:140]}")
        finally:
            pump.cancel()
        print(f"  agent audio total: {agent_audio/2/RATE:.2f}s")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    asyncio.run(run(sys.argv[1], sys.argv[2], " ".join(sys.argv[3:])))
