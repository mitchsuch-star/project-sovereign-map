extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Capture Choice Dialog (Phase 6.2.E)
# =============================================================================
# Displays when player captures an enemy region.
# Player chooses: Plunder (gold + destroy buildings) or Secure (higher stability)
# W6-8 (Spoils of War): the same dialog also serves the second, estate stage
# (stage == "estate") — Confiscate the estate vs Respect the title.
# =============================================================================

signal choice_made(choice: String)

# UI References
@onready var panel_container = $PanelContainer
@onready var title_label = $PanelContainer/VBoxContainer/TitleLabel
@onready var region_label = $PanelContainer/VBoxContainer/RegionLabel
@onready var description_label = $PanelContainer/VBoxContainer/DescriptionLabel
@onready var plunder_button = $PanelContainer/VBoxContainer/ButtonContainer/PlunderButton
@onready var secure_button = $PanelContainer/VBoxContainer/ButtonContainer/SecureButton

var current_region: String = ""
var current_capturer: String = ""
var current_stage: String = "capture"  # "capture" or "estate" (W6-8)
var current_dialogue_id: int = -1      # W6-0 identity (stage 1 since IGR-E; estate stage since W6-8)

func _ready():
	# Connect button signals
	if plunder_button:
		plunder_button.pressed.connect(_on_plunder_pressed)
	else:
		push_error("CaptureChoiceDialog: PlunderButton is NULL!")

	if secure_button:
		secure_button.pressed.connect(_on_secure_pressed)
	else:
		push_error("CaptureChoiceDialog: SecureButton is NULL!")

	# Hide by default
	hide()

func show_capture_choice(data: Dictionary):
	"""Display capture choice popup with data from backend."""
	AudioManager.play("cloth")
	var region_val = data.get("region")
	var capturer_val = data.get("capturer")

	current_region = region_val if region_val != null else "Unknown"
	current_capturer = capturer_val if capturer_val != null else "Marshal"
	current_stage = str(data.get("stage", "capture"))
	current_dialogue_id = int(data.get("dialogue_id", -1))

	if current_stage == "estate":
		# W6-8: the second question — the conquered province funds an
		# enemy marshal's estate.
		var holder = str(data.get("estate_holder", "the enemy marshal"))
		var holder_nation = str(data.get("estate_holder_nation", "their nation"))
		var windfall = int(data.get("windfall", 0))
		title_label.text = "AN ESTATE IN YOUR HANDS"
		region_label.text = "%s sustains Marshal %s's household" % [current_region, holder]
		description_label.text = "How shall the conqueror treat his title?"
		plunder_button.text = "CONFISCATE (+%s gold, %s will not forgive it)" % [Utils.format_number(windfall), holder_nation]
		secure_button.text = "RESPECT THE TITLE (%s will remember the courtesy)" % holder_nation
	else:
		# Set title
		title_label.text = "REGION CAPTURED!"

		# Set region info
		region_label.text = "%s has taken %s" % [current_capturer, current_region]

		# Set description
		description_label.text = "How shall your forces treat the conquered territory?"

		# Set button text with consequences.
		# IGR-E: the PLUNDER arm now quotes what it will actually pay. The
		# backend sends `plunder_gold` computed by the same expression that
		# pays it (world_state.plunder_yield), so this is shown=applied, not
		# an estimate. Post-landing review #4/#11: a payload that predates
		# the key (pre-IGR-E save whose load-time backfill could not resolve
		# the region) gets an UNPRICED label, never "+0 gold" for a choice
		# that pays the real sum; and the figure uses Utils.format_number so
		# the modal, terminal and outcome line all read "1,200" the same way.
		var plunder_gold = int(data.get("plunder_gold", 0))
		if data.has("plunder_gold"):
			plunder_button.text = "PLUNDER (+%s gold, buildings burned, stability 10)" % Utils.format_number(plunder_gold)
		else:
			plunder_button.text = "PLUNDER (loot the province, buildings burned, stability 10)"
		secure_button.text = "SECURE (Preserve order, stability 25, buildings damaged)"

	# Ensure all children are visible first
	if panel_container:
		panel_container.visible = true

	var bg_overlay = get_node_or_null("BackgroundOverlay")
	if bg_overlay:
		bg_overlay.visible = true

	# Show the CanvasLayer
	show()
	# July 18, 2026 viewport sweep: fit to the CURRENT logical viewport.
	# Interface Scale (content_scale_factor, up to 2.0) divides the logical
	# viewport, so a fixed authored rect can carry the action row off-screen
	# and leave a modal undismissable. The helper is a no-op wherever the
	# panel already fits, and returns early for non-centre-anchored panels.
	Utils.clamp_centered_panel($PanelContainer)
	visible = true

func _on_plunder_pressed():
	"""Player chooses the first option (plunder / confiscate)."""
	AudioManager.play("coin_pour")
	hide()
	choice_made.emit("confiscate" if current_stage == "estate" else "plunder")

func _on_secure_pressed():
	"""Player chooses the second option (secure / respect)."""
	hide()
	choice_made.emit("respect" if current_stage == "estate" else "secure")
