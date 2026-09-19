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
#        mode "main"      the real `main.tscn` (Family B) — REFUSED unless
#                         SOVEREIGN_PORT points away from the player's 8005
#   3. adopts any `nation_display_overrides` the payload carries (the
#      `api_client._adopt_formation_overrides` chokepoint, mirrored);
#   4. runs the shot's `steps` (call / set / press / scroll_to / wait / shot);
#   5. saves the PNG to an ABSOLUTE path and records, per frame: every visible
#      text on screen (RichTextLabel parsed text, Label, Button + disabled +
#      tooltip), every probed node's rect, every BaseButton that lies outside
#      the logical viewport, and every RichTextLabel whose content is taller
#      than its box with no ScrollContainer above it.
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
var _backdrop: CanvasLayer = null
var _window_size := Vector2i(0, 0)
var _fatal := ""


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


# ── lifecycle ───────────────────────────────────────────────────────────────

func _init():
	# BEFORE any scene script can read a setting: an in-memory config. The
	# getters return published defaults; the player's file is never opened.
	UiSettings._cfg = ConfigFile.new()
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
	_current["window"] = [size.x, size.y]
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
	_node = packed.instantiate()
	root.add_child(_node)
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
		return
	var step = _steps[_step_i]
	_step_i += 1
	if not (step is Dictionary):
		return
	if step.has("wait"):
		_wait = int(step["wait"])
		return
	var target: Node = _node
	if step.has("node"):
		target = _node.get_node_or_null(str(step["node"]))
		if target == null:
			_note_error("step node missing: " + str(step["node"]))
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
	frame["probe"] = _probe(_shot().get("probe", []))
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
	return n is CanvasItem and (n as CanvasItem).is_visible_in_tree()


func _collect_texts() -> Array:
	var out: Array = []
	for n in _all_nodes(root):
		if n == _backdrop or not _shown(n):
			continue
		var entry := {}
		if n is RichTextLabel:
			entry = {"class": "RichTextLabel", "text": n.get_parsed_text()}
		elif n is Label:
			entry = {"class": "Label", "text": n.text}
		elif n is BaseButton and ("text" in n):
			entry = {"class": n.get_class(), "text": str(n.text), "disabled": n.disabled}
		elif n is LineEdit:
			entry = {"class": "LineEdit", "text": n.text}
		else:
			continue
		if n is Control and str((n as Control).tooltip_text) != "":
			entry["tooltip"] = (n as Control).tooltip_text
		if str(entry.get("text", "")) == "" and not entry.has("tooltip"):
			continue
		entry["path"] = str(root.get_path_to(n))
		out.append(entry)
	return out


func _buttons_offscreen(view: Vector2) -> Array:
	var out: Array = []
	var screen := Rect2(Vector2.ZERO, view)
	for n in _all_nodes(root):
		if not (n is BaseButton) or not _shown(n):
			continue
		var r: Rect2 = (n as Control).get_global_rect()
		if r.size.x <= 0.0 or r.size.y <= 0.0:
			continue
		if not screen.encloses(r):
			out.append({"path": str(root.get_path_to(n)),
					"text": (str(n.text) if ("text" in n) else ""),
					"rect": [r.position.x, r.position.y, r.size.x, r.size.y]})
	return out


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
