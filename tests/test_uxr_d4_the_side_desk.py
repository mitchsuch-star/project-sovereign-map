"""UXR-D4 "The Side Desk" — a layer-50 screen pinned NON-modal in the right
third, beside a live map (Pre-Deploy S12b, October 14, 2026).

The contract is `docs/DESIGN_REFINEMENT.md` UXR-D4 (ruled October 13, 2026
under the user's delegation: build it, non-modal). Every layer-50 screen —
the Strategic Ledger, the Generals, the dispatch, the campaign log, the
Gazette, the Diplomatic Ledger — carries a "Pin" chip by its close cross.
A pinned screen docks in the right third of the HUD band; the map, the
command line and the rail stay live; a decision popup (layer >= 100) still
blocks above it. One pinned screen at a time; Esc or Unpin closes it.

Slice 1 (the pin and the dock) is pinned here on the source. The driven
proof — a pinned ledger survives a command, a popup and an end turn beside a
live map — and the census join this file with Slices 2 and 3.
"""
from __future__ import annotations

import pathlib
import re

from tests import _godot_scenes as G

REPO = pathlib.Path(__file__).resolve().parents[1]
PROJECT = REPO / "godot-client" / "project-sovereign"
SCRIPTS = PROJECT / "scripts"
SCENES = PROJECT / "scenes"
SIX_SCREENS = ("strategic_ledger", "marshal_management", "dispatch_view", "campaign_log",
               "gazette_view", "diplomatic_ledger")


def _top() -> str:
    return G.read(SCRIPTS / "top_bar.gd")


class TestThePin:
    def test_every_screen_carries_the_pin_chip(self):
        top = _top()
        reg = G.func_body(top, "register_screen")
        assert "_attach_pin_chip(screen_name, node)" in reg
        chip = G.func_body(top, "_attach_pin_chip")
        assert 'node.get_node_or_null("PanelContainer/VBoxContainer/HeaderRow/CloseButton")' in chip
        assert 'chip.text = "Pin"' in chip
        assert "chip.tooltip_text = PIN_TOOLTIP" in chip
        assert 'chip.theme_type_variation = &"CaptionButton"' in chip
        assert "chip.focus_mode = Control.FOCUS_NONE" in chip
        assert "row.move_child(chip, close_btn.get_index())" in chip, "beside its close cross"
        assert ('const PIN_TOOLTIP := "Keep this screen open beside the map — Esc or Unpin closes it"'
                in top)
        # The six screens all hold the header row the chip is built into.
        for scene in SIX_SCREENS:
            tscn = G.read(SCENES / f"{scene}.tscn")
            assert '[node name="CloseButton" type="Button" parent="PanelContainer/VBoxContainer/HeaderRow"]' in tscn, scene
            assert '[node name="BackgroundOverlay"' in tscn, scene
        # The screens main.gd registers with the bar are exactly the six.
        main = G.read(SCRIPTS / "main.gd")
        for scene in SIX_SCREENS:
            assert f'"res://scenes/{scene}.tscn"]' in main, scene

    def test_one_pinned_screen_and_the_one_screen_rule(self):
        top = _top()
        assert 'var pinned_screen: String = ""' in top
        pin = G.func_body(top, "_pin")
        assert "if active_screen == screen_name:\n\t\tactive_screen = \"\"" in pin
        assert "pinned_screen = screen_name" in pin
        # Pinning hands the map back its mouse: screen_changed with "".
        assert pin.index('active_screen = ""') < pin.index("screen_changed.emit(active_screen)")
        # A pinned screen alone is not an open (modal) one.
        assert 'return active_screen != ""' in G.func_body(top, "is_screen_open")
        # Any OTHER screen opening unpins and closes it first.
        room = G.func_body(top, "_make_room_for")
        assert 'if pinned_screen != "" and pinned_screen != screen_name:' in room and "unpin()" in room
        for fn in ("_open_screen", "open_diplomatic_ledger_review", "open_ledger_to_tab"):
            assert "_make_room_for(screen_name)" in G.func_body(top, fn), fn
        # Its own key or button closes it, as it closes an open screen.
        toggle = G.func_body(top, "toggle_screen")
        assert toggle.index("if pinned_screen == screen_name:") < toggle.index("if active_screen == screen_name:")
        # Unpin closes it; its own cross leaves the desk.
        unpin = G.func_body(top, "unpin")
        assert "_set_docked(node, false)" in unpin and "_close_node(node)" in unpin
        closed = G.func_body(top, "_on_screen_closed")
        assert closed.index("if pinned_screen == screen_name:") < closed.index("if active_screen == screen_name:")

    def test_docked_the_screen_is_not_modal(self):
        top = _top()
        dock = G.func_body(top, "_set_docked")
        assert "overlay.visible = not on" in dock
        assert "Control.MOUSE_FILTER_IGNORE if on" in dock
        assert "(c as ResizeGrip).set_suppressed(on)" in dock
        assert '"Unpin" if on else "Pin"' in dock
        grip = G.read(SCRIPTS / "resize_grip.gd")
        assert "visible = _target.is_visible_in_tree() and not suppressed" in G.func_body(grip, "reposition")
        # Main gives the map back its mouse and panning on an empty active screen.
        main = G.read(SCRIPTS / "main.gd")
        changed = G.func_body(main, "_on_screen_changed")
        assert "map_area.mouse_filter = Control.MOUSE_FILTER_STOP" in changed
        assert "map_area.panning_enabled = true" in changed


class TestTheDock:
    def test_the_right_third_under_the_bar(self):
        utils = G.read(SCRIPTS / "utils.gd")
        assert "const DOCK_FRACTION := 1.0 / 3.0" in utils
        assert "const DOCK_MIN_FRACTION := 0.25" in utils
        assert "const DOCK_MAX_FRACTION := 0.5" in utils
        rect = G.func_body(utils, "dock_rect")
        assert "var band := hud_band_full(view)" in rect
        assert 'want = (panel.get_meta("clamp_user_size") as Vector2).x' in rect, "the remembered grip width"
        assert "clampf(want, bw * DOCK_MIN_FRACTION, bw * DOCK_MAX_FRACTION)" in rect
        assert "var top := TOP_BAR_HEIGHT + top_bar_growth() + HUD_MARGIN" in rect
        assert "var bottom := view.y - HUD_MARGIN" in rect
        assert "var right := band.y - HUD_MARGIN" in rect
        right = G.func_body(utils, "dock_right")
        assert "_relax_child_minimums(panel, r.size.y)" in right

    def test_the_hud_gives_the_dock_its_third(self):
        utils = G.read(SCRIPTS / "utils.gd")
        band = G.func_body(utils, "hud_band")
        assert "band.y = maxf(band.x, band.y - _dock_width - HUD_MARGIN)" in band
        top = _top()
        assert "_publish_dock(Utils.dock_right(panel))" in G.func_body(top, "_dock")
        assert "dock_changed.emit()" in G.func_body(top, "_publish_dock")
        assert "Utils.set_dock_width(0.0)" in G.func_body(top, "_exit_tree"), (
            "a war room torn down with a screen pinned leaves no dock behind")
        main = G.read(SCRIPTS / "main.gd")
        assert "top_bar.dock_changed.connect(_on_dock_changed)" in main
        assert 'call_deferred("_refit_hud_band")' in G.func_body(main, "_on_dock_changed")
        # A pinned screen re-docks on the one live-refit road.
        assert "_dock(screens[pinned_screen])" in G.func_body(top, "refit_active_screen")

    def test_the_map_keeps_to_the_room_left_of_the_dock(self):
        main = G.read(SCRIPTS / "main.gd")
        assert "_fit_map_inset()" in G.func_body(main, "_on_root_resized")
        inset = G.func_body(main, "_fit_map_inset")
        assert "inset = maxf(size.x - Utils.hud_band(size).y, 0.0)" in inset
        r = G.read(SCENES / "map_renderer_base.gd")
        assert "s.x = maxf(s.x - _inset_view_px(), 1.0)" in G.func_body(r, "_get_camera_viewport_size")
        assert ("map_camera.offset = Vector2(_inset_view_px() / 2.0 / maxf(_zoom_level, 0.001), 0.0)"
                in G.func_body(r, "_sync_camera_zoom"))
        assert "var viewport_center = _view_centre()" in G.func_body(r, "_zoom_at_point")
        assert "global_position + _view_centre()" in G.func_body(r, "zoom_step")
        setter = G.func_body(r, "set_right_inset")
        assert "var was_fit := is_fit_view()" in setter and "fit_europe()" in setter

    def test_no_hud_line_is_cut_beside_the_dock(self):
        war = G.read(SCRIPTS / "war_status_panel.gd")
        assert "w = maxf(w, _content_need_width())" in G.func_body(war, "_apply_geometry")
        main = G.read(SCRIPTS / "main.gd")
        assert 'call_deferred("_resnap_output")' in G.func_body(main, "_reposition_after_layout")
        resnap = G.func_body(main, "_resnap_output")
        assert "_output_pad.content_margin_bottom = 0.0" in resnap
        assert "await _snap_output_to_a_whole_line()" in resnap


SCREEN_FETCH = {
    "strategic_ledger": "get_ledger",
    "marshal_management": "get_marshal_overview",
    "diplomatic_ledger": "get_diplomatic_ledger",
    "dispatch_view": "get_dispatch",
    "gazette_view": "get_gazette",
    "campaign_log": "get_campaign_log",
}

# Slice 2: every close site in main.gd, by the one rule. A turn transition,
# a command, a popup or the mailbox keeps the pin (`close_all_screens`, the
# open screen only); the pause menu, a scene change, a load, a new campaign
# and the Fall unpin as well (`close_everything`). A new site must be
# classified here, or this census fails.
CLOSE_SITES = {
    "_unhandled_input": ["close_all_screens"],               # Esc: an open screen first
    "_show_pending_ending": ["close_everything",              # the Fall
                             "close_all_screens"],            # a marked ending: a card
    "_on_campaign_over": ["close_everything"],                # the Fall
    "_on_command_result": ["close_all_screens"],              # the enemy phase: a popup
    "_display_turn_change": ["close_all_screens"],            # a turn transition
    "_display_turn_advance": ["close_all_screens"],           # a turn transition
    "_reset_frontend_state_for_world_swap": ["close_everything"],   # a load, a new campaign
    "_on_top_bar_menu_clicked": ["close_everything"],         # the pause menu
    "_open_diplomacy_wizard": ["close_all_screens"],          # a popup (the wizard)
    "_on_ledger_open_diplomacy_for": ["close_all_screens"],   # a popup (the wizard)
    "_on_ledger_assess_requested": ["close_all_screens"],     # a command
    "_on_tutorial_open_cabinet": ["close_all_screens"],       # a popup (the wizard)
}


class TestItLivesThroughTheTurn:
    def test_every_screen_re_reads_its_current_book_and_keeps_its_scroll(self):
        for scene, fetch in SCREEN_FETCH.items():
            src = G.read(SCRIPTS / f"{scene}.gd")
            body = G.func_body(src, "refresh_pinned")
            assert f"_api_client_ref.{fetch}(" in body, scene
            assert "scroll_container.scroll_vertical" in body, (scene, "the scroll is held")
            # No tab reset, no scroll to the top.
            assert "current_tab =" not in body and "scroll_vertical = 0" not in body, scene
            callbacks = re.findall(r"func (_on_pinned_\w+)\(", src)
            assert len(callbacks) == 1, scene
            assert "Utils.restore_scroll(scroll_container, held_scroll)" in G.func_body(src, callbacks[0]), scene
        utils = G.read(SCRIPTS / "utils.gd")
        keep = G.func_body(utils, "restore_scroll")
        assert "await tree.process_frame" in keep and "scroll.scroll_vertical = value" in keep
        # The Gazette keeps the issue the reader holds; the log its folds.
        gazette = G.func_body(G.read(SCRIPTS / "gazette_view.gd"), "_on_pinned_gazette")
        assert "if not on_latest and held_index >= 0" in gazette
        log = G.func_body(G.read(SCRIPTS / "campaign_log.gd"), "_on_pinned_log")
        assert "_toggle_turn(int(turn_num))" in log

    def test_every_command_and_every_end_turn_re_read_the_desk(self):
        top = _top()
        assert "node.refresh_pinned()" in G.func_body(top, "refresh_pinned")
        main = G.read(SCRIPTS / "main.gd")
        result = G.func_body(main, "_on_command_result")
        assert result.index("_queue_pinned_refresh()") < result.index("_forget_unreadable_command(response)"), (
            "before any route can return early")
        tail = G.func_body(main, "_return_control_to_player")
        assert tail.index("_queue_pinned_refresh()") < tail.index("if _raise_pending_surfaces():")
        queue = G.func_body(main, "_queue_pinned_refresh")
        assert "if _pinned_refresh_queued" in queue and 'call_deferred("_refresh_pinned_now")' in queue
        assert "top_bar.refresh_pinned()" in G.func_body(main, "_refresh_pinned_now")
        # An objection's answer bypasses _on_command_result; it refreshes the
        # open info screens itself, the pinned ledger among them (visible).
        assert "_refresh_open_info_screens()" in G.func_body(main, "_on_objection_response")

    def test_every_close_site_is_classified(self):
        main = G.read(SCRIPTS / "main.gd")
        found: dict[str, list[str]] = {}
        current = ""
        for line in main.splitlines():
            m = re.match(r"(?:static )?func (\w+)\(", line)
            if m:
                current = m.group(1)
            for call in ("close_all_screens", "close_everything"):
                if re.search(r"\btop_bar\.%s\(\)" % call, line):
                    found.setdefault(current, []).append(call)
        assert found == CLOSE_SITES

    def test_the_pin_is_a_session_state(self):
        # Not saved, not restored on the next launch: nothing promises it.
        for path in (SCRIPTS / "ui_settings.gd", REPO / "backend" / "save_manager.py"):
            assert "pinned" not in G.read(path).lower(), path


class TestTheKeys:
    def test_esc_unpins_when_nothing_else_is_open(self):
        main = G.read(SCRIPTS / "main.gd")
        body = G.func_body(main, "_unhandled_input")
        esc = body[body.index("if event.keycode == KEY_ESCAPE:"):body.index("# Block all hotkeys while pause menu is open")]
        assert esc.index("region_panel.close_panel()") < esc.index("top_bar.unpin()") < esc.index("pause_menu.open_menu()")
        assert re.search(r"top_bar\.is_pinned\(\) \\\s*\n\s*and not _is_modal_dialog_open\(\)", esc)

    def test_the_war_room_leavers_unpin(self):
        main = G.read(SCRIPTS / "main.gd")
        assert "top_bar.close_everything()" in G.func_body(main, "_on_top_bar_menu_clicked")
        assert "top_bar.close_everything()" in G.func_body(main, "_reset_frontend_state_for_world_swap")
        assert "top_bar.close_everything()" in G.func_body(main, "_on_campaign_over")
        ending = G.func_body(main, "_show_pending_ending")
        assert 'if bool(payload.get("terminal", false)):\n\t\t\ttop_bar.close_everything()' in ending
