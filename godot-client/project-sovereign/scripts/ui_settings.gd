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


static func harness_active() -> bool:
	"""True under a capture / driven harness (which sets `_persist` false):
	the one thing such a run must never do is move or resize the OS window
	it was parked in (`Utils.apply_window_settings` checks this)."""
	return not _persist


# --- Terminal footprint ---
# UXR-1b (October 9, 2026): the DEFAULT footprint is no longer the 400x270 a
# 24-inch monitor wanted — with nothing stored, main.gd sizes the command
# window as a FRACTION of its logical viewport (`_default_terminal_size`,
# TERMINAL_WIDTH_FRACTION / TERMINAL_HEIGHT_FRACTION inside the published
# min/max). The constants below are the floor of that default and the value
# a caller with no viewport gets.
const TERMINAL_WIDTH_FRACTION := 0.28
const TERMINAL_HEIGHT_FRACTION := 0.32


# --- Panel sizes (UXR-2 "the layout law", October 12, 2026) ---
# Every gripped surface's remembered size, in LOGICAL px (like the terminal's,
# so a panel and its text scale together with the Interface Scale), one
# section per surface with `width` / `height` keys — `[terminal]` is the
# command window's own section, byte-identical to its pre-UXR-2 format. A
# closed table: name → [min, max]. The min is the floor a grip cannot drag
# under (the panel's own content minimum floors it further at drag time);
# the max only guards a hand-edited file — the clamp caps every panel to the
# live viewport anyway. The keys are the top bar's screen names.
const PANEL_LIMITS := {
	"terminal": [Vector2(MIN_TERMINAL_WIDTH, MIN_TERMINAL_HEIGHT), Vector2(MAX_TERMINAL_WIDTH, MAX_TERMINAL_HEIGHT)],
	"war_status": [Vector2(150, 60), Vector2(800, 1400)],
	"ledger": [Vector2(640, 360), Vector2(8192, 8192)],
	"diplomatic_ledger": [Vector2(680, 360), Vector2(8192, 8192)],
	"generals": [Vector2(560, 360), Vector2(8192, 8192)],
	"dispatch": [Vector2(480, 320), Vector2(8192, 8192)],
	"event_log": [Vector2(480, 320), Vector2(8192, 8192)],
	"gazette": [Vector2(480, 320), Vector2(8192, 8192)],
}


static func panel_min(panel_name: String) -> Vector2:
	return (PANEL_LIMITS[panel_name][0] if PANEL_LIMITS.has(panel_name) else Vector2.ZERO)


static func panel_max(panel_name: String) -> Vector2:
	return (PANEL_LIMITS[panel_name][1] if PANEL_LIMITS.has(panel_name) else Vector2(4096, 4096))


static func has_panel_size(panel_name: String) -> bool:
	return PANEL_LIMITS.has(panel_name) \
			and _config().has_section_key(panel_name, "width") \
			and _config().has_section_key(panel_name, "height")


static func get_panel_size(panel_name: String, fallback: Vector2) -> Vector2:
	"""The stored size clamped to the table's range, or `fallback` when none."""
	if not has_panel_size(panel_name):
		return fallback
	var lo := panel_min(panel_name)
	var hi := panel_max(panel_name)
	return Vector2(
		clampf(_read_num(panel_name, "width", fallback.x), lo.x, hi.x),
		clampf(_read_num(panel_name, "height", fallback.y), lo.y, hi.y))


static func set_panel_size(panel_name: String, panel_size: Vector2) -> void:
	if not PANEL_LIMITS.has(panel_name):
		return
	var lo := panel_min(panel_name)
	var hi := panel_max(panel_name)
	_config().set_value(panel_name, "width", clampf(panel_size.x, lo.x, hi.x))
	_config().set_value(panel_name, "height", clampf(panel_size.y, lo.y, hi.y))
	_save()


static func clear_panel_size(panel_name: String) -> void:
	for key in ["width", "height"]:
		if _config().has_section_key(panel_name, key):
			_config().erase_section_key(panel_name, key)
	_save()


static func clear_all_panel_sizes() -> void:
	"""Reset layout: every gripped surface back to its authored / fractional size."""
	for panel_name in PANEL_LIMITS:
		for key in ["width", "height"]:
			if _config().has_section_key(panel_name, key):
				_config().erase_section_key(panel_name, key)
	_save()


static func has_terminal_size() -> bool:
	return has_panel_size("terminal")


static func get_terminal_width() -> float:
	return clampf(_read_num("terminal", "width", DEFAULT_TERMINAL_WIDTH),
			MIN_TERMINAL_WIDTH, MAX_TERMINAL_WIDTH)


static func get_terminal_height() -> float:
	return clampf(_read_num("terminal", "height", DEFAULT_TERMINAL_HEIGHT),
			MIN_TERMINAL_HEIGHT, MAX_TERMINAL_HEIGHT)


static func set_terminal_size(width: float, height: float) -> void:
	# UXR-2: the command window is one row of the panel store (same keys,
	# same clampf to MIN/MAX_TERMINAL_* via PANEL_LIMITS, one save not two).
	set_panel_size("terminal", Vector2(width, height))


static func clear_terminal_size() -> void:
	"""Back to the viewport-fraction default (Reset layout / the grip's double-click)."""
	clear_panel_size("terminal")


static func default_terminal_size(viewport: Vector2) -> Vector2:
	"""The footprint a fresh install gets on THIS viewport (logical px)."""
	if viewport.x <= 0.0 or viewport.y <= 0.0:
		return Vector2(DEFAULT_TERMINAL_WIDTH, DEFAULT_TERMINAL_HEIGHT)
	return Vector2(
		clampf(viewport.x * TERMINAL_WIDTH_FRACTION, DEFAULT_TERMINAL_WIDTH, MAX_TERMINAL_WIDTH),
		clampf(viewport.y * TERMINAL_HEIGHT_FRACTION, DEFAULT_TERMINAL_HEIGHT, MAX_TERMINAL_HEIGHT))


# --- Window mode and size (UXR-1b: Settings → DISPLAY) ---
# "maximized" is the project's own boot (project.godot window/size/mode=2) and
# the default; the other three are applied by Utils.apply_window_settings at
# the menu's boot and on change. The size applies to "windowed" only.
const WINDOW_MODES := ["maximized", "fullscreen", "borderless", "windowed"]
const DEFAULT_WINDOW_MODE := "maximized"
const WINDOW_SIZES := ["native", "3440x1440", "2560x1440", "1920x1080"]
const DEFAULT_WINDOW_SIZE := "native"


static func get_window_mode() -> String:
	var mode := str(_config().get_value("display", "window_mode", DEFAULT_WINDOW_MODE))
	return mode if mode in WINDOW_MODES else DEFAULT_WINDOW_MODE


static func set_window_mode(mode: String) -> void:
	_config().set_value("display", "window_mode", mode if mode in WINDOW_MODES else DEFAULT_WINDOW_MODE)
	_save()


static func get_window_size() -> String:
	var size := str(_config().get_value("display", "window_size", DEFAULT_WINDOW_SIZE))
	return size if size in WINDOW_SIZES else DEFAULT_WINDOW_SIZE


static func set_window_size(size: String) -> void:
	_config().set_value("display", "window_size", size if size in WINDOW_SIZES else DEFAULT_WINDOW_SIZE)
	_save()


# --- Body text face (UXR-1b: Settings → INTERFACE) ---
# "garamond" is the July design (EB Garamond, x-height 0.44 em); "plain" swaps
# the theme's body faces for Source Sans 3 (OFL, shipped) — 0.49 em at the same
# size — through Utils.apply_body_font. Headings (Cinzel), the menu's own faces
# and the map's labels are untouched.
const BODY_FONTS := ["garamond", "plain"]
const DEFAULT_BODY_FONT := "garamond"


static func get_body_font() -> String:
	var face := str(_config().get_value("display", "body_font", DEFAULT_BODY_FONT))
	return face if face in BODY_FONTS else DEFAULT_BODY_FONT


static func set_body_font(face: String) -> void:
	_config().set_value("display", "body_font", face if face in BODY_FONTS else DEFAULT_BODY_FONT)
	_save()


# --- Text size (UXR-D1, Pre-Deploy S9b: Settings → INTERFACE) ---
# A multiplier on the THEME's named type sizes alone (Utils.apply_text_size):
# Caption 14, the theme's 16, BodyLarge 17 … DisplayTitleLarge 30 all scale
# together; no panel rect, no Interface Scale, no raw override moves. On an
# ultra-wide the panels have room and the type is the problem — this grows
# the type without growing the chrome. Never under 1.0: below it the theme's
# own sizes would read RED by the readability floor's rule.
const DEFAULT_TEXT_SIZE := 1.0
const MIN_TEXT_SIZE := 1.0
const MAX_TEXT_SIZE := 1.75
const TEXT_SIZE_STEP := 0.05


static func get_text_size() -> float:
	return clampf(_read_num("display", "text_size", DEFAULT_TEXT_SIZE), MIN_TEXT_SIZE, MAX_TEXT_SIZE)


static func set_text_size(value: float) -> void:
	_write_num("display", "text_size", clampf(snappedf(value, TEXT_SIZE_STEP), MIN_TEXT_SIZE, MAX_TEXT_SIZE))


# --- High contrast (UXR-D2, Pre-Deploy S9b: Settings → INTERFACE) ---
# Every dim-grey text class raised at least one step of the dim ladder, and
# none left under the step that reads 4.5 : 1 on the game's panels (this hex,
# the old COLOR_INFO) — Utils.apply_contrast holds the ladder. A preference
# like the body face: Reset layout keeps it.
const HIGH_CONTRAST_FLOOR_HEX := "a0a0a8"


static func get_high_contrast() -> bool:
	return bool(_config().get_value("display", "high_contrast", false))


static func set_high_contrast(on: bool) -> void:
	_config().set_value("display", "high_contrast", on)
	_save()


# --- HUD width (UXR-D3, Pre-Deploy S9b: Settings → DISPLAY) ---
# "full" spreads the HUD to the viewport's edges (the default, as ever);
# "centred" confines the command window, the notice rail, the top bar's two
# clusters, the war HUD and the map controls to a central band
# HUD_BAND_WIDTH logical px wide — on a 32:9 panel they sat 4,300–5,000 px
# apart. The map stays full-bleed. A viewport no wider than the band reads
# as Full (Utils.hud_band).
const HUD_WIDTHS := ["full", "centred"]
const DEFAULT_HUD_WIDTH := "full"
const HUD_BAND_WIDTH := 2560.0


static func get_hud_width() -> String:
	var width := str(_config().get_value("display", "hud_width", DEFAULT_HUD_WIDTH))
	return width if width in HUD_WIDTHS else DEFAULT_HUD_WIDTH


static func set_hud_width(width: String) -> void:
	_config().set_value("display", "hud_width", width if width in HUD_WIDTHS else DEFAULT_HUD_WIDTH)
	_save()


static func reset_layout() -> void:
	"""Settings → Reset layout: the scale back to the derivation, the text
	size to 100 %, the HUD to Full, the command window back to its viewport
	fraction, the window back to the project's maximized boot. Sound, the
	key, the School's latch stay."""
	set_ui_scale_auto()
	set_text_size(DEFAULT_TEXT_SIZE)
	set_hud_width(DEFAULT_HUD_WIDTH)
	clear_terminal_size()
	# UXR-2: every gripped screen's remembered size too.
	clear_all_panel_sizes()
	set_window_mode(DEFAULT_WINDOW_MODE)
	set_window_size(DEFAULT_WINDOW_SIZE)


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
# S14d part 2: one latch PER LESSON. The Danube keeps its original key
# ("tutorial", "done") byte-for-byte; every other lesson has its own.
static func _tutorial_done_key(lesson: String) -> String:
	return "done" if lesson == "tutorial" else "done_" + lesson


static func get_tutorial_done(lesson: String = "tutorial") -> bool:
	return bool(_config().get_value("tutorial", _tutorial_done_key(lesson), false))


static func set_tutorial_done(done: bool, lesson: String = "tutorial") -> void:
	_config().set_value("tutorial", _tutorial_done_key(lesson), done)
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
