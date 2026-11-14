"""Session UI-6 (November 13, 2026) — the command desk's three forms (builder I1, the HUD).

The blind readers' UI-5 final reading, verbatim in the plan: at 1600 x 900 "the command
card is cramped, an empty gap sits above the prompt", "a dim text block with a stray
rule"; at Interface Scale 2.0 "the command card covers a third of the map, the war chip
and map controls overlap map labels"; on 32:9 "the tiny HUD is stranded in the corners".
One window, three forms (`main._desk_mode`): the DESK (folded: one line of figures, the
marshal row, the log on the line, the send glyph, "⚖ Cabinet"), the slim BAR on the
compact view (its log a drawer that opens upward) and the COLUMN on a very wide view
(`Utils.hud_columns`: the desk the left column, the rail and the war list the right,
the map in the gap). Plan: C:/Users/User/.claude/plans/starry-zooming-stearns.md §4.

Source pins and Python mirrors of the arithmetic only — nothing here launches the
engine; the driven half rides tools/uxr2_grip_harness.gd (tests/test_uxr2b_hud_band.py)
and the lead's engine lane.
"""
from __future__ import annotations

import math
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROJECT = REPO / "godot-client" / "project-sovereign"
SCRIPTS = PROJECT / "scripts"
SCENES = PROJECT / "scenes"
TOOLS = REPO / "tools"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def _func(src: str, name: str) -> str:
    """One GDScript function, from its `func` line to the next top-level func."""
    m = re.search(r"(?m)^(?:static )?func %s\(" % re.escape(name), src)
    assert m, f"func {name} is gone"
    rest = src[m.end():]
    nxt = re.search(r"(?m)^(?:static )?func ", rest)
    return src[m.start():m.end() + (nxt.start() if nxt else len(rest))]


def _code(src: str) -> str:
    """The script with whole-line comments and docstrings dropped."""
    out, in_doc = [], False
    for line in src.split("\n"):
        s = line.strip()
        if in_doc:
            if s.endswith('"""'):
                in_doc = False
            continue
        if s.startswith('"""'):
            if not (len(s) > 3 and s.endswith('"""')):
                in_doc = True
            continue
        if s.startswith("#"):
            continue
        out.append(line)
    return "\n".join(out)


def _const(src: str, name: str) -> float:
    m = re.search(r"(?m)^const %s := (-?[0-9.]+)" % re.escape(name), src)
    assert m, name
    return float(m.group(1))


MAIN = _read(SCRIPTS / "main.gd")
ROW = _read(SCRIPTS / "marshal_chip_row.gd")
UTILS = _read(SCRIPTS / "utils.gd")
SETTINGS = _read(SCRIPTS / "ui_settings.gd")
WAR = _read(SCRIPTS / "war_status_panel.gd")
TOP = _read(SCRIPTS / "top_bar.gd")
RAIL = _read(SCRIPTS / "notification_bar.gd")
SCENE = _read(SCENES / "main.tscn")
OR_PICK = re.compile(r"\b(str|int|float)\([^()]*\.get\([^()]*\)[^()]* or ")


# ═══════════════════════════════════════════════════════════════════════════
# The marshal row — a component (scripts/marshal_chip_row.gd)
# ═══════════════════════════════════════════════════════════════════════════
class TestTheMarshalRowComponent:
    def test_it_is_a_control_with_the_contract_the_host_wires(self):
        assert ROW.startswith("extends Control\nclass_name MarshalChipRow")
        for sig in ("signal marshal_pressed(key: String)", "signal marshal_double_pressed(key: String)",
                    "signal more_pressed()", "signal idle_pressed()"):
            assert sig in ROW, sig
        for api in ("func set_mode(mode: String) -> void:", "func set_rows(rows: Array) -> void:",
                    "func set_selected(key: String) -> void:"):
            assert api in ROW, api

    def test_three_forms(self):
        assert 'const MODES := ["row", "grid", "idle"]' in ROW
        assert "const GRID_ROWS := 6" in ROW and "const GRID_COLUMNS := 2" in ROW
        assert '"● %d idle" % n' in _func(ROW, "_make_idle_chip")
        assert '_more.text = "+%d" % hidden' in _func(ROW, "_place_more")
        # the idle chip stands only while someone is idle
        rebuild = _func(ROW, "_rebuild")
        assert "if n > 0:" in rebuild and "_idle_chip = _make_idle_chip(n)" in rebuild

    def test_the_idle_stand_first_and_wear_gilt(self):
        first = _func(ROW, "_idle_first")
        assert "return idle + busy" in first
        dress = _func(ROW, "_dress")
        assert "if idle:" in dress and "rim = Color(Utils.UI_GOLD, 0.9)" in dress
        assert "ink = Utils.UI_GOLD_BRIGHT" in dress
        # the selected marshal wears the bright rim
        assert 'if key != "" and key == _selected:' in dress and "width = 2" in dress

    def test_each_chip_a_likeness_a_name_and_his_state(self):
        assert 'const MarshalKit := preload("res://scripts/marshal_state.gd")' in ROW
        like = _func(ROW, "_likeness")
        assert "MarshalKit.portrait_path(key)" in like and "MarshalKit.monogram(key)" in like
        chip = _func(ROW, "_make_chip")
        assert "Utils.display_marshal_name(key)" in chip
        mark = _func(ROW, "_state_mark")
        assert "Utils.glyph(glyph_name)" in mark and "g.modulate = _tone(st)" in mark
        # the idle wear the gilt dot (the kit's glyph is "" for idle)
        assert 'if glyph_name == "":' in mark and "sb.bg_color = Utils.UI_GOLD_BRIGHT" in mark

    def test_no_chip_takes_the_keyboard(self):
        code = _code(ROW)
        assert code.count("focus_mode = Control.FOCUS_NONE") >= 4   # the row, a chip, "+N", the idle chip
        assert "grab_focus" not in code

    def test_the_row_can_never_widen_the_window(self):
        """Laid out by hand: its minimum width is the "+N" chip's, whatever the
        number of marshals — the chips that do not fit become "+N"."""
        lay = _func(ROW, "_layout_row")
        assert "custom_minimum_size = Vector2(_more_width(_chips.size()), ROW_H)" in lay
        assert "while shown < _chips.size() and used + float(widths[shown]) + GAP + more_w <= room:" in lay
        grid = _func(ROW, "_layout_grid")
        assert "var shown := n if n <= cap else cap - 1" in grid

    def test_a_double_click_selects_once_and_opens(self):
        gui = _func(ROW, "_on_chip_gui_input")
        assert "if mb.double_click:" in gui and "marshal_double_pressed.emit(key)" in gui
        assert '_hush = key' in gui
        pressed = _func(ROW, "_on_chip_pressed")
        assert "if _hush == key:" in pressed and "marshal_pressed.emit(key)" in pressed

    def test_a_refresh_that_changes_nothing_rebuilds_nothing(self):
        body = _func(ROW, "set_rows")
        assert "if sig == _signature:\n\t\treturn" in body

    def test_the_house_rules(self):
        code = _code(ROW)
        assert not OR_PICK.search(code), "GDScript's `or` answers a bool"
        assert "add_theme_font_size_override" not in code and "[font_size=" not in code
        # only tutorial_overlay.gd may read the command window (S14G-X66's census)
        assert not re.search(r"BottomLeftUI|bottom_left_ui", code)
        assert not re.search(r'Color\.html\("#[0-9a-fA-F]', code), "colours from Utils tokens"


class TestTheRowIsWired:
    def test_loaded_by_path_and_its_signals_routed(self):
        assert 'const MarshalChipRowScript := preload("res://scripts/marshal_chip_row.gd")' in MAIN
        build = _func(MAIN, "_ui6_build_desk")
        assert "_marshal_row = MarshalChipRowScript.new()" in build
        for wire in ("_marshal_row.marshal_pressed.connect(_on_marshal_chip_pressed)",
                     "_marshal_row.marshal_double_pressed.connect(_on_marshal_chip_opened)",
                     "_marshal_row.more_pressed.connect(_on_marshal_row_more)",
                     "_marshal_row.idle_pressed.connect(_on_marshal_row_idle)"):
            assert wire in build, wire

    def test_the_rows_are_our_field_marshals_through_the_kit(self):
        rows = _func(MAIN, "_ui6_marshal_rows")
        assert 'const MarshalStateKit := preload("res://scripts/marshal_state.gd")' in MAIN
        assert "if not _own_field_marshal(k):" in rows
        assert "MarshalStateKit.from_board(_marshal_entry(k)" in rows
        assert "MarshalStateKit.status_of(view)" in rows
        # fog: the board's own `marshals` only — never the enemies' roster
        assert '_last_game_state.get("marshals", {})' in rows and "enemies" not in _code(rows)

    def test_a_new_board_and_every_selection_change_reach_it(self):
        assert "_ui6_refresh_marshal_row()" in _func(MAIN, "_remember_game_state")
        for fn in ("_select_marshal", "_clear_order_selection", "_set_order_group"):
            assert "_ui6_mark_selected()" in _func(MAIN, fn), fn
        assert "_marshal_row.set_selected(_order_marshal)" in _func(MAIN, "_ui6_mark_selected")

    def test_a_click_selects_him_on_an_empty_line_only(self):
        """RE-POINTED (Session UI-6 wave 2, the interaction): with a draft on the
        line the chip is CC-1's pen — it writes his name at the caret (as a
        Shift-click on his piece does) and returns; it still selects only on an
        empty line, and still sends nothing."""
        body = _func(MAIN, "_on_marshal_chip_pressed")
        assert ('if command_input.text.strip_edges() != "":\n\t\t_ui6_pen_writes_marshal(key)\n\t\treturn'
                in body)
        assert body.index("_ui6_pen_writes_marshal(key)") < body.index("_select_marshal(key)")
        assert "if not _order_input_ready() or not _own_field_marshal(key):" in body
        assert "_select_marshal(key)" in body and "map_area.focus_on_marshal(key)" in body
        pen = _func(MAIN, "_ui6_pen_writes_marshal")
        assert "_line_insert_name(shown, maxi(_click_name_plan(shown), 0), false)" in pen
        # the click road — and the pen — send nothing
        for road in (body, pen):
            assert "send_command" not in road and "_execute_command" not in road

    def test_more_opens_the_generals_and_idle_is_the_dot_key(self):
        assert "_ui6_open_generals()" in _func(MAIN, "_on_marshal_row_more")
        assert "_ui6_open_generals()" in _func(MAIN, "_on_marshal_chip_opened")
        assert "_cycle_idle_marshal()" in _func(MAIN, "_on_marshal_row_idle")
        gen = _func(MAIN, "_ui6_open_generals")
        assert 'top_bar.toggle_screen("generals")' in gen
        assert 'top_bar.get_active_screen() != "generals"' in gen
        # no new close site (the Side Desk's census classifies every one)
        assert "close_all_screens" not in gen and "close_everything" not in gen

    def test_it_sits_under_the_header_and_moves_with_the_form(self):
        seat = _func(MAIN, "_ui6_seat_marshal_row")
        assert '_marshal_row.set_mode("idle")' in seat
        assert '_marshal_row.set_mode("grid" if mode == "column" else "row")' in seat
        assert "_marshal_row.reparent(_bar_row, false)" in seat and "_marshal_row.reparent(layout, false)" in seat


# ═══════════════════════════════════════════════════════════════════════════
# The three forms
# ═══════════════════════════════════════════════════════════════════════════
class TestTheThreeForms:
    def test_one_switch_decides_the_form(self):
        mode = _func(MAIN, "_desk_mode")
        assert 'if Utils.compact_view():\n\t\treturn "bar"' in mode
        assert 'if Utils.hud_columns(size).x > 0.0:\n\t\treturn "column"' in mode
        assert 'return "desk"' in mode
        relayout = _func(MAIN, "_relayout_terminal")
        assert relayout.index("var mode := _desk_mode()") < relayout.index("_ui6_apply_desk_mode(mode)")

    def test_the_pinned_lines_of_the_hub_stand(self):
        relayout = _func(MAIN, "_relayout_terminal")
        for line in ("_hud_room().x - TERMINAL_ANCHOR_LEFT * 2.0",
                     "TOP_BAR_RESERVED_PX - Utils.top_bar_growth()",
                     'war_status_panel.call_deferred("_fit_panel_to_content")'):
            assert line in relayout, line
        assert relayout.index("_log_floor()") < relayout.index("_fold_header()")
        # the fractions and the default footprint are untouched (their pins hold)
        assert "const TERMINAL_WIDTH_FRACTION := 0.28" in SETTINGS
        assert "const TERMINAL_HEIGHT_FRACTION := 0.32" in SETTINGS
        assert MAIN.count("UiSettings.default_terminal_size(_hud_size_room())") == 3

    def test_the_bar_is_a_share_of_the_width_and_its_own_height(self):
        assert _const(MAIN, "BAR_MAX_WIDTH") == 560.0 and _const(MAIN, "BAR_WIDTH_SHARE") == 0.70
        relayout = _func(MAIN, "_relayout_terminal")
        assert "disp_w = minf(BAR_MAX_WIDTH, floorf(size.x * BAR_WIDTH_SHARE))" in relayout
        assert "disp_h = 0.0" in relayout          # the frame grows upward to its minimum
        assert 'grow_vertical = 0' in G_node_block("BottomLeftUI")
        # 800 x 450 (Interface Scale 2.0 on 1600 x 900): a 560-px bar
        assert min(560.0, math.floor(800 * 0.70)) == 560.0

    def test_the_column_is_the_left_column(self):
        relayout = _func(MAIN, "_relayout_terminal")
        assert "disp_w = maxf(Utils.hud_columns(size).x - TERMINAL_ANCHOR_LEFT - Utils.HUD_MARGIN," in relayout
        assert "disp_h = maxf(size.y + TERMINAL_ANCHOR_BOTTOM - _ui6_column_top(), UiSettings.MIN_TERMINAL_HEIGHT)" in relayout
        assert "TOP_BAR_RESERVED_PX + Utils.top_bar_growth() + Utils.HUD_MARGIN" in _func(MAIN, "_ui6_column_top")
        left = _func(MAIN, "_terminal_left")
        assert "Utils.hud_band_full(size).x + TERMINAL_ANCHOR_LEFT" in left

    def test_the_parts_of_each_form(self):
        apply = _func(MAIN, "_ui6_apply_desk_mode")
        for line in ("header.visible = not bar", "diplomacy_button.visible = not bar",
                     "_more_button.visible = bar", "_bar_row.visible = bar",
                     "_map_mode_chip.visible = not bar", "output_scroll.visible = (not bar) or _ui5_log_open"):
            assert line in apply, line
        assert "_ui6_seat_marshal_row(mode)" in apply

    def test_only_the_desk_has_a_grip_and_raises(self):
        assert 'resize_grip.visible = bottom_left_ui.visible and _desk_mode_now == "desk"' in _func(
            MAIN, "_position_resize_grip")
        tall = _func(MAIN, "_hold_tall_reply")
        assert 'if _desk_mode_now == "bar" or _desk_mode_now == "column":\n\t\treturn _ui6_hold_reply(reply_h)' in tall
        assert tall.index("_ui6_hold_reply(reply_h)") < tall.index("_apply_terminal_size(")
        hold = _func(MAIN, "_ui6_hold_reply")
        assert "_apply_terminal_size" not in hold and "MAX_TERMINAL_HEIGHT" not in hold
        assert "_reply_held = false" in _func(MAIN, "_end_reply")

    def test_the_readback_row_has_room(self):
        """Wave 2 adds `ReadbackRow` above the line in the window's own VBox: the
        desk's height is a floor the panel grows past (grow_vertical BEGIN), the
        bar's its own minimum — an extra row raises either, never clips."""
        assert "disp_h = 0.0" in _func(MAIN, "_relayout_terminal")
        assert "layout.add_child(_suggestion_row)" in _func(MAIN, "_install_suggestion_row")


def G_node_block(name: str) -> str:
    m = re.search(r'^\[node name="%s"[^\]]*\]\n(.*?)(?=^\[node |\Z)' % re.escape(name), SCENE, re.M | re.S)
    assert m, name
    return m.group(1)


# ═══════════════════════════════════════════════════════════════════════════
# The bar: its second row, the drawer, ⋯
# ═══════════════════════════════════════════════════════════════════════════
class TestTheBar:
    def test_the_log_is_an_explicit_drawer(self):
        assert "var _ui5_log_open := false" in MAIN
        assert "floorf(size.y * BAR_LOG_SHARE)" in _func(MAIN, "_ui6_bar_log_height")
        assert _const(MAIN, "BAR_LOG_SHARE") == 0.40
        opener = _func(MAIN, "_ui5_open_log")
        assert 'if _desk_mode_now != "bar" or _ui5_log_open:' in opener and "_relayout_terminal()" in opener
        assert "_ui5_log_open = false" in _func(MAIN, "_ui5_close_log")

    def test_it_folds_on_a_send_on_esc_and_on_a_press_outside(self):
        for fn in ("_execute_command", "_retire_line_latches", "_reset_frontend_state_for_world_swap",
                   "_escape_closes_topmost"):
            assert "_ui5_close_log()" in _func(MAIN, fn), fn
        ladder = _func(MAIN, "_escape_closes_topmost")
        assert (ladder.index("top_bar.close_all_screens()") < ladder.index("_ui5_close_log()")
                < ladder.index("if include_selection and _order_engaged()"))
        assert "_ui6_press_outside_folds_the_log(event)" in _func(MAIN, "_input")
        outside = _func(MAIN, "_ui6_press_outside_folds_the_log")
        assert "mb.button_index != MOUSE_BUTTON_LEFT" in outside and "desk.has_point(mb.position)" in outside
        assert "set_input_as_handled" not in outside and "accept_event" not in outside

    def test_a_reply_of_more_than_a_line_opens_it_once(self):
        assert _const(MAIN, "BAR_REPLY_LINES") == 2
        hold = _func(MAIN, "_ui6_hold_reply")
        assert "if _reply_held or _reply_line_count < BAR_REPLY_LINES:" in hold
        assert "_ui5_open_log(false)" in hold
        assert "_reply_line_count = 0" in _func(MAIN, "_begin_reply")
        note = _func(MAIN, "_ui6_note_log_line")
        assert "_reply_line_count += 1" in note and "Utils.bb_plain(text)" in note
        # the greeting's folded link leaves the reply line ("▸ every c…" ran it out);
        # a link's words are joined by no-break spaces in the log, so they are
        # normalised before the trim (the dry-run shoot still read the cut link)
        assert 'plain.replace("\\u00A0", " ").trim_suffix("▸ every command")' in note
        add = _func(MAIN, "add_output")
        assert add.index("_ui6_note_log_line(text)") < add.index("await get_tree().process_frame")

    def test_the_second_row_carries_the_turn_and_the_days_pools(self):
        figures = _func(MAIN, "_ui6_bar_figures_bbcode")
        assert '"]T" + str(int(current_turn))' in figures
        assert 'Utils.bb_glyph("actions", 16, a_hex)' in figures and 'Utils.bb_glyph("admin", 16, m_hex)' in figures
        assert "str(int(actions_remaining))" in figures and "str(int(max_admin_actions))" in figures
        assert "_ui6_refresh_bar()" in _func(MAIN, "_update_status")
        build = _func(MAIN, "_ui6_build_desk")
        assert '_bar_row.name = "BarStatusRow"' in build and '_bar_reply.name = "ReplyLine"' in build
        assert "_bar_reply.pressed.connect(_ui6_toggle_log)" in build
        assert "_bar_reply.focus_mode = Control.FOCUS_NONE" in build

    def test_the_menu_calls_each_controls_own_handler(self):
        menu = _func(MAIN, "_ui6_on_more_menu")
        for call in ("_on_diplomacy_button_pressed()", "_step_ui_scale(1)", "_step_ui_scale(-1)",
                     "_on_map_mode_chip_pressed()", "_print_boot_help(true)", "_ui6_toggle_log()",
                     "_minimize_terminal()"):
            assert call in menu, call
        fill = _func(MAIN, "_ui6_fill_more_menu")
        assert "menu.set_item_disabled(at, bool(diplomacy_button.disabled))" in fill
        build = _func(MAIN, "_ui6_build_desk")
        assert "_more_button.focus_mode = Control.FOCUS_NONE" in build
        assert "_more_button.about_to_popup.connect(_ui6_fill_more_menu)" in build

    def test_the_selection_strip_stands_over_the_bar(self):
        strip = _func(MAIN, "_fit_order_strip")
        assert "if _ui5_bar_mode() and desk.size.x > 0.0:" in strip
        assert "bottom = desk.position.y - Utils.HUD_MARGIN" in strip
        # S14G-X66: the strip still reads only the window's right edge literally
        assert "bottom_left_ui.get_global_rect().end.x + Utils.HUD_MARGIN" in strip


# ═══════════════════════════════════════════════════════════════════════════
# The columns on a very wide view (utils.gd, ui_settings.gd, the right column)
# ═══════════════════════════════════════════════════════════════════════════
def _columns(vx: float, vy: float, hud: str = "auto", wide: str = "fill", dock: float = 0.0):
    """A Python mirror of `Utils.hud_columns`, over the constants parsed from the source."""
    if vy < _const(UTILS, "COMPACT_BELOW") or vx / vy < _const(SETTINGS, "SAFE_ZONE_ASPECT"):
        return 0.0, 0.0
    if hud != "auto" or wide != "fill":
        return 0.0, 0.0
    lo, hi = _const(SETTINGS, "COLUMN_LEFT_MIN"), _const(SETTINGS, "COLUMN_LEFT_MAX")
    left = math.floor(min(max(vx * _const(SETTINGS, "COLUMN_LEFT_FRACTION"), lo), hi))
    right = 0.0
    if dock <= 0.0:
        lo, hi = _const(SETTINGS, "COLUMN_RIGHT_MIN"), _const(SETTINGS, "COLUMN_RIGHT_MAX")
        right = math.floor(min(max(vx * _const(SETTINGS, "COLUMN_RIGHT_FRACTION"), lo), hi))
    return float(left), float(right)


class TestTheColumns:
    def test_the_constants(self):
        for name, value in (("COLUMN_LEFT_FRACTION", 0.17), ("COLUMN_LEFT_MIN", 420.0), ("COLUMN_LEFT_MAX", 560.0),
                            ("COLUMN_RIGHT_FRACTION", 0.15), ("COLUMN_RIGHT_MIN", 380.0),
                            ("COLUMN_RIGHT_MAX", 480.0)):
            assert _const(SETTINGS, name) == value, name
        # HUD width keeps its four choices: Full is the corner escape (UI-4)
        assert 'const HUD_WIDTHS := ["auto", "full", "16:9", "centred"]' in SETTINGS

    def test_the_trigger(self):
        body = _func(UTILS, "hud_columns")
        assert "view.y < COMPACT_BELOW or not very_wide_view(view)" in body
        assert 'UiSettings.get_hud_width() != "auto" or UiSettings.get_wide_map() != "fill"' in body
        assert "if _dock_width <= 0.0:" in body       # a pinned Side Desk dissolves the right column
        assert "const HUD_COLUMNS_ACTIVE := true" in UTILS

    def test_the_users_panel_and_the_ordinary_screens(self):
        # 5120 x 1440 at the derived 1.80 -> 2844 x 800: L 483, R 426 (the rail's and
        # the war list's width at the top right). The interim blind reading (Nov 13)
        # collapsed the right column: the map's room is 2844 - 483 = 2361 x 800
        left, right = _columns(2844.0, 800.0)
        assert (left, right) == (483.0, 426.0)
        room = 2844.0 - left
        assert room == 2361.0
        # 2.95 : 1 — over the map's 2.2 for an inset room: the sheet fills its width
        assert room / 800.0 >= 2.2
        # the harness's own 5120 x 1440 at 1.4 (3657 x 1029): both columns at their ceilings
        assert _columns(3657.0, 1029.0) == (560.0, 480.0)
        # 1600 x 900 at 1.0 and at 2.0, a 21:9 screen, the compact 32:9: no columns
        for view in ((1600.0, 900.0), (800.0, 450.0), (3440.0 / 1.15, 1440.0 / 1.15), (1969.0, 554.0)):
            assert _columns(*view) == (0.0, 0.0), view
        # Full / 16:9 / Centred and Auto + the whole sheet keep their bands
        for hud, wide in (("full", "fill"), ("16:9", "fill"), ("centred", "fill"), ("auto", "sheet")):
            assert _columns(2844.0, 800.0, hud, wide) == (0.0, 0.0), (hud, wide)
        # a pinned screen at the Side Desk: the left column stands, the right dissolves
        assert _columns(2844.0, 800.0, dock=474.0) == (483.0, 0.0)

    def test_the_band_is_the_gap_and_the_anchor_band_the_right_column(self):
        band = _func(UTILS, "hud_band")
        assert band.index("var band := hud_band_full(view)") < band.index("var cols := hud_columns(view)")
        # the interim blind reading (Nov 13): the right column is collapsed — the
        # band (the map's room) runs to the screen's edge; the rail and the war
        # list keep the column's width at its top (hud_anchor_band)
        assert "band.y -= cols.y" not in band
        assert band.index("band.x += cols.x") < band.index("band.y = maxf(band.x, band.y - _dock_width - HUD_MARGIN)")
        anchor = _func(UTILS, "hud_anchor_band")
        assert "if cols.y > 0.0:" in anchor and "Vector2(full.y - cols.y, full.y)" in anchor
        assert "return hud_band(view)" in anchor
        # the whole band, the dock and the sizing room are untouched
        assert "hud_columns" not in _func(UTILS, "hud_band_full")
        assert "hud_columns" not in _func(UTILS, "dock_rect")

    def test_the_map_fills_the_gap(self):
        inset = _func(MAIN, "_fit_map_inset")
        assert "inset = maxf(size.x - Utils.hud_band(size).y, 0.0)" in inset
        assert "if Utils.dock_width() > 0.0 or Utils.hud_columns(size).y > 0.0:" in inset
        assert 'if map_area.has_method("set_left_inset"):' in inset
        assert "map_area.set_left_inset(maxf(Utils.hud_band(size).x - Utils.hud_band_full(size).x, 0.0))" in inset

    def test_the_rail_and_the_war_list_fill_the_right_column(self):
        rail = _func(TOP, "_fit_rail")
        assert "var band := Utils.hud_anchor_band(view)" in rail
        assert "w = maxf(band.y - band.x - Utils.HUD_MARGIN - RAIL_RIGHT_INSET, RAIL_MIN_WIDTH)" in rail
        assert "Utils.fraction_px(" in rail      # the layout law's evidence (the other views)
        war = _func(WAR, "_apply_geometry")
        assert "var band := Utils.hud_anchor_band(view)" in war
        assert "w = room - 2.0 * EDGE_MARGIN" in war
        assert "if column or room < NARROW_BELOW_PX:" in war
        assert "Utils.fraction_px(room, WIDTH_FRACTION, DEFAULT_MIN_WIDTH, DEFAULT_MAX_WIDTH)" in war
        # at 2844 x 800: the rail and the list share the column's left edge, 8 px into it
        right = 426.0
        assert 2844.0 - _const(TOP, "RAIL_RIGHT_INSET") - (right - 8.0 - _const(TOP, "RAIL_RIGHT_INSET")) == 2844.0 - right + 8.0
        assert 2844.0 - _const(WAR, "EDGE_MARGIN") - (right - 2.0 * _const(WAR, "EDGE_MARGIN")) == 2844.0 - right + 8.0

    def test_the_busy_chip_stands_in_the_gap(self):
        chip = _func(MAIN, "_ui5_place_busy_chip")
        assert 'if _desk_mode_now == "column":' in chip
        assert "Utils.hud_band(size).x + Utils.HUD_MARGIN" in chip


# ═══════════════════════════════════════════════════════════════════════════
# The compact view's top-right corner (F03)
# ═══════════════════════════════════════════════════════════════════════════
class TestTheCornerAtTwoPointZero:
    def test_the_war_chip_is_its_own_width_under_the_bell(self):
        war = _func(WAR, "_apply_geometry")
        assert "w = panel_container.get_combined_minimum_size().x + CHIP_SLACK" in war
        assert "w = clampf(w, CHIP_MIN_WIDTH if chip else float(MIN_WIDTH)" in war
        assert "top = _under_the_rail()" in war
        under = _func(WAR, "_under_the_rail")
        assert "avoid_rail.get_global_rect().end.y + RAIL_CHIP_GAP" in under
        assert "war_status_panel.avoid_rail = notification_bar.rail_panel" in MAIN
        # the window's clearance is unchanged (its pinned floor line)
        assert ("var floor_w: float = float(MIN_WIDTH) if Utils.compact_view() "
                "else maxf(float(MIN_WIDTH), _content_need_width())") in _func(WAR, "_clear_the_command_window")

    def test_the_folded_rail_is_its_bell_at_the_slots_edge(self):
        assert "_seat_folded_rail(_is_folded())" in _func(RAIL, "_sync_fold")
        seat = _func(RAIL, "_seat_folded_rail")
        assert "rail_panel.anchor_left = 1.0 if folded else 0.0" in seat
        assert "Control.GROW_DIRECTION_BEGIN if folded else Control.GROW_DIRECTION_BOTH" in seat
        assert "words.visible = not folded" in seat
        assert "return rail_panel.get_global_rect()" in _func(RAIL, "rail_rect")

    def test_the_controls_stay_at_the_bars_right(self):
        fit = _func(MAIN, "_fit_map_controls")
        assert "bottom_left_ui.get_global_rect().end.x + Utils.HUD_MARGIN" in fit
        assert "var y := size.y - Utils.HUD_MARGIN - cs.y" in fit
        # only a war HUD that reaches the controls' row moves them
        assert "and hud.end.y > y - Utils.HUD_MARGIN:" in fit

    def test_the_labels_dodge_the_war_chip_and_the_rail(self):
        avoid = _func(MAIN, "_push_map_label_avoid_rects")
        assert "var war := _war_hud_rect()" in avoid and "rects.append(war)" in avoid
        assert "notification_bar.rail_rect()" in avoid
        assert "_ui6_on_rail_moved" in MAIN and "notification_bar.rail_panel.item_rect_changed.connect(_ui6_on_rail_moved)" in MAIN


# ═══════════════════════════════════════════════════════════════════════════
# The desk's words, folded and On the page
# ═══════════════════════════════════════════════════════════════════════════
def _thousands(n: int) -> str:
    """A Python mirror of `main._ui6_thousands` (Godot's round is half away from zero)."""
    a = abs(n)
    minus = "−" if n < 0 else ""
    if a >= 10000:
        return minus + str(int(math.floor(a / 1000.0 + 0.5))) + "k"
    if a >= 1000:
        k = round(a / 100.0) / 10.0
        return minus + (str(int(k)) if k == math.floor(k) else f"{k:.1f}") + "k"
    return minus + str(a)


class TestTheDesksWords:
    def test_folded_the_header_is_one_line_of_figures(self):
        relayout = _func(MAIN, "_relayout_terminal")
        assert 'var full_header := mode != "bar" and not Utils.explanations_folded()' in relayout
        assert "(gold_value.get_parent() as Control).visible = full_header" in relayout
        assert "(turn_value.get_parent() as Control).visible = full_header" in relayout
        dress = _func(MAIN, "_ui6_dress_status_row")
        assert "var keys_shown := not Utils.explanations_folded()" in dress
        for key in ("ActionsDisplay/ActionsLabel", "AdminDisplay/AdminLabel", "ManpowerDisplay/InfLabel",
                    "ManpowerDisplay/CavLabel", "ManpowerDisplay/ArtLabel"):
            assert key in dress, key
        tips = _func(MAIN, "_ui6_refresh_status_tips")
        assert "Military actions left today: %d of %d" in tips and "Levies in the depots" in tips
        # the turn stays the header's write (the top bar shows it; On the page the header does)
        assert "turn_value.text = str(int(current_turn))\n" in MAIN

    def test_folded_a_levy_reads_in_thousands(self):
        body = _func(MAIN, "_update_manpower_display")
        assert "inf_value.text = _levy_text(infantry_pool)" in body
        levy = _func(MAIN, "_levy_text")
        assert "if not Utils.explanations_folded():\n\t\treturn _format_number(n)" in levy
        cases = {80000: "80k", 15000: "15k", 10000: "10k", 7500: "7.5k", 1000: "1k", 900: "900", 0: "0",
                 12345: "12k"}
        for n, want in cases.items():
            assert _thousands(n) == want, (n, _thousands(n))
        assert 'return minus + str(roundi(float(a) / 1000.0)) + "k"' in _func(MAIN, "_ui6_thousands")

    def test_the_greeting_keeps_its_line_and_the_door_to_every_command(self):
        boot = _func(MAIN, "_print_boot_help")
        at = boot.index("if folded:")
        folded = boot[at:boot.index("return", at)]
        assert "Your marshals await your orders, Sire." in folded and "\u25b8\u00a0every\u00a0command" in folded
        assert "_add_separator()" not in folded and "or click one of your marshals" not in folded
        # On the page: the greeting and the whole list, every word, as before
        assert 'add_output("[color=#" + Utils.COLOR_INFO + "]Your marshals await your orders, Sire.[/color]")' in boot
        assert boot.index("Commands:") > at
        ph = _func(MAIN, "_refresh_command_placeholder")
        assert "elif Utils.explanations_folded():\n\t\tcommand_input.placeholder_text = COMMAND_PLACEHOLDER_EXAMPLE" in ph
        assert 'placeholder_text = "Type command..."' in SCENE   # the scene's own default

    def test_the_cabinet_reads_cabinet(self):
        assert 'const CABINET_FACE_SHORT := "⚖ Cabinet"' in MAIN
        assert 'const CABINET_SHUT_FACE_SHORT := "⚖ Cabinet — shut"' in MAIN
        assert 'text = "⚖ The Cabinet"' in SCENE   # the authored face (On the page) stays the scene's
        locked = _func(MAIN, "_set_cabinet_locked")
        assert locked.rstrip().endswith("_ui6_dress_cabinet()   # Session UI-6 (N7): folded, \"⚖ Cabinet\" (its shut face shortened too)")
        dress = _func(MAIN, "_ui6_dress_cabinet")
        assert "CABINET_SHUT_FACE_SHORT if _cabinet_locked else CABINET_FACE_SHORT" in dress
        assert "CABINET_SHUT_FACE if _cabinet_locked else _cabinet_face_default_text" in dress

    def test_execute_is_a_send_glyph_shown_with_an_order(self):
        dress = _func(MAIN, "_ui6_dress_send_button")
        assert "Utils.apply_icon_only_button(send_button, Utils.glyph(SEND_GLYPH))" in dress
        assert "send_button.text = _send_words" in dress
        assert 'const SEND_GLYPH := "letter"' in MAIN
        refresh = _func(MAIN, "_refresh_send_button")
        assert "Utils.set_available(send_button, _input_open and not empty" in refresh
        assert 'send_button.set_deferred("visible", shown)' in refresh
        assert 'text = "Execute"' in SCENE

    def test_the_log_stands_on_the_line(self):
        build = _func(MAIN, "_ui6_build_desk")
        assert 'if output_display != null and "vertical_alignment" in output_display:' in build
        assert 'output_display.set("vertical_alignment", VERTICAL_ALIGNMENT_BOTTOM)' in build
        assert "Utils.on_explanations_changed(_ui6_on_explanations_changed)" in build

    def test_the_house_rules_in_the_new_block(self):
        block = _code(MAIN[MAIN.index("SESSION UI-6 (November 13, 2026) — THE COMMAND DESK"):])
        assert not OR_PICK.search(block)
        assert "add_theme_font_size_override" not in block and "[font_size=" not in block
        assert not re.search(r'Color\.html\("#[0-9a-fA-F]', block)
        assert not re.search(r"\bUtils\.COLOR_(?:DIMMED|GREY|DIM)\b", block)


# ═══════════════════════════════════════════════════════════════════════════
# The offers: the shared head dim, each tail gold
# ═══════════════════════════════════════════════════════════════════════════
def _shared_head(offers: list[str], typed: str) -> str:
    """A Python mirror of `main._ui6_shared_offer_head`."""
    lines = [o.strip() for o in offers]
    if not lines:
        return ""
    head = lines[0]
    if len(lines) == 1:
        head = head[:len(typed)] if head.lower().startswith(typed.lower()) else ""
    else:
        for o in lines:
            n = 0
            while n < min(len(head), len(o)) and head[n] == o[n]:
                n += 1
            head = head[:n]
    cut = head.rfind(" ")
    return head[:cut + 1] if cut >= 0 else ""


class TestTheOffers:
    def test_the_links_and_the_lines_are_unchanged(self):
        render = _func(MAIN, "_render_suggestions")
        assert 'parts.append("[url=sugg:%d]%s[/url]" % [i, shown])' in render
        assert 'var hint := "(Tab)" if _suggestions.size() < 2 else "(Tab · ↓)"' in render
        assert 'mark = "↳ "' in render and 'mark = "↩ "' in render
        # the row takes the theme's font (the line's — CX3-R8 / UXR-2)
        assert "font" not in _code(_func(MAIN, "_install_suggestion_row")).replace("fit_content", "")

    def test_the_shared_head_dim_and_each_tail_gold(self):
        render = _func(MAIN, "_render_suggestions")
        assert "var shared := _ui6_shared_offer_head()" in render
        assert "shown = _ui6_dim(mark + head) + Utils.bbcode_color(tail, Utils.COLOR_GOLD)" in render
        assert "Utils.bbcode_color(tail, lit_hex)" in render     # the highlighted tail, the brightest
        assert "Utils.bbcode_color(text, Utils.COLOR_INFO)" in _func(MAIN, "_ui6_dim")

    def test_the_head_is_cut_to_a_whole_word(self):
        assert _shared_head(["Ney, attack Mack", "Ney, attack Deroy"], "Ney, at") == "Ney, attack "
        assert _shared_head(["Ney, attack Mack", "Ney, attack Murat"], "Ney, attack M") == "Ney, attack "
        assert _shared_head(["Ney, attack Mack"], "ney, att") == "Ney, "
        assert _shared_head(["Ney, ", "Davout, "], "") == ""
        assert _shared_head(["status"], "sta") == ""


# ═══════════════════════════════════════════════════════════════════════════
# The settings (wave 2 builds their rows), the turn at every scale, the harness
# ═══════════════════════════════════════════════════════════════════════════
class TestTheSettings:
    def test_next_marshal_after_an_order(self):
        assert 'get_value("orders", "next_marshal_after_order", not harness_active())' in _func(
            SETTINGS, "get_next_marshal_after_order")
        setter = _func(SETTINGS, "set_next_marshal_after_order")
        assert "static func set_next_marshal_after_order(on: bool) -> void:" in setter
        assert '_config().set_value("orders", "next_marshal_after_order", on)' in setter and "_save()" in setter

    def test_the_readback(self):
        assert 'get_value("display", "readback", not harness_active())' in _func(SETTINGS, "get_readback")
        setter = _func(SETTINGS, "set_readback")
        assert "static func set_readback(on: bool) -> void:" in setter
        assert '_config().set_value("display", "readback", on)' in setter and "_save()" in setter

    def test_reset_layout_keeps_them(self):
        body = _func(SETTINGS, "reset_layout")
        assert "readback" not in body and "next_marshal" not in body


def _turn_text(step: int, turn: int, label: str) -> str:
    """A Python mirror of `top_bar._render_turn_text`."""
    if label == "" or step >= 8:
        return "Turn " + str(turn)
    if step >= 7:
        words = label.split()
        return str(turn) + " · " + (" ".join(words[1:]) if len(words) >= 3 else label)
    if step >= 6:
        return str(turn) + " · " + label
    return label


class TestTheTurnAtEveryScale:
    def test_the_narrow_date_keeps_the_turn(self):
        turn = _func(TOP, "_render_turn_text")
        assert 'turn_label.text = str(_turn_number) + " · " + _calendar_label' in turn
        assert "_turn_figure.get_parent().visible = step < 6" in _func(TOP, "_apply_fit_step")
        assert _turn_text(7, 1, "Late September 1805") == "1 · September 1805"
        assert _turn_text(6, 1, "Late September 1805") == "1 · Late September 1805"
        assert _turn_text(8, 20, "Late September 1805") == "Turn 20"
        assert _turn_text(5, 1, "Late September 1805") == "Late September 1805"   # the hourglass's figure stands
        # the top bar never names the pools (rf4c's pin) — the bar's second row does
        assert "max_actions" not in TOP


class TestTheHarness:
    def test_the_grip_harness_reads_the_whole_band_and_the_gap(self):
        harness = _read(TOOLS / "uxr2_grip_harness.gd")
        body = harness[harness.index("func _band_measure():"):harness.index("func _band_restore():")]
        for key in ('"band_full": [full.x, full.y]', '"gap": [band.x, band.y]', '"columns": [cols.x, cols.y]',
                    '"desk_mode"'):
            assert key in body, key
