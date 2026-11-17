"""Session UI-6 (November 13, 2026) - the province panel at 6: frame F24.

The blind readers scored the province panel 6/10: "a wall of small prose",
"tiny disabled chips", "no clear primary action", "lead with a stat strip",
"make the recruit and build actions real buttons". Folded (Settings ->
Interface -> Explanations, the default) the panel now reads figures first:

* the figures row leads, under the controller line and before ACTIONS, and
  war damage is a RED figure tile in it (its sentence the tile's hover);
* RECRUIT is one line - a "Levies x1.45" tag (the ordinance sentence its
  hover) and the arm chips - and ONE lock chip "Levies" when every arm is
  refused for the same reason;
* Build's upkeep parenthetical is a "40g / turn each" tag;
* the march captions' sentences, the Land chip's tail and the army's per-corps
  lines ride hovers;
* FORCES PRESENT is one row per marshal: his name (ours: a link, meta
  "select:<Name>", signal marshal_select_requested), strength with the arm's
  glyph, a status badge from MarshalState, the context verbs and a "+N orders"
  toggle (meta "toggle:orders:<Name>") that opens the rest in place;
* at the compact view the panel is capped near 30 % of the HUD band (min 360);
* the avoided command desk clamps the panel's height only where it shares the
  panel's columns (the 32:9 layout stands it in a full-height left column).

On the page (switch off) every word prints as it did - the page branches are
pinned here as still present. Source-level pins, the repo's idiom (the engine
is run by the lead, never by a builder).
"""

from __future__ import annotations

import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"
SRC = (SCRIPTS / "region_panel.gd").read_text(encoding="utf-8")


def _func(name: str, src: str = SRC) -> str:
    start = src.index(f"func {name}(")
    rest = src[start:]
    end = rest.find("\nfunc ", 1)
    return rest if end < 0 else rest[:end]


def _code(src: str) -> str:
    return "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))


class TestTheFiguresLead:
    def test_the_facts_row_takes_war_damage_as_a_red_tile(self):
        fn = _func("_facts_row")
        assert "war_damage: int = 0" in fn
        assert "Utils.bb_glyph(\"war\", 18, Utils.COLOR_ERROR)" in fn
        assert "Utils.bb_hint(tile," in fn and "suppressing this province's income" in fn

    def test_folded_the_row_is_spliced_before_the_actions(self):
        body = _func("_render")
        assert "var folded_facts := \"\"" in body
        assert "folded_facts = _facts_row(" in body
        # the page's lines stay (the facts_page literal, the war damage line)
        assert "bbcode += facts_page" in body
        assert '"War damage: [color=#"' in body
        splice = body.index('bbcode = bbcode.substr(0, actions_at) + actions + "\\n"')
        facts = body.index("bbcode = bbcode.substr(0, actions_at) + folded_facts")
        assert splice < facts, "the figures row is put in at the same index AFTER ACTIONS, so it stands above it"

    def test_the_war_damage_sentence_leaves_the_folded_page(self):
        body = _func("_render")
        guard = body.index("if war_dmg > 0:")
        assert "if not Utils.explanations_folded():" in body[guard:guard + 400]


class TestRecruitOnOneLine:
    def test_the_ordinance_is_a_tag_with_the_sentence_as_hover(self):
        fn = _func("_ordinance_tag")
        assert '"Levies ×"' in fn and "Utils.bb_tag(" in fn and "Utils.bb_hint(" in fn
        assert '" over the ordinance"' in fn and '" under the ordinance"' in fn
        assert "ordinance_mult_pct" in fn
        # the page's own sentence is untouched
        assert "func _ordinance_note(" in SRC

    def test_the_folded_levy_is_one_line_with_one_lock(self):
        fn = _func("_recruit_rows_folded")
        assert "_ordinance_tag(levy)" in fn
        assert 'Utils.bb_chip_disabled("Levies", "", str(shorts.keys()[0]))' in fn
        assert "shorts.size() == 1" in fn and "chips.is_empty()" in fn
        assert "rows.append(line)" in fn and "_chip_row(" not in fn
        assert "_recruit_refusal_line" not in SRC

    def test_the_arm_chips_send_what_they_sent(self):
        fn = _func("_recruit_rows_folded")
        assert '"do:recruit " + str(arm) + " in " + _region' in fn


class TestBuildAndTheMarchCaptions:
    def test_the_upkeep_is_a_tag_folded_and_a_sentence_on_the_page(self):
        body = _func("_render")
        assert 'str(upkeep) + "g / turn each"' in body
        assert '"each finished work keeps " + str(upkeep) + "g a turn"' in body
        assert '(each finished work keeps " + str(upkeep) + "g a turn)' in body   # the page

    def test_the_captions_sentences_ride_their_hover_folded(self):
        fn = _func("_march_caption")
        assert "Utils.bb_hint(Utils.HEAD_OPEN + title + Utils.HEAD_CLOSE, sentence)" in fn
        # the page prints title and sentence as it did
        assert 'Utils.HEAD_CLOSE + "  [color=#" + Utils.COLOR_INFO + "]" + sentence' in fn
        sect = _func("_march_here_section")
        for title in ('"MARCH HERE"', '"THE ARMY"', '"SUPPORT "', '"FOLLOW "'):
            assert f"_march_caption({title}" in sect, title
        for sentence in ("a standing order — he marches on each turn",
                         "he follows, and marches to the guns",
                         "one order, the Staff's price, every corps within the Emperor's reach"):
            assert sentence in sect, sentence

    def test_the_armys_per_corps_lines_ride_its_chip(self):
        for name in ("_army_detour_rows", "_army_rider_rows"):
            fn = _func(name)
            assert "if Utils.explanations_folded():" in fn and "return out" in fn
        tip = _func("_army_corps_tip")
        # Row BA, BA-4 (BA2-X21): the men a corps' first march costs ride the
        # ARMY chip's hover too, first of the per-corps lines.
        assert '["march_cost", "detour", "guard", "front", "terms"]' in tip
        rows = _func("_quote_rows")
        assert '== "army"' in rows and "_army_corps_tip(q)" in rows

    def test_the_land_chip_carries_its_tail_as_a_hover_folded(self):
        body = _func("_render")
        assert "land_tip" in body and "slip past" in body
        assert "If it lands: " in body
        assert body.count('"do:land " + who + " in " + _region') == 2   # folded chip + the page's


class TestForcesPresentIsOneRowAMarshal:
    def test_the_signal_and_the_two_metas(self):
        assert "signal marshal_select_requested(marshal_name: String)" in SRC
        meta = _func("_on_meta_clicked")
        assert 'meta_str.begins_with("select:")' in meta
        assert "marshal_select_requested.emit(picked)" in meta
        assert 'meta_str.begins_with("toggle:orders:")' in meta
        assert "_orders_open" in meta

    def test_the_folded_render_uses_the_row_and_the_page_keeps_its_own(self):
        body = _func("_render")
        assert "bbcode += _marshal_row_folded(m, enemy_names)" in body
        assert "bbcode += _format_marshal_row(m, enemy_names)" in body
        page = _func("_format_marshal_row")
        assert 'muster_lines.append("Attack " + enemy_shown + ": " + _muster_tail(chip_muster))' in page

    def test_the_row_reads_the_shared_marshal_state(self):
        fn = _func("_marshal_row_folded")
        assert "_MarshalState.from_board(m, {})" in fn
        assert "_MarshalState.status_of(view)" in fn
        assert "_MarshalState.order_specs(view)" in fn
        assert 'preload("res://scripts/marshal_state.gd")' in SRC
        assert '"[url=select:" + m_name' in fn
        assert '"[url=toggle:orders:" + m_name + "]"' in fn
        assert '" orders"' in fn and '"fewer orders"' in fn
        # the CN-4 census (the lead's engine run): the folded orders' reasons
        # ride the fold's own hover — a folded reason is a hover
        assert 'toggle_bb = Utils.bb_hint(toggle_bb, " · ".join(PackedStringArray(hidden)))' in fn
        assert 'part += " — " + str(spec.get("reason", ""))' in fn

    def test_the_verbs_are_attack_else_two_lit_orders_and_the_rest_toggles(self):
        fn = _func("_marshal_row_folded")
        assert "enemy_names.size(), 2" in fn
        assert "_CONTEXT_SHOWN" in fn and "const _CONTEXT_SHOWN := 2" in SRC
        assert 'verb == "cancel"' in fn   # the panel never offered a Cancel chip
        assert "rest_lit + rest_locked" in fn

    def test_the_muster_is_the_attack_chips_hover(self):
        fn = _func("_marshal_row_folded")
        assert "_here_attack_muster(m_name, enemy)" in fn
        assert '_here_attack_muster(m_name, enemy, "alarm")' in fn
        assert '" · ".join(PackedStringArray(tips))' in fn
        assert "muster_lines" not in fn

    def test_every_chip_sends_the_command_it_always_sent(self):
        fn = _func("_marshal_row_folded")
        assert '"do:" + m_name + ", attack " + enemy_shown' in fn
        assert "Utils.COLOR_ERROR_CHIP" in fn
        chip = _func("_order_chip")
        assert '"order:" + verb + ":" + m_name' in chip
        assert 'label += " (" + str(price) + " AP)"' in chip
        assert 'Utils.bb_chip_disabled(label, "", str(spec["reason"]))' in chip   # reason = hover

    def test_a_foreign_marshal_is_not_a_link_and_wears_no_badge(self):
        fn = _func("_marshal_row_folded")
        assert "if mine:" in fn
        assert "if not mine or not (tactical is Dictionary) or tactical.is_empty():" in fn


class TestTheWidthAndTheHeight:
    def test_the_compact_view_caps_the_width(self):
        fn = _func("_fit_width")
        assert "Utils.compact_view()" in fn
        assert "_COMPACT_FRACTION" in fn and "_COMPACT_MIN_WIDTH" in fn
        assert re.search(r"const _COMPACT_FRACTION := 0\.30\b", SRC)
        assert re.search(r"const _COMPACT_MIN_WIDTH := 360\.0\b", SRC)

    def test_the_avoided_desk_clamps_only_where_it_overlaps(self):
        fit = _func("_fit_height")
        assert "_avoid_overlaps_panel()" in fit
        assert "avoid_control.get_global_rect().position.y" in fit
        beside = _func("_beside_terminal_left")
        assert "_avoid_overlaps_panel()" in beside
        assert "avoid_control.visible" in beside
        ov = _func("_avoid_overlaps_panel")
        assert "_home_left()" in ov and "rect.position.x < panel_right and rect.end.x > panel_left" in ov

    def test_the_wire_count_is_one(self):
        main = (SCRIPTS / "main.gd").read_text(encoding="utf-8")
        assert main.count("region_panel.avoid_control = bottom_left_ui") == 1

    def test_the_overlap_arithmetic(self):
        """A Python mirror of `_avoid_overlaps_panel`'s test: a full-height
        left column (32:9) stands clear of the panel; a bottom desk shares its
        columns."""
        def overlaps(rect_x, rect_end, panel_left, width):
            return rect_x < panel_left + width and rect_end > panel_left
        assert overlaps(0, 483, 12, 440) is True              # the 16:9 desk under the panel
        assert overlaps(0, 483, 1000, 440) is False           # the 32:9 column, the panel in the gap
        assert overlaps(1000, 1400, 12, 440) is False


class TestTheRulesHold:
    def test_no_value_or_collapses_to_a_bool(self):
        assert not re.search(r"(str|int|float)\([^()]*\.get\([^()]*\)[^()]* or ", SRC)

    def test_no_font_size_tags_and_no_new_hex(self):
        code = _code(SRC)
        assert "[font_size" not in code
        # the session's own functions take every colour from a Utils token
        for name in ("_marshal_row_folded", "_order_chip", "_ordinance_tag", "_march_caption",
                     "_army_corps_tip", "_avoid_overlaps_panel"):
            assert not re.search(r'"[0-9a-fA-F]{6}"', _code(_func(name))), name
        assert not re.search(r'"[0-9a-fA-F]{6}"', _code(_func("_facts_row")))

    def test_the_locked_chip_keeps_its_rule(self):
        assert "_recruit_refusal_line" not in SRC
        assert "Utils.bb_chip_disabled(" in _func("_dim")
