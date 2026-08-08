extends SceneTree
# Main Menu pass (position 6) evidence harness (windowed, NOT --headless):
#   <godot> --path godot-client/project-sovereign --script ../../tools/main_menu_screenshot.gd
# Instantiates the real main_menu.tscn, lets the entrance animation and first
# slide settle, captures the menu, then opens the Settings view and captures
# again. Screenshots land in user:// (menu_shot_main.png / menu_shot_settings.png).
# Throwaway per the July-31 visual-capture loop — delete after use (+ .uid).

var _frames := 0
var _menu = null

func _init():
	process_frame.connect(_tick)

func _tick():
	_frames += 1
	if _frames == 1:
		root.mode = Window.MODE_WINDOWED
		root.size = Vector2i(2550, 1340)
		root.position = Vector2i(100, 60)
		return
	if _frames == 3:
		var scene = load("res://scenes/main_menu.tscn")
		_menu = scene.instantiate()
		root.add_child(_menu)
		return
	if _frames == 170:
		root.get_texture().get_image().save_png("user://menu_shot_main.png")
		return
	if _frames == 175:
		_menu._open_settings()
		return
	if _frames == 215:
		root.get_texture().get_image().save_png("user://menu_shot_settings.png")
		return
	if _frames == 225:
		quit(0)
