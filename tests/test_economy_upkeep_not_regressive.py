"""EC-U1 — non-regressive upkeep (Combat Overhaul Phase 4, §4 Phase 4).

The Field Review's economy finding: army upkeep was `(strength // 1000) *
rate`, purely proportional to SURVIVING strength, while income is region-
derived. So grinding a corps down in battle LOWERED its upkeep and — income
being unchanged — RAISED net income. "Losing pays." (Live proof: France's net
rose 1,702 -> 3,250 as its army was attrited.)

The fix bills upkeep on the corps' ESTABLISHMENT — a per-turn high-water-mark
of strength (`Marshal.establishment`, reconciled in
`WorldState._reconcile_establishments`) — so `billed = max(strength,
establishment)` never falls with battle losses. Era note: the Napoleonic
state committed to maintaining corps at establishment; losses obliged paid
replacements (recruit gold), never a rebate.

Establishment is 0 until the first per-turn reconcile, so a fresh / directly-
set marshal bills on CURRENT strength — every pre-existing direct-call upkeep
test is unchanged, and the E1 boot-solvency band (Austria +18) is untouched.
Europe-scoped (N1: the legacy fixture world keeps strength-proportional
upkeep).
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
    """Region-derived net (the seam attrition can move): income minus every
    per-turn drain. Trade/tribute/treaty are strength-independent and applied
    on their own seams, so they are irrelevant to the regressivity question."""
    inc = world.calculate_turn_income(nation)
    up = world.calculate_turn_upkeep(nation)
    return (inc["income"] - inc["occupation"] - inc["dotation_skim"]
            - inc["rente_cost"] - inc["infrastructure"] - up["total"])


class TestBootIsUnchanged:
    """Establishment is 0 at boot, so billed == strength — the fresh-world
    upkeep is byte-identical to the old strength-proportional formula."""

    def test_fresh_world_bills_on_current_strength(self, world):
        up = world.calculate_turn_upkeep("France")
        expected_base = sum((m.strength // 1000) * EUROPE_UPKEEP_RATE
                            for m in _france_marshals(world))
        assert up["base"] == expected_base

    def test_every_marshal_billed_on_current_strength_at_boot(self, world):
        for row in world.calculate_turn_upkeep("France")["breakdown"]:
            assert row["billed_strength"] == row["strength"]


class TestAttritionDoesNotRaiseNet:
    """The core exit criterion: attrition must not increase net income."""

    def test_establishment_holds_upkeep_after_losses(self, world):
        world._reconcile_establishments()          # establish peaks
        net_before = _net(world, "France")
        for m in _france_marshals(world):
            m.strength = int(m.strength * 0.6)      # heavy attrition
        net_after = _net(world, "France")
        assert net_after <= net_before, (
            f"attrition RAISED net ({net_before} -> {net_after}) — upkeep is "
            "still regressive")

    def test_the_bug_reproduces_without_the_fix(self, world):
        """Falsifiable counterfactual: with establishment forced back to 0
        (the pre-fix behaviour), the SAME attrition raises net — proving the
        test exercises the real mechanism, not a no-op."""
        world._reconcile_establishments()
        net_before = _net(world, "France")
        for m in _france_marshals(world):
            m.strength = int(m.strength * 0.6)
        for m in _france_marshals(world):
            m.establishment = 0                     # undo the fix
        net_buggy = _net(world, "France")
        assert net_buggy > net_before, (
            "counterfactual failed — without establishment, attrition should "
            "raise net (the original regressive bug)")


class TestEstablishmentHighWaterMark:
    """Pure-unit invariants for the billing helper and the reconcile."""

    def _europe_marshal(self):
        return Marshal(name="Test", location="Paris", strength=40000,
                       personality="aggressive", nation="France")

    def test_billed_strength_never_below_establishment(self):
        m = self._europe_marshal()
        m.establishment = 40000
        m.strength = 12000                          # ground down
        assert m.get_upkeep_strength() == 40000

    def test_growth_raises_establishment_bill(self):
        m = self._europe_marshal()
        m.establishment = 40000
        m.strength = 55000                          # reinforced above peak
        assert m.get_upkeep_strength() == 55000

    def test_reconcile_only_ratchets_up(self, world):
        m = _france_marshals(world)[0]
        m.establishment = 0
        m.strength = 30000
        world._reconcile_establishments()
        assert m.establishment == 30000
        m.strength = 10000                          # attrition
        world._reconcile_establishments()
        assert m.establishment == 30000             # holds, never falls

    def test_reconcile_captures_recruited_peak(self, world):
        m = _france_marshals(world)[0]
        m.establishment = 0
        start = m.strength
        world._reconcile_establishments()           # establish at start
        m.strength = start + 15000                  # recruit up
        world._reconcile_establishments()           # capture new peak
        m.strength = start                          # then attrit back
        assert m.get_upkeep_strength() == start + 15000

    def test_legacy_world_ignores_establishment(self):
        """N1: the legacy fixture world bills on strength regardless of
        establishment, so its economy pins never move."""
        legacy = WorldState()
        marshal = next(m for m in legacy.marshals.values() if m.strength > 0)
        marshal.establishment = 999999              # would inflate if read
        base = legacy.calculate_turn_upkeep(marshal.nation)["base"]
        expected = sum((m.strength // 1000) * 5
                       for m in legacy.marshals.values()
                       if m.nation == marshal.nation and m.strength > 0)
        assert base == expected


class TestSerialization:
    def test_establishment_round_trips(self):
        m = Marshal(name="Ney", location="Paris", strength=40000,
                    personality="aggressive", nation="France")
        m.establishment = 47000
        restored = Marshal.from_dict(m.to_dict())
        assert restored.establishment == 47000

    def test_old_save_defaults_to_zero(self):
        data = Marshal(name="Ney", location="Paris", strength=40000,
                       personality="aggressive", nation="France").to_dict()
        del data["establishment"]
        restored = Marshal.from_dict(data)
        assert restored.establishment == 0          # bills on current strength
