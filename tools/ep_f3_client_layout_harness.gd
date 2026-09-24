extends SceneTree
# Row EP F3 "The client layout pass" — the client, DRIVEN.
#
#   $env:EPF3_SPEC = "<absolute path to a spec JSON>"
#   <godot> --headless --path godot-client/project-sovereign \
#           --script <abs path>/tools/ep_f3_client_layout_harness.gd
#
# The spec (written by tests/test_ep_f3_the_client_layout_pass.py) carries
# REAL backend payloads — an attack response that ends in a CAPTURE (its
# battle_report, its message, its pending_capture_choice) and an end-turn
# response carrying strategic_reports, the enemy phase and the morning
# dispatch — and "out", the result path. The harness boots the REAL
# `main.tscn` behind an API stub (F1's shape), hands each payload to the
# handler the live client hands it to, and records what the player would
# read after each: the terminal text ADDED by that step, whether the
# Plunder/Secure dialog was raised, whether the retired strategic-report
# modal was raised, whether any modal stands, and whether the command line
# came back.
#
# Safety rails (IQ-10's): UiSettings on an in-memory ConfigFile, no setter
# called; the result JSON is written on every exit path.

const HARD_FRAME_LIMIT := 900


class ApiStub extends Node:
	var calls: Array = []

	func _answer(method: String, cb):
		calls.append(method)
		if cb is Callable:
			cb.call({"success": false, "message": "ep-f3 stub"})

	func test_connection(cb = null): _answer("test_connection", cb)
	func get_map_topology(_cb = null): calls.append("get_map_topology")
	func get_ledger(cb = null): _answer("get_ledger", cb)
	func get_diplomatic_ledger(cb = null): _answer("get_diplomatic_ledger", cb)
	func get_marshal_overview(cb = null): _answer("get_marshal_overview", cb)
	func get_dispatch(cb = null): _answer("get_dispatch", cb)
	func get_gazette(cb = null): _answer("get_gazette", cb)
	func get_campaign_log(cb = null): _answer("get_campaign_log", cb)
	func get_mailbox(_cb = null): calls.append("get_mailbox")
	func get_pending_envoy(cb = null): _answer("get_pending_envoy", cb)
	func get_pending_redemption(_cb = null): calls.append("get_pending_redemption")
	func list_saves(_cb = null): calls.append("list_saves")
	func load_game(_f, _cb = null): calls.append("load_game")
	func save_game(_f, _cb = null): calls.append("save_game")
	func new_game(_cb = null, _scenario = ""): calls.append("new_game")
	func set_llm_key(_k, _cb = null): calls.append("set_llm_key")
	func send_command(_c, _cb = null): calls.append("send_command")
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
var _api = null
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
	var path := OS.get_environment("EPF3_SPEC")
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(path)) if path != "" else null
	if not (parsed is Dictionary):
		_fatal = "EPF3_SPEC missing or not a JSON object"
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
	# The terminal trims its oldest lines past a cap, so a slice from a
	# remembered length is not the step's text. Each step starts empty and
	# is read whole.
	var display = _main.get("output_display")
	if display != null and display.has_method("clear"):
		display.clear()
	# `add_output` trims by its own message COUNT and re-prints the trimmed
	# marker once it passes the cap — the count starts over with the text.
	if "message_count" in _main:
		_main.set("message_count", 0)


func _modal_open() -> bool:
	var dm = _main.get("dialog_manager")
	return dm != null and dm.is_any_modal_open()


func _input_enabled() -> bool:
	var line = _main.get("command_input")
	return line != null and line.editable


func _run():
	var map_area = _main.get("map_area")
	if map_area != null and map_area.has_method("set_region_topology"):
		map_area.set_region_topology(_spec.get("topology", {}))
	_main.call("_reset_frontend_state_for_world_swap", true)
	_clear_terminal()

	# ── LV-22, the command path: an attack that ends in a capture ─────────
	var capture = _spec.get("capture", {})
	_main.call("_on_command_result", capture.duplicate(true))
	_out["command_terminal"] = _terminal()
	var dialog = _main.get("capture_choice_dialog")
	_out["command_capture_raised"] = dialog != null and dialog.visible
	_out["command_modal_open"] = _modal_open()
	if dialog != null:
		dialog.hide()
	_main.call("set_input_enabled", true)

	# ── LV-22, the muster road: the same battle through the interrupt answer
	_clear_terminal()
	var muster = _spec.get("capture", {}).duplicate(true)
	_main.call("_on_interrupt_response", muster)
	_out["muster_terminal"] = _terminal()
	_out["muster_capture_raised"] = dialog != null and dialog.visible
	if dialog != null:
		dialog.hide()
	_main.call("set_input_enabled", true)

	# ── LV-D3: an end turn with standing orders and no interrupt ──────────
	_clear_terminal()
	var end_turn = _spec.get("end_turn", {})
	_main.call("_on_command_result", end_turn.duplicate(true))
	var enemy_dialog = _main.get("enemy_phase_dialog")
	_out["enemy_phase_raised"] = enemy_dialog != null and enemy_dialog.visible
	_out["end_turn_terminal_before_dismiss"] = _terminal()
	_clear_terminal()
	# The live dialog hides itself before it emits `dismissed`; the handler
	# is what the harness drives, so the hide is done here as the dialog does.
	if enemy_dialog != null:
		enemy_dialog.hide()
	_main.call("_on_enemy_phase_dismissed")
	_out["end_turn_terminal"] = _terminal()
	var popup = _main.get("strategic_report_popup")
	_out["strategic_report_popup_raised"] = popup != null and popup.visible
	_out["end_turn_modal_open"] = _modal_open()
	_out["input_enabled_after_end_turn"] = _input_enabled()
	var standing: Array = []
	for key in ["enemy_phase_dialog", "strategic_report_popup", "interrupt_popup",
			"marshal_petition_dialog", "capture_choice_dialog", "incoming_proposal_popup",
			"proposal_confirm_popup", "objection_dialog", "battle_diorama", "mailbox_panel",
			"redemption_dialog", "vassal_rebellion_popup", "clarification_popup"]:
		var node = _main.get(key)
		if node != null and node.visible:
			standing.append(key)
	_out["standing_after_end_turn"] = standing

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
