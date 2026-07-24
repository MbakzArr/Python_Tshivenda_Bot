"""Rebuild data/lexicon.json from the old dataset. Run from the project root:

    python tools/rebuild.py dataset/response.json
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.migrate import convert
from core.lexicon import Lexicon

# Entries taken straight from the old dataset/todo notes. They prove the
# sense model: one Tshivenda word, several separate English meanings.
EXTRA = [
    ("day", "duvha", "noun", "time", "", "same word as sun, context decides"),
    ("sun", "duvha", "noun", "nature", "", "same word as day, context decides"),
    ("invitation", "thambo", "noun", "general", "", "same word as rope, context decides"),
    ("rope", "thambo", "noun", "general", "", "same word as invitation, context decides"),
    ("good morning", "Ndi matsheloni", "phrase", "greeting", "start", ""),
    ("good afternoon", "Ndi masiari", "phrase", "greeting", "start", ""),
    ("good evening", "Ndi madekwana", "phrase", "greeting", "start", ""),
    ("good morning", "Ndi matsheloni avhudi", "phrase", "greeting", "response", ""),
    ("good afternoon", "Ndi masiari avhudi", "phrase", "greeting", "response", ""),
    ("good evening", "Ndi madekwana avhudi", "phrase", "greeting", "response", ""),
]


def tidy(lex):
    """The old file mixed ALL CAPS and normal case. Make it consistent."""
    n = 0
    for e in lex.entries:
        if e["en"].isupper() and len(e["en"]) > 2:
            e["en"] = e["en"].lower()
            n += 1
        if e["ve"].isupper() and len(e["ve"]) > 2:
            e["ve"] = e["ve"].capitalize()
            n += 1
        e["alt"] = [a.capitalize() if a.isupper() else a for a in e.get("alt", [])]
    return n


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "dataset/response.json"
    dest = sys.argv[2] if len(sys.argv) > 2 else "data/lexicon.json"
    convert(src, dest)

    lex = Lexicon.load(dest)
    added = 0
    for en, ve, pos, cat, ctx, note in EXTRA:
        if not lex.duplicate_of(en, ve):
            lex.add(en=en, ve=ve, pos=pos, category=cat, context=ctx, note=note)
            added += 1
    fixed = tidy(lex)
    lex.build()
    lex.save(dest)
    print("added %d extra entries, tidied %d fields" % (added, fixed))
    print(lex.stats())


if __name__ == "__main__":
    main()
