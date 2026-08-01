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
# UI-2: emitted when the player moves the Interface Scale slider. main.gd owns
# applying it (content_scale_factor + native-map compensation + persistence).
# `persist` is false for the intermediate steps of a live drag (apply only) and
# true at drag end / for a click or keyboard change (apply AND save to disk).
signal ui_scale_changed(value, persist)

# True while the Interface Scale slider is being dragged (suppresses per-step
# disk writes; the final value persists on drag_ended).
var _scale_dragging := false

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
@onready var ui_scale_slider = $PanelContainer/VBoxContainer/SettingsBox/ScaleRow/UiScaleSlider
@onready var ui_scale_value = $PanelContainer/VBoxContainer/SettingsBox/ScaleRow/UiScaleValue
@onready var reset_scale_button = $PanelContainer/VBoxContainer/SettingsBox/ResetScaleButton
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
	# UI-2: initialize the Interface Scale slider from the saved preference and
	# wire it. `set_value_no_signal` avoids emitting a spurious change on boot.
	ui_scale_slider.min_value = UiSettings.MIN_UI_SCALE
	ui_scale_slider.max_value = UiSettings.MAX_UI_SCALE
	ui_scale_slider.step = UiSettings.UI_SCALE_STEP
	ui_scale_slider.set_value_no_signal(UiSettings.get_ui_scale())
	_update_scale_value_label(UiSettings.get_ui_scale())
	ui_scale_slider.value_changed.connect(_on_ui_scale_slider_changed)
	ui_scale_slider.drag_started.connect(_on_scale_drag_started)
	ui_scale_slider.drag_ended.connect(_on_scale_drag_ended)
	reset_scale_button.pressed.connect(_on_reset_scale)
	# BD: the Battle Diorama's sound toggle (the game's first audio) — built
	# in code so the settings box needs no scene surgery.
	var sfx_toggle := CheckButton.new()
	sfx_toggle.text = "Battle sounds"
	sfx_toggle.button_pressed = UiSettings.get_battle_sfx()
	sfx_toggle.toggled.connect(func(on): UiSettings.set_battle_sfx(on))
	settings_box.add_child(sfx_toggle)
	_add_asset_credits()
	_set_new_game_confirmation_visible(false)
	hide()

func _add_asset_credits():
	# UI-3: visible attribution for the shipped CC-BY asset (game-icons.net unit
	# silhouettes) — the licence requires end-user-visible credit. Phosphor is MIT
	# and the portraits/textures are PD/CC0 (credited for courtesy). Full terms:
	# repo-root THIRD_PARTY_LICENSES.md.
	var credit := Label.new()
	credit.name = "AssetCredits"
	credit.text = ("Unit icons by Lorc, Delapouite & contributors (game-icons.net, "
		+ "CC BY 3.0) · Interface icons: Phosphor (MIT) · Marshal portraits: "
		+ "public domain (Wikimedia Commons).")
	credit.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	credit.add_theme_font_size_override("font_size", 10)
	credit.add_theme_color_override("font_color", Utils.UI_TEXT_DIM)
	settings_box.add_child(credit)

func open_menu():
	_reset_menu_state()
	# Re-sync the slider from the saved scale: the command-window "Text Size"
	# +/- buttons write the same UiSettings value, so re-reading on open keeps
	# this slider from showing a stale figure after the player used them.
	ui_scale_slider.set_value_no_signal(UiSettings.get_ui_scale())
	_update_scale_value_label(UiSettings.get_ui_scale())
	show()
	# July 18, 2026 viewport sweep: fit to the CURRENT logical viewport.
	# Interface Scale (content_scale_factor, up to 2.0) divides the logical
	# viewport, so a fixed authored rect can carry the action row off-screen
	# and leave a modal undismissable. The helper is a no-op wherever the
	# panel already fits, and returns early for non-centre-anchored panels.
	Utils.clamp_centered_panel($PanelContainer)

func close_menu():
	_reset_menu_state()
	hide()
	closed.emit()

func _reset_menu_state():
	settings_box.visible = false
	_set_new_game_confirmation_visible(false)

func _set_new_game_confirmation_visible(visible: bool):
	new_game_confirm_box.visible = visible
	save_button.disabled = visible
	load_button.disabled = visible
	new_game_button.disabled = visible
	settings_button.disabled = visible
	quit_button.disabled = visible
	if visible:
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
	close_menu()
	new_game_requested.emit()

func _on_cancel_new_game():
	_set_new_game_confirmation_visible(false)
	new_game_button.grab_focus()

func _on_settings():
	settings_box.visible = not settings_box.visible

func _on_ui_scale_slider_changed(value: float):
	# Apply live every step; persist only when NOT mid-drag (i.e. a click on the
	# track or a keyboard step, which fire no drag_started/ended pair). Drag steps
	# persist once at drag_ended.
	_update_scale_value_label(value)
	ui_scale_changed.emit(value, not _scale_dragging)

func _on_scale_drag_started():
	_scale_dragging = true

func _on_scale_drag_ended(_value_changed: bool):
	_scale_dragging = false
	# Persist the settled value once, at drag end.
	ui_scale_changed.emit(ui_scale_slider.value, true)

func _on_reset_scale():
	# Snaps the slider to 1.0; value_changed fires only if it actually moved, so
	# emit explicitly to guarantee the reset applies (and persists) even when
	# already at 100%.
	if is_equal_approx(ui_scale_slider.value, UiSettings.DEFAULT_UI_SCALE):
		_update_scale_value_label(UiSettings.DEFAULT_UI_SCALE)
		ui_scale_changed.emit(UiSettings.DEFAULT_UI_SCALE, true)
	else:
		ui_scale_slider.value = UiSettings.DEFAULT_UI_SCALE

func _update_scale_value_label(value: float):
	ui_scale_value.text = "%d%%" % int(round(value * 100.0))

func _on_quit():
	get_tree().quit()

func _on_overlay_input(event):
	if event is InputEventMouseButton and event.pressed:
		close_menu()
