extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Strategic Ledger Screen (Session B)
# =============================================================================
# 8-section sub-tabbed screen. CanvasLayer 50.
# Tabs: FORCES, TERRITORIES, ECONOMY, INTELLIGENCE, MANPOWER, ORDERS,
# ADMIRALTY (NV-12 "The Clear Deck" — the naval block was buried at the
# bottom of ECONOMY; it is a first-class book now), LAWS (SR-5r RF-4a —
# the laws of state, REFORMS_SPEC §8a).
# Number keys 1-8 switch sub-tabs (guarded by visible check, and a digit
# belongs to whoever has the caret).
# =============================================================================

signal closed
# NV-6: an Admiralty chip — the same typed-command pipeline every other
# chip surface uses (main.gd owns the send + the in-place refresh). RF-4a:
# THE LAWS' Enact / Restore / Repeal chips ride the same road — it is the
# ledger's one chip pipeline, whatever the book.
signal naval_command(command: String)
# CC-X15 (CC-5's sweep): the ORDERS book's Cancel — main.gd sends it down the
# one cancel road the map's arrow card uses (the wire guard, the end-turn
# latch retired, the map and the actions count following the reply), then
# re-reads this book.
signal cancel_order_requested(marshal_name: String)

# NV-6: the Admiralty chip pill, matching the region panel's `_CHIP_BG`.
const _NAVAL_CHIP_BG = "233043"

# UI References — paths match scene tree
@onready var background_overlay = $BackgroundOverlay
@onready var close_button = $PanelContainer/VBoxContainer/HeaderRow/CloseButton
@onready var scroll_container = $PanelContainer/VBoxContainer/ScrollContainer
@onready var content_area = $PanelContainer/VBoxContainer/ScrollContainer/ContentArea
@onready var forces_tab = $PanelContainer/VBoxContainer/SubTabRow/ForcesTab
@onready var territories_tab = $PanelContainer/VBoxContainer/SubTabRow/TerritoriesTab
@onready var economy_tab = $PanelContainer/VBoxContainer/SubTabRow/EconomyTab
@onready var intel_tab = $PanelContainer/VBoxContainer/SubTabRow/IntelTab
@onready var manpower_tab = $PanelContainer/VBoxContainer/SubTabRow/ManpowerTab
@onready var orders_tab = $PanelContainer/VBoxContainer/SubTabRow/OrdersTab
@onready var admiralty_tab = $PanelContainer/VBoxContainer/SubTabRow/AdmiraltyTab
@onready var laws_tab = $PanelContainer/VBoxContainer/SubTabRow/LawsTab

# State
var current_tab: int = 0  # 0=forces, 1=territories, 2=economy, 3=intel, 4=manpower, 5=orders, 6=admiralty, 7=laws
# SF7-X24: Alt+1..8 turn the books while the command line holds the caret.
const ALT_TURNS_THE_BOOKS := true
var cached_data: Dictionary = {}
var tab_buttons: Array = []

# Active tab style
var _active_tab_style: StyleBoxFlat = null
var _normal_tab_style: StyleBoxFlat = null

# Session UI-4 (November 12, 2026): the Economy tables' column weights (line | gold | note).
const ECON_COLS := [3, 2, 7]


func _ready():
	# UXR3-F3: the reading scroll comes to rest on whole lines.
	Utils.keep_whole_lines(content_area)
	close_button.pressed.connect(close_view)
	Utils.apply_icon_only_button(close_button, Utils.ICON_PHOSPHOR + "x.svg")
	background_overlay.gui_input.connect(_on_overlay_input)
	# UXR-2: clamped AND gripped — the player's size is remembered.
	ResizeGrip.attach_centered($PanelContainer, "ledger")

	tab_buttons = [forces_tab, territories_tab, economy_tab, intel_tab, manpower_tab, orders_tab, admiralty_tab, laws_tab]
	for i in range(tab_buttons.size()):
		tab_buttons[i].pressed.connect(_on_tab_pressed.bind(i))

	# Wire meta_clicked for cancel buttons in Orders tab
	content_area.meta_clicked.connect(_on_meta_clicked)
	Utils.on_explanations_changed(_rerender_in_place)

	# NV-P1 (routed at the NV-V visual pass, pre-existing): the ledger
	# ignored the mouse wheel. The RichTextLabel defaults to
	# MOUSE_FILTER_STOP, so it consumed the wheel event before its own
	# ScrollContainer parent ever saw it — and THE ADMIRALTY block sits at
	# the bottom of a long ECONOMY list, which is where it started to bite.
	# PASS still delivers _gui_input (so meta_clicked and every chip on
	# this screen keep working) and then lets the parent scroll.
	content_area.mouse_filter = Control.MOUSE_FILTER_PASS

	# Session UI (November 11, 2026): the ONE tab strip (`Utils.tab_styles`) —
	# a closed book is its words, the open book stands on a gilt underline.
	# The margins are this strip's own (6 / 3), so no tab moves.
	var strip := Utils.tab_styles(6.0, 3.0)
	_active_tab_style = strip["active"]
	_normal_tab_style = strip["normal"]
	for tab in tab_buttons:
		Utils.dress_tab(tab, strip)

	# Session UI: every corps, province, arm and court a card (the marks are
	# in the builders; `scripts/card_underlay.gd` paints them).
	Utils.card_page(content_area)

	hide()


func _input(event):
	"""Handle number keys 1-8 for sub-tab switching. Only when visible."""
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
	# SF7-X24 (Score Finish Step 7, the frames, Oct 4 2026): the command line
	# holds the caret after nearly every action, so the advertised "Keys
	# 1–8" typed digits into it instead (measured in the Mode C session).
	# Alt+digit is the focus-safe form — PC15-18's idiom for the screen keys —
	# and a bare digit still belongs to whoever has the caret.
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
			KEY_8:
				_switch_tab(7)
			_:
				switched = false
		if switched:
			get_viewport().set_input_as_handled()


var _api_client_ref = null

func open(api_client):
	"""Fetch ledger from backend and display it."""
	_api_client_ref = api_client
	content_area.text = "[color=#" + Utils.COLOR_INFO + "]Loading ledger...[/color]"
	current_tab = 0
	AudioManager.play("panel_open")
	show()
	# Session UI-3 (November 12, 2026): the books take the room (0.62 x 0.85).
	Utils.set_reading_share($PanelContainer, Utils.BOOK_SHARE, Utils.BOOK_MAX)
	Utils.clamp_centered_panel($PanelContainer)
	_update_tab_highlights()
	api_client.get_ledger(_on_ledger_received)


func open_to_tab(api_client, tab_index: int):
	"""NUI: open straight to one book (THE ADMIRALTY = 6). `open` resets the
	tab to Forces and fetches; the fetch renders whatever `current_tab` says
	when it lands, so the tab is set right after the reset."""
	open(api_client)
	current_tab = clampi(tab_index, 0, tab_buttons.size() - 1)
	_update_tab_highlights()


func _first_open_bbcode(data, screen: String) -> String:
	"""S14d: a book's `first_open` {screen, line} as one INFO line, then the
	acknowledgement through the api_client (the ledger holds its own ref)."""
	if not (data is Dictionary):
		return ""
	var fo = data.get("first_open")
	if not (fo is Dictionary) or str(fo.get("screen", "")) != screen:
		return ""
	var line := str(fo.get("line", ""))
	if line == "":
		return ""
	if _api_client_ref != null and _api_client_ref.has_method("note_first_open"):
		_api_client_ref.note_first_open(screen)
	return "[color=#" + Utils.COLOR_INFO + "]" + line.replace("[", "[lb]") + "[/color]\n"


func close_view():
	"""Hide the overlay and emit closed signal."""
	if visible:
		AudioManager.play("panel_close")
	hide()
	cached_data = {}
	closed.emit()


func _on_ledger_received(response):
	"""Cache data and render current tab."""
	if not visible:
		return

	if not response.get("success", false):
		content_area.text = "[color=#" + Utils.COLOR_ERROR + "]Failed to load ledger.[/color]"
		return

	cached_data = response.get("ledger", {})
	if cached_data.is_empty():
		content_area.text = "[color=#" + Utils.COLOR_INFO + "]No ledger data available.[/color]"
		return

	_render_current_tab()


func _on_tab_pressed(tab_index: int):
	_switch_tab(tab_index)


func _switch_tab(tab_index: int):
	if tab_index == current_tab:
		return
	AudioManager.play("page_turn")
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


func _dated_line() -> String:
	# HC-0: the ledger's dateline under each book's header — "" (no line)
	# on worlds without a calendar anchor, so legacy renders unchanged.
	var cal = str(cached_data.get("calendar_label", ""))
	if cal == "":
		return ""
	return "[color=#" + Utils.COLOR_INFO + "]" + cal + "[/color]\n"


func _collapse_note_line() -> String:
	# IQ-2 (Sept 14, 2026): a France reduced to one province — then none —
	# opened this ledger on "No territories controlled." and a muster that
	# read as ordinary. The backend's `collapse_note` states the collapse
	# (sent only while it holds; absent = the pre-IQ-2 ledger exactly).
	var note = cached_data.get("collapse_note", "")
	if not (note is String) or note == "":
		return ""
	return "[color=#" + Utils.COLOR_ERROR + "]" + note + "[/color]\n\n"


func _fall_clock_lines() -> String:
	# GE-2 (ENDGAME_PLAN §4, the clock line): one line per held arm of the
	# Fall, the backend's own `clock_line` (`fall.clock_line`, the ONE source
	# the war room and the end-turn banner print too) — "THE EAGLE IN CHAINS
	# — 3 of 10 · the regency falls at the end of turn 21 (7 turns remain)".
	# A paused clock says the clock stands still and names NO date; the
	# `severity` the backend decided picks the tint. Absent = no arm holds
	# (or the lever is down) and the tab is the pre-GE-2 tab exactly.
	var clock = cached_data.get("fall_clock", null)
	if not (clock is Dictionary):
		return ""
	var arms = clock.get("arms", [])
	if not (arms is Array) or arms.is_empty():
		return ""
	var bbcode := ""
	for arm in arms:
		if not (arm is Dictionary):
			continue
		var line := str(arm.get("clock_line", ""))
		if line == "":
			continue
		var severity := str(arm.get("severity", "warning"))
		var tint := Utils.COLOR_BATTLE
		if severity == "critical":
			tint = Utils.COLOR_ERROR
		elif severity == "paused":
			tint = Utils.COLOR_INFO
		bbcode += "[color=#" + tint + "]" + line + "[/color]\n"
	if bbcode != "":
		bbcode += "\n"
	return bbcode


func _congress_clock_line() -> String:
	# GE-3 (ENDGAME_PLAN §4, the clock line): the Congress of Paris — the
	# gate before a summons ("THE CONGRESS OF PARIS — 43 of 50 titled …"),
	# the sitting's turn and table while it sits, the cooldown after a
	# dissolution. The backend's ONE line (`congress.state_line` — the same
	# words the war room and the end-turn banner print); its `severity` picks
	# the tint. Absent on a world whose ending is not authored, and after the
	# Imperial Peace: the tab is the pre-GE-3 tab exactly.
	var clock = cached_data.get("congress_clock", null)
	if not (clock is Dictionary):
		return ""
	var line = clock.get("line", "")
	if not (line is String) or line == "":
		return ""
	var severity = clock.get("severity", "gate")
	var tint := Utils.COLOR_GOLD
	if severity is String:
		if severity == "critical":
			tint = Utils.COLOR_ERROR
		elif severity == "warning":
			tint = Utils.COLOR_BATTLE
		elif severity == "paused":
			tint = Utils.COLOR_INFO
	var out: String = "[color=#" + tint + "]" + str(line) + "[/color]\n"
	# SR-1c: at the gate, each held province's road to title under the
	# clock (the backend's `held_roads`; at most four here — the Diplomatic
	# Ledger's CONGRESS tab lists them all).
	var roads = clock.get("held_roads", [])
	if roads is Array and roads.size() > 0:
		var shown := 0
		for r in roads:
			if shown >= 4:
				break
			if not (r is Dictionary):
				continue
			out += "[color=#" + Utils.COLOR_INFO + "]  • " + str(r.get("text", "")) + "[/color]\n"
			shown += 1
		if roads.size() > shown:
			# S14G-X77: the book's key form - a bare letter TYPES into the command line.
			out += "[color=#" + Utils.COLOR_INFO + "]  … and " + str(roads.size() - shown) + " more on the Diplomatic Ledger's CONGRESS tab (press D, then 7; Alt+D, then Alt+7 while you type).[/color]\n"
	return out + "\n"


func _render_current_tab():
	if cached_data.is_empty():
		return
	_set_strip()
	match current_tab:
		0:
			_render_forces()
		1:
			_render_territories()
		2:
			_render_economy()
		3:
			_render_intel()
		4:
			_render_manpower()
		5:
			_render_orders()
		6:
			_render_admiralty_tab()
		7:
			_render_laws_tab()


# =============================================================================
# TAB RENDERERS
# =============================================================================

func _render_forces():
	var forces = cached_data.get("forces", [])
	var bbcode = ""
	# Session UI-3 (November 12, 2026): each book's lead-in stands behind an ⓘ
	# at its heading (Explanations: Folded); On the page = the old line.
	var lead_line := "The muster of your corps — strength, morale, and each marshal's temper. Keys 1–8 turn the ledger's books (Alt+1–8 while you type); Esc closes it (Alt+T while you type)."
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]═══ FORCES ═══[/color]" + Utils.lead_mark(lead_line, "sl.forces.lead") + "\n"
	bbcode += _dated_line()
	# R159 (POSITION 7): each core screen names the mechanic it displays.
	bbcode += Utils.bb_lead("[color=#" + Utils.COLOR_INFO + "]The muster of your corps — strength, morale, and each marshal's temper. Keys 1–8 turn the ledger's books (Alt+1–8 while you type); Esc closes it (Alt+T while you type).[/color]\n\n", "sl.forces.lead")
	bbcode += _collapse_note_line()
	# UXR3-41: Talleyrand's mission leads the muster when one runs (the
	# Cabinet's full block); an idle Cabinet says so in one line.
	var forces_cabinet = cached_data.get("cabinet")
	if forces_cabinet is Dictionary and forces_cabinet.get("live", false):
		bbcode += _cabinet_block(forces_cabinet)
	elif forces_cabinet is Dictionary:
		bbcode += "[color=#" + Utils.COLOR_INFO + "]THE CABINET — Talleyrand is at the Cabinet, free to send: press F1, choose a court, and send him on a mission.[/color]\n\n"

	# Authority — global player stat (V2b)
	var authority = int(cached_data.get("authority", 100))
	var authority_label = str(cached_data.get("authority_label", ""))
	var auth_color = Utils.COLOR_INFO
	if authority >= 80:
		auth_color = Utils.COLOR_SUCCESS
	elif authority < 50:
		auth_color = Utils.COLOR_ERROR
	bbcode += "Authority: [color=#" + auth_color + "]" + str(authority) + (" (" + authority_label + ")" if authority_label != "" else "") + "[/color]\n\n"

	if forces.size() == 0:
		bbcode += "[color=#" + Utils.COLOR_INFO + "]No marshals available.[/color]\n"
		content_area.text = Utils.dress_heads(bbcode)
		return

	# UXR3-41: the Emperor's corps leads the muster — his state is the line
	# the Seat's point turns on (the backend marks him `sovereign`).
	var muster: Array = []
	for f in forces:
		if bool(f.get("sovereign", false)):
			muster.push_front(f)
		else:
			muster.append(f)
	# Session UI-2: the corps' strength bars share one scale — the largest corps.
	var widest := 1
	for f in muster:
		widest = maxi(widest, int(f.get("strength", 0)))
	# Session UI-4 (November 12, 2026): the blind readers called the Forces body
	# "plain stacked text with small, repetitive rows" and asked for "each corps a
	# compact table row with a morale/trust bar". Folded (the default) the muster
	# is ONE table — the arm's glyph and the name, the strength on its meter,
	# morale and trust on theirs, where he stands, the state as a tag — and the
	# rest of each corps' card (the facts, W/L, stance, order, flags, the Seat)
	# opens behind the corps' name, a note of its own (`sl.forces.<name>`), under
	# the table. On the page every corps stands as the card it was.
	var folded := Utils.explanations_folded()
	var table_rows: Array = []
	var open_cards := ""
	# Session UI-5 interim fix (Nov 13): the glance card stands above the table.
	bbcode += _forces_figure_card(muster)
	for f in muster:
		var name = str(f.get("name", "?"))
		var unit_type = str(f.get("type", "infantry"))
		var loc = str(f.get("location", "?"))
		var strength = int(f.get("strength", 0))
		var morale = int(f.get("morale", 100))
		var trust = int(f.get("trust", 70))
		var stance = str(f.get("stance", "neutral"))
		var status = str(f.get("status", "idle"))
		var strat = str(f.get("strategic_order", "None"))
		var won = int(f.get("battles_won", 0))
		var lost = int(f.get("battles_lost", 0))
		var flags = f.get("special_flags", {})
		var note_id := "sl.forces." + name.replace(" ", "_")

		# Session UI-2: the card leads with its header — the arm's glyph, the
		# name in gilt, the arm in words (UXR3-F6: never a bracketed "[INF]"),
		# the state as a badge — then the strength as a figure on its meter.
		var arm_glyph := "foot"
		if unit_type == "cavalry":
			arm_glyph = "horse"
		elif unit_type == "artillery":
			arm_glyph = "guns"
		var head := Utils.bb_glyph(arm_glyph, 18, Utils.COLOR_GOLD) + " "
		if bool(f.get("sovereign", false)):
			head += "[color=#" + Utils.COLOR_GOLD + "]THE EMPEROR — " + name + "[/color]"
		else:
			head += "[color=#" + Utils.COLOR_GOLD + "]" + name + "[/color]"
		head += "  [color=#" + Utils.COLOR_INFO + "]" + unit_type.capitalize() + "[/color]"
		var badge_tone := ""
		match status:
			"broken", "retreating", "captured":
				badge_tone = Utils.cv_hex("8b2a2a")
			"drilling":
				badge_tone = "3a4a6b"
			"idle":
				pass
			_:
				badge_tone = Utils.COLOR_BADGE_QUIET
		if badge_tone != "":
			head += "  " + Utils.bb_badge(status.replace("_", " ").to_upper(), badge_tone)
		var strength_line := "  Strength: [color=#" + Utils.COLOR_GOLD + "]" + _format_number(strength) + "[/color]  " \
			+ Utils.bb_meter(strength, widest, 150, 8) + "\n"
		# The Seat (NP-5): the Emperor holding court in his own capital is
		# worth a diplomatic point a turn — the backend's own figure.
		var seat_dp := int(f.get("seat_dp", 0))
		var seat_line := ""
		if seat_dp > 0:
			seat_line = "  [color=#" + Utils.COLOR_GOLD + "]Holds court at " + str(f.get("location", "")) \
				+ " — the Seat: +" + str(seat_dp) + " DP a turn[/color]\n"

		# Trust + morale with color thresholds
		var trust_color = Utils.COLOR_INFO
		var trust_fill = Utils.cv_hex(Utils.COLOR_SUCCESS)
		if trust < 30:
			trust_color = Utils.cv_hex(Utils.COLOR_ERROR)
			trust_fill = Utils.cv_hex(Utils.COLOR_ERROR)
		elif trust < 55:
			trust_color = Utils.COLOR_ORANGE
			trust_fill = Utils.COLOR_ORANGE

		var morale_color = Utils.COLOR_INFO
		var morale_fill = Utils.cv_hex(Utils.COLOR_SUCCESS)
		if morale < 40:
			morale_color = Utils.cv_hex(Utils.COLOR_ERROR)
			morale_fill = Utils.cv_hex(Utils.COLOR_ERROR)
		elif morale < 60:
			morale_color = Utils.COLOR_ORANGE
			morale_fill = Utils.COLOR_ORANGE

		# The figures line: where, morale and trust on their meters, W/L.
		# FA-32 (slice 11): this tab listed a PRISONER as an idle corps standing
		# in the captor's own capital at strength 0 with "No active orders" —
		# the persistent surface the player opens, saying the one thing that is
		# not true. Where he is held is not where he is posted.
		var where_text := ""
		var figures_line := ""
		if bool(f.get("captured", false)):
			var captor = Utils.display_nation_name(str(f.get("captured_by", "")))
			where_text = "[color=#" + Utils.COLOR_ERROR + "]Held by " + captor + " at " + loc + "[/color]"
			figures_line += "  " + where_text
		else:
			where_text = loc
			figures_line += "  Location: " + loc
		figures_line += "   " + Utils.bb_glyph("morale", 16, morale_fill) + " Morale: [color=#" + morale_color + "]" + str(morale) + "%[/color] " \
			+ Utils.bb_meter(morale, 100, 60, 7, morale_fill)
		figures_line += "   " + Utils.bb_glyph("trust", 16, trust_fill) + " Trust: [color=#" + trust_color + "]" + str(trust) + "[/color] " \
			+ Utils.bb_meter(trust, 100, 60, 7, trust_fill)
		figures_line += "   W/L: " + str(won) + "/" + str(lost) + "\n"

		# The notes under the figures: status and stance, the order, the flags.
		# FA-32: the status of a prisoner reads in the error colour, as before.
		var status_color = Utils.COLOR_INFO
		match status:
			"broken", "retreating", "captured":
				status_color = Utils.COLOR_ERROR
			"drilling":
				status_color = Utils.COLOR_BLUE
			"idle":
				status_color = Utils.COLOR_INFO
		var notes: String = "  [color=#" + Utils.COLOR_INFO + "]Status:[/color] [color=#" + status_color + "]" + status.replace("_", " ").capitalize() + "[/color]"
		notes += "  [color=#" + Utils.COLOR_INFO + "]Stance: " + stance + "[/color]\n"

		# Strategic order
		if strat != "None":
			notes += "  Order: " + strat + "\n"

		# Special flags
		var flag_parts = []
		if flags.get("shock_ready", false):
			flag_parts.append("SHOCK READY")
		if flags.get("counter_punch", false):
			flag_parts.append("COUNTER-PUNCH")
		if int(flags.get("reckless", 0)) > 0:
			flag_parts.append("RECKLESS:" + str(int(flags.get("reckless", 0))))
		if flags.get("exhausted", false):
			flag_parts.append("EXHAUSTED")
		if flag_parts.size() > 0:
			notes += "  [color=#" + Utils.COLOR_ORANGE + "]" + " | ".join(flag_parts) + "[/color]\n"

		if folded:
			# The table row: the name opens the corps' card (its hover says so).
			var open_here := Utils.note_is_open(note_id)
			var name_link := "[url=" + Utils.NOTE_META + note_id + "]" \
				+ Utils.bb_hint("[color=#" + Utils.COLOR_GOLD + "]" + ("▾ " if open_here else "▸ ") + name + "[/color]", "Open " + name + "'s card — the facts, W/L, stance, order and flags.") + "[/url]"
			var name_cell := Utils.bb_glyph(arm_glyph, 18, Utils.COLOR_GOLD) + " " + name_link
			if bool(f.get("sovereign", false)):
				name_cell = Utils.bb_glyph(arm_glyph, 18, Utils.COLOR_GOLD) + " [color=#" + Utils.COLOR_GOLD + "]THE EMPEROR —[/color] " + name_link
			var tag_tone := badge_tone if badge_tone != "" else Utils.COLOR_BADGE_QUIET
			var state_cell := Utils.bb_tag(status.replace("_", " ").to_upper(), tag_tone)
			if strat != "None":
				state_cell += " [color=#" + Utils.COLOR_INFO + "]" + strat + "[/color]"
			table_rows.append([
				name_cell,
				"[color=#" + Utils.COLOR_GOLD + "]" + _format_number(strength) + "[/color] " + Utils.bb_meter(strength, widest, 72, 8),
				"[color=#" + morale_color + "]" + str(morale) + "%[/color] " + Utils.bb_meter(morale, 100, 44, 7, morale_fill),
				"[color=#" + trust_color + "]" + str(trust) + "[/color] " + Utils.bb_meter(trust, 100, 44, 7, trust_fill),
				where_text,
				state_cell,
			])

		# Session UI: a corps a card (the marks; `card_underlay.gd` paints). On the
		# page every corps stands as a card; Folded only the corps whose note was
		# opened stands under the table, with its `▾ less`.
		if not folded or Utils.note_is_open(note_id):
			var card := Utils.card_open()
			card += head + (("  " + Utils.note_link(note_id)) if folded else "") + "\n"
			card += strength_line + seat_line + figures_line + notes
			card += Utils.CARD_CLOSE
			card += "\n"
			if folded:
				open_cards += card
			else:
				bbcode += card

	if folded:
		bbcode += Utils.bb_table(["Corps", "Strength", "Morale", "Trust", "Location", "Order"], table_rows, [], [5, 4, 3, 3, 4, 5], _table_px()) + "\n"
		bbcode += open_cards

	content_area.text = Utils.dress_heads(bbcode)


func _forces_figure_card(muster: Array) -> String:
	"""Session UI-5: the Forces book's foot — the army's composition as ONE bar
	(foot / horse / guns, a share of the whole) and the corps' states as chips,
	both read from the corps the payload already lists."""
	var by_arm := {"foot": 0, "horse": 0, "guns": 0}
	var states := {}
	var total := 0
	for f in muster:
		var strength: int = int(f.get("strength", 0))
		var arm := "foot"
		var unit_type: String = str(f.get("type", "infantry"))
		if unit_type == "cavalry":
			arm = "horse"
		elif unit_type == "artillery":
			arm = "guns"
		by_arm[arm] = int(by_arm[arm]) + strength
		total += strength
		var status: String = str(f.get("status", "idle"))
		var word := "Ready"
		match status:
			"moving_to", "pursuing", "supporting", "following":
				word = "On the march"
			"fortified":
				word = "Fortified"
			"drilling":
				word = "Drilling"
			"awaiting_decision":
				word = "Awaiting a decision"
			"broken", "retreating":
				word = "Broken"
			"captured":
				word = "Captured"
		states[word] = int(states.get(word, 0)) + 1
	# Session UI-5 interim fix (Nov 13): palette tones (the meters' own green and
	# gilt), not the saturated blue.
	var tones := {"foot": Utils.cv_hex(Utils.COLOR_SUCCESS), "horse": Utils.COLOR_GOLD, "guns": Utils.COLOR_ORANGE}
	var width := 220 if Utils.compact_view() else 340
	var out := Utils.card_open()
	out += Utils.bb_glyph("strength", 18, Utils.COLOR_GOLD) + " [color=#" + Utils.COLOR_GOLD + "]THE ARMY AT A GLANCE[/color]  [color=#" + Utils.COLOR_INFO + "]" + _format_number(total) + " men under arms[/color]\n"
	var bar := ""
	var legend := ""
	var spent := 0
	var arms: Array = ["foot", "horse", "guns"]
	for i in range(arms.size()):
		var arm_key: String = str(arms[i])
		var n: int = int(by_arm[arm_key])
		var share := 0
		if total > 0:
			share = int(round(100.0 * float(n) / float(total)))
		var w: int = 0
		if total > 0 and n > 0:
			w = maxi(1, int(round(float(width) * float(n) / float(total))))
		if i == arms.size() - 1:
			w = maxi(0, width - spent) if n > 0 else 0
		spent += w
		if w > 0:
			bar += "[img width=%d height=10 color=#%s]%s[/img]" % [w, str(tones[arm_key]), Utils.SWATCH]
		var arm_name: String = {"foot": "Foot", "horse": "Horse", "guns": "Guns"}[arm_key]
		legend += "   " + Utils.bb_glyph(arm_key, 16, str(tones[arm_key])) + " " + arm_name + " " + _format_number(n) + " (" + str(share) + "%)"
	if total <= 0:
		bar = Utils.bb_meter(0, 1, width, 10)
	out += "  " + bar + "\n" + " " + legend + "\n"
	var chips := ""
	for word in ["Ready", "On the march", "Fortified", "Drilling", "Awaiting a decision", "Broken", "Captured"]:
		var count: int = int(states.get(word, 0))
		if count <= 0:
			continue
		var tone := Utils.COLOR_BADGE_QUIET
		match word:
			"Fortified":
				tone = Utils.cv_hex("2f6b3a")
			"Drilling", "On the march":
				tone = "3a4a6b"
			"Broken", "Captured":
				tone = Utils.cv_hex("8b2a2a")
			"Awaiting a decision":
				tone = Utils.COLOR_WARNING
		chips += Utils.bb_tag(str(count) + " " + word, tone) + "  "
	out += "  [color=#" + Utils.COLOR_INFO + "]Corps:[/color] " + chips + "\n"
	out += Utils.CARD_CLOSE + "\n"
	return out


func _ceiling_line(econ: Dictionary, treasury: int) -> String:
	"""UXR3-41 (Pre-Deploy S12 part 2): the Ceiling line — where the Charges
	of Empire steer the chest at the rate in force. It LEADS the Economy tab
	(it sat under twenty lines of the books, below the fold on the boards
	that exist to show it); its three states and their colours are IQ1-2's."""
	var line := ""
	# IQ1-2: the ceiling had ONE sentence for three states, and the zero
	# sentinel meant the line VANISHED exactly when the chest was largest
	# (the charge had exceeded the gross, so the old post-charge argument
	# went negative). The three states are now named by the backend.
	var ceiling = int(econ.get("ceiling", 0))
	var ceiling_state = str(econ.get("ceiling_state", "bounded"))
	if ceiling_state == "unbounded":
		# Review round: name the CHARGES, not "the chest". This prints ~20
		# lines under an "Upkeep: -865g" line that IS drawing on the chest, so
		# "nothing is drawing on the chest" contradicted the payload above it.
		line += "  [color=#" + Utils.COLOR_INFO \
			+ "]Ceiling:  none — the charges of empire do not draw at this rate[/color]\n"
	elif ceiling_state == "no_surplus":
		# Review round: the COLOUR was inverted. This is the worst economic
		# state the tab can report — the treasury is not growing at all — and
		# it was rendered in the calmest colour in the palette, dimmer than
		# the merely-informational bounded line. It is an ERROR now, and the
		# sentence says what is true rather than what is absent.
		line += "  [color=#" + Utils.COLOR_ERROR \
			+ "]Ceiling:  none — the chest is not growing at this rate[/color]\n"
	elif ceiling > 0:
		if treasury > ceiling:
			# The chest is PAST its own fixed point, so the charges are pulling
			# it back down. ⚠ REVIEW ROUND CORRECTION: the first version of
			# this comment said the case "could not previously be rendered at
			# all". That is FALSE and the review caught it — the case WAS
			# rendered before, by the generic arm below, with the wrong copy
			# ("where the charges level the chest off") and, at a chest above
			# a quarter of the ceiling, the calm colour. What was unreachable
			# was a ceiling BELOW the chest that is also CORRECT; the old
			# post-charge argument understated it toward zero.
			line += "  [color=#" + Utils.COLOR_WARNING + "]Ceiling:  " \
				+ _format_number(ceiling) \
				+ "g  — the chest is above it; the charges are drawing it down[/color]\n"
		else:
			var ceil_color = Utils.COLOR_INFO
			if treasury > 0 and ceiling > treasury * 4:
				ceil_color = Utils.COLOR_WARNING
			line += "  [color=#" + ceil_color + "]Ceiling:  " + _format_number(ceiling) \
				+ "g  (where the charges level the chest off at this rate)[/color]\n"
	return line


func _render_territories():
	var territories = cached_data.get("territories", [])
	var bbcode = ""
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]═══ TERRITORIES ═══[/color]" + Utils.lead_mark("The provinces of the Empire — who holds each, what it pays, how quietly it sits under you.", "sl.territories.lead") + "\n"
	bbcode += _dated_line()
	bbcode += Utils.bb_lead("[color=#" + Utils.COLOR_INFO + "]The provinces of the Empire — who holds each, what it pays, how quietly it sits under you.[/color]\n\n", "sl.territories.lead")
	bbcode += _collapse_note_line()
	bbcode += _fall_clock_lines()
	bbcode += _congress_clock_line()

	if territories.size() == 0:
		bbcode += "[color=#" + Utils.COLOR_INFO + "]No territories controlled.[/color]\n"
		content_area.text = Utils.dress_heads(bbcode)
		return

	# Session UI-2: the provinces as ONE table — province, kind, income, stability
	# on its meter, supply as a badge with its figures, garrison, buildings.
	var rows: Array = []
	for t in territories:
		var name = str(t.get("name", "?"))
		var terrain = str(t.get("terrain", "plains"))
		var rtype = str(t.get("region_type", "town"))
		var garrison = int(t.get("garrison", 0))
		var supply_cap = int(t.get("supply_capacity", 0))
		var occupants = int(t.get("occupant_count", 0))
		var supply_status = str(t.get("supply_status", "OK"))
		var stability = int(t.get("stability", 100))
		var war_dmg = int(t.get("war_damage", 0))
		var income = int(t.get("income", 0))
		var buildings = t.get("buildings", [])

		var stab_fill = Utils.cv_hex(Utils.COLOR_SUCCESS)
		if stability < 40:
			stab_fill = Utils.cv_hex(Utils.COLOR_ERROR)
		elif stability < 70:
			stab_fill = Utils.COLOR_ORANGE
		var stab_cell = Utils.bb_meter(stability, 100, 56, 7, stab_fill) + " " + str(stability) + "%"
		if war_dmg > 0:
			stab_cell += "  Damage: " + str(war_dmg) + "%"

		# Supply status.
		# WO slice 8 in-game pass [V-1]: the backend gained a THIRD verdict
		# ("Crowded" — the death-ball arm, 3+ corps billing 2%+/turn under
		# the cap) and this colour map still knew only two, so a province
		# bleeding men was painted in the same tone as a healthy one.
		# The slice's own test asserted the backend STRING and never the
		# render — the un-rewritten-sibling class the review round named,
		# caught by driving the game.
		var supply_tone = Utils.cv_hex("2f6b3a")
		if supply_status == "Over capacity":
			supply_tone = Utils.cv_hex("8b2a2a")
		elif supply_status == "Crowded":
			supply_tone = Utils.COLOR_WARNING
		elif supply_status != "OK":
			supply_tone = Utils.COLOR_BADGE_QUIET
		# "(1 marshals" read as a typo on every single-corps province.
		var _corps_word = " marshal, cap " if occupants == 1 else " marshals, cap "
		# a table cell: the verdict an inline tag, its terms on the cell's second line
		# Session UI-4 (November 12, 2026): ONE line — the readers saw two-line rows
		# ("the wrapped city, plains column", "the dash-filled columns waste space").
		# Session UI-5 interim fix (Nov 13): the chip and a compact cap; the full
		# sentence rides the cell's hover.
		var cap_short := (str(int(round(float(supply_cap) / 1000.0))) + "k") if supply_cap >= 1000 else str(supply_cap)
		var corps_part := (str(occupants) + " corps · ") if occupants > 0 else ""
		var supply_cell = Utils.bb_hint(Utils.bb_tag(supply_status, supply_tone) + " [color=#" + Utils.COLOR_INFO + "]· " \
			+ corps_part + "cap " + cap_short + "[/color]",
			supply_status + " (" + str(occupants) + _corps_word + _format_number(supply_cap) + ")")

		# Buildings
		var bld_parts = []
		for b in buildings:
			var bname = str(b.get("name", "?"))
			var bstatus = str(b.get("status", "built"))
			if bstatus == "built":
				bld_parts.append(bname)
			elif bstatus == "damaged":
				bld_parts.append("[color=#" + Utils.COLOR_ERROR + "]" + bname + " (damaged)[/color]")
			else:
				bld_parts.append("[color=#" + Utils.COLOR_BLUE + "]" + bname + " (" + bstatus + ")[/color]")

		rows.append({
			"name": name, "income": income, "garrison": garrison, "group": _terr_group_key(t, rtype),
			"cells": [
				"[color=#" + Utils.COLOR_GOLD + "]" + name + "[/color] ",
				"[color=#" + Utils.COLOR_INFO + "]" + rtype.replace("_", " ") + " · " + terrain.replace("_", " ") + "[/color] ",
				str(income) + "g ",
				stab_cell + " ",
				supply_cell + " ",
				(_format_number(garrison) if garrison > 0 else "—") + " ",
				(", ".join(bld_parts) if bld_parts.size() > 0 else "—"),
			],
		})

	# Session UI-5: the provinces in groups — by how each came to be held (the
	# payload's `origin`: home soil, then the court it was taken from), or by
	# KIND on a payload without it — each with a subtotal row (count, income,
	# garrison) that folds its rows, and a sort toggle (income ↓ / name A–Z)
	# the session remembers.
	bbcode += _terr_sort_line()
	var cells: Array = []
	var first_key := ""
	for g in _terr_groups(rows):
		var key: String = str(g[0])
		var members: Array = []
		for r in rows:
			if str(r["group"]) == key:
				members.append(r)
		if members.is_empty():
			continue
		if first_key == "":
			first_key = key
		if _terr_sort == "name":
			members.sort_custom(func(a, b): return str(a["name"]) < str(b["name"]))
		else:
			members.sort_custom(func(a, b): return int(a["income"]) > int(b["income"]) or (int(a["income"]) == int(b["income"]) and str(a["name"]) < str(b["name"])))
		var sum_income := 0
		var sum_garrison := 0
		for r in members:
			sum_income += int(r["income"])
			sum_garrison += int(r["garrison"])
		var is_open: bool = bool(_terr_open.get(key, key == first_key))
		var fold_link := "[url=terr:fold:" + key + "]" \
			+ Utils.bb_hint("[color=#" + Utils.COLOR_GOLD + "]" + ("▾ " if is_open else "▸ ") + str(g[1]) + "[/color]", ("Fold" if is_open else "Open") + " the " + str(g[1]).to_lower() + " group.") + "[/url]"
		cells.append([
			"[b]" + fold_link + "[/b]",
			"[color=#" + Utils.COLOR_INFO + "]" + str(members.size()) + (" province" if members.size() == 1 else " provinces") + "[/color]",
			"[b]" + str(sum_income) + "g[/b] ",
			"", "",
			"[b]" + (_format_number(sum_garrison) if sum_garrison > 0 else "—") + "[/b] ",
			"",
		])
		if is_open:
			for r in members:
				cells.append(r["cells"])
	bbcode += Utils.bb_table(["Province", "Kind", "Income", "Stability", "Supply", "Garrison", "Buildings"],
		cells, [2, 5], [3, 5, 2, 4, 7, 2, 5], _table_px()) + "\n"

	content_area.text = Utils.dress_heads(bbcode)


# Session UI-5: the territory groups, in the order they read (key, heading).
const _TERR_GROUPS := [
	["seat", "Capital and great cities"],
	["city", "Cities"],
	["town", "Towns"],
	["rural", "Countryside"],
]

var _terr_sort: String = "income"
var _terr_open: Dictionary = {}


func _terr_group_of(rtype: String) -> String:
	match rtype:
		"capital", "major_city":
			return "seat"
		"city":
			return "city"
		"rural":
			return "rural"
	return "town"


func _terr_group_key(t: Dictionary, rtype: String) -> String:
	"""A row's group: by origin when the payload carries it ("home", the court
	it was taken from, "" = none recorded), else by kind."""
	if t.has("origin"):
		var origin: String = str(t.get("origin", ""))
		if origin == "home":
			return "home"
		return ("from:" + origin) if origin != "" else "other"
	return _terr_group_of(rtype)


func _terr_groups(rows: Array) -> Array:
	"""[key, heading] in reading order for the rows at hand: home soil first,
	then each court's provinces (the largest share first), then the rest; or
	the kinds, for a payload without origins."""
	var by_origin := false
	var counts := {}
	for r in rows:
		var key: String = str(r["group"])
		counts[key] = int(counts.get(key, 0)) + 1
		if key == "home" or key == "other" or key.begins_with("from:"):
			by_origin = true
	if not by_origin:
		return _TERR_GROUPS
	var out: Array = []
	if counts.has("home"):
		out.append(["home", "Home"])   # one line in the Province column (UI-5 interim fix)
	var courts: Array = []
	for key in counts.keys():
		if str(key).begins_with("from:"):
			courts.append(str(key))
	courts.sort_custom(func(a, b): return int(counts[a]) > int(counts[b]) or (int(counts[a]) == int(counts[b]) and a < b))
	for key in courts:
		out.append([key, "Taken from " + Utils.display_nation_name(str(key).substr(5))])
	if counts.has("other"):
		out.append(["other", "Other lands"])
	return out


func _terr_first_group_key() -> String:
	var rows: Array = []
	for t in cached_data.get("territories", []):
		if t is Dictionary:
			rows.append({"group": _terr_group_key(t, str(t.get("region_type", "town")))})
	for g in _terr_groups(rows):
		return str(g[0])
	return ""


func _terr_sort_line() -> String:
	var line := "[color=#" + Utils.COLOR_INFO + "]Sort:[/color] "
	for opt in [["income", "Income ↓"], ["name", "Name A–Z"]]:
		var on: bool = _terr_sort == str(opt[0])
		line += Utils.bb_button_chip("terr:sort:" + str(opt[0]), str(opt[1]),
			Utils.COLOR_GOLD if on else Utils.COLOR_INFO, _NAVAL_CHIP_BG) + " "
	return line + "\n\n"


func _econ_row(rows: Array, label: String, amount, note: String = "", counts: bool = true, tone: String = "", sub: bool = false) -> void:
	# Session UI-4 (November 12, 2026): one line of the books as DATA — its label,
	# its signed figure (null = a line of words only), the note that rides beside
	# it, whether it is part of Net (`counts`), and a colour for the figure that
	# overrides the sign's own (the informational Materiel is dim).
	rows.append({"label": label, "amount": amount, "note": note, "counts": counts, "tone": tone, "sub": sub})


func _econ_signed(n: int) -> String:
	# the books' figures carry the thousands mark the tiles above them do
	# ("+2,590g" under "8,677G" — the table printed "+2590g")
	return ("+" if n >= 0 else "-") + _format_number(absi(n)) + "g"


func _econ_cells(r: Dictionary, bold: bool = false) -> Array:
	# A row's three cells. The label in plain ink (a sub-line indented, in dim ink);
	# the figure signed — green for money in, crimson for money out — in tabular
	# figures (the table right-aligns it); the note dim. A long note rides the
	# label's hover Folded (Utils.bb_hint) and prints in its column On the page.
	var label := str(r.get("label", ""))
	var note := str(r.get("note", ""))
	var amount = r.get("amount", null)
	var shown_note := note
	if Utils.explanations_folded() and note.length() > 44 and label != "":
		label = Utils.bb_hint(label, note)
		shown_note = ""
	var label_cell := label
	if not bool(r.get("counts", true)) and amount != null:
		label_cell = "[color=#" + Utils.COLOR_INFO + "]" + label + "[/color]"
	var fig := ""
	if amount != null:
		var tone := str(r.get("tone", ""))
		if tone == "":
			tone = Utils.COLOR_SUCCESS if int(amount) >= 0 else Utils.COLOR_ERROR
		fig = "[color=#" + tone + "]" + _econ_signed(int(amount)) + "[/color]"
	var note_cell := ""
	if shown_note != "":
		note_cell = "[color=#" + Utils.COLOR_INFO + "]" + shown_note + "[/color]"
	if bold:
		label_cell = "[b]" + label_cell + "[/b]"
		if fig != "":
			fig = "[b]" + fig + "[/b]"
	return [label_cell, fig, note_cell]


func _econ_table(rows: Array, subtotal: bool, subtotal_label: String) -> String:
	# Session UI-4: a block of the books as ONE table — line | figure | note —
	# the figure column right-aligned so the gold reads down a column. The
	# subtotal is printed only by a caller that has proved the rows reconcile to
	# the payload's own Net (see _render_economy); lines outside Net follow it.
	var counted: Array = []
	var outside: Array = []
	var total := 0
	for r in rows:
		if bool(r.get("counts", true)) or r.get("amount", null) == null or bool(r.get("sub", false)):
			counted.append(r)
			if r.get("amount", null) != null and bool(r.get("counts", true)):
				total += int(r.get("amount", 0))
		else:
			outside.append(r)
	var cells: Array = []
	for r in counted:
		cells.append(_econ_cells(r))
	if subtotal:
		cells.append(_econ_cells({"label": subtotal_label, "amount": total, "note": "", "counts": true, "tone": ""}, true))
	for r in outside:
		cells.append(_econ_cells(r))
	# Session UI-5 interim fix (Nov 13): the Note column goes when every note is empty.
	var any_note := false
	for c in cells:
		if str(c[2]) != "":
			any_note = true
			break
	if not any_note:
		var slim: Array = []
		for c in cells:
			slim.append([c[0], c[1]])
		return Utils.bb_table(["Line", "Gold"], slim, [1], [ECON_COLS[0], ECON_COLS[1]], _table_px()) + "\n"
	return Utils.bb_table(["Line", "Gold", "Note"], cells, [1], ECON_COLS, _table_px()) + "\n"


func _table_px() -> float:
	"""Session UI-4: the width a book's table spans (Utils.bb_table's
	`width_px`) — the page's own, less the scroll bar and the card margins;
	0 (natural width) before the page has a size."""
	if content_area == null or content_area.size.x < 320.0:
		return 0.0
	return content_area.size.x - 48.0


func _render_economy():
	var econ = cached_data.get("economy", {})
	var bbcode = ""
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]═══ ECONOMY ═══[/color]" + Utils.lead_mark("The treasury's books — income against upkeep, and every charge with its name on it.", "sl.economy.lead") + "\n"
	bbcode += _dated_line()
	bbcode += Utils.bb_lead("[color=#" + Utils.COLOR_INFO + "]The treasury's books — income against upkeep, and every charge with its name on it.[/color]\n\n", "sl.economy.lead")

	var treasury = int(econ.get("treasury", 0))
	var income = int(econ.get("income", 0))
	var upkeep = int(econ.get("upkeep", 0))
	var net = int(econ.get("net", 0))
	var bankruptcy = int(econ.get("bankruptcy_turns", 0))

	var trade = int(econ.get("trade_income", 0))

	# Session UI-4 (November 12, 2026): the blind readers called this body "a flat
	# list of gold-on-navy lines" and asked for "a two-column table with
	# right-aligned figures and color-coded signs". The books are now two TABLES —
	# INCOME, then CHARGES — each line its label, its signed figure and its note;
	# a subtotal under a block, and Net bold and last. Every line keeps its words
	# (a long note rides its label's hover Folded; On the page it prints). A
	# subtotal is printed ONLY when the rows printed sum to the payload's own Net —
	# never a figure the backend did not stand behind (SC-33).
	var inc: Array = []
	var chg: Array = []
	var outside: Array = []
	# Session UI-4: these two repeat the tiles above (the readers: "drop the
	# redundant header lines") — folded they stand behind the book's ⓘ.
	bbcode += Utils.bb_lead("  Treasury: " + _format_number(treasury) + "g\n", "sl.economy.lead")
	# UXR3-41: the ceiling leads the books (the helper's comment).
	bbcode += Utils.bb_lead(_ceiling_line(econ, treasury), "sl.economy.lead")
	var income_prefix := "  Income:   +"  # the old line's own words; the row's label is its name
	# (strip again after the "+": "Income:   +" left its colon behind the spaces)
	_econ_row(inc, income_prefix.strip_edges().trim_suffix("+").strip_edges().trim_suffix(":"), income)
	if trade > 0:
		_econ_row(inc, "Trade", trade)
	# PRE-EC ledger floor (ECONOMY_REVISIT_SPEC.md §0): admin_bonus, treaty_gold
	# and vassal_tribute are folded into `net` by ledger.py _build_economy but
	# were never rendered here, so the visible lines did not sum to Net whenever
	# France held a vassal (tribute) or a gold-per-turn treaty clause (the SC-33
	# "invisible tribute" bug class). Render every component that feeds Net.
	var admin_bonus = int(econ.get("admin_bonus", 0))
	if admin_bonus != 0:
		_econ_row(inc if admin_bonus > 0 else chg, "Admin", admin_bonus)
	var treaty_gold = int(econ.get("treaty_gold", 0))
	if treaty_gold != 0:
		_econ_row(inc if treaty_gold > 0 else chg, "Treaty", treaty_gold)
	var vassal_tribute = int(econ.get("vassal_tribute", 0))
	if vassal_tribute != 0:
		_econ_row(inc if vassal_tribute > 0 else chg, "Tribute", vassal_tribute)
	# SC-33 recurring settlement streams (G4F smoke follow-up): the ratified
	# gold-per-turn tribute is real per-turn cash — show its net line and the
	# per-stream detail instead of leaving it dispatch-only.
	var settlement_gold = int(econ.get("settlement_gold", 0))
	if settlement_gold != 0:
		_econ_row(inc if settlement_gold > 0 else chg, "Settlements", settlement_gold)
	# EA-1 (the economy audit, Oct 5 2026): the recurring transfers between
	# courts, signed, each stream naming its counterparty and what is owed —
	# a sponsorship moved the chest 200 a turn and no line said so.
	# EA-4 (the economy audit, Oct 5 2026): the Continental System's closure
	# on the trade we actually earn across the line — its own Net line.
	var cs_loss = int(econ.get("continental_system", 0))
	if cs_loss > 0:
		_econ_row(chg, "Continental System", -cs_loss, "trade with Britain closed")
	var subsidies = int(econ.get("subsidies", 0))
	var subsidy_streams = econ.get("subsidy_streams", [])
	if subsidies != 0 or (subsidy_streams is Array and subsidy_streams.size() > 0):
		var sub_rows: Array = []
		_econ_row(sub_rows, "Subsidies", subsidies)
		if subsidy_streams is Array:
			for st in subsidy_streams:
				if not (st is Dictionary):
					continue
				var incoming = str(st.get("direction", "")) == "incoming"
				var who = Utils.display_nation_name(str(st.get("counterparty", "")))
				var amount = int(st.get("amount", 0))
				var owed = int(st.get("owed", amount))
				var line = ""
				if owed > amount:
					line += str(owed) + "g owed — the chest paid " + str(amount) + "g"
				var left = int(st.get("turns_remaining", 0))
				if left > 0:
					line += (", " if line != "" else "") + str(left) + " turn" + ("s" if left != 1 else "") + " left"
				_econ_row(sub_rows, "    " + ("from " if incoming else "to ") + who, amount if incoming else -amount, line, false, "", true)
		if subsidies >= 0:
			inc.append_array(sub_rows)
		else:
			chg.append_array(sub_rows)
	# ES-2 (Economy Revisit S6): recurring cost of holding non-homeland
	# soil — a signed Net component of its own (Income stays gross), so it
	# must render for the visible lines to sum to Net (SC-33 invariant).
	var occupation = int(econ.get("occupation", 0))
	if occupation > 0:
		_econ_row(chg, "Occupation", -occupation)
	# EC-W1 (Econ War-Coupling): income suspended by hostile armies standing
	# on our provinces — its own signed Net component (SC-33 contract).
	var contributions = int(econ.get("contributions", 0))
	if contributions > 0:
		_econ_row(chg, "Contributions", -contributions)
	# EB-5a (Econ Balance): what our own armies requisition from the enemy
	# provinces they disrupt — a positive signed Net component.
	var requisitions = int(econ.get("requisitions", 0))
	if requisitions > 0:
		_econ_row(inc, "Requisitions", requisitions)
	# EB-2 (Econ Balance): the authored overseas/colonial pool, modulated
	# by who commands the sea — a positive signed Net component.
	var overseas = int(econ.get("overseas", 0))
	if overseas > 0:
		_econ_row(inc, "Overseas trade", overseas)
	# EB-1 (Econ Balance): the Charges of Empire — the condition-priced
	# draw on the treasury (absorbs EC-W2's War Effort; the WE term rides
	# inside the rate). The named terms render so the rate explains itself.
	var state_charges = int(econ.get("state_charges", 0))
	if state_charges > 0:
		var terms_text := ""
		var charge_terms = econ.get("state_charges_terms", [])
		if charge_terms is Array and charge_terms.size() > 0:
			var term_bits = []
			for t in charge_terms:
				term_bits.append(str(t.get("label", "")) + " +" + str(int(t.get("amount", 0))))
			# Slice 17 review round (L2-7): the terms are rate points, not gold —
			# the backend states the unit from the constants it computes with.
			var rate_note = str(econ.get("state_charges_rate_note", ""))
			terms_text = ", ".join(PackedStringArray(term_bits))
			if rate_note != "":
				terms_text += " — " + rate_note
		_econ_row(chg, "Charges of Empire", -state_charges, terms_text)
		# SR-5a question (c): why the draw moved since the last charged turn.
		var charges_delta_note = str(econ.get("state_charges_delta_note", ""))
		if charges_delta_note != "":
			_econ_row(chg, "", null, charges_delta_note)
	# ES-7 (Economy Revisit S7): income of provinces endowed to marshals'
	# estates — a signed Net component of its own (Income stays gross), so
	# it must render for the visible lines to sum to Net (SC-33 invariant).
	var dotation_skim = int(econ.get("dotation_skim", 0))
	if dotation_skim > 0:
		_econ_row(chg, "Dotations", -dotation_skim)
	# ES-7 second pass (§0.6.8): the rente bill — treasury pensions at
	# premium; its own signed Net component (same SC-33 contract).
	var rente_cost = int(econ.get("rente_cost", 0))
	if rente_cost > 0:
		_econ_row(chg, "Rentes", -rente_cost)
	# SR-5r RF-1 (REFORMS_SPEC §2.2): the upkeep of the laws in force — its
	# own signed Net component (same SC-33 contract).
	var laws = int(econ.get("laws", 0))
	if laws > 0:
		_econ_row(chg, "Laws", -laws)
	# EC-U2 (Combat Overhaul Phase 4): per-turn maintenance of built
	# structures (depots, forts, training grounds, markets, stables,
	# watchtowers) — the conquest-free gold sink; its own signed Net
	# component (same SC-33 contract, NET_GOLD_COMPONENTS-guarded).
	var infrastructure = int(econ.get("infrastructure", 0))
	if infrastructure > 0:
		_econ_row(chg, "Infrastructure", -infrastructure)
	# DEF-5 naval (NV-1): the blockade's trade suspension + the Admiralty's
	# war ship upkeep — signed Net components (same SC-33 contract).
	var blockade = int(econ.get("blockade", 0))
	if blockade > 0:
		# SR-5r RF-2 (T8): the backend says what the blockade does to our
		# trade — "halved", or the deeper cut and the law that made it.
		var blockade_note = str(econ.get("blockade_note", ""))
		if blockade_note == "":
			blockade_note = "trade halved under enemy sail"
		_econ_row(chg, "Blockade", -blockade, blockade_note)
	# DY-7 (DYNAMISM_SPEC.md §6): a crown unrecognized — our trade with the
	# withholding courts halved; its own signed Net component (SC-33).
	var recognition = int(econ.get("recognition", 0))
	if recognition > 0:
		_econ_row(chg, "Recognition", -recognition, "the courts that withhold our crown trade at half")
	var admiralty = int(econ.get("admiralty", 0))
	if admiralty > 0:
		_econ_row(chg, "Admiralty", -admiralty)
	# FA-D26 (slice 17, Phase 2): the Butcher's Bill (EC-W3) — charged at the
	# battle, OUTSIDE Net by design (the plunder-gold precedent), so it is
	# informational: dimmed, and NOT part of the SC-33 sum above.
	var materiel = int(econ.get("materiel", 0))
	if materiel > 0:
		_econ_row(outside, "Materiel", -materiel, "guns, horses and stores lost with the fallen this turn — paid at the field, outside Net", false, Utils.COLOR_INFO)
	# ES-3 (Economy Revisit S5): Upkeep is split into the base line and an
	# over-limit surcharge line (backend guarantees base + surcharge == the
	# folded total, so the visible lines still sum to Net — §3 invariant).
	var upkeep_surcharge = int(econ.get("upkeep_surcharge", 0))
	var upkeep_base = int(econ.get("upkeep_base", upkeep))
	# EC-U3: the surcharge splits into the ES-3 over-limit part and the Grande
	# Armée premium (a supermassive standing army's diseconomies of scale).
	var grande_armee = int(econ.get("grande_armee", 0))
	# EAD-1 (the economy gate): campaign pay is part of the surcharge too.
	var campaign_pay = int(econ.get("campaign_pay", 0))
	var over_limit_surcharge = upkeep_surcharge - grande_armee - campaign_pay
	# SR-5a question (c): the army is paid for the men under arms today, and
	# the note says how the bill moved since the last turn it was charged.
	_econ_row(chg, "Upkeep", -upkeep_base, str(econ.get("upkeep_note", "")))
	if over_limit_surcharge > 0:
		var force_limit = int(econ.get("force_limit", 0))
		var army_total = int(econ.get("army_strength_total", 0))
		var over_note := ""
		if force_limit > 0:
			over_note = _format_number(army_total) + " / " + _format_number(force_limit) + " force limit"
		_econ_row(chg, "Over-limit surcharge", -over_limit_surcharge, over_note)
	if grande_armee > 0:
		_econ_row(chg, "Grande Armée surcharge", -grande_armee)
	if campaign_pay > 0:
		# EAD-1: the corps fed by contract on allied or neutral soil, named.
		var fed_at = []
		var ground = econ.get("campaign_ground", [])
		if ground is Array:
			for g in ground:
				if g is Dictionary:
					fed_at.append(str(g.get("marshal", "")) + " at " + str(g.get("region", "")) + " (" + str(g.get("holder", "")) + ")")
		var pay_note := ""
		if fed_at.size() > 0:
			pay_note = "fed by contract on allied or neutral soil: " + ", ".join(PackedStringArray(fed_at))
		_econ_row(chg, "Campaign pay", -campaign_pay, pay_note)

	# The subtotals stand only if the printed rows reach the payload's own Net.
	var rows_sum := 0
	for r in inc + chg:
		if bool(r.get("counts", true)) and r.get("amount", null) != null:
			rows_sum += int(r.get("amount", 0))
	var reconciles: bool = (rows_sum == net)

	# Session UI-2: the two groups stand here, under the heading each is named by.
	bbcode += Utils.bb_section("INCOME", "income") + _econ_table(inc, reconciles, "Subtotal")
	bbcode += Utils.bb_section("CHARGES", "admin") + _econ_table(chg + outside, reconciles, "Subtotal")

	# "The Levy is Open" (econ spec review §6). The force limit used to render
	# ONLY inside the over-limit branch above — visible exactly while the gate
	# was shut, and gone the moment it opened. It is now a standing line, and
	# when there is room under the ordinance it says what the room costs.
	var levy = econ.get("levy", {})
	if levy is Dictionary and int(levy.get("force_limit", 0)) > 0:
		var l_army = int(levy.get("army_strength", 0))
		var l_limit = int(levy.get("force_limit", 0))
		var l_room = int(levy.get("headroom", 0))
		var l_over = int(levy.get("over_by", 0))
		bbcode += "  Establishment: " + _format_number(l_army) + " / " + _format_number(l_limit)
		if l_over > 0:
			bbcode += "  [color=#" + Utils.COLOR_WARNING + "](" + _format_number(l_over) + " over the ordinance)[/color]\n"
		else:
			bbcode += "  [color=#" + Utils.COLOR_SUCCESS + "](" + _format_number(l_room) + " under)[/color]\n"
		# IQ-2 (Sept 14, 2026): when the levy is shut for a reason the
		# headroom arithmetic cannot show (no capital to raise men at, no
		# corps in reach of the depot), the backend names it — rendered in
		# place of the depots-open line. Absent/"" = the pre-IQ-2 block.
		var closed_reason = levy.get("closed_reason", "")
		if closed_reason is String and closed_reason != "":
			bbcode += "  [color=#" + Utils.COLOR_WARNING + "]" + closed_reason + "[/color]\n"
		elif bool(levy.get("open", false)):
			bbcode += "  [color=#" + Utils.COLOR_SUCCESS + "]The depots are open: " \
				+ _format_number(int(levy.get("infantry_amount", 0))) + " foot for " \
				+ str(int(levy.get("infantry_price", 0))) + "g" \
				+ "  (pool " + _format_number(int(levy.get("infantry_pool", 0))) + ")[/color]\n"
		bbcode += "\n"

	# Net: bold and last of the books, its own one-row table on the same column
	# weights (the gold figure lines up under the blocks above).
	# EA-13 (the economy audit, Oct 5 2026): which lines moved since
	# yesterday's accounts, and why — the backend's sentence, verbatim.
	var net_color = Utils.COLOR_SUCCESS if net >= 0 else Utils.COLOR_ERROR
	var net_note := str(econ.get("net_moves_note", ""))
	var net_label := "Net"
	if Utils.explanations_folded() and net_note.length() > 44:
		net_label = Utils.bb_hint(net_label, net_note)
		net_note = ""
	bbcode += "[table=3][cell expand=%d bg=#%s padding=6,4,6,4][b][color=#%s]%s[/color][/b][/cell]" % [ECON_COLS[0], Utils.TABLE_HEAD_BG, Utils.COLOR_GOLD, net_label]
	bbcode += "[cell expand=%d bg=#%s padding=6,4,6,4][right][opentype_features=tnum,lnum][b][color=#%s]%s[/color][/b][/opentype_features][/right][/cell]" % [ECON_COLS[1], Utils.TABLE_HEAD_BG, net_color, _econ_signed(net)]
	bbcode += "[cell expand=%d bg=#%s padding=6,4,6,4][color=#%s]%s[/color][/cell][/table]\n" % [ECON_COLS[2], Utils.TABLE_HEAD_BG, Utils.COLOR_INFO, net_note]

	# IQ-1 SW-0 "The Chest Speaks". `Spent` is informational and sits BELOW
	# Net on purpose: money already gone this turn (the projection above
	# does not and must not count it twice). `Ceiling` — a destination, not
	# a flow — leads the books since UXR3-41 (`_ceiling_line`).
	var spent = int(econ.get("spent", 0))
	if spent > 0:
		bbcode += "  [color=#" + Utils.COLOR_INFO + "]Spent:    -" + str(spent) + "g  (orders paid for this turn)[/color]\n"
	if bankruptcy > 0:
		bbcode += "  [color=#" + Utils.COLOR_ERROR + "]BANKRUPT — " + Utils.plural(int(bankruptcy), "turn") + "[/color]\n"

	# Active settlement payment streams (incoming tribute / outgoing
	# obligations), with turns remaining.
	var streams = econ.get("settlement_streams", [])
	if streams is Array and streams.size() > 0:
		bbcode += "\n" + Utils.bb_section("Settlement Payments")
		for stream in streams:
			if not (stream is Dictionary):
				continue
			var line = str(stream.get("display", ""))
			if line == "":
				continue
			var s_color = Utils.COLOR_SUCCESS if str(stream.get("direction", "")) == "incoming" else Utils.COLOR_ERROR
			bbcode += "  [color=#" + s_color + "]" + Utils.humanize_nation_keys_in_text(line) + "[/color]\n"

	# Income breakdown
	var breakdown = econ.get("income_breakdown", [])
	if breakdown.size() > 0:
		bbcode += "\n" + Utils.bb_section("Income by Region")
		var region_rows: Array = []
		for entry in breakdown:
			region_rows.append(["[color=#" + Utils.COLOR_GOLD + "]" + str(entry.get("region", "?")) + "[/color]",
				"[color=#" + Utils.COLOR_INFO + "]" + str(entry.get("type", "town")).replace("_", " ") + "[/color]",
				str(int(entry.get("income", 0))) + "g"])
		bbcode += Utils.bb_table(["Province", "Kind", "Income"], region_rows, [2], [4, 3, 2], _table_px()) + "\n"

	# Construction
	var queue = econ.get("construction_queue", [])
	if queue.size() > 0:
		bbcode += "\n" + Utils.bb_section("Under Construction")
		var works_rows: Array = []
		for item in queue:
			works_rows.append(["[color=#" + Utils.COLOR_GOLD + "]" + str(item.get("region", "?")) + "[/color]",
				str(item.get("building", "?")), str(int(item.get("turns_remaining", 0))) + " turns"])
		bbcode += Utils.bb_table(["Province", "Building", "Left"], works_rows, [2], [4, 4, 2], _table_px()) + "\n"

	# NV-12 "The Clear Deck": THE ADMIRALTY is a first-class book now
	# (tab 7, key 7) — it used to render at the BOTTOM of this tab, behind
	# treasury/income/trade/infrastructure, with no way in but scrolling.
	# The economy page keeps its signed naval lines and points across.
	var adm_ptr = cached_data.get("admiralty", {})
	if adm_ptr is Dictionary and adm_ptr.get("active", false):
		bbcode += "\n[color=#" + Utils.COLOR_INFO + "]→ THE ADMIRALTY has its own book — press 7 (Alt+7 while you type).[/color]\n"

	# Session UI-4: the page no longer rides `Utils.bb_tabulate` — the gold figures
	# stand in the tables' own right-aligned column.
	content_area.text = Utils.dress_heads(bbcode)


func _render_admiralty_tab():
	# NV-12: the naval theatre's own book.
	var bbcode = "[color=#" + Utils.COLOR_HEADER + "]═══ THE ADMIRALTY ═══[/color]" + Utils.lead_mark("The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type).", "sl.admiralty.lead") + "\n"
	bbcode += _dated_line()
	# R159 (POSITION 7): each core screen names the mechanic it displays.
	bbcode += Utils.bb_lead("[color=#" + Utils.COLOR_INFO + "]The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type).[/color]\n", "sl.admiralty.lead")
	var adm = cached_data.get("admiralty", {})
	if not (adm is Dictionary) or not adm.get("active", false):
		bbcode += "\n[color=#" + Utils.COLOR_INFO + "]This campaign has no naval theatre.[/color]\n"
		content_area.text = Utils.dress_heads(bbcode)
		return
	bbcode += _render_admiralty_block(adm)
	content_area.text = Utils.dress_heads(bbcode)


func _render_admiralty_block(adm: Dictionary) -> String:
	# DEF-5 naval (NAVAL_SPEC §9): THE ADMIRALTY — own fleet, the Blockade
	# board (both directions), CS closure, the Crossings verdict lines and
	# the honest gate terms. Backend-derived, shown = applied.
	var bbcode = ""
	var fleet = adm.get("own_fleet")
	if fleet is Dictionary:
		# S14d (docs/TABLE_LESSON_SPEC.md §2 line 6): the camp's first-open line at
		# the top of the fleet block, BEFORE the warning that names staging (S14D-X25).
		bbcode += _first_open_bbcode(adm, "admiralty_camp")
		var posture = str(fleet.get("posture", "guard"))
		var posture_line = "blockade — every enemy port watched" if posture == "blockade" else "guard — home waters covered"
		# DDB-61 (Pre-Deploy S13b part 4): the backend's ONE phrase, honest
		# about a blockade on her ("ordered to blockade stations — Britain
		# still pins her in port"); the old line is the fallback.
		var phrase = str(fleet.get("posture_phrase", ""))
		if phrase != "":
			posture_line = phrase
		bbcode += "  " + Utils.bb_glyph("fleet", 18, Utils.COLOR_GOLD) + " Fleet: " + str(int(fleet.get("ships", 0))) + " sail of the line — readiness " + str(int(fleet.get("readiness", 0)))
		var admiral = str(fleet.get("admiral", ""))
		if admiral != "":
			bbcode += "  (Adm. " + admiral + ")"
		# Session UI-2: the readiness on a meter and the posture as a badge — the
		# fleet's header row; its words are unchanged.
		bbcode += "  " + Utils.bb_meter(int(fleet.get("readiness", 0)), 100, 120, 8) + "  " \
			+ Utils.bb_badge("BLOCKADE" if posture == "blockade" else "GUARD", Utils.cv_hex("8b2a2a") if posture == "blockade" else "3a4a6b")
		bbcode += "\n  Posture: " + posture_line + "\n"
		# DDB-61: what stops the rot, when she rots.
		var rot = str(fleet.get("rot_line", ""))
		if rot != "":
			bbcode += "  [color=#" + Utils.COLOR_WARNING + "]" + rot + "[/color]\n"
		# RE-H (docs/RECURRING_EVENTS_SPEC.md §6.5): a squadron at sea — its
		# destination and its expected return from the fleet record alone.
		var squadron = str(fleet.get("squadron_line", ""))
		if squadron != "":
			bbcode += "  [color=#" + Utils.COLOR_WARNING + "]" + squadron + "[/color]\n"
		var yards = fleet.get("yards", [])
		if yards is Array and yards.size() > 0:
			var laid = int(fleet.get("laid_this_turn", 0))
			var rate = int(fleet.get("build_rate", 2))
			bbcode += "  Yards: " + ", ".join(PackedStringArray(yards)) + "  (" + str(laid) + "/" + str(rate) + " keels this turn)\n"
		var window = int(fleet.get("window_turns", 0))
		if window > 0:
			bbcode += "  [color=#" + Utils.COLOR_SUCCESS + "]THE STRAIT LIES OPEN — " + Utils.plural(int(window), "turn") + (" remains" if int(window) == 1 else " remain") + "[/color]\n"
		# DDB-59 (Pre-Deploy S13b part 4): the camp is a state the turn's
		# end counts — the backend's line says the count and why, no order.
		# S14D-X26 (October 23, 2026): the two client fallbacks that stood
		# here were dead — `camp_line` is non-empty whenever camp provinces
		# exist and `camp_strength` is 0 when none do — and their pin passed
		# on dead source; the ONE line is the backend's (`naval.py`).
		var camp_line = str(fleet.get("camp_line", ""))
		if camp_line != "":
			bbcode += "  The Camp: " + camp_line + "\n"
	else:
		bbcode += "  We keep no fleet in commission.\n"
	# NUI-2 (Sept 24, 2026): the ORDERS come first, under the fleet line.
	# They rendered at the bottom of the tab, below the Blockade board, the
	# Crossings and both sets of gate terms — so a player who opened THE
	# ADMIRALTY to act had to scroll past the whole report to find a button.
	var orders := _render_admiralty_orders(adm)
	if orders != "":
		bbcode += orders + "\n"
	var cs = adm.get("continental_system")
	if cs is Dictionary:
		var tier = int(cs.get("tier", 0))
		# VP1-X5 (S14b part 2): the closure in ports of the Continent — the
		# Congress, the designs and the counsel all speak in ports of 26.
		var cs_line = "  The Continental System: " + str(int(cs.get("ports_closed", 0))) + " of " + str(int(cs.get("ports_total", 0))) + " of the Continent's ports closed (" + str(int(cs.get("closure_pct", 0))) + "%)"
		if tier > 0:
			cs_line += " — " + Utils.humanize_nation_keys_in_text(str(cs.get("target", ""))) + "'s war-weariness rising +" + str(tier) + "/turn"
		else:
			# NV-5: below the lowest notch the percentage is true and inert.
			# Say so, and say what closes the next one.
			cs_line += " — [color=#" + Utils.COLOR_INFO + "]not yet biting[/color]"
		bbcode += cs_line + "\n"
		# DDB-58 (Pre-Deploy S13b part 4): how a port closes, in one
		# sentence, and the courts still open, with their ports.
		var rule_line = str(cs.get("rule_line", ""))
		if rule_line != "":
			bbcode += "  [color=#" + Utils.COLOR_INFO + "]" + rule_line + "[/color]\n"
		var open_line = str(cs.get("open_line", ""))
		if open_line != "":
			bbcode += "  " + open_line + ".\n"
		# The Tilsit clause (Score Finish Step 7 slice 4): the courts that
		# keep the System as members, named with their ports.
		var members_line = str(cs.get("members_line", ""))
		if members_line != "":
			bbcode += "  " + members_line + ".\n"
		# SR-5r RF-4b (T8): the clients counted by the decree alone, named.
		var decree_line = str(cs.get("decree_line", ""))
		if decree_line != "":
			bbcode += "  [color=#" + Utils.COLOR_SUCCESS + "]" + decree_line + ".[/color]\n"
		var next_pct = cs.get("next_tier_pct")
		if next_pct != null:
			bbcode += "  [color=#" + Utils.COLOR_INFO + "]Next notch at " + str(int(next_pct)) + "% — " + Utils.plural(int(cs.get("ports_to_next_tier", 0)), "more port") + " closed to them.[/color]\n"
		# SR5B-D1 (ruled Sept 28, 2026): the System's endgame use — the
		# Congress's SHUT OUT reading — and which of her corps keeps the
		# Continent open today, named where it stands (the backend's ONE
		# sentence, `congress.admiralty_shut_out_line`; fog-honest there).
		var shut_out_line = str(cs.get("shut_out_line", ""))
		if shut_out_line != "":
			bbcode += "  [color=#" + Utils.COLOR_INFO + "]" + shut_out_line + "[/color]\n"
	var board = adm.get("blockade_board", [])
	if board is Array and board.size() > 0:
		bbcode += "\n" + Utils.HEAD_OPEN + "The Blockade Board" + Utils.HEAD_CLOSE + "\n"
		for row in board:
			if not (row is Dictionary):
				continue
			var row_nation = Utils.humanize_nation_keys_in_text(str(row.get("nation", "?")))
			var row_blockader = Utils.humanize_nation_keys_in_text(str(row.get("blockader", "?")))
			var row_color = Utils.COLOR_ERROR if row.get("against_us", false) else (Utils.COLOR_SUCCESS if row.get("ours", false) else Utils.COLOR_TEXT)
			bbcode += "  [color=#" + row_color + "]" + row_nation + " — blockaded by " + row_blockader + ": " + str(row.get("effects", "")) + "[/color]\n"
	var crossings = adm.get("crossings", [])
	if crossings is Array and crossings.size() > 0:
		bbcode += "\n" + Utils.HEAD_OPEN + "The Crossings" + Utils.HEAD_CLOSE + "\n"
		for cx in crossings:
			if not (cx is Dictionary):
				continue
			var verdict = str(cx.get("verdict", "open"))
			var cx_color = Utils.COLOR_TEXT
			if verdict == "shut":
				cx_color = Utils.COLOR_ERROR
			elif verdict == "landing":
				# NV-4: the water is ours, the shore is not — amber, matching
				# the map's own tint for the same link.
				cx_color = Utils.COLOR_ORANGE
			elif verdict == "window":
				cx_color = Utils.COLOR_SUCCESS
			bbcode += "  [color=#" + cx_color + "]" + Utils.humanize_nation_keys_in_text(str(cx.get("line", ""))) + "[/color]\n"
		# NV-12: the legend + remedy line (the remedy copy used to fire ONLY
		# on an attempted march; the map has no legend at all).
		var legend = str(adm.get("crossings_legend", ""))
		if legend != "":
			bbcode += "  [color=#" + Utils.COLOR_INFO + "]" + legend + "[/color]\n"
	var div_terms = adm.get("diversion_terms", [])
	if div_terms is Array and div_terms.size() > 0:
		bbcode += "\n" + Utils.HEAD_OPEN + "The Grand Diversion" + Utils.HEAD_CLOSE + "  (the button below)\n"
		for term in div_terms:
			if not (term is Dictionary):
				continue
			var met = bool(term.get("met", false))
			var mark = "[color=#" + Utils.COLOR_SUCCESS + "]+[/color]" if met else "[color=#" + Utils.COLOR_ERROR + "]x[/color]"
			bbcode += "  " + mark + " " + str(term.get("text", "")) + "\n"
			# S14E-14: the throw's price in ships (a failed diversion fights a
			# fleet action) rides the term it belongs to, in the info register.
			var div_detail = str(term.get("detail", ""))
			if div_detail != "":
				bbcode += "      [color=#" + Utils.COLOR_INFO + "]" + div_detail + "[/color]\n"
	# NV-12 (recon gap 2): the Expedition's gate terms were BUILT at NV-6 and
	# read by no surface — the Diversion rendered its terms while the
	# Expedition's were dropped, and the 15,000 cap appeared in no client
	# copy at all. Rendered the same way, with per-term detail.
	var exp_terms = adm.get("expedition_terms", [])
	if exp_terms is Array and exp_terms.size() > 0:
		bbcode += "\n" + Utils.HEAD_OPEN + "The Expedition" + Utils.HEAD_CLOSE + "  (a landing chip below, or click a coastal province)\n"
		for term in exp_terms:
			if not (term is Dictionary):
				continue
			var met = bool(term.get("met", false))
			var mark = "[color=#" + Utils.COLOR_SUCCESS + "]+[/color]" if met else "[color=#" + Utils.COLOR_ERROR + "]x[/color]"
			bbcode += "  " + mark + " " + str(term.get("text", ""))
			var detail = str(term.get("detail", ""))
			if detail != "":
				bbcode += "  [color=#" + Utils.COLOR_INFO + "]" + detail + "[/color]"
			bbcode += "\n"
		var notes = adm.get("expedition_notes", [])
		if notes is Array:
			for note in notes:
				bbcode += "  [color=#" + Utils.COLOR_INFO + "]· " + str(note) + "[/color]\n"
	return bbcode


func _render_admiralty_orders(adm: Dictionary) -> String:
	"""NV-6 — the Admiralty's orders as clickable chips. Every naval verb
	but `build_fleet` used to be typed-command only. Each chip carries the
	same typed command a player would write, and its enabled state comes
	from the backend gate (honest availability, the section 11.6 idiom): a
	shown chip works, a withheld one states why in present tense.

	NUI-2 (Sept 24, 2026): the expedition's ROAD rides here too —
	`expedition_chips`, the next step toward a sailing (land a ready corps,
	march a small one to a yard, or commission a marshal), each the typed
	command the terminal takes. The naval orders carry no marshal's voice to
	prompt the words, so the words are the buttons."""
	var chips = adm.get("chips", [])
	var ready = adm.get("embark_ready", [])
	if not (chips is Array) or chips.is_empty():
		return ""
	var bbcode = "\n" + Utils.HEAD_OPEN + "Orders to the Admiralty" + Utils.HEAD_CLOSE + "\n"
	for chip in chips:
		bbcode += _chip_row(chip)
	var road = adm.get("expedition_chips", [])
	var has_road: bool = road is Array and road.size() > 0
	if has_road:
		# A blank line first: a chip's pill padding overlaps the line above
		# it (the house style — see the region panel's ACTIONS), and the
		# sub-header must not sit under the last order's pill.
		bbcode += "\n  [color=#" + Utils.COLOR_INFO + "]The expedition — the next step:[/color]\n"
		for chip in road:
			bbcode += _chip_row(chip)
	if ready is Array and ready.size() > 0:
		# The expedition's chip lives on the map, where its destination is
		# actually chosen — say so rather than offering a verb with no object.
		var names: Array = []
		for corps in ready:
			if corps is Dictionary:
				# S14G-17 (Pre-Deploy S14h part 2, October 26, 2026): and WHY he
				# may embark where he stands ("an allied shore") - the rule in
				# words (`naval.embark_reason`), the line the ready list lacked.
				var why = str(corps.get("reason", ""))
				names.append(str(corps.get("marshal", "")) + " ("
					+ Utils.format_number(int(corps.get("strength", 0))) + " at "
					+ str(corps.get("location", ""))
					+ (" — " + why if why != "" else "") + ")")
		var where := " — click a coastal province to choose the landing."
		if has_road:
			where = " — or click any coastal province for another landing."
		bbcode += "  [color=#" + Utils.COLOR_INFO + "]Ready to embark: " \
			+ ", ".join(names) + where + "[/color]\n"
	return bbcode


func _chip_row(chip) -> String:
	# One chip row, both families: enabled = the gold pill + its note,
	# disabled = the dimmed pill + the gate's own reason (NV-12 recon gap 13:
	# disabled chips were grey TEXT, reading as a different control family
	# than the region panel's disabled pills). Every book on this screen
	# renders its chips here — THE ADMIRALTY's orders and THE LAWS' (RF-4a).
	if not (chip is Dictionary):
		return ""
	var label = str(chip.get("label", ""))
	# S14G-29 (Pre-Deploy S14h part 2, October 26, 2026): the verb's price at the
	# point of choice - "(2 AP)" / "(1 Admin AP)" / "(2 AP · 4 turns)", stamped by
	# the backend from the world's own action table (`naval.ap_cost_note`), rides
	# beside the label of an enabled AND a withheld chip. A chip with no
	# `cost_note` (THE LAWS' rows) renders exactly as before.
	var cost_note = str(chip.get("cost_note", ""))
	var row := "  "
	if bool(chip.get("enabled", false)):
		row += Utils.bb_button_chip("do:" + str(chip.get("command", "")),
			label, Utils.COLOR_GOLD, _NAVAL_CHIP_BG)
		var note = str(chip.get("note", ""))
		var tail = cost_note
		if note != "":
			tail += (" · " if tail != "" else "") + note
		if tail != "":
			row += "  [color=#" + Utils.COLOR_INFO + "]" + tail + "[/color]"
	else:
		var why = str(chip.get("reason", "not available"))
		row += Utils.bb_chip_disabled(label) + "  [color=#" + Utils.COLOR_INFO + "]" \
			+ (cost_note + " · " if cost_note != "" else "") + why + "[/color]"
	return row + "\n"


func _render_laws_tab():
	"""SR-5r RF-4a — THE LAWS (REFORMS_SPEC §8, §8a): one row per law in the
	player's deck, in deck order — what it does (in numbers), what it costs,
	its status — and ONE chip whose enabled state IS the verb's predicate
	(the backend stamps it from `law_refusal` / `repeal_refusal`; a withheld
	chip states that predicate's own words). A chip sends the typed order down
	the ledger's one chip road; an enactment is quoted first on the
	clarification channel (the Council of State's confirm) and enacted there."""
	var laws = cached_data.get("laws", {})
	var bbcode = "[color=#" + Utils.COLOR_HEADER + "][b]THE LAWS OF STATE[/b][/color]" + Utils.lead_mark("The laws of the Empire — what each does, its price, its upkeep, and whether we may enact it now. Keys 1–8 turn the ledger's books (Alt+1–8 while you type).", "sl.laws.lead") + "\n"
	bbcode += _dated_line()
	# R159 (S14D-X2, October 23, 2026): the eighth book names the mechanic it
	# displays, as every other book does.
	bbcode += Utils.bb_lead("[color=#" + Utils.COLOR_INFO + "]The laws of the Empire — what each does, its price, its upkeep, and whether we may enact it now. Keys 1–8 turn the ledger's books (Alt+1–8 while you type).[/color]\n", "sl.laws.lead")
	# S14d (docs/TABLE_LESSON_SPEC.md §2 line 5): the book's first-open line.
	bbcode += _first_open_bbcode(laws, "laws")
	if not (laws is Dictionary) or laws.is_empty():
		bbcode += "[color=#" + Utils.COLOR_INFO + "]This campaign has no laws of state.[/color]\n"
		content_area.text = Utils.dress_heads(bbcode)
		return
	# RF-4b / RF-4c (REFORMS_SPEC §8 "The forecast"): the lapse the ledger's
	# own projection foresees for this turn's end LEADS the book, with its
	# lever — the RF-4c frame showed it below the fold, after five laws, and
	# it is the one line that must never surprise the player.
	var forecast = laws.get("forecast", null)
	if forecast is Dictionary and not forecast.is_empty():
		bbcode += "\n[color=#" + Utils.COLOR_WARNING + "][b]FORECAST[/b] " + str(forecast.get("line", "")) + "[/color]\n"
		var rescue = forecast.get("repeal_instead", null)
		if rescue is Dictionary and not rescue.is_empty():
			bbcode += "\n" + _chip_row(rescue)
	for row in laws.get("rows", []):
		if not (row is Dictionary):
			continue
		# Session UI-2: a law a card — its header row names it, dates it and
		# badges its standing; the figures and the chip stand under it.
		var row_status = str(row.get("status", ""))
		bbcode += "\n" + Utils.card_open() + Utils.bb_glyph("cabinet", 18, Utils.COLOR_GOLD) + " [color=#" + Utils.COLOR_GOLD + "][b]" + str(row.get("name", "")) + "[/b][/color]"
		match row_status:
			"in_force":
				bbcode += "  " + Utils.bb_badge("IN FORCE", Utils.cv_hex("2f6b3a"))
			"lapsed":
				bbcode += "  " + Utils.bb_badge("LAPSED", "8a6d2a")
			"refused":
				bbcode += "  " + Utils.bb_badge("REFUSED", Utils.COLOR_BADGE_QUIET)
		var date = str(row.get("date", ""))
		if date != "":
			bbcode += "  [color=#" + Utils.COLOR_INFO + "]" + date + "[/color]"
		bbcode += "\n"
		var says = str(row.get("says", ""))
		if says != "":
			bbcode += "  " + says + "\n"
		for line in row.get("effects", []):
			bbcode += "  [color=#" + Utils.COLOR_INFO + "]• " + str(line) + "[/color]\n"
		# SR-7d DC-3a (DOCTRINES_SPEC §4): a cure law says what it cures, what it
		# would lift THIS turn, and the Staff it needs (`laws[].cure_line`).
		var cure_line = str(row.get("cure_line", ""))
		if cure_line != "" and cure_line != "<null>":
			bbcode += "  [color=#" + Utils.COLOR_WARNING + "]• " + cure_line + "[/color]\n"
		# S14D-X27: a lapsed row prices its restoration (the backend's Arrears
		# figure, the one the chip's note quotes), an unlapsed one its enactment.
		bbcode += "  [color=#" + Utils.COLOR_INFO + "]" + str(row.get("price_words", "")) \
			+ (" to restore · " if str(row.get("status", "")) == "lapsed" else " to enact · ") \
			+ Utils.format_number(int(row.get("upkeep", 0))) + " gold a turn[/color]\n"
		# A refused row's reason is the chip's own — said once, beside the chip.
		var status = str(row.get("status", ""))
		if status != "refused":
			var status_color = Utils.COLOR_INFO
			if status == "in_force":
				status_color = Utils.COLOR_SUCCESS
			elif status == "lapsed":
				status_color = Utils.COLOR_WARNING
			bbcode += "  [color=#" + status_color + "]" + str(row.get("status_line", "")) + "[/color]\n"
		# A blank line first: a chip's pill padding overlaps the line above it.
		bbcode += "\n" + _chip_row(row.get("chip", {})) + Utils.CARD_CLOSE
	# RE-6 (RECURRING_EVENTS_SPEC.md §16 "RE-6", §25; SYSTEMS_REFERENCE §167): THE
	# EDICTS — the decrees in force (`laws.edicts`, present only where the
	# recurring deck is armed): what each does, in the laws' own words, and the
	# morning its term ends. No chip: a decree is bought by letter, never typed.
	var edicts = laws.get("edicts", null)
	if edicts is Array:
		bbcode += "\n" + Utils.bb_glyph("letter", 18, Utils.COLOR_GOLD) + " [color=#" + Utils.COLOR_HEADER + "][b]THE EDICTS[/b][/color]\n"
		if edicts.is_empty():
			bbcode += "  [color=#" + Utils.COLOR_INFO + "]No edict is in force.[/color]\n"
		for edict in edicts:
			if not (edict is Dictionary):
				continue
			bbcode += "  [color=#" + Utils.COLOR_GOLD + "][b]" + str(edict.get("spoken", edict.get("name", ""))) + "[/b][/color]"
			bbcode += "  [color=#" + Utils.COLOR_SUCCESS + "]" + str(edict.get("status_line", "")) + "[/color]\n"
			for line in edict.get("effects", []):
				bbcode += "    [color=#" + Utils.COLOR_INFO + "]• " + str(line) + "[/color]\n"
	bbcode += "\n[color=#" + Utils.COLOR_HEADER + "]" + str(laws.get("footer", "")) + "[/color]\n"
	content_area.text = Utils.dress_heads(bbcode)


func _render_intel():
	var intel_data = cached_data.get("intel", {})
	var bbcode = ""
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]═══ INTELLIGENCE ═══[/color]" + Utils.lead_mark("What the fog concedes — enemy armies as your scouts and towers last saw them, aging as reports go stale.", "sl.intel.lead") + "\n"
	bbcode += _dated_line()
	bbcode += Utils.bb_lead("[color=#" + Utils.COLOR_INFO + "]What the fog concedes — enemy armies as your scouts and towers last saw them, aging as reports go stale.[/color]\n\n", "sl.intel.lead")

	var enemies = intel_data.get("known_enemies", [])
	var unknown_count = int(intel_data.get("unknown_region_count", 0))

	if enemies.size() == 0:
		bbcode += "[color=#" + Utils.COLOR_INFO + "]No enemy forces in observation range.[/color]\n"
	else:
		bbcode += Utils.card_open()    # Session UI: the sighted forces, one card
		bbcode += Utils.bb_glyph("intel", 18, Utils.COLOR_GOLD) + " [color=#" + Utils.COLOR_HEADER + "]Known Enemy Forces[/color]\n"
		var sighted: Array = []
		for e in enemies:
			var ename = str(e.get("name", "?"))
			var enation = str(e.get("nation", "?"))
			var eloc = str(e.get("location", "?"))
			var estr = str(e.get("strength_display", "?"))
			var evis = str(e.get("visibility", "unknown"))

			# Session UI-2: the reading as a badge in its tone (the brackets were a raw tag).
			var vis_tone = Utils.COLOR_BADGE_QUIET
			var vis_label = ""
			match evis:
				"full":
					vis_tone = Utils.cv_hex("2f6b3a")
					vis_label = "confirmed"
				"partial":
					vis_tone = "3a4a6b"
					vis_label = "partial"
				"stale":
					vis_tone = "8a6d2a"
					vis_label = "stale"
				"last_known":
					vis_tone = Utils.cv_hex("8b2a2a")
					vis_label = "last known"

			sighted.append(["[color=#" + Utils.COLOR_GOLD + "]" + ename + "[/color] ",
				Utils.bb_flag(enation) + " " + Utils.display_nation_name(enation) + " ",
				"at " + eloc + " ", estr + " ",
				Utils.bb_tag(vis_label, vis_tone)])
		bbcode += Utils.bb_table(["Marshal", "Nation", "Where", "Strength", "Reading"], sighted, [3], [3, 3, 3, 2, 2], _table_px()) + "\n"
		bbcode += Utils.CARD_CLOSE

	# Nation summaries
	var summaries = intel_data.get("nation_summaries", [])
	if summaries.size() > 0:
		bbcode += "\n" + Utils.card_open() + Utils.bb_glyph("europe", 18, Utils.COLOR_GOLD) + " [color=#" + Utils.COLOR_HEADER + "]Nation Summary[/color]\n"
		var summary_rows: Array = []
		for s in summaries:
			var sname = str(s.get("nation", "?"))
			var smarshals = int(s.get("known_marshals", 0))
			var sstrength = int(s.get("estimated_strength", 0))
			var sregions = int(s.get("regions_controlled", 0))
			# S14E-5: the count agrees with its noun ("1 province", never "1 regions").
			summary_rows.append([Utils.bb_flag(sname) + " " + Utils.display_nation_name(sname) + " ",
				str(smarshals) + " marshals spotted ", "~" + _format_number(sstrength) + " est. strength ",
				Utils.plural(sregions, "province")])
		bbcode += Utils.bb_table(["Nation", "Marshals", "Strength", "Provinces"], summary_rows, [2, 3], [3, 3, 3, 2], _table_px()) + "\n"
		bbcode += Utils.CARD_CLOSE

	if unknown_count > 0:
		bbcode += "\n[color=#" + Utils.COLOR_INFO + "]" + Utils.plural(int(unknown_count), "region") + " with no intel.[/color]\n"

	# AI-0b: the campaign seed, shown and shareable (top-level ledger key).
	# Review fix [4]: the seed is a raw user-supplied string (SOVEREIGN_SEED
	# env / pasted shares) — strip bbcode brackets before rendering.
	var campaign_seed = str(cached_data.get("campaign_seed", "historical"))
	campaign_seed = campaign_seed.replace("[", "").replace("]", "")
	bbcode += "\n[color=#" + Utils.COLOR_INFO + "]Campaign seed: " + campaign_seed + "[/color]\n"

	content_area.text = Utils.dress_heads(bbcode)


func _render_manpower():
	var mp = cached_data.get("manpower", {})
	var bbcode = ""
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]═══ MANPOWER ═══[/color]" + Utils.lead_mark("The levy pools your recruits draw on — spent men return with time, not gold.", "sl.manpower.lead") + "\n"
	bbcode += _dated_line()
	bbcode += Utils.bb_lead("[color=#" + Utils.COLOR_INFO + "]The levy pools your recruits draw on — spent men return with time, not gold.[/color]\n\n", "sl.manpower.lead")

	# Session UI-2: the cost note is the same sentence for every arm of a levy —
	# it is said ONCE under the pools; a pool whose note differs keeps its own.
	bbcode += _manpower_figure_card(mp)
	var shared_note := ""
	var notes_agree := true
	for pool_type in ["infantry", "cavalry", "artillery"]:
		var probe_note = str(mp.get(pool_type, {}).get("cost_note", ""))
		if shared_note == "":
			shared_note = probe_note
		elif probe_note != shared_note:
			notes_agree = false
	if not notes_agree:
		shared_note = ""
	for pool_type in ["infantry", "cavalry", "artillery"]:
		var pool = mp.get(pool_type, {})
		var current = int(pool.get("current", 0))
		var max_val = int(pool.get("max", 0))
		var regen = int(pool.get("regen_rate", 0))
		var recruit_amt = int(pool.get("recruit_amount", 0))
		# Aug 2026 health-check audit: render the LIVE executor-priced figure
		# (war ×3, stability bands, force limit, marshal) — the base price
		# understated the real charge by up to 2.25× at the wartime boot.
		var recruit_cost = int(pool.get("recruit_price", int(pool.get("recruit_base_cost", 0))))
		var cost_note = str(pool.get("cost_note", ""))
		var turns_full = int(pool.get("turns_until_full", 0))

		bbcode += Utils.card_open()    # Session UI: an arm a card
		var arm_glyph := "foot"
		if pool_type == "cavalry":
			arm_glyph = "horse"
		elif pool_type == "artillery":
			arm_glyph = "guns"
		bbcode += Utils.bb_glyph(arm_glyph, 18, Utils.COLOR_GOLD) + " [color=#" + Utils.COLOR_GOLD + "]" + pool_type.to_upper() + "[/color]\n"

		# Pool bar with color coding
		var pool_color = Utils.COLOR_INFO
		var pool_fill = Utils.COLOR_GOLD
		if current == 0:
			pool_color = Utils.COLOR_ERROR
			pool_fill = Utils.COLOR_ERROR
		elif current < recruit_amt:
			pool_color = Utils.COLOR_ORANGE
			pool_fill = Utils.COLOR_ORANGE

		bbcode += "  Pool: [color=#" + pool_color + "]" + _format_number(current) + "[/color]"
		bbcode += " / " + _format_number(max_val) + "   " + Utils.bb_meter(current, maxi(max_val, 1), 220, 9, pool_fill) + "\n"
		bbcode += "  Regen: +" + _format_number(regen) + "/turn"
		if turns_full == 0:
			bbcode += " (full)\n"
		elif turns_full == -1:
			bbcode += " (no regen)\n"
		else:
			bbcode += " (" + str(turns_full) + " turns to full)\n"
		# SR-5r RF-4b (T8): the laws inside these figures, named — the rate
		# above and the price below are the APPLIED ones (RF-2's one source).
		for term in pool.get("regen_terms", []):
			if term is Array and term.size() >= 2:
				bbcode += "    [color=#" + Utils.COLOR_SUCCESS + "]includes +" + str(int(term[1])) + "% regen — " + str(term[0]) + "[/color]\n"
		for term in pool.get("price_terms", []):
			if term is Array and term.size() >= 2:
				bbcode += "    [color=#" + Utils.COLOR_SUCCESS + "]the draft price includes ×" + str(snappedf(float(term[1]), 0.01)) + " — " + str(term[0]) + "[/color]\n"

		# IQ-2: when the capital's depot is shut (enemy-held, or in unrest)
		# the executor refuses the DEFAULT (capital) recruit, so the capital
		# price is not quoted; the backend's cost_note names why, and names
		# the marshal's field levy while one is possible. Absent key = the
		# old line.
		var depot_closed = pool.get("depot_closed", false)
		if typeof(depot_closed) == TYPE_BOOL and depot_closed and cost_note != "":
			bbcode += "  Recruit: " + _format_number(recruit_amt) + " troops — " + cost_note
		else:
			bbcode += "  Recruit: " + _format_number(recruit_amt) + " troops for " + str(recruit_cost) + "g"
			if cost_note != "" and shared_note == "":
				bbcode += " — " + cost_note
		bbcode += "\n" + Utils.CARD_CLOSE + "\n"

	if shared_note != "":
		bbcode += "[color=#" + Utils.COLOR_INFO + "]Every arm's levy: " + shared_note + "[/color]\n"

	content_area.text = Utils.dress_heads(bbcode)


func _manpower_figure_card(mp: Dictionary) -> String:
	"""Session UI-5: the Manpower book's foot — all three pools on one gauge
	against their caps, the regrowth a turn and the turns to refill, every
	figure from the pools' own payload ("—" where nothing regrows)."""
	var cur_sum := 0
	var max_sum := 0
	var regen_sum := 0
	var refill := 0
	var stuck := false
	var width := 200 if Utils.compact_view() else 320
	for pool_type in ["infantry", "cavalry", "artillery"]:
		var pool: Dictionary = mp.get(pool_type, {})
		var current: int = int(pool.get("current", 0))
		var cap: int = int(pool.get("max", 0))
		var regen: int = int(pool.get("regen_rate", 0))
		var turns: int = int(pool.get("turns_until_full", 0))
		cur_sum += current
		max_sum += cap
		regen_sum += regen
		if turns > 0:
			refill = maxi(refill, turns)
		elif turns < 0:
			stuck = true
	# Session UI-5 interim fix (Nov 13): no per-arm rows — the three arm cards say them.
	var out := Utils.card_open()
	out += Utils.bb_glyph("strength", 18, Utils.COLOR_GOLD) + " [color=#" + Utils.COLOR_GOLD + "]THE LEVY AT A GLANCE[/color]\n"
	out += "  " + Utils.bb_meter(cur_sum, maxi(max_sum, 1), width, 10) + "  " + _format_number(cur_sum) + " / " + _format_number(max_sum) + " men in the pools\n"
	var refill_text := "—"
	if cur_sum >= max_sum and max_sum > 0:
		refill_text = "full"
	elif regen_sum > 0 and not stuck:
		refill_text = str(refill) + " turns"
	elif regen_sum > 0:
		refill_text = "— (an arm does not regrow)"
	out += "  Regrowth: [color=#" + Utils.COLOR_GOLD + "]+" + _format_number(regen_sum) + "/turn[/color]   To refill: [color=#" + Utils.COLOR_GOLD + "]" + refill_text + "[/color]\n"
	out += Utils.CARD_CLOSE + "\n"
	return out


func _render_orders():
	var orders = cached_data.get("orders", [])
	var ap_remaining = int(cached_data.get("actions_remaining", 1))
	var can_cancel = ap_remaining > 0
	var bbcode = ""
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]═══ STANDING ORDERS ═══[/color]" + Utils.lead_mark("Orders that march without you — each executes itself at dawn until done, or cancelled here.", "sl.orders.lead") + "\n"
	bbcode += _dated_line()
	bbcode += Utils.bb_lead("[color=#" + Utils.COLOR_INFO + "]Orders that march without you — each executes itself at dawn until done, or cancelled here.[/color]\n\n", "sl.orders.lead")

	# IQ-4 S3b — THE CABINET: Talleyrand's mission, read from the ledger's
	# `cabinet` block (built from diplomatic_dialogue.mission_status — ONE
	# source; nothing here computes a figure of its own). Rendered BEFORE the
	# empty-roster return below — a France with no marshal row still has a
	# Cabinet — and never as a row in `orders`. An absent key (the backend
	# lever down) renders nothing, so the tab is unchanged.
	# [Recall] rides the existing `do:` arm → naval_command →
	# main._on_naval_command — the typed pipeline, with its in-flight latch,
	# echo and history, which bypasses the Cabinet redirect. The recall is
	# FREE (no DP, no action point), so it is never gated on `can_cancel`.
	bbcode += _cabinet_block(cached_data.get("cabinet"))

	if orders.size() == 0:
		bbcode += "[color=#" + Utils.COLOR_INFO + "]No marshals available.[/color]\n"
		content_area.text = Utils.dress_heads(bbcode)
		return

	if not can_cancel:
		bbcode += "[color=#" + Utils.COLOR_INFO + "]No actions remaining — cancel unavailable this turn.[/color]\n\n"

	var has_active = false
	var has_idle = false

	# Active orders first
	for o in orders:
		if not o.get("has_order", false):
			continue
		has_active = true
		var mname = str(o.get("marshal", "?"))
		var order_type = str(o.get("order_type", "?"))
		# NPC-12: the display form beside the machine key (a pre-slice
		# payload carries no `target_display` and falls back to the key).
		var target = str(o.get("target_display", o.get("target", "")))
		var location = str(o.get("location", "?"))
		var condition = str(o.get("condition", ""))
		var path_left = int(o.get("path_remaining", 0))

		# Session UI-2: an order a card — the marshal's header row with the order
		# as a badge, then its object, the road left and its condition.
		bbcode += Utils.card_open()
		bbcode += "  " + Utils.bb_glyph("march", 18, Utils.COLOR_GOLD) + " [color=#" + Utils.COLOR_GOLD + "]" + mname + "[/color]"
		bbcode += " at " + location + "  " + Utils.bb_badge(order_type.to_upper(), "3a4a6b") + "\n"

		bbcode += "    "
		if target != "" and target != "generic":
			bbcode += target

		if path_left > 0:
			bbcode += "  (" + Utils.plural(path_left, "region") + " left)"

		bbcode += "  │ " + condition

		if can_cancel:
			# UXR3-F5: a chip, as every other tab's action (a red bracketed
			# word read as a raw tag).
			bbcode += "  " + Utils.bb_button_chip("cancel:" + mname, "Cancel", Utils.COLOR_ERROR_CHIP, "233043")
		else:
			bbcode += "  " + Utils.bb_chip_disabled("Cancel")
		bbcode += "\n" + Utils.CARD_CLOSE + "\n"

	# Separator between active and idle
	if has_active:
		for o in orders:
			if not o.get("has_order", false):
				has_idle = true
				break
		if has_idle:
			bbcode += "[color=#" + Utils.COLOR_INFO + "]─────────────────────────────────────────────────────[/color]\n"

	# Idle marshals
	for o in orders:
		if o.get("has_order", false):
			continue
		var mname = str(o.get("marshal", "?"))
		var location = str(o.get("location", "?"))
		var decision = str(o.get("decision", ""))
		if decision != "":
			# FA-N36 review round: an order-FREE decision (last stand, muster
			# confirm) is not idle — the same word the FORCES tab uses.
			bbcode += "  " + Utils.bb_glyph("march", 16, Utils.COLOR_WARNING) + " [color=#" + Utils.COLOR_WARNING + "]" + mname + " at " + location
			bbcode += "  │ " + str(o.get("order_type", "AWAITING YOUR WORD")).to_upper()
			var quarry = str(o.get("target_display", o.get("target", "")))
			if quarry != "":
				bbcode += " — " + quarry
			bbcode += "[/color]\n"
			continue
		bbcode += "  " + Utils.bb_glyph("march", 16, Utils.COLOR_INFO) + " [color=#" + Utils.COLOR_INFO + "]" + mname
		bbcode += " at " + location
		bbcode += "  │ No active orders"
		bbcode += "[/color]\n"

	content_area.text = Utils.dress_heads(bbcode)


func _cabinet_block(cabinet) -> String:
	"""IQ-4 S3b — THE CABINET, Talleyrand's mission, read from the ledger's
	`cabinet` block (one source). The Orders tab renders it; UXR3-41 (Pre-
	Deploy S12 part 2) leads the Forces tab with it as well, where the
	mission boards are read. An absent key renders nothing."""
	var bbcode := ""
	if cabinet is Dictionary:
		bbcode += "[color=#" + Utils.COLOR_HEADER + "]═══ THE CABINET ═══[/color]\n"
		if not cabinet.get("live", false):
			bbcode += "  [color=#" + Utils.COLOR_INFO + "]Talleyrand is at the Cabinet. Press F1, choose a court, and send him on a mission.[/color]\n"
			var last = cabinet.get("last")
			if last is Dictionary and not last.is_empty():
				var last_phrase = _cabinet_str(last, "reason_phrase")
				if last_phrase == "":
					last_phrase = _cabinet_str(last, "reason")
				bbcode += "  [color=#" + Utils.COLOR_INFO + "]Last mission: " + _cabinet_str(last, "type_display") + " — " + _cabinet_str(last, "target_display") + ", " + last_phrase + ".[/color]\n"
		else:
			var paused = false
			if cabinet.get("paused", false):
				paused = true
			var target_display = _cabinet_str(cabinet, "target_display")
			var ally_display = _cabinet_str(cabinet, "target_ally_display")

			# Line 1 — who, what, and the turn's arithmetic (effect, drift, net).
			var head = "  Talleyrand → [color=#" + Utils.COLOR_GOLD + "]" + target_display + "[/color] │ "
			head += _cabinet_str(cabinet, "type_display").to_upper() + "  "
			if _cabinet_str(cabinet, "type") == "GATHER_INTEL":
				# No relation work — the effect text states what he is doing.
				head += _cabinet_str(cabinet, "effect_text")
			elif _cabinet_str(cabinet, "type") == "UNDERMINE_ALLIANCE":
				# IQ-4 review: other courts' friction and subsidies move this
				# pair too, so his own work is named — never called a net.
				head += _cabinet_signed(_cabinet_int(cabinet, "effect_per_turn")) + " a turn from him"
			else:
				head += _cabinet_signed(_cabinet_int(cabinet, "effect_per_turn")) + " a turn, drift "
				head += _cabinet_signed(_cabinet_int(cabinet, "drift_per_turn")) + ", net "
				head += _cabinet_signed(_cabinet_int(cabinet, "net_per_turn"))

			# Line 2 — where it stands, when it ends, what it costs.
			var standing = "    "
			if ally_display != "":
				# UNDERMINE moves the target↔ally pair, not France's own relation.
				standing += target_display + " and " + ally_display + " at " + str(_cabinet_int(cabinet, "current_relation"))
			else:
				standing += "Relations " + str(_cabinet_int(cabinet, "current_relation"))
			var descriptor = _cabinet_str(cabinet, "relation_descriptor")
			if descriptor == "":
				descriptor = _cabinet_str(cabinet, "current_descriptor")
			if descriptor != "":
				standing += " (" + descriptor + ")"
			var remaining_note = _cabinet_str(cabinet, "remaining_note")
			if remaining_note != "":
				standing += " · " + remaining_note
			standing += " · " + str(_cabinet_int(cabinet, "dp_per_turn")) + " DP a turn"

			if paused:
				bbcode += "[color=#" + Utils.COLOR_WARNING + "]" + head + "[/color]\n"
				bbcode += "[color=#" + Utils.COLOR_WARNING + "]" + standing + "[/color]"
			else:
				bbcode += head + "\n"
				bbcode += standing
			var recall = _cabinet_str(cabinet, "recall_command")
			if recall != "":
				bbcode += "   [url=do:" + recall + "][color=#" + Utils.COLOR_ERROR + "][Recall][/color][/url]"
			bbcode += "\n"

			# S14E-9: the mission's books — what it earned, each shock with
			# its cause, the turns he stood away (the backend's one line).
			var ledger_line = _cabinet_str(cabinet, "ledger_line")
			if ledger_line != "":
				bbcode += "    [color=#" + Utils.COLOR_INFO + "]So far: " + ledger_line + "[/color]\n"

			# COURT only: the favour his courting has earned our proposals.
			if cabinet.has("favour_cap"):
				bbcode += "    Our proposals to " + target_display + ": +" + str(_cabinet_int(cabinet, "favour_now"))
				bbcode += " of +" + str(_cabinet_int(cabinet, "favour_cap")) + " for his courting\n"
		bbcode += "\n"
	return bbcode


func _cabinet_int(d: Dictionary, key: String) -> int:
	"""A figure off the cabinet payload — 0 unless it is a number. A key
	present with a null value survives `.get()`'s default, and `int(null)`
	is a hard error (the TUT-F1 trap)."""
	var v = d.get(key, 0)
	if v is int or v is float:
		return int(v)
	return 0


func _cabinet_str(d: Dictionary, key: String) -> String:
	"""A string off the cabinet payload — "" for a missing or null key."""
	var v = d.get(key, "")
	if v == null:
		return ""
	return str(v)


func _cabinet_signed(n: int) -> String:
	return ("+" if n >= 0 else "") + str(n)


func _on_meta_clicked(meta):
	# Session UI-3 (November 12, 2026): a lead-in's ⓘ opens in place — the
	# note routes first, the current book re-renders from the cache, the scroll
	# put back.
	if Utils.is_note_meta(meta):
		Utils.toggle_note(meta)
		_rerender_in_place()
		return
	var meta_str = str(meta)
	# Session UI-5: the Territories' sort toggle and group folds.
	if meta_str.begins_with("terr:sort:"):
		_terr_sort = meta_str.trim_prefix("terr:sort:")
		_rerender_in_place()
		return
	if meta_str.begins_with("terr:fold:"):
		var gkey: String = meta_str.trim_prefix("terr:fold:")
		var was_open: bool = bool(_terr_open.get(gkey, _terr_first_group_key() == gkey))
		_terr_open[gkey] = not was_open
		_rerender_in_place()
		return
	if meta_str.begins_with("cancel:"):
		var marshal_name = meta_str.substr(7)
		if not cancel_order_requested.get_connections().is_empty():
			# CC-X15: the one cancel road (main.gd re-reads this book after).
			Utils.order_taken = false
			cancel_order_requested.emit(marshal_name)
			if Utils.order_taken:
				Utils.mark_chip_sent(content_area, meta_str, "Cancel")
		elif _api_client_ref:
			_api_client_ref.cancel_strategic_order(marshal_name, _on_cancel_result)
			# S12 part 2 (R6): the request is out; the chip says so until the
			# refreshed ledger redraws the tab.
			Utils.mark_chip_sent(content_area, meta_str, "Cancel")
	elif meta_str.begins_with("do:"):
		# NV-6: an Admiralty chip carries its full typed command — the same
		# string a player would type; the executor owns every gate.
		var command = meta_str.substr("do:".length())
		if command != "":
			# S12 part 2 (R6): the chip answers in place (the terminal's echo
			# lies under this screen) when main.gd took the order.
			Utils.order_taken = false
			naval_command.emit(command)
			if Utils.order_taken:
				Utils.mark_chip_sent(content_area, meta_str)


func _rerender_in_place() -> void:
	"""Session UI-3: re-draw the current book from the cached ledger, the
	reader's scroll kept (the Explanations switch and an ⓘ toggle both come
	here — never a network re-fetch)."""
	if not visible or cached_data.is_empty():
		return
	var held: int = scroll_container.scroll_vertical
	_render_current_tab()
	Utils.restore_scroll(scroll_container, held)


func refresh_if_open() -> void:
	"""NV-6 — re-pull after a chip command so posture/crossings/gate terms
	update in place (the diplomatic-ledger idiom)."""
	if visible and _api_client_ref:
		_api_client_ref.get_ledger(_on_ledger_received)


func refresh_pinned() -> void:
	"""UXR-D4 (Pre-Deploy S12b): the Side Desk re-reads a pinned screen
	after every command and every end turn — its CURRENT book, its scroll where the
	reader left it."""
	if not visible or _api_client_ref == null:
		return
	_api_client_ref.get_ledger(_on_pinned_ledger.bind(scroll_container.scroll_vertical))


func _on_pinned_ledger(response, held_scroll: int) -> void:
	_on_ledger_received(response)
	Utils.restore_scroll(scroll_container, held_scroll)


func _on_cancel_result(_response):
	# Refresh the ledger to reflect the cancelled order
	if _api_client_ref:
		_api_client_ref.get_ledger(_on_ledger_received)


# =============================================================================
# HELPERS
# =============================================================================

func _format_number(n: int) -> String:
	"""Format number with comma separators — shared Utils helper (UI-6 dedupe)."""
	return Utils.format_number(n)


func _on_overlay_input(event):
	"""Click on dark overlay to close."""
	if event is InputEventMouseButton and event.pressed:
		close_view()


# ═══ Session UI-2 (November 11, 2026): the book's stat strip ═══════════════
# The figures a book is opened for, as tiles above its page (scripts/
# stat_strip.gd): the chest on Economy, the army on Forces, the realm on
# Territories, the pools on Manpower. The page's words below are unchanged.
var _strip: Container = null   # Session UI-4: the strip is a flow row (it wraps)


func _build_strip() -> void:
	if _strip != null:
		return
	var vbox := get_node_or_null("PanelContainer/VBoxContainer") as VBoxContainer
	var scroll := get_node_or_null("PanelContainer/VBoxContainer/ScrollContainer")
	if vbox == null or scroll == null:
		return
	_strip = load("res://scripts/stat_strip.gd").new()
	vbox.add_child(_strip)
	vbox.move_child(_strip, scroll.get_index())


func _set_strip() -> void:
	if _strip == null:
		_build_strip()
	if _strip == null:
		return
	var tiles: Array = []
	match current_tab:
		0:
			var forces = cached_data.get("forces", [])
			var men := 0
			var corps := 0
			if forces is Array:
				for f in forces:
					if f is Dictionary and not bool(f.get("captured", false)):
						men += int(f.get("strength", 0))
						corps += 1
			var authority := int(cached_data.get("authority", 100))
			tiles = [
				{"glyph": "authority", "figure": str(authority),
					"caption": "Authority — " + str(cached_data.get("authority_label", "")),
					"meter": authority, "meter_max": 100, "marks": [60, 70, 85]},
				{"glyph": "strength", "figure": _format_number(men), "caption": "Men under arms"},
				{"glyph": "actions", "figure": str(corps), "caption": "Corps in the field"},
			]
		1:
			var territories = cached_data.get("territories", [])
			var income := 0
			var stab := 0
			var n := 0
			if territories is Array:
				for t in territories:
					if t is Dictionary:
						income += int(t.get("income", 0))
						stab += int(t.get("stability", 100))
						n += 1
			tiles = [
				{"glyph": "garrison", "figure": str(n), "caption": "Provinces held"},
				{"glyph": "income", "figure": _format_number(income) + "g", "caption": "Their income a turn"},
				{"glyph": "stability", "figure": (str(int(round(float(stab) / float(n)))) + "%") if n > 0 else "—",
					"caption": "Mean stability"},
			]
		2:
			var econ = cached_data.get("economy", {})
			var treasury := int(econ.get("treasury", 0))
			var net := int(econ.get("net", 0))
			tiles = [
				{"glyph": "gold", "figure": _format_number(treasury) + "g", "caption": "The treasury"},
				{"glyph": "income", "figure": ("+" if net >= 0 else "\u2212") + _format_number(absi(net)) + "g",
					"caption": "Net a turn", "tone": Utils.UI_SCORE_POSITIVE.lightened(0.15) if net >= 0 else Utils.UI_ALERT_TEXT},
			]
			if str(econ.get("ceiling_state", "bounded")) == "bounded" and int(econ.get("ceiling", 0)) > 0:
				tiles.append({"glyph": "medal", "figure": _format_number(int(econ.get("ceiling", 0))) + "g",
					"caption": "Ceiling — where the charges level it"})
			var levy = econ.get("levy", {})
			if levy is Dictionary and int(levy.get("force_limit", 0)) > 0:
				var army := int(levy.get("army_strength", 0))
				var limit := int(levy.get("force_limit", 0))
				tiles.append({"glyph": "foot", "figure": _format_number(army),
					"caption": "Under arms of " + _format_number(limit), "meter": army,
					"meter_max": maxi(limit, army), "marks": [limit],
					"tone": Utils.UI_WARNING if army > limit else Utils.UI_GOLD_BRIGHT})
		4:
			var mp = cached_data.get("manpower", {})
			for pair in [["infantry", "foot", "Foot"], ["cavalry", "horse", "Horse"], ["artillery", "guns", "Guns"]]:
				var pool = mp.get(pair[0], {})
				if pool is Dictionary and not pool.is_empty():
					var cur := int(pool.get("current", 0))
					var mx := int(pool.get("max", 0))
					tiles.append({"glyph": pair[1], "figure": _format_number(cur),
						"caption": str(pair[2]) + " pool of " + _format_number(mx),
						"meter": cur, "meter_max": maxi(mx, 1)})
	_strip.set_tiles(tiles)
