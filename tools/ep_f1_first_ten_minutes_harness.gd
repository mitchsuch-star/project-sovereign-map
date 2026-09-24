extends SceneTree
# Row EP F1 "The first ten minutes" — the client, DRIVEN.
#
#   $env:EPF1_SPEC = "<absolute path to a spec JSON>"
#   <godot> --headless --path godot-client/project-sovereign \
#           --script <abs path>/tools/ep_f1_first_ten_minutes_harness.gd
#
# The spec (written by tests/test_ep_f1_the_first_ten_minutes.py) carries
# REAL backend payloads — the /new_game and /load responses, an attack
# response with an envoy riding it, the stored dispatch, a war row and a
# war-context snapshot — and "out", the result path. The harness boots the
# REAL `main.tscn` behind an API stub (CX-7's shape: the scene fetches on
# `_ready`, and a harness that waits for a live backend hangs), hands each
# payload to the handler the live client hands it to, and records what the
# player would read: the terminal's parsed text after each world swap and
# after the command result, whether the envoy's modal was raised, and the
# text of the Dispatch screen, the war tooltip, the war-detail popup and
# both War Summaries.
#
# Safety rails (IQ-10's): UiSettings on an in-memory ConfigFile, no setter
# called; the result JSON is written on every exit path.

const HARD_FRAME_LIMIT := 900


class ApiStub extends Node:
	var calls: Array = []

	func _answer(method: String, cb):
		calls.append(method)
		if cb is Callable:
			cb.call({"success": false, "message": "ep-f1 stub"})

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
	func new_game(_cb = null, _scenario = ""): calls.append("new_game")
	func set_llm_key(_k, _cb = null): calls.append("set_llm_key")
	func send_command(_c, _cb = null): calls.append("send_command")
	func send_dialogue_response(_c, _cb = null, _id = -1): calls.append("send_dialogue_response")
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
	var path := OS.get_environment("EPF1_SPEC")
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(path)) if path != "" else null
	if not (parsed is Dictionary):
		_fatal = "EPF1_SPEC missing or not a JSON object"
		_phase = "done"
		return
	_spec = parsed
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
	_phase = "run"
	# `_ready` awaits a 0.5 s timer before its connection test; let it run
	# and fail against the stub so nothing later appends to the terminal.
	_wait = 60


func _terminal() -> String:
	var display = _main.get("output_display")
	if display == null:
		return ""
	return display.get_parsed_text()


func _run():
	# The real topology first, as `/map_topology` hands it to the live map,
	# so the world swap's map update runs against the board it describes.
	var map_area = _main.get("map_area")
	if map_area != null and map_area.has_method("set_region_topology"):
		map_area.set_region_topology(_spec.get("topology", {}))

	# ── LV-1: Begin (the /new_game response through the live handler) ────
	_main.call("_on_new_game_result", _spec.get("new_game", {}))
	_out["new_game_terminal"] = _terminal()

	# ── LV-1 (c): Continue / Load ─────────────────────────────────────────
	_main.call("_on_load_result", _spec.get("load", {}))
	_out["load_terminal"] = _terminal()

	# ── LV-12: the order's result with an envoy riding the same response ──
	_main.call("_reset_frontend_state_for_world_swap", true)
	var attack = _spec.get("attack", {})
	_main.call("_on_command_result", attack)
	_out["attack_terminal"] = _terminal()
	var popup = _main.get("incoming_proposal_popup")
	_out["attack_envoy_raised"] = popup != null and popup.visible
	var dm = _main.get("dialog_manager")
	_out["attack_modal_open"] = dm != null and dm.is_any_modal_open()

	# ── LV-1 (b) + LV-7: the Dispatch screen (R) on the stored briefing ──
	var view = _main.get("dispatch_view")
	if view != null:
		view.visible = true
		view.call("_on_dispatch_received", {"success": true, "dispatch": _spec.get("dispatch", {})})
		var label = view.get("content_label")
		_out["dispatch_view_text"] = label.get_parsed_text() if label != null else ""
		view.visible = false

	# ── LV-8: the war tooltip, the war-detail popup, both War Summaries ───
	var war_row = _spec.get("war_row", {})
	var panel = _main.get("war_status_panel")
	if panel != null:
		_out["war_tooltip"] = str(panel.call("_build_war_tooltip", war_row))
	var detail = _main.get("war_detail_popup")
	if detail != null:
		detail.call("_render_war_detail", war_row)
		var detail_label = detail.get("content_label")
		_out["war_detail_text"] = detail_label.get_parsed_text() if detail_label != null else ""
	var snapshot_payload = {"war_context_snapshot": _spec.get("snapshot", {}),
		"target_nation": "Austria"}
	if popup != null:
		_out["incoming_summary"] = str(popup.call("_build_peace_preview_section", snapshot_payload, []))
	var confirm = _main.get("proposal_confirm_popup")
	if confirm != null:
		_out["confirm_summary"] = str(confirm.call("_build_peace_preview_content", snapshot_payload))

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
