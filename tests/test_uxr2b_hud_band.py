"""UXR-D3 "HUD width: Full · Centred" + the `[− ⌂ +]` map controls — the pins
(Pre-Deploy S9b Slice B, October 12, 2026).

On the user's 5120×1440 panel the HUD sat at the corners of a 3657-px logical
viewport: the command window bottom-left, the war HUD bottom-right, the top
bar's two clusters 2,500 px apart. Settings → DISPLAY now carries *HUD width:
Full · Centred*; Centred confines the command window (and its restore
button), the top bar's two clusters, the notice rail, the war HUD, the region
panel and the map controls to a central band 2560 logical px wide; the map
stays full-bleed. The map had no on-screen zoom at all, so ⌂ Fit Europe rides
in a `[− ⌂ +]` cluster at the band's bottom-centre (the user's ruling).

The done-when (`docs/DESIGN_REFINEMENT.md` §UXR, row UXR-D3): the driven grip
harness at 5120×1440 with Centred reads every HUD rect inside the band, and
the layout-law census still passes (`tests/test_uxr2_layout_law.py`, unchanged
and green). DRIVEN here: `tools/uxr2_grip_harness.gd` in band mode, the real
`main.tscn` behind an API stub in a real 5120×1440 window parked past the
desktop, Interface Scale 1.4 (the panel's derived scale), once Centred and
once Full. SKIPS when the Godot engine is absent (a skip is not a pass).
"""
from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess

import pytest

from tests import _godot_scenes as G

_REPO = pathlib.Path(__file__).resolve().parents[1]
_PROJECT = _REPO / "godot-client" / "project-sovereign"
_SCRIPTS = _PROJECT / "scripts"
_HARNESS = _REPO / "tools" / "uxr2_grip_harness.gd"
# Every HUD surface the band confines (the strip itself stays full-bleed).
IN_BAND = ("terminal", "restore_button", "screen_buttons", "right_section", "rail_slot",
           "war_hud", "region_panel", "map_controls")

_CANDIDATES = [
    os.environ.get("GODOT_BIN", ""),
    r"C:\Users\User\Downloads\Godot_v4.4.1-stable_win64.exe"
    r"\Godot_v4.4.1-stable_win64.exe",
    "godot",
    "godot4",
]


def _engine():
    for candidate in _CANDIDATES:
        if not candidate:
            continue
        if os.path.sep in candidate or "/" in candidate:
            if pathlib.Path(candidate).is_file():
                return candidate
            continue
        found = shutil.which(candidate)
        if found:
            return found
    return None


def _drive(tmp_path_factory, hud: str) -> dict:
    engine = _engine()
    if engine is None:
        pytest.skip("Godot engine not on this machine — the driven pins skip, "
                    "and a skip is not a pass")
    out = tmp_path_factory.mktemp("uxr2b_band") / f"band_{hud}.json"
    env = dict(os.environ, UXR2_OUT=str(out), UXR2_MODE="band", UXR2_RES="5120x1440",
               UXR2_SCALE="1.4", UXR2_HUD=hud, SOVEREIGN_PORT="8993")
    proc = subprocess.run(
        [engine, "--audio-driver", "Dummy", "--windowed", "--resolution", "5120x1440",
         "--position", "5200,20", "--path", str(_PROJECT), "--script", str(_HARNESS)],
        capture_output=True, text=True, timeout=300, env=env, cwd=str(_PROJECT),
        stdin=subprocess.DEVNULL)
    if not out.is_file():
        pytest.fail(f"the harness wrote nothing (exit {proc.returncode}):\n"
                    f"{proc.stdout[-3000:]}\n{proc.stderr[-3000:]}")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data.get("fatal") == "", data.get("fatal")
    assert "band" in data, data.keys()
    assert data["viewport"][0] >= 3600, ("the harness did not get its 5120x1440 window at 1.4",
                                         data["viewport"])
    return data["band"]


@pytest.fixture(scope="module")
def centred(tmp_path_factory) -> dict:
    return _drive(tmp_path_factory, "centred")


@pytest.fixture(scope="module")
def full(tmp_path_factory) -> dict:
    return _drive(tmp_path_factory, "full")


class TestTheDoneWhen:
    def test_the_band_is_2560_about_the_centre_of_the_users_panel(self, centred):
        vx = centred["view"][0]
        left, right = centred["band"]
        assert centred["hud_width"] == "centred"
        assert right - left == pytest.approx(2560.0)
        assert abs((left + right) / 2.0 - vx / 2.0) <= 1.0, (left, right, vx)

    @pytest.mark.parametrize("surface", IN_BAND)
    def test_every_hud_rect_is_inside_the_band(self, centred, surface):
        left, right = centred["band"]
        r = centred["rects"][surface]
        assert r, f"{surface} was not on screen"
        assert r[0] >= left - 0.5 and r[2] <= right + 0.5, (surface, r, (left, right))

    def test_the_strip_stays_full_bleed(self, centred):
        r = centred["rects"]["bar_strip"]
        assert r[0] <= 0.5 and r[2] >= centred["view"][0] - 0.5, r

    def test_the_map_controls_sit_at_the_bands_bottom_centre(self, centred):
        left, right = centred["band"]
        r = centred["rects"]["map_controls"]
        assert abs((r[0] + r[2]) / 2.0 - (left + right) / 2.0) <= 1.0, r
        assert centred["view"][1] - r[3] <= 12.0, r


class TestFullIsWhatItWas:
    """At Full every surface sits where S9 left it: the band is the viewport."""

    def test_full_is_the_whole_viewport(self, full):
        assert full["hud_width"] == "full"
        assert full["band"] == [0.0, full["view"][0]]

    def test_the_hud_keeps_its_edges(self, full):
        vx = full["view"][0]
        rects = full["rects"]
        assert rects["terminal"][0] == pytest.approx(10.0)          # TERMINAL_ANCHOR_LEFT
        assert rects["restore_button"][0] == pytest.approx(10.0)
        assert rects["region_panel"][0] == pytest.approx(12.0)      # _PANEL_LEFT
        assert rects["screen_buttons"][0] == pytest.approx(8.0)     # the strip's margin
        assert rects["rail_slot"][2] == pytest.approx(vx - 14.0)    # RAIL_RIGHT_INSET
        assert rects["war_hud"][2] == pytest.approx(vx - 8.0)       # EDGE_MARGIN


class TestFitEurope:
    def test_the_chip_fits_europe_even_mid_zoom(self, centred):
        """+ three times, then ⌂ while the zoom is still easing in: the fit
        lands (a live zoom tween used to land after it and undo it)."""
        assert centred["fit_button"] is True     # it never takes the command line's focus
        assert centred["zoom_in"] > centred["zoom_fit"] + 1e-3, centred
        assert centred["zoom_after_fit"] == pytest.approx(centred["zoom_fit"], abs=1e-4)


class TestTheSources:
    def test_the_setting_is_a_closed_list_with_full_as_default(self):
        src = G.read(_SCRIPTS / "ui_settings.gd")
        assert 'const HUD_WIDTHS := ["full", "centred"]' in src
        assert 'const DEFAULT_HUD_WIDTH := "full"' in src
        assert "const HUD_BAND_WIDTH := 2560.0" in src
        assert "set_hud_width(DEFAULT_HUD_WIDTH)" in G.func_body(src, "reset_layout")

    def test_one_band_and_every_hud_surface_measures_it(self):
        utils = G.read(_SCRIPTS / "utils.gd")
        # UXR-D4 (Pre-Deploy S12b): the band's own rule is `hud_band_full`;
        # `hud_band` is it minus the Side Desk's dock (0 with none pinned).
        full = G.func_body(utils, "hud_band_full")
        assert 'UiSettings.get_hud_width() == "centred"' in full
        assert "UiSettings.HUD_BAND_WIDTH + 2.0 * HUD_MARGIN" in full
        band = G.func_body(utils, "hud_band")
        assert "var band := hud_band_full(view)" in band
        assert "band.y = maxf(band.x, band.y - _dock_width - HUD_MARGIN)" in band
        assert "var band := hud_band(view)" in G.func_body(utils, "clamp_anchored_panel")
        main = G.read(_SCRIPTS / "main.gd")
        assert "Utils.hud_band(size).x + TERMINAL_ANCHOR_LEFT" in G.func_body(main, "_terminal_left")
        assert "_hud_room().x - TERMINAL_ANCHOR_LEFT * 2.0" in G.func_body(main, "_relayout_terminal")
        assert "mouse_pos.x - _terminal_left()" in G.func_body(main, "_resize_terminal_from_mouse")
        top = G.read(_SCRIPTS / "top_bar.gd")
        # The strip runs above the dock: the whole band.
        assert "Utils.hud_band_full(view)" in G.func_body(top, "_fit_bar")
        assert "Utils.hud_band(view)" in G.func_body(top, "_fit_rail")
        assert "Utils.hud_band(view)" in G.func_body(G.read(_SCRIPTS / "war_status_panel.gd"), "_apply_geometry")
        assert "Utils.hud_band(view)" in G.func_body(G.read(_SCRIPTS / "region_panel.gd"), "_fit_width")
        assert "Utils.hud_band(view)" in G.func_body(G.read(_SCRIPTS / "tutorial_overlay.gd"), "_card_placement")

    def test_a_change_refits_the_whole_hud(self):
        main = G.read(_SCRIPTS / "main.gd")
        body = G.func_body(main, "_refit_hud_band")
        for call in ("_on_root_resized()", "top_bar.refit_hud_band()", "_fit_panel_to_content",
                     "_on_viewport_resized", "_on_viewport_changed", "_queue_fit_map_controls()"):
            assert call in body, call
        assert "pause_menu.hud_width_changed.connect(" in G.code_lines(main)
        assert "_refit_hud_band()" in G.func_body(main, "_on_layout_reset")
        panel = G.read(_SCRIPTS / "settings_panel.gd")
        assert '_hud_width.name = "HudWidthOption"' in panel
        assert "hud_width_changed.emit(width)" in G.func_body(panel, "_on_hud_width_selected")

    def test_the_map_controls_are_fitted_and_never_take_focus(self):
        main = G.read(_SCRIPTS / "main.gd")
        build = G.func_body(main, "_build_map_controls")
        for name in ("ZoomOutButton", "FitEuropeButton", "ZoomInButton"):
            assert name in build
        assert "btn.focus_mode = Control.FOCUS_NONE" in build
        fit = G.func_body(main, "_fit_map_controls")
        assert "Utils.hud_band(size)" in fit and "_war_hud_rect()" in fit
        # reached by every resize and every terminal relayout (the live-refit road)
        assert "_queue_fit_map_controls()" in G.func_body(main, "_reposition_after_layout")
        renderer = G.read(_PROJECT / "scenes" / "map_renderer_base.gd")
        body = G.func_body(renderer, "fit_europe")
        assert body.index("zoom_tween.kill()") < body.index("_set_camera_zoom_level(_get_initial_zoom_level())")
        assert "_center_view_on_map()" in body
        assert "zoom_tween.kill()" in G.func_body(renderer, "recenter_view")


class TestTheHeaderSaysScale:
    """UXR-X23 (the user's ruling): the command window's + / − step the
    Interface SCALE, so the header reads "Scale"; Settings' Text size grows
    the words alone."""

    def test_the_label_and_its_tooltips(self):
        scene = G.read(_PROJECT / "scenes" / "main.tscn")
        assert 'text = "Scale"' in G.node_block(scene, "TextSizeLabel")
        assert "Interface Scale" in G.node_block(scene, "TextSizeBox")
        assert 'tooltip_text = "Larger interface (all screens)"' in scene
        readout = G.func_body(G.read(_SCRIPTS / "main.gd"), "_update_text_size_readout")
        assert '"Interface Scale: %d%%' in readout
