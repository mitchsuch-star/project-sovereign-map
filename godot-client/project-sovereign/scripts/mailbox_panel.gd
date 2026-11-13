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
# RE-C (RECURRING_EVENTS_SPEC.md §12b.1): the footer's second pointer into the
# home — the Correspondence page of the Dispatch (main opens it).
signal correspondence_requested

const ITEM_TYPE_DISPLAY = {
	"incoming_proposal": "Proposal",
	"moment_letter": "Moment",  # S14c: keyed by proposal type — a letter of the record
	"counter_offer": "Counter-Offer",
	"counter_offer_response": "Counter Response",
}

@onready var background_overlay: ColorRect = $BackgroundOverlay
@onready var title_label: Label = $PanelContainer/VBoxContainer/TitleLabel
@onready var subtitle_label: Label = $PanelContainer/VBoxContainer/SubtitleLabel
@onready var list_content: VBoxContainer = $PanelContainer/VBoxContainer/ScrollContainer/ListContent
@onready var empty_state_label: Label = $PanelContainer/VBoxContainer/ScrollContainer/ListContent/EmptyStateLabel
@onready var close_btn: Button = $PanelContainer/VBoxContainer/ButtonContainer/CloseButton

# R159 (POSITION 7): the subtitle names the mechanic — unanswered envoys ARE
# diplomacy in waiting, and they lapse.
# S14E-27 (S14f part 2): the subtitle names which rows answer in place — the
# letter-book's (routine mail from the lesser courts); every other row opens its
# letter in full, and says why on its own line.
const DEFAULT_SUBTITLE = "Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Routine letters from the lesser courts answer in place; every other letter opens in full. Select a row, or press its Open, to reopen or activate it."

const SEAL_PX := 22.0   # Session UI-2: the row's seal glyph
const FLAG_PX := 18.0   # and the court's flag (height)

var _items: Array = []
# IGR-F: mailbox_id -> the letter-book row for that item. Only rows in this
# map get inline Accept/Decline; everything else keeps the click-to-open
# behaviour it has always had, so great-power and settlement traffic is
# untouched on this surface too.
var _digest_rows: Dictionary = {}
# Session UI-3 (November 12, 2026): the book's lead-ins stand behind an ⓘ
# ("Fold, a switch restores"). The header's own ⓘ sits beside the title; the
# last payload is kept so the Settings switch re-renders locally.
const LEAD_ID := "mailbox.lead"
const SMALL_LEAD_ID := "mailbox.small.lead"
const INFO_PX := 18.0
var _last_data: Dictionary = {}
var _rerender := false
var _lead_icon: TextureRect = null


func _ready():
	hide()
	close_btn.pressed.connect(_on_close)
	close_btn.set_meta("no_click_sfx", true)  # its own cue is the book closing
	background_overlay.gui_input.connect(_on_overlay_input)
	_build_header_lead()
	Utils.on_explanations_changed(_on_explanations_changed)


func _build_header_lead() -> void:
	"""Session UI-3: the title in a row with its ⓘ (folded: the header
	paragraph's words are the icon's hover, a click opens them in place)."""
	var vbox := title_label.get_parent() as VBoxContainer
	var header := HBoxContainer.new()
	header.alignment = BoxContainer.ALIGNMENT_CENTER
	header.add_theme_constant_override("separation", 8)
	vbox.add_child(header)
	vbox.move_child(header, title_label.get_index())
	title_label.reparent(header, false)
	_lead_icon = _info_icon(DEFAULT_SUBTITLE, LEAD_ID)
	header.add_child(_lead_icon)
	_apply_main_lead()


func _info_icon(tip: String, id: String) -> TextureRect:
	"""The ⓘ for a Label lead-in: a real TextureRect whose hover is the line;
	a click toggles the note (`Utils.toggle_note`) and shows/hides its label."""
	var icon := TextureRect.new()
	icon.texture = load(Utils.INFO_GLYPH)
	icon.modulate = Utils.UI_GOLD
	icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	icon.custom_minimum_size = Vector2(INFO_PX, INFO_PX)
	icon.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	icon.mouse_filter = Control.MOUSE_FILTER_STOP
	icon.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	icon.tooltip_text = tip
	icon.set_meta("note_id", id)
	icon.gui_input.connect(_on_info_input.bind(icon))
	return icon


func _on_info_input(event: InputEvent, icon: TextureRect) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		var id: String = str(icon.get_meta("note_id"))
		Utils.toggle_note(id)
		if id == LEAD_ID:
			_apply_main_lead()
		else:
			var line = icon.get_meta("note_label", null)
			if line != null and is_instance_valid(line):
				(line as Control).visible = Utils.show_note(id)


func _apply_main_lead() -> void:
	"""The header paragraph: On the page as ever; Folded only once opened."""
	subtitle_label.visible = Utils.show_note(LEAD_ID)
	if _lead_icon != null:
		_lead_icon.visible = Utils.explanations_folded()


func _on_explanations_changed() -> void:
	_apply_main_lead()
	if visible and not _last_data.is_empty():
		_rerender = true
		show_mailbox(_last_data)
		_rerender = false


func show_mailbox(data: Dictionary):
	if not _rerender:
		AudioManager.play("letter_open")
	_last_data = data
	var items = data.get("items", [])
	var count = int(data.get("count", 0))
	_items = items.duplicate()

	_digest_rows = {}
	var digest = data.get("envoy_digest")
	if typeof(digest) == TYPE_DICTIONARY:
		for row in digest.get("items", []):
			if typeof(row) == TYPE_DICTIONARY:
				_digest_rows[int(row.get("mailbox_id", 0))] = row

	# IGR-F review [4]: the panel-wide header stays panel-wide. The digest's
	# "answer them here, they lapse when the turn ends" promise is FALSE over a
	# settlement offer or an ally petition — both are PERSISTENT mailbox types
	# that never lapse — and the digest count is smaller than the number of
	# rows on screen whenever one is waiting. The letter-book's own copy is a
	# caption over its own rows instead.
	title_label.text = "PENDING ENVOYS (%d)" % count
	subtitle_label.text = DEFAULT_SUBTITLE
	_clear_rows()

	if items.is_empty():
		empty_state_label.visible = true
		show()
		# IQ-10 "The Client Pass" (Sept 19, 2026): the EMPTY book is fitted
		# too. This early return used to skip the clamp below, so at
		# Interface Scale 2.0 (logical viewport 800x450) the authored 960x720
		# rect stood and carried the Close button to y=746 — off-screen, the
		# modal undismissable by mouse, the visible area a flat colour. One
		# row present and the clamp already fitted the same panel to 776x362.
		Utils.set_reading_share($PanelContainer, Vector2(0.62, 0.94), Vector2(1100, 1000))
		Utils.clamp_centered_panel($PanelContainer)
		return

	empty_state_label.visible = false
	var caption_placed := false
	for item in items:
		if not caption_placed and _digest_rows.has(int(item.get("mailbox_id", 0))):
			list_content.add_child(_build_digest_caption(digest))
			caption_placed = true
		list_content.add_child(_build_item_row(item))

	show()
	# July 18, 2026 viewport sweep: fit to the CURRENT logical viewport.
	# Interface Scale (content_scale_factor, up to 2.0) divides the logical
	# viewport, so a fixed authored rect can carry the action row off-screen
	# and leave a modal undismissable. The helper is a no-op wherever the
	# panel already fits, and returns early for non-centre-anchored panels.
	# Session UI-3: the book's reading ceiling (62 x 85 % of the view, capped
	# 1100 x 1000) - the rows' buttons stand whole instead of at the scroll's foot.
	Utils.set_reading_share($PanelContainer, Vector2(0.62, 0.94), Vector2(1100, 1000))
	Utils.clamp_centered_panel($PanelContainer)
	_fit_to_rows()


func _fit_to_rows() -> void:
	"""Session UI-2 (November 11, 2026): the book fits what it holds. The
	authored 960 x 720 stood over two short rows and a band of nothing.
	Session UI-3 (November 12, 2026): and the second envoy row's Accept /
	Decline stood cut at the scroll's foot - the list was measured once, two
	frames after the clamp, before its wrapping labels had settled to the
	scroll's width, and given 4 px of slack. It is measured now at the list's
	own settled height (the larger of its minimum and its last row's foot,
	rows' margins and separation included), twice - the second pass after the
	first has laid the labels out - +8 px, capped at the room the reading
	ceiling leaves, so a long book still scrolls and a short one shrinks."""
	for _pass in 2:
		await get_tree().process_frame
		await get_tree().process_frame
		if not visible:
			return
		var panel := $PanelContainer as Control
		if panel.has_meta("side_desk_docked") or panel.has_meta("clamp_user_size"):
			return
		var scroll := list_content.get_parent() as ScrollContainer
		var have: float = panel.offset_bottom - panel.offset_top
		scroll.custom_minimum_size.y = 0.0
		var others: float = panel.get_combined_minimum_size().y
		var foot: float = 0.0
		for child in list_content.get_children():
			if child is Control and (child as Control).visible:
				foot = maxf(foot, (child as Control).position.y + (child as Control).size.y)
		var list_h: float = maxf(list_content.get_combined_minimum_size().y, foot) + 8.0
		scroll.custom_minimum_size.y = clampf(list_h, 80.0, maxf(have - others, 80.0))
	Utils.shrink_centered_panel_to_content($PanelContainer)


func _build_digest_caption(digest: Dictionary) -> VBoxContainer:
	"""The letter-book's own heading, scoped to the rows it actually governs.

	The title comes from the backend so the noun follows the roster: the
	predicate deliberately includes the SECONDARY courts, and calling the
	Porte a small court is a different claim from batching its routine mail."""
	var box = VBoxContainer.new()
	box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	box.add_theme_constant_override("separation", 2)

	var heading = Label.new()
	var title = str(digest.get("title", "THE COURTS WRITE"))
	heading.text = "%s (%d)" % [title, int(digest.get("count", _digest_rows.size()))]
	heading.mouse_filter = Control.MOUSE_FILTER_IGNORE
	heading.theme_type_variation = &"HudTitle"
	heading.add_theme_color_override("font_color", Utils.UI_GOLD)
	# Session UI-3: the section's lead-in ("Hesse and Papal States write. Answer
	# them here. ...") stands behind an ⓘ at this heading, folded.
	var heading_row := HBoxContainer.new()
	heading_row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	heading_row.add_theme_constant_override("separation", 8)
	heading_row.add_child(heading)
	box.add_child(heading_row)

	var note = Label.new()
	var headline = Utils.humanize_nation_keys_in_text(str(digest.get("headline", "")))
	note.text = (headline + " " + str(digest.get("deadline_note", ""))).strip_edges()
	note.mouse_filter = Control.MOUSE_FILTER_IGNORE
	note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	note.theme_type_variation = &"Caption"
	note.add_theme_color_override("font_color", Utils.UI_MAILBOX_NOTE)
	box.add_child(note)
	if note.text != "":
		var lead_icon := _info_icon(note.text, SMALL_LEAD_ID)
		lead_icon.set_meta("note_label", note)
		lead_icon.visible = Utils.explanations_folded()
		heading_row.add_child(lead_icon)
		note.visible = Utils.show_note(SMALL_LEAD_ID)

	return box


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
	# UXR3-63 (Pre-Deploy S12): the row opens its letter, so it shows the hand
	# and says "Open ▸" — it was a card with no visible press.
	panel.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	panel.tooltip_text = "Open this letter"

	var style = StyleBoxFlat.new()
	style.bg_color = Color(0.1, 0.12, 0.18, 0.96) if is_active else Color(0.07, 0.08, 0.12, 0.94)
	style.border_width_left = 1
	style.border_width_top = 1
	style.border_width_right = 1
	style.border_width_bottom = 1
	style.border_color = Color(0.5, 0.72, 0.86, 0.9) if is_active else Utils.UI_MAILBOX_IDLE_BORDER
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

	# Session UI-2 (November 11, 2026): the row leads with its seal (a letter
	# for a letter of the record, an envoy for the courts' traffic) and the
	# court's flag, then the state as a tinted badge and the sender in the
	# title face - the sender and the subject in two weights.
	var is_letter = str(item.get("proposal_type", "")) == "moment_letter" or str(item.get("register", "")) == "affair"
	var seal = TextureRect.new()
	seal.texture = load(Utils.glyph("letter" if is_letter else "envoy"))
	seal.modulate = Utils.UI_GOLD
	seal.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	seal.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	seal.custom_minimum_size = Vector2(SEAL_PX, SEAL_PX)
	seal.mouse_filter = Control.MOUSE_FILTER_IGNORE
	top_row.add_child(seal)

	var flag_path: String = Utils.nation_flag_path(source)
	if flag_path != "" and ResourceLoader.exists(flag_path):
		var flag = TextureRect.new()
		flag.texture = load(flag_path)
		flag.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		flag.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		flag.custom_minimum_size = Vector2(FLAG_PX * 1.5, FLAG_PX)
		flag.mouse_filter = Control.MOUSE_FILTER_IGNORE
		top_row.add_child(flag)
	else:
		# Session UI-4 (November 12, 2026): a court with no flag still holds its
		# place, so the status badges stand in ONE column down the rows.
		var no_flag = Control.new()
		no_flag.custom_minimum_size = Vector2(FLAG_PX * 1.5, FLAG_PX)
		no_flag.mouse_filter = Control.MOUSE_FILTER_IGNORE
		top_row.add_child(no_flag)

	var state_badge = Label.new()
	state_badge.text = "ACTIVE" if is_active else "WAITING"
	state_badge.mouse_filter = Control.MOUSE_FILTER_IGNORE
	state_badge.theme_type_variation = &"Caption"
	# Session UI-4: one width, the word centred - "ACTIVE" and "WAITING" align
	# (the readers: "align the status tags").
	state_badge.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	state_badge.custom_minimum_size = Vector2(Utils.text_px(96), 0)
	state_badge.add_theme_color_override("font_color", Color.html("f4ead2"))
	state_badge.add_theme_stylebox_override("normal", _badge_box(
			Color.html("3a4a6b") if is_active else Color.html(Utils.COLOR_BADGE_QUIET)))
	top_row.add_child(state_badge)

	var source_label = Label.new()
	source_label.text = Utils.display_nation_name(source)
	source_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	source_label.theme_type_variation = &"Lead"
	source_label.add_theme_font_override("font", load(Utils.TITLE_FONT))
	source_label.add_theme_color_override("font_color", Utils.UI_GOLD)
	top_row.add_child(source_label)

	var spacer = Control.new()
	spacer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	top_row.add_child(spacer)

	var type_label = Label.new()
	var _type_key = "moment_letter" if str(item.get("proposal_type", "")) == "moment_letter" else item_type
	type_label.text = ITEM_TYPE_DISPLAY.get(_type_key, item_type.replace("_", " ").capitalize())
	# RE-2 (RECURRING_EVENTS_SPEC.md §12): an affair of state rides the moment
	# letter's transport and carries its own register on the row — the tag
	# says which (a moment's row carries no register key and reads as before).
	if str(item.get("register", "")) == "affair":
		type_label.text = "Affair"
	type_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	type_label.theme_type_variation = &"Caption"
	type_label.add_theme_color_override("font_color", Utils.UI_TEXT_DIM)
	top_row.add_child(type_label)

	# S14G-X24 (Pre-Deploy S14h part 1, October 26, 2026): the lock on the row.
	# The letter's popup, its Not Now button, the Cabinet button and the Envoys
	# badge all said whether a letter shuts the Cabinet (S14G-6); the mailbox,
	# where the player picks which letter to open, did not. `locks_cabinet` is
	# the backend's one predicate (`DialogueManager.item_locks_cabinet`); the
	# tooltip is the one sentence every surface says (`Utils.cabinet_shut_sentence`).
	# MOUSE_FILTER_PASS: the tooltip shows and a click still opens the row.
	if bool(item.get("locks_cabinet", false)):
		var lock_label = Label.new()
		lock_label.text = "Shuts the Cabinet"
		lock_label.mouse_filter = Control.MOUSE_FILTER_PASS
		lock_label.tooltip_text = Utils.cabinet_shut_sentence()
		lock_label.theme_type_variation = &"Caption"
		lock_label.add_theme_color_override("font_color", Utils.UI_WARNING)
		top_row.add_child(lock_label)

	# S14E-27 (S14f part 2): the word is the press. UXR3-63 gave the row the
	# hand and the word "Open ▸" — a Label that ignored the mouse, so the
	# control was the whole row and the word was only a sign. It is a flat
	# Button now, on the same `item_selected` path (`_open_row`); the whole
	# row stays clickable.
	var open_btn = Button.new()
	open_btn.text = "Open ▸"
	open_btn.flat = true
	open_btn.theme_type_variation = &"CaptionButton"
	open_btn.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	open_btn.tooltip_text = "Open this letter"
	open_btn.add_theme_color_override("font_color", Utils.UI_GOLD)
	open_btn.add_theme_color_override("font_hover_color", Utils.UI_GOLD)
	open_btn.pressed.connect(_open_row.bind(panel))
	top_row.add_child(open_btn)

	var turn_label = Label.new()
	turn_label.text = "Turn %d" % arrival_turn
	turn_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	turn_label.theme_type_variation = &"Caption"
	turn_label.add_theme_color_override("font_color", Utils.UI_TURN_STAMP)
	top_row.add_child(turn_label)

	var summary_label = Label.new()
	var summary_display = Utils.humanize_nation_keys_in_text(summary)
	summary_label.text = summary_display
	summary_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	summary_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	summary_label.theme_type_variation = &"BodyLarge"
	summary_label.add_theme_color_override("font_color", Color.html(Utils.COLOR_TEXT))
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
			voice_label.add_theme_color_override("font_color", Utils.UI_GOLD_BRIGHT)
			vbox.add_child(voice_label)
		var clauses = digest_row.get("clauses", [])
		if clauses is Array and clauses.size() > 0:
			vbox.add_child(_terms_line_label(clauses))
		vbox.add_child(_build_action_row(mailbox_id))
	else:
		# S14E-27: a row that opens its letter in full still shows what the
		# letter asks (the popup's own `clauses`, as the backend rides them on
		# the row) and says, on one line, why it is not answered in place.
		var row_terms = item.get("terms_lines", [])
		if row_terms is Array and row_terms.size() > 0:
			vbox.add_child(_terms_line_label(row_terms))
		var row_reason = str(item.get("reason", "")).strip_edges()
		if row_reason != "":
			var reason_label = Label.new()
			reason_label.text = row_reason
			reason_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
			reason_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			reason_label.theme_type_variation = &"Caption"
			reason_label.add_theme_color_override("font_color", Utils.UI_MAILBOX_NOTE)
			vbox.add_child(reason_label)

	return panel


func _badge_box(tone: Color) -> StyleBoxFlat:
	"""The state badge's tinted cell (Session UI-2)."""
	var box = StyleBoxFlat.new()
	box.bg_color = tone
	box.set_corner_radius_all(3)
	box.content_margin_left = 8.0
	box.content_margin_right = 8.0
	box.content_margin_top = 2.0
	box.content_margin_bottom = 2.0
	return box


func _terms_line_label(clauses: Array) -> Control:
	"""A letter's clause strings as a "Terms" caption over small tag chips, one
	per clause - the letter-book's rows and (S14E-27) every other
	incoming-proposal row draw it the same way. Session UI-4 (November 12,
	2026): the readers found the terms "a dense run-on in a plain box"
	("summarise the terms as bullet chips"); the words are unchanged, each
	clause its own chip, a short one beside its neighbours, a long one on a
	line of its own (it wraps inside its chip). The whole line stays the
	block's hover, the clauses joined as they were: "Terms: a · b · c"."""
	var block = VBoxContainer.new()
	block.mouse_filter = Control.MOUSE_FILTER_PASS
	block.add_theme_constant_override("separation", 4)
	var clause_strings: Array[String] = []
	for clause in clauses:
		clause_strings.append(Utils.humanize_nation_keys_in_text(str(clause)))
	block.tooltip_text = "Terms: " + " · ".join(clause_strings)
	var caption = Label.new()
	caption.text = "Terms"
	caption.mouse_filter = Control.MOUSE_FILTER_IGNORE
	caption.theme_type_variation = &"Caption"
	caption.add_theme_color_override("font_color", Utils.UI_TEXT_DIM)
	block.add_child(caption)
	var flow: HFlowContainer = null
	for text in clause_strings:
		var chip := _terms_chip(text, text.length() > TERMS_CHIP_SHORT)
		if text.length() > TERMS_CHIP_SHORT:
			# a long clause takes the block's width and wraps inside its chip
			flow = null
			chip.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			block.add_child(chip)
			continue
		if flow == null:
			flow = HFlowContainer.new()
			flow.mouse_filter = Control.MOUSE_FILTER_IGNORE
			flow.add_theme_constant_override("h_separation", 6)
			flow.add_theme_constant_override("v_separation", 6)
			flow.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			block.add_child(flow)
		flow.add_child(chip)
	return block


# a clause this long or shorter rides in the flow beside its neighbours
const TERMS_CHIP_SHORT := 36


func _terms_chip(text: String, wrap: bool) -> PanelContainer:
	"""One clause as a tag: a hairline of gilt on the darker field, the clause
	in the bright gilt ink."""
	var chip = PanelContainer.new()
	chip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	# Session UI-5 interim fix (Nov 13): a term pill is not clickable, so it is a
	# flat tinted badge with no border (a border made it read as a button).
	var box = StyleBoxFlat.new()
	box.bg_color = Utils.UI_INK_NAVY
	box.set_border_width_all(0)
	box.set_corner_radius_all(10)
	box.content_margin_left = 10.0
	box.content_margin_right = 10.0
	box.content_margin_top = 3.0
	box.content_margin_bottom = 3.0
	chip.add_theme_stylebox_override("panel", box)
	var label = Label.new()
	label.text = text
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART if wrap else TextServer.AUTOWRAP_OFF
	label.add_theme_color_override("font_color", Utils.UI_GOLD_BRIGHT)
	chip.add_child(label)
	return chip


func _open_row(panel: PanelContainer):
	"""Open this row's letter — the ONE path the row's own click and its "Open ▸"
	button share (S14E-27). Hides the panel and hands the row to `item_selected`
	(main.gd activates it)."""
	hide()
	item_selected.emit(
		int(panel.get_meta("mailbox_id")),
		bool(panel.get_meta("is_active")),
		str(panel.get_meta("item_type"))
	)


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
	accept_btn.theme_type_variation = &"PrimaryButton"   # Session UI-2: the one gilt answer
	accept_btn.custom_minimum_size = Vector2(112, 34)
	accept_btn.pressed.connect(_on_row_action.bind(mailbox_id, "accept"))
	row.add_child(accept_btn)

	var decline_btn = Button.new()
	decline_btn.text = "Decline"
	decline_btn.custom_minimum_size = Vector2(112, 34)
	decline_btn.pressed.connect(_on_row_action.bind(mailbox_id, "reject"))
	row.add_child(decline_btn)

	var hint = Label.new()
	hint.text = "or click the letter to reply in full"
	hint.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hint.theme_type_variation = &"Caption"
	hint.add_theme_color_override("font_color", Utils.UI_TURN_STAMP)
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
		_open_row(panel)


func _clear_rows():
	for child in list_content.get_children():
		if child != empty_state_label:
			list_content.remove_child(child)
			child.queue_free()


func _on_overlay_input(event):
	if event is InputEventMouseButton and event.pressed:
		_on_close()


func _unhandled_input(event: InputEvent) -> void:
	# FA-94 (slice 17): ESC dismisses the letter-book. Through `_on_close`
	# (the EXISTING handler, which emits `panel_closed` — main.gd's tail
	# re-enables the command line on it), never a bare hide().
	if not visible:
		return
	if event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		_on_close()


func _on_close():
	# Session UI-5: closing the letter-book is a book closing (the Close button,
	# Esc and a click on the overlay all arrive here, once; a re-render never does)
	if visible:
		AudioManager.play("book_close")
	hide()
	panel_closed.emit()


func _ensure_correspondence_button() -> void:
	"""RE-C: "The Correspondence ▸" beside Close, built once (the scene file
	stays as authored); it hides the panel and asks main for the page."""
	if close_btn == null or close_btn.get_parent() == null:
		return
	var row := close_btn.get_parent()
	if row.has_node("CorrespondenceButton"):
		return
	var btn := Button.new()
	btn.name = "CorrespondenceButton"
	btn.text = "The Correspondence ▸"
	btn.theme_type_variation = &"CaptionButton"
	btn.custom_minimum_size = Vector2(200, 40)
	btn.tooltip_text = "Every letter of state laid before you, the answer you gave, what it did and what came of it."
	btn.pressed.connect(_on_correspondence_pressed)
	row.add_child(btn)
	row.move_child(btn, 0)


func _on_correspondence_pressed() -> void:
	hide()
	correspondence_requested.emit()
