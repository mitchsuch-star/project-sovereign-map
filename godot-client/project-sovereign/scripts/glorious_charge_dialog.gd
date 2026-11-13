extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Glorious Charge Dialog
# =============================================================================
# Displays when a reckless cavalry marshal (Ney) reaches recklessness 3
# Player chooses: Execute Glorious Charge (2x damage) or Normal Attack
# =============================================================================

signal choice_made(choice: String)

# UI References
@onready var panel_container = $PanelContainer
@onready var title_label = $PanelContainer/VBoxContainer/TitleLabel
@onready var marshal_label = $PanelContainer/VBoxContainer/MarshalLabel
@onready var recklessness_label = $PanelContainer/VBoxContainer/RecklessnessLabel
@onready var warning_label = $PanelContainer/VBoxContainer/WarningLabel
@onready var charge_button = $PanelContainer/VBoxContainer/ButtonContainer/ChargeButton
@onready var restrain_button = $PanelContainer/VBoxContainer/ButtonContainer/RestrainButton

var current_marshal: String = ""
var current_target: String = ""
var current_recklessness: int = 0

# Napoleonic color palette
const COLOR_TEXT = "eee"
const COLOR_DANGER = "ff4444"
const COLOR_CAVALRY = "8b4513"  # Saddle brown for cavalry theme

# UI-5: the hooves the card opens on — an arrival sound, stopped when an answer is given
var _open_cue = null  # untyped: a one-shot frees itself when it ends

func _answer(cue: String) -> void:
	AudioManager.stop_player(_open_cue)
	_open_cue = null
	AudioManager.play(cue)

func _ready():
	print("GloriousChargeDialog: _ready() STARTING")
	print("  panel_container: ", panel_container)
	print("  charge_button: ", charge_button)
	print("  restrain_button: ", restrain_button)

	# Connect button signals
	if charge_button:
		charge_button.pressed.connect(_on_charge_pressed)
		print("  ✓ ChargeButton connected")
	else:
		push_error("GloriousChargeDialog: ChargeButton is NULL!")

	if restrain_button:
		restrain_button.pressed.connect(_on_restrain_pressed)
		print("  ✓ RestrainButton connected")
	else:
		push_error("GloriousChargeDialog: RestrainButton is NULL!")

	# UI-5: each answer plays its own cue, so the global click stands aside
	if charge_button:
		charge_button.set_meta("no_click_sfx", true)
	if restrain_button:
		restrain_button.set_meta("no_click_sfx", true)

	# Hide by default
	hide()

	print("GloriousChargeDialog: _ready() COMPLETE - is_inside_tree: ", is_inside_tree())

func show_glorious_charge(data: Dictionary):
	"""Display Glorious Charge popup with data from backend."""
	AudioManager.stop_player(_open_cue)
	_open_cue = AudioManager.play("cavalry")
	print("GloriousChargeDialog.show_glorious_charge() ENTERED")
	print("  Received data: ", data)

	# Handle null values from JSON (get() default doesn't work if key exists with null)
	var marshal_val = data.get("marshal")
	var target_val = data.get("target")
	var reck_val = data.get("recklessness")

	current_marshal = marshal_val if marshal_val != null else "Marshal"
	current_target = target_val if target_val != null else "enemy"
	current_recklessness = int(reck_val) if reck_val != null else 3

	print("  Parsed: marshal=%s, target=%s, recklessness=%d" % [current_marshal, current_target, current_recklessness])

	# Set title with horse emoji
	title_label.text = "GLORIOUS CHARGE!"

	# Set marshal info
	marshal_label.text = "%s's blood is up!" % current_marshal

	# Set recklessness level with visual indicator (simple bars)
	var reck_bars = ""
	for i in range(current_recklessness):
		reck_bars += "|"
	for i in range(4 - current_recklessness):
		reck_bars += "."
	recklessness_label.text = "Recklessness: %s (%d/4)" % [reck_bars, current_recklessness]

	# Set warning
	# DDB-17 (Pre-Deploy S13b part 2): the charge goes in alone — no muster.
	warning_label.text = "Glorious Charge deals 2x damage but also TAKES 2x damage!\n%s charges ALONE — no corps joins a charge.\nTarget: %s" % [current_marshal, current_target]

	# Set button text
	charge_button.text = "CHARGE! (2x damage dealt AND taken)"
	restrain_button.text = "Restrain - Normal Attack"

	# Show the dialog
	print("  About to call show()")

	# Ensure all children are visible first
	if panel_container:
		panel_container.visible = true
		print("  Set panel_container.visible = true")

	# Get the background overlay and make it visible too
	var bg_overlay = get_node_or_null("BackgroundOverlay")
	if bg_overlay:
		bg_overlay.visible = true
		print("  Set BackgroundOverlay.visible = true")

	# Now show the CanvasLayer itself
	_banner("charge")
	show()
	# July 18, 2026 viewport sweep: fit to the CURRENT logical viewport.
	# Interface Scale (content_scale_factor, up to 2.0) divides the logical
	# viewport, so a fixed authored rect can carry the action row off-screen
	# and leave a modal undismissable. The helper is a no-op wherever the
	# panel already fits, and returns early for non-centre-anchored panels.
	Utils.clamp_centered_panel($PanelContainer)
	visible = true  # Force visibility

	print("  AFTER show() - visible property: ", visible)
	print("  is_inside_tree: ", is_inside_tree())
	print("  PanelContainer visible: ", panel_container.visible if panel_container else "NULL")
	print("  layer: ", layer)

func _on_charge_pressed():
	"""Player chooses to execute Glorious Charge."""
	print("GloriousChargeDialog: CHARGE pressed")
	_answer("bugle_charge")
	hide()
	choice_made.emit("charge")

func _on_restrain_pressed():
	"""Player restrains the marshal - normal attack."""
	print("GloriousChargeDialog: RESTRAIN pressed")
	_answer("back")
	hide()
	choice_made.emit("restrain")


func _banner(surface: String) -> void:
	"""Session UI-5: the picture over the card (a 3:1 banner sized to the card's
	width; its hover is the credit). It steps aside on the compact view and in a
	short window, and `_banner_yield` takes it away again when the card's
	answers would otherwise leave the view."""
	var vb: VBoxContainer = $PanelContainer/VBoxContainer
	var old: Node = vb.get_node_or_null("Illustration")
	if old != null:
		vb.remove_child(old)
		old.queue_free()
	var view: Vector2 = get_viewport().get_visible_rect().size
	if Utils.compact_view() or view.y < 760.0:
		return
	var panel: Control = $PanelContainer
	var w: float = panel.offset_right - panel.offset_left
	if w <= 0.0:
		w = 480.0
	var pic: TextureRect = Illustrations.make_banner(surface, minf(w, view.x - 80.0) - 48.0, true)
	if pic == null:
		return
	vb.add_child(pic)
	vb.move_child(pic, 0)
	call_deferred("_banner_yield")


func _banner_yield() -> void:
	"""The banner is the first thing to give way: if the card cannot fit the
	view with it, it goes."""
	await get_tree().process_frame
	await get_tree().process_frame
	if not visible:
		return
	var pic: Control = $PanelContainer/VBoxContainer.get_node_or_null("Illustration") as Control
	if pic == null:
		return
	var view: Vector2 = get_viewport().get_visible_rect().size
	# Session UI-5: the banner shrinks first (it steps aside under its floor),
	# until the card stands centred below the top bar.
	if $PanelContainer.get_combined_minimum_size().y > Illustrations.card_room(view.y):
		Illustrations.fit_banner_to_card($PanelContainer, view.y)
		Utils.clamp_centered_panel($PanelContainer)
