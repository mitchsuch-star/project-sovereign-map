extends CanvasLayer
class_name PopupBase

# =============================================================================
# PROJECT SOVEREIGN - Popup Base Class (R15)
# =============================================================================
# Base class for modal popups. Provides common utilities:
# - show_popup / close_popup lifecycle
# - _disable_all_buttons helper (prevents double-click)
# - _apply_standard_theme for consistent panel styling
#
# Subclasses keep their own signals — this class does NOT impose a uniform
# signal interface. Each popup emits whatever main.gd expects.
# =============================================================================

# UX23-R1: cues this popup started and should take with it when it closes.
# A subclass declares them rather than PopupBase guessing, because the rule is
# not "stop everything" — an ARRIVAL sound stops on close; a DEPARTURE sound
# IS the close (this very function plays "back" on the way out).
var _own_cues: Array = []

func show_popup(_data: Dictionary = {}):
	"""Override in subclass. Called with popup data from backend."""
	show()

func claim_cue(p) -> void:
	"""Declare the player `AudioManager.play()` returned as this popup's own,
	so `close_popup` silences exactly THAT sound.

	UX23-R1. One-shots are children of the AudioManager singleton, not of the
	scene, so before `stop_player` existed a 6-second peal outlived both the
	panel that rang it and `change_scene_to_file`.

	Review round: this used to claim a cue NAME, which made the ownership
	nominal — closing this popup would have silenced every live play of that
	name, including another surface's."""
	if p != null and not _own_cues.has(p):
		_own_cues.append(p)

func close_popup():
	"""Standard close: silence what we started, disable buttons, then hide."""
	for p in _own_cues:
		AudioManager.stop_player(p)
	_own_cues.clear()
	if visible:
		AudioManager.play("back")
	_disable_all_buttons()
	hide()

func _disable_all_buttons():
	"""Recursively disable all Button nodes under this popup."""
	_disable_buttons_recursive(self)

func _disable_buttons_recursive(node: Node):
	for child in node.get_children():
		if child is Button:
			child.disabled = true
		_disable_buttons_recursive(child)

func _apply_standard_theme(panel: PanelContainer, border_color: Color = Color(Utils.UI_GOLD, 0.6)):
	"""Apply consistent dark panel theme with optional border color."""
	var style = StyleBoxFlat.new()
	style.bg_color = Utils.UI_POPUP_BG
	style.border_color = border_color
	style.set_border_width_all(2)
	style.set_corner_radius_all(8)
	style.content_margin_left = 24.0
	style.content_margin_top = 24.0
	style.content_margin_right = 24.0
	style.content_margin_bottom = 24.0
	panel.add_theme_stylebox_override("panel", style)
