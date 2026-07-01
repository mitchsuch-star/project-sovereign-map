extends Node
class_name Utils

# =============================================================================
# PROJECT SOVEREIGN - Shared Utilities (R15)
# =============================================================================
# Single source of truth for color palette, nation colors, and formatting
# helpers. Referenced as Utils.COLOR_* from any script (class_name autoload).
# =============================================================================

# === Shared Color Palette (hex strings for BBCode) ===
const COLOR_GOLD = "d9c08c"
const COLOR_COMMAND = "7eb8da"
const COLOR_SUCCESS = "8fbc8f"
const COLOR_ERROR = "cd6b6b"
const COLOR_BATTLE = "daa06d"
const COLOR_INFO = "a0a0a8"
const COLOR_MARSHAL = "c9b8e0"
const COLOR_CONQUEST = "90d890"
const COLOR_FEEDBACK = "b8a0d9"
const COLOR_DISPATCH = "c9b878"
const COLOR_BERTHIER = "B8860B"
const COLOR_OBSERVATION = "DAA520"
const COLOR_TEXT = "eeeeee"
const COLOR_DIMMED = "808080"
const COLOR_WARNING = "e0c060"

# === Semantic Aliases (same hex, different context) ===
const COLOR_BLUE = "6495ed"
const COLOR_ORANGE = "daa06d"       # Same as COLOR_BATTLE — semantic alias for ledger UIs
const COLOR_GREY = "808080"         # Same as COLOR_DIMMED — semantic alias
const COLOR_HEADER = "B8860B"       # Same as COLOR_BERTHIER — semantic alias for ledger headers

# === Nation Colors (Color objects for UI elements) ===
# Single source of truth for nation colors (SCALE_READINESS_PLAN §3.3).
# Any script needing a nation color reads Utils.NATION_COLORS — do NOT
# redefine these locally. Drift is guarded by
# tests/test_gdscript_color_centralization.py.
const NATION_COLORS = {
	"France": Color(0.255, 0.412, 0.882),
	"Britain": Color(0.863, 0.078, 0.235),
	"Prussia": Color(0.2, 0.2, 0.2),
	"Austria": Color(1.0, 0.843, 0.0),
	"Saxony": Color(0.4, 0.6, 0.3),
	"Russia": Color(0.2, 0.5, 0.2),
	"Spain": Color(0.8, 0.6, 0.1),
	# --- Full-Europe (126-province) roster — Map Slice 3 ---
	"Ottoman": Color(0.0, 0.5, 0.4),
	"Sweden": Color(0.0, 0.42, 0.65),
	"Naples": Color(0.5, 0.7, 0.85),
	"Portugal": Color(0.1, 0.55, 0.35),
	"Denmark": Color(0.85, 0.3, 0.3),
	"Bavaria": Color(0.45, 0.6, 0.85),
	"Hanover": Color(0.55, 0.35, 0.15),
	"Hesse": Color(0.6, 0.5, 0.3),
	"PapalStates": Color(0.9, 0.85, 0.55),
	"Sardinia": Color(0.7, 0.7, 0.72),
	"Holland": Color(0.9, 0.5, 0.1),
	"KingdomOfItaly": Color(0.2, 0.6, 0.35),
	"Switzerland": Color(0.8, 0.2, 0.2),
	"Neutral": Color(0.565, 0.933, 0.565),
}

# === Map Connection Line Color ===
const COLOR_CONNECTION = Color(0.6, 0.6, 0.6)

# === Default Fallback Colors for Unknown Nations ===
const COLOR_ENEMY_DEFAULT = Color(0.7, 0.2, 0.2)

# === Formatting Helpers ===

static func bbcode_color(text: String, color: String) -> String:
	return "[color=#" + color + "]" + text + "[/color]"

static func format_number(n: int) -> String:
	"""Format integer with thousands separators (e.g. 12,500)."""
	var s = str(abs(n))
	var result = ""
	var count = 0
	for i in range(s.length() - 1, -1, -1):
		if count > 0 and count % 3 == 0:
			result = "," + result
		result = s[i] + result
		count += 1
	if n < 0:
		result = "-" + result
	return result
