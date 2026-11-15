extends RefCounted
class_name BattleActs

# =============================================================================
# PROJECT SOVEREIGN — The battle in acts (row BA, session BA-1)
# =============================================================================
# The tableau's sequencer. The backend writes each battle a SCRIPT — an
# ordered list of developments in five acts (the approach, the cannonade, the
# assault, the crisis, the pursuit), every one made from a number the battle
# already produced (backend/game_logic/battle_script.py) — and this plays it
# on the war table: corps march in from the side they came from, an unseen
# enemy corps is turned up on arrival, the flank is drawn, the guns fire, each
# lead closes by his temperament, the dice are set on the baize, lines waver
# and break, the beaten are driven back and the victor follows.
#
# The user's rulings of November 14, 2026 (BATTLE_DIORAMA_SPEC.md §15.2): the
# Blend look (plinths under the carved figures), "Dice on the table", "Great
# ones in full" (a brief form for the rest), and a Settings switch.
#
# It is a HELPER of battle_diorama.gd, not a second scene: that script's
# function bodies are pinned by some thirty test files, so the acts hook into
# it at four unpinned seams (show, populate, play, the settled frame) and
# drive the block records it already builds. Display-only (Golden Rule 6).
#
# One law of the table: where the acts END is where the settled frame stands.
# `_plan_rest` decides every corps' resting place once, from the script; the
# verbs move toward it, the gavel brings whatever has not arrived to it, and
# `settle` (skip, a second viewing, "Final frame only") puts it there at once.
# =============================================================================

const ACT_TITLES := {
	"approach": "I  ·  THE APPROACH",
	"cannonade": "II  ·  THE CANNONADE",
	"assault": "III  ·  THE ASSAULT",
	"crisis": "IV  ·  THE CRISIS",
	"pursuit": "V  ·  THE PURSUIT",
}
# The time a showing may take. A captioned beat holds the table long enough to
# be read (by its length); when a battle has more to tell than the budget, the
# holds are tightened, never below HOLD_FLOOR of their length.
const FULL_BUDGET_S := 20.0
const BRIEF_BUDGET_S := 7.5
const HOLD_FLOOR := 0.72
const SILENT_S := 0.4           # a development that only moves, uncaptioned
# In the brief form the first three acts keep one head beat each, the crisis
# its dice and the first line that breaks (or that neither did), the pursuit
# its first head.
const BRIEF_KEEPS_ONE := ["approach", "cannonade", "assault", "pursuit"]

const MARCH_PX := 230.0         # how far off its place an arriving corps starts
const LEAVE_PX := 56.0          # how far a beaten corps is driven back
const WITHDRAW_PX := 24.0       # a corps that draws off in good order
const PURSUE_PX := 34.0         # how far the pursuer follows
const ADVANCE_PX := 18.0
const EDGE_KEEP := 90.0         # an arriving corps starts on the baize
const RANK_GAP_MIN := 106.0     # two ranks never stand closer than this (118 at rest)

const BRASS := Color(0.72, 0.60, 0.36, 1.0)
const BONE := Color(0.788, 0.761, 0.698, 1.0)
const GOLD := Color(0.851, 0.753, 0.549, 1.0)
const UNSEEN := Utils.UI_CORPS_UNSEEN           # a corps not yet made out

var host = null                 # the battle_diorama.gd instance
var _blocks: Dictionary = {}    # marshal name -> the host's block record
var _act_label: Label = null
var _dice: DiceTray = null
var _played: Array = []         # [{act, beat, captioned, hold}] this showing plays
# BA1-X6: what the host's populate sets for the END of the battle, held back
# while the day is open and brought by the gavel.
var _vignette_settled := Color.WHITE   # the baize's cast (a defeat's is red)
var _reserve_tails: Array = []         # [{label, full}] "+3 corps in reserve — 481 lost"
const RESERVE_DEAD := " — "            # what follows it on the tail is what the reserve lost


static func mode() -> String:
	"""Settings → Interface → Battle scenes: acts / brief / final."""
	return UiSettings.get_battle_scenes()


static func opens_settled() -> bool:
	"""'Final frame only', or Settings → Reduce motion: a battle opens as it
	ended (Replay still plays it — that is the player asking to see it)."""
	return mode() == "final" or UiSettings.get_reduce_motion()


func _init(diorama) -> void:
	host = diorama


func _the_script() -> Dictionary:
	var s = host._data.get("script", null) if host != null else null
	return s if s is Dictionary else {}


func plays() -> bool:
	"""A land battle that carries a script with something in it. A fleet
	action keeps its own sequence (no plinths at sea), and a payload from
	before the acts keeps the tableau's first sequence."""
	if host == null or host._is_naval():
		return false
	var acts = _the_script().get("acts", [])
	return acts is Array and not acts.is_empty()


func _brief() -> bool:
	return mode() == "brief" or str(_the_script().get("form", "full")) == "brief"


func _all_beats() -> Array:
	var out: Array = []
	for block in _the_script().get("acts", []):
		if block is Dictionary:
			for beat in block.get("beats", []):
				if beat is Dictionary:
					out.append({"act": str(block.get("act", "")), "beat": beat})
	return out


static func _natural_hold(beat: Dictionary, brief: bool) -> float:
	"""How long a sentence holds the table: by its length, the dice longer."""
	var n: int = str(beat.get("text", "")).length()
	if brief:
		return clampf(0.85 + 0.018 * n, 1.2, 1.9)
	var hold: float = clampf(1.1 + 0.028 * n, 1.7, 3.1)
	if str(beat.get("kind", "")) == "dice":
		hold = maxf(hold, 2.8)
	return hold


func _plan() -> Array:
	"""The showing: every beat it plays, which of them are captioned, and how
	long each holds. Full: every beat moves; the head beats are captioned and
	the details too while the budget has room. Brief: the head beats alone."""
	var brief: bool = _brief()
	var out: Array = []
	if brief:
		var kept: Dictionary = {}
		var crisis_break := false
		for item in _all_beats():
			var beat: Dictionary = item["beat"]
			var act: String = str(item["act"])
			var kind: String = str(beat.get("kind", ""))
			if str(beat.get("weight", "")) != "head":
				continue
			if act in BRIEF_KEEPS_ONE:
				if kept.has(act):
					continue
				kept[act] = true
			elif act == "crisis" and kind in ["break", "stand"]:
				if crisis_break:
					continue
				crisis_break = true
			out.append({"act": act, "beat": beat, "captioned": true,
					"hold": _natural_hold(beat, true)})
		_fit_budget(out, BRIEF_BUDGET_S)
		return out

	var total := 0.0
	var acts_told: Dictionary = {}
	for item in _all_beats():
		var beat: Dictionary = item["beat"]
		var head: bool = str(beat.get("weight", "")) == "head"
		var hold: float = _natural_hold(beat, false) if head else SILENT_S
		total += hold
		if head:
			acts_told[str(item["act"])] = true
		out.append({"act": str(item["act"]), "beat": beat, "captioned": head, "hold": hold})
	# Every act the battle has is NAMED on the table: an act of details alone
	# (a pursuit that is one corps leaving the field) tells its first.
	for row in out:
		if acts_told.has(str(row["act"])):
			continue
		acts_told[str(row["act"])] = true
		row["captioned"] = true
		row["hold"] = _natural_hold(row["beat"], false)
		total += float(row["hold"]) - SILENT_S
	# Room left: the details are told too, in order.
	for row in out:
		if bool(row["captioned"]):
			continue
		var want: float = _natural_hold(row["beat"], false)
		if total + want - SILENT_S > FULL_BUDGET_S:
			continue
		row["captioned"] = true
		row["hold"] = want
		total += want - SILENT_S
	_fit_budget(out, FULL_BUDGET_S)
	return out


static func _fit_budget(rows: Array, budget: float) -> void:
	var told := 0.0
	var silent := 0.0
	for row in rows:
		if bool(row["captioned"]):
			told += float(row["hold"])
		else:
			silent += float(row["hold"])
	if told <= 0.0 or told + silent <= budget:
		return
	var factor: float = clampf((budget - silent) / told, HOLD_FLOOR, 1.0)
	for row in rows:
		if bool(row["captioned"]):
			row["hold"] = float(row["hold"]) * factor


# ─────────────────────────────────────────────────────────────────────────────
# Dressing the table (the end of the host's _populate)
# ─────────────────────────────────────────────────────────────────────────────

func dress(final_frame: bool) -> void:
	"""Plinths under every corps, the act mark and the dice tray; then either
	the settled frame or the opening positions of the acts."""
	_blocks = {}
	if host == null:
		return
	_put_the_chrome_back()
	if host._is_naval():
		return
	for b in host._blocks_left + host._blocks_right:
		var c: Dictionary = b["data"]
		var name: String = str(c.get("name", ""))
		_blocks[name] = b
		b["home"] = (b["node"] as Node2D).position
		b["rest_dx"] = 0.0
		var art: Node2D = (b["node"] as Node2D).get_node_or_null("Art")
		if art == null:
			continue
		var plinth := DioramaPlinth.new()
		plinth.name = "Plinth"
		var key: String = str(c.get("origin_nation", c.get("nation", "")))
		plinth.setup(Utils.NATION_COLORS.get(key, Utils.UI_NEUTRAL_FIGURE), bool(b["is_left"]))
		art.add_child(plinth)
		art.move_child(plinth, 0)
		b["plinth"] = plinth
		b["pips"] = DioramaPlinth.pips_lost(int(c.get("committed", 0)), int(c.get("remaining", 0)))
		_keep_words_on_the_baize(b)
		_advance_toll_under_the_feet(b)
		_find_strength_line(b)
	_plan_rest()
	_keep_the_end()

	var sw: float = host._stage.size.x
	_act_label = host._mk_label(host._stage, "", &"Caption", BRASS, host._font_engraved)
	_act_label.size = Vector2(sw, 18.0)
	_act_label.position = Vector2(0.0, 16.0)
	_act_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_act_label.visible = false
	host._outline_over_colours(_act_label)
	host._transients.append(_act_label)

	var roll: Dictionary = _dice_beat()
	if not roll.is_empty():
		_dice = DiceTray.new()
		host._stage.add_child(_dice)
		host._transients.append(_dice)
		_dice.build(host, roll, _luck_line(roll))
		_dice.position = Vector2(sw / 2.0 - DiceTray.TRAY_W / 2.0, 74.0)
		_dice.visible = false

	if final_frame:
		settle()
	elif plays():
		_played = _plan()
		_set_opening()


func _dice_beat() -> Dictionary:
	for item in _all_beats():
		if str(item["beat"].get("kind", "")) == "dice":
			return item["beat"]
	return {}


func _keep_words_on_the_baize(b: Dictionary) -> void:
	"""BA1-X3. A one-line fate caption under an outer corps ("marched to the
	guns", "ROUTED") could not be cut to the baize as the wrapping captions
	are: at four ranks the outermost corps stands 80 px from the edge, the
	room between the baize's margin and the caption's inboard edge is 79 px,
	and the line is 125 px at the shipped type — so it hung 4 px off the
	baize, over the tray's wood. A line that does not fit its room is wrapped
	inside it (its inboard edge stays, as the host's own rule keeps it)."""
	var node: Node2D = b["node"]
	var art: Node2D = node.get_node_or_null("Art")
	var s: float = art.scale.x if art != null else 1.0
	var left: bool = bool(b["is_left"])
	var pad: float = host.BAIZE_PAD
	var inboard: float = host.FAITH_CAPTION_INBOARD * s * (1.0 if left else -1.0)
	var room: float = (node.position.x + inboard - pad) if left \
			else (host._stage.size.x - pad - (node.position.x + inboard))
	for child in node.get_children():
		if not (child is Label):
			continue
		var l: Label = child
		if l.position.y < 0.0 or l.autowrap_mode != TextServer.AUTOWRAP_OFF:
			continue
		if l.get_minimum_size().x <= room + 0.5:
			continue
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		l.custom_minimum_size = Vector2(room, 0.0)
		l.size = Vector2(room, l.size.y)
		l.position.x = (inboard - room) if left else inboard


const ADVANCE_TOLL := " after the advance"


func _advance_toll_under_the_feet(b: Dictionary) -> void:
	"""BA1-X1. The lead's strength line carried the advance's toll on its end
	("24,000 → 21,994 → 21,687 after the advance", LV-11): three figures and
	three words on a line laid out for two figures, so it ran across the
	centre line and over the other lead's own strength line — measured on the
	campaign's opening battle (Ney against Mack in Swabia, where the march
	into the province always costs men). The toll is the same words in the
	same size, told under the lead's feet where the fate captions stand; the
	strength line keeps its two figures."""
	var node: Node2D = b["node"]
	var floor_y := 0.0          # the foot of whatever already stands under the feet
	var strength: Label = null
	for child in node.get_children():
		if not (child is Label):
			continue
		var l: Label = child
		if l.position.y >= 0.0:
			floor_y = maxf(floor_y, l.position.y + maxf(l.size.y, l.get_minimum_size().y))
		elif l.text.ends_with(ADVANCE_TOLL) and l.text.count(" → ") >= 2:
			strength = l
	if strength == null:
		return
	var left: bool = bool(b["is_left"])
	var cut: int = strength.text.rfind(" → ")
	var toll: String = strength.text.substr(cut + 1)       # "→ 21,687 after the advance"
	strength.text = strength.text.substr(0, cut)
	# The long line had stretched the label past its box (a Label is never
	# narrower than its text), which on the right-hand side slid the
	# right-aligned figures under the portrait: back to the name's own width.
	var box_w: float = 150.0 if left else 226.0
	for child in node.get_children():
		if child is Label and child != strength \
				and is_equal_approx((child as Label).position.x, strength.position.x) \
				and (child as Label).position.y < strength.position.y:
			box_w = (child as Label).size.x
	strength.size = Vector2(box_w, strength.size.y)

	var art: Node2D = node.get_node_or_null("Art")
	var s: float = art.scale.x if art != null else 1.0
	var caption: Label = host._mk_label(node, toll, &"Caption", Color(host.BONE_HEX))
	var need: Vector2 = caption.get_minimum_size()
	caption.size = need
	# Under the slab, from its OUTER end toward the clash line: the reserve
	# note stands in the baize's outboard corner and the fate captions hang
	# outboard of the corps, so the toll reads inboard of both.
	var slab: float = DioramaPlinth.HALF_W * s
	caption.position = Vector2(-slab if left else slab - need.x,
			maxf(host.FAITH_CAPTION_Y * s, floor_y + 1.0))
	caption.z_index = host.TEXT_Z
	host._outline_over_colours(caption)
	b["toll"] = caption


func _find_strength_line(b: Dictionary) -> void:
	"""BA1-X6. The corps' strength line ("52,000 → 30,723") is kept with its
	settled words. The shipped tableau printed it whole from the first frame,
	which nobody read in four seconds; over acts of twenty it told where every
	corps would END before a die was thrown. The acts open the line on what
	the corps BROUGHT and run it with the count (`_run_strengths`), as the
	odometers, the army bars and the pips already run."""
	for child in (b["node"] as Node2D).get_children():
		if child is Label and (child as Label).position.y < 0.0 \
				and (child as Label).text.contains(" → "):
			var full: String = (child as Label).text
			b["strength"] = child
			b["strength_full"] = full
			b["strength_brought"] = full.substr(0, full.find(" → "))
			return


func _laurels() -> Array:
	var out: Array = []
	for laurel in [host._laurel_l, host._laurel_r]:
		if laurel != null and is_instance_valid(laurel):
			out.append(laurel)
	return out


func _laurel_alpha(laurel: CanvasItem) -> float:
	"""The laurels are chrome (built once, never rebuilt), so the alpha they
	were made with is read ONCE and kept on the node: a later populate would
	read back whatever an interrupted showing left."""
	if not laurel.has_meta(&"ba_settled_alpha"):
		laurel.set_meta(&"ba_settled_alpha", laurel.modulate.a)
	return float(laurel.get_meta(&"ba_settled_alpha"))


func _put_the_chrome_back() -> void:
	"""Every table that is laid — a fleet action and a payload from before
	the acts among them — starts from chrome as it was built. A showing that
	was closed mid-act (Esc) leaves the laurels held back, and one closed in
	its first quarter second leaves the tray part-faded (the first sequence
	always could); neither `settle` nor the gavel runs for the battle that is
	shown next unless it plays in acts or opens settled on land."""
	host._tray.modulate.a = 1.0
	for laurel in _laurels():
		(laurel as CanvasItem).modulate.a = _laurel_alpha(laurel)


func _keep_the_end() -> void:
	"""BA1-X6's siblings: three more things the host's populate sets from the
	battle's RESULT and shows from the first frame — the red cast a defeat
	puts on the baize, the laurels that flank the plate on a triumph, and
	what the corps in reserve lost. Kept here; `_set_opening` holds them back
	and the gavel (`_come_to_rest`, or `settle`) brings them."""
	_vignette_settled = host._vignette.modulate
	for laurel in _laurels():
		_laurel_alpha(laurel)
	_reserve_tails = []
	for node in host._transients:
		if node is Label and is_instance_valid(node) \
				and (node as Label).text.contains(RESERVE_DEAD) \
				and (node as Label).text.ends_with(" lost"):
			_reserve_tails.append({"label": node, "full": (node as Label).text})


func _the_end_is_told() -> void:
	"""At once (the settled frame)."""
	host._vignette.modulate = _vignette_settled
	for laurel in _laurels():
		(laurel as CanvasItem).modulate.a = _laurel_alpha(laurel)
	_tell_the_reserves_dead()


func _tell_the_reserves_dead() -> void:
	for tail in _reserve_tails:
		if is_instance_valid(tail["label"]):
			(tail["label"] as Label).text = str(tail["full"])


func _attacker_left() -> bool:
	"""The player's line is always the left; an observed battle keeps the
	attacker left (the host's `_side_payloads`)."""
	return str(host._data.get("player_side", "")) != "defender"


func _luck_line(roll: Dictionary) -> String:
	"""Each side's luck of the day, by the side it stands on the table."""
	var sides: Array = host._side_payloads()
	var left_key: String = "fortune_attacker" if _attacker_left() else "fortune_defender"
	var right_key: String = "fortune_defender" if _attacker_left() else "fortune_attacker"
	return "luck   %s %s   ·   %s %s" % [
		Utils.display_nation_name(str(sides[0].get("nation", ""))), _signed(int(roll.get(left_key, 0))),
		Utils.display_nation_name(str(sides[1].get("nation", ""))), _signed(int(roll.get(right_key, 0)))]


static func _signed(pct: int) -> String:
	return ("+%d%%" % pct) if pct >= 0 else ("−%d%%" % absi(pct))


func _outward(b: Dictionary) -> float:
	"""-1 for a corps on the left of the table (its own edge is the left)."""
	return -1.0 if bool(b["is_left"]) else 1.0


func _rest_pos(b: Dictionary) -> Vector2:
	return (b["home"] as Vector2) + Vector2(float(b.get("rest_dx", 0.0)), 0.0)


# ─────────────────────────────────────────────────────────────────────────────
# Where each corps comes to rest
# ─────────────────────────────────────────────────────────────────────────────

func _plan_rest() -> void:
	"""A beaten corps is driven back toward its own edge, one that draws off in
	good order a little, the pursuer and the advance forward. A corps never
	moves off the baize, and never closer to the rank behind it than the line
	was laid out to stand — so a lead who breaks in front of steady supports
	falls back ON them, and a whole line that breaks goes back together."""
	var wants: Dictionary = {}     # name -> signed px, + toward the clash line
	for item in _all_beats():
		var beat: Dictionary = item["beat"]
		var name: String = str(beat.get("actor", ""))
		if not _blocks.has(name):
			continue
		match str(beat.get("kind", "")):
			"leave":
				wants[name] = -(WITHDRAW_PX if str(beat.get("how", "")) == "withdrew" else LEAVE_PX)
			"pursue":
				wants[name] = PURSUE_PX
			"advance_to":
				if not wants.has(name):
					wants[name] = ADVANCE_PX
	for side in [host._blocks_left, host._blocks_right]:
		var n: int = side.size()
		var d: Array = []
		for k in range(n):
			var b: Dictionary = side[k]
			var want: float = float(wants.get(str((b["data"] as Dictionary).get("name", "")), 0.0))
			if k > 0:
				want = minf(want, 0.0)          # only the front rank goes forward
			d.append(maxf(want, -_room_back(b)))
		for k in range(n - 2, -1, -1):
			var gap: float = absf((side[k + 1]["home"] as Vector2).x - (side[k]["home"] as Vector2).x)
			d[k] = maxf(d[k], d[k + 1] - maxf(gap - RANK_GAP_MIN, 0.0))
		for k in range(n):
			side[k]["rest_dx"] = -_outward(side[k]) * float(d[k])


func _room_back(b: Dictionary) -> float:
	"""How far a corps can be driven toward its own edge before any of it —
	its locket, its slab, the words under its feet — leaves the baize."""
	var node: Node2D = b["node"]
	var art: Node2D = node.get_node_or_null("Art")
	var s: float = art.scale.x if art != null else 1.0
	var left: bool = bool(b["is_left"])
	# the art: the locket stands outboard of the men (the host's _make_block)
	var reach: float = 100.0 * s
	for child in node.get_children():
		if not (child is Label):
			continue
		var l: Label = child
		var w: float = l.size.x
		if l.autowrap_mode == TextServer.AUTOWRAP_OFF:
			w = minf(w, l.get_minimum_size().x)
		# the words sit at the label's aligned edge: outboard-reaching text is
		# what matters (a right-aligned label on the left side grows leftward)
		var lo: float = l.position.x
		var hi: float = l.position.x + l.size.x
		if l.horizontal_alignment == HORIZONTAL_ALIGNMENT_RIGHT:
			lo = hi - w
		else:
			hi = lo + w
		reach = maxf(reach, -lo if left else hi)
	var home: Vector2 = b["home"]
	var pad: float = host.BAIZE_PAD
	var room: float = (home.x - reach - pad) if left else (host._stage.size.x - pad - home.x - reach)
	return maxf(room, 0.0)


func _set_opening() -> void:
	"""Before the first beat: every corps' line reads what it BROUGHT and the
	advance's toll is not yet told (BA1-X6); a corps that marches in during
	the approach stands off its place, unseen."""
	for name in _blocks:
		var held: Dictionary = _blocks[name]
		var line: Label = held.get("strength", null)
		if line != null:
			line.text = str(held.get("strength_brought", line.text))
		var toll: Label = held.get("toll", null)
		if toll != null:
			# hidden, not drawn at no alpha: a line that is not shown is not on
			# the table for anything that reads it (the contrast instrument
			# measured the transparent line as unreadable text)
			toll.visible = false
	host._vignette.modulate = Color.WHITE
	for laurel in _laurels():
		(laurel as CanvasItem).modulate.a = 0.0
	for tail in _reserve_tails:
		var full: String = str(tail["full"])
		(tail["label"] as Label).text = full.substr(0, full.find(RESERVE_DEAD))
	for item in _played:
		var beat: Dictionary = item["beat"]
		if str(beat.get("kind", "")) != "arrive":
			continue
		var b = _blocks.get(str(beat.get("actor", "")), null)
		if b == null:
			continue
		var node: Node2D = b["node"]
		var home: Vector2 = b["home"]
		var room: float = (home.x - EDGE_KEEP) if bool(b["is_left"]) \
				else (host._stage.size.x - EDGE_KEEP - home.x)
		node.position = home + Vector2(_outward(b) * clampf(room, 0.0, MARCH_PX), 0.0)
		node.modulate.a = 0.0
		b["arrives"] = true
		if bool(beat.get("concealed", false)):
			# the other side's corps comes up unseen: a dark slab, no face and
			# no name until it is on the field
			b["concealed"] = true
			var art: Node2D = node.get_node_or_null("Art")
			if art != null:
				art.modulate = UNSEEN
			(b["locket"] as CanvasItem).modulate.a = 0.0
			# his name and his numbers are hidden, not drawn at no alpha (as
			# the toll above); the ones hidden HERE are the ones `_reveal`
			# brings — a fate caption the host keeps hidden stays hidden
			var unseen: Array = []
			for child in node.get_children():
				if child is Label and (child as Label).visible:
					(child as Label).visible = false
					unseen.append(child)
			b["unseen_labels"] = unseen


# ─────────────────────────────────────────────────────────────────────────────
# The settled frame (the end of the host's _apply_final_frame_instant)
# ─────────────────────────────────────────────────────────────────────────────

func settle() -> void:
	"""Everything as the battle left it: pips counted, a beaten corps' plinth
	turned down, every corps at its resting place, the dice on the baize."""
	if host == null or host._is_naval():
		return
	for name in _blocks:
		var b: Dictionary = _blocks[name]
		var plinth: DioramaPlinth = b.get("plinth", null)
		if plinth != null:
			plinth.set_lost(float(int(b.get("pips", 0))))
			plinth.set_face_down(str(b["status"]) in ["routed", "destroyed"])
		(b["node"] as Node2D).position = _rest_pos(b)
		_strength_settled(b)
		var toll: Label = b.get("toll", null)
		if toll != null:
			toll.visible = true
			toll.modulate.a = 1.0
	_the_end_is_told()
	if _act_label != null:
		_act_label.visible = false
	if _dice != null:
		_dice.visible = true
		_dice.settle()


func _come_to_rest() -> void:
	"""The gavel: whatever the showing did not move (the brief form plays no
	'leave'; a lead that surged stands ahead of his place) comes to where the
	settled frame has it, and every beaten plinth is turned down."""
	if host == null or not is_instance_valid(host):
		return
	if _act_label != null and is_instance_valid(_act_label):
		_act_label.visible = false
	_tell_the_reserves_dead()
	for name in _blocks:
		var b: Dictionary = _blocks[name]
		var node: Node2D = b["node"]
		if not is_instance_valid(node):
			continue
		var plinth: DioramaPlinth = b.get("plinth", null)
		if plinth != null:
			plinth.set_face_down(str(b["status"]) in ["routed", "destroyed"])
		_strength_settled(b)
		_tell_toll(b)
		var rest: Vector2 = _rest_pos(b)
		if node.position.is_equal_approx(rest) and is_equal_approx(node.modulate.a, 1.0):
			continue
		var tw: Tween = node.create_tween()
		tw.tween_property(node, "position", rest, 0.45) \
			.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN_OUT)
		tw.parallel().tween_property(node, "modulate:a", 1.0, 0.3)
		_reveal(b, tw)
	if _dice != null and is_instance_valid(_dice) and not _dice.visible:
		_dice.visible = true
		_dice.settle()


# ─────────────────────────────────────────────────────────────────────────────
# Playing the acts (the host's _play_cinematic)
# ─────────────────────────────────────────────────────────────────────────────

func play() -> void:
	host._final = false
	host._kill_sequence()
	if _played.is_empty():
		_played = _plan()

	host._tray.modulate.a = 0.0
	host._cue("drum_cadence")
	host._seq = host.create_tween()
	host._seq.tween_property(host._tray, "modulate:a", 1.0, 0.24)

	# The corps that stood on the field from the start are placed first.
	var t := 0.30
	for b in host._blocks_left + host._blocks_right:
		if bool(b.get("arrives", false)):
			continue
		for f in b["figures"]:
			f.pop_in(t)
			t += 0.02
		var locket: CanvasItem = b["locket"]
		locket.modulate.a = 0.0
		host._seq.parallel().tween_property(locket, "modulate:a", 1.0, 0.3).set_delay(t)
	t += 0.45

	var fight_from := -1.0
	var fight_to := t
	var first_break := -1.0
	for row in _played:
		var act: String = str(row["act"])
		var beat: Dictionary = row["beat"]
		var hold: float = float(row["hold"])
		row["at"] = t          # when this development begins (the walk's camera reads it)
		_at(t, _show_beat.bind(act, beat, bool(row["captioned"])))
		if act in ["assault", "crisis"]:
			if fight_from < 0.0:
				fight_from = t
			fight_to = t + hold
		if str(beat.get("kind", "")) == "break" and first_break < 0.0:
			first_break = t
		t += hold

	# The fighting's one count: the men fall, the odometers run and the pips
	# tick together, from the first blow to the end of the crisis.
	if fight_from < 0.0:
		fight_from = t
		fight_to = t + 1.6
		t = fight_to
	var span: float = maxf(fight_to - fight_from, 1.2)
	host._schedule_topples(fight_from, span)
	host._animate_odometers(fight_from, span + 0.4)
	_tick_pips(fight_from, span + 0.4)
	_run_strengths(fight_from, span + 0.4)
	host._schedule_standards(first_break + 0.5 if first_break >= 0.0 else fight_from + span * 0.75)

	# The gavel, as before: the table comes to rest, banner, then Berthier.
	t = maxf(t, fight_from + span + 0.5)
	_at(t, _come_to_rest)
	# BA1-X6: with the gavel, what the table held back — the defeat's cast and
	# the laurels. On the master sequence, so a skip or Replay kills them with
	# it (the chrome they touch outlives a showing; a tween of its own would
	# go on writing to it under the next one).
	host._seq.parallel().tween_property(host._vignette, "modulate", _vignette_settled, 0.5) \
		.set_delay(t)
	for laurel in _laurels():
		host._seq.parallel().tween_property(laurel, "modulate:a", _laurel_alpha(laurel), 0.5) \
			.set_delay(t)
	host._seq.parallel().tween_callback(host._show_banner).set_delay(t + 0.10)
	host._seq.parallel().tween_callback(host._type_verdict).set_delay(t + 0.55)
	host._seq.parallel().tween_callback(func(): host._enter_final(true)).set_delay(t + 0.70)


func _at(t: float, what: Callable) -> void:
	host._seq.parallel().tween_callback(what).set_delay(t)


func _tick_pips(start: float, span: float) -> void:
	for name in _blocks:
		var b: Dictionary = _blocks[name]
		var plinth: DioramaPlinth = b.get("plinth", null)
		var pips: int = int(b.get("pips", 0))
		if plinth == null or pips <= 0:
			continue
		var tw: Tween = plinth.create_tween()
		tw.tween_interval(start)
		tw.tween_method(plinth.set_lost, 0.0, float(pips), span)


func _run_strengths(start: float, span: float) -> void:
	"""BA1-X6. Each corps' strength line runs with the count — from what it
	brought to what it kept — and ends on its settled words."""
	for name in _blocks:
		var b: Dictionary = _blocks[name]
		var line: Label = b.get("strength", null)
		if line == null or not is_instance_valid(line):
			continue
		var c: Dictionary = b["data"]
		var tw: Tween = line.create_tween()
		tw.tween_interval(start)
		tw.tween_method(_strength_at.bind(line, str(b.get("strength_brought", "")),
				maxi(int(c.get("committed", 0)), 1), int(c.get("remaining", 0))), 0.0, 1.0, span)
		tw.tween_callback(_strength_settled.bind(b))


func _strength_at(v: float, line: Label, brought: String, before: int, after: int) -> void:
	if is_instance_valid(line):
		line.text = "%s → %s" % [brought,
				Utils.format_number(int(round(lerpf(float(before), float(after), v))))]


func _strength_settled(b: Dictionary) -> void:
	var line: Label = b.get("strength", null)
	if line != null and is_instance_valid(line):
		line.text = str(b.get("strength_full", line.text))


func _tell_toll(b: Dictionary) -> void:
	"""The advance's toll is told when the advance is (or at the gavel)."""
	var toll: Label = b.get("toll", null)
	if toll == null or not is_instance_valid(toll) or toll.visible:
		return
	toll.modulate.a = 0.0
	toll.visible = true
	toll.create_tween().tween_property(toll, "modulate:a", 1.0, 0.3)


func _show_beat(act: String, beat: Dictionary, captioned: bool) -> void:
	"""One development: its act named above the field and its sentence where
	Berthier's verdict will be written (when it is told), and its movement
	on the table (always)."""
	if host == null or not is_instance_valid(host) or host._final:
		return
	if captioned:
		if _act_label != null and is_instance_valid(_act_label):
			_act_label.text = str(ACT_TITLES.get(act, ""))
			_act_label.visible = _act_label.text != ""
		var line: String = str(beat.get("text", "")).replace("[", "[lb]")
		host._verdict.text = "[center][i]%s[/i][/center]" % Utils.bbcode_color(
				line, Utils.COLOR_OBSERVATION)
		host._verdict.visible_characters = -1

	var b = _blocks.get(str(beat.get("actor", "")), null)
	var attacker_side: bool = str(beat.get("side", "")) == "attacker"
	match str(beat.get("kind", "")):
		"arrive":
			if b != null:
				_march_in(b)
		"flank":
			_draw_flank(attacker_side)
		"battery":
			host._cue("cannon")
			_fire(b, str(beat.get("target", "")), attacker_side)
		"advance":
			if b != null:
				_advance(b, str(beat.get("temper", "steady")), attacker_side)
		"dice":
			if _dice != null and is_instance_valid(_dice):
				_dice.visible = true
				_dice.roll()
		"break":
			if b != null:
				_waver(b)
				host._cue("drum_sting")
		"stand":
			for lead in _leads():
				_pulse(lead["locket"])
		"pursue":
			if b != null:
				host._cue("cavalry" if str((b["data"] as Dictionary).get("arm", "")) == "cavalry"
						else "bugle_charge")
				_slide(b, 0.8)
		"leave":
			if b != null:
				if str(beat.get("how", "")) != "withdrew":
					host._cue("bugle_retreat")
				_slide(b, 0.9)
		"advance_to":
			if b != null:
				_slide(b, 0.7)
				_tell_toll(b)
		_:
			# every other development is about one corps: its commander answers
			if b != null:
				_pulse(b["locket"])


func _leads() -> Array:
	var out: Array = []
	for name in _blocks:
		if bool((_blocks[name]["data"] as Dictionary).get("lead", false)):
			out.append(_blocks[name])
	return out


# ── The verbs ────────────────────────────────────────────────────────────────

func _reveal(b: Dictionary, tw: Tween) -> void:
	"""An enemy corps that came up unseen is made out: its colours, its
	commander's face and its name."""
	if not bool(b.get("concealed", false)):
		(b["locket"] as CanvasItem).modulate.a = 1.0
		return
	b["concealed"] = false
	var node: Node2D = b["node"]
	var art: Node2D = node.get_node_or_null("Art")
	if art != null:
		tw.tween_property(art, "modulate", Color.WHITE, 0.35)
	tw.parallel().tween_property(b["locket"], "modulate:a", 1.0, 0.35)
	for child in b.get("unseen_labels", []):
		if not is_instance_valid(child):
			continue
		(child as Label).modulate.a = 0.0
		tw.parallel().tween_callback((child as Label).set_visible.bind(true))
		tw.parallel().tween_property(child, "modulate:a", 1.0, 0.35)
	b["unseen_labels"] = []


func _march_in(b: Dictionary) -> void:
	"""A corps comes onto the table from its own edge; an enemy corps that
	came up unseen is turned up as it arrives."""
	var node: Node2D = b["node"]
	host._cue("march_step")
	var tw: Tween = node.create_tween()
	tw.tween_property(node, "modulate:a", 1.0, 0.3)
	tw.parallel().tween_property(node, "position", b["home"], 0.9) \
		.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	_reveal(b, tw)


func _advance(b: Dictionary, temper: String, attacking: bool) -> void:
	"""Each temperament closes in its own way. The defender's line answers
	in kind but does not leave its ground."""
	var node: Node2D = b["node"]
	var toward: float = -_outward(b)
	var home_x: float = (b["home"] as Vector2).x
	var tw: Tween = node.create_tween()
	if attacking:
		host._cue("bugle_charge" if temper == "aggressive" else "musket_volley")
	match temper:
		"aggressive":
			# ahead of the line, at once, and a little too far
			tw.tween_property(node, "position:x", home_x + toward * (28.0 if attacking else 12.0), 0.34) \
				.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
		"cautious":
			# by measured steps: a step, a halt, a step
			var step: float = 7.0 if attacking else 0.0
			tw.tween_property(node, "position:x", home_x + toward * step, 0.30)
			tw.tween_interval(0.28)
			tw.tween_property(node, "position:x", home_x + toward * step * 2.0, 0.30)
		"literal":
			# to his mark, in one even movement, and no further
			tw.tween_property(node, "position:x", home_x + toward * (12.0 if attacking else 0.0), 0.55) \
				.set_trans(Tween.TRANS_LINEAR)
		"sovereign":
			# the line dresses on him: he does not surge, his corps closes up
			tw.tween_property(node, "position:x", home_x + toward * (8.0 if attacking else 0.0), 0.6) \
				.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN_OUT)
			_pulse(b["locket"])
		_:
			tw.tween_property(node, "position:x", home_x + toward * (12.0 if attacking else 0.0), 0.45) \
				.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)


func _slide(b: Dictionary, seconds: float) -> void:
	"""To the corps' resting place (driven back, drawn off, in pursuit)."""
	var node: Node2D = b["node"]
	var tw: Tween = node.create_tween()
	tw.tween_property(node, "position", _rest_pos(b), seconds) \
		.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN_OUT)


func _waver(b: Dictionary) -> void:
	"""The line shudders, then its plinth is turned down."""
	var node: Node2D = b["node"]
	var x: float = node.position.x
	var tw: Tween = node.create_tween()
	for i in range(3):
		tw.tween_property(node, "position:x", x + (3.0 if i % 2 == 0 else -3.0), 0.07)
	tw.tween_property(node, "position:x", x, 0.07)
	var plinth: DioramaPlinth = b.get("plinth", null)
	if plinth != null:
		tw.tween_callback(plinth.set_face_down.bind(true))


func _pulse(item) -> void:
	if not (item is Control) or not is_instance_valid(item):
		return
	var c: Control = item
	c.pivot_offset = c.size / 2.0
	var tw: Tween = c.create_tween()
	tw.tween_property(c, "scale", Vector2(1.22, 1.22), 0.16) \
		.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tw.tween_property(c, "scale", Vector2.ONE, 0.26)


func _fire(gunner, target_name: String, attacker_fires: bool) -> void:
	"""The guns. A battery that stands on the table fires from its own corps;
	one that fires from the next province (the usual case: guns ordered in
	support) is shown as a gun set at its side's edge of the field for as
	long as it fires. Three rounds; the line that takes them flinches."""
	var sw: float = host._stage.size.x
	var sh: float = host._stage.size.y
	var from_left: bool = attacker_fires == _attacker_left()
	var dir: float = 1.0 if from_left else -1.0
	var muzzle: Vector2
	if gunner != null:
		muzzle = (gunner["node"] as Node2D).position + Vector2(52.0 * dir, -34.0)
	else:
		var side: Dictionary = host._side_payloads()[0 if from_left else 1]
		var gun := DioramaFigure.new()
		gun.setup("artillery", "r" if from_left else "l",
				Utils.NATION_COLORS.get(str(side.get("nation", "")), Utils.UI_NEUTRAL_FIGURE),
				host.SHELF_FIGURE_PX * 1.35)
		gun.position = Vector2(66.0 if from_left else sw - 66.0, sh * 0.80)
		gun.modulate.a = 0.0
		host._stage.add_child(gun)
		host._transients.append(gun)
		var appear: Tween = gun.create_tween()
		appear.tween_property(gun, "modulate:a", 1.0, 0.2)
		appear.tween_interval(1.5)
		appear.tween_property(gun, "modulate:a", 0.0, 0.5)
		muzzle = gun.position + Vector2(30.0 * dir, -26.0)
	var target = _blocks.get(target_name, null)
	for i in range(3):
		var shot := Burst.new()
		shot.position = muzzle + Vector2(0.0, -5.0 + 5.0 * i)
		shot.dir = dir
		host._stage.add_child(shot)
		host._transients.append(shot)
		shot.go(0.25 + 0.22 * i)
		if target != null:
			var hit := Burst.new()
			hit.position = (target["node"] as Node2D).position \
					+ Vector2(-40.0 * dir + 26.0 * i * dir, -30.0 - 6.0 * i)
			hit.dir = 0.0
			host._stage.add_child(hit)
			host._transients.append(hit)
			hit.go(0.45 + 0.22 * i)
	if target != null:
		for f in target["figures"]:
			f.recoil(0.5)


class Burst:
	extends Node2D
	# One round: a flash at the muzzle (`dir` ±1, with a tongue of fire along
	# it) or where it lands (`dir` 0), and the smoke that drifts off it.

	var dir := 1.0
	var t := -1.0                # < 0: not yet fired

	func go(delay: float) -> void:
		z_index = 40
		var tw: Tween = create_tween()
		tw.tween_interval(delay)
		tw.tween_method(_at, 0.0, 1.0, 0.9)
		tw.tween_callback(queue_free)

	func _at(v: float) -> void:
		t = v
		queue_redraw()

	func _draw() -> void:
		if t < 0.0:
			return
		var flash: float = clampf(1.0 - t * 5.0, 0.0, 1.0)
		if flash > 0.0:
			draw_circle(Vector2.ZERO, 5.0 + 6.0 * (1.0 - flash), Color(1.0, 0.94, 0.72, flash))
			if dir != 0.0:
				draw_colored_polygon(PackedVector2Array([
					Vector2(0.0, -3.5), Vector2(24.0 * dir, 0.0), Vector2(0.0, 3.5)]),
					Color(1.0, 0.82, 0.42, flash))
		var smoke: float = clampf(1.0 - t, 0.0, 1.0) * 0.55
		var drift := Vector2(10.0 * dir * t, -12.0 * t)
		draw_circle(drift, 6.0 + 12.0 * t, Color(0.80, 0.78, 0.72, smoke))
		draw_circle(drift + Vector2(8.0 * dir, 3.0), 4.0 + 9.0 * t, Color(0.74, 0.72, 0.66, smoke * 0.8))


func _draw_flank(attacker_flanks: bool) -> void:
	"""The flank march: a line drawn from the attacker's own side, along the
	foot of the baize (under the corps and the words under their feet), round
	the enemy lead's outer end and up onto his flank. It is a development,
	not a state: it fades once it has been told."""
	var sw: float = host._stage.size.x
	var sh: float = host._stage.size.y
	var from_left: bool = attacker_flanks == _attacker_left()
	var dir: float = 1.0 if from_left else -1.0
	var mid: float = sw / 2.0
	var foot: float = sh - 6.0
	var pts := PackedVector2Array([
		Vector2(mid - dir * 230.0, foot),
		Vector2(mid - dir * 20.0, foot),
		Vector2(mid + dir * 204.0, foot),
		Vector2(mid + dir * 228.0, foot - 14.0),
		Vector2(mid + dir * 228.0, foot - 44.0),
	])
	var line := Line2D.new()
	line.width = 3.0
	line.default_color = Color(GOLD, 0.9)
	line.joint_mode = Line2D.LINE_JOINT_ROUND
	line.points = PackedVector2Array([pts[0]])
	host._stage.add_child(line)
	host._transients.append(line)
	var head := Polygon2D.new()
	head.polygon = PackedVector2Array([
		Vector2(8.0, 0.0), Vector2(-6.0, -7.0), Vector2(-6.0, 7.0)])
	head.color = Color(GOLD, 0.9)
	head.position = pts[pts.size() - 1]
	head.rotation = pts[pts.size() - 2].direction_to(pts[pts.size() - 1]).angle()
	head.visible = false
	host._stage.add_child(head)
	host._transients.append(head)
	var tw: Tween = line.create_tween()
	for i in range(1, pts.size()):
		tw.tween_callback(line.add_point.bind(pts[i])).set_delay(0.16)
	tw.tween_callback(head.set_visible.bind(true))
	tw.tween_interval(1.6)
	tw.tween_property(line, "modulate:a", 0.0, 0.5)
	tw.parallel().tween_property(head, "modulate:a", 0.0, 0.5)


# =============================================================================
# The dice on the table
# =============================================================================
# The user's ruling: "Dice on the table". The attacker's two dice, each
# modifier of the roll named, what the roll did (it scales the blood the
# attack draws: 85% at 0 to 120% at 14) and each side's luck of the day (the
# ±10% the battle drew for its strength). Two ivory dice are DRAWN; the words
# are labels on the theme's own steps, laid out by their own measured heights.

class DiceTray:
	extends Control

	const TRAY_W := 300.0
	const DIE := 30.0
	# The tray stands between the banner's second line and the crossed
	# swords: 74 → 180 on the stage. A row that would not fit that room is
	# not printed over what stands below it (at Text size 150 % and over the
	# three rows need more: the last — the luck — is the one left off;
	# BA1-X4 owns the tableau's whole layout at those sizes).
	const ROOM_H := 106.0
	const IVORY := Color(0.93, 0.89, 0.78, 1.0)
	const IVORY_EDGE := Color(0.42, 0.36, 0.24, 1.0)
	const PIP := Color(0.13, 0.10, 0.07, 1.0)

	var _a := 1
	var _b := 1
	var _shown_a := 1
	var _shown_b := 1
	var _sum: Label = null
	var _sum_text := ""
	var _dice_x := 0.0

	func build(diorama, roll: Dictionary, luck_line: String) -> void:
		"""Call AFTER the tray is in the tree: the rows are placed by the
		heights the theme gives them."""
		mouse_filter = Control.MOUSE_FILTER_IGNORE
		var natural: int = clampi(int(roll.get("natural", 2)), 2, 12)
		var modified: int = int(roll.get("modified", natural))
		_a = clampi(int(ceil(natural / 2.0)), 1, 6)
		_b = clampi(natural - _a, 1, 6)
		_shown_a = _a
		_shown_b = _b
		_sum_text = "= %d" % modified
		_sum = diorama._mk_label(self, _sum_text, &"Lead", BattleActs.GOLD, diorama._font_engraved)
		diorama._outline_over_colours(_sum)
		var sum_size: Vector2 = _sum.get_minimum_size()
		var row_w: float = DIE * 2.0 + 8.0 + 10.0 + sum_size.x
		_dice_x = (TRAY_W - row_w) / 2.0
		_sum.position = Vector2(_dice_x + DIE * 2.0 + 18.0, (DIE - sum_size.y) / 2.0)

		var bits: Array = ["%d on the dice" % natural]
		if int(roll.get("skill", 0)) != 0:
			bits.append("+%d skill" % int(roll.get("skill", 0)))
		if int(roll.get("flank", 0)) != 0:
			bits.append("+%d flank" % int(roll.get("flank", 0)))
		var crit: String = str(roll.get("critical", ""))
		var lands := "the attack lands at %d%%" % (100 + int(roll.get("swing", 0)))
		if crit == "success":
			lands = "a twelve: " + lands
		elif crit == "failure":
			lands = "a two: " + lands
		var y: float = DIE + 5.0
		for text in ["   ".join(bits), lands, luck_line]:
			var row: Label = diorama._mk_label(self, str(text), &"Caption", BattleActs.BONE)
			diorama._outline_over_colours(row)
			var row_size: Vector2 = row.get_minimum_size()
			if y + row_size.y > ROOM_H:
				row.queue_free()
				break
			row.size = row_size
			row.position = Vector2((TRAY_W - row_size.x) / 2.0, y)
			y += row_size.y + 1.0
		size = Vector2(TRAY_W, y)
		custom_minimum_size = size
		queue_redraw()

	func settle() -> void:
		_shown_a = _a
		_shown_b = _b
		if _sum != null:
			_sum.text = _sum_text
		queue_redraw()

	func roll() -> void:
		"""The dice tumble and come to rest on what was rolled."""
		if _sum != null:
			_sum.text = ""
		var tw: Tween = create_tween()
		tw.tween_method(_tumble, 0.0, 9.0, 0.6)
		tw.tween_callback(settle)

	func _tumble(step: float) -> void:
		var i: int = int(step)
		_shown_a = (i * 5 + _a) % 6 + 1
		_shown_b = (i * 3 + _b + 2) % 6 + 1
		queue_redraw()

	func _draw() -> void:
		_draw_die(Vector2(_dice_x, 0.0), _shown_a)
		_draw_die(Vector2(_dice_x + DIE + 8.0, 0.0), _shown_b)

	func _draw_die(at: Vector2, value: int) -> void:
		var face := Rect2(at, Vector2(DIE, DIE))
		draw_rect(face, IVORY)
		draw_rect(face, IVORY_EDGE, false, 1.5)
		var c: Vector2 = at + Vector2(DIE, DIE) / 2.0
		var o: float = DIE * 0.27
		var spots: Array = []
		if value % 2 == 1:
			spots.append(c)
		if value >= 2:
			spots.append(c + Vector2(-o, -o))
			spots.append(c + Vector2(o, o))
		if value >= 4:
			spots.append(c + Vector2(o, -o))
			spots.append(c + Vector2(-o, o))
		if value == 6:
			spots.append(c + Vector2(-o, 0.0))
			spots.append(c + Vector2(o, 0.0))
		for s in spots:
			draw_circle(s, DIE * 0.085, PIP)
