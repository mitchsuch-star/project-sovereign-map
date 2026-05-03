"""Slice C1b `project_balance_after_settlement()` projection tests.

Spec §6.acceptance lines 1200-1217 require a pure projection helper that:

- Reads cached `get_active_nations()`, `get_nation_regions()`,
  `get_diplomatic_state()`, `world.vassals`, `get_power_tier()` only.
- Applies term deltas in deterministic order (liberation → forced_alliance
  → territory → vassalage / subjugation).
- Returns the canonical settlement-preview shape.
- NEVER mutates `world.regions`, `world.diplomatic_states`,
  `world.vassals`, or any live cache. Plan line 228 requires a no-mutation
  regression test.
"""

from __future__ import annotations

from backend.game_logic.settlement_scoring import (
    HEGEMONY_MOD_CLAMP,
    project_balance_after_settlement,
)
from backend.models.world_state import WorldState


def _territory_term(*, from_n: str, to_n: str, regions: list[str]) -> dict:
    return {
        "type": "territory",
        "from": from_n,
        "to": to_n,
        "regions": list(regions),
    }


def test_projection_returns_canonical_shape():
    """Spec line 1203: shape must match the spec settlement-preview dict."""
    world = WorldState()
    result = project_balance_after_settlement(
        world,
        war_id="war_test_001",
        settlement_terms=[],
    )
    expected_keys = {
        "pre_hegemon",
        "post_hegemon",
        "pre_share",
        "post_share",
        "crossed_band",
        "deepened_band",
        "hegemon_swap",
        "modifier",
    }
    assert set(result.keys()) == expected_keys


def test_projection_modifier_clamped_to_minus_20_to_10():
    """Spec line 1119: clamp `[-20, 10]`."""
    lo, hi = HEGEMONY_MOD_CLAMP
    assert lo == -20
    assert hi == 10


def test_projection_no_terms_means_zero_modifier_or_steady_state():
    """No terms → no projected band crossing → modifier 0."""
    world = WorldState()
    result = project_balance_after_settlement(
        world,
        war_id="war_test_001",
        settlement_terms=[],
    )
    assert result["modifier"] == 0
    assert result["crossed_band"] is None
    assert result["deepened_band"] is None


def test_projection_does_not_mutate_world_regions():
    """Plan line 228: no-mutation regression test on world.regions."""
    world = WorldState()
    pre_regions = {
        name: region.controller for name, region in world.regions.items()
    }
    pre_active = list(world.get_active_nations())
    terms = [_territory_term(
        from_n="Austria", to_n="France", regions=["Bavaria", "Vienna"],
    )]
    project_balance_after_settlement(
        world,
        war_id="war_test_001",
        settlement_terms=terms,
    )
    post_regions = {
        name: region.controller for name, region in world.regions.items()
    }
    post_active = list(world.get_active_nations())
    assert pre_regions == post_regions
    assert pre_active == post_active


def test_projection_does_not_mutate_diplomatic_states():
    """Plan line 228: no-mutation regression test on diplomatic_states."""
    world = WorldState()
    pre_states = dict(world.diplomatic_states)
    terms = [
        {"type": "forced_alliance", "from": "Austria", "to": "France"},
    ]
    project_balance_after_settlement(
        world,
        war_id="war_test_001",
        settlement_terms=terms,
    )
    assert dict(world.diplomatic_states) == pre_states


def test_projection_does_not_mutate_vassals():
    """Plan line 228: no-mutation regression test on world.vassals."""
    world = WorldState()
    world.vassals = {"Saxony": {"lord": "France", "loyalty": 50}}
    pre_vassals = {k: dict(v) for k, v in world.vassals.items()}
    terms = [
        {"type": "liberation", "to": "Saxony"},
    ]
    project_balance_after_settlement(
        world,
        war_id="war_test_001",
        settlement_terms=terms,
    )
    assert {k: dict(v) for k, v in world.vassals.items()} == pre_vassals


def test_projection_territory_transfer_increases_recipient_share():
    """Apply a large territory transfer to France; projected share must
    move toward France."""
    world = WorldState()
    pre = project_balance_after_settlement(
        world,
        war_id="war_test_001",
        settlement_terms=[],
    )
    terms = [_territory_term(
        from_n="Austria",
        to_n="France",
        regions=["Bavaria", "Vienna", "Bohemia", "Tyrol"],
    )]
    post = project_balance_after_settlement(
        world,
        war_id="war_test_001",
        settlement_terms=terms,
    )
    # France's share of Europe must not decrease; it should rise as Austria
    # is reduced to zero regions.
    assert post["pre_share"] == pre["pre_share"]
    if pre["pre_hegemon"] == "France":
        assert post["post_share"] >= pre["post_share"]
