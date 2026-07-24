"""Tshivenda Bot. Run with: python bot.py"""

import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import ui, quiz, learn, news, history, content
from core.lexicon import Lexicon
from core.translate import translate, format_result, define
from core.text import fold, title

QUIT_WORDS = ("ndi zwone", "/quit", "/exit", "quit", "exit", "kha vha sale zwavhudi")


class Bot:
    def __init__(self):
        self.lex = Lexicon.load()
        self.progress = learn.Progress()
        self.riddles = content.Collection.load("riddles")
        self.proverbs = content.Collection.load("proverbs")
        self.jokes = content.Collection.load("jokes")
        self.culture = content.Collection.load("culture")
        self.running = True
        self.commands = self.build_commands()

    # ---------- command table ----------

    def build_commands(self):
        return {
            "help":      (self.cmd_help,     "this list"),
            "thusa":     (self.cmd_help,     "help, in Tshivenda"),
            "translate": (self.cmd_translate, "/translate <text>, works both ways"),
            "t":         (self.cmd_translate, "short for /translate"),
            "define":    (self.cmd_define,   "/define <word>, every meaning of a word"),
            "d":         (self.cmd_define,   "short for /define"),
            "search":    (self.cmd_search,   "/search <text>, find part of a word"),
            "word":      (self.cmd_word,     "word of the day"),
            "quiz":      (self.cmd_quiz,     "/quiz [rounds] [category]"),
            "learn":     (self.cmd_learn,    "/learn [count], spaced repetition drill"),
            "riddle":    (self.cmd_riddle,   "a Tshivenda riddle"),
            "thai":      (self.cmd_riddle,   "same as /riddle"),
            "proverb":   (self.cmd_proverb,  "a Tshivenda proverb"),
            "murero":    (self.cmd_proverb,  "same as /proverb"),
            "joke":      (self.cmd_joke,     "a joke"),
            "news":      (self.cmd_news,     "a news article from Limpopo"),
            "headlines": (self.cmd_headlines, "recent headlines only"),
            "about":     (self.cmd_about,    "/about <topic>, culture and history"),
            "history":   (self.cmd_history,  "the Venda territory in detail"),
            "geography": (self.cmd_geography, "land, capital and wildlife"),
            "add":       (self.cmd_add,      "/add [word|riddle|proverb|joke], teach the bot"),
            "review":    (self.cmd_review,   "/review [n], confirm or fix unverified entries"),
            "stats":     (self.cmd_stats,    "dictionary and progress numbers"),
            "categories": (self.cmd_categories, "list dictionary categories"),
        }

    # ---------- loop ----------

    def run(self):
        ui.banner(self.lex.stats())
        while self.running:
            try:
                raw = input(ui.c("You: ", "bold")).strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not raw:
                continue
            if fold(raw) in [fold(q) for q in QUIT_WORDS]:
                ui.bot("Kha vha sale zwavhudi. Goodbye.")
                break
            self.handle(raw)
        self.progress.save()

    def handle(self, raw):
        if raw.startswith("/"):
            parts = raw[1:].split(None, 1)
            name = parts[0].lower() if parts else ""
            arg = parts[1].strip() if len(parts) > 1 else ""
            fn = self.commands.get(name)
            if fn is None:
                near = [k for k in self.commands if k.startswith(name[:3])]
                ui.bot("No command called /%s." % name)
                if near:
                    ui.warn("Did you mean: " + ", ".join("/" + n for n in near[:5]))
                else:
                    ui.warn("Type /help to see everything.")
                return
            fn[0](arg)
        else:
            # anything that is not a command is treated as a translation
            self.cmd_translate(raw)

    # ---------- commands ----------

    def cmd_help(self, arg=""):
        ui.bot("Commands:")
        seen = set()
        for name, (fn, desc) in self.commands.items():
            if fn in seen:
                continue
            seen.add(fn)
            print("   /%-11s %s" % (name, desc))
        print()
        ui.warn("You can also just type any word or sentence with no slash.")
        ui.warn("Leave with: ndi zwone")

    def cmd_translate(self, arg):
        if not arg:
            ui.bot("Give me something to translate. Example: /translate welcome")
            return
        r = translate(self.lex, arg)
        if not r.ok:
            ui.bot("Thi khou zwi pfesesa. I do not have any of those words yet.")
            near = self.lex.near(arg, limit=4)
            if near:
                ui.warn("Closest entries: " + ", ".join(near))
            ui.warn("Teach me with: /add")
            return
        print()
        print(format_result(r))

    def cmd_define(self, arg):
        if not arg:
            ui.bot("Give me a word. Example: /define duvha")
            return
        print()
        print(define(self.lex, arg))

    def cmd_search(self, arg):
        if not arg:
            ui.bot("Give me something to search for.")
            return
        hits = self.lex.search(arg)
        if not hits:
            ui.bot("Nothing matched '%s'." % arg)
            return
        ui.bot("%d match%s for '%s':" % (len(hits), "" if len(hits) == 1 else "es", arg))
        for e in hits[:15]:
            print("   %-32s %s" % (e["en"], e["ve"]))
        if len(hits) > 15:
            ui.warn("...and %d more" % (len(hits) - 15))

    def cmd_word(self, arg=""):
        pool = self.lex.single_words() or self.lex.entries
        if not pool:
            ui.bot("The dictionary is empty.")
            return
        from datetime import date
        pick = pool[hash(date.today().isoformat()) % len(pool)]
        ui.bot("Ipfi la duvha, word of the day:")
        print("   %s  =  %s" % (title(pick["en"]), pick["ve"]))
        if pick.get("category"):
            print("   category: %s" % pick["category"])
        if pick.get("note"):
            print("   note: %s" % pick["note"])

    def cmd_quiz(self, arg):
        rounds = 5
        category = None
        for bit in arg.split():
            if bit.isdigit():
                rounds = max(1, min(50, int(bit)))
            else:
                category = bit.lower()
        if category and not self.lex.in_category(category):
            ui.warn("No category '%s'. Using all words." % category)
            category = None
        ui.bot("Quiz time. %d question(s)." % rounds)
        quiz.run(self.lex, rounds=rounds, category=category,
                 on_answer=lambda e, ok: self.progress.grade(e["id"], ok))
        self.progress.save()

    def cmd_learn(self, arg):
        size = 10
        if arg.strip().isdigit():
            size = max(1, min(50, int(arg.strip())))
        ui.bot("Drill mode. Words you get wrong come back sooner.")
        learn.session(self.lex, self.progress, size=size)

    def cmd_riddle(self, arg=""):
        print()
        content.show_riddle(self.riddles.pick())

    def cmd_proverb(self, arg=""):
        print()
        content.show_proverb(self.proverbs.pick())

    def cmd_joke(self, arg=""):
        print()
        content.show_joke(self.jokes.pick())

    def cmd_news(self, arg=""):
        ui.bot("Fetching, this can take a moment...")
        print(news.random_article())

    def cmd_headlines(self, arg=""):
        ui.bot("Fetching, this can take a moment...")
        print(news.headlines())

    def cmd_about(self, arg):
        item = content.find_topic(self.culture, arg)
        if item is None:
            ui.bot("No topic called '%s'. Try one of these:" % arg)
            for it in self.culture.items:
                print("   %s" % it["title"].lower())
            return
        print()
        content.show_culture(item)

    def cmd_history(self, arg=""):
        print()
        print(history.venda_history())

    def cmd_geography(self, arg=""):
        print()
        print(history.geography())


    def cmd_review(self, arg):
        """Walk unverified entries so a speaker can confirm or correct them.
        This is how the dictionary becomes trustworthy."""
        limit = 10
        if arg.strip().isdigit():
            limit = max(1, min(100, int(arg.strip())))
        pending = [e for e in self.lex.entries if e.get("review")]
        if not pending:
            ui.bot("Everything has been verified already.")
            return
        ui.bot("%d entries still need checking. Going through %d now."
               % (len(pending), min(limit, len(pending))))
        ui.warn("y = correct, n = delete, e = edit the Tshivenda, s = skip, stop = end")
        changed = 0
        for e in pending[:limit]:
            print()
            print("   %s  =  %s   [%s]" % (e["en"], e["ve"], e.get("category", "")))
            if e.get("note"):
                print("   note: %s" % e["note"])
            try:
                ans = input("   Correct? ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if ans in ("stop", "quit"):
                break
            if ans in ("y", "yes", "ee"):
                e["review"] = False
                changed += 1
            elif ans in ("n", "no", "hai"):
                self.lex.entries.remove(e)
                changed += 1
                ui.warn("   removed")
            elif ans in ("e", "edit"):
                new = input("   Correct Tshivenda: ").strip()
                if new:
                    e["ve"] = new
                    e["review"] = False
                    changed += 1
        if changed:
            self.lex.build()
            self.lex.save()
            left = sum(1 for x in self.lex.entries if x.get("review"))
            ui.bot("Saved. %d entries still waiting on review." % left)

    def cmd_stats(self, arg=""):
        s = self.lex.stats()
        p = self.progress.summary()
        ui.bot("Dictionary:")
        print("   entries %d, words %d, phrases %d" % (s["entries"], s["words"], s["phrases"]))
        print("   english keys %d, tshivenda keys %d" % (s["english_keys"], s["tshivenda_keys"]))
        print("   categories %d, awaiting speaker review %d" % (s["categories"], s["needs_review"]))
        ui.bot("Your progress:")
        print("   studied %d, due today %d, mastered %d" % (p["words_studied"], p["due_today"], p["mastered"]))
        print("   answers %d, accuracy %d%%, sessions %d" % (p["answers"], p["accuracy"], p["sessions"]))

    def cmd_categories(self, arg=""):
        ui.bot("Categories:")
        for cat, n in self.lex.categories().items():
            print("   %-12s %d" % (cat, n))
        ui.warn("Use them like: /quiz 10 body")

    def cmd_add(self, arg):
        kind = (arg or "word").strip().lower()
        try:
            if kind in ("word", "", "entry"):
                self._add_word()
            elif kind in ("riddle", "thai"):
                self._add_item(self.riddles, [("ve", "Riddle in Tshivenda"),
                                              ("en", "English version (optional)"),
                                              ("answer_ve", "Answer in Tshivenda"),
                                              ("answer_en", "Answer in English (optional)")])
            elif kind in ("proverb", "murero"):
                self._add_item(self.proverbs, [("ve", "Proverb in Tshivenda"),
                                               ("en", "Literal English"),
                                               ("meaning", "What it means")])
            elif kind == "joke":
                self._add_item(self.jokes, [("ve", "Joke in Tshivenda"),
                                            ("en", "English version (optional)")])
            else:
                ui.bot("I can add: word, riddle, proverb, joke.")
        except (EOFError, KeyboardInterrupt):
            print()
            ui.warn("Cancelled, nothing saved.")

    def _add_word(self):
        ui.bot("Adding a dictionary entry. Leave blank to cancel.")
        en = input("   English: ").strip()
        if not en:
            ui.warn("Cancelled.")
            return
        ve = input("   Tshivenda: ").strip()
        if not ve:
            ui.warn("Cancelled.")
            return
        dup = self.lex.duplicate_of(en, ve)
        if dup:
            ui.warn("Already in the dictionary as %s." % dup["id"])
            return
        cat = input("   Category (enter for general): ").strip() or "general"
        pos = input("   Part of speech (optional): ").strip()
        note = input("   Note, for example another meaning (optional): ").strip()
        e = self.lex.add(en=en, ve=ve, pos=pos, category=cat, note=note)
        self.lex.save()
        ui.bot("Saved as %s. Dictionary is now %d entries." % (e["id"], len(self.lex.entries)))
        others = [x for x in self.lex.senses_of(ve) if x["id"] != e["id"]]
        if others:
            ui.warn("Note: '%s' already means %s as well." % (ve, ", ".join(o["en"] for o in others)))

    def _add_item(self, coll, fields):
        ui.bot("Adding to %s. Leave the first field blank to cancel." % coll.name)
        item = {}
        for key, label in fields:
            val = input("   %s: " % label).strip()
            if not val and key == fields[0][0]:
                ui.warn("Cancelled.")
                return
            if val:
                item[key] = val
        coll.add(item)
        coll.save()
        ui.bot("Saved. %s now has %d items." % (coll.name, len(coll.items)))


HELP = """Tshivenda Bot

  python bot.py                  terminal
  python bot.py --web            web page in your browser
  python bot.py --web --open     web page, opens the browser for you
  python bot.py --web --port 8080
  python bot.py --gui            desktop window
  python bot.py /define duvha    run one command and exit
"""


def main():
    args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        print(HELP)
        return

    if "--web" in args:
        port = 8000
        if "--port" in args:
            try:
                port = int(args[args.index("--port") + 1])
            except (IndexError, ValueError):
                print("--port needs a number, for example --port 8080")
                return
        from web.server import serve
        serve(port=port, open_browser="--open" in args)
        return

    if "--gui" in args:
        try:
            from gui import launch
        except ImportError:
            print("The desktop window needs tkinter.")
            print("On Ubuntu or Debian: sudo apt install python3-tk")
            print("Otherwise use: python bot.py --web")
            return
        launch()
        return

    bot = Bot()
    if args:
        # one shot mode, useful for scripts and testing
        bot.handle(" ".join(args))
        return
    bot.run()


if __name__ == "__main__":
    main()
