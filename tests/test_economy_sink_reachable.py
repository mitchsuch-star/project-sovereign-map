"""EC-U2 — a gold sink reachable without conquest (Combat Overhaul Phase 4).

The Field Review's second economy finding: every recurring gold sink was
conquest-gated (occupation cost, dotation skim read 0 for a homeland-holding
France), so a homeland-only France banked its ~+3,000/turn surplus with
nothing to spend it on — treasury 800 -> 15,058 unspent.

EC-U2 adds `EUROPE_INFRASTRUCTURE_UPKEEP` per-turn maintenance for every built
structure (depots, fortifications, training grounds, markets, stables, and
active/damaged watchtowers) a nation keeps. It is reachable at home — build in
your own capital, no conquest needed — so the banked surplus becomes a
decision (invest in infrastructure and carry the bill, or hoard). Era note: a
Napoleonic state paid to garrison and maintain its fortress and depot network
whether or not it was expanding.

Boot-safe: the 1805 scenario authors no buildings, so infrastructure is 0 at
turn 1 for every nation — it cannot break the E1 boot-solvency band (Austria
+18). Europe-scoped (N1: the legacy fixture world pays none). Symmetric player
/ AI through the same per-nation income seam (GR5).

EB-3 (Econ Balance gate Aug 7 2026, ECON_BALANCE_GATE_2026_08_07.md §3):
CONSCIOUS RE-BLESS of the flat 40 — the rate is now TIER-scaled
(capital 40 / major_city 30 / city 20; towns and rural bill 20 for their
watchtowers), because the flat rate made a market on the modal buildable
tier a permanent −3/turn (CA8-D1). And a RUIN BILLS NOTHING: damaged
buildings and damaged watchtowers are exempt until repaired (the IGR-X9
decision — razing no longer strictly dominates securing a built province).
The per-tier rates below derive from `infrastructure_upkeep_rate`, the
single source the income loop bills through.
"""

from pathlib import Path

import pytest

from backend.game_logic.ledger import _build_economy
from backend.models.world_state import (
    WorldState, EUROPE_INFRASTRUCTURE_UPKEEP, EUROPE_INFRASTRUCTURE_UPKEEP_BY_TIER,
    infrastructure_upkeep_rate,
)

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)

RATE = EUROPE_INFRASTRUCTURE_UPKEEP


@pytest.fixture
def world():
    return WorldState.from_scenario(str(SCENARIO_PATH))


def _homeland_region(world, nation):
    return world.regions[world.nation_starting_regions[nation][0]]


class TestBootSafe:
    def test_no_nation_pays_infrastructure_at_boot(self, world):
        for nation in world.get_active_nations():
            inc = world.calculate_turn_income(nation)
            assert inc["infrastructure"] == 0, (
                f"{nation} pays infrastructure at boot — the scenario should "
                "author no buildings, so the E1 boot band is unaffected")


class TestReachableWithoutConquest:
    def test_homeland_build_creates_a_recurring_sink(self, world):
        nation = "France"
        # homeland only — no conquered/occupied province anywhere
        region = _homeland_region(world, nation)
        assert region.name in world.nation_starting_regions[nation]

        inc_before = world.calculate_turn_income(nation)
        region.buildings.append({"type": "fortification", "damaged": False})
        inc_after = world.calculate_turn_income(nation)

        assert inc_before["infrastructure"] == 0
        # EB-3: the bill is the REGION-TIER rate (single source)
        assert inc_after["infrastructure"] == infrastructure_upkeep_rate(region)
        # income stays GROSS — the cost rides its own signed component
        assert inc_after["income"] == inc_before["income"]

    def test_cost_scales_with_structures(self, world):
        nation = "France"
        region = _homeland_region(world, nation)
        region.buildings.append({"type": "fortification"})
        region.buildings.append({"type": "supply_depot"})
        region.watchtower = "active"
        inc = world.calculate_turn_income(nation)
        assert inc["infrastructure"] == 3 * infrastructure_upkeep_rate(region)

    def test_net_drops_by_the_maintenance(self, world):
        nation = "France"

        def net_of():
            return _build_economy(world, nation)["net"]

        # a fortification carries maintenance but no income bonus (unlike a
        # market), so the net delta is exactly the maintenance cost
        net_before = net_of()
        region = _homeland_region(world, nation)
        region.buildings.append({"type": "fortification"})
        assert net_of() == net_before - infrastructure_upkeep_rate(region)

    def test_meaningful_decision_by_turn_five(self, world):
        """A homeland France that invests its surplus in infrastructure over
        the first turns carries a real, non-trivial recurring bill — the sink
        the review said was missing. (EB-3: the bar drops with the tier-scaled
        rates — 12 structures at the lightest tier is still 240g/turn.)"""
        nation = "France"
        homeland = world.nation_starting_regions[nation]
        built = 0
        expected = 0
        for name in homeland:
            region = world.regions[name]
            # two structures per region, mirroring the max build slots
            region.buildings.append({"type": "fortification"})
            region.buildings.append({"type": "supply_depot"})
            built += 2
            expected += 2 * infrastructure_upkeep_rate(region)
            if built >= 12:
                break
        inc = world.calculate_turn_income(nation)
        assert inc["infrastructure"] == expected
        assert inc["infrastructure"] >= 240   # a decision, not a rounding error


class TestEB3TierScaleAndRuins:
    """EB-3 (Econ Balance gate Aug 7 2026): the tier-scaled rate + the
    ruins-bill-nothing rule, pinned at the seam that bills them."""

    def test_tier_ordering_is_structural(self):
        tiers = EUROPE_INFRASTRUCTURE_UPKEEP_BY_TIER
        assert tiers["capital"] >= tiers["major_city"] >= tiers["city"], (
            "EB-3 B10: the ordering capital >= major_city >= city is "
            "structural — the digits are in-band, the shape is not")
        assert tiers["capital"] == EUROPE_INFRASTRUCTURE_UPKEEP

    def test_market_on_a_city_is_finally_a_want(self, world):
        """CA8-D1's own measurement: a market on a `city` (+37 gross) paid
        40/turn forever = −3. Under the tier rate (20) it nets positive —
        every legal slot is a rational want."""
        city = next(r for r in world.regions.values()
                    if r.region_type == "city" and r.controller == "France")
        gross_bonus = int(city.income_value * 1.25) - city.income_value
        assert gross_bonus > infrastructure_upkeep_rate(city), (
            f"a market on {city.name} (+{gross_bonus}g) must out-earn its "
            f"{infrastructure_upkeep_rate(city)}g/turn bill")

    def test_a_ruin_bills_nothing(self, world):
        """The IGR-X9 decision: a damaged structure neither functions nor
        bills; repair (150g) restores function AND the bill."""
        nation = "France"
        region = _homeland_region(world, nation)
        region.buildings.append({"type": "fortification", "damaged": True})
        assert world.calculate_turn_income(nation)["infrastructure"] == 0
        # repair restores the bill
        region.buildings[-1]["damaged"] = False
        assert (world.calculate_turn_income(nation)["infrastructure"]
                == infrastructure_upkeep_rate(region))

    def test_a_damaged_watchtower_bills_nothing(self, world):
        nation = "France"
        region = _homeland_region(world, nation)
        region.watchtower = "damaged"
        assert world.calculate_turn_income(nation)["infrastructure"] == 0
        region.watchtower = "active"
        assert (world.calculate_turn_income(nation)["infrastructure"]
                == infrastructure_upkeep_rate(region))


class TestSymmetryAndScope:
    def test_ai_nation_pays_through_the_same_seam(self, world):
        """GR5: an enemy nation's buildings cost through the identical
        per-nation income seam — no player-only sink."""
        nation = "Austria"
        region = _homeland_region(world, nation)
        region.buildings.append({"type": "stables"})
        assert (world.calculate_turn_income(nation)["infrastructure"]
                == infrastructure_upkeep_rate(region))

    def test_bankruptcy_mercy_halves_it(self, world):
        nation = "France"
        region = _homeland_region(world, nation)
        region.buildings.append({"type": "fortification"})
        region.buildings.append({"type": "supply_depot"})
        world.nation_bankruptcy_turns[nation] = 1
        # 2 structures at the tier rate, halved by mercy (matches occupation/upkeep)
        assert (world.calculate_turn_income(nation)["infrastructure"]
                == (2 * infrastructure_upkeep_rate(region)) // 2)

    def test_legacy_world_pays_no_infrastructure(self):
        """N1: the legacy fixture world's economy pins never move."""
        legacy = WorldState()
        region = next(iter(legacy.regions.values()))
        region.buildings.append({"type": "fortification"})
        inc = legacy.calculate_turn_income(legacy.player_nation)
        assert inc["infrastructure"] == 0


class TestLedgerReconciles:
    def test_infrastructure_is_a_declared_net_component(self, world):
        nation = "France"
        region = _homeland_region(world, nation)
        region.buildings.append({"type": "fortification"})
        econ = _build_economy(world, nation)
        assert econ["infrastructure"] == infrastructure_upkeep_rate(region)
        # the signed-sum guard lives in test_economy_ledger_reconciliation;
        # here just confirm the value is present and non-zero when built
        assert econ["infrastructure"] > 0
