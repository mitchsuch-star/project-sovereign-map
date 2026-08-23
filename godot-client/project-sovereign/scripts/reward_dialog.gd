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

@onready var title_label = $PanelContainer/VBoxContainer/TitleLabel
@onready var info_label = $PanelContainer/VBoxContainer/InfoLabel
@onready var options_container = $PanelContainer/VBoxContainer/ScrollContainer/OptionsContainer
@onready var cancel_button = $PanelContainer/VBoxContainer/CancelButton


func _ready():
	if cancel_button:
		cancel_button.pressed.connect(_on_cancel)
	hide()


func show_reward(card: Dictionary):
	"""Build the reward portfolio for one marshal from his overview card."""
	AudioManager.play("to_the_color")  # honors for a marshal (capped in CUES)
	var m_name = str(card.get("name", "?"))
	title_label.text = "REWARD MARSHAL " + m_name.to_upper()

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
	bbcode += "\n[color=#909090]An [b]ESTATE[/b] redirects a conquered province's income to his household — the cheaper instrument, and the land APPRECIATES as it stabilizes"
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
	if face > 0:
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
		label.add_theme_color_override("font_color", Color(0.7, 0.7, 0.75, 1))
		label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		options_container.add_child(label)

	show()
	# July 18, 2026 viewport sweep: fit to the CURRENT logical viewport.
	# Interface Scale (content_scale_factor, up to 2.0) divides the logical
	# viewport, so a fixed authored rect can push the action row off-screen.
	# Runs AFTER show() so layout has settled.
	Utils.clamp_centered_panel($PanelContainer)


func _add_option(label_text: String, command: String, font_color: Color):
	var btn = Button.new()
	btn.text = label_text
	btn.custom_minimum_size = Vector2(0, 42)
	btn.add_theme_font_size_override("font_size", 13)
	btn.add_theme_color_override("font_color", font_color)
	btn.clip_text = true
	btn.pressed.connect(_on_option_pressed.bind(command))
	options_container.add_child(btn)


func _on_option_pressed(command: String):
	hide()
	reward_command.emit(command)


func _on_cancel():
	hide()
	cancelled.emit()
