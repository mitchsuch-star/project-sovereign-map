"""Region-panel + map hover/click UX pass (July 16, 2026).

User-reported defect: clicking a province opened the Region Action Panel
anchored center-left, growing downward into the expandable terminal's corner
— the panel and the command box fought for the same screen space (and, being
CanvasLayer 26, the panel covered the input box). The pass:

  1. Panel docked TOP-LEFT under the top bar; content in a ScrollContainer
     whose height is fitted per render and clamped above the terminal's live
     top edge (avoid_control wired from main.gd).
  2. Hover highlight moved to a GPU shader over the province lookup mask —
     the TRUE province silhouette lights up (old path CPU-stamped a circle
     into a full map-canvas image on every hover change).
  3. Click feedback: selected province stays lit while the panel is open
     (selected_key uniform + a decaying selected_boost pulse), pointing-hand
     cursor over wired provinces.
  4. Dismiss ladder: ESC (before pause), right-click, open-water click, and
     clicking the open province again all close the panel; closing clears
     the selection glow.

Source-level pins in the UI-6 test idiom (no headless Godot in CI).
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLIENT = ROOT / "godot-client" / "project-sovereign"
SCRIPTS = CLIENT / "scripts"
SCENES = CLIENT / "scenes"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TestPanelDock:
    def test_panel_docked_top_left_not_center(self):
        src = _read(SCENES / "region_panel.tscn")
        assert "layer = 26" in src  # still under every screen/modal
        # The old center-left anchor (anchor_top = 0.5 + negative offset) is
        # what grew the panel into the terminal's corner.
        assert "anchor_top = 0.5" not in src
        assert "offset_top = 48.0" in src

    def test_panel_content_scrolls(self):
        src = _read(SCENES / "region_panel.tscn")
        assert 'type="ScrollContainer"' in src
        # ContentArea now lives inside the scroll window.
        assert 'parent="PanelContainer/VBoxContainer/Scroll"' in src

    def test_panel_clamps_above_terminal(self):
        src = _read(SCRIPTS / "region_panel.gd")
        assert "avoid_control" in src
        assert "func _fit_height" in src
        # Clamp reads the avoided control's LIVE rect (terminal is draggable).
        assert "avoid_control.get_global_rect().position.y" in src
        # Refits on window/scale reflow.
        assert "size_changed.connect" in src

    def test_main_wires_terminal_as_avoid_control(self):
        src = _read(SCRIPTS / "main.gd")
        assert "region_panel.avoid_control = bottom_left_ui" in src

    def test_retarget_resets_scroll_refresh_keeps_it(self):
        src = _read(SCRIPTS / "region_panel.gd")
        assert "scroll.scroll_vertical = 0" in src
        assert "retargeted" in src


class TestHoverHighlightShader:
    def test_shader_exists_with_hover_and_selected_keys(self):
        src = _read(SCENES / "map_renderer_base.gd")
        assert "HIGHLIGHT_SHADER" in src
        for uniform in ("hover_key", "selected_key", "selected_boost"):
            assert uniform in src, uniform

    def test_shader_layer_uses_nearest_filter(self):
        """Exact palette match rule (same as the owner fill): filtering would
        blend lookup keys at province borders."""
        src = _read(SCENES / "map_renderer_base.gd")
        block = src.split("_highlight_material = null", 1)[1][:900]
        assert "TEXTURE_FILTER_NEAREST" in block

    def test_hover_refresh_is_a_uniform_write_in_bitmap_mode(self):
        src = _read(SCENES / "map_renderer_base.gd")
        refresh = src.split("func _refresh_highlight_texture", 1)[1]
        refresh = refresh.split("\nfunc ", 1)[0]
        assert 'set_shader_parameter("hover_key"' in refresh
        # The CPU circle path survives as the legacy-fixture fallback ONLY —
        # it must sit after the shader-material early return.
        assert refresh.index("set_shader_parameter") < refresh.index(
            "_draw_circle_on_image"
        )

    def test_selection_api_and_pulse(self):
        src = _read(SCENES / "map_renderer_base.gd")
        assert "func set_selected_region" in src
        assert "selected_region" in src
        assert 'set_shader_parameter("selected_boost", 1.0)' in src

    def test_pointing_hand_cursor_for_wired_provinces(self):
        src = _read(SCENES / "map_renderer_base.gd")
        assert "CURSOR_POINTING_HAND" in src
        assert "_is_region_wired(hovered_region)" in src


class TestDismissLadder:
    def test_map_emits_dismiss_on_right_click_and_open_water(self):
        src = _read(SCENES / "map_renderer_base.gd")
        assert "signal map_dismiss_requested" in src
        assert "MOUSE_BUTTON_RIGHT" in src
        # Both the sea-click else-branch and right-click emit it.
        assert src.count("map_dismiss_requested.emit()") >= 2

    def test_main_connects_dismiss_and_clears_selection(self):
        src = _read(SCRIPTS / "main.gd")
        assert "map_dismiss_requested.connect(_on_map_dismiss_requested)" in src
        assert "func _on_region_panel_closed" in src
        assert 'map_area.set_selected_region("")' in src

    def test_click_selects_and_reclick_toggles(self):
        src = _read(SCRIPTS / "main.gd")
        handler = src.split("func _on_map_region_clicked", 1)[1]
        handler = handler.split("\nfunc ", 1)[0]
        assert "set_selected_region(region_name)" in handler
        assert "current_region()" in handler

    def test_escape_closes_panel_before_pause(self):
        src = _read(SCRIPTS / "main.gd")
        esc = src.split("KEY_ESCAPE:", 2)[2]
        panel_close = esc.index("region_panel.close_panel()")
        pause_open = esc.index("pause_menu.open_menu()")
        assert panel_close < pause_open

    def test_panel_exposes_current_region(self):
        assert "func current_region" in _read(SCRIPTS / "region_panel.gd")


class TestReviewFixes:
    """Four confirmed findings from the pre-commit adversarial review
    (3 lenses -> per-finding refutation agents), all fixed in-session."""

    def test_esc_never_closes_panel_under_a_modal(self):
        """Finding 2: with the pause menu (a registered modal, layer 120)
        open over the panel, the first ESC closed the INVISIBLE panel and
        appeared to do nothing. The rung is now modal-gated."""
        src = _read(SCRIPTS / "main.gd")
        esc = src.split("KEY_ESCAPE:", 2)[2]
        idx = esc.index("region_panel.close_panel()")
        guard = esc[:idx]
        assert "region_panel.visible and not _is_modal_dialog_open()" in guard

    def test_avoid_control_refits_on_terminal_move(self):
        """Finding 1: grip-drag/reset/minimize/restore move the terminal
        WITHOUT a viewport resize — the panel must refit off the avoided
        control's own signals or its clamp goes stale."""
        src = _read(SCRIPTS / "region_panel.gd")
        assert "item_rect_changed.connect(_on_avoid_control_changed)" in src
        assert "visibility_changed.connect(_on_avoid_control_changed)" in src
        assert "func _on_avoid_control_changed" in src

    def test_world_swap_closes_panel_properly(self):
        """Finding 3: dialog_manager.hide_all() raw-hides the panel without
        emitting `closed`, stranding the old campaign's selection glow on
        the freshly loaded world. The swap now close_panel()s first."""
        src = _read(SCRIPTS / "main.gd")
        swap = src.split("func _reset_frontend_state_for_world_swap", 1)[1]
        swap = swap.split("\nfunc ", 1)[0]
        assert "region_panel.close_panel()" in swap
        assert swap.index("region_panel.close_panel()") < swap.index(
            "dialog_manager.hide_all()"
        )

    def test_no_select_or_dismiss_mid_pan(self):
        """Finding 4: while middle-button panning, _should_handle bypasses
        the hovered-control guard — clicks must not select/dismiss through
        overlying UI. Both pressed branches early-return on is_panning."""
        src = _read(SCENES / "map_renderer_base.gd")
        left = src.split("elif event.button_index == MOUSE_BUTTON_LEFT:", 1)[1]
        left_branch = left.split("elif event.button_index ==", 1)[0]
        assert "if is_panning:" in left_branch
        right = src.split("elif event.button_index == MOUSE_BUTTON_RIGHT:", 1)[1]
        right_branch = right.split("\n\t\telif", 1)[0].split("\n\tif ", 1)[0]
        assert "if is_panning:" in right_branch
