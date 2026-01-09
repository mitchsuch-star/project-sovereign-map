extends Control

# References to UI nodes
@onready var output_display = $VBoxContainer/OutputDisplay
@onready var command_input = $VBoxContainer/CommandInput
@onready var send_button = $VBoxContainer/SendButton

# API client
var api_client

func _ready():
	# Create API client
	api_client = load("res://scripts/api_client.gd").new()
	add_child(api_client)
	
	# Connect signals
	send_button.pressed.connect(_on_send_button_pressed)
	command_input.text_submitted.connect(_on_command_submitted)
	
	# Disable input while loading
	set_input_enabled(false)
	
	# Welcome message
	add_output("[b]PROJECT SOVEREIGN: Napoleonic Wars[/b]")
	add_output("Connecting to backend...\n")
	
	# Test connection
	await get_tree().create_timer(0.5).timeout
	test_connection()

func test_connection():
	add_output("[color=yellow]Testing backend connection...[/color]")
	api_client.send_command("status", _on_connection_test)

func _on_connection_test(response):
	if response.success:
		add_output("[color=green]✓ Backend connected![/color]")
		add_output("Type commands to control your marshals.")
		add_output("Example: 'Ney, attack Wellington'\n")
		set_input_enabled(true)
	else:
		add_output("[color=red]✗ Backend not running![/color]")
		add_output("Start the Python server first:")
		add_output("[color=gray]python backend/main.py[/color]\n")

func _on_send_button_pressed():
	_execute_command()

func _on_command_submitted(_text: String):
	_execute_command()

func _execute_command():
	var command = command_input.text.strip_edges()
	
	if command.is_empty():
		return
	
	# Display the command
	add_output("[color=cyan]> " + command + "[/color]")
	
	# Clear input and disable during processing
	command_input.clear()
	set_input_enabled(false)
	
	# Send to backend
	api_client.send_command(command, _on_command_result)

func _on_command_result(response):
	# Re-enable input
	set_input_enabled(true)
	
	if response.success:
		# Display result
		add_output(response.message)
		
		# Show events if any
		if response.has("events") and response.events.size() > 0:
			for event in response.events:
				if event.has("type"):
					add_output("[color=gray]  [" + event.type + "][/color]")
		
		add_output("")  # Blank line
	else:
		add_output("[color=red]Error: " + response.message + "[/color]\n")

func add_output(text: String):
	output_display.append_text(text + "\n")
	
	# Auto-scroll to bottom
	await get_tree().process_frame
	output_display.scroll_to_line(output_display.get_line_count())

func set_input_enabled(enabled: bool):
	command_input.editable = enabled
	send_button.disabled = not enabled
	
	if enabled:
		command_input.grab_focus()
