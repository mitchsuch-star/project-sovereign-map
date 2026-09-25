extends SceneTree
# Row EP GE-3 "The Congress of Paris" — the client surfaces, DRIVEN.
#
#   .venv/Scripts/python.exe tools/iq10_capture_payloads.py --out <DIR> --only congress
#   $env:GE3_SPEC = "<absolute path to a spec JSON>"   # {"payload_dir": "<DIR>", "out": "<result>"}
#   $env:SOVEREIGN_PORT = "8997"                         # a dead port: the wizard's own
#                                                        # HTTPRequest never reaches 8005
#   <godot> --headless --path godot-client/project-sovereign \
#           --log-file <abs log> --script <abs path>/tools/ge3_congress_harness.gd
#
# The payloads are REAL backend payloads, captured off STAGED boards by the
# IQ-10 `congress` capture group (`tools/iq10_capture_payloads.py`, whose
# `cap_congress` states exactly what was staged: the Pressburg ratified
# through `_ratify_treaty`, nine provinces handed over as treaty title, the
# summons, the sitting's days through the ONE per-turn caller, and the
# eighth day of a Congress every court signed played as a REAL end turn).
# A spec key may carry the payload inline (a Dictionary) or a path to its
# JSON file; any key left out is read from `payload_dir` under the capture's
# own file name:
#
#   ledger_sitting    GET /diplomatic_ledger — a Congress sitting, day 2
#   ledger_gate       GET /diplomatic_ledger — the 1805 boot (the gate)
#   wizard_gate       GET /diplomatic_preview — the gate, the summons refused
#   wizard_ready      GET /diplomatic_preview — every term met
#   wizard_sitting    GET /diplomatic_preview — the Congress sitting
#   imperial          POST /command end turn — the eighth day: `ending` =
#                     THE IMPERIAL PEACE through a real Congress
#   campaign_end      GET /campaign_end (the stub answers the stash's fetch)
#   dispatch          GET /dispatch — a briefing carrying `congress_clock`
#   strategic_ledger  GET /ledger — `congress_clock` for the Territories tab
#   gazette           GET /gazette — an issue with the Congress column
#   topology          GET /map_topology
#
# It boots the REAL `main.tscn` behind an API stub (the GE-2 harness's shape),
# hands each payload to the handler the live client hands it to, and records
# what the player would see: the CONGRESS tab reached by its deep link and by
# the wizard's "View the table", a court card's Cabinet link, the wizard's
# step-1 Congress row in its three phases (and the command its button sends),
# the gold card with its Congress block, and the clock line on the banner, the
# R screen and the Territories tab, and Le Moniteur's Congress column.
#
# Safety rails (IQ-10's): UiSettings on an in-memory ConfigFile, no setter
# called; the result JSON is written on every exit path.

const HARD_FRAME_LIMIT := 1200

const DEFAULT_FILES := {
	"ledger_sitting": "diplo_ledger_congress_sitting.json",
	"ledger_gate": "diplo_ledger_congress_gate.json",
	"wizard_gate": "wizard_nations_congress_gate.json",
	"wizard_ready": "wizard_nations_congress_ready.json",
	"wizard_sitting": "wizard_nations_congress_sitting.json",
	"imperial": "campaign_end_imperial_congress_response.json",
	"campaign_end": "campaign_end_congress_record.json",
	"dispatch": "dispatch_congress_clock.json",
	"strategic_ledger": "ledger_congress_clock.json",
	"gazette": "gazette_congress.json",
	"topology": "congress_map_topology.json",
}


class ApiStub extends Node:
	var calls: Array = []
	var sent: Array = []
	var responses: Dictionary = {}

	func _answer(method: String, cb):
		calls.append(method)
		if cb is Callable:
			var r = responses.get(method, null)
			if not (r is Dictionary):
				r = {"success": false, "message": "ge3 stub: no payload for " + method}
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
	func send_command(c, _cb = null, _relayed = false):
		calls.append("send_command")
		sent.append(str(c))
	func send_structured_command(c, _d = null, _cb = null):
		calls.append("send_structured_command")
		sent.append(str(c))
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
var _p: Dictionary = {}
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


func _read_json(path: String):
	if path == "" or not FileAccess.file_exists(path):
		return null
	return JSON.parse_string(FileAccess.get_file_as_string(path))


func _payload(key: String) -> Dictionary:
	"""Inline dict, a path string, or `payload_dir/<capture file>`."""
	var v = _spec.get(key, null)
	if v is Dictionary:
		return v
	if v is String:
		var parsed = _read_json(v)
		return parsed if parsed is Dictionary else {}
	var dir := str(_spec.get("payload_dir", ""))
	if dir != "" and DEFAULT_FILES.has(key):
		var from_dir = _read_json(dir.path_join(str(DEFAULT_FILES[key])))
		return from_dir if from_dir is Dictionary else {}
	return {}


func _boot():
	var path := OS.get_environment("GE3_SPEC")
	var parsed = _read_json(path)
	if not (parsed is Dictionary):
		_fatal = "GE3_SPEC missing or not a JSON object"
		_phase = "done"
		return
	_spec = parsed
	for key in DEFAULT_FILES:
		_p[key] = _payload(str(key))
	var missing: Array = []
	for key in DEFAULT_FILES:
		if (_p[key] as Dictionary).is_empty():
			missing.append(key)
	_out["missing_payloads"] = missing
	var packed: PackedScene = load("res://scenes/main.tscn")
	if packed == null:
		_fatal = "main.tscn did not load"
		_phase = "done"
		return
	_main = packed.instantiate()
	_api = ApiStub.new()
	_api.name = "APIClient"
	_api.responses = {
		"get_diplomatic_ledger": _p["ledger_sitting"],
		"get_campaign_end": _p["campaign_end"],
		"get_dispatch": _p["dispatch"],
		"get_ledger": _p["strategic_ledger"],
		"get_gazette": _p["gazette"],
	}
	var real = _main.get_node_or_null("APIClient")
	if real != null:
		_main.remove_child(real)
		real.queue_free()
	_main.add_child(_api)
	root.add_child(_main)
	if "api_client" in _main:
		_main.set("api_client", _api)
	# main.gd builds its own ApiClient in _ready and hands it to the top bar,
	# which opens every screen with it — the stub must reach the top bar too,
	# or the ledger and the R screen fetch from a server that is not there.
	var tb = _main.get("top_bar")
	if tb != null and tb.has_method("set_api_client"):
		tb.call("set_api_client", _api)
	_phase = "run"
	_wait = 60


# ── reading what the player sees ─────────────────────────────────────────────

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


func _input_enabled() -> bool:
	var line = _main.get("command_input")
	return line != null and line.editable


func _top_bar():
	return _main.get("top_bar")


func _dledger():
	var tb = _top_bar()
	if tb == null:
		return null
	var screens = tb.get("screens")
	if screens is Dictionary:
		return screens.get("diplomatic_ledger", null)
	return null


func _ledger_state() -> Dictionary:
	var dl = _dledger()
	if dl == null:
		return {"present": false}
	var tabs = dl.get("tab_buttons")
	var tab_texts: Array = []
	if tabs is Array:
		for b in tabs:
			tab_texts.append(str(b.text) if b != null else "")
	var area = dl.get("content_area")
	return {
		"present": true,
		"visible": bool(dl.visible),
		"current_tab": int(dl.get("current_tab")),
		"review_target": str(dl.get("_open_review_target")),
		"tabs": tab_texts,
		"text": area.get_parsed_text() if area != null else "",
		"bbcode": str(area.text) if area != null else "",
		"active_screen": str(_top_bar().call("get_active_screen")) if _top_bar() != null else "",
	}


func _wizard():
	return _main.get("diplomacy_wizard")


func _wizard_rows() -> Array:
	"""Every child of the step-1 list, in order: its kind and its text (a
	Button's `disabled` too) — the list the player reads top to bottom."""
	var rows: Array = []
	var wiz = _wizard()
	if wiz == null:
		return rows
	var list = wiz.get("content_list")
	if list == null:
		return rows
	for child in list.get_children():
		if child.is_queued_for_deletion():
			continue
		if child is Button:
			rows.append({"kind": "button", "text": str(child.text), "disabled": bool(child.disabled),
				"tooltip": str(child.tooltip_text)})
		elif child is RichTextLabel:
			rows.append({"kind": "rich", "text": child.get_parsed_text()})
		elif child is Label:
			rows.append({"kind": "label", "text": str(child.text)})
	return rows


func _find_button(prefix: String):
	var wiz = _wizard()
	if wiz == null:
		return null
	var list = wiz.get("content_list")
	if list == null:
		return null
	for child in list.get_children():
		if child is Button and not child.is_queued_for_deletion() and str(child.text).strip_edges().begins_with(prefix):
			return child
	return null


func _render_wizard(payload: Dictionary) -> void:
	"""The wizard's step 1, rendered off a captured payload through the SAME
	`_render_nations` the wire response reaches (the IQ-10 wizard road — the
	wizard fetches over its own HTTPRequest, which this harness never lets
	reach a server)."""
	var wiz = _wizard()
	if wiz == null:
		return
	wiz.set("_current_step", 1)
	wiz.show()
	wiz.call("_render_nations", payload.duplicate(true))


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
		"cause": str(ce.get("cause_label").text),
		"content": str(ce.get("content_label").get_parsed_text()),
		"primary": str(ce.get("primary_btn").text),
		"secondary": str(ce.get("secondary_btn").text),
		"secondary_visible": bool(ce.get("secondary_btn").visible),
		"input_enabled": _input_enabled(),
	}


func _dismiss_ahead_of_the_card() -> Array:
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
	_main.call("_reset_frontend_state_for_world_swap", true)
	var ce = _main.get("campaign_end")
	if ce != null:
		ce.hide()
	var wiz = _wizard()
	if wiz != null and wiz.visible:
		wiz.call("_close_wizard")
	var tb = _top_bar()
	if tb != null:
		tb.call("close_all_screens")
	_main.call("set_input_enabled", true)
	_clear_terminal()
	_api.calls.clear()
	_api.sent.clear()


# ── the scenes ───────────────────────────────────────────────────────────────

func _run():
	var map_area = _main.get("map_area")
	if map_area != null and map_area.has_method("set_region_topology"):
		map_area.set_region_topology(_p.get("topology", {}))
	_reset_between_scenes()
	_out["ledger_registered"] = _dledger() != null
	_out["wizard_registered"] = _wizard() != null

	# ── 1. The CONGRESS tab by its deep link (the `ledger_congress` review
	#       target — the road a notification and the wizard both take).
	var tb = _top_bar()
	if tb != null:
		tb.call("open_diplomatic_ledger_review", "ledger_congress")
	_out["ledger_sitting"] = _ledger_state()
	# A court's card opens the Cabinet at that court (open_diplomacy_for →
	# main closes the ledger and opens the wizard at the court).
	var dl = _dledger()
	if dl != null:
		var area = dl.get("content_area")
		if area != null:
			area.meta_clicked.emit("congress_court:Prussia")
	var wiz = _wizard()
	_out["court_click"] = {
		"ledger_visible": dl != null and dl.visible,
		"wizard_visible": wiz != null and wiz.visible,
		"wizard_nation": str(wiz.get("_selected_nation")) if wiz != null else "",
		"wizard_step": int(wiz.get("_current_step")) if wiz != null else -1,
	}

	# ── 2. The tab at boot — the gate, the table as each court would answer.
	_reset_between_scenes()
	_api.responses["get_diplomatic_ledger"] = _p["ledger_gate"]
	if dl != null:
		dl.call("open", _api)
		dl.call("_switch_tab", 6)
	_out["ledger_gate"] = _ledger_state()
	# The number key: 7 selects the CONGRESS tab (the guard reads focus).
	if dl != null:
		dl.call("_switch_tab", 0)
		# A digit belongs to whoever has the caret (the Aug 30 guard): the
		# command line gives it up first, as a player clicking the ledger does.
		var cmd_line = _main.get("command_input")
		if cmd_line != null:
			cmd_line.release_focus()
		var key := InputEventKey.new()
		key.keycode = KEY_7
		key.pressed = true
		dl.call("_input", key)
		_out["key_7_selects_tab"] = int(dl.get("current_tab"))
	_api.responses["get_diplomatic_ledger"] = _p["ledger_sitting"]

	# ── 3. The wizard's step 1 — the gate (the summons refused, its terms).
	_reset_between_scenes()
	_render_wizard(_p["wizard_gate"])
	_out["wizard_gate"] = _wizard_rows()
	var gate_btn = _find_button("Summon the Congress")
	_out["wizard_gate_summon_disabled"] = gate_btn != null and bool(gate_btn.disabled)

	# ── 4. Ready — every term met; the button sends the typed verb.
	_reset_between_scenes()
	_render_wizard(_p["wizard_ready"])
	_out["wizard_ready"] = _wizard_rows()
	var ready_btn = _find_button("Summon the Congress")
	_out["wizard_ready_summon_disabled"] = ready_btn == null or bool(ready_btn.disabled)
	if ready_btn != null and not ready_btn.disabled:
		ready_btn.pressed.emit()
	_out["wizard_ready_sent"] = _api.sent.duplicate()
	_out["wizard_ready_closed"] = _wizard() != null and not _wizard().visible
	_out["wizard_ready_terminal"] = _terminal()

	# ── 5. Sitting — "View the table" opens the ledger on its CONGRESS tab.
	_reset_between_scenes()
	_render_wizard(_p["wizard_sitting"])
	_out["wizard_sitting"] = _wizard_rows()
	var view_btn = _find_button("↳ View the table")
	if view_btn != null:
		view_btn.pressed.emit()
	_out["wizard_sitting_closed"] = _wizard() != null and not _wizard().visible
	_out["view_the_table"] = _ledger_state()

	# ── 6. THE IMPERIAL PEACE on the end-turn road — the eighth day of a
	#       Congress every court signed. The enemy phase renders first; the
	#       gold card after it.
	_reset_between_scenes()
	_main.call("_on_command_result", _p["imperial"].duplicate(true))
	var enemy_dialog = _main.get("enemy_phase_dialog")
	_out["imperial_enemy_phase_raised"] = enemy_dialog != null and enemy_dialog.visible
	if enemy_dialog != null and enemy_dialog.visible:
		enemy_dialog.hide()
		_main.call("_on_enemy_phase_dismissed")
	_out["imperial_ahead_of_the_card"] = _dismiss_ahead_of_the_card()
	_out["imperial"] = _screen_state()
	_out["imperial_terminal"] = _terminal()
	var ce = _main.get("campaign_end")
	if ce != null and ce.visible:
		ce.get("primary_btn").pressed.emit()   # Continue the reign
	_out["imperial_after_continue"] = {
		"visible": ce != null and ce.visible,
		"input_enabled": _input_enabled(),
	}

	# ── 7. The clock line on the end-turn banner (the dispatch render).
	_reset_between_scenes()
	var briefing = _p["dispatch"].get("dispatch", {})
	_main.call("_display_morning_dispatch", briefing.duplicate(true) if briefing is Dictionary else {})
	_out["dispatch_terminal"] = _terminal()

	# ── 8. The R screen (dispatch_view re-reads GET /dispatch).
	_reset_between_scenes()
	if tb != null:
		tb.call("toggle_screen", "dispatch")
		var screens = tb.get("screens")
		var dv = screens.get("dispatch", null) if screens is Dictionary else null
		var label = dv.get("content_label") if dv != null else null
		_out["r_screen_text"] = label.get_parsed_text() if label != null else ""

	# ── 9. The Territories tab (the Strategic Ledger).
	_reset_between_scenes()
	var packed = load("res://scenes/strategic_ledger.tscn")
	if packed is PackedScene:
		var ledger = packed.instantiate()
		root.add_child(ledger)
		ledger.call("open", _api)
		ledger.call("_switch_tab", 1)
		var larea = ledger.get("content_area")
		_out["ledger_territories_text"] = larea.get_parsed_text() if larea != null else ""
		ledger.hide()

	# ── 10. Le Moniteur's Congress column.
	_reset_between_scenes()
	var gpacked = load("res://scenes/gazette_view.tscn")
	if gpacked is PackedScene:
		var gz = gpacked.instantiate()
		root.add_child(gz)
		gz.call("open", _api)
		var glabel = gz.get("content_label")
		_out["gazette_text"] = glabel.get_parsed_text() if glabel != null else ""
		gz.hide()

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
