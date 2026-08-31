extends SceneTree
# REV visual-signoff harness (windowed, NOT --headless — the viewport has to
# render for get_texture() to return pixels):
#
#   <godot> --path godot-client/project-sovereign \
#           --script ../../tools/rev_visual_screenshot.gd
#
# The Aug 30, 2026 whole-systems review changed four client surfaces. Two of
# them are a RENDER and can be signed off from a picture; this harness draws
# both from REAL backend payloads, deterministically, instead of wrestling a
# live viewport into showing the right province at the right moment.
#
#   1. `region_panel.tscn` — the levy row. The panel used to quote
#      `levy_status.infantry_price`, which `get_levy_status` prices at the
#      CAPITAL, on the same row as chips that recruit in THIS province. The
#      payload now carries `recruit_price_here` and the row says "…g per
#      10,000 foot HERE". The shot must show the LOCAL figure.
#
#   2. `notification_bar.tscn` — the `buildings_damaged` pill. The producer
#      shipped in the [V-6] damage slice and the renderer join was never
#      made, so a wrecked market arrived as the anonymous priority pill
#      "INF". The shot must show "DMG".
#
# Payloads are read from res:// so no permission dance is needed:
#   res://rev_region.json   — one region dict from GET /test's map_data
#   res://rev_levy.json     — the `levy_status` block
#   res://rev_rows.json     — a notifications array
# Capture them against a SANDBOXED backend (never the player's 8005) — see
# the REV landing record. They are NOT committed; delete after the run.

const SHOT_REGION := "user://rev_region_panel.png"
const SHOT_RAIL := "user://rev_rail.png"
const MEASURED := "user://rev_measured.json"

var _frames := 0
var _panel = null
var _bar = null
var _measured := {}


func _init():
	process_frame.connect(_tick)


func _tick():
	_frames += 1
	if _frames == 1:
		root.mode = Window.MODE_WINDOWED
		root.size = Vector2i(1280, 760)
		return
	if _frames == 3:
		_build_region_panel()
		return
	if _frames == 25:
		_shoot_region()
		return
	if _frames == 27:
		_build_rail()
		return
	if _frames == 50:
		_shoot_rail()
		return
	if _frames == 52:
		_finish()
		return


func _read(path: String):
	var f = FileAccess.open(path, FileAccess.READ)
	if f == null:
		return null
	var parsed = JSON.parse_string(f.get_as_text())
	f.close()
	return parsed


# ── 1. the region panel's levy row ──────────────────────────────────────

class _MapStub extends Node:
	var region_full_data := {}
	var region_visibility := {}
	var region_marshals := {}
	var region_garrisons := {}
	var levy_status := {}


func _build_region_panel():
	var region = _read("res://rev_region.json")
	var levy = _read("res://rev_levy.json")
	if region == null or levy == null:
		printerr("REV-HARNESS: rev_region.json / rev_levy.json missing")
		quit(2)
		return

	var stub = _MapStub.new()
	var name_str := str(region.get("name", "Berry"))
	stub.region_full_data[name_str] = region
	stub.region_visibility[name_str] = "full"
	stub.region_marshals[name_str] = []
	stub.region_garrisons[name_str] = {}
	stub.levy_status = levy
	root.add_child(stub)

	var scene = load("res://scenes/region_panel.tscn")
	_panel = scene.instantiate()
	root.add_child(_panel)
	_panel.show_region(name_str, stub)

	_measured["region"] = {
		"region": name_str,
		"recruit_price_here": region.get("recruit_price_here"),
		"capital_price": levy.get("infantry_price"),
		"over_by": levy.get("over_by"),
		"headroom": levy.get("headroom"),
	}


func _shoot_region():
	root.get_texture().get_image().save_png(SHOT_REGION)
	# Read the rendered text back, so the sign-off is not "a human squinted".
	var content = _panel.get_node("PanelContainer/VBoxContainer/Scroll/ContentArea")
	var body := str(content.text)
	_measured["region"]["rendered_contains_local_price"] = body.contains(
		str(int(_measured["region"]["recruit_price_here"])))
	_measured["region"]["rendered_contains_capital_price"] = body.contains(
		str(int(_measured["region"]["capital_price"])))
	_measured["region"]["rendered_says_here"] = body.contains("foot here")
	_panel.visible = false


# ── 2. the buildings_damaged rail pill ──────────────────────────────────

func _build_rail():
	var rows = _read("res://rev_rows.json")
	if not (rows is Array):
		printerr("REV-HARNESS: rev_rows.json missing or not an array")
		quit(2)
		return
	var scene = load("res://scenes/notification_bar.tscn")
	_bar = scene.instantiate()
	root.add_child(_bar)
	_bar.set_anchors_preset(Control.PRESET_TOP_WIDE)
	_bar.position = Vector2(0, 12)
	_bar.size = Vector2(1280, 60)
	_bar.update_notifications(rows)


func _shoot_rail():
	root.get_texture().get_image().save_png(SHOT_RAIL)
	var icons: Node = _bar.get_node("RailPanel/RailLayout/IconContainer")
	var pills := []
	for child in icons.get_children():
		var notif = child.get_meta("notification_data", {})
		pills.append({
			"type": (str(notif.get("type", "")) if notif is Dictionary else ""),
			"text": str(child.text),
		})
	_measured["rail"] = {"pills": pills}


func _finish():
	var f = FileAccess.open(MEASURED, FileAccess.WRITE)
	f.store_string(JSON.stringify(_measured, "  "))
	f.close()
	print("REV-HARNESS: wrote ", SHOT_REGION, " ", SHOT_RAIL, " ", MEASURED)
	quit(0)
