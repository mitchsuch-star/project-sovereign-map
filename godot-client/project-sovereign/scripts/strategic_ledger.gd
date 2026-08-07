extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Strategic Ledger Screen (Session B)
# =============================================================================
# 6-section sub-tabbed screen. CanvasLayer 50.
# Tabs: FORCES, TERRITORIES, ECONOMY, INTELLIGENCE, MANPOWER, ORDERS
# Number keys 1-6 switch sub-tabs (guarded by visible check).
# =============================================================================

signal closed
# NV-6: an Admiralty chip — the same typed-command pipeline every other
# chip surface uses (main.gd owns the send + the in-place refresh).
signal naval_command(command: String)

# NV-6: the Admiralty chip pill, matching the region panel's `_CHIP_BG`.
const _NAVAL_CHIP_BG = "233043"

# UI References — paths match scene tree
@onready var background_overlay = $BackgroundOverlay
@onready var close_button = $PanelContainer/VBoxContainer/HeaderRow/CloseButton
@onready var scroll_container = $PanelContainer/VBoxContainer/ScrollContainer
@onready var content_area = $PanelContainer/VBoxContainer/ScrollContainer/ContentArea
@onready var forces_tab = $PanelContainer/VBoxContainer/SubTabRow/ForcesTab
@onready var territories_tab = $PanelContainer/VBoxContainer/SubTabRow/TerritoriesTab
@onready var economy_tab = $PanelContainer/VBoxContainer/SubTabRow/EconomyTab
@onready var intel_tab = $PanelContainer/VBoxContainer/SubTabRow/IntelTab
@onready var manpower_tab = $PanelContainer/VBoxContainer/SubTabRow/ManpowerTab
@onready var orders_tab = $PanelContainer/VBoxContainer/SubTabRow/OrdersTab

# State
var current_tab: int = 0  # 0=forces, 1=territories, 2=economy, 3=intel, 4=manpower, 5=orders
var cached_data: Dictionary = {}
var tab_buttons: Array = []

# Active tab style
var _active_tab_style: StyleBoxFlat = null
var _normal_tab_style: StyleBoxFlat = null

func _ready():
	close_button.pressed.connect(close_view)
	Utils.apply_icon_only_button(close_button, Utils.ICON_PHOSPHOR + "x.svg")
	background_overlay.gui_input.connect(_on_overlay_input)

	tab_buttons = [forces_tab, territories_tab, economy_tab, intel_tab, manpower_tab, orders_tab]
	for i in range(tab_buttons.size()):
		tab_buttons[i].pressed.connect(_on_tab_pressed.bind(i))

	# Wire meta_clicked for cancel buttons in Orders tab
	content_area.meta_clicked.connect(_on_meta_clicked)

	# NV-P1 (routed at the NV-V visual pass, pre-existing): the ledger
	# ignored the mouse wheel. The RichTextLabel defaults to
	# MOUSE_FILTER_STOP, so it consumed the wheel event before its own
	# ScrollContainer parent ever saw it — and THE ADMIRALTY block sits at
	# the bottom of a long ECONOMY list, which is where it started to bite.
	# PASS still delivers _gui_input (so meta_clicked and every chip on
	# this screen keep working) and then lets the parent scroll.
	content_area.mouse_filter = Control.MOUSE_FILTER_PASS

	# Build tab styles
	_active_tab_style = StyleBoxFlat.new()
	_active_tab_style.bg_color = Utils.UI_ACTIVE_TAB_BG
	_active_tab_style.border_width_bottom = 2
	_active_tab_style.border_color = Utils.UI_GOLD
	_active_tab_style.content_margin_left = 6.0
	_active_tab_style.content_margin_right = 6.0
	_active_tab_style.content_margin_top = 3.0
	_active_tab_style.content_margin_bottom = 3.0

	_normal_tab_style = StyleBoxFlat.new()
	_normal_tab_style.bg_color = Utils.UI_PANEL_BG
	_normal_tab_style.content_margin_left = 6.0
	_normal_tab_style.content_margin_right = 6.0
	_normal_tab_style.content_margin_top = 3.0
	_normal_tab_style.content_margin_bottom = 3.0

	hide()


func _input(event):
	"""Handle number keys 1-5 for sub-tab switching. Only when visible."""
	if not visible:
		return
	if event is InputEventKey and event.pressed and not event.echo:
		var switched = true
		match event.keycode:
			KEY_1:
				_switch_tab(0)
			KEY_2:
				_switch_tab(1)
			KEY_3:
				_switch_tab(2)
			KEY_4:
				_switch_tab(3)
			KEY_5:
				_switch_tab(4)
			KEY_6:
				_switch_tab(5)
			_:
				switched = false
		if switched:
			get_viewport().set_input_as_handled()


var _api_client_ref = null

func open(api_client):
	"""Fetch ledger from backend and display it."""
	_api_client_ref = api_client
	content_area.text = "[color=#" + Utils.COLOR_INFO + "]Loading ledger...[/color]"
	current_tab = 0
	AudioManager.play("panel_open")
	show()
	Utils.clamp_centered_panel($PanelContainer)
	_update_tab_highlights()
	api_client.get_ledger(_on_ledger_received)


func close_view():
	"""Hide the overlay and emit closed signal."""
	if visible:
		AudioManager.play("panel_close")
	hide()
	cached_data = {}
	closed.emit()


func _on_ledger_received(response):
	"""Cache data and render current tab."""
	if not visible:
		return

	if not response.get("success", false):
		content_area.text = "[color=#" + Utils.COLOR_ERROR + "]Failed to load ledger.[/color]"
		return

	cached_data = response.get("ledger", {})
	if cached_data.is_empty():
		content_area.text = "[color=#" + Utils.COLOR_INFO + "]No ledger data available.[/color]"
		return

	_render_current_tab()


func _on_tab_pressed(tab_index: int):
	_switch_tab(tab_index)


func _switch_tab(tab_index: int):
	if tab_index == current_tab:
		return
	AudioManager.play("page_turn")
	current_tab = tab_index
	scroll_container.scroll_vertical = 0
	_update_tab_highlights()
	_render_current_tab()


func _update_tab_highlights():
	for i in range(tab_buttons.size()):
		if i == current_tab:
			tab_buttons[i].add_theme_stylebox_override("normal", _active_tab_style)
		else:
			tab_buttons[i].add_theme_stylebox_override("normal", _normal_tab_style)


func _render_current_tab():
	if cached_data.is_empty():
		return
	match current_tab:
		0:
			_render_forces()
		1:
			_render_territories()
		2:
			_render_economy()
		3:
			_render_intel()
		4:
			_render_manpower()
		5:
			_render_orders()


# =============================================================================
# TAB RENDERERS
# =============================================================================

func _render_forces():
	var forces = cached_data.get("forces", [])
	var bbcode = ""
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]═══ FORCES ═══[/color]\n\n"

	# Authority — global player stat (V2b)
	var authority = int(cached_data.get("authority", 100))
	var authority_label = str(cached_data.get("authority_label", "Normal"))
	var auth_color = Utils.COLOR_INFO
	if authority >= 80:
		auth_color = Utils.COLOR_SUCCESS
	elif authority < 50:
		auth_color = Utils.COLOR_ERROR
	bbcode += "Authority: [color=#" + auth_color + "]" + str(authority) + " (" + authority_label + ")[/color]\n\n"

	if forces.size() == 0:
		bbcode += "[color=#" + Utils.COLOR_INFO + "]No marshals available.[/color]\n"
		content_area.text = bbcode
		return

	for f in forces:
		var name = str(f.get("name", "?"))
		var unit_type = str(f.get("type", "infantry"))
		var loc = str(f.get("location", "?"))
		var strength = int(f.get("strength", 0))
		var morale = int(f.get("morale", 100))
		var trust = int(f.get("trust", 70))
		var stance = str(f.get("stance", "neutral"))
		var status = str(f.get("status", "idle"))
		var strat = str(f.get("strategic_order", "None"))
		var won = int(f.get("battles_won", 0))
		var lost = int(f.get("battles_lost", 0))
		var flags = f.get("special_flags", {})

		# Name + type tag
		var type_tag = "[" + unit_type.substr(0, 3).to_upper() + "]"
		bbcode += "[color=#" + Utils.COLOR_GOLD + "]" + name + " " + type_tag + "[/color]\n"

		# Status with color coding
		var status_color = Utils.COLOR_INFO
		match status:
			"broken", "retreating":
				status_color = Utils.COLOR_ERROR
			"drilling":
				status_color = Utils.COLOR_BLUE
			"idle":
				status_color = Utils.COLOR_GREY

		bbcode += "  Status: [color=#" + status_color + "]" + status.replace("_", " ").capitalize() + "[/color]"
		bbcode += "  Location: " + loc + "\n"
		bbcode += "  Strength: " + _format_number(strength)
		bbcode += "  Stance: " + stance + "\n"

		# Trust + morale with color thresholds
		var trust_color = Utils.COLOR_INFO
		if trust < 30:
			trust_color = Utils.COLOR_ERROR
		elif trust < 55:
			trust_color = Utils.COLOR_ORANGE

		var morale_color = Utils.COLOR_INFO
		if morale < 40:
			morale_color = Utils.COLOR_ERROR
		elif morale < 60:
			morale_color = Utils.COLOR_ORANGE

		bbcode += "  Trust: [color=#" + trust_color + "]" + str(trust) + "[/color]"
		bbcode += "  Morale: [color=#" + morale_color + "]" + str(morale) + "%[/color]"
		bbcode += "  W/L: " + str(won) + "/" + str(lost) + "\n"

		# Strategic order
		if strat != "None":
			bbcode += "  Order: " + strat + "\n"

		# Special flags
		var flag_parts = []
		if flags.get("shock_ready", false):
			flag_parts.append("SHOCK READY")
		if flags.get("counter_punch", false):
			flag_parts.append("COUNTER-PUNCH")
		if int(flags.get("reckless", 0)) > 0:
			flag_parts.append("RECKLESS:" + str(int(flags.get("reckless", 0))))
		if flags.get("exhausted", false):
			flag_parts.append("EXHAUSTED")
		if flag_parts.size() > 0:
			bbcode += "  [color=#" + Utils.COLOR_ORANGE + "]" + " | ".join(flag_parts) + "[/color]\n"

		bbcode += "\n"

	content_area.text = bbcode


func _render_territories():
	var territories = cached_data.get("territories", [])
	var bbcode = ""
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]═══ TERRITORIES ═══[/color]\n\n"

	if territories.size() == 0:
		bbcode += "[color=#" + Utils.COLOR_INFO + "]No territories controlled.[/color]\n"
		content_area.text = bbcode
		return

	for t in territories:
		var name = str(t.get("name", "?"))
		var terrain = str(t.get("terrain", "plains"))
		var rtype = str(t.get("region_type", "town"))
		var garrison = int(t.get("garrison", 0))
		var supply_cap = int(t.get("supply_capacity", 0))
		var occupants = int(t.get("occupant_count", 0))
		var supply_status = str(t.get("supply_status", "OK"))
		var stability = int(t.get("stability", 100))
		var war_dmg = int(t.get("war_damage", 0))
		var income = int(t.get("income", 0))
		var buildings = t.get("buildings", [])

		bbcode += "[color=#" + Utils.COLOR_GOLD + "]" + name + "[/color]"
		bbcode += " [" + rtype.replace("_", " ") + ", " + terrain.replace("_", " ") + "]\n"

		bbcode += "  Income: " + str(income) + "g"
		bbcode += "  Stability: " + str(stability) + "%"
		if war_dmg > 0:
			bbcode += "  Damage: " + str(war_dmg) + "%"
		bbcode += "\n"

		# Supply status
		var supply_color = Utils.COLOR_INFO
		if supply_status == "Over capacity":
			supply_color = Utils.COLOR_ERROR
		bbcode += "  Supply: [color=#" + supply_color + "]" + supply_status + "[/color]"
		bbcode += " (" + str(occupants) + " marshals, cap " + _format_number(supply_cap) + ")"
		if garrison > 0:
			bbcode += "  Garrison: " + _format_number(garrison)
		bbcode += "\n"

		# Buildings
		if buildings.size() > 0:
			var bld_parts = []
			for b in buildings:
				var bname = str(b.get("name", "?"))
				var bstatus = str(b.get("status", "built"))
				if bstatus == "built":
					bld_parts.append(bname)
				elif bstatus == "damaged":
					bld_parts.append("[color=#" + Utils.COLOR_ERROR + "]" + bname + " (damaged)[/color]")
				else:
					bld_parts.append("[color=#" + Utils.COLOR_BLUE + "]" + bname + " (" + bstatus + ")[/color]")
			bbcode += "  Buildings: " + ", ".join(bld_parts) + "\n"

		bbcode += "\n"

	content_area.text = bbcode


func _render_economy():
	var econ = cached_data.get("economy", {})
	var bbcode = ""
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]═══ ECONOMY ═══[/color]\n\n"

	var treasury = int(econ.get("treasury", 0))
	var income = int(econ.get("income", 0))
	var upkeep = int(econ.get("upkeep", 0))
	var net = int(econ.get("net", 0))
	var bankruptcy = int(econ.get("bankruptcy_turns", 0))

	var trade = int(econ.get("trade_income", 0))

	bbcode += "  Treasury: " + _format_number(treasury) + "g\n"
	bbcode += "  Income:   +" + str(income) + "g\n"
	if trade > 0:
		bbcode += "  Trade:    +" + str(trade) + "g\n"
	# PRE-EC ledger floor (ECONOMY_REVISIT_SPEC.md §0): admin_bonus, treaty_gold
	# and vassal_tribute are folded into `net` by ledger.py _build_economy but
	# were never rendered here, so the visible lines did not sum to Net whenever
	# France held a vassal (tribute) or a gold-per-turn treaty clause (the SC-33
	# "invisible tribute" bug class). Render every component that feeds Net.
	var admin_bonus = int(econ.get("admin_bonus", 0))
	if admin_bonus != 0:
		var ab_sign = "+" if admin_bonus > 0 else ""
		bbcode += "  Admin:    " + ab_sign + str(admin_bonus) + "g\n"
	var treaty_gold = int(econ.get("treaty_gold", 0))
	if treaty_gold != 0:
		var tg_sign = "+" if treaty_gold > 0 else ""
		bbcode += "  Treaty:   " + tg_sign + str(treaty_gold) + "g\n"
	var vassal_tribute = int(econ.get("vassal_tribute", 0))
	if vassal_tribute != 0:
		var vt_sign = "+" if vassal_tribute > 0 else ""
		bbcode += "  Tribute:  " + vt_sign + str(vassal_tribute) + "g\n"
	# SC-33 recurring settlement streams (G4F smoke follow-up): the ratified
	# gold-per-turn tribute is real per-turn cash — show its net line and the
	# per-stream detail instead of leaving it dispatch-only.
	var settlement_gold = int(econ.get("settlement_gold", 0))
	if settlement_gold != 0:
		var sg_sign = "+" if settlement_gold > 0 else ""
		bbcode += "  Settlements: " + sg_sign + str(settlement_gold) + "g\n"
	# ES-2 (Economy Revisit S6): recurring cost of holding non-homeland
	# soil — a signed Net component of its own (Income stays gross), so it
	# must render for the visible lines to sum to Net (SC-33 invariant).
	var occupation = int(econ.get("occupation", 0))
	if occupation > 0:
		bbcode += "  [color=#" + Utils.COLOR_WARNING + "]Occupation: -" + str(occupation) + "g[/color]\n"
	# EC-W1 (Econ War-Coupling): income suspended by hostile armies standing
	# on our provinces — its own signed Net component (SC-33 contract).
	var contributions = int(econ.get("contributions", 0))
	if contributions > 0:
		bbcode += "  [color=#" + Utils.COLOR_WARNING + "]Contributions: -" + str(contributions) + "g[/color]\n"
	# EC-W2 (Econ War-Coupling): war-effort spending drawn from the war
	# chest, scaled by war exhaustion — its own signed Net component.
	var war_effort = int(econ.get("war_effort", 0))
	if war_effort > 0:
		bbcode += "  [color=#" + Utils.COLOR_WARNING + "]War Effort: -" + str(war_effort) + "g[/color]\n"
	# ES-7 (Economy Revisit S7): income of provinces endowed to marshals'
	# estates — a signed Net component of its own (Income stays gross), so
	# it must render for the visible lines to sum to Net (SC-33 invariant).
	var dotation_skim = int(econ.get("dotation_skim", 0))
	if dotation_skim > 0:
		bbcode += "  [color=#" + Utils.COLOR_WARNING + "]Dotations: -" + str(dotation_skim) + "g[/color]\n"
	# ES-7 second pass (§0.6.8): the rente bill — treasury pensions at
	# premium; its own signed Net component (same SC-33 contract).
	var rente_cost = int(econ.get("rente_cost", 0))
	if rente_cost > 0:
		bbcode += "  [color=#" + Utils.COLOR_WARNING + "]Rentes: -" + str(rente_cost) + "g[/color]\n"
	# EC-U2 (Combat Overhaul Phase 4): per-turn maintenance of built
	# structures (depots, forts, training grounds, markets, stables,
	# watchtowers) — the conquest-free gold sink; its own signed Net
	# component (same SC-33 contract, NET_GOLD_COMPONENTS-guarded).
	var infrastructure = int(econ.get("infrastructure", 0))
	if infrastructure > 0:
		bbcode += "  [color=#" + Utils.COLOR_WARNING + "]Infrastructure: -" + str(infrastructure) + "g[/color]\n"
	# DEF-5 naval (NV-1): the blockade's trade suspension + the Admiralty's
	# war ship upkeep — signed Net components (same SC-33 contract).
	var blockade = int(econ.get("blockade", 0))
	if blockade > 0:
		bbcode += "  [color=#" + Utils.COLOR_WARNING + "]Blockade: -" + str(blockade) + "g  (trade halved under enemy sail)[/color]\n"
	var admiralty = int(econ.get("admiralty", 0))
	if admiralty > 0:
		bbcode += "  [color=#" + Utils.COLOR_WARNING + "]Admiralty: -" + str(admiralty) + "g[/color]\n"
	# ES-3 (Economy Revisit S5): Upkeep is split into the base line and an
	# over-limit surcharge line (backend guarantees base + surcharge == the
	# folded total, so the visible lines still sum to Net — §3 invariant).
	var upkeep_surcharge = int(econ.get("upkeep_surcharge", 0))
	var upkeep_base = int(econ.get("upkeep_base", upkeep))
	# EC-U3: the surcharge splits into the ES-3 over-limit part and the Grande
	# Armée premium (a supermassive standing army's diseconomies of scale).
	var grande_armee = int(econ.get("grande_armee", 0))
	var over_limit_surcharge = upkeep_surcharge - grande_armee
	bbcode += "  Upkeep:   -" + str(upkeep_base) + "g\n"
	if over_limit_surcharge > 0:
		var force_limit = int(econ.get("force_limit", 0))
		var army_total = int(econ.get("army_strength_total", 0))
		bbcode += "  [color=#" + Utils.COLOR_WARNING + "]Over-limit surcharge: -" + str(over_limit_surcharge) + "g"
		if force_limit > 0:
			bbcode += "  (" + _format_number(army_total) + " / " + _format_number(force_limit) + " force limit)"
		bbcode += "[/color]\n"
	if grande_armee > 0:
		bbcode += "  [color=#" + Utils.COLOR_WARNING + "]Grande Armée surcharge: -" + str(grande_armee) + "g[/color]\n"

	# "The Levy is Open" (econ spec review §6). The force limit used to render
	# ONLY inside the over-limit branch above — visible exactly while the gate
	# was shut, and gone the moment it opened. It is now a standing line, and
	# when there is room under the ordinance it says what the room costs.
	var levy = econ.get("levy", {})
	if levy is Dictionary and int(levy.get("force_limit", 0)) > 0:
		var l_army = int(levy.get("army_strength", 0))
		var l_limit = int(levy.get("force_limit", 0))
		var l_room = int(levy.get("headroom", 0))
		var l_over = int(levy.get("over_by", 0))
		bbcode += "  Establishment: " + _format_number(l_army) + " / " + _format_number(l_limit)
		if l_over > 0:
			bbcode += "  [color=#" + Utils.COLOR_WARNING + "](" + _format_number(l_over) + " over the ordinance)[/color]\n"
		else:
			bbcode += "  [color=#" + Utils.COLOR_SUCCESS + "](" + _format_number(l_room) + " under)[/color]\n"
		if bool(levy.get("open", false)):
			bbcode += "  [color=#" + Utils.COLOR_SUCCESS + "]The depots are open: " \
				+ _format_number(int(levy.get("infantry_amount", 0))) + " foot for " \
				+ str(int(levy.get("infantry_price", 0))) + "g" \
				+ "  (pool " + _format_number(int(levy.get("infantry_pool", 0))) + ")[/color]\n"

	var net_color = Utils.COLOR_SUCCESS if net >= 0 else Utils.COLOR_ERROR
	var net_sign = "+" if net >= 0 else ""
	bbcode += "  Net:      [color=#" + net_color + "]" + net_sign + str(net) + "g[/color]\n"

	if bankruptcy > 0:
		bbcode += "  [color=#" + Utils.COLOR_ERROR + "]BANKRUPT — " + str(bankruptcy) + " turn(s)[/color]\n"

	# Active settlement payment streams (incoming tribute / outgoing
	# obligations), with turns remaining.
	var streams = econ.get("settlement_streams", [])
	if streams is Array and streams.size() > 0:
		bbcode += "\n[color=#" + Utils.COLOR_HEADER + "]Settlement Payments[/color]\n"
		for stream in streams:
			if not (stream is Dictionary):
				continue
			var line = str(stream.get("display", ""))
			if line == "":
				continue
			var s_color = Utils.COLOR_SUCCESS if str(stream.get("direction", "")) == "incoming" else Utils.COLOR_ERROR
			bbcode += "  [color=#" + s_color + "]" + Utils.humanize_nation_keys_in_text(line) + "[/color]\n"

	# Income breakdown
	var breakdown = econ.get("income_breakdown", [])
	if breakdown.size() > 0:
		bbcode += "\n[color=#" + Utils.COLOR_HEADER + "]Income by Region[/color]\n"
		for entry in breakdown:
			var rname = str(entry.get("region", "?"))
			var rincome = int(entry.get("income", 0))
			var rtype = str(entry.get("type", "town"))
			bbcode += "  " + rname + " (" + rtype.replace("_", " ") + "): " + str(rincome) + "g\n"

	# Construction
	var queue = econ.get("construction_queue", [])
	if queue.size() > 0:
		bbcode += "\n[color=#" + Utils.COLOR_HEADER + "]Under Construction[/color]\n"
		for item in queue:
			var cregion = str(item.get("region", "?"))
			var cbuilding = str(item.get("building", "?"))
			var cturns = int(item.get("turns_remaining", 0))
			bbcode += "  " + cregion + ": " + cbuilding + " (" + str(cturns) + " turns)\n"

	bbcode += _render_admiralty_block()

	content_area.text = bbcode


func _render_admiralty_block() -> String:
	# DEF-5 naval (NAVAL_SPEC §9): THE ADMIRALTY — own fleet, the Blockade
	# board (both directions), CS closure, the Crossings verdict lines and
	# the honest gate terms. Backend-derived, shown = applied; absent or
	# inactive on fleet-less worlds (the arm renders nothing).
	var adm = cached_data.get("admiralty", {})
	if not (adm is Dictionary) or not adm.get("active", false):
		return ""
	var bbcode = "\n[color=#" + Utils.COLOR_HEADER + "]═══ THE ADMIRALTY ═══[/color]\n"
	var fleet = adm.get("own_fleet")
	if fleet is Dictionary:
		var posture = str(fleet.get("posture", "guard"))
		var posture_line = "blockade — every enemy port watched" if posture == "blockade" else "guard — home waters covered"
		bbcode += "  Fleet: " + str(int(fleet.get("ships", 0))) + " sail of the line — readiness " + str(int(fleet.get("readiness", 0)))
		var admiral = str(fleet.get("admiral", ""))
		if admiral != "":
			bbcode += "  (Adm. " + admiral + ")"
		bbcode += "\n  Posture: " + posture_line + "\n"
		var yards = fleet.get("yards", [])
		if yards is Array and yards.size() > 0:
			var laid = int(fleet.get("laid_this_turn", 0))
			var rate = int(fleet.get("build_rate", 2))
			bbcode += "  Yards: " + ", ".join(PackedStringArray(yards)) + "  (" + str(laid) + "/" + str(rate) + " keels this turn)\n"
		var window = int(fleet.get("window_turns", 0))
		if window > 0:
			bbcode += "  [color=#" + Utils.COLOR_SUCCESS + "]THE STRAIT LIES OPEN — " + str(window) + " turn(s) remain[/color]\n"
		var camp_strength = int(fleet.get("camp_strength", 0))
		if camp_strength > 0:
			var camp_turns = int(fleet.get("camp_turns", 0))
			bbcode += "  The Camp: " + _format_number(camp_strength) + " men on the invasion coast"
			if camp_turns >= 2:
				bbcode += "  [color=#" + Utils.COLOR_WARNING + "](STAGED — the enemy has seen it)[/color]"
			bbcode += "\n"
	else:
		bbcode += "  We keep no fleet in commission.\n"
	var cs = adm.get("continental_system")
	if cs is Dictionary:
		var tier = int(cs.get("tier", 0))
		var cs_line = "  The Continental System: " + str(int(cs.get("closure_pct", 0))) + "% of the Continent's ports closed"
		if tier > 0:
			cs_line += " — " + Utils.humanize_nation_keys_in_text(str(cs.get("target", ""))) + "'s war-weariness rising +" + str(tier) + "/turn"
		else:
			# NV-5: below the lowest notch the percentage is true and inert.
			# Say so, and say what closes the next one.
			cs_line += " — [color=#" + Utils.COLOR_GREY + "]not yet biting[/color]"
		bbcode += cs_line + "\n"
		var next_pct = cs.get("next_tier_pct")
		if next_pct != null:
			bbcode += "  [color=#" + Utils.COLOR_GREY + "]Next notch at " + str(int(next_pct)) + "% — " + str(int(cs.get("ports_to_next_tier", 0))) + " more port(s) closed to them.[/color]\n"
	var board = adm.get("blockade_board", [])
	if board is Array and board.size() > 0:
		bbcode += "\n[color=#" + Utils.COLOR_HEADER + "]The Blockade Board[/color]\n"
		for row in board:
			if not (row is Dictionary):
				continue
			var row_nation = Utils.humanize_nation_keys_in_text(str(row.get("nation", "?")))
			var row_blockader = Utils.humanize_nation_keys_in_text(str(row.get("blockader", "?")))
			var row_color = Utils.COLOR_ERROR if row.get("against_us", false) else (Utils.COLOR_SUCCESS if row.get("ours", false) else Utils.COLOR_TEXT)
			bbcode += "  [color=#" + row_color + "]" + row_nation + " — blockaded by " + row_blockader + ": " + str(row.get("effects", "")) + "[/color]\n"
	var crossings = adm.get("crossings", [])
	if crossings is Array and crossings.size() > 0:
		bbcode += "\n[color=#" + Utils.COLOR_HEADER + "]The Crossings[/color]\n"
		for cx in crossings:
			if not (cx is Dictionary):
				continue
			var verdict = str(cx.get("verdict", "open"))
			var cx_color = Utils.COLOR_TEXT
			if verdict == "shut":
				cx_color = Utils.COLOR_ERROR
			elif verdict == "landing":
				# NV-4: the water is ours, the shore is not — amber, matching
				# the map's own tint for the same link.
				cx_color = Utils.COLOR_ORANGE
			elif verdict == "window":
				cx_color = Utils.COLOR_SUCCESS
			bbcode += "  [color=#" + cx_color + "]" + str(cx.get("line", "")) + "[/color]\n"
	var div_terms = adm.get("diversion_terms", [])
	if div_terms is Array and div_terms.size() > 0:
		bbcode += "\n[color=#" + Utils.COLOR_HEADER + "]The Grand Diversion[/color]  (\"order the diversion\")\n"
		for term in div_terms:
			if not (term is Dictionary):
				continue
			var met = bool(term.get("met", false))
			var mark = "[color=#" + Utils.COLOR_SUCCESS + "]+[/color]" if met else "[color=#" + Utils.COLOR_ERROR + "]x[/color]"
			bbcode += "  " + mark + " " + str(term.get("text", "")) + "\n"
	bbcode += _render_admiralty_orders(adm)
	return bbcode


func _render_admiralty_orders(adm: Dictionary) -> String:
	"""NV-6 — the Admiralty's orders as clickable chips. Every naval verb
	but `build_fleet` used to be typed-command only. Each chip carries the
	same typed command a player would write, and its enabled state comes
	from the backend gate (honest availability, the section 11.6 idiom): a
	shown chip works, a withheld one states why in present tense."""
	var chips = adm.get("chips", [])
	var ready = adm.get("embark_ready", [])
	if not (chips is Array) or chips.is_empty():
		return ""
	var bbcode = "\n[color=#" + Utils.COLOR_HEADER + "]Orders to the Admiralty[/color]\n"
	for chip in chips:
		if not (chip is Dictionary):
			continue
		var label = str(chip.get("label", ""))
		var enabled = bool(chip.get("enabled", false))
		bbcode += "  "
		if enabled:
			bbcode += Utils.bb_button_chip("do:" + str(chip.get("command", "")),
				label, Utils.COLOR_GOLD, _NAVAL_CHIP_BG)
			var note = str(chip.get("note", ""))
			if note != "":
				bbcode += "  [color=#" + Utils.COLOR_GREY + "]" + note + "[/color]"
		else:
			bbcode += "[color=#" + Utils.COLOR_GREY + "]" + label + " — " \
				+ str(chip.get("reason", "not available")) + "[/color]"
		bbcode += "\n"
	if ready is Array and ready.size() > 0:
		# The expedition's chip lives on the map, where its destination is
		# actually chosen — say so rather than offering a verb with no object.
		var names: Array = []
		for corps in ready:
			if corps is Dictionary:
				names.append(str(corps.get("marshal", "")) + " ("
					+ Utils.format_number(int(corps.get("strength", 0))) + " at "
					+ str(corps.get("location", "")) + ")")
		bbcode += "  [color=#" + Utils.COLOR_GREY + "]Ready to embark: " \
			+ ", ".join(names) + " — click a coastal province to choose the landing.[/color]\n"
	return bbcode


func _render_intel():
	var intel_data = cached_data.get("intel", {})
	var bbcode = ""
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]═══ INTELLIGENCE ═══[/color]\n\n"

	var enemies = intel_data.get("known_enemies", [])
	var unknown_count = int(intel_data.get("unknown_region_count", 0))

	if enemies.size() == 0:
		bbcode += "[color=#" + Utils.COLOR_INFO + "]No enemy forces in observation range.[/color]\n"
	else:
		bbcode += "[color=#" + Utils.COLOR_HEADER + "]Known Enemy Forces[/color]\n"
		for e in enemies:
			var ename = str(e.get("name", "?"))
			var enation = str(e.get("nation", "?"))
			var eloc = str(e.get("location", "?"))
			var estr = str(e.get("strength_display", "?"))
			var evis = str(e.get("visibility", "unknown"))

			var vis_color = Utils.COLOR_INFO
			var vis_label = ""
			match evis:
				"full":
					vis_color = Utils.COLOR_SUCCESS
					vis_label = "[confirmed]"
				"partial":
					vis_color = Utils.COLOR_INFO
					vis_label = "[partial]"
				"stale":
					vis_color = Utils.COLOR_ORANGE
					vis_label = "[stale]"
				"last_known":
					vis_color = Utils.COLOR_ERROR
					vis_label = "[last known]"

			bbcode += "  " + ename + " (" + Utils.display_nation_name(enation) + ") at " + eloc + " — " + estr
			bbcode += " [color=#" + vis_color + "]" + vis_label + "[/color]\n"

	# Nation summaries
	var summaries = intel_data.get("nation_summaries", [])
	if summaries.size() > 0:
		bbcode += "\n[color=#" + Utils.COLOR_HEADER + "]Nation Summary[/color]\n"
		for s in summaries:
			var sname = str(s.get("nation", "?"))
			var smarshals = int(s.get("known_marshals", 0))
			var sstrength = int(s.get("estimated_strength", 0))
			var sregions = int(s.get("regions_controlled", 0))
			bbcode += "  " + Utils.display_nation_name(sname) + ": " + str(smarshals) + " marshals spotted"
			bbcode += ", ~" + _format_number(sstrength) + " est. strength"
			bbcode += ", " + str(sregions) + " regions\n"

	if unknown_count > 0:
		bbcode += "\n[color=#" + Utils.COLOR_GREY + "]" + str(unknown_count) + " region(s) with no intel.[/color]\n"

	# AI-0b: the campaign seed, shown and shareable (top-level ledger key).
	# Review fix [4]: the seed is a raw user-supplied string (SOVEREIGN_SEED
	# env / pasted shares) — strip bbcode brackets before rendering.
	var campaign_seed = str(cached_data.get("campaign_seed", "historical"))
	campaign_seed = campaign_seed.replace("[", "").replace("]", "")
	bbcode += "\n[color=#" + Utils.COLOR_GREY + "]Campaign seed: " + campaign_seed + "[/color]\n"

	content_area.text = bbcode


func _render_manpower():
	var mp = cached_data.get("manpower", {})
	var bbcode = ""
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]═══ MANPOWER ═══[/color]\n\n"

	for pool_type in ["infantry", "cavalry", "artillery"]:
		var pool = mp.get(pool_type, {})
		var current = int(pool.get("current", 0))
		var max_val = int(pool.get("max", 0))
		var regen = int(pool.get("regen_rate", 0))
		var recruit_amt = int(pool.get("recruit_amount", 0))
		var recruit_cost = int(pool.get("recruit_base_cost", 0))
		var cost_note = str(pool.get("cost_note", ""))
		var turns_full = int(pool.get("turns_until_full", 0))

		bbcode += "[color=#" + Utils.COLOR_GOLD + "]" + pool_type.to_upper() + "[/color]\n"

		# Pool bar with color coding
		var pool_color = Utils.COLOR_INFO
		if current == 0:
			pool_color = Utils.COLOR_ERROR
		elif current < recruit_amt:
			pool_color = Utils.COLOR_ORANGE

		bbcode += "  Pool: [color=#" + pool_color + "]" + _format_number(current) + "[/color]"
		bbcode += " / " + _format_number(max_val) + "\n"
		bbcode += "  Regen: +" + _format_number(regen) + "/turn"
		if turns_full == 0:
			bbcode += " (full)\n"
		elif turns_full == -1:
			bbcode += " (no regen)\n"
		else:
			bbcode += " (" + str(turns_full) + " turns to full)\n"

		bbcode += "  Recruit: " + _format_number(recruit_amt) + " troops for " + str(recruit_cost) + "g"
		if cost_note != "":
			bbcode += " — " + cost_note
		bbcode += "\n\n"

	content_area.text = bbcode


func _render_orders():
	var orders = cached_data.get("orders", [])
	var ap_remaining = int(cached_data.get("actions_remaining", 1))
	var can_cancel = ap_remaining > 0
	var bbcode = ""
	bbcode += "[color=#" + Utils.COLOR_HEADER + "]═══ STANDING ORDERS ═══[/color]\n\n"

	if orders.size() == 0:
		bbcode += "[color=#" + Utils.COLOR_INFO + "]No marshals available.[/color]\n"
		content_area.text = bbcode
		return

	if not can_cancel:
		bbcode += "[color=#" + Utils.COLOR_GREY + "]No actions remaining — cancel unavailable this turn.[/color]\n\n"

	var has_active = false
	var has_idle = false

	# Active orders first
	for o in orders:
		if not o.get("has_order", false):
			continue
		has_active = true
		var mname = str(o.get("marshal", "?"))
		var order_type = str(o.get("order_type", "?"))
		var target = str(o.get("target", ""))
		var location = str(o.get("location", "?"))
		var condition = str(o.get("condition", ""))
		var path_left = int(o.get("path_remaining", 0))

		bbcode += "  [color=#" + Utils.COLOR_GOLD + "]" + mname + "[/color]"
		bbcode += " at " + location + "\n"

		bbcode += "    " + order_type.to_upper()
		if target != "" and target != "generic":
			bbcode += " " + target

		if path_left > 0:
			bbcode += "  (" + str(path_left) + " regions left)"

		bbcode += "  │ " + condition

		if can_cancel:
			bbcode += "  [url=cancel:" + mname + "][color=#" + Utils.COLOR_ERROR + "][Cancel][/color][/url]"
		else:
			bbcode += "  [color=#" + Utils.COLOR_GREY + "][Cancel][/color]"
		bbcode += "\n\n"

	# Separator between active and idle
	if has_active:
		for o in orders:
			if not o.get("has_order", false):
				has_idle = true
				break
		if has_idle:
			bbcode += "[color=#" + Utils.COLOR_GREY + "]─────────────────────────────────────────────────────[/color]\n"

	# Idle marshals
	for o in orders:
		if o.get("has_order", false):
			continue
		var mname = str(o.get("marshal", "?"))
		var location = str(o.get("location", "?"))
		bbcode += "  [color=#" + Utils.COLOR_GREY + "]" + mname
		bbcode += " at " + location
		bbcode += "  │ No active orders"
		bbcode += "[/color]\n"

	content_area.text = bbcode


func _on_meta_clicked(meta):
	var meta_str = str(meta)
	if meta_str.begins_with("cancel:"):
		var marshal_name = meta_str.substr(7)
		if _api_client_ref:
			_api_client_ref.cancel_strategic_order(marshal_name, _on_cancel_result)
	elif meta_str.begins_with("do:"):
		# NV-6: an Admiralty chip carries its full typed command — the same
		# string a player would type; the executor owns every gate.
		var command = meta_str.substr("do:".length())
		if command != "":
			naval_command.emit(command)


func refresh_if_open() -> void:
	"""NV-6 — re-pull after a chip command so posture/crossings/gate terms
	update in place (the diplomatic-ledger idiom)."""
	if visible and _api_client_ref:
		_api_client_ref.get_ledger(_on_ledger_received)


func _on_cancel_result(_response):
	# Refresh the ledger to reflect the cancelled order
	if _api_client_ref:
		_api_client_ref.get_ledger(_on_ledger_received)


# =============================================================================
# HELPERS
# =============================================================================

func _format_number(n: int) -> String:
	"""Format number with comma separators — shared Utils helper (UI-6 dedupe)."""
	return Utils.format_number(n)


func _on_overlay_input(event):
	"""Click on dark overlay to close."""
	if event is InputEventMouseButton and event.pressed:
		close_view()
