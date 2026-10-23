"""S14d "The Table Lesson", part 1 — the first-open lines (`docs/TABLE_LESSON_SPEC.md`
§2–§3, §6; `BUG_FIXES.md` §S14D; Pre-Deploy S14d, October 23, 2026).

Seven action screens name the mechanic they show the first time they open: one
short line, once per campaign, latched in the save (`world.first_opens`), attached
at the response edge on a copy while unlatched (a read is not a showing), drawn at
the head of the surface and acknowledged once through `POST /first_open`. The
muster's gate road carries `what_if_line` like its resolved road (S14D-X4); a
standing PURSUE no longer burns the opening-attack guidance latch (S14D-X1).

The pins: the store and its round trip; every line under the cap, "Sire" in its
opening, clean under the typed-order census, its numbers from the live constants;
each attach site on the 1805 boot, carried on the turn it was first shown and never
after; the stored dialogue never gains the key; the acknowledgement's tiny dict
drains nothing; the GR6 census over readers of `first_opens`; the client's draw
sites by source; the lessons' pre-sets.
"""
from __future__ import annotations

import ast
import json
import re
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.game_logic import first_open as FO
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
GODOT = REPO / "godot-client" / "project-sovereign" / "scripts"
MAPS = REPO / "godot-client" / "project-sovereign" / "assets" / "maps"

# The user's rule (October 20, 2026): no line teaches a typed diplomatic order.
# Copied from `test_vp1_the_roads_armed.py` so the two censuses cannot drift apart
# silently (a quoted question to the desk — "what if …" — is not an order).
_TYPED = re.compile(
    r"'(?:proclaim|summon|convene|propose|declare|offer|sue|ally|vassalize|subjugate|"
    r"bind|buy off|sponsor|guarantee|make amends|break)\b[^']*'",
    re.IGNORECASE)


def _gd(name: str) -> str:
    return (GODOT / name).read_text(encoding="utf-8")


def _func(src: str, name: str) -> str:
    start = src.index(f"func {name}(")
    nxt = src.find("\nfunc ", start + 5)
    return src[start:nxt if nxt > 0 else len(src)]


def _every_line(world):
    for screen in FO.SCREENS:
        if screen == "settlement":
            yield screen, FO.line_for(world, screen, {"mode": "PROPOSE"})
            yield screen, FO.line_for(world, screen, {"mode": "REVIEW"})
        else:
            yield screen, FO.line_for(world, screen)


@pytest.fixture
def world():
    return WorldState(player_nation="France")


@pytest.fixture
def europe():
    """The 1805 boot through the TestClient (the conftest pins the bare world
    suite-wide; this fixture boots the campaign explicitly, as `/new_game` does
    for a named scenario)."""
    save_dir = Path(tempfile.mkdtemp()) / "saves"
    with patch("backend.save_manager.SAVE_DIR", save_dir):
        import backend.main as main_module

        main_module._reset_world_state(scenario_override=str(MAPS / "europe_1805.json"))
        with TestClient(main_module.app) as client:
            yield client, main_module, main_module.game_state["world"]
        main_module._reset_world_state()
    shutil.rmtree(save_dir.parent, ignore_errors=True)


# ══════════════════════════════════════════════════════════════════════════
# The store (§3)
# ══════════════════════════════════════════════════════════════════════════

class TestTheStore:
    def test_a_fresh_world_has_an_empty_store_and_it_serializes(self, world):
        assert world.first_opens == {}
        assert world.to_dict()["first_opens"] == {}

    def test_mark_seen_stamps_the_turn_once_and_refuses_an_unknown_id(self, world):
        world.current_turn = 4
        assert FO.mark_seen(world, "laws") is True
        world.current_turn = 9
        assert FO.mark_seen(world, "laws") is True          # idempotent
        assert world.first_opens == {"laws": 4}              # the FIRST showing's turn
        assert FO.mark_seen(world, "no_such_screen") is False
        assert "no_such_screen" not in world.first_opens

    def test_the_round_trip_and_the_legacy_load(self, world):
        world.current_turn = 3
        FO.mark_seen(world, "cabinet")
        FO.mark_seen(world, "moment_letter")
        data = world.to_dict()
        restored = WorldState.from_dict(data)
        assert restored.first_opens == {"cabinet": 3, "moment_letter": 3}
        # a pre-S14d save: no key → an empty store (each line shows once more)
        legacy = {k: v for k, v in data.items() if k != "first_opens"}
        assert WorldState.from_dict(legacy).first_opens == {}

    def test_values_are_coerced_to_int_and_a_bad_value_is_dropped(self, world):
        data = world.to_dict()
        data["first_opens"] = {"laws": "7", "designs": 2.0, "cabinet": "late"}
        assert WorldState.from_dict(data).first_opens == {"laws": 7, "designs": 2}

    def test_to_dict_stays_at_the_ratchet_s_edge(self):
        """The new key shares the `moments` line: `to_dict` is exactly 500 lines
        and the ratchet caps functions over 500 (28 today, all named)."""
        src = (REPO / "backend" / "models" / "world_state.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        to_dict = next(n for n in ast.walk(tree)
                       if isinstance(n, ast.FunctionDef) and n.name == "to_dict")
        assert to_dict.end_lineno - to_dict.lineno + 1 <= 500


# ══════════════════════════════════════════════════════════════════════════
# The lines (§2)
# ══════════════════════════════════════════════════════════════════════════

class TestTheLines:
    def test_seven_screens_and_every_line_under_the_cap(self, world):
        assert FO.SCREENS == ("cabinet", "designs", "settlement", "separate_peace",
                              "laws", "admiralty_camp", "moment_letter")
        for screen, line in _every_line(world):
            assert line, screen
            assert len(line) <= FO.LINE_CAP, (screen, len(line), line)

    def test_every_line_opens_to_the_sovereign_and_teaches_no_typed_order(self, world):
        for screen, line in _every_line(world):
            assert "Sire" in line, (screen, line)
            assert not _TYPED.search(line), (screen, line)
            assert "_" not in line, (screen, line)          # no internal key leaks

    def test_every_number_is_the_live_constant(self, world):
        from backend.game_logic.imperial_designs import PROCLAIM_ADMIN_COST, PROCLAIM_DP_COST
        from backend.game_logic.naval import (
            DESCENT_CAMP_MIN_TROOPS, DESCENT_CAMP_STAGED_TURNS, WINDOW_TURNS,
        )
        from backend.game_logic.reforms import ARREARS_WINDOW_TURNS
        from backend.game_logic.settlement_scoring import ACCEPTANCE_THRESHOLD
        assert f"{PROCLAIM_DP_COST} DP" in FO.line_for(world, "designs")
        assert f"{PROCLAIM_ADMIN_COST} administrative" in FO.line_for(world, "designs")
        for mode in ("PROPOSE", "REVIEW"):
            assert f"reach {ACCEPTANCE_THRESHOLD}" in FO.line_for(world, "settlement", {"mode": mode})
        assert f"within {ARREARS_WINDOW_TURNS} turns" in FO.line_for(world, "laws")
        camp = FO.line_for(world, "admiralty_camp")
        assert f"{DESCENT_CAMP_MIN_TROOPS:,} men" in camp
        assert f"{DESCENT_CAMP_STAGED_TURNS} turns at war" in camp
        assert f"up to {WINDOW_TURNS} turns" in camp

    def test_the_table_s_two_forms_follow_the_mode(self, world):
        """The levers (Demand more / Ease / Drop / the chip) exist only in
        PROPOSE (`settlement_staging.py:3859-3937`); REVIEW names the frozen
        terms and the verdict beside each row."""
        propose = FO.line_for(world, "settlement", {"mode": "PROPOSE"})
        review = FO.line_for(world, "settlement", {"mode": "REVIEW"})
        assert "Demand more" in propose and "taken alone" in propose
        assert "Demand more" not in review and "as offered" in review
        assert FO.line_for(world, "settlement") == review   # no mode → the frozen form

    def test_the_camp_line_states_no_shut_outcome_as_certain(self, world):
        """The FA-31 class: the Strait "can open … for up to" — a fleet action or
        parity also opens it, and the second turn can be shut on the board."""
        camp = FO.line_for(world, "admiralty_camp")
        assert "can open the Strait for up to" in camp
        assert "blockade on you" in camp                    # Britain's blockade, not ours

    def test_a_line_is_a_pure_read(self, world):
        before = dict(world.first_opens)
        for _ in _every_line(world):
            pass
        assert world.first_opens == before


# ══════════════════════════════════════════════════════════════════════════
# The turn rule and the stored dialogue (§3)
# ══════════════════════════════════════════════════════════════════════════

class TestTheTurnRule:
    def test_the_line_rides_the_turn_it_was_first_shown_and_never_after(self, world):
        world.current_turn = 5
        assert FO.line_for(world, "laws")
        FO.mark_seen(world, "laws")
        assert FO.line_for(world, "laws")                    # the same turn: still carried
        world.current_turn = 6
        assert FO.line_for(world, "laws") == ""              # a later turn: gone

    def test_with_line_copies_and_the_stored_dialogue_never_gains_the_key(self, world):
        stored = {"type": "settlement_confirm", "dialogue_mode": "PROPOSE", "war_id": "war_1"}
        wired = FO.with_line(world, stored)
        assert wired is not stored
        assert wired["first_open"]["screen"] == "settlement"
        assert "Demand more" in wired["first_open"]["line"]
        assert "first_open" not in stored
        # not a lined dialogue → the SAME object, untouched
        other = {"type": "mission"}
        assert FO.with_line(world, other) is other

    def test_the_chooser_s_peace_arm_only_and_the_letter_by_its_register(self, world):
        peace = {"type": "settlement_pair_substitute_confirm", "proposal_type": "peace"}
        armistice = {"type": "settlement_pair_substitute_confirm", "proposal_type": "armistice"}
        assert FO.with_line(world, peace)["first_open"]["screen"] == "separate_peace"
        assert FO.with_line(world, armistice) is armistice
        letter = {"is_moment": True, "title": "The Bavarian Match"}
        assert FO.with_line(world, letter)["first_open"]["screen"] == "moment_letter"
        dialogue = {"type": "incoming_proposal", "popup_payload": {"is_moment": True}}
        assert FO.with_line(world, dialogue)["first_open"]["screen"] == "moment_letter"
        envoy = {"type": "incoming_proposal", "popup_payload": {"from_nation": "Austria"}}
        assert FO.with_line(world, envoy) is envoy


# ══════════════════════════════════════════════════════════════════════════
# The attach sites on the 1805 boot (§2) and the acknowledgement (§3)
# ══════════════════════════════════════════════════════════════════════════

class TestTheAttachSites:
    def test_the_cabinet_s_two_modes_and_never_the_settlement_mode(self, europe):
        client, _m, _w = europe
        listing = client.get("/diplomatic_preview").json()
        assert listing["mode"] == "nations"
        assert listing["first_open"]["screen"] == "cabinet"
        preview = client.get("/diplomatic_preview", params={"nation": "Austria"}).json()
        assert preview["success"] is True
        assert preview["first_open"]["screen"] == "cabinet"
        settlement_mode = client.get("/diplomatic_preview",
                                     params={"mode": "settlement", "war_id": "war_1"}).json()
        assert "first_open" not in settlement_mode

    def test_the_road_page_the_laws_book_and_the_camp(self, europe):
        client, _m, _w = europe
        designs = client.get("/imperial_designs").json()
        assert designs["armed"] is True
        assert designs["first_open"]["screen"] == "designs"
        ledger = client.get("/ledger").json()["ledger"]
        assert ledger["laws"]["first_open"]["screen"] == "laws"
        assert ledger["admiralty"]["own_fleet"]["camp_provinces"]      # France authors a camp
        assert ledger["admiralty"]["first_open"]["screen"] == "admiralty_camp"

    def test_the_table_arrives_lined_and_the_stored_dialogue_stays_clean(self, europe):
        client, _m, world = europe
        response = client.post("/command", json={"command": "propose common peace with Austria"}).json()
        dialogue = response["diplomatic_dialogue"]
        assert dialogue["dialogue_type"] == "settlement_confirm"
        assert dialogue["first_open"]["screen"] == "settlement"
        assert "Demand more" in dialogue["first_open"]["line"]           # PROPOSE form
        assert "first_open" not in world.pending_diplomatic_dialogue

    def test_the_acknowledgement_is_a_tiny_dict_that_drains_nothing(self, europe):
        client, _m, world = europe
        client.post("/command", json={"command": "propose common peace with Austria"})
        world.pending_settlement_draft_notices = [{"probe": True}]
        notices_before = list(world.pending_settlement_draft_notices)
        ack = client.post("/first_open", json={"screen": "settlement"}).json()
        assert ack == {"success": True, "screen": "settlement", "turn": int(world.current_turn)}
        assert world.pending_settlement_draft_notices == notices_before   # not drained
        assert world.first_opens == {"settlement": int(world.current_turn)}
        bogus = client.post("/first_open", json={"screen": "bogus"}).json()
        assert bogus == {"success": False, "screen": "bogus", "turn": int(world.current_turn)}

    def test_carried_through_the_turn_s_restages_then_never_again(self, europe):
        client, main_module, world = europe
        client.post("/command", json={"command": "propose common peace with Austria"})
        client.post("/first_open", json={"screen": "settlement"})
        again = client.post("/command", json={"command": "propose common peace with Austria"}).json()
        assert "first_open" in again["diplomatic_dialogue"]              # the same turn
        world.current_turn += 1
        try:
            later = main_module._wire_dialogue(world, world.pending_diplomatic_dialogue)
            assert "first_open" not in later
            client.post("/first_open", json={"screen": "cabinet"})
            world.current_turn += 1
            assert "first_open" not in client.get("/diplomatic_preview").json()
        finally:
            world.current_turn -= 2


# ══════════════════════════════════════════════════════════════════════════
# GR6 — no mechanic reads the store (§3)
# ══════════════════════════════════════════════════════════════════════════

class TestTheCensus:
    ALLOWED = {"backend/game_logic/first_open.py", "backend/models/world_state.py"}

    def test_only_the_module_and_the_save_touch_first_opens(self):
        found = set()
        for path in (REPO / "backend").rglob("*.py"):
            if "first_opens" in path.read_text(encoding="utf-8", errors="replace"):
                found.add(path.relative_to(REPO).as_posix())
        assert found == self.ALLOWED, found

    def test_the_module_adds_no_lever(self):
        """`LEVER_RE` matches a column-0 all-caps bool literal; the copy table
        is a dict and the ids a tuple."""
        src = (REPO / "backend" / "game_logic" / "first_open.py").read_text(encoding="utf-8")
        assert not re.search(r"^[A-Z][A-Z0-9_]{3,}\s*(?::\s*bool)?\s*=\s*(True|False)\s*(#.*)?$",
                             src, re.M)


# ══════════════════════════════════════════════════════════════════════════
# The client's draw sites (§2) — by source; the frames are IQ-10's
# ══════════════════════════════════════════════════════════════════════════

class TestTheClient:
    def test_the_acknowledgement_queue_and_its_reset_on_a_world_swap(self):
        api = _gd("api_client.gd")
        assert 'func note_first_open(screen: String) -> void:' in api
        assert '_send_post("/first_open", {"screen": screen}, func(_response): pass)' in api
        assert "func reset_first_open_acks() -> void:" in api
        main = _gd("main.gd")
        assert "api_client.reset_first_open_acks()" in _func(main, "_reset_frontend_state_for_world_swap")
        assert "func _on_first_open_seen(screen: String) -> void:" in main
        for surface in ("incoming_proposal_popup", "proposal_confirm_popup", "diplomacy_wizard"):
            assert f"{surface}.first_open_seen.connect(_on_first_open_seen)" in main, surface

    def test_the_wizard_draws_the_line_at_the_head_of_each_view(self):
        src = _gd("diplomacy_wizard.gd")
        assert "signal first_open_seen(screen: String)" in src
        helper = _func(src, "_add_first_open_line")
        assert 'data.get("first_open")' in helper and "first_open_seen.emit(screen)" in helper
        for view in ("_render_nations", "_render_designs"):
            assert "_add_first_open_line(data)" in _func(src, view), view
        # NOT on a court's page: at scale 2.0 a line above the assessment pushed
        # the action chips below the fold (the EA-E5 frame); the Cabinet's line
        # is its first view's, and a door-opened page meets it on the next open.
        assert "_add_first_open_line(data)" not in _func(src, "_render_preview")
        # the road page: the line precedes the headline (the strip stays above the fold)
        designs = _func(src, "_render_designs")
        assert designs.index("_add_first_open_line(data)") < designs.index("var head = RichTextLabel.new()")

    def test_the_table_and_the_chooser_lead_with_the_line(self):
        src = _gd("proposal_confirm_popup.gd")
        assert "signal first_open_seen(screen: String)" in src
        table = _func(src, "_build_settlement_content")
        assert '_first_open_bbcode(data, "settlement")' in table
        # under the heading's two lines (the verdict stays seen at scale 2.0 —
        # the EA-E6 frame), before the table and its rows
        line_at = table.index('_first_open_bbcode(data, "settlement")')
        assert table.index("ready for ratification") < line_at < table.index("UX-2 (GT-Slice-3)")
        chooser = _func(src, "_build_pair_substitute_confirm_content")
        assert chooser.index('_first_open_bbcode(data, "separate_peace")') < chooser.index("Leave the joint settlement?")

    def test_the_ledger_s_two_books_and_the_laws_subtitle(self):
        src = _gd("strategic_ledger.gd")
        laws = _func(src, "_render_laws_tab")
        assert "The laws of the Empire — what each does, its price, its upkeep" in laws   # R159 (S14D-X2)
        assert '_first_open_bbcode(laws, "laws")' in laws
        block = _func(src, "_render_admiralty_block")
        assert '_first_open_bbcode(adm, "admiralty_camp")' in block
        # the camp's line precedes the warning that names staging (S14D-X25)
        assert block.index('_first_open_bbcode(adm, "admiralty_camp")') < block.index('fleet.get("rot_line"')
        helper = _func(src, "_first_open_bbcode")
        assert "_api_client_ref.note_first_open(screen)" in helper

    def test_the_letter_s_sixth_part_precedes_the_record(self):
        src = _gd("incoming_proposal_popup.gd")
        assert "signal first_open_seen(screen: String)" in src
        body = _func(src, "_build_moment_body")
        assert body.index('data.get("first_open")') < body.index('data.get("record", "")')
        assert "_moment_text(fo.get(\"line\", \"\"))" in body


# ══════════════════════════════════════════════════════════════════════════
# The lessons' pre-sets (§0 Q5; S14D-X23)
# ══════════════════════════════════════════════════════════════════════════

class TestTheScenarioPreset:
    def test_the_danube_pre_sets_exactly_the_ids_its_cards_open(self):
        data = json.loads((MAPS / "tutorial_1805.json").read_text(encoding="utf-8"))
        assert data["first_opens"] == {"cabinet": 0, "laws": 0}
        assert set(data["first_opens"]) <= set(FO.SCREENS)
        # the fifth engine hint is authored like the other four (S14D-X23)
        for latch in ("coordination_tutorial_shown", "opening_attack_guidance_shown",
                      "delegation_hint_shown", "muster_hint_shown", "commission_hint_shown"):
            assert data[latch] is True, latch

    def test_a_pre_set_id_shows_no_line_on_the_lesson_world(self):
        world = WorldState.from_scenario(str(MAPS / "tutorial_1805.json"))
        assert FO.line_for(world, "cabinet") == ""
        assert FO.line_for(world, "laws") == ""
        assert FO.line_for(world, "settlement", {"mode": "PROPOSE"})   # not pre-set: the Table's


# ══════════════════════════════════════════════════════════════════════════
# The engine hints beside the store — S14D-X1 and S14D-X4
# ══════════════════════════════════════════════════════════════════════════

class TestTheEngineHints:
    def test_a_standing_pursue_never_burns_the_opening_guidance(self, world):
        """S14D-X1: turn 1, Ney at Belgium, Wellington at Waterloo, a PURSUE run by
        the strategic processor flipped the latch and dropped the card."""
        from backend.commands.executor import CommandExecutor
        from backend.commands.strategic import StrategicOrderProcessor
        from backend.models.marshal import StrategicOrder

        ney = world.get_marshal("Ney")
        assert (ney.location, world.get_marshal("Wellington").location, world.current_turn) == \
            ("Belgium", "Waterloo", 1)
        ney.strategic_order = StrategicOrder(
            command_type="PURSUE", target="Wellington", target_type="marshal",
            started_turn=1, original_command="Ney, pursue Wellington", path=[])
        StrategicOrderProcessor(CommandExecutor()).process_strategic_orders(world, {"world": world})
        assert world.opening_attack_guidance_shown is False

    def test_a_direct_order_still_surfaces_the_guidance_once(self, world):
        from backend.commands.executor import CommandExecutor
        ex = CommandExecutor()
        result = ex.execute({"success": True, "command": {"marshal": "Ney", "action": "attack",
                                                          "target": "Wellington"}},
                            {"world": world})
        assert world.opening_attack_guidance_shown is True
        assert result.get("opening_attack_guidance")

    def test_the_cancel_road_names_the_free_preview(self, world):
        """S14D-X4: the muster's gate road — the Cancel return carries `what_if_line`
        as the resolved road does."""
        from backend.commands.executor import CommandExecutor
        from backend.commands.strategic import StrategicOrderProcessor

        ney = world.get_marshal("Ney")
        ney.pending_interrupt = {"interrupt_type": "muster_confirm", "marshal": "Ney",
                                 "target": "Wellington", "options": ["attack_anyway", "cancel_order"]}
        out = StrategicOrderProcessor(CommandExecutor()).handle_response(
            "Ney", "muster_confirm", "cancel_order", world, {"world": world})
        assert out["success"] is True
        assert "stands down" in out["message"]
        assert "Ask 'what if Ney attacks Wellington'" in out["message"]

    def test_the_interrupt_s_message_names_the_free_preview(self):
        src = (REPO / "backend" / "commands" / "combat_executor.py").read_text(encoding="utf-8")
        stage = src[src.index("def _attack_routing_and_muster("):]
        stage = stage[:stage.index("\n    def ", 10)]
        assert "+ what_if_line(ctx.marshal, ctx.enemy_marshal)" in stage
