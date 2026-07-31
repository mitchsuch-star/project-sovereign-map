extends SceneTree
# IGR-G1 evidence harness (windowed, NOT --headless):
#   <godot> --path godot-client/project-sovereign --script ../../tools/settlement_popup_screenshot.gd
# Instantiates the real proposal_confirm_popup.tscn, feeds it a REAL
# settlement_confirm payload, lets clamp_centered_panel run, then saves a
# screenshot of the window and a JSON of the measured panel geometry to
# user:// (g1_settlement_shot.png / g1_geometry.json).
#
# The payload file is NOT committed — capture one first (backend on 8005):
#   curl -s -X POST http://127.0.0.1:8005/command -H "Content-Type: application/json" \
#     -d '{"command": "propose common peace with Britain"}' \
#     | jq .diplomatic_dialogue > godot-client/project-sovereign/settle_dialogue.json
# and delete it after the run (it lives inside res:// only so this script
# can read it without a permission dance).
#
# Used for the July 31, 2026 IGR-G before/after pack
# (docs/audits/IGR_G1_SETTLEMENT_*.png): BEFORE measured panel 720x520 with
# PerCourtScroll robbed to 145.24px on a 2550x1340 viewport; AFTER 1160x980
# with the scroll at its full 320 floor.

var _frames := 0
var _popup = null

func _init():
	process_frame.connect(_tick)

func _tick():
	_frames += 1
	if _frames == 1:
		root.mode = Window.MODE_WINDOWED
		root.size = Vector2i(2550, 1340)
		root.position = Vector2i(2565, 40)
		return
	if _frames == 3:
		var f = FileAccess.open("res://settle_dialogue.json", FileAccess.READ)
		if f == null:
			_fail("settle_dialogue.json missing")
			return
		var payload = JSON.parse_string(f.get_as_text())
		f.close()
		if not (payload is Dictionary):
			_fail("payload did not parse")
			return
		var scene = load("res://scenes/proposal_confirm_popup.tscn")
		_popup = scene.instantiate()
		root.add_child(_popup)
		_popup.show_dialogue(payload)
		return
	if _frames == 30:
		var img: Image = root.get_texture().get_image()
		img.save_png("user://g1_settlement_shot.png")
		var panel: Control = _popup.get_node("PanelContainer")
		var scroll: Control = _popup.get_node("PanelContainer/VBoxContainer/PerCourtScroll")
		var geometry = {
			"viewport": [root.size.x, root.size.y],
			"panel_size": [panel.size.x, panel.size.y],
			"panel_offsets": [panel.offset_left, panel.offset_top,
					panel.offset_right, panel.offset_bottom],
			"per_court_min_y": scroll.custom_minimum_size.y,
			"per_court_actual_y": scroll.size.y,
		}
		var out = FileAccess.open("user://g1_geometry.json", FileAccess.WRITE)
		out.store_string(JSON.stringify(geometry, "  "))
		out.close()
		quit(0)

func _fail(msg: String) -> void:
	var out = FileAccess.open("user://g1_geometry.json", FileAccess.WRITE)
	out.store_string(JSON.stringify({"error": msg}))
	out.close()
	quit(1)
