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

# File-specific colors (not in Utils)
const COLOR_AMBER = "d9a520"
const COLOR_RED = "cd5c5c"

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
var _pulse_state: bool = false

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
	content_area.text = "[color=#" + Utils.COLOR_INFO + "]Loading diplomatic ledger...[/color]"
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
		content_area.text = "[color=#" + Utils.COLOR_ERROR + "]Failed to load diplomatic ledger.[/color]"
		return

	cached_data = response.get("ledger", {})
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
			_render_threat_coalition()
		3:
			_render_talleyrand()


# =============================================================================
# TAB 1: NATION OVERVIEW
# =============================================================================

func _render_nations():
	var nations = cached_data.get("nations", [])
	var bbcode = ""
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]═══ NATION OVERVIEW ═══[/color]\n\n"

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

		# N7: Relation trend arrow
		var trend = str(n.get("relation_trend", "stable"))
		var trend_arrow = " →"
		if trend == "rising":
			trend_arrow = " ↑"
		elif trend == "falling":
			trend_arrow = " ↓"
		rel_text += trend_arrow

		bbcode += "[color=#" + Utils.COLOR_GOLD + "][b]" + name + "[/b][/color]"
		bbcode += " — [color=#" + state_color + "]" + diplo_state + "[/color]"
		bbcode += "  Relation: [color=#" + rel_color + "]" + rel_text + "[/color]"

		# N4: Vassal eligibility
		var vassal_eligible = n.get("vassal_eligible", false)
		if vassal_eligible:
			bbcode += "  [color=#" + Utils.COLOR_GOLD + "]★ Vassalizable[/color]"
		bbcode += "\n"

		# Diplomat info
		var diplomat = n.get("diplomat")
		if diplomat != null and diplomat is Dictionary:
			var d_name = str(diplomat.get("name", "?"))
			var d_pers = str(diplomat.get("personality", "?"))
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
				ai_parts.append(ar_nation + " [color=#" + ar_state_color + "][" + ar_state + "][/color] — [color=#" + ar_desc_color + "]" + ar_descriptor + " (" + str(ar_relation) + ")[/color]")
			bbcode += "  AI Relations: " + ", ".join(PackedStringArray(ai_parts)) + "\n"

		# N2: War Score Breakdown (WAR only)
		var war_score = n.get("war_score_breakdown")
		if war_score != null and war_score is Dictionary:
			var total = int(war_score.get("total", 0))
			var ws_color = Utils.COLOR_SUCCESS if total > 0 else (COLOR_RED if total < 0 else Utils.COLOR_GREY)
			var ws_sign = "+" if total > 0 else ""
			bbcode += "  War Score: [color=#" + ws_color + "][" + ws_sign + str(total) + "][/color]  ("
			var ws_parts = []
			for ws_key in ["territory", "battles", "decisive", "capital"]:
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
	var current_turn = int(cached_data.get("current_turn", 0))
	var bbcode = ""
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]═══ ACTIVE TREATIES ═══[/color]\n\n"

	if treaties.size() == 0:
		bbcode += "[color=#" + Utils.COLOR_GREY + "]No active treaties.[/color]\n"
		content_area.text = bbcode
		return

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

		bbcode += "[color=#" + header_color + "]" + nation_a + "[/color]"
		bbcode += " [color=#" + Utils.COLOR_INFO + "]↔[/color] "
		bbcode += "[color=#" + header_color + "]" + nation_b + "[/color]"
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
				bbcode += "  Gold Flow: [color=#" + Utils.COLOR_GOLD + "]" + gpt_from + " → " + gpt_to + ": " + str(gpt_amount) + "g/turn[/color]\n"

		bbcode += "\n"

	content_area.text = bbcode


# =============================================================================
# TAB 3: THREAT & COALITION
# =============================================================================

func _render_threat_coalition():
	var tc = cached_data.get("threat_coalition", {})
	var bbcode = ""
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]COALITION THREAT[/color]\n"
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]────────────────[/color]\n"

	var threat_level = int(tc.get("threat_level", 0))
	var threat_tier = str(tc.get("threat_tier", "LOW"))

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
	bbcode += bar + "\n\n"

	# TH3: Threat sources this turn (with human-readable labels)
	var sources = tc.get("threat_sources_this_turn", [])
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
	var qualifying = tc.get("qualifying_nations", [])
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]Nations That Would Join Coalition:[/color]\n"
	if qualifying.size() == 0:
		bbcode += "  [color=#" + Utils.COLOR_GREY + "]None currently[/color]\n"
	else:
		var qual_strs = []
		for q in qualifying:
			qual_strs.append(str(q))
		bbcode += "  " + ", ".join(PackedStringArray(qual_strs)) + "\n"
	bbcode += "\n"

	# Coalition status
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]Coalition Status:[/color]\n"
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
		# TH2: Show coalition cooldown if active
		var coalition_cooldown = int(tc.get("coalition_cooldown", 0))
		if coalition_cooldown > 0:
			bbcode += "  [color=#" + Utils.COLOR_GREY + "]No coalition active. Post-dissolution cooldown: " + str(coalition_cooldown) + " turns.[/color]\n"
		else:
			bbcode += "  [color=#" + Utils.COLOR_GREY + "]No coalition active.[/color]\n"

	# TH4: Dissolution conditions
	bbcode += "\n[color=#" + Utils.COLOR_GREY + "]Coalition dissolves if threat falls below "
	bbcode += str(int(tc.get("dissolution_threat_threshold", 20)))
	bbcode += " or any member's war exhaustion exceeds "
	bbcode += str(int(tc.get("dissolution_war_exhaustion_limit", 80)))
	bbcode += ".[/color]\n"

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
		bbcode += ")\n"
	bbcode += "\n"

	# Current mission
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]CURRENT MISSION[/color]\n"
	var mission = t.get("active_mission")
	if mission == null or not (mission is Dictionary):
		bbcode += "  [color=#" + Utils.COLOR_GREY + "]Idle — no active diplomatic mission.[/color]\n"
	else:
		var m_type = str(mission.get("type", "?"))
		var m_target = str(mission.get("target", "?"))
		var m_duration = int(mission.get("duration", 0))
		var m_paused = mission.get("paused", false)
		var status = "Active"
		if m_paused:
			status = "Paused"
		bbcode += "  " + m_type.replace("_", " ").capitalize() + " → " + m_target + "\n"

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

		# TA5: Remaining turns
		var remaining = mission.get("remaining_turns")
		if remaining != null:
			bbcode += "  [color=#" + Utils.COLOR_GOLD + "]Completes in " + str(int(remaining)) + " turn(s)[/color]\n"
		else:
			bbcode += "  [color=#" + Utils.COLOR_GREY + "]Ongoing[/color]\n"
	bbcode += "\n"

	# Proposal in transit
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]PROPOSAL IN TRANSIT[/color]\n"
	var pit = t.get("proposal_in_transit")
	if pit == null or not (pit is Dictionary):
		bbcode += "  [color=#" + Utils.COLOR_GREY + "]None[/color]\n"
	else:
		var p_target = str(pit.get("target", "?"))
		var p_type = str(pit.get("type", "?"))
		var p_eta = int(pit.get("eta", 0))
		bbcode += "  To " + p_target + ": " + p_type.replace("_", " ").capitalize()
		bbcode += ", ETA: " + str(p_eta) + " turns\n"
	bbcode += "\n"

	# Pending envoys
	var pending_count = int(t.get("pending_envoy_count", 0))
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]PENDING ENVOYS[/color]\n"
	bbcode += "  " + str(pending_count) + " envoy(s) awaiting response\n\n"

	# Sabotage warnings
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]SABOTAGE WARNINGS[/color]\n"
	var warnings = t.get("sabotage_warnings", [])
	if warnings.size() == 0:
		bbcode += "  [color=#" + Utils.COLOR_GREY + "]None detected.[/color]\n"
	else:
		for w in warnings:
			if w is Dictionary:
				var w_target = str(w.get("target", "?"))
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
				var h_target = str(entry.get("target", ""))
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
