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


func _ready():
	if later_button:
		later_button.pressed.connect(_on_later)
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
	AudioManager.play("sword_draw")
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
	Utils.clamp_centered_panel($PanelContainer)


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
	btn.add_theme_color_override("font_color", Utils.UI_GOLD)
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
	hide()
	petition_choice.emit(choice_id)


func _on_later():
	hide()
	# The pending petition genuinely does re-surface next turn (the backend
	# never popped it), so there is no answer to POST — but control MUST come
	# back, or the deferral is indistinguishable from a crash.
	petition_deferred.emit()
