@tool
extends StyleBox

# =============================================================================
# INK & IRON — The Gilt Frame (Session UI, November 11, 2026)
# =============================================================================
# ONE definition of the game's window chrome. Every screen, popup and HUD panel
# used to carry its own StyleBoxFlat — a navy fill inside a thick tan rounded
# border, thirty-four copies of it — and the look read as a web card. This is
# the frame they share now: drawn, outside in,
#
#     a soft shadow → a 1 px dark edge → the gilt rule → a gap →
#     a 1 px inner fillet with re-entrant corners → the panel's own fill,
#     washed slightly DARKER toward its foot (never lighter: no text on it can
#     lose contrast), or a leather texture for the HUD panels.
#
# It is geometry, not a 9-slice texture, so it is crisp at every Interface
# Scale (`content_scale_factor` 1.0 … 2.0) — the reason it is a scripted
# StyleBox (`_draw`) and not a StyleBoxTexture.
#
# THE CONTRACT (pinned by tests/test_ui_gilt_frame.py):
#   * Its properties keep StyleBoxFlat's NAMES — `bg_color`, `border_color`,
#     and the inherited `content_margin_*` — so a scene's own fill, tone and
#     margins stay in its .tscn byte for byte, and code that tints a panel at
#     run time (`style.border_color = …`) keeps working. A consumer asks
#     `"border_color" in style`, never `style is StyleBoxFlat`.
#   * It changes NO layout: the frame is drawn inside the content margins the
#     scene already declares (the widest frame is 7 px; the tightest window
#     margin is 12).
#   * No `class_name`: scenes and the theme reference it by path, so adding it
#     needs no global-class-cache import pass.
# =============================================================================

## The frame's weights. WINDOW: screens and popups (double rule, re-entrant
## corners, the full shadow). HUD: panels that live over the map (single rule
## and a hairline, a short shadow). HAIRLINE: the smallest chrome (one rule).
enum Weight { WINDOW, HUD, HAIRLINE }

const _EDGE := Color(0.016, 0.02, 0.035, 1.0)
const _SPECS := [
	# rule, gap, fillet (0 = none), notch, shadow size, shadow offset y, shadow alpha
	{"rule": 2, "gap": 3, "fillet": true, "notch": 8.0, "shadow": 26, "drop": 7.0, "dark": 0.55},
	{"rule": 1, "gap": 2, "fillet": true, "notch": 0.0, "shadow": 12, "drop": 3.0, "dark": 0.5},
	{"rule": 1, "gap": 0, "fillet": false, "notch": 0.0, "shadow": 6, "drop": 2.0, "dark": 0.4},
]

## The panel's own fill (StyleBoxFlat's name, so scenes keep their line).
@export var bg_color := Color(0.08, 0.1, 0.15, 1.0):
	set(value):
		bg_color = value
		emit_changed()
## The frame's tone: the gilt, or a surface's own amber / crimson / steel.
@export var border_color := Color(0.85, 0.75, 0.55, 1.0):
	set(value):
		border_color = value
		emit_changed()
@export_enum("window", "hud", "hairline") var weight: int = Weight.WINDOW:
	set(value):
		weight = value
		emit_changed()
## False for a panel that must not cast (a card inside another panel).
@export var shadow := true:
	set(value):
		shadow = value
		emit_changed()
## How much darker the fill stands at its foot than at its head (0 = flat).
@export_range(0.0, 0.6) var wash := 0.2:
	set(value):
		wash = value
		emit_changed()
## An optional texture fill (the HUD's leather), stretched from `texture_region`
## and tinted by `texture_modulate` — the theme's leather panel, inside a frame.
@export var texture: Texture2D:
	set(value):
		texture = value
		emit_changed()
@export var texture_region := Rect2(300, 150, 680, 680):
	set(value):
		texture_region = value
		emit_changed()
@export var texture_modulate := Color(0.24, 0.27, 0.46, 0.96):
	set(value):
		texture_modulate = value
		emit_changed()

var _base := StyleBoxFlat.new()
var _outer := StyleBoxFlat.new()


func _spec() -> Dictionary:
	return _SPECS[clampi(weight, 0, _SPECS.size() - 1)]


## The frame's total thickness at an edge, in logical px (edge + rule + gap +
## fillet) — what a corner control (the resize grip) must clear.
func thickness() -> float:
	var spec := _spec()
	return 1.0 + float(spec["rule"]) + float(spec["gap"]) + (1.0 if spec["fillet"] else 0.0)


func _get_draw_rect(rect: Rect2) -> Rect2:
	if not shadow:
		return rect
	var spec := _spec()
	return rect.grow(float(spec["shadow"]) + float(spec["drop"]))


func _draw(to_canvas_item: RID, rect: Rect2) -> void:
	var spec := _spec()
	var rule_w: int = int(spec["rule"])
	var alpha := bg_color.a

	# 1 — the shadow, the dark edge and the fill (one StyleBoxFlat).
	_base.bg_color = bg_color
	_base.border_color = Color(_EDGE.r, _EDGE.g, _EDGE.b, alpha)
	_base.set_border_width_all(1)
	_base.shadow_size = int(spec["shadow"]) if shadow else 0
	_base.shadow_color = Color(0, 0, 0, float(spec["dark"]) * alpha)
	_base.shadow_offset = Vector2(0, float(spec["drop"]))
	_base.draw(to_canvas_item, rect)

	var inner := rect.grow(-1.0)
	# 2 — the leather, where a panel carries one.
	if texture != null:
		RenderingServer.canvas_item_add_texture_rect_region(
			to_canvas_item, inner, texture.get_rid(), texture_region, texture_modulate)
	# 3 — the wash: darker toward the foot, never lighter than the fill.
	if wash > 0.0:
		var clear := Color(0, 0, 0, 0)
		var foot := Color(0, 0, 0, wash * alpha)
		RenderingServer.canvas_item_add_polygon(to_canvas_item,
			PackedVector2Array([inner.position, Vector2(inner.end.x, inner.position.y),
				inner.end, Vector2(inner.position.x, inner.end.y)]),
			PackedColorArray([clear, clear, foot, foot]))

	# 4 — the gilt rule.
	_outer.draw_center = false
	_outer.border_color = border_color
	_outer.set_border_width_all(rule_w)
	_outer.draw(to_canvas_item, inner)

	# 5 — the inner fillet, its corners re-entrant on a window.
	if not spec["fillet"]:
		return
	var inset := 1.0 + float(rule_w) + float(spec["gap"]) + 0.5
	var r := rect.grow(-inset)
	if r.size.x <= 4.0 or r.size.y <= 4.0:
		return
	var n: float = minf(float(spec["notch"]), minf(r.size.x, r.size.y) * 0.25)
	var line := Color(border_color.r, border_color.g, border_color.b, border_color.a * 0.6)
	var a := r.position
	var b := r.end
	var points: PackedVector2Array
	if n <= 0.0:
		points = PackedVector2Array([a, Vector2(b.x, a.y), b, Vector2(a.x, b.y), a])
	else:
		points = PackedVector2Array([
			Vector2(a.x + n, a.y), Vector2(b.x - n, a.y), Vector2(b.x - n, a.y + n),
			Vector2(b.x, a.y + n), Vector2(b.x, b.y - n), Vector2(b.x - n, b.y - n),
			Vector2(b.x - n, b.y), Vector2(a.x + n, b.y), Vector2(a.x + n, b.y - n),
			Vector2(a.x, b.y - n), Vector2(a.x, a.y + n), Vector2(a.x + n, a.y + n),
			Vector2(a.x + n, a.y)])
	RenderingServer.canvas_item_add_polyline(to_canvas_item, points, PackedColorArray([line]), 1.0, false)
	if n <= 0.0:
		return
	# 6 — a gilt stud in each cut corner.
	var s := 1.75
	var h := n * 0.5
	for stud in [Vector2(a.x + h, a.y + h), Vector2(b.x - h, a.y + h),
			Vector2(b.x - h, b.y - h), Vector2(a.x + h, b.y - h)]:
		RenderingServer.canvas_item_add_polygon(to_canvas_item,
			PackedVector2Array([stud + Vector2(0, -s), stud + Vector2(s, 0),
				stud + Vector2(0, s), stud + Vector2(-s, 0)]),
			PackedColorArray([border_color]))
