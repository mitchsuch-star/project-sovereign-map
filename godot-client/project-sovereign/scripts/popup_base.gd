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

func esc_control() -> Button:
	"""FA-94 (slice 17): the button ESC presses on this popup, or null.

	NULL BY DEFAULT — a decision modal (interrupt, paradox, capture choice)
	must never be answered by a reflex keypress: the rightmost cannon-fire
	option is `hold_position` at −3 trust and a cancelled order. A
	read-and-dismiss surface overrides this to its own dismiss button.
	ESC presses the button's HANDLER (which emits the dismissal main.gd's
	control-return tail listens for), never `close_popup()` directly — a
	bare close hides the card, leaves the command line disabled and orphans
	every stashed surface (the FA-N4 / slice-6 soft-lock class)."""
	return null

func _unhandled_input(event: InputEvent) -> void:
	if not visible:
		return
	if not event.is_action_pressed("ui_cancel"):
		return
	var control := esc_control()
	if control == null or control.disabled:
		return  # decline WITHOUT consuming — main.gd's ESC ladder may want it
	get_viewport().set_input_as_handled()
	control.pressed.emit()

# UI-5: set by `decided_with` — the next close (close_popup) skips its "back" cue.
var _decided: bool = false

func decided_with(cue: String) -> void:
	"""UI-5: a decision plays its own cue (the answer's sound), stops this
	popup's arrival cues, and marks the close that follows as already voiced —
	so "back" does not also play. Call it from the answer's handler, before
	close_popup()."""
	for p in _own_cues:
		AudioManager.stop_player(p)
	_own_cues.clear()
	_decided = true
	AudioManager.play(cue)

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
	# UI-5: a close that FOLLOWS a decision which already played its own cue
	# (`decided_with`) does not add the "back" on top; a plain close/Esc keeps it.
	var quiet: bool = _decided
	_decided = false
	if visible and not quiet:
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
	# Session UI (November 11, 2026): the gilt frame, in the popup's tone.
	panel.add_theme_stylebox_override("panel",
			Utils.gilt_frame(Utils.UI_POPUP_BG, border_color, Utils.FRAME_WINDOW, 24.0))
