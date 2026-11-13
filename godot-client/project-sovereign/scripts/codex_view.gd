extends CanvasLayer
class_name CodexView

# =============================================================================
# Session UI-5 (November 12, 2026) — "Help & Keys", the game's own manual.
# =============================================================================
# A book in the frame kit: CanvasLayer 50, a centred gilt window, three tabs
# (KEYS / TERMS / ORDERS) over ONE scrolling page, and a filter field that
# narrows the open tab's rows as you type. Nothing here asks the backend; the
# keys come live from `Keys` (so a rebinding shows at the next open), the words
# from `CodexTerms` (data only, written from the code and docs it names).
#
#   var codex := CodexView.new()
#   add_child(codex)
#   codex.open("keys")           # "keys" | "terms" | "orders"
#   codex.closed.connect(...)    # Esc, the ✕, or a click on the desk closes it
#
# Size: about 62 % x 85 % of the view; the whole view on the compact view
# (`Utils.compact_view()`). Everything scrolls inside the window.
# =============================================================================

signal closed

const TAB_KEYS := "keys"
const TAB_TERMS := "terms"
const TAB_ORDERS := "orders"
const TABS := [TAB_KEYS, TAB_TERMS, TAB_ORDERS]
const TAB_LABELS := {"keys": "Keys", "terms": "Terms", "orders": "Orders"}

const FULL_SHARE := Vector2(0.62, 0.85)
const MIN_FULL_WIDTH := 480.0
const SCROLL_STEP := 60

var _root: Control = null
var _panel: PanelContainer = null
var _title: Label = null
var _close_button: Button = null
var _filter: LineEdit = null
var _tab_buttons: Dictionary = {}
var _tab_strip: Dictionary = {}
var _scroll: ScrollContainer = null
var _label: RichTextLabel = null
var _footer: Label = null

var _tab: String = TAB_KEYS
var _page_width: float = 600.0


func _ready() -> void:
	layer = 50
	_build()
	var vp: Viewport = get_viewport()
	if vp != null and not vp.size_changed.is_connected(_on_viewport_resized):
		vp.size_changed.connect(_on_viewport_resized)
	hide()


func _build() -> void:
	# The desk: a dim sheet over the game; a click on it closes the book.
	_root = Control.new()
	_root.name = "CodexRoot"
	_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	_root.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(_root)

	var dim := ColorRect.new()
	dim.name = "BackgroundOverlay"
	dim.color = Color(0, 0, 0, 0.55)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_STOP
	dim.gui_input.connect(_on_overlay_input)
	_root.add_child(dim)

	var centre := CenterContainer.new()
	centre.name = "Centre"
	centre.set_anchors_preset(Control.PRESET_FULL_RECT)
	centre.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_root.add_child(centre)

	_panel = PanelContainer.new()
	_panel.name = "PanelContainer"
	centre.add_child(_panel)

	var box := VBoxContainer.new()
	box.name = "VBoxContainer"
	box.add_theme_constant_override("separation", 8)
	_panel.add_child(box)

	# Header: the title and the close ✕.
	var head := HBoxContainer.new()
	head.name = "HeaderRow"
	box.add_child(head)
	_title = Label.new()
	_title.name = "TitleLabel"
	_title.text = "Help & Keys"
	_title.theme_type_variation = &"DialogTitle"
	_title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	head.add_child(_title)
	_close_button = Button.new()
	_close_button.name = "CloseButton"
	_close_button.custom_minimum_size = Vector2(32, 32)
	_close_button.tooltip_text = "Close (Esc)"
	_close_button.focus_mode = Control.FOCUS_NONE
	_close_button.set_meta("no_click_sfx", true)
	_close_button.pressed.connect(close)
	head.add_child(_close_button)
	Utils.apply_icon_only_button(_close_button, Utils.ICON_PHOSPHOR + "x.svg")

	# The tab strip, the one idiom (`Utils.tab_styles`).
	var tabs := HBoxContainer.new()
	tabs.name = "TabRow"
	tabs.add_theme_constant_override("separation", 4)
	box.add_child(tabs)
	_tab_strip = Utils.tab_styles(12.0, 4.0)
	for id in TABS:
		var btn := Button.new()
		btn.name = "Tab_" + String(id)
		btn.text = String(TAB_LABELS[id])
		btn.focus_mode = Control.FOCUS_NONE
		btn.set_meta("no_click_sfx", true)
		btn.pressed.connect(_on_tab_pressed.bind(String(id)))
		tabs.add_child(btn)
		Utils.dress_tab(btn, _tab_strip)
		_tab_buttons[String(id)] = btn

	# The filter field: typing narrows the open tab's rows.
	_filter = LineEdit.new()
	_filter.name = "FilterField"
	_filter.placeholder_text = "Filter this tab…"
	_filter.clear_button_enabled = true
	_filter.text_changed.connect(_on_filter_changed)
	box.add_child(_filter)

	# The page: one label inside one scroll.
	_scroll = ScrollContainer.new()
	_scroll.name = "ScrollContainer"
	_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	box.add_child(_scroll)
	_label = RichTextLabel.new()
	_label.name = "ContentLabel"
	_label.bbcode_enabled = true
	_label.fit_content = true
	_label.scroll_active = false
	_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_label.theme_type_variation = &"BodyLargeRich"
	_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	# A fit_content label inside a scroll would eat the wheel at STOP.
	_label.mouse_filter = Control.MOUSE_FILTER_PASS
	_scroll.add_child(_label)
	Utils.keep_whole_lines(_label)
	Utils.card_page(_label)

	_footer = Label.new()
	_footer.name = "FooterLabel"
	_footer.theme_type_variation = &"Caption"
	_footer.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_footer.add_theme_color_override("font_color", Utils.UI_TEXT_DIM)
	box.add_child(_footer)


# --- the API ----------------------------------------------------------------

func open(tab: String = "keys") -> void:
	"""Open on `tab` ("keys", "terms" or "orders"), the filter cleared. The keys
	are read live from the binding registry, so a rebinding shows here."""
	if _root == null:
		return
	_tab = tab if tab in TABS else TAB_KEYS
	_filter.text = ""
	_fit()
	var was_open: bool = visible
	show()
	_refresh_tabs()
	_render()
	_scroll.scroll_vertical = 0
	if not was_open:
		AudioManager.play("book_open")
		Utils.motion_open(self)


func close() -> void:
	if not visible:
		return
	AudioManager.play("book_close")
	if _filter != null:
		_filter.release_focus()
	hide()
	closed.emit()


func is_open() -> bool:
	return visible


# --- layout -----------------------------------------------------------------

func _fit() -> void:
	"""The window's share of the view (the whole view when compact); the frame's
	margin and the page's width follow it."""
	var view: Vector2 = get_viewport().get_visible_rect().size
	var compact: bool = Utils.compact_view()
	var margin: float = 10.0 if compact else 24.0
	var w: float = view.x if compact else maxf(view.x * FULL_SHARE.x, minf(view.x, MIN_FULL_WIDTH))
	var h: float = view.y if compact else view.y * FULL_SHARE.y
	_panel.add_theme_stylebox_override("panel",
		Utils.gilt_frame(Utils.UI_POPUP_BG, Utils.UI_GOLD, Utils.FRAME_WINDOW, margin))
	_panel.custom_minimum_size = Vector2(w, h)
	_panel.size = Vector2(w, h)
	# The page is the window less the frame, its margins and the scroll bar.
	_page_width = maxf(w - 2.0 * margin - 20.0, 200.0)


func _on_viewport_resized() -> void:
	if not visible:
		return
	var held: int = _scroll.scroll_vertical
	_fit()
	_render()
	_scroll.scroll_vertical = held


# --- tabs and filter ----------------------------------------------------------

func _on_tab_pressed(id: String) -> void:
	if id == _tab:
		return
	AudioManager.play("page_turn")
	_tab = id
	_refresh_tabs()
	_render()
	_scroll.scroll_vertical = 0


func _refresh_tabs() -> void:
	for id in TABS:
		var btn: Button = _tab_buttons[String(id)]
		var active: bool = String(id) == _tab
		# tint first: the open tab's disabled colour is read from its font colour.
		Utils.tint_tab(btn, active)
		Utils.mark_active_tab(btn, active, _tab_strip["active"])


func _on_filter_changed(_text: String) -> void:
	_render()
	_scroll.scroll_vertical = 0


# --- the page ---------------------------------------------------------------

func _render() -> void:
	var f: String = _filter.text.strip_edges().to_lower()
	var bb: String = ""
	var shown: int = 0
	match _tab:
		TAB_TERMS:
			var out_terms: Dictionary = _page_terms(f)
			bb = String(out_terms["bb"])
			shown = int(out_terms["n"])
			_footer.text = "%d of %d entries." % [shown, CodexTerms.TERMS.size()] if f != "" \
				else "%d entries, A to Z. Type above to find one." % CodexTerms.TERMS.size()
		TAB_ORDERS:
			var out_orders: Dictionary = _page_orders(f)
			bb = String(out_orders["bb"])
			shown = int(out_orders["n"])
			_footer.text = "Orders are typed in the command window (the key above opens it); the map's clicks give the same orders."
		_:
			var out_keys: Dictionary = _page_keys(f)
			bb = String(out_keys["bb"])
			shown = int(out_keys["n"])
			_footer.text = "Rebind the listed keys in Settings, Controls. Esc, Enter and the number keys stay fixed."
	if shown == 0:
		bb = "[color=#" + Utils.COLOR_INFO + "]Nothing on this tab matches “" + _escape(_filter.text.strip_edges()) + "”.[/color]"
	_label.text = bb


func _page_keys(f: String) -> Dictionary:
	var rows_live: Array = []
	for entry in Keys.actions():
		var action: String = str(entry[0])
		var label: String = str(entry[1])
		var key_text: String = Keys.key_name(action)
		if key_text == "":
			key_text = "unbound"
		if _hit(f, [label, key_text]):
			rows_live.append([_gold(key_text), label])
	var rows_fixed: Array = []
	for entry in CodexTerms.FIXED_KEYS:
		var keys_text: String = str(entry[0])
		var does: String = str(entry[1])
		if _hit(f, [keys_text, does]):
			rows_fixed.append([_gold(keys_text), does])
	var bb: String = ""
	if not rows_live.is_empty():
		bb += Utils.bb_section("Your keys") + Utils.bb_table(["Key", "Does"], rows_live, [], [2, 6], _page_width) + "\n"
	if not rows_fixed.is_empty():
		bb += Utils.bb_section("Fixed keys and the mouse") + Utils.bb_table(["Keys", "Does"], rows_fixed, [], [2, 6], _page_width) + "\n"
	return {"bb": bb, "n": rows_live.size() + rows_fixed.size()}


func _page_terms(f: String) -> Dictionary:
	var bb: String = ""
	var n: int = 0
	for entry in CodexTerms.TERMS:
		var term: String = str(entry[0])
		var text: String = str(entry[1])
		if not _hit(f, [term, text]):
			continue
		n += 1
		bb += Utils.card_open() + Utils.HEAD_OPEN + term + Utils.HEAD_CLOSE + "\n"
		bb += "[color=#" + Utils.COLOR_TEXT + "]" + text + "[/color]" + Utils.CARD_CLOSE + "\n\n"
	return {"bb": bb, "n": n}


func _page_orders(f: String) -> Dictionary:
	var bb: String = ""
	var n: int = 0
	if f == "":
		bb += Utils.bb_section("How to give an order")
		bb += "[color=#" + Utils.COLOR_TEXT + "]" + _escape(CodexTerms.ORDER_GRAMMAR) + "[/color]\n\n"
	var rows_orders: Array = []
	for entry in CodexTerms.ORDERS:
		var verb: String = str(entry[0])
		var example: String = str(entry[1])
		var does: String = str(entry[2])
		if _hit(f, [verb, example, does]):
			rows_orders.append([verb, _gold("“" + example + "”"), does])
	if not rows_orders.is_empty():
		bb += Utils.bb_section("Orders to a marshal") + Utils.bb_table(["Order", "Say", "What happens"], rows_orders, [], [2, 4, 6], _page_width) + "\n"
		n += rows_orders.size()
	var rows_bare: Array = []
	for entry in CodexTerms.BARE:
		var cmd: String = str(entry[0])
		var does_bare: String = str(entry[1])
		if _hit(f, [cmd, does_bare]):
			rows_bare.append([_gold(cmd), does_bare])
	if not rows_bare.is_empty():
		bb += Utils.bb_section("Commands with no marshal") + Utils.bb_table(["Say", "What happens"], rows_bare, [], [2, 6], _page_width) + "\n"
		n += rows_bare.size()
	var rows_q: Array = []
	for entry in CodexTerms.QUESTIONS:
		var q: String = str(entry[0])
		var answers: String = str(entry[1])
		if _hit(f, [q, answers, "ask Berthier question"]):
			rows_q.append([_gold("“" + q + "”"), answers])
	if not rows_q.is_empty():
		bb += Utils.bb_section("Ask Berthier — free, no action spent") + Utils.bb_table(["Ask", "You learn"], rows_q, [], [4, 5], _page_width) + "\n"
		n += rows_q.size()
	return {"bb": bb, "n": n}


# --- small helpers ----------------------------------------------------------

func _gold(text: String) -> String:
	return "[color=#" + Utils.COLOR_GOLD + "]" + _escape(text) + "[/color]"


func _escape(text: String) -> String:
	"""Typed text (the filter's words, a key's name) never opens a BBCode tag."""
	return text.replace("[", "[lb]")


func _hit(f: String, parts: Array) -> bool:
	if f == "":
		return true
	for p in parts:
		if str(p).to_lower().find(f) >= 0:
			return true
	return false


# --- input ------------------------------------------------------------------

func _on_overlay_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed:
		close()


func _input(event: InputEvent) -> void:
	if not visible:
		return
	if not (event is InputEventKey) or not event.pressed:
		return
	var key := event as InputEventKey
	if key.keycode == KEY_ESCAPE:
		if not key.echo:
			# Esc in the field clears it first; then the book closes.
			if _filter.has_focus() and _filter.text != "":
				_filter.text = ""
				_on_filter_changed("")
			else:
				close()
		get_viewport().set_input_as_handled()
		return
	# The page scrolls from the keyboard while the field does not hold the caret.
	if _filter.has_focus():
		return
	match key.keycode:
		KEY_UP:
			_scroll.scroll_vertical = maxi(_scroll.scroll_vertical - SCROLL_STEP, 0)
		KEY_DOWN:
			_scroll.scroll_vertical += SCROLL_STEP
		KEY_PAGEUP:
			_scroll.scroll_vertical = maxi(_scroll.scroll_vertical - int(_scroll.size.y) + SCROLL_STEP, 0)
		KEY_PAGEDOWN:
			_scroll.scroll_vertical += int(_scroll.size.y) - SCROLL_STEP
		_:
			return
	get_viewport().set_input_as_handled()
