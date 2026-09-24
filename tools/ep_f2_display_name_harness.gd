extends SceneTree
# Row EP F2 "The display-name pass" — the client half, DRIVEN.
#
#   $env:EPF2_SPEC = "<absolute path to a spec JSON>"
#   <godot> --headless --path godot-client/project-sovereign \
#           --script <abs path>/tools/ep_f2_display_name_harness.gd
#
# The spec (written by tests/test_ep_f2_the_display_name_pass.py) carries:
#   enemy_phase        an enemy-phase payload with a conquest event and a
#                      field-battle capture, both stamped `captured_from`
#                      (LV-10 — " (was X)" on both branches)
#   strategic_reports  report rows with `command_display`, an int and a
#                      FLOAT `turns_remaining` (LV-4 — the retired modal's
#                      formatter, still the row renderer for an interrupt)
#   report             a REAL battle_report from `/command` whose
#                      casualty_summary carries the advance's toll (LV-11)
#                      and whose defence line is split (LV-18)
#   diorama            the REAL battle_diorama payload from the same
#                      response (LV-11 on the lead card, LV-2 nameplates)
#   out                the result path
# It boots the REAL `main.tscn` behind an API stub (F1/F3's shape), drives
# each renderer, and records the text a player would read.

const HARD_FRAME_LIMIT := 900


class ApiStub extends Node:
	var calls: Array = []

	func _answer(method: String, cb):
		calls.append(method)
		if cb is Callable:
			cb.call({"success": false, "message": "ep-f2 stub"})

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
		"diorama_wait":
			_read_diorama()
		"done":
			_finish()


func _boot():
	var path := OS.get_environment("EPF2_SPEC")
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(path)) if path != "" else null
	if not (parsed is Dictionary):
		_fatal = "EPF2_SPEC missing or not a JSON object"
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
	var display = _main.get("output_display")
	if display != null and display.has_method("clear"):
		display.clear()
	if "message_count" in _main:
		_main.set("message_count", 0)


func _labels_under(node: Node, acc: Array) -> void:
	if node is Label:
		acc.append(str(node.text))
	elif node is RichTextLabel:
		acc.append(str(node.get_parsed_text()))
	for child in node.get_children():
		_labels_under(child, acc)


func _run():
	_main.call("_reset_frontend_state_for_world_swap", true)

	# ── LV-10: the enemy phase's two capture branches ────────────────────
	var enemy_dialog = _main.get("enemy_phase_dialog")
	if enemy_dialog != null and _spec.has("enemy_phase"):
		enemy_dialog.show_enemy_phase(_spec.get("enemy_phase", {}), 5)
		var label = enemy_dialog.get("content_label")
		_out["enemy_text"] = label.get_parsed_text() if label != null else ""
		enemy_dialog.hide()

	# ── LV-4: the strategic report's row formatter ───────────────────────
	var popup = _main.get("strategic_report_popup")
	if popup != null and _spec.has("strategic_reports"):
		popup.show_reports(_spec.get("strategic_reports", []), 5)
		var label = popup.get("content_label")
		_out["report_popup_text"] = label.get_parsed_text() if label != null else ""
		popup.hide()

	# ── LV-9 / LV-2: the client helpers ───────────────────────────────────
	_out["plural"] = {
		"1 envoy": Utils.plural(1, "envoy"),
		"3 envoy": Utils.plural(3, "envoy"),
		"1 turn": Utils.plural(1, "turn"),
		"2 turn": Utils.plural(2, "turn"),
		"1 unanswered envoy": Utils.plural(1, "unanswered envoy"),
		"2 more port": Utils.plural(2, "more port"),
		"1 petition": Utils.plural(1, "petition"),
	}
	_out["display_marshal_name"] = {
		"ArchdukeCharles": Utils.display_marshal_name("ArchdukeCharles"),
		"Ney": Utils.display_marshal_name("Ney"),
	}

	# ── LV-11 / LV-18 / LV-19: Berthier's report on the terminal ─────────
	# `reports` = {name: battle_report}; each is rendered on a cleared
	# terminal and read whole.
	var reports = _spec.get("reports", {})
	var rendered := {}
	if reports is Dictionary:
		for name in reports:
			_clear_terminal()
			_main.call("_display_berthier_report", reports[name].duplicate(true))
			rendered[name] = _terminal()
	_out["berthier_terminal"] = rendered

	# ── LV-11 / LV-2: the diorama's lead card and nameplates ─────────────
	var diorama = _main.get("battle_diorama")
	if diorama != null and _spec.has("diorama"):
		diorama.show_diorama(_spec.get("diorama", {}).duplicate(true), false)
		_phase = "diorama_wait"
		_wait = 30
		return
	_out["api_calls"] = _api.calls
	_phase = "done"


func _read_diorama():
	var diorama = _main.get("battle_diorama")
	var labels: Array = []
	if diorama != null:
		_labels_under(diorama, labels)
	_out["diorama_labels"] = labels
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
