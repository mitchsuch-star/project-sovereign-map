extends SceneTree
# UX23-A visual-signoff harness (windowed, NOT --headless — the viewport has to
# render for get_texture() to return pixels):
#
#   <godot> --path godot-client/project-sovereign \
#           --script ../../tools/ux23a_rail_screenshot.gd
#
# Instantiates the REAL notification_bar.tscn, feeds it REAL reward-rail rows
# captured from a backend (res://ux23a_rows.json — a JSON array in the exact
# shape `GET /notifications` returns), then opens each row's detail panel and
# saves a screenshot plus the measured geometry to user://.
#
# The payload file is NOT committed. Capture one against a SANDBOXED backend
# (never the player's 8005):
#   SOVEREIGN_PORT=8006 INK_IRON_SAVE_DIR=<tmp> python -m backend.main &
#   curl -s http://127.0.0.1:8006/notifications \
#     | python -c "import sys,json; json.dump(json.load(sys.stdin)['notifications'],sys.stdout)" \
#     > godot-client/project-sovereign/ux23a_rows.json
# and delete it after the run (it lives inside res:// only so this script can
# read it without a permission dance).
#
# Answers the two questions the UX23-A landing record left open: does the rail
# icon carry a findable glyph, and does the full-width action button render as
# the primary affordance above [Reward…]/[Keep]/[Acknowledge]?

const SHOT_RAIL := "user://ux23a_rail.png"
const SHOT_PANEL := "user://ux23a_panel.png"
const GEOMETRY := "user://ux23a_geometry.json"

var _frames := 0
var _bar = null
var _rows: Array = []
var _geometry := {}


func _init():
	process_frame.connect(_tick)


func _tick():
	_frames += 1
	if _frames == 1:
		root.mode = Window.MODE_WINDOWED
		root.size = Vector2i(1400, 620)
		return
	if _frames == 3:
		_load_rows()
		return
	if _frames == 20:
		_shoot_rail()
		return
	if _frames == 22:
		_open_reward_row()
		return
	if _frames == 40:
		_shoot_panel()
		return


func _load_rows():
	var f = FileAccess.open("res://ux23a_rows.json", FileAccess.READ)
	if f == null:
		_fail("ux23a_rows.json missing — capture it first (see header)")
		return
	var parsed = JSON.parse_string(f.get_as_text())
	f.close()
	if not (parsed is Array):
		_fail("payload is not an array of notifications")
		return
	_rows = parsed

	var scene = load("res://scenes/notification_bar.tscn")
	_bar = scene.instantiate()
	root.add_child(_bar)
	# The rail anchors to the top-right of its parent; give it a real rect so
	# the screenshot is not a 0x0 control.
	_bar.set_anchors_preset(Control.PRESET_TOP_WIDE)
	_bar.position = Vector2(0, 12)
	_bar.size = Vector2(1400, 60)
	_bar.update_notifications(_rows)


func _shoot_rail():
	root.get_texture().get_image().save_png(SHOT_RAIL)
	var icons: Node = _bar.get_node("RailPanel/RailLayout/IconContainer")
	var pills := []
	for child in icons.get_children():
		pills.append({
			"text": child.text,
			"has_icon": child.icon != null,
			"tooltip": child.tooltip_text,
			"size": [child.size.x, child.size.y],
		})
	_geometry["rail"] = {
		"row_count": _rows.size(),
		"visible_pills": pills,
	}


func _open_reward_row():
	# Open the FIRST reward row the rail is showing — the one this slice put a
	# button on.
	var icons: Node = _bar.get_node("RailPanel/RailLayout/IconContainer")
	var target: Button = null
	for child in icons.get_children():
		var notif = child.get_meta("notification_data", {})
		var t: String = str(notif.get("type", "")) if notif is Dictionary else ""
		if t.begins_with("dotation_"):
			target = child
			break
	if target == null and icons.get_child_count() > 0:
		target = icons.get_child(0)
	if target == null:
		_fail("no rail pills rendered")
		return
	target.emit_signal("pressed")


func _shoot_panel():
	root.get_texture().get_image().save_png(SHOT_PANEL)
	var panel = _bar.expanded_panel
	if panel == null:
		_fail("detail panel did not open")
		return
	var vbox: Node = panel.get_child(0)
	var children := []
	for child in vbox.get_children():
		children.append({
			"class": child.get_class(),
			"text": (child.text if ("text" in child) else ""),
			"size": [child.size.x, child.size.y],
			"font_size": (child.get_theme_font_size("font_size")
					if child is Button or child is Label else 0),
		})
	_geometry["panel"] = {
		"panel_size": [panel.size.x, panel.size.y],
		"panel_position": [panel.position.x, panel.position.y],
		"children_in_order": children,
	}
	var out = FileAccess.open(GEOMETRY, FileAccess.WRITE)
	out.store_string(JSON.stringify(_geometry, "  "))
	out.close()
	quit(0)


func _fail(msg: String) -> void:
	var out = FileAccess.open(GEOMETRY, FileAccess.WRITE)
	out.store_string(JSON.stringify({"error": msg}, "  "))
	out.close()
	push_error("[ux23a_rail_screenshot] " + msg)
	quit(1)
