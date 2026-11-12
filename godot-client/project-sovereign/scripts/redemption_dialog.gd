extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Marshal Redemption Dialog
# =============================================================================
# Displays when a marshal's trust drops to critical levels (≤ 20)
# Player chooses: Grant Autonomy, Administrative Role, or Dismiss
#
# Options are dynamically shown/hidden based on availability from backend:
# - Grant Autonomy: Always available
# - Administrative Role: Only if ≥2 field marshals AND no existing admin
# - Dismiss: Only if ≥2 field marshals
# =============================================================================

signal choice_made(choice: String)

# UI References
@onready var panel_container = $PanelContainer
@onready var marshal_name_label = $PanelContainer/VBoxContainer/MarshalNameLabel
@onready var message_label = $PanelContainer/VBoxContainer/MessageLabel
@onready var trust_label = $PanelContainer/VBoxContainer/StatsContainer/TrustLabel
@onready var autonomy_button = $PanelContainer/VBoxContainer/ButtonContainer/AutonomyButton
@onready var dismiss_button = $PanelContainer/VBoxContainer/ButtonContainer/DismissButton
@onready var admin_button = $PanelContainer/VBoxContainer/ButtonContainer/AdminButton

var current_marshal: String = ""
# FA-D5 (slice 17, Phase 2): the arm that pays him — built from the payload
# like the others, first in the column, hidden until the audience offers it.
var settle_button: Button = null

# Napoleonic color palette
const COLOR_TEXT = "eee"
const COLOR_WARNING = "cd6b6b"
const COLOR_PANEL = "1a1a2e"

func _ready():
	# Connect button signals
	autonomy_button.pressed.connect(_on_autonomy_pressed)
	dismiss_button.pressed.connect(_on_dismiss_pressed)
	admin_button.pressed.connect(_on_admin_pressed)
	settle_button = Button.new()
	settle_button.name = "SettleButton"
	# Session UI-2: the arm wears the same step and height as its column.
	settle_button.theme_type_variation = autonomy_button.theme_type_variation
	settle_button.custom_minimum_size = autonomy_button.custom_minimum_size
	settle_button.visible = false
	settle_button.pressed.connect(_on_settle_pressed)
	var _column = autonomy_button.get_parent()
	_column.add_child(settle_button)
	_column.move_child(settle_button, 0)

	# Hide by default
	hide()

func show_redemption(redemption_data: Dictionary):
	"""Display redemption dialog with data from backend."""
	print("REDEMPTION DIALOG: show_redemption() called")
	print("  Data: ", redemption_data)

	current_marshal = redemption_data.get("marshal", "Marshal")

	# Set marshal name header
	marshal_name_label.text = "%s REQUESTS AUDIENCE" % current_marshal.to_upper()
	# Session UI-2: the trust glyph over the header — a marshal's loyalty is
	# what is asked.
	_arms_row([{"glyph": "trust"}])

	# Set message
	var message = redemption_data.get("message", "Our relationship has broken down, Sire. Something must change.")
	message_label.text = '"%s"' % message

	# Get trust value
	var trust = int(redemption_data.get("trust", 20))
	trust_label.text = "Trust: %d (Critical)" % trust

	# ════════════════════════════════════════════════════════════════════════════
	# DYNAMIC BUTTON VISIBILITY - Show only available options
	# ════════════════════════════════════════════════════════════════════════════
	var options = redemption_data.get("options", [])
	var available_ids = []

	# Collect available option IDs and update button text
	for opt in options:
		var opt_id = opt.get("id", "")
		var opt_text = opt.get("text", "")
		var opt_desc = opt.get("description", "")
		available_ids.append(opt_id)

		match opt_id:
			"settle_account":
				settle_button.text = opt_text if opt_text else "Settle his account (a rente)"
				settle_button.tooltip_text = opt_desc
			"grant_autonomy":
				autonomy_button.text = opt_text if opt_text else "Grant Autonomy (3 turns)"
				autonomy_button.tooltip_text = opt_desc
			"administrative_role":
				admin_button.text = opt_text if opt_text else "Transfer to Staff (+1 action)"
				admin_button.tooltip_text = opt_desc
			"dismiss":
				dismiss_button.text = opt_text if opt_text else "Dismiss Marshal"
				dismiss_button.tooltip_text = opt_desc

	# Show/hide buttons based on availability
	settle_button.visible = "settle_account" in available_ids
	autonomy_button.visible = "grant_autonomy" in available_ids
	admin_button.visible = "administrative_role" in available_ids
	dismiss_button.visible = "dismiss" in available_ids

	print("REDEMPTION DIALOG: Available options: ", available_ids)
	print("REDEMPTION DIALOG: Autonomy visible: ", autonomy_button.visible)
	print("REDEMPTION DIALOG: Admin visible: ", admin_button.visible)
	print("REDEMPTION DIALOG: Dismiss visible: ", dismiss_button.visible)

	# Show the dialog
	print("REDEMPTION DIALOG: Showing dialog...")
	show()
	# July 18, 2026 viewport sweep: fit to the CURRENT logical viewport.
	# Interface Scale (content_scale_factor, up to 2.0) divides the logical
	# viewport, so a fixed authored rect can carry the action row off-screen
	# and leave a modal undismissable. The helper is a no-op wherever the
	# panel already fits, and returns early for non-centre-anchored panels.
	Utils.clamp_centered_panel($PanelContainer)
	# Session UI-2: then shrink to the content (the authored 440 stood over a
	# band of empty panel when fewer arms are offered).
	Utils.shrink_centered_panel_to_content($PanelContainer)
	print("REDEMPTION DIALOG: visible = ", visible)

func refit() -> void:
	"""UXR-2's live-refit hook (`Utils.refit_surface`): the clamp, then the
	shrink to content, exactly as on open."""
	Utils.clamp_centered_panel($PanelContainer)
	Utils.shrink_centered_panel_to_content($PanelContainer)

func _on_settle_pressed():
	"""FA-D5: the player pays him — the executor prices and gates it."""
	hide()
	choice_made.emit("settle_account")

func _on_autonomy_pressed():
	"""Player grants marshal autonomy."""
	hide()
	choice_made.emit("grant_autonomy")

func _on_admin_pressed():
	"""Player transfers marshal to administrative role."""
	hide()
	choice_made.emit("administrative_role")

func _on_dismiss_pressed():
	"""Player dismisses the marshal."""
	hide()
	choice_made.emit("dismiss")


func _arms_row(parts: Array) -> void:
	"""Session UI-2: the arms the voice speaks under (a court's flag, an
	office's glyph, the Empire's eagle) in one centred row above the title;
	an empty list hides the row. Built once, refilled on every show."""
	var vb: VBoxContainer = $PanelContainer/VBoxContainer
	var row: HBoxContainer = vb.get_node_or_null("ArmsRow") as HBoxContainer
	if row == null:
		row = HBoxContainer.new()
		row.name = "ArmsRow"
		row.alignment = BoxContainer.ALIGNMENT_CENTER
		row.add_theme_constant_override("separation", 12)
		row.mouse_filter = Control.MOUSE_FILTER_IGNORE
		vb.add_child(row)
		vb.move_child(row, 0)
	for c in row.get_children():
		row.remove_child(c)
		c.queue_free()
	for part in parts:
		var tex_path: String = ""
		var tint: Color = Color.WHITE
		var h: float = 26.0
		if part.has("flag"):
			tex_path = Utils.nation_flag_path(str(part["flag"]))
		elif part.has("glyph"):
			tex_path = Utils.glyph(str(part["glyph"]))
			tint = Utils.UI_GOLD
		elif part.has("eagle"):
			tex_path = Utils.EAGLE
			tint = Color(Utils.UI_GOLD, 0.92)
			h = 44.0
		if tex_path == "" or not ResourceLoader.exists(tex_path):
			continue
		var tex: Texture2D = load(tex_path)
		if tex == null or tex.get_height() <= 0:
			continue
		var art := TextureRect.new()
		art.texture = tex
		art.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		art.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		art.custom_minimum_size = Vector2(h * float(tex.get_width()) / float(tex.get_height()), h)
		art.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		art.modulate = tint
		art.mouse_filter = Control.MOUSE_FILTER_IGNORE
		row.add_child(art)
	# the compact view (Interface Scale 2.0) keeps its room for the answers
	row.visible = row.get_child_count() > 0 and not Utils.compact_view()
