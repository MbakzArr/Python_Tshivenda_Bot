import re
import unicodedata

# Tshivenda uses d, l, n, t, n and v with a mark underneath. We keep the
# marks for display but strip them for matching, so somebody typing
# "duvha" still finds an entry stored with the proper marks.

VOWELS = "aeiou"

# Almost every Tshivenda word ends in a vowel. That single rule is the
# strongest signal we have for telling the two languages apart.

VE_PREFIX = ("vha", "mu", "mi", "tsh", "zwi", "zwa", "ma", "lu", "dz", "nga",
             "khou", "ndi", "thi", "ri", "vhu", "ha", "mv", "nn", "tha",
             "the", "tho", "no", "ndo")

VE_CLUSTER = ("dz", "zw", "tsh", "vh", "ng", "ny", "khw", "sw", "tsw",
              "nd", "mb", "nw", "hw", "bv", "fh")

EN_SUFFIX = ("ing", "ed", "tion", "sion", "ness", "ment", "able", "ible",
             "ous", "ful", "less", "est", "ight", "ck", "gh",
             "er", "ly", "ty", "cy", "ry")

EN_WORDS = {
    "the", "a", "an", "is", "are", "am", "i", "you", "he", "she", "it", "we",
    "they", "to", "of", "in", "on", "at", "my", "your", "his", "her", "our",
    "their", "and", "or", "but", "with", "for", "from", "this", "that",
    "these", "those", "was", "were", "be", "been", "have", "has", "had",
    "do", "does", "did", "not", "no", "yes", "what", "when", "where", "who",
    "why", "how", "will", "would", "can", "could", "should", "there", "here",
    "very", "too", "also", "some", "any", "all", "more", "most", "than",
    "then", "if", "so", "up", "down", "out", "about", "into", "over", "me",
}


def strip_marks(s):
    out = unicodedata.normalize("NFD", str(s))
    return "".join(c for c in out if not unicodedata.combining(c))


def fold(s):
    """Lowercase, strip marks and punctuation. Every lookup key goes through this."""
    s = strip_marks(str(s).lower().strip())
    s = s.replace("'", "")
    s = re.sub(r"[^\w\s-]", " ", s)
    s = re.sub(r"[\s_]+", " ", s)
    return s.strip()


def words(s):
    t = fold(s)
    return t.split() if t else []


def has_marks(s):
    return any(unicodedata.combining(c) for c in unicodedata.normalize("NFD", str(s)))


def word_score(w):
    """Positive means the word looks Tshivenda, negative means English."""
    if not w:
        return 0.0
    if w in EN_WORDS:
        return -2.0

    s = 1.2 if w[-1] in VOWELS else -1.5

    if any(w.startswith(p) for p in VE_PREFIX):
        s += 0.5
    if any(c in w for c in VE_CLUSTER):
        s += 0.6
    if len(w) > 3 and any(w.endswith(x) for x in EN_SUFFIX):
        s -= 1.0

    # letters that do not appear in Tshivenda spelling on their own
    for ch in ("c", "q", "x", "j"):
        if ch in w and "tsh" not in w:
            s -= 0.8
            break
    return s


def ve_score(s):
    """0 means clearly English, 1 means clearly Tshivenda."""
    toks = words(s)
    if not toks:
        return 0.5
    total = sum(word_score(w) for w in toks) / len(toks)
    if has_marks(s):
        total += 2.0
    return max(0.0, min(1.0, (total + 1.5) / 3.0))


def title(s):
    return s[:1].upper() + s[1:] if s else s
