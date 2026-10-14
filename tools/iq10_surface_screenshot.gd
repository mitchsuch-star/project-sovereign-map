extends SceneTree
# IQ-10 "The Client Pass" — ONE generic offscreen capture harness
# (windowed, NOT --headless: `root.get_texture().get_image()` needs a real
# renderer; the window is parked where it cannot cover the desktop).
#
#   $env:IQ10_SPEC = "<absolute path to a spec JSON>"
#   <godot> --audio-driver Dummy --windowed --resolution 1600x900 \
#           --position 5200,20 --log-file <abs log> \
#           --path godot-client/project-sovereign \
#           --script ../../tools/iq10_surface_screenshot.gd
#
# Do not write specs by hand: `tools/iq10_run_captures.py` builds them from
# payloads that `tools/iq10_capture_payloads.py` captures off STAGED boards
# (in-process TestClient, mock parser). The runner is the two-command road:
#
#   .venv/Scripts/python.exe tools/iq10_capture_payloads.py
#   .venv/Scripts/python.exe tools/iq10_run_captures.py
#
# What this script does, per shot and per requested Interface Scale:
#   1. sizes the window and sets `root.content_scale_factor` (the ONE value
#      the pause slider and the terminal's Text Size buttons write), and
#      REOPENS the surface — a popup fits itself only when it is opened;
#   2. instantiates the REAL scene and calls its REAL entry method:
#        mode "call"      the method takes the payload (popups, dialogs, HUD)
#        mode "api_stub"  the five self-fetching screens: `open(api)` is handed
#                         a stub whose `get_*` answers AT ONCE with the captured
#                         endpoint response — the screen's own `_on_*_received`
#                         runs exactly as it does against the wire
#        mode "map_stub"  the region panel: a map-node stand-in that derives
#                         region_visibility / region_marshals / region_garrisons
#                         from `game_state.map_data` the way
#                         `map_renderer_base.update_all_regions` does
#        mode "main"      the real `main.tscn` — the war room itself (UXR-0,
#                         October 9, 2026). The scene's APIClient node is
#                         replaced BEFORE `_ready` by a stub that answers the
#                         connection test with the payload's `test` (a real
#                         GET /test) and the topology request with its
#                         `topology` (a real GET /map_topology), so the live
#                         boot path runs end to end — map, HUD, boot help —
#                         with no backend; the shot's steps then hand the
#                         payload's `new_game` to `_on_new_game_result`, which
#                         is exactly the menu's Begin. Still REFUSED while
#                         SOVEREIGN_PORT points at the player's 8005 (the
#                         runner points it at an unused port for the run).
#   3. adopts any `nation_display_overrides` the payload carries (the
#      `api_client._adopt_formation_overrides` chokepoint, mirrored);
#   4. runs the shot's `steps` (call / set / press / scroll_to / wait / shot);
#   5. saves the PNG to an ABSOLUTE path and records, per frame: every visible
#      text on screen (RichTextLabel parsed text, Label, Button + disabled +
#      tooltip) WITH ITS RENDERED SIZE IN PHYSICAL PIXELS — the em, the cap
#      height ("H") and the x-height ("x") of the font the node resolves,
#      times the node's canvas scale, times the window's content scale
#      factor (which `get_screen_transform()` does NOT carry — measured) —
#      and whether the node is Caption-class (`theme_type_variation`
#      Caption / CaptionRich / CaptionButton) or body-class; every probed
#      node's rect, every BaseButton that lies outside the logical viewport,
#      and every RichTextLabel whose content is taller than its box with no
#      ScrollContainer above it. The readability floor is NOT applied here —
#      `tools/uxr0_readability_report.py` reads these numbers and holds the
#      thresholds in one place.
#
#   Per shot the spec may carry `window` ([w, h] — the PHYSICAL frame; the
#   window is parked off the desktop and may exceed the screen, proven at
#   5120x1440 and 3840x2160) and `scales` (the content scale factors to shoot
#   it at). The in-memory UiSettings is seeded with the shot's scale before
#   the scene loads, so a scene that applies `UiSettings.get_ui_scale()` in
#   its own `_ready` (main.gd does) agrees with the window.
#
# The result JSON (spec.result) is written on EVERY exit path; the exit code
# is non-zero when any shot failed. GDScript runtime errors cannot be caught
# in-engine on 4.4 — the runner greps the --log-file for SCRIPT ERROR between
# the `[IQ10] BEGIN` / `[IQ10] END` markers this script prints.
#
# Safety rails (the brief's): UiSettings is shimmed onto an IN-MEMORY
# ConfigFile before any scene loads, so nothing reads the player's stored API
# key and no default-path read touches disk; no UiSettings SETTER is ever
# called from here (they `save()` to the real user://ui_settings.cfg); audio
# runs on the Dummy driver; no input event is synthesised — buttons are
# "pressed" by emitting their own signal.

const SETTLE_DEFAULT := 30
const RESIZE_WAIT := 6
const TEARDOWN_WAIT := 4
const HARD_FRAME_LIMIT := 60000

var _spec: Dictionary = {}
var _shots: Array = []
var _results: Array = []
var _shot_i := 0
var _scale_i := 0
var _phase := "boot"
var _wait := 0
var _frames := 0
var _node: Node = null
var _stubs: Array = []
var _steps: Array = []
var _step_i := 0
var _payload = null
var _current: Dictionary = {}
# Every keyboard-focus change of the shot, with the GDScript stack that made
# it (empty when the engine moved it): [frame, path, [caller, …]].
var _focus_log: Array = []
# UXR-X24 (Pre-Deploy S9b): OS input that reached the capture window during
# the shot. The window is real and takes the foreground when it opens, so a
# key the player pressed elsewhere (a Tab, a Shift+Tab) landed in the scene
# and moved the command line's focus. The harness never synthesises input,
# so the root ignores all of it (`gui_disable_input`) and counts what came.
var _stray_input := 0
var _backdrop: CanvasLayer = null
var _window_size := Vector2i(0, 0)
var _fatal := ""
# UXR-3 (Pre-Deploy S11): a shot's `settle_ms` holds the capture until that
# much REAL time has passed after its steps. Frames are not time off-screen,
# so a surface with a real-time entrance (the main menu's 1.1-s title and
# staggered buttons) was shot mid-fade by a frame-count settle alone.
var _settle_until := 0


# ── stubs ───────────────────────────────────────────────────────────────────

class ApiStub extends Node:
	# The five self-fetching screens call `api_client.get_<x>(callback)`.
	# Each answers IMMEDIATELY with the captured endpoint response.
	var responses: Dictionary = {}
	var calls: Array = []

	func _answer(method: String, cb: Callable) -> void:
		calls.append(method)
		var r = responses.get(method, null)
		if not (r is Dictionary):
			r = {"success": false, "message": "iq10 stub: no payload for " + method}
		# api_client._adopt_formation_overrides, mirrored: it runs BEFORE the
		# callback on the wire, so it runs before it here.
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
	# Click-only roads: recorded, never answered (display needs none).
	func send_command(_c, _cb = null): calls.append("send_command")
	func cancel_strategic_order(_m, _cb = null): calls.append("cancel_strategic_order")
	func dismiss_notification(_i, _cb = null): calls.append("dismiss_notification")
	func dismiss_all_notifications(_cb = null): calls.append("dismiss_all_notifications")


class MainStub extends Node:
	# The war room's APIClient stand-in (the ep_f1 harness's shape, widened to
	# every method the client calls). `responses` answers `test_connection`
	# and `get_map_topology` with REAL captured payloads so main.gd's own boot
	# path runs; every other road is recorded and answered as a refusal, so
	# nothing a click could reach ever leaves the process.
	var responses: Dictionary = {}
	var calls: Array = []

	func _answer(method: String, cb):
		calls.append(method)
		if cb is Callable:
			var r = responses.get(method, null)
			if not (r is Dictionary):
				r = {"success": false, "message": "iq10 main stub: no payload for " + method}
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
	# What `region_panel.gd` reads off the map node. Derived from
	# `game_state.map_data` exactly as `map_renderer_base.update_all_regions`
	# derives it (minus the province_shapes "wired" filter — every 1805
	# province the backend sends is wired).
	var region_full_data: Dictionary = {}
	var region_visibility: Dictionary = {}
	var region_marshals: Dictionary = {}
	var region_garrisons: Dictionary = {}
	var levy_status: Dictionary = {}
	var naval_overlay: Dictionary = {}
	# CRT-9 (CQ-21): the turn's action pools the administrative chips read.
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


# ── lifecycle ───────────────────────────────────────────────────────────────

func _init():
	# BEFORE any scene script can read a setting: an in-memory config. The
	# getters return published defaults; the player's file is never opened —
	# and never WRITTEN: `_persist = false` keeps a scene's own setter calls
	# (the menu's auto-derived scale, UXR-1) in memory.
	UiSettings._cfg = ConfigFile.new()
	# Set dynamically, through a Variant: the harness also shoots OLDER
	# checkouts (a pristine worktree for a BEFORE record) whose UiSettings
	# has no `_persist`, and a typed member assignment would not compile
	# against them (`Object.set` on a static the script lacks is a no-op).
	var settings_class: Variant = UiSettings
	settings_class.set("_persist", false)
	process_frame.connect(_tick)


func _tick():
	_frames += 1
	if _frames > HARD_FRAME_LIMIT:
		_fatal = "frame limit hit in phase %s (shot %d)" % [_phase, _shot_i]
		_finish()
		return
	if _wait > 0:
		_wait -= 1
		return
	match _phase:
		"boot":
			_boot()
		"prepare":
			_prepare()
		"instantiate":
			_instantiate()
		"enter":
			_enter()
		"steps":
			_run_steps()
		"capture":
			if Time.get_ticks_msec() < _settle_until:
				return
			_capture("")
			_phase = "teardown"
		"teardown":
			_teardown()
		"done":
			_finish()


func _boot():
	var spec_path := OS.get_environment("IQ10_SPEC")
	if spec_path == "":
		_fatal = "IQ10_SPEC is not set"
		_finish()
		return
	var parsed = _read_json(spec_path)
	if not (parsed is Dictionary):
		_fatal = "spec did not parse: " + spec_path
		_finish()
		return
	_spec = parsed
	_shots = _spec.get("shots", [])
	if not (_shots is Array) or _shots.is_empty():
		_fatal = "spec carries no shots"
		_finish()
		return
	root.mode = Window.MODE_WINDOWED
	root.gui_disable_input = true
	if not root.window_input.is_connected(_on_stray_input):
		root.window_input.connect(_on_stray_input)
	var pos = _spec.get("window_position", [5200, 20])
	root.position = Vector2i(int(pos[0]), int(pos[1]))
	# A flat backdrop under every layer: an isolated popup over the engine's
	# default grey reads as a rendering fault in a still.
	_backdrop = CanvasLayer.new()
	_backdrop.layer = -100
	_backdrop.name = "IQ10Backdrop"
	var rect := ColorRect.new()
	var bc = _spec.get("backdrop", [0.07, 0.09, 0.13])
	rect.color = Color(float(bc[0]), float(bc[1]), float(bc[2]), 1.0)
	rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_backdrop.add_child(rect)
	root.add_child(_backdrop)
	_phase = "prepare"
	_wait = 2


func _shot() -> Dictionary:
	return _shots[_shot_i]


func _scales() -> Array:
	var s = _shot().get("scales", _spec.get("scales", [1.0]))
	return s if (s is Array and not s.is_empty()) else [1.0]


func _scale() -> float:
	return float(_scales()[_scale_i])


func _scale_key() -> String:
	return "%.1f" % _scale()


func _prepare():
	var shot := _shot()
	var key := _scale_key()
	_current = {
		"id": str(shot.get("id", "shot_%d" % _shot_i)),
		"scale": _scale(),
		"ok": false,
		"errors": [],
		"frames": [],
	}
	print("[IQ10] BEGIN %s@%s" % [_current["id"], key])
	var sizes = shot.get("window_by_scale", _spec.get("window_by_scale", {}))
	var want = sizes.get(key, shot.get("window", _spec.get("window", [1600, 900])))
	var size := Vector2i(int(want[0]), int(want[1]))
	if size != _window_size:
		root.size = size
		_window_size = size
		_wait = RESIZE_WAIT
	root.content_scale_factor = _scale()
	# The in-memory settings agree with the window: a scene that applies the
	# stored scale in its own `_ready` (main.gd) would otherwise reset the
	# factor to the published default and shoot the wrong frame. In memory
	# only — the harness never saves (see the UiSettings._persist rail).
	UiSettings._cfg.set_value("display", "ui_scale", _scale())
	# UXR-D1 (Pre-Deploy S9b): the Text size the frame is shot at (the spec's
	# or the shot's `text_size`, 1.0 when neither says) — seeded in memory and
	# applied to the project theme before the scene loads. An older checkout
	# (a BEFORE worktree) has no Text size: the harness then shoots its 1.0.
	var text_size := float(shot.get("text_size", _spec.get("text_size", 1.0)))
	UiSettings._cfg.set_value("display", "text_size", text_size)
	var settings_script: Script = UiSettings
	if settings_script.get_script_constant_map().has("MAX_TEXT_SIZE"):
		var utils_class: Variant = Utils
		utils_class.call("apply_text_size")
	_current["window"] = [size.x, size.y]
	_current["content_scale_factor"] = _scale()
	_current["text_size"] = text_size
	# UXR-D2: High contrast (off when unsaid) — seeded and applied like the
	# game does (main / main_menu re-tone each node as it enters the tree;
	# a scene shot alone has neither, so the harness hooks the same chokepoint).
	var high_contrast := bool(shot.get("high_contrast", _spec.get("high_contrast", false)))
	UiSettings._cfg.set_value("display", "high_contrast", high_contrast)
	_current["high_contrast"] = high_contrast
	if settings_script.get_script_constant_map().has("HIGH_CONTRAST_FLOOR_HEX"):
		var utils_hc: Variant = Utils
		utils_hc.call("apply_contrast")
		if high_contrast and not node_added.is_connected(_on_node_added_contrast):
			node_added.connect(_on_node_added_contrast)
		elif not high_contrast and node_added.is_connected(_on_node_added_contrast):
			node_added.disconnect(_on_node_added_contrast)
	# UXR-D3: the HUD width the frame is shot at ("full" when unsaid).
	var hud_width := str(shot.get("hud_width", _spec.get("hud_width", "full")))
	UiSettings._cfg.set_value("display", "hud_width", hud_width)
	_current["hud_width"] = hud_width
	_phase = "instantiate"
	_wait += 2


func _instantiate():
	var shot := _shot()
	var mode := str(shot.get("mode", "call"))
	var scene_path := str(shot.get("scene", ""))
	if mode == "main" or scene_path.ends_with("/main.tscn"):
		# Golden rule 7 + the brief: the player's live 8005 is never touched.
		if Utils.backend_url().ends_with(":8005"):
			_abort_shot("main.tscn refused: SOVEREIGN_PORT still points at the player's 8005")
			return
	var packed = load(scene_path)
	if not (packed is PackedScene):
		_abort_shot("scene did not load: " + scene_path)
		return
	_payload = null
	if shot.has("payload"):
		_payload = _read_json(str(shot["payload"]))
		if _payload == null:
			_abort_shot("payload did not parse: " + str(shot["payload"]))
			return
	_adopt_overrides(_payload)
	if shot.get("formation_overrides") is Dictionary:
		var fo: Dictionary = shot["formation_overrides"]
		Utils.set_formation_overrides(fo.get("names", {}), fo.get("flags", {}))
	_focus_log = []
	_stray_input = 0
	if not root.gui_focus_changed.is_connected(_on_focus_changed):
		root.gui_focus_changed.connect(_on_focus_changed)
	_node = packed.instantiate()
	root.add_child(_node)
	if mode == "main":
		# The war room: main.gd CREATES its APIClient inside `_ready` (which
		# ran during add_child above) and fetches 0.5 s later, so the swap
		# goes AFTER the add (the ep_f1 idiom): the real client is freed
		# before its first request, and the stub answers the boot's two
		# requests with the payload's real captures; every other road is
		# recorded.
		var stub := MainStub.new()
		stub.name = "APIClientStub"
		if _payload is Dictionary:
			if _payload.get("test") is Dictionary:
				stub.responses["test_connection"] = _payload["test"]
			if _payload.get("topology") is Dictionary:
				stub.responses["get_map_topology"] = _payload["topology"]
		var real = _node.get("api_client") if ("api_client" in _node) else null
		if real is Node:
			_node.remove_child(real)
			real.queue_free()
		_node.add_child(stub)
		if "api_client" in _node:
			_node.set("api_client", stub)
		_stubs.append(stub)
	var place = shot.get("place", null)
	if place is Dictionary and _node is Control:
		# A bare Control scene (the notification rail) has no rect of its own.
		var c: Control = _node
		c.set_anchors_preset(Control.PRESET_TOP_WIDE)
		var p = place.get("position", [0, 0])
		c.position = Vector2(float(p[0]), float(p[1]))
		c.size = Vector2(root.get_visible_rect().size.x, float(place.get("height", 60)))
	_phase = "enter"
	_wait = 2


func _enter():
	var shot := _shot()
	var mode := str(shot.get("mode", "call"))
	var method := str(shot.get("method", ""))
	var api: ApiStub = null
	var map: MapStub = null
	if mode == "api_stub":
		api = ApiStub.new()
		api.name = "IQ10ApiStub"
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
		map.name = "IQ10MapStub"
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
			_abort_shot("entry method missing: %s.%s" % [str(shot.get("scene", "")), method])
			return
		_node.callv(method, args)
	_steps = shot.get("steps", [])
	if not (_steps is Array):
		_steps = []
	_step_i = 0
	_phase = "steps"
	_wait = 1


func _run_steps():
	if _step_i >= _steps.size():
		_phase = "capture"
		_wait = int(_shot().get("settle", _spec.get("settle", SETTLE_DEFAULT)))
		_settle_until = Time.get_ticks_msec() + int(_shot().get("settle_ms", 0))
		return
	var step = _steps[_step_i]
	if not (step is Dictionary):
		_step_i += 1
		return
	if step.has("wait_for"):
		# Poll a property on the scene until it reads true (frames are NOT
		# time: parked off-screen with no vsync the engine runs unthrottled,
		# so main.gd's 0.5 s boot timer outlives any frame count — the war
		# room shot its map black until this waited on the boot flag).
		var target_node: Node = _node
		if step.has("node"):
			var held = _node.get(str(step["node"]).trim_prefix("@"))
			target_node = held if held is Node else _node
		var value = _read_path(target_node, str(step["wait_for"]))
		var spent := int(step.get("_spent", 0))
		if value:
			_step_i += 1
			if step.has("then_wait"):
				_wait = int(step["then_wait"])
			return
		if spent >= int(step.get("timeout", 1800)):
			_note_error("wait_for timed out: " + str(step["wait_for"]))
			_step_i += 1
			return
		step["_spent"] = spent + 1
		return
	_step_i += 1
	if step.has("wait"):
		_wait = int(step["wait"])
		return
	var target: Node = _node
	if step.has("node"):
		var want := str(step["node"])
		if want.begins_with("@"):
			# A node the scene holds in a PROPERTY rather than under a path —
			# main.gd's dialogs are registered at runtime (`pause_menu`,
			# `strategic_ledger`, …), so "@pause_menu" reads `_node.pause_menu`.
			var held = _node.get(want.substr(1))
			target = held if held is Node else null
		else:
			target = _node.get_node_or_null(want)
		if target == null:
			_note_error("step node missing: " + want)
			return
	if step.has("call"):
		var m := str(step["call"])
		if not target.has_method(m):
			_note_error("step method missing: " + m)
			return
		target.callv(m, _resolve_args(step.get("args", []), null, null))
	elif step.has("set_path"):
		_set_path(target, str(step["set_path"]), _resolve_value(step.get("value"), null, null))
	elif step.has("press"):
		_press(target, step["press"])
	elif step.has("read"):
		# Record properties off the target (dotted paths walk nested objects)
		# into the shot's `reads` — the diagnostic a frame cannot show (the
		# map camera's zoom, a derived scale, a card's rect). One entry per
		# read step, in order, so a value read twice keeps both readings.
		var values := {}
		for p in step["read"]:
			values[str(p)] = _read_path(target, str(p))
		var reads: Array = _current.get("reads", [])
		reads.append({"step": _step_i - 1, "node": str(step.get("node", "")), "values": values})
		_current["reads"] = reads
	elif step.has("scroll_to"):
		_scroll_to(step["scroll_to"])
	elif step.has("shot"):
		# An intermediate frame (a flow's before/after): its own PNG suffix.
		_capture(str(step["shot"]))
	if step.has("then_wait"):
		_wait = int(step["then_wait"])


# ── steps ───────────────────────────────────────────────────────────────────

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
	# JSON has no ints. A TOP-LEVEL argument is a typed parameter (`turn: int`),
	# so an integral float goes in as an int; payload dictionaries are left as
	# the wire leaves them (the real client parses the same floats).
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
	if obj is Vector2 or obj is Vector2i:
		return [obj.x, obj.y]
	if obj is Rect2:
		return [obj.position.x, obj.position.y, obj.size.x, obj.size.y]
	if obj is Object and not (obj is Node):
		return str(obj)
	if obj is Node:
		return str((obj as Node).name)
	return obj


func _set_path(target: Object, path: String, value) -> void:
	var segs := path.split(".")
	var obj = target
	for i in range(segs.size() - 1):
		obj = obj.get(segs[i])
		if obj == null:
			_note_error("set_path broke at " + segs[i])
			return
	obj.set(segs[segs.size() - 1], value)


func _press(scope: Node, how) -> void:
	# "Pressing" = emitting the button's own signal. No input event exists,
	# so nothing can reach another window.
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
	_note_error("press found no button: " + JSON.stringify(how))


func _scroll_to(how) -> void:
	# Bring the paragraph holding `text` to the top of its ScrollContainer.
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
		_note_error("scroll_to: no RichTextLabel holds '%s'" % needle)
		return
	var p: Node = rtl.get_parent()
	while p != null and sc == null:
		if p is ScrollContainer:
			sc = p
		p = p.get_parent()
	if sc == null:
		_note_error("scroll_to: no ScrollContainer above the label")
		return
	var parsed := rtl.get_parsed_text()
	var at := parsed.find(needle)
	if at < 0:
		_note_error("scroll_to: text not rendered: " + needle)
		return
	var para := parsed.substr(0, at).count("\n")
	var y := rtl.get_paragraph_offset(clampi(para, 0, maxi(rtl.get_paragraph_count() - 1, 0)))
	sc.scroll_vertical = maxi(0, int(y) - int(how.get("margin", 24)))


# ── capture ─────────────────────────────────────────────────────────────────

func _out_path(suffix: String) -> String:
	var out = _shot().get("out", {})
	var base := str(out.get(_scale_key(), "")) if out is Dictionary else ""
	if base == "" or suffix == "":
		return base
	return base.get_basename() + "_" + suffix + ".png"


func _capture(suffix: String) -> void:
	var path := _out_path(suffix)
	var frame := {"suffix": suffix, "png": path}
	if path == "":
		_note_error("no output path for scale " + _scale_key())
		return
	DirAccess.make_dir_recursive_absolute(path.get_base_dir())
	var img: Image = root.get_texture().get_image()
	if img == null or img.is_empty():
		_note_error("viewport returned no image (is the run --headless?)")
		return
	var down := float(_shot().get("downscale", _spec.get("downscale", 1.0)))
	if down > 0.0 and down < 1.0:
		img.resize(maxi(1, int(img.get_width() * down)), maxi(1, int(img.get_height() * down)),
				Image.INTERPOLATE_LANCZOS)
	var err := img.save_png(path)
	if err != OK:
		_note_error("save_png failed (%d): %s" % [err, path])
		return
	frame["image_size"] = [img.get_width(), img.get_height()]
	frame["bytes"] = FileAccess.get_file_as_bytes(path).size()
	frame["blank"] = _is_blank(img)
	var view: Vector2 = root.get_visible_rect().size
	frame["logical_viewport"] = [view.x, view.y]
	frame["texts"] = _collect_texts()
	frame["buttons_offscreen"] = _buttons_offscreen(view)
	frame["clipped_text"] = _clipped_text()
	# UXR-3 (Pre-Deploy S11): R7's cut text, every button, what lies under a
	# modal, and the files that drew the frame (R4's census reads them).
	frame["truncated_text"] = _truncated_text()
	frame["buttons"] = _visible_buttons()
	# S12 part 2 (UXR3-F4): every visible resize grip and corner ornament,
	# so the census can hold them off the text rows and the buttons.
	frame["grips"] = _grips_and_ornaments()
	# S12 part 2 (UXR3-F3): a line cut at a scroll's edge.
	frame["cut_lines"] = _cut_lines()
	var fit := _under_modal(view)
	for key in fit:
		frame[key] = fit[key]
	frame["files"] = _visible_files()
	frame["probe"] = _probe(_shot().get("probe", []))
	frame["surfaces"] = _surface_rects()
	# The control holding keyboard focus (the war room's command line should).
	var focus_owner: Control = root.gui_get_focus_owner()
	frame["focus"] = str(root.get_path_to(focus_owner)) if focus_owner != null else ""
	frame["focus_log"] = _focus_log.duplicate()
	frame["stray_input"] = _stray_input
	var stub_calls := []
	for s in _stubs:
		if s is ApiStub:
			stub_calls.append_array(s.calls)
	frame["api_calls"] = stub_calls
	if frame["blank"]:
		_note_error("frame is a single flat colour — nothing rendered")
	_current["frames"].append(frame)


func _is_blank(img: Image) -> bool:
	var w := img.get_width()
	var h := img.get_height()
	var first := img.get_pixel(0, 0)
	var step := maxi(1, mini(w, h) / 40)
	for y in range(0, h, step):
		for x in range(0, w, step):
			if not img.get_pixel(x, y).is_equal_approx(first):
				return false
	return true


func _all_nodes(from: Node) -> Array:
	var out: Array = []
	var stack: Array = [from]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		out.append(n)
		for c in n.get_children():
			stack.append(c)
	return out


func _shown(n: Node) -> bool:
	# Visible on SCREEN: `is_visible_in_tree` stops at a SubViewport (a
	# Viewport is not a CanvasItem), so a node drawn into the map's viewport
	# read as shown while the Control displaying that viewport was hidden
	# (the war room before its map bootstrapped). Climb through every
	# SubViewport to the Control that shows it.
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


func _collect_texts() -> Array:
	var out: Array = []
	for n in _all_nodes(root):
		if n == _backdrop or not _shown(n):
			continue
		var entry := {}
		var font: Font = null
		var font_size := 0
		if n is RichTextLabel:
			entry = {"class": "RichTextLabel", "text": n.get_parsed_text()}
			font = n.get_theme_font("normal_font")
			font_size = n.get_theme_font_size("normal_font_size")
		elif n is Label:
			entry = {"class": "Label", "text": n.text}
			font = n.get_theme_font("font")
			font_size = n.get_theme_font_size("font_size")
		elif n is BaseButton and ("text" in n):
			entry = {"class": n.get_class(), "text": str(n.text), "disabled": n.disabled}
			font = n.get_theme_font("font")
			font_size = n.get_theme_font_size("font_size")
		elif n is LineEdit:
			entry = {"class": "LineEdit", "text": n.text}
			font = n.get_theme_font("font")
			font_size = n.get_theme_font_size("font_size")
		else:
			continue
		if n is Control and str((n as Control).tooltip_text) != "":
			entry["tooltip"] = (n as Control).tooltip_text
		if str(entry.get("text", "")) == "" and not entry.has("tooltip"):
			continue
		entry["path"] = str(root.get_path_to(n))
		_add_text_metrics(entry, n, font, font_size)
		_add_text_colors(entry, n)
		_add_fit_fields(entry, n)
		out.append(entry)
	return out


# ── the readability census (UXR-0) ──────────────────────────────────────────

const _CAPTION_VARIATIONS := ["Caption", "CaptionRich", "CaptionButton"]
var _glyph_cache: Dictionary = {}


func _add_text_metrics(entry: Dictionary, n: Control, font: Font, font_size: int) -> void:
	# The node's resolved font and size (override → type variation → theme
	# type → default), its canvas scale, and the window's content scale
	# factor — which the screen transform does not carry — give the glyphs'
	# PHYSICAL size: the em, and the cap/x heights read off the font's own
	# "H" and "x" glyph bitmaps through the TextServer.
	var canvas_scale: float = n.get_global_transform_with_canvas().get_scale().y
	var view_mult := maxf(root.content_scale_factor, 0.01)
	var sv := _subviewport_of(n)
	if sv != null:
		# UXR-X26 (Pre-Deploy S9b): a SubViewport node's canvas transform is in
		# the SubViewport's OWN pixels; what reaches the screen is that times
		# the physical px its display gives each SubViewport px. The map renders
		# its SubViewport at physical resolution (1.0), so multiplying by the
		# window's content scale counted the scale twice and over-read every
		# map row by it (1.4x on the user's panel).
		view_mult = _subviewport_display_scale(sv)
	var mult: float = canvas_scale * view_mult
	entry["font_size"] = font_size
	entry["canvas_scale"] = canvas_scale
	entry["em_px"] = float(font_size) * mult
	var variation := str(n.theme_type_variation)
	if _inside_subviewport(n):
		# The map's world-space furniture (name stacks, garrison chips, sail
		# counts) is sized by the camera, not the interface: its own tier,
		# reported beside the floor, never under it (UXR-X4 owns it).
		entry["tier"] = "map"
	elif variation in _CAPTION_VARIATIONS:
		entry["tier"] = "caption"
	else:
		entry["tier"] = "body"
	entry["variation"] = variation
	if font == null or font_size <= 0:
		return
	entry["font"] = font.get_font_name()
	var ratios := _glyph_ratios(font, font_size)
	entry["cap_px"] = float(ratios.get("cap", 0.0)) * mult
	entry["x_px"] = float(ratios.get("x", 0.0)) * mult


# ── the contrast census (UXR-D2, Pre-Deploy S9b — UXR-3's R3 instrument) ────
# Per text row: its logical rect (clipped to the scroll that shows it) and the
# colours it DECLARES — a Label / Button / LineEdit's resolved font colour, a
# RichTextLabel's default colour and every BBCode [color] span, each times the
# node's modulate chain, and a chip's [bgcolor][color] pair apart.
# `tools/uxr2b_contrast_report.py` reads the background off the frame.
var _chip_re := RegEx.create_from_string("(?s)\\[bgcolor=([^\\]]+)\\](.*?)\\[/bgcolor\\]")
var _span_re := RegEx.create_from_string("\\[color=([^\\]]+)\\]")


func _modulate_chain(n: CanvasItem) -> Color:
	var m := n.self_modulate
	var p: Node = n
	while p != null and p is CanvasItem:
		m *= (p as CanvasItem).modulate
		p = p.get_parent()
	return m


func _add_text_colors(entry: Dictionary, n: Control) -> void:
	if _inside_subviewport(n):
		return
	var r := n.get_global_rect()
	var scroll := _scroll_ancestor(n)
	if scroll != null:
		r = r.intersection(scroll.get_global_rect())
	r = r.intersection(root.get_visible_rect())
	entry["rect"] = [r.position.x, r.position.y, r.size.x, r.size.y]
	var mod := _modulate_chain(n)
	var colors: Array = []
	var chips: Array = []
	if n is RichTextLabel:
		var rtl := n as RichTextLabel
		colors.append((rtl.get_theme_color("default_color") * mod).to_html(true))
		var src := rtl.text
		for m in _chip_re.search_all(src):
			var bg := Color.from_string(m.get_string(1), Color(0, 0, 0, 0))
			for span in _span_re.search_all(m.get_string(2)):
				chips.append([bg.to_html(true), (Color.from_string(span.get_string(1), Color.WHITE) * mod).to_html(true)])
		var rest := _chip_re.sub(src, "", true)
		for span in _span_re.search_all(rest):
			colors.append((Color.from_string(span.get_string(1), Color.WHITE) * mod).to_html(true))
	elif n is BaseButton:
		var key := "font_disabled_color" if (n as BaseButton).disabled else "font_color"
		colors.append((n.get_theme_color(key) * mod).to_html(true))
	else:
		colors.append((n.get_theme_color("font_color") * mod).to_html(true))
	var unique: Array = []
	for c in colors:
		if not unique.has(c):
			unique.append(c)
	entry["colors"] = unique
	if not chips.is_empty():
		entry["chips"] = chips


func _subviewport_of(n: Node) -> SubViewport:
	var p: Node = n.get_parent()
	while p != null:
		if p is SubViewport:
			return p
		p = p.get_parent()
	return null


var _sv_display_cache: Dictionary = {}


func _subviewport_display_scale(sv: SubViewport) -> float:
	"""Physical screen px per SubViewport px: the displaying control's
	logical width x the window's content scale / the SubViewport's width."""
	var csf := maxf(root.content_scale_factor, 0.01)
	var shown: Control = null
	if sv.get_parent() is SubViewportContainer:
		shown = sv.get_parent()
	else:
		shown = _sv_display_cache.get(sv.get_instance_id(), null)
		if shown == null or not is_instance_valid(shown):
			var tex := sv.get_texture()
			for c in _all_nodes(root):
				if c is TextureRect and (c as TextureRect).texture == tex:
					shown = c
					break
			_sv_display_cache[sv.get_instance_id()] = shown
	if shown == null or sv.size.x <= 0:
		return csf
	return shown.get_global_rect().size.x * csf / float(sv.size.x)


func _inside_subviewport(n: Node) -> bool:
	var p: Node = n.get_parent()
	while p != null:
		if p is SubViewport:
			return true
		p = p.get_parent()
	return false


func _glyph_ratios(font: Font, font_size: int) -> Dictionary:
	# Glyph bitmap heights in LOGICAL px at this size, cached per face+size.
	var rids := font.get_rids()
	if rids.is_empty():
		return {}
	var rid: RID = rids[0]
	var key := "%d:%d" % [rid.get_id(), font_size]
	if _glyph_cache.has(key):
		return _glyph_cache[key]
	var ts := TextServerManager.get_primary_interface()
	var sz := Vector2i(font_size, 0)
	var gi_h := ts.font_get_glyph_index(rid, font_size, "H".unicode_at(0), 0)
	var gi_x := ts.font_get_glyph_index(rid, font_size, "x".unicode_at(0), 0)
	var out := {
		"cap": ts.font_get_glyph_size(rid, sz, gi_h).y,
		"x": ts.font_get_glyph_size(rid, sz, gi_x).y,
	}
	_glyph_cache[key] = out
	return out


func _buttons_offscreen(view: Vector2) -> Array:
	# A button scrolled out of its ScrollContainer's view is REACHABLE (the
	# player scrolls to it), exactly as `_clipped_text` treats a tall label
	# inside one. Score Finish Step 7 frames (Oct 4, 2026): the first full
	# reading flagged 159 buttons, every one a row of a scrolled list — the
	# wizard's nation list and the campaign log's turn list — and none a
	# button the player could not reach. Only the scroll container's own
	# rect must lie on the screen.
	var out: Array = []
	var screen := Rect2(Vector2.ZERO, view)
	for n in _all_nodes(root):
		if not (n is BaseButton) or not _shown(n):
			continue
		var r: Rect2 = (n as Control).get_global_rect()
		if r.size.x <= 0.0 or r.size.y <= 0.0:
			continue
		var scroller := _scroll_ancestor(n)
		if scroller != null:
			r = scroller.get_global_rect()
		if not screen.encloses(r):
			out.append({"path": str(root.get_path_to(n)),
					"text": (str(n.text) if ("text" in n) else ""),
					"rect": [r.position.x, r.position.y, r.size.x, r.size.y]})
	return out


func _scroll_ancestor(n: Node) -> Control:
	var p: Node = n.get_parent()
	while p != null:
		if p is ScrollContainer:
			return p as Control
		p = p.get_parent()
	return null


func _clipped_text() -> Array:
	# A RichTextLabel taller than its box is fine INSIDE a ScrollContainer or
	# with its own scrollbar; anywhere else the overflow is simply not drawn.
	var out: Array = []
	for n in _all_nodes(root):
		if not (n is RichTextLabel) or not _shown(n):
			continue
		var rtl: RichTextLabel = n
		if rtl.scroll_active or rtl.fit_content:
			continue
		var inside_scroll := false
		var p: Node = rtl.get_parent()
		while p != null:
			if p is ScrollContainer:
				inside_scroll = true
				break
			p = p.get_parent()
		if inside_scroll:
			continue
		if rtl.get_content_height() > int(rtl.size.y) + 1:
			out.append({"path": str(root.get_path_to(rtl)),
					"content_height": rtl.get_content_height(), "box_height": rtl.size.y})
	return out


# ── the Fit and Consistency records (UXR-3, Pre-Deploy S11 — R7 and R4 of ──
# docs/UX_CHECKLIST_V1.json). Read by tools/uxr3_fit_report.py and
# tools/uxr3_consistency_census.py; the rules live in the checklist, these
# functions only record.

func _layer_of(n: Node) -> int:
	var p: Node = n
	while p != null:
		if p is CanvasLayer:
			return (p as CanvasLayer).layer
		p = p.get_parent()
	return 0


func _add_fit_fields(entry: Dictionary, n: Control) -> void:
	# The row's CanvasLayer, its UNCLIPPED rect (the `rect` above is clipped to
	# its scroll and the viewport, so a row past the edge reads as empty), and
	# the rect of the ScrollContainer that shows it — a scrolled list is judged
	# by its scroll, as `_buttons_offscreen` judges a button.
	if _inside_subviewport(n):
		return
	entry["layer"] = _layer_of(n)
	var r := n.get_global_rect()
	entry["rect_raw"] = [r.position.x, r.position.y, r.size.x, r.size.y]
	var scroll := _scroll_ancestor(n)
	if scroll != null:
		var s := scroll.get_global_rect()
		entry["scroll_rect"] = [s.position.x, s.position.y, s.size.x, s.size.y]


func _single_line_width(font: Font, text: String, size: int) -> float:
	var w := 0.0
	for line in text.split("\n"):
		w = maxf(w, font.get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x)
	return w


func _stylebox_h_margins(c: Control, sb_name: String) -> float:
	var sb := c.get_theme_stylebox(sb_name)
	if sb == null:
		return 0.0
	return sb.get_margin(SIDE_LEFT) + sb.get_margin(SIDE_RIGHT)


func _truncated_text() -> Array:
	# R7 (1)'s second half: a Label or Button whose words are CUT. A one-line
	# label or button with clip_text on, or a text_overrun_behavior other than
	# no-trimming, whose text is wider than its content box; an autowrapped
	# Label showing fewer lines than it holds; a non-wrapping RichTextLabel
	# wider than its box; a visible text node drawn in a zero-width box.
	var out: Array = []
	for n in _all_nodes(root):
		if n == _backdrop or not _shown(n) or _inside_subviewport(n):
			continue
		if n is Label:
			var l := n as Label
			if l.text.strip_edges() == "":
				continue
			var row := {"path": str(root.get_path_to(l)), "class": "Label", "text": l.text.left(60)}
			if l.size.x < 1.0:
				row["reason"] = "zero_box"
				out.append(row)
			elif l.autowrap_mode != TextServer.AUTOWRAP_OFF:
				var lines := l.get_line_count()
				var vis := l.get_visible_line_count()
				if vis < lines:
					row["reason"] = "lines"
					row["lines"] = lines
					row["visible_lines"] = vis
					out.append(row)
			elif l.clip_text or l.text_overrun_behavior != TextServer.OVERRUN_NO_TRIMMING:
				var font := l.get_theme_font("font")
				if font == null:
					continue
				var tw := _single_line_width(font, l.text, l.get_theme_font_size("font_size"))
				var box := l.size.x - _stylebox_h_margins(l, "normal")
				if tw > box + 1.0:
					row["reason"] = "width"
					row["text_w"] = tw
					row["box_w"] = box
					out.append(row)
		elif n is Button:
			var b := n as Button
			if b.text.strip_edges() == "":
				continue
			if not (b.clip_text or b.text_overrun_behavior != TextServer.OVERRUN_NO_TRIMMING):
				continue
			var font := b.get_theme_font("font")
			if font == null:
				continue
			var tw := _single_line_width(font, b.text, b.get_theme_font_size("font_size"))
			var box := b.size.x - _stylebox_h_margins(b, "normal")
			if b.icon != null and not b.expand_icon:
				box -= b.icon.get_width() + b.get_theme_constant("h_separation")
			if tw > box + 1.0:
				out.append({"path": str(root.get_path_to(b)), "class": b.get_class(),
						"text": b.text.left(60), "reason": "width", "text_w": tw, "box_w": box})
		elif n is RichTextLabel:
			var rtl := n as RichTextLabel
			if rtl.autowrap_mode != TextServer.AUTOWRAP_OFF or rtl.get_parsed_text().strip_edges() == "":
				continue
			if rtl.get_content_width() > int(rtl.size.x) + 1:
				out.append({"path": str(root.get_path_to(rtl)), "class": "RichTextLabel",
						"text": rtl.get_parsed_text().left(60), "reason": "rtl_width",
						"text_w": rtl.get_content_width(), "box_w": rtl.size.x})
	return out


func _cut_lines() -> Array:
	# Per visible RichTextLabel inside a ScrollContainer: the first and the
	# last line its scroll shows, and whether either straddles the scroll's
	# edge by more than 2 logical px (a line cut in half at the edge).
	var out: Array = []
	for n in _all_nodes(root):
		if not (n is RichTextLabel) or not _shown(n) or _inside_subviewport(n):
			continue
		var rtl := n as RichTextLabel
		var sc := _scroll_ancestor(rtl)
		if sc == null or rtl.get_parsed_text().strip_edges() == "":
			continue
		var s_rect := sc.get_global_rect()
		var r_top := rtl.get_global_rect().position.y
		var count := rtl.get_line_count()
		var cut_top := 0.0
		var cut_bottom := 0.0
		for i in range(count):
			var y0 := r_top + float(rtl.get_line_offset(i))
			var y1 := r_top + (float(rtl.get_line_offset(i + 1)) if i + 1 < count else float(rtl.get_content_height()))
			if y0 < s_rect.position.y - 2.0 and y1 > s_rect.position.y + 2.0:
				cut_top = minf(y1 - s_rect.position.y, s_rect.position.y - y0)
			if y0 < s_rect.end.y - 2.0 and y1 > s_rect.end.y + 2.0:
				cut_bottom = minf(s_rect.end.y - y0, y1 - s_rect.end.y)
		if cut_top > 0.0 or cut_bottom > 0.0:
			out.append({"path": str(root.get_path_to(rtl)), "layer": _layer_of(rtl),
					"scroll_rect": [s_rect.position.x, s_rect.position.y, s_rect.size.x, s_rect.size.y],
					"cut_top_px": cut_top, "cut_bottom_px": cut_bottom})
	return out


func _grips_and_ornaments() -> Array:
	# A ResizeGrip (its hit square, centred on its panel's corner), a node in
	# the `corner_ornaments` group and a bar's centre tick (`bar_ticks`), each
	# with its layer and rect.
	var out: Array = []
	for n in _all_nodes(root):
		if not (n is Control) or n == _backdrop or not _shown(n) or _inside_subviewport(n):
			continue
		var kind := ""
		if n is ResizeGrip:
			kind = "grip"
		elif n.is_in_group("corner_ornaments"):
			kind = "ornament"
		elif n.is_in_group("bar_ticks"):
			# UXR3-F1: a bar's centre tick, which the score label must clear.
			kind = "tick"
		else:
			continue
		var r := (n as Control).get_global_rect()
		out.append({"path": str(root.get_path_to(n)), "kind": kind, "layer": _layer_of(n),
				"tooltip": str((n as Control).tooltip_text).left(120),
				"rect": [r.position.x, r.position.y, r.size.x, r.size.y]})
	return out


func _visible_buttons() -> Array:
	# Every visible BaseButton outside the map's SubViewport — icon-only ones
	# too, which the text census cannot see — with its layer and rects.
	var out: Array = []
	for n in _all_nodes(root):
		if not (n is BaseButton) or n == _backdrop or not _shown(n) or _inside_subviewport(n):
			continue
		var b := n as BaseButton
		var r := b.get_global_rect()
		var row := {"path": str(root.get_path_to(b)), "class": b.get_class(),
				"text": (str(n.text) if ("text" in n) else "").left(60), "disabled": b.disabled,
				"tooltip": str(b.tooltip_text).left(120), "layer": _layer_of(b),
				"rect_raw": [r.position.x, r.position.y, r.size.x, r.size.y]}
		var scroll := _scroll_ancestor(b)
		if scroll != null:
			var s := scroll.get_global_rect()
			row["scroll_rect"] = [s.position.x, s.position.y, s.size.x, s.size.y]
		out.append(row)
	return out


func _draws(c: Control) -> bool:
	# A Control that paints over its rect: a panel, a coloured or textured rect
	# — not a bare container, and not a fully transparent one.
	if _modulate_chain(c).a <= 0.02:
		return false
	if c is ColorRect:
		return (c as ColorRect).color.a > 0.02
	if c is TextureRect:
		return (c as TextureRect).texture != null
	if c is NinePatchRect:
		return (c as NinePatchRect).texture != null
	if c is Panel or c is PanelContainer:
		var sb := c.get_theme_stylebox("panel")
		if sb == null or sb is StyleBoxEmpty:
			return false
		if sb is StyleBoxFlat:
			var f := sb as StyleBoxFlat
			var border := f.border_width_left + f.border_width_right + f.border_width_top + f.border_width_bottom
			return f.bg_color.a > 0.02 or (border > 0 and f.border_color.a > 0.02)
		return true
	return false


func _under_modal(view: Vector2) -> Dictionary:
	# R7 (3): a visible text row or button of the LIVE frame whose centre lies
	# inside a drawing Control on a strictly higher CanvasLayer. The live frame
	# is the layers at and above the topmost modal layer — one holding a
	# visible Control whose mouse filter is not IGNORE and which covers >= 95 %
	# of the logical viewport; what lies under a modal is suspended by it.
	var vrect := Rect2(Vector2.ZERO, view)
	var area := view.x * view.y
	var modal: Array = []
	var drawers: Array = []
	var rows: Array = []
	for n in _all_nodes(root):
		if not (n is Control) or n == _backdrop or not _shown(n) or _inside_subviewport(n):
			continue
		if _backdrop != null and _backdrop.is_ancestor_of(n):
			continue
		var c := n as Control
		var layer := _layer_of(c)
		var r := c.get_global_rect()
		if c.mouse_filter != Control.MOUSE_FILTER_IGNORE:
			var ri := r.intersection(vrect)
			if ri.size.x * ri.size.y >= 0.95 * area and not modal.has(layer):
				modal.append(layer)
		if _draws(c):
			drawers.append([layer, r, str(root.get_path_to(c)), c.get_class()])
		var words = null
		if c is BaseButton:
			words = str(n.text) if ("text" in n) else ""
		elif c is Label:
			words = (c as Label).text
		elif c is RichTextLabel:
			words = (c as RichTextLabel).get_parsed_text()
		elif c is LineEdit:
			words = (c as LineEdit).text
		if words == null or (not (c is BaseButton) and str(words).strip_edges() == ""):
			continue
		rows.append([layer, r.get_center(), str(root.get_path_to(c)), str(words)])
	var live_floor := -1000000
	for l in modal:
		live_floor = maxi(live_floor, int(l))
	var hits: Array = []
	var suspended := 0
	for row in rows:
		if int(row[0]) < live_floor:
			suspended += 1
			continue
		for d in drawers:
			var drect: Rect2 = d[1]
			if int(d[0]) > int(row[0]) and drect.has_point(row[1]):
				hits.append({"path": row[2], "text": str(row[3]).left(40), "layer": row[0],
						"cover": d[2], "cover_class": d[3], "cover_layer": d[0]})
				break
	modal.sort()
	return {"under_modal": hits.slice(0, 60), "under_modal_count": hits.size(),
			"modal_layers": modal, "live_floor": live_floor, "suspended_rows": suspended}


func _visible_files() -> Array:
	# R4's census reads the files that drew the frame: the scene file and the
	# script (with its base scripts) of every node shown AND of its ancestors
	# (a CanvasLayer is no CanvasItem, yet its script builds what it shows —
	# the top bar, the war HUD, the rail), plus the shot's own scene and root
	# script whatever they show.
	var seen := {}
	var picked := {}
	var nodes: Array = []
	for n in _all_nodes(root):
		if n == _backdrop or not _shown(n):
			continue
		var p: Node = n
		while p != null and p != root and not picked.has(p.get_instance_id()):
			picked[p.get_instance_id()] = true
			nodes.append(p)
			p = p.get_parent()
	if _node != null and is_instance_valid(_node):
		nodes.append(_node)
	for n in nodes:
		var s = n.get_script()
		while s is Script:
			var p := (s as Script).resource_path
			if p != "":
				seen[p] = true
			s = (s as Script).get_base_script()
		var sf := str(n.scene_file_path)
		if sf != "":
			seen[sf] = true
	var out := seen.keys()
	out.sort()
	return out


func _probe(paths) -> Dictionary:
	var out := {}
	if not (paths is Array) or _node == null:
		return out
	for p in paths:
		var n := _node.get_node_or_null(str(p))
		if n is Control:
			var r: Rect2 = (n as Control).get_global_rect()
			out[str(p)] = {"rect": [r.position.x, r.position.y, r.size.x, r.size.y],
					"visible": (n as Control).is_visible_in_tree()}
		else:
			out[str(p)] = {"missing": n == null}
	return out


func _on_node_added_contrast(node: Node) -> void:
	var utils_hc: Variant = Utils
	utils_hc.call_deferred("contrast_node", node)


func _on_stray_input(event: InputEvent) -> void:
	if event is InputEventKey or event is InputEventMouseButton:
		_stray_input += 1


func _on_focus_changed(node: Control) -> void:
	var callers: Array = []
	for f in get_stack():
		callers.append("%s:%d %s" % [str(f.get("source", "")).get_file(), int(f.get("line", 0)), str(f.get("function", ""))])
	_focus_log.append([_frames, str(root.get_path_to(node)) if node != null else "", callers])


func _surface_rects() -> Dictionary:
	"""UXR-D1 (Pre-Deploy S9b): the logical rect of every visible TOP-LEVEL
	surface — a Control whose parent is a CanvasLayer, or a child of the
	shot's own scene root — so a run can say whether a setting moved a panel
	(Text size must move none). Keyed by the node's path from the root."""
	var out := {}
	for n in _all_nodes(root):
		if not (n is Control) or n == _backdrop or not _shown(n):
			continue
		var parent: Node = n.get_parent()
		if not (parent is CanvasLayer or (_node != null and parent == _node and _node is Control)):
			continue
		if parent == _backdrop:
			continue
		var r: Rect2 = (n as Control).get_global_rect()
		out[str(root.get_path_to(n))] = [r.position.x, r.position.y, r.size.x, r.size.y]
	return out


# ── teardown / exit ─────────────────────────────────────────────────────────

func _note_error(msg: String) -> void:
	_current["errors"].append(msg)
	push_error("[IQ10] " + msg)


func _abort_shot(msg: String) -> void:
	_note_error(msg)
	_phase = "teardown"
	_wait = 0


func _adopt_overrides(payload) -> void:
	if payload is Dictionary and payload.get("nation_display_overrides") is Dictionary:
		var flags = payload.get("nation_flag_overrides")
		Utils.set_formation_overrides(payload["nation_display_overrides"],
				flags if flags is Dictionary else {})


func _teardown():
	_current["ok"] = (_current["errors"] as Array).is_empty() \
			and not (_current["frames"] as Array).is_empty()
	_results.append(_current)
	print("[IQ10] END %s@%s ok=%s" % [_current["id"], _scale_key(), str(_current["ok"])])
	if _node != null and is_instance_valid(_node):
		_node.queue_free()
	_node = null
	for s in _stubs:
		if is_instance_valid(s):
			s.queue_free()
	_stubs = []
	# Loops live under the audio singleton and outlive the scene that began
	# them (the enemy phase starts "march_long"); one shot's identity
	# overrides must not dress the next.
	AudioManager.stop_all_loops()
	AudioManager.stop_all_cues()
	Utils.set_formation_overrides({}, {})
	_scale_i += 1
	if _scale_i >= _scales().size():
		_scale_i = 0
		_shot_i += 1
	_phase = "done" if _shot_i >= _shots.size() else "prepare"
	_wait = TEARDOWN_WAIT


func _read_json(path: String):
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return null
	var parsed = JSON.parse_string(f.get_as_text())
	f.close()
	return parsed


func _finish():
	var failed := 0
	for r in _results:
		if not bool(r.get("ok", false)):
			failed += 1
	var summary := {
		"harness": "tools/iq10_surface_screenshot.gd",
		"godot": Engine.get_version_info().get("string", ""),
		"fatal": _fatal,
		"shots_run": _results.size(),
		"shots_failed": failed,
		"results": _results,
	}
	var out_path := str(_spec.get("result", ""))
	if out_path == "":
		out_path = OS.get_environment("IQ10_RESULT")
	if out_path != "":
		DirAccess.make_dir_recursive_absolute(out_path.get_base_dir())
		var f := FileAccess.open(out_path, FileAccess.WRITE)
		if f != null:
			f.store_string(JSON.stringify(summary, "  "))
			f.close()
	print("[IQ10] DONE shots=%d failed=%d fatal=%s" % [_results.size(), failed, _fatal])
	quit(1 if (_fatal != "" or failed > 0) else 0)
