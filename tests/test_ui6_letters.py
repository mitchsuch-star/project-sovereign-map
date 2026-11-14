"""Session UI-6 - the letters and the objection (frames F21, F22, F23).

The blind readers' complaints: the client's petition (F21) - small chips, the
Talleyrand quote truncated and dim; Berthier's memorial, an Affair of State letter
(F22) - a dense block, text over the ragged border, a stray empty seal; the
Marshal's objection (F23) - four answers of unequal size. Layout only: no authored
word changes. Source pins only (no engine is started here).
"""
from __future__ import annotations

import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"


def _read(name: str) -> str:
    return (SCRIPTS / name).read_text(encoding="utf-8")


def _func(src: str, name: str) -> str:
    at = src.index(f"func {name}(")
    ends = [i for i in (src.find("\nfunc ", at + 10), src.find("\nstatic func ", at + 10)) if i != -1]
    return src[at:min(ends)] if ends else src[at:]


POPUP = _read("incoming_proposal_popup.gd")
DIALOG = _read("objection_dialog.gd")


class TestThePetition:
    def test_the_chips_are_larger_with_room_around_them(self):
        chip = _func(POPUP, "_chip")
        assert "padding=10,6,10,6" in chip
        assert "Utils.CHIP_CLOSE" in chip
        row = _func(POPUP, "_figure_row")
        assert "_chip(str(fig), tone_hex)" in row and "Utils.bb_badge" not in row

    def test_talleyrands_reading_is_whole_and_bright_on_a_petition(self):
        block = _func(POPUP, "_assessment_block")
        assert "_assessment_id == NOTE_PETITION and Utils.explanations_folded()" in block
        whole = block[:block.index("var cut :=")]
        assert "Utils.COLOR_TEXT" in whole and "_assessment_text" in whole
        # On the page and every other assessment keep the grey note, byte for byte
        assert '"\\n[color=gray]" + Utils.bb_note(_assessment_id, summary, rest) + "[/color]\\n"' in block


class TestTheLetter:
    def test_the_body_breaks_into_short_paragraphs_with_the_same_words(self):
        body = _func(POPUP, "_build_moment_body")
        for key in ('_paragraphs(_moment_text(data.get("line", "")))',
                    '_paragraphs(_moment_text(data.get("record", "")))',
                    '_paragraphs(_moment_text(data.get("exhibit", "")))'):
            assert key in body
        assert "_gap()" in body
        para = _func(POPUP, "_paragraphs")
        # layout only: sentences are re-joined, never rewritten
        assert '" ".join(' in para
        assert "PARA_ABBREVIATIONS" in para
        gap = _func(POPUP, "_gap")
        # the lead's frame reading (Nov 13): a whole blank line between parts
        # and groups pushed the answers below the sheet's fold — a part opens on
        # its own line (HEAD's height), a new paragraph is indented as a letter
        # is set, and the answers' heading takes one break, never two
        assert 'return "\\n"' in gap and "font_size" not in gap
        assert '("\\n" + PARA_INDENT).join(PackedStringArray(groups))' in para
        assert 'const PARA_INDENT := "\\u2003\\u2003"' in POPUP
        assert 'out = out.trim_suffix("\\n") + _gap() + "[color=#" + Utils.INK_RUBRIC' in body

    def test_the_words_stay_inside_the_torn_rim(self):
        assert re.search(r"const LETTER_SHEET_PAD_X := (\d+)\.0", POPUP)
        pad_x = float(re.search(r"const LETTER_SHEET_PAD_X := ([\d.]+)", POPUP).group(1))
        pad_y = float(re.search(r"const LETTER_SHEET_PAD_Y := ([\d.]+)", POPUP).group(1))
        assert pad_x >= 36.0 and pad_y >= 30.0
        ensure = _func(POPUP, "_ensure_letter_dress")
        assert '_sheet.set("content_margin_" + side, LETTER_SHEET_PAD_X)' in ensure
        assert '_sheet.set("content_margin_" + side, LETTER_SHEET_PAD_Y)' in ensure

    def test_the_empty_seal_ring_is_gone(self):
        ensure = _func(POPUP, "_ensure_letter_dress")
        assert "StyleBoxEmpty.new()" in ensure
        assert "set_border_width_all(1)\n\tring" not in ensure


class TestTheObjection:
    def test_the_answers_stand_level(self):
        dress = _func(DIALOG, "_dress_answers")
        assert "btn.size_flags_vertical = Control.SIZE_EXPAND_FILL" in dress
        assert 'grid.name = "AnswerGrid"' in dress and "grid.columns = 2" in dress
        even = _func(DIALOG, "_even_the_answers")
        assert "tallest" in even and "custom_minimum_size.y = tallest" in even
        assert "custom_minimum_size.x = 0.0" in even

    def test_cancel_joins_the_grid_when_it_makes_an_even_block(self):
        fit = _func(DIALOG, "_fit_compact")
        assert "grid.columns = 3 if compact else 2" in fit          # UI-5's 2.0 rule kept
        assert "var joins: bool = compact or _standing_answers() % 2 == 1" in fit
        stand = _func(DIALOG, "_standing_answers")
        for name in ("trust_button", "insist_button", "word_button", "compromise_button"):
            assert name in stand

    def test_no_authored_label_changed(self):
        for label in ('_face("Proceed as Ordered", "%+d trust"', '"By My Word"',
                      '_face("Cancel the Order", "no cost")', '_face("Compromise: %s" % comp_desc, "%+d trust"'):
            assert label in DIALOG
