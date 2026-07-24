"""Convert the old dataset/response.json into data/lexicon.json.

The old file was a flat map of key to list of strings. Some keys were English
and some were already Tshivenda, so we detect the direction per pair instead
of assuming. Anything the detector was unsure about is flagged review=true.

Run once:  python tools/migrate.py ../dataset/response.json
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.lexicon import Lexicon
from core.text import ve_score, words, fold

CATEGORY_HINTS = [
    ("greeting", ["hello", "morning", "afternoon", "evening", "greet", "night", "welcome", "goodbye"]),
    ("family", ["father", "mother", "brother", "sister", "grandparent", "family", "cousin", "child", "aunt", "uncle", "wife", "husband"]),
    ("body", ["head", "hair", "ear", "eye", "nose", "mouth", "cheek", "jaw", "forehead", "tooth", "teeth", "hand", "leg", "foot", "arm", "finger", "neck", "back", "chest", "skin", "heart", "blood", "bone", "knee", "shoulder", "tongue", "lip", "nail", "stomach", "body"]),
    ("food", ["food", "water", "bread", "meat", "eat", "hunger", "drink", "milk", "porridge", "salt", "fruit", "vegetable", "cook"]),
    ("number", ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "hundred", "thousand", "number"]),
    ("time", ["day", "night", "week", "month", "year", "today", "tomorrow", "yesterday", "hour", "minute", "time", "morning"]),
    ("animal", ["dog", "cat", "cow", "goat", "lion", "elephant", "bird", "snake", "fish", "chicken", "animal", "horse"]),
    ("love", ["love", "lover", "sweetheart", "marry", "married", "heart", "kiss"]),
    ("nature", ["mountain", "river", "rain", "sun", "moon", "star", "tree", "stone", "wind", "fire", "sky", "earth", "cloud"]),
    ("home", ["house", "gate", "door", "room", "village", "yard", "home", "bed", "roof"]),
]

CONTEXT_SPLIT = re.compile(r"[-(](male|female|start|response|plural|singular|formal|informal)\)?\s*$", re.I)
PAREN = re.compile(r"\(([^)]*)\)")


def guess_category(en):
    low = " " + fold(en) + " "
    for cat, keys in CATEGORY_HINTS:
        for k in keys:
            if " " + k in low or low.strip().startswith(k):
                return cat
    if len(words(en)) > 2:
        return "phrase"
    return "general"


def split_context(key):
    """'Hello-male' becomes ('Hello', 'male')."""
    m = CONTEXT_SPLIT.search(key)
    if m:
        return key[:m.start()].strip(" -"), m.group(1).lower()
    return key.strip(), ""


def split_note(value):
    """'Ndala (I am hungry-Ndi na ndala)' becomes ('Ndala', 'I am hungry - Ndi na ndala')."""
    m = PAREN.search(value)
    if not m:
        return value.strip(), ""
    note = m.group(1).strip().replace("-", " - ")
    return PAREN.sub("", value).strip(), note


def convert(src, dest):
    with open(src, "r", encoding="utf-8") as f:
        old = json.load(f)

    lex = Lexicon([])
    flagged = 0
    skipped = 0

    for key, values in old.items():
        if not isinstance(values, list):
            values = [values]
        key_clean, context = split_context(str(key))
        cleaned = []
        notes = []
        for v in values:
            val, note = split_note(str(v))
            if val:
                cleaned.append(val)
            if note:
                notes.append(note)
        if not cleaned or not key_clean:
            skipped += 1
            continue

        # which side is Tshivenda
        key_score = ve_score(key_clean)
        val_score = max(ve_score(c) for c in cleaned)
        if val_score >= key_score:
            en, ve_list = key_clean, cleaned
        else:
            en, ve_list = cleaned[0], [key_clean]

        uncertain = abs(val_score - key_score) < 0.15
        if uncertain:
            flagged += 1

        primary = ve_list[0]
        alt = [v for v in ve_list[1:] if fold(v) != fold(primary)]

        if lex.duplicate_of(en, primary):
            skipped += 1
            continue

        lex.add(
            en=en,
            ve=primary,
            pos="phrase" if len(words(en)) > 2 else "",
            category=guess_category(en),
            context=context,
            note="; ".join(notes),
            alt=alt,
            review=True,
        )

    lex.save(dest)
    print("converted %d entries from %d old keys" % (len(lex.entries), len(old)))
    print("skipped %d, direction uncertain on %d" % (skipped, flagged))
    print("saved to %s" % dest)
    return lex


if __name__ == "__main__":
    source = sys.argv[1] if len(sys.argv) > 1 else "dataset/response.json"
    target = sys.argv[2] if len(sys.argv) > 2 else "data/lexicon.json"
    convert(source, target)
