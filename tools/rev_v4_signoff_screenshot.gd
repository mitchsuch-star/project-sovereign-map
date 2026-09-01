extends SceneTree
# REV-V4 visual sign-off harness (windowed, NOT --headless).
#
#   REV_V4_FLOW=1 SOVEREIGN_PORT=8007 <godot> \
#       --path godot-client/project-sovereign \
#       --script ../../tools/rev_v4_signoff_screenshot.gd
#
# The Aug 30, 2026 review landed two ORDERING fixes on the end-turn tail and
# neither had ever been seen by a human — both are pinned only by source-text
# greps over `main.gd`. This drives the REAL `main.tscn` against a REAL
# backend whose world has been staged into the exact state each fix needs,
# and shoots the result.
#
#   FLOW 1  a fresh capture question no longer swallows the end-turn report.
#           Staged: Ney holds fortified Bohemia, occupation completing.
#           `advance_turn` mounts the question INSIDE the end-turn response,
#           so it is stashed (`pending_capture_response`) and raised when
#           control returns, after the report and the Morning Dispatch.
#             rev_v4_flow1_1_enemy_phase.png
#             rev_v4_flow1_2_capture_after_report.png
#             rev_v4_flow1_terminal.txt   the scrollback UNDER the modal
#
#   FLOW 2  the Morning Dispatch shows on the interrupt tail.
#           Staged: Soult (literal) under a standing march whose destination
#           Mack holds — `destination_blocked`, requires_input. That route
#           early-returns out of BOTH dismissal handlers ahead of their own
#           `_show_pending_dispatch()`, so the briefing used to be stashed
#           and never shown.
#             rev_v4_flow2_1_strategic_report.png
#             rev_v4_flow2_2_interrupt.png
#             rev_v4_flow2_3_dispatch_after_interrupt.png
#             rev_v4_flow2_terminal.txt
#
# Every step goes through the client's OWN entry points — `_execute_command`,
# the dialogs' real button handlers — so the evidence is of the shipped path.
# The world is staged over HTTP beforehand; this script only plays the turn.
#
# Note the lapse confirm: UX23's typed `end turn` refuses once while envoys
# are unanswered and asks the player to repeat the order. The harness repeats
# it only when the enemy-phase dialog has NOT appeared, so on a turn with no
# waiting envoys nothing extra is sent.

const SHOTS := "user://"

var _frames := 0
var _main = null
var _step := 0
var _log: Array = []
var _flow := 1


func _init():
	_flow = 2 if OS.get_environment("REV_V4_FLOW") == "2" else 1
	process_frame.connect(_tick)


func _note(msg: String) -> void:
	_log.append(msg)
	print("[REV-V4] " + msg)


func _shot(name: String) -> void:
	var img: Image = root.get_texture().get_image()
	var path := SHOTS + name
	var err := img.save_png(path)
	_note("saved %s (err=%d) viewport=%dx%d" % [path, err, root.size.x, root.size.y])


func _dump_terminal(name: String) -> void:
	var body := ""
	if _main.output_display != null:
		body = _main.output_display.get_parsed_text()
	var f = FileAccess.open(SHOTS + name, FileAccess.WRITE)
	if f:
		f.store_string(body)
		f.close()
	_note("terminal scrollback -> %s (%d chars)" % [name, body.length()])


func _visible(node) -> bool:
	return node != null and node.visible


func _finish() -> void:
	var f = FileAccess.open(SHOTS + "rev_v4_log_%d.txt" % _flow, FileAccess.WRITE)
	if f:
		f.store_string("\n".join(_log) + "\n")
		f.close()
	_note("done")
	quit(0)


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
		_note("main.tscn instantiated; backend = %s; flow = %d"
			% [Utils.backend_url(), _flow])
		return

	# Let the client connect, hydrate the HUD and draw the map.
	if _frames == 160 and _step == 0:
		_step = 1
		_main.command_input.text = "end turn"
		_main._execute_command()
		_note("typed 'end turn' into the terminal")
		return

	# UX23's envoy-lapse gate: the first order is a warning, not an end turn.
	if _frames == 240 and _step == 1:
		_step = 2
		if not _visible(_main.enemy_phase_dialog):
			_main.command_input.text = "end turn"
			_main._execute_command()
			_note("the lapse warning stood — repeated 'end turn' to confirm")
		else:
			_note("no lapse warning; the turn ended on the first order")
		return

	if _flow == 1:
		_tick_flow_1()
	else:
		_tick_flow_2()

	if _frames > 1200:
		_note("FAIL: timed out at step %d" % _step)
		quit(1)


func _tick_flow_1():
	if _frames == 330 and _step == 2:
		_step = 3
		_note("enemy-phase dialog visible: %s" % _visible(_main.enemy_phase_dialog))
		_shot("rev_v4_flow1_1_enemy_phase.png")
		return

	if _frames == 350 and _step == 3:
		_step = 4
		# The dialog's own Continue button handler — the player's route.
		if _visible(_main.enemy_phase_dialog):
			_main.enemy_phase_dialog._on_continue_pressed()
			_note("pressed Continue on the enemy-phase dialog")
		else:
			_note("WARN: enemy-phase dialog was not visible")
		return

	if _frames == 430 and _step == 4:
		_step = 5
		_note("capture question raised after the report: %s"
			% _visible(_main.capture_choice_dialog))
		_shot("rev_v4_flow1_2_capture_after_report.png")
		# The modal covers most of the terminal, so the PNG alone cannot show
		# that the report is INTACT underneath it. Dump the scrollback while
		# the question stands: that is the ordering evidence a screenshot
		# cannot give. (Answering is a fresh command whose result TRIMS the
		# scrollback, so a shot taken afterwards would show an empty log and
		# prove nothing either way.)
		_dump_terminal("rev_v4_flow1_terminal.txt")
		_finish()
		return


func _tick_flow_2():
	if _frames == 330 and _step == 2:
		_step = 3
		if _visible(_main.enemy_phase_dialog):
			_main.enemy_phase_dialog._on_continue_pressed()
			_note("pressed Continue on the enemy-phase dialog")
		else:
			_note("WARN: enemy-phase dialog was not visible")
		return

	if _frames == 380 and _step == 3:
		_step = 4
		_note("strategic report popup visible: %s"
			% _visible(_main.strategic_report_popup))
		_shot("rev_v4_flow2_1_strategic_report.png")
		return

	if _frames == 400 and _step == 4:
		_step = 5
		if _visible(_main.strategic_report_popup):
			_main.strategic_report_popup._on_continue_pressed()
			_note("pressed Continue on the strategic report popup")
		else:
			_note("WARN: strategic report popup was not visible")
		return

	if _frames == 460 and _step == 5:
		_step = 6
		_note("interrupt popup visible: %s" % _visible(_main.interrupt_popup))
		_shot("rev_v4_flow2_2_interrupt.png")
		return

	if _frames == 480 and _step == 6:
		_step = 7
		if _visible(_main.interrupt_popup):
			_main.interrupt_popup._on_option_pressed("hold_position")
			_note("answered the interrupt: hold_position")
		else:
			_note("WARN: interrupt popup was not visible")
		return

	if _frames == 620 and _step == 7:
		_step = 8
		_shot("rev_v4_flow2_3_dispatch_after_interrupt.png")
		_dump_terminal("rev_v4_flow2_terminal.txt")
		_finish()
		return
