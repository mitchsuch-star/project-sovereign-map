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
# UXR3-23 (Pre-Deploy S12): a TODAY order chip types its order into the
# command line; the dispatch closes onto it.
signal order_typed(command: String)
# S14D-X3: the law line's door — main.gd opens the ledger on the book named.
signal ledger_tab_requested(tab: int)
# RE-C (RECURRING_EVENTS_SPEC.md §12b.1): the Correspondence page's roads —
# the desk's "Read the letter ▸" takes the rail card's (POST /mailbox/activate,
# main's handler); a court chip opens its Cabinet page through main's guarded
# route (`_on_ledger_open_diplomacy_for`). Both close the view first.
signal read_letter_requested(mailbox_id: int)
signal open_diplomacy_for(nation: String)

# UI References
@onready var background_overlay = $BackgroundOverlay
@onready var close_button = $PanelContainer/VBoxContainer/HeaderRow/CloseButton
@onready var scroll_container = $PanelContainer/VBoxContainer/ScrollContainer
@onready var content_label = $PanelContainer/VBoxContainer/ScrollContainer/ContentLabel
@onready var open_envoys_button: Button = $PanelContainer/VBoxContainer/ActionRow/OpenEnvoysButton
# RE-C: the page's nodes (the scene authors them; the slips are built here)
@onready var title_label: Label = $PanelContainer/VBoxContainer/HeaderRow/TitleLabel
@onready var corr_scroll: ScrollContainer = $PanelContainer/VBoxContainer/CorrespondenceScroll
@onready var corr_box: VBoxContainer = $PanelContainer/VBoxContainer/CorrespondenceScroll/CorrespondenceBox
@onready var correspondence_button: Button = $PanelContainer/VBoxContainer/ActionRow/CorrespondenceButton
@onready var back_to_dispatch_button: Button = $PanelContainer/VBoxContainer/ActionRow/BackToDispatchButton

func _ready():
	# UXR3-F3: the reading scroll comes to rest on whole lines.
	Utils.keep_whole_lines(content_label)
	close_button.pressed.connect(close_view)
	Utils.apply_icon_only_button(close_button, Utils.ICON_PHOSPHOR + "x.svg")
	background_overlay.gui_input.connect(_on_overlay_input)
	# UXR-2: clamped AND gripped — the player's size is remembered.
	ResizeGrip.attach_centered($PanelContainer, "dispatch")
	open_envoys_button.pressed.connect(_on_open_envoys_pressed)
	# RE-C: the page turns on its button and back on "◂ The Dispatch".
	correspondence_button.pressed.connect(open_correspondence)
	back_to_dispatch_button.pressed.connect(_show_dispatch_page)
	# PC15-18 (NV-P1 family census): a fit_content RichTextLabel inside a
	# ScrollContainer defaults to MOUSE_FILTER_STOP and eats the wheel
	# before its parent can scroll. PASS still delivers _gui_input.
	content_label.mouse_filter = Control.MOUSE_FILTER_PASS
	content_label.meta_clicked.connect(_on_meta_clicked)
	hide()


func _on_meta_clicked(meta) -> void:
	var m := str(meta)
	if m.begins_with("type:"):
		order_typed.emit(m.substr(5))
		close_view()
		return
	# S14D-X3 (October 23, 2026): the law line's chip opens the eighth book.
	if m.begins_with("ledger:"):
		ledger_tab_requested.emit(int(m.substr("ledger:".length())))
		close_view()

var _api_client_ref = null

# ═══════════════════════════════════════════════════════════════════════════
# RE-C — THE CORRESPONDENCE (RECURRING_EVENTS_SPEC.md §12b.1): a page of this
# screen — one column of parchment slips read from `GET /dispatch`'s
# `correspondence` dict (ON THE DESK, IN THE OFFING, ANSWERED, LEFT UNANSWERED
# / SET ASIDE, the closing record), turned by a button in the action row and
# back by "◂ The Dispatch". Read-only but for "Read the letter ▸". The slips
# wear the letter's parchment (its un-torn inner field) and its ink; the type
# sits on the theme ladder (Caption / Lead), never a raw size.
# ═══════════════════════════════════════════════════════════════════════════
const CORR_TITLE := "THE CORRESPONDENCE"
const DISPATCH_TITLE := "MORNING DISPATCH"
const CORR_SCREEN := "correspondence"
const CORR_SHEET := "res://assets/textures/old-parchment_alpha.png"
const CORR_SEAL := "res://assets/ui/ornaments/wax_seal.png"
const CORR_FELL_ITALIC := "res://assets/fonts/IMFeENit28P.ttf"
const CORR_CINZEL := "res://assets/fonts/Cinzel[wght].ttf"
const CORR_SHEET_FIELD := Rect2(72, 64, 496, 352)   # the sheet's un-torn inner field (640 × 480 art)
const CORR_DEVICE_PX := 24.0
const CORR_SEAL_PX := 18.0
const CORR_CHIP_BG := "1A1A2E"                       # the theme's navy plaque under a gold chip
# the page's ceiling grows with the window as the letter's (`_raise_letter_ceiling`)
const CORR_HEIGHT_FRACTION := 0.8
const CORR_WIDTH_FRACTION := 0.45
const CORR_MIN_WIDTH := 680.0
const CORR_MIN_HEIGHT := 440.0
const CORR_MAX_WIDTH := 860.0

var _corr: Dictionary = {}
var _corr_open := false
var _corr_pending_open := false
var _corr_scroll_hold := 0
var _corr_sheet: StyleBoxTexture = null
var _corr_sheet_hc: StyleBoxFlat = null
var _corr_fell_italic: Font = null
var _corr_cinzel: Font = null


func open(api_client):
	"""Fetch dispatch from backend and display it."""
	_api_client_ref = api_client
	AudioManager.play("parchment_open")  # the dispatch parchment, unrolled
	content_label.text = "[color=#" + Utils.COLOR_INFO + "]Loading dispatch...[/color]"
	show()
	Utils.clamp_centered_panel($PanelContainer)
	api_client.get_dispatch(_on_dispatch_received)

func refresh_pinned() -> void:
	"""UXR-D4 (Pre-Deploy S12b): the Side Desk re-reads a pinned screen
	after every command and every end turn — the morning's dispatch, its scroll where the
	reader left it."""
	if not visible or _api_client_ref == null:
		return
	# RE-C: the page's own scroll is held too, and restored below when open
	_corr_scroll_hold = corr_scroll.scroll_vertical
	_api_client_ref.get_dispatch(_on_pinned_dispatch.bind(scroll_container.scroll_vertical))


func _on_pinned_dispatch(response, held_scroll: int) -> void:
	_on_dispatch_received(response)
	Utils.restore_scroll(scroll_container, held_scroll)
	if _corr_open:
		Utils.restore_scroll(corr_scroll, _corr_scroll_hold)


func close_view():
	"""Hide the overlay and emit closed signal."""
	if visible:
		AudioManager.play("parchment_close")
	_reset_correspondence_page()
	hide()
	closed.emit()

func _on_dispatch_received(response):
	"""Build the dispatch display from backend response."""
	# Guard: screen was closed while fetching
	if not visible:
		return

	# RE-C: the page's dict rides every GET — absent on an unarmed world and
	# in the driven harnesses' hand-built responses, when the button hides.
	_take_correspondence(response)

	if not response.get("success", false):
		content_label.text = "[color=#" + Utils.COLOR_ERROR + "]Failed to load dispatch.[/color]"
		return

	var data = response.get("dispatch", {})
	if data.is_empty():
		# LV-1 (row EP F1): the old copy — "No dispatch available yet. The
		# morning dispatch appears at the start of each turn" — was FALSE on
		# turn 1, which is the only turn it ever showed. Every live campaign
		# now carries a briefing from its first morning (the backend builds
		# the boot one where a campaign starts or loads), so this arm is
		# reached only with the backend's lever down; it claims nothing.
		content_label.text = "[color=#" + Utils.COLOR_INFO + "]Berthier has no dispatch on the table.[/color]"
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
	bbcode += "[color=#" + Utils.COLOR_INFO + "]What changed overnight, before you spend a single order. Esc closes it; Alt+R (or Alt+B) while you type reopens it.[/color]\n"
	bbcode += "\n"
	var congress_at := bbcode.length()

	# ═══ W6-3 HEADLINE — the turn's top story, then up to 2 sub-beats ═══
	var headline = data.get("headline", {})
	if headline is Dictionary and headline.size() > 0:
		bbcode += "[color=#" + Utils.COLOR_WARNING + "]" + str(headline.get("text", "")) + "[/color]\n"
		var sub_beats = headline.get("sub_beats", [])
		if sub_beats is Array:
			for beat in sub_beats:
				bbcode += "[color=#" + Utils.COLOR_INFO + "]  • " + str(beat) + "[/color]\n"
		bbcode += "\n"
	# S14E-X122 (S14f part 2): the re-read keeps the morning's headline and
	# Berthier's note by design (re-deriving them is not a pure read) while the
	# marshal rows are read live -- when a corps has marched or changed state
	# since, the backend flags the copy and the page says which half is which.
	if bool(data.get("stale_headline", false)):
		bbcode += "[color=#" + Utils.COLOR_INFO + "]" + Utils.DISPATCH_AS_OF_THE_MORNING + "[/color]\n\n"

	# ═══ SITUATION ═══
	bbcode += "[color=#" + Utils.COLOR_BERTHIER + "]SITUATION[/color]\n"
	var player_regions = int(situation.get("player_regions", 0))
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
	# DDB-R7 (Pre-Deploy S13b part 3): the law the chest could buy at a rich
	# peace — the same `law_sink` the terminal's dispatch reads.
	var law_sink := str(situation.get("law_sink", ""))
	# S14D-X3 (October 23, 2026): the line carries a DOOR to the eighth book.
	var sink_suffix := "" if law_sink == "" else "[color=#" + Utils.COLOR_INFO + "] — " + law_sink + " (the Laws tab: T, then 8) [/color]" + Utils.bb_button_chip("ledger:7", "Open the Laws", Utils.COLOR_COMMAND, "233043")
	# VP-1 (S14b part 3): once the laws are bought, the Act of the Empire the
	# chest could decree — its row is on the road page (`act_sink`).
	var act_sink := str(situation.get("act_sink", ""))
	if sink_suffix == "" and act_sink != "":
		sink_suffix = "[color=#" + Utils.COLOR_INFO + "] — " + act_sink + " (F1 → The Emperor's Designs)[/color]"
	bbcode += "[color=#" + Utils.COLOR_INFO + "]  France holds " + str(player_regions) + " regions. Treasury: " + _format_number(treasury) + "g [/color][color=#" + delta_color + "](" + delta_sign + _format_number(treasury_delta) + delta_suffix + ")[/color]" + sink_suffix + "\n"
	# Tier 1 (DYNAMISM_SPEC §2): the first morning names the campaign's
	# seed — the key rides the boot briefing only, so every later morning
	# renders exactly as before.
	var seed_line := str(situation.get("campaign_seed_line", ""))
	if seed_line != "":
		bbcode += "[color=#" + Utils.COLOR_INFO + "]  " + seed_line + "[/color]\n"
	# SR-5r RF-4b (REFORMS_SPEC §8a): the Staff's first refill, named, and
	# the forecast — the same source as the terminal's dispatch.
	var staff_arrived = situation.get("staff_arrived", null)
	if staff_arrived is String and staff_arrived != "":
		bbcode += "[color=#" + Utils.COLOR_SUCCESS + "]  THE STAFF: " + staff_arrived + " is established — one more order of the day, from today.[/color]\n"
	var law_forecast = situation.get("law_forecast", null)
	if law_forecast is Dictionary and not law_forecast.is_empty():
		bbcode += "[color=#" + Utils.COLOR_WARNING + "]  THE LAWS: " + str(law_forecast.get("line", "")) + "[/color]\n"
	# RE-2 (docs/RECURRING_EVENTS_SPEC.md §12 — the Watch): at most two "may"
	# lines a morning — the nearest-due affairs of state over the premise's
	# own measures. The key rides only when the recurring deck is armed, so an
	# unarmed board prints nothing here.
	var affairs_watch = situation.get("affairs_watch", null)
	if affairs_watch is Array:
		for watch_line in affairs_watch:
			bbcode += "[color=#" + Utils.COLOR_INFO + "]  IN THE OFFING: " + str(watch_line) + "[/color]\n"
	# RE-R (docs/RECURRING_EVENTS_SPEC.md §12c, P10): the answers' receipts
	# the morning after — plain, the same key the terminal's dispatch prints
	# (`situation.affair_receipt`, absent on every other morning).
	var affair_receipt = situation.get("affair_receipt", null)
	if affair_receipt is Array:
		for receipt_line in affair_receipt:
			bbcode += "[color=#" + Utils.COLOR_INFO + "]  " + str(receipt_line) + "[/color]\n"
	# RE-H (docs/RECURRING_EVENTS_SPEC.md §6.5, §22.2): a squadron's fate on
	# its morning — amber, the same key the terminal's dispatch prints
	# (`situation.affair_fate`, absent on every other morning).
	var affair_fate = situation.get("affair_fate", null)
	if affair_fate is Array:
		for fate_line in affair_fate:
			bbcode += "[color=#" + Utils.COLOR_WARNING + "]  THE SQUADRON: " + str(fate_line) + "[/color]\n"

	if bankrupt:
		bbcode += "[color=#" + Utils.COLOR_ERROR + "]  BANKRUPT — Treasury exhausted. Troops desert.[/color]\n"
	else:
		# WO-10 (WO slice 12): the estimate says how good it is.
		var strength_note = str(situation.get("enemy_strength_note", ""))
		var note_suffix = "" if strength_note == "" else " " + strength_note
		# LV-7 (row EP F1): the same sentence the terminal prints (Utils).
		var held_line = Utils.enemy_regions_sentence(situation)
		# IQ-2 (Sept 14, 2026): with no French corps under arms the ratio has
		# no denominator — it printed "Estimated enemy strength: 0% of French
		# forces" over an annihilated army. The backend says so instead.
		var no_field_army = situation.get("no_field_army", false)
		if typeof(no_field_army) == TYPE_BOOL and no_field_army:
			bbcode += "[color=#" + Utils.COLOR_INFO + "]  " + held_line + " [/color][color=#" + Utils.COLOR_ERROR + "]France has no army in the field.[/color]\n"
		else:
			bbcode += "[color=#" + Utils.COLOR_INFO + "]  " + held_line + " Estimated enemy strength: " + str(strength_pct) + "% of French forces" + note_suffix + ".[/color]\n"

	# Authority (V2b)
	var authority = int(situation.get("authority", 100))
	var authority_label = str(situation.get("authority_label", ""))
	var auth_color = Utils.COLOR_INFO
	if authority >= 80:
		auth_color = Utils.COLOR_SUCCESS
	elif authority < 50:
		auth_color = Utils.COLOR_ERROR
	bbcode += "[color=#" + Utils.COLOR_INFO + "]  Your authority: [/color][color=#" + auth_color + "]" + str(authority) + (" (" + authority_label + ")" if authority_label != "" else "") + "[/color]\n"

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
				"awaiting_decision":
					# FA-N28: a man whose question the player has not answered.
					icon = "?"
				"counter_punch":
					# AAR-25: a free strike, open this turn only.
					icon = "»"
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
				line += " Morale: " + str(m_morale) + "%"

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
	# S14C-X27: a lapsed petition's receipt prints once — under LAPSED ENVOYS.
	var turn_events = Utils.turn_events_beside_lapses(data)
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
			# IQ-7 review R8(b): a lapsed PETITION prints the priced line the
			# lapse hook kept (shown = applied), never "offer lapsed".
			var l_line = str(lapse.get("line", ""))
			if bool(lapse.get("is_petition", false)) and l_line != "":
				bbcode += "[color=#" + Utils.COLOR_BATTLE + "]  " + l_line + "[/color]\n"
				continue
			# S14C-X15: a carried sentence prints for any letter (the moment's, the call's).
			if l_line != "":
				bbcode += "[color=#" + Utils.COLOR_BATTLE + "]  " + l_line + "[/color]\n"
				continue
			if bool(lapse.get("is_moment", false)):
				bbcode += "[color=#" + Utils.COLOR_BATTLE + "]  A letter of the record was left unanswered.[/color]\n"
				continue
			# PC-F45 (S13e part 4): the letter's display name (R7), never the raw key.
			var l_ptype = str(lapse.get("proposal_type_display", str(lapse.get("proposal_type", "offer")).replace("_", " ").capitalize()))
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
		bbcode += "[color=#" + Utils.COLOR_INFO + "]  Talleyrand: " + Utils.plural(pending_envoy_count, "envoy") + (" awaits" if pending_envoy_count == 1 else " await") + " your reply this turn. Use [b]Open Envoys[/b] below before ending the turn.[/color]\n"
		for i in range(min(pending_envoys.size(), 3)):
			var envoy = pending_envoys[i]
			var envoy_nation = str(envoy.get("nation", "?"))
			# PC-F45: "Austria — Armistice Losing" read as France losing; the
			# backend's display name names the letter.
			var envoy_type = str(envoy.get("proposal_type_display", str(envoy.get("proposal_type", "proposal")).capitalize()))
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
					de_color = Utils.COLOR_INFO      # dim grey
			bbcode += "[color=#" + de_color + "]  " + de_text + "[/color]\n"
		bbcode += "\n"

	# ═══ DIPLOMATIC STATUS ═══
	# FA-N69 (slice 17): this re-read screen dropped two sections main.gd
	# prints from the SAME payload, both non-empty on turn 1 of every
	# campaign. Translated to bbcode (this file has no add_output).
	# FA-N64: the override payoff rides the same block.
	var talleyrand_report = data.get("talleyrand_report", [])
	var override_note = data.get("talleyrand_override_note", null)
	var has_override_note = override_note != null and str(override_note) != ""
	if (talleyrand_report is Array and talleyrand_report.size() > 0) or has_override_note:
		bbcode += "[color=#" + Utils.COLOR_BERTHIER + "]DIPLOMATIC STATUS[/color]\n"
		if talleyrand_report is Array:
			for tal_entry in talleyrand_report:
				var tal_msg = str(tal_entry.get("message", "")) if tal_entry is Dictionary else str(tal_entry)
				if tal_msg != "":
					bbcode += "[color=#" + Utils.COLOR_INFO + "]  " + tal_msg + "[/color]\n"
		if has_override_note:
			bbcode += "[color=#" + Utils.COLOR_OBSERVATION + "]  Talleyrand: " + str(override_note) + "[/color]\n"
		bbcode += "\n"

	# ═══ COALITION THREAT ═══
	var coalition_status = data.get("coalition_status", null)
	if coalition_status != null and coalition_status is Dictionary:
		var threat_level = int(coalition_status.get("threat_level", 0))
		var tier = str(coalition_status.get("tier", ""))
		if threat_level > 0:
			bbcode += "[color=#" + Utils.COLOR_BERTHIER + "]COALITION THREAT[/color]\n"
			# SF7-X48: the section's tier is the coalition's name (Brewing / Formed
			# are the dangerous ones); the band names stay for an old payload.
			var tier_color = Utils.COLOR_ERROR if tier in ["Brewing", "Formed", "CRITICAL", "HIGH"] else Utils.COLOR_BATTLE
			# S14G-M3 (Pre-Deploy S14h part 2, October 26, 2026): what moved the figure
			# since yesterday's dawn - the backend's own sentence ("up 8 since
			# yesterday (Won a battle +3, Won a decisive battle +5)"); absent
			# where yesterday's figure is unknown, and the line reads as before.
			var threat_delta_line = str(coalition_status.get("threat_delta_line", ""))
			var threat_tail = (" — " + threat_delta_line) if threat_delta_line != "" else ""
			bbcode += "[color=#" + tier_color + "]  Threat: " + str(threat_level) + "/100 [" + tier + "]" + threat_tail + "[/color]\n"
			var brewing = coalition_status.get("brewing", null)
			if brewing != null and brewing is Dictionary:
				var brew_turns = int(brewing.get("turns_remaining", 0))
				# SF-RR7: a brew the Congress holds waits on Paris — no countdown.
				var brew_paris = str(brewing.get("waits_on_paris", ""))
				if brew_paris != "":
					bbcode += "[color=#" + Utils.COLOR_BATTLE + "]  A coalition brews — " + brew_paris + ".[/color]\n"
				else:
					bbcode += "[color=#" + Utils.COLOR_ERROR + "]  Coalition forming in " + str(brew_turns) + " turns![/color]\n"
			var active_coal = coalition_status.get("active_coalition", null)
			if active_coal != null and active_coal is Dictionary:
				var coal_name = str(active_coal.get("name", "Coalition"))
				var coal_leader = str(active_coal.get("leader", "?"))
				bbcode += "[color=#" + Utils.COLOR_ERROR + "]  ACTIVE: " + coal_name + " — Leader: " + coal_leader + "[/color]\n"
				# EAD-8 (the economy gate): the members that have not struck
				# us, each with why — the backend's public-facts reading.
				var unmarched = active_coal.get("unmarched", [])
				if unmarched is Array and unmarched.size() > 0:
					bbcode += "[color=#" + Utils.COLOR_BATTLE + "]  Not every court of the league has struck us:[/color]\n"
					for urow in unmarched:
						if urow is Dictionary and str(urow.get("text", "")) != "":
							bbcode += "[color=#" + Utils.COLOR_INFO + "]    • " + str(urow.get("text", "")) + "[/color]\n"
			# SF-LB-3 (Score Finish Step 7b): the next league and the price
			# to keep each court out of it — the backend's own forecast.
			var league_line = str(coalition_status.get("league_line", ""))
			if league_line != "":
				bbcode += "[color=#" + Utils.COLOR_BATTLE + "]  " + league_line + "[/color]\n"
			var league_rows = coalition_status.get("league_rows", [])
			if league_rows is Array:
				for lrow in league_rows:
					if lrow is Dictionary and str(lrow.get("text", "")) != "":
						bbcode += "[color=#" + Utils.COLOR_INFO + "]    • " + str(lrow.get("text", "")) + "[/color]\n"
			bbcode += "\n"

	# ═══ WAR PURPOSE ═══
	# FA-N71 (slice 17): WPS-A's section, built on every dispatch, rendered
	# by nothing until now. Empty until a war has a stated purpose (FA-D4).
	var war_objectives = data.get("war_objectives", [])
	if war_objectives is Array and war_objectives.size() > 0:
		bbcode += "[color=#" + Utils.COLOR_BERTHIER + "]WAR PURPOSE[/color]\n"
		for wo in war_objectives:
			var wo_text = str(wo.get("text", "")) if wo is Dictionary else str(wo)
			if wo_text != "":
				bbcode += "[color=#" + Utils.COLOR_INFO + "]  " + wo_text + "[/color]\n"
		bbcode += "\n"

	# ═══ DEFEAT WARNING ═══
	var defeat_imminent_warning = data.get("defeat_imminent_warning", null)
	if defeat_imminent_warning != null and defeat_imminent_warning is Dictionary:
		var diw_msg = str(defeat_imminent_warning.get("message", ""))
		var diw_sev = str(defeat_imminent_warning.get("severity", "warning"))
		if diw_msg != "":
			var diw_color = Utils.COLOR_ERROR if diw_sev == "critical" else Utils.COLOR_BATTLE
			# IQ-2 (Sept 14, 2026): the sandbox arm of this warning may not
			# promise an ending (the 1805 campaign is open-ended), so it names
			# its own heading; the legacy arm sends none and keeps the literal.
			var diw_heading = defeat_imminent_warning.get("heading", "")
			if not (diw_heading is String) or diw_heading == "":
				diw_heading = "DEFEAT WARNING"
			bbcode += "[color=#" + Utils.COLOR_BERTHIER + "]" + diw_heading + "[/color]\n"
			bbcode += "[color=#" + diw_color + "]  " + diw_msg + "[/color]\n"
			# GE-2 (ENDGAME_PLAN §4): the clock LINE, one per held arm — the
			# backend's own `clock_line` (the terminal banner, the war room
			# and the Territories tab print the same words); a paused clock
			# names no date. Mirrored from main.gd's `_add_fall_clock_lines`
			# so the R screen and the banner cannot drift (the "one reader
			# fixed" landmine).
			# UXR3-F8: the banner's one road — the prose already states an
			# arm's clock, so it is never printed twice.
			for row in Utils.fall_clock_rows(defeat_imminent_warning):
				bbcode += "[color=#" + str(row[1]) + "]  " + str(row[0]) + "[/color]\n"
			bbcode += "\n"

	# ═══ THE CONGRESS OF PARIS (GE-3, ENDGAME_PLAN §4 — the clock line) ═══
	# Mirrored from main.gd's `_add_congress_clock_line` so the R screen and
	# the end-turn banner cannot drift: the backend's ONE line
	# (`congress.state_line`), its `severity` picking the tint.
	# UXR3-19 (Pre-Deploy S12 part 2): a SITTING Congress is the live
	# subject of the morning — it leads the dispatch, under its header; at
	# the gate it keeps its place here.
	var congress_block := _congress_block(data)
	var congress_sits := false
	var congress_clock = data.get("congress_clock", null)
	if congress_clock is Dictionary:
		congress_sits = str(congress_clock.get("phase", "")) == "sitting"
	if congress_sits and congress_at >= 0:
		bbcode = bbcode.substr(0, congress_at) + congress_block + bbcode.substr(congress_at)
	else:
		bbcode += congress_block
	# VP-1 (S14b part 2): the designs' clock — mirrored from main.gd's
	# `_add_designs_clock_line`.
	bbcode += _designs_block(data)

	# ═══ TODAY — the first morning's doors (LV-1, row EP F1) ═══
	# The turn-1 briefing's own section, mirrored from main.gd.
	var today = data.get("today", null)
	if today is Dictionary and not today.is_empty():
		bbcode += "[color=#" + Utils.COLOR_BERTHIER + "]TODAY[/color]\n"
		var today_orders = today.get("orders", [])
		if today_orders is Array and today_orders.size() > 0:
			# SF7-X47: the header is the backend's sentence (a choice, not a plan).
			var today_header = str(today.get("orders_header", "Orders the board will take at once:"))
			bbcode += "[color=#" + Utils.COLOR_INFO + "]  " + today_header + "[/color]\n"
			for order in today_orders:
				# UXR3-23 (S12): a chip that types the order (it never sends).
				bbcode += "    " + Utils.bb_button_chip("type:" + str(order), str(order),
						Utils.COLOR_COMMAND, "233043") + "\n"
			# S14E-24: an attack among them is taught with its free preview.
			var today_hint = str(today.get("orders_hint", ""))
			if today_hint != "":
				bbcode += "[color=#" + Utils.COLOR_INFO + "]  " + today_hint + "[/color]\n"
		var today_doors = str(today.get("doors", ""))
		if today_doors != "":
			bbcode += "[color=#" + Utils.COLOR_INFO + "]  " + today_doors + "[/color]\n"
		var today_cabinet = str(today.get("cabinet", ""))
		if today_cabinet != "":
			bbcode += "[color=#" + Utils.COLOR_INFO + "]  " + today_cabinet + "[/color]\n"
		# VP1-X15 (S14b part 2): the re-read prints the doctrine line the live
		# dispatch prints (main.gd's TODAY block) — it was dropped here.
		var today_doctrine = today.get("doctrine", "")
		if today_doctrine is String and today_doctrine != "":
			bbcode += "[color=#" + Utils.COLOR_INFO + "]  " + today_doctrine + "[/color]\n"
		# VP-1 (S14b part 2): the road page's door, as main.gd prints it.
		var today_designs = today.get("designs", "")
		if today_designs is String and today_designs != "":
			bbcode += "[color=#" + Utils.COLOR_GOLD + "]  " + today_designs + "[/color]\n"
		bbcode += "\n"

	# ═══ BERTHIER'S NOTE ═══
	bbcode += "[color=#" + Utils.COLOR_OBSERVATION + "]  Berthier: \"" + berthier_note + "\"[/color]\n"
	bbcode += "[color=#" + Utils.COLOR_BERTHIER + "]════════════════════════════════════[/color]\n"

	content_label.text = Utils.humanize_nation_keys_in_text(bbcode)

func _designs_block(data: Dictionary) -> String:
	"""THE EMPEROR'S DESIGNS (VP-1) — the designs' clock, mirrored from
	main.gd's `_add_designs_clock_line` (the same line, the same tint)."""
	var clock = data.get("designs_clock", null)
	if not (clock is Dictionary):
		return ""
	var line = clock.get("line", "")
	if not (line is String) or line == "":
		return ""
	var tint := Utils.COLOR_GOLD
	if str(clock.get("severity", "")) == "warning":
		tint = Utils.COLOR_BATTLE
	return ("[color=#" + Utils.COLOR_BERTHIER + "]THE EMPEROR'S DESIGNS[/color]\n"
		+ "[color=#" + tint + "]  " + line + "[/color]\n\n")


func _congress_block(data: Dictionary) -> String:
	"""THE CONGRESS OF PARIS (GE-3, ENDGAME_PLAN §4 — the clock line).
	Mirrored from main.gd's `_add_congress_clock_line` so the R screen and
	the end-turn banner cannot drift: the backend's ONE line
	(`congress.state_line`), its `severity` picking the tint."""
	var congress_clock = data.get("congress_clock", null)
	if not (congress_clock is Dictionary):
		return ""
	var cc_line = congress_clock.get("line", "")
	if not (cc_line is String) or cc_line == "":
		return ""
	var cc_sev = congress_clock.get("severity", "gate")
	var cc_tint := Utils.COLOR_GOLD
	if cc_sev is String:
		if cc_sev == "critical":
			cc_tint = Utils.COLOR_ERROR
		elif cc_sev == "warning":
			cc_tint = Utils.COLOR_BATTLE
		elif cc_sev == "paused":
			cc_tint = Utils.COLOR_INFO
	return "[color=#" + Utils.COLOR_BERTHIER + "]THE CONGRESS OF PARIS[/color]\n" \
		+ "[color=#" + cc_tint + "]  " + cc_line + "[/color]\n\n"


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


# ═══════════════════════════════════════════════════════════════════════════
# RE-C — the Correspondence page
# ═══════════════════════════════════════════════════════════════════════════

func has_correspondence() -> bool:
	"""main's pointer lines: the client has seen the page's dict (an armed world)."""
	return not _corr.is_empty()


func open_correspondence() -> void:
	"""Turn the page — now when the dict is in hand, else as soon as the GET
	lands (the letter-book's footer opens the screen and asks in one breath)."""
	if _corr.is_empty():
		_corr_pending_open = true
		return
	_show_correspondence_page()


func refit() -> void:
	"""The live-refit road's hook (`Utils.refit_surface`): the page's raised
	ceiling follows the window as the letter's does; the dispatch page keeps
	the plain clamp. A docked panel (the Side Desk) keeps its dock."""
	if _corr_open:
		_raise_page_ceiling()
	if not $PanelContainer.has_meta("side_desk_docked"):
		Utils.clamp_centered_panel($PanelContainer)


func _take_correspondence(response) -> void:
	var corr = response.get("correspondence", {}) if response is Dictionary else {}
	_corr = corr if corr is Dictionary else {}
	_refresh_correspondence_button()
	if _corr_open or _corr_pending_open:
		if _corr.is_empty():
			_show_dispatch_page()
		else:
			_show_correspondence_page()


func _refresh_correspondence_button() -> void:
	"""The button's text is the backend's ("The Correspondence (1 standing)" /
	"(a squadron at sea)" / plain), amber when it has news — the Envoys
	badge's idiom; hidden on an unarmed world and while the page is open."""
	correspondence_button.visible = not _corr.is_empty() and not _corr_open
	if _corr.is_empty():
		return
	correspondence_button.text = str(_corr.get("button", "The Correspondence"))
	var counts = _corr.get("counts", {})
	var standing := int(counts.get("standing", 0)) if counts is Dictionary else 0
	if standing > 0 or bool(_corr.get("at_sea", false)):
		correspondence_button.add_theme_color_override("font_color", Utils.UI_WARNING)
	else:
		correspondence_button.remove_theme_color_override("font_color")


func _show_correspondence_page() -> void:
	_corr_pending_open = false
	_corr_open = true
	scroll_container.visible = false
	corr_scroll.visible = true
	back_to_dispatch_button.visible = true
	correspondence_button.visible = false
	title_label.text = CORR_TITLE
	_render_correspondence(_corr)
	_raise_page_ceiling()
	if not $PanelContainer.has_meta("side_desk_docked"):
		Utils.clamp_centered_panel($PanelContainer)


func _show_dispatch_page() -> void:
	_reset_correspondence_page()
	_refresh_correspondence_button()
	if visible and not $PanelContainer.has_meta("side_desk_docked"):
		Utils.clamp_centered_panel($PanelContainer)


func _reset_correspondence_page() -> void:
	"""The page state and its ceiling, cleared on back and on close."""
	_corr_open = false
	_corr_pending_open = false
	if $PanelContainer.has_meta("clamp_ceiling_override"):
		$PanelContainer.remove_meta("clamp_ceiling_override")
	if corr_scroll != null:
		corr_scroll.visible = false
	if scroll_container != null:
		scroll_container.visible = true
	if back_to_dispatch_button != null:
		back_to_dispatch_button.visible = false
	if title_label != null:
		title_label.text = DISPATCH_TITLE


func _raise_page_ceiling() -> void:
	"""The page's ceiling grows with the window as the letter's does (the
	same fractions; the authored 700 × 500 stays the floor); removed when
	the page turns back."""
	var view := get_viewport().get_visible_rect().size
	$PanelContainer.set_meta("clamp_ceiling_override", Vector2(
			clampf(view.x * CORR_WIDTH_FRACTION, CORR_MIN_WIDTH, CORR_MAX_WIDTH),
			maxf(view.y * CORR_HEIGHT_FRACTION, CORR_MIN_HEIGHT)))


func _render_correspondence(data: Dictionary) -> void:
	"""The one column: the first-open line (once), ON THE DESK, IN THE
	OFFING, ANSWERED newest first, LEFT UNANSWERED / SET ASIDE, the closing
	record of a closed file. Every row is the backend's; nothing is derived here."""
	for child in corr_box.get_children():
		corr_box.remove_child(child)
		child.queue_free()
	var empty = data.get("empty", {})
	if not (empty is Dictionary):
		empty = {}
	var fo = data.get("first_open")
	if fo is Dictionary and str(fo.get("screen", "")) == CORR_SCREEN and str(fo.get("line", "")) != "":
		_add_corr_note(str(fo.get("line", "")), Utils.COLOR_INFO)
		if _api_client_ref != null and _api_client_ref.has_method("note_first_open"):
			_api_client_ref.note_first_open(CORR_SCREEN)
	var standing = data.get("standing", [])
	if not (standing is Array):
		standing = []
	_add_corr_head("ON THE DESK (%d)" % standing.size(), "letters that wait for the Emperor")
	if standing.is_empty():
		_add_corr_note(str(empty.get("desk", "")), Utils.COLOR_INFO)
	for row in standing:
		if row is Dictionary:
			_add_slip(row, "standing")
	var offing = data.get("offing", [])
	if not (offing is Array):
		offing = []
	_add_corr_head("IN THE OFFING", "matters that may yet write; none is promised")
	if offing.is_empty():
		_add_corr_note(str(empty.get("offing", "")), Utils.COLOR_INFO)
	for line in offing:
		_add_corr_note(str(line), Utils.COLOR_INFO)
	var answered = data.get("answered", [])
	if not (answered is Array):
		answered = []
	_add_corr_head("ANSWERED (%d)" % answered.size(), "newest first")
	if answered.is_empty():
		_add_corr_note(str(empty.get("answered", "")), Utils.COLOR_INFO)
	for row in answered:
		if row is Dictionary:
			_add_slip(row, "answered")
	var aside = data.get("set_aside", [])
	if aside is Array and not aside.is_empty():
		_add_corr_head("LEFT UNANSWERED / SET ASIDE", "")
		for row in aside:
			if row is Dictionary:
				_add_corr_note(str(row.get("label", "")).to_upper() + " · " + str(row.get("title", "")).to_upper()
						+ " — " + str(row.get("line", "")), Utils.COLOR_INFO)
	var closing = data.get("closing", [])
	if closing is Array:
		for rec in closing:
			if rec is Dictionary:
				_add_slip(rec, "closing")


func _add_corr_head(text: String, sub: String) -> void:
	var head := RichTextLabel.new()
	head.bbcode_enabled = true
	head.fit_content = true
	head.scroll_active = false
	head.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	head.mouse_filter = Control.MOUSE_FILTER_PASS
	var bb := "[color=#" + Utils.COLOR_BERTHIER + "]" + text + "[/color]"
	if sub != "":
		bb += "  [color=#" + Utils.COLOR_INFO + "]— " + sub + "[/color]"
	head.text = bb
	corr_box.add_child(head)


func _add_corr_note(text: String, hex: String) -> void:
	if text == "":
		return
	var note := RichTextLabel.new()
	note.bbcode_enabled = true
	note.fit_content = true
	note.scroll_active = false
	note.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	note.mouse_filter = Control.MOUSE_FILTER_PASS
	note.text = "[color=#" + hex + "]" + _corr_esc(text) + "[/color]"
	corr_box.add_child(note)


func _add_slip(row: Dictionary, kind: String) -> void:
	"""One parchment slip (§12b.1): the rubric row — the dateline · the
	title in rubric with the device at the right — the apostille on an
	answered letter (the seal and the Emperor's word in IM Fell italic), the
	body in ink with its chips as `[url]` metas."""
	_ensure_corr_dress()
	var panel := PanelContainer.new()
	panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	panel.add_theme_stylebox_override("panel", _corr_sheet_hc if UiSettings.get_high_contrast() else _corr_sheet)
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 2)
	var head := HBoxContainer.new()
	var rubric := Label.new()
	rubric.theme_type_variation = &"Caption"
	rubric.add_theme_font_override("font", _corr_cinzel)
	rubric.add_theme_color_override("font_color", Color.html(Utils.INK_RUBRIC))
	rubric.text = _corr_rubric(row, kind)
	rubric.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	rubric.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	head.add_child(rubric)
	var dev = row.get("device", {})
	var device := _corr_device(dev if dev is Dictionary else {})
	if device != null:
		head.add_child(device)
	box.add_child(head)
	if kind == "answered":
		box.add_child(_corr_apostille(str(row.get("caption", ""))))
	var body := RichTextLabel.new()
	body.bbcode_enabled = true
	body.fit_content = true
	body.scroll_active = false
	body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	body.mouse_filter = Control.MOUSE_FILTER_PASS
	body.text = _corr_body_bbcode(row, kind)
	body.meta_clicked.connect(_on_corr_meta)
	box.add_child(body)
	panel.add_child(box)
	corr_box.add_child(panel)


func _corr_rubric(row: Dictionary, kind: String) -> String:
	var title := str(row.get("title", "")).to_upper()
	if kind == "standing":
		return "SEALED · ANSWER BY " + str(row.get("answer_by_label", "")).to_upper()
	if kind == "closing":
		return str(row.get("label", "")).to_upper() + " · " + title + " — THE FILE CLOSED"
	return str(row.get("dateline", "")).to_upper() + " · " + title


func _corr_body_bbcode(row: Dictionary, kind: String) -> String:
	"""The slip's body: every inline colour an `INK_*` (the ink census); the
	chips are the theme's gold-on-navy plaques, `[url]` metas the DD-B
	instrument presses (`click Read the letter`, `click#2 Read the letter`)."""
	var lines: Array[String] = []
	if kind == "closing":
		var rec_lines = row.get("lines", [])
		if rec_lines is Array:
			for i in range(rec_lines.size()):
				var rec_text := _corr_esc(str(rec_lines[i]))
				if i == 0:
					lines.append("[color=#" + Utils.INK_BODY + "]" + rec_text + "[/color]")
				else:
					lines.append("[color=#" + Utils.INK_SEPIA + "][font=" + CORR_FELL_ITALIC + "]" + rec_text + "[/font][/color]")
		return "\n".join(lines)
	if kind == "standing":
		var who := _corr_esc(str(row.get("writer", "")))
		var office := _corr_esc(str(row.get("office", "")))
		var line1 := "[color=#" + Utils.INK_BODY + "][b]" + _corr_esc(str(row.get("title", ""))) + "[/b]"
		if who != "":
			line1 += " — " + who + ((", " + office) if office != "" else "")
		lines.append(line1 + "[/color]")
		var parts: Array[String] = []
		var answers = row.get("answers", [])
		if answers is Array:
			for a in answers:
				if a is Dictionary:
					var cap := _corr_esc(str(a.get("caption", "")))
					var rec := _corr_esc(str(a.get("receipt", "")))
					parts.append(cap + ((": " + rec) if rec != "" else ""))
		if not parts.is_empty():
			lines.append("[color=#" + Utils.INK_BODY + "]" + "  ·  ".join(parts) + "[/color]")
		var mailbox_id := int(row.get("mailbox_id", 0))
		if mailbox_id > 0:
			lines.append(Utils.bb_button_chip("corr:read:" + str(mailbox_id), "Read the letter ▸", Utils.COLOR_GOLD, CORR_CHIP_BG))
		return "\n".join(lines)
	# answered: what it did, what came of it (at sea, or the echo), the fate, the chips
	var receipt := _corr_esc(str(row.get("receipt", "")))
	if receipt != "":
		lines.append("[color=#" + Utils.INK_BODY + "]" + receipt + "[/color]")
	var echo := _corr_esc(str(row.get("echo", "")))
	var at_sea = row.get("at_sea", {})
	var fate = row.get("fate", {})
	if at_sea is Dictionary and not at_sea.is_empty():
		lines.append("[color=#" + Utils.INK_SEPIA + "]" + _corr_esc(str(at_sea.get("line", ""))) + "[/color]")
	elif echo != "":
		var when := _corr_esc(str(row.get("echo_label", "")))
		lines.append("[color=#" + Utils.INK_SEPIA + "]" + ((when + " — ") if when != "" else "") + echo + "[/color]")
	# RE-6: a decree's term — "In force until …" while it stands, "Expired …" after
	var until_label := _corr_esc(str(row.get("until_label", "")))
	if until_label != "":
		var term_line := ("In force until " if bool(row.get("in_force", false)) else "Expired ") + until_label + "."
		lines.append("[color=#" + Utils.INK_SEPIA + "]" + term_line + "[/color]")
	if fate is Dictionary and not fate.is_empty():
		var fate_when := _corr_esc(str(fate.get("label", "")))
		lines.append("[color=#" + Utils.INK_RUBRIC + "]" + ((fate_when + " — ") if fate_when != "" else "")
				+ _corr_esc(str(fate.get("line", ""))) + "[/color]")
	var chips: Array[String] = []
	var chip_rows = row.get("chips", [])
	if chip_rows is Array:
		for chip in chip_rows:
			if not (chip is Dictionary):
				continue
			var ck := str(chip.get("kind", ""))
			var nation := str(chip.get("nation", ""))
			if ck == "court" and nation != "":
				chips.append(Utils.bb_button_chip("corr:court:" + nation, Utils.display_nation_name(nation) + " ▸", Utils.COLOR_GOLD, CORR_CHIP_BG))
			elif ck == "admiralty":
				chips.append(Utils.bb_button_chip("ledger:6", "Admiralty ▸", Utils.COLOR_GOLD, CORR_CHIP_BG))
			elif ck == "laws":
				chips.append(Utils.bb_button_chip("ledger:7", "Laws ▸", Utils.COLOR_GOLD, CORR_CHIP_BG))
	if not chips.is_empty():
		lines.append(" ".join(chips))
	return "\n".join(lines)


func _corr_apostille(caption: String) -> Control:
	"""The Emperor's word on an answered slip: an 18-px wax seal and
	"{caption}. — N." in IM Fell italic at Lead."""
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 6)
	var seal := TextureRect.new()
	seal.texture = load(CORR_SEAL)
	seal.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	seal.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	seal.custom_minimum_size = Vector2(CORR_SEAL_PX, CORR_SEAL_PX)
	seal.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_child(seal)
	var word := Label.new()
	word.theme_type_variation = &"Lead"
	word.add_theme_font_override("font", _corr_fell_italic)
	word.add_theme_color_override("font_color", Color.html(Utils.INK_BODY))
	word.text = (caption if caption != "" else "Answered") + ". — N."
	word.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	word.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(word)
	return row


func _corr_device(device: Dictionary) -> Control:
	"""The slip's device, the letter's rule in small: the court's arms (or the
	owner's sheet) as a 24-px flag, an office's gold monogram on leather; null
	when the letter carries none."""
	var kind := str(device.get("kind", ""))
	var nation := str(device.get("nation", ""))
	var flag := Utils.nation_flag_path(nation) if nation != "" else ""
	if kind in ["arms", "sheet"] and flag != "":
		var arms := TextureRect.new()
		arms.texture = load(flag)
		arms.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		arms.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		arms.custom_minimum_size = Vector2(CORR_DEVICE_PX * 1.5, CORR_DEVICE_PX)
		arms.mouse_filter = Control.MOUSE_FILTER_IGNORE
		return arms
	var letter := str(device.get("letter", ""))
	if letter == "":
		return null
	var locket := PortraitLocket.new()
	locket.setup(letter, CORR_DEVICE_PX, false)
	return locket


func _ensure_corr_dress() -> void:
	"""The slips' sheet and fonts, built once: the parchment's un-torn inner
	field as the box (no torn edge inside the page); a flat cream under High
	contrast; IM Fell italic for the apostille, Cinzel for the rubric."""
	if _corr_sheet != null:
		return
	_corr_sheet = StyleBoxTexture.new()
	_corr_sheet.texture = load(CORR_SHEET)
	_corr_sheet.region_rect = CORR_SHEET_FIELD
	for side in ["left", "right"]:
		_corr_sheet.set("texture_margin_" + side, 16.0)
		_corr_sheet.set("content_margin_" + side, 14.0)
	for side in ["top", "bottom"]:
		_corr_sheet.set("texture_margin_" + side, 12.0)
		_corr_sheet.set("content_margin_" + side, 10.0)
	_corr_sheet_hc = StyleBoxFlat.new()
	_corr_sheet_hc.bg_color = Color.html(Utils.INK_SHEET_HC)
	_corr_sheet_hc.border_color = Color.html(Utils.INK_RULE)
	_corr_sheet_hc.set_border_width_all(2)
	_corr_sheet_hc.set_corner_radius_all(4)
	_corr_sheet_hc.set_content_margin_all(12.0)
	_corr_fell_italic = load(CORR_FELL_ITALIC)
	_corr_cinzel = load(CORR_CINZEL)


func _corr_esc(text: String) -> String:
	return text.replace("[", "[lb]")


func _on_corr_meta(meta) -> void:
	"""The chips: "Read the letter ▸" closes the page and takes the rail
	card's road; a court chip closes it and asks main for that court's Cabinet
	page; the Admiralty and the Laws take the dispatch's own ledger doors."""
	var m := str(meta)
	if m.begins_with("corr:read:"):
		var mailbox_id := int(m.substr("corr:read:".length()))
		close_view()
		if mailbox_id > 0:
			read_letter_requested.emit(mailbox_id)
		return
	if m.begins_with("corr:court:"):
		var nation := m.substr("corr:court:".length())
		close_view()
		if nation != "":
			open_diplomacy_for.emit(nation)
		return
	_on_meta_clicked(meta)
