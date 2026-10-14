extends VBoxContainer
class_name SettingsPanel

# =============================================================================
# INK & IRON — Shared Settings surface (Main Menu pass, position 6)
# =============================================================================
# ONE settings component, embedded by BOTH the pause menu (its old code-built
# settings box promoted here) and the Main Menu's Settings view — so the two
# surfaces can never drift. Sections:
#   • INTERFACE — the global Interface Scale slider (UI-2 semantics: live-apply
#     every step, persist on drag end) + reset + hint
#   • SOUND     — Battle sounds toggle + the four bus volume sliders
#   • SMARTER PARSING — the player's own Anthropic API key (BYOK). Stored
#     locally in user://ui_settings.cfg, pushed to the player's OWN backend
#     (/config/llm), which checks it with Anthropic and sends hard phrasings
#     to Anthropic with it. An empty key reverts the backend to its launcher
#     configuration. C1 (the release build, Sept 23 2026): the copy says where
#     the key goes, and the status line says what the check found.
#   • SPOKEN ORDERS — the Voice-to-Text v1 hint (Road-to-EA position 8):
#     OS dictation (Win+H) into the command line. Display-only by design —
#     dictation types text; the SAME deterministic parser reads it (GR6).
#     Embedded STT (whisper.cpp) is deferred behind the ROADMAP row-8 re-open
#     condition (Round-0 tester usage).
#   • CREDITS   — the CC-BY obligations + courtesy lines
#
# The host applies scale itself (main.gd owns map compensation in-game; the
# menu applies content_scale_factor directly) via the ui_scale_changed signal —
# the same contract pause_menu.gd exposed before the promotion.
# Display-only (Golden Rule 6): nothing here reads or writes game state.
# =============================================================================

signal ui_scale_changed(value: float, persist: bool)
# UXR-1b (October 9, 2026): the panel asks its host to open the sizing card
# ("Preview with a sample…" — main_menu.gd / main.gd each hold a ScaleCard),
# and tells it a Reset layout happened (the terminal's footprint re-fits).
signal size_card_requested
signal layout_reset
# UXR-D1 (Pre-Deploy S9b): the panel re-themes the type sizes itself (the
# theme is global); the host refits its open surfaces on the live-refit road.
signal text_size_changed(value: float, persist: bool)
# UXR-D3 (Pre-Deploy S9b): HUD width changed; the campaign's host refits the
# HUD to the band (the menu has no HUD).
signal hud_width_changed(width: String)

# Golden Rule 7: same origin as api_client.gd — one source, env-overridable.
var BACKEND_URL: String = Utils.backend_url()

# UXR-1b: the DISPLAY section's choices, by UiSettings key.
const _WINDOW_MODE_LABELS := {
	"maximized": "Maximized (the default)",
	"fullscreen": "Fullscreen",
	"borderless": "Borderless window",
	"windowed": "Windowed",
}
const _HUD_WIDTH_LABELS := {
	"full": "Full (the default)",
	"centred": "Centred (a 2560-px band)",
}
const _BODY_FONT_LABELS := {
	"garamond": "Garamond (the default)",
	"plain": "Plain (Source Sans)",
}

var _scale_dragging := false
var _scale_slider: HSlider
var _scale_value: Label
var _text_dragging := false
var _text_slider: HSlider
var _text_value: Label
var _fit_button: Button
var _window_mode: OptionButton
var _window_size: OptionButton
var _window_size_row: HBoxContainer
var _body_font: OptionButton
var _hud_width: OptionButton
var _contrast_toggle: CheckButton
var _volume_sliders: Dictionary = {}   # bus name -> HSlider
var _battle_toggle: CheckButton
var _key_edit: LineEdit
# UXR3-68 / 69 (Pre-Deploy S12): honest availability — Connect needs a key on
# the line, Disconnect a key connected.
var _connect_btn: Button
var _disconnect_btn: Button
const CONNECT_TIP_OFF := "Paste an Anthropic API key above first"
const DISCONNECT_TIP_OFF := "No key is connected"
var _parser_status: Label
var _http: HTTPRequest
var _http_busy := false


func _ready() -> void:
	add_theme_constant_override("separation", 6)
	_build_display_section()
	_build_interface_section()
	_build_sound_section()
	_build_parser_section()
	_build_voice_section()
	_build_controls_section()
	_build_credits_section()
	_http = HTTPRequest.new()
	_http.timeout = 6.0
	add_child(_http)
	_http.request_completed.connect(_on_http_completed)


func refresh() -> void:
	"""Re-sync every control from the persisted settings + backend state.
	Hosts call this on open — the command-window Text Size buttons write the
	same UiSettings scale, so re-reading keeps the slider honest."""
	if _scale_slider:
		_scale_slider.set_value_no_signal(UiSettings.get_ui_scale())
		_update_scale_value_label(UiSettings.get_ui_scale())
	if _text_slider:
		_text_slider.set_value_no_signal(UiSettings.get_text_size())
		_update_text_value_label(UiSettings.get_text_size())
	_refresh_display_controls()
	for bus_name in _volume_sliders:
		_volume_sliders[bus_name].set_value_no_signal(AudioManager.get_bus_volume(bus_name))
	if _battle_toggle:
		_battle_toggle.set_pressed_no_signal(UiSettings.get_battle_sfx())
	if _key_edit:
		_key_edit.text = ""
		_key_edit.placeholder_text = _key_placeholder()
	_show_stored_parser_state()
	_fetch_parser_status()


# ── DISPLAY (UXR-1b) ────────────────────────────────────────────────────────

func _build_display_section() -> void:
	_add_header("DISPLAY")
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	var lbl := Label.new()
	lbl.text = "Window"
	lbl.theme_type_variation = &"Caption"
	lbl.custom_minimum_size.x = 72
	row.add_child(lbl)
	_window_mode = OptionButton.new()
	_window_mode.name = "WindowModeOption"
	for i in range(UiSettings.WINDOW_MODES.size()):
		var mode: String = UiSettings.WINDOW_MODES[i]
		_window_mode.add_item(str(_WINDOW_MODE_LABELS.get(mode, mode)), i)
	_window_mode.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_window_mode.item_selected.connect(_on_window_mode_selected)
	row.add_child(_window_mode)
	add_child(row)

	_window_size_row = HBoxContainer.new()
	_window_size_row.add_theme_constant_override("separation", 10)
	var size_lbl := Label.new()
	size_lbl.text = "Size"
	size_lbl.theme_type_variation = &"Caption"
	size_lbl.custom_minimum_size.x = 72
	_window_size_row.add_child(size_lbl)
	_window_size = OptionButton.new()
	_window_size.name = "WindowSizeOption"
	_window_size.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_window_size.item_selected.connect(_on_window_size_selected)
	_window_size_row.add_child(_window_size)
	add_child(_window_size_row)
	# UXR-D3: HUD width — Full, or the HUD confined to a central band.
	var hud_row := HBoxContainer.new()
	hud_row.add_theme_constant_override("separation", 10)
	var hud_lbl := Label.new()
	hud_lbl.text = "HUD width"
	hud_lbl.theme_type_variation = &"Caption"
	hud_lbl.custom_minimum_size.x = 72
	hud_row.add_child(hud_lbl)
	_hud_width = OptionButton.new()
	_hud_width.name = "HudWidthOption"
	for i in range(UiSettings.HUD_WIDTHS.size()):
		var width_key: String = UiSettings.HUD_WIDTHS[i]
		_hud_width.add_item(str(_HUD_WIDTH_LABELS.get(width_key, width_key)), i)
	_hud_width.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_hud_width.item_selected.connect(_on_hud_width_selected)
	hud_row.add_child(_hud_width)
	add_child(hud_row)
	_add_hint("Maximized is the game's own boot. Fullscreen takes the whole screen; "
		+ "a borderless window fills it without a frame; Windowed uses the size "
		+ "chosen above, centred. On a very wide screen, HUD width: Centred gathers "
		+ "the command window, the notices, the top bar and the war panel into the "
		+ "middle 2560 px while the map stays full width.")
	_refresh_display_controls()


func _refresh_display_controls() -> void:
	if _window_mode == null:
		return
	var mode := UiSettings.get_window_mode()
	_window_mode.select(maxi(UiSettings.WINDOW_MODES.find(mode), 0))
	# The size choices that fit THIS screen (the label names the native size).
	var screen := DisplayServer.screen_get_size(DisplayServer.window_get_current_screen())
	_window_size.clear()
	var choices: Array = Utils.window_size_choices(screen)
	var stored := UiSettings.get_window_size()
	var selected := 0
	for i in range(choices.size()):
		var choice: String = str(choices[i])
		var label := choice
		if choice == "native":
			label = "This screen (%dx%d)" % [screen.x, screen.y]
		_window_size.add_item(label, i)
		_window_size.set_item_metadata(i, choice)
		if choice == stored:
			selected = i
	_window_size.select(selected)
	_window_size_row.visible = mode == "windowed"
	if _body_font != null:
		_body_font.select(maxi(UiSettings.BODY_FONTS.find(UiSettings.get_body_font()), 0))
	if _hud_width != null:
		_hud_width.select(maxi(UiSettings.HUD_WIDTHS.find(UiSettings.get_hud_width()), 0))
	if _contrast_toggle != null:
		_contrast_toggle.set_pressed_no_signal(UiSettings.get_high_contrast())
	if _fit_button != null:
		_fit_button.text = "Size for this screen (%d%%)" % int(round(UiSettings.derive_default_ui_scale() * 100.0))


func _on_window_mode_selected(index: int) -> void:
	var mode: String = UiSettings.WINDOW_MODES[clampi(index, 0, UiSettings.WINDOW_MODES.size() - 1)]
	UiSettings.set_window_mode(mode)
	_window_size_row.visible = mode == "windowed"
	Utils.apply_window_settings(get_window())


func _on_hud_width_selected(index: int) -> void:
	var width: String = UiSettings.HUD_WIDTHS[clampi(index, 0, UiSettings.HUD_WIDTHS.size() - 1)]
	UiSettings.set_hud_width(width)
	hud_width_changed.emit(width)


func _on_window_size_selected(index: int) -> void:
	var choice := str(_window_size.get_item_metadata(index))
	UiSettings.set_window_size(choice)
	Utils.apply_window_settings(get_window())


# ── INTERFACE ───────────────────────────────────────────────────────────────

func _build_interface_section() -> void:
	_add_header("INTERFACE")
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	_scale_slider = HSlider.new()
	_scale_slider.min_value = UiSettings.MIN_UI_SCALE
	_scale_slider.max_value = UiSettings.MAX_UI_SCALE
	_scale_slider.step = UiSettings.UI_SCALE_STEP
	_scale_slider.custom_minimum_size = Vector2(180, 0)
	_scale_slider.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_scale_slider.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	_scale_slider.set_value_no_signal(UiSettings.get_ui_scale())
	_scale_slider.value_changed.connect(_on_scale_changed)
	_scale_slider.drag_started.connect(func(): _scale_dragging = true)
	_scale_slider.drag_ended.connect(_on_scale_drag_ended)
	row.add_child(_scale_slider)
	_scale_value = Label.new()
	_scale_value.custom_minimum_size = Vector2(52, 0)
	_scale_value.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_scale_value.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_scale_value.add_theme_color_override("font_color", Color(0.9, 0.85, 0.7))
	_scale_value.theme_type_variation = &"Caption"
	row.add_child(_scale_value)
	add_child(row)
	_update_scale_value_label(UiSettings.get_ui_scale())

	# UXR-1b: the old reset went to the 24-inch default (one hundred percent);
	# the screen's own derived size is the reset now, and the card previews
	# it with a sample.
	var buttons := HBoxContainer.new()
	buttons.add_theme_constant_override("separation", 8)
	_fit_button = Button.new()
	_fit_button.name = "SizeForScreenButton"
	_fit_button.text = "Size for this screen"
	_fit_button.custom_minimum_size = Vector2(0, 32)
	_fit_button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_fit_button.pressed.connect(_on_reset_scale)
	buttons.add_child(_fit_button)
	var preview := Button.new()
	preview.name = "PreviewSampleButton"
	preview.text = "Preview with a sample…"
	preview.custom_minimum_size = Vector2(0, 32)
	preview.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	preview.pressed.connect(func(): size_card_requested.emit())
	buttons.add_child(preview)
	add_child(buttons)

	_add_hint("Interface Scale resizes the whole interface — command window, "
		+ "ledgers, and pop-ups. Ctrl+= and Ctrl+− step it anywhere; Ctrl+0 returns "
		+ "to this screen's size; the command-window header has the same + / −.")

	# UXR-D1 (Pre-Deploy S9b): Text size — the theme's type sizes alone, the
	# panels left as they are. Live on every step, persisted when the drag
	# ends (the scale slider's own contract).
	var text_row := HBoxContainer.new()
	text_row.add_theme_constant_override("separation", 10)
	var text_lbl := Label.new()
	text_lbl.text = "Text size"
	text_lbl.theme_type_variation = &"Caption"
	text_lbl.custom_minimum_size.x = 72
	text_row.add_child(text_lbl)
	_text_slider = HSlider.new()
	_text_slider.name = "TextSizeSlider"
	_text_slider.min_value = UiSettings.MIN_TEXT_SIZE
	_text_slider.max_value = UiSettings.MAX_TEXT_SIZE
	_text_slider.step = UiSettings.TEXT_SIZE_STEP
	_text_slider.custom_minimum_size = Vector2(140, 0)
	_text_slider.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_text_slider.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	_text_slider.set_value_no_signal(UiSettings.get_text_size())
	_text_slider.value_changed.connect(_on_text_size_changed)
	_text_slider.drag_started.connect(func(): _text_dragging = true)
	_text_slider.drag_ended.connect(_on_text_size_drag_ended)
	text_row.add_child(_text_slider)
	_text_value = Label.new()
	_text_value.custom_minimum_size = Vector2(52, 0)
	_text_value.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_text_value.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_text_value.add_theme_color_override("font_color", Color(0.9, 0.85, 0.7))
	_text_value.theme_type_variation = &"Caption"
	text_row.add_child(_text_value)
	add_child(text_row)
	_update_text_value_label(UiSettings.get_text_size())
	_add_hint("Text size enlarges the words alone — the panels keep their size, "
		+ "so on a wide screen the type can grow without the chrome growing with it.")

	# UXR-1b: the body face. Garamond is the design; Plain (Source Sans 3)
	# gives a quarter more x-height at the same size.
	var font_row := HBoxContainer.new()
	font_row.add_theme_constant_override("separation", 10)
	var font_lbl := Label.new()
	font_lbl.text = "Body text"
	font_lbl.theme_type_variation = &"Caption"
	font_lbl.custom_minimum_size.x = 72
	font_row.add_child(font_lbl)
	_body_font = OptionButton.new()
	_body_font.name = "BodyFontOption"
	for i in range(UiSettings.BODY_FONTS.size()):
		var face: String = UiSettings.BODY_FONTS[i]
		_body_font.add_item(str(_BODY_FONT_LABELS.get(face, face)), i)
	_body_font.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_body_font.item_selected.connect(_on_body_font_selected)
	font_row.add_child(_body_font)
	add_child(font_row)

	# UXR-D2 (Pre-Deploy S9b): High contrast — every dim grey one step brighter.
	_contrast_toggle = CheckButton.new()
	_contrast_toggle.name = "HighContrastToggle"
	_contrast_toggle.text = "High contrast"
	_contrast_toggle.button_pressed = UiSettings.get_high_contrast()
	_contrast_toggle.toggled.connect(_on_high_contrast_toggled)
	add_child(_contrast_toggle)
	_add_hint("High contrast raises every dim grey text one step, and no hint or "
		+ "caption stays under the step that reads clearly. Text already written in "
		+ "the command window keeps its colour; everything drawn after takes the new one.")

	var reset_layout := Button.new()
	reset_layout.name = "ResetLayoutButton"
	reset_layout.text = "Reset layout"
	reset_layout.custom_minimum_size = Vector2(0, 32)
	reset_layout.pressed.connect(_on_reset_layout)
	add_child(reset_layout)
	_add_hint("Reset layout returns the scale to this screen's size, the text to "
		+ "100%, the HUD to Full, the command window and the screens to their default "
		+ "sizes and the window to Maximized. Sound, the parser key and the School's "
		+ "progress are kept.")


func _on_scale_changed(value: float) -> void:
	_update_scale_value_label(value)
	ui_scale_changed.emit(value, not _scale_dragging)


func _on_scale_drag_ended(_changed: bool) -> void:
	_scale_dragging = false
	ui_scale_changed.emit(_scale_slider.value, true)


func _on_reset_scale() -> void:
	# UXR-1b: the reset is the DERIVED size for this screen (1.0 on a 24-inch
	# 1080p, 1.40 on a 32:9 1440p), stored as auto so a monitor change
	# re-derives it; the host applies it like any slider change.
	UiSettings.set_ui_scale_auto()
	var derived := UiSettings.get_ui_scale()
	_scale_slider.set_value_no_signal(derived)
	_update_scale_value_label(derived)
	ui_scale_changed.emit(derived, false)


func _on_high_contrast_toggled(on: bool) -> void:
	UiSettings.set_high_contrast(on)
	# The tokens, the tree-wide re-tone and the node_added hook, at once.
	Utils.apply_contrast(get_tree())


func _on_text_size_changed(value: float) -> void:
	_update_text_value_label(value)
	_apply_text_size(value, not _text_dragging)


func _on_text_size_drag_ended(_changed: bool) -> void:
	_text_dragging = false
	_apply_text_size(_text_slider.value, true)


func _apply_text_size(value: float, persist: bool) -> void:
	if persist:
		UiSettings.set_text_size(value)
		Utils.apply_text_size()
	else:
		Utils.apply_text_size(value)
	text_size_changed.emit(value, persist)


func _update_text_value_label(value: float) -> void:
	if _text_value:
		_text_value.text = "%d%%" % int(round(value * 100.0))


func _on_body_font_selected(index: int) -> void:
	var face: String = UiSettings.BODY_FONTS[clampi(index, 0, UiSettings.BODY_FONTS.size() - 1)]
	UiSettings.set_body_font(face)
	Utils.apply_body_font()


func _on_reset_layout() -> void:
	UiSettings.reset_layout()
	Utils.apply_window_settings(get_window())
	Utils.apply_text_size()
	refresh()
	# Already persisted by reset_layout — the host applies the new value.
	ui_scale_changed.emit(UiSettings.get_ui_scale(), false)
	text_size_changed.emit(UiSettings.get_text_size(), false)
	hud_width_changed.emit(UiSettings.get_hud_width())
	layout_reset.emit()


func _update_scale_value_label(value: float) -> void:
	if _scale_value:
		_scale_value.text = "%d%%" % int(round(value * 100.0))


# ── CONTROLS (UXR-1b: the key reference, taught once on tutor card XIX) ────

func _build_controls_section() -> void:
	_add_header("CONTROLS")
	_add_hint("Screens — L Event Log · T Ledger · G Generals · D Diplomacy · R Dispatch "
		+ "· N Moniteur (Alt+key while typing) · F1 the Cabinet · Esc close / pause. "
		+ "The ledgers' books: 1–8.")
	_add_hint("The day — E End Turn · Tab show or hide the command window (Alt+` while "
		+ "typing) · Up / Down the command history · Tab completes a half-typed order.")
	_add_hint("The map — wheel zoom at the cursor · + / − zoom · Home recentre · the "
		+ "⌂ chip under the map fits all Europe · M map mode · arrows pan · middle-drag "
		+ "pan (Alt+key while typing).")
	_add_hint("The interface — Ctrl+= / Ctrl+− Interface Scale · Ctrl+0 this screen's "
		+ "size · the command window's corner grip resizes it (double-click resets).")


# ── SOUND ───────────────────────────────────────────────────────────────────

func _build_sound_section() -> void:
	_add_header("SOUND")
	_battle_toggle = CheckButton.new()
	_battle_toggle.text = "Battle sounds"
	_battle_toggle.button_pressed = UiSettings.get_battle_sfx()
	_battle_toggle.toggled.connect(func(on): UiSettings.set_battle_sfx(on))
	add_child(_battle_toggle)
	for bus_name in ["Master", "Music", "SFX", "UI"]:
		var row := HBoxContainer.new()
		var lbl := Label.new()
		lbl.text = bus_name
		lbl.custom_minimum_size.x = 64
		lbl.theme_type_variation = &"Caption"
		row.add_child(lbl)
		var slider := HSlider.new()
		slider.min_value = 0.0
		slider.max_value = 1.0
		slider.step = 0.05
		slider.custom_minimum_size = Vector2(140, 0)
		slider.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		slider.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		slider.set_value_no_signal(AudioManager.get_bus_volume(bus_name))
		slider.value_changed.connect(func(v): AudioManager.set_bus_volume(bus_name, v))
		row.add_child(slider)
		_volume_sliders[bus_name] = slider
		add_child(row)


# ── THE PARSER (BYOK) ───────────────────────────────────────────────────────

func _build_parser_section() -> void:
	_add_header("SMARTER PARSING (OPTIONAL)")
	_parser_status = Label.new()
	_parser_status.theme_type_variation = &"Caption"
	_parser_status.add_theme_color_override("font_color", Utils.UI_TEXT_DIM)
	_parser_status.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(_parser_status)

	_key_edit = LineEdit.new()
	_key_edit.secret = true
	_key_edit.placeholder_text = _key_placeholder()
	_key_edit.custom_minimum_size = Vector2(0, 34)
	add_child(_key_edit)

	var btn_row := HBoxContainer.new()
	btn_row.add_theme_constant_override("separation", 8)
	var apply := Button.new()
	apply.text = "Connect"
	apply.custom_minimum_size = Vector2(0, 32)
	apply.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	apply.pressed.connect(_on_apply_key)
	btn_row.add_child(apply)
	_connect_btn = apply
	var clear := Button.new()
	clear.text = "Disconnect"
	clear.custom_minimum_size = Vector2(0, 32)
	clear.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	clear.pressed.connect(_on_clear_key)
	btn_row.add_child(clear)
	add_child(btn_row)
	_disconnect_btn = clear
	_key_edit.text_changed.connect(func(_t): _refresh_key_buttons())

	_add_hint("Your orders are read by a fast offline parser that needs no key. "
		+ "Connect your own Anthropic account and the orders it is unsure of are "
		+ "also read by Claude: create an API key at console.anthropic.com and "
		+ "paste it here. Anthropic bills your account — under a cent for each "
		+ "order it reads. The key is stored on this PC (user://ui_settings.cfg) "
		+ "and sent to Anthropic through the game's own local server — to no one else.")
	_show_stored_parser_state()


func _key_placeholder() -> String:
	var stored := UiSettings.get_api_key()
	if stored == "":
		return "sk-ant-…  (paste your Anthropic API key)"
	return "current key kept — ends …" + stored.right(4)


func _on_apply_key() -> void:
	var key := _key_edit.text.strip_edges()
	if key == "":
		return
	UiSettings.set_api_key(key)
	_key_edit.text = ""
	_key_edit.placeholder_text = _key_placeholder()
	_refresh_key_buttons()
	_push_key(key)


func _on_clear_key() -> void:
	UiSettings.set_api_key("")
	_key_edit.text = ""
	_key_edit.placeholder_text = _key_placeholder()
	_refresh_key_buttons()
	_push_key("")


func _refresh_key_buttons() -> void:
	"""UXR3-68 / 69 (S12): Connect is disabled with no key on the line,
	Disconnect while no key is connected — each with its reason."""
	if _key_edit != null:
		Utils.set_available(_connect_btn, _key_edit.text.strip_edges() != "", "", CONNECT_TIP_OFF)
	Utils.set_available(_disconnect_btn, UiSettings.get_api_key() != "", "", DISCONNECT_TIP_OFF)


func _show_stored_parser_state() -> void:
	_refresh_key_buttons()
	if _parser_status == null:
		return
	var stored := UiSettings.get_api_key()
	if stored == "":
		_parser_status.text = "No key connected — the offline parser reads your orders."
	else:
		_parser_status.text = "Your key (ends …" + stored.right(4) + ") is stored on this PC and connected when a campaign starts."


func _push_key(key: String) -> void:
	if _http == null or not is_inside_tree() or _http_busy:
		return
	_http_busy = true
	_http.set_meta("mode", "push")
	var body := JSON.stringify({"api_key": key})
	var err := _http.request(BACKEND_URL + "/config/llm",
		["Content-Type: application/json"], HTTPClient.METHOD_POST, body)
	if err != OK:
		_http_busy = false
		_parser_status.text = "Backend offline — the key is stored and will apply when the campaign starts."


func _fetch_parser_status() -> void:
	if _http == null or not is_inside_tree() or _http_busy:
		return
	_http_busy = true
	_http.set_meta("mode", "status")
	var err := _http.request(BACKEND_URL + "/config/llm")
	if err != OK:
		_http_busy = false


func _on_http_completed(result: int, code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
	_http_busy = false
	var mode := str(_http.get_meta("mode", ""))
	if result != HTTPRequest.RESULT_SUCCESS or code != 200:
		if mode == "push":
			_parser_status.text = "Backend offline — the key is stored and will apply when the campaign starts."
		return
	var data = JSON.parse_string(body.get_string_from_utf8())
	if not (data is Dictionary):
		return
	# C1: the backend checked the key with Anthropic (a free Models-API GET)
	# and says what it found; a later live parse keeps the line honest.
	var line := str(data.get("key_status_text", ""))
	if line == "":
		line = "Smarter Parsing: on." if bool(data.get("live", false)) else "Not connected — the offline parser reads your orders."
	var status := str(data.get("key_status", ""))
	if status == "rejected" or status == "no_model":
		_parser_status.add_theme_color_override("font_color", Color(Utils.COLOR_ERROR))
	else:
		_parser_status.add_theme_color_override("font_color", Utils.UI_TEXT_DIM)
	_parser_status.text = line


# ── SPOKEN ORDERS (Voice-to-Text v1: OS dictation) ──────────────────────────

func _build_voice_section() -> void:
	_add_header("SPOKEN ORDERS")
	_add_hint("Dictation is supported through Windows voice typing: click the "
		+ "command line, press Win+H, and speak your order. It is typed into "
		+ "the box for you to review and send with Enter — through the same "
		+ "parser as typed orders. On Windows 10, turn on 'Online speech "
		+ "recognition' in Windows Settings if the panel refuses to listen.")


# ── CREDITS ─────────────────────────────────────────────────────────────────

func _build_credits_section() -> void:
	_add_header("CREDITS")
	var credit := Label.new()
	credit.name = "AssetCredits"
	# FA-S13-1(c) (slice 17): the location claim depends on which build is
	# running — the same reason `Utils.launch_hint()` exists. The zip carries
	# the notices beside the game in `licenses\`; a source checkout keeps
	# them at the repository root and beside each asset.
	var terms_where := ("THIRD_PARTY_LICENSES.md at the repository root, with the "
		+ "per-family notices beside each asset under assets\\"
		if OS.has_feature("editor")
		else "THIRD_PARTY_LICENSES.md, beside the game, with the per-family notices in licenses\\")
	credit.text = ("Unit icons by Lorc, Delapouite & contributors (game-icons.net, "
		+ "CC BY 3.0) · Interface icons: Phosphor (MIT) · Musket volley: aaronsiler "
		+ "& Benboncan (CC BY 4.0) · Menu paintings, marshal portraits & music: "
		+ "public domain (Wikimedia Commons / IMSLP) · Full terms: " + terms_where + ".")
	credit.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	credit.theme_type_variation = &"Caption"
	credit.add_theme_color_override("font_color", Utils.UI_TEXT_DIM)
	add_child(credit)


# ── shared bits ─────────────────────────────────────────────────────────────

func _add_header(text: String) -> void:
	var header := Label.new()
	header.text = text
	header.theme_type_variation = &"Caption"
	header.add_theme_color_override("font_color", Utils.UI_GOLD)
	add_child(header)


func _add_hint(text: String) -> void:
	var hint := Label.new()
	hint.text = text
	hint.add_theme_color_override("font_color", Color(0.627, 0.627, 0.659))
	hint.theme_type_variation = &"Caption"
	hint.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(hint)
