extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Vassal Rebellion Imminent Popup (Session 8C)
# =============================================================================
# Displays when a vassal's loyalty drops critically low.
# Three buttons: Invest / Show the Flag / Accept Risk
# (IQ-7 review [21]: "Send Garrison" promised a corps; none moves. The
# choice id stays "garrison" -> garrison_vassal_rebellion.)
# =============================================================================

signal choice_made(choice: String, data: Dictionary)

# UI References
@onready var content_label = $PanelContainer/VBoxContainer/ContentLabel
@onready var invest_btn = $PanelContainer/VBoxContainer/ButtonContainer/InvestButton
@onready var garrison_btn = $PanelContainer/VBoxContainer/ButtonContainer/GarrisonButton
@onready var accept_btn = $PanelContainer/VBoxContainer/ButtonContainer/AcceptButton

var current_data: Dictionary = {}

func _ready():
	hide()
	invest_btn.pressed.connect(_on_invest)
	garrison_btn.pressed.connect(_on_garrison)
	accept_btn.pressed.connect(_on_accept)
	# UI-5: each answer plays its own cue, so the global click stands aside
	for b in [invest_btn, garrison_btn, accept_btn]:
		(b as Button).set_meta("no_click_sfx", true)

# the grave bell the card opens on — an arrival sound, it goes with the card
var _open_cue = null  # untyped: a one-shot frees itself when it ends

func _answer(cue: String) -> void:
	AudioManager.stop_player(_open_cue)
	_open_cue = null
	AudioManager.play(cue)

func show_rebellion(data: Dictionary):
	"""Display vassal rebellion imminent popup."""
	AudioManager.stop_player(_open_cue)
	_open_cue = AudioManager.play("bell_toll")  # grave news
	current_data = data
	var nation = data.get("nation", "Unknown")
	var loyalty = data.get("loyalty", 0)
	var invest_cost = data.get("invest_cost_dp", 1)
	var invest_effect = data.get("invest_effect", "Loyalty +15")
	var garrison_effect = data.get("garrison_effect", "%d AP → Loyalty +10 now. No corps moves." % int(data.get("garrison_ap_cost", 2)))
	var accept_effect = data.get("accept_effect", "Rebellion may occur")

	# Session UI-2: the vassal's flag over the card; the heading in the title
	# face; the loyalty figure first, with its meter (red WORDS, not UI_ALERT).
	_arms_row([{"flag": str(nation)}])
	var bbcode = ""
	bbcode += Utils.HEAD_OPEN + "REBELLION IMMINENT" + Utils.HEAD_CLOSE + "\n"
	bbcode += "[color=#%s]%s loyalty: %d/100[/color] %s\n\n" % [
		Utils.UI_SCORE_NEGATIVE_TEXT.to_html(false), Utils.display_nation_name(str(nation)),
		loyalty, Utils.bb_meter(float(loyalty), 100.0, 120, 8, "8b2a2a")]
	bbcode += "[b]Invest (%d DP)[/b] — %s\n" % [invest_cost, invest_effect]
	# IQ-7 review [21]: the option says what it does — no corps moves (the
	# backend's own copy, which already names the AP cost; the header used
	# to double it and the button used to promise a garrison).
	bbcode += "[b]Show the Flag[/b] — %s\n" % garrison_effect
	bbcode += "[b]Accept the Risk[/b] — %s" % accept_effect

	# S12: through `text`, never append_text (the instrument reads the label's text)
	content_label.text = Utils.humanize_nation_keys_in_text(bbcode)

	invest_btn.disabled = false
	garrison_btn.disabled = false
	accept_btn.disabled = false
	_banner("rebellion")
	show()
	# July 18, 2026 viewport sweep: fit to the CURRENT logical viewport.
	# Interface Scale (content_scale_factor, up to 2.0) divides the logical
	# viewport, so a fixed authored rect can carry the action row off-screen
	# and leave a modal undismissable. The helper is a no-op wherever the
	# panel already fits, and returns early for non-centre-anchored panels.
	Utils.clamp_centered_panel($PanelContainer)
	call_deferred("_fit_card")

func _on_invest():
	_answer("quill_sign")  # the grant
	_disable_buttons()
	hide()
	choice_made.emit("invest", current_data)

func _on_garrison():
	_answer("drum_cadence")  # show the flag
	_disable_buttons()
	hide()
	choice_made.emit("garrison", current_data)

func _on_accept():
	_answer("back")
	_disable_buttons()
	hide()
	choice_made.emit("accept", current_data)

func _disable_buttons():
	invest_btn.disabled = true
	garrison_btn.disabled = true
	accept_btn.disabled = true


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


func _banner(surface: String) -> void:
	"""Session UI-5: the picture over the card (a 3:1 banner sized to the card's
	width; its hover is the credit). It steps aside on the compact view and in a
	short window, and `_banner_yield` takes it away again when the card's
	answers would otherwise leave the view."""
	var vb: VBoxContainer = $PanelContainer/VBoxContainer
	var old: Node = vb.get_node_or_null("Illustration")
	if old != null:
		vb.remove_child(old)
		old.queue_free()
	var view: Vector2 = get_viewport().get_visible_rect().size
	if Utils.compact_view() or view.y < 760.0:
		return
	var panel: Control = $PanelContainer
	var w: float = panel.offset_right - panel.offset_left
	if w <= 0.0:
		w = 480.0
	var pic: TextureRect = Illustrations.make_banner(surface, minf(w, view.x - 80.0) - 48.0, true)
	if pic == null:
		return
	vb.add_child(pic)
	vb.move_child(pic, 0)
	call_deferred("_banner_yield")


func _banner_yield() -> void:
	"""The banner is the first thing to give way: if the card cannot fit the
	view with it, it goes."""
	await get_tree().process_frame
	await get_tree().process_frame
	if not visible:
		return
	var pic: Control = $PanelContainer/VBoxContainer.get_node_or_null("Illustration") as Control
	if pic == null:
		return
	var view: Vector2 = get_viewport().get_visible_rect().size
	# Session UI-5: the banner shrinks first (it steps aside under its floor),
	# until the card stands centred below the top bar.
	if $PanelContainer.get_combined_minimum_size().y > Illustrations.card_room(view.y):
		Illustrations.fit_banner_to_card($PanelContainer, view.y)
		Utils.clamp_centered_panel($PanelContainer)


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
