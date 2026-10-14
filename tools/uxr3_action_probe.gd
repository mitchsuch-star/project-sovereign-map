extends SceneTree
# UXR-3 "The action probe" (Pre-Deploy S11, October 13, 2026) — the driven
# record behind R5 (Affordance) and R6 (Feedback) of docs/UX_CHECKLIST_V1.json.
#
#   $env:UXR3_PROBE_SPEC = "<absolute path to a spec JSON>"
#   <godot> --audio-driver Dummy --windowed --resolution 1920x1080 \
#           --position 5200,20 --log-file <abs log> \
#           --path godot-client/project-sovereign \
#           --script ../../tools/uxr3_action_probe.gd
#
# Do not write specs by hand: `tools/uxr3_action_probe.py` builds them from the
# IQ-10 manifest exactly as `tools/iq10_run_captures.py` does (the same
# payloads, scenes, entry methods and steps), so a probed surface is the
# surface the frames show. Per shot:
#
#   1. The surface is opened as the capture harness opens it. The frame is read
#      twice, 500 ms apart, with nothing pressed: whatever changes on its own
#      (a Ken Burns drift, a pulse) is set aside for the whole surface. The
#      LIVE frame's controls are listed: every visible BaseButton, every
#      visible non-button Control showing the pointing-hand cursor, every
#      visible non-button Control showing a resize cursor (a drag control,
#      S12 part 2), and every [url] link of a visible RichTextLabel. The live frame is R7's: the
#      layers at and above the topmost modal layer (a layer holding a visible
#      Control whose mouse filter is not IGNORE and which covers >= 95 % of the
#      logical viewport); what lies under a modal is suspended by it.
#   2. Each ENABLED control is pressed in a FRESH instance of the surface. A
#      button or pointing-hand control gets a synthetic left press and release
#      at its centre, as the player gives it (OS input stays disabled except
#      for those two frames). When the click never reaches the control (another
#      control takes it), the probe records that, re-opens the surface and
#      presses the control by its own signal. A link is pressed by its label's
#      meta_clicked. The frame is read before the press, 2 frames after it, and
#      again once 500 ms and at least 30 frames have passed.
#   3. The answer: VISIBLE when something on screen changed (a visible text, a
#      node shown or hidden, a control's rect, a button's pressed or disabled
#      state, the focus owner other than onto the pressed control itself, a
#      visible window, a Camera2D); HANDOFF when the only response was an API
#      call the stub recorded or a script signal some node emitted; SILENT when
#      nothing at all happened.
#
# Words that change the scene, quit, save, load or start a new game, and links
# to an outside address, are listed NOT PRESSED. Disabled controls are listed
# with their tooltip and the words beside them.
#
# WAR-ROOM MODE (Pre-Deploy S12 part 2, the R6 driven proofs): a spec with
# `"war_room": true` names one ROAD per entry (`road`: kind / text /
# meta_startswith / path_endswith). The surface is opened INSIDE the real
# main.tscn, whose REAL APIClient talks to a sandboxed live backend (the
# runner starts it; 8005 is refused): a screen with the shot's own payload
# through the top bar's own open road, a panel or dialog through main's own
# instance of it. The road's first matching control is pressed and the answer
# read in the LIVE frame only — a change under a modal screen (the terminal's
# echo beneath the Generals) is no answer; a screen that closes onto the
# terminal, a popup that opens, the scene that changes (the Main Menu stands)
# are. A quit is proven by the runner: the engine exits after the press.
#
# Rails (IQ-10's): UiSettings on an in-memory ConfigFile with `_persist` false;
# every API stubbed and main.tscn refused while SOVEREIGN_PORT points at the
# player's 8005; audio on the Dummy driver (the runner's flag); the window
# parked past the desktop. The result is written after EVERY shot and a
# progress marker before every press, so a crash costs one control, and the
# runner resumes after it.

const SETTLE_DEFAULT := 30
const OBSERVE_MS := 500
const OBSERVE_MIN_FRAMES := 30
const MODAL_COVER := 0.95
const MAX_CHANGES := 10
# S12 part 2 (UXR3-74): a DRAG control — a visible non-button Control taking
# the mouse whose default cursor is a resize shape (the ResizeGrip). It is
# pressed as the player uses it: a press at its centre, two motions of
# DRAG_STEP down and right, a release; it answers VISIBLE when any control's
# rect changed.
const DRAG_CURSORS := [Control.CURSOR_FDIAGSIZE, Control.CURSOR_BDIAGSIZE,
		Control.CURSOR_HSIZE, Control.CURSOR_VSIZE]
const DRAG_STEP := Vector2(20.0, 20.0)

class ApiStub extends Node:
	var responses: Dictionary = {}
	var calls: Array = []

	func _answer(method: String, cb: Callable) -> void:
		calls.append(method)
		var r = responses.get(method, null)
		if not (r is Dictionary):
			r = {"success": false, "message": "uxr3 probe stub: no payload for " + method}
		if r.has("nation_display_overrides"):
			var names = r.get("nation_display_overrides")
			var flags = r.get("nation_flag_overrides")
			if names is Dictionary:
				Utils.set_formation_overrides(names, flags if flags is Dictionary else {})
		cb.call(r)

	func get_ledger(cb: Callable): _answer("get_ledger", cb)
	func get_diplomatic_ledger(cb: Callable): _answer("get_diplomatic_ledger", cb)
	func get_marshal_overview(cb: Callable): _answer("get_marshal_overview", cb)
	func get_dispatch(cb: Callable): _answer("get_dispatch", cb)
	func get_gazette(cb: Callable): _answer("get_gazette", cb)
	func get_campaign_log(cb: Callable): _answer("get_campaign_log", cb)
	func get_mailbox(cb: Callable): _answer("get_mailbox", cb)
	func get_pending_envoy(cb: Callable): _answer("get_pending_envoy", cb)
	func send_command(_c, _cb = null): calls.append("send_command")
	func cancel_strategic_order(_m, _cb = null): calls.append("cancel_strategic_order")
	func dismiss_notification(_i, _cb = null): calls.append("dismiss_notification")
	func dismiss_all_notifications(_cb = null): calls.append("dismiss_all_notifications")


class MainStub extends Node:
	var responses: Dictionary = {}
	var calls: Array = []

	func _answer(method: String, cb):
		calls.append(method)
		if cb is Callable:
			var r = responses.get(method, null)
			if not (r is Dictionary):
				r = {"success": false, "message": "uxr3 probe main stub: no payload for " + method}
			cb.call(r)

	func test_connection(cb = null): _answer("test_connection", cb)
	func get_map_topology(cb = null): _answer("get_map_topology", cb)
	func get_ledger(cb = null): _answer("get_ledger", cb)
	func get_diplomatic_ledger(cb = null): _answer("get_diplomatic_ledger", cb)
	func get_marshal_overview(cb = null): _answer("get_marshal_overview", cb)
	func get_dispatch(cb = null): _answer("get_dispatch", cb)
	func get_gazette(cb = null): _answer("get_gazette", cb)
	func get_campaign_log(cb = null): _answer("get_campaign_log", cb)
	func get_campaign_end(cb = null): _answer("get_campaign_end", cb)
	func get_marshal_trust(_m, cb = null): _answer("get_marshal_trust", cb)
	func get_llm_config(cb = null): _answer("get_llm_config", cb)
	func get_mailbox(_cb = null): calls.append("get_mailbox")
	func get_pending_envoy(_cb = null): calls.append("get_pending_envoy")
	func get_marshal_petition(_cb = null): calls.append("get_marshal_petition")
	func get_pending_redemption(_cb = null): calls.append("get_pending_redemption")
	func list_saves(_cb = null): calls.append("list_saves")
	func load_game(_f, _cb = null): calls.append("load_game")
	func save_game(_f, _cb = null): calls.append("save_game")
	func new_game(_cb = null, _scenario = ""): calls.append("new_game")
	func set_llm_key(_k, _cb = null): calls.append("set_llm_key")
	func send_command(_c, _cb = null, _relayed = false): calls.append("send_command")
	func send_structured_command(_c, _d = null, _cb = null): calls.append("send_structured_command")
	func send_dialogue_response(_c, _cb = null, _id = -1): calls.append("send_dialogue_response")
	func send_dialogue_response_with_params(_c, _p = null, _cb = null, _id = -1): calls.append("send_dialogue_response_with_params")
	func send_capture_choice_response(_c, _cb = null, _id = -1): calls.append("send_capture_choice_response")
	func send_strategic_response(_m, _t = null, _c = null, _cb = null): calls.append("send_strategic_response")
	func send_objection_response(_c, _cb = null): calls.append("send_objection_response")
	func send_marshal_petition_response(_c, _cb = null): calls.append("send_marshal_petition_response")
	func send_glorious_charge_response(_c, _cb = null): calls.append("send_glorious_charge_response")
	func send_diplomatic_objection_response(_c, _d = null, _cb = null): calls.append("send_diplomatic_objection_response")
	func send_redemption_response(_c, _cb = null): calls.append("send_redemption_response")
	func activate_mailbox_item(_i, _cb = null): calls.append("activate_mailbox_item")
	func respond_to_mailbox_item(_i, _c = null, _cb = null): calls.append("respond_to_mailbox_item")
	func cancel_strategic_order(_m, _cb = null): calls.append("cancel_strategic_order")
	func dismiss_notification(_i, _cb = null): calls.append("dismiss_notification")
	func dismiss_all_notifications(_cb = null): calls.append("dismiss_all_notifications")


class MapStub extends Node:
	var region_full_data: Dictionary = {}
	var region_visibility: Dictionary = {}
	var region_marshals: Dictionary = {}
	var region_garrisons: Dictionary = {}
	var levy_status: Dictionary = {}
	var naval_overlay: Dictionary = {}
	var action_pools: Dictionary = {}

	func load_game_state(gs: Dictionary) -> void:
		var map_data = gs.get("map_data", {})
		if not (map_data is Dictionary):
			map_data = {}
		region_full_data = map_data
		for region_name in map_data:
			var data = map_data[region_name]
			if not (data is Dictionary):
				continue
			var vis = data.get("visibility_status", "full")
			region_visibility[region_name] = "full" if vis == null else vis
			var marshals = data.get("marshals", [])
			if marshals is Array and not marshals.is_empty():
				region_marshals[region_name] = marshals
			var g = int(data.get("garrison_strength", 0))
			if g != 0:
				region_garrisons[region_name] = {
					"strength": g,
					"detachment": data.get("garrison_detachment", false),
					"band": data.get("garrison_strength_band", ""),
				}
		var levy = gs.get("levy", {})
		levy_status = levy if levy is Dictionary else {}
		var naval = gs.get("naval_overlay", {})
		naval_overlay = naval if naval is Dictionary else {}
		var pools = gs.get("action_pools", {})
		action_pools = pools if pools is Dictionary else {}


var _spec: Dictionary = {}
var _result_path := ""
var _results: Array = []
var _backdrop: CanvasLayer = null
var _baseline_children: Array = []
var _node: Node = null
var _stubs: Array = []
var _payload = null
var _errors: Array = []
var _stray := 0
var _emitted: Array = []
var _connections: Array = []
var _fatal := ""
var _scale := 1.0
var _initial_cfg := ""
var _war_room := false
var _main: Node = null
const MAIN_SCENE := "res://scenes/main.tscn"
const WAR_ROOM_BOOT_MS := 30000
const WAR_ROOM_IDLE_MS := 15000
var _quit_re := RegEx.create_from_string("(?i)^\\s*(quit|exit)\\b")
var _norm_re := RegEx.create_from_string("@([A-Za-z0-9_]+)@[0-9]+")
var _url_re := RegEx.create_from_string("(?s)\\[url(?:=([^\\]]*))?\\](.*?)\\[/url\\]")
var _tag_re := RegEx.create_from_string("\\[[^\\]]*\\]")
var _img_re := RegEx.create_from_string("(?s)\\[img[^\\]]*\\].*?\\[/img\\]")
# A label LEADS with its verb ("Save Game", "Load a campaign", "Quit"); the
# Menu button's tooltip only LISTS "Save, Load, Settings" and is pressed.
# (The diorama's "Replay" replays its own tableau: it is pressed.)
var _never_re := RegEx.create_from_string("(?i)^\\s*(quit|exit|load|save|new game|new campaign|begin)\\b|\\bmain menu\\b")
var _outside_re := RegEx.create_from_string("(?i)^(https?:|mailto:|file:|www\\.)")


func _init():
	UiSettings._cfg = ConfigFile.new()
	var settings_class: Variant = UiSettings
	settings_class.set("_persist", false)
	_run.call_deferred()


# ── plumbing ────────────────────────────────────────────────────────────────

func _wait_frames(n: int) -> void:
	for _i in range(n):
		await process_frame


func _observe_wait() -> void:
	var t0 := Time.get_ticks_msec()
	var f := 0
	while Time.get_ticks_msec() - t0 < OBSERVE_MS or f < OBSERVE_MIN_FRAMES:
		await process_frame
		f += 1


func _read_json(path: String):
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return null
	var parsed = JSON.parse_string(f.get_as_text())
	f.close()
	return parsed


func _write_json(path: String, value) -> void:
	if path == "":
		return
	DirAccess.make_dir_recursive_absolute(path.get_base_dir())
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f != null:
		f.store_string(JSON.stringify(value, " "))
		f.close()


func _norm(path: String) -> String:
	return _norm_re.sub(path, "@$1@", true)


func _path(n: Node) -> String:
	return _norm(str(root.get_path_to(n)))


func _all_nodes(from: Node) -> Array:
	var out: Array = []
	var stack: Array = [from]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		out.append(n)
		var kids := n.get_children()
		for i in range(kids.size() - 1, -1, -1):
			stack.append(kids[i])
	return out


func _inside_subviewport(n: Node) -> bool:
	var p: Node = n.get_parent()
	while p != null:
		if p is SubViewport:
			return true
		p = p.get_parent()
	return false


func _shown(n: Node) -> bool:
	if not (n is CanvasItem) or not (n as CanvasItem).is_visible_in_tree():
		return false
	var p: Node = n.get_parent()
	while p != null:
		if p is SubViewport:
			var holder: Node = p.get_parent()
			if holder is CanvasItem and not (holder as CanvasItem).is_visible_in_tree():
				return false
		p = p.get_parent()
	return true


func _layer_of(n: Node) -> int:
	var p: Node = n
	while p != null:
		if p is CanvasLayer:
			return (p as CanvasLayer).layer
		p = p.get_parent()
	return 0


func _ours(n: Node) -> bool:
	if n == _backdrop:
		return true
	for s in _stubs:
		if is_instance_valid(s) and (n == s or s.is_ancestor_of(n)):
			return true
	return _backdrop != null and _backdrop.is_ancestor_of(n)


func _on_stray(event: InputEvent) -> void:
	if event is InputEventKey or event is InputEventMouseButton:
		_stray += 1


# ── the run ─────────────────────────────────────────────────────────────────

func _run() -> void:
	var spec_path := OS.get_environment("UXR3_PROBE_SPEC")
	var parsed = _read_json(spec_path) if spec_path != "" else null
	if not (parsed is Dictionary):
		_fatal = "UXR3_PROBE_SPEC missing or unparsable: " + spec_path
		_finish()
		return
	_spec = parsed
	_result_path = str(_spec.get("result", ""))
	_war_room = bool(_spec.get("war_room", false))
	if _war_room and Utils.backend_url().ends_with(":8005"):
		_fatal = "war-room mode refused: SOVEREIGN_PORT still points at the player's 8005"
		_finish()
		return
	root.mode = Window.MODE_WINDOWED
	root.gui_disable_input = true
	if not root.window_input.is_connected(_on_stray):
		root.window_input.connect(_on_stray)
	var pos = _spec.get("window_position", [5200, 20])
	root.position = Vector2i(int(pos[0]), int(pos[1]))
	var win = _spec.get("window", [1920, 1080])
	root.size = Vector2i(int(win[0]), int(win[1]))
	_scale = float(_spec.get("scale", 1.0))
	UiSettings._cfg.set_value("display", "ui_scale", _scale)
	UiSettings._cfg.set_value("display", "text_size", 1.0)
	UiSettings._cfg.set_value("display", "high_contrast", false)
	UiSettings._cfg.set_value("display", "hud_width", "full")
	if _war_room:
		# The first-run card is the menu's, not the road's.
		UiSettings._cfg.set_value("display", "scale_acknowledged", true)
	# Every fresh instance starts from THIS state: a press that writes a
	# setting (the war room's Scale +, the first-run card's Looks right, a
	# Settings row) writes the in-memory config, which outlives the instance
	# — the next instance then booted at another scale and the probe's clicks
	# landed beside their controls.
	_initial_cfg = UiSettings._cfg.encode_to_text()
	_reset_settings()
	_backdrop = CanvasLayer.new()
	_backdrop.layer = -100
	_backdrop.name = "UXR3Backdrop"
	var rect := ColorRect.new()
	rect.color = Color(0.07, 0.09, 0.13, 1.0)
	rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_backdrop.add_child(rect)
	root.add_child(_backdrop)
	await _wait_frames(10)
	_baseline_children = root.get_children()
	var resume = _spec.get("resume", {})
	var skip_shot := str(resume.get("shot", "")) if resume is Dictionary else ""
	var skip_through := int(resume.get("skip_through", -1)) if resume is Dictionary else -1
	for shot in _spec.get("shots", []):
		if not (shot is Dictionary):
			continue
		var rec: Dictionary = await _probe_shot(shot, skip_through if str(shot.get("id", "")) == skip_shot else -1)
		_results.append(rec)
		_write_result(false)
	_finish()


func _write_result(done: bool) -> void:
	_write_json(_result_path, {
		"harness": "tools/uxr3_action_probe.gd",
		"godot": Engine.get_version_info().get("string", ""),
		"done": done,
		"fatal": _fatal,
		"stray_input": _stray,
		"window": [root.size.x, root.size.y],
		"scale": root.content_scale_factor,
		"results": _results,
	})


func _progress(shot_id: String, index: int, quits := false) -> void:
	_write_json(_result_path + ".progress.json", {"shot": shot_id, "control": index,
			"quit": quits, "at_ms": Time.get_ticks_msec()})


func _finish() -> void:
	_write_result(true)
	print("[UXR3] DONE shots=%d fatal=%s" % [_results.size(), _fatal])
	quit(0 if _fatal == "" else 1)


# ── one surface ─────────────────────────────────────────────────────────────

func _probe_shot(shot: Dictionary, skip_through: int) -> Dictionary:
	if _war_room:
		return await _probe_road(shot)
	var sid := str(shot.get("id", ""))
	var rec := {"id": sid, "scene": str(shot.get("scene", "")), "controls": [], "errors": []}
	print("[UXR3] BEGIN " + sid)
	var opened: bool = await _open(shot)
	rec["errors"] = _errors.duplicate()
	if not opened:
		rec["reached"] = false
		await _close()
		print("[UXR3] END %s reached=false" % sid)
		return rec
	rec["reached"] = true
	var b0 := _snapshot()
	await _observe_wait()
	var b1 := _snapshot()
	var animated := _changed(b0, b1, "")
	rec["animated"] = animated.keys()
	var live := _live_floor()
	rec["live_floor"] = live["floor"]
	rec["modal_layers"] = live["modal"]
	var controls := _enumerate(int(live["floor"]))
	for c in controls:
		c.erase("_node")
	rec["control_count"] = controls.size()
	await _close()
	for i in range(controls.size()):
		var c: Dictionary = controls[i]
		c["i"] = i
		if i <= skip_through:
			c["result"] = "CRASHED" if i == skip_through else "SKIPPED (resumed)"
			rec["controls"].append(c)
			continue
		if bool(c.get("disabled", false)):
			c["result"] = "DISABLED"
			rec["controls"].append(c)
			continue
		var never := _never_reason(c, str(shot.get("scene", "")))
		if never != "":
			c["result"] = "NOT PRESSED"
			c["why_not"] = never
			rec["controls"].append(c)
			continue
		_progress(sid, i)
		print("[UXR3] PRESS %s %d %s" % [sid, i, str(c.get("text", c.get("meta", "")))])
		var res: Dictionary = await _press_one(shot, c, i, animated)
		rec["controls"].append(res)
	print("[UXR3] END %s controls=%d" % [sid, controls.size()])
	return rec


func _probe_road(shot: Dictionary) -> Dictionary:
	# War-room mode: ONE control per entry, pressed in the instance it was
	# found in (the instance is fresh: each entry boots its own war room).
	var sid := str(shot.get("id", ""))
	var road: Dictionary = shot.get("road", {})
	var rec := {"id": sid, "base_id": str(shot.get("base_id", sid)),
		"scene": str(shot.get("scene", "")), "road": road, "controls": [], "errors": []}
	print("[UXR3] BEGIN " + sid)
	var opened: bool = await _open(shot)
	rec["errors"] = _errors.duplicate()
	rec["reached"] = opened
	rec["backend"] = Utils.backend_url()
	if not opened:
		await _close()
		print("[UXR3] END %s reached=false" % sid)
		return rec
	var b0 := _snapshot()
	await _observe_wait()
	var b1 := _snapshot()
	var animated := _changed(b0, b1, "")
	var live := _live_floor()
	rec["live_floor"] = live["floor"]
	var controls := _enumerate(int(live["floor"]))
	rec["control_count"] = controls.size()
	var pick := -1
	for i in range(controls.size()):
		if _matches_road(controls[i], road):
			pick = i
			break
	if pick < 0:
		rec["errors"].append("no control of the live frame matches the road " + JSON.stringify(road))
		await _close()
		print("[UXR3] END %s no match" % sid)
		return rec
	var c: Dictionary = controls[pick]
	var target = c.get("_node")
	c.erase("_node")
	c["i"] = pick
	var quits := _quit_re.search(str(c.get("text", "")).strip_edges()) != null
	_progress(sid, pick, quits)
	print("[UXR3] PRESS %s %d %s" % [sid, pick, str(c.get("text", c.get("meta", "")))])
	var outcome: Dictionary = await _press_and_read(target, c, animated, true)
	if outcome.get("taken_by", null) != null:
		# the click never landed (nothing happened): press by its own signal
		var taken = outcome["taken_by"]
		outcome = await _press_and_read(target, c, animated, false)
		outcome["taken_by"] = taken
	for k in outcome:
		c[k] = outcome[k]
	rec["controls"].append(c)
	await _wait_api_idle()
	await _close()
	print("[UXR3] END %s %s" % [sid, str(c.get("result", ""))])
	return rec


func _matches_road(c: Dictionary, road: Dictionary) -> bool:
	if road.has("kind") and str(c.get("kind", "")) != str(road["kind"]):
		return false
	if road.has("text") and str(c.get("text", "")).strip_edges() != str(road["text"]):
		return false
	if road.has("meta_startswith") and not str(c.get("meta", "")).begins_with(str(road["meta_startswith"])):
		return false
	if road.has("path_endswith") and not str(c.get("path", "")).ends_with(str(road["path_endswith"])):
		return false
	return not bool(c.get("disabled", false))


func _api_idle() -> bool:
	var api = _main.get("api_client") if _main != null and is_instance_valid(_main) else null
	if api == null or not is_instance_valid(api):
		return true
	var busy = bool(api.get("_request_in_flight"))
	var queue = api.get("_request_queue")
	return not busy and (queue == null or queue.is_empty())


func _wait_api_idle() -> void:
	var start := Time.get_ticks_msec()
	var calm := 0
	while Time.get_ticks_msec() - start < WAR_ROOM_IDLE_MS:
		await process_frame
		if _api_idle():
			calm += 1
			if calm >= 6:
				return
		else:
			calm = 0


func _never_reason(c: Dictionary, scene: String) -> String:
	if str(c.get("kind", "")) == "link":
		var meta := str(c.get("meta", ""))
		if _outside_re.search(meta) != null:
			return "a link to an outside address"
		return ""
	# The label the player reads: the button's words, or its tooltip when it
	# is an icon.
	var words := str(c.get("text", "")).strip_edges()
	if words == "":
		words = str(c.get("tooltip", "")).strip_edges()
	var m := _never_re.search(words)
	if m != null:
		return "its words ('%s') change the scene, quit, save, load or start a game" % m.get_string(0)
	if scene.ends_with("main_menu.tscn") and words.to_lower().begins_with("continue"):
		return "the menu's Continue loads the last save (a scene change)"
	return ""


func _press_one(shot: Dictionary, c: Dictionary, i: int, animated: Dictionary) -> Dictionary:
	var res := c.duplicate(true)
	var opened: bool = await _open(shot)
	if not opened:
		res["result"] = "LOST"
		res["why"] = "the fresh instance did not open: " + str(_errors)
		await _close()
		return res
	var target = _find_control(c, i)
	if target == null:
		res["result"] = "LOST"
		res["why"] = "the fresh instance holds no such control"
		await _close()
		return res
	var outcome: Dictionary = await _press_and_read(target, c, animated, true)
	if outcome.get("taken_by", null) != null:
		# the click went elsewhere: record what took it, re-open, press by signal
		var taken = outcome["taken_by"]
		await _close()
		opened = await _open(shot)
		target = _find_control(c, i) if opened else null
		if target == null:
			res["result"] = "LOST"
			res["why"] = "re-opened after a taken click and lost the control"
			res["taken_by"] = taken
			await _close()
			return res
		outcome = await _press_and_read(target, c, animated, false)
		outcome["taken_by"] = taken
	for k in outcome:
		res[k] = outcome[k]
	await _close()
	return res


func _press_and_read(target: Node, c: Dictionary, animated: Dictionary, click: bool) -> Dictionary:
	var out := {}
	var tpath := _path(target)
	if target is Control:
		_scroll_into_view(target as Control)
		await _wait_frames(2)
	var calls0 := _stub_calls().size()
	_arm_recorders()
	var before := _snapshot()
	var method := ""
	var reached := true
	var is_drag := str(c.get("kind", "")) == "drag"
	if str(c.get("kind", "")) == "link":
		(target as RichTextLabel).emit_signal("meta_clicked", c.get("meta_value", c.get("meta", "")))
		method = "meta_clicked"
	elif is_drag and click:
		var dctrl := target as Control
		var from := dctrl.get_global_rect().get_center()
		var got_drag := [false]
		var dcb := func(ev):
			if ev is InputEventMouseButton:
				got_drag[0] = true
		dctrl.gui_input.connect(dcb)
		root.gui_disable_input = false
		_mouse(from, true)
		await process_frame
		_motion(from + DRAG_STEP, from)
		await process_frame
		_motion(from + 2.0 * DRAG_STEP, from + DRAG_STEP)
		await process_frame
		_mouse(from + 2.0 * DRAG_STEP, false)
		await process_frame
		root.gui_disable_input = true
		if is_instance_valid(dctrl) and dctrl.gui_input.is_connected(dcb):
			dctrl.gui_input.disconnect(dcb)
		if got_drag[0]:
			method = "drag"
		else:
			reached = false
			out["taken_by"] = _cover_at(from, dctrl)
	elif is_drag:
		method = "drag by gui_input (the press was taken)"
		_signal_drag(target as Control)
	elif click:
		var ctrl := target as Control
		var at := ctrl.get_global_rect().get_center()
		if not root.get_visible_rect().has_point(at):
			method = "signal (off-screen)"
			_signal_press(target)
		else:
			var got := [false]
			var cb := func(ev):
				if ev is InputEventMouseButton:
					got[0] = true
			ctrl.gui_input.connect(cb)
			root.gui_disable_input = false
			_mouse(at, true)
			await process_frame
			_mouse(at, false)
			await process_frame
			root.gui_disable_input = true
			# A control its own press frees (a rail row rebuilt) was reached.
			var gone := not is_instance_valid(ctrl)
			if not gone and ctrl.gui_input.is_connected(cb):
				ctrl.gui_input.disconnect(cb)
			if got[0] or gone:
				method = "click"
			else:
				reached = false
				out["taken_by"] = _cover_at(at, ctrl)
	else:
		method = "signal (the click was taken)"
		_signal_press(target)
	if not reached:
		_disarm_recorders()
		return out
	out["method"] = method
	await _wait_frames(2)
	var a2 := _snapshot()
	await _observe_wait()
	var a3 := _snapshot()
	var changed := _changed(before, a2, tpath)
	var later := _changed(before, a3, tpath)
	for k in later:
		changed[k] = later[k]
	for k in animated:
		changed.erase(k)
	if _war_room:
		changed = _live_only(changed, [before, a2, a3])
	var calls := _stub_calls().slice(calls0)
	var signals := _emitted.duplicate()
	_disarm_recorders()
	out["n_changed"] = changed.size()
	out["changes"] = _describe(changed)
	out["api_calls"] = calls
	out["signals"] = signals.slice(0, 12)
	var moved := false
	for k in changed:
		if str(k).begins_with("r:"):
			moved = true
			break
	if is_drag:
		# A drag answers by moving something; anything else it did is not
		# the answer it promises.
		if moved:
			out["result"] = "VISIBLE"
		elif not calls.is_empty() or not signals.is_empty():
			out["result"] = "HANDOFF"
		else:
			out["result"] = "SILENT"
	elif not changed.is_empty():
		out["result"] = "VISIBLE"
	elif not calls.is_empty() or not signals.is_empty():
		out["result"] = "HANDOFF"
	else:
		out["result"] = "SILENT"
	return out


func _live_only(changed: Dictionary, snaps: Array) -> Dictionary:
	# A change counts only on a node at or above the lowest live floor of the
	# three reads: a screen that closes drops the floor (the terminal under it
	# is live again), a popup that opens raises it (and is itself the change);
	# the terminal's echo beneath a standing screen is no answer.
	var floor_now := 1000000
	var layers := {}
	for snap in snaps:
		floor_now = mini(floor_now, int(snap.get("__floor", -1000000)))
		var l = snap.get("__layers", {})
		for path in l:
			layers[path] = l[path]
	var out := {}
	for k in changed:
		var key := str(k)
		if key == "s" or key.begins_with("w:"):
			out[k] = changed[k]
		elif key == "f" or key.begins_with("c:"):
			if floor_now < 0:          # the war room's own focus and camera
				out[k] = changed[k]
		elif int(layers.get(key.substr(2), 0)) >= floor_now:
			out[k] = changed[k]
	return out


func _signal_press(target: Node) -> void:
	if target is BaseButton:
		var b := target as BaseButton
		if b.toggle_mode:
			b.button_pressed = not b.button_pressed
		b.emit_signal("pressed")
	elif target is Control:
		var ctrl := target as Control
		for pressed in [true, false]:
			var ev := InputEventMouseButton.new()
			ev.button_index = MOUSE_BUTTON_LEFT
			ev.pressed = pressed
			ev.position = ctrl.size * 0.5
			ev.global_position = ctrl.get_global_rect().get_center()
			ctrl.emit_signal("gui_input", ev)
			if ctrl.has_method("_gui_input"):
				ctrl.call("_gui_input", ev)


func _signal_drag(ctrl: Control) -> void:
	# The drag fed to the control's own gui_input, when another control took
	# the press: the same press, two motions and release.
	var from := ctrl.get_global_rect().get_center()
	var steps := [[true, from], [null, from + DRAG_STEP], [null, from + 2.0 * DRAG_STEP],
			[false, from + 2.0 * DRAG_STEP]]
	for st in steps:
		var ev: InputEventMouse
		if st[0] == null:
			var mm := InputEventMouseMotion.new()
			mm.button_mask = MOUSE_BUTTON_MASK_LEFT
			mm.relative = DRAG_STEP
			ev = mm
		else:
			var mb := InputEventMouseButton.new()
			mb.button_index = MOUSE_BUTTON_LEFT
			mb.pressed = st[0]
			ev = mb
		ev.position = st[1] - ctrl.get_global_rect().position
		ev.global_position = st[1]
		ctrl.emit_signal("gui_input", ev)
		if ctrl.has_method("_gui_input"):
			ctrl.call("_gui_input", ev)


func _motion(pos: Vector2, prev: Vector2) -> void:
	var ev := InputEventMouseMotion.new()
	ev.button_mask = MOUSE_BUTTON_MASK_LEFT
	ev.position = pos
	ev.global_position = pos
	ev.relative = pos - prev
	root.push_input(ev)


func _mouse(pos: Vector2, pressed: bool) -> void:
	var ev := InputEventMouseButton.new()
	ev.button_index = MOUSE_BUTTON_LEFT
	ev.pressed = pressed
	ev.button_mask = MOUSE_BUTTON_MASK_LEFT if pressed else 0
	ev.position = pos
	ev.global_position = pos
	root.push_input(ev)


func _scroll_into_view(ctrl: Control) -> void:
	var p: Node = ctrl.get_parent()
	while p != null:
		if p is ScrollContainer:
			(p as ScrollContainer).ensure_control_visible(ctrl)
		p = p.get_parent()


func _cover_at(at: Vector2, target: Control) -> String:
	# The topmost visible input-taking Control at the point, by layer then tree
	# order — what the click most likely reached instead of the target.
	var best := ""
	var best_layer := -1000000
	for n in _all_nodes(root):
		if not (n is Control) or _ours(n) or not _shown(n) or _inside_subviewport(n):
			continue
		var ctrl := n as Control
		if ctrl == target or target.is_ancestor_of(ctrl):
			continue
		if ctrl.mouse_filter == Control.MOUSE_FILTER_IGNORE:
			continue
		if not ctrl.get_global_rect().has_point(at):
			continue
		var layer := _layer_of(ctrl)
		if layer >= best_layer:
			best_layer = layer
			best = "%s (%s, layer %d)" % [_path(ctrl), ctrl.get_class(), layer]
	return best


# ── the frame read ──────────────────────────────────────────────────────────

func _snapshot() -> Dictionary:
	var snap := {}
	var layers := {}
	for n in _all_nodes(root):
		if _ours(n):
			continue
		if n is Window and n != root:
			if (n as Window).visible:
				snap["w:" + _path(n)] = true
			continue
		if n is Camera2D and (n as Camera2D).is_inside_tree() and (n as Camera2D).is_current():
			var cam := n as Camera2D
			snap["c:" + _path(n)] = [snappedf(cam.zoom.x, 0.001), roundf(cam.global_position.x), roundf(cam.global_position.y)]
			continue
		if not _shown(n):
			continue
		var p := _path(n)
		snap["v:" + p] = true
		layers[p] = _layer_of(n)
		if n is Control:
			var r := (n as Control).get_global_rect()
			snap["r:" + p] = [roundf(r.position.x), roundf(r.position.y), roundf(r.size.x), roundf(r.size.y)]
		if n is RichTextLabel:
			snap["t:" + p] = (n as RichTextLabel).get_parsed_text()
		elif n is Label:
			snap["t:" + p] = (n as Label).text
		elif n is LineEdit:
			snap["t:" + p] = (n as LineEdit).text
		elif n is BaseButton:
			if "text" in n:
				snap["t:" + p] = str(n.text)
			snap["p:" + p] = [(n as BaseButton).button_pressed, (n as BaseButton).disabled]
	var fo: Control = root.gui_get_focus_owner()
	snap["f"] = _path(fo) if fo != null else ""
	# War-room mode reads the live frame (`_live_only`) and the scene change.
	snap["__layers"] = layers
	snap["__floor"] = int(_live_floor()["floor"])
	var cs: Node = current_scene
	snap["s"] = cs.scene_file_path if cs != null and is_instance_valid(cs) else ""
	return snap


func _changed(a: Dictionary, b: Dictionary, pressed_path: String) -> Dictionary:
	var out := {}
	for k in a:
		if str(k).begins_with("__"):
			continue
		if not b.has(k):
			out[k] = [a[k], null]
		elif not _same(a[k], b[k]):
			out[k] = [a[k], b[k]]
	for k in b:
		if not a.has(k) and not str(k).begins_with("__"):
			out[k] = [null, b[k]]
	if out.has("f") and pressed_path != "":
		var now = out["f"][1]
		if now is String and (now == pressed_path or now.begins_with(pressed_path + "/")):
			out.erase("f")
	return out


func _same(x, y) -> bool:
	if x is Array and y is Array and x.size() == y.size():
		for i in range(x.size()):
			if (x[i] is float or x[i] is int) and (y[i] is float or y[i] is int):
				if absf(float(x[i]) - float(y[i])) > 1.0:
					return false
			elif x[i] != y[i]:
				return false
		return true
	return x == y


func _describe(changed: Dictionary) -> Array:
	var out: Array = []
	var shown := 0
	var hidden := 0
	var texts: Array = []
	var other: Array = []
	var scene := ""
	for k in changed:
		var v = changed[k]
		if k.begins_with("v:"):
			if v[0] == null:
				shown += 1
			else:
				hidden += 1
		elif k.begins_with("t:"):
			texts.append(_text_change(k.substr(2).get_file(), v[0], v[1]))
		elif k == "s":
			scene = "the scene -> %s" % str(v[1]).get_file()
		elif k.begins_with("w:"):
			other.append("window %s %s" % [k.substr(2).get_file(), "opened" if v[0] == null else "closed"])
		elif k.begins_with("c:"):
			other.append("camera %s -> %s" % [str(v[0]), str(v[1])])
		elif k == "f":
			other.append("focus -> %s" % str(v[1]).get_file())
		elif k.begins_with("p:"):
			other.append("%s pressed/disabled %s -> %s" % [k.substr(2).get_file(), str(v[0]), str(v[1])])
	if scene != "":
		out.append(scene)    # a scene change leads: it is the answer
	if shown > 0:
		out.append("%d node(s) shown" % shown)
	if hidden > 0:
		out.append("%d node(s) hidden" % hidden)
	out.append_array(texts.slice(0, MAX_CHANGES))
	out.append_array(other.slice(0, MAX_CHANGES))
	var rects := 0
	for k in changed:
		if k.begins_with("r:"):
			rects += 1
	if rects > 0:
		out.append("%d rect(s) moved" % rects)
	return out


func _text_change(node: String, was, now) -> String:
	# A long label (a screen's whole BBCode body) changes deep inside: show
	# where. The first 40 characters when they differ; else the stretch from
	# the first character that differs.
	var a := str(was)
	var b := str(now)
	if was == null or now == null or a.left(40) != b.left(40):
		return "%s: '%s' -> '%s'" % [node, a.left(40), b.left(40)]
	var i := 0
	var n := mini(a.length(), b.length())
	while i < n and a[i] == b[i]:
		i += 1
	var from := maxi(0, i - 12)
	return "%s: at %d '…%s' -> '…%s'" % [node, i, a.substr(from, 60), b.substr(from, 60)]


func _stub_calls() -> Array:
	var out: Array = []
	for s in _stubs:
		if is_instance_valid(s) and ("calls" in s):
			out.append_array(s.calls)
	return out


func _arm_recorders() -> void:
	_emitted = []
	_connections = []
	for n in _all_nodes(root):
		if _ours(n):
			continue
		var scr = n.get_script()
		if not (scr is Script):
			continue
		for sig in (scr as Script).get_script_signal_list():
			var name := str(sig.get("name", ""))
			var argc := (sig.get("args", []) as Array).size()
			var cb := _on_signal.bind(_path(n), name)
			if argc > 0:
				cb = cb.unbind(argc)
			if not n.is_connected(name, cb):
				n.connect(name, cb)
				_connections.append([n, name, cb])


func _disarm_recorders() -> void:
	for c in _connections:
		var n = c[0]
		if is_instance_valid(n) and n.is_connected(c[1], c[2]):
			n.disconnect(c[1], c[2])
	_connections = []


func _on_signal(path: String, name: String) -> void:
	_emitted.append([path, name])


func _live_floor() -> Dictionary:
	var view := root.get_visible_rect()
	var area := view.size.x * view.size.y
	var modal: Array = []
	for n in _all_nodes(root):
		if not (n is Control) or _ours(n) or not _shown(n) or _inside_subviewport(n):
			continue
		var ctrl := n as Control
		if ctrl.mouse_filter == Control.MOUSE_FILTER_IGNORE:
			continue
		var r := ctrl.get_global_rect().intersection(view)
		if r.size.x * r.size.y >= MODAL_COVER * area:
			var layer := _layer_of(ctrl)
			if not modal.has(layer):
				modal.append(layer)
	var floor := -1000000
	for l in modal:
		floor = maxi(floor, int(l))
	modal.sort()
	return {"floor": floor, "modal": modal}


func _enumerate(floor: int) -> Array:
	var out: Array = []
	for n in _all_nodes(root):
		if _ours(n) or not _shown(n) or _inside_subviewport(n):
			continue
		if not (n is Control):
			continue
		var ctrl := n as Control
		var layer := _layer_of(ctrl)
		if layer < floor:
			continue
		var r := ctrl.get_global_rect()
		# `_node` is in-memory only (the press finds its control by it); the
		# record strips it.
		var base := {"path": _path(ctrl), "class": ctrl.get_class(), "layer": layer,
			"rect": [roundf(r.position.x), roundf(r.position.y), roundf(r.size.x), roundf(r.size.y)],
			"tooltip": str(ctrl.tooltip_text).left(160), "_node": ctrl}
		if ctrl is BaseButton:
			var b := ctrl as BaseButton
			base["kind"] = "button"
			base["text"] = (str(n.text) if ("text" in n) else "").left(80)
			base["disabled"] = b.disabled
			base["toggle"] = b.toggle_mode
			base["icon"] = ("icon" in n) and n.icon != null
			if b.disabled:
				base["beside"] = _beside(ctrl)
			out.append(base)
		elif ctrl.mouse_default_cursor_shape == Control.CURSOR_POINTING_HAND \
				and ctrl.mouse_filter != Control.MOUSE_FILTER_IGNORE:
			base["kind"] = "pointer"
			base["text"] = _own_text(ctrl).left(80)
			base["disabled"] = false
			out.append(base)
		elif ctrl.mouse_default_cursor_shape in DRAG_CURSORS \
				and ctrl.mouse_filter != Control.MOUSE_FILTER_IGNORE:
			base["kind"] = "drag"
			base["text"] = ""
			base["disabled"] = false
			out.append(base)
		if ctrl is RichTextLabel:
			var rtl := ctrl as RichTextLabel
			var k := 0
			for m in _url_re.search_all(rtl.text):
				var meta := m.get_string(1)
				var label := _tag_re.sub(_img_re.sub(m.get_string(2), "", true), "", true).strip_edges()
				var link := base.duplicate()
				link["kind"] = "link"
				link["class"] = "RichTextLabel [url]"
				link["meta"] = (meta if meta != "" else label).left(160)
				link["meta_value"] = meta if meta != "" else m.get_string(2)
				link["text"] = label.left(80)
				link["link_index"] = k
				link["disabled"] = false
				out.append(link)
				k += 1
	return out


func _find_control(c: Dictionary, i: int) -> Node:
	# The fresh instance is built from the same payload, so its live controls
	# list in the same order; the i-th is the one, checked by kind and path.
	var live := _live_floor()
	var now := _enumerate(int(live["floor"]))
	if i >= now.size():
		return null
	var d: Dictionary = now[i]
	if str(d.get("kind")) != str(c.get("kind")) or str(d.get("path")) != str(c.get("path")) \
			or str(d.get("text")) != str(c.get("text")):
		return null
	if str(d.get("kind")) == "link" and str(d.get("meta")) != str(c.get("meta")):
		return null
	# The node the enumeration itself walked to: a normalised path names
	# every auto-named sibling alike (`@Button@`), so a lookup by path alone
	# pressed the FIRST of them for all of them (the wizard's nation rows).
	return d.get("_node")


func _own_text(ctrl: Control) -> String:
	for n in _all_nodes(ctrl):
		if n is Label:
			return str((n as Label).text)
		if n is RichTextLabel:
			return (n as RichTextLabel).get_parsed_text()
	return ""


func _beside(ctrl: Control) -> String:
	var parts: Array = []
	var parent := ctrl.get_parent()
	if parent == null:
		return ""
	for sib in parent.get_children():
		if sib == ctrl or not (sib is CanvasItem) or not (sib as CanvasItem).is_visible_in_tree():
			continue
		var t := ""
		if sib is Label:
			t = (sib as Label).text
		elif sib is RichTextLabel:
			t = (sib as RichTextLabel).get_parsed_text()
		if t.strip_edges() != "":
			parts.append(t.strip_edges().left(100))
	return " | ".join(parts).left(240)


# ── open / close (the IQ-10 harness's road, as coroutines) ──────────────────

func _reset_settings() -> void:
	var cfg := ConfigFile.new()
	cfg.parse(_initial_cfg)
	UiSettings._cfg = cfg
	root.content_scale_factor = _scale
	var utils_class: Variant = Utils
	utils_class.call("apply_text_size")
	utils_class.call("apply_contrast")
	utils_class.call("apply_body_font")          # a Settings press may have chosen Plain
	utils_class.call("set_top_bar_drawn", float(Utils.TOP_BAR_HEIGHT))


func _open(shot: Dictionary) -> bool:
	if _war_room:
		return await _open_in_war_room(shot)
	_errors = []
	_reset_settings()
	var mode := str(shot.get("mode", "call"))
	var scene_path := str(shot.get("scene", ""))
	if mode == "main" or scene_path.ends_with("/main.tscn"):
		if Utils.backend_url().ends_with(":8005"):
			_errors.append("main.tscn refused: SOVEREIGN_PORT still points at the player's 8005")
			return false
	var packed = load(scene_path)
	if not (packed is PackedScene):
		_errors.append("scene did not load: " + scene_path)
		return false
	_payload = null
	if shot.has("payload"):
		_payload = _read_json(str(shot["payload"]))
		if _payload == null:
			_errors.append("payload did not parse: " + str(shot["payload"]))
			return false
	if _payload is Dictionary and _payload.get("nation_display_overrides") is Dictionary:
		var flags = _payload.get("nation_flag_overrides")
		Utils.set_formation_overrides(_payload["nation_display_overrides"], flags if flags is Dictionary else {})
	if shot.get("formation_overrides") is Dictionary:
		var fo: Dictionary = shot["formation_overrides"]
		Utils.set_formation_overrides(fo.get("names", {}), fo.get("flags", {}))
	_node = packed.instantiate()
	root.add_child(_node)
	if mode == "main":
		var stub := MainStub.new()
		stub.name = "APIClientStub"
		if _payload is Dictionary:
			if _payload.get("test") is Dictionary:
				stub.responses["test_connection"] = _payload["test"]
			if _payload.get("topology") is Dictionary:
				stub.responses["get_map_topology"] = _payload["topology"]
		var real = _node.get("api_client") if ("api_client" in _node) else null
		_node.add_child(stub)
		if "api_client" in _node:
			_node.set("api_client", stub)
		if real is Node:
			# main.gd hands its REAL client to the top bar and other nodes in
			# `_ready` (UXR-X14's trap): every reference is re-pointed to the
			# stub before the real one is freed, or a pressed nav button opens
			# a screen that calls a freed client.
			_repoint_api(real, stub)
			_node.remove_child(real)
			real.queue_free()
		_stubs.append(stub)
	return await _enter(shot)


func _enter(shot: Dictionary) -> bool:
	# The entry: the shot's stubs, its method and its steps, on `_node` (the
	# surface alone, or the war room's own instance of it).
	var mode := str(shot.get("mode", "call"))
	var place = shot.get("place", null)
	if place is Dictionary and _node is Control and not _war_room:
		var cc: Control = _node
		cc.set_anchors_preset(Control.PRESET_TOP_WIDE)
		var p = place.get("position", [0, 0])
		cc.position = Vector2(float(p[0]), float(p[1]))
		cc.size = Vector2(root.get_visible_rect().size.x, float(place.get("height", 60)))
	await _wait_frames(2)
	var method := str(shot.get("method", ""))
	var api: ApiStub = null
	var map: MapStub = null
	if mode == "api_stub":
		api = ApiStub.new()
		api.name = "UXR3ApiStub"
		var rmap = shot.get("responses", {})
		for m in rmap:
			var v = rmap[m]
			if v is String and v == "$payload":
				api.responses[m] = _payload
			elif v is String:
				api.responses[m] = _read_json(v)
			else:
				api.responses[m] = v
		if api.responses.is_empty() and _payload is Dictionary:
			api.responses[str(shot.get("api_method", "get_ledger"))] = _payload
		root.add_child(api)
		_stubs.append(api)
	elif mode == "map_stub":
		map = MapStub.new()
		map.name = "UXR3MapStub"
		var gs = _payload
		if gs is Dictionary and gs.get("game_state") is Dictionary:
			gs = gs["game_state"]
		if gs is Dictionary:
			map.load_game_state(gs)
		root.add_child(map)
		_stubs.append(map)
	if method != "":
		var default_args: Array = ["$payload"]
		if mode == "api_stub":
			default_args = ["$api"]
		var args := _resolve_args(shot.get("args", default_args), api, map)
		if not _node.has_method(method):
			_errors.append("entry method missing: " + method)
			return false
		if not (_war_room and mode == "api_stub" and _open_as_screen(api)):
			_node.callv(method, args)
	await _wait_frames(1)
	var steps = shot.get("steps", [])
	if steps is Array:
		for step in steps:
			if step is Dictionary:
				await _run_step(step.duplicate(true))
	await _wait_frames(int(shot.get("settle", SETTLE_DEFAULT)))
	return true


func _open_in_war_room(shot: Dictionary) -> bool:
	_errors = []
	_reset_settings()
	var scene_path := str(shot.get("scene", ""))
	_payload = null
	if shot.has("payload"):
		_payload = _read_json(str(shot["payload"]))
		if _payload == null:
			_errors.append("payload did not parse: " + str(shot["payload"]))
			return false
	if scene_path.ends_with("/main_menu.tscn"):
		# The title screen is its own scene: it stands alone, its real client
		# on the sandboxed backend.
		_node = (load(scene_path) as PackedScene).instantiate()
		root.add_child(_node)
		current_scene = _node
		await _wait_frames(int(shot.get("settle", SETTLE_DEFAULT)))
		var real_ms := int(shot.get("settle_ms", 0))
		if real_ms > 0:
			await create_timer(real_ms / 1000.0).timeout
		return true
	_main = (load(MAIN_SCENE) as PackedScene).instantiate()
	root.add_child(_main)
	current_scene = _main
	var start := Time.get_ticks_msec()
	while Time.get_ticks_msec() - start < WAR_ROOM_BOOT_MS:
		await process_frame
		if bool(_main.get("_initial_map_bootstrapped")) and _api_idle():
			break
	if not bool(_main.get("_initial_map_bootstrapped")):
		_errors.append("the war room did not boot against " + Utils.backend_url())
		return false
	await _wait_api_idle()
	await _wait_frames(10)
	if scene_path == MAIN_SCENE:
		_node = _main
	else:
		_node = _scene_in(_main, scene_path)
		if _node == null:
			_errors.append("the war room holds no " + scene_path)
			return false
	return await _enter(shot)


func _scene_in(from: Node, scene_path: String) -> Node:
	for n in _all_nodes(from):
		if n.scene_file_path == scene_path:
			return n
	return null


func _open_as_screen(api: Node) -> bool:
	# A top-bar screen opens by the bar's own road (its bookkeeping, the
	# button highlight, `screen_changed`), handed the stub that answers the
	# shot's payload; main.gd's own client stays on the live backend.
	var tb = _main.get("top_bar") if _main != null else null
	if tb == null:
		return false
	for screen_name in tb.screens:
		if tb.screens[screen_name] == _node:
			var real = tb.api_client
			tb.api_client = api
			tb.toggle_screen(screen_name)
			tb.api_client = real
			return true
	return false


func _repoint_api(real: Object, stub: Node) -> void:
	# Every script variable, on every node, that holds the real client.
	for n in _all_nodes(root):
		if n == real or n == stub or n.get_script() == null:
			continue
		for prop in n.get_property_list():
			if not (int(prop.get("usage", 0)) & PROPERTY_USAGE_SCRIPT_VARIABLE):
				continue
			var pname := str(prop.get("name", ""))
			var v = n.get(pname)
			if typeof(v) == TYPE_OBJECT and is_instance_valid(v) and v == real:
				n.set(pname, stub)


func _close() -> void:
	_disarm_recorders()
	if _node != null and is_instance_valid(_node):
		_node.queue_free()
	_node = null
	if _main != null and is_instance_valid(_main):
		_main.queue_free()
	_main = null
	if _war_room:
		current_scene = null
	for s in _stubs:
		if is_instance_valid(s):
			s.queue_free()
	_stubs = []
	for c in root.get_children():
		if not _baseline_children.has(c) and is_instance_valid(c):
			c.queue_free()
	AudioManager.stop_all_loops()
	AudioManager.stop_all_cues()
	Utils.set_formation_overrides({}, {})
	await _wait_frames(4)


func _run_step(step: Dictionary) -> void:
	if step.has("wait_for"):
		var target_node: Node = _node
		if step.has("node"):
			var held = _node.get(str(step["node"]).trim_prefix("@"))
			target_node = held if held is Node else _node
		var timeout := int(step.get("timeout", 1800))
		var spent := 0
		while not _read_path(target_node, str(step["wait_for"])):
			if spent >= timeout:
				_errors.append("wait_for timed out: " + str(step["wait_for"]))
				break
			await process_frame
			spent += 1
		if step.has("then_wait"):
			await _wait_frames(int(step["then_wait"]))
		return
	if step.has("wait"):
		await _wait_frames(int(step["wait"]))
		return
	if step.has("shot"):
		return
	var target: Node = _node
	if step.has("node"):
		var want := str(step["node"])
		if want.begins_with("@"):
			var held = _node.get(want.substr(1))
			target = held if held is Node else null
		else:
			target = _node.get_node_or_null(want)
		if target == null:
			_errors.append("step node missing: " + want)
			return
	if step.has("call"):
		var m := str(step["call"])
		if not target.has_method(m):
			_errors.append("step method missing: " + m)
		else:
			target.callv(m, _resolve_args(step.get("args", []), null, null))
	elif step.has("set_path"):
		_set_path(target, str(step["set_path"]), _resolve_value(step.get("value"), null, null))
	elif step.has("press"):
		_step_press(target, step["press"])
	elif step.has("scroll_to"):
		_scroll_to(step["scroll_to"])
	if step.has("then_wait"):
		await _wait_frames(int(step["then_wait"]))


func _resolve_args(raw, api, map) -> Array:
	var out: Array = []
	if not (raw is Array):
		return out
	for a in raw:
		out.append(_resolve_value(a, api, map))
	return out


func _resolve_value(a, api, map):
	if a is String:
		if a == "$payload":
			return _payload
		if a == "$api":
			return api if api != null else _first_stub(ApiStub)
		if a == "$map":
			return map if map != null else _first_stub(MapStub)
		if a == "$null":
			return null
		if a.begins_with("$payload."):
			return _dig(_payload, a.substr("$payload.".length()))
		return a
	if a is float and is_equal_approx(a, roundf(a)):
		return int(a)
	return a


func _first_stub(kind):
	for s in _stubs:
		if is_instance_of(s, kind):
			return s
	return null


func _dig(value, path: String):
	var cur = value
	for seg in path.split("."):
		if cur is Dictionary:
			cur = cur.get(seg, null)
		elif cur is Array and seg.is_valid_int() and int(seg) < cur.size():
			cur = cur[int(seg)]
		else:
			return null
	return cur


func _read_path(target: Object, path: String):
	var obj = target
	for seg in path.split("."):
		if obj == null:
			return null
		if obj is Dictionary:
			obj = obj.get(seg, null)
		elif obj is Object:
			if seg.ends_with("()") and obj.has_method(seg.trim_suffix("()")):
				obj = obj.call(seg.trim_suffix("()"))
			else:
				obj = obj.get(seg)
		else:
			return null
	return obj


func _set_path(target: Object, path: String, value) -> void:
	var segs := path.split(".")
	var obj = target
	for i in range(segs.size() - 1):
		obj = obj.get(segs[i])
		if obj == null:
			_errors.append("set_path broke at " + segs[i])
			return
	obj.set(segs[segs.size() - 1], value)


func _step_press(scope: Node, how) -> void:
	if not (how is Dictionary):
		return
	var want_text := str(how.get("text", ""))
	var meta_key := str(how.get("meta_key", ""))
	var meta_field := str(how.get("meta_field", ""))
	var equals := str(how.get("equals", ""))
	var search_root: Node = root if bool(how.get("anywhere", false)) else scope
	for b in _all_nodes(search_root):
		if not (b is BaseButton):
			continue
		if want_text != "" and ("text" in b) and str(b.text).strip_edges() == want_text:
			b.emit_signal("pressed")
			return
		if meta_key != "" and b.has_meta(meta_key):
			var m = b.get_meta(meta_key)
			if m is Dictionary and str(m.get(meta_field, "")) == equals:
				b.emit_signal("pressed")
				return
	_errors.append("press found no button: " + JSON.stringify(how))


func _scroll_to(how) -> void:
	if not (how is Dictionary):
		return
	var needle := str(how.get("text", ""))
	var rtl: RichTextLabel = null
	var sc: ScrollContainer = null
	if how.has("rtl"):
		rtl = _node.get_node_or_null(str(how["rtl"])) as RichTextLabel
	else:
		for n in _all_nodes(_node):
			if n is RichTextLabel and n.is_visible_in_tree() and n.get_parsed_text().contains(needle):
				rtl = n
				break
	if rtl == null:
		_errors.append("scroll_to: no RichTextLabel holds '%s'" % needle)
		return
	var p: Node = rtl.get_parent()
	while p != null and sc == null:
		if p is ScrollContainer:
			sc = p
		p = p.get_parent()
	if sc == null:
		_errors.append("scroll_to: no ScrollContainer above the label")
		return
	var parsed := rtl.get_parsed_text()
	var at := parsed.find(needle)
	if at < 0:
		_errors.append("scroll_to: text not rendered: " + needle)
		return
	var para := parsed.substr(0, at).count("\n")
	var y := rtl.get_paragraph_offset(clampi(para, 0, maxi(rtl.get_paragraph_count() - 1, 0)))
	sc.scroll_vertical = maxi(0, int(y) - int(how.get("margin", 24)))
