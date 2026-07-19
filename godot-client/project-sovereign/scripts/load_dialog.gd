extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Load Game Dialog (Phase 6: Save/Load)
# =============================================================================
# Displays available save files for the player to load.
# Follows the same pattern as capture_choice_dialog.gd.
# =============================================================================

signal save_selected(filename: String)
signal load_cancelled()

# UI References
@onready var panel_container = $PanelContainer
@onready var title_label = $PanelContainer/VBoxContainer/TitleLabel
@onready var saves_container = $PanelContainer/VBoxContainer/ScrollContainer/SavesContainer
@onready var cancel_button = $PanelContainer/VBoxContainer/CancelButton

func _ready():
	if cancel_button:
		cancel_button.pressed.connect(_on_cancel)
	hide()

func show_saves(saves: Array):
	"""Display load dialog with available saves."""
	# Clear old buttons
	for child in saves_container.get_children():
		child.queue_free()

	if saves.is_empty():
		var label = Label.new()
		label.text = "No saves found."
		label.add_theme_color_override("font_color", Color(0.7, 0.7, 0.75, 1))
		saves_container.add_child(label)
	else:
		for save_data in saves:
			var btn = Button.new()
			var meta = save_data.get("metadata", {})
			var save_name_val = meta.get("save_name")
			var turn_val = meta.get("turn")
			var filename_val = save_data.get("filename", "")

			var display_name = save_name_val if save_name_val != null else "Unknown"
			var display_turn = str(turn_val) if turn_val != null else "?"

			btn.text = "%s (Turn %s)" % [display_name, display_turn]
			btn.custom_minimum_size = Vector2(0, 40)
			btn.add_theme_font_size_override("font_size", 14)
			btn.pressed.connect(_on_save_chosen.bind(filename_val))
			saves_container.add_child(btn)

	# Ensure visibility
	if panel_container:
		panel_container.visible = true
	var bg_overlay = get_node_or_null("BackgroundOverlay")
	if bg_overlay:
		bg_overlay.visible = true

	show()
	# July 18, 2026 viewport sweep: fit to the CURRENT logical viewport.
	# Interface Scale (content_scale_factor, up to 2.0) divides the logical
	# viewport, so a fixed authored rect can carry the action row off-screen
	# and leave a modal undismissable. The helper is a no-op wherever the
	# panel already fits, and returns early for non-centre-anchored panels.
	Utils.clamp_centered_panel($PanelContainer)
	visible = true

func _on_save_chosen(filename: String):
	hide()
	save_selected.emit(filename)

func _on_cancel():
	hide()
	load_cancelled.emit()
