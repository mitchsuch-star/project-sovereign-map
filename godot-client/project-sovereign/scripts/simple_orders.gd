# =============================================================================
# Row IC, Session 2 (IC-7) — A BUTTON FOR EVERY SIMPLE ORDER: THE ONE TABLE.
#
# The user's word (November 20, 2026): "make sure buttons exist for simpler
# things but typing is used for missions". A SIMPLE order is one marshal (or
# one group), one verb, at most one place or one enemy, no condition, no time
# limit (docs/INDEPENDENT_COMMAND_SPEC.md §8.1). Every one is a button with its
# price on its face, and a button the game would refuse is greyed with the
# game's own reason. The general's seven digit slots (marshal_state.gd SLOTS)
# were built first; the review of November 20 found eight simple orders and
# four group orders with no button at all (row IC-V4). They are seated HERE,
# in one table, so the card, the map's cards, the province panel, the group
# face and the Help page read the same rows.
#
# A row:
#   id      the button's name
#   where   "card"     the general's card, the row under his seven slots
#           "posture"  the small menu "Posture" opens on that card
#           "enemy"    the card that opens on an enemy (beside Attack)
#           "march"    the card that opens on a province (what he does there)
#           "province" the province panel
#           "group"    the group face, beside Hold… Fortify… Drill…
#   label   the plain words on its face
#   line    what it sends after "<Marshal>, " ({enemy} {friend} {place} {verb}
#           are filled by the surface that draws it); "" = it sends nothing
#   price   where its price and its refusal come from:
#           "probe:<verb>"   tactical_state.order_prices / order_refusals
#                            (backend state_probe.VERBS)
#           "button:<key>"   tactical_state.buttons.prices / .refusals
#                            (backend state_probe.BUTTONS)
#           "quote"          the row the card's quote carries (alts / thens /
#                            look — backend order_quotes, each the order's own
#                            line read by the read-back's reader)
#           "list"           the group's list prices each man (the directive)
#           "none"           it is no order (it opens something)
#   tip     the hover, in plain words
#
# Loaded by path (no class_name: a new one needs the engine's class cache).
# =============================================================================
extends RefCounted

const SIMPLE_ORDER_BUTTONS := [
	# ---- the general's card ------------------------------------------------
	{"id": "stand", "where": "card", "label": "Stand here", "line": "defend",
		"price": "probe:defend",
		"tip": "He stands on the defensive where he is, for this turn. (Hold the ground is the standing order: it lasts until you change it.)"},
	{"id": "stay_put", "where": "card", "label": "Stay put", "line": "wait",
		"price": "button:wait",
		"tip": "He does nothing this turn and is not listed as waiting for orders. Next turn he is listed again."},
	{"id": "posture", "where": "card", "label": "Posture…", "line": "",
		"price": "none",
		"tip": "How he fights: attacking, steady or defending — and the square, for foot."},
	{"id": "task", "where": "card", "label": "Give him a task…", "line": "",
		"price": "none",
		"tip": "A task is an order with a condition, a time limit or an if-then. It is typed: this lists ready sentences for him here; press one and it is written on the command line for you to send or change."},
	# ---- his posture ---------------------------------------------------------
	{"id": "posture_attacking", "where": "posture", "label": "Attacking",
		"line": "aggressive stance", "price": "button:stance:aggressive",
		"tip": "He attacks harder and defends worse."},
	{"id": "posture_steady", "where": "posture", "label": "Steady",
		"line": "neutral stance", "price": "button:stance:neutral",
		"tip": "Neither harder in attack nor in defence."},
	{"id": "posture_defending", "where": "posture", "label": "Defending",
		"line": "defensive stance", "price": "button:stance:defensive",
		"tip": "He defends better and attacks worse."},
	{"id": "form_square", "where": "posture", "label": "Form square",
		"line": "form square", "price": "button:form_square",
		"tip": "Foot only: strong against horse, weak against guns. Any other order breaks it."},
	{"id": "break_square", "where": "posture", "label": "Break square",
		"line": "break square", "price": "button:break_square",
		"tip": "Back into line."},
	# ---- the card that opens on an enemy (beside Attack) ----------------------
	{"id": "pursue", "where": "enemy", "label": "Chase him", "line": "pursue {enemy}",
		"price": "quote", "tip": "A standing order: he follows him wherever he goes and attacks on contact."},
	{"id": "bombard", "where": "enemy", "label": "Bombard", "line": "bombard {enemy}",
		"price": "quote", "tip": "A gun corps shells him from where it stands."},
	{"id": "charge", "where": "enemy", "label": "Charge him", "line": "charge {enemy}",
		"price": "quote", "tip": "Only for cavalry that is eager to charge: an all-out charge — it deals double the damage and takes double."},
	{"id": "held_back", "where": "enemy", "label": "Attack, held back",
		"line": "attack {enemy}, held back", "price": "quote",
		"tip": "An ordinary attack: his cavalry is told beforehand not to make the all-out charge it is eager for."},
	# ---- the card that opens on a province ------------------------------------
	{"id": "then", "where": "march", "label": "then hold · then dig in · then drill · then stand",
		"line": "march to {place} then {verb}", "price": "quote",
		"tip": "What he does when he arrives, free with the march."},
	# ---- the province panel ---------------------------------------------------
	{"id": "look", "where": "province", "label": "Look at {place}", "line": "scout {place}",
		"price": "quote", "tip": "A corps within reach scouts the province from where it stands."},
	# ---- the group face -------------------------------------------------------
	{"id": "group_attack", "where": "group", "verb": "attack", "label": "Attack…",
		"line": "attack {enemy}", "price": "quote",
		"tip": "Then click the enemy. An attack by several is one battle: the first corps leads, and its card says who will answer the guns."},
	{"id": "group_support", "where": "group", "verb": "support", "label": "Support…",
		"line": "support {friend}", "price": "list",
		"tip": "Then click the friend they are to support. Shows the list of each corps' order and its price first."},
	{"id": "group_retreat", "where": "group", "verb": "retreat", "label": "Fall back…",
		"line": "retreat", "price": "list",
		"tip": "Each corps falls back to safe ground. Shows the list first; a corps in no danger stays."},
	{"id": "group_garrison", "where": "group", "verb": "garrison", "label": "Garrison…",
		"line": "garrison", "price": "list",
		"tip": "Each corps leaves a garrison where it stands. Shows the list of each corps' order and its price first."},
]


static func rows(where: String) -> Array:
	"""The table's rows for one surface, in the table's order."""
	var out: Array = []
	for row in SIMPLE_ORDER_BUTTONS:
		if str(row.get("where", "")) == where:
			out.append(row)
	return out


static func row(id: String) -> Dictionary:
	for entry in SIMPLE_ORDER_BUTTONS:
		if str(entry.get("id", "")) == id:
			return entry
	return {}


static func price_of(entry: Dictionary, view: Dictionary) -> int:
	"""What the button's order costs, from the MarshalState view the backend
	filled; -1 when no price is named (the face then names none)."""
	var source := str(entry.get("price", ""))
	if source.begins_with("probe:"):
		var prices = view.get("prices", {})
		var verb := source.substr(6)
		if prices is Dictionary and (prices as Dictionary).has(verb):
			return int(prices[verb])
		return -1
	if source.begins_with("button:"):
		var buttons = view.get("buttons", {})
		if not (buttons is Dictionary):
			return -1
		var button_prices = (buttons as Dictionary).get("prices", {})
		var key := source.substr(7)
		if button_prices is Dictionary and (button_prices as Dictionary).has(key):
			return int(button_prices[key])
	return -1


static func refusal_of(entry: Dictionary, view: Dictionary) -> String:
	"""The game's own short reason this order would be refused — "" when it
	would go."""
	var source := str(entry.get("price", ""))
	if source.begins_with("probe:"):
		var refusals = view.get("refusals", {})
		if refusals is Dictionary:
			return str((refusals as Dictionary).get(source.substr(6), ""))
		return ""
	if source.begins_with("button:"):
		var buttons = view.get("buttons", {})
		if not (buttons is Dictionary):
			return ""
		var button_refusals = (buttons as Dictionary).get("refusals", {})
		if button_refusals is Dictionary:
			return str((button_refusals as Dictionary).get(source.substr(7), ""))
	return ""


static func face(label: String, price: int) -> String:
	"""The words on a button: its label and its price — "Stand here · 1
	action", "Stay put · free"."""
	if price == 0:
		return label + " · free"
	if price > 0:
		return label + " · " + Utils.plural(price, "action")
	return label
