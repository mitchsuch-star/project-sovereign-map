"""PF-3 — Gate-4 pre-flight audit §6: the standing scenario-matrix harness.

The decisive test gap behind D1–D3: no test built a two-concede-court table
with the real scorer, so six doc audits missed an invalid-by-construction
losing baseline that any fixture run would have caught ("a spec audit
verifies the map; only a fixture verifies the territory" — DC-6).

This suite is the systemic guard: every cell of
``direction {winning, losing, mixed} × covered courts {1, 2, 3} ×
treasury {rich, poor}`` drives the REAL generator, validator, scorer, and
Tier-2 verbs (no acceptance patching) and asserts:

(a) the generated baseline passes ``validate_settlement_terms``;
(b) the staged dialogue's ``overall_acceptance.carries`` claim matches a
    fresh ``compute_per_court_acceptance`` pass over the staged terms;
(c) every Tier-2 verb on the resulting table either succeeds or returns a
    re-attached ``diplomatic_dialogue`` + ``error_display`` (the CH-5
    invariant: never a silent no-op, never an orphaned popup).
"""

from __future__ import annotations

import pytest

from backend.game_logic.settlement_preview import (
    compute_per_court_acceptance,
    compute_settlement_baseline,
    handle_settlement_dialogue_action,
    stage_settlement_confirm,
    validate_settlement_terms,
)
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import (
    make_synthetic_war_instance,
)

DIRECTIONS = ("winning", "losing", "mixed")
COURT_COUNTS = (1, 2, 3)
TREASURIES = {"rich": 5000, "poor": 600}
DEFENDER_POOL = ("Britain", "Prussia", "Austria")
DIRECT_SCORE_MAGNITUDE = 60


def _set_pair_score_for_france(world, opponent: str, score_for_france: int):
    pair = "|".join(sorted(("France", opponent)))
    first = pair.split("|")[0]
    world.war_scores[pair] = (
        score_for_france if first == "France" else -score_for_france
    )


def _build_matrix_world(direction: str, court_count: int, treasury: int):
    """One matrix cell: a France-led shared multi-party war on the canonical
    campaign world (real regions, real scorer inputs), with per-pair scores
    set by `direction`.

    `court_count` is the COVERED court count, not the war size: a strictly
    one-on-one war is settlement-ineligible by design (`one_to_one_war` —
    bilateral peace owns that surface), so the n=1 cell covers one court of
    a two-defender war (the spec's "n=1 collapses to the leader row").
    Returns ``(world, war, covered_courts)``.
    """
    world = WorldState()
    defenders = list(DEFENDER_POOL[: max(2, court_count)])
    covered = defenders[:court_count]
    war = make_synthetic_war_instance(
        "war_1",
        attackers=["France"],
        defenders=defenders,
        attacker_leader="France",
        defender_leader=defenders[0],
        created_turn=1,
        created_sequence=1,
    )
    world.war_instances["war_1"] = war
    for idx, opponent in enumerate(defenders):
        pair = "|".join(sorted(("France", opponent)))
        world.diplomatic_states[pair] = "WAR"
        if direction == "winning":
            score = DIRECT_SCORE_MAGNITUDE
        elif direction == "losing":
            score = -DIRECT_SCORE_MAGNITUDE
        else:  # mixed — alternate lead/pressed pair by pair
            score = DIRECT_SCORE_MAGNITUDE if idx % 2 == 0 else -DIRECT_SCORE_MAGNITUDE
        _set_pair_score_for_france(world, opponent, score)
    world.nation_gold["France"] = int(treasury)
    world.invalidate_war_instance_indexes()
    return world, war, covered


MATRIX_CELLS = [
    pytest.param(direction, courts, treasury_name, id=f"{direction}-{courts}court-{treasury_name}")
    for direction in DIRECTIONS
    for courts in COURT_COUNTS
    for treasury_name in TREASURIES
]


@pytest.mark.parametrize("direction,court_count,treasury_name", MATRIX_CELLS)
def test_generated_baseline_validates_and_carry_claim_is_honest(
    direction, court_count, treasury_name,
):
    """Matrix assertions (a) + (b): valid-by-construction baseline and an
    honest carries claim, for every direction × coverage × treasury cell."""
    world, war, covered = _build_matrix_world(
        direction, court_count, TREASURIES[treasury_name],
    )

    # (a) the generated baseline passes the authoring validator.
    baseline = compute_settlement_baseline(
        world,
        war_id="war_1",
        war_instance=war,
        proposer_side="attackers",
        accepting_side="defenders",
        proposer_side_leader="France",
        covered_enemy_participants=covered,
    )
    terms = baseline["settlement_terms"]
    validation = validate_settlement_terms(
        terms,
        proposer_side="attackers",
        covered_enemy_participants=covered,
        world=world,
        war_instance=war,
    )
    assert validation.get("valid"), (validation, terms)
    # Structural duplicates of the D1 classes, asserted directly so a
    # validator regression cannot mask them: one region promised once,
    # gold within the payer's balance.
    regions = [t.get("region") for t in terms if t.get("type") == "territory_cede"]
    assert len(regions) == len(set(regions)), regions
    committed = sum(
        int(t.get("amount", 0) or 0)
        for t in terms
        if t.get("type") in ("gold_indemnity", "gold_lump")
        and t.get("from") == "France"
    )
    assert committed <= int(world.nation_gold.get("France", 0)), terms

    # (b) the staged PROPOSE dialogue's carries claim matches a fresh
    # scorer pass over the exact staged terms.
    staged = stage_settlement_confirm(
        world,
        war_id="war_1",
        actor_nation="France",
        selected_target_nation=covered[0],
        covered_enemy_participants=covered,
        caller_kind="player_editor",
        dialogue_mode="PROPOSE",
    )
    assert staged.get("success"), staged
    dialogue = staged["diplomatic_dialogue"]
    claimed = dialogue.get("overall_acceptance") or {}
    fresh = compute_per_court_acceptance(
        world,
        war_id="war_1",
        war_instance=war,
        proposer_side="attackers",
        accepting_side="defenders",
        proposer_side_leader="France",
        covered_enemy_participants=list(
            dialogue.get("covered_enemy_participants") or []
        ),
        settlement_terms=list(dialogue.get("settlement_terms") or []),
    )["overall_acceptance"]
    assert bool(claimed.get("carries")) == bool(fresh.get("carries")), (
        claimed, fresh,
    )
    assert list(claimed.get("holdout_courts") or []) == list(
        fresh.get("holdout_courts") or []
    )


@pytest.mark.parametrize("direction,court_count,treasury_name", MATRIX_CELLS)
def test_every_tier2_verb_succeeds_or_renders_its_failure(
    direction, court_count, treasury_name,
):
    """Matrix assertion (c): no Tier-2 verb on any cell's table may produce
    a silent no-op — each either succeeds (new dialogue attached) or fails
    with a re-attached dialogue AND a rendered error_display."""
    world, war, covered = _build_matrix_world(
        direction, court_count, TREASURIES[treasury_name],
    )
    staged = stage_settlement_confirm(
        world,
        war_id="war_1",
        actor_nation="France",
        selected_target_nation=covered[0],
        covered_enemy_participants=covered,
        caller_kind="player_editor",
        dialogue_mode="PROPOSE",
    )
    assert staged.get("success"), staged

    verb_calls = [
        ("settlement_dial_harsher", {"scope": "table"}),
        ("settlement_dial_generous", {"scope": "table"}),
        ("settlement_focus_court", {"nation": covered[0]}),
        # Drop the last covered court: succeeds for n>1, V5-blocked for n=1.
        ("settlement_cover_drop", {"nation": covered[-1]}),
        # Re-add a court (the dropped one, or the uncovered defender at
        # n=1) — exercises the coverage-add redraw leg.
        ("settlement_cover_add", {
            "nation": covered[-1] if court_count > 1 else DEFENDER_POOL[1],
        }),
        # A dial scoped to a court that is not at the table must render
        # its rejection, never blink.
        ("settlement_dial_generous", {"scope": "Denmark"}),
    ]
    for verb, params in verb_calls:
        mounted = world.dialogue_manager.peek()
        assert mounted is not None, f"dialogue lost before {verb}"
        result = handle_settlement_dialogue_action(
            world,
            action=verb,
            dialogue=mounted,
            action_params={"action": verb, **params},
        )
        if result.get("success"):
            assert result.get("diplomatic_dialogue"), (
                f"{verb} succeeded without re-attaching a dialogue"
            )
        else:
            assert result.get("diplomatic_dialogue"), (
                f"{verb} failed without re-attaching the dialogue "
                f"(orphaned popup): {result}"
            )
            assert result.get("error_display"), (
                f"{verb} failed silently (no error_display): {result}"
            )
        # The mounted surface survives every verb (PROPOSE is never lost).
        assert world.dialogue_manager.peek() is not None, (
            f"{verb} left no mounted settlement dialogue"
        )
