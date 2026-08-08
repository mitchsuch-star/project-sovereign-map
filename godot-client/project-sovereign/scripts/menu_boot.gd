extends RefCounted
class_name MenuBoot

# =============================================================================
# INK & IRON — Main Menu → game scene hand-off (Main Menu pass, position 6)
# =============================================================================
# The class_name-static idiom (UiSettings / AudioManager pattern — NOT a
# project.godot autoload: the parse harness compiles scripts under a bare
# SceneTree where autoload globals never resolve).
#
# The Main Menu WRITES an action and changes to the game scene; main.gd
# CONSUMES it exactly once after its connection test succeeds (Golden Rule 4:
# read the value, use it, THEN clear).
#
#   ""          — plain entry: hydrate whatever world the backend holds
#   "new_game"  — POST /new_game (fresh 1805 campaign; autosave refreshed)
#   "continue"  — load the NEWEST save file (autosave included)
#   "load"      — open the Load Campaign dialog over the fresh session
# =============================================================================

static var pending_action := ""

# Set by main.gd when the player leaves a running campaign for the menu, so
# the menu can offer "Return to the war room" (plain re-entry, no /load — the
# live world still sits in the backend's memory) instead of only Continue.
static var came_from_game := false


static func take_action() -> String:
	var action := pending_action
	pending_action = ""
	return action
