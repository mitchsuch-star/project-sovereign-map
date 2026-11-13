extends PopupBase

# =============================================================================
# PROJECT SOVEREIGN - Strategic Interrupt Popup (R15 migrated)
# =============================================================================
# Displays when a marshal's strategic order hits an interrupt requiring
# player input: cannon fire, blocked path, contact, ally moving.
# Buttons are generated dynamically from the interrupt's options list.
# =============================================================================

signal choice_made(marshal_name: String, response_type: String, choice: String)

# UI References
@onready var title_label = $PanelContainer/VBoxContainer/TitleLabel
# S14D-X47 (October 23, 2026): the message stands in a ScrollContainer — the
# one unbounded child. A long muster (the `muster_confirm` gate road, nine
# lines and the free preview) grew the plain Label past the viewport and
# carried BOTH answers off the screen at 1.0 and 2.0, the message itself
# unseen at 2.0 — an undismissable modal (the re-shot frame found it).
# The message is a RichTextLabel with BBCode OFF (as literal as the plain
# Label it replaces — the producer still emits no markup, WO slice 8 [V-3]):
# the frame record reads a RichTextLabel line by line, so the lines a
# scrolling message shows are recorded as seen (a plain Label is recorded
# only when its WHOLE rect stands inside the window).
@onready var message_scroll = $PanelContainer/VBoxContainer/MessageScroll
@onready var message_label = $PanelContainer/VBoxContainer/MessageScroll/MessageLabel
@onready var button_container = $PanelContainer/VBoxContainer/ButtonContainer

# S14D-X47: the box may grow to the layer-50 screens' height for a long
# message before the message scrolls; a short question still shrinks to fit.
const MESSAGE_CEILING := Vector2(600.0, 620.0)
# The least room the message keeps when the box is at its budget.
const MESSAGE_MIN_ROOM := 72.0

# Current interrupt data
var current_marshal: String = ""
var current_response_type: String = ""

# Human-readable labels for option IDs
const OPTION_LABELS = {
	"attack": "Attack!",
	"attack_anyway": "Commit the Attack",
	"go_around": "Go Around",
	"hold_position": "Hold Position",
	"cancel_order": "Cancel Order",
	"investigate": "March to the Guns",
	"continue_order": "Continue as Ordered",
	"attack_again": "Attack Again",
	"follow": "Follow Ally",
	"hold_current": "Hold Current Position",
	"cancel_support": "Cancel Support",
	"fight_to_the_last": "Fight to the Last",
	"attempt_breakout": "Attempt a Breakout",
}

# SF7-X27 (Score Finish Step 7, the frames, Oct 5 2026): the panel is
# authored as a fixed 600x360 rect, so a two-line question ("Teulie is
# cornered at Milan... He asks leave to fight to the last") sat on top of
# ~130px of empty panel below its buttons. After the clamp (which keeps the
# authored rect as the CEILING), the panel shrinks to what its content
# needs — never past the clamp, and re-centred. False = the fixed rect.
const THE_QUESTION_FITS_ITS_BOX := true

func _ready():
	hide()

func show_interrupt(interrupt_data: Dictionary):
	"""Display interrupt popup with dynamic buttons."""
	# UI-5: an arrival sound — claimed, so it goes with the card
	claim_cue(AudioManager.play("drum_sting"))
	current_marshal = interrupt_data.get("marshal", "Marshal")
	current_response_type = interrupt_data.get("interrupt_type", "unknown")

	# Title
	title_label.text = current_marshal.to_upper() + " REPORTS"
	# Session UI-2: the drum above the report — the field speaks.
	_arms_row([{"glyph": "drum"}])

	# Message
	var message = interrupt_data.get("message", "Awaiting your orders, Sire.")
	message_label.text = '"%s"' % message

	# Clear existing buttons
	for child in button_container.get_children():
		child.queue_free()

	# Create buttons from options
	var options = interrupt_data.get("options", [])
	if options.is_empty():
		# Fallback: just a continue button
		options = ["continue_order"]

	for option_id in options:
		var btn = Button.new()
		btn.custom_minimum_size = Vector2(0, 45)
		btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		btn.text = OPTION_LABELS.get(option_id, option_id.replace("_", " ").capitalize())
		# FA-49: and what it costs. Two of the three cannon-fire buttons are
		# charged in trust and the popup stated no price — measured, the ask
		# fires every other turn per marshal and 19 times across the archived
		# campaigns, so a player could pay 36 trust without ever seeing a
		# figure. The costs ride their OWN payload key, not the label map:
		# `OPTION_LABELS` is pinned as a flat dict of strings one file over,
		# and `options` is a list of strings validated by the backend, so
		# neither may become a dict. Plain text — the button has no BBCode.
		var _costs = interrupt_data.get("option_costs", {})
		if typeof(_costs) == TYPE_DICTIONARY and _costs.has(option_id):
			var _cost = int(_costs[option_id])
			if _cost != 0:
				btn.text += "  (trust %d)" % _cost

		# Session UI-2: the buttons wear the theme's gilt face (the colour
		# overrides that stood here beat its words). A report that offers ONE
		# answer has a clear default — it is the primary; a choice has none.
		if options.size() == 1:
			btn.theme_type_variation = &"PrimaryButton"

		# Bind the option_id to the callback
		btn.pressed.connect(_on_option_pressed.bind(option_id))
		# UI-5: the answer plays its own cue (command_ack / latch)
		btn.set_meta("no_click_sfx", true)
		button_container.add_child(btn)

	_banner("interrupt")
	show()
	# S14D-X47: a long message may raise the clamp's ceiling (IGR-G1's meta);
	# the fit below still shrinks a short question to its box.
	$PanelContainer.set_meta("clamp_ceiling_override", MESSAGE_CEILING)
	# July 18, 2026 viewport sweep: fit to the CURRENT logical viewport.
	# Interface Scale (content_scale_factor, up to 2.0) divides the logical
	# viewport, so a fixed authored rect can carry the action row off-screen
	# and leave a modal undismissable. The helper is a no-op wherever the
	# panel already fits, and returns early for non-centre-anchored panels.
	Utils.clamp_centered_panel($PanelContainer)
	if THE_QUESTION_FITS_ITS_BOX:
		# Deferred: the label's text and the new buttons are measured once
		# the containers have sorted this frame's changes.
		call_deferred("_fit_to_content")


func _fit_to_content() -> void:
	"""SF7-X27: shrink the centred panel to its content's height (the clamp
	above already fitted it to the viewport; this only ever SHRINKS).

	It waits for the containers to sort first: the frame the text is set,
	the message label has no width yet and wraps per character — measured,
	a combined minimum of 3,328px that frame and 208px two frames later — so
	a fit read at once never shrinks anything (the first cut did exactly
	that, and the frame showed the box unchanged)."""
	await get_tree().process_frame
	await get_tree().process_frame
	var panel: Control = $PanelContainer
	if panel == null or not visible:
		return
	var have: float = panel.offset_bottom - panel.offset_top
	# S14D-X47: the message is the one unbounded child. Measure the box
	# without it, give it the room the clamp's budget leaves, and let it
	# scroll past that — the answers never leave the screen.
	if message_scroll != null:
		message_scroll.custom_minimum_size.y = 0.0
		var rest: float = panel.get_combined_minimum_size().y
		var text_h: float = message_label.get_combined_minimum_size().y
		var room: float = maxf(have - rest, MESSAGE_MIN_ROOM)
		message_scroll.custom_minimum_size.y = minf(text_h, room)
	var need: float = panel.get_combined_minimum_size().y
	if need > 0.0 and need < have:
		panel.offset_top = -need / 2.0
		panel.offset_bottom = need / 2.0

func refit() -> void:
	"""UXR-2: the live-refit road's hook (`Utils.refit_surface`). A generic
	re-clamp would regrow the panel to its authored 360 — the clamp, then
	the shrink-to-content, exactly as on open."""
	Utils.clamp_centered_panel($PanelContainer)
	if THE_QUESTION_FITS_ITS_BOX:
		call_deferred("_fit_to_content")


func _on_option_pressed(option_id: String):
	"""Handle player selecting an interrupt response option."""
	# UI-5: going on = the order acknowledged; halting / standing down = the latch
	var halts: bool = option_id in ["hold_position", "cancel_order", "hold_current", "cancel_support"]
	decided_with("latch" if halts else "command_ack")
	close_popup()
	choice_made.emit(current_marshal, current_response_type, option_id)


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
