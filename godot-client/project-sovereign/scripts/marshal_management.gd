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
# PC15-10 B1 "The Antechamber": the card's "Hear him" chip — main.gd
# fetches the waiting petition (GET /marshal_petition) into its dialog.
signal audience_requested

# UI References — paths match scene tree
@onready var background_overlay = $BackgroundOverlay
@onready var close_button = $PanelContainer/VBoxContainer/HeaderRow/CloseButton
@onready var scroll_container = $PanelContainer/VBoxContainer/ScrollContainer
@onready var content_area = $PanelContainer/VBoxContainer/ScrollContainer/ContentArea

# File-specific colors (not in Utils)
# UXR-D2: the faintest grey was Utils.COLOR_DIM; S12 (UXR3-25) set every body
# line at the floor step, Utils.COLOR_INFO (High contrast raises it).
const COLOR_DEVOTED = "ffd700"
# Session UI-2 (K): the card's highlighted chips (Hear him, Reward, Commission)
# wear the gilt: ivory ink on a deep gold, not the old muddy brown.
const CHIP_GILT_INK := "fbf1d6"
const CHIP_GILT_BG := "7a5c1c"
# IQ-2 (Sept 14, 2026) flip lever — true: a captured marshal's card renders
# the backend's `status_note` ("PRISONER of Austria since T37.") at the head
# of its status block. false = the pre-IQ-2 card byte-for-byte.
const PRISONER_NOTE_ON_THE_CARD := true

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
# CN-3 rider 2: the corps noun on the commission bench (the region panel's
# recruit chips say it the same way — foot, horse, guns).
const _BENCH_ARM_NOUN = {"infantry": "foot", "cavalry": "horse", "artillery": "guns"}
# Cache portrait lookups so a long roster doesn't re-probe ResourceLoader each
# render (the overview re-renders on every refresh).
var _portrait_cache: Dictionary = {}

# State
var cached_data: Array = []
# Jealousy v3.2: the player's glory ladder + the recruitment pool ride the
# same /marshal_overview payload.
var cached_ladder: Array = []
var cached_recruitment: Dictionary = {}
# SR-7d DC-3a (DOCTRINES_SPEC §4a): OUR DOCTRINE — `/marshal_overview`'s
# `doctrine` payload (name, says, strength, flaw with the cure's status).
var cached_doctrine: Dictionary = {}
# G2 (the played campaign): the kings the Emperor has made. A marshal
# crowned at the peace table left this screen without a word.
var cached_reigning: Array = []
# A11 (CA9 row 3): the glory window, served by the backend so the ladder
# caption cannot drift from `jealousy.GLORY_WINDOW` again.
var cached_glory_window: int = 8
# Commission view toggle — true renders the candidate bench instead of the
# marshal cards ([url=commission_open] / [url=commission_back]).
var _commission_view := false
# UXR3-24 / UXR3-80 (Pre-Deploy S15 head, October 25, 2026): OUR DOCTRINE
# folds to its one title line behind "▸ the doctrine", so the Emperor's card
# and the roster's sheets lead the first screenful. The player's own
# toggle persists for the session (a plain var, like the wizard's
# `_congress_terms_open`); close_view() leaves it alone. The one board whose
# subject IS the doctrine (`generals_doctrine`) opens it by a harness step.
var _doctrine_open := false
# Stored at open() so the screen can refresh in place after a reward
# command lands (strategic_ledger.gd precedent).
var _api_client_ref = null

func _ready():
	# UXR3-F3: the reading scroll comes to rest on whole lines.
	Utils.keep_whole_lines(scroll_container)
	# Session UI (November 11, 2026): every marshal a card — `_render_card`
	# wraps itself in the marks, `scripts/card_underlay.gd` paints them.
	Utils.card_page(content_area)
	close_button.pressed.connect(close_view)
	Utils.apply_icon_only_button(close_button, Utils.ICON_PHOSPHOR + "x.svg")
	background_overlay.gui_input.connect(_on_overlay_input)
	# UXR-2: clamped AND gripped — the player's size is remembered.
	ResizeGrip.attach_centered($PanelContainer, "generals")
	# PC15-18 (NV-P1 family census): a fit_content RichTextLabel inside a
	# ScrollContainer defaults to MOUSE_FILTER_STOP and eats the wheel
	# before its parent can scroll. PASS keeps the [url=…] chips working.
	content_area.mouse_filter = Control.MOUSE_FILTER_PASS
	# §0.6.8: bbcode [url=reward:N] affordances (strategic_ledger pattern)
	content_area.meta_clicked.connect(_on_meta_clicked)
	Utils.on_explanations_changed(_rerender_in_place)
	hide()


func _input(event):
	"""Handle number keys 1-N to scroll to specific marshal."""
	if not visible:
		return
	# Aug 30, 2026 review: `visible` is not the whole question. `Node._input`
	# runs BEFORE GUI input reaches a focused control, so with any of these
	# screens open — and they are all non-modal, the terminal stays live
	# behind them — every bare digit typed into the command line was eaten
	# here and `set_input_as_handled()` stopped it ever arriving. The player
	# typed "recruit 5000 infantry" and got "recruit  infantry" plus a tab
	# switch. A digit belongs to whoever has the caret.
	var _focused = get_viewport().gui_get_focus_owner()
	if _focused is LineEdit or _focused is TextEdit:
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
	# Session UI-3 (November 12, 2026): the books take the room (0.62 x 0.85).
	Utils.set_reading_share($PanelContainer, Utils.BOOK_SHARE, Utils.BOOK_MAX)
	Utils.clamp_centered_panel($PanelContainer)
	api_client.get_marshal_overview(_on_data_received)


func refresh_if_open():
	"""Re-fetch the overview after a reward command so the card reflects
	the new estate/rente state (§0.6.8 item 6)."""
	if visible and _api_client_ref:
		_api_client_ref.get_marshal_overview(_on_data_received)


func _rerender_in_place() -> void:
	"""Session UI-3: re-draw the current view from the cache, scroll kept."""
	if not visible or (cached_data.size() == 0 and not _commission_view):
		return
	var held: int = scroll_container.scroll_vertical
	_render_current_view()
	Utils.restore_scroll(scroll_container, held)


func refresh_pinned() -> void:
	"""UXR-D4 (Pre-Deploy S12b): the Side Desk re-reads a pinned screen
	after every command and every end turn — its current view (the cards or the commission), its scroll where the
	reader left it."""
	if not visible or _api_client_ref == null:
		return
	_api_client_ref.get_marshal_overview(_on_pinned_overview.bind(scroll_container.scroll_vertical))


func _on_pinned_overview(response, held_scroll: int) -> void:
	_on_data_received(response)
	Utils.restore_scroll(scroll_container, held_scroll)


func _on_meta_clicked(meta):
	# Session UI-3 (November 12, 2026): a lead-in's ⓘ opens in place, from the
	# cached overview, the scroll kept.
	if Utils.is_note_meta(meta):
		Utils.toggle_note(meta)
		_rerender_in_place()
		return
	var meta_str = str(meta)
	if meta_str.begins_with("reward:"):
		var index = int(meta_str.substr(7))
		if index >= 0 and index < cached_data.size():
			reward_requested.emit(cached_data[index])
	elif meta_str == "audience:open":
		audience_requested.emit()
	elif meta_str == "commission_open":
		_commission_view = true
		_render_current_view()
	elif meta_str == "commission_back":
		_commission_view = false
		_render_current_view()
	elif meta_str == "doctrine:toggle":
		# UXR3-24 / UXR3-80: the fold; the reader's place in the scroll stays.
		_doctrine_open = not _doctrine_open
		var held_scroll: int = scroll_container.scroll_vertical
		_render_current_view()
		Utils.restore_scroll(scroll_container, held_scroll)
	elif meta_str.begins_with("commission:"):
		var candidate = meta_str.substr(11)
		if candidate != "":
			commission_requested.emit(candidate)
	elif meta_str.begins_with("order:"):
		# UI-6: order chip — "order:<verb>:<MarshalName>" → "<Name>, <verb>",
		# the same string a player would type (marshal names carry no colons).
		var parts = meta_str.split(":")
		if parts.size() == 3 and str(parts[2]) != "":
			# S12 part 2 (R6): the terminal's echo lies under this screen —
			# the chip answers in place when main.gd took the order.
			Utils.order_taken = false
			order_command.emit(str(parts[2]) + ", " + str(parts[1]))
			if Utils.order_taken:
				Utils.mark_chip_sent(content_area, meta_str)


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
	# A11: the window comes from the backend constant (GLORY_WINDOW), never
	# a number typed here. The 8 below is only the fallback for an old
	# payload; the caption used to say 5, three turns adrift of the engine.
	cached_glory_window = int(response.get("glory_window", 8))
	cached_recruitment = response.get("recruitment", {})
	var _doctrine = response.get("doctrine")
	cached_doctrine = _doctrine if _doctrine is Dictionary else {}
	var _reigning = response.get("reigning")
	cached_reigning = _reigning if _reigning is Array else []
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
	# R159 (POSITION 7): each core screen names the mechanic it displays.
	# A11 (CA9 row 3): the previous caption urged the player to reward a
	# marshal pre-emptively, which was false twice — a grievance threshold
	# reads relationship, idle turns and authority and carries NO reward
	# term at all, and the [ Reward… ] chip is gated shut until he HAS
	# asked. It pointed the player at gold for a problem gold cannot
	# touch. (The old wording is deliberately not repeated here: the R159
	# pin is a source grep, and a comment quoting it would satisfy the
	# assertion while the screen said something else.)
	# Session UI-3 (November 12, 2026): the lead-in stands behind an ⓘ. This page
	# had no heading, so the folded page opens on one (THE GENERALS) to carry the
	# mark; On the page it is not drawn and the old line leads as before. The
	# per-card reward explainers below are exempt (the user's ruling).
	var bbcode = ""
	if Utils.explanations_folded():
		bbcode += "[color=#" + Utils.COLOR_HEADER + "]THE GENERALS[/color]" + Utils.lead_mark("Your marshals — loyalty, glory, and grievance. Gold answers loyalty; only glory answers envy. Esc closes it (Alt+G while you type).", "generals.lead") + "\n"
	bbcode += Utils.bb_lead("[color=#" + Utils.COLOR_INFO + "]Your marshals — loyalty, glory, and grievance. Gold answers loyalty; only glory answers envy. Esc closes it (Alt+G while you type).[/color]\n\n", "generals.lead")

	# UXR3-24 (Pre-Deploy S12 part 2): what asks for the Emperor's attention
	# leads the screen — a marshal captured or waiting on an audience is
	# listed first, his state in his header; then OUR DOCTRINE; then THE
	# EMPEROR, whose card opens on his own state; then THE LAURELS and the
	# rest of the roster.
	var apex_index := -1
	for i in range(cached_data.size()):
		if bool(cached_data[i].get("sovereign", false)):
			apex_index = i
			break
	var urgent: Array = []
	for i in range(cached_data.size()):
		if i == apex_index:
			continue
		var um: Dictionary = cached_data[i]
		if bool(um.get("captured", false)) or bool(um.get("seeks_audience", false)):
			urgent.append(i)
	for i in urgent:
		var um: Dictionary = cached_data[i]
		var state_head := "A PRISONER" if bool(um.get("captured", false)) else "SEEKS AN AUDIENCE"
		var state_color: String = Utils.COLOR_ERROR if bool(um.get("captured", false)) else Utils.COLOR_WARNING
		var state_words: String = state_head + " — " + str(um.get("name", "?"))
		var um_note = um.get("status_note", "")
		if bool(um.get("captured", false)) and um_note is String and um_note != "":
			state_words += ": " + Utils.humanize_nation_keys_in_text(um_note)
		# Session UI: the state line is the card's own heading — the card
		# opens above it (its hairline used to run through the words).
		bbcode += Utils.card_open(state_color)
		bbcode += "[color=#" + state_color + "]" + state_words + "[/color]\n"
		bbcode += _render_card(um, i, true)
		bbcode += "[color=#" + Utils.COLOR_INFO + "]────────────────────────────────────────[/color]\n\n"

	bbcode += _render_doctrine()

	# NP-3 (NAPOLEON_SPEC §6.5): the sovereign renders ABOVE the ladder as
	# a fixed apex block — THE EMPEROR header, his character sheet, no
	# glory bar, no rank, no envy arrow. The ladder itself never contains
	# him (the backend excludes him at get_nation_ladder).
	if apex_index >= 0:
		bbcode += Utils.card_open()    # Session UI: THE EMPEROR heads his card
		bbcode += _icon(_ICON_PHOSPHOR + "crown.svg", 20, Utils.COLOR_GOLD)
		bbcode += " [color=#" + Utils.COLOR_GOLD + "]THE EMPEROR[/color]\n"
		bbcode += _render_card(cached_data[apex_index], apex_index, true)
		bbcode += "[color=#" + Utils.COLOR_INFO + "]════════════════════════════════════════[/color]\n\n"

	bbcode += _render_glory_ladder()
	bbcode += _render_reigning()

	for i in range(cached_data.size()):
		if i == apex_index or i in urgent:
			continue
		var m = cached_data[i]
		bbcode += _render_card(m, i)
		if i < cached_data.size() - 1:
			bbcode += "[color=#" + Utils.COLOR_INFO + "]────────────────────────────────────────[/color]\n\n"

	content_area.text = Utils.dress_heads(bbcode)


func _render_doctrine() -> String:
	"""OUR DOCTRINE — above the Emperor and the roster since UXR3-24; folded
	to its one title line behind "▸ the doctrine" since S15's head."""
	var bbcode = ""
	# SR-7d DC-3a (DOCTRINES_SPEC §4a): OUR DOCTRINE — name, says, strength
	# and flaw with their applied numbers, the cure's status. Backend-composed
	# lines (R7); an empty payload omits the block (a world with no doctrines).
	if cached_doctrine is Dictionary and not cached_doctrine.is_empty():
		var d_strength = cached_doctrine.get("strength", {})
		var d_flaw = cached_doctrine.get("flaw", {})
		bbcode += Utils.bb_glyph("medal", 20, Utils.COLOR_GOLD)
		bbcode += " [color=#" + Utils.COLOR_GOLD + "]OUR DOCTRINE — " + str(cached_doctrine.get("name", "")) + "[/color]"
		# UXR3-24 / UXR3-80 (S15 head, October 25, 2026): the title line is all
		# the block is until the player opens it — the Emperor's card (or the
		# first marshal's sheet, where no Emperor serves) leads the screenful.
		bbcode += "  [url=doctrine:toggle][color=#" + Utils.COLOR_GOLD + "]" \
			+ ("▾ hide the doctrine" if _doctrine_open else "▸ the doctrine") + "[/color][/url]\n"
		if not _doctrine_open:
			return bbcode + "\n"
		var d_says = str(cached_doctrine.get("says", ""))
		if d_says != "":
			bbcode += "  [color=#" + Utils.COLOR_INFO + "]\"" + d_says + "\"[/color]\n"
		if d_strength is Dictionary:
			bbcode += "  [color=#" + Utils.COLOR_SUCCESS + "]Strength — " + str(d_strength.get("name", "")) + ":[/color] " + str(d_strength.get("line", "")) + "\n"
		if d_flaw is Dictionary:
			var flaw_color = Utils.COLOR_INFO if bool(d_flaw.get("cured", false)) else Utils.COLOR_WARNING
			bbcode += "  [color=#" + flaw_color + "]Flaw — " + str(d_flaw.get("name", "")) + ":[/color] " + str(d_flaw.get("line", "")) \
				+ "  [color=#" + Utils.COLOR_INFO + "](" + str(d_flaw.get("status_line", "")) + ")[/color]\n"
		bbcode += "\n"
	return bbcode


func _render_reigning() -> String:
	"""G2: REIGNING — the marshals and princes the Emperor has crowned, where
	each reigns and with what, and how he stands (a client's king, or in arms
	against France after his kingdom broke away). Backend-composed lines
	(`crowns.reigning_rows`); nothing here is commandable."""
	if cached_reigning.is_empty():
		return ""
	var bbcode = _icon(_ICON_PHOSPHOR + "crown.svg", 18, Utils.COLOR_GOLD)
	bbcode += " [color=#" + Utils.COLOR_GOLD + "]REIGNING — the crowns you have given[/color]
"
	for row in cached_reigning:
		if not (row is Dictionary):
			continue
		var line: String = Utils.humanize_nation_keys_in_text(str(row.get("line", "")))
		if line == "":
			continue
		var color: String = Utils.COLOR_INFO
		if str(row.get("state", "")) == "in_arms":
			color = Utils.COLOR_ERROR
		elif str(row.get("state", "")) == "fallen":
			color = Utils.COLOR_WARNING
		bbcode += "  [color=#" + color + "]" + line + "[/color]
"
	bbcode += "[color=#" + Utils.COLOR_INFO + "]──────────────────────────────────────────[/color]
"
	return bbcode


func _render_glory_ladder() -> String:
	"""Jealousy v3.2: THE LAURELS OF THE ARMY — the nation's glory ladder
	(rank, ★ crown, 10-wide glory bar, live grievance arrows) plus the
	Commission affordance when a candidate bench exists."""
	var bbcode = ""
	var candidates = cached_recruitment.get("candidates", [])
	var has_bench = candidates is Array and candidates.size() > 0

	var any_glory := false
	if cached_ladder is Array:
		for lrow in cached_ladder:
			if lrow is Dictionary and (int(lrow.get("glory", 0)) > 0 or bool(lrow.get("crowned", false))):
				any_glory = true
				break
	if cached_ladder is Array and cached_ladder.size() > 1 and not any_glory:
		# UXR3-24: a ladder of zeros said nothing in seven rows and pushed the
		# roster below the fold — one line says it.
		bbcode += Utils.bb_glyph("medal", 20, Utils.COLOR_GOLD)
		bbcode += " [color=#" + Utils.COLOR_GOLD + "]THE LAURELS OF THE ARMY[/color]  [color=#" \
			+ Utils.COLOR_INFO + "]no glory won in the last " + str(cached_glory_window) + " turns — no marshal envies another[/color]\n\n"
	elif cached_ladder is Array and cached_ladder.size() > 1:
		bbcode += Utils.bb_glyph("medal", 20, Utils.COLOR_GOLD)
		bbcode += " [color=#" + Utils.COLOR_GOLD + "]THE LAURELS OF THE ARMY[/color]"
		# A11: the window is INTERPOLATED from the backend constant, and the
		# rule is stated as the engine actually implements it — envy fixes
		# on a REMEMBERED rival (JEALOUSY_RIVAL_MEMORY), not on whoever
		# happens to stand one rung up this turn.
		bbcode += "  [color=#" + Utils.COLOR_INFO + "](glory, last " + str(cached_glory_window) + " turns — a marshal envies the man above him, and keeps that rival while he stays above)[/color]\n"
		for i in range(cached_ladder.size()):
			var row = cached_ladder[i]
			var rname = str(row.get("name", "?"))
			var glory = int(row.get("glory", 0))
			var crowned = bool(row.get("crowned", false))
			var envies = str(row.get("jealous_of", "")) if row.get("jealous_of") != null else ""
			var filled = clampi(glory, 0, 10)
			var bar_color = Utils.COLOR_GOLD if crowned else Utils.COLOR_INFO
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
		bbcode += _button_chip("commission_open", "Commission a Marshal…", CHIP_GILT_INK, CHIP_GILT_BG, _ICON_PHOSPHOR + "crown.svg")
		bbcode += "  [color=#" + Utils.COLOR_INFO + "]" + str(candidates.size()) + " await the Emperor's call[/color]\n\n"

	# Session UI-5 interim fix (Nov 13): no closing hairline here - the first card
	# opens with its own rule; the short stray one stood alone under the Commission row.
	return bbcode


func _render_commission_view():
	"""Marshal Recruitment: the candidate bench — full character sheets,
	honest availability (the executor's own check), price/corps chips."""
	var bbcode = _button_chip("commission_back", "← Back to the Marshalate", "a9c7e6", Utils.COLOR_CHIP_BG_NAVY) + "\n\n"
	bbcode += _icon(_ICON_PHOSPHOR + "crown.svg", 20, Utils.COLOR_GOLD)
	bbcode += " [color=#" + Utils.COLOR_GOLD + "]COMMISSION A MARSHAL[/color]\n"
	var treasury = int(cached_recruitment.get("treasury", 0))
	# CN-3 rider 2: every arm's pool, not the infantry pool alone — a
	# commission raises the candidate's corps from HIS arm's pool (the
	# payload's per-candidate `arm` and `corps`), so the old header promised
	# France's two gun marshals a 5,000-man corps from a pool they never draw.
	var pools = cached_recruitment.get("pools", {})
	if not (pools is Dictionary):
		pools = {}
	var inf_pool = int(pools.get("infantry", cached_recruitment.get("infantry_pool", 0)))
	bbcode += Utils.bb_glyph("gold", 16, Utils.COLOR_GOLD) + " [color=#" + Utils.COLOR_INFO + "]Treasury: " + _format_number(treasury) + "g | Pools: " + _format_number(inf_pool) + " foot · " + _format_number(int(pools.get("cavalry", 0))) + " horse · " + _format_number(int(pools.get("artillery", 0))) + " guns"
	bbcode += " | A commission raises his corps at the capital from his own arm's pool (1 admin AP + the candidate's price).[/color]\n\n"

	var candidates = cached_recruitment.get("candidates", [])
	if not (candidates is Array) or candidates.size() == 0:
		bbcode += "[color=#" + Utils.COLOR_INFO + "]The bench is empty — every marshal France could call already serves.[/color]"
		content_area.text = Utils.dress_heads(bbcode)
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
		bbcode += "  " + Utils.bb_badge(personality.capitalize(), Utils.COLOR_BADGE_QUIET)
		# CN-3 rider 2: every arm is tagged, the serving card's own idiom —
		# the bench tagged only [Cavalry], so Marmont and Senarmont, the gun
		# marshals, rendered untagged. The corps he raises rides beside it.
		var c_arm = str(c.get("arm", "infantry"))
		var arm_label = c_arm.capitalize()
		var arm_color = Utils.COLOR_INFO
		if c_arm == "cavalry":
			arm_color = Utils.COLOR_ORANGE
		elif c_arm == "artillery":
			arm_color = Utils.COLOR_ERROR
		# (the bench keeps its bracketed arm tag: the CN-3 census counts them)
		if c_arm != "infantry":
			bbcode += "  " + _unit_icon(arm_label, arm_color) + " [color=#" + arm_color + "][" + arm_label + "][/color]"
		else:
			bbcode += "  [color=#" + arm_color + "][" + arm_label + "][/color]"
		bbcode += " [color=#" + Utils.COLOR_INFO + "]a corps of " + _format_number(int(c.get("corps", 0))) + " " + str(_BENCH_ARM_NOUN.get(c_arm, "men")) + "[/color]"
		bbcode += "  [color=#" + Utils.COLOR_GOLD + "]" + _format_number(cost) + "g[/color]\n"
		var bio = str(c.get("biography", ""))
		if bio != "":
			bbcode += "[color=#" + Utils.COLOR_INFO + "]" + bio + "[/color]\n"
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
			bbcode += "  [color=#" + Utils.COLOR_INFO + "]Arrives with a history —[/color] " + ", ".join(seed_parts) + "\n"
		if available:
			bbcode += "  " + _button_chip("commission:" + cname, "Commission " + cname + " — " + _format_number(cost) + "g", "b6e6b6", Utils.COLOR_CHIP_BG_GREEN) + "\n"
		else:
			bbcode += "  [color=#" + Utils.COLOR_ERROR + "]Unavailable: " + reason + "[/color]\n"
		bbcode += "\n[color=#" + Utils.COLOR_INFO + "]────────────────────────────────────────[/color]\n\n"

	content_area.text = Utils.dress_heads(bbcode)


func _skills_block(m: Dictionary) -> String:
	"""The character sheet's skill bars and their notes — ONE block for the
	marshals' cards and the sovereign's (UXR3-82: his rides under his strength,
	above his prose). Skills — MC-2 character sheet: one bar row per wired
	skill (█░ bar idiom matches the diplomatic ledger's threat/WE bars).
	Values, hints, and the Rally/Intendance notes all ship from the backend
	(shown = applied — Godot renders, never recomputes thresholds). MC-2b
	(July 11, 2026): administration is wired (The Intendance, recruit
	pricing). The backend omits the key where the mechanic is not live
	(legacy rollback world), so absent keys are skipped, never defaulted."""
	var bbcode := ""
	var skills = m.get("skills", {})
	var skill_notes = m.get("skill_notes", {})
	# Session UI-4 (November 12, 2026): the bars stand under a "Skills" caption
	# (the readers: "separate the stats, abilities and orders into distinct
	# tidy blocks").
	for skill_name in ["tactical", "shock", "defense", "logistics", "administration", "command"]:
		if skills.has(skill_name):
			bbcode += _caption("Skills")
			break
	for skill_name in ["tactical", "shock", "defense", "logistics", "administration", "command"]:
		if not skills.has(skill_name):
			continue
		var val = int(skills.get(skill_name, 5))
		var note = str(skill_notes.get(skill_name, ""))
		bbcode += "  " + _skill_bar_row(skill_name.capitalize(), val, note)
	var admin_note = str(m.get("admin_note", ""))
	if admin_note != "":
		var admin_color = Utils.COLOR_SUCCESS if str(m.get("admin_tier", "")) == "thrifty" else Utils.COLOR_ORANGE
		bbcode += "  " + _prose("gen.admin." + str(m.get("name", "")), admin_note, admin_color)
	var rally_note = str(m.get("rally_note", ""))
	if rally_note != "":
		var rally_color = Utils.COLOR_SUCCESS if str(m.get("rally_tier", "")) == "fast" else Utils.COLOR_ORANGE
		bbcode += "  " + _prose("gen.rally." + str(m.get("name", "")), rally_note, rally_color)
	return bbcode


func _render_card(m: Dictionary, index: int, opened := false) -> String:
	"""Render a single marshal card. `opened`: the caller opened the card
	above a heading of its own (the Emperor's, a prisoner's, a petitioner's)."""
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
	# Session UI: the card opens here (its portrait is its first line — the
	# underlay rings it) in the marshal's own tone: a prisoner's crimson, a
	# petitioner's amber, the gilt for every other.
	var card_tone: String = Utils.COLOR_GOLD
	if bool(m.get("captured", false)):
		card_tone = Utils.COLOR_ERROR
	elif bool(m.get("seeks_audience", false)):
		card_tone = Utils.COLOR_WARNING
	if not opened:
		bbcode += Utils.card_open(card_tone)
	# Session UI-2 (November 11, 2026): the portrait stands in a gilt-ruled
	# cell BESIDE the sheet — the name in the title face, the arm and the
	# nation, and (below) the prose — instead of alone on a line over an empty
	# band (the readers' "portrait floats with a wasted gap").
	# Session UI-4 (November 12, 2026): a larger portrait (112 x 140, was 80 x
	# 100) so its column is not an empty band beside the sheet; the 800 x 450
	# view keeps the old size.
	var portrait := (_portrait_block(name) if Utils.compact_view() else _portrait_block(name, 112, 140)).strip_edges()
	var sheet := ""
	sheet += "[color=#" + Utils.COLOR_INFO + "]" + key_hint + "[/color]"
	sheet += Utils.HEAD_OPEN + name + Utils.HEAD_CLOSE
	# Cavalry/Artillery keep their (clear) icon; Infantry is label-only — the
	# game-icons infantry glyph reads as an ambiguous caret at 18px (UI-3 tune).
	# Session UI-2 (K): the arm and the nation are badges in the sheet's head —
	# the arm in its tone, the nation under its flag.
	var arm_tone := "3a4a6b"
	match unit_type:
		"Cavalry":
			arm_tone = "8a5a1a"
		"Artillery":
			arm_tone = Utils.cv_hex("8b2a2a")
	sheet += "  "
	if unit_type != "Infantry":
		sheet += _unit_icon(unit_type, type_color) + " "
	# the sheet is a table cell (bb_portrait_row): its tags are inline runs
	sheet += Utils.bb_tag(unit_type, arm_tone)
	sheet += "  " + Utils.bb_flag(nation) + " " + Utils.bb_tag(Utils.display_nation_name(nation), Utils.COLOR_BADGE_QUIET) + "\n"

	# UXR3-24: the Emperor's card opens on his STATE (the backend's line: in
	# the field, at the Seat, a captive), then The Presence as it applies and
	# his strength — the live facts above his biography.
	var is_sovereign := bool(m.get("sovereign", false))
	if is_sovereign:
		var state_line := str(m.get("sovereign_state_line", ""))
		if state_line != "":
			var state_color: String = Utils.COLOR_ERROR if bool(m.get("captured", false)) else Utils.COLOR_GOLD
			sheet += "[color=#" + state_color + "]" + Utils.humanize_nation_keys_in_text(state_line) + "[/color]\n"
		sheet += _ability_line(m).strip_edges() + "\n"
		sheet += _strength_line(m)
		# UXR3-82 (S15, October 26, 2026 — the walk's ✗ on the boot board): his
		# skill bars ride under his strength, ABOVE his two prose paragraphs —
		# the sheet before the biography, as on every marshal's card.
		sheet += _skills_block(m)

	# ═══════ TRUST, VINDICATION, RECORD, GLORY — the sheet's figures ═══════
	# Session UI-2 (K): figures before prose — trust and glory are labelled
	# meters with the figure beside, in the sheet's head.
	var trust_val = int(m.get("trust_value", 70))
	var trust_label = str(m.get("trust_label", "Neutral"))
	var vindication = int(m.get("vindication_score", 0))
	var won = int(m.get("battles_won", 0))
	var lost = int(m.get("battles_lost", 0))
	var overridden = int(m.get("orders_overridden", 0))
	sheet += "Trust: " + Utils.bb_meter(trust_val, 100, 110, 8, _trust_hex(trust_val)) + " " + _trust_colored(trust_val, trust_label) + "\n"
	sheet += "Vindication: " + _vindication_colored(vindication)
	sheet += "  Record: " + str(won) + "W/" + str(lost) + "L"
	if overridden > 0:
		sheet += "  [color=#" + Utils.COLOR_ORANGE + "]Overridden: " + str(overridden) + "x[/color]"
	sheet += "\n"

	# ═══════ JEALOUSY v3.2: GLORY (shown = applied) ═══════
	var glory = int(m.get("glory", 0))
	var glory_rank = int(m.get("glory_rank", 0))
	var glory_roster = int(m.get("glory_roster", 0))
	if glory > 0 or glory_rank > 0:
		var glory_hex: String = Utils.COLOR_GOLD if glory > 0 else Utils.COLOR_INFO
		sheet += "Glory: " + Utils.bb_meter(glory, 10, 110, 8, glory_hex) + " [color=#" + glory_hex + "]" + str(glory) + "[/color]"
		if glory_rank > 0 and glory_roster > 1:
			sheet += "  [color=#" + Utils.COLOR_INFO + "](rank " + str(glory_rank) + " of " + str(glory_roster) + " on the ladder)[/color]"
		if m.get("glory_crowned", false):
			sheet += "  [color=#" + COLOR_DEVOTED + "]★ CROWNED WITH GLORY (+1 shock/defense/administration)[/color]"
		sheet += "\n"

	# Session UI-5 interim fix (Nov 13): a marshal's strength / morale / range line
	# rides the sheet beside the portrait (the column is no longer shorter than it).
	if not is_sovereign:
		sheet += _strength_line(m).strip_edges(true, false)

	# ═══════ BIOGRAPHY ═══════
	# The lore stands under the figures as notes, dimmer (the card's last
	# block, `notes`), not beside the portrait.
	var notes := ""
	var bio = str(m.get("biography", ""))
	if bio != "":
		notes += _prose("gen.bio." + name, bio, Utils.COLOR_INFO)

	# ═══════ PERSONALITY & UNIT TYPE ═══════
	var pers_desc = str(m.get("personality_description", ""))
	if pers_desc != "":
		notes += _prose("gen.pers." + name, pers_desc, Utils.COLOR_INFO)
	var type_desc = str(m.get("unit_type_description", ""))
	if type_desc != "":
		notes += _prose("gen.type." + name, type_desc, Utils.COLOR_INFO)
	bbcode += Utils.bb_portrait_row(portrait, sheet, card_tone) + "\n"

	# ═══════ COMBAT STATS ═══════
	# (UI-5 interim fix: no blank line under the sheet; strength rides the sheet)
	if not is_sovereign:
		bbcode += _skills_block(m)

	# ═══════ ABILITY (only shown if active/wired) ═══════
	if not is_sovereign:
		bbcode += _ability_line(m)

	# ═══════ GRIEVANCES (the trust and glory figures ride the sheet's head) ═══════
	var jealous_of = str(m.get("jealous_of", "")) if m.get("jealous_of") != null else ""
	if jealous_of != "":
		var jl_turns = int(m.get("jealousy_turns_remaining", 0))
		var grievance: String = "  [color=#" + Utils.COLOR_ERROR + "]GRIEVANCE: envious of " + jealous_of
		if jl_turns > 0:
			grievance += " (" + str(jl_turns) + " turn" + ("s" if jl_turns != 1 else "") + " unless satisfied)"
		grievance += "[/color]"
		if m.get("jealousy_warned", false):
			# Session UI-4: the warning's long tail opens from the grievance line
			bbcode += Utils.bb_note("gen.grievance." + name, grievance,
				"[color=#" + Utils.COLOR_ERROR + "] — HE EYES THE ENEMY ON HIS OWN; any order restrains him[/color]", "\n")
		else:
			bbcode += grievance + "\n"
	if m.get("jealousy_surge", false):
		bbcode += "  [color=#" + Utils.COLOR_SUCCESS + "]VINDICATED — he fights with renewed purpose this turn[/color]\n"
	var feuds = m.get("feuds", [])
	if feuds is Array and feuds.size() > 0:
		bbcode += "  [color=#" + Utils.COLOR_ORANGE + "]Entrenched feud: " + ", ".join(feuds) + "[/color]\n"
	var separations = m.get("separations", [])
	if separations is Array and separations.size() > 0:
		bbcode += "  [color=#" + Utils.COLOR_INFO + "]Kept apart from: " + ", ".join(separations) + " (Berthier watches)[/color]\n"
	# PC15-10 B1: he waits in the antechamber — his petition is no modal;
	# the chip opens it (the same dialog, the same answer).
	if m.get("seeks_audience", false):
		bbcode += "  " + _button_chip("audience:open", "Hear him — he seeks an audience", CHIP_GILT_INK, CHIP_GILT_BG, _ICON_PHOSPHOR + "scales.svg") + "\n"

	# ═══════ ES-7 ESTATES & EXPECTATION (Economy Revisit S7 + §0.6.8) ═══════
	# Expectation vs estate income vs rente in the same g/turn units — the
	# number IS the explanation (green met / amber unmet / red eroding).
	var expectation = int(m.get("expectation", 0))
	var estate_income = int(m.get("estate_income", 0))
	var pension = int(m.get("pension", 0))
	var shortfall = int(m.get("expectation_shortfall", 0))
	var estate_title = str(m.get("estate_title", ""))
	var is_dotation = bool(m.get("is_dotation_world", false))
	# NP-3 (NAPOLEON_SPEC §6.5): the sovereign is never rewarded — the
	# chip renders his stated refusal, never options ("The Empire is his
	# estate."). Branch FIRST so the fresh-marshal line below can never
	# promise the Emperor an expectation.
	if bool(m.get("sovereign", false)):
		if is_dotation:
			var sov_why := str(m.get("sovereign_note", "The Empire is his estate."))
			bbcode += "  " + Utils.bb_chip_disabled("Reward…", _ICON_GAME + "estate-domaine.svg", sov_why) \
				+ "  [color=#" + Utils.COLOR_INFO + "]" + sov_why + "[/color]\n"
	elif expectation > 0 or estate_income > 0 or pension > 0:
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
			bbcode += "  " + _prose("gen.steward." + name, steward_note, steward_color)
		# §0.6.8 item 6, re-surfaced Aug 8, 2026 (user: "I don't see a button to
		# reward marshals"): the Reward affordance is a real CHIP in the fixed
		# spot on every card — enabled when there is something to grant or
		# revoke, otherwise DISABLED with its gate reason stated (the UI-6
		# honest-availability idiom). The ES-7 reactive gate itself is design
		# and unchanged: no proactive endow, and never for a PRISONER (the
		# executors refuse him; review fix).
		if m.get("captured", false):
			bbcode += "  " + Utils.bb_chip_disabled("Reward…", _ICON_GAME + "estate-domaine.svg") \
				+ "  [color=#" + Utils.COLOR_INFO + "]held prisoner — his rewards await his release[/color]\n"
		elif shortfall > 0 or pension > 0:
			bbcode += "  " + _button_chip("reward:" + str(index), "Reward — estate or rente…", CHIP_GILT_INK, CHIP_GILT_BG, _ICON_GAME + "estate-domaine.svg")
			var eligible = m.get("eligible_estates", [])
			if shortfall > 0 and eligible is Array and eligible.size() > 0:
				var m_name_hint = str(m.get("name", "?"))
				bbcode += "  [color=#" + Utils.COLOR_INFO + "]or type: 'endow " + m_name_hint + " with " + str(eligible[0]) + "'[/color]"
			bbcode += "\n"
		else:
			bbcode += "  " + Utils.bb_chip_disabled("Reward…", _ICON_GAME + "estate-domaine.svg") \
				+ "  [color=#" + Utils.COLOR_INFO + "]his expectation is met — new victories raise it[/color]\n"
	elif is_dotation and not m.get("captured", false):
		# Fresh marshal, no expectation yet. The reward portfolio is REACTIVE
		# by design (ES-7 "cost of success"): there is nothing to grant until
		# he EARNS an expectation by winning battles. The chip sits in its
		# fixed place, locked, and says exactly what unlocks it.
		bbcode += "  " + Utils.bb_chip_disabled("Reward…", _ICON_GAME + "estate-domaine.svg") \
			+ "  [color=#" + Utils.COLOR_INFO + "]victories raise his expectation — then endow a conquered province (a Duchy) or grant a rente (gold/turn)[/color]\n"

	# ═══════ CURRENT STATUS ═══════
	# IQ-2 (Sept 14, 2026): W6-7 put a prisoner's fate on the card payload —
	# "PRISONER of Austria since T37." — and no line of this renderer read it,
	# so the card of a marshal in an enemy cell (the Emperor's, in the played
	# collapse campaigns) showed Location/Stance as if he stood in the field.
	bbcode += _caption("Status")
	var status_note = m.get("status_note", "")
	if (PRISONER_NOTE_ON_THE_CARD and m.get("captured", false)
			and status_note is String and status_note != ""):
		bbcode += "  [color=#" + Utils.COLOR_ERROR + "]" + Utils.humanize_nation_keys_in_text(status_note) + "[/color]\n"
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
	# VP-M1 "The Fortunes of War" (GE-V, Sept 25 2026): the wound and the turn
	# it heals — the backend's own field (shown = applied; the executor refuses
	# his attack until then, the corps stands and marches).
	if m.get("is_wounded", false):
		flags.append("[color=#" + Utils.COLOR_ERROR + "]WOUNDED (until turn " + str(int(m.get("wounded_until_turn", 0))) + ")[/color]")
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
		flags.append("[color=#" + Utils.COLOR_INFO + "]IDLE " + str(idle) + " turns[/color]")

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
	# Session UI-4 (November 12, 2026): ONE row under an "Orders" caption (the
	# readers' "the action buttons are small and cramped", "disabled chips hard
	# to tell from the live ones"): every order of the card - Fortify, Drill,
	# Hold, Fall back, Garrison - in one list, two no-break spaces between the
	# chips; a locked one is `bb_chip_disabled` (lock glyph, dim ink) and its
	# reason is its hover when explanations are folded, a stated line under the
	# row On the page.
	var order_chips = []
	var locked_notes: Array = []
	# Only for a marshal who can act — the executor still owns every gate
	# (AP, objections, terrain); a refused chip reports like a typed refusal.
	if (not m.get("captured", false) and not m.get("is_broken", false)
			and not m.get("is_retreating", false)):
		var chip_name = str(m.get("name", ""))
		if chip_name != "":
			# CRT-9 (Oct 3, 2026): the card's `order_refusals` — the one
			# state probe the region panel and the completer read too (the
			# turn's actions first, then his state, then each verb's own
			# gate). CQ-21: at zero actions every chip here was offered and
			# refused. A refused chip is dimmed beside the probe's reason.
			var refusals = m.get("order_refusals", {})
			if not (refusals is Dictionary):
				refusals = {}
			# CN-4: Fortify is offered only where the works would begin (the
			# card's `fortify_refusal`), else dimmed beside the reason.
			var fortify_why = str(refusals.get("fortify", m.get("fortify_refusal", "")))
			if m.get("is_fortified", false):
				var unfortify_why = str(refusals.get("unfortify", ""))
				if unfortify_why == "":
					order_chips.append(Utils.bb_button_chip("order:unfortify:" + chip_name, "Unfortify", Utils.COLOR_COMMAND, "233043"))
				else:
					order_chips.append(_locked_chip("Unfortify", unfortify_why, locked_notes))
			elif fortify_why == "":
				# S14G-X170 (Pre-Deploy S14h part 2, October 26, 2026): the Generals card's
				# Fortify chip priced nothing while the region panel's names the price a
				# NEUTRAL corps pays - the same payload figure (`order_prices.fortify`, the
				# executor's own `insist_terms`), the same convention (priced above 0).
				var fortify_label := "Fortify"
				var fortify_prices = m.get("order_prices", {})
				if fortify_prices is Dictionary and int(fortify_prices.get("fortify", 0)) > 0:
					fortify_label += " (" + str(int(fortify_prices.get("fortify", 0))) + " AP)"
				order_chips.append(Utils.bb_button_chip("order:fortify:" + chip_name, fortify_label, Utils.COLOR_COMMAND, "233043"))
			else:
				# the dimmed chip keeps its bare label (the CN-4 census); the reason is
				# its hover Folded, the stated line under the row On the page
				order_chips.append(Utils.bb_chip_disabled("Fortify") if not Utils.explanations_folded() else Utils.bb_chip_disabled("Fortify", "", fortify_why))
				locked_notes.append(["Fortify", fortify_why])
			# CN-4: Drill is offered only where the drill would begin;
			# otherwise it is dimmed beside the executor's own reason (the
			# card's `drill_refusal`, `tactical_executor.drill_refusal`) —
			# at the 1805 boot every corps stood one province from Mack and
			# every Drill chip was refused.
			var drill_why = str(refusals.get("drill", m.get("drill_refusal", "")))
			if not m.get("is_drilling", false):
				if drill_why == "":
					order_chips.append(Utils.bb_button_chip("order:drill:" + chip_name, "Drill", Utils.COLOR_COMMAND, "233043"))
				else:
					order_chips.append(_locked_chip("Drill", drill_why, locked_notes))
	# CF-6 sibling (October 17, 2026): the card offers the province panel's
	# Hold · Fall back · Garrison too — lit where the card's `order_refusals`
	# carries no reason, dimmed beside the reason otherwise, priced from its
	# `order_prices`. Rendered for a recovering or broken corps as well: the
	# probe names his state as the reason, and the free Fall back is the one
	# order a corps recovering beside the enemy still has.
	if not m.get("captured", false) and str(m.get("name", "")) != "":
		var state_refusals = m.get("order_refusals", {})
		if not (state_refusals is Dictionary):
			state_refusals = {}
		var prices = m.get("order_prices", {})
		if not (prices is Dictionary):
			prices = {}
		for spec in [["hold", "Hold"], ["retreat", "Fall back"], ["garrison", "Garrison"]]:
			var verb := str(spec[0])
			var label := str(spec[1])
			var ap := int(prices.get(verb, 0))
			if ap > 0:
				label += " (" + str(ap) + " AP)"
			var why := str(state_refusals.get(verb, ""))
			if why == "":
				order_chips.append(Utils.bb_button_chip("order:" + verb + ":" + str(m.get("name", "")), label, Utils.COLOR_COMMAND, "233043"))
			else:
				order_chips.append(_locked_chip(label, why, locked_notes))
	if order_chips.size() > 0:
		bbcode += _caption("Orders")
		# regular spaces at 800 x 450 (a no-break run could overflow the window)
		var chip_gap := "  " if Utils.compact_view() else "\u00A0\u00A0"
		bbcode += "  " + chip_gap.join(PackedStringArray(order_chips)) + "\n"
		if not Utils.explanations_folded():
			for note in locked_notes:
				bbcode += "  [color=#" + Utils.COLOR_INFO + "]" + str(note[0]) + " — " + str(note[1]) + "[/color]\n"

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

	# Session UI-2 (K): the lore, under the figures, as notes.
	if notes != "":
		bbcode += "\n" + _caption("Character") + notes

	# Session UI: the card closes on its last line (the mark heads the blank
	# line under it).
	bbcode += Utils.CARD_CLOSE
	bbcode += "\n"
	return bbcode


# =============================================================================
# COLOR HELPERS
# =============================================================================

# =============================================================================
# UI-3 PORTRAIT / ICON HELPERS
# =============================================================================

func _caption(text: String) -> String:
	"""Session UI-4 (November 12, 2026): a block's small-caps caption (Skills,
	Status, Orders, Character) - the card in captioned blocks, one grid."""
	return "  [color=#" + Utils.COLOR_INFO + "][opentype_features=smcp]" + text + "[/opentype_features][/color]\n"


func _prose(id: String, text: String, hex: String, tail: String = "\n") -> String:
	"""Long card prose opens from its first sentence ("▸ more", `Utils.bb_note`)
	when folded; On the page every word prints as it did. A one-sentence or
	short passage is not folded."""
	var cut: int = Utils.first_sentence_end(text) if text.length() > 90 else -1
	if cut < 0:
		return "[color=#" + hex + "]" + text + "[/color]" + tail
	return Utils.bb_note(id, "[color=#" + hex + "]" + text.substr(0, cut) + "[/color]",
		"[color=#" + hex + "]" + text.substr(cut) + "[/color]", tail)


func _locked_chip(label: String, why: String, locked_notes: Array) -> String:
	"""A locked order: `bb_chip_disabled`, the reason its hover when folded; the
	reason is also kept for the stated line under the row On the page."""
	locked_notes.append([label, why])
	return Utils.bb_chip_disabled(label, "", why if Utils.explanations_folded() else "")


func _strength_line(m: Dictionary) -> String:
	"""Strength (coloured by losses), morale and range — one line."""
	var strength = int(m.get("strength", 0))
	var starting = int(m.get("starting_strength", 0))
	var morale = int(m.get("morale", 100))
	var move_range = int(m.get("movement_range", 1))
	var str_color = Utils.COLOR_INFO
	if starting > 0:
		var ratio = float(strength) / float(starting)
		if ratio < 0.3:
			str_color = Utils.COLOR_ERROR
		elif ratio < 0.6:
			str_color = Utils.COLOR_ORANGE
	var line: String = "  Strength: [color=#" + str_color + "]" + _format_number(strength) + "[/color]"
	line += " / " + _format_number(starting)
	line += "  Morale: " + _morale_colored(morale)
	line += "  Range: " + str(move_range) + "\n"
	return line


func _ability_line(m: Dictionary) -> String:
	"""The signature ability, only when wired and active (its effect as the
	backend states it — shown = applied)."""
	var ab_name = str(m.get("ability_name", ""))
	var ab_effect = str(m.get("ability_effect", ""))
	if not m.get("ability_active", false) or ab_name == "":
		return ""
	# UXR3-24 / UXR3-80 (S15 head, October 25, 2026): the Emperor's Presence
	# states the figure AS APPLIED where he stands — "+10% here at Bohemia" —
	# and its star dims with it (the backend's own "his star dims", drawn).
	if bool(m.get("sovereign", false)):
		var presence := _presence_applied_line(m, ab_name, ab_effect)
		if presence != "":
			return presence
	var line: String = "  [color=#" + Utils.COLOR_GOLD + "]" + ab_name + "[/color]"
	if ab_effect != "":
		line += "  " + _prose("gen.ability." + str(m.get("name", "")), ab_effect, Utils.COLOR_INFO, "")
	return line + "\n\n"


func _presence_applied_line(m: Dictionary, ab_name: String, ab_effect: String) -> String:
	"""UXR3-24 / UXR3-80: The Presence as APPLIED where the Emperor stands.
	The backend's `ability_effect` carries the authored figure ("+10% attack
	and defense") and, when the aura has decayed with the Empire's grip,
	"Today it stands at +N% — his star dims" (marshal_overview
	`_build_ability`, NPC-D1). This reads those two figures — never
	recomputes them — and draws the line as "★ The Presence  +10% here at
	Bohemia": the star is gold at the full figure and dims toward the grey
	ink as the applied figure falls, out at +0%. "" when the effect carries
	no figure (the caller keeps the plain line)."""
	var re_any := RegEx.new()
	re_any.compile("\\+(\\d+)%")
	var first := re_any.search(ab_effect)
	if first == null:
		return ""
	var full_pct := int(first.get_string(1))
	var applied_pct := full_pct
	var re_now := RegEx.new()
	re_now.compile("Today it stands at \\+(\\d+)%")
	var now := re_now.search(ab_effect)
	if now != null:
		applied_pct = int(now.get_string(1))
	var held_at := str(m.get("location", ""))
	var here := " here at " + held_at if held_at != "" else " here"
	var lit := 1.0 if full_pct <= 0 else clampf(float(applied_pct) / float(full_pct), 0.0, 1.0)
	var star_hex: String = Color.html("#" + Utils.COLOR_GOLD).lerp(Color.html("#" + Utils.COLOR_INFO), 1.0 - lit).to_html(false)
	var line := "  [color=#" + star_hex + "]★[/color] [color=#" + Utils.COLOR_GOLD + "]" + ab_name + "[/color]"
	line += "  [color=#" + star_hex + "]+" + str(applied_pct) + "%" + here + "[/color]"
	if ab_effect != "":
		line += "  " + _prose("gen.ability." + str(m.get("name", "")), ab_effect, Utils.COLOR_INFO, "")
	return line + "\n\n"


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
		color = Utils.COLOR_INFO
	var filled = clampi(val, 0, 10)
	# Inline GRAPHICAL bar (CC0 Kenney RPG frame+fill, assets/ui/bars/bar_<v>.png):
	# a grayscale glossy fill tinted per value via [img color]. Bar FIRST + fixed
	# width so the bars form a clean column regardless of label width (the old █░
	# text bars staircased under the proportional UI font once a label like
	# "Administration" led the row).
	var bar = _stat_bar_img(filled, color)
	# Session UI-2: the skill's glyph beside its name (the books' one set).
	var skill_glyph := Utils.bb_glyph(label.to_lower(), 16, Utils.COLOR_GOLD) + " " if \
		label.to_lower() in SKILL_GLYPHS else ""
	var row = bar + "  " + skill_glyph + label + " [color=#" + color + "]" + str(val) + "[/color]"
	if note != "":
		row += "  [color=#" + Utils.COLOR_INFO + "]" + note + "[/color]"
	return row + "\n"


const SKILL_GLYPHS := ["tactical", "shock", "defense", "logistics", "administration", "command"]


func _stat_bar_img(filled: int, hex_color: String) -> String:
	"""One inline stat bar, value 0..10, tinted to hex_color (no '#'). Session
	UI-2: an exact meter with its track (Utils.bb_bar_img), so every bar is the
	same visible length and the names after it stand in one column."""
	return Utils.bb_bar_img(clampi(filled, 0, 10), hex_color, STAT_BAR_W, 8)


func _trust_hex(val: int) -> String:
	var color: String = Utils.COLOR_INFO
	if val < 30:
		color = Utils.cv_hex(Utils.COLOR_ERROR)
	elif val < 55:
		color = Utils.COLOR_ORANGE
	elif val >= 80:
		color = Utils.cv_hex(Utils.COLOR_SUCCESS)
	return color


func _trust_colored(val: int, label: String) -> String:
	var color = Utils.COLOR_INFO
	if val < 30:
		color = Utils.cv_hex(Utils.COLOR_ERROR)
	elif val < 55:
		color = Utils.COLOR_ORANGE
	elif val >= 80:
		color = Utils.cv_hex(Utils.COLOR_SUCCESS)
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
	var color = Utils.COLOR_INFO
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
