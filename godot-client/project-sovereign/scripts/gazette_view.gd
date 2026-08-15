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
	close_button.pressed.connect(close_view)
	Utils.apply_icon_only_button(close_button, Utils.ICON_PHOSPHOR + "x.svg")
	background_overlay.gui_input.connect(_on_overlay_input)
	prev_button.pressed.connect(_on_prev)
	# PC15-18 (NV-P1 family census): a fit_content RichTextLabel inside a
	# ScrollContainer defaults to MOUSE_FILTER_STOP and eats the wheel
	# before its parent can scroll. PASS still delivers _gui_input.
	content_label.mouse_filter = Control.MOUSE_FILTER_PASS
	next_button.pressed.connect(_on_next)
	hide()


func open(api_client):
	"""Fetch the archive and open on the latest issue."""
	AudioManager.play("parchment_open")
	content_label.text = "[color=#" + Utils.COLOR_INFO + "]The presses turn...[/color]"
	show()
	Utils.clamp_centered_panel($PanelContainer)
	api_client.get_gazette(_on_gazette_received)


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

	# Masthead — the paper's own dated identity (HC-0 dateline).
	bbcode += "[color=#" + Utils.COLOR_BERTHIER + "]════════════════════════════════════[/color]\n"
	bbcode += "[color=#" + Utils.COLOR_BERTHIER + "]  " + str(issue.get("masthead", "LE MONITEUR")) + "[/color]\n"
	if bool(issue.get("special", false)):
		bbcode += "[color=#" + Utils.COLOR_ERROR + "]  SPECIAL EDITION — " + str(issue.get("special_reason", "")) + "[/color]\n"
	bbcode += "[color=#" + Utils.COLOR_BERTHIER + "]════════════════════════════════════[/color]\n"
	# R159: each core screen names the mechanic it displays.
	bbcode += "[color=#" + Utils.COLOR_DIMMED + "]The capital's press — the continent's story as printed, issue by issue. Page through the archive below.[/color]\n\n"

	# The lead — the press's voice.
	var lead = str(issue.get("lead", ""))
	if lead != "":
		bbcode += "[color=#" + Utils.COLOR_GOLD + "]" + lead + "[/color]\n\n"

	bbcode += _section("THE WAR", issue.get("war", []))
	bbcode += _section("THE COURTS", issue.get("courts", []))
	bbcode += _section("THE ARMY", issue.get("army", []))

	var bourse = str(issue.get("bourse", ""))
	if bourse != "":
		bbcode += "[color=#" + Utils.COLOR_INFO + "]" + bourse + "[/color]\n"

	content_label.text = bbcode
	scroll_container.scroll_vertical = 0
	_update_page_row()


func _section(title: String, rows) -> String:
	if not (rows is Array) or rows.is_empty():
		return ""
	var out = "[color=#" + Utils.COLOR_HEADER + "]— " + title + " —[/color]\n"
	for row in rows:
		out += "[color=#" + Utils.COLOR_TEXT + "]  " + str(row) + "[/color]\n"
	return out + "\n"


func _on_overlay_input(event):
	if event is InputEventMouseButton and event.pressed:
		close_view()
