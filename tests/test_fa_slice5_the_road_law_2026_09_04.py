"""Final Whole-Game Audit — slice 5, "The Road Law" (FA-13, FA-46, FA-N11,
FA-N12, FA-N49, FA-N41).

Four marching verbs × two seams each owned a private copy of route-plotting
and only the per-turn `_get_personality_aware_path` obeyed the movement law
(PF-8's `passable_for`). Reproduced on the shipped board before a line was
written (`docs/audits/fa_build_2026_09_04/REPRO_D_the_road_law.md`):

* FA-13 — `Ney, march to Normandy` from Flanders plotted the terrain-cheapest
  road THROUGH Hanover's Westphalia (PEACE, closed), charged 2 AP, and the
  first hop was refused in silence — Ney stood at Flanders with a route
  announced; the lawful road by Picardy was on the map the whole time.
* FA-13c / FA-N49 — a march or a HOLD whose DESTINATION is closed soil
  (Frankfurt is Hesse's, Brunswick is Hanover's, both at PEACE) was accepted
  at 2 AP, marched a turn and died "Cannot reach X" — the tactical `move`
  refused the same destination at 0 AP.
* FA-46 — `Ney, march to London` was accepted with a route and no naval word
  in it while the Royal Navy held the Normandy→London crossing SHUT at 0.54.
* FA-N11 — HOLD re-plotted its road from scratch every turn, so a literal
  marshal's reroute around an enemy was thrown away on the next tick.
* FA-N12 — HOLD's re-plot ignored the law and then broke the order with a
  reason that was false ("Cannot reach Normandy" — a lawful all-French
  corridor existed).
* FA-N41 — SUPPORT's first step refused at a closed border or a covered
  strait re-stalled "could not move toward" every turn, for ever.

Built as ONE ladder (`plot_route`), ONE verdict reader at issuance
(`issuance_road_refusal`) and ONE stall idiom (`_stall_verdict`), each
behaviour behind a lever whose False arm reproduces the prior behaviour
byte-for-byte; the per-turn helper delegates and is pinned byte-identical.
The AI never reaches these seams (the processor's roster is the player's;
`plot_route` keeps omniscient routing and computes no verdict for a
non-player corps), so `BASELINE_SERIES` and M1–M7 hold by construction.
"""
import contextlib
import io
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands import strategic as strategic_mod
from backend.commands.executor import CommandExecutor
from backend.commands.parser import CommandParser
from backend.commands.strategic import (
    StrategicOrderProcessor,
    enemy_occupied_regions,
    issuance_road_refusal,
    plot_route,
    region_is_adjacent,
)
from backend.models.marshal import StrategicOrder
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO = str(REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
               / "europe_1805.json")

# The shipped 1805 geometry this file leans on (measured, not assumed):
#   Flanders (French) adj Picardy (French) and Westphalia (Hanover, PEACE);
#   the terrain-cheapest Flanders→Normandy road runs Westphalia→Artois, the
#   lawful one Picardy→Artois. Frankfurt and Nassau are Hesse's, Brunswick
#   is Hanover's (all PEACE); Gelderland is Holland's (VASSAL, passable).
#   Normandy→London is a sea link the Royal Navy holds SHUT at 0.54.
LAWFUL_ROAD = ["Picardy", "Artois", "Normandy"]
LONG_LAWFUL_ROAD = ["Orleanais", "Burgundy", "Limousin", "Berry", "Normandy"]


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _boot():
    with _quiet():
        return WorldState.from_scenario(SCENARIO)


def _place(world, name, location, strength=None):
    marshal = world.get_marshal(name)
    marshal.location = location
    if strength is not None:
        marshal.strength = strength
    world.invalidate_active_nations_cache()
    world._build_marshal_index()
    world.calculate_visibility()
    return marshal


@contextlib.contextmanager
def _served(world):
    saved = (M.world, M.game_state, M.parser)
    M.world = world
    M.game_state = {"world": world}
    M.parser = CommandParser(use_real_llm=False)
    try:
        assert M.parser.llm.use_real_api is False
        yield TestClient(M.app)
    finally:
        M.world, M.game_state, M.parser = saved


def _post(client, line):
    with _quiet():
        return client.post("/command", json={"command": line}).json()


def _order(command_type, target, path=None, target_type="region"):
    return StrategicOrder(command_type=command_type, target=target,
                          target_type=target_type, started_turn=0, issued_turn=0,
                          path=list(path or []),
                          original_command=f"x, {command_type} {target}")


def _tick(world, marshal):
    """One per-turn pass for one marshal (the order aged one turn so the
    issued-this-turn skip does not apply)."""
    proc = StrategicOrderProcessor(CommandExecutor())
    world.current_turn += 1
    if marshal.strategic_order is not None:
        marshal.strategic_order.issued_turn = world.current_turn - 1
    with _quiet():
        return proc._execute_strategic_turn(marshal, world, {"world": world}) or {}


def _lawful(world, path, nation="France", here="Flanders"):
    return all(world._region_passable_for(r, nation, mover_location=here)
               for r in path[:-1])


# ═══════════════════════════════════════════════════════════════════════
# FA-13 — issuance plots the lawful road, and the first hop MARCHES
# ═══════════════════════════════════════════════════════════════════════

class TestIssuancePlotsTheLawfulRoad:

    def test_fa13_the_first_hop_marches_on_the_lawful_road(self):
        world = _boot()
        ney = _place(world, "Ney", "Flanders")
        ap = world.actions_remaining
        with _served(world) as client:
            reply = _post(client, "Ney, march to Normandy")
        assert reply.get("success") is True, reply.get("message")
        assert ney.location == "Picardy", "the first hop was refused in silence"
        assert ney.strategic_order.path == ["Artois", "Normandy"]
        assert "Westphalia" not in (reply.get("message") or "")
        assert world.actions_remaining == ap - 2

    def test_the_lever_off_arm_reproduces_the_row(self, monkeypatch):
        """FA-13 as filed: the road through Westphalia, 2 AP charged, Ney
        standing still."""
        monkeypatch.setattr(strategic_mod, "ROAD_LAW_AT_ISSUANCE", False)
        world = _boot()
        ney = _place(world, "Ney", "Flanders")
        ap = world.actions_remaining
        with _served(world) as client:
            reply = _post(client, "Ney, march to Normandy")
        assert reply.get("success") is True
        assert ney.strategic_order.path[0] == "Westphalia"
        assert ney.location == "Flanders"
        assert world.actions_remaining == ap - 2

    def test_the_cautious_avoid_set_is_the_one_source(self, monkeypatch):
        """The issuance scan used to be an inline copy of the processor's
        fog-aware loop; it now reads `enemy_occupied_regions`, and a visible
        enemy on the lawful road is in the avoid set the ladder receives."""
        seen = {}
        real = strategic_mod.plot_route

        def spy(world, marshal, destination, **kw):
            seen["avoid"] = list(kw.get("avoid_regions") or [])
            return real(world, marshal, destination, **kw)
        monkeypatch.setattr(strategic_mod, "plot_route", spy)
        world = _boot()
        _place(world, "Davout", "Flanders")
        _place(world, "Mack", "Picardy", 5000)
        assert world.get_visible_enemies_in_region("Picardy", "France")
        with _served(world) as client:
            _post(client, "Davout, march to Normandy")
        assert "Picardy" in seen.get("avoid", []), seen


# ═══════════════════════════════════════════════════════════════════════
# FA-13c / FA-N49 — a closed destination is refused at issuance, at 0 AP
# ═══════════════════════════════════════════════════════════════════════

class TestAClosedDestinationIsRefusedAtIssuance:

    def test_a_march_onto_peaceful_soil_is_refused_at_zero_ap(self):
        world = _boot()
        ney = world.get_marshal("Ney")
        ap = world.actions_remaining
        with _served(world) as client:
            reply = _post(client, "Ney, march to Frankfurt")
        message = reply.get("message") or ""
        assert reply.get("success") is False
        assert world.actions_remaining == ap
        assert ney.strategic_order is None
        assert "Cannot enter Frankfurt" in message and "Hesse" in message
        assert "declare war" in message

    def test_a_hold_past_a_closed_border_is_refused_at_zero_ap(self):
        """FA-N49's issuance half: `Davout, hold Brunswick` used to charge 2
        AP, march a turn and die 'Cannot reach Brunswick'."""
        world = _boot()
        davout = world.get_marshal("Davout")
        ap = world.actions_remaining
        with _served(world) as client:
            reply = _post(client, "Davout, hold Brunswick")
        assert reply.get("success") is False
        assert world.actions_remaining == ap
        assert davout.strategic_order is None
        assert "Hanover" in (reply.get("message") or "")

    def test_a_visible_enemy_on_closed_soil_keeps_the_road_open(self):
        """A march to where a VISIBLE enemy stands is an attack in the making —
        the first-step-blocked flow owns it, whatever flag flies there."""
        world = _boot()
        ney = _place(world, "Ney", "Rhineland")
        _place(world, "Mack", "Nassau", 5000)
        assert world.regions["Nassau"].controller == "Hesse"
        assert world.get_visible_enemies_in_region("Nassau", "France")
        _road, verdict = plot_route(world, ney, "Nassau", use_weighted=True,
                                    want_verdict=True)
        assert verdict["closed_destination"] is False
        assert issuance_road_refusal(world, ney, "Nassau", "MOVE_TO", verdict) is None
        with _served(world) as client:
            reply = _post(client, "Ney, march to Nassau")
        assert "Cannot enter Nassau" not in (reply.get("message") or "")

    def test_an_unseen_enemy_on_closed_soil_neither_opens_it_nor_leaks(self):
        """Fog decides: the refusal with an unseen Mack at Brunswick is the
        refusal without him, word for word."""
        def refusal(with_mack):
            world = _boot()
            _place(world, "Davout", "Rhineland")
            if with_mack:
                _place(world, "Mack", "Brunswick", 5000)
                assert not world.get_visible_enemies_in_region("Brunswick", "France")
            with _served(world) as client:
                reply = _post(client, "Davout, hold Brunswick")
            assert reply.get("success") is False
            return reply.get("message")
        assert refusal(True) == refusal(False)

    def test_the_lever_off_arm_accepts_and_charges(self, monkeypatch):
        monkeypatch.setattr(strategic_mod, "ROAD_LAW_AT_ISSUANCE", False)
        world = _boot()
        ney = world.get_marshal("Ney")
        ap = world.actions_remaining
        with _served(world) as client:
            reply = _post(client, "Ney, march to Frankfurt")
        assert reply.get("success") is True
        assert ney.strategic_order is not None and ney.strategic_order.target == "Frankfurt"
        assert world.actions_remaining == ap - 2


# ═══════════════════════════════════════════════════════════════════════
# S5-D2's own refusal survives, in its own words
# ═══════════════════════════════════════════════════════════════════════

class TestNoLawfulCorridorSpeaksInItsOwnWords:

    def test_the_s5d2_refusal_is_preserved(self):
        world = _boot()
        ney = _place(world, "Ney", "Flanders")
        verdict = {"legal": False, "blocker_region": "Westphalia",
                   "blocker_controller": "Hanover", "closed_destination": False,
                   "naval_leg": None, "naval_check": None}
        refusal = issuance_road_refusal(world, ney, "Normandy", "MOVE_TO", verdict)
        assert refusal is not None and refusal["success"] is False
        assert refusal["variable_action_cost"] == 0
        assert "no open road" in refusal["message"]
        assert "Westphalia" in refusal["message"] and "Hanover" in refusal["message"]

    def test_a_lawful_road_is_not_refused(self):
        world = _boot()
        ney = _place(world, "Ney", "Flanders")
        road, verdict = plot_route(world, ney, "Normandy", use_weighted=True,
                                   want_verdict=True)
        assert road == LAWFUL_ROAD
        assert verdict["legal"] is True and verdict["blocker_region"] is None
        assert issuance_road_refusal(world, ney, "Normandy", "MOVE_TO", verdict) is None


# ═══════════════════════════════════════════════════════════════════════
# FA-46 — a route over a SHUT crossing is refused at issuance
# ═══════════════════════════════════════════════════════════════════════

class TestAShutCrossingIsRefusedAtIssuance:

    def _channel(self, where="Rhineland", navy=100):
        world = _boot()
        ney = _place(world, "Ney", where)
        _place(world, "Moore", "East Anglia")
        world.fleets["Britain"]["ships"] = navy
        return world, ney

    def test_a_route_whose_last_leg_is_shut_is_refused_at_zero_ap(self):
        world, ney = self._channel()
        ap = world.actions_remaining
        with _served(world) as client:
            reply = _post(client, "Ney, march to London")
        assert reply.get("success") is False
        assert world.actions_remaining == ap
        assert ney.strategic_order is None
        assert "Royal Navy" in (reply.get("message") or "")

    def test_with_the_navy_sunk_the_march_forms(self):
        world, ney = self._channel(navy=0)
        with _served(world) as client:
            reply = _post(client, "Ney, march to London")
        assert reply.get("success") is True, reply.get("message")
        assert ney.strategic_order is not None and ney.strategic_order.target == "London"

    def test_the_verdict_names_the_shut_leg(self):
        world, ney = self._channel()
        _road, verdict = plot_route(world, ney, "London", use_weighted=True,
                                    want_verdict=True)
        assert verdict["naval_leg"] == ("Normandy", "London")
        assert verdict["naval_check"]["verdict"] == "shut"
        assert verdict["naval_check"]["coverer"] == "Britain"

    def test_a_refused_march_writes_no_log_row(self):
        """The companion of the slice-3r retraction pin: refused BEFORE an
        order exists, there is nothing to retract."""
        world, ney = self._channel()
        rows = lambda: [e for e in world.event_log  # noqa: E731
                        if e.get("type") == "strategic_order" and e.get("marshal") == "Ney"]
        before = rows()
        with _served(world) as client:
            _post(client, "Ney, march to London")
        assert rows() == before

    def test_a_pursuit_across_the_water_is_refused_too(self):
        world = _boot()
        ney = _place(world, "Ney", "Normandy")
        _place(world, "Moore", "London", 20000)
        with _served(world) as client:
            reply = _post(client, "Ney, pursue Moore")
        assert reply.get("success") is False
        assert "Royal Navy" in (reply.get("message") or "")
        assert ney.strategic_order is None


# ═══════════════════════════════════════════════════════════════════════
# FA-N11 — HOLD keeps its road
# ═══════════════════════════════════════════════════════════════════════

class TestHoldKeepsItsRoad:

    def test_a_literal_reroute_survives_the_next_tick(self):
        world = _boot()
        soult = _place(world, "Soult", "Flanders")
        _place(world, "Mack", "Picardy", 5000)
        soult.strategic_order = _order("HOLD", "Normandy", LAWFUL_ROAD)
        first = _tick(world, soult)
        assert first.get("action") == "reroute", first
        assert soult.strategic_order is not None
        rerouted = list(soult.strategic_order.path)
        assert rerouted and "Picardy" not in rerouted
        second = _tick(world, soult)
        assert second.get("order_status") == "continues", second
        assert soult.location == rerouted[0], "the reroute was thrown away"

    def test_a_sound_road_is_kept_not_replotted(self):
        world = _boot()
        soult = _place(world, "Soult", "Flanders")
        soult.strategic_order = _order("HOLD", "Normandy", LONG_LAWFUL_ROAD)
        report = _tick(world, soult)
        assert report.get("order_status") == "continues", report
        assert soult.location == "Orleanais", "the stored road was re-plotted"

    def test_a_stale_road_is_replotted_and_the_hold_survives(self):
        world = _boot()
        soult = _place(world, "Soult", "Flanders")
        soult.strategic_order = _order("HOLD", "Normandy", ["Artois", "Normandy"])
        assert not region_is_adjacent(world, "Flanders", "Artois")
        report = _tick(world, soult)
        assert report.get("order_status") == "continues", report
        assert soult.location == "Picardy"
        assert soult.strategic_order is not None
        assert soult.strategic_order.target == "Normandy"

    def test_the_lever_off_arm_reproduces_the_row(self, monkeypatch):
        monkeypatch.setattr(strategic_mod, "HOLD_KEEPS_ITS_ROAD", False)
        world = _boot()
        soult = _place(world, "Soult", "Flanders")
        soult.strategic_order = _order("HOLD", "Normandy", LAWFUL_ROAD)
        report = _tick(world, soult)
        assert report.get("order_status") == "breaks"
        assert "Cannot reach Normandy" in report.get("message", "")


# ═══════════════════════════════════════════════════════════════════════
# FA-N12 — HOLD's issuance plots the lawful road and marches it
# ═══════════════════════════════════════════════════════════════════════

class TestHoldIssuanceObeysTheLaw:

    def test_the_hold_marches_the_lawful_road_to_its_position(self):
        world = _boot()
        soult = _place(world, "Soult", "Flanders")
        with _served(world) as client:
            reply = _post(client, "Soult, hold Normandy")
        assert reply.get("success") is True, reply.get("message")
        assert soult.location == "Picardy"
        assert soult.strategic_order.path == ["Artois", "Normandy"]
        assert _tick(world, soult).get("order_status") == "continues"
        assert soult.location == "Artois"
        arrival = _tick(world, soult)
        assert soult.location == "Normandy"
        assert "arrives" in arrival.get("message", ""), arrival

    def test_the_lever_off_arm_reproduces_the_row(self, monkeypatch):
        monkeypatch.setattr(strategic_mod, "ROAD_LAW_AT_ISSUANCE", False)
        monkeypatch.setattr(strategic_mod, "HOLD_KEEPS_ITS_ROAD", False)
        world = _boot()
        soult = _place(world, "Soult", "Flanders")
        with _served(world) as client:
            _post(client, "Soult, hold Normandy")
        assert soult.strategic_order.path[0] == "Westphalia"
        report = _tick(world, soult)
        assert report.get("order_status") == "breaks"
        assert "Cannot reach Normandy" in report.get("message", "")


# ═══════════════════════════════════════════════════════════════════════
# FA-N49 — the HOLD stall speaks
# ═══════════════════════════════════════════════════════════════════════

class TestTheHoldStallSpeaks:

    def test_a_stored_road_through_closed_land_reroutes_with_the_reason(self):
        world = _boot()
        soult = _place(world, "Soult", "Flanders")
        soult.strategic_order = _order("HOLD", "Normandy", ["Westphalia", "Artois", "Normandy"])
        report = _tick(world, soult)
        assert report.get("order_status") == "continues", report
        assert "reroutes around Hanover territory toward Normandy" in report.get("message", "")
        assert soult.strategic_order.path == LAWFUL_ROAD

    def test_a_closed_hold_position_breaks_with_its_reason(self):
        world = _boot()
        davout = _place(world, "Davout", "Gelderland")
        davout.strategic_order = _order("HOLD", "Brunswick", ["Brunswick"])
        report = _tick(world, davout)
        assert report.get("order_status") == "breaks", report
        message = report.get("message", "")
        assert "Cannot enter Brunswick" in message and "declare war" in message
        assert "Cannot reach" not in message
        assert davout.strategic_order is None


# ═══════════════════════════════════════════════════════════════════════
# FA-N41 — the SUPPORT stall speaks
# ═══════════════════════════════════════════════════════════════════════

class TestTheSupportStallSpeaks:

    def _support(self, world, who, ally):
        marshal = world.get_marshal(who)
        marshal.strategic_order = StrategicOrder(
            command_type="SUPPORT", target=ally, target_type="marshal",
            started_turn=0, issued_turn=0, path=[world.get_marshal(ally).location],
            original_command=f"{who}, support {ally}")
        return marshal

    def test_a_covered_strait_breaks_the_support_at_the_waters_edge(self):
        world = _boot()
        ney = _place(world, "Ney", "Normandy")
        _place(world, "Massena", "London")
        _place(world, "Moore", "East Anglia")
        self._support(world, "Ney", "Massena")
        report = _tick(world, ney)
        assert report.get("order_status") == "breaks", report
        message = report.get("message", "")
        assert "water's edge" in message and "Royal Navy" in message
        assert "lapses" in message
        assert ney.strategic_order is None

    def test_a_closed_border_breaks_the_support_naming_the_lapse(self):
        world = _boot()
        soult = _place(world, "Soult", "Rhineland")
        _place(world, "Davout", "Frankfurt")
        self._support(world, "Soult", "Davout")
        report = _tick(world, soult)
        assert report.get("order_status") == "breaks", report
        message = report.get("message", "")
        assert "Cannot enter Frankfurt" in message
        assert "authorization" in message and "Davout's guns" in message
        assert soult.strategic_order is None

    def test_the_lever_off_arm_re_stalls_forever(self, monkeypatch):
        monkeypatch.setattr(strategic_mod, "SUPPORT_STALL_SPEAKS", False)
        world = _boot()
        ney = _place(world, "Ney", "Normandy")
        _place(world, "Massena", "London")
        _place(world, "Moore", "East Anglia")
        self._support(world, "Ney", "Massena")
        for _ in range(2):
            report = _tick(world, ney)
            assert report.get("order_status") == "error"
            assert "could not move toward" in report.get("message", "")
            assert ney.strategic_order is not None


# ═══════════════════════════════════════════════════════════════════════
# A stale road never mints a new order
# ═══════════════════════════════════════════════════════════════════════

class TestAStaleRoadNeverMintsAnOrder:

    def test_move_to_with_a_stale_first_step_keeps_its_destination(self):
        world = _boot()
        ney = _place(world, "Ney", "Flanders")
        ney.strategic_order = _order("MOVE_TO", "Normandy", ["Artois", "Normandy"])
        report = _tick(world, ney)
        assert report.get("order_status") == "continues", report
        assert ney.location == "Picardy"
        assert ney.strategic_order.target == "Normandy"
        assert ney.strategic_order.path == ["Artois", "Normandy"]

    def test_a_strategic_step_two_provinces_off_is_refused(self):
        world = _boot()
        ney = _place(world, "Ney", "Flanders")
        with _quiet():
            result = CommandExecutor().execute(
                {"command": {"marshal": "Ney", "action": "move", "target": "Artois",
                             "_strategic_execution": True}}, {"world": world})
        assert result.get("success") is False
        assert result.get("stale_road") is True
        assert ney.strategic_order is None
        assert ney.location == "Flanders"

    def test_the_lever_off_arm_loses_the_destination(self, monkeypatch):
        """The measured hazard: the auto-upgrade replaced 'march to Normandy'
        with an order for Artois."""
        monkeypatch.setattr(strategic_mod, "STALE_ROAD_REPLOTS", False)
        monkeypatch.setattr(strategic_mod, "STRATEGIC_STEP_NEVER_UPGRADES", False)
        world = _boot()
        ney = _place(world, "Ney", "Flanders")
        ney.strategic_order = _order("MOVE_TO", "Normandy", ["Artois", "Normandy"])
        _tick(world, ney)
        assert ney.strategic_order is not None
        assert ney.strategic_order.target == "Artois"


# ═══════════════════════════════════════════════════════════════════════
# The three re-plots and the compromise obey the law
# ═══════════════════════════════════════════════════════════════════════

class TestTheReroutesObeyTheLaw:

    def _blocked_at_picardy(self, who):
        world = _boot()
        marshal = _place(world, who, "Flanders")
        _place(world, "Mack", "Picardy", 5000)
        assert world.get_visible_enemies_in_region("Picardy", "France")
        return world, marshal

    def test_the_literal_reroute_prefers_a_lawful_road(self):
        world, soult = self._blocked_at_picardy("Soult")
        soult.strategic_order = _order("MOVE_TO", "Normandy", LAWFUL_ROAD)
        report = _tick(world, soult)
        assert report.get("action") == "reroute", report
        road = [soult.location] + list(soult.strategic_order.path)
        assert "Picardy" not in road and "Westphalia" not in road, road
        assert _lawful(world, road)

    def test_go_around_prefers_a_lawful_road(self):
        world, ney = self._blocked_at_picardy("Ney")
        ney.strategic_order = _order("MOVE_TO", "Normandy", LAWFUL_ROAD)
        pending = {"interrupt_type": "destination_blocked", "marshal": "Ney",
                   "enemy": "Mack", "location": "Picardy"}
        proc = StrategicOrderProcessor(CommandExecutor())
        with _quiet():
            result = proc._respond_blocked_path(ney, ney.strategic_order, "go_around",
                                                pending, world, {"world": world})
        assert result.get("action_taken") == "go_around", result
        road = [ney.location] + list(ney.strategic_order.path)
        assert "Picardy" not in road and "Westphalia" not in road, road
        assert _lawful(world, road)

    def test_the_first_step_reroute_prefers_a_lawful_road(self):
        world, soult = self._blocked_at_picardy("Soult")
        with _served(world) as client:
            reply = _post(client, "Soult, march to Normandy")
        assert reply.get("success") is True, reply.get("message")
        assert soult.strategic_order is not None
        road = [soult.location] + list(soult.strategic_order.path)
        assert "Picardy" not in road and "Westphalia" not in road, road
        assert _lawful(world, road)

    def test_the_objection_compromise_prefers_a_lawful_road(self):
        world, davout = self._blocked_at_picardy("Davout")
        world.pending_strategic_objection = {
            "marshal_name": "Davout",
            "original_command": {"marshal": "Davout", "action": "move",
                                 "target": "Normandy"},
            "parsed_command": {"command": {"marshal": "Davout", "action": "move",
                                           "target": "Normandy"}},
            "strategic_type": "MOVE_TO", "path": [], "target": "Normandy",
            "options": [
                {"type": "proceed", "text": "Proceed", "trust_change": -10, "ap_cost": 2},
                {"type": "compromise", "text": "Compromise: safe road",
                 "trust_change": 3, "ap_cost": 2, "compromise": {"safe_path": True}}],
            "trust_gain": 8, "insist_penalty": -10,
        }
        executor = CommandExecutor()
        with _quiet():
            result = executor._strategic._handle_strategic_objection_from_endpoint(
                "compromise", {"world": world})
        assert result.get("success") is True, result
        assert davout.strategic_order is not None
        road = [davout.location] + list(davout.strategic_order.path)
        assert "Picardy" not in road and "Westphalia" not in road, road
        assert _lawful(world, road)


# ═══════════════════════════════════════════════════════════════════════
# One seam
# ═══════════════════════════════════════════════════════════════════════

class TestOneSeam:

    CASES = [("Ney", "Flanders", "Normandy"), ("Davout", "Flanders", "Normandy"),
             ("Soult", "Lorraine", "Brunswick"), ("Mack", "Swabia", "Paris"),
             ("Moore", "London", "Paris"), ("Davout", "Rhineland", "Vienna")]

    def test_the_per_turn_helper_is_byte_identical_to_its_inline_copy(self, monkeypatch):
        world = _boot()
        proc = StrategicOrderProcessor(CommandExecutor())
        for who, here, there in self.CASES:
            marshal = _place(world, who, here)
            arms = []
            for lever in (True, False):
                monkeypatch.setattr(strategic_mod, "ROAD_LAW_ONE_SEAM", lever)
                arms.append((proc._get_personality_aware_path(marshal, there, world, use_weighted=True),
                             proc._get_personality_aware_path(marshal, there, world, use_weighted=False)))
            assert arms[0] == arms[1], (who, here, there, arms)
            assert arms[0][0], (who, here, there)

    def test_the_fog_scan_is_one_source(self, monkeypatch):
        world = _boot()
        davout = _place(world, "Davout", "Rhineland")
        _place(world, "Mack", "Brunswick", 5000)
        assert not world.get_visible_enemies_in_region("Brunswick", "France")
        proc = StrategicOrderProcessor(CommandExecutor())
        monkeypatch.setattr(strategic_mod, "ROAD_LAW_ONE_SEAM", False)
        inline = proc._get_enemy_occupied_regions("France", world, marshal=davout)
        monkeypatch.setattr(strategic_mod, "ROAD_LAW_ONE_SEAM", True)
        assert enemy_occupied_regions(world, "France", marshal=davout) == inline
        assert "Brunswick" not in inline
        assert "Brunswick" in enemy_occupied_regions(world, "France", fog_aware=False)

    def test_an_ai_corps_plots_omnisciently_and_gets_no_verdict(self):
        world = _boot()
        mack = world.get_marshal("Mack")
        road, verdict = plot_route(world, mack, "Paris", use_weighted=True,
                                   want_verdict=True)
        assert verdict is None
        raw = world.find_weighted_path(mack.location, "Paris")
        assert road == [r for r in raw if r != mack.location]

    def test_region_is_adjacent_reads_walkability_including_the_sea_link(self):
        world = _boot()
        assert region_is_adjacent(world, "Normandy", "London")
        assert region_is_adjacent(world, "Flanders", "Picardy")
        assert not region_is_adjacent(world, "Flanders", "Artois")
        assert not region_is_adjacent(world, "", "Artois")


# ═══════════════════════════════════════════════════════════════════════
# FA-54's rule holds on the refusal
# ═══════════════════════════════════════════════════════════════════════

class TestTheSubstitutionNoteRidesTheRefusal:

    def test_a_substituted_closed_destination_is_disclosed(self):
        world = _boot()
        with _served(world) as client:
            reply = _post(client, "Ney, march to Lisboa")
        message = reply.get("message") or ""
        assert reply.get("success") is False
        assert "Cannot enter Lisbon" in message
        assert "Our maps read" in message, message


@pytest.fixture(autouse=True)
def _levers_at_default():
    """Every lever on for every test unless a test flips it itself."""
    names = ("ROAD_LAW_AT_ISSUANCE", "ROAD_LAW_ON_REPLOT", "ROAD_LAW_ONE_SEAM",
             "HOLD_KEEPS_ITS_ROAD", "SUPPORT_STALL_SPEAKS", "STALE_ROAD_REPLOTS",
             "STRATEGIC_STEP_NEVER_UPGRADES")
    saved = {n: getattr(strategic_mod, n) for n in names}
    yield
    for n, v in saved.items():
        setattr(strategic_mod, n, v)
