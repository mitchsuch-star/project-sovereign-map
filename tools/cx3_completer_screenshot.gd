extends SceneTree
# CX-3 — the completion row, on screen, at BOTH Interface Scales.
#
#   <godot> --path godot-client/project-sovereign \
#           --script ../../tools/cx3_completer_screenshot.gd
#
# Instantiates the REAL main.tscn — not a mock of the terminal — installs a
# deterministic `_last_game_state` and a history, types into the real
# `command_input`, and captures the row at `content_scale_factor` 1.0 and 2.0.
# The 2.0 pass is the one that matters: IQ-10's two P3s were both a surface
# authored at a fixed size that did not fit the client's own maximum scale,
# and this row draws inside the terminal's VBox precisely so it cannot be a
# third. PNGs land in user://; the runner copies them under docs/audits/.
#
# The board is a STUB, not a live backend: the completer's only source is the
# `/command` response's own `game_state`, so handing it that dict is handing
# it exactly what it reads in play.

const SHOTS := [
	["ney", "ne"],                    # the addressee slot
	["verbs", "Ney, "],               # the verb slot
	["enemy", "Ney, attack "],        # the target slot, enemy roster
	["region", "Ney, march to S"],    # the target slot, province roster
	["history", "st"],                # a past command, recalled by prefix
]

var _frames := 0
var _main = null
var _shot := 0
var _scale := 1.0
var _pass := 0

const STATE := {
	"marshals": {
		"Ney": {"location": "Rhineland", "strength": 24000, "morale": 100},
		"Davout": {"location": "Rhineland", "strength": 26000, "morale": 100},
		"Soult": {"location": "Lorraine", "strength": 30000, "morale": 100},
		"Murat": {"location": "Franche-Comte", "strength": 22000, "morale": 100},
	},
	"enemies": {
		"Mack": {"location": "Swabia", "strength": "unknown", "nation": "Austria"},
		"ArchdukeJohn": {"location": "Tyrol", "strength": "unknown", "nation": "Austria"},
	},
	"map_data": {
		"Swabia": {"controller": "Bavaria"},
		"Saxony": {"controller": "Saxony"},
		"Savoy": {"controller": "France"},
		"Lorraine": {"controller": "France"},
		"Rhineland": {"controller": "France"},
	},
}


func _init():
	process_frame.connect(_tick)


func _tick():
	_frames += 1
	if _frames == 1:
		root.mode = Window.MODE_WINDOWED
		root.size = Vector2i(1600, 900)
		root.position = Vector2i(2565, 20)
		return
	if _frames == 3:
		_main = load("res://scenes/main.tscn").instantiate()
		root.add_child(_main)
		return
	if _frames == 60:
		_main._last_game_state = STATE
		_main.command_history = ["status", "Ney, fortify", "start the drill"]
		_apply_scale()
		return
	if _frames > 60 and (_frames - 60) % 24 == 0:
		_step()


func _apply_scale():
	root.content_scale_factor = _scale


func _step():
	if _shot >= SHOTS.size():
		if _pass == 0:
			_pass = 1
			_scale = 2.0
			_shot = 0
			_apply_scale()
			return
		quit(0)
		return
	var entry = SHOTS[_shot]
	_main.command_input.text = str(entry[1])
	_main.command_input.caret_column = _main.command_input.text.length()
	_main._refresh_suggestions()
	await process_frame
	await process_frame
	var suffix := "" if _pass == 0 else "_X2"
	var path := "user://cx3_completer_%s%s.png" % [str(entry[0]), suffix]
	root.get_texture().get_image().save_png(path)
	print("[cx3] shot %s -> %s (suggestions: %d)" % [
		str(entry[0]), path, _main._suggestions.size()])
	_shot += 1
