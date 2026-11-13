extends RefCounted
class_name Keys

# =============================================================================
# Session UI-5 (November 12, 2026) — the remappable global hotkeys.
# =============================================================================
# The hotkey handlers (main.gd `_unhandled_input` / `_on_command_input_gui_input`
# / `_alt_game_key`, map_renderer_base.gd's key handlers) keep their literal
# KEY_* tables — many pins read them. A rebinding is applied at their DOOR:
# `canonical(event)` rewrites the key the player pressed into the DEFAULT key of
# the action bound to it, so every handler below reads the default it always
# read. A key whose action moved elsewhere comes back as KEY_NONE (it no longer
# fires that action); a key no action knows passes through untouched. Alt (the
# "while typing" modifier) and every other modifier is kept.
#
# Stored per machine in UiSettings ("keys" section): only the actions the
# player rebound; DEFAULTS below hold the rest. Settings → CONTROLS lists them
# (click a row, press a key; a clash SWAPS the two, Restore defaults).
# The in-screen number keys (the ledgers' tabs 1–8) and Esc/Enter stay fixed.
# =============================================================================

# [action, the player's words for it, default keycode]
const ACTIONS := [
	["event_log", "Event Log", KEY_L],
	["ledger", "Strategic Ledger", KEY_T],
	["generals", "Generals", KEY_G],
	["diplomacy", "Diplomatic Ledger", KEY_D],
	["dispatch", "Dispatch", KEY_R],
	["moniteur", "Le Moniteur", KEY_N],
	["end_turn", "End Turn", KEY_E],
	["terminal", "Command window", KEY_TAB],
	["idle_corps", "Next idle corps", KEY_PERIOD],
	["map_mode", "Map view", KEY_M],
	["cabinet", "The Cabinet", KEY_F1],
	["help", "Help & Keys", KEY_F10],
	["hide_hud", "Hide the HUD", KEY_H],
	["quicksave", "Quicksave", KEY_F5],
	["quickload", "Quickload", KEY_F9],
	["recentre", "Recentre the map", KEY_HOME],
]

# Keys a player may not bind to an action: they type, close, confirm or move
# the map, or they are the ledgers' own tab keys.
const RESERVED := [KEY_ESCAPE, KEY_ENTER, KEY_KP_ENTER, KEY_SPACE, KEY_BACKSPACE,
	KEY_DELETE, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_SHIFT, KEY_CTRL,
	KEY_ALT, KEY_META, KEY_CAPSLOCK, KEY_EQUAL, KEY_MINUS, KEY_KP_ADD,
	KEY_KP_SUBTRACT, KEY_0, KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6, KEY_7,
	KEY_8, KEY_9]


static func actions() -> Array:
	return ACTIONS


static func default_key(action: String) -> int:
	for row in ACTIONS:
		if String(row[0]) == action:
			return int(row[2])
	return KEY_NONE


static func label_of(action: String) -> String:
	for row in ACTIONS:
		if String(row[0]) == action:
			return String(row[1])
	return action


static func key_for(action: String) -> int:
	var fallback := default_key(action)
	if fallback == KEY_NONE:
		return KEY_NONE
	return UiSettings.get_key_binding(action, fallback)


static func key_name(action: String) -> String:
	"""The bound key's own name as a keyboard prints it ("L", "F10", "Tab")."""
	var key := key_for(action)
	if key == KEY_NONE:
		return ""
	if key == KEY_PERIOD:
		return "."
	return OS.get_keycode_string(key)


static func hint(action: String) -> String:
	"""The parenthesised key a button shows: "(L)"."""
	var key_text := key_name(action)
	return "(" + key_text + ")" if key_text != "" else ""


static func action_for_key(keycode: int) -> String:
	for row in ACTIONS:
		if key_for(String(row[0])) == keycode:
			return String(row[0])
	return ""


static func is_reserved(keycode: int) -> bool:
	return keycode in RESERVED


static func rebind(action: String, keycode: int) -> String:
	"""Bind `action` to `keycode`. A clash SWAPS: the action that held the key
	takes `action`'s old key. Returns the swapped action ("" for none), or
	"reserved" when the key may not be bound."""
	if default_key(action) == KEY_NONE or keycode == KEY_NONE:
		return ""
	if is_reserved(keycode):
		return "reserved"
	var old_key := key_for(action)
	if old_key == keycode:
		return ""
	var holder := action_for_key(keycode)
	UiSettings.set_key_binding(action, keycode)
	if holder != "" and holder != action:
		UiSettings.set_key_binding(holder, old_key)
		return holder
	return ""


static func reset_all() -> void:
	UiSettings.clear_key_bindings()


static func is_rebound() -> bool:
	for row in ACTIONS:
		if key_for(String(row[0])) != int(row[2]):
			return true
	return false


static func canonical(event: InputEvent) -> InputEvent:
	"""The door every global hotkey handler reads through (see the header)."""
	if not (event is InputEventKey) or not is_rebound():
		return event
	var key := event as InputEventKey
	var pressed_key := key.keycode
	var bound := action_for_key(pressed_key)
	var target := pressed_key
	if bound != "":
		target = default_key(bound)
	else:
		for row in ACTIONS:
			if int(row[2]) == pressed_key:
				target = KEY_NONE   # its action moved to another key
				break
	if target == pressed_key:
		return event
	var copy := key.duplicate() as InputEventKey
	copy.keycode = target
	copy.physical_keycode = target
	return copy


static func matches(event: InputEvent, action: String) -> bool:
	"""True when `event` is a press of `action`'s bound key (modifiers aside)."""
	if not (event is InputEventKey) or not event.pressed or event.echo:
		return false
	return (event as InputEventKey).keycode == key_for(action)


static func is_help_key(event: InputEvent) -> bool:
	"""Help & Keys opens on its bound key or on "?" (Shift+/ on any layout)."""
	if not (event is InputEventKey) or not event.pressed or event.echo:
		return false
	var key := event as InputEventKey
	return key.keycode == key_for("help") or key.unicode == 63
