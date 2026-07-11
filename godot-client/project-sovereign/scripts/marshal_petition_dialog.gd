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


func _add_option(option: Dictionary):
	var btn = Button.new()
	var label = str(option.get("label", "?"))
	var cost_note = str(option.get("cost_note", ""))
	if cost_note != "":
		label += "   [" + cost_note + "]"
	btn.text = label
	btn.custom_minimum_size = Vector2(0, 40)
	btn.add_theme_font_size_override("font_size", 14)
	btn.add_theme_color_override("font_color", Color(0.85, 0.75, 0.55, 1))
	btn.disabled = not bool(option.get("enabled", true))
	btn.tooltip_text = str(option.get("detail", ""))
	btn.pressed.connect(_on_option_pressed.bind(str(option.get("id", ""))))
	options_container.add_child(btn)

	var detail = str(option.get("detail", ""))
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
