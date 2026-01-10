extends Control

# =============================================================================
# PROJECT SOVEREIGN - Main UI Controller
# =============================================================================
# Handles command input, output display, and status updates
# Color scheme: Dark blue background, gold accents, cream text
# =============================================================================

# UI References - Header Status
@onready var turn_value = $BottomLeftUI/MainMargin/MainLayout/Header/HeaderMargin/HeaderContent/StatusSection/TurnDisplay/TurnValue
@onready var actions_value = $BottomLeftUI/MainMargin/MainLayout/Header/HeaderMargin/HeaderContent/StatusSection/ActionsDisplay/ActionsValue
@onready var gold_value = $BottomLeftUI/MainMargin/MainLayout/Header/HeaderMargin/HeaderContent/StatusSection/GoldDisplay/GoldValue

# UI References - Main Interface  
@onready var output_scroll = $BottomLeftUI/MainMargin/MainLayout/OutputScroll
@onready var output_display = $BottomLeftUI/MainMargin/MainLayout/OutputScroll/OutputDisplay
@onready var command_input = $BottomLeftUI/MainMargin/MainLayout/InputSection/CommandInput
@onready var send_button = $BottomLeftUI/MainMargin/MainLayout/InputSection/SendButton

# API Client
var api_client = null

# Game state tracking
var actions_remaining = 4
var max_actions = 4
var current_turn = 1
var max_turns = 40
var gold = 1200

# Color palette (Napoleonic theme)
const COLOR_GOLD = "d9c08c"        # Gold for titles, important text
const COLOR_COMMAND = "7eb8da"     # Light blue for player commands
const COLOR_SUCCESS = "8fbc8f"     # Soft green for success
const COLOR_ERROR = "cd6b6b"       # Muted red for errors
const COLOR_BATTLE = "daa06d"      # Orange/amber for battle results
const COLOR_INFO = "a0a0a8"        # Gray for system info
const COLOR_MARSHAL = "c9b8e0"     # Lavender for marshal responses
const COLOR_CONQUEST = "90d890"    # Bright green for conquests

# Message history limit (prevents infinite growth)
const MAX_MESSAGES = 100
var message_count = 0

func _ready():
	# Create API client
	api_client = load("res://scripts/api_client.gd").new()
	add_child(api_client)
	
	# Connect signals
	if not send_button.pressed.is_connected(_on_send_button_pressed):
		send_button.pressed.connect(_on_send_button_pressed)
	
	if not command_input.text_submitted.is_connected(_on_command_submitted):
		command_input.text_submitted.connect(_on_command_submitted)
	
	# Start disabled until connected
	set_input_enabled(false)
	
	# Welcome message
	_show_welcome()
	
	# Test connection after brief delay
	await get_tree().create_timer(0.5).timeout
	test_connection()

func _show_welcome():
	"""Display welcome message with proper formatting."""
	add_output("")
	add_output("[color=#" + COLOR_GOLD + "][b]═══════════════════════════════════════[/b][/color]")
	add_output("[color=#" + COLOR_GOLD + "][b]        IMPERIAL HEADQUARTERS[/b][/color]")
	add_output("[color=#" + COLOR_GOLD + "][b]═══════════════════════════════════════[/b][/color]")
	add_output("")
	add_output("[color=#" + COLOR_INFO + "]June 1815 — The Hundred Days Campaign[/color]")
	add_output("[color=#" + COLOR_INFO + "]You are Napoleon Bonaparte.[/color]")
	add_output("")

func test_connection():
	"""Test if backend is running."""
	add_output("[color=#" + COLOR_INFO + "]Establishing connection to headquarters...[/color]")
	api_client.test_connection(_on_connection_test)

func _on_connection_test(response):
	"""Handle connection test response."""
	if response.success:
		add_output("[color=#" + COLOR_SUCCESS + "]✓ Communications established![/color]")
		add_output("")
		
		# Update status from server
		if response.has("action_summary"):
			_update_status(response.action_summary)
		if response.has("gold"):
			gold = int(response.gold)
			_update_gold_display()
		
		# Show instructions
		add_output("[color=#" + COLOR_INFO + "]Your marshals await your orders, Sire.[/color]")
		add_output("")
		add_output("[color=#" + COLOR_INFO + "]Commands:[/color]")
		add_output("[color=#" + COLOR_INFO + "]  • \"Ney, attack Wellington\"[/color]")
		add_output("[color=#" + COLOR_INFO + "]  • \"scout Rhine\" or \"move to Belgium\"[/color]")
		add_output("[color=#" + COLOR_INFO + "]  • \"recruit\" or \"end turn\"[/color]")
		add_output("")
		_add_separator()
		
		set_input_enabled(true)
	else:
		add_output("[color=#" + COLOR_ERROR + "]✗ Cannot reach headquarters![/color]")
		add_output("[color=#" + COLOR_INFO + "]Start the Python server: python backend/main.py[/color]")
		add_output("")

func _on_send_button_pressed():
	"""Handle send button click."""
	_execute_command()

func _on_command_submitted(_text: String):
	"""Handle enter key in command input."""
	_execute_command()

func _execute_command():
	"""Execute the command in the input field."""
	var command = command_input.text.strip_edges()
	
	if command.is_empty():
		return
	
	# Display player command with prompt styling
	add_output("")
	add_output("[color=#" + COLOR_COMMAND + "]► " + command + "[/color]")
	
	# Clear input
	command_input.text = ""
	
	# Disable input while processing
	set_input_enabled(false)
	
	# Send to backend
	api_client.send_command(command, _on_command_result)

func _on_command_result(response):
	"""Handle command execution result."""
	# Re-enable input
	set_input_enabled(true)
	
	if response.success:
		# Update status displays
		if response.has("action_summary"):
			_update_status(response.action_summary)
		
		if response.has("game_state") and response.game_state.has("gold"):
			gold = int(response.game_state.gold)
			_update_gold_display()
		
		# Format and display result based on event type
		_display_result(response)
		
	else:
		add_output("[color=#" + COLOR_ERROR + "]" + response.message + "[/color]")
	
	add_output("")
	
	# Auto-focus input
	command_input.grab_focus()

func _display_result(response):
	"""Display result with appropriate formatting based on event type."""
	var message = response.message
	var events = response.get("events", [])
	var action_info = response.get("action_info", {})
	
	# Determine event type for coloring
	var event_type = ""
	if events.size() > 0:
		event_type = events[0].get("type", "")
	
	# Color based on event type
	match event_type:
		"battle":
			_display_battle_result(message, events[0], action_info)
		"conquest":
			add_output("[color=#" + COLOR_CONQUEST + "]⚑ " + message + "[/color]")
			_show_action_cost(action_info)
		"move":
			add_output("[color=#" + COLOR_SUCCESS + "]→ " + message + "[/color]")
			_show_action_cost(action_info)
		"scout":
			add_output("[color=#" + COLOR_INFO + "]👁 " + message + "[/color]")
			_show_action_cost(action_info)
		"recruit":
			add_output("[color=#" + COLOR_SUCCESS + "]+ " + message + "[/color]")
			_show_action_cost(action_info)
		"defend":
			add_output("[color=#" + COLOR_SUCCESS + "]⛨ " + message + "[/color]")
			_show_action_cost(action_info)
		"turn_end":
			_display_turn_change(events[0])
		_:
			add_output("[color=#" + COLOR_SUCCESS + "]" + message + "[/color]")
			_show_action_cost(action_info)
	
	# Check for turn advancement
	if action_info.get("turn_advanced", false):
		_display_turn_advance(action_info)

func _display_battle_result(message: String, event: Dictionary, action_info: Dictionary):
	"""Display battle results with dramatic formatting."""
	var outcome = event.get("outcome", "")
	var victor = event.get("victor", "")
	var enemy_destroyed = event.get("enemy_destroyed", false)
	var region_conquered = event.get("region_conquered", false)
	
	# Battle header
	add_output("[color=#" + COLOR_BATTLE + "]⚔ BATTLE ⚔[/color]")
	
	# Main result
	add_output("[color=#" + COLOR_BATTLE + "]" + message + "[/color]")
	
	# Special notifications
	if enemy_destroyed:
		add_output("[color=#" + COLOR_CONQUEST + "]   ★ Enemy army destroyed! ★[/color]")
	
	if region_conquered:
		var region_name = event.get("region_name", "territory")
		add_output("[color=#" + COLOR_CONQUEST + "]   ⚑ " + region_name + " captured! ⚑[/color]")
	
	_show_action_cost(action_info)

func _display_turn_change(event: Dictionary):
	"""Display turn end notification."""
	var old_turn = int(event.get("old_turn", 0))
	var new_turn = int(event.get("new_turn", 0))
	var income = int(event.get("income", 0))
	
	add_output("")
	add_output("[color=#" + COLOR_GOLD + "]═══════════════════════════════════════[/color]")
	add_output("[color=#" + COLOR_GOLD + "]         TURN " + str(int(new_turn)) + " BEGINS[/color]")
	add_output("[color=#" + COLOR_GOLD + "]═══════════════════════════════════════[/color]")
	add_output("[color=#" + COLOR_SUCCESS + "]Treasury: +" + str(int(income)) + " gold[/color]")
	add_output("[color=#" + COLOR_SUCCESS + "]Actions refreshed: " + str(int(max_actions)) + "/" + str(int(max_actions)) + "[/color]")
	add_output("")

func _display_turn_advance(action_info: Dictionary):
	"""Display automatic turn advancement when actions run out."""
	var new_turn = int(action_info.get("new_turn", current_turn + 1))
	add_output("")
	add_output("[color=#" + COLOR_GOLD + "]═══════════════════════════════════════[/color]")
	add_output("[color=#" + COLOR_GOLD + "]  Actions exhausted — Turn " + str(int(new_turn)) + " begins[/color]")
	add_output("[color=#" + COLOR_GOLD + "]═══════════════════════════════════════[/color]")
	add_output("")

func _show_action_cost(action_info: Dictionary):
	"""Show action point usage."""
	var cost = int(action_info.get("cost", 0))
	var remaining = int(action_info.get("remaining", actions_remaining))
	
	if cost > 0:
		add_output("[color=#" + COLOR_INFO + "]   [" + str(int(remaining)) + "/" + str(int(max_actions)) + " actions remaining][/color]")

func _update_status(action_summary: Dictionary):
	"""Update header status displays."""
	if action_summary.has("actions_remaining"):
		actions_remaining = int(action_summary.actions_remaining)
	
	if action_summary.has("max_actions"):
		max_actions = int(action_summary.max_actions)
	
	if action_summary.has("turn"):
		current_turn = int(action_summary.turn)
	
	if action_summary.has("max_turns"):
		max_turns = int(action_summary.max_turns)
	
	# Update displays - force integer conversion in strings
	turn_value.text = str(int(current_turn)) + "/" + str(int(max_turns))
	
	# Color actions based on remaining
	if actions_remaining <= 1:
		actions_value.add_theme_color_override("font_color", Color(0.8, 0.4, 0.4))  # Red when low
	elif actions_remaining <= 2:
		actions_value.add_theme_color_override("font_color", Color(0.9, 0.7, 0.3))  # Yellow when medium
	else:
		actions_value.add_theme_color_override("font_color", Color(0.4, 0.8, 0.4))  # Green when good
	
	actions_value.text = str(int(actions_remaining)) + "/" + str(int(max_actions))

func _update_gold_display():
	"""Update treasury display with formatting."""
	gold_value.text = _format_number(gold)

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

func _add_separator():
	"""Add a visual separator line."""
	add_output("[color=#" + COLOR_INFO + "]─────────────────────────────────────[/color]")

func add_output(text: String):
	"""Add text to output display with message limit."""
	message_count += 1
	
	# Trim old messages if over limit
	if message_count > MAX_MESSAGES:
		_trim_old_messages()
	
	output_display.append_text(text + "\n")
	
	# Ensure scroll to bottom
	await get_tree().process_frame
	output_scroll.scroll_vertical = output_scroll.get_v_scroll_bar().max_value

func _trim_old_messages():
	"""Remove oldest messages to prevent infinite growth."""
	var current_text = output_display.get_parsed_text()
	var lines = current_text.split("\n")
	
	# Keep last 75% of messages
	var keep_from = int(lines.size() * 0.25)
	var new_lines = lines.slice(keep_from)
	
	output_display.clear()
	output_display.append_text("[color=#" + COLOR_INFO + "][...earlier messages trimmed...][/color]\n\n")
	for line in new_lines:
		output_display.append_text(line + "\n")
	
	message_count = new_lines.size()

func set_input_enabled(enabled: bool):
	"""Enable or disable command input."""
	command_input.editable = enabled
	send_button.disabled = not enabled
	
	if enabled:
		command_input.grab_focus()
