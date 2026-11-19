extends SceneTree
# Row PW part 2 (November 18, 2026) — THE PLAYED BOARD, DRIVEN.
#
#   Godot --headless --path godot-client/project-sovereign \
#         --script <abs path>/tools/pw2_played_board_probe.gd -- <out json>
#
# The enemy's moves are played on the map in two beats: `play_all_regions`
# (the pieces march, a province that changed hands keeps its old colour) and
# `finish_play` (the new board, whole). The review (PW2-R9) found the second
# beat had ONE caller — the report's own telling — and a response another
# window answers first (a letter, a petition, a paradox riding the end of the
# turn) returned before it: the board stood in its old colours with its
# marchers held out. A played board now finishes itself.
#
# The probe stands the smoke map (the shared renderer, the registry's 1805
# board), puts a corps the fog half-hides on it, and plays three boards:
#   1. nobody comes back for beat two  -> the board finishes itself;
#   2. the caller finishes at once     -> the board's own clock finds nothing to do;
#   3. a newer board lands meanwhile   -> the played one never lands over it.
# What it reads is the renderer's own state, never a picture. Read by
# tests/test_pw2_the_enemys_moves.py::TestThePlayedBoardDriven.

const MARCH_S := 0.2

var _out := ""
var _result := {}


func _initialize() -> void:
	_run.call_deferred()


func _markers(map) -> int:
	var n := 0
	if map.force_layer == null:
		return 0
	for child in map.force_layer.get_children():
		if str(child.name).begins_with("MarchingMarker"):
			n += 1
	return n


func _run() -> void:
	var a := OS.get_cmdline_user_args()
	if a.size() < 1:
		push_error("usage: -- <out json>")
		quit(2)
		return
	_out = a[0]
	var scene: PackedScene = load("res://scenes/europe_map_smoke.tscn")
	var map = scene.instantiate()
	root.add_child(map)
	for _i in range(12):
		await process_frame
	var seeded: Dictionary = map._seeded_map_data.duplicate(true)
	# three wired provinces with a holder: where the corps stands, where he
	# marches, and the one that changes hands
	var wired: Array = []
	for name in seeded:
		if map.region_controllers.has(name) and str(map.region_controllers[name]) != "Neutral":
			wired.append(str(name))
	wired.sort()
	if wired.size() < 3:
		_finish({"error": "the smoke board has fewer than three held provinces"})
		return
	var stands: String = wired[0]
	var goes: String = wired[1]
	var taken: String = wired[2]
	var old_holder: String = str(map.region_controllers[taken])
	var new_holder: String = "France" if old_holder != "France" else "Austria"
	var corps := {"name": "Mack", "nation": str(map.region_controllers[stands]), "fog_level": "partial",
		"strength_band": "20,000 to 30,000"}

	var first: Dictionary = seeded.duplicate(true)
	first[stands]["fogged_forces"] = [corps]
	map.update_all_regions(first)
	for _i in range(3):
		await process_frame
	_result["stands_before"] = map.region_fogged_forces.has(stands)

	# ── 1. nobody comes back for beat two ────────────────────────────────
	var second: Dictionary = seeded.duplicate(true)
	second[goes]["fogged_forces"] = [corps]
	second[taken]["controller"] = new_holder
	var played: Dictionary = map.play_all_regions(second, MARCH_S)
	_result["played"] = {"changed": played.get("changed", []), "moved": int(played.get("moved", 0))}
	_result["one_held_old_colour"] = str(map.region_controllers[taken]) == old_holder
	_result["one_final_pending"] = not map._play_final.is_empty()
	_result["one_marcher_held_out"] = not map.region_fogged_forces.has(goes)
	_result["one_markers_marching"] = _markers(map)
	await create_timer(MARCH_S + map.PLAY_SELF_FINISH_S + 0.25).timeout
	_result["one_self_finished"] = map._play_final.is_empty()
	_result["one_new_colour"] = str(map.region_controllers[taken]) == new_holder
	_result["one_marcher_arrived"] = map.region_fogged_forces.has(goes) and not map.region_fogged_forces.has(stands)
	_result["one_markers_after"] = _markers(map)

	# ── 2. the caller finishes at once ───────────────────────────────────
	var third: Dictionary = seeded.duplicate(true)
	third[goes]["fogged_forces"] = [corps]
	third[taken]["controller"] = old_holder
	map.play_all_regions(third, MARCH_S)
	_result["two_caller_finished"] = map.finish_play()
	_result["two_colour_at_once"] = str(map.region_controllers[taken]) == old_holder
	await create_timer(MARCH_S + map.PLAY_SELF_FINISH_S + 0.25).timeout
	_result["two_colour_stays"] = str(map.region_controllers[taken]) == old_holder
	_result["two_nothing_left"] = not map.finish_play()

	# ── 3. a newer board lands while the played one marches ──────────────
	var fourth: Dictionary = seeded.duplicate(true)
	fourth[taken]["controller"] = new_holder
	map.play_all_regions(fourth, MARCH_S)
	var fifth: Dictionary = seeded.duplicate(true)
	fifth[taken]["controller"] = "Britain"
	map.update_all_regions(fifth)
	await create_timer(MARCH_S + map.PLAY_SELF_FINISH_S + 0.25).timeout
	_result["three_newer_board_stands"] = str(map.region_controllers[taken])
	_result["three_final_empty"] = map._play_final.is_empty()
	_finish(_result)


func _finish(result: Dictionary) -> void:
	var f := FileAccess.open(_out, FileAccess.WRITE)
	if f != null:
		f.store_string(JSON.stringify(result))
		f.close()
	quit(0)
