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
@onready var end_turn_button = $BottomLeftUI/MainMargin/MainLayout/InputSection/EndTurnButton

# Map reference
@onready var map_area = $MapArea

# Objection Dialog
var objection_dialog = null

# Redemption Dialog
var redemption_dialog = null

# Enemy Phase Dialog
var enemy_phase_dialog = null
var pending_enemy_phase_response = null  # Store response to check game_over after dismissal

# Glorious Charge Dialog (Phase 3 Cavalry Recklessness)
var glorious_charge_dialog = null

# API Client
var api_client = null

# Game state tracking
var actions_remaining = 4
var max_actions = 4
var current_turn = 1
var max_turns = 40
var gold = 1200
var pending_redemption = false  # True when awaiting redemption choice

# Command history (up/down arrow navigation)
var command_history: Array = []
var history_index: int = -1  # -1 means "new command mode"
const MAX_HISTORY = 10

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

	# Load and setup Objection Dialog
	print("🔧 Loading ObjectionDialog scene...")
	var dialog_scene = load("res://scenes/objection_dialog.tscn")
	if dialog_scene == null:
		push_error("❌ FAILED to load objection_dialog.tscn!")
		print("❌ FAILED to load objection_dialog.tscn!")
	else:
		print("✓ Scene loaded, instantiating...")
		objection_dialog = dialog_scene.instantiate()
		if objection_dialog == null:
			push_error("❌ FAILED to instantiate ObjectionDialog!")
			print("❌ FAILED to instantiate ObjectionDialog!")
		else:
			print("✓ Dialog instantiated, adding to tree...")
			add_child(objection_dialog)
			objection_dialog.choice_made.connect(_on_objection_choice_made)
			print("✓ ObjectionDialog ready! Node: ", objection_dialog.name)
			print("  In tree: ", objection_dialog.is_inside_tree())
			print("  Visible: ", objection_dialog.visible)

	# Load and setup Redemption Dialog
	print("🔧 Loading RedemptionDialog scene...")
	var redemption_scene = load("res://scenes/redemption_dialog.tscn")
	if redemption_scene == null:
		push_error("❌ FAILED to load redemption_dialog.tscn!")
		print("❌ FAILED to load redemption_dialog.tscn!")
	else:
		print("✓ Redemption scene loaded, instantiating...")
		redemption_dialog = redemption_scene.instantiate()
		if redemption_dialog == null:
			push_error("❌ FAILED to instantiate RedemptionDialog!")
			print("❌ FAILED to instantiate RedemptionDialog!")
		else:
			print("✓ Redemption dialog instantiated, adding to tree...")
			add_child(redemption_dialog)
			redemption_dialog.choice_made.connect(_on_redemption_choice_made)
			print("✓ RedemptionDialog ready!")

	# Load and setup Enemy Phase Dialog
	print("🔧 Loading EnemyPhaseDialog scene...")
	var enemy_phase_scene = load("res://scenes/enemy_phase_dialog.tscn")
	if enemy_phase_scene == null:
		push_error("❌ FAILED to load enemy_phase_dialog.tscn!")
		print("❌ FAILED to load enemy_phase_dialog.tscn!")
	else:
		print("✓ Enemy phase scene loaded, instantiating...")
		enemy_phase_dialog = enemy_phase_scene.instantiate()
		if enemy_phase_dialog == null:
			push_error("❌ FAILED to instantiate EnemyPhaseDialog!")
			print("❌ FAILED to instantiate EnemyPhaseDialog!")
		else:
			print("✓ Enemy phase dialog instantiated, adding to tree...")
			add_child(enemy_phase_dialog)
			enemy_phase_dialog.dismissed.connect(_on_enemy_phase_dismissed)
			print("✓ EnemyPhaseDialog ready!")

	# Load and setup Glorious Charge Dialog (Phase 3 Cavalry Recklessness)
	print("🔧 Loading GloriousChargeDialog scene...")
	var glorious_charge_scene = load("res://scenes/glorious_charge_dialog.tscn")
	if glorious_charge_scene == null:
		push_error("❌ FAILED to load glorious_charge_dialog.tscn!")
		print("❌ FAILED to load glorious_charge_dialog.tscn!")
	else:
		print("✓ Glorious charge scene loaded, instantiating...")
		glorious_charge_dialog = glorious_charge_scene.instantiate()
		if glorious_charge_dialog == null:
			push_error("❌ FAILED to instantiate GloriousChargeDialog!")
			print("❌ FAILED to instantiate GloriousChargeDialog!")
		else:
			print("✓ Glorious charge dialog instantiated, adding to tree...")
			add_child(glorious_charge_dialog)
			glorious_charge_dialog.choice_made.connect(_on_glorious_charge_choice_made)
			print("✓ GloriousChargeDialog ready!")

	# Connect signals
	if not send_button.pressed.is_connected(_on_send_button_pressed):
		send_button.pressed.connect(_on_send_button_pressed)

	if not command_input.text_submitted.is_connected(_on_command_submitted):
		command_input.text_submitted.connect(_on_command_submitted)

	if not end_turn_button.pressed.is_connected(_on_end_turn_pressed):
		end_turn_button.pressed.connect(_on_end_turn_pressed)

	if not command_input.gui_input.is_connected(_on_command_input_gui_input):
		command_input.gui_input.connect(_on_command_input_gui_input)

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

		# Update map with initial state
		if response.has("game_state") and response.game_state.has("map_data"):
			print("MAIN: Connection test - map_data found, updating map")
			print("MAIN: map_data keys: ", response.game_state.map_data.keys())
			map_area.update_all_regions(response.game_state.map_data)
		else:
			print("⚠️  MAIN: Connection test - NO map_data in response!")
			if response.has("game_state"):
				print("     game_state keys: ", response.game_state.keys())

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

func _on_command_input_gui_input(event):
	"""Handle special keys in command input."""
	if event is InputEventKey and event.pressed:
		if event.keycode == KEY_UP:
			_history_previous()
			command_input.accept_event()  # Consume event, prevent camera movement
		elif event.keycode == KEY_DOWN:
			_history_next()
			command_input.accept_event()  # Consume event, prevent camera movement
		elif event.keycode == KEY_ESCAPE:
			command_input.release_focus()  # Unfocus to allow camera controls
			command_input.accept_event()

func _history_previous():
	"""Navigate to previous command in history (up arrow)."""
	if command_history.is_empty():
		return

	if history_index == -1:
		# Start from most recent
		history_index = command_history.size() - 1
	elif history_index > 0:
		# Go further back
		history_index -= 1
	# else: already at oldest, stay there

	command_input.text = command_history[history_index]
	command_input.caret_column = command_input.text.length()

func _history_next():
	"""Navigate to next command in history (down arrow)."""
	if history_index == -1:
		# Already in new command mode
		return

	if history_index < command_history.size() - 1:
		# Go forward in history
		history_index += 1
		command_input.text = command_history[history_index]
		command_input.caret_column = command_input.text.length()
	else:
		# At newest, return to new command mode (clear)
		history_index = -1
		command_input.text = ""

func _add_to_history(command: String):
	"""Add command to history if valid."""
	if command.is_empty():
		return

	# Don't add if same as last command
	if not command_history.is_empty() and command_history.back() == command:
		return

	command_history.append(command)

	# Trim to max size
	while command_history.size() > MAX_HISTORY:
		command_history.pop_front()

	# Reset to new command mode
	history_index = -1

func _on_end_turn_pressed():
	"""Handle End Turn button click."""
	_execute_end_turn()

func _unhandled_input(event):
	"""Handle hotkeys when command input is not focused."""
	# E key for End Turn (only when not typing in command input)
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_E:
			# Don't trigger if command input has focus
			if not command_input.has_focus() and end_turn_button.visible and not end_turn_button.disabled:
				_execute_end_turn()
				get_viewport().set_input_as_handled()

func _execute_end_turn():
	"""Execute end turn command."""
	# Add to history
	_add_to_history("end turn")

	# Display the command
	add_output("")
	add_output("[color=#" + COLOR_COMMAND + "]► end turn[/color]")

	# Disable input while processing
	set_input_enabled(false)

	# Send to backend
	api_client.send_command("end turn", _on_command_result)

func _execute_command():
	"""Execute the command in the input field."""
	var command = command_input.text.strip_edges()

	if command.is_empty():
		return

	# Add to history before clearing
	_add_to_history(command)

	# Display player command with prompt styling
	add_output("")
	add_output("[color=#" + COLOR_COMMAND + "]► " + command + "[/color]")

	# Clear input
	command_input.text = ""

	# ════════════════════════════════════════════════════════════
	# CHECK FOR REDEMPTION COMMAND: Handle redemption choices
	# ════════════════════════════════════════════════════════════
	var redemption_choices = ["grant_autonomy", "dismiss", "demand_obedience"]
	if command.to_lower() in redemption_choices:
		print("REDEMPTION COMMAND DETECTED: ", command)
		set_input_enabled(false)
		api_client.send_redemption_response(command.to_lower(), _on_redemption_response)
		return

	# Disable input while processing
	set_input_enabled(false)

	# Send to backend
	api_client.send_command(command, _on_command_result)

func _on_command_result(response):
	"""Handle command execution result."""
	# ═══════════════════════════════════════════════════════════
	# DEBUG TRACE: Exact step-by-step debugging
	# ═══════════════════════════════════════════════════════════
	print("\n" + "=".repeat(60))
	print("1. GOT RESPONSE: ", response)
	print("=".repeat(60))
	print("2. HAS 'state' key: ", response.has("state"))
	print("2b. HAS 'awaiting_player_choice' key: ", response.has("awaiting_player_choice"))
	if response.has("state"):
		print("3. STATE VALUE: ", response.state)
		print("3b. STATE == 'awaiting_player_choice': ", response.state == "awaiting_player_choice")
	print("3c. response.success: ", response.get("success", false))
	print("=".repeat(60) + "\n")

	# Check for marshal objection FIRST (before re-enabling input)
	# The backend returns state: "awaiting_player_choice"
	var is_objection = response.get("success", false) and response.has("state") and response.state == "awaiting_player_choice"
	print("4. IS_OBJECTION CHECK RESULT: ", is_objection)

	if is_objection:
		print("5. OBJECTION DETECTED - About to show dialog")
		print("6. DIALOG NODE: ", objection_dialog)
		print("7. DIALOG IN TREE: ", objection_dialog.is_inside_tree() if objection_dialog else "NULL")
		print("8. DIALOG VISIBLE BEFORE: ", objection_dialog.visible if objection_dialog else "NULL")
		_show_objection_dialog(response)
		return  # Don't re-enable input or continue processing
	else:
		print("5. No objection - continuing normal flow")

	# Check for Glorious Charge popup (Phase 3 Cavalry Recklessness)
	# This happens when a reckless cavalry marshal at recklessness 3 tries to attack
	print("GLORIOUS_CHARGE CHECK:")
	print("  response.has('pending_glorious_charge'): ", response.has("pending_glorious_charge"))
	if response.has("pending_glorious_charge"):
		print("  response.pending_glorious_charge VALUE: ", response.pending_glorious_charge)

	if response.has("pending_glorious_charge") and response.pending_glorious_charge:
		print(">>> GLORIOUS CHARGE CONDITION MET - calling _show_glorious_charge_dialog()")
		print(">>> glorious_charge_dialog is: ", glorious_charge_dialog)
		print(">>> glorious_charge_dialog == null: ", glorious_charge_dialog == null)
		_show_glorious_charge_dialog(response)
		return  # Don't re-enable input until choice made

	# Re-enable input
	set_input_enabled(true)

	if response.success:
		# Update status displays
		if response.has("action_summary"):
			_update_status(response.action_summary)

		if response.has("game_state") and response.game_state.has("gold"):
			gold = int(response.game_state.gold)
			_update_gold_display()

		# Update map with latest state
		if response.has("game_state") and response.game_state.has("map_data"):
			print("MAIN: Command result - map_data found, updating map")
			print("MAIN: Received map_data with ", response.game_state.map_data.keys().size(), " regions")
			map_area.update_all_regions(response.game_state.map_data)
		else:
			print("⚠️  MAIN: Command result - NO map_data in response!")
			if response.has("game_state"):
				print("     game_state keys: ", response.game_state.keys())

		# Format and display result based on event type
		_display_result(response)

		# Check for enemy phase (from end_turn)
		if response.has("enemy_phase") and response.enemy_phase.get("total_actions", 0) > 0:
			print("ENEMY PHASE DETECTED - showing dialog")
			set_input_enabled(false)  # Disable input until dismissed
			var turn = current_turn
			if response.has("action_summary"):
				turn = int(response.action_summary.get("turn", current_turn))
			pending_enemy_phase_response = response  # Store to check game_over after dismiss
			_show_enemy_phase_dialog(response.enemy_phase, turn)
			return  # Don't re-enable input until dialog dismissed

		# Check for game over
		if response.has("game_state") and response.game_state.has("game_over"):
			if response.game_state.game_over:
				_show_game_over_screen(response.game_state)
				return  # Don't auto-focus input

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
		var event = events[0]
		if event.get("marshal_switched", false):
			# Split message at double newline
			var parts = message.split("\n\n", true, 1)
			if parts.size() == 2:
				 # Color explanation differently
				add_output("[color=#" + COLOR_INFO + "]" + parts[0] + "[/color]")
				add_output("")
				message = parts[1]  # Rest of message
	
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

	# Battle header - use battle_name if available
	var battle_name = event.get("battle_name", "BATTLE")
	add_output("[color=#" + COLOR_BATTLE + "]⚔ " + battle_name + " ⚔[/color]")
	
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

func _show_game_over_screen(game_state: Dictionary):
	"""Display dramatic game over screen with final statistics."""
	# Disable input permanently
	set_input_enabled(false)

	# Add spacing for dramatic effect
	add_output("")
	add_output("")

	# Dramatic separator
	add_output("[color=#" + COLOR_GOLD + "]═══════════════════════════════════════[/color]")
	add_output("[color=#" + COLOR_GOLD + "]═══════════════════════════════════════[/color]")
	add_output("")

	# Victory or defeat title
	var victory_status = game_state.get("victory", "defeat")
	if victory_status == "victory":
		add_output("[center][color=#" + COLOR_GOLD + "][b][font_size=28]⚜ VICTOIRE! ⚜[/font_size][/b][/color][/center]")
		add_output("")
		add_output("[center][color=#" + COLOR_SUCCESS + "]The Empire Triumphant![/color][/center]")
		add_output("")
		add_output("[color=#" + COLOR_INFO + "]Europe bends the knee before the French Eagle.[/color]")
		add_output("[color=#" + COLOR_INFO + "]Your marshals have conquered all who opposed them.[/color]")
		add_output("[color=#" + COLOR_INFO + "]History will remember this as the height of Imperial glory![/color]")
	else:
		add_output("[center][color=#" + COLOR_ERROR + "][b][font_size=28]⚔ DÉFAITE ⚔[/font_size][/b][/color][/center]")
		add_output("")
		add_output("[center][color=#" + COLOR_ERROR + "]The Empire Has Fallen[/color][/center]")
		add_output("")
		add_output("[color=#" + COLOR_INFO + "]The enemies of France have prevailed.[/color]")
		add_output("[color=#" + COLOR_INFO + "]Your marshals fought bravely, but it was not enough.[/color]")
		add_output("[color=#" + COLOR_INFO + "]The eagles are furled. The Grande Armée is no more.[/color]")

	add_output("")
	add_output("[color=#" + COLOR_GOLD + "]─────────────────────────────────────[/color]")
	add_output("[color=#" + COLOR_GOLD + "]         FINAL STATISTICS[/color]")
	add_output("[color=#" + COLOR_GOLD + "]─────────────────────────────────────[/color]")

	# Display final statistics
	var final_turn = int(game_state.get("turn", current_turn))
	var regions_controlled = int(game_state.get("regions_controlled", 0))
	var total_regions = int(game_state.get("total_regions", 13))
	var final_gold = int(game_state.get("gold", gold))

	add_output("[color=#" + COLOR_INFO + "]Campaign Duration: " + str(final_turn) + " turns[/color]")
	add_output("[color=#" + COLOR_INFO + "]Regions Controlled: " + str(regions_controlled) + "/" + str(total_regions) + "[/color]")
	add_output("[color=#" + COLOR_INFO + "]Imperial Treasury: " + _format_number(final_gold) + " gold[/color]")

	# Marshal status if available
	if game_state.has("player_marshals"):
		var marshals = game_state.player_marshals
		add_output("")
		add_output("[color=#" + COLOR_MARSHAL + "]Marshal Status:[/color]")
		for marshal_name in marshals:
			var marshal = marshals[marshal_name]
			var strength = int(marshal.get("strength", 0))
			var location = marshal.get("location", "Unknown")
			if strength > 0:
				add_output("[color=#" + COLOR_INFO + "]  • " + marshal_name + ": " + _format_number(strength) + " troops at " + location + "[/color]")
			else:
				add_output("[color=#" + COLOR_ERROR + "]  • " + marshal_name + ": Destroyed[/color]")

	add_output("")
	add_output("[color=#" + COLOR_GOLD + "]═══════════════════════════════════════[/color]")
	add_output("[color=#" + COLOR_GOLD + "]═══════════════════════════════════════[/color]")
	add_output("")

	# Closing message
	if victory_status == "victory":
		add_output("[center][color=#" + COLOR_GOLD + "]Vive l'Empereur![/color][/center]")
	else:
		add_output("[center][color=#" + COLOR_INFO + "]The game is over, but the legend endures...[/color][/center]")

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
	"""Enable or disable command input and buttons."""
	command_input.editable = enabled
	send_button.disabled = not enabled
	end_turn_button.disabled = not enabled

	if enabled:
		command_input.grab_focus()

func _show_objection_dialog(response):
	"""Display objection dialog when marshal objects."""
	print("9. _show_objection_dialog() CALLED")

	add_output("")
	add_output("[color=#" + COLOR_MARSHAL + "]⚠ Marshal " + response.get("marshal", "Unknown") + " raises concerns...[/color]")
	add_output("")

	# Prepare objection data for dialog
	var objection_data = {
		"marshal": response.get("marshal", "Marshal"),
		"personality": response.get("personality", "unknown"),
		"message": response.get("message", "I have concerns about this order, Sire."),
		"trust": response.get("trust", 70),
		"trust_label": response.get("trust_label", "Unknown"),
		"vindication": response.get("vindication", 0),
		"authority": response.get("authority", 100),
		"suggested_alternative": response.get("suggested_alternative"),
		"compromise": response.get("compromise")
	}

	print("10. OBJECTION DATA: ", objection_data)

	# CHECK: Is dialog null?
	if objection_dialog == null:
		print("11. ❌ ERROR: objection_dialog is NULL!")
		push_error("objection_dialog is NULL! Cannot show dialog.")
		add_output("[color=#" + COLOR_ERROR + "]ERROR: Dialog not loaded![/color]")
		set_input_enabled(true)
		return

	print("11. Dialog exists, calling show_objection()")
	print("12. BEFORE show_objection - visible: ", objection_dialog.visible)

	# Show the dialog
	objection_dialog.show_objection(objection_data)

	print("13. AFTER show_objection - visible: ", objection_dialog.visible)

func _on_objection_choice_made(choice: String):
	"""Handle player's choice in objection dialog."""
	# Disable input while processing
	set_input_enabled(false)

	# Display player choice
	var choice_text = ""
	match choice:
		"trust":
			choice_text = "You decide to trust your marshal's judgment."
		"insist":
			choice_text = "You insist the order be carried out as given."
		"compromise":
			choice_text = "You seek a middle ground with your marshal."

	add_output("[color=#" + COLOR_COMMAND + "]► " + choice_text + "[/color]")
	add_output("")

	# Send choice to backend
	api_client.send_objection_response(choice, _on_objection_response)

func _on_objection_response(response):
	"""Handle backend response after player makes objection choice."""
	print("\n" + "=".repeat(60))
	print("OBJECTION RESPONSE RECEIVED:")
	print("  success: ", response.get("success", false))
	print("  disobeyed: ", response.get("disobeyed", false))
	print("  has redemption_event: ", response.has("redemption_event"))
	print("  state: ", response.get("state", "none"))
	print("=".repeat(60) + "\n")

	# ════════════════════════════════════════════════════════════
	# CHECK FOR DISOBEY: Marshal refused to obey
	# ════════════════════════════════════════════════════════════
	if response.get("disobeyed", false):
		add_output("[color=#" + COLOR_ERROR + "]⚠ DISOBEDIENCE![/color]")
		add_output("[color=#" + COLOR_MARSHAL + "]" + response.message + "[/color]")
		add_output("")

		# Update status even on disobey
		if response.has("action_summary"):
			_update_status(response.action_summary)

		# Check for redemption event triggered by disobey
		if response.has("redemption_event"):
			print("🚨 REDEMPTION EVENT after disobey - showing dialog")
			_show_redemption_dialog(response.redemption_event)
			return  # Don't re-enable input until redemption resolved

		set_input_enabled(true)
		command_input.grab_focus()
		return

	# ════════════════════════════════════════════════════════════
	# CHECK FOR REDEMPTION EVENT: Trust at critical low
	# ════════════════════════════════════════════════════════════
	if response.has("redemption_event"):
		print("🚨 REDEMPTION EVENT detected - showing dialog")

		# First show the normal result
		if response.success:
			if response.has("action_summary"):
				_update_status(response.action_summary)
			if response.has("game_state") and response.game_state.has("gold"):
				gold = int(response.game_state.gold)
				_update_gold_display()
			if response.has("game_state") and response.game_state.has("map_data"):
				map_area.update_all_regions(response.game_state.map_data)
			_display_result(response)

		# Then show redemption dialog
		_show_redemption_dialog(response.redemption_event)
		return  # Don't re-enable input until redemption resolved

	# Re-enable input (normal flow)
	set_input_enabled(true)

	if response.success:
		# Update status displays
		if response.has("action_summary"):
			_update_status(response.action_summary)

		if response.has("game_state") and response.game_state.has("gold"):
			gold = int(response.game_state.gold)
			_update_gold_display()

		# Update map with latest state
		if response.has("game_state") and response.game_state.has("map_data"):
			map_area.update_all_regions(response.game_state.map_data)

		# Display result
		_display_result(response)

		# Check for game over
		if response.has("game_state") and response.game_state.has("game_over"):
			if response.game_state.game_over:
				_show_game_over_screen(response.game_state)
				return
	else:
		add_output("[color=#" + COLOR_ERROR + "]" + response.message + "[/color]")

	add_output("")
	command_input.grab_focus()


func _show_redemption_dialog(redemption_event: Dictionary):
	"""Display redemption popup dialog when trust hits critical low."""
	print("REDEMPTION DIALOG - showing popup for event: ", redemption_event)

	var marshal_name = redemption_event.get("marshal", "Marshal")

	# Show brief notification in log
	add_output("")
	add_output("[color=#" + COLOR_ERROR + "]⚠ " + marshal_name + " requests an urgent audience...[/color]")
	add_output("")

	# Check if dialog exists
	if redemption_dialog == null:
		print("❌ ERROR: redemption_dialog is NULL!")
		push_error("redemption_dialog is NULL! Cannot show dialog.")
		add_output("[color=#" + COLOR_ERROR + "]ERROR: Redemption dialog not loaded![/color]")
		# Fallback to text commands
		_show_redemption_text_fallback(redemption_event)
		return

	# Show the popup dialog
	redemption_dialog.show_redemption(redemption_event)
	pending_redemption = true


func _show_redemption_text_fallback(redemption_event: Dictionary):
	"""Fallback text display if dialog fails to load."""
	var options = redemption_event.get("options", [])

	add_output("[color=#" + COLOR_INFO + "]You must decide how to handle this:[/color]")
	for opt in options:
		add_output("[color=#" + COLOR_INFO + "]  • " + opt.get("id", "?") + ": " + opt.get("text", "Unknown") + "[/color]")

	add_output("")
	add_output("[color=#" + COLOR_GOLD + "]Type: 'grant_autonomy', 'dismiss', or 'demand_obedience'[/color]")
	add_output("")

	pending_redemption = true
	set_input_enabled(true)
	command_input.grab_focus()


func _on_redemption_choice_made(choice: String):
	"""Handle player's choice in redemption dialog."""
	print("REDEMPTION CHOICE MADE: ", choice)

	# Disable input while processing
	set_input_enabled(false)

	# Display player choice in log
	var choice_text = ""
	match choice:
		"grant_autonomy":
			choice_text = "You grant the marshal autonomy to act independently."
		"dismiss":
			choice_text = "You dismiss the marshal from command."
		"demand_obedience":
			choice_text = "You demand continued obedience despite the broken trust."

	add_output("[color=#" + COLOR_COMMAND + "]► " + choice_text + "[/color]")
	add_output("")

	# Send choice to backend
	api_client.send_redemption_response(choice, _on_redemption_response)


func _on_redemption_response(response):
	"""Handle backend response after player makes redemption choice."""
	print("\n" + "=".repeat(60))
	print("REDEMPTION RESPONSE RECEIVED:")
	print("  success: ", response.get("success", false))
	print("  choice: ", response.get("choice", "unknown"))
	print("  autonomous: ", response.get("autonomous", false))
	print("  dismissed: ", response.get("dismissed", false))
	print("=".repeat(60) + "\n")

	pending_redemption = false

	if response.success:
		# Update status displays
		if response.has("action_summary"):
			_update_status(response.action_summary)

		if response.has("game_state") and response.game_state.has("gold"):
			gold = int(response.game_state.gold)
			_update_gold_display()

		# Update map
		if response.has("game_state") and response.game_state.has("map_data"):
			map_area.update_all_regions(response.game_state.map_data)

		# Display result based on choice
		var choice = response.get("choice", "")
		add_output("")

		if choice == "grant_autonomy":
			add_output("[color=#" + COLOR_SUCCESS + "]═══════════════════════════════════════[/color]")
			add_output("[color=#" + COLOR_SUCCESS + "]   AUTONOMY GRANTED[/color]")
			add_output("[color=#" + COLOR_SUCCESS + "]═══════════════════════════════════════[/color]")
			add_output("[color=#" + COLOR_MARSHAL + "]" + response.message + "[/color]")
			var turns = response.get("autonomy_turns", 3)
			add_output("[color=#" + COLOR_INFO + "]The marshal will act independently for " + str(turns) + " turns.[/color]")

		elif choice == "dismiss":
			add_output("[color=#" + COLOR_ERROR + "]═══════════════════════════════════════[/color]")
			add_output("[color=#" + COLOR_ERROR + "]   MARSHAL DISMISSED[/color]")
			add_output("[color=#" + COLOR_ERROR + "]═══════════════════════════════════════[/color]")
			add_output("[color=#" + COLOR_MARSHAL + "]" + response.message + "[/color]")

		elif choice == "demand_obedience":
			add_output("[color=#" + COLOR_GOLD + "]═══════════════════════════════════════[/color]")
			add_output("[color=#" + COLOR_GOLD + "]   OBEDIENCE DEMANDED[/color]")
			add_output("[color=#" + COLOR_GOLD + "]═══════════════════════════════════════[/color]")
			add_output("[color=#" + COLOR_MARSHAL + "]" + response.message + "[/color]")
			add_output("[color=#" + COLOR_INFO + "]Warning: High chance of future disobedience.[/color]")

		else:
			add_output("[color=#" + COLOR_SUCCESS + "]" + response.message + "[/color]")

		add_output("")
	else:
		add_output("[color=#" + COLOR_ERROR + "]" + response.message + "[/color]")
		add_output("")

	set_input_enabled(true)
	command_input.grab_focus()


func _show_enemy_phase_dialog(enemy_phase: Dictionary, turn: int):
	"""Display enemy phase popup with full battle details."""
	print("Showing enemy phase dialog for turn ", turn)

	# Check if dialog exists
	if enemy_phase_dialog == null:
		print("ERROR: enemy_phase_dialog is NULL!")
		push_error("enemy_phase_dialog is NULL! Cannot show dialog.")
		# Fallback: just re-enable input
		set_input_enabled(true)
		return

	# Show the dialog
	enemy_phase_dialog.show_enemy_phase(enemy_phase, turn)


func _on_enemy_phase_dismissed():
	"""Handle enemy phase dialog dismissal."""
	print("Enemy phase dialog dismissed")

	# Check for game over (Paris captured, all marshals destroyed, etc.)
	if pending_enemy_phase_response != null:
		var response = pending_enemy_phase_response
		pending_enemy_phase_response = null  # Clear it

		if response.has("game_state") and response.game_state.has("game_over"):
			if response.game_state.game_over:
				_show_game_over_screen(response.game_state)
				return  # Don't re-enable input

	set_input_enabled(true)
	command_input.grab_focus()


# ════════════════════════════════════════════════════════════════════════════
# GLORIOUS CHARGE DIALOG (Phase 3 Cavalry Recklessness)
# ════════════════════════════════════════════════════════════════════════════

var pending_charge_marshal: String = ""
var pending_charge_target: String = ""

func _show_glorious_charge_dialog(response):
	"""Display Glorious Charge popup when reckless cavalry is at recklessness 3."""
	print("_show_glorious_charge_dialog() CALLED")
	print("  Response: ", response)

	# Store pending info for sending back to server
	# Handle null values (get() default doesn't work if key exists with null)
	var marshal_val = response.get("marshal")
	var target_val = response.get("target")
	var reck_val = response.get("recklessness")

	pending_charge_marshal = marshal_val if marshal_val != null else ""
	pending_charge_target = target_val if target_val != null else ""

	# Get recklessness - backend sends it in the response directly
	var recklessness = int(reck_val) if reck_val != null else 3

	print("  Parsed: marshal=%s, target=%s, recklessness=%d" % [pending_charge_marshal, pending_charge_target, recklessness])

	# Show notification in log
	add_output("")
	add_output("[color=#" + COLOR_BATTLE + "]🐴 " + pending_charge_marshal + "'s blood is up![/color]")
	add_output("[color=#" + COLOR_INFO + "]Recklessness at " + str(recklessness) + "/4 - Glorious Charge available![/color]")
	add_output("")

	# Check if dialog exists
	if glorious_charge_dialog == null:
		print("❌ ERROR: glorious_charge_dialog is NULL!")
		push_error("glorious_charge_dialog is NULL! Cannot show dialog.")
		add_output("[color=#" + COLOR_ERROR + "]ERROR: Glorious Charge dialog not loaded![/color]")
		# Fallback to text
		_show_glorious_charge_text_fallback()
		return

	# Prepare data for dialog
	var charge_data = {
		"marshal": pending_charge_marshal,
		"target": pending_charge_target,
		"recklessness": recklessness
	}

	# Show the popup dialog
	glorious_charge_dialog.show_glorious_charge(charge_data)


func _show_glorious_charge_text_fallback():
	"""Fallback text display if dialog fails to load."""
	add_output("[color=#" + COLOR_GOLD + "]═══════════════════════════════════════[/color]")
	add_output("[color=#" + COLOR_GOLD + "]         GLORIOUS CHARGE![/color]")
	add_output("[color=#" + COLOR_GOLD + "]═══════════════════════════════════════[/color]")
	add_output("")
	add_output("[color=#" + COLOR_ERROR + "]⚠ Glorious Charge deals 2x damage but also TAKES 2x damage![/color]")
	add_output("[color=#" + COLOR_INFO + "]Target: " + pending_charge_target + "[/color]")
	add_output("")
	add_output("[color=#" + COLOR_INFO + "]Type 'charge' to execute Glorious Charge[/color]")
	add_output("[color=#" + COLOR_INFO + "]Type 'restrain' for normal attack[/color]")
	add_output("")

	set_input_enabled(true)
	command_input.grab_focus()


func _on_glorious_charge_choice_made(choice: String):
	"""Handle player's choice in Glorious Charge dialog."""
	print("GLORIOUS CHARGE CHOICE MADE: ", choice)
	print("  Marshal: ", pending_charge_marshal)
	print("  Target: ", pending_charge_target)

	# Disable input while processing
	set_input_enabled(false)

	# Display player choice in log
	var choice_text = ""
	if choice == "charge":
		choice_text = pending_charge_marshal + " unleashes a GLORIOUS CHARGE!"
		add_output("[color=#" + COLOR_BATTLE + "]🐴⚔ " + choice_text + " ⚔🐴[/color]")
	else:
		choice_text = "You restrain " + pending_charge_marshal + " - normal attack."
		add_output("[color=#" + COLOR_COMMAND + "]► " + choice_text + "[/color]")

	add_output("")

	# Send choice to backend
	api_client.send_glorious_charge_response(choice, _on_glorious_charge_response)


func _on_glorious_charge_response(response):
	"""Handle backend response after player makes Glorious Charge choice."""
	print("\n" + "=".repeat(60))
	print("GLORIOUS CHARGE RESPONSE RECEIVED:")
	print("  success: ", response.get("success", false))
	print("  message: ", response.get("message", ""))
	print("=".repeat(60) + "\n")

	# Clear pending state
	pending_charge_marshal = ""
	pending_charge_target = ""

	# Re-enable input
	set_input_enabled(true)

	if response.success:
		# Update status displays
		if response.has("action_summary"):
			_update_status(response.action_summary)

		if response.has("game_state") and response.game_state.has("gold"):
			gold = int(response.game_state.gold)
			_update_gold_display()

		# Update map with latest state
		if response.has("game_state") and response.game_state.has("map_data"):
			map_area.update_all_regions(response.game_state.map_data)

		# Display result
		_display_result(response)

		# Check for game over
		if response.has("game_state") and response.game_state.has("game_over"):
			if response.game_state.game_over:
				_show_game_over_screen(response.game_state)
				return
	else:
		add_output("[color=#" + COLOR_ERROR + "]" + response.message + "[/color]")

	add_output("")
	command_input.grab_focus()
