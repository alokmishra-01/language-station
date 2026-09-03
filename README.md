# Language Station

An interactive language station for a school event. A child walks up, picks a language
from the dropdown, puts on the headset, and has a short conversation with a native-voiced
guide who teaches them words to say back. The screen carries the script, the numbers, and
their own name written in that language.

Seven languages: **Odia, Hindi, Kannada, Telugu, German, Spanish, French.**

Everything runs on this Mac. The only thing that needs the internet is the live
conversation — the words, letters and name-writing keep working without it, because
their audio is pre-rendered into `cache/`. (That is true of the local station only.
A [hosted deployment](#deploy-it) has no `cache/` and needs the network for every
sound, so run the event off the Mac.)

## Run it

Double-click **`start-station.command`**. That starts the local server, blocks the screen
from sleeping, runs a preflight check, and opens Chrome in kiosk mode.
`stop-station.command` shuts it down. Leave kiosk mode with cmd-Q.

By hand:

```bash
python3 server.py serve            # then open http://127.0.0.1:8777/
python3 server.py check            # key, all seven agents, TTS, fonts
python3 server.py langs            # what is configured
python3 server.py warm             # pre-render every screen phrase (256 of them)
python3 server.py warm hi de       # ...just those languages
python3 server.py say kn "ನಮಸ್ಕಾರ"  # speak a phrase through the speakers
python3 server.py name te Sophie   # transliterate a name and say it
```

## The guides

| | Language | Guide | Voice | Script |
|---|---|---|---|---|
| `or` | Odia | Smruti | Smruti – Precise Anchor | ଓଡ଼ିଆ |
| `hi` | Hindi | Meera | Meera – Bright Companion | देवनागरी |
| `kn` | Kannada | Divya | Divya – Joyful Narrator | ಕನ್ನಡ |
| `te` | Telugu | Ramya | Ramya – Graceful Host | తెలుగు |
| `de` | German | Leni | Leni – Daymaker | Latin |
| `es` | Spanish | Fernanda | Fernanda – Friendly Guide | Latin |
| `fr` | French | Pauline | Pauline – Helpful Companion | Latin |

All native voices from Cartesia's library, chosen for warmth rather than authority —
Kannada has only two voices in the entire library and happily one of them is cheerful.
Agent ids live in `agents.json`.

## What the station does

- **Talk to the guide** — a real conversation. She greets in her language, offers two
  things to try, teaches a couple of words, and says goodbye. Sessions cap at 3½ minutes
  and the page resets itself for the next child. **It never gets stuck:** a watchdog
  re-opens a dropped socket without the child noticing, and when nothing usable is
  reaching the guide she stops asking and carries the visit herself — one word, a long
  pause, the next word — because a child in front of a guide that has gone quiet thinks
  they broke it.
- **Words & letters** — greetings, numbers, colours, family words, and for Odia the full
  vowel and consonant explorer. Tap anything to hear it. All cached as audio, so it works
  offline. A number card shows the native numeral (୧) above the word (ଏକ), and tapping it
  speaks the **word** — never the numeral, which is read aloud wrong.
- **Your name** — for Odia, Hindi, Kannada and Telugu, type a name and watch it become
  that script, then hear it. For German, Spanish and French there is nothing to
  transliterate, so it speaks the name with that language's sounds instead.

## The one thing to understand before the event

**The children speak English; the guide replies in her language.** That is not a style
choice, it is what the platform allows: Cartesia's speech-to-text only understands
English, so every agent's `language` must stay `"en"`. Setting it to the target language
looks more correct and makes the agent completely deaf — measured, with identical audio:

| agent `language` | what the agent heard |
|---|---|
| `"or"` | *(nothing — empty transcript)* |
| `"en"` | `Hello, how do you say thank you?` |

The target language comes from the **voice** and the **instructions**, never from
`language`. `server.py check` asserts this for all seven agents, so a later regression
gets caught rather than discovered mid-event.

A consequence to be honest about: **she cannot mark pronunciation.** A child's attempt
arrives as rough English spelling — ନମସ୍କାର comes through as something like "namaskar",
ମୁଁ ଓଡ଼ିଆ ଜାଣେ as "Mu Oriya jaane" — enough to know they tried, not enough to grade. Every
prompt tells the guide to read those generously and never claim she didn't catch it when
the sounds are close. Each agent also carries ~28 romanised keyterms to help.

For German, Spanish and French this is much less of a problem: English speech-to-text
transcribes their words fairly well, so a child saying "Danke" will usually be heard.

## Before the event — a short list

1. **Read `languages.py`.** Everything on screen and every spoken word comes from that
   one file. I am confident about the German, Spanish, French and Hindi rows; the
   **Kannada and Telugu rows are common vocabulary but I do not speak either language, so
   please have someone check them.** The Odia rows are worth your own eye too. The
   **number words for all four Indic languages went in late** (ଏକ ଦୁଇ ତିନି, एक दो तीन,
   ಒಂದು ಎರಡು ಮೂರು, ఒకటి రెండు మూడు) — they are the first thing to have read back to you.
2. **Tongue twisters.** German, Spanish and French have one. Odia, Hindi, Kannada and
   Telugu have `"twister": None` — deliberately, rather than my inventing one. Fill any in
   and it appears as its own card and in the guide's repertoire.
3. **Re-run `python3 server.py warm`** after any content change, and
   `python3 agent/create_agents.py` after changing a prompt or a voice.
4. **Listen to the guides.** `python3 server.py say or "ନମସ୍କାର"`. If one sounds too
   formal for children, `python3 agent/find_voices.py or` lists the alternatives — change
   `voice` in `languages.py` and re-run `create_agents.py`.
5. **Grant the microphone once** in the real browser before the day, so Chrome's
   permission prompt never appears mid-event.
6. **Check audio routing.** macOS silently moves output to a monitor's speakers. System
   Settings → Sound: both input and output on the headset.
7. **Test with the Wi-Fi off.** Talking should fail with a friendly message while the
   words and name-writing carry on.
8. **Tick "hold space to talk"** if the hall is loud. Open mic is nicer when it is quiet.

## Deploy it

The event runs on the Mac. This is for sharing it afterwards — the same station, minus
the offline safety net.

```bash
vercel                                            # preview
vercel --prod
python3 prewarm.py https://your-deploy.vercel.app # pay Cartesia once, then the CDN holds it
```

Set `CARTESIA_KEY` in Project Settings → Environment Variables. `station.html` is copied
to `public/index.html` at build time and the five routes become the functions in `api/`;
both sides call the same functions in `server.py`, so there is only ever one
implementation of each.

**Set `STATION_PASSCODE` too.** `/api/token` mints Cartesia tokens that spend real money
against your key, so a deployment without one is an open tab for anyone who finds the URL.
Unset — the default, and how the station runs at the event — means anyone who can reach
the page can talk. Set it and the page asks once and remembers.

## Layout

```
station.html            the whole kiosk UI (one file, no build step, no CDN)
server.py               local server + CLI: tokens, TTS cache, transliteration
languages.py            ALL content, voices and facts for the seven languages - review this
translit.py             Latin -> Odia / Devanagari / Kannada / Telugu, tuned for names
agents.json             language code -> Cartesia agent id
cache/                  pre-rendered audio, 256 phrases (gitignored)
.env                    CARTESIA_KEY (gitignored, mode 600) - .env.example shows the shape
api/                    the same five routes as Vercel functions; each is ~10 lines
vercel.json             build + function config for a hosted deployment
prewarm.py              warms a deployment's CDN, the hosted answer to `server.py warm`
agent/
  prompt-template.md    the guide's persona, teaching style and safety rails
  create_agents.py      fills the template per language, creates/updates the agents
  find_voices.py        browse Cartesia's 939 voices by language
  probe_call.py         silent test call; saves the greeting to a WAV
  test_hearing.py       speaks TO an agent using synthesized audio, to test its STT
  backups/              each agent's config before the last update
```

## Adding a language

Cartesia has voices for Tamil, Bengali, Marathi and plenty more, so this is mostly
content work:

1. `python3 agent/find_voices.py ta` and pick a voice id.
2. Copy a block in `languages.py`, fill in the words, add it to `LANGUAGES`.
   For a new Indic script also add a glyph table to `_TABLES` in `translit.py` — the
   engine is shared, only the letters differ — and its Unicode range to `SCRIPT_RANGES`
   and `FACE` in `station.html`.
3. `python3 agent/create_agents.py ta && python3 server.py warm ta`.

It appears in the dropdown on next load.

## Cartesia notes worth keeping

- **Odia exists only in `sonic-3.6`.** `sonic-3.5` and `sonic-3` reject language `or`
  outright, so anything pinned to an older Sonic cannot speak it at all.
- **Managed agents live on `/agents/v1` with `Cartesia-Version: 2026-03-01`.**
  `POST /agents/v1` creates a runnable one. The legacy `POST /agents` appears to work but
  returns an unmanaged shell whose websocket 404s — that dead end cost an hour.
- **`<break time="700ms" />` is the only way to slow the guide down.** Punctuation barely
  registers inside a turn — measured on Smruti, a full stop between sentences is ~0.3 s of
  quiet, a dash ~0.2 s, and *nothing at all* buys quiet after a native word. The break tag
  is honoured exactly (a greeting went 5.76 s → 6.46 s for one 700 ms tag) and is stripped
  from the transcript, so the child hears silence, never the tag. Every prompt now teaches
  it, and it is why a word the child should repeat is put last in the turn.
- **PATCH goes live immediately.** `version.id` advances and the next call's
  `session_ready` reports it. There is no publish step.
- The websocket is `wss://api.cartesia.ai/v1/agents/websocket/{id}?cartesia_version=2026-08-14`
  plus `&access_token=`, and it **closes after 120 s without a client event — ping frames
  do not count**, so the page streams silence as its keepalive.

## One trap in `station.html`

`fitText()` shrinks a native word until it fits its box. It must measure **line count**,
not width: the cards are CSS grid, so a too-long word does not overflow its cell — the grid
grows and `scrollWidth === clientWidth` reports a comfortable fit while the word sits on
three lines over the top of its neighbour. That is what made ଓଡ଼ିଆ land on top of "this?" on
the first poster. Measure `offsetHeight / lineHeight`, and never with `white-space: nowrap`,
which hides the very wrap you are looking for.
