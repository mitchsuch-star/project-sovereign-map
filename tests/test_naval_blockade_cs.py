"""NV-1 — The Blockade War (docs/NAVAL_SPEC.md §11).

The untargeted blockade predicate (v1.0.3 — the simultaneous watch), the
trade ×0.5 "Blockade" component threaded the full EC-U2 recipe, the
trade_dominance absorption of the Britain naval_income literal (both sites),
the island WE clause, CS 2.0 closure + tiers, and the state-change beats.

Boot deltas (§7, conscious + MEASURED): France −175 trade − 90 upkeep
≈ −265/turn — re-blessed at NV-1 with the E1-family discipline.
"""

from pathlib import Path

import pytest

from backend.game_logic import naval
from backend.game_logic.diplomacy import (
    calculate_trade_income,
    process_trade_income,
)
from backend.models.world_state import WorldState

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)


@pytest.fixture
def world():
    return WorldState.from_scenario(str(SCENARIO_PATH))


# ═══════════════════════════════════════════════════════════════════════════
# THE PREDICATE (§4.2 / §3.3 — untargeted, per-target ratio)
# ═══════════════════════════════════════════════════════════════════════════

class TestBlockadePredicate:
    def test_boot_blockade_pins_france_and_spain(self, world):
        """v1.0.3: Britain's ONE blockade posture covers EVERY at-war
        enemy — the hole where Spain drilled to 100 unmolested is closed."""
        assert naval.is_blockaded(world, "France")
        assert naval.is_blockaded(world, "Spain")
        assert naval.is_blockaded(world, "Holland")

    def test_the_blockader_is_never_blockaded_at_boot(self, world):
        assert not naval.is_blockaded(world, "Britain")

    def test_a_court_with_no_navies_row_cannot_be_blockaded(self, world):
        # Bavaria has no entry — landlocked courts are out of naval reach
        # (recorded NV-1 ruling).
        world.diplomatic_states[world._make_diplo_key("Britain", "Bavaria")] = "WAR"
        world.invalidate_active_nations_cache()
        assert not naval.is_blockaded(world, "Bavaria")

    def test_peace_lifts_the_blockade(self, world):
        world.diplomatic_states[world._make_diplo_key("Britain", "France")] = "PEACE"
        world.invalidate_active_nations_cache()
        assert not naval.is_blockaded(world, "France")

    def test_guard_posture_blockades_nobody(self, world):
        world.fleets["Britain"]["posture"] = "guard"
        assert naval.blockaded_nations(world) == []

    def test_the_ratio_gate_is_honest(self, world):
        """A fleet below 1.25× pins nothing."""
        world.fleets["Britain"]["ships"] = 30  # 30 eff vs France 31.5
        assert not naval.is_blockaded(world, "France")


# ═══════════════════════════════════════════════════════════════════════════
# TRADE ×0.5 — the "Blockade" component (the EC-W1 gross-plus-suspension
# pattern: chokepoint stays gross, the loss is its own signed line)
# ═══════════════════════════════════════════════════════════════════════════

class TestBlockadeTradeComponent:
    def test_the_measured_boot_loss(self, world):
        losses = naval.blockade_trade_loss(world)
        assert losses.get("France") == 175  # the §13.2 measured −175
        assert losses.get("Spain", 0) > 0
        assert "Britain" not in losses

    def test_chokepoint_stays_gross(self, world):
        """calculate_trade_income keeps returning the full figure — every
        existing trade pin survives byte-identically."""
        gross = calculate_trade_income(world)
        assert gross["France"] == 350

    def test_applied_gold_is_gross_minus_loss(self, world):
        gold0 = world.nation_gold.get("France", 0)
        applied = process_trade_income(world)
        assert applied["France"] == 350 - 175
        assert world.nation_gold["France"] == gold0 + 175

    def test_ledger_carries_the_component(self, world):
        from backend.game_logic.ledger import _build_economy
        econ = _build_economy(world, "France")
        assert econ["blockade"] == 175
        assert econ["trade_income"] == 350  # gross shown
        # net reconciliation is guarded suite-wide by
        # test_economy_ledger_reconciliation.py (NET_GOLD_COMPONENTS).

    def test_dispatch_carries_the_component(self, world):
        from backend.game_logic.dispatch import build_morning_dispatch
        dispatch = build_morning_dispatch(world)
        situation = dispatch.get("situation") or {}
        assert situation.get("blockade") == 175
        assert situation.get("admiralty") == 90

    def test_fleetless_world_pays_nothing(self):
        legacy = WorldState(player_nation="France")
        assert naval.blockade_trade_loss(legacy) == {}


# ═══════════════════════════════════════════════════════════════════════════
# TRADE DOMINANCE (§4.2/§5.1 — the naval_income absorption, both sites)
# ═══════════════════════════════════════════════════════════════════════════

class TestTradeDominance:
    def test_boot_scaling_by_closure(self, world):
        """300 × (1 − 0.385) = 184 — the System squeezes from turn one."""
        assert naval.trade_dominance_income(world, "Britain") == 184
        income = world.calculate_turn_income("Britain")
        assert income["breakdown"]["naval_income"] == 184

    def test_suspended_entirely_under_blockade(self, world):
        world.fleets["France"]["posture"] = "blockade"
        world.fleets["France"]["ships"] = 200
        world.fleets["France"]["readiness"] = 100
        assert naval.is_blockaded(world, "Britain")
        assert naval.trade_dominance_income(world, "Britain") == 0

    def test_the_smugglers_floor(self, world):
        """×0.4 floor — the System leaked, historically and here."""
        # Close everything: every continental port counted.
        for nation in list(world.fleets):
            if nation == naval.META_KEY or nation == "Britain":
                continue
            key = world._make_diplo_key("Britain", nation)
            world.diplomatic_states[key] = "WAR"
        world.invalidate_active_nations_cache()
        assert naval.closure_against(world, "Britain") == 1.0
        assert naval.trade_dominance_income(world, "Britain") == 120  # 300×0.4

    def test_power_score_absorbed_static(self, world):
        """The td arm is STATIC — closure never feeds coalition math
        (recorded NV-1 decision)."""
        from backend.game_logic.diplomacy import calculate_national_power
        power_boot = calculate_national_power("Britain", world)
        # Drive closure to the maximum: the power score must not move.
        for nation in list(world.fleets):
            if nation in (naval.META_KEY, "Britain"):
                continue
            key = world._make_diplo_key("Britain", nation)
            world.diplomatic_states[key] = "WAR"
        world.invalidate_active_nations_cache()
        # Bust the per-turn power cache so the assertion is not vacuous.
        if hasattr(world, "_national_power_cache"):
            world._national_power_cache = {}
        assert calculate_national_power("Britain", world) == power_boot


# ═══════════════════════════════════════════════════════════════════════════
# CS 2.0 (§5.1 — closure, tiers, the compounding WE)
# ═══════════════════════════════════════════════════════════════════════════

class TestClosure:
    def test_the_boot_fact(self, world):
        """France 4 + Spain 3 + Holland 2 + KingdomOfItaly 1 = 10 of 26
        ≈ 38% — one diplomatic move short of the first WE tier."""
        closure = naval.closure_against(world, "Britain")
        assert closure == pytest.approx(10 / 26)
        assert naval.cs_closure_tier(closure) == 0

    def test_tiers(self):
        assert naval.cs_closure_tier(0.39) == 0
        assert naval.cs_closure_tier(0.40) == 1
        assert naval.cs_closure_tier(0.60) == 2
        assert naval.cs_closure_tier(0.80) == 3

    def test_one_diplomatic_move_crosses_the_first_tier(self, world):
        """Portugal (2 ports) at war with Britain → 12/26 ≈ 46% → tier 1."""
        world.diplomatic_states[world._make_diplo_key("Britain", "Portugal")] = "WAR"
        world.invalidate_active_nations_cache()
        closure = naval.closure_against(world, "Britain")
        assert naval.cs_closure_tier(closure) == 1

    def test_cs_members_count_toward_closure(self, world):
        world.continental_system_members = ["Denmark"]
        closure = naval.closure_against(world, "Britain")
        assert closure == pytest.approx(12 / 26)


class TestWarWearinessCoupling:
    def test_island_clause_bleeds_the_blockaded_islander(self, world):
        """H5: +2/turn applies ONLY to a blockaded `island: true` nation —
        continental economies were import-resilient."""
        world.fleets["France"]["posture"] = "blockade"
        world.fleets["France"]["ships"] = 200
        world.fleets["France"]["readiness"] = 100
        we0 = world.war_exhaustion.get("Britain", 0)
        fr0 = world.war_exhaustion.get("France", 0)
        naval.process_naval_turn(world)
        assert world.war_exhaustion.get("Britain", 0) == we0 + naval.ISLAND_BLOCKADE_WE
        # France is ALSO blockaded (mutual) but is not an island: untouched
        # by the island clause (the naval tick adds it nothing).
        assert world.war_exhaustion.get("France", 0) == fr0

    def test_cs_tier_weariness_ticks(self, world):
        world.diplomatic_states[world._make_diplo_key("Britain", "Portugal")] = "WAR"
        world.invalidate_active_nations_cache()
        we0 = world.war_exhaustion.get("Britain", 0)
        naval.process_naval_turn(world)
        assert world.war_exhaustion.get("Britain", 0) >= we0 + 1

    def test_a2_arithmetic_the_strangulation_path(self, world):
        """A2 (arithmetic arm): ≥80% closure + blockade + the standing
        at-war tick caps Britain's WE within 12 turns from the boot 60 —
        the sue-for-peace threshold machinery does the rest
        (effective_peace_threshold rises with WE//20)."""
        world.war_exhaustion["Britain"] = 60
        per_turn = 8 + 3 + naval.ISLAND_BLOCKADE_WE  # war tick + tier 3 + island
        turns_to_cap = -(-(200 - 60) // per_turn)
        assert turns_to_cap <= 12

    def test_cs_tier_shift_beat_fires_once_per_change(self, world):
        world.fleets[naval.META_KEY] = {"cs_tier": 0, "blockaded": [],
                                        "verdicts": {}}
        world.diplomatic_states[world._make_diplo_key("Britain", "Portugal")] = "WAR"
        world.invalidate_active_nations_cache()
        naval.process_naval_turn(world)
        shifts = [e for e in world.event_log if e.get("type") == "cs_tier_shift"]
        assert len(shifts) == 1
        naval.process_naval_turn(world)
        shifts = [e for e in world.event_log if e.get("type") == "cs_tier_shift"]
        assert len(shifts) == 1  # state-change only, never per-turn


# ═══════════════════════════════════════════════════════════════════════════
# THE BEATS (§9 — state-change only)
# ═══════════════════════════════════════════════════════════════════════════

class TestBlockadeBeats:
    def test_blockade_begins_fires_on_the_transition(self, world):
        naval.process_naval_turn(world)  # establishes the baseline
        begins = [e for e in world.event_log
                  if e.get("type") == "blockade_begins"]
        count0 = len(begins)
        naval.process_naval_turn(world)  # no change: no new beat
        begins = [e for e in world.event_log
                  if e.get("type") == "blockade_begins"]
        assert len(begins) == count0

    def test_blockade_broken_fires_when_the_pressure_lifts(self, world):
        naval.process_naval_turn(world)
        # Peace with Britain ends the war — the blockade lifts.
        for nation in ("France", "Spain", "Holland"):
            world.diplomatic_states[world._make_diplo_key("Britain", nation)] = "PEACE"
        world.invalidate_active_nations_cache()
        naval.process_naval_turn(world)
        broken = [e for e in world.event_log
                  if e.get("type") == "blockade_broken"]
        assert {e["nation"] for e in broken} >= {"France", "Spain"}


# ═══════════════════════════════════════════════════════════════════════════
# THE BOOT DELTA (§7 — conscious, measured, re-blessed HERE)
# ═══════════════════════════════════════════════════════════════════════════

class TestBootDelta:
    def test_france_boot_delta_is_the_blessed_minus_265(self, world):
        """−175 trade − 90 Admiralty ≈ −265/turn ≈ 12.6% of the measured
        +2,107 pre-naval net (spec §13.2). The E1 band file re-blesses the
        absorption window; this pins the DELTA's two halves exactly."""
        assert naval.blockade_trade_loss(world).get("France") == 175
        assert naval.ship_upkeep(world, "France") == 90

    def test_every_fleet_nation_stays_boot_solvent(self, world):
        """The E1-family discipline extended to the naval bill: income +
        gross trade − upkeep − Admiralty − blockade loss stays positive for
        every fleet-holding nation at boot (Naples' 5 sail must not sink
        Naples)."""
        from backend.models.world_state import WorldState as _WS  # noqa: F401
        trade = calculate_trade_income(world)
        losses = naval.blockade_trade_loss(world)
        for nation, _rec in naval.iter_fleets(world):
            income = world.calculate_turn_income(nation)
            upkeep = world.calculate_turn_upkeep(nation)
            net = (income["income"] + trade.get(nation, 0)
                   - losses.get(nation, 0)
                   - upkeep["total"] - income["admiralty"]
                   - income["occupation"] - income["contributions"]
                   - income["war_effort"])
            assert net > 0, f"{nation} goes under at boot: {net}"
