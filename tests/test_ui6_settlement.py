"""Session UI-6 (November 13, 2026) - the settlement table, figures first (frame F16).

The blind readers scored the table 6/10: "a wall of italic and gold prose below the
court rows", "the draft's status is buried", "break it into one verdict panel plus
the table". Folded (Settings -> Interface -> Explanations, the default) the table
now opens on a verdict panel (one status tile, the treasury as tiles), the repeated
verdict lines leave the tail for the tile's hover and the one counsel note, the
court meters are wider, "The peace" is a card above the counsel (chips, badges, a
glyph list, one compact table) and the first-open line stays but quiet. On the page
every sentence prints exactly as before.

Source pins plus the backend sidecars (pure functions). Nothing here starts an engine.
"""
from __future__ import annotations

import pathlib

REPO = pathlib.Path(__file__).resolve().parents[1]
POPUP = REPO / "godot-client" / "project-sovereign" / "scripts" / "proposal_confirm_popup.gd"


def _src() -> str:
    return POPUP.read_text(encoding="utf-8")


def _func(src: str, head: str) -> str:
    return src.split(head, 1)[1].split("\nfunc ", 1)[0]


class TestTheVerdictPanel:
    def test_the_panel_is_folded_only_and_full_view_only(self):
        body = _func(_src(), "func _figures_first(")
        assert "not Utils.explanations_folded() or Utils.compact_view()" in body
        assert '"settlement_confirm"' in body

    def test_the_panel_is_a_stat_strip_under_the_title_row(self):
        src = _src()
        assert 'const _StatStrip := preload("res://scripts/stat_strip.gd")' in src
        body = _func(src, "func _sync_verdict_panel(")
        assert 'strip.name = "VerdictPanel"' in body
        assert "vb.move_child(strip, content_label.get_index())" in body
        # the panel is added to the tree BEFORE its tiles are set (the strip's _ready hides it)
        assert body.index("vb.add_child(strip)") < body.index("strip.set_tiles(")
        assert "_sync_verdict_panel(is_settlement_table)" in src
        assert "_sync_verdict_panel(true)" in _func(src, "func _on_explanations_changed(")

    def test_the_status_tile_reads_its_verdict_and_the_treasury_is_tiles(self):
        body = _func(_src(), "func _verdict_tiles(")
        # RE-SEATED (row PW, November 18, 2026 — the first playtest: "diplomacy
        # is very confusing"): the tiles read in everyday words. "Will carry"
        # -> "They will sign", "Will not carry" -> "They will not sign yet",
        # "Ready to ratify" -> "Ready to sign", "Cannot be ratified" ->
        # "Cannot be signed", "N of M hold out" -> "N of M refuse", and the
        # gold tiles "Committed / Reserve / Remaining" -> "Gold you offer /
        # In your treasury / Left if they sign" (what the deal pays, what the
        # purse holds, what would be left: the middle tile was the suggestions'
        # hold-back, which the dial spends — it fell while "Remaining" read 0).
        for words in ('"They will sign"', '"They will not sign yet"', '"Ready to sign"',
                      '"Cannot be signed"', '"%d of %d refuse"', '"Gold you offer"',
                      '"In your treasury"', '"Left if they sign"'):
            assert words in body, words
        assert "Utils.clean_tip(_verdict_words(data))" in body

    def test_the_heading_and_the_treasury_line_leave_the_head_folded(self):
        src = _src()
        head = _func(src, "func _build_settlement_content(")
        assert head.index("if _figures_first(data):") < head.index('elif dialogue_mode == "PROPOSE":')
        # On the page the heading still prints (row PW: its words come from
        # the ONE source, `_verdict_heading_words` — "They will not sign this yet.")
        assert "_verdict_heading_words(data)" in head
        assert 'return "They will not sign this yet."' in _func(src, "func _verdict_heading_words(")
        pre = _func(src, "func _build_settlement_table_preamble(")
        assert "and not _figures_first(data)" in pre
        # (row PW: the page's line says the tiles' own figures)
        assert "Treasury[/b] %s gold: you offer %s; left if they sign %s" in pre

    def test_no_sentence_is_lost_the_verdict_words_are_the_tiles_hover_and_the_counsel(self):
        src = _src()
        words = _func(src, "func _verdict_words(")
        for key in ("_verdict_heading_words(data)", "carry_verdict_display", "summary_display", "propose_carry_hint"):
            assert key in words, key
        counsel = _func(src, "func _build_settlement_counsel_below(")
        assert "summary_display" in counsel and "propose_carry_hint" in counsel
        assert "_quote_block(reading," in counsel

    def test_the_tail_drops_the_repeated_lines_folded_and_keeps_them_on_the_page(self):
        body = _func(_src(), "func _build_settlement_per_court_block(")
        assert body.index("if _figures_first(data):\n\t\treturn bbcode") < body.index('overall.get("summary_display", "")')
        assert '_fold_first_sentence("settle.carry", carry_hint)' in body


class TestTheCourtRowsAndThePeace:
    def test_the_meters_are_wider(self):
        assert "const COURT_METER_WIDTH := 160.0" in _src()

    def test_the_peace_card_sits_above_the_counsel(self):
        src = _src()
        render = _func(src, "func _render_per_court_table(")
        assert render.index("_build_peace_bbcode(data)") < render.index('counsel_label.name = "PerCourtCounsel"')
        for name in ('lead_label.name = "PerCourtLead"', 'tail_label.name = "PerCourtTail"',
                     'coverage_host.name = "CoverageHost"', 'footer_label.name = "PerCourtFooter"'):
            assert name in render, name
        assert 'label.name = "PerCourtPeace"' in _func(src, "func _peace_card(")

    def test_every_peace_sentence_is_a_hover_through_bb_hint(self):
        src = _src()
        for fn in ("_peace_titles_bbcode(", "_peace_manner_bbcode(", "_peace_revanche_bbcode(", "_peace_table_bbcode("):
            assert "Utils.bb_hint(" in _func(src, "func " + fn), fn
        assert "[hint=" not in _func(src, "func _build_peace_bbcode(")

    def test_the_footer_moves_its_blocks_into_the_card_folded_only(self):
        footer = _func(_src(), "func _build_settlement_footer(")
        assert "var figures: bool = _figures_first(data)" in footer
        for gate in ('if heading_voice != "" and not figures:', "and not figures:\n\t\t# PC-F33",
                     "if not figures:\n\t\tbbcode += _settlement_designs_lines(data)",
                     "if allies is Dictionary and not figures:", "if terms is Dictionary and not figures:",
                     "if ttext and not figures:"):
            assert gate in footer, gate
        # what the card does not own stays in the footer
        assert "Allied petitions" in footer and "road_closing" in footer

    def test_the_counsel_is_one_fold_with_talleyrands_first_sentence_as_its_hover(self):
        counsel = _func(_src(), "func _build_settlement_counsel_below(")
        assert "Utils.bb_hint(" in counsel and "first_words" in counsel
        assert "COUNSEL_NOTE_ID" in counsel and "settle.talleyrand" not in counsel

    def test_the_first_open_line_stays_but_quiet(self):
        """The line stays (first-open lines are never folded) in the quiet info ink — not a dim step under the
        contrast floor (tests/test_uxr3_s12_fixes.py's dim-token census)."""
        body = _func(_src(), "func _first_open_bbcode(")
        assert '"[color=#" + Utils.COLOR_INFO + "]" + line.replace("[", "[lb]")' in body
        assert "COLOR_DIM" not in body
        assert "[font" not in body


class TestTheSidecars:
    def test_manner_badges_read_off_the_manner_lines(self):
        from backend.game_logic.imperial_designs import MANNER_WORDS
        from backend.game_logic.settlement_staging import settlement_manner_badges

        lines = [
            {"court": "Austria", "line": "The manner of this peace: a partition — it brings Austria to terms."},
            {"court": "Britain", "line": "The manner of this peace: none — it brings Britain to no terms the Emperor's designs read."},
            {"court": "Russia", "line": "The manner of this peace: subjugation — Russia is brought to terms as the Emperor's vassal."},
            {"court": "Prussia", "line": "The manner of this peace: the moderate peace — Prussia is brought to terms once she allies."},
            {"court": "Spain", "line": "The manner of this peace: a partition — but while Spain's bloc holds French soil, the Emperor's designs record nothing of it."},
            {"court": "Nobody", "line": ""},
        ]
        got = {b["court"]: b["manner"] for b in settlement_manner_badges(lines)}
        assert got == {"Austria": "partition", "Britain": "none", "Russia": "subjugation",
                       "Prussia": "moderate", "Spain": "guarded"}
        assert set(MANNER_WORDS) == {"partition", "subjugation", "moderate"}
        assert settlement_manner_badges([]) == []

    def test_the_staged_payload_carries_both_sidecars_beside_the_unchanged_sentences(self):
        src = (REPO / "backend" / "game_logic" / "settlement_staging.py").read_text(encoding="utf-8")
        assert '"status_quo_regions": _status_quo_regions,' in src
        assert '"manner_badges": _manner_badges,' in src
        assert '"status_quo_review": _status_quo_review,' in src
        assert '"held_line_note": _held_note,' in src
        assert '"manner_lines": list(preview.get("manner_lines") or []),' in src
