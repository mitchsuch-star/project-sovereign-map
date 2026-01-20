extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Enemy Phase Dialog
# =============================================================================
# Displays enemy actions after player ends their turn.
# Shows full battle details: casualties, outcomes, conquests.
# Player must click Continue to proceed.
# =============================================================================

signal dismissed

# UI References
@onready var panel_container = $PanelContainer
@onready var title_label = $PanelContainer/VBoxContainer/TitleLabel
@onready var content_label = $PanelContainer/VBoxContainer/ContentScroll/ContentLabel
@onready var continue_button = $PanelContainer/VBoxContainer/ContinueButton

# Color palette (matching main.gd)
const COLOR_GOLD = "d9c08c"
const COLOR_TEXT = "eeeeee"
const COLOR_ERROR = "cd5c5c"
const COLOR_SUCCESS = "8fbc8f"
const COLOR_BATTLE = "daa06d"
const COLOR_INFO = "a0a0a8"
const COLOR_NATION_BRITAIN = "cd5c5c"  # Red for Britain
const COLOR_NATION_PRUSSIA = "6495ed"  # Blue for Prussia
const COLOR_NATION_AUSTRIA = "f0e68c"  # Yellow for Austria
const COLOR_CONQUEST = "90d890"

func _ready():
	# Connect button signal
	continue_button.pressed.connect(_on_continue_pressed)

	# Hide by default
	hide()

func show_enemy_phase(enemy_phase: Dictionary, turn: int):
	"""Display enemy phase with full battle details."""

	# Set title
	title_label.text = "ENEMY PHASE - Turn %d" % turn

	# Build content
	var content = ""

	var nations = enemy_phase.get("nations", {})
	var total_actions = enemy_phase.get("total_actions", 0)

	if total_actions == 0:
		content = "[color=#" + COLOR_INFO + "]No enemy actions this turn.[/color]"
	else:
		for nation in nations:
			var nation_data = nations[nation]
			var action_count = nation_data.get("action_count", 0)

			# Nation header with colored name
			var nation_color = _get_nation_color(nation)
			content += "[color=#" + nation_color + "][b]" + nation.to_upper() + "[/b][/color]\n"
			content += "[color=#" + COLOR_INFO + "]" + "-".repeat(40) + "[/color]\n"

			# Process each action
			var actions = nation_data.get("actions", [])
			for action in actions:
				content += _format_action(action)

			content += "\n"

	# Set content
	content_label.text = content

	# Show the dialog
	show()

func _format_action(action: Dictionary) -> String:
	"""Format a single action with full details."""
	var result = ""

	var ai_action = action.get("ai_action", {})
	var marshal_name = ai_action.get("marshal", "Unknown")
	var action_type = ai_action.get("action", "unknown")
	var target = ai_action.get("target", "")

	# Basic action line
	var action_str = marshal_name + " "
	match action_type:
		"attack":
			action_str += "attacks " + target
		"move":
			action_str += "moves to " + target
		"defend":
			action_str += "defends"
		"fortify":
			action_str += "fortifies position"
		"drill":
			action_str += "drills troops"
		"stance_change":
			action_str += "changes stance to " + target
		"retreat":
			action_str += "retreats to " + target
		"wait":
			action_str += "holds position"
		_:
			action_str += action_type
			if target:
				action_str += " " + target

	result += "[color=#" + COLOR_TEXT + "]- " + action_str + "[/color]\n"

	# Check for battle events
	var events = action.get("events", [])
	for event in events:
		if event.get("type") == "battle":
			result += _format_battle(event)
		elif event.get("type") == "conquest":
			var region = event.get("region", "territory")
			result += "[color=#" + COLOR_CONQUEST + "]    Region captured: " + region + "[/color]\n"

	return result

func _format_battle(event: Dictionary) -> String:
	"""Format battle details."""
	var result = ""

	var attacker = event.get("attacker", {})
	var defender = event.get("defender", {})
	var outcome = event.get("outcome", "unknown")
	var victor = event.get("victor", null)

	var attacker_name = attacker.get("name", "Unknown")
	var attacker_casualties = attacker.get("casualties", 0)
	var attacker_remaining = attacker.get("remaining", 0)
	var attacker_morale = attacker.get("morale", 0)

	var defender_name = defender.get("name", "Unknown")
	var defender_casualties = defender.get("casualties", 0)
	var defender_remaining = defender.get("remaining", 0)
	var defender_morale = defender.get("morale", 0)

	# Battle header
	result += "[color=#" + COLOR_BATTLE + "]    BATTLE: " + attacker_name + " vs " + defender_name + "[/color]\n"

	# Casualties
	result += "[color=#" + COLOR_INFO + "]    " + attacker_name + ": "
	result += _format_number(attacker_casualties) + " casualties, "
	result += _format_number(attacker_remaining) + " remaining[/color]\n"

	result += "[color=#" + COLOR_INFO + "]    " + defender_name + ": "
	result += _format_number(defender_casualties) + " casualties, "
	result += _format_number(defender_remaining) + " remaining[/color]\n"

	# Outcome
	var outcome_text = _get_outcome_text(outcome)
	var outcome_color = COLOR_INFO
	if victor:
		outcome_color = COLOR_SUCCESS if _is_player_marshal(defender_name) else COLOR_ERROR

	result += "[color=#" + outcome_color + "]    Result: " + outcome_text
	if victor:
		result += " (" + victor + " victorious)"
	result += "[/color]\n"

	# Check for enemy destroyed
	if event.get("enemy_destroyed", false):
		result += "[color=#" + COLOR_CONQUEST + "]    ARMY DESTROYED![/color]\n"

	# Check for region conquered
	if event.get("region_conquered", false):
		var region = event.get("region_name", "territory")
		result += "[color=#" + COLOR_CONQUEST + "]    " + region + " CAPTURED![/color]\n"

	# Check for forced retreat
	if attacker.get("forced_retreat", false):
		result += "[color=#" + COLOR_ERROR + "]    " + attacker_name + " forced to retreat![/color]\n"
	if defender.get("forced_retreat", false):
		result += "[color=#" + COLOR_ERROR + "]    " + defender_name + " forced to retreat![/color]\n"

	return result

func _get_outcome_text(outcome: String) -> String:
	"""Convert outcome code to readable text."""
	match outcome:
		"attacker_victory":
			return "Decisive attacker victory"
		"defender_victory":
			return "Decisive defender victory"
		"attacker_tactical_victory":
			return "Attacker tactical victory"
		"defender_tactical_victory":
			return "Defender tactical victory"
		"stalemate":
			return "Bloody stalemate"
		_:
			return outcome.replace("_", " ").capitalize()

func _get_nation_color(nation: String) -> String:
	"""Get color for nation name."""
	match nation.to_lower():
		"britain":
			return COLOR_NATION_BRITAIN
		"prussia":
			return COLOR_NATION_PRUSSIA
		"austria":
			return COLOR_NATION_AUSTRIA
		_:
			return COLOR_TEXT

func _is_player_marshal(name: String) -> bool:
	"""Check if marshal belongs to player (France)."""
	var player_marshals = ["Ney", "Davout", "Grouchy"]
	return name in player_marshals

func _format_number(num: int) -> String:
	"""Format number with comma separators."""
	var s = str(num)
	var result = ""
	var count = 0
	for i in range(s.length() - 1, -1, -1):
		if count > 0 and count % 3 == 0:
			result = "," + result
		result = s[i] + result
		count += 1
	return result

func _on_continue_pressed():
	"""Handle continue button press."""
	hide()
	dismissed.emit()
