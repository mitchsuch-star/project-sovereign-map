"""Row IC "Independent Command", the desk (November 19, 2026) — IC-2: the turn's end.

End Turn stopped once for seven kinds of reason and said them in ONE joined sentence printed into the log,
with no way to act on it; and a province taken by a march into empty ground ("Carniola … walked back into
by Austria on turn 5 because nothing stood there") was never said to be in danger beforehand. Pinned here:
the list that stands above the command line while End Turn waits (the desk's own rows, each a door that
sends nothing); the two new reasons to stop once (a province in danger, named once per province; a man who
may attack without orders); the map's standing mark; and the report's word on each loss — "You were warned
before the turn ended." or "The enemy who took it was out of your sight."
"""

from __future__ import annotations

import contextlib
import io
import json
import pathlib
import re

import pytest

from backend.game_logic import threats, today
from backend.game_logic import while_you_waited as WYW

REPO = pathlib.Path(__file__).resolve().parents[1]
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
CLIENT = REPO / "godot-client" / "project-sovereign"
SCRIPTS = CLIENT / "scripts"
SCENES = CLIENT / "scenes"

# (+ "directive": row IC's second commit — a row that opens the LIST of an order to several corps)
DOOR_KINDS = ("marshal", "region", "day", "envoys", "ledger", "congress", "generals", "idle", "war", "court",
              "directive")


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _src(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def _func(source: str, name: str) -> str:
    match = re.search(rf"^(?:static )?func {re.escape(name)}\(.*?(?=^\S|\Z)", source, re.S | re.M)
    assert match, f"no func {name}"
    return match.group(0)


@pytest.fixture(scope="module")
def _boot():
    from backend.models.world_state import WorldState
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO))


@pytest.fixture
def world(_boot):
    from backend.models.world_state import WorldState
    return WorldState.from_dict(json.loads(json.dumps(_boot.to_dict(), default=str)))


def _open_province_beside(world, foe_name: str = "Mack"):
    foe = world.marshals[foe_name]
    for name in world.get_region(foe.location).adjacent_regions:
        region = world.get_region(name)
        if region is not None and region.controller == world.player_nation:
            for m in world.get_marshals_in_region(name):
                m.location = "Paris"
            region.garrison_strength = 0
            region.garrison_detachment = False
            region.buildings = [b for b in region.buildings if b["type"] != "fortification"]
            return region
    raise AssertionError(f"no province of ours stands beside {foe_name}")


def _lose(world, before, region_name: str, events):
    """`region_name` passes to Austria, and the digest reads it."""
    world.get_region(region_name).controller = "Austria"
    told = WYW.digest(world, before, None, events)
    return next(row for row in told["lost"] if row["region"] == region_name)


# ═════════════════════════════════════════════════════════════════════════════
# 1. The report says whether a loss was foreseen
# ═════════════════════════════════════════════════════════════════════════════

class TestALossSaysIfItWasForeseen:
    def test_the_snapshot_keeps_what_the_player_had_been_told(self, world):
        region = _open_province_beside(world, "Mack")
        before = WYW.snapshot(world)
        assert before["danger"] == sorted(r["region"] for r in threats.in_danger(world, world.player_nation))
        assert region.name in before["danger"]
        # every FOREIGN corps in sight — at war with us or not (the review, IC-R2)
        from backend.game_logic import intel_surfaces
        assert before["seen"] == sorted(m.name for m in world.marshals.values()
                                        if intel_surfaces.in_sight(world, world.player_nation, m))
        assert "Mack" in before["seen"]
        assert set(before["seen"]) >= {m.name for m in world.get_visible_enemies(world.player_nation)}

    def test_a_court_at_peace_in_plain_sight_was_not_out_of_sight(self, world):
        """The review (IC-R2): a corps of a court AT PEACE stood in a province we could see,
        declared war in the night and walked in. He was no enemy when End Turn was pressed —
        and he was not "out of your sight" either: the row says neither."""
        from backend.models.intel import RegionIntel
        prussian = next(m for m in world.marshals.values() if m.nation == "Prussia" and m.strength > 0)
        assert not world.is_at_war(world.player_nation, "Prussia")
        intel = world.intel.get(prussian.location)
        if intel is None:
            intel = world.intel[prussian.location] = RegionIntel(prussian.location)
        intel.visibility = "full"
        before = WYW.snapshot(world)
        assert prussian.name in before["seen"]
        assert prussian.name not in [m.name for m in world.get_visible_enemies(world.player_nation)]
        assert WYW._foreseen(before, "Lorraine", {"how": "walked_in", "taker": prussian.name}) == ""
        intel.visibility = "unknown"
        hidden = WYW.snapshot(world)
        assert WYW._foreseen(hidden, "Lorraine", {"how": "walked_in", "taker": prussian.name}) == "unseen"

    def test_a_province_the_desk_named_was_warned(self, world):
        region = _open_province_beside(world, "Mack")
        before = WYW.snapshot(world)
        row = _lose(world, before, region.name,
                    [{"type": "conquest", "region": region.name, "marshal": "Mack"}])
        assert row["foreseen"] == "warned"
        assert row["line"].endswith("nobody was holding it. You were warned before the turn ended.")
        assert "taker" not in row                       # the taker's roster key never rides the reply

    def test_a_corps_that_was_in_no_province_we_could_see(self, world):
        before = WYW.snapshot(world)
        assert "Kutuzov" not in before["seen"] and "Burgundy" not in before["danger"]
        row = _lose(world, before, "Burgundy",
                    [{"type": "conquest", "region": "Burgundy", "marshal": "Kutuzov"}])
        assert row["foreseen"] == "unseen"
        assert row["line"].endswith("The enemy who took it was out of your sight.")

    def test_a_province_held_and_threatened_in_plain_sight_says_neither(self, world):
        mack = world.marshals["Mack"]
        held = next(name for name in world.get_region(mack.location).adjacent_regions
                    if world.get_region(name).controller == world.player_nation
                    and any(m.nation == world.player_nation for m in world.get_marshals_in_region(name)))
        before = WYW.snapshot(world)
        assert held not in before["danger"] and "Mack" in before["seen"]
        defender = next(m.name for m in world.get_marshals_in_region(held) if m.nation == world.player_nation)
        row = _lose(world, before, held, [{
            "type": "battle", "region_name": held, "victor": "Mack",
            "attacker": {"name": "Mack"}, "defender": {"name": defender},
            "attacker_nation": "Austria", "defender_nation": "France"}])
        assert row["how"] == "battle" and row["foreseen"] == ""
        assert "warned" not in row["line"] and "out of your sight" not in row["line"]

    def test_a_treaty_s_hand_over_is_no_feat_of_arms(self):
        before = {"danger": ["Savoy"], "seen": []}
        assert WYW._foreseen(before, "Savoy", {"how": "treaty", "taker": ""}) == ""
        assert WYW._foreseen(before, "Savoy", {"how": "", "taker": ""}) == ""
        assert WYW._foreseen(before, "Savoy", {"how": "walked_in", "taker": "Mack"}) == "warned"
        assert WYW._foreseen(before, "Lorraine", {"how": "siege", "taker": "Mack"}) == "unseen"
        assert WYW._foreseen(before, "Lorraine", {"how": "empty", "taker": ""}) == ""      # nobody to name
        assert WYW._foreseen({"danger": [], "seen": ["Mack"]}, "Lorraine",
                             {"how": "stormed", "taker": "Mack"}) == ""                   # he was in sight

    def test_an_older_snapshot_says_nothing(self, world):
        region = _open_province_beside(world, "Mack")
        before = WYW.snapshot(world)
        before.pop("danger")
        before.pop("seen")
        row = _lose(world, before, region.name,
                    [{"type": "conquest", "region": region.name, "marshal": "Mack"}])
        assert row["foreseen"] == ""
        assert row["line"].endswith("nobody was holding it.")

    def test_the_seam_down_is_the_report_as_it_was(self, world, monkeypatch):
        region = _open_province_beside(world, "Mack")
        monkeypatch.setattr(WYW, "a_loss_says_if_it_was_foreseen", lambda: False)
        before = WYW.snapshot(world)
        assert "danger" not in before and "seen" not in before
        row = _lose(world, before, region.name,
                    [{"type": "conquest", "region": region.name, "marshal": "Mack"}])
        assert row["line"].endswith("nobody was holding it.")

    def test_only_our_own_losses_are_judged(self, world):
        """An ally's province carries no `foreseen`: the desk warns of ours alone."""
        before = WYW.snapshot(world)
        ally = next(name for name, r in sorted(world.regions.items()) if r.controller == "Bavaria")
        world.get_region(ally).controller = "Austria"
        told = WYW.digest(world, before, None, [{"type": "conquest", "region": ally, "marshal": "Mack"}])
        row = next(r for r in told["friends_lost"] if r["region"] == ally)
        assert "foreseen" not in row


# ═════════════════════════════════════════════════════════════════════════════
# 2. The gate in the client: two more reasons, each said once
# ═════════════════════════════════════════════════════════════════════════════

class TestTheGate:
    def test_the_new_reasons_stand_after_the_army_s_and_before_the_day_s(self):
        gate = _func(_src(SCRIPTS / "main.gd"), "_execute_end_turn")
        army = gate.index("if _army_warning_stands():")
        new = gate.index("if _ic_danger_warning_stands() or _ic_strike_warning_stands():")
        day = gate.index("if _day_warning_stands():")
        assert army < new < day

    def test_the_log_s_warning_gains_their_sentences_and_nothing_else_changes(self):
        said = _func(_src(SCRIPTS / "main.gd"), "_show_lapse_confirmation")
        assert said.index("for ic_said in _ic_gate_sentences():") < said.index('var msg := " ".join(parts)')
        assert said.rstrip().endswith("_ic_show_turn_end_list()   # row IC: the same stop, as a list above the line")
        # the sentences row PW, BA and UI-5 wrote stand word for word
        assert "that will lapse if you end the turn now." in said
        assert "to end the turn anyway.[/color]" in said
        assert 'add_output("[color=#" + Utils.COLOR_WARNING + "]⚠ %s[/color]" % msg)' in said

    def test_a_province_is_named_once_and_a_striker_once_a_turn(self):
        main = _src(SCRIPTS / "main.gd")
        sentences = _func(main, "_ic_gate_sentences")
        assert "_ic_danger_warned[region_name] = true" in sentences
        assert '_ic_strike_warned[str(r.get("id", ""))] = true' in sentences
        send = _func(main, "_send_end_turn")
        assert "_ic_strike_warned.clear()" in send
        assert "_ic_danger_warned" not in send          # a standing danger does not stop every turn
        take = _func(main, "_ic_take_desk")
        assert "_ic_danger_warned.erase(region_name)" in take     # it leaves danger: it may be named again
        fresh = _func(main, "_ic_new_danger")
        assert "not _ic_danger_warned.has(" in fresh

    def test_a_new_board_forgets_every_latch(self):
        main = _src(SCRIPTS / "main.gd")
        forget = _func(main, "_ic_forget_the_board")
        for line in ("_ic_danger_warned.clear()", "_ic_strike_warned.clear()", "_ic_first_line_said = false",
                     "map_area.set_danger_regions([])"):
            assert line in forget, line
        assert "_ic_forget_the_board()" in _func(main, "_reset_frontend_state_for_world_swap")


# ═════════════════════════════════════════════════════════════════════════════
# 3. The list above the line, and the doors
# ═════════════════════════════════════════════════════════════════════════════

class TestTheListAndTheDoors:
    def test_the_list_is_the_desk_s_rows_that_bite_or_waste(self):
        main = _src(SCRIPTS / "main.gd")
        show = _func(main, "_ic_show_turn_end_list")
        assert 'if int(r.get("tier", 3)) <= 2:' in show
        stand = _func(main, "_ic_stand_the_list")
        assert "_turn_end_list.show_rows(_ic_list_rows, closing, _ic_list_cap)" in stand
        # The third blind reading ("I am told to decide, but I have no actions left"): with no
        # action left the one remedy in hand is to take the last order back — said only while
        # the server offers it.
        assert 'if int(actions_remaining) <= 0 and bool(_take_back_offer.get("available", false)):' in stand
        assert "closing = IC_LIST_NO_ACTIONS + closing" in stand
        assert ('const IC_LIST_NO_ACTIONS := "No actions are left — Take back (Ctrl+Z) undoes your last order. "'
                in main)
        assert "KEY_Z" in main and "_pw3_take_back" in main          # the key the sentence names is the game's
        # "Still to decide": the card's own words — four readers in six asked whether the card and
        # the list were one list or two
        listing = _src(SCRIPTS / "turn_end_list.gd")
        assert '"Still to decide before the turn ends — %s%s. Press one to go to it."' in listing
        assert "end_turn_button.focus_neighbor_top = end_turn_button.get_path_to(last)" in stand   # the keyboard reaches it
        assert today.TIER_BITES == 1 and today.TIER_WASTES == 2 and today.TIER_GROWS == 3

    def test_the_list_never_stands_taller_than_the_log(self):
        """It stands over the log, never over the marshals above it: the rows that do not fit
        are counted on its last line."""
        main = _src(SCRIPTS / "main.gd")
        room = _func(main, "_ic_list_room")
        assert "output_scroll.get_global_rect().position.y" in room
        place = _func(main, "_ic_place_turn_end_list")
        assert "want.y > _ic_list_room() + 2.0 and _ic_list_cap > IC_LIST_MIN_ROWS" in place
        assert "_ic_list_cap -= 1" in place
        # the review: a wrapped row measures true only a frame after it is built — the
        # "one row fewer" reckoning waits for it (it fell to its floor in the frame it stood)
        assert "var measured: bool = Engine.get_process_frames() > _ic_list_stood_frame + 1" in place
        assert "if measured and want.y" in place
        assert "_ic_list_stood_frame = Engine.get_process_frames()" in _func(main, "_ic_stand_the_list")
        assert "const IC_LIST_MIN_ROWS := 1" in main
        listing = _src(SCRIPTS / "turn_end_list.gd")
        # the words the player can find on the screen: the card's own head
        assert "…and %d more on the TO DECIDE card. " in listing
        assert 'more on the desk above. "' not in listing

    def test_the_list_never_covers_the_line(self):
        """Its foot stands just above the command line — always (the review: clamped under the
        top bar, a tall list ran down over the line and End Turn)."""
        place = _func(_src(SCRIPTS / "main.gd"), "_ic_place_turn_end_list")
        assert "var at := Vector2(anchor.position.x, anchor.position.y - 4.0 - tall)" in place
        assert "maxf(anchor.position.y" not in place

    def test_the_list_covers_the_log_while_it_stands(self):
        """Lever L6 (both blind readings: the log's last reply showed above the list, cut off
        mid-line, and was read as one more matter): while the log is on show the panel covers its
        WHOLE room, its rows at the foot beside the line; on the slim bar it is as tall as its rows."""
        place = _func(_src(SCRIPTS / "main.gd"), "_ic_place_turn_end_list")
        assert "if output_scroll != null and output_scroll.is_visible_in_tree():" in place
        assert "tall = maxf(want.y, _ic_list_room())" in place
        assert "var box := Vector2(want.x, tall)" in place
        listing = _src(SCRIPTS / "turn_end_list.gd")
        # in its middle, not at its foot ("a big empty gap at the top" — the third reading)
        assert "_box.alignment = BoxContainer.ALIGNMENT_CENTER" in listing

    def test_the_mark_is_explained_where_it_is_worn(self):
        """Lever L2 of the blind reading (all three readers: "the ! is not explained")."""
        listing = _src(SCRIPTS / "turn_end_list.gd")
        assert 'const LEGEND := " (! can cost you when the turn ends)"' in listing
        assert "LEGEND if any_bites else" in listing
        card = _src(SCRIPTS / "desk_lines.gd")
        assert 'const LEGEND := "    ! can cost you when the turn ends"' in card
        assert "_legend.visible = any_bites" in card

    def test_neither_new_surface_is_a_row_of_the_command_window(self):
        """The window's own rows, heights and floors are as they were: both stand over it
        (three more lines inside the 32:9 column pushed its header under the top bar)."""
        build = _func(_src(SCRIPTS / "main.gd"), "_ic_build_desk")
        assert "add_child(_desk_card)" in build and "add_child(_turn_end_list)" in build
        assert "layout" not in build
        place = _func(_src(SCRIPTS / "main.gd"), "_ic_place_turn_end_list")
        assert "command_input.get_parent() as Control" in place and "anchor.position.y - 4.0 - tall" in place

    def test_the_list_stands_exactly_while_the_gate_waits(self):
        process = _func(_src(SCRIPTS / "main.gd"), "_process")
        assert "if not _awaiting_end_turn_confirmation" in process and "_turn_end_list.hide_list()" in process
        assert "set_process(false)" in process

    def test_a_door_sends_nothing(self):
        main = _src(SCRIPTS / "main.gd")
        for name in ("_ic_open_door", "_ic_go_to_marshal", "_ic_go_to_region"):
            body = _func(main, name)
            code = "\n".join(line for line in body.split("\n") if not line.strip().startswith("#"))
            code = code.split('"""')[0] + code.split('"""')[-1]      # the docstring may say "sends"
            for forbidden in ("send_command", "_send_", "api_client", "_pw_send", "_execute_command"):
                assert forbidden not in code, (name, forbidden)
        door = _func(main, "_ic_open_door")
        for kind in DOOR_KINDS:
            assert f'"{kind}":' in door or f'"{kind}", ' in door, kind
        # RE-SEATED by the review: a door does NOT end End Turn's wait ("armed and visible is
        # one state" — `_on_envoy_clicked`'s rule). A wait ended here let the next End Turn
        # straight through, every reason already named, the other matters never seen again.
        code = "\n".join(line for line in door.split("\n") if not line.strip().startswith("#"))
        code = code.split('"""')[0] + code.split('"""')[-1]
        assert "_awaiting_end_turn_confirmation" not in code
        assert "_set_open_envoys_prompt_visible" not in code
        assert "command_input.grab_focus()" in door                  # … and hands the keyboard back to the line
        assert "_resume_editing()" in door                           # focus is not editing (CC-X10)

    def test_the_province_door_is_the_panel_s_one_door(self):
        """S14G-X66: the province panel has ONE door. The desk's row goes through it
        (`by_door`: no click was made, so no click gesture is read and an open panel is not
        toggled shut) after a notice's own "Show on map"."""
        main = _src(SCRIPTS / "main.gd")
        go = _func(main, "_ic_go_to_region")
        assert go.index("_on_show_on_map_requested(region_name)") < go.index("_on_map_region_clicked(region_name, true)")
        assert ".show_region(" not in go and "close_all_screens" not in go
        click = _func(main, "_on_map_region_clicked")
        assert "func _on_map_region_clicked(region_name: String, by_door: bool = false):" in click
        gestures = click[click.index("if not by_door:"):click.index("_end_reply()")]
        for gesture in ("_click_groups_a_marshal()", "_group_click(region_name)", "_order_click(region_name",
                        "_click_writes_a_name(region_name)", "_click_selects_a_marshal()",
                        "region_panel.close_panel()"):
            assert gesture in gestures, gesture
        assert sum(1 for line in main.split("\n")
                   if ".show_region(" in line and not line.strip().startswith(("#", "func "))) == 1

    def test_every_door_the_backend_names_has_a_road(self, world):
        door = _func(_src(SCRIPTS / "main.gd"), "_ic_open_door")
        kinds = {row["door"]["kind"] for row in today.decide(world)}
        kinds |= {today.peace(world)["door"]["kind"], today.war(world)["door"]["kind"]}
        assert kinds <= set(DOOR_KINDS)
        for kind in kinds:
            assert f'"{kind}"' in door, kind

    def test_the_rows_are_buttons_the_keyboard_reaches(self):
        for script in ("desk_lines.gd", "turn_end_list.gd"):
            source = _src(SCRIPTS / script)
            assert "b.focus_mode = Control.FOCUS_ALL" in source, script
            assert "signal door_pressed(door: Dictionary, row_id: String)" in source, script
            for forbidden in ("api_client", "HTTPRequest", "send_command"):
                assert forbidden not in source, (script, forbidden)       # a control that only signals
        lines = _src(SCRIPTS / "desk_lines.gd")
        assert "key.keycode == KEY_DELETE" in lines                      # the set-aside has a key
        assert "_aside.clear()" in _func(lines, "set_desk")              # … and lasts the turn only

    def test_the_card_dodges_the_window_and_the_names_dodge_the_card(self):
        main = _src(SCRIPTS / "main.gd")
        fit = _func(main, "_ic_fit_card")
        assert "if desk_rect.intersects(Rect2(at, want)):" in fit
        assert "not _hud_hidden and not _campaign_over" in fit
        assert "bottom_left_ui.item_rect_changed.connect(_ic_queue_fit_card)" in _func(main, "_ic_build_desk")
        avoid = _func(main, "_push_map_label_avoid_rects")
        assert "var desk_card := _ic_desk_card_rect()" in avoid
        mode = _func(main, "_ic_apply_desk_mode")
        assert '_desk_lines.set_mode("line")' in mode and '_desk_lines.set_mode("full")' in mode


# ═════════════════════════════════════════════════════════════════════════════
# 4. The map's mark
# ═════════════════════════════════════════════════════════════════════════════

class TestTheMapsMark:
    def test_the_order_layer_draws_a_standing_mark(self):
        layer = _src(SCENES / "map_order_layer.gd")
        assert "func set_dangers(points_world: Array, names: Array = []) -> void:" in layer
        assert "_draw_dangers(xform)" in _func(layer, "_draw")
        dangers = _func(layer, "_draw_dangers")
        assert "draw_colored_polygon" in dangers and "draw_circle" in dangers     # a shape and its "!"
        # lever L3 of the blind reading (reader 2: "the red triangle on the map has no name")
        assert "_draw_badge_in(box, label, Utils.cv(DANGER_COLOR), BADGE_FONT_PX, BADGE_BG, false)" in dangers
        assert "func danger_names() -> Array:" in layer
        assert '"dangers": _dangers.size()' in _func(layer, "report")
        assert "and _dangers.is_empty()" in _func(layer, "_process")              # it follows the camera

    def test_the_renderer_seats_it_from_the_names(self):
        renderer = _src(SCENES / "map_renderer_base.gd")
        seat = _func(renderer, "set_danger_regions")
        assert "order_layer.set_dangers(points, shown)" in seat
        assert "shown.append(str(n))" in seat                      # each mark wears its province's name
        # … and the map's names dodge the mark and its plate (seen in the real client: the
        # "Rhineland" plate stood over the name HESSE) — both tiers, as they dodge a UI panel
        # Row IC, directives: the goal ring's boxes join the danger marks' (one list for the label layer)
        assert "map_label_layer.set_mark_boxes(order_layer.mark_boxes())" in seat
        labels = _src(SCENES / "map_label_layer.gd")
        assert "_draw_label_tier(spec, xform, avoid, _local_ui_avoid_rects() + _mark_rects(xform), guard, fresh)" in labels
        assert "func set_mark_boxes(boxes: Array) -> void:" in labels
        boxes = _func(_src(SCENES / "map_order_layer.gd"), "danger_mark_boxes")
        assert '"at": _dangers[i]' in boxes and "DANGER_LIFT" in boxes and "BADGE_PAD" in boxes
        assert "set_danger_regions(_danger_regions)" in renderer.split("order_layer.set_arrows(arrows)")[1][:400]
        take = _func(_src(SCRIPTS / "main.gd"), "_ic_take_desk")
        assert "map_area.set_danger_regions(_ic_danger_regions())" in take

    def test_the_key_names_it(self):
        key = _src(SCRIPTS / "map_key.gd")
        entries = re.findall(r'^\t\["([A-Z ]+)", "(\w+)", "', key, re.M)
        # Fourteen since row IC's directives: the war goal's gold ring ("goal", in ORDERS).
        assert len(entries) == 14
        assert ("ORDERS", "goal") in entries
        assert ("THE LAND", "danger") in entries
        assert '"danger":' in key.split("func _draw() -> void:")[1]
        words = next(line for line in key.split("\n") if '"danger", "' in line)
        assert "nothing strong enough to hold it" in words and "one march away" in words
        assert "March a corps in, or have a corps there leave a garrison." in words

    def test_the_marks_are_the_desk_s_danger_rows(self, world):
        region = _open_province_beside(world, "Mack")
        built = today.desk(world)
        assert [d["region"] for d in built["danger"]] == [region.name]
        assert built["danger"][0]["line"] == next(
            r["text"] for r in built["decide"] if r["id"] == f"danger:{region.name}")
