extends CanvasLayer

# =============================================================================
# INK & IRON - Pause Menu (Phase 6.5; Settings promoted → SettingsPanel,
# Main Menu pass position 6)
# =============================================================================
# Modal overlay triggered by Esc when no input is focused.
# Save / Load / New Campaign / Settings / Main Menu / Quit to Desktop.
#
# The Settings content is the SHARED SettingsPanel scene (settings_panel.gd) —
# the same component the Main Menu embeds — so the two surfaces can never
# drift. This script keeps only the frame: open/close, the confirm flow, and
# the ui_scale_changed forwarding contract main.gd already wires (main.gd owns
# applying scale: content_scale_factor + native-map compensation + persist).
# =============================================================================

signal save_requested
signal load_requested
signal new_game_requested
signal main_menu_requested
signal closed
# Re-emitted from the embedded SettingsPanel (UI-2 semantics: live-apply every
# step, persist at drag end / on click or keyboard change).
signal ui_scale_changed(value, persist)

# UI References
@onready var background_overlay = $BackgroundOverlay
@onready var save_button = $PanelContainer/VBoxContainer/SaveButton
@onready var load_button = $PanelContainer/VBoxContainer/LoadButton
@onready var new_game_button = $PanelContainer/VBoxContainer/NewGameButton
@onready var new_game_confirm_box = $PanelContainer/VBoxContainer/NewGameConfirmBox
@onready var confirm_new_game_button = $PanelContainer/VBoxContainer/NewGameConfirmBox/NewGameConfirmButtons/ConfirmNewGameButton
@onready var cancel_new_game_button = $PanelContainer/VBoxContainer/NewGameConfirmBox/NewGameConfirmButtons/CancelNewGameButton
@onready var settings_button = $PanelContainer/VBoxContainer/SettingsButton
@onready var settings_box = $PanelContainer/VBoxContainer/SettingsBox
@onready var main_menu_button = $PanelContainer/VBoxContainer/MainMenuButton
@onready var quit_button = $PanelContainer/VBoxContainer/QuitButton

var _settings_panel: SettingsPanel = null

func _ready():
	save_button.pressed.connect(_on_save)
	load_button.pressed.connect(_on_load)
	new_game_button.pressed.connect(_on_new_game)
	confirm_new_game_button.pressed.connect(_on_confirm_new_game)
	cancel_new_game_button.pressed.connect(_on_cancel_new_game)
	settings_button.pressed.connect(_on_settings)
	main_menu_button.pressed.connect(_on_main_menu)
	quit_button.pressed.connect(_on_quit)
	background_overlay.gui_input.connect(_on_overlay_input)
	# The shared Settings surface, in a scroll so the pause panel stays
	# inside small viewports at high Interface Scale.
	var scroll := ScrollContainer.new()
	scroll.custom_minimum_size = Vector2(0, 440)
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	settings_box.add_child(scroll)
	_settings_panel = (load("res://scenes/settings_panel.tscn") as PackedScene).instantiate()
	_settings_panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(_settings_panel)
	_settings_panel.ui_scale_changed.connect(func(v, p): ui_scale_changed.emit(v, p))
	_set_new_game_confirmation_visible(false)
	hide()

func open_menu():
	_reset_menu_state()
	AudioManager.play("door_open")
	# Re-sync every settings control from disk/backend: the command-window
	# "Text Size" +/- buttons write the same UiSettings scale value.
	if _settings_panel:
		_settings_panel.refresh()
	show()
	# July 18, 2026 viewport sweep: fit to the CURRENT logical viewport.
	Utils.clamp_centered_panel($PanelContainer)

func close_menu():
	_reset_menu_state()
	AudioManager.play("door_close")
	hide()
	closed.emit()

func _reset_menu_state():
	settings_box.visible = false
	_set_new_game_confirmation_visible(false)

func _set_new_game_confirmation_visible(confirm_visible: bool):
	new_game_confirm_box.visible = confirm_visible
	save_button.disabled = confirm_visible
	load_button.disabled = confirm_visible
	new_game_button.disabled = confirm_visible
	settings_button.disabled = confirm_visible
	main_menu_button.disabled = confirm_visible
	quit_button.disabled = confirm_visible
	if confirm_visible:
		settings_box.visible = false
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
	AudioManager.play("paper_crumple")  # the old campaign, crumpled and binned
	close_menu()
	new_game_requested.emit()

func _on_cancel_new_game():
	_set_new_game_confirmation_visible(false)
	new_game_button.grab_focus()

func _on_settings():
	settings_box.visible = not settings_box.visible
	# The settings content changes the panel's height class — re-fit.
	Utils.clamp_centered_panel($PanelContainer)

func _on_main_menu():
	close_menu()
	main_menu_requested.emit()

func _on_quit():
	get_tree().quit()

func _on_overlay_input(event):
	if event is InputEventMouseButton and event.pressed:
		close_menu()
