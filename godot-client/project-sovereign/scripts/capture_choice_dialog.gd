extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Capture Choice Dialog (Phase 6.2.E)
# =============================================================================
# Displays when player captures an enemy region.
# Player chooses: Plunder (gold + destroy buildings) or Secure (higher stability)
# W6-8 (Spoils of War): the same dialog also serves the second, estate stage
# (stage == "estate") — Confiscate the estate vs Respect the title.
# =============================================================================

signal choice_made(choice: String)

# UI References
@onready var panel_container = $PanelContainer
@onready var title_label = $PanelContainer/VBoxContainer/TitleLabel
@onready var region_label = $PanelContainer/VBoxContainer/RegionLabel
@onready var description_label = $PanelContainer/VBoxContainer/DescriptionLabel
@onready var plunder_button = $PanelContainer/VBoxContainer/ButtonContainer/PlunderButton
@onready var secure_button = $PanelContainer/VBoxContainer/ButtonContainer/SecureButton

var current_region: String = ""
var current_capturer: String = ""
var current_stage: String = "capture"  # "capture" or "estate" (W6-8)
var current_dialogue_id: int = -1      # W6-0 identity (stage 1 since IGR-E; estate stage since W6-8)

func _ready():
	# Connect button signals
	if plunder_button:
		plunder_button.pressed.connect(_on_plunder_pressed)
	else:
		push_error("CaptureChoiceDialog: PlunderButton is NULL!")

	if secure_button:
		secure_button.pressed.connect(_on_secure_pressed)
	else:
		push_error("CaptureChoiceDialog: SecureButton is NULL!")

	# UI-5: each answer plays its own cue (coin_pour / latch), so the global click stands aside
	if plunder_button:
		plunder_button.set_meta("no_click_sfx", true)
	if secure_button:
		secure_button.set_meta("no_click_sfx", true)

	# Hide by default
	hide()

func show_capture_choice(data: Dictionary):
	"""Display capture choice popup with data from backend."""
	AudioManager.play("cloth")
	var region_val = data.get("region")
	var capturer_val = data.get("capturer")

	current_region = region_val if region_val != null else "Unknown"
	current_capturer = capturer_val if capturer_val != null else "Marshal"
	current_stage = str(data.get("stage", "capture"))
	current_dialogue_id = int(data.get("dialogue_id", -1))

	if current_stage == "estate":
		# W6-8: the second question — the conquered province funds an
		# enemy marshal's estate.
		# FA-69: the DISPLAY forms, with the raw keys as a fallback so a save
		# taken before the backend stamped them still renders. Measured
		# before this: "Bohemia sustains Marshal ArchdukeCharles's household",
		# and the nation was interpolated without the R7 chokepoint, so a
		# formed nation was named by its dead tag.
		var holder = str(data.get("estate_holder_display", ""))
		if holder == "":
			holder = str(data.get("estate_holder", "the enemy marshal"))
		var holder_nation = str(data.get("estate_holder_nation_display", ""))
		if holder_nation == "":
			holder_nation = Utils.display_nation_name(
				str(data.get("estate_holder_nation", "their nation")))
		var windfall = int(data.get("windfall", 0))
		title_label.text = "AN ESTATE IN YOUR HANDS"
		_arms_row([{"glyph": "gold"}])
		region_label.text = "%s sustains Marshal %s's household" % [current_region, holder]
		description_label.text = "How shall the conqueror treat his title?"
		plunder_button.text = "CONFISCATE (+%s gold, %s will not forgive it)" % [Utils.format_number(windfall), holder_nation]
		secure_button.text = "RESPECT THE TITLE (%s will remember the courtesy)" % holder_nation
	else:
		# Set title
		title_label.text = "REGION CAPTURED!"
		_arms_row([{"glyph": "march"}])

		# Set region info
		region_label.text = "%s has taken %s" % [current_capturer, current_region]

		# Set description
		description_label.text = "How shall your forces treat the conquered territory?"
		# S14E-15: the formable road this capture stands on, said at the
		# question ("Ireland needs Ulster too — …"); absent key = no line.
		var road_note := str(data.get("road_note", ""))
		if road_note != "":
			description_label.text = road_note + ".\n" + description_label.text

		# Set button text with consequences.
		# IGR-E: the PLUNDER arm now quotes what it will actually pay. The
		# backend sends `plunder_gold` computed by the same expression that
		# pays it (world_state.plunder_yield), so this is shown=applied, not
		# an estimate. Post-landing review #4/#11: a payload that predates
		# the key (pre-IGR-E save whose load-time backfill could not resolve
		# the region) gets an UNPRICED label, never "+0 gold" for a choice
		# that pays the real sum; and the figure uses Utils.format_number so
		# the modal, terminal and outcome line all read "1,200" the same way.
		var plunder_gold = int(data.get("plunder_gold", 0))
		if data.has("plunder_gold"):
			plunder_button.text = "PLUNDER (+%s gold, buildings burned, stability 10)" % Utils.format_number(plunder_gold)
		else:
			plunder_button.text = "PLUNDER (loot the province, buildings burned, stability 10)"
		secure_button.text = "SECURE (Preserve order, stability 25, buildings damaged)"

	# Ensure all children are visible first
	if panel_container:
		panel_container.visible = true

	var bg_overlay = get_node_or_null("BackgroundOverlay")
	if bg_overlay:
		bg_overlay.visible = true

	# Show the CanvasLayer
	_banner("capture")
	show()
	_fit_compact()
	# July 18, 2026 viewport sweep: fit to the CURRENT logical viewport.
	# Interface Scale (content_scale_factor, up to 2.0) divides the logical
	# viewport, so a fixed authored rect can carry the action row off-screen
	# and leave a modal undismissable. The helper is a no-op wherever the
	# panel already fits, and returns early for non-centre-anchored panels.
	Utils.clamp_centered_panel($PanelContainer)
	visible = true
	# UXR3-X2 (Pre-Deploy S12): then shrink to the content (SF7-X27's fit).
	Utils.shrink_centered_panel_to_content($PanelContainer)

func refit() -> void:
	"""UXR-2's live-refit hook (`Utils.refit_surface`): the clamp, then the
	shrink to content, exactly as on open."""
	_fit_compact()
	Utils.clamp_centered_panel($PanelContainer)
	Utils.shrink_centered_panel_to_content($PanelContainer)


func _fit_compact() -> void:
	"""Session UI-4 (November 12, 2026): in the compact view (Interface Scale 2.0
	on a 900-px window: 800 wide) the two answers wrap inside equal halves — at
	the shipped 115 % their labels at their natural width ran the panel 796 px
	wide in an 800-px view (SF-RR5's 12-px margins). A full view keeps them on
	their own lines' widths, as before."""
	var compact := Utils.compact_view()
	for b in [plunder_button, secure_button]:
		var btn := b as Button
		if btn == null:
			continue
		btn.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART if compact else TextServer.AUTOWRAP_OFF
		if compact:
			btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL

func _on_plunder_pressed():
	"""Player chooses the first option (plunder / confiscate)."""
	AudioManager.play("coin_pour")
	hide()
	choice_made.emit("confiscate" if current_stage == "estate" else "plunder")

func _on_secure_pressed():
	"""Player chooses the second option (secure / respect)."""
	AudioManager.play("latch")  # UI-5: a departure sound — it IS the close
	hide()
	choice_made.emit("respect" if current_stage == "estate" else "secure")


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
		Utils.shrink_centered_panel_to_content($PanelContainer)


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
