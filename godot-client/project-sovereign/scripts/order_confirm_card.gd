extends PopupBase

# =============================================================================
# PROJECT SOVEREIGN - The Order Card (row CC, CC-3 "Select, click, Enter")
# =============================================================================
# The confirm card a MAP GESTURE opens (the plan's D4: select then click, or
# a drag — the province panel's chips still send directly): the exact command
# the backend quoted (`GET /march_quotes?marshal=…`), its price, its clock,
# its road, the standing order it would replace, whether he may object, the
# contact the road meets — and [Send] [Put in line] [Cancel].
#
# MODAL (dialog_manager-registered, layer 123): while it is up it takes EVERY
# key in `_input` — Enter sends (a refused order's Enter only closes it), Esc
# cancels, and nothing else reaches the command line or a hotkey beneath it
# (a bare E would have ended the turn). Its buttons take no focus. It composes
# no order and judges no rule: every word on it is the quote's.
# =============================================================================

signal send_requested(command: String)
signal line_requested(command: String)
signal cancelled

@onready var title_label: Label = $PanelContainer/VBox/TitleLabel
@onready var command_label: Label = $PanelContainer/VBox/CommandLabel
@onready var terms_label: RichTextLabel = $PanelContainer/VBox/TermsLabel
@onready var send_button: Button = $PanelContainer/VBox/Buttons/SendButton
@onready var line_button: Button = $PanelContainer/VBox/Buttons/LineButton
@onready var cancel_button: Button = $PanelContainer/VBox/Buttons/CancelButton

var _quote: Dictionary = {}
# The screen rects the card stands clear of (the selected corps' ring and
# ghost road, the selection's strip) — GLOBAL, logical px.
var _avoid: Array = []
const CARD_WIDTH := 560.0
const CARD_EDGE := 12.0


func _ready():
	hide()
	send_button.pressed.connect(_on_send)
	line_button.pressed.connect(_on_line)
	cancel_button.pressed.connect(_on_cancel)


func open_card(quote: Dictionary, title: String, reading: String, avoid: Array = []) -> void:
	"""Raise the card — on the quote when it is in hand, else on a line that
	says it is being read (`show_quote` fills it when the answer lands) —
	where it hides least of `avoid` (the road it confirms)."""
	title_label.text = title
	_avoid = avoid.duplicate()
	if quote.is_empty():
		_quote = {}
		command_label.text = "…"
		terms_label.text = "[color=#" + Utils.COLOR_INFO + "]" + reading + "[/color]"
		_set_buttons(false, false)
	else:
		show_quote(quote)
	if not visible:
		AudioManager.play("select")
	show()
	# The line must not take the keys the card is reading.
	var viewport := get_viewport()
	if viewport != null:
		viewport.gui_release_focus()
	refit()


func show_quote(quote: Dictionary) -> void:
	_quote = quote.duplicate(true)
	var command_text := str(_quote.get("command", ""))
	command_label.text = command_text if command_text != "" else "—"
	terms_label.text = _terms(_quote)
	var ok := bool(_quote.get("ok", false)) and command_text != ""
	_set_buttons(ok, command_text != "")
	if visible:
		refit.call_deferred()   # the terms re-wrap first


func set_avoid(avoid: Array) -> void:
	_avoid = avoid.duplicate()
	if visible:
		refit()


func refit() -> void:
	"""The card's place (UXR-2's live-refit road calls it too): sized to its
	content, clamped inside the viewport, and — among the centre, the top,
	the bottom and the two sides — where it covers least of `_avoid`; the
	centre wins a tie."""
	var panel: PanelContainer = $PanelContainer
	# The layout law's clamp first (UXR-2): the authored rect fitted to the
	# viewport, every descendant minimum relaxed where it would not fit (at
	# Interface Scale 2.0 the logical viewport halves); then the card's own
	# size and place below.
	Utils.clamp_centered_panel($PanelContainer)
	var view := panel.get_viewport_rect().size
	var w := minf(CARD_WIDTH, maxf(160.0, view.x - 2.0 * CARD_EDGE))
	panel.custom_minimum_size = Vector2(w, 0.0)
	var h := minf(_content_height(w, view.y), maxf(120.0, view.y - 2.0 * CARD_EDGE))
	var top := Utils.TOP_BAR_HEIGHT + Utils.top_bar_growth() + CARD_EDGE
	var mid_y := clampf((view.y - h) / 2.0, top, maxf(top, view.y - h - CARD_EDGE))
	var spots := [
		Vector2((view.x - w) / 2.0, mid_y),
		Vector2((view.x - w) / 2.0, top),
		Vector2((view.x - w) / 2.0, maxf(top, view.y - h - CARD_EDGE)),
		Vector2(CARD_EDGE, mid_y),
		Vector2(maxf(CARD_EDGE, view.x - w - CARD_EDGE), mid_y),
	]
	var pick: Vector2 = spots[0]
	var least := INF
	for spot in spots:
		var box := Rect2(spot, Vector2(w, h))
		var covered := 0.0
		for r in _avoid:
			if r is Rect2 and (r as Rect2).size != Vector2.ZERO:
				covered += box.intersection((r as Rect2).grow(16.0)).get_area()
		if covered < least - 0.5:
			least = covered
			pick = spot
	# Centre-anchored (the scene's, and `Utils.clamp_centered_panel`'s rule):
	# the offsets are measured from the viewport's middle.
	panel.offset_left = pick.x - view.x * 0.5
	panel.offset_right = panel.offset_left + w
	panel.offset_top = pick.y - view.y * 0.5
	panel.offset_bottom = panel.offset_top + h


func _content_height(w: float, view_h: float) -> float:
	"""The card's height at width `w`, measured now — and the terms' room
	set: the terms laid out at the inner width (a container's minimum before
	its first layout reads a wrapping label at width 0 — a card 1,483 px
	tall), every other row at its own minimum, the separations and the
	panel's margins. The terms are BOUNDED (UXR-2's scroll rule): their
	height is the text's, capped at the room the viewport leaves — longer
	terms scroll inside the label."""
	var panel: PanelContainer = $PanelContainer
	var box: VBoxContainer = $PanelContainer/VBox
	var frame: StyleBox = panel.get_theme_stylebox("panel")
	var margins: Vector2 = frame.get_minimum_size() if frame != null else Vector2(40, 32)
	terms_label.size = Vector2(maxf(40.0, w - margins.x), terms_label.size.y)
	var others := margins.y
	var rows := 0
	for child in box.get_children():
		var c := child as Control
		if c == null or not c.visible:
			continue
		rows += 1
		if c != terms_label:
			others += c.get_combined_minimum_size().y
	others += float(box.get_theme_constant("separation")) * maxf(0.0, float(rows - 1))
	var room := maxf(48.0, view_h - 2.0 * CARD_EDGE - others)
	var terms_h := minf(float(terms_label.get_content_height()), room)
	terms_label.custom_minimum_size = Vector2(0.0, terms_h)
	return others + terms_h


func placed_rect() -> Rect2:
	"""Where the card stands (GLOBAL) — read by the CC harness."""
	return ($PanelContainer as Control).get_global_rect()


func command() -> String:
	"""The command on the card — exactly the quote's."""
	return str(_quote.get("command", ""))


func is_sendable() -> bool:
	return visible and not send_button.disabled


func close_card() -> void:
	"""Shut the card WITHOUT an answer (the selection was let go under it)."""
	_quote = {}
	if visible:
		close_popup()


func _set_buttons(can_send: bool, can_line: bool) -> void:
	send_button.disabled = not can_send
	line_button.disabled = not can_line
	cancel_button.disabled = false


func _terms(q: Dictionary) -> String:
	"""The quote's own terms, line by line."""
	var lines := PackedStringArray()
	if not bool(q.get("ok", false)):
		var why := str(q.get("refusal", "")).strip_edges()
		if why == "":
			why = "the order cannot be given"
		lines.append("[color=#" + Utils.COLOR_ERROR + "]Refused — " + why + "[/color]")
		return "\n".join(lines)
	if bool(q.get("already", false)):
		lines.append("[b]No cost[/b] — " + str(q.get("note", "he is already carrying out that order.")))
		return "\n".join(lines)
	lines.append("[b]" + _price(int(q.get("ap", 0))) + "[/b] · " + _clock(q))
	var road = q.get("road", [])
	if road is Array and road.size() > 1:
		lines.append("[color=#" + Utils.COLOR_INFO + "]Road: " + " → ".join(PackedStringArray(road)) + "[/color]")
	var replaces := str(q.get("replaces", ""))
	if replaces != "":
		lines.append("[color=#" + Utils.COLOR_GOLD + "]Replaces " + replaces + ".[/color]")
	if str(q.get("objection", "none")) == "possible":
		lines.append("[color=#" + Utils.COLOR_WARNING + "]He may object.[/color]")
	var contact := str(q.get("contact", ""))
	var note := str(q.get("note", ""))
	if contact != "":
		lines.append("[color=#" + Utils.COLOR_WARNING + "]" + contact + "[/color]")
	if note != "" and note != contact:
		lines.append("[color=#" + Utils.COLOR_WARNING + "]" + note + "[/color]")
	return "\n".join(lines)


static func _price(ap: int) -> String:
	return "free" if ap <= 0 else Utils.plural(ap, "action")


static func _clock(q: Dictionary) -> String:
	var turns := int(q.get("turns", 0))
	match str(q.get("kind", "")):
		"attack":
			return "attacks at once"
		"support", "follow":
			return "joins him this turn" if turns <= 0 else "joins him in " + Utils.plural(turns, "turn")
	return "arrives this turn" if turns <= 0 else "arrives in " + Utils.plural(turns, "turn")


func _input(event: InputEvent) -> void:
	if not visible or not (event is InputEventKey):
		return
	# Modal: every key is the card's while it is up.
	get_viewport().set_input_as_handled()
	if not event.pressed or event.echo:
		return
	match event.keycode:
		KEY_ENTER, KEY_KP_ENTER:
			if not send_button.disabled:
				_on_send()
			else:
				_on_cancel()   # a refused order's Enter only closes the card
		KEY_ESCAPE:
			_on_cancel()


func _on_send() -> void:
	var cmd := command()
	if cmd == "" or send_button.disabled:
		return
	_close_quietly()   # the quill answers a sent order, not the "back" tap
	send_requested.emit(cmd)


func _on_line() -> void:
	var cmd := command()
	if cmd == "":
		return
	_close_quietly()
	line_requested.emit(cmd)


func _close_quietly() -> void:
	_disable_all_buttons()
	hide()


func _on_cancel() -> void:
	_quote = {}
	close_popup()
	cancelled.emit()
