"""SR-1b "The client's war is the lord's war" (Score Mandate Chunk 1,
September 26, 2026; `BUG_FIXES.md` AAR-1 P1, `DESIGN_REFINEMENT.md` AAR-D1
ruled at default (a); landing record `SCORE_MANDATE_PLAN.md` §2 Chunk 1).

The AAR's Treaty of Vienna (turn 9) resolved the France–Austria pair only;
`Austria|KingdomOfItaly` stayed active, and Austria — at PEACE with France —
took Piedmont, Tyrol and Milan and eliminated the client by turn 18. A
lord's PEACE or ARMISTICE now resolves its satellites' pairs with the same
court (and the court's satellites' pairs with the lord's bloc) to the same
state by the same road: ONE helper, `diplomacy.follow_the_lord`, called from
the four treaty roads. The offer surface names who follows (the clients)
beside who fights on (the allies — AAR-28's HARD_STOP that stopped nothing
is a WARNING that says what it does). GR5: any lord, any board.
"""
import contextlib
import io
from pathlib import Path

import pytest

import backend.game_logic.diplomacy as D
from backend.ai.enemy_ai import EnemyAI
from backend.commands.executor import CommandExecutor
from backend.game_logic import coalition, game_end
from backend.game_logic.mailbox_payloads import build_pending_envoy_popup_from_terms
from backend.game_logic.settlement_ratify import ratify_settlement_confirm
from backend.game_logic.settlement_third_party import PAIR_EXIT_TRUCE_FLOOR_TURNS
from backend.game_logic.turn_manager import TurnManager
from backend.models.world_state import WorldState
from tests.test_common_peace_c2_ratification import (
    _install_two_v_two_war, _stage_dialogue,
)

SCENARIO_PATH = (Path(__file__).resolve().parents[1] / "godot-client"
                 / "project-sovereign" / "assets" / "maps" / "europe_1805.json")

KOI = "KingdomOfItaly"


def _boot() -> WorldState:
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(SCENARIO_PATH))


def _ratify(world, proposer, target, ptype="peace"):
    with contextlib.redirect_stdout(io.StringIO()):
        return world._ratify_treaty({
            "proposer_nation": proposer, "target_nation": target,
            "type": ptype, "sweeteners": [], "demands": []})


def _state(world, a, b):
    return world.get_diplomatic_state(a, b)


def _pair_meta(world, a, b):
    key = world._make_diplo_key(a, b)
    for war in world.war_instances.values():
        meta = (war.get("diplo_key_meta") or {}).get(key)
        if meta:
            return war, meta
    return None, None


def _stage_austrian_client(world, name="Tyrol_Client"):
    """A satellite of AUSTRIA at war with France — the mirror geometry.
    Staged on the vassal row alone (the boot has no Austrian client)."""
    world.vassals[name] = {"lord": "Austria", "loyalty": 60, "autonomy": 1,
                          "path": "treaty", "created_turn": 1,
                          "tribute_rate": 0.3, "regions": []}
    world.diplomatic_states[world._make_diplo_key(name, "France")] = "WAR"
    world.invalidate_bloc_members_cache()
    world.invalidate_active_nations_cache()
    return name


class TestTheAARReproduction:
    """The boot: the Kingdom of Italy (Piedmont, Milan) is France's client
    and at war with Austria; Bavaria is France's ALLY and at war with
    Austria; Austria's corps stand at Swabia, Carniola and Tyrol."""

    def test_the_boot_geometry_is_the_aars(self):
        w = _boot()
        assert w.vassals[KOI]["lord"] == "France"
        assert _state(w, KOI, "Austria") == "WAR"
        assert _state(w, "Bavaria", "France") == "ALLIANCE"
        assert _state(w, "Bavaria", "Austria") == "WAR"

    def test_the_lords_peace_resolves_the_clients_pair(self):
        w = _boot()
        _ratify(w, "Austria", "France")
        assert _state(w, "France", "Austria") == "PEACE"
        assert _state(w, KOI, "Austria") == "PEACE"
        assert _state(w, "Holland", "Britain") == "WAR"      # a different court
        # PC-R1 (S13e part 1): an ally France LEADS is carried in by the
        # leader's peace — Bavaria's pair ends in the same instrument.
        assert _state(w, "Bavaria", "Austria") == "PEACE"
        war, meta = _pair_meta(w, KOI, "Austria")
        assert meta["pair_status"] == "resolved"
        assert meta["resolved_turn"] == w.current_turn
        assert w._make_diplo_key(KOI, "Austria") in war["resolved_diplo_keys"]
        assert w._make_diplo_key(KOI, "Austria") not in war["active_diplo_keys"]

    def test_the_summary_names_who_follows_and_who_fights_on(self):
        w = _boot()
        _ratify(w, "Austria", "France")
        aftermath = w.peace_ratification_log[-1]["political_aftermath"]
        assert any(a.startswith("Our clients follow us into the peace: ")
                   and "Kingdom of Italy" in a for a in aftermath), aftermath
        # PC-R1: Bavaria is carried in, named on the aftermath — not aggrieved.
        assert any("Bavaria's war with Austria ends in this instrument" in a
                   for a in aftermath), aftermath
        assert not any("Bavaria views this separate peace unfavorably" in a
                       for a in aftermath), aftermath

    def test_austria_can_no_longer_find_the_client_on_its_board(self):
        w = _boot()
        _ratify(w, "Austria", "France")
        assert not w.is_at_war("Austria", KOI)
        ai = EnemyAI(CommandExecutor())
        charles = w.marshals["ArchdukeCharles"]
        john = w.marshals["ArchdukeJohn"]
        client_soil = set(w.get_nation_regions(KOI))
        with contextlib.redirect_stdout(io.StringIO()):
            for marshal in (charles, john):
                for rung in (ai._find_undefended_capture, ai._find_garrison_attack,
                             ai._find_attack_opportunity):
                    pick = rung(marshal, "Austria", w)
                    target = (pick or {}).get("target")
                    assert target not in client_soil, (rung.__name__, pick)

    def test_eight_unattended_turns_leave_the_client_standing(self):
        """The AAR's sequence — Piedmont on turn 10, Tyrol, Milan stormed on
        17 — cannot recur under the peace: the client's provinces are
        still its own after eight enemy phases with France passive."""
        w = _boot()
        _ratify(w, "Austria", "France")
        executor = CommandExecutor()
        tm = TurnManager(w, executor=executor)
        gs = {"world": w, "executor": executor}
        with contextlib.redirect_stdout(io.StringIO()):
            for _ in range(8):
                tm.end_turn(gs)
        assert _state(w, KOI, "Austria") != "WAR"
        assert w.regions["Milan"].controller == KOI
        assert w.regions["Piedmont"].controller == KOI
        assert KOI in w.vassals

    def test_the_client_retains_what_it_holds_of_the_ceder(self):
        """SR-1a rides the cascade: the client's pair is signed by the same
        road, so what it holds of Austria's is titled for France's house."""
        w = _boot()
        w.regions["Tyrol"].controller = KOI
        game_end.record_province_title(w, "Tyrol", game_end.TITLE_CONQUEST, "Austria", KOI)
        w.invalidate_active_nations_cache()
        _ratify(w, "Austria", "France")
        rec = w.province_title["Tyrol"]
        assert rec["kind"] == game_end.TITLE_TREATY and rec["retained"] is True
        assert rec["house"] == "France"
        assert "Tyrol" in game_end.titled_provinces(w, "France")["titled"]


class TestTheTruce:

    def test_the_lords_truce_is_the_clients_truce(self):
        w = _boot()
        _ratify(w, "Austria", "France", ptype="armistice")
        assert _state(w, "France", "Austria") == "ARMISTICE"
        assert _state(w, KOI, "Austria") == "ARMISTICE"
        assert w.armistice_cooldowns[w._make_diplo_key(KOI, "Austria")] == 5
        _, meta = _pair_meta(w, KOI, "Austria")
        # DD1-5 (DD-1 S7, October 11, 2026): a truce resolves nothing, and the
        # instance now SAYS so — the pair stays active, paused. (Pinned "war"
        # until S7: the bilateral truce never restamped the instance.)
        assert meta["pair_status"] == "armistice"

    def test_the_clients_truce_thaws_with_the_lords(self):
        w = _boot()
        _ratify(w, "Austria", "France", ptype="armistice")
        lord_key = w._make_diplo_key("France", "Austria")
        client_key = w._make_diplo_key(KOI, "Austria")
        w.nation_relations[lord_key] = -20                      # thawed enough
        w.nation_relations[client_key] = -100                   # would collapse alone
        w.armistice_turns[lord_key] = D.ARMISTICE_DURATION - 1
        w.armistice_turns[client_key] = D.ARMISTICE_DURATION - 1
        with contextlib.redirect_stdout(io.StringIO()):
            D._process_armistice_expiration(w)
        assert _state(w, "France", "Austria") == "PEACE"
        assert _state(w, KOI, "Austria") == "PEACE"
        _, meta = _pair_meta(w, KOI, "Austria")
        assert meta["pair_status"] == "resolved"

    def test_the_clients_truce_collapses_with_the_lords(self):
        w = _boot()
        _ratify(w, "Austria", "France", ptype="armistice")
        lord_key = w._make_diplo_key("France", "Austria")
        client_key = w._make_diplo_key(KOI, "Austria")
        w.nation_relations[lord_key] = -100                     # collapses
        w.nation_relations[client_key] = 0                      # would thaw alone
        w.armistice_turns[lord_key] = D.ARMISTICE_DURATION - 1
        w.armistice_turns[client_key] = D.ARMISTICE_DURATION - 1
        with contextlib.redirect_stdout(io.StringIO()):
            D._process_armistice_expiration(w)
        assert _state(w, "France", "Austria") == "WAR"
        assert _state(w, KOI, "Austria") == "WAR"

    def test_a_clients_own_truce_still_decides_itself(self):
        """No lord pair in ARMISTICE beside it: the client's truce is its
        own (the pre-SR-1b rule, untouched)."""
        w = _boot()
        client_key = w._make_diplo_key(KOI, "Austria")
        w.diplomatic_states[client_key] = "ARMISTICE"
        w.nation_relations[client_key] = 0
        w.armistice_turns[client_key] = D.ARMISTICE_DURATION - 1
        with contextlib.redirect_stdout(io.StringIO()):
            D._process_armistice_expiration(w)
        assert _state(w, KOI, "Austria") == "PEACE"
        assert _state(w, "France", "Austria") == "WAR"


class TestTheOtherRoads:

    def test_the_settlement_table_carries_a_cross_instance_client_pair(self):
        """The plan resolves the pairs of ITS instance; a client's older war
        with the covered court, in an instance of its own, follows the lord
        by the same road."""
        world = WorldState()
        _install_two_v_two_war(world)
        world.vassals["Saxony"] = {"lord": "France", "loyalty": 60, "autonomy": 1,
                                   "path": "treaty", "created_turn": 1,
                                   "tribute_rate": 0.3, "regions": []}
        world.invalidate_bloc_members_cache()
        # Saxony's pair with Austria sits in war_1 (the plan's); stage a
        # SECOND client with a pair the plan cannot see.
        world.vassals["Holland"] = {"lord": "France", "loyalty": 60, "autonomy": 1,
                                    "path": "treaty", "created_turn": 1,
                                    "tribute_rate": 0.3, "regions": []}
        world.diplomatic_states[world._make_diplo_key("Holland", "Austria")] = "WAR"
        world.invalidate_bloc_members_cache()
        world.invalidate_active_nations_cache()
        dialogue = _stage_dialogue(world, covered_enemy_participants=["Austria"])
        with contextlib.redirect_stdout(io.StringIO()):
            result = ratify_settlement_confirm(world, dialogue)
        assert result["success"] is True
        assert world.diplomatic_states[world._make_diplo_key("Holland", "Austria")] == "PEACE"
        # The cascaded pair is COUNTED among the resolved pairs the table
        # reports (AAR-1's "resolve — or at least LIST").
        assert result["settlement_result_feedback"]["resolved_pair_count"] >= 3
        assert "Holland" not in world.get_nations_at_war_with("Austria")

    def test_the_exhausted_pair_exit_takes_the_clients_out_on_the_truce_floor(self):
        w = _boot()
        client = _stage_austrian_client(w)
        moved = D.follow_the_lord(w, "Austria", "France", "PEACE", "mutual_exhaustion",
                                  truce_floor=PAIR_EXIT_TRUCE_FLOOR_TURNS)
        pairs = {row["pair"] for row in moved}
        assert w._make_diplo_key(KOI, "Austria") in pairs
        assert w._make_diplo_key(client, "France") in pairs
        assert w._make_diplo_key(client, KOI) not in pairs   # never at war
        for key in pairs:
            assert w.armistice_cooldowns[key] == PAIR_EXIT_TRUCE_FLOOR_TURNS

    def test_the_pair_exit_calls_the_helper(self):
        src = Path("backend/game_logic/settlement_third_party.py").read_text(encoding="utf-8")
        body = src.split("def _process_exhausted_pair_exits(", 1)[1].split("\ndef ", 1)[0]
        # PC-F28 (S13e part 4): the exit's reason is the mutual-exhaustion
        # white peace or the beaten loser's suit — both follow the lord
        assert 'exit_reason = "sub_pair_loser_sues" if sued else "mutual_exhaustion"' in body
        assert 'set_diplomatic_state(world, a, b, "PEACE", exit_reason)' in body
        assert "follow_the_lord(world, a, b, \"PEACE\", exit_reason" in body


class TestGR5:

    def test_an_ai_lords_peace_cascades_to_its_client(self):
        w = _boot()
        client = _stage_austrian_client(w)
        assert _state(w, client, "France") == "WAR"
        _ratify(w, "Austria", "France")
        assert _state(w, client, "France") == "PEACE"
        assert _state(w, client, KOI) != "WAR"

    def test_the_read_lists_both_sides_clients(self):
        w = _boot()
        client = _stage_austrian_client(w)
        pairs = {tuple(sorted(p)) for p in D.client_pairs_that_follow(w, "France", "Austria", "PEACE")}
        assert tuple(sorted((KOI, "Austria"))) in pairs
        assert tuple(sorted((client, "France"))) in pairs


class TestTheFreshPeaceFloor:

    def test_the_cascaded_pair_is_a_fresh_peace_too(self):
        w = _boot()
        _ratify(w, "Austria", "France")
        assert coalition.peace_with_target_is_fresh("Austria", w, "France")
        _, meta = _pair_meta(w, KOI, "Austria")
        assert meta["resolved_turn"] == w.current_turn


class TestTheSurface:

    def _incoming(self, w, ptype="peace"):
        with contextlib.redirect_stdout(io.StringIO()):
            return build_pending_envoy_popup_from_terms(
                w, nation="Austria",
                terms={"type": ptype, "proposer_nation": "Austria",
                       "target_nation": "France", "sweeteners": [], "demands": []})

    def test_the_incoming_offer_names_who_follows_and_who_fights_on(self):
        w = _boot()
        payload = self._incoming(w)
        follow = [f for f in payload["fallout_warnings"]
                  if f.get("warning_type") == "clients_follow"]
        assert len(follow) == 1
        assert follow[0]["display"].startswith("Our clients follow us out of the war: ")
        assert "Kingdom of Italy" in follow[0]["display"]
        assert "Bavaria" not in follow[0]["display"]
        # PC-R1 (S13e part 1): Bavaria is CARRIED IN by France's peace —
        # no fallout line of hers, the carried-in row instead.
        ally = [f for f in payload["fallout_warnings"]
                if f.get("warning_type") == "separate_peace_ally"]
        assert not any(f["ally"] == "Bavaria" for f in ally)

    def test_the_paradox_on_an_incoming_offer_says_what_it_does(self):
        """AAR-28 made the accept road's paradox a WARNING; PC-R1 (S13e part
        1) reads the carry-in there too — France leads its side, so Bavaria's
        pair ends in the letter's instrument (an INFO row)."""
        w = _boot()
        payload = self._incoming(w)
        rows = [c for c in payload["commitment_conflicts"]
                if c.get("affected_entity") == "Bavaria"]
        assert len(rows) == 1
        assert rows[0]["conflict_type"] == "carried_in" and rows[0]["severity"] == "INFO"
        assert rows[0]["display"] == (
            "Bavaria's war with Austria ends in this instrument; she takes nothing by it.")

    def test_the_players_own_outgoing_peace_carries_the_ally(self):
        # PC-R1 (S13e part 1): the outgoing peace's HARD_STOP is retired —
        # the snapshot carries Bavaria as carried in.
        w = _boot()
        snapshot = D.build_war_context_snapshot(w, "France", "Austria", "peace", terms={})
        rows = [c for c in snapshot["commitment_conflicts"] if c.get("affected_entity") == "Bavaria"]
        assert len(rows) == 1 and rows[0]["conflict_type"] == "carried_in"
        assert rows[0]["severity"] == "INFO"
        assert not any(c.get("severity") == "HARD_STOP" for c in snapshot["commitment_conflicts"])
        assert snapshot.get("clients_following", "").startswith("Our clients follow us out of the war")

    def test_a_truce_offer_says_the_truce(self):
        w = _boot()
        payload = self._incoming(w, ptype="armistice")
        follow = [f for f in payload["fallout_warnings"]
                  if f.get("warning_type") == "clients_follow"]
        assert follow and "out of the truce" in follow[0]["display"]
