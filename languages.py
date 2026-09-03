#!/usr/bin/env python3
"""The languages the station offers: voices, content, and teaching notes.

>>> REVIEW THE CONTENT BEFORE THE EVENT. <<<
Everything on screen and every word spoken comes from this file. I am confident
about the German, Spanish, French and Hindi rows and reasonably confident about
Odia; the Kannada and Telugu rows are common, well-attested vocabulary but I am
not a speaker of either, so please have someone check them. Anything you change
here changes the station -- re-run `python3 server.py warm` afterwards.

Row shape is (native, hint, english):
  * for a non-Latin script, `hint` is the romanisation -- also roughly what
    English speech-to-text hears when a child attempts the word;
  * for German/Spanish/French, `hint` is an English-speaker pronunciation cue,
    which is more use to a nine-year-old than a phonetic romanisation.
"""

from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
AGENTS_FILE = os.path.join(HERE, "agents.json")


# --------------------------------------------------------------------- Odia
OR = {
    "code": "or",
    "english": "Odia",
    "native": "ଓଡ଼ିଆ",
    "hello": "ନମସ୍କାର",
    "hello_hint": "namaskara",
    "script": "or",                      # drives name transliteration
    "voice": "0046dfd7-171b-4442-9eb7-0712fa712a7a",
    "voice_name": "Smruti - Precise Anchor",
    # Alternatives if Smruti reads too formal for children:
    #   b2a31ee9-7373-4122-852d-eec9576e2fa6  Rian - Supportive Communicator
    #   3cd7da94-509d-4a2a-b0f0-67fd39fe4e8e  Geeta - Informative Curator
    "agent_name": "Smruti",
    "region": "in Odisha, on the east coast of India",
    "facts": [
        "Odia is one of India's classical languages.",
        "It is spoken in Odisha, on the east coast of India.",
        "Its letters are round because they were written on palm leaves - "
        "straight lines would tear the leaf.",
        "Odia writes numbers with its own symbols, not the ones English uses. The number cards on the screen show them.",
    ],
    "greetings": [
        ("ନମସ୍କାର", "namaskaara", "hello"),
        ("ଧନ୍ୟବାଦ", "dhanyabaada", "thank you"),
        ("ଆଚ୍ଛା", "achhaa", "okay / alright"),
        ("ବିଦାୟ", "bidaaya", "goodbye"),
        ("ତୁମ ନାମ କଣ?", "tuma naama kana?", "what is your name?"),
        ("ମୋ ନାମ ...", "mo naama ...", "my name is ..."),
        ("କେମିତି ଅଛ?", "kemiti achha?", "how are you?"),
        ("ମୁଁ ଭଲ ଅଛି", "mun bhala achhi", "I am well"),
    ],
    "numbers": [
        # (numeral, word, romanisation, value): the numeral is what a child sees,
        # the word is what gets spoken and what the guide teaches from.
        ("୧", "ଏକ", "eka", "1"), ("୨", "ଦୁଇ", "dui", "2"), ("୩", "ତିନି", "tini", "3"),
        ("୪", "ଚାରି", "chaari", "4"), ("୫", "ପାଞ୍ଚ", "paancha", "5"), ("୬", "ଛଅ", "chhaa", "6"),
        ("୭", "ସାତ", "saata", "7"), ("୮", "ଆଠ", "aatha", "8"), ("୯", "ନଅ", "naa", "9"),
        ("୧୦", "ଦଶ", "dasha", "10"),
    ],
    "colours": [
        ("ଲାଲ", "laala", "red"), ("ନୀଳ", "niila", "blue"),
        ("ସବୁଜ", "sabuja", "green"), ("ହଳଦିଆ", "haladiaa", "yellow"),
        ("ଧଳା", "dhalaa", "white"), ("କଳା", "kalaa", "black"),
    ],
    "family": [
        ("ମା", "maa", "mother"), ("ବାପା", "baapaa", "father"),
        ("ଭାଇ", "bhaai", "brother"), ("ଭଉଣୀ", "bhauunii", "sister"),
    ],
    "vowels": [
        ("ଅ", "a", "as in 'up'"), ("ଆ", "aa", "as in 'father'"),
        ("ଇ", "i", "as in 'sit'"), ("ଈ", "ii", "as in 'see'"),
        ("ଉ", "u", "as in 'put'"), ("ଊ", "uu", "as in 'boot'"),
        ("ଏ", "e", "as in 'bed'"), ("ଐ", "ai", "as in 'aisle'"),
        ("ଓ", "o", "as in 'go'"), ("ଔ", "au", "as in 'cow'"),
    ],
    "letters": [
        ("କ", "ka", "କଲମ  kalama - pen"), ("ଖ", "kha", "ଖରାପ  kharaapa - bad"),
        ("ଗ", "ga", "ଗଛ  gachha - tree"), ("ଘ", "gha", "ଘର  ghara - house"),
        ("ଚ", "cha", "ଚନ୍ଦ୍ର  chandra - moon"), ("ଜ", "ja", "ଜଳ  jala - water"),
        ("ଟ", "ta", "ଟମାଟୋ  tamato - tomato"), ("ତ", "ta", "ତାରା  taaraa - star"),
        ("ଦ", "da", "ଦିନ  dina - day"), ("ନ", "na", "ନଦୀ  nadii - river"),
        ("ପ", "pa", "ପାଣି  paani - water"), ("ଫ", "pha", "ଫୁଲ  phula - flower"),
        ("ବ", "ba", "ବହି  bahi - book"), ("ଭ", "bha", "ଭାତ  bhaata - rice"),
        ("ମ", "ma", "ମା  maa - mother"), ("ର", "ra", "ରାତି  raati - night"),
        ("ଲ", "la", "ଲାଲ  laala - red"), ("ସ", "sa", "ସୂର୍ଯ୍ୟ  suurya - sun"),
        ("ହ", "ha", "ହାତ  haata - hand"),
    ],
    # Deliberately empty rather than invented. Add one and it gets its own card.
    "twister": None,
}

# -------------------------------------------------------------------- Hindi
HI = {
    "code": "hi",
    "english": "Hindi",
    "native": "हिन्दी",
    "hello": "नमस्ते",
    "hello_hint": "namaste",
    "script": "hi",
    "voice": "a81fccdc-5595-4dfc-ae76-4de6a515b8a2",
    "voice_name": "Meera - Bright Companion",
    "agent_name": "Meera",
    "region": "across northern India",
    "facts": [
        "Hindi is written in Devanagari, the same script as Sanskrit and Marathi.",
        "Devanagari letters hang from a line along the top, called the shirorekha.",
        "Hindi writes numbers with its own symbols, not the ones English uses. The number cards on the screen show them.",
        "Hindi and Urdu are close enough that speakers understand each other easily.",
    ],
    "greetings": [
        ("नमस्ते", "namaste", "hello"),
        ("धन्यवाद", "dhanyavaad", "thank you"),
        ("अच्छा", "achchha", "okay / I see"),
        ("अलविदा", "alvida", "goodbye"),
        ("तुम्हारा नाम क्या है?", "tumhaara naam kya hai?", "what is your name?"),
        ("मेरा नाम ... है", "mera naam ... hai", "my name is ..."),
        ("कैसे हो?", "kaise ho?", "how are you?"),
        ("मैं ठीक हूँ", "main theek hoon", "I am fine"),
    ],
    "numbers": [
        # (numeral, word, romanisation, value): the numeral is what a child sees,
        # the word is what gets spoken and what the guide teaches from.
        ("१", "एक", "ek", "1"), ("२", "दो", "do", "2"), ("३", "तीन", "teen", "3"),
        ("४", "चार", "chaar", "4"), ("५", "पाँच", "paanch", "5"), ("६", "छह", "chhah", "6"),
        ("७", "सात", "saat", "7"), ("८", "आठ", "aath", "8"), ("९", "नौ", "nau", "9"),
        ("१०", "दस", "das", "10"),
    ],
    "colours": [
        ("लाल", "laal", "red"), ("नीला", "neela", "blue"),
        ("हरा", "hara", "green"), ("पीला", "peela", "yellow"),
        ("सफ़ेद", "safed", "white"), ("काला", "kaala", "black"),
    ],
    "family": [
        ("माँ", "maa", "mother"), ("पिता", "pita", "father"),
        ("भाई", "bhai", "brother"), ("बहन", "behan", "sister"),
    ],
    "vowels": [
        ("अ", "a", "as in 'up'"), ("आ", "aa", "as in 'father'"),
        ("इ", "i", "as in 'sit'"), ("ई", "ii", "as in 'see'"),
        ("उ", "u", "as in 'put'"), ("ऊ", "uu", "as in 'boot'"),
        ("ए", "e", "as in 'bed'"), ("ऐ", "ai", "as in 'aisle'"),
        ("ओ", "o", "as in 'go'"), ("औ", "au", "as in 'cow'"),
    ],
    "letters": [],
    "twister": None,
}

# ------------------------------------------------------------------ Kannada
KN = {
    "code": "kn",
    "english": "Kannada",
    "native": "ಕನ್ನಡ",
    "hello": "ನಮಸ್ಕಾರ",
    "hello_hint": "namaskara",
    "script": "kn",
    # Kannada has only two voices in the whole library; happily one is cheerful.
    "voice": "7c6219d2-e8d2-462c-89d8-7ecba7c75d65",
    "voice_name": "Divya - Joyful Narrator",
    "agent_name": "Divya",
    "region": "in Karnataka, in southern India",
    "facts": [
        "Kannada is one of India's classical languages, over 1,500 years old.",
        "It is spoken in Karnataka, whose capital is Bengaluru.",
        "Kannada and Telugu scripts look alike because they share an ancestor.",
        "Kannada writes numbers with its own symbols, not the ones English uses. The number cards on the screen show them.",
    ],
    "greetings": [
        ("ನಮಸ್ಕಾರ", "namaskaara", "hello"),
        ("ಧನ್ಯವಾದ", "dhanyavaada", "thank you"),
        ("ಸರಿ", "sari", "okay / alright"),
        ("ನಿಮ್ಮ ಹೆಸರು ಏನು?", "nimma hesaru eenu?", "what is your name?"),
        ("ನನ್ನ ಹೆಸರು ...", "nanna hesaru ...", "my name is ..."),
        ("ಹೇಗಿದ್ದೀರಾ?", "heegiddeeraa?", "how are you?"),
        ("ಚೆನ್ನಾಗಿದ್ದೇನೆ", "chennaagiddeene", "I am well"),
    ],
    "numbers": [
        # (numeral, word, romanisation, value): the numeral is what a child sees,
        # the word is what gets spoken and what the guide teaches from.
        ("೧", "ಒಂದು", "ondu", "1"), ("೨", "ಎರಡು", "eradu", "2"), ("೩", "ಮೂರು", "mooru", "3"),
        ("೪", "ನಾಲ್ಕು", "naalku", "4"), ("೫", "ಐದು", "aidu", "5"), ("೬", "ಆರು", "aaru", "6"),
        ("೭", "ಏಳು", "eelu", "7"), ("೮", "ಎಂಟು", "entu", "8"), ("೯", "ಒಂಬತ್ತು", "ombattu", "9"),
        ("೧೦", "ಹತ್ತು", "hattu", "10"),
    ],
    "colours": [
        ("ಕೆಂಪು", "kempu", "red"), ("ನೀಲಿ", "neeli", "blue"),
        ("ಹಸಿರು", "hasiru", "green"), ("ಹಳದಿ", "haladi", "yellow"),
        ("ಬಿಳಿ", "bili", "white"), ("ಕಪ್ಪು", "kappu", "black"),
    ],
    "family": [
        ("ಅಮ್ಮ", "amma", "mother"), ("ಅಪ್ಪ", "appa", "father"),
        ("ಅಣ್ಣ", "anna", "elder brother"), ("ಅಕ್ಕ", "akka", "elder sister"),
    ],
    "vowels": [
        ("ಅ", "a", "as in 'up'"), ("ಆ", "aa", "as in 'father'"),
        ("ಇ", "i", "as in 'sit'"), ("ಈ", "ii", "as in 'see'"),
        ("ಉ", "u", "as in 'put'"), ("ಊ", "uu", "as in 'boot'"),
        ("ಎ", "e", "as in 'bed'"), ("ಐ", "ai", "as in 'aisle'"),
        ("ಒ", "o", "as in 'go'"), ("ಔ", "au", "as in 'cow'"),
    ],
    "letters": [],
    "twister": None,
}

# ------------------------------------------------------------------- Telugu
TE = {
    "code": "te",
    "english": "Telugu",
    "native": "తెలుగు",
    "hello": "నమస్కారం",
    "hello_hint": "namaskaaram",
    "script": "te",
    "voice": "cf061d8b-a752-4865-81a2-57570a6e0565",
    "voice_name": "Ramya - Graceful Host",
    "agent_name": "Ramya",
    "region": "in Andhra Pradesh and Telangana, in southern India",
    "facts": [
        "Telugu is one of India's classical languages.",
        "It is spoken in Andhra Pradesh and Telangana.",
        "Its round, looping letters get it the nickname 'the Italian of the East'.",
        "Telugu writes numbers with its own symbols, not the ones English uses. The number cards on the screen show them.",
    ],
    "greetings": [
        ("నమస్కారం", "namaskaaram", "hello"),
        ("ధన్యవాదాలు", "dhanyavaadaalu", "thank you"),
        ("సరే", "sare", "okay / alright"),
        ("మీ పేరు ఏమిటి?", "mee peru emiti?", "what is your name?"),
        ("నా పేరు ...", "naa peru ...", "my name is ..."),
        ("ఎలా ఉన్నారు?", "elaa unnaaru?", "how are you?"),
        ("బాగున్నాను", "baagunnaanu", "I am well"),
    ],
    "numbers": [
        # (numeral, word, romanisation, value): the numeral is what a child sees,
        # the word is what gets spoken and what the guide teaches from.
        ("౧", "ఒకటి", "okati", "1"), ("౨", "రెండు", "rendu", "2"), ("౩", "మూడు", "moodu", "3"),
        ("౪", "నాలుగు", "naalugu", "4"), ("౫", "ఐదు", "aidu", "5"), ("౬", "ఆరు", "aaru", "6"),
        ("౭", "ఏడు", "edu", "7"), ("౮", "ఎనిమిది", "enimidi", "8"), ("౯", "తొమ్మిది", "tommidi", "9"),
        ("౧౦", "పది", "padi", "10"),
    ],
    "colours": [
        ("ఎరుపు", "erupu", "red"), ("నీలం", "neelam", "blue"),
        ("ఆకుపచ్చ", "aakupachcha", "green"), ("పసుపు", "pasupu", "yellow"),
        ("తెలుపు", "telupu", "white"), ("నలుపు", "nalupu", "black"),
    ],
    "family": [
        ("అమ్మ", "amma", "mother"), ("నాన్న", "naanna", "father"),
        ("అన్న", "anna", "elder brother"), ("అక్క", "akka", "elder sister"),
    ],
    "vowels": [
        ("అ", "a", "as in 'up'"), ("ఆ", "aa", "as in 'father'"),
        ("ఇ", "i", "as in 'sit'"), ("ఈ", "ii", "as in 'see'"),
        ("ఉ", "u", "as in 'put'"), ("ఊ", "uu", "as in 'boot'"),
        ("ఎ", "e", "as in 'bed'"), ("ఐ", "ai", "as in 'aisle'"),
        ("ఒ", "o", "as in 'go'"), ("ఔ", "au", "as in 'cow'"),
    ],
    "letters": [],
    "twister": None,
}

# ------------------------------------------------------------------- German
DE = {
    "code": "de",
    "english": "German",
    "native": "Deutsch",
    "hello": "Hallo",
    "hello_hint": "HAH-loh",
    "script": None,                      # Latin script: no transliteration
    "voice": "adc919b3-6ebf-47fd-8a46-27c5169d6d94",
    "voice_name": "Leni - Daymaker",
    "agent_name": "Leni",
    "region": "in Germany, Austria and much of Switzerland",
    "facts": [
        "German writes every noun with a capital letter. Haus. Hund. Kind.",
        "A glove in German is a 'hand shoe'. Handschuh.",
        "German has an extra letter, ß, which sounds like a double s.",
        "About 130 million people speak German as their first language.",
    ],
    "greetings": [
        ("Hallo", "HAH-loh", "hello"),
        ("Guten Morgen", "GOO-ten MOR-gen", "good morning"),
        ("Danke", "DAHN-keh", "thank you"),
        ("Bitte", "BIT-teh", "please / you're welcome"),
        ("Wie heißt du?", "vee HYSST doo", "what is your name?"),
        ("Ich heiße ...", "ikh HY-seh ...", "my name is ..."),
        ("Wie geht's?", "vee GAYTS", "how are you?"),
        ("Tschüss", "CHOOSS", "bye"),
    ],
    "numbers": [
        ("eins", "eynss", "1"), ("zwei", "tsvy", "2"), ("drei", "dry", "3"),
        ("vier", "feer", "4"), ("fünf", "fuunf", "5"), ("sechs", "zeks", "6"),
        ("sieben", "ZEE-ben", "7"), ("acht", "ahkht", "8"), ("neun", "noyn", "9"),
        ("zehn", "tsayn", "10"),
    ],
    "colours": [
        ("rot", "roht", "red"), ("blau", "blow", "blue"),
        ("grün", "gruun", "green"), ("gelb", "gelp", "yellow"),
        ("weiß", "vyss", "white"), ("schwarz", "shvarts", "black"),
    ],
    "family": [
        ("Mutter", "MOO-ter", "mother"), ("Vater", "FAH-ter", "father"),
        ("Bruder", "BROO-der", "brother"), ("Schwester", "SHVES-ter", "sister"),
    ],
    "vowels": [],
    "letters": [],
    "twister": ("Fischers Fritz fischt frische Fische",
                "FISH-ers frits fisht FRISH-eh FISH-eh",
                "Fischer's Fritz fishes fresh fish"),
}

# ------------------------------------------------------------------ Spanish
ES = {
    "code": "es",
    "english": "Spanish",
    "native": "Español",
    "hello": "¡Hola!",
    "hello_hint": "OH-lah",
    "script": None,
    "voice": "b4b8e2af-6139-466e-a93a-30c20d2e1fc5",
    "voice_name": "Fernanda - Friendly Guide",
    "agent_name": "Fernanda",
    "region": "in Spain and most of Latin America",
    "facts": [
        "Spanish opens a question with an upside-down mark: ¿Como estas?",
        "Spanish has a letter English does not: ñ, as in 'mañana'.",
        "It is the world's second most spoken native language, after Mandarin.",
        "In Spanish almost every letter is always said the same way, so once you "
        "know the letters you can read any word.",
    ],
    "greetings": [
        ("¡Hola!", "OH-lah", "hello"),
        ("Buenos días", "BWEH-nos DEE-as", "good morning"),
        ("Gracias", "GRAH-see-as", "thank you"),
        ("Por favor", "por fah-VOR", "please"),
        ("¿Cómo te llamas?", "KOH-mo teh YAH-mas", "what is your name?"),
        ("Me llamo ...", "meh YAH-mo ...", "my name is ..."),
        ("¿Cómo estás?", "KOH-mo es-TAHS", "how are you?"),
        ("Adiós", "ah-DYOHS", "goodbye"),
    ],
    "numbers": [
        ("uno", "OO-no", "1"), ("dos", "dohs", "2"), ("tres", "trehs", "3"),
        ("cuatro", "KWAH-tro", "4"), ("cinco", "SEEN-ko", "5"),
        ("seis", "seys", "6"), ("siete", "SYEH-teh", "7"),
        ("ocho", "OH-cho", "8"), ("nueve", "NWEH-veh", "9"),
        ("diez", "dyehs", "10"),
    ],
    "colours": [
        ("rojo", "ROH-ho", "red"), ("azul", "ah-SOOL", "blue"),
        ("verde", "VEHR-deh", "green"), ("amarillo", "ah-mah-REE-yo", "yellow"),
        ("blanco", "BLAHN-ko", "white"), ("negro", "NEH-gro", "black"),
    ],
    "family": [
        ("madre", "MAH-dreh", "mother"), ("padre", "PAH-dreh", "father"),
        ("hermano", "ehr-MAH-no", "brother"), ("hermana", "ehr-MAH-nah", "sister"),
    ],
    "vowels": [],
    "letters": [],
    "twister": ("Tres tristes tigres", "trehs TREES-tehs TEE-grehs",
                "three sad tigers"),
}

# ------------------------------------------------------------------- French
FR = {
    "code": "fr",
    "english": "French",
    "native": "Français",
    "hello": "Bonjour",
    "hello_hint": "bon-ZHOOR",
    "script": None,
    "voice": "65b25c5d-ff07-4687-a04c-da2f43ef6fa9",
    "voice_name": "Pauline - Helpful Companion",
    "agent_name": "Pauline",
    "region": "in France, and parts of Canada, Belgium, Switzerland and Africa",
    "facts": [
        "French often does not say the last letter of a word - 'Paris' ends on the 'ree'.",
        "French counts oddly above sixty. Eighty is four twenties. Quatre-vingts.",
        "French is an official language on five continents.",
        "Lots of English words are French. Menu. Ballet. Bouquet. Restaurant.",
    ],
    "greetings": [
        ("Bonjour", "bon-ZHOOR", "hello / good day"),
        ("Salut", "sah-LOO", "hi"),
        ("Merci", "mehr-SEE", "thank you"),
        ("S'il vous plaît", "seel voo PLEH", "please"),
        ("Comment tu t'appelles?", "koh-MON too tah-PELL", "what is your name?"),
        ("Je m'appelle ...", "zhuh mah-PELL ...", "my name is ..."),
        ("Ça va?", "sah VAH", "how are you?"),
        ("Au revoir", "oh ruh-VWAHR", "goodbye"),
    ],
    "numbers": [
        ("un", "uhn", "1"), ("deux", "duh", "2"), ("trois", "trwah", "3"),
        ("quatre", "KAT-ruh", "4"), ("cinq", "sank", "5"), ("six", "seess", "6"),
        ("sept", "set", "7"), ("huit", "weet", "8"), ("neuf", "nuhf", "9"),
        ("dix", "deess", "10"),
    ],
    "colours": [
        ("rouge", "roozh", "red"), ("bleu", "bluh", "blue"),
        ("vert", "vehr", "green"), ("jaune", "zhohn", "yellow"),
        ("blanc", "blahn", "white"), ("noir", "nwahr", "black"),
    ],
    "family": [
        ("mère", "mehr", "mother"), ("père", "pehr", "father"),
        ("frère", "frehr", "brother"), ("sœur", "sur", "sister"),
    ],
    "vowels": [],
    "letters": [],
    "twister": ("Un chasseur sachant chasser",
                "uhn shah-SUR sah-SHAHN shah-SAY",
                "a hunter who knows how to hunt"),
}


LANGUAGES = [OR, HI, KN, TE, DE, ES, FR]
BY_CODE = {lang["code"]: lang for lang in LANGUAGES}
DEFAULT = "or"

_SECTION_ORDER = [
    ("greetings", "Say hello", "Tap to hear it"),
    ("numbers", "Numbers", "Count along"),
    ("colours", "Colours", "Tap to hear it"),
    ("family", "Family", "Tap to hear it"),
    ("vowels", "Vowels", "The sounds it starts with"),
    ("letters", "Letters", "Tap a letter to hear it"),
]


def agent_ids() -> dict[str, str]:
    """code -> agent_id, written by agent/create_agents.py."""
    try:
        with open(AGENTS_FILE, encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def row_parts(row: tuple) -> tuple[str, str, str, str | None]:
    """One content row as (native, hint, gloss, numeral).

    Almost every row is (native, hint, gloss). Number rows in a script with its
    own digits carry a fourth thing: the numeral. It is written (numeral, word,
    hint, value) there because that is the reading order on screen -- but the
    *word* is the native thing, since `native` is what gets spoken, cached and
    taught. This keeps that invariant true everywhere and hands the glyph back
    separately for whoever wants to show it.
    """
    if len(row) == 4:
        numeral, native, hint, gloss = row
        return native, hint, gloss, numeral
    native, hint, gloss = row
    return native, hint, gloss, None


def sections_for(lang: dict) -> list[dict]:
    out = []
    for key, title, hint in _SECTION_ORDER:
        rows = lang.get(key) or []
        if not rows:
            continue
        cells = []
        for row in rows:
            native, romanised, gloss, numeral = row_parts(row)
            cell = {"native": native, "hint": romanised, "gloss": gloss}
            if numeral:
                cell["numeral"] = numeral
            cells.append(cell)
        out.append({"id": key, "title": title, "hint": hint, "rows": cells})
    if lang.get("twister"):
        a, b, c = lang["twister"]
        out.append({
            "id": "twister", "title": "Tongue twister", "hint": "Say it fast!",
            "rows": [{"native": a, "hint": b, "gloss": c}],
        })
    return out


def spoken_rows(lang: dict) -> list[str]:
    """Every phrase the screen can speak, for the offline audio cache."""
    seen, out = set(), []
    for section in sections_for(lang):
        for row in section["rows"]:
            if row["native"] not in seen:
                seen.add(row["native"])
                out.append(row["native"])
    return out


def as_json() -> dict:
    ids = agent_ids()
    return {
        "default": DEFAULT,
        "languages": [
            {
                "code": lang["code"],
                "english": lang["english"],
                "native": lang["native"],
                "hello": lang["hello"],
                "hello_hint": lang["hello_hint"],
                "agent_name": lang["agent_name"],
                "voice_name": lang["voice_name"],
                "region": lang["region"],
                "script": lang["script"],
                "has_agent": bool(ids.get(lang["code"])),
                "facts": lang["facts"],
                "sections": sections_for(lang),
            }
            for lang in LANGUAGES
        ],
    }


if __name__ == "__main__":
    ids = agent_ids()
    print(f"{len(LANGUAGES)} languages\n")
    for lang in LANGUAGES:
        secs = sections_for(lang)
        rows = sum(len(s["rows"]) for s in secs)
        have = ids.get(lang["code"])
        print(f"  {lang['code']}  {lang['english']:<9} {lang['native']:<10} "
              f"{rows:>3} rows  {len(secs)} sections  "
              f"script={lang['script'] or '-':<3} "
              f"agent={'yes' if have else 'MISSING'}  {lang['voice_name']}")
    total = sum(len(spoken_rows(l)) for l in LANGUAGES)
    print(f"\n{total} phrases to cache in total")
