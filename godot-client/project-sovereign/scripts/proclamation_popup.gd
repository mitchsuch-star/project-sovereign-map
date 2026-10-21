extends PopupBase

# =============================================================================
# PROJECT SOVEREIGN — The Proclamation (Nation Agendas NA-6b, spec §11.8)
# =============================================================================
# The one place the game stops for a landmark: a nation has been formed or
# created. CanvasLayer 117 (the only free slot in 101-118, measured).
#
# Choice-less by design — §11.8: "the moment is a fact, not a decision"
# (the decisions happened at the settlement table or on the battlefield).
# [Acknowledge] is therefore a CLIENT-SIDE dismiss with no response
# endpoint: the backend already popped the card off the PopupQueue when it
# delivered it, and the persistent notification is the click-past recovery.
#
# Never blocks the turn: Acknowledge is always available and always enabled.
# =============================================================================

signal dismissed

@onready var new_flag = $PanelContainer/VBoxContainer/FlagRow/NewFlag
@onready var content_label = $PanelContainer/VBoxContainer/ContentScroll/ContentLabel
@onready var acknowledge_btn = $PanelContainer/VBoxContainer/ButtonContainer/AcknowledgeButton
# UXR3-62 (Pre-Deploy S12): the name was a BBCode [font_size=26] inside the
# body; it is a Label on the theme step ProclamationName, under a rich head
# (the heading and the struck old name), above the scrolling body.
var head_label: RichTextLabel
var name_label: Label
# SFR-B11 (SF-RR5, October 21, 2026): the perspective line ("By your hand.")
# closes the card UNDER the scrolling body, above Acknowledge — at Interface
# Scale 2.0 it sat below the body's fold, the card's own signature unread.
var subtitle_label: RichTextLabel


func _ready():
	hide()
	acknowledge_btn.pressed.connect(_on_acknowledge_pressed)
	# PC15-18 (NV-P1 family census): a fit_content RichTextLabel inside a
	# ScrollContainer defaults to MOUSE_FILTER_STOP and eats the wheel
	# before its parent can scroll. PASS still delivers _gui_input.
	content_label.mouse_filter = Control.MOUSE_FILTER_PASS


func _build_head() -> void:
	if name_label != null:
		return
	var vbox: VBoxContainer = $PanelContainer/VBoxContainer
	var scroll: Control = $PanelContainer/VBoxContainer/ContentScroll
	head_label = RichTextLabel.new()
	head_label.name = "HeadLabel"
	head_label.bbcode_enabled = true
	head_label.fit_content = true
	head_label.scroll_active = false
	head_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	vbox.add_child(head_label)
	vbox.move_child(head_label, scroll.get_index())
	name_label = Label.new()
	name_label.name = "NameLabel"
	name_label.theme_type_variation = &"ProclamationName"
	name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	name_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	name_label.add_theme_color_override("font_color", Color(Utils.COLOR_GOLD))
	var bold := head_label.get_theme_font("bold_font")
	if bold != null:
		name_label.add_theme_font_override("font", bold)
	vbox.add_child(name_label)
	vbox.move_child(name_label, scroll.get_index())
	subtitle_label = RichTextLabel.new()
	subtitle_label.name = "SubtitleLabel"
	subtitle_label.bbcode_enabled = true
	subtitle_label.fit_content = true
	subtitle_label.scroll_active = false
	subtitle_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	vbox.add_child(subtitle_label)
	vbox.move_child(subtitle_label, scroll.get_index() + 1)


func show_proclamation(data: Dictionary):
	"""Display the formation card. §11.8 stage 2, top to bottom."""
	claim_cue(AudioManager.play("bells_peal"))  # UX23-R1: an arrival sound goes when the panel does
	# the new flag over the struck old
	var new_name := str(data.get("display_name", ""))
	var old_name := str(data.get("old_display_name", ""))
	var flag_tag := str(data.get("flag_tag", ""))

	# The NEW flag, large. Resolved by the formation's own asset tag rather
	# than the nation key — the tag never changes, the colours do.
	var flag_path := Utils.nation_flag_path(flag_tag)
	if flag_path != "" and ResourceLoader.exists(flag_path):
		new_flag.texture = load(flag_path)
		new_flag.visible = true
	else:
		# No asset is not a reason to withhold the moment.
		new_flag.texture = null
		new_flag.visible = false

	_build_head()
	var head := "[center]%s[/center]" % Utils.bbcode_color(
		"[b]A NATION IS PROCLAIMED[/b]", Utils.COLOR_GOLD)

	# The old name, struck through — "a country ended, a country began".
	if old_name != "" and old_name != new_name:
		head += "\n[center]%s[/center]" % Utils.bbcode_color(
			"[s]%s[/s]" % old_name, Utils.COLOR_INFO)
	head_label.text = Utils.humanize_nation_keys_in_text(head)
	name_label.text = Utils.humanize_nation_keys_in_text(new_name)

	var bbcode := ""

	# The engraved proclamation line (authored per formation).
	var proclamation := str(data.get("proclamation", ""))
	if proclamation != "":
		bbcode += "[center][i]%s[/i][/center]\n\n" % proclamation

	# The terms of its birth, stated plainly.
	var terms = data.get("terms", [])
	if typeof(terms) == TYPE_ARRAY and not terms.is_empty():
		for term in terms:
			bbcode += "  • %s\n" % str(term)
		bbcode += "\n"

	var next_design := str(data.get("next_design", ""))
	if next_design != "":
		bbcode += "%s\n" % Utils.bbcode_color(
			"Its court now takes up a new design: %s." % next_design,
			Utils.COLOR_INFO)

	# §11.9 — the courts that read this as a declaration.
	var fury := str(data.get("fury_line", ""))
	if fury != "":
		bbcode += "%s\n" % Utils.bbcode_color(fury, Utils.COLOR_WARNING)

	# Perspective-aware subtitle: witness vs author — under the body, never
	# below its fold (SFR-B11).
	var subtitle := str(data.get("subtitle", ""))
	subtitle_label.text = "" if subtitle == "" else "[center]%s[/center]" % Utils.bbcode_color(
		"[i]%s[/i]" % Utils.humanize_nation_keys_in_text(subtitle), Utils.COLOR_INFO)
	subtitle_label.visible = subtitle != ""

	# S12: through `text`, never append_text (the instrument reads the label's text).
	# SFR-B11: no trailing blank line spends the body's last visible row.
	content_label.text = Utils.humanize_nation_keys_in_text(bbcode.strip_edges(false, true))
	# PopupBase.close_popup() permanently disables every Button, so a second
	# proclamation would open with a dead Acknowledge — re-enable on show.
	acknowledge_btn.disabled = false
	show()
	# Fit to the CURRENT logical viewport (Interface Scale can halve it).
	# A blocking modal whose only dismiss button leaves the screen is
	# unrecoverable, so this runs after show(), once layout has settled.
	Utils.clamp_centered_panel($PanelContainer)


func esc_control() -> Button:
	# FA-94: a single-Acknowledge ceremony card is read-and-dismiss; ESC
	# presses Acknowledge (through its handler, so `dismissed` still fires).
	return acknowledge_btn


func _on_acknowledge_pressed():
	close_popup()
	dismissed.emit()
