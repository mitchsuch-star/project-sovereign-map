extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Settlement Editor Popup (SC-5R-2)
# =============================================================================
# Inline EDIT-mode editor for the settlement_confirm dialogue. Mounted when
# the staged review carries `can_edit_terms=true` and `editor_route`. Reads
# `available_clause_types[]` + `clause_control_schema` for picker contents,
# preserves drafts via the backend's scoped `draft_key` store, and submits
# authored packages through structured `propose_common_peace` POSTs.
# =============================================================================

signal submit_requested(payload: Dictionary)
signal back_out_requested(payload: Dictionary)

const COLOR_GOLD = "#d9c08c"
const COLOR_DIMMED = "#808080"
const COLOR_RED = "#e04040"
const COLOR_GREEN = "#80c080"

@onready var header_label: RichTextLabel = $PanelContainer/VBoxContainer/HeaderLabel
@onready var covered_enemies_container: HBoxContainer = $PanelContainer/VBoxContainer/CoveredEnemiesSection/CoveredEnemiesContainer
@onready var clause_list: VBoxContainer = $PanelContainer/VBoxContainer/ClauseSection/ClauseScroll/ClauseList
@onready var add_clause_selector: OptionButton = $PanelContainer/VBoxContainer/ClauseSection/AddClauseRow/AddClauseTypeSelector
@onready var add_clause_button: Button = $PanelContainer/VBoxContainer/ClauseSection/AddClauseRow/AddClauseButton
@onready var clause_editor_panel: VBoxContainer = $PanelContainer/VBoxContainer/ClauseSection/ClauseEditorPanel
@onready var clause_editor_label: Label = $PanelContainer/VBoxContainer/ClauseSection/ClauseEditorPanel/ClauseEditorLabel
@onready var clause_editor_fields: VBoxContainer = $PanelContainer/VBoxContainer/ClauseSection/ClauseEditorPanel/ClauseEditorFields
@onready var confirm_clause_button: Button = $PanelContainer/VBoxContainer/ClauseSection/ClauseEditorPanel/ClauseEditorActions/ConfirmClauseButton
@onready var cancel_clause_button: Button = $PanelContainer/VBoxContainer/ClauseSection/ClauseEditorPanel/ClauseEditorActions/CancelClauseButton
@onready var status_label: RichTextLabel = $PanelContainer/VBoxContainer/StatusLabel
@onready var back_out_button: Button = $PanelContainer/VBoxContainer/ActionRail/BackOutButton
@onready var submit_button: Button = $PanelContainer/VBoxContainer/ActionRail/SubmitForReviewButton

var current_data: Dictionary = {}
var editor_route: Dictionary = {}
var settlement_terms: Array = []
var covered_enemies: Array = []
var available_enemies: Array = []
var clause_control_schema: Dictionary = {}
var available_clause_types: Array = []
var pending_clause_type: String = ""
var pending_clause_field_controls: Dictionary = {}

func _ready():
	hide()
	add_clause_button.pressed.connect(_on_add_clause_pressed)
	confirm_clause_button.pressed.connect(_on_confirm_clause_pressed)
	cancel_clause_button.pressed.connect(_on_cancel_clause_pressed)
	submit_button.pressed.connect(_on_submit_pressed)
	back_out_button.pressed.connect(_on_back_out_pressed)

func show_editor(data: Dictionary):
	"""Mount the editor with a staged settlement_confirm payload that
	carries `can_edit_terms=true`, `editor_route`, `available_clause_types`,
	and `clause_control_schema`."""
	current_data = data.duplicate(true)
	editor_route = data.get("editor_route", {}) if data.get("editor_route") is Dictionary else {}
	# Seed terms from editor_route.staged_settlement_terms if present;
	# otherwise from the top-level settlement_terms.
	if editor_route.has("staged_settlement_terms"):
		var seeded = editor_route.get("staged_settlement_terms", [])
		settlement_terms = []
		if seeded is Array:
			for t in seeded:
				if t is Dictionary:
					settlement_terms.append(t.duplicate(true))
	else:
		settlement_terms = []
		var top_terms = data.get("settlement_terms", [])
		if top_terms is Array:
			for t in top_terms:
				if t is Dictionary:
					settlement_terms.append(t.duplicate(true))
	covered_enemies = []
	var covered_seed = editor_route.get("covered_enemy_participants", data.get("covered_enemy_participants", []))
	if covered_seed is Array:
		for n in covered_seed:
			covered_enemies.append(str(n))
	# Available enemies pool comes from the staged dialogue's display
	# chips (covered + uncovered) so the picker mirrors hostile-pair
	# eligibility from POST preview.
	available_enemies = []
	var covered_chips = data.get("covered_enemy_display_chips", [])
	if covered_chips is Array:
		for n in covered_chips:
			var ns = str(n)
			if ns != "" and ns not in available_enemies:
				available_enemies.append(ns)
	var uncovered_chips = data.get("uncovered_enemy_display_chips", [])
	if uncovered_chips is Array:
		for n in uncovered_chips:
			var ns = str(n)
			if ns != "" and ns not in available_enemies:
				available_enemies.append(ns)
	for n in covered_enemies:
		var ns = str(n)
		if ns != "" and ns not in available_enemies:
			available_enemies.append(ns)
	clause_control_schema = data.get("clause_control_schema", {})
	if not (clause_control_schema is Dictionary):
		clause_control_schema = {}
	available_clause_types = []
	var atypes = data.get("available_clause_types", editor_route.get("available_clause_types", []))
	if atypes is Array:
		for tname in atypes:
			available_clause_types.append(str(tname))
	pending_clause_type = ""
	pending_clause_field_controls = {}
	clause_editor_panel.visible = false
	_render_header()
	_render_covered_enemies()
	_render_clause_list()
	_populate_add_clause_selector()
	_render_status()
	show()

func _render_header():
	var war_label = str(current_data.get("war_label", current_data.get("war_id", "Settlement")))
	var selected_target = str(current_data.get("selected_target_nation", editor_route.get("selected_target_nation", "")))
	var source = str(editor_route.get("source", "explicit_revise"))
	var source_display = "Editing draft"
	match source:
		"rejected_review":
			source_display = "Editing rejected draft"
		"stale_recovery":
			source_display = "Editing recovered draft"
		_:
			source_display = "Editing draft"
	var bbcode = "[b][color=%s]%s — %s[/color][/b]\n" % [COLOR_GOLD, source_display, war_label]
	if selected_target != "":
		bbcode += "[color=#a0a0a8]Selected target: %s[/color]\n" % selected_target
	var draft_key = str(editor_route.get("draft_key", current_data.get("draft_key", "")))
	if draft_key != "":
		bbcode += "[color=#808080]Draft key: %s[/color]" % draft_key
	header_label.text = ""
	header_label.append_text(bbcode)

func _render_covered_enemies():
	for child in covered_enemies_container.get_children():
		child.queue_free()
	if available_enemies.is_empty():
		var none_label = Label.new()
		none_label.text = "(no eligible enemies)"
		none_label.add_theme_color_override("font_color", Color(COLOR_DIMMED))
		covered_enemies_container.add_child(none_label)
		return
	for nation in available_enemies:
		var check = CheckBox.new()
		check.text = str(nation)
		check.button_pressed = str(nation) in covered_enemies
		check.toggled.connect(_on_covered_enemy_toggled.bind(str(nation)))
		covered_enemies_container.add_child(check)

func _on_covered_enemy_toggled(pressed: bool, nation: String):
	if pressed:
		if nation not in covered_enemies:
			covered_enemies.append(nation)
	else:
		covered_enemies.erase(nation)
	_render_status()

func _render_clause_list():
	for child in clause_list.get_children():
		child.queue_free()
	if settlement_terms.is_empty():
		var empty = Label.new()
		empty.text = "(no clauses authored — Submit for Review is disabled)"
		empty.add_theme_color_override("font_color", Color(COLOR_DIMMED))
		clause_list.add_child(empty)
		return
	for i in range(settlement_terms.size()):
		var clause = settlement_terms[i]
		if not (clause is Dictionary):
			continue
		var row = HBoxContainer.new()
		row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var summary = _format_clause_summary(clause)
		var summary_label = Label.new()
		summary_label.text = summary
		summary_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row.add_child(summary_label)
		var remove_btn = Button.new()
		remove_btn.text = "Remove"
		remove_btn.pressed.connect(_on_remove_clause_pressed.bind(i))
		row.add_child(remove_btn)
		clause_list.add_child(row)

func _format_clause_summary(clause: Dictionary) -> String:
	var ttype = str(clause.get("type", ""))
	match ttype:
		"peace":
			return "Peace — end hostilities"
		"territory_cede":
			return "Territory: %s cedes %s to %s" % [
				str(clause.get("from", "?")),
				str(clause.get("region", "?")),
				str(clause.get("to", "?")),
			]
		"gold_indemnity":
			return "Gold indemnity: %s pays %s %s" % [
				str(clause.get("from", "?")),
				str(clause.get("amount", 0)),
				str(clause.get("to", "?")),
			]
		"gold_per_turn":
			return "Recurring gold: %s pays %s/turn for %s turns to %s" % [
				str(clause.get("from", "?")),
				str(clause.get("amount", 0)),
				str(clause.get("turns", 0)),
				str(clause.get("to", "?")),
			]
		"forced_alliance":
			var cs = " (incl. Continental System)" if bool(clause.get("includes_continental_system", false)) else ""
			return "Forced alliance: %s → %s%s" % [
				str(clause.get("from", "?")),
				str(clause.get("to", "?")),
				cs,
			]
		"vassalage", "subjugation", "liberation":
			return "%s: %s → %s" % [
				ttype.capitalize(),
				str(clause.get("from", "?")),
				str(clause.get("to", "?")),
			]
		_:
			return ttype.replace("_", " ").capitalize()

func _on_remove_clause_pressed(index: int):
	if index < 0 or index >= settlement_terms.size():
		return
	settlement_terms.remove_at(index)
	_render_clause_list()
	_render_status()

func _populate_add_clause_selector():
	add_clause_selector.clear()
	if available_clause_types.is_empty():
		add_clause_selector.add_item("(no clause types available)")
		add_clause_selector.disabled = true
		add_clause_button.disabled = true
		return
	add_clause_selector.disabled = false
	add_clause_button.disabled = false
	for ttype in available_clause_types:
		var label = _humanize_clause_type(str(ttype))
		add_clause_selector.add_item(label)
		var idx = add_clause_selector.item_count - 1
		add_clause_selector.set_item_metadata(idx, str(ttype))

func _humanize_clause_type(ttype: String) -> String:
	match ttype:
		"peace":
			return "Peace"
		"territory_cede":
			return "Territory cession"
		"gold_indemnity":
			return "Gold indemnity (lump sum)"
		"gold_per_turn":
			return "Recurring gold payment"
		"forced_alliance":
			return "Forced alliance"
		"vassalage":
			return "Vassalage"
		"subjugation":
			return "Subjugation"
		"liberation":
			return "Liberation"
		_:
			return ttype.replace("_", " ").capitalize()

func _on_add_clause_pressed():
	if available_clause_types.is_empty():
		return
	var idx = add_clause_selector.get_selected_id()
	if idx < 0:
		idx = add_clause_selector.selected
	if idx < 0:
		idx = 0
	var meta = add_clause_selector.get_item_metadata(idx)
	pending_clause_type = str(meta) if meta != null else str(available_clause_types[idx])
	clause_editor_label.text = "Add %s clause" % _humanize_clause_type(pending_clause_type)
	_render_clause_editor_fields(pending_clause_type)
	clause_editor_panel.visible = true

func _render_clause_editor_fields(ttype: String):
	for child in clause_editor_fields.get_children():
		child.queue_free()
	pending_clause_field_controls = {}
	var schema = clause_control_schema.get(ttype, {})
	if not (schema is Dictionary):
		schema = {}
	var fields = schema.get("fields", {})
	if not (fields is Dictionary):
		fields = {}
	# Special case: peace has no required user input.
	if ttype == "peace" and fields.is_empty():
		var info = Label.new()
		info.text = "Peace clause has no parameters."
		clause_editor_fields.add_child(info)
		return
	for field_name in fields.keys():
		var spec = fields.get(field_name, {})
		if not (spec is Dictionary):
			continue
		var control_kind = str(spec.get("control", "readonly"))
		var label_text = str(spec.get("label", field_name.replace("_", " ").capitalize()))
		var row = HBoxContainer.new()
		row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var lbl = Label.new()
		lbl.text = label_text + ":"
		lbl.custom_minimum_size = Vector2(140, 0)
		row.add_child(lbl)
		var control_node: Control = null
		match control_kind:
			"picker":
				var picker = OptionButton.new()
				picker.size_flags_horizontal = Control.SIZE_EXPAND_FILL
				var options = spec.get("options", [])
				if options is Array:
					for opt in options:
						if not (opt is Dictionary):
							continue
						var opt_label = str(opt.get("label", opt.get("id", "?")))
						var disabled = bool(opt.get("disabled", false))
						if disabled:
							opt_label += " (unavailable)"
						picker.add_item(opt_label)
						var oi = picker.item_count - 1
						picker.set_item_metadata(oi, str(opt.get("id", "")))
						picker.set_item_disabled(oi, disabled)
				control_node = picker
			"number":
				var spin = SpinBox.new()
				spin.size_flags_horizontal = Control.SIZE_EXPAND_FILL
				var min_v = spec.get("min", null)
				var max_v = spec.get("max", null)
				if min_v != null:
					spin.min_value = float(min_v)
				if max_v != null:
					spin.max_value = float(max_v)
				var default_v = spec.get("default", null)
				if default_v != null:
					spin.value = float(default_v)
				spin.step = 1.0
				spin.rounded = true
				control_node = spin
			"toggle":
				var toggle = CheckBox.new()
				toggle.text = ""
				toggle.button_pressed = bool(spec.get("default", false))
				control_node = toggle
			_:
				var ro = Label.new()
				ro.text = str(spec.get("default", ""))
				ro.add_theme_color_override("font_color", Color(COLOR_DIMMED))
				control_node = ro
		row.add_child(control_node)
		pending_clause_field_controls[field_name] = {"control": control_node, "kind": control_kind, "spec": spec}
		clause_editor_fields.add_child(row)

func _on_confirm_clause_pressed():
	if pending_clause_type == "":
		return
	var clause: Dictionary = {"type": pending_clause_type}
	for field_name in pending_clause_field_controls.keys():
		var record = pending_clause_field_controls[field_name]
		var control_node = record.get("control")
		var kind = str(record.get("kind", ""))
		match kind:
			"picker":
				if control_node is OptionButton:
					var idx = control_node.selected
					if idx >= 0:
						var meta = control_node.get_item_metadata(idx)
						clause[field_name] = str(meta) if meta != null else ""
			"number":
				if control_node is SpinBox:
					clause[field_name] = int(control_node.value)
			"toggle":
				if control_node is CheckBox:
					clause[field_name] = control_node.button_pressed
			_:
				pass
	# Sanity: territory_cede requires region; gold types require amount.
	# Reject empty critical fields with inline status feedback rather than
	# silently appending malformed clauses.
	var missing = []
	for field_name in pending_clause_field_controls.keys():
		var val = clause.get(field_name, "")
		if typeof(val) == TYPE_STRING and str(val) == "":
			missing.append(field_name)
	if not missing.is_empty():
		_set_status("[color=%s]Missing required field(s): %s[/color]" % [
			COLOR_RED,
			", ".join(PackedStringArray(missing)),
		])
		return
	settlement_terms.append(clause)
	pending_clause_type = ""
	pending_clause_field_controls = {}
	clause_editor_panel.visible = false
	_render_clause_list()
	_render_status()

func _on_cancel_clause_pressed():
	pending_clause_type = ""
	pending_clause_field_controls = {}
	clause_editor_panel.visible = false
	_set_status("")

func _render_status():
	var lines: Array = []
	var submit_enabled = true
	if settlement_terms.is_empty():
		lines.append("[color=%s]Author at least one clause to enable Submit for Review.[/color]" % COLOR_DIMMED)
		submit_enabled = false
	if covered_enemies.is_empty():
		lines.append("[color=%s]Cover at least one enemy to enable Submit for Review.[/color]" % COLOR_RED)
		submit_enabled = false
	if submit_enabled:
		lines.append("[color=%s]Ready to submit %d clause(s) for review.[/color]" % [
			COLOR_GREEN,
			settlement_terms.size(),
		])
	submit_button.disabled = not submit_enabled
	_set_status("\n".join(PackedStringArray(lines)))

func _set_status(text: String):
	status_label.text = ""
	status_label.append_text(text)

func _on_submit_pressed():
	var payload = {
		"action": "propose_common_peace",
		"war_id": str(current_data.get("war_id", editor_route.get("war_id", ""))),
		"selected_target_nation": str(current_data.get("selected_target_nation", editor_route.get("selected_target_nation", ""))),
		"covered_enemy_participants": covered_enemies.duplicate(),
		"settlement_terms": settlement_terms.duplicate(true),
		"draft_key": str(editor_route.get("draft_key", current_data.get("draft_key", ""))),
		"caller_kind": "player_editor",
	}
	hide()
	submit_requested.emit(payload)

func _on_back_out_pressed():
	# Back Out preserves the scoped draft via the backend's scoped store;
	# the editor surface emits the structured payload so main.gd can route
	# through `back_out_settlement` and the active dialogue manager.
	var payload = {
		"action": "back_out_settlement",
		"war_id": str(current_data.get("war_id", editor_route.get("war_id", ""))),
		"selected_target_nation": str(current_data.get("selected_target_nation", editor_route.get("selected_target_nation", ""))),
		"covered_enemy_participants": covered_enemies.duplicate(),
		"draft_key": str(editor_route.get("draft_key", current_data.get("draft_key", ""))),
	}
	hide()
	back_out_requested.emit(payload)

func close_editor():
	hide()

func is_open() -> bool:
	return visible
