"""Session UI-6 (November 13, 2026) - the master-detail Generals screen.

Source pins for `scripts/marshal_management.gd`, `scripts/marshal_roster_row.gd` and
`scenes/marshal_management.tscn`. Folded (the default), the screen is a roster beside one
marshal: a head of three buttons over a real Button per marshal, a detail pane with a header,
an order bar of real Buttons pinned above the scroll, and a body of skills grid, ability chips,
the printed Reward line, status and one Character fold. On the page, none of it is drawn and
`_render_all_cards` prints the screen as it always did. Nothing here starts an engine.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GODOT = REPO / "godot-client" / "project-sovereign"
SRC = (GODOT / "scripts" / "marshal_management.gd").read_text(encoding="utf-8")
ROW = (GODOT / "scripts" / "marshal_roster_row.gd").read_text(encoding="utf-8")
SCENE = (GODOT / "scenes" / "marshal_management.tscn").read_text(encoding="utf-8")
MAIN = (GODOT / "scripts" / "main.gd").read_text(encoding="utf-8")


def _func(src: str, name: str) -> str:
    start = src.index("func " + name + "(")
    nxt = src.find("\nfunc ", start + 1)
    return src[start:nxt] if nxt != -1 else src[start:]


class TestTheScene:

    def test_the_named_nodes_survive(self):
        for node in ("PanelContainer", "VBoxContainer", "HeaderRow", "TitleLabel", "CloseButton",
                     "ScrollContainer", "ContentArea"):
            assert f'[node name="{node}"' in SCENE, node

    def test_a_split_holds_the_roster_and_the_detail(self):
        assert '[node name="Split" type="HSplitContainer" parent="PanelContainer/VBoxContainer"]' in SCENE
        assert "dragger_visibility = 1" in SCENE   # not draggable: the divider is hidden
        for node, kind in (("RosterColumn", "VBoxContainer"), ("RosterHead", "VBoxContainer"),
                           ("CommissionButton", "Button"), ("DoctrineButton", "Button"),
                           ("LaurelsButton", "Button"), ("RosterScroll", "ScrollContainer"),
                           ("RosterList", "VBoxContainer"), ("DetailPane", "VBoxContainer"),
                           ("DetailHeader", "HBoxContainer"), ("PortraitRect", "TextureRect"),
                           ("OrderBar", "HFlowContainer")):
            assert f'[node name="{node}" type="{kind}"' in SCENE, node

    def test_the_scroll_lives_under_the_detail_pane(self):
        assert 'name="ScrollContainer" type="ScrollContainer" parent="PanelContainer/VBoxContainer/Split/DetailPane"' in SCENE
        assert 'parent="PanelContainer/VBoxContainer/Split/DetailPane/ScrollContainer"' in SCENE
        assert '@onready var scroll_container = $PanelContainer/VBoxContainer/Split/DetailPane/ScrollContainer' in SRC
        assert '@onready var content_area = $PanelContainer/VBoxContainer/Split/DetailPane/ScrollContainer/ContentArea' in SRC

    def test_the_order_bar_is_pinned_above_the_scroll(self):
        assert SCENE.index('name="OrderBar"') < SCENE.index('name="ScrollContainer"')

    def test_the_commission_button_is_the_gilt_primary(self):
        block = SCENE[SCENE.index('name="CommissionButton"'):]
        block = block[:block.index("\n\n")]
        assert 'theme_type_variation = &"PrimaryButton"' in block
        assert 'text = "Commission a Marshal"' in block

    def test_the_grip_and_the_margins_hold(self):
        assert 'ResizeGrip.attach_centered($PanelContainer, "generals")' in SRC
        assert "corner_ornaments" not in SCENE and "Filigree" not in SCENE


class TestTheSignalsAndTheRoute:

    def test_the_old_signals_stay_and_one_is_new(self):
        for sig in ("signal closed", "signal reward_requested(card: Dictionary)",
                    "signal commission_requested(candidate_name: String)",
                    "signal order_command(command: String)", "signal audience_requested",
                    "signal locate_requested(marshal_name: String)"):
            assert sig in SRC, sig

    def test_the_kit_loads_by_path(self):
        assert 'const MarshalKit := preload("res://scripts/marshal_state.gd")' in SRC
        assert 'const RosterRow := preload("res://scripts/marshal_roster_row.gd")' in SRC
        assert 'preload("res://scripts/marshal_state.gd")' in ROW

    def test_the_census_regex_still_finds_only_the_three_chip_verbs(self):
        assert set(re.findall(r'"order:(\w+):"', SRC)) == {"fortify", "unfortify", "drill"}

    def test_the_first_order_emit_is_still_the_chip_handlers(self):
        """test_uxr3_s12_part2 reads the FIRST `order_command.emit(`: the new bar's emit stands after it."""
        first = SRC.index("order_command.emit(")
        assert first < SRC.index("func _on_order_pressed(")
        assert "Utils.order_taken = false" in SRC[first - 220:first]
        assert "Utils.mark_chip_sent(content_area, meta_str)" in SRC[first:first + 220]


class TestTheOrderBar:

    def test_it_is_built_from_the_kit_specs(self):
        body = _func(SRC, "_fill_order_bar")
        assert "MarshalKit.order_specs(MarshalKit.from_overview(m))" in body
        assert 'str(spec["verb"]) == "cancel" and not standing' in body
        assert "order_bar.add_child(_order_button(mname, spec))" in body

    def test_a_captured_marshal_has_no_bar(self):
        body = _func(SRC, "_fill_order_bar")
        assert 'bool(m.get("captured", false))' in body and "order_bar.visible = false" in body

    def test_a_locked_order_is_a_disabled_button_whose_reason_is_its_hover(self):
        body = _func(SRC, "_order_button")
        assert 'if bool(spec["locked"]):' in body
        assert "btn.disabled = true" in body
        assert 'var why := str(spec["reason"])' in body       # a String, never `a or b`
        assert "btn.tooltip_text = why" in body
        assert "MarshalKit.price_text(int(spec[\"price\"]))" in body

    def test_a_lit_order_takes_the_same_road_as_typing(self):
        body = _func(SRC, "_order_button")
        assert "btn.pressed.connect(_on_order_pressed.bind(btn, mname, str(spec[\"verb\"])))" in body
        assert 'return mname + ", " + verb' in _func(SRC, "_order_sentence")
        pressed = _func(SRC, "_on_order_pressed")
        i = pressed.index("order_command.emit(_order_sentence(mname, verb))")
        assert "Utils.order_taken = false" in pressed[:i]
        assert "if Utils.order_taken" in pressed[i:] and 'btn.text = "Sent"' in pressed[i:]

    def test_on_the_map_emits_the_new_signal(self):
        body = _func(SRC, "_fill_order_bar")
        assert 'locate.pressed.connect(_on_locate_pressed.bind(mname))' in body
        assert "locate_requested.emit(mname)" in _func(SRC, "_on_locate_pressed")

    def test_no_new_order_literals_for_the_census(self):
        for fn in ("_fill_order_bar", "_order_button", "_order_sentence", "_on_order_pressed"):
            assert '"order:' not in _func(SRC, fn), fn


class TestTheRosterAndTheKeys:

    def test_the_head_has_three_buttons(self):
        body = _func(SRC, "_build_master_detail_chrome")
        for kind in ("commission", "doctrine", "laurels"):
            assert f'_on_head_button.bind("{kind}")' in body
        head = _func(SRC, "_on_head_button")
        assert "_commission_view = not _commission_view" in head
        # each switches the detail view, rendered by the existing builders
        assert "_render_commission_view()" in _func(SRC, "_render_master_detail")
        assert "_render_doctrine()" in _func(SRC, "_doctrine_view")
        assert "_render_glory_ladder()" in _func(SRC, "_laurels_view")

    def test_urgent_first_then_the_emperor_then_the_rest(self):
        body = _func(SRC, "_display_order")
        assert body.index('bool(um.get("captured", false)) or bool(um.get("seeks_audience", false))') \
            < body.index("out.append(apex)") < body.index("if i != apex and not (i in out):")

    def test_the_dot_marks_captured_petition_and_grievance(self):
        body = _func(SRC, "_is_urgent")
        for field in ('"captured"', '"seeks_audience"', '"jealous_of"'):
            assert field in body, field

    def test_a_row_is_a_button_with_a_portrait_a_badge_and_a_dot(self):
        assert "extends Button" in ROW and "class_name MarshalRosterRow" in ROW
        assert "TextureRect.new()" in ROW and "MarshalKit.portrait_path(key)" in ROW
        assert "MarshalKit.monogram(key)" in ROW
        assert "signal chosen(marshal_name: String)" in ROW
        assert "func _badge(" in ROW and "func _dot(" in ROW
        # the lead's frame reading (Nov 13): ScreenTitle cut "BERNADO..." and
        # overran the row — the HUD's title step, and the badge beside the place
        assert '&"HudTitle"' in ROW and '&"ScreenTitle"' not in ROW
        assert "line2.add_child(_badge(status, tone))" in ROW
        assert "const PORTRAIT_H := 44" in ROW
        # the narrow row is the portrait alone; the name is its tooltip
        setup = _func(ROW, "setup")
        assert "if narrow:\n\t\ttooltip_text = shown" in setup
        assert "if not narrow:" in setup

    def test_the_roster_reads_the_status_from_the_kit(self):
        body = _func(SRC, "_build_roster")
        assert "MarshalKit.status_of(MarshalKit.from_overview(m))" in body
        assert "row.setup(" in body and "row.chosen.connect(select_marshal)" in body

    def test_the_narrow_roster_is_portraits_alone(self):
        body = _func(SRC, "_is_narrow")
        assert "Utils.compact_view()" in body and "NARROW_BELOW" in body and "side_desk_docked" in body
        assert "const NARROW_BELOW := 760.0" in SRC

    def test_the_keys_belong_to_the_roster_folded_only(self):
        inp = _func(SRC, "_input")
        assert "if _master_detail() and _roster_key(event, _focused):" in inp
        # the page's old digit scroll is still there, after the roster's hand-off
        assert inp.index("_roster_key(") < inp.index("scroll_target = index * 520")
        # a focused text field still gets its digits first
        assert inp.index("is LineEdit") < inp.index("_roster_key(")
        key = _func(SRC, "_roster_key")
        for token in ("KEY_1", "KEY_9", "KEY_UP", "KEY_DOWN", "KEY_ENTER", "KEY_KP_ENTER",
                      "select_marshal(str(_roster_names[slot]))"):
            assert token in key, token
        assert "ctrl_pressed or event.alt_pressed or event.meta_pressed" in key
        assert "_focus_first_order()" in key

    def test_enter_on_a_focused_button_presses_it(self):
        key = _func(SRC, "_roster_key")
        assert "if focused is Button and not (focused is RosterRow):" in key

    def test_enter_focuses_the_first_enabled_order(self):
        body = _func(SRC, "_focus_first_order")
        assert "not c.disabled" in body and "grab_focus()" in body

    def test_the_selection_persists_and_select_marshal_is_public(self):
        assert "var _selected_name := \"\"" in SRC
        body = _func(SRC, "select_marshal")
        assert "_selected_name = marshal_name" in body
        assert "_commission_view = false" in body and 'if not _master_detail() or not visible or cached_data.size() == 0:' in body
        # refresh and the Side Desk's re-read go through the one renderer, which keeps the name
        assert "_selected_name = \"\"" not in _func(SRC, "close_view")
        resolve = _func(SRC, "_resolve_selection")
        assert "not (_selected_name in _roster_names)" in resolve
        assert "_render_current_view()" in _func(SRC, "_on_data_received")
        assert "_selected_name" not in _func(SRC, "refresh_pinned")


class TestTheBody:

    def test_the_skills_are_a_three_by_two_grid_with_hover_notes(self):
        body = _func(SRC, "_skills_grid")
        assert "[table=3]" in body
        assert "Utils.bb_hint(head, tip)" in body and "Utils.bb_hint(meter, tip)" in body
        assert "Utils.bb_glyph(skill_name, 16, Utils.COLOR_GOLD)" in body
        assert "SKILL_GLYPHS" in body

    def test_the_abilities_are_chips_with_hover_prose(self):
        body = _func(SRC, "_ability_chips")
        for chip in ('"The Intendance"', '"The Rally"', '"The Steward"'):
            assert chip in body, chip
        assert body.count("Utils.bb_hint(Utils.bb_tag(") >= 4
        for note in ("ab_effect", "admin_note", "rally_note", "steward_note"):
            assert note in body, note

    def test_the_reward_line_is_still_printed(self):
        body = _func(SRC, "_reward_lines")
        for words in ("held prisoner", "his expectation is met", "victories raise his expectation",
                      "The Empire is his estate."):
            assert words in body, words
        assert "elif shortfall > 0 or pension > 0:" in body
        assert '_button_chip("reward:" + str(index)' in body
        assert '_button_chip("audience:open"' in body
        # printed, not folded: no hover wraps the reasons
        assert "Utils.bb_hint(" not in body and "Utils.bb_note(" not in body
        assert "_reward_lines(m, index)" in _func(SRC, "_detail_body")

    def test_one_character_fold_holds_the_lore(self):
        body = _func(SRC, "_character_fold")
        assert "Utils.bb_note(" in body
        for key in ("biography", "personality_description", "unit_type_description"):
            assert f'"{key}"' in body, key
        assert _func(SRC, "_detail_body").count("_character_fold(m)") == 1

    def test_the_body_order(self):
        body = _func(SRC, "_detail_body")
        order = ["_skills_grid(m)", "_ability_chips(m)", "_reward_lines(m, index)",
                 "_grievance_lines(m)", "_status_lines(m)", "_character_fold(m)"]
        assert [body.index(t) for t in order] == sorted(body.index(t) for t in order)

    def test_the_detail_carries_no_duplicate_orders(self):
        for fn in ("_detail_body", "_skills_grid", "_ability_chips", "_status_lines", "_character_fold"):
            assert "order_prices" not in _func(SRC, fn) and "Orders" not in _func(SRC, fn), fn

    def test_the_header_is_a_portrait_tags_status_and_a_figure_strip(self):
        body = _func(SRC, "_fill_header")
        assert "MarshalKit.status_of(view)" in body and "MarshalKit.portrait_path(mname)" in body
        assert "_figure_strip.set_tiles(_figure_tiles(m))" in body
        tiles = _func(SRC, "_figure_tiles")
        for caption in ('"Strength"', '"Morale"', '"Range"', '"Glory"', '"Record"'):
            assert caption in tiles, caption
        assert '"glyph": "trust"' in tiles


class TestPageModeIsUntouched:

    def test_the_card_builders_are_not_edited(self):
        cards = _func(SRC, "_render_all_cards")
        assert "_render_card(" in cards and "_render_doctrine()" in cards and "_render_glory_ladder()" in cards
        assert cards.count(", true)") == 2
        card = _func(SRC, "_render_card")
        assert card.count("Utils.CARD_CLOSE") == 1 and "if not opened:" in card
        assert SRC.count("_skills_block(m)") == 2
        assert "# CN-4: Drill is offered only where the drill would begin" in SRC
        assert "# ═══════ BIOGRAPHY ═══════" in SRC and "# ═══════ ABILITY (only shown if active/wired) ═══════" in SRC

    def test_the_render_dispatch_only_gained_a_guard(self):
        body = _func(SRC, "_render_current_view")
        assert body.index("_apply_layout_mode()") < body.index("if _master_detail():")
        assert "elif _commission_view:" in body and "_render_all_cards()" in body

    def test_the_page_hides_the_roster_the_header_and_the_bar(self):
        body = _func(SRC, "_apply_layout_mode")
        assert "roster_column.visible = md" in body
        assert "detail_header.visible = false" in body and "order_bar.visible = false" in body
        assert "func _master_detail() -> bool:\n\t\"\"\"The Folded layout (a switch in Settings restores the page).\"\"\"\n\treturn Utils.explanations_folded()" in SRC

    def test_the_fold_is_the_only_gate(self):
        for fn in ("_roster_key", "_render_master_detail", "_fill_order_bar", "_build_roster"):
            assert "UiSettings" not in _func(SRC, fn)


class TestTheHouseRules:

    def test_no_or_picks_a_value(self):
        for src in (SRC, ROW):
            assert not re.search(r"str\(\s*\w[\w.\[\]\"]* or ", src)
            assert not re.search(r"\.get\([^)]*\)\s+or\s+\w+\)", src)

    def test_no_font_size_tags_and_no_new_hex_literals_in_the_new_code(self):
        new = SRC[SRC.index("# SESSION UI-6"):] + ROW
        assert "[font_size" not in new
        assert not re.search(r'["\']#?[0-9a-fA-F]{6}["\']', new)

    def test_numbers_are_ints(self):
        new = SRC[SRC.index("# SESSION UI-6"):]
        assert "str(m.get(\"strength\"" not in new   # always through int()
        assert "Utils.format_number(int(m.get(\"strength\", 0)))" in new


class TestTheRelationshipsNeverDangle:
    """UI6-X53 (the final readers' F10, fixed after the reading): the detail's
    relationships were a table under a "Relationships:" heading — one box the
    pane's fold cut, the heading left alone at the foot ("a dangling
    'Relationships:' with nothing under it"). They are one wrapped paragraph,
    as the card prints them On the page."""

    def test_the_detail_prints_them_inline(self):
        status = _func(SRC, "_status_lines")
        assert '"  Relationships: " + ", ".join(rel_parts) + "\\n"' in status
        assert "[table=2]" not in status
