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
#
# Map Slice 6: ownership fills are live. The registry's 1805 starting
# controllers are seeded through the SAME update_all_regions() path the game
# uses, and clicking a province cycles its owner (smoke-only G4 demo — the
# re-tint is one shader-palette upload, visible the next frame).

const EUROPE_DEFINITION := "res://assets/maps/europe.json"
const EUROPE_VISUAL := "res://assets/maps/europe_visual.png"
const EUROPE_LOOKUP := "res://assets/maps/europe_lookup.png"

# Smoke-only owner-cycle order for the click demo. Names only — nation colors
# always resolve through Utils.NATION_COLORS.
const SMOKE_OWNER_CYCLE := ["France", "Britain", "Austria", "Russia", "Prussia"]

var _smoke_hover_label: Label
# The seeded political snapshot, retained so the click demo can mutate a
# province's controller and re-send the WHOLE dict through
# update_all_regions() — keeping the fill and the hover tooltip in sync.
var _seeded_map_data := {}


func _get_map_asset_definition_path() -> String:
	return EUROPE_DEFINITION


func _load_province_definition() -> Dictionary:
	# The registry keys regions by stable Region_NNN ids with the historical
	# name in a `name` field, while gameplay data from the backend is keyed by
	# name (create_europe_regions() does the same re-key server-side). Re-key
	# here so province_shapes, the color lookup, hover/click, and owner fills
	# all speak the backend's key scheme.
	# NOTE: each row's `adjacent` list still holds Region_NNN ids after the
	# re-key — Slice 7 must translate them before feeding
	# _build_connection_nodes() (the smoke draws no connections).
	var definition = super._load_province_definition()
	var regions = definition.get("regions", {})
	var renamed := {}
	for region_id in regions:
		var row: Dictionary = regions[region_id]
		renamed[str(row.get("name", region_id))] = row
	definition = definition.duplicate()
	definition["regions"] = renamed
	return definition


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
	_seed_registry_ownership()


func _seed_registry_ownership():
	# Smoke-only: paint the 1805 political snapshot from the registry's
	# starting_controller fields through the real update_all_regions() path
	# (Slice 7 sends backend map_data through the same entry point).
	_seeded_map_data = {}
	var regions: Dictionary = province_definition.get("regions", {})
	for region_name in regions:
		var row: Dictionary = regions[region_name]
		_seeded_map_data[region_name] = {
			"controller": str(row.get("starting_controller", "Neutral")),
			"terrain": str(row.get("terrain", "plains")),
			"region_type": str(row.get("region_type", "town")),
		}
	update_all_regions(_seeded_map_data)


func _on_smoke_region_hovered(region_name: String):
	_smoke_hover_label.text = region_name


func _on_smoke_region_clicked(region_name: String):
	print("[europe smoke] clicked province: ", region_name)
	_cycle_smoke_owner(region_name)


func _cycle_smoke_owner(region_name: String):
	# Smoke-only G4 demo: each click hands the province to the next nation in
	# SMOKE_OWNER_CYCLE and re-sends the whole snapshot, so the fill AND the
	# hover tooltip change together on the next frame.
	if not _seeded_map_data.has(region_name):
		return
	var current = str(_seeded_map_data[region_name].get("controller", "Neutral"))
	var next_owner: String = SMOKE_OWNER_CYCLE[0]
	var cycle_index = SMOKE_OWNER_CYCLE.find(current)
	if cycle_index != -1:
		next_owner = SMOKE_OWNER_CYCLE[(cycle_index + 1) % SMOKE_OWNER_CYCLE.size()]
	_seeded_map_data[region_name]["controller"] = next_owner
	update_all_regions(_seeded_map_data)
	print("[europe smoke] %s -> %s" % [region_name, next_owner])
	_smoke_hover_label.text = "%s -> %s" % [region_name, next_owner]
