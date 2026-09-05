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
	Utils.apply_icon_only_button(close_button, Utils.ICON_PHOSPHOR + "x.svg")
	background_overlay.gui_input.connect(_on_overlay_input)
	open_envoys_button.pressed.connect(_on_open_envoys_pressed)
	# PC15-18 (NV-P1 family census): a fit_content RichTextLabel inside a
	# ScrollContainer defaults to MOUSE_FILTER_STOP and eats the wheel
	# before its parent can scroll. PASS still delivers _gui_input.
	content_label.mouse_filter = Control.MOUSE_FILTER_PASS
	hide()

func open(api_client):
	"""Fetch dispatch from backend and display it."""
	AudioManager.play("parchment_open")  # the dispatch parchment, unrolled
	content_label.text = "[color=#" + Utils.COLOR_INFO + "]Loading dispatch...[/color]"
	show()
	Utils.clamp_centered_panel($PanelContainer)
	api_client.get_dispatch(_on_dispatch_received)

func close_view():
	"""Hide the overlay and emit closed signal."""
	if visible:
		AudioManager.play("parchment_close")
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
	# HC-0: dated header on anchored campaigns ("" keeps plain "Turn N").
	var calendar_label = str(data.get("calendar_label", ""))
	var turn_text = "Turn " + str(turn_num)
	if calendar_label != "":
		turn_text += " — " + calendar_label
	bbcode += "[color=#" + Utils.COLOR_BERTHIER + "]  MORNING DISPATCH — " + turn_text + "[/color]\n"
	bbcode += "[color=#" + Utils.COLOR_INFO + "]  Chief of Staff Berthier reporting[/color]\n"
	bbcode += "[color=#" + Utils.COLOR_BERTHIER + "]════════════════════════════════════[/color]\n"
	# R159 (POSITION 7): each core screen names the mechanic it displays.
	bbcode += "[color=#" + Utils.COLOR_DIMMED + "]What changed overnight, before you spend a single order. Press R to reread it any time.[/color]\n"
	bbcode += "\n"

	# ═══ W6-3 HEADLINE — the turn's top story, then up to 2 sub-beats ═══
	var headline = data.get("headline", {})
	if headline is Dictionary and headline.size() > 0:
		bbcode += "[color=#" + Utils.COLOR_WARNING + "]" + str(headline.get("text", "")) + "[/color]\n"
		var sub_beats = headline.get("sub_beats", [])
		if sub_beats is Array:
			for beat in sub_beats:
				bbcode += "[color=#" + Utils.COLOR_INFO + "]  • " + str(beat) + "[/color]\n"
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
	# PT-C4: this figure SUMS the declared components; the end-turn banner
	# MEASURES the treasury. Both can be right and still disagree — measured
	# on 10 of 18 turns — so it says which one it is.
	var delta_label = str(situation.get("treasury_delta_label", ""))
	var delta_suffix = "" if delta_label == "" else " " + delta_label
	bbcode += "[color=#" + Utils.COLOR_INFO + "]  France holds " + str(player_regions) + " regions. Treasury: " + _format_number(treasury) + "g [/color][color=#" + delta_color + "](" + delta_sign + str(treasury_delta) + delta_suffix + ")[/color]\n"

	if bankrupt:
		bbcode += "[color=#" + Utils.COLOR_ERROR + "]  BANKRUPT — Treasury exhausted. Troops desert.[/color]\n"
	else:
		# WO-10 (WO slice 12): the estimate says how good it is.
		var strength_note = str(situation.get("enemy_strength_note", ""))
		var note_suffix = "" if strength_note == "" else " " + strength_note
		bbcode += "[color=#" + Utils.COLOR_INFO + "]  Enemy nations hold " + str(enemy_regions) + " regions. Estimated enemy strength: " + str(strength_pct) + "% of French forces" + note_suffix + ".[/color]\n"

	# Authority (V2b)
	var authority = int(situation.get("authority", 100))
	var authority_label = str(situation.get("authority_label", "Normal"))
	var auth_color = Utils.COLOR_INFO
	if authority >= 80:
		auth_color = Utils.COLOR_SUCCESS
	elif authority < 50:
		auth_color = Utils.COLOR_ERROR
	bbcode += "[color=#" + Utils.COLOR_INFO + "]  Your authority: [/color][color=#" + auth_color + "]" + str(authority) + " (" + authority_label + ")[/color]\n"

	# ES-7 second pass (§0.6.8 item 4a): expectation RISES — the briefing
	# announces WHEN a marshal starts expecting more, not just when he sours.
	var rises = situation.get("expectation_rises", [])
	if rises is Array and rises.size() > 0:
		for r in rises:
			if not (r is Dictionary):
				continue
			var r_name = str(r.get("marshal", "?"))
			var r_exp = int(r.get("expectation", 0))
			var r_sat = int(r.get("satisfaction", 0))
			var r_line = "  " + r_name + "'s victories raise his expectation — he now looks for " + str(r_exp) + "g/turn (holds " + str(r_sat) + "g)."
			bbcode += "[color=#" + Utils.COLOR_GOLD + "]" + r_line + "[/color]\n"

	# ES-7 (Economy Revisit S7): Unmet Marshals roll-up — marshals whose
	# reward expectation exceeds their estate income; eroding = loyalty
	# actively bleeding (grace window elapsed). §0.6.8: plus the grace
	# countdown (the action window) and any standing rente.
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
			var u_note = ""
			if u_eroding:
				u_note = " — loyalty eroding"
			else:
				var u_grace = int(u.get("grace_turns_left", -1))
				if u_grace >= 0:
					u_note = " — patience holds " + str(u_grace) + " more turn" + ("s" if u_grace != 1 else "")
			var u_pension = int(u.get("pension", 0))
			var u_rente = " (incl. " + str(u_pension) + "g rente)" if u_pension > 0 else ""
			bbcode += "[color=#" + u_color + "]    " + u_name + " expects " + str(u_exp) + "g/turn, holds " + str(u_sat) + "g" + u_rente + u_note + "[/color]\n"
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

			# Build the line. Separator-based, NOT space-padded columns: the UI
			# font (EB Garamond) is proportional, so char-count padding rendered
			# as ragged staircases — the same failure the marshal card's █░ bars
			# hit — and an exactly-full field fused into the next with no gap.
			var line = "  " + icon + " "
			line += m_name + " — " + m_loc + " — " + _format_number(m_str)
			if m_note != "":
				line += " — " + m_note

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

			# W6-3 §5.2: danger flag line (fog-legal threat under the row)
			var m_danger = str(m.get("danger", ""))
			if m_danger != "":
				bbcode += "[color=#" + Utils.COLOR_WARNING + "]      ⚠ " + m_danger + "[/color]\n"
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

			# Separator-based (see the marshal table above): proportional font
			# breaks char-count column stops.
			var intel_line = "  " + i_name + " — " + i_loc + " — " + i_strength

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
			# Renamed from `headline`: W6-3 added a dispatch-headline local at
			# the top of this function and GDScript forbids the shadow.
			var settlement_headline = str(settlement.get("headline", "Peace Settlement"))
			var detail = str(settlement.get("detail", ""))
			bbcode += "[color=#" + Utils.COLOR_GOLD + "]  " + settlement_headline + "[/color]\n"
			if detail != "":
				bbcode += "[color=#" + Utils.COLOR_INFO + "]    " + detail + "[/color]\n"
		bbcode += "\n"

	# PRISONERS OF WAR — FA-32 (slice 11).
	# The backend has built `dispatch["prisoners"]` since W6-7 and NO client
	# script ever read it (measured: a key census of both renderers). The
	# `marshal_captured` event window is two turns wide, so after that the
	# dispatch dropped a captured marshal entirely — he was on the Generals
	# card and nowhere else the player looks each morning.
	var prisoners = data.get("prisoners", [])
	if prisoners != null and prisoners.size() > 0:
		bbcode += "[color=#" + Utils.COLOR_BERTHIER + "]PRISONERS OF WAR[/color]\n"
		for p in prisoners:
			var p_name = str(p.get("name", "?"))
			var p_captor = Utils.display_nation_name(str(p.get("captor", "")))
			var p_turn = int(p.get("captured_turn", 0))
			bbcode += "[color=#" + Utils.COLOR_ERROR + "]  " + p_name
			bbcode += " — held by " + p_captor
			if p_turn > 0:
				bbcode += " since turn " + str(p_turn)
			bbcode += ".[/color]\n"
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

func _format_number(n: int) -> String:
	"""Format number with comma separators — shared Utils helper (UI-6 dedupe)."""
	return Utils.format_number(n)

func _on_overlay_input(event):
	"""Click on dark overlay to close."""
	if event is InputEventMouseButton and event.pressed:
		close_view()


func _on_open_envoys_pressed():
	close_view()
	open_envoys_requested.emit()
