"""C1a side-pressure foundation tests.

Slice C1a of `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md`
ships the pure helpers consumed by common-peace acceptance, direct-score
gates, territory legitimacy `weak_pressure_penalty` checks, and advisory
rows per spec §6.3 / §10.4.

These tests pin the spec §6.3 weighted-average contract before C1b layers
the full common-peace acceptance formula (`base_side_pressure`,
`term_harshness_penalty`, leader-own-loss clamp, burden penalty,
projected hegemony, war-objective alignment, war exhaustion,
abandoned-by-ally) on top.

Coverage owned here:

- Hard-stop reasons (`no_covered_enemy_participants`,
  `no_direct_war_score_for_covered_enemy`).
- `direct_scores` is built before any `max()` (spec line 237).
- `direct_score = max(active_pairs)` with deterministic alphabetical
  tie-break and named `direct_score_source` (spec line 243).
- ARMISTICE / PEACE / non-WAR proposer-side members are excluded from
  pressure terms (spec line 215 — `if world.is_at_war(...)`).
- Power-tier weights `{major: 3, secondary: 2, minor: 1}` with
  ``DEFAULT_POWER_TIER = secondary`` fallback for unauthored nations.
- ``round()`` not floor (spec line 242), and the exact Pressburg-style
  worked example (line 1153).
- Aggregate clamp to ``[-100, 100]`` (spec line 239).
- Symmetric defender-side calculation (spec §6.3 used both sides).
- Mixed-strength dilution where many minors lower the average against a
  strong major-vs-major direct score (spec line 244).
- Monotonicity: increasing one direct score does not lower the
  side-pressure score with all other inputs fixed (spec line 246 / plan
  acceptance line 220).
- Memoization contract: settlement preview / confirm pass a pre-computed
  ``direct_scores`` map and the helper trusts it without recomputation
  (spec line 238).
"""

from __future__ import annotations

import pytest

from backend.game_logic.settlement_scoring import (
    DEFAULT_POWER_TIER,
    HARD_STOP_NO_COVERED_ENEMY,
    HARD_STOP_NO_DIRECT_WAR_SCORE,
    POWER_TIER_WEIGHTS,
    compute_direct_scores_by_enemy,
    compute_side_pressure_score,
    power_tier_weight,
    select_direct_score,
)
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import (
    install_synthetic_active_roster,
    make_synthetic_war_instance,
)


# ===========================================================================
# Test world helpers
# ===========================================================================


def _build_world_with_war_pair(
    *,
    pairs: dict,
    states: dict | None = None,
    extra_active: list[str] | None = None,
) -> WorldState:
    """Build a world with explicit war_scores + diplomatic_states.

    `pairs` maps ``(nation_a, nation_b)`` to a war_score from
    ``nation_a``'s perspective. The helper writes the canonical alphabetical
    storage value so `get_war_score_for(world, nation_a, nation_b)` returns
    exactly the requested score after sign flipping.

    `states` lets a test override the diplomatic state for a pair (default
    ``"WAR"``). Pass ``"ARMISTICE"`` / ``"PEACE"`` to exclude that pair
    from the side-pressure calculation.
    """
    world = WorldState()
    if extra_active:
        install_synthetic_active_roster(world, extra_active)

    states = states or {}
    for (a, b), score in pairs.items():
        key = world._make_diplo_key(a, b)
        # Stored sign convention: alphabetically-first nation's perspective.
        if sorted([a, b])[0] == a:
            world.war_scores[key] = int(score)
        else:
            world.war_scores[key] = -int(score)
        diplo_state = states.get((a, b)) or states.get((b, a)) or "WAR"
        world.diplomatic_states[key] = diplo_state
    return world


def _instance(
    *,
    attackers: list[str],
    defenders: list[str],
    attacker_leader: str | None = None,
    defender_leader: str | None = None,
):
    return make_synthetic_war_instance(
        "war_test_001",
        attackers=attackers,
        defenders=defenders,
        attacker_leader=attacker_leader or attackers[0],
        defender_leader=defender_leader or defenders[0],
    )


# ===========================================================================
# Tests
# ===========================================================================


def test_empty_covered_enemy_set_returns_no_covered_enemy_hard_stop():
    world = _build_world_with_war_pair(pairs={("France", "Austria"): 30})
    instance = _instance(attackers=["France"], defenders=["Austria"])

    result = compute_side_pressure_score(
        world,
        instance,
        proposer_side="attackers",
        covered_enemy_participants=[],
    )

    assert result["score"] is None
    assert result["hard_stops"] == [
        {"reason": HARD_STOP_NO_COVERED_ENEMY, "enemy": None}
    ]
    assert result["direct_scores"] == {}
    assert result["direct_score_sources"] == {}
    assert result["pressure_terms"] == []


def test_covered_enemy_with_no_active_war_pair_emits_per_enemy_hard_stop():
    """Spec §6.3 line 237: an enemy with no proposer-side war pair is a hard
    stop for that enemy, named `no_direct_war_score_for_covered_enemy`."""
    world = _build_world_with_war_pair(pairs={("France", "Austria"): 30})
    # Default WorldState() seeds France|Prussia as WAR; the test needs
    # Prussia to have NO active proposer-side pair so the hard stop fires.
    world.diplomatic_states[world._make_diplo_key("France", "Prussia")] = "PEACE"

    # Prussia has no war pair against France; instance includes both
    # attackers and defenders for shape, but Prussia is the covered enemy.
    instance = _instance(
        attackers=["France"],
        defenders=["Austria", "Prussia"],
    )

    result = compute_side_pressure_score(
        world,
        instance,
        proposer_side="attackers",
        covered_enemy_participants=["Prussia"],
    )

    assert result["score"] is None
    assert {
        "reason": HARD_STOP_NO_DIRECT_WAR_SCORE,
        "enemy": "Prussia",
    } in result["hard_stops"]
    # The map names the missing enemy explicitly so callers see *which*
    # covered enemy caused the hard stop.
    assert "Prussia" in result["direct_scores"]
    assert result["direct_scores"]["Prussia"] == {}


def test_direct_scores_built_before_max_then_select_returns_max_with_source():
    """Spec line 243: `direct_score = max(active_pairs)` and debug must
    name the selected `direct_score_source`."""
    world = _build_world_with_war_pair(
        pairs={
            ("France", "Austria"): 10,
            ("Bavaria", "Austria"): 50,  # ally pressure outshines leader
        }
    )
    instance = _instance(
        attackers=["France", "Bavaria"],
        defenders=["Austria"],
    )

    direct_map = compute_direct_scores_by_enemy(
        world,
        instance,
        proposer_side="attackers",
        covered_enemy_participants=["Austria"],
    )
    assert direct_map == {"Austria": {"France": 10, "Bavaria": 50}}

    selection = select_direct_score(direct_map["Austria"])
    assert selection == (50, "Bavaria")

    result = compute_side_pressure_score(
        world,
        instance,
        proposer_side="attackers",
        covered_enemy_participants=["Austria"],
    )
    assert result["direct_score_sources"]["Austria"]["score"] == 50
    assert result["direct_score_sources"]["Austria"]["source"] == "Bavaria"


def test_select_direct_score_breaks_ties_alphabetically_for_determinism():
    """Settlement reviews must regenerate identically across reruns; ties
    must therefore have a deterministic break per spec debug-output rule."""
    selection = select_direct_score({"Saxony": 30, "Bavaria": 30, "Naples": 30})
    assert selection == (30, "Bavaria")  # alphabetical winner among ties


def test_armistice_pairs_are_excluded_from_pressure_terms():
    """Spec §6.3 line 215: only WAR pairs feed `pressure_terms` via
    `if world.is_at_war(side_member, enemy)`."""
    world = _build_world_with_war_pair(
        pairs={
            ("France", "Austria"): 50,
            ("Bavaria", "Austria"): 80,
        },
        states={
            ("France", "Austria"): "WAR",
            ("Bavaria", "Austria"): "ARMISTICE",
        },
    )
    instance = _instance(
        attackers=["France", "Bavaria"],
        defenders=["Austria"],
    )

    result = compute_side_pressure_score(
        world,
        instance,
        proposer_side="attackers",
        covered_enemy_participants=["Austria"],
    )

    # Bavaria's higher score is excluded by the ARMISTICE filter; only
    # France's score survives.
    assert result["direct_scores"]["Austria"] == {"France": 50}
    assert result["direct_score_sources"]["Austria"]["source"] == "France"
    assert result["score"] == 50


def test_power_tier_weights_match_spec_with_secondary_fallback():
    """Spec §6.3 + DEFAULT_POWER_TIER fallback for unauthored nations."""
    world = WorldState()

    assert POWER_TIER_WEIGHTS == {"major": 3, "secondary": 2, "minor": 1}
    assert DEFAULT_POWER_TIER == "secondary"

    assert power_tier_weight(world, "France") == 3
    assert power_tier_weight(world, "Spain") == 2
    assert power_tier_weight(world, "Bavaria") == 1
    # Unauthored nation falls back to `secondary` weight 2.
    assert power_tier_weight(world, "FictionalNation") == 2
    # Defensive: unrecognized authored strings also fall back to secondary.
    unknown_tier_world = type(
        "UnknownTierWorld",
        (),
        {"get_power_tier": lambda self, nation: "great_power"},
    )()
    assert power_tier_weight(unknown_tier_world, "Austria") == 2


def test_pressburg_worked_example_uses_round_not_floor_and_clamps_to_range():
    """Spec line 1153 worked example: `side_pressure_score = 70`, scale `0.65`
    → `+46`. The aggregate before scaling must already round to `70`.

    Concrete fixture: France (major) vs Austria (major) at +70, France vs
    Naples (secondary) at +70 → weighted average = 70.
    Increase Naples to +79 → aggregate = (70*3 + 79*2)/5 = 73.6 → 74.
    """
    world = _build_world_with_war_pair(
        pairs={
            ("France", "Austria"): 70,
            ("France", "Naples"): 70,
        }
    )
    instance = _instance(
        attackers=["France"],
        defenders=["Austria", "Naples"],
    )

    result = compute_side_pressure_score(
        world,
        instance,
        proposer_side="attackers",
        covered_enemy_participants=["Austria", "Naples"],
    )
    assert result["score"] == 70  # exact match to worked example seed

    world2 = _build_world_with_war_pair(
        pairs={
            ("France", "Austria"): 70,
            ("France", "Naples"): 79,
        }
    )
    result2 = compute_side_pressure_score(
        world2,
        instance,
        proposer_side="attackers",
        covered_enemy_participants=["Austria", "Naples"],
    )
    # (70*3 + 79*2) / 5 = 73.6 — `round()` not floor, integer clamp.
    assert result2["score"] == 74


def test_aggregate_score_clamps_to_war_score_range_after_rounding():
    """Spec line 239: scores are clamped to `[-100, 100]` after aggregation.

    Defensive: we directly inject pre-computed `direct_scores` outside the
    normal `get_war_score_for` ceiling so the helper proves the post-round
    clamp is applied.
    """
    world = WorldState()
    instance = _instance(attackers=["France"], defenders=["Austria"])

    high_result = compute_side_pressure_score(
        world,
        instance,
        proposer_side="attackers",
        covered_enemy_participants=["Austria"],
        direct_scores={"Austria": {"France": 250}},
    )
    assert high_result["score"] == 100

    low_result = compute_side_pressure_score(
        world,
        instance,
        proposer_side="attackers",
        covered_enemy_participants=["Austria"],
        direct_scores={"Austria": {"France": -250}},
    )
    assert low_result["score"] == -100


def test_defender_side_proposer_is_symmetric_to_attacker_side():
    """Spec §6.3 used both sides — defender-side common peace must compute
    identically when `proposer_side="defenders"`."""
    world = _build_world_with_war_pair(
        pairs={
            ("Austria", "France"): 50,  # Austria's score from its POV
            ("Prussia", "France"): 30,
        }
    )
    instance = _instance(
        attackers=["France"],
        defenders=["Austria", "Prussia"],
    )

    result = compute_side_pressure_score(
        world,
        instance,
        proposer_side="defenders",
        covered_enemy_participants=["France"],
    )

    # Direct scores are from defender perspective; max picks Austria's +50.
    assert result["direct_scores"]["France"]["Austria"] == 50
    assert result["direct_scores"]["France"]["Prussia"] == 30
    assert result["score"] == 50


def test_mixed_strength_minors_dilute_strong_major_vs_major_pressure():
    """Spec line 244: weighted average is anti-farming by design — many
    minor covered enemies dilute a strong major-vs-major score. Pin the
    behavior so future tuning changes are explicit.
    """
    world = _build_world_with_war_pair(
        pairs={
            ("France", "Austria"): 80,    # major vs major
            ("France", "Bavaria"): 10,    # minor
            ("France", "Saxony"): 10,     # minor
            ("France", "Portugal"): 10,   # minor
        }
    )
    instance = _instance(
        attackers=["France"],
        defenders=["Austria", "Bavaria", "Saxony", "Portugal"],
    )

    narrow = compute_side_pressure_score(
        world,
        instance,
        proposer_side="attackers",
        covered_enemy_participants=["Austria"],
    )
    full = compute_side_pressure_score(
        world,
        instance,
        proposer_side="attackers",
        covered_enemy_participants=[
            "Austria",
            "Bavaria",
            "Saxony",
            "Portugal",
        ],
    )

    # Narrow major-only: weighted = 80, weight = 3 → 80
    assert narrow["score"] == 80
    # Full coverage: (80*3 + 10*1 + 10*1 + 10*1) / (3+1+1+1) = 270/6 = 45
    assert full["score"] == 45
    assert full["score"] < narrow["score"]


def test_covered_enemy_iteration_is_deterministic_for_debug_rows():
    """Advisory/debug rows should not depend on caller iterable ordering."""
    world = _build_world_with_war_pair(
        pairs={
            ("France", "Austria"): 60,
            ("France", "Bavaria"): 20,
            ("France", "Saxony"): 10,
        }
    )
    instance = _instance(
        attackers=["France"],
        defenders=["Austria", "Bavaria", "Saxony"],
    )

    result = compute_side_pressure_score(
        world,
        instance,
        proposer_side="attackers",
        covered_enemy_participants={"Saxony", "Austria", "Bavaria"},
    )

    assert list(result["direct_scores"]) == ["Austria", "Bavaria", "Saxony"]
    assert list(result["direct_score_sources"]) == [
        "Austria",
        "Bavaria",
        "Saxony",
    ]
    assert result["pressure_terms"] == [(60, 3), (20, 1), (10, 1)]


def test_minor_ally_high_score_outweighs_losing_leader():
    """Spec line 243 mandates a fixture where the side leader is losing or
    barely winning while a minor ally has the selected high score; debug
    must name `direct_score_source`.
    """
    world = _build_world_with_war_pair(
        pairs={
            ("France", "Austria"): -20,    # leader losing
            ("Bavaria", "Austria"): 60,    # minor ally winning hard
        }
    )
    instance = _instance(
        attackers=["France", "Bavaria"],
        defenders=["Austria"],
    )

    result = compute_side_pressure_score(
        world,
        instance,
        proposer_side="attackers",
        covered_enemy_participants=["Austria"],
    )

    assert result["direct_score_sources"]["Austria"]["source"] == "Bavaria"
    assert result["direct_score_sources"]["Austria"]["score"] == 60
    assert result["score"] == 60


def test_score_is_monotonic_in_direct_score_with_all_else_held_constant():
    """Plan acceptance line 220: increasing `side_pressure_score` with all
    other components fixed must not worsen the eventual common-peace
    acceptance. This test pins the underlying side-pressure helper's own
    monotonicity precondition.
    """
    instance = _instance(
        attackers=["France"],
        defenders=["Austria", "Prussia"],
    )

    base_world = _build_world_with_war_pair(
        pairs={
            ("France", "Austria"): 30,
            ("France", "Prussia"): 30,
        }
    )
    higher_world = _build_world_with_war_pair(
        pairs={
            ("France", "Austria"): 50,  # bumped
            ("France", "Prussia"): 30,
        }
    )

    base = compute_side_pressure_score(
        base_world,
        instance,
        proposer_side="attackers",
        covered_enemy_participants=["Austria", "Prussia"],
    )
    higher = compute_side_pressure_score(
        higher_world,
        instance,
        proposer_side="attackers",
        covered_enemy_participants=["Austria", "Prussia"],
    )

    assert higher["score"] >= base["score"]
    assert higher["score"] > base["score"]  # strict — only one input changed


def test_caller_supplied_direct_scores_skip_recomputation_on_world():
    """Spec line 238: settlement preview / confirm pass a pre-computed
    `direct_scores` map so a single evaluation walks war scores at most
    once. Prove the helper trusts the caller's map by mutating
    `world.war_scores` after building the map and observing the result is
    NOT recomputed.
    """
    world = _build_world_with_war_pair(
        pairs={("France", "Austria"): 40},
    )
    instance = _instance(attackers=["France"], defenders=["Austria"])

    direct = compute_direct_scores_by_enemy(
        world,
        instance,
        proposer_side="attackers",
        covered_enemy_participants=["Austria"],
    )
    assert direct["Austria"] == {"France": 40}

    # After caching the map, mutate war_scores. A correct memoization
    # contract means the side-pressure helper trusts the cached map.
    key = world._make_diplo_key("France", "Austria")
    world.war_scores[key] = 999  # would otherwise lift the score

    result = compute_side_pressure_score(
        world,
        instance,
        proposer_side="attackers",
        covered_enemy_participants=["Austria"],
        direct_scores=direct,
    )

    # If the helper recomputed, score would clamp to 100. Trusting the
    # supplied map means it stays at 40.
    assert result["score"] == 40


def test_proposer_side_member_at_peace_with_enemy_is_excluded():
    """Spec §6.3 `if world.is_at_war(side_member, enemy)`: if a proposer-
    side member never declared / has separately peaced with the covered
    enemy, that pair is not counted toward `direct_score`.
    """
    world = _build_world_with_war_pair(
        pairs={
            ("France", "Austria"): 30,
            ("Bavaria", "Austria"): 70,  # PEACE — separate-peaced ally
        },
        states={
            ("France", "Austria"): "WAR",
            ("Bavaria", "Austria"): "PEACE",
        },
    )
    instance = _instance(
        attackers=["France", "Bavaria"],
        defenders=["Austria"],
    )

    result = compute_side_pressure_score(
        world,
        instance,
        proposer_side="attackers",
        covered_enemy_participants=["Austria"],
    )

    assert result["direct_scores"]["Austria"] == {"France": 30}
    assert result["direct_score_sources"]["Austria"]["source"] == "France"
    assert result["score"] == 30


def test_invalid_proposer_side_raises_value_error():
    """Defensive: typo'd side string should fail loud, not silently return
    a zero-pressure score (which would mask a settlement bug)."""
    world = _build_world_with_war_pair(pairs={("France", "Austria"): 30})
    instance = _instance(attackers=["France"], defenders=["Austria"])

    with pytest.raises(ValueError, match="proposer_side"):
        compute_side_pressure_score(
            world,
            instance,
            proposer_side="aggressors",  # typo
            covered_enemy_participants=["Austria"],
        )
