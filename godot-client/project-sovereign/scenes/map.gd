extends Control

# Region positions from SVG map
const REGION_POSITIONS = {
	"Paris": Vector2(300, 350),
	"Belgium": Vector2(400, 250),
	"Netherlands": Vector2(450, 150),
	"Waterloo": Vector2(400, 350),
	"Rhine": Vector2(600, 300),
	"Bavaria": Vector2(750, 400),
	"Vienna": Vector2(950, 450),
	"Lyon": Vector2(500, 450),
	"Marseille": Vector2(450, 600),
	"Geneva": Vector2(600, 650),
	"Milan": Vector2(800, 600),
	"Brittany": Vector2(200, 300),
	"Bordeaux": Vector2(250, 550)
}

# Region adjacencies (from region.py)
const REGION_CONNECTIONS = {
	"Paris": ["Belgium", "Brittany", "Lyon"],
	"Belgium": ["Paris", "Netherlands", "Waterloo", "Rhine"],
	"Netherlands": ["Belgium"],
	"Waterloo": ["Belgium", "Paris"],
	"Rhine": ["Belgium", "Bavaria", "Lyon"],
	"Bavaria": ["Rhine", "Vienna", "Lyon"],
	"Vienna": ["Bavaria", "Milan"],
	"Lyon": ["Paris", "Rhine", "Bavaria", "Marseille", "Milan"],
	"Milan": ["Lyon", "Vienna", "Geneva"],
	"Marseille": ["Lyon", "Geneva"],
	"Geneva": ["Marseille", "Milan", "Bordeaux"],
	"Brittany": ["Paris", "Bordeaux"],
	"Bordeaux": ["Brittany", "Geneva"]
}

# Color scheme
const COLORS = {
	"France": Color(0.255, 0.412, 0.882),   # Royal Blue
	"Britain": Color(0.863, 0.078, 0.235),  # Crimson
	"Prussia": Color(0.2, 0.2, 0.2),        # Dark Gray (Prussian Iron)
	"Austria": Color(1.0, 0.843, 0.0),      # Gold
	"Neutral": Color(0.565, 0.933, 0.565),  # Light Green
	"connection": Color(0.6, 0.6, 0.6)      # Gray
}

# Current region states (updated from backend)
var region_controllers = {}
var region_marshals = {}

func _ready():
	# Initialize with starting state
	_initialize_map()
	queue_redraw()

func _initialize_map():
	"""Set up initial region ownership."""
	# Start with empty state - backend data is source of truth
	region_controllers = {}
	region_marshals = {}

func _draw():
	"""Draw the entire map."""
	# Draw connections first (so they're behind regions)
	_draw_connections()
	
	# Draw regions
	_draw_regions()

func _draw_connections():
	"""Draw lines showing region adjacencies."""
	var drawn_connections = []
	
	for region in REGION_CONNECTIONS:
		var start_pos = REGION_POSITIONS[region]
		
		for adjacent in REGION_CONNECTIONS[region]:
			# Avoid drawing same connection twice
			var connection_key = [region, adjacent]
			connection_key.sort()
			var connection_str = str(connection_key)
			
			if connection_str in drawn_connections:
				continue
			
			var end_pos = REGION_POSITIONS[adjacent]
			draw_line(start_pos, end_pos, COLORS["connection"], 2.0)
			drawn_connections.append(connection_str)

func _draw_regions():
	"""Draw all regions as circles."""
	for region_name in REGION_POSITIONS:
		var pos = REGION_POSITIONS[region_name]
		var controller = region_controllers.get(region_name, "Neutral")

		# DEBUG: Print controller for each region
		print("Drawing region ", region_name, ": controller = ", controller)

		# Get color with fallback warning
		var color = COLORS.get(controller)
		if color == null:
			print("⚠️  WARNING: Unknown nation '", controller, "' for region ", region_name, " - using magenta")
			color = Color(1.0, 0.0, 1.0)  # Magenta for debugging

		# Draw circle
		draw_circle(pos, 30, color)
		
		# Draw border
		if region_name == "Paris":
			# Capital gets gold border
			draw_arc(pos, 30, 0, TAU, 32, COLORS["Austria"], 3.0)
		else:
			draw_arc(pos, 30, 0, TAU, 32, Color.BLACK, 2.0)
		
		# Draw label (region name)
		var font = ThemeDB.fallback_font
		var font_size = 14
		var text_size = font.get_string_size(region_name, HORIZONTAL_ALIGNMENT_CENTER, -1, font_size)
		draw_string(font, pos - Vector2(text_size.x / 2, -5), region_name, HORIZONTAL_ALIGNMENT_CENTER, -1, font_size, Color.WHITE if controller != "Neutral" else Color.BLACK)

		# Draw marshal icons
		if region_name in region_marshals:
			var marshals = region_marshals[region_name]
			_draw_marshal_icons(pos, marshals)

func _draw_marshal_icons(region_pos: Vector2, marshals: Array):
	"""Draw marshal icons above a region."""
	var icon_size = Vector2(16, 16)
	var icon_y_offset = -50  # Above region circle
	var font = ThemeDB.fallback_font
	var name_font_size = 11

	# Calculate horizontal spacing for multiple marshals
	var num_marshals = marshals.size()
	var total_width = num_marshals * icon_size.x + (num_marshals - 1) * 8  # 8px spacing between icons
	var start_x = -total_width / 2.0

	for i in range(num_marshals):
		var marshal = marshals[i]
		var marshal_name = marshal.get("name", "?")
		var marshal_nation = marshal.get("nation", "Neutral")

		# Calculate icon position
		var icon_x_offset = start_x + i * (icon_size.x + 8)
		var icon_pos = region_pos + Vector2(icon_x_offset, icon_y_offset)

		# Get nation color
		var nation_color = COLORS.get(marshal_nation, Color(1.0, 0.0, 1.0))  # Magenta if unknown

		# Draw icon background (filled rectangle)
		draw_rect(Rect2(icon_pos, icon_size), nation_color)

		# Draw icon border
		draw_rect(Rect2(icon_pos, icon_size), Color.BLACK, false, 2.0)

		# Draw marshal name above icon
		var name_text_size = font.get_string_size(marshal_name, HORIZONTAL_ALIGNMENT_CENTER, -1, name_font_size)
		var name_pos = icon_pos + Vector2(icon_size.x / 2.0 - name_text_size.x / 2.0, -4)
		draw_string(font, name_pos, marshal_name, HORIZONTAL_ALIGNMENT_LEFT, -1, name_font_size, Color.WHITE)

func _gui_input(event):
	"""Handle clicks on regions."""
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		var click_pos = event.position
		
		# Check which region was clicked
		for region_name in REGION_POSITIONS:
			var region_pos = REGION_POSITIONS[region_name]
			var distance = click_pos.distance_to(region_pos)
			
			if distance <= 30:  # Within region circle
				_on_region_clicked(region_name)
				break

func _on_region_clicked(region_name: String):
	"""Handle region click."""
	print("Clicked region: ", region_name)
	# TODO: Emit signal to main script
	# emit_signal("region_selected", region_name)

func update_region(region_name: String, controller: String, marshal: String = ""):
	"""Update a region's state (called from backend response)."""
	if region_name in REGION_POSITIONS:
		region_controllers[region_name] = controller
		
		if marshal:
			region_marshals[region_name] = marshal
		elif region_name in region_marshals:
			region_marshals.erase(region_name)
		
		queue_redraw()

func update_all_regions(map_data: Dictionary):
	"""Update all regions from backend map data."""
	print("═══════════════════════════════════════")
	print("MAP: update_all_regions() called")
	print("Received ", map_data.keys().size(), " regions")
	print("═══════════════════════════════════════")

	for region_name in map_data:
		var data = map_data[region_name]

		# Handle null controller (backend sends null for neutral regions)
		var controller = data.get("controller", "Neutral")
		if controller == null:
			controller = "Neutral"

		# Update controller
		region_controllers[region_name] = controller

		# Update marshals (array of {name, nation})
		var marshals = data.get("marshals", [])
		if marshals.size() > 0:
			region_marshals[region_name] = marshals
			print("Map updating region ", region_name, ": controller = ", controller, ", marshals = ", marshals)
		else:
			region_marshals.erase(region_name)
			print("Map updating region ", region_name, ": controller = ", controller, ", no marshals")

	# Trigger redraw
	queue_redraw()

	print("═══════════════════════════════════════")
	print("MAP: Update complete, triggering redraw")
	print("═══════════════════════════════════════")
