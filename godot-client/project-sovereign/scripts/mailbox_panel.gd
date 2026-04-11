extends CanvasLayer

# =============================================================================
# PROJECT SOVEREIGN - Mailbox Panel (Session 2 follow-up)
# =============================================================================
# Browsable inbox for pending diplomatic items. Shows all mailbox-eligible
# diplomacy (incoming_proposal, counter_offer, counter_offer_response,
# conflict_alert) with ACTIVE/WAITING state. Click a row to open/activate.
# =============================================================================

signal item_selected(mailbox_id: int, is_active: bool, item_type: String)
signal panel_closed

const ITEM_TYPE_DISPLAY = {
	"incoming_proposal": "Proposal",
	"counter_offer": "Counter-Offer",
	"counter_offer_response": "Counter Response",
	"conflict_alert": "Conflict Alert",
}

@onready var title_label: Label = $PanelContainer/VBoxContainer/TitleLabel
@onready var item_list: RichTextLabel = $PanelContainer/VBoxContainer/ItemList
@onready var close_btn: Button = $PanelContainer/VBoxContainer/ButtonContainer/CloseButton

var _items: Array = []

func _ready():
	hide()
	close_btn.pressed.connect(_on_close)
	item_list.meta_clicked.connect(_on_meta_clicked)


func show_mailbox(data: Dictionary):
	"""Display mailbox with items from GET /mailbox response."""
	var items = data.get("items", [])
	var count = int(data.get("count", 0))
	_items = items

	title_label.text = "DIPLOMATIC MAILBOX (%d)" % count

	if items.size() == 0:
		item_list.text = ""
		item_list.append_text("[center][color=#a0a0a8]No pending diplomatic items.[/color][/center]")
		show()
		return

	var bbcode = ""
	for i in range(items.size()):
		var item = items[i]
		var mid = int(item.get("mailbox_id", 0))
		var state = str(item.get("state", "WAITING"))
		var source = str(item.get("source_nation", "Unknown"))
		var itype = str(item.get("item_type", "unknown"))
		var ptype = str(item.get("proposal_type", itype))
		var turn = int(item.get("arrival_turn", 0))
		var type_display = ITEM_TYPE_DISPLAY.get(itype, itype.replace("_", " ").capitalize())

		# State badge color
		var state_color = "#7eb8da" if state == "ACTIVE" else "#a0a0a8"
		var state_text = "[ACTIVE]" if state == "ACTIVE" else "[WAITING]"

		# Clickable row via meta tag
		bbcode += "[url=%d]" % mid
		bbcode += "[color=%s]%s[/color] " % [state_color, state_text]
		bbcode += "[b]%s[/b] from [color=#e0c060]%s[/color]" % [type_display, source]
		bbcode += " — %s" % ptype.replace("_", " ").capitalize()
		bbcode += "  [color=#707080](Turn %d)[/color]" % turn
		bbcode += "[/url]\n"

		if i < items.size() - 1:
			bbcode += "[color=#404050]────────────────────────────────────────[/color]\n"

	item_list.text = ""
	item_list.append_text(bbcode)
	show()


func _on_meta_clicked(meta):
	"""Handle click on a mailbox item row."""
	var mailbox_id = int(str(meta))
	if mailbox_id <= 0:
		return

	# Find the item to determine if it's active or waiting
	var is_active = false
	var item_type = ""
	for item in _items:
		if int(item.get("mailbox_id", 0)) == mailbox_id:
			is_active = str(item.get("state", "")) == "ACTIVE"
			item_type = str(item.get("item_type", ""))
			break

	hide()
	item_selected.emit(mailbox_id, is_active, item_type)


func _on_close():
	hide()
	panel_closed.emit()
