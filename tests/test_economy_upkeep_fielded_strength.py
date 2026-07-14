"""Upkeep bills on ACTUAL fielded strength — "you pay for the soldiers you have."

Design reversal (July 14, 2026, user-directed after the Sweep-3 economy
playthrough): the earlier EC-U1 "non-regressive" upkeep billed a corps on its
ESTABLISHMENT — a monotonic high-water-mark of strength — so attrition never
lowered the bill. Playtest verdict: a battered corps became a permanent money
pit with no relief, and the ledger showed a phantom army total (establishment,
not the men actually in the field). The chosen model is the intuitive one:
upkeep is `(strength // 1000) * rate`, proportional to CURRENT strength. Lose
troops → pay less; rebuild the corps (recruit gold) → pay more again.

Boot is byte-identical to the old formula (at boot billed == strength either
way), so the E1 solvency band, the ES-3 over-limit surcharge, and the EC-U3
Grande Armée surcharge are all untouched at turn 1 — they simply now key off
the live fielded total, so a shrinking army sheds its surcharge too.
"""

from pathlib import Path

import pytest

from backend.models.marshal import Marshal
from backend.models.world_state import WorldState, EUROPE_UPKEEP_RATE

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)


@pytest.fixture
def world():
    return WorldState.from_scenario(str(SCENARIO_PATH))


def _france_marshals(world):
    return [m for m in world.marshals.values()
            if m.nation == "France" and m.strength > 0]


def _net(world, nation):
    """Region-derived net (the seam attrition moves): income minus every
    per-turn drain. Trade/tribute/treaty are strength-independent."""
    inc = world.calculate_turn_income(nation)
    up = world.calculate_turn_upkeep(nation)
    return (inc["income"] - inc["occupation"] - inc["dotation_skim"]
            - inc["rente_cost"] - inc["infrastructure"] - up["total"])


class TestBillsOnCurrentStrength:
    """Upkeep is proportional to the strength actually in the field."""

    def test_boot_base_is_strength_proportional(self, world):
        up = world.calculate_turn_upkeep("France")
        expected_base = sum((m.strength // 1000) * EUROPE_UPKEEP_RATE
                            for m in _france_marshals(world))
        assert up["base"] == expected_base

    def test_billed_strength_equals_current_strength(self, world):
        for row in world.calculate_turn_upkeep("France")["breakdown"]:
            assert row["billed_strength"] == row["strength"]

    def test_total_strength_is_fielded_not_peak(self, world):
        """army total reflects the men actually present — a corps ground down
        in battle immediately shrinks the reported total (fixes the phantom
        establishment total the playtest flagged)."""
        m = _france_marshals(world)[0]
        peak = m.strength
        before = world.calculate_turn_upkeep("France")["total_strength"]
        m.strength = peak // 2
        after = world.calculate_turn_upkeep("France")["total_strength"]
        assert after == before - (peak - peak // 2)


class TestAttritionLowersTheBill:
    """The intended model: losing soldiers reduces upkeep."""

    def test_attrition_lowers_upkeep(self, world):
        base_before = world.calculate_turn_upkeep("France")["base"]
        for m in _france_marshals(world):
            m.strength = int(m.strength * 0.6)
        base_after = world.calculate_turn_upkeep("France")["base"]
        assert base_after < base_before

    def test_attrition_raises_net(self, world):
        """The flip side, stated as the playtest measured it: a smaller army
        is cheaper, so net rises — you are not taxed for troops you no longer
        have. (This is now the design, not a bug.)"""
        net_before = _net(world, "France")
        for m in _france_marshals(world):
            m.strength = int(m.strength * 0.6)
        net_after = _net(world, "France")
        assert net_after > net_before

    def test_rebuilding_raises_upkeep_again(self, world):
        m = _france_marshals(world)[0]
        start = m.strength
        m.strength = start // 2
        low = world.calculate_turn_upkeep("France")["base"]
        m.strength = start + 10000            # rebuilt above the original size
        high = world.calculate_turn_upkeep("France")["base"]
        assert high > low


class TestSurchargesFollowFieldedTotal:
    """Over-limit and Grande Armée surcharges key off live strength, so a
    shrinking army sheds them (no surcharge for a phantom establishment)."""

    def test_over_limit_surcharge_shrinks_with_the_army(self, world):
        up_full = world.calculate_turn_upkeep("France")
        assert up_full["over_limit"] is True            # boot France is over
        surcharge_full = up_full["surcharge"]
        for m in _france_marshals(world):
            m.strength = m.strength // 3                 # collapse below limit
        surcharge_small = world.calculate_turn_upkeep("France")["surcharge"]
        assert surcharge_small < surcharge_full

    def test_ledger_total_reconciles(self, world):
        up = world.calculate_turn_upkeep("France")
        assert up["total"] == up["base"] + up["surcharge"]


class TestLegacyWorldUnchanged:
    def test_legacy_bills_on_strength(self):
        legacy = WorldState()
        marshal = next(m for m in legacy.marshals.values() if m.strength > 0)
        base = legacy.calculate_turn_upkeep(marshal.nation)["base"]
        expected = sum((m.strength // 1000) * 5
                       for m in legacy.marshals.values()
                       if m.nation == marshal.nation and m.strength > 0)
        assert base == expected


class TestNoEstablishmentResidue:
    """Regression guard: the establishment high-water-mark machinery is gone —
    a marshal carries no establishment field, and serialization ignores a
    stale key from an old save."""

    def test_marshal_has_no_establishment_field(self):
        m = Marshal(name="Ney", location="Paris", strength=40000,
                    personality="aggressive", nation="France")
        assert not hasattr(m, "establishment")
        assert "establishment" not in m.to_dict()

    def test_old_save_with_establishment_key_still_loads(self):
        data = Marshal(name="Ney", location="Paris", strength=40000,
                       personality="aggressive", nation="France").to_dict()
        data["establishment"] = 99999          # stale key from a pre-reversal save
        restored = Marshal.from_dict(data)      # must not raise
        assert restored.strength == 40000
        assert not hasattr(restored, "establishment")

    def test_world_has_no_reconcile_method(self, world):
        assert not hasattr(world, "_reconcile_establishments")
