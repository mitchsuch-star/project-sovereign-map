extends SceneTree
# UX23-1 audio-audition substitute — offline dev tool, NOT in CI.
#
#   <godot> --path godot-client/project-sovereign \
#           --script ../../tools/audio_envelope_probe.gd
#
# WHY THIS EXISTS. `MUSIC_SOUND_SPEC.md` §0.6 records that nobody has ever
# LISTENED to the cue files — durations are verified, ears are not. The Aug-23
# UX23-1 fix capped eleven over-long one-shots with a `max_s` registry field,
# and its own acceptance note names the risk plainly: *"a 1.4 s cap assumes
# the gesture is in the first 1.4 s. If the head is a fade-in or room tone the
# capped cue is worse than the bug."*
#
# I cannot listen. But that question is measurable from the waveform, and the
# venv has no mp3/ogg decoder (no soundfile, no pydub, no ffmpeg) — while
# GODOT decodes both natively. So: route each cue through a bus carrying an
# `AudioEffectCapture`, play it, and read the PCM back frame by frame.
#
# HONESTY GUARD. If Godot falls back to its dummy audio driver there is no
# device, every buffer reads as silence, and the probe would cheerfully report
# that every cue is a fade-in. The run therefore FAILS LOUDLY unless at least
# one file returns real energy (`device_ok`), and the report says which files
# were truncated by the per-file wall clock rather than pretending it saw
# the whole thing.
#
# Output: user://audio_envelope.json
#   {device_ok, files: [{path, capped_at, seconds_seen, truncated,
#                        peak_pos_frac, rms_in_cap, rms_after_cap,
#                        head_200ms_rms, verdict}]}

const OUT := "user://audio_envelope.json"
const WINDOW_S := 0.05          # 50 ms envelope resolution
const MAX_SECONDS_PER_FILE := 20.0   # wall clock; longer files are truncated
const BUS_NAME := "EnvelopeProbe"

# (cue, path, max_s) — mirrors the `max_s` rows of audio_manager.gd's CUES.
# Kept as a literal on purpose: this is a measuring instrument, and it must be
# possible to point it at a file whose registry entry is WRONG.
const TARGETS := [
	["letter_open", "res://assets/audio/ui/letter_open.mp3", 1.4],
	["coin_pour", "res://assets/audio/ui/coin_pour.mp3", 3.0],
	["musket_volley", "res://assets/audio/battle/musket_battle_volley.mp3", 4.2],
	["cavalry", "res://assets/audio/battle/cavalry_gallop.mp3", 3.2],
	["march_step", "res://assets/audio/battle/army_march_loop_short.mp3", 0.65],
	["bells_peal", "res://assets/audio/ambient/church_bells_peal.mp3", 5.2],
	["bell_toll", "res://assets/audio/ambient/bell_toll_single.mp3", 3.2],
	["reveille", "res://assets/audio/music/bugle_reveille.ogg", 4.2],
	["first_call", "res://assets/audio/music/bugle_first_call.mp3", 4.2],
	["to_the_color", "res://assets/audio/music/bugle_to_the_color.ogg", 5.2],
	["fanfare", "res://assets/audio/music/fanfare_erafnaf.ogg", 5.2],
]

var _idx := -1
var _player: AudioStreamPlayer = null
var _capture: AudioEffectCapture = null
var _windows: Array = []          # rms per WINDOW_S
var _pending := PackedFloat32Array()
var _elapsed := 0.0
var _results: Array = []
var _device_ok := false
var _bus_idx := -1
var _mix_rate := 44100.0


func _init():
	process_frame.connect(_tick)
	_mix_rate = AudioServer.get_mix_rate()
	_bus_idx = AudioServer.bus_count
	AudioServer.add_bus(_bus_idx)
	AudioServer.set_bus_name(_bus_idx, BUS_NAME)
	# Silent to the speakers — this is a measurement, not a performance.
	AudioServer.set_bus_mute(_bus_idx, true)
	_capture = AudioEffectCapture.new()
	_capture.buffer_length = 2.0
	AudioServer.add_bus_effect(_bus_idx, _capture)
	# NOT here: `root` is not usable from _init(), so the first player was
	# added outside the tree and Godot refused to play it — which silently cost
	# the measurement of letter_open, the one file the user actually reported.
	# Start on the first frame instead.


func _next():
	if _player != null:
		_finish_current()
	_idx += 1
	if _idx >= TARGETS.size():
		_write()
		return
	var path: String = TARGETS[_idx][1]
	var stream = load(path)
	if stream == null:
		_results.append({"cue": TARGETS[_idx][0], "path": path,
				"error": "could not load"})
		call_deferred("_next")
		return
	_windows = []
	_pending = PackedFloat32Array()
	_elapsed = 0.0
	_capture.clear_buffer()
	_player = AudioStreamPlayer.new()
	_player.stream = stream
	_player.bus = BUS_NAME
	_player.volume_db = 0.0          # measure the FILE, not the trim
	root.add_child(_player)
	_player.play()


func _tick():
	if _idx == -1:
		_next()
		return
	if _player == null:
		return
	var delta := 1.0 / 60.0
	_elapsed += delta
	var available := _capture.get_frames_available()
	if available > 0:
		var frames := _capture.get_buffer(available)
		for f in frames:
			# mono-sum the stereo frame
			_pending.append((f.x + f.y) * 0.5)
		while _pending.size() >= int(_mix_rate * WINDOW_S):
			var n := int(_mix_rate * WINDOW_S)
			var acc := 0.0
			for i in range(n):
				acc += _pending[i] * _pending[i]
			_windows.append(sqrt(acc / float(n)))
			_pending = _pending.slice(n)
	if not _player.playing or _elapsed >= MAX_SECONDS_PER_FILE:
		_next()


func _finish_current():
	var cue: String = TARGETS[_idx][0]
	var path: String = TARGETS[_idx][1]
	var cap: float = TARGETS[_idx][2]
	var length := 0.0
	if _player.stream != null:
		length = _player.stream.get_length()
	var seen: float = min(_elapsed, MAX_SECONDS_PER_FILE)
	var truncated := length > MAX_SECONDS_PER_FILE + 0.5

	var row := {
		"cue": cue, "path": path, "capped_at": cap,
		"stream_length": snapped(length, 0.001),
		"seconds_seen": snapped(seen, 0.01),
		"truncated": truncated,
		"windows": _windows.size(),
	}
	if _windows.is_empty():
		row["error"] = "no frames captured"
	else:
		var peak := 0.0
		var peak_i := 0
		for i in range(_windows.size()):
			if _windows[i] > peak:
				peak = _windows[i]
				peak_i = i
		if peak > 0.0005:
			_device_ok = true
		var cap_windows := int(cap / WINDOW_S)
		row["peak_rms"] = snapped(peak, 0.00001)
		row["peak_at_s"] = snapped(peak_i * WINDOW_S, 0.01)
		row["peak_pos_frac"] = snapped(
			float(peak_i) / float(max(1, _windows.size() - 1)), 0.001)
		row["rms_in_cap"] = snapped(_mean(_windows, 0, cap_windows), 0.00001)
		row["rms_after_cap"] = snapped(
			_mean(_windows, cap_windows, _windows.size()), 0.00001)
		row["head_200ms_rms"] = snapped(_mean(_windows, 0, 4), 0.00001)
		row["peak_inside_cap"] = peak_i < cap_windows
		# Where the sound actually STARTS: the first window at a quarter of
		# peak energy. A head of room tone or a slow fade shows up here as an
		# onset later than the cap, which is the whole question UX23-1 left
		# open — and it is what a `start_s` offset would have to skip.
		var onset_i := -1
		for i in range(_windows.size()):
			if _windows[i] >= peak * 0.25:
				onset_i = i
				break
		row["onset_s"] = snapped(onset_i * WINDOW_S, 0.01) if onset_i >= 0 else -1.0
		row["onset_after_cap"] = onset_i >= 0 and onset_i >= cap_windows
	_results.append(row)
	_player.stop()
	root.remove_child(_player)
	_player.queue_free()
	_player = null


func _mean(arr: Array, from_i: int, to_i: int) -> float:
	var a: int = max(0, from_i)
	var b: int = min(arr.size(), to_i)
	if b <= a:
		return 0.0
	var acc := 0.0
	for i in range(a, b):
		acc += arr[i]
	return acc / float(b - a)


func _write():
	var out = FileAccess.open(OUT, FileAccess.WRITE)
	out.store_string(JSON.stringify({
		"device_ok": _device_ok,
		"mix_rate": _mix_rate,
		"window_s": WINDOW_S,
		"max_seconds_per_file": MAX_SECONDS_PER_FILE,
		"note": ("device_ok=false means Godot gave us a dummy audio driver and "
				+ "EVERY reading below is silence - the run proves nothing."),
		"files": _results,
	}, "  "))
	out.close()
	if _bus_idx >= 0:
		AudioServer.remove_bus(_bus_idx)
	quit(0 if _device_ok else 1)
