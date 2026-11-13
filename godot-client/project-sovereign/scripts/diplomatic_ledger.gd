extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Diplomatic Ledger Screen (Session 8B)
# =============================================================================
# 7-section sub-tabbed screen. CanvasLayer 50.
# Tabs: NATIONS, TREATIES, BALANCE OF EUROPE, TALLEYRAND, WAR BARGAINS, VASSALS,
# CONGRESS
# Number keys 1-7 switch sub-tabs (guarded by visible check).
# Pattern follows strategic_ledger.gd.
# UI-6: the VASSALS tab renders per-vassal cards with honest-availability
# action chips (invest / autonomy / cede / release) — the chips send the same
# typed commands the parser accepts, or hand off to the F1 wizard for the
# cede province picker.
# GE-3 (ENDGAME_PLAN §2.4/§4): the CONGRESS tab renders the Congress of Paris's
# table from ONE backend payload (`congress.build_congress_payload`, the
# ledger's `congress` key) — the clock line, the summons' gate terms, the
# sitting's days and its hold, and every great power's stance, reason and
# price. It recomputes nothing and sends nothing: a court's card opens the
# Cabinet at that court (the existing `open_diplomacy_for` road).
# =============================================================================

signal closed
# UI-6: a vassal action chip — the typed command through main.gd's pipeline
# (history + terminal echo + refresh this ledger on result).
signal vassal_command(command: String)
# UI-6: [Cede Province…] — open the F1 wizard at this nation (its picker
# states each province's terms). GE-3: a CONGRESS-tab court card rides it too
# ("Open the Cabinet at Vienna").
signal open_diplomacy_for(nation: String)
# UI-6: Talleyrand tab [Assess the Situation] — the W6-9 counsel verb; main.gd
# closes the ledger first so the war room renders in the terminal.
signal assess_requested

# UI References — paths match scene tree
@onready var background_overlay = $BackgroundOverlay
@onready var close_button = $PanelContainer/VBoxContainer/HeaderRow/CloseButton
@onready var dp_display = $PanelContainer/VBoxContainer/HeaderRow/DPDisplay
@onready var scroll_container = $PanelContainer/VBoxContainer/ScrollContainer
@onready var content_area = $PanelContainer/VBoxContainer/ScrollContainer/ContentArea
@onready var nations_tab = $PanelContainer/VBoxContainer/SubTabRow/NationsTab
@onready var treaties_tab = $PanelContainer/VBoxContainer/SubTabRow/TreatiesTab
@onready var threat_tab = $PanelContainer/VBoxContainer/SubTabRow/ThreatTab
@onready var talleyrand_tab = $PanelContainer/VBoxContainer/SubTabRow/TalleyrandTab
@onready var bargains_tab = $PanelContainer/VBoxContainer/SubTabRow/BargainsTab
@onready var vassals_tab = $PanelContainer/VBoxContainer/SubTabRow/VassalsTab
@onready var congress_tab = $PanelContainer/VBoxContainer/SubTabRow/CongressTab

# File-specific colors (not in Utils)
const COLOR_AMBER = "d9a520"
# S12 (UXR3-33): cd5c5c read 4.41 : 1 on the ledger's navy; the same hue, lighter.
const COLOR_RED = "d16969"
# IQ-2 (Sept 14, 2026) flip lever — true: the Talleyrand tab's authority
# colour arms test the vocabulary the backend actually emits
# (`AuthorityTracker.get_authority_label`). false = the pre-IQ-2 arms, which
# never matched, byte-for-byte.
const AUTHORITY_ARMS_READ_THE_BACKEND := true

# State
var current_tab: int = 0  # 0=nations, 1=treaties, 2=threat, 3=talleyrand, 4=bargains, 5=vassals, 6=congress
# SF7-X24: Alt+1..7 turn the books while the command line holds the caret.
const ALT_TURNS_THE_BOOKS := true
var cached_data: Dictionary = {}
var tab_buttons: Array = []
var _open_review_target: String = ""
var _focus_settlement_route_id: String = ""
var _focus_settlement_war_id: String = ""
var _expanded_peace_ratifications: Dictionary = {}
# F2: inline expansion state for Recent Settlements rows. Keyed by the
# `settlement:<idx>:<route_id>` URL meta so the toggle survives a
# `_render_treaties()` rerender; cleared on close_view().
var _expanded_settlements: Dictionary = {}

# Active tab style
var _active_tab_style: StyleBoxFlat = null
var _normal_tab_style: StyleBoxFlat = null

# Threat pulse timer for CRITICAL tier
var _critical_pulse_timer: Timer = null
var _critical_pulsing: bool = false
var _pulse_state: bool = false

func _ready():
	# UXR3-F3: the reading scroll comes to rest on whole lines.
	Utils.keep_whole_lines(content_area)
	close_button.pressed.connect(close_view)
	Utils.apply_icon_only_button(close_button, Utils.ICON_PHOSPHOR + "x.svg")
	background_overlay.gui_input.connect(_on_overlay_input)
	# UXR-2: clamped AND gripped — the player's size is remembered (the
	# sixth screen: the user's ruling, October 12, 2026).
	ResizeGrip.attach_centered($PanelContainer, "diplomatic_ledger")
	content_area.meta_clicked.connect(_on_content_meta_clicked)
	# Session UI-3 (November 12, 2026): the Explanations switch re-renders the
	# open tab from the cached ledger, the scroll kept.
	Utils.on_explanations_changed(_rerender_keeping_scroll)
	# PC15-18 (NV-P1 family census): a fit_content RichTextLabel inside a
	# ScrollContainer defaults to MOUSE_FILTER_STOP and eats the wheel
	# before its parent can scroll. PASS keeps meta_clicked chips working.
	content_area.mouse_filter = Control.MOUSE_FILTER_PASS

	tab_buttons = [nations_tab, treaties_tab, threat_tab, talleyrand_tab, bargains_tab, vassals_tab, congress_tab]
	for i in range(tab_buttons.size()):
		tab_buttons[i].pressed.connect(_on_tab_pressed.bind(i))

	# Session UI (November 11, 2026): the ONE tab strip (`Utils.tab_styles`) —
	# a closed book is its words, the open book stands on a gilt underline.
	# The margins are this strip's own (6 / 3), so no tab moves.
	var strip := Utils.tab_styles(6.0, 3.0)
	_active_tab_style = strip["active"]
	_normal_tab_style = strip["normal"]
	for tab in tab_buttons:
		Utils.dress_tab(tab, strip)

	# Session UI: every court, treaty and client a card (the marks are in the
	# builders; `scripts/card_underlay.gd` paints them).
	Utils.card_page(content_area)

	# Critical threat pulse timer
	_critical_pulse_timer = Timer.new()
	_critical_pulse_timer.wait_time = 0.4
	_critical_pulse_timer.timeout.connect(_on_critical_pulse)
	add_child(_critical_pulse_timer)

	hide()


func _input(event):
	"""Handle number keys 1-7 for sub-tab switching. Only when visible."""
	if not visible:
		return
	# Aug 30, 2026 review: `visible` is not the whole question. `Node._input`
	# runs BEFORE GUI input reaches a focused control, so with any of these
	# screens open — and they are all non-modal, the terminal stays live
	# behind them — every bare digit typed into the command line was eaten
	# here and `set_input_as_handled()` stopped it ever arriving. The player
	# typed "recruit 5000 infantry" and got "recruit  infantry" plus a tab
	# switch. A digit belongs to whoever has the caret.
	var _focused = get_viewport().gui_get_focus_owner()
	# SF7-X24: Alt+digit is the focus-safe form (the strategic ledger's
	# twin); a bare digit still belongs to whoever has the caret.
	var _typing: bool = _focused is LineEdit or _focused is TextEdit
	if _typing and not (ALT_TURNS_THE_BOOKS and event is InputEventKey and event.alt_pressed):
		return
	if event is InputEventKey and event.pressed and not event.echo:
		var switched = true
		match event.keycode:
			KEY_1:
				_switch_tab(0)
			KEY_2:
				_switch_tab(1)
			KEY_3:
				_switch_tab(2)
			KEY_4:
				_switch_tab(3)
			KEY_5:
				_switch_tab(4)
			KEY_6:
				_switch_tab(5)
			KEY_7:
				_switch_tab(6)
			_:
				switched = false
		if switched:
			get_viewport().set_input_as_handled()


var _api_client_ref = null

# UXR3-77 (Pre-Deploy S12 part 2): the ledger's header names the Cabinet on
# every book — "Talleyrand: Idle", or his mission and its court — as the top
# bar does. The Cabinet block lived on the TALLEYRAND book alone, so six of
# the seven books could not show the state their boards were taken to check
# (IQ-4: never "None"). One Caption beside the DP figure, built in code.
var _cabinet_line: Label = null


func _set_cabinet_line(talleyrand_data) -> void:
	if _cabinet_line == null:
		var header = dp_display.get_parent()
		if header == null:
			return
		_cabinet_line = Label.new()
		_cabinet_line.name = "CabinetLine"
		_cabinet_line.theme_type_variation = &"Caption"
		_cabinet_line.add_theme_color_override("font_color", Utils.UI_GOLD)
		header.add_child(_cabinet_line)
		header.move_child(_cabinet_line, dp_display.get_index())
	var words := "Talleyrand: Idle"
	var mission = talleyrand_data.get("active_mission") if talleyrand_data is Dictionary else null
	if mission is Dictionary and not mission.is_empty():
		var kind := str(mission.get("type_display", ""))
		if kind == "":
			kind = str(mission.get("type", "")).replace("_", " ").capitalize()
		words = "Talleyrand: " + kind + " → " + Utils.display_nation_name(str(mission.get("target", "")))
		if bool(mission.get("paused", false)):
			words += " (paused)"
	_cabinet_line.text = words + "   "


func open(api_client):
	"""Fetch diplomatic ledger from backend and display it."""
	_open_with_tab(api_client, 0, "")


func open_to_commitments(api_client):
	"""Fetch diplomatic ledger and open the commitments review surface."""
	_open_with_tab(api_client, 1, "ledger_commitments")


func open_to_war_bargains(api_client):
	"""Fetch diplomatic ledger and open the war bargains tab."""
	_open_with_tab(api_client, 4, "ledger_war_bargains")


func open_to_vassals(api_client):
	"""Fetch diplomatic ledger and open the Vassals tab (UI-6 deep link)."""
	_open_with_tab(api_client, 5, "ledger_vassals")


func open_to_talleyrand(api_client):
	"""Fetch diplomatic ledger and open the TALLEYRAND tab (UXR3-2: the top
	bar's Cabinet chip)."""
	_open_with_tab(api_client, 3, "")


func open_to_balance(api_client):
	"""Session UI-2: the top bar's threat figure — the BALANCE OF EUROPE book."""
	_open_with_tab(api_client, 2, "")


func open_to_congress(api_client):
	"""Fetch diplomatic ledger and open the CONGRESS tab (GE-3 deep link —
	the wizard's 'View the table' and a `ledger_congress` review target)."""
	_open_with_tab(api_client, 6, "ledger_congress")


func refresh_if_open():
	"""Re-fetch and re-render in place after a vassal-chip command changed
	state (loyalty, DP, autonomy). No-op when the ledger is hidden — the
	marshal_management.refresh_if_open precedent."""
	if not visible or _api_client_ref == null:
		return
	_api_client_ref.get_diplomatic_ledger(_on_ledger_received)


func refresh_pinned() -> void:
	"""UXR-D4 (Pre-Deploy S12b): the Side Desk re-reads a pinned screen
	after every command and every end turn — its CURRENT book, its scroll where the
	reader left it."""
	if not visible or _api_client_ref == null:
		return
	_api_client_ref.get_diplomatic_ledger(_on_pinned_ledger.bind(scroll_container.scroll_vertical))


func _on_pinned_ledger(response, held_scroll: int) -> void:
	_on_ledger_received(response)
	Utils.restore_scroll(scroll_container, held_scroll)


func open_to_settlements(api_client, route_id: String = "", war_id: String = ""):
	"""Fetch diplomatic ledger and open the Treaties tab focused on the
	`Recent Settlements` section.

	Settlement review uses the existing Treaties sub-tab so we keep the
	one-screen-at-a-time CanvasLayer 50 rule and avoid a new tab; the
	`ledger_settlements` review target is recorded so the renderer
	highlights the settlements block.
	"""
	_open_with_tab(api_client, 1, "ledger_settlements", route_id, war_id)


func _open_with_tab(api_client, tab_index: int, review_target: String, route_id: String = "", war_id: String = ""):
	"""Fetch diplomatic ledger from backend and display a chosen tab."""
	_api_client_ref = api_client
	content_area.text = "[color=#" + Utils.COLOR_INFO + "]Loading diplomatic ledger...[/color]"
	current_tab = tab_index
	_open_review_target = review_target
	_focus_settlement_route_id = route_id
	_focus_settlement_war_id = war_id
	AudioManager.play("panel_open")
	show()
	# Session UI-3 (November 12, 2026): the book takes the room.
	Utils.set_reading_share($PanelContainer, Utils.BOOK_SHARE, Utils.BOOK_MAX)
	Utils.clamp_centered_panel($PanelContainer)
	_update_tab_highlights()
	api_client.get_diplomatic_ledger(_on_ledger_received)


func close_view():
	"""Hide the overlay and emit closed signal."""
	if visible:
		AudioManager.play("panel_close")
	hide()
	cached_data = {}
	_open_review_target = ""
	_focus_settlement_route_id = ""
	_focus_settlement_war_id = ""
	_expanded_peace_ratifications = {}
	_expanded_settlements = {}
	_stop_critical_pulse()
	closed.emit()


func _on_ledger_received(response):
	"""Cache data and render current tab."""
	if not visible:
		return

	if not response.get("success", false):
		content_area.text = "[color=#" + Utils.COLOR_ERROR + "]Failed to load diplomatic ledger.[/color]"
		return

	cached_data = response.get("ledger", {})
	_expanded_peace_ratifications = {}
	_expanded_settlements = {}
	if cached_data.is_empty():
		content_area.text = "[color=#" + Utils.COLOR_INFO + "]No diplomatic data available.[/color]"
		return

	# Update DP display in header
	var talleyrand_data = cached_data.get("talleyrand", {})
	var dp = int(talleyrand_data.get("dp_remaining", 0))
	var dp_max = int(talleyrand_data.get("dp_max", 3))
	dp_display.text = "DP: " + str(dp) + "/" + str(dp_max)
	_set_cabinet_line(talleyrand_data)

	_render_current_tab()


func _on_tab_pressed(tab_index: int):
	_switch_tab(tab_index)


func _switch_tab(tab_index: int):
	if tab_index == current_tab:
		return
	current_tab = tab_index
	scroll_container.scroll_vertical = 0
	_update_tab_highlights()
	_render_current_tab()


func _update_tab_highlights():
	for i in range(tab_buttons.size()):
		# Session UI: the open book's words bright, a closed book's dim.
		Utils.tint_tab(tab_buttons[i], i == current_tab)
		if i == current_tab:
			tab_buttons[i].add_theme_stylebox_override("normal", _active_tab_style)
		else:
			tab_buttons[i].add_theme_stylebox_override("normal", _normal_tab_style)
		# UXR3-43 / 37 (Pre-Deploy S12): the open book's tab is selected and
		# disabled ("You are reading this book") — its press answered nothing.
		Utils.mark_active_tab(tab_buttons[i], i == current_tab, _active_tab_style)


func _render_current_tab():
	if cached_data.is_empty():
		return
	_stop_critical_pulse()
	match current_tab:
		0:
			_render_nations()
		1:
			_render_treaties()
		2:
			_render_balance_of_europe()
		3:
			_render_talleyrand()
		4:
			_render_war_bargains()
		5:
			_render_vassals()
		6:
			_render_congress()


func _format_bloc_stamp(stamp) -> String:
	if stamp == null or not stamp is Dictionary:
		return ""
	var label = str(stamp.get("label", "")).strip_edges()
	if label == "":
		return ""
	var kind = str(stamp.get("kind", "neutral"))
	var stamp_color = Utils.COLOR_INFO
	match kind:
		"coalition":
			stamp_color = Utils.cv_hex(COLOR_RED)
		"proper_bloc":
			stamp_color = Utils.COLOR_COMMAND
		"descriptive_bloc":
			stamp_color = Utils.COLOR_INFO
		"vassal":
			stamp_color = Utils.COLOR_GOLD
		"neutral":
			stamp_color = Utils.COLOR_INFO
	return " [color=#" + stamp_color + "][" + label + "][/color]"

# Session UI-2 (November 11, 2026): the ledger's two small kit helpers — a
# facts table (label / value, striped, the label a glyph and its words) and the
# wide threat gauge. A cell never holds a newline; the label ends in a space so
# `get_parsed_text()` reads "Diplomat: Talleyrand" across the two cells.
func _fact_label(glyph_name: String, words: String) -> String:
	return Utils.bb_glyph(glyph_name, 16, Utils.COLOR_GOLD) + " [color=#" + Utils.COLOR_INFO + "]" + words + "[/color]"


func _facts_table(rows: Array, wide := false) -> String:
	if rows.is_empty():
		return ""
	# Session UI-5 interim fix (Nov 13): `wide` (a content area of 820 px or more: two label/value pairs need ~760) sets
	# the rows in two label/value column pairs, so a card does not leave its right
	# half empty. Rows keep their order: the first half down the left, the rest
	# down the right.
	if wide and rows.size() >= 4:
		var half: int = int(ceil(rows.size() / 2.0))
		var out2 := "[table=4]"
		for i in range(half):
			var left: Array = rows[i]
			out2 += "[cell bg=#%s,#%s padding=6,2,10,2]%s[/cell]" % [Utils.ZEBRA_A, Utils.ZEBRA_B, str(left[0])]
			out2 += "[cell expand=1 bg=#%s,#%s padding=6,2,18,2]%s[/cell]" % [Utils.ZEBRA_A, Utils.ZEBRA_B, str(left[1])]
			if i + half < rows.size():
				var right: Array = rows[i + half]
				out2 += "[cell bg=#%s,#%s padding=6,2,10,2]%s[/cell]" % [Utils.ZEBRA_A, Utils.ZEBRA_B, str(right[0])]
				out2 += "[cell expand=1 bg=#%s,#%s padding=6,2,6,2]%s[/cell]" % [Utils.ZEBRA_A, Utils.ZEBRA_B, str(right[1])]
			else:
				out2 += "[cell padding=6,2,10,2] [/cell][cell expand=1 padding=6,2,6,2] [/cell]"
		return out2 + "[/table]\n"
	var out := "[table=2]"
	for r in rows:
		out += "[cell bg=#%s,#%s padding=6,2,10,2]%s[/cell]" % [Utils.ZEBRA_A, Utils.ZEBRA_B, str(r[0])]
		out += "[cell expand=1 bg=#%s,#%s padding=6,2,6,2]%s[/cell]" % [Utils.ZEBRA_A, Utils.ZEBRA_B, str(r[1])]
	return out + "[/table]\n"


func _threat_gauge(level: int, width: int, height: int, fill_hex: String, marks: Array, ghost_to: int = -1) -> String:
	"""The wide threat gauge: 0-100 across `width` px, filled to `level` in
	`fill_hex`, a 2-px gilt tick at each of `marks` (60 'brews', 80 'forms').
	Session UI-4 (November 12, 2026): `ghost_to` (>= level) lays a lighter ghost
	segment from the level to where the next war of conquest would take it."""
	var out := ""
	var lvl: int = clampi(level, 0, 100)
	var ghost: int = clampi(ghost_to, lvl, 100) if ghost_to >= 0 else lvl
	var edges: Array = [0]
	for m in marks:
		edges.append(int(m))
	edges.append(100)
	for i in range(edges.size() - 1):
		var a: int = edges[i]
		var b: int = edges[i + 1]
		var span_w: int = int(round(float(width) * float(b - a) / 100.0))
		var fill_w: int = int(round(float(span_w) * float(clampi(lvl - a, 0, b - a)) / float(maxi(b - a, 1))))
		var ghost_w: int = int(round(float(span_w) * float(clampi(ghost - a, 0, b - a)) / float(maxi(b - a, 1)))) - fill_w
		ghost_w = maxi(ghost_w, 0)
		if fill_w > 0:
			out += "[img width=%d height=%d color=#%s]%s[/img]" % [fill_w, height, fill_hex, Utils.SWATCH]
		if ghost_w > 0:
			out += "[img width=%d height=%d color=#%s55]%s[/img]" % [ghost_w, height, fill_hex, Utils.SWATCH]
		if span_w - fill_w - ghost_w > 0:
			out += "[img width=%d height=%d color=#%s]%s[/img]" % [span_w - fill_w - ghost_w, height, Utils.METER_TRACK, Utils.SWATCH]
		if i < edges.size() - 2:
			out += "[img width=2 height=%d color=#%s]%s[/img]" % [height + 4, Utils.COLOR_GOLD, Utils.SWATCH]
	return out


func _balance_width() -> int:
	"""Session UI-4: the Balance page's content width in px (the window's own
	less its margins and the scroll bar), 640 before the window has a size."""
	var w: int = int(content_area.size.x) - 64 if content_area != null else 0
	return w if w > 280 else 640


func _gauge_scale_table(brews: int, forms: int) -> String:
	"""Labels standing under the gauge's ticks: 0, brews N, forms N and 100 at
	the far right. Measured on the first shoot: a BBCode table shrinks to its
	words here (the four labels stood together at the left, "0 brews 60 forms
	80 100"), so each label is set at its tick by a transparent spacer image,
	the widths read off the gauge's own width and the page's font."""
	var w := float(_balance_width())
	var b: int = clampi(brews, 1, 98)
	var f: int = clampi(forms, b + 1, 99)
	var font: Font = content_area.get_theme_font("normal_font") if content_area != null else null
	var size: int = content_area.get_theme_font_size("normal_font_size") if content_area != null else 16
	var measure := func(text: String) -> float:
		return font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x if font != null else 8.0 * text.length()
	var spacer := func(px: float) -> String:
		var n := int(floor(px))
		return "[img width=%d height=1 color=#00000000]%s[/img]" % [n, Utils.SWATCH] if n >= 1 else ""
	var ink := "[color=#" + Utils.COLOR_INFO + "]%s[/color]"
	var out := ""
	var x := 0.0
	for mark in [[0.0, "0"], [w * b / 100.0, "brews " + str(brews)], [w * f / 100.0, "forms " + str(forms)]]:
		var at: float = maxf(float(mark[0]), x)
		out += spacer.call(at - x) + ink % str(mark[1])
		x = at + float(measure.call(str(mark[1])))
	var last_w: float = measure.call("100")
	out += spacer.call(maxf(w - last_w - x, 4.0)) + ink % "100"
	return out + "\n"


func _balance_figures(boe: Dictionary, projection) -> String:
	"""Session UI-4: the figure row under the gauge — glyph, figure, caption
	(the Dispatch's idiom). A figure the payload lacks is skipped."""
	var gap := "  "
	var parts: Array = []
	var hegemon_name := str(boe.get("hegemon", ""))
	if hegemon_name != "" and hegemon_name != "<null>" and boe.has("hegemon_share"):
		parts.append(Utils.bb_glyph("europe", 18) + " " + Utils.HEAD_OPEN + str(int(boe.get("hegemon_share", 0))) + "%" + Utils.HEAD_CLOSE
			+ " [color=#" + Utils.COLOR_INFO + "]of Europe's power[/color]")
	if projection is Dictionary and projection.has("wars_until_brewing") and str(projection.get("collapse_line", "")) == "":
		var wars := int(projection.get("wars_until_brewing", 0))
		parts.append(Utils.bb_glyph("war", 18) + " " + Utils.HEAD_OPEN + str(wars) + Utils.HEAD_CLOSE
			+ " [color=#" + Utils.COLOR_INFO + "]" + ("wars" if wars != 1 else "war") + " until a coalition brews[/color]")
	var coalition = boe.get("active_coalition")
	if coalition is Dictionary:
		var leader_key := str(coalition.get("leader", ""))
		parts.append(Utils.bb_flag(leader_key, 18) + Utils.HEAD_OPEN
			+ Utils.humanize_nation_keys_in_text(str(coalition.get("name", "Coalition"))).replace("[", "[lb]") + Utils.HEAD_CLOSE
			+ " [color=#" + Utils.COLOR_INFO + "]led by " + Utils.display_nation_name(leader_key) + "[/color]")
	else:
		parts.append(Utils.bb_glyph("command", 18) + " " + Utils.HEAD_OPEN + "none" + Utils.HEAD_CLOSE
			+ " [color=#" + Utils.COLOR_INFO + "]no coalition[/color]")
	if boe.has("dissolution_threat_threshold"):
		parts.append(Utils.bb_glyph("stability", 18) + " " + Utils.HEAD_OPEN + "<" + str(int(boe.get("dissolution_threat_threshold", 20))) + Utils.HEAD_CLOSE
			+ " [color=#" + Utils.COLOR_INFO + "]dissolves below[/color]")
	# Session UI-5 interim fix (Nov 13): the figures stand two to a line (they ran
	# four across and crammed); the figures and words are unchanged.
	var lines: Array = []
	for i in range(0, parts.size(), 2):
		lines.append(gap.join(PackedStringArray(parts.slice(i, i + 2))))
	return "\n".join(PackedStringArray(lines)) + "\n"



# =============================================================================
# TAB 1: NATION OVERVIEW
# =============================================================================

func _render_nations():
	var nations = cached_data.get("nations", [])
	var bbcode = ""
	# Session UI-3 (November 12, 2026): the lead-in stands behind an ⓘ at the
	# heading's line ("Fold, a switch restores"); On the page both lines print as
	# they did.
	var nations_lead := "Every court of Europe — its temper toward France, and the instruments to move it. Press F1 to treat; D closes this ledger."
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]═══ NATION OVERVIEW ═══[/color]" + Utils.lead_mark(nations_lead, "dl.nations.lead") + "\n"
	# R159 (POSITION 7): each core screen names the mechanic it displays.
	bbcode += Utils.bb_lead("[color=#" + Utils.COLOR_INFO + "]Every court of Europe — its temper toward France, and the instruments to move it. Press F1 to treat; D closes this ledger.[/color]\n", "dl.nations.lead") + "\n"

	# UXR3-29 (Pre-Deploy S15 head, October 25, 2026): the Nations book LEADS
	# WITH THE COURTS' CARDS — each great power's Laws and Doctrine lines sit in
	# the first screenful. The two France-centred blocks below (the mirror and
	# the exposure) are built here and appended UNDER the last card (and under
	# the empty notice when no court is in contact).
	var france_blocks := ""
	# AI-1b (the mirror): Europe's derived reading of FRANCE — the player's
	# own row. Omitted when null (legacy/bare worlds).
	var mirror = cached_data.get("france_mirror")
	if mirror != null and mirror is Dictionary:
		france_blocks += "[color=#" + Utils.COLOR_GOLD + "][b]How Europe Reads France[/b][/color]\n"
		var mirror_lines = mirror.get("lines", [])
		for ml in mirror_lines:
			france_blocks += "  [color=#" + Utils.COLOR_INFO + "]" + str(ml) + "[/color]\n"
		france_blocks += "\n"

	# AI-3r (§2.5-3): France's own exposure — the same reserve/free
	# derivation the war council applies to every court, shown to the
	# player. Display only, never a gate on orders (gate Q5). Backend-
	# composed line (R7); null omits the block.
	var exposure = cached_data.get("france_exposure")
	if exposure != null and exposure is Dictionary:
		var exposure_line = str(exposure.get("line", ""))
		if exposure_line != "":
			france_blocks += "[color=#" + Utils.COLOR_GOLD + "][b]The Emperor's Own Exposure[/b][/color]\n"
			france_blocks += "  [color=#" + Utils.COLOR_INFO + "]" + Utils.humanize_nation_keys_in_text(exposure_line) + "[/color]\n"
			france_blocks += "\n"

	if nations.size() == 0:
		bbcode += "[color=#" + Utils.COLOR_INFO + "]No nations in diplomatic contact.[/color]\n"
		if france_blocks != "":
			bbcode += "\n" + france_blocks
		content_area.text = Utils.dress_heads(bbcode)
		return

	for n in nations:
		var name = str(n.get("name", "?"))
		var diplo_state = str(n.get("diplomatic_state", "PEACE"))
		var relation = int(n.get("relation", 0))

		# Diplomatic state color
		var state_color = Utils.COLOR_INFO
		match diplo_state:
			"WAR":
				state_color = Utils.COLOR_ERROR
			"PEACE":
				state_color = Utils.COLOR_INFO
			"ALLIANCE":
				state_color = Utils.COLOR_SUCCESS
			"NON_AGGRESSION":
				state_color = Utils.COLOR_BLUE
			"OPEN_BORDERS":
				state_color = Utils.COLOR_BLUE

		# Relation color
		var rel_color = Utils.COLOR_INFO
		if relation < -50:
			rel_color = Utils.COLOR_ERROR
		elif relation > 50:
			rel_color = Utils.COLOR_SUCCESS

		var rel_sign = "+" if relation > 0 else ""

		# N6: Relation descriptor
		var rel_desc = str(n.get("relation_descriptor", ""))
		var rel_text = rel_sign + str(relation)
		if rel_desc:
			rel_text += " (" + rel_desc + ")"

		# N7: Relation trend arrow. Stable draws nothing — a flat "→" after
		# the descriptor read as a dangling artifact, not a trend.
		var trend = str(n.get("relation_trend", "stable"))
		if trend == "rising":
			rel_text += " ↑"
		elif trend == "falling":
			rel_text += " ↓"

		# Session UI (November 11, 2026): a court a card, its hairline and
		# spine in its standing's colour (a court at peace takes the gilt).
		bbcode += Utils.card_open(Utils.COLOR_GOLD if diplo_state == "PEACE" else state_color)
		# Session UI-2 (November 11, 2026): the court's header row — its arms,
		# its name in the title face, its standing as a badge, its relation on
		# a meter centred on nought (the readers: "a flag / relation header").
		bbcode += Utils.bb_flag(name, 18) + " "
		bbcode += Utils.HEAD_OPEN + Utils.display_nation_name(name) + Utils.HEAD_CLOSE
		bbcode += _format_bloc_stamp(n.get("bloc_stamp"))
		bbcode += "  " + Utils.bb_badge(Utils.display_diplo_state(diplo_state), state_color)
		bbcode += "  Relation: " + Utils.bb_relation_meter(relation, 100, 7) \
			+ " [color=#" + rel_color + "]" + rel_text + "[/color]"

		# N4: Vassal eligibility
		var vassal_eligible = n.get("vassal_eligible", false)
		var power_tier = str(n.get("power_tier", ""))
		if vassal_eligible and power_tier == "minor":
			bbcode += "  [color=#" + Utils.COLOR_GOLD + "]★ Vassalizable[/color]"
		bbcode += "\n"
		# Session UI-2 (November 11, 2026): the court's facts as a two-column
		# label/value table under its header row (the readers: "dense lines per
		# nation") — every line of the old card is a row here, in its order, its
		# words unchanged; the AI relations, the war score and the cooldowns
		# follow as badge / figure lines.
		var facts: Array = []
		# UXR3-29 (Pre-Deploy S12 part 2): the court's Laws and Doctrine lines
		# LEAD its card, under its name — they were its eighth and ninth
		# lines, under the diplomat, the treaties and the design.
		# SR-5r RF-4b (REFORMS_SPEC §8a): the court's laws in force, by name
		# and what they cost it a turn — diplomacy has no fog. Backend-
		# composed line (R7); null omits the row.
		var laws_row = n.get("laws")
		if laws_row != null and str(laws_row) != "":
			facts.append([_fact_label("administration", "Laws: "), "[color=#" + Utils.COLOR_GOLD + "]" + str(laws_row) + "[/color]"])
		# SR-7d DC-3a (DOCTRINES_SPEC §4a): the court's doctrine — name,
		# strength, flaw and the cure's status, ONE line (the two-line budget
		# with the laws line). Backend-composed; null omits.
		# Session UI-3 (November 12, 2026): a court's long rows (the doctrine's flaw
		# clause, Design, Intent, the AI relations, the war score) stand behind ONE
		# "▸ more" at the card's foot; On the page, or opened, every row prints as
		# it did.
		var court_note_id: String = "dl.nations.court." + name
		var court_open: bool = Utils.show_note(court_note_id)
		var doctrine_row = n.get("doctrine")
		if doctrine_row != null and str(doctrine_row) != "":
			var doctrine_text: String = str(doctrine_row)
			if not court_open and doctrine_text.find("; flaw:") >= 0:
				doctrine_text = doctrine_text.substr(0, doctrine_text.find("; flaw:"))
			facts.append([_fact_label("tactical", "Doctrine: "), "[color=#" + Utils.COLOR_INFO + "]" + doctrine_text + "[/color]"])
		# DY-7 (DYNAMISM_SPEC.md §6): a crown's row names who withholds its
		# recognition; a legitimist's row names the crowns of ours it withholds
		# and the price. Backend-composed (R7); null omits the row.
		var crown_row = n.get("crown")
		if crown_row != null and str(crown_row) != "":
			facts.append([_fact_label("glory", "Crown: "), "[color=#" + Utils.COLOR_GOLD + "]" + Utils.humanize_nation_keys_in_text(str(crown_row)) + "[/color]"])
		var recognition_row = n.get("recognition")
		if recognition_row != null and str(recognition_row) != "":
			facts.append([_fact_label("letter", "Recognition: "), "[color=#" + Utils.COLOR_WARNING + "]" + Utils.humanize_nation_keys_in_text(str(recognition_row)) + "[/color]"])

		# Diplomat info
		var diplomat = n.get("diplomat")
		if diplomat != null and diplomat is Dictionary:
			var d_name = str(diplomat.get("name", "?"))
			var d_pers = str(diplomat.get("personality", "?")).capitalize()
			var d_skill = int(diplomat.get("skill", 0))
			facts.append([_fact_label("envoy", "Diplomat: "), d_name + " (" + d_pers + ") — Skill " + str(d_skill)])
		else:
			facts.append([_fact_label("envoy", "Diplomat: "), "[color=#" + Utils.COLOR_INFO + "]None[/color]"])
		# AU-4 (AUTHORITY_CURRENCY_SPEC.md Q6): the court's standing beside its
		# envoy — both feed its diplomatic points; the term said only when it
		# is not zero (the DP rule's own bands, backend-composed). Absent omits.
		var auth_row = n.get("authority")
		if auth_row is Dictionary and auth_row.has("figure"):
			var auth_dp = int(auth_row.get("dp", 0))
			var auth_tail = ""
			if auth_dp > 0:
				auth_tail = " (+" + str(auth_dp) + " diplomatic point a turn)"
			elif auth_dp < 0:
				auth_tail = " (−" + str(-auth_dp) + " diplomatic point a turn)"
			facts.append([_fact_label("authority", "Authority: "), str(int(auth_row.get("figure", 0))) + auth_tail])

		# Regions + Army
		var regions = int(n.get("regions_controlled", 0))
		var army = str(n.get("army_strength", "Unknown"))
		facts.append([_fact_label("europe", "Regions: "), str(regions)])
		facts.append([_fact_label("strength", "Army: "), army])

		# N5: Trade income
		var trade_income = int(n.get("trade_income", 0))
		if trade_income > 0:
			facts.append([_fact_label("gold", "Trade: "), "[color=#" + Utils.COLOR_GOLD + "]+" + str(trade_income) + "g/turn[/color]"])

		# Treaties
		var treaties = n.get("active_treaties", [])
		if treaties.size() > 0:
			facts.append([_fact_label("letter", "Treaties: "), ", ".join(PackedStringArray(treaties))])
		else:
			facts.append([_fact_label("letter", "Treaties: "), "[color=#" + Utils.COLOR_INFO + "]None[/color]"])

		# NA-1: the nation's active design (omit when null — bloc_stamp contract)
		var agenda = n.get("agenda")
		if court_open and agenda != null and agenda is Dictionary:
			var agenda_title = str(agenda.get("title", ""))
			var agenda_stance = str(agenda.get("stance_line", ""))
			if agenda_title != "":
				var design_cell: String = "[color=#" + Utils.COLOR_GOLD + "]" + agenda_title + "[/color]"
				if agenda_stance != "":
					design_cell += " [color=#" + Utils.COLOR_INFO + "]— " + agenda_stance + "[/color]"
				# NA-6d §11.6-5: the watcher marker — a design carrying a
				# `forms` block advertises the nation it would become, with
				# live progress, so no formation ever ambushes the player.
				var agenda_forms = agenda.get("forms")
				if agenda_forms != null and agenda_forms is Dictionary:
					var forms_name = str(agenda_forms.get("display_name", ""))
					if forms_name != "":
						var forms_line = "forms: " + forms_name
						var forms_progress = str(agenda_forms.get("progress", ""))
						if forms_progress != "":
							forms_line += " (" + forms_progress + ")"
						design_cell += " [color=#" + Utils.COLOR_GOLD + "]→ " + forms_line + "[/color]"
				facts.append([_fact_label("cabinet", "Design: "), design_cell])

		# AI-1: the nation's intent — its price, fully open (D4: want,
		# target and rung always shown; only timing is uncertain).
		var intent = n.get("intent")
		if court_open and intent != null and intent is Dictionary:
			var intent_summary = str(intent.get("summary", ""))
			if intent_summary != "":
				facts.append([_fact_label("intel", "Intent: "), "[color=#" + Utils.COLOR_INFO + "]" + intent_summary + "[/color]"])

		# AI-2b/2e (Stage C): every live D5 instrument this court is
		# party to — sponsorships, licences, neutrality compacts,
		# buy-off bargains, guarantees, an open allegiance auction.
		# Backend-composed line (R7); null omits the row.
		var compacts = n.get("compacts")
		if compacts != null and str(compacts) != "":
			facts.append([_fact_label("cabinet", "Compacts: "), "[color=#" + Utils.COLOR_GOLD + "]" + Utils.humanize_nation_keys_in_text(str(compacts)) + "[/color]"])

		# AI-4c (Stage D): war-weariness, explicitly labelled as national
		# exhaustion across ALL the court's wars, belligerents named —
		# "let them bleed while France rearms" readable per court.
		# Backend-composed line (R7); null omits the row.
		var weariness = n.get("war_weariness")
		if weariness != null and weariness is Dictionary:
			var weariness_line = str(weariness.get("line", ""))
			if weariness_line != "":
				facts.append([_fact_label("morale", "Weariness: "), "[color=#" + Utils.COLOR_WARNING + "]" + Utils.humanize_nation_keys_in_text(weariness_line) + "[/color]"])

		# AI-3r (§2.5-2): the court's exposure — free field army vs the
		# rear-security reserve, the war council's own arithmetic made
		# readable. Backend-composed line (R7); null omits the row.
		var exposure_row = n.get("exposure")
		if exposure_row != null and exposure_row is Dictionary:
			var exposure_row_line = str(exposure_row.get("line", ""))
			if exposure_row_line != "":
				facts.append([_fact_label("defense", "Exposure: "), "[color=#" + Utils.COLOR_INFO + "]" + Utils.humanize_nation_keys_in_text(exposure_row_line) + "[/color]"])

		bbcode += _facts_table(facts, content_area != null and int(content_area.size.x) >= 820)

		# N1: AI-AI Relations (DPF-1: includes relation descriptor) — each tie
		# a state badge, the temper in words after it.
		var ai_relations = n.get("ai_relations", [])
		if court_open and ai_relations.size() > 0:
			var ai_parts = []
			for ar in ai_relations:
				var ar_nation = str(ar.get("nation", "?"))
				var ar_state = str(ar.get("state", "PEACE"))
				var ar_relation = int(ar.get("relation", 0))
				var ar_descriptor = str(ar.get("relation_descriptor", "Neutral"))
				var ar_tone = Utils.COLOR_BADGE_QUIET
				match ar_state:
					"WAR":
						ar_tone = Utils.cv_hex("8b2a2a")
					"ALLIANCE", "DEFENSIVE_ALLIANCE":
						ar_tone = Utils.cv_hex("2f6b3a")
					"NON_AGGRESSION", "OPEN_BORDERS":
						ar_tone = "3a4a6b"
				var ar_desc_color = Utils.COLOR_INFO
				if ar_relation > 0:
					ar_desc_color = Utils.COLOR_SUCCESS
				elif ar_relation < 0:
					ar_desc_color = Utils.cv_hex(COLOR_RED)
				ai_parts.append(Utils.display_nation_name(ar_nation) + " " + Utils.bb_badge(Utils.display_diplo_state(ar_state), ar_tone) + " — [color=#" + ar_desc_color + "]" + ar_descriptor + " (" + str(ar_relation) + ")[/color]")
			bbcode += "  AI Relations: " + "   ".join(PackedStringArray(ai_parts)) + "\n"

		# N2: War Score Breakdown (WAR only) — the total a badge, the parts after it
		var war_score = n.get("war_score_breakdown")
		if court_open and war_score != null and war_score is Dictionary:
			var total = int(war_score.get("total", 0))
			var ws_color = Utils.COLOR_SUCCESS if total > 0 else (Utils.cv_hex(COLOR_RED) if total < 0 else Utils.COLOR_INFO)
			var ws_tone = Utils.cv_hex("2f6b3a") if total > 0 else (Utils.cv_hex("8b2a2a") if total < 0 else Utils.COLOR_BADGE_QUIET)
			var ws_sign = "+" if total > 0 else ""
			bbcode += "  War Score: " + Utils.bb_badge(ws_sign + str(total), ws_tone) + "  ("
			var ws_parts = []
			# PT-J2: campaign + blood are the war's memory components.
			# HC-1: blockade joins them, rendered only when nonzero.
			var ws_keys = ["territory", "battles", "decisive", "capital", "campaign", "blood"]
			if int(war_score.get("blockade", 0)) != 0:
				ws_keys.append("blockade")
			for ws_key in ws_keys:
				var ws_val = int(war_score.get(ws_key, 0))
				var comp_sign = "+" if ws_val > 0 else ""
				var comp_color = Utils.COLOR_SUCCESS if ws_val > 0 else (Utils.cv_hex(COLOR_RED) if ws_val < 0 else Utils.COLOR_INFO)
				ws_parts.append(ws_key.capitalize() + " [color=#" + comp_color + "]" + comp_sign + str(ws_val) + "[/color]")
			bbcode += ", ".join(PackedStringArray(ws_parts)) + ")\n"

		# N3: Proposal cooldowns
		var cooldowns = n.get("proposal_cooldowns")
		if cooldowns != null and cooldowns is Dictionary and cooldowns.size() > 0:
			var cd_parts = []
			for cd_key in cooldowns:
				var cd_val = int(cooldowns[cd_key])
				cd_parts.append(cd_key.capitalize() + ": " + str(cd_val) + " turns")
			bbcode += "  Cooldowns: [color=#" + COLOR_AMBER + "][" + ", ".join(PackedStringArray(cd_parts)) + "][/color]\n"

		# Session UI-3: the one toggle at the card's foot (nothing On the page),
		# only where the court has a long row to open.
		var long_rows: bool = (agenda != null and agenda is Dictionary and str(agenda.get("title", "")) != "") \
			or (intent != null and intent is Dictionary and str(intent.get("summary", "")) != "") \
			or ai_relations.size() > 0 \
			or (war_score != null and war_score is Dictionary) \
			or (doctrine_row != null and str(doctrine_row).find("; flaw:") >= 0)
		if long_rows:
			var court_link: String = Utils.note_link(court_note_id)
			if court_link != "":
				bbcode += "  " + court_link + "\n"

		bbcode += Utils.CARD_CLOSE
		bbcode += "\n"

	# UXR3-29 (S15 head): France's own two blocks close the book, under the
	# courts' cards.
	bbcode += france_blocks
	content_area.text = Utils.dress_heads(bbcode)


# =============================================================================
# TAB 2: ACTIVE TREATIES
# =============================================================================

func _render_treaties():
	var treaties = cached_data.get("treaties", [])
	var recent_peace = cached_data.get("recent_peace_ratifications", [])
	var current_turn = int(cached_data.get("current_turn", 0))
	var bbcode = ""
	var header = "ACTIVE TREATIES"
	if _open_review_target == "ledger_commitments":
		header = "COMMITMENTS REVIEW"
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]═══ " + header + " ═══[/color]\n\n"

	if treaties.size() == 0 and recent_peace.size() == 0:
		bbcode += "[color=#" + Utils.COLOR_INFO + "]No active treaties.[/color]\n"
		content_area.text = Utils.dress_heads(bbcode)
		return
	elif treaties.size() == 0:
		bbcode += "[color=#" + Utils.COLOR_INFO + "]No active treaties.[/color]\n\n"

	for t in treaties:
		var nation_a = str(t.get("nation_a", "?"))
		var nation_b = str(t.get("nation_b", "?"))
		var treaty_type = str(t.get("treaty_type", "unknown"))
		var clauses = t.get("clauses", [])
		var duration = t.get("duration", "permanent")
		var cancel_cost = int(t.get("cancel_cost", 1))

		# T3: Player vs AI-AI distinction
		var involves_player = t.get("involves_player", true)
		var header_color = Utils.COLOR_GOLD if involves_player else Utils.COLOR_INFO

		bbcode += Utils.card_open()    # Session UI: a treaty a card
		# Session UI-2 (November 11, 2026): the two courts' arms and names, the
		# kind of treaty a badge (the player's own in the gilt, a pact of two
		# other courts in the quiet tone).
		bbcode += Utils.bb_flag(nation_a, 16) + " [color=#" + header_color + "]" + Utils.display_nation_name(nation_a) + "[/color]"
		bbcode += " [color=#" + Utils.COLOR_INFO + "]↔[/color] "
		bbcode += Utils.bb_flag(nation_b, 16) + " [color=#" + header_color + "]" + Utils.display_nation_name(nation_b) + "[/color]"
		bbcode += ": " + Utils.bb_badge(treaty_type.replace("_", " ").capitalize(), "8a6d2a" if involves_player else Utils.COLOR_BADGE_QUIET) + "\n"

		# DDB-32: an alliance with no treaty record (the 1805 alliances) says
		# what it is, and carries no clauses or term of ours.
		if bool(t.get("inherited", false)):
			bbcode += "  [color=#" + Utils.COLOR_INFO + "][i]" + str(t.get("note", "")) + "[/i][/color]\n" + Utils.CARD_CLOSE + "\n"
			continue

		var terms_facts: Array = []
		# Clauses
		if clauses.size() > 0:
			var clause_strs = []
			for c in clauses:
				clause_strs.append(str(c))
			terms_facts.append([_fact_label("letter", "Clauses: "), ", ".join(PackedStringArray(clause_strs))])
		else:
			terms_facts.append([_fact_label("letter", "Clauses: "), "[color=#" + Utils.COLOR_INFO + "]None[/color]"])

		# T4: Armistice countdown
		var armistice_remaining = t.get("armistice_remaining")
		if armistice_remaining != null:
			terms_facts.append([_fact_label("turn", "Duration: "), "[color=#" + COLOR_AMBER + "]Armistice — expires in " + str(int(armistice_remaining)) + " turns[/color]"])
		else:
			# Duration
			var dur_str = ""
			if duration is int or duration is float:
				dur_str = str(int(duration)) + " turns"
			else:
				dur_str = str(duration)
			terms_facts.append([_fact_label("turn", "Duration: "), dur_str + "   Cancel cost: " + str(cancel_cost) + " DP"])

		# T2: Turn signed
		var turn_signed = int(t.get("turn_signed", 0))
		if turn_signed > 0 and current_turn > 0:
			var turns_ago = current_turn - turn_signed
			terms_facts.append([_fact_label("medal", "Signed: "), "Turn " + str(turn_signed) + " (" + str(turns_ago) + " turns ago)"])

		# T1: Gold per turn
		var gold_per_turn = t.get("gold_per_turn")
		if gold_per_turn != null and gold_per_turn is Array and gold_per_turn.size() > 0:
			for gpt in gold_per_turn:
				var gpt_from = str(gpt.get("from", "?"))
				var gpt_to = str(gpt.get("to", "?"))
				var gpt_amount = int(gpt.get("amount", 0))
				terms_facts.append([_fact_label("gold", "Gold Flow: "), "[color=#" + Utils.COLOR_GOLD + "]" + Utils.display_nation_name(gpt_from) + " → " + Utils.display_nation_name(gpt_to) + ": " + str(gpt_amount) + "g/turn[/color]"])

		bbcode += _facts_table(terms_facts)
		bbcode += Utils.CARD_CLOSE
		bbcode += "\n"

	# SC-23 (Settlement UI Cleanup G2-Slice-5): merged PEACE & SETTLEMENT
	# HISTORY surface. Render `peace_settlement_history` when present
	# (newer payload). Each row carries a `row_type` ("settlement" or
	# "bilateral_peace") so the player sees one reverse-chronological
	# stream with type pills instead of two confusingly named sections.
	var merged_history = cached_data.get("peace_settlement_history", [])
	var recent_settlements = cached_data.get("recent_settlements", [])
	var rendered_settlement_meta = {}
	if merged_history is Array and merged_history.size() > 0:
		var hist_header = "PEACE & SETTLEMENT HISTORY"
		if _open_review_target == "ledger_settlements":
			hist_header = "▶ PEACE & SETTLEMENT HISTORY"
		bbcode += "[color=#" + Utils.COLOR_HEADER + "]--- " + hist_header + " ---[/color]\n\n"
		var h_idx = 0
		for row in merged_history:
			if not row is Dictionary:
				h_idx += 1
				continue
			var row_type = str(row.get("row_type", "settlement"))
			var row_type_display = str(row.get("row_type_display", row_type.capitalize()))
			var s_war_id = str(row.get("war_id", "?"))
			var s_turn = int(row.get("turn", 0))
			var s_headline = Utils.humanize_nation_keys_in_text(str(row.get("headline", "Settlement")))
			var s_route = str(row.get("route_id", ""))
			if row_type == "settlement":
				var s_meta = "settlement:" + str(h_idx) + ":" + s_route
				rendered_settlement_meta[s_meta] = true
				var focus_match = (
					(_focus_settlement_route_id != "" and s_route == _focus_settlement_route_id)
					or (_focus_settlement_war_id != "" and s_war_id == _focus_settlement_war_id)
				)
				if focus_match and not _expanded_settlements.has(s_meta):
					_expanded_settlements[s_meta] = true
				var s_expanded = bool(_expanded_settlements.get(s_meta, false))
				var s_marker = "v" if s_expanded else ">"
				var row_color = Utils.COLOR_SUCCESS if focus_match else Utils.COLOR_GOLD
				bbcode += "  [url=" + s_meta + "][color=#" + row_color + "]" + s_marker + " " + s_headline + "[/color][/url]"
				bbcode += "  [color=#" + Utils.COLOR_INFO + "](" + row_type_display + " · T" + str(s_turn) + ")[/color]\n"
				var awe_tags = row.get("awe_tag_displays", row.get("awe_tags", []))
				if awe_tags is Array and awe_tags.size() > 0:
					bbcode += "    [color=#" + Utils.COLOR_INFO + "]Awe: " + ", ".join(PackedStringArray(awe_tags)) + "[/color]\n"
				var named = row.get("named_reactions", [])
				var more_count = int(row.get("additional_reaction_count", 0))
				if named is Array and named.size() > 0:
					var who_str = ", ".join(PackedStringArray(named))
					if more_count > 0:
						who_str += " +" + str(more_count) + " more"
					bbcode += "    [color=#" + Utils.COLOR_INFO + "]Reactions: " + who_str + "[/color]\n"
				var terms_summary = row.get("terms_summary", [])
				if terms_summary is Array and terms_summary.size() > 0:
					bbcode += "    [color=#" + Utils.COLOR_INFO + "]Terms: " + _humanize_label(str(terms_summary[0])) + "[/color]\n"
				if s_expanded:
					bbcode += _format_settlement_sections(row.get("review_sections", {}))
			else:
				# Bilateral peace row — render in the same merged stream
				# with a type pill, distinct route id namespace
				# (`peace:{participants_signature}:{turn}:{seq}`).
				# Bilateral peace row — PLAIN text. Unlike a settlement row it
				# carries no review_sections body, so the old [url] + "> " marker
				# toggled an expansion that rendered nothing (dead affordance).
				bbcode += "  [color=#" + Utils.COLOR_GOLD + "]" + s_headline + "[/color]"
				bbcode += "  [color=#" + Utils.COLOR_INFO + "](" + row_type_display + " · T" + str(s_turn) + ")[/color]\n"
			h_idx += 1
		bbcode += "\n"
	# Legacy fallback: render the old "RECENT SETTLEMENTS" section only
	# when the merged surface is unavailable (older backend payloads).
	elif recent_settlements is Array and recent_settlements.size() > 0:
		var settle_header = "RECENT SETTLEMENTS"
		if _open_review_target == "ledger_settlements":
			settle_header = "▶ RECENT SETTLEMENTS"
		bbcode += "[color=#" + Utils.COLOR_HEADER + "]--- " + settle_header + " ---[/color]\n\n"
		var s_idx = 0
		for settle in recent_settlements:
			var s_war_id = str(settle.get("war_id", "?"))
			var s_turn = int(settle.get("turn", 0))
			var s_headline = Utils.humanize_nation_keys_in_text(str(settle.get("headline", "Settlement")))
			var s_route = str(settle.get("route_id", ""))
			var s_meta = "settlement:" + str(s_idx) + ":" + s_route
			var focus_match = (
				(_focus_settlement_route_id != "" and s_route == _focus_settlement_route_id)
				or (_focus_settlement_war_id != "" and s_war_id == _focus_settlement_war_id)
			)
			if focus_match and not _expanded_settlements.has(s_meta):
				_expanded_settlements[s_meta] = true
			var s_expanded = bool(_expanded_settlements.get(s_meta, false))
			var s_marker = "v" if s_expanded else ">"
			var row_color = Utils.COLOR_SUCCESS if focus_match else Utils.COLOR_GOLD
			bbcode += "  [url=" + s_meta + "][color=#" + row_color + "]" + s_marker + " " + s_headline + "[/color][/url]"
			bbcode += "  [color=#" + Utils.COLOR_INFO + "](T" + str(s_turn) + ")[/color]\n"
			s_idx += 1
		bbcode += "\n"

	# Legacy bilateral peace section is suppressed when the merged
	# surface rendered above; otherwise fall through to the original
	# RECENT PEACE RATIFICATIONS block for older payloads.
	var has_merged_history = (merged_history is Array and merged_history.size() > 0)
	if not has_merged_history and recent_peace.size() > 0:
		bbcode += "[color=#" + Utils.COLOR_HEADER + "]--- RECENT PEACE RATIFICATIONS ---[/color]\n"
		bbcode += "\n"
		var peace_idx = 0
		for peace in recent_peace:
			var meta_key = "peace_ratification:" + str(peace_idx)
			var headline = Utils.humanize_nation_keys_in_text(str(peace.get("headline", "Peace Ratification")))
			var summary = Utils.humanize_nation_keys_in_text(str(peace.get("summary", "")))
			var detail = Utils.humanize_nation_keys_in_text(str(peace.get("detail", "")))
			var expanded = bool(_expanded_peace_ratifications.get(meta_key, false))
			var marker = "v" if expanded else ">"
			bbcode += "  [url=" + meta_key + "][color=#" + Utils.COLOR_GOLD + "]" + marker + " " + headline + "[/color][/url]"
			if summary != "":
				bbcode += " - [color=#" + Utils.COLOR_INFO + "]" + summary + "[/color]"
			bbcode += "\n"
			if expanded:
				if detail != "":
					bbcode += "    [color=#" + Utils.COLOR_INFO + "]" + detail + "[/color]\n"
				var terms = peace.get("terms_ratified", [])
				if terms is Array and terms.size() > 0:
					bbcode += "    Terms:\n"
					for term in terms:
						bbcode += "      - " + Utils.humanize_nation_keys_in_text(str(term)) + "\n"
				var aftermath = peace.get("political_aftermath", [])
				if aftermath is Array and aftermath.size() > 0:
					bbcode += "    Aftermath:\n"
					for item in aftermath:
						bbcode += "      - " + Utils.humanize_nation_keys_in_text(str(item)) + "\n"
			peace_idx += 1
		bbcode += "\n"

	content_area.text = Utils.dress_heads(bbcode)


# =============================================================================
# TAB 3: BALANCE OF EUROPE (VP1-X6: the button's title, every pointer's name)

func _designs_block(designs) -> String:
	"""VP-1: the Emperor's designs on the Balance of Europe — the road and
	its two designs, or the three roads before a proclamation. The controls
	live on the Cabinet's road page (F1)."""
	if not (designs is Dictionary) or designs.is_empty():
		return ""
	# Session UI-3 (November 12, 2026): the headline and the road page's pointer
	# stand behind an ⓘ at the heading (id dl.balance.designs); the roads' figure
	# lines stay.
	var designs_tip: String = str(designs.get("headline", ""))
	var designs_control = designs.get("control")
	if designs_control is String and designs_control != "":
		designs_tip += " The road page: " + designs_control
	var out := "[color=#" + Utils.COLOR_HEADER + "]THE EMPEROR'S DESIGNS[/color]" + Utils.lead_mark(designs_tip, "dl.balance.designs") + "\n"
	out += Utils.bb_lead("[color=#" + Utils.COLOR_INFO + "]" + str(designs.get("headline", "")).replace("[", "[lb]") + "[/color]\n", "dl.balance.designs")
	var roads = designs.get("roads")
	if not (roads is Array):
		return out + "\n"
	for road in roads:
		if not (road is Dictionary):
			continue
		var proclaimed: bool = road.get("proclaimed") is bool and road.get("proclaimed")
		var forsworn: bool = road.get("forsworn") is bool and road.get("forsworn")
		if forsworn:
			continue
		var color: String = Utils.COLOR_GOLD if proclaimed else Utils.COLOR_INFO
		# Session UI-2 (November 11, 2026): each road a card — the proclaimed
		# road in the gilt, an open one in the quiet tone.
		out += Utils.card_open(color if proclaimed else Utils.COLOR_BADGE_QUIET)
		out += "  " + Utils.bb_glyph("march", 16, color) + " [color=#" + color + "]Road " + str(road.get("numeral", "")) + " — " + str(road.get("title", "")).replace("[", "[lb]") + "[/color]\n"
		var ds = road.get("designs")
		if not (ds is Array):
			out += Utils.CARD_CLOSE
			continue
		# Session UI-4 (November 12, 2026): the three blind readers called the
		# designs "a bare list". Each road's designs are now progress rows in one
		# table — status mark and title, a meter of held / required, the hold pips,
		# a status tag. Folded, the progress sentence rides the meter's hover and the
		# hint (and the hold line) the title's; On the page every word prints.
		var folded: bool = Utils.explanations_folded()
		var meter_w: int = 110 if Utils.compact_view() else 160
		var design_rows: Array = []
		for d in ds:
			if not (d is Dictionary):
				continue
			var status: String = str(d.get("status", ""))
			var mark: String = "✓" if status == "fulfilled" or status == "met" else ("✗" if status == "lapsed" else "•")
			var tone: String = Utils.COLOR_GOLD
			var tag_text: String = "Open"
			match status:
				"fulfilled":
					tone = Utils.COLOR_SUCCESS
					tag_text = "Fulfilled"
				"met":
					tone = Utils.COLOR_SUCCESS
					tag_text = "Met"
				"lapsed":
					tone = Utils.COLOR_ERROR
					tag_text = "Lapsed"
			var held: int = int(d.get("held", 0))
			var required: int = int(d.get("required", 0))
			var hold_n: int = int(d.get("hold", 0))
			var hold_needed: int = int(d.get("hold_needed", 0))
			var progress_text: String = str(d.get("progress", "")).replace("[", "[lb]")
			var hold = d.get("hold_line")
			var hold_text: String = hold if hold is String else ""
			var title_cell: String = "[color=#" + Utils.COLOR_INFO + "]" + mark + " " + str(d.get("title", "")).replace("[", "[lb]") + "[/color]"
			var title_tip: String = str(d.get("hint", ""))
			if folded and hold_needed <= 0 and hold_text != "":
				title_tip += " (" + hold_text + ")"
			title_cell = Utils.bb_hint(title_cell, title_tip)
			var meter_cell: String = Utils.bb_meter(held, maxi(required, 1), meter_w, 10, tone)
			meter_cell += " [color=#" + Utils.COLOR_INFO + "]" + str(held) + " / " + str(required) + "[/color]"
			if folded:
				meter_cell = Utils.bb_hint(meter_cell, str(d.get("progress", "")))
			elif progress_text != "":
				meter_cell += " [color=#" + Utils.COLOR_INFO + "]— " + progress_text + "[/color]"
			var hold_cell := ""
			if hold_needed > 0:
				var pips := ""
				for i in range(hold_needed):
					pips += "●" if i < hold_n else "○"
				hold_cell = "[color=#" + tone + "]" + pips + "[/color]"
				if folded:
					hold_cell = Utils.bb_hint(hold_cell, hold_text)
				elif hold_text != "":
					hold_cell += " [color=#" + Utils.COLOR_INFO + "]" + hold_text.replace("[", "[lb]") + "[/color]"
			elif not folded and hold_text != "":
				hold_cell = "[color=#" + Utils.COLOR_INFO + "]" + hold_text.replace("[", "[lb]") + "[/color]"
			# Session UI-5 interim fix (Nov 13): the status is a FLAT badge (ink in
			# its tone, no ground, no rim) - the filled "Open" block read as a button.
			design_rows.append([title_cell, meter_cell, hold_cell, "[color=#" + tone + "]" + tag_text + "[/color]"])
		if not design_rows.is_empty():
			out += Utils.bb_table(["Design", "Progress", "Hold", "Status"], design_rows, [], [5, 5, 2, 1], float(_balance_width()) - 16.0) + "\n"
		out += Utils.CARD_CLOSE
	var control = designs.get("control")
	if control is String and control != "":
		out += Utils.bb_lead("[color=#" + Utils.COLOR_INFO + "]  The road page: " + control.replace("[", "[lb]") + "[/color]\n", "dl.balance.designs")
	return out + "\n"

# =============================================================================

func _render_balance_of_europe():
	var boe = cached_data.get("balance_of_europe", {})
	if boe.is_empty():
		content_area.text = "[color=#" + Utils.COLOR_INFO + "]No data available.[/color]"
		return
	var bbcode = ""
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]BALANCE OF EUROPE[/color]\n"
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]────────────────[/color]\n"

	bbcode += "[color=#" + Utils.COLOR_HEADER + "]COALITION THREAT[/color]\n"

	var threat_level = int(boe.get("threat_level", 0))
	var threat_tier = str(boe.get("threat_tier", "LOW"))

	# Tier color
	var tier_color = Utils.COLOR_SUCCESS
	match threat_tier:
		"LOW":
			tier_color = Utils.COLOR_SUCCESS
		"MODERATE":
			tier_color = COLOR_AMBER
		"HIGH":
			tier_color = Utils.cv_hex(COLOR_RED)
		"CRITICAL":
			tier_color = Utils.cv_hex(COLOR_RED)
			_start_critical_pulse()
		_:
			tier_color = Utils.COLOR_INFO

	# SF7-X48: the bracket prints the alarm's one name (the dispatch's own);
	# the band above still colours it.
	var threat_name = str(boe.get("threat_name", ""))
	var tier_shown = threat_name if threat_name != "" else threat_tier
	# UXR3-F6 (Pre-Deploy S12 part 2): the tier is a word after a dash, not
	# a bracketed tag.
	# Session UI-2 (November 11, 2026): the threat as a LARGE gauge leading the
	# page — the figure in the title face, 0-100 across a wide meter with a
	# gilt tick at the brewing threshold and at the instant one.
	var gauge_proj = boe.get("threat_projection", {})
	var gauge_brews: int = 60
	var gauge_forms: int = 80
	if gauge_proj is Dictionary:
		gauge_brews = int(gauge_proj.get("brewing_threshold", 60))
		gauge_forms = int(gauge_proj.get("instant_threshold", 80))
	var bar_color = Utils.COLOR_SUCCESS
	if threat_level >= 60:
		bar_color = Utils.cv_hex(COLOR_RED)
	elif threat_level >= 30:
		bar_color = COLOR_AMBER
	# Session UI-4 (November 12, 2026): the three blind readers scored this page
	# 6/10 ("plain text blocks with a thin threat meter"). The threat is now a hero
	# block: the figure large in the title face with its tier as a tag, a gauge the
	# width of the page (the level, a ghost segment to where the next war of
	# conquest would take it, ticks at the brewing and the instant threshold), the
	# scale under its ticks, and a figure row. Folded, the old lines (the
	# thresholds, "Threat Level:", the projection) stand as the hero's hover;
	# On the page they print as they did.
	var folded: bool = Utils.explanations_folded()
	var projection = boe.get("threat_projection", {})
	var ghost_to: int = threat_level
	if projection is Dictionary and projection.has("after_next_war"):
		ghost_to = int(projection.get("after_next_war", threat_level))
	var gauge_w: int = _balance_width()
	var gauge_tip: String = str(gauge_brews) + " brews · " + str(gauge_forms) + " forms. Threat Level: " + str(threat_level) + " / 100 — " + tier_shown + "."
	var hero: String = Utils.bb_glyph("threat", 28, tier_color) + "  [font=" + Utils.TITLE_FONT + "][color=#" + tier_color + "]" + str(threat_level) + "[/color][/font]"
	hero += " [color=#" + Utils.COLOR_INFO + "]/ 100[/color]  " + Utils.bb_tag(threat_tier, tier_color) + "\n"
	# FA-D11 (slice 17, Phase 2): the one number a player plans around — the
	# backend computed it all along and no renderer read it.
	# IQ-2: a collapsed France is planning no war of conquest — the backend
	# sends the true reading of the alarm instead of the projection.
	var projection_collapse = projection.get("collapse_line", "") if projection is Dictionary else ""
	var projection_line := ""
	if projection_collapse is String and projection_collapse != "":
		pass
	elif projection is Dictionary and projection.size() > 0:
		var nxt = int(projection.get("after_next_war", threat_level))
		var brewing = int(projection.get("brewing_threshold", 60))
		var instant = int(projection.get("instant_threshold", 80))
		var to_brewing = int(projection.get("wars_until_brewing", 0))
		var to_instant = int(projection.get("wars_until_instant", 0))
		projection_line = "Next war of conquest: " + str(threat_level) + " → " + str(nxt)
		projection_line += " · brews at " + str(brewing) + " (" + (str(to_brewing) + " war" + ("s" if to_brewing != 1 else "") + " away" if to_brewing > 0 else "now") + ")"
		projection_line += " · forms at once at " + str(instant) + " (" + (str(to_instant) if to_instant > 0 else "now") + ")"
		var dissolve = int(boe.get("dissolution_threat_threshold", 20))
		projection_line += " · dissolves below " + str(dissolve)
	if folded:
		if projection_line != "":
			gauge_tip += " " + projection_line + "."
		bbcode += Utils.bb_hint(hero.trim_suffix("\n"), gauge_tip) + "\n"
	else:
		bbcode += hero
	bbcode += _threat_gauge(threat_level, gauge_w, 20, bar_color, [gauge_brews, gauge_forms], ghost_to) + "\n"
	bbcode += _gauge_scale_table(gauge_brews, gauge_forms)
	if not folded:
		bbcode += "[color=#" + Utils.COLOR_INFO + "]" + str(gauge_brews) + " brews · " + str(gauge_forms) + " forms[/color]" + "\n"
		bbcode += "Threat Level: [color=#" + tier_color + "]" + str(threat_level) + " / 100 — " + tier_shown + "[/color]" + "\n"
	if projection_collapse is String and projection_collapse != "":
		bbcode += "[color=#" + Utils.COLOR_ERROR + "]" + projection_collapse + "[/color]" + "\n"
	elif projection_line != "" and not folded:
		bbcode += "[color=#" + Utils.COLOR_INFO + "]" + projection_line + "[/color]" + "\n"
	bbcode += _balance_figures(boe, projection)
	bbcode += "\n"

	var headline_case = str(boe.get("headline_case", "NO_HEGEMON"))
	var hegemon = Utils.display_nation_name(str(boe.get("hegemon", "")))
	var share_pct = int(boe.get("hegemon_share", 0))  # S14E-X100: a whole percent from the backend
	var bloc_label = str(boe.get("bloc_label", ""))
	var descriptive_label = str(boe.get("descriptive_label", ""))
	var label = bloc_label if bloc_label != "" and bloc_label != "<null>" else descriptive_label
	if label == "" or label == "<null>":
		label = hegemon
	label = Utils.humanize_nation_keys_in_text(label)
	var bloc_members = boe.get("bloc_members", [])
	var member_line = ""
	if bloc_members is Array and bloc_members.size() > 1:
		var member_names = []
		for member in bloc_members:
			member_names.append(Utils.display_nation_name(str(member)))
		member_line = "Bloc members: " + ", ".join(PackedStringArray(member_names)) + ".\n"
	match headline_case:
		"ACTIVE_COALITION":
			var leader = Utils.display_nation_name(str(boe.get("coalition_leader", "")))
			bbcode += "[color=#" + Utils.cv_hex(COLOR_RED) + "]Coalition declared"
			if leader != "":
				bbcode += " under " + leader
			bbcode += ".[/color]\n\n"
		"BREWING":
			bbcode += "[color=#" + COLOR_AMBER + "]A coalition is brewing against " + label + ".[/color]\n\n"
		"COOLDOWN":
			bbcode += _cooldown_counsel(boe) + "\n"
		"HEGEMON_NO_COALITION":
			bbcode += "[color=#" + Utils.COLOR_INFO + "]" + label + " holds " + str(share_pct) + "% of active European bloc power.[/color]\n"
			var hegemon_power = int(boe.get("hegemon_power", 0))
			var total_power = int(boe.get("total_power", 0))
			if hegemon_power > 0 and total_power > 0:
				bbcode += "Power score: " + str(hegemon_power) + " / " + str(total_power) + ".\n"
			bbcode += "This counts " + hegemon + "'s direct allies and vassal bloc against all active courts. Alliance networks can overlap; the headline shows the current largest alignment.\n"
			if member_line != "":
				bbcode += member_line
			bbcode += "Warning bands: 33% noticed, 50% alarming, 60% crisis.\n\n"
		_:
			bbcode += "[color=#" + Utils.COLOR_INFO + "]No single court dominates the balance.[/color]\n\n"

	# VP-1 (S14b part 2, the record §6.2): THE EMPEROR'S DESIGNS — the road,
	# each design's progress, off the one payload (null: no designs authored).
	bbcode += _designs_block(boe.get("imperial_designs"))

	# Threat sources this turn (with human-readable labels)
	var sources = boe.get("threat_sources_this_turn", [])
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]This Turn's Sources:[/color]\n"
	if sources.size() == 0:
		bbcode += "  [color=#" + Utils.COLOR_INFO + "]No new threats[/color]\n"
	else:
		# Session UI-4 (November 12, 2026): one signed tag a source, in the
		# colour its line carried, on one wrapping line instead of a bulleted list.
		var source_tags: Array = []
		for s in sources:
			if s is Dictionary:
				var s_display = str(s.get("display", str(s)))
				var s_amount = int(s.get("amount", 0))
				var s_color = Utils.cv_hex(COLOR_RED) if s_amount > 0 else (Utils.COLOR_SUCCESS if s_amount < 0 else Utils.COLOR_INFO)
				source_tags.append(Utils.bb_tag(s_display.replace("[", "(").replace("]", ")"), s_color))
			else:
				source_tags.append(Utils.bb_tag(str(s).replace("[", "(").replace("]", ")"), Utils.COLOR_INFO))
		bbcode += "  " + "  ".join(PackedStringArray(source_tags)) + "\n"
	bbcode += "\n"

	# SF-LB-3 (Score Finish Step 7b): the next league — who would march,
	# when the courts consult and declare, what each court's war would
	# reopen, who pays her, and the price to keep her out. Every figure is
	# the backend's own forecast (shown = applied); the bare list below is
	# the pre-7b fallback (the lever down sends no rows).
	var league_rows = boe.get("league_rows", [])
	var league_line = str(boe.get("league_line", ""))
	if (league_rows is Array and league_rows.size() > 0) or league_line != "":
		bbcode += "[color=#" + Utils.COLOR_HEADER + "]THE NEXT LEAGUE[/color]\n"
		if league_line != "":
			bbcode += "[color=#" + COLOR_AMBER + "]" + league_line + "[/color]\n"
		if league_rows is Array:
			for lrow in league_rows:
				if not (lrow is Dictionary):
					continue
				var lstatus = str(lrow.get("status", ""))
				var lcolor = Utils.COLOR_INFO
				if lstatus == "joins" or lstatus == "refuses" or bool(lrow.get("out_of_time", false)):
					lcolor = Utils.cv_hex(COLOR_RED)
				elif lstatus == "bound":
					lcolor = COLOR_AMBER
				bbcode += "  • [color=#" + lcolor + "]" + str(lrow.get("text", "")) + "[/color]\n"
		var league_footer = str(boe.get("league_footer", ""))
		if league_footer != "":
			bbcode += "  [color=#" + Utils.COLOR_INFO + "]" + league_footer + "[/color]\n"
	else:
		var qualifying = boe.get("qualifying_nations", [])
		bbcode += "[color=#" + Utils.COLOR_HEADER + "]Nations That Would Join Coalition:[/color]\n"
		if qualifying.size() == 0:
			bbcode += "  [color=#" + Utils.COLOR_INFO + "]None currently[/color]\n"
		else:
			var qual_strs = []
			for q in qualifying:
				# Session UI-4: a flag and a name tag a court that would join.
				qual_strs.append(Utils.bb_flag(str(q), 16) + Utils.bb_tag(Utils.display_nation_name(str(q)), Utils.COLOR_BADGE_QUIET))
			bbcode += "  " + "  ".join(PackedStringArray(qual_strs)) + "\n"
	bbcode += "\n"

	# DY-1 (DYNAMISM_SPEC.md §3, Q6): the Alarm of Europe in words — the
	# courts whose appetite Europe has remarked. The backend composes every
	# sentence (R7) and never sends a figure.
	var alarm_lines = boe.get("alarm_lines", [])
	if alarm_lines is Array and alarm_lines.size() > 0:
		bbcode += "[color=#" + Utils.COLOR_HEADER + "]THE COURTS TAKE NOTE[/color]\n"
		for aline in alarm_lines:
			bbcode += "  [color=#" + COLOR_AMBER + "]" + str(aline) + "[/color]\n"
		bbcode += "\n"

	# DY-2 (DYNAMISM_SPEC.md §4): the Questions of Europe — one sentence a
	# table, composed by the backend (R7); never a bar, never a figure.
	var question_lines = boe.get("question_lines", [])
	if question_lines is Array and question_lines.size() > 0:
		bbcode += "[color=#" + Utils.COLOR_HEADER + "]THE QUESTIONS OF EUROPE[/color]\n"
		for qline in question_lines:
			bbcode += "  [color=#" + COLOR_AMBER + "]" + str(qline) + "[/color]\n"
		bbcode += "\n"

	# Coalition status
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]Coalition Status:[/color]\n"
	var coalition_state = str(boe.get("coalition_state", "NO_HEGEMON"))
	var brewing_turns = boe.get("brewing_turns_remaining")
	var active_coalition = boe.get("active_coalition")

	if active_coalition != null and active_coalition is Dictionary:
		var c_name = Utils.humanize_nation_keys_in_text(str(active_coalition.get("name", "Unknown")))
		var c_leader = Utils.display_nation_name(str(active_coalition.get("leader", "?")))
		var c_posture = str(active_coalition.get("posture", "defensive"))
		bbcode += "  [color=#" + Utils.cv_hex(COLOR_RED) + "]ACTIVE: " + c_name + " — Leader: " + c_leader + ", Posture: " + c_posture.capitalize() + "[/color]\n"
		bbcode += "  Combined Strength: " + str(active_coalition.get("combined_strength_display", "Unknown")) + "\n\n"

		# Per-member block — Session UI-2: a table (court, strength, exhaustion)
		var members = active_coalition.get("members", [])
		var member_rows: Array = []
		for mem in members:
			var m_nation = Utils.display_nation_name(str(mem.get("nation", "?")))
			var m_strength = str(mem.get("strength_display", "?"))
			var m_we = int(mem.get("war_exhaustion", 0))
			# FA-D11: which member is tiring — the backend's own trend, a glyph.
			var trend = str(mem.get("war_exhaustion_trend", ""))
			var trend_glyph = ""
			if trend == "rising":
				trend_glyph = " ▲"
			elif trend == "falling":
				trend_glyph = " ▼"
			elif trend != "":
				trend_glyph = " –"
			# AI-4c: exhaustion runs to WAR_EXHAUSTION_MAX (200), not 100 —
			# a saturated court used to read "WE: 200/100".
			var we_max = int(boe.get("war_exhaustion_max", 200))
			if we_max <= 0:
				we_max = 200

			# Mini WE bar (10 chars)
			var we_filled = int(round(float(m_we) / float(we_max) * 10.0))
			if we_filled > 10:
				we_filled = 10
			if we_filled < 0:
				we_filled = 0
			var we_empty = 10 - we_filled
			var we_color := Utils.COLOR_WARNING if we_filled >= 5 else Utils.COLOR_INFO
			member_rows.append([Utils.bb_flag(str(mem.get("nation", "?")), 16) + " " + m_nation + " ", m_strength + " ",
				"WE: " + str(m_we) + "/" + str(we_max) + "  " + Utils.bb_bar_img(we_filled, we_color, 110, 12)])
		if not member_rows.is_empty():
			bbcode += Utils.bb_table(["Member", "Strength", "Exhaustion"], member_rows, [], [2, 2, 3]) + "\n"
	elif coalition_state == "BREWING":
		var turns_str = ""
		if brewing_turns != null:
			turns_str = str(int(brewing_turns))
		else:
			turns_str = "?"
		# SF-RR7: a brew the Congress holds waits on Paris — no countdown.
		var brewing_paris_v = boe.get("brewing_waits_on_paris")
		var brewing_paris: String = brewing_paris_v if brewing_paris_v is String else ""
		if brewing_paris != "":
			bbcode += "  [color=#" + COLOR_AMBER + "]Brewing — " + brewing_paris + "[/color]\n"
		else:
			bbcode += "  [color=#" + COLOR_AMBER + "]Brewing — " + turns_str + " turns until formation[/color]\n"
	else:
		var coalition_cooldown = int(boe.get("coalition_cooldown", 0))
		if coalition_cooldown > 0:
			bbcode += "  [color=#" + Utils.COLOR_INFO + "]No coalition active. Post-dissolution cooldown: " + str(coalition_cooldown) + " turns.[/color]\n"
		else:
			bbcode += "  [color=#" + Utils.COLOR_INFO + "]No coalition active.[/color]\n"

	# AI-2e §3.7 (Stage C): the paymaster's purse, visible and
	# contestable — payer, client, amount, and how to take the client
	# away. Backend-composed lines; null omits the block.
	var subsidy = boe.get("paymaster_subsidy")
	if subsidy != null and subsidy is Dictionary:
		var subsidy_line = str(subsidy.get("line", ""))
		if subsidy_line != "":
			bbcode += "\n[b]THE PAYMASTER'S PURSE[/b]\n"
			bbcode += "  [color=#" + Utils.COLOR_GOLD + "]" + Utils.humanize_nation_keys_in_text(subsidy_line) + "[/color]\n"
			var subsidy_counter = str(subsidy.get("counterplay", ""))
			if subsidy_counter != "":
				bbcode += "  [color=#" + Utils.COLOR_INFO + "]" + subsidy_counter + "[/color]\n"

	# Dissolution conditions — the TWO the engine actually tests
	# (coalition.check_dissolution). The retired war-exhaustion clause
	# promised a lever that never existed: a live campaign showed a member
	# pinned at the exhaustion cap with the coalition still standing.
	bbcode += "\n[color=#" + Utils.COLOR_INFO + "]Coalition dissolves if threat falls below "
	bbcode += str(int(boe.get("dissolution_threat_threshold", 20)))
	bbcode += " or fewer than "
	bbcode += str(int(boe.get("dissolution_min_members", 2)))
	bbcode += " members remain at war.[/color]\n"

	content_area.text = Utils.dress_heads(bbcode)


# =============================================================================
# TAB 4: TALLEYRAND
# =============================================================================

func _cooldown_counsel(boe: Dictionary) -> String:
	"""IQ-3's spent-league counsel (the COOLDOWN headline): the courts are
	recovering from the last coalition, for how long, and — IQ-2, under the
	collapse — the backend's note naming the courts still fighting us."""
	var cooldown = int(boe.get("cooldown_turns_remaining", 0))
	var line: String = "[color=#" + Utils.COLOR_INFO + "]The courts are recovering from the last coalition."
	if cooldown > 0:
		line += " Cooldown: " + str(cooldown) + " turns."
	var cooldown_note = boe.get("headline_note", "")
	if cooldown_note is String and cooldown_note != "":
		line += " " + cooldown_note
	return line + "[/color]\n"


func _render_talleyrand():
	var t = cached_data.get("talleyrand", {})
	var bbcode = ""
	# UXR3-29 (Pre-Deploy S12 part 2): while the league is spent, its
	# counsel LEADS Talleyrand's book — the one thing he would tell you first.
	var boe_t = cached_data.get("balance_of_europe", {})
	if boe_t is Dictionary and str(boe_t.get("headline_case", "")) == "COOLDOWN":
		bbcode += "[color=#" + Utils.COLOR_HEADER + "]THE LEAGUE IS SPENT[/color]\n" + _cooldown_counsel(boe_t) + "\n"

	var authority = int(t.get("authority", 60))
	var authority_label = str(t.get("authority_label", "Stable"))
	var skill = int(t.get("skill", 0))
	var dp_remaining = int(t.get("dp_remaining", 0))
	var dp_max = int(t.get("dp_max", 3))

	# Authority label color (PL-23: trust → authority)
	var authority_color = Utils.COLOR_INFO
	if AUTHORITY_ARMS_READ_THE_BACKEND:
		# IQ-2 (Sept 14, 2026): the arms below the `else` tested a vocabulary
		# the backend never emits — `AuthorityTracker.get_authority_label`
		# says "Divine Right / Commanding / Respected / Questionable / Emperor
		# in Name Only" — so no arm ever fired and "Emperor in Name Only"
		# rendered in the same neutral grey as "Divine Right".
		match authority_label:
			"Divine Right", "Commanding":
				authority_color = Utils.COLOR_SUCCESS
			"Respected":
				authority_color = Utils.COLOR_INFO
			"Questionable":
				authority_color = Utils.COLOR_ORANGE
			"Emperor in Name Only":
				authority_color = Utils.COLOR_ERROR
	else:
		match authority_label:
			"Absolute":
				authority_color = Utils.COLOR_SUCCESS
			"Strong":
				authority_color = Utils.COLOR_SUCCESS
			"Stable":
				authority_color = Utils.COLOR_INFO
			"Shaky":
				authority_color = Utils.COLOR_ORANGE
			"Crumbling":
				authority_color = Utils.COLOR_ERROR

	bbcode += "[color=#" + Utils.COLOR_HEADER + "]TALLEYRAND[/color] — [color=#" + authority_color + "]" + authority_label + "[/color]\n"
	# Session UI-2 (November 11, 2026): his figures lead as one line — a glyph
	# for each, the authority on a meter.
	bbcode += Utils.bb_glyph("authority", 18, authority_color) + " Authority: [color=#" + authority_color + "]" + str(authority) + "[/color]/100 "
	bbcode += Utils.bb_meter(authority, 100, 110, 8, authority_color)
	bbcode += "   " + Utils.bb_glyph("envoy", 18, Utils.COLOR_GOLD) + " Skill: " + str(skill)
	bbcode += "   " + Utils.bb_glyph("dp", 18, Utils.COLOR_GOLD) + " DP: [color=#" + Utils.COLOR_GOLD + "]" + str(dp_remaining) + "/" + str(dp_max) + "[/color]\n"

	# TA3: DP Breakdown
	var dp_breakdown = t.get("dp_breakdown")
	if dp_breakdown != null and dp_breakdown is Dictionary:
		var bp_base = int(dp_breakdown.get("base", 3))
		var bp_skill = int(dp_breakdown.get("skill_bonus", 0))
		var bp_auth = int(dp_breakdown.get("authority_bonus", 0))
		var bp_cap = int(dp_breakdown.get("capital_penalty", 0))
		bbcode += "  (Base " + str(bp_base)
		if bp_skill != 0:
			var sk_sign = "+" if bp_skill > 0 else ""
			bbcode += " + Skill " + sk_sign + str(bp_skill)
		if bp_auth != 0:
			var au_sign = "+" if bp_auth > 0 else ""
			bbcode += " + Authority " + au_sign + str(bp_auth)
		if bp_cap != 0:
			bbcode += " + Capital [color=#" + Utils.cv_hex(COLOR_RED) + "]" + str(bp_cap) + "[/color]"
		# NP-5 THE SEAT (N11): the Emperor holds court in the capital.
		var bp_seat = int(dp_breakdown.get("seat_bonus", 0))
		if bp_seat != 0:
			bbcode += " + The Seat [color=#" + Utils.COLOR_GOLD + "]+" + str(bp_seat) + "[/color]"
		bbcode += ")\n"
		if bp_seat != 0:
			bbcode += "  [color=#" + Utils.COLOR_GOLD + "]The Emperor is at the Tuileries — the courts attend him.[/color]\n"
	bbcode += "\n"

	# UI-6: the W6-9 assessment verb as a chip — the war room + executable
	# counsel render in the terminal, so main.gd closes the ledger first.
	bbcode += "  " + Utils.bb_button_chip("talleyrand_assess", "Assess the Situation", Utils.COLOR_GOLD, "233043")
	bbcode += "  [color=#" + Utils.COLOR_INFO + "]his full survey of the war, the treasury, and the courts[/color]\n\n"

	# Current mission
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]CURRENT MISSION[/color]\n"
	var mission = t.get("active_mission")
	if mission == null or not (mission is Dictionary):
		bbcode += "  [color=#" + Utils.COLOR_INFO + "]Idle — no active diplomatic mission.[/color]\n"
		# IQ-4: how his last mission ended, when the ledger carries it.
		var last_mission = t.get("last_mission")
		if last_mission is Dictionary and not last_mission.is_empty():
			var last_phrase = str(last_mission.get("reason_phrase", last_mission.get("reason", "")))
			bbcode += "  [color=#" + Utils.COLOR_INFO + "]Last mission: " + str(last_mission.get("type_display", "?")) + " — " + str(last_mission.get("target_display", "?")) + ", " + last_phrase + ".[/color]\n"
	else:
		var m_type = str(mission.get("type", "?"))
		var m_target = Utils.display_nation_name(str(mission.get("target", "?")))
		var m_duration = int(mission.get("duration", 0))
		var m_paused = mission.get("paused", false)
		var status = "Active"
		if m_paused:
			status = "Paused"
		# IQ-4: the backend's display name (display_names.MISSION_TYPE_DISPLAY)
		# when present — never the raw key with its underscores swapped.
		var m_type_display = str(mission.get("type_display", ""))
		if m_type_display == "":
			m_type_display = m_type.replace("_", " ").capitalize()
		bbcode += "  " + Utils.bb_glyph("envoy", 16, Utils.COLOR_GOLD) + " [b]" + m_type_display + " → " + m_target + "[/b]\n"
		# Session UI-2: the rest of the mission a label / value table (a row a
		# line of the old page, its words unchanged).
		var mission_facts: Array = []

		# DPF-2: Descriptor-based progress
		var initial_desc = str(mission.get("initial_descriptor", ""))
		var current_desc = str(mission.get("current_descriptor", ""))
		var relation_delta = int(mission.get("relation_delta", 0))
		if initial_desc != "" and current_desc != "":
			var delta_str = str(relation_delta) if relation_delta < 0 else "+" + str(relation_delta)
			var arrow_color = Utils.COLOR_INFO
			if relation_delta > 0:
				arrow_color = Utils.COLOR_SUCCESS
			elif relation_delta < 0:
				arrow_color = Utils.cv_hex(COLOR_RED)
			if initial_desc != current_desc:
				mission_facts.append([_fact_label("intel", ""), "[color=#" + arrow_color + "]" + initial_desc + " → " + current_desc + " (" + delta_str + ", " + str(m_duration) + " turns)[/color]"])
			else:
				mission_facts.append([_fact_label("intel", ""), "[color=#" + arrow_color + "]" + current_desc + " (" + delta_str + " over " + str(m_duration) + " turns)[/color]"])
		else:
			mission_facts.append([_fact_label("intel", ""), "Progress: N/A (mission predates tracking)"])

		# S14E-9: the mission's books — earned, shocks with their cause, the
		# turns paused (the backend's one line, as the Cabinet row prints it).
		var ledger_line = str(mission.get("ledger_line", ""))
		if ledger_line != "" and ledger_line != "<null>":
			mission_facts.append([_fact_label("letter", ""), "[color=#" + Utils.COLOR_INFO + "]So far: " + ledger_line + "[/color]"])

		var status_cell: String = "Status: " + status
		# TA4: Mission effect text
		var effect_text = str(mission.get("effect_text", ""))
		var dp_cost = int(mission.get("dp_cost_per_turn", 0))
		if dp_cost > 0:
			status_cell += ", Cost: " + str(dp_cost) + " DP/turn"
		mission_facts.append([_fact_label("turn", ""), status_cell])
		if effect_text:
			mission_facts.append([_fact_label("cabinet", ""), "[color=#" + Utils.COLOR_INFO + "]Effect: " + effect_text + "[/color]"])

		# IQ-4: the one-source forecast (mission_status.remaining_note, with its
		# net per turn) replaces both the old count and "Ongoing" when present.
		var remaining_note = str(mission.get("remaining_note", ""))
		if remaining_note != "" and remaining_note != "<null>":
			var net_clause = ""
			# IQ-4 review: UNDERMINE's pair is moved by other courts too, so
			# its figure is not a net — the note carries its terms instead.
			if mission.has("net_per_turn") and m_type != "GATHER_INTEL" and m_type != "UNDERMINE_ALLIANCE":
				var mission_net = int(mission.get("net_per_turn", 0))
				net_clause = "Net " + ("+" if mission_net >= 0 else "") + str(mission_net) + " a turn · "
			mission_facts.append([_fact_label("march", ""), "[color=#" + Utils.COLOR_GOLD + "]" + net_clause + remaining_note + "[/color]"])
		else:
			# TA5: Remaining turns (the pre-IQ-4 render, kept for an absent key)
			var remaining = mission.get("remaining_turns")
			if remaining != null:
				mission_facts.append([_fact_label("march", ""), "[color=#" + Utils.COLOR_GOLD + "]Completes in " + Utils.plural(int(remaining), "turn") + "[/color]"])
			else:
				mission_facts.append([_fact_label("march", ""), "[color=#" + Utils.COLOR_INFO + "]Ongoing[/color]"])
		bbcode += _facts_table(mission_facts)
	bbcode += "\n"

	# Proposal in transit
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]PROPOSAL IN TRANSIT[/color]\n"
	var pit = t.get("proposal_in_transit")
	if pit == null or not (pit is Dictionary):
		bbcode += "  [color=#" + Utils.COLOR_INFO + "]None[/color]\n"
	else:
		var p_target = Utils.display_nation_name(str(pit.get("target", "?")))
		var p_type = str(pit.get("type", "?"))
		var p_eta = int(pit.get("eta", 0))
		bbcode += "  To " + p_target + ": " + p_type.replace("_", " ").capitalize()
		bbcode += ", ETA: " + str(p_eta) + " turns\n"
	bbcode += "\n"

	# Pending envoys
	var pending_count = int(t.get("pending_envoy_count", 0))
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]PENDING ENVOYS[/color]\n"
	bbcode += "  " + Utils.plural(pending_count, "envoy") + " awaiting response\n\n"

	# Sabotage warnings
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]SABOTAGE WARNINGS[/color]\n"
	var warnings = t.get("sabotage_warnings", [])
	if warnings.size() == 0:
		bbcode += "  [color=#" + Utils.COLOR_INFO + "]None detected.[/color]\n"
	else:
		for w in warnings:
			if w is Dictionary:
				var w_target = Utils.display_nation_name(str(w.get("target", "?")))
				var w_type = str(w.get("type", "?"))
				bbcode += "  [color=#" + Utils.COLOR_ERROR + "]WARNING: " + w_type + " targeting " + w_target + "[/color]\n"
			else:
				bbcode += "  [color=#" + Utils.COLOR_ERROR + "]" + str(w) + "[/color]\n"
	bbcode += "\n"

	# TA2: Diplomatic reliability
	var reliability = int(t.get("diplomatic_reliability", 0))
	var rel_desc = ""
	var rel_color = Utils.COLOR_INFO
	if reliability >= 30:
		rel_desc = "Honorable"
		rel_color = Utils.COLOR_SUCCESS
	elif reliability >= 0:
		rel_desc = "Neutral"
		rel_color = Utils.COLOR_INFO
	elif reliability >= -30:
		rel_desc = "Unreliable"
		rel_color = COLOR_AMBER
	else:
		rel_desc = "Treacherous"
		rel_color = Utils.cv_hex(COLOR_RED)
	var rel_sign = "+" if reliability > 0 else ""
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]DIPLOMATIC RELIABILITY[/color]\n"
	bbcode += "  Reliability: [color=#" + rel_color + "]" + rel_sign + str(reliability) + " (" + rel_desc + ")[/color]  " + Utils.bb_relation_meter(reliability, 110, 7) + "\n\n"

	# TA1: Diplomatic history
	var history = t.get("diplomatic_history", [])
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]DIPLOMATIC HISTORY[/color]\n"
	if history.size() == 0:
		bbcode += "  [color=#" + Utils.COLOR_INFO + "]No diplomatic events recorded.[/color]\n"
	else:
		# Show last 10 entries
		var start_idx = max(0, history.size() - 10)
		var history_rows: Array = []
		for i in range(start_idx, history.size()):
			var entry = history[i]
			if entry is Dictionary:
				var h_turn = int(entry.get("turn", 0))
				var h_type = str(entry.get("type") if entry.get("type") != null else "?")
				var h_target = Utils.display_nation_name(str(entry.get("target", "")))
				var h_nation = str(entry.get("nation", ""))
				var h_detail = str(entry.get("detail", ""))
				# Color by type
				var h_color = Utils.COLOR_INFO
				if h_type != "?" and "accept" in h_type.to_lower():
					h_color = Utils.COLOR_SUCCESS
				elif h_type != "?" and ("war" in h_type.to_lower() or "break" in h_type.to_lower()):
					h_color = Utils.cv_hex(COLOR_RED)
				var h_text = h_type.replace("_", " ").capitalize()
				if h_target:
					h_text += " — " + h_target
				if h_detail:
					h_text += " (" + h_detail + ")"
				history_rows.append(["Turn " + str(h_turn) + ": ", "[color=#" + h_color + "]" + h_text + "[/color]"])
			else:
				history_rows.append(["", str(entry)])
		if not history_rows.is_empty():
			bbcode += Utils.bb_table(["Turn", "Event"], history_rows, [], [1, 5]) + "\n"

	content_area.text = Utils.dress_heads(bbcode)


# =============================================================================
# TAB 5: WAR BARGAINS
# =============================================================================

func _render_war_bargains():
	var bargains = cached_data.get("war_bargains", [])
	var bbcode = ""
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]═══ WAR BARGAINS ═══[/color]\n\n"

	if bargains.size() == 0:
		bbcode += "[color=#" + Utils.COLOR_INFO + "]No war bargains recorded.[/color]\n"
		content_area.text = Utils.dress_heads(bbcode)
		return

	var live = []
	var completed = []
	for b in bargains:
		var status = str(b.get("status", ""))
		if status == "active" or status == "triggered":
			live.append(b)
		else:
			completed.append(b)

	if live.size() > 0:
		bbcode += "[color=#" + Utils.COLOR_HEADER + "]ACTIVE BARGAINS[/color]\n"
		for b in live:
			bbcode += _format_bargain_entry(b)
		bbcode += "\n"

	if completed.size() > 0:
		bbcode += "[color=#" + Utils.COLOR_HEADER + "]COMPLETED BARGAINS[/color]\n"
		for b in completed:
			bbcode += _format_bargain_entry(b)

	content_area.text = Utils.dress_heads(bbcode)


func _format_bargain_entry(b: Dictionary) -> String:
	var promiser = Utils.display_nation_name(str(b.get("promiser", "?")))
	var beneficiary = Utils.display_nation_name(str(b.get("beneficiary", "?")))
	var named_enemy = Utils.display_nation_name(str(b.get("named_enemy", "?")))
	var claim_region = str(b.get("claim_region", "?"))
	var status = str(b.get("status", "?"))
	var created_turn = int(b.get("created_turn", 0))

	var status_color = Utils.COLOR_INFO
	match status:
		"active":
			status_color = Utils.COLOR_BLUE
		"triggered":
			status_color = COLOR_AMBER
		"fulfilled":
			status_color = Utils.COLOR_SUCCESS
		"breached":
			status_color = Utils.COLOR_ERROR
		"void":
			status_color = Utils.COLOR_INFO

	var entry = ""
	# Session UI-2 (November 11, 2026): the bargain's header row — the two
	# courts' arms and names, its status a badge — over a facts table.
	var status_tone = Utils.COLOR_BADGE_QUIET
	match status:
		"active":
			status_tone = "3a4a6b"
		"triggered":
			status_tone = "8a6d2a"
		"fulfilled":
			status_tone = Utils.cv_hex("2f6b3a")
		"breached":
			status_tone = Utils.cv_hex("8b2a2a")
	entry += "  " + Utils.bb_flag(str(b.get("promiser", "")), 16) + " [color=#" + Utils.COLOR_GOLD + "][b]" + promiser + " → " + beneficiary + "[/b][/color]"
	entry += "  " + Utils.bb_badge(status.to_upper(), status_tone) + "\n"
	var bargain_facts: Array = []
	bargain_facts.append([_fact_label("war", "Enemy: "), named_enemy + "   Claim: " + claim_region])
	var sealed_cell: String = "Turn " + str(created_turn)

	var badge = str(b.get("badge", ""))
	if badge != "":
		var badge_color = Utils.COLOR_INFO
		match badge:
			"honoured":
				badge_color = Utils.COLOR_SUCCESS
			"broken":
				badge_color = Utils.COLOR_ERROR
			"lapsed":
				badge_color = Utils.COLOR_INFO
		sealed_cell += "   [color=#" + badge_color + "]" + badge.to_upper() + "[/color]"

	var ended_turn = b.get("ended_turn")
	if ended_turn != null:
		sealed_cell += "   Ended: Turn " + str(int(ended_turn))

	var end_reason = str(b.get("end_reason", ""))
	if end_reason != "":
		sealed_cell += "   (" + end_reason.replace("_", " ") + ")"
	bargain_facts.append([_fact_label("medal", "Sealed: "), sealed_cell])

	var cooldown = int(b.get("cooldown_remaining", 0))
	if cooldown > 0:
		bargain_facts.append([_fact_label("turn", "Cooldown: "), "[color=#" + COLOR_AMBER + "]" + str(cooldown) + " turns[/color]"])

	entry += _facts_table(bargain_facts)
	entry += "\n"
	return entry


# =============================================================================
# TAB 6: VASSALS (UI-6 — client states with action chips)
# =============================================================================

const _LOYALTY_BAR_W = 150
const _LOYALTY_BAR_H = 13

func _render_vassals():
	var vassal_data = cached_data.get("vassals", {})
	var rows = vassal_data.get("rows", [])
	var bbcode = ""
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]═══ CLIENT STATES ═══[/color]\n\n"

	if rows.size() == 0:
		bbcode += "[color=#" + Utils.COLOR_INFO + "]France holds no client states.[/color]\n\n"
		bbcode += "[color=#" + Utils.COLOR_INFO + "]Bind a minor power to the Empire: vassalize a court marked "
		bbcode += "[color=#" + Utils.COLOR_GOLD + "]★ Vassalizable[/color][color=#" + Utils.COLOR_INFO + "] on the Nations tab "
		bbcode += "once she is beaten (F1 → the court → Subjugate), demand vassalage at the peace table, or propose it through the Cabinet (F1).[/color]\n"
		content_area.text = Utils.dress_heads(bbcode)
		return

	var total_tribute = int(vassal_data.get("total_tribute", 0))
	bbcode += "[color=#" + Utils.COLOR_INFO + "]" + str(rows.size()) + " client state" + ("s" if rows.size() != 1 else "")
	bbcode += " remit [color=#" + Utils.COLOR_GOLD + "]+" + Utils.format_number(total_tribute) + "g/turn[/color] in tribute.[/color]\n"
	if vassal_data.get("actions_blocked", false):
		# S14G-X25 (Pre-Deploy S14h part 1, October 26, 2026): the notice names
		# what suspends the instruments - the court whose letter stands, or the
		# dialogue awaiting an answer - where it said "Envoys await your reply"
		# with no one in it (and "envoys" for a hard-stop dialogue too).
		bbcode += "[color=#" + COLOR_AMBER + "]" + _vassal_block_notice(vassal_data) + "[/color]\n"
	bbcode += "\n"

	# UXR3-81 (Pre-Deploy S15 head, October 25, 2026): a court whose petition
	# was GRANTED is listed first (the book's own order otherwise, kept), and
	# its Bond line leads its card — the grant's result is what the first
	# screenful shows, not two cards reading "no bond yet".
	var granted_rows: Array = []
	var other_rows: Array = []
	for v in rows:
		if v is Dictionary and _vassal_petition_granted(v):
			granted_rows.append(v)
		else:
			other_rows.append(v)
	for v in granted_rows + other_rows:
		bbcode += _format_vassal_card(v, bool(vassal_data.get("actions_blocked", false)))

	content_area.text = Utils.dress_heads(bbcode)


func _vassal_block_notice(vassal_data: Dictionary) -> String:
	"""S14G-X25: the Vassals tab's suspended-instruments notice, naming its
	cause (the backend's `blocked_by`: "letter" with `blocked_by_courts`, or
	"dialogue" with `blocked_by_dialogue`). A letter's lead is the lock's one
	wording (`Utils.cabinet_shut_lead`): "Austria's letter stands unanswered —
	vassal instruments are suspended until it is answered." A dialogue's name is
	a number-neutral noun phrase, so the sentence closes on "the matter"."""
	var blocked_by = str(vassal_data.get("blocked_by", ""))
	if blocked_by == "letter":
		var courts = vassal_data.get("blocked_by_courts", [])
		if not (courts is Array):
			courts = []
		var answered = "they are answered." if courts.size() > 1 else "it is answered."
		return Utils.cabinet_shut_lead(courts, true) + "vassal instruments are suspended until " + answered
	if blocked_by == "dialogue":
		var dialogue_name = str(vassal_data.get("blocked_by_dialogue", ""))
		if dialogue_name != "":
			return "You have " + dialogue_name + " awaiting your answer — vassal instruments are suspended until the matter is answered."
	return "A matter awaits your reply — vassal instruments are suspended until the matter is answered."


func _vassal_petition_granted(v: Dictionary) -> bool:
	"""UXR3-81: a granted petition leaves two marks on the client's row — the
	bond it earned (`relation_modifier`, +1/turn per honoured petition: the
	`petition_standing_keys` term) and the tribute it remitted
	(`remission_left`). Either one is "a court with a granted petition"."""
	return int(v.get("relation_modifier", 0)) > 0 or int(v.get("remission_left", 0)) > 0


func _format_vassal_card(v: Dictionary, actions_blocked: bool) -> String:
	var bbcode = ""
	var name = str(v.get("name", "?"))
	var loyalty = int(v.get("loyalty", 50))
	var autonomy_name = str(v.get("autonomy_name", "Satellite"))
	var path = str(v.get("path", "treaty"))
	var created_turn = int(v.get("created_turn", 0))

	# ── Header: flag + name + autonomy + provenance ──
	bbcode += Utils.card_open()    # Session UI: a client a card
	# Session UI-2 (November 11, 2026): the client's name in the title face, its
	# autonomy a badge, its provenance in words after it.
	bbcode += Utils.bb_flag(name, 18) + " "
	bbcode += Utils.HEAD_OPEN + Utils.display_nation_name(name) + Utils.HEAD_CLOSE
	bbcode += "  " + Utils.bb_badge(autonomy_name, "8a6d2a")
	# UI-6 review fix (UI6-R1): three-way path label — the 1805 boot vassals
	# are seeded with path "scenario" (an authoring fact, not an in-game
	# conquest), so the old two-way branch mislabeled all three as conquests.
	var path_label = ""
	match path:
		"treaty":
			path_label = "sworn by treaty"
		"conquest":
			path_label = "subjugated by conquest"
		_:
			path_label = "client state of the Empire"
	bbcode += "  [color=#" + Utils.COLOR_INFO + "](" + path_label
	if created_turn > 0 and path != "scenario":
		bbcode += ", Turn " + str(created_turn)
	bbcode += ")[/color]"
	# Session UI-4 (November 12, 2026): the readers found the cards "dense lines"
	# with the secondary rows (Standing, Bond) as prose. Folded, a standing that
	# blocks a petition ("5 turns until it may ask") and a bond not yet earned
	# ("no bond yet — ...") become tags in this header line, their full words the
	# tags' hover; On the page the rows stand as they were (further down).
	var fold_standing := false
	var fold_bond := false
	if Utils.explanations_folded():
		var standing_words: String = str(v.get("standing", ""))
		if v.has("standing") and standing_words != "may petition" and standing_words != "":
			fold_standing = true
			var standing_tag: String = standing_words
			var count_end: int = standing_words.find(" until it may ask")
			if count_end > 0 and standing_words.substr(0, count_end).split(" ")[0].is_valid_int():
				standing_tag = "asks in " + standing_words.substr(0, count_end)
			bbcode += "  " + Utils.bb_hint(Utils.bb_tag(standing_tag, Utils.COLOR_BADGE_QUIET), standing_words)
		var header_bond: String = _vassal_bond_text(v)
		if v.has("bond") and header_bond.begins_with("no bond yet") and not _vassal_petition_granted(v):
			fold_bond = true
			bbcode += "  " + Utils.bb_hint(Utils.bb_tag("no bond yet", Utils.COLOR_BADGE_QUIET), header_bond)
	# Session UI-3 (November 12, 2026): the client's foreign-policy sentence
	# stands behind an ⓘ after its header line (On the page it prints below).
	var policy_line = str(v.get("policy_line", ""))
	var pact_id: String = "dl.vassals.pact." + name
	if policy_line != "":
		bbcode += Utils.lead_mark(policy_line, pact_id)
	bbcode += "\n"
	# DY-7 (DYNAMISM_SPEC.md §6): a crown's card — the title, who reigns, who
	# withholds recognition. Backend-composed (R7); an empty line is omitted.
	var crown_line = str(v.get("crown_line", ""))
	if crown_line != "":
		bbcode += "  Crown: [color=#" + Utils.COLOR_GOLD + "]" + Utils.humanize_nation_keys_in_text(crown_line) + "[/color]\n"
	# Session G3: the client's foreign policy is its lord's — one
	# backend-composed line (R7); an empty line is omitted.
	if policy_line != "":
		bbcode += Utils.bb_lead("  [color=#" + Utils.COLOR_INFO + "]" + policy_line + "[/color]\n", pact_id)

	# UXR3-81 (S15 head): a court with a granted petition leads with its BOND
	# — the line the grant earned — straight under its header.
	var bond_led: bool = _vassal_petition_granted(v) and v.has("bond") and _vassal_bond_text(v) != ""
	if bond_led:
		var bond_ink: String = Utils.COLOR_SUCCESS if int(v.get("relation_modifier", 0)) > 0 else Utils.COLOR_INFO
		bbcode += "  Bond: [color=#" + bond_ink + "]" + _vassal_bond_text(v) + "[/color]\n"

	# ── Loyalty bar + trend forecast ──
	# Session UI-2: an exact meter (the figure and the forecast beside it).
	var loyalty_color = Utils.COLOR_SUCCESS
	if loyalty < 35:
		loyalty_color = Utils.COLOR_ERROR
	elif loyalty < 60:
		loyalty_color = COLOR_AMBER
	bbcode += "  " + Utils.bb_meter(loyalty, 100, _LOYALTY_BAR_W, _LOYALTY_BAR_H, loyalty_color)
	bbcode += "  Loyalty [color=#" + loyalty_color + "]" + str(loyalty) + "/100[/color]"
	var forecast = int(v.get("loyalty_forecast", 0))
	var trend = str(v.get("loyalty_trend", "stable"))
	var forecast_sign = "+" if forecast > 0 else ""
	match trend:
		"rising":
			bbcode += "  [color=#" + Utils.COLOR_SUCCESS + "]↑ " + forecast_sign + str(forecast) + "/turn[/color]"
		"falling":
			bbcode += "  [color=#" + Utils.COLOR_ERROR + "]↓ " + str(forecast) + "/turn[/color]"
		_:
			bbcode += "  [color=#" + Utils.COLOR_INFO + "]≈ steady[/color]"
	bbcode += "\n"

	# ── Warning band + the grip-aware recovery hint ──
	var warning = str(v.get("warning", ""))
	if warning != "":
		var warn_color = Utils.COLOR_ERROR if warning != "warning" else COLOR_AMBER
		var warn_label = ""
		match warning:
			"critical":
				warn_label = "REBELLION IMMINENT"
			"urgent":
				warn_label = "LOYALTY FAILING"
			_:
				warn_label = "Loyalty slipping"
		bbcode += "  [color=#" + warn_color + "]⚠ " + warn_label + "[/color]"
		var hint = str(v.get("recovery_hint", ""))
		if hint != "":
			bbcode += "  [color=#" + Utils.COLOR_INFO + "]" + hint + "[/color]"
		bbcode += "\n"

	# Session UI-2: the levers' facts as a label / value table — every line of
	# the old card a row, in its order, its words unchanged.
	var facts: Array = []

	# ── Tribute + contribution tier ──
	var tribute = int(v.get("tribute", 0))
	var tribute_pct = int(v.get("tribute_rate_pct", 75))
	var tribute_cell := ""
	if v.has("tribute_note"):
		# SFR-B7: the backend's line names a zero's cause (a remission, an
		# invaded client); an old payload keeps the old line.
		tribute_cell += "[color=#" + Utils.COLOR_GOLD + "]" + str(v.get("tribute_note", "")) + "[/color]"
	else:
		tribute_cell += "[color=#" + Utils.COLOR_GOLD + "]+" + Utils.format_number(tribute) + "g/turn[/color]"
		tribute_cell += " [color=#" + Utils.COLOR_INFO + "](" + str(tribute_pct) + "% of their income)[/color]"
	var contribution = str(v.get("contribution", "loyal"))
	match contribution:
		"loyal":
			tribute_cell += "   [color=#" + Utils.COLOR_SUCCESS + "]Answers the call to arms[/color]"
		"wavering":
			# IQ-7 review [22]: the regiments clause is a claim about VS-4
			# Rule 1b, which only bites when the lord fields a corps of the
			# vassal's own colours. The backend says whether it does
			# (`wavering_regiments`, present only with THE_WAVERING_LINE_IS_
			# HONEST up); an old payload without the key keeps the old line.
			var drag = bool(v.get("wavering_regiments", true))
			if drag:
				tribute_cell += "   [color=#" + COLOR_AMBER + "]Wavering — their marshals drag their feet[/color]"
			else:
				tribute_cell += "   [color=#" + COLOR_AMBER + "]Wavering — no standing to petition[/color]"
		"disaffected":
			tribute_cell += "   [color=#" + Utils.COLOR_ERROR + "]Disaffected — refuses new calls to arms[/color]"
	facts.append([_fact_label("gold", "Tribute: "), tribute_cell])

	# ── IQ-7 The Client's Petition: standing, cadence, bond, remission ──
	# Every key is display-only and present only when the backend's
	# THE_CLIENT_PETITIONS lever is up (diplomatic_ledger._build_vassals),
	# so a payload without them renders this card exactly as before.
	if v.has("standing"):
		# IQ-7 review R7 ([08]/[20]): `standing` reads "may petition" ONLY
		# when every producer gate passes (the backend's ONE gate verdict);
		# otherwise it carries the blocking reason ("bonded — asks no more",
		# "nothing to ask for", "relief running, N collections", "N turns
		# until it may ask"). Green means a petition really may come at the
		# turn's end; the countdown suffix rides only the green form, and
		# "now" is stated as what it is — at the turn's end.
		var standing = str(v.get("standing", ""))
		var may_petition = standing == "may petition"
		var standing_color = Utils.COLOR_SUCCESS if may_petition else COLOR_AMBER
		var standing_cell: String = "[color=#" + standing_color + "]" + standing + "[/color]"
		if may_petition and v.has("next_petition_in"):
			var next_in = int(v.get("next_petition_in", 0))
			if next_in <= 0:
				standing_cell += "  [color=#" + Utils.COLOR_INFO + "]· may petition at the turn's end[/color]"
			else:
				standing_cell += "  [color=#" + Utils.COLOR_INFO + "]· next petition in " + str(next_in) + " turn" + ("s" if next_in != 1 else "") + "[/color]"
		if not fold_standing:   # Session UI-4: folded, a blocked standing is a header tag
			facts.append([_fact_label("authority", "Standing: "), standing_cell])
	if v.has("bond") and not bond_led:
		var bond_text = _vassal_bond_text(v)
		if bond_text != "" and not fold_bond:   # Session UI-4: folded, "no bond yet" is a header tag
			facts.append([_fact_label("trust", "Bond: "), "[color=#" + Utils.COLOR_INFO + "]" + bond_text + "[/color]"])
	var remission_left = int(v.get("remission_left", 0))
	if remission_left > 0:
		facts.append([_fact_label("gold", "Tribute remitted: "), "[color=#" + Utils.COLOR_GOLD + "]" + str(remission_left) + " collection" + ("s" if remission_left != 1 else "") + "[/color]"])

	# ── Garrison lever (VP-D1) ──
	var capital = str(v.get("capital", ""))
	if v.get("garrison_present", false):
		facts.append([_fact_label("garrison", ""), "[color=#" + Utils.COLOR_SUCCESS + "]Garrisoned — our presence in " + capital + " steadies them (+" + str(int(v.get("garrison_bonus", 2))) + "/turn)[/color]"])
	elif capital != "":
		facts.append([_fact_label("garrison", ""), "[color=#" + Utils.COLOR_INFO + "]No garrison — a corps in " + capital + " would add a standing +2/turn[/color]"])

	# ── Standing subsidy (treaty gold_per_turn — a forecast term, so name it) ──
	var subsidy = int(v.get("subsidy_bonus", 0))
	if subsidy > 0:
		facts.append([_fact_label("income", ""), "[color=#" + Utils.COLOR_SUCCESS + "]Subsidized — treaty gold steadies them (+" + str(subsidy) + "/turn)[/color]"])

	# ── The laws that bind them (SR-5r RF-4b, T8 — the forecast's own term) ──
	for term in v.get("law_terms", []):
		if term is Array and term.size() >= 2:
			var law_name = str(term[0])
			if law_name != "":
				law_name = law_name.substr(0, 1).to_upper() + law_name.substr(1)
			facts.append([_fact_label("administration", ""), "[color=#" + Utils.COLOR_SUCCESS + "]" + law_name + " binds them (+" + str(int(term[1])) + "/turn)[/color]"])

	# ── Granted provinces (VS-3 provenance) ──
	var granted = v.get("granted_regions", [])
	if granted is Array and granted.size() > 0:
		var granted_strs = []
		for g in granted:
			granted_strs.append(str(g))
		facts.append([_fact_label("europe", ""), "[color=#" + Utils.COLOR_INFO + "]Ceded to them: " + ", ".join(PackedStringArray(granted_strs)) + "[/color]"])
	bbcode += _facts_table(facts)

	# ── Action chips (honest availability — the wizard's own gate rows) ──
	# Session UI-2: ONE row of chips on its own line, never inside a sentence;
	# each chip's terms a note under the row.
	var actions = v.get("actions", [])
	if actions is Array and actions.size() > 0:
		var chips: Array = []
		var notes := ""
		for a in actions:
			var parts: Array = _vassal_action_parts(a, v)
			if parts.is_empty():
				continue
			chips.append(parts[0])
			notes += parts[1]
		if not chips.is_empty():
			bbcode += "  " + "  ".join(PackedStringArray(chips)) + "\n" + notes
	elif actions_blocked:
		pass  # section-level notice already shown
	bbcode += Utils.CARD_CLOSE
	bbcode += "\n"
	return bbcode


# IQ-7: the bond line. The backend's `bond` is the lord–client relation plus
# the text its `relation // 20` term earns ("+2/turn — two petitions
# honoured"); read whichever shape the row carries (a dict with
# `relation`/`text`, a bare string, or the bare number beside
# `relation_modifier`) so the card never prints a raw Dictionary.
func _vassal_bond_text(v: Dictionary) -> String:
	var bond = v.get("bond", null)
	if bond is Dictionary:
		var text = str(bond.get("text", ""))
		var relation = bond.get("relation", null)
		if relation != null and text != "":
			return "relation " + str(int(relation)) + " · " + text
		if relation != null:
			return "relation " + str(int(relation))
		return text
	if bond is String:
		return str(bond)
	if bond is int or bond is float:
		var line = "relation " + str(int(bond))
		if v.has("relation_modifier"):
			var mod = int(v.get("relation_modifier", 0))
			line += " · " + ("+" if mod >= 0 else "") + str(mod) + "/turn"
		return line
	return ""


# Compact chip labels per action id. All NUMBERS in the terms come from the
# backend payload (dp_cost/gold_cost on the action row; grip-effective
# invest_gain/autonomy_up_gain/autonomy_down_loss on the vassal row) — the
# UI6-R2 review fix: the first cut hardcoded the loyalty gain the executor
# blunts to 40% in the VS-R spiral band. Shown = applied.
const _VASSAL_ACTION_LABELS = {
	"invest_vassal": "Invest",
	"increase_autonomy": "Loosen Rein",
	"decrease_autonomy": "Tighten Rein",
	"release_vassal": "Release",
	"grant_region_to_vassal": "Cede Province…",
}

func _vassal_action_parts(a: Dictionary, v: Dictionary) -> Array:
	"""Session UI-2: one action as [the chip, its note line]. A live action is a
	gilt chip with its terms noted under the row; a gated one is the dimmed chip
	with its reason said in its note. [] for an action the card does not know."""
	var action_id = str(a.get("action", ""))
	if not _VASSAL_ACTION_LABELS.has(action_id):
		return []
	var label = str(_VASSAL_ACTION_LABELS[action_id])
	var nation = str(v.get("name", ""))
	var dp_cost = int(a.get("dp_cost", 1))
	var gold_cost = int(a.get("gold_cost", 0))
	var cost_text = str(dp_cost) + " DP"
	if gold_cost > 0:
		cost_text = str(gold_cost) + "g · " + cost_text
	var blunted = bool(v.get("gains_blunted", false))
	var terms = ""
	match action_id:
		"invest_vassal":
			terms = "+" + str(int(v.get("invest_gain", 10))) + " loyalty — " + cost_text
		"increase_autonomy":
			# S14C-X10: the plan's own line (the ports named) when the payload carries it.
			var up_line = str(v.get("autonomy_up_line", ""))
			if up_line != "":
				terms = up_line + " — " + cost_text
			else:
				terms = "+" + str(int(v.get("autonomy_up_gain", 10))) + " loyalty, they keep more income — " + cost_text
		"decrease_autonomy":
			var down_line = str(v.get("autonomy_down_line", ""))
			if down_line != "":
				terms = down_line + " — " + cost_text
			else:
				terms = "−" + str(int(v.get("autonomy_down_loss", 15))) + " loyalty, they remit more — " + cost_text
			blunted = false  # a downgrade is NEVER softened (VS-R Q3)
		"release_vassal":
			terms = "free them honorably — " + cost_text
			blunted = false
		"grant_region_to_vassal":
			terms = "bind them with land — picker states each province's terms"
			blunted = false  # the land grant is never spiral-blunted
	if blunted:
		# The executor's own disclosure phrasing — chip copy and result
		# message can never disagree.
		terms += " (the Emperor's faltering grip blunts the gesture)"
	if a.get("available", false):
		var meta = ""
		if action_id == "grant_region_to_vassal":
			meta = "vassal_cede:" + nation
		else:
			meta = "vassal:" + action_id + ":" + nation
		var chip_bg = "233043"
		var chip_text = Utils.COLOR_GOLD
		if action_id == "release_vassal":
			chip_text = Utils.COLOR_ERROR_CHIP
		# Session UI-3 (November 12, 2026): Folded, the lever's line is the chip's
		# hover and its cost rides the chip's face; On the page the chip and the
		# line print as they did.
		if Utils.explanations_folded():
			var face: String = label
			if action_id != "grant_region_to_vassal":
				face += " · " + cost_text
			return [Utils.bb_button_chip(meta, face, chip_text, chip_bg, "", label + " — " + terms), ""]
		return [Utils.bb_button_chip(meta, label, chip_text, chip_bg),
			"    [color=#" + Utils.COLOR_INFO + "]" + label + " — " + terms + "[/color]\n"]
	# Session UI-5: the payload's display reason first, then its raw one — the
	# locked chip's hover (folded) and its stated line (On the page).
	# (GDScript's `or` answers a bool, never an operand: `str(x or y)` read
	# "true" on every locked chip — the final shoot's catch.)
	var reason := ""
	for reason_key in ["disabled_reason_display", "disabled_reason"]:
		var said = a.get(reason_key)
		if said is String and said != "":
			reason = said
			break
	var gated: String = label + " — unavailable"
	if reason != "":
		gated += ": " + reason
	if Utils.explanations_folded():
		# Folded, a locked chip is a lock and dim words; its hover says why
		# (UI-4's rule — the final reading read a visible caption per locked
		# chip as clutter: the Vassals card fell 8 -> 6).
		return [Utils.bb_chip_disabled(label, "", gated), ""]
	return [Utils.bb_chip_disabled(label), "    [color=#" + Utils.COLOR_INFO + "]" + gated + "[/color]\n"]


# =============================================================================
# TAB 7: CONGRESS (GE-3 — the Congress of Paris, ENDGAME_PLAN §2.4 / §4)
# =============================================================================
# ONE payload (`congress.build_congress_payload`): every figure and sentence
# here is the backend's. Null-safe on every key — a present-but-null value
# survives `.get(key, default)`, and bool(null) / int(null) / `for x in null`
# are Godot runtime errors (TUT-F1/F3's class).

const COLOR_SLATE = "8fa3b8"
# The stances the Imperial Peace counts as answered (`congress.SATISFIED`).
const CONGRESS_SATISFIED = ["RECOGNIZES", "SHUT OUT", "GONE"]


static func congress_stance_color(stance: String) -> String:
	"""RECOGNIZES green · REFUSES crimson · SUES amber · SHUT OUT slate ·
	GONE grey (the end screen's SIGNED reads as RECOGNIZES)."""
	match stance:
		"RECOGNIZES", "SIGNED":
			return Utils.COLOR_SUCCESS
		"REFUSES":
			return Utils.COLOR_ERROR
		"SUES":
			return COLOR_AMBER
		"SHUT OUT":
			return COLOR_SLATE
	return Utils.COLOR_INFO


static func congress_stance_tone(stance: String) -> String:
	"""Session UI-2: the stance badge's ground (the same reading as the ink)."""
	match stance:
		"RECOGNIZES", "SIGNED":
			return Utils.cv_hex("2f6b3a")
		"REFUSES":
			return Utils.cv_hex("8b2a2a")
		"SUES":
			return "8a6d2a"
		"SHUT OUT":
			return "3a4a6b"
	return Utils.COLOR_BADGE_QUIET


static func congress_severity_tint(severity: String) -> String:
	"""The clock line's tint — the backend decided the severity once
	(`congress.clock_severity`); the fall clock's tints, gold for the gate."""
	match severity:
		"critical":
			return Utils.COLOR_ERROR
		"warning":
			return Utils.COLOR_BATTLE
		"paused":
			return Utils.COLOR_INFO
	return Utils.COLOR_GOLD


func _cstr(d: Dictionary, key: String) -> String:
	var v = d.get(key, "")
	if v == null:
		return ""
	return str(v)


func _cint(d: Dictionary, key: String, fallback: int = 0) -> int:
	var v = d.get(key, fallback)
	if v is int or v is float:
		return int(v)
	return fallback


func _ctrue(v) -> bool:
	return v is bool and v


func _bb_safe(text: String) -> String:
	# A sentence from the world must not open a bbcode tag.
	return text.replace("[", "[lb]")


func _render_congress():
	var c = cached_data.get("congress", null)
	var bbcode := ""
	if not (c is Dictionary) or c.is_empty() or not _ctrue(c.get("armed", false)):
		bbcode += "[color=#" + Utils.COLOR_HEADER + "]═══ THE CONGRESS OF PARIS ═══[/color]\n"
		bbcode += "[color=#" + Utils.COLOR_INFO + "]There is no Congress of Paris in this campaign — the rules of the ending are not authored here.[/color]\n"
		content_area.text = Utils.dress_heads(bbcode)
		return
	var needed := _cint(c, "titled_needed")
	var turns := _cint(c, "turns")
	# R159: the screen names the mechanic it shows — in the payload's numbers.
	# Session UI-3 (November 12, 2026): that lead-in stands behind an ⓘ at the
	# heading (id dl.congress.lead); On the page it prints as it did.
	var congress_lead: String = "Europe must RECOGNIZE the new order. With " + str(needed)
	congress_lead += " titled provinces the Emperor may summon the great powers to Paris; each answers at every end turn, with its reason and its price, and the Congress sits "
	congress_lead += Utils.plural(turns, "turn") + ". If on the last day every court recognizes, is shut out or is gone, and the hold never broke, the Imperial Peace is proclaimed."
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]═══ THE CONGRESS OF PARIS ═══[/color]" + Utils.lead_mark(congress_lead, "dl.congress.lead") + "\n"
	bbcode += Utils.bb_lead("[color=#" + Utils.COLOR_INFO + "]" + congress_lead + "[/color]\n", "dl.congress.lead") + "\n"
	var line := _cstr(c, "state_line")
	if line != "":
		bbcode += "[color=#" + congress_severity_tint(_cstr(c, "severity")) + "][b]" + _bb_safe(line) + "[/b][/color]\n\n"
	var phase := _cstr(c, "phase")
	if phase == "sitting":
		bbcode += _congress_sitting_block(c)
	elif phase == "concluded":
		bbcode += "[color=#" + Utils.COLOR_GOLD + "]The Imperial Peace is signed — the powers of Europe recognize the order of the Empire.[/color]\n\n"
	else:
		bbcode += _congress_gate_block(c)
	bbcode += _congress_table_block(c)
	content_area.text = Utils.dress_heads(bbcode)


func _congress_gate_block(c: Dictionary) -> String:
	var out := "[color=#" + Utils.COLOR_HEADER + "]THE SUMMONS[/color]\n"
	var terms = c.get("gate_terms", [])
	if terms is Array:
		for t in terms:
			if not (t is Dictionary):
				continue
			var met := _ctrue(t.get("met", false))
			var mark: String = "✓" if met else "•"
			var col: String = Utils.COLOR_SUCCESS if met else Utils.COLOR_INFO
			out += "  [color=#" + col + "]" + mark + " " + _bb_safe(_cstr(t, "text")) + "[/color]\n"
	var cost := _cstr(c, "cost_text")
	if cost != "":
		out += "  [color=#" + Utils.COLOR_INFO + "]Cost: " + cost + " — once summoned, it cannot be recalled.[/color]\n"
	if _ctrue(c.get("available", false)):
		# PC-X51: the Cabinet's row is the road — never a typed line
		out += "  [color=#" + Utils.COLOR_SUCCESS + "]The powers may be summoned — the Cabinet (F1), 'The Congress of Paris'.[/color]\n"
	else:
		var why := _cstr(c, "unavailable_reason")
		if why != "":
			out += "  [color=#" + Utils.COLOR_INFO + "]Not yet: " + _bb_safe(why) + "[/color]\n"
	var held = c.get("held_unsettled", [])
	var roads = c.get("held_roads", [])
	if roads is Array and roads.size() > 0:
		# SR-1c: the road each held province has to title (the backend's
		# `game_end.title_roads` — the same record the count reads).
		out += "  [color=#" + Utils.COLOR_INFO + "]Held but not yet titled (" + str(roads.size()) + ") — the road to each:[/color]\n"
		var shown_roads := 0
		for r in roads:
			if shown_roads >= 8:
				break
			if not (r is Dictionary):
				continue
			out += "    [color=#" + Utils.COLOR_INFO + "]• " + _bb_safe(_cstr(r, "text")) + "[/color]\n"
			shown_roads += 1
		if roads.size() > shown_roads:
			out += "    [color=#" + Utils.COLOR_INFO + "]… and " + str(roads.size() - shown_roads) + " more.[/color]\n"
	elif held is Array and held.size() > 0:
		var names: Array = []
		for h in held:
			if names.size() >= 8:
				break
			names.append(str(h))
		var shown := ", ".join(PackedStringArray(names))
		if held.size() > names.size():
			shown += " and " + str(held.size() - names.size()) + " more"
		out += "  [color=#" + Utils.COLOR_INFO + "]Held but not yet titled (" + str(held.size()) + "): " + _bb_safe(shown) + " — a conquest counts once a treaty cedes it or it is held in quiet possession.[/color]\n"
	if _cstr(c, "phase") == "cooldown":
		var reason := _cstr(c, "dissolve_reason")
		if reason != "":
			out += "  [color=#" + COLOR_AMBER + "]The last Congress dissolved — " + _bb_safe(reason) + ".[/color]\n"
		var refusers = c.get("refusers", [])
		if refusers is Array and refusers.size() > 0:
			var shown_r: Array = []
			for r in refusers:
				shown_r.append(Utils.display_nation_name(str(r)))
			out += "  [color=#" + Utils.COLOR_INFO + "]The courts that would not sign: " + ", ".join(PackedStringArray(shown_r)) + ".[/color]\n"
	return out + "\n"


func _congress_sitting_block(c: Dictionary) -> String:
	var day := _cint(c, "day")
	var turns := _cint(c, "turns")
	var ends := _cint(c, "ends_turn")
	var out := "[color=#" + Utils.COLOR_HEADER + "]THE SITTING[/color]\n"
	if day >= 1:
		out += "  Turn " + str(day) + " of " + str(turns) + " — the Congress resolves at the end of turn " + str(ends) + ".\n"
	else:
		out += "  The powers gather — the sitting opens at this end turn and resolves at the end of turn " + str(ends) + ".\n"
	out += congress_strip_table(c.get("strip", []), turns, day) + "\n"
	out += "[color=#" + Utils.COLOR_HEADER + "]THE HOLD[/color] [color=#" + Utils.COLOR_INFO + "]— every condition, at every end turn; one broken, and the Congress dissolves[/color]\n"
	var hold = c.get("hold", [])
	if hold is Array:
		for h in hold:
			if not (h is Dictionary):
				continue
			var met := _ctrue(h.get("met", false))
			var mark: String = "✓" if met else "✗"
			var col: String = Utils.COLOR_SUCCESS if met else Utils.COLOR_ERROR
			out += "  [color=#" + col + "]" + mark + " " + _bb_safe(_cstr(h, "text")) + "[/color]\n"
	return out + "\n"


static func congress_strip_table(strip, turns: int, today: int) -> String:
	"""The sitting as a strip — one cell per day: whether the hold stood at
	that end turn and how many courts had answered (recognizes / shut out /
	gone), read off the backend's per-turn record. A day not yet reached is
	a dot; today's number is gilded and its answer is still to come (…)."""
	if turns <= 0:
		return ""
	var by_day := {}
	if strip is Array:
		for row in strip:
			if row is Dictionary and (row.get("day") is int or row.get("day") is float):
				by_day[int(row.get("day"))] = row
	var out := "[table=" + str(turns + 1) + "]"
	out += "[cell][color=#" + Utils.COLOR_INFO + "]Day  [/color][/cell]"
	for d in range(1, turns + 1):
		var day_col: String = Utils.COLOR_GOLD if d == today else Utils.COLOR_INFO
		out += "[cell][color=#" + day_col + "] " + str(d) + " [/color][/cell]"
	out += "[cell][color=#" + Utils.COLOR_INFO + "]Hold  [/color][/cell]"
	for d in range(1, turns + 1):
		var row = by_day.get(d, null)
		if row is Dictionary:
			var held: bool = row.get("held") is bool and row.get("held")
			out += "[cell][color=#" + (Utils.COLOR_SUCCESS if held else Utils.COLOR_ERROR) + "] " + ("✓" if held else "✗") + " [/color][/cell]"
		elif d == today:
			# Today's answer is taken at this end turn (its day number is
			# gilded in the row above).
			out += "[cell][color=#" + Utils.COLOR_GOLD + "] … [/color][/cell]"
		else:
			out += "[cell][color=#" + Utils.COLOR_INFO + "] · [/color][/cell]"
	out += "[cell][color=#" + Utils.COLOR_INFO + "]Signed  [/color][/cell]"
	for d in range(1, turns + 1):
		var row2 = by_day.get(d, null)
		var stances = row2.get("stances", {}) if row2 is Dictionary else null
		if stances is Dictionary and not stances.is_empty():
			var answered := 0
			for court in stances:
				if str(stances[court]) in CONGRESS_SATISFIED:
					answered += 1
			out += "[cell][color=#" + Utils.COLOR_INFO + "] " + str(answered) + "/" + str(stances.size()) + " [/color][/cell]"
		else:
			out += "[cell] [/cell]"
	return out + "[/table]\n"


func _congress_table_block(c: Dictionary) -> String:
	var courts = c.get("courts", [])
	if not (courts is Array) or courts.is_empty():
		return ""
	var sitting := _cstr(c, "phase") == "sitting"
	var out := "[color=#" + Utils.COLOR_HEADER + "]THE TABLE[/color] [color=#" + Utils.COLOR_INFO + "]— "
	if sitting:
		out += "every great power answers again at every end turn"
	else:
		out += "how each great power would answer today"
	out += "[/color]\n"
	for ct in courts:
		if ct is Dictionary:
			out += _format_congress_court(ct, sitting)
	return out


func _format_congress_court(ct: Dictionary, sitting: bool) -> String:
	var nation := _cstr(ct, "nation")
	var display := _cstr(ct, "display")
	if display == "":
		display = Utils.display_nation_name(nation)
	var seat := _cstr(ct, "seat")
	var stance := _cstr(ct, "stance")
	# Session UI-2 (November 11, 2026): a court a card — its arms, its name in
	# the title face, its stance a badge; the reckoning and the price a table.
	var out := Utils.card_open(congress_stance_color(stance)) + "  " + Utils.bb_flag(nation, 18) + " "
	out += Utils.HEAD_OPEN + display + Utils.HEAD_CLOSE
	if seat != "" and seat != display:
		out += "  [color=#" + Utils.COLOR_INFO + "](" + seat + ")[/color]"
	out += "   " + Utils.bb_badge(stance, congress_stance_tone(stance)) + "\n"
	var reason := _cstr(ct, "reason")
	if reason != "":
		out += "    [color=#" + Utils.COLOR_INFO + "]" + _bb_safe(reason) + "[/color]\n"
	var court_facts: Array = []
	var score = ct.get("score", null)
	if (score is int or score is float) and _cstr(ct, "by") == "formula":
		court_facts.append([_fact_label("intel", "Its reckoning: "), "[color=#" + Utils.COLOR_INFO + "]" + str(int(score)) + " — it signs at " + str(_cint(ct, "threshold")) + "[/color]"])
	var price := _cstr(ct, "price")
	if price != "":
		court_facts.append([_fact_label("gold", "Price: "), "[color=#" + Utils.COLOR_INFO + "]" + _bb_safe(price) + "[/color]"])
	out += _facts_table(court_facts)
	# The War of the Congress: the backend sends `war_in` ONLY when the join
	# would really fire (`congress.march_blocker` empty), else the blocker —
	# a court in a truce, an ally, or no coalition to join is never promised
	# a declaration that cannot come (GE-3 review).
	if ct.get("war_in") is int or ct.get("war_in") is float:
		var war_in := _cint(ct, "war_in")
		var refusing := _cint(ct, "refusing_turns")
		var threat := "    [color=#" + Utils.COLOR_ERROR + "]Refusing " + Utils.plural(refusing, "turn") + " — "
		if war_in > 1:
			threat += "it takes up arms against us in " + Utils.plural(war_in, "turn") + " unless it signs."
		else:
			threat += "it takes up arms against us at this end turn unless it signs."
		out += threat + "[/color]\n"
	elif _cstr(ct, "march_blocker") != "":
		out += "    [color=#" + Utils.COLOR_INFO + "]Refusing " + Utils.plural(_cint(ct, "refusing_turns"), "turn") + " — it will not march: " + _bb_safe(_cstr(ct, "march_blocker")) + ".[/color]\n"
	# The price's levers that are typed orders — the backend names the command
	# (`levers[].command`). Gold is laid at the table only while it sits.
	# DDB-10 (S13b): a lever the Cabinet owns names its control ("F1 →
	# Prussia → Buy Off Their Design"), never a typed line the door refuses.
	var controls: Array = []
	var levers = ct.get("levers", [])
	if levers is Array:
		for lv in levers:
			if not (lv is Dictionary):
				continue
			# PC-X51: each lever names its Cabinet control (the sweetener's
			# only while the Congress sits); the typed line is never shown
			if _cstr(lv, "key") == "sweetener" and not sitting:
				continue
			var control := _cstr(lv, "control")
			if control != "":
				controls.append(_bb_safe(control))
	if not controls.is_empty():
		out += "    [color=#" + Utils.COLOR_INFO + "]In the Cabinet: " + "; ".join(PackedStringArray(controls)) + ".[/color]\n"
	if stance != "GONE" and nation != "":
		var where: String = seat if seat != "" else display
		out += "    " + Utils.bb_button_chip("congress_court:" + nation, "Open the Cabinet at " + where + " →", Utils.COLOR_GOLD, "233043") + "\n"
	return out + Utils.CARD_CLOSE + "\n"


# =============================================================================
# CRITICAL PULSE (flashing red for CRITICAL threat tier)
# =============================================================================

func _start_critical_pulse():
	if not _critical_pulsing:
		_critical_pulsing = true
		_pulse_state = false
		_critical_pulse_timer.start()


func _stop_critical_pulse():
	if _critical_pulsing:
		_critical_pulsing = false
		_critical_pulse_timer.stop()
		# TH1: Reset modulate to white
		content_area.modulate = Color(1.0, 1.0, 1.0, 1.0)


func _on_critical_pulse():
	# TH1: Toggle between white and slight red tint
	_pulse_state = not _pulse_state
	if _pulse_state:
		content_area.modulate = Color(1.0, 0.85, 0.85, 1.0)
	else:
		content_area.modulate = Color(1.0, 1.0, 1.0, 1.0)


# =============================================================================
# HELPERS
# =============================================================================

func _on_overlay_input(event):
	"""Click on dark overlay to close."""
	if event is InputEventMouseButton and event.pressed:
		close_view()


func _rerender_keeping_scroll() -> void:
	"""Session UI-3: re-render the open tab from the cached ledger (never a
	re-fetch) and put the reader's scroll back."""
	if cached_data.is_empty():
		return
	var at: int = scroll_container.scroll_vertical
	_render_current_tab()
	Utils.restore_scroll(scroll_container, at)


func _on_content_meta_clicked(meta):
	var meta_key = str(meta)
	# Session UI-3 (November 12, 2026): an ⓘ / "▸ more" opens its words in place,
	# the reader's scroll kept.
	if Utils.is_note_meta(meta):
		Utils.toggle_note(meta)
		_rerender_keeping_scroll()
		return
	if meta_key.begins_with("peace_ratification:"):
		var expanded = bool(_expanded_peace_ratifications.get(meta_key, false))
		_expanded_peace_ratifications[meta_key] = not expanded
		if current_tab == 1:
			_render_treaties()
	elif meta_key.begins_with("settlement:"):
		# F2: toggle the inline Terms/Allies/Warnings/Acceptance expansion.
		var s_expanded = bool(_expanded_settlements.get(meta_key, false))
		_expanded_settlements[meta_key] = not s_expanded
		if current_tab == 1:
			_render_treaties()
	elif meta_key.begins_with("congress_court:"):
		# GE-3: a court's card opens the Cabinet at that court — the wizard
		# states each instrument's terms (buy off its design, an alliance, a
		# peace); this tab itself sends nothing.
		var court = meta_key.substr("congress_court:".length())
		if court != "":
			open_diplomacy_for.emit(court)
	elif meta_key.begins_with("vassal_cede:"):
		# UI-6: [Cede Province…] — the wizard owns the province picker.
		var cede_nation = meta_key.substr("vassal_cede:".length())
		if cede_nation != "":
			open_diplomacy_for.emit(cede_nation)
	elif meta_key.begins_with("vassal:"):
		# UI-6: an action chip — build the same typed command the wizard sends.
		var parts = meta_key.split(":")
		if parts.size() == 3:
			var command = _vassal_chip_command(str(parts[1]), str(parts[2]))
			if command != "":
				# S12 part 2 (R6): the chip answers in place (the terminal's
				# echo lies under this screen) when main.gd took the order.
				Utils.order_taken = false
				vassal_command.emit(command)
				if Utils.order_taken:
					Utils.mark_chip_sent(content_area, meta_key)
	elif meta_key == "talleyrand_assess":
		# UI-6: the W6-9 counsel verb from the Talleyrand tab.
		assess_requested.emit()


func _vassal_chip_command(action_id: String, nation: String) -> String:
	"""Typed-command echoes — byte-identical to diplomacy_wizard._build_command
	for the same actions, so chips and wizard cannot drift apart."""
	match action_id:
		"invest_vassal":
			return "invest in " + nation
		"increase_autonomy":
			return "increase autonomy " + nation
		"decrease_autonomy":
			return "decrease autonomy " + nation
		"release_vassal":
			return "release " + nation
	return ""


func _format_settlement_sections(sections) -> String:
	"""Render the sectioned settlement review payload inline.

	`sections` is the `review_sections` dict from `recent_settlement_summaries`
	produced by `build_settlement_review_from_event()`. Empty sections are
	skipped silently. Output is indented two spaces deeper than the row
	header so the expansion reads as a child block.
	"""
	if not sections is Dictionary or sections.is_empty():
		return ""
	var bbcode := ""
	var section_dict = sections.get("sections", {})
	if not section_dict is Dictionary:
		return ""

	# Terms section
	var terms = section_dict.get("terms", {})
	if terms is Dictionary:
		var term_rows = terms.get("rows", [])
		var term_overflow = int(terms.get("overflow_count", 0))
		if term_rows is Array and term_rows.size() > 0:
			bbcode += "    [color=#" + Utils.COLOR_HEADER + "]Terms:[/color]\n"
			for term in term_rows:
				if not term is Dictionary:
					continue
				var ttype = str(term.get("display_label", term.get("type_display", term.get("type", "?"))))
				var t_from = Utils.display_nation_name(str(term.get("from", "")))
				var t_to = Utils.display_nation_name(str(term.get("to", "")))
				var arrow = ""
				if t_from != "" or t_to != "":
					arrow = " " + t_from + "→" + t_to
				bbcode += "      • " + ttype + arrow + "\n"
			if term_overflow > 0:
				bbcode += "      [color=#" + Utils.COLOR_INFO + "]+" + str(term_overflow) + " more terms[/color]\n"

	# Allies section
	var allies = section_dict.get("allies", {})
	if allies is Dictionary:
		var ally_rows = allies.get("rows", [])
		var ally_overflow = int(allies.get("overflow_count", 0))
		if ally_rows is Array and ally_rows.size() > 0:
			bbcode += "    [color=#" + Utils.COLOR_HEADER + "]Allies:[/color]\n"
			for ally in ally_rows:
				if not ally is Dictionary:
					continue
				var nation = Utils.display_nation_name(str(ally.get("nation", "?")))
				var standing = str(ally.get("standing_display", ally.get("standing", "consult")))
				var marker = ""
				if bool(ally.get("is_beneficiary", false)):
					marker = " (rewarded)"
				if bool(ally.get("is_leader", false)):
					marker = " (leader)" + marker
				bbcode += "      • " + nation + " — " + standing + marker + "\n"
			if ally_overflow > 0:
				bbcode += "      [color=#" + Utils.COLOR_INFO + "]+" + str(ally_overflow) + " more participants — View all participants[/color]\n"

	# Warnings section
	var warnings = section_dict.get("warnings", {})
	if warnings is Dictionary:
		var inline_warns = warnings.get("inline", [])
		var overflow_warns = warnings.get("overflow", [])
		if inline_warns is Array and inline_warns.size() > 0:
			bbcode += "    [color=#" + Utils.COLOR_HEADER + "]Warnings:[/color]\n"
			for w in inline_warns:
				if not w is Dictionary:
					continue
				var sev = str(w.get("severity", "WARNING"))
				var code = str(w.get("code_display", w.get("code", "?")))
				var detail = str(w.get("detail", ""))
				var warn_color = Utils.COLOR_INFO
				if sev == "HARD_STOP":
					warn_color = Utils.cv_hex(COLOR_RED)
				bbcode += "      [color=#" + warn_color + "]• [" + sev.replace("_", " ") + "] " + code
				if detail != "":
					bbcode += " — " + detail
				bbcode += "[/color]\n"
			if overflow_warns is Array and overflow_warns.size() > 0:
				bbcode += "      [color=#" + Utils.COLOR_INFO + "]+" + str(overflow_warns.size()) + " more — View all concerns[/color]\n"

	# Acceptance section (often empty for archived events).
	var acceptance = section_dict.get("acceptance", {})
	if acceptance is Dictionary and not acceptance.is_empty():
		var total = int(acceptance.get("total", 0))
		var band = str(acceptance.get("band_display", "Review"))
		bbcode += "    [color=#" + Utils.COLOR_HEADER + "]Acceptance:[/color] "
		bbcode += str(total) + " (" + band + ")\n"
		var top = acceptance.get("top_components", [])
		if top is Array and top.size() > 0:
			for c in top:
				if not c is Dictionary:
					continue
				var component_label = str(c.get("component_display", c.get("name", "?")))
				var value_label = str(c.get("value_display", str(c.get("value", 0))))
				bbcode += "      • " + component_label + ": " + value_label + "\n"

	return bbcode


func _humanize_label(value: String) -> String:
	var label = value.replace("_", " ").strip_edges()
	if label == "":
		return value
	return label.capitalize()
