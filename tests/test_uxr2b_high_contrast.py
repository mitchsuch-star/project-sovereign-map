"""UXR-D2 "High contrast" — the pins (Pre-Deploy S9b Slice D, October 13, 2026),
with the contrast instrument it needed (UXR-3's R3 item, built now).

"Dim" is a class, not one token: the BBCode greys (COLOR_DIM 666670, DIMMED /
GREY 808080, INFO a0a0a8), UI_TEXT_DIM, and grey font colours authored as
literals in scenes and scripts. Settings → INTERFACE → *High contrast* raises
every member at least one step of the dim ladder, and leaves none under the
step that reads 4.5 : 1 on the game's panels (a0a0a8).

The done-when (`docs/DESIGN_REFINEMENT.md` §UXR, row UXR-D2): the contrast
measured off the frames reads >= 4.5 : 1 for body and >= 3 : 1 for captions on
the five named surfaces with the toggle on. Read off the committed records
(`tools/uxr2b_contrast_report.py` over `iq10_run_captures.py --physical
--physical-scale auto [--high-contrast]`): the text colour is the one the node
DECLARES (font colour, BBCode spans, chip pairs, times its modulate), the
colour behind it is read off the frame (the median of the row's rect), the
ratio is WCAG's. The OFF record is the instrument shown able to fail.
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
import pytest

from tests import _godot_scenes as G

REPO = pathlib.Path(__file__).resolve().parents[1]
PROJECT = REPO / "godot-client" / "project-sovereign"
SCRIPTS = PROJECT / "scripts"
RECORDS = REPO / "docs" / "audits" / "uxr0"
OFF = RECORDS / "contrast_hc_off_named_2026_10_13.json"
ON = RECORDS / "contrast_hc_on_named_2026_10_13.json"
NAMED = ("tutorial_card", "war_room_tutorial", "dispatch_boot_today", "dispatch_t20",
         "war_room_boot", "top_bar_boot", "generals_boot")
RESOLUTIONS = ("1920x1080", "2560x1440", "3440x1440", "5120x1440", "3840x2160")

sys.path.insert(0, str(REPO / "tools"))
import uxr2b_contrast_report as C  # noqa: E402


def _load(path: pathlib.Path) -> dict:
    assert path.is_file(), f"the committed record is missing: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def off() -> dict:
    return _load(OFF)


@pytest.fixture(scope="module")
def on() -> dict:
    return _load(ON)


class TestTheDoneWhen:
    def test_both_records_cover_the_named_surfaces_at_every_resolution(self, off, on):
        assert on["high_contrast"] is True and off["high_contrast"] is False
        for rec in (off, on):
            assert rec["physical_scale"] == "auto"
            for sid in NAMED:
                keys = set(rec["surfaces"][sid]["readings"])
                for res in RESOLUTIONS:
                    assert any(k.startswith(res + "@") for k in keys), (sid, res)

    def test_with_the_toggle_on_nothing_reads_under_the_floor(self, on):
        for sid in NAMED:
            for key, r in on["surfaces"][sid]["readings"].items():
                assert r["ok"], (sid, key)
                assert r["counts"]["measured"] > 0, (sid, key)
                assert r["counts"]["under"] == 0, (sid, key, r["under"][:3])

    def test_with_it_off_the_instrument_finds_the_dim_class(self, off):
        """The OFF reading is the instrument shown able to fail: the Generals'
        666670 (3.1 : 1), the tutor card's and the dispatch's 808080 (4.3 / 4.4)
        — every one a member of the dim class the toggle raises."""
        under = [(sid, u) for sid in NAMED for r in off["surfaces"][sid]["readings"].values()
                 for u in r["under"]]
        assert len(under) >= 15, len(under)
        for sid, u in under:
            assert u["color"][:6] in ("666670", "808080"), (sid, u)


class TestTheReaderItself:
    """The reader on synthetic frames: a known background, a known colour."""

    def test_wcag_ratio_matches_the_reference_values(self):
        assert C.ratio((0, 0, 0), (1, 1, 1)) == pytest.approx(21.0, abs=0.01)
        assert C.ratio((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)) == pytest.approx(1.0)
        # 808080 on white is the textbook 3.95 : 1
        assert C.ratio(C._hex("808080")[:3], (1, 1, 1)) == pytest.approx(3.95, abs=0.01)

    def test_a_dim_row_on_a_dark_panel_is_caught_and_a_bright_one_passes(self):
        img = np.zeros((40, 200, 3), dtype=np.uint8)
        img[:, :] = (0x14, 0x19, 0x26)          # the dispatch panel's navy
        dim = {"tier": "body", "rect": [0, 0, 200, 40], "colors": ["666670ff"]}
        bright = {"tier": "body", "rect": [0, 0, 200, 40], "colors": ["a0a0a8ff"]}
        assert C.measure_row(dim, img, 1.0)[0] < C.BODY_FLOOR
        assert C.measure_row(bright, img, 1.0)[0] >= C.BODY_FLOOR
        # a caption has the lower floor; a disabled button is not measured
        assert C.floor_for({"tier": "caption"}) == C.CAPTION_FLOOR
        assert C.measure_row(dict(dim, disabled=True), img, 1.0) is None

    def test_a_chip_is_measured_against_its_own_fill(self):
        img = np.zeros((40, 200, 3), dtype=np.uint8)
        row = {"tier": "body", "rect": [0, 0, 200, 40], "colors": ["ffffffff"],
               "chips": [["d9c08cff", "e0d0a0ff"]]}            # pale gold on pale gold
        assert C.measure_row(row, img, 1.0)[0] < 2.0
        locked = dict(row, chips=[list(C.DISABLED_CHIP)])
        assert C.measure_row(locked, img, 1.0)[0] > 15.0       # white on black; the locked chip skipped


class TestTheToggle:
    def test_the_store(self):
        src = G.read(SCRIPTS / "ui_settings.gd")
        assert '"display", "high_contrast", false' in G.func_body(src, "get_high_contrast")
        assert 'const HIGH_CONTRAST_FLOOR_HEX := "a0a0a8"' in src
        assert "high_contrast" not in G.func_body(src, "reset_layout")   # a preference, kept

    def test_the_ladder_and_the_floor_step(self):
        src = G.read(SCRIPTS / "utils.gd")
        code = G.code_lines(src)
        assert "const DIM_FLOOR_INDEX := 2" in code
        raise_body = G.func_body(src, "raise_dim")
        assert "if i >= DIM_FLOOR_INDEX and t.get_luminance() > l + 0.02:" in raise_body
        assert "return Color(t.r, t.g, t.b, c.a)" in raise_body     # alpha kept
        assert "chroma <= 0.12" in G.func_body(src, "is_dim")      # greys only — colours stay

    def test_the_bbcode_tokens_are_static_and_retoned(self):
        src = G.read(SCRIPTS / "utils.gd")
        for token in ('static var COLOR_INFO := "a0a0a8"', 'static var COLOR_DIMMED := "808080"',
                      'static var COLOR_GREY := "808080"', 'static var COLOR_DIM := "666670"'):
            assert token in src, token
        body = G.func_body(src, "apply_contrast")
        for token in ("COLOR_DIM", "COLOR_DIMMED", "COLOR_GREY", "COLOR_INFO"):
            assert f"{token} = toned_hex(" in body, token
        # the Generals' local faintest grey is the shared token now — and since
        # Pre-Deploy S12 (UXR3-25) every body line sits at the floor step,
        # COLOR_INFO, so the screen names no step under it
        mm = G.read(SCRIPTS / "marshal_management.gd")
        assert 'const COLOR_DIM = "666670"' not in mm and "Utils.COLOR_INFO" in mm
        assert "Utils.COLOR_DIM" not in G.code_lines(mm)

    def test_one_chokepoint_raises_and_restores(self):
        src = G.read(SCRIPTS / "utils.gd")
        body = G.func_body(src, "contrast_node")
        assert 'for key in ["font_color", "default_color"]:' in body
        assert "c.set_meta(meta, orig)" in body                        # the original kept
        assert "c.add_theme_color_override(key, c.get_meta(meta))" in body   # and restored
        hook = G.func_body(src, "apply_contrast")
        assert "tree.node_added.connect(hook)" in hook and "tree.node_added.disconnect(hook)" in hook
        assert "apply_contrast_to(tree.root)" in hook

    def test_both_boots_and_the_settings_toggle_apply_it(self):
        for name in ("main.gd", "main_menu.gd"):
            assert "Utils.apply_contrast(get_tree())" in G.code_lines(G.read(SCRIPTS / name)), name
        panel = G.read(SCRIPTS / "settings_panel.gd")
        assert '_contrast_toggle.name = "HighContrastToggle"' in panel
        body = G.func_body(panel, "_on_high_contrast_toggled")
        assert "UiSettings.set_high_contrast(on)" in body and "Utils.apply_contrast(get_tree())" in body
        # the top bar's run-time greys go through the same tone
        assert G.read(SCRIPTS / "top_bar.gd").count("Utils.toned(Utils.UI_TEXT_DIM)") == 3

    def test_the_capture_shoots_with_it(self):
        runner = G.read(REPO / "tools" / "iq10_run_captures.py")
        assert '"--high-contrast"' in runner
        harness = G.read(REPO / "tools" / "iq10_surface_screenshot.gd")
        assert 'UiSettings._cfg.set_value("display", "high_contrast", high_contrast)' in harness
        assert "_add_text_colors(entry, n)" in harness
        assert 'entry["rect"] = [r.position.x, r.position.y, r.size.x, r.size.y]' in harness
