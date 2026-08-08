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
#   • THE PARSER — the in-client Anthropic API key (BYOK). Stored locally in
#     user://ui_settings.cfg, pushed to the player's OWN backend at
#     127.0.0.1:8005 (/config/llm); an empty key reverts the backend to its
#     .env configuration. The key is never sent anywhere else.
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

# Golden Rule 7: same origin as api_client.gd.
const BACKEND_URL := "http://127.0.0.1:8005"

var _scale_dragging := false
var _scale_slider: HSlider
var _scale_value: Label
var _volume_sliders: Dictionary = {}   # bus name -> HSlider
var _battle_toggle: CheckButton
var _key_edit: LineEdit
var _parser_status: Label
var _http: HTTPRequest
var _http_busy := false


func _ready() -> void:
	add_theme_constant_override("separation", 6)
	_build_interface_section()
	_build_sound_section()
	_build_parser_section()
	_build_voice_section()
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
	for bus_name in _volume_sliders:
		_volume_sliders[bus_name].set_value_no_signal(AudioManager.get_bus_volume(bus_name))
	if _battle_toggle:
		_battle_toggle.set_pressed_no_signal(UiSettings.get_battle_sfx())
	if _key_edit:
		_key_edit.text = ""
		_key_edit.placeholder_text = _key_placeholder()
	_show_stored_parser_state()
	_fetch_parser_status()


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
	_scale_value.add_theme_font_size_override("font_size", 14)
	row.add_child(_scale_value)
	add_child(row)
	_update_scale_value_label(UiSettings.get_ui_scale())

	var reset := Button.new()
	reset.text = "Reset to 100%"
	reset.custom_minimum_size = Vector2(0, 32)
	reset.pressed.connect(_on_reset_scale)
	add_child(reset)

	_add_hint("Interface Scale resizes the whole interface — command window, "
		+ "ledgers, and pop-ups. In the campaign, the command-window header has "
		+ "quick Text Size + / − buttons that adjust this same scale.")


func _on_scale_changed(value: float) -> void:
	_update_scale_value_label(value)
	ui_scale_changed.emit(value, not _scale_dragging)


func _on_scale_drag_ended(_changed: bool) -> void:
	_scale_dragging = false
	ui_scale_changed.emit(_scale_slider.value, true)


func _on_reset_scale() -> void:
	if is_equal_approx(_scale_slider.value, UiSettings.DEFAULT_UI_SCALE):
		_update_scale_value_label(UiSettings.DEFAULT_UI_SCALE)
		ui_scale_changed.emit(UiSettings.DEFAULT_UI_SCALE, true)
	else:
		_scale_slider.value = UiSettings.DEFAULT_UI_SCALE


func _update_scale_value_label(value: float) -> void:
	if _scale_value:
		_scale_value.text = "%d%%" % int(round(value * 100.0))


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
		lbl.add_theme_font_size_override("font_size", 12)
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
	_add_header("THE PARSER (AI)")
	_parser_status = Label.new()
	_parser_status.add_theme_font_size_override("font_size", 12)
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
	apply.text = "Apply key"
	apply.custom_minimum_size = Vector2(0, 32)
	apply.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	apply.pressed.connect(_on_apply_key)
	btn_row.add_child(apply)
	var clear := Button.new()
	clear.text = "Clear (use .env)"
	clear.custom_minimum_size = Vector2(0, 32)
	clear.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	clear.pressed.connect(_on_clear_key)
	btn_row.add_child(clear)
	add_child(btn_row)

	_add_hint("Typed orders are read by a fast offline parser; an Anthropic API "
		+ "key lets Berthier's aide handle the hard phrasings live. The key is "
		+ "stored locally (user://ui_settings.cfg) and sent only to your own "
		+ "backend on this machine — never anywhere else.")
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
	_push_key(key)


func _on_clear_key() -> void:
	UiSettings.set_api_key("")
	_key_edit.text = ""
	_key_edit.placeholder_text = _key_placeholder()
	_push_key("")


func _show_stored_parser_state() -> void:
	if _parser_status == null:
		return
	var stored := UiSettings.get_api_key()
	if stored == "":
		_parser_status.text = "No key stored — the backend uses its .env configuration."
	else:
		_parser_status.text = "Your key (ends …" + stored.right(4) + ") is stored and pushed when a campaign starts."


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
	var provider := str(data.get("provider", "?"))
	var key_source := str(data.get("key_source", "none"))
	var live := bool(data.get("live", false))
	var line: String
	if not live:
		line = "Live parser: OFF — offline mock parser (deterministic keywords only)."
	elif key_source == "byok":
		line = "Live parser: %s — using YOUR key." % provider.to_upper()
	elif key_source == "inhouse":
		line = "Live parser: %s — key from the backend's .env." % provider.to_upper()
	else:
		line = "Live parser: %s — but NO key found; falls back to the offline parser." % provider.to_upper()
	if mode == "push":
		line = "Applied. " + line
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
	credit.text = ("Unit icons by Lorc, Delapouite & contributors (game-icons.net, "
		+ "CC BY 3.0) · Interface icons: Phosphor (MIT) · Musket volley: aaronsiler "
		+ "& Benboncan (CC BY 4.0) · Menu paintings, marshal portraits & music: "
		+ "public domain (Wikimedia Commons / IMSLP) · Full terms: THIRD_PARTY_LICENSES.md.")
	credit.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	credit.add_theme_font_size_override("font_size", 10)
	credit.add_theme_color_override("font_color", Utils.UI_TEXT_DIM)
	add_child(credit)


# ── shared bits ─────────────────────────────────────────────────────────────

func _add_header(text: String) -> void:
	var header := Label.new()
	header.text = text
	header.add_theme_font_size_override("font_size", 13)
	header.add_theme_color_override("font_color", Utils.UI_GOLD)
	add_child(header)


func _add_hint(text: String) -> void:
	var hint := Label.new()
	hint.text = text
	hint.add_theme_color_override("font_color", Color(0.627, 0.627, 0.659))
	hint.add_theme_font_size_override("font_size", 11)
	hint.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(hint)
