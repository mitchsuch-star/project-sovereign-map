extends CanvasLayer
class_name SaveDialog

# =============================================================================
# INK & IRON - The Save Dialog (Session UI-5, November 12, 2026)
# =============================================================================
# Pause menu -> "Save Game...". A name field, the slots on disk (newest first)
# with their date, nation and the time saved, an overwrite confirm, and Delete
# behind a confirm. It talks to the backend itself through the api client
# (the `api_client` group main.gd adds), and tells main.gd only the result:
#   saved(save_name, calendar_label)  - the file is written
#   closed                            - the dialog is gone (saved or not)
#
# The dialog also owns the ROW LOOK that the load dialog shares (the static
# `build_row`), so the two lists can never drift.
#
# The slot rule is the backend's (`save_manager.save_game`): the file is
# "<name with every character that is not alphanumeric, '-', ' ' or '_' made
# '_'>.json" - so two different names can write ONE file, and a name is an
# existing slot when its slug (compared lowercase: the saves folder lives on a
# case-insensitive disk) equals a listed file's stem.
# =============================================================================

signal saved(save_name: String, calendar_label: String)
signal closed

const AUTOSAVE_FILENAME := "autosave.json"
const MONTHS := ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
const PANEL_HALF_W := 290.0
const PANEL_HALF_H := 230.0

var _api: Node = null
var _overlay: ColorRect
var _panel: PanelContainer
var _vbox: VBoxContainer
var _name_field: LineEdit
var _scroll: ScrollContainer
var _list: VBoxContainer
var _error_label: Label
var _confirm_box: VBoxContainer
var _confirm_label: Label
var _confirm_yes: Button
var _confirm_no: Button
var _button_row: HBoxContainer
var _save_button: Button
var _cancel_button: Button
var _slots: Dictionary = {}          # slug -> {"name": String, "date": String}
var _confirm_kind := ""              # "" | "overwrite" | "delete"
var _confirm_filename := ""
var _confirm_name := ""
var _busy := false


func _ready() -> void:
	layer = 113
	_build()
	hide()


# --- The slot rule and the row words (static: the load dialog calls them) ----

static func slug_of(save_name: String) -> String:
	"""The backend's file stem for `save_name`, lowercased for comparison.
	save_manager.save_game keeps a character that is alphanumeric or one of
	'-', ' ', '_' and writes '_' for every other."""
	# UI-5 review: Python's str.isalnum() keeps a LETTER or a digit above 127
	# (é, ü, ß) but not punctuation there (·, —, «); a cased letter is told by
	# its case pair, the rest written "_" as the backend writes them.
	var out := ""
	for i in range(save_name.length()):
		var c := save_name.substr(i, 1)
		var code: int = save_name.unicode_at(i)
		var ascii_alnum: bool = (code >= 48 and code <= 57) or (code >= 65 and code <= 90) \
			or (code >= 97 and code <= 122)
		var wide_letter: bool = code > 127 and c.to_upper() != c.to_lower()
		var keep: bool = ascii_alnum or wide_letter or c == "-" or c == " " or c == "_"
		out += c if keep else "_"
	return out.to_lower()


static func date_of(meta: Dictionary, turn_text: String = "") -> String:
	"""The save's calendar date; a save without one reads 'Turn N'."""
	var label: String = str(meta.get("calendar_label") if meta.get("calendar_label") != null else "")
	if label.strip_edges() != "":
		return label.strip_edges()
	if turn_text != "":
		return "Turn " + turn_text
	var turn_val = meta.get("turn")
	if turn_val != null:
		return "Turn " + str(int(turn_val))
	return "Turn ?"


static func saved_words(iso: String) -> String:
	"""'today 21:14' / 'yesterday 21:14' / '12 Nov' - the ISO UTC stamp in the
	player's local time. An unreadable stamp reads as nothing."""
	if iso.length() < 19:
		return ""
	var stamp := iso.substr(0, 19).replace(" ", "T")
	var unix: int = int(Time.get_unix_time_from_datetime_string(stamp))
	if unix <= 0:
		return ""
	var zone: Dictionary = Time.get_time_zone_from_system()
	var bias: int = int(zone.get("bias", 0)) * 60
	var local: Dictionary = Time.get_datetime_dict_from_unix_time(unix + bias)
	var now: Dictionary = Time.get_datetime_dict_from_unix_time(int(Time.get_unix_time_from_system()) + bias)
	var yesterday: Dictionary = Time.get_datetime_dict_from_unix_time(int(Time.get_unix_time_from_system()) + bias - 86400)
	var hhmm := "%02d:%02d" % [int(local.get("hour", 0)), int(local.get("minute", 0))]
	if _same_day(local, now):
		return "today " + hhmm
	if _same_day(local, yesterday):
		return "yesterday " + hhmm
	return "%d %s" % [int(local.get("day", 1)), MONTHS[clampi(int(local.get("month", 1)) - 1, 0, 11)]]


static func _same_day(a: Dictionary, b: Dictionary) -> bool:
	return int(a.get("year", 0)) == int(b.get("year", -1)) and int(a.get("month", 0)) == int(b.get("month", -1)) \
		and int(a.get("day", 0)) == int(b.get("day", -1))


static func nation_of(meta: Dictionary) -> String:
	var nation: String = str(meta.get("player_nation") if meta.get("player_nation") != null else "")
	return Utils.display_nation_name(nation) if nation != "" else ""


static func _row_style(hover: bool) -> StyleBox:
	# The tokens, not one-off greys (the R4 consistency census): a row on the
	# popup's own fill, a hovered one on the panel fill.
	var fill: Color = Utils.UI_POPUP_BG if not hover else Utils.UI_PANEL_BG
	var tone: Color = Utils.UI_GOLD if hover else Color(Utils.UI_GOLD, 0.45)
	return Utils.gilt_frame(fill, tone, Utils.FRAME_HAIRLINE, 8.0)


static func build_row(save_data: Dictionary, turn_text: String, on_pick: Callable,
		on_delete: Callable = Callable(), seed_in_hover: bool = false) -> PanelContainer:
	"""One save as a row card: its name, its date and nation, the time it was
	saved, and (when `on_delete` is valid and it is not the autosave) a Delete
	button. Clicking the row (or Enter on it) calls on_pick(filename, name);
	Delete calls on_delete(filename, name, date). The campaign seed rides only
	the row's hover, and only when asked."""
	var meta: Dictionary = save_data.get("metadata", {}) if save_data.get("metadata") is Dictionary else {}
	var filename: String = str(save_data.get("filename") if save_data.get("filename") != null else "")
	var raw_name = meta.get("save_name")
	var display_name: String = str(raw_name) if raw_name != null else "Unknown"
	var date: String = date_of(meta, turn_text)
	var nation: String = nation_of(meta)
	var when: String = saved_words(str(meta.get("saved_at") if meta.get("saved_at") != null else ""))

	var row := PanelContainer.new()
	row.name = "SaveRow"
	row.focus_mode = Control.FOCUS_ALL
	row.mouse_filter = Control.MOUSE_FILTER_STOP
	row.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	row.add_theme_stylebox_override("panel", _row_style(false))
	row.set_meta("save_filename", filename)
	row.set_meta("save_name", display_name)
	row.set_meta("save_date", date)
	var tip := ""
	if seed_in_hover:
		var row_seed: String = str(meta.get("campaign_seed") if meta.get("campaign_seed") != null else "")
		if row_seed != "":
			tip = "Campaign seed '%s'" % row_seed
	row.tooltip_text = tip

	var hb := HBoxContainer.new()
	hb.add_theme_constant_override("separation", 12)
	hb.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_child(hb)

	var left := VBoxContainer.new()
	left.add_theme_constant_override("separation", 2)
	left.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	left.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hb.add_child(left)
	var name_label := Label.new()
	name_label.text = display_name
	name_label.theme_type_variation = &"BodyLarge"
	name_label.add_theme_color_override("font_color", Utils.UI_GOLD_BRIGHT)
	name_label.clip_text = true
	name_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	left.add_child(name_label)
	var detail := date if nation == "" else "%s · %s" % [date, nation]
	var detail_label := Label.new()
	detail_label.text = detail
	detail_label.theme_type_variation = &"Caption"
	detail_label.add_theme_color_override("font_color", Utils.UI_TEXT_DIM)
	detail_label.clip_text = true
	detail_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	left.add_child(detail_label)

	if when != "":
		var when_label := Label.new()
		when_label.text = when
		when_label.theme_type_variation = &"Caption"
		when_label.add_theme_color_override("font_color", Utils.UI_TEXT_DIM)
		when_label.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		when_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
		hb.add_child(when_label)

	if on_delete.is_valid() and filename != AUTOSAVE_FILENAME:
		var del := Button.new()
		del.name = "DeleteButton"
		del.text = "Delete"
		del.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		del.set_meta("no_click_sfx", true)   # the crumple is its own cue
		del.tooltip_text = "Delete this save"
		del.pressed.connect(_on_delete_pressed.bind(on_delete, filename, display_name, date))
		hb.add_child(del)

	row.gui_input.connect(_on_row_input.bind(on_pick, filename, display_name))
	row.mouse_entered.connect(_on_row_hover.bind(row.get_instance_id(), true))
	row.mouse_exited.connect(_on_row_hover.bind(row.get_instance_id(), false))
	row.focus_entered.connect(_on_row_hover.bind(row.get_instance_id(), true))
	row.focus_exited.connect(_on_row_hover.bind(row.get_instance_id(), false))
	return row


static func _on_row_hover(row_id: int, hover: bool) -> void:
	var row := instance_from_id(row_id) as Control
	if row != null:
		row.add_theme_stylebox_override("panel", _row_style(hover))


static func _on_row_input(event: InputEvent, on_pick: Callable, filename: String, display_name: String) -> void:
	var pick := false
	if event is InputEventMouseButton:
		var mb := event as InputEventMouseButton
		pick = mb.pressed and mb.button_index == MOUSE_BUTTON_LEFT
	elif event is InputEventKey:
		var key := event as InputEventKey
		pick = key.pressed and not key.echo and (key.keycode == KEY_ENTER or key.keycode == KEY_KP_ENTER or key.keycode == KEY_SPACE)
	if pick and on_pick.is_valid():
		on_pick.call(filename, display_name)


static func _on_delete_pressed(on_delete: Callable, filename: String, display_name: String, date: String) -> void:
	if on_delete.is_valid():
		on_delete.call(filename, display_name, date)


# --- Building the window -----------------------------------------------------

func _build() -> void:
	_overlay = ColorRect.new()
	_overlay.name = "BackgroundOverlay"
	_overlay.set_anchors_preset(Control.PRESET_FULL_RECT)
	_overlay.color = Color(0, 0.05, 0.1, 0.7)
	_overlay.gui_input.connect(_on_overlay_input)
	add_child(_overlay)

	_panel = PanelContainer.new()
	_panel.name = "PanelContainer"
	_panel.set_anchors_preset(Control.PRESET_CENTER)
	_panel.offset_left = -PANEL_HALF_W
	_panel.offset_right = PANEL_HALF_W
	_panel.offset_top = -PANEL_HALF_H
	_panel.offset_bottom = PANEL_HALF_H
	_panel.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_panel.grow_vertical = Control.GROW_DIRECTION_BOTH
	_panel.add_theme_stylebox_override("panel", Utils.gilt_frame(Utils.UI_POPUP_BG, Utils.UI_GOLD, Utils.FRAME_WINDOW, 20.0))
	add_child(_panel)

	_vbox = VBoxContainer.new()
	_vbox.add_theme_constant_override("separation", 10)
	_panel.add_child(_vbox)

	var title := Label.new()
	title.name = "TitleLabel"
	title.text = "Save the campaign"
	title.theme_type_variation = &"DialogTitle"
	title.add_theme_color_override("font_color", Utils.UI_GOLD)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_vbox.add_child(title)

	var name_row := HBoxContainer.new()
	name_row.add_theme_constant_override("separation", 8)
	_vbox.add_child(name_row)
	var name_caption := Label.new()
	name_caption.text = "Name"
	name_caption.theme_type_variation = &"Caption"
	name_caption.add_theme_color_override("font_color", Utils.UI_TEXT_DIM)
	name_caption.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	name_row.add_child(name_caption)
	_name_field = LineEdit.new()
	_name_field.name = "NameField"
	_name_field.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_name_field.max_length = 60
	_name_field.placeholder_text = "Name this save"
	_name_field.text_changed.connect(_on_name_changed)
	_name_field.text_submitted.connect(_on_name_submitted)
	name_row.add_child(_name_field)

	_scroll = ScrollContainer.new()
	_scroll.name = "ScrollContainer"
	_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_vbox.add_child(_scroll)
	_list = VBoxContainer.new()
	_list.name = "SavesContainer"
	_list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_list.add_theme_constant_override("separation", 6)
	_scroll.add_child(_list)

	_error_label = Label.new()
	_error_label.name = "ErrorLabel"
	_error_label.theme_type_variation = &"Caption"
	_error_label.add_theme_color_override("font_color", Utils.UI_ALERT_TEXT)
	_error_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_error_label.visible = false
	_vbox.add_child(_error_label)

	_confirm_box = VBoxContainer.new()
	_confirm_box.name = "ConfirmBox"
	_confirm_box.add_theme_constant_override("separation", 8)
	_confirm_box.visible = false
	_vbox.add_child(_confirm_box)
	_confirm_label = Label.new()
	_confirm_label.theme_type_variation = &"BodyLarge"
	_confirm_label.add_theme_color_override("font_color", Utils.UI_GOLD_BRIGHT)
	_confirm_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_confirm_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_confirm_box.add_child(_confirm_label)
	var confirm_row := HBoxContainer.new()
	confirm_row.alignment = BoxContainer.ALIGNMENT_CENTER
	confirm_row.add_theme_constant_override("separation", 12)
	_confirm_box.add_child(confirm_row)
	_confirm_yes = Button.new()
	_confirm_yes.name = "ConfirmYesButton"
	_confirm_yes.custom_minimum_size = Vector2(120, 0)
	_confirm_yes.set_meta("no_click_sfx", true)
	_confirm_yes.pressed.connect(_on_confirm_yes)
	confirm_row.add_child(_confirm_yes)
	_confirm_no = Button.new()
	_confirm_no.name = "ConfirmNoButton"
	_confirm_no.custom_minimum_size = Vector2(120, 0)
	_confirm_no.pressed.connect(_on_confirm_no)
	confirm_row.add_child(_confirm_no)

	_button_row = HBoxContainer.new()
	_button_row.alignment = BoxContainer.ALIGNMENT_CENTER
	_button_row.add_theme_constant_override("separation", 12)
	_vbox.add_child(_button_row)
	_save_button = Button.new()
	_save_button.name = "SaveButton"
	_save_button.text = "Save"
	_save_button.theme_type_variation = &"PrimaryButton"
	_save_button.custom_minimum_size = Vector2(140, 0)
	_save_button.set_meta("no_click_sfx", true)   # the quill and the seal are its cues
	_save_button.pressed.connect(_on_save_pressed)
	_button_row.add_child(_save_button)
	_cancel_button = Button.new()
	_cancel_button.name = "CancelButton"
	_cancel_button.text = "Cancel"
	_cancel_button.custom_minimum_size = Vector2(120, 0)
	_cancel_button.set_meta("no_click_sfx", true)  # closing is the book_close cue
	_cancel_button.pressed.connect(close)
	_button_row.add_child(_cancel_button)


# --- Open / close ------------------------------------------------------------

func open(default_name: String) -> void:
	"""Show the dialog with `default_name` in the name field and the slots listed."""
	_api = get_tree().get_first_node_in_group("api_client")
	_busy = false
	_hide_confirm()
	_set_error("")
	_name_field.text = default_name
	_scroll.custom_minimum_size.y = 110.0 if Utils.compact_view() else 220.0
	for child in _list.get_children():
		child.queue_free()
	_slots.clear()
	_refresh_save_state()
	show()
	AudioManager.play("book_open")
	Utils.clamp_centered_panel(_panel)
	_name_field.grab_focus()
	_name_field.select_all()
	if _api == null:
		_set_error("The save list is not available just now.")
	else:
		_api.list_saves(_on_saves_listed)


func close() -> void:
	if not visible:
		return
	AudioManager.play("book_close")
	hide()
	closed.emit()


func _on_overlay_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and (event as InputEventMouseButton).pressed:
		close()


func _unhandled_input(event: InputEvent) -> void:
	if not visible:
		return
	if event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		if _confirm_box.visible:
			_on_confirm_no()
		else:
			close()


# --- The list ----------------------------------------------------------------

func _on_saves_listed(response) -> void:
	if not visible:
		return
	for child in _list.get_children():
		child.queue_free()
	_slots.clear()
	var saves = response.get("saves") if response is Dictionary else null
	if not (saves is Array):
		_set_error("The save list could not be read.")
		return
	for save_data in saves:
		if not (save_data is Dictionary):
			continue
		var filename: String = str(save_data.get("filename") if save_data.get("filename") != null else "")
		var meta: Dictionary = save_data.get("metadata", {}) if save_data.get("metadata") is Dictionary else {}
		var raw_name = meta.get("save_name")
		var display_name: String = str(raw_name) if raw_name != null else filename.get_basename()
		_slots[filename.get_basename().to_lower()] = {"name": display_name, "date": date_of(meta)}
		_list.add_child(build_row(save_data, "", _on_row_picked, _on_delete_asked, false))
	var damaged = response.get("damaged", []) if response is Dictionary else []
	if damaged is Array:
		for bad in damaged:
			if bad is Dictionary:
				var stem: String = str(bad.get("filename", "")).get_basename().to_lower()
				if stem != "":
					_slots[stem] = {"name": str(bad.get("filename", "")), "date": "damaged"}
	if saves.is_empty():
		var empty := Label.new()
		empty.text = "No saves yet."
		empty.theme_type_variation = &"Caption"
		empty.add_theme_color_override("font_color", Utils.UI_HINT_GREY)
		_list.add_child(empty)
	_refresh_save_state()


func _on_row_picked(_filename: String, display_name: String) -> void:
	if _busy:
		return
	_name_field.text = display_name
	_name_field.caret_column = display_name.length()
	_set_error("")
	_refresh_save_state()
	_name_field.grab_focus()


func _on_name_changed(_text: String) -> void:
	_set_error("")
	_refresh_save_state()


func _on_name_submitted(_text: String) -> void:
	if not _save_button.disabled:
		_on_save_pressed()


func _refresh_save_state() -> void:
	var typed := _name_field.text.strip_edges()
	if typed == "":
		Utils.set_available(_save_button, false, "", "Name the save first.")
	elif slug_of(typed) == AUTOSAVE_FILENAME.get_basename():
		Utils.set_available(_save_button, false, "", "That name belongs to the autosave. Choose another.")
	elif _busy:
		Utils.set_available(_save_button, false, "", "Saving…")
	else:
		Utils.set_available(_save_button, true, "", "")


# --- Save --------------------------------------------------------------------

func _on_save_pressed() -> void:
	var typed := _name_field.text.strip_edges()
	if typed == "" or _busy:
		return
	var slot: Variant = _slots.get(slug_of(typed))
	if slot is Dictionary:
		var slot_dict: Dictionary = slot
		_show_confirm("overwrite", "Overwrite %s (%s)?" % [str(slot_dict.get("name", typed)), str(slot_dict.get("date", ""))],
			"Overwrite", "Cancel", "", typed)
		return
	_do_save(typed)


func _do_save(save_name: String) -> void:
	if _api == null:
		_set_error("The campaign cannot be saved just now.")
		return
	_busy = true
	_set_error("")
	_refresh_save_state()
	AudioManager.play("quill_sign")
	_api.save_game(save_name, _on_save_result.bind(save_name))


func _on_save_result(response, save_name: String) -> void:
	_busy = false
	var ok: bool = response is Dictionary and bool(response.get("success", false))
	if not ok:
		var msg := "The campaign could not be saved."
		if response is Dictionary and response.get("message") != null and str(response.get("message")) != "":
			msg = str(response.get("message"))
		_set_error(msg)
		_refresh_save_state()
		return
	AudioManager.play("wax_seal")
	# The date for the toast: the slot's own metadata, read back (the save reply
	# carries no calendar label).
	if _api != null:
		_api.list_saves(_on_saved_listed.bind(save_name))
	else:
		_finish_saved(save_name, "")


func _on_saved_listed(response, save_name: String) -> void:
	var label := ""
	var saves = response.get("saves") if response is Dictionary else null
	if saves is Array:
		var want := slug_of(save_name)
		for save_data in saves:
			if save_data is Dictionary:
				var stem: String = str(save_data.get("filename", "")).get_basename().to_lower()
				if stem == want and save_data.get("metadata") is Dictionary:
					label = date_of(save_data.get("metadata"))
	_finish_saved(save_name, label)


func _finish_saved(save_name: String, calendar_label: String) -> void:
	ToastLayer.say("Saved · " + calendar_label if calendar_label != "" else "Saved", "")
	if visible:
		hide()
		closed.emit()
	saved.emit(save_name, calendar_label)


# --- Delete ------------------------------------------------------------------

func _on_delete_asked(filename: String, display_name: String, _date: String) -> void:
	if _busy:
		return
	_show_confirm("delete", "Delete %s? It cannot be undone." % display_name, "Delete", "Keep", filename, display_name)


func _do_delete(filename: String) -> void:
	if _api == null:
		_set_error("The save cannot be deleted just now.")
		return
	_busy = true
	AudioManager.play("paper_crumple")
	_api.delete_save(filename, _on_delete_result)


func _on_delete_result(response) -> void:
	_busy = false
	var ok: bool = response is Dictionary and bool(response.get("success", false))
	if not ok:
		var msg := "The save could not be deleted."
		if response is Dictionary and response.get("message") != null and str(response.get("message")) != "":
			msg = str(response.get("message"))
		_set_error(msg)
		_refresh_save_state()
		return
	if _api != null and visible:
		_api.list_saves(_on_saves_listed)
	_refresh_save_state()


# --- The inline confirm ------------------------------------------------------

func _show_confirm(kind: String, text: String, yes_text: String, no_text: String,
		filename: String, display_name: String) -> void:
	_confirm_kind = kind
	_confirm_filename = filename
	_confirm_name = display_name
	_confirm_label.text = text
	_confirm_yes.text = yes_text
	_confirm_no.text = no_text
	_confirm_box.visible = true
	_button_row.visible = false
	_name_field.editable = false
	if Utils.compact_view():
		_scroll.visible = false
	AudioManager.play("question")
	Utils.clamp_centered_panel(_panel)
	_confirm_no.grab_focus()


func _hide_confirm() -> void:
	_confirm_kind = ""
	_confirm_box.visible = false
	_button_row.visible = true
	_name_field.editable = true
	_scroll.visible = true


func _on_confirm_yes() -> void:
	var kind := _confirm_kind
	var filename := _confirm_filename
	var display_name := _confirm_name
	_hide_confirm()
	if kind == "overwrite":
		_do_save(display_name)
	elif kind == "delete":
		_do_delete(filename)


func _on_confirm_no() -> void:
	AudioManager.play("back")
	_hide_confirm()
	_name_field.grab_focus()


func _set_error(text: String) -> void:
	_error_label.text = text
	_error_label.visible = text != ""
