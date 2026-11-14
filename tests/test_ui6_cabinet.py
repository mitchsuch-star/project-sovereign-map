"""Session UI-6 (November 13, 2026) - the Cabinet's two steps (frames F14, F15).

The UI-5 readers held both frames at 7: "the intro paragraph is long, and the list
needs scrolling to reach most nations", "the nation row sits misaligned with the
relation text", "put the recommendation first and loud", "the dashed disabled rows
are hard to read - widen the action column", "the recommendation text cramped".

Source pins only (no engine). Folded (the default) carries the changes; On the
page keeps every old line.
"""
from __future__ import annotations

import pathlib

REPO = pathlib.Path(__file__).resolve().parents[1]
WIZ = REPO / "godot-client" / "project-sovereign" / "scripts" / "diplomacy_wizard.gd"


def _src() -> str:
    return WIZ.read_text(encoding="utf-8")


def _func(src: str, name: str) -> str:
    at = src.index(f"func {name}(")
    end = src.find("\nfunc ", at + 10)
    return src[at:end if end >= 0 else len(src)]


def test_the_first_open_line_is_never_folded():
    """The user's standing ruling (Session UI-3's record): the first-open lines stay on the face. The Cabinet's
    prints whole at the head of step 1 in both modes and is acknowledged as drawn."""
    src = _src()
    body = _func(src, "_add_first_open_line")
    assert "Utils.explanations_folded()" not in body
    assert "lead_mark(" not in body and "PREFACE_NOTE" not in src
    assert '"[color=#" + Utils.COLOR_INFO + "]" + _bb(line) + "[/color]"' in body
    assert body.index("content_list.add_child(lbl)") < body.index("first_open_seen.emit(screen)")


def test_the_switch_redraws_step_one():
    body = _func(_src(), "_on_explanations_changed")
    assert "_current_step == 1" in body and "_render_nations(_last_nations_data)" in body


def test_a_court_row_is_fixed_columns_folded_and_the_old_row_on_the_page():
    src = _src()
    row = _func(src, "_add_nation_button")
    assert "_add_nation_columns(row, nation_data, state_display)" in row
    # the page branch is untouched
    assert 'figures.custom_minimum_size.x = float(Utils.text_px(230))' in row
    cols = _func(src, "_add_nation_columns")
    assert "tag.custom_minimum_size.x" in cols and "rel_cell.custom_minimum_size.x" in cols
    assert "Utils.bb_relation_meter(rel, 80, 7)" in cols
    assert "Utils.bb_badge(state_display" in cols and "MISSION" in cols


def test_the_counsel_card_stands_first_folded_in_the_title_face():
    src = _src()
    render = _func(src, "_render_preview")
    assert "var counsel_at: int = bbcode.length()" in render
    assert "bbcode = head_bb.substr(0, counsel_at) + bbcode + head_bb.substr(counsel_at)" in render
    # On the page the old line and its order stand
    assert '"[color=#" + Utils.COLOR_GOLD + "]Recommendation: " + recommendation + "[/color]\\n"' in render
    verdict = _func(src, "_verdict_line")
    assert "Utils.HEAD_OPEN" in verdict and "Recommendation: " in verdict and "Utils.HEAD_CLOSE" in verdict
    assert "Utils.note_link(COUNSEL_NOTE)" in render  # the "more" link is kept


def test_the_columns_stand_45_55_folded_and_even_on_the_page():
    src = _src()
    assert "const ASSESSMENT_COLUMN_RATIO := 0.45" in src
    assert "const ACTIONS_COLUMN_RATIO := 0.55" in src
    body = _func(src, "_sync_body")
    assert "_actions_col.size_flags_stretch_ratio = ACTIONS_COLUMN_RATIO if Utils.explanations_folded() else 1.0" in body
    assert "ASSESSMENT_COLUMN_RATIO if Utils.explanations_folded() else 1.0" in body


def test_the_key_factors_span_their_column_folded():
    src = _src()
    assert "Utils.bb_table([\"Factor\", \"Value\"], factor_rows, [1], [4, 1], _factors_width())" in _func(src, "_render_preview")
    width = _func(src, "_factors_width")
    assert "if not Utils.explanations_folded():\n\t\treturn 0.0" in width


def test_a_shut_act_reads_shut_yet_legible_and_its_reason_is_the_hover():
    body = _func(_src(), "_add_action_button")
    assert 'btn.add_theme_color_override("font_disabled_color", Utils.UI_TEXT_DIM)' in body
    assert "btn.tooltip_text = disabled_reason" in body
    # folded: no printed reason line; the page branch keeps it
    assert "if has_reason and not Utils.explanations_folded():" in body
    assert "reason_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART" in body
    assert "0.85 if Utils.explanations_folded() else 0.6" in body


def test_dim_words_pass_contrast_on_the_panel():
    """UI_TEXT_DIM (0.75, 0.72, 0.65) on the window's dark ground clears 4.5:1."""
    def lin(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    def lum(r: float, g: float, b: float) -> float:
        return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)

    fg = lum(0.75, 0.72, 0.65)
    bg = lum(0.12, 0.13, 0.19)
    assert (fg + 0.05) / (bg + 0.05) >= 4.5


def test_on_the_compact_view_talleyrands_quote_opens_above_the_fold():
    """EA-E5 at 2.0 (the engine lanes, Session UI-6): with the counsel card
    first, the assessment's 30 % held the heading, a two-line status and the
    title-face verdict wrapped to two lines — the quote stood under its fold.
    Folded on the compact view the heading steps aside (the window's title
    names the court) and the verdict is bold gilt in the body face, one line;
    elsewhere, and On the page, both stand as authored."""
    src = _src()
    render = _func(src, "_render_preview")
    gate = render.index("if Utils.explanations_folded() and Utils.compact_view():")
    assert render.index('"TALLEYRAND\'S ASSESSMENT — "') > gate
    verdict = _func(src, "_verdict_line")
    compact = verdict.index("if Utils.compact_view():")
    assert '"[b][color=#" + Utils.COLOR_GOLD + "]Recommendation: "' in verdict[compact:]
    assert compact < verdict.index("Utils.HEAD_OPEN")


def test_the_compact_assessment_cap_holds_the_quotes_opening_line():
    """Session UI-6: 0.3 -> 0.33 on the compact view (the quote's opening line
    stood cut by 6 px on the 392-px panel); the full view's 0.5 is UI-4's."""
    src = _src()
    assert "const ASSESSMENT_CAP_SHARE_COMPACT := 0.33" in src
    assert "const ASSESSMENT_CAP_SHARE := 0.5" in src
