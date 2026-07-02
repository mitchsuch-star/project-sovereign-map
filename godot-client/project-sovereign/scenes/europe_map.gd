extends "res://scenes/map_renderer_base.gd"

# Shared Europe renderer (Map Slices 6-7).
#
# Loads the commissioned art end-to-end: the visual export (europe_visual.png)
# plus the flat region-key (europe_lookup.png) generated from `map final1.psd`'s
# County Colors layer by `tools/build_region_key_from_psd.py`, driven by the
# `europe.json` registry. Provides the §4.2 bitmap pipeline + pixel-perfect
# hit-testing + Slice 6 owner fills for BOTH consumers:
#   - scenes/map.gd            — the live game map (main.tscn MapArea, Slice 7)
#   - scenes/europe_map_smoke.gd — the F6 smoke scene (seed + owner-cycle demo)
#
# Region marker panels + name labels are suppressed (126 of them would bury the
# art); hover highlight + click hit-testing still work (they use the lookup
# image and province_shapes, not the marker nodes), and hover tooltips carry
# the province names. Connection lines are the registry's hand-authored sea
# links ONLY — land adjacency reads as shared borders on the art itself.

const EUROPE_DEFINITION := "res://assets/maps/europe.json"
const EUROPE_VISUAL := "res://assets/maps/europe_visual.png"
const EUROPE_LOOKUP := "res://assets/maps/europe_lookup.png"

# Region_NNN id -> historical name, retained from the re-key so sea links (and
# any other id-keyed registry data) can be translated to the backend's
# name-keyed scheme.
var _region_id_to_name := {}


func _get_map_asset_definition_path() -> String:
	return EUROPE_DEFINITION


func _load_province_definition() -> Dictionary:
	# The registry keys regions by stable Region_NNN ids with the historical
	# name in a `name` field, while gameplay data from the backend is keyed by
	# name (create_europe_regions() does the same re-key server-side). Re-key
	# here so province_shapes, the color lookup, hover/click, and owner fills
	# all speak the backend's key scheme.
	# NOTE: each row's `adjacent` list still holds Region_NNN ids after the
	# re-key — it is never fed to _build_connection_nodes(); drawn connections
	# come from the top-level `sea_links` via _get_region_connections().
	var definition = super._load_province_definition()
	var regions = definition.get("regions", {})
	var renamed := {}
	_region_id_to_name = {}
	for region_id in regions:
		var row: Dictionary = regions[region_id]
		var region_name := str(row.get("name", region_id))
		renamed[region_name] = row
		_region_id_to_name[str(region_id)] = region_name
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


func _get_region_connections() -> Dictionary:
	# Bitmap map: land adjacency reads as shared borders on the art — drawing
	# all 248 land edges would bury it. Only the registry's hand-authored sea
	# links (invisible on the art, gameplay-walkable — e.g. London<->Flanders)
	# get connection lines. `sea_links` holds numeric Region_NNN index pairs;
	# translate through the retained id->name map so the segments speak the
	# backend's name-keyed scheme. DEF-7 registry edits flow through untouched.
	var connections := {}
	for pair in province_definition.get("sea_links", []):
		if not (pair is Array) or pair.size() != 2:
			continue
		var a: String = _region_id_to_name.get("Region_%03d" % int(pair[0]), "")
		var b: String = _region_id_to_name.get("Region_%03d" % int(pair[1]), "")
		if a == "" or b == "":
			continue
		if not connections.has(a):
			connections[a] = []
		connections[a].append(b)
	return connections


func _build_region_nodes():
	# Suppress the per-region marker panels + name labels (designed for the
	# 19-region circle map; 126 of them would clutter the art). Hit-testing,
	# hover highlight, tooltips, owner fills, and force/garrison markers do not
	# depend on these nodes.
	pass
