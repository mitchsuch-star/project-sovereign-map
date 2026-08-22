extends SceneTree
# Row WO visual-sign-off evidence harness (windowed, NOT --headless).
#
#   SOVEREIGN_PORT=8006 <godot> --path godot-client/project-sovereign \
#       --script ../../tools/wo_signoff_screenshot.gd
#
# Captures the THREE surfaces row WO owed a sign-off on, in the REAL
# `main.tscn` against a REAL backend, one PNG each into user://:
#
#   wo_signoff_1_cabinet_redirect.png  — slice 7: Berthier's redirect line
#                                        and its ⚜ Cabinet link, produced by
#                                        typing a diplomatic order into the
#                                        terminal (nothing is sent).
#   wo_signoff_2_wizard_from_link.png  — slice 7: the wizard opened through
#                                        the link itself (`cabinet:open`),
#                                        i.e. the same door F1 uses.
#   wo_signoff_3_load_capture.png      — slice 15: a restored plunder/secure
#                                        question raised by the world-swap
#                                        handler, which is what `/load`
#                                        returns to.
#
# Deliberately drives the client's OWN entry points — `_execute_command`,
# `_on_output_meta_clicked`, `_apply_world_swap_response` — rather than
# rebuilding their effects, so the evidence is of the shipped path and not
# of this script. Run the backend on 8006 first so the player's own 8005
# session is untouched (golden rule 7).

const SHOTS := "user://"

var _frames := 0
var _main = null
var _step := 0
var _log: Array = []


func _init():
	process_frame.connect(_tick)


func _note(msg: String) -> void:
	_log.append(msg)
	print("[WO-SIGNOFF] " + msg)


func _shot(name: String) -> void:
	var img: Image = root.get_texture().get_image()
	var path := SHOTS + name
	var err := img.save_png(path)
	_note("saved %s (err=%d) viewport=%dx%d" % [path, err, root.size.x, root.size.y])


func _capture_payload() -> Dictionary:
	# The exact two keys `/load` now attaches (WO-30), plus the priced
	# stage-1 shape `build_capture_choice` mints.
	return {
		"success": true,
		# `load_game` returns "Loaded: <save_name>"; the client's own
		# `_on_load_result` supplies "Game loaded successfully." as the
		# success_text. Two DIFFERENT lines — use the real shapes so the
		# evidence does not look like a double print.
		"message": "Loaded: Quicksave",
		"pending_capture_choice": true,
		"capture_data": {
			"region": "Swabia",
			"capturer": "Ney",
			"previous_controller": "Austria",
			"plunder_gold": 600,
			"dialogue_id": 9,
		},
	}


func _tick():
	_frames += 1

	if _frames == 1:
		root.mode = Window.MODE_WINDOWED
		root.size = Vector2i(1600, 900)
		return

	if _frames == 3:
		var scene = load("res://scenes/main.tscn")
		if scene == null:
			_note("FAIL: main.tscn did not load")
			quit(1)
			return
		_main = scene.instantiate()
		root.add_child(_main)
		_note("main.tscn instantiated; backend = " + Utils.backend_url())
		return

	# Give the client time to connect, hydrate the HUD and draw the map.
	if _frames == 150 and _step == 0:
		_step = 1
		# ── Surface 1: the Cabinet redirect ────────────────────────────
		# `_execute_command` is the ONE terminal-typed path (the G1 redirect
		# lands there and nowhere else), so this is the player's own route.
		# `_execute_command()` reads the input field — type into it exactly
		# as the player does, then press it.
		_main.command_input.text = "propose alliance with Austria"
		_main._execute_command()
		_note("typed a diplomatic order into the terminal")
		return

	if _frames == 175 and _step == 1:
		_step = 2
		_shot("wo_signoff_1_cabinet_redirect.png")
		return

	if _frames == 185 and _step == 2:
		_step = 3
		# ── Surface 2: the wizard, opened THROUGH the link ─────────────
		_main._on_output_meta_clicked("cabinet:open")
		_note("clicked the ⚜ cabinet:open link")
		return

	if _frames == 230 and _step == 3:
		_step = 4
		_shot("wo_signoff_2_wizard_from_link.png")
		# Close it again so the next surface is not drawn behind a modal.
		if _main.diplomacy_wizard != null:
			_main.diplomacy_wizard.hide()
		return

	if _frames == 245 and _step == 4:
		_step = 5
		# ── Surface 3: the restored capture question ───────────────────
		# `_apply_world_swap_response` is exactly what `/load` returns to.
		_main._apply_world_swap_response(_capture_payload(),
			"Game loaded successfully.")
		_note("fed the world-swap handler a /load response carrying a "
			+ "restored capture question")
		return

	if _frames == 290 and _step == 5:
		_step = 6
		_shot("wo_signoff_3_load_capture.png")
		var f = FileAccess.open(SHOTS + "wo_signoff_log.txt", FileAccess.WRITE)
		if f:
			f.store_string("\n".join(_log) + "\n")
			f.close()
		_note("done")
		quit(0)
		return

	if _frames > 400:
		_note("FAIL: timed out at step %d" % _step)
		quit(1)
