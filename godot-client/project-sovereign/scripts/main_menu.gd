extends Control

# =============================================================================
# INK & IRON — The Main Menu (Road to EA position 6)
# =============================================================================
# The front door: a slow slideshow of public-domain Napoleonic battle
# paintings (Ken Burns drift + crossfade), the title in Cinzel over a gold
# rule, and the campaign column. The Settings surface is the SHARED
# SettingsPanel (also embedded by the pause menu), so the two can never drift.
#
# The menu owns NO game state: campaign actions are written to MenuBoot and
# consumed by main.gd once its backend connection test succeeds — so New /
# Continue / Load reuse the exact world-swap machinery the pause menu uses.
# The menu polls GET /test itself only to be HONEST about availability
# (buttons disabled with the reason stated while the backend is down).
# =============================================================================

const BACKEND_URL := "http://127.0.0.1:8005"   # Golden Rule 7 — api_client.gd's origin
const GAME_SCENE := "res://scenes/main.tscn"
const PAINTINGS_DIR := "res://assets/ui/paintings/"

const SLIDE_SECONDS := 13.0     # hold per painting (motion runs the whole time)
const FADE_SECONDS := 2.8       # crossfade overlap
const KB_SCALE_FROM := 1.03     # Ken Burns drift: gentle push-in
const KB_SCALE_TO := 1.115
const POLL_SECONDS := 2.5       # backend reachability poll while down

# The gallery: every file license-verified Public Domain on Wikimedia Commons
# (sourcing record: THIRD_PARTY_LICENSES.md §Menu paintings).
const SLIDES := [
	{"file": "gerard_austerlitz_pd.jpg", "caption": "François Gérard — The Battle of Austerlitz, 1805"},
	{"file": "david_alps_pd.jpg", "caption": "Jacques-Louis David — Bonaparte Crossing the Alps"},
	{"file": "meissonier_friedland_pd.jpg", "caption": "Ernest Meissonier — 1807, Friedland"},
	{"file": "gros_eylau_pd.jpg", "caption": "Antoine-Jean Gros — Napoleon on the Field of Eylau"},
	{"file": "vernet_jena_pd.jpg", "caption": "Horace Vernet — The Battle of Jena"},
	{"file": "turner_trafalgar_pd.jpg", "caption": "J. M. W. Turner — The Battle of Trafalgar"},
]
# Ken Burns pivot corners (fraction of rect) — cycled so consecutive slides
# drift toward different corners.
const KB_PIVOTS := [Vector2(0.32, 0.38), Vector2(0.68, 0.30), Vector2(0.38, 0.66), Vector2(0.64, 0.62)]

@onready var slide_a: TextureRect = $SlideA
@onready var slide_b: TextureRect = $SlideB
@onready var status_http: HTTPRequest = $StatusHttp

var _slide_index := -1
var _front_is_a := false
var _tex_cache: Dictionary = {}        # slide index -> Texture2D (current + next only)
# Child Timer NODES, not SceneTree timers: a SceneTreeTimer outlives the scene,
# so a pending slide tick would fire on the FREED menu after entering the game
# (console error on every campaign start). Children die with the scene.
var _slide_timer: Timer
var _poll_timer: Timer
var _kb_tweens: Array = []

var _backend_up := false
var _http_mode := ""                   # "test" | "saves"
var _saves: Array = []
var _leaving := false

var _caption: Label
var _status_label: Label
var _buttons: Dictionary = {}          # id -> Button
var _confirm_box: VBoxContainer
# POSITION 7: Begin and the School of War share the one confirm row — both
# REPLACE the backend's running world. The pressed handler stamps which
# action the yes-button launches plus the matching copy.
var _confirm_action := "new_game"
var _confirm_label: Label
var _confirm_yes: Button
var _menu_column: VBoxContainer
var _settings_view: PanelContainer
var _settings_panel: SettingsPanel
var _fade_rect: ColorRect

# fonts (variable-weight OFL files already shipped in assets/fonts)
var _font_title: FontVariation
var _font_button: FontVariation
var _font_fell: FontFile
var _font_fell_italic: FontFile


func _ready() -> void:
	# The menu is the first scene: these calls self-install the audio engine
	# (buses, saved volumes, the global button-click hook) and start the
	# title theme. Returning from a campaign, they also silence the map beds.
	# DEFERRED like main.gd's AudioManager.boot — the lazy instance cannot
	# add_child to a root that is busy instantiating this very scene.
	AudioManager.stop_all_loops.call_deferred()
	AudioManager.set_menu_mood.call_deferred()

	_load_fonts()
	_build_title_block()
	_build_menu_column()
	_build_footer()
	_build_settings_view()
	_build_fade_rect()
	_apply_backend_state()

	_slide_timer = Timer.new()
	_slide_timer.one_shot = true
	_slide_timer.timeout.connect(_advance_slide)
	add_child(_slide_timer)
	_poll_timer = Timer.new()
	_poll_timer.one_shot = true
	_poll_timer.wait_time = POLL_SECONDS
	_poll_timer.timeout.connect(_poll_backend)
	add_child(_poll_timer)

	status_http.request_completed.connect(_on_http_completed)
	_poll_backend()

	resized.connect(_update_kb_pivots)
	# Deferred: the first slide's Ken Burns pivot needs the post-layout rect
	# size, and the entrance animation reads settled anchor positions.
	_start_presentation.call_deferred()


func _start_presentation() -> void:
	_advance_slide()
	_entrance_animation()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel") and _settings_view and _settings_view.visible:
		_close_settings()
		get_viewport().set_input_as_handled()


# ── fonts ───────────────────────────────────────────────────────────────────

func _load_fonts() -> void:
	var cinzel: FontFile = load("res://assets/fonts/Cinzel[wght].ttf")
	_font_title = FontVariation.new()
	_font_title.base_font = cinzel
	_font_title.variation_opentype = {"wght": 700}
	var cormorant: FontFile = load("res://assets/fonts/CormorantGaramond[wght].ttf")
	_font_button = FontVariation.new()
	_font_button.base_font = cormorant
	_font_button.variation_opentype = {"wght": 600}
	_font_fell = load("res://assets/fonts/IMFeENrm28P.ttf")
	_font_fell_italic = load("res://assets/fonts/IMFeENit28P.ttf")


# ── the title block ─────────────────────────────────────────────────────────

func _build_title_block() -> void:
	var block := VBoxContainer.new()
	block.name = "TitleBlock"
	block.set_anchors_preset(Control.PRESET_TOP_LEFT)
	block.position = Vector2(0, 0)
	block.anchor_left = 0.07
	block.anchor_right = 0.07
	block.anchor_top = 0.10
	block.anchor_bottom = 0.10
	block.grow_horizontal = Control.GROW_DIRECTION_END
	block.grow_vertical = Control.GROW_DIRECTION_END
	block.add_theme_constant_override("separation", 6)
	block.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(block)

	var over := Label.new()
	over.name = "OverTitle"
	over.text = "ANNO 1805 · EUROPE IN THE BALANCE"
	over.add_theme_font_override("font", _font_fell)
	over.add_theme_font_size_override("font_size", 19)
	over.add_theme_color_override("font_color", Color(0.87, 0.8, 0.62, 0.92))
	over.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.7))
	over.add_theme_constant_override("shadow_offset_y", 2)
	block.add_child(over)

	var title := Label.new()
	title.name = "Title"
	title.text = "INK & IRON"
	title.add_theme_font_override("font", _font_title)
	title.add_theme_font_size_override("font_size", 96)
	title.add_theme_color_override("font_color", Color(0.92, 0.83, 0.6))
	title.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.78))
	title.add_theme_constant_override("shadow_offset_x", 0)
	title.add_theme_constant_override("shadow_offset_y", 4)
	title.add_theme_constant_override("shadow_outline_size", 10)
	block.add_child(title)

	# the gold rule with flourishes under the title
	var rule := HBoxContainer.new()
	rule.name = "Rule"
	rule.add_theme_constant_override("separation", 10)
	var fl := TextureRect.new()
	fl.texture = load("res://assets/ui/ornaments/flourish_left.svg")
	fl.custom_minimum_size = Vector2(120, 20)
	fl.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	fl.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	fl.modulate = Color(0.85, 0.75, 0.55, 0.95)
	rule.add_child(fl)
	var sub := Label.new()
	sub.name = "SubTitle"
	sub.text = "The Campaigns of Napoleon"
	sub.add_theme_font_override("font", _font_fell_italic)
	sub.add_theme_font_size_override("font_size", 24)
	sub.add_theme_color_override("font_color", Color(0.88, 0.83, 0.7, 0.95))
	sub.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.7))
	sub.add_theme_constant_override("shadow_offset_y", 2)
	rule.add_child(sub)
	var fr := TextureRect.new()
	fr.texture = load("res://assets/ui/ornaments/flourish_right.svg")
	fr.custom_minimum_size = Vector2(120, 20)
	fr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	fr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	fr.modulate = Color(0.85, 0.75, 0.55, 0.95)
	rule.add_child(fr)
	block.add_child(rule)


# ── the campaign column ─────────────────────────────────────────────────────

func _build_menu_column() -> void:
	_menu_column = VBoxContainer.new()
	_menu_column.name = "MenuColumn"
	_menu_column.anchor_left = 0.07
	_menu_column.anchor_right = 0.07
	_menu_column.anchor_top = 0.40
	_menu_column.anchor_bottom = 0.40
	_menu_column.grow_horizontal = Control.GROW_DIRECTION_END
	_menu_column.grow_vertical = Control.GROW_DIRECTION_END
	_menu_column.add_theme_constant_override("separation", 12)
	add_child(_menu_column)

	if MenuBoot.came_from_game:
		_add_menu_button("return", "Return to the War Room", _on_return_pressed, true)
	_add_menu_button("begin", "Begin the 1805 Campaign", _on_begin_pressed, not MenuBoot.came_from_game)

	# the Begin confirm row (shown only when Begin would replace a campaign)
	_confirm_box = VBoxContainer.new()
	_confirm_box.visible = false
	_confirm_box.add_theme_constant_override("separation", 8)
	var warn := Label.new()
	warn.text = "Begin anew? The autosave of your running campaign is replaced."
	warn.add_theme_font_size_override("font_size", 14)
	warn.add_theme_color_override("font_color", Utils.UI_WARNING)
	warn.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.8))
	warn.add_theme_constant_override("shadow_offset_y", 1)
	_confirm_box.add_child(warn)
	_confirm_label = warn
	var confirm_row := HBoxContainer.new()
	confirm_row.add_theme_constant_override("separation", 10)
	var yes := _make_button("Confirm — begin anew", false)
	yes.custom_minimum_size = Vector2(220, 44)
	yes.pressed.connect(func(): _launch(_confirm_action))
	_confirm_yes = yes
	confirm_row.add_child(yes)
	var no := _make_button("Keep my campaign", false)
	no.custom_minimum_size = Vector2(200, 44)
	no.pressed.connect(func(): _confirm_box.visible = false)
	confirm_row.add_child(no)
	_confirm_box.add_child(confirm_row)
	_menu_column.add_child(_confirm_box)

	_add_menu_button("tutorial", "The School of War — a guided campaign", _on_tutorial_pressed, false)
	_add_menu_button("continue", "Continue", _on_continue_pressed, false)
	_add_menu_button("load", "Load a Campaign…", _on_load_pressed, false)
	_add_menu_button("settings", "Settings", _open_settings, false)
	_add_menu_button("quit", "Quit to Desktop", _on_quit_pressed, false)


func _add_menu_button(id: String, text: String, cb: Callable, prominent: bool) -> void:
	var b := _make_button(text, prominent)
	b.pressed.connect(cb)
	_menu_column.add_child(b)
	_buttons[id] = b


func _make_button(text: String, prominent: bool) -> Button:
	var b := Button.new()
	b.text = text
	b.custom_minimum_size = Vector2(400, 56 if prominent else 50)
	b.alignment = HORIZONTAL_ALIGNMENT_LEFT
	b.add_theme_font_override("font", _font_button)
	b.add_theme_font_size_override("font_size", 26 if prominent else 23)
	b.add_theme_color_override("font_color", Color(0.93, 0.88, 0.74) if prominent else Color(0.85, 0.82, 0.72))
	b.add_theme_color_override("font_hover_color", Color(1.0, 0.95, 0.8))
	b.add_theme_color_override("font_focus_color", Color(1.0, 0.95, 0.8))
	b.add_theme_color_override("font_disabled_color", Color(0.55, 0.55, 0.55, 0.8))

	var normal := StyleBoxFlat.new()
	normal.bg_color = Color(0.03, 0.045, 0.085, 0.62)
	normal.border_color = Color(0.85, 0.75, 0.55, 0.5 if prominent else 0.32)
	normal.set_border_width_all(1)
	if prominent:
		normal.border_width_left = 3
	normal.set_content_margin_all(10)
	normal.content_margin_left = 18
	normal.content_margin_right = 18
	var hover: StyleBoxFlat = normal.duplicate()
	hover.bg_color = Color(0.10, 0.115, 0.19, 0.82)
	hover.border_color = Color(0.94, 0.88, 0.69, 0.9)
	hover.border_width_left = 3
	var pressed: StyleBoxFlat = hover.duplicate()
	pressed.bg_color = Color(0.14, 0.13, 0.10, 0.9)
	var disabled: StyleBoxFlat = normal.duplicate()
	disabled.bg_color = Color(0.03, 0.04, 0.06, 0.4)
	disabled.border_color = Color(0.5, 0.48, 0.42, 0.2)
	b.add_theme_stylebox_override("normal", normal)
	b.add_theme_stylebox_override("hover", hover)
	b.add_theme_stylebox_override("pressed", pressed)
	b.add_theme_stylebox_override("disabled", disabled)
	b.add_theme_stylebox_override("focus", hover)
	return b


# ── footer: status line + caption + version ─────────────────────────────────

func _build_footer() -> void:
	_status_label = Label.new()
	_status_label.name = "StatusLine"
	_status_label.anchor_left = 0.07
	_status_label.anchor_right = 0.6
	_status_label.anchor_top = 0.955
	_status_label.anchor_bottom = 0.955
	_status_label.add_theme_font_size_override("font_size", 13)
	_status_label.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.8))
	_status_label.add_theme_constant_override("shadow_offset_y", 1)
	_status_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_status_label)

	_caption = Label.new()
	_caption.name = "PaintingCaption"
	_caption.anchor_left = 0.55
	_caption.anchor_right = 0.97
	_caption.anchor_top = 0.955
	_caption.anchor_bottom = 0.955
	_caption.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_caption.add_theme_font_override("font", _font_fell_italic)
	_caption.add_theme_font_size_override("font_size", 15)
	_caption.add_theme_color_override("font_color", Color(0.82, 0.78, 0.68, 0.85))
	_caption.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.85))
	_caption.add_theme_constant_override("shadow_offset_y", 1)
	_caption.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_caption)

	var version := Label.new()
	version.name = "VersionLine"
	version.anchor_left = 0.07
	version.anchor_right = 0.6
	version.anchor_top = 0.925
	version.anchor_bottom = 0.925
	version.text = "Ink & Iron — development build"
	version.add_theme_font_size_override("font_size", 12)
	version.add_theme_color_override("font_color", Color(0.65, 0.63, 0.58, 0.8))
	version.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.8))
	version.add_theme_constant_override("shadow_offset_y", 1)
	version.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(version)


# ── settings view (the shared SettingsPanel, promoted from pause) ───────────

func _build_settings_view() -> void:
	_settings_view = PanelContainer.new()
	_settings_view.name = "SettingsView"
	_settings_view.visible = false
	_settings_view.set_anchors_preset(Control.PRESET_CENTER)
	_settings_view.custom_minimum_size = Vector2(520, 0)
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.055, 0.07, 0.115, 0.97)
	style.border_color = Utils.UI_GOLD
	style.set_border_width_all(2)
	style.set_corner_radius_all(6)
	style.set_content_margin_all(24)
	_settings_view.add_theme_stylebox_override("panel", style)
	add_child(_settings_view)

	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 10)
	_settings_view.add_child(vbox)

	var header := Label.new()
	header.text = "SETTINGS"
	header.add_theme_font_override("font", _font_title)
	header.add_theme_font_size_override("font_size", 26)
	header.add_theme_color_override("font_color", Color(0.92, 0.83, 0.6))
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	vbox.add_child(header)

	var scroll := ScrollContainer.new()
	scroll.custom_minimum_size = Vector2(0, 520)
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	vbox.add_child(scroll)
	_settings_panel = (load("res://scenes/settings_panel.tscn") as PackedScene).instantiate()
	_settings_panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(_settings_panel)
	_settings_panel.ui_scale_changed.connect(_on_ui_scale_changed)

	var back := _make_button("Back", false)
	back.alignment = HORIZONTAL_ALIGNMENT_CENTER
	back.custom_minimum_size = Vector2(0, 44)
	back.pressed.connect(_close_settings)
	vbox.add_child(back)


func _open_settings() -> void:
	_settings_view.visible = true
	_settings_panel.refresh()
	Utils.clamp_centered_panel(_settings_view)
	AudioManager.play("panel_open")


func _close_settings() -> void:
	_settings_view.visible = false
	AudioManager.play("panel_close")


func _on_ui_scale_changed(value: float, persist: bool) -> void:
	# The menu has no map to compensate — content_scale_factor is the whole
	# story here. In the campaign, main.gd owns the full application.
	get_window().content_scale_factor = clampf(value, UiSettings.MIN_UI_SCALE, UiSettings.MAX_UI_SCALE)
	if persist:
		UiSettings.set_ui_scale(value)


# ── campaign actions ────────────────────────────────────────────────────────

func _on_return_pressed() -> void:
	_launch("")


func _on_begin_pressed() -> void:
	# A fresh campaign REPLACES the backend's running world and refreshes the
	# autosave (POST /new_game) — confirm when there is anything to lose.
	if _saves.size() > 0 or MenuBoot.came_from_game:
		_confirm_action = "new_game"
		_confirm_label.text = "Begin anew? The autosave of your running campaign is replaced."
		_confirm_yes.text = "Confirm — begin anew"
		_confirm_box.visible = not _confirm_box.visible
	else:
		_launch("new_game")


func _on_tutorial_pressed() -> void:
	# POSITION 7: the School of War REPLACES the backend's running world
	# exactly like Begin (POST /new_game with the tutorial scenario) — the
	# same confirm row guards it when there is anything to lose.
	if _saves.size() > 0 or MenuBoot.came_from_game:
		_confirm_action = "tutorial"
		_confirm_label.text = "Enter the School of War? The autosave of your running campaign is replaced."
		_confirm_yes.text = "Confirm — to school"
		_confirm_box.visible = not _confirm_box.visible
	else:
		_launch("tutorial")


func _on_continue_pressed() -> void:
	_launch("continue")


func _on_load_pressed() -> void:
	_launch("load")


func _on_quit_pressed() -> void:
	get_tree().quit()


func _launch(action: String) -> void:
	if _leaving:
		return
	_leaving = true
	MenuBoot.pending_action = action
	MenuBoot.came_from_game = false
	_fade_rect.mouse_filter = Control.MOUSE_FILTER_STOP
	var tw := create_tween()
	tw.tween_property(_fade_rect, "color:a", 1.0, 0.5)
	tw.tween_callback(func(): get_tree().change_scene_to_file(GAME_SCENE))


func _build_fade_rect() -> void:
	_fade_rect = ColorRect.new()
	_fade_rect.name = "FadeRect"
	_fade_rect.color = Color(0, 0, 0, 0)
	_fade_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	_fade_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_fade_rect)


# ── backend availability (honest buttons) ───────────────────────────────────

func _poll_backend() -> void:
	if _leaving or _http_mode != "" or _backend_up:
		return
	_http_mode = "test"
	var err := status_http.request(BACKEND_URL + "/test")
	if err != OK:
		_http_mode = ""
		_poll_timer.start()


func _on_http_completed(result: int, code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
	var mode := _http_mode
	_http_mode = ""
	if mode == "test":
		if result == HTTPRequest.RESULT_SUCCESS and code == 200:
			_backend_up = true
			_apply_backend_state()
			# now learn what there is to continue
			_http_mode = "saves"
			var err := status_http.request(BACKEND_URL + "/saves")
			if err != OK:
				_http_mode = ""
		else:
			_backend_up = false
			_apply_backend_state()
			_poll_timer.start()
	elif mode == "saves":
		if result == HTTPRequest.RESULT_SUCCESS and code == 200:
			var data = JSON.parse_string(body.get_string_from_utf8())
			if data is Dictionary and data.get("saves") is Array:
				_saves = data["saves"]
		_apply_backend_state()


func _apply_backend_state() -> void:
	if _status_label == null:
		return
	if _backend_up:
		_status_label.text = "✓ The war office answers.  ·  127.0.0.1:8005"
		_status_label.add_theme_color_override("font_color", Color(0.55, 0.72, 0.55, 0.9))
	else:
		_status_label.text = "The war office does not answer — start the backend:  .venv\\Scripts\\python.exe -m backend.main"
		_status_label.add_theme_color_override("font_color", Color(0.85, 0.55, 0.45, 0.95))
	var has_saves := _saves.size() > 0
	for id in _buttons:
		var b: Button = _buttons[id]
		match id:
			"begin", "return", "tutorial":
				b.disabled = not _backend_up
			"continue":
				b.disabled = not (_backend_up and has_saves)
				if has_saves:
					var meta: Dictionary = _saves[0].get("metadata", {})
					var turn := int(meta.get("turn", 0))
					b.text = "Continue" + ("  ·  Turn %d" % turn if turn > 0 else "")
			"load":
				b.disabled = not (_backend_up and has_saves)
	if not _backend_up:
		_confirm_box.visible = false


# ── the slideshow ───────────────────────────────────────────────────────────

func _advance_slide() -> void:
	if _leaving:
		return
	_slide_index = (_slide_index + 1) % SLIDES.size()
	var tex := _slide_texture(_slide_index)
	if tex == null:
		return
	var incoming := slide_b if _front_is_a else slide_a
	var outgoing := slide_a if _front_is_a else slide_b
	_front_is_a = not _front_is_a

	incoming.texture = tex
	incoming.modulate.a = 0.0
	_start_ken_burns(incoming)
	var tw := create_tween()
	tw.set_parallel(true)
	tw.tween_property(incoming, "modulate:a", 1.0, FADE_SECONDS)
	if outgoing.texture != null:
		tw.tween_property(outgoing, "modulate:a", 0.0, FADE_SECONDS)

	_caption.text = str(SLIDES[_slide_index].get("caption", "")) + "  ·  public domain"

	# pre-warm the next painting, drop the ones behind us (VRAM hygiene)
	var next_i := (_slide_index + 1) % SLIDES.size()
	_slide_texture(next_i)
	for k in _tex_cache.keys().duplicate():
		if k != _slide_index and k != next_i:
			_tex_cache.erase(k)

	_slide_timer.start(SLIDE_SECONDS)


func _slide_texture(i: int) -> Texture2D:
	if _tex_cache.has(i):
		return _tex_cache[i]
	var path := PAINTINGS_DIR + str(SLIDES[i]["file"])
	if not ResourceLoader.exists(path):
		push_warning("MainMenu: missing painting " + path)
		return null
	var tex: Texture2D = load(path)
	_tex_cache[i] = tex
	return tex


func _start_ken_burns(rect: TextureRect) -> void:
	var pivot_frac: Vector2 = KB_PIVOTS[_slide_index % KB_PIVOTS.size()]
	rect.set_meta("kb_pivot", pivot_frac)
	rect.pivot_offset = rect.size * pivot_frac
	rect.scale = Vector2.ONE * KB_SCALE_FROM
	var tw := create_tween()
	tw.tween_property(rect, "scale", Vector2.ONE * KB_SCALE_TO, SLIDE_SECONDS + FADE_SECONDS)
	_kb_tweens.append(tw)
	while _kb_tweens.size() > 2:
		_kb_tweens.pop_front()


func _update_kb_pivots() -> void:
	for rect in [slide_a, slide_b]:
		if rect and rect.has_meta("kb_pivot"):
			rect.pivot_offset = rect.size * (rect.get_meta("kb_pivot") as Vector2)


# ── entrance ────────────────────────────────────────────────────────────────

func _entrance_animation() -> void:
	var title_block := get_node_or_null("TitleBlock")
	if title_block:
		title_block.modulate.a = 0.0
		title_block.position.y -= 14
		var tw := create_tween()
		tw.set_parallel(true)
		tw.tween_property(title_block, "modulate:a", 1.0, 1.1).set_delay(0.15)
		tw.tween_property(title_block, "position:y", title_block.position.y + 14, 1.1) \
			.set_delay(0.15).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	var delay := 0.5
	for b in _menu_column.get_children():
		if b == _confirm_box:
			continue
		b.modulate.a = 0.0
		var tw2 := create_tween()
		tw2.tween_property(b, "modulate:a", 1.0, 0.5).set_delay(delay)
		delay += 0.08
