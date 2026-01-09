extends Control

# UI References
@onready var output_display = $VBoxContainer/OutputDisplay
@onready var command_input = $VBoxContainer/CommandInput
@onready var send_button = $VBoxContainer/SendButton

# API Client
var api_client = null

# Action economy tracking
var actions_remaining = 4
var max_actions = 4
var current_turn = 1
var max_turns = 40

func _ready():
	# Get references to UI nodes
	output_display = $VBoxContainer/OutputDisplay
	command_input = $VBoxContainer/CommandInput
	send_button = $VBoxContainer/SendButton
	
	# Create API client
	api_client = load("res://scripts/api_client.gd").new()
	add_child(api_client)
	
	# Connect signals ONLY if not already connected
	if not send_button.pressed.is_connected(_on_send_button_pressed):
		send_button.pressed.connect(_on_send_button_pressed)
	
	if not command_input.text_submitted.is_connected(_on_command_submitted):
		command_input.text_submitted.connect(_on_command_submitted)
	
	# Start disabled
	set_input_enabled(false)
	
	# Welcome message
	add_output("[b]PROJECT SOVEREIGN: Napoleonic Wars[/b]")
	add_output("[color=gray]Turn-based strategy with action economy[/color]")
	add_output("")
	
	# Test connection after a brief delay
	await get_tree().create_timer(0.5).timeout
	test_connection()

func test_connection():
	"""Test if backend is running."""
	add_output("Testing connection to Python backend...")
	api_client.test_connection(_on_connection_test)  

func _on_connection_test(response):
	"""Handle connection test response."""
	if response.success:
		add_output("[color=green]✓ Backend connected![/color]")
		add_output("")
		
		# Get initial game state
		if response.has("action_summary"):
			_update_action_display(response.action_summary)
		
		add_output("Type commands to control your marshals.")
		add_output("[color=gray]Examples: 'Ney, attack Wellington' or 'scout Rhine'[/color]")
		add_output("[color=gray]Type 'end turn' to skip remaining actions[/color]\n")
		
		set_input_enabled(true)
	else:
		add_output("[color=red]✗ Backend not running![/color]")
		add_output("Start the Python server first:")
		add_output("[color=gray]python backend/main.py[/color]\n")

func _on_send_button_pressed():
	"""Handle send button click."""
	_execute_command()

func _on_command_submitted(text: String):
	"""Handle enter key in command input."""
	_execute_command()

func _execute_command():
	"""Execute the command in the input field."""
	var command = command_input.text.strip_edges()
	
	if command.is_empty():
		return
	
	# Display command
	add_output("[color=cyan]> " + command + "[/color]")
	
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
		# Update action economy
		if response.has("action_summary"):
			_update_action_display(response.action_summary)
		
		# Display result
		add_output(response.message)
		
		# Show action info
		if response.has("action_info"):
			var action_info = response.action_info
			
			if action_info.has("turn_advanced") and action_info.turn_advanced:
				var turn_text = "═══ TURN %d BEGINS ═══" % int(action_info.new_turn)
				add_output("[color=yellow]" + turn_text + "[/color]")
				var available_text = "%d actions available" % int(max_actions)
				add_output("[color=green]" + available_text + "[/color]")
			else:
				if action_info.has("cost") and action_info.cost > 0:
					var actions_text = "Action used. %d/%d remaining" % [int(actions_remaining), int(max_actions)]
					add_output("[color=gray]" + actions_text + "[/color]")
		
		# Show events if any
		if response.has("events") and response.events.size() > 0:
			for event in response.events:
				if event.has("type"):
					add_output("[color=gray]  [" + event.type + "][/color]")
		
		add_output("")  # Blank line
	else:
		add_output("[color=red]Error: " + response.message + "[/color]")
		
		# Still update action display on error
		if response.has("action_summary"):
			_update_action_display(response.action_summary)
		
		add_output("")
	
	# Auto-focus input
	command_input.grab_focus()

func _update_action_display(action_summary):
	"""Update action economy variables from server response."""
	if action_summary.has("actions_remaining"):
		actions_remaining = int(action_summary.actions_remaining)
	
	if action_summary.has("max_actions"):
		max_actions = int(action_summary.max_actions)
	
	if action_summary.has("turn"):
		current_turn = int(action_summary.turn)
	
	if action_summary.has("max_turns"):
		max_turns = int(action_summary.max_turns)
	
	# Update window title (shows current state)
	get_tree().root.title = "Project Sovereign - Turn" + str(current_turn) + " - " + str(actions_remaining) + "/" + str(max_actions) + " actions"

func add_output(text: String):
	"""Add text to output display with BBCode support."""
	output_display.append_text(text + "\n")

func set_input_enabled(enabled: bool):
	"""Enable or disable command input."""
	command_input.editable = enabled
	send_button.disabled = not enabled
	
	if enabled:
		command_input.grab_focus()
