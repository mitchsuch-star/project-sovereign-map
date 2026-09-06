extends CanvasLayer

# =============================================================================
# INK & IRON — THE SCHOOL OF WAR (POSITION 7 tutorial overlay)
# =============================================================================
# Berthier's tutor card for the Danube Lesson (tutorial_1805.json). A
# NON-MODAL CanvasLayer at 90: above the layer-50 screens and the TopBar (75)
# so the card survives the ledger opening, UNDER the 101+ modal band so an
# objection popup draws over it. Registered modal=false — a modal
# registration would block ESC/pause, hide the war HUD and block hotkeys.
#
# OBSERVE-ONLY DISCIPLINE (the NA-6b lesson): main.gd hands every backend
# response to observe() from the stash-first block of _on_command_result and
# from _on_interrupt_response. This overlay never routes, never blocks, and
# NEVER sends a command — the suggest chip FILLS the command line via the
# suggest_command signal (muscle memory for a typed-command game; main.gd
# owns the LineEdit). It must never become a _post_hud_response_routes entry
# (the documented end-turn-tail soft-lock, main.gd).
#
# ARMING: on_world_swap() reads game_state.scenario_name — exactly "tutorial"
# arms the card (unless UiSettings.get_tutorial_done()). The current step is
# DERIVED from game_state.turn (turn_gate), never stored: a mid-lesson reload
# resumes at the turn's first step. Completion/skip latches per-machine via
# UiSettings.set_tutorial_done.
#
# ADVANCE RULE: at most ONE step per observed response; a step whose event
# passed unseen (the player ran ahead) is released by the turn-gate catch-up
# so the school can never stall. A step the WAR refuses (Aug 8 live report:
# Austria's reserve massed in Bohemia while IX demanded its capture) releases
# the same way — and once overdue the card SAYS so, re-rendering on turn
# change (TUT-F4c). Choice popups DEFER past enemy_phase responses (backend
# main.py) — no predicate requires a popup key and enemy_phase in the same
# response.
#
# No timers of any kind (pulses are tweens); the SceneTreeTimer ban that is
# test-pinned for menu code is kept absolute here.
# =============================================================================

signal suggest_command(cmd: String)

const CHIP_TEXT_HEX := "e8d4a8"
const CHIP_BG_HEX := "233043"

# ── the Danube Lesson step table ────────────────────────────────────────────
# {id, turn_gate, title, body, suggest, suggest_action, advance}
# `suggest` is the EXACT string the chip fills into the command line; a
# backend test (test_tutorial_position7.py::test_every_suggest_mock_parses)
# regex-extracts every (suggest, suggest_action) pair and mock-parses it
# against the tutorial world — edit both fields together. suggest "" = no
# chip (e.g. pending-question tokens like insist/plunder never reach the
# parser, so they are named in the body, never chipped).
const STEPS := [
	{
		"id": "survey",
		"turn_gate": 1,
		"title": "I. The Situation",
		"body": "Sire — Austria has pushed two corps over the Iller while her main army musters at Vienna. Before orders, knowledge: every command is TYPED into the line below. Ask the treasury for its books; it costs no action.",
		"suggest": "economy",
		"suggest_action": "economy",
		"advance": "_pred_any_success",
	},
	{
		"id": "first_move",
		"turn_gate": 1,
		"title": "II. The Army Marches",
		"body": "You hold 4 command actions and 2 administrative actions each turn — the counters stand above. A march costs one command action. Send Senarmont's guns forward through allied Bavaria — an ALLIANCE opens the road.",
		"suggest": "Senarmont, move to Munich",
		"suggest_action": "move",
		"advance": "_pred_senarmont_in_munich",
	},
	{
		"id": "first_end_turn",
		"turn_gate": 1,
		"title": "III. The Day Closes",
		"body": "Spend what actions you please, Sire — then close the day. The enemy moves when you have finished, and my morning dispatch reports what changed overnight.",
		"suggest": "end turn",
		"suggest_action": "end_turn",
		"advance": "_pred_turn_advanced",
	},
	{
		"id": "objection",
		"turn_gate": 2,
		"title": "IV. The Marshal's Temper",
		"body": "Your marshals are men, not pieces. Order Ney — who smells the enemy across the border — onto the DEFENSIVE, and hear what the bravest of the brave thinks of that.",
		"suggest": "Ney, defend",
		"suggest_action": "defend",
		"advance": "_pred_objection_pending",
	},
	{
		"id": "objection_answer",
		"turn_gate": 2,
		"title": "V. Trust, Insist, Compromise",
		# FA-N78: the card named three typed tokens for a modal that DISABLES
		# the command line, so the player was told to type words they could
		# not type. The buttons are built at runtime and carry the marshal's
		# name and the trust figures, so only the stable leading words are
		# named here.
		"body": "He objects — as he should. Answer on the card before you: [color=#e8d4a8]Trust[/color] to let him have his way, [color=#e8d4a8]Proceed as Ordered[/color] to be obeyed at a price in trust, or [color=#e8d4a8]Compromise[/color] to meet him halfway. I advise PROCEED AS ORDERED, Sire — the lesson is that command costs something.",
		"suggest": "",
		"suggest_action": "",
		"advance": "_pred_objection_resolved",
	},
	{
		"id": "bombardment",
		# PC15-9: gate 3 -> 2. Jellacic's hold on Tyrol is only guaranteed
		# until Austria reacts to Kienmayer's fate (ambient combat RNG), so
		# the beat opens the FIRST turn the guns can legally fire (marched
		# T1, laid overnight) — two guaranteed turns instead of one.
		"turn_gate": 2,
		"title": "VI. The Guns Speak",
		"body": "Senarmont's batteries at Munich range the Tyrol passes, where Jellacic digs in. Artillery fires one province distant — but never on the day it marched; the guns must be laid. Bombard him while he still holds the pass; Austria rotates her corps within days. Should he slip away first, any enemy corps one province out serves the lesson — or end the turn and the school will move on.",
		"suggest": "Senarmont, bombard Jellacic",
		"suggest_action": "attack",
		"advance": "_pred_bombardment",
	},
	{
		"id": "first_battle",
		"turn_gate": 4,
		"title": "VII. First Blood",
		"body": "Now the sword. Kienmayer's screen still stands across the Rhine on allied Bavarian soil — Ney carries three times their number. Attack, and read the battle report that follows: terrain, casualties, and the temper of the men. Then occupy Swabia ([color=#e8d4a8]Ney, move to Swabia[/color]); if the move is refused, his corps still stands — beaten men must be broken, so strike again before you walk in.",
		"suggest": "Ney, attack Kienmayer",
		"suggest_action": "attack",
		"advance": "_pred_battle_happened",
		# FA-42: the promised "trust branch pivot". Under `trust` Ney attacks
		# on turn 2 and the screen is gone by the time this card is due —
		# measured over 40 trials at a held seed: at large 21, a prisoner 18,
		# absent from the roster 1 — yet the card said "still stands" 12/12
		# and offered a chip the executor refuses.
		#
		# THREE RULES, each one measured:
		#   * The arms live in a nested `alt` dict, AFTER this step's own
		#     "suggest" and carrying no "id:" key. The `alt` re-uses the
		#     "suggest"/"suggest_action" names so T-B1 pins the branch chips
		#     for free; a new key name ships them unpinned, and an "id:"
		#     inside would mint a phantom step for the census in
		#     test_fa_slice8.
		#   * The top-level chip STAYS. A pin asserts that literal string is
		#     in this file, and it is the right pin: the branch is a
		#     variation, not a replacement.
		#   * A second gate-4 STEPS entry is NOT an option — STEPS.size() is
		#     rendered in the badge and _derive_step_for_turn resumes at the
		#     first step of the highest gate, so a mid-lesson reload would
		#     land on the wrong branch.
		"alt": {
			"running": {
				"body": "Now the sword — and Ney has already drawn it. Kienmayer's screen is broken and what is left of it is running; my scouts have not pinned it down. Order the pursuit if you please — if he is beyond our reach the refusal will say so, and it costs you nothing. Then read the battle report he sent up: terrain, casualties, and the temper of the men.",
				"suggest": "Ney, attack Kienmayer",
				"suggest_action": "attack",
			},
			"lost": {
				"body": "Now the sword — and Ney has already drawn it. Kienmayer's screen is broken; where the remnant went my scouts cannot say, and I will not send Ney chasing a rumour. Read the battle report he sent up — terrain, casualties, and the temper of the men — and the school will move on.",
				"suggest": "",
				"suggest_action": "",
			},
			"taken": {
				"body": "Now the sword — and you have already drawn it, Sire. Kienmayer is our prisoner; there is no screen left to break. Read the battle report your marshals sent up — terrain, casualties, and the temper of the men — and hold him for the peace table.",
				"suggest": "",
				"suggest_action": "",
			},
		},
	},
	{
		"id": "strategic_order",
		"turn_gate": 5,
		"title": "VIII. Standing Orders",
		"body": "For distant objectives, give a STANDING order — it costs 2 command actions and executes itself each morning until done. March Davout for Franconia, two provinces east; watch the later legs move without you at dawn (he routes around enemies on his own).",
		"suggest": "Davout, march to Franconia",
		"suggest_action": "move",
		"advance": "_pred_davout_marching",
	},
	{
		"id": "capture",
		"turn_gate": 6,
		"title": "IX. Conquest",
		"body": "Bohemia is Austrian soil, one march past Franconia. When Davout reaches the border, march in and it is yours ([color=#e8d4a8]Davout, move to Bohemia[/color]); if an Austrian corps holds it, the refusal names him — attack that name, and the battle that breaks the last of them hands you the province. Should Austria mass there in strength, any Austrian province serves the lesson — the battered Tyrol will do — or fight your own war and the school will catch up. Capitals are not taken by walking: Munich's fortress holds 10,000, Vienna's 25,000.",
		"suggest": "Davout, move to Bohemia",
		"suggest_action": "move",
		"advance": "_pred_capture_pending",
	},
	{
		"id": "capture_answer",
		"turn_gate": 6,
		"title": "X. The Conqueror's Choice",
		# FA-N78: same lie as card V — the capture modal disables the command
		# line. The button WORDS are right (they are built at runtime as
		# "PLUNDER (…)" / "SECURE (…)"); only "Type" was false.
		"body": "The province is yours, Sire — now choose its fate on the card before you: [color=#e8d4a8]PLUNDER[/color] for gold now and a hostile countryside after, or [color=#e8d4a8]SECURE[/color] for order and income that lasts. On an allied front, I counsel SECURE.",
		"suggest": "",
		"suggest_action": "",
		"advance": "_pred_capture_resolved",
	},
	{
		"id": "recruit_build",
		"turn_gate": 7,
		"title": "XI. The Depots",
		"body": "War eats men and gold. Your 2 ADMINISTRATIVE actions recruit and build: raise infantry for Soult at Paris — the price is war-inflated, the capital discounts it — and spend the second on [color=#e8d4a8]build watchtower in Lorraine[/color] to watch the frontier.",
		"suggest": "Soult, recruit troops",
		"suggest_action": "recruit",
		"advance": "_pred_recruited",
	},
	{
		"id": "free_scout",
		"turn_gate": 8,
		"title": "XII. The Fog",
		"body": "You see only what your armies and towers see. Austria's main body is stirring — scout toward Bohemia and find it before it finds you. From here the school only advises, Sire; the war is yours.",
		"suggest": "Davout, scout Bohemia",
		"suggest_action": "scout",
		"advance": "_pred_turn_gte_9",
	},
	{
		"id": "free_stand",
		"turn_gate": 9,
		"title": "XIII. The Counter-Blow",
		"body": "Charles and Schwarzenberg will come west — fifty thousand of them. Mountains favor the defender; so do earthworks ([color=#e8d4a8]Ney, fortify[/color]) and a garrison detachment. Stand where the ground is strong and let them bleed on it.",
		"suggest": "Ney, fortify",
		"suggest_action": "fortify",
		"advance": "_pred_turn_gte_10",
	},
	{
		"id": "free_books",
		"turn_gate": 10,
		"title": "XIV. The Instruments",
		"body": "Everything I have taught has a screen: [color=#e8d4a8]T[/color] the Strategic Ledger, [color=#e8d4a8]G[/color] your Generals, [color=#e8d4a8]D[/color] the courts of Europe, [color=#e8d4a8]R[/color] my morning dispatch again. The treasury now carries occupation costs and the charges of empire — read them in the ledger. Four more instruments the great campaign will hand you, Sire: the ledger's seventh book is [color=#e8d4a8]THE ADMIRALTY[/color] — fleets, blockades, and the crossings. [color=#e8d4a8]F1[/color] opens the diplomacy wizard, and its Formable Nations button shows what new crowns a settlement can carve. A general's card carries a [color=#e8d4a8]Reward[/color] chip when his service demands payment. And the ledger's Design rows read each court's ambition — the why behind their armies.",
		"suggest": "",
		"suggest_action": "",
		"advance": "_pred_turn_gte_12",
	},
	{
		"id": "handoff",
		"turn_gate": 12,
		"title": "XV. The Lesson Ends",
		"body": "That is the whole of the craft, Sire: orders, temper, battle, conquest, coin — and the courts beyond. The real war of 1805 waits at the main menu under BEGIN. Hold this little front as long as it amuses you.",
		"suggest": "",
		"suggest_action": "",
		"advance": "_pred_never",
	},
]

var _active := false
var _done := false
var _step_index := 0
var _minimized := false
var _turn := 1
var _saw_objection := false
var _saw_capture := false
# FA-42: which arm of card VII is true. "" until a roster is seen.
var _kienmayer_state := ""
# The infantry pool as of the PREVIOUS observed response. Pools regenerate
# every turn, so recruit detection must be a drop BETWEEN responses, never a
# comparison against a turn-1 baseline (regen would mask the recruit).
# Updated AFTER the current step's predicate runs — the predicate compares
# the incoming response against this previous value.
var _last_infantry_pool := -1
var _pending_pulse := false
# Aug 8 live report (TUT-F4c): the card's waiting/overdue lines derive from
# _turn, but _render only ran on STEP change — a wedged step showed the same
# text forever while turns passed. Re-render whenever the observed turn moves.
var _last_rendered_turn := -1

@onready var _card: PanelContainer = $Card
@onready var _title_label: Label = $Card/VBox/HeaderRow/TitleLabel
@onready var _step_badge: Label = $Card/VBox/HeaderRow/StepBadge
@onready var _body: RichTextLabel = $Card/VBox/BodyText
@onready var _confirm_row: HBoxContainer = $Card/VBox/ConfirmRow
@onready var _restore_button: Button = $RestoreButton


func _ready() -> void:
	hide()
	_body.meta_clicked.connect(_on_meta_clicked)
	$Card/VBox/HeaderRow/MinimizeButton.pressed.connect(_on_minimize)
	$Card/VBox/HeaderRow/SkipButton.pressed.connect(_on_skip_pressed)
	$Card/VBox/ConfirmRow/ConfirmYes.pressed.connect(_on_skip_confirmed)
	$Card/VBox/ConfirmRow/ConfirmNo.pressed.connect(func(): _confirm_row.visible = false)
	_restore_button.pressed.connect(_on_restore)


# ── payload safety ──────────────────────────────────────────────────────────

static func _as_int(value, fallback: int) -> int:
	# JSON null SURVIVES Dictionary.get()'s default (the key exists, holding
	# null — the `.get('key', 0)` trap from the CLAUDE.md table), and
	# int(null) is a script error ("Nonexistent 'int' constructor"): the
	# backend stamps `turn_ended: null` on every non-end-turn response, which
	# crashed the end-turn step live (Aug 8). Every int read off a PAYLOAD
	# goes through here; authored STEPS constants may keep bare int().
	match typeof(value):
		TYPE_INT:
			return value
		TYPE_FLOAT:
			return int(value)
		TYPE_BOOL:
			return 1 if value else 0
		TYPE_STRING:
			return int(value) if str(value).is_valid_int() else fallback
		_:
			return fallback


static func _truthy(value) -> bool:
	# TUT-F3 (the Aug 8 live report, second family): GDScript's bool()
	# constructor accepts ONLY bool/int/float — bool(null) AND
	# bool(Dictionary) are both "Invalid call. Nonexistent 'bool'
	# constructor", and the backend's popup passthroughs stamp
	# `pending_objection: null` / `pending_capture_choice: null` on every
	# response (present-but-null, so .get()'s default never applies — the
	# same trap _as_int closes for ints). Variant truthiness is what these
	# predicates mean: null / false / 0 / "" / {} / [] all read as absent.
	# Every bool read off a PAYLOAD goes through here, never bare bool().
	return true if value else false


# ── arming (world identity) ─────────────────────────────────────────────────

func on_world_swap(response) -> void:
	"""Arm iff the world says it is the tutorial. Called from
	_apply_world_swap_response AND the connection-test success arm — which is
	also the mandatory re-assert after dialog_manager.hide_all() (raw hide(),
	fired on every world swap)."""
	if typeof(response) != TYPE_DICTIONARY:
		return
	var gs = response.get("game_state")
	var name := ""
	if typeof(gs) == TYPE_DICTIONARY:
		name = str(gs.get("scenario_name", ""))
		_turn = _as_int(gs.get("turn"), _turn)
	if name != "tutorial" or UiSettings.get_tutorial_done():
		_active = false
		hide()
		return
	_active = true
	_done = false
	_saw_objection = false
	_saw_capture = false
	_kienmayer_state = ""
	# FA-42: SEED it from the swap payload. /load carries `game_state.enemies`
	# and _derive_step_for_turn can resume ON card VII, so without this the
	# first frame after a mid-lesson reload renders the default arm — the
	# "screen still stands" body — over a board where he is a prisoner.
	_note_kienmayer(response)
	_last_infantry_pool = _pool_from(response)
	_step_index = _derive_step_for_turn(_turn)
	_minimized = false
	_card.visible = true
	_restore_button.visible = false
	show()
	_render()


func _derive_step_for_turn(turn: int) -> int:
	"""Resume anchor: the FIRST step of the highest turn_gate <= turn
	(sub-turn progress resets to the turn's first step — accepted)."""
	var best_gate := 1
	for step in STEPS:
		var gate := int(step["turn_gate"])
		if gate <= turn and gate > best_gate:
			best_gate = gate
	for i in STEPS.size():
		if int(STEPS[i]["turn_gate"]) == best_gate:
			return i
	return 0


# ── observation (advance-one + catch-up) ────────────────────────────────────

func observe(response) -> void:
	"""Observe-only read of a backend response. Never routes, never sends."""
	if not _active or _done:
		return
	if typeof(response) != TYPE_DICTIONARY:
		return
	var gs = response.get("game_state")
	if typeof(gs) == TYPE_DICTIONARY:
		_turn = _as_int(gs.get("turn"), _turn)
	_note_observations(response)
	var step: Dictionary = STEPS[_step_index]
	if call(str(step["advance"]), response):
		_advance_one()
	else:
		_maybe_catch_up()
	# AFTER the predicate: the pool memory rolls forward (see _pred_recruited).
	var pool_now := _pool_from(response)
	if pool_now >= 0:
		_last_infantry_pool = pool_now
	# TUT-F4c: the waiting/overdue lines read _turn — refresh them when the
	# turn moves even though the step did not (a step advance re-rendered
	# already and stamped _last_rendered_turn itself).
	if _turn != _last_rendered_turn:
		_render()


func _pool_from(response: Dictionary) -> int:
	var gs = response.get("game_state")
	if typeof(gs) == TYPE_DICTIONARY and typeof(gs.get("manpower_pools")) == TYPE_DICTIONARY:
		return _as_int(gs["manpower_pools"].get("infantry"), -1)
	return -1


func _note_observations(response: Dictionary) -> void:
	# Latches read by the *_resolved predicates.
	if response.get("pending_objection") or str(response.get("state", "")) == "awaiting_player_choice":
		_saw_objection = true
	if response.get("pending_capture_choice"):
		_saw_capture = true
	_note_kienmayer(response)


func _note_kienmayer(response: Dictionary) -> void:
	"""FA-42 — which of four things is true of the screen card VII names.

	Read from `game_state.enemies`, which rides EVERY response, so the branch
	does not depend on catching a transient battle event (the filed fix does,
	and that event arrives only on `/respond_to_objection`).

	⚠ FOG. This entry is fog-masked: `strength` reads 0 at PARTIAL against a
	truth of 900-1,500, and `location` can name a province the executor will
	refuse to pursue to. It is read here for a NEGATIVE test only — which arm
	to render — and neither field is ever printed. A missing row means
	LAST_KNOWN, UNKNOWN, or gone from the roster entirely, and those are
	indistinguishable from the payload, so it is `lost` and never `taken`.
	"""
	var gs = response.get("game_state")
	if typeof(gs) != TYPE_DICTIONARY:
		return
	var enemies = gs.get("enemies")
	if typeof(enemies) != TYPE_DICTIONARY:
		return
	if not enemies.has("Kienmayer"):
		# Only downgrade once we have seen him — a payload that carries no
		# roster at all must not manufacture a fate.
		if _kienmayer_state != "":
			_kienmayer_state = "lost"
		return
	var rec = enemies.get("Kienmayer")
	if typeof(rec) != TYPE_DICTIONARY:
		return
	if not rec.has("fog_level") and _as_int(rec.get("strength"), 0) <= 0:
		# No fog entry means FULL visibility, which passes the true strength.
		# Zero men in full view is a prisoner, not a screen.
		_kienmayer_state = "taken"
	elif str(rec.get("location", "")) == "Swabia":
		_kienmayer_state = "stands"
	else:
		_kienmayer_state = "running"


func _advance_one() -> void:
	if _step_index >= STEPS.size() - 1:
		return
	_step_index += 1
	if visible and _card.visible:
		AudioManager.play("select")
	else:
		_pending_pulse = true
	_render()


func _maybe_catch_up() -> void:
	"""Liveness guarantee: a step whose event passed unseen (the player ran
	ahead of the school) is released once the campaign is a full turn past
	its gate — the free-play cards from XII gate on turns alone."""
	while _step_index < STEPS.size() - 1 \
			and _turn > int(STEPS[_step_index]["turn_gate"]) + 1 \
			and _turn >= int(STEPS[_step_index + 1]["turn_gate"]):
		_step_index += 1
		_render()


func on_control_returned() -> void:
	"""Cosmetic only — replay the advance cue if a modal covered the card
	when a step turned. Correctness never depends on this hook."""
	if _pending_pulse and _active and visible:
		_pending_pulse = false
		AudioManager.play("select")


# ── rendering ───────────────────────────────────────────────────────────────

func _render() -> void:
	if not _active:
		return
	_last_rendered_turn = _turn
	var step: Dictionary = STEPS[_step_index]
	# FA-42: swap in the branch arm when one is authored and true.
	# ⛔ `STEPS` is a `const`, and in Godot 4 a const Dictionary is
	# READ-ONLY AT RUNTIME — assigning into it raises "Invalid assignment
	# on read-only value" the moment the card draws, and the parse harness
	# CANNOT see it because it never calls _render(). Duplicate first.
	var alt = step.get("alt")
	if typeof(alt) == TYPE_DICTIONARY and alt.has(_kienmayer_state):
		var arm = alt[_kienmayer_state]
		step = step.duplicate()
		for key in arm:
			step[key] = arm[key]
	_title_label.text = "THE SCHOOL OF WAR"
	_step_badge.text = "%d of %d" % [_step_index + 1, STEPS.size()]
	var lines := PackedStringArray()
	lines.append("[b][color=#" + Utils.COLOR_GOLD + "]" + str(step["title"]) + "[/color][/b]")
	lines.append("[color=#d8d4c8]" + str(step["body"]) + "[/color]")
	var waiting := int(step["turn_gate"]) > _turn
	# TUT-F4c: an event step the war refuses (the live case — Austria's
	# reserve massed in Bohemia while the card demanded its capture) must
	# SAY the school moves on. The catch-up already guarantees release at
	# gate+2; this line makes that guarantee visible. Turn-gated free-play
	# cards and the terminal handoff release themselves — no line there.
	var advance_name := str(step["advance"])
	var overdue := int(step["turn_gate"]) < _turn \
		and not advance_name.begins_with("_pred_turn_gte") \
		and advance_name != "_pred_never"
	if waiting:
		lines.append("[color=#" + Utils.COLOR_DIMMED + "]Berthier resumes with the morning dispatch — end the turn when ready.[/color]")
	elif str(step["suggest"]) != "":
		lines.append(Utils.bb_button_chip("suggest:" + str(step["suggest"]), "✎ " + str(step["suggest"]), CHIP_TEXT_HEX, CHIP_BG_HEX))
		lines.append("[color=#" + Utils.COLOR_DIMMED + "]Click the quill to place the order on your command line — you give the word.[/color]")
	if overdue:
		lines.append("[color=#" + Utils.COLOR_DIMMED + "]The war has outrun this page — fight it as you find it; end the turn and the school will move on.[/color]")
	if str(step["id"]) == "handoff":
		lines.append(Utils.bb_button_chip("skipdone:", "Conclude the lesson", CHIP_TEXT_HEX, CHIP_BG_HEX))
	_body.text = "\n".join(lines)


# ── chip + button handlers ──────────────────────────────────────────────────

func _on_meta_clicked(meta) -> void:
	var meta_str := str(meta)
	if meta_str.begins_with("suggest:"):
		AudioManager.play("click")
		suggest_command.emit(meta_str.substr(8))
	elif meta_str.begins_with("skipdone:"):
		_conclude()


func _on_minimize() -> void:
	_minimized = true
	_card.visible = false
	_restore_button.visible = true
	AudioManager.play("back")


func _on_restore() -> void:
	_minimized = false
	_card.visible = true
	_restore_button.visible = false
	AudioManager.play("select")


func _on_skip_pressed() -> void:
	_confirm_row.visible = not _confirm_row.visible


func _on_skip_confirmed() -> void:
	_conclude()


func _conclude() -> void:
	UiSettings.set_tutorial_done(true)
	_done = true
	_active = false
	hide()
	AudioManager.play("back")


# ── advance predicates (verified response fields ONLY) ──────────────────────
# Fields: events[] typed entries, battle_report, bombardment_result +
# action=="bombardment", turn_ended / action_info, game_state.*,
# pending_objection / state, pending_capture_choice / capture_choice,
# enemy_phase. Choice popups DEFER past enemy_phase responses — no predicate
# requires a popup key and enemy_phase together.

func _pred_any_success(response: Dictionary) -> bool:
	return _truthy(response.get("success")) and typeof(response.get("game_state")) == TYPE_DICTIONARY


func _marshal_location(response: Dictionary, marshal_name: String) -> String:
	# The REAL payload shape (caught by the S5 live drive, not by any unit
	# test): game_state.marshals is a DICTIONARY of name -> {location,
	# strength, morale}. A list-of-dicts arm is kept as tolerance.
	var gs = response.get("game_state")
	if typeof(gs) != TYPE_DICTIONARY:
		return ""
	var marshals = gs.get("marshals")
	if typeof(marshals) == TYPE_DICTIONARY:
		var rec = marshals.get(marshal_name)
		if typeof(rec) == TYPE_DICTIONARY:
			return str(rec.get("location", ""))
		return ""
	if typeof(marshals) == TYPE_ARRAY:
		for m in marshals:
			if typeof(m) == TYPE_DICTIONARY and str(m.get("name", "")) == marshal_name:
				return str(m.get("location", ""))
	return ""


func _pred_senarmont_in_munich(response: Dictionary) -> bool:
	return _marshal_location(response, "Senarmont") == "Munich"


func _pred_turn_advanced(response: Dictionary) -> bool:
	if _as_int(response.get("turn_ended"), 0) > 0:
		return true
	var info = response.get("action_info")
	if typeof(info) == TYPE_DICTIONARY and info.get("turn_advanced"):
		return true
	return _turn >= 2


func _pred_objection_pending(response: Dictionary) -> bool:
	return _truthy(response.get("pending_objection")) \
		or str(response.get("state", "")) == "awaiting_player_choice"


func _pred_objection_resolved(response: Dictionary) -> bool:
	return _saw_objection and not _pred_objection_pending(response) \
		and _truthy(response.get("success"))


func _pred_battle_happened(response: Dictionary) -> bool:
	if typeof(response.get("battle_report")) == TYPE_DICTIONARY:
		return true
	for ev in response.get("events", []):
		if typeof(ev) == TYPE_DICTIONARY and str(ev.get("type", "")) in ["battle", "conquest"]:
			return true
	return false


func _pred_bombardment(response: Dictionary) -> bool:
	return str(response.get("action", "")) == "bombardment" \
		or typeof(response.get("bombardment_result")) == TYPE_DICTIONARY


func _pred_davout_marching(response: Dictionary) -> bool:
	# Any waypoint counts — the S5 live drive saw the pathfinder route the
	# second leg through Munich around an enemy-held Franconia, which IS the
	# lesson ("he routes around enemies on his own").
	return _marshal_location(response, "Davout") in ["Swabia", "Munich", "Franconia"]


func _pred_capture_pending(response: Dictionary) -> bool:
	return _truthy(response.get("pending_capture_choice"))


func _pred_capture_resolved(response: Dictionary) -> bool:
	# Null-guarded: /capture_choice answers carry `capture_choice: null` when
	# the token was invalid, and str(null) is "<null>" — a false advance.
	#
	# FA-N78: and question-guarded. W6-8's `_maybe_mount_estate_choice`
	# mutates the stage-1 response IN PLACE, so an answer that mounts the
	# ESTATE stage carries `capture_choice` and `pending_capture_choice`
	# together — the card would advance while a modal it has not been
	# answered is still on screen. Latent in the lesson (the tutorial
	# scenario authors no `dotation_regions`, so no estate holder is ever
	# found) and already reachable on the typed route at HEAD, which is why
	# it is fixed here rather than filed.
	var choice = response.get("capture_choice")
	if choice != null and str(choice) != "" \
			and not _truthy(response.get("pending_capture_choice")):
		return true
	return _saw_capture and not response.get("pending_capture_choice") \
		and _truthy(response.get("success"))


func _pred_recruited(response: Dictionary) -> bool:
	# A DROP since the previous response — pools only fall when men are
	# recruited out of them (regen only raises them, at turn end).
	var pool_now := _pool_from(response)
	return pool_now >= 0 and _last_infantry_pool >= 0 \
		and pool_now < _last_infantry_pool


func _pred_turn_gte_9(_response: Dictionary) -> bool:
	return _turn >= 9


func _pred_turn_gte_10(_response: Dictionary) -> bool:
	return _turn >= 10


func _pred_turn_gte_12(_response: Dictionary) -> bool:
	return _turn >= 12


func _pred_never(_response: Dictionary) -> bool:
	return false
