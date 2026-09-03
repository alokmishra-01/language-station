# Posters for the Odia station

Ten HTML files, seventeen A4 sheets, and **ready-made PDFs in `pdf/`**. Nothing to
install and no build step — if you just want to print, use the PDFs and ignore
everything else here.

## If you only print one thing

```
pdf/TABLE-SET-5-posters.pdf     ← five A4 posters, in the order a visitor meets them
```

Five sheets, five pieces of A4 cardboard, done. In order:

1. **Script detective** — nine scripts, all meaning *mother*. Which one is Odia?
2. **Why round?** — the answer: straight strokes split a palm leaf along the grain.
3. **Odia numerals** — write the year you were born in ୧ ୯ ୨ ୩.
4. **What's on screen** — the menu. This is the one that goes beside the monitor.
5. **Two families, one sound** — the poster that links you to the German, Spanish
   and French tables.

Then one optional extra, because it's the thing that keeps a queue occupied:

```
pdf/HANDOUT-detective-slips.pdf ← 2 slips per sheet; print 20-30 and cut in half
```

## Print settings

| setting | value | why |
|---|---|---|
| Paper | **A4** | — |
| Margins | **None** | the layout has its own 14 mm margin built in |
| Scale | **100 %** | *not* "Fit to page", which shrinks and re-centres everything |
| Background graphics | **ON** | without it the coloured panels print as white boxes |

Chrome hides the last three under **More settings**. Printing the PDFs from Preview
needs only *A4* and *Scale 100 %*.

## The full set

Every file has a matching PDF in `pdf/`. Sheet counts are verified: seventeen A4
pages, nothing clipped, no blank pages.

| # | What | Sheets | Copies |
|---|---|---|---|
| 01 | Hero band | 3 | **optional** — a 594 mm banner for a wall behind you. With a big monitor doing the attracting, you probably don't need it. Dark ground, so it's also the only ink-heavy sheet. |
| 02 | Script detective | 2 | 1 poster + 20–30 handouts (page 2, cut in half) |
| 03 | Why round? | 1 | 1 |
| 04 | Odia numerals | 1 | 1 |
| 05 | Name cards | 1 | 15–25 → four A6 cards each, so 60–100 cards |
| 06 | What's on screen | 1 | 1 |
| 07 | Features | 3 | optional — one big sheet per feature, if you have board space. 06 says the same thing on one sheet. |
| 08 | Table tents | 3 | optional — fold in half; only useful if signs can stand rather than being pasted flat |
| 09 | Two families, one sound | 1 | 1–2 (give one to the other language tables) |
| 10 | Sounds / tongue twister | 1 | 1 — **prints unfinished on purpose**, see below |

Also bring: **scissors**, **masking tape**, and **fine-tip black pens** (~0.4 mm — a
fat marker cannot draw ଓ, and a child whose name comes out as a blob won't keep the card).

## Laying out the table

```
            ┌─────────────────────────────────────┐
            │        BIG MONITOR — the app        │
            └─────────────────────────────────────┘
     ╔═══════════════════════════════════════════════════╗
     ║  [02]  [03]        headset         [06]  [04][09]  ║  ← A4 on cardboard, propped
     ║  slips + pencils                   name cards + pens
     ╚═══════════════════════════════════════════════════╝
        queue side           you              exit side
```

Three things matter more than the exact positions:

1. **The headset is the bottleneck.** One child at a time, two to three minutes each.
   Everything on the queue side exists to occupy the people waiting — that is what
   the detective slips and pencils are for, and why the answer is deliberately *not*
   printed on the slip. The only way to check it is to reach the table.
2. **Make traffic flow one way**, queue side → screen → exit side. Left hand takes a
   slip, right hand leaves with a name card. That card is your best advertising:
   the next child stops because someone their age walked past holding one.
3. **Prop the cards up, don't lay them flat.** A poster lying face-up on a table is
   invisible from two metres. Cardboard folded into an L, or leant against something,
   or bulldog-clipped to a bottle — anything that gets them near vertical.

## Worth doing before the day

Talk to the German, Spanish and French parents. Poster 09 is built for it: Odia ମା,
Hindi माँ, Latin *mater*, German *Mutter*, French *mère* are genuinely related — while
Tamil *amma* is from a completely unrelated family and sounds the same anyway, because
**m** is the first consonant a baby can make. Agree on three words with the other
tables — *two*, *three*, *night* — and children will go collecting the same word
across five stations. That costs one photocopy and makes every table busier.

## Two things a speaker should still check

Everything Odia here comes from `content.py`, which is already flagged for review.
Two additions of mine are **not** in that file and want the same treatment:

- **The eight non-Odia glyphs on 02 and 09** — Devanagari माँ / मातृ, Bengali মা,
  Gujarati મા, Gurmukhi ਮਾ, Tamil அம்மா, Telugu అమ్మ, Kannada ಅಮ್ಮ, Malayalam അമ്മ.
  They render correctly on this Mac; whether each is the word a speaker would
  actually write is worth one pair of eyes per script.
- **The dental/retroflex descriptions on 10** — ତ vs ଟ, ଦ vs ଣ.

And the honest gap: **`TONGUE_TWISTER` in `content.py` is still `None`.** Sheet 10
says so on its face, in a coral dashed box with ruled lines to write the twister on
by hand. Fill it into `content.py`, re-run `python3 server.py warm`, delete the box
from `10-tongue-twister.html`, and it appears on both paper and screen.

## Claims I checked, and one I left out

- **Round letters / palm leaves** — asserted for Odia only, which is what
  `content.py` itself says. Sheet 03 contrasts Odia with Devanagari *visually* and
  makes no claim about why Devanagari has its top bar.
- **Brahmagupta, 628 CE** (sheet 04) — he set down the arithmetic rules for zero in
  the *Brāhmasphuṭasiddhānta*. There is a popular claim tying him to Odisha; it is
  not solid, so it is not on the poster.
- **`*méh₂tēr` and `*amma`** (sheet 09) — two reconstructed ancestors from two
  unrelated families. The poster's twist, that the shared **m** proves nothing
  because babies produce it first, is the mainstream account of nursery words.

## Editing

`_print.css` holds the palette (lifted from `station.html`, inverted so deep purple
is the ink on white paper) and the A4 page machinery. Each poster has its own
`<style>` block.

Two traps, both of which bit during this build:

- **`@page { size: A4 }` in `_print.css` is load-bearing.** Remove it and Chrome
  prints at US Letter, cropping every sheet *and* adding a blank page after it.
- **Content taller than the sheet is silently clipped** by `overflow: hidden` — it
  looks fine in the browser and reaches the printer wrong. After editing, re-render
  to PDF and confirm the page count still matches the number of `.sheet` elements.
  Note that `scrollHeight` does *not* catch this on 01, whose panels are centred
  flex boxes: overflow there spills off both ends. Look at that one by eye.

```bash
# regenerate every PDF in pdf/
for f in 0*.html 1*.html; do
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    --headless=new --no-pdf-header-footer \
    --print-to-pdf="pdf/${f%.html}.pdf" "file://$PWD/$f"
done
```
