import random

from core.text import fold

# Questions are generated from the lexicon, so the quiz grows on its own
# every time a word is added. No hand written question bank to maintain.


class Question:
    def __init__(self, entry, prompt, answer, options, direction):
        self.entry = entry
        self.prompt = prompt
        self.answer = answer
        self.options = options
        self.direction = direction

    def check(self, given):
        given = fold(given)
        if not given:
            return False
        # accept the letter, the number or the word itself
        if len(given) == 1 and given.isalpha():
            idx = ord(given) - ord("a")
            if 0 <= idx < len(self.options):
                return fold(self.options[idx]) == fold(self.answer)
        if given.isdigit():
            idx = int(given) - 1
            if 0 <= idx < len(self.options):
                return fold(self.options[idx]) == fold(self.answer)
        return given == fold(self.answer)

    def render(self, n=None):
        head = "Q%s: %s" % (n if n else "", self.prompt)
        lines = [head]
        for i, o in enumerate(self.options):
            lines.append("   %s) %s" % (chr(ord("a") + i), o))
        return "\n".join(lines)


def distractors(lex, entry, field, count=3):
    """Wrong answers from the same category first so the quiz is not trivial."""
    cat = entry.get("category") or "general"
    pool = [e for e in lex.in_category(cat)
            if e["id"] != entry["id"] and e.get(field)]
    if len(pool) < count:
        extra = [e for e in lex.single_words()
                 if e["id"] != entry["id"] and e.get(field)]
        pool = pool + extra
    seen = {fold(entry.get(field, ""))}
    out = []
    random.shuffle(pool)
    for e in pool:
        v = e.get(field, "")
        if fold(v) not in seen:
            seen.add(fold(v))
            out.append(v)
        if len(out) == count:
            break
    return out


def make(lex, entry=None, direction=None, category=None):
    pool = lex.in_category(category) if category else lex.single_words()
    pool = [e for e in pool if e.get("en") and e.get("ve")]
    if not pool:
        pool = [e for e in lex.entries if e.get("en") and e.get("ve")]
    if not pool:
        return None
    entry = entry or random.choice(pool)
    direction = direction or random.choice(["en-ve", "ve-en"])

    if direction == "en-ve":
        prompt = "What is '%s' in Tshivenda?" % entry["en"]
        answer = entry["ve"]
        field = "ve"
    else:
        prompt = "What does '%s' mean in English?" % entry["ve"]
        answer = entry["en"]
        field = "en"

    opts = distractors(lex, entry, field, 3) + [answer]
    if len(opts) < 2:
        return None
    random.shuffle(opts)
    return Question(entry, prompt, answer, opts, direction)


def run(lex, rounds=5, category=None, ask=input, say=print, on_answer=None):
    """Play a quiz round. on_answer(entry, correct) lets learn mode hook in."""
    score = 0
    asked = 0
    streak = 0
    best_streak = 0

    for i in range(1, rounds + 1):
        q = make(lex, category=category)
        if q is None:
            say("Not enough words in the dictionary to build a quiz yet.")
            return 0, 0
        asked += 1
        say("")
        say(q.render(i))
        try:
            given = ask("Your answer (a-d, or 'stop'): ").strip()
        except (EOFError, KeyboardInterrupt):
            say("")
            break
        if fold(given) in ("stop", "quit", "ndi zwone"):
            break
        correct = q.check(given)
        if correct:
            score += 1
            streak += 1
            best_streak = max(best_streak, streak)
            say("Ndi zwone! Correct.")
        else:
            streak = 0
            say("Hai. The answer is: %s" % q.answer)
            if q.entry.get("note"):
                say("   note: %s" % q.entry["note"])
        if on_answer:
            on_answer(q.entry, correct)

    if asked:
        pct = int(score * 100 / asked)
        say("")
        say("Score: %d out of %d (%d%%). Best streak: %d" % (score, asked, pct, best_streak))
        say(grade(pct))
    return score, asked


def grade(pct):
    if pct == 100:
        return "Perfect. Ni na vhutali."
    if pct >= 80:
        return "Strong round."
    if pct >= 50:
        return "Getting there. Try /learn to drill the ones you missed."
    return "Keep practising. /learn will focus on your weak words."
