extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Marshal Petition Dialog (Jealousy v3.2, spec §0.2-10)
# =============================================================================
# ONE popup channel for every marshal-drama petition the backend queues:
#   jealousy_confrontation  (§6  — Acknowledge / Promise Glory / Rebuke)
#   rivalry_confrontation   (§6b — Let be / Mediate / Reprimand ... Separate)
#   fontainebleau           (ESP-1 — the collective petition)
#   war_weary               (ESP-2 — "I have my duchy, Sire...")
# Options arrive DATA-DRIVEN from world.pending_marshal_petition — id, label,
# detail, cost_note, enabled (EC-I: unaffordable choices arrive greyed).
# The answer POSTs to /marshal_petition_response via main.gd.
# "Later" merely hides — the pending petition re-surfaces next turn.
# CanvasLayer 114.
# =============================================================================

signal petition_choice(choice_id: String)
# CA9 row 3 / A1 (Aug 9 2026): "Later" used to be a bare `hide()`. The card is
# shown from `_post_hud_response_routes`, and EVERY entry there returns before
# `set_input_enabled(true)` — so deferring the petition left the command line,
# Send, End Turn and the diplomacy wizard permanently disabled with no
# recovery path short of reloading. The polite button bricked the turn.
# Same contract as the Proclamation's `dismissed` (proclamation_popup.gd):
# the shower does not hand control back, the dismiss handler does.
signal petition_deferred

@onready var title_label = $PanelContainer/VBoxContainer/TitleLabel
# LV-5 (row EP F3): a closed arm's reason, ONE line under the header — above
# the fold, where the player reads it before the options scroll.
@onready var gate_label = $PanelContainer/VBoxContainer/GateLabel
@onready var body_label = $PanelContainer/VBoxContainer/BodyLabel
# SFR-B11 (SF-RR5): the answers are a row that wraps under the letter, Later
# last in it — never a scroll (see the scene).
@onready var options_container = $PanelContainer/VBoxContainer/OptionsContainer
@onready var later_button = $PanelContainer/VBoxContainer/OptionsContainer/LaterButton

const KIND_TITLES = {
	"jealousy_confrontation": "A MARSHAL SEEKS AN AUDIENCE",
	"rivalry_confrontation": "A RIVALRY AMONG THE MARSHALS",
	"fontainebleau": "THE MARSHALS PETITION THE EMPEROR",
	"war_weary": "A MARSHAL COUNSELS PEACE",
	"shadow_command": "A MARSHAL ASKS FOR A COMMAND",  # NP-3 §6.3
}
# Session UI-2: the glyph each petition stands under (one icon per category).
const KIND_GLYPHS = {
	"jealousy_confrontation": "glory",
	"rivalry_confrontation": "war",
	"fontainebleau": "cabinet",
	"war_weary": "drum",
	"shadow_command": "command",
}


# UI-5: the arrival sound the card opens on stops when an answer is given
var _open_cue = null  # untyped: a one-shot frees itself when it ends

# UI-5: answers that decline, rebuff or hold the line (the paper is crumpled);
# every other arm grants something (the quill signs).
const REFUSING_ARMS = ["rebuke", "reprimand", "refuse", "stays", "march_anyway",
	"let_be", "accept_breach", "separate"]

func _answer(cue: String) -> void:
	AudioManager.stop_player(_open_cue)
	_open_cue = null
	AudioManager.play(cue)


func _ready():
	if later_button:
		later_button.pressed.connect(_on_later)
		later_button.set_meta("no_click_sfx", true)
	# LV-5: the body is the petition — clamp_centered_panel's relax pass
	# shrinks the man's words last (since SFR-B11 the answers are a row of
	# buttons the pass never shrinks; the letter is the one region that yields).
	if body_label:
		body_label.set_meta("relax_last", true)
		# SFR-B11: the letter is now the card's one scroll — it rests on
		# whole lines like every reading scroll (UXR3-F3).
		Utils.keep_whole_lines(body_label)
	hide()


func show_petition(petition: Dictionary):
	"""Render one backend petition: title, body, dynamic option buttons."""
	AudioManager.stop_player(_open_cue)
	_open_cue = AudioManager.play("sword_draw")
	var kind = str(petition.get("kind", ""))
	title_label.text = str(petition.get("title", KIND_TITLES.get(kind, "A PETITION")))
	if title_label.text == "":
		title_label.text = KIND_TITLES.get(kind, "A PETITION")

	# A14 (CA9 row 3): the modal renders the MARSHAL. The backend has set
	# `speaker` on every petition since v3.2 and no .gd file ever read it,
	# so the flagship drama card arrived as an unsigned staff memo — which
	# is why `war_weary`, the one petition carrying a spoken clause, was
	# the only one that read as drama. His own words go FIRST, in gold,
	# above the staff's summary; the header names him.
	# Session UI-2: the office the petition comes from, above the header.
	_arms_row([{"glyph": str(KIND_GLYPHS.get(kind, "letter"))}])
	var speaker = str(petition.get("speaker", ""))
	if speaker != "" and speaker != "<null>":
		title_label.text = Utils.humanize_nation_keys_in_text(speaker).to_upper() \
			+ " — " + title_label.text
	var body = ""
	var spoken = str(petition.get("speaker_line", ""))
	if spoken != "" and spoken != "<null>":
		body += "[color=#" + Utils.COLOR_GOLD + "]" \
			+ Utils.humanize_nation_keys_in_text(spoken) + "[/color]\n\n"
	body += "[color=#d0c0b0]" + str(petition.get("body", "")) + "[/color]"
	# The scene authors BodyLabel at a bounded 120px with scroll_active so
	# `Utils.clamp_centered_panel` can shrink it (an unbounded fit_content
	# RichTextLabel cannot be clamped). The spoken line adds two lines, so
	# raise the floor rather than let the man's own words scroll out of
	# sight — still bounded, so the clamp still works.
	if body_label:
		body_label.custom_minimum_size.y = 170.0

	for child in options_container.get_children():
		if child != later_button:
			child.queue_free()

	var options = petition.get("options", [])
	var closed_lines: Array = []
	var prices: Array = []
	if options is Array:
		for option in options:
			if not (option is Dictionary):
				continue
			var price := _add_option(option)
			if price != "":
				prices.append(price)
			# LV-5: a closed arm names its reason ABOVE the fold. The backend
			# always sends one (`unavailable_reason`) for a refused arm; an
			# arm shut only by the action-point purse names the price.
			if not bool(option.get("enabled", true)):
				var why = str(option.get("unavailable_reason", ""))
				if why == "" or why == "<null>":
					var cost_note = str(option.get("cost_note", ""))
					if cost_note != "" and cost_note != "<null>":
						why = "it needs " + cost_note + " this turn"
				if why != "" and why != "<null>":
					closed_lines.append(str(option.get("label", "That arm"))
						+ " is closed — " + Utils.humanize_nation_keys_in_text(why))
	if gate_label:
		gate_label.text = "\n".join(PackedStringArray(closed_lines))
		gate_label.visible = not closed_lines.is_empty()
	# SFR-B11: what each answer costs is read in the letter, under his words
	# (and on each button's tooltip) — the client's petition and the envoy's
	# letter read the same way; the answers stand as buttons below.
	if not prices.is_empty():
		body += "\n\n[color=#" + Utils.COLOR_HEADER + "]What each answer does[/color]\n" \
			+ "\n".join(PackedStringArray(prices))
	body_label.text = body
	options_container.move_child(later_button, -1)
	_banner("petition")

	# Fontainebleau and war-weary petitions demand an answer NOW — the
	# moment does not keep. Grievance/rivalry petitions (and NP-3's
	# request for a command) may wait a turn.
	if later_button:
		later_button.visible = kind in ["jealousy_confrontation", "rivalry_confrontation", "shadow_command"]

	show()
	# July 18, 2026 viewport sweep: fit to the CURRENT logical viewport.
	# Interface Scale (content_scale_factor, up to 2.0) divides the logical
	# viewport, so a fixed authored rect can carry the action row off-screen
	# and leave a modal undismissable. The helper is a no-op wherever the
	# panel already fits, and returns early for non-centre-anchored panels.
	Utils.clamp_centered_panel($PanelContainer)
	# LV-5: then size the body to its own text and fit again — after layout
	# has given the label its width (deferred, one frame).
	call_deferred("_fit_body")


func _fit_body() -> void:
	"""LV-5 (row EP F3): the body sizes to `get_content_height()` (bounded)
	so the petition's second line no longer falls below the fold with only
	a thin scrollbar as the cue, and the clamp still fits the whole panel to
	the viewport: the letter is what yields (relax_last), the row of answers
	never does (SFR-B11 — buttons are click targets)."""
	await get_tree().process_frame
	if body_label == null or not visible:
		return
	var wanted: float = body_label.get_content_height() + 12.0
	body_label.custom_minimum_size.y = clampf(wanted, 120.0, 360.0)
	# Session UI-2: the ceiling grows with the window — the arms row took the
	# authored 540's last line of the letter, and every enabled answer's price
	# must stay in view (SFR-B11); the band still bounds it.
	var view := get_viewport().get_visible_rect().size
	$PanelContainer.set_meta("clamp_ceiling_override", Vector2(680.0, maxf(view.y * 0.86, 540.0)))
	Utils.clamp_centered_panel($PanelContainer)
	# Session UI-2: and the card shrinks to what it holds (the authored 540
	# stood over a band of empty panel under a short petition) — not in the
	# compact view, where the clamp has already relaxed the letter to the
	# room and a shrink would trim the answers' prices out of sight.
	# A long petition keeps the authored room (its letter expands into it and
	# every answer's price stays in view, SFR-B11); only a short one shrinks.
	if wanted <= 360.0 and not Utils.compact_view():
		Utils.shrink_centered_panel_to_content($PanelContainer)


func refit() -> void:
	"""UXR-2: the live-refit road's hook — the body re-sizes to its content
	and the clamp re-fits the panel (`_fit_body` does both)."""
	_fit_body()


func _add_option(option: Dictionary) -> String:
	"""The answer's button in the row; returns its line for the letter (what
	it does), or "" when there is nothing to say twice."""
	var btn = Button.new()
	var label = str(option.get("label", "?"))
	var cost_note = str(option.get("cost_note", ""))
	if cost_note != "":
		label += "   [" + cost_note + "]"
	btn.text = label
	btn.custom_minimum_size = Vector2(0, 40)
	# Session UI-2: an open arm wears the theme's gilt face (the gold override
	# that stood here beat its words); a closed arm is dimmed below.
	var is_enabled = bool(option.get("enabled", true))
	btn.disabled = not is_enabled
	btn.tooltip_text = str(option.get("detail", ""))
	if not is_enabled:
		# July 25, 2026 in-game review: a greyed arm used to say nothing about
		# WHY, and at a glance read as merely un-hovered. Dim the label and let
		# the detail line carry the backend's reason.
		btn.add_theme_color_override("font_color", Utils.UI_CLOSED_ARM)
		btn.add_theme_color_override("font_disabled_color", Utils.UI_CLOSED_ARM)
	btn.pressed.connect(_on_option_pressed.bind(str(option.get("id", ""))))
	btn.set_meta("no_click_sfx", true)  # UI-5: the answer plays its own cue
	options_container.add_child(btn)

	var detail = str(option.get("detail", ""))
	var reason = str(option.get("unavailable_reason", ""))
	# LV-5 (row EP F3): the reason renders above the fold (GateLabel, see
	# show_petition); the letter carries only the detail — and never the reason
	# twice (the backend sends `detail == reason` for a non-AP refusal).
	if not is_enabled and reason != "" and detail == reason:
		detail = ""
	if detail == "":
		return ""
	var named := str(option.get("label", "?"))
	if cost_note != "":
		named += " (" + cost_note + ")"
	var hue := Utils.COLOR_GOLD if is_enabled else Utils.UI_CLOSED_ARM.to_html(false)
	return "• [color=#" + hue + "]" + named + "[/color] — " + detail


func _on_option_pressed(choice_id: String):
	_answer("paper_crumple" if choice_id in REFUSING_ARMS else "quill_sign")
	hide()
	petition_choice.emit(choice_id)


func _on_later():
	_answer("back")
	hide()
	# The pending petition genuinely does re-surface next turn (the backend
	# never popped it), so there is no answer to POST — but control MUST come
	# back, or the deferral is indistinguishable from a crash.
	petition_deferred.emit()


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
