extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Talleyrand Redemption Popup (Session 8C)
# =============================================================================
# Displays when Talleyrand's trust drops below 20.
# Three buttons: Apologize / Replace with Loyalist / Continue Regardless
# =============================================================================

signal choice_made(choice: String, data: Dictionary)

# UI References
@onready var content_label = $PanelContainer/VBoxContainer/ContentLabel
@onready var apologize_btn = $PanelContainer/VBoxContainer/ButtonContainer/ApologizeButton
@onready var replace_btn = $PanelContainer/VBoxContainer/ButtonContainer/ReplaceButton
@onready var continue_btn = $PanelContainer/VBoxContainer/ButtonContainer/ContinueButton

var current_data: Dictionary = {}

func _ready():
	hide()
	apologize_btn.pressed.connect(_on_apologize)
	replace_btn.pressed.connect(_on_replace)
	continue_btn.pressed.connect(_on_continue)

func show_redemption(data: Dictionary):
	"""Display Talleyrand redemption popup."""
	current_data = data
	var trust = data.get("trust", 0)
	var trigger = data.get("trigger_reason", "")
	var apologize_fx = data.get("option_apologize", {}).get("effect", "Trust +15, Authority -5")
	var replace_fx = data.get("option_replace", {}).get("effect", "Irreversible replacement")
	var continue_fx = data.get("option_continue", {}).get("effect", "Authority -10")

	var bbcode = ""
	bbcode += "[b]TALLEYRAND'S LOYALTY QUESTIONED[/b]\n"
	bbcode += "Trust has fallen to %d/100.\n\n" % trust
	bbcode += "The Foreign Minister of France stands before you. "
	bbcode += "His methods have grown... independent.\n\n"
	bbcode += "[b]Apologize[/b] — %s\n" % apologize_fx
	bbcode += "[b]Replace with Loyalist[/b] — %s  [color=red]IRREVERSIBLE[/color]\n" % replace_fx
	bbcode += "[b]Continue Regardless[/b] — %s" % continue_fx

	content_label.text = ""
	content_label.append_text(bbcode)

	apologize_btn.disabled = false
	replace_btn.disabled = false
	continue_btn.disabled = false
	show()

func _on_apologize():
	_disable_buttons()
	hide()
	choice_made.emit("apologize", current_data)

func _on_replace():
	_disable_buttons()
	hide()
	choice_made.emit("replace", current_data)

func _on_continue():
	_disable_buttons()
	hide()
	choice_made.emit("continue", current_data)

func _disable_buttons():
	apologize_btn.disabled = true
	replace_btn.disabled = true
	continue_btn.disabled = true
