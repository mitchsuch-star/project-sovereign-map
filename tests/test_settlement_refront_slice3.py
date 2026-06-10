"""Settlement Conversational Re-front — Slice 3 behavior tests
(GT-Slice-4 re-home: the Tier-3 editor surfaces are retired).

`docs/SETTLEMENT_CONVERSATIONAL_REFRONT_SPEC.md` v0.6 §14 Slice 3 — what
survives GT-Slice-4 (the freeform editor, its picker schema, the REFRONT-8
consumption pins, and the DWL-SET-SC5R-3 merge-conflict controls were all
deleted with the editor; the guided per-court rows are the deep tier):

- The PROPOSE rail carries NO `adjust_terms` and no editor contract; the
  presentation-only court focus (REFRONT-9's transport) still carries.
- Multi-party cross-court validity V1-V3 in `validate_settlement_terms` (§12):
  V1 `region_double_promised`, V2 `clause_target_uncovered`,
  V3 `clause_side_mismatch`. (V4 self-reference + V5 coverage floor already
  land in Slice 0 / Slice 2 and are exercised there.)
- Ratify-time defense in depth re-runs the validator against the live world.
- The `CLAUSE_CONFLICT_MATRIX` authority names both offending indices.
"""

from __future__ import annotations

from unittest.mock import patch

from backend.game_logic.settlement_preview import (
    handle_settlement_dialogue_action,
    ratify_settlement_confirm,
    stage_settlement_confirm,
    validate_settlement_terms,
)
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import (
    make_synthetic_war_instance,
)

_SCORER_PATH = "backend.game_logic.settlement_preview.calculate_common_peace_acceptance"


# ===========================================================================
# Helpers
# ===========================================================================


def _set_war_score(world: WorldState, frm: str, to: str, score: int) -> None:
    key = world._make_diplo_key(frm, to)
    world.diplomatic_states[key] = "WAR"
    if sorted([frm, to])[0] == frm:
        world.war_scores[key] = int(score)
    else:
        world.war_scores[key] = -int(score)


def _three_court_world():
    """France (attacker) vs Britain + Prussia + Austria (defenders)."""
    world = WorldState()
    inst = make_synthetic_war_instance(
        "war_rf",
        attackers=["France"],
        defenders=["Britain", "Prussia", "Austria"],
        attacker_leader="France",
        defender_leader="Austria",
    )
    world.war_instances["war_rf"] = inst
    _set_war_score(world, "France", "Prussia", 70)
    _set_war_score(world, "France", "Britain", -70)
    _set_war_score(world, "France", "Austria", 0)
    world.invalidate_war_instance_indexes()
    return world, inst


def _accept_scorer(world=None, *, accepting_leader=None, **kwargs):
    return {
        "score": 60,
        "verdict": "accept",
        "components": {},
        "component_debug": {},
        "feedback": [],
        "hard_stops": [],
        "accept_threshold": 50,
        "near_acceptable_threshold": 35,
        "side_pressure_score": 30,
        "raw_total": 60,
        "raw_total_harshness": 0.0,
        "direct_scores": {},
        "direct_score_sources": {},
    }


def _stage_propose(world, *, terms=None, covered=None):
    with patch(_SCORER_PATH, side_effect=_accept_scorer):
        staged = stage_settlement_confirm(
            world,
            war_id="war_rf",
            actor_nation="France",
            settlement_terms=terms or [{"type": "peace"}],
            covered_enemy_participants=covered or ["Britain", "Prussia", "Austria"],
            selected_target_nation="Austria",
            caller_kind="player_editor",
            dialogue_mode="PROPOSE",
        )
    assert staged.get("success"), staged
    return staged["diplomatic_dialogue"]


# ===========================================================================
# 1. PROPOSE rail carries no editor (GT-Slice-4); court focus still carries
# ===========================================================================


def test_propose_rail_offers_no_adjust_terms_and_focus_carries():
    """GT-Slice-4: the PROPOSE rail no longer offers `adjust_terms` and the
    dialogue carries no editor contract — the guided per-court rows are the
    deep tier. The presentation-only court focus (REFRONT-9's transport)
    still carries `focused_court` across the restage."""
    world, _ = _three_court_world()
    dialogue = _stage_propose(world)
    assert dialogue.get("dialogue_mode") == "PROPOSE"
    rail = set(dialogue.get("available_action_ids") or [])
    option_actions = {o.get("action") for o in (dialogue.get("options") or [])}
    assert "adjust_terms" not in rail
    assert "adjust_terms" not in option_actions
    for retired_key in (
        "can_edit_terms",
        "editor_route",
        "available_clause_types",
        "clause_control_schema",
    ):
        assert retired_key not in dialogue, retired_key
    assert dialogue.get("focused_court") in (None, "")

    with patch(_SCORER_PATH, side_effect=_accept_scorer):
        focused = handle_settlement_dialogue_action(
            world,
            action="settlement_focus_court",
            dialogue=dialogue,
            action_params={"nation": "Prussia"},
        )
    assert focused.get("success"), focused
    fdlg = focused["diplomatic_dialogue"]
    assert fdlg.get("focused_court") == "Prussia"
    assert "can_edit_terms" not in fdlg


# ===========================================================================
# 2-4. Multi-party cross-court validity rules (§12 V1-V3)
# ===========================================================================


def test_no_region_promised_to_two_courts():
    """V1 — a region may appear in at most one territory_cede clause."""
    _, inst = _three_court_world()
    result = validate_settlement_terms(
        [
            {"type": "territory_cede", "from": "Britain", "to": "France", "region": "Hanover"},
            {"type": "territory_cede", "from": "Prussia", "to": "France", "region": "Hanover"},
        ],
        war_instance=inst,
        proposer_side="attackers",
        covered_enemy_participants=["Britain", "Prussia", "Austria"],
    )
    assert result["valid"] is False
    assert result["error"] == "region_double_promised"
    # Both offending clause indices are named so the editor can resolve.
    assert result["error_index"] == 1
    assert result["conflicting_index"] == 0
    assert result.get("disabled_reason_display")

    # A single promise of the same region is valid.
    ok = validate_settlement_terms(
        [{"type": "territory_cede", "from": "Britain", "to": "France", "region": "Hanover"}],
        war_instance=inst,
        proposer_side="attackers",
        covered_enemy_participants=["Britain", "Prussia", "Austria"],
    )
    assert ok["valid"] is True


def test_clause_cannot_bind_uncovered_court():
    """V2 — a clause may not bind an enemy court outside the covered set."""
    _, inst = _three_court_world()
    # Prussia is NOT covered; a clause naming it must reject.
    result = validate_settlement_terms(
        [{"type": "territory_cede", "from": "Prussia", "to": "France", "region": "Hanover"}],
        war_instance=inst,
        proposer_side="attackers",
        covered_enemy_participants=["Britain"],
    )
    assert result["valid"] is False
    assert result["error"] == "clause_target_uncovered"
    assert result.get("uncovered_nation") == "Prussia"

    # Covering Prussia makes the same clause bindable (V3 still applies to
    # from/to sides, which here are correct: Prussia=defender, France=attacker).
    ok = validate_settlement_terms(
        [{"type": "territory_cede", "from": "Prussia", "to": "France", "region": "Hanover"}],
        war_instance=inst,
        proposer_side="attackers",
        covered_enemy_participants=["Britain", "Prussia"],
    )
    assert ok["valid"] is True


def test_clause_from_to_must_match_war_sides():
    """V3 — a value-transfer clause must straddle opposite war sides."""
    _, inst = _three_court_world()
    # Britain and Prussia are both defenders — a transfer between them is a
    # same-side clause and must reject even though both are covered.
    result = validate_settlement_terms(
        [{"type": "territory_cede", "from": "Britain", "to": "Prussia", "region": "Hanover"}],
        war_instance=inst,
        proposer_side="attackers",
        covered_enemy_participants=["Britain", "Prussia", "Austria"],
    )
    assert result["valid"] is False
    assert result["error"] == "clause_side_mismatch"

    # A self-referential transfer (from == to) is the degenerate same-side
    # case V3 also catches (kills "France pays France").
    self_ref = validate_settlement_terms(
        [{"type": "gold_indemnity", "from": "France", "to": "France", "amount": 100}],
        war_instance=inst,
        proposer_side="attackers",
        covered_enemy_participants=["Britain", "Prussia", "Austria"],
    )
    assert self_ref["valid"] is False
    assert self_ref["error"] == "clause_side_mismatch"


def test_submit_revalidation_enforces_uncovered_court_defense_in_depth():
    """§12 defense-in-depth (GT-Slice-4 re-home): the guided Submit-for-Review
    arm re-runs V2 with the covered set, so a tampered staged package binding
    an uncovered court is rejected at Submit — and the failure re-attaches the
    mounted PROPOSE dialogue with a rendered reason (PF-1/CH-5), never a
    silent dead end."""
    world, _ = _three_court_world()
    with patch(_SCORER_PATH, side_effect=_accept_scorer):
        staged = stage_settlement_confirm(
            world,
            war_id="war_rf",
            actor_nation="France",
            settlement_terms=[{"type": "peace"}],
            covered_enemy_participants=["Britain"],
            selected_target_nation="Britain",
            caller_kind="player_editor",
            dialogue_mode="PROPOSE",
        )
    assert staged.get("success"), staged
    dialogue = staged["diplomatic_dialogue"]
    # Tamper the STAGED draft to bind uncovered Prussia (bypasses authoring).
    dialogue["settlement_terms"] = [
        {"type": "territory_cede", "from": "Prussia", "to": "France", "region": "Hanover"},
    ]
    with patch(_SCORER_PATH, side_effect=_accept_scorer):
        result = handle_settlement_dialogue_action(
            world,
            action="submit_settlement_for_review",
            dialogue=dialogue,
        )
    assert result.get("success") is False
    assert result.get("error") == "submitted_terms_failed_revalidation"
    assert result.get("validation_error") == "clause_target_uncovered"
    # CH-5 failure contract: the dialogue is re-attached with a reason.
    assert result.get("diplomatic_dialogue")
    assert result.get("error_display")


def test_ratify_blocks_staged_liberation_after_live_lord_drift():
    """§12 defense-in-depth at the RATIFY gate (CRITICAL audit fix).

    A liberation that is valid when staged (Saxony's lord is the covered enemy
    Britain) must NOT ratify after the world drifts so Saxony's live lord is a
    DIFFERENT, uncovered court (Prussia). Before this gate the apply path called
    `release_vassal(Saxony)` and freed Saxony from whatever its CURRENT lord was
    — mutating the uncovered party. The ratify-time revalidation now rejects the
    stale package via `evaluate_liberation_eligibility` (current_lord !=
    staged lord_nation) and no vassal is released.
    """
    world = WorldState()
    war = make_synthetic_war_instance(
        "war_lib",
        attackers=["Britain", "Prussia"],
        defenders=["France"],
        attacker_leader="Britain",
        defender_leader="France",
    )
    world.war_instances["war_lib"] = war
    for pair in war["active_diplo_keys"]:
        world.diplomatic_states[pair] = "WAR"
        world.war_scores[pair] = -100 if pair.split("|")[0] == "France" else 100
    world.invalidate_war_instance_indexes()
    # Saxony is Britain's vassal at the moment the liberation is staged.
    world.vassals["Saxony"] = {
        "lord": "Britain", "loyalty": 50, "autonomy": 1,
        "path": "treaty", "tribute_rate": 0.5,
    }
    terms = [
        {"type": "peace"},
        {
            "type": "liberation",
            "vassal_nation": "Saxony",
            "lord_nation": "Britain",
            "liberator": "France",
        },
    ]
    with patch(_SCORER_PATH, side_effect=_accept_scorer):
        staged = stage_settlement_confirm(
            world,
            war_id="war_lib",
            settlement_terms=terms,
            covered_enemy_participants=["Britain"],
        )
    assert staged.get("success"), staged
    dialogue = world.pending_diplomatic_dialogue

    # World drifts under the staged package: Saxony's live lord is now the
    # UNCOVERED court Prussia (e.g. a rebellion/transfer between stage and
    # ratify, or a save-loaded draft against a changed world).
    world.vassals["Saxony"]["lord"] = "Prussia"

    with patch(_SCORER_PATH, side_effect=_accept_scorer):
        result = ratify_settlement_confirm(world, dialogue)

    assert result.get("success") is False, result
    assert result.get("error") == "submitted_terms_failed_revalidation"
    assert result.get("validation_error") == "liberation_lord_mismatch"
    assert result.get("mutated") is False
    # The uncovered party's vassal was NOT released — no state mutation.
    assert "Saxony" in world.vassals
    assert world.vassals["Saxony"]["lord"] == "Prussia"


def test_ratify_normalizes_apply_format_terms_so_valid_package_still_ratifies():
    """The ratify-time revalidation normalizes apply-format staged terms
    (`gold_lump` -> `gold_indemnity`, plural `regions` -> single `region`) and
    skips the authoring-only solvency gate, so a legitimately-staged
    apply-format package still ratifies and mutates (no regression to the C2
    fixtures' clamp/plural behavior)."""
    world = WorldState()
    war = make_synthetic_war_instance(
        "war_norm",
        attackers=["France"],
        defenders=["Britain", "Prussia"],
        attacker_leader="France",
        defender_leader="Britain",
    )
    world.war_instances["war_norm"] = war
    for pair in war["active_diplo_keys"]:
        world.diplomatic_states[pair] = "WAR"
        world.war_scores[pair] = 100 if pair.split("|")[0] == "France" else -100
    world.invalidate_war_instance_indexes()
    # Britain owes more than it holds — the apply path clamps, the solvency gate
    # must NOT block at ratify.
    world.nation_gold["Britain"] = 40
    world.nation_gold["France"] = 0
    terms = [
        {"type": "peace"},
        {"type": "gold_lump", "from": "Britain", "to": "France", "amount": 500},
    ]
    with patch(_SCORER_PATH, side_effect=_accept_scorer):
        staged = stage_settlement_confirm(
            world,
            war_id="war_norm",
            settlement_terms=terms,
            covered_enemy_participants=["Britain"],
        )
        assert staged.get("success"), staged
        dialogue = world.pending_diplomatic_dialogue
        result = ratify_settlement_confirm(world, dialogue)
    assert result.get("success") is True, result
    assert result.get("mutated") is True
    # Clamped to Britain's available balance, not blocked.
    assert world.nation_gold["Britain"] == 0
    assert world.nation_gold["France"] == 40


# ===========================================================================
# 5. Conflict-matrix authority names both offending indices
# ===========================================================================


def test_merge_conflict_backend_authority_returns_conflicting_index():
    """Behavioral pin for the authority the client mirror is checked against.

    The GDScript Discard/Replace state transitions cannot run in pytest (the
    project has no GDScript runtime harness — hence the source-grep pins above),
    so this asserts the BACKEND authority they mirror: `validate_settlement_terms`
    rejects a `CLAUSE_CONFLICT_MATRIX` pair (vassalage + forced_alliance on the
    same from/to) with the `error_index` + `conflicting_index` parity that the
    inline merge-conflict resolution relies on. This runs before the world-
    dependent V1–V3 checks, so it needs no world/war_instance."""
    result = validate_settlement_terms([
        {"type": "vassalage", "from": "Saxony", "to": "France"},
        {"type": "forced_alliance", "from": "Saxony", "to": "France"},
    ])
    assert result["valid"] is False
    assert result["error"] == "duplicate_or_conflicting_clauses"
    # Parity with the V1 region rule: both offending indices are named so the
    # client can offer Discard new (error_index) / Replace active (conflicting).
    assert result["error_index"] == 1
    assert result["conflicting_index"] == 0
