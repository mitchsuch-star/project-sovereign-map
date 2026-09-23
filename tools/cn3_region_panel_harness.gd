extends SceneTree
# CN-3 "The Chip Names the Man" — the region panel and the commission bench,
# DRIVEN, headless.
#
#   $env:CN3_SPEC = "<absolute path to a spec JSON>"
#   <godot> --headless --path godot-client/project-sovereign \
#           --script <abs path>/tools/cn3_region_panel_harness.gd
#
# The spec (written by tests/test_cn3_the_chip_tells_the_truth.py):
#   {"game_state": <GET /test → game_state>, "regions": [<province>, ...],
#    "recruitment": <recruitment.build_recruitment_payload>, "out": <abs path>}
#
# For each province the REAL `region_panel.tscn` renders through its own
# `show_region`, handed a map-node stand-in derived from `game_state.map_data`
# exactly as IQ-10's MapStub derives it (`tools/iq10_surface_screenshot.gd`),
# and the panel's own bbcode is written out. The bench renders through
# `marshal_management.gd`'s own `_render_commission_view`. Nothing here decides
# what a chip says: the test drives every `do:` url the panel rendered through
# POST /command and reads the effect.
#
# Why a driven pin and not a source census: the memo's R6 — a pin that reads
# the source is killed by a text mutation by construction and proves nothing
# about what the player sees.
#
# Safety rails (IQ-10's): UiSettings is shimmed onto an in-memory ConfigFile
# before any scene loads, no setter is called, and the result JSON is written
# on every exit path.

const FRAME_LIMIT := 600

var _frames := 0
var _phase := "boot"
var _spec: Dictionary = {}
var _panel = null
var _map = null
var _bench = null
var _wizard = null
var _result: Dictionary = {"regions": {}, "bench": ""}


class MapStub extends Node:
	# What `region_panel.gd` reads off the map node — IQ-10's MapStub, verbatim.
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
			var path := OS.get_environment("CN3_SPEC")
			if path == "":
				_result["error"] = "CN3_SPEC is not set"
				_finish()
				return
			var text := FileAccess.get_file_as_string(path)
			var parsed = JSON.parse_string(text)
			if not (parsed is Dictionary):
				_result["error"] = "the spec at " + path + " is not a JSON object"
				_finish()
				return
			_spec = parsed
			_map = MapStub.new()
			root.add_child(_map)
			_map.load_game_state(_spec.get("game_state", {}))
			_panel = load("res://scenes/region_panel.tscn").instantiate()
			root.add_child(_panel)
			_bench = load("res://scenes/marshal_management.tscn").instantiate()
			root.add_child(_bench)
			# CN-4: the diplomacy wizard, for its REAL `_build_command` and
			# `echo_note` — a census that composed the echoes from the
			# template text could not see a branch condition change.
			_wizard = load("res://scenes/diplomacy_wizard.tscn").instantiate()
			root.add_child(_wizard)
			_phase = "render"
		"render":
			# One frame after add_child: every @onready is bound.
			for region in _spec.get("regions", []):
				_panel.show_region(str(region), _map)
				_result["regions"][str(region)] = _panel.content_area.text
			_bench.cached_recruitment = _spec.get("recruitment", {})
			_bench._render_commission_view()
			_result["bench"] = _bench.content_area.text
			# CN-4: the Generals cards too, when the spec carries the
			# `/marshal_overview` response — the screen's own renderer.
			var overview = _spec.get("overview", {})
			if overview is Dictionary and not overview.is_empty():
				_bench.cached_data = overview.get("marshals", [])
				_bench.cached_ladder = overview.get("glory_ladder", [])
				_bench.cached_glory_window = int(overview.get("glory_window", 8))
				_bench._commission_view = false
				_bench._render_all_cards()
				_result["cards"] = _bench.content_area.text
			# Each case: [action_id, nation, payload] -> [echo, echo_note].
			var echoes = []
			for case in _spec.get("wizard_cases", []):
				var payload = case[2] if case.size() > 2 and case[2] is Dictionary else {}
				echoes.append([_wizard._build_command(str(case[0]), str(case[1]), payload),
					_wizard.echo_note(str(case[0]))])
			_result["wizard"] = echoes
			_finish()


func _finish():
	var out := str(_spec.get("out", ""))
	if out == "":
		out = OS.get_environment("CN3_OUT")
	if out != "":
		var f := FileAccess.open(out, FileAccess.WRITE)
		if f != null:
			f.store_string(JSON.stringify(_result))
			f.close()
	quit(1 if _result.has("error") else 0)
