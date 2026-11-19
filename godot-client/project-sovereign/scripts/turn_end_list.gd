extends PanelContainer

# =============================================================================
# INK & IRON - The list as the turn ends (row IC, November 19, 2026)
# =============================================================================
# End Turn stops once when something would bite or be wasted, and until now it
# said why in ONE joined sentence printed into the log - easy to miss, and with
# no way to act on it. This is the same stop said as a list, above the command
# line, where the eye already is: one row a matter, each row a door to the
# place that settles it, and the End Turn button still one press away.
#
# The rows are the desk's own (`backend/game_logic/today.py`, the matters that
# bite or waste the turn), so the desk and the stop can never disagree. The
# log's printed warning stays exactly as it was. The list sends nothing: a
# press is the signal `door_pressed(door, row_id)` and the host opens the place.
# Rows are Buttons: Tab and the arrows walk them, Enter or Space presses.
# =============================================================================

signal door_pressed(door: Dictionary, row_id: String)

const BITES := 1
const MARK_BITES := "!"
const LEGEND := " (! can cost you when the turn ends)"
const MAX_ROWS := 6      # the rest are counted on the last line

var _box: VBoxContainer = null
var _head: Label = null
var _rows_box: VBoxContainer = null
var _tail: Label = null
var _buttons: Array = []


func _init() -> void:
	name = "TurnEndList"
	visible = false
	var sb := StyleBoxFlat.new()
	sb.bg_color = Utils.UI_PANEL_BG      # solid: it stands over the log, whose last lines say the same thing
	sb.border_color = Color.html("#" + Utils.COLOR_WARNING)
	sb.set_border_width_all(1)
	sb.set_corner_radius_all(3)
	sb.set_content_margin_all(6)
	add_theme_stylebox_override("panel", sb)
	_box = VBoxContainer.new()
	_box.add_theme_constant_override("separation", 1)
	# The host stands the panel over the log's WHOLE room (lever L6); the rows
	# stand in its middle (at its foot they left "a big empty gap at the top"
	# — the third reading).
	_box.alignment = BoxContainer.ALIGNMENT_CENTER
	add_child(_box)
	_head = Label.new()
	_head.name = "Head"
	_head.theme_type_variation = &"Caption"
	_head.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_head.add_theme_color_override("font_color", Color.html("#" + Utils.COLOR_WARNING))
	_box.add_child(_head)
	_rows_box = VBoxContainer.new()
	_rows_box.name = "Rows"
	_rows_box.add_theme_constant_override("separation", 0)
	_box.add_child(_rows_box)
	_tail = Label.new()
	_tail.name = "Tail"
	_tail.theme_type_variation = &"Caption"
	_tail.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_tail.add_theme_color_override("font_color", Utils.toned(Utils.UI_TEXT_DIM))
	_box.add_child(_tail)


func show_rows(rows: Array, closing: String, max_rows: int = MAX_ROWS) -> void:
	"""Stand the list: `rows` are desk rows ({id, tier, text, more, door});
	`closing` is the one line under them (how to end the turn anyway);
	`max_rows` is how many the host has room for (the rest are counted)."""
	for b in _buttons:
		if is_instance_valid(b):
			_rows_box.remove_child(b)
			b.queue_free()
	_buttons.clear()
	var shown := mini(rows.size(), clampi(max_rows, 1, MAX_ROWS))
	# Lever L2 of the blind reading (all three readers: "the ! in front of a
	# matter is not explained"): the head says what the mark means, while a
	# row on show wears it.
	var any_bites := false
	for i in shown:
		if int((rows[i] as Dictionary).get("tier", 0)) == BITES:
			any_bites = true
	# "Still to decide": the card's own words (TO DECIDE) — the second and
	# third blind readings: four readers in six asked whether the card and
	# this list were one list or two. They are one; the words say so.
	_head.text = "Still to decide before the turn ends — %s%s. Press one to go to it." % [
			Utils.plural(rows.size(), "matter"), LEGEND if any_bites else ""]
	for i in shown:
		var row: Dictionary = rows[i]
		var b := Button.new()
		b.name = "Matter%d" % (i + 1)
		b.flat = true
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var bites := int(row.get("tier", 0)) == BITES
		var door = row.get("door", {})
		var has_door: bool = door is Dictionary and not (door as Dictionary).is_empty()
		# a row with no door is a sentence, not a button: no hand, no "›", no stop for Tab
		b.focus_mode = Control.FOCUS_ALL if has_door else Control.FOCUS_NONE
		b.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND if has_door else Control.CURSOR_ARROW
		b.text = "%s%s%s" % [(MARK_BITES + " ") if bites else "", str(row.get("text", "")), "  ›" if has_door else ""]
		var more := str(row.get("more", ""))
		b.tooltip_text = (more + "\n" if more != "" and has_door else more) + ("Press to go to it." if has_door else "")
		b.add_theme_color_override("font_color",
				Color.html("#" + Utils.COLOR_WARNING) if bites else Utils.toned(Utils.UI_TEXT_DIM))
		b.add_theme_color_override("font_hover_color", Utils.UI_GOLD_BRIGHT)
		b.add_theme_color_override("font_focus_color", Utils.UI_GOLD_BRIGHT)
		b.set_meta("row_id", str(row.get("id", "")))
		b.set_meta("door", row.get("door", {}))
		b.pressed.connect(_on_row_pressed.bind(b))
		_rows_box.add_child(b)
		_buttons.append(b)
	var extra := rows.size() - shown
	# "the TO DECIDE card": the card's own head, the words the player can find
	# on the screen (the review: "the desk above" named nothing he could see).
	_tail.text = ("…and %d more on the TO DECIDE card. " % extra if extra > 0 else "") + closing
	visible = not rows.is_empty()


func hide_list() -> void:
	visible = false


func shown_ids() -> Array:
	var out: Array = []
	for b in _buttons:
		if is_instance_valid(b):
			out.append(str(b.get_meta("row_id", "")))
	return out


func shown_texts() -> Array:
	var out: Array = []
	for b in _buttons:
		if is_instance_valid(b):
			out.append(str(b.text))
	return out


func last_button() -> Button:
	if _buttons.is_empty():
		return null
	return _buttons[_buttons.size() - 1]


func _on_row_pressed(b: Button) -> void:
	var door = b.get_meta("door", {})
	if door is Dictionary and not (door as Dictionary).is_empty():
		door_pressed.emit(door, str(b.get_meta("row_id", "")))
