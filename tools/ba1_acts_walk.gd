extends SceneTree
# Row BA, BA-1 "the battle in acts" — the camera for the tableau's acts.
#
#   $env:BA1_SPEC = "<absolute path to a spec JSON>"
#   <godot> --audio-driver Dummy --windowed --resolution 1600x900 \
#           --position 5200,20 --log-file <abs log> \
#           --path godot-client/project-sovereign \
#           --script ../../tools/ba1_acts_walk.gd
#
# Do not write specs by hand: `tools/ba1_acts_walk.py` builds one from the
# payloads `tools/ba1_stage_battles.py` staged (real 1805 battles through the
# real attack road) and runs this — windowed for the frames (a frame needs a
# real renderer), or `--headless` with the spec's `record_only` for the
# record alone (the suite's driven pin, tests/test_ba1_the_battle_in_acts.py).
#
# Per shot: the REAL battle_diorama.tscn is instantiated and its REAL entry
# (`show_diorama(payload, cinematic)`) is called, with Settings → Battle
# scenes (and Reduce motion) set as the shot says. Then each event of the
# shot fires at its moment, in SCENE seconds since the tableau opened. The
# acts are tweens, stepped by the tree's own frame deltas, so the walk counts
# those same deltas (never the wall clock: opening the first tableau takes a
# third of a second the tweens never see, and `time_scale` in the spec — the
# suite runs the scene eight times faster — would multiply the error):
#     {"t": 0.9, ...}                              a fixed moment
#     {"act": "crisis", "after": 0.9, ...}         WATCHED: the table is read
#                                                  the first frame it names
#                                                  that act, and shot `after`
#                                                  seconds into it if the act
#                                                  is still named then (a slow
#                                                  frame on a loaded machine
#                                                  cannot step over an act)
#     {"beat": "arrive", "where": {"late": true},
#      "nth": 0, "after": 0.6, ...}                 a development, by its kind
#     {"end": true, "after": 2.8, ...}             after the last beat's hold
#     "frames": 4                                  …and not before this many
#                                                  frames of the showing (a
#                                                  settled table's plate is
#                                                  laid out a frame late)
# and does one or both of:
#     "shot": "<tag>"     a frame (unless record_only) and a record of the table
#     "do": "click"                                a REAL left click at the
#                                                  tableau's centre (the one
#                                                  moment input is let in)
#     "do": "click_margin"                         the same on the dark margin
#     "do": "skip" | "replay" | "close"            the handler a key or a
#                                                  button calls
#     "do": "reopen", "cinematic": bool,
#      "strip_script": bool                        the SAME tableau shows the
#                                                  battle again (as the next
#                                                  battle of a turn would)
# After a "replay" or a "reopen" the clock restarts: later events are timed
# from it.
# An event whose act or beat this battle does not play is recorded as missed.
#
# The record, per frame: which act is named and what is told, where every
# corps stands against its place in the line and its resting place, its pips
# and whether its plinth is turned down, the dice, the banner, `_final` — and
# `marks`: where every line of text on the baize and every portrait stands, in
# the stage's own pixels, by the INK's extent (a label's box is wider than
# its words: the two leads' name boxes overlap by design, their words do not).
#
# Safety rails (the IQ-10 harness's): UiSettings is shimmed onto an in-memory
# ConfigFile that is never saved; audio runs on the Dummy driver; the window
# ignores all input except the walk's own clicks (`_click`), which are let in
# for one event and shut out again. The result JSON is written on every exit
# path.

const HARD_FRAME_LIMIT := 4000000

var _spec: Dictionary = {}
var _shots: Array = []
var _results: Array = []
var _i := -1
var _node = null
var _payload: Dictionary = {}  # this shot's battle, whole (a `reopen` shows it again)
var _events: Array = []        # this shot's events, in spec order
var _queue: Array = []         # [{at, event}] resolved against the scene clock
var _watches: Array = []       # act events: [{event, at, first}] read off the table
var _ei := 0
var _scene_t := 0.0            # scene seconds since this showing began
var _phase := "boot"
var _wait := 0
var _frames := 0
var _current: Dictionary = {}
var _time_scale := 1.0
var _record_only := false


func _init():
	UiSettings._cfg = ConfigFile.new()
	var settings_class: Variant = UiSettings
	settings_class.set("_persist", false)
	var path := OS.get_environment("BA1_SPEC")
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		push_error("[BA1] no spec at BA1_SPEC=%s" % path)
		quit(2)
		return
	var parsed = JSON.parse_string(f.get_as_text())
	f.close()
	if not (parsed is Dictionary):
		push_error("[BA1] the spec did not parse")
		quit(2)
		return
	_spec = parsed
	_shots = _spec.get("shots", [])
	_time_scale = maxf(float(_spec.get("time_scale", 1.0)), 0.1)
	_record_only = bool(_spec.get("record_only", false))
	Engine.time_scale = _time_scale
	print("[BA1] BEGIN %d shot(s)" % _shots.size())
	process_frame.connect(_tick)


func _tick() -> void:
	_frames += 1
	_scene_t += root.get_process_delta_time()
	if _frames > HARD_FRAME_LIMIT:
		_finish(3)
		return
	if _wait > 0:
		_wait -= 1
		return
	match _phase:
		"boot":
			var want = _spec.get("window", [1600, 900])
			if not _record_only:
				root.mode = Window.MODE_WINDOWED
			root.size = Vector2i(int(want[0]), int(want[1]))
			root.gui_disable_input = true
			_phase = "next"
			_wait = 6
		"next":
			_i += 1
			if _i >= _shots.size():
				_finish(0)
				return
			_open(_shots[_i])
		"play":
			_play()
		"teardown":
			if _node != null and is_instance_valid(_node):
				_node.queue_free()
			_node = null
			_results.append(_current)
			_phase = "next"
			_wait = 4


func _open(shot: Dictionary) -> void:
	_current = {"id": str(shot.get("id", "")), "frames": [], "missed": [], "ok": false}
	var scale := float(shot.get("scale", _spec.get("scale", 1.0)))
	root.content_scale_factor = scale
	UiSettings._cfg.set_value("display", "ui_scale", scale)
	var consts: Dictionary = (UiSettings as Script).get_script_constant_map()
	var text_size := float(shot.get("text_size", _spec.get("text_size",
			float(consts.get("DEFAULT_TEXT_SIZE", 1.0)))))
	UiSettings._cfg.set_value("display", "text_size", text_size)
	Utils.apply_text_size()
	UiSettings._cfg.set_value("display", "battle_scenes", str(shot.get("mode", "acts")))
	UiSettings._cfg.set_value("display", "reduce_motion", bool(shot.get("reduce_motion", false)))
	_current["mode"] = str(shot.get("mode", "acts"))
	_current["scale"] = scale
	_current["text_size"] = text_size

	var f := FileAccess.open(str(shot.get("payload", "")), FileAccess.READ)
	if f == null:
		_current["error"] = "payload missing: %s" % str(shot.get("payload", ""))
		_phase = "teardown"
		return
	var payload = JSON.parse_string(f.get_as_text())
	f.close()
	if not (payload is Dictionary):
		_current["error"] = "payload did not parse"
		_phase = "teardown"
		return
	_payload = (payload as Dictionary).duplicate(true)
	if bool(shot.get("strip_script", false)):
		payload.erase("script")       # a payload from before the acts (an old save's)
	var scene: PackedScene = load("res://scenes/battle_diorama.tscn")
	_node = scene.instantiate()
	root.add_child(_node)
	print("[BA1] shot %s" % _current["id"])
	_node.show_diorama(payload, bool(shot.get("cinematic", true)))
	_events = shot.get("events", [])
	_ei = 0
	_restart_clock(0)
	_phase = "play"


func _restart_clock(from_event: int) -> void:
	"""Time the events from `from_event` on against the showing that just
	began (the tableau's opening, or a Replay): its tweens and this clock
	are stepped by the same deltas from the next frame on."""
	_scene_t = 0.0
	_queue = []
	_watches = []
	for k in range(from_event, _events.size()):
		var event: Dictionary = _events[k]
		var when: float = _when(event)
		if when < 0.0:
			(_current["missed"] as Array).append(str(event.get("shot", event.get("do", "?"))))
			continue
		if event.has("act"):
			_watches.append({"event": event, "at": when, "first": null})
			continue
		# "frames": N — not before N frames of this showing have passed. The
		# plate, the seal and the laurels are laid out a frame AFTER the table
		# (the host awaits one to measure the plate), and eight times faster
		# the first frame alone is a second of scene time.
		_queue.append({"at": when, "event": event, "index": k,
				"min_frame": _frames + int(event.get("frames", 0))})
		if str(event.get("do", "")) in ["replay", "reopen"]:
			break          # what follows is timed from the replay (or the re-opening)
	_queue.sort_custom(func(a, b): return a["at"] < b["at"])
	_ei = 0


func _rows() -> Array:
	var acts = _node._acts
	if acts == null or bool(_node._final):
		return []
	return acts._played


func _when(event: Dictionary) -> float:
	"""The event's moment, in scene seconds since this showing began."""
	if event.has("t"):
		return float(event["t"])
	var rows: Array = _rows()
	if event.has("end"):
		var last := 0.0
		for row in rows:
			last = maxf(last, float(row.get("at", 0.0)) + float(row.get("hold", 0.0)))
		return last + float(event.get("after", 2.8))
	var seen := 0
	for row in rows:
		var beat: Dictionary = row["beat"]
		if event.has("act"):
			if str(row["act"]) != str(event["act"]) or not bool(row["captioned"]):
				continue
		elif event.has("beat"):
			if str(beat.get("kind", "")) != str(event["beat"]):
				continue
			var fits := true
			var where = event.get("where", {})
			if where is Dictionary:
				for key in where:
					if beat.get(key, null) != where[key]:
						fits = false
			if not fits:
				continue
		else:
			return -1.0
		if seen < int(event.get("nth", 0)):
			seen += 1
			continue
		return float(row.get("at", 0.0)) + float(event.get("after", 0.9))
	return -1.0


func _named_act() -> String:
	var acts = _node._acts
	if acts == null or acts._act_label == null or not is_instance_valid(acts._act_label):
		return ""
	return str(acts._act_label.text) if acts._act_label.visible else ""


func _watch() -> void:
	"""Each frame: an act the table names is read at once (the record), and
	shot when its moment comes if it is still named; an act the table has
	moved on from keeps the record it was first read with."""
	var named: String = _named_act()
	var still: Array = []
	for w in _watches:
		var event: Dictionary = w["event"]
		var shown: bool = named != "" and named == str(BattleActs.ACT_TITLES.get(str(event["act"]), "-"))
		if shown and w["first"] == null:
			var first := _read_table()
			first["tag"] = str(event.get("shot", event["act"]))
			first["at_ms"] = int(_scene_t * 1000.0)
			first["saved"] = true
			first["read_at_first_sight"] = true
			w["first"] = first
		if shown and _scene_t >= float(w["at"]):
			_capture(str(event.get("shot", event["act"])))
		elif not shown and w["first"] != null:
			(_current["frames"] as Array).append(w["first"])
		else:
			still.append(w)
	_watches = still


func _close_watches() -> void:
	"""The showing is over: an act that was read keeps its record; one the
	table never named is missed."""
	for w in _watches:
		if w["first"] != null:
			(_current["frames"] as Array).append(w["first"])
		else:
			(_current["missed"] as Array).append(str(w["event"].get("shot", w["event"]["act"])))
	_watches = []


func _play() -> void:
	_watch()
	if _ei >= _queue.size():
		_close_watches()
		_current["ok"] = true
		_phase = "teardown"
		_wait = 2
		return
	var item: Dictionary = _queue[_ei]
	if _scene_t < float(item["at"]) or _frames < int(item.get("min_frame", 0)):
		return
	if (item["event"] as Dictionary).has("end") and _verdict_being_written():
		return     # BA-2: the kept end frame shows Berthier's line whole, not half written
	_ei += 1
	var event: Dictionary = item["event"]
	if event.has("shot") and not event.has("do"):
		_capture(str(event["shot"]))
		return
	match str(event.get("do", "")):
		"click":
			_click(Vector2(root.size) / 2.0)
		"click_margin":
			_click(Vector2(12.0, 12.0))
		"skip":
			_node._skip_to_final()
		"replay":
			_close_watches()
			_node._on_replay_pressed()
			_restart_clock(int(item["index"]) + 1)
		"close":
			_node._on_close_pressed()
		"reopen":
			# The SAME tableau shows a battle again (the next battle of the
			# turn, or a second viewing): nothing an interrupted showing left
			# on the chrome may be on it. What follows is timed from here.
			_close_watches()
			var again: Dictionary = _payload.duplicate(true)
			if bool(event.get("strip_script", false)):
				again.erase("script")
			_node.show_diorama(again, bool(event.get("cinematic", false)))
			_restart_clock(int(item["index"]) + 1)
	_wait = 1
	if event.has("shot"):
		_capture(str(event["shot"]))


func _verdict_being_written() -> bool:
	"""The host writes the verdict out a character at a time once the battle is
	told (`_type_verdict`): true while that is still going. A short showing (an
	assault, a cannonade) reaches its end shot before a long line is done."""
	if _node == null or not bool(_node._final):
		return false
	var v: RichTextLabel = _node._verdict
	return v != null and v.visible_characters >= 0 \
			and v.visible_characters < v.get_total_character_count()


func _click(at: Vector2) -> void:
	"""A left click at a point of the window, as the mouse gives it."""
	root.gui_disable_input = false
	for pressed in [true, false]:
		var ev := InputEventMouseButton.new()
		ev.button_index = MOUSE_BUTTON_LEFT
		ev.pressed = pressed
		ev.position = at
		ev.global_position = at
		root.push_input(ev)
	root.gui_disable_input = true


func _capture(tag: String) -> void:
	var row := _read_table()
	row["tag"] = tag
	row["at_ms"] = int(_scene_t * 1000.0)
	row["saved"] = true
	if not _record_only:
		var name := "%s_%s.png" % [_current["id"], tag]
		var img: Image = root.get_texture().get_image()
		row["png"] = name
		row["saved"] = img.save_png(str(_spec.get("out", "")).path_join(name)) == OK
	(_current["frames"] as Array).append(row)


func _read_table() -> Dictionary:
	"""What stands on the table now, as plain data."""
	var row := {"final": bool(_node._final), "visible": bool(_node.visible)}
	row["banner"] = str(_node._banner.text) if _node._banner.visible else ""
	row["sub_banner"] = str(_node._sub_banner.text) if _node._sub_banner.visible else ""
	row["told"] = str(_node._verdict.get_parsed_text())
	row["replay_shown"] = bool(_node._btn_replay.visible)
	row["close_shown"] = bool(_node._btn_close.visible)
	# BA1-X6: what the table holds back while the day is open.
	row["vignette"] = str(_node._vignette.modulate.to_html())
	var laurels := 0
	for laurel in [_node._laurel_l, _node._laurel_r]:
		if laurel != null and laurel.visible and laurel.modulate.a > 0.05:
			laurels += 1
	row["laurels"] = laurels
	row["tray_alpha_pct"] = int(round(_node._tray.modulate.a * 100.0))
	# The plate's furniture, where it is SHOWN, in window pixels (BA1-X8: the
	# laurels against the seal and the buttons).
	var chrome := {}
	for pair in [["seal", _node._seal], ["laurel_l", _node._laurel_l], ["laurel_r", _node._laurel_r],
			["replay", _node._btn_replay], ["close", _node._btn_close], ["plate", _node._nameplate]]:
		var piece = pair[1]
		if piece == null or not is_instance_valid(piece):
			continue
		if not (piece as CanvasItem).is_visible_in_tree() or (piece as CanvasItem).modulate.a <= 0.05:
			continue
		var pr: Rect2 = (piece as Control).get_global_rect()
		chrome[pair[0]] = [int(round(pr.position.x)), int(round(pr.position.y)),
				int(round(pr.size.x)), int(round(pr.size.y))]
	row["chrome"] = chrome
	var acts = _node._acts
	row["act"] = ""
	row["dice_shown"] = false
	row["plays"] = false
	row["played"] = []
	if acts != null:
		if acts._act_label != null and is_instance_valid(acts._act_label) and acts._act_label.visible:
			row["act"] = str(acts._act_label.text)
		if acts._dice != null and is_instance_valid(acts._dice):
			row["dice_shown"] = bool(acts._dice.visible)
			var d: Control = acts._dice
			row["dice_rect"] = [int(d.position.x), int(d.position.y), int(d.size.x), int(d.size.y)]
		row["plays"] = bool(acts.plays())
		var beats: Array = []
		for item in acts._played:
			beats.append({"act": str(item["act"]), "kind": str(item["beat"].get("kind", "")),
					"captioned": bool(item["captioned"]),
					"at_ms": int(float(item.get("at", 0.0)) * 1000.0),
					"hold_ms": int(float(item["hold"]) * 1000.0)})
		row["played"] = beats
	# BA-2: which table is laid, the wall, the works.
	row["kind"] = str(_node._data.get("kind", "battle"))
	row["laid"] = str(acts._laid) if acts != null else "file"
	row["wall"] = ""
	var works := {}
	if acts != null:
		if acts._wall != null and is_instance_valid(acts._wall):
			row["wall"] = str(acts._wall.state())
			row["wall_ladders_pct"] = int(round(float(acts._wall._ladders) * 100.0))
			row["wall_rect"] = _on_stage(acts._wall, acts._wall.stone())
		for who in acts._works:
			if is_instance_valid(acts._works[who]):
				works[str(who)] = int(acts._works[who].shown_pct())
	row["works"] = works
	var corps: Array = []
	var labels: Array = []
	for b in _node._blocks_left + _node._blocks_right:
		var node: Node2D = b["node"]
		var plinth = b.get("plinth", null)
		var art: Node2D = node.get_node_or_null("Art")
		var words: Array = []
		for child in node.get_children():
			if child is Label:
				labels.append(str((child as Label).text))
				if (child as Label).text.strip_edges() != "" and _shown(child):
					words.append(_ink(child))
		var xs: Array = []
		for f in b["figures"]:
			xs.append(float((f as Node2D).position.x))
		var locket: CanvasItem = b["locket"]
		var standard = b["standard"]
		corps.append({
			"name": str((b["data"] as Dictionary).get("name", "")),
			"left": bool(b["is_left"]),
			"x": int(round(node.position.x)), "y": int(round(node.position.y)),
			"home_x": int(round((b.get("home", node.position) as Vector2).x)),
			"home_y": int(round((b.get("home", node.position) as Vector2).y)),
			"rest_dx": int(round(float(b.get("rest_dx", 0.0)))),
			"alpha_pct": int(round(node.modulate.a * 100.0)),
			"dark": art != null and art.modulate != Color.WHITE,
			"status": str(b["status"]),
			"pips_lost": int(round(plinth.get_lost())) if plinth != null else -1,
			"face_down": bool(plinth.is_face_down()) if plinth != null else false,
			# BA-2: the order of battle and the manoeuvre
			"role": str(b.get("role", "")),
			"lead": bool((b["data"] as Dictionary).get("lead", false)),
			"garrison": bool((b["data"] as Dictionary).get("garrison", false)),
			"in_square": bool(b.get("in_square", false)),
			# BA2-X5: where the corps' standard stands, in its art's own px
			"standard_x": int(round((b["standard"] as Node2D).position.x)) \
					if b["standard"] != null and is_instance_valid(b["standard"]) else 0,
			"portrait_shown": locket != null and _shown(locket),
			"standard_shown": standard != null and is_instance_valid(standard) and _shown(standard),
			"body": _on_stage(art, Rect2(-78.0, -50.0, 156.0, 74.0)) if art != null else [],
			"words": words,
			"files_px": int(round(xs.max() - xs.min())) if xs.size() > 1 else 0,
		})
	row["corps"] = corps
	row["labels"] = labels
	var marks: Array = []
	_collect_marks(_node._stage, marks)
	row["marks"] = marks
	return row


func _on_stage(item: CanvasItem, local: Rect2) -> Array:
	"""`local` (in the item's own space) as [x, y, w, h] in the stage's pixels."""
	var xf: Transform2D = _node._stage.get_global_transform().affine_inverse() \
			* item.get_global_transform()
	var r := Rect2(xf * local.position, Vector2.ZERO).expand(xf * local.end)
	return [int(floor(r.position.x)), int(floor(r.position.y)),
			int(ceil(r.size.x)), int(ceil(r.size.y))]


func _shown(item: CanvasItem) -> bool:
	if not item.is_visible_in_tree():
		return false
	var alpha := 1.0
	var at: Node = item
	while at != null and at != _node._stage.get_parent():
		if at is CanvasItem:
			alpha *= (at as CanvasItem).modulate.a
		at = at.get_parent()
	return alpha > 0.05


func _ink(l: Label) -> Array:
	"""A line's own extent on the stage (a label's box is wider than its words)."""
	var need: Vector2 = l.get_minimum_size()
	var wrapped: bool = l.autowrap_mode != TextServer.AUTOWRAP_OFF
	var w: float = l.size.x if wrapped else minf(l.size.x, need.x)
	var h: float = l.size.y if wrapped else minf(l.size.y, need.y)
	var x := 0.0
	if l.horizontal_alignment == HORIZONTAL_ALIGNMENT_RIGHT:
		x = l.size.x - w
	elif l.horizontal_alignment == HORIZONTAL_ALIGNMENT_CENTER:
		x = (l.size.x - w) / 2.0
	return _on_stage(l, Rect2(x, 0.0, w, h))


func _collect_marks(node: Node, out: Array) -> void:
	for child in node.get_children():
		if child is Label:
			var l: Label = child
			if l.text.strip_edges() != "" and _shown(l):
				out.append({"kind": "text", "text": l.text.substr(0, 48), "rect": _ink(l)})
		elif child is PortraitLocket:
			var locket: Control = child
			if _shown(locket):
				out.append({"kind": "portrait", "text": str(child.get("marshal_name")),
						"rect": _on_stage(locket, Rect2(Vector2.ZERO, locket.size))})
			continue          # a portrait's own initial is not a line on the baize
		_collect_marks(child, out)


func _finish(code: int) -> void:
	if _node != null and is_instance_valid(_node):
		_node.queue_free()
	var out := FileAccess.open(str(_spec.get("result", "")), FileAccess.WRITE)
	if out != null:
		out.store_string(JSON.stringify({"exit": code, "results": _results}, "  "))
		out.close()
	print("[BA1] END")
	quit(code)
