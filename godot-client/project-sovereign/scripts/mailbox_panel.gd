extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Mailbox Panel
# =============================================================================
# Browsable inbox for pending diplomatic items. Real row controls make it easy
# to scan ACTIVE vs WAITING, source nation, item family, one-line summary, and
# arrival turn without leaning on one BBCode blob.
# =============================================================================

signal item_selected(mailbox_id: int, is_active: bool, item_type: String)
signal row_action(mailbox_id: int, action: String)
signal panel_closed

const ITEM_TYPE_DISPLAY = {
	"incoming_proposal": "Proposal",
	"counter_offer": "Counter-Offer",
	"counter_offer_response": "Counter Response",
}

@onready var background_overlay: ColorRect = $BackgroundOverlay
@onready var title_label: Label = $PanelContainer/VBoxContainer/TitleLabel
@onready var subtitle_label: Label = $PanelContainer/VBoxContainer/SubtitleLabel
@onready var list_content: VBoxContainer = $PanelContainer/VBoxContainer/ScrollContainer/ListContent
@onready var empty_state_label: Label = $PanelContainer/VBoxContainer/ScrollContainer/ListContent/EmptyStateLabel
@onready var close_btn: Button = $PanelContainer/VBoxContainer/ButtonContainer/CloseButton

const DEFAULT_SUBTITLE = "Every envoy still awaiting your answer. Select a row to reopen or activate it."

var _items: Array = []
# IGR-F: mailbox_id -> the letter-book row for that item. Only rows in this
# map get inline Accept/Decline; everything else keeps the click-to-open
# behaviour it has always had, so great-power and settlement traffic is
# untouched on this surface too.
var _digest_rows: Dictionary = {}


func _ready():
	hide()
	close_btn.pressed.connect(_on_close)
	background_overlay.gui_input.connect(_on_overlay_input)


func show_mailbox(data: Dictionary):
	var items = data.get("items", [])
	var count = int(data.get("count", 0))
	_items = items.duplicate()

	_digest_rows = {}
	var digest = data.get("envoy_digest")
	if typeof(digest) == TYPE_DICTIONARY:
		for row in digest.get("items", []):
			if typeof(row) == TYPE_DICTIONARY:
				_digest_rows[int(row.get("mailbox_id", 0))] = row

	if _digest_rows.is_empty():
		title_label.text = "PENDING ENVOYS (%d)" % count
		subtitle_label.text = DEFAULT_SUBTITLE
	else:
		title_label.text = "THE SMALL COURTS WRITE (%d)" % int(digest.get("count", _digest_rows.size()))
		var headline = Utils.humanize_nation_keys_in_text(str(digest.get("headline", "")))
		var deadline = str(digest.get("deadline_note", ""))
		subtitle_label.text = (headline + " " + deadline).strip_edges()
	_clear_rows()

	if items.is_empty():
		empty_state_label.visible = true
		show()
		return

	empty_state_label.visible = false
	for item in items:
		list_content.add_child(_build_item_row(item))

	show()
	# July 18, 2026 viewport sweep: fit to the CURRENT logical viewport.
	# Interface Scale (content_scale_factor, up to 2.0) divides the logical
	# viewport, so a fixed authored rect can carry the action row off-screen
	# and leave a modal undismissable. The helper is a no-op wherever the
	# panel already fits, and returns early for non-centre-anchored panels.
	Utils.clamp_centered_panel($PanelContainer)


func _build_item_row(item: Dictionary) -> PanelContainer:
	var state = str(item.get("state", "WAITING"))
	var source = str(item.get("source_nation", "Unknown"))
	var item_type = str(item.get("item_type", "unknown"))
	var summary = str(item.get("summary_text", item.get("summary", "Diplomatic item"))).strip_edges()
	var arrival_turn = int(item.get("arrival_turn", 0))
	var mailbox_id = int(item.get("mailbox_id", 0))
	var is_active = state == "ACTIVE"

	var panel = PanelContainer.new()
	panel.custom_minimum_size = Vector2(0, 74)
	panel.mouse_filter = Control.MOUSE_FILTER_STOP
	panel.set_meta("mailbox_id", mailbox_id)
	panel.set_meta("is_active", is_active)
	panel.set_meta("item_type", item_type)
	panel.gui_input.connect(_on_row_gui_input.bind(panel))

	var style = StyleBoxFlat.new()
	style.bg_color = Color(0.1, 0.12, 0.18, 0.96) if is_active else Color(0.07, 0.08, 0.12, 0.94)
	style.border_width_left = 1
	style.border_width_top = 1
	style.border_width_right = 1
	style.border_width_bottom = 1
	style.border_color = Color(0.5, 0.72, 0.86, 0.9) if is_active else Color(0.26, 0.3, 0.38, 0.9)
	style.corner_radius_top_left = 6
	style.corner_radius_top_right = 6
	style.corner_radius_bottom_right = 6
	style.corner_radius_bottom_left = 6
	style.content_margin_left = 12.0
	style.content_margin_top = 10.0
	style.content_margin_right = 12.0
	style.content_margin_bottom = 10.0
	panel.add_theme_stylebox_override("panel", style)

	var vbox = VBoxContainer.new()
	vbox.mouse_filter = Control.MOUSE_FILTER_IGNORE
	vbox.add_theme_constant_override("separation", 6)
	panel.add_child(vbox)

	var top_row = HBoxContainer.new()
	top_row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	top_row.add_theme_constant_override("separation", 8)
	vbox.add_child(top_row)

	var state_badge = Label.new()
	state_badge.text = "ACTIVE" if is_active else "WAITING"
	state_badge.mouse_filter = Control.MOUSE_FILTER_IGNORE
	state_badge.add_theme_font_size_override("font_size", 10)
	state_badge.add_theme_color_override(
		"font_color",
		Color(0.5, 0.72, 0.86, 1.0) if is_active else Color(0.66, 0.66, 0.7, 1.0)
	)
	top_row.add_child(state_badge)

	var source_label = Label.new()
	source_label.text = Utils.display_nation_name(source)
	source_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	source_label.add_theme_font_size_override("font_size", 13)
	source_label.add_theme_color_override("font_color", Color(0.88, 0.76, 0.38, 1.0))
	top_row.add_child(source_label)

	var spacer = Control.new()
	spacer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	top_row.add_child(spacer)

	var type_label = Label.new()
	type_label.text = ITEM_TYPE_DISPLAY.get(item_type, item_type.replace("_", " ").capitalize())
	type_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	type_label.add_theme_font_size_override("font_size", 11)
	type_label.add_theme_color_override("font_color", Color(0.74, 0.78, 0.86, 1.0))
	top_row.add_child(type_label)

	var turn_label = Label.new()
	turn_label.text = "Turn %d" % arrival_turn
	turn_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	turn_label.add_theme_font_size_override("font_size", 10)
	turn_label.add_theme_color_override("font_color", Color(0.56, 0.58, 0.64, 1.0))
	top_row.add_child(turn_label)

	var summary_label = Label.new()
	var summary_display = Utils.humanize_nation_keys_in_text(summary)
	summary_label.text = summary_display
	summary_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	summary_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	summary_label.add_theme_font_size_override("font_size", 11)
	summary_label.add_theme_color_override("font_color", Color(0.82, 0.82, 0.86, 1.0))
	summary_label.tooltip_text = summary_display
	vbox.add_child(summary_label)

	# IGR-F: a letter-book row carries the court's own spoken line and answers
	# in place. Volume is what was flattening these voices, so the digest
	# gives each one MORE room than the one-line summary it replaces, not less.
	var digest_row = _digest_rows.get(mailbox_id)
	if digest_row != null:
		panel.custom_minimum_size = Vector2(0, 0)
		var voice = str(digest_row.get("diplomat_line", "")).strip_edges()
		if voice != "":
			var voice_label = Label.new()
			voice_label.text = Utils.humanize_nation_keys_in_text(voice)
			voice_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
			voice_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			voice_label.add_theme_font_size_override("font_size", 12)
			voice_label.add_theme_color_override("font_color", Color(0.86, 0.8, 0.6, 1.0))
			vbox.add_child(voice_label)
		var clauses = digest_row.get("clauses", [])
		if clauses is Array and clauses.size() > 0:
			var terms_label = Label.new()
			var clause_strings: Array[String] = []
			for clause in clauses:
				clause_strings.append(str(clause))
			terms_label.text = "Terms: " + " · ".join(clause_strings)
			terms_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
			terms_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			terms_label.add_theme_font_size_override("font_size", 10)
			terms_label.add_theme_color_override("font_color", Color(0.68, 0.72, 0.8, 1.0))
			vbox.add_child(terms_label)
		vbox.add_child(_build_action_row(mailbox_id))

	return panel


func _build_action_row(mailbox_id: int) -> HBoxContainer:
	"""Accept / Decline for one letter, plus the way out to the full popup.

	The buttons are real Button nodes, so they stop the click themselves and
	the row's own gui_input never fires — which is what keeps the panel from
	closing on the first Accept. Clicking the row anywhere ELSE still opens
	the letter in full, so the counter-offer arm is never lost."""
	var row = HBoxContainer.new()
	row.add_theme_constant_override("separation", 8)

	var accept_btn = Button.new()
	accept_btn.text = "Accept"
	accept_btn.custom_minimum_size = Vector2(96, 28)
	accept_btn.pressed.connect(_on_row_action.bind(mailbox_id, "accept"))
	row.add_child(accept_btn)

	var decline_btn = Button.new()
	decline_btn.text = "Decline"
	decline_btn.custom_minimum_size = Vector2(96, 28)
	decline_btn.pressed.connect(_on_row_action.bind(mailbox_id, "reject"))
	row.add_child(decline_btn)

	var hint = Label.new()
	hint.text = "or click the letter to reply in full"
	hint.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hint.add_theme_font_size_override("font_size", 10)
	hint.add_theme_color_override("font_color", Color(0.56, 0.58, 0.64, 1.0))
	row.add_child(hint)

	return row


func _on_row_action(mailbox_id: int, action: String):
	set_row_buttons_enabled(false)
	row_action.emit(mailbox_id, action)


func set_row_buttons_enabled(enabled: bool):
	"""Latch every inline button while an answer is in flight.

	Without this a fast double-click sends two answers for one letter; the
	second lands after the first has already popped the dialogue, so it would
	be applied to whatever the queue promoted in its place."""
	for child in list_content.get_children():
		_set_buttons_enabled_recursive(child, enabled)


func _set_buttons_enabled_recursive(node: Node, enabled: bool):
	if node is Button:
		node.disabled = not enabled
	for child in node.get_children():
		_set_buttons_enabled_recursive(child, enabled)


func _on_row_gui_input(event: InputEvent, panel: PanelContainer):
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		hide()
		item_selected.emit(
			int(panel.get_meta("mailbox_id")),
			bool(panel.get_meta("is_active")),
			str(panel.get_meta("item_type"))
		)


func _clear_rows():
	for child in list_content.get_children():
		if child != empty_state_label:
			list_content.remove_child(child)
			child.queue_free()


func _on_overlay_input(event):
	if event is InputEventMouseButton and event.pressed:
		_on_close()


func _on_close():
	hide()
	panel_closed.emit()
