import json
import os
import random
from datetime import date

from core import paths

# Riddles (thai), proverbs (mirero), jokes and culture notes all share the
# same shape, so one loader handles all of them. Every item carries a
# review flag. Anything not yet checked by a speaker is shown with a mark
# so nobody learns a wrong phrase from this bot.


class Collection:
    def __init__(self, name, items=None):
        self.name = name
        self.items = items or []

    @classmethod
    def load(cls, name):
        path = paths.data(name + ".json")
        if not os.path.exists(path):
            return cls(name, [])
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except (ValueError, OSError):
            return cls(name, [])
        return cls(name, raw.get("items", []))

    def save(self):
        path = paths.data(self.name + ".json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"name": self.name, "count": len(self.items),
                       "items": self.items}, f, ensure_ascii=False, indent=2)

    def add(self, item):
        item.setdefault("id", "%s%03d" % (self.name[:3], len(self.items) + 1))
        item.setdefault("review", True)
        self.items.append(item)
        return item

    def pick(self, seed=None):
        if not self.items:
            return None
        rng = random.Random(seed) if seed is not None else random
        return rng.choice(self.items)

    def daily(self):
        """Same item all day, changes at midnight."""
        if not self.items:
            return None
        return self.items[hash(date.today().isoformat()) % len(self.items)]


def mark(item):
    return "  (not yet verified by a speaker)" if item.get("review") else ""


def show_riddle(item, ask=input, say=print):
    if not item:
        say("No riddles loaded yet. Add one with /add riddle.")
        return
    say("Thai (riddle):" + mark(item))
    say("  %s" % item.get("ve", ""))
    if item.get("en"):
        say("  [%s]" % item["en"])
    try:
        ask("  Press enter for the answer... ")
    except (EOFError, KeyboardInterrupt):
        say("")
        return
    say("  Answer: %s" % item.get("answer_ve", item.get("answer", "")))
    if item.get("answer_en"):
        say("  [%s]" % item["answer_en"])


def show_proverb(item, say=print):
    if not item:
        say("No proverbs loaded yet. Add one with /add proverb.")
        return
    say("Murero (proverb):" + mark(item))
    say("  %s" % item.get("ve", ""))
    if item.get("en"):
        say("  [%s]" % item["en"])
    if item.get("meaning"):
        say("  meaning: %s" % item["meaning"])


def show_joke(item, say=print):
    if not item:
        say("No jokes loaded yet. Add one with /add joke.")
        return
    say("Tshiseo (joke):" + mark(item))
    say("  %s" % item.get("ve", item.get("en", "")))
    if item.get("ve") and item.get("en"):
        say("  [%s]" % item["en"])


def show_culture(item, say=print):
    if not item:
        say("Nothing on that topic yet.")
        return
    say("%s" % item.get("title", ""))
    say("  %s" % item.get("text", ""))
    if item.get("source"):
        say("  source: %s" % item["source"])


def find_topic(coll, term):
    term = (term or "").lower().strip()
    if not term:
        return coll.pick()
    for it in coll.items:
        if term in it.get("title", "").lower() or term in " ".join(it.get("tags", [])).lower():
            return it
    return None
