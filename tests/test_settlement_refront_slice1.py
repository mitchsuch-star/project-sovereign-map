"""Settlement Conversational Re-front — Slice 1 behavior tests.

`docs/SETTLEMENT_CONVERSATIONAL_REFRONT_SPEC.md` v0.6 §14 Slice 1:
Tier-1 multi-party baseline (`compute_settlement_baseline`, per-court
direction — §8 OQ#5), the PROPOSE surface + `per_court_acceptance` /
`overall_acceptance` payload (§11.2), the per-covered-court ratification gate
(§11.4), holdout ease/drop affordances, PROPOSE non-blocking + Back Out draft
preservation (§10), and PROPOSE replacing the blank-EDIT landing (§3a).

Direction is verified with the REAL scorer (it is deterministic from each
court's `direct_score`); exact per-court acceptance bands are pinned with a
patched scorer because `base_side_pressure` is package-level (§11.2), so a
mixed synthetic war with no configured war objectives scores every court
alike.
"""

from __future__ import annotations

from unittest.mock import patch

from backend.commands.diplomatic_executor import DiplomaticExecutor
from backend.game_logic.settlement_preview import (
    DIRECT_SCORE_DIRECTION_MARGIN,
    LOSING_SIDE_PRESSURE_THRESHOLD,
    build_settlement_confirm_dialogue,
    build_settlement_preview,
    compute_per_court_acceptance,
    compute_settlement_baseline,
    handle_settlement_dialogue_action,
    load_scoped_settlement_draft,
    ratify_settlement_confirm,
    stage_settlement_confirm,
    validate_settlement_terms,
)
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import (
    make_synthetic_war_instance,
)


# ===========================================================================
# Helpers
# ===========================================================================


def _set_war_score(world: WorldState, frm: str, to: str, score: int) -> None:
    """Mark (frm, to) at WAR and set war score so get_war_score_for(frm, to)
    == score (matching the canonical synthetic-fixture sign convention)."""
    key = world._make_diplo_key(frm, to)
    world.diplomatic_states[key] = "WAR"
    if sorted([frm, to])[0] == frm:
        world.war_scores[key] = int(score)
    else:
        world.war_scores[key] = -int(score)


def _three_court_world(
    *,
    prussia: int = 70,
    britain: int = -70,
    austria: int = 0,
    defender_leader: str = "Austria",
    stamp_all_war: bool = True,
):
    """France (attacker) vs Britain + Prussia + Austria (defenders).

    Positive score => France leads that court (demand direction); negative =>
    France is pressured (concede); near-zero => dead-band (peace floor).
    """
    world = WorldState()
    inst = make_synthetic_war_instance(
        "war_rf",
        attackers=["France"],
        defenders=["Britain", "Prussia", "Austria"],
        attacker_leader="France",
        defender_leader=defender_leader,
    )
    world.war_instances["war_rf"] = inst
    if stamp_all_war:
        _set_war_score(world, "France", "Prussia", prussia)
        _set_war_score(world, "France", "Britain", britain)
        _set_war_score(world, "France", "Austria", austria)
    world.invalidate_war_instance_indexes()
    return world, inst


def _baseline(world, inst, covered=None):
    return compute_settlement_baseline(
        world,
        war_id="war_rf",
        war_instance=inst,
        proposer_side="attackers",
        accepting_side="defenders",
        proposer_side_leader="France",
        covered_enemy_participants=covered or ["Britain", "Prussia", "Austria"],
    )


def _make_scorer(score_by_leader: dict, default: int = 60):
    """Patched `calculate_common_peace_acceptance` keyed on accepting_leader."""

    def _side_effect(world=None, *, accepting_leader=None, **kwargs):
        score = score_by_leader.get(accepting_leader, default)
        if score is None:
            verdict = "reject"
        elif score >= 50:
            verdict = "accept"
        elif score >= 35:
            verdict = "near_acceptable"
        else:
            verdict = "reject"
        return {
            "score": score,
            "verdict": verdict,
            "components": {},
            "component_debug": {},
            "feedback": [],
            "hard_stops": [],
            "accept_threshold": 50,
            "near_acceptable_threshold": 35,
            "side_pressure_score": 30,
            "raw_total": score if score is not None else 0,
            "raw_total_harshness": 0.0,
            "direct_scores": {},
            "direct_score_sources": {},
        }

    return _side_effect


# ===========================================================================
# Baseline direction (§8 OQ#5) — real scorer, deterministic from direct_score
# ===========================================================================


def test_settlement_baseline_demands_from_winning_courts_concedes_to_losing():
    world, inst = _three_court_world(prussia=70, britain=-70, austria=0)
    baseline = _baseline(world, inst)
    pcb = baseline["per_court_baseline"]

    # Direction is chosen per court from each court's direct score.
    assert pcb["Prussia"]["direction"] == "demand"
    # Demands (when suggested) are levied FROM the led court — never a
    # concession TO it. The floor-aware baseline (R6-M1) may suppress the
    # demand entirely in a mixed war where the shared package pressure already
    # depresses the led court below the near-acceptance floor; a real demand
    # term IS produced when the court can absorb it (pinned by
    # test_demand_baseline_keeps_winning_court_at_or_above_near_acceptance_floor).
    assert all(t.get("from") == "Prussia" for t in pcb["Prussia"]["terms"]), pcb
    # Never demand FROM a losing court; concessions flow TO it.
    assert pcb["Britain"]["direction"] == "concede"
    assert all(t.get("from") != "Britain" for t in pcb["Britain"]["terms"])
    assert all(
        t.get("to") == "Britain" or t.get("type") == "peace"
        for t in pcb["Britain"]["terms"]
    )
    assert pcb["Austria"]["direction"] == "peace"
    assert pcb["Austria"]["terms"] == []


def test_settlement_baseline_per_court_direction_uses_per_court_direct_score_not_side_pressure():
    # France is crushed at sea by Britain (huge negative) but decisively leads
    # weak Prussia. The package side-pressure scalar is dominated by the
    # Britain loss, yet Prussia must still be DEMAND because direction reads
    # Prussia's own direct score, not the package scalar.
    world, inst = _three_court_world(prussia=80, britain=-95, austria=-90)
    baseline = _baseline(world, inst)
    pcb = baseline["per_court_baseline"]
    # The package side pressure is clearly negative (two heavy losses)...
    from backend.game_logic.settlement_scoring import compute_side_pressure_score

    sp = compute_side_pressure_score(
        world, inst, proposer_side="attackers",
        covered_enemy_participants=["Britain", "Prussia", "Austria"],
    )
    assert sp["score"] is not None and sp["score"] < 0, sp
    # ...yet Prussia is demanded from (per-court direct score +80), while the
    # courts France trails are conceded to.
    assert pcb["Prussia"]["direction"] == "demand"
    assert pcb["Britain"]["direction"] == "concede"
    assert pcb["Austria"]["direction"] == "concede"


def test_per_court_direction_threshold_is_war_score_margin_not_side_pressure_constant():
    # A court with direct_score = -15 sits BETWEEN the war-score direction
    # margin (10) and the side-pressure constant (|-20|). With the correct
    # DIRECT_SCORE_DIRECTION_MARGIN it is a CONCEDE court; if the code wrongly
    # thresholded on LOSING_SIDE_PRESSURE_THRESHOLD (-20) it would fall in the
    # dead-band and be peace-floored.
    assert DIRECT_SCORE_DIRECTION_MARGIN < abs(LOSING_SIDE_PRESSURE_THRESHOLD)
    world, inst = _three_court_world(prussia=70, britain=-15, austria=5)
    pcb = _baseline(world, inst)["per_court_baseline"]
    assert pcb["Britain"]["direction"] == "concede", pcb["Britain"]
    # Austria at +5 is inside the +/-10 margin => peace, not demand.
    assert pcb["Austria"]["direction"] == "peace", pcb["Austria"]


def test_settlement_baseline_court_with_no_demand_or_concession_uses_peace_floor():
    world, inst = _three_court_world(prussia=70, britain=-70, austria=4)
    pcb = _baseline(world, inst)["per_court_baseline"]
    assert pcb["Austria"]["direction"] == "peace"
    assert pcb["Austria"]["terms"] == []
    # The neutral court still rides the shared package {"type": "peace"} floor.
    assert {"type": "peace"} in _baseline(world, inst)["settlement_terms"]


def test_settlement_baseline_no_direct_score_court_is_hard_stopped_not_peace_floored():
    # Russia is covered but has no WAR pair with any proposer member, so
    # select_direct_score returns None -> per-court hard stop, NOT peace floor.
    world, inst = _three_court_world(prussia=70, britain=-70, austria=0)
    covered = ["Britain", "Prussia", "Austria", "Russia"]
    baseline = _baseline(world, inst, covered=covered)
    pcb = baseline["per_court_baseline"]
    assert pcb["Russia"]["direction"] == "hard_stop"
    assert pcb["Russia"]["direct_score"] is None
    assert pcb["Russia"]["terms"] == []
    assert "Russia" in baseline["hard_stop_courts"]
    # And it is distinct from a dead-band peace court.
    assert pcb["Russia"]["direction"] != "peace"


def test_settlement_baseline_suggestions_are_valid_by_construction():
    world, inst = _three_court_world(prussia=70, britain=-70, austria=0)
    terms = _baseline(world, inst)["settlement_terms"]
    result = validate_settlement_terms(terms, world=world, war_instance=inst)
    assert result.get("valid") is True, result


def test_settlement_baseline_is_deterministic_same_world_same_terms():
    w1, i1 = _three_court_world(prussia=70, britain=-70, austria=0)
    w2, i2 = _three_court_world(prussia=70, britain=-70, austria=0)
    assert _baseline(w1, i1)["settlement_terms"] == _baseline(w2, i2)["settlement_terms"]


# ===========================================================================
# PROPOSE payload (§11.2) + per-court call signature
# ===========================================================================


def test_propose_mode_payload_shape_per_court_and_overall():
    world, inst = _three_court_world(prussia=70, britain=-70, austria=0)
    block = compute_per_court_acceptance(
        world, war_id="war_rf", war_instance=inst,
        proposer_side="attackers", accepting_side="defenders",
        proposer_side_leader="France",
        covered_enemy_participants=["Britain", "Prussia", "Austria"],
        settlement_terms=[{"type": "peace"}],
    )
    per_court = block["per_court_acceptance"]
    assert {r["nation"] for r in per_court} == {"Britain", "Prussia", "Austria"}
    required = {
        "nation", "band", "band_display", "total", "threshold", "verdict",
        "top_blocker_display", "direction_summary", "previous_band",
        "delta_display", "hard_stops",
    }
    for row in per_court:
        assert required <= set(row), row
    overall = block["overall_acceptance"]
    assert set(overall) == {"carries", "holdout_courts", "summary_display"}
    assert isinstance(overall["carries"], bool)


def test_per_court_call_varies_leader_and_holdings_holds_covered_set():
    world, inst = _three_court_world(prussia=70, britain=-70, austria=0)
    seen = []

    def _spy(world=None, *, accepting_leader=None, covered_enemy_participants=None, **kw):
        seen.append((accepting_leader, sorted(covered_enemy_participants or [])))
        return _make_scorer({})(world, accepting_leader=accepting_leader, **kw)

    with patch(
        "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
        side_effect=_spy,
    ):
        compute_per_court_acceptance(
            world, war_id="war_rf", war_instance=inst,
            proposer_side="attackers", accepting_side="defenders",
            proposer_side_leader="France",
            covered_enemy_participants=["Britain", "Prussia", "Austria"],
            settlement_terms=[{"type": "peace"}],
        )
    leaders = sorted(leader for leader, _ in seen)
    assert leaders == ["Austria", "Britain", "Prussia"]
    full = ["Austria", "Britain", "Prussia"]
    assert all(covered == full for _, covered in seen), seen


# ===========================================================================
# Per-court ratification gate (§11.4)
# ===========================================================================


def _stage_review(world, terms, *, scorer=None):
    if scorer is None:
        scorer = _make_scorer({})
    with patch(
        "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
        side_effect=scorer,
    ):
        return stage_settlement_confirm(
            world, war_id="war_rf", actor_nation="France",
            settlement_terms=terms,
            selected_target_nation="Austria",
            covered_enemy_participants=["Britain", "Prussia", "Austria"],
            caller_kind="player_editor",
            dialogue_mode="REVIEW",
        )


def test_ratify_requires_all_covered_courts_at_or_above_threshold_not_just_leader():
    world, inst = _three_court_world(prussia=70, britain=-70, austria=0)
    terms = [{"type": "peace"}, {
        "type": "gold_indemnity", "from": "Prussia", "to": "France", "amount": 100,
    }]
    # Leader (Austria) ACCEPTS, but covered minor Prussia REJECTS.
    scorer = _make_scorer({"Austria": 60, "Britain": 60, "Prussia": 20})
    staged = _stage_review(world, terms, scorer=scorer)
    dialogue = staged["diplomatic_dialogue"]
    # The leader row alone would pass...
    assert dialogue["settlement_preview"]["acceptance"]["verdict"] == "accept"
    # ...but the per-court gate blocks ratification and confirm is not offered.
    assert dialogue["overall_acceptance"]["carries"] is False
    assert "confirm_settlement" not in dialogue["available_action_ids"]
    with patch(
        "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
        side_effect=scorer,
    ):
        result = ratify_settlement_confirm(world, dialogue)
    assert result.get("success") is False
    assert result.get("error") == "acceptance_rejected"
    assert "Prussia" in (result.get("holdout_courts") or [])
    assert result.get("mutated") is False


def test_review_payload_carries_per_court_acceptance():
    world, inst = _three_court_world(prussia=70, britain=-70, austria=0)
    staged = _stage_review(world, [{"type": "peace"}])
    dialogue = staged["diplomatic_dialogue"]
    assert dialogue["dialogue_mode"] == "REVIEW"
    rows = dialogue["per_court_acceptance"]
    assert {r["nation"] for r in rows} == {"Britain", "Prussia", "Austria"}
    assert "overall_acceptance" in dialogue


def test_holdout_court_offers_ease_or_drop_not_dead_end():
    world, inst = _three_court_world(prussia=70, britain=-70, austria=0)
    # Prussia is the only holdout.
    scorer = _make_scorer({"Austria": 60, "Britain": 60, "Prussia": 20})
    staged = _stage_review(world, [{"type": "peace"}], scorer=scorer)
    rows = staged["diplomatic_dialogue"]["per_court_acceptance"]
    prussia = next(r for r in rows if r["nation"] == "Prussia")
    assert prussia["is_holdout"] is True
    holdout_actions = {a.get("action") for a in prussia["holdout_actions"]}
    assert "settlement_dial_generous" in holdout_actions  # Ease
    assert "settlement_cover_drop" in holdout_actions      # Drop
    assert all(a.get("nation") == "Prussia" for a in prussia["holdout_actions"])
    # Non-holdout courts carry no escape affordances.
    britain = next(r for r in rows if r["nation"] == "Britain")
    assert britain["is_holdout"] is False
    assert britain["holdout_actions"] == []


def test_baseline_concede_court_at_near_acceptable_is_flagged_holdout_not_auto_carry():
    world, inst = _three_court_world(prussia=80, britain=-70, austria=60)
    # Britain's affordable concessions only reach near_acceptable (40): a
    # holdout under the >=50 carry gate, NOT auto-carry.
    scorer = _make_scorer({"Prussia": 80, "Austria": 60, "Britain": 40})
    with patch(
        "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
        side_effect=scorer,
    ):
        block = compute_per_court_acceptance(
            world, war_id="war_rf", war_instance=inst,
            proposer_side="attackers", accepting_side="defenders",
            proposer_side_leader="France",
            covered_enemy_participants=["Britain", "Prussia", "Austria"],
            settlement_terms=[{"type": "peace"}],
        )
    britain = next(r for r in block["per_court_acceptance"] if r["nation"] == "Britain")
    assert britain["band"] == "near_acceptable"
    assert britain["total"] == 40
    assert block["overall_acceptance"]["carries"] is False
    assert "Britain" in block["overall_acceptance"]["holdout_courts"]


def test_overall_carries_false_when_any_covered_court_hard_stopped_total_null():
    world, inst = _three_court_world(prussia=70, britain=-70, austria=0)
    # Russia covered but never WAR-stamped -> no direct score -> hard stop.
    scorer = _make_scorer({"Austria": 80, "Britain": 80, "Prussia": 80})
    with patch(
        "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
        side_effect=scorer,
    ):
        block = compute_per_court_acceptance(
            world, war_id="war_rf", war_instance=inst,
            proposer_side="attackers", accepting_side="defenders",
            proposer_side_leader="France",
            covered_enemy_participants=["Britain", "Prussia", "Austria", "Russia"],
            settlement_terms=[{"type": "peace"}],
        )
    russia = next(r for r in block["per_court_acceptance"] if r["nation"] == "Russia")
    assert russia["total"] is None
    assert russia["hard_stops"]
    assert block["overall_acceptance"]["carries"] is False
    assert "Russia" in block["overall_acceptance"]["holdout_courts"]


# ===========================================================================
# PROPOSE surface — non-blocking, draft preservation, default landing (§3a/§10)
# ===========================================================================


def test_propose_does_not_block_end_turn_and_back_out_preserves_scoped_draft():
    world, inst = _three_court_world(prussia=70, britain=-70, austria=0)
    # PROPOSE landing.
    with patch(
        "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
        side_effect=_make_scorer({}),
    ):
        propose = stage_settlement_confirm(
            world, war_id="war_rf", actor_nation="France",
            covered_enemy_participants=["Britain", "Prussia", "Austria"],
            selected_target_nation="Austria",
            caller_kind="player_editor", dialogue_mode="PROPOSE",
        )
    propose_dialogue = propose["diplomatic_dialogue"]
    assert propose_dialogue["dialogue_mode"] == "PROPOSE"
    assert propose_dialogue["blocking"] is False
    # PROPOSE must NOT block end-turn (authoring surface, like EDIT).
    assert world.dialogue_manager.is_hard_stop() is False

    # REVIEW, by contrast, IS a hard stop.
    world2, inst2 = _three_court_world(prussia=70, britain=-70, austria=0)
    review = _stage_review(world2, [{"type": "peace"}])
    assert review["diplomatic_dialogue"]["blocking"] is True
    assert world2.dialogue_manager.is_hard_stop() is True

    # Back Out from PROPOSE preserves the scoped draft for same-turn reopen.
    save_terms = [{"type": "peace"}, {
        "type": "gold_indemnity", "from": "Prussia", "to": "France", "amount": 100,
    }]
    from backend.game_logic.settlement_preview import save_scoped_settlement_draft

    save_scoped_settlement_draft(
        world, war_id="war_rf", selected_target_nation="Austria",
        covered_enemy_participants=["Britain", "Prussia", "Austria"],
        settlement_terms=save_terms,
    )
    propose_dialogue["settlement_terms"] = save_terms
    handle_settlement_dialogue_action(
        world, action="suspend_settlement_editor", dialogue=propose_dialogue,
    )
    restored = load_scoped_settlement_draft(
        world, war_id="war_rf", selected_target_nation="Austria",
        covered_enemy_participants=["Britain", "Prussia", "Austria"],
    )
    assert restored == save_terms


def test_propose_landing_replaces_blank_edit_as_default():
    world, inst = _three_court_world(prussia=70, britain=-70, austria=0)
    executor = DiplomaticExecutor(None)
    with patch(
        "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
        side_effect=_make_scorer({}),
    ):
        result = executor._execute_propose_common_peace(
            {
                "action": "propose_common_peace",
                "target_nation": "Austria",
                "war_id": "war_rf",
                "selected_target_nation": "Austria",
                "covered_enemy_participants": ["Britain", "Prussia", "Austria"],
            },
            {"world": world},
        )
    assert result.get("success"), result
    assert result.get("propose_on_mount") is True
    assert result.get("open_editor_on_mount") is not True
    staged = result.get("diplomatic_dialogue") or {}
    assert staged.get("dialogue_mode") == "PROPOSE"
    # Landed populated (a Talleyrand baseline), not a blank form.
    assert staged.get("settlement_terms")


def test_propose_and_dial_routes_reject_non_player_caller_kind():
    # Slice-G absence test (owned here): the PROPOSE / dial / coverage routes
    # are player-only. AI/system staging cannot advertise an editable surface
    # NOR the authoring action rail (R6-M2). Prussia is forced to a holdout so
    # the dial/coverage-affordance absence assertion is non-vacuous.
    world, inst = _three_court_world(prussia=70, britain=-70, austria=0)
    with patch(
        "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
        side_effect=_make_scorer({"Prussia": 20}),
    ):
        staged = stage_settlement_confirm(
            world, war_id="war_rf", actor_nation="France",
            settlement_terms=[{"type": "peace"}],
            covered_enemy_participants=["Britain", "Prussia", "Austria"],
            selected_target_nation="Austria",
            caller_kind="ai_system", dialogue_mode="PROPOSE",
        )
    dialogue = staged["diplomatic_dialogue"]
    assert dialogue["can_edit_terms"] is False
    assert dialogue["editor_route"] is None
    assert dialogue["available_clause_types"] == []
    # R6-M2: the player-only authoring rail must be absent from a non-player
    # staging — not just the editor surface.
    rail = set(dialogue.get("available_action_ids") or [])
    option_actions = {o.get("action") for o in (dialogue.get("options") or [])}
    for banned in ("adjust_terms", "submit_settlement_for_review", "suspend_settlement_editor"):
        assert banned not in rail, rail
        assert banned not in option_actions, option_actions
    # No dial/coverage affordances ride on any per-court row for a non-player.
    for row in dialogue.get("per_court_acceptance") or []:
        for ha in (row.get("holdout_actions") or []):
            action = str(ha.get("action", ""))
            assert not action.startswith("settlement_dial_"), action
            assert not action.startswith("settlement_cover_"), action


def test_demand_baseline_keeps_winning_court_at_or_above_near_acceptance_floor():
    # R6-M1 regression: a suggested demand must never push a winning court into
    # outright reject. Real scorer (deterministic from each court's direct_score).
    from backend.game_logic.settlement_scoring import NEAR_ACCEPTANCE_FLOOR

    # Clean strong lead (bilateral n=1): a demand IS suggested and the court
    # stays at/above the near-acceptance floor (non-vacuous — demands survive).
    world = WorldState()
    inst = make_synthetic_war_instance(
        "war_rf", attackers=["France"], defenders=["Prussia"],
        attacker_leader="France", defender_leader="Prussia",
    )
    world.war_instances["war_rf"] = inst
    _set_war_score(world, "France", "Prussia", 70)
    world.invalidate_war_instance_indexes()
    base = compute_settlement_baseline(
        world, war_id="war_rf", war_instance=inst, proposer_side="attackers",
        accepting_side="defenders", proposer_side_leader="France",
        covered_enemy_participants=["Prussia"],
    )
    pcb = base["per_court_baseline"]["Prussia"]
    assert pcb["direction"] == "demand"
    assert pcb["terms"], "a clean strong lead should still be demanded from"
    acc = compute_per_court_acceptance(
        world, war_id="war_rf", war_instance=inst, proposer_side="attackers",
        accepting_side="defenders", proposer_side_leader="France",
        covered_enemy_participants=["Prussia"], settlement_terms=base["settlement_terms"],
    )
    prow = next(r for r in acc["per_court_acceptance"] if r["nation"] == "Prussia")
    assert prow["total"] is not None and prow["total"] >= NEAR_ACCEPTANCE_FLOOR, prow

    # Catastrophic mixed war: France leads Prussia (+11) but is crushed
    # elsewhere, so even white peace for Prussia is below the floor (shared
    # package pressure). The demand branch must suggest NOTHING rather than
    # deepen the reject — never push a court below the floor via a demand.
    world2, inst2 = _three_court_world(prussia=11, britain=-95, austria=-90)
    base2 = compute_settlement_baseline(
        world2, war_id="war_rf", war_instance=inst2, proposer_side="attackers",
        accepting_side="defenders", proposer_side_leader="France",
        covered_enemy_participants=["Britain", "Prussia", "Austria"],
    )
    pru2 = base2["per_court_baseline"]["Prussia"]
    assert pru2["direction"] == "demand"
    assert pru2["terms"] == [], pru2


def test_baseline_winning_multilateral_clears_floor_not_gross_reject(monkeypatch):
    """Audit fix (Gate-4 smoke): a winning multilateral default must not open as
    a gross reject. Each court's demand was floor-checked against its OWN slice's
    harshness, but the surface scores every court against the WHOLE package's
    harshness — so France-vs-Britain+Prussia opened at 5/-4 (both far below the
    floor). `_relax_baseline_demands_for_package_harshness` now strips
    over-demanded clauses until every covered demand court clears the
    near-acceptance floor under the FULL package (parity with the single-court
    demand baseline). Ratification stays reachable — white peace carries on this
    decisive win; the demand baseline is near-acceptable and the player eases it.
    """
    from backend.game_logic.settlement_scoring import NEAR_ACCEPTANCE_FLOOR

    monkeypatch.setenv("SOVEREIGN_SMOKE_START", "settlement_multilateral")
    world = WorldState()
    inst = world.war_instances["war_1"]
    covered = ["Britain", "Prussia"]
    kw = dict(
        war_id="war_1", war_instance=inst, proposer_side="attackers",
        accepting_side="defenders", proposer_side_leader="France",
        covered_enemy_participants=covered,
    )
    terms = compute_settlement_baseline(world, **kw)["settlement_terms"]
    block = compute_per_court_acceptance(world, settlement_terms=terms, **kw)
    covered_set = set(covered)
    scores = {r["nation"]: r["total"] for r in block["per_court_acceptance"]}
    for row in block["per_court_acceptance"]:
        # No gross reject: every covered court is at least near-acceptable under
        # the FULL package (fails pre-fix at 5/-4; passes post-fix at 44/35).
        assert row["total"] is not None, row
        assert row["total"] >= NEAR_ACCEPTANCE_FLOOR, (row["nation"], row["total"], terms)
    # Relaxation invariant: no court is left below the floor while still demanded.
    for t in terms:
        if t.get("type") != "peace" and t.get("from") in covered_set:
            assert scores[t["from"]] >= NEAR_ACCEPTANCE_FLOOR, (t, scores)


def test_propose_end_turn_discards_unsubmitted_scoped_draft():
    # §10: end turn from PROPOSE discards the unsubmitted scoped draft (the SC-2
    # discard contract PROPOSE inherits from EDIT). Proven via real advance_turn,
    # not a manual store reset.
    from backend.game_logic.settlement_preview import save_scoped_settlement_draft

    world, inst = _three_court_world(prussia=70, britain=-70, austria=0)
    save_terms = [{"type": "peace"}, {
        "type": "gold_indemnity", "from": "Prussia", "to": "France", "amount": 100,
    }]
    save_scoped_settlement_draft(
        world, war_id="war_rf", selected_target_nation="Austria",
        covered_enemy_participants=["Britain", "Prussia", "Austria"],
        settlement_terms=save_terms,
    )
    assert load_scoped_settlement_draft(
        world, war_id="war_rf", selected_target_nation="Austria",
        covered_enemy_participants=["Britain", "Prussia", "Austria"],
    ) == save_terms
    world.advance_turn()
    assert not load_scoped_settlement_draft(
        world, war_id="war_rf", selected_target_nation="Austria",
        covered_enemy_participants=["Britain", "Prussia", "Austria"],
    )


# ===========================================================================
# REFRONT-V — multi-court settlement-table voice (Voice Bible gap B4)
# ===========================================================================


def _per_court_rows(rows):
    out = []
    for nation, band, total in rows:
        out.append({
            "nation": nation,
            "band": band,
            "total": total,
            "top_blocker_display": None if band == "accept" else "the territory demand",
            "hard_stops": [] if total is not None else [{"reason": "x", "enemy": nation}],
        })
    return out


def test_multi_court_per_court_voice_resolves_named_diplomat_or_chancery_fallback():
    from backend.game_logic.diplomatic_templates import (
        resolve_multi_court_settlement_voice,
    )

    world = WorldState()
    rows = _per_court_rows([
        ("Britain", "accept", 60),
        ("Prussia", "reject", 20),
        ("Russia", "near_acceptable", 40),  # no named envoy -> chancery
    ])
    voice = resolve_multi_court_settlement_voice(
        world, per_court_acceptance=rows,
        overall_acceptance={"carries": False, "holdout_courts": ["Prussia", "Russia"]},
        war_label="War of the Third Coalition",
    )
    by_nation = {v["nation"]: v for v in voice["per_court_voice"]}
    # Named diplomats for cast courts...
    assert "Chancery" not in by_nation["Britain"]["speaker"]
    assert "Chancery" not in by_nation["Prussia"]["speaker"]
    # ...chancery fallback for a court with no named envoy; never anonymous.
    assert "Chancery" in by_nation["Russia"]["speaker"]
    for v in voice["per_court_voice"]:
        assert v["speaker"]
        assert v["line"]
        assert v["speaker"] in v["line"]


def test_talleyrand_narrates_table_and_binding_constraint():
    from backend.game_logic.diplomatic_templates import (
        resolve_multi_court_settlement_voice,
    )

    world = WorldState()
    # Holdout case: narration names the binding constraint (the holdout court).
    rows = _per_court_rows([("Britain", "accept", 60), ("Prussia", "reject", 20)])
    voice = resolve_multi_court_settlement_voice(
        world, per_court_acceptance=rows,
        overall_acceptance={"carries": False, "holdout_courts": ["Prussia"]},
        war_label="War of the Third Coalition",
    )
    narration = voice["table_narration"]
    assert narration
    assert "Prussia" in narration
    assert "War of the Third Coalition" in narration

    # Carry case: narration reads as carrying, not blocked.
    rows_ok = _per_court_rows([("Britain", "accept", 60), ("Prussia", "accept", 70)])
    voice_ok = resolve_multi_court_settlement_voice(
        world, per_court_acceptance=rows_ok,
        overall_acceptance={"carries": True, "holdout_courts": []},
        war_label="War of the Third Coalition",
    )
    assert "carries" in voice_ok["table_narration"].lower()


def test_committed_multi_court_copy_avoids_conference_congress_veto_terms():
    # SC-32 D5 copy boundary: no committed multi-court copy may imply a
    # conference / congress / veto procedure.
    from backend.game_logic.diplomatic_templates import (
        SETTLEMENT_VOICE_TEMPLATES,
        resolve_multi_court_settlement_voice,
    )

    banned = ("conference", "congress", "veto")
    for key, template in SETTLEMENT_VOICE_TEMPLATES.items():
        if "multi_court" not in key:
            continue
        lowered = template.lower()
        assert not any(word in lowered for word in banned), key

    # Also assert the fully-resolved lines stay clean.
    world = WorldState()
    rows = _per_court_rows([("Britain", "accept", 60), ("Prussia", "reject", 20)])
    voice = resolve_multi_court_settlement_voice(
        world, per_court_acceptance=rows,
        overall_acceptance={"carries": False, "holdout_courts": ["Prussia"]},
        war_label="the Continental war",
    )
    blob = (voice["table_narration"] + " " + " ".join(
        v["line"] for v in voice["per_court_voice"]
    )).lower()
    assert not any(word in blob for word in banned)


def test_godot_proposal_popup_renders_per_court_table():
    # Source-level pin: the Godot settlement popup renders the per-court table
    # (PROPOSE surface) and reads the per-court / narration / holdout fields.
    from pathlib import Path

    repo = Path(__file__).resolve().parents[1]
    popup = (
        repo / "godot-client" / "project-sovereign" / "scripts"
        / "proposal_confirm_popup.gd"
    ).read_text(encoding="utf-8")
    assert "_build_settlement_per_court_block" in popup
    assert "per_court_acceptance" in popup
    assert "multi_court_table_narration" in popup
    assert "holdout_actions" in popup
    main_gd = (
        repo / "godot-client" / "project-sovereign" / "scripts" / "main.gd"
    ).read_text(encoding="utf-8")
    # `Adjust terms` mounts the Tier-3 editor client-side (its own branch,
    # parallel to the revise intercept).
    assert 'if action == "adjust_terms":' in main_gd
    assert '"submit_settlement_for_review"' in main_gd


def test_propose_dialogue_per_court_rows_carry_named_voice():
    # Integration: the staged PROPOSE surface carries named per-court voice.
    world, inst = _three_court_world(prussia=70, britain=-70, austria=0)
    with patch(
        "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
        side_effect=_make_scorer({}),
    ):
        staged = stage_settlement_confirm(
            world, war_id="war_rf", actor_nation="France",
            covered_enemy_participants=["Britain", "Prussia", "Austria"],
            selected_target_nation="Austria",
            caller_kind="player_editor", dialogue_mode="PROPOSE",
        )
    dialogue = staged["diplomatic_dialogue"]
    assert dialogue.get("multi_court_table_narration")
    for row in dialogue["per_court_acceptance"]:
        assert row.get("speaker_display")
        assert row.get("voice_line")
