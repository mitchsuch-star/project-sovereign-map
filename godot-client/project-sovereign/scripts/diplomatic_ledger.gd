extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Diplomatic Ledger Screen (Session 8B)
# =============================================================================
# 7-section sub-tabbed screen. CanvasLayer 50.
# Tabs: NATIONS, TREATIES, THREAT & COALITION, TALLEYRAND, WAR BARGAINS, VASSALS,
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
const COLOR_RED = "cd5c5c"
# IQ-2 (Sept 14, 2026) flip lever — true: the Talleyrand tab's authority
# colour arms test the vocabulary the backend actually emits
# (`AuthorityTracker.get_authority_label`). false = the pre-IQ-2 arms, which
# never matched, byte-for-byte.
const AUTHORITY_ARMS_READ_THE_BACKEND := true

# State
var current_tab: int = 0  # 0=nations, 1=treaties, 2=threat, 3=talleyrand, 4=bargains, 5=vassals, 6=congress
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
	close_button.pressed.connect(close_view)
	Utils.apply_icon_only_button(close_button, Utils.ICON_PHOSPHOR + "x.svg")
	background_overlay.gui_input.connect(_on_overlay_input)
	content_area.meta_clicked.connect(_on_content_meta_clicked)
	# PC15-18 (NV-P1 family census): a fit_content RichTextLabel inside a
	# ScrollContainer defaults to MOUSE_FILTER_STOP and eats the wheel
	# before its parent can scroll. PASS keeps meta_clicked chips working.
	content_area.mouse_filter = Control.MOUSE_FILTER_PASS

	tab_buttons = [nations_tab, treaties_tab, threat_tab, talleyrand_tab, bargains_tab, vassals_tab, congress_tab]
	for i in range(tab_buttons.size()):
		tab_buttons[i].pressed.connect(_on_tab_pressed.bind(i))

	# Build tab styles
	_active_tab_style = StyleBoxFlat.new()
	_active_tab_style.bg_color = Utils.UI_ACTIVE_TAB_BG
	_active_tab_style.border_width_bottom = 2
	_active_tab_style.border_color = Utils.UI_GOLD
	_active_tab_style.content_margin_left = 6.0
	_active_tab_style.content_margin_right = 6.0
	_active_tab_style.content_margin_top = 3.0
	_active_tab_style.content_margin_bottom = 3.0

	_normal_tab_style = StyleBoxFlat.new()
	_normal_tab_style.bg_color = Utils.UI_PANEL_BG
	_normal_tab_style.content_margin_left = 6.0
	_normal_tab_style.content_margin_right = 6.0
	_normal_tab_style.content_margin_top = 3.0
	_normal_tab_style.content_margin_bottom = 3.0

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
	if _focused is LineEdit or _focused is TextEdit:
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
		if i == current_tab:
			tab_buttons[i].add_theme_stylebox_override("normal", _active_tab_style)
		else:
			tab_buttons[i].add_theme_stylebox_override("normal", _normal_tab_style)


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
	var stamp_color = Utils.COLOR_GREY
	match kind:
		"coalition":
			stamp_color = COLOR_RED
		"proper_bloc":
			stamp_color = Utils.COLOR_COMMAND
		"descriptive_bloc":
			stamp_color = Utils.COLOR_INFO
		"vassal":
			stamp_color = Utils.COLOR_GOLD
		"neutral":
			stamp_color = Utils.COLOR_GREY
	return " [color=#" + stamp_color + "][" + label + "][/color]"


# =============================================================================
# TAB 1: NATION OVERVIEW
# =============================================================================

func _render_nations():
	var nations = cached_data.get("nations", [])
	var bbcode = ""
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]═══ NATION OVERVIEW ═══[/color]\n"
	# R159 (POSITION 7): each core screen names the mechanic it displays.
	bbcode += "[color=#" + Utils.COLOR_DIMMED + "]Every court of Europe — its temper toward France, and the instruments to move it. Press F1 to treat; D closes this ledger.[/color]\n\n"

	# AI-1b (the mirror): Europe's derived reading of FRANCE — the player's
	# own row, first. Omitted when null (legacy/bare worlds).
	var mirror = cached_data.get("france_mirror")
	if mirror != null and mirror is Dictionary:
		bbcode += "[color=#" + Utils.COLOR_GOLD + "][b]How Europe Reads France[/b][/color]\n"
		var mirror_lines = mirror.get("lines", [])
		for ml in mirror_lines:
			bbcode += "  [color=#" + Utils.COLOR_INFO + "]" + str(ml) + "[/color]\n"
		bbcode += "\n"

	# AI-3r (§2.5-3): France's own exposure — the same reserve/free
	# derivation the war council applies to every court, shown to the
	# player. Display only, never a gate on orders (gate Q5). Backend-
	# composed line (R7); null omits the block.
	var exposure = cached_data.get("france_exposure")
	if exposure != null and exposure is Dictionary:
		var exposure_line = str(exposure.get("line", ""))
		if exposure_line != "":
			bbcode += "[color=#" + Utils.COLOR_GOLD + "][b]The Emperor's Own Exposure[/b][/color]\n"
			bbcode += "  [color=#" + Utils.COLOR_INFO + "]" + Utils.humanize_nation_keys_in_text(exposure_line) + "[/color]\n"
			bbcode += "\n"

	if nations.size() == 0:
		bbcode += "[color=#" + Utils.COLOR_INFO + "]No nations in diplomatic contact.[/color]\n"
		content_area.text = bbcode
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
				state_color = Utils.COLOR_GREY
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

		bbcode += Utils.bb_flag(name, 14)
		bbcode += "[color=#" + Utils.COLOR_GOLD + "][b]" + Utils.display_nation_name(name) + "[/b][/color]"
		bbcode += _format_bloc_stamp(n.get("bloc_stamp"))
		bbcode += " — [color=#" + state_color + "]" + Utils.display_diplo_state(diplo_state) + "[/color]"
		bbcode += "  Relation: [color=#" + rel_color + "]" + rel_text + "[/color]"

		# N4: Vassal eligibility
		var vassal_eligible = n.get("vassal_eligible", false)
		var power_tier = str(n.get("power_tier", ""))
		if vassal_eligible and power_tier == "minor":
			bbcode += "  [color=#" + Utils.COLOR_GOLD + "]★ Vassalizable[/color]"
		bbcode += "\n"

		# Diplomat info
		var diplomat = n.get("diplomat")
		if diplomat != null and diplomat is Dictionary:
			var d_name = str(diplomat.get("name", "?"))
			var d_pers = str(diplomat.get("personality", "?")).capitalize()
			var d_skill = int(diplomat.get("skill", 0))
			bbcode += "  Diplomat: " + d_name + " (" + d_pers + ") — Skill " + str(d_skill) + "\n"
		else:
			bbcode += "  Diplomat: [color=#" + Utils.COLOR_GREY + "]None[/color]\n"

		# Regions + Army
		var regions = int(n.get("regions_controlled", 0))
		var army = str(n.get("army_strength", "Unknown"))
		bbcode += "  Regions: " + str(regions) + "   Army: " + army + "\n"

		# N5: Trade income
		var trade_income = int(n.get("trade_income", 0))
		if trade_income > 0:
			bbcode += "  Trade: [color=#" + Utils.COLOR_GOLD + "]+" + str(trade_income) + "g/turn[/color]\n"

		# Treaties
		var treaties = n.get("active_treaties", [])
		if treaties.size() > 0:
			bbcode += "  Treaties: " + ", ".join(PackedStringArray(treaties)) + "\n"
		else:
			bbcode += "  Treaties: [color=#" + Utils.COLOR_GREY + "]None[/color]\n"

		# NA-1: the nation's active design (omit when null — bloc_stamp contract)
		var agenda = n.get("agenda")
		if agenda != null and agenda is Dictionary:
			var agenda_title = str(agenda.get("title", ""))
			var agenda_stance = str(agenda.get("stance_line", ""))
			if agenda_title != "":
				bbcode += "  Design: [color=#" + Utils.COLOR_GOLD + "]" + agenda_title + "[/color]"
				if agenda_stance != "":
					bbcode += " [color=#" + Utils.COLOR_GREY + "]— " + agenda_stance + "[/color]"
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
						bbcode += " [color=#" + Utils.COLOR_GOLD + "]→ " + forms_line + "[/color]"
				bbcode += "\n"

		# AI-1: the nation's intent — its price, fully open (D4: want,
		# target and rung always shown; only timing is uncertain).
		var intent = n.get("intent")
		if intent != null and intent is Dictionary:
			var intent_summary = str(intent.get("summary", ""))
			if intent_summary != "":
				bbcode += "  Intent: [color=#" + Utils.COLOR_INFO + "]" + intent_summary + "[/color]\n"

		# AI-2b/2e (Stage C): every live D5 instrument this court is
		# party to — sponsorships, licences, neutrality compacts,
		# buy-off bargains, guarantees, an open allegiance auction.
		# Backend-composed line (R7); null omits the row.
		var compacts = n.get("compacts")
		if compacts != null and str(compacts) != "":
			bbcode += "  Compacts: [color=#" + Utils.COLOR_GOLD + "]" + Utils.humanize_nation_keys_in_text(str(compacts)) + "[/color]\n"

		# AI-4c (Stage D): war-weariness, explicitly labelled as national
		# exhaustion across ALL the court's wars, belligerents named —
		# "let them bleed while France rearms" readable per court.
		# Backend-composed line (R7); null omits the row.
		var weariness = n.get("war_weariness")
		if weariness != null and weariness is Dictionary:
			var weariness_line = str(weariness.get("line", ""))
			if weariness_line != "":
				bbcode += "  Weariness: [color=#" + Utils.COLOR_WARNING + "]" + Utils.humanize_nation_keys_in_text(weariness_line) + "[/color]\n"

		# AI-3r (§2.5-2): the court's exposure — free field army vs the
		# rear-security reserve, the war council's own arithmetic made
		# readable. Backend-composed line (R7); null omits the row.
		var exposure_row = n.get("exposure")
		if exposure_row != null and exposure_row is Dictionary:
			var exposure_row_line = str(exposure_row.get("line", ""))
			if exposure_row_line != "":
				bbcode += "  Exposure: [color=#" + Utils.COLOR_INFO + "]" + Utils.humanize_nation_keys_in_text(exposure_row_line) + "[/color]\n"

		# N1: AI-AI Relations (DPF-1: includes relation descriptor)
		var ai_relations = n.get("ai_relations", [])
		if ai_relations.size() > 0:
			var ai_parts = []
			for ar in ai_relations:
				var ar_nation = str(ar.get("nation", "?"))
				var ar_state = str(ar.get("state", "PEACE"))
				var ar_relation = int(ar.get("relation", 0))
				var ar_descriptor = str(ar.get("relation_descriptor", "Neutral"))
				var ar_state_color = Utils.COLOR_GREY
				match ar_state:
					"WAR":
						ar_state_color = COLOR_RED
					"ALLIANCE", "DEFENSIVE_ALLIANCE":
						ar_state_color = Utils.COLOR_SUCCESS
					"NON_AGGRESSION", "OPEN_BORDERS":
						ar_state_color = Utils.COLOR_BLUE
				var ar_desc_color = Utils.COLOR_GREY
				if ar_relation > 0:
					ar_desc_color = Utils.COLOR_SUCCESS
				elif ar_relation < 0:
					ar_desc_color = COLOR_RED
				ai_parts.append(Utils.display_nation_name(ar_nation) + " [color=#" + ar_state_color + "][" + Utils.display_diplo_state(ar_state) + "][/color] — [color=#" + ar_desc_color + "]" + ar_descriptor + " (" + str(ar_relation) + ")[/color]")
			bbcode += "  AI Relations: " + ", ".join(PackedStringArray(ai_parts)) + "\n"

		# N2: War Score Breakdown (WAR only)
		var war_score = n.get("war_score_breakdown")
		if war_score != null and war_score is Dictionary:
			var total = int(war_score.get("total", 0))
			var ws_color = Utils.COLOR_SUCCESS if total > 0 else (COLOR_RED if total < 0 else Utils.COLOR_GREY)
			var ws_sign = "+" if total > 0 else ""
			bbcode += "  War Score: [color=#" + ws_color + "][" + ws_sign + str(total) + "][/color]  ("
			var ws_parts = []
			# PT-J2: campaign + blood are the war's memory components.
			# HC-1: blockade joins them, rendered only when nonzero.
			var ws_keys = ["territory", "battles", "decisive", "capital", "campaign", "blood"]
			if int(war_score.get("blockade", 0)) != 0:
				ws_keys.append("blockade")
			for ws_key in ws_keys:
				var ws_val = int(war_score.get(ws_key, 0))
				var comp_sign = "+" if ws_val > 0 else ""
				var comp_color = Utils.COLOR_SUCCESS if ws_val > 0 else (COLOR_RED if ws_val < 0 else Utils.COLOR_GREY)
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

		bbcode += "\n"

	content_area.text = bbcode


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
		bbcode += "[color=#" + Utils.COLOR_GREY + "]No active treaties.[/color]\n"
		content_area.text = bbcode
		return
	elif treaties.size() == 0:
		bbcode += "[color=#" + Utils.COLOR_GREY + "]No active treaties.[/color]\n\n"

	for t in treaties:
		var nation_a = str(t.get("nation_a", "?"))
		var nation_b = str(t.get("nation_b", "?"))
		var treaty_type = str(t.get("treaty_type", "unknown"))
		var clauses = t.get("clauses", [])
		var duration = t.get("duration", "permanent")
		var cancel_cost = int(t.get("cancel_cost", 1))

		# T3: Player vs AI-AI distinction
		var involves_player = t.get("involves_player", true)
		var header_color = Utils.COLOR_GOLD if involves_player else Utils.COLOR_GREY

		bbcode += "[color=#" + header_color + "]" + Utils.display_nation_name(nation_a) + "[/color]"
		bbcode += " [color=#" + Utils.COLOR_INFO + "]↔[/color] "
		bbcode += "[color=#" + header_color + "]" + Utils.display_nation_name(nation_b) + "[/color]"
		bbcode += ": [b]" + treaty_type.replace("_", " ").capitalize() + "[/b]\n"

		# Clauses
		if clauses.size() > 0:
			var clause_strs = []
			for c in clauses:
				clause_strs.append(str(c))
			bbcode += "  Clauses: " + ", ".join(PackedStringArray(clause_strs)) + "\n"
		else:
			bbcode += "  Clauses: [color=#" + Utils.COLOR_GREY + "]None[/color]\n"

		# T4: Armistice countdown
		var armistice_remaining = t.get("armistice_remaining")
		if armistice_remaining != null:
			bbcode += "  Duration: [color=#" + COLOR_AMBER + "]Armistice — expires in " + str(int(armistice_remaining)) + " turns[/color]\n"
		else:
			# Duration
			var dur_str = ""
			if duration is int or duration is float:
				dur_str = str(int(duration)) + " turns"
			else:
				dur_str = str(duration)
			bbcode += "  Duration: " + dur_str + "   Cancel cost: " + str(cancel_cost) + " DP\n"

		# T2: Turn signed
		var turn_signed = int(t.get("turn_signed", 0))
		if turn_signed > 0 and current_turn > 0:
			var turns_ago = current_turn - turn_signed
			bbcode += "  Signed: Turn " + str(turn_signed) + " (" + str(turns_ago) + " turns ago)\n"

		# T1: Gold per turn
		var gold_per_turn = t.get("gold_per_turn")
		if gold_per_turn != null and gold_per_turn is Array and gold_per_turn.size() > 0:
			for gpt in gold_per_turn:
				var gpt_from = str(gpt.get("from", "?"))
				var gpt_to = str(gpt.get("to", "?"))
				var gpt_amount = int(gpt.get("amount", 0))
				bbcode += "  Gold Flow: [color=#" + Utils.COLOR_GOLD + "]" + Utils.display_nation_name(gpt_from) + " → " + Utils.display_nation_name(gpt_to) + ": " + str(gpt_amount) + "g/turn[/color]\n"

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
				bbcode += "  [color=#" + Utils.COLOR_GREY + "](" + row_type_display + " · T" + str(s_turn) + ")[/color]\n"
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
				bbcode += "  [color=#" + Utils.COLOR_GREY + "](" + row_type_display + " · T" + str(s_turn) + ")[/color]\n"
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
			bbcode += "  [color=#" + Utils.COLOR_GREY + "](T" + str(s_turn) + ")[/color]\n"
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

	content_area.text = bbcode


# =============================================================================
# TAB 3: THREAT & COALITION
# =============================================================================

func _render_balance_of_europe():
	var boe = cached_data.get("balance_of_europe", {})
	if boe.is_empty():
		content_area.text = "[color=#" + Utils.COLOR_GREY + "]No data available.[/color]"
		return
	var bbcode = ""
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]BALANCE OF EUROPE[/color]\n"
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]────────────────[/color]\n"

	var headline_case = str(boe.get("headline_case", "NO_HEGEMON"))
	var hegemon = Utils.display_nation_name(str(boe.get("hegemon", "")))
	var share_pct = int(float(boe.get("hegemon_share", 0.0)) * 100.0)
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
			bbcode += "[color=#" + COLOR_RED + "]Coalition declared"
			if leader != "":
				bbcode += " under " + leader
			bbcode += ".[/color]\n\n"
		"BREWING":
			bbcode += "[color=#" + COLOR_AMBER + "]A coalition is brewing against " + label + ".[/color]\n\n"
		"COOLDOWN":
			var cooldown = int(boe.get("cooldown_turns_remaining", 0))
			bbcode += "[color=#" + Utils.COLOR_GREY + "]The courts are recovering from the last coalition."
			if cooldown > 0:
				bbcode += " Cooldown: " + str(cooldown) + " turns."
			# IQ-2: under the collapse the league lapsed on low threat and
			# ended no war — the backend names the courts still fighting us.
			var cooldown_note = boe.get("headline_note", "")
			if cooldown_note is String and cooldown_note != "":
				bbcode += " " + cooldown_note
			bbcode += "[/color]\n\n"
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
			bbcode += "[color=#" + Utils.COLOR_GREY + "]No single court dominates the balance.[/color]\n\n"

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
			tier_color = COLOR_RED
		"CRITICAL":
			tier_color = COLOR_RED
			_start_critical_pulse()
		_:
			tier_color = Utils.COLOR_INFO

	bbcode += "Threat Level: [color=#" + tier_color + "]" + str(threat_level) + " / 100  [" + threat_tier + "][/color]\n"

	# Visual threat bar — 20 chars wide
	var filled = int(threat_level / 5)  # 0-20
	if filled > 20:
		filled = 20
	var empty = 20 - filled

	var bar_color = Utils.COLOR_SUCCESS
	if threat_level >= 60:
		bar_color = COLOR_RED
	elif threat_level >= 30:
		bar_color = COLOR_AMBER

	var bar = "[color=#" + bar_color + "]"
	for i in range(filled):
		bar += "█"
	bar += "[/color][color=#" + Utils.COLOR_GREY + "]"
	for i in range(empty):
		bar += "░"
	bar += "[/color]"
	bbcode += bar + "\n"
	# FA-D11 (slice 17, Phase 2): the one number a player plans around — the
	# backend computed it all along and no renderer read it.
	var projection = boe.get("threat_projection", {})
	# IQ-2: a collapsed France is planning no war of conquest — the backend
	# sends the true reading of the alarm instead of the projection.
	var projection_collapse = projection.get("collapse_line", "") if projection is Dictionary else ""
	if projection_collapse is String and projection_collapse != "":
		bbcode += "[color=#" + Utils.COLOR_ERROR + "]" + projection_collapse + "[/color]\n"
	elif projection is Dictionary and projection.size() > 0:
		var nxt = int(projection.get("after_next_war", threat_level))
		var brewing = int(projection.get("brewing_threshold", 60))
		var instant = int(projection.get("instant_threshold", 80))
		var to_brewing = int(projection.get("wars_until_brewing", 0))
		var to_instant = int(projection.get("wars_until_instant", 0))
		bbcode += "[color=#" + Utils.COLOR_DIMMED + "]Next war of conquest: " + str(threat_level) + " → " + str(nxt)
		bbcode += " · brews at " + str(brewing) + " (" + (str(to_brewing) + " war" + ("s" if to_brewing != 1 else "") + " away" if to_brewing > 0 else "now") + ")"
		bbcode += " · forms at once at " + str(instant) + " (" + (str(to_instant) if to_instant > 0 else "now") + ")"
		var dissolve = int(boe.get("dissolution_threat_threshold", 20))
		bbcode += " · dissolves below " + str(dissolve) + "[/color]\n"
	bbcode += "\n"

	# Threat sources this turn (with human-readable labels)
	var sources = boe.get("threat_sources_this_turn", [])
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]This Turn's Sources:[/color]\n"
	if sources.size() == 0:
		bbcode += "  [color=#" + Utils.COLOR_GREY + "]No new threats[/color]\n"
	else:
		for s in sources:
			if s is Dictionary:
				var s_display = str(s.get("display", str(s)))
				var s_amount = int(s.get("amount", 0))
				var s_color = COLOR_RED if s_amount > 0 else (Utils.COLOR_SUCCESS if s_amount < 0 else Utils.COLOR_GREY)
				bbcode += "  • [color=#" + s_color + "]" + s_display + "[/color]\n"
			else:
				bbcode += "  • " + str(s) + "\n"
	bbcode += "\n"

	# Qualifying nations
	var qualifying = boe.get("qualifying_nations", [])
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]Nations That Would Join Coalition:[/color]\n"
	if qualifying.size() == 0:
		bbcode += "  [color=#" + Utils.COLOR_GREY + "]None currently[/color]\n"
	else:
		var qual_strs = []
		for q in qualifying:
			qual_strs.append(Utils.display_nation_name(str(q)))
		bbcode += "  " + ", ".join(PackedStringArray(qual_strs)) + "\n"
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
		bbcode += "  [color=#" + COLOR_RED + "]ACTIVE: " + c_name + " — Leader: " + c_leader + ", Posture: " + c_posture.capitalize() + "[/color]\n"
		bbcode += "  Combined Strength: " + str(active_coalition.get("combined_strength_display", "Unknown")) + "\n\n"

		# Per-member block
		var members = active_coalition.get("members", [])
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
			var we_bar = ""
			for i in range(we_filled):
				we_bar += "█"
			for i in range(we_empty):
				we_bar += "░"

			bbcode += "  • " + m_nation + ": " + m_strength + ", WE: " + str(m_we) + "/" + str(we_max) + " [" + we_bar + "]\n"
	elif coalition_state == "BREWING":
		var turns_str = ""
		if brewing_turns != null:
			turns_str = str(int(brewing_turns))
		else:
			turns_str = "?"
		bbcode += "  [color=#" + COLOR_AMBER + "]Brewing — " + turns_str + " turns until formation[/color]\n"
	else:
		var coalition_cooldown = int(boe.get("coalition_cooldown", 0))
		if coalition_cooldown > 0:
			bbcode += "  [color=#" + Utils.COLOR_GREY + "]No coalition active. Post-dissolution cooldown: " + str(coalition_cooldown) + " turns.[/color]\n"
		else:
			bbcode += "  [color=#" + Utils.COLOR_GREY + "]No coalition active.[/color]\n"

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
				bbcode += "  [color=#" + Utils.COLOR_GREY + "]" + subsidy_counter + "[/color]\n"

	# Dissolution conditions — the TWO the engine actually tests
	# (coalition.check_dissolution). The retired war-exhaustion clause
	# promised a lever that never existed: a live campaign showed a member
	# pinned at the exhaustion cap with the coalition still standing.
	bbcode += "\n[color=#" + Utils.COLOR_GREY + "]Coalition dissolves if threat falls below "
	bbcode += str(int(boe.get("dissolution_threat_threshold", 20)))
	bbcode += " or fewer than "
	bbcode += str(int(boe.get("dissolution_min_members", 2)))
	bbcode += " members remain at war.[/color]\n"

	content_area.text = bbcode


# =============================================================================
# TAB 4: TALLEYRAND
# =============================================================================

func _render_talleyrand():
	var t = cached_data.get("talleyrand", {})
	var bbcode = ""

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
	bbcode += "Authority: [color=#" + authority_color + "]" + str(authority) + "[/color]/100"
	bbcode += "   Skill: " + str(skill)
	bbcode += "   DP: [color=#" + Utils.COLOR_GOLD + "]" + str(dp_remaining) + "/" + str(dp_max) + "[/color]\n"

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
			bbcode += " + Capital [color=#" + COLOR_RED + "]" + str(bp_cap) + "[/color]"
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
	bbcode += "  [color=#" + Utils.COLOR_GREY + "]his full survey of the war, the treasury, and the courts[/color]\n\n"

	# Current mission
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]CURRENT MISSION[/color]\n"
	var mission = t.get("active_mission")
	if mission == null or not (mission is Dictionary):
		bbcode += "  [color=#" + Utils.COLOR_GREY + "]Idle — no active diplomatic mission.[/color]\n"
		# IQ-4: how his last mission ended, when the ledger carries it.
		var last_mission = t.get("last_mission")
		if last_mission is Dictionary and not last_mission.is_empty():
			var last_phrase = str(last_mission.get("reason_phrase", last_mission.get("reason", "")))
			bbcode += "  [color=#" + Utils.COLOR_GREY + "]Last mission: " + str(last_mission.get("type_display", "?")) + " — " + str(last_mission.get("target_display", "?")) + ", " + last_phrase + ".[/color]\n"
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
		bbcode += "  " + m_type_display + " → " + m_target + "\n"

		# DPF-2: Descriptor-based progress
		var initial_desc = str(mission.get("initial_descriptor", ""))
		var current_desc = str(mission.get("current_descriptor", ""))
		var relation_delta = int(mission.get("relation_delta", 0))
		if initial_desc != "" and current_desc != "":
			var delta_str = str(relation_delta) if relation_delta < 0 else "+" + str(relation_delta)
			var arrow_color = Utils.COLOR_GREY
			if relation_delta > 0:
				arrow_color = Utils.COLOR_SUCCESS
			elif relation_delta < 0:
				arrow_color = COLOR_RED
			if initial_desc != current_desc:
				bbcode += "  [color=#" + arrow_color + "]" + initial_desc + " → " + current_desc + " (" + delta_str + ", " + str(m_duration) + " turns)[/color]\n"
			else:
				bbcode += "  [color=#" + arrow_color + "]" + current_desc + " (" + delta_str + " over " + str(m_duration) + " turns)[/color]\n"
		else:
			bbcode += "  Progress: N/A (mission predates tracking)\n"

		bbcode += "  Status: " + status
		# TA4: Mission effect text
		var effect_text = str(mission.get("effect_text", ""))
		var dp_cost = int(mission.get("dp_cost_per_turn", 0))
		if dp_cost > 0:
			bbcode += ", Cost: " + str(dp_cost) + " DP/turn"
		bbcode += "\n"
		if effect_text:
			bbcode += "  [color=#" + Utils.COLOR_GREY + "]Effect: " + effect_text + "[/color]\n"

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
			bbcode += "  [color=#" + Utils.COLOR_GOLD + "]" + net_clause + remaining_note + "[/color]\n"
		else:
			# TA5: Remaining turns (the pre-IQ-4 render, kept for an absent key)
			var remaining = mission.get("remaining_turns")
			if remaining != null:
				bbcode += "  [color=#" + Utils.COLOR_GOLD + "]Completes in " + Utils.plural(int(remaining), "turn") + "[/color]\n"
			else:
				bbcode += "  [color=#" + Utils.COLOR_GREY + "]Ongoing[/color]\n"
	bbcode += "\n"

	# Proposal in transit
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]PROPOSAL IN TRANSIT[/color]\n"
	var pit = t.get("proposal_in_transit")
	if pit == null or not (pit is Dictionary):
		bbcode += "  [color=#" + Utils.COLOR_GREY + "]None[/color]\n"
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
		bbcode += "  [color=#" + Utils.COLOR_GREY + "]None detected.[/color]\n"
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
	var rel_color = Utils.COLOR_GREY
	if reliability >= 30:
		rel_desc = "Honorable"
		rel_color = Utils.COLOR_SUCCESS
	elif reliability >= 0:
		rel_desc = "Neutral"
		rel_color = Utils.COLOR_GREY
	elif reliability >= -30:
		rel_desc = "Unreliable"
		rel_color = COLOR_AMBER
	else:
		rel_desc = "Treacherous"
		rel_color = COLOR_RED
	var rel_sign = "+" if reliability > 0 else ""
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]DIPLOMATIC RELIABILITY[/color]\n"
	bbcode += "  Reliability: [color=#" + rel_color + "]" + rel_sign + str(reliability) + " (" + rel_desc + ")[/color]\n\n"

	# TA1: Diplomatic history
	var history = t.get("diplomatic_history", [])
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]DIPLOMATIC HISTORY[/color]\n"
	if history.size() == 0:
		bbcode += "  [color=#" + Utils.COLOR_GREY + "]No diplomatic events recorded.[/color]\n"
	else:
		# Show last 10 entries
		var start_idx = max(0, history.size() - 10)
		for i in range(start_idx, history.size()):
			var entry = history[i]
			if entry is Dictionary:
				var h_turn = int(entry.get("turn", 0))
				var h_type = str(entry.get("type") if entry.get("type") != null else "?")
				var h_target = Utils.display_nation_name(str(entry.get("target", "")))
				var h_nation = str(entry.get("nation", ""))
				var h_detail = str(entry.get("detail", ""))
				# Color by type
				var h_color = Utils.COLOR_GREY
				if h_type != "?" and "accept" in h_type.to_lower():
					h_color = Utils.COLOR_SUCCESS
				elif h_type != "?" and ("war" in h_type.to_lower() or "break" in h_type.to_lower()):
					h_color = COLOR_RED
				var h_text = "Turn " + str(h_turn) + ": "
				h_text += h_type.replace("_", " ").capitalize()
				if h_target:
					h_text += " — " + h_target
				if h_detail:
					h_text += " (" + h_detail + ")"
				bbcode += "  [color=#" + h_color + "]" + h_text + "[/color]\n"
			else:
				bbcode += "  " + str(entry) + "\n"

	content_area.text = bbcode


# =============================================================================
# TAB 5: WAR BARGAINS
# =============================================================================

func _render_war_bargains():
	var bargains = cached_data.get("war_bargains", [])
	var bbcode = ""
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]═══ WAR BARGAINS ═══[/color]\n\n"

	if bargains.size() == 0:
		bbcode += "[color=#" + Utils.COLOR_GREY + "]No war bargains recorded.[/color]\n"
		content_area.text = bbcode
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

	content_area.text = bbcode


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
			status_color = Utils.COLOR_GREY

	var entry = ""
	entry += "  [color=#" + Utils.COLOR_GOLD + "][b]" + promiser + " → " + beneficiary + "[/b][/color]"
	entry += "  [color=#" + status_color + "][" + status.to_upper() + "][/color]\n"
	entry += "    Enemy: " + named_enemy + "   Claim: " + claim_region + "\n"
	entry += "    Sealed: Turn " + str(created_turn)

	var badge = str(b.get("badge", ""))
	if badge != "":
		var badge_color = Utils.COLOR_GREY
		match badge:
			"honoured":
				badge_color = Utils.COLOR_SUCCESS
			"broken":
				badge_color = Utils.COLOR_ERROR
			"lapsed":
				badge_color = Utils.COLOR_GREY
		entry += "   [color=#" + badge_color + "]" + badge.to_upper() + "[/color]"

	var ended_turn = b.get("ended_turn")
	if ended_turn != null:
		entry += "   Ended: Turn " + str(int(ended_turn))

	var end_reason = str(b.get("end_reason", ""))
	if end_reason != "":
		entry += "   (" + end_reason.replace("_", " ") + ")"

	var cooldown = int(b.get("cooldown_remaining", 0))
	if cooldown > 0:
		entry += "\n    [color=#" + COLOR_AMBER + "]Cooldown: " + str(cooldown) + " turns[/color]"

	entry += "\n\n"
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
		bbcode += "[color=#" + Utils.COLOR_GREY + "]Bind a minor power to the Empire: vassalize a court marked "
		bbcode += "[color=#" + Utils.COLOR_GOLD + "]★ Vassalizable[/color][color=#" + Utils.COLOR_GREY + "] on the Nations tab "
		bbcode += "('vassalize Saxony'), demand vassalage at the peace table, or propose it through Diplomacy (F1).[/color]\n"
		content_area.text = bbcode
		return

	var total_tribute = int(vassal_data.get("total_tribute", 0))
	bbcode += "[color=#" + Utils.COLOR_INFO + "]" + str(rows.size()) + " client state" + ("s" if rows.size() != 1 else "")
	bbcode += " remit [color=#" + Utils.COLOR_GOLD + "]+" + Utils.format_number(total_tribute) + "g/turn[/color] in tribute.[/color]\n"
	if vassal_data.get("actions_blocked", false):
		bbcode += "[color=#" + COLOR_AMBER + "]Envoys await your reply — vassal instruments are suspended until the matter is answered.[/color]\n"
	bbcode += "\n"

	for v in rows:
		bbcode += _format_vassal_card(v, bool(vassal_data.get("actions_blocked", false)))

	content_area.text = bbcode


func _format_vassal_card(v: Dictionary, actions_blocked: bool) -> String:
	var bbcode = ""
	var name = str(v.get("name", "?"))
	var loyalty = int(v.get("loyalty", 50))
	var autonomy_name = str(v.get("autonomy_name", "Satellite"))
	var path = str(v.get("path", "treaty"))
	var created_turn = int(v.get("created_turn", 0))

	# ── Header: flag + name + autonomy + provenance ──
	bbcode += Utils.bb_flag(name, 18)
	bbcode += "[color=#" + Utils.COLOR_GOLD + "][b]" + Utils.display_nation_name(name) + "[/b][/color]"
	bbcode += "  [color=#" + Utils.COLOR_INFO + "]" + autonomy_name + "[/color]"
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
	bbcode += "  [color=#" + Utils.COLOR_GREY + "](" + path_label
	if created_turn > 0 and path != "scenario":
		bbcode += ", Turn " + str(created_turn)
	bbcode += ")[/color]\n"

	# ── Loyalty bar + trend forecast ──
	var loyalty_color = Utils.COLOR_SUCCESS
	if loyalty < 35:
		loyalty_color = Utils.COLOR_ERROR
	elif loyalty < 60:
		loyalty_color = COLOR_AMBER
	var filled = clampi(int(round(loyalty / 10.0)), 0, 10)
	bbcode += "  [img color=#" + loyalty_color + " width=" + str(_LOYALTY_BAR_W) + " height=" + str(_LOYALTY_BAR_H) + "]res://assets/ui/bars/bar_" + str(filled) + ".png[/img]"
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
			bbcode += "  [color=#" + Utils.COLOR_GREY + "]≈ steady[/color]"
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
			bbcode += "  [color=#" + Utils.COLOR_GREY + "]" + hint + "[/color]"
		bbcode += "\n"

	# ── Tribute + contribution tier ──
	var tribute = int(v.get("tribute", 0))
	var tribute_pct = int(v.get("tribute_rate_pct", 75))
	bbcode += "  Tribute: [color=#" + Utils.COLOR_GOLD + "]+" + Utils.format_number(tribute) + "g/turn[/color]"
	bbcode += " [color=#" + Utils.COLOR_GREY + "](" + str(tribute_pct) + "% of their income)[/color]"
	var contribution = str(v.get("contribution", "loyal"))
	match contribution:
		"loyal":
			bbcode += "   [color=#" + Utils.COLOR_SUCCESS + "]Answers the call to arms[/color]"
		"wavering":
			# IQ-7 review [22]: the regiments clause is a claim about VS-4
			# Rule 1b, which only bites when the lord fields a corps of the
			# vassal's own colours. The backend says whether it does
			# (`wavering_regiments`, present only with THE_WAVERING_LINE_IS_
			# HONEST up); an old payload without the key keeps the old line.
			var drag = bool(v.get("wavering_regiments", true))
			if drag:
				bbcode += "   [color=#" + COLOR_AMBER + "]Wavering — their marshals drag their feet[/color]"
			else:
				bbcode += "   [color=#" + COLOR_AMBER + "]Wavering — no standing to petition[/color]"
		"disaffected":
			bbcode += "   [color=#" + Utils.COLOR_ERROR + "]Disaffected — refuses new calls to arms[/color]"
	bbcode += "\n"

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
		bbcode += "  Standing: [color=#" + standing_color + "]" + standing + "[/color]"
		if may_petition and v.has("next_petition_in"):
			var next_in = int(v.get("next_petition_in", 0))
			if next_in <= 0:
				bbcode += "  [color=#" + Utils.COLOR_GREY + "]· may petition at the turn's end[/color]"
			else:
				bbcode += "  [color=#" + Utils.COLOR_GREY + "]· next petition in " + str(next_in) + " turn" + ("s" if next_in != 1 else "") + "[/color]"
		bbcode += "\n"
	if v.has("bond"):
		var bond_text = _vassal_bond_text(v)
		if bond_text != "":
			bbcode += "  Bond: [color=#" + Utils.COLOR_INFO + "]" + bond_text + "[/color]\n"
	var remission_left = int(v.get("remission_left", 0))
	if remission_left > 0:
		bbcode += "  [color=#" + Utils.COLOR_GOLD + "]Tribute remitted: " + str(remission_left) + " collection" + ("s" if remission_left != 1 else "") + "[/color]\n"

	# ── Garrison lever (VP-D1) ──
	var capital = str(v.get("capital", ""))
	if v.get("garrison_present", false):
		bbcode += "  [color=#" + Utils.COLOR_SUCCESS + "]Garrisoned — our presence in " + capital + " steadies them (+" + str(int(v.get("garrison_bonus", 2))) + "/turn)[/color]\n"
	elif capital != "":
		bbcode += "  [color=#" + Utils.COLOR_GREY + "]No garrison — a corps in " + capital + " would add a standing +2/turn[/color]\n"

	# ── Standing subsidy (treaty gold_per_turn — a forecast term, so name it) ──
	var subsidy = int(v.get("subsidy_bonus", 0))
	if subsidy > 0:
		bbcode += "  [color=#" + Utils.COLOR_SUCCESS + "]Subsidized — treaty gold steadies them (+" + str(subsidy) + "/turn)[/color]\n"

	# ── Granted provinces (VS-3 provenance) ──
	var granted = v.get("granted_regions", [])
	if granted is Array and granted.size() > 0:
		var granted_strs = []
		for g in granted:
			granted_strs.append(str(g))
		bbcode += "  [color=#" + Utils.COLOR_GREY + "]Ceded to them: " + ", ".join(PackedStringArray(granted_strs)) + "[/color]\n"

	# ── Action chips (honest availability — the wizard's own gate rows) ──
	var actions = v.get("actions", [])
	if actions is Array and actions.size() > 0:
		for a in actions:
			bbcode += _format_vassal_action_row(a, v)
	elif actions_blocked:
		pass  # section-level notice already shown
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

func _format_vassal_action_row(a: Dictionary, v: Dictionary) -> String:
	var action_id = str(a.get("action", ""))
	if not _VASSAL_ACTION_LABELS.has(action_id):
		return ""
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
			terms = "+" + str(int(v.get("autonomy_up_gain", 10))) + " loyalty, they keep more income — " + cost_text
		"decrease_autonomy":
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
	var row = "  "
	if a.get("available", false):
		var meta = ""
		if action_id == "grant_region_to_vassal":
			meta = "vassal_cede:" + nation
		else:
			meta = "vassal:" + action_id + ":" + nation
		var chip_bg = "233043"
		var chip_text = Utils.COLOR_GOLD
		if action_id == "release_vassal":
			chip_text = Utils.COLOR_ERROR
		row += Utils.bb_button_chip(meta, label, chip_text, chip_bg)
		row += "  [color=#" + Utils.COLOR_GREY + "]" + terms + "[/color]"
	else:
		var reason = str(a.get("disabled_reason", ""))
		row += "[color=#" + Utils.COLOR_GREY + "]" + label + " — unavailable"
		if reason != "":
			row += ": " + reason
		row += "[/color]"
	return row + "\n"


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
	return Utils.COLOR_GREY


static func congress_severity_tint(severity: String) -> String:
	"""The clock line's tint — the backend decided the severity once
	(`congress.clock_severity`); the fall clock's tints, gold for the gate."""
	match severity:
		"critical":
			return Utils.COLOR_ERROR
		"warning":
			return Utils.COLOR_BATTLE
		"paused":
			return Utils.COLOR_DIMMED
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
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]═══ THE CONGRESS OF PARIS ═══[/color]\n"
	if not (c is Dictionary) or c.is_empty() or not _ctrue(c.get("armed", false)):
		bbcode += "[color=#" + Utils.COLOR_INFO + "]There is no Congress of Paris in this campaign — the rules of the ending are not authored here.[/color]\n"
		content_area.text = bbcode
		return
	var needed := _cint(c, "titled_needed")
	var turns := _cint(c, "turns")
	# R159: the screen names the mechanic it shows — in the payload's numbers.
	bbcode += "[color=#" + Utils.COLOR_DIMMED + "]Europe must RECOGNIZE the new order. With " + str(needed)
	bbcode += " titled provinces the Emperor may summon the great powers to Paris; each answers at every end turn, with its reason and its price, and the Congress sits "
	bbcode += Utils.plural(turns, "turn") + ". If on the last day every court recognizes, is shut out or is gone, and the hold never broke, the Imperial Peace is proclaimed.[/color]\n\n"
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
	content_area.text = bbcode


func _congress_gate_block(c: Dictionary) -> String:
	var out := "[color=#" + Utils.COLOR_HEADER + "]THE SUMMONS[/color]\n"
	var terms = c.get("gate_terms", [])
	if terms is Array:
		for t in terms:
			if not (t is Dictionary):
				continue
			var met := _ctrue(t.get("met", false))
			var mark: String = "✓" if met else "•"
			var col: String = Utils.COLOR_SUCCESS if met else Utils.COLOR_GREY
			out += "  [color=#" + col + "]" + mark + " " + _bb_safe(_cstr(t, "text")) + "[/color]\n"
	var cost := _cstr(c, "cost_text")
	if cost != "":
		out += "  [color=#" + Utils.COLOR_INFO + "]Cost: " + cost + " — once summoned, it cannot be recalled.[/color]\n"
	if _ctrue(c.get("available", false)):
		var command := _cstr(c, "command")
		out += "  [color=#" + Utils.COLOR_SUCCESS + "]The powers may be summoned — the Cabinet (F1), 'The Congress of Paris'"
		if command != "":
			out += ", or type '" + command + "'"
		out += ".[/color]\n"
	else:
		var why := _cstr(c, "unavailable_reason")
		if why != "":
			out += "  [color=#" + Utils.COLOR_GREY + "]Not yet: " + _bb_safe(why) + "[/color]\n"
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
			out += "    [color=#" + Utils.COLOR_GREY + "]• " + _bb_safe(_cstr(r, "text")) + "[/color]\n"
			shown_roads += 1
		if roads.size() > shown_roads:
			out += "    [color=#" + Utils.COLOR_GREY + "]… and " + str(roads.size() - shown_roads) + " more.[/color]\n"
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
			out += "  [color=#" + Utils.COLOR_GREY + "]The courts that would not sign: " + ", ".join(PackedStringArray(shown_r)) + ".[/color]\n"
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
	out += "[color=#" + Utils.COLOR_HEADER + "]THE HOLD[/color] [color=#" + Utils.COLOR_DIMMED + "]— every condition, at every end turn; one broken, and the Congress dissolves[/color]\n"
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
	out += "[cell][color=#" + Utils.COLOR_DIMMED + "]Day  [/color][/cell]"
	for d in range(1, turns + 1):
		var day_col: String = Utils.COLOR_GOLD if d == today else Utils.COLOR_DIMMED
		out += "[cell][color=#" + day_col + "] " + str(d) + " [/color][/cell]"
	out += "[cell][color=#" + Utils.COLOR_DIMMED + "]Hold  [/color][/cell]"
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
			out += "[cell][color=#" + Utils.COLOR_DIMMED + "] · [/color][/cell]"
	out += "[cell][color=#" + Utils.COLOR_DIMMED + "]Signed  [/color][/cell]"
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
	var out := "[color=#" + Utils.COLOR_HEADER + "]THE TABLE[/color] [color=#" + Utils.COLOR_DIMMED + "]— "
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
	var out := "  " + Utils.bb_flag(nation, 18)
	out += "[color=#" + Utils.COLOR_GOLD + "][b]" + display + "[/b][/color]"
	if seat != "" and seat != display:
		out += "  [color=#" + Utils.COLOR_GREY + "](" + seat + ")[/color]"
	out += "   [color=#" + congress_stance_color(stance) + "][b]" + stance + "[/b][/color]\n"
	var reason := _cstr(ct, "reason")
	if reason != "":
		out += "    [color=#" + Utils.COLOR_INFO + "]" + _bb_safe(reason) + "[/color]\n"
	var score = ct.get("score", null)
	if (score is int or score is float) and _cstr(ct, "by") == "formula":
		out += "    [color=#" + Utils.COLOR_GREY + "]Its reckoning: " + str(int(score)) + " — it signs at " + str(_cint(ct, "threshold")) + "[/color]\n"
	var price := _cstr(ct, "price")
	if price != "":
		out += "    [color=#" + Utils.COLOR_GREY + "]Price: " + _bb_safe(price) + "[/color]\n"
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
		out += "    [color=#" + Utils.COLOR_GREY + "]Refusing " + Utils.plural(_cint(ct, "refusing_turns"), "turn") + " — it will not march: " + _bb_safe(_cstr(ct, "march_blocker")) + ".[/color]\n"
	# The price's levers that are typed orders — the backend names the command
	# (`levers[].command`). Gold is laid at the table only while it sits.
	var orders: Array = []
	var levers = ct.get("levers", [])
	if levers is Array:
		for lv in levers:
			if not (lv is Dictionary):
				continue
			var order := _cstr(lv, "command")
			if order == "":
				continue
			if _cstr(lv, "key") == "sweetener" and not sitting:
				continue
			orders.append("'" + _bb_safe(order) + "'")
	if not orders.is_empty():
		out += "    [color=#" + Utils.COLOR_DIMMED + "]Type " + " or ".join(PackedStringArray(orders)) + ".[/color]\n"
	if stance != "GONE" and nation != "":
		var where: String = seat if seat != "" else display
		out += "    [url=congress_court:" + nation + "][color=#" + Utils.COLOR_GOLD + "]Open the Cabinet at " + where + " →[/color][/url]\n"
	return out + "\n"


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


func _on_content_meta_clicked(meta):
	var meta_key = str(meta)
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
				vassal_command.emit(command)
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
				bbcode += "      [color=#" + Utils.COLOR_GREY + "]+" + str(term_overflow) + " more terms[/color]\n"

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
				bbcode += "      [color=#" + Utils.COLOR_GREY + "]+" + str(ally_overflow) + " more participants — View all participants[/color]\n"

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
					warn_color = COLOR_RED
				bbcode += "      [color=#" + warn_color + "]• [" + sev.replace("_", " ") + "] " + code
				if detail != "":
					bbcode += " — " + detail
				bbcode += "[/color]\n"
			if overflow_warns is Array and overflow_warns.size() > 0:
				bbcode += "      [color=#" + Utils.COLOR_GREY + "]+" + str(overflow_warns.size()) + " more — View all concerns[/color]\n"

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
