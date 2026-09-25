extends SceneTree
# Row EP GE-2 "the client" — the end screen, DRIVEN.
#
#   $env:GE2_SPEC = "<absolute path to a spec JSON>"
#   <godot> --headless --path godot-client/project-sovereign \
#           --script <abs path>/tools/ge2_campaign_end_harness.gd
#
# The spec (written by tests/test_ge2_the_client.py) carries REAL backend
# payloads and "out", the result path:
#   funeral       a /command response — `Napoleon, attack Mack` at
#                 SOVEREIGN_DEATH_CHANCE_PCT = 100: the war ends INSIDE the
#                 command (no dispatch, no Moniteur), `ending` is the funeral
#   verdict       an end-turn response at the Verdict's turn (enemy_phase +
#                 `ending` verdict, a MARKED ending)
#   humbled       a response whose `game_state.endings` names humbled_peace
#                 and which carries NO `ending` (the ratify road's shape)
#   campaign_end  the GET /campaign_end payload the stub answers for it
#   load_final    the /load response of a "Final — …" save (`ending`, game_over)
#   dispatch      a morning_dispatch dict carrying defeat_imminent_warning
#                 .fall.arms with the one-source `clock_line`
#   ledger        a GET /ledger payload carrying `fall_clock`
#   saves         a GET /saves payload (so the Load dialog can open)
#
# It boots the REAL `main.tscn` behind an API stub (F3's shape), hands each
# payload to the handler the live client hands it to, and records what the
# player would see: whether the end screen stands, its register, title, cause
# and body text, its buttons, whether the command line came back, the
# terminal text, the Load dialog's rise and the card's return after a
# cancelled load, and the clock line on the banner and the Territories tab.
#
# Safety rails (IQ-10's): UiSettings on an in-memory ConfigFile, no setter
# called; the result JSON is written on every exit path.

const HARD_FRAME_LIMIT := 900


class ApiStub extends Node:
	var calls: Array = []
	var responses: Dictionary = {}

	func _answer(method: String, cb):
		calls.append(method)
		if cb is Callable:
			var r = responses.get(method, null)
			if not (r is Dictionary):
				r = {"success": false, "message": "ge2 stub: no payload for " + method}
			cb.call(r)

	func test_connection(cb = null): _answer("test_connection", cb)
	func get_map_topology(_cb = null): calls.append("get_map_topology")
	func get_ledger(cb = null): _answer("get_ledger", cb)
	func get_diplomatic_ledger(cb = null): _answer("get_diplomatic_ledger", cb)
	func get_marshal_overview(cb = null): _answer("get_marshal_overview", cb)
	func get_dispatch(cb = null): _answer("get_dispatch", cb)
	func get_gazette(cb = null): _answer("get_gazette", cb)
	func get_campaign_log(cb = null): _answer("get_campaign_log", cb)
	func get_campaign_end(cb = null): _answer("get_campaign_end", cb)
	func get_mailbox(_cb = null): calls.append("get_mailbox")
	func get_pending_envoy(cb = null): _answer("get_pending_envoy", cb)
	func get_pending_redemption(_cb = null): calls.append("get_pending_redemption")
	func list_saves(cb = null): _answer("list_saves", cb)
	func load_game(_f, _cb = null): calls.append("load_game")
	func save_game(_f, _cb = null): calls.append("save_game")
	func new_game(_cb = null, _scenario = ""): calls.append("new_game")
	func set_llm_key(_k, _cb = null): calls.append("set_llm_key")
	func send_command(_c, _cb = null, _relayed = false): calls.append("send_command")
	func send_structured_command(_c, _d = null, _cb = null): calls.append("send_structured_command")
	func send_dialogue_response(_c, _cb = null, _id = -1): calls.append("send_dialogue_response")
	func send_dialogue_response_with_params(_c, _p = null, _cb = null, _id = -1): calls.append("send_dialogue_response_with_params")
	func send_capture_choice_response(_c, _cb = null, _id = ""): calls.append("send_capture_choice_response")
	func send_strategic_response(_m, _t = null, _c = null, _cb = null): calls.append("send_strategic_response")
	func send_objection_response(_c, _cb = null): calls.append("send_objection_response")
	func send_marshal_petition_response(_c, _cb = null): calls.append("send_marshal_petition_response")
	func send_glorious_charge_response(_c, _cb = null): calls.append("send_glorious_charge_response")
	func send_diplomatic_objection_response(_c, _cb = null): calls.append("send_diplomatic_objection_response")
	func send_redemption_response(_c, _cb = null): calls.append("send_redemption_response")
	func activate_mailbox_item(_i, _cb = null): calls.append("activate_mailbox_item")
	func respond_to_mailbox_item(_i, _c = null, _cb = null): calls.append("respond_to_mailbox_item")
	func cancel_strategic_order(_m, _cb = null): calls.append("cancel_strategic_order")
	func dismiss_notification(_i, _cb = null): calls.append("dismiss_notification")
	func dismiss_all_notifications(_cb = null): calls.append("dismiss_all_notifications")


var _frames := 0
var _phase := "boot"
var _wait := 0
var _main = null
var _api: ApiStub = null
var _spec: Dictionary = {}
var _out: Dictionary = {}
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
		"boot":
			_boot()
		"run":
			_run()
		"done":
			_finish()


func _boot():
	var path := OS.get_environment("GE2_SPEC")
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(path)) if path != "" else null
	if not (parsed is Dictionary):
		_fatal = "GE2_SPEC missing or not a JSON object"
		_phase = "done"
		return
	_spec = parsed
	var packed: PackedScene = load("res://scenes/main.tscn")
	if packed == null:
		_fatal = "main.tscn did not load"
		_phase = "done"
		return
	_main = packed.instantiate()
	_api = ApiStub.new()
	_api.name = "APIClient"
	_api.responses = {
		"get_campaign_end": _spec.get("campaign_end", {}),
		"list_saves": _spec.get("saves", {}),
		"get_ledger": _spec.get("ledger", {}),
	}
	var real = _main.get_node_or_null("APIClient")
	if real != null:
		_main.remove_child(real)
		real.queue_free()
	_main.add_child(_api)
	root.add_child(_main)
	if "api_client" in _main:
		_main.set("api_client", _api)
	_phase = "run"
	_wait = 60


func _terminal() -> String:
	var display = _main.get("output_display")
	if display == null:
		return ""
	return display.get_parsed_text()


func _clear_terminal() -> void:
	var display = _main.get("output_display")
	if display != null and display.has_method("clear"):
		display.clear()
	if "message_count" in _main:
		_main.set("message_count", 0)


func _modal_open() -> bool:
	var dm = _main.get("dialog_manager")
	return dm != null and dm.is_any_modal_open()


func _input_enabled() -> bool:
	var line = _main.get("command_input")
	return line != null and line.editable


func _button(btn) -> Dictionary:
	if btn == null:
		return {}
	return {"text": str(btn.text), "visible": bool(btn.visible), "disabled": bool(btn.disabled)}


func _screen_state() -> Dictionary:
	var ce = _main.get("campaign_end")
	if ce == null:
		return {"present": false}
	return {
		"present": true,
		"visible": bool(ce.visible),
		"register": str(ce.call("current_register")),
		"terminal": bool(ce.call("is_terminal")),
		"title": str(ce.get("title_label").text),
		"date": str(ce.get("date_label").text),
		"cause": str(ce.get("cause_label").text),
		"content": str(ce.get("content_label").get_parsed_text()),
		"primary": _button(ce.get("primary_btn")),
		"secondary": _button(ce.get("secondary_btn")),
		"layer": int(ce.layer),
		"input_enabled": _input_enabled(),
		"modal_open": _modal_open(),
		"campaign_over": bool(_main.get("_campaign_over")),
	}


func _dismiss_ahead_of_the_card() -> Array:
	"""Dismiss the surfaces the control-return tail raises AHEAD of the end
	screen (the battle tableau; the retired strategic-report modal), through
	their own dismiss handlers, up to a few times. Returns their names."""
	var stood: Array = []
	for _i in range(4):
		var diorama = _main.get("battle_diorama")
		if diorama != null and diorama.visible:
			stood.append("battle_diorama")
			diorama.hide()
			_main.call("_on_battle_diorama_dismissed")
			continue
		var report = _main.get("strategic_report_popup")
		if report != null and report.visible:
			stood.append("strategic_report_popup")
			report.hide()
			_main.call("_on_strategic_report_dismissed")
			continue
		break
	return stood


func _reset_between_scenes() -> void:
	# The world swap's own reset (a Load / New Campaign lifts the Fall) and a
	# clean terminal, so each scene is read whole.
	_main.call("_reset_frontend_state_for_world_swap", true)
	var ce = _main.get("campaign_end")
	if ce != null:
		ce.hide()
	_main.call("set_input_enabled", true)
	_clear_terminal()
	_api.calls.clear()


func _run():
	var map_area = _main.get("map_area")
	if map_area != null and map_area.has_method("set_region_topology"):
		map_area.set_region_topology(_spec.get("topology", {}))
	_reset_between_scenes()
	var ce = _main.get("campaign_end")
	_out["registered"] = ce != null

	# ── 1. The command road: the Emperor dies inside the player's own attack
	#       (GE-1 review #10 — no dispatch, no special; this card is the ONLY
	#       surface). The response is `success: true` with `game_state.game_over`.
	_main.call("_on_command_result", _spec.get("funeral", {}).duplicate(true))
	_out["funeral"] = _screen_state()
	_out["funeral_terminal"] = _terminal()
	# Load a campaign: the card steps aside for the Load dialog…
	if ce != null:
		ce.get("primary_btn").pressed.emit()
	var load_dialog = _main.get("load_dialog")
	_out["funeral_load_dialog_raised"] = load_dialog != null and load_dialog.visible
	_out["funeral_screen_hidden_for_load"] = ce != null and not ce.visible
	_out["funeral_input_during_load"] = _input_enabled()
	# …and a cancelled load brings it back, the command line still closed.
	if load_dialog != null:
		load_dialog.hide()
	_main.call("_on_load_cancelled")
	_out["funeral_after_cancel"] = _screen_state()
	# A second response of the fallen campaign (the refusal "The war is
	# over." carries game_over + the same ending) must not raise a second card
	# or reopen the line.
	if ce != null:
		ce.hide()
	var refusal = _spec.get("funeral_refusal", {})
	if not refusal.is_empty():
		_main.call("_on_command_result", refusal.duplicate(true))
		_out["funeral_refusal_reraised"] = ce != null and ce.visible
		_out["funeral_refusal_input_enabled"] = _input_enabled()

	# ── 2. A world swap lifts the Fall: the line reopens.
	_reset_between_scenes()
	_out["after_swap_input_enabled"] = _input_enabled()

	# ── 3. The end-turn road: the Verdict rides behind the enemy phase.
	_main.call("_on_command_result", _spec.get("verdict", {}).duplicate(true))
	var enemy_dialog = _main.get("enemy_phase_dialog")
	_out["verdict_enemy_phase_raised"] = enemy_dialog != null and enemy_dialog.visible
	_out["verdict_screen_before_dismiss"] = ce != null and ce.visible
	if enemy_dialog != null:
		enemy_dialog.hide()
	_main.call("_on_enemy_phase_dismissed")
	# The tail raises the battle tableau FIRST (the enemy phase at the
	# Verdict's turn fights real battles) and the strategic-report popup is
	# retired but still registered; dismiss what stands ahead of the card the
	# way the live dialogs do, and record what stood.
	_out["verdict_ahead_of_the_card"] = _dismiss_ahead_of_the_card()
	_out["verdict"] = _screen_state()
	_out["verdict_terminal"] = _terminal()
	if ce != null:
		ce.get("primary_btn").pressed.emit()   # Continue
	_out["verdict_after_continue"] = {
		"visible": ce != null and ce.visible,
		"input_enabled": _input_enabled(),
		"modal_open": _modal_open(),
	}
	# The same end-turn response again: the cause is shown, nothing re-raises.
	_main.call("_on_command_result", _spec.get("verdict", {}).duplicate(true))
	if enemy_dialog != null:
		enemy_dialog.hide()
	_main.call("_on_enemy_phase_dismissed")
	_dismiss_ahead_of_the_card()
	_out["verdict_repeat_raised"] = ce != null and ce.visible

	# ── 3b. The same Verdict with NO tableau riding the response: the
	#       control-return tail ITSELF raises the card (nothing stands ahead
	#       of it to hand the raise on).
	_reset_between_scenes()
	_main.call("_on_command_result", _spec.get("verdict_plain", {}).duplicate(true))
	if enemy_dialog != null:
		enemy_dialog.hide()
	_main.call("_on_enemy_phase_dismissed")
	var plain_diorama = _main.get("battle_diorama")
	_out["verdict_plain_diorama_visible"] = plain_diorama != null and plain_diorama.visible
	_out["verdict_plain"] = _screen_state()
	if ce != null and ce.visible:
		ce.get("primary_btn").pressed.emit()   # Continue

	# ── 4. The ratify road: a Humbled Peace named only in the compact list —
	#       the client asks the record (GET /campaign_end) and raises it after
	#       the response has rendered.
	_reset_between_scenes()
	_main.call("_on_command_result", _spec.get("humbled", {}).duplicate(true))
	_out["humbled"] = _screen_state()
	_out["humbled_fetched"] = _api.calls.has("get_campaign_end")
	_out["humbled_terminal"] = _terminal()
	if ce != null:
		ce.get("primary_btn").pressed.emit()   # Continue
	_out["humbled_after_continue"] = {
		"visible": ce != null and ce.visible,
		"input_enabled": _input_enabled(),
	}
	_api.calls.clear()
	_main.call("_on_command_result", _spec.get("humbled", {}).duplicate(true))
	_out["humbled_repeat_raised"] = ce != null and ce.visible
	_out["humbled_repeat_fetched"] = _api.calls.has("get_campaign_end")

	# ── 5. /load of a Final save: the card, the line closed, no fetch needed.
	_reset_between_scenes()
	_main.call("_on_load_result", _spec.get("load_final", {}).duplicate(true))
	_out["load_final"] = _screen_state()
	_out["load_final_fetched"] = _api.calls.has("get_campaign_end")
	_out["load_final_terminal"] = _terminal()

	# ── 6. The clock line on the end-turn banner (the dispatch render).
	_reset_between_scenes()
	_main.call("_display_morning_dispatch", _spec.get("dispatch", {}).duplicate(true))
	_out["dispatch_terminal"] = _terminal()

	# ── 7. The clock line on the Strategic Ledger's Territories tab.
	var packed = load("res://scenes/strategic_ledger.tscn")
	if packed is PackedScene:
		var ledger = packed.instantiate()
		root.add_child(ledger)
		ledger.call("open", _api)
		ledger.call("_switch_tab", 1)
		var area = ledger.get("content_area")
		_out["ledger_territories_text"] = area.get_parsed_text() if area != null else ""
		ledger.hide()

	_out["api_calls"] = _api.calls
	_phase = "done"


func _finish():
	if _fatal != "":
		_out["error"] = _fatal
	_out["frames"] = _frames
	var out := str(_spec.get("out", ""))
	if out != "":
		var f := FileAccess.open(out, FileAccess.WRITE)
		if f != null:
			f.store_string(JSON.stringify(_out))
			f.close()
	quit(1 if _fatal != "" else 0)
