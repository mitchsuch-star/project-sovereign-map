extends Node2D
class_name DioramaPlinth

# =============================================================================
# PROJECT SOVEREIGN — The corps plinth (row BA, the battle in acts)
# =============================================================================
# The Blend look the user ruled on November 14, 2026 (BATTLE_DIORAMA_SPEC.md
# §15.2 row 2): each corps' carved figures stand on a card-like plinth, in the
# manner of the tabletop game Blücher's unit cards — a slab under the men with
# the nation's band at its outer end and six strength pips on its front face,
# ticked off as the corps bleeds. The plinth is part of the block's ART, so
# the block that marches, gives way and leaves the table is the plinth.
#
# The marshal's name and his before -> after figures stay ABOVE the men, where
# the tableau's measured layout keeps them readable at every rank (four ranks
# recede; a name scaled with the art read 9 px at the fourth - UXR-X5).
#
# Display-only (Golden Rule 6): fed from the diorama payload, never reads or
# writes game state.
# =============================================================================

const PIPS := 6
const HALF_W := 78.0        # the slab under the three-abreast front rank and its bases
const TOP_Y := -30.0        # behind the rear rank's feet (they stand at y = -22)
const LIP_Y := 12.0         # where the top face meets the front face, clear of the bases' rims
const FACE_H := 12.0        # the front face: band, pips (it ends above the fate captions at y = 30)
const BAND_W := 9.0
const PIP_W := 10.0
const PIP_H := 7.0
const PIP_GAP := 4.0

const SLAB_TOP := Color(0.235, 0.170, 0.110, 0.92)     # waxed walnut, a tone above the tray
const SLAB_FACE := Color(0.150, 0.105, 0.068, 1.0)
const SLAB_EDGE := Color(0.72, 0.60, 0.36, 0.70)        # the brass line
const PIP_STANDS := Color(0.86, 0.80, 0.66, 1.0)        # ivory
const PIP_LOST := Color(0.843, 0.388, 0.369, 1.0)       # the tally's own red
const PIP_SEAT := Color(0.0, 0.0, 0.0, 0.45)
const FACE_DOWN := Utils.UI_PLINTH_FACE_DOWN            # a beaten corps slab, dulled

var is_left := true
var band_color := Utils.UI_NEUTRAL_FIGURE
var _lost := 0.0            # pips lost, 0 .. PIPS (fractional while the count runs)
var _face_down := false


func setup(nation_color: Color, left_side: bool) -> void:
	band_color = nation_color
	is_left = left_side
	z_index = -1            # under the men who stand on it
	queue_redraw()


static func pips_lost(committed: int, remaining: int) -> int:
	"""How many of the six pips a corps has lost: its losses as a share of
	what it brought, rounded; a corps that lost anything has lost one, and
	only a corps with nothing left has lost all six."""
	if committed <= 0:
		return 0
	var lost: int = clampi(committed - remaining, 0, committed)
	if lost <= 0:
		return 0
	if remaining <= 0:
		return PIPS
	return clampi(int(round(float(lost) / float(committed) * PIPS)), 1, PIPS - 1)


func set_lost(value: float) -> void:
	var v: float = clampf(value, 0.0, float(PIPS))
	if is_equal_approx(v, _lost):
		return
	_lost = v
	queue_redraw()


func get_lost() -> float:
	return _lost


func set_face_down(down: bool) -> void:
	if down == _face_down:
		return
	_face_down = down
	modulate = FACE_DOWN if down else Color.WHITE
	queue_redraw()


func is_face_down() -> bool:
	return _face_down


func _draw() -> void:
	# The top face the men stand on, then the front face, then the brass line.
	draw_rect(Rect2(-HALF_W, TOP_Y, HALF_W * 2.0, LIP_Y - TOP_Y), SLAB_TOP)
	draw_rect(Rect2(-HALF_W, LIP_Y, HALF_W * 2.0, FACE_H), SLAB_FACE)
	draw_rect(Rect2(-HALF_W, TOP_Y, HALF_W * 2.0, LIP_Y - TOP_Y + FACE_H), SLAB_EDGE, false, 1.0)
	draw_line(Vector2(-HALF_W, LIP_Y), Vector2(HALF_W, LIP_Y), SLAB_EDGE, 1.0)

	# The nation's band at the OUTER end (away from the clash line), the one
	# faction colour on the slab — as the standard is the one on the men.
	var band_x: float = -HALF_W if is_left else HALF_W - BAND_W
	draw_rect(Rect2(band_x, TOP_Y, BAND_W, LIP_Y - TOP_Y + FACE_H),
			WarTablePiece.legible_tint(band_color))

	# Six pips on the front face. They are lost from the CLASH side first -
	# the corps wears away from where it met the enemy.
	var run: float = PIPS * PIP_W + (PIPS - 1) * PIP_GAP
	var free_left: float = -HALF_W + (BAND_W if is_left else 0.0)
	var free_w: float = HALF_W * 2.0 - BAND_W
	var x0: float = free_left + (free_w - run) / 2.0
	var y0: float = LIP_Y + (FACE_H - PIP_H) / 2.0
	for i in range(PIPS):
		var from_clash: int = (PIPS - 1 - i) if is_left else i
		var x: float = x0 + i * (PIP_W + PIP_GAP)
		var cell := Rect2(x, y0, PIP_W, PIP_H)
		draw_rect(cell, PIP_SEAT)
		var gone: float = clampf(_lost - float(from_clash), 0.0, 1.0)
		if gone >= 1.0:
			draw_rect(cell.grow(-1.0), Color(PIP_LOST, 0.55))
		elif gone > 0.0:
			draw_rect(cell.grow(-1.0), PIP_STANDS.lerp(PIP_LOST, gone))
		else:
			draw_rect(cell.grow(-1.0), PIP_STANDS)
