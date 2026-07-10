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
signal open_envoys_requested

# UI References
@onready var background_overlay = $BackgroundOverlay
@onready var close_button = $PanelContainer/VBoxContainer/HeaderRow/CloseButton
@onready var scroll_container = $PanelContainer/VBoxContainer/ScrollContainer
@onready var content_label = $PanelContainer/VBoxContainer/ScrollContainer/ContentLabel
@onready var open_envoys_button: Button = $PanelContainer/VBoxContainer/ActionRow/OpenEnvoysButton

func _ready():
	close_button.pressed.connect(close_view)
	background_overlay.gui_input.connect(_on_overlay_input)
	open_envoys_button.pressed.connect(_on_open_envoys_pressed)
	hide()

func open(api_client):
	"""Fetch dispatch from backend and display it."""
	content_label.text = "[color=#" + Utils.COLOR_INFO + "]Loading dispatch...[/color]"
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
		content_label.text = "[color=#" + Utils.COLOR_ERROR + "]Failed to load dispatch.[/color]"
		return

	var data = response.get("dispatch", {})
	if data.is_empty():
		content_label.text = "[color=#" + Utils.COLOR_INFO + "]No dispatch available yet.\nThe morning dispatch appears at the start of each turn.[/color]"
		return

	# Build BBCode — same format as main.gd _display_morning_dispatch()
	var bbcode = ""
	var turn_num = int(data.get("turn", 0))
	var situation = data.get("situation", {})
	var marshals_list = data.get("marshals", [])
	var intel_list = data.get("intelligence", [])
	var peace_settlements = data.get("peace_settlements", [])
	var berthier_note = str(data.get("berthier_note", "Your orders, Sire."))

	# ═══ DISPATCH HEADER ═══
	bbcode += "[color=#" + Utils.COLOR_BERTHIER + "]════════════════════════════════════[/color]\n"
	bbcode += "[color=#" + Utils.COLOR_BERTHIER + "]  MORNING DISPATCH — Turn " + str(turn_num) + "[/color]\n"
	bbcode += "[color=#" + Utils.COLOR_INFO + "]  Chief of Staff Berthier reporting[/color]\n"
	bbcode += "[color=#" + Utils.COLOR_BERTHIER + "]════════════════════════════════════[/color]\n"
	bbcode += "\n"

	# ═══ SITUATION ═══
	bbcode += "[color=#" + Utils.COLOR_BERTHIER + "]SITUATION[/color]\n"
	var player_regions = int(situation.get("player_regions", 0))
	var enemy_regions = int(situation.get("enemy_regions", 0))
	var treasury = int(situation.get("treasury", 0))
	var treasury_delta = int(situation.get("treasury_delta", 0))
	var bankrupt = situation.get("bankrupt", false)
	var strength_pct = int(situation.get("strength_ratio_pct", 0))

	var delta_sign = "+" if treasury_delta >= 0 else ""
	var delta_color = Utils.COLOR_SUCCESS if treasury_delta >= 0 else Utils.COLOR_ERROR
	bbcode += "[color=#" + Utils.COLOR_INFO + "]  France holds " + str(player_regions) + " regions. Treasury: " + _format_number(treasury) + "g [/color][color=#" + delta_color + "](" + delta_sign + str(treasury_delta) + ")[/color]\n"

	if bankrupt:
		bbcode += "[color=#" + Utils.COLOR_ERROR + "]  BANKRUPT — Treasury exhausted. Troops desert.[/color]\n"
	else:
		bbcode += "[color=#" + Utils.COLOR_INFO + "]  Enemy nations hold " + str(enemy_regions) + " regions. Estimated enemy strength: " + str(strength_pct) + "% of French forces.[/color]\n"

	# Authority (V2b)
	var authority = int(situation.get("authority", 100))
	var authority_label = str(situation.get("authority_label", "Normal"))
	var auth_color = Utils.COLOR_INFO
	if authority >= 80:
		auth_color = Utils.COLOR_SUCCESS
	elif authority < 50:
		auth_color = Utils.COLOR_ERROR
	bbcode += "[color=#" + Utils.COLOR_INFO + "]  Your authority: [/color][color=#" + auth_color + "]" + str(authority) + " (" + authority_label + ")[/color]\n"

	# ES-7 (Economy Revisit S7): Unmet Marshals roll-up — marshals whose
	# reward expectation exceeds their estate income; eroding = loyalty
	# actively bleeding (grace window elapsed).
	var unmet = situation.get("unmet_marshals", [])
	if unmet is Array and unmet.size() > 0:
		bbcode += "[color=#" + Utils.COLOR_WARNING + "]  UNMET MARSHALS[/color]\n"
		for u in unmet:
			if not (u is Dictionary):
				continue
			var u_name = str(u.get("marshal", "?"))
			var u_exp = int(u.get("expectation", 0))
			var u_sat = int(u.get("satisfaction", 0))
			var u_eroding = u.get("eroding", false)
			var u_color = Utils.COLOR_ERROR if u_eroding else Utils.COLOR_WARNING
			var u_note = " — loyalty eroding" if u_eroding else ""
			bbcode += "[color=#" + u_color + "]    " + u_name + " expects " + str(u_exp) + "g/turn of estates, holds " + str(u_sat) + "g" + u_note + "[/color]\n"
	bbcode += "\n"

	# ═══ MARSHAL STATUS ═══
	if marshals_list.size() > 0:
		bbcode += "[color=#" + Utils.COLOR_BERTHIER + "]MARSHAL STATUS[/color]\n"
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
			var line_color = Utils.COLOR_INFO
			if m_status == "broken":
				line_color = Utils.COLOR_ERROR
			elif m_status == "retreating":
				line_color = Utils.COLOR_ERROR
			elif m_status == "idle_restless":
				line_color = Utils.COLOR_BATTLE

			bbcode += "[color=#" + line_color + "]" + line + "[/color]\n"
		bbcode += "\n"

	# ═══ INTELLIGENCE ═══
	bbcode += "[color=#" + Utils.COLOR_BERTHIER + "]INTELLIGENCE[/color]\n"
	if intel_list.size() == 0:
		bbcode += "[color=#" + Utils.COLOR_INFO + "]  No enemy forces in observation range.[/color]\n"
	else:
		for intel_entry in intel_list:
			var i_name = str(intel_entry.get("name", "?"))
			var i_loc = str(intel_entry.get("location", "?"))
			var i_strength = str(intel_entry.get("strength_display", "?"))
			var i_vis = str(intel_entry.get("visibility", "unknown"))
			var i_turn = int(intel_entry.get("intel_turn", 0))

			var vis_label = ""
			var vis_color = Utils.COLOR_INFO
			match i_vis:
				"full":
					vis_label = "[confirmed]"
					vis_color = Utils.COLOR_SUCCESS
				"partial":
					vis_label = "[partial]"
					vis_color = Utils.COLOR_INFO
				"stale":
					vis_label = "[stale - T" + str(i_turn) + "]"
					vis_color = Utils.COLOR_BATTLE
				"last_known":
					vis_label = "[last known - T" + str(i_turn) + "]"
					vis_color = Utils.COLOR_ERROR
				_:
					vis_label = ""

			var intel_line = "  " + i_name
			while intel_line.length() < 18:
				intel_line += " "
			intel_line += i_loc
			while intel_line.length() < 34:
				intel_line += " "
			intel_line += i_strength

			bbcode += "[color=#" + Utils.COLOR_INFO + "]" + intel_line + " [/color][color=#" + vis_color + "]" + vis_label + "[/color]\n"
	bbcode += "\n"

	# ═══ TURN EVENTS ═══
	var turn_events = data.get("turn_events", [])
	if turn_events.size() > 0:
		bbcode += "[color=#" + Utils.COLOR_BERTHIER + "]TURN EVENTS[/color]\n"
		for evt in turn_events:
			var evt_msg = str(evt.get("message", ""))
			var evt_sev = str(evt.get("severity", "info"))
			var evt_color = Utils.COLOR_INFO
			if evt_sev == "warning":
				evt_color = Utils.COLOR_ERROR
			elif evt_sev == "good":
				evt_color = Utils.COLOR_SUCCESS
			bbcode += "[color=#" + evt_color + "]  " + evt_msg + "[/color]\n"
		bbcode += "\n"

	# ═══ LAPSED ENVOYS ═══
	var lapsed_offers = data.get("lapsed_offers", [])
	if lapsed_offers.size() > 0:
		bbcode += "[color=#" + Utils.COLOR_BERTHIER + "]LAPSED ENVOYS[/color]\n"
		for lapse in lapsed_offers:
			var l_nation = str(lapse.get("nation", "?"))
			var l_ptype = str(lapse.get("proposal_type", "offer")).replace("_", " ").capitalize()
			bbcode += "[color=#" + Utils.COLOR_BATTLE + "]  " + Utils.display_nation_name(l_nation) + "'s " + l_ptype + " offer lapsed unanswered[/color]\n"
		bbcode += "\n"

	# ═══ ENVOYS AWAITING RESPONSE ═══
	var pending_envoys = data.get("pending_envoys", [])
	var pending_envoy_count = int(data.get("pending_envoy_count", pending_envoys.size()))
	open_envoys_button.visible = pending_envoy_count > 0
	if pending_envoy_count > 0:
		open_envoys_button.text = "Open Envoys (%d)" % pending_envoy_count
	if pending_envoys.size() > 0 and pending_envoy_count > 0:
		bbcode += "[color=#" + Utils.COLOR_BERTHIER + "]ENVOYS AWAITING RESPONSE[/color]\n"
		bbcode += "[color=#" + Utils.COLOR_INFO + "]  Talleyrand: " + str(pending_envoy_count) + " envoy(s) await your reply this turn. Use [b]Open Envoys[/b] below before ending the turn.[/color]\n"
		for i in range(min(pending_envoys.size(), 3)):
			var envoy = pending_envoys[i]
			var envoy_nation = str(envoy.get("nation", "?"))
			var envoy_type = str(envoy.get("proposal_type", "proposal")).capitalize()
			bbcode += "[color=#" + Utils.COLOR_INFO + "]    - " + Utils.display_nation_name(envoy_nation) + " — " + envoy_type + "[/color]\n"
		if pending_envoys.size() > 3:
			bbcode += "[color=#" + Utils.COLOR_INFO + "]    - ...and " + str(pending_envoys.size() - 3) + " more[/color]\n"
		bbcode += "[color=#" + Utils.COLOR_OBSERVATION + "]  Berthier: \"I have placed the diplomatic packet atop the morning dispatch, Sire.\"[/color]\n\n"

	# Peace Deals BPH-D: previous-turn ratification summaries
	if peace_settlements.size() > 0:
		bbcode += "[color=#" + Utils.COLOR_BERTHIER + "]PEACE SETTLEMENTS[/color]\n"
		for settlement in peace_settlements:
			var headline = str(settlement.get("headline", "Peace Settlement"))
			var detail = str(settlement.get("detail", ""))
			bbcode += "[color=#" + Utils.COLOR_GOLD + "]  " + headline + "[/color]\n"
			if detail != "":
				bbcode += "[color=#" + Utils.COLOR_INFO + "]    " + detail + "[/color]\n"
		bbcode += "\n"

	# DIPLOMATIC EVENTS
	var diplo_events = data.get("diplomatic_events", [])
	if diplo_events.size() > 0:
		bbcode += "[color=#" + Utils.COLOR_BERTHIER + "]DIPLOMATIC EVENTS[/color]\n"
		for de in diplo_events:
			var de_text = str(de.get("text", ""))
			var de_priority = str(de.get("priority", "MEDIUM"))
			var de_color = Utils.COLOR_INFO  # default grey
			match de_priority:
				"HIGH":
					de_color = Utils.COLOR_BATTLE  # amber
				"MEDIUM":
					de_color = Utils.COLOR_INFO    # grey
				"LOW":
					de_color = "808088"      # dim grey
			bbcode += "[color=#" + de_color + "]  " + de_text + "[/color]\n"
		bbcode += "\n"

	# ═══ DEFEAT WARNING ═══
	var defeat_imminent_warning = data.get("defeat_imminent_warning", null)
	if defeat_imminent_warning != null and defeat_imminent_warning is Dictionary:
		var diw_msg = str(defeat_imminent_warning.get("message", ""))
		var diw_sev = str(defeat_imminent_warning.get("severity", "warning"))
		if diw_msg != "":
			var diw_color = Utils.COLOR_ERROR if diw_sev == "critical" else Utils.COLOR_BATTLE
			bbcode += "[color=#" + Utils.COLOR_BERTHIER + "]DEFEAT WARNING[/color]\n"
			bbcode += "[color=#" + diw_color + "]  " + diw_msg + "[/color]\n\n"

	# ═══ BERTHIER'S NOTE ═══
	bbcode += "[color=#" + Utils.COLOR_OBSERVATION + "]  Berthier: \"" + berthier_note + "\"[/color]\n"
	bbcode += "[color=#" + Utils.COLOR_BERTHIER + "]════════════════════════════════════[/color]\n"

	content_label.text = Utils.humanize_nation_keys_in_text(bbcode)

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


func _on_open_envoys_pressed():
	close_view()
	open_envoys_requested.emit()
