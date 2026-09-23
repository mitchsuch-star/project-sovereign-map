extends SceneTree
# NUI "The Admiralty on the Map" — the top bar, DRIVEN headless at several
# logical viewport sizes (IQ10-X1's completion: no BaseButton of the bar lies
# outside the logical viewport at Interface Scale 2.0, whose logical viewport
# is 800x450).
#
#   $env:NUI_SPEC = "<absolute path to a spec JSON>"
#   <godot> --headless --path godot-client/project-sovereign \
#           --script ../../tools/nui_top_bar_harness.gd
#
# Spec: {"sizes": [[1600, 900], [800, 450]],
#        "diplomatic_fields": <the update_diplomatic_fields payload>,
#        "admiralty": <naval_overlay.player_summary>,
#        "out": <abs path of the result JSON>}
#
# For each size the ROOT WINDOW is resized, the REAL top_bar.tscn is
# instantiated, fed through its own `update_diplomatic_fields` /
# `update_admiralty`, and after a few frames every BaseButton's global rect,
# text, tooltip and visibility are recorded beside the viewport size and the
# bar's own `is_compact()`. A pytest reads the JSON; nothing here decides
# what the bar says.
#
# Safety rails (IQ-10's): UiSettings is shimmed onto an in-memory ConfigFile
# before any scene loads, no setter is called, and the result JSON is written
# on every exit path.

const FRAME_LIMIT := 900
const SETTLE := 8

var _frames := 0
var _phase := "boot"
var _spec: Dictionary = {}
var _sizes: Array = []
var _size_i := 0
var _wait := 0
var _bar = null
var _result: Dictionary = {"runs": []}


func _init():
	UiSettings._cfg = ConfigFile.new()
	process_frame.connect(_tick)


func _tick():
	_frames += 1
	if _frames > FRAME_LIMIT:
		_result["error"] = "frame limit hit in phase " + _phase
		_finish()
		return
	match _phase:
		"boot":
			var path := OS.get_environment("NUI_SPEC")
			if path == "":
				_result["error"] = "NUI_SPEC is not set"
				_finish()
				return
			var parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
			if not (parsed is Dictionary):
				_result["error"] = "the spec at " + path + " is not a JSON object"
				_finish()
				return
			_spec = parsed
			_sizes = _spec.get("sizes", [[1600, 900], [800, 450]])
			_phase = "resize"
		"resize":
			if _size_i >= _sizes.size():
				_finish()
				return
			var sz = _sizes[_size_i]
			root.size = Vector2i(int(sz[0]), int(sz[1]))
			_wait = 2
			_phase = "spawn"
		"spawn":
			_wait -= 1
			if _wait > 0:
				return
			_bar = load("res://scenes/top_bar.tscn").instantiate()
			root.add_child(_bar)
			_wait = 2
			_phase = "feed"
		"feed":
			_wait -= 1
			if _wait > 0:
				return
			var fields = _spec.get("diplomatic_fields", {})
			if fields is Dictionary and _bar.has_method("update_diplomatic_fields"):
				_bar.update_diplomatic_fields(fields)
			var adm = _spec.get("admiralty", {})
			if adm is Dictionary and _bar.has_method("update_admiralty"):
				_bar.update_admiralty(adm)
			_wait = SETTLE
			_phase = "record"
		"record":
			_wait -= 1
			if _wait > 0:
				return
			var run := {
				"size": [int(root.size.x), int(root.size.y)],
				"viewport": [root.get_visible_rect().size.x, root.get_visible_rect().size.y],
				"compact": bool(_bar.is_compact()) if _bar.has_method("is_compact") else null,
				"buttons": [],
				"labels": [],
			}
			_walk(_bar, run)
			_result["runs"].append(run)
			_bar.queue_free()
			_bar = null
			_size_i += 1
			_wait = 3
			_phase = "teardown"
		"teardown":
			_wait -= 1
			if _wait > 0:
				return
			_phase = "resize"


func _walk(node: Node, run: Dictionary) -> void:
	if node is BaseButton:
		var b: BaseButton = node
		var r: Rect2 = b.get_global_rect()
		run["buttons"].append({
			"name": b.name,
			"text": b.text if "text" in b else "",
			"tooltip": b.tooltip_text,
			"visible": b.is_visible_in_tree(),
			"rect": [r.position.x, r.position.y, r.size.x, r.size.y],
		})
	elif node is Label:
		var l: Label = node
		var r2: Rect2 = l.get_global_rect()
		run["labels"].append({
			"name": l.name, "text": l.text, "visible": l.is_visible_in_tree(),
			"rect": [r2.position.x, r2.position.y, r2.size.x, r2.size.y],
		})
	for child in node.get_children():
		_walk(child, run)


func _finish():
	var out := str(_spec.get("out", ""))
	if out == "":
		out = OS.get_environment("NUI_OUT")
	if out != "":
		var f := FileAccess.open(out, FileAccess.WRITE)
		if f != null:
			f.store_string(JSON.stringify(_result))
			f.close()
	quit(0 if not _result.has("error") else 1)
