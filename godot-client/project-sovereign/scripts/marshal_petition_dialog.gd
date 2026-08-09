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
@onready var body_label = $PanelContainer/VBoxContainer/BodyLabel
@onready var options_container = $PanelContainer/VBoxContainer/ScrollContainer/OptionsContainer
@onready var later_button = $PanelContainer/VBoxContainer/LaterButton

const KIND_TITLES = {
	"jealousy_confrontation": "A MARSHAL SEEKS AN AUDIENCE",
	"rivalry_confrontation": "A RIVALRY AMONG THE MARSHALS",
	"fontainebleau": "THE MARSHALS PETITION THE EMPEROR",
	"war_weary": "A MARSHAL COUNSELS PEACE",
}


func _ready():
	if later_button:
		later_button.pressed.connect(_on_later)
	hide()


func show_petition(petition: Dictionary):
	"""Render one backend petition: title, body, dynamic option buttons."""
	AudioManager.play("sword_draw")
	var kind = str(petition.get("kind", ""))
	title_label.text = str(petition.get("title", KIND_TITLES.get(kind, "A PETITION")))
	if title_label.text == "":
		title_label.text = KIND_TITLES.get(kind, "A PETITION")

	var body = "[color=#d0c0b0]" + str(petition.get("body", "")) + "[/color]"
	body_label.text = body

	for child in options_container.get_children():
		child.queue_free()

	var options = petition.get("options", [])
	if options is Array:
		for option in options:
			if not (option is Dictionary):
				continue
			_add_option(option)

	# Fontainebleau and war-weary petitions demand an answer NOW — the
	# moment does not keep. Grievance/rivalry petitions may wait a turn.
	if later_button:
		later_button.visible = kind in ["jealousy_confrontation", "rivalry_confrontation"]

	show()
	# July 18, 2026 viewport sweep: fit to the CURRENT logical viewport.
	# Interface Scale (content_scale_factor, up to 2.0) divides the logical
	# viewport, so a fixed authored rect can carry the action row off-screen
	# and leave a modal undismissable. The helper is a no-op wherever the
	# panel already fits, and returns early for non-centre-anchored panels.
	Utils.clamp_centered_panel($PanelContainer)


func _add_option(option: Dictionary):
	var btn = Button.new()
	var label = str(option.get("label", "?"))
	var cost_note = str(option.get("cost_note", ""))
	if cost_note != "":
		label += "   [" + cost_note + "]"
	btn.text = label
	btn.custom_minimum_size = Vector2(0, 40)
	btn.add_theme_font_size_override("font_size", 14)
	btn.add_theme_color_override("font_color", Utils.UI_GOLD)
	var is_enabled = bool(option.get("enabled", true))
	btn.disabled = not is_enabled
	btn.tooltip_text = str(option.get("detail", ""))
	if not is_enabled:
		# July 25, 2026 in-game review: a greyed arm used to say nothing about
		# WHY, and at a glance read as merely un-hovered. Dim the label and let
		# the detail line carry the backend's reason.
		btn.add_theme_color_override("font_color", Color(0.55, 0.52, 0.48, 1))
		btn.add_theme_color_override("font_disabled_color", Color(0.55, 0.52, 0.48, 1))
	btn.pressed.connect(_on_option_pressed.bind(str(option.get("id", ""))))
	options_container.add_child(btn)

	var detail = str(option.get("detail", ""))
	var reason = str(option.get("unavailable_reason", ""))
	if not is_enabled and reason != "":
		detail = reason if detail == "" else reason + "  " + detail
	if detail != "":
		var detail_label = Label.new()
		detail_label.text = "    " + detail
		detail_label.add_theme_font_size_override("font_size", 11)
		detail_label.add_theme_color_override("font_color", Color(0.6, 0.6, 0.65, 1))
		detail_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		options_container.add_child(detail_label)


func _on_option_pressed(choice_id: String):
	hide()
	petition_choice.emit(choice_id)


func _on_later():
	hide()
	# The pending petition genuinely does re-surface next turn (the backend
	# never popped it), so there is no answer to POST — but control MUST come
	# back, or the deferral is indistinguishable from a crash.
	petition_deferred.emit()
