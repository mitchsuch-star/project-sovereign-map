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
# Row IC, Session 2 (IC-7): the ONE table of the simple orders that had no button.
const SimpleOrders = preload("res://scripts/simple_orders.gd")

signal verb_pressed(verb: String, marshal: String)
signal cancel_order_pressed(marshal: String)
signal close_pressed
signal take_pressed(marshal: String)   # row PW: "Take <province>" where he stands

signal group_verb_pressed(verb: String)   # row IC, directives: "hold", "fortify" or "drill"
# Row IC, Session 2: "Give him a task…" (the host asks the staff for ready
# sentences) and a ready sentence chosen (the host writes it on the command line).
signal task_pressed(marshal: String)
signal task_line_pressed(line: String)
# Row IC, Session 3: a man ON HIS OWN — a line written on the command line
# (Ask him, Change his task) or sent at once (Carry on, Stand him down).
signal own_write_pressed(line: String)
signal own_send_pressed(line: String)
signal name_army_pressed
signal army_task_pressed(name: String)   # row IC, Session 3b: "Give it a task…"
signal save_army_pressed(name: String)
signal disband_army_pressed(name: String)

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
var _army_name := ""            # row IC, directives: the army the group came from ("" = none)
var _army_same := false
var _group_button_texts: Array = []
var _specs: Array = []
var _buttons: Dictionary = {}   # slot (int) -> Button
var _posture_open := false      # row IC, Session 2: the "Posture…" menu is showing
var _tasks: Array = []          # … and the ready tasks the staff wrote for him
var _tasks_for := ""
var _own_now := false           # row IC, Session 3: the man shown is on his own
var _hint_height := 0.0         # the hint's measured height: an opened menu stands in its place
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
	if marshal != _marshal:
		_posture_open = false
	# (the review, C4) ready tasks are for the board they were written on:
	# another man, or an action spent since, lets them go
	if marshal != _tasks_for or actions_left != _actions_left:
		_tasks = []
		_tasks_for = ""
	_marshal = marshal
	_view = view.duplicate(true)
	_actions_left = actions_left
	_hint = hint_bbcode
	_group = []
	_render()
	show()


func show_tasks(marshal: String, presets: Array) -> void:
	"""Row IC, Session 2 (IC-8): the ready tasks the staff wrote for `marshal`
	(GET /task_presets) - a button each under his orders; pressing one writes
	its sentence on the command line. Ignored if the card has moved on."""
	if marshal == "" or marshal != _marshal or not _group.is_empty():
		return
	_tasks = presets.duplicate(true)
	_tasks_for = marshal
	_posture_open = false   # one menu at a time: it stands in the hint's place
	_render()


func show_group(names: Array, total_ap: int, in_hand: int, hint_bbcode: String) -> void:
	"""The group face: who marches together and what it costs - no verb buttons."""
	_marshal = ""
	_view = {}
	_tasks = []
	_tasks_for = ""
	_posture_open = false
	_group = names.duplicate()
	_group_total = total_ap
	_group_in_hand = in_hand
	_army_name = ""   # row IC: main names the army right after, via set_group_army
	_army_same = false
	_hint = hint_bbcode
	_render()
	show()


func hide_card() -> void:
	_marshal = ""
	_view = {}
	_tasks = []
	_tasks_for = ""
	_posture_open = false
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
	var menu: Control = null
	if _group.is_empty():
		_body.add_child(_head_row(compact))
		_own_now = str(_dict_of_view_own().get("task", "")) != ""
		# Row IC, Session 2b: on a task to prove himself his card carries NO
		# order at all — what he is doing, his task as it was given, and that
		# he cannot be called back. (The first blind reading: the card said "he
		# takes no orders" above eleven greyed order buttons, "Cancel order"
		# among them; all three readers answered right and all three said they
		# could not tell whether the buttons still worked.)
		var proving := _trial_row(compact)
		if proving != null:
			_body.add_child(proving)
			_body.add_child(_hint_label(compact))
			reset_size()
			return
		_specs = MarshalStateKit.order_specs(_view)
		var ground := _ground_row(compact)
		if ground != null:
			_body.add_child(ground)
		# Row IC, Session 3: ON HIS OWN — his task, "Tonight", what he asks,
		# and the four click twins of typed lines. He still takes today's
		# orders (§6.3), so his order rows stand below as for any man.
		var own_row := _own_row(compact)
		if own_row != null:
			_body.add_child(own_row)
		# Row IC, Session 3b: a man who FOLLOWS an army's commander — whom, and
		# what he does tonight. He takes today's orders as any man does.
		var follows_row := _follows_row(compact)
		if follows_row != null:
			_body.add_child(follows_row)
		# Row IC, Session 2 (pressed in the real client at the first player's
		# setup): the card stands on its bottom edge, so whatever makes it taller
		# lifts every row above the new one out from under the cursor - with the
		# menus added at the foot, "Posture" itself moved 84 px up as it was
		# pressed, and a ready task slid under the cursor that had pressed "Give
		# him a task…". So nothing that was pressed ever moves:
		#   the READY TASKS stand above his orders (only his name is lifted);
		#   the POSTURE menu stands in the hint's place, at least as tall as it.
		# One of the two at a time (`_toggle_posture`, `show_tasks`).
		if not _posture_open and not _tasks.is_empty() and _tasks_for == _marshal:
			_body.add_child(_task_rows(compact))
		_body.add_child(_order_row(compact))
		_body.add_child(_simple_row(compact))
		if _posture_open:
			menu = _posture_row(compact)
	else:
		_body.add_child(_group_row(compact))
	if menu != null:
		menu.custom_minimum_size.y = maxf(menu.custom_minimum_size.y, _hint_height)
		_body.add_child(menu)
	else:
		_body.add_child(_hint_label(compact))
	reset_size()


func _ground_row(compact: bool) -> Control:
	"""Row PW (the first playtest: "i had 3 people in colinia and no one could
	take it"): he stands on a province that is not ours — the board's
	`stands_on`. Where an order would take it, that order is a button here
	("Take Carniola", "Storm Vienna"); where none would, the reason is said in
	one line. Null on our own ground."""
	var stands = _view.get("stands_on", {})
	if not (stands is Dictionary) or (stands as Dictionary).is_empty():
		return null
	var place := str(_view.get("stands_at", ""))
	var line := str(stands.get("line", "")).strip_edges()
	var row := VBoxContainer.new()
	row.name = "GroundRow"
	row.add_theme_constant_override("separation", 3)
	var wrap_w: float = maxf(_card_width(compact) - 24.0, 120.0)
	if bool(stands.get("ok", false)) and str(stands.get("command", "")) != "":
		var btn := Button.new()
		btn.name = "TakeButton"
		btn.text = str(stands.get("label", "Take it"))
		btn.focus_mode = Control.FOCUS_NONE
		btn.custom_minimum_size = Vector2(0, 34)
		btn.tooltip_text = Utils.clean_tip(
			(place + ": " if place != "" else "") + line + " — one action.")
		btn.theme_type_variation = &"PrimaryButton"   # the one gilt act on the card
		btn.pressed.connect(func(): take_pressed.emit(_marshal))
		row.add_child(btn)
	if line != "":
		var words := ("[color=#" + Utils.COLOR_WARNING + "]" + (place + " is not ours: " if place != "" else "")
			+ line + ".[/color]")
		if str(stands.get("refusal", "")) != "":
			words += " [color=#" + Utils.COLOR_INFO + "](" + str(stands.get("refusal", "")) + ")[/color]"
		row.add_child(_measured_rich("GroundLine", words, wrap_w, true))
	return row


func _trial_row(compact: bool) -> Control:
	"""Row IC, Session 2b: he is on a TASK TO PROVE HIMSELF — the server's own
	words for how long it runs ("On a task to prove himself — 2 turns left"),
	the task as it was given, and that he takes no orders and cannot be called
	back. It stands where his orders would (`_render`). Null for every other man."""
	var trial = _view.get("trial", {})
	if not (trial is Dictionary) or (trial as Dictionary).is_empty():
		return null
	var wrap_w: float = maxf(_card_width(compact) - 24.0, 120.0)
	var status := str(trial.get("status", "")).strip_edges()
	if status == "":
		status = "On a task to prove himself"
	var words := "[color=#" + Utils.COLOR_WARNING + "]" + status + ".[/color]"
	var line := str(trial.get("line", "")).strip_edges()
	if line != "":
		words += "\n[color=#" + Utils.COLOR_INFO + "]His task: \"" + line + "\"[/color]"
	words += "\n[color=#" + Utils.COLOR_INFO + "]He takes no orders until it ends, and you cannot call him back.[/color]"
	return _measured_rich("TrialLine", words, wrap_w, true)


func _own_row(compact: bool) -> Control:
	"""Row IC, Session 3: he is ON HIS OWN — the server's own words for his
	task, what he did as this turn opened (Session 4b: never a preview), what
	he asks of you, his odds — and four buttons, each the click twin of a typed
	line: "Ask him" and "Change his task…" WRITE the line (asking is free and
	his answer shows before Enter; a change costs 1 action), "Carry on" (when
	he asks) and "Stand him down" SEND it (both free). Null for every other man."""
	var own = _view.get("own", {})
	if not (own is Dictionary) or str((own as Dictionary).get("task", "")) == "":
		return null
	var col := VBoxContainer.new()
	col.name = "OwnRow"
	col.add_theme_constant_override("separation", 4)
	var wrap_w: float = maxf(_card_width(compact) - 24.0, 120.0)
	var shown := Utils.humanize_entity_name(_marshal)
	var task_words := str(own.get("words", ""))
	var words := "[color=#" + Utils.COLOR_GOLD + "]On his own: " + task_words + "[/color]"
	# Row IC, Session 4b — what he did as this turn opened; read first, so the
	# state's own words are not said twice (pressed in the real client: "(makes
	# his first move at the start of next turn)" stood right above the same
	# sentence on its own line)
	var done := str(own.get("this_turn", "")).strip_edges().trim_suffix(".")
	var first_next := done == "" and bool(own.get("first_move_next", false))
	var state_words := str(own.get("state_words", ""))
	if state_words != "" and not first_next:
		words += "  [color=#" + Utils.COLOR_INFO + "](" + state_words + ")[/color]"
	# Row IC, Session 3b: the army he commands, and who follows him; the war
	# goal his task serves.
	# ONE line for both (pressed in the real client at the first player's
	# setup: two more lines pushed his last row of orders 11 px past the
	# screen's foot — the card stands on its bottom edge). Who follows him is
	# named on the army's chip and on the desk's line.
	var army := str(own.get("army", ""))
	var serves := bool(own.get("goal", false))
	if army != "":
		var followers = own.get("followers", [])
		var n: int = (followers as Array).size() if followers is Array else 0
		var men := "nobody follows yet" if n == 0 else ("1 man follows" if n == 1 else (str(n) + " men follow"))
		words += "\n[color=#" + Utils.COLOR_GOLD + "]Commands the " + army + "[/color]"
		if serves:
			words += " (" + men + ") · serves your war goal."
		else:
			words += " — " + men + (" him." if n > 0 else ".")
	elif serves:
		words += ("\n[color=#" + Utils.COLOR_GOLD + "]Serves your war goal[/color] — a new goal turns him (1 action).")
	# Row IC, Session 4b — the user's "He moves at turn start": what he DID as
	# this turn opened, never what he will do (no preview).
	if done != "":
		words += "\n[color=#" + Utils.COLOR_COMMAND + "]This turn:[/color] " + done + "."
	elif first_next:
		words += "\n[color=#" + Utils.COLOR_COMMAND + "]He makes his first move at the start of next turn.[/color]"
	var help := str(own.get("help", "")).strip_edges()
	if help != "":
		words += "\n[color=#" + Utils.COLOR_COMMAND + "]Every turn:[/color] " + help + "."
	var asks := str(own.get("asks", "")).strip_edges()
	if asks != "":
		if bool(own.get("carries_on", false)):
			words += "\n[color=#" + Utils.COLOR_WARNING + "]He asks for your word: " + asks + ". He carries on meanwhile.[/color]"
		else:
			words += "\n[color=#" + Utils.COLOR_WARNING + "]He asks for your word: " + asks + ".[/color]"
	if not compact:
		words += "\n[color=#" + Utils.COLOR_INFO + "]"
		words += ("He attacks only when the odds are " + str(own.get("odds", ""))
			+ " (men of ours to theirs, as the battle forecast reckons them). ")
		# (pressed in the real client: a man set on his own with NO task read
		# "Your task guides him")
		if str(own.get("task", "")) == "free":
			words += "No task: each turn he weighs the chances around him and makes war as he sees fit; a task you give later guides him. "
		else:
			words += "Your task guides him: each turn he weighs it against the chances around him. "
		words += "An order you give him by hand is carried out at its usual price.[/color]"
	col.add_child(_measured_rich("OwnLine", words, wrap_w, true))
	var flow := HFlowContainer.new()
	flow.name = "OwnButtons"
	flow.add_theme_constant_override("h_separation", 4)
	flow.add_theme_constant_override("v_separation", 4)
	flow.add_child(_simple_button("Own_ask", "Ask him",
		"Writes \"" + shown + ", what will you do?\" on the command line. Asking is free; his answer shows before you press Enter.",
		"", _emit_own_write.bind(shown + ", what will you do?")))
	flow.add_child(_simple_button("Own_change", "Change his task…",
		"Writes his task on the command line for you to change (more risk, less risk, another place). A change costs 1 action.",
		"", _emit_own_write.bind(shown + ", " + task_words + " on your own.")))
	if asks != "":
		var carry := _simple_button("Own_carry", "Carry on · free",
			"Tells him to carry on with his task. Free.", "",
			_emit_own_send.bind(shown + ", carry on"))
		carry.theme_type_variation = &"PrimaryButton"
		flow.add_child(carry)
	var price := str(own.get("stand_down", "free"))
	flow.add_child(_simple_button("Own_stand", "Stand him down · " + price.split(",")[0],
		"Ends his task on his own: " + price + ".", "",
		_emit_own_send.bind(shown + ", stand down")))
	col.add_child(flow)
	return col


func _follows_row(compact: bool) -> Control:
	"""Row IC, Session 3b: he FOLLOWS the commander of an army's task — whom,
	for which army and task, and what he did as this turn opened (Session 4b:
	he moves right after his commander at the turn's start). Null for every
	other man."""
	var follows = _view.get("follows", {})
	if not (follows is Dictionary) or str((follows as Dictionary).get("lead", "")) == "":
		return null
	var wrap_w: float = maxf(_card_width(compact) - 24.0, 120.0)
	var lead := str(follows.get("lead_shown", follows.get("lead", "")))
	var words := ("[color=#" + Utils.COLOR_GOLD + "]Follows " + lead + "[/color] — the " + str(follows.get("army", ""))
		+ " is on its own: " + str(follows.get("task", "")) + ".")
	var done := str(follows.get("this_turn", "")).strip_edges().trim_suffix(".")
	if done != "":
		words += "\n[color=#" + Utils.COLOR_COMMAND + "]This turn:[/color] " + done + "."
	elif bool(follows.get("first_move_next", false)):
		words += "\n[color=#" + Utils.COLOR_COMMAND + "]He moves with " + lead + " from the start of next turn.[/color]"
	if not compact:
		var odds := int(follows.get("odds", 0))
		words += ("\n[color=#" + Utils.COLOR_INFO + "]He moves with " + lead + " at the start of each turn, and may"
			+ " join " + lead + "'s battles next to him" + ((" (about " + str(odds) + " times in 100)") if odds > 0 else "")
			+ ". He takes none of your places for men on their own. An order you give him by hand is carried out;"
			+ " he follows again at the start of next turn.[/color]")
	return _measured_rich("FollowsLine", words, wrap_w, true)


func _dict_of_view_own() -> Dictionary:
	var own = _view.get("own", {})
	return own if own is Dictionary else {}


func _emit_own_write(line: String) -> void:
	AudioManager.play("click")
	own_write_pressed.emit(line)


func _emit_own_send(line: String) -> void:
	AudioManager.play("click")
	own_send_pressed.emit(line)


func _no_orders_reason() -> String:
	"""Row IC, Session 2b: the server's short reason why he takes no orders
	while he is on his task to prove himself, or "" for every other man."""
	var trial = _view.get("trial", {})
	if not (trial is Dictionary) or (trial as Dictionary).is_empty():
		return ""
	return str(trial.get("reason", "on his task to prove himself"))


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
	col.add_child(_measured_rich("Figures", _figures_bbcode(compact), 0.0))
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
	if str(label.name) == "Hint":
		_hint_height = label.custom_minimum_size.y   # what an opened menu fills (`_render`)
	reset_size()


func _figures_bbcode(compact: bool = false) -> String:
	var parts := PackedStringArray()
	parts.append(Utils.bb_glyph("strength", 16) + " " + Utils.format_number(int(_view.get("strength", 0))))
	if _view.has("morale"):
		parts.append(Utils.bb_glyph("morale", 16) + " " + str(int(_view.get("morale", 0))) + "%")
	# Row PW part 2 (three blind readers of three: "the icon is not labelled
	# actions"): the figure says what it counts. The short view keeps its room.
	# Row IC, Session 2b (the blind reading, three of three: "4 actions left"
	# on the card of a man who takes no orders — "what can they be spent on?"):
	# the Emperor's pool is not shown on the card of a man on his task.
	if not _no_orders_reason().is_empty():
		return "   ".join(parts)
	var left := (str(_actions_left) + " left") if compact else (Utils.plural(_actions_left, "action") + " left")
	parts.append(Utils.bb_glyph("actions", 16) + " " + left)
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
	var label := str(spec.get("card_label", spec["label"]))
	btn.name = "Slot" + str(slot)
	btn.focus_mode = Control.FOCUS_NONE
	btn.mouse_filter = Control.MOUSE_FILTER_STOP
	# Row PW part 3: the price in words on the face — "1 Hold · 1 action", "5
	# Fall back · free" (it read "1 Hold · 1": two bare numbers, the key and the
	# price, which four readers of four parsed only by inference).
	var tail := price
	if price != "" and price != "free":
		tail = Utils.plural(int(spec["price"]), "action")
	var full := label + (" · " + tail if tail != "" else "")
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
		# Row PW part 2 (four blind readers of four read "1 Hold · 2" right, and
		# only by inference — its two numbers are never labelled): the hover
		# says them in words. The face keeps its room.
		tip = slot_words(label, int(spec["price"]), slot)
	var locked := bool(spec["locked"])
	btn.disabled = locked
	var reason := str(spec["reason"])
	if locked:
		if reason != "":
			tip = (tip + " - " + reason) if tip != "" else reason
	btn.tooltip_text = tip
	btn.pressed.connect(_fire.bind(spec))
	return btn


static func slot_words(label: String, price: int, slot: int) -> String:
	"""A slot's two numbers in words: "Hold — costs 2 actions · key 1",
	"Fall back — free · key 5", "Cancel order · key 7" (no price named)."""
	var out := label
	if price == 0:
		out += " — free"
	elif price > 0:
		out += " — costs " + Utils.plural(price, "action")
	return out + " · key " + str(slot)


func _fire(spec: Dictionary) -> void:
	AudioManager.play("click")
	_put_menus_away()
	var verb := str(spec["verb"])
	if verb == "cancel":
		cancel_order_pressed.emit(_marshal)
	else:
		verb_pressed.emit(verb, _marshal)


# ------------------------------------------- row IC, Session 2: simple orders

func _simple_row(compact: bool) -> Control:
	"""The simple orders that had no button, under the seven slots: "Stand
	here", "Stay put", "Posture…" and "Give him a task…" - the table's `card`
	rows (simple_orders.gd). No digit: the slots keep 1 to 7."""
	var flow := HFlowContainer.new()
	flow.name = "SimpleRow"
	flow.add_theme_constant_override("h_separation", 4)
	flow.add_theme_constant_override("v_separation", 4)
	for entry in SimpleOrders.rows("card"):
		var id := str(entry["id"])
		if id == "posture":
			var mark := " ▾" if not _posture_open else " ▴"
			flow.add_child(_simple_button("Simple_posture", _posture_face() + mark,
				str(entry["tip"]), "", _toggle_posture))
		elif id == "task":
			# Row IC, Session 3 (the blind reading: "Give him a task…" beside
			# "Change his task…" read as two roads): a man on his own changes
			# his task from his own block.
			if not _own_now:
				flow.add_child(_simple_button("Simple_task", str(entry["label"]),
					str(entry["tip"]), "", _emit_task))
		elif id == "own_free":
			# Row IC, Session 4b: on his own with no task — only for a man who
			# may ever be set so (the server prices it then), never once he is.
			var offered = (_view.get("buttons", {}) as Dictionary).get("offered", {}) \
				if _view.get("buttons", {}) is Dictionary else {}
			if not _own_now and offered is Dictionary and bool((offered as Dictionary).get("own_free", false)):
				flow.add_child(_order_button(entry, compact))
		else:
			flow.add_child(_order_button(entry, compact))
	return flow


func _posture_row(_compact: bool) -> Control:
	"""The "Posture…" menu: attacking, steady, defending - each with its price
	- and the square. The game's own reason greys what he cannot take."""
	var flow := HFlowContainer.new()
	flow.name = "PostureRow"
	flow.add_theme_constant_override("h_separation", 4)
	flow.add_theme_constant_override("v_separation", 4)
	for entry in SimpleOrders.rows("posture"):
		var id := str(entry["id"])
		# one of the two square buttons: the one that applies
		if id == "form_square" and bool(_view.get("square", false)):
			continue
		if id == "break_square" and not bool(_view.get("square", false)):
			continue
		flow.add_child(_order_button(entry, false))
	return flow


func _posture_face() -> String:
	"""The posture he is in, on the menu's own face: "Posture: steady"."""
	var words := {"aggressive": "attacking", "neutral": "steady", "defensive": "defending"}
	var stance := str(_view.get("stance", ""))
	if words.has(stance):
		return "Posture: " + str(words[stance])
	return "Posture"


func _order_button(entry: Dictionary, _compact: bool) -> Button:
	"""One row of the table as a button: its words and its price on the face,
	greyed with the game's own reason where the order would be refused."""
	var price := SimpleOrders.price_of(entry, _view)
	var reason := SimpleOrders.refusal_of(entry, _view)
	var tip := str(entry.get("tip", ""))
	var btn := _simple_button("Simple_" + str(entry["id"]),
		SimpleOrders.face(str(entry["label"]), price), tip, reason,
		_fire_line.bind(str(entry["line"])))
	return btn


func _simple_button(node_name: String, face: String, tip: String, reason: String,
		on_press: Callable) -> Button:
	var btn := Button.new()
	btn.name = node_name
	btn.focus_mode = Control.FOCUS_NONE
	btn.mouse_filter = Control.MOUSE_FILTER_STOP
	btn.text = face
	btn.disabled = reason != ""
	if reason != "":
		tip = (tip + " - " + reason) if tip != "" else reason
	btn.tooltip_text = Utils.clean_tip(tip)
	btn.pressed.connect(on_press)
	return btn


func _task_rows(compact: bool) -> Control:
	"""The staff's ready tasks for him, a button each: its short words and its
	price. Pressing one WRITES its sentence on the command line - nothing is
	sent."""
	var col := VBoxContainer.new()
	col.name = "TaskRows"
	col.add_theme_constant_override("separation", 3)
	var wrap_w: float = maxf(_card_width(compact) - 24.0, 120.0)
	col.add_child(_measured_rich("TaskHead",
		"[color=#" + Utils.COLOR_INFO + "]Ready tasks - a press writes the sentence on the command line; change it or press Enter.[/color]",
		wrap_w, true))
	var index := 0
	for preset in _tasks:
		if not (preset is Dictionary):
			continue
		var line := str((preset as Dictionary).get("line", ""))
		if line == "":
			continue
		var words := str((preset as Dictionary).get("label", line))
		var price := str((preset as Dictionary).get("price", ""))
		# Row IC, Session 4 (IC-13): the task that is HIS idea carries his own
		# line on its hover - `Ney: "..."` under the sentence it writes.
		var tip := line
		var said := str((preset as Dictionary).get("says", ""))
		if said != "":
			tip += "
" + VoiceLine.plain_text(str((preset as Dictionary).get("speaker", _marshal)), said)
		var btn := _simple_button("Task" + str(index), words + (" · " + price if price != "" else ""),
			tip, "", _emit_task_line.bind(line))
		btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
		# (the review, C2) a long task wraps inside the card - it never widens it
		btn.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		btn.clip_text = false
		btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		col.add_child(btn)
		index += 1
	return col


func simple_buttons() -> Array:
	"""The faces of the simple-order buttons now on the card, in order (a test
	reader): the second row, then the posture menu and the ready tasks when open."""
	var out: Array = []
	if _body == null:
		return out
	for row_name in ["SimpleRow", "PostureRow", "TaskRows"]:
		var row := _body.get_node_or_null(row_name)
		if row == null:
			continue
		for child in row.get_children():
			if child is Button:
				out.append({"name": str(child.name), "text": (child as Button).text,
					"disabled": (child as Button).disabled, "tip": (child as Button).tooltip_text})
	return out


func press_simple(node_name: String) -> bool:
	"""Press a simple-order button by its node name (a test hand). False when
	it is missing or greyed."""
	if _body == null:
		return false
	for row_name in ["SimpleRow", "PostureRow", "TaskRows"]:
		var row := _body.get_node_or_null(row_name)
		if row == null:
			continue
		var btn := row.get_node_or_null(node_name)
		if btn is Button:
			if (btn as Button).disabled:
				return false
			(btn as Button).pressed.emit()
			return true
	return false


func _fire_line(line: String) -> void:
	if line == "" or _marshal == "":
		return
	AudioManager.play("click")
	_put_menus_away()
	verb_pressed.emit(line, _marshal)


func _put_menus_away() -> void:
	"""An order given from the card puts its menus away (the second look: a FREE
	order - a fall back, a cancel - leaves his actions as they were, so the ready
	tasks written for the board before it stayed above his orders)."""
	_posture_open = false
	_tasks = []
	_tasks_for = ""


func _toggle_posture() -> void:
	AudioManager.play("click")
	_posture_open = not _posture_open
	if _posture_open:
		_tasks = []   # one menu at a time
		_tasks_for = ""
	_render()


func _emit_task() -> void:
	AudioManager.play("click")
	if not _tasks.is_empty() and _tasks_for == _marshal:
		# a second press puts the ready tasks away (the hint returns)
		_tasks = []
		_tasks_for = ""
		_render()
		return
	task_pressed.emit(_marshal)


func _emit_task_line(line: String) -> void:
	AudioManager.play("click")
	task_line_pressed.emit(line)


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
	# Row IC, directives (pressed in the real client): a group that is exactly an
	# army is titled by it — the chip lit beside the marshals named it, the card
	# did not.
	var heading := ", ".join(shown)
	if _army_name != "" and _army_same:
		heading = "The " + _army_name + " — " + heading
	var names_label := _title(heading)
	names_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	names_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	names_label.custom_minimum_size = Vector2(80.0, 0.0)
	top.add_child(names_label)
	top.add_child(_close_button())
	# Row IC, directives: "up to" — a province next door is each man's one-action
	# move (the click road's rule since row PW), so a march's price is the most.
	# In plain words since the directives' blind reading 1, where all three
	# readers could not read "march together · up to 4 of 4 actions in hand".
	var line := ("sending them costs up to " + Utils.plural(_group_total, "action")
		+ " · you have " + str(_group_in_hand))
	if _group_total > _group_in_hand:
		line = "[color=#" + Utils.COLOR_WARNING + "]" + line + "[/color]"
	col.add_child(_measured_rich("GroupSum", Utils.bb_glyph("actions", 16) + " " + line, 0.0, true))
	# Row IC, directives: the group's orders and its army (the buttons are built
	# by helpers below, so this body holds none itself).
	col.add_child(_group_buttons_row(compact))
	return col


# Row IC, directives: the group face's orders and army buttons. Each order opens
# ONE list of every corps' order and price first; nothing is spent until "Give".
func set_group_army(army_name: String, same: bool) -> void:
	"""Main calls this right after show_group. "" = a plain group (offer to name
	it); a name and same = exactly that army in the field (offer to disband it);
	a name and not same = picked from an army, then changed (offer to save over
	it, or to name a new one)."""
	_army_name = army_name
	_army_same = same
	if not _group.is_empty() and visible:
		_render()


func group_buttons() -> Array:
	"""The texts of the group face's buttons, in order (a test reader)."""
	return _group_button_texts.duplicate()


func _group_buttons_row(compact: bool) -> Control:
	var flow := HFlowContainer.new()
	flow.name = "GroupButtons"
	flow.add_theme_constant_override("h_separation", 4)
	flow.add_theme_constant_override("v_separation", 4)
	_group_button_texts = []
	var order_tip := "Shows the list of each corps' order and its price first — nothing is spent until you press Give."
	for verb in ["hold", "fortify", "drill"]:
		var word := str(verb).capitalize()
		_add_group_button(flow, "Group" + word, word + "…", order_tip, compact,
			_emit_group_verb.bind(str(verb)))
	# Row IC, Session 2 (IC-7): the group's attack, support, fall back and
	# garrison - the table's `group` rows (simple_orders.gd).
	for entry in SimpleOrders.rows("group"):
		_add_group_button(flow, "Group" + str(entry["verb"]).capitalize(), str(entry["label"]),
			str(entry["tip"]), compact, _emit_group_verb.bind(str(entry["verb"])))
	if _army_name == "":
		_add_group_button(flow, "NameArmy", "Name this army…",
			"Gives these corps a name, so one chip or one line (“Army of Italy, hold”) orders them all again. Free.",
			compact, _emit_name_army)
	elif _army_same:
		# Row IC, Session 3b: an army's TASK — its commander on his own, the
		# rest following him. The button writes a ready sentence on the line.
		_add_group_button(flow, "ArmyTask", "Give it a task…",
			"Writes a task for the " + _army_name + " on the command line (“" + _army_name
			+ ", take …”). Its commander is set on his own and the others follow him. "
			+ "You see the list and its price before anything is spent.",
			compact, _emit_army_task)
		_add_group_button(flow, "DisbandArmy", "Disband the " + _army_name,
			"The " + _army_name + " is dissolved; its corps keep their orders and stand where they are. Free.",
			compact, _emit_disband)
	else:
		_add_group_button(flow, "SaveArmy", "Save as " + _army_name,
			"The " + _army_name + " becomes exactly these corps. Free.", compact, _emit_save)
		_add_group_button(flow, "NameNewArmy", "Name a new army…",
			"Gives these corps a new name, so one chip or one line orders them all again. Free.",
			compact, _emit_name_army)
	return flow


func _add_group_button(flow: Control, node_name: String, face: String, tip: String,
		compact: bool, on_press: Callable) -> void:
	var btn := Button.new()
	btn.name = node_name
	btn.focus_mode = Control.FOCUS_NONE
	btn.mouse_filter = Control.MOUSE_FILTER_STOP
	# The short view keeps its room: a short face, the full words on the hover.
	btn.text = face
	if compact:
		btn.text = _short_face(node_name, face)
		if btn.text != face:
			tip = face + " — " + tip
	btn.tooltip_text = Utils.clean_tip(tip)
	btn.pressed.connect(on_press)
	flow.add_child(btn)
	_group_button_texts.append(btn.text)


func _short_face(node_name: String, face: String) -> String:
	match node_name:
		"NameArmy", "NameNewArmy":
			return "Name…"
		"ArmyTask":
			return "Task…"
		"DisbandArmy":
			return "Disband"
		"SaveArmy":
			return "Save"
	return face


func _emit_group_verb(verb: String) -> void:
	AudioManager.play("click")
	group_verb_pressed.emit(verb)


func _emit_name_army() -> void:
	AudioManager.play("click")
	name_army_pressed.emit()


func _emit_army_task() -> void:
	AudioManager.play("click")
	army_task_pressed.emit(_army_name)


func _emit_save() -> void:
	AudioManager.play("click")
	save_army_pressed.emit(_army_name)


func _emit_disband() -> void:
	AudioManager.play("click")
	disband_army_pressed.emit(_army_name)


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
