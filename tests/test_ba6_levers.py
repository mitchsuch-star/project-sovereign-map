"""Row BA, "the levers past 5" (BA-6) — the client half, pinned at the source.

Two blind readers scored the day table's player agency 5 and decision clarity 5
(bar 7). Their asks (`docs/BATTLE_DIORAMA_SPEC.md` §15.23) became six levers on
the day's panel; the backend half (the chips' `risk`, the exits' stakes in
`does`) is pinned elsewhere. What stands here is what the client does with
them — by source, the behaviour itself being read by the acts' walk
(`tools/ba1_acts_walk.py`, claims BA6-1 … BA6-6, each watched failing with its
fix off in `tools/ba2_switch_off.py`):

1. the tray grows by DAY_ROOM while a day's panel stands, the foot's controls
   and the panel's floor with it, and a table without a day is as it was built;
2. the lead's own words are three-line cards (the word at the body's size, what
   it does and what it risks at the Caption step), the third line shed first;
3. the exits' stakes: a full-width row above the buttons, the second line
   wrapped at a semicolon, the one-line chips as the last rung;
4. the groups show the chips the digits reach and one quiet "+N more";
5. the luck set against what told, in one phrase;
6. the table's marks in one caption line, in the marks themselves.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "godot-client" / "project-sovereign" / "scripts"
ACTS = (SCRIPTS / "battle_acts.gd").read_text(encoding="utf-8")
HOST = (SCRIPTS / "battle_diorama.gd").read_text(encoding="utf-8")


def _func(src: str, name: str) -> str:
    head = f"func {name}("
    body = src.split(head, 1)[1]
    return head + body.split("\nfunc ", 1)[0]


def _static(src: str, name: str) -> str:
    head = f"static func {name}("
    body = src.split(head, 1)[1]
    return head + body.split("\nfunc ", 1)[0].split("\nstatic func ", 1)[0]


class TestLever1TheTrayGrows:
    def test_the_host_owns_the_room_and_every_foot_control_follows_it(self):
        assert "var _day_room := 0.0" in HOST
        assert "return TRAY_H + _day_room" in _func(HOST, "tray_h")
        grow = _func(HOST, "set_day_room")
        assert "_day_room = maxf(px, 0.0)" in grow, "idempotent: a number, never a delta"
        assert "_tray.offset_top = -tray_h() / 2.0" in grow and "_tray.offset_bottom = tray_h() / 2.0" in grow
        assert "_tray_inner.custom_minimum_size = Vector2(TRAY_W, tray_h())" in grow
        assert "_place_the_foot()" in grow and "_fit_tray_to_viewport()" in grow
        foot = _func(HOST, "_place_the_foot")
        for node in ("_btn_close", "_btn_replay", "_skip_hint"):
            assert f"{node}.position.y = tray_h()" in foot
        assert "_nameplate.position.y = tray_h()" in grow
        assert "_seal.position.y" in grow

    def test_the_fit_rule_reads_the_grown_height(self):
        fit = _func(HOST, "_fit_tray_to_viewport")
        assert "(view.y - FIT_MARGIN_Y) / tray_h()" in fit
        assert "Vector2(TRAY_W / 2.0, tray_h() / 2.0)" in fit

    def test_nothing_of_the_foot_is_still_authored_against_the_bare_tray(self):
        for src in (HOST, ACTS):
            for line in src.splitlines():
                code = line.split("#")[0]
                if "TRAY_H" in code and ("- 46" in code or "- 40" in code or "SPEED_MID_UP" in code):
                    assert "tray_h()" in code, line
        assert "tray_h() - plate_size.y - 12.0" in HOST

    def test_a_table_asks_for_the_room_before_anything_stands_on_the_foot(self):
        dress = _func(ACTS, "dress")
        i_put, i_room, i_speed = (dress.index(m) for m in (
            "_put_the_chrome_back()", "host.set_day_room(DAY_ROOM if _day_has_panel() else 0.0)",
            "_build_the_speed()"))
        assert i_put < i_room < i_speed, "the room is asked after the chrome is put back and before the switch stands"
        has = _func(ACTS, "_day_has_panel")
        assert 'return _day_banner() != "" or bool(day.get("open", false))' in has
        assert "const DAY_ROOM := 110.0" in ACTS

    def test_the_panels_floor_is_the_tray_s_and_it_is_given_back_on_close(self):
        assert "func _day_floor() -> float:" in ACTS and "DAY_BOTTOM + (host._day_room" in ACTS
        build = _func(ACTS, "_build_the_day")
        assert "panel.size = Vector2(DAY_W, floor_px - top)" in build
        assert "DAY_BOTTOM - top" not in build
        close = _func(HOST, "_on_close_pressed")
        assert "set_day_room(0.0)" in close.split("\n", 3)[1] + close.split("\n", 3)[2]


class TestLever2ThreeLineCards:
    def test_the_card_has_a_third_line_at_the_caption_step_in_the_caption_ink(self):
        card = _func(ACTS, "_day_card_bb")
        assert 'var risk := str(chip.get("risk", ""))' in card
        assert 'var risk_on_face: bool = lit and _day_risk_lines and risk != ""' in card
        assert 'inner += "\\n" + Utils.bb_step(third, &"Caption")' in card
        third = card.split("var third: String", 1)[1].split("\n", 3)[0:3]
        assert "sub," in "".join(third), "the caption ink"
        head = card.split("var inner :=", 1)[1].split("\n", 1)[0]
        assert "bb_step" not in head, "the first line stays at the body's size"
        assert "[font_size" not in ACTS, "no BBCode font size: a smaller line takes Utils.bb_step"

    def test_where_the_face_has_no_third_line_the_hover_says_it(self):
        tip = _func(ACTS, "_day_chip_tip")
        assert "with_risk: bool = true" in tip
        # row PW (plain words): the same third line, headed "Expect:" on a day
        # served in everyday words and "It risks:" on a day as it was
        assert ('parts.append(("Expect: " if _day_is_plain() else "It risks: ") '
                '+ str(chip.get("risk", "")) + ".")') in tip
        card = _func(ACTS, "_day_card_bb")
        assert 'var tip := _day_chip_tip(chip, false, not lit and why != "", not risk_on_face)' in card

    def test_the_ladder_sheds_the_third_line_before_the_second(self):
        build = _func(ACTS, "_build_the_day")
        assert "var risk_lines: bool = cards" in build
        assert "_day_risk_lines = risk_lines and cards" in build
        over = build.split("if cards and c_box != null and c_box.get_content_width() > DAY_W + 1.0:", 1)[1][:160]
        assert "if risk_lines:" in over and over.index("risk_lines = false") < over.index("cards = false")
        rungs = build.split("elif risk_lines and cards:", 1)[1]
        assert rungs.index("risk_lines = false") < rungs.index("elif cards:")
        assert "var _day_risk_lines := false" in ACTS


class TestLever3TheExitsStakes:
    def test_a_full_width_row_above_the_buttons_then_the_wrap_then_the_chips(self):
        build = _func(ACTS, "_build_the_day")
        row = build.split("if exit_cards:\n\t\t\t\tvar e_w: float = e_box.get_content_width()", 1)[1][:900]
        i_row = row.index("exits_row = true")
        i_wrap = row.index("exits_wrapped = true")
        i_chip = row.index("exit_cards = false")
        assert i_row < i_wrap < i_chip
        assert "e_top_abs = btn_top - 4.0 - e_h" in build, "the row stands on the line above the buttons"
        assert "e_top_abs = floor_px - DAY_EXIT_FLOOR - e_h" in build, "beside the buttons, down to the tray's floor"
        assert "DAY_W if (exit_cards and exits_row) else DAY_CHIPS_W" in build

    def test_the_stakes_wrap_at_a_semicolon_only(self):
        wrap = _static(ACTS, "_wrap_does")
        assert 'does.split("; ")' in wrap and "if parts.size() < 2:" in wrap
        card = _func(ACTS, "_day_exit_card_bb")
        assert 'if _day_exits_wrapped and (lit or why == "") and does != "":' in card
        assert "third_line" in card and "var halves := _wrap_does(does)" in card

    def test_rows_are_measured_in_a_box_no_narrower_than_their_words(self):
        assert "const DAY_MEASURE_W := 4000.0" in ACTS
        build = _func(ACTS, "_build_the_day")
        assert "e_box.size.x = DAY_MEASURE_W" in build and "c_box.size.x = DAY_MEASURE_W" in build


class TestLever4FewerChips:
    def test_the_groups_show_the_chips_the_digits_reach_and_a_quiet_chip_holds_the_rest(self):
        groups = _func(ACTS, "_day_groups_text")
        assert "if _day_more_open or _day_digit_of.has(int(i)):" in groups
        assert "var more := _day_more_chip()" in groups
        more = _func(ACTS, "_day_more_chip")
        assert '"+%d more" % hidden.size()' in more and '"show fewer"' in more
        assert '", ".join(PackedStringArray(names))' in more, "the hover names the rest"
        hidden = _func(ACTS, "_day_hidden_groups")
        assert "if not _day_digit_of.has(int(i)):" in hidden

    def test_pressing_it_toggles_and_sends_no_word(self):
        chip = _func(ACTS, "_on_day_chip")
        head = chip.split("if _day_latched:", 1)[0]
        assert "str(meta) == DAY_MORE_KEY" in head
        assert "_day_more_open = not _day_more_open" in head and "return" in head
        assert 'const DAY_MORE_KEY := "daymore"' in ACTS

    def test_the_digits_are_untouched_and_the_state_resets_per_table(self):
        digits = _func(ACTS, "_day_digit_map")
        assert "DAY_DIGIT_GROUP_FROM" in digits and "next > DAY_DIGIT_GROUP_TO" in digits
        build = _func(ACTS, "_build_the_day")
        assert "_day_more_open = false" in build.split("var day := _the_day()", 1)[0]


class TestLever5LuckAgainstMargin:
    def test_the_luck_is_one_phrase_that_sets_it_against_what_told(self):
        luck = _func(ACTS, "_luck_line")
        assert 'var told := _what_told()' in luck
        assert '"%s; the dice added %s to the blow, the day\'s fortune %s to us"' in luck
        assert "int(roll.get(\"swing\", 0)) + 100 - DiceTray.AVERAGE_LANDS" in luck
        assert "_signed(int(roll.get(left_key, 0)))" in luck, "our side's own figure"
        # row PW (November 18, 2026): the head is a variable now — the line as it was for a payload that
        # is not plain, "luck today, as extra strength:" only where the payload says `plain`
        assert 'var luck_head := "the day\'s fortune in strength:"' in luck, "no what-told: the line as it was"
        assert "BattleActs.payload_is_plain(host._data)" in luck
        assert 'luck_head = "luck today, as extra strength:"' in luck
        assert 'return "%s  %s %s  ·  %s %s" % [luck_head,' in luck

    def test_what_told_is_the_cause_alone(self):
        told = _func(ACTS, "_what_told")
        assert 'line.begins_with("Decided") and line.contains(": ")' in told
        assert 'line.ends_with(".")' in told and "to_upper()" in told
        assert 'host._data.get("verdict_told", "")' in told


class TestLever6TheLegend:
    def test_the_legend_is_one_caption_line_in_the_marks_themselves(self):
        legend = _func(ACTS, "_day_legend_bb")
        assert "Utils.SWATCH, 10, DAY_PIP_ON" in legend and "Utils.SWATCH, 10, DAY_PIP_OFF" in legend, (
            "the squares are drawn, as the head's are: no font's missing glyph shows as a box")
        for words in ("each side's lead", "a point in hand", "a point spent", "keys 1-9 say the words",
                      "a card: its price, what it does, what it risks"):
            assert words in legend
        for glyph in "◆■□":
            assert glyph not in legend and glyph not in ACTS.split("const DAY_LEGEND_HOVER", 1)[1][:400]
        assert 'legend_box.name = "DayLegend"' in _func(ACTS, "_build_the_day")

    def test_it_is_shed_to_the_heads_hover_under_pressure_after_the_lift(self):
        build = _func(ACTS, "_build_the_day")
        # row PW: the legend is read through `_day_legend_hover()` (its plain
        # form on a plain day; this one as it was)
        assert "hover.append(_day_legend_hover())" in build
        assert "return DAY_LEGEND_HOVER_PLAIN if _day_is_plain() else DAY_LEGEND_HOVER" in _func(
            ACTS, "_day_legend_hover")
        assert "_day_legend_row = legend_row" in build
        ladder = build.split("elif legend_row and not lifted:", 1)[1]
        assert ladder.index("lifted = true") < ladder.index("legend_row = false") < ladder.index("rule_row = false")
        assert "keys 1 to 9 say the words" in ACTS.split("const DAY_LEGEND_HOVER", 1)[1][:300]


class TestTheWalkReadsEveryLever:
    def test_every_lever_has_its_claim_and_its_switch_off_case(self):
        walk = (ROOT / "tools" / "ba1_acts_walk.py").read_text(encoding="utf-8")
        cases = (ROOT / "tools" / "ba2_switch_off.py").read_text(encoding="utf-8")
        for claim in ("BA6-1", "BA6-2", "BA6-3", "BA6-4", "BA6-5", "BA6-6"):
            assert f"({claim})" in walk, claim
        for case in ("ba6_tray_room", "ba6_panel_floor", "ba6_risk_line", "ba6_exits_row", "ba6_exits_wrap",
                     "ba6_more_chip", "ba6_more_toggle", "ba6_legend", "ba6_luck"):
            assert f'("{case}"' in cases, case


class TestTheReviewsFixes:
    """The review of BA-6's client: each fix pinned at its source."""

    def test_the_survey_is_cropped_never_stretched(self):
        ground = ACTS.split("class Ground:", 1)[1].split("\n# ──", 1)[0]
        draw = ground.split("func _draw()", 1)[1]
        assert "draw_texture_rect_region(_tex, r, src)" in draw
        assert "draw_texture_rect(_tex, r, false)" not in draw, "a plate is never stretched to the sheet"
        assert "_tex.get_size()" in draw and "/ 2.0" in draw, "a centred source rect of the sheet's own aspect"
        assert "draw_set_transform" not in ground, "never a mirror"

    def test_the_held_type_leaves_the_fixed_display_steps_and_the_hint_alone(self):
        mk = _func(HOST, "_mk_label")
        assert "Utils.TEXT_SIZE_FIXED_STEPS" in mk and "else _tableau_theme" in mk
        assert "_skip_hint.theme = null" in HOST
        refit = _func(HOST, "_refit_chrome_type")
        assert "_chrome_labels" in refit and "TEXT_SIZE_FIXED_STEPS" in refit
        assert "_refit_chrome_type()" in _func(HOST, "show_diorama").split("_populate(", 1)[0]

    def test_more_relays_the_panel_and_a_new_table_resets_it(self):
        chip = _func(ACTS, "_on_day_chip").split("if _day_latched:", 1)[0]
        assert "_relay_the_day()" in chip
        relay = _func(ACTS, "_relay_the_day")
        assert "_relaying = true" in relay and "_build_the_day()" in relay
        build = _func(ACTS, "_build_the_day")
        assert "if not _relaying:\n\t\t_day_more_open = false" in build

    def test_a_verdict_with_no_cause_names_an_even_fight(self):
        told = _func(ACTS, "_what_told")
        assert '", in an even fight"' in told and '"An even fight"' in told

    def test_the_exits_flags_say_what_they_say(self):
        build = _func(ACTS, "_build_the_day")
        assert "_day_exits_row_tried = true" in build
        wide = build.split("_day_exits_wide = true", 1)[0]
        assert "exit_cards = false        # ...then the one-line chips" in wide.rsplit("\n\t\t\t\t", 1)[0] \
            or "exit_cards = false        # ...then the one-line chips" in build
