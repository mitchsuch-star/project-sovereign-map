extends Node
class_name DialogManager

# =============================================================================
# PROJECT SOVEREIGN - Dialog Manager (R16)
# =============================================================================
# Centralized dialog registry. Handles scene loading, instantiation, and
# modal tracking. Replaces ~275 lines of boilerplate in main.gd _ready().
#
# Layer assignments (set in .tscn files, higher = draws on top):
#    90: tutorial_overlay (POSITION 7 — the School of War tutor card,
#        NON-modal: above the layer-50 screens and TopBar 75 so it survives
#        the ledger opening, UNDER the whole 101+ modal band so an objection
#        popup draws over it)
#   101: load_dialog
#   102: clarification_popup
#   103: interrupt_popup
#   104: strategic_report_popup
#   105: capture_choice_dialog
#   106: glorious_charge_dialog
#   107: redemption_dialog
#   108: objection_dialog
#   109: reward_dialog (ES-7 second pass §0.6.8)
#   110: proposal_confirm_popup + diplomacy_wizard (pre-existing double-book;
#        never open simultaneously — the wizard hands off before confirm)
#   111: commitment_paradox_popup
#   112: incoming_proposal_popup
#   113: talleyrand_objection_popup
#   114: marshal_petition_dialog (Jealousy v3.2 — the petition channel)
#   115: vassal_rebellion_popup + proposal_result_popup (orphan scene, never
#        registered or routed — recorded so the slot is not re-used blind)
#   116: sabotage_discovery_popup
#   117: proclamation_popup (NA-6b — The Proclamation, spec §11.8 stage 2)
#   118: enemy_phase_dialog
#   119: mailbox_panel
#   120: pause_menu (always on top of the 101-119 band)
#   121: battle_diorama (BD — above enemy_phase so "⚔ View the field" opens
#        over it; pause cannot stack above it because a visible modal blocks
#        the ESC ladder, so 120-vs-121 never actually contest)
# =============================================================================

var _dialogs: Dictionary = {}  # name -> {node, modal}

func register(dialog_name: String, scene_path: String, modal: bool = true) -> Node:
	var scene = load(scene_path)
	if not scene:
		push_error("DialogManager: Failed to load " + scene_path)
		return null
	var instance = scene.instantiate()
	get_parent().add_child(instance)
	instance.hide()
	_dialogs[dialog_name] = {"node": instance, "modal": modal}
	return instance

func get_dialog(dialog_name: String) -> Node:
	var entry = _dialogs.get(dialog_name)
	if entry:
		return entry.node
	return null

func is_any_modal_open() -> bool:
	for entry in _dialogs.values():
		if entry.modal and entry.node and entry.node.visible:
			return true
	return false

func hide_all():
	for entry in _dialogs.values():
		if entry.node:
			entry.node.hide()
