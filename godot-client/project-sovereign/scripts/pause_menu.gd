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
@onready var new_game_confirm_box = $PanelContainer/VBoxContainer/NewGameConfirmBox
@onready var confirm_new_game_button = $PanelContainer/VBoxContainer/NewGameConfirmBox/NewGameConfirmButtons/ConfirmNewGameButton
@onready var cancel_new_game_button = $PanelContainer/VBoxContainer/NewGameConfirmBox/NewGameConfirmButtons/CancelNewGameButton
@onready var settings_button = $PanelContainer/VBoxContainer/SettingsButton
@onready var settings_stub = $PanelContainer/VBoxContainer/SettingsStub
@onready var quit_button = $PanelContainer/VBoxContainer/QuitButton

func _ready():
	save_button.pressed.connect(_on_save)
	load_button.pressed.connect(_on_load)
	new_game_button.pressed.connect(_on_new_game)
	confirm_new_game_button.pressed.connect(_on_confirm_new_game)
	cancel_new_game_button.pressed.connect(_on_cancel_new_game)
	settings_button.pressed.connect(_on_settings)
	quit_button.pressed.connect(_on_quit)
	background_overlay.gui_input.connect(_on_overlay_input)
	_set_new_game_confirmation_visible(false)
	hide()

func open_menu():
	_reset_menu_state()
	show()

func close_menu():
	_reset_menu_state()
	hide()
	closed.emit()

func _reset_menu_state():
	settings_stub.visible = false
	_set_new_game_confirmation_visible(false)

func _set_new_game_confirmation_visible(visible: bool):
	new_game_confirm_box.visible = visible
	save_button.disabled = visible
	load_button.disabled = visible
	new_game_button.disabled = visible
	settings_button.disabled = visible
	quit_button.disabled = visible
	if visible:
		settings_stub.visible = false
		confirm_new_game_button.grab_focus()

func _on_save():
	close_menu()
	save_requested.emit()

func _on_load():
	close_menu()
	load_requested.emit()

func _on_new_game():
	_set_new_game_confirmation_visible(true)

func _on_confirm_new_game():
	close_menu()
	new_game_requested.emit()

func _on_cancel_new_game():
	_set_new_game_confirmation_visible(false)
	new_game_button.grab_focus()

func _on_settings():
	settings_stub.visible = true

func _on_quit():
	get_tree().quit()

func _on_overlay_input(event):
	if event is InputEventMouseButton and event.pressed:
		close_menu()
