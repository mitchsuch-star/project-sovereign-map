extends RefCounted
class_name UiSettings

# =============================================================================
# PROJECT SOVEREIGN — UI Settings persistence (UI-2 / DEF-13 fold)
# =============================================================================
# Single source of truth for the user-adjustable display preferences added in
# the UI Visual Foundation Sweep, Session U2 (+ U2c: Global Text Size):
#   • the command window's footprint (drag-resize grip)   → terminal/width,height
#   • the global interface / text scale                   → display/ui_scale
#     — driven by BOTH the pause-menu "Interface Scale" slider AND the command
#       window's "Text Size" +/- buttons (they share this one value, so a bump
#       from either surface scales the terminal, every ledger, AND every pop-up;
#       the map is kept crisp by the renderer's native-resolution compensation).
#
# U2c retired the old *terminal-only* text scale (`terminal/scale`, the former
# A− / A+): it multiplied font-size overrides inside the command window alone and
# never reached the CanvasLayer pop-ups the player actually asked to enlarge.
# The one global `display/ui_scale` (`content_scale_factor`) supersedes it and
# scales the whole GUI uniformly, so there is now a single text-size source.
#
# Backed by a ConfigFile at `user://ui_settings.cfg`. Every setter writes
# through immediately (the file is a handful of scalars). Values are clamped to
# their published ranges on read AND write, so a hand-edited or corrupt config
# can never push the UI into an unusable geometry.
#
# Display-only (Golden Rule 6): nothing here touches game state or serialization.
# =============================================================================

const PATH := "user://ui_settings.cfg"

# --- Command-window footprint (logical px; drag-resize grip) ---
const DEFAULT_TERMINAL_WIDTH := 400.0
const DEFAULT_TERMINAL_HEIGHT := 270.0
const MIN_TERMINAL_WIDTH := 300.0
const MAX_TERMINAL_WIDTH := 1000.0
const MIN_TERMINAL_HEIGHT := 180.0
const MAX_TERMINAL_HEIGHT := 900.0

# --- Global interface / text scale (content_scale_factor) ---
# Driven by the pause-menu slider (fine 0.05 steps) AND the command-window
# "Text Size" +/- buttons (coarser BUTTON_STEP so one click is a visible jump).
# UXR-1 (October 9, 2026): the DEFAULT is no longer a number — it is DERIVED
# from the screen the game boots on (`derive_default_ui_scale`), and the cap
# rose 2.0 → 3.0 for 4K-and-up panels. DEFAULT_UI_SCALE stays as the floor the
# derivation can never go under and the value a headless run (no screen) gets.
const DEFAULT_UI_SCALE := 1.0
const MIN_UI_SCALE := 0.75
const MAX_UI_SCALE := 3.0
const UI_SCALE_STEP := 0.05
const UI_SCALE_BUTTON_STEP := 0.1
# The derivation's own terms (the Python twin lives in
# tools/uxr0_readability_report.py `derive_ui_scale`; a test pins the two on
# a table — change both or neither):
#   d = dpi / 96                 the Windows scaling the player chose
#   h = height / 1080            1.0 at 1080p, 1.33 at 1440p, 2.0 at 2160p
#   s = max(d, (d + h) / 2)      never below the player's own scaling
#   +0.25 when width/height ≥ 3.0 (a 32:9 panel is sat further from; a 21:9
#   at 2.39 is a 27-inch's distance and gets no bonus)
#   clamp [1.0, 3.0], rounded to 0.05
const DERIVE_FLOOR := 1.0
const ULTRA_WIDE_ASPECT := 3.0
const ULTRA_WIDE_BONUS := 0.25

static var _cfg: ConfigFile = null
# UXR-0 (October 9, 2026): the capture harnesses shim `_cfg` onto an in-memory
# ConfigFile so the player's stored settings are never READ — but every setter
# still `save()`d that in-memory file over the player's real one, which is why
# no harness could ever call a setter, and why a scene that writes a setting
# in its own `_ready` (the auto-derived scale, the first-run card) could not be
# shot. `_persist = false` keeps every write in memory. Set ONLY by harnesses.
static var _persist := true


static func _config() -> ConfigFile:
	if _cfg == null:
		_cfg = ConfigFile.new()
		# A missing/unreadable file leaves an empty ConfigFile → pure defaults.
		_cfg.load(PATH)
	return _cfg


static func _save() -> void:
	if _persist:
		_config().save(PATH)


static func _read_num(section: String, key: String, default: float) -> float:
	return float(_config().get_value(section, key, default))


static func _write_num(section: String, key: String, value: float) -> void:
	_config().set_value(section, key, value)
	_save()


# --- Terminal footprint ---
static func get_terminal_width() -> float:
	return clampf(_read_num("terminal", "width", DEFAULT_TERMINAL_WIDTH),
			MIN_TERMINAL_WIDTH, MAX_TERMINAL_WIDTH)


static func get_terminal_height() -> float:
	return clampf(_read_num("terminal", "height", DEFAULT_TERMINAL_HEIGHT),
			MIN_TERMINAL_HEIGHT, MAX_TERMINAL_HEIGHT)


static func set_terminal_size(width: float, height: float) -> void:
	_write_num("terminal", "width", clampf(width, MIN_TERMINAL_WIDTH, MAX_TERMINAL_WIDTH))
	_write_num("terminal", "height", clampf(height, MIN_TERMINAL_HEIGHT, MAX_TERMINAL_HEIGHT))


# --- Global interface / text scale ---
static func get_ui_scale() -> float:
	# No stored value → the screen's own derived scale (never the flat 1.0 a
	# 24-inch monitor wanted), so every road into the game agrees with the
	# menu that boots first. A stored value, auto or chosen, is read as is.
	if not _config().has_section_key("display", "ui_scale"):
		return derive_default_ui_scale()
	return clampf(_read_num("display", "ui_scale", DEFAULT_UI_SCALE),
			MIN_UI_SCALE, MAX_UI_SCALE)


static func set_ui_scale(scale: float) -> void:
	# A scale the player CHOSE — the slider, the +/- buttons, the first-run
	# card's "Looks right" — is never overwritten by a later derivation.
	_config().set_value("display", "ui_scale", clampf(scale, MIN_UI_SCALE, MAX_UI_SCALE))
	_config().set_value("display", "ui_scale_auto", false)
	_save()


static func is_ui_scale_auto() -> bool:
	"""True while the stored scale is the derivation's (or none is stored):
	a monitor change re-derives it; a chosen scale stays."""
	if not _config().has_section_key("display", "ui_scale"):
		return true
	return bool(_config().get_value("display", "ui_scale_auto", false))


static func resolve_ui_scale_at_boot() -> float:
	"""The main menu's boot call: derive the scale for THIS screen when none
	is stored or the stored one was auto, write it tagged auto, and return
	what the game should draw at. A chosen scale is returned untouched."""
	if is_ui_scale_auto():
		var derived := derive_default_ui_scale()
		_config().set_value("display", "ui_scale", derived)
		_config().set_value("display", "ui_scale_auto", true)
		_save()
		return derived
	return get_ui_scale()


static func set_ui_scale_auto() -> void:
	"""Reset layout / 'size for this screen': back to the derivation."""
	_config().set_value("display", "ui_scale", derive_default_ui_scale())
	_config().set_value("display", "ui_scale_auto", true)
	_save()


static func derive_default_ui_scale() -> float:
	"""The Interface Scale a player at this screen would have (the terms are
	documented at the constants). Reads the window's screen; a headless run
	(no screen, size 0) gets DEFAULT_UI_SCALE."""
	var screen := DisplayServer.window_get_current_screen()
	var size := DisplayServer.screen_get_size(screen)
	var dpi := float(DisplayServer.screen_get_dpi(screen))
	return derive_ui_scale_for(size.x, size.y, dpi)


static func derive_ui_scale_for(width: int, height: int, dpi: float) -> float:
	if width <= 0 or height <= 0:
		return DEFAULT_UI_SCALE
	var d := maxf(dpi, 1.0) / 96.0
	var h := float(height) / 1080.0
	var s := maxf(d, (d + h) / 2.0)
	if float(width) / float(height) >= ULTRA_WIDE_ASPECT:
		s += ULTRA_WIDE_BONUS
	s = clampf(s, DERIVE_FLOOR, MAX_UI_SCALE)
	return snappedf(s, UI_SCALE_STEP)


# --- The first-run sizing card's latch (UXR-1) ---
static func get_scale_acknowledged() -> bool:
	return bool(_config().get_value("display", "scale_acknowledged", false))


static func set_scale_acknowledged(done: bool) -> void:
	_config().set_value("display", "scale_acknowledged", done)
	_save()


# --- Battle sound effects (BD: the diorama's cannon thud + drum sting) ---
# The game's first audio — one boolean, honoured by every diorama sound call.
static func get_battle_sfx() -> bool:
	return bool(_config().get_value("audio", "battle_sfx", true))


static func set_battle_sfx(enabled: bool) -> void:
	_config().set_value("audio", "battle_sfx", enabled)
	_save()


# --- POSITION 7: the School of War completion/skip latch ---
# Per-machine is ACCEPTED for "don't re-open the tutor": the in-campaign step
# is DERIVED from game_state.turn, never stored here.
static func get_tutorial_done() -> bool:
	return bool(_config().get_value("tutorial", "done", false))


static func set_tutorial_done(done: bool) -> void:
	_config().set_value("tutorial", "done", done)
	_save()


# --- C1 (the release build): the once-ever keyless Smarter Parsing hint ---
# Per-machine, like the School's latch: Berthier's line is said on the first
# keyless campaign start and never again (reactive-but-discoverable, never a
# nag; the line itself lives in main.gd `_maybe_print_parser_hint`).
static func get_parser_hint_seen() -> bool:
	return bool(_config().get_value("parser", "hint_seen", false))


static func set_parser_hint_seen(seen: bool) -> void:
	_config().set_value("parser", "hint_seen", seen)
	_save()


# --- Bus volumes (Music & Sound Core: Master / Music / SFX / UI) ---
# Linear 0..1, applied by AudioManager (linear→dB); pause-menu sliders write here.
const AUDIO_VOLUME_DEFAULTS := {
	"Master": 1.0,
	"Music": 0.55,
	"SFX": 0.9,
	"UI": 0.65,
}


static func get_audio_volume(bus_name: String) -> float:
	var default := float(AUDIO_VOLUME_DEFAULTS.get(bus_name, 1.0))
	return clampf(_read_num("audio", "volume_" + bus_name.to_lower(), default), 0.0, 1.0)


static func set_audio_volume(bus_name: String, linear: float) -> void:
	_write_num("audio", "volume_" + bus_name.to_lower(), clampf(linear, 0.0, 1.0))


# --- The parser key (BYOK — Main Menu pass, position 6) ---
# The Anthropic API key the player enters in Settings. Plaintext in the local
# user:// config — the same trust level as the developer .env; it never leaves
# this machine except to the player's OWN backend at 127.0.0.1:8005.
static func get_api_key() -> String:
	return str(_config().get_value("llm", "api_key", ""))


static func set_api_key(key: String) -> void:
	_config().set_value("llm", "api_key", key.strip_edges())
	_save()
