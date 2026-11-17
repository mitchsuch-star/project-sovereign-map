"""Row BA, BA-2: each new claim of the walk, watched FAILING with its fix
switched off. One mutation of battle_acts.gd at a time, the walk run headless
on the scenes it bears on — at the scene's own speed for the claims read in a
showing's first instant — and the file put back whatever happens.

    python tools/ba2_switch_off.py [<repo root> [<case key> ...]]

It CHANGES A SOURCE FILE IN THE WORKING TREE while it runs. So (the review of
November 15, 2026 — BA2-X15):

* never run it while a commit's hook is running (the hook tests the working
  tree) or while another session edits battle_acts.gd;
* it refuses to start while its lock or its kept copy exists — another copy is
  running, or one was killed: the kept copy (`tools/.ba2_switch_off.kept`) is
  then the file as it was, byte for byte;
* every anchor is checked before anything is written; the file is read and put
  back as BYTES, so its line endings are its own; the walk has a time limit.
"""
import hashlib
import os
import pathlib
import subprocess
import time
import sys

WALK_TIMEOUT_S = 1200

# key, name, [(old, new), ...], scenes, time scale, the words the failure must carry
CASES = [
    ("wall", "the wall is laid as it ended, and the opening does not stand it whole",
     [("""		host._transients.append(_wall)
		return
""", """		host._transients.append(_wall)
		_wall.show_the_end()
		return
"""), ("""	if _wall != null and is_instance_valid(_wall):
		_wall.stand_whole()
	for name in _works:
""", """	for name in _works:
""")], "assault_stormed", 1.0, "at the opening the wall already reads"),
    ("works", "the works are laid as they ended, and the opening does not rebuild them",
     [("""		bank.stand_as_built()
""", """		bank.stand_as_ended()
"""), ("""		(_works[name] as Rampart).stand_as_built()
""", """		pass
""")], "bombard_levels", 1.0, "the works stand at"),
    ("reserve", "the reserve's dead are on the table at the opening",
     [("""	for dead in _reserve_dead:
		if is_instance_valid(dead):
			(dead as Label).visible = false
""", """	for dead in _reserve_dead:
		if is_instance_valid(dead):
			pass
""")], "the_reserve", 1.0, "the reserve's dead are already told"),
    ("garrison", "the garrison keeps a portrait and a standard",
     [("""		if bool(c.get("garrison", false)):
			_dress_garrison(b)
""", """		if bool(c.get("garrison", false)):
			pass
""")], "assault_held", 8.0, "the garrison shows a portrait"),
    ("column", "a corps opens already in line",
     [("""		fig.position.x = float(fig.get_meta(&"ba_line_x")) * COLUMN_SQUEEZE
""", """		fig.position.x = float(fig.get_meta(&"ba_line_x"))
""")], "two_a_side", 1.0, "already stands in line"),
    ("wedge", "the order of battle is switched off",
     [("""const ORDER_OF_BATTLE := true
""", """const ORDER_OF_BATTLE := false
""")], "two_a_side", 8.0, "the table is laid as 'file'"),
    ("square", "a square is marked and not formed",
     [("""		_form_square(b, art)
""", """		pass
""")], "square_and_horse", 8.0, "is in square and stands in line"),
    ("standard", "the settled frame of a defeat leaves the victor's standard at home (BA2-X5)",
     [("""	_the_ground_is_as_it_ended()
	_the_victors_standard_stands_forward()
""", """	_the_ground_is_as_it_ended()
""")], "defeat_defending", 8.0, "'s standard stands at"),
    ("storm", "the stormers close up at once and the host's recoil stands them in line again",
     [("""	_close_up(b, AFTER_THE_RECOIL, 0.25)
""", """	_in_column(b)
""")], "assault_stormed", 8.0, "goes in standing in line"),
    ("ladders", "ladders are left against a wall that held",
     [("""		if fate != "stormed":
			_ladders = 0.0      # they fell back from it, or it opened its gates
""", """		if fate == "nothing":
			_ladders = 0.0      # they fell back from it, or it opened its gates
""")], "assault_held", 8.0, "ladders still stand against a wall that held"),
    # ── Row BA, BA-3: the day's panel (the walk's day claims, tools/ba1_acts_walk.py) ──
    # The panel is hidden while the acts play by TWO safeguards, each alone
    # invisible to the walk (measured November 15: built shown + held back, or
    # built hidden + not held back, both read clean): `_build_the_day` builds it
    # hidden and `_set_opening` holds it back again. They back one another, so
    # the case switches both off.
    ("day_hidden_at_opening", "the panel is built shown AND the opening does not hold it back",
     [("""	panel.visible = false
	host._tray_inner.add_child(panel)
""", """	panel.visible = true
	host._tray_inner.add_child(panel)
"""), ("""	host._vignette.modulate = Color.WHITE
	_hold_the_day_back()
""", """	host._vignette.modulate = Color.WHITE
""")], "day_opens", 1.0, "the day's panel is on the table while the acts play"),
    ("day_chrome", "the chrome the panel lent (verdict, plate, seal) is not put back for the next battle",
     [("""	host._verdict.visible = true
	host._nameplate.visible = true
	if host._seal != null:
		host._seal.visible = true
""", """	pass
""")], "day_opens", 8.0, "the chrome did not come back for the next battle"),
    ("day_room", "the panel does not take the room of the verdict, the plate and the seal",
     [("""	host._verdict.visible = false
	host._nameplate.visible = false
	if host._seal != null:
		host._seal.visible = false
	for laurel in _laurels():
		(laurel as CanvasItem).visible = false
	if _day_hide_shelves:
""", """	for laurel in _laurels():
		(laurel as CanvasItem).visible = false
	if _day_hide_shelves:
"""), ("""	host._verdict.visible = false
	host._nameplate.visible = false
	if host._seal != null:
		host._seal.visible = false
	for laurel in _laurels():
		(laurel as CanvasItem).visible = false


func _type_the_verdict""", """	for laurel in _laurels():
		(laurel as CanvasItem).visible = false


func _type_the_verdict""")], "day_opens", 8.0, "stands in the panel's room"),
    ("day_latch", "the in-flight latch is not set: a second press sends a second word",
     [("""	_day_latched = true                       # one press, one word
""", """	pass
""")], "day_opens", 8.0, "a second press before new data gave"),
    ("day_dim_draw", "a dim chip is drawn as a lit link",
     [("""	if bool(chip.get("ok", false)) and not _day_latched:
""", """	if not _day_latched:
"""), ("""	var lit: bool = bool(chip.get("ok", false)) and not _day_latched
	var price := int(chip.get("price", 0))
""", """	var lit: bool = not _day_latched
	var price := int(chip.get("price", 0))
""")], "day_dim_chip", 8.0, "is dim and is drawn as a link"),
    ("day_dim_press", "a dim chip's press is not refused (the handler's own guard)",
     [("""	if not (chip is Dictionary) or not bool(chip.get("ok", false)):
		return
""", """	if not (chip is Dictionary):
		return
""")], "day_dim_chip", 8.0, "pressing a dim chip gave"),
    ("day_focus", "the panel's lines take keyboard focus",
     [("""	l.focus_mode = Control.FOCUS_NONE        # Esc / Enter / Space keep their meaning
""", """	l.focus_mode = Control.FOCUS_ALL
""")], "day_opens", 8.0, "the panel takes keyboard focus"),
    # ── BA-3 round 2: the reworked panel (exits, scroll, pips, prices, head, follows) ──
    ("day_pips", "a spent point leaves no empty slot (slots are the points left, not `ours_of`)",
     [("""_day_pips(ours, slots_ours)""", """_day_pips(ours, ours)""")],
     "day_dim_chip", 8.0, "purse is drawn"),
    # (the second reading: the exits are cards — a one-line free chip stands on the table only
    # where the cards gave way, so the case takes them away first)
    ("day_free_price", "a free word shows a price",
     [("""		var exit_cards: bool = offering and can_tag                 # 6 the exits as cards, each with what it does
""", """		var exit_cards: bool = false
"""), ("""	return label if price <= 0 else "%s · %d" % [label, price]
""", """	return "%s · %d" % [label, price]
""")], "day_opens", 8.0, "is free and carries a price"),
    ("day_temper", "the head does not name his temper",
     [("""	if level >= 2 and str(day.get("his_temper", "")) != "":
""", """	if false and str(day.get("his_temper", "")) != "":
""")], "day_opens", 8.0, "does not name his temper"),
    ("day_follows_asks", "a table that follows asks the server for his answer",
     [("""	if not _day_asked and open and not follows \\
""", """	if not _day_asked and open \\
""")], "day_follows", 8.0, "a table that follows gave"),
    ("day_asks_twice", "a day that awaits him asks again every time the panel is shown",
     [("""	if not _day_asked and open and not follows \\
""", """	if open and not follows \\
"""), ("""		_day_asked = true
		host.word_given.emit("@refresh:" """, """		host.word_given.emit("@refresh:" """)],
     "day_opens", 8.0, "a day that awaits him gave"),
    ("day_no_script", "a payload with no script acts never shows its panel (`settle` does not show it)",
     [("""		host.get_tree().process_frame.connect(_refit_the_verdict, CONNECT_ONE_SHOT)
	_show_the_day()
""", """		host.get_tree().process_frame.connect(_refit_the_verdict, CONNECT_ONE_SHOT)
""")], "day_opens", 8.0, "is not shown at rest"),
    # ── BA-3 round 3: three boxes (the lead's own words, the groups, the exits), the banner, the shelf ──
    ("day_exits_scroll", "the exits row scrolls (it must stand whole on the tray's floor)",
     [("""		e_box.autowrap_mode = TextServer.AUTOWRAP_OFF
""", """		e_box.autowrap_mode = TextServer.AUTOWRAP_OFF
		e_box.scroll_active = true
""")], "day_opens", 8.0, "scrolls (only the groups may"),
    ("day_sliced", "the groups' box is cut 14 px short of its rows: a row is sliced at the bottom edge (j)",
     [("""			d_box.size = Vector2(d_box.size.x, d_h)
""", """			d_box.size = Vector2(d_box.size.x, d_h - 14.0)
""")], "day_ulm", 8.0, "(j)"),
    ("day_exit_leave", "'Leave it to <lead>' is not drawn among the exits",
     [("""	for i in _day_split()[2]:
""", """	for i in (_day_split()[2] as Array).slice(0, -1):
""")], "day_opens", 8.0, "row E draws"),
    ("day_guard_row", "the Guard is not one of the lead's own words (it falls into a group, off row C) (k)",
     [("""const DAY_OWN_KINDS := ["press", "guard", "dig_in"]""", """const DAY_OWN_KINDS := ["press", "dig_in"]""")],
     "day_ulm", 8.0, "row C draws"),
    ("day_exits_first", "the exits row is not anchored to the buttons: it stands at the top (l)",
     [("""		e_box.position = Vector2(0.0, e_top_abs - top)
""", """		e_box.position = Vector2(0.0, 0.0)
""")], "day_opens", 8.0, "(l) the exits row is not the last row"),
    ("day_resorted", "row C is drawn in reverse: the client re-sorts the block's array (m)",
     [("""	for i in _day_split()[0]:
""", """	var order: Array = _day_split()[0].duplicate()
	order.reverse()
	for i in order:
""")], "day_opens", 8.0, "(m) the chips are not drawn in the block's array order"),
    ("day_groups_wrong_index", "a group's name chip carries the NEXT chip's index (q)",
     [("""			line += _day_chip_bb(int(i), chips[int(i)], true) + " "
""", """			line += _day_chip_bb(int(i) + 1, chips[int(i)], true) + " "
""")], "day_ulm", 8.0, "without its link"),
    ("day_banner", "the day's banner does not replace the clash's headline (n)",
     [("""		host._banner.text = banner.to_upper()
		host._banner.add_theme_color_override("font_color", host._banner_color(""))
""", """		pass
""")], "day_opens", 8.0, "(n) the headline reads"),
    ("day_shelf", "the panel takes the shelves' room and leaves them standing (o)",
     [("""		_day_hide_shelves = give_shelves
""", """		_day_hide_shelves = false
""")], "day_ulm", 8.0, "(o) the shelf is up"),
    ("day_ulm_scrolls", "the groups box always scrolls: on Ulm at the shipped size a box scrolls (p)",
     [("""			d_box.meta_clicked.connect(_on_day_chip)
""", """			d_box.meta_clicked.connect(_on_day_chip)
			d_box.scroll_active = true
""")], "day_ulm", 8.0, "(p) a box scrolls on Ulm"),
    # ── BA-3 round 4: the builder's K1..K11 (the panel comes in final; the exits centred; the head's
    #    prefix; "His answer ▸"; the groups inline; the chipless refresh; no quill; the sub-banner; a decided day) ──
    ("day_early_panel", "the panel is shown at the gavel, with the skip hint still up and no Close (K1)",
     [("""	_clear_the_room()
""", """	_show_the_day()
""")], "day_opens", 8.0, "while the acts play"),
    ("day_exits_off_centre", "as one-line chips the exits row is nine pixels above the buttons' mid-line (K2)",
     [("""		var exit_cards: bool = offering and can_tag                 # 6 the exits as cards, each with what it does
""", """		var exit_cards: bool = false
"""), ("""		e_box.position = Vector2(0.0, e_top_abs - top)
""", """		e_box.position = Vector2(0.0, e_top_abs - top - 9.0)
""")], "day_opens", 8.0, "(K2)"),
    ("day_head_prefix", "the head never says the purses in words (K3)",
     [("""	if level >= 1:
		out += info + "%d of %d points[/color] " % [ours, slots_ours]
""", """	if level >= 99:
		out += info + "%d of %d points[/color] " % [ours, slots_ours]
""")], "day_opens", 8.0, "(K3)"),
    ("day_his_label", "the table that follows keeps its primary button's own word (K4)",
     [("""		host._btn_close.text = "His answer ▸"
""", """		pass
""")], "day_follows", 8.0, "(K4)"),
    ("day_his_advance", "the table that follows never goes on by itself (K4)",
     [("""			host.get_tree().create_timer(DAY_ADVANCE_S).timeout.connect(_his_answer_comes)
""", """			pass
""")], "day_follows", 8.0, "did not go on by itself"),
    ("day_his_reduced", "the table that follows goes on by itself under Reduce motion too (K4)",
     [("""		if not _his_waiting and not UiSettings.get_reduce_motion() and host.is_inside_tree():
""", """		if not _his_waiting and host.is_inside_tree():
""")], "day_follows", 8.0, "under Reduce motion the table that follows went on"),
    ("day_inline_off", "the groups never flow inline: three groups on the guns' day do not fit (K5)",
     [("""				inline = true                         # 2
""", """				pass
""")], "day_guns|--text-size 1.3", 8.0, "(K5)"),
    ("day_chipless_silent", "a chipless table that awaits our word asks nothing (K7)",
     [("""			and (str(day.get("awaits", "")) == "theirs" or chipless):
""", """			and (str(day.get("awaits", "")) == "theirs"):
""")], "day_opens", 8.0, "(K7)"),
    ("day_quill", "the verdict's quill is written over a day's own banner (K10)",
     [("""	if _day_panel != null and is_instance_valid(_day_panel):
		return
	host._type_verdict()
""", """	host._type_verdict()
""")], "day_opens", 8.0, "(K10)"),
    ("day_sub_banner", "the day's morning is not written into the sub-banner (K11)",
     [("""		if morning_said != "" and host._sub_banner.text == "":
			host._sub_banner.text = morning_said
""", """		pass
""")], "day_opens", 8.0, "(K11)"),
    ("day_decided_panel", "a day decided by its clash builds a panel over the verdict",
     [("""	if _day_banner() == "" and not bool(day.get("open", false)):
		return   # decided by its clash: that clash's verdict, plate and cues stand
""", """	pass
""")], "day_decided", 8.0, "built a panel"),
    # Row BA, BA-4 (November 16, 2026): the digits on the table and the first day's row.
    # (the second reading: on a day of two leads every control is a card — the one-line chips that
    # carry digits are the groups' names, on a crowded day)
    ("ba4_digit_face", "a chip does not show the digit that fires it (BA4-d)",
     [("""		label = "%d %s" % [digit, label]          # the selection card's form: "<digit> Label"
""", """		pass
""")], "day_ulm", 8.0, "(BA4-d)"),
    ("ba4_digit_press", "a digit does not press its slot's chip (BA4-k)",
     [("""	_on_day_chip("day:%d" % index)
	return true
""", """	return true
""")], "day_opens", 8.0, "(BA4-k)"),
    ("ba4_digit_denial", "a digit whose slot holds no lit chip is not denied (BA4-k)",
     [("""		_day_denied += 1
		AudioManager.play(DAY_DENY_CUE)
		return true
""", """		return true
""")], "day_opens,day_dim_chip", 8.0, "was not denied"),
    ("ba4_digit_at_rest", "a digit is the day's while the acts still play (BA4-k)",
     [("""		and bool(host._final) and _day_panel != null and is_instance_valid(_day_panel) \\
		and _day_panel.visible and _day_offering()
""", """		and _day_panel != null and is_instance_valid(_day_panel) and _day_offering()
""")], "day_opens", 8.0, "a digit while the acts play"),
    ("ba4_first_row_ack", "the first day's line is shown and never acknowledged (BA4-f)",
     [("""		_note_first_open(_day_first_screen)
		_day_first_screen = ""
""", """		_day_first_screen = ""
""")], "day_opens", 8.0, "(BA4-f)"),
    ("ba4_first_row_fit", "the first day's line takes a row on a table that has no room for it (BA4-f)",
     [("""			elif first_row:
				first_row = false                     # 5
""", """			elif false:
				first_row = false                     # 5
""")], "day_crowded,day_guns", 8.0, "(BA5-l)"),
    # ── Row BA, BA-5 "the finish": the day's table tells itself ──
    ("ba5_no_reading", "the head carries no reading of him (BA5-r)",
     [("""	if _day_reading(day) != "":
""", """	if false:
""")], "day_opens", 8.0, "(BA5-r)"),
    ("ba5_head_in_panel", "the head does not stand at the panel's own top (BA5-h)",
     [("""	var head := _day_rtl(panel, Vector2.ZERO, Vector2(DAY_W, 31.0))
""", """	var head := _day_rtl(panel, Vector2(0.0, 6.0), Vector2(DAY_W, 31.0))
""")], "day_opens", 8.0, "(BA5-h)"),
    ("ba5_card_says_nothing", "a card drops its second line and says what it does nowhere (BA5-c)",
     [("""	if caption != "":
""", """	if false:
""")], "day_opens", 8.0, "(BA5-c)"),
    ("ba5_cards_first_to_go", "the cards lose their second lines while the told line still stands (BA5-l)",
     [("""		var cards: bool = offering and can_card                     # 7 the cards' second lines
""", """		var cards: bool = false
""")], "day_ulm", 8.0, "(BA5-l)"),
    ("ba5_tags_on_the_buttons_row", "the exits are cards and the table says they are not (BA5-e)",
     [("""		_day_exits_up = exit_cards
""", """		_day_exits_up = false
""")], "day_opens", 8.0, "(BA5-e)"),
    ("ba5_tags_past_replay", "as one-line chips the exits keep a tag the row has no room for",
     [("""		var exit_cards: bool = offering and can_tag                 # 6 the exits as cards, each with what it does
""", """		var exit_cards: bool = false
"""), ("""				if e_box.get_content_width() <= DAY_CHIPS_W:
""", """				if true:
""")], "day_opens", 8.0, "runs past its box's right edge"),
    ("ba5_verdict_told_unsaid", "a battle's table does not say what told under its headline (BA5-v)",
     [("""		_sub_told = told
		host._sub_banner.text = told if host._sub_banner.text == "" else host._sub_banner.text + " " + told
""", """		_sub_told = ""
		pass
""")], "ulm_full", 8.0, "(BA5-v)"),
    ("ba5_close_stays_primary", "Close keeps the primary look while the words are offered (BA5-p)",
     [("""		host._btn_close.theme_type_variation = &""
""", """		pass
""")], "day_opens", 8.0, "(BA5-p)"),
    ("ba5_dice_read_early", "the tray reads its lines while the dice still tumble (BA5-d6)",
     [("""		for row in _rows:                # BA5-D6: nothing of the throw is told while it tumbles
			if is_instance_valid(row):
				(row as CanvasItem).visible = false
""", """		for row in _rows:                # BA5-D6: nothing of the throw is told while it tumbles
			if is_instance_valid(row):
				(row as CanvasItem).visible = true
""")], "ulm_full", 1.0, "(BA5-d6)"),
    # ── BA-5: the acts' speed (the switch in Close's room, the engine's clock) ──
    ("ba5_speed_doubles_unasked", "the acts double the clock at their own pace (BA5-s1)",
     [("""	var factor: float = float(UiSettings.BATTLE_SPEED_FACTORS.get(speed(), 1.0)) if playing else 1.0
""", """	var factor: float = 2.0 if playing else 1.0
""")], "ulm_full", 8.0, "(BA5-s1) the clock reads 200%"),
    ("ba5_speed_stays_up", "the speed switch stays on a table at rest (BA5-s1)",
     [("""		if hint != null and is_instance_valid(hint):
			visible = hint.visible
""", """		if hint != null and is_instance_valid(hint):
			visible = true
""")], "ulm_full", 8.0, "(BA5-s1) the speed switch is up while the skip hint is gone"),
    ("ba5_speed_clock_kept", "the acts keep the engine's clock after they end (BA5-s2)",
     [("""		if _clock_held and _clock_keeper == keeper:
			Engine.time_scale = _clock_base
			_clock_held = false
""", """		if _clock_held and _clock_keeper == keeper:
			_clock_held = false
""")], "ulm_full", 8.0, "(BA5-s2) the clock was not given back at the gavel"),
    ("ba5_verdict_measured_unwritten", "the verdict is measured before the quill has written it (BA5-d3)",
     [("""	var shown: int = v.visible_characters
	v.visible_characters = -1
""", """	var shown: int = v.visible_characters
""")], "ulm_full", 8.0, "(BA5-d3) the verdict stands behind a scrollbar"),
    # (the house rule) a step smaller is the verdict label's own Caption step: the check that reads it
    ("ba5_verdict_never_smaller", "a verdict too tall for its room is never set a step smaller (BA5-d3)",
     [("""\tvar tries: Array = [[VERDICT_STEP, _verdict_source], [VERDICT_STEP_SMALL, _verdict_source]]
""", """\tvar tries: Array = [[VERDICT_STEP, _verdict_source], [VERDICT_STEP, _verdict_source]]
"""), ("""\tfor step in [VERDICT_STEP, VERDICT_STEP_SMALL]:
""", """\tfor step in [VERDICT_STEP, VERDICT_STEP]:
""")], "the_capitulation|--text-size 1.3", 8.0, "(BA5-d3) a line too tall"),
    ("ba5_ground_over_the_men", "the ground is drawn over the men and the labels (BA5-g)",
     [("""	host._stage.move_child(g, 1)          # over the felt; under the lamp, the men and every label
""", """	pass
""")], "ulm_full", 8.0, "(BA5-g) the ground stands at"),
    ("ba5_ground_on_his_half", "the ground lies on the attacker's half (BA5-g)",
     [("""	g.dir = 1.0 if _attacker_left() else -1.0
""", """	g.dir = -1.0 if _attacker_left() else 1.0
""")], "ulm_full", 8.0, "(BA5-g) the ground lies on the attacker's half"),
    ("ba5_speed_press_skips", "a press on the speed switch is a click on the table (BA5-s3)",
     [("""	sw.focus_mode = Control.FOCUS_NONE       # Space and Enter stay the table's (skip, then close)
""", """	sw.mouse_filter = Control.MOUSE_FILTER_IGNORE
""")], "ulm_full", 8.0, "(BA5-s3) a press on it skipped the acts"),
    # Row BA, BA-5 — the second reading: the decision block, and figures that agree
    ("ba5_band_names_no_battle", "the band above the baize does not name the battle (BA5-n)",
     [("""	if _day_name() != "":
		name_label = host._mk_label(panel, _day_name(), &"Caption", BRASS, host._font_engraved)
""", """	if false:
		name_label = host._mk_label(panel, _day_name(), &"Caption", BRASS, host._font_engraved)
""")], "day_opens", 8.0, "(BA5-n)"),
    ("ba5_rule_misquoted", "the day's rule on the table is not the rule (BA5-u)",
     [("""const DAY_RULE := "A word costs points, and he answers it.""",
       """const DAY_RULE := "A word costs nothing, and he answers it.""")], "day_dim_chip", 8.0, "(BA5-u)"),
    ("ba5_counters_unscoped", "on a day's table neither counter says it counts this clash (BA5-k)",
     [("""		cap.text = plain.substr(0, plain.length() - DAY_LOSSES.length()) + DAY_CLASH_SCOPE
""", """		pass
""")], "day_opens", 8.0, "(BA5-k)"),
    ("ba5_march_cost_unsaid", "the advance's toll does not say what the march cost (BA5-m)",
     [("""	if kept > marched and marched > 0:
""", """	if false:
""")], "ulm_full", 8.0, "(BA5-m)"),
    ("ba5_exit_card_no_price", "an exit's card does not say that it is free (BA5-e)",
     [("""	var paid := "free" if price <= 0 else "%d %s" % [price, "point" if price == 1 else "points"]
""", """	var paid := ""
""")], "day_opens", 8.0, "(BA5-e)"),
    ("ba5_group_label_plain", "a group's label does not say what its kind of word does",
     [(""""lead": "Another leads the attack",""", """"lead": "Another leads",""")],
     "day_ulm", 8.0, "group's label"),
    ("ba5_lift_untold", "the panel takes the gap under the bars and the table does not say so (BA5-t)",
     [("""		_day_lifted = lifted
""", """		_day_lifted = false
""")], "day_ulm", 8.0, "(BA5-t)"),
    ("ba5_guns_uncounted", "the guns' toll is not counted as the battery fires (BA5-q)",
     [("""	_count_the_guns(fight_from, span + 0.4)
""", """	pass
""")], "the_guns", 1.0, "(BA5-q)"),
    ("ba5_line_reaches_the_reserve", "the line under the headline reaches the reserve's dead at Text size 130 %",
     [("""	sub.theme_type_variation = &"Caption"
	if _sub_fits(sub, half):
		return
	if _sub_told != "":
""", """	pass
	if true:
		return
	if _sub_told != "":
""")], "day_crowded|--text-size 1.3", 8.0, "ink over ink"),
    ("ba5_exit_cards_off_the_floor", "the exits' cards stand nine pixels off the tray's floor (BA5-e)",
     [("""				e_top_abs = DAY_BOTTOM - DAY_EXIT_FLOOR - e_h    # beside the buttons, down to the tray's floor
""", """				e_top_abs = DAY_BOTTOM - DAY_EXIT_FLOOR - e_h - 9.0
""")], "day_opens", 8.0, "(BA5-e)"),
    ("ba5_card_no_digit", "a card of the lead's own word does not show the digit that fires it (BA4-d)",
     [("""		head = "%d %s" % [digit, head]
	var why := str(chip.get("why", ""))
""", """		pass
	var why := str(chip.get("why", ""))
""")], "day_opens", 8.0, "(BA4-d)"),
    ("ba5_exit_card_no_digit", "an exit's card does not show the digit that fires it (BA4-d)",
     [("""		head = "%d %s" % [digit, head]
	var price := int(chip.get("price", 0))
""", """		pass
	var price := int(chip.get("price", 0))
""")], "day_opens", 8.0, "(BA4-d)"),
    # ── the session's review ──
    ("ba5_told_drops_how", "the closing table drops the line that says how the day ended (BA5-o)",
     # (the re-review) the table keeps at least four rows at every size the walk reads and a close
     # tells four lines, so a table that kept only the newest rows dropped nothing on a staged
     # scene: the case drops the first row kept - on a closing table, the line that says how it ended
     [("""	for i in _day_told_kept(lines, keep):
""", """	for i in _day_told_kept(lines, keep).slice(1):
""")],
     "day_night", 8.0, "(BA5-o)"),
    ("ba5_locked_card_hides_does", "a locked card's hover does not say what the word would do (BA5-c)",
     [("""		inner += "\\n" + Utils.bb_step(second, &"Caption")   # the ladder's Caption step
	# the hover: the rest of what the word does (its face says the first of it)
	# (the review) a locked card's face says why: its hover says it too, and what the word would do
	var tip := _day_chip_tip(chip, false, not lit and why != "")
""", """		inner += "\\n" + Utils.bb_step(second, &"Caption")   # the ladder's Caption step
	var tip := _day_chip_tip(chip, false, false)
""")], "day_dim_chip", 8.0, "(BA5-c)"),
    ("ba5_toll_one_line_lost", "at the baize's foot the march's cost is left off its one line (BA5-m)",
     [("""	var cost: int = int(b.get("march_cost", 0))
	if cost <= 0:
		return first
""", """	var cost: int = int(b.get("march_cost", 0))
	if true:
		return first
""")], "defeat_defending", 8.0, "(BA5-m)"),
    ("ba5_long_line_off_the_baize", "a liberation's line and what told run off the baize at 130 % (BA5-w)",
     [("""	if _sub_fits(sub, half):
		return
	if _sub_told != "":
""", """	if true:
		return
	if _sub_told != "":
""")], "ulm_full|--text-size 1.3", 8.0, "(BA5-w)"),
    ("ba5_cannonade_counts_the_act", "a cannonade's own count runs the whole act (BA5-q)",
     [("""		span = 1.2
""", """		pass
""")], "bombard_link", 1.0, "(BA5-q)"),
]


def _the_walk(root: pathlib.Path, scenes: str, speed: float) -> str:
    """The walk of one scene with the mutation in place -> everything it printed."""
    scenes, _, extra = scenes.partition("|")      # "day_guns|--text-size 1.3": the walk's own extra arguments
    cmd = [str(root / ".venv/Scripts/python.exe"), str(root / "tools/ba1_acts_walk.py"),
           "--tag", "ba2_switch_off", "--only", scenes, "--headless", "--time-scale", str(speed)] + extra.split()
    try:
        out = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True,
                             encoding="utf-8", errors="replace", timeout=WALK_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return f"the walk did not finish in {WALK_TIMEOUT_S} s"
    return (out.stdout or "") + (out.stderr or "")


def mutated(clean: bytes, swaps) -> bytes:
    """`clean` with each (old, new) put in once — in the file's own line
    endings. Raises ValueError when an anchor is not there exactly once."""
    text = clean.decode("utf-8")
    eol = "\r\n" if "\r\n" in text else "\n"
    text = text.replace("\r\n", "\n")
    for old, new in swaps:
        found = text.count(old)
        if found != 1:
            raise ValueError(f"an anchor matches {found} times: {old[:60]!r}")
        text = text.replace(old, new)
    return text.replace("\n", eol).encode("utf-8")


def _write(path: pathlib.Path, data: bytes, tries: int = 12, pause: float = 0.5) -> None:
    """Write `data`, trying again when Windows refuses the open for an instant.

    Row BA, BA-4 (November 16, 2026): a run started a minute after a windowed
    walk had closed died on its FIRST case — `OSError: [Errno 22] Invalid
    argument` opening `battle_acts.gd` to write, and again on the restore. The
    file had never been written (it equalled the kept copy) and took a write
    without complaint moments later: something held it for an instant. A
    restore that still fails after these tries raises, and the kept copy and
    the lock stay behind to say so, as after a killed run."""
    last: OSError | None = None
    for _ in range(max(1, tries)):
        try:
            path.write_bytes(data)
            return
        except OSError as exc:
            last = exc
            time.sleep(pause)
    assert last is not None
    raise last


def switch_off(root: pathlib.Path, only=(), walk=_the_walk, cases=None, say=print):
    """Run the cases -> [(name, caught)]. The file is put back, byte for byte,
    whatever happens short of the process being killed — and then the kept
    copy and the lock stay behind to say so."""
    root = pathlib.Path(root)
    acts = root / "godot-client/project-sovereign/scripts/battle_acts.gd"
    lock = root / "tools/.ba2_switch_off.lock"
    kept = root / "tools/.ba2_switch_off.kept"
    chosen = [case for case in (CASES if cases is None else cases) if not only or case[0] in only]
    if lock.exists() or kept.exists():
        raise SystemExit(
            f"refused: {lock.name} or {kept.name} exists in tools/ — another copy is running, or one "
            f"was killed. If none is running: {kept.name} is battle_acts.gd as it was; put it back "
            f"(or read `git diff` of battle_acts.gd), then delete both.")
    clean = acts.read_bytes()
    clean_sha = hashlib.sha256(clean).hexdigest()
    for _key, name, swaps, *_rest in chosen:          # every anchor, before anything is written
        try:
            mutated(clean, swaps)
        except ValueError as exc:
            raise SystemExit(f"refused, nothing written — '{name}': {exc}")
    with open(lock, "x", encoding="utf-8") as handle:  # "x": two copies cannot both pass here
        handle.write(str(os.getpid()))
    results = []
    try:
        kept.write_bytes(clean)
        for _key, name, swaps, scenes, speed, words in chosen:
            _write(acts, mutated(clean, swaps))
            text = walk(root, scenes, speed)
            caught = words in text
            tail = [line for line in text.splitlines() if "claim(s) failed" in line]
            results.append((name, caught))
            say(("CAUGHT  " if caught else "MISSED  ") + name + " :: "
                + (tail[-1].strip().split(";")[0] if tail else "?"))
            if not caught:
                say("   ... " + "\n   ... ".join(text.splitlines()[-12:]))
    finally:
        _write(acts, clean)
        back = hashlib.sha256(acts.read_bytes()).hexdigest() == clean_sha
        say(f"battle_acts.gd put back: {back}")
        if back:
            kept.unlink(missing_ok=True)
            lock.unlink(missing_ok=True)
    return results


def main(argv) -> int:
    root = pathlib.Path(argv[1]) if len(argv) > 1 else pathlib.Path(__file__).resolve().parents[1]
    results = switch_off(root, set(argv[2:]), say=lambda line: print(line, flush=True))
    print(sum(1 for _name, caught in results if caught), "of", len(results),
          "claims caught their fix switched off")
    return 0 if results and all(caught for _name, caught in results) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
