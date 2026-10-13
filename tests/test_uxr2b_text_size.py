"""UXR-D1 "Text size" — the pins (Pre-Deploy S9b Slice A, October 12, 2026).

On an ultra-wide the panels have room and the type is the problem; one global
Interface Scale enlarges the chrome with the text. Settings → INTERFACE now
carries a second slider, *Text size* (100–175 %), that scales the THEME's named
sizes alone — the ladder S9's diet built in `ui/main_theme.tres` (Caption 14 ·
the theme's 16 · BodyLarge 17 · Lead 18 · ScreenTitle 20 · DialogTitle /
HeadingLabel 22 · DialogTitleLarge 24 · DisplayTitle 28 · DisplayTitleLarge 30).

The done-when (`docs/DESIGN_REFINEMENT.md` §UXR, row UXR-D1): the slider moves
every text node the census sees and no panel rect; the census at Text size 1.5
and Interface Scale 1.0 reads 0 RED on the five named surfaces. Read off the
committed pair record (`tools/uxr2b_text_size_check.py` over two
`iq10_run_captures.py --physical --physical-scale 1.0` runs, one per Text
size), never off Godot. The live slider itself is driven in
`tests/test_uxr2_grips_driven.py` (TestTheTextSizeSlider).
"""
from __future__ import annotations

import json
import pathlib
import re

import pytest

from tests import _godot_scenes as G

REPO = pathlib.Path(__file__).resolve().parents[1]
PROJECT = REPO / "godot-client" / "project-sovereign"
SCRIPTS = PROJECT / "scripts"
RECORD = REPO / "docs" / "audits" / "uxr0" / "readability_text150_named_2026_10_12.json"
# The slider's top, the same pair (the regression arm: nothing clipped or off
# the screen at 175 % — it found the full-text top bar running off a 1920-px
# screen, UXR-X22).
RECORD_175 = REPO / "docs" / "audits" / "uxr0" / "readability_text175_named_2026_10_12.json"
RESOLUTIONS = ("1920x1080", "2560x1440", "3440x1440", "5120x1440", "3840x2160")
# The five named surfaces of UXR-1's done-when, by the ids the census groups on.
NAMED = {
    "tutorial": ("tutorial_card", "war_room_tutorial"),
    "dispatch": ("dispatch_boot_today", "dispatch_t20"),
    "terminal": ("war_room_boot",),
    "top bar": ("top_bar_boot",),
    "Generals": ("generals_boot",),
}


# What Text size may change, each by its own rule (SYSTEMS_REFERENCE §112.1);
# every other top-level surface keeps its rect to the half pixel.
STRIP = "TopBar/BarContainer"                       # one line of buttons
RAIL = "TopBar/NotificationArea"                    # the rail slot, under the strip
CARD = "TutorialOverlay/Card"                       # top-anchored, shrink-wrapped
WAR_HUD = "WarStatusPanel/PanelContainer"           # bottom-right, shrink-wrapped
WAR_HUD_GRIP = "WarStatusPanel/ResizeGrip"          # rides the HUD's top-left corner
TERMINAL = "BottomLeftUI"                           # bottom-left, footprint + its floor
TERMINAL_GRIP = "TerminalResizeGrip"                # rides the window's top-right corner
# How far the strip grows at 150 % (36 -> 45 px): what the rail and the tutor
# card move down by to clear it (UXR-X22).
STRIP_GROWTH_150 = 9.0
# The command window's width floor at 150 %: its input row (569 logical px,
# measured by the driven harness — the command line holds 8 em, UXR-X21)
# plus the panel's chrome (under 70).
TERMINAL_FLOOR_150 = 569.0 + 70.0


def _read(p: pathlib.Path) -> str:
    return p.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def record() -> dict:
    assert RECORD.is_file(), f"the committed record is missing: {RECORD}"
    return json.loads(RECORD.read_text(encoding="utf-8"))


def _readings(record: dict):
    for ids in NAMED.values():
        for sid in ids:
            for res, r in record["surfaces"][sid]["readings"].items():
                yield sid, res, r


class TestTheDoneWhen:
    def test_the_record_is_the_pair_at_one_and_a_half_on_scale_one(self, record):
        assert record["factor"] == pytest.approx(1.5)
        assert record["physical_scale"] == "1.0"
        for ids in NAMED.values():
            for sid in ids:
                assert set(record["surfaces"][sid]["readings"]) == set(RESOLUTIONS), sid

    @pytest.mark.parametrize("surface", sorted(NAMED))
    def test_zero_red_on_the_named_surface(self, record, surface):
        for sid in NAMED[surface]:
            for res, r in record["surfaces"][sid]["readings"].items():
                assert r["ok"], (sid, res)
                assert r["counts"]["red"] == 0 and r["counts"]["p1"] == 0, (sid, res, r["flagged"][:3])

    def test_the_slider_moves_every_text_node_the_census_sees(self, record):
        for sid, res, r in _readings(record):
            c = r["counts"]
            assert c["paired"] > 0 and c["paired"] >= 0.8 * c["rows"], (sid, res, c)
            assert c["unscaled"] == 0 and r["unscaled"] == [], (sid, res, r["unscaled"][:4])
            assert c["scaled"] == c["paired"], (sid, res, c)

    def test_and_no_panel_rect(self, record):
        """Every top-level surface keeps its rect, but for the ones whose size
        IS their text, each held to its rule: the top bar's strip grows by its
        line, and the rail slot and the tutor card move down by exactly that
        growth to clear it (UXR-X22); the tutor card and the war HUD
        shrink-wrap their content (their width and their anchored edge fixed);
        the command window keeps its left and bottom edges and outgrows its
        footprint only up to its input row's floor (its stats line wraps —
        UXR-X21). A clamped screen (the dispatch, the Generals) never moves."""
        def same(a, b, *idx):
            return all(abs(float(a[i]) - float(b[i])) <= 0.51 for i in idx)
        for sid, res, r in _readings(record):
            assert r["surfaces_seen"] > 0, (sid, res)
            if sid.startswith(("dispatch", "generals")):
                assert r["surfaces_moved"] == [], (sid, res, r["surfaces_moved"])
                continue
            for m in r["surfaces_moved"]:
                path, a, b = m["path"], m["base"], m["scaled"]
                bottom_a, bottom_b = a[1] + a[3], b[1] + b[3]
                if path.endswith(STRIP):
                    assert same(a, b, 0, 1, 2), (sid, res, m)
                    assert abs((b[3] - a[3]) - STRIP_GROWTH_150) <= 0.51, (sid, res, m)
                elif path.endswith(RAIL):
                    assert same(a, b, 0, 2, 3), (sid, res, m)
                    assert abs((b[1] - a[1]) - STRIP_GROWTH_150) <= 0.51, (sid, res, m)
                elif path.endswith(CARD):
                    assert same(a, b, 0, 2) and b[3] > a[3], (sid, res, m)
                    assert abs((b[1] - a[1]) - STRIP_GROWTH_150) <= 0.51, (sid, res, m)
                elif path.endswith(WAR_HUD):
                    assert same(a, b, 0, 2) and abs(bottom_a - bottom_b) <= 0.51 and b[3] > a[3], (sid, res, m)
                elif path.endswith(WAR_HUD_GRIP):
                    assert same(a, b, 0), (sid, res, m)
                elif path.endswith(TERMINAL):
                    assert same(a, b, 0) and abs(bottom_a - bottom_b) <= 0.51, (sid, res, m)
                    assert b[2] <= max(a[2], TERMINAL_FLOOR_150) + 0.51, (sid, res, m)
                elif path.endswith(TERMINAL_GRIP):
                    pass  # rides the window's corner, checked above
                else:
                    raise AssertionError(("a surface Text size may not move", sid, res, m))

    def test_nothing_clipped_and_no_button_off_screen(self, record):
        for sid, res, r in _readings(record):
            assert r["clipped_text"] == 0, (sid, res)
            assert r["buttons_offscreen"] == 0, (sid, res)


class TestTheTop:
    def test_at_one_seventy_five_nothing_clips_and_nothing_leaves_the_screen(self):
        rec = json.loads(RECORD_175.read_text(encoding="utf-8"))
        assert rec["factor"] == pytest.approx(1.75)
        for ids in NAMED.values():
            for sid in ids:
                readings = rec["surfaces"][sid]["readings"]
                assert set(readings) == set(RESOLUTIONS), sid
                for res, r in readings.items():
                    assert r["ok"], (sid, res)
                    assert r["counts"]["red"] == 0 and r["counts"]["p1"] == 0, (sid, res)
                    assert r["clipped_text"] == 0 and r["buttons_offscreen"] == 0, (sid, res)
                    assert r["counts"]["unscaled"] == 0, (sid, res, r["unscaled"][:3])


class TestTheStore:
    def test_the_range_never_goes_under_the_theme(self):
        src = _read(SCRIPTS / "ui_settings.gd")
        assert "const DEFAULT_TEXT_SIZE := 1.0" in src
        assert "const MIN_TEXT_SIZE := 1.0" in src
        assert "const MAX_TEXT_SIZE := 1.75" in src
        assert "const TEXT_SIZE_STEP := 0.05" in src
        body = G.func_body(src, "get_text_size")
        assert '"display", "text_size"' in body and "MIN_TEXT_SIZE, MAX_TEXT_SIZE" in body
        body = G.func_body(src, "set_text_size")
        assert "clampf(" in body and "MIN_TEXT_SIZE, MAX_TEXT_SIZE" in body

    def test_reset_layout_returns_the_text_to_one_hundred(self):
        src = _read(SCRIPTS / "ui_settings.gd")
        assert "set_text_size(DEFAULT_TEXT_SIZE)" in G.func_body(src, "reset_layout")


class TestTheThemeSwap:
    def test_it_scales_every_named_size_from_the_authored_ones_in_one_merge(self):
        body = G.func_body(_read(SCRIPTS / "utils.gd"), "apply_text_size")
        code = G.code_lines(body)
        # the authored sizes, captured once, are the base — never the live ones
        assert "if _text_size_bases.is_empty():" in code
        assert "get_font_size_type_list()" in code and "get_font_size_list(theme_type)" in code
        assert "theme.default_font_size" in code
        # one merge, so the controls re-theme once
        assert code.count("theme.merge_with(") == 1
        assert "set_font_size(" not in code.replace("scaled.set_font_size(", "")
        # 1.0 at boot is a no-op
        assert "if is_equal_approx(factor, _text_size_applied):" in code

    def test_the_raw_overrides_do_not_ride_it(self):
        # the swap writes the THEME; a node's own override is never touched
        code = G.code_lines(G.func_body(_read(SCRIPTS / "utils.gd"), "apply_text_size"))
        assert "add_theme_font_size_override" not in code

    def test_both_boots_apply_the_stored_size(self):
        for name in ("main.gd", "main_menu.gd"):
            src = G.code_lines(_read(SCRIPTS / name))
            assert re.search(r"Utils\.apply_body_font\(\)\s*\n\s*Utils\.apply_text_size\(\)", src), name


class TestTheSlider:
    def test_settings_carries_it_with_the_scale_sliders_contract(self):
        src = _read(SCRIPTS / "settings_panel.gd")
        code = G.code_lines(src)
        assert 'signal text_size_changed(value: float, persist: bool)' in src
        assert '_text_slider.name = "TextSizeSlider"' in code
        assert "_text_slider.min_value = UiSettings.MIN_TEXT_SIZE" in code
        assert "_text_slider.max_value = UiSettings.MAX_TEXT_SIZE" in code
        # live on every step, persisted when the drag ends (or at once on a click)
        assert "_apply_text_size(value, not _text_dragging)" in code
        assert "_apply_text_size(_text_slider.value, true)" in code
        body = G.func_body(src, "_apply_text_size")
        assert "UiSettings.set_text_size(value)" in body and "Utils.apply_text_size(value)" in body

    def test_the_hosts_put_every_open_surface_on_the_refit_road(self):
        pause = G.code_lines(_read(SCRIPTS / "pause_menu.gd"))
        assert "_settings_panel.text_size_changed.connect(" in pause
        main = _read(SCRIPTS / "main.gd")
        assert "pause_menu.text_size_changed.connect(_on_text_size_changed)" in G.code_lines(main)
        assert 'call_deferred("_on_root_resized")' in G.func_body(main, "_on_text_size_changed")
        menu = G.code_lines(_read(SCRIPTS / "main_menu.gd"))
        assert "_settings_panel.text_size_changed.connect(" in menu
        assert "_refit_open_panels.call_deferred()" in menu

    def test_reset_layout_reapplies_the_theme(self):
        body = G.func_body(_read(SCRIPTS / "settings_panel.gd"), "_on_reset_layout")
        assert "UiSettings.reset_layout()" in body and "Utils.apply_text_size()" in body
        assert "Utils.apply_text_size()" in G.func_body(_read(SCRIPTS / "main.gd"), "_on_layout_reset")


class TestTheInstrument:
    def test_the_capture_shoots_at_a_text_size(self):
        runner = _read(REPO / "tools" / "iq10_run_captures.py")
        assert '"--text-size"' in runner and '"text_size": text_size' in runner
        harness = _read(REPO / "tools" / "iq10_surface_screenshot.gd")
        assert 'UiSettings._cfg.set_value("display", "text_size", text_size)' in harness
        assert 'utils_class.call("apply_text_size")' in harness
        assert 'frame["surfaces"] = _surface_rects()' in harness


class TestTheStripAndTheFloor:
    """UXR-X22: the top bar's one line grows with the text and everything that
    clears the bar clears its DRAWN height; UXR-X21: the command window's
    stats line wraps, so its width floor is its input row."""

    def test_the_bar_publishes_its_drawn_height_and_rethinks_compact(self):
        src = _read(SCRIPTS / "top_bar.gd")
        assert "signal bar_height_changed" in src
        assert "bar.resized.connect(_on_bar_resized)" in G.code_lines(src)
        body = G.func_body(src, "_on_bar_resized")
        assert body.index("_fit_bar()") < body.index("Utils.set_top_bar_drawn(bar.size.y)")
        assert "bar_height_changed.emit()" in body
        assert "COMPACT_BELOW_PX * Utils.text_size_factor()" in G.func_body(src, "_fit_bar")

    def test_everything_that_clears_the_bar_clears_its_growth(self):
        utils = _read(SCRIPTS / "utils.gd")
        assert "view.y - 88.0 - 2.0 * top_bar_growth()" in G.func_body(utils, "clamp_centered_panel")
        assert "TOP_BAR_HEIGHT + top_bar_growth() + HUD_MARGIN" in G.func_body(utils, "clamp_anchored_panel")
        assert "Utils.TOP_BAR_HEIGHT + RAIL_GAP + Utils.top_bar_growth()" in G.func_body(
            _read(SCRIPTS / "top_bar.gd"), "_fit_rail")
        tutor = G.func_body(_read(SCRIPTS / "tutorial_overlay.gd"), "_card_placement")
        assert tutor.count("CARD_TOP + Utils.top_bar_growth()") == 2
        region = _read(SCRIPTS / "region_panel.gd")
        assert "panel_container.offset_top = _PANEL_TOP + Utils.top_bar_growth()" in G.func_body(region, "_fit_width")
        assert "_PANEL_TOP - Utils.top_bar_growth()" in G.func_body(region, "_fit_height")
        main = _read(SCRIPTS / "main.gd")
        assert "TOP_BAR_RESERVED_PX - Utils.top_bar_growth()" in G.func_body(main, "_relayout_terminal")
        assert "top_bar.bar_height_changed.connect(_on_bar_height_changed)" in G.code_lines(main)
        body = G.func_body(main, "_on_bar_height_changed")
        assert "_on_root_resized()" in body and "_on_viewport_changed" in body and "_on_viewport_resized" in body

    def test_the_command_windows_stats_line_wraps(self):
        scene = G.read(PROJECT / "scenes" / "main.tscn")
        assert ('[node name="StatusSection" type="HFlowContainer" '
                'parent="BottomLeftUI/MainMargin/MainLayout/Header/HeaderMargin/HeaderContent"]') in scene

    def test_the_command_line_holds_eight_em_at_any_size(self):
        """The wrap exposed the LineEdit's default 4-em floor (~70 px on an
        800-px screen, ~100 px at 150 % on 1080p): the primary input holds
        8 em, a theme constant that grows with the text."""
        block = G.node_block(G.read(PROJECT / "scenes" / "main.tscn"), "CommandInput")
        assert "theme_override_constants/minimum_character_width = 8" in block
