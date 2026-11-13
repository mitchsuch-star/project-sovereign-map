extends SceneTree
# RE-5 the close — the Mode C walk on 8007 (`docs/RECURRING_EVENTS_SPEC.md`
# §16 "RE-5", §16b; the landing record §26.1; November 2, 2026).
#
#   $env:SOVEREIGN_PORT        = "8007"        # a sandboxed backend listening there
#   $env:RE5_WALK_OUT          = "<abs dir>"   # frames + walk.json land here
#   $env:RE5_WITHDRAWAL_SAVE   = "re5_withdrawal.json"   # chapter B's crafted save
#   <godot> --audio-driver Dummy --windowed --resolution 1920x1080 \
#           --path godot-client/project-sovereign --script <abs>/tools/re5_mode_c_walk.gd
#
# The REAL `main.tscn` with the REAL APIClient against a live sandboxed backend
# (never 8005 or 8006 — the player's ports). Every key is pushed into the
# viewport as an ENGINE event, every typed line goes down the command line's
# own road, every button is pressed as the capture harness presses it (its
# own `pressed` signal) and every desk chip as the page's own `meta_clicked`;
# no operating-system input, the window parked off the desktop. The script
# reads the desk each morning and acts on what arrives — seeded paths, not
# laws; `walk.json` records the turns it found.
#
#   Chapter A — the fresh campaign (the shipped default, the courts decreeing)
#     rail / arrival      the first affair stands (the rail card; the desk's "Read the letter ▸")
#     letter              the letter in the dress (the device, the board, the priced buttons, the counsel)
#     seal / echo         the Accept: the answer beat; the response's lines
#     receipt             the morning after: SITUATION's receipt
#     correspondence      the page: the desk, the offing, the answered slip
#     home                the squadron settled (its fate on the slip and in the morning)
#     offer / offer_seal  the first offer (an Edict) and its Accept
#     laws_edicts         THE LAWS — THE EDICTS block
#     recruit_quote       `recruit cavalry` — the quote names the decree
#     watch               the Dispatch's Watch naming the next letter
#     lapsed              a letter left unopened lapses: the set-aside slip
#   Chapter B — the crafted save (the Host's Claims standing, the Match due)
#     standing            the letter on the desk after the load
#     withdrawn           the morning after: set aside for the Match
#     set_aside           the Correspondence's set-aside slip

const WALL_LIMIT_MS := 1200000
const OUT_DEFAULT := "res://../../docs/audits/re5_mode_c_2026_11_02"
const TURN_CAP := 30
const TEXT_CAP := 2400

var _main = null
var _out: Dictionary = {"steps": [], "turns": {}, "errors": []}
var _dir := ""
var _t0 := 0
var _done := false
var _n := 0


func _init():
	UiSettings._cfg = ConfigFile.new()
	UiSettings._persist = false   # Session UI-5: the harness flag — writes stay in memory, and the scripted day keeps its one End Turn
	_t0 = Time.get_ticks_msec()
	process_frame.connect(_watchdog)
	_walk.call_deferred()


func _watchdog():
	if not _done and Time.get_ticks_msec() - _t0 > WALL_LIMIT_MS:
		_out["error"] = "wall-clock limit hit"
		_finish()


# ── the engine's own roads ───────────────────────────────────────────────────

func _frames(n: int) -> void:
	for _i in range(n):
		await process_frame


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


func _key(keycode: int, unicode: int = 0) -> void:
	for pressed in [true, false]:
		var ev := InputEventKey.new()
		ev.keycode = keycode
		ev.physical_keycode = keycode
		ev.unicode = unicode
		ev.pressed = pressed
		root.push_input(ev)
	await _frames(3)


func _type(line: String) -> void:
	var input = _main.get("command_input")
	input.text = line
	input.caret_column = line.length()
	_main.call("_execute_command")
	await _settle(90000)
	await _frames(6)


func _turn() -> int:
	return int(_main.get("current_turn")) if _main != null else 0


func _terminal_tail(chars: int = 1200) -> String:
	var display = _main.get("output_display")
	var text: String = display.get_parsed_text() if display != null else ""
	return text.substr(maxi(0, text.length() - chars))


func _cap(text: String) -> String:
	return text if text.length() <= TEXT_CAP else text.substr(0, TEXT_CAP) + " …"


func _all_nodes(from: Node) -> Array:
	var out: Array = []
	var stack: Array = [from]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		out.append(n)
		for c in n.get_children():
			stack.append(c)
	return out


func _texts_under(from: Node) -> String:
	var parts: Array = []
	for n in _all_nodes(from):
		if n is RichTextLabel and n.is_visible_in_tree():
			parts.append(n.get_parsed_text())
		elif n is Label and n.is_visible_in_tree() and str(n.text) != "":
			parts.append(str(n.text))
	return "\n".join(parts)


func _press_text(scope: Node, first_line: String) -> bool:
	# The capture harness's road: the button's own `pressed` — matched on the
	# first line of its text (the letter's buttons are two-line priced).
	for b in _all_nodes(scope):
		if b is BaseButton and b.is_visible_in_tree() and not b.disabled and ("text" in b):
			var head := str(b.text).strip_edges().split("\n")[0].strip_edges()
			if head == first_line:
				b.emit_signal("pressed")
				return true
	return false


func _hold_window() -> void:
	# A load's refit can hand the window to the desktop; every frame is taken
	# at the walk's one size, parked off the desktop.
	if root.mode != Window.MODE_WINDOWED or root.size != Vector2i(1920, 1080):
		root.mode = Window.MODE_WINDOWED
		root.size = Vector2i(1920, 1080)
		root.position = Vector2i(5200, 20)
		await _frames(6)


func _clear_overlays() -> void:
	# What a player dismisses before reading a screen: the enemy phase's
	# report (its own Continue) and the envoys' panel that opens on its own
	# when two or more letters wait (its own Close). The letter popup and
	# the screens are left as the scene has them.
	for _i in range(8):
		var pressed := false
		# the battle diorama ("click anywhere to skip"), one per battle of the
		# night — found by its script, skipped by its own road
		for n in _all_nodes(root):
			var scr = n.get_script() if n is Object and n.has_method("get_script") else null
			if scr == null or not str(scr.resource_path).ends_with("battle_diorama.gd"):
				continue
			if not (("visible" in n) and bool(n.visible)):
				continue
			# played to its final frame it offers Replay / Close — the Close;
			# still playing, a click anywhere skips to that frame
			if _press_text(n, "Close"):
				pass
			elif n.has_method("_skip_to_final"):
				n.call("_skip_to_final")
			else:
				var ev := InputEventMouseButton.new()
				ev.button_index = MOUSE_BUTTON_LEFT
				ev.pressed = true
				ev.position = Vector2(960, 540)
				ev.global_position = ev.position
				root.push_input(ev, true)
				ev = InputEventMouseButton.new()
				ev.button_index = MOUSE_BUTTON_LEFT
				ev.pressed = false
				ev.position = Vector2(960, 540)
				ev.global_position = ev.position
				root.push_input(ev, true)
			pressed = true
			break
		var mb = _mailbox()
		if mb != null and mb.visible:
			var btn = mb.get("close_btn")
			if btn != null:
				btn.emit_signal("pressed")
				pressed = true
			else:
				mb.visible = false
		# a court's envoy promoted into the popup after a letter was answered:
		# a player sets it aside with its own Not Now (it waits in the mailbox);
		# a letter of state in the popup is the scene's own and is left standing
		var p = _popup()
		if p != null and p.visible:
			var data = p.get("current_data")
			var is_letter: bool = data is Dictionary and bool(data.get("is_moment", false))
			if not is_letter:
				var dismiss = p.get("dismiss_btn")
				if dismiss != null and not dismiss.disabled and dismiss.visible:
					dismiss.emit_signal("pressed")
					pressed = true
		# the enemy phase's report is a CanvasLayer registered with the dialog
		# manager; its Continue is the player's road out of it
		var ep = _main.get("enemy_phase_dialog")
		if ep != null and ("visible" in ep) and bool(ep.visible):
			if _press_text(ep, "Continue"):
				pressed = true
			elif _press_text(root, "Continue"):
				pressed = true
			else:
				ep.visible = false
		# a marshal's interrupt ("TEULIE REPORTS — cornered: fight to the last
		# or attempt a breakout") stands over the screens until answered: a
		# player answers it; the walk takes the first option offered and
		# records what it took
		var ip = _main.get("interrupt_popup")
		if ip != null and ("visible" in ip) and bool(ip.visible):
			var bc = ip.get("button_container")
			var taken := ""
			if bc != null:
				for c in bc.get_children():
					if c is BaseButton and not c.disabled and c.visible:
						taken = str(c.text)
						c.emit_signal("pressed")
						break
			if taken == "":
				ip.visible = false
			var overlays: Array = _out.get("overlays", [])
			overlays.append({"turn": _turn(), "kind": "interrupt", "marshal": str(ip.get("current_marshal")), "took": taken})
			_out["overlays"] = overlays
			pressed = true
		if not pressed:
			break
		await _frames(6)
		await _settle()


func _scroll_to(scroll, label, needle: String) -> bool:
	# Scroll a screen's ScrollContainer to the first paragraph of its rich
	# text that carries the needle (the EDICTS block, the set-aside line) —
	# what a player scrolls to before reading it; false when absent.
	if scroll == null or label == null:
		return false
	var paras := str(label.get_parsed_text()).split("\n")
	var up := needle.to_upper()
	for i in range(paras.size()):
		if str(paras[i]).to_upper().contains(up):
			var y := 0.0
			if label.has_method("get_paragraph_offset"):
				y = float(label.call("get_paragraph_offset", i))
			else:
				var bar = scroll.get_v_scroll_bar()
				y = float(bar.max_value) if bar != null else 0.0
			scroll.set("scroll_vertical", int(maxf(0.0, y - 24.0)))
			return true
	return false


func _shot(name: String, note: String, extra: Dictionary = {}, clear: bool = true) -> void:
	if clear:
		await _clear_overlays()
	await _hold_window()
	var park := InputEventMouseMotion.new()
	park.position = Vector2(-40, -40)
	park.global_position = park.position
	root.push_input(park, true)
	await _frames(4)
	_n += 1
	var img := root.get_texture().get_image()
	var file := "RE5_%02d_%s_2026_11_02.jpg" % [_n, name]
	var err := img.save_jpg(_dir.path_join(file), 0.86)
	var row := {"step": name, "note": note, "frame": file, "saved": err == OK, "turn": _turn(),
		"ms": Time.get_ticks_msec() - _t0}
	for k in extra:
		row[k] = extra[k]
	_out["steps"].append(row)


func _note_error(what: String) -> void:
	_out["errors"].append({"turn": _turn(), "what": what})


# ── the screens ──────────────────────────────────────────────────────────────

func _top_bar():
	return _main.get("top_bar")


func _dispatch():
	return _main.get("dispatch_view")


func _popup():
	return _main.get("incoming_proposal_popup")


func _ledger():
	var tb = _top_bar()
	if tb == null:
		return null
	var screens = tb.get("screens")
	return screens.get("ledger") if screens is Dictionary else null


func _open_dispatch() -> void:
	var dv = _dispatch()
	if dv != null and dv.visible:
		return
	await _key(KEY_R, 114)
	await _frames(6)
	dv = _dispatch()
	if dv != null and not dv.visible and _top_bar() != null:
		_top_bar().call("toggle_screen", "dispatch")
		await _frames(6)
	await _settle()
	await _frames(4)


func _close_dispatch() -> void:
	var dv = _dispatch()
	if dv != null and dv.visible:
		dv.call("close_view")
		await _frames(4)


func _mailbox():
	return _main.get("mailbox_panel")


func _close_modals() -> void:
	# The envoys' panel opens on its own when two or more letters wait and
	# stands as a modal over the screens; a player closes it with its own
	# Close — so does the walk. The letter popup is left to its scene.
	var mb = _mailbox()
	if mb != null and mb.visible:
		var btn = mb.get("close_btn")
		if btn != null:
			btn.emit_signal("pressed")
		else:
			mb.visible = false
		await _frames(6)
	await _close_dispatch()
	await _close_ledger()


func _dispatch_text() -> String:
	var dv = _dispatch()
	if dv == null:
		return ""
	var label = dv.get("content_label")
	return str(label.get_parsed_text()) if label != null else ""


func _open_correspondence() -> void:
	await _open_dispatch()
	var dv = _dispatch()
	if dv == null:
		return
	if bool(dv.call("has_correspondence")):
		if not _press_text(dv, str(dv.get("correspondence_button").text).strip_edges()):
			dv.call("open_correspondence")
	else:
		dv.call("open_correspondence")
	await _settle()
	await _frames(8)


func _correspondence_text() -> String:
	var dv = _dispatch()
	if dv == null:
		return ""
	var box = dv.get("corr_box")
	return _texts_under(box) if box != null else ""


func _corr() -> Dictionary:
	var dv = _dispatch()
	if dv == null:
		return {}
	var c = dv.get("_corr")
	return c if c is Dictionary else {}


func _desk_rows() -> Array:
	# The page's own payload: the standing slips (register "affair" for a
	# letter of state, "moment" for a dated letter of the record).
	var out: Array = []
	for row in (_corr().get("standing", []) as Array):
		if row is Dictionary:
			out.append(row)
	return out


func _desk_chip() -> String:
	# The desk's "Read the letter ▸" chip of the first AFFAIR standing: the
	# page's own url `corr:read:<mailbox id>` (a dated moment's letter stands
	# on the same desk and is left to its own road).
	for row in _desk_rows():
		if str(row.get("register", "")) == "affair" and int(row.get("mailbox_id", 0) or 0) > 0:
			return "corr:read:%d" % int(row.get("mailbox_id"))
	return ""


func _set_aside_rows() -> Array:
	var c := _corr()
	var rows = c.get("set_aside", c.get("aside", []))
	var out: Array = []
	for row in (rows if rows is Array else []):
		if row is Dictionary:
			out.append(row)
	return out


func _read_letter_from_desk() -> bool:
	var dv = _dispatch()
	var box = dv.get("corr_box") if dv != null else null
	if box == null:
		return false
	var url := _desk_chip()
	if url == "":
		return false
	for n in _all_nodes(box):
		if n is RichTextLabel and str(n.text).contains(url):
			n.emit_signal("meta_clicked", url)
			break
	await _settle()
	await _frames(10)
	var p = _popup()
	return p != null and p.visible


func _letter_read() -> Dictionary:
	var p = _popup()
	if p == null or not p.visible:
		return {}
	var data: Dictionary = p.get("current_data") if p.get("current_data") is Dictionary else {}
	return {
		"title": str(data.get("title", data.get("header", ""))),
		"register": str(data.get("register", "")),
		"writer": str(data.get("writer", "")),
		"accept": str(p.get("accept_btn").text).replace("\n", " / "),
		"decline": str(p.get("reject_btn").text).replace("\n", " / "),
		"counsel": str(data.get("counsel", "")),
		"body": _cap(str(p.get("content_label").get_parsed_text())),
	}


func _accept_letter(name: String) -> void:
	var p = _popup()
	if p == null or not p.visible:
		_note_error("accept: no letter open")
		return
	var before := _terminal_tail(200)
	p.get("accept_btn").emit_signal("pressed")
	# The beat starts on the RESPONSE (`moment_answered`), not on the press:
	# wait for it to land, set aside a court's envoy the same response may
	# have promoted into the popup (its own Not Now, no settling — the slip
	# lives 0.8 s), then the frame inside the beat, the overlays left as
	# they are (the slip rides layer 125, over every dialog — RE5-3).
	await _settle(90000)
	var next_envoy = _popup()
	if next_envoy != null and next_envoy.visible:
		var data = next_envoy.get("current_data")
		if not (data is Dictionary and bool(data.get("is_moment", false))):
			var dismiss = next_envoy.get("dismiss_btn")
			if dismiss != null and not dismiss.disabled and dismiss.visible:
				dismiss.emit_signal("pressed")
	await _frames(10)
	await _shot(name + "_seal", "the response landed: the answer beat — the apostille and the seal", {}, false)
	await _settle(90000)
	await _frames(40)
	var tail := _terminal_tail(1400)
	await _shot(name + "_echo", "the response: the apply line and the echo", {"terminal": _cap(tail), "before": _cap(before)})


func _end_turn() -> void:
	await _close_dispatch()
	var before := _turn()
	await _type("end turn")
	await _settle(120000)
	await _frames(12)
	# The client's own gates ask for the order again — the peril warning
	# ("Press End Turn again … or type end turn again") and the lapse
	# warning; a player types it again, so does the walk (twice at most).
	for _i in range(2):
		if _turn() != before:
			break
		if _terminal_tail(600).contains("end turn again"):
			await _type("end turn")
			await _settle(120000)
			await _frames(12)
	# the morning's report read and dismissed, as a player does
	await _clear_overlays()
	_out["turns"][str(_turn())] = Time.get_ticks_msec() - _t0


func _advance_until_desk(cap: int, what: String) -> bool:
	# End turns until the desk carries a chip (a letter standing), or the cap.
	for _i in range(cap):
		await _open_correspondence()
		if _desk_chip() != "":
			return true
		await _end_turn()
		if _turn() > TURN_CAP:
			break
	_note_error("no letter on the desk: " + what)
	return false


func _lines_with(text: String, needles: Array) -> Array:
	var out: Array = []
	for line in text.split("\n"):
		for nd in needles:
			if line.to_lower().contains(str(nd).to_lower()):
				out.append(line.strip_edges())
				break
	return out


func _laws_text() -> String:
	# THE LAWS is the ledger's eighth book (forces, territories, economy,
	# intel, manpower, orders, the Admiralty, the laws): the key 8.
	await _close_modals()
	var tb = _top_bar()
	if tb != null:
		tb.call("toggle_screen", "ledger")
	await _settle()
	await _frames(6)
	var ledger = _ledger()
	if ledger == null or not ledger.visible:
		_note_error("no ledger screen open")
		return ""
	await _key(KEY_8, 56)
	await _frames(4)
	if ledger.has_method("_switch_tab"):
		ledger.call("_switch_tab", 7)
	await _settle()
	await _frames(8)
	var area = ledger.get("content_area")
	return str(area.get_parsed_text()) if area != null else ""


func _close_ledger() -> void:
	var ledger = _ledger()
	if ledger != null and ledger.visible and _top_bar() != null:
		_top_bar().call("toggle_screen", "ledger")
		await _frames(4)


# ── the walk ─────────────────────────────────────────────────────────────────

func _walk() -> void:
	var dir_env := OS.get_environment("RE5_WALK_OUT")
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
	_out["boot_turn"] = _turn()
	await _frames(10)

	# ── Chapter A ──
	# The live board at turn 6 with the standing held (RE5-2: an idle
	# Emperor's standing falls under the Marine's floor by turn 7 and the
	# letter never comes) — loaded by the client's own road.
	var save_a := OS.get_environment("RE5_CHAPTER_A_SAVE")
	if save_a != "":
		_main.call("_on_load_save_selected", save_a)
		await _settle(90000)
		await _frames(20)
		_out["chapter_a_loaded_turn"] = _turn()
	# A1 — the first affair: end turns until the desk carries a letter.
	if await _advance_until_desk(12, "the first affair"):
		await _close_dispatch()
		await _shot("rail", "the morning the letter came: the rail card, the map, the terminal",
			{"terminal": _cap(_terminal_tail(900))})
		await _open_correspondence()
		await _shot("arrival", "the Correspondence's desk: the letter standing, 'Read the letter ▸'",
			{"desk": _cap(_correspondence_text())})
		# A2 — the letter in the dress.
		if await _read_letter_from_desk():
			var read := _letter_read()
			_out["first_letter"] = read
			await _shot("letter", "the letter opened from the desk: the dress", read)
			# A3 — the Accept: the seal, the echo.
			await _accept_letter("accept")
		else:
			_note_error("the first letter did not open from the desk")
		# A4 — the morning after: the receipt; the Correspondence.
		await _end_turn()
		await _open_dispatch()
		var morning := _dispatch_text()
		await _shot("receipt", "the morning after: SITUATION's receipt",
			{"receipt_lines": _lines_with(morning, ["squadron", "sail", "Decrès", "Domingo", "magazines", "remounts", "camps", "decree", "edict"])})
		await _open_correspondence()
		await _shot("correspondence", "the page: the desk, the offing, the answered slip",
			{"page": _cap(_correspondence_text())})
		# A5 — the squadron settled: end turns until the slip names its fate.
		var fate := ""
		for _i in range(8):
			await _end_turn()
			await _open_correspondence()
			var page := _correspondence_text()
			var hits := _lines_with(page, ["came home", "home whole", "caught", "were lost", "lost with", "are ashore", "home T", "returned"])
			if not hits.is_empty():
				fate = str(hits[0])
				break
		await _open_dispatch()
		await _shot("home", "the squadron's fate", {"fate": fate,
			"morning_lines": _lines_with(_dispatch_text(), ["squadron", "sail", "home", "caught", "lost", "Decrès"]),
			"page": _cap(_correspondence_text())})
	# A6 — the offer, an Edict: the edicts pins' Remounts board (the live
	# board's offer moved between the walk's own runs — turn 13, turn 14,
	# never by turn 23 — a seeded path per process, so the scene is promised
	# from a board), loaded by the client's own road.
	var offer_turn := 0
	var save_d := OS.get_environment("RE5_OFFER_SAVE")
	var offer_ready := false
	if save_d != "":
		await _close_modals()
		_main.call("_on_load_save_selected", save_d)
		await _settle(90000)
		await _frames(20)
		_out["offer_loaded_turn"] = _turn()
		await _open_correspondence()
		offer_ready = _desk_chip() != ""
		if not offer_ready:
			_note_error("the offer board carries no letter on the desk")
	else:
		offer_ready = await _advance_until_desk(12, "the first offer")
	if offer_ready:
		offer_turn = _turn()
		if await _read_letter_from_desk():
			var read2 := _letter_read()
			_out["offer_letter"] = read2
			await _shot("offer", "the offer in the dress: the two priced buttons", read2)
			await _accept_letter("offer")
		else:
			_note_error("the offer did not open from the desk")
		var laws := await _laws_text()
		# the book opens at its head; a player scrolls to the EDICTS block
		var ledger_screen = _ledger()
		if ledger_screen != null:
			if not _scroll_to(ledger_screen.get("scroll_container"), ledger_screen.get("content_area"), "EDICT"):
				_scroll_to(ledger_screen.get("scroll_container"), ledger_screen.get("content_area"), "In force until")
			await _frames(4)
		await _shot("laws_edicts", "THE LAWS — THE EDICTS block",
			{"edicts_lines": _lines_with(laws, ["EDICT", "In force until", "No edict", "Magazines", "Remounts", "Camps"]),
			 "laws": _cap(laws)})
		await _close_modals()
		# the reply to a bare `recruit cavalry` names the order when no corps
		# of horse stands in reach: "Murat, recruit cavalry" — the walk types it
		await _type("recruit cavalry")
		var tail := _terminal_tail(1400)
		var marshal_rx := RegEx.new()
		marshal_rx.compile("'([A-Z][a-z]+), recruit cavalry'")
		var named := marshal_rx.search(tail)
		if named != null:
			await _type("%s, recruit cavalry" % named.get_string(1))
			tail = _terminal_tail(1400)
		await _shot("recruit_quote", "`recruit cavalry`: the quote",
			{"quote_lines": _lines_with(tail, ["recruit", "Remounts", "×", "cavalry", "levy"]), "terminal": _cap(tail)})
		await _open_correspondence()
		_out["offer_offing"] = _lines_with(_correspondence_text(), ["may write", "may offer", "may ask", "gathering"])
	_out["offer_turn"] = offer_turn

	# ── Chapter C — a letter left unopened lapses (a crafted save) ──
	var save_c := OS.get_environment("RE5_LAPSE_SAVE")
	if save_c != "":
		await _close_modals()
		_main.call("_on_load_save_selected", save_c)
		await _settle(90000)
		await _frames(20)
		_out["lapse_loaded_turn"] = _turn()
		await _open_correspondence()
		var left_id := ""
		for row in _desk_rows():
			if str(row.get("register", "")) == "affair":
				left_id = str(row.get("id", ""))
				break
		await _shot("left", "a letter of state left on the desk, unopened",
			{"chip": _desk_chip(), "left_id": left_id, "desk": _cap(_correspondence_text())})
		var lapsed: Dictionary = {}
		for _i in range(3):
			await _end_turn()
			await _open_correspondence()
			for row in _set_aside_rows():
				if str(row.get("id", "")) == left_id and str(row.get("kind", "")) == "lapsed":
					lapsed = {"id": left_id, "line": str(row.get("line", "")), "label": str(row.get("label", ""))}
					break
			if not lapsed.is_empty():
				break
		await _shot("lapsed", "the letter lapsed: the set-aside slip", {"left_id": left_id, "lapsed": lapsed,
			"morning_lines": _lines_with(_dispatch_text(), ["lapse", "unanswered", "set aside"]),
			"page": _cap(_correspondence_text())})

	# ── Chapter B — the crafted save ──
	var save_name := OS.get_environment("RE5_WITHDRAWAL_SAVE")
	if save_name != "":
		await _close_modals()
		_main.call("_on_load_save_selected", save_name)
		await _settle(90000)
		await _frames(20)
		_out["loaded_turn"] = _turn()
		await _open_correspondence()
		await _shot("standing", "the crafted save: the Host's Claims standing on the desk",
			{"chip": _desk_chip(), "desk": _cap(_correspondence_text())})
		# the Watch, on this board: IN THE OFFING on the page and in the morning's SITUATION
		var offing := _lines_with(_correspondence_text(), ["may write", "may offer", "may ask", "gathering"])
		await _close_dispatch()
		await _open_dispatch()
		await _shot("watch", "the Watch: the matters that may yet write",
			{"offing": offing,
			 "watch_lines": _lines_with(_dispatch_text(), ["may write", "may offer", "may ask", "gathering"])})
		await _end_turn()
		await _open_dispatch()
		# the set-aside line sits below SITUATION; a player scrolls to it
		var dv = _dispatch()
		if dv != null:
			_scroll_to(dv.get("scroll_container"), dv.get("content_label"), "set aside")
			await _frames(4)
		await _shot("withdrawn", "the morning after: the letter set aside for the Match",
			{"morning_lines": _lines_with(_dispatch_text(), ["set aside", "Match", "Host"]),
			 "terminal": _cap(_terminal_tail(900))})
		await _open_correspondence()
		await _shot("set_aside", "the Correspondence's set-aside slip",
			{"page": _cap(_correspondence_text()), "popup_open": _popup() != null and _popup().visible,
			 "popup": _letter_read()})
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
