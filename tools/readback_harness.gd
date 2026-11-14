# Session UI-6 (November 13, 2026) — THE READBACK ROW and THE HISTORY'S
# OFFERS (UI6-X1), DRIVEN.
#
#   Godot --headless --path godot-client/project-sovereign \
#         --script <abs path>/tools/readback_harness.gd
#
# The REAL `main.tscn` behind an API stub (the shape `tools/cx7_predictor_
# harness.gd` proved): an in-memory UiSettings config, real keys pushed into
# the viewport, and a stub that RECORDS `get_parse_preview` and HOLDS its
# callback so a scenario answers it when (and with what) it chooses.
#
# What it drives:
#   h1 — the persisted history OFFERS (the completer's first step) only lines
#        whose every word stands on the board: a fogged marshal's name, an
#        invented one and a typo withhold their line from the offers; the
#        Up / Down walk recalls every line as typed (the player's own words —
#        a name is public under the fog doctrine);
#   h2 — before the first board nothing naming a marshal is offered (fail
#        closed); the walk still recalls every line;
#   r1 — the row stands in the window's own VBox, right after the completion
#        row, before the line, hidden, with no font override;
#   r2 — with Settings → Readback on, a typed line is asked for once after
#        the rest; a stale answer (an older line) is dropped; the answer for
#        the line shows; a remembered line shows at once with no new ask;
#   r3 — a candidate chip FILLS the line and sends nothing;
#   r4 — the closed line (a send in flight) hides the row and cancels.
#
# Writes one JSON object to $READBACK_OUT (default user://readback.json) and
# prints it after a `[readback]` marker. Read by
# `tests/test_cx_readback_history_fog.py`, which SKIPS when the engine is
# absent (a skip is not a pass).
extends SceneTree

# A headless run keeps no frame rate (no vsync): the readback's rest is real
# time, so the waits are on the clock, and both limits stand.
const HARD_FRAME_LIMIT := 200000
const WALL_LIMIT_MS := 120000
const ASK_WAIT_MS := 3000


class ApiStub extends Node:
	var calls: Array = []
	var previews: Array = []      # [line, callback], oldest first

	func _answer(method: String, cb):
		calls.append(method)
		if cb is Callable:
			cb.call({"success": false, "message": "readback stub"})

	func test_connection(cb = null): _answer("test_connection", cb)
	# Recorded, never answered (the real client's timing — see cx7's stub).
	func get_map_topology(_cb = null): calls.append("get_map_topology")
	func get_ledger(cb = null): _answer("get_ledger", cb)
	func get_diplomatic_ledger(cb = null): _answer("get_diplomatic_ledger", cb)
	func get_marshal_overview(cb = null): _answer("get_marshal_overview", cb)
	func get_dispatch(cb = null): _answer("get_dispatch", cb)
	func get_gazette(cb = null): _answer("get_gazette", cb)
	func get_campaign_log(cb = null): _answer("get_campaign_log", cb)
	func get_mailbox(cb = null): _answer("get_mailbox", cb)
	func get_pending_envoy(cb = null): _answer("get_pending_envoy", cb)
	func get_march_reach(m, _cb = null): calls.append("march_reach:" + str(m))
	func get_order_quote(m, k, t, _cb = null): calls.append("order_quote:%s|%s|%s" % [str(m), str(k), str(t)])
	func send_command(c, _cb = null, _r = false): calls.append("send:" + str(c))
	func cancel_strategic_order(m, _cb = null): calls.append("cancel:" + str(m))
	func dismiss_notification(_i, _cb = null): calls.append("dismiss_notification")
	func dismiss_all_notifications(_cb = null): calls.append("dismiss_all_notifications")
	# Session UI-6: the readback's own road — recorded, its callback HELD.
	func get_parse_preview(line, cb = null):
		calls.append("preview:" + str(line))
		previews.append([str(line), cb])
	func cancel_parse_preview():
		calls.append("preview_cancel")
	func answer_preview(index: int, payload) -> bool:
		if index < 0 or index >= previews.size():
			return false
		var cb = previews[index][1]
		if cb is Callable:
			(cb as Callable).call(payload)
			return true
		return false


var _frames := 0
var _phase := "boot"
var _wait := 0
var _main: Node = null
var _input: LineEdit = null
var _api: ApiStub = null
var _out := {}
var _fatal := ""
var _t0 := 0
var _typed_at := 0           # when the line was typed (the rest runs from here)

# The seeded history: the design's own six lines (§4's test).
const SEEDED := ["Ney, attack Archduke Charles", "Ney, attack Mack", "Ney, march to Vienna",
	"Zorglub, charge", "what can I do", "ney, atack mack"]


func _init():
	UiSettings._cfg = ConfigFile.new()
	UiSettings._persist = false   # the harness flag: writes stay in memory
	_t0 = Time.get_ticks_msec()
	process_frame.connect(_tick)


func _tick():
	_frames += 1
	if _frames > HARD_FRAME_LIMIT or Time.get_ticks_msec() - _t0 > WALL_LIMIT_MS:
		_fatal = "limit hit in phase %s" % _phase
		_finish()
		return
	if _wait > 0:
		_wait -= 1
		return
	match _phase:
		"boot": _boot()
		"settle": _settle()
		"history": _history()
		"readback_type": _readback_type()
		"readback_asked": _readback_asked()
		"readback_cached": _readback_cached()
		"done": _finish()


func _boot():
	var packed: PackedScene = load("res://scenes/main.tscn")
	if packed == null:
		_fatal = "main.tscn did not load"
		_phase = "done"
		return
	_main = packed.instantiate()
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
	_phase = "history"


func _board() -> Dictionary:
	"""Ney and Davout ours; Mack in sight and at war; Vienna, Swabia and
	Paris on the map. No Archduke Charles anywhere: he is in fog."""
	var gates := {"fortify_refusal": "", "unfortify_refusal": "not fortified", "drill_refusal": "",
		"defend_refusal": "", "garrison_refusal": "", "scout_range": 2, "move_open": ["Swabia"]}
	return {
		"player_nation": "France",
		"marshals": {"Ney": {"location": "Paris", "strength": 20000},
			"Davout": {"location": "Paris", "strength": 18000}},
		"enemies": {"Mack": {"location": "Swabia", "nation": "Austria", "at_war_with_player": true}},
		"passable_nations": ["Austria", "France"],
		"map_data": {
			"Vienna": {"controller": "Austria", "marshals": []},
			"Swabia": {"controller": "Austria", "marshals": []},
			"Paris": {"controller": "France", "marshals": [
				{"name": "Ney", "nation": "France", "tactical_state": gates},
				{"name": "Davout", "nation": "France", "tactical_state": gates}]},
		},
	}


func _key(code: int, unicode: int = 0) -> void:
	var ev := InputEventKey.new()
	ev.keycode = code
	ev.physical_keycode = code
	ev.unicode = unicode
	ev.pressed = true
	_input.grab_focus()
	_input.get_viewport().push_input(ev)
	var up := ev.duplicate()
	up.pressed = false
	_input.get_viewport().push_input(up)


func _clear_line() -> void:
	_input.text = ""
	_input.caret_column = 0
	_main.set("history_index", -1)
	_main.set("_history_anchor", "")
	_main.set("_history_walk_text", "")
	_main.call("_on_command_text_changed", "")


func _walk(code: int, presses: int) -> Array:
	"""Press Up (or Down) `presses` times from where the line stands; the
	line's text after each press."""
	var seen: Array = []
	for _i in range(presses):
		_key(code)
		seen.append(str(_input.text))
	return seen


func _offers_for(prefix: String) -> Array:
	var got = _main.call("_build_completions", prefix)
	return (got as Array).duplicate() if got is Array else []


func _history():
	# the line open, as after any reply (the stub never answers the boot)
	_main.call("set_input_enabled", true)
	# ── h2 — no board yet: nothing naming a marshal is offered (the walk recalls all) ──
	_main.set("_last_game_state", {})
	_main.set("_history_known_built", false)
	_main.set("command_history", SEEDED.duplicate())
	_main.set("_offered_command", "")
	_main.set("_parked_draft", "")
	_clear_line()
	_out["h2_offers_ney"] = _offers_for("Ney")
	_out["h2_offers_what"] = _offers_for("what")
	_out["h2_safe_lines"] = (_main.call("_history_safe_lines") as Array).duplicate()
	_clear_line()
	_out["h2_walk_up"] = _walk(KEY_UP, SEEDED.size() + 2)

	# ── h1 — on the board: only the lines it can stand behind ──
	_main.call("_remember_game_state", _board())
	_main.set("command_history", SEEDED.duplicate())
	_clear_line()
	_out["h1_safe_lines"] = (_main.call("_history_safe_lines") as Array).duplicate()
	var verdicts := {}
	for line in SEEDED:
		verdicts[line] = bool(_main.call("_history_line_is_safe", line))
	_out["h1_verdicts"] = verdicts
	_out["h1_offers_ney"] = _offers_for("Ney")
	_out["h1_offers_ney_attack"] = _offers_for("Ney, attack ")
	_out["h1_offers_zorg"] = _offers_for("Zorg")
	_clear_line()
	_out["h1_walk_up"] = _walk(KEY_UP, SEEDED.size() + 2)
	_out["h1_walk_down"] = _walk(KEY_DOWN, SEEDED.size() + 2)
	_clear_line()
	# the prefix-filtered walk narrows by the prefix alone
	_input.text = "ney"
	_input.caret_column = 3
	_out["h1_walk_prefixed"] = _walk(KEY_UP, 4)
	_clear_line()

	# ── r1 — the row's seat ──
	var row = _main.get("_readback_row")
	_out["r1_row_exists"] = row != null
	if row != null:
		var layout: Node = (row as Node).get_parent()
		var names: Array = []
		for child in layout.get_children():
			names.append(str(child.name))
		_out["r1_siblings"] = names
		_out["r1_hidden_at_rest"] = not bool(row.visible)
		_out["r1_font_override"] = (row as Control).has_theme_font_size_override("normal_font_size")
		_out["r1_fit_content"] = bool(row.fit_content)

	# ── r2 — the readback on: one ask after the rest ──
	UiSettings.set_readback(true)
	_out["r2_setting_on"] = UiSettings.get_readback()
	# how the row reads its notes here: the compact view drops them, folded
	# they are the hover, on the page they print
	_out["r2_compact"] = Utils.compact_view()
	_out["r2_folded"] = Utils.explanations_folded()
	_main.call("set_input_enabled", true)
	_api.previews.clear()
	_api.calls.clear()
	_input.grab_focus()
	_input.text = "Ney, attack Mack"
	_input.caret_column = _input.text.length()
	_main.call("_on_command_text_changed", _input.text)
	_out["r2_asked_at_once"] = _api.previews.size()
	_typed_at = Time.get_ticks_msec()
	_phase = "readback_type"


func _asked_or_waiting() -> bool:
	"""True while the rest has not run out (no ask yet, inside the wait)."""
	return _api.previews.is_empty() and Time.get_ticks_msec() - _typed_at < ASK_WAIT_MS


func _readback_type():
	if _asked_or_waiting():
		return
	_out["r2_rest_ms"] = Time.get_ticks_msec() - _typed_at
	_out["r2_asked_after_rest"] = _api.previews.size()
	_out["r2_asked_line"] = str(_api.previews[0][0]) if _api.previews.size() > 0 else ""
	# a stale answer — the line it read is not the line now — is dropped
	var row = _main.get("_readback_row")
	if _api.previews.size() > 0:
		_api.answer_preview(0, {"success": true, "line": "Ney, attack Ma", "kind": "order",
			"parts": [{"role": "head", "text": "Ney · attack Ma"}], "candidates": []})
		_out["r2_visible_after_stale"] = bool(row.visible)
		_out["r2_text_after_stale"] = str(row.get_parsed_text())
		# the answer for the line shows
		_api.answer_preview(0, {"success": true, "line": "Ney, attack Mack", "kind": "order",
			"parts": [{"role": "head", "text": "Ney · attack Mack (Swabia)"},
				{"role": "cost", "text": "1 action"}, {"role": "warn", "text": "he may object"},
				{"role": "note", "text": "replaces his march"}],
			"candidates": []})
		_out["r2_visible"] = bool(row.visible)
		_out["r2_text"] = str(row.get_parsed_text())
		_out["r2_tooltip"] = str(row.tooltip_text)
	# an unknown name: its candidate fills the line, nothing is sent
	_api.previews.clear()
	_input.text = "Nye, attack Mack"
	_input.caret_column = _input.text.length()
	_main.call("_on_command_text_changed", _input.text)
	_typed_at = Time.get_ticks_msec()
	_phase = "readback_asked"


func _readback_asked():
	if _asked_or_waiting():
		return
	var row = _main.get("_readback_row")
	_out["r3_asked"] = _api.previews.size()
	if _api.previews.size() > 0:
		_api.answer_preview(0, {"success": true, "line": "Nye, attack Mack", "kind": "unknown_name",
			"parts": [{"role": "head", "text": "No marshal ‘Nye’ of ours"}],
			"candidates": [{"label": "Ney", "line": "Ney, attack Mack"}]})
	_out["r3_text"] = str(row.get_parsed_text())
	var sends_before := 0
	for c in _api.calls:
		if str(c).begins_with("send:"):
			sends_before += 1
	_main.call("_on_readback_meta_clicked", "fill:0")
	_out["r3_line_after_fill"] = str(_input.text)
	var sends_after := 0
	for c in _api.calls:
		if str(c).begins_with("send:"):
			sends_after += 1
	_out["r3_sends"] = sends_after - sends_before
	# the line now reads "Ney, attack Mack" — remembered: shown at once, no ask
	_api.previews.clear()
	_out["r3_cached_visible"] = bool(row.visible)
	_out["r3_cached_text"] = str(row.get_parsed_text())
	_typed_at = Time.get_ticks_msec()
	_phase = "readback_cached"


func _readback_cached():
	# a full rest (and more) passes: a remembered line asks nothing
	if Time.get_ticks_msec() - _typed_at < 600:
		return
	var row = _main.get("_readback_row")
	_out["r3_cached_new_asks"] = _api.previews.size()
	# r4 — the line closes (a send in flight): the row hides, the ask is cancelled
	var cancels_before := _api.calls.count("preview_cancel")
	_main.call("set_input_enabled", false)
	_out["r4_visible_after_close"] = bool(row.visible)
	_out["r4_cancelled"] = _api.calls.count("preview_cancel") > cancels_before
	_main.call("set_input_enabled", true)
	_phase = "done"


func _finish():
	if _fatal != "":
		_out["error"] = _fatal
	_out["frames"] = _frames
	var text := JSON.stringify(_out, "  ")
	var path := OS.get_environment("READBACK_OUT")
	if path == "":
		path = "user://readback.json"
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f != null:
		f.store_string(text)
		f.close()
	print("[readback] ", text)
	quit(1 if _fatal != "" else 0)
