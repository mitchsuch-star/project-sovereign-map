"""PRE-EC ledger-floor regression tests (ECONOMY_REVISIT_SPEC.md §0, §3).

The §3 presentation invariant was ALREADY BROKEN before the Economy Revisit
phase: ``ledger.py _build_economy`` folds seven gold streams into ``net``
(income + trade_income + admin_bonus + treaty_gold + vassal_tribute
+ settlement_gold − upkeep), but the Godot economy tab
(``strategic_ledger.gd _render_economy``) only rendered a subset — ``admin_bonus``,
``treaty_gold`` and ``vassal_tribute`` were invisible. So whenever France held a
vassal (tribute is common) or a gold-per-turn treaty clause, the on-screen lines
did NOT sum to the displayed Net — the SC-33 "invisible tribute" bug class
recurring for three live streams.

These pins guard the invariant in BOTH directions:
  1. the backend Net equals the signed sum of its declared components, and
  2. every declared component is actually rendered in the Godot ledger.

If a future slice adds a new gold stream to Net, test (1) fails until the new
term is added to ``NET_GOLD_COMPONENTS`` here, and test (2) then fails until the
stream is also rendered in ``strategic_ledger.gd`` — closing the SC-33 gap by
construction.
"""

from pathlib import Path

import pytest

from backend.game_logic.ledger import _build_economy
from backend.models.world_state import WorldState

# The gold-bearing keys in the _build_economy dict that are summed into `net`,
# with their sign. MUST mirror ledger.py _build_economy's `net` expression.
# ES-3 (S5): upkeep is split into base + over-limit surcharge so the surcharge
# renders as its own ledger line — the by-construction guard below then forces
# both halves to be rendered ("upkeep" total stays in the dict for reference
# but is no longer a net term).
# ES-2 (S6): occupation cost on non-homeland provinces is its own signed
# component (income stays GROSS) — declared here so the guard forces its
# "Occupation" line in strategic_ledger.gd.
NET_GOLD_COMPONENTS = {
    "income": +1,
    "trade_income": +1,
    "admin_bonus": +1,
    "treaty_gold": +1,
    "vassal_tribute": +1,
    "settlement_gold": +1,
    "occupation": -1,
    "upkeep_base": -1,
    "upkeep_surcharge": -1,
}

_LEDGER_GD = (
    Path(__file__).resolve().parents[1]
    / "godot-client"
    / "project-sovereign"
    / "scripts"
    / "strategic_ledger.gd"
)


@pytest.fixture()
def europe():
    return WorldState(sovereign_map="europe")


class TestNetReconciliation:
    def test_net_equals_signed_component_sum(self, europe):
        econ = _build_economy(europe, europe.player_nation)
        total = sum(
            sign * int(econ.get(key, 0)) for key, sign in NET_GOLD_COMPONENTS.items()
        )
        assert total == int(econ["net"]), (
            "Net must equal the signed sum of its declared components; "
            f"got components={ {k: econ.get(k) for k in NET_GOLD_COMPONENTS} } "
            f"sum={total} net={econ['net']}. A stream was added to Net without "
            "being declared in NET_GOLD_COMPONENTS (and rendered in the ledger)."
        )

    def test_admin_bonus_is_exercised(self, europe):
        # Non-vacuity: at least one of the previously-invisible components is
        # live on a fresh France world (admin_bonus = unused admin AP x 25), so
        # the reconciliation identity above is not trivially all-zeros.
        econ = _build_economy(europe, europe.player_nation)
        assert econ["admin_bonus"] > 0


class TestEveryNetComponentIsRendered:
    """The direct guard for the PRE-EC bug: read the Godot renderer and assert
    each Net component key is referenced. Before the fix this failed for
    admin_bonus / treaty_gold / vassal_tribute."""

    def test_ledger_gd_exists(self):
        assert _LEDGER_GD.is_file(), f"ledger renderer not found at {_LEDGER_GD}"

    @pytest.mark.parametrize("component", sorted(NET_GOLD_COMPONENTS))
    def test_component_is_rendered_in_gd(self, component):
        gd_text = _LEDGER_GD.read_text(encoding="utf-8")
        assert f'"{component}"' in gd_text, (
            f'"{component}" is summed into Net (ledger.py _build_economy) but is '
            f"not referenced in strategic_ledger.gd _render_economy — the on-screen "
            f"economy lines will not reconcile to Net (SC-33 / PRE-EC invariant)."
        )
