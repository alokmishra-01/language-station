#!/usr/bin/env python3
"""Create or update one Cartesia agent per language, from prompt-template.md.

    python3 create_agents.py            # every language in languages.py
    python3 create_agents.py hi de      # just these
    python3 create_agents.py --dry-run  # print the prompts, touch nothing

Ids land in ../agents.json, which the server and the page read.

Facts baked in here, so nobody re-derives them:

* Managed agents live on `/agents/v1` with `Cartesia-Version: 2026-03-01`.
  `POST /agents/v1` DOES create a runnable one (201). The legacy `POST /agents`
  looks like it works but returns an unmanaged shell whose websocket 404s.
* `language` MUST be "en". It drives SPEECH-TO-TEXT, not the voice. Measured on
  the Odia agent with identical audio: "or" -> empty transcript (deaf agent),
  "en" -> "Hello, how do you say thank you?". The target language comes from
  `audio.output.voice` plus the instructions.
* PATCH goes live immediately -- `version.id` advances and the next call's
  `session_ready` reports it. There is no publish step.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

import languages  # noqa: E402

TEMPLATE = os.path.join(HERE, "prompt-template.md")
AGENTS_FILE = languages.AGENTS_FILE
BACKUP_DIR = os.path.join(HERE, "backups")

API = "https://api.cartesia.ai"
V1 = "2026-03-01"

# Latin-script languages: an English ear transcribes their words fairly well.
LATIN_HEARING = """Their attempts will reach you as ordinary English spelling, and usually
close enough to read. "Danke" may arrive as "danka", "gracias" as "gracious". **Read these
generously.** If the child was plainly having a go at the phrase you just taught, count it
as a good attempt and praise it warmly. Only ask them to repeat when what arrives has
nothing to do with the phrase."""

NONLATIN_HEARING = """Your ears are tuned to English, so when someone says {AN} {LANGUAGE} word
it arrives as rough English spelling rather than in {NATIVE_NAME} letters. {EXAMPLES}

**Read these generously.** If the child was plainly having a go at the phrase you just
taught, count it as a good attempt and praise it warmly. Do not say you did not catch it
when the sounds are anywhere close — a child hears that as failing.

Only ask them to repeat when what arrives has nothing to do with the phrase at all."""

NONLATIN_SCRIPT_RULE = """- Write every {LANGUAGE} word or phrase in **{NATIVE_NAME} script**.
  Never write {LANGUAGE} in English letters — it makes the pronunciation wrong."""

LATIN_SCRIPT_RULE = """- Write {LANGUAGE} words with their proper spelling and accents
  ({EXAMPLE}). Do not respell them phonetically."""


def api_key() -> str:
    for path in (os.path.join(ROOT, ".env"), os.path.expanduser("~/Documents/digital-brain/.env")):
        try:
            for line in open(path, encoding="utf-8"):
                m = re.match(r"^CARTESIA_KEY=(.*)$", line.strip())
                if m:
                    return m.group(1).strip().strip("\"'")
        except FileNotFoundError:
            continue
    sys.exit("CARTESIA_KEY not found")


def call(method: str, path: str, key: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method)
    req.add_header("X-API-Key", key)
    req.add_header("Cartesia-Version", V1)
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            return json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{method} {path} -> HTTP {e.code}: "
                           f"{e.read().decode(errors='replace')[:400]}") from None


ENGLISH_NUMBERS = {"1": "one", "2": "two", "3": "three", "4": "four", "5": "five",
                   "6": "six", "7": "seven", "8": "eight", "9": "nine", "10": "ten"}

# The number rule earns its place. Without it the guides counted badly: a digit or a
# numeral in the reply gets read aloud by the wrong rules, and a model with no word to
# reach for repeats the one it has. Both variants say: use the word, one at a time.
NONLATIN_NUMBER_RULE = """- **Numbers are words, never symbols.** Write every number as the \
{LANGUAGE} word from the counting list below — {EXAMPLE}. Never write a number as `1`, `2`, \
`3` and never as a {NATIVE_NAME} numeral like {NUMERALS}; those are read aloud wrong.
- **One number per sentence, with a silence between them.** Write `{COUNT_GOOD}` — never \
`{COUNT_BAD}`, which runs them into one long noise. The `<break>` tags are not spoken; they \
are the pauses the child counts in.
- **Count at most five numbers in a turn, and say each number once.** Only the ones on \
that list."""

LATIN_NUMBER_RULE = """- **Numbers are words, never digits.** Write every number as the \
{LANGUAGE} word — {EXAMPLE}. Never write `1`, `2`, `3`: a digit gets read aloud in the \
wrong language.
- **One number per sentence, with a silence between them.** Write `{COUNT_GOOD}` — never \
`{COUNT_BAD}`, which runs them into one long noise. The `<break>` tags are not spoken; they \
are the pauses the child counts in.
- **Count at most five numbers in a turn, and say each number once.**"""


def _counting_example(lang: dict, sep: str) -> str:
    """The first three number words joined by `sep`: `ଏକ. ଦୁଇ. ତିନି.` or `ଏକ, ଦୁଇ, ତିନି`."""
    parts = [languages.row_parts(r) for r in (lang.get("numbers") or [])[:3]]
    words = [native for native, _, _, _ in parts]
    return sep.join(words) + ("." if sep != ", " else "")


def _number_example(lang: dict) -> str:
    """The first three number words, spelled out: `ଏକ (one), ଦୁଇ (two), ତିନି (three)`."""
    rows = (lang.get("numbers") or [])[:3]
    parts = [languages.row_parts(r) for r in rows]
    return ", ".join(f"`{native}` ({ENGLISH_NUMBERS.get(gloss, gloss)})"
                     for native, _, gloss, _ in parts) or "the words in that list"


def _numeral_example(lang: dict) -> str:
    """The first three native numerals, as the thing NOT to write."""
    numerals = [languages.row_parts(r)[3] for r in (lang.get("numbers") or [])[:3]]
    return " ".join(f"`{n}`" for n in numerals if n) or "`1` `2` `3`"


def build_prompt(lang: dict) -> str:
    tpl = open(TEMPLATE, encoding="utf-8").read()
    non_latin = bool(lang["script"])

    vocab_lines = []
    for key, label in (("greetings", "Greetings and everyday phrases"),
                       ("numbers", "Counting"),
                       ("colours", "Colours"),
                       ("family", "Family words")):
        rows = lang.get(key) or []
        if not rows:
            continue
        parts = [languages.row_parts(r) for r in rows[:10]]
        if key == "numbers":
            # Gloss with the English *word*. Given "ଏକ (1)" a model will happily
            # echo the digit, and TTS then reads it in the wrong language.
            items = ", ".join(f"{native} ({ENGLISH_NUMBERS.get(gloss, gloss)})"
                              for native, _, gloss, _ in parts)
        else:
            items = ", ".join(f"{native} ({gloss})" for native, _, gloss, _ in parts)
        vocab_lines.append(f"- **{label}** — {items}.")
    if non_latin:
        vocab_lines.append(
            f"- **The {lang['native']} script** — name a letter, say its sound, and give a "
            f"word that starts with it.")

    if non_latin:
        examples = " ".join(
            f'{a} may come through as "{b}".' for a, b, _ in (lang["greetings"] or [])[:2]
        )
        article = "an" if lang["english"][0].lower() in "aeiou" else "a"
        hearing = NONLATIN_HEARING.format(
            LANGUAGE=lang["english"], NATIVE_NAME=lang["native"], EXAMPLES=examples,
            AN=article)
        script_rule = NONLATIN_SCRIPT_RULE.format(
            LANGUAGE=lang["english"], NATIVE_NAME=lang["native"])
        number_rule = NONLATIN_NUMBER_RULE.format(
            LANGUAGE=lang["english"], NATIVE_NAME=lang["native"],
            EXAMPLE=_number_example(lang), NUMERALS=_numeral_example(lang),
            COUNT_GOOD=_counting_example(lang, '. <break time="500ms" /> '),
            COUNT_BAD=_counting_example(lang, ", "))
    else:
        hearing = LATIN_HEARING
        script_rule = LATIN_SCRIPT_RULE.format(
            LANGUAGE=lang["english"],
            EXAMPLE=", ".join(a for a, _, _ in (lang["greetings"] or [])[:3]))
        number_rule = LATIN_NUMBER_RULE.format(
            LANGUAGE=lang["english"], EXAMPLE=_number_example(lang),
            COUNT_GOOD=_counting_example(lang, '. <break time="500ms" /> '),
            COUNT_BAD=_counting_example(lang, ", "))

    if lang.get("twister"):
        vocab_lines.append(
            f"- **A tongue twister** — \"{lang['twister'][0]}\" ({lang['twister'][2]}). "
            f"Offer it as a challenge, say it slowly first, then a bit faster.")

    return (tpl
            .replace("{AGENT_NAME}", lang["agent_name"])
            .replace("{LANGUAGE}", lang["english"])
            .replace("{NATIVE_NAME}", lang["native"])
            .replace("{REGION}", lang["region"])
            .replace("{HELLO}", lang["hello"])
            .replace("{SCRIPT_RULE}", script_rule)
            .replace("{NUMBER_RULE}", number_rule)
            .replace("{VOCAB}", "\n".join(vocab_lines))
            .replace("{FACTS}", "\n".join(f"  - {f}" for f in lang["facts"]))
            .replace("{HEARING}", hearing))


def build_intro(lang: dict) -> str:
    """The greeting every child hears first, paced so the word survives.

    Measured on the live agent rather than assumed. Punctuation buys almost nothing inside
    a multi-sentence turn: a full stop between sentences is only ~0.3 s of quiet, a dash
    ~0.2 s, and *nothing* buys quiet after a native word. `<break time="..." />` is the one
    lever that works — the pipeline turns it into exactly that much silence and strips it
    from the transcript, so nobody hears the tag. Probed: this greeting runs 5.76 s without
    the tags and 6.46 s with one 700 ms tag, +0.70 s to the millisecond.

    So: a break after the opening greeting to let it land, and a break before the closing
    one, which goes last where the end of the turn adds its own quiet.
    """
    # "¡Hola!" already carries its own punctuation; don't end up with "¡Hola!!".
    hello = lang["hello"]
    lead = hello if hello[-1] in "!?." else hello + "!"
    last = hello if hello[-1] in "!?." else hello + "."
    return (f'{lead} <break time="500ms" /> That is hello in {lang["english"]}. '
            f'My name is {lang["agent_name"]}. Say it with me. '
            f'<break time="700ms" /> {last}')


def build_keyterms(lang: dict) -> list[str]:
    """Nudge speech-to-text toward the words this station teaches."""
    terms: list[str] = []
    for key in ("greetings", "numbers", "colours", "family"):
        for row in (lang.get(key) or []):
            native, hint, _, _ = languages.row_parts(row)
            term = (hint if lang["script"] else native)
            term = re.sub(r"[¿?¡!.,]", "", term).strip()
            # single words and short phrases only; keyterms are not sentences
            if term and len(term.split()) <= 2 and term.lower() not in [t.lower() for t in terms]:
                terms.append(term)
    terms += [lang["english"], lang["agent_name"]]
    return terms[:44]


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    codes = args or [l["code"] for l in languages.LANGUAGES]

    key = None if dry else api_key()
    ids = languages.agent_ids()
    os.makedirs(BACKUP_DIR, exist_ok=True)

    for code in codes:
        lang = languages.BY_CODE.get(code)
        if not lang:
            print(f"!! unknown language {code}")
            continue

        prompt = build_prompt(lang)
        payload = {
            "name": f"station-{code}",
            "description": f"School language station - {lang['english']}",
            "instructions": prompt,
            "initial_message": build_intro(lang),
            # See the module docstring: this is STT, and it must stay "en".
            "language": "en",
            "audio": {
                "input": {"noise_suppression_level": "auto", "keyterms": build_keyterms(lang)},
                "output": {"voice": lang["voice"]},
            },
        }

        if dry:
            print(f"\n{'=' * 72}\n{code}  {lang['english']}  ({len(prompt)} chars prompt)\n{'=' * 72}")
            print(prompt[:1400])
            print(f"\n  intro: {payload['initial_message']}")
            print(f"  keyterms ({len(payload['audio']['input']['keyterms'])}): "
                  f"{payload['audio']['input']['keyterms'][:10]}")
            continue

        existing = ids.get(code)
        try:
            if existing:
                before = call("GET", f"/agents/v1/{existing}", key)
                with open(os.path.join(BACKUP_DIR, f"{existing}-v1.json"), "w",
                          encoding="utf-8") as fh:
                    json.dump(before, fh, ensure_ascii=False, indent=2)
                out = call("PATCH", f"/agents/v1/{existing}", key, payload)
                action = "updated"
            else:
                out = call("POST", "/agents/v1", key, payload)
                ids[code] = out["id"]
                action = "created"
        except RuntimeError as err:
            print(f"  {code:<3} FAILED  {err}")
            continue

        voice = ((out.get("audio") or {}).get("output") or {}).get("voice")
        kt = len(((out.get("audio") or {}).get("input") or {}).get("keyterms") or [])
        ok = voice == lang["voice"] and out.get("language") == "en"
        print(f"  {code:<3} {action:<8} {out['id']}  lang={out.get('language')!r} "
              f"voice={'ok' if voice == lang['voice'] else 'MISMATCH'} keyterms={kt} "
              f"prompt={len(out.get('instructions') or '')}  {'' if ok else '<-- CHECK'}")

    if not dry:
        with open(AGENTS_FILE, "w", encoding="utf-8") as fh:
            json.dump(ids, fh, indent=2, sort_keys=True)
        print(f"\nwrote {AGENTS_FILE}: {len(ids)} agents")


if __name__ == "__main__":
    main()
