extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Pause Menu (Phase 6.5)
# =============================================================================
# Modal overlay triggered by Esc when no input is focused.
# Save/Load/Settings(stub)/Quit to Desktop.
# =============================================================================

signal save_requested
signal load_requested
signal new_game_requested
signal closed

# UI References
@onready var background_overlay = $BackgroundOverlay
@onready var save_button = $PanelContainer/VBoxContainer/SaveButton
@onready var load_button = $PanelContainer/VBoxContainer/LoadButton
@onready var new_game_button = $PanelContainer/VBoxContainer/NewGameButton
@onready var settings_button = $PanelContainer/VBoxContainer/SettingsButton
@onready var settings_stub = $PanelContainer/VBoxContainer/SettingsStub
@onready var quit_button = $PanelContainer/VBoxContainer/QuitButton

func _ready():
	save_button.pressed.connect(_on_save)
	load_button.pressed.connect(_on_load)
	new_game_button.pressed.connect(_on_new_game)
	settings_button.pressed.connect(_on_settings)
	quit_button.pressed.connect(_on_quit)
	background_overlay.gui_input.connect(_on_overlay_input)
	hide()

func open_menu():
	settings_stub.visible = false
	show()

func close_menu():
	settings_stub.visible = false
	hide()
	closed.emit()

func _on_save():
	close_menu()
	save_requested.emit()

func _on_load():
	close_menu()
	load_requested.emit()

func _on_new_game():
	close_menu()
	new_game_requested.emit()

func _on_settings():
	settings_stub.visible = true

func _on_quit():
	get_tree().quit()

func _on_overlay_input(event):
	if event is InputEventMouseButton and event.pressed:
		close_menu()
