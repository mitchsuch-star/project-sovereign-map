extends RefCounted
class_name UiSettings

# =============================================================================
# PROJECT SOVEREIGN — UI Settings persistence (UI-2 / DEF-13 fold)
# =============================================================================
# Single source of truth for the user-adjustable display preferences added in
# the UI Visual Foundation Sweep, Session U2:
#   • the command window's footprint (drag-resize grip)   → terminal/width,height
#   • the command window's text scale (A− / A+ buttons)   → terminal/scale
#   • the global interface scale (pause-menu Settings)    → display/ui_scale
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

# --- Command-window text scale (A− / A+) ---
const DEFAULT_TERMINAL_SCALE := 1.0
const MIN_TERMINAL_SCALE := 0.8
const MAX_TERMINAL_SCALE := 2.0
const TERMINAL_SCALE_STEP := 0.1

# --- Global interface scale (content_scale_factor; pause-menu Settings) ---
const DEFAULT_UI_SCALE := 1.0
const MIN_UI_SCALE := 0.75
const MAX_UI_SCALE := 2.0
const UI_SCALE_STEP := 0.05

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


# --- Terminal text scale ---
static func get_terminal_scale() -> float:
	return clampf(_read_num("terminal", "scale", DEFAULT_TERMINAL_SCALE),
			MIN_TERMINAL_SCALE, MAX_TERMINAL_SCALE)


static func set_terminal_scale(scale: float) -> void:
	_write_num("terminal", "scale", clampf(scale, MIN_TERMINAL_SCALE, MAX_TERMINAL_SCALE))


# --- Global interface scale ---
static func get_ui_scale() -> float:
	return clampf(_read_num("display", "ui_scale", DEFAULT_UI_SCALE),
			MIN_UI_SCALE, MAX_UI_SCALE)


static func set_ui_scale(scale: float) -> void:
	_write_num("display", "ui_scale", clampf(scale, MIN_UI_SCALE, MAX_UI_SCALE))
