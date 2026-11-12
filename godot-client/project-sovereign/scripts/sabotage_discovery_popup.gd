extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Sabotage Discovery Popup (Session 8C)
# =============================================================================
# Displays when player discovers Talleyrand modified their proposal.
# Two buttons: Confront / Overlook
# =============================================================================

signal choice_made(choice: String, data: Dictionary)

# UI References
@onready var content_label = $PanelContainer/VBoxContainer/ContentLabel
@onready var confront_btn = $PanelContainer/VBoxContainer/ButtonContainer/ConfrontButton
@onready var overlook_btn = $PanelContainer/VBoxContainer/ButtonContainer/OverlookButton

var current_data: Dictionary = {}

func _ready():
	hide()
	confront_btn.pressed.connect(_on_confront)
	overlook_btn.pressed.connect(_on_overlook)

func show_sabotage(data: Dictionary):
	"""Display sabotage discovery popup."""
	current_data = data
	var target = data.get("target_nation", "Unknown")
	var ordered = data.get("ordered_summary", "?")
	var delivered = data.get("delivered_summary", "?")
	var auth_bonus = data.get("authority_bonus_if_confronted", 5)
	var auth_penalty = data.get("authority_penalty_if_overlooked", 3)

	# Session UI-2: the Foreign Office speaks under France's arms and the
	# envoy's glyph; the heading in the title face.
	_arms_row([{"flag": "France"}, {"glyph": "envoy"}])
	var bbcode = ""
	bbcode += Utils.HEAD_OPEN + "TALLEYRAND'S DECEPTION DISCOVERED" + Utils.HEAD_CLOSE + "\n\n"
	bbcode += "[b]You ordered:[/b]  %s\n" % ordered
	bbcode += "[b]He delivered:[/b] %s\n\n" % delivered
	bbcode += "[b]How do you respond?[/b]\n\n"
	bbcode += Utils.bb_glyph("authority", 16) + " [color=#%s]Confront:[/color] Authority +%d, cooldown 5 turns\n" % [Utils.COLOR_GOLD, auth_bonus]
	bbcode += Utils.bb_glyph("authority", 16) + " [color=#%s]Overlook:[/color] Authority -%d" % [Utils.UI_SCORE_POSITIVE.to_html(false), auth_penalty]

	# S12: through `text`, never append_text (the instrument reads the label's text)
	content_label.text = Utils.humanize_nation_keys_in_text(bbcode)

	confront_btn.disabled = false
	overlook_btn.disabled = false
	show()
	# July 18, 2026 viewport sweep: fit to the CURRENT logical viewport.
	# Interface Scale (content_scale_factor, up to 2.0) divides the logical
	# viewport, so a fixed authored rect can carry the action row off-screen
	# and leave a modal undismissable. The helper is a no-op wherever the
	# panel already fits, and returns early for non-centre-anchored panels.
	Utils.clamp_centered_panel($PanelContainer)
	call_deferred("_fit_card")

func _on_confront():
	_disable_buttons()
	hide()
	choice_made.emit("confront", current_data)

func _on_overlook():
	_disable_buttons()
	hide()
	choice_made.emit("overlook", current_data)

func _disable_buttons():
	confront_btn.disabled = true
	overlook_btn.disabled = true


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
