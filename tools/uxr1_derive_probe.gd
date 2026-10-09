extends SceneTree
# UXR-1 — the derivation twins, DRIVEN (tests/test_uxr1_scale_fix.py).
#
#   $env:UXR1_PROBE_TABLE = "<abs path to a JSON list of [width, height, dpi]>"
#   $env:UXR1_PROBE_OUT   = "<abs path for the result JSON>"
#   <godot> --headless --path godot-client/project-sovereign \
#           --script ../../tools/uxr1_derive_probe.gd
#
# Runs `UiSettings.derive_ui_scale_for` over the table and writes the scales
# out, so the test can hold the GDScript formula and its Python twin
# (`tools/uxr0_readability_report.py` derive_ui_scale) to the same numbers.
# No screen is read — `derive_ui_scale_for` is the pure half; a headless run
# of `derive_default_ui_scale` would only prove the no-screen floor.

func _init():
	var table_path := OS.get_environment("UXR1_PROBE_TABLE")
	var out_path := OS.get_environment("UXR1_PROBE_OUT")
	var out := {"rows": [], "max": UiSettings.MAX_UI_SCALE, "min": UiSettings.MIN_UI_SCALE,
			"no_screen": UiSettings.derive_ui_scale_for(0, 0, 96.0)}
	var table = JSON.parse_string(FileAccess.get_file_as_string(table_path)) if table_path != "" else null
	if table is Array:
		for row in table:
			if row is Array and row.size() >= 3:
				out["rows"].append({
					"width": int(row[0]), "height": int(row[1]), "dpi": float(row[2]),
					"scale": UiSettings.derive_ui_scale_for(int(row[0]), int(row[1]), float(row[2])),
				})
	if out_path != "":
		var f := FileAccess.open(out_path, FileAccess.WRITE)
		if f != null:
			f.store_string(JSON.stringify(out, "  "))
			f.close()
	quit(0)
