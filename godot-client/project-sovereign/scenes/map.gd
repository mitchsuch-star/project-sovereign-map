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

# Color scheme
const COLORS = {
	"France": Color(0.255, 0.412, 0.882),
	"Britain": Color(0.863, 0.078, 0.235),
	"Prussia": Color(0.2, 0.2, 0.2),
	"Austria": Color(1.0, 0.843, 0.0),
	"Saxony": Color(0.4, 0.6, 0.3),
	"Neutral": Color(0.565, 0.933, 0.565),
	"connection": Color(0.6, 0.6, 0.6)
}


func _get_region_positions() -> Dictionary:
	return REGION_POSITIONS


func _get_region_connections() -> Dictionary:
	return REGION_CONNECTIONS


func _get_colors() -> Dictionary:
	return COLORS


func _get_map_asset_definition_path() -> String:
	return PLACEHOLDER_PROVINCE_DEFINITION_PATH
