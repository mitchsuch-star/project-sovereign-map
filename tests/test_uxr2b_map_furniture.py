"""UXR-X4 "the map's own furniture follows the scale" — the pins (Pre-Deploy
S9b Slice C, October 12, 2026), with UXR-X26 (the census over-read the map
tier) and UXR-X27 (the sail counts drew at ~2 px).

The marshals' names and stacks, the fogged "?" chips, the garrison chips and
the sail counts are world-space Labels inside the map's SubViewport: sized by
the camera alone, they read 6.75-9 px at the whole-map view on every monitor.
The user's ruling: a SCREEN-SPACE FLOOR — the province names' own rule. The
authored sizes (a named table) hold until the smallest would read under 16
logical px on screen; from there every one, chips with their text, grows by
one factor, times the Interface Scale. Zoomed in, the furniture is world-space
as it always was.

The completion (`BUG_FIXES.md` UXR-X4): the furniture's size carries a term in
`content_scale_factor`; the five raw sizes leave `map_renderer_base.gd`'s
exemption (the diet's census, `tests/test_uxr2_override_diet.py`, lowered to
11; the floor sweep's exemption retired, `tests/test_uxr1_scale_fix.py`); and
the physical census's `map_small` reads 0 at the derived scale. Read off the
committed records — the BEFORE shot from the pristine pre-S9b worktree
(`c8e65997`) through the FIXED instrument, the AFTER on this tree — never off
Godot.
"""
from __future__ import annotations

import json
import pathlib
import re

import pytest

from tests import _godot_scenes as G

REPO = pathlib.Path(__file__).resolve().parents[1]
PROJECT = REPO / "godot-client" / "project-sovereign"
RECORDS = REPO / "docs" / "audits" / "uxr0"
BEFORE = RECORDS / "readability_map_before_2026_10_12.json"
AFTER = RECORDS / "readability_map_after_2026_10_12.json"
SURFACES = ("war_room_boot", "war_room_tutorial", "war_room_pause_settings")
RESOLUTIONS = ("1920x1080", "2560x1440", "3440x1440", "5120x1440", "3840x2160")
FLOOR = 16.0     # BODY_RED: the floor the map tier is counted against (map_small)


def _load(path: pathlib.Path) -> dict:
    assert path.is_file(), f"the committed record is missing: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def before() -> dict:
    return _load(BEFORE)


@pytest.fixture(scope="module")
def after() -> dict:
    return _load(AFTER)


def _readings(rec: dict):
    for sid in SURFACES:
        for key, r in rec["surfaces"][sid]["readings"].items():
            yield sid, key, r


class TestTheRecords:
    def test_both_cover_the_war_room_at_every_resolution_at_the_derived_scale(self, before, after):
        for rec in (before, after):
            assert rec["physical_scale"] == "auto"
            for sid in SURFACES:
                keys = set(rec["surfaces"][sid]["readings"])
                for res in RESOLUTIONS:
                    assert any(k.startswith(res + "@") for k in keys), (sid, res)

    def test_the_before_is_the_pristine_client(self, before):
        assert before["client_commit"] == "c8e65997"


class TestTheDoneWhen:
    def test_the_before_was_small_everywhere(self, before):
        """Through the FIXED instrument the pre-S9b map read small at every
        resolution — every label but a few at 4K (the old double count had
        hidden most of it there)."""
        for sid, key, r in _readings(before):
            assert r["counts"]["map"] > 0, (sid, key)
            assert r["counts"]["map_small"] >= r["counts"]["map"] - 3, (sid, key, r["counts"])

    def test_map_small_reads_zero_at_the_derived_scale(self, after):
        for sid, key, r in _readings(after):
            assert r["ok"], (sid, key)
            assert r["counts"]["map"] > 0, (sid, key)
            assert r["counts"]["map_small"] == 0, (sid, key, r["counts"],
                                                   [m for m in r["map_rows"] if m["em"] < FLOOR][:4])

    def test_nothing_else_moved_on_the_floor(self, after):
        for sid, key, r in _readings(after):
            assert r["counts"]["red"] == 0 and r["counts"]["p1"] == 0, (sid, key, r["flagged"][:3])


class TestTheSailCounts:
    """UXR-X27: the count was a CHILD of the ship standee, which scales itself
    by 64 x 0.85 / 256 = 0.21 — it drew at ~2 px on the user's panel."""

    def test_the_before_drew_them_at_two_pixels(self, before):
        rows = before["surfaces"]["war_room_boot"]["readings"]["5120x1440@1.40"]["map_rows"]
        sails = [m for m in rows if m["path"].startswith("SailCount")]
        assert sails and all(m["em"] < 3.0 for m in sails), sails[:3]

    def test_the_after_reads_them_at_the_floor(self, after):
        for key, r in after["surfaces"]["war_room_boot"]["readings"].items():
            sails = [m for m in r["map_rows"] if m["path"].startswith("SailCount")]
            assert sails, key
            assert all(m["em"] >= FLOOR for m in sails), (key, sails[:3])

    def test_the_count_is_the_pieces_sibling(self):
        src = G.read(PROJECT / "scenes" / "map_renderer_base.gd")
        body = G.func_body(src, "_update_fleet_pieces")
        assert "pieces_layer.add_child(sail)" in body and "piece.add_child(sail)" not in body
        assert '_style_furniture(sail, "sail")' in body
        assert "gone_sail.queue_free()" in body


class TestTheScaleTerm:
    def test_one_named_table_and_no_raw_size(self):
        src = G.read(PROJECT / "scenes" / "map_renderer_base.gd")
        code = G.code_lines(src)
        assert ('const FURNITURE_PX := {"region": 14, "name": 11, "fog_chip": 12, '
                '"garrison": 10, "sail": 11}') in code
        assert "const FURNITURE_FLOOR_PX := 16.0" in code
        assert "add_theme_font_size_override" not in code

    def test_the_floor_is_screen_space_times_the_interface_scale(self):
        src = G.read(PROJECT / "scenes" / "map_renderer_base.gd")
        body = G.func_body(src, "_wanted_furniture_scale")
        assert ("FURNITURE_FLOOR_PX * _target_content_scale() / (FURNITURE_SMALLEST_PX * zoom)"
                in body)
        assert "maxf(s, 1.0)" in body     # zoomed in, world-space as ever

    def test_every_zoom_and_scale_change_reaches_it(self):
        src = G.read(PROJECT / "scenes" / "map_renderer_base.gd")
        assert "_check_furniture_scale()" in G.func_body(src, "_set_camera_zoom_level")
        assert "_check_furniture_scale()" in G.func_body(src, "refresh_viewport_scale")
        assert "_apply_pending_furniture_scale()" in G.func_body(src, "_process")
        apply = G.func_body(src, "_apply_pending_furniture_scale")
        # once, when the zoom's ease is over — not a rebuild a frame
        assert "zoom_tween.is_running()" in apply
        assert "_rebuild_dynamic_nodes()" in apply and "_layout_sail_labels()" in apply
        assert G.func_body(src, "_rebuild_dynamic_nodes").count("_sync_furniture_scale()") == 1

    def test_each_kind_styles_through_its_theme(self):
        src = G.code_lines(G.read(PROJECT / "scenes" / "map_renderer_base.gd"))
        for kind in ("name", "fog_chip", "garrison", "sail", "region"):
            assert re.search(r'_style_furniture\(\w+, "%s"\)' % kind, src), kind
        assert "label.theme = _furniture_theme(kind)" in src


class TestTheTooltip:
    """The hover tooltip's draw_string text (no census sees a draw call): the
    body at Caption 14 and the title at Lead 18, times Text size, where they
    were raw 11 / 14 px."""

    def test_no_tooltip_size_under_the_caption_floor(self):
        src = G.read(PROJECT / "scenes" / "map_tooltip_layer.gd")
        assert "const BODY_PX := 14" in src and "const TITLE_PX := 18" in src
        assert "Utils.text_px(TITLE_PX if design_size >= TITLE_DESIGN_PX else BODY_PX)" in src
        draw = G.func_body(src, "_draw")
        assert "line_px(design_size)" in draw
        assert "width * type_ratio()" in G.func_body(src, "_measure_tooltip")
        assert "font.get_height(px)" in G.func_body(src, "_line_height")

    def test_the_renderers_dead_copies_are_gone(self):
        src = G.read(PROJECT / "scenes" / "map_renderer_base.gd")
        for dead in ("func _measure_tooltip(", "func _tooltip_line_height(", "func _clamp_tooltip_pos("):
            assert dead not in src, dead


class TestTheInstrument:
    """UXR-X26: a SubViewport node's canvas transform is in the SubViewport's
    own pixels; the map renders its SubViewport at physical resolution, so the
    census's x content_scale_factor counted the scale twice."""

    def test_the_census_reads_the_display_not_the_window(self):
        src = G.read(REPO / "tools" / "iq10_surface_screenshot.gd")
        body = G.func_body(src, "_add_text_metrics")
        assert "view_mult = _subviewport_display_scale(sv)" in body
        disp = G.func_body(src, "_subviewport_display_scale")
        assert "shown.get_global_rect().size.x * csf / float(sv.size.x)" in disp
