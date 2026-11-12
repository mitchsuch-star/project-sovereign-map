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

# PC-F46 (S15 head): the letter's box as a fraction of the logical viewport —
# the authored 680 x 440 is the floor (`incoming_proposal_popup.tscn`).
const LETTER_HEIGHT_FRACTION := 0.8
const LETTER_WIDTH_FRACTION := 0.45
const LETTER_MIN_WIDTH := 680.0
const LETTER_MIN_HEIGHT := 440.0
const LETTER_MAX_WIDTH := 860.0

# S14G-6 / S14G-D3 (Pre-Deploy S14h part 1, October 26, 2026): what "Not Now"
# does to the Cabinet is VISIBLE, not a tooltip — the button's own label when
# the letter locks it, and a line under the buttons either way. Only a great
# court's letter, an ultimatum or a war decision locks (the backend's
# `locks_cabinet`, from `DialogueManager.letter_locks_cabinet`); a lesser
# court's routine letter waits in the mailbox and the Cabinet stays open.
const NOT_NOW_LABEL := "Not Now"
const NOT_NOW_LOCKED_LABEL := "Not Now (Cabinet stays shut)"
const SET_ASIDE_LOCKED_PREFIX := "Set aside — "
const SET_ASIDE_WAITS_LINE := "Set aside — it waits in the mailbox until the turn ends; the Cabinet stays open."

var current_data: Dictionary = {}
var _default_border_color: Color
# S14G-6: the line under the buttons (built here, not in the .tscn).
var _set_aside_line: Label = null
# Session UI (November 11, 2026): the panel's box is the gilt frame now
# (`scripts/gilt_frame.gd`, a scripted StyleBox — not a StyleBoxFlat). It keeps
# StyleBoxFlat's `border_color` name, so every tint below writes as it did;
# the variable is untyped because the property lives on the script.
@onready var panel_style = $PanelContainer.get_theme_stylebox("panel")

func _ready():
	# UXR3-F3: the reading scroll comes to rest on whole lines.
	Utils.keep_whole_lines(content_label)
	hide()
	# Session UI-3: a note's more/less link opens in place; the Settings switch
	# re-renders an open letter from its cached data.
	content_label.meta_clicked.connect(_on_body_meta)
	Utils.on_explanations_changed(_on_explanations_switched)
	accept_btn.pressed.connect(_on_accept)
	counter_btn.pressed.connect(_on_counter)
	reject_btn.pressed.connect(_on_reject)
	dismiss_btn.pressed.connect(_on_dismiss)
	# S14G-6: the line under the buttons — what setting the letter aside does
	# to the Cabinet, where the player decides it (the sentence was on the
	# button's tooltip only).
	_set_aside_line = Label.new()
	_set_aside_line.theme_type_variation = &"Caption"
	_set_aside_line.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_set_aside_line.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_set_aside_line.visible = false
	$PanelContainer/VBoxContainer.add_child(_set_aside_line)
	# Cache default border color for normal proposals
	_default_border_color = panel_style.border_color

# Session UI-3 (November 12, 2026): the body's composed template (the grey
# assessment's slot left open), so a note toggle re-sets ONLY the body text —
# the dress (`_dress_letter`) appends to the buttons' words and must never run
# twice on one letter.
const ASSESS_SLOT := "\u0001ASSESS\u0001"
const NOTE_PETITION := "petition.talleyrand"
const NOTE_ASSESSMENT := "proposal.assessment"
var _body_template: String = ""
var _assessment_text: String = ""
var _assessment_id: String = NOTE_ASSESSMENT
var _silent_rebuild := false


func _assessment_block() -> String:
	"""The grey assessment line: whole On the page (byte for byte as before);
	Folded, its first sentence and a more/less link (`Utils.bb_note`)."""
	if _assessment_text == "":
		return ""
	var cut := _assessment_text.find(". ")
	var summary := _assessment_text
	var rest := ""
	if cut > 0 and cut + 2 < _assessment_text.length():
		summary = _assessment_text.substr(0, cut + 1)
		rest = _assessment_text.substr(cut + 1)
	return "\n[color=gray]" + Utils.bb_note(_assessment_id, summary, rest) + "[/color]\n"


func _render_body() -> void:
	"""Compose the body from the cached template and the note's state. S12:
	through `text`, never append_text (the instrument reads the label's text)."""
	content_label.text = Utils.humanize_nation_keys_in_text(
		_body_template.replace(ASSESS_SLOT, _assessment_block()))


func _on_body_meta(meta) -> void:
	if not Utils.is_note_meta(meta):
		return
	Utils.toggle_note(meta)
	var kept: float = content_label.get_v_scroll_bar().value
	_render_body()
	refit()
	Utils.restore_label_scroll(content_label, kept)


func _on_explanations_switched() -> void:
	"""The Settings switch moved while a letter stands: the body is rebuilt from
	the cached data (a letter of state carries no notes and is left alone)."""
	if not visible or current_data.is_empty() or bool(current_data.get("is_moment", false)):
		return
	_silent_rebuild = true
	show_proposal(current_data)
	_silent_rebuild = false


func _petition_figure_rows(clauses: Array, grant_figs: Array, refuse_figs: Array) -> String:
	"""A client's petition as figures: the design note (when the petition carries
	one — the clause list then runs four, not three) stays a line on the face;
	GRANT and REFUSE each lead their figures as badges, and LAPSE is one short
	badge. The sentences themselves are the buttons' hover."""
	var out := ""
	for i in range(maxi(clauses.size() - 3, 0)):
		out += "  - %s\n" % str(clauses[i])
	out += _figure_row("grant", grant_figs, Utils.COLOR_GOLD)
	out += _figure_row("refuse", refuse_figs, Utils.COLOR_ERROR)
	out += _figure_row("lapse", ["a lapse is a refusal"], Utils.COLOR_INFO)
	return out


func _figure_row(label: String, figures: Array, tone_hex: String) -> String:
	var row := "[color=#" + tone_hex + "][b][opentype_features=smcp]" + label \
		+ "[/opentype_features][/b][/color]  "
	var badges: Array = []
	for fig in figures:
		badges.append(Utils.bb_badge(str(fig), tone_hex))
	return row + " ".join(badges) + "\n"


func show_proposal(data: Dictionary):
	"""Display incoming proposal popup."""
	if not _silent_rebuild:
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
	# Session UI-3 (November 12, 2026): the petition's three dense sentences fold
	# to two rows of FIGURES (GRANT / REFUSE) and a lapse badge when the payload
	# carries them (`grant_figures` / `refuse_figures`, from the one pricing
	# function); the sentences ride the buttons' hover. A payload without the
	# figures (an older save), or Explanations On the page, prints the clause
	# lines as before — no word is lost.
	var grant_figs: Array = []
	var refuse_figs: Array = []
	if data.get("grant_figures", []) is Array:
		grant_figs = data.get("grant_figures", [])
	if data.get("refuse_figures", []) is Array:
		refuse_figs = data.get("refuse_figures", [])
	var figure_mode: bool = bool(is_petition) and Utils.explanations_folded() \
		and not grant_figs.is_empty() and not refuse_figs.is_empty() \
		and clauses is Array and clauses.size() >= 3
	# a note opened on the last letter must not stand open on the next
	for _note_id in [NOTE_PETITION, NOTE_ASSESSMENT]:
		if Utils.note_is_open(_note_id):
			Utils.toggle_note(_note_id)
	# DDB-2 (DDB-D8): an ally's call to arms — joined or refused, never
	# bargained; its price and its two-turn deadline are on the letter.
	var is_call_to_arms = data.get("is_call_to_arms", false)
	# S14c (docs/EVENTS_SPEC.md §6): a moment of history — an authored letter
	# of the record with no court; the Cabinet (or Talleyrand) lays it before
	# the Emperor. Two answers, each saying what it does; no Counter.
	var is_moment = data.get("is_moment", false)
	# RE-2 (§12b.2): a letter of state carries its counsel under the buttons
	# (`_dress_letter`); the grey assessment slot is skipped for this register.
	if is_moment:
		assessment = ""
	# OCT27-D9 (S14i): an allied court asks for its home province back —
	# Return or Keep, never bargained (the Counter rides hidden).
	var is_province_letter = data.get("is_province_letter", false)
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
		# RE-2 (RECURRING_EVENTS_SPEC.md §12b.2, line 2): the writer and the
		# office, named — "The Host's Claims — Montgelas, for the court of
		# Munich"; a payload without a writer reads as S14c wrote it. The
		# header line above is lifted into the letterhead by `_dress_letter`,
		# which reads the letter's own `header` (an affair's says so).
		var writer := _moment_text(data.get("writer", ""))
		if writer != "":
			var office := _moment_text(data.get("office", ""))
			bbcode += "[b]" + _moment_text(data.get("title", "")) + "[/b] — " + writer + ((", " + office) if office != "" else "") + "\n"
		else:
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
	elif figure_mode:
		bbcode += _petition_figure_rows(clauses, grant_figs, refuse_figs)
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

	# Session UI-3: Talleyrand's reading opens from its first sentence (a note;
	# On the page it is the grey line it was). The slot is filled by
	# `_render_body` — a note toggle re-sets ONLY the body, never the dress.
	_assessment_text = str(assessment) if assessment else ""
	_assessment_id = NOTE_PETITION if is_petition else NOTE_ASSESSMENT
	bbcode += ASSESS_SLOT

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

	# S14G-6 (Pre-Deploy S14h part 1, October 26, 2026): the lock in the
	# letter's BODY — a letter that shuts the Cabinet while it stands says so
	# where it is read (the backend's `locks_cabinet`; a moment letter and a
	# lesser court's routine letter never do), in the one sentence every
	# surface uses (`Utils.cabinet_shut_line`, set to start a sentence).
	var locks_cabinet: bool = bool(data.get("locks_cabinet", false)) and not bool(is_moment)
	if locks_cabinet:
		var body_lock_turn: int = int(data.get("answer_by_turn", 0)) if is_call_to_arms else 0
		bbcode += "\n[color=#" + Utils.COLOR_WARNING + "]" + Utils.cabinet_shut_sentence(body_lock_turn) + "[/color]"

	# Backend prose (clause strings, court rationale, hints) can embed raw
	# multi-word nation keys — humanize once at the render chokepoint. S12:
	# through `text`, never append_text (the instrument reads the label's text).
	_body_template = bbcode
	_render_body()

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
	# AU-3a (AUTHORITY_CURRENCY_SPEC.md §5.3): an Edict letter's third answer,
	# "Decree it", rides the Counter's slot — a moment letter is answered,
	# never bargained, so the slot is free there. Captioned, quoted, and closed
	# with the backend's stamped reason (the Accept's own shape).
	_is_decree_letter = is_moment and not _moment_answer(data, "decree_ai_proposal").is_empty()
	if _is_decree_letter:
		var decree_opt := _decree_option(data)
		var decree_reason := str(decree_opt.get("reason", ""))
		counter_btn.visible = true
		counter_btn.disabled = not bool(decree_opt.get("enabled", true))
		counter_btn.text = _moment_caption(data, "decree_ai_proposal", "Decree it")
		counter_btn.tooltip_text = decree_reason if counter_btn.disabled and decree_reason != "" \
			else _moment_quote(data, "decree_ai_proposal")
	# AU-16: the third answer sits third on the row, as in the letter's list, so
	# "its second answer" (the one a lapse takes) is the Decline on the buttons
	# too; every other register keeps the Counter between Accept and Reject.
	var answer_row: Node = counter_btn.get_parent()
	if _is_decree_letter and counter_btn.get_index() < reject_btn.get_index():
		answer_row.move_child(counter_btn, reject_btn.get_index())
	elif not _is_decree_letter and counter_btn.get_index() > reject_btn.get_index():
		answer_row.move_child(counter_btn, reject_btn.get_index())
	reject_btn.disabled = false
	dismiss_btn.disabled = false
	dismiss_btn.text = NOT_NOW_LABEL
	_set_aside_line.visible = false
	# S14E-18 (S14f part 2): a set-aside letter still stands, and while it does
	# the Cabinet stays shut — said on the button that does it, in the sentence
	# the echo and the locked Cabinet use. A moment letter locks nothing; a call
	# to arms stands to its answer-by turn.
	# S14G-6 / S14G-D3 (Pre-Deploy S14h part 1, October 26, 2026): ...but only
	# a letter that LOCKS says it. A great court's letter, an ultimatum or a war
	# decision puts it on the button's face ("Not Now (Cabinet stays shut)") and
	# on a line under the buttons; a lesser court's routine letter says it waits
	# in the mailbox and the Cabinet stays open (it used to claim a lock it
	# did not have to keep).
	if is_moment:
		dismiss_btn.tooltip_text = "Set this letter aside. The envoy badge reopens it."
	else:
		var _lock_by_turn := int(data.get("answer_by_turn", 0)) if is_call_to_arms else 0
		if locks_cabinet:
			dismiss_btn.text = NOT_NOW_LOCKED_LABEL
			dismiss_btn.tooltip_text = "Set this letter aside — " + Utils.cabinet_shut_line(_lock_by_turn) + " The envoy badge reopens it."
			_set_aside_line.text = SET_ASIDE_LOCKED_PREFIX + Utils.cabinet_shut_line(_lock_by_turn)
			_set_aside_line.add_theme_color_override("font_color", Utils.UI_WARNING)
		else:
			dismiss_btn.tooltip_text = "Set this letter aside — it waits in the mailbox and the Cabinet stays open. The envoy badge reopens it."
			_set_aside_line.text = SET_ASIDE_WAITS_LINE
			_set_aside_line.add_theme_color_override("font_color", Utils.toned(Utils.UI_TEXT_DIM))
		_set_aside_line.visible = true
	# Button labels adapt to context. S14I-3: the Reject tooltip is set per
	# letter below (a moment's quote, a province letter's price) — cleared
	# first, or it lingered on the next letter's Reject.
	reject_btn.tooltip_text = ""
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
	elif is_province_letter:
		# Captions only — the buttons emit the router's "accept" / "reject";
		# the refusal's price is on the letter and on the button's tooltip.
		accept_btn.text = "Return"
		reject_btn.text = "Keep"
		reject_btn.tooltip_text = str(data.get("keep_line", ""))
	else:
		accept_btn.text = "Accept Terms" if is_counter else "Accept"
		reject_btn.text = "Reject Terms" if is_counter else "Reject"
	# Session UI-3: a folded petition's options say what they do on the
	# buttons' hover (the sentences left the face for the figure rows).
	if figure_mode:
		var n_cl: int = clauses.size()
		Utils.explain_tip(accept_btn, str(clauses[n_cl - 3]), accept_btn.tooltip_text)
		Utils.explain_tip(reject_btn, str(clauses[n_cl - 2]), reject_btn.tooltip_text)
		Utils.explain_tip(dismiss_btn, str(clauses[n_cl - 1]), dismiss_btn.tooltip_text)
	# RE-2 (RECURRING_EVENTS_SPEC.md §12b.2): the letter's dress — the sheet,
	# the ink, the letterhead, the two-line buttons, the counsel — over the
	# composed letter; every override removed again for any other register.
	_dress_letter(data, is_moment, grant_enabled, grant_reason)
	show()
	# July 18, 2026 viewport sweep: fit to the CURRENT logical viewport.
	# Interface Scale (content_scale_factor, up to 2.0) divides the logical
	# viewport, so a fixed authored rect can carry the action row off-screen
	# and leave a modal undismissable. The helper is a no-op wherever the
	# panel already fits, and returns early for non-centre-anchored panels.
	# PC-F46: the ceiling it fits UNDER grows with the window first.
	_raise_letter_ceiling()
	Utils.clamp_centered_panel($PanelContainer)
	_fit_to_letter()


func _fit_to_letter() -> void:
	"""Session UI-2 (November 11, 2026): the box fits what it holds. The clamp
	sets it to the whole PC-F46 ceiling (80 % of the window), and a short
	letter or a client's petition stood over half a sheet of nothing above its
	answers (the blind readers' "void"). Two frames after the clamp (a
	wrapping label has no height before it has a width), the body asks for
	its own height — capped at the room the clamped box leaves it, so a long
	armistice letter still scrolls under its answers — and the panel shrinks
	to its content (the objection and capture popups' helper)."""
	await get_tree().process_frame
	await get_tree().process_frame
	if not visible or not is_instance_valid(content_label):
		return
	var panel := $PanelContainer as Control
	var have: float = panel.offset_bottom - panel.offset_top
	content_label.custom_minimum_size.y = 0.0
	var others: float = panel.get_combined_minimum_size().y
	var body_h := float(content_label.get_content_height()) + 6.0
	content_label.custom_minimum_size.y = clampf(body_h, 72.0, maxf(have - others, 72.0))
	Utils.shrink_centered_panel_to_content(panel)


func _raise_letter_ceiling() -> void:
	"""PC-F46 (S15 head, October 25, 2026): the letter's box GROWS with the
	window. The authored 680 x 440 stood unchanged at 1920 x 1080 and at
	5120 x 1440 (3657 x 1028 logical at 140 %), where a third of the screen
	was the letter and 640 px of its 966 sat under a scroll — the truce's
	cost below the fold, under Accept. The clamp's ceiling (the IGR-G1 meta
	every other surface raises the same way) is now a fraction of the logical
	viewport — its height `LETTER_HEIGHT_FRACTION`, its width
	`LETTER_WIDTH_FRACTION` to a reading measure of `LETTER_MAX_WIDTH`; the
	authored rect stays the floor, so a small window (Interface Scale 2.0:
	800 x 450) is fitted exactly as before. The clamp still keeps the panel
	under the bar and inside the window, and the answers stand under the
	scroll, never in it."""
	var view := get_viewport().get_visible_rect().size
	$PanelContainer.set_meta("clamp_ceiling_override", Vector2(
			clampf(view.x * LETTER_WIDTH_FRACTION, LETTER_MIN_WIDTH, LETTER_MAX_WIDTH),
			maxf(view.y * LETTER_HEIGHT_FRACTION, LETTER_MIN_HEIGHT)))


func refit() -> void:
	"""The live-refit road's hook (`Utils.refit_surface`, run by
	`main._on_root_resized` on a window resize or an Interface Scale change):
	an open letter follows the window, not only the window it opened in."""
	_raise_letter_ceiling()
	Utils.clamp_centered_panel($PanelContainer)
	_fit_to_letter()


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


func _decree_option(data: Dictionary) -> Dictionary:
	"""AU-3a: the letter's stamped Decree option (`enabled` / `reason`)."""
	var opts = data.get("options", [])
	if opts is Array:
		for opt in opts:
			if opt is Dictionary and str(opt.get("action", "")) == "decree_ai_proposal":
				return opt
	return {}


func _moment_caption(data: Dictionary, action: String, fallback: String) -> String:
	var caption := str(_moment_answer(data, action).get("caption", ""))
	return caption if caption != "" else fallback


func _moment_quote(data: Dictionary, action: String) -> String:
	return str(_moment_answer(data, action).get("quote", ""))


func _build_moment_body(data: Dictionary) -> String:
	"""S14c (docs/EVENTS_SPEC.md §2's copy contract): the record, the board
	(derived lines), then what each answer does — the plan's own quotes, the
	caption in bold. The unanswered line is the footer.

	RE-2 (RECURRING_EVENTS_SPEC.md §12b.2): the first-open line in sepia;
	the writer's own line (`line`) before the record; the ground and the
	chapter in IM Fell italic — history's voice, set apart from the writer's
	(`[font=…]` parses; the file name carries no bracket; IM Fell has no
	arrow or minus glyph, so it is scoped to the record and the exhibit);
	the exhibit (RE-H's) in IM Fell roman under a run-in in the rubric; the
	board led by a fleuron; the heading in the rubric. The body ink is laid
	over the whole by `_dress_letter`."""
	var out := ""
	# S14d: the sixth part of the copy contract (EVENTS_SPEC §2, A5) — the
	# first letter's line, before the record, in the R159 register.
	var fo = data.get("first_open")
	if fo is Dictionary and str(fo.get("line", "")) != "":
		out += "[color=#" + Utils.INK_SEPIA + "]" + _moment_text(fo.get("line", "")) + "[/color]\n"
		first_open_seen.emit(str(fo.get("screen", "moment_letter")))
	var writer_line := _moment_text(data.get("line", ""))
	if writer_line != "":
		out += writer_line + "\n"
	var record := _moment_text(data.get("record", ""))
	if record != "":
		out += "[font=" + LETTER_FELL_ITALIC + "]" + record + "[/font]\n"
	var exhibit := _moment_text(data.get("exhibit", ""))
	if exhibit != "":
		var exhibit_from := _moment_text(data.get("exhibit_from", EXHIBIT_FROM_DEFAULT))
		out += "[color=#" + Utils.INK_RUBRIC + "]" + exhibit_from.to_upper() + "[/color]\n"
		out += "[font=" + LETTER_FELL_ROMAN + "]" + exhibit + "[/font]\n"
	var board = data.get("board", [])
	if board is Array:
		for line in board:
			# the hedera (U+2767) — EB Garamond's own fleuron, in the rubric;
			# a glyph scales with the type where a 10-px image aliased
			out += "[color=#" + Utils.INK_RUBRIC + "]" + LETTER_FLEURON + "[/color] " + _moment_text(line) + "\n"
	var answers = data.get("answers", [])
	if answers is Array and answers.size() > 0:
		out += "[color=#" + Utils.INK_RUBRIC + "][b]" + "What each answer does".to_upper() + "[/b][/color]\n"
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
	# RE-2: the beat draws at the pressed button's rect once the popup is gone
	_pressed_rect = accept_btn.get_global_rect()
	_disable_buttons()
	hide()
	choice_made.emit("accept", current_data)

func _on_counter():
	if _is_decree_letter:
		# AU-3a: the slot answers the letter with its third answer
		_pressed_rect = counter_btn.get_global_rect()
		_disable_buttons()
		hide()
		choice_made.emit("decree", current_data)
		return
	_disable_buttons()
	hide()
	choice_made.emit("counter", current_data)

func _on_reject():
	_pressed_rect = reject_btn.get_global_rect()
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

# S14G-X109: one counter-offer line the diff MARKED - what the court struck, added
# or cut. The backend writes them (`display_names._counter_offer_parts`): "Struck ...",
# "Added by <court>: ...", "Cut by <court>: ...", and, for a caller that names no
# reader, "Added: ..." / "Cut: ...". The prefixes are exact, so a plain term whose
# label starts with the same letters ("Cutoff", "Addition") is not a change line.
func _is_counter_change_line(line: String) -> bool:
	for prefix in ["Struck", "Added by ", "Added: ", "Cut by ", "Cut: "]:
		if line.begins_with(prefix):
			return true
	return false


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
		# S14G-X109 (Pre-Deploy S14h part 2, October 26, 2026): the same beneath
		# for what the court ADDED or CUT ("Added by Bavaria: you pay 100 gold
		# more (242 at the signing)") - the annotated preview draws the counter's
		# terms with nothing marked new, and only "Struck" lines were caught.
		if bool(data.get("is_counter_offer", false)):
			for clause in clauses:
				if _is_counter_change_line(str(clause)):
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

	# PC-F46 (S15 head, October 25, 2026): THE CONSEQUENCES LEAD. What the
	# letter costs and how it ends — the truce's keeps, its expiry rule (the
	# -60 line), the projection at expiry (-65), the cure; then the political
	# consequences — stood 640 px down, under Accept, behind the whole War
	# Summary (the reader had to scroll past the war to learn what accepting
	# does). They stand above the summary now; the box grows besides
	# (`_raise_letter_ceiling`).
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
			# S14G-X52 (Pre-Deploy S14h part 1, October 26, 2026): the truce's
			# `war_runs_on` row (WARNING) sorts beside HARD_STOP — see the
			# confirm popup's conflict loop.
			if conflict is Dictionary and str(conflict.get("conflict_type", "")) == "war_runs_on":
				conflict_priority = 0
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


# ═══════════════════════════════════════════════════════════════════════════
# RE-2 (docs/RECURRING_EVENTS_SPEC.md §12b.2, October 31, 2026): THE LETTER'S
# DRESS — one register for every letter of state (`is_moment`: the four
# moments, the affairs, the Edicts' offers), gated in `show_proposal`; every
# other letter keeps the flat navy panel. Built in code (the .tscn is
# untouched): the parchment sheet, the ink, the letterhead row at the VBox's
# head (the device · the dateline · the seal well), the two-line buttons, the
# opaque disabled plaque, the counsel under the buttons, and the answer beat's
# own slip. The quote is never traded for ornament: every part the S14c
# register wrote is still written, in ink.
#
# The type stays on the ruled ladder (tests/test_uxr2_override_diet.py): no
# `[font_size=]`, no size override — the body 16, the dateline Caption, the
# apostille Lead; a bbcode `[font=…]` is allowed (IM Fell for history's
# voice). Every inline colour this register emits is a `Utils.INK_*`.
# ═══════════════════════════════════════════════════════════════════════════
const LETTER_SHEET := "res://assets/textures/old-parchment_alpha.png"
const LETTER_SEAL := "res://assets/ui/ornaments/wax_seal.png"
const LETTER_FLEURON := "❧"       # the hedera, U+2767 — EB Garamond carries it (the body face)
const LETTER_FELL_ITALIC := "res://assets/fonts/IMFeENit28P.ttf"
const LETTER_FELL_ROMAN := "res://assets/fonts/IMFeENrm28P.ttf"
const LETTER_CINZEL := "res://assets/fonts/Cinzel[wght].ttf"
const LETTER_DEVICE_PX := 44.0
const LETTER_BUTTON_MIN_HEIGHT := 56.0
const LETTER_BUTTON_LINE_MAX := 40
const LETTER_BEAT_SECONDS := 0.8
const LETTER_SEAL_PX := 48.0
const NOT_NOW_DESK_LINE := "waits on the desk"
const EXHIBIT_FROM_DEFAULT := "FROM HAITI —"

# Instance-held Resources (never a `static var`: S14E-X207 — a static holding
# a Resource outlives the engine's teardown check).
var _sheet: StyleBoxTexture = null
var _sheet_hc: StyleBoxFlat = null
var _closed_plaque: StyleBoxFlat = null
var _fell_italic: Font = null
var _cinzel: Font = null
var _letterhead: HBoxContainer = null
var _device_slot: CenterContainer = null
var _dateline_label: Label = null
var _seal_well: Panel = null
var _pressed_rect := Rect2()
var _dressed := false
var _plain_variation := {}   # Session UI-2: each answer's own step off the sheet
var _is_decree_letter := false   # AU-3a: the letter's third answer rides the Counter's slot


func _ensure_letter_dress() -> void:
	"""The dress's nodes and resources, built once on the first letter of state."""
	if _letterhead != null:
		return
	_sheet = StyleBoxTexture.new()
	_sheet.texture = load(LETTER_SHEET)
	# the torn rim drawn OUTSIDE the box (expand), the inner field stretched
	# (texture margins), the content margin kept at the flat box's 24
	for side in ["left", "right"]:
		_sheet.set("texture_margin_" + side, 48.0)
		_sheet.set("expand_margin_" + side, 12.0)
		_sheet.set("content_margin_" + side, 24.0)
	for side in ["top", "bottom"]:
		_sheet.set("texture_margin_" + side, 40.0)
		_sheet.set("expand_margin_" + side, 12.0)
		_sheet.set("content_margin_" + side, 24.0)
	# High contrast: a flat cream sheet under the same ink (the ink IS the
	# contrast; `Utils.contrast_node` raises mid greys only, never ink)
	_sheet_hc = StyleBoxFlat.new()
	_sheet_hc.bg_color = Color.html(Utils.INK_SHEET_HC)
	_sheet_hc.border_color = Color.html(Utils.INK_RULE)
	_sheet_hc.set_border_width_all(2)
	_sheet_hc.set_corner_radius_all(4)
	_sheet_hc.set_content_margin_all(24.0)
	# the opaque plaque under a closed Accept (the theme's translucent one
	# reads 1.7 : 1 on paper)
	_closed_plaque = StyleBoxFlat.new()
	# Session UI-2: an opaque, darker vellum under a sepia rule — closed, and
	# still of the paper (the navy plaque read as a slab on the sheet).
	_closed_plaque.bg_color = Color.html(Utils.INK_SHEET_HC).darkened(0.14)
	_closed_plaque.border_color = Color.html(Utils.INK_RULE)
	_closed_plaque.set_border_width_all(1)
	_closed_plaque.set_corner_radius_all(4)
	_closed_plaque.set_content_margin_all(6.0)
	_fell_italic = load(LETTER_FELL_ITALIC)
	var cinzel_file: Font = load(LETTER_CINZEL)
	var spaced := FontVariation.new()
	spaced.base_font = cinzel_file
	spaced.set_spacing(TextServer.SPACING_GLYPH, 1)
	_cinzel = spaced
	# the letterhead: device · dateline · seal well, at the VBox's head
	_letterhead = HBoxContainer.new()
	_letterhead.name = "Letterhead"
	_letterhead.add_theme_constant_override("separation", 12)
	_letterhead.visible = false
	_device_slot = CenterContainer.new()
	_device_slot.custom_minimum_size = Vector2(LETTER_DEVICE_PX, LETTER_DEVICE_PX)
	_device_slot.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_letterhead.add_child(_device_slot)
	_dateline_label = Label.new()
	_dateline_label.theme_type_variation = &"Caption"
	_dateline_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_dateline_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_dateline_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_dateline_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_dateline_label.add_theme_font_override("font", _cinzel)
	_dateline_label.add_theme_color_override("font_color", Color.html(Utils.INK_RUBRIC))
	_letterhead.add_child(_dateline_label)
	# the seal well: a faint wax-red ring (a bordered round Panel)
	_seal_well = Panel.new()
	_seal_well.custom_minimum_size = Vector2(LETTER_DEVICE_PX, LETTER_DEVICE_PX)
	_seal_well.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var ring := StyleBoxFlat.new()
	ring.bg_color = Color(0, 0, 0, 0)
	ring.border_color = Color(Color.html(Utils.INK_RUBRIC), 0.35)
	ring.set_border_width_all(1)
	ring.set_corner_radius_all(int(LETTER_DEVICE_PX / 2.0))
	_seal_well.add_theme_stylebox_override("panel", ring)
	_letterhead.add_child(_seal_well)
	var vbox := $PanelContainer/VBoxContainer
	vbox.add_child(_letterhead)
	vbox.move_child(_letterhead, 0)


func _set_letter_device(device: Dictionary) -> void:
	"""The letterhead's device: the court's arms (`Utils.nation_flag_path`),
	the owner's sheet for the Secretariat, a gold monogram on leather for an
	office (`PortraitLocket`'s own fallback — never a portrait)."""
	for child in _device_slot.get_children():
		child.queue_free()
	var kind := str(device.get("kind", ""))
	var nation := str(device.get("nation", ""))
	var flag := Utils.nation_flag_path(nation) if nation != "" else ""
	if kind in ["arms", "sheet"] and flag != "":
		var arms := TextureRect.new()
		arms.texture = load(flag)
		arms.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		arms.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		arms.custom_minimum_size = Vector2(LETTER_DEVICE_PX, LETTER_DEVICE_PX)
		arms.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_device_slot.add_child(arms)
		return
	var letter := str(device.get("letter", ""))
	if letter == "":
		letter = "N"
	var locket := PortraitLocket.new()
	# the letter itself is the name key: no portrait file carries it, so the
	# locket draws its gold monogram on leather (its own fallback)
	locket.setup(letter, LETTER_DEVICE_PX, false)
	_device_slot.add_child(locket)


func _letter_header_text(data: Dictionary) -> String:
	var header := str(data.get("header", ""))
	if header != "":
		return header
	return "A MOMENT OF HISTORY — " + str(data.get("dateline", "")).to_upper()


func _ink(text: String) -> String:
	"""Every inline colour the register wrote, remapped to ink: the first-open
	line's grey to sepia; the closed-Accept line, the gold header line and the
	unanswered line to the rubric; the grey assessment slot is skipped for
	this register (the counsel rides under the buttons)."""
	var out := text
	out = out.replace("[color=#" + Utils.COLOR_INFO + "]", "[color=#" + Utils.INK_SEPIA + "]")
	out = out.replace("[color=#" + Utils.COLOR_ERROR + "]", "[color=#" + Utils.INK_RUBRIC + "]")
	out = out.replace("[color=#e0c060]", "[color=#" + Utils.INK_RUBRIC + "]")
	out = out.replace("[color=#" + Utils.COLOR_WARNING + "]", "[color=#" + Utils.INK_RUBRIC + "]")
	out = out.replace("[color=#" + Utils.COLOR_GOLD + "]", "[color=#" + Utils.INK_RUBRIC + "]")
	out = out.replace("[color=gray]", "[color=#" + Utils.INK_SEPIA + "]")
	return out


func _button_second_line(data: Dictionary, key: String, fallback: String) -> String:
	var line := str(data.get(key, "")).strip_edges()
	if line == "":
		line = fallback
	if line.length() > LETTER_BUTTON_LINE_MAX:
		line = line.substr(0, LETTER_BUTTON_LINE_MAX - 1).strip_edges() + "…"
	return line


func _dress_letter(data: Dictionary, is_letter: bool, accept_open: bool, accept_reason: String) -> void:
	"""The dress, applied after the body is composed and the buttons are
	captioned; every override removed again for any other register."""
	var panel := $PanelContainer
	var buttons := [accept_btn, counter_btn, reject_btn, dismiss_btn]
	if not is_letter:
		_dressed = false
		if _letterhead != null:
			_letterhead.visible = false
		panel.add_theme_stylebox_override("panel", panel_style)
		accept_btn.remove_theme_stylebox_override("disabled")
		counter_btn.remove_theme_stylebox_override("disabled")
		content_label.remove_theme_color_override("default_color")
		for b in buttons:
			b.custom_minimum_size = Vector2(140, 45)
			b.theme_type_variation = _plain_variation.get(b.name, &"")
		_set_aside_line.remove_theme_font_override("font")
		return
	_ensure_letter_dress()
	_dressed = true
	panel.add_theme_stylebox_override("panel", _sheet_hc if UiSettings.get_high_contrast() else _sheet)
	_letterhead.visible = true
	_set_letter_device(data.get("device", {}))
	_dateline_label.text = _letter_header_text(data)
	# the header line leaves the body for the letterhead; the rest is inked
	var body: String = content_label.text
	if body.begins_with("[center]"):
		var head_end := body.find("\n")
		body = body.substr(head_end + 1) if head_end >= 0 else ""
	content_label.text = "[color=#" + Utils.INK_BODY + "]" + _ink(body) + "[/color]"
	# Session UI-2: the label's own colour is the ink too (a span without its
	# colour tag would otherwise draw white on the paper — the contrast census
	# read every letter's label so).
	content_label.add_theme_color_override("default_color", Color.html(Utils.INK_BODY))
	# the two-line buttons: the caption, then the price (the plan's receipt)
	for b in buttons:
		b.custom_minimum_size = Vector2(140, LETTER_BUTTON_MIN_HEIGHT)
		# Session UI-2: ink on vellum — paper-native answers on the sheet
		if not _plain_variation.has(b.name):
			_plain_variation[b.name] = b.theme_type_variation
		b.theme_type_variation = &"ParchmentButton"
	var accept_line := _button_second_line(data, "button_accept", "no change")
	if not accept_open:
		# a closed Accept says why on an opaque plaque (the reason when it
		# fits the line, else its price; the body's line carries the whole)
		var reason := accept_reason.strip_edges().rstrip(".")
		if reason != "" and reason.length() <= LETTER_BUTTON_LINE_MAX:
			accept_line = reason
		accept_btn.add_theme_stylebox_override("disabled", _closed_plaque)
	else:
		accept_btn.remove_theme_stylebox_override("disabled")
	accept_btn.text = accept_btn.text + "\n" + accept_line
	if _is_decree_letter:
		# AU-3a: the Decree's price line; closed, its reason on the opaque plaque
		var decree_line := _button_second_line(data, "button_decree", "no change")
		if counter_btn.disabled:
			var decree_reason := str(_decree_option(data).get("reason", "")).strip_edges().rstrip(".")
			if decree_reason != "" and decree_reason.length() <= LETTER_BUTTON_LINE_MAX:
				decree_line = decree_reason
			counter_btn.add_theme_stylebox_override("disabled", _closed_plaque)
		else:
			counter_btn.remove_theme_stylebox_override("disabled")
		counter_btn.text = counter_btn.text + "\n" + decree_line
	else:
		counter_btn.remove_theme_stylebox_override("disabled")
	reject_btn.text = reject_btn.text + "\n" + _button_second_line(data, "button_decline", "no change")
	dismiss_btn.text = dismiss_btn.text + "\n" + NOT_NOW_DESK_LINE
	# the counsel under the buttons: Caption italic in sepia, never a body line
	var counsel := _moment_text(data.get("counsel", ""))
	if counsel != "":
		_set_aside_line.text = counsel
		_set_aside_line.add_theme_font_override("font", _fell_italic)
		_set_aside_line.add_theme_color_override("font_color", Color.html(Utils.INK_SEPIA))
		_set_aside_line.visible = true
	else:
		_set_aside_line.remove_theme_font_override("font")
		_set_aside_line.visible = false


func play_answer_beat(answer_key: String, parent: Node) -> void:
	"""RE-2 (§12b.2) — the answer's beat, under 0.8 s, on the backend's own
	word that the letter was answered (`moment_answered`; a refusal carries
	`diplomatic_dialogue` instead and never reaches here): the popup is
	already hidden, so the apostille and the seal draw on a parchment slip of
	their own, parented under an existing layer the caller hands in (main.gd's
	scale card layer 125, above every dialog — RE5-3: under the top bar's 75 a
	court's envoy promoted into this popup on the same response covered the
	seal; the top bar is the fallback; never a `CanvasLayer.new()`), at the
	pressed button's rect: the apostille fades in
	("{caption}. — N."), the seal presses with a 6° settle under a gold N
	cipher, the `wax_seal` cue plays once; then the slip frees itself. Not
	Now never reaches here (no slip, no seal, no sound)."""
	if parent == null or not is_instance_valid(parent) or not (parent is Node):
		return
	if not bool(current_data.get("is_moment", false)):
		return
	var action := "accept_ai_proposal" if answer_key == "accept" else "reject_ai_proposal"
	if answer_key == "decree":
		action = "decree_ai_proposal"   # AU-3a: the Decree seals as an Accept does
	var caption := _moment_caption(current_data, action, "")
	if caption == "":
		return
	_ensure_letter_dress()
	var slip := PanelContainer.new()
	slip.name = "AnswerBeatSlip"
	slip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	slip.add_theme_stylebox_override("panel", _sheet_hc if UiSettings.get_high_contrast() else _sheet)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 12)
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	slip.add_child(row)
	var apostille := Label.new()
	apostille.theme_type_variation = &"Lead"
	apostille.text = caption + ". — N."
	apostille.add_theme_font_override("font", _fell_italic)
	apostille.add_theme_color_override("font_color", Color.html(Utils.INK_BODY))
	apostille.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	apostille.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_child(apostille)
	var seal_box := Control.new()
	seal_box.custom_minimum_size = Vector2(LETTER_SEAL_PX, LETTER_SEAL_PX)
	seal_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_child(seal_box)
	var seal := TextureRect.new()
	seal.texture = load(LETTER_SEAL)
	seal.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	seal.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	seal.set_anchors_preset(Control.PRESET_FULL_RECT)
	seal.pivot_offset = Vector2(LETTER_SEAL_PX / 2.0, LETTER_SEAL_PX / 2.0)
	seal.mouse_filter = Control.MOUSE_FILTER_IGNORE
	seal_box.add_child(seal)
	var cipher := Label.new()
	cipher.theme_type_variation = &"Lead"
	cipher.text = "N"
	cipher.add_theme_font_override("font", _cinzel)
	cipher.add_theme_color_override("font_color", Utils.UI_GOLD_BRIGHT)
	cipher.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	cipher.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	cipher.set_anchors_preset(Control.PRESET_FULL_RECT)
	cipher.mouse_filter = Control.MOUSE_FILTER_IGNORE
	seal.add_child(cipher)
	parent.add_child(slip)
	# at the pressed button, kept inside the window
	var view := get_viewport().get_visible_rect().size
	slip.reset_size()
	var at := _pressed_rect.position + Vector2(0, -8.0)
	if _pressed_rect.size == Vector2.ZERO:
		at = (view - slip.size) / 2.0
	at.x = clampf(at.x, 8.0, maxf(8.0, view.x - slip.size.x - 8.0))
	at.y = clampf(at.y, 8.0, maxf(8.0, view.y - slip.size.y - 8.0))
	slip.position = at
	slip.modulate.a = 0.0
	seal.rotation_degrees = -6.0
	seal.scale = Vector2(1.3, 1.3)
	AudioManager.play("wax_seal", 1.4)
	var tw := slip.create_tween()
	tw.tween_property(slip, "modulate:a", 1.0, 0.15)
	tw.parallel().tween_property(seal, "rotation_degrees", 0.0, 0.25)
	tw.parallel().tween_property(seal, "scale", Vector2.ONE, 0.25).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tw.tween_interval(LETTER_BEAT_SECONDS - 0.4)
	tw.tween_property(slip, "modulate:a", 0.0, 0.25)
	tw.tween_callback(slip.queue_free)
