extends PopupBase

# =============================================================================
# INK & IRON — The End Screen (row EP, GE-2 "the client"; ENDGAME_PLAN §4)
# =============================================================================
# ONE scene, FOUR registers, fed by ONE backend payload — `game_end.
# screen_payload(record)`: {kind, cause, register, title, cause_line, turn,
# calendar_label, terminal, tier, tier_title, summary}. The client never
# recomputes any of it: every figure and every sentence on this card is the
# backend's, taken at the moment the ending was stamped.
#
#   fall            crimson      THE FALL OF THE EMPIRE — the cause line, the
#                                exile epilogue (`summary.epilogue`), the
#                                record, the eclipse. TERMINAL: [Load a
#                                campaign] / [Main Menu]; the command line
#                                never reopens (main.gd keeps it closed).
#   humbled_peace   crimson-grey THE HUMBLED PEACE — the treaty's terms (the
#                                "signed" epilogue), the record, the tier.
#                                [Continue].
#   verdict         parchment    THE VERDICT OF HISTORY — the tier and its
#                                three lines. [Continue].
#   imperial_peace  gold         THE IMPERIAL PEACE (GE-3's; the scene takes
#                                it now) — [Continue the reign] / [Retire to
#                                the Tuileries].
#
# Raised by main.gd through the NA-6b stash-and-raise discipline: stashed the
# moment a response arrives (`_stash_ending`), shown where control would
# otherwise return (`_show_pending_ending`), never above the response that
# carried it — the turn's report, the battle, the enemy phase all render
# first. Choice-less on the marked registers (Continue hands control back);
# on the Fall the two buttons are the only roads left (R3).
# CanvasLayer 122: above the diorama (121) and the pause menu (120).
# =============================================================================

signal continued            # a MARKED ending acknowledged — play goes on
signal load_requested       # the Fall: Load a campaign
signal main_menu_requested  # the Fall: Main Menu · the Peace: Retire to the Tuileries

const FONT_ENGRAVED := "res://assets/fonts/Cinzel[wght].ttf"
const FONT_VOICE := "res://assets/fonts/IMFeENrm28P.ttf"
const FONT_VOICE_ITALIC := "res://assets/fonts/IMFeENit28P.ttf"

# The register owns the colours, the sound and the buttons. Hex strings are
# bbcode colours (Utils.bbcode_color); Colors paint the panel.
const REGISTER_STYLE := {
	"fall": {
		"title": "THE FALL OF THE EMPIRE",
		"title_hex": "cd6b6b",          # Utils.COLOR_ERROR
		"border": Color(0.58, 0.14, 0.14, 1.0),
		"bg": Color(0.10, 0.045, 0.055, 1.0),
		"overlay": Color(0.06, 0.0, 0.0, 0.88),
		"cue": "bell_toll",
		"primary": "Load a campaign",
		"secondary": "Main Menu",
	},
	"humbled_peace": {
		"title": "THE HUMBLED PEACE",
		"title_hex": "b89090",
		"border": Color(0.46, 0.25, 0.27, 1.0),
		"bg": Color(0.11, 0.085, 0.095, 1.0),
		"overlay": Color(0.04, 0.03, 0.035, 0.86),
		"cue": "quill_sign",
		"primary": "Continue",
		"secondary": "",
	},
	"verdict": {
		"title": "THE VERDICT OF HISTORY",
		"title_hex": "d9c08c",          # Utils.COLOR_GOLD
		"border": Color(0.66, 0.56, 0.38, 1.0),
		"bg": Color(0.17, 0.15, 0.11, 1.0),
		"overlay": Color(0.0, 0.0, 0.0, 0.82),
		"cue": "parchment_open",
		"primary": "Continue",
		"secondary": "",
	},
	"imperial_peace": {
		"title": "THE IMPERIAL PEACE",
		"title_hex": "f0e0b0",          # Utils.UI_GOLD_BRIGHT
		"border": Color(0.851, 0.753, 0.549, 1.0),
		"bg": Color(0.13, 0.11, 0.06, 1.0),
		"overlay": Color(0.02, 0.02, 0.0, 0.86),
		"cue": "fanfare",
		"primary": "Continue the reign",
		"secondary": "Retire to the Tuileries",
	},
}

# The exile block's heading follows the epilogue's variant.
const EPILOGUE_HEADINGS := {
	"captivity": "THE EXILE",
	"abdication": "THE EXILE",
	"funeral": "THE FUNERAL",
	"humbled": "THE PEACE",
}

@onready var overlay = $BackgroundOverlay
@onready var panel = $PanelContainer
@onready var title_label = $PanelContainer/VBoxContainer/TitleLabel
@onready var date_label = $PanelContainer/VBoxContainer/DateLabel
@onready var cause_label = $PanelContainer/VBoxContainer/CauseLabel
@onready var content_label = $PanelContainer/VBoxContainer/ContentScroll/ContentLabel
@onready var content_scroll = $PanelContainer/VBoxContainer/ContentScroll
@onready var primary_btn = $PanelContainer/VBoxContainer/ButtonContainer/PrimaryButton
@onready var secondary_btn = $PanelContainer/VBoxContainer/ButtonContainer/SecondaryButton

var _payload: Dictionary = {}
var _register: String = "verdict"
var _font_engraved: Font = null
var _font_voice: Font = null
var _font_voice_italic: Font = null


func _ready():
	hide()
	primary_btn.pressed.connect(_on_primary_pressed)
	secondary_btn.pressed.connect(_on_secondary_pressed)
	# PC15-18 (NV-P1 family census): a fit_content RichTextLabel inside a
	# ScrollContainer defaults to MOUSE_FILTER_STOP and eats the wheel
	# before its parent can scroll. PASS still delivers _gui_input.
	content_label.mouse_filter = Control.MOUSE_FILTER_PASS
	_load_fonts()


func _load_fonts() -> void:
	if ResourceLoader.exists(FONT_ENGRAVED):
		_font_engraved = load(FONT_ENGRAVED)
	if ResourceLoader.exists(FONT_VOICE):
		_font_voice = load(FONT_VOICE)
	if ResourceLoader.exists(FONT_VOICE_ITALIC):
		_font_voice_italic = load(FONT_VOICE_ITALIC)
	if _font_engraved != null:
		title_label.add_theme_font_override("font", _font_engraved)
		# [b] in the body = the engraved capitals of a section heading.
		content_label.add_theme_font_override("bold_font", _font_engraved)
	if _font_voice != null:
		cause_label.add_theme_font_override("font", _font_voice)
		content_label.add_theme_font_override("normal_font", _font_voice)
		content_label.add_theme_font_size_override("normal_font_size", 17)
		content_label.add_theme_font_size_override("bold_font_size", 15)
	if _font_voice_italic != null:
		content_label.add_theme_font_override("italics_font", _font_voice_italic)
		content_label.add_theme_font_size_override("italics_font_size", 17)


# ── the entry ────────────────────────────────────────────────────────────────

func register_of(payload: Dictionary) -> String:
	"""The register the payload names, or the one its title implies; a
	payload the table does not know renders on the parchment (a marked
	ending is never mistaken for the Fall)."""
	var reg := str(payload.get("register", ""))
	if REGISTER_STYLE.has(reg):
		return reg
	if bool(payload.get("terminal", false)):
		return "fall"
	return "verdict"


func show_ending(payload: Dictionary) -> void:
	"""Render the ending and raise the card. The payload is
	`game_end.screen_payload` (the compact view + `summary`)."""
	_payload = payload.duplicate(true) if payload != null else {}
	_register = register_of(_payload)
	var style: Dictionary = REGISTER_STYLE[_register]
	_apply_style(style)
	claim_cue(AudioManager.play(str(style["cue"])))  # UX23-R1: leaves with the card
	_render(style)
	_arm_buttons(style)
	show()
	# Fit to the CURRENT logical viewport (Interface Scale can halve it).
	# A card whose only buttons leave the screen is unrecoverable, so this
	# runs after show(), once layout has settled.
	Utils.clamp_centered_panel($PanelContainer)
	content_scroll.scroll_vertical = 0


func reraise() -> void:
	"""Show the card again without re-ringing it — the Fall's card after a
	cancelled Load, when the campaign is still over and the two roads are
	still the only ones."""
	if _payload.is_empty():
		return
	_arm_buttons(REGISTER_STYLE[_register])
	show()
	Utils.clamp_centered_panel($PanelContainer)


func is_terminal() -> bool:
	return bool(_payload.get("terminal", false))


func current_register() -> String:
	return _register


# ── rendering ────────────────────────────────────────────────────────────────

func _apply_style(style: Dictionary) -> void:
	var box := StyleBoxFlat.new()
	box.bg_color = style["bg"]
	box.border_color = style["border"]
	box.set_border_width_all(3)
	box.set_corner_radius_all(8)
	box.content_margin_left = 30.0
	box.content_margin_right = 30.0
	box.content_margin_top = 26.0
	box.content_margin_bottom = 24.0
	panel.add_theme_stylebox_override("panel", box)
	overlay.color = style["overlay"]
	title_label.add_theme_color_override("font_color", Color("#" + str(style["title_hex"])))


func _render(style: Dictionary) -> void:
	var summary: Dictionary = _payload.get("summary", {}) if _payload.get("summary") is Dictionary else {}
	var title := str(_payload.get("title", "")).strip_edges()
	if title == "":
		title = str(style["title"])
	title_label.text = title
	date_label.text = _date_line()
	cause_label.text = Utils.humanize_nation_keys_in_text(str(_payload.get("cause_line", "")))

	var bbcode := ""
	# 1. The epilogue — the exile / the funeral / the peace (the Fall and the
	#    Humbled Peace carry one; GE-1 builds it, every clause from the record).
	var epilogue = summary.get("epilogue")
	if epilogue is Dictionary and (epilogue.get("paragraphs") is Array) \
			and not (epilogue.get("paragraphs") as Array).is_empty():
		var variant := str(epilogue.get("variant", ""))
		bbcode += _heading(str(EPILOGUE_HEADINGS.get(variant, "THE EXILE")), style)
		for para in epilogue["paragraphs"]:
			bbcode += "[i]" + _esc(str(para)) + "[/i]\n\n"
	# 2. The Verdict — its own card on the parchment register, the closing
	#    block on the others.
	var verdict = summary.get("verdict")
	var verdict_block := _verdict_block(verdict, style)
	if _register == "verdict":
		bbcode += verdict_block
	# 2b. GE-3: the Imperial Peace's own block — the four courts with SIGNED /
	#     SHUT OUT / GONE, the titled count, the sitting's days (or the
	#     Universal Monarchy's line), from the ending's own detail.
	if _register == "imperial_peace":
		bbcode += _congress_block(summary.get("congress"), style)
	# 3. The record — the campaign's totals, taken at the moment.
	bbcode += _record_block(summary, style)
	if _register != "verdict":
		bbcode += verdict_block
	# 3b. GE-3: Le Moniteur's final line — the proclamation as printed.
	if _register == "imperial_peace":
		bbcode += _moniteur_line(summary)
	# 4. What comes next, in one line.
	bbcode += _what_now_line()
	content_label.text = ""
	content_label.append_text(Utils.humanize_nation_keys_in_text(bbcode))


func _date_line() -> String:
	var parts: Array = []
	var cal := str(_payload.get("calendar_label", "")).strip_edges()
	if cal != "":
		parts.append(cal)
	var turn := int(_payload.get("turn", 0))
	if turn > 0:
		parts.append("turn " + str(turn))
	return " · ".join(parts)


func _heading(text: String, style: Dictionary) -> String:
	return Utils.bbcode_color("[b]" + text + "[/b]", str(style["title_hex"])) + "\n"


func _verdict_block(verdict, style: Dictionary) -> String:
	if not (verdict is Dictionary) or verdict.is_empty():
		return ""
	var out := ""
	var tier_title := str(verdict.get("title", "")).strip_edges()
	if _register == "verdict":
		# The card IS the Verdict: the tier reads as the heading.
		out += _heading(tier_title if tier_title != "" else "THE VERDICT", style)
	else:
		out += _heading("THE VERDICT OF HISTORY", style)
		if tier_title != "":
			out += Utils.bbcode_color(tier_title, Utils.COLOR_GOLD) + "\n"
	var lines = verdict.get("lines", [])
	if lines is Array:
		for ln in lines:
			out += _esc(str(ln)) + "\n"
	var closing := str(verdict.get("closing", "")).strip_edges()
	if closing != "":
		out += "[i]" + _esc(closing) + "[/i]\n"
	return out + "\n"


func _record_block(summary: Dictionary, style: Dictionary) -> String:
	var totals = summary.get("totals", {})
	if not (totals is Dictionary):
		totals = {}
	var out := _heading("THE RECORD", style)
	var since = summary.get("record_since_turn")
	if since != null:
		out += Utils.bbcode_color("(The record was kept from turn " + str(int(since))
			+ " only.)", Utils.COLOR_DIMMED) + "\n"
	var held := int(summary.get("provinces_held", 0))
	var total := int(summary.get("total_regions", 0))
	if total > 0:
		out += "The realm at the end: " + Utils.plural(held, "province") + " of " + str(total) + ".\n"
	var fought := _n(totals, "battles_fought")
	if fought > 0:
		var won := _n(totals, "battles_won")
		var lost := _n(totals, "battles_lost")
		var drawn := _n(totals, "battles_drawn")
		var line := "Battles fought: " + str(fought) + " — won " + str(won) + ", lost " + str(lost)
		if drawn > 0:
			line += ", drawn " + str(drawn)
		var in_person := _n(totals, "battles_in_person")
		if in_person > 0:
			line += " (" + str(in_person) + " with the Emperor present)"
		out += line + ".\n"
		out += "Men lost: " + Utils.format_number(_n(totals, "men_lost")) \
			+ " · men inflicted: " + Utils.format_number(_n(totals, "men_inflicted")) + ".\n"
	else:
		out += "No battle was fought.\n"
	var taken := _n(totals, "provinces_taken")
	var lost_p := _n(totals, "provinces_lost")
	var ceded := _n(totals, "provinces_ceded")
	var gained := _n(totals, "provinces_gained_by_treaty")
	var prov := "Provinces taken: " + str(taken) + " · lost: " + str(lost_p)
	if ceded > 0 or gained > 0:
		prov += " · ceded by treaty: " + str(ceded) + " · gained by treaty: " + str(gained)
	out += prov + ".\n"
	var marshal_bits: Array = []
	if _n(totals, "marshals_fallen") > 0:
		marshal_bits.append(Utils.plural(_n(totals, "marshals_fallen"), "marshal") + " fallen")
	if _n(totals, "own_marshals_taken") > 0:
		marshal_bits.append(str(_n(totals, "own_marshals_taken")) + " taken")
	if _n(totals, "enemy_marshals_taken") > 0:
		marshal_bits.append(str(_n(totals, "enemy_marshals_taken")) + " of the enemy's taken")
	if _n(totals, "enemy_corps_destroyed") > 0:
		marshal_bits.append(Utils.plural(_n(totals, "enemy_corps_destroyed"), "enemy corps") + " destroyed")
	if not marshal_bits.is_empty():
		out += "Marshals: " + ", ".join(marshal_bits) + ".\n"
	var coalitions := _n(totals, "coalitions_faced")
	var names = summary.get("coalition_names", [])
	var coal_line := "Coalitions faced: " + str(coalitions)
	if names is Array and not names.is_empty():
		var shown: Array = []
		for nm in names:
			shown.append(_esc(str(nm)))
		coal_line += " (" + ", ".join(shown) + ")"
	var peaces := _n(totals, "peaces_signed")
	out += coal_line + " · peaces signed: " + str(peaces) + ".\n"
	var best = summary.get("greatest_victory")
	if best is Dictionary and not best.is_empty():
		out += "Greatest victory: " + _battle_line(best, "inflicted") + "\n"
	var worst = summary.get("worst_defeat")
	if worst is Dictionary and not worst.is_empty():
		out += "Worst defeat: " + _battle_line(worst, "suffered") + "\n"
	return out + "\n"


# GE-3: the stances the Imperial Peace counts as answered, and their ink on
# the gold card (the ledger's CONGRESS tab uses the same colours).
const CONGRESS_SATISFIED := ["RECOGNIZES", "SHUT OUT", "GONE"]


func _congress_stance_hex(stance: String) -> String:
	match stance:
		"SIGNED", "RECOGNIZES":
			return Utils.COLOR_SUCCESS
		"SHUT OUT":
			return "8fa3b8"
		"REFUSES":
			return Utils.COLOR_ERROR
	return Utils.COLOR_GREY


func _congress_block(congress, style: Dictionary) -> String:
	"""GE-3 (ENDGAME_PLAN §4): the Imperial Peace's block — built by the
	backend from the ending's OWN detail (`congress.summary_block`), never
	from live state. A Peace with no Congress behind it (the GE-2 staged
	preview: no courts, no route) renders nothing here."""
	if not (congress is Dictionary):
		return ""
	var route_v = congress.get("route")
	var route: String = route_v if route_v is String else "congress"
	var courts = congress.get("courts")
	var have_courts: bool = courts is Array and not (courts as Array).is_empty()
	if not have_courts and route != "universal_monarchy":
		return ""
	var out := ""
	if route == "universal_monarchy":
		out += _heading("THE UNIVERSAL MONARCHY", style)
		out += "No great power remains to contest the order.\n"
	else:
		out += _heading("THE CONGRESS OF PARIS", style)
		var number := _n(congress, "number")
		if number > 1:
			out += Utils.bbcode_color("Summoned " + str(number) + " times before Europe signed.", Utils.COLOR_DIMMED) + "\n"
		for row in courts:
			if not (row is Dictionary):
				continue
			var nation_v = row.get("nation")
			var nation: String = nation_v if nation_v is String else ""
			var display_v = row.get("display")
			var display: String = display_v if display_v is String and display_v != "" else Utils.display_nation_name(nation)
			var stance_v = row.get("stance")
			var stance: String = stance_v if stance_v is String else ""
			out += Utils.bb_flag(nation, 18) + _esc(display) + " — " \
				+ Utils.bbcode_color(stance, _congress_stance_hex(stance)) + "\n"
	var hold := _n(congress, "hold_titled")
	if hold > 0:
		# GE-3 review #59: the titled count is the BLOC's (the Empire and its
		# satellites), while THE RECORD's realm line counts France alone —
		# the card says so rather than print 50 beside 43 unexplained.
		out += str(_n(congress, "titled")) + " of " + str(hold) + " titled provinces in the Empire and its satellites.\n"
	var sitting = congress.get("sitting")
	if sitting is Array and not (sitting as Array).is_empty():
		out += "\n" + _heading("THE SITTING", style)
		out += _sitting_strip(sitting)
	return out + "\n"


func _sitting_strip(rows: Array) -> String:
	"""The sitting's days as a strip — one cell per day: the hold (✓ held /
	✗ broke) and how many courts had answered (recognizes / shut out / gone)
	at that end turn, off the backend's per-turn record."""
	var days: Array = []
	for row in rows:
		if row is Dictionary:
			days.append(row)
	if days.is_empty():
		return ""
	var out := "[table=" + str(days.size() + 1) + "]"
	out += "[cell]" + Utils.bbcode_color("Day  ", Utils.COLOR_DIMMED) + "[/cell]"
	for row in days:
		out += "[cell] " + str(_n(row, "day")) + " [/cell]"
	out += "[cell]" + Utils.bbcode_color("Hold  ", Utils.COLOR_DIMMED) + "[/cell]"
	for row in days:
		var held: bool = row.get("held") is bool and row.get("held")
		out += "[cell]" + Utils.bbcode_color(" ✓ " if held else " ✗ ",
			Utils.COLOR_SUCCESS if held else Utils.COLOR_ERROR) + "[/cell]"
	out += "[cell]" + Utils.bbcode_color("Signed  ", Utils.COLOR_DIMMED) + "[/cell]"
	for row in days:
		var stances = row.get("stances")
		if stances is Dictionary and not (stances as Dictionary).is_empty():
			var answered := 0
			for court in stances:
				if str(stances[court]) in CONGRESS_SATISFIED:
					answered += 1
			out += "[cell] " + str(answered) + "/" + str((stances as Dictionary).size()) + " [/cell]"
		else:
			out += "[cell] [/cell]"
	return out + "[/table]\n"


func _moniteur_line(summary: Dictionary) -> String:
	"""GE-3: Le Moniteur's final line — the proclamation as the paper printed
	it (`summary.moniteur_line`, stamped with the ending)."""
	var line = summary.get("moniteur_line")
	if not (line is String) or line == "":
		return ""
	return "[i]" + Utils.bbcode_color(_esc(line), Utils.COLOR_GOLD) + "[/i]\n\n"


func _battle_line(row: Dictionary, key: String) -> String:
	var name := _esc(str(row.get("name", "the fighting")))
	var line := name
	var turn := int(row.get("turn", 0))
	if turn > 0:
		line += " (turn " + str(turn) + ")"
	var figure := int(row.get(key, 0))
	if figure > 0:
		line += " — " + Utils.format_number(figure) + (" of the enemy fell." if key == "inflicted" else " of our own fell.")
	else:
		line += "."
	return line


func _what_now_line() -> String:
	match _register:
		"fall":
			return Utils.bbcode_color("[i]The campaign is over. Load another, or return to the Main Menu.[/i]", Utils.COLOR_DIMMED)
		"humbled_peace":
			return Utils.bbcode_color("[i]The reign goes on, under the terms every court in Europe has read. The Verdict of History will grade it as an eclipse.[/i]", Utils.COLOR_DIMMED)
		"imperial_peace":
			return Utils.bbcode_color("[i]The order of the French Empire stands. Continue the reign, or retire to the Tuileries.[/i]", Utils.COLOR_DIMMED)
		_:
			return Utils.bbcode_color("[i]The reign goes on; the Empire can still fall.[/i]", Utils.COLOR_DIMMED)


func _n(totals: Dictionary, key: String) -> int:
	var v = totals.get(key, 0)
	if v == null:
		return 0
	return int(v)


func _esc(text: String) -> String:
	# The record's names come from the world; a bracket in one must not open
	# a bbcode tag.
	return text.replace("[", "[lb]")


# ── the buttons ──────────────────────────────────────────────────────────────

func _arm_buttons(style: Dictionary) -> void:
	primary_btn.text = str(style["primary"])
	primary_btn.disabled = false
	primary_btn.visible = true
	var secondary := str(style["secondary"])
	secondary_btn.text = secondary
	secondary_btn.visible = secondary != ""
	secondary_btn.disabled = secondary == ""


func esc_control() -> Button:
	# FA-94: a marked ending is read-and-dismiss — ESC presses Continue. The
	# Fall's buttons leave the campaign; no reflex keypress takes them.
	if is_terminal():
		return null
	return primary_btn


func _on_primary_pressed() -> void:
	if is_terminal():
		close_popup()
		load_requested.emit()
		return
	close_popup()
	continued.emit()


func _on_secondary_pressed() -> void:
	close_popup()
	main_menu_requested.emit()
