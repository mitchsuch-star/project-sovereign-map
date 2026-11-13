extends CanvasLayer

# =============================================================================
# INK & IRON - Load Game Dialog (Phase 6: Save/Load; Session UI-5 restyle)
# =============================================================================
# Displays available save files for the player to load. Session UI-5: the rows
# are the save dialog's row cards (name, date or "Turn N", nation, the time it
# was saved; the campaign seed only in the row's hover), a click asks first
# ("Load <name> - <date>? Orders given since your last save are lost."), the
# title is the dialogs' title face, and the book opens and the door closes.
# =============================================================================

const SAVE_ROWS := preload("res://scripts/save_dialog.gd")

signal save_selected(filename: String)
signal load_cancelled()

# UI References
@onready var panel_container = $PanelContainer
@onready var title_label = $PanelContainer/VBoxContainer/TitleLabel
@onready var saves_container = $PanelContainer/VBoxContainer/ScrollContainer/SavesContainer
@onready var cancel_button = $PanelContainer/VBoxContainer/CancelButton

var _scroll: ScrollContainer = null
var _confirm_box: VBoxContainer = null
var _confirm_label: Label = null
var _confirm_filename := ""

func _ready():
	if cancel_button:
		cancel_button.pressed.connect(_on_cancel)
		cancel_button.set_meta("no_click_sfx", true)   # closing is the book_close cue
	if title_label:
		title_label.text = "Load a campaign"
		title_label.theme_type_variation = &"DialogTitle"
	_scroll = $PanelContainer/VBoxContainer/ScrollContainer
	_build_confirm()
	hide()

func _build_confirm() -> void:
	"""The card that asks before the world is swapped, above the Cancel button."""
	var vb: VBoxContainer = $PanelContainer/VBoxContainer
	_confirm_box = VBoxContainer.new()
	_confirm_box.name = "ConfirmBox"
	_confirm_box.add_theme_constant_override("separation", 8)
	_confirm_box.visible = false
	vb.add_child(_confirm_box)
	vb.move_child(_confirm_box, cancel_button.get_index())
	_confirm_label = Label.new()
	_confirm_label.theme_type_variation = &"BodyLarge"
	_confirm_label.add_theme_color_override("font_color", Utils.UI_GOLD_BRIGHT)
	_confirm_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_confirm_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_confirm_box.add_child(_confirm_label)
	var row := HBoxContainer.new()
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	row.add_theme_constant_override("separation", 12)
	_confirm_box.add_child(row)
	var yes := Button.new()
	yes.name = "ConfirmLoadButton"
	yes.text = "Load"
	yes.theme_type_variation = &"PrimaryButton"
	yes.custom_minimum_size = Vector2(120, 0)
	yes.set_meta("no_click_sfx", true)   # the door is its own cue
	yes.pressed.connect(_on_confirm_load)
	row.add_child(yes)
	var no := Button.new()
	no.name = "ConfirmCancelButton"
	no.text = "Cancel"
	no.custom_minimum_size = Vector2(120, 0)
	no.pressed.connect(_hide_confirm)
	row.add_child(no)

func show_saves(saves: Array, damaged: Array = []):
	"""Display load dialog with available saves — and, below them, the files
	the backend could not read (DD-C, Pre-Deploy S7b: a corrupt save used to
	vanish from this list without a word), disabled, with the reason."""
	# Clear old rows
	for child in saves_container.get_children():
		child.queue_free()
	_hide_confirm()

	if saves.is_empty() and damaged.is_empty():
		var label = Label.new()
		label.text = "No saves found."
		label.add_theme_color_override("font_color", Utils.UI_HINT_GREY)
		saves_container.add_child(label)
	else:
		for save_data in saves:
			if not (save_data is Dictionary):
				continue
			var meta = save_data.get("metadata", {})
			var turn_val = meta.get("turn") if meta is Dictionary else null
			# S14c part 4 (the walk): JSON numbers parse as floats in Godot —
			# a save listed as "Turn 6.0". Rule 2: every figure shown as an int.
			var display_turn = str(int(turn_val)) if turn_val != null else "?"
			# Tier 1 (DYNAMISM_SPEC §2): the campaign's seed — the metadata copy
			# save_manager has written since AI-0b; a pre-seed save reads
			# 'historical', which is the truth. Session UI-5: it rides the row's
			# hover (meta "campaign_seed"), not its face.
			saves_container.add_child(SAVE_ROWS.build_row(save_data, display_turn, _on_row_picked, Callable(), true))
		for bad in damaged:
			if not (bad is Dictionary):
				continue
			var holder := VBoxContainer.new()
			holder.add_theme_constant_override("separation", 2)
			var row = Button.new()
			row.text = "%s — damaged, cannot be loaded" % str(bad.get("filename", "?"))
			row.tooltip_text = str(bad.get("message", ""))
			row.disabled = true
			row.custom_minimum_size = Vector2(0, 40)
			holder.add_child(row)
			var reason := str(bad.get("message", ""))
			if reason != "":
				var reason_label := Label.new()
				reason_label.text = reason
				reason_label.theme_type_variation = &"Caption"
				reason_label.add_theme_color_override("font_color", Utils.UI_REASON_GREY)
				reason_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
				holder.add_child(reason_label)
			saves_container.add_child(holder)

	# Ensure visibility
	if panel_container:
		panel_container.visible = true
	var bg_overlay = get_node_or_null("BackgroundOverlay")
	if bg_overlay:
		bg_overlay.visible = true

	if _scroll != null:
		_scroll.custom_minimum_size.y = 110.0 if Utils.compact_view() else 250.0
	show()
	AudioManager.play("book_open")
	# July 18, 2026 viewport sweep: fit to the CURRENT logical viewport.
	# Interface Scale (content_scale_factor, up to 2.0) divides the logical
	# viewport, so a fixed authored rect can carry the action row off-screen
	# and leave a modal undismissable. The helper is a no-op wherever the
	# panel already fits, and returns early for non-centre-anchored panels.
	Utils.clamp_centered_panel($PanelContainer)
	visible = true

func _on_row_picked(filename: String, display_name: String) -> void:
	var date := ""
	for row in saves_container.get_children():
		if row.has_meta("save_filename") and str(row.get_meta("save_filename")) == filename:
			date = str(row.get_meta("save_date"))
	_confirm_filename = filename
	_confirm_label.text = "Load %s — %s? Orders given since your last save are lost." % [display_name, date]
	_confirm_box.visible = true
	if Utils.compact_view() and _scroll != null:
		_scroll.visible = false
	AudioManager.play("question")
	Utils.clamp_centered_panel($PanelContainer)

func _hide_confirm() -> void:
	_confirm_filename = ""
	if _confirm_box != null:
		_confirm_box.visible = false
	if _scroll != null:
		_scroll.visible = true

func _on_confirm_load() -> void:
	var filename := _confirm_filename
	if filename == "":
		return
	_hide_confirm()
	AudioManager.play("door_close")
	hide()
	save_selected.emit(filename)

func _unhandled_input(event: InputEvent) -> void:
	if not visible:
		return
	if event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		if _confirm_box != null and _confirm_box.visible:
			_hide_confirm()
		else:
			_on_cancel()

func _on_cancel():
	AudioManager.play("book_close")
	hide()
	load_cancelled.emit()
