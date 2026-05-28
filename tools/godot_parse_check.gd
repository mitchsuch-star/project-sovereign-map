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
	"res://scripts/war_detail_popup.gd",
	"res://scripts/war_status_panel.gd",
	"res://scripts/diplomatic_ledger.gd",
	"res://scripts/top_bar.gd",
	"res://scripts/notification_bar.gd",
	"res://scripts/mailbox_panel.gd",
]

const REPORT_PATH = "res://../../tools/godot_parse_report.json"


func _init():
	var report = {
		"timestamp": Time.get_datetime_string_from_system(true, false) + "Z",
		"godot_version": Engine.get_version_info().get("string", ""),
		"harness": "tools/godot_parse_check.gd",
		"note": "SETTLEMENT_UI_CLEANUP_SPEC v0.32 May 28 all-tiers audit repair refresh. Invoke from repo root with --path godot-client/project-sovereign --script ../../tools/godot_parse_check.gd after a headless editor/import pass if the class-name cache is missing.",
		"scripts": [],
	}
	var any_failed = false
	for script_path in SETTLEMENT_CRITICAL_SCRIPTS:
		var entry = _check_script(script_path)
		report["scripts"].append(entry)
		if not entry["parse_ok"] or not entry["load_ok"]:
			any_failed = true
			push_error("[godot_parse_check] %s failed: %s" % [script_path, entry["errors"]])
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
