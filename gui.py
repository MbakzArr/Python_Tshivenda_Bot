"""Desktop window. Standard library only.

    python bot.py --gui

Works with no browser and no internet. Same engine as the terminal and
the web page, so anything added here shows up everywhere.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.api import Service

PAPER = "#E4E6DA"
PAPER2 = "#EDEEE4"
INK = "#16241D"
SOFT = "#4A5B50"
LAKE = "#1E5C4C"
OCHRE = "#B57324"
OXIDE = "#8C3E2B"
LINE = "#C3C8B7"

BODY = ("Georgia", 12)
BIG = ("Georgia", 20)
SMALL = ("Segoe UI", 9)
LABEL = ("Segoe UI", 10, "bold")


class App:
    def __init__(self, root):
        self.svc = Service()
        self.root = root
        self.token = None
        self.drill = []

        root.title("Tshivenda Bot")
        root.configure(bg=PAPER)
        root.geometry("760x620")
        root.minsize(560, 480)

        self.style()
        self.header()
        self.tabs()
        self.status()
        self.refresh_counts()

    # ---------- chrome ----------

    def style(self):
        s = ttk.Style()
        try:
            s.theme_use("clam")
        except tk.TclError:
            pass
        s.configure("TNotebook", background=PAPER, borderwidth=0)
        s.configure("TNotebook.Tab", background=PAPER, foreground=SOFT,
                    padding=(16, 8), font=LABEL, borderwidth=0)
        s.map("TNotebook.Tab", background=[("selected", PAPER2)],
              foreground=[("selected", INK)])
        s.configure("TFrame", background=PAPER)
        s.configure("TLabel", background=PAPER, foreground=INK, font=BODY)

    def header(self):
        bar = tk.Frame(self.root, bg=PAPER)
        bar.pack(fill="x", padx=18, pady=(16, 0))
        tk.Label(bar, text="Tshivenda Bot", bg=PAPER, fg=INK,
                 font=("Segoe UI", 20, "bold")).pack(side="left")
        self.counts = tk.Label(bar, text="", bg=PAPER, fg=SOFT, font=SMALL)
        self.counts.pack(side="right", pady=(10, 0))
        # the mark under the wordmark, same idea as the web page
        tk.Frame(self.root, bg=LAKE, height=4, width=120).pack(anchor="w", padx=18, pady=(2, 0))

    def tabs(self):
        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=14, pady=14)
        for build, name in ((self.tab_translate, "Translate"),
                            (self.tab_lookup, "Look up"),
                            (self.tab_practise, "Practise"),
                            (self.tab_add, "Add a word")):
            f = ttk.Frame(nb)
            nb.add(f, text=name)
            build(f)

    def status(self):
        self.msg = tk.Label(self.root, text="", bg=PAPER, fg=SOFT,
                            font=SMALL, anchor="w")
        self.msg.pack(fill="x", padx=18, pady=(0, 10))

    def refresh_counts(self):
        s = self.svc.stats()
        self.counts.config(text="%d entries, %d verified, %d answered"
                                % (s["entries"], s["verified"], s["answers"]))

    def say(self, text, bad=False):
        self.msg.config(text=text, fg=OXIDE if bad else SOFT)

    @staticmethod
    def output(parent):
        box = tk.Text(parent, wrap="word", bg=PAPER2, fg=INK, font=BODY,
                      relief="flat", padx=14, pady=12, height=14,
                      highlightthickness=1, highlightbackground=LINE)
        box.tag_configure("big", font=BIG, foreground=INK, spacing3=8)
        box.tag_configure("dim", foreground=SOFT, font=SMALL)
        box.tag_configure("hit", foreground=LAKE, font=("Georgia", 12, "bold"))
        box.tag_configure("gap", foreground=OCHRE, font=("Georgia", 12, "italic"))
        box.tag_configure("warn", foreground=OCHRE, font=SMALL)
        box.configure(state="disabled")
        return box

    def write(self, box, chunks):
        box.configure(state="normal")
        box.delete("1.0", "end")
        for text, tag in chunks:
            box.insert("end", text, tag or "")
        box.configure(state="disabled")

    # ---------- translate ----------

    def tab_translate(self, f):
        tk.Label(f, text="Type in either language", bg=PAPER, fg=INK,
                 font=LABEL).pack(anchor="w", pady=(6, 4))
        self.t_in = tk.Text(f, height=3, wrap="word", bg=PAPER2, fg=INK,
                            font=BODY, relief="flat", padx=12, pady=10,
                            highlightthickness=1, highlightbackground=LINE,
                            highlightcolor=LAKE)
        self.t_in.pack(fill="x")
        self.t_in.bind("<Return>", lambda e: (self.do_translate(), "break")[1])

        row = tk.Frame(f, bg=PAPER)
        row.pack(fill="x", pady=10)
        tk.Button(row, text="Translate", command=self.do_translate, bg=LAKE,
                  fg=PAPER2, relief="flat", font=LABEL, padx=18, pady=6,
                  activebackground="#164A3D", activeforeground=PAPER2,
                  cursor="hand2").pack(side="left")
        tk.Label(row, text="Enter to translate", bg=PAPER, fg=SOFT,
                 font=SMALL).pack(side="left", padx=12)

        self.t_out = self.output(f)
        self.t_out.pack(fill="both", expand=True)

    def do_translate(self):
        text = self.t_in.get("1.0", "end").strip()
        if not text:
            return
        d = self.svc.translate(text)
        if not d["ok"]:
            self.write(self.t_out, [("None of those words are in the dictionary yet.\n", "dim")])
            if d["suggestions"]:
                self.write(self.t_out, [("None of those words are in the dictionary yet.\n\n", "dim"),
                                        ("Closest entries: " + ", ".join(d["suggestions"]), "warn")])
            self.say("Nothing matched. Add the words under Add a word.", bad=True)
            return

        arrow = "English to Tshivenda" if d["direction"] == "en-ve" else "Tshivenda to English"
        chunks = [(arrow.upper() + "\n", "dim"), (d["text"] + "\n\n", "big")]
        matched = sum(1 for p in d["parts"] if p["matched"])
        chunks.append(("%d of %d matched, %d%% confidence\n\n"
                       % (matched, len(d["parts"]), round(d["confidence"] * 100)), "dim"))
        if len(d["parts"]) > 1:
            for p in d["parts"]:
                chunks.append(("  %-16s " % p["source"], "dim"))
                if p["matched"]:
                    chunks.append((p["target"] + "\n", "hit"))
                else:
                    chunks.append(("not known\n", "gap"))
            chunks.append(("\n", None))
        for n in d["notes"]:
            chunks.append(("  note: " + n + "\n", "dim"))
        if d["senses"]:
            other = ", ".join((x["ve"] if d["direction"] == "en-ve" else x["en"])
                              for x in d["senses"])
            chunks.append(("  also means: " + other + "\n", "dim"))
        self.write(self.t_out, chunks)
        self.say("")

    # ---------- look up ----------

    def tab_lookup(self, f):
        tk.Label(f, text="Word", bg=PAPER, fg=INK, font=LABEL).pack(anchor="w", pady=(6, 4))
        self.l_in = tk.Entry(f, bg=PAPER2, fg=INK, font=BODY, relief="flat",
                             highlightthickness=1, highlightbackground=LINE,
                             highlightcolor=LAKE)
        self.l_in.pack(fill="x", ipady=8)
        self.l_in.bind("<Return>", lambda e: self.do_lookup())

        row = tk.Frame(f, bg=PAPER)
        row.pack(fill="x", pady=10)
        tk.Button(row, text="Look up", command=self.do_lookup, bg=LAKE, fg=PAPER2,
                  relief="flat", font=LABEL, padx=18, pady=6, cursor="hand2",
                  activebackground="#164A3D", activeforeground=PAPER2).pack(side="left")
        tk.Button(row, text="Word of the day", command=self.do_word, bg=PAPER,
                  fg=INK, relief="solid", bd=1, font=LABEL, padx=14, pady=5,
                  cursor="hand2").pack(side="left", padx=8)

        self.l_out = self.output(f)
        self.l_out.pack(fill="both", expand=True)

    def entry_chunks(self, e, n=None):
        head = ("%s. " % n if n else "") + e["en"]
        out = [(head + "\n", "hit"), (e["ve"] + "\n", "big")]
        if e["alt"]:
            out.append(("also: " + ", ".join(e["alt"]) + "\n", "dim"))
        if e["note"]:
            out.append((e["note"] + "\n", "dim"))
        tags = " . ".join(t for t in (e["pos"], e["category"], e["context"]) if t)
        if tags:
            out.append((tags + "\n", "dim"))
        if not e["verified"]:
            out.append(("not yet verified by a speaker\n", "warn"))
        out.append(("\n", None))
        return out

    def do_lookup(self):
        w = self.l_in.get().strip()
        if not w:
            return
        d = self.svc.define(w)
        if d["senses"]:
            chunks = [("%d meaning%s\n\n" % (len(d["senses"]),
                       "" if len(d["senses"]) == 1 else "s"), "dim")]
            for i, e in enumerate(d["senses"], 1):
                chunks += self.entry_chunks(e, i)
            self.write(self.l_out, chunks)
            self.say("")
            return
        hits = self.svc.search(w)
        if hits:
            chunks = [("No exact entry, %d partial matches\n\n" % len(hits), "dim")]
            for e in hits[:12]:
                chunks += self.entry_chunks(e)
            self.write(self.l_out, chunks)
            return
        chunks = [("Nothing yet for '%s'.\n" % w, "dim")]
        if d["near"]:
            chunks.append(("Closest: " + ", ".join(d["near"]), "warn"))
        self.write(self.l_out, chunks)

    def do_word(self):
        e = self.svc.word_of_day()
        if e:
            self.write(self.l_out, [("Ipfi la duvha, word of the day\n\n", "dim")]
                       + self.entry_chunks(e))

    # ---------- practise ----------

    def tab_practise(self, f):
        self.p_prompt = tk.Label(f, text="", bg=PAPER, fg=INK, font=("Georgia", 16),
                                 wraplength=620, justify="left", anchor="w")
        self.p_prompt.pack(fill="x", pady=(14, 14))
        self.p_opts = tk.Frame(f, bg=PAPER)
        self.p_opts.pack(fill="x")
        self.p_feedback = tk.Label(f, text="", bg=PAPER, fg=SOFT, font=BODY,
                                   wraplength=620, justify="left", anchor="w")
        self.p_feedback.pack(fill="x", pady=14)

        row = tk.Frame(f, bg=PAPER)
        row.pack(fill="x", pady=6)
        tk.Button(row, text="Next question", command=self.next_question, bg=LAKE,
                  fg=PAPER2, relief="flat", font=LABEL, padx=18, pady=6,
                  cursor="hand2", activebackground="#164A3D",
                  activeforeground=PAPER2).pack(side="left")
        tk.Button(row, text="Drill my weak words", command=self.start_drill,
                  bg=PAPER, fg=INK, relief="solid", bd=1, font=LABEL,
                  padx=14, pady=5, cursor="hand2").pack(side="left", padx=8)
        self.next_question()

    def next_question(self):
        for w in self.p_opts.winfo_children():
            w.destroy()
        self.p_feedback.config(text="")
        if self.drill:
            d = self.svc.question_for(self.drill.pop(0))
        else:
            d = self.svc.new_question()
        if not d["ok"]:
            self.p_prompt.config(text=d["error"])
            return
        self.token = d["token"]
        self.p_prompt.config(text=d["prompt"])
        for opt in d["options"]:
            b = tk.Button(self.p_opts, text=opt, anchor="w", bg=PAPER2, fg=INK,
                          font=BODY, relief="solid", bd=1, padx=14, pady=9,
                          cursor="hand2",
                          command=lambda o=opt: self.answer(o))
            b.pack(fill="x", pady=3)

    def answer(self, given):
        d = self.svc.answer(self.token, given)
        if not d["ok"]:
            self.say(d["error"], bad=True)
            return
        for b in self.p_opts.winfo_children():
            b.config(state="disabled")
            if b.cget("text") == d["answer"]:
                b.config(fg=LAKE, bd=2)
            elif b.cget("text") == given:
                b.config(fg=OXIDE)
        if d["correct"]:
            msg = "Ndi zwone. Correct. Coming back in %d day%s." % (
                d["next_review_days"], "" if d["next_review_days"] == 1 else "s")
        else:
            msg = "The answer is %s. This one comes back tomorrow." % d["answer"]
        if d["note"]:
            msg += "\n" + d["note"]
        self.p_feedback.config(text=msg, fg=LAKE if d["correct"] else OXIDE)
        self.refresh_counts()

    def start_drill(self):
        self.drill = [e["id"] for e in self.svc.drill_queue(10)]
        self.say("Drilling %d words you have missed or not seen." % len(self.drill))
        self.next_question()

    # ---------- add ----------

    def tab_add(self, f):
        tk.Label(f, text="Anything you save goes straight into the dictionary "
                         "and works in translation and quizzes right away.",
                 bg=PAPER, fg=SOFT, font=SMALL, wraplength=620,
                 justify="left").pack(anchor="w", pady=(10, 14))
        self.fields = {}
        for key, label in (("en", "English"), ("ve", "Tshivenda"),
                           ("category", "Category"), ("pos", "Part of speech"),
                           ("note", "Note, such as another meaning")):
            tk.Label(f, text=label, bg=PAPER, fg=INK, font=LABEL).pack(anchor="w", pady=(8, 3))
            ent = tk.Entry(f, bg=PAPER2, fg=INK, font=BODY, relief="flat",
                           highlightthickness=1, highlightbackground=LINE,
                           highlightcolor=LAKE)
            ent.pack(fill="x", ipady=6)
            self.fields[key] = ent
        tk.Button(f, text="Save word", command=self.do_add, bg=LAKE, fg=PAPER2,
                  relief="flat", font=LABEL, padx=18, pady=7, cursor="hand2",
                  activebackground="#164A3D", activeforeground=PAPER2
                  ).pack(anchor="w", pady=18)

    def do_add(self):
        vals = {k: v.get().strip() for k, v in self.fields.items()}
        d = self.svc.add_word(vals["en"], vals["ve"], vals["category"] or "general",
                              vals["pos"], vals["note"])
        if not d["ok"]:
            messagebox.showwarning("Not saved", d["error"])
            return
        for k in ("en", "ve", "pos", "note"):
            self.fields[k].delete(0, "end")
        self.refresh_counts()
        note = ""
        if d["other_senses"]:
            note = "  '%s' also means %s. Both are kept." % (
                d["entry"]["ve"], ", ".join(x["en"] for x in d["other_senses"]))
        self.say("Saved. The dictionary is now %d entries.%s" % (d["total"], note))


def launch():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    launch()
