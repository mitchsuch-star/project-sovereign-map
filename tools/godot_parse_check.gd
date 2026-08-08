# SETTLEMENT_UI_CLEANUP_SPEC v0.28 G2-Slice-W1 Godot Parse Harness.
#
# Invoke headless:
#   Godot_v4.4.1-stable_win64.exe --headless --quit --path godot-client/project-sovereign --script ../../tools/godot_parse_check.gd
#
# The harness parses + loads every settlement-critical Godot script and
# writes a JSON report to tools/godot_parse_report.json. Exit code is
# non-zero on any parse/load failure so CI machines with Godot on PATH
# can fail builds. CI machines without Godot consume the committed
# report and rely on the pytest stale-report guard.
#
# Report shape:
#   {
#     "timestamp": "<ISO8601 UTC>",
#     "godot_version": "<engine version string>",
#     "scripts": [
#       {"path": "...", "parse_ok": bool, "load_ok": bool, "errors": [...]},
#       ...
#     ]
#   }
extends SceneTree


const SETTLEMENT_CRITICAL_SCRIPTS = [
	"res://scripts/utils.gd",
	"res://scripts/dialog_manager.gd",
	"res://scripts/main.gd",
	"res://scripts/diplomacy_wizard.gd",
	"res://scripts/proposal_confirm_popup.gd",
	# G4F-17: renders the armistice mechanics block on incoming offers
	# (and is the counter-offer popup surface) — settlement-adjacent.
	"res://scripts/incoming_proposal_popup.gd",
	"res://scripts/war_detail_popup.gd",
	"res://scripts/war_status_panel.gd",
	"res://scripts/diplomatic_ledger.gd",
	"res://scripts/top_bar.gd",
	"res://scripts/notification_bar.gd",
	"res://scripts/mailbox_panel.gd",
	# IGR-E: the plunder/secure modal. It is instantiated at RUNTIME by
	# dialog_manager.register, not embedded in main.tscn, so it was covered
	# by neither the script list nor SCENE_INSTANTIATION_CHECKS — a parse
	# error in it passed this harness EXIT=0 and surfaced only in a live
	# boot. It renders a gold figure the player decides on; guard it.
	"res://scripts/capture_choice_dialog.gd",
	# BD (Battle Diorama): the tableau + its locket are runtime-registered
	# (same IGR-E gap class); the enemy-phase dialog gained the view-field
	# links; pause_menu/ui_settings gained the battle-sfx toggle.
	"res://scripts/battle_diorama.gd",
	"res://scripts/portrait_locket.gd",
	"res://scripts/enemy_phase_dialog.gd",
	"res://scripts/pause_menu.gd",
	"res://scripts/ui_settings.gd",
	# DEF-5 naval (NV surfaces): the Admiralty ledger block + the dockyard
	# chip touched these; the XR-1 rule adds every touched script.
	"res://scripts/strategic_ledger.gd",
	"res://scripts/region_panel.gd",
	# Music & Sound Core (wiring half): the autoload + every script the cue
	# map touched (XR-1 — every touched script parses in the harness).
	"res://scripts/audio_manager.gd",
	"res://scripts/popup_base.gd",
	"res://scripts/campaign_log.gd",
	"res://scripts/dispatch_view.gd",
	"res://scripts/marshal_management.gd",
	"res://scripts/proclamation_popup.gd",
	"res://scripts/marshal_petition_dialog.gd",
	"res://scripts/objection_dialog.gd",
	"res://scripts/interrupt_popup.gd",
	"res://scripts/glorious_charge_dialog.gd",
	"res://scripts/clarification_popup.gd",
	"res://scripts/vassal_rebellion_popup.gd",
	"res://scripts/reward_dialog.gd",
	"res://scripts/proposal_result_popup.gd",
	# Main Menu pass (position 6): the front door + the shared Settings
	# surface + the scene hand-off statics (XR-1 — every touched script
	# parses in the harness).
	"res://scripts/main_menu.gd",
	"res://scripts/settings_panel.gd",
	"res://scripts/menu_boot.gd",
]

# Map Slices 6-7: the map renderer scripts live under scenes/, not
# scripts/ — kept in their own list because the pytest staleness guard for
# SETTLEMENT_CRITICAL_SCRIPTS resolves names against scripts/ only; the
# scenes-dir coverage + staleness checks are owned by
# tests/test_map_owner_fill.py.
const MAP_CRITICAL_SCRIPTS = [
	"res://scenes/map_renderer_base.gd",
	"res://scenes/europe_map.gd",
	"res://scenes/europe_map_smoke.gd",
	"res://scenes/map.gd",
	"res://scenes/map_label_layer.gd",
	# BD: the shared piece art (public accessors added) + the diorama's
	# falling figure — both live under scenes/.
	"res://scenes/war_table_piece.gd",
	"res://scenes/diorama_figure.gd",
	# DEF-5 naval: verdict tints + port glyphs on the connection layer.
	"res://scenes/map_connection_layer.gd",
]

# Map Slice 7: headless scene-instantiation checks. instantiate() attaches
# scripts and loads every ext_resource WITHOUT entering the tree (_ready never
# runs, no backend needed). main.tscn additionally verifies the MapArea node is
# scripted by the Europe game map (scenes/map.gd).
const SCENE_INSTANTIATION_CHECKS = [
	"res://scenes/main.tscn",
	"res://scenes/europe_map_smoke.tscn",
	"res://scenes/battle_diorama.tscn",  # BD: runtime-registered modal
	# Main Menu pass (position 6): the project's NEW main scene + the shared
	# Settings component it instantiates at runtime (IGR-E gap class).
	"res://scenes/main_menu.tscn",
	"res://scenes/settings_panel.tscn",
]
const MAIN_SCENE_PATH = "res://scenes/main.tscn"
const MAP_AREA_EXPECTED_SCRIPT = "res://scenes/map.gd"

const REPORT_PATH = "res://../../tools/godot_parse_report.json"


func _init():
	var report = {
		"timestamp": Time.get_datetime_string_from_system(true, false) + "Z",
		"godot_version": Engine.get_version_info().get("string", ""),
		"harness": "tools/godot_parse_check.gd",
		"note": "Map Slice 7 refresh: map.gd is the Europe game map (extends europe_map.gd); europe_map_smoke.gd carries the smoke-only demo; scene-instantiation checks added. Invoke from repo root with --path godot-client/project-sovereign --script ../../tools/godot_parse_check.gd after a headless editor/import pass if the class-name cache is missing.",
		"scripts": [],
		"scenes": [],
	}
	var any_failed = false
	for script_path in SETTLEMENT_CRITICAL_SCRIPTS + MAP_CRITICAL_SCRIPTS:
		var entry = _check_script(script_path)
		report["scripts"].append(entry)
		if not entry["parse_ok"] or not entry["load_ok"]:
			any_failed = true
			push_error("[godot_parse_check] %s failed: %s" % [script_path, entry["errors"]])
	for scene_path in SCENE_INSTANTIATION_CHECKS:
		var scene_entry = _check_scene(scene_path)
		report["scenes"].append(scene_entry)
		if not scene_entry["load_ok"] or not scene_entry["instantiate_ok"]:
			any_failed = true
			push_error("[godot_parse_check] %s failed: %s" % [scene_path, scene_entry["errors"]])
	var report_text = JSON.stringify(report, "  ")
	var f = FileAccess.open(REPORT_PATH, FileAccess.WRITE)
	if f == null:
		push_error("[godot_parse_check] Cannot open report file %s" % REPORT_PATH)
		quit(2)
		return
	f.store_string(report_text)
	f.close()
	if any_failed:
		quit(1)
	else:
		quit(0)


func _check_script(path: String) -> Dictionary:
	var entry = {
		"path": path,
		"parse_ok": false,
		"load_ok": false,
		"errors": [],
	}
	if not ResourceLoader.exists(path):
		entry["errors"].append("script_not_found")
		return entry
	# ResourceLoader.load() returns null on parse failure; an actual GDScript
	# resource indicates the file parsed. `reload()` then runs the validator.
	var script = ResourceLoader.load(path)
	if script == null:
		entry["errors"].append("resource_load_returned_null")
		return entry
	entry["parse_ok"] = true
	if not (script is GDScript):
		entry["errors"].append("resource_not_gdscript")
		return entry
	var reload_err = script.reload()
	if reload_err != OK:
		entry["errors"].append("reload_error_%d" % reload_err)
		return entry
	entry["load_ok"] = true
	return entry


func _check_scene(path: String) -> Dictionary:
	# instantiate() never adds the node to the tree, so _ready()/@onready never
	# run — this validates the scene's resource graph + attached scripts, not
	# runtime behavior (the live smoke owns that).
	var entry = {
		"path": path,
		"load_ok": false,
		"instantiate_ok": false,
		"errors": [],
	}
	if not ResourceLoader.exists(path):
		entry["errors"].append("scene_not_found")
		return entry
	var packed = ResourceLoader.load(path)
	if packed == null or not (packed is PackedScene):
		entry["errors"].append("scene_load_failed")
		return entry
	entry["load_ok"] = true
	var root = packed.instantiate()
	if root == null:
		entry["errors"].append("instantiate_returned_null")
		return entry
	if path == MAIN_SCENE_PATH:
		var map_area = root.get_node_or_null("MapArea")
		var map_script = map_area.get_script() if map_area != null else null
		var script_path = map_script.resource_path if map_script != null else ""
		entry["map_area_script"] = script_path
		if script_path != MAP_AREA_EXPECTED_SCRIPT:
			entry["errors"].append("map_area_script_mismatch:%s" % script_path)
			root.free()
			return entry
	entry["instantiate_ok"] = true
	root.free()
	return entry
