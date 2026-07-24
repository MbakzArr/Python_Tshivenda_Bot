import json
import os
import random
from datetime import date, timedelta

from core import paths
from core import quiz

PROGRESS_FILE = paths.user("progress.json")

# Spaced repetition, cut down version of SM-2. Words you get wrong come
# back tomorrow, words you know keep moving further into the future.
# This is what turns the bot from a lookup tool into a teacher.


def _today():
    return date.today().isoformat()


def _plus(days):
    return (date.today() + timedelta(days=days)).isoformat()


class Progress:
    def __init__(self, path=None):
        self.path = path or PROGRESS_FILE
        self.cards = {}
        self.log = {"sessions": 0, "answers": 0, "correct": 0, "last": ""}
        self.load()

    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                self.cards = raw.get("cards", {})
                self.log.update(raw.get("log", {}))
            except (ValueError, OSError):
                self.cards = {}

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({"cards": self.cards, "log": self.log}, f,
                      ensure_ascii=False, indent=2)

    def card(self, entry_id):
        return self.cards.setdefault(entry_id, {
            "reps": 0, "ease": 2.5, "interval": 0, "due": _today(),
            "seen": 0, "wrong": 0,
        })

    def grade(self, entry_id, correct):
        c = self.card(entry_id)
        c["seen"] += 1
        q = 4 if correct else 2
        if correct:
            if c["reps"] == 0:
                c["interval"] = 1
            elif c["reps"] == 1:
                c["interval"] = 3
            else:
                c["interval"] = max(1, int(round(c["interval"] * c["ease"])))
            c["reps"] += 1
        else:
            c["wrong"] += 1
            c["reps"] = 0
            c["interval"] = 1
        c["ease"] = max(1.3, c["ease"] + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)))
        c["ease"] = round(c["ease"], 2)
        c["due"] = _plus(c["interval"])
        self.log["answers"] += 1
        if correct:
            self.log["correct"] += 1
        self.log["last"] = _today()

    def due_ids(self):
        t = _today()
        return [k for k, v in self.cards.items() if v.get("due", t) <= t]

    def weak_ids(self, limit=15):
        ranked = sorted(self.cards.items(),
                        key=lambda kv: (-kv[1].get("wrong", 0), kv[1].get("ease", 2.5)))
        return [k for k, v in ranked if v.get("wrong", 0) > 0][:limit]

    def summary(self):
        seen = len(self.cards)
        acc = 0
        if self.log["answers"]:
            acc = int(self.log["correct"] * 100 / self.log["answers"])
        return {
            "words_studied": seen,
            "due_today": len(self.due_ids()),
            "answers": self.log["answers"],
            "accuracy": acc,
            "sessions": self.log["sessions"],
            "mastered": sum(1 for c in self.cards.values() if c.get("interval", 0) >= 21),
        }


def build_queue(lex, prog, size=10):
    """Due cards first, then weak ones, then words never seen before."""
    order = []
    for cid in prog.due_ids():
        if cid in lex.by_id and cid not in order:
            order.append(cid)
    for cid in prog.weak_ids():
        if cid in lex.by_id and cid not in order:
            order.append(cid)
    if len(order) < size:
        fresh = [e["id"] for e in lex.single_words() if e["id"] not in prog.cards]
        random.shuffle(fresh)
        order += fresh[:size - len(order)]
    if len(order) < size:
        rest = [e["id"] for e in lex.single_words() if e["id"] not in order]
        random.shuffle(rest)
        order += rest[:size - len(order)]
    return order[:size]


def session(lex, prog, size=10, ask=input, say=print):
    queue = build_queue(lex, prog, size)
    if not queue:
        say("No words available yet. Add some with /add.")
        return

    prog.log["sessions"] += 1
    say("Drill of %d words. Type 'stop' to end early." % len(queue))
    right = 0
    done = 0

    for n, cid in enumerate(queue, 1):
        entry = lex.by_id.get(cid)
        if not entry:
            continue
        q = quiz.make(lex, entry=entry)
        if q is None:
            continue
        done += 1
        say("")
        say(q.render(n))
        try:
            given = ask("Your answer: ").strip()
        except (EOFError, KeyboardInterrupt):
            say("")
            break
        if given.lower() in ("stop", "quit", "ndi zwone"):
            break
        ok = q.check(given)
        prog.grade(cid, ok)
        if ok:
            right += 1
            card = prog.card(cid)
            say("Correct. Next review in %d day(s)." % card["interval"])
        else:
            say("The answer is: %s. This one comes back tomorrow." % q.answer)

    prog.save()
    if done:
        say("")
        say("Drill done: %d of %d correct." % (right, done))
        s = prog.summary()
        say("Studied %d words overall, %d mastered, %d%% lifetime accuracy."
            % (s["words_studied"], s["mastered"], s["accuracy"]))
