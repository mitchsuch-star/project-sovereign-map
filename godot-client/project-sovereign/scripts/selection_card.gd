extends PanelContainer
class_name SelectionCard

# =============================================================================
# PROJECT SOVEREIGN - The Selection Card (Session UI-6, November 13, 2026)
# =============================================================================
# The war room's card for a selected marshal, in place of the two-line strip
# ("<Name> selected - click a province: march ..."), which had no order buttons.
#
#   row 1  portrait, name (title face), status badge, strength / morale, actions left
#   row 2  the seven fixed order slots, "<digit> Label - price" (MarshalState.order_specs)
#   row 3  the hint (the caller's strip text)
#
# A slot never moves: a verb he may not take stays in its place, disabled, and
# its reason is the hover (a folded reason is never a printed caption). The
# digits 1-7 come from main.gd through `press_slot(n)`; this card handles no
# key of its own and takes no focus, so the command line keeps the keyboard.
# Every verb goes out as a signal - the host sends it down the same /command
# road as typed text. The card judges no rule: prices and refusals are the
# backend's, read through the shared MarshalState kit.
#
# The compact view (Utils.compact_view(): a window under 600 logical px tall)
# shows a 32x40 portrait, digit + glyph buttons (the label and price on the
# hover) and a one-line hint, in at most 90 % of the HUD band.
# =============================================================================

const MarshalStateKit = preload("res://scripts/marshal_state.gd")

signal verb_pressed(verb: String, marshal: String)
signal cancel_order_pressed(marshal: String)
signal close_pressed

const CARD_WIDTH := 440.0
const CARD_MIN_WIDTH := 280.0
const COMPACT_BAND_SHARE := 0.9
const DENY_CUE := "error"

var _marshal := ""
var _view: Dictionary = {}
var _actions_left := 0
var _hint := ""
var _group: Array = []
var _group_total := 0
var _group_in_hand := 0
var _specs: Array = []
var _buttons: Dictionary = {}   # slot (int) -> Button
var _body: VBoxContainer = null
# The host's room for the card (logical px; 0 = no cap) — the 32:9 right wing is
# narrower than CARD_WIDTH, so main.gd sets it there (`_ui6_card_width_cap`).
var width_cap := 0.0


func _init() -> void:
	name = "SelectionCard"
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_theme_stylebox_override("panel", Utils.leather_frame(Utils.FRAME_HUD, 10.0))
	_body = VBoxContainer.new()
	_body.name = "Body"
	_body.mouse_filter = Control.MOUSE_FILTER_PASS
	_body.add_theme_constant_override("separation", 6)
	add_child(_body)
	visible = false


# ---------------------------------------------------------------- the API

func show_for(view: Dictionary, marshal: String, actions_left: int, hint_bbcode: String) -> void:
	"""Raise the card on one marshal: `view` is a MarshalState view."""
	_marshal = marshal
	_view = view.duplicate(true)
	_actions_left = actions_left
	_hint = hint_bbcode
	_group = []
	_render()
	show()


func show_group(names: Array, total_ap: int, in_hand: int, hint_bbcode: String) -> void:
	"""The group face: who marches together and what it costs - no verb buttons."""
	_marshal = ""
	_view = {}
	_group = names.duplicate()
	_group_total = total_ap
	_group_in_hand = in_hand
	_hint = hint_bbcode
	_render()
	show()


func hide_card() -> void:
	_marshal = ""
	_view = {}
	_group = []
	_specs = []
	_buttons = {}
	_clear_body()
	hide()


func current_marshal() -> String:
	return _marshal


func press_slot(n: int) -> bool:
	"""A digit from the host. True when the slot fired; a locked or missing slot
	plays the deny cue and nothing else."""
	var btn: Button = _buttons.get(n, null)
	var spec: Dictionary = _spec_of(n)
	if btn == null or spec.is_empty() or bool(spec.get("locked", false)) or _marshal == "":
		AudioManager.play(DENY_CUE)
		return false
	_fire(spec)
	return true


# ---------------------------------------------------------------- drawing

func _spec_of(n: int) -> Dictionary:
	for spec in _specs:
		if int(spec["slot"]) == n:
			return spec
	return {}


func _clear_body() -> void:
	if _body == null:
		return
	for child in _body.get_children():
		_body.remove_child(child)
		child.queue_free()


func _render() -> void:
	_clear_body()
	_buttons = {}
	_specs = []
	var compact := Utils.compact_view()
	custom_minimum_size = Vector2(_card_width(compact), 0.0)
	size.x = custom_minimum_size.x
	if _group.is_empty():
		_specs = MarshalStateKit.order_specs(_view)
		_body.add_child(_head_row(compact))
		_body.add_child(_order_row(compact))
	else:
		_body.add_child(_group_row(compact))
	_body.add_child(_hint_label(compact))
	reset_size()


func _card_width(compact: bool) -> float:
	var w := CARD_WIDTH
	if compact:
		var band := Vector2(0.0, CARD_WIDTH)
		var vp := get_viewport()
		if vp != null:
			band = Utils.hud_band(vp.get_visible_rect().size)
		var cap := maxf(CARD_MIN_WIDTH * 0.6, (band.y - band.x) * COMPACT_BAND_SHARE)
		w = minf(CARD_WIDTH, cap)
	if width_cap > 0.0:
		w = minf(w, maxf(CARD_MIN_WIDTH, width_cap))
	return w


func _head_row(compact: bool) -> Control:
	var row := HBoxContainer.new()
	row.name = "HeadRow"
	row.add_theme_constant_override("separation", 8)
	row.add_child(_portrait(_marshal, compact))
	var col := VBoxContainer.new()
	col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	col.add_theme_constant_override("separation", 2)
	row.add_child(col)
	var top := HBoxContainer.new()
	top.add_theme_constant_override("separation", 8)
	col.add_child(top)
	top.add_child(_title(Utils.humanize_entity_name(_marshal)))
	var status: Dictionary = MarshalStateKit.status_of(_view)
	top.add_child(_status_badge(status))
	var spacer := Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	spacer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	top.add_child(spacer)
	top.add_child(_close_button())
	col.add_child(_measured_rich("Figures", _figures_bbcode(), 0.0))
	return row


# UXR-2's scroll rule keeps unbounded text out of a panel's minimum, so no
# label here is fit_content: a one-line label is measured unwrapped (its own
# width and height), the hint wraps at the card's width and takes the height
# its lines need — the order strip's idiom (`main._show_order_strip`). The
# measure runs once the label stands in the tree (its font resolved).
func _measured_rich(node_name: String, bbcode: String, wrap_width: float,
		clip_to_card := false) -> RichTextLabel:
	var label := RichTextLabel.new()
	label.name = node_name
	label.bbcode_enabled = true
	label.fit_content = false
	label.scroll_active = false
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	if wrap_width > 0.0:
		label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	else:
		label.autowrap_mode = TextServer.AUTOWRAP_OFF
	label.clip_contents = clip_to_card
	label.text = bbcode
	_measure_rich.call_deferred(label, wrap_width, clip_to_card)
	return label


func _measure_rich(label: RichTextLabel, wrap_width: float, clip_to_card: bool) -> void:
	if not is_instance_valid(label) or not label.is_inside_tree():
		return
	var lay_w := wrap_width if wrap_width > 0.0 else 4096.0
	label.size = Vector2(lay_w, label.size.y)
	var w := wrap_width if wrap_width > 0.0 else float(label.get_content_width())
	if clip_to_card:
		w = 0.0   # the card's own width bounds it; the line clips at its edge
	label.custom_minimum_size = Vector2(w, float(label.get_content_height()))
	reset_size()


func _figures_bbcode() -> String:
	var parts := PackedStringArray()
	parts.append(Utils.bb_glyph("strength", 16) + " " + Utils.format_number(int(_view.get("strength", 0))))
	if _view.has("morale"):
		parts.append(Utils.bb_glyph("morale", 16) + " " + str(int(_view.get("morale", 0))) + "%")
	parts.append(Utils.bb_glyph("actions", 16) + " " + str(_actions_left) + " left")
	return "   ".join(parts)


func _order_row(compact: bool) -> Control:
	var flow := HFlowContainer.new()
	flow.name = "OrderRow"
	flow.add_theme_constant_override("h_separation", 4)
	flow.add_theme_constant_override("v_separation", 4)
	for spec in _specs:
		var btn := _slot_button(spec, compact)
		flow.add_child(btn)
		_buttons[int(spec["slot"])] = btn
	return flow


func _slot_button(spec: Dictionary, compact: bool) -> Button:
	var btn := Button.new()
	var slot := int(spec["slot"])
	var price := MarshalStateKit.price_text(int(spec["price"]))
	var label := str(spec["label"])
	btn.name = "Slot" + str(slot)
	btn.focus_mode = Control.FOCUS_NONE
	btn.mouse_filter = Control.MOUSE_FILTER_STOP
	var full := label + (" · " + price if price != "" else "")
	var tip := ""
	if compact:
		btn.text = str(slot)
		var tex = load(Utils.glyph(str(spec["glyph"])))
		if tex is Texture2D:
			btn.icon = tex
			btn.add_theme_constant_override("icon_max_width", 16)
		tip = full
	else:
		btn.text = str(slot) + " " + full
	var locked := bool(spec["locked"])
	btn.disabled = locked
	var reason := str(spec["reason"])
	if locked:
		if reason != "":
			tip = (tip + " - " + reason) if tip != "" else reason
	btn.tooltip_text = tip
	btn.pressed.connect(_fire.bind(spec))
	return btn


func _fire(spec: Dictionary) -> void:
	AudioManager.play("click")
	var verb := str(spec["verb"])
	if verb == "cancel":
		cancel_order_pressed.emit(_marshal)
	else:
		verb_pressed.emit(verb, _marshal)


func _group_row(compact: bool) -> Control:
	var col := VBoxContainer.new()
	col.name = "GroupFace"
	col.add_theme_constant_override("separation", 4)
	var top := HBoxContainer.new()
	top.add_theme_constant_override("separation", 8)
	col.add_child(top)
	var shown := PackedStringArray()
	for n in _group:
		shown.append(Utils.humanize_entity_name(str(n)))
	var names_label := _title(", ".join(shown))
	names_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	names_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	names_label.custom_minimum_size = Vector2(80.0, 0.0)
	top.add_child(names_label)
	top.add_child(_close_button())
	var line := "march together · " + str(_group_total) + " of " + str(_group_in_hand) + " actions in hand"
	if _group_total > _group_in_hand:
		line = "[color=#" + Utils.COLOR_WARNING + "]" + line + "[/color]"
	col.add_child(_measured_rich("GroupSum", Utils.bb_glyph("actions", 16) + " " + line, 0.0, true))
	return col


func _hint_label(compact: bool) -> Control:
	# Ordinary: the hint wraps at the card's inner width. Compact: one line,
	# clipped at the card's edge (the hover of the card's buttons carries the rest).
	var inner := maxf(120.0, _card_width(compact) - 28.0)
	var hint := _measured_rich("Hint", _hint, 0.0 if compact else inner, compact)
	hint.add_theme_color_override("default_color", Utils.UI_TEXT_DIM)
	return hint


func _portrait(marshal: String, compact: bool) -> Control:
	var size_px := Vector2(32.0, 40.0) if compact else Vector2(48.0, 60.0)
	var path := MarshalStateKit.portrait_path(marshal)
	var holder := Control.new()
	holder.name = "Portrait"
	holder.custom_minimum_size = size_px
	holder.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var tex = load(path) if path != "" else null
	if tex is Texture2D:
		var rect := TextureRect.new()
		rect.texture = tex
		rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
		rect.set_anchors_preset(Control.PRESET_FULL_RECT)
		rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
		holder.add_child(rect)
	else:
		var mono := Label.new()
		mono.text = MarshalStateKit.monogram(marshal)
		mono.set_anchors_preset(Control.PRESET_FULL_RECT)
		mono.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		mono.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		mono.add_theme_color_override("font_color", Utils.UI_GOLD)
		mono.mouse_filter = Control.MOUSE_FILTER_IGNORE
		holder.add_child(mono)
	return holder


func _title(text: String) -> Label:
	var label := Label.new()
	label.name = "Title"
	label.text = text
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	label.add_theme_color_override("font_color", Utils.UI_GOLD_BRIGHT)
	var face = load(Utils.TITLE_FONT)
	if face is Font:
		label.add_theme_font_override("font", face)
	return label


func _status_badge(status: Dictionary) -> Control:
	var glyph_name := str(status.get("glyph", ""))
	var tone := str(status.get("tone", Utils.COLOR_GOLD))
	var lead := Utils.bb_glyph(glyph_name, 16, tone) + " " if glyph_name != "" else ""
	var badge := _measured_rich("StatusBadge",
		"[color=#" + tone + "]" + lead + str(status.get("label", "")) + "[/color]", 0.0)
	badge.tooltip_text = str(status.get("detail", ""))
	badge.mouse_filter = Control.MOUSE_FILTER_PASS
	return badge


func _close_button() -> Button:
	var btn := Button.new()
	btn.name = "CloseButton"
	btn.text = "×"
	btn.flat = true
	btn.focus_mode = Control.FOCUS_NONE
	btn.tooltip_text = "Deselect (Esc)"
	btn.pressed.connect(func(): close_pressed.emit())
	return btn
