"""UXR-1 "The scale fix with the widest reach" — the pins (October 9, 2026).

`docs/UX_UI_REVIEW_PLAN.md` UXR-1 and the ruling in
`docs/audits/UXR_ADJUSTABILITY_REVIEW_2026_10_09.md` §7. What is pinned:

  * the Interface Scale is DERIVED from the screen at first boot — the GDScript
    formula (`UiSettings.derive_ui_scale_for`) and its Python twin
    (`tools/uxr0_readability_report.derive_ui_scale`) agree on a table of
    screens, DRIVEN through the engine (skips without it — a skip is not a pass);
  * the cap is 3.0; a CHOSEN scale is never overwritten by a derivation; the
    menu applies the stored scale at launch (UXR-X1);
  * the theme floor — Caption / CaptionButton / CaptionRich at 14 — and NO raw
    font-size override under 14 survives in the client's scenes or scripts,
    outside the two recorded exemptions;
  * the tutor card is sized by the viewport and bounds its body (UXR-X3);
  * the pause menu's Settings are no longer squeezed (UXR-X2);
  * the first-run card exists, asks ONE question, and persists through the one
    setter that marks the scale chosen;
  * the capture harness keeps the player's settings file untouched by
    construction (`UiSettings._persist`), and shoots PHYSICAL frames at the
    five resolutions incl. the user's own 5120x1440.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
PROJECT = REPO / "godot-client" / "project-sovereign"
SCRIPTS = PROJECT / "scripts"
SCENES = PROJECT / "scenes"
TOOLS = REPO / "tools"
THEME = PROJECT / "ui" / "main_theme.tres"

sys.path.insert(0, str(TOOLS))
from uxr0_readability_report import (  # noqa: E402
    BODY_P1, BODY_RED, CAPTION_P1, CAPTION_RED, PHYSICAL_RESOLUTIONS, derive_ui_scale,
)


def _read(p: pathlib.Path) -> str:
    return p.read_text(encoding="utf-8")


def _godot() -> str:
    for cand in (os.environ.get("GODOT_BIN", ""),
                 r"C:\Users\User\Downloads\Godot_v4.4.1-stable_win64.exe"
                 r"\Godot_v4.4.1-stable_win64.exe",
                 "godot"):
        if cand and (pathlib.Path(cand).is_file() or shutil.which(cand)):
            return cand
    return ""


# ═══════════════════════════ the derivation ═════════════════════════════════

# (width, height, dpi) → the scale a player at that screen gets. The table IS
# the ruling (§5 of the review): the Windows scaling is the floor, the pixel
# height lifts it, a 32:9 panel adds a quarter, 3.0 caps it.
DERIVATION_TABLE = [
    ((1920, 1080, 96), 1.00),    # a 24-inch 1080p: nothing to derive
    ((2560, 1440, 96), 1.15),    # a 27-inch 1440p
    ((3440, 1440, 96), 1.15),    # a 34-inch 21:9 (2.39 — under the 32:9 term)
    ((5120, 1440, 96), 1.40),    # THE USER'S OWN PANEL — 32:9 at 100%
    ((3840, 2160, 144), 1.75),   # a 27-inch 4K at Windows 150%
    ((3840, 2160, 96), 1.50),    # a 43-inch 4K at 100%
    ((1920, 1080, 120), 1.25),   # a 15-inch laptop at 125%
    ((7680, 4320, 96), 2.50),    # 8K at 100%: (1 + 4) / 2, still under the cap
    ((7680, 4320, 192), 3.00),   # 8K at Windows 200%: the cap
    ((1280, 720, 96), 1.00),     # under 1080p: the floor, never below 1.0
]


class TestTheDerivation:
    @pytest.mark.parametrize("screen,expected", DERIVATION_TABLE)
    def test_the_python_twin_on_the_table(self, screen, expected):
        assert derive_ui_scale(*screen) == pytest.approx(expected, abs=1e-6)

    def test_no_screen_is_the_floor(self):
        assert derive_ui_scale(0, 0, 96) == 1.0

    def test_the_gdscript_terms_are_the_pythons(self):
        """The constants the two formulas share, read off the GDScript."""
        text = _read(SCRIPTS / "ui_settings.gd")
        assert re.search(r"const MAX_UI_SCALE := 3\.0\b", text)
        assert re.search(r"const ULTRA_WIDE_ASPECT := 3\.0\b", text)
        assert re.search(r"const ULTRA_WIDE_BONUS := 0\.25\b", text)
        assert re.search(r"const DERIVE_FLOOR := 1\.0\b", text)
        assert "static func derive_default_ui_scale() -> float" in text
        assert "static func derive_ui_scale_for(width: int, height: int, dpi: float) -> float" in text
        assert "DisplayServer.screen_get_dpi(" in text
        assert "DisplayServer.screen_get_size(" in text

    def test_the_two_formulas_agree_driven(self, tmp_path):
        """The engine runs `derive_ui_scale_for` over the table; the numbers
        must be the Python twin's to the last digit."""
        engine = _godot()
        if not engine:
            pytest.skip("Godot engine not on this machine — the driven pin skips, "
                        "and a skip is not a pass")
        table = [[w, h, d] for (w, h, d), _ in DERIVATION_TABLE] + [[1600, 900, 96], [2560, 1440, 120]]
        table_path = tmp_path / "table.json"
        table_path.write_text(json.dumps(table), encoding="utf-8")
        out = tmp_path / "out.json"
        env = dict(os.environ, UXR1_PROBE_TABLE=str(table_path), UXR1_PROBE_OUT=str(out))
        env.pop("PYTHONIOENCODING", None)
        subprocess.run([engine, "--headless", "--path", str(PROJECT),
                        "--script", str(TOOLS / "uxr1_derive_probe.gd")],
                       capture_output=True, text=True, timeout=300, env=env, cwd=str(REPO))
        assert out.is_file(), "the probe wrote nothing"
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["max"] == 3.0 and data["min"] == 0.75
        assert data["no_screen"] == 1.0
        rows = data["rows"]
        assert len(rows) == len(table)
        for row in rows:
            py = derive_ui_scale(row["width"], row["height"], row["dpi"])
            assert row["scale"] == pytest.approx(py, abs=1e-6), row


# ═══════════════════════════ the settings seam ══════════════════════════════

class TestTheScaleIsNeverOverwritten:
    def test_a_chosen_scale_is_marked_chosen(self):
        text = _read(SCRIPTS / "ui_settings.gd")
        body = text.split("static func set_ui_scale(", 1)[1].split("static func", 1)[0]
        assert '"ui_scale_auto", false' in body

    def test_the_boot_resolver_derives_only_while_auto(self):
        text = _read(SCRIPTS / "ui_settings.gd")
        body = text.split("static func resolve_ui_scale_at_boot(", 1)[1].split("static func", 1)[0]
        assert "if is_ui_scale_auto():" in body
        assert "derive_default_ui_scale()" in body
        assert '"ui_scale_auto", true' in body

    def test_an_unstored_scale_reads_as_the_derivation(self):
        text = _read(SCRIPTS / "ui_settings.gd")
        body = text.split("static func get_ui_scale(", 1)[1].split("static func", 1)[0]
        assert 'has_section_key("display", "ui_scale")' in body
        assert "return derive_default_ui_scale()" in body

    def test_every_write_goes_through_the_persist_guard(self):
        """The harness rail: `_persist = false` keeps a scene's own setter
        calls in memory. No setter may save the file directly."""
        text = _read(SCRIPTS / "ui_settings.gd")
        assert "static var _persist := true" in text
        assert text.count("_config().save(PATH)") == 1, "only _save() may touch the file"
        assert "if _persist:" in text
        harness = _read(TOOLS / "iq10_surface_screenshot.gd")
        assert 'settings_class.set("_persist", false)' in harness


class TestTheMenuAppliesTheScaleAtLaunch:
    """UXR-X1: the menu drew at 100% every launch whatever was stored."""

    def test_ready_applies_the_resolved_scale_first(self):
        text = _read(SCRIPTS / "main_menu.gd")
        ready = text.split("func _ready() -> void:", 1)[1].split("\nfunc ", 1)[0]
        assert "_apply_boot_scale()" in ready
        assert ready.index("_apply_boot_scale()") < ready.index("_build_title_block()")
        body = text.split("func _apply_boot_scale() -> void:", 1)[1].split("\nfunc ", 1)[0]
        assert "UiSettings.resolve_ui_scale_at_boot()" in body
        assert "content_scale_factor" in body

    def test_the_card_is_raised_once_until_acknowledged(self):
        text = _read(SCRIPTS / "main_menu.gd")
        body = text.split("func _maybe_open_scale_card() -> void:", 1)[1].split("\nfunc ", 1)[0]
        assert "UiSettings.get_scale_acknowledged()" in body
        assert "open_scale_card()" in body
        start = text.split("func _start_presentation() -> void:", 1)[1].split("\nfunc ", 1)[0]
        assert "_maybe_open_scale_card()" in start


class TestTheFirstRunCard:
    def test_it_asks_one_question_with_a_live_sample(self):
        text = _read(SCRIPTS / "scale_card.gd")
        assert "class_name ScaleCard" in text
        assert "CAN YOU READ THIS COMFORTABLY?" in text
        for name in ("SampleCaption", "SampleBody", "SampleCounters"):
            assert f'name = "{name}"' in text
        # exactly one slider, bound to the published range
        assert text.count("HSlider.new()") == 1
        assert "UiSettings.MIN_UI_SCALE" in text and "UiSettings.MAX_UI_SCALE" in text

    def test_looks_right_persists_through_the_chosen_setter(self):
        text = _read(SCRIPTS / "scale_card.gd")
        body = text.split("func _on_accept() -> void:", 1)[1].split("\nfunc ", 1)[0]
        assert "UiSettings.set_ui_scale(value)" in body
        assert "UiSettings.set_scale_acknowledged(true)" in body
        # a preview stores nothing
        preview = text.split("func _on_slider_changed(value: float) -> void:", 1)[1].split("\nfunc ", 1)[0]
        assert "UiSettings.set_" not in preview

    def test_the_card_is_in_the_parse_harness(self):
        check = _read(TOOLS / "godot_parse_check.gd")
        assert '"res://scripts/scale_card.gd"' in check
        assert '"res://../../tools/uxr1_derive_probe.gd"' in check


# ═══════════════════════════ the theme floor ════════════════════════════════

FLOOR = 14
# Recorded exemptions (the sweep's docstring): world-space map furniture
# (UXR-X4) and the war-detail popup's two computed sizes (UXR-2's).
GD_EXEMPT = {"map_renderer_base.gd"}


class TestTheThemeFloor:
    def test_the_caption_family_is_defined_at_fourteen(self):
        text = _read(THEME)
        assert re.search(r'(?m)^Caption/base_type = &"Label"$', text)
        assert re.search(r"(?m)^Caption/font_sizes/font_size = 14$", text)
        assert re.search(r'(?m)^CaptionButton/base_type = &"Button"$', text)
        assert re.search(r"(?m)^CaptionButton/font_sizes/font_size = 14$", text)
        assert re.search(r'(?m)^CaptionRich/base_type = &"RichTextLabel"$', text)
        for key in ("normal", "bold", "italics", "bold_italics"):
            assert re.search(rf"(?m)^CaptionRich/font_sizes/{key}_font_size = 14$", text), key

    def test_no_scene_carries_a_raw_override_under_the_floor(self):
        offenders = []
        for scene in sorted(SCENES.glob("*.tscn")):
            for m in re.finditer(r"theme_override_font_sizes/[a-z_]+ = (\d+)", _read(scene)):
                if int(m.group(1)) < FLOOR:
                    offenders.append((scene.name, m.group(0)))
        assert offenders == [], offenders

    def test_no_script_carries_a_raw_override_under_the_floor(self):
        offenders = []
        for script in sorted(list(SCRIPTS.glob("*.gd")) + list(SCENES.glob("*.gd"))):
            if script.name in GD_EXEMPT:
                continue
            for m in re.finditer(r'add_theme_font_size_override\("[a-z_]+", *(\d+)\)', _read(script)):
                if int(m.group(1)) < FLOOR:
                    offenders.append((script.name, m.group(0)))
        assert offenders == [], offenders

    def test_the_exemption_is_real_and_bounded(self):
        """The map renderer's world-space labels keep their sizes (UXR-X4);
        the count is pinned so a new one cannot hide under the exemption."""
        text = _read(SCENES / "map_renderer_base.gd")
        small = [m.group(0) for m in re.finditer(
            r'add_theme_font_size_override\("font_size", *(\d+)\)', text) if int(m.group(1)) < FLOOR]
        assert len(small) == 5, small

    def test_the_floor_is_used_not_just_declared(self):
        """The sweep's variations are referenced across the client."""
        hits = 0
        for p in list(SCENES.glob("*.tscn")) + list(SCRIPTS.glob("*.gd")):
            hits += len(re.findall(r'theme_type_variation = &"Caption(Button|Rich)?"', _read(p)))
        assert hits >= 120, hits

    def test_the_sweep_is_idempotent(self):
        """Running the recorded sweep again changes nothing (its rule has
        been fully applied)."""
        proc = subprocess.run([sys.executable, str(TOOLS / "uxr1_font_floor_sweep.py")],
                              capture_output=True, text=True, cwd=str(REPO), timeout=120)
        assert proc.returncode == 0, proc.stderr
        assert "swept 0 site(s)" in proc.stdout, proc.stdout


# ═══════════════════════════ the tutor card ═════════════════════════════════

class TestTheTutorCardIsSizedByTheScreen:
    def test_width_is_a_viewport_fraction_inside_bounds(self):
        text = _read(SCRIPTS / "tutorial_overlay.gd")
        assert re.search(r"const CARD_WIDTH_FRACTION := 0\.22\b", text)
        assert re.search(r"const CARD_MIN_WIDTH := 396\.0\b", text)
        assert re.search(r"const CARD_MAX_WIDTH := 560\.0\b", text)
        body = text.split("func _fit_card_width() -> void:", 1)[1].split("\nfunc ", 1)[0]
        assert "view.x * CARD_WIDTH_FRACTION" in body
        assert "_card.offset_left" in body and "_card.offset_right" in body

    def test_the_body_is_bounded_by_the_viewport_and_scrolls_past_it(self):
        """UXR-X3: card XIX ran off a 480-px logical viewport."""
        text = _read(SCRIPTS / "tutorial_overlay.gd")
        body = text.split("func _fit_card_height() -> void:", 1)[1].split("\nfunc ", 1)[0]
        assert "_body.get_content_height()" in body
        assert "_body.scroll_active = true" in body and "_body.fit_content = false" in body
        assert "_body.scroll_active = false" in body and "_body.fit_content = true" in body
        render = text.split("func _render() -> void:", 1)[1].split("\nfunc ", 1)[0]
        assert "_fit_card_height.call_deferred()" in render
        ready = text.split("func _ready() -> void:", 1)[1].split("\nfunc ", 1)[0]
        assert "size_changed.connect(_on_viewport_changed)" in ready

    def test_the_card_text_rides_the_theme(self):
        scene = _read(SCENES / "tutorial_overlay.tscn")
        assert "theme_override_font_sizes" not in scene.split('[node name="BodyText"', 1)[1].split("[node", 1)[0]
        assert scene.count('theme_type_variation = &"Caption"') >= 3


class TestThePauseMenuSettingsAreNotSqueezed:
    def test_the_ceiling_is_raised_while_settings_are_open(self):
        """UXR-X2: the clamp kept the authored 400 as the ceiling against a
        440-px settings scroll, and cut the scroll to a sliver."""
        text = _read(SCRIPTS / "pause_menu.gd")
        body = text.split("func _on_settings():", 1)[1].split("\nfunc ", 1)[0]
        assert 'set_meta("clamp_ceiling_override", Vector2(360, 900))' in body
        assert 'remove_meta("clamp_ceiling_override")' in body
        reset = text.split("func _reset_menu_state():", 1)[1].split("\nfunc ", 1)[0]
        assert 'remove_meta("clamp_ceiling_override")' in reset


# ═══════════════════════════ the instrument (UXR-0) ═════════════════════════

class TestTheInstrument:
    def test_the_five_resolutions_include_the_users_own(self):
        assert (5120, 1440) in PHYSICAL_RESOLUTIONS
        assert PHYSICAL_RESOLUTIONS == [(1920, 1080), (2560, 1440), (3440, 1440), (5120, 1440),
                                        (3840, 2160)]

    def test_the_floor_is_held_in_one_place(self):
        assert (BODY_RED, BODY_P1, CAPTION_RED, CAPTION_P1) == (16.0, 13.0, 14.0, 12.0)
        harness = _read(TOOLS / "iq10_surface_screenshot.gd")
        # the harness records numbers; it applies no threshold
        assert "BODY_RED" not in harness and "16.0" not in harness.split("_add_text_metrics", 1)[1][:3000]

    def test_the_census_records_em_cap_and_x_in_physical_px(self):
        harness = _read(TOOLS / "iq10_surface_screenshot.gd")
        body = harness.split("func _add_text_metrics(", 1)[1].split("\nfunc ", 1)[0]
        assert "root.content_scale_factor" in body, "the screen transform does not carry it"
        assert "get_global_transform_with_canvas().get_scale().y" in body
        for key in ('entry["em_px"]', 'entry["cap_px"]', 'entry["x_px"]', 'entry["tier"]'):
            assert key in body, key
        glyph = harness.split("func _glyph_ratios(", 1)[1].split("\nfunc ", 1)[0]
        assert "font_get_glyph_size" in glyph

    def test_the_runner_has_physical_mode_and_the_war_room(self):
        runner = _read(TOOLS / "iq10_run_captures.py")
        assert "--physical" in runner and "def expand_physical(" in runner
        assert "from uxr0_readability_report import PHYSICAL_RESOLUTIONS, derive_ui_scale" in runner
        for shot in ("war_room_boot", "war_room_tutorial", "war_room_pause_settings",
                     "tutorial_card", "main_menu", "main_menu_settings"):
            assert f'"id": "{shot}"' in runner, shot
        assert 'HARNESS_PORT = "8999"' in runner

    def test_the_war_room_waits_on_the_boot_flag_not_on_frames(self):
        runner = _read(TOOLS / "iq10_run_captures.py")
        assert '{"wait_for": "_initial_map_bootstrapped"' in runner
        harness = _read(TOOLS / "iq10_surface_screenshot.gd")
        assert 'step.has("wait_for")' in harness
        assert "class MainStub extends Node" in harness

    def test_the_payload_tool_captures_the_war_room(self):
        tool = _read(TOOLS / "iq10_capture_payloads.py")
        assert "def cap_war_room():" in tool
        assert '"war_room": cap_war_room' in tool
        for name in ("war_room_boot", "war_room_tutorial", "new_game_tutorial"):
            assert f'record("{name}"' in tool, name
