import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from core.lexicon import Lexicon
from core.text import fold, ve_score, strip_marks
from core.translate import translate, detect, variants, define
from core import quiz, learn


@pytest.fixture
def lex():
    return Lexicon.load()


# ---------- text handling ----------

def test_fold_removes_case_and_punctuation():
    assert fold("  Hello, World!  ") == "hello world"


def test_marks_are_stripped_for_matching():
    assert strip_marks("\u1e13uvha") == "duvha"
    assert fold("\u1e13uvha") == fold("Duvha")


def test_tshivenda_scores_higher_than_english():
    assert ve_score("ndi khou ya") > ve_score("I am going")
    assert ve_score("Ndala") > ve_score("Hunger")


# ---------- lexicon ----------

def test_lexicon_loads(lex):
    assert len(lex.entries) > 200


def test_one_word_can_hold_several_senses(lex):
    senses = lex.senses_of("duvha")
    meanings = {s["en"].lower() for s in senses}
    assert len(senses) >= 2
    assert "day" in meanings and "sun" in meanings


def test_thambo_keeps_both_meanings(lex):
    meanings = {s["en"].lower() for s in lex.senses_of("thambo")}
    assert "rope" in meanings and "invitation" in meanings


def test_every_entry_has_the_required_fields(lex):
    for e in lex.entries:
        assert e["id"] and e["en"] and e["ve"]
        assert isinstance(e.get("alt", []), list)


def test_ids_are_unique(lex):
    ids = [e["id"] for e in lex.entries]
    assert len(ids) == len(set(ids))


# ---------- direction ----------

def test_direction_english_to_tshivenda(lex):
    assert detect(lex, "water") == "en-ve"


def test_direction_tshivenda_to_english(lex):
    assert detect(lex, "madi") == "ve-en"


# ---------- translation ----------

def test_exact_phrase_is_full_confidence(lex):
    r = translate(lex, "thank you")
    assert r.confidence == 1.0
    assert "livhuwa" in r.text.lower()


def test_unknown_words_are_marked_not_invented(lex):
    r = translate(lex, "quixotic zzzz", direction="en-ve")
    assert r.unknown
    assert r.confidence < 0.5


def test_partial_phrase_still_returns_what_it_knows(lex):
    r = translate(lex, "where is my house")
    assert 0 < r.confidence < 1.0
    assert any(p["matched"] for p in r.parts)


def test_empty_input_is_safe(lex):
    r = translate(lex, "")
    assert not r.ok


def test_verb_endings_resolve(lex):
    assert "to go" in variants("going", "en-ve")
    assert "to want" in variants("wants", "en-ve")
    assert "u toda" in variants("toda", "ve-en")


def test_define_lists_all_senses(lex):
    out = define(lex, "duvha")
    assert "sense" in out.lower()


def test_define_handles_missing_word(lex):
    assert "no entry" in define(lex, "zzzzqqq").lower()


# ---------- quiz ----------

def test_quiz_question_has_the_answer_among_options(lex):
    q = quiz.make(lex)
    assert q is not None
    assert q.answer in q.options
    assert 2 <= len(q.options) <= 4


def test_quiz_accepts_letter_and_word(lex):
    q = quiz.make(lex)
    letter = chr(ord("a") + q.options.index(q.answer))
    assert q.check(letter)
    assert q.check(q.answer)
    assert not q.check("definitely wrong answer")


# ---------- spaced repetition ----------

def test_wrong_answer_schedules_a_retry(tmp_path):
    p = learn.Progress(path=str(tmp_path / "p.json"))
    p.grade("e0001", False)
    assert p.card("e0001")["interval"] == 1
    assert p.card("e0001")["wrong"] == 1


def test_repeated_correct_answers_push_the_interval_out(tmp_path):
    p = learn.Progress(path=str(tmp_path / "p.json"))
    for _ in range(4):
        p.grade("e0001", True)
    assert p.card("e0001")["interval"] > 3


def test_progress_survives_a_reload(tmp_path):
    path = str(tmp_path / "p.json")
    p = learn.Progress(path=path)
    p.grade("e0002", True)
    p.save()
    again = learn.Progress(path=path)
    assert "e0002" in again.cards


# ---------- service layer shared by every interface ----------

@pytest.fixture
def svc():
    from core.api import Service
    return Service()


def test_service_translate_is_json_ready(svc):
    d = svc.translate("water")
    assert d["ok"] and d["direction"] == "en-ve"
    assert isinstance(d["parts"], list)
    import json
    json.dumps(d)


def test_service_reports_gaps_without_inventing_words(svc):
    d = svc.translate("where is my house")
    assert "is" in d["unknown"]
    assert all(p["target"] or not p["matched"] for p in d["parts"])


def test_service_define_returns_every_sense(svc):
    d = svc.define("duvha")
    assert len(d["senses"]) >= 2


def test_service_rejects_a_half_filled_word(svc):
    assert svc.add_word("", "duvha")["ok"] is False
    assert svc.add_word("day", "")["ok"] is False


def test_service_refuses_a_duplicate(svc):
    d = svc.add_word("day", "duvha")
    assert d["ok"] is False and "Already" in d["error"]


def test_service_quiz_round_trip(svc):
    q = svc.new_question()
    assert q["ok"] and q["options"]
    a = svc.answer(q["token"], q["options"][0])
    assert a["ok"] and isinstance(a["correct"], bool)


def test_service_rejects_an_expired_quiz_token(svc):
    assert svc.answer("not-a-real-token", "a")["ok"] is False


def test_service_review_rejects_unknown_id(svc):
    assert svc.review("nope", "confirm")["ok"] is False


def test_pending_matches_the_review_count(svc):
    s = svc.stats()
    assert svc.pending(1000)["total"] == s["needs_review"]
