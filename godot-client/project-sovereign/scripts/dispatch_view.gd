extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Dispatch Re-read Screen (Session A)
# =============================================================================
# Read-only re-read of last morning dispatch. CanvasLayer 50.
# Same styling as campaign_log (dark panel, gold border).
# BBCode formatting duplicated from main.gd _display_morning_dispatch().
# TECH DEBT: Extract shared formatting into utility if dispatch format changes.
# =============================================================================

signal closed

# UI References
@onready var background_overlay = $BackgroundOverlay
@onready var close_button = $PanelContainer/VBoxContainer/HeaderRow/CloseButton
@onready var scroll_container = $PanelContainer/VBoxContainer/ScrollContainer
@onready var content_label = $PanelContainer/VBoxContainer/ScrollContainer/ContentLabel

# Color palette (duplicated from main.gd — tech debt)
const COLOR_GOLD = "d9c08c"
const COLOR_SUCCESS = "8fbc8f"
const COLOR_ERROR = "cd6b6b"
const COLOR_BATTLE = "daa06d"
const COLOR_INFO = "a0a0a8"
const COLOR_BERTHIER = "B8860B"
const COLOR_OBSERVATION = "DAA520"

func _ready():
	close_button.pressed.connect(close_view)
	background_overlay.gui_input.connect(_on_overlay_input)
	hide()

func open(api_client):
	"""Fetch dispatch from backend and display it."""
	content_label.text = "[color=#" + COLOR_INFO + "]Loading dispatch...[/color]"
	show()
	api_client.get_dispatch(_on_dispatch_received)

func close_view():
	"""Hide the overlay and emit closed signal."""
	hide()
	closed.emit()

func _on_dispatch_received(response):
	"""Build the dispatch display from backend response."""
	# Guard: screen was closed while fetching
	if not visible:
		return

	if not response.get("success", false):
		content_label.text = "[color=#" + COLOR_ERROR + "]Failed to load dispatch.[/color]"
		return

	var data = response.get("dispatch", {})
	if data.is_empty():
		content_label.text = "[color=#" + COLOR_INFO + "]No dispatch available yet.\nThe morning dispatch appears at the start of each turn.[/color]"
		return

	# Build BBCode — same format as main.gd _display_morning_dispatch()
	var bbcode = ""
	var turn_num = int(data.get("turn", 0))
	var situation = data.get("situation", {})
	var marshals_list = data.get("marshals", [])
	var intel_list = data.get("intelligence", [])
	var berthier_note = str(data.get("berthier_note", "Your orders, Sire."))

	# ═══ DISPATCH HEADER ═══
	bbcode += "[color=#" + COLOR_BERTHIER + "]════════════════════════════════════[/color]\n"
	bbcode += "[color=#" + COLOR_BERTHIER + "]  MORNING DISPATCH — Turn " + str(turn_num) + "[/color]\n"
	bbcode += "[color=#" + COLOR_INFO + "]  Chief of Staff Berthier reporting[/color]\n"
	bbcode += "[color=#" + COLOR_BERTHIER + "]════════════════════════════════════[/color]\n"
	bbcode += "\n"

	# ═══ SITUATION ═══
	bbcode += "[color=#" + COLOR_BERTHIER + "]SITUATION[/color]\n"
	var player_regions = int(situation.get("player_regions", 0))
	var enemy_regions = int(situation.get("enemy_regions", 0))
	var treasury = int(situation.get("treasury", 0))
	var treasury_delta = int(situation.get("treasury_delta", 0))
	var bankrupt = situation.get("bankrupt", false)
	var strength_pct = int(situation.get("strength_ratio_pct", 0))

	var delta_sign = "+" if treasury_delta >= 0 else ""
	var delta_color = COLOR_SUCCESS if treasury_delta >= 0 else COLOR_ERROR
	bbcode += "[color=#" + COLOR_INFO + "]  France holds " + str(player_regions) + " regions. Treasury: " + _format_number(treasury) + "g [/color][color=#" + delta_color + "](" + delta_sign + str(treasury_delta) + ")[/color]\n"

	if bankrupt:
		bbcode += "[color=#" + COLOR_ERROR + "]  BANKRUPT — Treasury exhausted. Troops desert.[/color]\n"
	else:
		bbcode += "[color=#" + COLOR_INFO + "]  Enemy nations hold " + str(enemy_regions) + " regions. Estimated enemy strength: " + str(strength_pct) + "% of French forces.[/color]\n"

	# Authority (V2b)
	var authority = int(situation.get("authority", 100))
	var authority_label = str(situation.get("authority_label", "Normal"))
	var auth_color = COLOR_INFO
	if authority >= 80:
		auth_color = COLOR_SUCCESS
	elif authority < 50:
		auth_color = COLOR_ERROR
	bbcode += "[color=#" + COLOR_INFO + "]  Your authority: [/color][color=#" + auth_color + "]" + str(authority) + " (" + authority_label + ")[/color]\n"
	bbcode += "\n"

	# ═══ MARSHAL STATUS ═══
	if marshals_list.size() > 0:
		bbcode += "[color=#" + COLOR_BERTHIER + "]MARSHAL STATUS[/color]\n"
		for m in marshals_list:
			var m_name = str(m.get("name", "?"))
			var m_loc = str(m.get("location", "?"))
			var m_str = int(m.get("strength", 0))
			var m_status = str(m.get("status", "awaiting"))
			var m_note = str(m.get("status_note", ""))
			var m_trust = int(m.get("trust", 75))
			var m_trust_notable = m.get("trust_notable", false)
			var m_morale = int(m.get("morale", 100))
			var m_morale_warning = m.get("morale_warning", false)

			# Status icon
			var icon = ""
			match m_status:
				"awaiting":
					icon = "-"
				"drilling":
					icon = "*"
				"fortified":
					icon = "#"
				"retreating":
					icon = "<"
				"broken":
					icon = "!"
				"en_route":
					icon = ">"
				"idle_restless":
					icon = "-"
				"artillery":
					icon = "+"
				_:
					icon = "-"

			# Build the line
			var line = "  " + icon + " "
			line += m_name
			while line.length() < 18:
				line += " "
			line += m_loc
			while line.length() < 34:
				line += " "
			line += _format_number(m_str)
			while line.length() < 44:
				line += " "
			line += m_note

			# Append trust/morale warnings
			if m_trust_notable and m_trust < 55:
				line += " Trust:" + str(m_trust)
			if m_morale_warning:
				line += " Morale:" + str(m_morale) + "%"

			# Color based on status
			var line_color = COLOR_INFO
			if m_status == "broken":
				line_color = COLOR_ERROR
			elif m_status == "retreating":
				line_color = COLOR_ERROR
			elif m_status == "idle_restless":
				line_color = COLOR_BATTLE

			bbcode += "[color=#" + line_color + "]" + line + "[/color]\n"
		bbcode += "\n"

	# ═══ INTELLIGENCE ═══
	bbcode += "[color=#" + COLOR_BERTHIER + "]INTELLIGENCE[/color]\n"
	if intel_list.size() == 0:
		bbcode += "[color=#" + COLOR_INFO + "]  No enemy forces in observation range.[/color]\n"
	else:
		for intel_entry in intel_list:
			var i_name = str(intel_entry.get("name", "?"))
			var i_loc = str(intel_entry.get("location", "?"))
			var i_strength = str(intel_entry.get("strength_display", "?"))
			var i_vis = str(intel_entry.get("visibility", "unknown"))
			var i_turn = int(intel_entry.get("intel_turn", 0))

			var vis_label = ""
			var vis_color = COLOR_INFO
			match i_vis:
				"full":
					vis_label = "[confirmed]"
					vis_color = COLOR_SUCCESS
				"partial":
					vis_label = "[partial]"
					vis_color = COLOR_INFO
				"stale":
					vis_label = "[stale - T" + str(i_turn) + "]"
					vis_color = COLOR_BATTLE
				"last_known":
					vis_label = "[last known - T" + str(i_turn) + "]"
					vis_color = COLOR_ERROR
				_:
					vis_label = ""

			var intel_line = "  " + i_name
			while intel_line.length() < 18:
				intel_line += " "
			intel_line += i_loc
			while intel_line.length() < 34:
				intel_line += " "
			intel_line += i_strength

			bbcode += "[color=#" + COLOR_INFO + "]" + intel_line + " [/color][color=#" + vis_color + "]" + vis_label + "[/color]\n"
	bbcode += "\n"

	# ═══ TURN EVENTS ═══
	var turn_events = data.get("turn_events", [])
	if turn_events.size() > 0:
		bbcode += "[color=#" + COLOR_BERTHIER + "]TURN EVENTS[/color]\n"
		for evt in turn_events:
			var evt_msg = str(evt.get("message", ""))
			var evt_sev = str(evt.get("severity", "info"))
			var evt_color = COLOR_INFO
			if evt_sev == "warning":
				evt_color = COLOR_ERROR
			elif evt_sev == "good":
				evt_color = COLOR_SUCCESS
			bbcode += "[color=#" + evt_color + "]  " + evt_msg + "[/color]\n"
		bbcode += "\n"

	# ═══ BERTHIER'S NOTE ═══
	bbcode += "[color=#" + COLOR_OBSERVATION + "]  Berthier: \"" + berthier_note + "\"[/color]\n"
	bbcode += "[color=#" + COLOR_BERTHIER + "]════════════════════════════════════[/color]\n"

	content_label.text = bbcode

# TECH DEBT: _format_number() duplicated in dispatch_view.gd, strategic_ledger.gd,
# marshal_management.gd. Extract to shared utils.gd autoload during Map Renderer refactor.
func _format_number(n: int) -> String:
	"""Format number with comma separators (e.g. 80000 -> 80,000)."""
	var s = str(int(n))
	var result = ""
	var count = 0
	for i in range(s.length() - 1, -1, -1):
		if count > 0 and count % 3 == 0:
			result = "," + result
		result = s[i] + result
		count += 1
	return result

func _on_overlay_input(event):
	"""Click on dark overlay to close."""
	if event is InputEventMouseButton and event.pressed:
		close_view()
