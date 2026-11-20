extends RefCounted
class_name MarshalState

# =============================================================================
# PROJECT SOVEREIGN - One reading of a marshal (Session UI-6, November 13, 2026)
# =============================================================================
# The Generals screen's roster, the war room's selection card and the command
# desk's marshal row all ask THIS what a marshal is doing and what he may be
# ordered to do, so the three can never disagree.
#
# It reads two shapes and turns each into one VIEW (a plain Dictionary):
#   * `from_overview(card)` - a card of GET /marshal_overview (the Generals);
#   * `from_board(entry, row)` - his entry on the map (`map_data[region]
#     .marshals[]`, which carries `tactical_state`) and his roster row
#     (`game_state.marshals[name]`: strength, morale, location).
# Then `status_of(view)` says what he is doing, and `order_specs(view)` lays
# out the seven fixed order slots (the selection card's digits 1-7).
#
# It judges no rule. "Idle" is `main._idle_marshals()`'s own test - no
# standing order, no works, no drill, no square; a broken or retreating corps
# with no order is idle by that test and wears his worse state as his badge.
# Every price and every refusal is the backend's (`state_probe.order_prices` /
# `order_refusals`, on both payloads). Numbers are int(); nothing here returns
# `a or b` (GDScript's `or` answers a bool, never an operand).
#
# Consumers load it by path (`preload("res://scripts/marshal_state.gd")`) or by
# its class name once Godot's `--import` has registered it.
# =============================================================================

const PORTRAIT_DIR := "res://assets/portraits/"
const PORTRAIT_EXTS := [".jpg", ".png", ".jpeg", ".webp"]

## The seven fixed order slots, in their digit order. A slot never moves: a
## verb the marshal may not take stays in its place, locked, its reason the
## hover - so a digit always means the same order. Slot 2 wears Unfortify
## while he is fortified. Slot 7 cancels his standing order (the arrow card's
## own road, POST /cancel_order); it is locked while he has none.
const SLOTS := [
	# (row IC, Session 2: on the general's card the Hold slot reads "Hold the
	# ground" beside the one-action "Stand here" — `card_label`; every other
	# surface keeps "Hold")
	{"slot": 1, "verb": "hold", "label": "Hold", "glyph": "defense", "card_label": "Hold the ground"},
	{"slot": 2, "verb": "fortify", "label": "Fortify", "glyph": "garrison",
		"alt_verb": "unfortify", "alt_label": "Unfortify"},
	{"slot": 3, "verb": "drill", "label": "Drill", "glyph": "drum"},
	{"slot": 4, "verb": "scout", "label": "Scout", "glyph": "intel"},
	{"slot": 5, "verb": "retreat", "label": "Fall back", "glyph": "march"},
	{"slot": 6, "verb": "garrison", "label": "Garrison", "glyph": "garrison"},
	{"slot": 7, "verb": "cancel", "label": "Cancel order", "glyph": "turn"},
]
const NO_STANDING_ORDER := "no standing order to cancel"

## Standing-order types (the strategic executor's) -> the status key.
const _ORDER_KEYS := {
	"MOVE_TO": "marching",
	"PURSUE": "pursuing",
	"HOLD": "holding",
	"SUPPORT": "supporting",
}

static var _portrait_paths: Dictionary = {}   # name -> path or "" (probe once; path strings, no Resource)


# ---------------------------------------------------------------- the views

static func from_overview(card: Dictionary) -> Dictionary:
	"""A /marshal_overview card as a view."""
	var order_type := ""
	var order_target := ""
	var so = card.get("strategic_order", null)
	if so is Dictionary:
		order_type = str(so.get("command_type", ""))
		order_target = str(so.get("target", ""))
	return {
		"name": str(card.get("name", "")),
		"captured": bool(card.get("captured", false)),
		"petition": bool(card.get("seeks_audience", false)),
		"sovereign": bool(card.get("sovereign", false)),
		"broken": bool(card.get("is_broken", false)),
		"retreating": bool(card.get("is_retreating", false)),
		"order_type": order_type,
		"order_target": order_target,
		"fortified": bool(card.get("is_fortified", false)),
		# the card folds drilling_locked into is_drilling
		"drilling": bool(card.get("is_drilling", false)),
		"square": bool(card.get("square_formation", false)),
		"strength": int(card.get("strength", 0)),
		"location": str(card.get("location", "")),
		"prices": _dict_of(card.get("order_prices", {})),
		"refusals": _dict_of(card.get("order_refusals", {})),
	}


static func from_board(entry: Dictionary, row: Dictionary = {}) -> Dictionary:
	"""His map entry (with `tactical_state`) and his roster row as a view.
	Either may be empty - a prisoner or a marshal on administrative duty has
	no map entry; the view then reads what the row carries."""
	var ts = entry.get("tactical_state", {})
	if not (ts is Dictionary):
		ts = {}
	var order_type := str(ts.get("strategic_command_type", ""))
	if order_type == "" and bool(ts.get("in_strategic_mode", false)):
		order_type = "MOVE_TO"
	var strength := int(row.get("strength", entry.get("strength", 0)))
	var location := str(entry.get("location", row.get("location", "")))
	return {
		"name": str(entry.get("name", row.get("name", ""))),
		"captured": bool(row.get("captured", false)),
		"petition": false,
		"sovereign": bool(row.get("sovereign", false)),
		"broken": bool(ts.get("broken", false)),
		"retreating": bool(ts.get("retreating", false)),
		"order_type": order_type,
		"order_target": str(ts.get("strategic_target", "")),
		"fortified": bool(ts.get("fortified", false)),
		"drilling": bool(ts.get("drilling", false)) or bool(ts.get("drilling_locked", false)),
		"square": bool(ts.get("square_formation", false)),
		"strength": strength,
		"location": location,
		"prices": _dict_of(ts.get("order_prices", {})),
		"refusals": _dict_of(ts.get("order_refusals", {})),
		# Row IC, Session 2 (IC-7): the simple orders that are no screen verb
		# (a posture, the square, "stay put") with the game's own prices and
		# refusals; his posture; and whether he was told to stay put this turn.
		"buttons": _dict_of(ts.get("buttons", {})),
		"stance": str(ts.get("stance", "")),
		"stay_put": bool(ts.get("stay_put", false)),
	}


# ---------------------------------------------------------------- the status

static func is_idle(view: Dictionary) -> bool:
	"""`main._idle_marshals()`'s test: no standing order, no works, no drill,
	no square (a prisoner is never idle - he is not in the field)."""
	if bool(view.get("captured", false)):
		return false
	if str(view.get("order_type", "")) != "":
		return false
	if bool(view.get("fortified", false)) or bool(view.get("drilling", false)):
		return false
	# Row IC, Session 2 (IC-7): told to "stay put" this turn - not idle today.
	if bool(view.get("stay_put", false)):
		return false
	return not bool(view.get("square", false))


static func has_standing_order(view: Dictionary) -> bool:
	return str(view.get("order_type", "")) != ""


static func status_of(view: Dictionary) -> Dictionary:
	"""What he is doing, as one badge: {key, label, detail, tone, glyph, idle}.
	`key` is idle | marching | pursuing | holding | supporting | fortified |
	drilling | square | broken | retreating | prisoner | petition; `label` the
	short word for a badge, `detail` the line with its object ("Marching to
	Vienna"); `tone` a Utils colour (hex, no '#'); `glyph` a stat glyph name
	for Utils.glyph() ("" for idle - the consumer draws the gilt dot)."""
	var idle := is_idle(view)
	var target := Utils.humanize_entity_name(str(view.get("order_target", "")))
	var order_type := str(view.get("order_type", ""))
	if bool(view.get("captured", false)):
		return _badge("prisoner", "Prisoner", "Held prisoner", Utils.COLOR_ERROR, "war", false)
	if bool(view.get("petition", false)):
		return _badge("petition", "Petition", "Seeks an audience", Utils.COLOR_WARNING, "letter", idle)
	if bool(view.get("broken", false)):
		return _badge("broken", "Broken", "Broken - rallying", Utils.COLOR_WARNING, "morale", idle)
	if bool(view.get("retreating", false)):
		return _badge("retreating", "Retreating", "Falling back", Utils.COLOR_WARNING, "morale", idle)
	if order_type != "":
		var key := str(_ORDER_KEYS.get(order_type, "marching"))
		match key:
			"pursuing":
				return _badge(key, "Pursuing", _join("Pursuing", target), Utils.COLOR_COMMAND, "march", false)
			"holding":
				return _badge(key, "Holding", _join("Holding", target), Utils.COLOR_COMMAND, "defense", false)
			"supporting":
				return _badge(key, "Supporting", _join("Supporting", target), Utils.COLOR_COMMAND, "march", false)
			_:
				return _badge("marching", "Marching", _join("Marching to", target), Utils.COLOR_COMMAND, "march", false)
	if bool(view.get("fortified", false)):
		return _badge("fortified", "Fortified", "Fortified", Utils.COLOR_SUCCESS, "garrison", false)
	if bool(view.get("drilling", false)):
		return _badge("drilling", "Drilling", "Drilling", Utils.COLOR_SUCCESS, "drum", false)
	if bool(view.get("square", false)):
		return _badge("square", "Square", "Formed in square", Utils.COLOR_SUCCESS, "defense", false)
	return _badge("idle", "Idle", "Idle - awaiting orders", Utils.COLOR_GOLD, "", true)


# ---------------------------------------------------------------- the orders

static func order_specs(view: Dictionary) -> Array:
	"""The seven fixed slots as specs: {slot, verb, label, glyph, price, locked,
	reason}. `price` is the executor's figure in military actions (-1 when the
	payload names none - the button then shows no price); `reason` is the
	short refusal (always a String, "" when the order stands). A verb the
	payload neither prices nor refuses is locked with no reason - the marshal
	is not ours to order (a prisoner, a foreign corps)."""
	var prices: Dictionary = _dict_of(view.get("prices", {}))
	var refusals: Dictionary = _dict_of(view.get("refusals", {}))
	var fortified := bool(view.get("fortified", false))
	var captured := bool(view.get("captured", false))
	var out: Array = []
	for slot in SLOTS:
		var verb := str(slot["verb"])
		var label := str(slot["label"])
		if verb == "fortify" and fortified:
			verb = str(slot["alt_verb"])
			label = str(slot["alt_label"])
		var price := -1
		var reason := ""
		var locked := false
		if verb == "cancel":
			if not has_standing_order(view):
				locked = true
				reason = NO_STANDING_ORDER
			else:
				price = int(prices.get("cancel", 1))
		else:
			if prices.has(verb):
				price = int(prices[verb])
			if refusals.has(verb):
				locked = true
				reason = str(refusals[verb])
			elif not prices.has(verb):
				locked = true
		if captured:
			locked = true
		out.append({
			"slot": int(slot["slot"]),
			"card_label": str(slot.get("card_label", label)),
			"verb": verb,
			"label": label,
			"glyph": str(slot["glyph"]),
			"price": price,
			"locked": locked,
			"reason": reason,
		})
	return out


static func spec_for_slot(view: Dictionary, slot: int) -> Dictionary:
	"""The spec in slot `slot` (1-7), or {} for a digit that names none."""
	for spec in order_specs(view):
		if int(spec["slot"]) == slot:
			return spec
	return {}


static func price_text(price: int) -> String:
	"""A price as it reads on a button face: "" (none named), "free", "1", "2"."""
	if price < 0:
		return ""
	if price == 0:
		return "free"
	return str(price)


# ---------------------------------------------------------------- the portrait

static func portrait_path(name: String) -> String:
	"""His public-domain likeness, or "" (a monogram is the consumer's), cached
	so a roster does not probe ResourceLoader on every redraw. `name` is the
	backend key ("Ney", "Napoleon", "ArchdukeCharles")."""
	if _portrait_paths.has(name):
		return str(_portrait_paths[name])
	var found := ""
	for ext in PORTRAIT_EXTS:
		var p: String = PORTRAIT_DIR + name + ext
		if ResourceLoader.exists(p):
			found = p
			break
	_portrait_paths[name] = found
	return found


static func monogram(name: String) -> String:
	"""The initial a missing likeness wears."""
	var shown := Utils.humanize_entity_name(name)
	return shown.substr(0, 1).to_upper() if shown.length() > 0 else "?"


# ---------------------------------------------------------------- helpers

static func _badge(key: String, label: String, detail: String, tone: String, glyph: String,
		idle: bool) -> Dictionary:
	return {"key": key, "label": label, "detail": detail, "tone": tone, "glyph": glyph, "idle": idle}


static func _join(head: String, target: String) -> String:
	return head + " " + target if target != "" else head


static func _dict_of(value) -> Dictionary:
	return value if value is Dictionary else {}
