extends SceneTree
# Row BA, BA-3 - the day's points, pressed in the real client (November 15, 2026)
# - modeled on tools/ba2_mode_c_walk.gd (WRITTEN, NOT RUN: it needs a windowed Godot).
#
#   $env:SOVEREIGN_PORT   = "8006"        # a sandboxed backend listening there (never 8005)
#   $env:BA3_WALK_OUT     = "<abs dir>"   # frames + walk.json land here
#   <godot> --audio-driver Dummy --windowed --resolution 1920x1080 \
#           --path godot-client/project-sovereign --script <abs>/tools/ba3_mode_c_walk.gd
#
# Do not start it by hand: `tools/ba3_mode_c_walk.py` hunts a campaign seed whose
# opening attack leaves a day hanging (the day's dice are the campaign's, so the
# real backend, started with that seed, fights the same battle), starts the
# sandboxed backend on it and runs this.
#
# The REAL main.tscn against that backend (the 1805 scenario with Masséna in the
# Tyrol and the Archduke Charles in Carniola, `ba3_mode_c_walk.write_scenario`).
# Steps: boot; Masséna's attack card on the Archduke Charles at Carniola, Send; the table plays and the DAY'S PANEL stands at rest (both
# purses, the chips); the lead's press (the table chip "Massena presses" — a typed
# order through the ordinary road, with the table still up); then the word chip
# "Leave it to Massena" (POST /battle_day/word). Each step records {step, did, saw,
# ok} in walk.json["results"] (and a frame row in walk.json["steps"]), tolerates
# failure, and the walk never aborts. What it reads: the table's own `_data.day`
# (the purses, whose word it is, the chips), the actions before and after
# (`action_info.cost == 0`: a word costs points, never an action), whether the
# table is still up, and the word given to `word_given` (counted by a
# connection made here, never by a picture).

const WALL_LIMIT_MS := 900000
const OUT_DEFAULT := "res://../../docs/audits/ba3_mode_c_2026_11_15"
# the board comes from the runner (BA3_LEAD / BA3_FOE / BA3_FIELD): Masséna against the
# Archduke Charles at Carniola by default (`--board ulm`: Ney against Mack at Swabia)
var FIELD := "Carniola"
var FOE := "ArchdukeCharles"
var LEAD := "Massena"
var PLAN := "leave"      # "guard" (the real Ulm opening) or "leave" (the Masséna board)
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
	var file := "BA3_WALK_%02d_%s_2026_11_15.jpg" % [_n, name]
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


func _walk_dawn() -> void:
	"""The DEFENDED day, at dawn, through the real controls only: End Turn, the
	enemy phase's dialog, the rail's notice, the day's table; then "<lead> digs
	in" and "Fall back". A control that cannot be reached the way a player
	reaches it fails its step (the handler behind it is never called)."""
	var lead_shown: String = LEAD
	# 2 - End Turn (the lapse gate asks once for a corps with no orders: pressed again, as a player does)
	var turn0 := _turn()
	var ap0 := _ap()
	var btn = _main.get("end_turn_button")
	var gate := false
	var presses := 0
	var dlg = _main.get("enemy_phase_dialog")
	var log0 := _log_len()
	var gate_said := ""
	if btn != null and btn.visible and not btn.disabled and dlg != null:
		for _i in range(2):
			btn.emit_signal("pressed")
			presses += 1
			if presses == 1:
				await _frames(10)
				gate_said = _log_since(log0)
			await _frames(6)
			await _settle(90000)
			await _frames(10)
			if bool(dlg.visible):
				break
			if bool(_main.get("_awaiting_end_turn_confirmation")):
				gate = true
	var start := Time.get_ticks_msec()
	while dlg != null and not bool(dlg.visible) and Time.get_ticks_msec() - start < 60000:
		await process_frame
	var phase_up: bool = dlg != null and bool(dlg.visible)
	_rec("end_turn", "pressed the End Turn button (%d press(es))" % presses,
		"turn %d -> %d; the lapse gate stood=%s and spoke of a day=%s; the enemy phase's dialog up=%s; the log: %s" % [
			turn0, _turn(), str(gate), str(gate_said.find("Take the field") >= 0 or gate_said.find("still hangs") >= 0),
			str(phase_up), _last_words(_log_tail(), 200)],
		btn != null and phase_up and gate_said.find("Take the field") < 0 and gate_said.find("still hangs") < 0)
	await _shot("enemy_phase", "the enemy phase's dialog")
	if not phase_up:
		_finish()
		return

	# 3 - the dialog's battle row says the day awaits us
	var said := _text_of(dlg)
	# K13: the row's badge is the day's own banner ("THE DAY HANGS"), never DEFEAT / VICTORY / STALEMATE
	var badge_ok: bool = said.find("THE DAY HANGS") >= 0
	var row_ok: bool = said.find("the day awaits your word") >= 0 and badge_ok
	var row_line := ""
	for ln in said.split("\n"):
		if str(ln).find("awaits your word") >= 0:
			row_line = str(ln).strip_edges()
	_rec("enemy_row", "read the enemy phase's dialog for the great battle's row",
		"row says the day awaits us (badge 'THE DAY HANGS'=%s) ok=%s ('%s')" % [str(badge_ok), str(row_ok), row_line], row_ok,
		{"dialog_tail": said.substr(maxi(0, said.length() - 600))})

	# 3b - K6: the dialog's own "⚔ View the field" link, pressed once BEFORE Continue: its table
	# offers the chips (the day as the enemy phase's tableau remembers it)
	var link := ""
	var link_box = null
	for n in _all_nodes(dlg):
		if n is RichTextLabel and _meta_labelled(n, "View the field") != "":
			link = _meta_labelled(n, "View the field")
			link_box = n
			break
	var field_up := false
	var field_day := {}
	if link != "":
		link_box.emit_signal("meta_clicked", link)
		field_up = await _wait_for_chips(90000)
		field_day = _day()
		await _shot("view_the_field", "the dialog's View the field: the table over the dialog")
		await _close_the_table()
	_rec("view_field", "pressed the enemy phase dialog's 'View the field' link before Continue",
		"the link stood=%s; its table offers the words=%s; the day: %s; chips: %s" % [
			str(link != ""), str(field_up), _purses(field_day), str(_chips_of(field_day))],
		link != "" and field_up and bool(field_day.get("open", false)), {"day": field_day})

	# 4 - leave the dialog as a player does: its Continue button. The morning battle's
	# table then RISES BY ITSELF (a great battle is `dramatic`): it is the dawn's offer,
	# and the server has written the day as it stands at dawn onto it.
	var cont = dlg.get("continue_button")
	if cont != null and cont.visible and not cont.disabled:
		cont.emit_signal("pressed")
	await _frames(8)
	await _settle(60000)
	var up := await _wait_for_chips(120000)
	var day := _day()
	_rec("leave_dialog", "pressed the dialog's Continue button",
		"dialog still up=%s; the morning table rose by itself=%s; its panel offers the words=%s (the dawn's block: %s; chips: %s)" % [
			str(bool(dlg.visible)), str(_table_up()), str(up), _purses(day), str(_chips_of(day))],
		not bool(dlg.visible) and up and str(day.get("side", "")) == "defence" and bool(day.get("open", false))
			and str(day.get("awaits", "")) == "ours", {"day": day})
	await _shot("the_dawn_table", "the morning battle's table, risen by itself after the dialog")
	if not up:
		_finish()
		return

	# 5 - the panel at rest: the banner, both purses, row C (strikes back), the exits (Fall back)
	var dio = _dio()
	var acts = dio.get("_acts")
	var banner_now: String = str(dio.get("_banner").text)
	var row_c := ""
	if acts != null and acts.get("_day_chips") != null and is_instance_valid(acts.get("_day_chips")):
		row_c = _plain((acts.get("_day_chips") as RichTextLabel).get_parsed_text())
	var row_e := ""
	if acts != null and acts.get("_day_exits") != null and is_instance_valid(acts.get("_day_exits")):
		row_e = _plain((acts.get("_day_exits") as RichTextLabel).get_parsed_text())
	var fall_i := _chip_index(day, "break_off", "")
	var dig_i := _chip_index(day, "dig_in", "")
	var strike_i := _chip_index(day, "press", "")
	_rec("panel_at_rest", "read the day's panel at rest",
		"banner '%s'; %s of %s / %s of %s; row C: %s; exits: %s; 'strikes back' lit=%s; 'digs in' lit=%s; 'Fall back' lit=%s" % [
			banner_now, str(day.get("ours", "?")), str(day.get("ours_of", "?")), str(day.get("theirs", "?")),
			str(day.get("theirs_of", "?")), row_c, row_e, str(strike_i >= 0), str(dig_i >= 0), str(fall_i >= 0)],
		banner_now == "THE DAY HANGS" and row_c.find("strikes back") >= 0 and row_e.find("Fall back") >= 0
			and strike_i >= 0 and dig_i >= 0 and fall_i >= 0,
		{"day": day})
	await _shot("day_panel", "the defended day's panel at rest")

	# 6 - "<lead> digs in": a typed order (the lead objects: Insist), one point, no action;
	# his answer is a clash on the same table
	var ours_b := int(day.get("ours", -1))
	var ap_b := _ap()
	var words_b := _words.size()
	var pressed := dig_i >= 0 and _press(dig_i)
	await _frames(6)
	await _settle(60000)
	await _frames(12)
	var objected := await _answer_objection("dig_in")
	await _commit_if_asked("dig_in")
	var back := await _wait_for_chips(120000)
	var after := _day()
	var told: Array = after.get("told", []) if after.get("told", null) is Array else []
	var his_line := ""
	if not told.is_empty():
		his_line = str((told[told.size() - 1] as Dictionary).get("line", ""))
	# (the cost is NOT read here: the objection's answer comes by /respond_to_objection and
	# `_last_command_response` is the command's, not that answer's — the actions and the purse are the proof)
	_rec("dig_in", "pressed '%s digs in' (row C)" % lead_shown,
		"pressed=%s; objected=%s; words %s; actions %d -> %d (no cost read on the objection's road: the actions held); purses %d -> %s; his answer: '%s'; the table up=%s, chips back=%s, follows=%s" % [
			str(pressed), str(objected), str(_words.slice(words_b)), ap_b, _ap(), ours_b, _purses(after),
			his_line, str(_table_up()), str(back), str(after.get("follows", false))],
		pressed and _words.size() == words_b + 1 and _ap() == ap_b
			and int(after.get("ours", -1)) == ours_b - 1 and back,
		{"day": after})
	await _shot("after_dig_in", "his answer on the same table")
	if not (bool(after.get("open", false)) and str(after.get("awaits", "")) == "ours"):
		_rec("fall_back", "the day no longer awaits our word after his answer",
			"ended '%s'; banner '%s'" % [str(after.get("ended", "")), str(dio.get("_banner").text)], true,
			{"day": after})
		_finish()
		return

	# 7 - CLOSE the table with the day still open (its own Close button), then the SECOND road:
	# the rail's notice, "Take the field", the table back settled with its chips
	var closed_ok := await _close_the_table()
	await _clear_boot_overlays()
	# the turn's own tail raises the letter-book ("PENDING ENVOYS"): a modal; closed by its own
	# Close button, as a player closes it — any other modal the same way, or the step fails naming it
	var modals := await _close_modals()
	var field_s := str(day.get("field_shown", ""))
	var lead_s := str(day.get("lead_shown", lead_shown))
	# K12 - End Turn WITH the day open: the gate stops the turn; its warning (which also speaks of
	# the unanswered envoys, in the same message) holds the day's sentence, "The day at <field> still
	# hangs — <lead> holds <N point(s)>" (or "may still stand, fall back or break off"), and the log
	# carries a "Take the field — <field>" chip (`dayopen:<enemy>`) that opens the table
	var log1 := _log_len()
	var msg1 := _log_msgs()
	var turn1 := _turn()
	var btn2 = _main.get("end_turn_button")
	var pressable: bool = closed_ok and str(modals.get("stuck", "")) == "" and btn2 != null and btn2.visible and not btn2.disabled
	if pressable:
		btn2.emit_signal("pressed")
		await _frames(10)
		await _settle(30000)
		await _frames(10)
	var gate2 := _log_since(log1)
	var stopped: bool = pressable and not bool(dlg.visible) and _turn() == turn1
	var chip_meta := _log_meta_labelled("Take the field", msg1)
	var sentence_ok: bool = gate2.find("The day at " + field_s) >= 0 and gate2.find("still hangs") >= 0 \
		and (gate2.find(lead_s + " holds") >= 0 or gate2.find(lead_s + " may still stand") >= 0) \
		and gate2.find("answers alone") >= 0
	_rec("day_gate", "closed the table and the modals the turn's tail raised (%s), then pressed End Turn once with the day open" % str(modals.get("closed", [])),
		"modal stuck='%s'; the turn stopped=%s (turn %d -> %d); the gate's sentence in its message: %s; the day's sentence ok=%s; a 'Take the field' chip (%s) in the log=%s" % [
			str(modals.get("stuck", "")), str(stopped), turn1, _turn(), _last_words(gate2, 420), str(sentence_ok),
			chip_meta, str(chip_meta != "")],
		stopped and sentence_ok and chip_meta.begins_with("dayopen:"))
	if chip_meta != "":
		_log().emit_signal("meta_clicked", chip_meta)
		var chip_up := await _wait_for_chips(90000)
		var cday := _day()
		_rec("gate_chip", "pressed the log's 'Take the field' chip",
			"the table is up=%s with its chips=%s; the day: %s" % [str(_table_up()), str(chip_up), _purses(cday)],
			chip_up and bool(cday.get("open", false)), {"day": cday})
		await _shot("the_table_from_the_log", "the table opened from the gate's own chip")
		closed_ok = await _close_the_table()
		await _clear_boot_overlays()
		var modals2 := await _close_modals()
		if str(modals2.get("stuck", "")) != "":
			closed_ok = false
	var icon = _notice_button("battle_day_awaits")
	var shown_types: Array = []
	var bar = _main.get("notification_bar")
	if bar != null:
		for n in bar.current_notifications:
			if n is Dictionary:
				shown_types.append(str(n.get("type", "")))
	var take = null
	if closed_ok and icon != null:
		icon.emit_signal("pressed")
		await _frames(10)
		take = _button_named(bar.expanded_panel, "Take the field")
	_rec("notice", "closed the table (the day still open), found the 'battle_day_awaits' icon on the rail and opened it",
		"table closed=%s; the icon on the rail=%s; notices held: %s; 'Take the field' reachable=%s" % [
			str(closed_ok), str(icon != null), str(shown_types), str(take != null)],
		closed_ok and icon != null and take != null)
	await _shot("the_notice", "the rail's notice for the day")
	if take == null:
		_finish()
		return
	take.emit_signal("pressed")
	var again := await _wait_for_chips(90000)
	var day2 := _day()
	_rec("take_the_field", "pressed 'Take the field'",
		"the table is back=%s, final with its chips=%s; the day: %s; chips: %s" % [
			str(_table_up()), str(again), _purses(day2), str(_chips_of(day2))],
		again and bool(day2.get("open", false)) and str(day2.get("awaits", "")) == "ours" and _chip_index(day2, "break_off", "") >= 0,
		{"day": day2})
	await _shot("the_table_again", "the table back from the notice: settled, with its chips")
	if not again:
		_finish()
		return

	# 8 - "Fall back": the day closes, the lead has moved, no action spent
	var fb := _chip_index(day2, "break_off", "")
	var ap_f := _ap()
	var words_f := _words.size()
	var fpressed := fb >= 0 and _press(fb)
	await _frames(6)
	await _settle(60000)
	await _frames(12)
	var obj_f := await _answer_objection("fall_back")
	# the command's response is routed through the incoming-proposal road FIRST (the game's standing
	# order for any command): a court's proposal may interpose its popup, and the day's closing table
	# waits in the stash until it is answered. Set it aside as a player does (its own dismiss button),
	# naming the court; any other modal likewise.
	var interposed := ""
	var proposal = _main.get("incoming_proposal_popup")
	if proposal != null and bool(proposal.visible):
		interposed = _text_of(proposal).substr(0, 160)
		await _shot("after_fall_back_popup", "an envoy's proposal interposes before the closing table")
	var set_aside := await _close_modals()
	var table_up := false
	var wait_start := Time.get_ticks_msec()
	while Time.get_ticks_msec() - wait_start < 60000:
		await process_frame
		var d_now := _day()
		var dio_now = _dio()
		if dio_now != null and bool(dio_now.visible) and bool(dio_now.get("_final")) \
				and str(d_now.get("ended", "")) == "fell_back":
			table_up = true
			break
	await _frames(10)
	var closed := _day()
	var cost_f := _cost_of_last()
	if obj_f:
		cost_f = 0     # an objection's answer comes by /respond_to_objection: the actions held (checked below) are the proof
	var banner_f: String = str(_dio().get("_banner").text) if _dio() != null else ""
	var chips_left: int = (closed.get("chips", []) as Array).size() if closed.get("chips", null) is Array else 0
	_rec("fall_back", "pressed 'Fall back' (the exits row)",
		"pressed=%s; words %s; actions %d -> %d (cost %d); an envoy's popup interposed: %s; modals set aside: %s (stuck '%s'); the closing table came up final=%s; ended '%s'; banner '%s'; chips left %d; the log: %s" % [
			str(fpressed), str(_words.slice(words_f)), ap_f, _ap(), cost_f,
			("'" + interposed + "'") if interposed != "" else "no", str(set_aside.get("closed", [])),
			str(set_aside.get("stuck", "")), str(table_up), str(closed.get("ended", "")), banner_f, chips_left,
			_last_words(_log_tail(), 200)],
		fpressed and _words.size() == words_f + 1 and _ap() == ap_f and cost_f == 0
			and str(set_aside.get("stuck", "")) == "" and table_up
			and str(closed.get("ended", "")) == "fell_back"
			and banner_f == (lead_shown + " falls back").to_upper() and chips_left == 0,
		{"day": closed})
	await _shot("after_fall_back", "the day closed: the lead has fallen back")
	# End Turn with NO day open: the gate (if any) says nothing of a day
	await _close_the_table()
	await _clear_boot_overlays()
	var modals3 := await _close_modals()
	var log2 := _log_len()
	var btn3 = _main.get("end_turn_button")
	var pend_before: int = (_main.get("pending_battle_days") as Array).size() if _main.get("pending_battle_days") is Array else -1
	if btn3 != null and btn3.visible and not btn3.disabled:
		btn3.emit_signal("pressed")
		await _frames(10)
		await _settle(30000)
		await _frames(10)
	var said3 := _log_since(log2)
	var went: bool = bool(dlg.visible)
	_rec("no_day_gate", "pressed End Turn with no day open",
		"pending days held=%d; the enemy phase's dialog came up=%s (no gate); the gate's words: %s; spoke of a day=%s" % [
			pend_before, str(went), _last_words(said3, 240),
			str(said3.find("Take the field") >= 0 or said3.find("still hangs") >= 0)],
		pend_before == 0 and said3.find("Take the field") < 0 and said3.find("still hangs") < 0
			and str(modals3.get("stuck", "")) == "")
	_finish()


func _log_meta_last(part: String) -> String:
	"""The LAST link in the log whose label holds `part`."""
	var found := ""
	for m in _metas_in_text(_log_messages_since(0)):
		if str((m as Dictionary).get("label", "")).find(part) >= 0:
			found = str((m as Dictionary).get("meta", ""))
	return found


func _end_turn_to_dialog(max_presses: int) -> Dictionary:
	"""End Turn pressed as a player presses it, through every gate that asks again, until the
	enemy phase's dialog is up (or the turn has gone with no dialog)."""
	var turn0 := _turn()
	var btn = _main.get("end_turn_button")
	var dlg = _main.get("enemy_phase_dialog")
	var presses := 0
	for _i in range(max_presses):
		if btn == null or not btn.visible or btn.disabled:
			break
		btn.emit_signal("pressed")
		presses += 1
		await _frames(8)
		await _settle(90000)
		await _frames(10)
		if dlg != null and bool(dlg.visible):
			break
		if _turn() > turn0:
			break
	var start := Time.get_ticks_msec()
	while dlg != null and not bool(dlg.visible) and _turn() == turn0 and Time.get_ticks_msec() - start < 20000:
		await process_frame
	return {"presses": presses, "turn0": turn0, "dialog": dlg != null and bool(dlg.visible)}


func _leave_the_phase() -> Dictionary:
	"""The enemy phase's tail, left as a player leaves it: the dialog's Continue, every table
	closed by its own Close, every modal by its own button, until the line is the player's again."""
	var dlg = _main.get("enemy_phase_dialog")
	var did: Array = []
	for _i in range(10):
		var moved := false
		if dlg != null and bool(dlg.visible):
			var cont = dlg.get("continue_button")
			if cont != null and cont.visible and not cont.disabled:
				cont.emit_signal("pressed")
				did.append("Continue")
				moved = true
				await _frames(8)
				await _settle(60000)
		if _table_up():
			await _close_the_table()
			did.append("table closed")
			moved = true
		var mods := await _close_modals()
		if not (mods.get("closed", []) as Array).is_empty():
			did.append_array(mods.get("closed", []))
			moved = true
		await _clear_boot_overlays()
		if not moved:
			break
		await _frames(10)
	return {"did": did, "editable": bool(_main.get("command_input").editable)}


func _review_r11() -> void:
	"""R11 — after a word that draws HIS clash, `_day_latest[enemy]` is the stale `follows` snapshot
	(no chips): read it directly; then close the table and press the log's last 'View the field'
	link — a day that awaits OUR word must show its chips, a primary button that is not 'His answer',
	and stay up."""
	var latest = _main.get("_day_latest")
	var blk = (latest as Dictionary).get(FOE, null) if latest is Dictionary else null
	var l_chips := -1
	var l_follows := false
	var l_awaits := ""
	if blk is Dictionary:
		l_chips = (blk.get("chips", []) as Array).size() if blk.get("chips", null) is Array else 0
		l_follows = bool(blk.get("follows", false))
		l_awaits = str(blk.get("awaits", ""))
	var now_day := _day()
	var table_chips_now := (now_day.get("chips", []) as Array).size() if now_day.get("chips", null) is Array else 0
	var closed := await _close_the_table()
	var mods := await _close_modals()
	var link := _log_meta_last("View the field")
	if link == "" or not closed:
		_rec("r11_view_the_field", "closed the table, looked for the log's 'View the field' link",
			"COULD NOT REACH: link='%s', table closed=%s; _day_latest chips=%d follows=%s awaits='%s'" % [
				link, str(closed), l_chips, str(l_follows), l_awaits],
			false, {"holds": false, "reached": false, "latest_chips": l_chips, "latest_follows": l_follows})
		return
	_log().emit_signal("meta_clicked", link)
	await _frames(20)
	var up_now := _table_up()
	var view := _day()
	var v_chips := (view.get("chips", []) as Array).size() if view.get("chips", null) is Array else 0
	var btn_text := ""
	if _dio() != null and _dio().get("_btn_close") != null:
		btn_text = str(_dio().get("_btn_close").text)
	await _shot("r11_view_the_field", "the table opened from the log's View the field")
	await _secs(3.5)
	var still_up := _table_up()
	await _shot("r11_after_3_5s", "the same table 3.5 s later")
	var holds: bool = v_chips > 0 and btn_text.find("His answer") < 0 and still_up
	_rec("r11_view_the_field", "read _day_latest, closed the table, pressed the log's last 'View the field'",
		"_day_latest[%s]: chips=%d follows=%s awaits='%s' (the table before closing had %d chips); the re-viewed table up=%s: day awaits '%s', chips on it=%d, primary button '%s', still up after 3.5 s=%s  => %s" % [
			FOE, l_chips, str(l_follows), l_awaits, table_chips_now, str(up_now), str(view.get("awaits", "")),
			v_chips, btn_text, str(still_up), "HOLDS" if holds else "REPRODUCED (the stale snapshot)"],
		holds, {"holds": holds, "reached": true, "latest_chips": l_chips, "latest_follows": l_follows,
			"view_chips": v_chips, "view_button": btn_text, "still_up_after_3_5s": still_up})


func _review_r12() -> void:
	"""R12 — `_day_latest` is never pruned: with the day ended on the server unseen (night at End
	Turn), the old log line's ORDER chip must be dim on the new turn. Press End Turn through the
	gate with the day open, let the phase finish, then read `_day_chip_live` for the old chip,
	the HUD's actions, press it, and record what was sent and spent."""
	if _press_meta == "":
		_rec("r12_old_chip", "no log chip was kept from the board", "COULD NOT REACH: no chip meta", false,
			{"holds": false, "reached": false})
		return
	var cmd := _press_meta.trim_prefix("day:")
	await _close_the_table()
	await _close_modals()
	var live_before := bool(_main.call("_day_chip_live", cmd))
	if not live_before:
		_rec("r12_old_chip", "the old chip was not lit when the turn was ended",
			"COULD NOT REACH: _day_chip_live('%s') is false before End Turn (the purse is spent: the chip is dim)" % cmd,
			true, {"holds": true, "reached": false})
		return
	var turn0 := _turn()
	var gate := await _end_turn_to_dialog(4)
	var tail := await _leave_the_phase()
	await _frames(20)
	var turn1 := _turn()
	# what the server holds now
	_days_probe = []
	var api = _api()
	var got := {"done": false}
	if api != null:
		api.get_battle_day(func(resp):
			_days_probe = resp.get("days", []) if resp is Dictionary and resp.get("days", null) is Array else []
			got["done"] = true)
		await _settle(20000)
	var server_days := _days_probe.size()
	var live := bool(_main.call("_day_chip_live", cmd))
	var ap_b := _ap()
	var log0 := _log_len()
	var words0 := _words.size()
	var latest = _main.get("_day_latest")
	var kept: bool = latest is Dictionary and (latest as Dictionary).has(FOE)
	await _shot("r12_new_turn", "the new turn, the old day's chip in the log")
	var sent := false
	if turn1 > turn0:
		_log().emit_signal("meta_clicked", _press_meta)
		await _frames(8)
		await _settle(60000)
		await _frames(12)
		await _commit_if_asked("r12")
		await _answer_objection("r12")
		await _frames(12)
	var said := _log_since(log0)
	sent = said.find("►") >= 0
	var ap_a := _ap()
	var table_after := _table_up()
	await _shot("r12_after_the_press", "after pressing the old chip on the new turn")
	if table_after:
		await _close_the_table()
	var spent: bool = ap_a < ap_b
	var holds: bool = (turn1 > turn0) and not live
	_rec("r12_old_chip", "End Turn through the gate with the day open, the phase left, then the old log chip pressed on the new turn",
		"turn %d -> %d (%d End Turn press(es), the phase's dialog came up=%s; tail: %s); server days open now=%d; _day_latest still holds %s=%s; chip '%s' live before=%s, live on the new turn=%s; HUD actions before the press %d, after %d (spent=%s); sent a typed order=%s; the log since: %s  => %s" % [
			turn0, turn1, int(gate.get("presses", 0)), str(gate.get("dialog", false)), str(tail.get("did", [])),
			server_days, FOE, str(kept), cmd, str(live_before), str(live), ap_b, ap_a, str(spent), str(sent),
			_last_words(said, 260), "HOLDS" if holds else ("REPRODUCED (action spent)" if (live and spent) else "REPRODUCED (chip live)" if live else "turn did not advance")],
		holds, {"holds": holds, "reached": turn1 > turn0, "live_on_new_turn": live, "live_before": live_before,
			"actions_before": ap_b, "actions_after": ap_a, "spent": spent, "sent": sent, "server_days": server_days})


func _walk_r12() -> void:
	"""R12 on the typed board's first half: the day is told in the log with its order chip LIT (the
	purse holds a point), then the turn is ended with the day open and the old chip is read and
	pressed on the new turn."""
	await _select(LEAD)
	var opened := await _open_attack_card()
	var oc = _card()
	if opened:
		var sendb = oc.get("send_button")
		if sendb != null and sendb.visible and not sendb.disabled:
			sendb.emit_signal("pressed")
	await _frames(6)
	await _settle(90000)
	await _frames(12)
	await _answer_objection("attack")
	await _commit_if_asked("attack")
	var up := await _wait_for_chips(90000)
	var day := _day()
	var dig_i := _chip_index(day, "dig_in", "")
	var dig_cmd := ""
	if dig_i >= 0:
		dig_cmd = str((day.get("chips", [])[dig_i] as Dictionary).get("command", ""))
	_rec("day_opens", "pressed the card's Send", "the table up=%s; the day: %s" % [str(up), _purses(day)],
		up and dig_cmd != "", {"day": day})
	if not up or dig_cmd == "":
		_finish()
		return
	var closed := await _close_the_table()
	var line = _main.get("command_input")
	var msg0 := _log_msgs()
	if closed and line != null and bool(line.editable):
		line.text = dig_cmd
		line.emit_signal("text_submitted", dig_cmd)
		await _frames(6)
		await _settle(60000)
		await _frames(12)
		await _commit_if_asked("typed")
		await _answer_objection("typed")
		await _frames(12)
	_press_meta = _log_meta_labelled("presses", msg0)
	_rec("typed_word", "typed the lead's dig-in with the table closed",
		"the log's order chip for the lead's press stands='%s'; the day's purse in the client's latest block: %s" % [
			_press_meta, str(((_main.get("_day_latest") as Dictionary).get(FOE, {}) as Dictionary).get("ours", "?"))],
		_press_meta != "")
	await _shot("typed_word", "the day told in the log, its chips written there")
	await _review_r12()
	_finish()


func _walk_r15() -> void:
	"""R15 — the word given from a table raised OVER the enemy phase's list: his clash's table
	must come up by itself (within ~4 s), the list still open. Defence board: End Turn, the
	list's 'View the field' on the day's row, then the lead's clash chip FROM THAT TABLE."""
	var gate := await _end_turn_to_dialog(3)
	var dlg = _main.get("enemy_phase_dialog")
	_rec("end_turn", "pressed End Turn (%d press(es))" % int(gate.get("presses", 0)),
		"the enemy phase's dialog up=%s" % str(gate.get("dialog", false)), bool(gate.get("dialog", false)))
	if not bool(gate.get("dialog", false)):
		_finish()
		return
	var link := ""
	var link_box = null
	for n in _all_nodes(dlg):
		if n is RichTextLabel and _meta_labelled(n, "View the field") != "":
			link = _meta_labelled(n, "View the field")
			link_box = n
			break
	var up := false
	if link != "":
		link_box.emit_signal("meta_clicked", link)
		up = await _wait_for_chips(90000)
	var day := _day()
	var strike_i := _chip_index(day, "press", "")
	_rec("r15_table", "pressed the list's 'View the field' on the day's row",
		"link stood=%s; the table over the list is up with its chips=%s; the day: %s; the lead's clash chip lit=%s" % [
			str(link != ""), str(up), _purses(day), str(strike_i >= 0)],
		link != "" and up, {"day": day})
	await _shot("r15_table_over_the_list", "the table raised over the enemy phase's list")
	if not up or strike_i < 0:
		_rec("r15_his_clash", "the lead's clash chip was not offered on this table",
			"COULD NOT REACH: no clash chip lit", true, {"holds": true, "reached": false})
		_finish()
		return
	var words0 := _words.size()
	var pressed := _press(strike_i)
	await _frames(6)
	await _settle(60000)
	await _frames(12)
	await _commit_if_asked("r15")
	await _answer_objection("r15")
	# What comes up after the word? The old table stands with the dawn's purses; the answer's tables (OUR
	# clash's, then HIS) are the new ones: a changed purse or a `follows` block says one was raised.
	var before := _purses(day)
	var t0 := Time.get_ticks_msec()
	var raised_ms := -1
	var first := day
	while Time.get_ticks_msec() - t0 < 45000:
		await process_frame
		var d = _dio()
		var now := _day()
		if d != null and bool(d.visible) and bool(d.get("_final")) \
				and (_purses(now) != before or bool(now.get("follows", false))):
			raised_ms = Time.get_ticks_msec() - t0
			first = now
			break
	var list_open_now: bool = bool(dlg.visible)
	await _shot("r15_after_the_word", "45 s after the word: what stands over the list")
	# the client's own state, read as it stands (what did and did not happen)
	var state := {
		"pending_diorama_data_held": _main.get("pending_diorama_data") != null,
		"day_followup_held": _main.get("_day_followup") != null,
		"diorama_standalone": _main.get("_diorama_standalone"),
		"battle_word_in_flight": _main.get("_battle_word_in_flight"),
		"chip_command_in_flight": _main.get("_chip_command_in_flight"),
		"day_word_sent": _main.get("_day_word_sent"),
		"day_table_held": _main.get("_day_table_held") != null,
		"reduce_motion": UiSettings.get_reduce_motion(),
		"table_final": bool(_dio().get("_final")) if _dio() != null else false,
		"table_close_text": str(_dio().get("_btn_close").text) if _dio() != null else "",
		"words_given": _words.duplicate(),
	}
	if raised_ms < 0:
		# nothing was raised while the list stood open (the server ran both clashes: read it back)
		var probe_before := _day()
		var cont = dlg.get("continue_button")
		var cont_pressed := false
		if cont != null and cont.visible and not cont.disabled:
			cont.emit_signal("pressed")
			cont_pressed = true
		var t1 := Time.get_ticks_msec()
		var after_ms := -1
		var after_day := {}
		var after_btn := ""
		while Time.get_ticks_msec() - t1 < 40000:
			await process_frame
			var d3 = _dio()
			var n3 := _day()
			if d3 != null and bool(d3.visible) and (_purses(n3) != before or bool(n3.get("follows", false))):
				after_ms = Time.get_ticks_msec() - t1
				after_day = n3
				after_btn = str(d3.get("_btn_close").text)
				break
		await _shot("r15_after_continue", "after the list's Continue: does the answer's table come up now?")
		# the old table still stands: close it as a player does and see whether the answer's tables come then
		var old_up_after := _table_up()
		var old_chips_lit := _chip_index(_day(), "press", "") >= 0
		var closed_old := false
		var after_close_ms := -1
		var after_close_day := {}
		if after_ms < 0 and old_up_after:
			closed_old = await _close_the_table()
			var t2 := Time.get_ticks_msec()
			while Time.get_ticks_msec() - t2 < 20000:
				await process_frame
				var d4 = _dio()
				var n4 := _day()
				if d4 != null and bool(d4.visible) and (_purses(n4) != before or bool(n4.get("follows", false))):
					after_close_ms = Time.get_ticks_msec() - t2
					after_close_day = n4
					break
			await _shot("r15_after_closing_the_old_table", "the old table closed: does the answer's table come now?")
		_rec("r15_his_clash", "pressed the lead's clash chip from the table over the list",
			"the word was given (%s) and the muster answered; for 45 s NO table of the answer was raised over the open list (the table still read '%s', list open=%s); after the list's Continue (pressed=%s) the answer's table %s%s  => REPRODUCED (the answer's tables wait for the list's Continue)" % [
				str(pressed), before, str(list_open_now), str(cont_pressed),
				("came up after %d ms: %s, primary button '%s'" % [after_ms, _purses(after_day), after_btn]) if after_ms >= 0 else "did not come up within 40 s",
				("; the OLD table stood on (up=%s, its 'strikes back' chip still lit=%s); closed by its own Close=%s, then the answer's table %s" % [
					str(old_up_after), str(old_chips_lit), str(closed_old),
					("came up after %d ms: %s" % [after_close_ms, _purses(after_close_day)]) if after_close_ms >= 0 else "did not come up within 20 s"]) if after_ms < 0 else ""],
			false, {"holds": false, "reached": true, "answer_raised_over_list_ms": -1, "continue_pressed": cont_pressed,
				"after_continue_ms": after_ms, "after_continue_button": after_btn, "purses_before": before,
				"old_table_stood_after_continue": old_up_after, "old_chip_still_lit": old_chips_lit, "state_at_45s": state,
				"after_closing_old_follows": bool(after_close_day.get("follows", false)),
				"after_closing_old_purses": _purses(after_close_day),
				"after_closing_old_ms": after_close_ms})
		_finish()
		return
	var follows := bool(first.get("follows", false))
	var btn_text := str(_dio().get("_btn_close").text) if _dio() != null else ""
	var rested_ms := Time.get_ticks_msec()
	await _shot("r15_our_clash", "our clash's table (the list still open behind it)")
	if not follows:
		_rec("r15_his_clash", "pressed the lead's clash chip from the table over the list",
			"COULD NOT REACH the follow-up: our clash's table was raised over the list after %d ms and does not carry `follows` (he did not strike back): %s, primary button '%s'" % [
				raised_ms, _purses(first), btn_text],
			true, {"holds": true, "reached": false, "answer_raised_over_list_ms": raised_ms})
		_finish()
		return
	# his clash must come by itself: our table rests (measured FROM THE REST), goes on 2.5 s later, and
	# HIS table is raised on the same road. The closing and the raising can be the same frame, so the
	# table may never read "down": watch for a table that is no longer ours (`follows` gone) or hidden.
	var rest_t := Time.get_ticks_msec()
	var went_ms := -1
	var his_ms := -1
	while Time.get_ticks_msec() - rest_t < 15000:
		await process_frame
		var d2 = _dio()
		var gone: bool = d2 == null or not bool(d2.visible)
		var his_now: bool = d2 != null and bool(d2.visible) and not bool(_day().get("follows", false)) \
			and str(d2.get("_btn_close").text).find("His answer") < 0
		if went_ms < 0 and (gone or his_now):
			went_ms = Time.get_ticks_msec() - rest_t
		if his_now:
			his_ms = Time.get_ticks_msec() - rest_t
			break
	var his_day := _day()
	var his_chips_up := false
	if his_ms >= 0:
		his_chips_up = await _wait_for_chips(60000)
		his_day = _day()
	await _shot("r15_his_table", "his clash's table over the list, rested with the day's new purses and chips")
	var list_open: bool = bool(dlg.visible)
	var holds: bool = went_ms >= 0 and his_ms >= 0 and his_ms <= 6000 and list_open and his_chips_up \
		and (his_day.get("chips", []) as Array).size() > 0
	_rec("r15_his_clash", "pressed the lead's clash chip from the table over the list, rode 'His answer ▸'",
		"pressed=%s; our table raised after %d ms: follows=true, primary button '%s'; measured from its rest it went on by itself after %s; his clash's table came up %s after the rest; it rested with chips=%s: %s; the list still open=%s  => %s" % [
			str(pressed), raised_ms, btn_text, ("%d ms" % went_ms) if went_ms >= 0 else "NEVER (15 s)",
			("%d ms" % his_ms) if his_ms >= 0 else "NEVER (15 s)", str(his_chips_up), _purses(his_day),
			str(list_open), "HOLDS" if holds else "REPRODUCED (his clash waits for the list's Continue)"],
		holds, {"holds": holds, "reached": true, "our_button": btn_text, "went_on_ms": went_ms,
			"his_table_ms": his_ms, "list_open": list_open, "answer_raised_over_list_ms": raised_ms,
			"his_purses": _purses(his_day)})
	# the list's own Continue still works afterwards (the table closed first, as a player does)
	await _close_the_table()
	var cont2 = dlg.get("continue_button")
	var pressed2 := false
	if cont2 != null and cont2.visible and not cont2.disabled:
		cont2.emit_signal("pressed")
		pressed2 = true
		await _frames(10)
		await _settle(30000)
	await _frames(10)
	_rec("r15_continue", "closed the table and pressed the list's Continue",
		"Continue pressed=%s; the list is gone=%s" % [str(pressed2), str(not bool(dlg.visible))],
		pressed2 and not bool(dlg.visible))
	_finish()


func _walk_typed() -> void:
	"""A word TYPED into the real command line with the table closed (the lead's dig-in as
	text, submitted as a player submits it): the log tells the day and writes its chips; one
	chip is then pressed IN THE LOG."""
	await _select(LEAD)
	var opened := await _open_attack_card()
	var oc = _card()
	if opened:
		var sendb = oc.get("send_button")
		if sendb != null and sendb.visible and not sendb.disabled:
			sendb.emit_signal("pressed")
	await _frames(6)
	await _settle(90000)
	await _frames(12)
	await _answer_objection("attack")
	await _commit_if_asked("attack")
	var up := await _wait_for_chips(90000)
	var day := _day()
	var dig_i := _chip_index(day, "dig_in", "")
	var dig_cmd := ""
	if dig_i >= 0:
		dig_cmd = str((day.get("chips", [])[dig_i] as Dictionary).get("command", ""))
	_rec("day_opens", "pressed the card's Send (%s, attack %s)" % [LEAD, FOE],
		"the table up=%s; the day: %s; the dig-in order reads '%s'" % [str(up), _purses(day), dig_cmd],
		up and bool(day.get("open", false)) and dig_cmd != "", {"day": day})
	if not up or dig_cmd == "":
		_finish()
		return
	var closed := await _close_the_table()
	var line = _main.get("command_input")
	var editable: bool = line != null and bool(line.editable)
	var log0 := _log_len()
	var msg0 := _log_msgs()
	var ap0 := _ap()
	if closed and editable:
		line.text = dig_cmd
		line.emit_signal("text_submitted", dig_cmd)       # what Enter does on the line
		await _frames(6)
		await _settle(60000)
		await _frames(12)
		await _commit_if_asked("typed")
		await _answer_objection("typed")
		await _frames(12)
	var said := _log_since(log0)
	var metas: Array = _metas_in_text(_log_messages_since(msg0))
	var at_day := said.find("The day at")
	# the order's own reply (any line between the echoed order and the day's block) stands ABOVE
	# "The day at ..." — the reply first, the day's block after it
	var reply_above := false
	if at_day > 0:
		for ln in said.substr(0, at_day).split("\n"):
			var t := str(ln).strip_edges()
			if t != "" and not t.begins_with("►"):
				reply_above = true
	var day_chips: Array = []
	for m in metas:
		if str((m as Dictionary).get("meta", "")).begins_with("day:"):
			day_chips.append(str((m as Dictionary).get("label", "")))
	_rec("typed_word", "closed the table (its Close button) and typed '%s' into the command line" % dig_cmd,
		"table closed=%s, line editable=%s; the log told the day=%s; the order's reply stands above 'The day at'=%s; chips written into the log: %s; actions %d -> %d; the log: %s" % [
			str(closed), str(editable), str(at_day >= 0), str(reply_above), str(day_chips), ap0, _ap(),
			_last_words(said, 300)],
		closed and editable and at_day >= 0 and reply_above and not day_chips.is_empty() and _ap() == ap0,
		{"log": said.substr(maxi(0, said.length() - 600))})
	await _shot("typed_word", "the day told in the log, its chips written there")
	# one chip pressed IN THE LOG: the lead's press (a typed order, a clash, the table comes up)
	var words0 := _words.size()
	_press_meta = _log_meta_labelled("presses", msg0)
	var pressed := _press_log_chip("presses", msg0)
	await _frames(6)
	await _settle(60000)
	await _frames(12)
	await _commit_if_asked("log_chip")
	await _answer_objection("log_chip")
	var shown := await _wait_for_chips(120000)
	var after := _day()
	_rec("log_chip", "pressed the log's 'presses' chip",
		"pressed=%s; the client then shows: the table up=%s, its chips=%s; the day: %s; actions %d -> %d (cost %d)" % [
			str(pressed), str(_table_up()), str(shown), _purses(after), ap0, _ap(), _cost_of_last()],
		pressed and _table_up() and _ap() == ap0 and _cost_of_last() == 0, {"day": after})
	await _shot("log_chip", "what the client shows after a chip pressed in the log")
	# ── the review's reproductions (appended; nothing above changes) ──
	await _review_r11()
	_finish()


func _walk() -> void:
	for pair in [["BA3_LEAD", "LEAD"], ["BA3_FOE", "FOE"], ["BA3_FIELD", "FIELD"], ["BA3_PLAN", "PLAN"]]:
		var given := OS.get_environment(pair[0])
		if given != "":
			set(pair[1], given)
	var dir_env := OS.get_environment("BA3_WALK_OUT")
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

	# 1 - boot
	_rec("boot", "booted the real main.tscn against the sandboxed backend",
		"booted=%s turn=%d actions=%d" % [str(_out["booted"]), _turn(), _ap()], bool(_out["booted"]))

	if PLAN == "dawn":
		await _walk_dawn()
		return
	if PLAN == "typed":
		await _walk_typed()
		return
	if PLAN == "r15":
		await _walk_r15()
		return
	if PLAN == "r12":
		await _walk_r12()
		return

	# 2 - Massena's attack card on the Archduke Charles, Send
	await _select(LEAD)
	var opened := await _open_attack_card()
	var oc = _card()
	var ap_open := _ap()
	if opened:
		var sendb = oc.get("send_button")
		if sendb != null and sendb.visible and not sendb.disabled:
			sendb.emit_signal("pressed")
	await _frames(6)
	await _settle(90000)
	await _frames(12)
	var objected := await _answer_objection("attack")
	await _commit_if_asked("attack")
	var up := await _wait_for_chips(90000)
	var day := _day()
	_rec("day_opens", "pressed the card's Send (%s, attack %s)" % [LEAD, FOE],
		"actions %d -> %d; objected=%s; the table up=%s; the panel at rest=%s; the day: %s; chips: %s" % [
			ap_open, _ap(), str(objected), str(_table_up()), str(up), _purses(day), str(_chips_of(day))],
		up and bool(day.get("open", false)) and str(day.get("awaits", "")) == "ours"
			and _chip_index(day, "press", "") >= 0,
		{"day": day})
	await _shot("day_panel", "the day's panel at rest: both purses, the last told, the chips")
	if not up:
		_finish()
		return

	# 2b - what the panel says at rest: the banner, the pips, the Guard on row C
	var dio = _dio()
	var acts = dio.get("_acts")
	var banner_now: String = str(dio.get("_banner").text)
	var row_c: String = ""
	var c_rows := 0
	if acts != null and acts.get("_day_chips") != null and is_instance_valid(acts.get("_day_chips")):
		row_c = _plain((acts.get("_day_chips") as RichTextLabel).get_parsed_text())
		c_rows = (acts.get("_day_chips") as RichTextLabel).get_line_count()
	var guard_i := _chip_index(day, "guard", "")
	var chips_now: Array = day.get("chips", [])
	_rec("panel_at_rest", "read the panel at rest",
		"banner '%s' (the day's own: '%s'); purses %s of %s / %s of %s; row C (%d row): %s; the Guard is chip %d" % [
			banner_now, str(day.get("banner", "")), str(day.get("ours", "?")), str(day.get("ours_of", "?")),
			str(day.get("theirs", "?")), str(day.get("theirs_of", "?")), c_rows, row_c, guard_i],
		banner_now == str(day.get("banner", "")).to_upper() and int(day.get("ours_of", 0)) >= int(day.get("ours", 0))
			and (guard_i < 0 or (guard_i == 1 and c_rows == 1 and row_c.find("Guard") >= 0)),
		{"day": day})
	if PLAN == "guard":
		# 3g - the Guard: two points, no action (the real Ulm opening). The press may decide the day.
		var gap := _ap()
		var gi := guard_i
		var gtext := "no Guard chip on this day"
		var gpressed := false
		var gcost := -1
		if gi >= 0:
			var ours_g := int(day.get("ours", -1))
			gpressed = _press(gi)
			await _frames(6)
			await _settle(60000)
			await _frames(12)
			await _commit_if_asked("guard")
			await _answer_objection("guard")
			await _wait_final(90000)          # the Guard's clash plays its acts; the frame is the field at rest
			var last_g = _main.get("_last_command_response")
			if last_g is Dictionary and (last_g as Dictionary).get("action_info", null) is Dictionary:
				gcost = int((last_g as Dictionary)["action_info"].get("cost", -1))
			var after_g := _day()
			gtext = "pressed=%s; words %s; actions %d -> %d (cost %d); purses %d -> %s; banner '%s'; ended '%s'; the log: %s" % [
				str(gpressed), str(_words), gap, _ap(), gcost, ours_g, _purses(after_g),
				str(_dio().get("_banner").text), str(after_g.get("ended", "")), _last_words(_log_tail())]
		_rec("guard", "pressed 'The Guard' (two points) on row C", gtext,
			gpressed and _words.size() == 1 and _ap() == gap and gcost == 0, {"words": _words.duplicate()})
		await _shot("after_the_guard", "the Guard has gone in: whatever the server answered")
		_finish()
		return

	# 2c - the PROVINCE PANEL's chip: close the table as a player does, open the field's
	# panel from the map, read the day's chips there (above the ATTACK rows), press
	# "<lead> digs in" (a typed order, 1 point, 0 actions): main.gd answers with the
	# table again (`_stash_battle_day` -> the settled frame with the new block)
	var dig_p := _chip_index(day, "dig_in", "")
	var dig_cmd := ""
	if dig_p >= 0:
		dig_cmd = str((day.get("chips", [])[dig_p] as Dictionary).get("command", ""))
	var ours_p := int(day.get("ours", -1))
	var ap_p := _ap()
	var table_closed := await _close_the_table()
	var panel_up := await _open_province_panel(FIELD)
	var ptext := _panel_text()
	var meta_p := "do:@day:" + dig_cmd
	var chip_there: bool = dig_cmd != "" and _panel_source().find("[url=" + meta_p + "]") >= 0
	var above: bool = ptext.find("THE DAY AT") >= 0 and (ptext.find("ATTACK") < 0 or ptext.find("THE DAY AT") < ptext.find("ATTACK"))
	_rec("panel_day", "closed the table (its Close button), clicked %s on the map" % FIELD,
		"table closed=%s; the panel up=%s; the day's block on it=%s (above the ATTACK rows=%s); the dig-in chip stands=%s; panel: %s" % [
			str(table_closed), str(panel_up), str(ptext.find("THE DAY AT") >= 0), str(above), str(chip_there),
			_last_words(ptext, 240)],
		table_closed and panel_up and ptext.find("THE DAY AT") >= 0 and above and chip_there)
	await _shot("panel_day", "the province panel: the day's chips above the ATTACK rows")
	if chip_there:
		var area = _panel().get("content_area")
		var words_p := _words.size()
		area.emit_signal("meta_clicked", meta_p)       # a click on the chip delivers this meta
		await _frames(6)
		await _settle(60000)
		await _frames(12)
		await _commit_if_asked("panel_dig")
		await _answer_objection("panel_dig")
		var back_p := await _wait_for_chips(60000)
		var after_p := _day()
		var cost_p := _cost_of_last()
		_rec("panel_press", "pressed the panel's chip '%s' (a typed order)" % dig_cmd,
			"actions %d -> %d (action_info.cost=%d); purses %d -> %s; the table is back=%s with the new block, chips back=%s; the panel open=%s, its day line: %s; word_given untouched=%s" % [
				ap_p, _ap(), cost_p, ours_p, _purses(after_p), str(_table_up()), str(back_p),
				str(_panel() != null and bool(_panel().visible)),
				_last_words(_panel_text(), 120), str(_words.size() == words_p)],
			_ap() == ap_p and cost_p == 0 and _table_up() and int(after_p.get("ours", -1)) == ours_p - 1
				and str(after_p.get("awaits", "")) == "ours",
			{"day": after_p})
		await _shot("panel_press", "the table is back with the new block")
		# BA3-X19: the province panel's title says "1 POINT" (not "1 POINTS") with one point left
		await _frames(20)
		await _settle(15000)
		var pt := _panel_text()
		var at_t := pt.find("THE DAY AT")
		var title := ""
		if at_t >= 0:
			title = pt.substr(at_t, 40).strip_edges()
		var one_point: bool = title.find("1 POINT") >= 0 and title.find("1 POINTS") < 0
		_rec("panel_points", "read the province panel's day title with one point left",
			("the panel's title: '%s' (one point left; says '1 POINT', not '1 POINTS'=%s)" % [title, str(one_point)]) if at_t >= 0
				else "the panel carries no day block behind the table after the first point (title not on screen): not read",
			(at_t < 0) or one_point, {"reached": at_t >= 0, "title": title})
		if not back_p:
			_finish()
			return
		day = after_p

	# 3 - the lead's press: a table chip, a typed order, the table still up
	var ours_before := int(day.get("ours", -1))
	var theirs_before := int(day.get("theirs", -1))
	var ap_before := _ap()
	var idx := _chip_index(day, "press", "")
	var pressed := _press(idx)
	await _frames(6)
	await _settle(60000)
	await _frames(12)
	var asked := await _commit_if_asked("press")
	var objected2 := await _answer_objection("press")
	await _frames(24)
	# our clash's table rests with `follows` ("<his name> strikes back."): its primary
	# button reads "His answer ▸" and the table goes on by itself; the live chips ride
	# HIS table. Read the button, time the advance, then read his table's chips.
	var follow_seen := false
	var follow_btn := ""
	var follow_ms := -1
	var wait_start := Time.get_ticks_msec()
	while Time.get_ticks_msec() - wait_start < 90000:
		await process_frame
		var dio_f = _dio()
		if dio_f == null:
			continue
		if bool(dio_f.visible) and bool(dio_f.get("_final")) and bool(_day().get("follows", false)):
			follow_seen = true
			follow_btn = str(dio_f.get("_btn_close").text)
			var t_follow := Time.get_ticks_msec()
			while Time.get_ticks_msec() - t_follow < 30000:
				await process_frame
				if not bool(_day().get("follows", false)) and _chips_up():
					follow_ms = Time.get_ticks_msec() - t_follow
					break
			break
		if _chips_up():
			break
	var back := _chips_up()
	if not back:
		back = await _wait_for_chips(30000)
	day = _day()
	var cost := -1
	var last = _main.get("_last_command_response")
	if last is Dictionary and (last as Dictionary).get("action_info", null) is Dictionary:
		cost = int((last as Dictionary)["action_info"].get("cost", -1))
	_rec("press", "pressed the table chip '%s' (index %d)" % [LEAD + " presses", idx],
		"pressed=%s; words given=%s; actions %d -> %d (action_info.cost=%d); muster asked=%s; objected=%s; "
		% [str(pressed), str(_words), ap_before, _ap(), cost, str(asked), str(objected2)]
			+ "the table up=%s, the panel back=%s; purses %d/%d -> %s; the log: %s" % [
				str(_table_up()), str(back), ours_before, theirs_before, _purses(day), _last_words(_log_tail())],
		pressed and _words.size() == 1 and _ap() == ap_before and cost == 0 and _table_up()
			and int(day.get("ours", -1)) == ours_before - 1,
		{"day": day, "words": _words.duplicate(), "log_tail": _log_tail()})
	await _shot("after_the_press", "his clash on the same table; the purses one point lower")
	_rec("follows", "read our clash's table when his answer follows it",
		("his clash followed: the primary button read '%s'; the table went on by itself after %d ms; his table's chips back=%s"
			% [follow_btn, follow_ms, str(back)]) if follow_seen
			else "his answer did not follow our clash on this seed (no clash of his): nothing to read",
		(not follow_seen) or (follow_btn.find("His answer") >= 0 and follow_ms >= 1800 and back))

	# 4 - the word chip: "Leave it to Massena" (POST /battle_day/word)
	var open_now := bool(day.get("open", false)) and str(day.get("awaits", "")) == "ours"
	var wi := _chip_index(day, "stand", "leave_it")
	if wi < 0:
		wi = _chip_index(day, "stand", "stand")
	if not open_now or wi < 0:
		_rec("word", "the day offered no word chip after the press", _purses(day) + "; chips " + str(_chips_of(day)), false)
		_finish()
		return
	var words_before := _words.size()
	ours_before = int(day.get("ours", -1))
	ap_before = _ap()
	var word_chip: String = str((day.get("chips", [])[wi] as Dictionary).get("label", "?"))
	var sent := _press(wi)
	await _frames(6)
	await _settle(90000)
	await _frames(24)
	await _secs(2.5)
	var after := _day()
	_rec("word", "pressed the word chip '%s' (index %d)" % [word_chip, wi],
		"pressed=%s; the word given=%s; actions %d -> %d; the table up=%s; the day now: %s; ended='%s'; told: %s" % [
			str(sent), str(_words.slice(words_before)), ap_before, _ap(), str(_table_up()), _purses(after),
			str(after.get("ended", "")), str(after.get("told", []).slice(-3) if after.get("told", null) is Array else [])],
		sent and _words.size() == words_before + 1 and _words[_words.size() - 1].begins_with("@word:")
			and _ap() == ap_before,
		{"day": after, "words": _words.duplicate()})
	await _shot("after_the_word", "the day after the lead was left to it")
	await _secs(6.0)
	await _shot("the_field_at_rest", "the field at rest")
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
