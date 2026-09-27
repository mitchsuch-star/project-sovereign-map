extends SceneTree
# PC15-10 B4b "The one tail" — the client's stash-and-raise, DRIVEN.
#
#   $env:B4B_SPEC = "<absolute path to a spec JSON>"
#   <godot> --headless --path godot-client/project-sovereign \
#           --script <abs path>/tools/b4b_one_tail_harness.gd
#
# The spec (written by tests/test_b4b_the_one_tail.py) carries REAL backend
# payloads — the answer to an objection the player overrode, whose attack took
# a province (the backend sends its Plunder/Secure question on that answer);
# the capture answer the backend gives back; a redemption event from the
# backend's own checker; a Proclamation card from the backend's own builder;
# a /new_game response — and "out", the result path. The harness boots the
# REAL `main.tscn` behind an API stub (F1's shape), hands each payload to the
# handler the live client hands it to, and records what stands on screen
# after each step: every visible modal, whether the command line is live,
# what it holds, and what is still queued.
#
# Six scenarios, one per defect the B4b recon found (plus the two the
# review of the first cut found):
#   s1  an objection overridden, and the attack takes a province
#   s2  an interrupt answer raises a redemption with a second question queued
#   s3  an end turn closes with a capture question AND a Proclamation stashed
#   s4  a Load over the old campaign's stashes
#   s5  the pause menu opened while a request was in flight
#   s6  a capture answer that asks again (the estate stage's shape)
#
# Safety rails (IQ-10's): UiSettings on an in-memory ConfigFile, no setter
# called; the result JSON is written on every exit path.

const HARD_FRAME_LIMIT := 900

const MODALS := [
	"objection_dialog", "redemption_dialog", "enemy_phase_dialog", "battle_diorama",
	"glorious_charge_dialog", "capture_choice_dialog", "reward_dialog",
	"marshal_petition_dialog", "proclamation_popup", "campaign_end", "load_dialog",
	"strategic_report_popup", "interrupt_popup", "clarification_popup",
	"incoming_proposal_popup", "proposal_confirm_popup", "talleyrand_objection_popup",
	"sabotage_discovery_popup", "vassal_rebellion_popup", "commitment_paradox_popup",
	"diplomacy_wizard", "war_detail_popup", "mailbox_panel", "pause_menu",
]


class ApiStub extends Node:
	var calls: Array = []

	func _answer(method: String, cb):
		calls.append(method)
		if cb is Callable:
			cb.call({"success": false, "message": "b4b stub"})

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
	func get_campaign_end(_cb = null): calls.append("get_campaign_end")
	func list_saves(_cb = null): calls.append("list_saves")
	func load_game(_f, _cb = null): calls.append("load_game")
	func save_game(_f, _cb = null): calls.append("save_game")
	func new_game(_cb = null, _scenario = ""): calls.append("new_game")
	func set_llm_key(_k, _cb = null): calls.append("set_llm_key")
	func send_command(_c, _cb = null, _r = false): calls.append("send_command")
	func send_structured_command(_c, _d = null, _cb = null): calls.append("send_structured_command")
	func send_dialogue_response(_c, _cb = null, _id = -1): calls.append("send_dialogue_response")
	func send_dialogue_response_with_params(_c, _p = null, _cb = null, _id = -1): calls.append("send_dialogue_response_with_params")
	func send_capture_choice_response(_c, _cb = null, _id = -1): calls.append("send_capture_choice_response")
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
	var path := OS.get_environment("B4B_SPEC")
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(path)) if path != "" else null
	if not (parsed is Dictionary):
		_fatal = "B4B_SPEC missing or not a JSON object"
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


func _node(key: String):
	return _main.get(key) if key in _main else null


func _visible_modals() -> Array:
	var standing: Array = []
	for key in MODALS:
		var node = _node(key)
		if node != null and node.visible:
			standing.append(key)
	return standing


func _input_enabled() -> bool:
	var line = _node("command_input")
	return line != null and line.editable


func _command_line() -> String:
	var line = _node("command_input")
	return "" if line == null else str(line.text)


func _hide(key: String) -> void:
	# The live dialogs hide themselves before they emit; the harness drives
	# the handler, so the hide is done here as the dialog does.
	var node = _node(key)
	if node != null:
		node.hide()


func _scrub() -> void:
	"""Isolation between scenarios — never through the code under test (the
	committed client has no `_clear_pending_surfaces`), always by name."""
	for key in MODALS:
		_hide(key)
	for key in ["pending_capture_response", "pending_proclamation_data",
			"pending_redemption_data", "pending_deferred_dialogue",
			"pending_petition_data", "pending_diorama_data",
			"pending_enemy_phase_response", "pending_strategic_response"]:
		if key in _main:
			_main.set(key, null)
	if "pending_relay_command" in _main:
		_main.set("pending_relay_command", "")
	if "pending_redemption" in _main:
		_main.set("pending_redemption", false)
	if "_diorama_standalone" in _main:
		_main.set("_diorama_standalone", false)
	var queue = _node("interrupt_queue")
	if queue is Array:
		queue.clear()
	var endings = _node("pending_ending_queue")
	if endings is Array:
		endings.clear()
	var line = _node("command_input")
	if line != null:
		line.text = ""
	_main.call("set_input_enabled", true)


func _dismiss_diorama_if_raised() -> bool:
	var diorama = _node("battle_diorama")
	if diorama == null or not diorama.visible:
		return false
	diorama.hide()
	_main.call("_on_battle_diorama_dismissed")
	return true


func _run():
	var map_area = _node("map_area")
	if map_area != null and map_area.has_method("set_region_topology"):
		map_area.set_region_topology(_spec.get("topology", {}))
	_main.call("_reset_frontend_state_for_world_swap", true)
	_scrub()

	# ── s1: an objection overridden, and the attack takes a province ──────
	_main.call("set_input_enabled", false)
	_main.call("_on_objection_response", _spec.get("objection_capture", {}).duplicate(true))
	_out["s1_modals"] = _visible_modals()
	_out["s1_diorama_first"] = _dismiss_diorama_if_raised()
	_out["s1_modals_before_control"] = _visible_modals()
	_out["s1_capture_raised"] = "capture_choice_dialog" in _visible_modals()
	_out["s1_input_enabled"] = _input_enabled()
	_scrub()

	# ── s2: an interrupt answer raises a redemption; a second question waits
	var queue = _node("interrupt_queue")
	if queue is Array:
		queue.append(_spec.get("second_question", {}).duplicate(true))
	_main.call("set_input_enabled", false)
	_main.call("_on_interrupt_response", _spec.get("interrupt_redemption", {}).duplicate(true))
	_out["s2_modals"] = _visible_modals()
	_out["s2_queue_after_answer"] = (queue.size() if queue is Array else -1)
	_hide("redemption_dialog")
	_main.call("_on_redemption_response", _spec.get("redemption_answer", {}).duplicate(true))
	_out["s2_modals_after_redemption"] = _visible_modals()
	_out["s2_queue_after_redemption"] = (queue.size() if queue is Array else -1)
	_scrub()

	# ── s3: an end turn closes with a capture question AND a Proclamation ──
	_main.set("pending_capture_response", _spec.get("objection_capture", {}).duplicate(true))
	_main.set("pending_proclamation_data", _spec.get("proclamation", {}).duplicate(true))
	_main.set("pending_enemy_phase_response", null)
	_main.call("set_input_enabled", false)
	_main.call("_on_enemy_phase_dismissed")
	_out["s3_modals"] = _visible_modals()
	_hide("capture_choice_dialog")
	_main.call("_on_capture_choice_response", _spec.get("capture_answer", {}).duplicate(true))
	_out["s3_modals_after_capture"] = _visible_modals()
	_hide("proclamation_popup")
	_main.call("_on_proclamation_dismissed")
	_out["s3_modals_at_end"] = _visible_modals()
	_out["s3_input_enabled_at_end"] = _input_enabled()
	_scrub()

	# ── s4: a Load over the old campaign's stashes ─────────────────────────
	_main.set("pending_relay_command", str(_spec.get("old_relay", "")))
	_main.set("pending_petition_data", _spec.get("old_petition", {}).duplicate(true))
	_main.set("pending_capture_response", _spec.get("objection_capture", {}).duplicate(true))
	_main.call("set_input_enabled", false)
	_main.call("_apply_world_swap_response", _spec.get("new_game", {}).duplicate(true), "Loaded.")
	_out["s4_modals"] = _visible_modals()
	_out["s4_command_line"] = _command_line()
	_out["s4_input_enabled"] = _input_enabled()
	# The next control return in the NEW campaign — the old campaign's
	# question must not be waiting for it.
	_main.call("_return_control_to_player")
	_out["s4_modals_at_next_return"] = _visible_modals()
	_scrub()

	# ── s5: the pause menu opened while a request was in flight ───────────
	_main.call("set_input_enabled", false)
	var pause = _node("pause_menu")
	if pause != null:
		pause.open_menu()
	_main.set("pending_proclamation_data", _spec.get("proclamation", {}).duplicate(true))
	_main.call("_on_mailbox_panel_closed")
	_out["s5_modals"] = _visible_modals()
	_out["s5_input_enabled"] = _input_enabled()
	if pause != null:
		pause.close_menu()
	_main.call("_on_mailbox_panel_closed")
	_out["s5_modals_at_next_return"] = _visible_modals()
	_scrub()

	# ── s6: a capture answer that asks again (the estate stage's shape) ──
	_main.call("set_input_enabled", false)
	_main.call("_on_capture_choice_response", _spec.get("objection_capture", {}).duplicate(true))
	_out["s6_modals"] = _visible_modals()
	_out["s6_input_enabled"] = _input_enabled()
	_scrub()

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
