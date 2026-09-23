extends SceneTree
# NUI "The Admiralty on the Map" — the REAL game map (scenes/map.gd, the
# Europe renderer) driven with a captured board so its fleet pieces, sea
# segments and hitboxes can be read back — and, windowed, SHOT.
#
#   $env:NUI_SPEC = "<absolute path to a spec JSON>"
#   headless (the driven pin):
#     <godot> --headless --path godot-client/project-sovereign \
#             --script ../../tools/nui_map_capture.gd
#   windowed (the evidence PNG — rendering needs a real window):
#     <godot> --audio-driver Dummy --windowed --resolution 1600x900 \
#             --position 2565,20 --path godot-client/project-sovereign \
#             --script ../../tools/nui_map_capture.gd
#
# Spec: {"topology": <GET /map_topology>, "game_state": <GET /test → game_state>,
#        "out": <abs result JSON>, "png": <abs PNG path or "">,
#        "hover": [x, y] (optional — a WORLD point to hit-test for a crossing),
#        "settle": 40}
#
# The map is fed exactly as main.gd feeds it — `set_region_topology`,
# `update_all_regions(map_data)`, `update_naval_overlay(naval_overlay)` — and
# after the settle the JSON records every fleet piece (nation, station,
# layer position), every fleet hitbox, the sea-segment count, the nearest
# crossing to `hover`, and the pieces layer's presence. Nothing here decides
# where a fleet stands; the pytest reads the record.
#
# Safety rails (IQ-10's): UiSettings shimmed in memory; no setter called;
# the result JSON is written on every exit path.

const FRAME_LIMIT := 2000

var _frames := 0
var _phase := "boot"
var _spec: Dictionary = {}
var _map = null
var _wait := 0
var _result: Dictionary = {}


func _init():
	UiSettings._cfg = ConfigFile.new()
	process_frame.connect(_tick)


func _tick():
	_frames += 1
	if _frames > FRAME_LIMIT:
		_result["error"] = "frame limit hit in phase " + _phase
		_finish()
		return
	match _phase:
		"boot":
			var path := OS.get_environment("NUI_SPEC")
			if path == "":
				_result["error"] = "NUI_SPEC is not set"
				_finish()
				return
			var parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
			if not (parsed is Dictionary):
				_result["error"] = "the spec at " + path + " is not a JSON object"
				_finish()
				return
			_spec = parsed
			var script = load("res://scenes/map.gd")
			_map = Control.new()
			_map.name = "MapArea"
			_map.set_script(script)
			_map.set_anchors_preset(Control.PRESET_FULL_RECT)
			root.add_child(_map)
			_wait = 3
			_phase = "feed"
		"feed":
			_wait -= 1
			if _wait > 0:
				return
			var topology = _spec.get("topology", {})
			if topology is Dictionary and _map.has_method("set_region_topology"):
				_map.set_region_topology(topology)
			var gs = _spec.get("game_state", {})
			if gs is Dictionary:
				var map_data = gs.get("map_data", {})
				if map_data is Dictionary and _map.has_method("update_all_regions"):
					_map.update_all_regions(map_data)
				if _map.has_method("update_naval_overlay"):
					_map.update_naval_overlay(gs.get("naval_overlay", {}))
			_wait = int(_spec.get("settle", 40))
			_phase = "record"
		"record":
			_wait -= 1
			if _wait > 0:
				return
			_record()
			var png := str(_spec.get("png", ""))
			if png != "" and not DisplayServer.get_name().begins_with("headless"):
				var img: Image = root.get_texture().get_image()
				if img != null:
					img.save_png(png)
					_result["png"] = png
			_finish()


func _record() -> void:
	_result["pieces_layer"] = _map.pieces_layer != null if "pieces_layer" in _map else false
	var pieces := []
	if "_fleet_pieces" in _map:
		for nation in _map._fleet_pieces:
			var p = _map._fleet_pieces[nation]
			if p == null or not is_instance_valid(p):
				continue
			pieces.append({"nation": str(nation), "position": [p.position.x, p.position.y],
				"arm": str(p.arm) if "arm" in p else ""})
	_result["fleet_pieces"] = pieces
	var boxes := []
	if "fleet_hitboxes" in _map:
		for hb in _map.fleet_hitboxes:
			var r: Rect2 = hb["rect"]
			boxes.append({"nation": str(hb["fleet"].get("nation", "")),
				"station": str(hb["fleet"].get("station", "")),
				"rect": [r.position.x, r.position.y, r.size.x, r.size.y]})
	_result["fleet_hitboxes"] = boxes
	_result["sea_segments"] = _map._sea_segments.size() if "_sea_segments" in _map else -1
	var hover = _spec.get("hover", null)
	if hover is Array and hover.size() == 2 and _map.has_method("_nearest_sea_link"):
		_result["hover"] = _map._nearest_sea_link(Vector2(float(hover[0]), float(hover[1])))
	# A crossing hit-test AT a segment's own midpoint must find that segment.
	if "_sea_segments" in _map and _map._sea_segments.size() > 0 and _map.has_method("_nearest_sea_link"):
		var seg = _map._sea_segments[0]
		var mid: Vector2 = (seg["start"] + seg["end"]) / 2.0
		_result["midpoint_probe"] = _map._nearest_sea_link(mid)
		_result["midpoint_probe_expected"] = [str(seg["a"]), str(seg["b"])]


func _finish():
	var out := str(_spec.get("out", ""))
	if out == "":
		out = OS.get_environment("NUI_OUT")
	if out != "":
		var f := FileAccess.open(out, FileAccess.WRITE)
		if f != null:
			f.store_string(JSON.stringify(_result))
			f.close()
	quit(0 if not _result.has("error") else 1)
