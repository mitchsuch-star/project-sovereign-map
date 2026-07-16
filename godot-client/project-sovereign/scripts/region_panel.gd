extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Region Action Panel (UI-6)
# =============================================================================
# The map's provinces finally answer a click. Non-modal side panel
# (CanvasLayer 26 — beside the war HUD's 25, below every screen/modal) that
# renders the clicked province from the map node's OWN fog-filtered data
# (region_full_data / region_visibility / region_marshals / region_garrisons
# — no extra fetch, no fog leak) plus context action chips:
#   - own province:      [Recruit Infantry] [Build Depot]
#   - foreign controller: [Negotiate with X] → the F1 wizard at that court
#   - own marshals here:  [Fortify]/[Unfortify] [Drill] per marshal
# Chips send the SAME typed commands a player would type — the executor owns
# every gate (AP, gold, objections); a refused chip reports like a typed
# refusal in the terminal. Display-only, Golden Rule 6 clean.
# =============================================================================

signal region_command(command: String)
signal negotiate_requested(nation: String)
signal closed

@onready var panel_container = $PanelContainer
@onready var title_label = $PanelContainer/VBoxContainer/HeaderRow/TitleLabel
@onready var close_button = $PanelContainer/VBoxContainer/HeaderRow/CloseButton
@onready var content_area = $PanelContainer/VBoxContainer/ContentArea

const _CHIP_BG = "233043"
# The whole client plays France (1805 campaign); dispatch/ledger make the
# same assumption.
const _PLAYER_NATION = "France"

var _region: String = ""
var _map_node = null


func _ready():
	close_button.pressed.connect(close_panel)
	Utils.apply_icon_only_button(close_button, Utils.ICON_PHOSPHOR + "x.svg")
	content_area.meta_clicked.connect(_on_meta_clicked)
	hide()


func show_region(region_name: String, map_node) -> void:
	"""Open (or retarget) the panel for a clicked province."""
	if region_name == "" or map_node == null:
		return
	_region = region_name
	_map_node = map_node
	_render()
	show()


func refresh_if_open() -> void:
	"""Re-render from the map node's current data after a chip command lands
	(the map itself refreshes from every response's game_state.map_data)."""
	if visible and _region != "" and _map_node != null:
		_render()


func close_panel() -> void:
	hide()
	_region = ""
	closed.emit()


func _on_meta_clicked(meta):
	var meta_str = str(meta)
	if meta_str.begins_with("order:"):
		# "order:<verb>:<MarshalName>" → "<Name>, <verb>" (typed-command echo)
		var parts = meta_str.split(":")
		if parts.size() == 3 and str(parts[2]) != "":
			region_command.emit(str(parts[2]) + ", " + str(parts[1]))
	elif meta_str.begins_with("do:"):
		# The chip carries its full typed command — the same string a player
		# would type; the executor owns every gate.
		var command = meta_str.substr("do:".length())
		if command != "":
			region_command.emit(command)
	elif meta_str.begins_with("negotiate:"):
		var nation = meta_str.substr("negotiate:".length())
		if nation != "":
			negotiate_requested.emit(nation)


func _render() -> void:
	var data: Dictionary = _map_node.region_full_data.get(_region, {})
	var visibility = str(_map_node.region_visibility.get(_region, "unknown"))
	var controller_raw = data.get("controller", "Neutral")
	var controller = str(controller_raw) if controller_raw != null else "Neutral"

	title_label.text = _region
	var bbcode = ""

	# ── Controller + terrain ──
	bbcode += Utils.bb_flag(controller, 15)
	bbcode += "[color=#" + Utils.COLOR_GOLD + "][b]" + Utils.display_nation_name(controller) + "[/b][/color]"
	var region_type = str(data.get("region_type", ""))
	var terrain = str(data.get("terrain", ""))
	if region_type != "" or terrain != "":
		bbcode += "  [color=#" + Utils.COLOR_GREY + "]" + region_type.replace("_", " ").capitalize()
		if terrain != "":
			bbcode += " · " + terrain.replace("_", " ").capitalize()
		bbcode += "[/color]"
	bbcode += "\n"

	# ── Fog-honest economy block ──
	if visibility == "unknown" or visibility == "last_known":
		var intel_note = "No intelligence" if visibility == "unknown" else "Last known (outdated)"
		bbcode += "[color=#" + Utils.COLOR_GREY + "]" + intel_note + " — scout or advance to learn more.[/color]\n"
	else:
		if visibility == "partial":
			bbcode += "[color=#" + Utils.COLOR_INFO + "]Intel: Partial (reports only)[/color]\n"
		elif visibility == "stale":
			bbcode += "[color=#" + Utils.COLOR_ORANGE + "]Intel: Stale (outdated)[/color]\n"
		var effective_income = int(data.get("effective_income", 0))
		var stability = int(data.get("stability", 100))
		bbcode += "Income: [color=#" + Utils.COLOR_GOLD + "]" + str(effective_income) + "g[/color]"
		bbcode += "   Stability: " + str(stability) + "%"
		bbcode += "   Supply: " + Utils.format_number(int(data.get("supply_capacity", 0))) + "\n"
		var garrison_info = _map_node.region_garrisons.get(_region, null)
		if garrison_info != null:
			var g_strength = int(garrison_info.get("strength", 0))
			var g_text = "Present (unknown strength)" if g_strength == -1 else Utils.format_number(g_strength)
			bbcode += "Garrison: " + g_text + "\n"
		var buildings = data.get("buildings", [])
		if buildings is Array and buildings.size() > 0:
			var b_names = []
			for b in buildings:
				b_names.append(str(b.get("type", "?")).replace("_", " ").capitalize())
			bbcode += "Buildings: " + ", ".join(PackedStringArray(b_names)) + "\n"

	# ── Forces present ──
	var marshals = _map_node.region_marshals.get(_region, [])
	var enemy_names = []
	if marshals is Array:
		for em in marshals:
			if str(em.get("nation", "")) != _PLAYER_NATION:
				enemy_names.append(str(em.get("name", "")))
	if marshals is Array and marshals.size() > 0:
		bbcode += "\n[color=#" + Utils.COLOR_HEADER + "]FORCES PRESENT[/color]\n"
		for m in marshals:
			bbcode += _format_marshal_row(m, enemy_names)

	# ── Context actions ──
	var action_rows = []
	if controller == _PLAYER_NATION:
		# Recruit — all three arms (the executor gates gold/pools/AP).
		var recruit_chips = ""
		for arm in ["infantry", "cavalry", "artillery"]:
			recruit_chips += Utils.bb_button_chip("do:recruit " + arm + " in " + _region, arm.capitalize(), Utils.COLOR_GOLD, _CHIP_BG) + " "
		action_rows.append("  Recruit: " + recruit_chips)

		# Build — every missing building while a slot is free (slot math from
		# the fog-filtered payload; towns/rural report 0 slots so the row
		# hides itself). Watchtowers ride their own field, slot-exempt.
		var buildings = data.get("buildings", [])
		var used_slots = buildings.size() if buildings is Array else 0
		if data.get("building_under_construction") != null:
			used_slots += 1
		var max_slots = int(data.get("max_building_slots", 0))
		var build_chips = ""
		if max_slots > used_slots:
			for def in _BUILD_CHIP_DEFS:
				if not _region_has_building(data, str(def[0])):
					build_chips += Utils.bb_button_chip("do:" + str(def[2]) % _region, str(def[1]), Utils.COLOR_GOLD, _CHIP_BG) + " "
		if str(data.get("watchtower", "none")) == "none":
			build_chips += Utils.bb_button_chip("do:build watchtower in " + _region, "Watchtower", Utils.COLOR_GOLD, _CHIP_BG) + " "
		if build_chips != "":
			action_rows.append("  Build: " + build_chips)

		# Repair — only when the payload shows damage.
		var needs_repair = str(data.get("watchtower", "")) == "damaged"
		if buildings is Array:
			for b in buildings:
				if b is Dictionary and b.get("damaged", false):
					needs_repair = true
		if needs_repair:
			action_rows.append("  " + Utils.bb_button_chip("do:repair buildings in " + _region, "Repair", Utils.COLOR_WARNING, _CHIP_BG)
				+ "  [color=#" + Utils.COLOR_GREY + "]restore damaged works[/color]")
	elif controller != "Neutral" and controller != "" and visibility != "unknown":
		action_rows.append("  " + Utils.bb_button_chip("negotiate:" + controller, "Negotiate with " + Utils.display_nation_name(controller), Utils.COLOR_COMMAND, _CHIP_BG))
	if action_rows.size() > 0:
		bbcode += "\n[color=#" + Utils.COLOR_HEADER + "]ACTIONS[/color]\n"
		for row in action_rows:
			bbcode += row + "\n"

	content_area.text = bbcode


# Build chip catalog: backend BUILDING_TYPES key → chip label → the typed
# command (the executor's _extract_building_type keys off these words).
const _BUILD_CHIP_DEFS = [
	["supply_depot", "Depot", "build depot in %s"],
	["fortification", "Fort", "build fort in %s"],
	["training_ground", "Training Ground", "build training ground in %s"],
	["market", "Market", "build market in %s"],
	["stables", "Stables", "build stables in %s"],
]


func _format_marshal_row(m: Dictionary, enemy_names: Array) -> String:
	var m_name = str(m.get("name", "?"))
	var m_nation = str(m.get("nation", ""))
	var m_strength = int(m.get("strength", 0))
	var row = "  "
	var nation_color = Utils.COLOR_TEXT if m_nation == _PLAYER_NATION else Utils.COLOR_ERROR
	row += "[color=#" + nation_color + "]" + m_name + "[/color]"
	if m_strength > 0:
		row += " [color=#" + Utils.COLOR_GREY + "](" + Utils.format_number(m_strength) + ")[/color]"
	if m_nation == _PLAYER_NATION:
		# Order chips — mirror the Generals-card gating: nothing for a
		# broken/retreating marshal. The map summary carries tactical_state
		# (flat bools: fortified/retreating/broken/drilling) for PLAYER
		# marshals only, fog-safe.
		var tactical = m.get("tactical_state", {})
		if tactical is Dictionary and not tactical.is_empty():
			var retreating = bool(tactical.get("retreating", false))
			var broken = bool(tactical.get("broken", false))
			if not retreating and not broken:
				if bool(tactical.get("fortified", false)):
					row += "  " + Utils.bb_button_chip("order:unfortify:" + m_name, "Unfortify", Utils.COLOR_COMMAND, _CHIP_BG)
				else:
					row += "  " + Utils.bb_button_chip("order:fortify:" + m_name, "Fortify", Utils.COLOR_COMMAND, _CHIP_BG)
				if not bool(tactical.get("drilling", false)):
					row += "  " + Utils.bb_button_chip("order:drill:" + m_name, "Drill", Utils.COLOR_COMMAND, _CHIP_BG)
				row += "  " + Utils.bb_button_chip("order:scout:" + m_name, "Scout", Utils.COLOR_COMMAND, _CHIP_BG)
				# Attack chips — only enemies the fog actually shows here
				# (enemy marshals ride region_marshals at FULL visibility
				# only), capped so a stacked province stays readable.
				for i in range(mini(enemy_names.size(), 2)):
					var enemy = str(enemy_names[i])
					if enemy != "":
						row += "  " + Utils.bb_button_chip("do:" + m_name + ", attack " + enemy, "Attack " + enemy, Utils.COLOR_ERROR, _CHIP_BG)
	return row + "\n"


func _region_has_building(data: Dictionary, building_type: String) -> bool:
	var buildings = data.get("buildings", [])
	if not buildings is Array:
		return false
	for b in buildings:
		if b is Dictionary and str(b.get("type", "")) == building_type:
			return true
	var construction = data.get("building_under_construction", null)
	if construction is Dictionary and str(construction.get("type", "")) == building_type:
		return true
	return false
