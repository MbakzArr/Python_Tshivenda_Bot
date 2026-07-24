"""One place every interface talks to.

The terminal bot, the web page and the desktop window all call these
functions and get plain dictionaries back. No interface knows how the
translation engine works and the engine knows nothing about interfaces.
"""

import random
from datetime import date

from core import content, learn, news, quiz
from core.lexicon import Lexicon
from core.translate import translate as run_translate
from core.text import title


class Service:
    def __init__(self):
        self.lex = Lexicon.load()
        self.progress = learn.Progress()
        self.riddles = content.Collection.load("riddles")
        self.proverbs = content.Collection.load("proverbs")
        self.jokes = content.Collection.load("jokes")
        self.culture = content.Collection.load("culture")
        self._quizzes = {}

    # ---------- shared shapes ----------

    @staticmethod
    def entry_dict(e):
        if not e:
            return None
        return {
            "id": e.get("id"),
            "en": e.get("en", ""),
            "ve": e.get("ve", ""),
            "pos": e.get("pos", ""),
            "category": e.get("category", ""),
            "context": e.get("context", ""),
            "note": e.get("note", ""),
            "alt": e.get("alt", []),
            "verified": not e.get("review", True),
        }

    # ---------- dictionary ----------

    def stats(self):
        s = self.lex.stats()
        s.update(self.progress.summary())
        s["verified"] = s["entries"] - s["needs_review"]
        return s

    def categories(self):
        return [{"name": k, "count": v} for k, v in self.lex.categories().items()]

    def translate(self, text, direction=None):
        r = run_translate(self.lex, text, direction)
        parts = []
        for p in r.parts:
            e = p.get("entry")
            parts.append({
                "source": p["source"],
                "target": p["target"],
                "matched": p["matched"],
                "note": (e or {}).get("note", ""),
                "id": (e or {}).get("id"),
            })
        return {
            "input": text,
            "direction": r.direction,
            "text": title(r.text) if r.text else "",
            "confidence": r.confidence,
            "parts": parts,
            "unknown": r.unknown,
            "suggestions": r.suggestions[:5],
            "notes": r.notes[:3],
            "senses": [self.entry_dict(e) for e in r.senses[:4]],
            "ok": r.ok,
        }

    def define(self, word):
        hits = self.lex.senses_of(word)
        return {
            "word": word,
            "senses": [self.entry_dict(e) for e in hits],
            "near": [] if hits else self.lex.near(word, limit=5),
        }

    def search(self, term, limit=40):
        return [self.entry_dict(e) for e in self.lex.search(term, limit=limit)]

    def word_of_day(self):
        pool = self.lex.single_words() or self.lex.entries
        if not pool:
            return None
        pick = pool[hash(date.today().isoformat()) % len(pool)]
        return self.entry_dict(pick)

    def add_word(self, en, ve, category="general", pos="", note=""):
        en, ve = (en or "").strip(), (ve or "").strip()
        if not en or not ve:
            return {"ok": False, "error": "Both the English and the Tshivenda are needed."}
        dup = self.lex.duplicate_of(en, ve)
        if dup:
            return {"ok": False, "error": "Already saved as %s." % dup["id"],
                    "entry": self.entry_dict(dup)}
        e = self.lex.add(en=en, ve=ve, pos=pos, category=category, note=note)
        self.lex.save()
        others = [self.entry_dict(x) for x in self.lex.senses_of(ve) if x["id"] != e["id"]]
        return {"ok": True, "entry": self.entry_dict(e),
                "total": len(self.lex.entries), "other_senses": others}

    # ---------- verification ----------

    def pending(self, limit=25):
        out = [e for e in self.lex.entries if e.get("review")]
        return {"total": len(out), "items": [self.entry_dict(e) for e in out[:limit]]}

    def review(self, entry_id, action, corrected=""):
        e = self.lex.by_id.get(entry_id)
        if not e:
            return {"ok": False, "error": "No entry with that id."}
        if action == "confirm":
            e["review"] = False
        elif action == "delete":
            self.lex.entries.remove(e)
        elif action == "edit":
            if not corrected.strip():
                return {"ok": False, "error": "Give the corrected spelling."}
            e["ve"] = corrected.strip()
            e["review"] = False
        else:
            return {"ok": False, "error": "Unknown action."}
        self.lex.build()
        self.lex.save()
        left = sum(1 for x in self.lex.entries if x.get("review"))
        return {"ok": True, "remaining": left}

    # ---------- practice ----------

    def new_question(self, category=None, token=None):
        q = quiz.make(self.lex, category=category or None)
        if q is None:
            return {"ok": False, "error": "Not enough words to build a question yet."}
        token = token or "q%d" % random.randint(100000, 999999)
        self._quizzes[token] = q
        if len(self._quizzes) > 500:
            self._quizzes.pop(next(iter(self._quizzes)))
        return {
            "ok": True,
            "token": token,
            "prompt": q.prompt,
            "options": q.options,
            "direction": q.direction,
            "entry_id": q.entry["id"],
        }

    def answer(self, token, given):
        q = self._quizzes.get(token)
        if q is None:
            return {"ok": False, "error": "That question has expired. Ask for a new one."}
        correct = q.check(given)
        self.progress.grade(q.entry["id"], correct)
        self.progress.save()
        card = self.progress.card(q.entry["id"])
        return {
            "ok": True,
            "correct": correct,
            "answer": q.answer,
            "note": q.entry.get("note", ""),
            "next_review_days": card["interval"],
            "entry": self.entry_dict(q.entry),
        }

    def drill_queue(self, size=10):
        ids = learn.build_queue(self.lex, self.progress, size)
        return [self.entry_dict(self.lex.by_id[i]) for i in ids if i in self.lex.by_id]

    def question_for(self, entry_id, token=None):
        e = self.lex.by_id.get(entry_id)
        if not e:
            return {"ok": False, "error": "No entry with that id."}
        q = quiz.make(self.lex, entry=e)
        if q is None:
            return {"ok": False, "error": "Could not build a question for that word."}
        token = token or "d%d" % random.randint(100000, 999999)
        self._quizzes[token] = q
        return {"ok": True, "token": token, "prompt": q.prompt,
                "options": q.options, "entry_id": e["id"]}

    # ---------- content ----------

    def riddle(self):
        return self.riddles.pick()

    def proverb(self):
        return self.proverbs.pick()

    def joke(self):
        return self.jokes.pick()

    def culture_topics(self):
        return [{"id": i.get("id"), "title": i.get("title", ""),
                 "tags": i.get("tags", [])} for i in self.culture.items]

    def culture(self, topic=None):
        return content.find_topic(self.culture, topic)

    def add_content(self, kind, item):
        coll = {"riddle": self.riddles, "proverb": self.proverbs,
                "joke": self.jokes}.get(kind)
        if coll is None:
            return {"ok": False, "error": "Can only add a riddle, proverb or joke."}
        if not (item.get("ve") or "").strip():
            return {"ok": False, "error": "The Tshivenda text is needed."}
        saved = coll.add({k: v for k, v in item.items() if v})
        coll.save()
        return {"ok": True, "item": saved, "total": len(coll.items)}

    def news(self, limit=6):
        articles, cached = news.fetch()
        return {"cached": cached, "articles": articles[:limit]}
