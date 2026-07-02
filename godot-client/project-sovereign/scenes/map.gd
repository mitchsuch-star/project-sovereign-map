extends "res://scenes/europe_map.gd"

# The live game map (Map Slice 7 cutover): main.tscn's MapArea renders the
# 126-province Europe world through the shared Europe renderer
# (europe_map.gd — commissioned bitmap art, registry anchors, owner-fill
# shader, hover/click hit-testing). This script adds only the game glue:
# the backend topology handoff and the shared color scheme. The 19-region
# circle placeholder this file used to hold is retired from the game path.

# Region adjacencies come from backend `/map_topology` (§3.2, name-keyed since
# Map Slice 5). Do NOT re-hardcode adjacency or positions here — positions come
# from the registry anchors, and the connection lines drawn on the bitmap map
# are the registry's hand-authored sea links (see europe_map.gd).
var _region_topology: Dictionary = {}

# Color scheme — built from Utils.NATION_COLORS + connection line color (§3.3).
# Do NOT define nation colors locally; update Utils.NATION_COLORS instead.
var _colors_cache: Dictionary = {}


func set_region_topology(topology: Dictionary) -> void:
	"""Store adjacency from the backend /map_topology payload and rebuild visuals.

	Called once on game start (main.gd after connection test). Safe to call
	again on reconnect — _build_static_map_visuals() clears and rebuilds."""
	var connections := {}
	var regions: Dictionary = topology.get("regions", {})
	for region_name in regions:
		var entry: Dictionary = regions[region_name]
		connections[region_name] = entry.get("adjacent", [])
	_region_topology = connections
	if is_inside_tree():
		_build_static_map_visuals()


func _get_colors() -> Dictionary:
	if _colors_cache.is_empty():
		_colors_cache = Utils.NATION_COLORS.duplicate()
		_colors_cache["connection"] = Utils.COLOR_CONNECTION
	return _colors_cache
