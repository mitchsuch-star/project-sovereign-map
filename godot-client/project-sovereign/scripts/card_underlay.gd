extends Control

# =============================================================================
# INK & IRON — The Card Underlay (Session UI, November 11, 2026)
# =============================================================================
# The text-heavy books (the Generals, both ledgers) are each ONE RichTextLabel:
# a long run of lines in which no entry was bounded. This paints a card behind
# each entry — a dark inset well, a hairline in the entry's tone, a spine of the
# same tone down its left edge — WITHOUT touching a word of the page.
#
# How a page describes its own cards. A builder wraps an entry between two
# invisible marks (`Utils.card_open(tone)` … `Utils.CARD_CLOSE`): empty no-op
# colour tags, which add nothing to the label's parsed text and draw nothing.
# This control reads them out of the label's CURRENT `text` every time it
# draws, so there is no bookkeeping to go stale — a tab switch, a refresh, a
# chip that greys itself in place (`Utils.mark_chip_sent` rewrites `text`) all
# leave the marks where the cards are.
#
# Where a card stands. A mark's paragraph is the count of "\n" before it; the
# label gives each paragraph's offset (`get_paragraph_offset`). If the label's
# own paragraph count ever disagrees with the text's, NOTHING is drawn: a page
# with a construct this model does not know can lose its cards, never have
# them drawn across the wrong lines.
#
# What it is not. A plain Control with `_draw` — not a Panel or a ColorRect, so
# the capture harness never reads it as a surface lying over text; mouse-
# ignored, zero minimum size, a CHILD of the label, so the whole-line scroll
# snap (`Utils._whole_line_boxes` never descends into a RichTextLabel) and the
# action probe do not see it.
# =============================================================================

## The open mark's head and tail: "[fgcolor=#RRGGBB00][/fgcolor]" — the six
## digits are the card's tone, the alpha is zero.
const OPEN_HEAD := "[fgcolor=#"
const OPEN_TAIL := "00][/fgcolor]"
const CLOSE_MARK := "[bgcolor=#00000000][/bgcolor]"
## The label's own left / right text margins, so words sit inside the cards.
const SIDE_MARGIN := 12.0
## A card's reach above its first line and below its last.
const PAD_TOP := 5.0
const PAD_BOTTOM := 6.0
const SPINE_WIDTH := 3.0

var _label: RichTextLabel = null
var _image_re: RegEx = null


static func attach(label: RichTextLabel) -> Control:
	"""Give `label` its underlay (once) and its side margins. Returns the
	underlay; a label that already carries one is left as it is."""
	if label == null:
		return null
	var held = label.get_node_or_null("CardUnderlay")
	if held != null:
		return held
	var box := StyleBoxEmpty.new()
	box.content_margin_left = SIDE_MARGIN
	box.content_margin_right = SIDE_MARGIN
	label.add_theme_stylebox_override("normal", box)
	var layer: Control = load("res://scripts/card_underlay.gd").new()
	layer.name = "CardUnderlay"
	layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.show_behind_parent = true
	layer.set_anchors_preset(Control.PRESET_FULL_RECT)
	label.add_child(layer)
	return layer


func _ready() -> void:
	_label = get_parent() as RichTextLabel
	if _label == null:
		return
	_image_re = RegEx.create_from_string("^\\[img width=(\\d+) height=(\\d+)\\]")
	_label.finished.connect(queue_redraw)
	_label.resized.connect(queue_redraw)
	_label.draw.connect(queue_redraw)


static func cards_in(text: String) -> Array:
	"""Every card the text describes: [first paragraph, last paragraph, tone,
	portrait size]. Pure — the pins read it without an engine frame."""
	var out: Array = []
	var at := 0
	var paragraph := 0
	var counted := 0
	while true:
		var open := text.find(OPEN_HEAD, at)
		if open < 0:
			break
		var tail := open + OPEN_HEAD.length() + 6
		if text.substr(tail, OPEN_TAIL.length()) != OPEN_TAIL:
			at = open + OPEN_HEAD.length()
			continue
		var close := text.find(CLOSE_MARK, tail)
		if close < 0:
			break
		paragraph += text.count("\n", counted, open) if open > counted else 0
		counted = open
		var first := paragraph
		paragraph += text.count("\n", counted, close) if close > counted else 0
		counted = close
		# A close mark at the head of a paragraph ends the card on the line above.
		var last := paragraph
		if close > 0 and text[close - 1] == "\n":
			last = paragraph - 1
		var tone := Color.from_string(text.substr(open + OPEN_HEAD.length(), 6), Color(0.85, 0.75, 0.55))
		var body_at := tail + OPEN_TAIL.length()
		out.append([first, maxi(last, first), tone, body_at, close])
		at = close + CLOSE_MARK.length()
	return out


func _draw() -> void:
	if _label == null or not _label.is_visible_in_tree():
		return
	# Session UI-2: a table is one paragraph of its page, whatever its cells
	# hold — the newlines INSIDE tables are the cells' own (Utils.flatten_tables).
	var text := Utils.flatten_tables(_label.text)
	if text.find(CLOSE_MARK) < 0:
		return
	var count := _label.get_paragraph_count()
	# The fail-safe: the page's paragraphs are the text's newlines, or no card.
	if count != text.count("\n") + 1:
		return
	var box := _label.get_theme_stylebox("normal")
	var top: float = box.get_margin(SIDE_TOP) if box != null else 0.0
	var left: float = box.get_margin(SIDE_LEFT) if box != null else 0.0
	var width := size.x
	var foot := float(_label.get_content_height())
	var paragraphs := text.split("\n")
	for card in cards_in(text):
		var first: int = card[0]
		var last: int = card[1]
		if first >= count:
			continue
		# Session UI-3: a pad reaches into the neighbouring paragraph only
		# when that paragraph is blank (or the label's edge).
		var pad_top: float = PAD_TOP if blank_paragraph(paragraphs, first - 1) else 0.0
		var pad_bottom: float = PAD_BOTTOM if blank_paragraph(paragraphs, last + 1) else 0.0
		var y0 := top + _label.get_paragraph_offset(first) - pad_top
		var y1 := top + (_label.get_paragraph_offset(last + 1) if last + 1 < count else foot) + pad_bottom
		if y1 - y0 < 8.0:
			continue
		_draw_card(Rect2(2.0, y0, width - 4.0, y1 - y0), card[2])
		_draw_locket(text, card, left, top)


static func blank_paragraph(paragraphs: PackedStringArray, i: int) -> bool:
	"""Session UI-3 (November 12, 2026): whether a card's pad may reach into
	paragraph `i` — only a blank one (or past the label's edge). Two cards set
	line on line, or a heading set straight on a card, had each card's rule
	drawn through the other's words (the Balance's road cards, the blind
	readers' F13): with no blank paragraph between, the card's edge is its own
	paragraph's edge. Pure — the pins read it without an engine frame."""
	if i < 0 or i >= paragraphs.size():
		return true
	var p: String = paragraphs[i]
	if p.find("[img") >= 0 or p.find("[lb]") >= 0 or p.find("[rb]") >= 0:
		return false
	return Utils.bb_plain(p) == ""


func _draw_card(rect: Rect2, tone: Color) -> void:
	# the well: darker than the panel it is cut into, never lighter
	draw_rect(rect, Color(0, 0, 0, 0.22))
	# an inset's upper lip
	draw_rect(Rect2(rect.position, Vector2(rect.size.x, 1.0)), Color(0, 0, 0, 0.35))
	# the hairline, in the entry's tone
	draw_rect(rect, Color(tone.r, tone.g, tone.b, 0.32), false, 1.0)
	# the spine
	draw_rect(Rect2(rect.position, Vector2(SPINE_WIDTH, rect.size.y)), Color(tone.r, tone.g, tone.b, 0.85))


func _draw_locket(text: String, card: Array, left: float, top: float) -> void:
	"""A portrait standing at the head of a line in a card is ringed in gilt:
	the image is the page's own (untouched); the ring and its shadow are drawn
	round it. A small image (a flag, a bar) is not a portrait."""
	if _image_re == null:
		return
	var body_at: int = card[3]
	var span := text.substr(body_at, int(card[4]) - body_at)
	var at := 0
	var paragraph: int = card[0]
	while true:
		var m := _image_re.search(span.substr(at, 64))
		if m != null:
			var w := float(m.get_string(1).to_int())
			var h := float(m.get_string(2).to_int())
			if w >= 32.0 and h >= 32.0:
				var origin := Vector2(left, top + _label.get_paragraph_offset(paragraph))
				_ring(Rect2(origin - Vector2(2.0, 2.0), Vector2(w + 4.0, h + 4.0)), card[2])
				return
		var nl := span.find("\n", at)
		if nl < 0:
			return
		at = nl + 1
		paragraph += 1


func _ring(frame: Rect2, tone: Color) -> void:
	draw_rect(frame.grow(2.0), Color(0, 0, 0, 0.35))
	draw_rect(frame, Color(tone.r, tone.g, tone.b, 0.9), false, 1.0)
	draw_rect(frame.grow(-2.0), Color(0, 0, 0, 0.6), false, 1.0)
