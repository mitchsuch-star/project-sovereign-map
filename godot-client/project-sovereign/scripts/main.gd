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
@onready var admin_value = $BottomLeftUI/MainMargin/MainLayout/Header/HeaderMargin/HeaderContent/StatusSection/AdminDisplay/AdminValue
@onready var gold_value = $BottomLeftUI/MainMargin/MainLayout/Header/HeaderMargin/HeaderContent/StatusSection/GoldDisplay/GoldValue
@onready var inf_value = $BottomLeftUI/MainMargin/MainLayout/Header/HeaderMargin/HeaderContent/StatusSection/ManpowerDisplay/InfValue
@onready var cav_value = $BottomLeftUI/MainMargin/MainLayout/Header/HeaderMargin/HeaderContent/StatusSection/ManpowerDisplay/CavValue
@onready var art_value = $BottomLeftUI/MainMargin/MainLayout/Header/HeaderMargin/HeaderContent/StatusSection/ManpowerDisplay/ArtValue

# UI References - Main Interface
@onready var output_scroll = $BottomLeftUI/MainMargin/MainLayout/OutputScroll
@onready var output_display = $BottomLeftUI/MainMargin/MainLayout/OutputScroll/OutputDisplay
@onready var command_input = $BottomLeftUI/MainMargin/MainLayout/InputSection/CommandInput
@onready var send_button = $BottomLeftUI/MainMargin/MainLayout/InputSection/SendButton
@onready var end_turn_button = $BottomLeftUI/MainMargin/MainLayout/InputSection/EndTurnButton

# UI References - Minimize/Restore
@onready var bottom_left_ui = $BottomLeftUI
@onready var minimize_button = $BottomLeftUI/MainMargin/MainLayout/Header/HeaderMargin/HeaderContent/TitleRow/MinimizeButton
@onready var restore_button = $RestoreButton

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

# Capture Choice Dialog (Phase 6.2.E Plunder/Secure)
var capture_choice_dialog = null

# Load Game Dialog (Phase 6: Save/Load)
var load_dialog = null

# Strategic Command Dialogs (Phase J)
var strategic_report_popup = null
var interrupt_popup = null
var clarification_popup = null
var pending_strategic_response = null  # Store response for post-report flow
var interrupt_queue: Array = []  # Queue of interrupts to show one at a time

# API Client
var api_client = null

# Game state tracking
var actions_remaining = 4
var max_actions = 4
var admin_actions_remaining = 2
var max_admin_actions = 2
var current_turn = 1
var max_turns = 40
var gold = 1200
var infantry_pool = 80000
var cavalry_pool = 15000
var artillery_pool = 10000
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
const COLOR_FEEDBACK = "b8a0d9"    # Soft purple/lavender for AI feedback
const COLOR_DISPATCH = "c9b878"    # Warm gold for field dispatches (MILD flavor)

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

	# Load and setup Capture Choice Dialog (Phase 6.2.E Plunder/Secure)
	var capture_choice_scene = load("res://scenes/capture_choice_dialog.tscn")
	if capture_choice_scene:
		capture_choice_dialog = capture_choice_scene.instantiate()
		add_child(capture_choice_dialog)
		capture_choice_dialog.choice_made.connect(_on_capture_choice_made)
		print("✓ CaptureChoiceDialog ready!")

	# Load and setup Load Game Dialog (Phase 6: Save/Load)
	var load_dialog_scene = load("res://scenes/load_dialog.tscn")
	if load_dialog_scene:
		load_dialog = load_dialog_scene.instantiate()
		add_child(load_dialog)
		load_dialog.save_selected.connect(_on_load_save_selected)
		load_dialog.load_cancelled.connect(_on_load_cancelled)
		print("LoadDialog ready!")

	# Load and setup Strategic Report Popup (Phase J)
	var strategic_report_scene = load("res://scenes/strategic_report_popup.tscn")
	if strategic_report_scene:
		strategic_report_popup = strategic_report_scene.instantiate()
		add_child(strategic_report_popup)
		strategic_report_popup.dismissed.connect(_on_strategic_report_dismissed)
		print("✓ StrategicReportPopup ready!")

	# Load and setup Interrupt Popup (Phase J)
	var interrupt_scene = load("res://scenes/interrupt_popup.tscn")
	if interrupt_scene:
		interrupt_popup = interrupt_scene.instantiate()
		add_child(interrupt_popup)
		interrupt_popup.choice_made.connect(_on_interrupt_choice_made)
		print("✓ InterruptPopup ready!")

	# Load and setup Clarification Popup (Phase J)
	var clarification_scene = load("res://scenes/clarification_popup.tscn")
	if clarification_scene:
		clarification_popup = clarification_scene.instantiate()
		add_child(clarification_popup)
		clarification_popup.clarification_choice.connect(_on_clarification_choice_made)
		clarification_popup.cancelled.connect(_on_clarification_cancelled)
		print("✓ ClarificationPopup ready!")

	# Connect signals
	if not send_button.pressed.is_connected(_on_send_button_pressed):
		send_button.pressed.connect(_on_send_button_pressed)

	if not command_input.text_submitted.is_connected(_on_command_submitted):
		command_input.text_submitted.connect(_on_command_submitted)

	if not end_turn_button.pressed.is_connected(_on_end_turn_pressed):
		end_turn_button.pressed.connect(_on_end_turn_pressed)

	if not command_input.gui_input.is_connected(_on_command_input_gui_input):
		command_input.gui_input.connect(_on_command_input_gui_input)

	# Minimize/Restore terminal panel
	if not minimize_button.pressed.is_connected(_minimize_terminal):
		minimize_button.pressed.connect(_minimize_terminal)
	if not restore_button.pressed.is_connected(_restore_terminal):
		restore_button.pressed.connect(_restore_terminal)

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
		if response.has("manpower_pools"):
			_apply_manpower(response.manpower_pools)

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
	if event is InputEventKey and event.pressed and not event.echo:
		# E key for End Turn (only when not typing in command input)
		if event.keycode == KEY_E:
			# Don't trigger if command input has focus
			if not command_input.has_focus() and end_turn_button.visible and not end_turn_button.disabled:
				_execute_end_turn()
				get_viewport().set_input_as_handled()
		# Tab key to toggle terminal panel
		elif event.keycode == KEY_TAB:
			if not command_input.has_focus():
				_toggle_terminal()
				get_viewport().set_input_as_handled()

func _minimize_terminal():
	"""Collapse the terminal panel, show restore button."""
	bottom_left_ui.visible = false
	restore_button.visible = true

func _restore_terminal():
	"""Expand the terminal panel, hide restore button."""
	bottom_left_ui.visible = true
	restore_button.visible = false

func _toggle_terminal():
	"""Toggle terminal panel visibility."""
	if bottom_left_ui.visible:
		_minimize_terminal()
	else:
		_restore_terminal()

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
	# Tactical objections: state == "awaiting_player_choice"
	# Strategic objections (Phase M): pending_objection == true
	var is_tactical_objection = response.get("success", false) and response.has("state") and response.state == "awaiting_player_choice"
	var is_strategic_objection = response.get("success", false) and response.has("pending_objection") and response.pending_objection == true
	var is_objection = is_tactical_objection or is_strategic_objection
	print("4. IS_OBJECTION CHECK: tactical=", is_tactical_objection, " strategic=", is_strategic_objection, " => ", is_objection)

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

	# Check for capture choice (Phase 6.2.E: Plunder or Secure)
	if response.has("pending_capture_choice") and response.pending_capture_choice:
		_show_capture_choice_dialog(response)
		return  # Don't re-enable input until choice made

	# Check for load dialog request (Phase 6: Save/Load)
	if response.has("show_load_dialog") and response.show_load_dialog:
		_show_load_dialog()
		# Don't return — still show the save list message in terminal

	# Check for clarification request (Grouchy/literal marshal)
	if response.has("state") and response.state == "awaiting_clarification":
		_show_clarification_popup(response)
		return  # Don't re-enable input until choice made

	# Check for strategic interrupt (blocked path, cannon fire, etc.)
	if response.has("pending_interrupt") and response.pending_interrupt:
		_show_interrupt_popup(response.pending_interrupt)
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
		if response.has("game_state") and response.game_state.has("manpower_pools"):
			_apply_manpower(response.game_state.manpower_pools)

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

		# Display tactical events (supply attrition, etc.) from turn resolution
		if response.has("tactical_events"):
			_display_tactical_events(response.tactical_events)

		# Check for enemy phase (from end_turn)
		# NOTE: No total_actions > 0 gate — dialog shows even with 0 enemy actions
		# (e.g. debug freeze_enemies). The dialog handles 0-action case with
		# "No enemy actions this turn." message.
		if response.has("enemy_phase"):
			print("ENEMY PHASE DETECTED - showing dialog")
			set_input_enabled(false)  # Disable input until dismissed
			var turn = current_turn
			if response.has("action_summary"):
				turn = int(response.action_summary.get("turn", current_turn))
			pending_enemy_phase_response = response  # Store for post-enemy-phase flow
			_show_enemy_phase_dialog(response.enemy_phase, turn)
			return  # Don't re-enable input until dialog dismissed

		# V2a: Show MILD dispatches when no enemy phase dialog
		_show_mild_dispatches(response)

		# Check for strategic reports (when no enemy phase dialog)
		if response.has("strategic_reports") and not response.strategic_reports.is_empty():
			set_input_enabled(false)
			pending_strategic_response = response
			_show_strategic_reports(response)
			return  # Don't re-enable input until reports dismissed

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
		event_type = event.get("type", "")
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
		"bombardment":
			add_output("[color=#" + COLOR_BATTLE + "]" + message + "[/color]")
			_show_action_cost(action_info)
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

	# Berthier's After-Action Report — shown after any combat event type
	if response.has("battle_report"):
		_display_berthier_report(response.battle_report)

	# Berthier's Bombardment Report — shown after bombardment actions
	if response.has("bombardment_result"):
		_display_bombardment_report(response.bombardment_result)

	# Berthier's Bombardment Advisory — shown when artillery crumbles enemy forts
	var bombardment_advisory = response.get("bombardment_advisory", "")
	if bombardment_advisory != "" and bombardment_advisory != null:
		add_output("[color=#" + COLOR_DISPATCH + "]  Berthier: \"" + str(bombardment_advisory) + "\"[/color]")
	
	# Check for turn advancement
	if action_info.get("turn_advanced", false):
		_display_turn_advance(action_info)

	# Display AI feedback if present (LLM mode only)
	if response.has("feedback"):
		_display_feedback(response.feedback)

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

	# Cavalry terrain flavor (Phase 6.1: separate colored line for cavalry effectiveness)
	var cav_terrain_msg = event.get("cavalry_terrain_message", "")
	if cav_terrain_msg != "" and cav_terrain_msg != null:
		add_output("[color=#" + COLOR_DISPATCH + "]   🐴 " + cav_terrain_msg + "[/color]")

	# Special notifications
	if enemy_destroyed:
		add_output("[color=#" + COLOR_CONQUEST + "]   ★ Enemy army destroyed! ★[/color]")
	
	if region_conquered:
		var region_name = event.get("region_name", "territory")
		add_output("[color=#" + COLOR_CONQUEST + "]   ⚑ " + region_name + " captured! ⚑[/color]")
	
	_show_action_cost(action_info)

func _display_berthier_report(report: Dictionary):
	"""Display Berthier's After-Action Report with modifier breakdown and observation."""
	var COLOR_BERTHIER = "B8860B"   # Dark goldenrod for header
	var COLOR_REPORT = "CCCCCC"     # Light gray for report lines
	var COLOR_OBSERVATION = "DAA520" # Goldenrod for Berthier's quote

	add_output("[color=#" + COLOR_BERTHIER + "]--- Berthier's Report ---[/color]")

	# Modifier breakdown
	var breakdown = report.get("modifier_breakdown", {})

	# Attacker modifiers
	var atk_mods = breakdown.get("attacker", [])
	var casualty = report.get("casualty_summary", {})
	var atk_name = str(casualty.get("attacker_name", "Attacker"))
	if atk_mods.size() > 0:
		var atk_parts: Array = []
		for m in atk_mods:
			var sign = "+" if m.get("type", "") == "bonus" else "-"
			atk_parts.append(str(m.get("label", "")) + " " + sign + str(int(m.get("value", 0))) + "%")
		add_output("[color=#" + COLOR_REPORT + "]  Attack: " + atk_name + " (" + ", ".join(PackedStringArray(atk_parts)) + ")[/color]")

	# Defender modifiers
	var def_mods = breakdown.get("defender", [])
	var def_name = str(casualty.get("defender_name", "Defender"))
	if def_mods.size() > 0:
		var def_parts: Array = []
		for m in def_mods:
			var sign = "+" if m.get("type", "") == "bonus" else "-"
			def_parts.append(str(m.get("label", "")) + " " + sign + str(int(m.get("value", 0))) + "%")
		add_output("[color=#" + COLOR_REPORT + "]  Defense: " + def_name + " (" + ", ".join(PackedStringArray(def_parts)) + ")[/color]")

	# Casualty summary
	var atk_cas = int(casualty.get("attacker_casualties", 0))
	var def_cas = int(casualty.get("defender_casualties", 0))
	var atk_orig = int(casualty.get("attacker_original", 0))
	var atk_rem = int(casualty.get("attacker_remaining", 0))
	var def_orig = int(casualty.get("defender_original", 0))
	var def_rem = int(casualty.get("defender_remaining", 0))

	# Format with thousands separators
	add_output("[color=#" + COLOR_REPORT + "]  Casualties: " + atk_name + " " + _format_number(atk_cas) + " | " + def_name + " " + _format_number(def_cas) + "[/color]")
	add_output("[color=#" + COLOR_REPORT + "]  Strength: " + atk_name + " " + _format_number(atk_orig) + " -> " + _format_number(atk_rem) + " | " + def_name + " " + _format_number(def_orig) + " -> " + _format_number(def_rem) + "[/color]")

	# Berthier's observation
	var observation = str(report.get("observation", ""))
	if observation != "":
		add_output("[color=#" + COLOR_OBSERVATION + "]  Berthier: \"" + observation + "\"[/color]")

	add_output("")

func _display_bombardment_report(result: Dictionary):
	"""Display Berthier's bombardment report with casualty summary and observation."""
	var COLOR_BERTHIER = "B8860B"   # Dark goldenrod for header
	var COLOR_CASUALTY = "a0a0a8"   # Info gray for stats
	var COLOR_ENEMY_CAS = "cd5c5c"  # Red for enemy casualties
	var COLOR_OWN_CAS = "8fbc8f"    # Muted green for own (low) casualties
	var COLOR_TERRAIN = "b0a890"    # Warm gray for terrain info
	var COLOR_FORT = "daa06d"       # Battle orange for fort degradation
	var COLOR_OBSERVATION = "DAA520" # Goldenrod for Berthier's quote
	var COLOR_FRIENDLY = "cd6b6b"   # Muted red for friendly fire
	var COLOR_REMAINING = "a0a0a8"  # Info gray for remaining count

	add_output("[color=#" + COLOR_BERTHIER + "]--- Bombardment Report ---[/color]")

	# Attacker (artillery) casualties
	var atk = result.get("attacker", {})
	var atk_name = str(atk.get("name", "Artillery"))
	var atk_cas = int(atk.get("casualties", 0))
	var atk_rem = int(atk.get("remaining", 0))

	# Defender casualties
	var defn = result.get("defender", {})
	var def_name = str(defn.get("name", "Enemy"))
	var def_cas = int(defn.get("casualties", 0))
	var def_rem = int(defn.get("remaining", 0))
	var def_morale = int(defn.get("morale", 100))

	# Terrain effectiveness
	var terrain_name = str(result.get("terrain", "plains")).replace("_", " ").capitalize()
	var terrain_mod = result.get("terrain_modifier", 1.0)
	# terrain_mod may be a float — display as percentage
	var terrain_pct = int(terrain_mod * 100)
	var terrain_label = ""
	if terrain_pct > 100:
		terrain_label = terrain_name + " (+" + str(terrain_pct - 100) + "% damage)"
	elif terrain_pct < 100:
		terrain_label = terrain_name + " (-" + str(100 - terrain_pct) + "% damage)"
	else:
		terrain_label = terrain_name + " (no modifier)"
	add_output("[color=#" + COLOR_TERRAIN + "]  Terrain: " + terrain_label + "[/color]")

	# Casualty summary — enemy in red, own in green
	add_output("[color=#" + COLOR_ENEMY_CAS + "]  Enemy casualties: " + def_name + " " + _format_number(def_cas) + " (remaining: " + _format_number(def_rem) + ", morale: " + str(def_morale) + "%)[/color]")
	add_output("[color=#" + COLOR_OWN_CAS + "]  Return fire: " + atk_name + " " + _format_number(atk_cas) + " (remaining: " + _format_number(atk_rem) + ")[/color]")

	# Fort degradation
	var fort_degraded = result.get("fort_degraded", false)
	if fort_degraded:
		var fort_old = int(result.get("fort_old", 0) * 100)
		var fort_new = int(result.get("fort_new", 0) * 100)
		if fort_new <= 0:
			add_output("[color=#" + COLOR_FORT + "]  Fortifications DESTROYED! (" + str(fort_old) + "% -> 0%)[/color]")
		else:
			add_output("[color=#" + COLOR_FORT + "]  Fort degraded: " + str(fort_old) + "% -> " + str(fort_new) + "%[/color]")

	# Collateral damage
	var collateral = result.get("collateral", [])
	if collateral is Array and collateral.size() > 0:
		add_output("[color=#" + COLOR_CASUALTY + "]  -- Collateral Damage --[/color]")
		for c in collateral:
			var c_name = str(c.get("name", "Unknown"))
			var c_nation = str(c.get("nation", ""))
			var c_cas = int(c.get("casualties", 0))
			var is_friendly = c.get("friendly_fire", false)
			if is_friendly:
				add_output("[color=#" + COLOR_FRIENDLY + "]  FRIENDLY FIRE: " + c_name + " (" + c_nation + ") — " + _format_number(c_cas) + " casualties[/color]")
			else:
				add_output("[color=#" + COLOR_ENEMY_CAS + "]  " + c_name + " (" + c_nation + ") — " + _format_number(c_cas) + " casualties[/color]")

	# Bombardments remaining
	var remaining = int(result.get("bombardments_remaining", 0))
	add_output("[color=#" + COLOR_REMAINING + "]  Bombardments remaining today: " + str(remaining) + "[/color]")

	# Berthier's observation
	var obs = str(result.get("berthier_observation", ""))
	if obs != "" and obs != "null":
		add_output("[color=#" + COLOR_OBSERVATION + "]  Berthier: \"" + obs + "\"[/color]")

	add_output("")

func _display_turn_change(event: Dictionary):
	"""Display turn end notification with full financial summary.

	Backend sends: income, upkeep, spent, net, treasury in turn_end event.
	All values are int() wrapped by executor.py (Godot crashes on floats).
	"""
	var new_turn = int(event.get("new_turn", 0))
	var income = int(event.get("income", 0))
	var upkeep = int(event.get("upkeep", 0))
	var spent = int(event.get("spent", 0))
	var net = int(event.get("net", 0))
	var treasury = int(event.get("treasury", 0))

	var net_sign = "+" if net >= 0 else ""
	var spent_str = ""
	if spent > 0:
		spent_str = " | Spent: " + str(int(spent)) + "g"

	add_output("")
	add_output("[color=#" + COLOR_GOLD + "]═══════════════════════════════════════[/color]")
	add_output("[color=#" + COLOR_GOLD + "]         TURN " + str(int(new_turn)) + " BEGINS[/color]")
	add_output("[color=#" + COLOR_GOLD + "]═══════════════════════════════════════[/color]")
	add_output("[color=#" + COLOR_SUCCESS + "]Income: " + str(int(income)) + "g | Upkeep: " + str(int(upkeep)) + "g | Net: " + net_sign + str(int(net)) + "g" + spent_str + "[/color]")
	add_output("[color=#" + COLOR_GOLD + "]Treasury: " + _format_number(int(treasury)) + "g[/color]")

	# Bankruptcy warning
	var bankruptcy_turns = int(event.get("bankruptcy_turns", 0))
	if bankruptcy_turns > 0:
		if bankruptcy_turns >= 3:
			add_output("[color=#" + COLOR_ERROR + "]BANKRUPTCY: Troops are deserting! (" + str(bankruptcy_turns) + " turns in deficit)[/color]")
		elif bankruptcy_turns >= 2:
			add_output("[color=#" + COLOR_ERROR + "]WARNING: Treasury in deficit! Troops grow restless![/color]")
		else:
			add_output("[color=#" + COLOR_ERROR + "]WARNING: Treasury in deficit! Upkeep costs halved as mercy.[/color]")

	add_output("[color=#" + COLOR_SUCCESS + "]Actions refreshed: " + str(int(max_actions)) + "/" + str(int(max_actions)) + "[/color]")
	add_output("")

func _display_tactical_events(tactical_events):
	"""Display tactical events from turn resolution (supply attrition, construction, occupation, etc.)."""
	if tactical_events is Array and tactical_events.size() > 0:
		for event in tactical_events:
			var event_type = event.get("type", "")
			if event_type == "supply_attrition":
				var marshal_name = event.get("marshal", "Unknown")
				var region_name = event.get("region", "Unknown")
				var losses = int(event.get("losses", 0))
				add_output("[color=#" + COLOR_ERROR + "]Supply shortage at " + region_name + ": " + marshal_name + " loses " + _format_number(losses) + " troops[/color]")
			elif event_type == "bankruptcy_desertion":
				var marshal_name = event.get("marshal", "Unknown")
				var losses = int(event.get("losses", 0))
				var remaining = int(event.get("remaining", 0))
				add_output("[color=#" + COLOR_ERROR + "]DESERTION: " + marshal_name + " loses " + _format_number(losses) + " troops (" + _format_number(remaining) + " remaining)[/color]")
			elif event_type == "construction_complete":
				var msg = event.get("message", "Construction complete.")
				add_output("[color=#" + COLOR_GOLD + "]" + msg + "[/color]")
			elif event_type == "occupation_complete":
				var msg = event.get("message", "Siege complete.")
				add_output("[color=#" + COLOR_GOLD + "]" + msg + "[/color]")
			elif event_type == "occupation_continues":
				var msg = event.get("message", "Siege continues.")
				add_output("[color=#" + COLOR_INFO + "]" + msg + "[/color]")
			elif event_type == "occupation_abandoned":
				var msg = event.get("message", "Siege abandoned.")
				add_output("[color=#" + COLOR_ERROR + "]" + msg + "[/color]")

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
	"""Update header status displays.

	Backend sends action_summary with: actions_remaining, max_actions,
	admin_actions_remaining, max_admin_actions, turn, max_turns.
	All values are int() wrapped by world_state.py get_action_summary().
	"""
	if action_summary.has("actions_remaining"):
		actions_remaining = int(action_summary.actions_remaining)

	if action_summary.has("max_actions"):
		max_actions = int(action_summary.max_actions)

	if action_summary.has("admin_actions_remaining"):
		admin_actions_remaining = int(action_summary.admin_actions_remaining)

	if action_summary.has("max_admin_actions"):
		max_admin_actions = int(action_summary.max_admin_actions)

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

	# Admin AP display
	if admin_actions_remaining == 0:
		admin_value.add_theme_color_override("font_color", Color(0.5, 0.5, 0.55))  # Grey when spent
	else:
		admin_value.add_theme_color_override("font_color", Color(0.6, 0.7, 0.9))  # Blue when available
	admin_value.text = str(int(admin_actions_remaining)) + "/" + str(int(max_admin_actions))

func _update_gold_display():
	"""Update treasury display with formatting."""
	gold_value.text = _format_number(gold)

func _apply_manpower(pools: Dictionary):
	"""Extract manpower values from a dict and update display."""
	if pools.has("infantry"):
		infantry_pool = int(pools.infantry)
	if pools.has("cavalry"):
		cavalry_pool = int(pools.cavalry)
	if pools.has("artillery"):
		artillery_pool = int(pools.artillery)
	_update_manpower_display()

func _update_manpower_display():
	"""Update manpower pool display with formatting."""
	inf_value.text = _format_number(infantry_pool)
	cav_value.text = _format_number(cavalry_pool)
	art_value.text = _format_number(artillery_pool)
	# Color shift when pools are low
	if cavalry_pool < 5000:
		cav_value.add_theme_color_override("font_color", Color(0.9, 0.3, 0.3))
	elif cavalry_pool < 10000:
		cav_value.add_theme_color_override("font_color", Color(0.9, 0.6, 0.4))
	else:
		cav_value.add_theme_color_override("font_color", Color(0.85, 0.75, 0.55))
	if infantry_pool < 20000:
		inf_value.add_theme_color_override("font_color", Color(0.9, 0.3, 0.3))
	elif infantry_pool < 40000:
		inf_value.add_theme_color_override("font_color", Color(0.9, 0.6, 0.4))
	else:
		inf_value.add_theme_color_override("font_color", Color(0.6, 0.8, 0.6))
	if artillery_pool < 3000:
		art_value.add_theme_color_override("font_color", Color(0.9, 0.3, 0.3))
	elif artillery_pool < 8000:
		art_value.add_theme_color_override("font_color", Color(0.9, 0.6, 0.4))
	else:
		art_value.add_theme_color_override("font_color", Color(0.75, 0.7, 0.85))

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

func _display_feedback(feedback: Dictionary):
	"""Display AI feedback from LLM response (words, not numbers)."""
	if feedback.is_empty():
		return

	# Strategic feedback (eloquence/inspiration)
	if feedback.has("strategic") and feedback.strategic != "":
		add_output("[color=#" + COLOR_FEEDBACK + "][i]" + feedback.strategic + "[/i][/color]")

	# Ambiguity feedback (clarity)
	if feedback.has("ambiguity") and feedback.ambiguity != "":
		add_output("[color=#" + COLOR_FEEDBACK + "][i]" + feedback.ambiguity + "[/i][/color]")

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
	# Strategic objections (Phase M) nest data in response.objection
	# Tactical objections have data at top level
	var is_strategic = response.has("pending_objection") and response.pending_objection == true
	var objection = response.get("objection", {}) if is_strategic else response

	var marshal_name = objection.get("marshal", response.get("marshal", "Unknown"))

	add_output("")
	add_output("[color=#" + COLOR_MARSHAL + "]⚠ Marshal " + marshal_name + " raises concerns...[/color]")
	add_output("")

	# Prepare objection data for dialog
	# Handle both tactical (top-level) and strategic (nested in objection) formats
	var objection_data = {
		"marshal": marshal_name,
		"personality": objection.get("personality", response.get("personality", "unknown")),
		"message": objection.get("message", response.get("message", "I have concerns about this order, Sire.")),
		"trust": response.get("trust", 70),
		"trust_label": response.get("trust_label", "Unknown"),
		"vindication": response.get("vindication", 0),
		"authority": response.get("authority", 100),
		"suggested_alternative": objection.get("suggested_alternative", response.get("suggested_alternative")),
		"compromise": objection.get("compromise", response.get("compromise")),
		# Strategic objections have options array instead of suggested_alternative/compromise
		"options": objection.get("options", []),
		"is_strategic": is_strategic,
		# V2a fields: tone, concern_level, trust change previews
		"tone": objection.get("tone", response.get("tone", "firm")),
		"concern_level": objection.get("concern_level", response.get("concern_level", "MODERATE")),
		"trust_gain": objection.get("trust_gain", response.get("trust_gain", 3)),
		"insist_penalty": objection.get("insist_penalty", response.get("insist_penalty", -10)),
		"compromise_gain": objection.get("compromise_gain", response.get("compromise_gain", 3)),
	}

	if objection_dialog == null:
		push_error("objection_dialog is NULL! Cannot show dialog.")
		add_output("[color=#" + COLOR_ERROR + "]ERROR: Dialog not loaded![/color]")
		set_input_enabled(true)
		return

	objection_dialog.show_objection(objection_data)

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
			if response.has("game_state") and response.game_state.has("manpower_pools"):
				_apply_manpower(response.game_state.manpower_pools)
			if response.has("game_state") and response.game_state.has("map_data"):
				map_area.update_all_regions(response.game_state.map_data)
			_display_result(response)

		# Then show redemption dialog
		_show_redemption_dialog(response.redemption_event)
		return  # Don't re-enable input until redemption resolved

	# Check for strategic interrupt (post-objection command hit blocked path)
	if response.has("pending_interrupt") and response.pending_interrupt:
		# Show the command result message first
		if response.has("message") and response.message:
			_display_result(response)
		_show_interrupt_popup(response.pending_interrupt)
		return  # Don't re-enable input until interrupt resolved

	# Re-enable input (normal flow)
	set_input_enabled(true)

	if response.success:
		# Update status displays
		if response.has("action_summary"):
			_update_status(response.action_summary)

		if response.has("game_state") and response.game_state.has("gold"):
			gold = int(response.game_state.gold)
			_update_gold_display()
		if response.has("game_state") and response.game_state.has("manpower_pools"):
			_apply_manpower(response.game_state.manpower_pools)

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
		if response.has("game_state") and response.game_state.has("manpower_pools"):
			_apply_manpower(response.game_state.manpower_pools)

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


func _show_mild_dispatches(response):
	"""V2a: Show MILD concerns as 'Field Dispatches' in the turn log.
	Atmosphere text — feels like reading war dispatches, not game feedback.
	Key 'mild_concerns' must match exactly what main.py sends — verify with curl if dispatches stop appearing."""
	if not response.has("mild_concerns"):
		return
	var concerns = response.mild_concerns
	if concerns is Array and concerns.size() > 0:
		add_output("")
		add_output("[color=#" + COLOR_DISPATCH + "]━━ Field Dispatches ━━[/color]")
		for concern in concerns:
			var marshal_name = concern.get("marshal", "Unknown")
			var msg = concern.get("message", "")
			if msg != "":
				add_output("[color=#" + COLOR_DISPATCH + "]  " + msg + "[/color]")
		add_output("")


func _on_enemy_phase_dismissed():
	"""Handle enemy phase dialog dismissal."""
	# Show enemy phase summary in command output after dialog dismissed
	# so the player has a text record in the command history.
	if pending_enemy_phase_response != null:
		var ep = pending_enemy_phase_response.get("enemy_phase", {})
		var summary_lines = ep.get("summary", [])
		if summary_lines.size() > 0:
			add_output("[color=#" + COLOR_GOLD + "]═══ ENEMY PHASE ═══[/color]")
			for line in summary_lines:
				add_output("[color=#" + COLOR_INFO + "]" + str(line) + "[/color]")
			add_output("")

	# Show MILD dispatches after enemy phase (V2a: atmosphere text)
	if pending_enemy_phase_response != null:
		_show_mild_dispatches(pending_enemy_phase_response)

	# Check for game over (Paris captured, all marshals destroyed, etc.)
	if pending_enemy_phase_response != null:
		var response = pending_enemy_phase_response

		if response.has("game_state") and response.game_state.has("game_over"):
			if response.game_state.game_over:
				pending_enemy_phase_response = null
				_show_game_over_screen(response.game_state)
				return  # Don't re-enable input

		# Check for strategic reports (show after enemy phase)
		if response.has("strategic_reports") and not response.strategic_reports.is_empty():
			# Keep pending_enemy_phase_response for post-report game over check
			pending_strategic_response = response
			_show_strategic_reports(response)
			return  # Don't re-enable input until reports dismissed

		pending_enemy_phase_response = null

	set_input_enabled(true)
	command_input.grab_focus()


# ════════════════════════════════════════════════════════════════════════════
# CAPTURE CHOICE DIALOG (Phase 6.2.E Plunder/Secure)
# ════════════════════════════════════════════════════════════════════════════

func _show_capture_choice_dialog(response):
	"""Display Plunder/Secure popup when player captures an enemy region."""
	var capture_data = response.get("capture_data", {})
	var region_name = capture_data.get("region", "Unknown") if capture_data is Dictionary else "Unknown"
	var capturer_name = capture_data.get("capturer", "Marshal") if capture_data is Dictionary else "Marshal"

	# Show the capture message in log first
	if response.has("message"):
		add_output("[color=#" + COLOR_CONQUEST + "]" + response.message + "[/color]")

	# Update status/map from the response
	if response.has("action_summary"):
		_update_status(response.action_summary)
	if response.has("game_state") and response.game_state.has("gold"):
		gold = int(response.game_state.gold)
		_update_gold_display()
	if response.has("game_state") and response.game_state.has("manpower_pools"):
		_apply_manpower(response.game_state.manpower_pools)
	if response.has("game_state") and response.game_state.has("map_data"):
		map_area.update_all_regions(response.game_state.map_data)

	add_output("")
	add_output("[color=#" + COLOR_GOLD + "]Your forces await orders: Plunder or Secure?[/color]")
	add_output("")

	if capture_choice_dialog == null:
		push_error("capture_choice_dialog is NULL! Cannot show dialog.")
		add_output("[color=#" + COLOR_ERROR + "]ERROR: Capture choice dialog not loaded![/color]")
		set_input_enabled(true)
		return

	capture_choice_dialog.show_capture_choice(capture_data)


func _on_capture_choice_made(choice: String):
	"""Handle player's plunder/secure choice."""
	set_input_enabled(false)

	var choice_text = ""
	if choice == "plunder":
		choice_text = "You order your troops to plunder the region!"
		add_output("[color=#" + COLOR_BATTLE + "]" + choice_text + "[/color]")
	else:
		choice_text = "You order your troops to secure the region."
		add_output("[color=#" + COLOR_SUCCESS + "]" + choice_text + "[/color]")
	add_output("")

	api_client.send_capture_choice_response(choice, _on_capture_choice_response)


func _on_capture_choice_response(response):
	"""Handle backend response after player makes plunder/secure choice."""
	set_input_enabled(true)

	if response.success:
		if response.has("action_summary"):
			_update_status(response.action_summary)
		if response.has("game_state") and response.game_state.has("gold"):
			gold = int(response.game_state.gold)
			_update_gold_display()
		if response.has("game_state") and response.game_state.has("manpower_pools"):
			_apply_manpower(response.game_state.manpower_pools)
		if response.has("game_state") and response.game_state.has("map_data"):
			map_area.update_all_regions(response.game_state.map_data)

		add_output("[color=#" + COLOR_SUCCESS + "]" + response.message + "[/color]")

		if response.has("game_state") and response.game_state.has("game_over"):
			if response.game_state.game_over:
				_show_game_over_screen(response.game_state)
				return
	else:
		add_output("[color=#" + COLOR_ERROR + "]" + response.message + "[/color]")

	add_output("")
	command_input.grab_focus()


# ════════════════════════════════════════════════════════════════════════════
# LOAD GAME DIALOG (Phase 6: Save/Load)
# ════════════════════════════════════════════════════════════════════════════

func _show_load_dialog():
	"""Fetch saves from backend and show load dialog."""
	if load_dialog == null:
		add_output("[color=#" + COLOR_ERROR + "]Load dialog not available.[/color]")
		return
	api_client.list_saves(_on_saves_listed)

func _on_saves_listed(response):
	"""Handle saves list response from backend."""
	if response.success and response.has("saves"):
		load_dialog.show_saves(response.saves)
	else:
		add_output("[color=#" + COLOR_ERROR + "]Failed to list saves.[/color]")
		set_input_enabled(true)

func _on_load_save_selected(filename: String):
	"""Player selected a save to load."""
	set_input_enabled(false)
	add_output("[color=#" + COLOR_INFO + "]Loading save...[/color]")
	api_client.load_game(filename, _on_load_result)

func _on_load_result(response):
	"""Handle load result from backend."""
	set_input_enabled(true)
	if response.success:
		# Refresh entire display from new game state
		if response.has("game_state"):
			var gs = response.game_state
			if gs.has("map_data"):
				map_area.update_all_regions(gs.map_data)
			if gs.has("gold"):
				gold = int(gs.gold)
				_update_gold_display()
			if gs.has("manpower_pools"):
				_apply_manpower(gs.manpower_pools)
			if gs.has("turn"):
				current_turn = int(gs.turn)
				turn_value.text = str(current_turn)
			if gs.has("actions_remaining"):
				actions_remaining = int(gs.actions_remaining)
			if gs.has("max_actions"):
				max_actions = int(gs.max_actions)
			if gs.has("admin_actions_remaining"):
				admin_actions_remaining = int(gs.admin_actions_remaining)
			if gs.has("max_admin_actions"):
				max_admin_actions = int(gs.max_admin_actions)
			# Update actions display
			actions_value.text = "%d / %d" % [actions_remaining, max_actions]
			admin_value.text = "%d / %d" % [admin_actions_remaining, max_admin_actions]

		add_output("[color=#" + COLOR_SUCCESS + "]Game loaded successfully.[/color]")
		add_output("[color=#" + COLOR_INFO + "]" + response.get("message", "") + "[/color]")
	else:
		add_output("[color=#" + COLOR_ERROR + "]Load failed: " + response.get("message", "Unknown error") + "[/color]")
	add_output("")
	command_input.grab_focus()

func _on_load_cancelled():
	"""Player cancelled the load dialog."""
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
		if response.has("game_state") and response.game_state.has("manpower_pools"):
			_apply_manpower(response.game_state.manpower_pools)

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


# ════════════════════════════════════════════════════════════════════════════
# STRATEGIC COMMAND UI (Phase J)
# ════════════════════════════════════════════════════════════════════════════

func _show_strategic_reports(response):
	"""Show strategic order reports popup after enemy phase."""
	var reports = response.get("strategic_reports", [])
	if reports.is_empty():
		_on_strategic_report_dismissed()
		return

	if strategic_report_popup == null:
		push_error("strategic_report_popup is NULL!")
		_on_strategic_report_dismissed()
		return

	var turn = current_turn
	if response.has("action_summary"):
		turn = int(response.action_summary.get("turn", current_turn))

	# Log reports to output too
	add_output("")
	add_output("[color=#" + COLOR_GOLD + "]--- Strategic Order Updates ---[/color]")
	for report in reports:
		var marshal_name = report.get("marshal", "")
		var msg = report.get("message", "")
		if msg:
			add_output("[color=#" + COLOR_INFO + "]" + marshal_name + ": " + msg + "[/color]")
		# Log sally battle details to output
		var battle_msg = report.get("battle_message", "")
		if battle_msg:
			add_output("[color=#" + COLOR_BATTLE + "]  " + battle_msg + "[/color]")
		var outcome = report.get("outcome", "")
		if outcome:
			var outcome_color = COLOR_SUCCESS if outcome == "victory" else COLOR_ERROR if outcome == "defeat" else COLOR_BATTLE
			add_output("[color=#" + outcome_color + "]  Result: " + outcome.capitalize() + "[/color]")
	add_output("")

	strategic_report_popup.show_reports(reports, turn)


func _on_strategic_report_dismissed():
	"""Handle strategic report popup dismissed."""
	print("Strategic report popup dismissed")

	# Check if any reports have interrupts that need input
	if pending_strategic_response != null:
		var response = pending_strategic_response
		var reports = response.get("strategic_reports", [])

		# Queue up any interrupts that require input
		interrupt_queue.clear()
		for report in reports:
			if report.get("requires_input", false):
				interrupt_queue.append(report)

		# Show first interrupt if any
		if not interrupt_queue.is_empty():
			var first_interrupt = interrupt_queue.pop_front()
			_show_interrupt_popup(first_interrupt)
			return  # Don't re-enable input yet

		# Check for game over
		if response.has("game_state") and response.game_state.has("game_over"):
			if response.game_state.game_over:
				pending_strategic_response = null
				_show_game_over_screen(response.game_state)
				return

	pending_strategic_response = null
	pending_enemy_phase_response = null
	set_input_enabled(true)
	command_input.grab_focus()


func _show_interrupt_popup(interrupt_data: Dictionary):
	"""Show interrupt popup for a marshal needing a decision."""
	set_input_enabled(false)

	if interrupt_popup == null:
		push_error("interrupt_popup is NULL!")
		add_output("[color=#" + COLOR_ERROR + "]ERROR: Interrupt popup not loaded![/color]")
		_process_next_interrupt()
		return

	var marshal_name = interrupt_data.get("marshal", "Marshal")
	add_output("[color=#" + COLOR_BATTLE + "]" + marshal_name + " awaits your orders![/color]")

	interrupt_popup.show_interrupt(interrupt_data)


func _on_interrupt_choice_made(marshal_name: String, response_type: String, choice: String):
	"""Handle player choosing an interrupt response."""
	print("Interrupt choice: marshal=%s, type=%s, choice=%s" % [marshal_name, response_type, choice])
	set_input_enabled(false)

	add_output("[color=#" + COLOR_COMMAND + "]> " + marshal_name + ": " + choice.replace("_", " ") + "[/color]")

	# Send to backend
	api_client.send_strategic_response(marshal_name, response_type, choice, _on_interrupt_response)


func _on_interrupt_response(response):
	"""Handle backend response to interrupt choice."""
	if response.success:
		var msg = response.get("message", "Order acknowledged.")
		add_output("[color=#" + COLOR_SUCCESS + "]" + msg + "[/color]")

		# Update UI state
		if response.has("action_summary"):
			_update_status(response.action_summary)
		if response.has("game_state") and response.game_state.has("gold"):
			gold = int(response.game_state.gold)
			_update_gold_display()
		if response.has("game_state") and response.game_state.has("manpower_pools"):
			_apply_manpower(response.game_state.manpower_pools)
		if response.has("game_state") and response.game_state.has("map_data"):
			map_area.update_all_regions(response.game_state.map_data)
	else:
		add_output("[color=#" + COLOR_ERROR + "]" + response.get("message", "Error processing response.") + "[/color]")

	# Process next interrupt in queue
	_process_next_interrupt()


func _process_next_interrupt():
	"""Show next queued interrupt or re-enable input."""
	if not interrupt_queue.is_empty():
		var next_interrupt = interrupt_queue.pop_front()
		_show_interrupt_popup(next_interrupt)
	else:
		# All interrupts processed
		pending_strategic_response = null
		pending_enemy_phase_response = null
		set_input_enabled(true)
		command_input.grab_focus()


func _show_clarification_popup(response):
	"""Show clarification popup for literal marshals."""
	set_input_enabled(false)

	var data = response.get("clarification_data", response)

	if clarification_popup == null:
		push_error("clarification_popup is NULL!")
		add_output("[color=#" + COLOR_ERROR + "]ERROR: Clarification popup not loaded![/color]")
		set_input_enabled(true)
		return

	var marshal_name = data.get("marshal", "Marshal")
	add_output("[color=#" + COLOR_MARSHAL + "]" + marshal_name + " requests clarification...[/color]")

	clarification_popup.show_clarification(data)


func _on_clarification_choice_made(marshal_name: String, chosen_target: String, strategic_type: String):
	"""Handle player selecting a clarification target."""
	print("Clarification choice: marshal=%s, target=%s, type=%s" % [marshal_name, chosen_target, strategic_type])
	add_output("[color=#" + COLOR_COMMAND + "]> " + marshal_name + ", target " + chosen_target + "[/color]")

	# Reissue with correct strategic keyword for the command type
	var keyword_map = {
		"PURSUE": "pursue",
		"MOVE_TO": "march to",
		"SUPPORT": "support",
		"HOLD": "hold",
	}
	var keyword = keyword_map.get(strategic_type, "pursue")
	var clarified_command = marshal_name + " " + keyword + " " + chosen_target
	set_input_enabled(false)
	api_client.send_command(clarified_command, _on_command_result)


func _on_clarification_cancelled():
	"""Handle player cancelling a clarification."""
	add_output("[color=#" + COLOR_INFO + "]Order cancelled.[/color]")
	set_input_enabled(true)
	command_input.grab_focus()
