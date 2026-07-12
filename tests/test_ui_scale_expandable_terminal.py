"""UI Visual Foundation Sweep — Session U2 Part 1 behavior gate.

Pins the "UI Scale & Expandable Command Window" deliverables per
``docs/UI_VISUAL_FOUNDATION_SPEC.md`` §8 U2 (the DEF-13 fold):

- ``ui_settings.gd`` persists the three display preferences (terminal size,
  terminal text scale, global UI scale) with clamped ranges.
- The command window (``BottomLeftUI``) is user-resizable via a corner grip and
  text-scalable via A− / A+ buttons, wired in ``main.gd``.
- A global ``content_scale_factor`` "Interface Scale" slider lives in the
  pause-menu Settings and drives ``main.gd`` (which owns persistence + the
  native-map compensation).
- The map renderer re-asserts the SubViewport at physical resolution so the map
  stays crisp under a non-1.0 scale (``refresh_viewport_scale``).

Display-only slice (Golden Rule 6): these are file/text assertions — no game
logic. The engine boot-smoke (0 ``SCRIPT ERROR``) is the manual per-session
gate pytest cannot observe.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GODOT = REPO_ROOT / "godot-client" / "project-sovereign"
SCRIPTS = GODOT / "scripts"
SCENES = GODOT / "scenes"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════════
# ui_settings.gd — the persistence layer
# ═══════════════════════════════════════════════════════════════════════════


def test_ui_settings_exists_and_is_a_class():
    text = _read(SCRIPTS / "ui_settings.gd")
    assert "class_name UiSettings" in text
    assert 'const PATH := "user://ui_settings.cfg"' in text


def test_ui_settings_exposes_the_three_preferences():
    text = _read(SCRIPTS / "ui_settings.gd")
    for getter in (
        "func get_terminal_width",
        "func get_terminal_height",
        "func set_terminal_size",
        "func get_terminal_scale",
        "func set_terminal_scale",
        "func get_ui_scale",
        "func set_ui_scale",
    ):
        assert getter in text, f"ui_settings.gd missing {getter}"


def test_ui_settings_clamps_ranges():
    text = _read(SCRIPTS / "ui_settings.gd")
    # Every getter/setter clamps; the ranges are published as constants.
    assert "clampf(" in text
    for const in (
        "MIN_TERMINAL_WIDTH",
        "MAX_TERMINAL_WIDTH",
        "MIN_TERMINAL_HEIGHT",
        "MAX_TERMINAL_HEIGHT",
        "MIN_TERMINAL_SCALE",
        "MAX_TERMINAL_SCALE",
        "MIN_UI_SCALE",
        "MAX_UI_SCALE",
    ):
        assert const in text, f"ui_settings.gd missing range constant {const}"


def test_ui_scale_range_is_sane():
    text = _read(SCRIPTS / "ui_settings.gd")
    lo = float(re.search(r"MIN_UI_SCALE\s*:=\s*([\d.]+)", text).group(1))
    hi = float(re.search(r"MAX_UI_SCALE\s*:=\s*([\d.]+)", text).group(1))
    assert lo < 1.0 < hi, "UI scale range must straddle 1.0"
    assert 0.5 <= lo <= 0.9 and 1.5 <= hi <= 3.0


# ═══════════════════════════════════════════════════════════════════════════
# main.gd — the expandable + scaling command window
# ═══════════════════════════════════════════════════════════════════════════


def test_main_wires_resize_grip_and_drag():
    text = _read(SCRIPTS / "main.gd")
    assert "func _create_resize_grip" in text
    assert "func _on_grip_gui_input" in text
    assert "func _resize_terminal_from_mouse" in text
    # Double-click on the grip resets the footprint.
    assert "double_click" in text
    assert "func _reset_terminal_size" in text


def test_main_wires_terminal_text_scale():
    text = _read(SCRIPTS / "main.gd")
    assert "func _apply_terminal_scale" in text
    assert "add_theme_font_size_override" in text
    assert "scale_down_button" in text and "scale_up_button" in text
    # Base sizes are auto-discovered from the .tscn, not hardcoded.
    assert "func _collect_scalable_fonts" in text


def test_main_applies_and_persists_settings():
    text = _read(SCRIPTS / "main.gd")
    assert "UiSettings.get_terminal_scale()" in text
    assert "UiSettings.set_terminal_size(" in text
    assert "UiSettings.get_ui_scale()" in text
    assert "func _apply_ui_scale" in text
    assert "content_scale_factor" in text


def test_main_refreshes_map_on_scale_change():
    text = _read(SCRIPTS / "main.gd")
    assert "refresh_viewport_scale" in text


# ═══════════════════════════════════════════════════════════════════════════
# pause_menu — the global Interface Scale slider
# ═══════════════════════════════════════════════════════════════════════════


def test_pause_menu_scene_has_ui_scale_slider():
    text = _read(SCENES / "pause_menu.tscn")
    assert '[node name="UiScaleSlider" type="HSlider"' in text
    # The old dead stub is gone.
    assert "Settings coming soon" not in text


def test_pause_menu_emits_ui_scale_changed():
    text = _read(SCRIPTS / "pause_menu.gd")
    assert "signal ui_scale_changed" in text
    assert "ui_scale_changed.emit(" in text
    assert "func _on_ui_scale_slider_changed" in text
    # Initializes from the saved preference without a spurious boot emit.
    assert "set_value_no_signal(" in text


def test_main_connects_pause_menu_scale_signal():
    text = _read(SCRIPTS / "main.gd")
    assert 'pause_menu.ui_scale_changed.connect(_on_ui_scale_changed)' in text


# ═══════════════════════════════════════════════════════════════════════════
# map renderer — native-map compensation
# ═══════════════════════════════════════════════════════════════════════════


def test_renderer_has_scale_refresh_hook():
    text = _read(SCENES / "map_renderer_base.gd")
    # UI-2 Part 2 landed the physical-resolution compensation: the hook now
    # re-asserts the SubViewport render resolution (via
    # _refresh_map_viewport_resolution) AND recomputes the camera fit after a
    # global content_scale_factor change. (Deeper Part-2 assertions live in
    # tests/test_ui2_part2_color_and_map.py.)
    hook = text.split("func refresh_viewport_scale", 1)
    assert len(hook) == 2, "renderer must define refresh_viewport_scale"
    body = hook[1].split("\nfunc ", 1)[0]
    assert "_update_camera_limits" in body
    assert "_refresh_map_viewport_resolution" in body, (
        "refresh_viewport_scale must re-assert the physical render resolution"
    )
