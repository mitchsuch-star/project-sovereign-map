"""Row PW "Plain Words" (November 18, 2026 — the first playtest).

The player, of thirteen turns of the 1805 campaign: a sound that lingers and a
clicking "like a car's turn signal"; generals hard to click, clumsy to send and
charged two actions for a step next door; corps that entered enemy land and did
not take it ("i had 3 people in colinia and no one could take it"); provinces
that "randomly flipped back"; an enemy turn that is "opaque and confusing";
battles whose decisions are unclear; a peace table that gave away his own
province on "More generous", buttons that "sometimes do nothing", windows that
bob and one bigger than the screen. "Everything feels convoluted and opaque and
disconnected."

These are the behaviour pins of what row PW changed, rule by rule. The client's
own halves are pinned on their source here and driven in the real client by the
instrument (`tools/dd_b_play.py`; the records are in `docs/BUG_FIXES.md` §PW).
"""

from __future__ import annotations

import pathlib
import re

import pytest

from backend.commands import ground
from backend.commands import order_quotes as Q
from backend.display_names import (
    ACCEPTANCE_COMPONENT_DISPLAY,
    ACCEPTANCE_COMPONENT_PLAIN,
    ODDS_PLAIN,
    acceptance_band_plain,
    odds_plain,
)
from backend.game_logic import battle_telling as T
from backend.game_logic import while_you_waited as WYW
from backend.models.intel import FULL, PARTIAL
from backend.models.world_state import WorldState

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"
SCENES = REPO / "godot-client" / "project-sovereign" / "scenes"


def _src(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def _func(source: str, name: str) -> str:
    """The body of a top-level GDScript function (to the next top-level line)."""
    match = re.search(rf"^(?:static )?func {re.escape(name)}\(.*?(?=^\S|\Z)", source, re.S | re.M)
    assert match, f"no func {name}"
    return match.group(0)


def _code(source: str) -> str:
    """A script without its whole-line comments (a comment may quote the words
    a rule retired; the pin is on what the script DOES)."""
    return "\n".join(line for line in source.splitlines() if not line.lstrip().startswith("#"))


FORT = {"type": "fortification", "damaged": False}      # `Region.buildings` rows


def _see(world, region: str, level=FULL) -> None:
    world._intel_entry(region).visibility = level


def _clear(world, region: str) -> None:
    """Empty a province of every corps but the player's (moved far away)."""
    for m in world.marshals.values():
        if m.location == region and m.nation != world.player_nation:
            m.location = "Dresden"


@pytest.fixture
def board():
    """The flag world: France at war with Britain and Prussia; Grouchy
    (28,000, range 1) at Lyon beside Prussia's Rhineland."""
    world = WorldState()
    _clear(world, "Rhineland")
    _see(world, "Rhineland")
    return world


# ═════════════════════════════════════════════════════════════════════════════
# 1. Sound — the clock is out of the study, the quill stops with the reply
# ═════════════════════════════════════════════════════════════════════════════

class TestTheSoundsStop:
    AUDIO = _src(SCRIPTS / "audio_manager.gd")

    def test_the_study_bed_has_no_clock(self):
        assert 'const STUDY_BED := ["wind", "fire"]' in self.AUDIO
        bed = _func(self.AUDIO, "_start_ambience")
        assert "STUDY_BED" in bed and '"clock"' not in bed

    def test_a_loop_of_waiting_has_a_ceiling(self):
        assert re.search(r'const LOOP_MAX_S := \{"scribble": 6\.0', self.AUDIO)
        start = _func(self.AUDIO, "_start_loop")
        assert "LOOP_MAX_S.has(tag)" in start and "_loop_cap_due.bind(tag, p.get_instance_id())" in start
        cap = _func(self.AUDIO, "_loop_cap_due")
        assert "p.get_instance_id() == player_id" in cap and "_stop_loop(tag)" in cap

    def test_the_quill_stops_when_the_reply_arrives(self):
        api = _src(SCRIPTS / "api_client.gd")
        done = _func(api, "_on_request_completed")
        assert "AudioManager.stop_scribble()" in done and "_in_flight_is_post" in done

    def test_each_screens_loop_stops_however_the_screen_shuts(self):
        wizard = _func(_src(SCRIPTS / "diplomacy_wizard.gd"), "_on_visibility_changed")
        assert 'AudioManager.stop_loop("crowd")' in wizard
        phase = _func(_src(SCRIPTS / "enemy_phase_dialog.gd"), "_on_visibility_changed")
        assert 'AudioManager.stop_loop("march_long")' in phase
        table = _func(_src(SCRIPTS / "battle_diorama.gd"), "_on_table_visibility_changed")
        for loop in ("battle_bed", "scribble_verdict"):
            assert loop in table


# ═════════════════════════════════════════════════════════════════════════════
# 2. Does he take it? — the ground, read before the order and after it
# ═════════════════════════════════════════════════════════════════════════════

class TestTheGroundIsRead:
    def test_an_open_province_in_full_sight_is_taken(self, board):
        grouchy = board.get_marshal("Grouchy")
        reading = ground.entering(board, grouchy, "Rhineland")
        assert reading["takes"] is True and reading["code"] == "takes"
        assert reading["line"] == "takes the province"

    def test_out_of_full_sight_nothing_is_promised(self, board):
        _see(board, "Rhineland", PARTIAL)
        reading = ground.entering(board, board.get_marshal("Grouchy"), "Rhineland")
        assert reading["takes"] is None and reading["code"] == "takes_if_open"
        assert "if nothing we cannot see holds it" in reading["line"]

    def test_a_garrison_that_fights_is_named_with_its_remedy(self, board):
        region = board.get_region("Rhineland")
        region.garrison_strength = 12500
        reading = ground.entering(board, board.get_marshal("Grouchy"), "Rhineland")
        assert reading["takes"] is False and reading["code"] == "garrison"
        assert "a garrison of 12,500 holds it" in reading["line"]
        assert reading["remedy_command"] == "Grouchy, attack Rhineland"
        assert reading["remedy_label"] == "Storm Rhineland"

    def test_works_must_be_besieged(self, board):
        board.get_region("Rhineland").buildings.append(dict(FORT))
        reading = ground.entering(board, board.get_marshal("Grouchy"), "Rhineland")
        assert reading["takes"] is False and reading["code"] == "fort"
        assert reading["remedy_label"] == "Besiege Rhineland"

    def test_a_corps_in_sight_comes_first(self, board):
        board.get_marshal("Gneisenau").location = "Rhineland"
        reading = ground.entering(board, board.get_marshal("Grouchy"), "Rhineland")
        assert reading["code"] == "enemy_corps" and reading["takes"] is False
        assert reading["remedy_command"] == "Grouchy, attack Gneisenau"

    def test_a_friends_or_a_neutrals_province_says_nothing(self, board):
        # Austria is at peace with France on this board: nothing to take, no line.
        reading = ground.entering(board, board.get_marshal("Grouchy"), "Tyrol")
        assert reading["code"] == "not_at_war" and reading["line"] == "" and reading["takes"] is None

    def test_a_raiding_party_is_told_it_cannot_hold(self, board):
        # the rule is the Europe map's: under the floor, onto a province that
        # opened the campaign as its holder's own (VP-R1 b)
        board.sovereign_map = "europe"
        board.nation_starting_regions = {"Prussia": ["Rhineland"]}
        grouchy = board.get_marshal("Grouchy")
        grouchy.strength = 3000
        reading = ground.entering(board, grouchy, "Rhineland")
        assert reading["takes"] is False and reading["code"] == "raiding"

    def test_standing_reads_the_attack_roads_exits_in_order(self, board):
        grouchy = board.get_marshal("Grouchy")
        grouchy.location = "Rhineland"
        open_ground = ground.standing(board, grouchy)
        assert open_ground["code"] == "open" and open_ground["remedy_label"] == "Take Rhineland"
        assert ground.can_take_where_he_stands(board, grouchy) is True
        board.get_region("Rhineland").buildings.append(dict(FORT))
        fort = ground.standing(board, grouchy)
        assert fort["code"] == "fort" and fort["remedy_label"] == "Besiege Rhineland"
        assert ground.can_take_where_he_stands(board, grouchy) is False
        board.get_region("Rhineland").garrison_strength = 9000
        assert ground.standing(board, grouchy)["code"] == "garrison"
        board.get_marshal("Gneisenau").location = "Rhineland"
        corps = ground.standing(board, grouchy)
        assert corps["code"] == "enemy_corps" and corps["foe"] == "Gneisenau"

    def test_the_card_row_stands_only_on_ground_we_are_at_war_for(self, board):
        from backend.models.world_state import _stands_on
        grouchy = board.get_marshal("Grouchy")
        grouchy.location = "Tyrol"                      # Austria's: no war, no row
        assert _stands_on(board, grouchy) == {}
        grouchy.location = "Rhineland"
        row = _stands_on(board, grouchy)
        assert row["code"] == "open" and row["ok"] is True and row["open"] is True
        assert row["command"] == "Grouchy, attack Rhineland"
        board.get_marshal("Gneisenau").location = "Rhineland"
        row = _stands_on(board, grouchy)
        assert row["code"] == "enemy_corps" and row["foe"] == "Gneisenau" and row["open"] is False

    def test_every_panel_code_is_a_code_standing_can_give(self):
        source = _src(REPO / "backend" / "commands" / "ground.py")
        body = source[source.index("def standing("):source.index("def can_take_where_he_stands")]
        for code in ground.SAID_ON_THE_PANEL:
            assert f'"{code}"' in body, code


# ═════════════════════════════════════════════════════════════════════════════
# 3. Sending — a step within reach is the MOVE (1 action), and what is quoted
#    is what the order then does
# ═════════════════════════════════════════════════════════════════════════════

class TestAMoveInReachIsAMove:
    def test_next_door_is_quoted_as_the_one_action_move(self, board):
        grouchy = board.get_marshal("Grouchy")
        quote = Q.march_quote(board, grouchy, "Rhineland", click=True)
        assert quote["kind"] == "move" and quote["ok"] is True
        assert quote["command"] == "Grouchy, move to Rhineland"
        assert quote["ap"] == int(board.get_action_cost("move")) == 1
        assert quote["turns"] == 0 and quote["road"] == ["Rhineland"]
        assert quote["confirm"] is False and quote["ground"]["takes"] is True

    def test_a_typed_march_is_still_read_as_the_march(self, board):
        """The move is the CLICK road's (`click=True`: the map, the province
        panel). A reader of a typed march — the readback under the line,
        Berthier's "what if he marches to …" — asks about the march and is
        answered about the march (found by the suite: the readback priced a
        typed `march to` at the move's price)."""
        grouchy = board.get_marshal("Grouchy")
        typed = Q.march_quote(board, grouchy, "Rhineland")
        assert typed["kind"] == "march" and typed["command"] == "Grouchy, march to Rhineland"
        clicked = Q.march_quote(board, grouchy, "Rhineland", click=True)
        assert clicked["kind"] == "move" and clicked["command"] == "Grouchy, move to Rhineland"

    def test_further_off_is_still_the_march(self, board):
        grouchy = board.get_marshal("Grouchy")
        quote = Q.march_quote(board, grouchy, "Saxony", click=True)
        assert quote["kind"] == "march" and quote["command"] == "Grouchy, march to Saxony"
        assert quote["turns"] >= 1

    def test_the_seam_down_restores_the_march(self, board, monkeypatch):
        monkeypatch.setattr(Q, "a_move_in_reach_is_a_move", lambda: False)
        quote = Q.march_quote(board, board.get_marshal("Grouchy"), "Rhineland", click=True)
        assert quote["kind"] == "march" and quote["command"] == "Grouchy, march to Rhineland"

    def test_a_province_he_would_only_enter_asks_first(self, board):
        board.get_region("Rhineland").garrison_strength = 12500
        quote = Q.march_quote(board, board.get_marshal("Grouchy"), "Rhineland", click=True)
        assert quote["kind"] == "move" and quote["confirm"] is True
        assert quote["ground"]["remedy_label"] == "Storm Rhineland"

    def test_the_reach_prices_each_row_and_carries_its_tag(self, board):
        grouchy = board.get_marshal("Grouchy")
        reach = Q.march_reach(board, grouchy)
        assert reach["ok"] is True
        row = reach["reach"]["Rhineland"]
        assert row["kind"] == "move" and row["ap"] == 1 and row["turns"] == 0
        # every row's tag is the exact quote's tag (the drift census)
        for dest, entry in reach["reach"].items():
            quote = Q.march_quote(board, grouchy, dest, click=True)
            assert list(entry.get("tag") or []) == list(quote.get("tag") or []), dest
            assert entry.get("kind", "march") == ("move" if quote["kind"] == "move" else "march"), dest

    def test_the_tag_says_what_the_march_costs_in_men(self, board):
        grouchy = board.get_marshal("Grouchy")
        quote = Q.march_quote(board, grouchy, "Rhineland", click=True)
        lost, unsure = Q.march_cost_reading(board, grouchy, ["Rhineland"])
        if lost > 0:
            assert any("men lost on the march" in line for line in quote["tag"])
            assert quote["march_cost"].startswith("The march costs")
        assert quote["tag"][0] == "takes the province"

    def test_what_is_quoted_is_what_the_order_does(self, board):
        """The drift census: send the quoted move down the typed road."""
        from backend.commands.executor import CommandExecutor
        from backend.commands.parser import CommandParser
        grouchy = board.get_marshal("Grouchy")
        quote = Q.march_quote(board, grouchy, "Rhineland", click=True)
        before = int(board.actions_remaining)
        parsed = CommandParser(use_real_llm=False).parse(quote["command"])
        result = CommandExecutor().execute(parsed, {"world": board})
        assert result.get("success"), result.get("message")
        assert grouchy.location == "Rhineland"
        assert before - int(board.actions_remaining) == quote["ap"]
        # the ground said he would take it, and he did
        assert board.get_region("Rhineland").controller == "France"

    def test_a_move_that_does_not_take_says_why_and_offers_the_order(self, board):
        from backend.commands.executor import CommandExecutor
        from backend.commands.parser import CommandParser
        board.get_region("Rhineland").garrison_strength = 12500
        grouchy = board.get_marshal("Grouchy")
        parsed = CommandParser(use_real_llm=False).parse("Grouchy, move to Rhineland")
        result = CommandExecutor().execute(parsed, {"world": board})
        assert result.get("success"), result.get("message")
        assert board.get_region("Rhineland").controller == "Prussia"
        assert result["ground"]["code"] == "garrison"
        assert result["remedy_command"] == "Grouchy, attack Rhineland"
        assert "Rhineland is not ours yet" in result["message"]


class TestTheOrderThatTakes:
    def test_an_open_province_underfoot_is_one_click(self, board):
        grouchy = board.get_marshal("Grouchy")
        grouchy.location = "Rhineland"
        quote = Q.take_quote(board, grouchy)
        assert quote["kind"] == "take" and quote["ok"] is True
        assert quote["command"] == "Grouchy, attack Rhineland"
        assert quote["confirm"] is False and quote["ap"] == int(board.get_action_cost("attack"))

    def test_works_are_a_siege_and_say_so(self, board):
        grouchy = board.get_marshal("Grouchy")
        grouchy.location = "Rhineland"
        board.get_region("Rhineland").buildings.append(dict(FORT))
        quote = Q.take_quote(board, grouchy)
        assert quote["ok"] is True and quote["confirm"] is True
        assert "lays siege" in quote["note"] and "falls when the turn ends" in quote["note"]

    def test_a_corps_in_the_field_is_no_take(self, board):
        grouchy = board.get_marshal("Grouchy")
        grouchy.location = "Rhineland"
        board.get_marshal("Gneisenau").location = "Rhineland"
        quote = Q.take_quote(board, grouchy)
        assert quote["ok"] is False and "Gneisenau" in quote["refusal"]

    def test_the_siege_reply_does_not_say_taken(self, board):
        from backend.commands.executor import CommandExecutor
        from backend.commands.parser import CommandParser
        grouchy = board.get_marshal("Grouchy")
        grouchy.location = "Rhineland"
        board.get_region("Rhineland").buildings.append(dict(FORT))
        parsed = CommandParser(use_real_llm=False).parse("Grouchy, attack Rhineland")
        result = CommandExecutor().execute(parsed, {"world": board})
        assert result.get("occupation_started") is True, result.get("message")
        assert "lays siege to Rhineland" in result["message"]
        assert "takes Rhineland where he stands" not in result["message"]
        assert board.get_region("Rhineland").controller == "Prussia"
        assert ground.standing(board, grouchy)["code"] == "besieging"


# ═════════════════════════════════════════════════════════════════════════════
# 4. While you waited — what changed for the player, and why
# ═════════════════════════════════════════════════════════════════════════════

class TestWhileYouWaited:
    def test_a_province_walked_into_is_named_with_its_cause(self, board):
        before = WYW.snapshot(board)
        board.get_region("Belgium").controller = "Britain"
        board.get_marshal("Ney").location = "Paris"
        board.get_marshal("Wellington").location = "Belgium"
        _see(board, "Belgium")
        phase = {"nations": {"Britain": {"actions": [{"events": [{
            "type": "conquest", "marshal": "Wellington", "region": "Belgium",
            "unopposed": True, "captured_by": "Britain", "captured_from": "France"}]}]}}}
        # (the snapshot was read with Ney standing there: he left in the phase)
        before["corps"].pop("Belgium", None)
        digest = WYW.digest(board, before, phase, [])
        assert digest["quiet"] is False
        row = digest["lost"][0]
        assert row["region"] == "Belgium" and row["how"] == "walked_in"
        assert row["line"] == "Belgium — lost to Britain. Wellington marched in; nobody was holding it."
        assert "Belgium" in digest["flash"]
        assert digest["keep_it"].startswith("An empty province can be walked back into")

    def test_a_marshal_out_of_sight_is_never_named(self, board):
        before = WYW.snapshot(board)
        before["corps"].pop("Belgium", None)
        board.get_region("Belgium").controller = "Britain"
        board.get_marshal("Ney").location = "Paris"
        board.get_marshal("Wellington").location = "Belgium"
        board._intel_entry("Belgium").visibility = "unknown"
        phase = {"nations": {"Britain": {"actions": [{"events": [{
            "type": "conquest", "marshal": "Wellington", "region": "Belgium",
            "captured_from": "France"}]}]}}}
        digest = WYW.digest(board, before, phase, [])
        line = digest["lost"][0]["line"]
        assert "Wellington" not in line and "A British army marched in" in line

    def test_a_province_lost_in_battle_names_the_battle(self, board):
        before = WYW.snapshot(board)
        board.get_region("Belgium").controller = "Britain"
        board.get_marshal("Wellington").location = "Belgium"
        _see(board, "Belgium")
        battle = {"type": "battle", "location": "Belgium", "attacker_nation": "Britain",
                  "defender_nation": "France", "victor": "Wellington", "outcome": "attacker_victory",
                  "region_conquered": True, "region_name": "Belgium",
                  "attacker": {"name": "Wellington", "casualties": 900},
                  "defender": {"name": "Ney", "casualties": 4200, "forced_retreat": True}}
        digest = WYW.digest(board, before, {"nations": {"Britain": {"actions": [{"events": [battle]}]}}}, [])
        assert digest["lost"][0]["line"] == "Belgium — lost to Britain. Wellington beat Ney there."
        fight = digest["battles"][0]
        assert fight["result"] == "lost" and fight["our_loss"] == 4200 and fight["their_loss"] == 900
        assert fight["line"] == ("Belgium: Wellington attacked Ney and won. Losses: you 4,200, "
                                 "him 900. Ney was driven off.")

    def test_a_siege_that_ends_is_a_gain(self, board):
        before = WYW.snapshot(board)
        board.get_region("Rhineland").controller = "France"
        events = [{"type": "occupation_complete", "marshal": "Grouchy", "nation": "France",
                   "region": "Rhineland"}]
        digest = WYW.digest(board, before, None, events)
        assert digest["gained"][0]["line"] == "Rhineland — now yours (was Prussia's). Grouchy's siege ended."

    def test_a_quiet_turn_says_so(self, board):
        digest = WYW.digest(board, WYW.snapshot(board), None, [])
        assert digest["quiet"] is True and digest["lost"] == [] and digest["flash"] == []

    def test_an_enemy_who_moved_beside_us_is_named_when_seen(self, board):
        before = WYW.snapshot(board)
        board.get_marshal("Gneisenau").location = "Rhineland"       # beside Belgium and Lyon
        _see(board, "Rhineland")
        digest = WYW.digest(board, before, None, [])
        beside = digest["beside"]
        assert beside and beside[0]["marshal"] == "Gneisenau" and "next to" in beside[0]["line"]
        _see(board, "Rhineland", "unknown")
        assert WYW.digest(board, before, None, [])["beside"] == []

    def test_the_seam_down_builds_nothing(self, board, monkeypatch):
        monkeypatch.setattr(WYW, "the_turn_is_summed_up", lambda: False)
        assert WYW.snapshot(board) == {} and WYW.digest(board, {"regions": {}}, None, []) == {}

    def test_the_end_of_a_turn_carries_the_digest(self):
        """End to end: the real End Turn hands the digest to the response."""
        import contextlib
        import io

        import backend.main as M
        from backend.commands.parser import CommandParser
        from fastapi.testclient import TestClient
        with contextlib.redirect_stdout(io.StringIO()):
            M._reset_world_state()
            M.parser = CommandParser(use_real_llm=False)
            with TestClient(M.app) as client:
                reply = client.post("/command", json={"command": "end turn"}).json()
                if "while_you_waited" not in reply:
                    reply = client.post("/command", json={"command": "end turn"}).json()
        digest = reply.get("while_you_waited")
        assert isinstance(digest, dict) and "lost" in digest and "quiet" in digest
        for key in ("lost", "gained", "friends_lost", "friends_gained", "battles", "beside", "flash"):
            assert isinstance(digest[key], list), key


# ═════════════════════════════════════════════════════════════════════════════
# 5. The peace table — plain words, and the player's land never given unasked
# ═════════════════════════════════════════════════════════════════════════════

class TestThePeaceTableInPlainWords:
    def test_every_scorer_column_has_a_plain_reason(self):
        assert set(ACCEPTANCE_COMPONENT_PLAIN) == set(ACCEPTANCE_COMPONENT_DISPLAY)
        for reason in ACCEPTANCE_COMPONENT_PLAIN.values():
            assert reason == reason.lower() or "I" in reason
            assert "legitimacy" not in reason and "pressure" not in reason

    def test_the_band_says_what_the_court_will_do(self):
        assert acceptance_band_plain("accept") == "will sign"
        assert acceptance_band_plain("reject") == "will not sign"
        assert acceptance_band_plain("near_acceptable") == "will not sign yet — close"
        assert acceptance_band_plain("nonsense") == ""

    def test_a_row_carries_its_plain_reason_beside_the_column(self):
        from tests.test_settlement_gate4_leg1_fixes import _stage_propose, _winning_two_court_world
        world, _war = _winning_two_court_world()
        dialogue = _stage_propose(world)
        for row in dialogue["per_court_acceptance"]:
            assert "band_plain" in row and row["band_plain"]
            if row.get("top_blocker_display"):
                from backend.display_names import acceptance_component_plain
                assert row["top_blocker_plain"] == acceptance_component_plain(
                    row.get("top_blocker_component"), row.get("top_blocker_detail"))
            else:
                assert row["top_blocker_plain"] == ""

    def test_the_dial_never_gives_the_players_land_unasked(self):
        """The first playtest's Bohemia: three presses of More generous ended
        by ceding the player's province. The dial now stops at gold and ASKS."""
        from backend.game_logic.settlement_preview import handle_settlement_dialogue_action
        from tests.test_settlement_gate4_leg1_fixes import (
            _gold_for, _stage_propose, _strip_to_peace_only, _winning_two_court_world,
        )
        world, _war = _winning_two_court_world(france_gold=0)
        for captured in ("Rhineland", "Waterloo"):
            world.regions[captured].controller = "France"
        world.invalidate_active_nations_cache()
        dialogue = _strip_to_peace_only(world, _stage_propose(world))
        result = handle_settlement_dialogue_action(
            world, action="settlement_dial_generous", dialogue=dialogue,
            action_params={"action": "settlement_dial_generous", "scope": "table"})
        assert result["success"] is True, result.get("error_display")
        new = result["diplomatic_dialogue"]
        terms = new.get("settlement_terms") or []
        assert not [t for t in terms if str(t.get("type") or "").startswith("territory")
                    and t.get("from") == "France"], terms
        assert _gold_for(terms, "France") == 0
        offers = new.get("land_offers") or []
        assert offers, new.keys()
        regions = [row["region"] for row in offers]
        assert len(regions) == len(set(regions)) and set(regions) <= {"Rhineland", "Waterloo"}
        for row in offers:
            assert row["action"] == "settlement_demand_add"
            assert row["action_params"] == {"nation": row["court"], "group": "offer",
                                            "clause_type": "territory_cede", "region": row["region"]}
            assert row["label"].startswith("Offer ") and row["keep_label"].startswith("No — keep ")
            assert "Nothing is given unless you choose it" in row["line"]
        change = new["dial_change"]
        assert change["changed"] is False
        assert change["line"] == "Nothing changed — you have no more gold to offer."

    def test_the_named_button_is_the_tables_own_offer(self):
        """Pressing "Offer <province>" authors exactly the clause a deliberate
        click on the court's own row would."""
        from backend.game_logic.settlement_preview import handle_settlement_dialogue_action
        from tests.test_settlement_gate4_leg1_fixes import (
            _stage_propose, _strip_to_peace_only, _winning_two_court_world,
        )
        world, _war = _winning_two_court_world(france_gold=0)
        for captured in ("Rhineland", "Waterloo"):
            world.regions[captured].controller = "France"
        world.invalidate_active_nations_cache()
        dialogue = _strip_to_peace_only(world, _stage_propose(world))
        eased = handle_settlement_dialogue_action(
            world, action="settlement_dial_generous", dialogue=dialogue,
            action_params={"action": "settlement_dial_generous", "scope": "table"})
        offer = eased["diplomatic_dialogue"]["land_offers"][0]
        pressed = handle_settlement_dialogue_action(
            world, action=offer["action"], dialogue=eased["diplomatic_dialogue"],
            action_params={"action": offer["action"], **offer["action_params"]})
        assert pressed["success"] is True, pressed.get("error_display")
        terms = pressed["diplomatic_dialogue"]["settlement_terms"]
        assert any(t.get("type") == "territory_cede" and t.get("from") == "France"
                   and t.get("to") == offer["court"] and t.get("region") == offer["region"]
                   for t in terms), terms

    def test_the_seam_down_is_the_old_escalation(self, monkeypatch):
        from backend.game_logic import settlement_actions
        from backend.game_logic.settlement_preview import handle_settlement_dialogue_action
        from tests.test_settlement_gate4_leg1_fixes import (
            _stage_propose, _strip_to_peace_only, _winning_two_court_world,
        )
        monkeypatch.setattr(settlement_actions, "the_dial_never_gives_land_unasked", lambda: False)
        world, _war = _winning_two_court_world(france_gold=0)
        for captured in ("Rhineland", "Waterloo"):
            world.regions[captured].controller = "France"
        world.invalidate_active_nations_cache()
        dialogue = _strip_to_peace_only(world, _stage_propose(world))
        result = handle_settlement_dialogue_action(
            world, action="settlement_dial_generous", dialogue=dialogue,
            action_params={"action": "settlement_dial_generous", "scope": "table"})
        terms = result["diplomatic_dialogue"]["settlement_terms"]
        assert [t for t in terms if str(t.get("type") or "").startswith("territory")
                and t.get("from") == "France"]
        assert not result["diplomatic_dialogue"].get("land_offers")

    def test_a_press_says_what_it_changed(self):
        from backend.game_logic.settlement_actions import dial_change_line
        world = WorldState()
        before = [{"type": "peace"},
                  {"type": "gold_indemnity", "from": "France", "to": "Prussia", "amount": 825}]
        after = [{"type": "peace"},
                 {"type": "gold_indemnity", "from": "France", "to": "Prussia", "amount": 925}]
        change = dial_change_line(world, before, after, direction="generous", proposer_leader="France")
        assert change == {"changed": True, "parts": ["gold you pay Prussia 825 → 925"],
                          "line": "Changed: gold you pay Prussia 825 → 925."}
        added = dial_change_line(world, [{"type": "peace"}],
                                 [{"type": "peace"},
                                  {"type": "gold_indemnity", "from": "Britain", "to": "France", "amount": 100}],
                                 direction="harsher", proposer_leader="France")
        assert added["line"] == "Changed: added gold Britain pays you (100)."
        none = dial_change_line(world, before, before, direction="harsher", proposer_leader="France")
        assert none["changed"] is False and none["line"].startswith("Nothing changed — ")

    def test_this_deal_reads_the_packages_own_terms(self):
        from backend.game_logic.settlement_staging import settlement_plain_deal
        from tests.test_settlement_gate4_leg1_fixes import _stage_propose, _winning_two_court_world
        world, war = _winning_two_court_world()
        dialogue = _stage_propose(world)
        deal = dialogue["plain_deal"]
        assert set(deal) >= {"get", "give", "keep", "allies_keep", "allies_hand_back",
                             "they_keep", "still_at_war", "with"}
        terms = [{"type": "peace"},
                 {"type": "gold_indemnity", "from": "Britain", "to": "France", "amount": 400},
                 {"type": "gold_indemnity", "from": "France", "to": "Prussia", "amount": 150},
                 {"type": "territory_cede", "from": "Prussia", "to": "France", "region": "Rhineland"}]
        deal = settlement_plain_deal(world, war, "attackers", ["Britain", "Prussia"], terms,
                                     dialogue["per_court_acceptance"], player="France")
        assert deal["get"] == ["400 gold from Britain", "Rhineland from Prussia"]
        assert deal["give"] == ["150 gold to Prussia"]
        assert deal["still_at_war"] == []
        left_out = settlement_plain_deal(world, war, "attackers", ["Britain"], terms[:2],
                                         dialogue["per_court_acceptance"], player="France")
        assert left_out["still_at_war"] == ["Prussia"]

    def test_the_client_wears_the_plain_faces(self):
        popup = _src(SCRIPTS / "proposal_confirm_popup.gd")
        for action, face in (("settlement_dial_harsher", "Ask for more"),
                             ("settlement_dial_generous", "Offer them more"),
                             ("submit_settlement_for_review", "Review and sign"),
                             ("suspend_settlement_editor", "Cancel"),
                             ("confirm_settlement", "Sign the peace")):
            assert re.search(rf'"{action}": \["{re.escape(face)}"', popup), action
        tiles = _func(popup, "_verdict_tiles")
        assert '"They will sign" if can else "They will not sign yet"' in tiles
        assert '"Will carry"' not in _code(tiles) and "hold out" not in _code(tiles)
        short = _func(popup, "_short_face")
        for face in ('"Ask more"', '"Offer more"', '"Leave out"'):
            assert face in short
        deal = _func(popup, "_pw_this_deal_bbcode")
        for head in ("THIS DEAL", "You get:", "You give:", "You keep:", "hands back:",
                     "Still at war after this:"):
            assert head in deal, head
        answer = _func(popup, "_pw_land_answer")
        assert 'row["kept"] = true' in answer and "_emit_settlement_action" in answer

    def test_the_table_stays_on_the_screen_through_a_press(self):
        popup = _src(SCRIPTS / "proposal_confirm_popup.gd")
        stay = _func(popup, "_stay_for_restage")
        assert "STAYS_THROUGH.has(action)" in stay and "_find_safe_exit_action()" in stay
        for handler in ("_on_option_selected", "_on_settlement_tier2_affordance", "_emit_settlement_action"):
            body = _func(popup, handler)
            assert "_stay_for_restage(" in body and "_restaging" in body, handler
        hold = _func(popup, "_hold_document")
        assert 'panel.offset_top = float(held["top"])' in hold
        assert "restage_answered" in _src(SCRIPTS / "main.gd")


class TestThePeaceForecastIsWhatThePeaceDoes:
    def test_an_allys_occupation_is_forecast_as_handed_back(self, monkeypatch):
        """Shown == applied: `status_quo_forecast` reads T3-6 for every holder
        against its OWN pair, as the retention pass applies it."""
        from backend.game_logic import game_end

        calls = []

        def fake_evacuations(world, a, b, holder_leader, ceder, kept):
            calls.append((a, b, holder_leader, ceder))
            if holder_leader == "Bavaria":
                return {}, {"Bavaria": list(kept.get("Bavaria") or [])}
            return kept, {}

        monkeypatch.setattr(game_end, "status_quo_retentions",
                            lambda world, leader, ceder, forecast=False: (
                                {"France": ["Bohemia"], "Bavaria": ["Moravia", "Vienna"]}
                                if leader == "France" else {}))
        monkeypatch.setattr(game_end, "ally_homeland_returns", lambda world, leader, ceder: {})
        monkeypatch.setattr(game_end, "homeland_returns",
                            lambda world, leader, ceder, kept: (kept, {}))
        monkeypatch.setattr(game_end, "aim_evacuations", fake_evacuations)
        world = WorldState()
        entries = game_end.status_quo_forecast(world, "France", "Austria")
        entry = next(e for e in entries if e["ceder"] == "Austria")
        assert entry["titled"] == {"France": ["Bohemia"]}
        assert entry["returned"]["Austria"] == ["Moravia", "Vienna"]
        assert entry["evacuated"] == {"Bavaria": ["Moravia", "Vienna"]}
        # each holder was read against its own pair with the ceder
        assert ("Bavaria", "Austria", "Bavaria", "Austria") in calls
        assert ("France", "Austria", "France", "Austria") in calls
        lines = game_end.status_quo_summary_lines(world, [entry], "France")
        assert any(line.startswith("Moravia and Vienna go back to Austria: Bavaria only occupied them")
                   for line in lines), lines

    def test_the_seam_down_keeps_the_old_forecast(self, monkeypatch):
        from backend.game_logic import game_end
        monkeypatch.setattr(game_end, "the_forecast_reads_each_holders_own_peace", lambda: False)
        monkeypatch.setattr(game_end, "status_quo_retentions",
                            lambda world, leader, ceder, forecast=False: (
                                {"Bavaria": ["Vienna"]} if leader == "France" else {}))
        monkeypatch.setattr(game_end, "ally_homeland_returns", lambda world, leader, ceder: {})
        monkeypatch.setattr(game_end, "homeland_returns",
                            lambda world, leader, ceder, kept: (kept, {}))
        entries = game_end.status_quo_forecast(WorldState(), "France", "Austria")
        assert entries[0]["titled"] == {"Bavaria": ["Vienna"]} and "evacuated" not in entries[0]


# ═════════════════════════════════════════════════════════════════════════════
# 6. Battles — the day in everyday words
# ═════════════════════════════════════════════════════════════════════════════

class TestTheOddsSaidPlainly:
    def test_one_table_for_every_surface(self):
        assert set(ODDS_PLAIN) == {"favorable", "even", "unfavorable"}
        assert odds_plain("unfavorable") == "odds bad — you will probably lose"
        assert odds_plain("") == "" and odds_plain(None) == ""
        utils = _src(SCRIPTS / "utils.gd")
        assert "ODDS_PLAIN" not in utils          # the client holds no copy

    def test_the_attack_quotes_force_block_says_what_to_expect(self, board):
        ney = board.get_marshal("Ney")
        wellington = board.get_marshal("Wellington")
        _see(board, "Waterloo")
        quote = Q.attack_quote(board, ney, wellington)
        assert quote["kind"] == "attack"
        force = quote.get("force") or {}
        assert force.get("expect") == odds_plain(force.get("odds"))
        assert quote["tag"] == ([force["expect"]] if force.get("expect") else [])


class TestTheDayInPlainWords:
    DAY = {"side": "attack", "toll": {"ours": 10837, "his": 9559}, "clashes": 2, "open": True}

    def _chip(self, kind, label, **extra):
        chip = {"kind": kind, "label": label, "price": 1, "command": "", "word": "",
                "ok": True, "why": "", "counsel": "none", "odds": "", "marshal": "Massena",
                "shown": "Massena", "does": "x", "more": "y", "risk": "z"}
        chip.update(extra)
        return chip

    def test_an_attack_says_the_men_and_what_to_expect(self):
        chip = self._chip("press", "Massena presses",
                          _force={"ours": 31163, "theirs_low": 44441, "theirs_high": 44441,
                                  "odds": "unfavorable"})
        T.speak_plainly(chip, self.DAY, lead_shown="Massena")
        assert chip["label"] == "Attack again"
        assert chip["does"] == "31,163 men against 44,441"
        assert chip["risk"] == "odds bad — you will probably lose"
        assert "_force" not in chip
        riposte = self._chip("press", "Massena strikes back", _force={})
        T.speak_plainly(riposte, dict(self.DAY, side="defence"), lead_shown="Massena")
        assert riposte["label"] == "Counter-attack"

    def test_the_other_orders_wear_their_plain_names(self):
        cases = [
            (self._chip("guard", "The Guard", _force={}), "Send in the Guard"),
            (self._chip("lead", "Ney leads", shown="Ney", _force={}), "Attack with Ney"),
            (self._chip("cannonade", "Drouot's guns", shown="Drouot", _force={}), "Bombard with Drouot's guns"),
            (self._chip("dig_in", "Massena digs in", does="defensive stance: +9% if he strikes"), "Dig in"),
            (self._chip("stand", "Massena stands", word="stand", does="he speaks next — he may strike",
                        _reading="may"), "Wait"),
            (self._chip("stand", "Leave it to Massena", word="leave_it", does="he may press"),
             "Let Massena decide"),
            (self._chip("break_off", "Break off", word="break_off"), "Withdraw"),
            (self._chip("break_off", "Fall back", command="Massena, retreat"), "Retreat"),
        ]
        said = {}
        for chip, label in cases:
            T.speak_plainly(chip, self.DAY, lead_shown="Massena")
            assert chip["label"] == label
            said[label] = chip
        assert said["Dig in"]["does"] == "+9% defence if he attacks"
        assert said["Dig in"]["risk"] == "he moves next — this helps only if he attacks"
        assert said["Wait"]["does"] == "he moves next — he may attack"
        assert said["Let Massena decide"]["does"] == "he will probably attack"
        assert said["Withdraw"]["does"] == ("the battle ends; he keeps the province; "
                                            "losses so far: you 10,837 · him 9,559")
        assert said["Retreat"]["does"].startswith("the battle ends; he takes the province")
        for chip in said.values():
            for line in (chip["label"], chip["does"], chip.get("risk", ""), chip.get("more", "")):
                for idiom in ("speaks next", "the toll", "strikes", "a word costs", "presses"):
                    assert idiom not in line, (chip["label"], line)

    def test_the_seam_down_leaves_a_chip_as_it_was(self, monkeypatch):
        monkeypatch.setattr(T, "the_day_speaks_plainly", lambda: False)
        chip = self._chip("press", "Massena presses", _force={"ours": 1}, _reading="may")
        was = {k: v for k, v in chip.items() if not k.startswith("_")}
        T.speak_plainly(chip, self.DAY, lead_shown="Massena")
        assert chip == was

    def test_the_headline_and_the_line_under_it(self):
        assert T.plain_banner("The day hangs") == "No winner yet"
        assert T.plain_banner("Night falls") == "Night — no winner"
        assert T.plain_banner("Mack draws off") == "Mack withdraws"
        assert T.plain_so_far(self.DAY) == "Losses so far: you 10,837 · him 9,559 — about even."
        closed = dict(self.DAY, open=False, toll={"ours": 2000, "his": 9000})
        assert T.plain_so_far(closed) == "Losses: you 2,000 · him 9,000 — you have lost fewer."
        assert T.plain_so_far({"clashes": 0}) == ""

    def test_what_told_in_everyday_words(self):
        for idiom, plain in (
                ("our weight of numbers told", "you had more men"),
                ("his weight of numbers told", "he had more men"),
                ("the ground told for us", "the ground helped you"),
                ("the dice told for him", "the dice ran his way"),
                ("his dug-in line told", "his dug-in line helped him"),
                ("our exhaustion told against us", "your exhaustion hurt you"),
                ("the ground told against his horse", "the ground hurt his horse"),
                ("an even fight", "an even fight")):
            assert T.plain_told(idiom) == plain
        assert T.verdict_line("our weight of numbers told") == "You had more men."

    def test_why_names_the_men_the_advantages_and_the_dice(self):
        class Ctx:
            battle_result = {
                "modifier_snapshot": {
                    "attacker": [{"label": "Drill training", "value": 10, "type": "bonus"},
                                 {"label": "Exhaustion", "value": 3, "type": "penalty"}],
                    "defender": [{"label": "Fortified position", "value": 15, "type": "bonus"}],
                },
                "attacker_roll": {"natural": 3},
            }
            pre_battle_attacker_strength = 12000
            pre_battle_defender_strength = 25000
            marshal = None
            enemy_marshal = None
            atk_participants = []
            def_participants = []
            _bd_pre_strengths = {}

        why = T.why_plain(Ctx(), True)
        assert why[0] == "he had more men — 25,000 against your 12,000"
        assert "your drill training +10%" in why
        assert "his fortified position +15%" in why
        assert not any("exhaustion" in line for line in why)        # under five points: not named
        assert why[-1] == "the dice ran his way (the attacker threw 3 of 12)"

    def test_the_tables_captions_follow_the_block(self):
        acts = _src(SCRIPTS / "battle_acts.gd")
        assert 'return said if said != "" else DAY_RULE' in _func(acts, "_day_rule")
        assert "DAY_GROUP_LABEL_PLAIN" in _func(acts, "_day_group_label")
        assert '"Expect: " if _day_is_plain() else "It risks: "' in acts
        assert T.PLAIN_RULE.startswith("Each order costs battle points")


# ═════════════════════════════════════════════════════════════════════════════
# 7. The client's hands — clicking, sending, the windows that stand still
# ═════════════════════════════════════════════════════════════════════════════

class TestTheClientsHands:
    MAP = _src(SCENES / "map_renderer_base.gd")
    MAIN = _src(SCRIPTS / "main.gd")

    def test_a_piece_is_picked_from_near_it(self):
        assert "const PIECE_GRAB_PX := 30.0" in self.MAP
        pick = _func(self.MAP, "pick_piece_near")
        assert "reach" in pick and "distance" in pick.lower()
        hover = _func(self.MAP, "_refresh_hover_state")
        assert "pick_piece_near(marshal_hitboxes, map_mouse, _piece_grab_world())" in hover

    def test_a_stacks_label_asks_which_corps(self):
        assert "signal stack_clicked(region_name: String, marshal_names: Array, at: Vector2)" in self.MAP
        picker = _src(SCRIPTS / "stack_picker.gd")
        assert "signal picked(marshal_key: String)" in picker
        assert "Engine.get_process_frames() == _opened_frame" in _func(picker, "_on_catch_input")
        assert "_stack_picker.open_list(region, rows, at)" in _func(self.MAIN, "_on_stack_clicked")

    def test_one_click_sends_what_asks_nothing(self):
        go = _func(self.MAIN, "_order_go")
        assert 'UiSettings.get_confirm_every_order() or not key.begins_with("dest:")' in go
        send = _func(self.MAIN, "_order_go_with")
        assert 'quote.has("confirm") and not bool(quote.get("confirm"))' in send
        assert "_pw_send_and_keep_him(command)" in send
        keep = _func(self.MAIN, "_pw_send_and_keep_him")
        assert "_card_sent_stays = true" in keep
        settings = _src(SCRIPTS / "ui_settings.gd")
        assert '"confirm_every_order", harness_active()' in _func(settings, "get_confirm_every_order")
        assert '"next_marshal_after_order", false' in _func(settings, "get_next_marshal_after_order")

    def test_the_tag_names_the_place_and_carries_the_backends_lines(self):
        label = _func(self.MAIN, "_order_ghost_label")
        assert 'var tag = q.get("tag", [])' in label
        assert 'head = named + " — " + head' in label
        assert '"Move" if kind == "move"' in label and '"arrives now"' in label
        assert " AP" not in label
        draw = _func(self.MAP, "_draw")
        assert "order_selected != \"\" and _order_ghost_set and hovered_region != \"\"" in draw

    def test_the_hover_box_stays_whole_and_clear_of_the_tag(self):
        layer = _src(SCENES / "map_tooltip_layer.gd")
        clamp = _func(layer, "clamp_box")
        assert "if pos.y < top_floor:" in clamp and "pos.x = maxf(pos.x, left_floor)" in clamp
        assert "intersects(avoid)" in _func(layer, "clear_of")

    def test_the_selection_card_stands_clear_of_the_map(self):
        dock = _func(self.MAIN, "_pw_dock_card_beside_the_window")
        assert "bottom_left_ui.get_global_rect()" in dock
        fit = _func(self.MAIN, "_fit_order_strip")
        assert "_pw_dock_card_beside_the_window(surface)" in fit

    def test_the_end_of_turn_asks_about_ground_that_can_be_taken(self):
        takers = _func(self.MAIN, "_pw_takers")
        assert 'bool(stands.get("open", false)) or code == "fort"' in takers
        assert "_pw_take_warning_stands()" in self.MAIN and '"pwtake:"' in self.MAIN

    def test_a_window_opens_once_at_the_size_it_keeps(self):
        utils = _src(SCRIPTS / "utils.gd")
        assert "const MOTION_HOLD_FRAMES := 4" in utils
        fade = _func(utils, "_fade_in_after_the_fit")
        assert "range(MOTION_HOLD_FRAMES)" in fade and "process_frame" in fade
        card = _func(self.MAIN, "_open_order_card")
        assert "_order_card_wait = key" in card and "ORDER_CARD_WAIT_SEC" in card

    def test_the_report_opens_on_what_changed_for_the_player(self):
        dialog = _src(SCRIPTS / "enemy_phase_dialog.gd")
        block = _func(dialog, "_wyw_block")
        for head in ("WHAT CHANGED FOR YOU", "You lost", "You gained", "Your allies",
                     "Your battles", "Now next to you"):
            assert head in block, head
        assert "Everything else that happened" in _func(dialog, "_render_phase")
        assert "_pw_say_the_digest(" in _func(self.MAIN, "_pw_after_the_report")
        assert "map_area.flash_regions(flash)" in _func(self.MAIN, "_pw_say_the_digest")
        assert "KEEP_IT_LINE" in _src(SCRIPTS / "capture_choice_dialog.gd")

    def test_a_war_card_says_how_it_stands_and_ends_it(self):
        panel = _src(SCRIPTS / "war_status_panel.gd")
        word = _func(panel, "war_standing_word")
        for said in ('"Winning"', '"Losing"', '"Even"'):
            assert said in word
        assert 'peace_btn.text = "Make peace"' in panel
        assert "_on_war_settlement_clicked(war_id, nation)" in _func(self.MAIN, "_on_war_card_peace")
        detail = _src(SCRIPTS / "war_detail_popup.gd")
        assert 'const MAKE_PEACE := "Make peace"' in detail
        assert '"Open Settlement"' not in _code(detail) and '"Request Terms"' not in _code(detail)


# ═════════════════════════════════════════════════════════════════════════════
# 9. What the real client showed (found pressing it at the player's own setup)
# ═════════════════════════════════════════════════════════════════════════════

class TestTheCabinetSaysHowToEndAWar:
    """ "its unclear how to end wars": four peace acts under four names of the
    trade and a verdict that read "Hopeless"."""

    def _rows(self):
        import contextlib
        import io

        from backend.game_logic import diplomacy as D
        world = WorldState()                       # France at war with Britain and Prussia
        with contextlib.redirect_stdout(io.StringIO()):
            return world, D.get_diplomatic_preview(world, "Prussia")["actions"]

    def test_every_peace_row_says_what_it_is_and_does(self):
        _world, rows = self._rows()
        peace = [r for r in rows if r.get("group") == "peace"]
        assert {r["action"] for r in peace} >= {"open_settlement", "propose_white_peace",
                                               "propose_peace", "propose_armistice"}
        for row in peace:
            assert row["plain_name"] and row["plain_line"], row["action"]
            # the names every pin and the counsel read are untouched beside them
            assert row["display_name"] and row["display_name"] != row["plain_name"]
        by = {r["action"]: r for r in peace}
        assert by["open_settlement"]["plain_name"].startswith("Make peace — choose the terms")
        assert by["propose_white_peace"]["plain_name"].startswith("Make peace with no terms")
        assert by["propose_peace"]["plain_name"] == "Offer peace to Prussia alone"
        assert by["propose_armistice"]["plain_name"] == "Ask for a truce"
        # (row PW part 2, the review: a truce becomes a peace at its end, or the war starts again)
        assert "When the truce runs out it becomes a peace" in by["propose_armistice"]["plain_line"]
        assert "{" not in by["propose_armistice"]["plain_line"], "the truce's length is filled from its constant"
        # no other row is in the group
        assert not [r for r in rows if r.get("group") == "peace" and not r["action"].startswith(
            ("open_settlement", "propose_"))]

    def test_every_verdict_word_says_what_the_court_will_do(self):
        from backend.display_names import LIKELIHOOD_PLAIN, likelihood_plain
        from backend.game_logic.diplomacy import get_likelihood_descriptor
        words = {get_likelihood_descriptor(score, counter) for score in range(-20, 101, 5)
                 for counter in (None, False)}
        assert words <= set(LIKELIHOOD_PLAIN), words - set(LIKELIHOOD_PLAIN)
        assert likelihood_plain("Hopeless") == "They will refuse"
        assert likelihood_plain("Almost Certain") == "They will accept"
        _world, rows = self._rows()
        said = [r for r in rows if r.get("likelihood")]
        assert said and all(r.get("likelihood_plain") == likelihood_plain(r["likelihood"]) for r in said)

    def test_the_seam_down_leaves_the_rows_as_they_were(self, monkeypatch):
        from backend.game_logic import cabinet_rows
        monkeypatch.setattr(cabinet_rows, "the_cabinet_says_peace_plainly", lambda: False)
        _world, rows = self._rows()
        assert not [r for r in rows if "plain_name" in r or "group" in r or "likelihood_plain" in r]

    def test_the_client_sets_the_group_first_under_its_heading(self):
        wizard = _src(SCRIPTS / "diplomacy_wizard.gd")
        assert 'const PEACE_HEADING := "END THE WAR"' in wizard
        assert ('const PEACE_ROW_RANK := {"open_settlement": 0, "propose_white_peace": 1, '
                '"propose_peace": 2, "propose_armistice": 3}') in wizard
        button = _func(wizard, "_add_action_button")
        assert 'str(action.get("plain_name", ""))' in button and 'str(action.get("plain_line", ""))' in button
        # the badge's tone is still keyed by the trade's word
        assert "_verdict_tone(tone_word if tone_word != \"\" else verdict)" in button


class TestThePeaceTableAfterTheRealClient:
    def test_the_why_is_honest_when_nothing_is_asked(self):
        """A draft that asked NOTHING was told "you ask for more than you have
        won": the legitimacy column also stands low when the war itself has
        decided nothing (its tier's base), and only its MISMATCH is an
        overreach."""
        from backend.display_names import acceptance_component_plain
        assert acceptance_component_plain("settlement_tier_legitimacy", "tier_mismatch") \
            == "you ask more than you have won"
        assert acceptance_component_plain("settlement_tier_legitimacy", "tier_base") \
            == "the war has decided nothing yet"
        assert acceptance_component_plain("concession_credit") == "you offer them too little"
        for words in ACCEPTANCE_COMPONENT_PLAIN.values():
            assert len(words) <= 37, words          # the court row's "Why:" shows it whole

    def test_a_press_that_changes_nothing_shuts_its_button_with_the_reason(self):
        from backend.game_logic.settlement_actions import dial_change_line
        from backend.game_logic.settlement_preview import handle_settlement_dialogue_action
        from tests.test_settlement_gate4_leg1_fixes import (
            _stage_propose, _strip_to_peace_only, _winning_two_court_world,
        )
        nothing = dial_change_line(WorldState(), [{"type": "peace"}], [{"type": "peace"}],
                                   direction="generous", proposer_leader="France", no_gold=True)
        assert nothing["changed"] is False and nothing["why"] == "you have no more gold to offer"
        # end to end: France with an empty purse and no land to offer presses the dial
        world, _war = _winning_two_court_world(france_gold=0)
        dialogue = _strip_to_peace_only(world, _stage_propose(world))
        result = handle_settlement_dialogue_action(
            world, action="settlement_dial_generous", dialogue=dialogue,
            action_params={"action": "settlement_dial_generous", "scope": "table"})
        assert result["success"] is True, result.get("error_display")
        new = result["diplomatic_dialogue"]
        if not (new.get("dial_change") or {}).get("changed", True):
            assert new["dial_dead"] == {"table:generous": new["dial_change"]["why"]}
            assert new["dial_change"]["line"].startswith("Nothing changed — ")
        popup = _src(SCRIPTS / "proposal_confirm_popup.gd")
        dead = _func(popup, "_pw_dial_dead_reason")
        assert 'current_data.get("dial_dead", {})' in dead
        assert 'disabled_reason = "Nothing more to change — " + dead_why + "."' in popup

    def test_what_a_signed_peace_did_is_said_as_the_table_said_it(self):
        from backend.game_logic.settlement_staging import settlement_plain_result
        deal = {"with": ["Austria"], "get": ["37 gold a turn from Austria for 10 turns"], "give": [],
                "keep": ["Bohemia", "Croatia"], "allies_keep": [],
                "allies_hand_back": [{"ally": "Bavaria", "ally_display": "Bavaria", "to": "Austria",
                                      "to_display": "Austria", "regions": ["Moravia", "Vienna"], "claims": []}],
                "they_keep": [], "still_at_war": ["Britain", "Russia"]}
        told = settlement_plain_result(deal)
        assert told["head"] == "Peace signed with Austria."
        assert told["lines"] == [
            "You got: 37 gold a turn from Austria for 10 turns.",
            "You gave: nothing.",
            "You keep: Bohemia and Croatia.",
            "Bavaria handed back Moravia and Vienna to Austria: it only occupied them, "
            "and the treaty did not award them.",
            "Still at war with Britain and Russia.",
        ]
        assert told["toast"] == "Peace signed with Austria. Still at war with Britain and Russia."
        assert settlement_plain_result({}) == {}
        over = settlement_plain_result({"with": ["Prussia"], "get": [], "give": [], "still_at_war": []})
        assert over["lines"][-1] == "That war is over."
        ratify = _src(REPO / "backend" / "game_logic" / "settlement_ratify.py")
        assert '"plain": _plain_result_of(dialogue),' in ratify
        main = _func(_src(SCRIPTS / "main.gd"), "_display_settlement_result_feedback")
        assert 'feedback.get("plain", {})' in main and "ToastLayer.say(said" in main

    def test_the_tables_own_sentences_are_printed_in_the_buttons_words(self):
        popup = _src(SCRIPTS / "proposal_confirm_popup.gd")
        for old, new in (("Will NOT carry as drafted", "They will not sign this"),
                         ("Holding out:", "Refusing:"),
                         ("More generous", "Offer them more"),
                         ("Submit for Review", "Review and sign")):
            assert f'["{old}", "{new}"]' in popup, old
        arrive = _func(popup, "_pw_plain_table_strings")
        for key in ("propose_carry_hint", "ratify_blocked_reason", "carry_verdict_display", "summary_display"):
            assert f'"{key}"' in arrive, key
        assert "_pw_plain_table_strings(current_data)" in _func(popup, "show_dialogue")
        head = _func(popup, "_verdict_heading_words")
        assert 'return "They will not sign this yet."' in head
        for said in re.findall(r'return "([^"]*)"', head):
            assert "ratif" not in said.lower() and "carry" not in said.lower(), said
        tiles = _func(popup, "_verdict_tiles")
        for caption in ('"Gold you offer"', '"In your treasury"', '"Left if they sign"'):
            assert caption in tiles
        assert "The reserve is never offered" not in tiles

    def test_the_draft_and_the_first_line_name_the_buttons_as_they_read(self):
        from backend.display_names import settlement_draft_words
        from backend.game_logic import first_open
        assert "Make peace" in settlement_draft_words("badge") and "Make peace" in settlement_draft_words("reply")
        assert "Open Settlement" not in settlement_draft_words("badge")
        line = first_open._line_settlement(WorldState(), {"mode": "PROPOSE"})
        assert line.startswith("This is the table, Sire. Every court seated here signs for itself")
        assert "Ask more of a court, offer it more, or leave it out" in line and "carry" not in line


class TestTheBattleAndTheReportAfterTheRealClient:
    def test_the_notice_and_the_first_line_of_a_day_are_plain(self):
        from backend.game_logic import first_open
        line = first_open._line_battle_day(WorldState())
        assert line.startswith("No winner yet, Sire.") and "battle points" in line
        assert len(line) <= first_open.LINE_CAP, len(line)
        # the day's four ends, as `battle_day._spent` rules them (the review, PW-R11)
        for end in ("an army breaks", "someone withdraws", "two turns pass with no order", "the points run out"):
            assert end in line, end
        assert "all the points are spent" in T.PLAIN_RULE and "two turns in a row with no order" in T.PLAIN_RULE
        assert T.PLAIN_READ == {"will": "he will attack", "may": "he may attack",
                                "will_not": "he will not attack"}
        day = _src(REPO / "backend" / "game_logic" / "battle_day.py")
        assert 'title = f"Battle at {_place(world, day.get(\'field\'))}: no winner yet"' in day
        assert "The battle waits for your " in day
        acts = _src(SCRIPTS / "battle_acts.gd")
        # (row PW part 2: the two lines became sentences — `plain_lands`, `plain_luck`)
        assert "lands = BattleActs.plain_lands(100 + int(roll.get(\"swing\", 0)), AVERAGE_LANDS)" in acts
        assert 'return "a strong roll: the attack hits %d%% harder than an average one" % diff' in acts
        assert 'return "a weak roll: the attack hits %d%% weaker than an average one" % -diff' in acts
        assert 'return "an average roll: the attack hits as hard as usual"' in acts
        assert 'return "today\'s luck: %s · %s" % [' in acts
        assert "static func payload_is_plain(data) -> bool:" in acts
        assert 'details["review_label"] = "Give your orders"' in _src(SCRIPTS / "notification_bar.gd")

    def test_the_seam_down_keeps_the_days_old_words(self, monkeypatch):
        from backend.game_logic import first_open
        monkeypatch.setattr(T, "the_day_speaks_plainly", lambda: False)
        assert first_open._line_battle_day(WorldState()).startswith("The day hangs, Sire.")

    def test_an_enemy_on_our_corps_ground_is_said_to_be_there(self, board):
        before = WYW.snapshot(board)
        ney = board.get_marshal("Ney")
        wellington = board.get_marshal("Wellington")
        wellington.location = ney.location
        _see(board, ney.location)
        rows = WYW._now_beside(board, before)
        line = next(r["line"] for r in rows if r["marshal"] == "Wellington")
        if board.get_region(ney.location).controller != board.player_nation or True:
            assert line == f"Wellington is in {ney.location}, where your corps stands."

    def test_the_digests_two_steps_are_the_end_turn_commands(self):
        assert WYW.before(WorldState(), True) == {}          # a resumed close has no honest "before"
        result: dict = {}
        WYW.attach(result, WorldState(), {}, None, [])
        assert result == {}                                   # nothing to compare with: nothing said
        meta = _src(REPO / "backend" / "commands" / "meta_executor.py")
        assert "_while_you_waited.before(" in meta and "_while_you_waited.attach(turn_result, world" in meta
        # ...and the turn's own function (at the 500-line ratchet) is untouched
        assert "while_you_waited" not in _src(REPO / "backend" / "game_logic" / "turn_manager.py")

    def test_the_war_card_is_as_tall_as_its_two_lines(self):
        panel = _src(SCRIPTS / "war_status_panel.gd")
        entry = _func(panel, "_add_war_entry")
        assert "row_btn.custom_minimum_size.y = maxf(50.0, col.get_combined_minimum_size().y + 6.0)" in entry
        assert 'if glyph != "" and glyph != "→":' in entry


# ═════════════════════════════════════════════════════════════════════════════
# 10. The session's one review (three Sonnet readers by lane; `BUG_FIXES.md` §PW)
# ═════════════════════════════════════════════════════════════════════════════

class TestTheReviewTheOrdersLane:
    def test_pw_r1_the_works_are_named_only_at_full_sight(self, board):
        """Fog: a foreign province's buildings are FULL-only. The tag by the
        cursor said "the province is fortified" over a province read in part."""
        board.get_region("Rhineland").buildings.append(dict(FORT))
        grouchy = board.get_marshal("Grouchy")
        assert ground.entering(board, grouchy, "Rhineland")["code"] == "fort"      # FULL sight
        _see(board, "Rhineland", PARTIAL)
        reading = ground.entering(board, grouchy, "Rhineland")
        assert reading["code"] == "takes_if_open" and "fortif" not in reading["line"]

    def test_pw_r2_the_garrison_is_read_before_the_works(self, board):
        """The order storms the garrison first and lays the siege after: where
        both stand the remedy is "Storm", as `standing` reads it."""
        region = board.get_region("Rhineland")
        region.buildings.append(dict(FORT))
        region.garrison_strength = 9000
        grouchy = board.get_marshal("Grouchy")
        reading = ground.entering(board, grouchy, "Rhineland")
        assert reading["code"] == "garrison" and reading["remedy_label"] == "Storm Rhineland"
        quote = Q.take_quote(board, grouchy, "Rhineland")
        assert quote["ok"] is True and "lays siege" not in str(quote.get("note") or "")

    def test_pw_r3_the_take_order_asks_the_sea(self):
        source = _src(REPO / "backend" / "commands" / "order_quotes.py")
        take = source[source.index("def take_quote("):source.index("def march_quote(")]
        assert "crossing_check_reach(world, marshal.nation, here, name, int(marshal.strength))" in take
        assert take.index("crossing_check_reach(") < take.index('_state_refusal(world, marshal, "attack", None)')

    def test_pw_r4_the_take_order_does_what_its_chip_says_in_recovery(self, board):
        """Not upheld as a defect of the chip: the attack road takes an open
        province for a corps in its recovery window too (the walk-in does not —
        FA-9's rule, older than row PW). The chip and the order agree."""
        from backend.commands.executor import CommandExecutor
        from backend.commands.parser import CommandParser
        grouchy = board.get_marshal("Grouchy")
        grouchy.location = "Rhineland"
        grouchy.retreat_recovery = 2
        assert ground.standing(board, grouchy)["code"] == "open"
        parsed = CommandParser(use_real_llm=False).parse("Grouchy, attack Rhineland")
        CommandExecutor().execute(parsed, {"world": board})
        assert board.get_region("Rhineland").controller == "France"

    def test_pw_r5_who_held_it_is_said_only_of_the_players_own_province(self, board):
        """An ally's or an enemy's province: who marched in, and no more —
        "nobody was holding it" there was a guess."""
        before = WYW.snapshot(board)
        before["corps"].pop("Rhineland", None)
        cause = WYW._cause(board, before, "Rhineland", "Prussia", "Britain",
                           [{"type": "conquest", "region": "Rhineland", "marshal": "Wellington"}])
        assert cause["how"] == "walked_in" and "nobody was holding it" not in cause["words"]
        own = WYW._cause(board, dict(before, corps={}, garrisons={"Belgium": 0}), "Belgium", "France", "Britain",
                         [{"type": "conquest", "region": "Belgium", "marshal": "Wellington"}])
        assert own["words"].endswith("marched in; nobody was holding it")

    def test_pw_r6_a_treaty_is_named_only_where_a_war_ended(self, board):
        before = WYW.snapshot(board)
        assert board._make_diplo_key("France", "Prussia") in before["wars"]
        # Austria and Prussia were never at war: a change of hands between them
        # with no event names no cause
        quiet = WYW._cause(board, before, "Rhineland", "Prussia", "Austria", [])
        assert quiet == {"how": "", "by": "", "words": ""}
        # France and Prussia were at war as the turn ended and are at peace now
        from backend.game_logic.diplomacy import set_diplomatic_state
        set_diplomatic_state(board, "France", "Prussia", "PEACE")
        peace = WYW._cause(board, before, "Rhineland", "Prussia", "France", [])
        assert peace["how"] == "treaty" and peace["words"] == "handed over under their peace treaty"

    def test_pw_r7_a_marchs_own_hop_is_told_nothing_it_cannot_answer(self):
        mover = _src(REPO / "backend" / "commands" / "movement_executor.py")
        at = mover.index("_reading = _ground.after_the_move(world, marshal, target_name, captured_on_move)")
        guard = mover[mover.rfind("if (marshal.nation == world.player_nation", 0, at):at]
        assert "and not strategic_execution" in guard


class TestTheReviewThePeaceLane:
    def _deal(self, world, terms, covered=("Britain", "Prussia")):
        from backend.game_logic.settlement_staging import settlement_plain_deal
        war = {"side_by_nation": {"France": "attackers", "Bavaria": "attackers",
                                  "Britain": "defenders", "Prussia": "defenders"}}
        return settlement_plain_deal(world, war, "attackers", list(covered), terms, [], player="France")

    def test_pw_r8_an_allys_gains_and_payments_are_the_allys(self):
        """P1: a province ceded to Bavaria read "You get", a payment by Bavaria
        "You give"."""
        world = WorldState()
        deal = self._deal(world, [
            {"type": "peace"},
            {"type": "territory_cede", "from": "Britain", "to": "Bavaria", "region": "Netherlands"},
            {"type": "gold_indemnity", "from": "Prussia", "to": "Bavaria", "amount": 300},
            {"type": "gold_indemnity", "from": "Bavaria", "to": "Britain", "amount": 100},
            {"type": "gold_indemnity", "from": "Prussia", "to": "France", "amount": 500},
            {"type": "gold_indemnity", "from": "France", "to": "Britain", "amount": 50},
        ])
        assert deal["get"] == ["500 gold from Prussia"]
        assert deal["give"] == ["50 gold to Britain"]
        assert deal["allies_get"] == ["Bavaria gets Netherlands from Britain", "Bavaria gets 300 gold from Prussia"]
        assert deal["allies_give"] == ["Bavaria gives 100 gold to Britain"]
        from backend.game_logic.settlement_staging import settlement_plain_result
        told = settlement_plain_result(dict(deal, **{"with": ["Britain", "Prussia"]}))
        assert "Bavaria got Netherlands from Britain." in told["lines"]
        assert "Bavaria gave 100 gold to Britain." in told["lines"]
        assert told["lines"][0] == "You got: 500 gold from Prussia."
        # ...and the change line names both parties of an ally's clause
        from backend.game_logic.settlement_actions import _term_words
        assert _term_words(world, {"type": "gold_indemnity", "from": "Bavaria", "to": "Britain"},
                           "France") == "gold Bavaria pays Britain"
        popup = _src(SCRIPTS / "proposal_confirm_popup.gd")
        deal_bb = _func(popup, "_pw_this_deal_bbcode")
        assert "Your allies get:" in deal_bb and "Your allies give:" in deal_bb and "Goes home to " in deal_bb

    def test_pw_r9_land_the_treaty_sends_home_is_said(self):
        staging = _src(REPO / "backend" / "game_logic" / "settlement_staging.py")
        block = staging[staging.index("def settlement_plain_deal("):staging.index("def _plain_join(")]
        assert 'for home, regions in (entry.get("returned") or {}).items():' in block
        assert '"goes_home": [{"to": h, "to_display": court(h), "yours": h == player' in block

    def test_pw_r10_a_dead_press_names_its_true_cause(self):
        from backend.game_logic.settlement_actions import dial_change_line, land_offer_rows
        world = WorldState()
        same = [{"type": "peace"}]
        rich = dial_change_line(world, same, same, direction="generous", proposer_leader="France",
                                land_offers=[{"court": "Britain"}], no_gold=False)
        assert rich["why"] == "more gold would buy nothing more from them"
        poor = dial_change_line(world, same, same, direction="generous", proposer_leader="France",
                                land_offers=[{"court": "Britain"}], no_gold=True)
        assert poor["why"] == "you have no more gold to offer"
        capped = dial_change_line(world, same, same, direction="generous", proposer_leader="France")
        assert capped["why"] == "nothing more can be added to this deal"
        event = [{"kind": "territory_escalation", "group": "offer", "court": "Britain", "region": "Belgium"}]
        row = land_offer_rows(world, event, war_id="w", draft_key="d", no_gold=False)[0]
        assert row["line"].startswith("More gold would buy nothing more from Britain.")
        assert "Belgium, which is yours" in row["line"]
        world.get_region("Belgium").controller = "Bavaria"
        row = land_offer_rows(world, event, war_id="w", draft_key="d", no_gold=True)[0]
        assert row["line"].startswith("You have no more gold to offer Britain.")
        assert "which your ally Bavaria holds" in row["line"] and row["holder"] == "Bavaria"

    def test_pw_r12_the_wars_object_blocks_in_two_ways(self):
        from backend.display_names import acceptance_component_plain
        assert acceptance_component_plain("war_objective_alignment", "objective_contradicts") \
            == "it gives away what the war was for"
        assert acceptance_component_plain("war_objective_alignment", "objective_unrelated_harsh") \
            == "it asks what the war was not about"
        baseline = _src(REPO / "backend" / "game_logic" / "settlement_baseline.py")
        assert 'tier_detail or str(_objective_view.get("top_blocker_detail") or ""))' in baseline

    def test_pw_r14_the_seam_down_is_the_old_dial_exactly(self, monkeypatch):
        from backend.game_logic import settlement_actions
        from backend.game_logic.settlement_preview import handle_settlement_dialogue_action
        from tests.test_settlement_gate4_leg1_fixes import (
            _stage_propose, _strip_to_peace_only, _winning_two_court_world,
        )
        monkeypatch.setattr(settlement_actions, "the_dial_never_gives_land_unasked", lambda: False)
        world, _war = _winning_two_court_world(france_gold=0)
        dialogue = _strip_to_peace_only(world, _stage_propose(world))
        result = handle_settlement_dialogue_action(
            world, action="settlement_dial_generous", dialogue=dialogue,
            action_params={"action": "settlement_dial_generous", "scope": "table"})
        new = result["diplomatic_dialogue"]
        assert "dial_change" not in new and "dial_dead" not in new and "land_offers" not in new

    def test_pw_r15_a_truce_is_an_ask_and_runs_out(self):
        from backend.game_logic.cabinet_rows import _PLAIN_PEACE
        line = _PLAIN_PEACE["propose_armistice"][1]
        # (row PW part 2, the review: a truce is not "signed into a peace before it runs out" — at its end
        # it becomes one, or the war starts again: `diplomacy.armistice_expiry_exit`)
        assert line.startswith("If they agree, the fighting stops for {truce} turns.")
        assert "When the truce runs out it becomes a peace if relations have mended enough" in line
        assert line.endswith("If not, the war starts again.") and "has to be signed" not in line

    def test_pw_r16_a_label_with_its_own_figure_is_said_once(self):
        class Ctx:
            battle_result = {"modifier_snapshot": {"attacker": [
                {"type": "bonus", "label": "Ranged bombardment (−50% return fire)", "value": 50}], "defender": []}}
            marshal = enemy_marshal = None
            world = None
        lines = T.why_plain(Ctx(), True)
        assert "your ranged bombardment +50%" in lines and not any("return fire" in ln for ln in lines)


class TestTheReviewTheClientLane:
    MAIN = _src(SCRIPTS / "main.gd")
    POPUP = _src(SCRIPTS / "proposal_confirm_popup.gd")

    def test_pw_r17_a_waiting_click_dies_with_its_selection(self):
        """P1: a click that waited on a quote survived a change of selection —
        a later hover of the same province under another corps sent him."""
        for fn in ("_select_marshal", "_reread_order_selection", "_clear_order_selection"):
            body = _func(self.MAIN, fn)
            assert '_order_go_pending = ""' in body and '_order_card_wait = ""' in body, fn

    def test_pw_r18_the_deferred_send_asks_the_guards_again(self):
        go = _func(self.MAIN, "_order_go_with")
        guard = 'if not _order_input_ready() or command_input.text.strip_edges() != "":\n\t\treturn'
        assert guard in go and go.index(guard) < go.index("_pw_send_and_keep_him(command)")

    def test_pw_r19_the_near_grab_selects_and_never_redirects_an_order(self):
        hover = _func(_src(SCENES / "map_renderer_base.gd"), "_refresh_hover_state")
        grab = hover.index("pick_piece_near(marshal_hitboxes, map_mouse, _piece_grab_world())")
        assert hover.rfind("if not ordering:", 0, grab) > 0
        # after every exact hit: the fog chips, the fleets, the garrison chips
        for exact in ("for hitbox in fogged_force_hitboxes:", "for hitbox in ([] if ordering else fleet_hitboxes):",
                      '_label_hit("region", map_mouse, label_hitboxes)'):
            assert hover.index(exact) < grab, exact
        assert grab < hover.index("var color_map_region = _lookup_region_from_color_map(map_mouse)")

    def test_pw_r20_the_client_raises_no_report_window_of_its_own(self):
        result = _func(self.MAIN, "_on_command_result")
        assert '"digest_only"' not in _code(self.MAIN)
        assert 'if wyw_news and not response.has("enemy_phase"):\n\t\t\t_pw_say_the_digest(wyw)' in result
        assert "map_area.flash_regions(flash)" in _func(self.MAIN, "_pw_say_the_digest")

    def test_pw_r21_the_table_stays_through_review_and_back(self):
        stay = _func(self.POPUP, "_stay_for_restage")
        assert "STAYS_THROUGH.has(action)" in stay and 'action.begins_with("settlement_demand_")' in stay
        listed = self.POPUP[self.POPUP.index("const STAYS_THROUGH := ["):]
        listed = listed[:listed.index("]")]
        for action in ("settlement_dial_harsher", "settlement_dial_generous", "settlement_cover_drop",
                       "submit_settlement_for_review", "return_to_settlement_terms"):
            assert f'"{action}"' in listed, action
        assert '"confirm_settlement"' not in listed      # a signature closes the table

    def test_pw_r22_only_the_tables_own_answer_answers_the_table(self):
        result = _func(self.MAIN, "_on_command_result")
        assert "if _pw_table_answer_due and proposal_confirm_popup != null" in result
        assert "_pw_table_answer_due = true" in _func(self.MAIN, "_on_proposal_confirm_choice")

    def test_pw_r23_a_court_button_with_no_scope_is_never_the_tables(self):
        assert ('_pw_dial_dead_reason(str(aff.get("action", "")), aff_scope) if aff_scope != "" else ""'
                in self.POPUP)

    def test_pw_r24_r25_the_leftovers(self):
        assert "Treasury[/b] %s gold: you offer %s; left if they sign %s" in self.POPUP
        assert 'verb = "March, then attack"' in _func(self.MAIN, "_order_ghost_label")
        assert "_pw_shut_the_stack_list()" in _func(self.MAIN, "_on_command_result")
        assert "_pw_shut_the_stack_list()" in _func(self.MAIN, "_reset_frontend_state_for_world_swap")
        echo = _func(self.MAIN, "_pw_dialogue_echo")
        assert 'action.trim_prefix("settlement_")' in echo


# ═════════════════════════════════════════════════════════════════════════════
# 9. After the blind reading — a dial says its next step; the rail stands still;
#    the report is "The enemy's moves"
# ═════════════════════════════════════════════════════════════════════════════

class TestTheDialSaysItsNextStep:
    """PW-X13. The blind reading (three readers, November 18): five questions
    of six answered by every reader; none could say what "Offer them more"
    would do BEFORE pressing it. A dial now wears its next press — the dial's
    own dry run — and what it shows is what the press applies."""

    POPUP = _src(SCRIPTS / "proposal_confirm_popup.gd")

    @staticmethod
    def _press(world, dialogue, direction, scope):
        from backend.game_logic.settlement_preview import handle_settlement_dialogue_action
        action = f"settlement_dial_{direction}"
        return handle_settlement_dialogue_action(
            world, action=action, dialogue=dialogue, action_params={"action": action, "scope": scope})

    def _walk(self, world, dialogue, steps):
        """Each step: the preview, then the press — shown == applied."""
        from backend.game_logic.settlement_actions import dial_previews
        seen = []
        for direction, scope in steps:
            row = dial_previews(world, dialogue)[f"{scope}:{direction}"]
            result = self._press(world, dialogue, direction, scope)
            assert result["success"] is True, result.get("error_display")
            new = result["diplomatic_dialogue"]
            change = new["dial_change"]
            assert bool(row["changes"]) == bool(change["changed"]), (row, change)
            if change["changed"]:
                assert row["line"] == "Next press: " + "; ".join(change["parts"]) + "."
                assert row["face"]
            else:
                assert bool(row.get("asks_land")) == bool(new.get("land_offers")), (row, new.get("land_offers"))
                assert bool(row.get("dead")) == (not new.get("land_offers"))
                assert row["why"] == change["why"]
            seen.append(row)
            dialogue = new
        return seen

    def test_the_preview_is_what_the_press_then_does(self):
        from tests.test_settlement_gate4_leg1_fixes import _stage_propose, _winning_two_court_world
        world, _war = _winning_two_court_world()
        dialogue = _stage_propose(world)
        court = dialogue["covered_enemy_participants"][0]
        rows = self._walk(world, dialogue, [
            ("generous", "table"), ("generous", "table"), ("harsher", "table"), ("harsher", "table"),
            ("harsher", court), ("generous", court)])
        assert rows[1]["face"] == "you pay each court 100 more gold"
        assert rows[2]["face"] == "you pay each court 100 less gold"

    def test_at_the_end_of_the_gold_it_says_so_before_the_press(self):
        from tests.test_settlement_gate4_leg1_fixes import (
            _stage_propose, _strip_to_peace_only, _winning_two_court_world,
        )
        world, _war = _winning_two_court_world(france_gold=250)
        dialogue = _strip_to_peace_only(world, _stage_propose(world))
        rows = self._walk(world, dialogue, [("generous", "table")] * 4)
        assert rows[0]["face"] == "you pay each court 100 more gold"
        assert rows[1]["face"] == "you pay Britain 50 more gold"         # what the purse still holds
        assert rows[2] == {"changes": False, "dead": True, "why": "you have no more gold to offer",
                           "face": "nothing more to add",
                           "line": "Nothing more to change — you have no more gold to offer."}

    def test_where_only_land_is_left_the_press_is_said_to_ask(self):
        from tests.test_settlement_gate4_leg1_fixes import (
            _stage_propose, _strip_to_peace_only, _winning_two_court_world,
        )
        world, _war = _winning_two_court_world(france_gold=0)
        for captured in ("Rhineland", "Waterloo"):
            world.regions[captured].controller = "France"
        world.invalidate_active_nations_cache()
        dialogue = _strip_to_peace_only(world, _stage_propose(world))
        rows = self._walk(world, dialogue, [("generous", "table")])
        assert rows[0]["asks_land"] is True and not rows[0].get("dead")
        assert rows[0]["face"] == "gold can add no more — asks about land"
        assert "nothing is given unless you choose it" in rows[0]["line"]

    def test_it_reads_and_changes_nothing(self):
        import copy
        from backend.game_logic.settlement_actions import dial_previews
        from tests.test_settlement_gate4_leg1_fixes import _stage_propose, _winning_two_court_world
        world, _war = _winning_two_court_world()
        dialogue = _stage_propose(world)
        before = copy.deepcopy(dialogue)
        gold = copy.deepcopy(dict(world.nation_gold))
        rows = dial_previews(world, dialogue)
        assert set(rows) == {f"{scope}:{direction}" for scope in ("table", "Britain", "Prussia")
                             for direction in ("harsher", "generous")}
        assert dialogue == before
        assert gold == dict(world.nation_gold)

    def test_only_the_players_own_open_table_has_one(self, monkeypatch):
        from backend.game_logic import settlement_actions
        from tests.test_settlement_gate4_leg1_fixes import _stage_propose, _winning_two_court_world
        world, _war = _winning_two_court_world()
        dialogue = _stage_propose(world)
        assert settlement_actions.dial_previews(world, dict(dialogue, dialogue_mode="REVIEW")) == {}
        assert settlement_actions.dial_previews(world, dict(dialogue, caller_kind="ai_offer")) == {}
        monkeypatch.setattr(settlement_actions, "the_dial_says_its_next_step", lambda: False)
        assert settlement_actions.dial_previews(world, dialogue) == {}

    def test_it_leaves_on_the_wire_and_is_never_stored(self):
        import backend.main as M
        from tests.test_settlement_gate4_leg1_fixes import _stage_propose, _winning_two_court_world
        world, _war = _winning_two_court_world()
        dialogue = _stage_propose(world)
        wired = M._wire_dialogue(world, dialogue)
        assert set(wired["dial_next"]) >= {"table:harsher", "table:generous"}
        assert "dial_next" not in dialogue
        letter = {"type": "diplomatic_dialogue", "dialogue_mode": "", "target_nation": "Prussia"}
        assert "dial_next" not in M._wire_dialogue(world, letter)

    def test_the_face_names_whom_and_folds_a_long_list(self):
        from backend.game_logic.settlement_actions import _dial_face
        world = WorldState()
        before = [{"type": "peace"}]
        after = before + [
            {"type": "gold_indemnity", "from": "France", "to": court, "amount": 100}
            for court in ("Austria", "Britain", "Russia")]
        assert _dial_face(world, before, after, proposer_leader="France",
                          scope_courts=["Austria", "Britain", "Russia"]) == "you pay each court 100 more gold"
        assert _dial_face(world, before, after[:2], proposer_leader="France",
                          scope_courts=["Austria", "Britain", "Russia"]) == "you pay Austria 100 more gold"
        assert _dial_face(world, before, after[:3], proposer_leader="France",
                          scope_courts=["Austria", "Britain", "Russia"]) == "you pay 2 courts 100 more gold"
        asks = before + [{"type": "territory_cede", "from": "Austria", "to": "France", "region": "Tyrol"},
                         {"type": "gold_indemnity", "from": "Britain", "to": "France", "amount": 100},
                         {"type": "gold_per_turn", "from": "Russia", "to": "France", "amount": 20, "turns": 5}]
        face = _dial_face(world, before, asks, proposer_leader="France",
                          scope_courts=["Austria", "Britain", "Russia"])
        assert face == "Britain pays you 100 more gold · Russia pays you 20 more gold a turn · and 1 more"

    def test_the_rail_wears_it_and_shuts_before_a_dead_press(self):
        show = _func(self.POPUP, "show_dialogue")
        assert 'var next_step: Dictionary = _pw_dial_next(str(opt.get("action", "")), str(opt.get("scope", "table")))' in show
        assert 'btn.text = str(plain_face[0]) + "\\n" + second' in show
        assert "not Utils.compact_view()" in show.split("var second: String", 1)[1][:120], (
            "the short window keeps one line a button (EA-E6): the step is the hover there")
        assert 'if bool(next_step.get("dead", false)) and available:' in show
        reader = _func(self.POPUP, "_pw_dial_next")
        assert '(scope if scope != "" else "table") + ":" + direction' in reader
        assert 'current_data.get("dial_next", {})' in reader
        rows = _func(self.POPUP, "_add_settlement_tier2_buttons")
        assert 'var aff_next: Dictionary = _pw_dial_next(str(aff.get("action", "")), aff_scope) if aff_scope != "" else {}' in rows
        assert 'if aff_dead == "" and bool(aff_next.get("dead", false)):' in rows

    def test_review_is_primary_only_where_they_would_sign(self):
        show = _func(self.POPUP, "show_dialogue")
        assert 'var _would_be_signed: bool = (not is_settlement_table) or bool(data.get("can_ratify", true))' in show
        assert ('if (original_label.begins_with("Submit for Review") and _would_be_signed) '
                'or original_label.begins_with("Ratify"):') in show

    def test_the_number_on_a_row_is_said_where_the_rows_begin(self):
        assert ('const TABLE_NUMBER_CAPTION := "The number on each row is how willing that court is to sign '
                '— it signs at 50. It rises as you win the war and as you offer more, and falls as you ask '
                'more."') in self.POPUP
        block = _func(self.POPUP, "_build_settlement_per_court_block")
        assert "if authoring_surface:" in block.split('Utils.bb_section("The table")', 1)[1][:260]
        from backend.game_logic.settlement_scoring import ACCEPTANCE_THRESHOLD
        assert int(ACCEPTANCE_THRESHOLD) == 50, "the caption names the bar"


class TestTheRailKeepsItsRow:
    """PW-X12. Measured frame by frame in the real client: under every press
    the table's four buttons stood in two rows for two frames (the rail 45 ->
    98 px, the list 78 px shorter, then back). The row is decided in the frame
    the buttons are built."""

    POPUP = _src(SCRIPTS / "proposal_confirm_popup.gd")

    def test_the_last_showings_buttons_leave_the_rail_at_once(self):
        show = _func(self.POPUP, "show_dialogue")
        assert "_rail_rebuilds_in_place = true" in show and "_rail_rebuilds_in_place = was_visible" not in show
        clear = _func(self.POPUP, "_clear_buttons")
        assert "if _rail_rebuilds_in_place and not child.is_queued_for_deletion():" in clear
        assert "button_container.remove_child(child)" in clear

    def test_the_row_is_decided_in_the_frame_the_buttons_are_built(self):
        show = _func(self.POPUP, "show_dialogue")
        tail = show.split("Utils.clamp_centered_panel($PanelContainer)", 1)[1]
        first = tail.split("if held_doc.is_empty():", 1)[0]
        assert "if _fit_action_columns():" in first, "before the fit's two frames, not after them"
        assert "Utils.clamp_centered_panel($PanelContainer)" in first
        fit = _func(self.POPUP, "_fit_settlement_document")
        assert "if _fit_action_columns() and not held:" in fit, "the fit's own measure stands (it finds the same)"


class TestTheReportIsTheEnemysMoves:
    """The user, November 18: "while you were away isnt thematic or sensible"."""

    def test_the_title_and_the_logs_rule(self):
        dialog = _src(SCRIPTS / "enemy_phase_dialog.gd")
        assert 'const REPORT_TITLE := "THE ENEMY\'S MOVES"' in dialog
        assert '(REPORT_TITLE + " · TURN %d") % turn if not _digest.is_empty()' in dialog
        main = _src(SCRIPTS / "main.gd")
        assert "━━ The enemy's moves ━━" in main
        for script in (dialog, main, _src(SCRIPTS / "codex_terms.gd")):
            assert "while you waited" not in _code(script).lower()

    def test_help_files_it_under_e(self):
        terms = _src(SCRIPTS / "codex_terms.gd")
        names = re.findall(r'^\t\["([^"]+)",', terms.split("const ORDER_GRAMMAR", 1)[0], flags=re.M)
        at = names.index("The enemy's moves")
        assert names[at - 1] == "Ending a war" and names[at + 1] == "Expedition"
        # 61 -> 64 (row IC, directives, November 19, 2026): "Named army",
        # "Orders to several corps" and "War goal" joined the glossary.
        assert len(names) == 64
