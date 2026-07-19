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


func _ready():
	hide()
	acknowledge_btn.pressed.connect(_on_acknowledge_pressed)


func show_proclamation(data: Dictionary):
	"""Display the formation card. §11.8 stage 2, top to bottom."""
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

	var bbcode := ""
	bbcode += "[center]%s[/center]\n" % Utils.bbcode_color(
		"[b]A NATION IS PROCLAIMED[/b]", Utils.COLOR_GOLD)

	# The old name, struck through — "a country ended, a country began".
	if old_name != "" and old_name != new_name:
		bbcode += "[center]%s[/center]\n" % Utils.bbcode_color(
			"[s]%s[/s]" % old_name, Utils.COLOR_DIMMED)
	bbcode += "[center][font_size=26]%s[/font_size][/center]\n\n" % (
		Utils.bbcode_color("[b]%s[/b]" % new_name, Utils.COLOR_GOLD))

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

	# Perspective-aware subtitle: witness vs author.
	var subtitle := str(data.get("subtitle", ""))
	if subtitle != "":
		bbcode += "\n[center]%s[/center]" % Utils.bbcode_color(
			"[i]%s[/i]" % subtitle, Utils.COLOR_DIMMED)

	content_label.text = ""
	content_label.append_text(Utils.humanize_nation_keys_in_text(bbcode))
	# PopupBase.close_popup() permanently disables every Button, so a second
	# proclamation would open with a dead Acknowledge — re-enable on show.
	acknowledge_btn.disabled = false
	show()
	# Fit to the CURRENT logical viewport (Interface Scale can halve it).
	# A blocking modal whose only dismiss button leaves the screen is
	# unrecoverable, so this runs after show(), once layout has settled.
	Utils.clamp_centered_panel($PanelContainer)


func _on_acknowledge_pressed():
	close_popup()
	dismissed.emit()
