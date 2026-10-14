extends Node
class_name Utils

# =============================================================================
# PROJECT SOVEREIGN - Shared Utilities (R15)
# =============================================================================
# Single source of truth for color palette, nation colors, and formatting
# helpers. Referenced as Utils.COLOR_* from any script (class_name autoload).
# =============================================================================

# === Backend origin (Golden Rule 7 + SOVEREIGN_PORT override) ===
# THE single source for the backend URL on the client side. Default stays
# 127.0.0.1:8005; a SOVEREIGN_PORT env var moves BOTH sides at once
# (backend/main.py reads the same variable), so a test client can run
# beside the player's live session without fighting over one port.
# Every script that talks to the backend derives from this — never
# hardcode the origin again.

static func backend_url() -> String:
	var port := OS.get_environment("SOVEREIGN_PORT")
	if port == "" or not port.is_valid_int():
		port = "8005"
	return "http://127.0.0.1:" + port


static func backend_origin_label() -> String:
	"""The origin without the scheme — for status lines."""
	return backend_url().trim_prefix("http://")


# FA-29 (slice 13): what to tell somebody whose war office does not answer.
# Two surfaces said `.venv\Scripts\python.exe -m backend.main` and
# `python -m backend.main` unconditionally, and NEITHER exists in the zip a
# tester unpacks — no Python, no `backend/`, no venv. The whole project had
# ZERO `has_feature` / `is_debug_build` / `is_editor_hint` calls (census over
# every tracked file), so no arm could exist.
#
# The template arm deliberately does NOT say "double-click launch.bat" alone:
# `launch.bat` reuses an already-answering server and then runs
# `start /wait InkAndIron.exe`, so a player who launched the exe directly must
# CLOSE it first or the batch waits behind the window it is telling them about.
# FA-D10 (slice 17, Phase 2): the ally-standing rows, formatted ONCE for the
# HUD tooltip and the War Detail screen (both read `contribution_share`).
static func standing_lines(war_data: Dictionary) -> Array:
	var lines: Array = []
	var contribution = war_data.get("contribution_share", [])
	if contribution is Array and contribution.size() > 0:
		lines.append("Standing (top 5):")
		for row in contribution:
			if not row is Dictionary:
				continue
			var nation = str(row.get("nation", "?"))
			var standing = str(row.get("standing_display", "Standing pending"))
			var material = float(row.get("material_share", 0.0)) * 100.0
			var leader_marker = "*" if row.get("is_leader", false) else " "
			# FA-S17-18 (Phase 4): say which side each row is on. The block
			# listed both sides under a title naming only the ENEMIES
			# ("WAR WITH BRITAIN + AUSTRIA + RUSSIA"), so France and her
			# allies read as peers of the courts they are fighting — and on
			# the boot board Austria sorted FIRST, above France. The backend
			# has always carried `side_label`; the formatter dropped it. The
			# ordering, the cap and the overflow count are untouched.
			var side_label = str(row.get("side_label", ""))
			var side_note = ""
			if side_label != "":
				side_note = " [" + side_label + "]"
			lines.append("  " + leader_marker + " " + display_nation_name(nation) + side_note + " — " + standing + " (" + str(int(round(material))) + "%)")
		var overflow = int(war_data.get("contribution_overflow_count", 0))
		if overflow > 0:
			lines.append("  +" + plural(overflow, "more participant"))
	else:
		var status_display = str(war_data.get("standing_status_display", ""))
		if status_display != "":
			lines.append("Standing: " + status_display)
	return lines


# LV-7 (row EP F1): the SITUATION line's first sentence, ONCE for the terminal
# briefing and the Dispatch screen. It read "Enemy nations hold 98 regions" on
# the 1805 boot — every controller that was not France, vassals and neutral
# courts included. The backend now counts only the courts AT WAR with us and
# says so with `enemy_regions_are_at_war`; a payload without the flag (the
# legacy fixture, the lever down) keeps the old wording, which is what it
# counted.
static func enemy_regions_sentence(situation: Dictionary) -> String:
	var n := int(situation.get("enemy_regions", 0))
	var noun := "region" if n == 1 else "regions"
	var at_war = situation.get("enemy_regions_are_at_war", false)
	if typeof(at_war) == TYPE_BOOL and at_war:
		return "The courts at war hold " + str(n) + " " + noun + "."
	return "Enemy nations hold " + str(n) + " " + noun + "."


# LV-8 (row EP F1): a war purpose's targets, ONCE for the war panel tooltip,
# the war-detail popup and both War Summaries. The backend's `target_summary`
# is the one sentence ("the homeland — 28 of 28 provinces held", or at most
# eight names); a payload without it (the legacy fixture, the lever down)
# keeps the joined list — or `fallback` when there is none.
static func objective_targets_text(objective: Dictionary, fallback: String) -> String:
	var summary = objective.get("target_summary", "")
	if summary is String and summary != "":
		return summary
	var targets = objective.get("target_regions", [])
	if targets is Array and not targets.is_empty():
		return ", ".join(targets)
	return fallback


static func launch_hint() -> String:
	if OS.has_feature("editor"):
		return ".venv\\Scripts\\python.exe -m backend.main"
	return ("close this window and start the game with launch.bat "
			+ "(it starts the war office first, and must stay open)")


static func server_lost_hint() -> String:
	"""PB-4 (the release build, Sept 23 2026): what to do when the war office
	stops answering mid-game. The zip has no console to read, so the line names
	the remedy and the log a report should carry."""
	if OS.has_feature("editor"):
		return "The war office is not answering — restart it with " + launch_hint() + "."
	return ("The war office (the server window) is not answering. If that window "
		+ "has closed, close the game and start it again with launch.bat — your "
		+ "campaign is autosaved every turn (Load). Its log is "
		+ SERVER_LOG_PATH + " — please send it with a report.")


static func server_error_hint(code: int) -> String:
	"""PB-4: a 500 is a bug, and the log holds its traceback."""
	if OS.has_feature("editor"):
		return "Server error (code " + str(code) + ") — see the backend console."
	return ("The war office hit an error (code " + str(code) + "). Your last turn "
		+ "is autosaved. The details are in " + SERVER_LOG_PATH
		+ " — please send it with a report.")


const SERVER_LOG_PATH = "%APPDATA%\\InkAndIron\\logs\\server.log"


static func build_label() -> String:
	"""The version line. `application/config/version` is authored in
	project.godot; the fallback is what a source checkout without one reads."""
	var v := str(ProjectSettings.get_setting(
		"application/config/version", ""))
	if v.strip_edges() == "":
		return "development build"
	return v


# === Shared Color Palette (hex strings for BBCode) ===
const COLOR_GOLD = "d9c08c"
const COLOR_COMMAND = "7eb8da"
const COLOR_SUCCESS = "8fbc8f"
const COLOR_ERROR = "cd6b6b"
# S12 (UXR3-4, UXR3-35): COLOR_ERROR read 3.75 : 1 as chip text on the chip
# fill 233043; a red chip label takes the same hue, lighter (4.83 : 1).
const COLOR_ERROR_CHIP = "d68686"
const COLOR_BATTLE = "daa06d"
# UXR-D2 (Pre-Deploy S9b): the DIM tokens are static — High contrast raises
# them (Utils.apply_contrast); every other colour stays a constant.
static var COLOR_INFO := "a0a0a8"
const COLOR_MARSHAL = "c9b8e0"
const COLOR_CONQUEST = "90d890"
const COLOR_FEEDBACK = "b8a0d9"
const COLOR_DISPATCH = "c9b878"
const COLOR_BERTHIER = "B8860B"
const COLOR_OBSERVATION = "DAA520"
# CA8-7: the enemy commander's own line. A cool tone against
# Berthier's gold, so the two narrators are never confused for one
# another in the enemy phase (battle_diorama.gd dims it instead --
# there the speaker is already labelled by position on the tableau).
const COLOR_ENEMY_VOICE = "9aaec9"
const COLOR_TEXT = "eeeeee"
static var COLOR_DIMMED := "808080"
const COLOR_WARNING = "e0c060"

# === Semantic Aliases (same hex, different context) ===
const COLOR_BLUE = "6495ed"
const COLOR_ORANGE = "daa06d"       # Same as COLOR_BATTLE — semantic alias for ledger UIs
static var COLOR_GREY := "808080"         # Same as COLOR_DIMMED — semantic alias
# The faintest grey (the Generals screen's own until UXR-D2 shared it).
static var COLOR_DIM := "666670"
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
	# DEF-5 naval NV-2 (Free Ireland): emerald-teal — measured with the set
	# present: blended worst pair 13.2 vs Ottoman (floor 12.0), fogged 7.88
	# (floor 7.0); the set minimums stay 13.2 / 7.66.
	"Ireland": Color(0.0, 0.73, 0.60),
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

# PT-G5(a): the client had NO marshal-name helper at all. Nation keys are
# routed (`display_nation_name`), marshal keys never were — measured ~84
# raw camelCase renders in one campaign, with the correctly spaced name
# printing three lines below in the same block because the BACKEND
# humanizes `enemy_voice` and the dialog does not humanize its own.
#
# Mirrors `display_names.humanize_entity_name` exactly: split camelCase
# boundaries, and underscores to spaces.
static func humanize_entity_name(name: String) -> String:
	if name == "":
		return name
	var out := ""
	for i in name.length():
		var ch := name[i]
		if i > 0 and ch == ch.to_upper() and ch != ch.to_lower() 				and name[i - 1] != " " and name[i - 1] == name[i - 1].to_lower() 				and name[i - 1] != name[i - 1].to_upper():
			out += " "
		out += ch
	return out.replace("_", " ")


# LV-2 (row EP F2, Sept 25 2026): the marshal-name sibling of
# `display_nation_name` — the diorama nameplate and the war-table piece
# label rendered the roster KEY ("ArchdukeCharles"). One name for the
# concept, so a new surface reaches for it rather than the raw field.
static func display_marshal_name(name: String) -> String:
	return humanize_entity_name(name)


# LV-9 (row EP F2): "1 unanswered envoy(s)" — the `(s)` hedge stood at
# fourteen client sites. The client mirror of `display_names.plural`:
# the count and the noun, the noun agreeing with the count.
const _PLURAL_IRREGULAR = {
	"envoy": "envoys", "man": "men", "corps": "corps", "sail": "sail",
	"province": "provinces", "turn": "turns", "port": "ports",
	"region": "regions", "participant": "participants",
	"petition": "petitions",
}

static func plural(n: int, noun: String) -> String:
	if n == 1:
		return str(n) + " " + noun
	if _PLURAL_IRREGULAR.has(noun):
		return str(n) + " " + _PLURAL_IRREGULAR[noun]
	if noun.ends_with("s") or noun.ends_with("x") or noun.ends_with("ch") or noun.ends_with("sh"):
		return str(n) + " " + noun + "es"
	if noun.ends_with("y") and noun.length() > 1 and not ("aeiou".contains(noun[noun.length() - 2])):
		return str(n) + " " + noun.substr(0, noun.length() - 1) + "ies"
	return str(n) + " " + noun + "s"


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
# UXR-D2 (Pre-Deploy S9b): the dim ladder, faintest first — 666670, 808080,
# a0a0a8, UI_TEXT_DIM, and the step High contrast adds above it.
const DIM_LADDER: Array = [
	Color(0.4, 0.4, 0.4392, 1.0), Color(0.502, 0.502, 0.502, 1.0),
	Color(0.6275, 0.6275, 0.6588, 1.0), UI_TEXT_DIM, Color(0.8667, 0.8392, 0.7843, 1.0)]
# The step that reads 4.5 : 1 on the game's panels: High contrast leaves no
# dim text under it (808080 on the navy panel read 4.3 : 1).
const DIM_FLOOR_INDEX := 2
const UI_ALERT := Color(0.85, 0.25, 0.25, 1.0)                 # alert / danger red
const UI_WARNING := Color(0.85, 0.65, 0.2, 1.0)               # amber warning / threat
# Score / balance-bar palette (shared by war_status_panel + war_detail_popup):
const UI_SCORE_POSITIVE := Color(0.29, 0.67, 0.29)            # winning green
const UI_SCORE_NEGATIVE := Color(0.67, 0.27, 0.27)           # losing red
const UI_SCORE_NEUTRAL := Color(0.75, 0.75, 0.78)           # neutral grey
const UI_BAR_BG := Color(0.15, 0.15, 0.2, 0.8)              # score bar track
# UXR-3 fixes (Pre-Deploy S12, R4 "0 one-off greys in a surface's own files"):
# every grey a script drew as a literal is a named token here, its value
# unchanged. Alpha is part of the token where the site drew one.
const UI_REASON_GREY := Color(0.6, 0.6, 0.65, 1)            # a closed arm's reason line (wizard, petition card)
const UI_DISABLED_TEXT := Color(0.55, 0.55, 0.55, 0.8)      # the title screen's disabled button text
const UI_FAINT_BORDER := Color(0.5, 0.48, 0.42, 0.2)        # the title screen's disabled button border
const UI_VERSION_LINE := Color(0.65, 0.63, 0.58, 0.8)       # the build line (title screen, pause menu)
const UI_CLOSED_ARM := Color(0.55, 0.52, 0.48, 1)           # the petition card's closed command arm
const UI_MAILBOX_NOTE := Color(0.7, 0.72, 0.78, 1.0)        # the letter-book's caption note
const UI_MAILBOX_IDLE_BORDER := Color(0.26, 0.3, 0.38, 0.9) # a waiting letter's border
const UI_MAILBOX_WAITING := Color(0.66, 0.66, 0.7, 1.0)     # the WAITING badge
const UI_TURN_STAMP := Color(0.56, 0.58, 0.64, 1.0)         # a letter's turn stamp; the letter-book hint
const UI_MAILBOX_TERMS := Color(0.68, 0.72, 0.8, 1.0)       # a digest letter's terms line
const UI_RAIL_TURN_STAMP := Color(0.58, 0.58, 0.64, 1)      # the notice rail's turn stamp
const UI_ENVOY_IDLE_BORDER := Color(0.32, 0.35, 0.42, 0.9)  # the top bar's idle Envoys border
const UI_ENVOY_IDLE_HOVER := Color(0.16, 0.18, 0.23, 0.95)  # its hover fill
const UI_BAR_CENTER_HUD := Color(0.35, 0.35, 0.4, 0.6)      # the war HUD bar's centre tick
const UI_BAR_CENTER_DETAIL := Color(0.4, 0.4, 0.45, 0.6)    # the war-detail bar's centre tick
const UI_NEUTRAL_FIGURE := Color(0.6, 0.6, 0.6)             # a tableau figure with no nation colour
const UI_ABSENT_FIGURE := Color(0.62, 0.62, 0.66, 1.0)      # a no-show's line on the tableau's shelf
const UI_ABSENT_WASH := Color(0.62, 0.62, 0.66, 0.9)        # the no-show shelf's figure wash
const UI_DIORAMA_BAIZE := Color(0.129, 0.208, 0.153, 1.0)   # the tableau's green felt
const UI_TOPPLE_TINT := Color(0.52, 0.47, 0.44, 1.0)        # a fallen figure
const UI_FOUNDER_TINT := Color(0.42, 0.40, 0.42, 1.0)       # a foundering ship
const UI_DEAD_RING := Color(0.45, 0.45, 0.48, 1.0)          # a fallen marshal's locket ring
const UI_END_PLATE_BG := Color(0.17, 0.15, 0.11, 1.0)       # the end card's register plate
const UI_HINT_GREY := Color(0.7, 0.7, 0.75, 1)              # a dialog's hint line (Load, Reward)
const COLOR_REPORT := "aaaaaa"                              # the enemy phase's report lines (toned at the site)
const COLOR_CHIP_BG_NAVY := "22283a"                        # the Marshalate's Back chip
const COLOR_CHIP_BG_GREEN := "1e3320"                       # the Commission chip
# The war room's map: the renderer's 29 grey literals, values unchanged.
const MAP_UNWIRED_GREY := Color(0.32, 0.32, 0.34, 1.0)      # a province not yet in play
const MAP_CONNECTION_GREY := Color(0.6, 0.6, 0.6)           # a road with no colour of its own
const MAP_FOG_BORDER := Color(0.25, 0.25, 0.3)              # an unknown province's border
const MAP_FOG_TEXT := Color(0.5, 0.5, 0.55)                 # unknown / last-known text
const MAP_STALE_TEXT := Color(0.7, 0.7, 0.75)               # stale text; a fogged tooltip's border
const MAP_NEUTRAL_NATION := Color(0.5, 0.5, 0.5)            # a force or province with no nation colour
const MAP_CHIP_BORDER := Color(0.4, 0.4, 0.45)              # a force chip's border
const MAP_CHIP_DARK_BORDER := Color(0.25, 0.22, 0.18)       # a garrison chip's border on a light fill
const MAP_TEXT_GREY := Color(0.7, 0.7, 0.7)                 # secondary tooltip and chip text
const MAP_TOOLTIP_BORDER := Color(0.6, 0.6, 0.7)            # a force tooltip's border
const MAP_TOOLTIP_FOG_BORDER := Color(0.4, 0.4, 0.5)        # an unknown province's tooltip border
const MAP_UNKNOWN_TEXT := Color(0.55, 0.55, 0.6)            # "Income: Unknown", "Stability: Unknown"

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


static func bb_chip_disabled(label: String, icon_path := "") -> String:
	"""The honest-availability partner of bb_button_chip: the same pill shape
	with NO url and dimmed ink, so a gated action reads as present-but-locked
	instead of missing. Pair it with a short stated reason after the chip."""
	var inner := ""
	if icon_path != "":
		inner += bb_icon(icon_path, 18, "6f7480") + " "
	inner += "[color=#6f7480]" + label + "[/color]"
	return "[bgcolor=#20242c]  " + inner + "  [/bgcolor]"


# === High contrast (UXR-D2, Pre-Deploy S9b) ===
# Settings → INTERFACE → High contrast. "Dim" is a CLASS, not one token: the
# BBCode greys (COLOR_DIM / DIMMED / GREY / INFO), UI_TEXT_DIM, and the grey
# font colours authored as literals in scenes and scripts. On: every member
# rises at least one step of DIM_LADDER, and none stays under the step that
# reads 4.5 : 1. Two roads carry it: the BBCode tokens are static (re-toned
# here, so every text built after reads them), and every Control's grey
# font-colour override is raised through ONE chokepoint (`contrast_node`) —
# as each node enters the tree (main / main_menu hook `node_added`) and over
# the whole tree when the toggle flips. Text a screen already wrote in BBCode
# takes the new colour when that screen next draws.
static var _hc_on := false


static func is_dim(c: Color) -> bool:
	"""A grey (low chroma) in the dim band: from the ladder's faintest step
	to UI_TEXT_DIM. Brighter text and coloured text are not dim."""
	var chroma := maxf(c.r, maxf(c.g, c.b)) - minf(c.r, minf(c.g, c.b))
	var l := c.get_luminance()
	return chroma <= 0.12 and l >= 0.15 and l <= UI_TEXT_DIM.get_luminance() + 0.02


static func raise_dim(c: Color) -> Color:
	"""A dim colour one ladder step up (never under DIM_FLOOR_INDEX), its
	alpha kept; anything else unchanged."""
	if not is_dim(c):
		return c
	var l := c.get_luminance()
	for i in range(DIM_LADDER.size()):
		var t: Color = DIM_LADDER[i]
		if i >= DIM_FLOOR_INDEX and t.get_luminance() > l + 0.02:
			return Color(t.r, t.g, t.b, c.a)
	return c


static func toned(c: Color) -> Color:
	"""A colour as High contrast would draw it (unchanged when off) — for
	code that re-sets a grey at run time (the top bar's idle buttons)."""
	return raise_dim(c) if _hc_on else c


static func toned_hex(hex: String) -> String:
	"""A BBCode grey as High contrast would draw it (the same hex when off) —
	for a literal grey written straight into a string."""
	return raise_dim(Color(hex)).to_html(false) if _hc_on else hex


static func apply_contrast(tree: SceneTree = null) -> void:
	"""Re-tone the BBCode tokens from the stored setting; with a tree, hook
	(or unhook) `node_added` and re-tone every node already in it."""
	_hc_on = UiSettings.get_high_contrast()
	COLOR_DIM = toned_hex("666670")
	COLOR_DIMMED = toned_hex("808080")
	COLOR_GREY = toned_hex("808080")
	COLOR_INFO = toned_hex("a0a0a8")
	if tree == null:
		return
	var hook := Callable(Utils, "_on_node_added_contrast")
	if _hc_on and not tree.node_added.is_connected(hook):
		tree.node_added.connect(hook)
	elif not _hc_on and tree.node_added.is_connected(hook):
		tree.node_added.disconnect(hook)
	apply_contrast_to(tree.root)


static func _on_node_added_contrast(node: Node) -> void:
	# Deferred: a node's builder often sets its colour right after add_child.
	Callable(Utils, "contrast_node").call_deferred(node)


static func apply_contrast_to(root: Node) -> void:
	if root == null:
		return
	contrast_node(root)
	for child in root.get_children():
		apply_contrast_to(child)


static func contrast_node(node) -> void:
	"""THE chokepoint: a Control's grey font-colour override raised (the
	original kept in meta, so turning High contrast off restores it)."""
	if not (node is Control) or not is_instance_valid(node):
		return
	var c := node as Control
	for key in ["font_color", "default_color"]:
		var meta: String = "hc_" + key
		if _hc_on:
			if c.has_theme_color_override(key) and not c.has_meta(meta):
				var orig: Color = c.get_theme_color(key)
				var up := raise_dim(orig)
				if up != orig:
					c.set_meta(meta, orig)
					c.add_theme_color_override(key, up)
		elif c.has_meta(meta):
			c.add_theme_color_override(key, c.get_meta(meta))
			c.remove_meta(meta)


# === Display settings (UXR-1b, October 9, 2026) ===

static func apply_window_settings(window: Window) -> void:
	"""Apply the stored window mode and size (Settings → DISPLAY) to the OS
	window. The project boots maximized (project.godot), so the default mode
	changes nothing; the other three are set here, at the menu's boot and on
	every change. NEVER under a capture / driven harness — it parked the
	window where it must stay (`UiSettings.harness_active`)."""
	if window == null or UiSettings.harness_active():
		return
	var mode := UiSettings.get_window_mode()
	var screen := window.current_screen
	var screen_size := DisplayServer.screen_get_size(screen)
	var screen_pos := DisplayServer.screen_get_position(screen)
	match mode:
		"fullscreen":
			window.borderless = false
			window.mode = Window.MODE_FULLSCREEN
		"borderless":
			# The usual "borderless full-screen window": windowed, no frame,
			# the screen's own size at its origin.
			window.mode = Window.MODE_WINDOWED
			window.borderless = true
			window.size = screen_size
			window.position = screen_pos
		"windowed":
			window.mode = Window.MODE_WINDOWED
			window.borderless = false
			var want := window_size_for(UiSettings.get_window_size(), screen_size)
			window.size = want
			window.position = screen_pos + (screen_size - want) / 2
		_:
			window.borderless = false
			window.mode = Window.MODE_MAXIMIZED


static func window_size_for(choice: String, screen_size: Vector2i) -> Vector2i:
	"""A Settings size choice → pixels, never larger than the screen."""
	var want := screen_size
	var parts := choice.split("x")
	if parts.size() == 2 and parts[0].is_valid_int() and parts[1].is_valid_int():
		want = Vector2i(int(parts[0]), int(parts[1]))
	return Vector2i(mini(want.x, screen_size.x), mini(want.y, screen_size.y))


static func window_size_choices(screen_size: Vector2i) -> Array:
	"""The size choices that fit this screen (native always)."""
	var out := []
	for choice in UiSettings.WINDOW_SIZES:
		var parts = choice.split("x")
		if parts.size() != 2:
			out.append(choice)
		elif int(parts[0]) <= screen_size.x and int(parts[1]) <= screen_size.y:
			out.append(choice)
	return out


const _PLAIN_BODY_REGULAR := "res://assets/fonts/SourceSans3[wght].ttf"
const _PLAIN_BODY_ITALIC := "res://assets/fonts/SourceSans3-Italic[wght].ttf"
static var _garamond_faces: Dictionary = {}


static func apply_body_font() -> void:
	"""Settings → INTERFACE → Body text: swap the project theme's body faces
	(the default font and the RichTextLabel's four) for Source Sans 3 — or
	back to the July design. Headings keep Cinzel; the menu's own faces and
	the map's labels are untouched. The theme resource is live: every control
	re-renders on its `changed` signal."""
	var theme: Theme = ThemeDB.get_project_theme()
	if theme == null:
		return
	if _garamond_faces.is_empty():
		_garamond_faces = {
			"default": theme.default_font,
			"bold": theme.get_font("bold_font", "RichTextLabel"),
			"italics": theme.get_font("italics_font", "RichTextLabel"),
			"bold_italics": theme.get_font("bold_italics_font", "RichTextLabel"),
		}
	if UiSettings.get_body_font() == "plain":
		var regular: Font = load(_PLAIN_BODY_REGULAR)
		var italic: Font = load(_PLAIN_BODY_ITALIC)
		if regular == null:
			return
		var bold := FontVariation.new()
		bold.base_font = regular
		bold.variation_opentype = {"wght": 700}
		var bold_italic := FontVariation.new()
		bold_italic.base_font = italic if italic != null else regular
		bold_italic.variation_opentype = {"wght": 700}
		theme.default_font = regular
		theme.set_font("normal_font", "RichTextLabel", regular)
		theme.set_font("bold_font", "RichTextLabel", bold)
		theme.set_font("italics_font", "RichTextLabel", italic if italic != null else regular)
		theme.set_font("bold_italics_font", "RichTextLabel", bold_italic)
	else:
		theme.default_font = _garamond_faces["default"]
		if theme.has_font("normal_font", "RichTextLabel"):
			theme.clear_font("normal_font", "RichTextLabel")
		theme.set_font("bold_font", "RichTextLabel", _garamond_faces["bold"])
		theme.set_font("italics_font", "RichTextLabel", _garamond_faces["italics"])
		theme.set_font("bold_italics_font", "RichTextLabel", _garamond_faces["bold_italics"])


# UXR-D1 (Pre-Deploy S9b): the theme's authored type sizes, captured once —
# "type|item" → [type, item, size] — and the factor last written over them.
static var _text_size_bases: Dictionary = {}
static var _text_size_default_base := 0
static var _text_size_applied := 1.0


# UXR-3 fixes (Pre-Deploy S12): the title screen's and the tableau's display
# type are named theme steps now (they were the RAW_RATCHET's exemptions), and
# Text size leaves them at their authored sizes, as it left the raw overrides:
# both are fixed-geometry art (a 96-px title, the engraved tableau).
const TEXT_SIZE_FIXED_STEPS := [
	"TitleScreen", "TitleScreenOverline", "TitleScreenLead", "TitleScreenHeader",
	"TitleScreenButton", "TitleScreenButtonProminent",
	"TableauClash", "TableauOdometer", "TableauBanner", "TableauPlate",
]


static func apply_text_size(preview := -1.0) -> void:
	"""Settings → INTERFACE → Text size: every named type size in the project
	theme — the default 16, the Label / Button / RichTextLabel / LineEdit
	sizes, and the ladder's steps (Caption 14 … DisplayTitleLarge 30) — times
	the stored factor (or `preview`, a slider step not yet persisted), from
	the AUTHORED sizes captured on the first call (so repeated changes never
	compound). One `merge_with` writes them all, so the controls re-theme
	once. No panel rect, no Interface Scale and no raw override moves: the
	eighteen named raw overrides (the map's furniture, the title screen's and
	the tableau's display type) keep their sizes. At the factor already
	applied it does nothing — 1.0 at boot is a no-op."""
	var factor := UiSettings.get_text_size() if preview < 0.0 else clampf(
			preview, UiSettings.MIN_TEXT_SIZE, UiSettings.MAX_TEXT_SIZE)
	if is_equal_approx(factor, _text_size_applied):
		return
	var theme: Theme = ThemeDB.get_project_theme()
	if theme == null:
		return
	if _text_size_bases.is_empty():
		_text_size_default_base = theme.default_font_size
		for theme_type in theme.get_font_size_type_list():
			if String(theme_type) in TEXT_SIZE_FIXED_STEPS:
				continue
			for item in theme.get_font_size_list(theme_type):
				_text_size_bases["%s|%s" % [theme_type, item]] = [
					theme_type, item, theme.get_font_size(item, theme_type)]
	var scaled := Theme.new()
	if _text_size_default_base > 0:
		scaled.default_font_size = text_px(_text_size_default_base, factor)
	for key in _text_size_bases:
		var row: Array = _text_size_bases[key]
		scaled.set_font_size(row[1], row[0], text_px(int(row[2]), factor))
	theme.merge_with(scaled)
	_text_size_applied = factor


static func text_size_factor() -> float:
	"""The Text size factor the theme carries now (1.0 at the shipped theme)."""
	return _text_size_applied


static func text_px(authored: int, factor := -1.0) -> int:
	"""An authored theme size at the Text size factor (the factor the theme
	carries now when none is given): the one rounding rule every scaled size
	shares."""
	var f := _text_size_applied if factor < 0.0 else factor
	return int(round(float(authored) * f))


# === Honest availability (UXR-3 fixes, Pre-Deploy S12) ===

const ACTIVE_TAB_TIP := "You are reading this book"


static func mark_active_tab(tab: Button, active: bool, active_style: StyleBox) -> void:
	"""UXR3-37 / UXR3-43 (Pre-Deploy S12): a control that cannot act is
	disabled, with its reason. The open book's tab is selected AND disabled —
	pressing it answered nothing — with "You are reading this book" as its
	tooltip; it keeps the selected look (the active fill, its own text
	colour), never the greyed disabled one, and the arrow cursor."""
	if tab == null:
		return
	if not tab.has_meta("_tab_tip"):
		tab.set_meta("_tab_tip", tab.tooltip_text)
		tab.set_meta("_tab_cursor", tab.mouse_default_cursor_shape)
	tab.disabled = active
	if active:
		tab.add_theme_stylebox_override("disabled", active_style)
		tab.add_theme_color_override("font_disabled_color", tab.get_theme_color("font_color"))
		tab.tooltip_text = ACTIVE_TAB_TIP
		tab.mouse_default_cursor_shape = Control.CURSOR_ARROW
	else:
		tab.tooltip_text = str(tab.get_meta("_tab_tip"))
		tab.mouse_default_cursor_shape = int(tab.get_meta("_tab_cursor"))


static func set_available(button: BaseButton, available: bool, tip_on: String, tip_off: String) -> void:
	"""UXR-3 fixes (S12): a control that cannot act in the current state is
	DISABLED, its reason the tooltip; when it can, it carries its own tip.
	Writes only on change, so a caller may run it every frame the state moves."""
	if button == null:
		return
	if button.disabled == available:
		button.disabled = not available
	var tip := tip_on if available else tip_off
	if button.tooltip_text != tip:
		button.tooltip_text = tip


# === Layout Helpers ===

static func shrink_centered_panel_to_content(panel: Control) -> void:
	"""SF7-X27's fit as one helper (Pre-Deploy S12, UXR3-X2): after the
	clamp, a centre-anchored popup shrinks to the height its content needs —
	never past the clamp (it only ever SHRINKS) — and stays centred. The
	objection and capture dialogs were authored as fixed rects, so a two-line
	question sat over a band of empty panel below its buttons.

	A coroutine: it waits two frames for the containers to sort (the frame
	the text is set, a wrapping label has no width yet and its minimum is
	thousands of px tall — the interrupt popup measured this). Call it after
	`clamp_centered_panel`, without awaiting."""
	if panel == null:
		return
	await panel.get_tree().process_frame
	await panel.get_tree().process_frame
	if not is_instance_valid(panel) or not panel.visible:
		return
	var have: float = panel.offset_bottom - panel.offset_top
	var need: float = panel.get_combined_minimum_size().y
	if need > 0.0 and need < have:
		panel.offset_top = -need / 2.0
		panel.offset_bottom = need / 2.0


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
	# UXR-2 (October 12, 2026): the player's remembered size — set by a
	# ResizeGrip, larger or smaller than authored — REPLACES the authored
	# rect; the per-state override below may still raise it and the viewport
	# caps below still fit it. `design_size` stays the authored rect (the
	# size a double-click or Reset layout returns to).
	if panel.has_meta("clamp_user_size"):
		design = panel.get_meta("clamp_user_size")
	# IGR-G1: a caller may raise the ceiling for ONE surface without touching
	# the authored rect every other dialogue type shares. The settlement
	# authoring screen (proposal_confirm_popup, dtype settlement_confirm) sets
	# this meta per-open and REMOVES it for every other dtype — the cached
	# design_size stays the ceiling for the other ~27 call sites, so their
	# rendering is byte-unchanged. A meta (not a parameter) because the exact
	# call string `Utils.clamp_centered_panel($PanelContainer)` is pinned
	# across every centre-anchored surface by test_ui_visual_foundation.py.
	if panel.has_meta("clamp_ceiling_override"):
		var override: Vector2 = panel.get_meta("clamp_ceiling_override")
		design = Vector2(maxf(design.x, override.x), maxf(design.y, override.y))
	var view: Vector2 = viewport.get_visible_rect().size
	var w: float = minf(design.x, maxf(320.0, view.x - 24.0))
	var h: float = minf(design.y, maxf(240.0, view.y - 88.0 - 2.0 * top_bar_growth()))
	panel.offset_left = -w / 2.0
	panel.offset_right = w / 2.0
	panel.offset_top = -h / 2.0
	panel.offset_bottom = h / 2.0
	_relax_child_minimums(panel, h)



# ── the ANCHORED half of the layout law (UXR-2 Slice D, October 12, 2026) ──
# The top bar's height — the one number every HUD surface keeps clear of:
# the command window's reserve (main.gd TOP_BAR_RESERVED_PX 36), the region
# panel's dock (48 = 36 + 12), the tutor card's top (44 = 36 + 8), the rail
# slot's top (42 = 36 + 6) and the centre clamp's vertical reserve (88 =
# 2 x (36 + 8)). The layout-law census pins each authored number to it.
const TOP_BAR_HEIGHT := 36.0
const HUD_MARGIN := 8.0
# UXR-D1 (Pre-Deploy S9b): the bar's DRAWN height, published by top_bar.gd.
# Its one line of buttons grows with Text size (45 px at 150 %), so every
# number above clears TOP_BAR_HEIGHT + top_bar_growth(); 0 at 100 %.
static var _top_bar_drawn := TOP_BAR_HEIGHT


static func top_bar_growth() -> float:
	"""How far the top bar's drawn strip stands below its authored height."""
	return maxf(_top_bar_drawn - TOP_BAR_HEIGHT, 0.0)


static func set_top_bar_drawn(height: float) -> bool:
	"""top_bar.gd's report of its strip's drawn height; true when it moved."""
	if is_equal_approx(height, _top_bar_drawn):
		return false
	_top_bar_drawn = height
	return true


static func hud_band(view: Vector2) -> Vector2:
	"""UXR-D3 (Pre-Deploy S9b): the HUD's horizontal band, (left, right) in
	logical px. Full: the whole viewport. Centred: UiSettings.HUD_BAND_WIDTH
	about the viewport's centre — on a viewport wider than the band and its
	margins only; a narrower one reads as Full. Every HUD surface measures
	its edge inset and its fraction from this band, never from 0 / view.x."""
	if UiSettings.get_hud_width() == "centred" \
			and view.x > UiSettings.HUD_BAND_WIDTH + 2.0 * HUD_MARGIN:
		var left := floorf((view.x - UiSettings.HUD_BAND_WIDTH) / 2.0)
		return Vector2(left, left + UiSettings.HUD_BAND_WIDTH)
	return Vector2(0.0, view.x)


static func fraction_px(view_len: float, frac: float, min_px: float, max_px: float,
		reserve: float = 16.0) -> float:
	"""An ANCHORED surface's extent: a fraction of the logical viewport
	between a floor and a ceiling (logical px) — and never more than the room
	the viewport leaves (`view_len - reserve`), so a floor cannot push a HUD
	panel off a narrow screen."""
	return minf(clampf(view_len * frac, min_px, max_px), maxf(view_len - reserve, 0.0))


static func clamp_anchored_panel(panel: Control) -> void:
	"""The edge-anchored twin of `clamp_centered_panel` (whose centre-only
	anchor guard is pinned and stays). On each axis whose anchors meet at a
	point, the extent is capped to the band the viewport leaves — x in
	[HUD_MARGIN, view.x - HUD_MARGIN], y in [TOP_BAR_HEIGHT + HUD_MARGIN,
	view.y - HUD_MARGIN] — keeping the edge its grow direction holds; the
	descendant height minimums relax to that height (the centre clamp's own
	second pass, so a Container cannot override it); and the rect is slid
	back inside the band, so its header never sits under the top bar."""
	if panel == null or not is_instance_valid(panel):
		return
	var viewport := panel.get_viewport()
	if viewport == null:
		return
	var view: Vector2 = viewport.get_visible_rect().size
	var band_top := TOP_BAR_HEIGHT + top_bar_growth() + HUD_MARGIN
	var max_h := maxf(view.y - band_top - HUD_MARGIN, 0.0)
	# UXR-D3: x lives in the HUD band (the whole width at Full).
	var band := hud_band(view)
	var max_w := maxf(band.y - band.x - 2.0 * HUD_MARGIN, 0.0)
	var w := minf(panel.offset_right - panel.offset_left, max_w)
	var h := minf(panel.offset_bottom - panel.offset_top, max_h)
	_relax_child_minimums(panel, h)
	# A Container grows to its combined minimum whatever its offsets say:
	# place (and slide) by the size it will really draw at, within the band.
	var drawn := panel.get_combined_minimum_size()
	w = maxf(w, minf(drawn.x, max_w))
	h = maxf(h, minf(drawn.y, max_h))
	if is_equal_approx(panel.anchor_left, panel.anchor_right):
		match panel.grow_horizontal:
			Control.GROW_DIRECTION_BEGIN:
				panel.offset_left = panel.offset_right - w
			Control.GROW_DIRECTION_END:
				panel.offset_right = panel.offset_left + w
			_:
				var cx := (panel.offset_left + panel.offset_right) / 2.0
				panel.offset_left = cx - w / 2.0
				panel.offset_right = cx + w / 2.0
	if is_equal_approx(panel.anchor_top, panel.anchor_bottom):
		match panel.grow_vertical:
			Control.GROW_DIRECTION_BEGIN:
				panel.offset_top = panel.offset_bottom - h
			Control.GROW_DIRECTION_END:
				panel.offset_bottom = panel.offset_top + h
			_:
				var cy := (panel.offset_top + panel.offset_bottom) / 2.0
				panel.offset_top = cy - h / 2.0
				panel.offset_bottom = cy + h / 2.0
	# Slide inside the band (a point anchor adds its own position to the offsets).
	var left := panel.anchor_left * view.x + panel.offset_left
	var top := panel.anchor_top * view.y + panel.offset_top
	var dx := 0.0
	var dy := 0.0
	if left + w > band.y - HUD_MARGIN:
		dx = (band.y - HUD_MARGIN) - (left + w)
	if left + dx < band.x + HUD_MARGIN:
		dx = band.x + HUD_MARGIN - left
	if top + h > view.y - HUD_MARGIN:
		dy = (view.y - HUD_MARGIN) - (top + h)
	if top + dy < band_top:
		dy = band_top - top
	panel.offset_left += dx
	panel.offset_right += dx
	panel.offset_top += dy
	panel.offset_bottom += dy


static func refit_surface(host: Node) -> void:
	"""UXR-2: the one live-refit road's per-surface step. Every clamped
	surface used to fit the viewport ON OPEN only, so raising the Interface
	Scale (Ctrl+=, the pause slider) or resizing the window under an open
	ledger or popup left it at the old size — its header could leave the
	screen. `main._on_root_resized` now refits every OPEN surface: a surface
	with its own fit (`refit()`: the wizard, the diorama, the interrupt and
	petition popups) runs it; any other re-clamps its PanelContainer (the
	clamp's anchor guard leaves an edge-anchored panel to its own fit)."""
	if host == null or not is_instance_valid(host):
		return
	if host.has_method("refit"):
		host.refit()
		return
	var panel := host.get_node_or_null("PanelContainer") as Control
	if panel != null:
		clamp_centered_panel(panel)


static func bound_rich_body(body: RichTextLabel, room: float, min_height: float) -> void:
	"""UXR-2 part 5 (October 12, 2026) — the rule the docstring above states:
	a `fit_content` RichTextLabel outside any ScrollContainer imposes its
	height through its text, so no clamp can bound it. This bounds it: content
	that fits `room` keeps `fit_content` (no scrollbar, no reserved space);
	content past it becomes a scrolling body `room` tall, never under
	`min_height`. The tutor card's toggle (UXR-X3) as one helper — call it
	deferred, once the body's width has settled, and again on a resize."""
	if body == null or not is_instance_valid(body):
		return
	var budget := maxf(room, min_height)
	if float(body.get_content_height()) <= budget:
		body.fit_content = true
		body.scroll_active = false
		body.custom_minimum_size.y = 0.0
	else:
		body.fit_content = false
		body.scroll_active = true
		body.custom_minimum_size.y = budget


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
		# IGR-G1: the old pass distributed proportional to headroom, which
		# charged the LARGEST floor the largest share — the settlement
		# per-court table (the primary content, 320px authored floor) was
		# robbed hardest precisely because it declared the biggest minimum.
		# A control tagged `relax_last` (the caller marks its primary
		# content) now yields only when every untagged control is already
		# at the floor — secondary rails give first, the document last.
		var room: float = 0.0
		var givers: Array = []
		for control in flexible:
			if control.has_meta("relax_last"):
				continue
			var headroom: float = control.custom_minimum_size.y - _RELAX_FLOOR
			if headroom > 0.5:
				givers.append(control)
				room += headroom
		if givers.is_empty() or room <= 0.0:
			for control in flexible:
				if not control.has_meta("relax_last"):
					continue
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
