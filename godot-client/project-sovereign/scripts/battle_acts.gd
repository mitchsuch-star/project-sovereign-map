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

# ── Row BA, session BA-2: the order of battle ───────────────────────────────
# The user's words of November 14, 2026 (BATTLE_DIORAMA_SPEC.md §15.11):
# "watching an interesting strategic battle with flanks and movements unfold",
# "an engaging autobattler", "they should move in napoleonic style". A side
# seats THREE corps (the backend's cap): the lead in the centre and most
# advanced, a wing behind him on either side. The stations are the LEFT
# side's, in the stage's pixels (the right mirrors x → width − x); they were
# laid out against the real label boxes, the dice tray, the crossed swords,
# the banner and the loss counters at Text size 100 % and the shipped 115 %.
# `_relay` keeps the host's file when the table cannot take them — an old
# payload that seats four, a duel of one corps a side, Text size 120 % and
# over (`_wedge_is_clear` measures the live boxes). One constant reverses it.
#
# Row BA, BA-4 (BA3-X2, November 16, 2026) — the file at 120 % and over is the
# RULED layout, and the table says why it kept it (`_laid_why`, `wedge_faults`).
# Measured at 130 % on the two wedge scenes: the near wing's captions run 19 px
# below the baize and the far wing's stand 18 px on the near wing. Moving the
# stations does not clear it: no pair of heights clears both (raised enough,
# the far wing stands on its side's loss counter: 10 to 25 px), and stepped in
# beside the counter (near 128,356 / far 190,136 — which passes this file's own
# test) the far wing stands, at rest, on the reserve's note, on the losses'
# caption and on the banner. Two stacked corps with their captions need about
# 40 px more than the baize has at that size.
const ORDER_OF_BATTLE := true
const WEDGE_LEAD := Vector2(330.0, 342.0)
const WEDGE_NEAR := Vector2(128.0, 380.0)
const WEDGE_FAR := Vector2(128.0, 182.0)
const WEDGE_ROLES := ["lead", "near", "far"]
const SAFE_GAP := 3.0           # two corps' words and bodies never stand closer
const GUN_POCKET := Vector2(292.0, 136.0)   # the off-field gun's place on a wedge (left side)
const RESERVE_NOTE_Y := 24.0    # the reserve's note stands beside its side's loss counter
const COLUMN_SQUEEZE := 0.32    # a corps in column: its files closed up to this much of the line
# The host's own two figures (battle_diorama.gd): where `_make_block` plants a
# corps' standard (38 art px toward the clash) and how far `_schedule_standards`
# advances the victor's on a defeat (its alarm register).
const STANDARD_AT := 38.0
const ALARM_ADVANCE := 60.0
# The host shudders a line that takes fire (`DioramaFigure.recoil`: 0.25 s,
# 0.15 s a rank later) and puts each man back where he stood WHEN IT WAS
# SCHEDULED. A verb that moves men as the fight opens waits it out.
const AFTER_THE_RECOIL := 0.45

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
# BA-2: the board and the two new tables.
var _laid := "file"                    # "wedge" when the order of battle is laid
var _laid_why: Array = []              # BA3-X2: what the wedge would have stood on (the walk reads it)
var _reserve_dead: Array = []          # the reserve's dead, a line of its own on a wedge
var _wall: SiegeWall = null            # a garrison's wall (kind "assault")
var _works: Dictionary = {}            # corps name -> its Rampart (field works)
var _squares: Array = []               # the ground marks of corps in square


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
	_laid = "file"
	_laid_why = []
	_reserve_dead = []
	_wall = null
	_works = {}
	_squares = []
	# BA-2: the order of battle, laid BEFORE a corps' home is read — everything
	# after this stands on the station it is given here.
	var relaid: Array = _relay()
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
		if bool(c.get("garrison", false)):
			_dress_garrison(b)
	if not relaid.is_empty() and not _wedge_is_clear():
		_unrelay(relaid)
	if _kind() == "assault":
		_build_the_wall()      # before the rest is planned: the stormers stop at its foot
	_plan_rest()
	_keep_the_end()
	_dress_the_kind()
	_build_the_day()       # BA-3: hidden; shown at rest, never while the acts play

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


# ─────────────────────────────────────────────────────────────────────────────
# BA-2: the order of battle
# ─────────────────────────────────────────────────────────────────────────────

func _kind() -> String:
	"""A field battle ("battle"), a garrison assault ("assault") or a
	standalone bombardment ("bombardment"): the payload says which table to
	lay (backend/game_logic/siege_diorama.py)."""
	return str(host._data.get("kind", "battle")) if host != null else "battle"


func _relay() -> Array:
	"""Each side's lead in the centre and most advanced, its second corps on
	the near wing and its third on the far wing. Returns what it moved — to be
	put back if the table cannot take it — or [] where the host's file
	stands: the switch is off, a duel of one corps a side, or an old payload
	that seats four."""
	if not ORDER_OF_BATTLE:
		return []
	var sides: Array = [host._blocks_left, host._blocks_right]
	var most: int = maxi((sides[0] as Array).size(), (sides[1] as Array).size())
	if most < 2 or most > WEDGE_ROLES.size():
		return []
	var sw: float = host._stage.size.x
	var stations: Array = [WEDGE_LEAD, WEDGE_NEAR, WEDGE_FAR]
	var saved: Array = []
	for side in sides:
		for k in range((side as Array).size()):
			var b: Dictionary = side[k]
			var node: Node2D = b["node"]
			var boxes: Array = []
			for child in node.get_children():
				if child is Label:
					var l: Label = child
					boxes.append([l, l.position, l.size, l.custom_minimum_size, l.autowrap_mode])
			saved.append({"block": b, "position": node.position, "z": node.z_index,
					"depth": b["depth"], "boxes": boxes})
			var st: Vector2 = stations[k]
			var to: Vector2 = st if bool(b["is_left"]) else Vector2(sw - st.x, st.y)
			_recut_captions(b, to)
			node.position = to
			# the nearer corps draws over the farther; the wings fall together
			# (the host staggers its topples by depth)
			node.z_index = 20 - [1, 0, 2][k]
			b["depth"] = 0 if k == 0 else 1
			b["role"] = WEDGE_ROLES[k]
	_laid = "wedge"
	return saved


func _unrelay(saved: Array) -> void:
	"""The table could not take the order of battle (a pair of lines closer
	than SAFE_GAP: Text size 120 % and over, a name longer than any the
	stations were laid for): every corps back on the host's file, its words
	as the host cut them, and the acts' own fitting run again from there."""
	_laid_why = wedge_faults()             # BA3-X2: measured while the wedge still stands
	for row in saved:
		var b: Dictionary = row["block"]
		var node: Node2D = b["node"]
		node.position = row["position"]
		node.z_index = int(row["z"])
		b["depth"] = row["depth"]
		b.erase("role")
		for box in row["boxes"]:
			var l: Label = box[0]
			if not is_instance_valid(l):
				continue
			l.autowrap_mode = box[4]
			l.custom_minimum_size = box[3]
			l.size = box[2]
			l.position = box[1]
		b["home"] = node.position
		_keep_words_on_the_baize(b)
	_laid = "file"


func _recut_captions(b: Dictionary, to: Vector2) -> void:
	"""The host cut each caption under a corps' feet to the baize's margin from
	the place it laid the corps (`_keep_fate_on_baize`): at its station the
	same rule is read again from there."""
	var left: bool = bool(b["is_left"])
	var pad: float = host.BAIZE_PAD
	var full: float = host.FAITH_CAPTION_W
	for child in (b["node"] as Node2D).get_children():
		if not (child is Label) or (child as Label).position.y < 0.0:
			continue
		var l: Label = child
		var w: float
		if left:
			var inboard: float = l.position.x + l.size.x
			w = maxf(inboard - maxf(inboard - full, pad - to.x), host.FATE_MIN_W)
			l.position.x = inboard - w
		else:
			w = maxf(minf(l.position.x + full, host._stage.size.x - pad - to.x) - l.position.x,
					host.FATE_MIN_W)
		if l.autowrap_mode != TextServer.AUTOWRAP_OFF:
			l.custom_minimum_size.x = w
		l.size.x = w


func _on_stage(item: CanvasItem, local: Rect2) -> Rect2:
	"""`local` (in the item's own space) in the stage's pixels."""
	var xf: Transform2D = host._stage.get_global_transform().affine_inverse() \
			* item.get_global_transform()
	return Rect2(xf * local.position, Vector2.ZERO).expand(xf * local.end)


func _label_ink(l: Label) -> Rect2:
	"""A line's own extent on the stage (a label's box is wider than its
	words: the two leads' name boxes overlap by design, their words do not)."""
	var need: Vector2 = l.get_minimum_size()
	var wrapped: bool = l.autowrap_mode != TextServer.AUTOWRAP_OFF
	var w: float = l.size.x if wrapped else minf(l.size.x, need.x)
	var h: float = maxf(l.size.y, need.y) if wrapped else minf(l.size.y, need.y)
	var x := 0.0
	if l.horizontal_alignment == HORIZONTAL_ALIGNMENT_RIGHT:
		x = l.size.x - w
	elif l.horizontal_alignment == HORIZONTAL_ALIGNMENT_CENTER:
		x = (l.size.x - w) / 2.0
	return _on_stage(l, Rect2(x, 0.0, w, h))


func _words(b: Dictionary) -> Array:
	"""Every line a corps carries, shown or held back (a held-back line WILL
	be shown: the table must have room for it)."""
	var out: Array = []
	for child in (b["node"] as Node2D).get_children():
		if child is Label and (child as Label).text.strip_edges() != "":
			out.append(_label_ink(child))
	return out


func _body(b: Dictionary) -> Array:
	"""The slab with its men, and the portrait: what a neighbour's words may
	not stand on."""
	var out: Array = []
	var art: Node2D = (b["node"] as Node2D).get_node_or_null("Art")
	if art != null:
		out.append(_on_stage(art, Rect2(-DioramaPlinth.HALF_W, -50.0,
				DioramaPlinth.HALF_W * 2.0, 74.0)))
	var locket: Control = b["locket"]
	if locket != null and is_instance_valid(locket) and locket.visible:
		out.append(_on_stage(locket, Rect2(Vector2.ZERO, locket.size)))
	return out


func _chrome_rects() -> Array:
	"""What already stands on the baize: the loss counters, the crossed
	swords and the dice tray's room."""
	var out: Array = []
	for piece in [host._odo_left_cap, host._odo_left, host._odo_right_cap, host._odo_right,
			host._clash_label]:
		if piece is Label and is_instance_valid(piece):
			out.append(_label_ink(piece))
	out.append(Rect2(host._stage.size.x / 2.0 - 110.0, 74.0, 220.0, DiceTray.ROOM_H))
	return out


func _wedge_is_clear() -> bool:
	"""No line of a corps off the baize, on the chrome, or within SAFE_GAP of
	a neighbour's line, slab or portrait — measured on the live boxes."""
	var sw: float = host._stage.size.x
	var sh: float = host._stage.size.y
	var pad: float = host.BAIZE_PAD
	var chrome: Array = _chrome_rects()
	for side in [host._blocks_left, host._blocks_right]:
		for a in side:
			var words: Array = _words(a)
			for r in words:
				var rect: Rect2 = r
				if rect.position.x < pad - 1.0 or rect.end.x > sw - pad + 1.0 \
						or rect.position.y < 0.0 or rect.end.y > sh:
					return false
				for c in chrome:
					if rect.grow(SAFE_GAP).intersects(c):
						return false
			for other in side:
				if other == a:
					continue
				var theirs: Array = _words(other) + _body(other)
				for r in words:
					for o in theirs:
						if (r as Rect2).grow(SAFE_GAP).intersects(o):
							return false
	return true


func _corps_named(b: Dictionary) -> String:
	return str((b["data"] as Dictionary).get("name", ""))


func wedge_faults() -> Array:
	"""BA3-X2 (row BA, BA-4): every reason `_wedge_is_clear` would refuse the
	order of battle as it stands now — which corps' line leaves the baize,
	stands on the chrome, or comes within SAFE_GAP of a neighbour's line, slab
	or portrait, and by how many pixels the two overlap. For the walk and the
	record only: the table's own test is `_wedge_is_clear`, unchanged."""
	var out: Array = []
	var sw: float = host._stage.size.x
	var sh: float = host._stage.size.y
	var pad: float = host.BAIZE_PAD
	var chrome: Array = _chrome_rects()
	for side in [host._blocks_left, host._blocks_right]:
		for a in side:
			var words: Array = _words(a)
			for r in words:
				var rect: Rect2 = r
				if rect.position.x < pad - 1.0 or rect.end.x > sw - pad + 1.0 \
						or rect.position.y < 0.0 or rect.end.y > sh:
					out.append("%s: a line leaves the baize (x %d to %d, y %d to %d)" % [
						_corps_named(a), int(rect.position.x), int(rect.end.x),
						int(rect.position.y), int(rect.end.y)])
				for c in chrome:
					var met: Rect2 = rect.grow(SAFE_GAP).intersection(c)
					if met.has_area():
						out.append("%s: a line stands on the chrome by %d x %d px" % [
							_corps_named(a), int(met.size.x), int(met.size.y)])
			for other in side:
				if other == a:
					continue
				var theirs_words: Array = _words(other)
				var theirs_body: Array = _body(other)
				for r in words:
					for o in theirs_words:
						var w: Rect2 = (r as Rect2).grow(SAFE_GAP).intersection(o)
						if w.has_area():
							out.append("%s: a line meets a line of %s by %d x %d px" % [
								_corps_named(a), _corps_named(other), int(w.size.x), int(w.size.y)])
					for o in theirs_body:
						var bd: Rect2 = (r as Rect2).grow(SAFE_GAP).intersection(o)
						if bd.has_area():
							out.append("%s: a line meets the slab or portrait of %s by %d x %d px" % [
								_corps_named(a), _corps_named(other), int(bd.size.x), int(bd.size.y)])
	return out


func _room_fwd(b: Dictionary) -> float:
	"""How far a lead may go toward the clash before a line of his crosses the
	centre or meets the crossed swords."""
	var mid: float = host._stage.size.x / 2.0
	var left: bool = bool(b["is_left"])
	var swords: Rect2 = _label_ink(host._clash_label)
	var room := 400.0
	for r in _words(b):
		var rect: Rect2 = r
		var edge: float = rect.end.x if left else rect.position.x
		var limit: float = (mid - 6.0 - edge) if left else (edge - mid - 6.0)
		if rect.position.y < swords.end.y and rect.end.y > swords.position.y:
			limit = minf(limit, (swords.position.x - 6.0 - edge) if left
					else (edge - swords.end.x - 6.0))
		room = minf(room, limit)
	return maxf(room, 0.0)


func _clear_back(b: Dictionary, side: Array, want: float) -> float:
	"""How far of `want` px a corps can fall back toward its own edge before
	its words or its body come within SAFE_GAP of a neighbour's."""
	var mine: Array = _words(b) + _body(b)
	var theirs: Array = []
	for other in side:
		if other != b:
			theirs += _words(other) + _body(other)
	var step := Vector2(_outward(b) * 2.0, 0.0)
	var got := 0.0
	while got + 2.0 <= want:
		var shift: Vector2 = step * (got / 2.0 + 1.0)
		for r in mine:
			var moved := Rect2((r as Rect2).position + shift, (r as Rect2).size)
			for o in theirs:
				if moved.grow(SAFE_GAP).intersects(o):
					return got
		got += 2.0
	return got


func _dress_garrison(b: Dictionary) -> void:
	"""A garrison has no commander: no portrait, and no standard to take. Its
	fate is the wall's — STORMED or CAPITULATED where a corps reads DESTROYED."""
	(b["locket"] as CanvasItem).visible = false
	var std = b["standard"]
	if std != null and is_instance_valid(std):
		(std as CanvasItem).visible = false
	var word: Label = b["status_label"]
	if word != null and is_instance_valid(word):
		match str(host._data.get("fate", "")):
			"stormed":
				word.text = "STORMED"
			"capitulated":
				word.text = "CAPITULATED"


func _dress_the_kind() -> void:
	"""What a table carries beyond its corps: the banner's own words, the
	reserve's note on a wedge, a garrison's wall, field works, the ground mark
	of a corps in square."""
	var banner: String = str(host._data.get("banner", ""))
	if banner != "" and banner != "<null>":
		host._banner.text = banner
	var sub: String = str(host._data.get("sub_banner", ""))
	if sub != "" and sub != "<null>" and host._sub_banner.text == "":
		host._sub_banner.text = sub
	if _laid == "wedge":
		_rehome_the_reserve()
	_build_the_works()
	_mark_the_squares()


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
	# BA-3: a day's panel lent its room (the verdict, the plate, the seal);
	# every table that is laid takes those three back (the laurels' visibility
	# is the host's `_laurel_layout`, run at every populate before this).
	host._verdict.visible = true
	host._nameplate.visible = true
	if host._seal != null:
		host._seal.visible = true
	# BA-3: the primary button and Replay stand as they were built ("His answer ▸"
	# widened Close on a table whose clash is followed)
	host._btn_close.text = "Close"
	host._btn_close.reset_size()
	host._btn_close.position = Vector2(host.TRAY_W - 154.0, host.TRAY_H - 46.0)
	host._btn_replay.position = Vector2(host.TRAY_W - 274.0, host.TRAY_H - 46.0)
	# BA-3: the headline a day's banner replaced comes back (the host's own words
	# and colour for this payload's register — what its populate set)
	var register := str(host._data.get("register", "observer"))
	host._banner.text = host._banner_text(register)
	host._banner.add_theme_color_override("font_color", host._banner_color(register))


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


# ─────────────────────────────────────────────────────────────────────────────
# BA-3: the day's panel (a great battle that did not decide the day)
# ─────────────────────────────────────────────────────────────────────────────
# The payload's `day` block (backend/game_logic/battle_day.py): both purses,
# the morning line, the last of what was told, and — when it is ours to speak —
# the chips. It is a RESULT mark: built hidden, held back while the acts play,
# shown at rest in the room of the verdict, the name plate and the seal (the
# tray does not grow). A payload without `day` builds nothing at all.

const DAY_X := 30.0
const DAY_W := 940.0
const DAY_BOTTOM := 738.0              # the tray's floor, less its edge
const DAY_CHIPS_W := 680.0             # clear of Replay (x 726) and Close (x 846) at y 698
const DAY_CHIP_BG := "233043"
const DAY_EXIT_BG := Utils.COLOR_CHIP_BG_GREEN   # "Leave it to ..." ends our say: a different ground
const DAY_PIP_ON := "d9c08c"
const DAY_PIP_OFF := Utils.CHIP_DIM_INK   # a spent point (the locked chip's own grey)
const DAY_OWN_KINDS := ["press", "guard", "dig_in"]            # the lead's own words (row C)
const DAY_EXIT_KINDS := ["stand", "break_off"]                 # the exits (row E, with leave_it)
const DAY_GROUP_LABEL := {"lead": "Another leads", "bring_up": "Bring up", "cannonade": "The guns"}

var _day_panel: Control = null
var _day_chips: RichTextLabel = null   # row C: the lead's own words, full chips
var _day_groups: RichTextLabel = null  # rows D: one line per kind, a label then name-only chips
var _day_exits: RichTextLabel = null   # row E: the exits, always on the table, never scrolled
var _day_latched := false              # one press, one word: inert until new data
var _day_asked := false                # a day awaiting HIS word asked the server once
var _day_hide_shelves := false         # the panel took the shelves' room
var _day_inline := false               # the groups flow in one paragraph (room was short)
var _his_waiting := false              # a table whose clash is followed by his waits to go on
const DAY_ADVANCE_S := 2.5             # at rest on such a table, then his clash by itself

# Row BA, BA-4 (the user's ruling at the plan gate, November 16, 2026 — "Yes, on
# the table"): while the table awaits our word the bare digits press the day's
# chips, in FIXED slots as the selection card's are (a slot never moves): 1 the
# lead presses / strikes back, 2 the Guard, 3 he digs in, 4-6 the first three
# chips of the other kinds (another corps leads, the guns, a corps brought up)
# in the server's own order, 7 he stands, 8 break off / fall back, 9 leave it
# to him. A chip past the sixth of its kind is the mouse's and shows no digit.
# Who owns the bare digits OFF the table stays WS-10's ruling (Session H).
const DAY_DIGIT_OWN := {"press": 1, "guard": 2, "dig_in": 3}
const DAY_DIGIT_GROUP_FROM := 4
const DAY_DIGIT_GROUP_TO := 6
const DAY_DIGIT_STAND := 7
const DAY_DIGIT_BREAK := 8
const DAY_DIGIT_LEAVE := 9
const DAY_DENY_CUE := "error"          # the selection card's cue for a slot that cannot fire
var _day_digit_of: Dictionary = {}     # index into `chips` -> its digit
var _day_denied := 0                   # digits this table refused with the deny cue (the walk reads it)
# Row BA, BA-4 (the user's tick — "First-open line"): the first day of battle of
# a campaign names its own rules, once (the block's `first_open`) — on a row of
# its own above the head where the table has the room for it whole, else on the
# head's hover (a hover is not a showing: it is then not acknowledged and comes
# again on the next day's table). The showing is acknowledged to the scene that
# holds the API client (main.gd `_on_first_open_seen`) — never as a word.
var _day_first_screen := ""            # the screen to acknowledge when the panel is shown
var _day_first_shown := ""             # the screen whose line this table has shown (the walk reads it)


func _the_day() -> Dictionary:
	var d = host._data.get("day", null) if host != null else null
	return d if d is Dictionary else {}


func _day_pips(left: int, slots: int) -> String:
	var out := ""
	for i in range(slots):
		out += Utils.bb_icon(Utils.SWATCH, 10, DAY_PIP_ON if i < left else DAY_PIP_OFF)
		out += " "
	return out


func _day_rtl(parent: Control, at: Vector2, size: Vector2) -> RichTextLabel:
	var l := RichTextLabel.new()
	l.bbcode_enabled = true
	l.fit_content = false
	l.scroll_active = false
	l.selection_enabled = false
	l.focus_mode = Control.FOCUS_NONE        # Esc / Enter / Space keep their meaning
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	l.theme_type_variation = &"BodyLargeRich"
	l.position = at
	l.size = size
	parent.add_child(l)
	return l


func _day_line_h(l: RichTextLabel) -> float:
	"""The font's own line (more at 115 % and 130 % text size)."""
	var f: Font = l.get_theme_font(&"normal_font")
	var sz: int = l.get_theme_font_size(&"normal_font_size")
	return maxf(f.get_height(sz) if f != null else 27.0, 20.0)


func _day_road(day: Dictionary) -> String:
	var road = day.get("his_road", null)
	if road is bool:
		return "his road is open" if road else "no road behind him"
	return ""


func _day_head(day: Dictionary, level: int) -> String:
	"""One line: the lead and his purse against the enemy and his; then — as
	room allows — his temper (level 1) and whether a road lies open behind him
	(level 2)."""
	var ours: int = int(day.get("ours", 0))
	var theirs: int = int(day.get("theirs", 0))
	var ours_of: int = int(day.get("ours_of", 0))
	var theirs_of: int = int(day.get("theirs_of", 0))
	var lead := str(day.get("lead_shown", ""))
	var foe := str(day.get("enemy_shown", ""))
	var out := ""
	if level >= 3:
		out = "[color=#" + Utils.COLOR_INFO + "]The day's points —[/color] "
	out += "[color=#" + Utils.COLOR_GOLD + "]" + lead + "[/color] " \
		+ _day_pips(ours, ours_of if ours_of > 0 else maxi(ours, 2)) \
		+ " [color=#" + Utils.COLOR_INFO + "]against[/color] [color=#" + Utils.COLOR_GOLD + "]" \
		+ foe + "[/color] " + _day_pips(theirs, theirs_of if theirs_of > 0 else maxi(theirs, 2))
	var info := "[color=#" + Utils.COLOR_INFO + "]"
	if level >= 1 and str(day.get("his_temper", "")) != "":
		out += " " + info + "· " + str(day.get("his_temper", "")) + "[/color]"
	if level >= 2 and _day_road(day) != "":
		out += " " + info + "· " + _day_road(day) + "[/color]"
	return out


func _day_told_lines(day: Dictionary) -> Array:
	var out: Array = []
	var told = day.get("told", [])
	if told is Array:
		for t in told:
			if t is Dictionary and str(t.get("line", "")) != "":
				out.append(t)
	return out


func _day_told(lines: Array, keep: int) -> String:
	var out := ""
	var from: int = maxi(0, lines.size() - keep)
	for i in range(from, lines.size()):
		var t: Dictionary = lines[i]
		var who := str(t.get("who", ""))
		var hex := Utils.COLOR_GOLD if who == "ours" else (Utils.COLOR_INFO if who == "end" else Utils.COLOR_TEXT)
		var line := str(t.get("line", ""))
		line = "[i]" + line + "[/i]" if who == "end" else line
		out += ("\n" if out != "" else "") + "[color=#" + hex + "]" + line + "[/color]"
	return out


func _day_chip_label(chip: Dictionary) -> String:
	"""A word that costs nothing shows no price. (The server's label is shown
	as it is: "Mack strikes back" is never rewritten here.)"""
	var price := int(chip.get("price", 0))
	var label := str(chip.get("label", ""))
	return label if price <= 0 else "%s · %d" % [label, price]


func _day_chip_tip(chip: Dictionary, with_label: bool = false) -> String:
	var parts: Array = []
	if with_label:
		parts.append(_day_chip_label(chip) + ".")
	if not bool(chip.get("ok", false)) and str(chip.get("why", "")) != "":
		parts.append(str(chip.get("why", "")))
	if str(chip.get("counsel", "none")) == "possible":
		parts.append("The marshal may object to this word.")
	if str(chip.get("odds", "")) != "":
		parts.append("The odds read: " + str(chip.get("odds", "")) + ".")
	return " ".join(PackedStringArray(parts))


func _day_offering() -> bool:
	var day := _the_day()
	return bool(day.get("open", false)) and str(day.get("awaits", "")) == "ours" \
		and not bool(day.get("pending", false)) and not bool(day.get("follows", false)) \
		and day.get("chips", []) is Array and not (day.get("chips", []) as Array).is_empty()


func _day_split() -> Array:
	"""[own, groups, exits]: indices into `chips`, IN THE ARRAY'S ORDER (the
	server orders them once for every surface; nothing is re-sorted here).
	`own` are the lead's press / Guard / dig-in; `groups` is a list of
	{kind, idx} for every other kind of word; `exits` are every "stands",
	"Break off" / "Fall back" and "Leave it to <lead>"."""
	var own: Array = []
	var groups: Array = []
	var exits: Array = []
	var chips = _the_day().get("chips", [])
	for i in range(chips.size()):
		var chip = chips[i]
		if not (chip is Dictionary):
			continue
		var kind := str(chip.get("kind", ""))
		if str(chip.get("word", "")) != "" or kind in DAY_EXIT_KINDS:
			exits.append(i)
		elif kind in DAY_OWN_KINDS:
			own.append(i)
		else:
			var found = null
			for g in groups:
				if g["kind"] == kind:
					found = g
			if found == null:
				found = {"kind": kind, "idx": []}
				groups.append(found)
			(found["idx"] as Array).append(i)
	return [own, groups, exits]


func _day_chip_bb(i: int, chip: Dictionary, name_only: bool = false) -> String:
	var leave: bool = str(chip.get("word", "")) == "leave_it"
	var label := _day_chip_label(chip)
	if name_only:
		label = str(chip.get("shown", "")) if str(chip.get("shown", "")) != "" else str(chip.get("label", ""))
	var digit: int = int(_day_digit_of.get(i, 0))
	if digit > 0:
		label = "%d %s" % [digit, label]          # the selection card's form: "<digit> Label"
	var tip := _day_chip_tip(chip, name_only)
	if bool(chip.get("ok", false)) and not _day_latched:
		return Utils.bb_button_chip("day:%d" % i, label,
				Utils.COLOR_WARNING if leave else Utils.COLOR_GOLD,
				DAY_EXIT_BG if leave else DAY_CHIP_BG, "", tip)
	return Utils.bb_chip_disabled(label, "", tip)


func _day_own_text() -> String:
	if not _day_offering():
		return ""
	var chips = _the_day().get("chips", [])
	var out := ""
	for i in _day_split()[0]:
		out += _day_chip_bb(int(i), chips[int(i)]) + " "
	return out


func _day_groups_text(inline: bool = false) -> String:
	"""One line per kind: a plain label once (with the price), then name-only
	chips. A kind with a single word is written whole. `inline`: every group
	flows in ONE paragraph with a clear gap between groups."""
	if not _day_offering():
		return ""
	var chips = _the_day().get("chips", [])
	var info := "[color=#" + Utils.COLOR_INFO + "]"
	var lines: Array = []
	for g in _day_split()[1]:
		var idx: Array = g["idx"]
		if idx.size() == 1:
			lines.append(_day_chip_bb(int(idx[0]), chips[int(idx[0])]) + " ")
			continue
		var first: Dictionary = chips[int(idx[0])]
		var price := int(first.get("price", 0))
		var label: String = str(DAY_GROUP_LABEL.get(g["kind"], first.get("label", "")))
		var line := info + label + (" · %d" % price if price > 0 else "") + ":[/color] "
		for i in idx:
			line += _day_chip_bb(int(i), chips[int(i)], true) + " "
		lines.append(line)
	return ("      " if inline else "\n").join(PackedStringArray(lines))


func _day_exits_text() -> String:
	var day := _the_day()
	if bool(day.get("open", false)) and str(day.get("awaits", "")) == "ours" \
			and bool(day.get("pending", false)):
		return "[color=#" + Utils.COLOR_INFO + "]A marshal's question waits on your answer, Sire.[/color]"
	if not _day_offering():
		return ""
	var chips = day.get("chips", [])
	var out := ""
	for i in _day_split()[2]:
		var chip: Dictionary = chips[int(i)]
		if str(chip.get("word", "")) == "leave_it":
			out += "[color=#" + Utils.COLOR_INFO + "]|[/color] "      # it ends our say: set apart
		out += _day_chip_bb(int(i), chip) + " "
	return out


func _day_digit_map() -> Dictionary:
	"""index into `chips` -> digit, for the day as it is offered (empty when it
	offers nothing). The slots are fixed; a kind that is not on the table
	leaves its digit unused."""
	var out := {}
	if not _day_offering():
		return out
	var chips = _the_day().get("chips", [])
	var split := _day_split()
	var taken := {}
	for i in split[0]:
		var kind := str((chips[int(i)] as Dictionary).get("kind", ""))
		if DAY_DIGIT_OWN.has(kind) and not taken.has(DAY_DIGIT_OWN[kind]):
			out[int(i)] = int(DAY_DIGIT_OWN[kind])
			taken[DAY_DIGIT_OWN[kind]] = true
	var next := DAY_DIGIT_GROUP_FROM
	for g in split[1]:
		for i in g["idx"]:
			if next > DAY_DIGIT_GROUP_TO:
				break
			out[int(i)] = next
			next += 1
	for i in split[2]:
		var chip: Dictionary = chips[int(i)]
		var d := DAY_DIGIT_BREAK
		if str(chip.get("word", "")) == "leave_it":
			d = DAY_DIGIT_LEAVE
		elif str(chip.get("kind", "")) == "stand":
			d = DAY_DIGIT_STAND
		if not taken.has(d):
			out[int(i)] = d
			taken[d] = true
	return out


static func day_digit(event: InputEvent) -> int:
	"""The bare digit 1-9 a key press is (the keypad's too; the physical key on
	a layout whose top row needs Shift), else 0. A press with a modifier is
	never the day's."""
	if not (event is InputEventKey):
		return 0
	var key: InputEventKey = event
	if not key.pressed or key.echo or key.ctrl_pressed or key.alt_pressed \
			or key.meta_pressed or key.shift_pressed:
		return 0
	for code in [key.keycode, key.physical_keycode]:
		if code >= KEY_1 and code <= KEY_9:
			return int(code) - int(KEY_0)
		if code >= KEY_KP_1 and code <= KEY_KP_9:
			return int(code) - int(KEY_KP_0)
	return 0


func day_keys_live() -> bool:
	"""The digits are the day's only on a table at rest that offers its chips."""
	return host != null and is_instance_valid(host) and host.visible and host._acts == self \
		and bool(host._final) and _day_panel != null and is_instance_valid(_day_panel) \
		and _day_panel.visible and _day_offering()


func day_key(event: InputEvent) -> bool:
	"""A bare digit on a table that awaits our word presses its slot's chip — a
	slot with no chip, a locked chip or a table already latched answers with
	the deny cue. True when the key was the day's: it goes no further (not to
	the command line, not to the selection card under the table)."""
	var n := day_digit(event)
	if n <= 0 or not day_keys_live():
		return false
	var index := -1
	for i in _day_digit_of:
		if int(_day_digit_of[i]) == n:
			index = int(i)
	var chips = _the_day().get("chips", [])
	if _day_latched or index < 0 or index >= chips.size() \
			or not bool((chips[index] as Dictionary).get("ok", false)):
		_day_denied += 1
		AudioManager.play(DAY_DENY_CUE)
		return true
	_on_day_chip("day:%d" % index)
	return true


class DayKeys:
	extends Node
	# The acts are a RefCounted and hear no key: this node, a child of the day's
	# panel (and freed with it), hears them for it — before the command line and
	# before main's own digits.
	var acts = null

	func _input(event: InputEvent) -> void:
		if acts != null and acts.day_key(event):
			get_viewport().set_input_as_handled()


func _day_retext() -> void:
	_day_digit_of = _day_digit_map()
	if _day_chips != null and is_instance_valid(_day_chips):
		_day_chips.text = _day_own_text()
	if _day_groups != null and is_instance_valid(_day_groups):
		_day_groups.text = _day_groups_text(_day_inline)
	if _day_exits != null and is_instance_valid(_day_exits):
		_day_exits.text = _day_exits_text()


func _shelf_up() -> bool:
	return (host._shelf_left != null and host._shelf_left.visible) \
		or (host._shelf_right != null and host._shelf_right.visible)


func _day_groups_h(d_box: RichTextLabel, inline: bool, start_abs: float, btn_top: float) -> float:
	"""What the groups' box measures laid stacked or inline: as wide as the
	panel when it ends above the buttons' top edge, else held clear of Replay."""
	d_box.text = _day_groups_text(inline)
	d_box.size.x = DAY_W
	var h: float = d_box.get_content_height()
	if start_abs + h > btn_top - 2.0:
		d_box.size.x = DAY_CHIPS_W
		h = d_box.get_content_height()
	return h


func _day_first_fits(above: float, d_box: RichTextLabel, e_top_abs: float, top: float,
		btn_top: float) -> bool:
	"""BA-4: with the first day's line on a row of its own, do the head, the
	lead's chips and the groups (stacked, or flowing inline) all stand whole
	above the exits, the shelves' room given and the told line sent to the
	hover if it must be? Those are the ladder's first three steps; the line
	never costs the fourth (a chip scrolled out of sight)."""
	var d_h := 0.0
	if d_box != null:
		d_h = minf(_day_groups_h(d_box, false, top + above, btn_top),
				_day_groups_h(d_box, true, top + above, btn_top))
	return above + d_h <= e_top_abs - 2.0 - top


func _note_first_open(screen: String) -> void:
	"""BA-4: the first day's line is on the table — the scene that holds the
	API client acknowledges it, once a world (main.gd `_on_first_open_seen`):
	the first ancestor of the tableau that can. A staged table (the acts' walk,
	the captures) stands under none: nothing is sent."""
	_day_first_shown = screen
	var node: Node = host if host != null and is_instance_valid(host) else null
	while node != null:
		if node.has_method("_on_first_open_seen"):
			node.call("_on_first_open_seen", screen)
			return
		node = node.get_parent()


func _day_banner() -> String:
	return str(_the_day().get("banner", ""))


func _build_the_day() -> void:
	"""At the end of the dress: the panel, hidden. Nothing for a payload that
	carries no `day` (a small battle, a fleet action, a harness world) or whose
	day was decided by its clash (its own verdict stands).
	Rows, top to bottom: A the head, B the last word told, C the lead's own
	words, D the other kinds of word, E the exits (centred on the buttons'
	row). Every row's height is what its text measures, so a row is whole or
	not there. Room is made in this order: the shelves give theirs, the groups
	flow inline, the told line rides the head's hover, the groups scroll."""
	_day_panel = null
	_day_chips = null
	_day_groups = null
	_day_exits = null
	_day_latched = false
	_day_asked = false
	_day_hide_shelves = false
	_day_inline = false
	_his_waiting = false
	_day_digit_of = {}
	_day_denied = 0
	_day_first_screen = ""
	_day_first_shown = ""
	var day := _the_day()
	if day.is_empty() or host == null or host._verdict == null:
		return
	if _day_banner() == "" and not bool(day.get("open", false)):
		return   # decided by its clash: that clash's verdict, plate and cues stand
	var top_with: float = host._verdict.position.y
	var shelf_up := _shelf_up()
	var top_free: float = top_with - (host.SHELF_H + 8.0) if shelf_up else top_with
	var panel := Control.new()
	panel.name = "DayPanel"
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	panel.visible = false
	host._tray_inner.add_child(panel)
	host._transients.append(panel)
	_day_panel = panel

	# the banner: a day that still hangs says so in the tableau's headline, in
	# the neutral colour; hidden until the result, like the headline itself
	var banner := _day_banner()
	if banner != "":
		host._banner.text = banner.to_upper()
		host._banner.add_theme_color_override("font_color", host._banner_color(""))
		# under it, the sub-banner tells how the last clash stood (won / lost /
		# drawn on points) — unless the host's own line is there (a province that
		# changed hands); the next populate sets its own text
		var morning_said := str(day.get("morning", ""))
		if morning_said != "" and host._sub_banner.text == "":
			host._sub_banner.text = morning_said

	var head := _day_rtl(panel, Vector2.ZERO, Vector2(DAY_W, 31.0))
	head.autowrap_mode = TextServer.AUTOWRAP_OFF
	var lh: float = _day_line_h(head)
	var head_h: float = lh + 4.0
	head.size.y = head_h
	# BA-4: the first day's own line (`first_open`), measured now and given its
	# row below only where the table has the room for it whole
	var first_said := ""
	var first_screen := ""
	var first_box: RichTextLabel = null
	var first_h := 0.0
	var fo = day.get("first_open", null)
	if fo is Dictionary and bool(day.get("open", false)):
		first_said = str(fo.get("line", ""))
		first_screen = str(fo.get("screen", ""))
	if first_said != "" and first_screen != "":
		first_box = _day_rtl(panel, Vector2.ZERO, Vector2(DAY_W, 100.0))
		first_box.name = "FirstOpen"
		first_box.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		first_box.text = "[color=#" + Utils.COLOR_INFO + "]" + first_said.replace("[", "[lb]") + "[/color]"
		first_h = first_box.get_content_height() + 2.0
		first_box.visible = false
	var level := 3
	head.text = _day_head(day, level)
	while level > 0 and head.get_content_width() > DAY_W - 8.0:
		level -= 1                            # one line at any text size: the prefix goes first
		head.text = _day_head(day, level)

	var hover: Array = []
	if str(day.get("morning", "")) != "":
		hover.append(str(day.get("morning", "")))
	if level < 2 and _day_road(day) != "":
		hover.append(str(day.get("his_temper", "")) + (" — " if str(day.get("his_temper", "")) != "" else "") + _day_road(day) + ".")
	var lines := _day_told_lines(day)
	var offering := _day_offering()
	var pending: bool = bool(day.get("open", false)) and bool(day.get("pending", false)) \
		and str(day.get("awaits", "")) == "ours"

	# the buttons' row: the exits stand level with Replay / Close, centred on them
	var btn_top: float = host._btn_close.position.y
	var btn_h: float = maxf(host._btn_close.size.y, host._btn_close.custom_minimum_size.y)
	var btn_mid: float = btn_top + btn_h / 2.0

	var top: float = top_with
	var total: float = DAY_BOTTOM - top
	var y: float = head_h
	if not offering and not pending:
		# no chips (closed, his word, his clash follows): the told block, whole
		# — and above the buttons' row
		if first_box != null and minf(DAY_BOTTOM, btn_top - 4.0) - top - head_h - first_h >= lh:
			first_box.visible = true          # the first day's line, above the head
			first_box.size.y = first_h
			head.position.y = first_h
			head_h += first_h
			y = head_h
			_day_first_screen = first_screen
		elif first_box != null:
			panel.remove_child(first_box)
			first_box.queue_free()
			hover.append(first_said)
		var avail: float = minf(DAY_BOTTOM, btn_top - 4.0) - top - head_h
		var keep := clampi(int(avail / lh), 1, 5)
		var told := _day_rtl(panel, Vector2(0.0, y), Vector2(DAY_W, lh * float(keep) + 2.0))
		told.text = _day_told(lines, keep)
	else:
		var split := _day_split()
		var c_box: RichTextLabel = null
		var d_box: RichTextLabel = null
		var e_box: RichTextLabel = null
		if offering and not (split[0] as Array).is_empty():
			c_box = _day_rtl(panel, Vector2.ZERO, Vector2(DAY_CHIPS_W, 100.0))
			c_box.mouse_filter = Control.MOUSE_FILTER_STOP
			c_box.meta_underlined = false
			c_box.autowrap_mode = TextServer.AUTOWRAP_OFF
			c_box.meta_clicked.connect(_on_day_chip)
		if offering and not (split[1] as Array).is_empty():
			d_box = _day_rtl(panel, Vector2.ZERO, Vector2(DAY_W, 100.0))
			d_box.mouse_filter = Control.MOUSE_FILTER_STOP
			d_box.meta_underlined = false
			d_box.meta_clicked.connect(_on_day_chip)
		e_box = _day_rtl(panel, Vector2.ZERO, Vector2(DAY_CHIPS_W, 100.0))
		e_box.mouse_filter = Control.MOUSE_FILTER_STOP
		e_box.meta_underlined = false
		e_box.autowrap_mode = TextServer.AUTOWRAP_OFF
		e_box.meta_clicked.connect(_on_day_chip)
		_day_chips = c_box
		_day_groups = d_box
		_day_exits = e_box
		_day_retext()
		# what each row measures (a row is a whole number of text rows)
		var c_h: float = c_box.get_content_height() if c_box != null else 0.0
		var e_h: float = e_box.get_content_height()
		var row_h: float = maxf(e_h, lh)
		var b_h: float = lh + 2.0 if (offering and not lines.is_empty()) else 0.0
		var e_top_abs: float = btn_mid - e_h / 2.0
		# BA-4: the first day's line takes its row wherever no chip has to
		# scroll for it (`_day_first_fits`). On a crowded table — Ulm, the
		# first great battle of a campaign — it may take the told line's row
		# for this one showing (the ladder's third step: the last word told
		# rides the head's hover, where the morning already is). Where even
		# that is not room enough it rides the hover itself and is NOT
		# acknowledged — a hover is not a showing.
		if first_box != null:
			if _day_first_fits(first_h + head_h + c_h, d_box, e_top_abs,
					top_free if shelf_up else top, btn_top):
				first_box.visible = true
				first_box.size.y = first_h
				head.position.y = first_h
				head_h += first_h
				y = head_h
				_day_first_screen = first_screen
			else:
				panel.remove_child(first_box)
				first_box.queue_free()
				hover.append(first_said)
		var d_h := 0.0
		var above: float = head_h + b_h + c_h
		if d_box != null:
			d_h = _day_groups_h(d_box, false, top + above, btn_top)
		var room: float = e_top_abs - 2.0 - top
		if above + d_h > room and shelf_up:
			top = top_free                    # 1. the shelves give their room, at rest
			total = DAY_BOTTOM - top
			_day_hide_shelves = true
			room = e_top_abs - 2.0 - top
			if d_box != null:
				d_h = _day_groups_h(d_box, false, top + above, btn_top)
		if d_box != null and above + d_h > room:
			_day_inline = true                # 2. the groups flow in one paragraph
			d_h = _day_groups_h(d_box, true, top + above, btn_top)
		if above + d_h > room and b_h > 0.0:
			b_h = 0.0                         # 3. the told line rides the head's hover
			above = head_h + c_h
			if d_box != null:
				d_h = _day_groups_h(d_box, _day_inline, top + above, btn_top)
		if d_box != null and above + d_h > room:
			# 4. whole text rows or nothing: the groups scroll by rows, never rows C or E
			var left: float = room - above
			var unit: float = maxf(row_h, 1.0)
			d_h = maxf(unit, floorf(left / unit) * unit)
			d_box.scroll_active = true
		if b_h > 0.0:
			var told := _day_rtl(panel, Vector2(0.0, y), Vector2(DAY_W, b_h))
			told.text = _day_told(lines, 1)
			y += b_h
		elif not lines.is_empty():
			hover.append(str((lines[lines.size() - 1] as Dictionary).get("line", "")))
		if c_box != null:
			c_box.position = Vector2(0.0, y)
			c_box.size = Vector2(DAY_CHIPS_W, c_h)
			y += c_h
		if d_box != null:
			d_box.position = Vector2(0.0, y)
			d_box.size = Vector2(d_box.size.x, d_h)
			y += d_h
		e_box.position = Vector2(0.0, e_top_abs - top)    # level with, and centred on, the buttons
		e_box.size = Vector2(DAY_CHIPS_W, e_h)
		if offering:
			var keys := DayKeys.new()             # BA-4: the bare digits press the chips
			keys.name = "DayKeys"
			keys.acts = self
			panel.add_child(keys)
	panel.position = Vector2(DAY_X, top)
	panel.size = Vector2(DAY_W, total)
	if not hover.is_empty():
		head.mouse_filter = Control.MOUSE_FILTER_STOP
		head.text = Utils.bb_hint(head.text, " ".join(PackedStringArray(hover)))
	# a result mark: it comes in when the table is FINAL (the skip hint gone,
	# Replay and Close there) — never together with the skip hint
	if host._skip_hint != null and host._skip_hint.visible:
		host._skip_hint.visibility_changed.connect(_on_skip_hint_changed, CONNECT_ONE_SHOT)


func _on_skip_hint_changed() -> void:
	if host == null or not is_instance_valid(host) or host._acts != self or host._skip_hint.visible:
		return
	if _day_panel == null or not is_instance_valid(_day_panel) or _day_panel.is_queued_for_deletion():
		return
	_show_the_day()


func _on_day_chip(meta) -> void:
	if _day_latched:
		return
	var s := str(meta)
	if not s.begins_with("day:"):
		return
	var day := _the_day()
	var chips = day.get("chips", [])
	var i := int(s.substr(4))
	if not (chips is Array) or i < 0 or i >= chips.size():
		return
	var chip = chips[i]
	if not (chip is Dictionary) or not bool(chip.get("ok", false)):
		return
	var word := str(chip.get("word", ""))
	var command := "@word:%s:%s" % [word, str(day.get("enemy", ""))] if word != "" \
		else str(chip.get("command", ""))
	if command == "":
		return
	_day_latched = true                       # one press, one word
	_day_retext()
	host.word_given.emit(command)


func release_the_day() -> void:
	"""Main refused the word (another order on the wire): the chips come back."""
	_day_latched = false
	_day_retext()


func _hold_the_day_back() -> void:
	"""A result mark: not on the table while the acts play."""
	if _day_panel != null and is_instance_valid(_day_panel):
		_day_panel.visible = false


func _show_the_day() -> void:
	"""At rest: the panel takes the room of the verdict, the name plate and the
	seal (and the laurels that flank the plate). The next table laid gives them
	back: `_put_the_chrome_back` restores the verdict, the plate and the seal,
	and the host's own `_laurel_layout` sets the laurels' visibility afresh on
	every populate. The tableau does not grow."""
	if _day_panel == null or not is_instance_valid(_day_panel):
		return
	host._verdict.visible = false
	host._nameplate.visible = false
	if host._seal != null:
		host._seal.visible = false
	for laurel in _laurels():
		(laurel as CanvasItem).visible = false
	if _day_hide_shelves:
		# the panel needs the shelves' room (the rows did not fit under the
		# faction bars): they stand again at the next table laid (the host's
		# populate sets their visibility afresh)
		for shelf in [host._shelf_left, host._shelf_right]:
			if shelf != null:
				(shelf as CanvasItem).visible = false
	_day_panel.visible = true
	if _day_first_screen != "":
		# BA-4: the first day's line is on the table now — the showing is the
		# acknowledgement (the scene sends it once a world: `_on_first_open_seen`)
		_note_first_open(_day_first_screen)
		_day_first_screen = ""
	var day := _the_day()
	var follows: bool = bool(day.get("follows", false))
	# a day that opened on a road which did not carry his answer — or a table that
	# awaits OUR word and carries none of its chips (a stale tableau from any
	# road): ask once a showing; the answer (main.gd) refreshes the panel or
	# shows his clash next
	var open: bool = bool(day.get("open", false))
	var chipless: bool = str(day.get("awaits", "")) == "ours" and not bool(day.get("pending", false)) \
		and (day.get("chips", []) as Array).is_empty()
	if not _day_asked and open and not follows \
			and (str(day.get("awaits", "")) == "theirs" or chipless):
		_day_asked = true
		host.word_given.emit("@refresh:" + str(day.get("enemy", "")))
	if follows:
		# his clash is next: the primary button says so, and after a rest the
		# table goes on by the same road as the button (not under Reduce Motion)
		host._btn_close.text = "His answer ▸"
		host._btn_close.reset_size()
		host._btn_close.position.x = host.TRAY_W - 44.0 - host._btn_close.size.x
		host._btn_replay.position.x = host._btn_close.position.x - 10.0 - host._btn_replay.size.x
		if not _his_waiting and not UiSettings.get_reduce_motion() and host.is_inside_tree():
			_his_waiting = true
			host.get_tree().create_timer(DAY_ADVANCE_S).timeout.connect(_his_answer_comes)


func _his_answer_comes() -> void:
	"""The rest is over: on to his clash — the primary button's own road. A
	Replay (a new showing), a close or a skip in the meantime cancels it."""
	if host == null or not is_instance_valid(host) or host._acts != self or not host.visible \
			or not host._final or not _his_waiting:
		return
	_his_waiting = false
	host._btn_close.pressed.emit()


func _clear_the_room() -> void:
	"""At the gavel: the verdict, the plate, the seal and the laurels give their
	room NOW (they would flash otherwise); the panel itself waits for the table
	to be final."""
	if _day_panel == null or not is_instance_valid(_day_panel):
		return
	host._verdict.visible = false
	host._nameplate.visible = false
	if host._seal != null:
		host._seal.visible = false
	for laurel in _laurels():
		(laurel as CanvasItem).visible = false


func _type_the_verdict() -> void:
	"""The host writes the verdict (the quill, and the fanfare or the bell) —
	not over a day's own banner. A day decided by its clash keeps both."""
	if _day_panel != null and is_instance_valid(_day_panel):
		return
	host._type_verdict()


func _tell_the_reserves_dead() -> void:
	for tail in _reserve_tails:
		if is_instance_valid(tail["label"]):
			(tail["label"] as Label).text = str(tail["full"])
	# BA-2: on a wedge the reserve's dead is a line of its own
	for dead in _reserve_dead:
		if is_instance_valid(dead):
			(dead as Label).visible = true


func _rehome_the_reserve() -> void:
	"""BA-2. On a wedge the baize's bottom corner is the near wing's, so the
	reserve's note stands beside its side's loss counter: how many corps wait
	behind the line and, on a line of its own that comes with the gavel as
	every figure of the end does, what they lost. It is set clear of the
	counter's own figure at its FINAL width."""
	var sw: float = host._stage.size.x
	var sides: Array = host._side_payloads()
	for node in host._transients:
		if not (node is Label) or not is_instance_valid(node):
			continue
		var tail: Label = node
		if not tail.text.contains(" corps in reserve"):
			continue
		var left: bool = tail.position.x < sw / 2.0
		var odo: Label = host._odo_left if left else host._odo_right
		var shown: String = odo.text
		odo.text = Utils.format_number(int((sides[0 if left else 1] as Dictionary).get(
				"casualties_total", 0)))
		var figure_w: float = odo.get_minimum_size().x
		odo.text = shown
		var edge: float = maxf(14.0 + figure_w + 12.0, 104.0)
		var full: String = tail.text
		var cut: int = full.find(RESERVE_DEAD)
		tail.autowrap_mode = TextServer.AUTOWRAP_OFF
		tail.text = (full.substr(0, cut) if cut >= 0 else full).replace(
				" corps in reserve", " in reserve")
		tail.size = tail.get_minimum_size()
		tail.position = Vector2(edge if left else sw - edge - tail.size.x, RESERVE_NOTE_Y)
		if cut < 0:
			continue
		# the second line of the SAME note: the tail line's own ink (the host's
		# engraved caption — the one dim step the tableau keeps)
		var dead: Label = host._mk_label(host._stage, full.substr(cut + RESERVE_DEAD.length()),
				&"Caption", tail.get_theme_color(&"font_color"))
		dead.size = dead.get_minimum_size()
		dead.position = Vector2(edge if left else sw - edge - dead.size.x,
				RESERVE_NOTE_Y + tail.size.y - 4.0)
		host._transients.append(dead)
		_reserve_dead.append(dead)
	# the file's hold-back rewrites a tail's own text; these carry their dead
	# on the second line instead
	_reserve_tails = []


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
	if _kind() == "assault":
		# BA-2: the stormers go to the foot of the wall; where it holds they
		# fall back to their mark, where it falls they stand in the breach.
		for who in _blocks:
			var stormer: Dictionary = _blocks[who]
			if bool((stormer["data"] as Dictionary).get("garrison", false)):
				continue
			stormer["storm_reach"] = _storm_reach(stormer)
			if str(host._data.get("fate", "held")) != "held":
				wants[who] = float(stormer["storm_reach"])
	if _laid == "wedge":
		_plan_rest_on_the_wedge(wants)
		return
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


func _plan_rest_on_the_wedge(wants: Dictionary) -> void:
	"""BA-2, the order of battle's rest. A beaten corps is driven back toward
	its own edge as far as the baize and its neighbours allow: the lead toward
	the wings behind him and never onto them; a wing, whose words already
	stand at the baize's edge, a few pixels (its plinth turned down says the
	rest). Only the lead goes forward, and never so far that a line of his
	crosses the centre or meets the crossed swords."""
	for side in [host._blocks_left, host._blocks_right]:
		for b in side:
			var want: float = float(wants.get(str((b["data"] as Dictionary).get("name", "")), 0.0))
			if str(b.get("role", "lead")) != "lead":
				want = minf(want, 0.0)
			var d := 0.0
			if want > 0.0:
				d = minf(want, _room_fwd(b))
			elif want < 0.0:
				d = -_clear_back(b, side, minf(-want, _room_back(b)))
			b["rest_dx"] = -_outward(b) * d


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
	_hold_the_day_back()
	for laurel in _laurels():
		(laurel as CanvasItem).modulate.a = 0.0
	for tail in _reserve_tails:
		var full: String = str(tail["full"])
		(tail["label"] as Label).text = full.substr(0, full.find(RESERVE_DEAD))
	# BA-2: what the reserve lost (a wedge's second line), a garrison's wall as
	# it ENDS and works as the battle left them are the result's too — hidden
	# or whole until their moment, never drawn at no alpha.
	for dead in _reserve_dead:
		if is_instance_valid(dead):
			(dead as Label).visible = false
	if _wall != null and is_instance_valid(_wall):
		_wall.stand_whole()
	for name in _works:
		(_works[name] as Rampart).stand_as_built()
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
	_the_ground_is_as_it_ended()
	_the_victors_standard_stands_forward()
	if _act_label != null:
		_act_label.visible = false
	if _dice != null:
		_dice.visible = true
		_dice.settle()
	_show_the_day()


func _the_victors_standard_stands_forward() -> void:
	"""BA2-X5. On a defeat the played tableau advances the victor's lead
	standard onto the player's half and leaves it there (the host's alarm
	register, `_schedule_standards`); the settled frame — a skip, a second
	viewing, Final frame only — never showed it (`_apply_final_frame_instant`,
	pinned). Where the acts end is where the settled frame stands: the same
	standard, the same distance, measured from where the host planted it (so a
	second call moves nothing)."""
	if str(host._data.get("register", "")) != "defeat" \
			or str(host._data.get("player_side", "")) == "":
		return
	for b in host._blocks_right:
		if bool((b["data"] as Dictionary).get("lead", false)) \
				and str(b["status"]) not in ["routed", "destroyed"]:
			var std = b["standard"]
			if std != null and is_instance_valid(std):
				(std as Node2D).position.x = -STANDARD_AT - ALARM_ADVANCE
			return


func _come_to_rest() -> void:
	"""The gavel: whatever the showing did not move (the brief form plays no
	'leave'; a lead that surged stands ahead of his place) comes to where the
	settled frame has it, and every beaten plinth is turned down."""
	if host == null or not is_instance_valid(host):
		return
	if _act_label != null and is_instance_valid(_act_label):
		_act_label.visible = false
	_tell_the_reserves_dead()
	_the_ground_is_as_it_ended()
	_clear_the_room()
	for name in _blocks:
		var b: Dictionary = _blocks[name]
		var node: Node2D = b["node"]
		if not is_instance_valid(node):
			continue
		_in_line(b)
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
	# BA-2: a bombardment is the cannonade alone — its count runs with the guns.
	var fight_acts: Array = ["cannonade"] if _kind() == "bombardment" else ["assault", "crisis"]
	for row in _played:
		var act: String = str(row["act"])
		var beat: Dictionary = row["beat"]
		var hold: float = float(row["hold"])
		row["at"] = t          # when this development begins (the walk's camera reads it)
		_at(t, _show_beat.bind(act, beat, bool(row["captioned"])))
		if act in fight_acts:
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
	host._seq.parallel().tween_callback(_type_the_verdict).set_delay(t + 0.55)
	host._seq.parallel().tween_callback(func(): host._enter_final(true)).set_delay(t + 0.70)

	# BA-2, the manoeuvre: every corps comes on in COLUMN and deploys into line
	# — those on the field as the table opens, those that march in as they
	# arrive. Set AFTER the count is scheduled: the host's recoil reads each
	# man's place when it is scheduled, and that place is his place in LINE.
	for b in host._blocks_left + host._blocks_right:
		if not _manoeuvres(b):
			continue
		_in_column(b)
		if not bool(b.get("arrives", false)):
			_deploy(b, 0.32, 0.34)


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
				_march_in(b, bool(beat.get("late", false)))
		"flank":
			_draw_flank(attacker_side)
		"battery":
			host._cue("cannon")
			_fire(b, str(beat.get("target", "")), attacker_side)
		"advance":
			if b != null:
				_advance(b, str(beat.get("temper", "steady")), attacker_side)
		# ── BA-2: the plan, the walls, the guns ──
		"plan":
			_tell_the_plan(beat)
		"walls":
			if _wall != null and is_instance_valid(_wall):
				_wall.pulse()
		"storm":
			if b != null:
				_storm(b)
		"wall_holds":
			_the_wall_answers(false)
		"wall_falls", "capitulates":
			_the_wall_answers(true)
			if b != null:
				_waver(b)
				host._cue("drum_sting")
		"repulsed", "occupy":
			if b != null:
				_slide(b, 0.8)
		"province":
			if b != null and _kind() == "assault":
				_slide(b, 0.8)
			elif b != null:
				_pulse(b["locket"])
		"bystander":
			if b != null:
				_struck(b)
		"shaken":
			if b != null:
				for f in b["figures"]:
					f.recoil(0.1)
		"destroyed":
			if b != null:
				_waver(b)
				host._cue("drum_sting")
		"works":
			_batter(str(beat.get("actor", "")))
			if b != null:
				_pulse(b["locket"])
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
				var horse: bool = str((b["data"] as Dictionary).get("arm", "")) == "cavalry"
				host._cue("cavalry" if horse else "bugle_charge")
				if horse:
					_sweep(b, 0.8)
				else:
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


func _march_in(b: Dictionary, late: bool = false) -> void:
	"""A corps comes onto the table from its own edge, in column, and deploys
	into line at its station; one that comes up at the last hour comes at the
	double. An enemy corps that came up unseen is turned up as it arrives."""
	var node: Node2D = b["node"]
	host._cue("march_step")
	var march: float = 0.55 if late else 0.9
	var tw: Tween = node.create_tween()
	tw.tween_property(node, "modulate:a", 1.0, 0.3)
	tw.parallel().tween_property(node, "position", b["home"], march) \
		.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	_reveal(b, tw)
	_deploy(b, march * 0.7, 0.3)


func _advance(b: Dictionary, temper: String, attacking: bool) -> void:
	"""Each temperament closes in its own way, and each arm in its own: horse
	comes on at the trot, charges home and recoils to re-form; guns unlimber
	forward of the line; foot goes in as its commander is. The defender's
	line answers in kind but does not leave its ground. On the order of
	battle the wings press with the lead, a short way, each in its own lane."""
	var node: Node2D = b["node"]
	var toward: float = -_outward(b)
	var home_x: float = (b["home"] as Vector2).x
	# BA-2: on a wedge no line of a lead's may cross the centre or meet the
	# crossed swords (the file's reaches were laid out for the file)
	var cap: float = _room_fwd(b) if _laid == "wedge" else 1000.0
	var arm: String = str((b["data"] as Dictionary).get("arm", "infantry"))
	var tw: Tween = node.create_tween()
	if attacking:
		host._cue("cavalry" if arm == "cavalry"
				else ("bugle_charge" if temper == "aggressive" else "musket_volley"))
	if attacking and arm == "cavalry":
		tw.tween_property(node, "position:x", home_x + toward * minf(8.0, cap), 0.22)
		tw.tween_property(node, "position:x", home_x + toward * minf(34.0, cap), 0.16) \
			.set_trans(Tween.TRANS_EXPO).set_ease(Tween.EASE_IN)
		tw.tween_property(node, "position:x", home_x + toward * minf(14.0, cap), 0.30) \
			.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	elif attacking and arm == "artillery":
		# unlimbered a little forward of the line, and no further
		tw.tween_property(node, "position:x", home_x + toward * minf(10.0, cap), 0.4) \
			.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	else:
		match temper:
			"aggressive":
				# ahead of the line, at once, and a little too far
				tw.tween_property(node, "position:x",
						home_x + toward * minf(28.0 if attacking else 12.0, cap), 0.34) \
					.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
			"cautious":
				# by measured steps: a step, a halt, a step
				var step: float = minf(7.0, cap / 2.0) if attacking else 0.0
				tw.tween_property(node, "position:x", home_x + toward * step, 0.30)
				tw.tween_interval(0.28)
				tw.tween_property(node, "position:x", home_x + toward * step * 2.0, 0.30)
			"literal":
				# to his mark, in one even movement, and no further
				tw.tween_property(node, "position:x",
						home_x + toward * minf(12.0 if attacking else 0.0, cap), 0.55) \
					.set_trans(Tween.TRANS_LINEAR)
			"sovereign":
				# the line dresses on him: he does not surge, his corps closes up
				tw.tween_property(node, "position:x",
						home_x + toward * minf(8.0 if attacking else 0.0, cap), 0.6) \
					.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN_OUT)
				_pulse(b["locket"])
			_:
				tw.tween_property(node, "position:x",
						home_x + toward * minf(12.0 if attacking else 0.0, cap), 0.45) \
					.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	if attacking and _laid == "wedge" and str(b.get("role", "")) == "lead":
		_the_wings_press(b)


func _the_wings_press(lead: Dictionary) -> void:
	"""The order of battle goes in together: each wing a short step forward in
	its own lane as the lead closes, and back to its station."""
	var side: Array = host._blocks_left if bool(lead["is_left"]) else host._blocks_right
	for wing in side:
		if wing == lead or bool(wing.get("arrives", false)) and \
				not is_equal_approx((wing["node"] as Node2D).modulate.a, 1.0):
			continue
		var node: Node2D = wing["node"]
		var home_x: float = (wing["home"] as Vector2).x
		var step: float = -_outward(wing) * 16.0
		var tw: Tween = node.create_tween()
		tw.tween_interval(0.12)
		tw.tween_property(node, "position:x", home_x + step, 0.32) \
			.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		tw.tween_interval(0.5)
		tw.tween_property(node, "position:x", home_x, 0.36) \
			.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN_OUT)


func _slide(b: Dictionary, seconds: float) -> void:
	"""To the corps' resting place (driven back, drawn off, in pursuit)."""
	var node: Node2D = b["node"]
	var tw: Tween = node.create_tween()
	tw.tween_property(node, "position", _rest_pos(b), seconds) \
		.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN_OUT)


func _sweep(b: Dictionary, seconds: float) -> void:
	"""Horse in pursuit: not straight at the beaten line but round its flank —
	a short curve off its lane and in again — to the same resting place a
	slide would take it to."""
	var node: Node2D = b["node"]
	var rest: Vector2 = _rest_pos(b)
	# toward the middle of the baize, whichever side of it the corps stands
	var off: float = -10.0 if rest.y > host._stage.size.y * 0.75 else 10.0
	var mid: Vector2 = (node.position + rest) / 2.0 + Vector2(0.0, off)
	var tw: Tween = node.create_tween()
	tw.tween_property(node, "position", mid, seconds * 0.5) \
		.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	tw.tween_property(node, "position", rest, seconds * 0.5) \
		.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)


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
		# (the muzzle follows the art's own scale: a wing's guns are smaller)
		var gun_art: Node2D = (gunner["node"] as Node2D).get_node_or_null("Art")
		var gs: float = gun_art.scale.x if gun_art != null else 1.0
		muzzle = (gunner["node"] as Node2D).position + Vector2(52.0 * dir, -34.0) * gs
	else:
		var side: Dictionary = host._side_payloads()[0 if from_left else 1]
		var gun := DioramaFigure.new()
		gun.setup("artillery", "r" if from_left else "l",
				Utils.NATION_COLORS.get(str(side.get("nation", "")), Utils.UI_NEUTRAL_FIGURE),
				host.SHELF_FIGURE_PX * 1.35)
		gun.position = Vector2(66.0 if from_left else sw - 66.0, sh * 0.80)
		if _laid == "wedge":
			# BA-2: the baize's bottom corner is the near wing's — the gun
			# stands in the pocket above and behind the lead
			gun.position = GUN_POCKET if from_left else Vector2(sw - GUN_POCKET.x, GUN_POCKET.y)
			gun.z_index = 30
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
	if _laid == "wedge":
		# BA-2: on the order of battle the march goes round the enemy lead's
		# outer end, through the notch his near wing does not cover, and up
		# onto his flank — read off where he stands, not off the file.
		var foe = null
		for lead in _leads():
			if bool(lead["is_left"]) != from_left:
				foe = lead
		if foe != null:
			var at: Vector2 = foe["home"]
			var round_x: float = at.x + dir * (DioramaPlinth.HALF_W + 13.0)
			pts = PackedVector2Array([
				Vector2(mid - dir * 230.0, foot),
				Vector2(mid - dir * 20.0, foot),
				Vector2(round_x - dir * 14.0, foot),
				Vector2(round_x, foot - 14.0),
				Vector2(round_x, at.y - 40.0),
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

	# BA-2: the flank is a MARCH — a column in the attacker's colours goes
	# along the line as it is drawn and stands on the enemy's flank while the
	# development is told. It is a development, not a corps: it fades with it.
	var side: Dictionary = host._side_payloads()[0 if from_left else 1]
	var column := DioramaFigure.new()
	column.setup("infantry", "r" if from_left else "l",
			Utils.NATION_COLORS.get(str(side.get("nation", "")), Utils.UI_NEUTRAL_FIGURE),
			host.SHELF_FIGURE_PX)
	column.position = pts[0]
	column.z_index = 30
	column.modulate.a = 0.0
	host._stage.add_child(column)
	host._transients.append(column)
	var march: Tween = column.create_tween()
	march.tween_property(column, "modulate:a", 1.0, 0.12)
	for i in range(1, pts.size()):
		march.tween_property(column, "position", pts[i], 0.16)
	march.tween_interval(1.6)
	march.tween_property(column, "modulate:a", 0.0, 0.5)


# =============================================================================
# BA-2: the manoeuvre — column and line, the plan, the square, the works, the wall
# =============================================================================
# Every verb here is keyed on something the payload already carries (a corps'
# arm, a beat's flags, the wall's fate) and adds neither a beat nor a second to
# a showing. What is laid from the battle's RESULT — the wall as it ended, the
# works as the battle left them — is held back until its moment (BA1-X6).

func _manoeuvres(b: Dictionary) -> bool:
	"""A corps that comes on in column: not a garrison (it stands behind its
	wall) and not a corps in square (it is already formed)."""
	return not bool((b["data"] as Dictionary).get("garrison", false)) \
			and not bool(b.get("in_square", false))


func _in_column(b: Dictionary) -> void:
	"""Its files closed up on the centre: a column of march."""
	for f in b["figures"]:
		var fig: Node2D = f
		if not fig.has_meta(&"ba_line_x"):
			fig.set_meta(&"ba_line_x", fig.position.x)
		fig.position.x = float(fig.get_meta(&"ba_line_x")) * COLUMN_SQUEEZE


func _close_up(b: Dictionary, delay: float, seconds: float) -> void:
	"""Line into column, in time: the files close on the centre."""
	for f in b["figures"]:
		var fig: Node2D = f
		if not fig.has_meta(&"ba_line_x"):
			fig.set_meta(&"ba_line_x", fig.position.x)
		var tw: Tween = fig.create_tween()
		tw.tween_interval(delay)
		tw.tween_property(fig, "position:x",
				float(fig.get_meta(&"ba_line_x")) * COLUMN_SQUEEZE, seconds) \
			.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN_OUT)


func _deploy(b: Dictionary, delay: float, seconds: float) -> void:
	"""…and into line: the files open out to their places."""
	for f in b["figures"]:
		var fig: Node2D = f
		if not fig.has_meta(&"ba_line_x"):
			continue
		var tw: Tween = fig.create_tween()
		tw.tween_interval(delay)
		tw.tween_property(fig, "position:x", float(fig.get_meta(&"ba_line_x")), seconds) \
			.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)


func _in_line(b: Dictionary) -> void:
	"""At once: every man on his place in the line (the gavel, for whatever
	the showing did not bring there)."""
	for f in b["figures"]:
		var fig: Node2D = f
		if is_instance_valid(fig) and fig.has_meta(&"ba_line_x"):
			fig.position.x = float(fig.get_meta(&"ba_line_x"))
			fig.remove_meta(&"ba_line_x")


func _tell_the_plan(beat: Dictionary) -> void:
	"""The plan is shown on the board: the lead answers, then each corps
	ordered in support and each battery it names, in turn."""
	var names: Array = [str(beat.get("actor", ""))]
	for key in ["supports", "guns"]:
		var listed = beat.get(key, [])
		if listed is Array:
			for n in listed:
				names.append(str(n))
	var k := 0
	for n in names:
		var b = _blocks.get(n, null)
		if b == null:
			continue
		var tw: Tween = (b["node"] as Node2D).create_tween()
		tw.tween_interval(0.22 * k)
		tw.tween_callback(_pulse.bind(b["locket"]))
		k += 1


func _storm_reach(b: Dictionary) -> float:
	"""How far a storming corps goes: to the foot of the wall, and never so
	far that a line of his meets one of the garrison's. The same whether the
	wall will hold or fall — the storm tells nothing of its end."""
	if _wall == null or not is_instance_valid(_wall):
		return 0.0
	var toward: float = -_outward(b)
	var home_x: float = (b["home"] as Vector2).x
	var reach: float = (_wall.position.x - toward * (_wall.reach() + 2.0)
			- (home_x + toward * DioramaPlinth.HALF_W)) * toward
	var theirs: Array = []
	for who in _blocks:
		if bool((_blocks[who]["data"] as Dictionary).get("garrison", false)):
			theirs += _words(_blocks[who])
	for r in _words(b):
		var mine: Rect2 = r
		for o in theirs:
			var other: Rect2 = o
			if mine.position.y < other.end.y and mine.end.y > other.position.y:
				var room: float = (other.position.x - mine.end.x) if toward > 0.0 \
						else (mine.position.x - other.end.x)
				reach = minf(reach, room - 6.0)
	return clampf(reach, 0.0, 96.0)


func _storm(b: Dictionary) -> void:
	"""The stormers close up into columns and go in to the foot of the wall,
	the ladders raised."""
	var node: Node2D = b["node"]
	var toward: float = -_outward(b)
	var home_x: float = (b["home"] as Vector2).x
	host._cue("bugle_charge")
	# closed up at once, a victor's stormers stood in line again a quarter
	# second later (the host's recoil): they close up as they come
	_close_up(b, AFTER_THE_RECOIL, 0.25)
	if _wall != null and is_instance_valid(_wall):
		_wall.raise_ladders()
	var tw: Tween = node.create_tween()
	tw.tween_property(node, "position:x", home_x + toward * float(b.get("storm_reach", 0.0)), 0.55) \
		.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)


func _the_wall_answers(fell: bool) -> void:
	"""What the wall did, at its moment: it stands and the stormers fall back
	from it, or it is carried (or yields) and they stand in the breach."""
	if _wall != null and is_instance_valid(_wall):
		_wall.show_the_end()
	for who in _blocks:
		var b: Dictionary = _blocks[who]
		if bool((b["data"] as Dictionary).get("garrison", false)):
			continue
		_deploy(b, 0.0, 0.3)
		if not fell:
			host._cue("bugle_retreat")
			_slide(b, 0.9)


func _struck(b: Dictionary) -> void:
	"""A corps standing by is caught in the fire."""
	var node: Node2D = b["node"]
	for i in range(2):
		var hit := Burst.new()
		hit.position = node.position + Vector2(-14.0 + 28.0 * i, -30.0 - 6.0 * i)
		hit.dir = 0.0
		host._stage.add_child(hit)
		host._transients.append(hit)
		hit.go(0.1 + 0.2 * i)
	for f in b["figures"]:
		f.recoil(0.25)


func _build_the_wall() -> void:
	"""A garrison's curtain wall, between its block and the line. It opens
	WHOLE: what the assault did to it is the result's, and comes with the
	crisis (`_the_wall_answers`) or with the settled frame."""
	for who in _blocks:
		var keeper: Dictionary = _blocks[who]
		if not bool((keeper["data"] as Dictionary).get("garrison", false)):
			continue
		var node: Node2D = keeper["node"]
		var toward: float = -_outward(keeper)
		_wall = SiegeWall.new()
		_wall.facing = toward
		_wall.fortified = bool(host._data.get("fortified", false))
		_wall.fate = str(host._data.get("fate", "held"))
		for other in _blocks:
			var stormer: Dictionary = (_blocks[other] as Dictionary)["data"]
			if not bool(stormer.get("garrison", false)) and bool(stormer.get("lead", false)):
				_wall.victor = Utils.NATION_COLORS.get(
						str(stormer.get("origin_nation", stormer.get("nation", ""))),
						Utils.UI_NEUTRAL_FIGURE)
		_wall.position = Vector2(
				node.position.x + toward * (DioramaPlinth.HALF_W + SiegeWall.HALF_W
						+ SiegeWall.BATTER - 1.0),
				node.position.y + 24.0)
		_wall.z_index = 19
		host._stage.add_child(_wall)
		host._transients.append(_wall)
		return


func _build_the_works() -> void:
	"""Field works stand as a drawn rampart in front of the corps that threw
	them up, at the strength the battle met them with, and come down by what
	the battle's own report says. Read off the beats alone: a watcher is told
	of no works (they are the side's own), so none is drawn for him."""
	var marks: Dictionary = {}          # corps -> [as built %, as it ended %]
	for item in _all_beats():
		var beat: Dictionary = item["beat"]
		var who: String = str(beat.get("actor", ""))
		match str(beat.get("kind", "")):
			"ground", "plan":
				var pct: int = int(beat.get("works_pct", 0))
				if pct > 0 and not marks.has(who):
					marks[who] = [pct, pct]
			"works":
				marks[who] = [int(beat.get("old", 0)), int(beat.get("new", 0))]
	for who in marks:
		var b = _blocks.get(who, null)
		if b == null:
			continue
		var node: Node2D = b["node"]
		var art: Node2D = node.get_node_or_null("Art")
		var s: float = art.scale.x if art != null else 1.0
		var bank := Rampart.new()
		bank.facing = -_outward(b)
		bank.built = int(marks[who][0])
		bank.ended = int(marks[who][1])
		bank.position = node.position + Vector2(
				bank.facing * (DioramaPlinth.HALF_W * s + Rampart.BACK + 2.0), 24.0 * s)
		bank.z_index = 19
		host._stage.add_child(bank)
		host._transients.append(bank)
		bank.stand_as_built()
		_works[who] = bank


func _batter(who: String) -> void:
	"""The works come down, at the moment the battle's report tells it."""
	var bank = _works.get(who, null)
	if bank != null and is_instance_valid(bank):
		(bank as Rampart).come_down()


func _the_ground_is_as_it_ended() -> void:
	"""At once: the wall as the assault left it, the works as the battle did."""
	if _wall != null and is_instance_valid(_wall):
		_wall.show_the_end()
	for who in _works:
		if is_instance_valid(_works[who]):
			(_works[who] as Rampart).stand_as_ended()


func _mark_the_squares() -> void:
	"""A corps the battle met in square stands in square: its rear rank faces
	about and the square is marked on its slab. A disposition, not a result —
	it stands from the first frame; and only where the script tells it (the
	enemy's in a battle the player fought, never a watched one's)."""
	var who: Dictionary = {}
	for item in _all_beats():
		var beat: Dictionary = item["beat"]
		match str(beat.get("kind", "")):
			"ground", "plan":
				if bool(beat.get("square", false)):
					who[str(beat.get("actor", ""))] = true
			"square":
				# the row is the horse's own: the squares are the corps it rode at
				var rider_left: bool = (str(beat.get("side", "")) == "attacker") == _attacker_left()
				for lead in _leads():
					if bool(lead["is_left"]) != rider_left:
						who[str((lead["data"] as Dictionary).get("name", ""))] = true
	for n in who:
		var b = _blocks.get(n, null)
		if b == null:
			continue
		var art: Node2D = (b["node"] as Node2D).get_node_or_null("Art")
		if art == null:
			continue
		b["in_square"] = true
		_form_square(b, art)
		var mark := SquareMark.new()
		art.add_child(mark)
		art.move_child(mark, 1)          # over the slab, under the men
		_squares.append(mark)


func _form_square(b: Dictionary, art: Node2D) -> void:
	"""The stands of a corps in square as a wargamer lays them: a face to the
	enemy and a face to the rear, the far and the near face, the colours
	inside. Each stand keeps the place in the host's drawing order it was built
	with (far to near), so nothing is re-parented and the host's own tumbles
	still find their men."""
	var toward: float = -_outward(b)
	# far face · rear face · front face · the colours · near face
	var slots: Array = [Vector2(0.0, -24.0), Vector2(-toward * 36.0, -11.0),
			Vector2(toward * 36.0, -11.0), Vector2(0.0, -9.0), Vector2(0.0, 3.0)]
	var k := 0
	for child in art.get_children():
		if not (child is DioramaFigure) or not (b["figures"] as Array).has(child):
			continue
		var stand: Node2D = child
		stand.position = slots[mini(k, slots.size() - 1)]
		# the rear face looks the other way
		stand.scale.x = -absf(stand.scale.x) if k == 1 else absf(stand.scale.x)
		k += 1


class SiegeWall:
	extends Node2D
	# A garrison's wall: a battlemented curtain between the garrison and the
	# line, its foot at the origin, `facing` the unit x toward the stormers.
	# Stone, courses, parapet and merlons are DRAWN (no new art). It stands
	# whole until the assault's end is told; then it is scarred (held), broken
	# down under the stormers' colour (stormed) or flies a white flag
	# (capitulated).

	const HALF_W := 20.0
	const HEIGHT := 104.0       # its foot to the walkway
	const MERLON := 12.0        # the battlements above the walkway
	const BATTER := 4.0         # how far its foot spreads
	const OUTWORK := 18.0       # a fortress's outer work, on the stormers' side
	# A carried wall's broken edge: (toward the stormers from its centre, below
	# the walkway), from the crest down to the stormers' face.
	const BREACH := [Vector2(-3.0, 0.0), Vector2(3.0, 30.0), Vector2(9.0, 38.0),
			Vector2(14.0, 60.0), Vector2(20.0, 66.0)]

	var facing := -1.0
	var fortified := false
	var fate := "held"
	var victor := Color.WHITE   # the stormers' colour, flown on a wall they carried
	var _state := "whole"       # whole | held | stormed | capitulated
	var _ladders := 0.0         # 0 … 1: how far up the wall the ladders stand

	func state() -> String:
		return _state

	func stone() -> Rect2:
		"""The curtain itself, in its own space: what no corps may stand in."""
		return Rect2(-HALF_W, -HEIGHT - MERLON, HALF_W * 2.0, HEIGHT + MERLON)

	func reach() -> float:
		"""How far its stone stands toward the stormers, from its centre."""
		return HALF_W + (OUTWORK if fortified else BATTER)

	func stand_whole() -> void:
		_state = "whole"
		_ladders = 0.0
		queue_redraw()

	func show_the_end() -> void:
		if _state == fate:
			return
		_state = fate
		if fate != "stormed":
			_ladders = 0.0      # they fell back from it, or it opened its gates
		queue_redraw()

	func raise_ladders() -> void:
		var tw: Tween = create_tween()
		tw.tween_method(_set_ladders, 0.0, 1.0, 0.45)

	func _set_ladders(v: float) -> void:
		if _state == "whole":
			_ladders = v
			queue_redraw()

	func pulse() -> void:
		var tw: Tween = create_tween()
		tw.tween_property(self, "modulate", Color(1.25, 1.22, 1.15, 1.0), 0.16)
		tw.tween_property(self, "modulate", Color.WHITE, 0.26)

	func _broken_at(below: float) -> float:
		"""Where a carried wall's broken edge stands `below` px under the
		walkway (toward the stormers, from its centre); under the breach, the
		whole width."""
		for i in range(1, BREACH.size()):
			var a: Vector2 = BREACH[i - 1]
			var b: Vector2 = BREACH[i]
			if below <= b.y:
				return lerpf(a.x, b.x, clampf((below - a.y) / maxf(b.y - a.y, 0.001), 0.0, 1.0))
		return HALF_W

	func _draw() -> void:
		var f: float = facing
		var top: float = -HEIGHT
		var stone_c: Color = Utils.UI_WALL_STONE
		var shade: Color = Utils.UI_WALL_SHADE
		var scar: Color = Utils.UI_WALL_SCAR
		var carried: bool = _state == "stormed"
		if fortified:
			# a fortress: a low sloped outwork at the curtain's foot
			draw_colored_polygon(PackedVector2Array([
				Vector2(f * HALF_W, 0.0), Vector2(f * (HALF_W + OUTWORK), 0.0),
				Vector2(f * (HALF_W + OUTWORK - 7.0), -36.0), Vector2(f * HALF_W, -36.0)]), shade)
			draw_line(Vector2(f * (HALF_W + OUTWORK - 7.0), -36.0), Vector2(f * HALF_W, -36.0),
					stone_c, 2.0)
		# the curtain, battered at its foot; a carried wall is broken down from
		# its crest on the stormers' side
		var body := PackedVector2Array([
			Vector2(-f * (HALF_W + BATTER), 0.0), Vector2(-f * HALF_W, -26.0),
			Vector2(-f * HALF_W, top)])
		if carried:
			for p in BREACH:
				body.append(Vector2(f * (p as Vector2).x, top + (p as Vector2).y))
		else:
			body.append(Vector2(f * HALF_W, top))
		body.append(Vector2(f * HALF_W, -26.0))
		body.append(Vector2(f * (HALF_W + BATTER), 0.0))
		draw_colored_polygon(body, stone_c)
		# the parapet and its merlons — on a carried wall, what is left of them
		var from: float = -HALF_W - 3.0
		var to: float = HALF_W + 3.0
		if carried:
			if f > 0.0:
				to = -3.0
			else:
				from = 3.0
		draw_rect(Rect2(from, top - 4.0, to - from, 6.0), stone_c)
		var merlons: int = 2 if carried else 4
		var gap: float = (to - from - 8.0 * merlons) / float(merlons - 1)
		for i in range(merlons):
			draw_rect(Rect2(from + (8.0 + gap) * i, top - MERLON, 8.0, MERLON - 4.0), stone_c)
		# the far face in shade
		var far: float = -f * HALF_W
		draw_rect(Rect2(minf(far, far * 0.4), top, HALF_W * 0.6, HEIGHT), Color(shade, 0.5))
		# the courses and their joints (only where the stone still stands)
		var line_c := Color(shade, 0.7)
		var row := 0
		var y: float = -16.0
		while y > top + 6.0:
			var edge: float = _broken_at(y - top) if carried else HALF_W
			draw_line(Vector2(-f * HALF_W, y), Vector2(f * edge, y), line_c, 1.0)
			var above: float = maxf(y - 16.0, top)
			var over: float = _broken_at(above - top) if carried else HALF_W
			var jx: float = -HALF_W + 7.0 + (7.0 if row % 2 == 1 else 0.0)
			while jx < HALF_W - 2.0:
				if jx * f < over - 1.0:
					draw_line(Vector2(jx, y), Vector2(jx, above), Color(shade, 0.4), 1.0)
				jx += 14.0
			row += 1
			y -= 16.0
		# a loophole in its outer half
		draw_rect(Rect2(f * 6.0 - 1.5, top + 72.0, 3.0, 13.0), scar)
		if _state == "held":
			# it stood: shot marks on its outer face
			for at in [Vector2(f * 9.0, top + 26.0), Vector2(f * 4.0, top + 44.0),
					Vector2(f * 13.0, top + 56.0)]:
				draw_circle(at, 3.0, scar)
		elif carried:
			# the rubble of the breach, and the stormers' colour on the crest
			for i in range(5):
				draw_circle(Vector2(f * (HALF_W - 2.0 + 6.0 * i), -3.0 - float((7 - i) % 3)),
						3.5 + float(i % 2), shade if i % 2 == 0 else scar)
			var staff := Vector2(-f * 13.0, top - MERLON)
			draw_line(staff, staff + Vector2(0.0, -22.0), scar, 2.0)
			draw_rect(Rect2(minf(staff.x, staff.x - f * 18.0), staff.y - 22.0, 18.0, 11.0), victor)
		elif _state == "capitulated":
			var staff_top := Vector2(0.0, top - MERLON - 30.0)
			draw_line(Vector2(0.0, top - 4.0), staff_top, scar, 2.0)
			draw_rect(Rect2(minf(0.0, f * 22.0), staff_top.y, 22.0, 14.0), Utils.UI_WHITE_FLAG)
		if _ladders > 0.0:
			for i in range(2):
				var foot := Vector2(f * (reach() + 12.0 + 13.0 * i), 0.0)
				var head_y: float = top * (0.66 + 0.3 * i) * _ladders
				if carried:
					head_y = maxf(head_y, top + 62.0 + 4.0 * i)   # onto the lip of the breach
				var head := Vector2(f * HALF_W, head_y)
				for rail in [0.0, 5.0]:
					draw_line(foot + Vector2(f * rail, 0.0), head + Vector2(f * rail, 0.0),
							Utils.UI_WORKS_CREST, 2.0)
				for k in range(1, 6):
					var rung: Vector2 = foot.lerp(head, float(k) / 6.0)
					draw_line(rung, rung + Vector2(f * 5.0, 0.0), Utils.UI_WORKS_CREST, 1.0)


class Rampart:
	extends Node2D
	# Field works: a bank of thrown-up earth with a firing step behind it and
	# sharpened stakes out of its face, in front of the corps that made them —
	# its foot at the origin, `facing` the unit x toward the enemy. Its height
	# is the works' strength in percent, as the battle's report gives it.

	const PX_PER_PCT := 3.0
	const MAX_H := 58.0
	const MIN_H := 4.0          # under this the works are levelled
	const BACK := 18.0          # its foot behind the crest …
	const FRONT := 18.0         # … and before it

	var facing := 1.0
	var built := 0              # as the battle met them
	var ended := 0              # as it left them
	var _pct := 0.0

	func shown_pct() -> int:
		return int(round(_pct))

	func stand_as_built() -> void:
		_pct = float(built)
		queue_redraw()

	func stand_as_ended() -> void:
		_pct = float(ended)
		queue_redraw()

	func come_down() -> void:
		var tw: Tween = create_tween()
		tw.tween_method(_set_pct, _pct, float(ended), 0.6) \
			.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)

	func _set_pct(v: float) -> void:
		_pct = v
		queue_redraw()

	func _draw() -> void:
		var f: float = facing
		var h: float = clampf(_pct * PX_PER_PCT, 0.0, MAX_H)
		if h < MIN_H:
			# levelled: the earth thrown down, a stake left in it
			for i in range(5):
				draw_circle(Vector2(f * (-12.0 + 7.0 * i), -2.0 - float(i % 2)),
						3.0 + float(i % 2), Utils.UI_WORKS_EARTH)
			draw_line(Vector2(f * 6.0, -3.0), Vector2(f * 15.0, -8.0), Utils.UI_WORKS_CREST, 1.5)
			return
		# the bank: a firing step behind, steep toward the enemy
		var step := Vector2(-f * 8.0, -h * 0.55)
		var crest := Vector2(-f * 2.0, -h)
		var lip := Vector2(f * 5.0, -h + 3.0)
		var toe := Vector2(f * FRONT, 0.0)
		draw_colored_polygon(PackedVector2Array([
			Vector2(-f * BACK, 0.0), Vector2(-f * 13.0, -h * 0.55), step, crest, lip, toe]),
			Utils.UI_WORKS_EARTH)
		draw_polyline(PackedVector2Array([step, crest, lip]), Utils.UI_WORKS_CREST, 2.0)
		# the fraises: sharpened stakes out of its outer slope
		if h > 12.0:
			var stakes: int = 3 if h < 30.0 else 4
			for i in range(stakes):
				var at: Vector2 = lip.lerp(toe, 0.2 + 0.6 * float(i) / float(stakes - 1))
				draw_line(at, at + Vector2(f * 9.0, -7.0), Utils.UI_WORKS_CREST, 1.5)


class SquareMark:
	extends Node2D
	# The ground mark of a corps formed in square, on its slab (the art's own
	# units: the slab's top face runs y −30 … 12): its four faces, and the
	# bayonets it shows at its two corners.

	func _draw() -> void:
		var c: Color = Utils.UI_SQUARE_MARK
		var left := Vector2(-66.0, -9.0)
		var right := Vector2(66.0, -9.0)
		draw_polyline(PackedVector2Array([
			left, Vector2(0.0, -27.0), right, Vector2(0.0, 9.0), left]), c, 2.0, true)
		for k in [-1.0, 0.0, 1.0]:
			draw_line(left, left + Vector2(-1.0, 0.5 * k).normalized() * 9.0, c, 1.5)
			draw_line(right, right + Vector2(1.0, 0.5 * k).normalized() * 9.0, c, 1.5)


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
