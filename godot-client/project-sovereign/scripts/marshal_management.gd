extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Marshal Management Screen (Phase 6.5)
# =============================================================================
# Card-based read-only view of player marshals. CanvasLayer 50.
# Number keys 1-N jump to/highlight specific marshal.
# Pattern follows strategic_ledger.gd.
# =============================================================================

signal closed
# ES-7 second pass (§0.6.8 item 6): the card's [Reward…] link — main.gd
# opens the reward dialog with this card's payload.
signal reward_requested(card: Dictionary)
# Marshal Recruitment (Jealousy v3.2): the Commission view's button —
# main.gd issues the typed `commission <name>` command through the same
# pipeline the reward dialog uses.
signal commission_requested(candidate_name: String)
# UI-6: a per-card order chip ([Fortify]/[Drill]) — main.gd sends the typed
# command through the reward pipeline (history + echo + Generals refresh).
signal order_command(command: String)

# UI References — paths match scene tree
@onready var background_overlay = $BackgroundOverlay
@onready var close_button = $PanelContainer/VBoxContainer/HeaderRow/CloseButton
@onready var scroll_container = $PanelContainer/VBoxContainer/ScrollContainer
@onready var content_area = $PanelContainer/VBoxContainer/ScrollContainer/ContentArea

# File-specific colors (not in Utils)
const COLOR_DIM = "666670"
const COLOR_DEVOTED = "ffd700"

# Inline graphical stat bars (skill + glory rows): the CC0 Kenney RPG frame+fill
# baked to assets/ui/bars/bar_<0..10>.png (grayscale, tinted per value via
# [img color]). Baked at 110x14 = display 1:1.
const STAT_BAR_W = 110
const STAT_BAR_H = 14

# UI-3 (texture/icon/portrait polish): PD marshal likenesses keyed by internal
# marshal name (assets/portraits/<name>.jpg|png — the same keys the coverage
# test guards). A keyless marshal (only Abdurrahman by design) degrades to a
# gold monogram so no card is ever faceless (spec §4/§2). Icons are the curated
# white-silhouette sets, tinted at render via the [img color=...] BBCode option.
const _PORTRAIT_DIR = "res://assets/portraits/"
const _PORTRAIT_EXTS = [".jpg", ".png", ".jpeg", ".webp"]
const _PORTRAIT_W = 80
const _PORTRAIT_H = 100
const _ICON_GAME = "res://assets/ui/icons/game-icons/"
const _ICON_PHOSPHOR = "res://assets/ui/icons/phosphor/"
# Cache portrait lookups so a long roster doesn't re-probe ResourceLoader each
# render (the overview re-renders on every refresh).
var _portrait_cache: Dictionary = {}

# State
var cached_data: Array = []
# Jealousy v3.2: the player's glory ladder + the recruitment pool ride the
# same /marshal_overview payload.
var cached_ladder: Array = []
var cached_recruitment: Dictionary = {}
# Commission view toggle — true renders the candidate bench instead of the
# marshal cards ([url=commission_open] / [url=commission_back]).
var _commission_view := false
# Stored at open() so the screen can refresh in place after a reward
# command lands (strategic_ledger.gd precedent).
var _api_client_ref = null

func _ready():
	close_button.pressed.connect(close_view)
	Utils.apply_icon_only_button(close_button, Utils.ICON_PHOSPHOR + "x.svg")
	background_overlay.gui_input.connect(_on_overlay_input)
	# §0.6.8: bbcode [url=reward:N] affordances (strategic_ledger pattern)
	content_area.meta_clicked.connect(_on_meta_clicked)
	hide()


func _input(event):
	"""Handle number keys 1-N to scroll to specific marshal."""
	if not visible:
		return
	if event is InputEventKey and event.pressed and not event.echo:
		var index = -1
		match event.keycode:
			KEY_1:
				index = 0
			KEY_2:
				index = 1
			KEY_3:
				index = 2
			KEY_4:
				index = 3
			KEY_5:
				index = 4
			KEY_6:
				index = 5
			KEY_7:
				index = 6
			KEY_8:
				index = 7
			KEY_9:
				index = 8
			_:
				return
		if index >= 0 and index < cached_data.size():
			# Scroll to marshal card — approximate position based on card height
			# TECH DEBT: px/card is hardcoded (320 → 380 for MC-2's skill-bar
			# rows → 520 for the UI-3 portrait thumbnail + the larger card font).
			# Revisit if playtesting shows scroll misalignment.
			var scroll_target = index * 520
			scroll_container.scroll_vertical = scroll_target
			get_viewport().set_input_as_handled()


func open(api_client):
	"""Fetch marshal overview from backend and display it."""
	_api_client_ref = api_client
	content_area.text = "[color=#" + Utils.COLOR_INFO + "]Loading marshal data...[/color]"
	AudioManager.play("panel_open")
	show()
	Utils.clamp_centered_panel($PanelContainer)
	api_client.get_marshal_overview(_on_data_received)


func refresh_if_open():
	"""Re-fetch the overview after a reward command so the card reflects
	the new estate/rente state (§0.6.8 item 6)."""
	if visible and _api_client_ref:
		_api_client_ref.get_marshal_overview(_on_data_received)


func _on_meta_clicked(meta):
	var meta_str = str(meta)
	if meta_str.begins_with("reward:"):
		var index = int(meta_str.substr(7))
		if index >= 0 and index < cached_data.size():
			reward_requested.emit(cached_data[index])
	elif meta_str == "commission_open":
		_commission_view = true
		_render_current_view()
	elif meta_str == "commission_back":
		_commission_view = false
		_render_current_view()
	elif meta_str.begins_with("commission:"):
		var candidate = meta_str.substr(11)
		if candidate != "":
			commission_requested.emit(candidate)
	elif meta_str.begins_with("order:"):
		# UI-6: order chip — "order:<verb>:<MarshalName>" → "<Name>, <verb>",
		# the same string a player would type (marshal names carry no colons).
		var parts = meta_str.split(":")
		if parts.size() == 3 and str(parts[2]) != "":
			order_command.emit(str(parts[2]) + ", " + str(parts[1]))


func close_view():
	"""Hide the overlay and emit closed signal."""
	if visible:
		AudioManager.play("panel_close")
	hide()
	cached_data = []
	cached_ladder = []
	cached_recruitment = {}
	_commission_view = false
	closed.emit()


func _on_data_received(response):
	"""Cache data and render all marshal cards."""
	if not visible:
		return

	if not response.get("success", false):
		content_area.text = "[color=#" + Utils.COLOR_ERROR + "]Failed to load marshal data.[/color]"
		return

	cached_data = response.get("marshals", [])
	cached_ladder = response.get("glory_ladder", [])
	cached_recruitment = response.get("recruitment", {})
	# A wiped standing roster must STILL render the glory ladder + Commission
	# link (the sole UI door to the Marshalate recovery feature) when a bench
	# exists — otherwise losing every marshal strands the player with no path
	# to raise a new one. Only truly-empty (no marshals AND no bench) shows the
	# bare notice.
	var _bench = cached_recruitment.get("candidates", []) if cached_recruitment is Dictionary else []
	var _has_bench = _bench is Array and _bench.size() > 0
	if cached_data.size() == 0 and not _commission_view and not _has_bench:
		content_area.text = "[color=#" + Utils.COLOR_INFO + "]No marshals available.[/color]"
		return

	_render_current_view()


func _render_current_view():
	if _commission_view:
		_render_commission_view()
	else:
		_render_all_cards()


func _render_all_cards():
	"""Render the glory ladder header, then all marshal cards."""
	var bbcode = _render_glory_ladder()

	for i in range(cached_data.size()):
		var m = cached_data[i]
		bbcode += _render_card(m, i)
		if i < cached_data.size() - 1:
			bbcode += "[color=#" + Utils.COLOR_GREY + "]────────────────────────────────────────[/color]\n\n"

	content_area.text = bbcode


func _render_glory_ladder() -> String:
	"""Jealousy v3.2: THE LAURELS OF THE ARMY — the nation's glory ladder
	(rank, ★ crown, 10-wide glory bar, live grievance arrows) plus the
	Commission affordance when a candidate bench exists."""
	var bbcode = ""
	var candidates = cached_recruitment.get("candidates", [])
	var has_bench = candidates is Array and candidates.size() > 0

	if cached_ladder is Array and cached_ladder.size() > 1:
		bbcode += _icon(_ICON_PHOSPHOR + "medal-military.svg", 20, Utils.COLOR_GOLD)
		bbcode += " [color=#" + Utils.COLOR_GOLD + "]THE LAURELS OF THE ARMY[/color]"
		bbcode += "  [color=#" + COLOR_DIM + "](glory, last 5 turns — the man above draws the envy of the man below)[/color]\n"
		for i in range(cached_ladder.size()):
			var row = cached_ladder[i]
			var rname = str(row.get("name", "?"))
			var glory = int(row.get("glory", 0))
			var crowned = bool(row.get("crowned", false))
			var envies = str(row.get("jealous_of", "")) if row.get("jealous_of") != null else ""
			var filled = clampi(glory, 0, 10)
			var bar_color = Utils.COLOR_GOLD if crowned else (Utils.COLOR_INFO if glory > 0 else COLOR_DIM)
			var bar = _stat_bar_img(filled, bar_color)
			bbcode += "  " + str(i + 1) + ". "
			if crowned:
				bbcode += "[color=#" + COLOR_DEVOTED + "]★ " + rname + "[/color]"
			else:
				bbcode += rname
			bbcode += "  " + bar + " [color=#" + bar_color + "]" + str(glory) + "[/color]"
			if crowned:
				bbcode += "  [color=#" + COLOR_DEVOTED + "]Crowned with Glory (+1 shock/defense/administration)[/color]"
			if envies != "":
				bbcode += "  [color=#" + Utils.COLOR_ERROR + "]» envious of " + envies + "[/color]"
			bbcode += "\n"
		bbcode += "\n"

	if has_bench:
		bbcode += _button_chip("commission_open", "Commission a Marshal…", "f4e6bd", "3a2f18", _ICON_PHOSPHOR + "crown.svg")
		bbcode += "  [color=#" + COLOR_DIM + "]" + str(candidates.size()) + " await the Emperor's call[/color]\n\n"

	if bbcode != "":
		bbcode += "[color=#" + Utils.COLOR_GREY + "]════════════════════════════════════════[/color]\n\n"
	return bbcode


func _render_commission_view():
	"""Marshal Recruitment: the candidate bench — full character sheets,
	honest availability (the executor's own check), price/corps chips."""
	var bbcode = _button_chip("commission_back", "← Back to the Marshalate", "a9c7e6", "22283a") + "\n\n"
	bbcode += _icon(_ICON_PHOSPHOR + "crown.svg", 20, Utils.COLOR_GOLD)
	bbcode += " [color=#" + Utils.COLOR_GOLD + "]COMMISSION A MARSHAL[/color]\n"
	var treasury = int(cached_recruitment.get("treasury", 0))
	var pool = int(cached_recruitment.get("infantry_pool", 0))
	var corps = int(cached_recruitment.get("corps_size", 5000))
	bbcode += "[color=#" + COLOR_DIM + "]Treasury: " + _format_number(treasury) + "g | Infantry pool: " + _format_number(pool)
	bbcode += " | A commission raises a corps of " + _format_number(corps) + " at the capital (1 admin AP + the candidate's price).[/color]\n\n"

	var candidates = cached_recruitment.get("candidates", [])
	if not (candidates is Array) or candidates.size() == 0:
		bbcode += "[color=#" + Utils.COLOR_INFO + "]The bench is empty — every marshal France could call already serves.[/color]"
		content_area.text = bbcode
		return

	for c in candidates:
		if not (c is Dictionary):
			continue
		var cname = str(c.get("name", "?"))
		var personality = str(c.get("personality", "?"))
		var cost = int(c.get("cost", 0))
		var available = bool(c.get("available", false))
		var reason = str(c.get("blocked_reason", ""))

		bbcode += _portrait_block(cname, 64, 80)
		bbcode += "[color=#" + Utils.COLOR_GOLD + "]" + cname + "[/color]"
		bbcode += "  [color=#" + Utils.COLOR_INFO + "][" + personality.capitalize() + "][/color]"
		if c.get("cavalry", false):
			bbcode += "  " + _unit_icon("Cavalry", Utils.COLOR_ORANGE) + " [color=#" + Utils.COLOR_ORANGE + "][Cavalry][/color]"
		bbcode += "  [color=#" + Utils.COLOR_GOLD + "]" + _format_number(cost) + "g[/color]\n"
		var bio = str(c.get("biography", ""))
		if bio != "":
			bbcode += "[color=#" + COLOR_DIM + "]" + bio + "[/color]\n"
		var skills = c.get("skills", {})
		if skills is Dictionary:
			for skill_name in ["tactical", "shock", "defense", "logistics", "administration", "command"]:
				if skills.has(skill_name):
					bbcode += "  " + _skill_bar_row(skill_name.capitalize(), int(skills.get(skill_name, 5)), "")
		var seeds = c.get("relationships", {})
		if seeds is Dictionary and seeds.size() > 0:
			var seed_parts = []
			for other in seeds:
				var v = int(seeds[other])
				var vlabel = "Friendly" if v > 0 else ("Rival" if v == -1 else "Hostile")
				seed_parts.append(other + ": " + _relationship_colored(v, vlabel))
			bbcode += "  [color=#" + COLOR_DIM + "]Arrives with a history —[/color] " + ", ".join(seed_parts) + "\n"
		if available:
			bbcode += "  " + _button_chip("commission:" + cname, "Commission " + cname + " — " + _format_number(cost) + "g", "b6e6b6", "1e3320") + "\n"
		else:
			bbcode += "  [color=#" + Utils.COLOR_ERROR + "]Unavailable: " + reason + "[/color]\n"
		bbcode += "\n[color=#" + Utils.COLOR_GREY + "]────────────────────────────────────────[/color]\n\n"

	content_area.text = bbcode


func _render_card(m: Dictionary, index: int) -> String:
	"""Render a single marshal card."""
	var bbcode = ""

	# ═══════ HEADER ═══════
	var name = str(m.get("name", "?"))
	var unit_type = str(m.get("unit_type", "Infantry"))
	var nation = str(m.get("nation", "?"))
	var personality = str(m.get("personality", "?"))

	# Unit type badge color
	var type_color = Utils.COLOR_INFO
	match unit_type:
		"Cavalry":
			type_color = Utils.COLOR_ORANGE
		"Artillery":
			type_color = Utils.COLOR_ERROR

	var key_hint = "[" + str(index + 1) + "] "
	bbcode += _portrait_block(name)
	bbcode += "[color=#" + Utils.COLOR_GREY + "]" + key_hint + "[/color]"
	bbcode += "[color=#" + Utils.COLOR_GOLD + "]" + name + "[/color]"
	# Cavalry/Artillery keep their (clear) icon; Infantry is label-only — the
	# game-icons infantry glyph reads as an ambiguous caret at 18px (UI-3 tune).
	if unit_type != "Infantry":
		bbcode += "  " + _unit_icon(unit_type, type_color) + " [color=#" + type_color + "][" + unit_type + "][/color]"
	else:
		bbcode += "  [color=#" + type_color + "][" + unit_type + "][/color]"
	bbcode += "  [color=#" + Utils.COLOR_GREY + "]" + Utils.display_nation_name(nation) + "[/color]\n"

	# ═══════ BIOGRAPHY ═══════
	var bio = str(m.get("biography", ""))
	if bio != "":
		bbcode += "[color=#" + COLOR_DIM + "]" + bio + "[/color]\n"

	# ═══════ PERSONALITY & UNIT TYPE ═══════
	var pers_desc = str(m.get("personality_description", ""))
	if pers_desc != "":
		bbcode += "[color=#" + Utils.COLOR_INFO + "]" + pers_desc + "[/color]\n"
	var type_desc = str(m.get("unit_type_description", ""))
	if type_desc != "":
		bbcode += "[color=#" + Utils.COLOR_INFO + "]" + type_desc + "[/color]\n"

	bbcode += "\n"

	# ═══════ COMBAT STATS ═══════
	var strength = int(m.get("strength", 0))
	var starting = int(m.get("starting_strength", 0))
	var morale = int(m.get("morale", 100))
	var move_range = int(m.get("movement_range", 1))

	# Strength color based on losses
	var str_color = Utils.COLOR_INFO
	if starting > 0:
		var ratio = float(strength) / float(starting)
		if ratio < 0.3:
			str_color = Utils.COLOR_ERROR
		elif ratio < 0.6:
			str_color = Utils.COLOR_ORANGE

	bbcode += "  Strength: [color=#" + str_color + "]" + _format_number(strength) + "[/color]"
	bbcode += " / " + _format_number(starting)
	bbcode += "  Morale: " + _morale_colored(morale)
	bbcode += "  Range: " + str(move_range) + "\n"

	# Skills — MC-2 character sheet: one bar row per wired skill (█░ bar idiom
	# matches the diplomatic ledger's threat/WE bars). Values, hints, and the
	# Rally/Intendance notes all ship from the backend (shown = applied —
	# Godot renders, never recomputes thresholds).
	# MC-2b (July 11, 2026): administration is wired (The Intendance, recruit
	# pricing). The backend omits the key where the mechanic is not live
	# (legacy rollback world), so absent keys are skipped, never defaulted.
	var skills = m.get("skills", {})
	var skill_notes = m.get("skill_notes", {})
	for skill_name in ["tactical", "shock", "defense", "logistics", "administration", "command"]:
		if not skills.has(skill_name):
			continue
		var val = int(skills.get(skill_name, 5))
		var note = str(skill_notes.get(skill_name, ""))
		bbcode += "  " + _skill_bar_row(skill_name.capitalize(), val, note)
	var admin_note = str(m.get("admin_note", ""))
	if admin_note != "":
		var admin_color = Utils.COLOR_SUCCESS if str(m.get("admin_tier", "")) == "thrifty" else Utils.COLOR_ORANGE
		bbcode += "  [color=#" + admin_color + "]" + admin_note + "[/color]\n"
	var rally_note = str(m.get("rally_note", ""))
	if rally_note != "":
		var rally_color = Utils.COLOR_SUCCESS if str(m.get("rally_tier", "")) == "fast" else Utils.COLOR_ORANGE
		bbcode += "  [color=#" + rally_color + "]" + rally_note + "[/color]\n"

	# ═══════ ABILITY (only shown if active/wired) ═══════
	var ab_name = str(m.get("ability_name", ""))
	var ab_effect = str(m.get("ability_effect", ""))
	var ab_active = m.get("ability_active", false)

	if ab_active and ab_name != "":
		bbcode += "  [color=#" + Utils.COLOR_GOLD + "]" + ab_name + "[/color]"
		if ab_effect != "":
			bbcode += "  [color=#" + Utils.COLOR_INFO + "]" + ab_effect + "[/color]"
		bbcode += "\n\n"

	# ═══════ TRUST & RECORD ═══════
	var trust_val = int(m.get("trust_value", 70))
	var trust_label = str(m.get("trust_label", "Neutral"))
	var vindication = int(m.get("vindication_score", 0))
	var won = int(m.get("battles_won", 0))
	var lost = int(m.get("battles_lost", 0))
	var overridden = int(m.get("orders_overridden", 0))

	bbcode += "  Trust: " + _trust_colored(trust_val, trust_label)
	bbcode += "  Vindication: " + _vindication_colored(vindication)
	bbcode += "  Record: " + str(won) + "W/" + str(lost) + "L"
	if overridden > 0:
		bbcode += "  [color=#" + Utils.COLOR_ORANGE + "]Overridden: " + str(overridden) + "x[/color]"
	bbcode += "\n"

	# ═══════ JEALOUSY v3.2: GLORY & GRIEVANCES (shown = applied) ═══════
	var glory = int(m.get("glory", 0))
	var glory_rank = int(m.get("glory_rank", 0))
	var glory_roster = int(m.get("glory_roster", 0))
	if glory > 0 or glory_rank > 0:
		bbcode += "  Glory: [color=#" + (Utils.COLOR_GOLD if glory > 0 else Utils.COLOR_GREY) + "]" + str(glory) + "[/color]"
		if glory_rank > 0 and glory_roster > 1:
			bbcode += "  [color=#" + COLOR_DIM + "](rank " + str(glory_rank) + " of " + str(glory_roster) + " on the ladder)[/color]"
		if m.get("glory_crowned", false):
			bbcode += "  [color=#" + COLOR_DEVOTED + "]★ CROWNED WITH GLORY (+1 shock/defense/administration)[/color]"
		bbcode += "\n"
	var jealous_of = str(m.get("jealous_of", "")) if m.get("jealous_of") != null else ""
	if jealous_of != "":
		var jl_turns = int(m.get("jealousy_turns_remaining", 0))
		bbcode += "  [color=#" + Utils.COLOR_ERROR + "]GRIEVANCE: envious of " + jealous_of
		if jl_turns > 0:
			bbcode += " (" + str(jl_turns) + " turn" + ("s" if jl_turns != 1 else "") + " unless satisfied)"
		if m.get("jealousy_warned", false):
			bbcode += " — HE EYES THE ENEMY ON HIS OWN; any order restrains him"
		bbcode += "[/color]\n"
	if m.get("jealousy_surge", false):
		bbcode += "  [color=#" + Utils.COLOR_SUCCESS + "]VINDICATED — he fights with renewed purpose this turn[/color]\n"
	var feuds = m.get("feuds", [])
	if feuds is Array and feuds.size() > 0:
		bbcode += "  [color=#" + Utils.COLOR_ORANGE + "]Entrenched feud: " + ", ".join(feuds) + "[/color]\n"
	var separations = m.get("separations", [])
	if separations is Array and separations.size() > 0:
		bbcode += "  [color=#" + COLOR_DIM + "]Kept apart from: " + ", ".join(separations) + " (Berthier watches)[/color]\n"

	# ═══════ ES-7 ESTATES & EXPECTATION (Economy Revisit S7 + §0.6.8) ═══════
	# Expectation vs estate income vs rente in the same g/turn units — the
	# number IS the explanation (green met / amber unmet / red eroding).
	var expectation = int(m.get("expectation", 0))
	var estate_income = int(m.get("estate_income", 0))
	var pension = int(m.get("pension", 0))
	var shortfall = int(m.get("expectation_shortfall", 0))
	var estate_title = str(m.get("estate_title", ""))
	var is_dotation = bool(m.get("is_dotation_world", false))
	if expectation > 0 or estate_income > 0 or pension > 0:
		if estate_title != "":
			bbcode += "  [color=#" + Utils.COLOR_GOLD + "]" + estate_title + "[/color]"
		var exp_color = Utils.COLOR_SUCCESS
		if m.get("is_eroding", false):
			exp_color = Utils.COLOR_ERROR
		elif shortfall > 0:
			exp_color = Utils.COLOR_WARNING
		bbcode += "  [color=#" + exp_color + "]Expects: " + str(expectation) + "g/turn | Estates: " + str(estate_income) + "g/turn"
		if pension > 0:
			bbcode += " | Rente: " + str(pension) + "g/turn (costs " + str(int(m.get("pension_cost", 0))) + "g)"
		if shortfall > 0:
			bbcode += " | Shortfall: " + str(shortfall) + "g"
			if m.get("is_eroding", false):
				bbcode += " — loyalty eroding"
		bbcode += "[/color]\n"
		# The Steward (§0.6.8 item 2): land appreciates or rots by this
		# marshal's administration — decision-relevant before endowing.
		var steward_note = str(m.get("steward_note", ""))
		if steward_note != "" and (estate_income > 0 or shortfall > 0):
			var steward_color = Utils.COLOR_SUCCESS if str(m.get("steward_tier", "")) == "prosperous" else Utils.COLOR_ORANGE
			bbcode += "  [color=#" + steward_color + "]" + steward_note + "[/color]\n"
		# §0.6.8 item 6: the Reward button — opens the estate/rente dialog.
		# Never for a PRISONER (the executors refuse him; review fix).
		if (shortfall > 0 or pension > 0) and not m.get("captured", false):
			bbcode += "  [url=reward:" + str(index) + "][color=#" + Utils.COLOR_GOLD + "][ Reward… ][/color][/url]"
			var eligible = m.get("eligible_estates", [])
			if shortfall > 0 and eligible is Array and eligible.size() > 0:
				var m_name_hint = str(m.get("name", "?"))
				bbcode += "  [color=#" + COLOR_DIM + "]or type: 'endow " + m_name_hint + " with " + str(eligible[0]) + "'[/color]"
			bbcode += "\n"
	elif is_dotation and not m.get("captured", false):
		# The reward portfolio is REACTIVE by design (ES-7 "cost of success"):
		# there is nothing to grant until he EARNS an expectation by winning
		# battles (and you hold a conquered province to endow). Surface that
		# it exists — otherwise the buttons the player is looking for read as
		# simply missing. (Fix for "where are the reward/duchy buttons?")
		bbcode += "  [color=#" + COLOR_DIM + "]Reward: victories in the field raise his expectation — then [ Reward… ] appears here to endow a conquered province (a Duchy) or grant a rente (gold per turn).[/color]\n"

	# ═══════ CURRENT STATUS ═══════
	var location = str(m.get("location", "?"))
	var stance = str(m.get("stance", "neutral"))

	bbcode += "  Location: " + location
	bbcode += "  Stance: " + _stance_colored(stance)

	# Status flags
	var flags = []
	if m.get("is_broken", false):
		flags.append("[color=#" + Utils.COLOR_ERROR + "]BROKEN (recovery: " + str(int(m.get("broken_recovery", 0))) + ")[/color]")
	if m.get("is_retreating", false):
		flags.append("[color=#" + Utils.COLOR_ERROR + "]RETREATING (stage: " + str(int(m.get("retreat_recovery", 0))) + ")[/color]")
	if m.get("is_fortified", false):
		var def_bonus = int(m.get("defense_bonus", 0))
		flags.append("[color=#" + Utils.COLOR_BLUE + "]FORTIFIED +" + str(def_bonus) + "%[/color]")
	# MC-1c Iron Resolve: render the backend's derived numbers (shown = applied)
	var iron_stacks = int(m.get("iron_resolve_stacks", 0))
	if iron_stacks > 0:
		var iron_pct = int(m.get("iron_resolve_bonus_pct", 0))
		var iron_max = int(m.get("iron_resolve_max_stacks", 3))
		flags.append("[color=#" + Utils.COLOR_GOLD + "]IRON RESOLVE " + str(iron_stacks) + "/" + str(iron_max) + " (+" + str(iron_pct) + "% next attack)[/color]")
	if m.get("is_drilling", false):
		var drill_txt = "DRILLING"
		if m.get("drilling_locked", false):
			drill_txt = "DRILL LOCKED"
		var shock = int(m.get("shock_bonus", 0))
		if shock > 0:
			drill_txt += " (+" + str(shock * 10) + "% shock)"
		flags.append("[color=#" + Utils.COLOR_BLUE + "]" + drill_txt + "[/color]")
	if m.get("square_formation", false):
		flags.append("[color=#" + Utils.COLOR_GOLD + "]SQUARE (+5% def, cav -40%, arty +50% vuln)[/color]")
	if m.get("is_autonomous", false):
		var reason = str(m.get("autonomy_reason", ""))
		flags.append("[color=#" + Utils.COLOR_ORANGE + "]AUTONOMOUS" + (" (" + reason + ")" if reason != "" else "") + "[/color]")

	var idle = int(m.get("idle_turns", 0))
	if idle >= 2:
		flags.append("[color=#" + Utils.COLOR_GREY + "]IDLE " + str(idle) + " turns[/color]")

	if flags.size() > 0:
		bbcode += "\n  " + " | ".join(flags)

	# Strategic order
	var strat = m.get("strategic_order")
	if strat != null and strat is Dictionary:
		var cmd = str(strat.get("command_type", "?"))
		var target = str(strat.get("target", "?"))
		bbcode += "\n  [color=#" + Utils.COLOR_BLUE + "]Order: " + cmd + " → " + target + "[/color]"

	bbcode += "\n"

	# ═══════ UI-6: ORDER CHIPS (target-free orders, one click) ═══════
	# Only for a marshal who can act — the executor still owns every gate
	# (AP, objections, terrain); a refused chip reports like a typed refusal.
	if (not m.get("captured", false) and not m.get("is_broken", false)
			and not m.get("is_retreating", false)):
		var chip_name = str(m.get("name", ""))
		if chip_name != "":
			var order_chips = []
			if m.get("is_fortified", false):
				order_chips.append(Utils.bb_button_chip("order:unfortify:" + chip_name, "Unfortify", Utils.COLOR_COMMAND, "233043"))
			else:
				order_chips.append(Utils.bb_button_chip("order:fortify:" + chip_name, "Fortify", Utils.COLOR_COMMAND, "233043"))
			if not m.get("is_drilling", false):
				order_chips.append(Utils.bb_button_chip("order:drill:" + chip_name, "Drill", Utils.COLOR_COMMAND, "233043"))
			if order_chips.size() > 0:
				bbcode += "  " + "  ".join(PackedStringArray(order_chips)) + "\n"

	# ═══════ UNIT SPECIFICS ═══════
	var specifics = []
	if m.get("cavalry", false):
		if m.get("counter_punch_available", false):
			specifics.append("[color=#" + Utils.COLOR_SUCCESS + "]Counter-Punch READY[/color]")
		if m.get("holding_position", false):
			specifics.append("[color=#" + Utils.COLOR_BLUE + "]Holding Position[/color]")
	if m.get("artillery", false):
		var bombards = int(m.get("bombardments_this_turn", 0))
		specifics.append("Bombardments: " + str(bombards) + "/2")
		if m.get("moved_this_turn", false):
			specifics.append("[color=#" + Utils.COLOR_ORANGE + "]Moved (cannot fire)[/color]")

	if specifics.size() > 0:
		bbcode += "  " + " | ".join(specifics) + "\n"

	# ═══════ RELATIONSHIPS ═══════
	var rels = m.get("relationships", [])
	if rels.size() > 0:
		var rel_parts = []
		for r in rels:
			var rname = str(r.get("name", "?"))
			var rval = int(r.get("value", 0))
			var rlabel = str(r.get("label", "Professional"))
			rel_parts.append(rname + ": " + _relationship_colored(rval, rlabel))
		bbcode += "  Relationships: " + ", ".join(rel_parts) + "\n"

	bbcode += "\n"
	return bbcode


# =============================================================================
# COLOR HELPERS
# =============================================================================

# =============================================================================
# UI-3 PORTRAIT / ICON HELPERS
# =============================================================================

func _portrait_block(name: String, w: int = _PORTRAIT_W, h: int = _PORTRAIT_H) -> String:
	"""A portrait thumbnail on its own line (natural colour), or a gold monogram
	when no PD likeness exists (Abdurrahman by design). Lookups are cached so a
	long roster does not re-probe ResourceLoader on every re-render."""
	var path = ""
	if _portrait_cache.has(name):
		path = _portrait_cache[name]
	else:
		for ext in _PORTRAIT_EXTS:
			var p = _PORTRAIT_DIR + name + ext
			if ResourceLoader.exists(p):
				path = p
				break
		_portrait_cache[name] = path
	if path != "":
		return "[img width=%d height=%d]%s[/img]\n" % [w, h, path]
	var initial = name.substr(0, 1).to_upper() if name.length() > 0 else "?"
	return "[color=#" + Utils.COLOR_GOLD + "]〔 " + initial + " 〕[/color]\n"


func _icon(path: String, size: int, color: String) -> String:
	"""Inline BBCode icon — delegates to the UI-6 shared helper."""
	return Utils.bb_icon(path, size, color)


func _unit_icon(unit_type: String, color: String) -> String:
	var key = "unit-infantry"
	match unit_type:
		"Cavalry":
			key = "unit-cavalry"
		"Artillery":
			key = "unit-artillery"
	return _icon(_ICON_GAME + key + ".svg", 18, color)


func _button_chip(url_meta: String, label: String, text_hex: String, bg_hex: String, icon_path := "") -> String:
	"""Filled bbcode 'button' — delegates to the UI-6 shared helper."""
	return Utils.bb_button_chip(url_meta, label, text_hex, bg_hex, icon_path)


func _format_number(n: int) -> String:
	"""Format number with comma separators — shared Utils helper (UI-6 dedupe)."""
	return Utils.format_number(n)


func _morale_colored(morale: int) -> String:
	var color = Utils.COLOR_INFO
	if morale < 40:
		color = Utils.COLOR_ERROR
	elif morale < 60:
		color = Utils.COLOR_ORANGE
	return "[color=#" + color + "]" + str(morale) + "%[/color]"


func _skill_bar_row(label: String, val: int, note: String) -> String:
	"""One character-sheet skill row: label, 10-wide █░ bar, value, dim hint.
	Peak (8+) green, weak (3-) red, middling grey/plain — same thresholds the
	old compact line used."""
	var color = Utils.COLOR_INFO
	if val >= 8:
		color = Utils.COLOR_SUCCESS
	elif val <= 3:
		color = Utils.COLOR_ERROR
	elif val <= 5:
		color = Utils.COLOR_GREY
	var filled = clampi(val, 0, 10)
	# Inline GRAPHICAL bar (CC0 Kenney RPG frame+fill, assets/ui/bars/bar_<v>.png):
	# a grayscale glossy fill tinted per value via [img color]. Bar FIRST + fixed
	# width so the bars form a clean column regardless of label width (the old █░
	# text bars staircased under the proportional UI font once a label like
	# "Administration" led the row).
	var bar = _stat_bar_img(filled, color)
	var row = bar + "  " + label + " [color=#" + color + "]" + str(val) + "[/color]"
	if note != "":
		row += "  [color=#" + COLOR_DIM + "]" + note + "[/color]"
	return row + "\n"


func _stat_bar_img(filled: int, hex_color: String) -> String:
	"""One inline graphical stat bar, value 0..10, tinted to hex_color (no '#')."""
	var v = clampi(filled, 0, 10)
	return ("[img color=#" + hex_color + " width=" + str(STAT_BAR_W)
		+ " height=" + str(STAT_BAR_H) + "]res://assets/ui/bars/bar_"
		+ str(v) + ".png[/img]")


func _trust_colored(val: int, label: String) -> String:
	var color = Utils.COLOR_INFO
	if val < 30:
		color = Utils.COLOR_ERROR
	elif val < 55:
		color = Utils.COLOR_ORANGE
	elif val >= 80:
		color = Utils.COLOR_SUCCESS
	return "[color=#" + color + "]" + str(val) + " (" + label + ")[/color]"


func _vindication_colored(val: int) -> String:
	var color = Utils.COLOR_INFO
	if val > 0:
		color = Utils.COLOR_SUCCESS
	elif val < 0:
		color = Utils.COLOR_ERROR
	var sign = "+" if val > 0 else ""
	return "[color=#" + color + "]" + sign + str(val) + "[/color]"


func _stance_colored(stance: String) -> String:
	var color = Utils.COLOR_INFO
	match stance:
		"aggressive":
			color = Utils.COLOR_ERROR
		"defensive":
			color = Utils.COLOR_BLUE
	return "[color=#" + color + "]" + stance.capitalize() + "[/color]"


func _relationship_colored(val: int, label: String) -> String:
	var color = Utils.COLOR_GREY
	match val:
		-2:
			color = Utils.COLOR_ERROR
		-1:
			color = Utils.COLOR_ORANGE
		1:
			color = Utils.COLOR_SUCCESS
		2:
			color = COLOR_DEVOTED
	var sign = "+" if val > 0 else ""
	return "[color=#" + color + "]" + label + " (" + sign + str(val) + ")[/color]"


func _on_overlay_input(event):
	"""Click on dark overlay to close."""
	if event is InputEventMouseButton and event.pressed:
		close_view()
