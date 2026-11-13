# Session UI-5 (November 12, 2026) — the full measure's headless probe.
#
#   Godot_v4.4.1-stable_win64.exe --headless --path godot-client/project-sovereign --script ../../tools/ui5_probe.gd
#
# Driven by tests/test_ui5_full_measure.py::TestDriven (the engine_panels
# lane). Prints "[UI5] PASS" or "[UI5] FAIL: <checks>" and exits 0 / 1. Every
# setting it touches stays in memory (UiSettings._persist = false — the
# harness flag): the player's own settings file is never written.
extends SceneTree

var _fails: Array = []
var _notes: Array = []


func _check(ok: bool, name: String) -> void:
	if ok:
		_notes.append("ok " + name)
	else:
		_fails.append(name)


func _initialize() -> void:
	UiSettings._persist = false
	_run.call_deferred()


func _wait(seconds: float) -> void:
	await create_timer(seconds).timeout


func _run() -> void:
	# ── A1: the buses and their effects ──
	AudioManager.boot()
	await process_frame
	await process_frame
	for bus_name in ["Music", "SFX", "UI", "Ambience", "Ceremony"]:
		_check(AudioServer.get_bus_index(bus_name) != -1, "bus " + bus_name)
	var ceremony := AudioServer.get_bus_index("Ceremony")
	_check(ceremony != -1 and AudioServer.get_bus_send(ceremony) == &"SFX", "Ceremony sends to SFX")
	var music := AudioServer.get_bus_index("Music")
	var ducks := false
	for i in AudioServer.get_bus_effect_count(music):
		var e := AudioServer.get_bus_effect(music, i)
		if e is AudioEffectCompressor and (e as AudioEffectCompressor).sidechain == &"Ceremony":
			ducks = true
	_check(ducks, "the music ducks under a ceremony")
	var master := AudioServer.get_bus_index("Master")
	var limited := false
	for i in AudioServer.get_bus_effect_count(master):
		if AudioServer.get_bus_effect(master, i) is AudioEffectHardLimiter:
			limited = true
	_check(limited, "the master is limited")

	var inst = AudioManager._inst()
	_check(inst != null, "the manager installs")

	# ── the window in the background ──
	UiSettings.set_background_audio("quiet")
	var before := AudioServer.get_bus_volume_db(master)
	inst._notification(Node.NOTIFICATION_APPLICATION_FOCUS_OUT)
	await _wait(0.6)
	var quiet := AudioServer.get_bus_volume_db(master)
	_check(absf((before - quiet) - 12.0) < 0.6, "the background is 12 dB quieter (%.1f -> %.1f)" % [before, quiet])
	inst._notification(Node.NOTIFICATION_APPLICATION_FOCUS_IN)
	await _wait(0.6)
	_check(absf(AudioServer.get_bus_volume_db(master) - before) < 0.6, "the foreground comes back")

	# ── the study restarts after a swap ──
	AudioManager.start_ambience()
	await process_frame
	_check(inst._loop_players.has("wind") and inst._loop_players.has("fire") and inst._loop_players.has("clock"), "the study's beds")
	AudioManager.stop_all_loops()
	await process_frame
	_check(not inst._loop_players.has("fire"), "the swap silences the beds")
	AudioManager.start_ambience()
	await process_frame
	_check(inst._loop_players.has("fire"), "the beds come back after the swap")
	AudioManager.set_calendar_label("January 1806")
	await process_frame
	_check(inst._loop_players.has("winter_wind") and not inst._loop_players.has("rain"), "winter's layer")
	AudioManager.set_calendar_label("September 1806")
	await process_frame
	_check(inst._loop_players.has("rain") and not inst._loop_players.has("winter_wind"), "autumn's layer")

	# ── two quills ──
	AudioManager.start_scribble()
	AudioManager.start_loop("scribble_verdict")
	AudioManager.stop_loop("scribble_verdict")
	await process_frame
	_check(inst._loop_players.has("scribble"), "closing the verdict leaves the command's quill")
	AudioManager.stop_scribble()

	# ── the orders and the notices are heard ──
	AudioManager.play_result("attack")
	_check(inst._live_players.has("bugle_to_arms"), "an attack sounds To Arms")
	AudioManager.hint_notification_priority(2)
	AudioManager.play("notification")
	_check(inst._live_players.has("notification_critical"), "a critical notice sounds Assembly")

	# ── the anthem rule ──
	AudioManager.announce_war("Austria", false)
	await process_frame
	_check(String(inst._overlay_key) == "anthem:Austria", "attacked by Austria: the Kaiserhymne (%s)" % inst._overlay_key)
	inst._skip_track()
	AudioManager.announce_war("Russia", false)
	await process_frame
	_check(String(inst._overlay_key) == "marseillaise", "no period anthem: La Marseillaise answers")
	inst._skip_track()

	# ── the Music Room ──
	var room: Array = AudioManager.music_room_tracks()
	_check(room.size() >= 20, "the Music Room lists the pieces (%d)" % room.size())

	# ── Help & Keys ──
	var codex := CodexView.new()
	root.add_child(codex)
	await process_frame
	codex.open("keys")
	await process_frame
	_check(codex.is_open(), "Help & Keys opens")
	_check(String(codex._label.text).find("Strategic Ledger") >= 0, "Help & Keys lists the bindings")
	codex.close()

	# ── the busy chip ──
	var chip := BusyChip.new()
	root.add_child(chip)
	chip.show_busy("enemy")
	_check(chip.visible and chip.kind() == "enemy", "the courier rides")
	chip.hide_busy()
	await _wait(0.35)
	_check(not chip.visible, "the chip folds after its moment")

	# ── toasts ──
	for i in 4:
		ToastLayer.say("probe toast %d" % i)
	await process_frame
	await process_frame
	var layer = ToastLayer._inst()
	_check(layer != null and layer._column.get_child_count() <= 3, "three toasts at most")

	# ── the save rows ──
	var meta := {"save_name": "Ulm", "turn": 7, "calendar_label": "October 1805", "player_nation": "France"}
	_check(SaveDialog.date_of(meta) == "October 1805", "a save's date")
	_check(SaveDialog.date_of({"turn": 7}) == "Turn 7", "a save without a calendar")

	# ── a rebinding round-trips ──
	Keys.reset_all()
	var swapped := Keys.rebind("ledger", KEY_G)
	_check(swapped == "generals" and Keys.key_for("generals") == KEY_T, "a clash swaps")
	var press := InputEventKey.new()
	press.keycode = KEY_G
	press.pressed = true
	_check((Keys.canonical(press) as InputEventKey).keycode == KEY_T, "the ledger's new key reads as its default")
	_check(Keys.rebind("ledger", KEY_ESCAPE) == "reserved", "Esc stays Esc")
	Keys.reset_all()
	_check(Keys.key_for("ledger") == KEY_T, "Restore defaults")

	# ── colour vision ──
	UiSettings.set_colour_vision("red_green")
	Utils.apply_colour_vision()
	var green := Color("8fbc8f")
	var toned := Utils.cv(green)
	_check(Utils.COLOR_SUCCESS != "8fbc8f", "the green token re-tones")
	_check(toned.h > 0.5 and toned.h < 0.65, "green reads blue (hue %.2f)" % toned.h)
	_check(toned.get_luminance() + 0.003 >= green.get_luminance(), "never darker than the green")
	UiSettings.set_colour_vision("standard")
	Utils.apply_colour_vision()
	_check(Utils.COLOR_SUCCESS == "8fbc8f", "standard restores")

	# ── every letter and surface has its picture ──
	var blank: Array = []
	for template in Illustrations.LETTER_BY_TEMPLATE.keys():
		var p := Illustrations.for_letter({"moment_id": template})
		if p == "" or not ResourceLoader.exists(p):
			blank.append(template)
	for surface in Illustrations.SURFACES.keys():
		if Illustrations.for_surface(surface) == "":
			blank.append(surface)
	for court in Illustrations.WAR_BY_COURT.keys():
		if Illustrations.for_surface("war:" + court) == "":
			blank.append("war:" + court)
	for style in Illustrations.END_BY_STYLE.keys():
		if Illustrations.for_surface("campaign_end:" + style, "plate") == "":
			blank.append("campaign_end:" + style)
	_check(blank.is_empty(), "every letter and surface has a picture %s" % [blank])

	if _fails.is_empty():
		print("[UI5] PASS (%d checks)" % _notes.size())
		quit(0)
	else:
		print("[UI5] FAIL: ", _fails)
		for n in _notes:
			print("  ", n)
		quit(1)
