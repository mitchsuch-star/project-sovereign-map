extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Marshal Redemption Dialog (the audience)
# =============================================================================
# Displays when a marshal's trust drops to critical levels (≤ 20)
# Player chooses: a task to prove himself, a post on the staff, dismissal —
# or, when an unpaid claim is the cause, the rente that pays him.
#
# Options are dynamically shown/hidden based on availability from backend:
# - A task to prove himself: Always available (row IC, Session 2b — it stands
#   where "Grant Autonomy" stood). HIS proposal is written out under the
#   button, in full, before it is pressed: what he will do, that he then takes
#   no orders and cannot be called back, how long, and what earns trust.
# - Every answer says what it does UNDER its own button (the blind reading:
#   "Dismiss Ney" and "Transfer Ney to Staff" stood with no words — what each
#   does was a hover). Where the window is too short for the captions of the
#   other answers they step aside and the hover carries the words, as before;
#   the task's own words always stand.
# - Administrative Role: Only if ≥2 field marshals AND no existing admin
# - Dismiss: Only if ≥2 field marshals
# =============================================================================

signal choice_made(choice: String)

# UI References
@onready var panel_container = $PanelContainer
@onready var marshal_name_label = $PanelContainer/VBoxContainer/MarshalNameLabel
@onready var message_label = $PanelContainer/VBoxContainer/MessageLabel
@onready var trust_label = $PanelContainer/VBoxContainer/StatsContainer/TrustLabel
@onready var trial_button = $PanelContainer/VBoxContainer/ButtonContainer/TrialButton
@onready var proposal_label = $PanelContainer/VBoxContainer/ButtonContainer/ProposalLabel
# the space that keeps his proposal with ITS button, apart from the next answer
@onready var proposal_gap = $PanelContainer/VBoxContainer/ButtonContainer/ProposalGap
@onready var dismiss_button = $PanelContainer/VBoxContainer/ButtonContainer/DismissButton
@onready var admin_button = $PanelContainer/VBoxContainer/ButtonContainer/AdminButton

var current_marshal: String = ""
# Row IC, Session 2b (the review): the task's own line as THIS window shows
# it - sent back with the answer, so "what was shown is what is given" is
# checked against the screen (the server refuses, free, when the board has
# changed under it, and the question comes back with his new proposal).
var _shown_line: String = ""
# FA-D5 (slice 17, Phase 2): the arm that pays him — built from the payload
# like the others, first in the column, hidden until the audience offers it.
var settle_button: Button = null

# Napoleonic color palette
const COLOR_TEXT = "eee"
const COLOR_WARNING = "cd6b6b"
const COLOR_PANEL = "1a1a2e"
# Row IC, Session 2b: the picture at the head of the sheet steps aside when
# the window is short (the proposal's words need the room — the type never
# shrinks). At Interface Scale 1.8 on a 5120 x 1377 screen the logical view
# is 765 tall.
const BANNER_NEEDS_HEIGHT := 900.0
# ... and the captions of the OTHER answers step aside (the hover carries
# their words) where the window has no room for them: three answers with their
# words stand about 670 px tall at the first player's setup (a logical view of
# 765), each further answer about 100 more. The window is then MEASURED once
# its lines have wrapped (`_settle_fit`): words that would push it past the
# screen's band step aside whatever this estimate said.
const CAPTIONS_NEED_HEIGHT := 740.0
const CAPTIONS_NEED_PER_ANSWER := 100.0
const WINDOW_RESERVE := 88.0          # `Utils.clamp_centered_panel`'s own band
const CAPTION_INK := Color(0.86, 0.84, 0.78)
# The review (the client's lane), pressed: at the compact views (Interface
# Scale 2.0 on 1600 x 900 - a logical 800 x 450) the window ran 77 px past the
# screen and "Transfer to Staff" fell off it. Where the window cannot hold
# his proposal whole, the marshal's quoted line steps aside and the proposal
# SCROLLS - never less than this much of it - so every answer stays on the
# screen. Nothing of this is touched where the window fits.
const PROPOSAL_LEAST_ROOM := 96.0
# ... and only where it would run off the SCREEN: the top bar and a little air
# (the 88 px band above is the roomy margin the other answers' words keep; a
# window a few px over that band still stands whole on the screen - Interface
# Scale 2.0 on a 1080p panel - and is left as it is).
const SCREEN_RESERVE := 56.0
var _proposal_scroll: ScrollContainer = null
# Each fit carries its own number: a later one (a new audience, a resize while
# the first still waits for its frames) makes every earlier one stand down, so
# two fits never undo each other.
var _fit_pass: int = 0
# the answer's button -> [its caption Label, the space under it, its words]
var _captions: Dictionary = {}

func _ready():
	# Connect button signals
	trial_button.pressed.connect(_on_trial_pressed)
	dismiss_button.pressed.connect(_on_dismiss_pressed)
	admin_button.pressed.connect(_on_admin_pressed)
	settle_button = Button.new()
	settle_button.name = "SettleButton"
	# Session UI-2: the arm wears the same step and height as its column.
	settle_button.theme_type_variation = trial_button.theme_type_variation
	settle_button.custom_minimum_size = trial_button.custom_minimum_size
	settle_button.visible = false
	settle_button.pressed.connect(_on_settle_pressed)
	# Session UI-5: each course has its own cue (the global click stays out).
	for b in [settle_button, trial_button, admin_button, dismiss_button]:
		b.set_meta("no_click_sfx", true)
	var _column = trial_button.get_parent()
	_column.add_child(settle_button)
	_column.move_child(settle_button, 0)
	for b in [settle_button, admin_button, dismiss_button]:
		_captions[b] = _caption_under(b)

	# Hide by default
	hide()

func show_redemption(redemption_data: Dictionary):
	"""Display redemption dialog with data from backend."""
	print("REDEMPTION DIALOG: show_redemption() called")
	print("  Data: ", redemption_data)

	current_marshal = redemption_data.get("marshal", "Marshal")
	_shown_line = ""
	_proposal_out_of_scroll()
	message_label.visible = true
	AudioManager.play("letter_open")

	# Set marshal name header
	marshal_name_label.text = "%s REQUESTS AUDIENCE" % current_marshal.to_upper()
	# Session UI-2: the trust glyph over the header — a marshal's loyalty is
	# what is asked.
	_arms_row([{"glyph": "trust"}])
	_set_banner()

	# Set message
	var message = redemption_data.get("message", "Our relationship has broken down, Sire. Something must change.")
	message_label.text = '"%s"' % message

	# Get trust value
	var trust = int(redemption_data.get("trust", 20))
	# (the blind reading: "Trust: 15 (Critical)" has no scale)
	trust_label.text = "Trust: %d of 100 — critical" % trust

	# ════════════════════════════════════════════════════════════════════════════
	# DYNAMIC BUTTON VISIBILITY - Show only available options
	# ════════════════════════════════════════════════════════════════════════════
	var options = redemption_data.get("options", [])
	var available_ids = []
	var proposal_words := ""
	for b in _captions:
		_captions[b][2] = ""      # (the last audience's words never linger)

	# Collect available option IDs and update button text
	for opt in options:
		var opt_id = opt.get("id", "")
		var opt_text = opt.get("text", "")
		var opt_desc = opt.get("description", "")
		available_ids.append(opt_id)

		match opt_id:
			"settle_account":
				settle_button.text = opt_text if opt_text else "Settle his account (a rente)"
				_captions[settle_button][2] = str(opt_desc)
			"trial":
				trial_button.text = opt_text if opt_text else "Give him a task to prove himself"
				# Row IC, Session 2b: his proposal stands ON the window, in
				# full — never only in a hover. It wraps; the type never shrinks.
				proposal_words = str(opt_desc)
				trial_button.tooltip_text = ""
				var asked = opt.get("proposal")
				_shown_line = str(asked.get("line", "")) if asked is Dictionary else ""
			"administrative_role":
				admin_button.text = opt_text if opt_text else "Transfer to Staff (+1 action)"
				_captions[admin_button][2] = str(opt_desc)
			"dismiss":
				dismiss_button.text = opt_text if opt_text else "Dismiss Marshal"
				_captions[dismiss_button][2] = str(opt_desc)

	# Show/hide buttons based on availability
	settle_button.visible = "settle_account" in available_ids
	trial_button.visible = "trial" in available_ids
	proposal_label.text = proposal_words
	proposal_label.visible = trial_button.visible and proposal_words != ""
	proposal_gap.visible = proposal_label.visible
	admin_button.visible = "administrative_role" in available_ids
	dismiss_button.visible = "dismiss" in available_ids
	_place_captions(_captions_have_room())

	print("REDEMPTION DIALOG: Available options: ", available_ids)
	print("REDEMPTION DIALOG: Trial visible: ", trial_button.visible)
	print("REDEMPTION DIALOG: Admin visible: ", admin_button.visible)
	print("REDEMPTION DIALOG: Dismiss visible: ", dismiss_button.visible)

	# Show the dialog
	print("REDEMPTION DIALOG: Showing dialog...")
	show()
	# July 18, 2026 viewport sweep: fit to the CURRENT logical viewport.
	# Interface Scale (content_scale_factor, up to 2.0) divides the logical
	# viewport, so a fixed authored rect can carry the action row off-screen
	# and leave a modal undismissable. The helper is a no-op wherever the
	# panel already fits, and returns early for non-centre-anchored panels.
	Utils.clamp_centered_panel($PanelContainer)
	# Session UI-2: then shrink to the content (the authored height stood over
	# a band of empty panel when fewer arms are offered) — row IC, Session 2b:
	# after the answers' words have been measured against the screen.
	_settle_fit()
	print("REDEMPTION DIALOG: visible = ", visible)

func shown_line() -> String:
	"""The proposal this window displays (the task's own line), "" when it
	shows none."""
	return _shown_line


func refit() -> void:
	"""UXR-2's live-refit hook (`Utils.refit_surface`): the clamp, then the
	shrink to content, exactly as on open."""
	_set_banner()
	_proposal_out_of_scroll()
	message_label.visible = true
	_place_captions(_captions_have_room())
	Utils.clamp_centered_panel($PanelContainer)
	_settle_fit()

func _caption_under(button: Button) -> Array:
	"""An answer's words under its button, and the space that keeps them with
	it and apart from the next answer -> [Label, space, ""]."""
	var column: Node = button.get_parent()
	var label := Label.new()
	label.name = str(button.name).replace("Button", "Caption")
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.add_theme_color_override("font_color", CAPTION_INK)
	label.visible = false
	column.add_child(label)
	column.move_child(label, button.get_index() + 1)
	var space := Control.new()
	space.name = str(button.name).replace("Button", "CaptionGap")
	space.custom_minimum_size = proposal_gap.custom_minimum_size
	space.mouse_filter = Control.MOUSE_FILTER_IGNORE
	space.visible = false
	column.add_child(space)
	column.move_child(space, label.get_index() + 1)
	return [label, space, ""]


func _captions_have_room() -> bool:
	"""The estimate, before anything is drawn: is the view tall enough for
	every offered answer's words? (`_settle_fit` then measures.)"""
	var answers := 0
	for b in [settle_button, trial_button, admin_button, dismiss_button]:
		if b != null and b.visible:
			answers += 1
	var need: float = CAPTIONS_NEED_HEIGHT + CAPTIONS_NEED_PER_ANSWER * float(maxi(0, answers - 3))
	return get_viewport().get_visible_rect().size.y >= need


func _settle_fit() -> void:
	"""Once the lines have wrapped (two frames): a window that the answers'
	words push past the screen's band lets the OTHER answers' words go to
	their hovers — the task's own always stand — and then it shrinks to its
	content, as every window does."""
	_fit_pass += 1
	var mine: int = _fit_pass
	await get_tree().process_frame
	await get_tree().process_frame
	if mine != _fit_pass or not is_inside_tree() or not visible:
		return
	var view: float = get_viewport().get_visible_rect().size.y
	var screen: float = view - SCREEN_RESERVE - 2.0 * Utils.top_bar_growth()
	var need: float = $PanelContainer.get_combined_minimum_size().y
	if need > view - WINDOW_RESERVE - 2.0 * Utils.top_bar_growth():
		_place_captions(false)
		Utils.clamp_centered_panel($PanelContainer)
		# ... and where even that would run it off the screen (the compact
		# views): his quoted line steps aside, then the proposal scrolls.
		await get_tree().process_frame
		if mine != _fit_pass or not is_inside_tree() or not visible:
			return
		need = $PanelContainer.get_combined_minimum_size().y
		if need > screen and proposal_label.visible:
			message_label.visible = false
			await get_tree().process_frame
			if mine != _fit_pass or not is_inside_tree() or not visible:
				return
			need = $PanelContainer.get_combined_minimum_size().y
			if need > screen:
				var whole: float = proposal_label.get_combined_minimum_size().y
				_proposal_in_scroll(maxf(PROPOSAL_LEAST_ROOM, whole - (need - screen)))
				await get_tree().process_frame
				if mine != _fit_pass or not is_inside_tree() or not visible:
					return
			Utils.clamp_centered_panel($PanelContainer)
	Utils.shrink_centered_panel_to_content($PanelContainer)


func _proposal_in_scroll(room: float) -> void:
	"""His proposal moved into a scroll `room` px tall - only where the
	window cannot hold it whole (`_settle_fit`)."""
	if _proposal_scroll == null:
		var scroll := ScrollContainer.new()
		scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_RESERVE
		scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
		scroll.name = "ProposalScroll"
		_proposal_scroll = scroll
	if proposal_label.get_parent() != _proposal_scroll:
		var column: Node = proposal_label.get_parent()
		var at: int = proposal_label.get_index()
		column.remove_child(proposal_label)
		column.add_child(_proposal_scroll)
		column.move_child(_proposal_scroll, at)
		_proposal_scroll.add_child(proposal_label)
		proposal_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_proposal_scroll.custom_minimum_size.y = room
	_proposal_scroll.visible = proposal_label.visible


func _proposal_out_of_scroll() -> void:
	"""Back to the whole proposal on the window (a new audience, a refit)."""
	if _proposal_scroll == null or proposal_label.get_parent() != _proposal_scroll:
		return
	var column: Node = _proposal_scroll.get_parent()
	var at: int = _proposal_scroll.get_index()
	_proposal_scroll.remove_child(proposal_label)
	column.remove_child(_proposal_scroll)
	column.add_child(proposal_label)
	column.move_child(proposal_label, at)


func _place_captions(roomy: bool) -> void:
	"""Each offered answer's words under its button where the window has the
	room (`roomy`); else in its hover (the words are never lost)."""
	for b in _captions:
		var row: Array = _captions[b]
		var said: String = str(row[2])
		var shown: bool = roomy and b.visible and said != ""
		row[0].text = said
		row[0].visible = shown
		row[1].visible = shown
		b.tooltip_text = "" if shown else said


func _on_settle_pressed():
	"""FA-D5: the player pays him — the executor prices and gates it."""
	AudioManager.play("coins_small")
	hide()
	choice_made.emit("settle_account")

func _on_trial_pressed():
	"""Row IC, Session 2b: the player gives him his task to prove himself."""
	AudioManager.play("quill_sign")
	hide()
	choice_made.emit("trial")

func _on_admin_pressed():
	"""Player transfers marshal to administrative role."""
	AudioManager.play("quill_flick")
	hide()
	choice_made.emit("administrative_role")

func _on_dismiss_pressed():
	"""Player dismisses the marshal."""
	AudioManager.play("back")
	hide()
	choice_made.emit("dismiss")


func _set_banner() -> void:
	"""Session UI-5: the redemption's picture at the head of the sheet; it steps
	aside on the compact view (make_banner returns null there) — and, row IC
	Session 2b, on any window too short to hold it beside the proposal's
	words (`BANNER_NEEDS_HEIGHT`)."""
	var vb: VBoxContainer = $PanelContainer/VBoxContainer
	var old: Node = vb.get_node_or_null("Illustration")
	if old != null:
		vb.remove_child(old)
		old.queue_free()
	if get_viewport().get_visible_rect().size.y < BANNER_NEEDS_HEIGHT:
		return
	var w: float = maxf(panel_container.size.x, panel_container.custom_minimum_size.x)
	if w <= 0.0:
		w = 440.0
	var banner: TextureRect = Illustrations.make_banner("redemption", w)
	if banner == null:
		return
	# up to four arms stand below: the picture is capped so none falls off
	banner.custom_minimum_size.y = minf(banner.custom_minimum_size.y, 110.0)
	vb.add_child(banner)
	vb.move_child(banner, 0)


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
	# Row IC, Session 2b: ... and so does any view too short for the picture
	# (`BANNER_NEEDS_HEIGHT`): the answers' own words need the room.
	if get_viewport().get_visible_rect().size.y < BANNER_NEEDS_HEIGHT:
		row.visible = false
