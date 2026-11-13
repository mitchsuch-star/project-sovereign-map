extends CanvasLayer

# =============================================================================
# INK & IRON - Pause Menu (Phase 6.5; Settings promoted → SettingsPanel,
# Main Menu pass position 6)
# =============================================================================
# Modal overlay triggered by Esc when no input is focused.
# Save / Load / New Campaign / Settings / Main Menu / Quit to Desktop.
#
# The Settings content is the SHARED SettingsPanel scene (settings_panel.gd) —
# the same component the Main Menu embeds — so the two surfaces can never
# drift. This script keeps only the frame: open/close, the confirm flow, and
# the ui_scale_changed forwarding contract main.gd already wires (main.gd owns
# applying scale: content_scale_factor + native-map compensation + persist).
# =============================================================================

signal save_requested
signal load_requested
signal new_game_requested
signal main_menu_requested
signal closed
# Session UI-5: "Save Game…" opens the SaveDialog (main.gd shows it; the old
# `save_requested` quick-save signal is kept but no longer emitted from here —
# F5 owns the quicksave now).
signal save_dialog_requested
# "Help & Keys" — main.gd opens the Help & Keys book.
signal help_requested
# "The School of War…" after its confirm card — main.gd starts the tutorial.
signal tutorial_requested
# "Save & leave" on the leave card: main.gd opens the SaveDialog and, once the
# save lands, leaves (to_menu true = the Main Menu, false = the desktop).
signal save_and_leave_requested(to_menu: bool)
# Re-emitted from the embedded SettingsPanel (UI-2 semantics: live-apply every
# step, persist at drag end / on click or keyboard change).
signal ui_scale_changed(value, persist)
# UXR-1b: the panel's two new asks, re-emitted for main.gd — open the sizing
# card ("Preview with a sample…") and re-fit the terminal after Reset layout.
signal size_card_requested
signal layout_reset
# UXR-D1 (Pre-Deploy S9b): the panel re-themed the type sizes; main.gd refits
# every open surface on the live-refit road.
signal text_size_changed(value, persist)
# UXR-D3: HUD width changed; main.gd refits the HUD to the band.
signal hud_width_changed(width)
# Session UI-3: the very wide screen's map view changed; main.gd re-derives it.
signal wide_map_changed(mode)
# Session UI-5: Settings → DISPLAY's "Show first-open notes again".
signal first_open_reset_requested

# UI References
@onready var background_overlay = $BackgroundOverlay
@onready var save_button = $PanelContainer/VBoxContainer/SaveButton
@onready var load_button = $PanelContainer/VBoxContainer/LoadButton
@onready var new_game_button = $PanelContainer/VBoxContainer/NewGameButton
@onready var new_game_confirm_box = $PanelContainer/VBoxContainer/NewGameConfirmBox
@onready var confirm_new_game_button = $PanelContainer/VBoxContainer/NewGameConfirmBox/NewGameConfirmButtons/ConfirmNewGameButton
@onready var cancel_new_game_button = $PanelContainer/VBoxContainer/NewGameConfirmBox/NewGameConfirmButtons/CancelNewGameButton
@onready var settings_button = $PanelContainer/VBoxContainer/SettingsButton
@onready var settings_box = $PanelContainer/VBoxContainer/SettingsBox
@onready var main_menu_button = $PanelContainer/VBoxContainer/MainMenuButton
@onready var quit_button = $PanelContainer/VBoxContainer/QuitButton

var _settings_panel: SettingsPanel = null
var _version_line: Label = null  # PB-4: the build stamp line

# Session UI-5: the menu's roads (every button that leaves or opens something),
# the one card that asks before a road is taken, and the Help / School buttons.
var _subtitle: Label = null
var _help_button: Button = null
var _school_button: Button = null
var _nav: Array = []
var _ask_box: VBoxContainer = null
var _ask_title: Label = null
var _ask_detail: Label = null
var _ask_buttons: HBoxContainer = null
var _ask_to_menu := false
var _ask_hidden: Array = []

const ROAD_BUSY_TIP := "Answer the question above first."
const TITLE_FONT_PATH := "res://assets/fonts/Cinzel[wght].ttf"
const PAIR_PANEL_HALF_W := 230.0

func _ready():
	save_button.pressed.connect(_on_save)
	load_button.pressed.connect(_on_load)
	new_game_button.pressed.connect(_on_new_game)
	confirm_new_game_button.pressed.connect(_on_confirm_new_game)
	cancel_new_game_button.pressed.connect(_on_cancel_new_game)
	settings_button.pressed.connect(_on_settings)
	main_menu_button.pressed.connect(_on_main_menu)
	quit_button.pressed.connect(_on_quit)
	background_overlay.gui_input.connect(_on_overlay_input)
	# UXR3-F5 (Pre-Deploy S12 part 2): a way back to the war room, first —
	# the panel offered every road out of the campaign and none back into it
	# (Esc and a click outside closed it, but nothing said so).
	var resume := Button.new()
	resume.name = "ResumeButton"
	resume.text = "Resume (Esc)"
	resume.custom_minimum_size = Vector2(0, 36)
	resume.pressed.connect(close_menu)
	var vb: VBoxContainer = $PanelContainer/VBoxContainer
	vb.add_child(resume)
	vb.move_child(resume, save_button.get_index())
	resume.theme_type_variation = &"PrimaryButton"   # Session UI-5: the one gilt answer
	_build_roads(vb, resume)
	# The shared Settings surface, in a scroll so the pause panel stays
	# inside small viewports at high Interface Scale.
	var scroll := ScrollContainer.new()
	scroll.custom_minimum_size = Vector2(0, 440)
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	settings_box.add_child(scroll)
	_settings_panel = (load("res://scenes/settings_panel.tscn") as PackedScene).instantiate()
	_settings_panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(_settings_panel)
	_settings_panel.ui_scale_changed.connect(func(v, p): ui_scale_changed.emit(v, p))
	_settings_panel.size_card_requested.connect(func(): size_card_requested.emit())
	_settings_panel.layout_reset.connect(func(): layout_reset.emit())
	_settings_panel.text_size_changed.connect(func(v, p): text_size_changed.emit(v, p))
	_settings_panel.hud_width_changed.connect(func(w): hud_width_changed.emit(w))
	_settings_panel.wide_map_changed.connect(func(m): wide_map_changed.emit(m))
	# Session UI-5: Settings' Help & Keys button and its "Show first-open notes
	# again" reach main.gd through the menu, as the other settings signals do.
	# (The menu closes first, as its own Help & Keys button does: the book is on
	# layer 50, under this menu's 120 — UI-5 review.)
	_settings_panel.help_requested.connect(func():
		close_menu()
		help_requested.emit())
	_settings_panel.first_open_reset_requested.connect(func(): first_open_reset_requested.emit())
	# PB-4 (the release build): the build stamp on the pause menu too, so a
	# player reporting from mid-game can quote it without leaving the campaign.
	_version_line = Label.new()
	_version_line.name = "VersionLine"
	_version_line.theme_type_variation = &"Caption"
	_version_line.add_theme_color_override("font_color", Utils.UI_VERSION_LINE)
	_version_line.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_version_line.mouse_filter = Control.MOUSE_FILTER_IGNORE
	$PanelContainer/VBoxContainer.add_child(_version_line)
	_refresh_version_line()
	_set_new_game_confirmation_visible(false)
	hide()

func _build_roads(vb: VBoxContainer, resume: Button) -> void:
	"""Session UI-5: the title face, the roads (Help & Keys, The School of War…),
	the paired rows that keep the menu inside the compact view, and the one card
	that asks before a road that leaves the campaign is taken."""
	# The game's title, in the title face (the Main Menu's Cinzel, bold).
	var title: Label = $PanelContainer/VBoxContainer/TitleLabel
	title.text = "Ink & Iron"
	title.theme_type_variation = &"DialogTitleLarge"
	var cinzel = load(TITLE_FONT_PATH)
	if cinzel is Font:
		var face := FontVariation.new()
		face.base_font = cinzel
		face.variation_opentype = {"wght": 700}
		title.add_theme_font_override("font", face)
	_subtitle = Label.new()
	_subtitle.name = "SubtitleLabel"
	_subtitle.text = "Campaign menu"
	_subtitle.theme_type_variation = &"Caption"
	_subtitle.add_theme_color_override("font_color", Utils.UI_TEXT_DIM)
	_subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	vb.add_child(_subtitle)
	vb.move_child(_subtitle, title.get_index() + 1)

	save_button.text = "Save Game…"
	load_button.text = "Load…"
	_help_button = Button.new()
	_help_button.name = "HelpButton"
	_help_button.text = "Help & Keys"
	_help_button.pressed.connect(_on_help)
	_school_button = Button.new()
	_school_button.name = "SchoolButton"
	_school_button.text = "The School of War…"
	_school_button.pressed.connect(_on_school)
	var tips := {
		save_button: "Write the campaign to a named save.",
		load_button: "Choose a saved campaign to return to.",
		new_game_button: "Begin a fresh campaign.",
		_help_button: "The keys, the terms and the orders.",
		_school_button: "A short lesson on the Danube; this campaign is autosaved first.",
		settings_button: "Sound, display, controls.",
		main_menu_button: "Leave this campaign for the title screen.",
		quit_button: "Close the game.",
	}
	_nav = [save_button, load_button, new_game_button, _help_button, _school_button,
		settings_button, main_menu_button, quit_button]
	for b in _nav:
		(b as Button).set_meta("road_tip", str(tips[b]))
		(b as Button).tooltip_text = str(tips[b])

	# Paired rows: [Save | Load], [Help | School], [Main Menu | Quit].
	_pair(vb, save_button, load_button, save_button.get_index())
	_pair(vb, _help_button, _school_button, settings_button.get_index())
	_pair(vb, main_menu_button, quit_button, main_menu_button.get_index())

	# The card that asks, just above the exit row.
	_ask_box = VBoxContainer.new()
	_ask_box.name = "AskBox"
	_ask_box.add_theme_constant_override("separation", 6)
	_ask_box.visible = false
	vb.add_child(_ask_box)
	vb.move_child(_ask_box, $PanelContainer/VBoxContainer/HSeparator2.get_index())
	_ask_title = Label.new()
	_ask_title.theme_type_variation = &"BodyLarge"
	_ask_title.add_theme_color_override("font_color", Utils.UI_GOLD_BRIGHT)
	_ask_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_ask_title.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_ask_box.add_child(_ask_title)
	_ask_detail = Label.new()
	_ask_detail.theme_type_variation = &"Caption"
	_ask_detail.add_theme_color_override("font_color", Utils.UI_TEXT_DIM)
	_ask_detail.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_ask_detail.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_ask_box.add_child(_ask_detail)
	_ask_buttons = HBoxContainer.new()
	_ask_buttons.alignment = BoxContainer.ALIGNMENT_CENTER
	_ask_buttons.add_theme_constant_override("separation", 10)
	_ask_box.add_child(_ask_buttons)

	# Two buttons a row need a wider sheet than the old single column.
	var panel: PanelContainer = $PanelContainer
	panel.offset_left = -PAIR_PANEL_HALF_W
	panel.offset_right = PAIR_PANEL_HALF_W
	_apply_density(resume)


func _pair(vb: VBoxContainer, a: Button, b: Button, at_index: int) -> void:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	vb.add_child(row)
	for btn in [a, b]:
		if btn.get_parent() != null:
			btn.get_parent().remove_child(btn)
		btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row.add_child(btn)
	vb.move_child(row, mini(at_index, vb.get_child_count() - 1))


func _apply_density(resume: Button = null) -> void:
	"""The roads' height and the gap between them: 44 / 10 at the full view,
	30 / 4 on the compact one (no button may leave the view)."""
	var compact := Utils.compact_view()
	var h := 30.0 if compact else 44.0
	var buttons: Array = _nav.duplicate()
	var rb: Button = resume if resume != null else get_node_or_null("PanelContainer/VBoxContainer/ResumeButton") as Button
	if rb != null:
		buttons.append(rb)
	for b in buttons:
		(b as Button).custom_minimum_size.y = h
	$PanelContainer/VBoxContainer.add_theme_constant_override("separation", 4 if compact else 10)
	if _subtitle != null:
		_subtitle.visible = not compact


func _set_roads_available(available: bool) -> void:
	"""A road that cannot be taken while a question stands is DISABLED, its
	reason the tooltip (the shared disabled language)."""
	for b in _nav:
		Utils.set_available(b as Button, available, str((b as Button).get_meta("road_tip", "")), ROAD_BUSY_TIP)


func _fold_for_compact(on: bool) -> void:
	"""On the compact view a standing question takes the sheet: the roads step
	aside (they would carry the answer buttons off the view)."""
	var vb: VBoxContainer = $PanelContainer/VBoxContainer
	if on:
		if not Utils.compact_view() or not _ask_hidden.is_empty():
			return
		for child in vb.get_children():
			if child == _ask_box or child == new_game_confirm_box or child.name == "TitleLabel":
				continue
			if child is Control and (child as Control).visible:
				_ask_hidden.append(child)
				(child as Control).visible = false
	else:
		for child in _ask_hidden:
			if is_instance_valid(child):
				(child as Control).visible = true
		_ask_hidden.clear()


func _ask(title_text: String, detail_text: String, options: Array) -> void:
	"""Show the one card: `options` = [[label, id, primary], ...]. Roads are
	disabled with a reason beneath it; Esc and Stay take it down."""
	_close_asks()
	_ask_title.text = title_text
	_ask_detail.text = detail_text
	for old in _ask_buttons.get_children():
		_ask_buttons.remove_child(old)
		old.queue_free()
	var last: Button = null
	for opt in options:
		var btn := Button.new()
		btn.text = str(opt[0])
		btn.custom_minimum_size = Vector2(110, 0)
		if bool(opt[2]):
			btn.theme_type_variation = &"PrimaryButton"
		btn.pressed.connect(_on_ask_answer.bind(str(opt[1])))
		_ask_buttons.add_child(btn)
		last = btn
	new_game_confirm_box.visible = false
	_ask_box.visible = true
	_set_roads_available(false)
	_fold_for_compact(true)
	AudioManager.play("question")
	Utils.clamp_centered_panel($PanelContainer)
	if last != null:
		last.grab_focus()   # the safe answer (Stay) is the one under Enter


func _close_asks() -> void:
	if _ask_box == null:
		return
	_ask_box.visible = false
	if not new_game_confirm_box.visible:
		_fold_for_compact(false)
		_set_roads_available(true)


func _on_ask_answer(answer: String) -> void:
	var to_menu := _ask_to_menu
	match answer:
		"go":
			close_menu()
			tutorial_requested.emit()
		"save_leave":
			close_menu()
			save_and_leave_requested.emit(to_menu)
		"leave":
			if to_menu:
				close_menu()
				main_menu_requested.emit()
			else:
				get_tree().quit()
		_:
			_close_asks()


func open_menu():
	_reset_menu_state()
	_apply_density()
	AudioManager.play("door_open")
	# Re-sync every settings control from disk/backend: the command-window
	# "Text Size" +/- buttons write the same UiSettings scale value.
	if _settings_panel:
		_settings_panel.refresh()
	_refresh_version_line()
	show()
	# July 18, 2026 viewport sweep: fit to the CURRENT logical viewport.
	Utils.clamp_centered_panel($PanelContainer)

func _refresh_version_line() -> void:
	"""PB-4: `MenuBoot.server_version` arrives with the connection test, which
	may land after this menu's `_ready` — re-read it on every open."""
	if _version_line == null:
		return
	var text := "Ink & Iron — " + Utils.build_label()
	var stamp := MenuBoot.server_version
	if stamp != "" and stamp != "dev":
		text += "  ·  build " + stamp
	_version_line.text = text


func close_menu():
	_reset_menu_state()
	AudioManager.play("door_close")
	hide()
	closed.emit()

func _reset_menu_state():
	if settings_box.visible:
		_show_settings_page(false)
	settings_box.visible = false
	if $PanelContainer.has_meta("clamp_ceiling_override"):
		$PanelContainer.remove_meta("clamp_ceiling_override")
	_close_asks()
	_set_new_game_confirmation_visible(false)

func _set_new_game_confirmation_visible(confirm_visible: bool):
	new_game_confirm_box.visible = confirm_visible
	if confirm_visible and _ask_box != null:
		_ask_box.visible = false
	# Session UI-5: the roads a standing question closes are disabled with a
	# reason (Utils.set_available), not silently greyed.
	_set_roads_available(not confirm_visible)
	_fold_for_compact(confirm_visible)
	if confirm_visible:
		settings_box.visible = false
		confirm_new_game_button.grab_focus()

func _on_save():
	# Session UI-5: "Save Game…" opens the save dialog (main.gd shows it).
	close_menu()
	save_dialog_requested.emit()

func _on_help():
	close_menu()
	help_requested.emit()

func _on_school():
	_ask("Leave this campaign for the lesson?", "It was autosaved this morning.",
		[["Go", "go", true], ["Stay", "stay", false]])

func _on_load():
	close_menu()
	load_requested.emit()

func _on_new_game():
	_set_new_game_confirmation_visible(true)

func _on_confirm_new_game():
	AudioManager.play("paper_crumple")  # the old campaign, crumpled and binned
	close_menu()
	new_game_requested.emit()

func _on_cancel_new_game():
	_set_new_game_confirmation_visible(false)
	new_game_button.grab_focus()

func _on_settings():
	settings_box.visible = not settings_box.visible
	_show_settings_page(settings_box.visible)
	# UXR-X2 (October 9, 2026): the panel is authored 360x400 and the clamp
	# keeps that authored rect as its CEILING, while the settings scroll
	# inside it wants 440 — so the only shrinkable child, the scroll, was cut
	# toward the 48-px floor and the whole Settings read as one slider. With
	# the settings open the ceiling is raised (the IGR-G1 meta, scoped to this
	# state and removed with it); the viewport budget still bounds it.
	if settings_box.visible:
		$PanelContainer.set_meta("clamp_ceiling_override", Vector2(SETTINGS_PAGE_WIDTH, 900))
	elif $PanelContainer.has_meta("clamp_ceiling_override"):
		$PanelContainer.remove_meta("clamp_ceiling_override")
	# The settings content changes the panel's height class — re-fit.
	Utils.clamp_centered_panel($PanelContainer)

# Session UI-2 (November 11, 2026): Settings opens as its own page of the
# Campaign Menu — the menu's roads step aside, the page takes the panel's room
# (the readers: settings crammed into a small scroll between menu items) and
# the Settings button reads "‹ Back to the menu".
const SETTINGS_PAGE_WIDTH := 600.0
var _page_hidden: Array = []


func _show_settings_page(on: bool) -> void:
	var vb := $PanelContainer/VBoxContainer
	if on:
		_page_hidden.clear()
		for child in vb.get_children():
			if child == settings_box or child == settings_button or child.name == "TitleLabel" \
					or child.name == "HSeparator":
				continue
			if child is Control and (child as Control).visible:
				_page_hidden.append(child)
				(child as Control).visible = false
		settings_button.text = "\u2039 Back to the menu"
		var scroll := settings_box.get_child(0) as Control if settings_box.get_child_count() > 0 else null
		if scroll != null:
			var view := get_viewport().get_visible_rect().size
			scroll.custom_minimum_size.y = clampf(view.y * 0.62, 240.0, 640.0)
			# Session UI-3 (November 12, 2026): the page's scroll takes the
			# panel's whole room — at 62 % of the view it stood over a blank band
			# the height of four settings (the frames, at 1.0 and at 2.0).
			settings_box.size_flags_vertical = Control.SIZE_EXPAND_FILL
			scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	else:
		for child in _page_hidden:
			if is_instance_valid(child):
				(child as Control).visible = true
		_page_hidden.clear()
		settings_button.text = "Settings"
		settings_box.size_flags_vertical = Control.SIZE_FILL


func _on_main_menu():
	_ask_leave(true)

func _on_quit():
	_ask_leave(false)

func _ask_leave(to_menu: bool) -> void:
	"""Main Menu and Quit to Desktop both ask first and say what is lost."""
	_ask_to_menu = to_menu
	_ask("Leave the campaign?", "Orders given since this morning's autosave are lost.",
		[["Save & leave", "save_leave", true], ["Leave", "leave", false], ["Stay", "stay", false]])

func _on_overlay_input(event):
	if event is InputEventMouseButton and event.pressed:
		close_menu()
