extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Marshal Reward Dialog (ES-7 second pass, §0.6.8 item 6)
# =============================================================================
# Opened from the Generals screen's [Reward…] link. Presents the reward
# PORTFOLIO for one marshal — estates (land: cheaper, appreciating, lootable)
# vs the rente (cash: instant, war-safe, premium-priced) — every option
# stating its terms in one line, then issues the same typed command the
# terminal accepts. CanvasLayer 109. Follows load_dialog.gd's
# dynamic-button pattern.
# =============================================================================

signal reward_command(command: String)
signal cancelled()

# RR5-X5: the choices the dialog keeps in view, and one choice's height.
const REWARD_ROWS_SEEN := 4
const REWARD_ROW_PX := 42.0

# UX23-R1: the player this dialog started, silenced when it closes.
var _own_cue = null

@onready var title_label = $PanelContainer/VBoxContainer/TitleLabel
@onready var info_label = $PanelContainer/VBoxContainer/InfoLabel
@onready var options_container = $PanelContainer/VBoxContainer/ScrollContainer/OptionsContainer
@onready var cancel_button = $PanelContainer/VBoxContainer/CancelButton


func _ready():
	if cancel_button:
		cancel_button.pressed.connect(_on_cancel)
	# RR5-X5: the explainer is the dialog's reading scroll now that the
	# choices keep their rows — it rests on whole lines (UXR3-F3).
	Utils.keep_whole_lines(info_label)
	hide()


func show_reward(card: Dictionary):
	"""Build the reward portfolio for one marshal from his overview card."""
	_own_cue = AudioManager.play("to_the_color")  # honors for a marshal
	# UX23-R1 review: 6.0 s of bugle on a dialog the player dismisses in
	# one click — the longest cue in the tree that nothing was stopping.
	# reward_dialog extends CanvasLayer, not PopupBase, so it holds its
	# own handle rather than calling claim_cue.
	var m_name = str(card.get("name", "?"))
	title_label.text = "REWARD MARSHAL " + m_name.to_upper()
	# Session UI-2: the medal over the header (the Emperor's honours).
	_arms_row([{"glyph": "medal"}])
	_set_banner()

	for child in options_container.get_children():
		child.queue_free()

	var expectation = int(card.get("expectation", 0))
	var estate_income = int(card.get("estate_income", 0))
	var pension = int(card.get("pension", 0))
	var pension_cost = int(card.get("pension_cost", 0))
	var shortfall = int(card.get("expectation_shortfall", 0))
	var eroding = bool(card.get("is_eroding", false))

	# ── Header: the numbers, then what each instrument IS ──
	var bbcode = "[color=#e0c070]" + m_name + " expects [b]" + str(expectation) + "g/turn[/b]"
	bbcode += " — holds " + str(estate_income) + "g/turn in estates"
	if pension > 0:
		bbcode += " + a " + str(pension) + "g/turn rente (costing the treasury " + str(pension_cost) + "g)"
	bbcode += ".[/color]\n"
	if shortfall > 0:
		if eroding:
			bbcode += "[color=#e08060]Shortfall: " + str(shortfall) + "g/turn — his loyalty is ERODING.[/color]\n"
		else:
			bbcode += "[color=#e0a060]Shortfall: " + str(shortfall) + "g/turn — his patience is finite.[/color]\n"
	else:
		bbcode += "[color=#80c0a0]His expectation is met.[/color]\n"
	bbcode += "\n[color=#" + Utils.COLOR_INFO + "]An [b]ESTATE[/b] redirects a conquered province's income to his household — the cheaper instrument, and the land APPRECIATES as it stabilizes"
	var steward_tier = str(card.get("steward_tier", ""))
	if steward_tier == "prosperous":
		bbcode += " (faster under his able hand)"
	elif steward_tier == "wasteful":
		bbcode += " (slowly — he is a wasteful lord)"
	bbcode += " — but land can be lost to conquest or signed away at a peace table.\n"
	# The premium is DERIVED from the backend's face/cost pair so the prose
	# can never lie when RENTE_PREMIUM is retuned (shown = applied).
	var offer_preview = card.get("rente_offer", {})
	var premium_note = "more than its face"
	if offer_preview is Dictionary:
		var pf = int(offer_preview.get("face", 0))
		var pc = int(offer_preview.get("cost", 0))
		if pf > 0 and pc > pf:
			premium_note = str(int(round(float(pc - pf) / float(pf) * 100.0))) + "% above its face"
	bbcode += "A [b]RENTE[/b] is treasury gold — instant, precise, and safe from any enemy, but it costs the crown " + premium_note + " each turn, never grows, and buys no title.[/color]"
	info_label.text = bbcode
	_set_strip(expectation, estate_income, pension, shortfall)

	var option_count = 0

	# ── Estate options (top eligible provinces, richest first) ──
	var details = card.get("eligible_estate_details", [])
	var fee = int(card.get("investiture_fee", 0))
	if details is Array:
		for d in details:
			if not (d is Dictionary):
				continue
			var region = str(d.get("region", ""))
			if region == "":
				continue
			var income = int(d.get("income", 0))
			var covers = ""
			if shortfall > 0:
				if income >= shortfall:
					covers = " — covers his full gap"
				else:
					covers = " — covers " + str(income) + "g of " + str(shortfall) + "g"
			# XR-4 (Econ Balance EB-3, + review [4]): the pre-flight
			# warning names the TRUE recovery mechanism — an OCCUPIED
			# estate pays nothing until the enemy army is driven off
			# (its stability is falling), a war-torn one recovers as
			# stability grows.
			if bool(d.get("occupied", false)):
				covers = " — under enemy occupation: yields nothing until the army is driven off"
			elif bool(d.get("war_torn", false)):
				covers = " — war-torn: yields 0 today, recovers as stability does"
			var fee_str = "  [+" + str(fee) + "g investiture]" if fee > 0 else ""
			_add_option(
				"Endow " + region + " — " + str(income) + "g/turn" + covers + fee_str,
				"endow " + m_name + " with " + region,
				Utils.UI_GOLD
			)
			option_count += 1

	# ── Rente options ──
	var offer = card.get("rente_offer", {})
	var face = int(offer.get("face", 0)) if offer is Dictionary else 0
	var cost = int(offer.get("cost", 0)) if offer is Dictionary else 0
	# Aug 23, 2026: gate on the backend's own predicate, not on `face > 0`.
	# The face is `expectation − ESTATE income` and ignores the rente he
	# already holds, so a fully-paid marshal reported face 80 and this offered
	# "Re-size rente — 80g/turn" that the executor then refused — and counting
	# it as an option made the honest "His expectation is met" fallback below
	# unreachable. `would_change` is the same call `grant_pension` gates on.
	var rente_changes = bool(offer.get("would_change", face > 0)) \
			if offer is Dictionary else false
	if face > 0 and rente_changes:
		var verb = "Grant rente" if pension <= 0 else "Re-size rente"
		_add_option(
			verb + " — " + str(face) + "g/turn to him, " + str(cost) + "g/turn from the treasury",
			"grant " + m_name + " a rente",
			Color(0.55, 0.75, 0.85, 1)
		)
		option_count += 1
	if pension > 0:
		# Honest copy (review fix): threaten the reopened shortfall only
		# when his estates do NOT already cover his full expectation —
		# revoking a redundant rente after estate appreciation is free.
		var covered_without_rente = int(card.get("estate_income", 0)) >= expectation
		var revoke_note = "; his estates sustain him — no shortfall reopens" if covered_without_rente else "; his shortfall reopens"
		_add_option(
			"Revoke his rente — keep " + str(pension_cost) + "g/turn" + revoke_note,
			"revoke " + m_name + "'s rente",
			Color(0.85, 0.55, 0.45, 1)
		)
		option_count += 1

	if option_count == 0:
		var label = Label.new()
		if shortfall > 0:
			label.text = "No conquered province remains to endow, and no rente is possible.\nVictory abroad will furnish an estate."
		else:
			label.text = "His expectation is met — no reward is needed."
		label.add_theme_color_override("font_color", Utils.UI_HINT_GREY)
		label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		options_container.add_child(label)

	# RR5-X5 (SF-RR5, October 21, 2026): the choices are answers — their
	# scroll keeps up to REWARD_ROWS_SEEN of them whole at any Interface Scale
	# (the relax pass never takes it below them); the explainer above yields
	# first and scrolls. At 2.0 the two shared 222 px half and half, and Ney's
	# third choice, revoking his rente, sat below the fold.
	var scroll: ScrollContainer = $PanelContainer/VBoxContainer/ScrollContainer
	var rows := mini(maxi(option_count, 1), REWARD_ROWS_SEEN)
	scroll.custom_minimum_size.y = maxf(120.0, float(rows) * (REWARD_ROW_PX + 8.0) + 2.0)
	scroll.set_meta("relax_floor", scroll.custom_minimum_size.y)

	show()
	# July 18, 2026 viewport sweep: fit to the CURRENT logical viewport.
	# Interface Scale (content_scale_factor, up to 2.0) divides the logical
	# viewport, so a fixed authored rect can push the action row off-screen.
	# Runs AFTER show() so layout has settled.
	Utils.clamp_centered_panel($PanelContainer)
	call_deferred("_fit_info")


func _set_strip(expectation: int, estate_income: int, pension: int, shortfall: int) -> void:
	"""Session UI-2 (figures before prose): his expectation, what his estates
	pay, the rente and the shortfall stand as a figure strip above the
	explainer — the prose below stays exactly as it was."""
	var vb: VBoxContainer = $PanelContainer/VBoxContainer
	var strip: Control = vb.get_node_or_null("FigureStrip") as Control
	if strip == null:
		strip = preload("res://scripts/stat_strip.gd").new()
		strip.name = "FigureStrip"
		vb.add_child(strip)
		vb.move_child(strip, info_label.get_index())
	var tiles: Array = [
		{"glyph": "gold", "figure": str(expectation) + "g", "caption": "Expects", "tip": "Gold per turn he expects"},
		{"glyph": "build", "figure": str(estate_income) + "g", "caption": "In estates", "tip": "Gold per turn his estates pay"},
	]
	if pension > 0:
		tiles.append({"glyph": "income", "figure": str(pension) + "g", "caption": "Rente", "tip": "Gold per turn of rente"})
	var gap_tone: Color = Utils.UI_ALERT_TEXT if shortfall > 0 else Utils.UI_SCORE_POSITIVE   # a figure: the alert red
	tiles.append({"glyph": "stability", "figure": str(shortfall) + "g", "caption": "Shortfall",
		"tone": gap_tone, "tip": "Gold per turn short of his expectation"})
	strip.call("set_tiles", tiles)
	# the figures are the prose's own; the compact view keeps the room
	if Utils.compact_view():
		strip.visible = false


func _set_banner() -> void:
	"""Session UI-5: the reward's picture at the head of the card (null — no
	picture, or the compact view — leaves the card as it was)."""
	var vb: VBoxContainer = $PanelContainer/VBoxContainer
	var old: Node = vb.get_node_or_null("Illustration")
	if old != null:
		vb.remove_child(old)
		old.queue_free()
	var w: float = maxf(($PanelContainer as Control).size.x, ($PanelContainer as Control).custom_minimum_size.x)
	if w <= 0.0:
		w = 480.0
	var banner: TextureRect = Illustrations.make_banner("reward", w)
	if banner == null:
		return
	banner.custom_minimum_size.y = minf(banner.custom_minimum_size.y, 100.0)
	vb.add_child(banner)
	vb.move_child(banner, 0)


func _fit_info() -> void:
	"""Session UI-2: the explainer sizes to its own text (bounded) and the card
	shrinks to what it holds — after the layout has given it its width."""
	await get_tree().process_frame
	if not visible:
		return
	if Utils.compact_view():
		# the compact view: the clamp alone, as before (it relaxes the
		# explainer to the room; every choice and Not now stay in view)
		Utils.clamp_centered_panel($PanelContainer)
		return
	info_label.custom_minimum_size.y = clampf(info_label.get_content_height() + 12.0, 100.0, 260.0)
	# Session UI-5: the picture steps aside first when the card would not fit
	var banner := get_node_or_null("PanelContainer/VBoxContainer/Illustration") as Control
	if banner != null:
		banner.visible = true
		var view_h: float = get_viewport().get_visible_rect().size.y
		if ($PanelContainer as Control).get_combined_minimum_size().y > view_h * 0.94:
			banner.visible = false
	Utils.clamp_centered_panel($PanelContainer)
	Utils.shrink_centered_panel_to_content($PanelContainer)


func refit() -> void:
	"""UXR-2's live-refit hook (`Utils.refit_surface`): the fit, as on open."""
	call_deferred("_fit_info")


func _add_option(label_text: String, command: String, font_color: Color):
	var btn = Button.new()
	btn.text = label_text
	btn.custom_minimum_size = Vector2(0, REWARD_ROW_PX)
	btn.theme_type_variation = &"CaptionButton"
	btn.add_theme_color_override("font_color", font_color)
	btn.clip_text = true
	btn.pressed.connect(_on_option_pressed.bind(command))
	options_container.add_child(btn)


func _on_option_pressed(command: String):
	AudioManager.stop_player(_own_cue)
	_own_cue = null
	hide()
	reward_command.emit(command)


func _on_cancel():
	AudioManager.stop_player(_own_cue)
	_own_cue = null
	hide()
	cancelled.emit()


func _arms_row(parts: Array) -> void:
	"""Session UI-2: the arms the voice speaks under (a court's flag, an
	office's glyph, the Empire's eagle) in one centred row above the title;
	an empty list hides the row. Built once, refilled on every show."""
	var vb: VBoxContainer = $PanelContainer/VBoxContainer
	var row: HBoxContainer = vb.get_node_or_null("ArmsRow") as HBoxContainer
	if row == null:
		row = HBoxContainer.new()
		row.name = "ArmsRow"
		row.alignment = BoxContainer.ALIGNMENT_CENTER
		row.add_theme_constant_override("separation", 12)
		row.mouse_filter = Control.MOUSE_FILTER_IGNORE
		vb.add_child(row)
		vb.move_child(row, 0)
	for c in row.get_children():
		row.remove_child(c)
		c.queue_free()
	for part in parts:
		var tex_path: String = ""
		var tint: Color = Color.WHITE
		var h: float = 26.0
		if part.has("flag"):
			tex_path = Utils.nation_flag_path(str(part["flag"]))
		elif part.has("glyph"):
			tex_path = Utils.glyph(str(part["glyph"]))
			tint = Utils.UI_GOLD
		elif part.has("eagle"):
			tex_path = Utils.EAGLE
			tint = Color(Utils.UI_GOLD, 0.92)
			h = 44.0
		if tex_path == "" or not ResourceLoader.exists(tex_path):
			continue
		var tex: Texture2D = load(tex_path)
		if tex == null or tex.get_height() <= 0:
			continue
		var art := TextureRect.new()
		art.texture = tex
		art.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		art.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		art.custom_minimum_size = Vector2(h * float(tex.get_width()) / float(tex.get_height()), h)
		art.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		art.modulate = tint
		art.mouse_filter = Control.MOUSE_FILTER_IGNORE
		row.add_child(art)
	# the compact view (Interface Scale 2.0) keeps its room for the answers
	row.visible = row.get_child_count() > 0 and not Utils.compact_view()
