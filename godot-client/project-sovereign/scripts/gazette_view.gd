extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Le Moniteur (HC-G) — the Gazette screen
# =============================================================================
# The PERIODICAL: retrospective issues published every few turns, with a
# browsable back-issue archive (the half the Dispatch structurally cannot
# be). CanvasLayer 50, top_bar-owned like every core screen; renders the
# serialized archive the backend composed at publish time — this screen
# never recomputes anything. Paging is client-local over the returned
# list (cap 20 — no server paging needed).
# =============================================================================

signal closed

@onready var background_overlay = $BackgroundOverlay
@onready var close_button = $PanelContainer/VBoxContainer/HeaderRow/CloseButton
@onready var scroll_container = $PanelContainer/VBoxContainer/ScrollContainer
@onready var content_label = $PanelContainer/VBoxContainer/ScrollContainer/ContentLabel
@onready var prev_button: Button = $PanelContainer/VBoxContainer/PageRow/PrevButton
@onready var page_label: Label = $PanelContainer/VBoxContainer/PageRow/PageLabel
@onready var next_button: Button = $PanelContainer/VBoxContainer/PageRow/NextButton

var _issues: Array = []
var _index: int = -1  # index into _issues (newest = size-1)


func _ready():
	# UXR3-F3: the reading scroll comes to rest on whole lines.
	Utils.keep_whole_lines(content_label)
	# Session UI-2: each column of the paper is a card (the marks are in `_section`).
	Utils.card_page(content_label)
	close_button.pressed.connect(close_view)
	Utils.apply_icon_only_button(close_button, Utils.ICON_PHOSPHOR + "x.svg")
	background_overlay.gui_input.connect(_on_overlay_input)
	# UXR-2: clamped AND gripped — the player's size is remembered.
	ResizeGrip.attach_centered($PanelContainer, "gazette")
	prev_button.pressed.connect(_on_prev)
	# PC15-18 (NV-P1 family census): a fit_content RichTextLabel inside a
	# ScrollContainer defaults to MOUSE_FILTER_STOP and eats the wheel
	# before its parent can scroll. PASS still delivers _gui_input.
	content_label.mouse_filter = Control.MOUSE_FILTER_PASS
	next_button.pressed.connect(_on_next)
	hide()


var _api_client_ref = null


func open(api_client):
	"""Fetch the archive and open on the latest issue."""
	_api_client_ref = api_client
	AudioManager.play("parchment_open")
	content_label.text = "[color=#" + Utils.COLOR_INFO + "]The presses turn...[/color]"
	show()
	Utils.clamp_centered_panel($PanelContainer)
	api_client.get_gazette(_on_gazette_received)


func refresh_pinned() -> void:
	"""UXR-D4 (Pre-Deploy S12b): the Side Desk re-reads a pinned screen
	after every command and every end turn — the issue the reader holds (the newest stays the newest), its scroll where the
	reader left it."""
	if not visible or _api_client_ref == null:
		return
	var on_latest: bool = _index < 0 or _index == _issues.size() - 1
	_api_client_ref.get_gazette(_on_pinned_gazette.bind(on_latest, _index, scroll_container.scroll_vertical))


func _on_pinned_gazette(response, on_latest: bool, held_index: int, held_scroll: int) -> void:
	_on_gazette_received(response)
	if not on_latest and held_index >= 0 and held_index < _issues.size() and held_index != _index:
		_index = held_index
		_render_issue()
	Utils.restore_scroll(scroll_container, held_scroll)


func close_view():
	if visible:
		AudioManager.play("parchment_close")
	hide()
	closed.emit()


func _on_gazette_received(response):
	if not visible:
		return
	if not response.get("success", false):
		content_label.text = "[color=#" + Utils.COLOR_ERROR + "]The presses are silent.[/color]"
		_issues = []
		_update_page_row()
		return
	_issues = response.get("issues", [])
	if _issues.is_empty():
		content_label.text = "[color=#" + Utils.COLOR_INFO + "]No issue has yet gone to print.\nThe Moniteur publishes as the campaign unfolds.[/color]"
		_update_page_row()
		return
	_index = _issues.size() - 1
	_render_issue()


func _on_prev():
	if _index > 0:
		AudioManager.play("page_turn")
		_index -= 1
		_render_issue()


func _on_next():
	if _index < _issues.size() - 1:
		AudioManager.play("page_turn")
		_index += 1
		_render_issue()


func _update_page_row():
	var have := not _issues.is_empty() and _index >= 0
	prev_button.disabled = not have or _index <= 0
	next_button.disabled = not have or _index >= _issues.size() - 1
	if have:
		page_label.text = "Issue %d of %d" % [_index + 1, _issues.size()]
	else:
		page_label.text = ""


func _render_issue():
	if _index < 0 or _index >= _issues.size():
		return
	var issue: Dictionary = _issues[_index]
	var bbcode = ""

	# Masthead — the paper's own dated identity (HC-0 dateline). Session UI-2:
	# the paper's name in blackletter (UnifrakturMaguntia, OFL), its dateline
	# under it in the title face, between two gilt hairlines.
	var masthead := str(issue.get("masthead", "LE MONITEUR"))
	var head := masthead
	var dateline := ""
	var cut := masthead.find(" — ")
	if cut > 0:
		head = masthead.substr(0, cut)
		dateline = masthead.substr(cut + 3)
	var rule := "[center][img width=420 height=1 color=#" + Utils.COLOR_GOLD + "99]" + Utils.SWATCH + "[/img][/center]\n"
	bbcode += rule
	bbcode += "[center][font=" + MASTHEAD_FONT + "][color=#ece0c4]" + head.capitalize() + "[/color][/font][/center]\n"
	if dateline != "":
		bbcode += "[center]" + Utils.HEAD_OPEN + dateline + Utils.HEAD_CLOSE + "[/center]\n"
	if bool(issue.get("special", false)):
		bbcode += "[center][color=#" + Utils.COLOR_ERROR + "]SPECIAL EDITION — " + str(issue.get("special_reason", "")) + "[/color][/center]\n"
	bbcode += rule
	# R159: each core screen names the mechanic it displays.
	bbcode += "[color=#" + Utils.COLOR_INFO + "]The capital's press — the continent's story as printed, issue by issue. Page through the archive below.[/color]\n\n"

	# The lead — the press's voice.
	var lead = str(issue.get("lead", ""))
	if lead != "":
		# Session UI-2: the issue's headline, in the title face.
		bbcode += "[font=" + Utils.TITLE_FONT + "][color=#" + Utils.COLOR_GOLD + "]" + lead + "[/color][/font]\n\n"

	bbcode += _section("THE WAR", issue.get("war", []), "war")
	bbcode += _section("THE COURTS", issue.get("courts", []), "envoy")
	# GE-3: the Congress column — the table in the paper's voice every issue
	# of the sitting, the proclamation on the Imperial Peace's own edition
	# (`gazette._congress_column`). Absent / empty → no section.
	bbcode += _section("THE CONGRESS OF PARIS", issue.get("congress", []), "europe")
	bbcode += _section("THE ARMY", issue.get("army", []), "foot")

	var bourse = str(issue.get("bourse", ""))
	if bourse != "":
		bbcode += Utils.bb_glyph("gold", 16, Utils.COLOR_INFO) + " [color=#" + Utils.COLOR_INFO + "]" + bourse + "[/color]\n"

	content_label.text = bbcode
	scroll_container.scroll_vertical = 0
	_update_page_row()


const MASTHEAD_FONT := "res://assets/fonts/UnifrakturMaguntia-Book.ttf"


func _section(title: String, rows, glyph_name: String = "") -> String:
	"""One column of the paper: a card led by its glyph and its heading in the
	title face, its rows under it (the card's marks add no line)."""
	if not (rows is Array) or rows.is_empty():
		return ""
	var out: String = Utils.card_open()
	if glyph_name != "":
		out += Utils.bb_glyph(glyph_name, 18) + " "
	out += Utils.HEAD_OPEN + title + Utils.HEAD_CLOSE + "\n"
	for i in range(rows.size()):
		out += "[color=#" + Utils.COLOR_TEXT + "]  " + str(rows[i]) + "[/color]"
		out += (Utils.CARD_CLOSE if i == rows.size() - 1 else "") + "\n"
	return out + "\n"


func _on_overlay_input(event):
	if event is InputEventMouseButton and event.pressed:
		close_view()
