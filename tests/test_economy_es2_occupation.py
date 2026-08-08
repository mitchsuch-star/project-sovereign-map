"""ES-2 stability-tier occupation cost — S6 (Track 2, spec §0.6.7 amendment 2).

Blessed shape (EC-2 gate, July 9, 2026): every controlled province NOT in the
nation's `nation_starting_regions` pays a per-turn occupation cost = stability-
tier fraction × the region's BASE `income_value` — Hostile 0.50 / Unrest 0.35 /
Settling 0.20 / Stable 0.10 permanent floor. ZERO new serialized fields: the
homeland substrate (`nation_starting_regions`) and the stability ramp already
exist, so recapture-reset is free (recapture drops stability) and marshal
pacification is free (the existing +10 garrisoned stability growth). E6:
bankruptcy mercy halves the occupation total. Constants are OCCUPATION_* by
gate mandate (never "garrison" — that name belongs to real garrison mechanics).

EUROPE-SCOPED: the legacy 19-region world is a pinned test fixture and pays no
occupation (the N1 pattern, matching ES-3's flat legacy rate).

Threading pins: `income` stays GROSS everywhere; occupation rides a separate
signed component through process_income_phase (GR5 — AI pays the same seam),
the ledger "Occupation" line (+ NET_GOLD_COMPONENTS extension forcing the .gd
render by construction), the dispatch situation, the treasury report, and both
turn-end financial messages.

The E1 band assertion (France absorbs ~55–70% of TOTAL net with ES-2+ES-3+ES-7
stacked) lands with S7's stacked two-sided band test — the Track-2 acceptance.
At boot occupation is 0 for every nation by construction (nation_starting_regions
IS starting control), so this slice's anchors are conquest-shaped, not turn-1.

Amendment-4 rider: the estate (dotation) exemption from occupation lands with
S7 ES-7, where `Marshal.dotation_regions` is introduced.
"""

from pathlib import Path

import pytest

from backend.commands.executor import CommandExecutor
from backend.game_logic.dispatch import _build_situation
from backend.game_logic.ledger import _build_economy
from backend.models.region import (
    OCCUPATION_HOSTILE_FRACTION,
    OCCUPATION_SETTLING_FRACTION,
    OCCUPATION_STABLE_FRACTION,
    OCCUPATION_UNREST_FRACTION,
)
from backend.models.world_state import WorldState

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
)

_LEDGER_GD = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "scripts" / "strategic_ledger.gd"
)


@pytest.fixture
def europe():
    """Bare Europe flag world (126 provinces, no marshals)."""
    return WorldState(player_nation="France", sovereign_map="europe")


@pytest.fixture
def legacy():
    return WorldState(player_nation="France")


@pytest.fixture(scope="module")
def world1805():
    """Read-only module-scoped 1805 campaign — mutating tests copy it."""
    return WorldState.from_scenario(str(SCENARIO_PATH))


def _copy(world):
    return WorldState.from_dict(world.to_dict())


def _conquer(world, nation="France", stability=10):
    """Flip one foreign region to `nation` and return it (cache invalidated).

    Prefers a non-capital region whose owner fields no marshals, so tests
    that run a full end-turn can't have the conquest retaken (or provoke
    capital-shaped reactions) during the enemy phase.
    """
    armed = {m.nation for m in world.marshals.values() if m.strength > 0}
    homeland = set(world.nation_starting_regions.get(nation, []))

    def eligible(region, safe):
        if not region.controller or region.controller == nation:
            return False
        if region.name in homeland:
            return False
        if safe and (region.is_capital or region.controller in armed):
            return False
        return True

    for safe in (True, False):
        for region in world.regions.values():
            if eligible(region, safe):
                region.controller = nation
                region.stability = stability
                world.invalidate_active_nations_cache()
                return region
    raise AssertionError("no conquerable region found")


# ══════════════════════ tier fractions (region-level) ══════════════════════


class TestOccupationFractions:
    @pytest.mark.parametrize("stability,fraction", [
        (0, OCCUPATION_HOSTILE_FRACTION),
        (10, OCCUPATION_HOSTILE_FRACTION),
        (25, OCCUPATION_HOSTILE_FRACTION),    # boundary falls into LOWER tier
        (26, OCCUPATION_UNREST_FRACTION),
        (50, OCCUPATION_UNREST_FRACTION),
        (51, OCCUPATION_SETTLING_FRACTION),
        (75, OCCUPATION_SETTLING_FRACTION),
        (76, OCCUPATION_STABLE_FRACTION),
        (100, OCCUPATION_STABLE_FRACTION),
    ])
    def test_tier_mapping_matches_stability_boundaries(self, europe, stability, fraction):
        region = next(iter(europe.regions.values()))
        region.stability = stability
        assert region.get_occupation_fraction() == fraction

    def test_blessed_fractions(self):
        """The §0.6.7 blessed starting fractions — a conscious re-pin is a
        band retune, allowed without a new gate; a SHAPE change is not."""
        assert OCCUPATION_HOSTILE_FRACTION == 0.50
        assert OCCUPATION_UNREST_FRACTION == 0.35
        assert OCCUPATION_SETTLING_FRACTION == 0.20
        assert OCCUPATION_STABLE_FRACTION == 0.10

    def test_cost_is_fraction_of_base_income_not_effective(self, europe):
        """Hostile soil yields ZERO effective income but still costs 50% of
        BASE — the 'digest before you bite' shape: fresh conquest is
        genuinely net-negative until pacified."""
        region = _conquer(europe, stability=10)
        assert region.get_effective_income() == 0
        income_data = europe.calculate_turn_income("France")
        expected = int(region.income_value * OCCUPATION_HOSTILE_FRACTION)
        assert income_data["occupation"] == expected
        assert expected > 0


# ═══════════════════════ homeland exemption ═══════════════════════


class TestHomelandExemption:
    def test_no_nation_pays_occupation_at_boot(self, world1805):
        """Two-sided boot anchor: nation_starting_regions IS starting control,
        so occupation is structurally 0 for every nation at campaign start."""
        for nation in world1805.get_active_nations():
            assert world1805.calculate_turn_income(nation)["occupation"] == 0

    def test_conquered_province_pays(self, europe):
        region = _conquer(europe, stability=10)
        income_data = europe.calculate_turn_income("France")
        assert income_data["occupation"] == int(
            region.income_value * OCCUPATION_HOSTILE_FRACTION)

    def test_recaptured_homeland_pays_nothing(self, europe):
        """A starting province lost and retaken is homeland, not occupation —
        even at rock-bottom stability."""
        home_name = europe.nation_starting_regions["France"][0]
        home = europe.regions[home_name]
        home.controller = "Austria"
        europe.invalidate_active_nations_cache()
        home.controller = "France"
        home.stability = 10
        europe.invalidate_active_nations_cache()
        assert europe.calculate_turn_income("France")["occupation"] == 0

    def test_income_stays_gross(self, europe):
        """The `income` figure never absorbs the cost — occupation is its own
        signed component (the ledger renders both; SC-33 both-halves)."""
        before = europe.calculate_turn_income("France")["income"]
        region = _conquer(europe, stability=100)  # Stable: full income, 10% cost
        data = europe.calculate_turn_income("France")
        assert data["income"] == before + region.get_effective_income()
        assert data["occupation"] == int(
            region.income_value * OCCUPATION_STABLE_FRACTION)


# ═══════════════ tier ramp / recapture / permanent floor ═══════════════


class TestTierRampAndFloor:
    def test_cost_declines_as_stability_grows(self, europe):
        region = _conquer(europe, stability=10)
        costs = []
        for stability in (10, 40, 60, 100):
            region.stability = stability
            costs.append(europe.calculate_turn_income("France")["occupation"])
        assert costs == sorted(costs, reverse=True)
        assert costs[0] > costs[-1]

    def test_stable_conquest_keeps_permanent_floor(self, europe):
        """Occupation never reaches zero on non-homeland soil — fully
        pacified conquests still pay the 10% floor forever."""
        region = _conquer(europe, stability=100)
        assert europe.calculate_turn_income("France")["occupation"] == int(
            region.income_value * OCCUPATION_STABLE_FRACTION) > 0

    def test_recapture_reset_is_free_via_stability(self, europe):
        """Recapture drops stability (combat sets 10/25 on capture), which
        alone re-raises the tier — no new serialized field needed."""
        region = _conquer(europe, stability=100)
        floor_cost = europe.calculate_turn_income("France")["occupation"]
        region.stability = 10  # what a recapture does
        assert europe.calculate_turn_income("France")["occupation"] == int(
            region.income_value * OCCUPATION_HOSTILE_FRACTION) > floor_cost

    def test_plundered_region_lingers_in_high_tiers(self, europe):
        """Plunder finally has a recurring price: it crushes stability, so the
        province sits in the expensive tiers longer (§0.6.7 rationale)."""
        region = _conquer(europe, stability=60)
        settling = europe.calculate_turn_income("France")["occupation"]
        region.stability = max(0, region.stability - 40)  # plunder-shaped hit
        assert europe.calculate_turn_income("France")["occupation"] > settling


# ═══════════════════ vassal no-double-charge (guard) ═══════════════════


class TestVassalNoDoubleCharge:
    def test_vassal_soil_is_not_lord_occupation(self, europe):
        """ES-2 vs tribute are disjoint by construction: get_nation_regions
        keys on controller, so soil handed to a vassal leaves the lord's
        occupation ledger entirely (vassal income is already tribute-skimmed)."""
        region = _conquer(europe, stability=10)
        with_occupation = europe.calculate_turn_income("France")["occupation"]
        assert with_occupation > 0
        region.controller = "Bavaria"  # vassalize the conquest
        europe.invalidate_active_nations_cache()
        assert europe.calculate_turn_income("France")["occupation"] == 0
        # ...and the cost lands on the vassal's own ledger instead (it is
        # non-homeland for Bavaria too), never charged twice to the lord.
        assert europe.calculate_turn_income("Bavaria")["occupation"] > 0


# ══════════════════════ E6 — bankruptcy mercy ══════════════════════


class TestBankruptcyMercy:
    def test_mercy_halves_occupation(self, europe):
        _conquer(europe, stability=10)
        full = europe.calculate_turn_income("France")["occupation"]
        europe.nation_bankruptcy_turns["France"] = 1
        merciful = europe.calculate_turn_income("France")
        assert merciful["occupation"] == full // 2
        assert merciful["occupation_halved"] is True

    def test_no_mercy_when_solvent(self, europe):
        _conquer(europe, stability=10)
        data = europe.calculate_turn_income("France")
        assert data["occupation_halved"] is False


# ══════════════════ legacy fixture world unchanged ══════════════════


class TestLegacyUnchanged:
    def test_legacy_conquest_pays_no_occupation(self, legacy):
        _conquer(legacy, stability=10)
        data = legacy.calculate_turn_income("France")
        assert data["occupation"] == 0

    def test_legacy_income_phase_net_formula_unmoved(self, legacy):
        income = legacy.calculate_turn_income("France")["income"]
        upkeep = legacy.calculate_turn_upkeep("France")["total"]
        admin = legacy._calculate_admin_bonus("France")
        result = legacy.process_income_phase("France")
        assert result["net"] == income - upkeep + admin


# ═══════════════ threading — ledger / dispatch / reports ═══════════════


class TestThreading:
    def test_income_phase_subtracts_occupation(self, europe):
        region = _conquer(europe, stability=100)
        gold_before = europe.nation_gold["France"]
        result = europe.process_income_phase("France")
        expected_occ = int(region.income_value * OCCUPATION_STABLE_FRACTION)
        assert result["occupation"] == expected_occ
        assert "occupation" in result["message"]
        assert europe.nation_gold["France"] == gold_before + result["net"]
        assert result["net"] == (result["income"] - result["occupation"]
                                 - result["upkeep"] + result["admin_bonus"])

    def test_ai_nations_pay_through_the_same_seam(self, europe):
        """GR5: a minor AI pays occupation through the identical
        process_income_phase seam — zero AI-only code."""
        _conquer(europe, nation="Bavaria", stability=10)
        occ = europe.calculate_turn_income("Bavaria")["occupation"]
        assert occ > 0
        gold_before = europe.nation_gold.get("Bavaria", 0)
        result = europe.process_income_phase("Bavaria")
        assert result["occupation"] == occ
        assert europe.nation_gold["Bavaria"] == gold_before + result["net"]

    def test_ledger_renders_occupation_and_reconciles(self, europe):
        _conquer(europe, stability=10)
        econ = _build_economy(europe, "France")
        assert econ["occupation"] > 0
        signed_sum = (
            econ["income"] + econ["trade_income"] + econ["admin_bonus"]
            + econ["treaty_gold"] + econ["vassal_tribute"]
            + econ["settlement_gold"] - econ["occupation"]
            - econ["upkeep_base"] - econ["upkeep_surcharge"]
        )
        assert signed_sum == econ["net"]

    def test_ledger_gd_renders_occupation_line(self):
        src = _LEDGER_GD.read_text(encoding="utf-8")
        assert '"occupation"' in src
        assert "Occupation" in src

    def test_dispatch_situation_carries_occupation(self, europe):
        region = _conquer(europe, stability=100)
        situation = _build_situation(europe, "France")
        expected = int(region.income_value * OCCUPATION_STABLE_FRACTION)
        assert situation["occupation"] == expected
        # EB review [5] re-pin (Aug 7 2026): the dispatch delta stopped
        # being hand-assembled (it omitted vassal tribute / admin bonus /
        # treaty + settlement gold — the CA8-10 class) and now reads the
        # ledger's reconciled net, whose own guard pins net == the signed
        # component sum. The occupation term still moves it (asserted via
        # the component key above and the ledger identity here).
        from backend.game_logic.ledger import _build_economy
        assert situation["treasury_delta"] == int(
            _build_economy(europe, "France")["net"])

    def test_treasury_report_shows_occupation_lines(self, world1805):
        world = _copy(world1805)
        region = _conquer(world, stability=10)
        executor = CommandExecutor()
        result = executor.execute(
            {"command": {"action": "economy"}}, {"world": world}
        )
        assert result["success"] is True
        assert "Occupation:" in result["message"]
        assert region.name in result["message"]

    def test_end_turn_message_annotates_occupation(self, world1805):
        world = _copy(world1805)
        _conquer(world, stability=10)
        executor = CommandExecutor()
        result = executor.execute(
            {"command": {"action": "end_turn"}}, {"world": world}
        )
        assert "Occupation:" in result.get("message", "")

    def test_turn_end_event_carries_occupation_int(self, world1805):
        world = _copy(world1805)
        region = _conquer(world, stability=10)
        executor = CommandExecutor()
        result = executor.execute(
            {"command": {"action": "end_turn"}}, {"world": world}
        )
        turn_end = next(e for e in result["events"] if e.get("type") == "turn_end")
        assert isinstance(turn_end["occupation"], int)
        # stability grew during end-turn processing — re-derive from the
        # post-advance state the executor itself read
        assert region.controller == "France"
        assert turn_end["occupation"] == (
            world.calculate_turn_income("France")["occupation"])
        assert turn_end["occupation"] > 0
