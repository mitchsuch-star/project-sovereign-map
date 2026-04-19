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

# Region adjacencies (from region.py)
const REGION_CONNECTIONS = {
	"Paris": ["Normandy", "Belgium", "Lyon", "Bordeaux"],
	"Belgium": ["Paris", "Normandy", "Netherlands", "Waterloo", "Rhineland"],
	"Netherlands": ["Belgium", "Waterloo", "Hanover"],
	"Waterloo": ["Belgium", "Netherlands", "Hanover"],
	"Rhineland": ["Belgium", "Bavaria", "Lyon", "Saxony"],
	"Bavaria": ["Rhineland", "Saxony", "Vienna", "Tyrol"],
	"Vienna": ["Bavaria", "Bohemia", "Tyrol", "Milan"],
	"Lyon": ["Paris", "Bordeaux", "Marseille", "Rhineland", "Milan"],
	"Milan": ["Lyon", "Marseille", "Tyrol", "Vienna"],
	"Marseille": ["Lyon", "Bordeaux", "Milan"],
	"Brittany": ["Normandy", "Bordeaux"],
	"Bordeaux": ["Brittany", "Paris", "Lyon", "Marseille"],
	"Normandy": ["Paris", "Belgium", "Brittany"],
	"Hanover": ["Netherlands", "Waterloo", "Saxony", "Berlin"],
	"Berlin": ["Hanover", "Saxony", "Bohemia"],
	"Saxony": ["Hanover", "Berlin", "Bavaria", "Dresden", "Bohemia", "Rhineland"],
	"Dresden": ["Saxony", "Bohemia"],
	"Bohemia": ["Berlin", "Saxony", "Dresden", "Vienna"],
	"Tyrol": ["Bavaria", "Vienna", "Milan"]
}

# Color scheme — built from Utils.NATION_COLORS + connection line color (§3.3).
# Do NOT define nation colors locally; update Utils.NATION_COLORS instead.
var _colors_cache: Dictionary = {}


func _get_region_positions() -> Dictionary:
	return REGION_POSITIONS


func _get_region_connections() -> Dictionary:
	return REGION_CONNECTIONS


func _get_colors() -> Dictionary:
	if _colors_cache.is_empty():
		_colors_cache = Utils.NATION_COLORS.duplicate()
		_colors_cache["connection"] = Utils.COLOR_CONNECTION
	return _colors_cache


func _get_map_asset_definition_path() -> String:
	return PLACEHOLDER_PROVINCE_DEFINITION_PATH
