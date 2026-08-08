extends SceneTree
# POSITION 7 evidence harness (windowed, NOT --headless), the committed-
# siblings pattern (main_menu_screenshot.gd / settlement_popup_screenshot.gd):
#   <godot> --path godot-client/project-sovereign --script ../../tools/tutorial_screenshot.gd
# Requires the LIVE backend on 8005. Two modes via TUT_SHOT_MODE env:
#   "tutorial"  (default) — capture the menu (School of War button), then a
#                real main.tscn boot with MenuBoot.pending_action="tutorial":
#                the connection test consumes it, /new_game {"scenario":
#                "tutorial"} round-trips, the world swaps and the School of
#                War card ARMS from game_state.scenario_name — the whole
#                production path, live. Shots: user://tut_shot_menu.png +
#                user://tut_shot_card.png.
#   "admiralty" — plain-entry main.tscn against whatever world the backend
#                holds (flip it to the 1805 campaign first), open the
#                Strategic Ledger and switch to the NEW tab 7. Shot:
#                user://tut_shot_admiralty.png.

var _frames := 0
var _menu = null
var _main = null
var _mode := "tutorial"

func _init():
	var env_mode := OS.get_environment("TUT_SHOT_MODE")
	if env_mode != "":
		_mode = env_mode
	process_frame.connect(_tick)

func _tick():
	_frames += 1
	if _frames == 1:
		root.mode = Window.MODE_WINDOWED
		root.size = Vector2i(2550, 1340)
		root.position = Vector2i(100, 60)
		return
	if _mode == "tutorial":
		_tick_tutorial()
	else:
		_tick_admiralty()

func _tick_tutorial():
	if _frames == 3:
		var scene = load("res://scenes/main_menu.tscn")
		_menu = scene.instantiate()
		root.add_child(_menu)
		return
	if _frames == 180:
		root.get_texture().get_image().save_png("user://tut_shot_menu.png")
		return
	if _frames == 190:
		_menu.queue_free()
		MenuBoot.pending_action = "tutorial"
		MenuBoot.came_from_game = false
		return
	if _frames == 200:
		var scene = load("res://scenes/main.tscn")
		_main = scene.instantiate()
		root.add_child(_main)
		return
	if _frames == 700:
		root.get_texture().get_image().save_png("user://tut_shot_card.png")
		return
	if _frames == 710:
		quit(0)

func _tick_admiralty():
	if _frames == 3:
		MenuBoot.pending_action = ""
		var scene = load("res://scenes/main.tscn")
		_main = scene.instantiate()
		root.add_child(_main)
		return
	if _frames == 420:
		if _main and _main.top_bar:
			_main.top_bar.toggle_screen("ledger")
		return
	if _frames == 560:
		var ledger = _main.top_bar.screens.get("ledger") if _main and _main.top_bar else null
		if ledger and ledger.has_method("_switch_tab"):
			ledger._switch_tab(6)
		return
	if _frames == 640:
		root.get_texture().get_image().save_png("user://tut_shot_admiralty.png")
		return
	if _frames == 650:
		quit(0)
