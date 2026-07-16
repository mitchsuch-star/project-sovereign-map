extends Node
class_name Utils

# =============================================================================
# PROJECT SOVEREIGN - Shared Utilities (R15)
# =============================================================================
# Single source of truth for color palette, nation colors, and formatting
# helpers. Referenced as Utils.COLOR_* from any script (class_name autoload).
# =============================================================================

# === Shared Color Palette (hex strings for BBCode) ===
const COLOR_GOLD = "d9c08c"
const COLOR_COMMAND = "7eb8da"
const COLOR_SUCCESS = "8fbc8f"
const COLOR_ERROR = "cd6b6b"
const COLOR_BATTLE = "daa06d"
const COLOR_INFO = "a0a0a8"
const COLOR_MARSHAL = "c9b8e0"
const COLOR_CONQUEST = "90d890"
const COLOR_FEEDBACK = "b8a0d9"
const COLOR_DISPATCH = "c9b878"
const COLOR_BERTHIER = "B8860B"
const COLOR_OBSERVATION = "DAA520"
const COLOR_TEXT = "eeeeee"
const COLOR_DIMMED = "808080"
const COLOR_WARNING = "e0c060"

# === Semantic Aliases (same hex, different context) ===
const COLOR_BLUE = "6495ed"
const COLOR_ORANGE = "daa06d"       # Same as COLOR_BATTLE — semantic alias for ledger UIs
const COLOR_GREY = "808080"         # Same as COLOR_DIMMED — semantic alias
const COLOR_HEADER = "B8860B"       # Same as COLOR_BERTHIER — semantic alias for ledger headers

# === Nation Colors (Color objects for UI elements) ===
# Single source of truth for nation colors (SCALE_READINESS_PLAN §3.3).
# Any script needing a nation color reads Utils.NATION_COLORS — do NOT
# redefine these locally. Drift is guarded by
# tests/test_gdscript_color_centralization.py.
const NATION_COLORS = {
	# Re-authored July 16, 2026 (user-directed): Paradox/EU4-convention national
	# colors so each nation reads by its grand-strategy identity — Austria WHITE,
	# Spain GOLD, Russia forest green, Ottoman vivid green, Prussia anthracite,
	# Portugal teal, Hanover pale yellow, Sardinia (Savoy) dark red-brown, Papal
	# cardinal purple. Second-tier entries keep their Slice-7.5 values where EU4
	# identity doesn't demand a change. The SET discipline still holds (DEF-10):
	# every edit must pass the perceptual floors in
	# tests/test_map_slice75_presentation.py — this set measures min pairwise
	# blended deltaE 13.4 / fogged 7.8 over the shipped terrain art.
	"France": Color(0.255, 0.412, 0.882),
	"Britain": Color(0.863, 0.078, 0.235),
	"Prussia": Color(0.16, 0.18, 0.22),
	"Austria": Color(0.93, 0.93, 0.90),
	"Saxony": Color(0.62, 0.72, 0.18),
	"Russia": Color(0.16, 0.38, 0.20),
	"Spain": Color(0.93, 0.76, 0.18),
	"Ottoman": Color(0.0, 0.58, 0.33),
	"Sweden": Color(0.0, 0.42, 0.65),
	"Naples": Color(0.62, 0.15, 0.4),
	"Portugal": Color(0.10, 0.42, 0.44),
	"Denmark": Color(0.5, 0.08, 0.12),
	"Bavaria": Color(0.62, 0.78, 0.95),
	"Hanover": Color(0.90, 0.86, 0.58),
	"Hesse": Color(0.66, 0.53, 0.82),
	"PapalStates": Color(0.50, 0.28, 0.58),
	"Sardinia": Color(0.42, 0.20, 0.24),
	"Holland": Color(0.95, 0.44, 0.03),
	"KingdomOfItaly": Color(0.25, 0.78, 0.35),
	"Switzerland": Color(0.92, 0.5, 0.6),
	"Neutral": Color(0.565, 0.933, 0.565),
}

# === Nation Display Names (map labels / player-facing surfaces) ===
# Internal nation keys are single tokens ("KingdomOfItaly"); never show them
# raw (R7). Map labels resolve through display_nation_name(); keys absent
# here fall back to a camelCase split.
const NATION_DISPLAY_NAMES = {
	"Ottoman": "Ottoman Empire",
	"PapalStates": "Papal States",
	"KingdomOfItaly": "Kingdom of Italy",
}

static func contrast_text_color(background: Color) -> Color:
	# Slice 7.5 review fold: light palette entries (Austria white, Bavaria
	# pale blue, Spain gold, Hanover pale yellow) make white chip text
	# illegible. Any consumer drawing text directly over a raw NATION_COLORS
	# fill picks its text color here so the palette can be re-authored
	# without re-auditing every chip.
	if background.get_luminance() > 0.62:
		return Color(0.12, 0.1, 0.08)
	return Color.WHITE


static func display_nation_name(nation: String) -> String:
	if NATION_DISPLAY_NAMES.has(nation):
		return NATION_DISPLAY_NAMES[nation]
	# The camelCase split only applies to strict single-token alphabetic keys.
	# Anything carrying a space, hyphen, or digit is already display text
	# (e.g. region names like "Franche-Comte" pass through untouched, so the
	# helper is safe on mixed nation-or-region fields).
	for i in range(nation.length()):
		var ch := nation[i]
		if ch.to_upper() == ch.to_lower():
			return nation
	var result := ""
	for i in range(nation.length()):
		var ch := nation[i]
		if i > 0 and ch == ch.to_upper() and ch != ch.to_lower():
			result += " "
		result += ch
	return result


# === Diplomatic State Display (player-facing pills) ===
# Internal diplomatic states are SNAKE_CASE enums; multi-word states must not
# leak raw underscores to players (R7). Pills stay upper-case by convention.
const DIPLO_STATE_DISPLAY = {
	"NON_AGGRESSION": "NON-AGGRESSION",
}

static func display_diplo_state(state: String) -> String:
	if DIPLO_STATE_DISPLAY.has(state):
		return DIPLO_STATE_DISPLAY[state]
	return state.replace("_", " ")


# === Backend-Prose Nation Key Substitution ===
# Backend-composed prose (dispatch lines, notifications, headlines) can embed
# raw multi-word nation keys mid-sentence. These tokens never appear in
# correct display text, so whole-string replacement is safe. "Ottoman" is
# deliberately EXCLUDED: it is valid prose on its own ("the Ottoman court")
# and substituting "Ottoman Empire" would corrupt existing sentences.
const PROSE_NATION_KEY_SUBSTITUTIONS = {
	"KingdomOfItaly": "Kingdom of Italy",
	"PapalStates": "Papal States",
}

static func humanize_nation_keys_in_text(text: String) -> String:
	var result := text
	for key in PROSE_NATION_KEY_SUBSTITUTIONS:
		if result.contains(key):
			result = result.replace(key, PROSE_NATION_KEY_SUBSTITUTIONS[key])
	return result

# === Map Connection Line Color ===
# Slice 7.5 fold (user report: lines blend in with the map): sea-link routes
# draw as dashed dark map-ink — the old light grey vanished against the
# blue-grey sea art and read as a rendering artifact rather than a route.
const COLOR_CONNECTION = Color(0.25, 0.17, 0.1, 0.8)

# === Default Fallback Colors for Unknown Nations ===
# Deliberately artificial magenta (Slice 7.5 / DEF-10): the old muted red sat
# a blended deltaE ~4 from Switzerland, so an unmapped controller silently
# impersonated Swiss territory. A controller falling back to this color is a
# BUG to be seen, not camouflage.
const COLOR_ENEMY_DEFAULT = Color(0.9, 0.05, 0.85)

# === Shared UI Chrome Colors (Color objects for StyleBox / theme overrides) ===
# UI-2 Part 2 centralization: these navy/gold/state Colors recurred inline
# across the HUD, ledger, and popup scripts (top_bar, both ledgers, popup_base,
# war status/detail, notifications, dialogs). Single source so a re-skin is one
# edit instead of touching dozens of scenes. The COLOR_* consts above are hex
# STRINGS for BBCode; these are the Color-object equivalents for
# add_theme_*_override() and StyleBoxFlat. Values are byte-identical to the
# literals they replace (the gold matches main_theme.tres / COLOR_GOLD).
const UI_GOLD := Color(0.85, 0.75, 0.55, 1.0)                    # primary gold accent (borders, active text)
const UI_GOLD_BRIGHT := Color(0.941176, 0.878431, 0.690196, 1.0)  # hover/focus gold
const UI_PANEL_BG := Color(0.12, 0.14, 0.18, 1.0)               # normal tab / bar panel fill
const UI_ACTIVE_TAB_BG := Color(0.25, 0.22, 0.15, 1.0)         # active tab / highlighted button fill
const UI_POPUP_BG := Color(0.1, 0.1, 0.18, 0.95)               # modal popup panel fill (matches theme PanelContainer)
const UI_TEXT_DIM := Color(0.75, 0.72, 0.65, 1.0)              # dimmed label text
const UI_ALERT := Color(0.85, 0.25, 0.25, 1.0)                 # alert / danger red
const UI_WARNING := Color(0.85, 0.65, 0.2, 1.0)               # amber warning / threat
# Score / balance-bar palette (shared by war_status_panel + war_detail_popup):
const UI_SCORE_POSITIVE := Color(0.29, 0.67, 0.29)            # winning green
const UI_SCORE_NEGATIVE := Color(0.67, 0.27, 0.27)           # losing red
const UI_SCORE_NEUTRAL := Color(0.75, 0.75, 0.78)           # neutral grey
const UI_BAR_BG := Color(0.15, 0.15, 0.2, 0.8)              # score bar track

# === UI-3 Icon Wiring Helpers ===
# The curated icon sets ship as WHITE silhouettes (game-icons: black bg stripped;
# phosphor: currentColor→#ffffff), so a gold icon_*_color tint lands the intended
# hue. These centralize the two button-icon patterns so every screen wires icons
# identically (display-only, GR6).
const ICON_PHOSPHOR := "res://assets/ui/icons/phosphor/"
const ICON_GAME := "res://assets/ui/icons/game-icons/"

static func apply_icon_only_button(btn, icon_path: String) -> void:
	"""Turn a small text button (a close X, etc.) into a tinted icon-only button:
	transparent bg, tight margins so a 256px SVG shrinks to the button, gold tint
	that brightens on hover. `expand_icon` keeps the source high-res (crisp at any
	UI scale)."""
	if btn == null:
		return
	var tex = load(icon_path)
	if tex == null:
		return
	btn.text = ""
	btn.icon = tex
	btn.expand_icon = true
	var empty := StyleBoxEmpty.new()
	empty.set_content_margin_all(3)
	for state in ["normal", "hover", "pressed", "focus", "disabled"]:
		btn.add_theme_stylebox_override(state, empty)
	btn.add_theme_color_override("icon_normal_color", UI_GOLD)
	btn.add_theme_color_override("icon_hover_color", UI_GOLD_BRIGHT)
	btn.add_theme_color_override("icon_pressed_color", UI_GOLD_BRIGHT)
	btn.add_theme_color_override("icon_focus_color", UI_GOLD_BRIGHT)


static func apply_button_icon(btn, icon_path: String) -> void:
	"""Add a tinted leading icon to a text button (keeps the label + its styling).
	`expand_icon` scales the icon to the button height so the bar layout is not
	blown out by the 256px source."""
	if btn == null:
		return
	var tex = load(icon_path)
	if tex == null:
		return
	btn.icon = tex
	btn.expand_icon = true
	btn.add_theme_color_override("icon_normal_color", UI_GOLD)
	btn.add_theme_color_override("icon_hover_color", UI_GOLD_BRIGHT)
	btn.add_theme_color_override("icon_pressed_color", UI_GOLD_BRIGHT)
	btn.add_theme_color_override("icon_focus_color", UI_GOLD_BRIGHT)


# === UI-6 Heraldry Helpers ===
# 16 period national flag SVGs (PD, assets/ui/heraldry/<Nation>.svg) — wired
# into the diplomatic ledger, wizard, and war surfaces. Flags are colored art:
# NEVER tint them gold (that is the silhouette-icon pattern above). Lookups
# are cached so bbcode re-renders do not re-probe ResourceLoader.
const FLAG_DIR := "res://assets/ui/heraldry/"
static var _flag_path_cache := {}

static func nation_flag_path(nation: String) -> String:
	"""Path to a nation's flag SVG, or '' when no flag asset exists."""
	if _flag_path_cache.has(nation):
		return _flag_path_cache[nation]
	var path := FLAG_DIR + nation + ".svg"
	if not ResourceLoader.exists(path):
		path = ""
	_flag_path_cache[nation] = path
	return path


static var _flag_aspect_cache := {}

static func bb_flag(nation: String, height: int = 14) -> String:
	"""Inline BBCode flag thumbnail (with trailing space), or '' if none.
	Width derives from the texture's REAL aspect ratio — a hardcoded 3:2 box
	squashed the 2:1 Union Jack 25% and stretched the 1:1 Papal banner 50%
	([img] with both dims hard-stretches; only width-alone preserves aspect)."""
	var path := nation_flag_path(nation)
	if path == "":
		return ""
	var aspect: float = 1.5
	if _flag_aspect_cache.has(path):
		aspect = _flag_aspect_cache[path]
	else:
		var tex = load(path)
		if tex != null and tex.get_height() > 0:
			aspect = float(tex.get_width()) / float(tex.get_height())
		_flag_aspect_cache[path] = aspect
	var width := int(round(height * aspect))
	return "[img width=%d height=%d]%s[/img] " % [width, height, path]


static func apply_flag_icon(btn, nation: String) -> void:
	"""Add a nation flag as a button's leading icon (untinted — flags are
	colored art, unlike the white-silhouette icon sets)."""
	if btn == null:
		return
	var path := nation_flag_path(nation)
	if path == "":
		return
	var tex = load(path)
	if tex == null:
		return
	btn.icon = tex
	btn.expand_icon = true


# === Shared BBCode Widget Helpers (UI-6) ===
# Single source for the inline-icon and button-chip idioms that grew up in
# marshal_management.gd — any RichTextLabel surface builds chips through
# these instead of re-authoring the pattern.

static func bb_icon(path: String, size: int, color: String) -> String:
	"""Inline BBCode icon, tinted (the curated sets ship as white silhouettes
	so the [img color=...] multiply lands the intended hue)."""
	return "[img width=%d height=%d color=#%s]%s[/img]" % [size, size, color, path]


static func bb_button_chip(url_meta: String, label: String, text_hex: String, bg_hex: String, icon_path := "") -> String:
	"""A filled bbcode 'button' — a `bgcolor` pill with padding, an optional
	leading icon, and a `url` covering the whole chip. Reads as a button
	inside a RichTextLabel without a real Button node."""
	var inner := ""
	if icon_path != "":
		inner += bb_icon(icon_path, 18, text_hex) + " "
	inner += "[color=#" + text_hex + "]" + label + "[/color]"
	return "[bgcolor=#" + bg_hex + "]  [url=" + url_meta + "]" + inner + "[/url]  [/bgcolor]"


# === Layout Helpers ===

static func clamp_centered_panel(panel: Control) -> void:
	"""Fit a centre-anchored fixed-size panel inside the CURRENT logical
	viewport. The layer-50 screens are authored as fixed rects (e.g. 840x620)
	that overflow small windows at high Interface Scale (content_scale_factor
	up to 2.0 halves the logical viewport) — the header row with the close X
	slides off-screen and becomes unclickable. Display-only: call on every
	open; the authored rect (captured on first call) stays the ceiling, so
	nothing changes on viewports that already fit. The 88px height reserve
	covers the 36px top bar plus breathing room."""
	if panel == null:
		return
	if not panel.has_meta("design_size"):
		panel.set_meta("design_size", Vector2(
			panel.offset_right - panel.offset_left,
			panel.offset_bottom - panel.offset_top))
	var design: Vector2 = panel.get_meta("design_size")
	var viewport := panel.get_viewport()
	if viewport == null:
		return
	var view: Vector2 = viewport.get_visible_rect().size
	var w: float = minf(design.x, maxf(320.0, view.x - 24.0))
	var h: float = minf(design.y, maxf(240.0, view.y - 88.0))
	panel.offset_left = -w / 2.0
	panel.offset_right = w / 2.0
	panel.offset_top = -h / 2.0
	panel.offset_bottom = h / 2.0


# === Formatting Helpers ===

static func bbcode_color(text: String, color: String) -> String:
	return "[color=#" + color + "]" + text + "[/color]"

static func format_number(n: int) -> String:
	"""Format integer with thousands separators (e.g. 12,500)."""
	var s = str(abs(n))
	var result = ""
	var count = 0
	for i in range(s.length() - 1, -1, -1):
		if count > 0 and count % 3 == 0:
			result = "," + result
		result = s[i] + result
		count += 1
	if n < 0:
		result = "-" + result
	return result
