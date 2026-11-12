extends PopupBase

# =============================================================================
# PROJECT SOVEREIGN - Commitment Paradox Popup (Deep Audit Session 8, R15 migrated)
# =============================================================================
# Shown when an attack forces France to choose between competing alliances.
# The player must either honor the defender or break faith with them.
# CanvasLayer 100 (modal). Standard registered-dialog popup pattern.
# =============================================================================

signal choice_made(choice: String, data: Dictionary)

# UI References
@onready var content_label = $PanelContainer/VBoxContainer/ContentLabel
@onready var honor_button = $PanelContainer/VBoxContainer/ButtonContainer/HonorButton
@onready var break_button = $PanelContainer/VBoxContainer/ButtonContainer/BreakButton

var _data: Dictionary = {}
var _choice_locked: bool = false


func _ready():
	hide()
	honor_button.pressed.connect(_on_honor_pressed)
	break_button.pressed.connect(_on_break_pressed)


func show_paradox(data: Dictionary):
	"""Display commitment paradox popup."""
	_data = data
	_choice_locked = false
	honor_button.visible = true
	break_button.visible = true
	honor_button.disabled = false
	break_button.disabled = false
	honor_button.theme_type_variation = &""
	var attacker = str(data.get("attacker", "?"))
	var defender = str(data.get("defender", "?"))
	var defender_alliance = str(data.get("defender_alliance", "?"))
	var message = str(data.get("message", ""))
	var attacker_display = Utils.display_nation_name(attacker)
	var defender_display = Utils.display_nation_name(defender)

	# Session UI-2: the two courts' flags either side of the quarrel, the
	# heading in the title face (red WORDS on dark, never UI_ALERT as text).
	_arms_row([{"flag": attacker}, {"glyph": "war"}, {"flag": defender}])
	var bbcode = ""
	bbcode += "[center][font=" + Utils.TITLE_FONT + "][color=#" \
		+ Utils.UI_SCORE_NEGATIVE_TEXT.to_html(false) + "]COMMITMENT PARADOX[/color][/font][/center]\n\n"
	if message:
		bbcode += message + "\n\n"
	else:
		bbcode += "Attacking %s would violate our %s.\n\n" % [defender_display, Utils.display_diplo_state(str(defender_alliance)).to_lower()]
	bbcode += Utils.bbcode_color(
		"Talleyrand: \"Europe watches how we honor one promise without disgracing another, Sire.\"",
		Utils.COLOR_INFO
	)

	honor_button.text = "Honor " + defender_display
	break_button.text = "Side with " + attacker_display

	# S12: through `text`, never append_text (the instrument reads the label's text)
	content_label.text = Utils.humanize_nation_keys_in_text(bbcode)
	show()
	# July 18, 2026 viewport sweep: fit to the CURRENT logical viewport.
	# Interface Scale (content_scale_factor, up to 2.0) divides the logical
	# viewport, so a fixed authored rect can carry the action row off-screen
	# and leave a modal undismissable. The helper is a no-op wherever the
	# panel already fits, and returns early for non-centre-anchored panels.
	Utils.clamp_centered_panel($PanelContainer)
	call_deferred("_fit_card")


func _on_honor_pressed():
	if _choice_locked:
		close_popup()
		return
	_show_after_choice_aside("honor_defender")
	choice_made.emit("honor_defender", _data)


func _on_break_pressed():
	if _choice_locked:
		close_popup()
		return
	_show_after_choice_aside("break_defender_alliance")
	choice_made.emit("break_defender_alliance", _data)


func _show_after_choice_aside(choice: String):
	_choice_locked = true
	var attacker = str(_data.get("attacker", "?"))
	var defender = str(_data.get("defender", "?"))
	var spurned = attacker if choice == "honor_defender" else defender
	var diplomat_key = "attacker_diplomat" if choice == "honor_defender" else "defender_diplomat"
	var diplomat = str(_data.get(diplomat_key, ""))
	if diplomat == "":
		diplomat = "The Chancery of " + Utils.display_nation_name(spurned)

	var aside = "\n\n" + Utils.bbcode_color(
		diplomat + ": \"The wound is recorded. Europe will remember which oath France chose.\"",
		Utils.COLOR_ERROR
	)
	aside += "\n" + Utils.bbcode_color(
		"Talleyrand: \"Then let the record show a choice, not confusion.\"",
		Utils.COLOR_INFO
	)
	content_label.text += aside
	honor_button.text = "Continue"
	# Session UI-2: the lone answer left is the primary act.
	honor_button.theme_type_variation = &"PrimaryButton"
	break_button.visible = false
	call_deferred("_fit_card")


func _fit_card() -> void:
	"""Session UI-2: the card shrinks to what it holds — the reading sizes to
	its own text (bounded), the clamp fits it to the viewport, then the panel
	shrinks to its content (the authored rect stood over a band of empty
	panel). After the layout has given the label its width (deferred)."""
	await get_tree().process_frame
	if not visible:
		return
	content_label.custom_minimum_size.y = clampf(content_label.get_content_height() + 12.0, 80.0, 300.0)
	Utils.clamp_centered_panel($PanelContainer)
	Utils.shrink_centered_panel_to_content($PanelContainer)


func refit() -> void:
	"""UXR-2's live-refit hook (`Utils.refit_surface`): the fit, as on open."""
	call_deferred("_fit_card")


func _arms_row(parts: Array) -> void:
	"""Session UI-2: the arms the voice speaks under (a court's flag, an
	office's glyph, the Empire's eagle) in one centred row above the title;
	an empty list hides the row. Built once, refilled on every show."""
	var vb: VBoxContainer = $PanelContainer/VBoxContainer
	var row: HBoxContainer = vb.get_node_or_null("ArmsRow") as HBoxContainer
	if row == null:
		row = HBoxContainer.new()
		row.name = "ArmsRow"
		row.alignment = BoxContainer.ALIGNMENT_CENTER
		row.add_theme_constant_override("separation", 12)
		row.mouse_filter = Control.MOUSE_FILTER_IGNORE
		vb.add_child(row)
		vb.move_child(row, 0)
	for c in row.get_children():
		row.remove_child(c)
		c.queue_free()
	for part in parts:
		var tex_path: String = ""
		var tint: Color = Color.WHITE
		var h: float = 26.0
		if part.has("flag"):
			tex_path = Utils.nation_flag_path(str(part["flag"]))
		elif part.has("glyph"):
			tex_path = Utils.glyph(str(part["glyph"]))
			tint = Utils.UI_GOLD
		elif part.has("eagle"):
			tex_path = Utils.EAGLE
			tint = Color(Utils.UI_GOLD, 0.92)
			h = 44.0
		if tex_path == "" or not ResourceLoader.exists(tex_path):
			continue
		var tex: Texture2D = load(tex_path)
		if tex == null or tex.get_height() <= 0:
			continue
		var art := TextureRect.new()
		art.texture = tex
		art.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		art.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		art.custom_minimum_size = Vector2(h * float(tex.get_width()) / float(tex.get_height()), h)
		art.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		art.modulate = tint
		art.mouse_filter = Control.MOUSE_FILTER_IGNORE
		row.add_child(art)
	# the compact view (Interface Scale 2.0) keeps its room for the answers
	row.visible = row.get_child_count() > 0 and not Utils.compact_view()
