extends SceneTree
# NV-7 evidence harness (windowed, NOT --headless) — the naval diorama's
# visual check, following the IGR-G1 settlement-popup pattern:
#
#   <godot> --path godot-client/project-sovereign \
#           --script ../../tools/naval_diorama_screenshot.gd
#
# It instantiates the REAL battle_diorama.tscn, feeds it a REAL
# `naval_diorama` payload produced by backend/game_logic/naval_diorama.py,
# lets the settled frame render, and saves a PNG to user://.
#
# Capture the payload first (it is NOT committed — it lives inside res://
# only so this script can read it without a permission dance):
#
#   .venv/Scripts/python.exe -c "...resolve_fleet_action..." \
#       > godot-client/project-sovereign/naval_diorama.json
#
# and delete it after the run. `show_diorama(data, true)` opens SETTLED
# (the final frame), which is what a screenshot wants — the cinematic
# tween is checked live, not in a still.

var _frames := 0
var _popup = null

func _init():
	process_frame.connect(_tick)

func _tick():
	_frames += 1
	if _frames == 1:
		root.mode = Window.MODE_WINDOWED
		root.size = Vector2i(1400, 900)
		root.position = Vector2i(120, 60)
		return
	if _frames == 3:
		var f = FileAccess.open("res://naval_diorama.json", FileAccess.READ)
		if f == null:
			_fail("naval_diorama.json missing")
			return
		var payload = JSON.parse_string(f.get_as_text())
		f.close()
		if not (payload is Dictionary):
			_fail("payload did not parse")
			return
		var scene = load("res://scenes/battle_diorama.tscn")
		_popup = scene.instantiate()
		root.add_child(_popup)
		_popup.show_diorama(payload, false)   # settled: the final frame
		return
	if _frames == 40:
		var img: Image = root.get_texture().get_image()
		img.save_png("user://nv7_naval_diorama.png")
		var out = FileAccess.open("user://nv7_result.json", FileAccess.WRITE)
		out.store_string(JSON.stringify({"ok": true}))
		out.close()
		quit(0)

func _fail(msg: String) -> void:
	var out = FileAccess.open("user://nv7_result.json", FileAccess.WRITE)
	out.store_string(JSON.stringify({"error": msg}))
	out.close()
	quit(1)
