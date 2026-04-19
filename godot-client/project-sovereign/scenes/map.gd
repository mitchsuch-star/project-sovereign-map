extends "res://scenes/map_renderer_base.gd"

const PLACEHOLDER_PROVINCE_DEFINITION_PATH = "res://assets/maps/session8_placeholder_provinces.json"

# Fallback region positions for the 19-region placeholder map.
# Runtime anchor positions should come from the province-definition asset when it loads.
const REGION_POSITIONS = {
	"Paris": Vector2(300, 350),
	"Belgium": Vector2(400, 250),
	"Netherlands": Vector2(450, 150),
	"Waterloo": Vector2(500, 300),
	"Rhineland": Vector2(600, 300),
	"Bavaria": Vector2(750, 400),
	"Vienna": Vector2(1000, 450),
	"Lyon": Vector2(400, 500),
	"Marseille": Vector2(350, 650),
	"Milan": Vector2(700, 600),
	"Brittany": Vector2(150, 400),
	"Bordeaux": Vector2(200, 600),
	"Normandy": Vector2(200, 250),
	"Hanover": Vector2(650, 150),
	"Berlin": Vector2(800, 100),
	"Saxony": Vector2(700, 250),
	"Dresden": Vector2(800, 300),
	"Bohemia": Vector2(850, 200),
	"Tyrol": Vector2(800, 500)
}

# Region adjacencies come from backend `/map_topology` (§3.2).
# Do NOT re-hardcode here; update backend/models/region.py REGIONS_DATA instead.
var _region_connections: Dictionary = {}

# Color scheme — built from Utils.NATION_COLORS + connection line color (§3.3).
# Do NOT define nation colors locally; update Utils.NATION_COLORS instead.
var _colors_cache: Dictionary = {}


func _get_region_positions() -> Dictionary:
	return REGION_POSITIONS


func _get_region_connections() -> Dictionary:
	return _region_connections


func set_region_topology(topology: Dictionary) -> void:
	"""Populate adjacency from the backend /map_topology payload and rebuild visuals.

	Called once on game start (main.gd after connection test). Safe to call
	again on reconnect — _build_static_map_visuals() clears and rebuilds."""
	var connections := {}
	var regions: Dictionary = topology.get("regions", {})
	for region_name in regions:
		var entry: Dictionary = regions[region_name]
		connections[region_name] = entry.get("adjacent", [])
	_region_connections = connections
	if is_inside_tree():
		_build_static_map_visuals()


func _get_colors() -> Dictionary:
	if _colors_cache.is_empty():
		_colors_cache = Utils.NATION_COLORS.duplicate()
		_colors_cache["connection"] = Utils.COLOR_CONNECTION
	return _colors_cache


func _get_map_asset_definition_path() -> String:
	return PLACEHOLDER_PROVINCE_DEFINITION_PATH
