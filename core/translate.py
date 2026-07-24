from core.text import fold, words, ve_score, title

MAX_PHRASE = 6  # longest window we try when matching a phrase


class Result:
    def __init__(self):
        self.direction = "en-ve"
        self.text = ""
        self.parts = []      # list of dicts: source, target, entry, matched
        self.confidence = 0.0
        self.senses = []     # other meanings worth showing
        self.suggestions = []
        self.notes = []

    @property
    def ok(self):
        return self.confidence > 0

    @property
    def unknown(self):
        return [p["source"] for p in self.parts if not p["matched"]]



def variants(word, direction):
    """Other shapes of a word to try when the plain form is not indexed.
    English verbs are stored as 'to go' and Tshivenda verbs as 'u ya',
    so we build the likely stems and try both wrappers."""
    w = fold(word)
    if not w:
        return []
    stems = [w]

    if direction == "en-ve":
        if w.endswith("ies") and len(w) > 4:
            stems.append(w[:-3] + "y")
        if w.endswith("es") and len(w) > 3:
            stems.append(w[:-2])
        if w.endswith("s") and not w.endswith("ss") and len(w) > 2:
            stems.append(w[:-1])
        if w.endswith("ing") and len(w) > 4:
            base = w[:-3]
            stems += [base, base + "e"]
            if len(base) > 2 and base[-1] == base[-2]:
                stems.append(base[:-1])
        if w.endswith("ed") and len(w) > 3:
            base = w[:-2]
            stems += [base, base + "e", w[:-1]]
            if len(base) > 2 and base[-1] == base[-2]:
                stems.append(base[:-1])
        wrapper = "to "
    else:
        for pre in ("khou ", "ndi khou ", "do ", "u ", "a "):
            if w.startswith(pre) and len(w) > len(pre):
                stems.append(w[len(pre):])
        wrapper = "u "

    out = []
    for st in stems:
        for form in (st, wrapper + st):
            form = form.strip()
            if form and form not in out:
                out.append(form)
    return out


def detect(lex, phrase):
    """Decide which way to translate. Lexicon evidence beats the letter heuristic."""
    toks = words(phrase)
    if not toks:
        return "en-ve"
    en_hits = sum(1 for t in toks if fold(t) in lex.en_index)
    ve_hits = sum(1 for t in toks if fold(t) in lex.ve_index)
    if fold(phrase) in lex.en_index and fold(phrase) not in lex.ve_index:
        return "en-ve"
    if fold(phrase) in lex.ve_index and fold(phrase) not in lex.en_index:
        return "ve-en"
    if en_hits != ve_hits:
        return "en-ve" if en_hits > ve_hits else "ve-en"
    return "ve-en" if ve_score(phrase) > 0.45 else "en-ve"


def _side(lex, direction):
    if direction == "en-ve":
        return lex.en_index, "ve", "en"
    return lex.ve_index, "en", "ve"


def _out(entry, want):
    if want == "ve":
        return entry.get("ve", "")
    return entry.get("en", "")


def translate(lex, phrase, direction=None):
    r = Result()
    phrase = (phrase or "").strip()
    if not phrase:
        return r

    r.direction = direction or detect(lex, phrase)
    index, want, src_field = _side(lex, r.direction)

    # 1. whole phrase exact hit
    whole = index.get(fold(phrase))
    if not whole:
        for alt in variants(phrase, r.direction)[1:]:
            whole = index.get(alt)
            if whole:
                break
    if whole:
        best = whole[0]
        r.text = _out(best, want)
        r.parts = [{"source": phrase, "target": r.text, "entry": best, "matched": True}]
        r.confidence = 1.0
        r.senses = whole[1:]
        _collect_notes(r, whole)
        return r

    # 2. greedy longest phrase segmentation
    toks = phrase.split()
    i = 0
    matched_tokens = 0
    pieces = []
    while i < len(toks):
        hit = None
        span = 0
        for size in range(min(MAX_PHRASE, len(toks) - i), 0, -1):
            window = " ".join(toks[i:i + size])
            found = index.get(fold(window))
            if not found and size == 1:
                for alt in variants(window, r.direction)[1:]:
                    found = index.get(alt)
                    if found:
                        break
            if found:
                hit = found
                span = size
                break
        if hit:
            best = hit[0]
            out = _out(best, want)
            pieces.append(out)
            r.parts.append({"source": " ".join(toks[i:i + span]),
                            "target": out, "entry": best, "matched": True})
            _collect_notes(r, hit)
            if len(hit) > 1:
                r.senses.extend(hit[1:])
            matched_tokens += span
            i += span
        else:
            word = toks[i]
            near = lex.near(word, side=src_field, limit=3)
            pieces.append("[%s]" % word)
            r.parts.append({"source": word, "target": None,
                            "entry": None, "matched": False})
            for n in near:
                if n not in r.suggestions:
                    r.suggestions.append(n)
            i += 1

    r.text = " ".join(p for p in pieces if p)
    r.confidence = round(matched_tokens / len(toks), 2) if toks else 0.0
    return r


def _collect_notes(r, entries):
    for e in entries:
        n = e.get("note")
        if n and n not in r.notes:
            r.notes.append(n)


def format_result(r):
    """Human readable block for the CLI."""
    if not r.parts:
        return "Nothing to translate."

    arrow = "English to Tshivenda" if r.direction == "en-ve" else "Tshivenda to English"
    lines = ["[%s]" % arrow, "  %s" % title(r.text)]

    if r.confidence < 1.0 and len(r.parts) > 1:
        bits = []
        for p in r.parts:
            if p["matched"]:
                bits.append("%s = %s" % (p["source"], p["target"]))
            else:
                bits.append("%s = ?" % p["source"])
        lines.append("  breakdown: " + "; ".join(bits))

    lines.append("  confidence: %d%%" % int(r.confidence * 100))

    if r.senses:
        alt = []
        for e in r.senses[:4]:
            side = e.get("ve") if r.direction == "en-ve" else e.get("en")
            tag = e.get("context") or e.get("pos") or ""
            alt.append("%s%s" % (side, " (%s)" % tag if tag else ""))
        lines.append("  other senses: " + ", ".join(alt))

    for n in r.notes[:3]:
        lines.append("  note: " + n)

    if r.unknown:
        lines.append("  not in the dictionary: " + ", ".join(r.unknown))
        if r.suggestions:
            lines.append("  did you mean: " + ", ".join(r.suggestions[:5]))
        lines.append("  use /add to teach the bot these words")

    return "\n".join(lines)


def define(lex, word):
    """All senses of a word, with part of speech and notes."""
    hits = lex.senses_of(word)
    if not hits:
        near = lex.near(word, limit=5)
        msg = "No entry for '%s'." % word
        if near:
            msg += " Closest: " + ", ".join(near)
        return msg

    lines = ["%s  (%d sense%s)" % (title(word), len(hits), "" if len(hits) == 1 else "s")]
    for n, e in enumerate(hits, 1):
        head = "  %d. %s = %s" % (n, e.get("en", ""), e.get("ve", ""))
        tags = [t for t in (e.get("pos"), e.get("category"), e.get("context")) if t]
        if tags:
            head += "  [%s]" % ", ".join(tags)
        lines.append(head)
        if e.get("alt"):
            lines.append("     also: " + ", ".join(e["alt"]))
        if e.get("note"):
            lines.append("     note: " + e["note"])
        if e.get("review"):
            lines.append("     status: not yet verified by a speaker")
    return "\n".join(lines)
