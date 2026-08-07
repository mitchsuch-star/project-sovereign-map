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
const DEFAULT_UI_SCALE := 1.0
const MIN_UI_SCALE := 0.75
const MAX_UI_SCALE := 2.0
const UI_SCALE_STEP := 0.05
const UI_SCALE_BUTTON_STEP := 0.1

static var _cfg: ConfigFile = null


static func _config() -> ConfigFile:
	if _cfg == null:
		_cfg = ConfigFile.new()
		# A missing/unreadable file leaves an empty ConfigFile → pure defaults.
		_cfg.load(PATH)
	return _cfg


static func _read_num(section: String, key: String, default: float) -> float:
	return float(_config().get_value(section, key, default))


static func _write_num(section: String, key: String, value: float) -> void:
	_config().set_value(section, key, value)
	_config().save(PATH)


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
	return clampf(_read_num("display", "ui_scale", DEFAULT_UI_SCALE),
			MIN_UI_SCALE, MAX_UI_SCALE)


static func set_ui_scale(scale: float) -> void:
	_write_num("display", "ui_scale", clampf(scale, MIN_UI_SCALE, MAX_UI_SCALE))


# --- Battle sound effects (BD: the diorama's cannon thud + drum sting) ---
# The game's first audio — one boolean, honoured by every diorama sound call.
static func get_battle_sfx() -> bool:
	return bool(_config().get_value("audio", "battle_sfx", true))


static func set_battle_sfx(enabled: bool) -> void:
	_config().set_value("audio", "battle_sfx", enabled)
	_config().save(PATH)


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
