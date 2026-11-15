extends SceneTree
# Row BA, BA-2 - the plan's loop, pressed in the real client (November 15, 2026)
# - modeled on tools/ui6_mode_c_walk.gd.
#
#   $env:SOVEREIGN_PORT   = "8006"        # a sandboxed backend listening there (never 8005)
#   $env:BA2_WALK_OUT     = "<abs dir>"   # frames + walk.json land here
#   <godot> --audio-driver Dummy --windowed --resolution 1920x1080 \
#           --path godot-client/project-sovereign --script <abs>/tools/ba2_mode_c_walk.gd
#
# The REAL main.tscn against a live sandboxed backend, on the campaign's opening
# board. Steps: boot; the province panel at Swabia, its "Bring up" fold and its
# "+N more" (who is offered to whom); a chip pressed IN THE PANEL (Soult ordered
# in support of Ney); Lannes's attack card and a chip pressed ON THE CARD (Murat,
# who stands beside him) — the card shuts, the order goes, Lannes is selected
# again and his next card counts Murat in the muster; then Ney's card (no chip
# left for Soult) and the attack sent; Act I's plan on the table. No step may
# end on a marshal's question ("<NAME> REPORTS ... Your orders?"): an order
# that asks is not an order that brings. Each step records {step, did, saw, ok}
# in walk.json["results"] (and a frame row in walk.json["steps"]), tolerates
# failure, and the walk never aborts.

const WALL_LIMIT_MS := 600000
const OUT_DEFAULT := "res://../../docs/audits/ba2_mode_c_2026_11_15"
const FIELD := "Swabia"
const FOE := "Mack"
const LEAD := "Ney"              # the lead the battle is fought under
const PANEL_CHIP := "Soult, support Ney"
const CARD_LEAD := "Lannes"      # the lead whose card's chip is pressed
const CARD_CHIP := "Murat, support Lannes"
const NBSP := " "

var _main = null
var _out: Dictionary = {"steps": [], "errors": [], "results": []}
var _dir := ""
var _t0 := 0
var _done := false
var _n := 0


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


func _ap() -> int:
	return int(_main.get("actions_remaining")) if _main != null else -1


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
	"""A chip keeps its words on one line with no-break spaces: read as plain ones."""
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
	var file := "BA2_WALK_%02d_%s_2026_11_15.jpg" % [_n, name]
	var err := img.save_jpg(_dir.path_join(file), 0.88)
	_out["steps"].append({"step": name, "note": note, "frame": file, "saved": err == OK,
		"turn": _turn(), "ms": Time.get_ticks_msec() - _t0})


func _rec(step: String, did: String, saw: String, ok: bool, extra: Dictionary = {}) -> void:
	var row := {"step": step, "did": did, "saw": saw, "ok": ok}
	for k in extra:
		row[k] = extra[k]
	_out["results"].append(row)
	if not ok:
		_out["errors"].append({"turn": _turn(), "what": step + ": " + saw})


func _log_tail(chars: int = 700) -> String:
	var display = _main.get("output_display")
	var text: String = display.get_parsed_text() if display != null else ""
	return text.substr(maxi(0, text.length() - chars))


func _last_words(text: String, chars: int = 260) -> String:
	var t := text.strip_edges()
	return t.substr(maxi(0, t.length() - chars))


func _panel() -> Node:
	return _main.get("region_panel")


func _panel_text() -> String:
	var panel = _panel()
	if panel == null or not panel.visible:
		return ""
	var area = panel.get("content_area")
	return _plain(area.get_parsed_text()) if area != null else ""


func _panel_to_its_attack_rows() -> void:
	"""The ATTACK rows stand at the foot of a long province's panel: the scroll
	run to its end, as a wheel does, so the frame shows them."""
	var panel = _panel()
	if panel == null or not panel.visible:
		return
	var area = panel.get("content_area")
	var scroll = area.get_parent() if area != null else null
	if scroll is ScrollContainer:
		await _frames(4)
		(scroll as ScrollContainer).scroll_vertical = int((scroll as ScrollContainer).get_v_scroll_bar().max_value)
		await _frames(6)


func _card() -> Node:
	return _main.get("order_card")


func _card_terms() -> String:
	var oc = _card()
	if oc == null or not oc.visible:
		return ""
	var terms = oc.get("terms_label")
	return _plain(terms.get_parsed_text()) if terms != null else ""


func _question() -> String:
	"""A marshal's question on screen (the interrupt popup: "<NAME> REPORTS"),
	its words - "" when none stands."""
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
	"""A marshal's objection to the order stands as a modal: answered Insist
	(the chip said 'he may object'). True when one stood."""
	var dlg = _main.get("objection_dialog")
	if dlg == null or not dlg.visible:
		return false
	var words := ""
	for n in _all_nodes(dlg):
		if n is RichTextLabel and n.is_visible_in_tree():
			words += n.get_parsed_text() + " "
		elif n is Label and n.is_visible_in_tree():
			words += str(n.text) + " "
	await _shot(step + "_objection", "the marshal objects, as the chip said he might")
	var insist = dlg.get("insist_button")
	if insist != null and insist.visible and not insist.disabled:
		insist.emit_signal("pressed")
	await _settle(60000)
	await _frames(12)
	_rec(step + "_objection", "the objection answered: Insist", words.strip_edges().substr(0, 260), true)
	return true


func _select(who: String) -> String:
	"""A corps selected as a click on his chip in the marshal row does it."""
	if str(_main.get("_order_marshal")) == who:
		return "already selected"
	var line = _main.get("command_input")
	if line != null:
		line.release_focus()
	_main.call("_on_marshal_chip_pressed", who)
	await _frames(8)
	await _settle(15000)
	await _frames(6)
	return "the marshal row's handler"


func _open_attack_card() -> bool:
	var map = _main.get("map_area")
	if map == null:
		return false
	map.emit_signal("order_context_requested", FIELD, FOE)   # the map's right click on Mack's piece
	var start := Time.get_ticks_msec()
	while Time.get_ticks_msec() - start < 20000:
		await process_frame
		var oc = _card()
		if oc != null and oc.visible and _api_idle() and str(oc.call("command")) != "":
			break
	await _frames(12)
	var card = _card()
	return card != null and card.visible


func _plan_beat() -> String:
	"""Act I's plan as the tableau was handed it (its own payload's script)."""
	var dio = _main.get("battle_diorama")
	if dio == null:
		return ""
	var data = dio.get("_data")
	if not (data is Dictionary):
		return ""
	var script = (data as Dictionary).get("script", {})
	if not (script is Dictionary):
		return ""
	for act in (script as Dictionary).get("acts", []):
		if not (act is Dictionary):
			continue
		for beat in (act as Dictionary).get("beats", []):
			if beat is Dictionary and str((beat as Dictionary).get("kind", "")) == "plan":
				return str((beat as Dictionary).get("text", ""))
	return ""


func _bring_lines_of(text: String) -> Array:
	var out: Array = []
	for raw in text.split("\n"):
		var ln := str(raw).strip_edges()
		if ln.find("to support ") >= 0 or ln.find("Bring up") >= 0:
			out.append(ln)
	return out


func _offered(text: String, corps: String) -> Array:
	"""The leads whose line 'to support <Lead>:' carries a chip for `corps`."""
	var leads: Array = []
	for ln in _bring_lines_of(text):
		var line := str(ln)
		var at := line.find("to support ")
		var colon := line.find(":", at)
		if at < 0 or colon < 0:
			continue
		if line.substr(colon).find(corps + " · ") >= 0:
			leads.append(line.substr(at + "to support ".length(), colon - at - "to support ".length()))
	return leads


func _walk() -> void:
	var dir_env := OS.get_environment("BA2_WALK_OUT")
	_dir = dir_env if dir_env != "" else ProjectSettings.globalize_path(OUT_DEFAULT)
	DirAccess.make_dir_recursive_absolute(_dir)
	root.mode = Window.MODE_WINDOWED
	root.position = Vector2i(5200, 20)
	root.size = Vector2i(1920, 1080)
	await _frames(4)
	var packed: PackedScene = load("res://scenes/main.tscn")
	_main = packed.instantiate()
	root.add_child(_main)
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

	# 2 - the province panel at Swabia: the plan behind one fold
	var map = _main.get("map_area")
	map.emit_signal("region_clicked", FIELD)   # the map's left click on the province
	await _frames(10)
	await _settle(20000)
	await _frames(12)
	var panel = _panel()
	var text := _panel_text()
	var shut_fold: bool = text.find("▸ Bring up — ") >= 0
	_rec("panel_open", "clicked %s on the map (region_clicked)" % FIELD,
		"panel visible=%s province=%s fold=%s" % [str(panel != null and panel.visible),
			str(panel.get("_region")) if panel != null else "",
			str(_bring_lines_of(text))],
		panel != null and panel.visible and shut_fold, {"panel_tail": _last_words(text, 900)})
	await _panel_to_its_attack_rows()
	await _shot("panel_fold_shut", "the province panel at Swabia: the ATTACK rows, the plan behind one fold")

	# 3 - the fold opened, and the "+N more" leads with it
	var area = panel.get("content_area") if panel != null else null
	if area != null:
		area.emit_signal("meta_clicked", "toggle:bring")
		await _frames(10)
		area.emit_signal("meta_clicked", "toggle:march_more")
		await _frames(12)
	text = _panel_text()
	var soult_for: Array = _offered(text, "Soult")
	var murat_for: Array = _offered(text, "Murat")
	var bernadotte_for: Array = _offered(text, "Bernadotte")
	var open_ok: bool = soult_for.has(LEAD) and murat_for == [CARD_LEAD] and bernadotte_for.is_empty()
	_rec("panel_fold_open", "pressed the fold (toggle:bring) and '+N more' (toggle:march_more)",
		"Soult offered to %s; Murat to %s; Bernadotte to %s" % [str(soult_for), str(murat_for),
			str(bernadotte_for)],
		open_ok, {"bring_lines": _bring_lines_of(text)})
	await _panel_to_its_attack_rows()
	await _shot("panel_fold_open", "the fold open: a line per lead, a chip per corps and its price")

	# 4 - the chip pressed in the panel
	var ap_before := _ap()
	var chip_there: bool = text.find("to support " + LEAD + ":") >= 0
	if area != null:
		area.emit_signal("meta_clicked", "do:" + PANEL_CHIP)
	await _frames(6)
	await _settle(60000)
	await _frames(12)
	var objected := await _answer_objection("panel_chip")
	var asked := _question()
	var ap_after := _ap()
	var tail := _log_tail()
	var taken: bool = chip_there and asked == "" and ap_after == ap_before - 1 \
		and tail.find("Soult moves to support " + LEAD) >= 0
	_rec("panel_chip", "pressed the panel's chip '%s'" % PANEL_CHIP,
		"the chip stood on %s's line=%s; actions %d -> %d; objected=%s; a question raised='%s'; the log: %s" % [
			LEAD, str(chip_there), ap_before, ap_after, str(objected), asked, _last_words(tail)],
		taken, {"log_tail": tail})
	await _shot("panel_chip_sent", "the order taken: the log's answer, an action spent")
	if panel != null and panel.visible and panel.has_method("close_panel"):
		panel.call("close_panel")
	await _frames(10)
	await _settle(15000)

	# 5 - Lannes selected, his attack card on Mack: Murat's chip
	var road := await _select(CARD_LEAD)
	var opened := await _open_attack_card()
	var terms := _card_terms()
	var oc = _card()
	var murat_chip: bool = terms.find("Murat · support " + CARD_LEAD + " · 1 AP") >= 0
	_rec("card_open", "selected %s (%s) and right-clicked %s's piece at %s" % [CARD_LEAD, road, FOE, FIELD],
		"card open=%s command='%s'; Murat's chip=%s; 'he may object'=%s" % [
			str(opened), str(oc.call("command")) if opened else "", str(murat_chip),
			str(terms.find("he may object") >= 0)],
		opened and murat_chip, {"terms": terms})
	await _shot("card_open", "Lannes's attack card: the muster, then the plan's chips")

	# 6 - the chip pressed on the card
	ap_before = _ap()
	var terms_label = oc.get("terms_label") if oc != null else null
	if terms_label != null and opened:
		terms_label.emit_signal("meta_clicked", "do:" + CARD_CHIP)
	await _frames(2)
	var shut_at_once: bool = oc != null and not oc.visible
	await _frames(6)
	await _settle(60000)
	await _frames(12)
	objected = await _answer_objection("card_chip")
	await _frames(24)
	asked = _question()
	ap_after = _ap()
	tail = _log_tail()
	var again := str(_main.get("_order_marshal"))
	_rec("card_chip", "pressed the card's chip '%s'" % CARD_CHIP,
		"card shut at once=%s; actions %d -> %d; objected=%s; a question raised='%s'; selected again=%s; the log: %s" % [
			str(shut_at_once), ap_before, ap_after, str(objected), asked, again, _last_words(tail)],
		shut_at_once and asked == "" and ap_after == ap_before - 1 and again == CARD_LEAD
			and tail.find("Murat") >= 0,
		{"log_tail": tail})
	await _shot("card_chip_sent", "the order sent from the card; Lannes selected again")

	# 7 - Lannes's card again: the muster as it then stands
	road = await _select(CARD_LEAD)
	opened = await _open_attack_card()
	terms = _card_terms()
	oc = _card()
	var muster_line := ""
	for raw in terms.split("\n"):
		if str(raw).find("would answer the guns") >= 0:
			muster_line = str(raw)
	var murat_counted: bool = muster_line.split(" would answer the guns")[0].find("Murat") >= 0
	var murat_gone: bool = terms.find("Murat · support " + CARD_LEAD) < 0
	_rec("card_again", "%s's attack card opened again (%s)" % [CARD_LEAD, road],
		"card open=%s; the muster: %s; Murat counted=%s; no chip for him again=%s" % [
			str(opened), muster_line, str(murat_counted), str(murat_gone)],
		opened and murat_counted and murat_gone, {"terms": terms})
	await _shot("card_again", "the card again: Murat in the muster, no chip for him")
	if oc != null and oc.visible:
		oc.call("_on_cancel")   # the card's Cancel: Lannes is not sent in
		await _frames(10)

	# 8 - Ney's card: Soult ordered, no chip left for him
	if _main.has_method("_clear_order_selection"):
		_main.call("_clear_order_selection")
		await _frames(6)
	road = await _select(LEAD)
	opened = await _open_attack_card()
	terms = _card_terms()
	oc = _card()
	muster_line = ""
	for raw in terms.split("\n"):
		if str(raw).find("would answer the guns") >= 0:
			muster_line = str(raw)
	var soult_counted: bool = muster_line.split(" would answer the guns")[0].find("Soult") >= 0
	var no_chip: bool = terms.find(" · support " + LEAD + " · ") < 0
	_rec("lead_card", "selected %s (%s) and opened his attack card" % [LEAD, road],
		"card open=%s command='%s'; the muster: %s; Soult counted=%s; no chip offered=%s" % [
			str(opened), str(oc.call("command")) if opened else "", muster_line, str(soult_counted),
			str(no_chip)],
		opened and soult_counted and no_chip, {"terms": terms})
	await _shot("lead_card", "Ney's attack card: Soult in the muster; Murat and Bernadotte offered no chip")

	# 9 - the attack sent; Act I names the plan
	ap_before = _ap()
	if opened:
		var sendb = oc.get("send_button")
		if sendb != null and sendb.visible and not sendb.disabled:
			sendb.emit_signal("pressed")
	await _frames(6)
	await _settle(90000)
	await _frames(12)
	objected = await _answer_objection("attack")
	await _secs(2.5)
	var dio = _main.get("battle_diorama")
	var on_table: bool = dio != null and dio.visible
	var plan := _plan_beat()
	var plan_ok: bool = plan.find(LEAD + " leads") >= 0 and plan.find("Soult") >= 0 \
		and plan.find("ordered in support") >= 0
	_rec("attack_sent", "pressed the card's Send (%s, attack %s)" % [LEAD, FOE],
		"actions %d -> %d; objected=%s; the tableau up=%s; Act I: %s" % [ap_before, _ap(), str(objected),
			str(on_table), plan],
		on_table and plan_ok, {"plan": plan})
	await _shot("act_one", "the battle on the table: Act I")
	await _secs(9.0)
	await _shot("the_battle_plays", "the acts play")
	await _secs(16.0)
	await _shot("the_field_at_rest", "the field at rest")
	_finish()


func _finish():
	if _done:
		return
	_done = true
	_out["ms"] = Time.get_ticks_msec() - _t0
	_out["final_turn"] = _turn()
	var path := _dir.path_join("walk.json") if _dir != "" else ""
	if path != "":
		var f := FileAccess.open(path, FileAccess.WRITE)
		if f != null:
			f.store_string(JSON.stringify(_out, "  "))
			f.close()
	quit(1 if _out.has("error") else 0)
