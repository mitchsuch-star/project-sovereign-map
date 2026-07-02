extends "res://scenes/europe_map.gd"

# Europe map smoke scene (F6) — smoke-only behaviors on top of the shared
# Europe renderer (europe_map.gd). The game map (scenes/map.gd) never runs
# this script.
#
# Map Slice 6: ownership fills are live. The registry's 1805 starting
# controllers are seeded through the SAME update_all_regions() path the game
# uses, and clicking a province cycles its owner (smoke-only G4 demo — the
# re-tint is one shader-palette upload, visible the next frame).

# Smoke-only owner-cycle order for the click demo. Names only — nation colors
# always resolve through Utils.NATION_COLORS.
const SMOKE_OWNER_CYCLE := ["France", "Britain", "Austria", "Russia", "Prussia"]

var _smoke_hover_label: Label
# The seeded political snapshot, retained so the click demo can mutate a
# province's controller and re-send the WHOLE dict through
# update_all_regions() — keeping the fill and the hover tooltip in sync.
var _seeded_map_data := {}


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
	# (the game map sends backend map_data through the same entry point).
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
