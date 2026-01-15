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
	"Paris": ["Belgium", "Waterloo", "Brittany", "Lyon"],
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

# Mouse tracking for hover tooltips
var mouse_position: Vector2 = Vector2.ZERO
var hovered_marshal: Dictionary = {}  # Stores marshal data when hovering

# Camera/zoom control variables
var zoom_level: float = 1.0
var target_zoom: float = 1.0
var min_zoom: float = 0.5
var max_zoom: float = 2.0
var pan_offset: Vector2 = Vector2.ZERO
var is_panning: bool = false
var pan_start_pos: Vector2 = Vector2.ZERO
var zoom_tween: Tween = null
var is_zooming: bool = false

# Pan speeds
const PAN_SPEED_KEYS: float = 300.0  # pixels per second with arrow keys
const ZOOM_SPEED: float = 0.1  # zoom increment per wheel notch
const ZOOM_DURATION: float = 0.2  # seconds for smooth zoom transition

func _ready():
	# Initialize with starting state
	_initialize_map()

	# Center camera on map
	# Map bounds approximately: x(200-950), y(150-650)
	var map_center = Vector2(575, 400)
	var viewport_size = size
	if viewport_size.x > 0 and viewport_size.y > 0:
		pan_offset = (viewport_size / 2) - map_center

	queue_redraw()

func _initialize_map():
	"""Set up initial region ownership."""
	# Start with empty state - backend data is source of truth
	region_controllers = {}
	region_marshals = {}

func _get_map_mouse_position() -> Vector2:
	"""Convert screen mouse position to map coordinates accounting for zoom and pan."""
	return (mouse_position - pan_offset) / zoom_level

func _process(delta: float):
	"""Handle arrow key panning and continuous zoom redraws."""
	# Redraw continuously during zoom animation
	if is_zooming:
		queue_redraw()

	# Arrow key panning
	var pan_input = Vector2.ZERO

	# Check arrow key inputs
	if Input.is_action_pressed("ui_left"):
		pan_input.x += 1
	if Input.is_action_pressed("ui_right"):
		pan_input.x -= 1
	if Input.is_action_pressed("ui_up"):
		pan_input.y += 1
	if Input.is_action_pressed("ui_down"):
		pan_input.y -= 1

	# Apply panning
	if pan_input != Vector2.ZERO:
		pan_offset += pan_input * PAN_SPEED_KEYS * delta
		queue_redraw()

func _draw():
	"""Draw the entire map."""
	# Reset hovered marshal at start of each frame
	hovered_marshal = {}

	# Apply camera transformations (pan and zoom)
	draw_set_transform(pan_offset, 0.0, Vector2(zoom_level, zoom_level))

	# Draw connections first (so they're behind regions)
	_draw_connections()

	# Draw regions
	_draw_regions()

	# Reset transform for UI elements (tooltip in screen space)
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)

	# Draw tooltip last (on top of everything, in screen space)
	if hovered_marshal.size() > 0:
		_draw_tooltip()

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

		# VERTICAL NAME STACKING - Fix overlap
		# First marshal at -4, each additional stacks below at -4 - (index * 14)
		var name_y_offset = -4 - (i * 14)
		var name_text_size = font.get_string_size(marshal_name, HORIZONTAL_ALIGNMENT_CENTER, -1, name_font_size)
		var name_pos = icon_pos + Vector2(icon_size.x / 2.0 - name_text_size.x / 2.0, name_y_offset)
		draw_string(font, name_pos, marshal_name, HORIZONTAL_ALIGNMENT_LEFT, -1, name_font_size, Color.WHITE)

		# HOVER DETECTION - Check if mouse is over this icon
		var icon_rect = Rect2(icon_pos, icon_size)
		var map_mouse_pos = _get_map_mouse_position()
		if icon_rect.has_point(map_mouse_pos):
			# Store hovered marshal data for tooltip
			hovered_marshal = marshal

func _gui_input(event):
	"""Handle clicks, mouse motion, zoom, and pan."""
	# Track mouse position for hover detection
	if event is InputEventMouseMotion:
		mouse_position = event.position

		# Handle middle mouse drag for panning
		if is_panning:
			var delta = event.position - pan_start_pos
			pan_offset += delta
			pan_start_pos = event.position

		queue_redraw()  # Redraw to update tooltip/pan

	# Handle mouse button events
	if event is InputEventMouseButton and event.pressed:
		# Mouse wheel zoom
		if event.button_index == MOUSE_BUTTON_WHEEL_UP:
			_zoom_at_point(event.position, 1 + ZOOM_SPEED)
			return
		elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			_zoom_at_point(event.position, 1 - ZOOM_SPEED)
			return

		# Middle mouse button for panning
		elif event.button_index == MOUSE_BUTTON_MIDDLE:
			is_panning = true
			pan_start_pos = event.position
			return

	# Handle mouse button release
	if event is InputEventMouseButton and not event.pressed:
		if event.button_index == MOUSE_BUTTON_MIDDLE:
			is_panning = false
			return

	# Handle region clicks
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		var map_click_pos = _get_map_mouse_position()

		# Check which region was clicked
		for region_name in REGION_POSITIONS:
			var region_pos = REGION_POSITIONS[region_name]
			var distance = map_click_pos.distance_to(region_pos)

			if distance <= 30:  # Within region circle
				_on_region_clicked(region_name)
				break

func _on_region_clicked(region_name: String):
	"""Handle region click."""
	print("Clicked region: ", region_name)
	# TODO: Emit signal to main script
	# emit_signal("region_selected", region_name)

func _zoom_at_point(point: Vector2, zoom_factor: float):
	"""Zoom smoothly at a specific point (keeps point under cursor)."""
	var new_zoom = clamp(zoom_level * zoom_factor, min_zoom, max_zoom)

	if new_zoom == zoom_level:
		return  # Already at limit

	# Calculate the point in map coordinates before zoom
	var map_point_before = (point - pan_offset) / zoom_level

	# Kill existing zoom tween
	if zoom_tween:
		zoom_tween.kill()

	# Set zooming flag for continuous redraws
	is_zooming = true

	# Create smooth zoom transition
	zoom_tween = create_tween()
	zoom_tween.set_parallel(true)

	# Animate zoom
	zoom_tween.tween_property(self, "zoom_level", new_zoom, ZOOM_DURATION).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)

	# Adjust pan to keep the point under cursor
	var map_point_after = (point - pan_offset) / new_zoom
	var pan_adjustment = (map_point_after - map_point_before) * new_zoom
	var new_pan = pan_offset + pan_adjustment
	zoom_tween.tween_property(self, "pan_offset", new_pan, ZOOM_DURATION).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)

	# Clear zooming flag when finished
	zoom_tween.finished.connect(func(): is_zooming = false)

func _draw_tooltip():
	"""Draw tooltip panel showing marshal details."""
	# Tooltip dimensions
	var tooltip_size = Vector2(200, 120)
	var tooltip_pos = mouse_position + Vector2(15, 15)  # Offset from cursor
	var padding = 10

	# Draw semi-transparent dark panel
	var panel_color = Color(0.1, 0.1, 0.15, 0.95)
	draw_rect(Rect2(tooltip_pos, tooltip_size), panel_color)

	# Draw white border
	draw_rect(Rect2(tooltip_pos, tooltip_size), Color.WHITE, false, 2.0)

	# Get marshal data
	var marshal_name = hovered_marshal.get("name", "Unknown")
	var marshal_nation = hovered_marshal.get("nation", "Neutral")
	var strength = hovered_marshal.get("strength", 0)
	var morale = hovered_marshal.get("morale", 0)
	var movement_range = hovered_marshal.get("movement_range", 1)

	# Font setup
	var font = ThemeDB.fallback_font
	var line_spacing = 16
	var text_x = tooltip_pos.x + padding
	var text_y = tooltip_pos.y + padding

	# Line 1: Marshal name (size 14, white)
	draw_string(font, Vector2(text_x, text_y + 14), marshal_name, HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color.WHITE)
	text_y += line_spacing + 4  # Extra spacing after name

	# Line 2: Nation (size 11, gray)
	draw_string(font, Vector2(text_x, text_y + 11), marshal_nation, HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color(0.7, 0.7, 0.7))
	text_y += line_spacing + 4  # Extra spacing before stats

	# Line 3: Troops (formatted with commas)
	var troops_text = "Troops: " + _format_number(strength)
	draw_string(font, Vector2(text_x, text_y + 11), troops_text, HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color.WHITE)
	text_y += line_spacing

	# Line 4: Morale
	var morale_text = "Morale: " + str(morale) + "%"
	draw_string(font, Vector2(text_x, text_y + 11), morale_text, HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color.WHITE)
	text_y += line_spacing

	# Line 5: Movement range
	var movement_text = "Movement: Range " + str(movement_range)
	draw_string(font, Vector2(text_x, text_y + 11), movement_text, HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color.WHITE)

func _format_number(num: int) -> String:
	"""Format number with comma separators (72000 → 72,000)."""
	var num_str = str(num)
	var result = ""
	var count = 0

	# Process string from right to left
	for i in range(num_str.length() - 1, -1, -1):
		if count == 3:
			result = "," + result
			count = 0
		result = num_str[i] + result
		count += 1

	return result

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
