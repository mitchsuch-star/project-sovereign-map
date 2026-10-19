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
# CC-5 "The war table" gives the same card two more faces:
#   * the ARROW card — a standing order of ours, clicked on the map: its
#     road and clock, and [Cancel order (1 AP)] (POST /cancel_order — the
#     price and the trust it costs are the backend's) [Change (Enter)]
#     (selects him: CC-3) [Close (Esc)]. Enter is the harmless answer.
#   * the GROUP card — a Ctrl-click group sent to one province: a line per
#     corps, each its own quote (`GET /march_quotes?marshals=…`), the taken
#     lines' actions summed against the pool, and [Send N orders (Enter)]
#     [Cancel (Esc)].
#
# MODAL (dialog_manager-registered, layer 123): while it is up it takes EVERY
# key in `_input` — Enter answers, Esc cancels, and nothing else reaches the
# command line or a hotkey beneath it (a bare E would have ended the turn).
# Its buttons take no focus. It composes no order and judges no rule: every
# word on it is the backend's.
# =============================================================================

signal send_requested(command: String)
signal line_requested(command: String)
signal cancelled
# CC-5
signal standing_cancel_requested(marshal: String)
signal standing_change_requested(marshal: String)
signal group_send_requested(lines: Array, held: Array)

@onready var title_label: Label = $PanelContainer/VBox/TitleLabel
@onready var command_label: Label = $PanelContainer/VBox/CommandLabel
@onready var terms_label: RichTextLabel = $PanelContainer/VBox/TermsLabel
@onready var send_button: Button = $PanelContainer/VBox/Buttons/SendButton
@onready var line_button: Button = $PanelContainer/VBox/Buttons/LineButton
@onready var cancel_button: Button = $PanelContainer/VBox/Buttons/CancelButton

var _quote: Dictionary = {}
# CC-5: which face the card wears — "order" (CC-3), "standing" (an arrow's),
# "group" (a Ctrl-click group's).
var _mode := "order"
var _standing: Dictionary = {}       # the arrow's: {marshal, shown, info, ap_left}
var _group_plan: Dictionary = {}     # the group's: {send, held, total, ap_left, dest}
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


func _wear(mode: String) -> void:
	"""Each face's buttons."""
	_mode = mode
	line_button.visible = mode != "group"
	match mode:
		"standing":
			send_button.text = "Cancel order"
			line_button.text = "Change  (Enter)"
			cancel_button.text = "Close  (Esc)"
		"group":
			send_button.text = "Send  (Enter)"
			cancel_button.text = "Cancel  (Esc)"
		_:
			send_button.text = "Send  (Enter)"
			line_button.text = "Put in line"
			cancel_button.text = "Cancel  (Esc)"


func open_card(quote: Dictionary, title: String, reading: String, avoid: Array = []) -> void:
	"""Raise the card — on the quote when it is in hand, else on a line that
	says it is being read (`show_quote` fills it when the answer lands) —
	where it hides least of `avoid` (the road it confirms)."""
	_wear("order")
	_standing = {}
	_group_plan = {}
	title_label.text = title
	_avoid = avoid.duplicate()
	if quote.is_empty():
		_quote = {}
		command_label.text = "…"
		terms_label.text = "[color=#" + Utils.COLOR_INFO + "]" + reading + "[/color]"
		_set_buttons(false, false)
	else:
		show_quote(quote)
	_raise()


func _raise() -> void:
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


# ── CC-5: the arrow's card ─────────────────────────────────────────────────

func open_standing_card(marshal: String, shown: String, info: Dictionary, ap_left: int,
		avoid: Array = []) -> void:
	"""A standing order of ours, clicked on the map: what it is, its road
	and clock, and what cancelling it costs — [Cancel order] [Change]."""
	_wear("standing")
	_quote = {}
	_group_plan = {}
	_standing = {"marshal": marshal, "shown": shown, "info": info.duplicate(true), "ap_left": ap_left}
	_avoid = avoid.duplicate()
	title_label.text = "STANDING ORDER — " + shown.to_upper()
	command_label.text = standing_headline(shown, info)
	var cancel_ap := int(info.get("cancel_ap", 1))
	send_button.text = "Cancel order  (%s)" % ("free" if cancel_ap <= 0 else "%d AP" % cancel_ap)
	terms_label.text = _standing_terms(info, ap_left)
	send_button.disabled = ap_left < cancel_ap
	line_button.disabled = false
	cancel_button.disabled = false
	_raise()


const _THEN_DONE := {"fortify": "fortifies", "hold": "holds it", "drill": "drills", "defend": "defends it"}


static func standing_headline(shown: String, info: Dictionary) -> String:
	var dest := str(info.get("dest", ""))
	var who := str(info.get("target_shown", ""))
	# CC-4: the arrival verb (D7) and the standing contingency (D8), in the
	# backend's own words (`order_road.then` / `order_road.watch`).
	var then := str(info.get("then", ""))
	var watch := str(info.get("watch", ""))
	match str(info.get("kind", "")):
		"march":
			return shown + " marches to " + dest + ((", then " + str(_THEN_DONE.get(then, then))) if then != "" else "")
		"pursue":
			return shown + " pursues " + who
		"hold":
			return shown + " holds " + dest + ((" — " + watch) if watch != "" else "")
		"support":
			return shown + " supports " + who
		"follow":
			return shown + " follows " + who
	return shown


func _standing_terms(info: Dictionary, ap_left: int) -> String:
	var lines := PackedStringArray()
	var road = info.get("road", [])
	var turns := int(info.get("turns", 0))
	if bool(info.get("halted", false)):
		lines.append("[color=#" + Utils.COLOR_WARNING + "]Halted — he awaits your word on the road.[/color]")
	elif road is Array and not road.is_empty():
		var clock := "arrives next turn" if turns == 1 else ("arrives in " + Utils.plural(turns, "turn"))
		if str(info.get("kind", "")) == "pursue":
			clock = "closes next turn" if turns == 1 else (Utils.plural(turns, "turn") + " behind him")
		lines.append("[b]" + clock + "[/b]")
		lines.append("[color=#" + Utils.COLOR_INFO + "]Road: " + " → ".join(PackedStringArray(road)) + "[/color]")
	elif str(info.get("kind", "")) == "hold" and int(info.get("holds_for", 0)) > 0:
		lines.append("[b]holds " + Utils.plural(int(info.get("holds_for", 0)), "more turn") + "[/b]")
	var cancel_ap := int(info.get("cancel_ap", 1))
	var trust := int(info.get("cancel_trust", 0))
	var price := "Cancelling costs " + ("nothing" if cancel_ap <= 0 else Utils.plural(cancel_ap, "action"))
	if trust < 0:
		price += " and %d trust — he is already on the road" % -trust
	else:
		price += " — no trust lost: it was given this turn"
	lines.append("[color=#" + Utils.COLOR_GOLD + "]" + price + ".[/color]")
	if ap_left < cancel_ap:
		lines.append("[color=#" + Utils.COLOR_ERROR + "]No action left to cancel it today.[/color]")
	lines.append("[color=#" + Utils.COLOR_INFO + "]Change selects him: click where he should go instead.[/color]")
	return "\n".join(lines)


func standing_marshal() -> String:
	return str(_standing.get("marshal", "")) if _mode == "standing" else ""


# ── CC-5: the group's card ─────────────────────────────────────────────────

func open_group_card(title: String, dest: String, reading: String, avoid: Array = []) -> void:
	"""A Ctrl-click group sent to `dest` — raised while its quotes are read;
	`show_group` fills it."""
	_wear("group")
	_quote = {}
	_standing = {}
	_group_plan = {"dest": dest, "send": [], "held": [], "total": 0, "ap_left": 0}
	_avoid = avoid.duplicate()
	title_label.text = title
	command_label.text = "March to " + dest
	terms_label.text = "[color=#" + Utils.COLOR_INFO + "]" + reading + "[/color]"
	send_button.disabled = true
	cancel_button.disabled = false
	_raise()


static func group_plan(quotes: Array, ap_left: int) -> Dictionary:
	"""Which lines go: each corps' own quote, in the group's order — a taken
	line goes while the pool can pay it; a refused line, a man already
	there or already on that march, and a line the pool cannot pay stay
	(named). The sum is the taken lines' own prices."""
	var send: Array = []
	var held: Array = []
	var total := 0
	var left := ap_left
	for q in quotes:
		if not (q is Dictionary):
			continue
		var shown := str(q.get("shown", q.get("marshal", "")))
		if not bool(q.get("ok", false)):
			held.append({"shown": shown, "reason": str(q.get("refusal", "the order cannot be given"))})
		elif bool(q.get("already", false)):
			held.append({"shown": shown, "reason": "already on that march"})
		elif int(q.get("ap", 0)) > left:
			held.append({"shown": shown, "reason": "the pool is spent before him (needs %s)"
				% Utils.plural(int(q.get("ap", 0)), "action")})
		else:
			send.append({"marshal": str(q.get("marshal", "")), "shown": shown,
				"command": str(q.get("command", "")), "ap": int(q.get("ap", 0))})
			total += int(q.get("ap", 0))
			left -= int(q.get("ap", 0))
	return {"send": send, "held": held, "total": total, "ap_left": ap_left}


func show_group(quotes: Array, ap_left: int) -> void:
	var plan := group_plan(quotes, ap_left)
	plan["dest"] = str(_group_plan.get("dest", ""))
	_group_plan = plan
	var lines := PackedStringArray()
	for q in quotes:
		if not (q is Dictionary):
			continue
		var shown := str(q.get("shown", q.get("marshal", "")))
		if not bool(q.get("ok", false)):
			lines.append("[color=#" + Utils.COLOR_ERROR + "]" + shown + " — refused: "
				+ str(q.get("refusal", "")) + "[/color]")
			continue
		if bool(q.get("already", false)):
			lines.append(shown + " — already on that march")
			continue
		var row := "[b]" + shown + "[/b] · " + _price(int(q.get("ap", 0))) + " · " + _clock(q)
		if str(q.get("objection", "none")) == "possible":
			row += " · [color=#" + Utils.COLOR_WARNING + "]he may object[/color]"
		lines.append(row)
		var contact := str(q.get("contact", ""))
		if contact != "":
			lines.append("   [color=#" + Utils.COLOR_WARNING + "]" + contact + "[/color]")
	var send: Array = plan["send"]
	var sum_line := "[b]" + Utils.plural(int(plan["total"]), "action") + " of " + str(ap_left) + " in hand[/b]"
	if send.is_empty():
		sum_line += " — no order can go."
	else:
		sum_line += " — " + Utils.plural(send.size(), "order") + " go, corps by corps"
		var stays := PackedStringArray()
		for h in plan["held"]:
			stays.append(str(h["shown"]))
		sum_line += ("; " + ", ".join(stays) + " stay" + ("s" if stays.size() == 1 else "") + ".") if not stays.is_empty() else "."
	lines.append("")
	lines.append("[color=#" + Utils.COLOR_GOLD + "]" + sum_line + "[/color]")
	lines.append("[color=#" + Utils.COLOR_INFO + "]Send stops at the first question or refusal and says how far it got.[/color]")
	terms_label.text = "\n".join(lines)
	send_button.text = ("Send %s  (Enter)" % Utils.plural(send.size(), "order")) if not send.is_empty() else "Nothing to send"
	send_button.disabled = send.is_empty()
	if visible:
		refit.call_deferred()


func group_lines() -> Array:
	"""The lines Send would carry, in order — read by the CC harness."""
	return (_group_plan.get("send", []) as Array).duplicate(true) if _mode == "group" else []


func mode() -> String:
	return _mode


# ── the card's place ───────────────────────────────────────────────────────

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
	_standing = {}
	_group_plan = {}
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
			if _mode == "standing":
				_on_line()        # the arrow card's Enter is Change — never the cancel
			elif not send_button.disabled:
				_on_send()
			else:
				_on_cancel()   # a refused order's Enter only closes the card
		KEY_ESCAPE:
			_on_cancel()


func _on_send() -> void:
	if send_button.disabled:
		return
	match _mode:
		"standing":
			var who := standing_marshal()
			_close_quietly()
			standing_cancel_requested.emit(who)
			return
		"group":
			var lines := group_lines()
			var held: Array = (_group_plan.get("held", []) as Array).duplicate(true)
			if lines.is_empty():
				return
			_close_quietly()
			group_send_requested.emit(lines, held)
			return
	var cmd := command()
	if cmd == "":
		return
	_close_quietly()   # the quill answers a sent order, not the "back" tap
	send_requested.emit(cmd)


func _on_line() -> void:
	if _mode == "standing":
		var who := standing_marshal()
		_close_quietly()
		standing_change_requested.emit(who)
		return
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
	_standing = {}
	_group_plan = {}
	close_popup()
	cancelled.emit()
