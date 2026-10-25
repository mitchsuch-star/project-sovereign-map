extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Incoming Proposal Popup (Session 8C)
# =============================================================================
# Displays when an AI nation sends a diplomatic proposal to the player.
# Three buttons: Accept / Counter / Reject
# =============================================================================

signal choice_made(choice: String, data: Dictionary)
# S14d (docs/TABLE_LESSON_SPEC.md §2 line 7): the letter's first-open line was
# drawn before the record — main.gd acknowledges it.
signal first_open_seen(screen: String)

# UI References
@onready var content_label = $PanelContainer/VBoxContainer/ContentLabel
@onready var accept_btn = $PanelContainer/VBoxContainer/ButtonContainer/AcceptButton
@onready var counter_btn = $PanelContainer/VBoxContainer/ButtonContainer/CounterButton
@onready var reject_btn = $PanelContainer/VBoxContainer/ButtonContainer/RejectButton
@onready var dismiss_btn = $PanelContainer/VBoxContainer/ButtonContainer/DismissButton

var current_data: Dictionary = {}
var _default_border_color: Color
@onready var panel_style: StyleBoxFlat = $PanelContainer.get_theme_stylebox("panel")

func _ready():
	# UXR3-F3: the reading scroll comes to rest on whole lines.
	Utils.keep_whole_lines(content_label)
	hide()
	accept_btn.pressed.connect(_on_accept)
	counter_btn.pressed.connect(_on_counter)
	reject_btn.pressed.connect(_on_reject)
	dismiss_btn.pressed.connect(_on_dismiss)
	# Cache default border color for normal proposals
	_default_border_color = panel_style.border_color

func show_proposal(data: Dictionary):
	"""Display incoming proposal popup."""
	AudioManager.play("letter_open")
	current_data = data
	var from_nation = data.get("from_nation", "Unknown")
	var from_display = Utils.display_nation_name(str(from_nation))
	var diplomat_name = data.get("diplomat_name", "An envoy")
	var diplomat_personality = data.get("diplomat_personality", "")
	var proposal_type = data.get("proposal_type", "unknown")
	var proposal_type_display = data.get("proposal_type_display", proposal_type)
	var clauses = data.get("clauses", [])
	var assessment = data.get("talleyrand_assessment", "")
	var accept_hint = data.get("acceptance_hint", "")
	var reject_hint = data.get("rejection_hint", "")
	var decision_reason = str(data.get("decision_reason", ""))
	var is_counter = data.get("is_counter_offer", false)
	# NA-5 §8: incoming AI ultimatum — its own register (never a counter)
	var is_ultimatum = data.get("is_ultimatum", false)
	# IQ-7: a client's petition — a loyal satellite asks its lord for a
	# province or for relief from tribute. Its own register (the petition
	# header, the clause lines as the terms, no Counter — a petition is
	# granted or refused, never bargained); the same shape `is_ultimatum`
	# takes. The producer's own field (mailbox_payloads).
	var is_petition = data.get("is_petition", false)
	# DDB-2 (DDB-D8): an ally's call to arms — joined or refused, never
	# bargained; its price and its two-turn deadline are on the letter.
	var is_call_to_arms = data.get("is_call_to_arms", false)
	# S14c (docs/EVENTS_SPEC.md §6): a moment of history — an authored letter
	# of the record with no court; the Cabinet (or Talleyrand) lays it before
	# the Emperor. Two answers, each saying what it does; no Counter.
	var is_moment = data.get("is_moment", false)
	var decision_reason_display = str(data.get("decision_reason_display", ""))
	# W6-10: the diplomat's own spoken line (voices the motive in-register)
	var diplomat_line = str(data.get("diplomat_line", ""))

	var type_display = str(proposal_type_display)
	var bbcode = ""

	if is_ultimatum:
		# Ultimatum: struck header, crimson border, demands not terms
		bbcode += "[center][color=#e66262][b]ULTIMATUM[/b][/color][/center]\n"
		var ult_pers_str = " (%s)" % str(diplomat_personality).capitalize() if diplomat_personality else ""
		bbcode += "%s%s of %s\n\n" % [diplomat_name, ult_pers_str, from_display]
		bbcode += "[b]Demands:[/b]\n"
		panel_style.border_color = Color(0.878, 0.251, 0.251, 1.0)  # Crimson
	elif is_call_to_arms:
		bbcode += "[center][color=#" + Utils.COLOR_WARNING + "][b]A CALL TO ARMS[/b][/color][/center]\n"
		var cta_pers_str = " (%s)" % str(diplomat_personality).capitalize() if diplomat_personality else ""
		bbcode += "%s%s of %s\n\n" % [diplomat_name, cta_pers_str, from_display]
		panel_style.border_color = _default_border_color
	elif is_moment:
		# The dateline is the in-game calendar label, never a historical date.
		bbcode += "[center][color=#e0c060][b]A MOMENT OF HISTORY — " + _moment_text(data.get("dateline", "")) + "[/b][/color][/center]\n"
		bbcode += "[b]" + _moment_text(data.get("title", "")) + "[/b] — " + _moment_text(diplomat_name) + " lays a letter before the Emperor.\n"
		panel_style.border_color = _default_border_color
	elif is_petition:
		# Petition: the client's own header; the clauses ARE the petition
		# (design note, grant line, refuse line, lapse rule — every figure
		# the backend applies, from one source). Gold border: a court that
		# answers to Paris, not a rival's terms.
		bbcode += "[center][color=#e0c060][b]A CLIENT'S PETITION[/b][/color][/center]\n"
		var pet_pers_str = " (%s)" % str(diplomat_personality).capitalize() if diplomat_personality else ""
		bbcode += "%s%s of %s\n\n" % [diplomat_name, pet_pers_str, from_display]
		bbcode += "[b]The petition:[/b]\n"
		panel_style.border_color = _default_border_color
	elif is_counter:
		# Counter-offer: distinct header + context
		bbcode += "[center][color=#7eb8da][b]COUNTER-OFFER[/b][/color][/center]\n"
		var pers_str = " (%s)" % str(diplomat_personality).capitalize() if diplomat_personality else ""
		bbcode += "%s%s of %s\n\n" % [diplomat_name, pers_str, from_display]
		bbcode += "[color=#" + Utils.toned_hex("a0a0a8") + "]In response to your %s proposal, %s offers modified terms:[/color]\n\n" % [type_display, from_display]
		bbcode += "[b]Revised Terms:[/b]\n"
		# Style: blue border for counter-offers
		panel_style.border_color = Color(0.494, 0.722, 0.855, 1.0)  # Steel blue
	else:
		# Normal AI proposal
		bbcode += "[b]DIPLOMATIC ENVOY[/b]\n"
		var pers_str = " (%s)" % str(diplomat_personality).capitalize() if diplomat_personality else ""
		bbcode += "%s%s of %s\n\n" % [diplomat_name, pers_str, from_display]
		# S14E-23: the header says what the treaty does ("Open Borders Agreement
		# (free military passage)") - the backend's summary, when it has one.
		var type_summary = str(data.get("proposal_type_summary", ""))
		bbcode += "[b]Proposes:[/b] %s\n" % (type_summary if type_summary != "" else type_display)
		bbcode += "[b]Terms:[/b]\n"
		# Restore default gold border
		panel_style.border_color = _default_border_color

	if is_moment:
		bbcode += _build_moment_body(data)
	elif data.has("war_context_snapshot"):
		bbcode += _build_peace_preview_section(data, clauses)
	else:
		for clause in clauses:
			bbcode += "  - %s\n" % str(clause)

	# W6-10: the envoy speaks the proposal and its motive in his own
	# register — when the line is present, it REPLACES the raw
	# "Court rationale" tag (the motive is voiced, not labeled).
	if diplomat_line != "":
		bbcode += "\n[color=#e0c060][i]%s[/i][/color]\n" % diplomat_line
	elif decision_reason_display:
		bbcode += "\n[color=#" + Utils.toned_hex("a0a0a8") + "]Court rationale: %s.[/color]\n" % decision_reason_display

	if assessment:
		bbcode += "\n[color=gray]%s[/color]\n" % assessment

	if diplomat_line == "" and decision_reason != "" and decision_reason_display == "":
		bbcode += "\n[color=#9cb2c5]Court motive: %s[/color]\n" % decision_reason

	if accept_hint:
		bbcode += "\n[color=green]If accepted: %s[/color]" % accept_hint
	if reject_hint:
		bbcode += "\n[color=red]Key obstacle: %s[/color]" % reject_hint

	# IQ-7 review R2 (honest availability): the Grant option's `enabled` /
	# `reason` are DERIVED by the backend at every read (never baked at
	# issue), and the popup reads them — it used to hard-set Grant live, so a
	# lord with no DP pressed "Grant … for 1 DP" and got a free withdrawal.
	var grant_enabled := true
	var grant_reason := ""
	if is_petition:
		grant_enabled = bool(data.get("grant_enabled", true))
		grant_reason = str(data.get("grant_reason", ""))
	# DD-1 Slice B (Oct 11, 2026): EVERY letter's accept-shaped option carries
	# the backend's one verdict (`enabled` / `reason` — the ratifier's own
	# refusal), not only a petition's Grant: a treaty the ratifier would
	# refuse (the floor, the ladder, a vassal pair) is shown as mail with its
	# reason and a dead button, never a button that bounces.
	var opts = data.get("options", [])
	if opts is Array:
		for opt in opts:
			if opt is Dictionary and str(opt.get("action", "")) in ["accept_ai_proposal", "accept_counter_offer", "accept_ai_ultimatum"]:
				grant_enabled = bool(opt.get("enabled", grant_enabled))
				if str(opt.get("reason", "")) != "":
					grant_reason = str(opt.get("reason", ""))
	# S14E-20 (S14f part 2): the haggle carries its own verdict the same way —
	# the backend asks the dry run (`generate_counter_offer(…, dry_run=True)`,
	# side-effect-free) at every read and stamps the Counter option: `enabled` /
	# `reason` when Talleyrand can or cannot find a counter, `hidden` when the
	# letter asks nothing of France (a courtesy, a peace on the held line) and
	# there is nothing to strike — no dead control. Unstamped, it stays live as
	# before; the press still reaches the handler, which spends nothing when it
	# finds none.
	var counter_enabled := true
	var counter_reason := ""
	var counter_hidden := false
	if opts is Array:
		for opt in opts:
			if opt is Dictionary and str(opt.get("action", "")) == "counter_ai_proposal":
				counter_enabled = bool(opt.get("enabled", true))
				counter_reason = str(opt.get("reason", ""))
				counter_hidden = bool(opt.get("hidden", false))
	var counter_offered: bool = not is_counter and not is_ultimatum and not is_petition and not is_call_to_arms and not is_moment and not counter_hidden
	if counter_offered and not counter_enabled and counter_reason != "":
		# Above the fold, under the header, like the Accept's own reason line
		# (IQ10-X2) — quieter: a haggle declined is not a treaty refused.
		var _c_tail := "" if counter_reason.ends_with(".") or counter_reason.ends_with("!") \
			or counter_reason.ends_with("?") else "."
		var _c_line := "[color=#" + Utils.toned_hex("a0a0a8") + "]Haggle unavailable: " + counter_reason + _c_tail + "[/color]"
		var _c_head_end := bbcode.find("\n")
		if _c_head_end >= 0:
			bbcode = bbcode.substr(0, _c_head_end + 1) + _c_line + "\n" \
				+ bbcode.substr(_c_head_end + 1)
		else:
			bbcode = _c_line + "\n" + bbcode
	if not grant_enabled and grant_reason != "":
		# IQ-10 (Sept 19, 2026): the backend's reasons are whole sentences and
		# already end in a full stop, so the template's own added one read
		# "...or refuse it..". The line keeps its stop when a reason lacks one.
		var _tail := "" if grant_reason.ends_with(".") or grant_reason.ends_with("!") \
			or grant_reason.ends_with("?") else "."
		# IQ10-X2 (Sept 23, 2026): this line explains a DEAD button, and it
		# sat LAST in a scrollable body — cut mid-sentence at 1600x900, the
		# one line the player had to scroll for. It goes under the header
		# now, above the fold; the button's tooltip still carries it too.
		var _verb := "Grant" if is_petition else "Accept"
		if is_moment:
			_verb = _moment_caption(data, "accept_ai_proposal", "Accept")
		var _reason_line := "[color=#" + Utils.COLOR_ERROR + "]" + _verb + " unavailable: " + grant_reason + _tail + "[/color]"
		var _head_end := bbcode.find("\n")
		if _head_end >= 0:
			bbcode = bbcode.substr(0, _head_end + 1) + _reason_line + "\n" \
				+ bbcode.substr(_head_end + 1)
		else:
			bbcode = _reason_line + "\n" + bbcode

	# Lapse warning
	if is_ultimatum:
		bbcode += "\n[color=#e0c060][i]This demand will lapse at end of turn.[/i][/color]"
	elif is_call_to_arms:
		bbcode += "\n[color=#" + Utils.COLOR_WARNING + "][i]Unanswered by the end of turn %d, the call is refused.[/i][/color]" % int(data.get("answer_by_turn", 0))
	elif is_petition:
		# What a lapse COSTS is the backend's lapse clause above (a lever
		# governs it); the client states only that the petition lapses.
		bbcode += "\n[color=#e0c060][i]This petition will lapse at end of turn.[/i][/color]"
	elif is_moment:
		var unanswered := _moment_text(data.get("unanswered_line", ""))
		if unanswered == "":
			unanswered = "Unanswered by the end of turn %d, the letter takes its second answer." % int(data.get("answer_by_turn", 0))
		# No blank line before it: the whole letter stands above the fold at 2.0.
		bbcode += "[color=#e0c060][i]" + unanswered + "[/i][/color]"
	elif is_counter:
		bbcode += "\n[color=#e0c060][i]This response will lapse at end of turn.[/i][/color]"
	else:
		bbcode += "\n[color=#e0c060][i]This offer will lapse at end of turn.[/i][/color]"

	# Backend prose (clause strings, court rationale, hints) can embed raw
	# multi-word nation keys — humanize once at the render chokepoint. S12:
	# through `text`, never append_text (the instrument reads the label's text).
	content_label.text = Utils.humanize_nation_keys_in_text(bbcode)

	# Enable buttons — hide Counter for counter-offers (no counter-counter),
	# for ultimatums (an ultimatum is not a negotiation — NA-5 §8) and for a
	# client's petition (granted or refused, never bargained — IQ-7)
	# IQ-7 review R2: a petition's Grant follows the backend's `enabled`
	# (see above); every other register keeps Accept live as before.
	# DD-1 Slice B: `enabled` is read for ANY letter, not only a petition.
	accept_btn.disabled = not grant_enabled
	accept_btn.tooltip_text = grant_reason if not grant_enabled else ""
	if is_moment and grant_enabled:
		accept_btn.tooltip_text = _moment_quote(data, "accept_ai_proposal")
	counter_btn.visible = not is_counter and not is_ultimatum and not is_petition and not is_call_to_arms and not is_moment and not counter_hidden
	counter_btn.disabled = is_counter or is_ultimatum or is_petition or is_call_to_arms or is_moment or not counter_enabled
	# DDB-4 (S13b): the button says what it does and what it may cost — it
	# is no editor; Talleyrand picks the counter, and a dry run spends nothing
	# when he finds none.
	counter_btn.text = "Let Talleyrand haggle (1 DP)"
	counter_btn.tooltip_text = "He sends a counter of his own choosing; if he finds none, nothing is spent and the offer stands"
	if not counter_enabled and counter_reason != "":
		# S14E-20: greyed with the reason (the Accept's own tooltip shape).
		counter_btn.tooltip_text = counter_reason
	reject_btn.disabled = false
	dismiss_btn.disabled = false
	dismiss_btn.text = "Not Now"
	# S14E-18 (S14f part 2): a set-aside letter still stands, and while it does
	# the Cabinet stays shut — said on the button that does it, in the sentence
	# the echo and the locked Cabinet use. A moment letter locks nothing; a call
	# to arms stands to its answer-by turn.
	if is_moment:
		dismiss_btn.tooltip_text = "Set this letter aside. The envoy badge reopens it."
	else:
		var _lock_by_turn := int(data.get("answer_by_turn", 0)) if is_call_to_arms else 0
		dismiss_btn.tooltip_text = "Set this letter aside — " + Utils.cabinet_shut_line(_lock_by_turn) + " The envoy badge reopens it."
	# Button labels adapt to context
	if is_ultimatum:
		accept_btn.text = "Yield"
		reject_btn.text = "Defy"
	elif is_call_to_arms:
		accept_btn.text = "Join"
		reject_btn.text = "Refuse"
	elif is_petition:
		# Captions only (the buttons emit the "accept"/"reject" keywords the
		# router already owns); the typed route's option labels are the
		# multi-word "Grant the petition" / "Refuse the petition".
		accept_btn.text = "Grant"
		reject_btn.text = "Refuse"
	elif is_moment:
		# The authored captions ("Seal the match" / "Let Baden keep her"); the
		# buttons still emit the "accept" / "reject" keywords the router owns.
		accept_btn.text = _moment_caption(data, "accept_ai_proposal", "Accept")
		reject_btn.text = _moment_caption(data, "reject_ai_proposal", "Decline")
		reject_btn.tooltip_text = _moment_quote(data, "reject_ai_proposal")
	else:
		accept_btn.text = "Accept Terms" if is_counter else "Accept"
		reject_btn.text = "Reject Terms" if is_counter else "Reject"
	show()
	# July 18, 2026 viewport sweep: fit to the CURRENT logical viewport.
	# Interface Scale (content_scale_factor, up to 2.0) divides the logical
	# viewport, so a fixed authored rect can carry the action row off-screen
	# and leave a modal undismissable. The helper is a no-op wherever the
	# panel already fits, and returns early for non-centre-anchored panels.
	Utils.clamp_centered_panel($PanelContainer)

func _moment_text(value) -> String:
	"""S14c: backend copy into BBCode — a `[` escaped (never parsed as a tag)."""
	if value == null:
		return ""
	return str(value).replace("[", "[lb]")


func _moment_answer(data: Dictionary, action: String) -> Dictionary:
	var answers = data.get("answers", [])
	if answers is Array:
		for a in answers:
			if a is Dictionary and str(a.get("action", "")) == action:
				return a
	return {}


func _moment_caption(data: Dictionary, action: String, fallback: String) -> String:
	var caption := str(_moment_answer(data, action).get("caption", ""))
	return caption if caption != "" else fallback


func _moment_quote(data: Dictionary, action: String) -> String:
	return str(_moment_answer(data, action).get("quote", ""))


func _build_moment_body(data: Dictionary) -> String:
	"""S14c (docs/EVENTS_SPEC.md §2's copy contract): the record, the board
	(derived lines), then what each answer does — the plan's own quotes, the
	caption in bold. The unanswered line is the footer."""
	var out := ""
	# S14d: the sixth part of the copy contract (EVENTS_SPEC §2, A5) — the
	# first letter's line, before the record, in the R159 register.
	var fo = data.get("first_open")
	if fo is Dictionary and str(fo.get("line", "")) != "":
		out += "[color=#" + Utils.COLOR_INFO + "]" + _moment_text(fo.get("line", "")) + "[/color]\n"
		first_open_seen.emit(str(fo.get("screen", "moment_letter")))
	var record := _moment_text(data.get("record", ""))
	if record != "":
		out += "[i]" + record + "[/i]\n"
	var board = data.get("board", [])
	if board is Array:
		for line in board:
			out += "  - " + _moment_text(line) + "\n"
	var answers = data.get("answers", [])
	if answers is Array and answers.size() > 0:
		out += "[b]What each answer does[/b]\n"
		for a in answers:
			if not (a is Dictionary):
				continue
			var caption := _moment_text(a.get("caption", ""))
			var quote := _moment_text(a.get("quote", ""))
			if caption != "" and quote.begins_with(caption + ":"):
				quote = "[b]" + caption + "[/b]" + quote.substr(caption.length())
			out += "  " + quote + "\n"
	return out


func _on_accept():
	_disable_buttons()
	hide()
	choice_made.emit("accept", current_data)

func _on_counter():
	_disable_buttons()
	hide()
	choice_made.emit("counter", current_data)

func _on_reject():
	_disable_buttons()
	hide()
	choice_made.emit("reject", current_data)

func _on_dismiss():
	_disable_buttons()
	hide()
	choice_made.emit("dismiss", current_data)

func _disable_buttons():
	accept_btn.disabled = true
	counter_btn.disabled = true
	reject_btn.disabled = true
	dismiss_btn.disabled = true

func _build_peace_preview_section(data: Dictionary, clauses: Array) -> String:
	var snapshot = data.get("war_context_snapshot", {})
	# UXR3-30 (Pre-Deploy S12 part 2): the offer's terms render directly
	# under "Terms:" — they sat under a second heading after the whole
	# War Summary, below the fold, and "Terms:" stood empty.
	var bbcode = ""
	var annotated = snapshot.get("annotated_terms", data.get("annotated_terms", []))
	if annotated is Array and not annotated.is_empty():
		bbcode += _build_annotated_terms_section(annotated)
		# S14D-X50 (October 24, 2026): a peace COUNTER that strikes one demand
		# and keeps others carries its "Struck: …" lines in `clauses` (S14D-X13)
		# while the annotated preview draws the kept terms — print the struck
		# lines beneath it, so the letter says what the court would not sign.
		if bool(data.get("is_counter_offer", false)):
			for clause in clauses:
				if str(clause).begins_with("Struck"):
					bbcode += "  - %s\n" % str(clause)
	else:
		for clause in clauses:
			bbcode += "  - %s\n" % str(clause)

	var harshness_label = str(snapshot.get("harshness_label", data.get("harshness_label", "")))
	if harshness_label:
		var harshness_color = "#80a0d0"
		if harshness_label == "generous":
			harshness_color = "#80c080"
		elif harshness_label == "harsh":
			harshness_color = "#e09040"
		elif harshness_label == "punitive":
			harshness_color = "#e66262"
		bbcode += "Assessment: [color=%s]%s[/color]\n" % [harshness_color, harshness_label.to_upper()]

	# VP1-X7 (S14b part 2): the manner of this peace and its Revanche — the
	# snapshot's pair, off the clause list the ratifier builds.
	var manner_line = str(snapshot.get("manner_line", ""))
	if manner_line != "":
		bbcode += "[color=#e0c070]" + Utils.humanize_nation_keys_in_text(manner_line.replace("[", "[lb]")) + "[/color]\n"
	var revanche_line = str(snapshot.get("revanche_line", ""))
	if revanche_line != "":
		var rv_color = "#e66262" if revanche_line.begins_with("Revanche stands") else "#80a0d0"
		bbcode += "[color=" + rv_color + "]" + Utils.humanize_nation_keys_in_text(revanche_line.replace("[", "[lb]")) + "[/color]\n"

	bbcode += "\n[b]War Summary[/b]\n"
	# PC-X27 (S13e part 4): the war is named by its stake.
	var war_title_line = str(snapshot.get("war_title_line", ""))
	if war_title_line != "":
		bbcode += Utils.humanize_nation_keys_in_text(war_title_line) + "\n"
	var war_score = int(snapshot.get("war_score", 0))
	var score_color = "#80c080"
	if war_score < 0:
		score_color = "#e66262"
	elif war_score == 0:
		score_color = "#80a0d0"
	var trend = str(snapshot.get("war_score_trend", "stagnant"))
	var trend_arrow = "->"
	if trend == "rising":
		trend_arrow = "^"
	elif trend == "falling":
		trend_arrow = "v"
	bbcode += "War score: [color=%s]%d %s[/color]" % [score_color, war_score, trend_arrow]
	var components = snapshot.get("war_score_components", {})
	if components is Dictionary:
		var parts = []
		# PC-F39 (S13e part 3): one list with the war-detail popup — the
		# breakdown sums to its score (Campaign, Blood, Blockade, Captive
		# were dropped: "52 (… Ticking −4)" summed to 31).
		for key in ["territory", "battle", "decisive_battle", "capital", "campaign", "blood", "blockade", "captive", "ticking"]:
			var val = int(components.get(key, 0))
			if val != 0:
				var label = str(key).replace("_", " ").capitalize()
				parts.append("%s %s%d" % [label, "+" if val > 0 else "", val])
		if not parts.is_empty():
			bbcode += " (%s)" % ", ".join(parts)
	bbcode += "\n"

	var tier_display = str(snapshot.get("settlement_tier_display", ""))
	if tier_display:
		# IQ-2 review round: an enemy's offer to a losing France showed its
		# own leverage as a gold prize. Absent key = the old line.
		var tier_side = snapshot.get("settlement_tier_side", "")
		# PC-F38 (S13e part 3): this is the PAIR's own tier (what the table
		# scores this court on since PC-R4), labelled as the pair's.
		var scope = str(snapshot.get("settlement_tier_scope", ""))
		var scope_text = "" if scope == "" else " (" + scope + ")"
		if tier_side is String and tier_side == "theirs":
			bbcode += "Settlement" + scope_text + " (theirs to impose): [color=#" + Utils.COLOR_ERROR + "]%s[/color]\n" % tier_display
		else:
			bbcode += "Settlement" + scope_text + ": [color=#e0c070]%s[/color]\n" % tier_display
	var objective = snapshot.get("war_objective", {})
	if objective is Dictionary and not objective.is_empty():
		var objective_type = str(objective.get("type", "")).replace("_", " ").capitalize()
		# LV-8 (row EP F1): one sentence, not the 28-name homeland list.
		var region_text = Utils.objective_targets_text(objective, "objective target")
		var accumulated = int(objective.get("accumulated_ticking", 0))
		var active = bool(objective.get("ticking_active", false))
		var active_text = "active" if active else "inactive"
		bbcode += "Objective: %s - %s (%s)\n" % [objective_type, region_text, active_text]
		bbcode += "Ticking: +%d\n" % accumulated

	var duration = int(snapshot.get("war_duration_turns", 0))
	var won = int(snapshot.get("battles_won", 0))
	var lost = int(snapshot.get("battles_lost", 0))
	# S14E-X201: a drawn battle (a stalemate) is a battle fought — "0W / 0L / 1 drawn"
	var drawn = int(snapshot.get("battles_drawn", 0))
	var drawn_text = (" / %d drawn" % drawn) if drawn > 0 else ""
	bbcode += "Duration: %d turns   Battles: %dW / %dL%s\n" % [duration, won, lost, drawn_text]

	var french_casualties = int(snapshot.get("french_casualties_total", 0))
	var enemy_casualties = int(snapshot.get("enemy_casualties_total", 0))
	if french_casualties > 0 or enemy_casualties > 0:
		bbcode += "Casualties: ours %s / theirs %s\n" % [str(french_casualties), str(enemy_casualties)]

	var held_by_us = snapshot.get("regions_held_by_france", [])
	if held_by_us is Array and not held_by_us.is_empty():
		bbcode += "[color=#80c080]We hold: %s[/color]\n" % ", ".join(held_by_us)
	var held_by_them = snapshot.get("regions_held_by_enemy", [])
	if held_by_them is Array and not held_by_them.is_empty():
		bbcode += "[color=#e66262]They hold: %s[/color]\n" % ", ".join(held_by_them)
	if snapshot.has("armistice_remaining_turns"):
		bbcode += "Armistice remaining: %d turns\n" % int(snapshot.get("armistice_remaining_turns", 0))

	# G4F-17: incoming armistice offers explain the truce mechanics too.
	var armistice_mechanics = snapshot.get("armistice_mechanics", {})
	if armistice_mechanics is Dictionary and not armistice_mechanics.is_empty():
		bbcode += "\n[b]Armistice Terms[/b]\n"
		for line in armistice_mechanics.get("display_lines", []):
			var line_color = "#a0a0d0"
			if str(line).begins_with("Relations stand"):
				line_color = "#80c080" if str(armistice_mechanics.get("projected_outcome", "")) == "peace" else "#e09040"
			bbcode += "  [color=%s]%s[/color]\n" % [line_color, str(line)]

	var fallout = data.get("fallout_warnings", snapshot.get("fallout_warnings", []))
	var conflicts = data.get("commitment_conflicts", snapshot.get("commitment_conflicts", []))
	var tier_warnings = snapshot.get("tier_mismatch_warnings", [])
	if (tier_warnings is Array and not tier_warnings.is_empty()) or (fallout is Array and not fallout.is_empty()) or (conflicts is Array and not conflicts.is_empty()):
		bbcode += "\n[b]Political Consequences[/b]\n"
		var consequence_items = []
		for warning in tier_warnings:
			var warning_text = warning.get("display", warning.get("text", str(warning))) if warning is Dictionary else str(warning)
			consequence_items.append({"priority": 1, "color": "#e0c070", "text": warning_text})
		for warning in fallout:
			var warning_text = warning.get("display", str(warning)) if warning is Dictionary else str(warning)
			var severity = str(warning.get("severity", "INFO")).to_upper() if warning is Dictionary else "INFO"
			var warning_type = str(warning.get("warning_type", "")) if warning is Dictionary else ""
			var priority = 2 if warning_type in ["separate_peace_ally", "contingent_released", "sanctuary"] else 3
			var color = "#e66262" if severity == "SEVERE" else "#e0c070"
			consequence_items.append({"priority": priority, "color": color, "text": warning_text})
		for conflict in conflicts:
			var conflict_text = conflict.get("display", str(conflict)) if conflict is Dictionary else str(conflict)
			var conflict_severity = str(conflict.get("severity", "INFO")).to_upper() if conflict is Dictionary else "INFO"
			var conflict_priority = 0 if conflict_severity == "HARD_STOP" else 4
			if conflict_severity == "WARNING":
				conflict_priority = 1
			var conflict_color = "#e66262" if conflict_severity in ["WARNING", "HARD_STOP"] else "#e0c070"
			consequence_items.append({"priority": conflict_priority, "color": conflict_color, "text": conflict_text})
		consequence_items.sort_custom(func(a, b): return int(a.get("priority", 99)) < int(b.get("priority", 99)))
		# S14E-25: every consequence is printed — the popup scrolls, and a cap
		# of three with an overflow line left the rest with no way open.
		# S14E-X198: each consequence once (the confirm popup's own guard).
		var printed_texts := {}
		for item in consequence_items:
			if printed_texts.has(str(item.get("text", ""))):
				continue
			printed_texts[str(item.get("text", ""))] = true
			bbcode += "  [color=%s]-[/color] %s\n" % [str(item.get("color", "#e0c070")), str(item.get("text", ""))]

	return bbcode

func _build_annotated_terms_section(annotated: Array) -> String:
	var demands = []
	var concessions = []
	var mutual = []
	for term in annotated:
		var direction = str(term.get("term_direction", "mutual"))
		if direction == "demand":
			demands.append(term)
		elif direction == "concession":
			concessions.append(term)
		else:
			mutual.append(term)

	var bbcode = ""
	if not demands.is_empty():
		bbcode += "[b]France demands:[/b]\n"
		for term in demands:
			bbcode += "  [color=#e09040]-[/color] %s\n" % _term_label(term)
	if not concessions.is_empty():
		bbcode += "[b]France concedes:[/b]\n"
		for term in concessions:
			bbcode += "  [color=#80c0a0]-[/color] %s\n" % _term_label(term)
	if not mutual.is_empty():
		bbcode += "[b]Mutual:[/b]\n"
		for term in mutual:
			bbcode += "  [color=#e0c070]-[/color] %s\n" % _term_label(term)
	if bbcode:
		bbcode += "\n"
	return bbcode

func _term_label(term: Dictionary) -> String:
	return str(term.get("display_label", term.get("display", "?")))
