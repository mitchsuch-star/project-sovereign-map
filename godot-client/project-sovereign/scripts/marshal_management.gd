extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Marshal Management Screen (Phase 6.5)
# =============================================================================
# Card-based read-only view of player marshals. CanvasLayer 50.
# Number keys 1-N jump to/highlight specific marshal.
# Pattern follows strategic_ledger.gd.
# =============================================================================

signal closed

# UI References — paths match scene tree
@onready var background_overlay = $BackgroundOverlay
@onready var close_button = $PanelContainer/VBoxContainer/HeaderRow/CloseButton
@onready var scroll_container = $PanelContainer/VBoxContainer/ScrollContainer
@onready var content_area = $PanelContainer/VBoxContainer/ScrollContainer/ContentArea

# File-specific colors (not in Utils)
const COLOR_DIM = "666670"
const COLOR_DEVOTED = "ffd700"

# State
var cached_data: Array = []

func _ready():
	close_button.pressed.connect(close_view)
	background_overlay.gui_input.connect(_on_overlay_input)
	hide()


func _input(event):
	"""Handle number keys 1-N to scroll to specific marshal."""
	if not visible:
		return
	if event is InputEventKey and event.pressed and not event.echo:
		var index = -1
		match event.keycode:
			KEY_1:
				index = 0
			KEY_2:
				index = 1
			KEY_3:
				index = 2
			KEY_4:
				index = 3
			KEY_5:
				index = 4
			KEY_6:
				index = 5
			KEY_7:
				index = 6
			KEY_8:
				index = 7
			KEY_9:
				index = 8
			_:
				return
		if index >= 0 and index < cached_data.size():
			# Scroll to marshal card — approximate position based on card height
			# TECH DEBT: 320px/card is hardcoded. Revisit if playtesting shows scroll misalignment.
			var scroll_target = index * 320
			scroll_container.scroll_vertical = scroll_target
			get_viewport().set_input_as_handled()


func open(api_client):
	"""Fetch marshal overview from backend and display it."""
	content_area.text = "[color=#" + Utils.COLOR_INFO + "]Loading marshal data...[/color]"
	show()
	api_client.get_marshal_overview(_on_data_received)


func close_view():
	"""Hide the overlay and emit closed signal."""
	hide()
	cached_data = []
	closed.emit()


func _on_data_received(response):
	"""Cache data and render all marshal cards."""
	if not visible:
		return

	if not response.get("success", false):
		content_area.text = "[color=#" + Utils.COLOR_ERROR + "]Failed to load marshal data.[/color]"
		return

	cached_data = response.get("marshals", [])
	if cached_data.size() == 0:
		content_area.text = "[color=#" + Utils.COLOR_INFO + "]No marshals available.[/color]"
		return

	_render_all_cards()


func _render_all_cards():
	"""Render all marshal cards as a vertical list."""
	var bbcode = ""

	for i in range(cached_data.size()):
		var m = cached_data[i]
		bbcode += _render_card(m, i)
		if i < cached_data.size() - 1:
			bbcode += "[color=#" + Utils.COLOR_GREY + "]────────────────────────────────────────[/color]\n\n"

	content_area.text = bbcode


func _render_card(m: Dictionary, index: int) -> String:
	"""Render a single marshal card."""
	var bbcode = ""

	# ═══════ HEADER ═══════
	var name = str(m.get("name", "?"))
	var unit_type = str(m.get("unit_type", "Infantry"))
	var nation = str(m.get("nation", "?"))
	var personality = str(m.get("personality", "?"))

	# Unit type badge color
	var type_color = Utils.COLOR_INFO
	match unit_type:
		"Cavalry":
			type_color = Utils.COLOR_ORANGE
		"Artillery":
			type_color = Utils.COLOR_ERROR

	var key_hint = "[" + str(index + 1) + "] "
	bbcode += "[color=#" + Utils.COLOR_GREY + "]" + key_hint + "[/color]"
	bbcode += "[color=#" + Utils.COLOR_GOLD + "]" + name + "[/color]"
	bbcode += "  [color=#" + type_color + "][" + unit_type + "][/color]"
	bbcode += "  [color=#" + Utils.COLOR_GREY + "]" + nation + "[/color]\n"

	# ═══════ BIOGRAPHY ═══════
	var bio = str(m.get("biography", ""))
	if bio != "":
		bbcode += "[color=#" + COLOR_DIM + "]" + bio + "[/color]\n"

	# ═══════ PERSONALITY & UNIT TYPE ═══════
	var pers_desc = str(m.get("personality_description", ""))
	if pers_desc != "":
		bbcode += "[color=#" + Utils.COLOR_INFO + "]" + pers_desc + "[/color]\n"
	var type_desc = str(m.get("unit_type_description", ""))
	if type_desc != "":
		bbcode += "[color=#" + Utils.COLOR_INFO + "]" + type_desc + "[/color]\n"

	bbcode += "\n"

	# ═══════ COMBAT STATS ═══════
	var strength = int(m.get("strength", 0))
	var starting = int(m.get("starting_strength", 0))
	var morale = int(m.get("morale", 100))
	var move_range = int(m.get("movement_range", 1))

	# Strength color based on losses
	var str_color = Utils.COLOR_INFO
	if starting > 0:
		var ratio = float(strength) / float(starting)
		if ratio < 0.3:
			str_color = Utils.COLOR_ERROR
		elif ratio < 0.6:
			str_color = Utils.COLOR_ORANGE

	bbcode += "  Strength: [color=#" + str_color + "]" + _format_number(strength) + "[/color]"
	bbcode += " / " + _format_number(starting)
	bbcode += "  Morale: " + _morale_colored(morale)
	bbcode += "  Range: " + str(move_range) + "\n"

	# Skills
	var skills = m.get("skills", {})
	bbcode += "  Skills: "
	var skill_parts = []
	for skill_name in ["shock", "defense", "tactical", "logistics", "administration", "command"]:
		var val = int(skills.get(skill_name, 5))
		skill_parts.append(_skill_colored(skill_name.substr(0, 3).to_upper(), val))
	bbcode += " ".join(skill_parts) + "\n"

	# ═══════ ABILITY (only shown if active/wired) ═══════
	var ab_name = str(m.get("ability_name", ""))
	var ab_effect = str(m.get("ability_effect", ""))
	var ab_active = m.get("ability_active", false)

	if ab_active and ab_name != "":
		bbcode += "  [color=#" + Utils.COLOR_GOLD + "]" + ab_name + "[/color]"
		if ab_effect != "":
			bbcode += "  [color=#" + Utils.COLOR_INFO + "]" + ab_effect + "[/color]"
		bbcode += "\n\n"

	# ═══════ TRUST & RECORD ═══════
	var trust_val = int(m.get("trust_value", 70))
	var trust_label = str(m.get("trust_label", "Neutral"))
	var vindication = int(m.get("vindication_score", 0))
	var won = int(m.get("battles_won", 0))
	var lost = int(m.get("battles_lost", 0))
	var overridden = int(m.get("orders_overridden", 0))

	bbcode += "  Trust: " + _trust_colored(trust_val, trust_label)
	bbcode += "  Vindication: " + _vindication_colored(vindication)
	bbcode += "  Record: " + str(won) + "W/" + str(lost) + "L"
	if overridden > 0:
		bbcode += "  [color=#" + Utils.COLOR_ORANGE + "]Overridden: " + str(overridden) + "x[/color]"
	bbcode += "\n"

	# ═══════ CURRENT STATUS ═══════
	var location = str(m.get("location", "?"))
	var stance = str(m.get("stance", "neutral"))

	bbcode += "  Location: " + location
	bbcode += "  Stance: " + _stance_colored(stance)

	# Status flags
	var flags = []
	if m.get("is_broken", false):
		flags.append("[color=#" + Utils.COLOR_ERROR + "]BROKEN (recovery: " + str(int(m.get("broken_recovery", 0))) + ")[/color]")
	if m.get("is_retreating", false):
		flags.append("[color=#" + Utils.COLOR_ERROR + "]RETREATING (stage: " + str(int(m.get("retreat_recovery", 0))) + ")[/color]")
	if m.get("is_fortified", false):
		var def_bonus = int(m.get("defense_bonus", 0))
		flags.append("[color=#" + Utils.COLOR_BLUE + "]FORTIFIED +" + str(def_bonus) + "%[/color]")
	if m.get("is_drilling", false):
		var drill_txt = "DRILLING"
		if m.get("drilling_locked", false):
			drill_txt = "DRILL LOCKED"
		var shock = int(m.get("shock_bonus", 0))
		if shock > 0:
			drill_txt += " (+" + str(shock * 10) + "% shock)"
		flags.append("[color=#" + Utils.COLOR_BLUE + "]" + drill_txt + "[/color]")
	if m.get("square_formation", false):
		flags.append("[color=#" + Utils.COLOR_GOLD + "]SQUARE (+5% def, cav -40%, arty +50% vuln)[/color]")
	if m.get("is_autonomous", false):
		var reason = str(m.get("autonomy_reason", ""))
		flags.append("[color=#" + Utils.COLOR_ORANGE + "]AUTONOMOUS" + (" (" + reason + ")" if reason != "" else "") + "[/color]")

	var idle = int(m.get("idle_turns", 0))
	if idle >= 2:
		flags.append("[color=#" + Utils.COLOR_GREY + "]IDLE " + str(idle) + " turns[/color]")

	if flags.size() > 0:
		bbcode += "\n  " + " | ".join(flags)

	# Strategic order
	var strat = m.get("strategic_order")
	if strat != null and strat is Dictionary:
		var cmd = str(strat.get("command_type", "?"))
		var target = str(strat.get("target", "?"))
		bbcode += "\n  [color=#" + Utils.COLOR_BLUE + "]Order: " + cmd + " → " + target + "[/color]"

	bbcode += "\n"

	# ═══════ UNIT SPECIFICS ═══════
	var specifics = []
	if m.get("cavalry", false):
		if m.get("counter_punch_available", false):
			specifics.append("[color=#" + Utils.COLOR_SUCCESS + "]Counter-Punch READY[/color]")
		if m.get("holding_position", false):
			specifics.append("[color=#" + Utils.COLOR_BLUE + "]Holding Position[/color]")
	if m.get("artillery", false):
		var bombards = int(m.get("bombardments_this_turn", 0))
		specifics.append("Bombardments: " + str(bombards) + "/2")
		if m.get("moved_this_turn", false):
			specifics.append("[color=#" + Utils.COLOR_ORANGE + "]Moved (cannot fire)[/color]")

	if specifics.size() > 0:
		bbcode += "  " + " | ".join(specifics) + "\n"

	# ═══════ RELATIONSHIPS ═══════
	var rels = m.get("relationships", [])
	if rels.size() > 0:
		var rel_parts = []
		for r in rels:
			var rname = str(r.get("name", "?"))
			var rval = int(r.get("value", 0))
			var rlabel = str(r.get("label", "Professional"))
			rel_parts.append(rname + ": " + _relationship_colored(rval, rlabel))
		bbcode += "  Relationships: " + ", ".join(rel_parts) + "\n"

	bbcode += "\n"
	return bbcode


# =============================================================================
# COLOR HELPERS
# =============================================================================

# TECH DEBT: _format_number() duplicated in dispatch_view.gd, strategic_ledger.gd,
# marshal_management.gd. Extract to shared utils.gd autoload during Map Renderer refactor.
func _format_number(n: int) -> String:
	"""Format number with comma separators."""
	var s = str(int(n))
	var result = ""
	var count = 0
	for i in range(s.length() - 1, -1, -1):
		if count > 0 and count % 3 == 0:
			result = "," + result
		result = s[i] + result
		count += 1
	return result


func _morale_colored(morale: int) -> String:
	var color = Utils.COLOR_INFO
	if morale < 40:
		color = Utils.COLOR_ERROR
	elif morale < 60:
		color = Utils.COLOR_ORANGE
	return "[color=#" + color + "]" + str(morale) + "%[/color]"


func _skill_colored(label: String, val: int) -> String:
	var color = Utils.COLOR_INFO
	if val >= 8:
		color = Utils.COLOR_SUCCESS
	elif val <= 3:
		color = Utils.COLOR_ERROR
	elif val <= 5:
		color = Utils.COLOR_GREY
	return label + ":[color=#" + color + "]" + str(val) + "[/color]"


func _trust_colored(val: int, label: String) -> String:
	var color = Utils.COLOR_INFO
	if val < 30:
		color = Utils.COLOR_ERROR
	elif val < 55:
		color = Utils.COLOR_ORANGE
	elif val >= 80:
		color = Utils.COLOR_SUCCESS
	return "[color=#" + color + "]" + str(val) + " (" + label + ")[/color]"


func _vindication_colored(val: int) -> String:
	var color = Utils.COLOR_INFO
	if val > 0:
		color = Utils.COLOR_SUCCESS
	elif val < 0:
		color = Utils.COLOR_ERROR
	var sign = "+" if val > 0 else ""
	return "[color=#" + color + "]" + sign + str(val) + "[/color]"


func _stance_colored(stance: String) -> String:
	var color = Utils.COLOR_INFO
	match stance:
		"aggressive":
			color = Utils.COLOR_ERROR
		"defensive":
			color = Utils.COLOR_BLUE
	return "[color=#" + color + "]" + stance.capitalize() + "[/color]"


func _relationship_colored(val: int, label: String) -> String:
	var color = Utils.COLOR_GREY
	match val:
		-2:
			color = Utils.COLOR_ERROR
		-1:
			color = Utils.COLOR_ORANGE
		1:
			color = Utils.COLOR_SUCCESS
		2:
			color = COLOR_DEVOTED
	var sign = "+" if val > 0 else ""
	return "[color=#" + color + "]" + label + " (" + sign + str(val) + ")[/color]"


func _on_overlay_input(event):
	"""Click on dark overlay to close."""
	if event is InputEventMouseButton and event.pressed:
		close_view()
