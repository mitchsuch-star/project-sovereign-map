"""AU-3a the close — the Mode C walk on 8007, read off its committed record
(`docs/AUTHORITY_CURRENCY_SPEC.md` §10: "the Mode C walk of the chip, a letter
decreed, a word given and a Te Deum at AU-3a's close"; the landing record §6.5).

`tools/au3a_mode_c_walk.py` ran the real `main.tscn` against a sandboxed
backend (two crafted saves staged by `tools/au3a_stage_saves.py`) and wrote
`docs/audits/au3a_mode_c_2026_11_05/walk.json` (what each step read off the
screen's own nodes) and `run.json` (the engine's own log, censused). The pins
read the record, never the screen: every step present with its read, no
SCRIPT ERROR in a log that was written, the frames beside them.
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
AUDIT = REPO / "docs" / "audits" / "au3a_mode_c_2026_11_05"
STEPS = ("chip", "objection_word", "word_given", "letter_decree", "decreed",
         "te_deum_before", "te_deum", "te_deum_dispatch", "te_deum_gazette")


def _walk():
    return json.loads((AUDIT / "walk.json").read_text(encoding="utf-8"))


def _run():
    return json.loads((AUDIT / "run.json").read_text(encoding="utf-8"))


def _by(walk):
    return {s["step"]: s for s in walk["steps"]}


class TestTheWalkRanClean:
    def test_every_step_is_on_the_record_with_its_frame(self):
        walk = _walk()
        by = _by(walk)
        assert [s["step"] for s in walk["steps"]] == list(STEPS)
        for name in STEPS:
            s = by[name]
            assert s["saved"] is True and s["frame"].endswith(".jpg"), name
            assert (AUDIT / "frames" / s["frame"]).is_file(), s["frame"]
        assert walk["booted"] is True and walk["errors"] == [], walk["errors"]
        assert "error" not in walk

    def test_no_script_error_in_a_log_that_was_written(self):
        run = _run()
        assert run["engine_exit"] == 0 and run["script_errors"] == []
        assert run["engine_log_bytes"] > 0          # the census read the engine's own log
        assert run["staged"] == {"b": True, "d": True}
        assert run["port"] != 8005


class TestTheChipTheWordTheDecreeAndTheTeDeum:
    def test_the_chip_on_the_boot(self):
        chip = _by(_walk())["chip"]["chip"]
        assert chip["present"] and chip["visible"] and chip["text"] == "Authority 100"

    def test_the_word_is_offered_priced_and_given(self):
        by = _by(_walk())
        word = by["objection_word"]["buttons"]["word_button"]
        assert word["visible"] and not word["disabled"]
        assert word["text"] == "By My Word (-3 authority)"
        assert "By your word: no trust or defiance; lost within 3 turns" in word["tooltip"]
        given = by["word_given"]
        assert given["chip"]["text"] == "Authority 97"
        assert "your word given over Ney's objection (−3)" in given["chip"]["tooltip"]
        assert any(line.startswith("By your word, Ney carries out the order as given.")
                   for line in given["reply_lines"]), given["reply_lines"]

    def test_the_letter_offers_the_decree_third_and_it_lands(self):
        by = _by(_walk())
        letter = by["letter_decree"]
        assert letter["title"] == "The Remounts" and letter["register"] == "affair"
        assert letter["answers"] == ["accept_ai_proposal", "reject_ai_proposal", "decree_ai_proposal"]
        assert letter["counter_visible"] and not letter["counter_disabled"]
        assert letter["counter"] == "Decree it / auth 90 → 87 · 1 action · 8 turns"
        decreed = by["decreed"]
        assert decreed["chip_before"]["text"] == "Authority 90" and decreed["chip"]["text"] == "Authority 87"
        assert "the Remounts decreed on the Emperor's word (−3)" in decreed["chip"]["tooltip"]
        assert "Answering The Remounts: Decree it" in decreed["reply_lines"]

    def test_the_te_deum_lands_on_the_chip_the_dispatch_and_the_moniteur(self):
        by = _by(_walk())
        te = by["te_deum"]
        assert te["chip_before"]["text"] == "Authority 88" and te["chip"]["text"] == "Authority 92"
        assert te["tooltip_has_te_deum"] is True
        assert any("up 4 since yesterday: the Te Deum for the peace with Austria (+4)" in line
                   for line in by["te_deum_dispatch"]["dispatch_lines"])
        gazette = by["te_deum_gazette"]
        assert gazette["gazette_open"] is True
        assert "PARIS — A Te Deum is sung at Notre-Dame for the peace" in gazette["gazette_lines"]
