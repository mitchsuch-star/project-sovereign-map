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
	# NA-6c (July 19, 2026): the three Class C carve-out client states. None
	# exists at boot — these paint only once a settlement erects one — but an
	# unauthored tag falls through to COLOR_ENEMY_DEFAULT magenta, which is
	# deliberately "a bug to be seen" and would be exactly wrong for a state
	# the player just created on purpose. Chosen by searching the palette
	# space for the nearest colour to each nation's own heraldry that still
	# clears both perceptual floors: Polish crimson, Norman russet (gold on
	# gules), republican slate. Measured with the set present: min pairwise
	# blended deltaE 13.4 -> 13.35, fogged 7.8 -> 7.66 (floors 12.0 / 7.0).
	"DuchyOfWarsaw": Color(0.8, 0.275, 0.35),
	"Normandy": Color(0.725, 0.425, 0.175),
	"RomanRepublic": Color(0.4, 0.425, 0.475),
}

# === Nation Display Names (map labels / player-facing surfaces) ===
# Internal nation keys are single tokens ("KingdomOfItaly"); never show them
# raw (R7). Map labels resolve through display_nation_name(); keys absent
# here fall back to a camelCase split.
const NATION_DISPLAY_NAMES = {
	"Ottoman": "Ottoman Empire",
	"PapalStates": "Papal States",
	"KingdomOfItaly": "Kingdom of Italy",
	# NA-6c: the carve tags. "DuchyOfWarsaw" would otherwise camelCase-split
	# to "Duchy Of Warsaw" (capital O). RomanRepublic splits correctly by
	# luck — authored anyway so the rendering is intentional rather than
	# incidental. "Normandy" needs no row (single token, already correct)
	# and deliberately gets none: it is also a PROVINCE name on this map,
	# and prose substitution must keep skipping it.
	"DuchyOfWarsaw": "Duchy of Warsaw",
	"RomanRepublic": "Roman Republic",
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


# === NA-6 Formable Dreams: the formation identity override ===
# A formed nation keeps its internal TAG forever (save safety) and changes
# only its DISPLAY identity. The backend ships the whole map on every
# response (`nation_display_overrides` / `nation_flag_overrides`); both R7
# chokepoints below consult it FIRST, so "no surface may show the dead
# name" is a two-function property rather than an N-call-site sweep.
static var formation_overrides := {}      # tag -> new display name
static var formation_flag_overrides := {}  # tag -> heraldry asset tag

static func set_formation_overrides(names: Dictionary, flags: Dictionary) -> void:
	"""Adopt the backend's override maps. Flushes the nation-keyed flag
	path cache, which is otherwise NEVER invalidated and caches the
	negative result — without this a single lookup taken before the new
	asset resolved would serve the dead flag for the rest of the session."""
	if names == formation_overrides and flags == formation_flag_overrides:
		return
	formation_overrides = names.duplicate(true)
	formation_flag_overrides = flags.duplicate(true)
	_flag_path_cache.clear()


static func display_nation_name(nation: String) -> String:
	# The override outranks the static map: a formed nation must not fall
	# through to its authored name, nor to the camelCase split below
	# (which would render "DuchyOfWarsaw" as "Duchy Of Warsaw").
	if formation_overrides.has(nation):
		return formation_overrides[nation]
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
	# NA-6: the formation overrides run FIRST and shadow the static map.
	# Order is load-bearing: PROSE_NATION_KEY_SUBSTITUTIONS rewrites
	# "KingdomOfItaly" -> "Kingdom of Italy", after which the raw token is
	# gone and the override below could never match — which made the whole
	# formation branch dead for the entire v1 formable set.
	for key in formation_overrides:
		if _is_prose_safe_nation_key(key) and result.contains(key):
			result = result.replace(key, formation_overrides[key])
	for key in PROSE_NATION_KEY_SUBSTITUTIONS:
		# A live override already renamed this tag — never re-apply the
		# authored (now dead) name over it.
		if formation_overrides.has(key):
			continue
		if result.contains(key):
			result = result.replace(key, PROSE_NATION_KEY_SUBSTITUTIONS[key])
	# ONLY prose-safe tags are substituted above — that is, tags that
	# are safe to substring-replace. A tag that is also a province name on
	# this map (Normandy, Rome) or valid standalone prose would corrupt
	# every sentence containing the word; that is the documented `Ottoman`
	# exclusion above, and the NA-6c carve tags hit it head-on. Multi-token
	# camelCase tags ("KingdomOfItaly") never occur in correct prose, so
	# they are safe. Single-word tags are skipped and rely on the exact-key
	# display_nation_name() path instead.
	return result


static func _is_prose_safe_nation_key(key: String) -> bool:
	"""True when a nation tag can never appear as ordinary prose — i.e. it
	is a multi-token camelCase key like "KingdomOfItaly". Single words
	("Holland", "Normandy", "Rome") are NOT safe to substring-replace."""
	var seen_lower := false
	for i in range(key.length()):
		var ch := key[i]
		if ch.to_upper() == ch.to_lower():
			return false   # space, hyphen or digit — already display text
		if i > 0 and ch == ch.to_upper() and seen_lower:
			return true    # a second capitalised token
		if ch == ch.to_lower():
			seen_lower = true
	return false

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
	# NA-6: a formed nation flies its NEW colours. The cache is keyed by
	# the incoming tag, and set_formation_overrides() clears it, so the
	# swap takes effect on the response that carries the override.
	var asset := nation
	if formation_flag_overrides.has(nation):
		asset = str(formation_flag_overrides[nation])
	var path := FLAG_DIR + asset + ".svg"
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
	viewport. The layer-50 screens and every modal popup are authored as fixed
	rects (e.g. 840x620) that overflow small windows at high Interface Scale
	(content_scale_factor up to 2.0 halves the logical viewport) — the header
	row with the close X slides off-screen and becomes unclickable. Display-
	only: call on every open; the authored rect (captured on first call) stays
	the ceiling, so nothing changes on viewports that already fit. The 88px
	height reserve covers the 36px top bar plus breathing room.

	IMPORTANT (July 18, 2026): rewriting the offsets is NOT sufficient on its
	own. Godot clamps a Container's size UP to get_combined_minimum_size(), so
	a panel whose children declare fixed custom_minimum_size heights ignores
	the clamped offsets entirely — which is why the settlement popup ran off
	the screen. The second pass below therefore relaxes descendant height
	minimums to fit the budget, caching each authored value once so it stays
	the CEILING and viewports that already fit are byte-unchanged.

	Content that is genuinely unbounded (a fit_content RichTextLabel outside
	any ScrollContainer) still cannot be clamped by this function — such a
	label imposes height through its rendered text, not through a minimum this
	pass can see. Bound it at the scene level (scroll_active + fit_content
	false, or wrap it in a ScrollContainer) as well as calling this."""
	if panel == null:
		return
	# Anchor guard: this function assumes a CENTRE anchor (it writes symmetric
	# offsets about the midpoint). Edge-anchored panels — war_detail_popup
	# (right-anchored), war_status_panel — would be teleported by it, so they
	# are structurally excluded here rather than relying on each caller to
	# remember to skip.
	if not (is_equal_approx(panel.anchor_left, 0.5)
			and is_equal_approx(panel.anchor_right, 0.5)):
		return
	var viewport := panel.get_viewport()
	if viewport == null:
		return
	if not panel.has_meta("design_size"):
		var authored := Vector2(
			panel.offset_right - panel.offset_left,
			panel.offset_bottom - panel.offset_top)
		# Degenerate-rect guard: a scene that authors no offsets (only a
		# custom_minimum_size, as proclamation_popup did) would otherwise cache
		# (0,0) forever and every later clamp would compute w=h=0.
		var floor_size := panel.get_combined_minimum_size()
		if authored.x <= 1.0:
			authored.x = maxf(floor_size.x, 320.0)
		if authored.y <= 1.0:
			authored.y = maxf(floor_size.y, 240.0)
		panel.set_meta("design_size", authored)
	var design: Vector2 = panel.get_meta("design_size")
	var view: Vector2 = viewport.get_visible_rect().size
	var w: float = minf(design.x, maxf(320.0, view.x - 24.0))
	var h: float = minf(design.y, maxf(240.0, view.y - 88.0))
	panel.offset_left = -w / 2.0
	panel.offset_right = w / 2.0
	panel.offset_top = -h / 2.0
	panel.offset_bottom = h / 2.0
	_relax_child_minimums(panel, h)



const _RELAX_FLOOR := 48.0
const _RELAX_ROUNDS := 4


static func _relax_child_minimums(panel: Control, budget: float) -> void:
	"""Second pass: shrink descendant height minimums so the clamped offsets
	are not overridden by get_combined_minimum_size(). Never shrinks below a
	usable floor, and never shrinks a Button (its minimum is a click target).

	RESTORE FIRST, THEN MEASURE. The first cut measured the excess against the
	ALREADY-SHRUNK minimums left by the previous open and never wrote anything
	back, which made it a one-way ratchet: open the settlement popup once at
	Interface Scale 2.0 and the per-court table stayed pinned near the floor for
	the rest of the session, on a full-size screen, with no way to recover short
	of a restart. Restoring the cached authored values before measuring makes
	the result a pure function of (viewport, content) instead of a function of
	the previous call's writes — so it is genuinely idempotent, and it grows
	back when the player enlarges the window or lowers Interface Scale.

	ITERATE. One proportional pass systematically under-delivers, because a
	share handed to a control whose REAL minimum is text-derived (a fit_content
	label) or scroll-internal buys no actual reduction. Re-measuring each round
	and redistributing only among controls that still have room converges on the
	budget instead of stopping short of it."""
	var flexible: Array = []
	_collect_flexible(panel, flexible)
	if flexible.is_empty():
		return
	for control in flexible:
		control.custom_minimum_size.y = float(control.get_meta("authored_min_y"))

	for _round in range(_RELAX_ROUNDS):
		var excess: float = panel.get_combined_minimum_size().y - budget
		if excess <= 0.0:
			break
		# Only controls that can still give something up take a share.
		var room: float = 0.0
		var givers: Array = []
		for control in flexible:
			var headroom: float = control.custom_minimum_size.y - _RELAX_FLOOR
			if headroom > 0.5:
				givers.append(control)
				room += headroom
		if givers.is_empty() or room <= 0.0:
			break
		var take: float = minf(excess, room)
		for control in givers:
			var headroom: float = control.custom_minimum_size.y - _RELAX_FLOOR
			var share: float = take * (headroom / room)
			control.custom_minimum_size.y = maxf(
				_RELAX_FLOOR, control.custom_minimum_size.y - share)
			# Record our OWN output, so the next open can tell a value this pass
			# wrote apart from one the caller re-derived (see _collect_flexible).
			control.set_meta("relaxed_min_y", control.custom_minimum_size.y)


static func _collect_flexible(node: Node, out: Array) -> void:
	for child in node.get_children():
		if child is Control and child.visible and child.custom_minimum_size.y > 0.0:
			# The cached ceiling must FOLLOW the caller. proposal_confirm_popup
			# re-derives PerCourtScroll's floor from the live viewport on every
			# open, so a write-once cache would let a later relax clobber that
			# fresh value with a stale, smaller one. A value this pass wrote is
			# always smaller than the authored ceiling, so recognising our own
			# output (relaxed_min_y) is what keeps the two apart.
			var live: float = child.custom_minimum_size.y
			var ours: bool = (child.has_meta("relaxed_min_y")
					and is_equal_approx(live, float(child.get_meta("relaxed_min_y"))))
			if not ours and (not child.has_meta("authored_min_y")
					or not is_equal_approx(live, float(child.get_meta("authored_min_y")))):
				child.set_meta("authored_min_y", live)
			# A Button's minimum is its click target — shrinking it makes the
			# control harder to hit, which is the opposite of the goal.
			if not (child is Button):
				out.append(child)
		_collect_flexible(child, out)


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
