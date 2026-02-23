extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Strategic Ledger Screen (Session B)
# =============================================================================
# 5-section sub-tabbed screen. CanvasLayer 50.
# Tabs: FORCES, TERRITORIES, ECONOMY, INTELLIGENCE, MANPOWER
# Number keys 1-5 switch sub-tabs (guarded by visible check).
# =============================================================================

signal closed

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

# Color palette (duplicated across dispatch_view.gd, strategic_ledger.gd,
# marshal_management.gd — consolidate into shared utils.gd during Map Renderer refactor)
const COLOR_GOLD = "d9c08c"
const COLOR_SUCCESS = "8fbc8f"
const COLOR_ERROR = "cd6b6b"
const COLOR_INFO = "a0a0a8"
const COLOR_BLUE = "6495ed"
const COLOR_ORANGE = "daa06d"
const COLOR_GREY = "808080"
const COLOR_HEADER = "B8860B"

# State
var current_tab: int = 0  # 0=forces, 1=territories, 2=economy, 3=intel, 4=manpower
var cached_data: Dictionary = {}
var tab_buttons: Array = []

# Active tab style
var _active_tab_style: StyleBoxFlat = null
var _normal_tab_style: StyleBoxFlat = null

func _ready():
	close_button.pressed.connect(close_view)
	background_overlay.gui_input.connect(_on_overlay_input)

	tab_buttons = [forces_tab, territories_tab, economy_tab, intel_tab, manpower_tab]
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

	hide()


func _input(event):
	"""Handle number keys 1-5 for sub-tab switching. Only when visible."""
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
			KEY_5:
				_switch_tab(4)
			_:
				switched = false
		if switched:
			get_viewport().set_input_as_handled()


func open(api_client):
	"""Fetch ledger from backend and display it."""
	content_area.text = "[color=#" + COLOR_INFO + "]Loading ledger...[/color]"
	current_tab = 0
	show()
	_update_tab_highlights()
	api_client.get_ledger(_on_ledger_received)


func close_view():
	"""Hide the overlay and emit closed signal."""
	hide()
	cached_data = {}
	closed.emit()


func _on_ledger_received(response):
	"""Cache data and render current tab."""
	if not visible:
		return

	if not response.get("success", false):
		content_area.text = "[color=#" + COLOR_ERROR + "]Failed to load ledger.[/color]"
		return

	cached_data = response.get("ledger", {})
	if cached_data.is_empty():
		content_area.text = "[color=#" + COLOR_INFO + "]No ledger data available.[/color]"
		return

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


# =============================================================================
# TAB RENDERERS
# =============================================================================

func _render_forces():
	var forces = cached_data.get("forces", [])
	var bbcode = ""
	bbcode += "[color=#" + COLOR_HEADER + "]═══ FORCES ═══[/color]\n\n"

	if forces.size() == 0:
		bbcode += "[color=#" + COLOR_INFO + "]No marshals available.[/color]\n"
		content_area.text = bbcode
		return

	for f in forces:
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

		# Name + type tag
		var type_tag = "[" + unit_type.substr(0, 3).to_upper() + "]"
		bbcode += "[color=#" + COLOR_GOLD + "]" + name + " " + type_tag + "[/color]\n"

		# Status with color coding
		var status_color = COLOR_INFO
		match status:
			"broken", "retreating":
				status_color = COLOR_ERROR
			"drilling":
				status_color = COLOR_BLUE
			"idle":
				status_color = COLOR_GREY

		bbcode += "  Status: [color=#" + status_color + "]" + status + "[/color]"
		bbcode += "  Location: " + loc + "\n"
		bbcode += "  Strength: " + _format_number(strength)
		bbcode += "  Stance: " + stance + "\n"

		# Trust + morale with color thresholds
		var trust_color = COLOR_INFO
		if trust < 30:
			trust_color = COLOR_ERROR
		elif trust < 55:
			trust_color = COLOR_ORANGE

		var morale_color = COLOR_INFO
		if morale < 40:
			morale_color = COLOR_ERROR
		elif morale < 60:
			morale_color = COLOR_ORANGE

		bbcode += "  Trust: [color=#" + trust_color + "]" + str(trust) + "[/color]"
		bbcode += "  Morale: [color=#" + morale_color + "]" + str(morale) + "%[/color]"
		bbcode += "  W/L: " + str(won) + "/" + str(lost) + "\n"

		# Strategic order
		if strat != "None":
			bbcode += "  Order: " + strat + "\n"

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
			bbcode += "  [color=#" + COLOR_ORANGE + "]" + " | ".join(flag_parts) + "[/color]\n"

		bbcode += "\n"

	content_area.text = bbcode


func _render_territories():
	var territories = cached_data.get("territories", [])
	var bbcode = ""
	bbcode += "[color=#" + COLOR_HEADER + "]═══ TERRITORIES ═══[/color]\n\n"

	if territories.size() == 0:
		bbcode += "[color=#" + COLOR_INFO + "]No territories controlled.[/color]\n"
		content_area.text = bbcode
		return

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

		bbcode += "[color=#" + COLOR_GOLD + "]" + name + "[/color]"
		bbcode += " [" + rtype.replace("_", " ") + ", " + terrain.replace("_", " ") + "]\n"

		bbcode += "  Income: " + str(income) + "g"
		bbcode += "  Stability: " + str(stability) + "%"
		if war_dmg > 0:
			bbcode += "  Damage: " + str(war_dmg) + "%"
		bbcode += "\n"

		# Supply status
		var supply_color = COLOR_INFO
		if supply_status == "Over capacity":
			supply_color = COLOR_ERROR
		bbcode += "  Supply: [color=#" + supply_color + "]" + supply_status + "[/color]"
		bbcode += " (" + str(occupants) + " marshals, cap " + _format_number(supply_cap) + ")"
		if garrison > 0:
			bbcode += "  Garrison: " + _format_number(garrison)
		bbcode += "\n"

		# Buildings
		if buildings.size() > 0:
			var bld_parts = []
			for b in buildings:
				var bname = str(b.get("name", "?"))
				var bstatus = str(b.get("status", "built"))
				if bstatus == "built":
					bld_parts.append(bname)
				elif bstatus == "damaged":
					bld_parts.append("[color=#" + COLOR_ERROR + "]" + bname + " (damaged)[/color]")
				else:
					bld_parts.append("[color=#" + COLOR_BLUE + "]" + bname + " (" + bstatus + ")[/color]")
			bbcode += "  Buildings: " + ", ".join(bld_parts) + "\n"

		bbcode += "\n"

	content_area.text = bbcode


func _render_economy():
	var econ = cached_data.get("economy", {})
	var bbcode = ""
	bbcode += "[color=#" + COLOR_HEADER + "]═══ ECONOMY ═══[/color]\n\n"

	var treasury = int(econ.get("treasury", 0))
	var income = int(econ.get("income", 0))
	var upkeep = int(econ.get("upkeep", 0))
	var net = int(econ.get("net", 0))
	var bankruptcy = int(econ.get("bankruptcy_turns", 0))

	bbcode += "  Treasury: " + _format_number(treasury) + "g\n"
	bbcode += "  Income:   +" + str(income) + "g\n"
	bbcode += "  Upkeep:   -" + str(upkeep) + "g\n"

	var net_color = COLOR_SUCCESS if net >= 0 else COLOR_ERROR
	var net_sign = "+" if net >= 0 else ""
	bbcode += "  Net:      [color=#" + net_color + "]" + net_sign + str(net) + "g[/color]\n"

	if bankruptcy > 0:
		bbcode += "  [color=#" + COLOR_ERROR + "]BANKRUPT — " + str(bankruptcy) + " turn(s)[/color]\n"

	# Income breakdown
	var breakdown = econ.get("income_breakdown", [])
	if breakdown.size() > 0:
		bbcode += "\n[color=#" + COLOR_HEADER + "]Income by Region[/color]\n"
		for entry in breakdown:
			var rname = str(entry.get("region", "?"))
			var rincome = int(entry.get("income", 0))
			var rtype = str(entry.get("type", "town"))
			bbcode += "  " + rname + " (" + rtype.replace("_", " ") + "): " + str(rincome) + "g\n"

	# Construction
	var queue = econ.get("construction_queue", [])
	if queue.size() > 0:
		bbcode += "\n[color=#" + COLOR_HEADER + "]Under Construction[/color]\n"
		for item in queue:
			var cregion = str(item.get("region", "?"))
			var cbuilding = str(item.get("building", "?"))
			var cturns = int(item.get("turns_remaining", 0))
			bbcode += "  " + cregion + ": " + cbuilding + " (" + str(cturns) + " turns)\n"

	content_area.text = bbcode


func _render_intel():
	var intel_data = cached_data.get("intel", {})
	var bbcode = ""
	bbcode += "[color=#" + COLOR_HEADER + "]═══ INTELLIGENCE ═══[/color]\n\n"

	var enemies = intel_data.get("known_enemies", [])
	var unknown_count = int(intel_data.get("unknown_region_count", 0))

	if enemies.size() == 0:
		bbcode += "[color=#" + COLOR_INFO + "]No enemy forces in observation range.[/color]\n"
	else:
		bbcode += "[color=#" + COLOR_HEADER + "]Known Enemy Forces[/color]\n"
		for e in enemies:
			var ename = str(e.get("name", "?"))
			var enation = str(e.get("nation", "?"))
			var eloc = str(e.get("location", "?"))
			var estr = str(e.get("strength_display", "?"))
			var evis = str(e.get("visibility", "unknown"))

			var vis_color = COLOR_INFO
			var vis_label = ""
			match evis:
				"full":
					vis_color = COLOR_SUCCESS
					vis_label = "[confirmed]"
				"partial":
					vis_color = COLOR_INFO
					vis_label = "[partial]"
				"stale":
					vis_color = COLOR_ORANGE
					vis_label = "[stale]"
				"last_known":
					vis_color = COLOR_ERROR
					vis_label = "[last known]"

			bbcode += "  " + ename + " (" + enation + ") at " + eloc + " — " + estr
			bbcode += " [color=#" + vis_color + "]" + vis_label + "[/color]\n"

	# Nation summaries
	var summaries = intel_data.get("nation_summaries", [])
	if summaries.size() > 0:
		bbcode += "\n[color=#" + COLOR_HEADER + "]Nation Summary[/color]\n"
		for s in summaries:
			var sname = str(s.get("nation", "?"))
			var smarshals = int(s.get("known_marshals", 0))
			var sstrength = int(s.get("estimated_strength", 0))
			var sregions = int(s.get("regions_controlled", 0))
			bbcode += "  " + sname + ": " + str(smarshals) + " marshals spotted"
			bbcode += ", ~" + _format_number(sstrength) + " est. strength"
			bbcode += ", " + str(sregions) + " regions\n"

	if unknown_count > 0:
		bbcode += "\n[color=#" + COLOR_GREY + "]" + str(unknown_count) + " region(s) with no intel.[/color]\n"

	content_area.text = bbcode


func _render_manpower():
	var mp = cached_data.get("manpower", {})
	var bbcode = ""
	bbcode += "[color=#" + COLOR_HEADER + "]═══ MANPOWER ═══[/color]\n\n"

	for pool_type in ["infantry", "cavalry", "artillery"]:
		var pool = mp.get(pool_type, {})
		var current = int(pool.get("current", 0))
		var max_val = int(pool.get("max", 0))
		var regen = int(pool.get("regen_rate", 0))
		var recruit_amt = int(pool.get("recruit_amount", 0))
		var recruit_cost = int(pool.get("recruit_base_cost", 0))
		var cost_note = str(pool.get("cost_note", ""))
		var turns_full = int(pool.get("turns_until_full", 0))

		bbcode += "[color=#" + COLOR_GOLD + "]" + pool_type.to_upper() + "[/color]\n"

		# Pool bar with color coding
		var pool_color = COLOR_INFO
		if current == 0:
			pool_color = COLOR_ERROR
		elif current < recruit_amt:
			pool_color = COLOR_ORANGE

		bbcode += "  Pool: [color=#" + pool_color + "]" + _format_number(current) + "[/color]"
		bbcode += " / " + _format_number(max_val) + "\n"
		bbcode += "  Regen: +" + _format_number(regen) + "/turn"
		if turns_full == 0:
			bbcode += " (full)\n"
		elif turns_full == -1:
			bbcode += " (no regen)\n"
		else:
			bbcode += " (" + str(turns_full) + " turns to full)\n"

		bbcode += "  Recruit: " + _format_number(recruit_amt) + " troops for " + str(recruit_cost) + "g"
		if cost_note != "":
			bbcode += " — " + cost_note
		bbcode += "\n\n"

	content_area.text = bbcode


# =============================================================================
# HELPERS
# =============================================================================

# TECH DEBT: _format_number() duplicated in dispatch_view.gd, strategic_ledger.gd,
# marshal_management.gd. Extract to shared utils.gd autoload during Map Renderer refactor.
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
