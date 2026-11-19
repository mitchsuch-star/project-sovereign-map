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
var _reserve_short_at_end: Array = []  # BA6-X10: [{label, short, left, edge}] a note a triumph's laurel will crowd
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
	# BA-6 (lever 1): a table with a day's panel asks the tray for DAY_ROOM at its foot, and every
	# table without one has the tray as it was built — before the speed switch (and the plate) stand on it
	host.set_day_room(DAY_ROOM if _day_has_panel() else 0.0)
	_build_the_speed()     # BA-5: every table that plays — a fleet action's and an old payload's too
	if host._is_naval():
		return
	_build_the_ground()    # BA-5: the province's terrain, on the felt under the men
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
	_the_tolls_keep_the_baize()
	_keep_the_end()
	_dress_the_kind()
	_build_the_day()       # BA-3: hidden; shown at rest, never while the acts play
	_lift_the_verdict()    # BA5-D3: after the day's panel has read the verdict's own top
	_fit_the_line_under_the_headline()    # ...and after every word of that line is written

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
		_dice.build(host, roll, _luck_line(roll), _luck_short(roll))
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
	out.append(Rect2(host._stage.size.x / 2.0 - 110.0, 74.0, 220.0, DiceTray.room_h(host)))
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
	# BA-5: what told in the battle, under its headline — after the host's own
	# line where the province changed hands ("Swabia falls to France. Our numbers told.")
	var told: String = str(host._data.get("verdict_told", ""))
	_sub_host = host._sub_banner.text          # (the review) the line's two parts, for its fit
	_sub_told = ""
	if told != "" and told != "<null>":
		_sub_told = told
		host._sub_banner.text = told if host._sub_banner.text == "" else host._sub_banner.text + " " + told
	# Row PW (plain words): every cause of the battle with its numbers, as the
	# line's hover — the line itself carries the first ("Why: he had more men —
	# 25,000 against your 12,000."), the payload's `why` the rest.
	var why = host._data.get("why", [])
	if why is Array and (why as Array).size() > 1:
		var causes := PackedStringArray()
		for cause in why:
			causes.append(str(cause))
		_hint_the_line("Why: " + "; ".join(causes) + ".")
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
	# (the second reading: "24,000 → 21,994" above and "→ 21,687" below read as two
	# figures for one corps) what the march cost stands under it, on a line of its own
	var kept: int = strength.text.substr(strength.text.rfind(" → ") + 3).to_int()
	var marched: int = toll.to_int()
	var plain: String = toll
	if kept > marched and marched > 0:
		toll += "\n(%s lost on the march)" % Utils.format_number(kept - marched)
		b["march_cost"] = kept - marched
	var caption: Label = host._mk_label(node, toll, &"Caption", Color(host.BONE_HEX))
	var need: Vector2 = caption.get_minimum_size()
	var art_now: Node2D = node.get_node_or_null("Art")
	var under: float = maxf(host.FAITH_CAPTION_Y * (art_now.scale.x if art_now != null else 1.0), floor_y + 1.0)
	if toll != plain and node.position.y + under + need.y > host._stage.size.y:
		# a lead at the baize's foot has no room under him for the second line: one line
		# (the review: the toll alone left two figures for one corps unexplained there)
		caption.text = _toll_on_one_line(b, plain, node.position.x, left,
				DioramaPlinth.HALF_W * (art_now.scale.x if art_now != null else 1.0))
		need = caption.get_minimum_size()
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


func _the_tolls_keep_the_baize() -> void:
	"""The march's cost stands on a second line under the advance's toll — where the
	lead's FINAL station leaves it the room. The toll is written while the order of
	battle is laid, and the wedge may be taken back to the file after that (it is, from
	Text size 120 % up: the lead then stands at the baize's foot, and the second line
	ran off it — the walk at that size caught it). A toll with no room for its second
	line keeps its first, the words every surface has always had."""
	for name in _blocks:
		var b: Dictionary = _blocks[name]
		var toll: Label = b.get("toll", null)
		if toll == null or not is_instance_valid(toll):
			continue
		var station_y: float = maxf((b["node"] as Node2D).position.y, _rest_pos(b).y)
		if station_y + toll.position.y + toll.size.y <= host._stage.size.y:
			continue
		if not toll.text.contains("\n"):
			# BA1-X4: a single line may still hang under the baize (Text size 175 %):
			# it is lifted to stand inside the stage
			toll.position.y -= station_y + toll.position.y + toll.size.y - host._stage.size.y
			continue
		var was_w: float = toll.size.x
		var left: bool = bool(b["is_left"])
		var slab_end: float = toll.position.x if left else toll.position.x + was_w
		toll.text = _toll_on_one_line(b, toll.text.get_slice("\n", 0), _rest_pos(b).x,
				left, absf(slab_end))
		toll.size = toll.get_minimum_size()
		if not left:
			toll.position.x += was_w - toll.size.x      # a right-hand toll ends at its slab's outer end


func _toll_on_one_line(b: Dictionary, first: String, node_x: float, left: bool, slab: float) -> String:
	"""(The review) The toll and what the march cost on ONE line — "→ 21,687 after
	the advance (−307)" — where the second line has no room; the toll alone only
	where even that line would leave the baize sideways. A left toll runs inboard
	from its slab's outer end, a right one ends there."""
	var cost: int = int(b.get("march_cost", 0))
	if cost <= 0:
		return first
	var one: String = first + " (−%s)" % Utils.format_number(cost)
	var probe: Label = host._mk_label(host._stage, one, &"Caption", Color(host.BONE_HEX))
	var w: float = probe.get_minimum_size().x
	probe.queue_free()
	var x0: float = (node_x - slab) if left else (node_x + slab - w)
	if x0 < host.BAIZE_PAD or x0 + w > host._stage.size.x - host.BAIZE_PAD:
		return first
	return one


func _fit_the_line_under_the_headline() -> void:
	"""The line under the headline is centred on the stage, and on an order of battle the
	reserve's dead stand beside each counter at its height. A line that would reach them
	is set in the theme's Caption size (the second reading's longer lines did at Text size
	130 %: "The day so far: … — the better of the toll is ours." over "1,211 lost"). The
	next table laid has the line's own size back (`_put_the_chrome_back`).
	(The review) The line must fit the baize itself too: a province's own line
	followed by what told ran wider than the stage at Text size 130 % even in the
	Caption size. Then what told is said short (the moment a line broke rides the
	line's hover), and where even that is too wide the line keeps the host's own
	words and what told rides its hover whole."""
	var sub: Label = host._sub_banner
	if sub == null or sub.text == "":
		return
	var mid: float = host._stage.size.x / 2.0
	var half: float = mid - host.BAIZE_PAD
	var line_h: float = sub.get_minimum_size().y
	for dead in _reserve_dead:
		if not is_instance_valid(dead):
			continue
		var l: Label = dead
		if l.position.y >= sub.position.y + line_h or l.position.y + l.size.y <= sub.position.y:
			continue          # not at the line's height
		half = minf(half, (mid - (l.position.x + l.size.x)) if l.position.x < mid else (l.position.x - mid))
	if _sub_fits(sub, half):
		return
	sub.theme_type_variation = &"Caption"
	if _sub_fits(sub, half):
		return
	if _sub_told != "":
		var short := _told_short(_sub_told)
		if short != "":
			sub.text = (_sub_host + " " + short) if _sub_host != "" else short
			if _sub_fits(sub, half) or _sub_host == "":
				_hint_the_line(_sub_told)
				return
		if _sub_host == "":
			return
		sub.text = _sub_host
		_hint_the_line(_sub_told)
		if _sub_fits(sub, half):
			return
	# (the walk of record, at the shipped Text size) a province's own line can be too wide beside
	# the reserve's dead even alone, what told or none: the clause before its dash stands ("Naples,
	# the Kingdom of the Two Sicilies' capital, retaken."), the whole line on its hover
	var dash := _sub_host.find(" — ")
	if dash > 0:
		sub.text = _sub_host.substr(0, dash) + "."
		_hint_the_line((_sub_host + " " + _sub_told).strip_edges())


func _sub_fits(sub: Label, half: float) -> bool:
	return sub.get_minimum_size().x / 2.0 + SUB_CLEAR <= half


static func _told_short(told: String) -> String:
	"""What told without its moment: "Decided when Mack's line broke: our weight
	of numbers told." -> "Our weight of numbers told." ("" for a line that names
	no moment, or one that names no cause after it)."""
	var cut := told.find(": ")
	if not told.begins_with("Decided") or cut < 0:
		return ""
	var rest := told.substr(cut + 2)
	return rest.substr(0, 1).to_upper() + rest.substr(1)


func _hint_the_line(text: String) -> void:
	"""The whole of what told, as the line's hover (a Label takes a hover only
	where it takes the mouse: PASS, so a click still reaches the table)."""
	host._sub_banner.tooltip_text = text
	host._sub_banner.mouse_filter = Control.MOUSE_FILTER_PASS


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
	# BA-5: ...the line under the headline its own size (`_fit_the_line_under_the_headline`)
	host._sub_banner.theme_type_variation = &""
	host._verdict.theme_type_variation = VERDICT_STEP          # ...and the verdict its own step (`_fit_the_verdict`)
	host._sub_banner.tooltip_text = ""                     # (the review) ...and no hover of its last fit
	host._sub_banner.mouse_filter = Control.MOUSE_FILTER_IGNORE
	# BA-5: ...and Close its primary look (a day that offered its words made it plain)
	host._btn_close.theme_type_variation = &"PrimaryButton"
	for face in [&"normal", &"hover"]:
		host._btn_close.remove_theme_stylebox_override(face)
	for ink in [&"font_color", &"font_hover_color"]:
		host._btn_close.remove_theme_color_override(ink)
	host._btn_close.reset_size()
	host._btn_close.position = Vector2(host.TRAY_W - 154.0, host.tray_h() - 46.0)
	host._btn_replay.position = Vector2(host.TRAY_W - 274.0, host.tray_h() - 46.0)
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
# BA-5 / BA-6: the ground on the table (the user's tick — "The ground on the table")
# ─────────────────────────────────────────────────────────────────────────────
# The province's ground is a SHEET OF A PERIOD SURVEY laid on the felt under the
# men — row BA, BA-6, by the user's "make sure the terrain background does not
# look ai genned even get assets if needed" (BA-5 had drawn it in code, and it
# read as generated). Ferraris's hand-coloured survey of the Austrian
# Netherlands (1771-78) gives the fields, woods, hills, towns and rivers; Anich's
# engraved Atlas Tyrolensis (1774) the mountains: real scans, cut and graded by
# lamplight into the felt's own dark range so every caption over them keeps its
# contrast (tools/ba6_terrain_plates.py; assets/textures/battle/; the sources in
# THIRD_PARTY_LICENSES.md). Open country, hills, mountains and a river span the
# table; a wood or a town is the defender's ground (its bonus is his), so its
# plate is the one whose feature lies on his half. A plate is never mirrored —
# a survey's lettering would read backwards. A province picks its plate among
# its kind's by its own name, so a field looks the same each time it is fought
# on. A payload without `ground` (an old save's, a fleet action's) is a bare
# felt, as before.

var _ground: Ground = null


func _build_the_ground() -> void:
	_ground = null
	var kind := str(host._data.get("ground", ""))
	if not Ground.KINDS.has(kind):
		return
	var g := Ground.new()
	g.name = "Ground"
	g.kind = kind
	g.dir = 1.0 if _attacker_left() else -1.0
	g.felt = host._stage.size
	g.seed_text = str(host._data.get("region", ""))
	host._stage.add_child(g)
	host._stage.move_child(g, 1)          # over the felt; under the lamp, the men and every label
	host._transients.append(g)
	_ground = g


class Ground:
	extends Node2D
	# `kind` is the payload's `ground` (the backend's terrain key); `dir` is +1
	# when the defender holds the right half of the table and -1 the left. The
	# plate is the province's own among its kind's (seeded by its name). The
	# sheet lies inside the felt's border band and below the loss counters'
	# line, its shadow cast left and down from the lamp (upper right).
	const KINDS := ["plains", "forest", "hills", "mountains", "urban", "river_crossing"]
	const PLATES := {              # a kind that spans the table: any of its plates
		"plains": ["plains_1", "plains_2", "plains_3"],
		"hills": ["hills_1", "hills_2"],
		"mountains": ["mountains_1", "mountains_2"],
		"river_crossing": ["river_crossing_1"],
	}
	const SIDED := {               # a kind on the defender's half: the plate with its feature there
		"forest": {"right": ["forest_1"], "left": ["forest_2"]},
		"urban": {"right": ["urban_1"], "left": ["urban_2"]},
	}
	const PLATE_DIR := "res://assets/textures/battle/"
	const SIDE := 14.0                             # the sheet's margin on the felt, left and right
	const TOP := 40.0                              # ...under the loss counters' line
	const FOOT := 14.0
	const SHADOW := Color(0.0, 0.0, 0.0, 0.42)
	const EDGE_LIT := Color(0.86, 0.80, 0.62, 0.16)  # its trimmed edge, where the lamp catches it
	var kind := ""
	var dir := 1.0
	var felt := Vector2(948.0, 440.0)
	var seed_text := ""
	var plate := ""                                # the plate on the table (the walk reads it)
	var _tex: Texture2D = null

	func _rng() -> RandomNumberGenerator:
		var rng := RandomNumberGenerator.new()
		rng.seed = (kind + "|" + seed_text).hash()
		return rng

	func _ready() -> void:
		texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
		var names: Array = PLATES.get(kind, [])
		if SIDED.has(kind):
			names = SIDED[kind]["right" if dir > 0.0 else "left"]
		if names.is_empty():
			return
		var rng := _rng()
		plate = str(names[rng.randi() % names.size()])
		var path := PLATE_DIR + plate + ".jpg"
		if ResourceLoader.exists(path):
			_tex = load(path)

	func sheet_rect() -> Rect2:
		return Rect2(Vector2(SIDE, TOP), Vector2(felt.x - 2.0 * SIDE, felt.y - TOP - FOOT))

	func _draw() -> void:
		if _tex == null:
			return
		var r := sheet_rect()
		draw_rect(Rect2(r.position + Vector2(-3.0, 4.0), r.size), SHADOW)   # the sheet's shadow on the felt
		# C15: the survey is cropped to the sheet's aspect, never stretched to it (the plates are
		# wider than tall by 2.155 to 1, the sheet by about 2.38): the full width, a centred band
		var tex_size: Vector2 = _tex.get_size()
		var src_h: float = minf(tex_size.y, tex_size.x * r.size.y / maxf(r.size.x, 1.0))
		var src_w: float = src_h * r.size.x / maxf(r.size.y, 1.0)
		var src := Rect2(Vector2((tex_size.x - src_w) / 2.0, (tex_size.y - src_h) / 2.0), Vector2(src_w, src_h))
		draw_texture_rect_region(_tex, r, src)
		draw_rect(r, EDGE_LIT, false, 1.0)

# ─────────────────────────────────────────────────────────────────────────────
# BA-5: the acts' speed (the user's tick at the gate — "Speed for the acts")
# ─────────────────────────────────────────────────────────────────────────────
# A small switch in Close's room, on the table only while something plays (it
# comes and goes with the skip hint). It runs the ENGINE's clock for the acts — every tween, timer and count of the
# table together (the walk of record plays the scene eight times faster the same
# way) — and gives the clock back the moment the table is final, hidden or gone.
# At the table's own pace it never touches the clock. The setting is written by
# the tableau (`keep_battle_speed`): this helper writes none.

const SPEED_WORDS := {"x1": "Speed ×1", "x2": "Speed ×2"}
const SPEED_TIPS := {
	"x1": "The acts play at their own pace. Press for twice as fast.",
	"x2": "The acts play twice as fast. Press for their own pace.",
}
const SPEED_RIGHT := 44.0             # its right edge is Close's (TRAY_W - 44)
const SPEED_MID_UP := 29.0            # ...and its middle is Close's (TRAY_H - 46 + 34 / 2)
static var _clock_held := false       # the engine's clock is the acts' for now
static var _clock_base := 1.0         # ...and this is what it read before they took it
static var _clock_keeper := 0         # the switch that holds it (an instance id)
var _speed_switch: SpeedSwitch = null


static func speed() -> String:
	"""Settings → Interface → Battle speed: x1 / x2."""
	return UiSettings.get_battle_speed()


static func _run_the_clock(factor: float, keeper: int) -> void:
	"""The engine's clock, for the acts. A factor of 1 gives it back — only the
	switch that holds it may (a table laid again builds its own switch before
	the last one is freed); any other takes it, remembering what it read."""
	if is_equal_approx(factor, 1.0):
		if _clock_held and _clock_keeper == keeper:
			Engine.time_scale = _clock_base
			_clock_held = false
		return
	if not _clock_held:
		_clock_base = Engine.time_scale
		_clock_held = true
	_clock_keeper = keeper
	Engine.time_scale = _clock_base * factor


func _build_the_speed() -> void:
	"""The switch, per showing (a transient of the table: freed when the next is
	laid). It follows the skip hint — there while something plays, gone at rest,
	when Replay and Close take the corner it stood in."""
	_speed_switch = null
	var hint: Label = host._skip_hint
	if hint == null or not is_instance_valid(hint):
		return
	var sw := SpeedSwitch.new()
	sw.name = "SpeedSwitch"
	sw.acts = self
	sw.hint = hint
	sw.focus_mode = Control.FOCUS_NONE       # Space and Enter stay the table's (skip, then close)
	for face in [&"normal", &"hover", &"pressed"]:
		# Replay's own face (a dark ground, a gilt rim), drawn closer: a quieter
		# control than the two buttons the table ends on
		var st: StyleBoxFlat = host._replay_face(face != &"normal")
		st.content_margin_left = 9.0
		st.content_margin_right = 9.0
		st.content_margin_top = 2.0
		st.content_margin_bottom = 2.0
		sw.add_theme_stylebox_override(face, st)
	for ink in [&"font_color", &"font_hover_color", &"font_pressed_color"]:
		sw.add_theme_color_override(ink, Utils.UI_GOLD)
	sw.visible = hint.visible
	host._tray_inner.add_child(sw)
	host._transients.append(sw)
	_speed_switch = sw
	_speed_retext()
	# In Close's own room — the bottom right, empty while something plays (Replay
	# and Close come with the gavel, and the switch goes with the skip hint). Not
	# beside the hint's words: the seal stands LEFT of the plate and reaches that
	# side whenever the plate runs wide, while Close's room is kept clear of the
	# plate, the seal and the laurels by the table's own laws.
	var sw_size: Vector2 = sw.get_combined_minimum_size()
	sw.position = Vector2(host.TRAY_W - SPEED_RIGHT - sw_size.x,
			host.tray_h() - SPEED_MID_UP - sw_size.y / 2.0)
	sw.pressed.connect(_on_speed_pressed)
	hint.visibility_changed.connect(sw.follow)
	_speed_sync(sw)


func _speed_retext() -> void:
	if _speed_switch == null or not is_instance_valid(_speed_switch):
		return
	var now := speed()
	_speed_switch.text = str(SPEED_WORDS.get(now, now))
	_speed_switch.tooltip_text = str(SPEED_TIPS.get(now, ""))
	_speed_switch.reset_size()


func _speed_sync(sw: Node, gone: bool = false) -> void:
	"""The clock follows the switch: the acts' pace while it stands on a table
	that is playing, the engine's own the moment it is hidden, off the tree or
	freed."""
	var playing: bool = not gone and sw.is_inside_tree() and (sw as CanvasItem).is_visible_in_tree()
	var factor: float = float(UiSettings.BATTLE_SPEED_FACTORS.get(speed(), 1.0)) if playing else 1.0
	_run_the_clock(factor, sw.get_instance_id())


func _on_speed_pressed() -> void:
	var speeds: Array = UiSettings.BATTLE_SPEEDS
	var next := str(speeds[(speeds.find(speed()) + 1) % speeds.size()])
	host.keep_battle_speed(next)      # the tableau writes the setting; this helper writes none
	_speed_retext()
	if _speed_switch != null and is_instance_valid(_speed_switch):
		_speed_sync(_speed_switch)
	host._cue("tick")


class SpeedSwitch:
	extends Button
	# The acts are a RefCounted and keep no clock: this button, a child of the
	# tray (freed when the next table is laid), keeps the engine's for them.
	var acts = null
	var hint: CanvasItem = null

	func follow() -> void:
		if hint != null and is_instance_valid(hint):
			visible = hint.visible
		if acts != null:
			acts._speed_sync(self)

	func _notification(what: int) -> void:
		if acts == null:
			return
		if what == NOTIFICATION_VISIBILITY_CHANGED:
			acts._speed_sync(self)
		elif what == NOTIFICATION_EXIT_TREE:
			acts._speed_sync(self, true)


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
const DAY_BOTTOM := 738.0              # the tray's floor, less its edge (plus the room: `_day_floor`)
# Row BA, the levers past 5 (the readers' agency 5 and clarity 5, bar 7): the tray grows by
# this much, at its foot, while a day's panel stands (`BattleDiorama.set_day_room`); the
# miniature keeps its place and the words keep their faces.
const DAY_ROOM := 110.0
const DAY_MEASURE_W := 4000.0           # the width a row of cards is measured in (read, then given its own)
const DAY_MORE_SHOWN := 3              # the chips of the other kinds the digits 4-6 reach: the rest ride "+N more"
const DAY_MORE_KEY := "daymore"
const DAY_LEGEND_HOVER := "Gold names are each side's lead; a gold square is a point in hand and a grey one a point spent; the keys 1 to 9 say the words; a card shows its price, what it does and what it risks."
const DAY_CHIPS_W := 680.0             # clear of Replay (x 726) and Close (x 846) at y 698
const DAY_CHIP_BG := "233043"
const DAY_CARD_BG := "2e3d57"          # BA-5: a word's card: a lighter ground than a chip's, under a gilt rim
const DAY_CAPTION_INK := "dcd8cc"      # ...in an ink that reads 7.7 to 1 on the card's ground (the info grey read 4.2, under the floor;
                                       # the second reading still called the line dim at 5.8)
const DAY_HEAD_Y := 9.0                # BA-5: the band above the baize (the tray's y) — the day's own NAME stands there
const DAY_EXIT_INK := "c9c2b2"         # BA-5, the second reading: an exit costs nothing — bone on a quiet ground,
const DAY_EXIT_RIM := Utils.CHIP_EXIT_RIM   # ...a dim rim: the words that cost points are the loudest things on the table
const DAY_EXIT_CARD_BG := "1c222c"
const DAY_EXIT_FLOOR := 3.0            # ...and as cards they stand beside the buttons, this far above the tray's floor
const DAY_LIFT := 8.0                  # ...and before a word loses what it does the panel takes this much of the gap under the bars
const DAY_PIP_ON := "d9c08c"
const DAY_PIP_OFF := Utils.CHIP_DIM_INK   # a spent point (the locked chip's own grey)
const DAY_OWN_KINDS := ["press", "guard", "dig_in"]            # the lead's own words (row C)
const DAY_EXIT_KINDS := ["stand", "break_off"]                 # the exits (row E, with leave_it)
# BA-5: level with the buttons the exits' row is short of room. What an exit
# does stays on its face in this order, as far as the row fits left of Replay:
# to leave the day to the marshal (what he would do), to leave the field, to stand.
const DAY_TAG_ORDER := ["leave_it", "break_off", "stand"]
# BA-5, the second reading: a group's label says what its kind of word DOES ("Another
# leads · 1" read as a riddle); its price follows in points.
const DAY_GROUP_LABEL := {"lead": "Another leads the attack", "bring_up": "Bring up",
	"cannonade": "The guns, no clash"}
# ...and the day's rule stands on every table that offers its words, in one caption line
# ("keep this explainer visible on every turn"): what a word costs, what decides, what ends it.
const DAY_RULE := "A word costs points, and he answers it. A line that breaks decides the day; two silences running, or no point left, and night falls: nothing decided."
# Row PW "Plain Words" (November 18, 2026 — the first playtest: "battles are opaque
# and its unclear what decisions mean"): a day whose block carries `rule` speaks in
# everyday words (`battle_telling.speak_plainly`) — the table's own captions follow it.
# A block without one (the seam down, an older payload) keeps the idiom above.
const DAY_GROUP_LABEL_PLAIN := {"lead": "Attack with another corps", "bring_up": "Bring up",
	"cannonade": "Bombard, no clash"}
const DAY_LEGEND_HOVER_PLAIN := "Gold names are each side's commander; a gold square is a battle point in hand and a grey one a point spent; the keys 1 to 9 give the orders; a card shows its price, what it does and what to expect."


func _day_is_plain() -> bool:
	return str(_the_day().get("rule", "")) != ""


static func payload_is_plain(data) -> bool:
	"""Row PW: this tableau speaks in everyday words — the server says so
	(`plain`, every battle), or its open day does (`rule`)."""
	if not (data is Dictionary):
		return false
	if bool((data as Dictionary).get("plain", false)):
		return true
	var day = (data as Dictionary).get("day", null)
	return day is Dictionary and str((day as Dictionary).get("rule", "")) != ""


func _day_rule() -> String:
	var said := str(_the_day().get("rule", ""))
	return said if said != "" else DAY_RULE


func _day_legend_hover() -> String:
	return DAY_LEGEND_HOVER_PLAIN if _day_is_plain() else DAY_LEGEND_HOVER


func _day_group_label(kind: String) -> String:
	var table: Dictionary = DAY_GROUP_LABEL_PLAIN if _day_is_plain() else DAY_GROUP_LABEL
	return str(table.get(kind, DAY_GROUP_LABEL.get(kind, kind)))


const DAY_CLASH_SCOPE := " LOST THIS CLASH"   # the two counters' scope on a day's table, in the room of " LOSSES" (the line under the title counts the day)
const DAY_LOSSES := " LOSSES"                 # ...the host's own word (a fleet action counts sail and hangs no day)
const DAY_SCOPE_ROOM := 300.0              # ...as wide as a caption may run before it nears the headline (a long crown's name keeps " LOSSES")
const SUB_CLEAR := 8.0                     # the line under the headline stands this clear of the reserve's dead
var _sub_host := ""                        # (the review) the line's host part (a province's own line), for its fit
var _sub_told := ""                        # ...and what told, as the server said it

var _day_panel: Control = null
var _day_chips: RichTextLabel = null   # row C: the lead's own words, full chips
var _day_groups: RichTextLabel = null  # rows D: one line per kind, a label then name-only chips
var _day_exits: RichTextLabel = null   # row E: the exits, always on the table, never scrolled
var _day_latched := false              # one press, one word: inert until new data
var _day_asked := false                # a day awaiting HIS word asked the server once
var _day_hide_shelves := false         # the panel took the shelves' room
var _day_inline := false               # the groups flow in one paragraph (room was short)
var _day_cards := false                # BA-5: row C is two-line cards (the word, and what it does)
var _day_exit_tags := false            # BA-5: the exits say what they do on their faces
var _day_tags_kept := 0                # BA-5: level with the buttons, how many (in DAY_TAG_ORDER) still say it
var _day_exits_up := false             # BA-5: the exits are two-line cards beside the buttons (the walk reads it)
var _day_rule_row := false             # BA-5: the day's rule has its caption line (the walk reads it)
var _day_exits_wide := false           # BA-5: the exits' cards gave way to the one-line chips for their WIDTH (the walk reads it)
var _day_exits_row_tried := false      # BA-6: beside the buttons the cards did not fit, so the full-width row was tried (the walk reads it)
var _relaying := false                 # BA-6: `_relay_the_day` rebuilds the panel: the latches, "+N more" and the first-day line stand
var _day_cards_wide := false           # BA-6: the cards' second lines went for their width, not for room (the walk reads it)
var _day_risk_lines := false           # BA-6: the cards' third line — what the word risks (the walk reads it)
var _day_legend_row := false           # BA-6: the table's marks have their caption line (the walk reads it)
var _day_more_open := false            # BA-6: "+N more" was pressed: every chip of the groups stands
var _day_more_n := 0                   # BA-6: the chips of the groups the digits do not reach
var _day_exits_row := false            # BA-6: the exits' cards stand full width, above the buttons (the walk reads it)
var _day_exits_wrapped := false        # BA-6: ...and their second line wraps at a semicolon (the walk reads it)
var _day_groups_scrolls := false       # BA-6: whether the groups scroll as the ladder left them
var _day_lifted := false               # BA-5: the panel took DAY_LIFT of the gap under the bars (the walk reads it)
var _day_top_plain := 0.0              # ...and where its top stands without that (the walk reads it)
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
# BA-5 (the user's tick - "Sounds for the day"): the day's own beats, in cues the game
# already has. A word given, by its kind; his word that was no clash; how a day closed.
const DAY_WORD_CUES := {
	"press": "bugle_to_arms", "lead": "bugle_to_arms", "guard": "drum_cadence",
	"cannonade": "cannon_distant", "bring_up": "order_march", "dig_in": "spade",
	"stand": "tick", "break_off": "boots", "leave_it": "select",
}
const DAY_HIS_CUES := {"dig_in": "spade", "bring_up": "order_march"}
const DAY_END_CUES := {"night": "bugle_retreat", "drew_off": "boots", "broke_off": "boots", "fell_back": "boots"}
const DAY_SILENT_KINDS := ["clash", "tally", "shape", "after"]     # lines told that are no word
static var _day_sounded: Dictionary = {}     # enemy -> what the table last sounded of his day
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
	l.hint_underlined = false                # BA-5: a hover is not a link (the readers took the dotted rule for one)
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


func _day_reading(day: Dictionary) -> String:
	"""BA-5: Berthier's reading of his next word — "he will strike", "he may
	strike", "he will not strike" (`battle_telling.reading_of`: the rule he
	follows, shown only as far as the player can see). "" when the table
	carries none."""
	var r = day.get("reading", null)
	return str((r as Dictionary).get("line", "")) if r is Dictionary else ""


func _day_head(day: Dictionary, level: int) -> String:
	"""One line, the day's STAKES: the lead and his purse against the enemy and
	his, in pips and — as room allows (level 1) — in words ("2 of 2 points");
	then his temper (level 2) and whether a road lies open behind him (level 3);
	and last, at every level, Berthier's reading of him (BA-5). The words give
	way in this order: his road, his temper, the purses' words."""
	var ours: int = int(day.get("ours", 0))
	var theirs: int = int(day.get("theirs", 0))
	var ours_of: int = int(day.get("ours_of", 0))
	var theirs_of: int = int(day.get("theirs_of", 0))
	var slots_ours: int = ours_of if ours_of > 0 else maxi(ours, 2)
	var slots_his: int = theirs_of if theirs_of > 0 else maxi(theirs, 2)
	var lead := str(day.get("lead_shown", ""))
	var foe := str(day.get("enemy_shown", ""))
	var info := "[color=#" + Utils.COLOR_INFO + "]"
	var out := "[color=#" + Utils.COLOR_GOLD + "]" + lead + "[/color] " + _day_pips(ours, slots_ours)
	if level >= 1:
		out += info + "%d of %d points[/color] " % [ours, slots_ours]
	out += info + "against[/color] [color=#" + Utils.COLOR_GOLD + "]" + foe + "[/color] " \
		+ _day_pips(theirs, slots_his)
	if level >= 1:
		out += info + "%d of %d[/color]" % [theirs, slots_his]
	if level >= 2 and str(day.get("his_temper", "")) != "":
		out += " " + info + "· " + str(day.get("his_temper", "")) + "[/color]"
	if level >= 3 and _day_road(day) != "":
		out += " " + info + "· " + _day_road(day) + "[/color]"
	if _day_reading(day) != "":
		out += " " + info + "·[/color] [color=#" + Utils.COLOR_WARNING + "]" + _day_reading(day) + "[/color]"
	return out


func _day_name() -> String:
	"""The battle's name and its turn, as the plate engraves them — for the band
	above the baize (the panel stands in the plate's room; the second reading:
	"battle name and footer are gone in the day frames")."""
	var named := str(host._data.get("battle_name", "")).strip_edges()
	if named == "" or named == "<null>":
		return ""
	return "%s  ·  TURN %d" % [named.to_upper(), int(host._data.get("turn", 0))]


func _scope_the_counters() -> void:
	"""The second reading: on a day's table the two counters count the CLASH the
	table shows while the line under the title counts the day — two "losses" on
	one screen. Each counter's caption says its scope, where the words fit the
	caption's own box (the host writes the captions afresh at every populate)."""
	for cap in [host._odo_left_cap, host._odo_right_cap]:
		if cap == null or not is_instance_valid(cap):
			continue
		var plain: String = str(cap.text)
		if not plain.ends_with(DAY_LOSSES):
			continue
		cap.text = plain.substr(0, plain.length() - DAY_LOSSES.length()) + DAY_CLASH_SCOPE
		var need: float = cap.get_minimum_size().x
		if need > DAY_SCOPE_ROOM:
			cap.text = plain
		elif cap == host._odo_right_cap and need > cap.size.x:
			# (at Text size 130 % the words outgrow the right-hand caption's own box, and a label
			# grows to its right — off the baize: it keeps its right edge instead)
			var right_edge: float = cap.position.x + cap.size.x
			cap.size.x = need
			cap.position.x = right_edge - need


func _day_told_lines(day: Dictionary) -> Array:
	var out: Array = []
	var told = day.get("told", [])
	if told is Array:
		for t in told:
			if t is Dictionary and str(t.get("line", "")) != "":
				out.append(t)
	return out


func _day_told_kept(lines: Array, keep: int) -> Array:
	"""(The review) The told lines a table keeps, `keep` of them, by index in
	their order. A closed day keeps first the line that says HOW it ended (its
	first "end" line), then the rest of its close in order (the tally, whom the
	toll favoured and its shape, what follows), then its words and clashes,
	newest first; a day still open keeps its last `keep`, as before."""
	var n := lines.size()
	var first_end := -1
	for i in range(n):
		if str((lines[i] as Dictionary).get("who", "")) == "end":
			first_end = i
			break
	var pick: Array = []
	if first_end < 0 or keep >= n:
		for i in range(maxi(0, n - keep), n):
			pick.append(i)
		return pick
	for i in range(first_end, n):
		if pick.size() < keep:
			pick.append(i)
	var j := first_end - 1
	while pick.size() < keep and j >= 0:
		pick.append(j)
		j -= 1
	pick.sort()
	return pick


func _day_told(lines: Array, keep: int) -> String:
	var out := ""
	for i in _day_told_kept(lines, keep):
		var t: Dictionary = lines[i]
		var who := str(t.get("who", ""))
		# BA-5: a clash's own line (who "clash") is set apart from the words
		# that fought it — the neutral ink, upright; the day's end is italic.
		var hex := Utils.COLOR_GOLD if who == "ours" else (
			Utils.COLOR_INFO if who in ["end", "clash"] else Utils.COLOR_TEXT)
		var line := str(t.get("line", "")).replace("[", "[lb]")
		line = "[i]" + line + "[/i]" if who == "end" else line
		out += ("\n" if out != "" else "") + "[color=#" + hex + "]" + line + "[/color]"
	return out


func _day_chip_label(chip: Dictionary) -> String:
	"""A word that costs nothing shows no price. (The server's label is shown
	as it is: "Mack strikes back" is never rewritten here.)"""
	var price := int(chip.get("price", 0))
	var label := str(chip.get("label", ""))
	return label if price <= 0 else "%s · %d" % [label, price]


static func _sentence(words: String) -> String:
	""""he keeps the field" -> "He keeps the field." (a hover's own sentence)."""
	var s := words.strip_edges()
	if s == "":
		return ""
	s = s.substr(0, 1).to_upper() + s.substr(1)
	return s if s.ends_with(".") else s + "."


func _day_chip_tip(chip: Dictionary, with_label: bool = false, with_does: bool = true, with_risk: bool = true) -> String:
	"""A chip's hover: why it is locked (always — a dim chip carries its reason
	as its hover, wherever else it stands); what the word does, where its face
	does not say it (BA-5: `does`), and the rest of it (`more`); whether the
	marshal may object."""
	var parts: Array = []
	if with_label:
		parts.append(_day_chip_label(chip) + ".")
	if not bool(chip.get("ok", false)) and str(chip.get("why", "")) != "":
		parts.append(str(chip.get("why", "")))
	var does := str(chip.get("does", ""))
	if with_does and does != "":
		parts.append(_sentence(does))
	if with_risk and str(chip.get("risk", "")) != "":
		parts.append(("Expect: " if _day_is_plain() else "It risks: ") + str(chip.get("risk", "")) + ".")     # BA-6: the third line, where the face has no room for it
	if str(chip.get("more", "")) != "":
		parts.append(str(chip.get("more", "")))
	if str(chip.get("counsel", "none")) == "possible":
		parts.append("The marshal may object to this word.")
	if does == "" and str(chip.get("odds", "")) != "":
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


func _day_chip_bb(i: int, chip: Dictionary, name_only: bool = false, tagged: bool = false) -> String:
	"""A word as a one-line chip. `tagged` (BA-5, the exits): what the word
	does stands on its face after a dash, and is then left out of its hover."""
	var is_exit: bool = str(chip.get("word", "")) != "" or str(chip.get("kind", "")) in DAY_EXIT_KINDS
	var label := _day_chip_label(chip)
	if name_only:
		label = str(chip.get("shown", "")) if str(chip.get("shown", "")) != "" else str(chip.get("label", ""))
	var does := str(chip.get("does", ""))
	var on_face: bool = tagged and not name_only and does != ""
	if on_face:
		label += " — " + does
	var digit: int = int(_day_digit_of.get(i, 0))
	if digit > 0:
		label = "%d %s" % [digit, label]          # the selection card's form: "<digit> Label"
	var tip := _day_chip_tip(chip, name_only, not on_face)
	if bool(chip.get("ok", false)) and not _day_latched:
		# (the second reading: an exit costs nothing and reads quieter than a word that costs points)
		return Utils.bb_button_chip("day:%d" % i, label,
				DAY_EXIT_INK if is_exit else Utils.COLOR_GOLD,
				DAY_EXIT_CARD_BG if is_exit else DAY_CHIP_BG, "", tip)
	return Utils.bb_chip_disabled(label, "", tip)


func _day_card_bb(i: int, chip: Dictionary) -> String:
	"""BA-5: a word of the lead's own as a two-line CARD — the chip's own cell
	(one rich-text system: the same link, hover and digit) with a second line:
	the digit, the word and its price in points; under it what the word does.
	A locked card says on its face why it is locked."""
	var lit: bool = bool(chip.get("ok", false)) and not _day_latched
	var price := int(chip.get("price", 0))
	var head := str(chip.get("label", ""))
	if price > 0:
		head += " · %d %s" % [price, "point" if price == 1 else "points"]
	var digit: int = int(_day_digit_of.get(i, 0))
	if digit > 0:
		head = "%d %s" % [digit, head]
	var why := str(chip.get("why", ""))
	var caption := str(chip.get("does", "")) if (lit or why == "") else why
	var ink := Utils.COLOR_GOLD if lit else Utils.CHIP_DIM_INK
	var sub := DAY_CAPTION_INK if lit else Utils.CHIP_DIM_INK
	var inner := "[color=#" + ink + "]" + Utils.CHIP_PAD + head.replace(" ", " ") + Utils.CHIP_PAD + "[/color]"
	if caption != "":
		var second: String = "[color=#%s]%s%s%s[/color]" % [
			sub, Utils.CHIP_PAD,
			caption.replace("[", "[lb]").replace(" ", " "), Utils.CHIP_PAD]
		inner += "\n" + Utils.bb_step(second, &"Caption")   # the ladder's Caption step
	# BA-6: the third line, what the word risks — the Caption step, in the caption ink
	var risk := str(chip.get("risk", ""))
	var risk_on_face: bool = lit and _day_risk_lines and risk != ""
	if risk_on_face:
		var third: String = "[color=#%s]%s%s%s[/color]" % [
			sub, Utils.CHIP_PAD, risk.replace("[", "[lb]").replace(" ", "\u00A0"), Utils.CHIP_PAD]
		inner += "\n" + Utils.bb_step(third, &"Caption")
	# the hover: the rest of what the word does (its face says the first of it)
	# (the review) a locked card's face says why: its hover says it too, and what the word would do
	var tip := _day_chip_tip(chip, false, not lit and why != "", not risk_on_face)
	if tip != "":
		inner = Utils.bb_hint(inner, tip)
	if lit:
		return Utils.CHIP_OPEN_HEAD + Utils.COLOR_GOLD + Utils.CHIP_RIM_ALPHA + " bg=#" + DAY_CARD_BG \
			+ "][url=day:%d]" % i + inner + "[/url]" + Utils.CHIP_CLOSE
	return Utils.CHIP_OPEN_HEAD + Utils.CHIP_DIM_RIM + " bg=#" + Utils.CHIP_DIM_BG + "]" \
		+ Utils.bb_icon(Utils.LOCK_GLYPH, 16, Utils.CHIP_DIM_INK) + " " + inner + Utils.CHIP_CLOSE


func _day_own_text() -> String:
	if not _day_offering():
		return ""
	var chips = _the_day().get("chips", [])
	var out := ""
	for i in _day_split()[0]:
		out += (_day_card_bb(int(i), chips[int(i)]) if _day_cards
				else _day_chip_bb(int(i), chips[int(i)])) + " "
	return out


func _day_groups_text(inline: bool = false) -> String:
	"""One line per kind: a plain label once — what that kind of word DOES, and
	its price in points (the second reading: "Another leads · 1" and "Bring up
	· 1" read as riddles) — then name-only chips, for a kind of one word as for
	a kind of five. A kind this table has no label for is written whole, as
	before. `inline`: every group flows in ONE paragraph with a clear gap
	between groups."""
	if not _day_offering():
		return ""
	var chips = _the_day().get("chips", [])
	var info := "[color=#" + Utils.COLOR_INFO + "]"
	var lines: Array = []
	for g in _day_split()[1]:
		# BA-6 (fewer chips): the chips the digits 4-6 reach stand; the rest ride "+N more"
		var idx: Array = []
		for i in g["idx"]:
			if _day_more_open or _day_digit_of.has(int(i)):
				idx.append(i)
		if idx.is_empty():
			continue
		if not DAY_GROUP_LABEL.has(g["kind"]):
			for i in idx:
				lines.append(_day_chip_bb(int(i), chips[int(i)]) + " ")
			continue
		var first: Dictionary = chips[int(idx[0])]
		var price := int(first.get("price", 0))
		var label: String = _day_group_label(str(g["kind"]))
		var paid := (" · %d %s" % [price, "point" if price == 1 else "points"]) if price > 0 else ""
		# (a label never breaks inside itself, nor from its first chip)
		var line := info + (label + paid).replace(" ", "\u00A0") + ":[/color]\u00A0"
		for i in idx:
			line += _day_chip_bb(int(i), chips[int(i)], true) + " "
		lines.append(line)
	var more := _day_more_chip()
	if more != "":
		if lines.is_empty():
			lines.append(more)
		else:
			lines[lines.size() - 1] = str(lines[lines.size() - 1]) + more + " "
	return ("      " if inline else "\n").join(PackedStringArray(lines))


func _day_hidden_groups() -> Array:
	"""BA-6: the indices (into `chips`) of the groups' words the digits do not reach."""
	var out: Array = []
	if not _day_offering():
		return out
	for g in _day_split()[1]:
		for i in g["idx"]:
			if not _day_digit_of.has(int(i)):
				out.append(int(i))
	return out


func _day_more_chip() -> String:
	"""BA-6: the one quiet chip that holds the rest of the groups' words: "+N more"
	(its hover names them), and "show fewer" once pressed."""
	var hidden := _day_hidden_groups()
	if hidden.is_empty():
		return ""
	var chips = _the_day().get("chips", [])
	var names: Array = []
	for i in hidden:
		names.append(str((chips[int(i)] as Dictionary).get("label", "")))
	if _day_more_open:
		return Utils.bb_button_chip(DAY_MORE_KEY, "show fewer", DAY_EXIT_INK, DAY_EXIT_CARD_BG, "",
				"Back to the words the keys 4 to 6 reach.")
	return Utils.bb_button_chip(DAY_MORE_KEY, "+%d more" % hidden.size(), DAY_EXIT_INK, DAY_EXIT_CARD_BG, "",
			"Press to show every word. Also: " + ", ".join(PackedStringArray(names)) + ".")


func _day_legend_bb() -> String:
	"""BA-6: the table's marks in one caption line, in the marks themselves (the head's
	gold name and its squares — drawn, so no font's missing glyph shows as a box)."""
	var info := "[color=#" + Utils.COLOR_INFO + "]"
	var gold := "[color=#" + Utils.COLOR_GOLD + "]"
	return info + gold + "name[/color] each side's lead · " \
		+ Utils.bb_icon(Utils.SWATCH, 10, DAY_PIP_ON) + " a point in hand · " \
		+ Utils.bb_icon(Utils.SWATCH, 10, DAY_PIP_OFF) \
		+ " a point spent · keys 1-9 say the words · a card: its price, what it does, what it risks[/color]"


func _day_floor() -> float:
	"""The panel's floor now: the tray's, with the room a day's panel asks for."""
	return DAY_BOTTOM + (host._day_room if host != null else 0.0)


static func _wrap_does(does: String) -> Array:
	"""BA-6: an exit's stakes in two lines, broken at a semicolon where the words have one
	(["the day ends; he keeps the field", "the toll stands at ..."]); one line otherwise."""
	var parts: PackedStringArray = does.split("; ")
	if parts.size() < 2:
		return [does]
	var cut := int(ceil(float(parts.size()) / 2.0))
	return ["; ".join(parts.slice(0, cut)), "; ".join(parts.slice(cut))]


func _day_exit_rank(chip: Dictionary) -> int:
	"""An exit's place in DAY_TAG_ORDER (-1: none)."""
	if str(chip.get("word", "")) == "leave_it":
		return 0
	return DAY_TAG_ORDER.find(str(chip.get("kind", "")))


func _day_exit_tagged(chip: Dictionary) -> bool:
	"""Whether this exit says what it does on its face as a one-line chip: level
	with the buttons, the first `_day_tags_kept` of the order. (As cards every
	exit says it: `_day_exit_card_bb`.)"""
	if _day_exit_tags:
		return true
	var rank := _day_exit_rank(chip)
	return rank >= 0 and rank < _day_tags_kept


func _day_exit_card_bb(i: int, chip: Dictionary) -> String:
	"""BA-5, the second reading ("put a one-line consequence on EVERY button"):
	an exit as a two-line card, quieter than a word that costs points — the
	digit and the word; under it its price ("free") and what it does. A locked
	exit says on its face why it is locked."""
	var lit: bool = bool(chip.get("ok", false)) and not _day_latched
	var head := str(chip.get("label", ""))
	var digit: int = int(_day_digit_of.get(i, 0))
	if digit > 0:
		head = "%d %s" % [digit, head]
	var price := int(chip.get("price", 0))
	var paid := "free" if price <= 0 else "%d %s" % [price, "point" if price == 1 else "points"]
	var why := str(chip.get("why", ""))
	var does := str(chip.get("does", ""))
	var caption := (paid + (" · " + does if does != "" else "")) if (lit or why == "") else why
	var third_line := ""
	if _day_exits_wrapped and (lit or why == "") and does != "":
		var halves := _wrap_does(does)           # BA-6: the stakes on two lines
		caption = paid + " · " + str(halves[0])
		if halves.size() > 1:
			third_line = str(halves[1])
	var ink := DAY_EXIT_INK if lit else Utils.CHIP_DIM_INK
	var sub := DAY_CAPTION_INK if lit else Utils.CHIP_DIM_INK
	var inner := "[color=#" + ink + "]" + Utils.CHIP_PAD + head.replace(" ", " ") + Utils.CHIP_PAD + "[/color]"
	var second: String = "[color=#%s]%s%s%s[/color]" % [
		sub, Utils.CHIP_PAD,
		caption.replace("[", "[lb]").replace(" ", " "), Utils.CHIP_PAD]
	inner += "\n" + Utils.bb_step(second, &"Caption")   # the ladder's Caption step
	if third_line != "":
		inner += "\n" + Utils.bb_step("[color=#%s]%s%s%s[/color]" % [
			sub, Utils.CHIP_PAD, third_line.replace("[", "[lb]").replace(" ", "\u00A0"), Utils.CHIP_PAD], &"Caption")
	# the hover: the rest of what the word does (its face says the first of it)
	# (the review) a locked card's face says why: its hover says it too, and what the word would do
	var tip := _day_chip_tip(chip, false, not lit and why != "")
	if tip != "":
		inner = Utils.bb_hint(inner, tip)
	if lit:
		return Utils.CHIP_OPEN_HEAD + DAY_EXIT_RIM + Utils.CHIP_RIM_ALPHA + " bg=#" + DAY_EXIT_CARD_BG \
			+ "][url=day:%d]" % i + inner + "[/url]" + Utils.CHIP_CLOSE
	return Utils.CHIP_OPEN_HEAD + Utils.CHIP_DIM_RIM + " bg=#" + Utils.CHIP_DIM_BG + "]" \
		+ Utils.bb_icon(Utils.LOCK_GLYPH, 16, Utils.CHIP_DIM_INK) + " " + inner + Utils.CHIP_CLOSE


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
		if _day_exit_tags:
			out += _day_exit_card_bb(int(i), chip) + " "      # a card says its price and what it does
			continue
		if str(chip.get("word", "")) == "leave_it":
			out += "[color=#" + Utils.COLOR_INFO + "]|[/color] "      # it ends our say: set apart
		out += _day_chip_bb(int(i), chip, false, _day_exit_tagged(chip)) + " "
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


func _day_has_panel() -> bool:
	"""Whether `_build_the_day` builds a panel for this table (its own early returns)."""
	var day := _the_day()
	if day.is_empty() or host == null or host._verdict == null:
		return false
	return _day_banner() != "" or bool(day.get("open", false))


func _build_the_day() -> void:
	"""At the end of the dress: the panel, hidden. Nothing for a payload that
	carries no `day` (a small battle, a fleet action, a harness world) or whose
	day was decided by its clash (its own verdict stands).
	BA-5, the second reading: the panel is ONE decision block, read top to
	bottom. H, the STAKES (each purse in pips and in words, his temper and road,
	Berthier's reading), heads it — right above the words it governs; the band
	above the baize carries the battle's NAME (the plate's, whose room the panel
	takes). Under the head: F the first day's line, or R the day's rule in one
	caption line; B the last word told; C the lead's own words (two-line cards:
	the word and its price, and what it does); D the other kinds of word, each
	under a label that says what the kind does; E the exits — two-line cards
	beside the buttons (the word, and "free · what it does") or, where those do
	not fit, one-line chips level with the buttons that keep in DAY_TAG_ORDER
	what fits left of Replay of what they do (the rest rides their hovers).
	Every row's height is what its text measures, so a row is whole or not
	there. Room is made in this order: the shelves give theirs, the groups flow
	inline, the rule rides the head's hover, the told line rides it, the first
	day's line rides it too (unacknowledged — and the told line then has its
	row back if it fits), the panel takes DAY_LIFT of the gap under the bars,
	the exits' cards give way to the one-line chips, the cards' second lines
	ride their hovers, the groups scroll."""
	_day_panel = null
	_day_chips = null
	_day_groups = null
	_day_exits = null
	if not _relaying:
		_day_latched = false
		_day_asked = false
	_day_hide_shelves = false
	_day_inline = false
	_day_cards = false
	_day_exit_tags = false
	_day_tags_kept = 0
	_day_exits_up = false
	_day_rule_row = false
	_day_exits_wide = false
	_day_exits_row_tried = false
	_day_lifted = false
	_day_risk_lines = false
	_day_cards_wide = false
	_day_legend_row = false
	if not _relaying:
		_day_more_open = false          # a NEW table starts with the keys' three; a relay keeps what was pressed
	_day_more_n = 0
	_day_exits_row = false
	_day_exits_wrapped = false
	_day_groups_scrolls = false
	_his_waiting = false
	_day_digit_of = {}
	_day_denied = 0
	if not _relaying:
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
		# under it, the sub-banner tells the day so far (BA-5: its own toll and
		# who has the better of it) — unless the host's own line is there (a
		# province that changed hands); the next populate sets its own text
		var morning_said := str(day.get("morning", ""))
		if morning_said != "" and host._sub_banner.text == "":
			host._sub_banner.text = morning_said
	# ...and the two counters say they count this clash (the line under the title counts the day)
	_scope_the_counters()

	var head := _day_rtl(panel, Vector2.ZERO, Vector2(DAY_W, 31.0))
	head.name = "DayHead"
	head.autowrap_mode = TextServer.AUTOWRAP_OFF
	var lh: float = _day_line_h(head)
	var head_h: float = lh + 2.0
	head.size.y = head_h
	# the band above the baize: the battle's own name (the plate stands under the panel)
	var name_label: Label = null
	if _day_name() != "":
		name_label = host._mk_label(panel, _day_name(), &"Caption", BRASS, host._font_engraved)
		name_label.name = "DayName"
		name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		name_label.size = Vector2(DAY_W, name_label.get_minimum_size().y)
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
		level -= 1                            # one line at any text size: his road goes first
		head.text = _day_head(day, level)

	var hover: Array = []
	if str(day.get("morning", "")) != "":
		hover.append(str(day.get("morning", "")))
	var aside: Array = []
	if level < 2 and str(day.get("his_temper", "")) != "":
		aside.append(str(day.get("his_temper", "")))
	if level < 3 and _day_road(day) != "":
		aside.append(_day_road(day))
	if not aside.is_empty():
		hover.append(" — ".join(PackedStringArray(aside)) + ".")
	var reading = day.get("reading", null)
	if reading is Dictionary and str((reading as Dictionary).get("hover", "")) != "":
		hover.append(str((reading as Dictionary).get("hover", "")))
	var lines := _day_told_lines(day)
	var offering := _day_offering()
	var pending: bool = bool(day.get("open", false)) and bool(day.get("pending", false)) \
		and str(day.get("awaits", "")) == "ours"

	# the buttons' row: the exits stand beside Replay / Close
	var btn_top: float = host._btn_close.position.y
	var btn_h: float = maxf(host._btn_close.size.y, host._btn_close.custom_minimum_size.y)
	var btn_mid: float = btn_top + btn_h / 2.0

	var floor_px: float = _day_floor()
	var top: float = top_with
	_day_top_plain = top_with
	var y: float = head_h                     # the head is the panel's first row
	if not offering and not pending:
		# no chips (closed, his word, his clash follows): the told block, whole
		# — and above the buttons' row
		var floor_y: float = minf(floor_px, btn_top - 4.0)
		if first_box != null and floor_y - top - y - first_h >= lh:
			first_box.visible = true          # the first day's line, right under the head
			first_box.position = Vector2(0.0, y)
			first_box.size.y = first_h
			y += first_h
			_day_first_screen = first_screen
		elif first_box != null:
			panel.remove_child(first_box)
			first_box.queue_free()
			hover.append(first_said)
		var avail: float = floor_y - top - y
		var keep := clampi(int(avail / lh), 1, 5)
		var told := _day_rtl(panel, Vector2(0.0, y), Vector2(DAY_W, lh * float(keep) + 2.0))
		told.text = _day_told(lines, keep)
		while keep > 1 and told.get_content_height() > avail:
			keep -= 1                         # BA-6: a wrapped line takes two rows: whole rows or none
			told.text = _day_told(lines, keep)
		told.size.y = minf(maxf(told.get_content_height() + 2.0, lh), avail)
		# (the review) a line of the close the table had no row for rides the head's hover
		var kept_idx := _day_told_kept(lines, keep)
		for i in range(lines.size()):
			if not (i in kept_idx) and str((lines[i] as Dictionary).get("who", "")) == "end":
				hover.append(str((lines[i] as Dictionary).get("line", "")))
	else:
		var split := _day_split()
		var chips_now = day.get("chips", [])
		var c_box: RichTextLabel = null
		var d_box: RichTextLabel = null
		var e_box: RichTextLabel = null
		if offering and not (split[0] as Array).is_empty():
			c_box = _day_rtl(panel, Vector2.ZERO, Vector2(DAY_W, 100.0))
			c_box.mouse_filter = Control.MOUSE_FILTER_STOP
			c_box.meta_underlined = false
			c_box.autowrap_mode = TextServer.AUTOWRAP_OFF
			c_box.meta_clicked.connect(_on_day_chip)
		if offering and not (split[1] as Array).is_empty():
			d_box = _day_rtl(panel, Vector2.ZERO, Vector2(DAY_W, 100.0))
			d_box.mouse_filter = Control.MOUSE_FILTER_STOP
			d_box.meta_underlined = false
			d_box.meta_clicked.connect(_on_day_chip)
		e_box = _day_rtl(panel, Vector2.ZERO, Vector2(DAY_W, 100.0))
		e_box.mouse_filter = Control.MOUSE_FILTER_STOP
		e_box.meta_underlined = false
		e_box.autowrap_mode = TextServer.AUTOWRAP_OFF
		e_box.meta_clicked.connect(_on_day_chip)
		_day_chips = c_box
		_day_groups = d_box
		_day_exits = e_box
		# R: the day's rule, in one caption line (the second reading: "keep this
		# explainer visible on every turn") — one whole line or not on the table
		var rule_box: RichTextLabel = null
		var rule_h := 0.0
		if offering:
			rule_box = _day_rtl(panel, Vector2.ZERO, Vector2(DAY_W, 40.0))
			rule_box.name = "DayRule"
			rule_box.autowrap_mode = TextServer.AUTOWRAP_OFF
			rule_box.theme_type_variation = &"CaptionRich"     # the ladder's Caption step (no BBCode size)
			rule_box.text = "[color=#%s]%s[/color]" % [Utils.COLOR_INFO, _day_rule()]
			rule_h = rule_box.get_content_height() + 2.0
			rule_box.visible = false
			if rule_box.get_content_width() > DAY_W - 8.0:
				panel.remove_child(rule_box)      # no room for it whole at this text size
				rule_box.queue_free()
				rule_box = null
				hover.append(_day_rule())
		# BA-6 (lever 6): the table's marks, in one caption line — whole or on the head's hover
		var legend_box: RichTextLabel = null
		var legend_h := 0.0
		if offering:
			legend_box = _day_rtl(panel, Vector2.ZERO, Vector2(DAY_W, 40.0))
			legend_box.name = "DayLegend"
			legend_box.autowrap_mode = TextServer.AUTOWRAP_OFF
			legend_box.theme_type_variation = &"CaptionRich"
			legend_box.text = _day_legend_bb()
			legend_h = legend_box.get_content_height() + 2.0
			legend_box.visible = false
			if legend_box.get_content_width() > DAY_W - 8.0:
				panel.remove_child(legend_box)     # no room for it whole at this text size
				legend_box.queue_free()
				legend_box = null
				hover.append(_day_legend_hover())
		# BA-5: what the table CAN say on a word's face (a payload from before
		# the finish carries no `does`: its chips are BA-4's)
		var can_card := false
		for i in split[0]:
			if str((chips_now[int(i)] as Dictionary).get("does", "")) != "":
				can_card = true
		var can_tag := false
		for i in split[2]:
			if str((chips_now[int(i)] as Dictionary).get("does", "")) != "":
				can_tag = true
		# the ladder's state: what still stands on the table
		var give_shelves := false                                   # 1 the shelves give their room
		var inline := false                                         # 2 the groups flow in one paragraph
		var first_row: bool = first_box != null                     # 5 the first day's line
		var rule_row: bool = rule_box != null and not first_row     # 3 the day's rule (the first day's line says it in full)
		var told_row: bool = offering and not lines.is_empty()      # 4 the last word told
		var told_fits := true
		if told_row:
			# BA-6: one row for the line, or none: a line that wraps at a large type rides the head's hover
			var probe := _day_rtl(panel, Vector2.ZERO, Vector2(DAY_W, 100.0))
			probe.text = _day_told(lines, 1)
			if probe.get_content_height() > lh * 1.5:
				told_row = false
				told_fits = false
			panel.remove_child(probe)
			probe.queue_free()
		var exit_cards: bool = offering and can_tag                 # 6 the exits as cards, each with what it does
		var lifted := false                                         # 5b the panel takes DAY_LIFT of the gap under the bars
		var cards: bool = offering and can_card                     # 7 the cards' second lines
		var legend_row: bool = legend_box != null                   # 2b the legend's caption line
		var risk_lines: bool = cards                                # 5c the cards' third line (what the word risks)
		var exits_row := false                                      # the exits' cards full width, above the buttons
		var exits_wrapped := false                                  # ...with their stakes on two lines
		var tail_h := 0.0
		var b_h: float = lh + 2.0
		var c_h := 0.0
		var d_h := 0.0
		var e_h := 0.0
		var e_top_abs := 0.0
		var above := 0.0
		var room := 0.0
		var fits := false
		for _step in range(20):
			_day_cards = cards
			_day_risk_lines = risk_lines and cards
			_day_exit_tags = exit_cards
			_day_exits_row = exit_cards and exits_row
			_day_exits_wrapped = exit_cards and exits_wrapped
			_day_inline = inline
			_day_retext()
			# a rich line's content width is read against a box no narrower than its words (a box of
			# the panel's own width would clip what it measures)
			e_box.size.x = DAY_MEASURE_W
			if c_box != null:
				c_box.size.x = DAY_MEASURE_W
			tail_h = legend_h if legend_row else 0.0
			top = (top_free if give_shelves else top_with) - (DAY_LIFT if lifted else 0.0)
			c_h = c_box.get_content_height() if c_box != null else 0.0
			e_h = e_box.get_content_height()
			# a row wider than its room is no row: its second lines go first
			if cards and c_box != null and c_box.get_content_width() > DAY_W + 1.0:
				if risk_lines:
					risk_lines = false        # the third line goes before the second
				else:
					cards = false
					_day_cards_wide = true    # (the walk reads it: a row wider than its room is no row)
				continue
			if exit_cards:
				var e_w: float = e_box.get_content_width()
				if not exits_row and e_w > DAY_CHIPS_W:
					exits_row = true              # BA-6: beside the buttons they do not fit: the full-width row above them
					_day_exits_row_tried = true
					continue
				if exits_row and e_w > DAY_W - 4.0:
					if not exits_wrapped:
						exits_wrapped = true      # ...then their stakes on two lines
					else:
						exit_cards = false        # ...then the one-line chips
						exits_row = false
						exits_wrapped = false
						_day_exits_wide = true    # (the cards gave way for their width)
					continue
			above = head_h + (first_h if first_row else 0.0) + (rule_h if rule_row else 0.0) \
				+ (b_h if told_row else 0.0) + c_h
			if exit_cards:
				if exits_row:
					e_top_abs = btn_top - 4.0 - e_h              # BA-6: full width, on the row above the buttons
				else:
					e_top_abs = floor_px - DAY_EXIT_FLOOR - e_h  # beside the buttons, down to the tray's floor
			else:
				e_top_abs = minf(btn_mid - e_h / 2.0, floor_px - 3.0 - e_h)   # level with, and centred on, the buttons (never on the floor)
			room = e_top_abs - 2.0 - top
			d_h = 0.0
			if d_box != null:
				d_h = _day_groups_h(d_box, inline, top + above, (e_top_abs if exit_cards else btn_top) - tail_h)
			fits = above + d_h + tail_h <= room
			if fits:
				break
			if shelf_up and not give_shelves:
				give_shelves = true                   # 1
			elif d_box != null and not inline:
				inline = true                         # 2
			elif legend_row and not lifted:
				lifted = true                         # 2a: the lift costs least, and the legend is the first row to go after it
			elif legend_row:
				legend_row = false                    # 2b
			elif rule_row:
				rule_row = false                      # 3
			elif told_row:
				told_row = false                      # 4
			elif first_row:
				first_row = false                     # 5
				# ...and the last word told may have its row back: it gave it up for a line
				# that is not on the table after all (one row for two)
				told_row = offering and not lines.is_empty() and told_fits
			elif not lifted:
				lifted = true                         # 5b
			elif risk_lines and cards:
				risk_lines = false                    # 5c: the third line goes before the second, and before the exits' faces
			elif exit_cards:
				exit_cards = false                    # 6
				exits_row = false
				exits_wrapped = false
			elif cards:
				cards = false                         # 7
			else:
				break
		if not fits and d_box != null:
			# 8. whole text rows or nothing: the groups scroll by rows, never rows C or E
			# (the exits are one-line chips by now: a chip's row is the groups' own)
			var row_h: float = maxf(e_h, lh)
			var left: float = room - above - tail_h
			var unit: float = maxf(row_h, 1.0)
			d_h = maxf(unit, floorf(left / unit) * unit)
			d_box.scroll_active = true
		_day_hide_shelves = give_shelves
		_day_risk_lines = risk_lines and cards
		_day_legend_row = legend_row
		_day_exits_row = exit_cards and exits_row
		_day_exits_wrapped = exit_cards and exits_wrapped
		_day_more_n = _day_hidden_groups().size()
		_day_groups_scrolls = d_box != null and d_box.scroll_active
		_day_exits_up = exit_cards
		_day_rule_row = rule_row
		_day_lifted = lifted
		_day_top_plain = top_free if give_shelves else top_with
		if not exit_cards and can_tag:
			# BA-5: as one-line chips — what an exit does stays on its face as far as
			# the row fits left of Replay, in DAY_TAG_ORDER (the rest ride their hovers)
			for kept in range(DAY_TAG_ORDER.size(), 0, -1):
				_day_tags_kept = kept
				_day_retext()
				if e_box.get_content_width() <= DAY_CHIPS_W:
					break
				_day_tags_kept = 0
			if _day_tags_kept == 0:
				_day_retext()
		if first_box != null:
			# BA-4: the first day's line takes its row wherever the ladder left
			# it one; else it rides the head's hover and is NOT acknowledged — a
			# hover is not a showing (the next table with the room shows it)
			if first_row:
				first_box.visible = true
				first_box.position = Vector2(0.0, y)
				first_box.size.y = first_h
				y += first_h
				_day_first_screen = first_screen
			else:
				panel.remove_child(first_box)
				first_box.queue_free()
				hover.append(first_said)
		if rule_box != null:
			if rule_row:
				rule_box.visible = true
				rule_box.position = Vector2(0.0, y)
				rule_box.size.y = rule_h
				y += rule_h
			else:
				panel.remove_child(rule_box)
				rule_box.queue_free()
				if not first_row:
					hover.append(_day_rule())        # (the first day's line says the rule in full)
		if told_row:
			var told := _day_rtl(panel, Vector2(0.0, y), Vector2(DAY_W, b_h))
			told.text = _day_told(lines, 1)
			y += b_h
		elif not lines.is_empty():
			hover.append(str((lines[lines.size() - 1] as Dictionary).get("line", "")))
		if c_box != null:
			c_box.position = Vector2(0.0, y)
			c_box.size = Vector2(DAY_W, c_h)
			y += c_h
		if d_box != null:
			d_box.position = Vector2(0.0, y)
			d_box.size = Vector2(d_box.size.x, d_h)
			y += d_h
		e_box.position = Vector2(0.0, e_top_abs - top)
		e_box.size = Vector2(DAY_W if (exit_cards and exits_row) else DAY_CHIPS_W, maxf(e_h, 1.0))
		if legend_box != null:
			if legend_row:
				legend_box.visible = true
				legend_box.position = Vector2(0.0, e_top_abs - top - legend_h - 2.0)   # the foot of the words, above the exits
				legend_box.size.y = legend_h
			else:
				panel.remove_child(legend_box)
				legend_box.queue_free()
				hover.append(_day_legend_hover())
		if offering:
			var keys := DayKeys.new()             # BA-4: the bare digits press the chips
			keys.name = "DayKeys"
			keys.acts = self
			panel.add_child(keys)
	panel.position = Vector2(DAY_X, top)
	panel.size = Vector2(DAY_W, floor_px - top)
	if name_label != null:
		# in the band above the baize (its place is the tray's, whatever room the panel took)
		name_label.position = Vector2(0.0, DAY_HEAD_Y - top)
	if not hover.is_empty():
		head.mouse_filter = Control.MOUSE_FILTER_STOP
		head.text = Utils.bb_hint(head.text, " ".join(PackedStringArray(hover)))
	# a result mark: it comes in when the table is FINAL (the skip hint gone,
	# Replay and Close there) — never together with the skip hint
	if host._skip_hint != null and host._skip_hint.visible:
		host._skip_hint.visibility_changed.connect(_on_skip_hint_changed, CONNECT_ONE_SHOT)


func _relay_the_day() -> void:
	"""BA-6: the panel laid again at rest, with `_day_more_open` as pressed - the ladder reads the
	groups' opened text, makes room for it (shedding the lower rungs as it always does) and only
	scrolls where it cannot. What the first laying did to the stage is undone for the measure
	(the shelves it hid stand, the verdict is as populate set it) and done again by the result."""
	if _day_panel == null or not is_instance_valid(_day_panel) or host == null or not is_instance_valid(host):
		return
	var was_shown: bool = _day_panel.visible
	var shelves_were_hidden := _day_hide_shelves
	var shelves: Array = [host._shelf_left, host._shelf_right]
	if shelves_were_hidden:
		for shelf in shelves:
			if shelf != null:
				(shelf as CanvasItem).visible = true
	var lifted_verdict := _shelf_up()
	if lifted_verdict:
		host._verdict.position.y += VERDICT_LIFT     # (`_lift_the_verdict` lent it four; the ladder reads the populate's top)
		host._verdict.size.y -= VERDICT_LIFT
	var old: Control = _day_panel
	host._transients.erase(old)
	if old.get_parent() != null:
		old.get_parent().remove_child(old)
	old.queue_free()
	_relaying = true
	_build_the_day()
	_relaying = false
	_day_first_screen = ""                           # (shown already: the showing was the acknowledgement)
	if lifted_verdict:
		_lift_the_verdict()
	if _day_panel != null and is_instance_valid(_day_panel):
		if _day_hide_shelves:
			for shelf in shelves:
				if shelf != null:
					(shelf as CanvasItem).visible = false
		_day_panel.visible = was_shown


func _on_skip_hint_changed() -> void:
	if host == null or not is_instance_valid(host) or host._acts != self or host._skip_hint.visible:
		return
	if _day_panel == null or not is_instance_valid(_day_panel) or _day_panel.is_queued_for_deletion():
		return
	_show_the_day()


func _on_day_chip(meta) -> void:
	if str(meta) == DAY_MORE_KEY:
		# BA-6: "+N more" is a toggle: every word of the groups in place, or back to the keys' three
		_day_more_open = not _day_more_open
		_relay_the_day()       # the ladder measures the opened words and gives them their room
		return
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
	# BA-5: the word goes out with its own sound (the bugle, the Guard's drums, the spade)
	host._cue(str(DAY_WORD_CUES.get(word if word != "" else str(chip.get("kind", "")), "select")))
	host.word_given.emit(command)


func _sound_the_day() -> void:
	"""BA-5: what the day just told, sounded ONCE - his word that was no clash (the
	spade as he digs in, the march as a corps comes up), the tattoo as night falls,
	the boots of a side leaving the field. A table shown again says nothing twice
	(`_day_sounded` remembers, by enemy, the last thing it sounded)."""
	var day := _the_day()
	var enemy := str(day.get("enemy", ""))
	var told: Array = day.get("told", []) if day.get("told", []) is Array else []
	var last_line := str((told[told.size() - 1] as Dictionary).get("line", "")) if not told.is_empty() else ""
	# BA6-X2: the mark carries the battle's own identity (its turn, ground and name): the
	# SAME table shown again stays silent, a LATER battle against the same enemy sounds
	# (a night's close and its last line are fixed text, and `told` is capped)
	var mark := "%d|%s|%s|%s|%d|%s" % [int(host._data.get("turn", 0)), str(host._data.get("region", "")),
			str(host._data.get("battle_name", "")), str(day.get("ended", "")), told.size(), last_line]
	if enemy == "" or str(_day_sounded.get(enemy, "")) == mark:
		return
	_day_sounded[enemy] = mark
	var ended := str(day.get("ended", ""))
	if ended != "":
		if DAY_END_CUES.has(ended):
			host._cue(str(DAY_END_CUES[ended]))
		return
	for i in range(told.size() - 1, -1, -1):
		var t: Dictionary = told[i]
		if str(t.get("kind", "")) in DAY_SILENT_KINDS:
			continue
		if str(t.get("who", "")) == "theirs" and DAY_HIS_CUES.has(str(t.get("kind", ""))):
			host._cue(str(DAY_HIS_CUES[str(t.get("kind", ""))]))
		return


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
	_sound_the_day()
	if _day_offering():
		# BA-5: the words are the table's business - Close gives up the primary look
		# while they are offered (`_put_the_chrome_back` gives it back at the next table)
		host._btn_close.theme_type_variation = &""
		host._btn_close.add_theme_stylebox_override("normal", host._replay_face(false))
		host._btn_close.add_theme_stylebox_override("hover", host._replay_face(true))
		host._btn_close.add_theme_color_override("font_color", Utils.UI_GOLD)
		host._btn_close.add_theme_color_override("font_hover_color", Utils.UI_GOLD)
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
	_fit_the_verdict()


const VERDICT_LIFT := 4.0      # BA5-D3: of the 8 px between a shelf and the verdict, four are the verdict's
const VERDICT_STEP := &"BodyLargeRich"       # the verdict's own ladder step (the host builds it so)
const VERDICT_STEP_SMALL := &"CaptionRich"   # ...and a step smaller, where it would not stand whole
var _verdict_source := ""      # BA5-D3: the verdict as the table (or a beat) set it: whole, unsized
var _verdict_written := ""     # ...and as `_fit_the_verdict` last wrote it
var _verdict_refits := 0


func _fit_the_verdict() -> void:
	"""BA5-D3: what stands in the verdict's room stands WHOLE. A beat's line read
	"...He brings three-" behind a scrollbar, and at rest Berthier's own two lines
	hid the enemy's answer under them (a shelf is up: the room is two lines). In
	order: as it is; a step smaller; then as many whole paragraphs as the room
	holds - as it is, else a step smaller - with an (i) at their end and every word
	in its hover. One paragraph too long for the room alone scrolls on whole lines,
	as it always did.
	It is measured with every character shaped (the quill has not written them
	yet, and what is not written is not laid out), and from the text it was GIVEN,
	so it can be fitted again when the room is known (`settle`)."""
	var v: RichTextLabel = host._verdict
	if v == null or v.text == "":
		return
	if v.text != _verdict_written:
		_verdict_source = v.text           # set afresh since this last wrote it
	var shown: int = v.visible_characters
	v.visible_characters = -1
	var room: float = v.size.y + 1.0
	v.theme_type_variation = VERDICT_STEP
	v.text = _verdict_source
	var every_word: String = v.get_parsed_text()
	# what is tried, in order — [the label's ladder step, the text]; the last stands if nothing fits
	# (and scrolls). A step smaller is the theme's Caption step of the label, never a BBCode size.
	var tries: Array = [[VERDICT_STEP, _verdict_source], [VERDICT_STEP_SMALL, _verdict_source]]
	var parts: PackedStringArray = _verdict_source.split("\n")
	for step in [VERDICT_STEP, VERDICT_STEP_SMALL]:
		for keep in range(parts.size() - 1, 0, -1):
			var kept: String = "\n".join(parts.slice(0, keep))
			tries.append([step, Utils.bb_hint(_with_more(kept), every_word)])
	var pick: Array = tries[tries.size() - 1]
	for candidate in tries:
		v.theme_type_variation = candidate[0]
		v.text = candidate[1]
		if v.get_content_height() <= room:
			pick = candidate
			break
	v.theme_type_variation = pick[0]
	v.text = pick[1]
	v.hint_underlined = false         # the (i) says there is more; no dotted line under Berthier
	_verdict_written = pick[1]
	v.visible_characters = shown


func _lift_the_verdict() -> void:
	"""BA5-D3: under a shelf the verdict's room is 51 px, and two lines of Berthier
	are 54: every two-line verdict of a table with a reserve stood behind a
	scrollbar. Four of the eight pixels between the shelf and the verdict are lent
	to it (the host sets the verdict's top afresh at every populate, and measures
	its room from that top once the plate is placed)."""
	if _shelf_up():
		host._verdict.position.y -= VERDICT_LIFT
		host._verdict.size.y += VERDICT_LIFT


func _with_more(bb: String) -> String:
	"""`bb` with the (i) that says there is more, inside its own closing tags (so it
	stands at the end of the last line kept, not on a line of its own)."""
	var mark: String = " " + Utils.bb_info_glyph(16)
	var closers := RegEx.create_from_string("(\\[/[a-z_]+\\])+$")
	var found := closers.search(bb)
	if found == null:
		return bb + mark
	return bb.substr(0, found.get_start()) + mark + bb.substr(found.get_start())


func _refit_the_verdict() -> void:
	"""The plate is measured a frame after the table is laid, and the verdict's room
	ends above the plate: a settled table fits its verdict again once the room is
	known (two frames: the host's own measure waits one)."""
	if host == null or not is_instance_valid(host) or host._acts != self or not host.is_inside_tree():
		return
	_fit_the_verdict()
	_verdict_refits -= 1
	if _verdict_refits > 0:
		host.get_tree().process_frame.connect(_refit_the_verdict, CONNECT_ONE_SHOT)


func _tell_the_reserves_dead() -> void:
	for tail in _reserve_tails:
		if is_instance_valid(tail["label"]):
			(tail["label"] as Label).text = str(tail["full"])
	# BA6-X10: the laurels come now - a note one of them would stand on says it shortly
	var sw: float = host._stage.size.x
	for note in _reserve_short_at_end:
		var label: Label = note["label"]
		if not is_instance_valid(label):
			continue
		label.text = str(note["short"])
		label.size = label.get_minimum_size()
		label.position.x = float(note["edge"]) if bool(note["left"]) \
				else sw - float(note["edge"]) - label.size.x
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
	# BA6-X10: where a triumph's laurels will flank its banner at the end, the stage x each
	# takes (the host's `_laurel_layout`, measured on the register's own banner words)
	var laurel_l := -1.0
	var laurel_r := -1.0
	var register := str(host._data.get("register", "observer"))
	if register == "triumph" and host._laurel_l != null:
		var shown_banner: String = host._banner.text
		host._banner.text = host._banner_text(register)
		var words: float = host._banner.get_minimum_size().x
		host._banner.text = shown_banner
		laurel_l = sw / 2.0 - words / 2.0 - host.LAUREL_GAP - host.LAUREL_PX
		laurel_r = sw / 2.0 + words / 2.0 + host.LAUREL_GAP + host.LAUREL_PX
	_reserve_short_at_end = []
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
		# BA6-X10 (the blind reading, both readers): the note keeps its noun - "+3 in reserve"
		# beside the LOSSES counter was read as a count of men
		tail.text = full.substr(0, cut) if cut >= 0 else full
		tail.size = tail.get_minimum_size()
		tail.position = Vector2(edge if left else sw - edge - tail.size.x, RESERVE_NOTE_Y)
		# BA6-X10: the note keeps its noun while the battle is told; a triumph's laurel that would
		# stand on it at the end takes it back to "+3 in reserve" as the laurels come
		var crowded := (laurel_l >= 0.0 and edge + tail.size.x + 4.0 > laurel_l) if left \
				else (laurel_r >= 0.0 and sw - edge - tail.size.x - 4.0 < laurel_r)
		if crowded:
			_reserve_short_at_end.append({"label": tail, "left": left, "edge": edge,
					"short": tail.text.replace(" corps in reserve", " in reserve")})
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
	"""Each side's fortune of the day, by the side it stands on the table — said
	for what it is (the second reading took it for the luck of the THROW and found
	its sign against the dice): the chance each line's strength drew, apart from
	the throw (`combat._fortune_pct`)."""
	var sides: Array = host._side_payloads()
	var left_key: String = "fortune_attacker" if _attacker_left() else "fortune_defender"
	var right_key: String = "fortune_defender" if _attacker_left() else "fortune_attacker"
	var told := _what_told()
	if told != "":
		# BA-6 (lever 5): the luck set against the margin, in one phrase — what told, then what the dice
		# added to the blow (the lands figure the row above shows, against the average throw's 102 %) and
		# what the day's fortune added to US (our side's own figure, signed)
		var dice_pct: int = int(roll.get("swing", 0)) + 100 - DiceTray.AVERAGE_LANDS
		return "%s; the dice added %s to the blow, the day's fortune %s to us" % [
			told, _signed(dice_pct), _signed(int(roll.get(left_key, 0)))]
	var luck_head := "the day's fortune in strength:"
	if host != null and BattleActs.payload_is_plain(host._data):
		luck_head = "luck today, as extra strength:"   # row PW
	return "%s  %s %s  ·  %s %s" % [luck_head,
		Utils.display_nation_name(str(sides[0].get("nation", ""))), _signed(int(roll.get(left_key, 0))),
		Utils.display_nation_name(str(sides[1].get("nation", ""))), _signed(int(roll.get(right_key, 0)))]


func _luck_short(roll: Dictionary) -> String:
	"""BA-6 (the client review's C12, ruled): the luck's phrase without what told — the dice's
	share of the blow and the day's fortune to us — for a plate whose room holds two rows only
	(Text size 120 % and up), where it takes the lands row's place: no wider than that row, and
	what told stands on the verdict's own line. "" where nothing told (the lands row stays)."""
	if _what_told() == "":
		return ""
	var left_key: String = "fortune_attacker" if _attacker_left() else "fortune_defender"
	var dice_pct: int = int(roll.get("swing", 0)) + 100 - DiceTray.AVERAGE_LANDS
	return "the dice added %s to the blow, the day's fortune %s to us" % [
		_signed(dice_pct), _signed(int(roll.get(left_key, 0)))]


func _what_told() -> String:
	"""BA-6: what told, as the payload says it ("Our weight of numbers told." / "Decided at the
	second clash, when Mack's line broke: our weight of numbers told."), the cause alone,
	capitalised and with no full stop — or "" where the payload says none."""
	var line: String = str(host._data.get("verdict_told", ""))
	if line == "" or line == "<null>":
		var d := _the_day()
		line = str(d.get("verdict_told", "")) if not d.is_empty() else ""
	line = line.strip_edges()
	if line == "" or line == "<null>":
		return ""
	if line.begins_with("Decided") and line.contains(": "):
		line = line.substr(line.rfind(": ") + 2)
	elif line.begins_with("Decided") and line.trim_suffix(".").ends_with(", in an even fight"):
		line = "An even fight"             # (no cause was named: the fight itself is the cause)
	if line.ends_with("."):
		line = line.substr(0, line.length() - 1)
	return line.substr(0, 1).to_upper() + line.substr(1)


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
			_band_hold_unseen(b)
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
	_band_all_made_out()
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
	_fit_the_verdict()
	if host.is_inside_tree() and _verdict_refits <= 0:      # BA5-D3: again, when the room is known
		_verdict_refits = 2
		host.get_tree().process_frame.connect(_refit_the_verdict, CONNECT_ONE_SHOT)
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
	if _kind() == "bombardment":
		# (the second reading: "3,470 fall" stood over a counter at 876 — the count ran
		# the whole act) a cannonade's toll is counted as its battery fires
		span = 1.2
	host._schedule_topples(fight_from, span)
	host._animate_odometers(fight_from, span + 0.4)
	_count_the_guns(fight_from, span + 0.4)
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


const GUNS_COUNT_AFTER := 0.15     # the battery fires, then its toll is counted
const GUNS_COUNT_S := 0.6


func _count_the_guns(start: float, span: float) -> void:
	"""The second reading: "3,152 fall before the assault" stood under two counters at
	0 — the host's count runs 0 to the day's total over the FIGHT — and a cannonade's
	own table read "3,470 fall" over a counter at 876. What a battery takes (the
	beat's `dealt`) and what it costs (`taken`) are counted as it fires; the fight's
	count then goes on from there and never under it (a second writer on the master
	sequence, added after the host's: it holds the guns' toll until the count passes
	it, and ends on the same total)."""
	if _kind() == "bombardment":
		return                                  # its own count runs with its battery (`play`)
	var sides: Array = host._side_payloads()
	var banded: bool = host._band != null and host._band.visible \
			and host._band_rows.size() >= 2 and host._band_figs.size() >= 2
	var held := {true: 0, false: 0}          # by "the LEFT counter": what the guns have counted
	var last_at := -1.0
	for row in _played:
		var beat: Dictionary = row["beat"]
		if str(row["act"]) != "cannonade" or str(beat.get("kind", "")) != "battery":
			continue
		var at: float = float(row.get("at", -1.0))
		if at < 0.0:
			continue
		# the battery's target stands across the table from the side that fires
		var target_left: bool = (str(beat.get("side", "")) == "attacker") != _attacker_left()
		for item in [[target_left, int(beat.get("dealt", 0))], [not target_left, int(beat.get("taken", 0))]]:
			var is_left: bool = item[0]
			var total: int = int((sides[0 if is_left else 1] as Dictionary).get("casualties_total", 0))
			var counted: int = int(held[is_left])
			var to: int = mini(counted + int(item[1]), total)
			if to <= counted:
				continue
			held[is_left] = to
			host._seq.parallel().tween_method(
					_odo_at.bind(host._odo_left if is_left else host._odo_right, 0),
					float(counted), float(to), GUNS_COUNT_S).set_delay(at + GUNS_COUNT_AFTER)
			if banded:
				# ...and the band's own figure of that side, with it
				var i: int = 0 if is_left else 1
				host._seq.parallel().tween_method(
						_band_at.bind(i, int((host._band_rows[i] as Dictionary).get("before", 0))),
						float(counted), float(to), GUNS_COUNT_S).set_delay(at + GUNS_COUNT_AFTER)
		last_at = maxf(last_at, at)
	if last_at < 0.0:
		return
	for is_left in [true, false]:
		if int(held[is_left]) <= 0:
			continue
		var total: int = int((sides[0 if is_left else 1] as Dictionary).get("casualties_total", 0))
		host._seq.parallel().tween_method(
				_odo_at.bind(host._odo_left if is_left else host._odo_right, int(held[is_left])),
				0.0, float(total), span) \
			.set_delay(maxf(start, last_at + GUNS_COUNT_AFTER + GUNS_COUNT_S)) \
			.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	if banded:
		# the host's band runs both figures on ONE progress, from the muster: after it has
		# written them, each frame of the fight's count, neither reads more men than the guns left
		var caps: Array = [
			int((host._band_rows[0] as Dictionary).get("before", 0)) - int(held[true]),
			int((host._band_rows[1] as Dictionary).get("before", 0)) - int(held[false])]
		host._seq.parallel().tween_method(_band_never_above.bind(caps), 0.0, 1.0, span).set_delay(start)


func _odo_at(v: float, odo: Label, never_under: int) -> void:
	if is_instance_valid(odo):
		odo.text = Utils.format_number(maxi(int(v), never_under))


func _band_at(v: float, i: int, before: int) -> void:
	"""The band's figure of one side while the guns' toll is counted: what it mustered,
	and that less `v` (the host's own words: `_band_fig_text`)."""
	if i < host._band_figs.size() and is_instance_valid(host._band_figs[i]):
		var seen: int = before - int(_band_unseen_of(i))    # BA5-X15: only the corps made out
		(host._band_figs[i] as Label).text = "%s → %s" % [
				Utils.format_number(seen), Utils.format_number(seen - int(v))]


func _band_never_above(_v: float, caps: Array) -> void:
	for i in range(mini(2, host._band_figs.size())):
		var fig: Label = host._band_figs[i]
		if not is_instance_valid(fig):
			continue
		var cut: int = fig.text.rfind(" → ")
		if cut >= 0 and fig.text.substr(cut + 3).to_int() > int(caps[i]):
			fig.text = fig.text.substr(0, cut + 3) + Utils.format_number(int(caps[i]))


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
		# (the second reading: mid-count a corps' line and the band beside it read two
		# figures — "2,993" and "2,988") the line runs on the band's own curve
		tw.tween_method(_strength_at.bind(line, str(b.get("strength_brought", "")),
				maxi(int(c.get("committed", 0)), 1), int(c.get("remaining", 0))), 0.0, 1.0, span) \
			.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
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
		_fit_the_verdict()                 # BA5-D3: whole, a step smaller, before it is cut

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
				if captioned:
					# BA5-D6: the throw is read when the dice have landed - its sentence
					# ("Ney rolls 10 ...: 11") named the roll while they still tumbled
					host._verdict.visible_characters = 0
					_dice.landed.connect(_read_the_throw.bind(host._verdict.text), CONNECT_ONE_SHOT)
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


func _read_the_throw(said: String) -> void:
	"""BA5-D6: the dice have landed - the sentence that names the throw is read
	(if the table still holds it: a skip or the gavel may have moved on)."""
	if host != null and is_instance_valid(host) and host._verdict.text == said:
		host._verdict.visible_characters = -1


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
	if float(b.get("band_unseen", 0.0)) > 0.0:
		# BA5-X15: his men join the band as he is made out, over the reveal's own time
		tw.parallel().tween_method(_band_unseen_step.bind(b), 1.0, 0.0, 0.35)
	tw.parallel().tween_property(b["locket"], "modulate:a", 1.0, 0.35)
	for child in b.get("unseen_labels", []):
		if not is_instance_valid(child):
			continue
		(child as Label).modulate.a = 0.0
		tw.parallel().tween_callback((child as Label).set_visible.bind(true))
		tw.parallel().tween_property(child, "modulate:a", 1.0, 0.35)
	b["unseen_labels"] = []


func _band_side(b: Dictionary) -> int:
	return 0 if bool(b["is_left"]) else 1


func _band_hold_unseen(b: Dictionary) -> void:
	"""BA5-X15: a corps that comes up unseen is not yet in the band's figure of his
	side - his committed men are held back until `_reveal`."""
	var men := float(int((b["data"] as Dictionary).get("committed", 0)))
	if men <= 0.0 or float(b.get("band_unseen", 0.0)) > 0.0:
		return
	b["band_unseen"] = men
	b["band_unseen_now"] = men
	host.set_band_unseen(_band_side(b), _band_unseen_of(_band_side(b)) + men)


func _band_unseen_of(i: int) -> float:
	if i < 0 or i >= host._band_rows.size():
		return 0.0
	return float((host._band_rows[i] as Dictionary).get("unseen", 0))


func _band_unseen_step(v: float, b: Dictionary) -> void:
	"""v runs 1 -> 0: this corps' share of the side's unseen men shrinks with it."""
	if host == null or not is_instance_valid(host):
		return
	var now: float = float(b.get("band_unseen", 0.0)) * v
	var delta: float = now - float(b.get("band_unseen_now", 0.0))
	b["band_unseen_now"] = now
	var i := _band_side(b)
	host.set_band_unseen(i, maxf(_band_unseen_of(i) + delta, 0.0))
	if v <= 0.0:
		b["band_unseen"] = 0.0


func _band_all_made_out() -> void:
	"""A settled frame / a skip: every corps is made out, whatever the tweens did."""
	for name in _blocks:
		var b: Dictionary = _blocks[name]
		b["band_unseen"] = 0.0
		b["band_unseen_now"] = 0.0
	if host != null and is_instance_valid(host):
		for i in range(mini(2, host._band_rows.size())):
			host.set_band_unseen(i, 0.0)


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
	const LUCK_ROW_MAX_EXTRA := 3.0     # BA-6: the Caption line's extra the luck's row is printed to. The tableau's type is held at 130 % (about +2), so
	# the branches that read it are the guard for a future TABLEAU_TEXT_CAP above 1.3 (150 % would be +4): unreachable today

	static func room_h(diorama) -> float:
		"""BA1-X4: the room the three rows need grows with the Caption line - the shipped
		106 at the sizes it has always served (100 %, 115 %), the die and three lines
		and their gaps above that - so the luck line is not the one left off."""
		return diorama.dice_room_h()
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
	var _rows: Array = []          # BA5-D6: the tray's lines, read when the dice have landed
	var _plate := Rect2()          # ...and the dark plate they are read on (the tray's own space)
	var _plate_on := false
	const PLATE := Color(0.05, 0.08, 0.06, 0.80)
	signal landed
	const AVERAGE_LANDS := 102     # what an average throw (7) gives: 85 % + 2.5 a pip

	func build(diorama, roll: Dictionary, luck_line: String, luck_short: String = "") -> void:
		"""Call AFTER the tray is in the tree: the rows are placed by the
		heights the theme gives them."""
		mouse_filter = Control.MOUSE_FILTER_IGNORE
		var natural: int = clampi(int(roll.get("natural", 2)), 2, 12)
		var modified: int = int(roll.get("modified", natural))
		_a = clampi(int(ceil(natural / 2.0)), 1, 6)
		_b = clampi(natural - _a, 1, 6)
		_shown_a = _a
		_shown_b = _b
		# (the second reading: "= 10" stood beside dice that show eight pips) what was
		# added to the throw stands with the sum: "+2 = 10"
		_sum_text = ("%+d = %d" % [modified - natural, modified]) if modified != natural \
				else ("= %d" % modified)
		_sum = diorama._mk_label(self, _sum_text, &"Lead", BattleActs.GOLD, diorama._font_engraved)
		diorama._outline_over_colours(_sum)
		var sum_size: Vector2 = _sum.get_minimum_size()
		var row_w: float = DIE * 2.0 + 8.0 + 10.0 + sum_size.x
		_dice_x = (TRAY_W - row_w) / 2.0
		_sum.position = Vector2(_dice_x + DIE * 2.0 + 18.0, (DIE - sum_size.y) / 2.0)

		# BA-5: one vocabulary - what was thrown and what was added make the
		# figure beside the dice; the blow it gives stands against an average throw's
		# ...and whose throw it is (the attacker's: the server names him on the beat)
		var thrower: String = Utils.display_marshal_name(str(roll.get("actor", "")))
		var plain: bool = BattleActs.payload_is_plain(diorama._data)
		var bits: Array = [("%s throws %d" % [thrower, natural]) if thrower != "" else ("thrown %d" % natural)]
		if plain:
			# Row PW (plain words): "X rolled 7", then what the roll did
			bits = [("%s rolled %d" % [thrower, natural]) if thrower != "" else ("rolled %d" % natural)]
		if int(roll.get("skill", 0)) != 0:
			bits.append("%+d skill" % int(roll.get("skill", 0)))
		if int(roll.get("flank", 0)) != 0:
			bits.append("%+d flank" % int(roll.get("flank", 0)))
		var thrown: String = ", ".join(PackedStringArray(bits))
		if modified != natural:
			thrown += " = %d" % modified
		var crit: String = str(roll.get("critical", ""))
		var crit_word := "a twelve: " if crit == "success" else ("a two: " if crit == "failure" else "")
		var lands := "the blow lands at %d%% of its weight · an average throw: %d%%" % [
				100 + int(roll.get("swing", 0)), AVERAGE_LANDS]
		if plain:
			lands = "the attack hits at %d%% strength · an average roll gives %d%%" % [
				100 + int(roll.get("swing", 0)), AVERAGE_LANDS]
		if diorama._line_extra() > LUCK_ROW_MAX_EXTRA:
			# BA-6 (a guard: unreachable while the type is held at 130 %): were the cap raised past 1.3 the line
			# would be as wide as the gap between the two leads' names: the short form
			lands = "lands at %d%% · an average throw: %d%%" % [100 + int(roll.get("swing", 0)), AVERAGE_LANDS]
		if crit == "success":
			lands = "a twelve: " + lands
		elif crit == "failure":
			lands = "a two: " + lands
		var y: float = DIE + 5.0
		_rows = []
		var texts: Array = [thrown, lands]
		if diorama._line_extra() <= LUCK_ROW_MAX_EXTRA:
			texts.append(luck_line)          # BA-6: the luck's phrase is wide: past a held 130 % (a guard) it would lie on the leads' names
		for text in texts:
			var row: Label = diorama._mk_label(self, str(text), &"Caption", BattleActs.BONE)
			diorama._outline_over_colours(row)
			var row_size: Vector2 = row.get_minimum_size()
			if y + row_size.y > room_h(diorama):
				row.queue_free()
				break
			row.size = row_size
			row.position = Vector2((TRAY_W - row_size.x) / 2.0, y)
			_rows.append(row)
			y += row_size.y + 1.0
		# BA-6 (the client review's C12, ruled): where the room holds two rows only (Text size
		# 120 % and up the third no longer fits, and the long phrase is too wide for the leads'
		# names), the luck set against the margin is the readers' lever 5 - it takes the second
		# row in its short form, no wider than the lands row it replaces (what told stands on
		# the verdict's own line)
		if _rows.size() == 2 and texts.size() == 3 and luck_short != "":
			var second: Label = _rows[1]
			second.text = crit_word + luck_short
			second.size = second.get_minimum_size()
			second.position.x = (TRAY_W - second.size.x) / 2.0
		elif _rows.size() == 2 and texts.size() == 2 and luck_short != "":
			# (the guard's branch, past a held 130 %: the long phrase was never offered)
			var second2: Label = _rows[1]
			second2.text = crit_word + luck_short
			second2.size = second2.get_minimum_size()
			second2.position.x = (TRAY_W - second2.size.x) / 2.0
		# (the second reading: the table's dashed centre line ran through these lines)
		# a dark plate behind the rows, as wide as the widest of them
		_plate = Rect2()
		for row in _rows:
			var r := Rect2((row as Label).position, (row as Label).size)
			_plate = r if _plate.size == Vector2.ZERO else _plate.merge(r)
		if _plate.size != Vector2.ZERO:
			_plate = _plate.grow_individual(8.0, 1.0, 8.0, 2.0)
		_plate_on = true
		size = Vector2(TRAY_W, y)
		custom_minimum_size = size
		queue_redraw()

	func settle() -> void:
		_shown_a = _a
		_shown_b = _b
		if _sum != null:
			_sum.text = _sum_text
		for row in _rows:                # BA5-D6: the lines are read now
			if is_instance_valid(row):
				(row as CanvasItem).visible = true
		_plate_on = true
		queue_redraw()
		landed.emit()

	func roll() -> void:
		"""The dice tumble and come to rest on what was rolled."""
		if _sum != null:
			_sum.text = ""
		for row in _rows:                # BA5-D6: nothing of the throw is told while it tumbles
			if is_instance_valid(row):
				(row as CanvasItem).visible = false
		_plate_on = false
		var tw: Tween = create_tween()
		tw.tween_method(_tumble, 0.0, 9.0, 0.6)
		tw.tween_callback(settle)

	func _tumble(step: float) -> void:
		var i: int = int(step)
		_shown_a = (i * 5 + _a) % 6 + 1
		_shown_b = (i * 3 + _b + 2) % 6 + 1
		queue_redraw()

	func _draw() -> void:
		if _plate_on and _plate.size != Vector2.ZERO:
			draw_rect(_plate, PLATE)
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
