"""UXR-1b "The Settings additions" — the pins (October 9, 2026; Pre-Deploy S1b).

The adjustability review's decisions 4 + 5 (`docs/audits/UXR_ADJUSTABILITY_REVIEW_2026_10_09.md`
§7): window mode + size picker, the command window's default footprint as a
viewport fraction, Ctrl+= / Ctrl+− / Ctrl+0, Reset layout, the CONTROLS reference,
the Plain body-font option, and the sizing card reachable from Settings — plus the
floor's residue the whole-client census exposed (the campaign log's 11-px routine
tier, six literal 15s, a bold smaller than its body). Rules `SYSTEMS_REFERENCE.md`
§99.8–§99.10.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
PROJECT = REPO / "godot-client" / "project-sovereign"
SCRIPTS = PROJECT / "scripts"
SCENES = PROJECT / "scenes"
TOOLS = REPO / "tools"


def _read(p: pathlib.Path) -> str:
    return p.read_text(encoding="utf-8")


def _func(src: str, head: str) -> str:
    """The body from `head` to the next function (plain or static)."""
    assert head in src, head
    rest = src.split(head, 1)[1]
    cut = len(rest)
    for marker in ("\nfunc ", "\nstatic func "):
        at = rest.find(marker)
        if at != -1:
            cut = min(cut, at)
    return rest[:cut]


# ═══════════════════════════ the settings seam ══════════════════════════════

class TestTheSettingsKeys:
    def test_window_mode_and_size_are_closed_lists_with_the_boot_as_default(self):
        src = _read(SCRIPTS / "ui_settings.gd")
        assert 'const WINDOW_MODES := ["maximized", "fullscreen", "borderless", "windowed"]' in src
        assert 'const DEFAULT_WINDOW_MODE := "maximized"' in src
        assert 'const WINDOW_SIZES := ["native", "3440x1440", "2560x1440", "1920x1080"]' in src
        body = _func(src, "static func get_window_mode() -> String:")
        assert "if mode in WINDOW_MODES else DEFAULT_WINDOW_MODE" in body

    def test_the_body_font_is_a_closed_list_with_garamond_as_default(self):
        src = _read(SCRIPTS / "ui_settings.gd")
        assert 'const BODY_FONTS := ["garamond", "plain"]' in src
        assert 'const DEFAULT_BODY_FONT := "garamond"' in src

    def test_the_terminal_default_is_a_viewport_fraction_inside_the_published_range(self):
        src = _read(SCRIPTS / "ui_settings.gd")
        assert re.search(r"const TERMINAL_WIDTH_FRACTION := 0\.28\b", src)
        assert re.search(r"const TERMINAL_HEIGHT_FRACTION := 0\.32\b", src)
        body = _func(src, "static func default_terminal_size(viewport: Vector2) -> Vector2:")
        assert "clampf(viewport.x * TERMINAL_WIDTH_FRACTION, DEFAULT_TERMINAL_WIDTH, MAX_TERMINAL_WIDTH)" in body
        assert "clampf(viewport.y * TERMINAL_HEIGHT_FRACTION, DEFAULT_TERMINAL_HEIGHT, MAX_TERMINAL_HEIGHT)" in body
        assert "static func has_terminal_size() -> bool:" in src
        assert "static func clear_terminal_size() -> void:" in src

    def test_reset_layout_resets_exactly_the_layout(self):
        src = _read(SCRIPTS / "ui_settings.gd")
        body = _func(src, "static func reset_layout() -> void:")
        assert "set_ui_scale_auto()" in body
        assert "clear_terminal_size()" in body
        assert "set_window_mode(DEFAULT_WINDOW_MODE)" in body
        assert "set_window_size(DEFAULT_WINDOW_SIZE)" in body
        for kept in ("audio", "api_key", "tutorial", "battle_sfx"):
            assert kept not in body, kept

    def test_the_harness_rail_is_read_by_the_window_setter(self):
        src = _read(SCRIPTS / "ui_settings.gd")
        assert "static func harness_active() -> bool:" in src
        assert "return not _persist" in src
        utils = _read(SCRIPTS / "utils.gd")
        body = _func(utils, "static func apply_window_settings(window: Window) -> void:")
        assert "UiSettings.harness_active()" in body, "a capture run must never move its window"
        for mode in ('"fullscreen":', '"borderless":', '"windowed":'):
            assert mode in body, mode
        assert "Window.MODE_MAXIMIZED" in body and "Window.MODE_FULLSCREEN" in body

    def test_a_window_size_never_exceeds_the_screen(self):
        utils = _read(SCRIPTS / "utils.gd")
        body = _func(utils, "static func window_size_for(choice: String, screen_size: Vector2i) -> Vector2i:")
        assert "mini(want.x, screen_size.x)" in body and "mini(want.y, screen_size.y)" in body


class TestTheBodyFont:
    def test_plain_is_source_sans_and_swaps_only_the_body_faces(self):
        utils = _read(SCRIPTS / "utils.gd")
        assert 'const _PLAIN_BODY_REGULAR := "res://assets/fonts/SourceSans3[wght].ttf"' in utils
        assert 'const _PLAIN_BODY_ITALIC := "res://assets/fonts/SourceSans3-Italic[wght].ttf"' in utils
        body = _func(utils, "static func apply_body_font() -> void:")
        assert "ThemeDB.get_project_theme()" in body
        assert "theme.default_font = regular" in body
        for face in ("normal_font", "bold_font", "italics_font", "bold_italics_font"):
            assert f'"{face}", "RichTextLabel"' in body, face
        # headings and the map are not touched
        assert "HeadingLabel" not in body and "Label\"" not in body.replace("RichTextLabel", "")
        # and garamond is restored from what was READ, not re-authored
        assert '_garamond_faces["default"]' in body

    def test_the_plain_faces_ship_with_their_licence(self):
        fonts = PROJECT / "assets" / "fonts"
        for name in ("SourceSans3[wght].ttf", "SourceSans3-Italic[wght].ttf", "SourceSans3-OFL.txt"):
            assert (fonts / name).is_file(), name
        for name in ("SourceSans3[wght].ttf.import", "SourceSans3-Italic[wght].ttf.import"):
            assert (fonts / name).is_file(), name


# ═══════════════════════════ the panel ══════════════════════════════════════

class TestTheSettingsPanel:
    def test_the_sections_in_order(self):
        src = _read(SCRIPTS / "settings_panel.gd")
        ready = _func(src, "func _ready() -> void:")
        order = [ready.index(s) for s in (
            "_build_display_section()", "_build_interface_section()", "_build_sound_section()",
            "_build_parser_section()", "_build_voice_section()", "_build_controls_section()",
            "_build_credits_section()")]
        assert order == sorted(order)
        for header in ('"DISPLAY"', '"INTERFACE"', '"CONTROLS"'):
            assert header in src, header

    def test_the_display_section_applies_the_window_on_change(self):
        src = _read(SCRIPTS / "settings_panel.gd")
        for fn in ("func _on_window_mode_selected(index: int) -> void:",
                   "func _on_window_size_selected(index: int) -> void:"):
            body = _func(src, fn)
            assert "Utils.apply_window_settings(get_window())" in body, fn
        assert "Utils.window_size_choices(screen)" in src
        assert '"This screen (%dx%d)"' in src

    def test_the_size_row_shows_for_windowed_only(self):
        src = _read(SCRIPTS / "settings_panel.gd")
        assert src.count('_window_size_row.visible = mode == "windowed"') == 2

    def test_the_reset_is_the_derived_size_not_one_hundred(self):
        src = _read(SCRIPTS / "settings_panel.gd")
        assert "Reset to 100%" not in src
        body = _func(src, "func _on_reset_scale() -> void:")
        assert "UiSettings.set_ui_scale_auto()" in body
        assert "ui_scale_changed.emit(derived, false)" in body
        assert '"Size for this screen (%d%%)"' in src

    def test_the_card_is_reachable_from_settings(self):
        src = _read(SCRIPTS / "settings_panel.gd")
        assert "signal size_card_requested" in src
        assert 'preview.text = "Preview with a sample…"' in src
        assert "size_card_requested.emit()" in src
        menu = _read(SCRIPTS / "main_menu.gd")
        assert "_settings_panel.size_card_requested.connect(open_scale_card)" in menu
        pause = _read(SCRIPTS / "pause_menu.gd")
        assert "signal size_card_requested" in pause and "signal layout_reset" in pause
        main = _read(SCRIPTS / "main.gd")
        assert "pause_menu.size_card_requested.connect(open_scale_card)" in main
        assert "pause_menu.layout_reset.connect(_on_layout_reset)" in main
        body = _func(main, "func open_scale_card() -> void:")
        assert "pause_menu.close_menu()" in body
        assert "_scale_card.open(UiSettings.get_ui_scale(), UiSettings.derive_default_ui_scale())" in body

    def test_opening_settings_answers_a_standing_card(self):
        """The first-run card must never sit over the Settings it points at:
        going to Settings keeps the size on screen and closes it."""
        menu = _read(SCRIPTS / "main_menu.gd")
        body = _func(menu, "func _open_settings() -> void:")
        assert body.index("_close_scale_card()") < body.index("_settings_view.visible = true")
        close = _func(menu, "func _close_scale_card() -> void:")
        assert "_scale_card._on_accept()" in close

    def test_reset_layout_reaches_both_hosts(self):
        src = _read(SCRIPTS / "settings_panel.gd")
        body = _func(src, "func _on_reset_layout() -> void:")
        assert "UiSettings.reset_layout()" in body
        assert "Utils.apply_window_settings(get_window())" in body
        assert "layout_reset.emit()" in body
        main = _read(SCRIPTS / "main.gd")
        body = _func(main, "func _on_layout_reset() -> void:")
        assert "_apply_ui_scale(UiSettings.get_ui_scale(), false)" in body
        assert "_reset_terminal_size()" in body

    def test_the_body_font_option_applies_at_once(self):
        src = _read(SCRIPTS / "settings_panel.gd")
        body = _func(src, "func _on_body_font_selected(index: int) -> void:")
        assert "UiSettings.set_body_font(face)" in body and "Utils.apply_body_font()" in body

    def test_the_controls_reference_names_every_advertised_key(self):
        src = _read(SCRIPTS / "settings_panel.gd")
        body = _func(src, "func _build_controls_section() -> void:")
        for key in ("L Event Log", "T Ledger", "G Generals", "D Diplomacy", "R Dispatch", "N Moniteur",
                    "F1 the Cabinet", "E End Turn", "Tab", "Home recentre", "M map", "Ctrl+=", "Ctrl+0",
                    "1–8"):
            assert key in body, key


# ═══════════════════════════ the hosts ══════════════════════════════════════

class TestTheHosts:
    def test_the_menu_applies_window_and_font_before_the_scale(self):
        menu = _read(SCRIPTS / "main_menu.gd")
        body = _func(menu, "func _apply_boot_scale() -> void:")
        assert body.index("Utils.apply_window_settings(get_window())") < body.index("resolve_ui_scale_at_boot")
        assert "Utils.apply_body_font()" in body

    def test_main_applies_font_and_window_at_ready(self):
        main = _read(SCRIPTS / "main.gd")
        ready = _func(main, "func _ready():")
        assert "Utils.apply_body_font()" in ready
        assert "Utils.apply_window_settings(get_window())" in ready
        assert ready.index("Utils.apply_body_font()") < ready.index("_apply_ui_scale(UiSettings.get_ui_scale(), false)")

    def test_the_scale_keys_on_both_input_roads_and_the_menu(self):
        main = _read(SCRIPTS / "main.gd")
        focused = _func(main, "func _on_command_input_gui_input(event):")
        assert "event.ctrl_pressed and _ctrl_scale_key(event.keycode)" in focused
        unfocused = _func(main, "func _unhandled_input(event):")
        assert "event.ctrl_pressed and _ctrl_scale_key(event.keycode)" in unfocused
        keys = _func(main, "func _ctrl_scale_key(keycode: int) -> bool:")
        assert "KEY_EQUAL, KEY_KP_ADD:" in keys and "_step_ui_scale(1)" in keys
        assert "KEY_MINUS, KEY_KP_SUBTRACT:" in keys and "_step_ui_scale(-1)" in keys
        assert "KEY_0, KEY_KP_0:" in keys and "UiSettings.set_ui_scale_auto()" in keys
        menu = _read(SCRIPTS / "main_menu.gd")
        assert "func _ctrl_scale_key(keycode: int) -> bool:" in menu
        # the map's bare +/- zoom never answers a Ctrl press
        renderer = _read(SCENES / "map_renderer_base.gd")
        body = _func(renderer, "func _unhandled_input(event):")
        assert "if event.ctrl_pressed:\n\t\t\treturn" in body

    def test_the_terminal_default_follows_the_viewport_until_the_player_drags(self):
        main = _read(SCRIPTS / "main.gd")
        assert "var _terminal_uses_default := true" in main
        setup = _func(main, "func _setup_scalable_terminal() -> void:")
        assert "_terminal_uses_default = not UiSettings.has_terminal_size()" in setup
        assert "UiSettings.default_terminal_size(size)" in setup
        resized = _func(main, "func _on_root_resized() -> void:")
        assert "if _terminal_uses_default:" in resized
        reset = _func(main, "func _reset_terminal_size() -> void:")
        assert "UiSettings.clear_terminal_size()" in reset and "_terminal_uses_default = true" in reset
        grip = _func(main, "func _on_grip_gui_input(event: InputEvent) -> void:")
        assert "_terminal_uses_default = false" in grip
        assert "UiSettings.set_terminal_size(_terminal_width, _terminal_height)" in grip

    def test_the_in_game_card_sits_above_the_pause_menu(self):
        main = _read(SCRIPTS / "main.gd")
        body = _func(main, "func _build_scale_card() -> void:")
        assert "_scale_card_layer.layer = 125" in body
        pause = _read(SCENES / "pause_menu.tscn")
        assert "layer = 120" in pause


# ═══════════════════════════ the floor's residue ════════════════════════════

class TestTheFloorsResidue:
    def test_no_literal_fifteen_survives_on_a_body_label_in_the_scenes(self):
        offenders = []
        for scene in sorted(SCENES.glob("*.tscn")):
            for m in re.finditer(r"theme_override_font_sizes/[a-z_]+ = 15$", _read(scene), re.M):
                offenders.append((scene.name, m.group(0)))
        assert offenders == [], offenders

    def test_the_log_tiers_stand_at_and_above_the_floor(self):
        src = _read(SCRIPTS / "campaign_log.gd")
        assert 'const TIER_FONT_SIZES := {"lead": 18, "notable": 16, "routine": 14}' in src
        assert 'const DEFAULT_ROW_FONT_SIZE := 16' in src
        assert 'label.theme_type_variation = &"CaptionRich"' in src

    def test_the_end_screens_bold_matches_its_body(self):
        src = _read(SCRIPTS / "campaign_end.gd")
        assert 'add_theme_font_size_override("normal_font_size", 17)' in src
        assert 'add_theme_font_size_override("bold_font_size", 17)' in src

    def test_the_sweep_records_the_fifteens_and_stays_idempotent(self):
        sweep = _read(TOOLS / "uxr1_font_floor_sweep.py")
        for name in ("clarification_popup.tscn", "diplomacy_wizard.tscn", "interrupt_popup.tscn",
                     "redemption_dialog.tscn"):
            assert f'("{name}", ' in sweep, name
        proc = subprocess.run([sys.executable, str(TOOLS / "uxr1_font_floor_sweep.py")],
                              capture_output=True, text=True, cwd=str(REPO), timeout=120)
        assert proc.returncode == 0, proc.stderr
        assert "swept 0 site(s)" in proc.stdout, proc.stdout
