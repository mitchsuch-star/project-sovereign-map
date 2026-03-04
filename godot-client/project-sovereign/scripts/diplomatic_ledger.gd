extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Diplomatic Ledger Screen (Session 8B)
# =============================================================================
# 4-section sub-tabbed screen. CanvasLayer 50.
# Tabs: NATIONS, TREATIES, THREAT & COALITION, TALLEYRAND
# Number keys 1-4 switch sub-tabs (guarded by visible check).
# Pattern follows strategic_ledger.gd.
# =============================================================================

signal closed

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

# Color palette (duplicated across screens — consolidate during Map Renderer refactor)
const COLOR_GOLD = "d9c08c"
const COLOR_SUCCESS = "8fbc8f"
const COLOR_ERROR = "cd6b6b"
const COLOR_INFO = "a0a0a8"
const COLOR_BLUE = "6495ed"
const COLOR_ORANGE = "daa06d"
const COLOR_GREY = "808080"
const COLOR_HEADER = "B8860B"
const COLOR_AMBER = "d9a520"
const COLOR_RED = "cd5c5c"
const COLOR_GREEN = "8fbc8f"

# State
var current_tab: int = 0  # 0=nations, 1=treaties, 2=threat, 3=talleyrand
var cached_data: Dictionary = {}
var tab_buttons: Array = []

# Active tab style
var _active_tab_style: StyleBoxFlat = null
var _normal_tab_style: StyleBoxFlat = null

# Threat pulse timer for CRITICAL tier
var _critical_pulse_timer: Timer = null
var _critical_pulsing: bool = false

func _ready():
	close_button.pressed.connect(close_view)
	background_overlay.gui_input.connect(_on_overlay_input)

	tab_buttons = [nations_tab, treaties_tab, threat_tab, talleyrand_tab]
	for i in range(tab_buttons.size()):
		tab_buttons[i].pressed.connect(_on_tab_pressed.bind(i))

	# Build tab styles
	_active_tab_style = StyleBoxFlat.new()
	_active_tab_style.bg_color = Color(0.25, 0.22, 0.15, 1.0)
	_active_tab_style.border_width_bottom = 2
	_active_tab_style.border_color = Color(0.85, 0.75, 0.55, 1.0)
	_active_tab_style.content_margin_left = 6.0
	_active_tab_style.content_margin_right = 6.0
	_active_tab_style.content_margin_top = 3.0
	_active_tab_style.content_margin_bottom = 3.0

	_normal_tab_style = StyleBoxFlat.new()
	_normal_tab_style.bg_color = Color(0.12, 0.14, 0.18, 1.0)
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
	"""Handle number keys 1-4 for sub-tab switching. Only when visible."""
	if not visible:
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
			_:
				switched = false
		if switched:
			get_viewport().set_input_as_handled()


var _api_client_ref = null

func open(api_client):
	"""Fetch diplomatic ledger from backend and display it."""
	_api_client_ref = api_client
	content_area.text = "[color=#" + COLOR_INFO + "]Loading diplomatic ledger...[/color]"
	current_tab = 0
	show()
	_update_tab_highlights()
	api_client.get_diplomatic_ledger(_on_ledger_received)


func close_view():
	"""Hide the overlay and emit closed signal."""
	hide()
	cached_data = {}
	_stop_critical_pulse()
	closed.emit()


func _on_ledger_received(response):
	"""Cache data and render current tab."""
	if not visible:
		return

	if not response.get("success", false):
		content_area.text = "[color=#" + COLOR_ERROR + "]Failed to load diplomatic ledger.[/color]"
		return

	cached_data = response.get("ledger", {})
	if cached_data.is_empty():
		content_area.text = "[color=#" + COLOR_INFO + "]No diplomatic data available.[/color]"
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
			_render_threat_coalition()
		3:
			_render_talleyrand()


# =============================================================================
# TAB 1: NATION OVERVIEW
# =============================================================================

func _render_nations():
	var nations = cached_data.get("nations", [])
	var bbcode = ""
	bbcode += "[color=#" + COLOR_HEADER + "]═══ NATION OVERVIEW ═══[/color]\n\n"

	if nations.size() == 0:
		bbcode += "[color=#" + COLOR_INFO + "]No nations in diplomatic contact.[/color]\n"
		content_area.text = bbcode
		return

	for n in nations:
		var name = str(n.get("name", "?"))
		var diplo_state = str(n.get("diplomatic_state", "PEACE"))
		var relation = int(n.get("relation", 0))

		# Diplomatic state color
		var state_color = COLOR_INFO
		match diplo_state:
			"WAR":
				state_color = COLOR_ERROR
			"PEACE":
				state_color = COLOR_GREY
			"ALLIANCE":
				state_color = COLOR_SUCCESS
			"NON_AGGRESSION":
				state_color = COLOR_BLUE
			"OPEN_BORDERS":
				state_color = COLOR_BLUE

		# Relation color
		var rel_color = COLOR_INFO
		if relation < -50:
			rel_color = COLOR_ERROR
		elif relation > 50:
			rel_color = COLOR_SUCCESS

		var rel_sign = "+" if relation > 0 else ""

		bbcode += "[color=#" + COLOR_GOLD + "][b]" + name + "[/b][/color]"
		bbcode += " — [color=#" + state_color + "]" + diplo_state + "[/color]"
		bbcode += "  Relation: [color=#" + rel_color + "]" + rel_sign + str(relation) + "[/color]\n"

		# Diplomat info
		var diplomat = n.get("diplomat")
		if diplomat != null and diplomat is Dictionary:
			var d_name = str(diplomat.get("name", "?"))
			var d_pers = str(diplomat.get("personality", "?"))
			var d_skill = int(diplomat.get("skill", 0))
			bbcode += "  Diplomat: " + d_name + " (" + d_pers + ") — Skill " + str(d_skill) + "\n"
		else:
			bbcode += "  Diplomat: [color=#" + COLOR_GREY + "]None[/color]\n"

		# Regions + Army
		var regions = int(n.get("regions_controlled", 0))
		var army = str(n.get("army_strength", "Unknown"))
		bbcode += "  Regions: " + str(regions) + "   Army: " + army + "\n"

		# Treaties
		var treaties = n.get("active_treaties", [])
		if treaties.size() > 0:
			bbcode += "  Treaties: " + ", ".join(PackedStringArray(treaties)) + "\n"
		else:
			bbcode += "  Treaties: [color=#" + COLOR_GREY + "]None[/color]\n"

		bbcode += "\n"

	content_area.text = bbcode


# =============================================================================
# TAB 2: ACTIVE TREATIES
# =============================================================================

func _render_treaties():
	var treaties = cached_data.get("treaties", [])
	var bbcode = ""
	bbcode += "[color=#" + COLOR_HEADER + "]═══ ACTIVE TREATIES ═══[/color]\n\n"

	if treaties.size() == 0:
		bbcode += "[color=#" + COLOR_GREY + "]No active treaties.[/color]\n"
		content_area.text = bbcode
		return

	for t in treaties:
		var nation_a = str(t.get("nation_a", "?"))
		var nation_b = str(t.get("nation_b", "?"))
		var treaty_type = str(t.get("treaty_type", "unknown"))
		var clauses = t.get("clauses", [])
		var duration = t.get("duration", "permanent")
		var cancel_cost = int(t.get("cancel_cost", 1))

		bbcode += "[color=#" + COLOR_GOLD + "]" + nation_a + "[/color]"
		bbcode += " [color=#" + COLOR_INFO + "]↔[/color] "
		bbcode += "[color=#" + COLOR_GOLD + "]" + nation_b + "[/color]"
		bbcode += ": [b]" + treaty_type.replace("_", " ").capitalize() + "[/b]\n"

		# Clauses
		if clauses.size() > 0:
			var clause_strs = []
			for c in clauses:
				clause_strs.append(str(c))
			bbcode += "  Clauses: " + ", ".join(PackedStringArray(clause_strs)) + "\n"
		else:
			bbcode += "  Clauses: [color=#" + COLOR_GREY + "]None[/color]\n"

		# Duration
		var dur_str = ""
		if duration is int or duration is float:
			dur_str = str(int(duration)) + " turns"
		else:
			dur_str = str(duration)
		bbcode += "  Duration: " + dur_str + "   Cancel cost: " + str(cancel_cost) + " DP\n"

		bbcode += "\n"

	content_area.text = bbcode


# =============================================================================
# TAB 3: THREAT & COALITION
# =============================================================================

func _render_threat_coalition():
	var tc = cached_data.get("threat_coalition", {})
	var bbcode = ""
	bbcode += "[color=#" + COLOR_HEADER + "]COALITION THREAT[/color]\n"
	bbcode += "[color=#" + COLOR_HEADER + "]────────────────[/color]\n"

	var threat_level = int(tc.get("threat_level", 0))
	var threat_tier = str(tc.get("threat_tier", "LOW"))

	# Tier color
	var tier_color = COLOR_SUCCESS
	match threat_tier:
		"LOW":
			tier_color = COLOR_SUCCESS
		"MODERATE":
			tier_color = COLOR_AMBER
		"HIGH":
			tier_color = COLOR_RED
		"CRITICAL":
			tier_color = COLOR_RED
			_start_critical_pulse()

	bbcode += "Threat Level: [color=#" + tier_color + "]" + str(threat_level) + " / 100  [" + threat_tier + "][/color]\n"

	# Visual threat bar — 20 chars wide
	var filled = int(threat_level / 5)  # 0-20
	if filled > 20:
		filled = 20
	var empty = 20 - filled

	var bar_color = COLOR_SUCCESS
	if threat_level >= 60:
		bar_color = COLOR_RED
	elif threat_level >= 30:
		bar_color = COLOR_AMBER

	var bar = "[color=#" + bar_color + "]"
	for i in range(filled):
		bar += "█"
	bar += "[/color][color=#" + COLOR_GREY + "]"
	for i in range(empty):
		bar += "░"
	bar += "[/color]"
	bbcode += bar + "\n\n"

	# Threat sources this turn
	var sources = tc.get("threat_sources_this_turn", [])
	bbcode += "[color=#" + COLOR_HEADER + "]This Turn's Sources:[/color]\n"
	if sources.size() == 0:
		bbcode += "  [color=#" + COLOR_GREY + "]No new threats[/color]\n"
	else:
		for s in sources:
			bbcode += "  • " + str(s) + "\n"
	bbcode += "\n"

	# Qualifying nations
	var qualifying = tc.get("qualifying_nations", [])
	bbcode += "[color=#" + COLOR_HEADER + "]Nations That Would Join Coalition:[/color]\n"
	if qualifying.size() == 0:
		bbcode += "  [color=#" + COLOR_GREY + "]None currently[/color]\n"
	else:
		var qual_strs = []
		for q in qualifying:
			qual_strs.append(str(q))
		bbcode += "  " + ", ".join(PackedStringArray(qual_strs)) + "\n"
	bbcode += "\n"

	# Coalition status
	bbcode += "[color=#" + COLOR_HEADER + "]Coalition Status:[/color]\n"
	var coalition_brewing = tc.get("coalition_brewing", false)
	var brewing_turns = tc.get("brewing_turns_remaining")
	var active_coalition = tc.get("active_coalition")

	if active_coalition != null and active_coalition is Dictionary:
		var c_name = str(active_coalition.get("name", "Unknown"))
		var c_leader = str(active_coalition.get("leader", "?"))
		var c_posture = str(active_coalition.get("posture", "defensive"))
		bbcode += "  [color=#" + COLOR_RED + "]ACTIVE: " + c_name + " — Leader: " + c_leader + ", Posture: " + c_posture.capitalize() + "[/color]\n"
		bbcode += "  Combined Strength: " + str(active_coalition.get("combined_strength_display", "Unknown")) + "\n\n"

		# Per-member block
		var members = active_coalition.get("members", [])
		for mem in members:
			var m_nation = str(mem.get("nation", "?"))
			var m_strength = str(mem.get("strength_display", "?"))
			var m_we = int(mem.get("war_exhaustion", 0))

			# Mini WE bar (10 chars)
			var we_filled = int(m_we / 10)
			if we_filled > 10:
				we_filled = 10
			var we_empty = 10 - we_filled
			var we_bar = ""
			for i in range(we_filled):
				we_bar += "█"
			for i in range(we_empty):
				we_bar += "░"

			bbcode += "  • " + m_nation + ": " + m_strength + ", WE: " + str(m_we) + "/100 [" + we_bar + "]\n"
	elif coalition_brewing:
		var turns_str = ""
		if brewing_turns != null:
			turns_str = str(int(brewing_turns))
		else:
			turns_str = "?"
		bbcode += "  [color=#" + COLOR_AMBER + "]Brewing — " + turns_str + " turns until formation[/color]\n"
	else:
		bbcode += "  [color=#" + COLOR_GREY + "]No coalition active.[/color]\n"

	content_area.text = bbcode


# =============================================================================
# TAB 4: TALLEYRAND
# =============================================================================

func _render_talleyrand():
	var t = cached_data.get("talleyrand", {})
	var bbcode = ""

	var trust = int(t.get("trust", 0))
	var trust_label = str(t.get("trust_label", "Wary"))
	var skill = int(t.get("skill", 0))
	var dp_remaining = int(t.get("dp_remaining", 0))
	var dp_max = int(t.get("dp_max", 3))

	# Trust label color
	var trust_color = COLOR_INFO
	match trust_label:
		"Loyal":
			trust_color = COLOR_SUCCESS
		"Wary":
			trust_color = COLOR_AMBER
		"Suspicious":
			trust_color = COLOR_ORANGE
		"Treacherous":
			trust_color = COLOR_ERROR

	bbcode += "[color=#" + COLOR_HEADER + "]TALLEYRAND[/color] — [color=#" + trust_color + "]" + trust_label + "[/color]\n"
	bbcode += "Trust: [color=#" + trust_color + "]" + str(trust) + "[/color]/100"
	bbcode += "   Skill: " + str(skill)
	bbcode += "   DP: [color=#" + COLOR_GOLD + "]" + str(dp_remaining) + "/" + str(dp_max) + "[/color]\n\n"

	# Current mission
	bbcode += "[color=#" + COLOR_HEADER + "]CURRENT MISSION[/color]\n"
	var mission = t.get("active_mission")
	if mission == null or not (mission is Dictionary):
		bbcode += "  [color=#" + COLOR_GREY + "]Idle — no active diplomatic mission.[/color]\n"
	else:
		var m_type = str(mission.get("type", "?"))
		var m_target = str(mission.get("target", "?"))
		var m_duration = int(mission.get("duration", 0))
		var m_paused = mission.get("progress", false)
		var status = "Active"
		if m_paused:
			status = "Paused"
		bbcode += "  " + m_type.replace("_", " ").capitalize() + " → " + m_target
		bbcode += ", Duration: " + str(m_duration) + " turns"
		bbcode += ", Status: " + status + "\n"
	bbcode += "\n"

	# Proposal in transit
	bbcode += "[color=#" + COLOR_HEADER + "]PROPOSAL IN TRANSIT[/color]\n"
	var pit = t.get("proposal_in_transit")
	if pit == null or not (pit is Dictionary):
		bbcode += "  [color=#" + COLOR_GREY + "]None[/color]\n"
	else:
		var p_target = str(pit.get("target", "?"))
		var p_type = str(pit.get("type", "?"))
		var p_eta = int(pit.get("eta", 0))
		bbcode += "  To " + p_target + ": " + p_type.replace("_", " ").capitalize()
		bbcode += ", ETA: " + str(p_eta) + " turns\n"
	bbcode += "\n"

	# Pending envoys
	var pending_count = int(t.get("pending_envoy_count", 0))
	bbcode += "[color=#" + COLOR_HEADER + "]PENDING ENVOYS[/color]\n"
	bbcode += "  " + str(pending_count) + " envoy(s) awaiting response\n\n"

	# Sabotage warnings
	bbcode += "[color=#" + COLOR_HEADER + "]SABOTAGE WARNINGS[/color]\n"
	var warnings = t.get("sabotage_warnings", [])
	if warnings.size() == 0:
		bbcode += "  [color=#" + COLOR_GREY + "]None detected.[/color]\n"
	else:
		for w in warnings:
			if w is Dictionary:
				var w_target = str(w.get("target", "?"))
				var w_type = str(w.get("type", "?"))
				bbcode += "  [color=#" + COLOR_ERROR + "]WARNING: " + w_type + " targeting " + w_target + "[/color]\n"
			else:
				bbcode += "  [color=#" + COLOR_ERROR + "]" + str(w) + "[/color]\n"

	content_area.text = bbcode


# =============================================================================
# CRITICAL PULSE (flashing red for CRITICAL threat tier)
# =============================================================================

func _start_critical_pulse():
	if not _critical_pulsing:
		_critical_pulsing = true
		_critical_pulse_timer.start()


func _stop_critical_pulse():
	if _critical_pulsing:
		_critical_pulsing = false
		_critical_pulse_timer.stop()


func _on_critical_pulse():
	# Pulse the threat section text — handled by re-rendering with alternating color
	# For simplicity, just toggle content area modulate
	pass


# =============================================================================
# HELPERS
# =============================================================================

# TECH DEBT: _format_number() duplicated across screens.
func _format_number(n: int) -> String:
	"""Format number with comma separators (e.g. 80000 -> 80,000)."""
	var s = str(int(n))
	var result = ""
	var count = 0
	for i in range(s.length() - 1, -1, -1):
		if count > 0 and count % 3 == 0:
			result = "," + result
		result = s[i] + result
		count += 1
	return result


func _on_overlay_input(event):
	"""Click on dark overlay to close."""
	if event is InputEventMouseButton and event.pressed:
		close_view()
