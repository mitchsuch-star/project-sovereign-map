"""Session UI-6 (November 13, 2026) — THE INTERACTION (wave 2, I2): the generals
and the command line, wired into main.gd.

The plan's analysis (C:/Users/User/.claude/plans/starry-zooming-stearns.md §2/§3):
a selected marshal got a two-line TEXT strip with no order buttons; the right
click only dismissed; a left click on a friend while one was selected opened a
SUPPORT card (a misclick could order one); the typed line could not be checked
before Enter; the persisted history could offer a fogged marshal's name.

What landed (each pinned below at its source; the behaviour is pinned DRIVEN in
tests/test_cc3_select_click_enter.py — k8/k13–k15/d6–d8 — and
tests/test_cx_readback_history_fog.py):
* the SELECTION CARD (scripts/selection_card.gd, loaded by path) in the strip's
  place — `order_strip_text()` keeps its contract; its verbs go down the chip
  road (`_on_reward_command`, the one in-flight latch); slot 7 the arrow card's
  cancel road; on 32:9 it docks at the foot of the right wing;
* DIGITS 1–7 press its fixed slots on an EMPTY line (N5);
* the RIGHT CLICK (`order_context_requested`) is the order with a corps
  selected; the LEFT click on another of ours picks him (N3);
* NEXT MARSHAL AFTER AN ORDER (N4) — On: the next idle marshal and the camera;
  Off (or a refusal, or the card's Cancel): him again; never after a typed line;
* the marshal row's pen, its double-click on the Generals' detail, the
  Generals' "On the map", the province panel's names, a toast for an order sent
  from behind a screen (decision 15);
* THE READBACK ROW (N6) — 220 ms rest, one ask in flight, stale drops, a cache,
  notes to the hover when folded, `fill:` chips that never send;
* UI6-X1 — the history offered and walked only where every word is on the board;
* the 32:9 right wing; the war detail suspends the notice rail; the order card
  capped at 0.9 of the band with its buttons whole; the grid's portraits 40 x 50.

Source pins only — nothing here launches the engine.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROJECT = REPO / "godot-client" / "project-sovereign"
SCRIPTS = PROJECT / "scripts"
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


MAIN = _read(SCRIPTS / "main.gd")
CARD = _read(SCRIPTS / "order_confirm_card.gd")
PANEL = _read(SCRIPTS / "region_panel.gd")
ROW = _read(SCRIPTS / "marshal_chip_row.gd")
HARNESS = _read(TOOLS / "cc_client_harness.gd")
READBACK_HARNESS = _read(TOOLS / "readback_harness.gd")
BLOCK = MAIN[MAIN.index("SESSION UI-6 (November 13, 2026) — THE INTERACTION"):]
OR_PICK = re.compile(r"\b(str|int|float)\([^()]*\.get\([^()]*\)[^()]* or ")


# ═══ the selection card ═════════════════════════════════════════════════════

class TestTheSelectionCard:
    def test_loaded_by_path_built_once_its_signals_routed(self):
        assert 'const SelectionCardScript := preload("res://scripts/selection_card.gd")' in MAIN
        assert MAIN.count("const MarshalStateKit :=") == 1 and MAIN.count("const MarshalChipRowScript :=") == 1
        build = _func(MAIN, "_ui6_build_selection_card")
        assert "_selection_card = SelectionCardScript.new()" in build
        for wire in ("_selection_card.verb_pressed.connect(_on_selection_verb)",
                     "_selection_card.cancel_order_pressed.connect(_on_selection_cancel)",
                     "_selection_card.close_pressed.connect(_clear_order_selection)",
                     "_selection_card.resized.connect(_queue_fit_map_controls)"):
            assert wire in build, wire
        # the wing first: the card draws over it
        assert build.index("_ui6_build_right_wing()") < build.index("SelectionCardScript.new()")
        ready = _func(MAIN, "_ready")
        assert ready.index("_build_order_strip()") < ready.index("_ui6_build_selection_card()")

    def test_it_shows_his_board_view_and_his_morale(self):
        show = _func(MAIN, "_ui6_show_selection_card")
        assert "MarshalStateKit.from_board(_marshal_entry(_order_marshal), row)" in show
        assert 'view["morale"] = int(row.get("morale", 0))' in show
        assert "_selection_card.show_for(view, _order_marshal, int(actions_remaining), hint)" in show
        assert "_selection_card.show_group(_order_group, _ui6_group_total(), int(actions_remaining), GROUP_CARD_HINT)" in show

    def test_the_strip_carries_the_words_and_the_card_shows_them(self):
        strip = _func(MAIN, "_show_order_strip")
        assert "_order_strip_label.text = text" in strip
        assert strip.index("_order_strip_label.text = text") < strip.index("_ui6_show_selection_card(text)")
        assert "if _hud_hidden or _ui6_show_selection_card(text):" in strip
        render = _func(MAIN, "_render_order_strip")
        assert "_ui6_hide_selection_card()" in render
        assert "var text := ORDER_STRIP_HINT" in render
        # (row PW — one click sends: the hint says what a click does now)
        assert ('const ORDER_STRIP_HINT := "Click a province to send him · an enemy to attack · '
                'right-click a marshal to support him · Esc lets him go"') in MAIN

    def test_order_strip_text_keeps_its_contract(self):
        body = _func(MAIN, "order_strip_text")
        assert "_ui6_selection_surface() == null" in body
        assert "return _order_strip_label.get_parsed_text()" in body
        surface = _func(MAIN, "_ui6_selection_surface")
        assert surface.index("_selection_card.visible") < surface.index("_order_strip.visible")

    def test_its_slot_the_strips_and_the_wings_foot_on_32_9(self):
        fit = _func(MAIN, "_fit_order_strip")
        assert "var surface: Control = _ui6_selection_surface()" in fit
        assert "if _ui6_dock_card_in_wing(surface):" in fit
        assert "surface.position = Vector2(x, maxf(top_floor, bottom - cs.y))" in fit
        # S14G-X66 / X64: the window's right edge, read literally and alone
        uses = re.findall(r"bottom_left_ui\.get_global_rect\(\)\.[a-z.]+", fit)
        assert uses and all(u.endswith(".end.x") for u in uses), uses
        dock = _func(MAIN, "_ui6_dock_card_in_wing")
        assert "surface.position = Vector2(x, wing.end.y - WING_PAD - cs.y)" in dock

    def test_the_labels_and_the_order_card_stand_clear_of_it(self):
        avoid = _func(MAIN, "_push_map_label_avoid_rects")
        assert "rects.append(_selection_card.get_global_rect())" in avoid
        assert "rects.append(_right_wing.get_global_rect())" in avoid
        assert "out.append(_selection_card.get_global_rect())" in _func(MAIN, "_order_card_avoid")

    def test_its_verbs_go_down_the_chip_road(self):
        verb = _func(MAIN, "_on_selection_verb")
        assert '_on_reward_command(marshal + ", " + verb)' in verb
        assert "_chip_command_in_flight" in verb and "_order_input_ready()" in verb
        assert verb.index("_card_sent_for = marshal") < verb.index("_on_reward_command(")
        assert "send_command" not in verb
        cancel = _func(MAIN, "_on_selection_cancel")
        assert "_send_cancel_order(marshal)" in cancel and "_card_sent_stays = true" in cancel
        # ONE cancel road (CC-X15) — the card adds no second sender
        assert MAIN.count("api_client.cancel_strategic_order(") == 1


# ═══ the digits (N5) ════════════════════════════════════════════════════════

class TestTheDigits:
    def test_the_gate(self):
        gate = _func(MAIN, "_ui6_digits_live")
        for clause in ('_order_marshal != ""', "_order_group.size() < 2",
                       'command_input.text.strip_edges() == ""', "_order_input_ready()",
                       "not _order_card_open()", "_selection_card.visible"):
            assert clause in gate, clause

    def test_the_digit_is_one_to_seven_fixed_never_shifted_or_echoed(self):
        digit = _func(MAIN, "_ui6_slot_digit")
        assert "event.echo" in digit and "event.shift_pressed" in digit and "event.ctrl_pressed" in digit
        assert "code >= KEY_1 and code <= KEY_7" in digit and "code >= KEY_KP_1 and code <= KEY_KP_7" in digit
        assert "event.physical_keycode" in digit
        # fixed: the digits are reserved, never remapped
        keys = _read(SCRIPTS / "keys.gd")
        assert "KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6, KEY_7" in keys

    def test_at_the_three_doors_of_the_period_key(self):
        line = _func(MAIN, "_on_command_input_gui_input")
        assert "elif not event.alt_pressed and _ui6_slot_digit(event) > 0 and _ui6_digits_live():" in line
        assert line.index("_cycle_idle_marshal()") < line.index("_ui6_slot_digit(event)")
        alt = _func(MAIN, "_alt_game_key")
        assert "KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6, KEY_7:" in alt
        assert "_ui6_press_slot(keycode - KEY_0)" in alt
        bare = _func(MAIN, "_unhandled_input")
        assert "elif _ui6_slot_digit(_raw_event) > 0 and _ui6_digits_live():" in bare
        assert bare.index("event.keycode == KEY_PERIOD") < bare.index("_ui6_slot_digit(_raw_event)")

    def test_the_card_plays_its_own_deny_cue(self):
        press = _func(MAIN, "_ui6_press_slot")
        assert "_selection_card.press_slot(n)" in press
        assert "AudioManager" not in press


# ═══ the right click and the left click on a friend (N3) ════════════════════

class TestTheClicks:
    def test_the_signal_is_connected_guarded(self):
        assert ('if map_area and map_area.has_signal("order_context_requested"):\n'
                '\t\tmap_area.order_context_requested.connect(_on_order_context_requested)') in MAIN

    def test_the_right_click_road(self):
        ctx = _func(MAIN, "_on_order_context_requested")
        assert "_order_click(region, marshal_key, true)" in ctx
        assert "_group_click(region)" in ctx
        assert 'if not drafting and marshal_key != "" and _click_selects_a_marshal():' in ctx
        assert _code(ctx).rstrip().endswith("_on_map_dismiss_requested()")
        # unchanged: the CC harness calls it directly
        dismiss = _func(MAIN, "_on_map_dismiss_requested")
        assert "_clear_order_selection()" in dismiss and "region_panel.close_panel()" in dismiss

    def test_the_left_click_on_a_friend_picks_him(self):
        key = _func(MAIN, "_order_target_key")
        assert "func _order_target_key(region: String, marshal_key: String, via_right := true) -> String:" in key
        assert 'return ("ally:" if via_right else "pick:") + marshal_key' in key
        click = _func(MAIN, "_order_click")
        assert "func _order_click(region: String, marshal_key: String, via_right := false) -> void:" in click
        assert 'if key.begins_with("pick:"):\n\t\t_select_marshal(key.substr(5))\n\t\treturn' in click
        # the left path takes the default (a pick); the drop keeps support
        assert "_order_click(region_name, _last_click_target_key())" in _func(MAIN, "_on_map_region_clicked")
        assert "_order_target_key(region, _last_click_target_key())" in _func(MAIN, "_on_piece_dropped")
        # Row FUN, FUN-1 (November 25, 2026), re-seated: the hover wears the
        # meaning of the gesture it previews — a plain hover the LEFT click's
        # (a pick: "Select <name>"), a dragged piece the drop's (support); it wore
        # the right click's, so its tag could promise a support the left click
        # never gave (driven: tests/test_fun1_the_hands.py).
        hover = _func(MAIN, "_on_map_order_hover")
        assert "_order_hover_key = _order_target_key(region, marshal_key, dragging)" in hover
        assert 'map_area.has_method("is_dragging_piece")' in hover


# ═══ the next marshal after an order (N4) ═══════════════════════════════════

class TestTheNextMarshal:
    def test_the_three_answers_that_move_the_selection(self):
        for fn in ("_on_reward_command_result", "_on_map_order_result", "_on_cancel_order_result"):
            body = _func(MAIN, fn)
            assert "_ui6_order_answered(response)" in body, fn
            assert body.index("_on_command_result(response)") < body.index("_ui6_order_answered(response)"), fn
        send = _func(MAIN, "_send_map_order")
        assert send.index("_card_sent_for = _order_marshal") < send.index("_clear_order_selection()")

    def test_never_after_a_typed_line(self):
        typed = _func(MAIN, "_execute_command")
        assert '_card_sent_for = ""' in typed
        assert "_ui6_order_answered" not in _func(MAIN, "_on_command_result")
        assert '_card_sent_for = ""' in _func(MAIN, "_reset_frontend_state_for_world_swap")

    def test_on_the_next_idle_off_him_again(self):
        after = _func(MAIN, "_ui6_after_order")
        assert "if not stay and UiSettings.get_next_marshal_after_order():" in after
        assert "_select_marshal(nxt)" in after and "map_area.focus_on_marshal(nxt)" in after
        assert after.index("_ui6_next_idle_after(actor)") < after.index("_select_marshal(nxt)")
        assert 'if nxt == "":\n\t\t\treturn' in after                 # none idle: nothing moves
        assert _code(after).rstrip().endswith("_select_marshal(actor)")
        assert "_order_input_ready()" in after and 'command_input.text.strip_edges() != ""' in after
        nxt = _func(MAIN, "_ui6_next_idle_after")
        assert "_idle_marshals()" in nxt and "idle.erase(actor)" in nxt
        answered = _func(MAIN, "_ui6_order_answered")
        assert "_ui6_after_order.call_deferred(actor, stays or not took)" in answered

    def test_the_setting_defaults_off_since_the_first_playtest(self):
        """RE-SEATED (row PW, November 18, 2026): UI-6 shipped this ON for a
        player. The first playtest ("everything feels … disconnected"): every
        order's answer took the selection AND the camera to another corps, so
        the player never saw his order carried out — and with one click
        sending a move, the next click would have commanded a different
        marshal. The default is OFF; the switch stays in Settings."""
        settings = _read(SCRIPTS / "ui_settings.gd")
        assert '"next_marshal_after_order", false)' in settings
        assert '"next_marshal_after_order", not harness_active()' not in settings


# ═══ the marshal row, the Generals, the province panel, the toast ═══════════

class TestTheHandoffs:
    def test_the_rows_double_click_opens_his_detail(self):
        opened = _func(MAIN, "_on_marshal_chip_opened")
        assert 'generals.has_method("select_marshal")' in opened
        assert opened.index("generals.select_marshal(key)") < opened.index("_ui6_open_generals()")

    def test_the_generals_on_the_map(self):
        assert 'if instance.has_signal("locate_requested"):' in MAIN
        assert "instance.locate_requested.connect(_on_generals_locate_requested)" in MAIN
        locate = _func(MAIN, "_on_generals_locate_requested")
        assert 'if str(top_bar.get_active_screen()) == "generals":\n\t\ttop_bar.toggle_screen("generals")' in locate
        assert "_select_marshal(key)" in locate and "map_area.focus_on_marshal(key)" in locate
        # no new close site for the Side Desk's census (a pinned desk stays)
        assert "close_all_screens" not in locate and "close_everything" not in locate

    def test_the_province_panels_names(self):
        assert ('if region_panel.has_signal("marshal_select_requested"):\n'
                '\t\t\tregion_panel.marshal_select_requested.connect(_on_panel_marshal_select)') in MAIN
        sel = _func(MAIN, "_on_panel_marshal_select")
        assert "_own_field_marshal(marshal_name)" in sel and "_select_marshal(marshal_name)" in sel
        assert MAIN.count("region_panel.avoid_control = bottom_left_ui") == 1

    def test_an_order_from_behind_a_screen_toasts_its_answer(self):
        result = _func(MAIN, "_on_reward_command_result")
        assert "_ui6_toast_reply(response)" in result
        toast = _func(MAIN, "_ui6_toast_reply")
        assert "not _is_screen_open()" in toast
        assert 'ToastLayer.say(first, "command" if took else "threat")' in toast
        assert "Utils.bb_plain(" in toast and "TOAST_REPLY_MAX" in toast

    def test_the_rows_and_the_rails_order_of_the_pipeline_is_kept(self):
        """UX23-A's pin reads `_on_notification_action_requested` up to the next
        func, and `_on_reward_command` up to its result: nothing between them."""
        assert re.search(r"func _on_notification_action_requested\(command: String\):(?:(?!\nfunc ).)*"
                         r"\nfunc _on_reward_command\(command: String\):", MAIN, re.S)
        assert re.search(r"func _on_reward_command\(command: String\):(?:(?!\nfunc ).)*"
                         r"\nfunc _on_reward_command_result\(response\):", MAIN, re.S)


# ═══ the readback row (N6) ══════════════════════════════════════════════════

class TestTheReadback:
    def test_installed_beside_the_line_measured_no_font(self):
        assert "_ui6_install_readback_row(layout, input_row)" in _func(MAIN, "_install_suggestion_row")
        inst = _func(MAIN, "_ui6_install_readback_row")
        assert '_readback_row.name = "ReadbackRow"' in inst
        assert "layout.move_child(_readback_row, input_row.get_index())" in inst
        assert "_readback_row.fit_content = false" in inst
        assert "fit_content = true" not in inst and "font" not in _code(inst).replace("fit_content", "")
        assert "_readback_row.meta_clicked.connect(_on_readback_meta_clicked)" in inst
        assert "_readback_timer.timeout.connect(_readback_ask)" in inst

    def test_the_rest_one_ask_and_the_guards(self):
        assert re.search(r"(?m)^const READBACK_DEBOUNCE_SEC := 0\.22$", MAIN)
        assert re.search(r"(?m)^const READBACK_CACHE_MAX := 24$", MAIN)
        ask = _func(MAIN, "_readback_ask")
        assert 'api_client.has_method("get_parse_preview")' in ask
        settle = _func(MAIN, "_readback_settle")
        assert 'api_client.has_method("cancel_parse_preview")' in settle
        on = _func(MAIN, "_on_readback")
        assert "serial != _readback_serial" in on
        assert 'str(resp.get("line", "")) != now' in on
        assert '"busy"' in on

    def test_asks_only_for_a_line_that_could_be_an_order(self):
        wanted = _func(MAIN, "_readback_wanted")
        for clause in ("UiSettings.get_readback()", "READBACK_MIN_CHARS", "READBACK_MAX_CHARS",
                       '"cheat "', '"debug "', 'line.find(",") >= 2', "READBACK_LEAD_WORDS",
                       "_MARSHAL_VERBS", "_BARE_COMMANDS", "_own_marshal_names()", "_is_modal_dialog_open()"):
            assert clause in wanted, clause
        assert '"display", "readback", not harness_active()' in _read(SCRIPTS / "ui_settings.gd")

    def test_every_seam_reads_the_line(self):
        assert "_readback_changed(_text)" in _func(MAIN, "_on_command_text_changed")
        for fn in ("_take_suggestion", "_refresh_after_accept", "_history_previous", "_history_next",
                   "_restore_parked_draft", "_fill_pending_relay", "_fill_pending_remedy",
                   "_on_tutorial_suggest_command"):
            assert "_readback_sync()" in _func(MAIN, fn), fn
        enable = _func(MAIN, "set_input_enabled")
        assert "_readback_cancel()" in enable and "_readback_sync()" in enable
        assert enable.index("_readback_sync()") < enable.rindex("_refresh_command_placeholder()")
        assert "_readback_cancel()" in _func(MAIN, "_execute_command")
        swap = _func(MAIN, "_reset_frontend_state_for_world_swap")
        assert "_readback_cancel()" in swap and "_readback_forget()" in swap
        assert "_readback_forget()" in _func(MAIN, "_on_command_result")
        assert "_readback_forget()" in _func(MAIN, "_remember_game_state")

    def test_it_renders_by_role_and_folds_its_notes(self):
        render = _func(MAIN, "_readback_render")
        assert 'if kind == "" or kind == "none" or kind == "busy":' in render
        assert 'glyph = "✕"' in render and 'glyph = "?"' in render and 'var glyph := "▸"' in render
        assert "if folded:\n\t\t\t\t\tnotes.append(words)" in render
        assert "_readback_row.tooltip_text = Utils.clean_tip(" in render
        assert "_ui6_bb_escape(words)" in render
        assert '"[url=cabinet:open]"' in render
        hexes = _func(MAIN, "_readback_part_hex")
        assert "Utils.COLOR_ERROR" in hexes and "Utils.COLOR_WARNING" in hexes and "Utils.COLOR_TEXT" in hexes

    def test_a_candidate_fills_and_never_sends(self):
        meta = _func(MAIN, "_on_readback_meta_clicked")
        assert 'm.begins_with("fill:")' in meta
        assert "command_input.text = line" in meta and "_resume_editing()" in meta
        for never in ("send_command", "_execute_command", "_on_reward_command"):
            assert never not in meta, never
        # row IC, Session 2: the links are built by ONE helper — the first line's
        # chips and, while a part of the line blocks, the "Or press to write:" line
        chips = _func(MAIN, "_readback_chips")
        assert "_readback_chip_links(resp)" in chips
        assert '"[url=fill:%d]%s[/url]"' in _func(MAIN, "_readback_chip_links")

    def test_the_harnesses_lack_nothing_the_client_asks(self):
        """A stub without the readback's two calls is guarded (has_method): the
        new harness carries both, recording and holding."""
        assert "func get_parse_preview(line, cb = null):" in READBACK_HARNESS
        assert "func cancel_parse_preview():" in READBACK_HARNESS


# ═══ UI6-X1 — the history ═══════════════════════════════════════════════════

class TestTheHistoryFilter:
    def test_the_offer_reads_the_safe_lines_and_the_walk_every_line(self):
        """The lead's ruling (the doctrine): an offer is the table's suggestion
        and stands on today's board; the Up / Down walk is the player's own
        recall — every line typed, as typed (a name is public, only a place is
        fogged; the walk writes nothing the player did not write)."""
        build = _func(MAIN, "_build_completions")
        assert "var remembered := _history_safe_lines()" in build
        assert "command_history[i]" not in build
        pool = _func(MAIN, "_history_pool")
        assert "var remembered: Array = command_history" in pool
        assert "_history_safe_lines()" not in pool.split('"""')[-1]
        # CX-3's prefix filter stands inside it
        assert "begins_with(prefix.to_lower())" in pool and "out.append(past)" in pool

    def test_the_test_is_a_whitelist_of_the_boards_words(self):
        safe = _func(MAIN, "_history_line_is_safe")
        assert "_history_known_words()" in safe and "w.is_valid_int()" in safe
        known = _func(MAIN, "_history_known_words")
        for source in ('_last_game_state.get("marshals", {})', '_last_game_state.get("enemies", {})',
                       "_region_names()", "_MARSHAL_VERBS", "_CONTINUATIONS", "_BARE_COMMANDS",
                       "HISTORY_JOIN_WORDS", "_NAME_SLOT_WORDS"):
            assert source in known, source
        # the omniscient roster is never read
        assert "get_enemies_of_nation" not in MAIN

    def test_the_joining_words_name_no_one(self):
        m = re.search(r"(?ms)^const HISTORY_JOIN_WORDS := \[(.*?)\]", MAIN)
        words = re.findall(r'"([^"]*)"', m.group(1))
        assert words and all(w == w.lower() and w.isalpha() for w in words), words
        for proper in ("charles", "kutuzov", "mack", "ney", "archduke", "john"):
            assert proper not in words

    def test_the_stale_comments_tell_the_truth(self):
        assert "Session-only and never written" not in MAIN
        assert "HISTORY IS SESSION-ONLY, AND DELIBERATELY NOT PERSISTED" not in MAIN
        assert "HISTORY IS PERSISTED — AND ITS OFFERS ARE FILTERED (UI6-X1; the walk is not)." in MAIN

    def test_the_driven_pin_rides_an_engine_lane(self):
        conftest = _read(REPO / "tests" / "conftest.py")
        panels = conftest[conftest.index('"engine_panels": frozenset({'):]
        panels = panels[:panels.index("}),")]
        assert '"test_cx_readback_history_fog"' in panels


# ═══ the 32:9 wing, the rail, the order card, the grid ══════════════════════

class TestTheWingTheRailTheCardTheGrid:
    def test_the_right_wing(self):
        build = _func(MAIN, "_ui6_build_right_wing")
        assert '_right_wing.name = "RightWing"' in build
        assert "_right_wing.mouse_filter = Control.MOUSE_FILTER_STOP" in build
        assert 'bottom_left_ui.get_theme_stylebox("panel")' in build       # the left column's frame
        fit = _func(MAIN, "_ui6_fit_right_wing")
        # the interim blind reading (Nov 13): the empty full-height frame is not drawn
        assert "WING_FRAME_DRAWN and Utils.hud_columns(size).y > 0.0 and not _hud_hidden" in fit
        assert "const WING_FRAME_DRAWN := false" in MAIN
        assert "Utils.hud_anchor_band(size)" in fit
        assert "_ui6_fit_right_wing()" in _func(MAIN, "_relayout_terminal")
        assert "_ui6_fit_right_wing()" in _func(MAIN, "_ui5_toggle_hud")

    def test_the_province_panel_docks_in_the_wing(self):
        assert ('if "avoid_above" in region_panel and war_status_panel != null') in MAIN
        assert "region_panel.avoid_above = war_status_panel.panel_container" in MAIN
        width = _func(PANEL, "_fit_width")
        assert width.index("_wing_band()") < width.index("Utils.hud_band(view)")
        assert "_fit_width_in_wing(wing)" in width
        height = _func(PANEL, "_fit_height")
        assert "_fit_height_in_wing()" in height
        assert height.index("_fit_height_in_wing()") < height.index("_beside_terminal_left(available)")
        band = _func(PANEL, "_wing_band")
        assert "Utils.hud_columns(view).y <= 0.0" in band and "Utils.hud_anchor_band(view)" in band
        top = _func(PANEL, "_wing_top")
        assert "avoid_above.get_global_rect().end.y + Utils.HUD_MARGIN" in top

    def test_the_war_detail_suspends_the_rail(self):
        assert "war_detail_popup.visibility_changed.connect(_ui6_refresh_rail_suspension)" in MAIN
        rail = _func(MAIN, "_ui6_refresh_rail_suspension")
        assert "notification_bar.set_suspended(_is_modal_dialog_open() or _is_screen_open() or _hud_hidden)" in rail
        # the war HUD's own rule is untouched
        assert ("notification_bar.set_suspended(_is_modal_dialog_open() or _is_screen_open() or _hud_hidden)"
                in _func(MAIN, "_update_war_panel_visibility"))

    def test_the_order_card_is_capped_and_its_buttons_stay_whole(self):
        refit = _func(CARD, "refit")
        assert "var band := Utils.hud_band(view)" in refit
        # Row IC, Session 3b (November 21, 2026): the card's authored width is 560 —
        # and the wider one only for the list of an army's task or a changed war goal
        # (`_authored_width`); the cap by the HUD band's share is the same for both.
        assert "minf(_authored_width(), (band.y - band.x) * BAND_SHARE)" in refit
        authored = _func(CARD, "_authored_width")
        assert "return CARD_WIDTH_TASK" in authored and authored.rstrip().endswith("return CARD_WIDTH")
        assert re.search(r"(?m)^const CARD_WIDTH := 560\.0$", CARD)
        assert "_fit_buttons(w)" in refit
        assert re.search(r"(?m)^const BAND_SHARE := 0\.9$", CARD)
        fit = _func(CARD, "_fit_buttons")
        assert "inner < BUTTONS_AUTHORED_W" in fit
        assert "b.custom_minimum_size.x = 0.0 if tight else float(_button_min_w[b.name])" in fit
        # 150 + 130 + 130 + two 10-px separations: the authored row
        assert 150 + 130 + 130 + 2 * 10 == 430

    def test_the_grid_portraits(self):
        # UI-6: 22 -> 40 x 50 (too small for the 32:9 column); row FR, Session FR-1 (IC2-N1):
        # 40 x 50 -> 32 x 40, the chip 58 -> 48 — the four rows give back the line's new row
        assert "const PORTRAIT_GRID := Vector2(32.0, 40.0)" in ROW
        assert re.search(r"(?m)^const GRID_H := 48\.0", ROW)
        chip = _func(ROW, "_make_chip")
        assert 'if not grid:\n\t\tname_label.theme_type_variation = &"Caption"' in chip
        assert "holder.custom_minimum_size = px" in _func(ROW, "_likeness")
        assert "const GRID_ROWS := 6" in ROW


# ═══ the house rules over the new block ═════════════════════════════════════

class TestTheHouseRules:
    def test_no_or_pick_no_size_tag_no_hex_no_dim(self):
        code = _code(BLOCK)
        assert not OR_PICK.search(code)
        assert "[font_size=" not in code and "add_theme_font_size_override" not in code
        assert not re.search(r'Color\.html\("#[0-9a-fA-F]', code)
        assert not re.search(r'"#?[0-9a-fA-F]{6}"', code)
        assert not re.search(r"\bUtils\.COLOR_(?:DIMMED|GREY|DIM)\b", code)

    def test_editing_is_asked_with_is_editing(self):
        assert "has_focus()" not in _code(_func(MAIN, "_ui6_digits_live"))

    def test_the_harness_stub_records_the_right_click_and_the_digits(self):
        assert 'func _right_click(region: String, marshal: String = "") -> void:' in HARNESS
        assert '_main.call("_on_order_context_requested", region, marshal)' in HARNESS
        assert "func _push_right(at: Vector2, pressed: bool) -> void:" in HARNESS
        assert '"cc3_digit":' in HARNESS and "UiSettings.set_next_marshal_after_order(true)" in HARNESS


class TestTheFoldedLogIsNeverMeasured:
    """UI6-X32 (Session UI-6, found by GE-2's driven harness): on the compact
    view the window is the slim bar and its log a folded drawer. A hidden
    label keeps a 1-px width — every character its own line — and the
    whole-line snap read each line's offset from the top, so every
    `add_output` cost O(paragraphs x characters): GE-2's Verdict day at the
    compact view spent minutes in one frame (the harness timed out at 300 s;
    it now runs in 16 s). The snap returns while the log is hidden, the folded
    bar's reply-hold counts lines and never measures, and opening the log
    re-snaps it."""

    def test_the_snap_returns_while_the_log_is_hidden(self):
        snap = _func(MAIN, "_snap_output_to_a_whole_line")
        guard = snap.index("if not output_scroll.is_visible_in_tree():")
        assert guard < snap.index("output_display.get_content_height()")
        assert guard < snap.index("output_display.get_line_offset(i)")

    def test_the_folded_bar_counts_lines_and_never_measures(self):
        hold = _func(MAIN, "_hold_tall_reply")
        fold = hold.index('if _desk_mode_now == "bar" and not _ui5_log_open:')
        assert "return _ui6_hold_reply(0.0)" in hold[fold:fold + 120]
        assert fold < hold.index("output_display.get_content_height()")
        assert "_reply_line_count < BAR_REPLY_LINES" in _func(MAIN, "_ui6_hold_reply")

    def test_opening_the_log_relayouts_and_scrolls_to_its_newest_line(self):
        opened = _func(MAIN, "_ui5_open_log")
        assert "_relayout_terminal()" in opened and "_scroll_output_to_end()" in opened
        assert "call_deferred(\"_resnap_output\")" in _func(MAIN, "_reposition_after_layout")
        assert "output_scroll.resized.connect(_on_output_scroll_resized)" in MAIN

    def test_the_shared_snap_already_skips_a_hidden_host(self):
        utils = _read(SCRIPTS / "utils.gd")
        assert "if rec.is_empty() or not host.is_visible_in_tree():" in _func(utils, "snap_whole_lines")


class TestTheLogsEndIsTheNewHeight:
    """UI6-X40 (Session UI-6, the dry-run census): the 32:9 desk column's log
    stood with its top line cut by 11.8 px. The whole-line pad grew the label
    (1978 -> 1991) but the scroll kept its old max: a stylebox margin never
    tells the parent a new minimum, and the ScrollContainer re-reads its
    child's minimum only when its own is recomputed. Under UI-5's AUTO mode the
    bar's show / hide re-sorted it by chance; UI6-X22's reserved gutter
    re-sorts on nothing. The snap now says so, and add_output waits for the
    snap's frame before it scrolls to the end."""

    def test_the_pad_tells_the_layout_and_the_scroll_re_reads_its_child(self):
        snap = _func(MAIN, "_snap_output_to_a_whole_line")
        at = snap.index("_output_pad.content_margin_bottom = pad")
        tail = snap[at:]
        for step in ("output_display.update_minimum_size()", "output_scroll.update_minimum_size()",
                     "output_scroll.get_combined_minimum_size()", "output_scroll.queue_sort()"):
            assert step in tail, step
        assert tail.index("output_scroll.queue_sort()") < tail.index("await get_tree().process_frame")

    def test_add_output_scrolls_after_the_snaps_frame(self):
        add = _func(MAIN, "add_output")
        assert "await _snap_output_to_a_whole_line()" in add
        assert add.index("await _snap_output_to_a_whole_line()") < add.index(
            "output_scroll.scroll_vertical = output_scroll.get_v_scroll_bar().max_value")
