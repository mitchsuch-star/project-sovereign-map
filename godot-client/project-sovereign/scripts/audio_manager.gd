extends Node
class_name AudioManager

# =============================================================================
# PROJECT SOVEREIGN — AudioManager (Music & Sound Core, wiring half)
# =============================================================================
# The game's audio engine, in the codebase's established singleton idiom
# (class_name statics, like Utils / UiSettings — NOT a project.godot autoload:
# the parse harness compiles scripts under a bare SceneTree where autoload
# globals never resolve, and this project's compile gate matters more than the
# autoload convenience). A lazy instance node self-installs under the scene
# root on first use; main.gd calls AudioManager.boot() once in _ready().
#
# Owns:
#   • the four runtime buses  Master / Music / SFX / UI  (created idempotently;
#     volumes persisted through UiSettings, sliders on the pause menu)
#   • the cue registry — every sourced file in assets/audio/ keyed by the
#     docs/MUSIC_SOUND_SPEC.md §2 cue map (variants round-robin; per-cue
#     trim + throttle so button spam or piece fleets never machine-gun)
#   • the music program — PEACE / WAR rotations with crossfade, a one-shot
#     overlay lane (La Marseillaise on a new war), ducking for the diorama,
#     and the reserved Victory-Pass tracks exposed via play_music_once()
#   • named ambient loops (scribble / wind / sea / crowd / march / bed)
#   • the global button hook: every BaseButton in every scene clicks through
#     one seam (node_added), CheckButton/CheckBox get the toggle sound, and
#     any button can opt out with  set_meta("no_click_sfx", true).
# Display-only (Golden Rule 6): nothing here reads or writes game state.
# =============================================================================

const AUDIO_ROOT := "res://assets/audio/"

# Cue registry: cue -> {files: [...], bus, db (trim), throttle_ms, max_s,
#                       start_s}
# `max_s` caps a one-shot that is LONGER THAN ITS MOMENT and fades it out over
# 0.8s (`_fade_stop`). Sourced CC0 assets are frequently whole ambiences rather
# than single hits — letter_open is 38.6s of paper, church_bells_peal is 77s —
# and a cue with no cap plays to the end of the file no matter how brief the
# interaction that fired it. Cap anything whose asset outlives its beat; leave
# it off when the file is already the right length.
const CUES := {
	# ── UI chrome ──
	# Aug 8, 2026 (user): the Interface-pack synth blips read as "laser" on the
	# screen-nav buttons — the war room clicks in wood and leather now. The old
	# click_primary/click_soft/select_item files stay on disk as pool variants
	# (MUSIC_SOUND_SPEC §2 cue table carries the swap).
	"click": {"files": ["ui/wood_tap_1.ogg", "ui/wood_tap_2.ogg", "ui/wood_tap_3.ogg"], "bus": "UI", "db": -8.0, "throttle_ms": 90},
	"toggle": {"files": ["ui/toggle_switch.ogg"], "bus": "UI", "db": -12.0, "throttle_ms": 90},
	"select": {"files": ["ui/leather_tap_1.ogg", "ui/leather_tap_2.ogg"], "bus": "UI", "db": -8.0, "throttle_ms": 120},
	"tick": {"files": ["ui/tick_subtle.ogg"], "bus": "UI", "db": -16.0, "throttle_ms": 90},
	"confirm": {"files": ["ui/confirm_chime.ogg"], "bus": "UI", "db": -8.0},
	"error": {"files": ["ui/error_soft.ogg"], "bus": "UI", "db": -8.0},
	"question": {"files": ["ui/question_open.ogg"], "bus": "UI", "db": -8.0},
	# Aug 8, 2026 (user, round 2): the panel/dismiss whooshes were the LAST
	# Interface-pack synths on the screen-nav path — opening the ledger still
	# read as "laser". The big screens now open and close as the books they
	# are, and a dismissal is a leather tap. Old files stay on disk as pool
	# variants (MUSIC_SOUND_SPEC §2 carries the swap).
	"panel_open": {"files": ["ui/book_open.ogg"], "bus": "UI", "db": -10.0, "throttle_ms": 200},
	"panel_close": {"files": ["ui/book_close.ogg"], "bus": "UI", "db": -10.0, "throttle_ms": 200},
	"back": {"files": ["ui/leather_tap_2.ogg"], "bus": "UI", "db": -10.0, "throttle_ms": 200},
	"page_turn": {"files": ["ui/page_turn_1.ogg", "ui/page_turn_2.ogg", "ui/page_turn_3.ogg"], "bus": "UI", "db": -8.0, "throttle_ms": 150},
	"book_open": {"files": ["ui/book_open.ogg"], "bus": "UI", "db": -8.0},
	"book_close": {"files": ["ui/book_close.ogg"], "bus": "UI", "db": -8.0},
	"parchment_open": {"files": ["ui/parchment_open_snd_use_map.wav"], "bus": "UI", "db": -10.0},
	"parchment_close": {"files": ["ui/parchment_close_snd_close_map.wav"], "bus": "UI", "db": -10.0},
	"door_open": {"files": ["ui/door_open_heavy.ogg"], "bus": "UI", "db": -10.0},
	"door_close": {"files": ["ui/door_close_heavy.ogg"], "bus": "UI", "db": -10.0},
	"latch": {"files": ["ui/latch_close.ogg"], "bus": "UI", "db": -10.0},
	"cloth": {"files": ["ui/cloth_rustle.ogg"], "bus": "UI", "db": -10.0, "throttle_ms": 200},
	# ── the desk: command flow, paper, seal ──
	"quill_flick": {"files": ["ui/quill_flick.mp3"], "bus": "UI", "db": -6.0},
	"quill_sign": {"files": ["ui/quill_sign.mp3"], "bus": "UI", "db": -6.0},
	"wax_seal": {"files": ["ui/wax_seal.mp3"], "bus": "UI", "db": -4.0},
	"command_ack": {"files": ["ui/command_ack_click.ogg"], "bus": "UI", "db": -12.0, "throttle_ms": 150},
	"letter_open": {"files": ["ui/letter_open.mp3"], "bus": "UI", "db": -8.0, "throttle_ms": 300, "max_s": 1.4, "start_s": 1.9},
	"paper_crumple": {"files": ["ui/paper_crumple.mp3"], "bus": "UI", "db": -6.0},
	"notification": {"files": ["ui/notification_bell.mp3"], "bus": "UI", "db": -10.0, "throttle_ms": 400},
	"coins_small": {"files": ["ui/coins_small.ogg", "ui/coins_small_2.ogg"], "bus": "UI", "db": -8.0},
	"coin_pour": {"files": ["ui/coin_pour.mp3"], "bus": "UI", "db": -6.0, "max_s": 3.0},
	"end_turn": {"files": ["ui/end_turn_drum_roll.mp3"], "bus": "UI", "db": -8.0},
	# ── battle ──
	"cannon": {"files": ["battle/cannon_thud.ogg"], "bus": "SFX", "db": -8.0},
	"cannon_distant": {"files": ["battle/cannon_distant.ogg"], "bus": "SFX", "db": -12.0, "throttle_ms": 300},
	"drum_sting": {"files": ["battle/drum_sting.wav"], "bus": "SFX", "db": -6.0},
	"musket_volley": {"files": ["battle/musket_battle_volley.mp3"], "bus": "SFX", "db": -10.0, "max_s": 4.2},
	"musket_shot": {"files": ["battle/musket_shot_1.ogg", "battle/musket_shot_2.ogg", "battle/musket_shot_3.ogg"], "bus": "SFX", "db": -12.0, "throttle_ms": 120},
	"cavalry": {"files": ["battle/cavalry_gallop.mp3"], "bus": "SFX", "db": -10.0, "max_s": 3.2, "start_s": 4.6},
	"whinny": {"files": ["battle/horse_whinny.ogg"], "bus": "SFX", "db": -14.0},
	"sword_draw": {"files": ["battle/sword_draw.mp3"], "bus": "SFX", "db": -8.0},
	"march_step": {"files": ["battle/army_march_loop_short.mp3"], "bus": "SFX", "db": -18.0, "throttle_ms": 1500, "max_s": 0.65},
	# ── world / ceremony ──
	"bells_peal": {"files": ["ambient/church_bells_peal.mp3"], "bus": "SFX", "db": -8.0, "max_s": 5.2},
	"bell_toll": {"files": ["ambient/bell_toll_single.mp3"], "bus": "SFX", "db": -8.0, "max_s": 3.2},
	"ship_bell": {"files": ["ambient/ship_bell.mp3"], "bus": "SFX", "db": -10.0, "throttle_ms": 400},
	# ── field music used as one-shot cues (capped where long) ──
	"reveille": {"files": ["music/bugle_reveille.ogg"], "bus": "SFX", "db": -14.0, "throttle_ms": 2000, "max_s": 4.2},
	"mail_call": {"files": ["music/bugle_mail_call.ogg"], "bus": "SFX", "db": -12.0, "throttle_ms": 2000},
	"first_call": {"files": ["music/bugle_first_call.mp3"], "bus": "SFX", "db": -14.0, "max_s": 4.2},
	"to_the_color": {"files": ["music/bugle_to_the_color.ogg"], "bus": "SFX", "db": -14.0, "max_s": 5.2},
	"fanfare": {"files": ["music/fanfare_erafnaf.ogg"], "bus": "SFX", "db": -10.0, "throttle_ms": 2000, "max_s": 5.2},
}

# Named ambient loops: tag -> {file, bus, db}
const LOOPS := {
	"scribble": {"file": "ui/quill_scribble_loop.ogg", "bus": "UI", "db": -16.0},
	"scribble_long": {"file": "ui/quill_scribble_long.ogg", "bus": "UI", "db": -18.0},
	"wind": {"file": "ambient/wind_map_loop.mp3", "bus": "SFX", "db": -26.0},
	"sea": {"file": "ambient/sea_loop.mp3", "bus": "SFX", "db": -16.0},
	"creak": {"file": "ambient/ship_creak_1.ogg", "bus": "SFX", "db": -18.0},
	"crowd": {"file": "ambient/crowd_murmur.mp3", "bus": "SFX", "db": -20.0},
	"march": {"file": "battle/army_march_loop_short.mp3", "bus": "SFX", "db": -16.0},
	"march_long": {"file": "battle/army_march.mp3", "bus": "SFX", "db": -16.0},
	"battle_bed": {"file": "battle/battlefield_ambience.mp3", "bus": "SFX", "db": -18.0},
	"campfire": {"file": "ambient/campfire_loop.mp3", "bus": "SFX", "db": -20.0},
}

# The music program (docs/MUSIC_SOUND_SPEC.md §2). Rotations crossfade on
# mood change and advance on track end. triumph/lament are RESERVED for the
# Victory Pass endings (positions 10-11) — reachable via play_music_once().
# "menu" is the Main Menu's slot (position 6): the §2 title theme, alone in
# its rotation so the refill-on-empty behaviour loops it with a crossfade.
const MUSIC := {
	"menu": ["music/theme_eroica_i.ogg"],
	"peace": ["music/theme_eroica_i.ogg", "music/calm_haydn_lark_adagio.ogg",
			"music/calm_mozart40_andante.ogg", "music/calm_goldberg_aria.mp3"],
	"war": ["music/tension_coriolan.ogg", "music/fife_drum_brandywine.ogg",
			"music/drums_rage_of_cornwallis.ogg", "music/fife_drum_field_medley.ogg",
			"music/fife_drum_warlike_medley.ogg", "music/marche_militaire_francaise.mp3"],
}
const MUSIC_ONESHOTS := {
	"marseillaise": "music/marseillaise_navy_band.ogg",
	"triumph": "music/triumph_eroica_iv_finale.ogg",
	"lament": "music/lament_eroica_ii_marcia_funebre.ogg",
}
const MUSIC_DB := -10.0        # base trim under the Music bus
const CROSSFADE_S := 2.0
const DUCK_DB := -14.0         # extra music attenuation while the diorama holds the stage
const MAX_ONESHOT_PLAYERS := 14

static var _instance: AudioManager = null

var _streams: Dictionary = {}          # path -> AudioStream (lazy cache)
var _rr: Dictionary = {}               # cue -> next round-robin index
var _last_played_ms: Dictionary = {}   # cue -> tick of last play (throttle)
var _loop_players: Dictionary = {}     # tag -> AudioStreamPlayer
# UX23-R1: cue -> [AudioStreamPlayer]. `_play_cue` kept NO handle on the
# one-shot it created, so nothing outside it could silence a cue early —
# and one-shots are children of this singleton, not of the scene, so they
# outlive `change_scene_to_file` as well as the panel that started them.
var _live_players: Dictionary = {}
var _oneshot_count: int = 0

var _music_a: AudioStreamPlayer
var _music_b: AudioStreamPlayer
var _music_active_is_a := true
var _music_mood := ""                  # "", "peace", "war"
var _music_queue: Array = []           # shuffled remainder of the mood's rotation
var _music_overlay: AudioStreamPlayer  # one-shot lane (anthem); rotation pauses under it
var _duck_depth := 0                   # diorama duck refcount


# ── the static face (the game calls these; all compile-safe, all null-safe) ──

static func boot() -> void:
	"""Called once from main._ready(): installs the instance, starts the
	quiet map bed; music mood follows the first live war data."""
	var inst := _inst()
	if inst == null:
		return
	inst._start_loop("wind")


static func play(cue: String, max_seconds: float = 0.0) -> AudioStreamPlayer:
	var inst := _inst()
	if inst != null:
		return inst._play_cue(cue, max_seconds)
	return null


static func start_loop(tag: String) -> void:
	var inst := _inst()
	if inst != null:
		inst._start_loop(tag)


static func stop_cue(cue: String) -> void:
	"""Silence any live one-shot of `cue`, fading over 150 ms.

	UX23-R1 — "closing a panel should silence the sound it started". The
	Aug-23 caps bounded how long a cue can outlive its panel (6 s worst case);
	this ends it at the moment of the close.

	The rule the wiring follows, which the routed row did not draw: **an
	arrival sound stops on close; a departure sound IS the close.** So the
	envoy's paper and the diorama's cannon stop, and
	`capture_choice_dialog`'s coins — played inside the Plunder handler, one
	line before `hide()`, as the sound of the decision — deliberately do not.
	`popup_base.close_popup` itself plays "back" ON close for the same reason.
	"""
	var inst := _inst()
	if inst != null:
		inst._stop_cue(cue)


static func stop_player(p: AudioStreamPlayer) -> void:
	"""Silence ONE live one-shot — the player `play()` handed back.

	Review round: `stop_cue(name)` is a global kill by cue name, so a closing
	panel silenced every live play of that name including other surfaces'.
	Measured shape: the tableau's close called `stop_cue("drum_sting")` and
	would have cut the strategic-interrupt popup's drum, still on screen.
	`_play_cue` has the handle in hand at the moment it registers it, so
	ownership can be real rather than nominal."""
	var inst := _inst()
	if inst != null and p != null and is_instance_valid(p) and p.playing:
		inst._fade_out_now(p, 0.15)


static func stop_all_cues() -> void:
	"""Silence every live one-shot. The sibling `stop_all_loops` has always
	existed because the players live under this singleton and a scene change
	does not free them; one-shots have exactly the same property and had no
	equivalent, so `dialog_manager.hide_all()` on a world swap left a 5-second
	peal ringing into the freshly loaded campaign."""
	var inst := _inst()
	if inst == null:
		return
	for cue in inst._live_players.keys().duplicate():
		inst._stop_cue(cue)


static func stop_loop(tag: String) -> void:
	var inst := _inst()
	if inst != null:
		inst._stop_loop(tag)


static func start_scribble() -> void:
	start_loop("scribble")


static func stop_scribble() -> void:
	stop_loop("scribble")


static func set_war_mood(at_war: bool) -> void:
	var inst := _inst()
	if inst != null:
		inst._set_mood("war" if at_war else "peace")


static func set_menu_mood() -> void:
	"""Main Menu (position 6): the title theme on the rotation lane. Entering
	the campaign flips the mood via set_war_mood on the first live war data —
	and the theme doubles as the peace rotation's opener, so the hand-off is
	musically continuous."""
	var inst := _inst()
	if inst != null:
		inst._set_mood("menu")


static func stop_all_loops() -> void:
	"""Scene-change hygiene (game ↔ menu): the loop players live under the
	persistent AudioManager node, so a scene change does NOT free them — the
	departing scene's beds (wind, march, battle, sea, scribble) must be
	stopped explicitly."""
	var inst := _inst()
	if inst == null:
		return
	for tag in inst._loop_players.keys().duplicate():
		inst._stop_loop(tag)


static func play_music_once(name_key: String) -> void:
	var inst := _inst()
	if inst != null:
		inst._play_music_once(name_key)


static func duck_music(on: bool) -> void:
	var inst := _inst()
	if inst != null:
		inst._duck_music(on)


static func set_bus_volume(bus_name: String, linear: float, persist: bool = true) -> void:
	var inst := _inst()
	if inst != null:
		inst._set_bus_volume(bus_name, linear, persist)


static func get_bus_volume(bus_name: String) -> float:
	return UiSettings.get_audio_volume(bus_name)


static func _inst() -> AudioManager:
	if _instance != null and is_instance_valid(_instance):
		return _instance
	var ml := Engine.get_main_loop()
	if ml == null or not (ml is SceneTree):
		return null  # headless harness / bare SceneTree: audio is a no-op
	var root := (ml as SceneTree).root
	if root == null:
		return null
	_instance = AudioManager.new()
	_instance.name = "AudioManagerNode"
	root.add_child(_instance)
	return _instance


# ── instance lifecycle ──────────────────────────────────────────────────────

func _ready() -> void:
	_ensure_buses()
	_apply_saved_volumes()
	_music_a = _make_player("Music")
	_music_b = _make_player("Music")
	_music_overlay = _make_player("Music")
	_music_a.finished.connect(_on_music_finished)
	_music_b.finished.connect(_on_music_finished)
	_music_overlay.finished.connect(_on_overlay_finished)
	# The global button hook — every current and future BaseButton.
	get_tree().node_added.connect(_on_node_added)
	_hook_existing(get_tree().root)


# ── buses & volumes ─────────────────────────────────────────────────────────

func _ensure_buses() -> void:
	for bus_name in ["Music", "SFX", "UI"]:
		if AudioServer.get_bus_index(bus_name) == -1:
			var idx := AudioServer.bus_count
			AudioServer.add_bus(idx)
			AudioServer.set_bus_name(idx, bus_name)
			AudioServer.set_bus_send(idx, "Master")


func _apply_saved_volumes() -> void:
	for bus_name in ["Master", "Music", "SFX", "UI"]:
		_set_bus_volume(bus_name, UiSettings.get_audio_volume(bus_name), false)


func _set_bus_volume(bus_name: String, linear: float, persist: bool) -> void:
	var idx := AudioServer.get_bus_index(bus_name)
	if idx == -1:
		return
	linear = clampf(linear, 0.0, 1.0)
	AudioServer.set_bus_volume_db(idx, linear_to_db(maxf(linear, 0.0001)))
	AudioServer.set_bus_mute(idx, linear <= 0.001)
	if persist:
		UiSettings.set_audio_volume(bus_name, linear)


# ── one-shot cues ───────────────────────────────────────────────────────────

func _play_cue(cue: String, max_seconds: float) -> AudioStreamPlayer:
	if not CUES.has(cue):
		push_warning("AudioManager: unknown cue '%s'" % cue)
		return null
	var spec: Dictionary = CUES[cue]
	var throttle := int(spec.get("throttle_ms", 0))
	if throttle > 0:
		var now := Time.get_ticks_msec()
		if _last_played_ms.has(cue) and now - int(_last_played_ms[cue]) < throttle:
			return null
	if _oneshot_count >= MAX_ONESHOT_PLAYERS:
		return null
	var files: Array = spec["files"]
	var i := int(_rr.get(cue, 0)) % files.size()
	var stream = _stream(String(files[i]))
	if stream == null:
		return null
	# Aug 23, 2026: the throttle stamp and the round-robin advance used to run
	# ABOVE the budget check and the missing-file check, so a play that never
	# happened still poisoned the window — a cue rejected for lack of a player
	# slot, or one whose file is absent, went silent for its whole throttle
	# period afterwards. Both are recorded only once the play is certain.
	_rr[cue] = i + 1
	if throttle > 0:
		_last_played_ms[cue] = Time.get_ticks_msec()
	var p := _make_player(String(spec["bus"]))
	p.stream = stream
	p.volume_db = float(spec.get("db", 0.0))
	_oneshot_count += 1
	p.finished.connect(func():
		_oneshot_count -= 1
		_forget_live(cue, p)
		p.queue_free())
	# UX23-1 follow-up, Aug 23 2026 — measured, not guessed. The Aug-23 caps
	# assumed the gesture sits at the head of the file. An envelope probe
	# through an AudioEffectCapture bus (tools/audio_envelope_probe.gd) says
	# otherwise for two of the eleven:
	#
	#   letter_open  cap 1.4 s, sound ONSET 2.05 s  -> the cap ended before the
	#                paper ever rustled. The fix "made" the reported cue silent.
	#   cavalry      cap 3.2 s, onset 4.9 s         -> a gallop that approaches;
	#                the capped window is the empty road, 30 dB down.
	#
	# Raising the caps would bring back the length the player complained about.
	# `start_s` skips the dead head instead, so the cue stays short AND is the
	# sound it is named for. The other nine measured onsets are all inside
	# their caps and carry no offset.
	_live_players.get_or_add(cue, []).append(p)
	var start_at := float(spec.get("start_s", 0.0))
	# An offset past the end of the file plays nothing at all — the very bug
	# `start_s` exists to fix, re-created through the new mechanism. Clamp with
	# a second of headroom so a mis-typed offset degrades to a short cue rather
	# than to silence (review round; the length census cannot see this field).
	var stream_len := 0.0
	if stream != null:
		stream_len = stream.get_length()
	if stream_len > 0.0 and start_at >= stream_len - 0.25:
		start_at = max(0.0, stream_len - 1.0)
	if start_at > 0.0:
		p.play(start_at)
	else:
		p.play()
	# Aug 23, 2026 (user: "the paper noise goes on for a really long time"):
	# a cue's cap now lives in the registry beside its file, not only in the
	# optional `max_seconds` argument. `_fade_stop` was NOT unreachable —
	# three call sites passed a cap (the diorama's volley, the reveille, the
	# reward fanfare) — but a cap a caller has to remember is a cap the other
	# 68 call sites did not have, so `letter_open` ran its full 38.6 SECONDS
	# every time an envoy was opened and the 300 ms throttle let a second
	# copy start over the first. The registry is the single source now; those
	# three sites dropped their arguments and their values moved here. The
	# argument still wins where it is passed, so a one-off ceremony can ask
	# for longer than its cue's own default.
	var cap := max_seconds if max_seconds > 0.0 else float(spec.get("max_s", 0.0))
	if cap > 0.0:
		_fade_stop(p, cap)
	return p


func _forget_live(cue: String, p: AudioStreamPlayer) -> void:
	var arr: Array = _live_players.get(cue, [])
	arr.erase(p)
	if arr.is_empty():
		_live_players.erase(cue)


func _stop_cue(cue: String) -> void:
	for p in _live_players.get(cue, []).duplicate():
		if is_instance_valid(p) and p.playing:
			_fade_out_now(p, 0.15)


func _fade_out_now(p: AudioStreamPlayer, secs: float) -> void:
	"""Fade a live one-shot to silence and retire it.

	`p.finished.emit()` is load-bearing and must not be replaced by a bare
	`queue_free`: the `finished` lambda in `_play_cue` is the ONLY thing that
	decrements `_oneshot_count` and drops the live-registry entry. A stop path
	that skips it leaks the MAX_ONESHOT_PLAYERS budget permanently, and the
	game goes quiet after fourteen cues — a worse bug than the one being
	fixed."""
	# Idempotent, and it has to be. Two fade paths can now reach the same
	# player: the `max_s` timer and a `stop_cue` from a closing panel. Without
	# this latch both build a tween, both callbacks pass `is_instance_valid`,
	# and `finished` fires TWICE — so the `_play_cue` lambda runs twice and
	# `_oneshot_count` is decremented twice for one player, quietly corrupting
	# the budget that exists to stop the game running out of voices. (Before
	# `stop_cue` existed only one path could fade, so the callback never
	# needed a second guard; the review round for this slice is what found it.)
	if p.has_meta("_retiring"):
		return
	p.set_meta("_retiring", true)
	var tw := create_tween()
	tw.tween_property(p, "volume_db", -50.0, secs)
	tw.tween_callback(func():
		if is_instance_valid(p) and p.playing:
			p.stop()
			p.finished.emit())


func _fade_stop(p: AudioStreamPlayer, after_s: float) -> void:
	var t := get_tree().create_timer(after_s)
	t.timeout.connect(func():
		if is_instance_valid(p) and p.playing:
			_fade_out_now(p, 0.8))


# ── named ambient loops ─────────────────────────────────────────────────────

func _start_loop(tag: String) -> void:
	if _loop_players.has(tag) or not LOOPS.has(tag):
		return
	var spec: Dictionary = LOOPS[tag]
	var stream = _stream(String(spec["file"]), true)
	if stream == null:
		return
	var p := _make_player(String(spec["bus"]))
	p.stream = stream
	p.volume_db = float(spec.get("db", -16.0))
	_loop_players[tag] = p
	p.play()


func _stop_loop(tag: String) -> void:
	if not _loop_players.has(tag):
		return
	var p: AudioStreamPlayer = _loop_players[tag]
	_loop_players.erase(tag)
	if is_instance_valid(p):
		var tw := create_tween()
		tw.tween_property(p, "volume_db", -50.0, 0.35)
		tw.tween_callback(p.queue_free)


# ── music ───────────────────────────────────────────────────────────────────

func _set_mood(mood: String) -> void:
	if mood == _music_mood or not MUSIC.has(mood):
		return
	_music_mood = mood
	_music_queue = (MUSIC[mood] as Array).duplicate()
	_music_queue.shuffle()
	# Null-safe: a static call can land before _ready has built the players
	# (the lazy install races scene setup — the call sites defer, this guards).
	if _music_overlay != null and _music_overlay.playing:
		return  # the overlay finishing will pull from the new mood's queue
	if _music_a != null:
		_play_next_music_track()


func _play_music_once(name_key: String) -> void:
	# The one-shot lane (anthem now; triumph/lament when the Victory Pass ends
	# a campaign). The rotation fades under it and resumes after.
	if not MUSIC_ONESHOTS.has(name_key):
		return
	var stream = _stream(String(MUSIC_ONESHOTS[name_key]))
	if stream == null:
		return
	var active := _active_music_player()
	if active.playing:
		var tw := create_tween()
		tw.tween_property(active, "volume_db", -50.0, 1.0)
		tw.tween_callback(active.stop)
	_music_overlay.stream = stream
	_music_overlay.volume_db = MUSIC_DB
	_music_overlay.play()


func _on_overlay_finished() -> void:
	_play_next_music_track()


func _active_music_player() -> AudioStreamPlayer:
	return _music_a if _music_active_is_a else _music_b


func _play_next_music_track() -> void:
	if _music_mood == "":
		return
	if _music_queue.is_empty():
		_music_queue = (MUSIC[_music_mood] as Array).duplicate()
		_music_queue.shuffle()
	var stream = _stream(String(_music_queue.pop_front()))
	if stream == null:
		return
	var from := _active_music_player()
	_music_active_is_a = not _music_active_is_a
	var to := _active_music_player()
	to.stream = stream
	to.volume_db = -50.0
	to.play()
	var duck := DUCK_DB if _duck_depth > 0 else 0.0
	var tw := create_tween()
	tw.set_parallel(true)
	tw.tween_property(to, "volume_db", MUSIC_DB + duck, CROSSFADE_S)
	if from.playing:
		tw.tween_property(from, "volume_db", -50.0, CROSSFADE_S)
		tw.chain().tween_callback(from.stop)


func _on_music_finished() -> void:
	if not _music_overlay.playing:
		_play_next_music_track()


# The diorama (and any full-stage moment) ducks the music under it.
func _duck_music(on: bool) -> void:
	_duck_depth = maxi(0, _duck_depth + (1 if on else -1))
	var target := MUSIC_DB + (DUCK_DB if _duck_depth > 0 else 0.0)
	for p in [_active_music_player(), _music_overlay]:
		if p.playing:
			var tw := create_tween()
			tw.tween_property(p, "volume_db", target, 0.5)


# ── the global button hook ──────────────────────────────────────────────────

func _on_node_added(node: Node) -> void:
	_hook_button(node)


func _hook_existing(node: Node) -> void:
	_hook_button(node)
	for child in node.get_children():
		_hook_existing(child)


func _hook_button(node: Node) -> void:
	if node is BaseButton and not node.has_meta("_audio_hooked"):
		node.set_meta("_audio_hooked", true)
		node.pressed.connect(_on_any_button_pressed.bind(node))


func _on_any_button_pressed(btn: Node) -> void:
	if not is_instance_valid(btn) or btn.has_meta("no_click_sfx"):
		return
	if btn is CheckButton or btn is CheckBox:
		_play_cue("toggle", 0.0)
	else:
		_play_cue("click", 0.0)


# ── internals ───────────────────────────────────────────────────────────────

func _make_player(bus_name: String) -> AudioStreamPlayer:
	var p := AudioStreamPlayer.new()
	p.bus = bus_name if AudioServer.get_bus_index(bus_name) != -1 else "Master"
	add_child(p)
	return p


func _stream(rel_path: String, want_loop: bool = false):
	var key := rel_path + ("#loop" if want_loop else "")
	if _streams.has(key):
		return _streams[key]
	var full := AUDIO_ROOT + rel_path
	if not ResourceLoader.exists(full):
		push_warning("AudioManager: missing audio file " + full)
		return null
	var stream = load(full)
	if want_loop and stream != null:
		# OGG and MP3 streams expose a runtime loop flag; WAV loops are set at
		# import time. Duplicate so the non-loop cache entry stays clean.
		stream = stream.duplicate()
		if "loop" in stream:
			stream.loop = true
	_streams[key] = stream
	return stream
