"""Session UI-6 (November 13, 2026) - the war detail (frame F25, scored 6).

The readers: "the dimmed HUD behind is cluttered, the command panel pokes
through", "cut the paragraph text under the table", "widen the table", "show
the full table". The war detail, Folded:

- the backdrop behind the window is near-opaque (0.85) and full-screen;
- the score table spans the window (its width is measured after the window has
  its rect, and the page is drawn again once the layout settles);
- the holdings paragraph is a GROUND block - `We hold N of theirs` / `They
  hold N of ours`, a count badge and up to six province chips then `+N`, the
  full names on hover, `With:` as flag chips - read from an ADDITIVE backend
  sidecar (`war_title.ground`, carried on the war row as `war_ground`) beside
  the sentence, which is unchanged;
- the tail is figures: a strip of tiles (Duration, Enemy exhaustion, the
  Objective meter), the Standing table, the Recent battles table; the prose
  stands behind ONE `more` note.

On the page the old tail prints exactly as before (the early return sits
between the two paths). Source pins (GDScript is invisible to pytest) plus a
real test of the backend sidecar.
"""

from __future__ import annotations

import contextlib
import io
import json
import re
from pathlib import Path

import pytest

from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "godot-client" / "project-sovereign" / "scripts" / "war_detail_popup.gd"
BOARDS = REPO / "tests" / "fixtures" / "pc_boards"


def _src() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def _func(src: str, name: str) -> str:
    m = re.search(r"^func " + re.escape(name) + r"\(", src, re.M)
    assert m, name
    nxt = re.search(r"^func |^static func ", src[m.end():], re.M)
    return src[m.start(): m.end() + (nxt.start() if nxt else len(src))]


def _board(name: str) -> WorldState:
    with contextlib.redirect_stdout(io.StringIO()):
        world = WorldState.from_dict(
            json.loads((BOARDS / name).read_text(encoding="utf-8"))["world_state"])
        while world.dialogue_manager.peek() is not None:
            world.dialogue_manager.pop()
    return world


# --- backend: the ground sidecar --------------------------------------------

class TestGroundSidecar:
    def test_the_sidecar_names_what_each_side_holds(self):
        from backend.game_logic.war_title import war_title
        rec = war_title(_board("turn6_vienna_held.json"), "war_1")
        ground = rec["ground"]
        taken = ground["theirs_held_by_us"]
        assert [r["province"] for r in taken] == rec["theirs_we_hold"] == ["Bohemia", "Tyrol", "Vienna"]
        assert all(r["owner"] == "Austria" and r["holder"] == "France" for r in taken)
        assert all(r["owner_display"] and r["holder_display"] for r in taken)
        assert ground["ours_held_by_them"] == []

    def test_every_count_is_an_int_and_matches_the_rows(self):
        from backend.game_logic.war_title import war_title
        rec = war_title(_board("turn6_vienna_held.json"), "war_1")
        g = rec["ground"]
        assert type(g["theirs_held_count"]) is int and g["theirs_held_count"] == len(g["theirs_held_by_us"]) == 3
        assert type(g["ours_held_count"]) is int and g["ours_held_count"] == 0

    def test_the_sentence_is_unchanged(self):
        from backend.game_logic.war_title import war_title
        rec = war_title(_board("turn6_vienna_held.json"), "war_1")
        assert rec["line"] == "The War for Bohemia: France holds Bohemia, Tyrol and Vienna of Austria's."

    def test_a_wound_lists_the_holders(self):
        from backend.game_logic.war_title import war_title
        for name in ("turn6_copy.json",):
            rec = war_title(_board(name), "war_1")
            g = rec["ground"]
            assert g["ours_held_count"] == len(g["ours_held_by_them"]) == len(rec["ours_they_hold"])
            assert g["theirs_held_count"] == len(rec["theirs_we_hold"])
            for row in g["ours_held_by_them"]:
                assert row["owner"] == "France" and row["holder"] != "France"

    def test_the_war_row_carries_the_ground(self):
        from backend.game_logic.war_status import _title_block
        world = _board("turn6_vienna_held.json")
        block = _title_block(world, "war_1")
        assert block["war_ground"]["theirs_held_count"] == 3
        assert block["war_title_line"].startswith("The War for Bohemia")
        json.dumps(block)  # serializable


# --- client source pins ------------------------------------------------------

class TestWarDetailClient:
    def test_the_backdrop_is_near_opaque_and_full_screen(self):
        src = _src()
        assert "const BACKDROP_ALPHA := 0.85" in src
        ready = _func(src, "_ready")
        assert "Color(0, 0, 0, BACKDROP_ALPHA)" in ready
        assert "backdrop.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)" in ready

    def test_the_table_spans_the_window_and_is_drawn_again_after_layout(self):
        src = _src()
        assert "_table_px())" in _func(src, "_render_war_detail")
        px = _func(src, "_table_px")
        assert "content_label.size.x >= 280.0" in px and "panel.offset_right - panel.offset_left" in px
        show = _func(src, "show_war")
        assert show.index("refit()") < show.index("_rerender_local.call_deferred()")
        # the lead's frame reading (Nov 13): the deferred redraw still ran before
        # the label's layout (the breakdown at ~60 % of the page) — the label's
        # own resize redraws the page when it settles at another width
        assert "content_label.resized.connect(_on_content_resized)" in _func(src, "_ready")
        assert "_table_px_used = px" in px
        resized = _func(src, "_on_content_resized")
        assert "> 16.0" in resized and 'call_deferred("_rerender_local")' in resized

    def test_the_ground_block_leads_the_tier_and_stays_inside_tier_bb(self):
        body = _func(_src(), "_render_war_detail")
        assert "var tier_bb: String = _ground_block(w) + bbcode" in body
        # the PC-F46 order and the HUD builder's literal both stand
        assert body.index('"Settlement Tier: [color="') < body.index("# Breakdown")
        assert "bbcode = tier_bb + bbcode + prose" in body

    def test_the_ground_block_is_folded_only_and_chips_with_hovers(self):
        src = _src()
        block = _func(src, "_ground_block")
        assert "if not Utils.explanations_folded():\n\t\treturn \"\"" in block
        assert 'w.get("war_ground", null)' in block
        assert '"We hold", "of theirs"' in block and '"They hold", "of ours"' in block
        assert "With:" in block and "Utils.bb_flag(" in block
        row = _func(src, "_ground_row")
        assert "Utils.bb_tag(" in row and "Utils.bb_hint(" in row
        assert "GROUND_CHIPS_COMPACT if Utils.compact_view() else GROUND_CHIPS" in row
        assert "const GROUND_CHIPS := 6" in src
        assert '"+" + str(rest.size())' in row
        assert "int(ground.get(\"theirs_held_count\", 0))" in block

    def test_the_on_the_page_path_is_reached_only_when_not_folded(self):
        body = _func(_src(), "_render_war_detail")
        early = body.index("if Utils.explanations_folded():\n\t\tcontent_label.text = ")
        assert "return" in body[early: early + 200]
        # everything the page printed stays below the early return
        for old in ('"Enemy War Exhaustion: [color="', '"Duration: " + str(duration)',
                    '"Casus belli: " + stated_reason', 'for ln in Utils.standing_lines(w):',
                    '"\\n[color=" + COLOR_HEADER + "]Recent Battles[/color]\\n"',
                    'bbcode += "Their fleet: "'):
            assert body.index(old) > early, old

    def test_the_tail_is_figures_and_the_prose_is_one_note(self):
        src = _src()
        tail = _func(src, "_figures_tail")
        assert "_tiles(w)" in tail and "_standing_table(w)" in tail and "_battles_table(w)" in tail
        assert tail.count("Utils.bb_note(") == 1 and '"war.account." + slug' in tail
        tiles = _func(src, "_tiles")
        assert '["Duration", "Enemy exhaustion", "Objective"]' in tiles
        assert "we_color = COLOR_RED" in tiles and "we_color = COLOR_AMBER" in tiles
        assert "we_int >= 80" in tiles and "we_int >= 40" in tiles
        # the purpose sentence printed beside its meter (EP-F1: one sentence on
        # every surface — "the homeland — 28 of 28 provinces held"), not "28 of 28 held"
        assert 'Utils.bb_meter(n, total, 90, 8) + " " + str(parts.get("target", ""))' in tiles
        assert '" held"' not in tiles
        assert '["Court", "Side", "Standing", "Share"]' in _func(src, "_standing_table")
        assert '["Result", "Place", "Turn"]' in _func(src, "_battles_table")

    def test_no_word_is_lost_the_note_holds_every_sentence(self):
        body = _func(_src(), "_account_body")
        for field in ("war_title_line", "war_roster_display", "objective_hint", "stated_reason",
                      "exhaustion_terms", "naval_line"):
            assert field in body, field
        assert "Casus belli: " in body and "Enemy Objective: " in body and "Their fleet: " in body
        assert "lead_line.strip_edges()" in body

    def test_the_house_rules(self):
        src = _src()
        new = "".join(_func(src, f) for f in (
            "_ground_row", "_ground_block", "_objective_parts", "_tiles", "_standing_table",
            "_battles_table", "_account_body", "_figures_tail", "_table_px"))
        assert "font_size" not in new
        assert not re.search(r"str\([^)]*\bor\b", new)
        assert not re.search(r"#[0-9a-fA-F]{6}\b", new)  # no new hex literals
