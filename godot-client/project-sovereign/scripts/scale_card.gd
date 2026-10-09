extends PanelContainer
class_name ScaleCard

# =============================================================================
# INK & IRON — "Can you read this comfortably?" (UXR-1, October 9, 2026)
# =============================================================================
# The first-run sizing card — the ONE new surface of the UX/UI review plan.
# The main menu raises it on the first boot (and whenever the stored scale is
# still the derivation's and never acknowledged); Settings → INTERFACE opens
# it on demand. It asks ONE question with a LIVE sample — the command window's
# body line, the tutor card's caption and a counter row, drawn at the scale
# the slider holds — and persists the answer through UiSettings.set_ui_scale,
# which marks the scale CHOSEN so no later derivation overwrites it.
#
# The host applies the preview (`scale_previewed`) to its own window — the
# menu sets content_scale_factor directly; main.gd owns the map compensation
# — exactly the contract the SettingsPanel slider already has.
# Display-only (Golden Rule 6).
# =============================================================================

signal scale_previewed(value: float)
signal accepted(value: float)
signal closed

const SAMPLE_BODY := "Sire — Austria has pushed two corps over the Iller while her main army musters at Vienna. Before orders, knowledge."
const SAMPLE_CAPTION := "THE SCHOOL OF WAR   1 of 20   ·   Turn 1 — Late September 1805"
const SAMPLE_COUNTERS := "Turn: 1    Actions: 4/4    Admin: 2/2    Gold: 900    Inf: 80,000"

var _slider: HSlider
var _value_label: Label
var _derived_label: Label
var _derived := 1.0
var _opened_at := 1.0
var _built := false


func _ready() -> void:
	if not _built:
		_build()


func _build() -> void:
	_built = true
	name = "ScaleCard"
	set_anchors_preset(Control.PRESET_CENTER)
	custom_minimum_size = Vector2(560, 0)
	offset_left = -280
	offset_right = 280
	offset_top = -230
	offset_bottom = 230
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.055, 0.07, 0.115, 0.97)
	style.border_color = Utils.UI_GOLD
	style.set_border_width_all(2)
	style.set_corner_radius_all(6)
	style.set_content_margin_all(22)
	add_theme_stylebox_override("panel", style)

	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 12)
	add_child(vbox)

	var header := Label.new()
	header.text = "CAN YOU READ THIS COMFORTABLY?"
	header.theme_type_variation = &"HeadingLabel"
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	vbox.add_child(header)

	var lead := Label.new()
	lead.text = ("Ink & Iron sized its interface for this screen. Drag the slider until the "
		+ "lines below read easily from where you sit — every window, ledger and pop-up "
		+ "follows. Settings → Interface changes it later.")
	lead.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	lead.add_theme_color_override("font_color", Utils.UI_TEXT_DIM)
	vbox.add_child(lead)

	# The sample: the three kinds of text the player meets first, at the
	# theme's own sizes (body 16, Caption 14), so the slider's effect is the
	# real one.
	var sample := PanelContainer.new()
	var sample_style := StyleBoxFlat.new()
	sample_style.bg_color = Color(0.07, 0.09, 0.14, 1.0)
	sample_style.border_color = Color(0.85, 0.7, 0.3, 0.6)
	sample_style.set_border_width_all(1)
	sample_style.set_corner_radius_all(3)
	sample_style.set_content_margin_all(12)
	sample.add_theme_stylebox_override("panel", sample_style)
	vbox.add_child(sample)
	var sample_box := VBoxContainer.new()
	sample_box.add_theme_constant_override("separation", 6)
	sample.add_child(sample_box)
	var caption := Label.new()
	caption.name = "SampleCaption"
	caption.text = SAMPLE_CAPTION
	caption.theme_type_variation = &"Caption"
	caption.add_theme_color_override("font_color", Color(0.85, 0.7, 0.3, 1))
	sample_box.add_child(caption)
	var body := Label.new()
	body.name = "SampleBody"
	body.text = SAMPLE_BODY
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	sample_box.add_child(body)
	var counters := Label.new()
	counters.name = "SampleCounters"
	counters.text = SAMPLE_COUNTERS
	counters.theme_type_variation = &"Caption"
	counters.add_theme_color_override("font_color", Utils.UI_TEXT_DIM)
	sample_box.add_child(counters)

	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	_slider = HSlider.new()
	_slider.min_value = UiSettings.MIN_UI_SCALE
	_slider.max_value = UiSettings.MAX_UI_SCALE
	_slider.step = UiSettings.UI_SCALE_STEP
	_slider.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_slider.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	_slider.custom_minimum_size = Vector2(240, 0)
	_slider.value_changed.connect(_on_slider_changed)
	row.add_child(_slider)
	_value_label = Label.new()
	_value_label.custom_minimum_size = Vector2(60, 0)
	_value_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_value_label.add_theme_color_override("font_color", Color(0.9, 0.85, 0.7))
	row.add_child(_value_label)
	vbox.add_child(row)

	_derived_label = Label.new()
	_derived_label.theme_type_variation = &"Caption"
	_derived_label.add_theme_color_override("font_color", Utils.UI_TEXT_DIM)
	_derived_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	vbox.add_child(_derived_label)

	var buttons := HBoxContainer.new()
	buttons.add_theme_constant_override("separation", 10)
	var fit := Button.new()
	fit.name = "SizeForScreenButton"
	fit.text = "Size for this screen"
	fit.custom_minimum_size = Vector2(0, 40)
	fit.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	fit.pressed.connect(_on_fit_pressed)
	buttons.add_child(fit)
	var ok := Button.new()
	ok.name = "LooksRightButton"
	ok.text = "Looks right"
	ok.custom_minimum_size = Vector2(0, 40)
	ok.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	ok.pressed.connect(_on_accept)
	buttons.add_child(ok)
	vbox.add_child(buttons)


func open(current: float, derived: float) -> void:
	"""Show the card at `current` (what the window draws at now), remembering
	`derived` for the 'Size for this screen' button."""
	if not _built:
		_build()
	_derived = derived
	_opened_at = current
	_slider.set_value_no_signal(clampf(current, UiSettings.MIN_UI_SCALE, UiSettings.MAX_UI_SCALE))
	_update_labels(_slider.value)
	visible = true
	Utils.clamp_centered_panel(self)
	_slider.grab_focus()


func current_value() -> float:
	return _slider.value if _slider != null else _opened_at


func _update_labels(value: float) -> void:
	_value_label.text = "%d%%" % int(round(value * 100.0))
	_derived_label.text = ("For this screen the derived size is %d%%. A chosen size is kept; "
		+ "'Size for this screen' returns to the derived one.") % int(round(_derived * 100.0))


func _on_slider_changed(value: float) -> void:
	_update_labels(value)
	# A preview on every step — the host applies it; nothing is stored until
	# 'Looks right'.
	scale_previewed.emit(value)


func _on_fit_pressed() -> void:
	_slider.value = _derived


func _on_accept() -> void:
	var value: float = _slider.value
	UiSettings.set_ui_scale(value)
	UiSettings.set_scale_acknowledged(true)
	visible = false
	accepted.emit(value)
	closed.emit()


func _unhandled_input(event: InputEvent) -> void:
	if visible and event.is_action_pressed("ui_cancel"):
		# Esc keeps what is on screen: the player has seen it at this size.
		_on_accept()
		get_viewport().set_input_as_handled()
