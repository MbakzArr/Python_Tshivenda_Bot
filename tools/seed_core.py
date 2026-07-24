"""Add high frequency words so phrase translation actually works.

IMPORTANT: every entry here is added with review=true. A first language
speaker must confirm each one with /review before it can be trusted.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.lexicon import Lexicon

CORE = [
    # pronouns and concords
    ("I", "nne", "pronoun", "core", "emphatic form"),
    ("I", "ndi", "pronoun", "core", "subject concord used before a verb"),
    ("you", "iwe", "pronoun", "core", "one person, informal"),
    ("you", "inwi", "pronoun", "core", "polite or more than one person"),
    ("he", "ene", "pronoun", "core", "same word for she"),
    ("she", "ene", "pronoun", "core", "same word for he"),
    ("we", "rine", "pronoun", "core", ""),
    ("they", "vhone", "pronoun", "core", ""),
    ("me", "nne", "pronoun", "core", ""),
    ("my", "wanga", "pronoun", "core", "comes after the noun"),
    ("your", "wau", "pronoun", "core", "comes after the noun"),
    ("our", "washu", "pronoun", "core", ""),
    # question words
    ("what", "mini", "question", "core", ""),
    ("who", "nnyi", "question", "core", ""),
    ("where", "ngafhi", "question", "core", ""),
    ("when", "lini", "question", "core", ""),
    ("how", "hani", "question", "core", ""),
    ("why", "ngani", "question", "core", ""),
    ("how much", "bogani", "question", "core", "also used for how many"),
    # small words
    ("and", "na", "conjunction", "core", "also means with"),
    ("with", "na", "preposition", "core", "also means and"),
    ("yes", "ee", "particle", "core", ""),
    ("no", "hai", "particle", "core", ""),
    ("not", "a si", "particle", "core", ""),
    ("here", "hafha", "adverb", "core", ""),
    ("there", "henefho", "adverb", "core", ""),
    ("now", "zwino", "adverb", "core", ""),
    ("very", "vhukuma", "adverb", "core", ""),
    ("again", "hafhu", "adverb", "core", ""),
    ("all", "vhothe", "adverb", "core", ""),
    # everyday verbs
    ("to go", "u ya", "verb", "core", ""),
    ("to come", "u da", "verb", "core", ""),
    ("to eat", "u la", "verb", "core", ""),
    ("to drink", "u nwa", "verb", "core", ""),
    ("to sleep", "u edela", "verb", "core", ""),
    ("to see", "u vhona", "verb", "core", ""),
    ("to speak", "u amba", "verb", "core", ""),
    ("to hear", "u pfa", "verb", "core", "also means to feel"),
    ("to know", "u divha", "verb", "core", ""),
    ("to want", "u toda", "verb", "core", "also means to look for"),
    ("to buy", "u renga", "verb", "core", ""),
    ("to work", "u shuma", "verb", "core", ""),
    ("to write", "u nwala", "verb", "core", ""),
    ("to read", "u vhala", "verb", "core", "also means to count"),
    ("to give", "u nea", "verb", "core", ""),
    ("to help", "u thusa", "verb", "core", ""),
    ("to learn", "u guda", "verb", "core", ""),
    ("to teach", "u funza", "verb", "core", ""),
    # numbers
    ("one", "nthihi", "number", "number", ""),
    ("two", "mbili", "number", "number", ""),
    ("three", "tharu", "number", "number", ""),
    ("four", "ina", "number", "number", ""),
    ("five", "thanu", "number", "number", ""),
    ("six", "rathi", "number", "number", ""),
    ("seven", "sumbe", "number", "number", ""),
    ("eight", "malo", "number", "number", ""),
    ("nine", "tahe", "number", "number", ""),
    ("ten", "fumi", "number", "number", ""),
    # courtesy
    ("thank you", "ndo livhuwa", "phrase", "greeting", ""),
    ("please", "ndi khou humbela", "phrase", "greeting", "literally I am asking"),
    ("sorry", "ndi khou humbela pfarelo", "phrase", "greeting", ""),
    ("goodbye", "kha vha sale zwavhudi", "phrase", "greeting", "said to the one staying"),
]


def main():
    dest = sys.argv[1] if len(sys.argv) > 1 else "data/lexicon.json"
    lex = Lexicon.load(dest)
    added = 0
    for en, ve, pos, cat, note in CORE:
        if not lex.duplicate_of(en, ve):
            lex.add(en=en, ve=ve, pos=pos, category=cat, note=note, review=True)
            added += 1
    lex.build()
    lex.save(dest)
    print("added %d core words, total %d" % (added, len(lex.entries)))
    print("all flagged for review, check them with /review")


if __name__ == "__main__":
    main()
