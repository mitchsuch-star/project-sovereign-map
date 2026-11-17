extends SceneTree
# Row BA, BA-4 - "the roads and the fog", pressed in the real client (November 16, 2026)
# - after tools/ba3_mode_c_walk.gd, whose helpers this file carries unchanged.
#
#   $env:SOVEREIGN_PORT   = "8006"        # a sandboxed backend listening there (never 8005)
#   $env:BA4_WALK_OUT     = "<abs dir>"   # frames + walk.json land here
#   <godot> --audio-driver Dummy --windowed --resolution 1920x1080 \
#           --path godot-client/project-sovereign --script <abs>/tools/ba4_mode_c_walk.gd
#
# Do not start it by hand: `tools/ba4_mode_c_walk.py` hunts the campaign seed, starts
# the sandboxed backend on it and runs this.
#
# The REAL main.tscn against that backend. Three plans (BA4_PLAN):
#   oldsave  a save BA-3 wrote (HEAD aeae6967, a day of battle open) loaded by the
#          client's own Load: the day offered on its province's panel, a word
#          played, the digit 8 breaks off, and the close tells no tally the
#          day never kept.
#   day    Masséna against the Archduke Charles: the attack card before a day; the
#          day's first-open line on a row of its own, acknowledged; the digits on
#          the chips; `2` denied (no Guard) and nothing sent; `1` presses; the
#          card and the province's panel while the day is open (a word of the
#          day, one point; no second ATTACK row); the panel's "Break off" and the
#          close's tally; a digit on the closed day's table.
#   roads  the real 1805 opening: Murat's support card for Ney halts at the
#          approach and its Send asks nothing; a march's card names the men its
#          first march costs; Help's Terms page.
# Each step records {step, did, saw, ok} in walk.json["results"] (and a frame row
# in walk.json["steps"]), tolerates failure, and the walk never aborts. What it
# reads is the client's own state — the table's `_data.day`, the acts' digits
# and denials, the card's and the panel's text, the log — never a picture.

const WALL_LIMIT_MS := 900000
const OUT_DEFAULT := "res://../../docs/audits/ba4_mode_c_2026_11_16"
# the board comes from the runner (BA4_LEAD / BA4_FOE / BA4_FIELD): Masséna against the
# Archduke Charles at Carniola on the `day` board; the real 1805 opening on `roads`
var FIELD := "Carniola"
var FOE := "ArchdukeCharles"
var LEAD := "Massena"
var PLAN := "day"        # "day" (the Masséna board) or "roads" (the real 1805 opening)
const NBSP := " "

var _main = null
var _out: Dictionary = {"steps": [], "errors": [], "results": []}
var _dir := ""
var _t0 := 0
var _done := false
var _n := 0
var _words: Array = []     # every `word_given` the table emitted
var _press_meta := ""      # the typed board's log chip ("presses"), kept for the review's R12
var _days_probe: Array = []  # what GET /battle_day answered (the review's R12)


func _init():
	UiSettings._cfg = ConfigFile.new()
	UiSettings._persist = false   # the harness flag: writes stay in memory
	UiSettings._cfg.set_value("orders", "next_marshal_after_order", true)   # the player's default
	_t0 = Time.get_ticks_msec()
	process_frame.connect(_watchdog)
	_walk.call_deferred()


func _watchdog():
	if not _done and Time.get_ticks_msec() - _t0 > WALL_LIMIT_MS:
		_out["error"] = "wall-clock limit hit"
		_finish()


func _frames(n: int) -> void:
	for _i in range(n):
		await process_frame


func _secs(s: float) -> void:
	await create_timer(s).timeout
	await _frames(2)


func _api():
	return _main.get("api_client") if _main != null else null


func _api_idle() -> bool:
	var api = _api()
	if api == null:
		return true
	var queue = api.get("_request_queue")
	return not bool(api.get("_request_in_flight")) and (queue == null or queue.is_empty())


func _settle(limit_ms: int = 30000) -> void:
	var start := Time.get_ticks_msec()
	var calm := 0
	while Time.get_ticks_msec() - start < limit_ms:
		await process_frame
		calm = calm + 1 if _api_idle() else 0
		if calm >= 8:
			return


func _turn() -> int:
	return int(_main.get("current_turn")) if _main != null else 0


var _hud_over: Array = []    # every reading of the HUD's actions above the turn's maximum


func _ap() -> int:
	var now := int(_main.get("actions_remaining")) if _main != null else -1
	var top := int(_main.get("max_actions")) if _main != null else 99
	if now > top:
		var line := "actions %d of a maximum %d" % [now, top]
		if not _hud_over.has(line):
			_hud_over.append(line)
	return now


func _all_nodes(from: Node) -> Array:
	var out: Array = []
	var stack: Array = [from]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		out.append(n)
		for c in n.get_children():
			stack.append(c)
	return out


func _plain(text: String) -> String:
	return text.replace(NBSP, " ")


func _hold_window() -> void:
	if root.mode != Window.MODE_WINDOWED or root.size != Vector2i(1920, 1080):
		root.mode = Window.MODE_WINDOWED
		root.size = Vector2i(1920, 1080)
		root.position = Vector2i(5200, 20)
		await _frames(6)


func _clear_boot_overlays() -> void:
	for _i in range(6):
		var pressed := false
		var p = _main.get("incoming_proposal_popup")
		if p != null and p.visible:
			var dismiss = p.get("dismiss_btn")
			if dismiss != null and dismiss.visible and not dismiss.disabled:
				dismiss.emit_signal("pressed")
				pressed = true
		var ip = _main.get("interrupt_popup")
		if ip != null and ("visible" in ip) and bool(ip.visible):
			ip.visible = false
			pressed = true
		if not pressed:
			break
		await _frames(6)
		await _settle()


func _shot(name: String, note: String) -> void:
	await _hold_window()
	var park := InputEventMouseMotion.new()
	park.position = Vector2(-40, -40)
	park.global_position = park.position
	root.push_input(park, true)
	await _frames(4)
	_n += 1
	var img := root.get_texture().get_image()
	# (row BA, BA-5: the frame's date is the run's own - BA4_WALK_STAMP, the runner's
	# `--stamp`; unset it is the day BA-4's record was shot)
	var stamp := OS.get_environment("BA4_WALK_STAMP")
	var file := "BA4_WALK_%02d_%s_%s.jpg" % [_n, name, stamp if stamp != "" else "2026_11_16"]
	var err := img.save_jpg(_dir.path_join(file), 0.88)
	_out["steps"].append({"step": name, "note": note, "frame": file, "saved": err == OK,
		"turn": _turn(), "ms": Time.get_ticks_msec() - _t0})


func _rec(step: String, did: String, saw: String, ok: bool, extra: Dictionary = {}) -> void:
	_ap()      # every step reads the HUD's actions: never above the turn's maximum
	if not _hud_over.is_empty():
		saw += " | THE HUD READ %s" % ", ".join(PackedStringArray(_hud_over))
		ok = false
		_hud_over = []
	var row := {"step": step, "did": did, "saw": saw, "ok": ok}
	for k in extra:
		row[k] = extra[k]
	_out["results"].append(row)
	if not ok:
		_out["errors"].append({"turn": _turn(), "what": step + ": " + saw})


func _last_words(text: String, chars: int = 260) -> String:
	var t := text.strip_edges()
	return t.substr(maxi(0, t.length() - chars))


func _log_tail(chars: int = 700) -> String:
	var display = _main.get("output_display")
	var text: String = display.get_parsed_text() if display != null else ""
	return text.substr(maxi(0, text.length() - chars))


func _card() -> Node:
	return _main.get("order_card")


func _question() -> String:
	"""A marshal's question on screen (the interrupt popup), its words - "" when none."""
	var ip = _main.get("interrupt_popup")
	if ip == null or not ("visible" in ip) or not bool(ip.visible):
		return ""
	var words := ""
	for n in _all_nodes(ip):
		if n is RichTextLabel and n.is_visible_in_tree():
			words += n.get_parsed_text() + " "
		elif n is Label and n.is_visible_in_tree():
			words += str(n.text) + " "
		elif n is Button and n.is_visible_in_tree():
			words += "[" + str(n.text) + "] "
	return words.strip_edges() if words.strip_edges() != "" else "(a question stands)"


func _answer_objection(step: String) -> bool:
	"""A marshal's objection to the order stands as a modal: answered Insist."""
	var dlg = _main.get("objection_dialog")
	if dlg == null or not dlg.visible:
		return false
	await _shot(step + "_objection", "the marshal objects")
	var insist = dlg.get("insist_button")
	if insist != null and insist.visible and not insist.disabled:
		insist.emit_signal("pressed")
	await _settle(60000)
	await _frames(12)
	_rec(step + "_objection", "the objection answered: Insist", "the modal stood and was answered", true)
	return true


func _commit_if_asked(step: String) -> bool:
	"""The muster's question on a chip's order ('Commit the Attack' / Cancel), if one
	stands: answered Commit. True when one stood. (Best effort: the question is the
	interrupt popup's, or the order card's own Send.)"""
	var asked := _question()
	if asked != "":
		var ip = _main.get("interrupt_popup")
		for n in _all_nodes(ip):
			if n is Button and n.is_visible_in_tree() and not n.disabled \
					and str(n.text).findn("commit") >= 0:
				n.emit_signal("pressed")
				break
		await _settle(60000)
		await _frames(12)
		_rec(step + "_muster", "the muster's question answered: Commit the Attack", asked.substr(0, 200), true)
		return true
	var oc = _card()
	if oc != null and oc.visible:
		var sendb = oc.get("send_button")
		if sendb != null and sendb.visible and not sendb.disabled:
			sendb.emit_signal("pressed")
			await _settle(60000)
			await _frames(12)
			_rec(step + "_muster", "the order card stood: Send", "the order card was answered", true)
			return true
	return false


func _select(who: String) -> void:
	var line = _main.get("command_input")
	if line != null:
		line.release_focus()
	_main.call("_on_marshal_chip_pressed", who)
	await _frames(8)
	await _settle(15000)
	await _frames(6)


func _open_attack_card() -> bool:
	var map = _main.get("map_area")
	if map == null:
		return false
	map.emit_signal("order_context_requested", FIELD, FOE)
	var start := Time.get_ticks_msec()
	while Time.get_ticks_msec() - start < 20000:
		await process_frame
		var oc = _card()
		if oc != null and oc.visible and _api_idle() and str(oc.call("command")) != "":
			break
	await _frames(12)
	var card = _card()
	return card != null and card.visible


# ── the table and its day ───────────────────────────────────────────────────

func _dio():
	return _main.get("battle_diorama")


func _day() -> Dictionary:
	var dio = _dio()
	if dio == null:
		return {}
	var data = dio.get("_data")
	if data is Dictionary and (data as Dictionary).get("day", null) is Dictionary:
		return (data as Dictionary)["day"]
	return {}


func _table_up() -> bool:
	var dio = _dio()
	return dio != null and bool(dio.visible)


func _panel_shown() -> bool:
	var dio = _dio()
	if dio == null or not bool(dio.visible):
		return false
	var acts = dio.get("_acts")
	if acts == null:
		return false
	var panel = acts.get("_day_panel")
	return bool(dio.get("_final")) and panel != null and is_instance_valid(panel) \
		and (panel as CanvasItem).is_visible_in_tree()


func _wait_final(limit_ms: int) -> bool:
	"""The host's `_final`: the showing has come to rest (the acts played, the
	gavel struck) with Close shown — what any step that presses Close or reads
	'at rest' waits on."""
	var start := Time.get_ticks_msec()
	while Time.get_ticks_msec() - start < limit_ms:
		await process_frame
		var dio = _dio()
		if dio != null and bool(dio.visible) and bool(dio.get("_final")) \
				and dio.get("_btn_close") != null and bool(dio.get("_btn_close").visible):
			await _frames(6)
			return true
	return false


func _wait_for_panel(limit_ms: int) -> bool:
	"""The table is up and the day's panel stands at rest (the acts have played).
	A click on the table skips the acts when they run long."""
	var start := Time.get_ticks_msec()
	while Time.get_ticks_msec() - start < limit_ms:
		await process_frame
		if _panel_shown():
			await _frames(10)
			return true
	return false


func _purses(day: Dictionary) -> String:
	return "ours %s / his %s, awaits '%s', open=%s" % [str(day.get("ours", "?")), str(day.get("theirs", "?")),
		str(day.get("awaits", "?")), str(day.get("open", "?"))]


func _chips_of(day: Dictionary) -> Array:
	var out: Array = []
	for c in day.get("chips", []):
		if c is Dictionary:
			out.append("%s%s" % [str(c.get("label", "?")), "" if bool(c.get("ok", false)) else " (dim)"])
	return out


func _chip_index(day: Dictionary, kind: String, word: String) -> int:
	var chips = day.get("chips", [])
	for i in range(chips.size()):
		var c = chips[i]
		if c is Dictionary and bool(c.get("ok", false)) and str(c.get("kind", "")) == kind \
				and str(c.get("word", "")) == word:
			return i
	return -1


func _press(index: int) -> bool:
	"""The chip pressed as a click on it delivers: the box that draws it emits
	`meta_clicked("day:<index>")`, the index being the chip's place in the
	block's FULL `chips` array. The panel has two boxes: the words that spend
	and the exits ("<lead> stands", "Break off" / "Fall back", "Leave it to
	...")."""
	var dio = _dio()
	var acts = dio.get("_acts") if dio != null else null
	if acts == null:
		return false
	var chips = _day().get("chips", [])
	if index < 0 or index >= chips.size():
		return false
	var chip: Dictionary = chips[index]
	# the panel's three boxes (battle_acts.gd `_day_split`): the exits (a word, or a
	# "stands" / "Break off" / "Fall back"), the lead's own words (press, the Guard,
	# dig in: `_day_chips`, row C) and every other kind in the compact groups
	# (another corps leads, the guns, a corps brought up: `_day_groups`, rows D)
	var kind := str(chip.get("kind", ""))
	var box = null
	if str(chip.get("word", "")) != "" or kind in ["stand", "break_off"]:
		box = acts.get("_day_exits")
	elif kind in ["press", "guard", "dig_in"]:
		box = acts.get("_day_chips")
	else:
		box = acts.get("_day_groups")
	if box == null or not is_instance_valid(box):
		return false
	(box as RichTextLabel).meta_clicked.emit("day:%d" % index)
	return true


func _chips_up() -> bool:
	"""The panel offers its words: the exits box exists only for a day that
	awaits us and whose clash no other follows."""
	var dio = _dio()
	var acts = dio.get("_acts") if dio != null else null
	if acts == null or not _panel_shown():
		return false
	var exits = acts.get("_day_exits")
	return exits != null and is_instance_valid(exits) and bool(_day().get("open", false)) 		and str(_day().get("awaits", "")) == "ours"


func _wait_for_chips(limit_ms: int) -> bool:
	"""The table is up and the panel offers its words (a table that FOLLOWS ours
	shows none: the live chips ride his clash's table, which comes next)."""
	var start := Time.get_ticks_msec()
	while Time.get_ticks_msec() - start < limit_ms:
		await process_frame
		if _chips_up():
			await _frames(10)
			return true
	return false


func _strip_tags(s: String) -> String:
	var re := RegEx.create_from_string("\\[[^\\]]*\\]")
	return _plain(re.sub(s, "", true)).strip_edges()


func _metas_of(rtl) -> Array:
	"""Every link of a rich text: [{meta, label}] (the label without its tags)."""
	return _metas_in_text(str(rtl.text) if rtl != null else "")


func _log_messages_since(n: int) -> String:
	"""The log's own SOURCE since message `n`: main appends each message with `append_text`
	(the label's `.text` stays empty), and keeps the messages as appended in `_output_messages`."""
	var msgs = _main.get("_output_messages")
	if not (msgs is Array):
		return ""
	return "\n".join(PackedStringArray((msgs as Array).slice(n)))


func _log_msgs() -> int:
	var msgs = _main.get("_output_messages")
	return (msgs as Array).size() if msgs is Array else 0


func _log_meta_labelled(part: String, since: int = 0) -> String:
	for m in _metas_in_text(_log_messages_since(since)):
		if str((m as Dictionary).get("label", "")).find(part) >= 0:
			return str((m as Dictionary).get("meta", ""))
	return ""


func _metas_in_text(text: String) -> Array:
	var out: Array = []
	var pos := 0
	while true:
		var a := text.find("[url=", pos)
		if a < 0:
			break
		var b := text.find("]", a)
		var e := text.find("[/url]", b)
		if b < 0 or e < 0:
			break
		out.append({"meta": text.substr(a + 5, b - a - 5), "label": _strip_tags(text.substr(b + 1, e - b - 1))})
		pos = e + 6
	return out


func _meta_labelled(rtl, part: String) -> String:
	for m in _metas_of(rtl):
		if str((m as Dictionary).get("label", "")).find(part) >= 0:
			return str((m as Dictionary).get("meta", ""))
	return ""


func _log():
	return _main.get("output_display")


func _log_len() -> int:
	var l = _log()
	return l.get_parsed_text().length() if l != null else 0


func _log_since(n: int) -> String:
	var l = _log()
	return _plain(l.get_parsed_text().substr(n)) if l != null else ""


func _press_log_chip(part: String, since: int = 0) -> bool:
	"""A chip written into the log, pressed as a click on it delivers: the log's
	rich text emits `meta_clicked` with the link's meta."""
	var meta := _log_meta_labelled(part, since)
	if meta == "":
		return false
	_log().emit_signal("meta_clicked", meta)
	return true


func _close_modals() -> Dictionary:
	"""Every modal the game holds open, closed by its own button as a player closes it (the
	letter-book's Close, a proposal's Dismiss, a popup's Continue). NEVER the battle table
	(`battle_diorama`): a table that rises by itself is the walk's to read, and `_close_the_table()`
	is the only thing that closes one. {closed: [names], stuck: name} — `stuck` is the modal that
	could not be closed honestly."""
	var closed: Array = []
	for _i in range(6):
		var dm = _main.get("dialog_manager")
		var open_name := ""
		var open_node = null
		if dm != null:
			for nm in dm._dialogs:
				var entry = dm._dialogs[nm]
				if str(nm) != "battle_diorama" and entry.modal and entry.node != null and entry.node.visible:
					open_name = str(nm)
					open_node = entry.node
					break
		if open_name == "":
			break
		var btn = null
		if open_name == "mailbox_panel":
			btn = open_node.get("close_btn")
		elif open_node.get("dismiss_btn") != null:
			btn = open_node.get("dismiss_btn")
		else:
			for n in _all_nodes(open_node):
				if n is Button and n.is_visible_in_tree() and not n.disabled \
						and str(n.text) in ["Close", "Dismiss", "Continue", "OK"]:
					btn = n
					break
		if btn == null or not btn.is_visible_in_tree() or btn.disabled:
			return {"closed": closed, "stuck": open_name}
		btn.emit_signal("pressed")
		closed.append(open_name)
		await _frames(8)
		await _settle(20000)
		await _frames(6)
	var left := ""
	var dm2 = _main.get("dialog_manager")
	if dm2 != null:
		for nm in dm2._dialogs:
			var e2 = dm2._dialogs[nm]
			if str(nm) != "battle_diorama" and e2.modal and e2.node != null and e2.node.visible:
				left = str(nm)
	return {"closed": closed, "stuck": left}


func _key_press(code: Key) -> void:
	"""A key as the keyboard gives it, through the window's input."""
	for pressed in [true, false]:
		var ev := InputEventKey.new()
		ev.keycode = code
		ev.physical_keycode = code
		ev.pressed = pressed
		root.push_input(ev)
	await _frames(4)


func _panel() -> Node:
	return _main.get("region_panel")


func _panel_text() -> String:
	var panel = _panel()
	if panel == null or not panel.visible:
		return ""
	var area = panel.get("content_area")
	return _plain(area.get_parsed_text()) if area != null else ""


func _panel_source() -> String:
	var panel = _panel()
	var area = panel.get("content_area") if panel != null else null
	return str(area.text) if area != null else ""


func _close_the_table() -> bool:
	"""The table's own Close button, as a player presses it."""
	var dio = _dio()
	if dio == null or not bool(dio.visible):
		return true
	await _wait_final(30000)      # Close is not shown until the table is final
	var close_btn = dio.get("_btn_close")
	if close_btn == null or not close_btn.visible or close_btn.disabled:
		return false
	close_btn.emit_signal("pressed")
	var start := Time.get_ticks_msec()
	while Time.get_ticks_msec() - start < 8000:
		await process_frame
		if not bool(dio.visible):
			break
	await _settle(15000)
	await _frames(6)
	return not bool(dio.visible)


func _open_province_panel(region: String) -> bool:
	"""The map's left click on the province (its `region_clicked` signal, as
	ba2_mode_c_walk does), with no corps selected: a selection is first let go
	by Esc, as a player lets it go. Waits for the panel's march quotes (the day's
	chips ride them)."""
	for _i in range(3):
		if str(_main.get("_order_marshal")) == "":
			break
		await _key_press(KEY_ESCAPE)
	var map = _main.get("map_area")
	if map == null:
		return false
	map.emit_signal("region_clicked", region)
	var start := Time.get_ticks_msec()
	while Time.get_ticks_msec() - start < 25000:
		await process_frame
		if _panel() != null and _panel().visible and _api_idle() and _panel_text().find("THE DAY AT") >= 0:
			break
	await _frames(10)
	return _panel() != null and bool(_panel().visible)


func _cost_of_last() -> int:
	var last = _main.get("_last_command_response")
	if last is Dictionary and (last as Dictionary).get("action_info", null) is Dictionary:
		return int((last as Dictionary)["action_info"].get("cost", -1))
	return -1


func _text_of(node: Node) -> String:
	var words := ""
	for n in _all_nodes(node):
		if n is RichTextLabel and n.is_visible_in_tree():
			words += n.get_parsed_text() + "\n"
		elif n is Label and n.is_visible_in_tree():
			words += str(n.text) + "\n"
	return _plain(words)


func _notice_button(kind: String):
	"""The rail's icon for a notice of this type (a real Button with the
	notice in its meta), or null."""
	var bar = _main.get("notification_bar")
	if bar == null:
		return null
	for n in _all_nodes(bar.icon_container):
		if n is Button and n.has_meta("notification_data"):
			var data = n.get_meta("notification_data")
			if data is Dictionary and str((data as Dictionary).get("type", "")) == kind:
				return n
	return null


func _button_named(under: Node, text: String):
	if under == null:
		return null
	for n in _all_nodes(under):
		if n is Button and n.is_visible_in_tree() and not n.disabled and str(n.text) == text:
			return n
	return null

# ═════════════════════════════════════════════════════════════════════════════
# BA-4: what this walk adds to BA-3's helpers above
# ═════════════════════════════════════════════════════════════════════════════

func _acts():
	var dio = _dio()
	return dio.get("_acts") if dio != null else null


func _box_text(box) -> String:
	if box == null or not is_instance_valid(box):
		return ""
	return _plain((box as RichTextLabel).get_parsed_text())


func _day_rows() -> Dictionary:
	"""The day's panel as its text: the first day's line (the row named
	FirstOpen), row C, rows D, row E, and everything the panel shows."""
	var out := {"first": "", "own": "", "groups": "", "exits": "", "all": ""}
	var acts = _acts()
	if acts == null:
		return out
	var panel = acts.get("_day_panel")
	if panel == null or not is_instance_valid(panel):
		return out
	for child in (panel as Node).get_children():
		if child is RichTextLabel and (child as CanvasItem).is_visible_in_tree():
			var text := _plain((child as RichTextLabel).get_parsed_text())
			out["all"] = str(out["all"]) + text + "\n"
			if str(child.name) == "FirstOpen":
				out["first"] = text
	out["own"] = _box_text(acts.get("_day_chips"))
	out["groups"] = _box_text(acts.get("_day_groups"))
	out["exits"] = _box_text(acts.get("_day_exits"))
	return out


func _orders_echoed() -> int:
	"""How many orders the log has echoed (a sent order is echoed "► …")."""
	var l = _log()
	return l.get_parsed_text().count("►") if l != null else 0


func _card_text() -> String:
	var oc = _card()
	return _text_of(oc) if oc != null and bool(oc.visible) else ""


func _ghost_badge() -> String:
	"""The badge at the head of the ghost road the map draws for the quoted order."""
	var map = _main.get("map_area")
	var layer = map.get("order_layer") if map != null else null
	return str(layer.get("_ghost_label")) if layer != null else ""


func _cancel_card() -> void:
	var oc = _card()
	if oc != null and bool(oc.visible):
		var cancel = oc.get("cancel_button")
		if cancel != null and cancel.visible and not cancel.disabled:
			cancel.emit_signal("pressed")
	await _frames(8)
	await _settle(15000)
	await _frames(4)


func _open_card_on(region: String, piece: String) -> bool:
	"""The map's right click with a corps selected: a province (a march), an
	enemy in sight (an attack), another of ours (a support) — the card."""
	var map = _main.get("map_area")
	if map == null:
		return false
	map.emit_signal("order_context_requested", region, piece)
	var start := Time.get_ticks_msec()
	while Time.get_ticks_msec() - start < 20000:
		await process_frame
		var oc = _card()
		if oc != null and oc.visible and _api_idle() and str(oc.call("command")) != "":
			break
	await _frames(12)
	var card = _card()
	return card != null and bool(card.visible)


func _wait_chips_through_his_answer(limit_ms: int) -> bool:
	"""After a word of ours: his clash may follow on the same table ("His answer
	▸", then the table goes on by itself) — wait until the chips are ours again,
	or the day is closed."""
	var start := Time.get_ticks_msec()
	while Time.get_ticks_msec() - start < limit_ms:
		await process_frame
		if _chips_up():
			await _frames(10)
			return true
		var day := _day()
		if _table_up() and bool(_dio().get("_final")) and not day.is_empty() \
				and not bool(day.get("open", true)) and not bool(day.get("follows", false)):
			return false
	return false


func _walk_day() -> void:
	"""The day's rules of BA-4, pressed: the first day's line, the digits, a
	word's price on the card and on the province's chips, the closing tally."""
	# 2 - the attack card BEFORE any day: an ordinary order, priced in actions
	await _select(LEAD)
	var opened := await _open_attack_card()
	var card0 := _card_text()
	var badge0 := _ghost_badge()
	_rec("card_before", "selected %s, right-clicked %s at %s" % [LEAD, FOE, FIELD],
		"the card up=%s; the road's badge on the map: '%s'; its terms: %s" % [str(opened), badge0, _last_words(card0, 200)],
		opened and card0.find("1 action") >= 0 and card0.find("word of the day") < 0 and badge0 == "attack · 1 AP")
	var ap_open := _ap()
	if opened:
		var sendb = _card().get("send_button")
		if sendb != null and sendb.visible and not sendb.disabled:
			sendb.emit_signal("pressed")
	await _frames(6)
	await _settle(90000)
	await _frames(12)
	await _answer_objection("attack")
	await _commit_if_asked("attack")
	var up := await _wait_chips_through_his_answer(120000)
	var day := _day()
	_rec("day_opens", "pressed the card's Send (%s, attack %s)" % [LEAD, FOE],
		"actions %d -> %d; the table up=%s; the panel offers=%s; the day: %s; chips: %s" % [
			ap_open, _ap(), str(_table_up()), str(up), _purses(day), str(_chips_of(day))],
		up and bool(day.get("open", false)) and _chip_index(day, "press", "") >= 0, {"day": day})
	if not up:
		await _shot("no_day", "the day did not open as hunted")
		return

	# 3 - the first day's line: on a row of its own, and acknowledged
	var rows := _day_rows()
	var acts = _acts()
	var api = _api()
	await _settle(15000)
	var acked: bool = api != null and (api.get("_first_open_acked") as Dictionary).has("battle_day")
	_rec("first_day_line", "read the day's panel at rest",
		"the first row: '%s'; the table says it showed '%s'; acknowledged to the server=%s" % [
			str(rows["first"]).strip_edges(), str(acts.get("_day_first_shown")), str(acked)],
		str(rows["first"]).begins_with("The day hangs, Sire.") and str(acts.get("_day_first_shown")) == "battle_day" and acked,
		{"panel": rows["all"]})
	await _shot("first_day_line", "the first day of the campaign: its own line above the head, the chips with their digits")

	# 4 - the digits on the chips
	var press_i := _chip_index(day, "press", "")
	var press_label: String = str((day.get("chips", [])[press_i] as Dictionary).get("label", ""))
	var own_text := str(rows["own"])
	var exits_text := str(rows["exits"])
	_rec("digits_shown", "read rows C and E",
		"row C: %s | row E: %s" % [own_text.strip_edges(), exits_text.strip_edges()],
		own_text.find("1 " + press_label) >= 0 and exits_text.find("7 ") >= 0 and exits_text.find("8 Break off") >= 0
			and exits_text.find("9 Leave it to") >= 0)

	# 5 - a digit whose slot holds no chip (2: no Guard on this field): denied, nothing sent
	var echoed := _orders_echoed()
	var words0 := _words.size()
	var denied0 := int(acts.get("_day_denied"))
	var selected := str(_main.get("_order_marshal"))
	await _key_press(KEY_2)
	await _frames(10)
	await _settle(8000)
	_rec("digit_empty_slot", "pressed 2 on the table (no Guard here; selected under the table: '%s')" % selected,
		"denied %d -> %d; words %d -> %d; orders echoed %d -> %d; the table up=%s; the line reads '%s'" % [
			denied0, int(_acts().get("_day_denied")), words0, _words.size(), echoed, _orders_echoed(),
			str(_table_up()), str(_main.get("command_input").text)],
		int(_acts().get("_day_denied")) == denied0 + 1 and _words.size() == words0 and _orders_echoed() == echoed
			and _table_up() and str(_main.get("command_input").text) == "")

	# 6 - the lead's digit: 1 presses — one word, a point, no action
	var ours_before := int(day.get("ours", -1))
	var ap_before := _ap()
	var command: String = str((day.get("chips", [])[press_i] as Dictionary).get("command", ""))
	await _key_press(KEY_1)
	await _frames(6)
	await _settle(60000)
	await _frames(12)
	await _commit_if_asked("press")
	await _answer_objection("press")
	var back := await _wait_chips_through_his_answer(120000)
	day = _day()
	_rec("digit_press", "pressed 1 on the table ('%s')" % press_label,
		"words given %s; actions %d -> %d (action_info.cost=%d); purses %d -> %s; the chips back=%s; the log: %s" % [
			str(_words.slice(words0)), ap_before, _ap(), _cost_of_last(), ours_before, _purses(day), str(back),
			_last_words(_log_tail(), 200)],
		_words.size() == words0 + 1 and str(_words[_words.size() - 1]) == command and _ap() == ap_before
			and (not back or int(day.get("ours", -1)) == ours_before - 1), {"day": day})
	# Row BA, BA-5 (BA5-X8): the first day's line stood on the day's FIRST table (the step
	# `first_day_line` saw it drawn and acknowledged) — this table, the day's next, does not
	# say it again, and its exits have their room back: each says what it does
	var rows_after := _day_rows()
	_rec("first_line_once", "the table after the first word",
		"the first day's line on this table='%s'; the exits: '%s'" % [
			str(rows_after["first"]).strip_edges().substr(0, 40),
			str(rows_after["exits"]).strip_edges().substr(0, 170)],
		(not back) or (str(rows_after["first"]).strip_edges() == ""
			and (str(rows_after["exits"]).find("free ·") >= 0 or str(rows_after["exits"]).find("—") >= 0)))
	await _shot("after_digit_press", "the lead pressed by the digit 1")
	if not back:
		_rec("day_decided_early", "the press closed the day on this seed", _purses(day), false)
		return

	# 7 - with the day OPEN: the same attack on the card is a word, priced in points
	var _day_before_close: Dictionary = day.duplicate(true)
	var closed := await _close_the_table()
	await _select(LEAD)
	var opened2 := await _open_attack_card()
	var card1 := _card_text()
	var badge1 := _ghost_badge()
	_rec("card_during_the_day", "closed the table (Close), selected %s, right-clicked %s" % [LEAD, FOE],
		"table closed=%s; the card up=%s; the road's badge on the map: '%s'; its terms: %s" % [
			str(closed), str(opened2), badge1, _last_words(card1, 220)],
		closed and opened2 and card1.find("A word of the day") >= 0 and card1.find("1 point") >= 0
			and card1.find("1 action") < 0 and card1.find("Free") < 0 and card1.find("free ·") < 0
			and badge1 == "attack · 1 point")
	await _shot("card_during_the_day", "the attack card while the day is open: a word of the day, one point")
	await _cancel_card()

	# 8 - the province's panel: the day's chips, and no second ATTACK row for a word
	# (the day's block rides the province its LAST clash was fought in: he struck
	# back on our ground, so that is where the panel carries it)
	var day_field := str(_day_before_close.get("field", FIELD))
	var panel_up := await _open_province_panel(day_field)
	var ptext := _panel_text()
	# (other corps' "march & attack" rows are ordinary orders and keep their
	# ATTACK heading; what must not stand there is the LEAD's own attack — the
	# day's chips above already carry it, at a point)
	var lead_shown := Utils.display_marshal_name(LEAD)
	var own_row := ptext.find(lead_shown + " · attack") >= 0
	_rec("panel_during_the_day", "clicked %s on the map (the day's field now)" % day_field,
		"the panel up=%s; the day's block on it=%s; a row '%s · attack' under ATTACK=%s; '0 AP' on it=%s; panel: %s" % [
			str(panel_up), str(ptext.find("THE DAY AT") >= 0), lead_shown, str(own_row),
			str(ptext.find(" 0 AP") >= 0), _last_words(ptext, 260)],
		panel_up and ptext.find("THE DAY AT") >= 0 and not own_row and ptext.find(" 0 AP") < 0)
	await _shot("panel_during_the_day", "the province panel: the day's chips; the same attack is not listed twice")

	# 9 - the panel's own "Break off": the day closes, and the close is told with its tally
	var source := _panel_source()
	var meta := ""
	for m in _metas_in_text(source):
		if str((m as Dictionary).get("meta", "")).find("@word:break_off:") >= 0:
			meta = str((m as Dictionary).get("meta", ""))
	var log0 := _log_len()
	if meta != "":
		_panel().get("content_area").emit_signal("meta_clicked", meta)
	await _frames(6)
	await _settle(60000)
	await _frames(24)
	await _wait_final(20000)
	var closing := _day()
	var told: Array = closing.get("told", []) if closing.get("told", null) is Array else []
	var tally := ""
	for t in told:
		if t is Dictionary and str((t as Dictionary).get("kind", "")) == "tally":
			tally = str((t as Dictionary).get("line", ""))
	var on_table := str(_day_rows()["all"])
	var in_log := _log_since(log0)
	_rec("day_closes", "pressed the panel's chip 'Break off' (meta '%s')" % meta,
		"the table up=%s; the day open=%s, ended '%s', banner '%s'; the tally: '%s'; on the table=%s; in the log=%s; close: '%s'" % [
			str(_table_up()), str(closing.get("open", "?")), str(closing.get("ended", "")), str(closing.get("banner", "")),
			tally, str(tally != "" and on_table.find(tally) >= 0), str(tally != "" and in_log.find(tally) >= 0),
			str(closing.get("close", ""))],
		meta != "" and str(closing.get("ended", "")) == "broke_off" and tally.find("of ours for") >= 0
			and (on_table.find(tally) >= 0 or in_log.find(tally) >= 0)
			and str(closing.get("close", "")).begins_with("The attack at "), {"day": closing})
	await _shot("day_closes", "the day closed: its banner, how it ended and what it came to")

	# 10 - a digit on a table that offers nothing is NOT the day's — and under the
	# table it is nobody's: no slot of the selection card fires behind a modal
	if _table_up():
		var echoed2 := _orders_echoed()
		var denied2 := int(_acts().get("_day_denied")) if _acts() != null else 0
		await _key_press(KEY_3)
		await _frames(10)
		await _settle(8000)
		_rec("digit_on_a_closed_day", "pressed 3 on the closed day's table (selected under it: '%s')" % str(_main.get("_order_marshal")),
			"orders echoed %d -> %d; denied %d -> %d; the table up=%s" % [
				echoed2, _orders_echoed(), denied2, int(_acts().get("_day_denied")) if _acts() != null else 0, str(_table_up())],
			_orders_echoed() == echoed2 and _table_up())
		await _close_the_table()
	await _shot("the_field_at_rest", "the field at rest")


func _walk_roads() -> void:
	"""The roads' rules of BA-4 on the real 1805 opening: a support order that
	halts at the approach, a quote that names its first march's cost, the Help."""
	var who := OS.get_environment("BA4_MARCH_WHO")
	var to := OS.get_environment("BA4_MARCH_TO")
	var cost_said := OS.get_environment("BA4_MARCH_COST")
	# 2 - Murat's support card for Ney: his road runs through Mack's Swabia
	await _select("Murat")
	var ap0 := _ap()
	var ney_at := OS.get_environment("BA4_FRIEND_AT")
	var opened := await _open_card_on(ney_at, "Ney")
	var text := _card_text()
	var badge := _ghost_badge()
	_rec("approach_card", "selected Murat, right-clicked Ney at %s" % ney_at,
		"the card up=%s; the road's badge on the map: '%s'; its terms: %s" % [str(opened), badge, _last_words(text, 320)],
		opened and text.find("halts at the approach") >= 0 and text.find("joins him in") < 0
			and text.find("1 action") >= 0 and (badge == "" or badge == "halts at the approach · 1 AP"))
	await _shot("approach_card", "the support order's card: it halts at the approach")
	var log0 := _log_len()
	if opened:
		var sendb = _card().get("send_button")
		if sendb != null and sendb.visible and not sendb.disabled:
			sendb.emit_signal("pressed")
	await _frames(6)
	await _settle(60000)
	await _frames(12)
	var asked := _question()
	var said := _log_since(log0)
	_rec("approach_sent", "pressed the card's Send",
		"actions %d -> %d; a question stands: '%s'; the log: %s" % [ap0, _ap(), asked.substr(0, 80), _last_words(said, 240)],
		asked == "" and _ap() == ap0 - 1 and said.find("at the approach to") >= 0)
	await _shot("approach_sent", "Murat stands at the approach: no question asked")

	# 3 - a march whose first step costs men: the card names the figure
	if who != "" and to != "":
		await _select(who)
		var opened2 := await _open_card_on(to, "")
		var text2 := _card_text()
		_rec("march_cost_card", "selected %s, right-clicked %s" % [who, to],
			"the card up=%s; the server's own line: '%s'; on the card=%s; terms: %s" % [
				str(opened2), cost_said, str(text2.find(cost_said) >= 0), _last_words(text2, 260)],
			opened2 and cost_said != "" and text2.find(cost_said) >= 0)
		await _shot("march_cost_card", "a march's card names the men its first march costs")
		await _cancel_card()

	# 3b - the key bar: an attack whose battle would be a key one SHORT of a great
	# one (50,000 men or more, under 80,000) — its card calls it a pitched battle.
	# A board that has none is a failed step, never a skipped one.
	var p_who := OS.get_environment("BA4_PITCHED_WHO")
	var p_foe := OS.get_environment("BA4_PITCHED_FOE")
	var p_at := OS.get_environment("BA4_PITCHED_AT")
	var p_said := OS.get_environment("BA4_PITCHED_SAID")
	var opened3 := false
	var text3 := ""
	if p_who != "" and p_foe != "":
		await _select(p_who)
		opened3 = await _open_card_on(p_at, p_foe)
		text3 = _card_text()
	_rec("pitched_card", "selected %s, right-clicked %s at %s" % [p_who, p_foe, p_at],
		"the card up=%s; the server's own line: '%s'; on the card=%s; 'A great battle' on the card=%s; terms: %s" % [
			str(opened3), p_said, str(p_said != "" and text3.find(p_said) >= 0),
			str(text3.find("A great battle") >= 0), _last_words(text3, 320)],
		opened3 and p_said != "" and text3.find(p_said) >= 0 and text3.find("A great battle") < 0)
	await _shot("pitched_card", "an attack's card: a pitched battle, short of a great one")
	await _cancel_card()

	# 4 - the Help's terms
	var codex = _main.get("codex")
	var terms_text := ""
	if codex != null:
		codex.call("open", "terms")
		await _frames(20)
		terms_text = _text_of(codex)
	var found: Array = []
	for term in ["The last hour", "News of a battle", "Pursuit"]:
		if terms_text.find(term) >= 0:
			found.append(term)
	_rec("help_terms", "opened Help on its Terms page",
		"terms found: %s; 'three-quarters of its weight' there=%s; 'digits 1 to 9' there=%s" % [
			str(found), str(terms_text.find("three-quarters of its weight") >= 0), str(terms_text.find("digits 1 to 9") >= 0)],
		found.size() == 3 and terms_text.find("three-quarters of its weight") >= 0 and terms_text.find("digits 1 to 9") >= 0)
	await _shot("help_terms", "Help: the session's terms")
	if codex != null:
		codex.call("close")
	await _frames(10)


func _walk_oldsave() -> void:
	"""A save BA-3 wrote (HEAD aeae6967: the day of battle open after two
	clashes, awaiting our word), loaded by the client's own Load: the day is
	offered with the first day's line, a word is played, and its close tells
	nothing that was never counted."""
	var file := OS.get_environment("BA4_OLD_SAVE")
	var field := OS.get_environment("BA4_OLD_FIELD")
	# 2 - the client's own Load (the handler the save dialog's row calls)
	var ap_boot := _ap()
	_main.call("_on_load_save_selected", file)
	await _frames(6)
	await _settle(90000)
	await _frames(30)
	await _clear_boot_overlays()
	# (the load clears the log and writes the loaded campaign's own: the whole of it is read)
	var l = _log()
	var said: String = l.get_parsed_text() if l != null else ""
	_rec("old_save_loaded", "loaded '%s' through the client's own load" % file,
		"turn=%d; actions %d (the boot's) -> %d (the save's); 'Game loaded successfully.' in the log=%s" % [
			_turn(), ap_boot, _ap(), str(said.find("Game loaded successfully.") >= 0)],
		said.find("Game loaded successfully.") >= 0 and _turn() == 1 and _ap() == 3)

	# 3 - the province's panel on the day's field: the day is offered
	var panel_up := await _open_province_panel(field)
	var ptext := _panel_text()
	var press_meta := ""
	var break_meta := ""
	for m in _metas_in_text(_panel_source()):
		var meta := str((m as Dictionary).get("meta", ""))
		if meta.begins_with("do:@day:") and str((m as Dictionary).get("label", "")).find("presses") >= 0:
			press_meta = meta
		if meta.find("@word:break_off:") >= 0:
			break_meta = meta
	_rec("old_day_offered", "clicked %s on the map" % field,
		"the panel up=%s; the day's block on it=%s; a press chip=%s; a break-off chip=%s; panel: %s" % [
			str(panel_up), str(ptext.find("THE DAY AT") >= 0), str(press_meta != ""), str(break_meta != ""),
			_last_words(ptext, 200)],
		panel_up and ptext.find("THE DAY AT") >= 0 and press_meta != "" and break_meta != "")
	await _shot("old_day_offered", "an old save's open day, offered on its province's panel")
	if press_meta == "":
		return

	# 4 - the press, from the panel: the table comes with the clash and the day's first line
	var ap0 := _ap()
	_panel().get("content_area").emit_signal("meta_clicked", press_meta)
	await _frames(6)
	await _settle(60000)
	await _frames(12)
	await _commit_if_asked("press")
	await _answer_objection("press")
	var back := await _wait_chips_through_his_answer(120000)
	var day := _day()
	var rows := _day_rows()
	var plate := str((_dio().get("_data") as Dictionary).get("battle_name", "")) if _table_up() else ""
	_rec("old_day_pressed", "pressed the panel's chip (meta '%s')" % press_meta,
		"actions %d -> %d; the table up=%s; the chips back=%s; the plate: '%s'; the first row: '%s'; close: '%s'; the day: %s" % [
			ap0, _ap(), str(_table_up()), str(back), plate, str(rows["first"]).strip_edges().substr(0, 40),
			str(day.get("close", "")), _purses(day)],
		_table_up() and _ap() == ap0 and plate != "" and plate.find(" — the ") < 0 and str(day.get("close", "")) == ""
			and (not back or str(rows["first"]).begins_with("The day hangs, Sire.")), {"day": day})
	await _shot("old_day_pressed", "the old day's next clash: its own name, the first day's line above the chips")
	if not back:
		return

	# 5 - the digit 8 breaks off: the day closes and tells no tally it never kept
	await _key_press(KEY_8)
	await _frames(6)
	await _settle(60000)
	await _frames(24)
	await _wait_final(20000)
	var closing := _day()
	var told: Array = closing.get("told", []) if closing.get("told", null) is Array else []
	var tallies := 0
	for t in told:
		if t is Dictionary and str((t as Dictionary).get("kind", "")) == "tally":
			tallies += 1
	var on_table := str(_day_rows()["all"])
	_rec("old_day_closes", "pressed 8 on the table (Break off)",
		# (row BA, BA-5: a clash's OWN line now carries that clash's toll - "... of ours for ... of
		# his" - which is no tally of the day; the day's tally and its close say "of the enemy's")
		"the day open=%s, ended '%s', banner '%s'; tally lines told: %d; a day's tally ('of the enemy's') on the table=%s; close: '%s'" % [
			str(closing.get("open", "?")), str(closing.get("ended", "")), str(closing.get("banner", "")),
			tallies, str(on_table.find("of the enemy") >= 0), str(closing.get("close", ""))],
		str(closing.get("ended", "")) == "broke_off" and tallies == 0 and on_table.find("of the enemy") < 0
			and str(closing.get("close", "")) == "", {"day": closing})
	await _shot("old_day_closes", "the old day closed: how it ended, and no count it never kept")
	if _table_up():
		await _close_the_table()


# ─────────────────────────────────────────────────────────────────────────────
# Row BA, BA-5 "the finish", pressed in the real client (November 17, 2026)
# ─────────────────────────────────────────────────────────────────────────────
# Two more plans (BA4_PLAN):
#   finish  the Masséna board again (the `day` board's hunted campaign): the acts'
#          SPEED switch pressed while the opening plays (the clock doubles and is
#          given back); the day's head carries Berthier's READING and the lead's
#          cards say what their words DO; the word given sounds its own cue; the
#          log's "View the field" opens the day's LATEST clash (BA5-D2); the
#          province's panel says the reading too; "Break off" closes the day on
#          the latest clash's own table, and the close says whom the toll favoured
#          and what kind of day it was; the lead's card on the Generals screen
#          lists the day among HIS DAYS.
#   oneday  the same board with a second enemy corps beside the lead (ruling 9):
#          with his day open, the attack card on the second corps says that a
#          battle there would be a single clash with no day of its own; its Send
#          fights that battle as an ordinary order and the open day stands.

func _table_sig(data) -> String:
	"""A tableau by what stands on it: its name, both sides' losses, its beats."""
	if not (data is Dictionary):
		return ""
	var d: Dictionary = data
	var beats := 0
	var script = d.get("script", null)
	if script is Dictionary:
		for act in (script as Dictionary).get("acts", []):
			if act is Dictionary and (act as Dictionary).get("beats", null) is Array:
				beats += ((act as Dictionary)["beats"] as Array).size()
	var atk = d.get("attacker", {})
	var dfd = d.get("defender", {})
	return "%s|%d|%d|%d" % [str(d.get("battle_name", "")),
		int((atk as Dictionary).get("casualties_total", 0)) if atk is Dictionary else 0,
		int((dfd as Dictionary).get("casualties_total", 0)) if dfd is Dictionary else 0, beats]


func _head_text() -> String:
	var acts = _acts()
	var panel = acts.get("_day_panel") if acts != null else null
	if panel == null or not is_instance_valid(panel):
		return ""
	var head = (panel as Node).get_node_or_null("DayHead")
	return _plain((head as RichTextLabel).get_parsed_text()) if head != null else ""


func _cues_started() -> Array:
	"""The sound files the table's own cue road has started, by file name."""
	var out: Array = []
	var dio = _dio()
	if dio == null:
		return out
	for p in dio.get("_own_cues_started"):
		if is_instance_valid(p) and p.stream != null:
			out.append(str(p.stream.resource_path).get_file())
	return out


func _cue_file(cue: String) -> String:
	var row = AudioManager.CUES.get(cue, {})
	var files = (row as Dictionary).get("files", []) if row is Dictionary else []
	return str(files[0]).get_file() if files is Array and not (files as Array).is_empty() else ""


func _ba5_speed() -> void:
	"""While the acts play: the table's own speed switch, pressed and pressed again."""
	var start := Time.get_ticks_msec()
	var sw = null
	while Time.get_ticks_msec() - start < 90000:
		await process_frame
		var acts = _acts()
		if _table_up() and acts != null and not bool(_dio().get("_final")):
			var found = acts.get("_speed_switch")
			if found != null and is_instance_valid(found) and (found as CanvasItem).is_visible_in_tree():
				sw = found
				break
		elif _table_up() and bool(_dio().get("_final")):
			break
	if sw == null:
		_rec("ba5_speed", "looked for the speed switch while the acts played", "no table was playing its acts", false)
		return
	await _frames(20)          # well into the acts
	var clock0: float = Engine.time_scale
	var text0 := str(sw.text)
	(sw as Button).emit_signal("pressed")
	await _frames(3)
	var clock1: float = Engine.time_scale
	var setting1 := str(UiSettings.get_battle_speed())
	var playing1: bool = not bool(_dio().get("_final"))
	var text1 := str(sw.text) if is_instance_valid(sw) else "?"
	var pressed_again := false
	if is_instance_valid(sw) and (sw as CanvasItem).is_visible_in_tree():
		(sw as Button).emit_signal("pressed")
		pressed_again = true
	await _frames(3)
	var clock2: float = Engine.time_scale
	_rec("ba5_speed", "pressed the table's speed switch while the acts played, then again",
		"the switch read '%s' -> '%s'; the engine's clock %.1f -> %.1f -> %.1f; the setting after the first press '%s' and now '%s'; the acts still played=%s; pressed again=%s" % [
			text0, text1, clock0, clock1, clock2, setting1, str(UiSettings.get_battle_speed()), str(playing1), str(pressed_again)],
		is_equal_approx(clock0, 1.0) and is_equal_approx(clock1, 2.0) and is_equal_approx(clock2, 1.0)
			and setting1 == "x2" and playing1 and pressed_again and str(UiSettings.get_battle_speed()) == "x1"
			and text0 == "Speed ×1" and text1 == "Speed ×2")
	await _shot("ba5_speed", "the acts play; the speed switch stands in Close's room")


func _walk_finish() -> void:
	"""BA-5's own rules of the day, pressed on the Masséna board."""
	await _select(LEAD)
	var opened := await _open_attack_card()
	if opened:
		var sendb = _card().get("send_button")
		if sendb != null and sendb.visible and not sendb.disabled:
			sendb.emit_signal("pressed")
	await _frames(6)
	await _settle(90000)
	await _frames(12)
	await _answer_objection("attack")
	await _commit_if_asked("attack")
	# 1 - the acts' speed, while the opening plays
	await _ba5_speed()
	var up := await _wait_chips_through_his_answer(150000)
	var day := _day()
	_rec("ba5_day_opens", "pressed the card's Send (%s, attack %s)" % [LEAD, FOE],
		"the table up=%s; the panel offers=%s; the clock at rest %.1f; the day: %s" % [
			str(_table_up()), str(up), Engine.time_scale, _purses(day)],
		up and bool(day.get("open", false)) and is_equal_approx(Engine.time_scale, 1.0), {"day": day})
	if not up:
		await _shot("ba5_no_day", "the day did not open as hunted")
		return
	var plate := str(_dio().get("_data").get("battle_name", ""))

	# 2 - Berthier's reading, at the end of the stakes that head the panel (the second reading:
	# each purse in words, right above the words they govern)
	var head := _head_text()
	var reading = day.get("reading", null)
	var line := str((reading as Dictionary).get("line", "")) if reading is Dictionary else ""
	var purse := "%d of %d points" % [int(day.get("ours", 0)), int(day.get("ours_of", 0))]
	_rec("ba5_reading", "read the day's head: the stakes, at the panel's top",
		"the head: '%s'; the server's reading: '%s'; our purse in words: '%s'" % [head.strip_edges(), line, purse],
		line in ["he will strike", "he may strike", "he will not strike"] and head.strip_edges().ends_with(line)
			and head.find(purse) >= 0)

	# 3 - a card says what its word does
	var press_i := _chip_index(day, "press", "")
	var press_chip: Dictionary = day.get("chips", [])[press_i] if press_i >= 0 else {}
	var does := str(press_chip.get("does", ""))
	var rows := _day_rows()
	var own := str(rows["own"])
	var exits := str(rows["exits"])
	_rec("ba5_cards", "read the lead's own cards (row C) and the exits (row E)",
		"row C: %s | the server's `does` for the press: '%s' | row E: %s" % [own.strip_edges(), does, exits.strip_edges()],
		does != "" and own.to_lower().find(does.to_lower()) >= 0 and own.find("1 point") >= 0
			and (exits.find("he keeps the field") >= 0 or exits.find("8 Break off") >= 0))
	await _shot("ba5_the_table_tells", "the head reads him; the cards say what their words do")

	# 4 - the word given sounds its own cue (the bugle), once
	var bugle := _cue_file("bugle_to_arms")
	var had_bugle: bool = _cues_started().has(bugle)
	var words0 := _words.size()
	await _key_press(KEY_1)
	await _frames(2)
	var sounded: Array = _cues_started()
	await _settle(60000)
	await _frames(12)
	await _commit_if_asked("press")
	await _answer_objection("press")
	var back := await _wait_chips_through_his_answer(150000)
	day = _day()
	_rec("ba5_word_sounds", "pressed 1 on the table (the lead presses)",
		"words given %s; the cues the table is sounding right after the press: %s (the word's own: %s; sounding before it=%s); the chips back=%s" % [
			str(_words.slice(words0)), str(sounded), bugle, str(had_bugle), str(back)],
		_words.size() == words0 + 1 and sounded.has(bugle) and not had_bugle)
	if not back:
		_rec("ba5_decided_early", "the press closed the day on this seed", _purses(day), false)
		return

	# 5 - BA5-D2: the log's "View the field" opens the day's LATEST clash
	# (the day's latest clash is the table that STANDS now, with the chips back: his
	# answering clash where he struck, else our own)
	var tables = _main.get("_day_tables")
	var stored_sig := _table_sig((tables as Dictionary).get(FOE, null)) if tables is Dictionary else ""
	var latest_sig := _table_sig(_dio().get("_data"))
	var closed := await _close_the_table()
	var viewed := _press_log_chip("View the field")
	await _frames(12)
	await _settle(20000)
	await _wait_final(30000)
	var viewed_sig := _table_sig(_dio().get("_data")) if _table_up() else ""
	_rec("ba5_d2_view_the_field", "closed the table, pressed the log's 'View the field'",
		"closed=%s; the link pressed=%s; the table up=%s; the day's latest clash (the table that stood): %s; the client's own store of it: %s; the table the link opened: %s" % [
			str(closed), str(viewed), str(_table_up()), latest_sig, stored_sig, viewed_sig],
		closed and viewed and _table_up() and latest_sig != "" and viewed_sig == latest_sig and stored_sig == latest_sig)
	await _shot("ba5_d2_view_the_field", "the log's link opens the day's latest clash")
	await _close_the_table()

	# 6 - the province's panel says the reading too
	var day_field := str(day.get("field", FIELD))
	var panel_up := await _open_province_panel(day_field)
	var ptext := _panel_text()
	_rec("ba5_panel_reading", "clicked %s on the map (the day's field)" % day_field,
		"the panel up=%s; the day's block=%s; Berthier's reading on it=%s; panel: %s" % [
			str(panel_up), str(ptext.find("THE DAY AT") >= 0), str(ptext.find("Berthier's reading: he ") >= 0),
			_last_words(ptext, 240)],
		panel_up and ptext.find("THE DAY AT") >= 0 and ptext.find("Berthier's reading: he ") >= 0)

	# 7 - "Break off" from the panel: the closing table is the latest clash's own, and the
	# close says whom the toll favoured and what kind of day it was
	var source := _panel_source()
	var meta := ""
	for m in _metas_in_text(source):
		if str((m as Dictionary).get("meta", "")).find("@word:break_off:") >= 0:
			meta = str((m as Dictionary).get("meta", ""))
	var boots := _cue_file("boots")
	var had_boots: bool = _cues_started().has(boots)
	if meta != "":
		_panel().get("content_area").emit_signal("meta_clicked", meta)
	# the close's own cue is short (it is cut at 1.6 s and its player freed): listened
	# for on every frame until the closing table stands
	var heard_boots := false
	var listen := Time.get_ticks_msec()
	while Time.get_ticks_msec() - listen < 45000:
		await process_frame
		if _cues_started().has(boots):
			heard_boots = true
		if heard_boots or (_table_up() and bool(_dio().get("_final")) and not bool(_day().get("open", true))):
			break
	await _frames(6)
	await _settle(60000)
	await _frames(24)
	await _wait_final(30000)
	var closing := _day()
	var closing_sig := _table_sig(_dio().get("_data")) if _table_up() else ""
	var told: Array = closing.get("told", []) if closing.get("told", null) is Array else []
	var shape := ""
	for t in told:
		if t is Dictionary and str((t as Dictionary).get("kind", "")) == "shape":
			shape = str((t as Dictionary).get("line", ""))
	_rec("ba5_d2_the_close", "pressed the panel's 'Break off' (meta '%s')" % meta,
		"the table up=%s; ended '%s'; the closing table: %s (the day's latest clash: %s); the close's own line: '%s'; the close: '%s'; cues at the close: %s" % [
			str(_table_up()), str(closing.get("ended", "")), closing_sig, latest_sig, shape,
			str(closing.get("close", "")), "heard=%s (the close's own: %s; sounding before it=%s)" % [str(heard_boots), boots, str(had_boots)]],
		meta != "" and str(closing.get("ended", "")) == "broke_off" and closing_sig == latest_sig
			and shape.find("The attack was given up") >= 0 and str(closing.get("close", "")).ends_with(shape)
			and (shape.to_lower().find("better of the toll") >= 0 or shape.find("The toll stood even") >= 0)
			and heard_boots and not had_boots,
		{"day": closing})
	await _shot("ba5_d2_the_close", "the day closed on its latest clash; the close says what kind of day it was")
	await _close_the_table()

	# 8 - a marshal's days: the lead's card on the Generals screen
	var top = _main.get("top_bar")
	var words := ""
	if top != null:
		top.toggle_screen("generals")
		await _frames(10)
		await _settle(30000)
		var screen = top.screens.get("generals", null)
		if screen != null:
			screen.select_marshal(LEAD)
			await _frames(12)
			await _settle(15000)
			for n in _all_nodes(screen):
				if n is RichTextLabel and (n as CanvasItem).is_visible_in_tree():
					words += _plain((n as RichTextLabel).get_parsed_text()) + "\n"
	var at := words.find("His days")
	var days_text := words.substr(at, 420) if at >= 0 else ""
	_rec("ba5_his_days", "opened the Generals screen and selected %s" % LEAD,
		"the card's block: %s" % days_text.strip_edges().replace("\n", " / "),
		at >= 0 and plate != "" and days_text.find(plate) >= 0 and days_text.find("against") >= 0
			and days_text.find("The attack was given up") >= 0)
	await _shot("ba5_his_days", "the lead's card: his days")
	if top != null:
		top.toggle_screen("generals")
		await _frames(8)


func _walk_one_day() -> void:
	"""Ruling 9: the card's line for a lead who already holds a day, pressed."""
	var other := OS.get_environment("BA5_OTHER")
	var other_at := OS.get_environment("BA5_OTHER_AT")
	await _select(LEAD)
	var opened := await _open_attack_card()
	if opened:
		var sendb = _card().get("send_button")
		if sendb != null and sendb.visible and not sendb.disabled:
			sendb.emit_signal("pressed")
	await _frames(6)
	await _settle(90000)
	await _frames(12)
	await _answer_objection("attack")
	await _commit_if_asked("attack")
	var up := await _wait_chips_through_his_answer(150000)
	var day := _day()
	_rec("one_day_opens", "pressed the card's Send (%s, attack %s)" % [LEAD, FOE],
		"the table up=%s; the panel offers=%s; the day: %s" % [str(_table_up()), str(up), _purses(day)],
		up and bool(day.get("open", false)), {"day": day})
	if not up:
		await _shot("one_day_no_day", "the day did not open as hunted")
		return
	var closed := await _close_the_table()

	# the card on the SECOND corps, the lead's day still open
	await _select(LEAD)
	var card_up := await _open_card_on(other_at, other)
	var card := _card_text()
	_rec("one_day_card", "closed the table (%s), selected %s, right-clicked %s at %s" % [str(closed), LEAD, other, other_at],
		"the card up=%s; its terms: %s" % [str(card_up), _last_words(card, 320)],
		card_up and card.find("is still open") >= 0
			and card.find("a battle here would be a single clash, with no day of its own") >= 0
			and card.find("Should he win it and advance, that day ends where it stands.") >= 0
			and card.find("1 action") >= 0 and card.find("word of the day") < 0)
	await _shot("one_day_card", "the attack card for a lead who already holds a day")

	# its Send: an ordinary battle - a single clash that opens no day (BA5-X1: though the
	# lead wins it on points and advances), and the first day, which he has left, ends
	# at once and is told with the battle
	var ap0 := _ap()
	var log0 := _log_len()
	var lead_at0 := ""
	var words0 := _words.size()
	if card_up:
		var send2 = _card().get("send_button")
		if send2 != null and send2.visible and not send2.disabled:
			send2.emit_signal("pressed")
	await _frames(6)
	await _settle(90000)
	await _frames(12)
	await _answer_objection("second")
	await _commit_if_asked("second")
	await _wait_final(120000)
	var second: Dictionary = _dio().get("_data") if _table_up() and _dio().get("_data") is Dictionary else {}
	var second_day = second.get("day", null)
	var tables = _main.get("_day_tables")
	var keys: Array = (tables as Dictionary).keys() if tables is Dictionary else []
	var alone := ""
	var script = second.get("script", null)
	if script is Dictionary:
		for act in (script as Dictionary).get("acts", []):
			if act is Dictionary:
				for beat in (act as Dictionary).get("beats", []):
					if beat is Dictionary and str((beat as Dictionary).get("text", "")).find("opens none of its own") >= 0:
						alone = str((beat as Dictionary).get("text", ""))
	var told_since := _log_since(log0)
	var advanced := false          # the script says so: "advances into ..."
	if script is Dictionary:
		for act in (script as Dictionary).get("acts", []):
			if act is Dictionary:
				for beat in (act as Dictionary).get("beats", []):
					if beat is Dictionary and str((beat as Dictionary).get("kind", "")) == "advance_to":
						advanced = true
	_rec("one_day_pressed", "pressed the card's Send (%s, attack %s)" % [LEAD, other],
		"the table up=%s on '%s' (%s); actions %d -> %d; words of a day given %d; a day's block on this table=%s; the days the client holds: %s; the script's own line: '%s'; the log says he marched from the first field=%s" % [
			str(_table_up()), str(second.get("battle_name", "")), str(second.get("outcome", "")), ap0, _ap(), _words.size() - words0,
			str(second_day is Dictionary), str(keys), alone,
			"%s (he advanced=%s)" % [str(told_since.find("marched from the field at") >= 0), str(advanced)]],
		_table_up() and str(second.get("battle_name", "")) != "" and _ap() == ap0 - 1 and _words.size() == words0
			and not (second_day is Dictionary) and not keys.has(other)
			# (the review, BA5-X20) a lead whose advance ends his first day: the battle says he marched from it
			and alone.find("has marched from his day" if advanced else "is still open") >= 0
			and alone.find("this clash opens none of its own") >= 0
			and (told_since.find("marched from the field at") >= 0) == advanced)
	await _shot("one_day_pressed", "the second battle: a single clash, no day of its own")
	await _close_the_table()

	# the first day is over (he left its ground): its province's panel offers no word of it
	var day_field := str(day.get("field", FIELD))
	var panel_up := await _open_province_panel(day_field)
	var ptext := _panel_text()
	_rec("one_day_first_is_over", "clicked %s on the map (the first day's field)" % day_field,
		"the panel up=%s; a day's block on it=%s; the days the client holds: %s" % [
			str(panel_up), str(ptext.find("THE DAY AT") >= 0), str((_main.get("_day_tables") as Dictionary).keys())],
		panel_up and (ptext.find("THE DAY AT") < 0) == advanced)


func _walk() -> void:
	for pair in [["BA4_LEAD", "LEAD"], ["BA4_FOE", "FOE"], ["BA4_FIELD", "FIELD"], ["BA4_PLAN", "PLAN"]]:
		var given := OS.get_environment(pair[0])
		if given != "":
			set(pair[1], given)
	var dir_env := OS.get_environment("BA4_WALK_OUT")
	_dir = dir_env if dir_env != "" else ProjectSettings.globalize_path(OUT_DEFAULT)
	DirAccess.make_dir_recursive_absolute(_dir)
	root.mode = Window.MODE_WINDOWED
	root.position = Vector2i(5200, 20)
	root.size = Vector2i(1920, 1080)
	await _frames(4)
	var packed: PackedScene = load("res://scenes/main.tscn")
	_main = packed.instantiate()
	root.add_child(_main)
	var dio0 = _main.get("battle_diorama")
	if dio0 != null:
		dio0.word_given.connect(func(command: String): _words.append(command))
	var start := Time.get_ticks_msec()
	while Time.get_ticks_msec() - start < 90000:
		await process_frame
		if bool(_main.get("_initial_map_bootstrapped")) and _main.get("command_input").editable:
			break
	await _settle()
	_out["backend"] = Utils.backend_url()
	_out["booted"] = bool(_main.get("_initial_map_bootstrapped"))
	await _frames(10)
	await _clear_boot_overlays()
	_rec("boot", "booted the real main.tscn against the sandboxed backend",
		"booted=%s turn=%d actions=%d" % [str(_out["booted"]), _turn(), _ap()], bool(_out["booted"]))
	if PLAN == "roads":
		await _walk_roads()
	elif PLAN == "oldsave":
		await _walk_oldsave()
	elif PLAN == "finish":       # row BA, BA-5
		await _walk_finish()
	elif PLAN == "oneday":       # row BA, BA-5 (ruling 9)
		await _walk_one_day()
	else:
		await _walk_day()
	_finish()


func _finish():
	if _done:
		return
	_done = true
	_out["ms"] = Time.get_ticks_msec() - _t0
	_out["final_turn"] = _turn()
	_out["words"] = _words
	var path := _dir.path_join("walk.json") if _dir != "" else ""
	if path != "":
		var f := FileAccess.open(path, FileAccess.WRITE)
		if f != null:
			f.store_string(JSON.stringify(_out, "  "))
			f.close()
	quit(1 if _out.has("error") else 0)
