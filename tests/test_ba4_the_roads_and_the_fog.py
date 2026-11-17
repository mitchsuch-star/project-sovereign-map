"""Row BA, session BA-4 — "the roads and the fog" (November 16, 2026).

The row's last session before the deploy: every open row that moves a
measured world-line, each behind a zero-argument seam in the module it gates,
with ONE measure (`tools/_ba4_measure.py`). The gate and the landing record
are `docs/BATTLE_DIORAMA_SPEC.md` §15.19 and §15.20; the rules are
`docs/SYSTEMS_REFERENCE.md` §222; the ledger rows are `docs/BUG_FIXES.md`
§BA2 and §BA3.

A class a rule. Where a rule reverses or replaces what the game did, a twin
holds its seam down and shows the game before it — the seam is the one line
that reverses the rule, and the twin proves the test can fail.

Each case is staged on the 1805 board (`tools.ba1_stage_battles._board`) and
judged by the game: an order is sent through the real executor and the world
read after it. A day of battle exists only in a campaign the game server
holds, so the day's rows play through `TestClient` (`Table`, as
`tests/test_ba3_the_rounds.py` does).
"""

import copy
import importlib
import json
import random
import re
import types
from pathlib import Path

import pytest

from backend.ai import enemy_ai
from backend.commands import combat_executor, movement_executor, order_quotes, relay
from backend.commands import strategic as road_law
from backend.commands.executor import CommandExecutor
from backend.game_logic import battle_day as BD
from backend.game_logic import battle_news, battle_script, intel_surfaces
from backend.game_logic import campaign_variance
from backend.game_logic.diplomacy import can_enter_territory
from backend.models.intel import FULL, PARTIAL
from backend.models.world_state import WorldState
from tests._ba4_seams import BA4_SEAMS_BY_ROW, BA4_SEAMS_DOWN, BA4_SESSION_OFF, BA4_THE_KEY_BAR
from tests._oct27_seams import OCT27_SEAMS_DOWN, parse
from tests.test_ba3_the_review import _a_day, _served
from tests.test_ba3_the_rounds import (  # noqa: F401  (`table` is the served-campaign fixture)
    HOME, Table, _awaits_us, _chip, _mk, _quiet, _seat, table,
)
from tools import ba1_stage_battles as STAGE

REPO = Path(__file__).resolve().parents[1]


def _down(monkeypatch, module, name, value=False):
    """Hold ONE seam down (or at `value`) for a test — the seam's own form:
    a zero-argument function read through its module."""
    assert callable(getattr(module, name)), f"{module.__name__}.{name} is no seam"
    monkeypatch.setattr(module, name, lambda *a, **k: value)


# ════════════════════════════════════════════════════════════════════════
# The seams themselves
# ════════════════════════════════════════════════════════════════════════

class TestTheSeams:
    """Every rule of the session is one function to reverse, and every
    recorded board holds it down."""

    @pytest.mark.parametrize("spec", BA4_SEAMS_DOWN)
    def test_each_is_a_zero_argument_function_that_stands_up(self, spec):
        module_name, attr, expr = parse(spec)
        seam = getattr(importlib.import_module(module_name), attr)
        assert callable(seam) and seam() is True, spec
        assert expr == "False", f"{spec}: the session OFF is the seam down"

    def test_the_recorded_boards_hold_every_one_of_them_down(self):
        assert BA4_SEAMS_DOWN, "the session has seams"
        missing = [spec for spec in BA4_SEAMS_DOWN if spec not in OCT27_SEAMS_DOWN]
        assert not missing, missing

    def test_a_row_names_the_rule_it_reverses(self):
        for row, specs in BA4_SEAMS_BY_ROW.items():
            assert specs and all(spec.startswith("backend.") for spec in specs), row

    def test_no_seam_is_a_module_lever(self):
        """The code-health ratchet caps module-level booleans at 231 of 231:
        a seam is a FUNCTION."""
        for spec in BA4_SEAMS_DOWN:
            module_name, attr, _expr = parse(spec)
            source = Path(importlib.import_module(module_name).__file__).read_text(encoding="utf-8")
            assert f"def {attr}() -> bool:" in source, spec


# ════════════════════════════════════════════════════════════════════════
# BA2-X2 (P1) — a court's turn is not lost to a corps raised again mid-phase
# ════════════════════════════════════════════════════════════════════════

class TestACourtsTurnIsNotLost:
    """The AI phase's fairness tally was built once, from the phase's opening
    roster (a corps with men). The roster is read again at every action, so a
    corps beaten to nothing and raised again while the phase ran was chosen —
    and the tally had no key for him: `KeyError`, the court's whole turn lost
    (seed jena, Prussia, Yorck: "Prussia did not complete its turn")."""

    @staticmethod
    def _phase():
        """Austria's phase on the 1805 board with the Archduke John at
        nothing when it opens; the first pick raises him again and names him."""
        world, executor = STAGE._board()
        john = world.marshals["ArchdukeJohn"]
        john.strength = 0
        assert john.name not in [m.name for m in world.get_marshals_by_nation("Austria")], \
            "a corps at nothing is not on the roster the phase opens with"
        ai = enemy_ai.EnemyAI(executor)
        picks = {"n": 0}

        def pick(marshals, nation, world_, actions_used, failed_actions=None):
            picks["n"] += 1
            if picks["n"] == 1:
                john.strength = 5000
                return john, {"action": "wait", "marshal": john.name}, 9
            return None, None, 999

        ai._select_next_marshal_action = pick
        return ai, world, executor, john

    def test_a_corps_raised_mid_phase_takes_its_turn(self):
        ai, world, executor, john = self._phase()
        with STAGE._quiet():
            results = ai._process_nation_turn_marked(
                "Austria", world, {"world": world, "executor": executor})
        assert [(row.get("ai_action") or {}).get("marshal") for row in results] == [john.name]

    def test_the_seam_down_is_the_turn_that_was_lost(self, monkeypatch):
        _down(monkeypatch, enemy_ai, "a_corps_raised_mid_phase_takes_its_turn")
        ai, world, executor, john = self._phase()
        with STAGE._quiet(), pytest.raises(KeyError, match=john.name):
            ai._process_nation_turn_marked("Austria", world, {"world": world, "executor": executor})

    def test_the_sweep_no_other_tally_is_built_from_the_opening_roster(self):
        """Rule 10. In `backend/` the only dict built `{corps: … for corps in
        roster}` and then INDEXED by a corps picked later is the tally: the
        others of the phase (`_marshal_visited_locations`, `_consecutive_waits`,
        `_walk_ins_this_turn`, the stagnation counters) are read with `.get`
        or guarded by `in`."""
        source = Path(enemy_ai.__file__).read_text(encoding="utf-8")
        assert source.count("{m.name: 0 for m in marshals}") == 1
        phase = source[source.index("def _process_nation_turn_marked"):
                       source.index("def _select_next_marshal_action")]
        assert "actions_used.get(_tallied, 0) + 1" in phase
        assert "if marshal_name not in self._marshal_visited_locations:" in phase
        assert "self._consecutive_waits.get(selected_marshal.name, 0) + 1" in phase
        assert "self._walk_ins_this_turn.get(selected_action[\"marshal\"], 0) + 1" in phase


# ════════════════════════════════════════════════════════════════════════
# BA2-X12 — a battery is never caught by its own fire
# ════════════════════════════════════════════════════════════════════════

class TestABatteryIsSparedItsOwnShells:
    """`_execute_bombardment` rolled stray shells for every corps in the
    target's province but the target — the firing battery too, when it stood
    there. Four roads reach it at that distance (the post-objection road and
    the two defiance roads take the nearest enemy within two provinces; a gun
    ordered in support fires from inside the battle's province); the roll is
    left out in the one function all four end in."""

    @staticmethod
    def _salvo(seed):
        world, executor = STAGE._board()
        STAGE._marmont(world)
        STAGE._place(world, Marmont="Swabia")
        board = copy.deepcopy(world)
        random.seed(seed)
        with STAGE._quiet():
            result = executor._combat._execute_bombardment(
                board.marshals["Marmont"], board.marshals["Mack"], board,
                {"world": board, "executor": executor})
        return board, result

    @pytest.mark.parametrize("seed", range(6))
    def test_no_salvo_names_its_own_battery(self, seed):
        _board, result = self._salvo(seed)
        assert "Marmont" not in [row["name"] for row in result["bombardment_result"]["collateral"]]
        assert "FRIENDLY FIRE: Marmont" not in result["message"]

    def test_the_seam_down_is_the_battery_under_its_own_shells(self, monkeypatch):
        _down(monkeypatch, combat_executor, "a_battery_is_spared_its_own_shells")
        hit = [seed for seed in range(6)
               if "Marmont" in [row["name"] for row in
                                self._salvo(seed)[1]["bombardment_result"]["collateral"]]]
        assert hit, "with the rule off a battery in its target's province shells itself"

    def test_a_friend_beside_the_target_is_still_under_the_guns(self):
        """The rule spares the battery, not the field: another corps of ours
        in the target's province still takes its stray shells (§4.4)."""
        caught = 0
        for seed in range(12):
            world, executor = STAGE._board()
            STAGE._marmont(world)
            STAGE._place(world, Marmont="Swabia", Lannes="Swabia")
            random.seed(seed)
            with STAGE._quiet():
                result = executor._combat._execute_bombardment(
                    world.marshals["Marmont"], world.marshals["Mack"], world,
                    {"world": world, "executor": executor})
            caught += "Lannes" in [row["name"] for row in result["bombardment_result"]["collateral"]]
        assert caught, "a corps of ours beside the target is still rolled for"

    def test_the_roll_is_left_out_where_every_road_ends(self):
        source = Path(combat_executor.__file__).read_text(encoding="utf-8")
        body = source[source.index("    def _execute_bombardment("):]
        body = body[:body.index("\n    def ", 10)]
        assert "m.name != marshal.name or not a_battery_is_spared_its_own_shells()" in body


# ════════════════════════════════════════════════════════════════════════
# Helpers for the roads: the 1805 board, staged; an order sent as the client
# sends it
# ════════════════════════════════════════════════════════════════════════

def _staged(mack_at, lead, lead_at, corps, corps_at):
    """The 1805 board with Mack, a lead and a corps of ours put where the case
    needs them, Mack's province seen whole, no order standing."""
    world, executor = STAGE._board()
    world.marshals["Mack"].location = mack_at
    world.get_region_intel(mack_at).visibility = FULL
    world.marshals[lead].location = lead_at
    world.marshals[corps].location = corps_at
    for marshal in world.marshals.values():
        marshal.strategic_order = None
    return world, executor


def _order(world, executor, command, marshal, action, target, strategic_type):
    parsed = {"command": {"raw_input": command, "marshal": marshal, "action": action,
                          "target": target},
              "is_strategic": True, "strategic_type": strategic_type}
    random.seed(11)
    with STAGE._quiet():
        return executor.execute(parsed, {"world": world})


def _support(world, executor, corps, lead):
    return _order(world, executor, f"{corps}, support {lead}", corps, "support", lead, "SUPPORT")


def _lit(world, lead, enemy="Mack"):
    """The chips an attack by `lead` offers LIT, by the corps they bring."""
    quote = order_quotes.attack_quote(world, world.marshals[lead], world.marshals[enemy])
    assert quote["ok"], quote.get("refusal")
    return {row["marshal"]: row for row in quote["bring"] if row["ok"]}


def _may_walk(world, marshal, road):
    """The first province of `road` (short of its end) the corps may NOT
    enter — the move's own rule — or None when the road is lawful."""
    here = marshal.location
    for province in list(road)[:-1]:
        holder = getattr(world.get_region(province), "controller", None)
        if holder and holder != marshal.nation and not can_enter_territory(
                world, marshal.nation, holder, mover_location=here):
            return province
        here = province
    return None


# ════════════════════════════════════════════════════════════════════════
# The approach rule (ruled IN) — a support order meets the corps to be attacked
# ════════════════════════════════════════════════════════════════════════

class TestASupportOrderMeetsTheCorpsToBeAttacked:
    """Murat stands at Franche-Comte; his road to Ney at the Rhineland runs
    through Swabia, where Mack stands — within Ney's reach, the very corps Ney
    is to attack. The order used to stop him on "Mack blocks the path at
    Swabia. Odds unfavorable. Your orders?", and of that question's four
    answers one kept the order: a corps like Murat could not be committed by
    an order at all. Ruled IN (§15.14 ruling 14): the order halts at the
    approach — the arm it already had when the foe held the friend's own
    province (DDB-20) — and he joins the next attack there."""

    def test_murat_halts_beside_mack_and_no_question_is_raised(self):
        world, executor = STAGE._board()
        murat = world.marshals["Murat"]
        before, stood = world.actions_remaining, murat.location
        result = _support(world, executor, "Murat", "Ney")
        assert result["success"] and not result.get("requires_input")
        assert murat.pending_interrupt is None
        assert murat.location == stood == "Franche-Comte"
        assert murat.strategic_order.command_type == "SUPPORT" and murat.strategic_order.path == []
        assert world.actions_remaining == before - 1
        assert result["message"] == ("Murat stands at Franche-Comte, at the approach to Swabia — "
                                     "he joins Ney's next attack there.")
        assert "Joins him in" not in result["message"], "a halted order promises no arrival"

    def test_the_muster_then_counts_him(self):
        world, executor = STAGE._board()
        murat, ney = world.marshals["Murat"], world.marshals["Ney"]
        _support(world, executor, "Murat", "Ney")
        assert executor._combat._muster_reason(murat, ney, "Swabia", "France", world) == (
            True, "has_support_order")

    def test_the_quote_says_what_the_order_does_and_the_chip_is_offered(self):
        world, executor = STAGE._board()
        murat, ney = world.marshals["Murat"], world.marshals["Ney"]
        quote = order_quotes.support_quote(world, murat, ney)
        assert quote["ok"] and quote["ap"] == 1
        assert quote["contact"] == ("Mack blocks the road at Swabia — Murat halts at the approach "
                                    "and joins the next attack there (1 action now).")
        assert order_quotes._stop_this_turn(world, murat, quote) == "Franche-Comte"
        row = _lit(world, "Ney")["Murat"]
        # the oracle: the chip's order, sent, leaves him with the odds it named
        _support(world, executor, "Murat", "Ney")
        real = executor._combat._arrival_odds_row(ney, murat, "Swabia", world, "has_support_order")
        assert row["odds_with"] == int(real["arrival_odds"])

    def test_a_foe_out_of_the_friends_reach_keeps_the_personality_arms(self):
        """The predicate itself: a foe on the friend's own province, or within
        the friend's attack reach — never further."""
        world, _executor = STAGE._board()
        ney = world.marshals["Ney"]
        order = types.SimpleNamespace(command_type="SUPPORT")
        assert ney.location == "Rhineland" and world.get_distance("Rhineland", "Swabia") == 1
        assert road_law.support_stands_at_approach(order, ney, "Swabia", world)
        far = next(name for name in world.regions if world.get_distance("Rhineland", name) == 3)
        assert not road_law.support_stands_at_approach(order, ney, far, world)
        march = types.SimpleNamespace(command_type="MOVE_TO")
        assert not road_law.support_stands_at_approach(march, ney, "Swabia", world), \
            "only a SUPPORT order halts at the approach"

    def test_the_seam_down_is_the_question_he_used_to_ask(self, monkeypatch):
        _down(monkeypatch, road_law, "a_support_order_halts_before_the_friends_foe")
        world, executor = STAGE._board()
        murat, ney = world.marshals["Murat"], world.marshals["Ney"]
        quote = order_quotes.support_quote(world, murat, ney)
        assert "asks your orders" in quote["contact"]
        assert "Murat" not in _lit(world, "Ney"), "an order that asks is not an order that brings"
        result = _support(world, executor, "Murat", "Ney")
        assert result.get("requires_input") and murat.pending_interrupt
        assert murat.pending_interrupt["interrupt_type"] == "contact_bad_odds"

    def test_ddb20s_arm_stands_with_the_seam_down(self, monkeypatch):
        """The foe on the friend's OWN province: the arm the order already
        had, with or without BA-4's rule."""
        _down(monkeypatch, road_law, "a_support_order_halts_before_the_friends_foe")
        world, _executor = STAGE._board()
        order = types.SimpleNamespace(command_type="SUPPORT")
        ally = types.SimpleNamespace(location="Swabia", movement_range=1)
        assert road_law.support_stands_at_approach(order, ally, "Swabia")
        assert road_law.support_stands_at_approach(order, ally, "Swabia", world)
        assert not road_law.support_stands_at_approach(order, ally, "Munich", world)

    def test_one_predicate_for_the_step_the_tick_and_the_quote(self):
        executor_source = (REPO / "backend" / "commands" / "strategic_executor.py").read_text(encoding="utf-8")
        tick_source = Path(road_law.__file__).read_text(encoding="utf-8")
        quote_source = Path(order_quotes.__file__).read_text(encoding="utf-8")
        assert "support_stands_at_approach(order, _ally, blocked_region, world)" in executor_source
        assert "support_stands_at_approach(order, ally, next_region, world)" in tick_source
        assert "road_law.support_stands_at_approach(_A_SUPPORT_ORDER, ally, region, world)" in quote_source

    def test_a_follow_is_quoted_as_the_support_it_is(self):
        """The sibling sweep: a follow is a SUPPORT order — the executor's arm
        halts it too; its quote said "asks your orders"."""
        world, _executor = STAGE._board()
        murat, ney = world.marshals["Murat"], world.marshals["Ney"]
        quote = order_quotes.follow_quote(world, murat, ney)
        assert "halts at the approach and joins the next attack there" in quote["contact"]


# ════════════════════════════════════════════════════════════════════════
# BA2-X10 — a road round a corps keeps to open frontiers
# ════════════════════════════════════════════════════════════════════════

class TestARoadRoundKeepsToOpenFrontiers:
    """A reroute's last rung dropped the frontier law, and a court's corps
    never had it: Soult's road round Mack began at Dresden (Saxony, at peace
    with France, its frontier shut) — the order was taken, the first march
    refused without a word, and the reply promised an arrival."""

    @staticmethod
    def _courts_road(seam_up, monkeypatch):
        """Austria's Mack at Bohemia with a French corps on his road at
        Franconia: his road ROUND it to the Rhineland."""
        _down(monkeypatch, road_law, "a_road_round_keeps_to_open_frontiers", seam_up)
        world, _executor = STAGE._board()
        mack, ney = world.marshals["Mack"], world.marshals["Ney"]
        mack.location, ney.location = "Bohemia", "Franconia"
        if hasattr(world, "refresh_marshal_indexes"):
            world.refresh_marshal_indexes()
        avoid = [name for name in world.regions if world.get_enemies_in_region(name, "Austria")]
        road, _verdict = road_law.plot_route(world, mack, "Rhineland", use_weighted=True,
                                             avoid_regions=avoid, avoid_is_law=True)
        return world, mack, road

    def test_a_courts_road_round_is_one_it_can_walk(self, monkeypatch):
        world, mack, road = self._courts_road(True, monkeypatch)
        assert road and _may_walk(world, mack, road) is None
        assert "Dresden" not in road

    def test_the_seam_down_is_the_road_through_saxony(self, monkeypatch):
        world, mack, road = self._courts_road(False, monkeypatch)
        assert road[0] == "Dresden" and _may_walk(world, mack, road) == "Dresden"

    def test_where_no_road_goes_round_the_order_ends_at_the_approach_and_says_so(self, monkeypatch):
        """The player's road: Soult at Bohemia, Mack at Franconia (the approach
        rule held down so that the reroute is asked for). No lawful road goes
        round: the quote refuses, and the order — sent all the same — is
        refused with nothing spent and no arrival promised."""
        _down(monkeypatch, road_law, "a_support_order_halts_before_the_friends_foe")
        world, executor = _staged("Franconia", "Ney", "Swabia", "Soult", "Bohemia")
        soult, ney = world.marshals["Soult"], world.marshals["Ney"]
        quote = order_quotes.support_quote(world, soult, ney)
        assert not quote["ok"] and quote["refusal"] == "Path blocked at Franconia, no alternate route."
        before = world.actions_remaining
        result = _support(world, executor, "Soult", "Ney")
        assert not result["success"] and world.actions_remaining == before
        assert soult.location == "Bohemia" and soult.strategic_order is None
        assert result["message"] == (
            "Path blocked at Franconia, no alternate route: no road round it lies over ground "
            "Soult may enter. He halts at Bohemia, at the approach, and awaits new orders.")
        assert "Joins him" not in result["message"] and "Adjusting route" not in result["message"]

    def test_the_seam_down_is_the_arrival_it_could_not_keep(self, monkeypatch):
        _down(monkeypatch, road_law, "a_support_order_halts_before_the_friends_foe")
        _down(monkeypatch, road_law, "a_road_round_keeps_to_open_frontiers")
        world, executor = _staged("Franconia", "Ney", "Swabia", "Soult", "Bohemia")
        soult = world.marshals["Soult"]
        result = _support(world, executor, "Soult", "Ney")
        assert result["success"] and "Joins him in" in result["message"]
        assert "Adjusting route to avoid Franconia" in result["message"]
        assert soult.location == "Bohemia" and soult.strategic_order.path[0] == "Dresden"

    def test_every_copy_of_the_ladder_reads_the_one_gate(self):
        """Rule 10: `plot_route` and the quote's batch copy of it
        (`order_quotes._literal_detours`, one pathfinding pass for every
        destination) climb the same ladder."""
        assert "if avoid_is_law and a_road_round_keeps_to_open_frontiers():" in \
            Path(road_law.__file__).read_text(encoding="utf-8")
        quotes = Path(order_quotes.__file__).read_text(encoding="utf-8")
        body = quotes[quotes.index("def _literal_detours("):quotes.index("def support_quote(")]
        assert "road_law.a_road_round_keeps_to_open_frontiers()" in body
        assert "if pf and not lawful_only:" in body


# ════════════════════════════════════════════════════════════════════════
# BA2-X21 — a quote names the men its first march costs
# ════════════════════════════════════════════════════════════════════════

class TestAQuoteNamesTheMenItsFirstMarchCosts:
    """A standing order's first march is taken the moment the order is given,
    and it costs men by the ordinary march rule. The quote named the price in
    actions, the road, the detour, the guard, the pay — and not the men."""

    @staticmethod
    def _case():
        world, executor = _staged("Bohemia", "Ney", "Munich", "Soult", "Swabia")
        return world, executor, world.marshals["Ney"], world.marshals["Soult"]

    def test_the_reader_and_the_mover_are_one_rule(self):
        """The calculation is split from its application: the mover applies
        exactly what the pure reader returns."""
        world, executor, _ney, soult = self._case()
        twin = copy.copy(soult)
        read = movement_executor.march_attrition_reading(world, twin, "Munich")
        assert int(twin.strength) == int(soult.strength), "the reader writes nothing"
        before = int(soult.strength)
        applied = executor._movement._calculate_movement_attrition(soult, "Munich", world)
        assert applied == read and before - int(soult.strength) == read["total_losses"] > 0

    @pytest.mark.parametrize("kind", ["support", "follow", "march"])
    def test_every_order_that_marches_at_once_says_it(self, kind):
        world, executor, ney, soult = self._case()
        quote = {"support": lambda: order_quotes.support_quote(world, soult, ney),
                 "follow": lambda: order_quotes.follow_quote(world, soult, ney),
                 "march": lambda: order_quotes.march_quote(world, soult, "Munich")}[kind]()
        before = int(soult.strength)
        action, target, strategic = {"support": ("support", "Ney", "SUPPORT"),
                                     "follow": ("follow", "Ney", "SUPPORT"),
                                     "march": ("move", "Munich", "MOVE_TO")}[kind]
        result = _order(world, executor, quote["command"], "Soult", action, target, strategic)
        assert result["success"], result.get("message")
        lost = before - int(soult.strength)
        assert lost > 0 and quote["march_cost"] == f"The first march costs {lost:,} men."

    def test_a_march_over_our_own_settled_soil_says_nothing(self):
        world, _executor = STAGE._board()
        soult = world.marshals["Soult"]
        home = next(name for name in world.get_region(soult.location).adjacent_regions
                    if world.get_region(name).controller == "France"
                    and world.get_region(name).stability >= 76)
        assert order_quotes.march_quote(world, soult, home)["march_cost"] == ""

    def test_an_order_whose_first_step_is_no_march_says_nothing(self):
        """Murat halts at the approach: nothing is walked, nothing is lost."""
        world, _executor = STAGE._board()
        quote = order_quotes.support_quote(world, world.marshals["Murat"], world.marshals["Ney"])
        assert quote["contact"] and quote["march_cost"] == ""

    def test_onto_an_enemys_ground_the_figure_is_about_and_names_no_works(self):
        """A stop held by a court at war: the march may take the province and
        its works may harass him — the quote says "about N, more if …" and
        never shows a fort the fog hides."""
        world, _executor = STAGE._board()
        ney = world.marshals["Ney"]
        ney.location = "Franche-Comte"
        world.marshals["Mack"].location = "Vienna"
        world.get_region("Swabia").controller = "Austria"
        line = order_quotes.march_cost_line(world, ney, ["Swabia"])
        read = movement_executor.march_attrition_reading(world, copy.copy(ney), "Swabia")
        assert line == (f"The first march costs about {read['march_losses']:,} men, "
                        f"more if Swabia's works harass him.")
        assert "fort" not in line.lower() and "garrison" not in line.lower()

    def test_a_bring_chip_inherits_its_orders_cost(self):
        world, _executor = STAGE._board()
        rows = _lit(world, "Ney")
        own = order_quotes.support_quote(world, world.marshals["Soult"], world.marshals["Ney"])
        assert rows["Soult"]["march_cost"] == own["march_cost"]

    def test_the_other_desks_print_it(self):
        from backend.game_logic import naval
        assert "march_cost" in naval._MARCH_QUOTE_LINES
        desk = (REPO / "backend" / "ai" / "state_desk.py").read_text(encoding="utf-8")
        assert 'march_cost = str(q.get("march_cost") or "")' in desk

    def test_the_client_prints_it_where_the_quotes_other_notes_are(self):
        scripts = REPO / "godot-client" / "project-sovereign" / "scripts"
        panel = (scripts / "region_panel.gd").read_text(encoding="utf-8")
        card = (scripts / "order_confirm_card.gd").read_text(encoding="utf-8")
        assert 'var march_cost := str(q.get("march_cost", ""))' in panel
        assert '["march_cost", "detour", "guard", "front", "terms"]' in panel
        assert card.count('q.get("march_cost", "")') == 2, "the order card and the group card"


# ════════════════════════════════════════════════════════════════════════
# BA2-X7 — the muster promises what the order delivers
# ════════════════════════════════════════════════════════════════════════

class TestTheMusterPromisesWhatTheOrderDelivers:
    """Berthier's muster named the order ("a written order ('Bernadotte,
    support Ney') would likely bring him") from where the corps STOOD. A
    SUPPORT order marches the corps toward the lead at once: Bernadotte goes
    to Munich, and from its mountains he cannot reach the field. The plan's
    chips were already held to the game; the muster's two sentences now read
    the same ONE source."""

    @staticmethod
    def _muster():
        world, executor = STAGE._board()
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        with STAGE._quiet():
            preview = executor._combat._build_muster_preview(ney, mack, world, {"world": world})
        return world, executor, {row["marshal"]: row for row in preview["rows"]}

    @staticmethod
    def _delivers(world, executor, name):
        ney = world.marshals["Ney"]
        m = world.marshals[name]
        beside = set(world.get_region("Swabia").adjacent_regions)
        will_join, code = executor._combat._muster_reason(m, ney, "Swabia", "France", world)
        now = (int(executor._combat._arrival_odds_row(ney, m, "Swabia", world, code)["arrival_odds"])
               if will_join else -1)
        return order_quotes.what_the_order_delivers(
            world, ney, m, "Swabia", beside, executor._combat, bool(will_join), now)

    def test_one_reading_of_what_the_order_delivers(self):
        world, executor = STAGE._board()
        soult, murat, bern = (self._delivers(world, executor, n) for n in ("Soult", "Murat", "Bernadotte"))
        assert soult["brings"] and soult["stop"] == "Rhineland" and soult["odds_with"] > 50
        assert murat["brings"] and murat["stop"] == "Franche-Comte" and murat["odds_with"] == 100
        assert not bern["brings"] and (bern["stop"], bern["why_not"]) == ("Munich", "no_odds")

    def test_the_hint_names_the_order_only_where_it_brings_him(self):
        _world, _executor, rows = self._muster()
        assert rows["Soult"]["standing_order_hint"] == "— order 'Soult, support Ney' and he will march"
        assert rows["Bernadotte"]["standing_order_hint"] == (
            "— an order to support Ney would march him to Munich, and from there he cannot "
            "reach this field in time")
        assert "support Ney'" not in rows["Bernadotte"]["standing_order_hint"], \
            "a sentence that puts the order in quotes is a promise"

    def test_the_arrival_note_names_the_odds_the_order_leaves_him_with(self):
        world, executor, rows = self._muster()
        chip = _lit(world, "Ney")["Murat"]
        assert (f"order 'Murat, support Ney' and it rises to about {chip['odds_with']}%"
                in rows["Murat"]["arrival_note"])

    def test_every_corps_the_muster_names_is_one_the_chips_offer(self):
        """On the opening board, for EVERY corps that could lead on Mack."""
        world, executor = STAGE._board()
        mack = world.marshals["Mack"]
        for lead in world.get_player_marshals():
            if lead.location == mack.location or int(lead.strength or 0) <= 0:
                continue
            if world.get_distance(lead.location, mack.location) > int(lead.movement_range or 1):
                continue
            with STAGE._quiet():
                preview = executor._combat._build_muster_preview(lead, mack, world, {"world": world})
            named = {row["marshal"] for row in preview["rows"]
                     if f", support {lead.name}'" in (str(row.get("standing_order_hint") or "")
                                                      + str(row.get("arrival_note") or ""))}
            # the chips also weigh the order's PRICE (BA2-X8); the muster's
            # sentence is about the order, so it is compared with what the
            # order delivers, whatever is left in the purse
            world.actions_remaining = 4
            offered = {b["marshal"] for b in order_quotes.bring_quotes(world, lead, mack) if b["ok"]}
            assert named <= offered, (lead.name, named - offered)

    def test_the_numbers_never_read_the_lever(self):
        world, executor = STAGE._board()
        ney, murat = world.marshals["Ney"], world.marshals["Murat"]
        plain = executor._combat._arrival_odds_row(ney, murat, "Swabia", world, "aggressive_marches")
        for lever in ({"brings": False, "why_not": "marches_away", "stop": "Munich", "odds_with": -1},
                      {"brings": True, "why_not": "", "stop": "Franche-Comte", "odds_with": 100}):
            told = executor._combat._arrival_odds_row(ney, murat, "Swabia", world,
                                                      "aggressive_marches", lever=lever)
            assert (told["arrival_odds"], told["arrival_odds_with_support"]) == (
                plain["arrival_odds"], plain["arrival_odds_with_support"])

    def test_a_courts_muster_reads_no_lever(self):
        world, executor = STAGE._board()
        mack, john = world.marshals["Mack"], world.marshals["ArchdukeJohn"]
        assert executor._combat._order_lever(mack, john, "Rhineland", set(), world, False,
                                             "literal_awaits_orders") is None

    def test_the_rule_off_is_the_promise_berthier_used_to_make(self, monkeypatch):
        _down(monkeypatch, combat_executor, "the_muster_names_only_an_order_that_brings")
        _world, _executor, rows = self._muster()
        assert rows["Bernadotte"]["standing_order_hint"] == (
            "— a written order ('Bernadotte, support Ney') would likely bring him")

    def test_the_reader_never_builds_the_muster_preview(self):
        """`_build_muster_preview` spends the one-time muster hint and now
        calls the reader: the reader must never call it back."""
        quotes = Path(order_quotes.__file__).read_text(encoding="utf-8")
        assert "_build_muster_preview(" not in quotes.replace("`_build_muster_preview`", "")


# ════════════════════════════════════════════════════════════════════════
# BA3-X5 — a quote says a word's price
# ════════════════════════════════════════════════════════════════════════

def _a_day_with_a_second_corps(table, **seat):
    """A served campaign with Ney's day against Mack open and awaiting us,
    and Davout beside Ney (a corps that can lead, and can be brought up)."""
    davout = _mk("Davout", HOME, 20000, personality="cautious")
    _body, day = table.open_a_day(_awaits_us, extra=(davout,), **seat)
    world = table.world
    return world, day, world.marshals["Ney"], world.marshals["Mack"], world.marshals["Davout"]


def _purse(world, enemy="Mack"):
    return int(((world.battle_days or {}).get("days") or {}).get(enemy, {}).get("ours", -1))


def _readback(table, line):
    return _quiet(table.tc.get, "/parse_preview", params={"line": line}).json()


class TestAQuoteSaysAWordsPrice:
    """While a day is open its own chips priced a word in points; every
    surface that quotes the SAME order outside them — the attack card, the
    plan's "Bring up" rows, the relay's note, the province's ordinary attack
    row, the readback — said "1 action", and the order then took a point and
    no action. ONE source: `battle_day.classify_word`, the door's own test."""

    def test_an_attack_on_the_days_enemy_is_quoted_in_points(self, table):
        world, _day, ney, mack, _davout = _a_day_with_a_second_corps(table)
        quote = order_quotes.attack_quote(world, ney, mack)
        assert (quote["ap"], quote["points"], quote["word"]) == (0, 1, "press")
        assert quote["price"] == "a word of the day — 1 point"

    def test_a_support_order_for_the_days_lead_is_quoted_in_points(self, table):
        world, _day, ney, _mack, davout = _a_day_with_a_second_corps(table)
        for quote in (order_quotes.support_quote(world, davout, ney),
                      order_quotes.follow_quote(world, davout, ney)):
            assert (quote["ap"], quote["points"], quote["word"]) == (0, 1, "bring_up")

    def test_the_oracle_send_then_read_the_pool_and_the_purse(self, table):
        """Every price surface agrees with what the order then takes."""
        for surface in ("attack", "another_leads", "support", "readback_defend"):
            # a campaign of its own a surface: a corps that marched to the guns
            # in the one before has spent his march, and the day's table then
            # offers no "Bring up" for him (his order is an ordinary one: BA4-X1)
            table.boot()
            world, _day, ney, mack, davout = _a_day_with_a_second_corps(table)
            if surface == "attack":
                quote = order_quotes.attack_quote(world, ney, mack)
            elif surface == "another_leads":
                quote = order_quotes.attack_quote(world, davout, mack)
            elif surface == "support":
                quote = order_quotes.support_quote(world, davout, ney)
            else:
                read = _readback(table, "Ney, defend")
                quote = {"command": "Ney, defend", "ap": read["ap"], "points": read["points"]}
            pool, purse = world.actions_remaining, _purse(world)
            sent = table.order(quote["command"])
            assert sent["success"], (surface, sent.get("message"))
            if (table.world.battle_days.get("days", {}).get("Mack") or {}).get("pending"):
                # the lead objected: the word is parked until he is answered
                assert table.answer("insist")["success"], surface
            world = table.world
            assert pool - world.actions_remaining == quote["ap"] == 0, surface
            spent = purse - _purse(world) if _purse(world) >= 0 else quote["points"]
            assert spent == quote["points"] == 1, surface

    def test_the_readback_says_it(self, table):
        _a_day_with_a_second_corps(table)
        for line, word in (("Ney, attack Mack", "press"), ("Davout, support Ney", "bring_up"),
                           ("Ney, defend", "dig_in"), ("Davout, attack Mack", "lead")):
            read = _readback(table, line)
            cost = [part["text"] for part in read["parts"] if part["role"] == "cost"]
            assert cost == ["a word of the day — 1 point"], (line, cost)
            assert (read["ap"], read["points"], read["word"]) == (0, 1, word), line

    def test_the_relays_note_says_it(self, table):
        world, *_ = _a_day_with_a_second_corps(table)
        note = relay.second_name_relay_note(world, "Davout", "Davout, support Ney")
        assert '"Davout, support Ney" (a word of the day — 1 point when sent)' in note
        assert "action" not in note

    def test_the_plans_rows_are_those_quotes(self, table):
        """A `bring` row IS a support quote: brought up on a day, it is priced
        in points — and offered though no action is left (it takes none)."""
        world, _day, ney, mack, _davout = _a_day_with_a_second_corps(table)
        # a literal corps beside the field, who will not march unordered
        spot = next(name for name in world.get_region(mack.location).adjacent_regions
                    if name != ney.location and not world.get_enemies_in_region(name, "France"))
        world.marshals["Soult"] = _mk("Soult", spot, 20000, personality="literal")
        world.actions_remaining = 0
        rows = [row for row in order_quotes.bring_quotes(world, ney, mack) if row["ok"]]
        assert rows, "an order that brings a corps is offered with no action left: it takes none"
        for row in rows:
            assert (row["ap"], row["points"], row["word"]) == (0, 1, "bring_up"), row["marshal"]
        # and with no action left the attack itself is still quoted as the word it is
        attack = order_quotes.attack_quote(world, ney, mack)
        assert attack["ok"] and (attack["ap"], attack["points"]) == (0, 1)

    def test_with_no_action_left_an_ordinary_order_is_still_refused(self, table):
        """The pool is set aside for a WORD's quote only."""
        world, _day, ney, mack, davout = _a_day_with_a_second_corps(table)
        world.actions_remaining = 0
        world.battle_days["days"]["Mack"]["ours"] = 0          # the purse cannot pay: no word
        attack = order_quotes.attack_quote(world, ney, mack)
        assert not attack["ok"] and "action" in attack["refusal"]

    def test_a_purse_that_cannot_pay_leaves_the_ordinary_price(self, table):
        """A purse spent is not a wall: the order is an ordinary order again,
        at its ordinary price — and its quote says THAT."""
        world, _day, ney, mack, davout = _a_day_with_a_second_corps(table)
        world.battle_days["days"]["Mack"]["ours"] = 0
        attack = order_quotes.attack_quote(world, ney, mack)
        support = order_quotes.support_quote(world, davout, ney)
        assert attack["ap"] == 1 and "points" not in attack and "word" not in attack
        assert support["ap"] == 1 and "points" not in support
        cost = [p["text"] for p in _readback(table, "Ney, attack Mack")["parts"] if p["role"] == "cost"]
        assert cost == ["1 action"]

    def test_with_no_day_open_every_quote_is_as_it_was(self, table):
        davout = _mk("Davout", HOME, 20000, personality="cautious")
        ney, mack = _seat(table.world, extra=(davout,))
        world = table.world
        quote = order_quotes.attack_quote(world, ney, mack)
        assert quote["ap"] == 1 and not ({"points", "word", "price"} & set(quote))
        assert "(1 action when sent)" in relay.second_name_relay_note(
            world, "Davout", "Davout, support Ney")

    def test_the_seam_down_is_the_quote_that_said_one_action(self, table, monkeypatch):
        _down(monkeypatch, BD, "a_word_is_quoted_in_points")
        world, _day, ney, mack, _davout = _a_day_with_a_second_corps(table)
        quote = order_quotes.attack_quote(world, ney, mack)
        assert quote["ap"] == 1 and "points" not in quote
        left = world.actions_remaining
        assert table.order(quote["command"])["success"]
        assert table.world.actions_remaining == left, "the order was a word all the same"

    def test_one_source_for_every_surface(self):
        """The quotes, the relay and the readback all ask `battle_day` — which
        asks `classify_word`, the test the door itself applies."""
        day = Path(BD.__file__).read_text(encoding="utf-8")
        assert "return classify_word(world, parsed)" in day
        quotes = Path(order_quotes.__file__).read_text(encoding="utf-8")
        assert quotes.count("_the_days_word(world, marshal.name,") == 3, "attack, support, follow"
        assert "_the_days_word(world, lead.name, \"attack\", enemy.name)" in quotes, \
            "the plan's rows weigh the attack at the same price"
        assert "_day.quoted_word(world, marshal.name, \"support\"," in \
            (REPO / "backend" / "commands" / "relay.py").read_text(encoding="utf-8")
        assert "_day.word_of(world, parsed)" in \
            (REPO / "backend" / "commands" / "parse_preview.py").read_text(encoding="utf-8")


# ════════════════════════════════════════════════════════════════════════
# §15.5.7 — the two rules of the battle: the pursuit, and the last hour
# ════════════════════════════════════════════════════════════════════════

def _beats_of(reply, kind):
    script = (reply.get("battle_diorama") or {}).get("script") or {}
    return [beat for act in script.get("acts", []) for beat in act["beats"]
            if beat["kind"] == kind]


def _fight(seed, lead="Ney", foe="Mack", *, tune=None, arrival=None):
    """`lead` attacks `foe` on the 1805 board with the dice seeded: (world,
    reply, seen). `tune(world, executor)` stages the board first. `arrival`
    fixes a corps' arrival roll at that many points over his bar (30 for
    every corps it does not name) — the roll's own draws are still made, so
    the dice after it stand. `seen` is what the resolver was handed."""
    world, executor = STAGE._board()
    combat = executor._combat
    if tune:
        tune(world, executor)
    if arrival is not None:
        real_score = combat._calculate_arrival_score
        field = world.marshals[foe].location

        def fixed(candidate, primary, world_, **kw):
            real_score(candidate, primary, world_, **kw)
            return (combat._arrival_threshold(candidate, primary, field, world_)
                    + arrival.get(candidate.name, 30))
        combat._calculate_arrival_score = fixed
    seen = {}
    real_resolve = combat.combat_resolver.resolve_battle

    def spy(**kw):
        seen.update(attacker=kw.get("committed_attacker"),
                    defender=kw.get("committed_defender"),
                    attacker_bodies=kw.get("attacker_bodies"),
                    defender_bodies=kw.get("defender_bodies"))
        return real_resolve(**kw)
    combat.combat_resolver.resolve_battle = spy
    random.seed(seed)
    with STAGE._quiet():
        reply = executor._execute_attack(world.marshals[lead], foe, world,
                                         {"world": world, "executor": executor})
    return world, reply, seen


def _a_rout(tune=None, seeds=range(16), arrival=None):
    """The first seed on which the attack routs its man and a pursuit fires."""
    for seed in seeds:
        world, reply, _seen = _fight(seed, tune=tune, arrival=arrival)
        if _beats_of(reply, "pursue"):
            return seed, world, reply
    raise RuntimeError("no rout with a pursuit on sixteen seeds: the board has changed")


# Blücher's ability, as the roster writes one (he is not on the 1805 board).
VORWAERTS = {"name": "Vorwärts!", "description": "Relentless pursuit of a beaten enemy.",
             "trigger": "enemy_retreats", "effect": "+3,000 pursuit casualties"}


def _with(name, ability):
    """Stage: `name` takes an ability — a dict, or the one another man of the
    1805 roster holds (his name)."""
    def tune(world, executor):
        world.marshals[name].ability = copy.deepcopy(
            world.marshals[ability].ability if isinstance(ability, str) else ability)
    return tune


class TestAPursuitIsAnyCorpsThatFought:
    """§15.5.7, the user's tick, and his answer to BA-3's second question —
    "any corps of the victor that FOUGHT on the field". Ney leads on Mack and
    has no pursuit of his own; Murat, the First Horseman of Europe, marches to
    his guns. MC-1 had pinned "a reinforcing Murat earns nothing; he must LEAD
    the killing blow": the rout was Ney's and the horse stood by."""

    def test_the_table_of_abilities(self):
        world, _executor = STAGE._board()
        assert combat_executor.pursuit_bonus(world.marshals["Murat"]) == 5000
        assert combat_executor.pursuit_bonus(world.marshals["Ney"]) == 0
        _with("Davout", VORWAERTS)(world, None)
        assert combat_executor.pursuit_bonus(world.marshals["Davout"]) == 3000
        murat = world.marshals["Murat"]
        murat.cavalry = False
        assert combat_executor.pursuit_bonus(murat) == 0, "the horseman's pursuit is his horse's"

    def test_murat_rides_them_down_though_ney_leads(self):
        _seed, _world, reply = _a_rout()
        [beat] = _beats_of(reply, "pursue")
        assert beat["damage"] == 5000 and beat["target"] == "Mack"
        assert "Murat's 'First Horseman of Europe'" in reply["message"]
        assert "(+5,000 pursuit casualties)" in reply["message"]

    def test_the_seam_down_is_mc1_he_must_lead_the_killing_blow(self, monkeypatch):
        seed, world, _reply = _a_rout()
        _down(monkeypatch, combat_executor, "a_pursuit_is_any_corps_that_fought")
        before, old, _seen = _fight(seed)
        assert not _beats_of(old, "pursue") and "pursuit casualties" not in old["message"]
        assert int(before.marshals["Mack"].strength) > int(world.marshals["Mack"].strength), \
            "the same dice, and the pursuit's men still under Mack's colours"

    def test_the_leads_own_pursuit_comes_first(self):
        """A lead who pursues by his own ability pursues, as he always did:
        one pursuit, his — a better horseman beside him adds nothing to it."""
        _seed, _world, reply = _a_rout(_with("Ney", VORWAERTS))
        [beat] = _beats_of(reply, "pursue")
        assert beat["damage"] == 3000 and beat["actor"] == "Ney"
        assert "Ney's 'Vorwärts!'" in reply["message"] and "Murat's" not in reply["message"]

    def test_the_highest_only(self):
        """Two corps that fought pursue by ability: ONE pursuit, the higher
        (every corps brought up — `arrival={}` — so that both fight)."""
        _seed, _world, reply = _a_rout(_with("Davout", VORWAERTS), arrival={})
        [beat] = _beats_of(reply, "pursue")
        assert beat["damage"] == 5000
        assert "Murat's 'First Horseman of Europe'" in reply["message"]
        assert "Davout's 'Vorwärts!'" not in reply["message"]

    def test_the_old_fox_still_halves_it(self):
        _seed, _world, reply = _a_rout(_with("Mack", "Kutuzov"))
        [beat] = _beats_of(reply, "pursue")
        assert beat["damage"] == 2500 and beat["halved"] is True
        assert "The Old Fox halves the harvest." in reply["message"]

    def test_he_must_have_fought(self, monkeypatch):
        """The pursuer is a corps that brought something to the fighting: a
        man who withheld everything, or whose corps is spent, pursues nothing."""
        world, executor = STAGE._board()
        combat = executor._combat
        ney, murat, davout = (world.marshals[name] for name in ("Ney", "Murat", "Davout"))
        ctx = types.SimpleNamespace(marshal=ney, atk_participants=[ney, davout, murat])
        assert combat._pursuer(ctx) == (murat, 5000)
        murat.strength = 0
        assert combat._pursuer(ctx) == (ney, 0)
        murat.strength = 22000
        cls = combat_executor.CombatExecutor
        real = cls._pair_contribution_scale
        monkeypatch.setattr(cls, "_pair_contribution_scale", lambda self, lead, ally: (
            0.0 if ally.name == "Murat" else real(self, lead, ally)))
        assert combat._pursuer(ctx) == (ney, 0)

    # ── the telling ──────────────────────────────────────────────────────

    @staticmethod
    def _told(shown, player_side):
        world, _executor = STAGE._board()
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        script = battle_script._Script(shown, world, ("Ney", "Mack", "Swabia", 1))
        battle_script._pursuit(
            script, world, {"region": "Swabia"}, ney, mack,
            {"pursuit_damage": 5000, "pursuer": "Murat",
             "pursuer_ability": "First Horseman of Europe"},
            {}, {}, "France", player_side)
        [beat] = script.acts["pursuit"]
        return beat

    def test_a_corps_the_table_seats_makes_the_move_itself(self):
        beat = self._told({"Ney", "Mack", "Murat"}, "attacker")
        assert beat["actor"] == "Murat"
        assert beat["text"] == "Murat rides them down (First Horseman of Europe): 5,000 more."

    def test_a_corps_of_ones_own_reserve_is_named(self):
        """The table seats three corps a side: a pursuer behind the line has
        no plinth to move, so the lead's plinth makes the move — and the
        player is told which of HIS corps it was."""
        beat = self._told({"Ney", "Mack"}, "attacker")
        assert beat["actor"] == "Ney"
        assert beat["text"] == ("Murat, from the reserve, rides them down "
                                "(First Horseman of Europe): 5,000 more.")

    @pytest.mark.parametrize("side", ["defender", None])
    def test_an_unseated_corps_of_another_crown_is_not_named(self, side):
        """Not his name, and not the ability only he holds."""
        beat = self._told({"Ney", "Mack"}, side)
        assert beat["actor"] == "Ney"
        assert beat["text"] == "Ney's reserve rides them down: 5,000 more."
        assert "Murat" not in beat["text"] and "Horseman" not in beat["text"]

    def test_on_the_board_the_reserves_pursuit_is_told_to_its_emperor(self):
        """The whole road: six French corps round Swabia, three seats."""
        _seed, _world, reply = _a_rout()
        [beat] = _beats_of(reply, "pursue")
        seats = [c["name"] for c in reply["battle_diorama"]["attacker"]["contingents"]]
        if "Murat" in seats and beat["actor"] == "Murat":
            assert beat["text"].startswith("Murat rides them down")
        else:
            assert beat["actor"] == "Ney"
            assert beat["text"].startswith("Murat, from the reserve, rides them down")


def _lone_murat(world, executor):
    """Ney and Murat alone before a shaken Mack: two French corps, both seated."""
    STAGE._place(world, Davout="Paris", Lannes="Paris", Napoleon="Paris", Soult="Paris",
                 Bernadotte="Paris", Massena="Paris")
    mack = world.marshals["Mack"]
    mack.strength, mack.morale = 30000, 25


class TestThePursuitOnASmallField:
    def test_a_seated_murat_pursues_in_his_own_name(self):
        _seed, _world, reply = _a_rout(_lone_murat)
        [beat] = _beats_of(reply, "pursue")
        assert beat["actor"] == "Murat"
        assert beat["text"] == "Murat rides them down (First Horseman of Europe): 5,000 more."


class TestTheLastHourBringsThreeQuarters:
    """§15.5.7, the user's tick: an arrival won by five points or fewer —
    the roll the table has told since BA-1 as "comes up at the last hour" —
    brings three quarters of its weight, on either side, through the one
    function that halves a faithless man's."""

    def test_the_rules_two_numbers(self):
        assert battle_script.LAST_HOUR_MARGIN == 5
        assert combat_executor.CombatExecutor.LAST_HOUR_CONTRIBUTION == 0.75

    def test_which_rolls_are_the_last_hour(self, monkeypatch):
        rows = [{"marshal": "One", "arrived": True, "score": 61, "threshold": 60},
                {"marshal": "Five", "arrived": True, "score": 65, "threshold": 60},
                {"marshal": "Six", "arrived": True, "score": 66, "threshold": 60},
                {"marshal": "Short", "arrived": False, "score": 60, "threshold": 60},
                {"marshal": "Fumbled", "arrived": False, "score": 83, "threshold": 80}]
        assert combat_executor.last_hour_names(rows) == frozenset({"One", "Five"})
        _down(monkeypatch, combat_executor, "the_last_hour_brings_three_quarters")
        assert combat_executor.last_hour_names(rows) == frozenset()

    def test_it_is_the_one_function_that_halves_a_faithless_man(self):
        world, executor = STAGE._board()
        ney, davout = world.marshals["Ney"], world.marshals["Davout"]
        whole = combat_executor.pair_contribution_breakdown(ney, davout, owner=executor._combat)
        late = combat_executor.pair_contribution_breakdown(
            ney, davout, owner=executor._combat, last_hour=True)
        assert "last_hour_factor" not in whole
        assert late["last_hour_factor"] == 0.75
        assert late["scale"] == whole["scale"] * 0.75 > 0
        assert executor._combat._weight_scale(ney, davout, ("Davout",)) == late["scale"]
        assert executor._combat._weight_scale(ney, davout, ("Murat",)) == whole["scale"]
        assert executor._combat._weight_scale(ney, davout) == whole["scale"]

    def test_davout_by_three_points_brings_three_quarters(self):
        """Davout's roll fixed at three points over his bar, then at six: the
        same corps arrive on the same dice, and only the hour differs."""
        world, late_reply, late = _fight(3, arrival={"Davout": 3})
        _world, _reply, timely = _fight(3, arrival={"Davout": 6})
        assert late["attacker"] < timely["attacker"]
        # the men engaged are the quantity half of the same term: six tenths
        # of his corps at his scale, and a quarter of that left behind
        davout = STAGE._board()[0].marshals["Davout"]
        quarter = 0.25 * combat_executor.CombatExecutor.COMMITTED_ALPHA * davout.strength
        assert timely["attacker_bodies"] - late["attacker_bodies"] == pytest.approx(quarter, abs=1)
        [beat] = [b for b in _beats_of(late_reply, "arrive") if b["actor"] == "Davout"]
        assert beat["late"] is True and beat["margin"] == 3
        assert beat["text"].endswith(" He brings three-quarters of his weight.")
        [timely_beat] = [b for b in _beats_of(_reply, "arrive") if b["actor"] == "Davout"]
        assert timely_beat["late"] is False and "three-quarters" not in timely_beat["text"]

    def test_the_seam_down_is_all_his_weight_at_any_hour(self, monkeypatch):
        _world, _reply, up_timely = _fight(3, arrival={"Davout": 6})
        _down(monkeypatch, combat_executor, "the_last_hour_brings_three_quarters")
        _world, reply, down_late = _fight(3, arrival={"Davout": 3})
        assert down_late["attacker"] == up_timely["attacker"]
        assert down_late["attacker_bodies"] == up_timely["attacker_bodies"]
        [beat] = [b for b in _beats_of(reply, "arrive") if b["actor"] == "Davout"]
        assert beat["late"] is True, "the table still tells the hour"
        assert "three-quarters" not in beat["text"], "and says nothing of a weight it did not cut"

    def test_the_defenders_side_is_weighed_the_same_way(self):
        """Davout on Kutuzov in the Tyrol; Buxhowden, ordered to support him,
        comes up from Bohemia — by three points, then by six."""
        def stage(world, executor):
            STAGE._stage_enemy_comes(world, executor)

        seed = 1
        _w, late_reply, late = _fight(seed, "Davout", "Kutuzov", tune=stage,
                                      arrival={"Buxhowden": 3})
        _w, _r, timely = _fight(seed, "Davout", "Kutuzov", tune=stage,
                                arrival={"Buxhowden": 6})
        assert late["defender"] < timely["defender"]
        assert late["defender_bodies"] < timely["defender_bodies"]
        assert late["attacker"] == timely["attacker"]
        [beat] = [b for b in _beats_of(late_reply, "arrive") if b["actor"] == "Buxhowden"]
        # the other side's corps is seen to come late — never by how much —
        # and what the hour cost him is the game's rule, told to a party
        assert beat["late"] is True and "margin" not in beat and "score" not in beat
        assert beat["text"] == ("Buxhowden comes up at the last hour. "
                                "He brings three-quarters of his weight.")

    def test_only_a_weight_that_was_cut_is_told(self, monkeypatch):
        world, executor = STAGE._board()
        combat = executor._combat
        ney, mack, murat, davout = (world.marshals[n] for n in ("Ney", "Mack", "Murat", "Davout"))
        ctx = types.SimpleNamespace(marshal=ney, enemy_marshal=mack,
                                    atk_participants=[ney, davout, murat],
                                    def_participants=[mack])
        late = frozenset({"Davout", "Murat"})
        assert combat._cut_by_the_last_hour(ctx, late, frozenset()) == ["Davout", "Murat"]
        assert combat._cut_by_the_last_hour(ctx, frozenset(), frozenset()) == []
        cls = combat_executor.CombatExecutor
        real = cls._pair_contribution_scale
        monkeypatch.setattr(cls, "_pair_contribution_scale", lambda self, lead, ally: (
            0.0 if ally.name == "Murat" else real(self, lead, ally)))
        assert combat._cut_by_the_last_hour(ctx, late, frozenset()) == ["Davout"], \
            "a man who withholds everything brings three quarters of nothing"


def _every_roll(combat, world, lead, joiners, region, stamp, *, marchers_only=False):
    """The resolver's arithmetic over EVERY roll the joiners can make —
    [(probability, committed strength)], worked from the rule itself: a corps
    on the field makes no roll; a marching corps arrives where its score
    passes its bar, fumbles five times in a hundred over 80, and is at the
    last hour where the roll is won by five points or fewer. Each state's
    team is stamped (`stamp(team)`) and summed by the resolver's own summer
    with the late corps named."""
    variance = combat._ARRIVAL_VARIANCE
    rolls = 2 * variance + 1
    here = [m for m in joiners if m.location == region]
    states = [((), (), 1.0)]
    for m in joiners:
        if m.location == region:
            continue
        base = combat._arrival_deterministic(m, lead, world)
        bar = combat._arrival_threshold(m, lead, region, world)
        absent = late = timely = 0.0
        for jitter in range(-variance, variance + 1):
            score = base + jitter
            if score <= bar:
                absent += 1.0
                continue
            fumble = 0.05 if score > 80 else 0.0
            absent += fumble
            if score - bar <= 5:
                late += 1.0 - fumble
            else:
                timely += 1.0 - fumble
        states = [(team + add, lates + mark, p * weight / rolls)
                  for team, lates, p in states
                  for add, mark, weight in (((), (), absent),
                                            ((m.name,), (m.name,), late),
                                            ((m.name,), (), timely))
                  if weight > 0.0]
    days = []
    for team, lates, p in states:
        squad = here + [world.marshals[name] for name in team]
        with stamp(squad):
            counted = [m for m in squad if m.location != region] if marchers_only else squad
            days.append((p, combat._committed_reinforcement_strength(
                lead, counted, world, late=lates)))
    return days


def _ulm_muster():
    """Ney on Mack as the campaign opens: the screen, and its own terms."""
    world, executor = STAGE._board()
    combat = executor._combat
    ney, mack = world.marshals["Ney"], world.marshals["Mack"]
    with STAGE._quiet():
        preview = combat._build_muster_preview(ney, mack, world, {"world": world})
    region = mack.location
    joining = [world.marshals[row["marshal"]] for row in preview["rows"]
               if row["will_join"] and not row.get("cannot_arrive")]
    enemy_joining, _ = combat._defender_muster(mack, world, term=False)
    enemy_team = combat._reachable_joiners(mack, enemy_joining, world, region, active=True)

    def stamp(squad):
        return combat._priced_coordination(ney, squad, mack, enemy_team, world, region)

    with STAGE._quiet():
        outcome_set = combat._muster_outcome_set(ney, joining, mack, enemy_joining, world, region)
    return types.SimpleNamespace(
        world=world, combat=combat, ney=ney, mack=mack, preview=preview, region=region,
        joining=joining, enemy_joining=enemy_joining, stamp=stamp, outcome_set=outcome_set)


class TestTheForecastCountsTheLastHour:
    """"…the muster's forecast counting it the same way." The chance a corps
    ARRIVES is what it was; what his arrival is WORTH is now two figures. The
    row prints the chance; the mean, the least and the bad day are the
    resolver's arithmetic over every roll; a court's price is the same sum."""

    def test_the_row_keeps_his_chance_and_carries_the_last_hours_share(self):
        ulm = _ulm_muster()
        rows = {row["marshal"]: row for row in ulm.preview["rows"]}
        murat = ulm.world.marshals["Murat"]
        chance = ulm.combat._arrival_chance(ulm.ney, murat, ulm.world, ulm.region)
        late = ulm.combat._last_hour_chance(ulm.ney, murat, ulm.world, ulm.region)
        assert 0.0 < late < 1.0, "on this board Murat may come up at the last hour"
        assert rows["Murat"]["arrival_odds"] == int(round(chance * 100))
        assert rows["Murat"]["last_hour_odds"] == int(round(chance * late * 100))
        assert f"(about {rows['Murat']['arrival_odds']}%)" in rows["Murat"]["arrival_note"]
        weight = ulm.combat._expected_arrival_weight(ulm.ney, murat, ulm.world, ulm.region)
        assert weight == pytest.approx(chance * (1.0 - 0.25 * late)) and weight < chance

    def test_the_muster_says_the_rule_once_under_its_rows(self):
        ulm = _ulm_muster()
        lines = ulm.combat._format_muster_lines(ulm.preview).split("\n")
        said = [i for i, line in enumerate(lines)
                if line.strip() == combat_executor.LAST_HOUR_MUSTER_LINE]
        assert len(said) == 1
        rows = [i for i, line in enumerate(lines)
                if line.startswith(("  WILL JOIN", "  WILL NOT", "  CANNOT ARRIVE"))]
        assert said[0] == rows[-1] + 1, "on the line under the last row"
        assert combat_executor.LAST_HOUR_MUSTER_LINE == (
            "At the last hour a corps brings three-quarters of its weight — "
            "counted in the figures above.")

    def test_a_muster_nobody_can_be_late_in_does_not_say_it(self):
        ulm = _ulm_muster()
        for row in ulm.preview["rows"]:
            row.pop("last_hour_odds", None)
        assert combat_executor.LAST_HOUR_MUSTER_LINE not in ulm.combat._format_muster_lines(ulm.preview)

    def test_the_screen_is_the_walk_over_every_roll(self):
        ulm = _ulm_muster()
        days = _every_roll(ulm.combat, ulm.world, ulm.ney, ulm.joining, ulm.region, ulm.stamp)
        assert sum(p for p, _v in days) == pytest.approx(1.0)
        mean = sum(p * v for p, v in days)
        floor, bad_day = ulm.combat._outcome_spread(days, combat_executor.MUSTER_BAD_DAY_CHANCE)
        assert "hours" in ulm.outcome_set, "the set holds a corps that may come late"
        assert ulm.combat._muster_mean_exact(ulm.outcome_set) == pytest.approx(mean, rel=1e-12)
        lead = int(ulm.ney.strength)
        mine = ulm.preview["attacker"]
        assert mine["committed_strength"] == pytest.approx(lead + mean, abs=1)
        assert mine["floor_strength"] == pytest.approx(lead + floor, abs=1)
        assert mine["bad_day_strength"] == pytest.approx(lead + bad_day, abs=1)

    def test_the_set_still_rolls_the_chance_he_arrives(self):
        """The outcome sets' coin is the arrival CHANCE (the defect of the
        session's first cut: it read the WEIGHT there, which made a corps
        sure to arrive an uncertain one and dropped him from the least)."""
        ulm = _ulm_muster()
        certain, uncertain = ulm.combat._arrival_roster(ulm.ney, ulm.joining, ulm.world, ulm.region)
        for chance, m in uncertain:
            assert chance == ulm.combat._arrival_chance(ulm.ney, m, ulm.world, ulm.region)
        for m in certain:
            assert ulm.combat._arrival_chance(ulm.ney, m, ulm.world, ulm.region) >= 1.0
        assert sum(p for p, _v in ulm.outcome_set["outcomes"]) == pytest.approx(1.0)

    def test_a_corps_sure_to_come_is_counted_in_the_least_at_three_quarters(self, monkeypatch):
        """Davout at 69 against a bar of 60: every roll brings him (61 to
        77), five of the seventeen at the last hour. He is in every outcome —
        and the least the muster promises takes him at his last-hour weight."""
        cls = combat_executor.CombatExecutor
        real_base, real_bar = cls._arrival_deterministic, cls._arrival_threshold
        monkeypatch.setattr(cls, "_arrival_deterministic", lambda self, m, lead, world: (
            69 if m.name == "Davout" else real_base(self, m, lead, world)))
        monkeypatch.setattr(cls, "_arrival_threshold", lambda self, m, lead, region, world, **kw: (
            60 if m.name == "Davout" else real_bar(self, m, lead, region, world, **kw)))
        ulm = _ulm_muster()
        davout = ulm.world.marshals["Davout"]
        assert ulm.combat._arrival_chance(ulm.ney, davout, ulm.world, ulm.region) == 1.0
        assert ulm.combat._last_hour_chance(ulm.ney, davout, ulm.world, ulm.region) == pytest.approx(5 / 17)
        certain, _uncertain = ulm.combat._arrival_roster(ulm.ney, ulm.joining, ulm.world, ulm.region)
        assert davout in certain
        row = next(r for r in ulm.preview["rows"] if r["marshal"] == "Davout")
        assert (row["arrival_odds"], row["last_hour_odds"]) == (100, 29)
        days = _every_roll(ulm.combat, ulm.world, ulm.ney, ulm.joining, ulm.region, ulm.stamp)
        floor, bad_day = ulm.combat._outcome_spread(days, combat_executor.MUSTER_BAD_DAY_CHANCE)
        lead = int(ulm.ney.strength)
        assert ulm.preview["attacker"]["floor_strength"] == pytest.approx(lead + floor, abs=1)
        assert ulm.preview["attacker"]["bad_day_strength"] == pytest.approx(lead + bad_day, abs=1)
        with ulm.stamp([davout]):
            whole = ulm.combat._committed_reinforcement_strength(ulm.ney, [davout], ulm.world)
            at_the_hour = ulm.combat._committed_reinforcement_strength(
                ulm.ney, [davout], ulm.world, late=("Davout",))
        assert at_the_hour == pytest.approx(0.75 * whole)
        assert lead < ulm.preview["attacker"]["floor_strength"] < lead + whole, \
            "he is counted, and not at all his weight"

    def test_the_band_reads_the_same_ratio_from_the_days_as_from_their_means(self):
        """The set keeps one figure an outcome — the mean over its hours —
        and the band's ratio is linear in each corps' term, so it loses
        nothing: opened into every day, the ratio is the same."""
        ulm = _ulm_muster()
        opened = {"outcomes": [], "lead_mods": [], "withheld": False}
        for (p, v), mod, hour in zip(ulm.outcome_set["outcomes"], ulm.outcome_set["lead_mods"],
                                     ulm.outcome_set["hours"]):
            for state in ulm.combat._hour_states(p, v, hour):
                opened["outcomes"].append(state)
                opened["lead_mods"].append(mod)
        assert len(opened["outcomes"]) > len(ulm.outcome_set["outcomes"])
        game_state = {"world": ulm.world}
        with ulm.stamp(ulm.joining):
            by_means = ulm.combat._muster_ratio_exact(
                ulm.ney, ulm.mack, game_state, 0.0, 0.0, ulm.outcome_set, None)
            by_days = ulm.combat._muster_ratio_exact(
                ulm.ney, ulm.mack, game_state, 0.0, 0.0, opened, None)
        assert by_means == pytest.approx(by_days, rel=1e-12)

    def test_the_one_stamp_mean_weighs_him_the_same_way(self):
        ulm = _ulm_muster()
        with ulm.stamp(ulm.joining):
            one_stamp = ulm.combat._committed_reinforcement_strength(
                ulm.ney, ulm.joining, ulm.world, expected_at=ulm.region)
            by_hand = sum(
                ulm.combat._expected_arrival_weight(ulm.ney, m, ulm.world, ulm.region)
                * ulm.combat._committed_share(ulm.ney, m, ulm.combat._pair_contribution_scale(ulm.ney, m))
                for m in ulm.joining)
        assert one_stamp == pytest.approx(by_hand, rel=1e-12)

    def test_a_court_prices_a_defender_by_the_same_walk(self, monkeypatch):
        """Austria pricing Soult at Lorraine on the shipped board (S14E-X76's
        own sighting): the corps that would march to him, each by its roll."""
        world, executor = STAGE._board()
        world.calculate_visibility()
        combat = executor._combat
        soult = world.marshals["Soult"]
        ai = enemy_ai.EnemyAI(executor)
        with STAGE._quiet():
            price = ai._muster_price(soult, "Austria", world)
            joining, _ = combat._defender_muster(soult, world, term=False)
        days = _every_roll(
            combat, world, soult, joining, soult.location,
            lambda squad: combat._priced_coordination(soult, squad, None, None, world, soult.location),
            marchers_only=True)
        assert price == pytest.approx(sum(p * v for p, v in days), abs=1)
        _down(monkeypatch, combat_executor, "the_last_hour_brings_three_quarters")
        with STAGE._quiet():
            before = ai._muster_price(soult, "Austria", world)
        assert price < before, "a corps of his may come at the last hour, and the price counts it"

    def test_the_seam_down_is_the_forecast_before(self, monkeypatch):
        _down(monkeypatch, combat_executor, "the_last_hour_brings_three_quarters")
        ulm = _ulm_muster()
        assert "hours" not in ulm.outcome_set
        assert not any("last_hour_odds" in row for row in ulm.preview["rows"])
        assert combat_executor.LAST_HOUR_MUSTER_LINE not in ulm.combat._format_muster_lines(ulm.preview)
        for m in ulm.joining:
            assert (ulm.combat._expected_arrival_weight(ulm.ney, m, ulm.world, ulm.region)
                    == ulm.combat._arrival_chance(ulm.ney, m, ulm.world, ulm.region))
            assert ulm.combat._last_hour_chance(ulm.ney, m, ulm.world, ulm.region) == 0.0
        # and an outcome's figure is the summer's own, to the bit
        team = list(ulm.joining)
        with ulm.stamp(team):
            assert ulm.combat._outcome_committed(ulm.ney, team, ulm.world, {}) == (
                ulm.combat._committed_reinforcement_strength(ulm.ney, team, ulm.world), None)


# ════════════════════════════════════════════════════════════════════════
# The day's rows: BA3-X13, X14, X15, X16; one name for a day; its close told;
# the first day names its own rules
# ════════════════════════════════════════════════════════════════════════

def _muster_answered(table, body, choice="attack_anyway"):
    """Where an order raised the muster's "Commit the Attack?", answer it."""
    for marshal in table.world.get_player_marshals():
        asking = getattr(marshal, "pending_interrupt", None)
        if asking and asking.get("interrupt_type") == "muster_confirm":
            return _quiet(table.tc.post, "/strategic_response", json={
                "marshal_name": asking["marshal"], "response_type": asking["interrupt_type"],
                "choice": choice}).json()
    return body


def _battle_names(world):
    return [str(e.get("battle_name") or "") for e in world.event_log if e.get("type") == "battle"]


def _acts_beats(payload, kind):
    return [beat for act in ((payload or {}).get("script") or {}).get("acts", [])
            for beat in act["beats"] if beat["kind"] == kind]


class TestADeadDayBarsNothing:
    """BA3-X13. Night bars a pair from a second strike in the phase that
    follows. It barred the pair of EVERY day open at nightfall — also one
    already over because its lead had marched off the field: walking away
    bought a phase in which that corps could not be struck. (The row's own
    pin is `tests/test_ba3_the_review.py`, a plain test since this session.)"""

    @staticmethod
    def _night(dead: bool):
        world, ney, mack = _served()
        world.battle_days = {"days": {"Mack": _a_day(ney, mack)}}
        if dead:
            ney.location = next(n for n in world.get_region(ney.location).adjacent_regions
                                if n != mack.location)
        assert BD._alive(world, world.battle_days["days"]["Mack"]) is (not dead)
        _quiet(BD.night_falls, world, {"world": world}, CommandExecutor())
        assert not BD.open_days(world), "night closes every day"
        return world

    def test_a_day_dead_at_nightfall_bars_no_strike(self):
        world = self._night(dead=True)
        assert BD.bars(world) == set()
        assert world.battle_days == {}, "and leaves no trace on the save"

    def test_a_day_alive_at_nightfall_still_bars_its_pair(self):
        assert BD.bars(self._night(dead=False)) == {("Mack", "Ney")}

    def test_the_seam_down_bars_the_dead_days_pair(self, monkeypatch):
        _down(monkeypatch, BD, "a_dead_day_bars_nothing")
        assert BD.bars(self._night(dead=True)) == {("Mack", "Ney")}


class TestHisWordIsScoredFromTheDay:
    """BA3-X14. His AI scores every order it runs with a draw from his
    court's stream of the PHASE. A word he gave in our turn, or at nightfall,
    drew from the stream the phase was about to draw from — so what the
    player did with a day moved his court's dice afterwards."""

    def test_a_stream_of_its_own_answers_for_the_court_while_it_runs(self):
        world, _ney, _mack = _served()
        phase = enemy_ai.ai_rng(world, "Austria")
        before = phase.getstate()
        with enemy_ai.a_stream_of_its_own(world, "Austria", "day", "Mack", "Ney", 2, 0):
            own = enemy_ai.ai_rng(world, "Austria")
            assert own is not phase
            first = own.randint(-10, 10)
        assert enemy_ai.ai_rng(world, "Austria") is phase and phase.getstate() == before
        with enemy_ai.a_stream_of_its_own(world, "Austria", "day", "Mack", "Ney", 2, 0):
            assert enemy_ai.ai_rng(world, "Austria").randint(-10, 10) == first, \
                "the same day at the same word draws the same — a save and a load too"
        with enemy_ai.a_stream_of_its_own(world, "Austria", "day", "Mack", "Ney", 3, 0):
            other = [enemy_ai.ai_rng(world, "Austria").randint(-10, 10) for _ in range(8)]
        with enemy_ai.a_stream_of_its_own(world, "Austria", "day", "Mack", "Ney", 2, 0):
            same = [enemy_ai.ai_rng(world, "Austria").randint(-10, 10) for _ in range(8)]
        assert other != same, "another word of the day draws apart"

    def test_the_seam_down_draws_from_the_phases_stream(self, table, monkeypatch):
        """The twin of the row's pin (`test_ba3_the_review`): the same board,
        the seam down, and his court's stream has moved."""
        _down(monkeypatch, BD, "his_word_is_scored_from_the_day")
        table.open_a_day(_awaits_us)
        world = table.world
        stream = enemy_ai.ai_rng(world, "Austria")
        before = stream.getstate()
        body = table.word("stand")
        said = (body.get("battle_day") or {}).get("told") or []
        if not any(t["who"] == "theirs" and t["kind"] not in ("stand", "") for t in said[-2:]):
            raise RuntimeError(f"he gave no word that runs an order on this board: {said}")
        assert enemy_ai.ai_rng(world, "Austria") is stream and stream.getstate() != before


def _two_hanging_battles_on_ney(world, ney):
    """Mack, then Kienmayer beside him, each fights Ney to a hanging great
    battle on Ney's own ground (the row's own staging)."""
    beside = next(n for n in world.get_region(ney.location).adjacent_regions
                  if n != world.marshals["Mack"].location)
    world.marshals["Kienmayer"] = _mk("Kienmayer", beside, 60000, nation="Austria",
                                      personality="literal")
    blocks = []
    for foe in ("Mack", "Kienmayer"):
        blocks.append(BD.after_the_battle(types.SimpleNamespace(
            world=world, marshal=world.marshals[foe], enemy_marshal=ney,
            battle_result={"outcome": "stalemate", "attacker": {"casualties": 3000},
                           "defender": {"casualties": 2000}},
            total_engaged_strength=120000, battle_region_name=ney.location,
            target_location=ney.location, battle_name="The Great Battle of " + ney.location,
            conquered=False, enemy_destroyed=False)))
    return blocks


class TestALeadHoldsOneDay:
    """BA3-X15, ruled by the user at the plan gate: "One day a lead". Two
    corps of his could each fight one lead of ours to a hanging great battle,
    and each opened a day: two purses, two enemies answering in turn, one
    lead whose `digs in` is one order."""

    def test_the_second_battle_opens_no_day(self):
        world, ney, _mack = _served()
        first, second = _two_hanging_battles_on_ney(world, ney)
        assert first is not None and first["open"] is True
        assert second is None, "told as a battle is told: the tableau carries no day"
        assert list(BD.open_days(world)) == ["Mack"]

    def test_its_script_says_why(self):
        world, ney, _mack = _served()
        _two_hanging_battles_on_ney(world, ney)
        ctx = types.SimpleNamespace(world=world, marshal=world.marshals["Kienmayer"],
                                    enemy_marshal=ney)
        said = BD.word_line(ctx)
        assert said == {"who": "", "kind": "alone",
                        "line": "Ney's day against Mack is still open — this clash opens none of its own."}
        assert BD.word_line(ctx) is None, "said once, by the battle that left it"

    def test_another_battles_script_does_not_take_the_line(self):
        world, ney, mack = _served()
        _two_hanging_battles_on_ney(world, ney)
        assert BD.word_line(types.SimpleNamespace(world=world, marshal=mack, enemy_marshal=ney)) is None

    def test_a_dead_day_does_not_hold_its_lead(self):
        """A day already over (its enemy gone from the field) is no day: the
        lead's next hanging great battle opens one."""
        world, ney, mack = _served()
        world.battle_days = {"days": {"Mack": _a_day(ney, mack, side="defence")}}
        field = mack.location
        mack.location = next(n for n in world.get_region(field).adjacent_regions
                             if n != ney.location)
        assert not BD._alive(world, world.battle_days["days"]["Mack"])
        world.marshals["Kienmayer"] = _mk("Kienmayer", field, 60000, nation="Austria")
        block = BD.after_the_battle(types.SimpleNamespace(
            world=world, marshal=world.marshals["Kienmayer"], enemy_marshal=ney,
            battle_result={"outcome": "stalemate", "attacker": {}, "defender": {}},
            total_engaged_strength=120000, battle_region_name=ney.location,
            conquered=False, enemy_destroyed=False))
        assert block is not None and "Kienmayer" in BD.open_days(world)

    def test_the_seam_down_is_two_days_on_one_lead(self, monkeypatch):
        _down(monkeypatch, BD, "a_lead_holds_one_day")
        world, ney, _mack = _served()
        _first, second = _two_hanging_battles_on_ney(world, ney)
        assert second is not None
        assert [day["lead"] for day in BD.open_days(world).values()] == ["Ney", "Ney"]

    def test_through_the_server_the_second_battle_is_one_clash(self, table):
        """Ney's day against Mack is open; a second corps of his stands on the
        day's own field, and Ney fights it to a hanging great battle."""
        table.open_a_day(_awaits_us)
        world = table.world
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        world.marshals["Kienmayer"] = _mk("Kienmayer", mack.location, 70000, nation="Austria",
                                          personality="literal")
        for _ in range(40):
            world = table.world
            ney, kienmayer = world.marshals["Ney"], world.marshals["Kienmayer"]
            if "Mack" not in BD.open_days(world):
                raise RuntimeError("the first day closed before the second battle hung")
            ney.strength, ney.morale = 70000, 80
            kienmayer.strength, kienmayer.morale = 70000, 80
            for corps in (ney, kienmayer):
                corps.broken = corps.retreating = False
            world.actions_remaining = 4
            body = _muster_answered(table, table.order("Ney, attack Kienmayer"))
            payload = body.get("battle_diorama") or {}
            if payload.get("great_battle") and payload.get("outcome") in BD.HANGING:
                break
        else:
            raise RuntimeError("no hanging great second battle on forty dice")
        assert list(BD.open_days(table.world)) == ["Mack"]
        assert "day" not in payload
        [line] = _acts_beats(payload, "word")
        assert line["text"] == "Ney's day against Mack is still open — this clash opens none of its own."


class TestADayIsOneBattle:
    """The user's tick at the plan gate — "One name for a day". Every clash of
    a day took the province's next ordinal: one afternoon at Swabia was "The
    Great Battle", "The Great Second Battle" and "The Great Third Battle" of
    Swabia."""

    def test_the_ordinal_leaves_a_days_later_clashes_out(self):
        world = WorldState()
        assert world.compose_battle_name("Swabia", 90000) == "The Great Battle of Swabia"
        # two later clashes of that day: the count advances, and they are counted beside it
        for _ in range(2):
            world.compose_battle_name("Swabia", 90000)
            key = BD.later_clashes_key(world, "Swabia")
            world.battle_counts[key] = world.battle_counts.get(key, 0) + 1
        assert world.battle_counts["Swabia"] == 3, "the dice and the voices still read every clash"
        assert world.compose_battle_name("Swabia", 30000) == "Second Battle of Swabia"
        assert world.compose_battle_name("Swabia", 90000) == "The Great Third Battle of Swabia"

    def test_no_province_is_named_as_the_key_is(self):
        world, _executor = STAGE._board()
        assert WorldState.DAY_CLASHES_SUFFIX == " (later clashes of a day)"
        assert not any(name.endswith(WorldState.DAY_CLASHES_SUFFIX) for name in world.regions)

    def test_a_province_first_fought_on_as_a_days_clash_starts_its_own_series(self):
        """He strikes back on OUR ground: that province's first battle is a
        clash of the day fought next door — its own first battle is still
        "the Battle of" it."""
        world = WorldState()
        world.compose_battle_name("Rhineland", 90000)
        world.battle_counts[BD.later_clashes_key(world, "Rhineland")] = 1
        assert world.compose_battle_name("Rhineland", 30000) == "Battle of Rhineland"

    def test_a_days_clashes_keep_its_name(self, table):
        body, day = table.open_a_day(_awaits_us)
        world = table.world
        name = world.battle_days["days"]["Mack"]["name"]
        assert name.endswith("Battle of Lorraine") and " — the " not in name
        fought = int(world.battle_days["days"]["Mack"]["clashes"])
        press = _chip(day, "press")
        body = _muster_answered(table, table.order(press["command"]))
        assert body["success"], body.get("message")
        names = _battle_names(table.world)
        opened = names.index(name)
        assert f"{name} — the {BD._ordinal(fought + 1)} clash" in names[opened:]
        assert all(n.startswith(name + " — the ") for n in names[opened + 1:]), names[opened:]
        assert body["battle_diorama"]["battle_name"] == name, "the table's plate keeps the day's name"
        assert names.count(name) == 1, "one battle of that name"

    def test_the_next_battle_there_takes_the_next_ordinal(self, table):
        body, day = table.open_a_day(_awaits_us)
        _muster_answered(table, table.order(_chip(day, "press")["command"]))
        world = table.world
        field = "Lorraine"
        later = int(world.battle_counts.get(BD.later_clashes_key(world, field), 0))
        fought = int(world.battle_counts[field])
        assert later >= 1, "our press was a later clash of the day, counted beside the province's own"
        world.battle_days = {}                       # the day is over; a new battle, days later
        nth = fought - later + 1                     # (the fixture may fight several openings)
        ordinal = WorldState._BATTLE_ORDINALS.get(nth, f"{nth}th")
        assert world.compose_battle_name(field, 30000) == f"{ordinal} Battle of {field}"

    def test_the_seam_down_is_a_battle_a_clash(self, table, monkeypatch):
        _down(monkeypatch, BD, "a_day_is_one_battle")
        body, day = table.open_a_day(_awaits_us)
        assert "name" not in table.world.battle_days["days"]["Mack"]
        _muster_answered(table, table.order(_chip(day, "press")["command"]))
        names = _battle_names(table.world)
        assert not any(" — the " in n for n in names)
        assert not any(k.endswith(WorldState.DAY_CLASHES_SUFFIX) for k in table.world.battle_counts)

    def test_the_reckoning_names_the_battle(self):
        from backend.game_logic.game_end import _battle_subject
        assert BD.the_battle_of("The Great Battle of Swabia — the third clash") == "The Great Battle of Swabia"
        assert BD.the_battle_of("Battle of Munich") == "Battle of Munich"
        assert _battle_subject("Battle of Munich — the second clash") == "The Battle of Munich"
        assert _battle_subject("The Great Battle of Swabia") == "The Great Battle of Swabia"


class TestADaysCloseIsTold:
    """The user's tick — "Line for a quiet night" — widened under his "make any
    other improvements": every way a day ends is told in one line, with its
    clashes and its toll."""

    DAY = {"enemy": "Mack", "lead": "Ney", "field": "Swabia", "clashes": 3,
           "toll": {"ours": 9200, "his": 27500}}
    TOLL = " — 9,200 of ours for 27,500 of the enemy's."

    @pytest.mark.parametrize("how, head", [
        ("night", "Night fell on the field at Swabia: three clashes and no decision"),
        ("decided", "The day at Swabia was decided at the third clash"),
        ("drew_off", "Mack drew off from Swabia after three clashes"),
        ("he_broke_off", "Mack broke off his attack at Swabia after three clashes"),
        ("broke_off", "The attack at Swabia was broken off after three clashes"),
        ("fell_back", "Ney fell back from Swabia after three clashes"),
        ("over", "The day at Swabia ended where it stood after three clashes"),
    ])
    def test_every_way_a_day_ends(self, how, head):
        assert BD.close_line(None, dict(self.DAY), how) == head + self.TOLL

    def test_one_clash_is_one_clash(self):
        line = BD.close_line(None, dict(self.DAY, clashes=1), "night")
        assert line.startswith("Night fell on the field at Swabia: one clash and no decision — ")

    def test_a_day_that_kept_no_count_says_nothing(self):
        assert BD.close_line(None, {"enemy": "Mack", "lead": "Ney", "field": "Swabia"}, "night") == ""

    def test_the_closing_table_and_the_log_carry_it(self, table):
        body, day = table.open_a_day(_awaits_us)
        assert "close" not in day, "an open day has no close"
        body = table.word("break_off")
        closing = body["battle_day"]
        assert closing["open"] is False and closing["ended"] == "broke_off"
        # the field the day OPENED on, though he struck back on our ground since
        assert closing["close"].startswith("The attack at Lorraine was broken off after ")
        # (Row BA, BA-5: BA-4's line stands whole, and the close goes on after it
        # — whom the toll favoured, what kind of day it was.)
        assert " of the enemy's. " in closing["close"]
        rows = [e for e in table.world.event_log if e.get("type") == "battle_day_closed"]
        assert len(rows) == 1 and rows[0]["line"] == closing["close"]
        assert rows[0]["nation"] == "France" and rows[0]["how"] == "broke_off"
        from backend.campaign_log import filter_campaign_log, format_event_oneliner
        assert rows[0] in filter_campaign_log(table.world.event_log, table.world)
        assert format_event_oneliner(rows[0], "France", table.world) == closing["close"]

    def test_a_quiet_night_is_told_in_the_morning(self, table):
        """We leave the day awaiting our word and end the turn: night falls
        with no table to tell it. The morning's turn events do."""
        table.open_a_day(_awaits_us)
        turn = int(table.world.current_turn)
        ended = table.order("end turn")
        assert int(table.world.current_turn) == turn + 1, ended.get("message")
        assert not BD.open_days(table.world)
        rows = [e for e in table.world.event_log if e.get("type") == "battle_day_closed"]
        assert rows, "the close is on the record"
        line = rows[-1]["line"]
        assert line.startswith(("Night fell on the field at ", "The day at ", "Mack "))
        events = [e.get("message") for e in (ended.get("morning_dispatch") or {}).get("turn_events") or []]
        assert line in events, events

    def test_a_close_in_the_players_turn_is_not_repeated_at_dawn(self, table):
        table.open_a_day(_awaits_us)
        table.word("break_off")
        assert not BD._NIGHT.get(table.world), "the table told it: nothing is kept for the morning"

    def test_the_seam_down_is_a_banner_alone(self, table, monkeypatch):
        _down(monkeypatch, BD, "a_days_close_is_told")
        table.open_a_day(_awaits_us)
        closing = table.word("break_off")["battle_day"]
        assert "close" not in closing and closing["banner"] == "The attack is broken off"
        assert not [e for e in table.world.event_log if e.get("type") == "battle_day_closed"]

    def test_with_both_tellings_down_a_days_record_is_ba3s(self, table, monkeypatch):
        _down(monkeypatch, BD, "a_days_close_is_told")
        _down(monkeypatch, BD, "a_day_is_one_battle")
        table.open_a_day(_awaits_us)
        kept = table.world.battle_days["days"]["Mack"]
        assert not ({"name", "clashes", "toll", "close", "opened_at"} & set(kept)), sorted(kept)


class TestTheFirstDayNamesItsRules:
    """The user's tick — "First-open line": the first day of battle of a
    campaign says what a day is, once, in the table's own words."""

    def test_the_line(self):
        from backend.game_logic import first_open
        line = first_open.LINES["battle_day"](None, None)
        assert line == ("The day hangs, Sire. Each side holds points for the rest of it: a "
                        "word costs points, never an action, and the enemy answers each word "
                        "in turn. Two silences running, or every point spent, and night falls.")
        assert len(line) <= first_open.LINE_CAP and first_open.SCREENS[-1] == "battle_day"

    def test_the_open_block_carries_it_until_it_is_shown(self, table):
        from backend.game_logic import first_open
        _body, day = table.open_a_day(_awaits_us)
        assert day["first_open"] == {"screen": "battle_day",
                                     "line": first_open.LINES["battle_day"](None, None)}
        assert "battle_day" not in table.world.first_opens, "a read is not a showing"
        shown = _quiet(table.tc.post, "/first_open", json={"screen": "battle_day"}).json()
        assert shown["success"] and table.world.first_opens["battle_day"] == table.world.current_turn
        # on the turn it was shown the line stays (the table re-reads the day) ...
        assert "first_open" in table.days()["days"][0]
        # ... and on any later turn it is gone, for the rest of the campaign
        table.world.first_opens["battle_day"] = int(table.world.current_turn) - 1
        assert "first_open" not in table.days()["days"][0]

    def test_a_closing_block_does_not_carry_it(self, table):
        table.open_a_day(_awaits_us)
        assert "first_open" not in table.word("break_off")["battle_day"]


OLD_SAVE = REPO / "tests" / "fixtures" / "playtest_saves" / "fixture_ba3_open_day_aeae6967.json"
OLD_DAY_COUNT_KEYS = {"name", "clashes", "toll", "opened_at", "close"}


class TestASaveMadeBeforeTheSession:
    """An OLD save in the new server. The fixture was written by HEAD
    `aeae6967` (BA-3) through its own `/save`: the 1805 campaign on BA-3's
    Masséna board (seed `ba4-walk-00`), the Archduke Charles attacked, the day
    open after two clashes and awaiting our word. A day made before BA-4 keeps
    no count of its clashes, no toll and no name — it is played on as BA-3
    played it, and nothing is told of it that was never counted.

    Found by loading it: the day's NEXT clash began a count at one, and its
    close would have told "after one clash" and half the toll of a day of
    three (`battle_day._count_the_clash`: the count begins at a day's opening
    clash or not at all). The real client loads the same file in the live
    walk (`tools/ba4_mode_c_walk.py --board oldsave`)."""

    @pytest.fixture
    def old(self, table, tmp_path, monkeypatch):
        from backend import save_manager
        monkeypatch.setattr(save_manager, "SAVE_DIR", tmp_path)
        (tmp_path / OLD_SAVE.name).write_bytes(OLD_SAVE.read_bytes())
        loaded = _quiet(table.tc.post, "/load", json={"filename": OLD_SAVE.name}).json()
        assert loaded["success"], loaded.get("message")
        return table

    @staticmethod
    def _go(old, command):
        """An order by the ordinary road, the muster's "Commit the Attack" and
        a marshal's objection answered as the client's buttons answer them."""
        import backend.main as M
        body = old.order(command)
        asking = getattr(M.world.marshals["Massena"], "pending_interrupt", None)
        if asking and asking.get("interrupt_type") == "muster_confirm":
            body = _quiet(old.tc.post, "/strategic_response", json={
                "marshal_name": asking["marshal"], "response_type": asking["interrupt_type"],
                "choice": "attack_anyway"}).json()
        if getattr(M.world, "pending_objection", None):
            body = old.answer("insist")
        return body

    def test_the_fixture_is_ba3s(self):
        saved = json.loads(OLD_SAVE.read_text(encoding="utf-8"))
        state = saved["world_state"]
        day = state["battle_days"]["days"]["ArchdukeCharles"]
        assert not (OLD_DAY_COUNT_KEYS & set(day)), "a day BA-4 made is no old save"
        assert (day["lead"], day["words"], day["awaits"]) == ("Massena", 1, "ours")
        assert "battle_day" not in (state.get("first_opens") or {})
        assert not [k for k in state["battle_counts"] if "later clashes" in k]

    def test_its_open_day_is_offered_with_the_first_days_line(self, old):
        block = old.days()["days"][0]
        assert block["open"] and block["awaits"] == "ours" and (block["ours"], block["theirs"]) == (2, 2)
        assert [c["kind"] for c in block["chips"]][:2] == ["press", "dig_in"]
        assert block["first_open"]["screen"] == "battle_day", "this campaign has not seen a day's rules"
        assert not block.get("close")

    def test_a_word_on_it_begins_no_count_and_names_no_clash(self, old):
        block = old.days()["days"][0]
        body = self._go(old, _chip(block, "press")["command"])
        assert body["success"], body.get("message")
        assert " — the " not in body["battle_diorama"]["battle_name"], \
            "a day that has no name names no further clash"
        after = body["battle_day"]
        assert not after.get("close") and [t for t in after["told"] if t.get("kind") == "tally"] == []
        stored = (old.world.battle_days.get("days") or {}).get("ArchdukeCharles")
        if stored is not None:
            assert not (OLD_DAY_COUNT_KEYS & set(stored)), "no count begun at the day's third clash"
        assert not [k for k in old.world.battle_counts if "later clashes" in k]
        assert [e for e in old.world.event_log if e.get("type") == "battle_day_closed"] == []

    def test_its_close_tells_no_tally_it_never_kept(self, old):
        closing = old.word("break_off", enemy="ArchdukeCharles")["battle_day"]
        assert closing["ended"] == "broke_off" and not closing.get("close")
        assert [t.get("kind") for t in closing["told"]].count("tally") == 0
        assert closing["told"][-1]["line"] == "You break off the attack."
        assert [e for e in old.world.event_log if e.get("type") == "battle_day_closed"] == []

    def test_the_night_passes_over_it_and_the_save_goes_round_again(self, old):
        ended = old.order("end turn")
        if not ended.get("success", True) or ended.get("requires_confirmation"):
            ended = old.order("end turn confirm")
        assert old.world.current_turn == 2, ended.get("message")
        assert BD.open_days(old.world) == {}
        assert [e for e in old.world.event_log if e.get("type") == "battle_day_closed"] == [], \
            "the night closed a day that kept no count: it tells none"
        again = _quiet(old.tc.post, "/save", json={"save_name": "ba4_round_trip"}).json()
        back = _quiet(old.tc.post, "/load", json={"filename": "ba4_round_trip.json"}).json()
        assert again["success"] and back["success"]


class TestAnOrderDrawsItsOwnTemper:
    """BA3-X16. The seeded temper's identity was the marshal, the action and
    the target; a stance order carries its stance beside the target, so "go
    aggressive" and "go defensive" drew one mood, one severity, one defiance."""

    def test_the_mark(self):
        mark = campaign_variance.order_mark
        assert mark({"action": "attack", "target": "Mack"}) == ()
        assert mark({"action": "stance_change", "target": None, "target_stance": "aggressive"}) == (
            "target_stance=aggressive",)
        assert mark({"action": "recruit", "requested_type": "cavalry"}) == ("requested_type=cavalry",)
        assert mark({"action": "build_fleet", "count": 3}) == ("count=3",)
        assert mark({"target_stance": "", "count": 0, "requested_type": None}) == ()
        assert mark(None) == () and mark("attack") == ()

    def test_the_strategic_road_reads_the_parse_beside_the_command(self):
        mark = campaign_variance.order_mark
        command = {"marshal": "Ney", "target": "Vienna"}
        parse = {"command": command, "attack_on_arrival": True, "arrival_target": "Mack",
                 "standing_follow": False}
        assert mark(command, parse) == ("attack_on_arrival=True", "arrival_target=Mack")

    def test_an_order_with_no_mark_draws_as_it_did(self):
        """The identity only grows where a mark is present."""
        world, _ney, _mack = _served()
        a = campaign_variance.temper_rng(world, "mood", "Ney", "attack", "Mack")
        b = campaign_variance.temper_rng(world, "mood", "Ney", "attack", "Mack",
                                         *campaign_variance.order_mark({"action": "attack", "target": "Mack"}))
        assert [a.random() for _ in range(4)] == [b.random() for _ in range(4)]

    def test_the_seam_down_is_one_temper_for_both_stances(self, monkeypatch):
        """The twin of the row's pin (`test_ba3_the_review`)."""
        _down(monkeypatch, campaign_variance, "an_order_draws_its_own_temper")
        made = []
        real = campaign_variance._PrivateStream

        class Recording(real):
            def __init__(self, seed):
                made.append(str(seed))
                super().__init__(seed)

        monkeypatch.setattr(campaign_variance, "_PrivateStream", Recording)
        keys = {}
        for stance in ("aggressive", "defensive"):
            world = WorldState()
            world.campaign_seed = "iron-eagle-07"
            campaign_variance.serve_campaign(world)
            del made[:]
            _quiet(CommandExecutor().execute, {"command": {
                "action": "stance_change", "type": "specific", "marshal": "Davout",
                "target": None, "target_stance": stance}}, {"world": world})
            keys[stance] = [name for name in made if "|mood|" in name]
        if not all(keys.values()):
            raise RuntimeError(f"a stance order drew no mood on this board: {keys}")
        assert keys["aggressive"] == keys["defensive"]

    def test_every_site_that_keys_an_order_reads_the_mark(self):
        sources = {name: (REPO / "backend" / "commands" / name).read_text(encoding="utf-8")
                   for name in ("executor.py", "severity.py", "meta_executor.py", "strategic_executor.py")}
        assert '(command or {}).get("target"), *_cv.order_mark(command))' in sources["executor.py"]
        assert "*_order_mark(order)))" in sources["severity.py"]
        assert "*_cv.order_mark(_ws16_order))" in sources["meta_executor.py"]
        assert sources["strategic_executor.py"].count("_cv.order_mark(") == 2


# ════════════════════════════════════════════════════════════════════════
# BA2-X20 — a battle lights its field for those who fought in it; a battle
# abroad is news
# ════════════════════════════════════════════════════════════════════════

def _lithuania(*, men=(50000, 50000), ally=False, scouted=False, seed=1):
    """Prussia attacks an Austrian corps in Lithuania — Russia's soil, far from
    any French corps (the row's own staging). Returns (world, reply, the
    sight France had of the province before the battle)."""
    world, executor = STAGE._board()
    STAGE._war(world, "Prussia", "Austria")
    if ally:
        world.diplomatic_states[world._make_diplo_key("France", "Prussia")] = "ALLIANCE"
    hohenlohe, john = world.marshals["Hohenlohe"], world.marshals["ArchdukeJohn"]
    john.location = "Lithuania"
    hohenlohe.strength, john.strength = men
    if scouted:
        world.update_intel_from_battle("Lithuania", int(world.current_turn))
    before = world.get_region_intel("Lithuania").visibility
    random.seed(seed)
    with STAGE._quiet():
        reply = executor._execute_attack(hohenlohe, "ArchdukeJohn", world,
                                         {"world": world, "executor": executor})
    assert reply.get("success"), reply.get("message")
    return world, reply, before


def _news(world):
    return [e for e in world.event_log if e.get("type") == "foreign_battle"]


class TestABattleLightsItsFieldForThoseWhoFought:
    """BA2-X20. "Fighting in a region immediately grants FULL visibility of
    that region" was written when every battle was the player's. The courts
    fight each other now, and each of their battles lit its province for him:
    the commanders, the exact men and the morale of two crowns he had no one
    near, for two turns. (The row's own pin is `tests/test_ba2_the_review.py`,
    a plain test since this session.)"""

    def test_who_a_battle_lights_its_field_for(self):
        world, _executor = STAGE._board()
        ney, mack, hohenlohe = (world.marshals[n] for n in ("Ney", "Mack", "Hohenlohe"))
        lights = intel_surfaces.battle_lights_field
        assert world.get_region("Lithuania").controller != "France"
        assert lights(world, "Lithuania", ney, mack), "his crown attacks"
        assert lights(world, "Lithuania", mack, ney), "his crown defends"
        assert lights(world, "Lithuania", hohenlohe, mack, [ney]), "a corps of his fought in it"
        assert lights(world, "Lithuania", "Prussia", "France"), "a crown may be named"
        assert not lights(world, "Lithuania", hohenlohe, mack, [], ()), "two other crowns, another's soil"
        own = next(name for name, region in world.regions.items() if region.controller == "France")
        assert lights(world, own, hohenlohe, mack), "any battle on his own soil"

    def test_a_battle_of_two_other_crowns_leaves_his_sight_as_it_was(self):
        world, _reply, before = _lithuania()
        assert before not in (FULL, PARTIAL)
        assert world.get_region_intel("Lithuania").visibility == before
        assert not world.get_region_intel("Lithuania").known_marshals

    def test_the_seam_down_lights_every_field(self, monkeypatch):
        _down(monkeypatch, intel_surfaces, "a_battle_lights_its_field_only_for_those_who_fought")
        world, _reply, before = _lithuania()
        assert before != FULL and world.get_region_intel("Lithuania").visibility == FULL
        assert not _news(world), "and a field in sight is no news"

    def test_his_own_battle_still_lights_its_field(self):
        world, executor = STAGE._board()
        world.get_region_intel("Swabia").visibility = PARTIAL
        random.seed(0)
        with STAGE._quiet():
            executor._execute_attack(world.marshals["Ney"], "Mack", world,
                                     {"world": world, "executor": executor})
        assert world.get_region_intel("Swabia").visibility == FULL
        assert not _news(world), "his own battle is told by its own row"

    def test_the_method_itself_is_untouched(self):
        """A caller that lights a province by hand (a scout's report, a
        test's board) still lights it: the rule sits at the battle's sites."""
        world, _executor = STAGE._board()
        world.update_intel_from_battle("Lithuania", int(world.current_turn))
        assert world.get_region_intel("Lithuania").visibility == FULL

    def test_every_battle_site_asks_before_it_lights(self):
        """Five roads resolve a battle and lit its field: the attack, the
        post-combat pipeline, the garrison assault, the bombardment, and the
        cavalry's charge at the turn's start."""
        for path, sites in (("backend/commands/combat_executor.py", 4),
                            ("backend/models/world_state.py", 1)):
            lines = (REPO / path).read_text(encoding="utf-8").split("\n")
            calls = [i for i, line in enumerate(lines)
                     if "update_intel_from_battle(" in line and "def " not in line
                     and not line.lstrip().startswith(("#", "`", "\"")) and "`" not in line]
            assert len(calls) == sites, (path, [i + 1 for i in calls])
            for i in calls:
                guard = "\n".join(lines[max(0, i - 8):i])
                assert "battle_lights_field(" in guard, f"{path}:{i + 1} lights a field unasked"


class TestNewsOfABattleAbroad:
    """So that Europe does not go dark with the rule: a GREAT battle between
    other crowns, or an ally's in a war the player shares, is news — the
    crowns, the province, how the day ended. Never a commander or a figure."""

    def test_the_sentences(self):
        line = battle_news.line_of
        assert line("Lithuania", "Prussia", "Austria", ("held", "Austria"), great=True) == (
            "News from Lithuania: Prussia and Austria have fought a great battle — "
            "Austria held the field.")
        assert line("Lithuania", "Prussia", "Austria", ("better", "Prussia"), great=True).endswith(
            " — Prussia had the better of the day.")
        assert line("Lithuania", "Prussia", "Austria", ("drawn", ""), great=True).endswith(
            " — the day was drawn.")
        assert line("Lithuania", "Prussia", "Austria", ("ruin", ""), great=True).endswith(
            " — both armies were ruined on it.")
        assert line("Lithuania", "Prussia", "Austria", ("held", "Prussia"), great=False,
                    ally="Prussia") == ("News from Lithuania: our ally Prussia has fought Austria — "
                                        "Prussia held the field.")
        assert line("Tyrol", "Austria", "Bavaria", ("drawn", ""), great=False, ally="Bavaria") == (
            "News from Tyrol: our ally Bavaria has fought Austria — the day was drawn.")

    @pytest.mark.parametrize("outcome, verdict", [
        ("attacker_victory", ("held", "Prussia")), ("defender_victory", ("held", "Austria")),
        ("attacker_tactical_victory", ("better", "Prussia")),
        ("defender_tactical_victory", ("better", "Austria")),
        ("stalemate", ("drawn", "")), ("mutual_destruction", ("ruin", "")), ("", ("drawn", ""))])
    def test_how_the_day_ended(self, outcome, verdict):
        assert battle_news.the_days_verdict({"outcome": outcome}, "Prussia", "Austria") == verdict

    def test_a_great_battle_abroad_is_news(self):
        world, reply, _before = _lithuania()
        [news] = _news(world)
        assert news["great"] is True and news["crowns"] == ["Prussia", "Austria"]
        assert news["location"] == "Lithuania"
        line = news["line"]
        # Row BA, BA-5 (the user's tick at its plan gate — "Name the commanders"):
        # a GREAT battle's news names its two commanders (the table's own law: a
        # great battle names its commander). It read "Prussia and Austria have
        # fought a great battle" and named no man; the seam's down twin is
        # `tests/test_ba5_the_finish.py`. Still never a figure.
        assert line.startswith("News from Lithuania: a great battle — ")
        assert "Hohenlohe of Prussia" in line and "Archduke John of Austria" in line
        assert news["commanders"] == ["Hohenlohe", "ArchdukeJohn"]
        assert not any(ch.isdigit() for ch in line), "no figure"
        # the player's log carries the news and not the battle's own row
        from backend.campaign_log import filter_campaign_log, format_event_oneliner
        shown = filter_campaign_log(world.event_log, world)
        assert news in shown and not [e for e in shown if e.get("type") == "battle"]
        assert format_event_oneliner(news, "France", world) == line
        # and the morning's dispatch has it queued, in the same words
        queued = [e for e in world.pending_dispatch_events if e.get("type") == "battle_news"]
        assert [e["template_vars"]["line"] for e in queued] == [line]
        from backend.game_logic.dispatch import _format_dispatch_event_text
        assert _format_dispatch_event_text("battle_news", {"line": line}) == line

    def test_a_small_battle_abroad_is_none(self):
        world, _reply, _before = _lithuania(men=(20000, 20000))
        assert not _news(world)
        assert not [e for e in world.pending_dispatch_events if e.get("type") == "battle_news"]

    def test_an_allys_battle_in_a_shared_war_is_news_though_small(self):
        world, _reply, _before = _lithuania(men=(20000, 20000), ally=True)
        [news] = _news(world)
        assert news["great"] is False and news["ally"] == "Prussia"
        assert news["line"].startswith("News from Lithuania: our ally Prussia has fought Austria — ")

    def test_an_ally_fighting_a_court_we_are_at_peace_with_is_not_our_war(self):
        world, _executor = STAGE._board()
        world.diplomatic_states[world._make_diplo_key("France", "Prussia")] = "ALLIANCE"
        assert battle_news.an_allys_in_a_shared_war(world, "France", "Prussia", "Austria") == "Prussia"
        assert battle_news.an_allys_in_a_shared_war(world, "France", "Austria", "Prussia") == "Prussia"
        world.diplomatic_states[world._make_diplo_key("France", "Austria")] = "PEACE"
        assert battle_news.an_allys_in_a_shared_war(world, "France", "Prussia", "Austria") == ""

    def test_a_field_in_his_sight_is_told_by_the_battles_own_row(self):
        world, _reply, before = _lithuania(scouted=True)
        assert before == FULL and not _news(world)
        from backend.campaign_log import filter_campaign_log
        assert [e for e in filter_campaign_log(world.event_log, world) if e.get("type") == "battle"]

    def test_le_moniteur_prints_it_and_a_great_one_forces_a_special(self):
        from backend.game_logic import gazette
        assert "foreign_battle" in gazette._WAR_TYPES
        assert gazette._SPECIAL_WEIGHTS["a great battle abroad"] == 55
        world, _reply, _before = _lithuania()
        reasons = [reason for _weight, reason, _key in gazette._special_candidates(world, _news(world))]
        assert reasons == ["a great battle abroad"]
        assert gazette._special_reason(world, _news(world)) == "a great battle abroad"
        small, _reply, _before = _lithuania(men=(20000, 20000), ally=True)
        assert not gazette._special_candidates(small, _news(small)), \
            "an ally's ordinary battle waits for the regular issue"

    def test_the_two_types_are_on_the_logs_books(self):
        from backend import campaign_log
        for kind in ("foreign_battle", "battle_day_closed"):
            assert kind in campaign_log.CAMPAIGN_LOG_TYPES
        assert len(campaign_log.CAMPAIGN_LOG_TYPES) == 188


# ════════════════════════════════════════════════════════════════════════
# The client: the digits on the table, the first day's line, a word's price,
# a halted order's clock, the help
# ════════════════════════════════════════════════════════════════════════
# What the client DOES is driven in the real engine: the days-panel walk
# (`tests/test_ba3_the_days_panel.py::TestThePanelDriven` — a real key a digit,
# the first day's row on Ulm) and the live walk of record
# (`tools/ba4_mode_c_walk.py`). Here: the backend's half of each rule, and the
# source's own shape where a rule is one line that must not drift.

SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"


def _gd(name):
    return (SCRIPTS / name).read_text(encoding="utf-8")


def _gd_func(source, name):
    """One function's text, to the next top-level definition."""
    start = source.index(f"func {name}(")
    following = re.search(r"\n(?:static func |func |class |const |var |signal |# ─)", source[start + 1:])
    return source[start: start + 1 + following.start() if following else len(source)]


class TestAHaltedOrdersQuoteSaysSo:
    """The approach rule's quote: the card's clock read "joins him in 2
    turns" — the road he will not walk this turn — over a line that said he
    halts. The quote carries `halts`; the card and the panel print it."""

    def test_the_quote_carries_it_where_the_order_halts(self):
        world, _executor = STAGE._board()
        murat, ney = world.marshals["Murat"], world.marshals["Ney"]
        quote = order_quotes.support_quote(world, murat, ney)
        assert quote["halts"] is True and "halts at the approach" in quote["contact"]

    def test_an_order_that_marches_carries_none(self):
        world, _executor = _staged("Bohemia", "Ney", "Munich", "Soult", "Swabia")
        quote = order_quotes.support_quote(world, world.marshals["Soult"], world.marshals["Ney"])
        assert quote["ok"] and "halts" not in quote

    def test_the_seam_down_is_the_question_and_no_halt(self, monkeypatch):
        _down(monkeypatch, road_law, "a_support_order_halts_before_the_friends_foe")
        world, _executor = STAGE._board()
        quote = order_quotes.support_quote(world, world.marshals["Murat"], world.marshals["Ney"])
        assert "halts" not in quote

    def test_the_card_and_the_panel_print_it(self):
        clock = _gd_func(_gd("order_confirm_card.gd"), "_clock")
        assert 'if bool(q.get("halts", false)):' in clock and 'return "halts at the approach"' in clock
        label = _gd_func(_gd("region_panel.gd"), "_quote_label")
        assert 'if bool(q.get("halts", false)):' in label and '" · halts at the approach"' in label


class TestAWordsPriceInTheClient:
    """BA3-X5's client half: the card printed "free" over a word of the day
    (the quote's `ap` is 0) and the province's chips "0 AP"."""

    def test_one_helper_for_the_card_and_the_chips(self):
        utils = _gd("utils.gd")
        price = _gd_func(utils, "quote_price")
        assert 'str(q.get("price", "")).strip_edges()' in price
        tail = _gd_func(utils, "quote_price_tail")
        assert 'if str(q.get("word", "")) != "":' in tail
        assert 'return "free" if points <= 0 else plural(points, "point")' in tail
        # the review (lane 5): an order taken at no action is "free" on the
        # chip, as on the card and the map's badge (`tests/test_ba4_the_review.py`)
        assert 'return str(ap) + " AP"' in tail
        card = _gd("order_confirm_card.gd")
        assert "Utils.quote_price(q)" in _gd_func(card, "price_of")
        assert 'lines.append("[b]" + price_of(q) + "[/b] · " + _clock(q))' in card
        assert "Utils.quote_price_tail(b)" in _gd_func(card, "bring_label")
        panel = _gd("region_panel.gd")
        assert "Utils.quote_price_tail(q)" in _gd_func(panel, "_quote_label")
        assert "Utils.quote_price_tail(b)" in _gd_func(panel, "_bring_label")
        # the one chip that still prints its actions itself is the army's (the
        # Staff's order is never a word of a day)
        assert _gd_func(panel, "_quote_label").count('+ " AP"') == 1
        assert '+ " AP"' not in _gd_func(panel, "_bring_label")
        assert '+ " AP"' not in _gd_func(card, "bring_label")

    def test_the_quote_gives_the_client_what_it_prints(self, table):
        world, _day, ney, mack, _davout = _a_day_with_a_second_corps(table)
        quote = order_quotes.attack_quote(world, ney, mack)
        assert (quote["ap"], quote["points"], quote["word"]) == (0, 1, "press")
        assert quote["price"] == "a word of the day — 1 point"

    def test_the_maps_ghost_road_prices_it_the_same(self):
        """Found by pressing it in the real client: the card said "A word of
        the day — 1 point" and the badge at the head of the ghost road beside
        it, on the map, said "attack · free" (the quote's `ap` is 0). The
        badge reads the chips' helper; and a halted order's badge says so
        where it said its road's turns (the card's `_clock` rule). The live
        walk reads both badges (`tools/ba4_mode_c_walk.py`: `card_before`,
        `card_during_the_day`, `approach_card`)."""
        label = _gd_func(_gd("main.gd"), "_order_ghost_label")
        assert 'if str(q.get("word", "")) != "":\n\t\tprice = Utils.quote_price_tail(q)' in label
        assert 'if bool(q.get("halts", false)):\n\t\treturn "halts at the approach · " + price' in label
        assert label.index('return "attack · " + price') < label.index('return "halts at the approach · "')
        # an ordinary order's badge is as it was: its actions, "free" for none
        assert 'var price := "free" if ap <= 0 else "%d AP" % ap' in label

    def test_the_province_does_not_offer_a_word_twice(self):
        """While a day is open its chips stand above the province's actions;
        the same attacks are not listed again under ATTACK as ordinary orders."""
        body = _gd("region_panel.gd")
        assert 'str((q as Dictionary).get("word", "")) == ""' in body
        assert "if ordinary.is_empty():\n\t\t\t\t\tcontinue" in body
        assert "out += _quote_rows(ordinary)" in body


class TestTheDayTakesTheOrderItsTableOffers:
    """BA4-X1 — found by loading an old save in the real client: with BA3-X5
    in, the province's panel priced "Murat, support Massena" at "1 point"
    while Murat stood in Paris, five provinces from the field. The quote was
    true to the door: BA-3's taker read EVERY support order for a day's lead
    as "a corps is brought up" — a point of the day spent, "Murat is ordered
    up." told and the enemy's next word given, for a march of three turns no
    day would see — though the day's own table offered no such chip. The
    taker asks the plan's reading (`order_quotes.the_order_brings`, the
    "Bring up" chip's own): any other support order is an ordinary order."""

    @staticmethod
    def _far_from(world, field, at_least=3):
        return next(name for name in sorted(world.regions)
                    if (world.get_distance(name, field) or 0) >= at_least)

    def _a_day_and_a_far_corps(self, table):
        table.open_a_day(_awaits_us)
        world = table.world
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        far = _mk("Davout", self._far_from(world, mack.location), 20000, personality="literal")
        world.marshals["Davout"] = far
        return world, ney, mack, far

    def test_a_corps_far_from_the_field_is_no_word(self, table):
        world, ney, mack, far = self._a_day_and_a_far_corps(table)
        assert BD.quoted_word(world, "Davout", "support", "Ney", "SUPPORT") is None
        quote = order_quotes.support_quote(world, far, ney)
        assert quote["ok"] and quote["ap"] == 1 and not quote.get("word") and not quote.get("points")
        chips = table.days()["days"][0]["chips"]
        assert not [c for c in chips if c["kind"] == "bring_up"], "and the table offers none"

    def test_sent_it_costs_its_action_and_the_day_is_not_touched(self, table):
        world, ney, _mack, far = self._a_day_and_a_far_corps(table)
        day = world.battle_days["days"]["Mack"]
        before = (int(day["ours"]), int(day["theirs"]), int(day["words"]), len(day["told"]), day["awaits"])
        pool = int(world.actions_remaining)
        sent = table.order("Davout, support Ney")
        if getattr(table.world, "pending_objection", None):
            sent = table.answer("insist")
        assert sent["success"], sent.get("message")
        world = table.world
        day = world.battle_days["days"]["Mack"]
        assert int(world.actions_remaining) == pool - 1, "an ordinary order, at its action"
        assert (int(day["ours"]), int(day["theirs"]), int(day["words"]), len(day["told"]),
                day["awaits"]) == before, "no point spent, no line told, no answer of his"
        assert "battle_day" not in sent or not sent["battle_day"]

    def test_the_readback_and_the_relay_price_it_as_an_order(self, table):
        world, *_ = self._a_day_and_a_far_corps(table)
        read = _readback(table, "Davout, support Ney")
        assert read["ap"] == 1 and not read.get("word") and not read.get("points")
        note = relay.second_name_relay_note(world, "Davout", "Davout, support Ney")
        assert "a word of the day" not in note

    def test_the_taker_is_the_offer(self, table):
        """One reading for both: on a board with a corps the plan would bring,
        one that would come without an order, and one far off, the day takes
        as a word exactly the orders its table shows lit as "Bring up"."""
        table.open_a_day(_awaits_us)
        world = table.world
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        world.marshals["Davout"] = _mk("Davout", HOME, 20000, personality="literal")
        world.marshals["Soult"] = _mk("Soult", HOME, 20000, personality="aggressive")
        world.marshals["Lannes"] = _mk("Lannes", self._far_from(world, mack.location), 20000,
                                       personality="literal")
        offered = {c["label"].replace("Bring up ", "") for c in table.days()["days"][0]["chips"]
                   if c["kind"] == "bring_up" and c["ok"]}
        taken = {name for name in ("Davout", "Soult", "Lannes")
                 if BD.quoted_word(world, name, "support", "Ney", "SUPPORT") is not None}
        assert offered == taken and "Davout" in taken and "Lannes" not in taken, (offered, taken)
        assert ney.name not in taken

    def test_the_seam_down_takes_every_support_order_for_the_lead(self, table, monkeypatch):
        _down(monkeypatch, BD, "a_brought_up_corps_is_one_the_table_offers")
        world, ney, _mack, far = self._a_day_and_a_far_corps(table)
        quote = order_quotes.support_quote(world, far, ney)
        assert (quote["ap"], quote["points"], quote["word"]) == (0, 1, "bring_up")
        purse, pool = _purse(world), int(world.actions_remaining)
        sent = table.order("Davout, support Ney")
        if getattr(table.world, "pending_objection", None):
            sent = table.answer("insist")
        assert sent["success"], sent.get("message")
        assert int(table.world.actions_remaining) == pool
        assert _purse(table.world) in (purse - 1, -1), "BA-3's taker: a point of the day (or the day itself)"

    def test_the_quote_of_a_quote_does_not_ask_forever(self, table):
        """The plan's row is a support quote, whose price asks the day, which
        asks the plan: the question is asked once (`battle_day._WEIGHING`)."""
        world, _day, ney, mack, _davout = _a_day_with_a_second_corps(table)
        rows = order_quotes.attack_quote(world, ney, mack)["bring"]
        assert [r["marshal"] for r in rows] == ["Davout"] and rows[0]["word"] == "bring_up"
        assert BD._WEIGHING.get() is False


class TestTheKeyBar:
    """The user's "dor erseaarch of whats the most FUN" — the bar a battle
    must reach to be fought on with the day's points, settled by a rule
    written before the data (`BATTLE_DIORAMA_SPEC.md` §15.19) and a measured
    ladder (§15.20 M6; `tools/_ba4_kbar_2026_11_16.json`): the LOWEST of
    50,000 / 60,000 / 70,000 / 80,000 whose days are rich, varied and rested
    with the band and the hand in place. It is 50,000. The game's GREAT
    battle keeps its 80,000, its name and its news."""

    def test_the_bar(self):
        world = WorldState()
        assert BD.KEY_BATTLE_MEN == 50_000 and BD.key_bar(world) == 50_000
        assert world.GREAT_BATTLE_THRESHOLD == 80_000
        world.GREAT_BATTLE_THRESHOLD = 40_000
        assert BD.key_bar(world) == 40_000, "never above the game's great battle"

    def test_a_pitched_battle_that_hangs_opens_a_day(self, table):
        """60,000 men: under the great bar, over the key one."""
        _body, day = table.open_a_day(_awaits_us, ours=30000, his=30000)
        assert day["open"] and day["awaits"] == "ours"
        stored = table.world.battle_days["days"]["Mack"]
        assert "Battle of" in stored["name"] and "Great" not in stored["name"], \
            "a pitched battle is no Great Battle by name"

    def test_a_battle_under_it_opens_none(self, table):
        _seat(table.world, ours=24000, his=24000)
        body = table.order("Ney, attack Mack")
        assert body["success"] and "battle_day" not in body and table.world.battle_days == {}

    def test_the_card_calls_it_a_pitched_battle(self, table):
        _seat(table.world, ours=30000, his=30000)
        quote = order_quotes.attack_quote(table.world, table.world.marshals["Ney"],
                                          table.world.marshals["Mack"])
        assert quote["day"]["pitched"] is True and quote["day"]["bar"] == 50_000
        card = _gd("order_confirm_card.gd")
        assert 'var battle_said := "A pitched battle" if bool(day.get("pitched", false)) else "A great battle"' in card
        assert 'lines.append("[color=#" + Utils.COLOR_GOLD + "]" + battle_said + " — "' in card

    def test_the_help_says_the_two_bars(self):
        source = _gd("codex_terms.gd")
        assert "When a pitched battle — 50,000 men or more engaged, both sides together — does not decide the day" \
            in source
        assert "A battle with 80,000 men or more engaged, both sides together: its name says so" in source

    def test_the_session_off_holds_the_bar_at_the_great_battles(self, table, monkeypatch):
        """The bar is a number, not a switch, and the session OFF is the bar
        every board before it was recorded under: with it held, the pitched
        battle that opens a day above opens none. (Found by the full suite on
        the final tree — RS-27's scripted arm met five days where it had met
        three — when the hold-list held sixteen switches and no bar.)"""
        from tests._oct27_seams import hold_down
        assert BA4_THE_KEY_BAR == ["backend.game_logic.battle_day:key_bar=80000"]
        assert BA4_SESSION_OFF == BA4_SEAMS_DOWN + BA4_THE_KEY_BAR
        assert BA4_THE_KEY_BAR[0] in OCT27_SEAMS_DOWN, "a recorded board replays under its own bar"
        hold_down(monkeypatch, BA4_THE_KEY_BAR)
        assert BD.key_bar(table.world) == 80_000 == table.world.GREAT_BATTLE_THRESHOLD
        _seat(table.world, ours=30000, his=30000)
        quote = order_quotes.attack_quote(table.world, table.world.marshals["Ney"],
                                          table.world.marshals["Mack"])
        assert "day" not in quote, "no day is forecast under the bar"
        body = table.order("Ney, attack Mack")
        assert body["success"] and "battle_day" not in body and table.world.battle_days == {}

    def test_the_pick_is_the_rules(self):
        """The rule, applied to the ladder's record: the lowest bar that
        passes rich, varied, rested and the band — and the bar in the code is
        that one."""
        record = json.loads((REPO / "tools" / "_ba4_kbar_2026_11_16.json").read_text(encoding="utf-8"))
        passing = sorted(int(bar) for bar, cell in record["bars"].items()
                         if all(cell["rule"][k] for k in ("rich", "varied", "rested", "band_in")))
        assert sorted(int(b) for b in record["bars"]) == [50000, 60000, 70000, 80000]
        assert passing and passing[0] == BD.KEY_BATTLE_MEN
        rule = record["bars"]["50000"]["rule"]
        assert rule["runs"] == 16 and rule["rich_share"] >= 2 / 3 and rule["repeat_share"] <= 0.2
        assert rule["days_per_campaign"] <= 8 and rule["campaigns_with_four_turns_running"] <= 1


class TestTheDigitsOnTheTable:
    """The user's ruling at the plan gate — "Yes, on the table". The slots are
    fixed, as the selection card's are; the rule is the client's
    (`battle_acts.gd`) and the walk works it again from the block alone
    (`tools/ba1_acts_walk.day_digits`)."""

    def test_the_fixed_slots(self):
        acts = _gd("battle_acts.gd")
        assert 'const DAY_DIGIT_OWN := {"press": 1, "guard": 2, "dig_in": 3}' in acts
        for line in ("const DAY_DIGIT_GROUP_FROM := 4", "const DAY_DIGIT_GROUP_TO := 6",
                     "const DAY_DIGIT_STAND := 7", "const DAY_DIGIT_BREAK := 8",
                     "const DAY_DIGIT_LEAVE := 9"):
            assert line in acts, line

    def test_the_walks_reading_of_the_slots(self):
        from tools import ba1_acts_walk as walk
        chips = [{"kind": "press", "ok": True}, {"kind": "guard", "ok": True}, {"kind": "dig_in", "ok": True},
                 {"kind": "lead", "ok": True}, {"kind": "lead", "ok": True}, {"kind": "cannonade", "ok": True},
                 {"kind": "bring_up", "ok": True},
                 {"kind": "stand", "word": "stand", "ok": True},
                 {"kind": "break_off", "word": "break_off", "ok": True},
                 {"kind": "stand", "word": "leave_it", "ok": True}]
        assert walk.day_digits(chips) == {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 7: 7, 8: 8, 9: 9}, \
            "the seventh corps chip is the mouse's"
        assert walk.day_digits([{"kind": "dig_in", "ok": True},
                                {"kind": "break_off", "command": "Ney, retreat", "ok": True},
                                {"kind": "stand", "word": "stand", "ok": True}]) == {0: 3, 1: 8, 2: 7}

    def test_a_key_is_the_days_only_on_a_table_at_rest_that_offers(self):
        acts = _gd("battle_acts.gd")
        live = _gd_func(acts, "day_keys_live")
        for clause in ("host.visible", "host._acts == self", "bool(host._final)",
                       "_day_panel.visible", "_day_offering()"):
            assert clause in live, clause
        key = _gd_func(acts, "day_key")
        assert "if n <= 0 or not day_keys_live():\n\t\treturn false" in key
        assert "AudioManager.play(DAY_DENY_CUE)" in key and '_on_day_chip("day:%d" % index)' in key
        digit = _gd_func(acts, "day_digit")
        assert "key.ctrl_pressed or key.alt_pressed" in digit and "key.shift_pressed" in digit
        assert "class DayKeys:\n\textends Node" in acts
        assert "get_viewport().set_input_as_handled()" in acts[acts.index("class DayKeys:"):][:600]

    def test_the_host_is_untouched(self):
        """The tableau's host keeps its bodies and its five hooks: the keys are
        a node of the acts' own, under the day's panel."""
        host = _gd("battle_diorama.gd")
        assert host.count("_acts.") == 5
        assert "DayKeys" not in host and "day_key" not in host

    def test_the_walk_reads_every_kind_of_shot_it_builds(self):
        """Found by the switch-off table (November 16, 2026): the walk built
        and shot the digits' six kinds and its reader's list did not name
        them, so three digit fixes switched off walked green. Every kind the
        walk builds is one its reader names — by kind, or by the shot's id."""
        from tools import ba1_acts_walk as walk
        source = (REPO / "tools" / "ba1_acts_walk.py").read_text(encoding="utf-8")
        built = {shot["id"].rsplit("__", 1)[-1]
                 for shot in walk.build_shots(walk.OUT / "payloads", [], 1.0) if "__" in shot["id"]}
        digits = {"digit_own", "digit_group", "digit_exit", "digit_empty", "digit_locked", "digit_playing"}
        assert digits <= built, "the staged days give every digit its shot"
        claims = source[source.index("def _day_press_claims("):source.index("def check(")]
        handled = set(re.findall(r'kind == "([a-z_]+)"', claims))
        for group in re.findall(r"kind in \(([^)]*)\)", claims):
            handled |= set(re.findall(r'"([a-z_]+)"', group))
        handled &= built
        gate = re.search(r'rid\.rsplit\("__", 1\)\[-1\] in \((.*?)\):\s*\n\s*problems \+= _day_press_claims',
                         source[source.index("def check("):], flags=re.S)
        assert gate, "the reader's list of the kinds whose presses it claims"
        named = set(re.findall(r'"([a-z_]+)"', gate.group(1)))
        assert digits <= handled and sorted(handled - named) == [], "a kind is claimed and never read"

    @pytest.mark.parametrize("kind, tag, key, value, said", [
        # the three fixes the switch-off table switches off, as the record would read
        ("digit_own", "pressed", "emitted", [], "wanted exactly"),
        ("digit_empty", "pressed", "denied", 0, "was not denied"),
        ("digit_playing", "pressed", "emitted", ["Ney, attack"], "a digit while the acts play gave"),
    ])
    def test_a_digit_that_misbehaves_fails_the_walk(self, kind, tag, key, value, said):
        """The same find, as behaviour: the walk's record of record, read
        again by the walk's own reader, is clean — and is not once a digit's
        shot says what the fix prevents."""
        import copy
        from tools import ba1_acts_walk as walk
        record = json.loads((walk.OUT / "walk_record.json").read_text(encoding="utf-8"))
        shots = walk.build_shots(walk.OUT / "payloads", [], 1.0)
        assert walk.check({"results": record["results"]}, shots) == []
        doctored, hit = copy.deepcopy(record["results"]), 0
        for res in doctored:
            if not res["id"].endswith("__" + kind):
                continue
            for row in res["frames"]:
                if row.get("tag") == tag:
                    target = row if key == "emitted" else row["day"]
                    target[key] = value
                    hit += 1
        assert hit >= 1, f"no {kind} shot on the record"
        told = walk.check({"results": doctored}, shots)
        assert any("(BA4-k)" in line and said in line for line in told), told[:3]


class TestTheFirstDaysLineInTheClient:
    def test_its_showing_is_no_word(self):
        """The table's road (`word_given`) carries words and the one refresh;
        the acknowledgement goes to the scene that holds the API client."""
        acts = _gd("battle_acts.gd")
        note = _gd_func(acts, "_note_first_open")
        assert 'node.has_method("_on_first_open_seen")' in note and "node = node.get_parent()" in note
        assert "@first_open" not in acts and "@first_open" not in _gd("main.gd")
        assert "func _on_first_open_seen(screen: String) -> void:" in _gd("main.gd")

    def test_it_never_scrolls_a_chip_for_its_row(self):
        """(Row BA, BA-5: the panel's rows are ONE ladder now — the line gives up
        its row at the fifth step, before a card loses its second line and
        before the groups scroll; `_day_first_fits` is gone. The second reading
        put two steps between them: the panel's lift and the exits' cards.)"""
        acts = _gd("battle_acts.gd")
        assert "func _day_first_fits(" not in acts
        build = _gd_func(acts, "_build_the_day")
        line_goes = build.index("first_row = false                     # 5")
        cards_go = build.index("cards = false                         # 7")
        assert line_goes < cards_go < build.index("d_box.scroll_active = true")
        assert build.count("hover.append(first_said)") == 2, "no room: the head's hover, in both branches"


class TestTheHelpNamesTheSessionsRules:
    TERMS = ("The last hour", "News of a battle", "Pursuit")

    def _terms(self):
        source = _gd("codex_terms.gd")
        block = source[source.index("const TERMS: Array = ["):]
        block = block[: block.index("\n]")]
        return [row.split('", "', 1) for row in block.split('\n\t["')[1:]]

    def test_the_three_terms_are_there_in_their_places(self):
        names = [row[0] for row in self._terms()]

        def key(name):
            return name[4:].lower() if name.startswith("The ") else name.lower()
        for term in self.TERMS:
            assert term in names, term
            at = names.index(term)
            assert key(names[at - 1]) < key(term) < key(names[at + 1]), (
                f"{term!r} stands between {names[at - 1]!r} and {names[at + 1]!r}: "
                "A to Z, the article aside")

    def test_they_state_the_rules_numbers(self):
        said = {row[0]: row[1] for row in self._terms()}
        assert "five points or fewer" in said["The last hour"] and "three-quarters" in said["The last hour"]
        assert "5,000" in said["Pursuit"] and "fought beside him" in said["Pursuit"]
        # (Row BA, BA-5: a great battle's news names its two commanders — the
        # user's tick; the page said "never a commander or a figure".)
        assert "a great battle's two commanders by name" in said["News of a battle"]
        assert "never a figure" in said["News of a battle"]
        assert "digits 1 to 9" in said["The day's points"]
        assert "A lead holds one day at a time" in said["The day's points"]
        assert "one you fought in" in said["Fog of war"]


class TestTheMeasureReadsEverySeam:
    def test_the_ladder_is_the_hold_list(self):
        """Every seam of the session is an arm of the ONE measure
        (`tools/_ba4_measure.py`), and the measure holds nothing down that the
        recorded boards do not."""
        from tools import _ba4_measure as measure
        ladder = sorted(f"{spec}=False" for specs in measure.LADDER.values() for spec in specs)
        assert ladder == sorted(BA4_SEAMS_DOWN)
        assert list(measure.LADDER) == ["X2", "X12", "X10", "APPROACH", "X20", "PURSUIT", "QUARTERS",
                                        "TELL", "OFFER", "X13", "X16", "X15", "X14"], \
            "the brief's order (OFFER: the session's own find, beside the rows that move no number)"
        assert "OFFER" not in measure.UNSERVED, "a day is opened only where a campaign is served"
        assert measure.down("X14") == [] and len(measure.down("0")) == len(BA4_SEAMS_DOWN)

    def test_the_served_surfaces_hold_the_bar_the_ladder_was_read_at(self):
        """The ladder was read while the game's bar was the great battle's;
        from the final tree the band and the day's sweep hold it there by
        default — arm 0 is the commit before again — and `--key-bar shipped`
        is the game's own."""
        from tools import _ba4_measure as measure
        assert measure.bar_held(measure.LADDER_BAR) == BA4_THE_KEY_BAR
        assert measure.bar_held("shipped") == [] and measure.bar_held("") == []
        assert sorted(measure.down("0") + measure.bar_held(measure.LADDER_BAR)) == sorted(BA4_SESSION_OFF)
        source = (REPO / "tools" / "_ba4_measure.py").read_text(encoding="utf-8")
        assert 'ap.add_argument("--key-bar", default=str(LADDER_BAR),' in source
        assert "held = down(arm) + bar_held(key_bar)" in source, "the day's sweep"
        assert "_flags(down(arm) + held_bar)" in source, "the commanded band"


# ════════════════════════════════════════════════════════════════════════
# The records: the live walk in the real client, the measure, the instruments
# ════════════════════════════════════════════════════════════════════════

AUDITS = REPO / "docs" / "audits"
STAMP = "2026_11_16"


class TestTheLiveWalkOfRecord:
    """Three boards pressed in the REAL client against a sandboxed server
    (`tools/ba4_mode_c_walk.py --export`; `BATTLE_DIORAMA_SPEC.md` §15.20).
    The record is part of the session's commit: a missing board is a failure,
    never a skip."""

    LIVE = AUDITS / "ba4_mode_c_2026_11_16"
    STEPS = {"day": 12, "roads": 6, "oldsave": 6}

    def _run(self, board):
        path = self.LIVE / board / "run.json"
        assert path.is_file(), f"the live walk of the {board} board is not on record"
        return json.loads(path.read_text(encoding="utf-8"))

    @pytest.mark.parametrize("board", sorted(STEPS))
    def test_every_step_of_the_board_held(self, board):
        run = self._run(board)
        walk = run.get("walk") or {}
        assert run.get("engine_exit") == 0 and run.get("script_errors") == []
        assert walk.get("errors") == []
        assert len(walk["results"]) == self.STEPS[board], [r["step"] for r in walk["results"]]
        assert [(r["step"], r["saw"]) for r in walk["results"] if not r.get("ok")] == []

    @pytest.mark.parametrize("board, step, said", [
        # each of these FAILED in the real client before its fix
        ("day", "card_during_the_day", "the road's badge on the map: 'attack · 1 point'"),
        ("day", "first_day_line", "acknowledged to the server=true"),
        ("day", "digit_empty_slot", "words"),
        ("day", "day_closes", "of ours for"),
        ("roads", "approach_card", "the road's badge on the map: 'halts at the approach · 1 AP'"),
        ("roads", "march_cost_card", "on the card=true"),
        # the key bar's wording, seen in the real client: on the real opening
        # Bernadotte against the Archduke John is 74,535 men by the card's own
        # bar (59,535 with the muster committed against a force of 15,000 at
        # the least) — a key battle and no great one
        ("roads", "pitched_card", "on the card=true; 'A great battle' on the card=false"),
        ("oldsave", "old_day_offered", "1 AP"),
        ("oldsave", "old_day_closes", "tally lines told: 0"),
    ])
    def test_the_steps_the_session_owes(self, board, step, said):
        found = [r for r in (self._run(board).get("walk") or {}).get("results", []) if r.get("step") == step]
        assert len(found) == 1, f"step {step} is not on the {board} board's record"
        assert found[0].get("ok") is True and said in found[0].get("saw", ""), found[0].get("saw")

    def test_the_old_save_is_the_one_the_commit_before_wrote(self):
        run = self._run("oldsave")
        assert run["seed"]["save"] == OLD_SAVE.name and run["seed"]["saved_seed"] == "ba4-walk-00"
        assert not (OLD_DAY_COUNT_KEYS & set(run["seed"]["day_keys"]))

    def test_the_parse_check_knows_the_walks(self):
        """BA-2's walk is named in the parse harness; BA-3's was not, and
        BA-4's joined with it: the committed report read both clean."""
        harness = (REPO / "tools" / "godot_parse_check.gd").read_text(encoding="utf-8")
        report = json.loads((REPO / "tools" / "godot_parse_report.json").read_text(encoding="utf-8"))
        rows = {row["path"]: row for row in report["scripts"]}
        for path in ("res://../../tools/ba3_mode_c_walk.gd", "res://../../tools/ba4_mode_c_walk.gd"):
            assert f'"{path}"' in harness, path
            assert rows[path]["parse_ok"] and rows[path]["load_ok"] and not rows[path]["errors"], path


class TestTheMeasureOfRecord:
    """The ONE measure (`tools/_ba4_measure.py`; `BATTLE_DIORAMA_SPEC.md`
    §15.19 the rules, §15.20 the readings), read off the records the chain
    wrote on the frozen backend. Session H reads the deploy gate against
    these files."""

    TOOLS = REPO / "tools"
    UNSERVED = ("0", "X2", "X12", "X10", "APPROACH", "X20", "PURSUIT", "QUARTERS", "TELL", "X14")
    COMMANDED = ("CMD-H", "CMD-A", "CMD-M")

    def _load(self, name):
        path = self.TOOLS / name
        assert path.is_file(), f"{name} is not on record"
        return json.loads(path.read_text(encoding="utf-8"))

    def _band(self, arm):
        cells = self._load(f"_ba4_band_{STAMP}.json")["arms"][arm]
        assert all(cells[n]["ok"] for n in self.COMMANDED), arm
        return [cells[n]["provinces"] for n in self.COMMANDED]

    def _signature(self, arm):
        return self._load(f"_dy_signature_ba4_{arm.lower()}_{STAMP}.json")

    def _census(self, arm):
        return self._load(f"_ba4_{arm.lower()}_census_{STAMP}.json")

    # ── M1: arm 0 reproduces the commit before ───────────────────────────
    def test_m1_the_probe_is_identical_with_every_seam_down(self):
        probe = self._load(f"_ba4_probe_{STAMP}.json")
        for seed in ("jena", "marengo"):
            assert probe["arms"]["0"][seed]["vs_head"] == {"identical": True}, seed
        assert len(probe["arms"]["0"]["seams_down"]) == len(BA4_SEAMS_DOWN)

    def test_m1_the_band_with_every_seam_down_is_the_commit_befores(self):
        assert self._band("0") == [28, 27, 27]
        assert self._band("0") == [self._load(f"_ba4_band_control_{STAMP}.json")["arms"]["HEAD"][n]["provinces"]
                                   for n in self.COMMANDED]

    def test_m1_the_ambient_sweep_and_the_harness_reproduce_the_control(self):
        assert self._signature("0")["seeds"] == self._signature("control")["seeds"]
        assert self._census("0")["seeds"] == self._census("control")["seeds"]
        control = self._load(f"_ba4_chain_d_control_{STAMP}.json")["arms"]["0"]
        assert self._load(f"_ba4_chain_d_{STAMP}.json")["arms"]["0"] == control

    def test_m1_the_days_sweep_reproduces_ba3s_cell_for_cell(self):
        ours, theirs = self._load(f"_ba4_sweep_0_{STAMP}.json"), self._load("_ba3_sweep_2026_11_15.json")
        assert ours["seeds"] == theirs["seeds"] and set(ours["arms"]) == set(theirs["arms"])
        for arm in theirs["arms"]:
            for seed in theirs["seeds"]:
                assert (ours["arms"][arm][seed]["provinces"], ours["arms"][arm][seed]["status"]) == (
                    theirs["arms"][arm][seed]["provinces"], theirs["arms"][arm][seed]["status"]), (arm, seed)

    # ── M2 and M5: attribution ───────────────────────────────────────────
    def test_m5_no_courts_turn_is_lost_on_jena_from_the_fix_on(self):
        probe = self._load(f"_ba4_probe_{STAMP}.json")
        assert probe["arms"]["0"]["jena"]["crashes"] == 1, "the commit before loses Prussia's turn 30"
        for arm in probe["arms"]:
            if arm != "0":
                assert probe["arms"][arm]["jena"]["crashes"] == 0, arm
                assert probe["arms"][arm]["marengo"]["crashes"] == 0, arm
        moved = probe["arms"]["X2"]["jena"]["vs_before"]
        assert moved["identical"] is False and moved["first_turn"] == 30

    def test_m2_the_rows_that_move_no_number_move_none(self):
        """TELL reads as QUARTERS on every surface; OFFER as TELL where a
        campaign is served; and nothing of the day's reaches a campaign nobody
        serves (the shipped arm reads as TELL on the ambient sweep and the
        harness)."""
        assert self._band("TELL") == self._band("QUARTERS") and self._band("OFFER") == self._band("TELL")
        assert self._signature("tell")["seeds"] == self._signature("quarters")["seeds"]
        assert self._census("tell")["seeds"] == self._census("quarters")["seeds"]
        harness = self._load(f"_ba4_chain_d_{STAMP}.json")["arms"]
        assert harness["TELL"] == harness["QUARTERS"] and harness["X14"] == harness["TELL"]
        assert self._signature("x14")["seeds"] == self._signature("tell")["seeds"]
        assert self._census("x14")["seeds"] == self._census("tell")["seeds"]
        probe = self._load(f"_ba4_probe_{STAMP}.json")["arms"]
        for arm in ("TELL", "OFFER", "X13", "X16", "X15", "X14"):
            for seed in ("jena", "marengo"):
                assert probe[arm][seed]["vs_before"] == {"identical": True}, (arm, seed)

    # ── M3: the gate on the shipped tree ─────────────────────────────────
    def test_m3_the_band_stays_inside_23_to_28_on_every_arm(self):
        band = self._load(f"_ba4_band_{STAMP}.json")
        for arm in band["arms"]:
            assert all(23 <= n <= 28 for n in self._band(arm)), (arm, self._band(arm))
        assert self._band("X14") == [27, 28, 27], "the ladder's last arm, read at the bar of 80,000"
        final = self._load(f"_ba4_band_{STAMP}_k50.json")["arms"]["X14"]
        assert final["seams_down"] == [] and all(final[n]["ok"] for n in self.COMMANDED)
        assert [final[n]["provinces"] for n in self.COMMANDED] == [28, 28, 27], \
            "the final tree, at the picked bar: the deploy gate's reading"

    def test_from_the_final_tree_the_ladder_reads_again_with_the_bar_held(self):
        """The ladder was read while the game's bar was 80,000. With the
        picked bar in the game, the measure holds the bar where the ladder
        was read (`--key-bar`, 80,000 by default): arm 0 is the commit before
        again and X14 the ladder's last reading — taken again on the final
        tree, the day the hold was added."""
        hold = self._load(f"_ba4_band_hold_{STAMP}.json")
        assert hold["key_bar"] == "80000" and sorted(hold["arms"]) == ["0", "X14"]
        for arm, want in (("0", [28, 27, 27]), ("X14", [27, 28, 27])):
            cells = hold["arms"][arm]
            assert BA4_THE_KEY_BAR[0] in cells["seams_down"], arm
            assert all(cells[n]["ok"] for n in self.COMMANDED), arm
            assert [cells[n]["provinces"] for n in self.COMMANDED] == want == self._band(arm), arm
        assert sorted(hold["arms"]["0"]["seams_down"]) == sorted(BA4_SESSION_OFF)

    def test_m3_the_gates_clauses_on_the_shipped_ambient_record(self):
        sig, cen = self._signature("x14"), self._census("x14")
        assert sig["story_class_count"] >= 6
        promoted = {s for s, v in sig["seeds"].items() if v["signature"]["rank_promotions"]}
        assert len(promoted) >= 1, "a minor at secondary rank by promotion on at least one seed"
        rosters = {tuple(n for _, n in v["signature"]["eliminations"]) for v in sig["seeds"].values()}
        assert len(rosters) >= 2, "the roster in at least two readings"
        assert cen["totals"]["annexations_outside_aim"] == 0, "the gated line: the AMBIENT record"

    # ── M4: the hand, at the picked bar on the final tree ────────────────
    def test_m4_the_hand_is_healthy_at_the_picked_bar(self):
        """§15.16's rule on `_ba4_sweep_x14_2026_11_16_k50.json`: the silent
        script's mean shift within ±1.5 provinces, no way of playing a day at
        ±3 or beyond on average, none best on six seeds of eight."""
        sweep = self._load(f"_ba4_sweep_x14_{STAMP}_k50.json")
        seeds, arms = sweep["seeds"], sweep["arms"]
        assert len(seeds) == 8 and sweep["held_down"] == []
        assert all(arms[a][s]["ok"] for a in arms for s in seeds)

        def row(arm):
            return [arms[arm][s]["provinces"] for s in seeds]

        hands = ("S", "L", "P", "D", "B", "G", "ALL")
        mean = {a: sum(x - t for x, t in zip(row(a), row("T"))) / len(seeds) for a in hands}
        assert abs(mean["S"]) <= 1.5 and round(mean["S"], 2) == -0.12
        assert all(abs(m) < 3 for m in mean.values()), mean
        best = {a: 0 for a in hands}
        for i in range(len(seeds)):
            top = max(row(a)[i] for a in hands)
            for a in hands:
                best[a] += row(a)[i] == top
        assert max(best.values()) < 6, best
        assert row("S")[:3] == [28, 28, 27], "the silent script on the commanded seeds: the gate's reading"

    def test_the_final_tree_is_the_measured_one_off_the_served_road(self):
        """The key bar, the help, Murat's sentence and the review's fixes
        (§15.21) came after the chain. Off the served road the final tree is
        read three ways against the measured shipped arm
        (`tools/_ba4_sentence_proof.py`): as it is, `marshals` — the sentence
        — and the keys of what the player is TOLD differ (the review's news
        of an assault, a cannonade, a charge abroad); with the old sentence
        put back, what he is told alone; and with those news rows left untold
        as well, NOTHING — no key of the board moved."""
        record = self._load(f"_ba4_final_tree_{STAMP}.json")
        told = ["event_log", "gazette_issues", "pending_dispatch_events"]
        assert record["turns"] == 40 and set(record["seeds"]) == {"jena", "marengo"}
        assert set(told) <= set(record["told"])
        for seed, cell in record["seeds"].items():
            assert cell == {"as_it_is": sorted(told + ["marshals"]), "with_the_old_sentence": told,
                            "and_the_reviews_news_untold": []}, seed
        # the chain's own probe at the picked bar, read before the review
        probe = self._load(f"_ba4_probe_{STAMP}_k50.json")["arms"]["X14"]
        for seed in ("jena", "marengo"):
            assert probe[seed]["crashes"] == 0
            assert probe[seed]["vs_head"]["keys"] == ["marshals"], "against the measured shipped arm"

    def test_after_the_review_the_gates_records_read_the_same(self):
        """The review's fixes are a backend change, so the surfaces a fix
        could touch were read again on the fixed tree (§15.21): the ambient
        sweep's signature and census and the AI-France harness at the shipped
        arm are the records of record, seed for seed; the band is in
        `test_m3…` and `test_from_the_final_tree…` above (their files were
        written again by the same run)."""
        sig, again = self._signature("x14"), self._load(f"_dy_signature_ba4_x14_{STAMP}_review.json")
        assert again["seeds"] == sig["seeds"] and len(again["seeds"]) == 10
        assert again["story_class_count"] == sig["story_class_count"] == 10
        cen, again = self._census("x14"), self._load(f"_ba4_x14_census_{STAMP}_review.json")
        assert again["totals"] == cen["totals"] and again["totals"]["annexations_outside_aim"] == 0
        harness = self._load(f"_ba4_chain_d_{STAMP}.json")["arms"]["X14"]
        again = self._load(f"_ba4_chain_d_{STAMP}_review.json")["arms"]
        assert list(again) == ["X14"] and again["X14"] == harness and len(harness) == 10


class TestTheInstrumentsOfRecord:
    """The day's surfaces as BA-4 left them and the three order cards whose
    words it changed, at the five physical sizes with the Interface Scale each
    derives, at the player's default text size
    (`tools/iq10_run_captures.py --only ba3,ba4 --physical`): twenty-four
    surfaces. BA-3's own records (`ba3_days_points_2026_11_15`) stay as the
    tree BA-3 left."""

    STAMP = "ba4_roads_and_fog_2026_11_16"
    CARDS = ("order_card_ba4_halts", "order_card_ba4_march_cost", "order_card_ba4_word",
             "order_card_ba4_pitched", "order_card_ba4_one_day")

    def _load(self, folder, name):
        path = AUDITS / folder / f"{name}_{self.STAMP}.json"
        assert path.is_file(), path.name
        return json.loads(path.read_text(encoding="utf-8"))

    def test_readability_has_no_red_row(self):
        record = self._load("uxr0", "readability")
        assert len(record["surfaces"]) >= 24 and set(self.CARDS) <= set(record["surfaces"])
        for name, surface in record["surfaces"].items():
            assert len(surface["readings"]) == 5, name
            for size, reading in surface["readings"].items():
                assert reading["counts"]["red"] == 0 and reading["counts"]["p1"] == 0, (name, size)
                assert abs(float(reading["text_size"]) - 1.15) < 1e-9, "shot at the default text size"

    def test_nothing_reads_under_the_contrast_floor(self):
        record = self._load("uxr0", "contrast")
        for name, surface in record["surfaces"].items():
            for size, reading in surface["readings"].items():
                assert reading["counts"]["under"] == 0, (name, size, reading["under"][:1])

    def test_every_surface_fits_at_every_size(self):
        record = self._load("uxr3", "fit")
        assert set(self.CARDS) <= set(record["surfaces"])
        for name, surface in record["surfaces"].items():
            assert set(surface["readings"]) == {"1920x1080", "3840x2160", "5120x1440"}, name
            for size, reading in surface["readings"].items():
                assert reading["ok"], (name, size)
                for key in ("errors", "clipped_text", "truncated_text", "buttons_offscreen", "text_offscreen"):
                    assert reading[key] == [], (name, size, key)

    def test_no_frame_has_a_cut_line_or_an_overlap(self):
        record = self._load("uxr3", "frame_census")
        assert record["frames"] >= 120 and record["frames_without_record"] == []
        assert record["cut_lines"] == [] and record["grip_overlaps"] == [] and record["tick_overlaps"] == []
        assert record["map_overlaps"] == []


class TestTheRecordsSayWhatLanded:
    """BA2-X19's sibling for this session: `STATUS.md` ▶ NEXT UP is read
    first, every session — its head names BA-4 as landed and the deploy as
    next — and the ledger holds the rows as they stand."""

    def test_the_head_of_status_names_the_session_as_landed(self):
        from tests._ledgers import doc_text
        head = next(line for line in doc_text("STATUS.md").splitlines()
                    if line.startswith("> **▶ NEXT ="))
        assert "next BA-4 the roads and the fog" not in head
        assert "ROW BA, BA-4 ✅ LANDED November 16, 2026" in head and "next session H, the deploy" in head

    def test_the_ledger_holds_the_rows(self):
        from tests._ledgers import doc_text
        ledger = doc_text("BUG_FIXES.md")
        rows = dict(re.findall(r"^\| \*\*(BA\d-X\d+)\*\* \| P\d \| (✅ FIXED|OPEN) ", ledger, flags=re.M))
        still_open = sorted(name for name, state in rows.items() if state == "OPEN")
        assert not [name for name in still_open if name.startswith("BA4-")], "none of BA-4's"
        # (row BA, BA-5 closed BA1-X8 and filed three older rows for Session H's head)
        assert still_open == ["BA1-X4", "BA2-X16", "BA2-X6", "BA5-X15", "BA5-X16", "BA5-X17"], "Session H's"
        assert rows["BA4-X1"] == rows["BA4-X2"] == "✅ FIXED"
        for name in ("BA2-X2", "BA2-X7", "BA2-X10", "BA2-X12", "BA2-X20", "BA2-X21",
                     "BA3-X2", "BA3-X5", "BA3-X13", "BA3-X14", "BA3-X15", "BA3-X16"):
            assert rows[name] == "✅ FIXED", name

    def test_the_brief_for_the_deploy_reads_the_gate_against_this_sessions_records(self):
        brief = (REPO / "docs" / "NEXT_SESSION_PROMPT.md").read_text(encoding="utf-8")
        assert brief.startswith("# NEXT SESSION PROMPT — Session H")
        # (row BA, BA-5 re-took every one of these surfaces on its final tree, and the brief now
        # reads the gate against those records: BA-4's stand as the game before the finish)
        for name in ("_ba5_band_2026_11_17.json", "_dy_signature_ba5_all_2026_11_17.json",
                     "_ba5_all_census_2026_11_17.json", "_ba5_chain_d_2026_11_17.json"):
            assert name in brief, name
        for name in (f"_ba4_band_{STAMP}.json", f"_dy_signature_ba4_x14_{STAMP}.json",
                     f"_ba4_x14_census_{STAMP}.json", f"_ba4_chain_d_{STAMP}.json"):
            assert (REPO / "tools" / name).is_file(), name
