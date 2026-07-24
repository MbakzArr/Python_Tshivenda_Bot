import json
import os
import random
import difflib

from core import paths
from core.text import fold, words, ve_score

LEXICON_FILE = paths.data("lexicon.json")

# One entry is one SENSE, not one word. That is how we handle the
# duvha problem from the old todo file: "duvha = day" and "duvha = sun"
# are two entries, so a reverse lookup returns both with their notes.

FIELDS = ("id", "en", "ve", "pos", "category", "context", "note", "alt", "review")


class Lexicon:
    def __init__(self, entries=None):
        self.entries = entries or []
        self.by_id = {}
        self.en_index = {}
        self.ve_index = {}
        self.build()

    # ---------- loading ----------

    @classmethod
    def load(cls, path=None):
        path = path or LEXICON_FILE
        if not os.path.exists(path):
            return cls([])
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return cls(raw.get("entries", []))

    def save(self, path=None):
        path = path or LEXICON_FILE
        payload = {"version": 2, "count": len(self.entries), "entries": self.entries}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    def build(self):
        self.by_id = {}
        self.en_index = {}
        self.ve_index = {}
        for e in self.entries:
            self.by_id[e["id"]] = e
            self._index(self.en_index, e.get("en", ""), e)
            self._index(self.ve_index, e.get("ve", ""), e)
            for a in e.get("alt", []):
                self._index(self.ve_index, a, e)

    @staticmethod
    def _index(idx, value, entry):
        key = fold(value)
        if not key:
            return
        idx.setdefault(key, [])
        if entry not in idx[key]:
            idx[key].append(entry)

    # ---------- lookup ----------

    def find_en(self, phrase):
        return list(self.en_index.get(fold(phrase), []))

    def find_ve(self, phrase):
        return list(self.ve_index.get(fold(phrase), []))

    def lookup(self, phrase):
        """Return (direction, entries). Direction is 'en-ve' or 've-en'."""
        en = self.find_en(phrase)
        ve = self.find_ve(phrase)
        if en and not ve:
            return "en-ve", en
        if ve and not en:
            return "ve-en", ve
        if en and ve:
            # word exists on both sides, let the shape of the string decide
            return ("ve-en", ve) if ve_score(phrase) > 0.45 else ("en-ve", en)
        return None, []

    def near(self, phrase, side="both", limit=5, cutoff=0.78):
        """Fuzzy suggestions for a word that was not found."""
        key = fold(phrase)
        pool = []
        if side in ("both", "en"):
            pool += list(self.en_index.keys())
        if side in ("both", "ve"):
            pool += list(self.ve_index.keys())
        return difflib.get_close_matches(key, pool, n=limit, cutoff=cutoff)

    def search(self, term, limit=25):
        """Substring search across both sides."""
        key = fold(term)
        if not key:
            return []
        hits = []
        for e in self.entries:
            hay = fold(e.get("en", "")) + " " + fold(e.get("ve", "")) + " " + \
                  " ".join(fold(a) for a in e.get("alt", []))
            if key in hay:
                hits.append(e)
            if len(hits) >= limit:
                break
        return hits

    def senses_of(self, phrase):
        """Every meaning of a word, both directions. Powers /define."""
        seen = []
        for e in self.find_en(phrase) + self.find_ve(phrase):
            if e not in seen:
                seen.append(e)
        return seen

    # ---------- collections ----------

    def categories(self):
        c = {}
        for e in self.entries:
            cat = e.get("category") or "general"
            c[cat] = c.get(cat, 0) + 1
        return dict(sorted(c.items(), key=lambda x: -x[1]))

    def in_category(self, cat):
        return [e for e in self.entries if (e.get("category") or "general") == cat]

    def single_words(self):
        """Entries that are one word on both sides. Best for quizzing."""
        out = []
        for e in self.entries:
            if len(words(e.get("en", ""))) == 1 and len(words(e.get("ve", ""))) == 1:
                out.append(e)
        return out

    def phrases(self):
        return [e for e in self.entries if len(words(e.get("en", ""))) > 1]

    def pick(self, pool=None, seed=None):
        pool = pool if pool is not None else self.entries
        if not pool:
            return None
        rng = random.Random(seed) if seed is not None else random
        return rng.choice(pool)

    # ---------- editing ----------

    def next_id(self):
        n = 0
        for e in self.entries:
            try:
                n = max(n, int(str(e["id"]).lstrip("e")))
            except (ValueError, KeyError):
                continue
        return "e%04d" % (n + 1)

    def add(self, en, ve, pos="", category="general", context="", note="",
            alt=None, review=True):
        entry = {
            "id": self.next_id(),
            "en": en.strip(),
            "ve": ve.strip(),
            "pos": pos.strip(),
            "category": (category or "general").strip().lower(),
            "context": context.strip(),
            "note": note.strip(),
            "alt": alt or [],
            "review": bool(review),
        }
        self.entries.append(entry)
        self.by_id[entry["id"]] = entry
        self._index(self.en_index, entry["en"], entry)
        self._index(self.ve_index, entry["ve"], entry)
        for a in entry["alt"]:
            self._index(self.ve_index, a, entry)
        return entry

    def duplicate_of(self, en, ve):
        ken, kve = fold(en), fold(ve)
        for e in self.entries:
            if fold(e.get("en", "")) == ken and fold(e.get("ve", "")) == kve:
                return e
        return None

    def stats(self):
        return {
            "entries": len(self.entries),
            "english_keys": len(self.en_index),
            "tshivenda_keys": len(self.ve_index),
            "words": len(self.single_words()),
            "phrases": len(self.phrases()),
            "categories": len(self.categories()),
            "needs_review": sum(1 for e in self.entries if e.get("review")),
        }
