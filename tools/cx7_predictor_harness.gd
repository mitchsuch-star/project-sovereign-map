# CX-7 slice 3 — the predictor, DRIVEN.
#
# The review round's sharpest procedural finding was that row CX pinned its
# own client half by READING THE SOURCE, on a stated belief that "there is no
# headless way to press Up in this project". There is: the same
# `Viewport.push_input(InputEventKey)` the row already used for Tab reaches
# `_on_command_input_gui_input`, and every key the completer binds is handled
# in that one function. This harness instantiates the REAL `main.tscn` and
# presses real keys at it.
#
# Built on IQ-10's proven shape (`tools/iq10_surface_screenshot.gd`): a
# `process_frame` tick with a hard frame limit, an in-memory `UiSettings`
# config so the player's file is never opened, and an API stub — the scene
# fetches on `_ready` and a harness that waits for a live backend is a
# harness that hangs.
#
#   Godot --headless --path godot-client/project-sovereign \
#         --script ../../tools/cx7_predictor_harness.gd
#
# Writes one JSON object to $CX7_OUT (default user://cx7_predictor.json) and
# prints it after a `[cx7]` marker. Read by `tests/test_cx7_predictor_driven.py`,
# which SKIPS when the engine is absent so the suite stays green without it.
extends SceneTree

const HARD_FRAME_LIMIT := 900


class ApiStub extends Node:
	var calls: Array = []

	func _answer(method: String, cb):
		calls.append(method)
		if cb is Callable:
			cb.call({"success": false, "message": "cx7 stub"})

	func test_connection(cb = null): _answer("test_connection", cb)
	# DELIBERATELY UNANSWERED. On the real client the topology request is
	# issued INSIDE `_on_connection_test` and its reply is 60+ frames away,
	# so `_initial_map_bootstrapped` is false for the whole of that handler.
	# A stub that answers synchronously flips the flag and hands the
	# handler the arm it takes in NO real boot — which made the first cut
	# of the CX3-R3 pin pass with the fix REVERTED. Recorded, not answered.
	func get_map_topology(_cb = null): calls.append("get_map_topology")
	func get_ledger(cb = null): _answer("get_ledger", cb)
	func get_diplomatic_ledger(cb = null): _answer("get_diplomatic_ledger", cb)
	func get_marshal_overview(cb = null): _answer("get_marshal_overview", cb)
	func get_dispatch(cb = null): _answer("get_dispatch", cb)
	func get_gazette(cb = null): _answer("get_gazette", cb)
	func get_campaign_log(cb = null): _answer("get_campaign_log", cb)
	func get_mailbox(cb = null): _answer("get_mailbox", cb)
	func get_pending_envoy(cb = null): _answer("get_pending_envoy", cb)
	func send_command(_c, _cb = null): calls.append("send_command")
	func cancel_strategic_order(_m, _cb = null): calls.append("cancel_strategic_order")
	func dismiss_notification(_i, _cb = null): calls.append("dismiss_notification")
	func dismiss_all_notifications(_cb = null): calls.append("dismiss_all_notifications")


var _frames := 0
var _phase := "boot"
var _wait := 0
var _main: Node = null
var _input: LineEdit = null
var _row: RichTextLabel = null
var _api: ApiStub = null
var _out := {}
var _fatal := ""


func _init():
	UiSettings._cfg = ConfigFile.new()
	process_frame.connect(_tick)


func _tick():
	_frames += 1
	if _frames > HARD_FRAME_LIMIT:
		_fatal = "frame limit hit in phase %s" % _phase
		_finish()
		return
	if _wait > 0:
		_wait -= 1
		return
	match _phase:
		"boot": _boot()
		"settle": _settle()
		"run": _run()
		"r4_hidden": _r4_hidden()
		"r4_shown": _r4_shown()
		"auto_end": _auto_end()
		"auto_end_t7_read": _auto_end_t7_read()
		"auto_end_t8_read": _auto_end_t8_read()
		"auto_end_t9_read": _auto_end_t9_read()
		"frames_faces": _frames_faces()
		"frames_trim": _frames_trim()
		"frames_trim_read": _frames_trim_read()
		"frames_hover": _frames_hover()
		"frames_hover_control": _frames_hover_control()
		"frames_hover_screen": _frames_hover_screen()
		"frames_hover_modal": _frames_hover_modal()
		"frames_interrupt": _frames_interrupt()
		"frames_interrupt_read": _frames_interrupt_read()
		"done": _finish()


func _boot():
	var packed: PackedScene = load("res://scenes/main.tscn")
	if packed == null:
		_fatal = "main.tscn did not load"
		_phase = "done"
		return
	_main = packed.instantiate()
	# swap the API before `_ready` can fetch
	_api = ApiStub.new()
	_api.name = "APIClient"
	var real = _main.get_node_or_null("APIClient")
	if real != null:
		_main.remove_child(real)
		real.queue_free()
	_main.add_child(_api)
	root.add_child(_main)
	if "api_client" in _main:
		_main.set("api_client", _api)
	_phase = "settle"
	_wait = 30


func _settle():
	_input = _main.get("command_input")
	if _input == null:
		_fatal = "command_input never resolved"
		_phase = "done"
		return
	if "api_client" in _main:
		_main.set("api_client", _api)
	_row = _main.get("_suggestion_row")
	if _row == null:
		_main.call("_install_suggestion_row")
		_row = _main.get("_suggestion_row")
	if _row == null:
		_fatal = "the completion row was never installed"
		_phase = "done"
		return
	_phase = "run"


func _key(code: int) -> void:
	var ev := InputEventKey.new()
	ev.keycode = code
	ev.pressed = true
	_input.grab_focus()
	_input.get_viewport().push_input(ev)


func _shift_tab() -> void:
	var ev := InputEventKey.new()
	ev.keycode = KEY_TAB
	ev.shift_pressed = true
	ev.pressed = true
	_input.grab_focus()
	_input.get_viewport().push_input(ev)


func _focus_name() -> String:
	var owner = _input.get_viewport().gui_get_focus_owner()
	return str(owner.name) if owner != null else ""


func _grip_gap() -> Dictionary:
	# The grip straddles the panel's top-right corner when it is placed
	# (`_position_resize_grip`'s own arithmetic); `gap` is how far it
	# drifted from that corner, `panel_h` proves the panel did resize.
	var panel = _main.get("bottom_left_ui")
	var grip = _main.get("resize_grip")
	if panel == null or grip == null:
		return {"gap": -1.0, "panel_h": -1.0}
	var rect: Rect2 = panel.get_global_rect()
	var corner := Vector2(rect.position.x + rect.size.x, rect.position.y)
	var center: Vector2 = grip.position + grip.size * 0.5
	return {"gap": (center - corner).length(), "panel_h": rect.size.y}


func _type(text: String) -> void:
	_input.grab_focus()
	_input.text = text
	_input.caret_column = text.length()
	_input.emit_signal("text_changed", text)


func _board() -> Dictionary:
	# CX-R2: the completer now draws each slot from the executor's answers on
	# the payload — a marshal's map entry (`tactical_state` gates), each
	# enemy's `at_war_with_player`, `passable_nations` — so the synthetic
	# board carries the shape the real payload has. The topology is left
	# unanswered (see `get_map_topology` above), so distances are unknown and
	# the pools come back alphabetically: the no-topology arm, exercised here.
	var gates := {
		"fortify_refusal": "", "unfortify_refusal": "not fortified",
		"drill_refusal": "", "defend_refusal": "", "garrison_refusal": "",
		"scout_range": 2, "move_open": ["Saxony", "Silesia"],
	}
	var corps := []
	for name in ["Ney", "Davout", "Soult", "Murat"]:
		corps.append({"name": name, "nation": "France", "tactical_state": gates})
	return {
		"player_nation": "France",
		"marshals": {"Ney": {"location": "Paris"}, "Davout": {"location": "Paris"},
			"Soult": {"location": "Paris"}, "Murat": {"location": "Paris"}},
		"enemies": {
			"Mack": {"location": "Swabia", "nation": "Austria", "at_war_with_player": true},
			"Brunswick": {"location": "Saxony", "nation": "Prussia", "at_war_with_player": true},
			"Deroy": {"location": "Silesia", "nation": "Bavaria", "at_war_with_player": true},
		},
		"passable_nations": ["Austria", "Bavaria", "France", "Prussia"],
		"map_data": {
			"Swabia": {"controller": "Austria", "marshals": []},
			"Silesia": {"controller": "Prussia", "marshals": []},
			"Saxony": {"controller": "Prussia", "marshals": []},
			"Paris": {"controller": "France", "marshals": corps},
		},
	}


func _offers() -> Array:
	var got = _main.get("_suggestions")
	return got if got is Array else []


func _run():
	# ── CX3-R8: the row's own font size, read off the LIVE node ────────
	_out["row_font_size"] = _row.get_theme_font_size("normal_font_size")
	_out["input_font_size"] = _input.get_theme_font_size("font_size")

	# ── CX3-R3: the boot handler must have REMEMBERED the board ────────
	# `_on_connection_test` ran on `_ready` against the stub, which answers
	# with no `game_state`; so this arm proves the SITE, not the payload —
	# the fix is that `_remember_game_state` is called for any response that
	# carries one, at the head of the block, rather than inside the
	# `_initial_map_bootstrapped` TRUE arm that is false on a fresh scene.
	_out["r3_bootstrapped_at_boot"] = _main.get("_initial_map_bootstrapped")
	_main.set("_last_game_state", {})      # the pre-boot state, explicitly
	_main.call("_on_connection_test", {"success": true, "game_state": _board()})
	# ... and the flag must STILL be false, or this arm took the other road
	_out["r3_bootstrapped_after"] = _main.get("_initial_map_bootstrapped")
	var remembered = _main.get("_last_game_state")
	_out["r3_remembered"] = (remembered is Dictionary
		and (remembered as Dictionary).size() > 0)
	_type("Ney, ")
	_out["r3_offers_after_boot"] = _offers().duplicate()

	# ── CX3-R1: every drawn offer must be reachable ────────────────────
	# An ADDRESSED verb slot, because that is where the list is longest —
	# three enemies on this board, and before CX3-R1 only the top one could
	# ever be placed on the line.
	_type("Ney, attack ")
	var drawn := _offers().duplicate()
	_out["r1_drawn"] = drawn.size()
	var reached := {}
	for _i in range(drawn.size() + 2):
		var idx = _main.get("_suggestion_index")
		if idx is int and idx >= 0 and idx < _offers().size():
			reached[str(_offers()[idx])] = true
		_key(KEY_DOWN)
	var missed := []
	for line in drawn:
		if not reached.has(str(line)):
			missed.append(str(line))
	_out["r1_unreachable"] = missed

	# ── CX3-R7: the completer wakes when a recalled line is EDITED ─────
	_main.call("_add_to_history", "Ney, attack Mack")
	_type("ney, a")
	_out["r7_before_up"] = _offers().size()
	_key(KEY_UP)
	_out["r7_line_after_up"] = _input.text
	_out["r7_during_walk"] = _offers().size()      # 0: the walk filled the line
	_type("Ney, attack Bru")                       # ... and now the player edits
	_out["r7_after_edit"] = _offers().duplicate()
	_out["r7_history_index"] = _main.get("history_index")

	# ── the completer never SENDS ──────────────────────────────────────
	_api.calls.clear()
	_type("ne")
	_key(KEY_TAB)
	_out["tab_filled"] = _input.text
	_out["tab_sent"] = ("send_command" in _api.calls)

	# ── CX3-R6: Tab belongs to the command line, offered or not ───────
	# A line with nothing to complete: Tab used to fall through to the
	# engine's `ui_focus_next` and throw the caret to Execute.
	_type("Ney, attack Mack at once")
	_out["r6_offers"] = _offers().size()
	_key(KEY_TAB)
	_out["r6_focus_after_tab"] = _focus_name()
	_out["r6_line_after_tab"] = _input.text
	# Shift+Tab walks the list backward where there is one.
	_type("Ney, attack ")
	_out["r6_list_size"] = _offers().size()
	_shift_tab()
	_out["r6_shift_tab_index"] = _main.get("_suggestion_index")
	_out["r6_focus_after_shift_tab"] = _focus_name()
	_out["r6_line_after_shift_tab"] = _input.text

	# ── CX3-R4: the grip follows the panel when the row opens ─────────
	_type("")
	_phase = "r4_hidden"
	_wait = 6


func _r4_hidden():
	_out["r4_hidden"] = _grip_gap()
	_type("Ney, attack ")
	_phase = "r4_shown"
	_wait = 6


func _r4_shown():
	_out["r4_row_visible"] = _row.visible
	_out["r4_shown"] = _grip_gap()
	_phase = "auto_end"


func _status_line(summary: Dictionary) -> String:
	_main.call("_update_status", summary)
	var button = _main.get("end_turn_button")
	return str(button.text) if button != null else ""


func _auto_end():
	# ── The auto-end confirm's client half (Chunk 9, slice 8) ─────────
	# The real `_update_status` the backend's action_summary feeds: the
	# warning is said once a turn before the day's last action, and the
	# End Turn button says when a spent day waits on it.
	var display = _main.get("output_display")
	_ae_text = display.get_parsed_text() if display != null else ""
	_ae_day = {"actions_remaining": 2, "max_actions": 4,
		"admin_actions_remaining": 1, "max_admin_actions": 2, "turn": 7, "max_turns": 0}
	_out["auto_end_button_full_day"] = _status_line(_ae_day)
	_ae_day["admin_actions_remaining"] = 0
	_out["auto_end_button_last_actions"] = _status_line(_ae_day)
	_ae_day["actions_remaining"] = 1
	_status_line(_ae_day)
	# SF7-X19 (Score Finish Step 7, slice 9): the line is said AFTER the
	# command's own output (`call_deferred`), so it is read a frame later.
	_out["auto_end_warning_same_frame_turn_7"] = (
		display.get_parsed_text() if display != null else "").substr(
			_ae_text.length()).count("ends the turn at once")
	_phase = "auto_end_t7_read"
	_wait = 2


var _ae_text := ""
var _ae_day := {}


func _auto_end_t7_read():
	var display = _main.get("output_display")
	var after: String = display.get_parsed_text() if display != null else ""
	_out["auto_end_warnings_turn_7"] = after.substr(_ae_text.length()).count("ends the turn at once")
	_ae_text = after
	_ae_day["actions_remaining"] = 0
	_out["auto_end_button_spent"] = _status_line(_ae_day)
	_ae_day["turn"] = 8
	_ae_day["actions_remaining"] = 4
	_ae_day["admin_actions_remaining"] = 2
	_out["auto_end_button_new_day"] = _status_line(_ae_day)
	_ae_day["actions_remaining"] = 2
	_ae_day["admin_actions_remaining"] = 0
	_status_line(_ae_day)
	_phase = "auto_end_t8_read"
	_wait = 2


func _auto_end_t8_read():
	var display = _main.get("output_display")
	var last: String = display.get_parsed_text() if display != null else ""
	_out["auto_end_warnings_turn_8"] = last.substr(_ae_text.length()).count("ends the turn at once")
	_ae_text = last
	# SF7-X19: with an envoy waiting, the day does NOT end at the last
	# action (WO-22's deferral) — and the line says so instead.
	_main.set("_current_lapsing_count", 2)
	_ae_day["turn"] = 9
	_ae_day["actions_remaining"] = 4
	_ae_day["admin_actions_remaining"] = 2
	_status_line(_ae_day)
	_ae_day["actions_remaining"] = 2
	_ae_day["admin_actions_remaining"] = 0
	_status_line(_ae_day)
	_phase = "auto_end_t9_read"
	_wait = 2


func _auto_end_t9_read():
	var display = _main.get("output_display")
	var tail: String = (display.get_parsed_text() if display != null else "").substr(
		_ae_text.length())
	_out["auto_end_waits_turn_9"] = tail.count("the day waits on the envoys")
	_out["auto_end_promises_turn_9"] = tail.count("ends the turn at once")
	_main.set("_current_lapsing_count", 0)
	_phase = "frames_faces"


# ── Score Finish Step 7 slice 9 (the frames): the terminal's own text ─────
func _frames_faces():
	# SF7-X18: `[b]` / `[i]` had no face of their own (the theme's
	# default_font answered every unset font item), and the terminal's
	# bold fell back to the theme's 16px against its 11px body.
	var od = _main.get("output_display")
	if od == null:
		_fatal = "no output_display"
		_finish()
		return
	_out["terminal_bold_face_differs"] = (
		od.get_theme_font("bold_font") != od.get_theme_font("normal_font"))
	_out["terminal_italic_face_differs"] = (
		od.get_theme_font("italics_font") != od.get_theme_font("normal_font"))
	_out["terminal_normal_size"] = od.get_theme_font_size("normal_font_size")
	_out["terminal_bold_size"] = od.get_theme_font_size("bold_font_size")
	_out["terminal_italics_size"] = od.get_theme_font_size("italics_font_size")
	_phase = "frames_trim"


func _frames_trim():
	# SF7-X17: the trim read `.text`, which `append_text` never fills, so
	# the first trim of a session wiped the whole scrollback. The terminal
	# starts EMPTY here (a fixed start, so the trim falls on line 100, not
	# wherever the boot's own messages left the count — the first cut of
	# this pin let the old trim pass when it fell early), then 130 numbered
	# lines through the ONE writer. The new trim keeps TRIMTEST 50..129
	# (80 lines); the old one keeps only the 30 written after its last
	# clear.
	var od = _main.get("output_display")
	od.clear()
	_main.set("message_count", 0)
	var kept = _main.get("_output_messages")
	if kept is Array:
		kept.clear()
	for i in range(130):
		_main.call("add_output", "TRIMTEST %d" % i)
		if i == 50:
			# The engine fact the row rests on: `append_text` does not fill
			# `.text` (Godot 4.4.1).
			_out["text_property_after_appends"] = str(od.text).length()
	_phase = "frames_trim_read"
	_wait = 2


func _frames_trim_read():
	var od = _main.get("output_display")
	var text: String = od.get_parsed_text() if od != null else ""
	_out["trim_lines_standing"] = text.count("TRIMTEST ")
	_out["trim_last_line_standing"] = text.find("TRIMTEST 129") >= 0
	_out["trim_line_50_standing"] = text.find("TRIMTEST 50\n") >= 0
	_out["trim_line_49_standing"] = text.find("TRIMTEST 49\n") >= 0
	_out["trim_marker"] = text.find("earlier messages trimmed") >= 0
	_phase = "frames_hover"


var _map_node: Node = null


func _frames_hover():
	# SF7-X21: a hover set before a screen or modal opened was never
	# cleared (only a mouse motion clears it). Three arms on the real map:
	# the control (nothing covers it — the hover stands), a screen open
	# (panning off), and a modal (the owner's check says so).
	_map_node = _main.get("map_area")
	if _map_node == null or not ("hovered_region" in _map_node):
		_out["hover_arm"] = "no map"
		_phase = "done"
		return
	_map_node.call("_set_hovered_region", "Paris")
	_phase = "frames_hover_control"
	_wait = 3


func _frames_hover_control():
	_out["hover_kept_when_uncovered"] = str(_map_node.get("hovered_region"))
	_map_node.set("panning_enabled", false)
	_map_node.call("_set_hovered_region", "Paris")
	_phase = "frames_hover_screen"
	_wait = 3


func _frames_hover_screen():
	_out["hover_after_screen"] = str(_map_node.get("hovered_region"))
	_map_node.set("panning_enabled", true)
	var saved_check = _map_node.get("pointer_blocked_check")
	_map_node.set("pointer_blocked_check", func(): return true)
	_map_node.set_meta("_saved_check", saved_check)
	_map_node.call("_set_hovered_region", "Paris")
	_phase = "frames_hover_modal"
	_wait = 3


func _frames_hover_modal():
	_out["hover_after_modal"] = str(_map_node.get("hovered_region"))
	_map_node.set("pointer_blocked_check", _map_node.get_meta("_saved_check"))
	_phase = "frames_interrupt"


func _frames_interrupt():
	# SF7-X27: the last-stand question on the real registered popup. The box
	# is measured the frame it opens (the clamp's authored rect) and after
	# the layout has settled (the fit).
	var popup = _main.get("interrupt_popup")
	if popup == null:
		_out["interrupt_arm"] = "no popup"
		_phase = "done"
		return
	popup.call("show_interrupt", {
		"interrupt_type": "last_stand", "marshal": "Ney",
		"message": "Ney is cornered at Rhineland with 2,840 men, Sire — capture looms. "
			+ "He asks leave to fight to the last, or he can attempt a breakout.",
		"options": ["fight_to_the_last", "attempt_breakout"]})
	var p: Control = popup.get_node("PanelContainer")
	_out["interrupt_h_opened"] = p.offset_bottom - p.offset_top
	_phase = "frames_interrupt_read"
	_wait = 6


func _frames_interrupt_read():
	var popup = _main.get("interrupt_popup")
	var p: Control = popup.get_node("PanelContainer")
	_out["interrupt_h_settled"] = p.offset_bottom - p.offset_top
	_out["interrupt_min_h"] = p.get_combined_minimum_size().y
	_out["interrupt_centred"] = is_equal_approx(p.offset_top, -p.offset_bottom)
	popup.hide()
	_phase = "done"


func _finish():
	if _fatal != "":
		_out["error"] = _fatal
	_out["frames"] = _frames
	var text := JSON.stringify(_out, "  ")
	var path := OS.get_environment("CX7_OUT")
	if path == "":
		path = "user://cx7_predictor.json"
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f != null:
		f.store_string(text)
		f.close()
	print("[cx7] ", text)
	quit(1 if _fatal != "" else 0)
