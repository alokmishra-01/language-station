#!/usr/bin/env python3
"""Latin -> Indic script transliteration, tuned for children's NAMES.

Odia, Devanagari (Hindi), Kannada and Telugu are all abugidas with the same
phonetic slots -- a consonant carries an inherent vowel, other vowels attach as
matras, and a bare consonant takes a virama. So one engine drives all four; only
the glyph tables differ. Add a script by adding a table.

This is deliberately not a scholarly romanisation scheme. It is tuned so a kid
typing "Sophie" or "Arjun" sees something a native reader would recognise:

* `t` and `d` map to the RETROFLEX series, because that is what English names
  sound like to an Indian ear ("Tom" reads as ଟମ୍ / टम्, not ତମ୍ / तम्). For
  real vocabulary in these languages the dental series is usually right, so do
  not reuse this for words -- those are hand-written in languages.py.
* A single 'a' takes the LONG matra, so "Zara" reads as ଜାରା / ज़ारा rather than
  collapsing to two inherent vowels.
* A name ending in a consonant gets a virama, so "Tom" is ଟମ୍ / टम् not ଟମ / टम.

No network, no dependencies: it works when the wifi does not.

    python3 translit.py                    # sample names in every script
    python3 translit.py hi Priya Arjun     # one script
"""

from __future__ import annotations

# Phonetic slots, in the order every script table lists them.
_V_KEYS = ("a", "aa", "i", "ii", "u", "uu", "e", "ai", "o", "au")
_C_KEYS = (
    "k", "kh", "g", "gh", "ng",
    "ch", "chh", "j", "jh", "ny",
    "t", "th", "d", "dh", "n",
    "p", "ph", "b", "bh", "m",
    "y", "r", "l", "v", "sh", "s", "h",
)

# For each script: independent vowels, matras, consonants, virama, digits.
# Consonant order follows _C_KEYS. The `t`/`d` slots hold the RETROFLEX letters
# on purpose (see the module docstring); `th`/`dh` hold the aspirated dentals,
# which is what English "th"/"dh" spellings usually want.
_TABLES: dict[str, dict] = {
    "or": {  # Odia
        "name": "Odia",
        "vowels": "ଅ ଆ ଇ ଈ ଉ ଊ ଏ ଐ ଓ ଔ",
        "matras": " ା ି ୀ ୁ ୂ େ ୈ ୋ ୌ",
        "cons": "କ ଖ ଗ ଘ ଙ ଚ ଛ ଜ ଝ ଞ ଟ ଥ ଡ ଧ ନ ପ ଫ ବ ଭ ମ ଯ ର ଲ ୱ ଶ ସ ହ",
        "virama": "୍",
        "digits": "୦୧୨୩୪୫୬୭୮୯",
        "yglide": "ୟ",
    },
    "hi": {  # Devanagari
        "name": "Devanagari",
        "vowels": "अ आ इ ई उ ऊ ए ऐ ओ औ",
        "matras": " ा ि ी ु ू े ै ो ौ",
        "cons": "क ख ग घ ङ च छ ज झ ञ ट थ ड ध न प फ ब भ म य र ल व श स ह",
        "virama": "्",
        "digits": "०१२३४५६७८९",
        "yglide": "य",
    },
    "kn": {  # Kannada
        "name": "Kannada",
        "vowels": "ಅ ಆ ಇ ಈ ಉ ಊ ಎ ಐ ಒ ಔ",
        "matras": " ಾ ಿ ೀ ು ೂ ೆ ೈ ೊ ೌ",
        "cons": "ಕ ಖ ಗ ಘ ಙ ಚ ಛ ಜ ಝ ಞ ಟ ಥ ಡ ಧ ನ ಪ ಫ ಬ ಭ ಮ ಯ ರ ಲ ವ ಶ ಸ ಹ",
        "virama": "್",
        "digits": "೦೧೨೩೪೫೬೭೮೯",
        "yglide": "ಯ",
    },
    "te": {  # Telugu
        "name": "Telugu",
        "vowels": "అ ఆ ఇ ఈ ఉ ఊ ఎ ఐ ఒ ఔ",
        "matras": " ా ి ీ ు ూ ె ై ొ ౌ",
        "cons": "క ఖ గ ఘ ఙ చ ఛ జ ఝ ఞ ట థ డ ధ న ప ఫ బ భ మ య ర ల వ శ స హ",
        "virama": "్",
        "digits": "౦౧౨౩౪౫౬౭౮౯",
        "yglide": "య",
    },
}


class Script:
    """One script's glyph tables, plus the Latin spellings that reach them."""

    def __init__(self, code: str, spec: dict) -> None:
        self.code = code
        self.name = spec["name"]
        self.virama = spec["virama"]
        self.yglide = spec["yglide"]
        self.digits = {str(i): ch for i, ch in enumerate(spec["digits"])}

        vs = spec["vowels"].split(" ")
        ms = spec["matras"].split(" ")
        cs = spec["cons"].split(" ")
        if not (len(vs) == len(ms) == len(_V_KEYS)):
            raise ValueError(f"{code}: need {len(_V_KEYS)} vowels+matras, got {len(vs)}/{len(ms)}")
        if len(cs) != len(_C_KEYS):
            raise ValueError(f"{code}: need {len(_C_KEYS)} consonants, got {len(cs)}")

        base_v = dict(zip(_V_KEYS, zip(vs, ms)))
        # 'a' takes the long matra so names keep their syllables (see docstring).
        base_v["a"] = (base_v["a"][0], base_v["aa"][1])

        # Latin spellings -> phonetic slot. Longer keys are tried first.
        self.vowels: dict[str, tuple[str, str]] = {}
        for latin, slot in (
            ("aa", "aa"), ("ai", "ai"), ("au", "au"), ("ee", "ii"), ("ii", "ii"),
            ("oo", "uu"), ("uu", "uu"), ("ou", "au"), ("ie", "i"),
            ("a", "a"), ("e", "e"), ("i", "i"), ("o", "o"), ("u", "u"), ("y", "i"),
        ):
            self.vowels[latin] = base_v[slot]

        base_c = dict(zip(_C_KEYS, cs))
        self.cons: dict[str, str] = {}
        for latin, slot in (
            ("chh", "chh"), ("kh", "kh"), ("gh", "gh"), ("ng", "ng"), ("ch", "ch"),
            ("jh", "jh"), ("th", "th"), ("dh", "dh"), ("ph", "ph"), ("bh", "bh"),
            ("sh", "sh"), ("ss", "s"), ("ck", "k"), ("kk", "k"), ("tt", "t"),
            ("dd", "d"), ("ll", "l"), ("mm", "m"), ("nn", "n"), ("pp", "p"),
            ("bb", "b"), ("rr", "r"), ("ff", "ph"), ("gg", "g"),
            ("k", "k"), ("c", "k"), ("q", "k"), ("g", "g"), ("j", "j"), ("z", "j"),
            ("t", "t"), ("d", "d"), ("n", "n"), ("p", "p"), ("f", "ph"), ("b", "b"),
            ("m", "m"), ("y", "y"), ("r", "r"), ("l", "l"), ("v", "v"), ("w", "v"),
            ("s", "s"), ("h", "h"),
        ):
            self.cons[latin] = base_c[slot]
        self.cons["x"] = base_c["k"] + self.virama + base_c["s"]

        self.matras = {m for _, m in base_v.values() if m}
        self._max_c = max(len(k) for k in self.cons)
        self._max_v = max(len(k) for k in self.vowels)

    # -- lookups

    def vowel_at(self, s: str, i: int):
        for ln in range(min(self._max_v, len(s) - i), 0, -1):
            got = self.vowels.get(s[i:i + ln])
            if got:
                return got[0], got[1], ln
        return None

    def cons_at(self, s: str, i: int):
        if s[i] == "c" and i + 1 < len(s) and s[i + 1] in "ei":
            return self.cons["s"], 1
        for ln in range(min(self._max_c, len(s) - i), 0, -1):
            got = self.cons.get(s[i:i + ln])
            if got:
                return got, ln
        return None

    # -- the engine

    def word(self, word: str) -> str:
        s = word.lower()
        out: list[str] = []
        i = 0
        at_start = True
        prev_vowel = False

        while i < len(s):
            ch = s[i]

            if ch in self.digits:
                out.append(self.digits[ch])
                i += 1
                at_start, prev_vowel = True, False
                continue

            if not ch.isalpha():
                out.append(ch)
                i += 1
                at_start, prev_vowel = True, False
                continue

            # 'y' before a vowel is a glide, not a vowel: "Maya", "Ananya".
            if ch == "y" and not at_start and i + 1 < len(s) and self.vowel_at(s, i + 1):
                out.append(self.yglide)
                i += 1
                prev_vowel = False
                continue

            # silent trailing "e": "Kate" -> ...ଟ୍ rather than ...ଟେ
            if ch == "e" and i == len(s) - 1 and not at_start and not prev_vowel and len(s) > 3:
                out.append(self.virama)
                i += 1
                continue

            vowel = self.vowel_at(s, i)
            if vowel:
                ind, matra, ln = vowel
                if at_start or prev_vowel:
                    # After another vowel a lone 'a' is long: "Liam" -> ଲିଆମ୍
                    long_a = prev_vowel and not at_start and s[i:i + ln] == "a"
                    out.append(self.vowels["aa"][0] if long_a else ind)
                else:
                    out.append(matra)
                i += ln
                at_start, prev_vowel = False, True
                continue

            cons = self.cons_at(s, i)
            if cons:
                glyph, ln = cons
                out.append(glyph)
                i += ln
                at_start, prev_vowel = False, False
                # A bare consonant takes a virama. A following 'y' about to become
                # a glide counts as a consonant here, so "Ananya" gets ନ୍ୟ not ନୟ.
                glide_next = (i + 1 < len(s) and s[i] == "y"
                              and self.vowel_at(s, i + 1) is not None)
                if i >= len(s) or glide_next or not self.vowel_at(s, i):
                    out.append(self.virama)
                continue

            i += 1  # unmappable, skip

        text = "".join(out)
        while self.virama + self.virama in text:
            text = text.replace(self.virama + self.virama, self.virama)
        for m in self.matras:  # a virama can never sit directly before a matra
            text = text.replace(self.virama + m, m)
        return text


SCRIPTS: dict[str, Script] = {code: Script(code, spec) for code, spec in _TABLES.items()}


def to_script(text: str, script: str) -> str:
    """Transliterate a name into `script` ('or', 'hi', 'kn', 'te')."""
    sc = SCRIPTS.get(script)
    if not sc:
        return text
    return " ".join(sc.word(tok) for tok in text.split())


# Kept for the original Odia-only callers.
def to_odia(text: str) -> str:
    return to_script(text, "or")


if __name__ == "__main__":
    import sys

    args = sys.argv[1:]
    codes = [args[0]] if args and args[0] in SCRIPTS else list(SCRIPTS)
    names = [a for a in args if a not in SCRIPTS] or [
        "Alok", "Sophie", "Arjun", "Maya", "Priya", "Tom", "Ananya", "Liam", "Meera",
    ]
    w = max(len(n) for n in names)
    print("      " + "".join(f"{SCRIPTS[c].name:<16}" for c in codes))
    for n in names:
        print(f"  {n:<{w}}  " + "".join(f"{to_script(n, c):<16}" for c in codes))
