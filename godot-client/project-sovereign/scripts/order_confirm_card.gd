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
#   * the LIST card (row IC, directives, November 19, 2026 — it replaced the
#     CC-5 group card, which sent one request a corps) — any order to SEVERAL
#     corps: a typed collective line, a list of names, a named army, a
#     Ctrl-click group sent to a province, a TO DECIDE row. One row a corps
#     with a tick, each man's order, its price, whether he may object; who
#     will not go and why; the total against the actions in hand; and
#     [Give the order (Enter)] [Cancel (Esc)]. Give is ONE request and one
#     Take-back unit; every row is the server's (`backend/commands/directive.py`).
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
# Row IC, directives: the list's Give — the line to send back, the ticked men
# in the list's order, the total the player saw, and whether the group came
# from a click on the map (each man's own plain order).
signal directive_give_requested(line: String, members: Array, expect_ap: int, click: bool)
# Row BA, BA-2: a `bring` chip on an attack's card — the order that brings a
# corps standing by, sent at once (the card closes; the lead is selected again).
signal bring_requested(command: String)
# Row PW: "Storm <province> instead" — the order that TAKES the province the
# quoted march would only enter; the host opens that order's own card.
signal take_requested(province: String)

@onready var title_label: Label = $PanelContainer/VBox/TitleLabel
@onready var command_label: Label = $PanelContainer/VBox/CommandLabel
@onready var terms_label: RichTextLabel = $PanelContainer/VBox/TermsLabel
@onready var send_button: Button = $PanelContainer/VBox/Buttons/SendButton
@onready var line_button: Button = $PanelContainer/VBox/Buttons/LineButton
@onready var cancel_button: Button = $PanelContainer/VBox/Buttons/CancelButton

var _quote: Dictionary = {}
# CC-5: which face the card wears — "order" (CC-3), "standing" (an arrow's),
# "directive" (row IC: the list of an order to several corps).
var _mode := "order"
var _standing: Dictionary = {}       # the arrow's: {marshal, shown, info, ap_left}
# The screen rects the card stands clear of (the selected corps' ring and
# ghost road, the selection's strip) — GLOBAL, logical px.
var _avoid: Array = []
const SimpleOrders = preload("res://scripts/simple_orders.gd")   # row IC, Session 2: the one table's tips
const CARD_WIDTH := 560.0
const CARD_EDGE := 12.0
# Session UI-6 (November 13, 2026): the card never takes more than this share
# of the HUD band (a narrow band — the compact view's, a docked desk's) …
const BAND_SHARE := 0.9
# … and its three buttons stay whole: under this inner width they drop their
# authored minimum widths (150 / 130 / 130) to their words' own.
const BUTTONS_AUTHORED_W := 430.0
var _button_min_w: Dictionary = {}   # button name -> its authored minimum width


func _ready():
	hide()
	send_button.pressed.connect(_on_send)
	line_button.pressed.connect(_on_line)
	cancel_button.pressed.connect(_on_cancel)
	terms_label.meta_clicked.connect(_on_terms_meta)


func _wear(mode: String) -> void:
	"""Each face's buttons."""
	_mode = mode
	if _force_box != null and is_instance_valid(_force_box):
		_force_box.visible = false
	# Row IC, directives: the list's face has no "Put in line" (Give sends the
	# ticked rows as one order) and stands its rows where the terms stand.
	var listing := mode == "directive"
	line_button.visible = not listing
	terms_label.visible = not listing
	if not listing:
		_free_directive()
	command_label.tooltip_text = ""
	match mode:
		"standing":
			send_button.text = "Cancel order"
			line_button.text = "Change  (Enter)"
			cancel_button.text = "Close  (Esc)"
		"directive":
			send_button.text = DIR_GIVE
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
	_dir = {}
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


# Session UI-5 (D8, November 12, 2026): the attack card's force bar — our
# strength (a solid bar) against the enemy's fog band (low to high, or the
# label alone when the band is unknown) and the odds word, drawn under the
# muster line. The data is the quote's `force` block; absent, no bar.
var _force_box: VBoxContainer = null
const FORCE_BAR_H := 14.0
const FORCE_LABEL_W := 56.0


func _set_force(q: Dictionary) -> void:
	if _force_box != null and is_instance_valid(_force_box):
		_force_box.get_parent().remove_child(_force_box)
		_force_box.queue_free()
		_force_box = null
	if _mode != "order" or not bool(q.get("ok", false)):
		return
	var f = q.get("force", null)
	if not (f is Dictionary) or (f as Dictionary).is_empty():
		return
	var force: Dictionary = f
	var ours: int = int(force.get("ours", 0))
	var low: int = int(force.get("theirs_low", 0))
	var high: int = maxi(int(force.get("theirs_high", 0)), low)
	var label: String = str(force.get("theirs_label", "")) if force.get("theirs_label") != null else ""
	var odds: String = str(force.get("odds", "")) if force.get("odds") != null else ""
	var scale_max: int = maxi(maxi(ours, high), 1)
	var box := VBoxContainer.new()
	box.name = "ForceBars"
	box.add_theme_constant_override("separation", 4)
	box.add_child(_force_row("Ours", Utils.format_number(ours),
			float(ours) / float(scale_max), -1.0, Utils.cv(Utils.UI_SCORE_POSITIVE), false))
	var theirs_text: String = label
	var has_band: bool = high > 0
	if has_band:
		var band_text: String = Utils.format_number(low) if low == high else Utils.format_number(low) + " – " + Utils.format_number(high)
		theirs_text = band_text if label == "" else label + " · " + band_text
		# BA5-D4: an exact sighting's label IS the figure ("39,718 men") — the
		# row read "39,718 men · 39,718". A banded sighting keeps both: its
		# label is words ("a large force") and the band is its range.
		if low == high and label == band_text + " men":
			theirs_text = label
	box.add_child(_force_row("Theirs", theirs_text,
			float(low) / float(scale_max), float(high) / float(scale_max),
			Utils.cv(Utils.UI_SCORE_NEGATIVE), not has_band))
	if odds != "":
		var odds_label := Label.new()
		odds_label.name = "OddsLabel"
		# Row PW (plain words): the band said as what to expect — the quote's
		# own `expect` ("odds bad — you will probably lose"); the bare word
		# only where an older reply carries none.
		var expect: String = str(force.get("expect", "")) if force.get("expect") != null else ""
		odds_label.text = (expect.substr(0, 1).to_upper() + expect.substr(1)) if expect != "" else "Odds: " + odds
		odds_label.theme_type_variation = &"Caption"
		odds_label.add_theme_color_override("font_color", Utils.UI_GOLD_BRIGHT)
		odds_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		box.add_child(odds_label)
	var vb: Control = terms_label.get_parent()
	vb.add_child(box)
	vb.move_child(box, terms_label.get_index() + 1)
	_force_box = box


func _force_row(who: String, value_text: String, frac_a: float, frac_b: float,
		colour: Color, label_only: bool) -> Control:
	"""One labelled meter: the name, the track (a solid bar to frac_a, a band
	to frac_b when given) and the figure; label_only draws the words alone."""
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 8)
	var name_label := Label.new()
	name_label.text = who
	name_label.theme_type_variation = &"Caption"
	name_label.add_theme_color_override("font_color", Utils.UI_TEXT_DIM)
	name_label.custom_minimum_size = Vector2(FORCE_LABEL_W, 0.0)
	row.add_child(name_label)
	if label_only:
		var words := Label.new()
		words.text = value_text
		words.theme_type_variation = &"Caption"
		words.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		words.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		words.custom_minimum_size = Vector2(40.0, 0.0)
		row.add_child(words)
		return row
	var bar := Control.new()
	bar.custom_minimum_size = Vector2(40.0, FORCE_BAR_H)
	bar.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	bar.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
	bar.set_meta("frac_a", frac_a)
	bar.set_meta("frac_b", frac_b)
	bar.set_meta("colour", colour)
	bar.draw.connect(_draw_force_bar.bind(bar.get_instance_id()))
	row.add_child(bar)
	var figure := Label.new()
	figure.text = value_text
	figure.theme_type_variation = &"Caption"
	figure.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	row.add_child(figure)
	return row


func _draw_force_bar(bar_id: int) -> void:
	var bar := instance_from_id(bar_id) as Control
	if bar == null or not is_instance_valid(bar):
		return
	var size_v: Vector2 = bar.size
	var colour: Color = bar.get_meta("colour")
	var a: float = clampf(float(bar.get_meta("frac_a")), 0.0, 1.0)
	var b: float = float(bar.get_meta("frac_b"))
	bar.draw_rect(Rect2(Vector2.ZERO, size_v), Utils.UI_BAR_BG)
	if b >= 0.0:
		# the fog band: faint from the low to the high, a solid bar to the low
		var x1: float = clampf(b, 0.0, 1.0) * size_v.x
		bar.draw_rect(Rect2(0.0, 0.0, x1, size_v.y), Color(colour, 0.40))
		bar.draw_line(Vector2(x1, 0.0), Vector2(x1, size_v.y), colour, 2.0)
	bar.draw_rect(Rect2(0.0, 0.0, a * size_v.x, size_v.y), colour)
	bar.draw_rect(Rect2(Vector2.ZERO, size_v), Color(Utils.UI_GOLD, 0.45), false, 1.0)


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
	_set_force(_quote)
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
	_dir = {}
	_standing = {"marshal": marshal, "shown": shown, "info": info.duplicate(true), "ap_left": ap_left}
	_avoid = avoid.duplicate()
	title_label.text = "STANDING ORDER — " + shown.to_upper()
	# Row IC, Session 2 (pressed in the real client at the first player's
	# setup): the headline is ONE clipped line, and an exact order's if-thens
	# are the order itself - "Soult holds Lorraine — if he is attacked, dig in;
	# if he is outnumbered, fall …" was cut at the card's edge. The headline
	# says the order; its if-thens stand in the terms, which wrap, a line each
	# (`_standing_terms`). The whole sentence stays the hover.
	var bare := info.duplicate(true)
	bare["watch"] = ""
	command_label.text = standing_headline(shown, bare)
	command_label.tooltip_text = standing_headline(shown, info)
	var cancel_ap := int(info.get("cancel_ap", 1))
	send_button.text = "Cancel order  (%s)" % ("free" if cancel_ap <= 0 else Utils.plural(cancel_ap, "action"))
	terms_label.text = _standing_terms(info, ap_left)
	send_button.disabled = ap_left < cancel_ap
	line_button.disabled = false
	cancel_button.disabled = false
	# Row IC, Session 2b: the order of a man on his task to prove himself can
	# be neither cancelled nor changed - he takes no orders until it ends (the
	# terms say so; the two buttons are greyed with that reason as their hover).
	var proving := str(info.get("trial", ""))
	send_button.tooltip_text = ""
	line_button.tooltip_text = ""
	if proving != "":
		send_button.disabled = true
		line_button.disabled = true
		send_button.tooltip_text = Utils.clean_tip("He takes no orders until his task ends.")
		line_button.tooltip_text = Utils.clean_tip("He takes no orders until his task ends.")
	_raise()


const _THEN_DONE := {"fortify": "fortifies", "hold": "holds it", "drill": "drills", "defend": "defends it"}


static func standing_headline(shown: String, info: Dictionary) -> String:
	var dest := str(info.get("dest", ""))
	var who := str(info.get("target_shown", ""))
	# CC-4: the arrival verb (D7) and the standing contingency (D8), in the
	# backend's own words (`order_road.then` / `order_road.watch`).
	var then := str(info.get("then", ""))
	var watch := str(info.get("watch", ""))
	# Row IC, Session 2 (IC-9): an exact order's if-thens, and how many are
	# still unused ("2 of 3 left") — on a hold, and on a literal man's march,
	# pursuit or support too.
	var left := str(info.get("watch_left", ""))
	if watch != "" and left != "":
		watch += " (" + left + ")"
	match str(info.get("kind", "")):
		"march":
			return shown + " marches to " + dest + ((", then " + str(_THEN_DONE.get(then, then))) if then != "" else "") \
				+ ((" — " + watch) if watch != "" else "")
		"pursue":
			return shown + " pursues " + who + ((" — " + watch) if watch != "" else "")
		"hold":
			return shown + " holds " + dest + ((" — " + watch) if watch != "" else "")
		"support":
			return shown + " supports " + who
		"follow":
			return shown + " follows " + who
	return shown


func _standing_terms(info: Dictionary, ap_left: int) -> String:
	var lines := PackedStringArray()
	# Row IC, Session 2: the order's if-thens still unused, a line each, and how
	# many are left - in the backend's own words (`order_road.watch`).
	var watch := str(info.get("watch", ""))
	if watch != "":
		var left := str(info.get("watch_left", ""))
		var parts := watch.split("; ")
		var many := parts.size() > 1
		lines.append("[b]" + ("His exact orders — " + left + ":" if left != "" else "His exact order:") + "[/b]")
		var n := 0
		for part in parts:
			n += 1
			lines.append("  " + ((str(n) + ".  ") if many else "•  ") + str(part))
		# (the blind reading: all three readers asked which line wins when two are
		# true) the rule, in the order's own confirmation's words
		lines.append("[color=#" + Utils.COLOR_INFO + "]"
			+ ("As a turn ends he carries out the first of them that is true — by himself, at no cost, each once."
				if many else "As a turn ends he carries it out if it is true — by himself, at no cost, once.")
			+ "[/color]")
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
	# Row IC, Session 2b: a man on his task to prove himself - the trial's own
	# words, and that this order can be neither cancelled nor changed.
	var proving := str(info.get("trial", ""))
	if proving != "":
		lines.append("[b]" + proving + ".[/b]")
		lines.append("[color=#" + Utils.COLOR_WARNING
			+ "]He takes no orders until it ends: this order cannot be cancelled or changed.[/color]")
		return "\n".join(lines)
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


# ── Row IC, directives: the list of an order to several corps ──────────────
# The user's ruling (Plan Mode, November 19, 2026): "One list for all" — any
# order to several marshals is shown as ONE list before anything is spent:
# who it goes to, each man's order, its price, whether he may object, who will
# not go and why, the total against the actions in hand. A tick per man who
# can go; [Give the order] sends the ticked rows as ONE order (one request,
# one Take-back unit); [Cancel] spends nothing. Every word on it is the
# server's (`/directive_quote`, or `/command` with `list_first` —
# `backend/commands/directive.py`): the card composes no order and prices
# nothing of its own. The total for a changed set of ticks is the rows' own
# figures summed — the Staff's one price only for its whole column, the
# server's own rule (`directive.total_for`) — and the server refuses a give
# whose total is not the one shown.

const DIR_GIVE := "Give the order  (Enter)"
const DIR_HELP := ("Untick a corps to leave him out — click his row, or Up/Down and Space. "
	+ "Give sends the ticked orders as one; Take back (Ctrl+Z) undoes them all and gives their actions back. "
	+ "A marshal who objects asks you himself, and the rest wait behind his question.")
const DIR_ROW_PAD := 4.0           # a row's own margin (the keyboard's frame)
const DIR_ROW_GAP := 4
const DIR_SCROLLBAR_W := 14.0      # the room a shown scrollbar takes from the rows' words
const DIR_TICK_GAP := 8.0

var _dir: Dictionary = {}          # the list as the server drew it
var _dir_ticks: Dictionary = {}    # marshal key -> ticked
var _dir_pick: Array = []          # the keys of the rows that can go, in the list's order
var _dir_cursor := 0               # index into _dir_pick: the keyboard's row
var _dir_box: VBoxContainer = null
var _dir_scroll: ScrollContainer = null
var _dir_rows: VBoxContainer = null
var _dir_row_nodes: Dictionary = {}  # marshal key -> his row (PanelContainer)
var _dir_sum: RichTextLabel = null
# Row IC, Session 3 (IC3-H1): where the card stood while the list was being
# read — the list that replaces it opens THERE (x and top), so a slow reply
# never makes the card jump across the screen. (-1, -1) = no anchor.
var _dir_anchor := Vector2(-1.0, -1.0)
var _given_up := ""                # the headline of the list last let go (Cancel / Esc)


func given_up_words() -> String:
	"""The list just let go, in its headline's words — "" after any other
	answer (read once by main's cancel handler)."""
	var words := _given_up
	_given_up = ""
	return words


func open_directive(listing: Dictionary, avoid: Array = [], note: String = "") -> void:
	"""Raise the card on the LIST of an order to several corps — `listing` is
	the server's `directive` ({kind, who, order, line, click, rows, total,
	have, staff, sendable, note}); while it is being read, a placeholder
	({who, order, count, reading: true, note}). `note` is said above the rows
	(why the list was drawn again)."""
	# IC3-H1: the list that replaces a "reading" card keeps that card's place;
	# any other opening picks its own.
	var was_reading := visible and _mode == "directive" and bool(_dir.get("reading", false))
	if not was_reading:
		_dir_anchor = Vector2(-1.0, -1.0)
	_wear("directive")
	_quote = {}
	_standing = {}
	_avoid = avoid.duplicate()
	_dir = listing.duplicate(true)
	_dir_ticks = {}
	_dir_pick = []
	var rows: Array = _dir.get("rows", []) if _dir.get("rows") is Array else []
	for r in rows:
		if not (r is Dictionary):
			continue
		var key := str(r.get("marshal", ""))
		if bool(r.get("ok", false)) or bool(r.get("covered", false)):
			_dir_pick.append(key)
			_dir_ticks[key] = bool(r.get("ticked", false))
	_dir_cursor = 0
	# A list still being read, or one that could not be read, carries no rows to
	# count — its title says no number (the review: "ORDERS FOR 2 CORPS" stood
	# over a list of five while it was read).
	title_label.text = ("ORDERS FOR %d CORPS" % rows.size()) if not rows.is_empty() else "ORDERS FOR SEVERAL CORPS"
	var who := str(_dir.get("who", ""))
	var order := str(_dir.get("order", ""))
	command_label.text = directive_headline(who, order, _headline_room())
	command_label.tooltip_text = (who + ": " + order) if (who != "" and order != "") else (who + order)
	cancel_button.disabled = false
	_build_directive(note)
	_raise()
	refit.call_deferred()   # the rows' words re-wrap first


func directive_headline(who: String, order: String, room: float) -> String:
	"""Who and what: "Ney, Davout and Soult: march to Lorraine". When that does
	not fit the line (`room` px; the label trims with "…"), the ORDER leads —
	"Go to Vienna — Ney, Davout, Soult, …" — so a cut takes names the rows list
	anyway, never the order (pressed in the real client: eight names left
	"…" where "go to Vienna" stood)."""
	if who == "" or order == "":
		return who + order
	var plain := who + ": " + order
	if room <= 0.0 or _text_width(plain) <= room:
		return plain
	return order.left(1).to_upper() + order.substr(1) + " — " + who


func _text_width(text: String) -> float:
	var font: Font = command_label.get_theme_font("font")
	if font == null:
		return 0.0
	return font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1,
		command_label.get_theme_font_size("font_size")).x


func _headline_room() -> float:
	"""The headline's width on the card as `refit` will make it (the card's
	width less the frame's margins)."""
	var panel: PanelContainer = $PanelContainer
	var frame: StyleBox = panel.get_theme_stylebox("panel")
	var view := panel.get_viewport_rect().size
	var band := Utils.hud_band(view)
	var w := minf(minf(CARD_WIDTH, (band.y - band.x) * BAND_SHARE), maxf(160.0, view.x - 2.0 * CARD_EDGE))
	return maxf(160.0, w) - (frame.get_minimum_size().x if frame != null else 40.0)


func _build_directive(note: String) -> void:
	"""The list's nodes: a note, the rows in a scroll (those who can go with a
	tick; then who will not go, and why), the sum and the help."""
	_free_directive()
	var vb: VBoxContainer = $PanelContainer/VBox
	_dir_box = VBoxContainer.new()
	_dir_box.name = "DirectiveBox"
	_dir_box.add_theme_constant_override("separation", 6)
	vb.add_child(_dir_box)
	vb.move_child(_dir_box, command_label.get_index() + 1)
	var reading := bool(_dir.get("reading", false))
	var said := note.strip_edges()
	if said == "" and (reading or not bool(_dir.get("sendable", true))):
		said = str(_dir.get("note", "")).strip_edges()
	if said != "":
		var tone: String = Utils.COLOR_INFO if reading else Utils.COLOR_WARNING
		_dir_label("DirectiveNote", "[color=#" + tone + "]" + said + "[/color]", _dir_box)
	_dir_scroll = ScrollContainer.new()
	_dir_scroll.name = "DirectiveRows"
	_dir_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	# UI6-X22: a scroll whose child's width follows its bar can flip forever in
	# one frame — the bar's room is reserved (the rows' words already leave it).
	_dir_scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_RESERVE
	_dir_box.add_child(_dir_scroll)
	_dir_rows = VBoxContainer.new()
	_dir_rows.name = "Rows"
	_dir_rows.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_dir_rows.add_theme_constant_override("separation", DIR_ROW_GAP)
	_dir_scroll.add_child(_dir_rows)
	_dir_row_nodes = {}
	var stays := PackedStringArray()
	var rows: Array = _dir.get("rows", []) if _dir.get("rows") is Array else []
	for r in rows:
		if not (r is Dictionary):
			continue
		var key := str(r.get("marshal", ""))
		if _dir_pick.has(key):
			var row := _dir_row(r)
			_dir_rows.add_child(row)
			_dir_row_nodes[key] = row
		else:
			stays.append("[b]" + str(r.get("shown", key)) + "[/b] — " + str(r.get("why", "")))
	if not stays.is_empty():
		_dir_label("WillNotGo", "[color=#" + Utils.COLOR_ERROR + "]Will not go:[/color]\n"
			+ "\n".join(stays), _dir_rows)
	_dir_sum = _dir_label("DirectiveSum", "", _dir_box)
	if not reading:
		_dir_label("DirectiveHelp", "[color=#" + Utils.COLOR_INFO + "]" + DIR_HELP + "[/color]", _dir_box)
	_paint_directive()


func _dir_label(node_name: String, bbcode: String, parent: Control) -> RichTextLabel:
	var label := RichTextLabel.new()
	label.name = node_name
	label.bbcode_enabled = true
	label.scroll_active = false
	label.fit_content = false
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	label.text = bbcode
	parent.add_child(label)
	return label


func _dir_row(r: Dictionary) -> PanelContainer:
	"""One man who can go: his tick and his order in words. A click anywhere on
	the row ticks or unticks him (the tick itself too)."""
	var key := str(r.get("marshal", ""))
	var shown := str(r.get("shown", key))
	var row := PanelContainer.new()
	row.name = "Row_" + key
	row.mouse_filter = Control.MOUSE_FILTER_STOP
	row.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	row.tooltip_text = "Click to tick or untick " + shown + "."
	row.gui_input.connect(_on_dir_row_input.bind(key))
	var line := HBoxContainer.new()
	line.name = "Line"
	line.mouse_filter = Control.MOUSE_FILTER_PASS
	line.add_theme_constant_override("separation", int(DIR_TICK_GAP))
	row.add_child(line)
	var tick := CheckBox.new()
	tick.name = "Tick"
	tick.focus_mode = Control.FOCUS_NONE
	tick.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	tick.button_pressed = bool(_dir_ticks.get(key, false))
	tick.tooltip_text = row.tooltip_text
	tick.toggled.connect(_on_dir_ticked.bind(key))
	line.add_child(tick)
	var words := _dir_label("Words", directive_row_text(r, false), line)
	words.mouse_filter = Control.MOUSE_FILTER_PASS
	return row


static func directive_row_text(r: Dictionary, staff_carries: bool) -> String:
	"""One row in words: "Ney · march to Lorraine · 2 actions · arrives in 2
	turns · he may object", then what he replaces and the order's own notes
	(the server's), each on its line. Under the Staff's one order a covered
	man's own price gives way to it."""
	var shown := str(r.get("shown", r.get("marshal", "")))
	var parts := PackedStringArray(["[b]" + shown + "[/b]"])
	var says := str(r.get("says", ""))
	if says != "":
		parts.append(says)
	parts.append("in the Staff's one order" if staff_carries else _price(int(r.get("ap", 0))))
	var turns := int(r.get("turns", 0))
	if turns >= 1:
		parts.append("arrives in " + Utils.plural(turns, "turn"))
	var text := " · ".join(parts)
	if str(r.get("objection", "none")) == "possible":
		text += " · [color=#" + Utils.COLOR_WARNING + "]he may object[/color]"
	var replaces := str(r.get("replaces", ""))
	if replaces != "":
		text += "\n[color=#" + Utils.COLOR_GOLD + "]Replaces " + replaces + ".[/color]"
	var notes = r.get("notes", [])
	if notes is Array:
		for n in notes:
			var noted := str(n).strip_edges()
			if noted != "":
				text += "\n[color=#" + Utils.COLOR_WARNING + "]" + noted + "[/color]"
	return text


func _paint_directive() -> void:
	"""The ticks, the keyboard's row, each row's price, the sum and Give — as
	the ticks stand now."""
	if _dir_box == null or not is_instance_valid(_dir_box):
		return
	var members := directive_members()
	var total := directive_total()
	var have := int(_dir.get("have", 0))
	var rides := _rides_staff(members)
	var reading := bool(_dir.get("reading", false))
	# The title counts the corps the order goes to as the ticks stand (the
	# blind reading 2, all three readers: "ORDERS FOR 4 CORPS" while two go).
	var named := (_dir.get("rows", []) as Array).size() if _dir.get("rows") is Array else 0
	if not reading and named > 0:
		title_label.text = ("ORDERS FOR %d CORPS" % named) if members.size() >= named \
			else ("ORDERS FOR %d OF %d CORPS" % [members.size(), named])
	var rows_by: Dictionary = {}
	var rows: Array = _dir.get("rows", []) if _dir.get("rows") is Array else []
	for r in rows:
		if r is Dictionary:
			rows_by[str(r.get("marshal", ""))] = r
	for i in range(_dir_pick.size()):
		var key := str(_dir_pick[i])
		var row = _dir_row_nodes.get(key)
		if row == null or not is_instance_valid(row):
			continue
		var tick := (row as Node).get_node_or_null("Line/Tick") as CheckBox
		if tick != null:
			tick.set_pressed_no_signal(bool(_dir_ticks.get(key, false)))
		var words := (row as Node).get_node_or_null("Line/Words") as RichTextLabel
		if words != null and rows_by.has(key):
			var r: Dictionary = rows_by[key]
			words.text = directive_row_text(r, rides and bool(r.get("covered", false)))
		(row as PanelContainer).add_theme_stylebox_override("panel", _dir_row_style(i == _dir_cursor))
	var sum := ""
	var staff = _dir.get("staff", null)
	if reading or named == 0:
		sum = ""   # still reading, or the list could not be read (its note says so)
	elif _dir_pick.is_empty():
		sum = "[color=#" + Utils.COLOR_ERROR + "]No corps can take this order today — nothing can be sent.[/color]"
	elif members.is_empty():
		sum = "[color=#" + Utils.COLOR_WARNING + "]No corps is ticked — tick at least one to give the order.[/color]"
	elif total > have:
		sum = ("[color=#" + Utils.COLOR_ERROR + "][b]Cost: " + _price(total) + "[/b]" + _dir_breakdown(members, rows_by)
			+ " — only " + str(have) + " in hand. Untick a corps.[/color]")
	elif rides:
		sum = (_cost_words(total, have) + " — the Grand Quartier Général carries the whole column ("
			+ str(members.size()) + " corps) as one order.")
	else:
		sum = _cost_words(total, have, _dir_breakdown(members, rows_by)) + (
			" — 1 corps goes, by his own order." if members.size() == 1
			else " — " + str(members.size()) + " corps go, each by his own order.")
	# Directives' blind reading 1 (all three readers): a man who could go stood
	# unticked with no word why. Where ticking him would cost more than is left,
	# the card says so.
	var short := PackedStringArray()
	if not reading and not rides:
		for key in _dir_pick:
			var r = rows_by.get(str(key))
			if not bool(_dir_ticks.get(str(key), false)) and r is Dictionary and bool(r.get("ok", false)) \
					and total + int(r.get("ap", 0)) > have:
				short.append(str(r.get("shown", key)))
	if not short.is_empty() and sum != "":
		# Who takes the actions, and what is left (the blind reading 3: "not
		# enough actions are left" read beside "4 of the 4 in hand" as if 4 were
		# still there).
		var left := maxi(0, have - total)
		var leave := "leave none" if left == 0 else ("leave only " + _price(left))
		var why := ""
		if short.size() == 1:
			var need := 0
			for key in _dir_pick:
				var row = rows_by.get(str(key))
				if row is Dictionary and str(row.get("shown", key)) == short[0]:
					need = int(row.get("ap", 0))
			why = (short[0] + " is not ticked: he needs " + _price(need) + ", and the ticked corps " + leave
				+ ". Untick one of them to send him instead.")
		else:
			why = (_and_names(short) + " are not ticked: the ticked corps " + leave
				+ ". Untick one of them to send one of these instead.")
		sum += "\n[color=#" + Utils.COLOR_INFO + "]" + why + "[/color]"
		if staff is Dictionary and not (staff as Dictionary).is_empty():
			var covers = (staff as Dictionary).get("covers", [])
			var column: int = (covers as Array).size() if covers is Array else 0
			sum += (" Tick the whole column (" + str(column) + " corps) and the Grand Quartier Général carries"
				+ " them all for " + _price(int((staff as Dictionary).get("ap", 0))) + ".")
	if _dir_sum != null and is_instance_valid(_dir_sum):
		_dir_sum.text = sum
		_dir_sum.visible = sum != ""
	send_button.text = DIR_GIVE if not members.is_empty() else "Nothing to give"
	send_button.disabled = reading or members.is_empty() or total > have
	if visible:
		refit.call_deferred()


static func _cost_words(total: int, have: int, breakdown: String = "") -> String:
	if total <= 0:
		return "[b]It costs nothing[/b]"
	return "[b]Cost: " + _price(total) + "[/b]" + breakdown + " of the " + str(have) + " in hand"


static func _dir_breakdown(members: Array, rows_by: Dictionary) -> String:
	"""How the cost adds up — " (2 + 2)" — for two to eight corps at their own
	prices (directives' blind reading 1: "4 actions — 2 corps go" left two
	readers unsure it was two times two). "" for one corps, or more than eight."""
	if members.size() < 2 or members.size() > 8:
		return ""
	var parts := PackedStringArray()
	for key in members:
		var r = rows_by.get(str(key))
		parts.append(str(int(r.get("ap", 0)) if r is Dictionary else 0))
	return " (" + " + ".join(parts) + ")"


static func _and_names(names: PackedStringArray) -> String:
	if names.size() <= 1:
		return "".join(names)
	return ", ".join(names.slice(0, names.size() - 1)) + " and " + names[names.size() - 1]


func _dir_row_style(on: bool) -> StyleBox:
	"""The keyboard's row wears a faint gilt frame; the others an empty one of
	the same margins (no row jumps when the frame moves)."""
	if on:
		var lit := StyleBoxFlat.new()
		lit.bg_color = Color(Utils.UI_GOLD, 0.12)
		lit.border_color = Color(Utils.UI_GOLD, 0.55)
		lit.set_border_width_all(1)
		lit.set_corner_radius_all(3)
		lit.set_content_margin_all(DIR_ROW_PAD)
		return lit
	var plain := StyleBoxEmpty.new()
	plain.set_content_margin_all(DIR_ROW_PAD)
	return plain


func directive_members() -> Array:
	"""The ticked men, in the order the list shows them."""
	var out: Array = []
	for key in _dir_pick:
		if bool(_dir_ticks.get(str(key), false)):
			out.append(str(key))
	return out


func _rides_staff(members: Array) -> bool:
	"""Exactly the Staff's column is ticked: its one price carries them."""
	var staff = _dir.get("staff", null)
	if not (staff is Dictionary) or (staff as Dictionary).is_empty() or members.is_empty():
		return false
	var covers = (staff as Dictionary).get("covers", [])
	if not (covers is Array) or (covers as Array).size() != members.size():
		return false
	for key in covers:
		if not members.has(str(key)):
			return false
	return true


func directive_total() -> int:
	"""What giving the order to the ticked men costs, by the list's own figures:
	the Staff's one price for exactly its column, else each man's own (the
	server's `directive.total_for`)."""
	var members := directive_members()
	if _rides_staff(members):
		return int((_dir.get("staff") as Dictionary).get("ap", 0))
	var total := 0
	var rows: Array = _dir.get("rows", []) if _dir.get("rows") is Array else []
	for r in rows:
		if r is Dictionary and members.has(str(r.get("marshal", ""))):
			total += int(r.get("ap", 0))
	return total


func _move_dir_cursor(step: int) -> void:
	if _dir_pick.is_empty():
		return
	_dir_cursor = clampi(_dir_cursor + step, 0, _dir_pick.size() - 1)
	_paint_directive()
	_show_dir_cursor.call_deferred()


func _show_dir_cursor() -> void:
	if _dir_scroll == null or not is_instance_valid(_dir_scroll) or _dir_pick.is_empty():
		return
	var row = _dir_row_nodes.get(str(_dir_pick[clampi(_dir_cursor, 0, _dir_pick.size() - 1)]))
	if row != null and is_instance_valid(row):
		_dir_scroll.ensure_control_visible(row)


func _toggle_dir(key: String) -> void:
	if not _dir_pick.has(key) or bool(_dir.get("reading", false)):
		return
	_dir_ticks[key] = not bool(_dir_ticks.get(key, false))
	_dir_cursor = _dir_pick.find(key)
	AudioManager.play("click")
	_paint_directive()


func _on_dir_ticked(pressed: bool, key: String) -> void:
	if not _dir_pick.has(key):
		return
	_dir_ticks[key] = pressed
	_dir_cursor = _dir_pick.find(key)
	AudioManager.play("click")
	_paint_directive()


func _on_dir_row_input(event: InputEvent, key: String) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		_toggle_dir(key)
		get_viewport().set_input_as_handled()


func _free_directive() -> void:
	if _dir_box != null and is_instance_valid(_dir_box):
		if _dir_box.get_parent() != null:
			_dir_box.get_parent().remove_child(_dir_box)
		_dir_box.queue_free()
	_dir_box = null
	_dir_scroll = null
	_dir_rows = null
	_dir_row_nodes = {}
	_dir_sum = null


func directive_report() -> Dictionary:
	"""The list as it stands on the card — read by the driven instrument
	(`tools/dd_b_client.gd`); {} when the card wears another face."""
	if _mode != "directive" or _dir.is_empty():
		return {}
	var rows: Array = []
	var src: Array = _dir.get("rows", []) if _dir.get("rows") is Array else []
	for r in src:
		if not (r is Dictionary):
			continue
		var key := str(r.get("marshal", ""))
		var can_go := _dir_pick.has(key)
		rows.append({"marshal": key, "shown": str(r.get("shown", key)), "ok": can_go,
			"ticked": bool(_dir_ticks.get(key, false)),
			"text": directive_row_text(r, false) if can_go else str(r.get("why", ""))})
	var rect := placed_rect()
	return {
		"visible": visible, "mode": _mode, "title": title_label.text, "who": command_label.text,
		"cursor": str(_dir_pick[clampi(_dir_cursor, 0, _dir_pick.size() - 1)]) if not _dir_pick.is_empty() else "",
		"rows": rows, "members": directive_members(), "total": directive_total(),
		"have": int(_dir.get("have", 0)), "line": str(_dir.get("line", "")),
		"reading": bool(_dir.get("reading", false)),
		"total_text": _dir_sum.get_parsed_text() if (_dir_sum != null and is_instance_valid(_dir_sum)) else "",
		"give_text": send_button.text, "give_disabled": send_button.disabled,
		"rect": [rect.position.x, rect.position.y, rect.size.x, rect.size.y],
	}


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
	# Session UI-6: min(560, 0.9 × the HUD band), never past the viewport.
	var band := Utils.hud_band(view)
	var w := minf(minf(CARD_WIDTH, (band.y - band.x) * BAND_SHARE), maxf(160.0, view.x - 2.0 * CARD_EDGE))
	w = maxf(w, 160.0)
	_fit_buttons(w)
	panel.custom_minimum_size = Vector2(w, 0.0)
	var top := Utils.TOP_BAR_HEIGHT + Utils.top_bar_growth() + CARD_EDGE
	# Row IC, directives (pressed in the real client): the room is from under the
	# top bar to the screen's foot — the card never stands above `top`, so a
	# budget of the whole height less two edges let an eight-corps list run 26 px
	# past the bottom of a 765-px view.
	var avail := maxf(120.0, view.y - top - CARD_EDGE)
	var h := minf(_content_height(w, avail), avail)
	if _mode == "directive" and _dir_scroll != null and is_instance_valid(_dir_scroll):
		# The container's own minimum can exceed the measure by a few px (a
		# label's line, a separator): the rows' scroll gives that room back.
		var real := panel.get_combined_minimum_size().y
		if real > h + 0.5:
			_dir_scroll.custom_minimum_size.y = maxf(48.0, _dir_scroll.custom_minimum_size.y - (real - h))
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
	if _mode == "directive":
		# IC3-H1: the list stands where its "reading" card stood — x and top
		# kept (clamped into the view), whatever its new height.
		if _dir_anchor.x >= 0.0:
			pick = Vector2(clampf(_dir_anchor.x, CARD_EDGE, maxf(CARD_EDGE, view.x - w - CARD_EDGE)),
				clampf(_dir_anchor.y, top, maxf(top, view.y - h - CARD_EDGE)))
		elif bool(_dir.get("reading", false)):
			_dir_anchor = pick
	# Centre-anchored (the scene's, and `Utils.clamp_centered_panel`'s rule):
	# the offsets are measured from the viewport's middle.
	panel.offset_left = pick.x - view.x * 0.5
	panel.offset_right = panel.offset_left + w
	panel.offset_top = pick.y - view.y * 0.5
	panel.offset_bottom = panel.offset_top + h


func _content_height(w: float, avail: float) -> float:
	"""The card's height at width `w`, measured now — and the terms' room
	set: the terms laid out at the inner width (a container's minimum before
	its first layout reads a wrapping label at width 0 — a card 1,483 px
	tall), every other row at its own minimum, the separations and the
	panel's margins. The terms are BOUNDED (UXR-2's scroll rule): their
	height is the text's, capped at the room `avail` leaves (the height from
	under the top bar to the screen's foot) — longer terms scroll inside the
	label."""
	var panel: PanelContainer = $PanelContainer
	var box: VBoxContainer = $PanelContainer/VBox
	var frame: StyleBox = panel.get_theme_stylebox("panel")
	var margins: Vector2 = frame.get_minimum_size() if frame != null else Vector2(40, 32)
	var inner := maxf(40.0, w - margins.x)
	terms_label.size = Vector2(inner, terms_label.size.y)
	# Row IC, directives: the list's rows are the bounded part on its face (the
	# terms' rule): its note, sum and help at their own height, the rows in a
	# scroll capped at the room the viewport leaves.
	var listing := _mode == "directive" and _dir_box != null and is_instance_valid(_dir_box)
	var others := margins.y
	var rows := 0
	for child in box.get_children():
		var c := child as Control
		if c == null or not c.visible:
			continue
		rows += 1
		if listing and c == _dir_box:
			others += _dir_fixed_height(inner)
		elif c != terms_label:
			others += c.get_combined_minimum_size().y
	others += float(box.get_theme_constant("separation")) * maxf(0.0, float(rows - 1))
	var room := maxf(48.0, avail - others)
	if listing:
		var rows_h := minf(_dir_rows_height(inner), room)
		_dir_scroll.custom_minimum_size = Vector2(0.0, rows_h)
		return others + rows_h
	var terms_h := minf(float(terms_label.get_content_height()), room)
	terms_label.custom_minimum_size = Vector2(0.0, terms_h)
	return others + terms_h


func _size_rich(label: RichTextLabel, width: float) -> float:
	"""A wrapping label's true height at `width`, set as its minimum (a label
	reads its height only once it has a width — the card's terms' rule)."""
	label.size = Vector2(maxf(40.0, width), label.size.y)
	var h := float(label.get_content_height())
	label.custom_minimum_size = Vector2(0.0, h)
	return h


func _dir_fixed_height(inner: float) -> float:
	"""The list's parts outside its scroll (its note, its sum, its help)."""
	var h := 0.0
	var count := 0
	for child in _dir_box.get_children():
		var c := child as Control
		if c == null or not c.visible:
			continue
		count += 1
		if c == _dir_scroll:
			continue
		if c is RichTextLabel:
			h += _size_rich(c as RichTextLabel, inner)
		else:
			h += c.get_combined_minimum_size().y
	return h + float(_dir_box.get_theme_constant("separation")) * maxf(0.0, float(count - 1))


func _dir_rows_height(inner: float) -> float:
	"""The rows' whole height at the card's width (each row its tick and its
	words, wrapped; then who will not go)."""
	if _dir_rows == null or not is_instance_valid(_dir_rows):
		return 0.0
	var text_w := inner - DIR_SCROLLBAR_W
	var h := 0.0
	var count := 0
	for child in _dir_rows.get_children():
		var c := child as Control
		if c == null or not c.visible:
			continue
		count += 1
		if c is RichTextLabel:
			h += _size_rich(c as RichTextLabel, text_w)
			continue
		var tick := c.get_node_or_null("Line/Tick") as Control
		var words := c.get_node_or_null("Line/Words") as RichTextLabel
		var tick_size: Vector2 = tick.get_combined_minimum_size() if tick != null else Vector2(24.0, 24.0)
		var words_h := 0.0
		if words != null:
			words_h = _size_rich(words, text_w - tick_size.x - DIR_TICK_GAP - 2.0 * DIR_ROW_PAD)
		h += maxf(words_h, tick_size.y) + 2.0 * DIR_ROW_PAD
	return h + float(DIR_ROW_GAP) * maxf(0.0, float(count - 1))


func _fit_buttons(w: float) -> void:
	"""Session UI-6: the buttons stay whole at the card's width — under their
	authored row (BUTTONS_AUTHORED_W) inside the frame they shrink to their
	words; with room again they take their authored widths back."""
	var frame: StyleBox = ($PanelContainer as PanelContainer).get_theme_stylebox("panel")
	var inner: float = w - (frame.get_minimum_size().x if frame != null else 40.0)
	var tight: bool = inner < BUTTONS_AUTHORED_W
	for button in [send_button, line_button, cancel_button]:
		var b := button as Button
		if b == null:
			continue
		if not _button_min_w.has(b.name):
			_button_min_w[b.name] = b.custom_minimum_size.x
		b.custom_minimum_size.x = 0.0 if tight else float(_button_min_w[b.name])


func placed_rect() -> Rect2:
	"""Where the card stands (GLOBAL) — read by the CC harness."""
	return ($PanelContainer as Control).get_global_rect()


func command() -> String:
	"""The command on the card — exactly the quote's."""
	return str(_quote.get("command", ""))


func is_sendable() -> bool:
	return visible and not send_button.disabled


func close_given() -> void:
	"""Row IC, directives: the host took the list's Give — the card shuts and
	the list is let go (a list drawn again arrives as a new one)."""
	_close_quietly()
	_free_directive()
	_dir = {}
	_dir_anchor = Vector2(-1.0, -1.0)


func close_card() -> void:
	"""Shut the card WITHOUT an answer (the selection was let go under it). A
	list shut so is remembered for main's "Not given" (`given_up_words`)."""
	_given_up = command_label.text if (_mode == "directive" and not _dir.is_empty() and visible) else ""
	_quote = {}
	_standing = {}
	_dir = {}
	_dir_anchor = Vector2(-1.0, -1.0)
	if visible:
		close_popup()
	_free_directive()


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
		lines.append_array(_alt_lines(q))   # row IC, Session 2: another order may still go
		return "\n".join(lines)
	if bool(q.get("already", false)):
		lines.append("[b]No cost[/b] — " + str(q.get("note", "he is already carrying out that order.")))
		return "\n".join(lines)
	lines.append("[b]" + price_of(q) + "[/b] · " + _clock(q))
	lines.append_array(_ground_lines(q))
	var road = q.get("road", [])
	if road is Array and road.size() > 1:
		lines.append("[color=#" + Utils.COLOR_INFO + "]Road: " + " → ".join(PackedStringArray(road)) + "[/color]")
	var replaces := str(q.get("replaces", ""))
	if replaces != "":
		lines.append("[color=#" + Utils.COLOR_GOLD + "]Replaces " + replaces + ".[/color]")
	if str(q.get("objection", "none")) == "possible":
		lines.append("[color=#" + Utils.COLOR_WARNING + "]He may object.[/color]")
	# S14E-24: an attack's card is the confirm - Berthier's muster is on it.
	var muster := str(q.get("muster", ""))
	if muster != "":
		lines.append("[color=#" + Utils.COLOR_INFO + "]" + muster + "[/color]")
	# Row BA, BA-3: a great battle opens a day — the card says so before the order is given
	var day = q.get("day", null)
	if day is Dictionary and bool(day.get("great", false)):
		var commander := str(q.get("shown", ""))
		var his_road_said := ""
		if day.get("his_road", null) is bool:
			his_road_said = " His road to the rear is open." if bool(day.get("his_road")) \
				else " No road lies open behind him."
		# BA-4: a key battle short of the game's great one (80,000 men) is a pitched battle
		var battle_said := "A pitched battle" if bool(day.get("pitched", false)) else "A great battle"
		lines.append("[color=#" + Utils.COLOR_GOLD + "]" + battle_said + " — "
			+ (commander if commander != "" else "your lead") + " commands the day: "
			+ Utils.plural(int(day.get("points", 0)), "point") + "." + his_road_said + "[/color]")
	# S14G-X165: what a win here adds to Europe's alarm (the muster preview's own sentence).
	var alarm := str(q.get("alarm", ""))
	if alarm != "":
		lines.append("[color=#" + Utils.COLOR_INFO + "]" + alarm + "[/color]")
	lines.append_array(_bring_lines(q))
	var contact := str(q.get("contact", ""))
	var note := str(q.get("note", ""))
	if contact != "":
		lines.append("[color=#" + Utils.COLOR_WARNING + "]" + contact + "[/color]")
	if note != "" and note != contact:
		lines.append("[color=#" + Utils.COLOR_WARNING + "]" + note + "[/color]")
	# S14E-13: what the march takes out of the Descent camp (said by the quote).
	var camp := str(q.get("camp", ""))
	if camp != "":
		lines.append("[color=#" + Utils.COLOR_WARNING + "]" + camp + "[/color]")
	# S14E-13's sweep: Iron Resolve stacks, a formed square, a turn-1 drill the march would cost.
	var departs := str(q.get("departs", ""))
	if departs != "":
		lines.append("[color=#" + Utils.COLOR_WARNING + "]" + departs + "[/color]")
	# BA2-X21 (row BA, BA-4): the men the order's first march costs — it is taken the moment the order is given.
	var march_cost := str(q.get("march_cost", ""))
	if march_cost != "":
		lines.append("[color=#" + Utils.COLOR_WARNING + "]" + march_cost + "[/color]")
	# S14E-22: the detour round a road the diplomacy shuts (the typed order asks the same).
	var detour := str(q.get("detour", ""))
	if detour != "":
		lines.append("[color=#" + Utils.COLOR_WARNING + "]" + detour + "[/color]")
	# S14E-X67: the campaign pay the destination draws.
	var pay := str(q.get("pay", ""))
	if pay != "":
		lines.append("[color=#" + Utils.COLOR_WARNING + "]" + pay + "[/color]")
	# S14G-11: the guarded ground the road crosses - the Ansbach trap's price (the typed order asks the same).
	var guard := str(q.get("guard", ""))
	if guard != "":
		lines.append("[color=#" + Utils.COLOR_WARNING + "]" + guard + "[/color]")
	# S14G-7: the front the destination is - an ally's province whose war a truce of ours leaves running.
	var front := str(q.get("front", ""))
	if front != "":
		lines.append("[color=#" + Utils.COLOR_WARNING + "]" + front + "[/color]")
	# S14G-2 / S14G-3: what the standing order does once taken (a support's lapse, an aggressive man's interrupt).
	var terms_text := str(q.get("terms", ""))
	if terms_text != "":
		lines.append("[color=#" + Utils.COLOR_WARNING + "]" + terms_text + "[/color]")
	lines.append_array(_alt_lines(q))
	return "\n".join(lines)


# ── Row IC, Session 2 (IC-7): a button for every simple order, on the card ──
# The card that opens on an enemy quoted the attack and nothing else; the card
# that opens on a province quoted the march. The quote now carries the OTHER
# simple orders (`alts`: chase him, bombard, charge him, the attack held back)
# and what a march may do on arrival (`thens`: then hold, then dig in, then
# drill, then stand) — each row the order's own line as the read-back reads it
# (`backend/commands/order_quotes.py`; the client's table is simple_orders.gd).
# A chip sends that line at once down the card's own road and the card closes;
# a row the game would refuse is dimmed beside the game's own reason.
const ALT_LEAD := "Or another order — a chip sends it now, and this card closes:"
const THEN_LEAD := "Or march and, on arrival — a chip sends the march with it:"


func _alt_lines(q: Dictionary) -> PackedStringArray:
	var lines := PackedStringArray()
	var info := "[color=#" + Utils.COLOR_INFO + "]"
	for key in ["alts", "thens"]:
		var rows = q.get(key, [])
		if not (rows is Array) or (rows as Array).is_empty():
			continue
		var chips := PackedStringArray()
		for a in rows:
			if not (a is Dictionary) or str(a.get("command", "")) == "":
				continue
			var label := str(a.get("label", ""))
			# a march's "then" is free with the march: its price is the card's own
			if key == "alts":
				label += " · " + _price(int(a.get("ap", 0)))
			# the chip's hover says what its order DOES, in the one table's words
			# (the blind reading: "Chase him" did not say what chasing is)
			var tip := str(SimpleOrders.row(str(a.get("id", "")).get_slice(":", 0)).get("tip", ""))
			if bool(a.get("ok", false)):
				chips.append(Utils.bb_button_chip("do:" + str(a.get("command", "")), label,
					Utils.COLOR_GOLD, BRING_CHIP_BG, "", tip))
			else:
				chips.append(Utils.bb_chip_disabled(str(a.get("label", "")), "", str(a.get("refusal", "")))
					+ " " + info + str(a.get("refusal", "")) + "[/color]")
		if chips.is_empty():
			continue
		lines.append(info + (ALT_LEAD if key == "alts" else THEN_LEAD) + "[/color]")
		lines.append("  " + "  ".join(chips))
	return lines


# ── Row BA, BA-2 (November 14, 2026): the plan of battle on the attack's card ──
# The quote's `bring` rows (`order_quotes.bring_quotes`): for each corps of ours
# standing by that the muster says will NOT come, or may not, the order the game
# already has that would bring him — SUPPORT's own quote, with the muster's
# reason or his odds before and after. A chip sends that order at once down the
# card's own road; the card closes (its muster is no longer true) and the lead
# is selected again, so the next card quotes the muster as it then stands.
const BRING_CHIP_BG := "233043"
const BRING_LEAD := "Bring up — a chip sends that order now, and this card closes:"


static func bring_label(b: Dictionary) -> String:
	"""`Soult · support Ney · 1 AP` — the man, the order in its own words (the
	quote's command after his name), its price."""
	var command := str(b.get("command", ""))
	var cut := command.find(", ")
	return str(b.get("shown", "")) + " · " + (command.substr(cut + 2) if cut >= 0 else command) \
		+ " · " + Utils.quote_price_tail(b)


func _bring_lines(q: Dictionary) -> PackedStringArray:
	"""A line per `bring` row under the muster: the chip, then why the order is
	needed (the muster's reason he stays, or his odds before and after) — or,
	for an order that would be refused, its words dimmed beside the reason."""
	var lines := PackedStringArray()
	var rows = q.get("bring", [])
	if not (rows is Array):
		return lines
	var info := "[color=#" + Utils.COLOR_INFO + "]"
	for b in rows:
		if not (b is Dictionary) or bool(b.get("already", false)) or str(b.get("command", "")) == "":
			continue
		if bool(b.get("ok", false)):
			var said := str(b.get("why", ""))
			# what the order's first step MEETS (a corps we see on his road)
			if str(b.get("contact", "")) != "":
				said += (" · " if said != "" else "") + str(b.get("contact", ""))
			if str(b.get("replaces", "")) != "":
				said += (" · " if said != "" else "") + "replaces " + str(b.get("replaces", ""))
			if str(b.get("objection", "none")) == "possible":
				said += (" · " if said != "" else "") + "he may object"
			lines.append("  " + Utils.bb_button_chip("do:" + str(b.get("command", "")), bring_label(b),
				Utils.COLOR_GOLD, BRING_CHIP_BG) + ("  " + info + said + "[/color]" if said != "" else ""))
		else:
			lines.append("  " + Utils.bb_chip_disabled(str(b.get("shown", "")) + " · support", "", "")
				+ "  " + info + str(b.get("refusal", "")) + "[/color]")
	if not lines.is_empty():
		lines.insert(0, info + BRING_LEAD + "[/color]")
	return lines


func _ground_lines(q: Dictionary) -> PackedStringArray:
	"""Row PW (the first playtest: "sometimes they enter enemy land without
	taking it"): what the order does to the province it ends in — the quote's
	`ground` (`backend/commands/ground.py`), in plain words under the price:
	green where the province becomes ours, amber where he would only stand
	there, and then the order that WOULD take it as a chip ("Storm Vienna
	instead" — its own card, with the reckoning)."""
	var lines := PackedStringArray()
	var ground = q.get("ground", {})
	if not (ground is Dictionary):
		return lines
	var said := str(ground.get("line", "")).strip_edges()
	if said == "":
		return lines
	# A corps we see in the road stops the march before the province is
	# reached: the contact line is what happens first, and a promise about
	# the province above it ("takes it …") would be read as the result.
	if str(q.get("contact", "")).strip_edges() != "" and str(ground.get("code", "")) != "enemy_corps":
		return lines
	# The siege's own card: its note says the whole of it, once.
	if str(q.get("kind", "")) == "take" and str(ground.get("code", "")) == "fort":
		return lines
	var takes = ground.get("takes", null)
	var tone: String = Utils.COLOR_SUCCESS if (takes is bool and takes) else Utils.COLOR_WARNING
	lines.append("[color=#" + tone + "]" + said.substr(0, 1).to_upper() + said.substr(1) + ".[/color]")
	var remedy := str(ground.get("remedy_command", ""))
	var label := str(ground.get("remedy_label", ""))
	if remedy != "" and label != "" and not (takes is bool and takes) and str(q.get("kind", "")) != "take":
		var chip_meta := "do:" + remedy
		if str(ground.get("code", "")) in ["garrison", "garrison_unsure", "fort"]:
			chip_meta = "take:" + str(q.get("dest", ""))   # its own card: the storm's reckoning
		lines.append("  " + Utils.bb_button_chip(chip_meta, label + " instead", Utils.COLOR_GOLD, BRING_CHIP_BG))
	return lines


func _on_terms_meta(meta) -> void:
	"""A `bring` chip pressed: its own quoted command is handed on, the card
	shut first (an order's card answers once)."""
	var meta_str := str(meta)
	# Row PW: "Storm it instead" — the order that takes the province, on its own card.
	if _mode == "order" and visible and meta_str.begins_with("take:"):
		var province := meta_str.substr("take:".length())
		if province != "":
			_close_quietly()
			take_requested.emit(province)
		return
	if _mode != "order" or not visible or not meta_str.begins_with("do:"):
		return
	var cmd := meta_str.substr("do:".length())
	if cmd == "":
		return
	_close_quietly()
	bring_requested.emit(cmd)


static func _price(ap: int) -> String:
	return "free" if ap <= 0 else Utils.plural(ap, "action")


static func price_of(q: Dictionary) -> String:
	"""Row BA, BA-4 (BA3-X5): a quote's price in the player's words — a word
	of an open day of battle costs the day's points, never an action
	(`Utils.quote_price`); the card said "free" over it."""
	var said := Utils.quote_price(q)
	return said if said != "" else _price(int(q.get("ap", 0)))


static func _clock(q: Dictionary) -> String:
	var turns := int(q.get("turns", 0))
	if bool(q.get("halts", false)):
		# Row BA, BA-4: the order's first step meets a corps his friend can
		# strike — he halts there and joins the friend's next attack (the
		# approach rule); "joins him in 2 turns" said the road he will not walk.
		return "halts at the approach"
	match str(q.get("kind", "")):
		"attack":
			return "attacks at once"
		"support", "follow":
			return "joins him this turn" if turns <= 0 else "joins him in " + Utils.plural(turns, "turn")
		"take":
			# Row PW: the order that takes a province — what begins, by what holds it.
			var held = q.get("ground", {})
			match str(held.get("code", "")) if held is Dictionary else "":
				"fort":
					return "the siege begins now"
				"garrison", "garrison_unsure":
					return "the assault goes in now"
			return "taken now"
		"move":
			return "arrives now"
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
			elif _mode == "directive":
				AudioManager.play("error")   # row IC: nothing ticked, or more than in hand — the list stays
			else:
				_on_cancel()   # a refused order's Enter only closes the card
		KEY_ESCAPE:
			_on_cancel()
		# Row IC, directives: the list's own keys — Up/Down move the keyboard's
		# row, Space ticks or unticks it.
		KEY_UP:
			if _mode == "directive":
				_move_dir_cursor(-1)
		KEY_DOWN:
			if _mode == "directive":
				_move_dir_cursor(1)
		KEY_SPACE:
			if _mode == "directive" and not _dir_pick.is_empty():
				_toggle_dir(str(_dir_pick[clampi(_dir_cursor, 0, _dir_pick.size() - 1)]))


func _on_send() -> void:
	if send_button.disabled:
		return
	match _mode:
		"standing":
			var who := standing_marshal()
			_close_quietly()
			standing_cancel_requested.emit(who)
			return
		"directive":
			# Row IC: the ticked men, in the list's order, and the total shown —
			# ONE request (the server checks both against the list it draws again).
			var members := directive_members()
			if members.is_empty():
				return
			var line := str(_dir.get("line", ""))
			var total := directive_total()
			var click := bool(_dir.get("click", false))
			# The host accepts the Give and shuts the card (`close_given`); a Give
			# it must refuse (a command still on the wire) leaves the list up —
			# the review: the list was dropped before the guard could refuse it.
			directive_give_requested.emit(line, members, total, click)
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
	# Row IC, directives: what a list let go was ("Not given: …" in the log —
	# the blind reading 2), read by main right after `cancelled`.
	_given_up = command_label.text if (_mode == "directive" and not _dir.is_empty()) else ""
	_quote = {}
	_standing = {}
	_dir = {}
	close_popup()
	_free_directive()
	cancelled.emit()
