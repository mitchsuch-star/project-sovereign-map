extends SceneTree
# UX23-R9 audition renderer — offline dev tool, NOT in CI.
#
#   <godot> --path godot-client/project-sovereign \
#           --script ../../tools/ux23_r9_audition_render.gd
#
# WHY THIS EXISTS. `tools/audio_envelope_probe.gd` answered the *silence* half
# of the capped-cue question by measurement: every capped cue is present and
# loud inside its window. The half it explicitly cannot answer is whether a
# capped MUSICAL cue ends on a phrase or is cut mid-figure — that needs a
# person and a pair of speakers (row UX23-R9, `docs/BUG_FIXES.md` §UX23-B).
#
# So this renders the three bugle/fanfare cues EXACTLY as the game plays them
# — the registry's `start_s` offset, its `db` trim, its `max_s` cap and the
# 0.8s fade `_fade_stop` applies at the cap — into .wav files a human can
# double-click. Plus one combined file with a second of silence between, so
# the whole audition is a single action.
#
# HONESTY GUARD, inherited from the probe: if Godot falls back to its dummy
# audio driver every buffer reads as silence and the renderer would happily
# write three silent files. The run FAILS LOUDLY unless real energy arrives.

const OUT_DIR := "user://ux23_r9/"
const BUS_NAME := "AuditionRender"
const FADE_S := 0.8               # `_fade_stop`'s fade, mirrored
const GAP_S := 1.0                # silence between cues in the combined file
const FULL_MAX_S := 45.0          # wall clock for the uncapped renders

# (cue, path, db, max_s, start_s) — mirrored from audio_manager.gd's CUES.
# A literal on purpose, exactly as in the probe: this is an instrument, and it
# must be possible to point it at a window whose registry entry is wrong.
const TARGETS := [
	["reveille", "res://assets/audio/music/bugle_reveille.ogg", -14.0, 4.2, 0.0],
	["to_the_color", "res://assets/audio/music/bugle_to_the_color.ogg", -14.0, 5.2, 0.0],
	["fanfare", "res://assets/audio/music/fanfare_erafnaf.ogg", -10.0, 5.2, 0.0],
]

var _idx := -1
var _player: AudioStreamPlayer = null
var _capture: AudioEffectCapture = null
var _frames: PackedVector2Array = PackedVector2Array()
var _all: PackedVector2Array = PackedVector2Array()
var _elapsed := 0.0
var _mix_rate := 44100.0
var _bus_idx := -1
var _device_ok := false
var _log: Array = []
# UX23_R9_FULL=1 renders each cue WHOLE and untrimmed instead, so the
# envelope around the cap can be measured from a plain PCM file. It cannot
# answer the phrase question - only a person can - but it can say whether
# the cap falls in a note or in the gap between two.
var _full := false


func _init():
	_full = OS.get_environment("UX23_R9_FULL") == "1"
	process_frame.connect(_tick)
	_mix_rate = AudioServer.get_mix_rate()
	_bus_idx = AudioServer.bus_count
	AudioServer.add_bus(_bus_idx)
	AudioServer.set_bus_name(_bus_idx, BUS_NAME)
	AudioServer.set_bus_mute(_bus_idx, true)
	_capture = AudioEffectCapture.new()
	_capture.buffer_length = 4.0
	AudioServer.add_bus_effect(_bus_idx, _capture)


func _note(msg: String) -> void:
	_log.append(msg)
	print("[UX23-R9] " + msg)


func _next():
	if _player != null:
		_write_one()
	_idx += 1
	if _idx >= TARGETS.size():
		_write_combined()
		return
	var path: String = TARGETS[_idx][1]
	var stream = load(path)
	if stream == null:
		_note("FAIL: could not load " + path)
		quit(1)
		return
	_frames = PackedVector2Array()
	_elapsed = 0.0
	_capture.clear_buffer()
	_player = AudioStreamPlayer.new()
	_player.stream = stream
	_player.bus = BUS_NAME
	_player.volume_db = 0.0 if _full else float(TARGETS[_idx][2])
	root.add_child(_player)
	_player.play(float(TARGETS[_idx][4]))
	# The cap's own fade, reproduced: `_fade_stop` starts a 0.8s tween to
	# -50 dB AFTER `max_s`, so what the player hears is max_s + 0.8s with the
	# tail fading. Rendering only the first max_s would answer a question
	# nobody asked.
	if _full:
		return
	var cap: float = float(TARGETS[_idx][3])
	var target := _player
	var timer := get_root().get_tree().create_timer(cap)
	timer.timeout.connect(func():
		if is_instance_valid(target) and target.playing:
			var tween := create_tween()
			tween.tween_property(target, "volume_db", -50.0, FADE_S)
			tween.tween_callback(func():
				if is_instance_valid(target):
					target.stop()))


func _tick():
	if _idx == -1:
		_next()
		return
	if _player == null:
		return
	_elapsed += 1.0 / 60.0
	var available := _capture.get_frames_available()
	if available > 0:
		var buffer := _capture.get_buffer(available)
		for frame in buffer:
			_frames.append(frame)
			if absf(frame.x) > 0.01 or absf(frame.y) > 0.01:
				_device_ok = true
	var cap: float = FULL_MAX_S if _full else float(TARGETS[_idx][3])
	if not _player.playing or _elapsed > cap + FADE_S + 1.0:
		_next()


func _write_one():
	var cue: String = TARGETS[_idx][0]
	var cap: float = float(TARGETS[_idx][3])
	var name := ("%s_FULL.wav" % cue) if _full else ("%s_capped_%.1fs.wav" % [cue, cap])
	_save_wav(OUT_DIR + name, _frames)
	_note("%s -> %s (%d frames, %.2fs)"
		% [cue, name, _frames.size(), _frames.size() / _mix_rate])
	for frame in _frames:
		_all.append(frame)
	var silence := int(_mix_rate * GAP_S)
	for i in range(silence):
		_all.append(Vector2.ZERO)
	if is_instance_valid(_player):
		_player.stop()
		_player.queue_free()
	_player = null


func _write_combined():
	if not _device_ok:
		_note("FAIL: no audio device produced energy — every file would be "
			+ "silent, and a silent audition answers nothing. Run windowed "
			+ "with a real output device.")
		quit(1)
		return
	if _full:
		quit(0)
		return
	_save_wav(OUT_DIR + "ux23_r9_all_three.wav", _all)
	_note("combined -> ux23_r9_all_three.wav (%.2fs)"
		% (_all.size() / _mix_rate))
	var f = FileAccess.open(OUT_DIR + "README.txt", FileAccess.WRITE)
	if f:
		f.store_string("\n".join(_log) + "\n")
		f.close()
	quit(0)


func _save_wav(path: String, frames: PackedVector2Array) -> void:
	DirAccess.make_dir_recursive_absolute(OUT_DIR)
	var pcm := PackedByteArray()
	pcm.resize(frames.size() * 4)          # 16-bit stereo
	var offset := 0
	for frame in frames:
		var left := int(clampf(frame.x, -1.0, 1.0) * 32767.0)
		var right := int(clampf(frame.y, -1.0, 1.0) * 32767.0)
		pcm.encode_s16(offset, left)
		pcm.encode_s16(offset + 2, right)
		offset += 4
	var out := FileAccess.open(path, FileAccess.WRITE)
	if out == null:
		_note("FAIL: could not open " + path)
		return
	var rate := int(_mix_rate)
	out.store_buffer("RIFF".to_ascii_buffer())
	out.store_32(36 + pcm.size())
	out.store_buffer("WAVEfmt ".to_ascii_buffer())
	out.store_32(16)                       # PCM header size
	out.store_16(1)                        # format = PCM
	out.store_16(2)                        # channels
	out.store_32(rate)
	out.store_32(rate * 4)                 # byte rate
	out.store_16(4)                        # block align
	out.store_16(16)                       # bits per sample
	out.store_buffer("data".to_ascii_buffer())
	out.store_32(pcm.size())
	out.store_buffer(pcm)
	out.close()
