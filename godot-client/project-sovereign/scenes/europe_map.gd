extends "res://scenes/map_renderer_base.gd"

# Europe map smoke scene.
#
# Loads the commissioned art end-to-end: the visual export (europe_visual.png)
# plus the flat region-key (europe_lookup.png) generated from `map final1.psd`'s
# County Colors layer by `tools/build_region_key_from_psd.py`, driven by the
# draft `europe.json` registry. Proves the §4.2 bitmap pipeline + pixel-perfect
# hit-testing work against real art.
#
# Region marker panels + name labels are suppressed so the scene reads as clean
# art; hover highlight + click hit-testing still work (they use the lookup image
# and province_shapes, not the marker nodes). The real wiring scope (which
# provinces become playable vs. grey "not yet in play") is decided in the map
# implementation plan — here every province renders full-color and is hoverable.

const EUROPE_DEFINITION := "res://assets/maps/europe.json"
const EUROPE_VISUAL := "res://assets/maps/europe_visual.png"
const EUROPE_LOOKUP := "res://assets/maps/europe_lookup.png"

var _smoke_hover_label: Label


func _get_map_asset_definition_path() -> String:
	return EUROPE_DEFINITION


func _get_map_visual_bitmap_path() -> String:
	return EUROPE_VISUAL


func _get_map_lookup_bitmap_path() -> String:
	return EUROPE_LOOKUP


func _get_region_positions() -> Dictionary:
	# Drive positions straight from the registry anchors so the scene scales to
	# however many provinces the PSD extraction produced (currently 126), with
	# no hardcoded position table.
	var positions := {}
	var regions: Dictionary = province_definition.get("regions", {})
	for region_name in regions:
		var anchor = regions[region_name].get("anchor", [0, 0])
		positions[region_name] = Vector2(float(anchor[0]), float(anchor[1]))
	return positions


func _build_region_nodes():
	# Smoke: suppress the per-region marker panels + name labels (designed for the
	# 19-region gameplay map; 126 of them would clutter the art). Hit-testing and
	# hover highlight do not depend on these nodes.
	pass


func _ready():
	super._ready()
	_smoke_hover_label = Label.new()
	_smoke_hover_label.name = "SmokeHoverLabel"
	_smoke_hover_label.position = Vector2(12, 64)
	_smoke_hover_label.add_theme_font_size_override("font_size", 22)
	_smoke_hover_label.add_theme_color_override("font_color", Color(1.0, 0.95, 0.7))
	_smoke_hover_label.add_theme_color_override("font_outline_color", Color.BLACK)
	_smoke_hover_label.add_theme_constant_override("outline_size", 4)
	_smoke_hover_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_smoke_hover_label.z_index = 300
	add_child(_smoke_hover_label)
	region_hovered.connect(_on_smoke_region_hovered)
	region_clicked.connect(_on_smoke_region_clicked)


func _on_smoke_region_hovered(region_name: String):
	_smoke_hover_label.text = region_name


func _on_smoke_region_clicked(region_name: String):
	print("[europe smoke] clicked province: ", region_name)
	_smoke_hover_label.text = "%s  (clicked)" % region_name
