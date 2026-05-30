"""Settlement Conversational Re-front — Slice 2 behavior tests.

`docs/SETTLEMENT_CONVERSATIONAL_REFRONT_SPEC.md` v0.6 §14 Slice 2:
Tier-2 intent dials (`settlement_dial_harsher` / `settlement_dial_generous`,
whole-table + focused court), coverage edits (`settlement_cover_add` /
`settlement_cover_drop` with `ignored_participants` / `remaining_wars`),
`settlement_focus_court`, the live per-court band + delta (§11.2,
presentation-only), the voice-only targeted-posture advisory (OQ#1), and the
shared one-pass score/projection memoization (§15 F-5, Golden Rule #8).

Per-court bands are pinned with a patched scorer keyed on `accepting_leader`
because the synthetic war's `base_side_pressure` is package-level (§11.2), so a
mixed synthetic war with no configured war objectives scores every court alike.
The shared-pass and projection-fallback tests use the REAL scorer.
"""

from __future__ import annotations

from unittest.mock import patch

from backend.game_logic import settlement_preview as sp
from backend.game_logic import settlement_scoring as ss
from backend.game_logic.settlement_preview import (
    SETTLEMENT_DIAL_GOLD_STEP,
    _redial_settlement_terms,
    build_settlement_preview,
    compute_per_court_acceptance,
    handle_settlement_dialogue_action,
    stage_settlement_confirm,
)
from backend.game_logic.settlement_scoring import (
    calculate_common_peace_acceptance,
    project_balance_after_settlement,
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


def _three_court_world(*, prussia: int = 70, britain: int = -70, austria: int = 0):
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
    _set_war_score(world, "France", "Prussia", prussia)
    _set_war_score(world, "France", "Britain", britain)
    _set_war_score(world, "France", "Austria", austria)
    world.invalidate_war_instance_indexes()
    return world, inst


def _make_scorer(score_by_leader: dict, default: int = 60, *, feedback: bool = False):
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
        result = {
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
        if feedback and score is not None and score < 50:
            result["feedback"] = [
                {"component": "term_harshness_penalty", "value": -30}
            ]
        return result

    return _side_effect


def _stage_propose(world, *, terms=None, covered=None, scorer=None, caller_kind="player_editor"):
    scorer = scorer or _make_scorer({})
    with patch(_SCORER_PATH, side_effect=scorer):
        staged = stage_settlement_confirm(
            world,
            war_id="war_rf",
            actor_nation="France",
            settlement_terms=terms,
            covered_enemy_participants=covered or ["Britain", "Prussia", "Austria"],
            selected_target_nation=(covered or ["Austria"])[-1] if covered else "Austria",
            caller_kind=caller_kind,
            dialogue_mode="PROPOSE",
        )
    assert staged.get("success"), staged
    return staged["diplomatic_dialogue"]


# ===========================================================================
# Tier-2 intent dials (§11.3, OQ#1)
# ===========================================================================


def test_harsher_dial_rescores_all_covered_courts():
    world, _ = _three_court_world()
    scorer = _make_scorer({})
    dialogue = _stage_propose(world, scorer=scorer)
    seen = []

    def _spy(world=None, *, accepting_leader=None, **kw):
        seen.append(accepting_leader)
        return scorer(world, accepting_leader=accepting_leader, **kw)

    with patch(_SCORER_PATH, side_effect=_spy):
        result = handle_settlement_dialogue_action(
            world,
            action="settlement_dial_harsher",
            dialogue=dialogue,
            action_params={"scope": "table"},
        )
    assert result.get("success"), result
    nd = result["diplomatic_dialogue"]
    assert nd["dialogue_mode"] == "PROPOSE"
    rows = {r["nation"] for r in nd["per_court_acceptance"]}
    assert rows == {"Britain", "Prussia", "Austria"}
    # The whole-table dial re-scored every covered court.
    assert {"Britain", "Prussia", "Austria"} <= set(seen)


def test_focused_dial_applies_to_single_court_only():
    world, _ = _three_court_world()
    terms = [
        {"type": "peace"},
        {"type": "gold_indemnity", "from": "Prussia", "to": "France", "amount": 200},
        {"type": "gold_indemnity", "from": "France", "to": "Britain", "amount": 300},
    ]
    dialogue = _stage_propose(world, terms=terms)
    with patch(_SCORER_PATH, side_effect=_make_scorer({})):
        result = handle_settlement_dialogue_action(
            world,
            action="settlement_dial_harsher",
            dialogue=dialogue,
            action_params={"scope": "Prussia"},
        )
    assert result.get("success"), result
    nt = result["diplomatic_dialogue"]["settlement_terms"]
    prussia = next(t for t in nt if t.get("from") == "Prussia")
    britain = next(t for t in nt if t.get("to") == "Britain")
    # Only the focused court's slice moved (Prussia gold +step); Britain untouched.
    assert prussia["amount"] == 200 + SETTLEMENT_DIAL_GOLD_STEP
    assert britain["amount"] == 300


def test_per_court_acceptance_payload_band_and_top_blocker():
    world, _ = _three_court_world()
    scorer = _make_scorer({"Prussia": 20, "Austria": 60, "Britain": 60}, feedback=True)
    dialogue = _stage_propose(world, scorer=scorer)
    with patch(_SCORER_PATH, side_effect=scorer):
        result = handle_settlement_dialogue_action(
            world,
            action="settlement_dial_harsher",
            dialogue=dialogue,
            action_params={"scope": "table"},
        )
    rows = {r["nation"]: r for r in result["diplomatic_dialogue"]["per_court_acceptance"]}
    for row in rows.values():
        assert "band" in row and row["band_display"]
        assert "top_blocker_display" in row
    # The holdout carries a top-blocker line; an accepting court does not.
    assert rows["Prussia"]["band"] == "reject"
    assert rows["Prussia"]["top_blocker_display"]
    assert rows["Austria"]["top_blocker_display"] is None


def test_dial_delta_previous_to_current_band_presentation_only():
    world, _ = _three_court_world()
    # Stage with Prussia ACCEPTING (previous band = accept)...
    dialogue = _stage_propose(world, scorer=_make_scorer({"Prussia": 60}))
    # ...then dial under a scorer where Prussia now REJECTS.
    with patch(_SCORER_PATH, side_effect=_make_scorer({"Prussia": 20})):
        result = handle_settlement_dialogue_action(
            world,
            action="settlement_dial_harsher",
            dialogue=dialogue,
            action_params={"scope": "table"},
        )
    prussia = next(
        r for r in result["diplomatic_dialogue"]["per_court_acceptance"]
        if r["nation"] == "Prussia"
    )
    assert prussia["previous_band"] == "accept"
    assert prussia["band"] == "reject"
    assert prussia["delta_display"]
    assert "Prussia" in prussia["delta_display"]
    # Presentation-only: the delta string never alters the scored total.
    assert prussia["total"] == 20


def test_dial_changes_magnitude_without_silently_swapping_requested_identity():
    # OQ#7: harsher/generous change amount + clause count only — never the
    # requested region or payer identity. Tested on the pure redraft helper.
    terms = [
        {"type": "peace"},
        {"type": "territory_cede", "from": "Prussia", "to": "France", "region": "Silesia"},
        {"type": "gold_indemnity", "from": "Prussia", "to": "France", "amount": 200},
    ]
    harsher = _redial_settlement_terms(
        terms=terms, scope_courts=["Prussia"], direction="harsher",
        proposer_side_leader="France",
    )
    terr = next(t for t in harsher if t["type"] == "territory_cede")
    gold = next(t for t in harsher if t["type"] == "gold_indemnity")
    # Region + payer identity preserved; only gold magnitude grew.
    assert terr["region"] == "Silesia"
    assert terr["from"] == "Prussia" and terr["to"] == "France"
    assert gold["amount"] == 200 + SETTLEMENT_DIAL_GOLD_STEP
    assert gold["from"] == "Prussia" and gold["to"] == "France"

    generous = _redial_settlement_terms(
        terms=terms, scope_courts=["Prussia"], direction="generous",
        proposer_side_leader="France",
    )
    gold2 = [t for t in generous if t["type"] == "gold_indemnity"]
    # Magnitude shrank; payer identity still never swapped.
    assert gold2 and gold2[0]["amount"] == 200 - SETTLEMENT_DIAL_GOLD_STEP
    assert gold2[0]["from"] == "Prussia"
    # The territory demand is dropped on generous (count down), never replaced
    # with a different region identity.
    assert all(t.get("region") != "Bavaria" for t in generous)


# ===========================================================================
# Coverage edits (§11.3, OQ#2)
# ===========================================================================


def test_coverage_drop_court_rescores_and_updates_remaining_wars_and_ignored():
    world, _ = _three_court_world()
    dialogue = _stage_propose(world)
    with patch(_SCORER_PATH, side_effect=_make_scorer({})):
        result = handle_settlement_dialogue_action(
            world,
            action="settlement_cover_drop",
            dialogue=dialogue,
            action_params={"nation": "Britain"},
        )
    assert result.get("success"), result
    nd = result["diplomatic_dialogue"]
    # Britain dropped from coverage; remaining courts re-scored.
    assert {r["nation"] for r in nd["per_court_acceptance"]} == {"Prussia", "Austria"}
    assert "Britain" not in nd["covered_enemy_participants"]
    # Britain is now ignored and stays at war (a remaining war pair).
    assert "Britain" in result["ignored_participants"]
    assert "Britain" in nd["ignored_participants"]
    assert any(rw.get("enemy") == "Britain" for rw in result["remaining_wars"])


def test_coverage_add_court_redraws_baseline_for_new_set():
    world, _ = _three_court_world()
    # Start with Britain OUT of the settlement (still a hostile, coverable court).
    dialogue = _stage_propose(world, covered=["Prussia", "Austria"])
    assert any(
        s["nation"] == "Britain" for s in dialogue["coverage_add_suggestions"]
    )
    with patch(_SCORER_PATH, side_effect=_make_scorer({})):
        result = handle_settlement_dialogue_action(
            world,
            action="settlement_cover_add",
            dialogue=dialogue,
            action_params={"nation": "Britain"},
        )
    assert result.get("success"), result
    nd = result["diplomatic_dialogue"]
    # Baseline re-drawn for the new three-court set.
    assert "Britain" in nd["covered_enemy_participants"]
    assert {r["nation"] for r in nd["per_court_acceptance"]} == {
        "Britain", "Prussia", "Austria",
    }
    assert "Britain" not in result.get("ignored_participants", [])


# ===========================================================================
# Focus + targeted-posture advisory (OQ#1)
# ===========================================================================


def test_settlement_focus_court_is_presentation_only_no_term_change():
    world, _ = _three_court_world()
    dialogue = _stage_propose(world)
    before_terms = [dict(t) for t in dialogue["settlement_terms"]]
    result = handle_settlement_dialogue_action(
        world,
        action="settlement_focus_court",
        dialogue=dialogue,
        action_params={"nation": "Prussia"},
    )
    assert result.get("success"), result
    assert result["focused_court"] == "Prussia"
    assert result["mutated"] is False
    # Focus never re-drafts: terms are byte-for-byte unchanged.
    assert result["diplomatic_dialogue"]["settlement_terms"] == before_terms


def test_per_court_row_exposes_focused_press_and_ease_dials():
    # OQ#1 / §17: focused dialing is reached from each per-court row. Every
    # dialable row exposes a focused `Press`; non-holdout rows also expose a
    # focused `Ease` (holdout rows get Ease via holdout_actions — no duplicate).
    world, _ = _three_court_world()
    scorer = _make_scorer({"Prussia": 20, "Austria": 60, "Britain": 60})
    dialogue = _stage_propose(world, scorer=scorer)
    rows = {r["nation"]: r for r in dialogue["per_court_acceptance"]}

    austria = rows["Austria"]  # accepting, non-holdout
    press = [a for a in austria["dial_actions"] if a["action"] == "settlement_dial_harsher"]
    ease = [a for a in austria["dial_actions"] if a["action"] == "settlement_dial_generous"]
    assert press and press[0]["scope"] == "Austria"
    assert ease and ease[0]["scope"] == "Austria"

    prussia = rows["Prussia"]  # holdout
    assert any(
        a["action"] == "settlement_dial_harsher" and a["scope"] == "Prussia"
        for a in prussia["dial_actions"]
    )
    # No duplicate Ease in dial_actions — the holdout Ease rides on holdout_actions.
    assert all(a["action"] != "settlement_dial_generous" for a in prussia["dial_actions"])

    # Non-player staging gets no focused dials (Slice-G boundary).
    world2, _ = _three_court_world()
    ai_dialogue = _stage_propose(world2, scorer=scorer, caller_kind="ai_system")
    for row in ai_dialogue["per_court_acceptance"]:
        assert row["dial_actions"] == []


def test_focused_press_from_row_affordance_presses_only_that_court():
    # §17 end-to-end: take the actual `Press Prussia` affordance off the row and
    # route it through the handler — only Prussia's slice moves.
    world, _ = _three_court_world()
    terms = [
        {"type": "peace"},
        {"type": "gold_indemnity", "from": "Prussia", "to": "France", "amount": 200},
        {"type": "gold_indemnity", "from": "France", "to": "Britain", "amount": 300},
    ]
    dialogue = _stage_propose(world, terms=terms)
    prussia_row = next(r for r in dialogue["per_court_acceptance"] if r["nation"] == "Prussia")
    press = next(
        a for a in prussia_row["dial_actions"] if a["action"] == "settlement_dial_harsher"
    )
    with patch(_SCORER_PATH, side_effect=_make_scorer({})):
        result = handle_settlement_dialogue_action(
            world, action=press["action"], dialogue=dialogue, action_params=press,
        )
    assert result.get("success"), result
    nt = result["diplomatic_dialogue"]["settlement_terms"]
    assert next(t for t in nt if t.get("from") == "Prussia")["amount"] == 300
    assert next(t for t in nt if t.get("to") == "Britain")["amount"] == 300


def test_targeted_posture_is_voice_only_not_applied():
    world, _ = _three_court_world()
    scorer = _make_scorer({"Prussia": 20, "Austria": 60, "Britain": 60})
    dialogue = _stage_propose(world, scorer=scorer)
    advisory = dialogue["targeted_posture_advisory"]
    # A targeted-posture recommendation is offered as voice...
    assert advisory
    assert "ease Prussia" in advisory          # the easeable holdout
    assert "press" in advisory                 # accepting courts -> press
    # ...but it is advice only: the staged package equals the raw baseline, so
    # the advisory silently applied no dial (Golden Rule #6).
    world2, inst2 = _three_court_world()
    with patch(_SCORER_PATH, side_effect=scorer):
        baseline = sp.compute_settlement_baseline(
            world2, war_id="war_rf", war_instance=inst2,
            proposer_side="attackers", accepting_side="defenders",
            proposer_side_leader="France",
            covered_enemy_participants=["Britain", "Prussia", "Austria"],
        )
    assert dialogue["settlement_terms"] == baseline["settlement_terms"]


def test_dial_rejects_non_player_caller_kind():
    # Slice-G boundary: only the player steers a settlement. An AI/system PROPOSE
    # staging cannot drive the dial/coverage redraw.
    world, _ = _three_court_world()
    dialogue = _stage_propose(world, caller_kind="ai_system")
    result = handle_settlement_dialogue_action(
        world,
        action="settlement_dial_harsher",
        dialogue=dialogue,
        action_params={"scope": "table"},
    )
    assert result.get("success") is False
    assert result.get("error") == "settlement_action_not_player_authored"
    assert result.get("mutated") is False


def test_cover_drop_last_court_blocked_by_coverage_floor():
    # V5: at least one covered enemy must remain.
    world, _ = _three_court_world()
    dialogue = _stage_propose(world, covered=["Prussia"])
    with patch(_SCORER_PATH, side_effect=_make_scorer({})):
        result = handle_settlement_dialogue_action(
            world,
            action="settlement_cover_drop",
            dialogue=dialogue,
            action_params={"nation": "Prussia"},
        )
    assert result.get("success") is False
    assert result.get("error") == "no_covered_enemy_participants"
    assert result.get("mutated") is False


# ===========================================================================
# Scale — one shared score/projection pass (§15 F-5, Golden Rule #8)
# ===========================================================================


def test_per_court_scoring_shares_one_direct_score_side_pressure_harshness_and_balance_projection_pass():
    world, inst = _three_court_world()
    with patch.object(
        sp, "project_balance_after_settlement",
        wraps=sp.project_balance_after_settlement,
    ) as proj, patch.object(
        sp, "compute_direct_scores_by_enemy",
        wraps=sp.compute_direct_scores_by_enemy,
    ) as ds, patch.object(
        sp, "compute_side_pressure_score",
        wraps=sp.compute_side_pressure_score,
    ) as sps:
        block = compute_per_court_acceptance(
            world, war_id="war_rf", war_instance=inst,
            proposer_side="attackers", accepting_side="defenders",
            proposer_side_leader="France",
            covered_enemy_participants=["Britain", "Prussia", "Austria"],
            settlement_terms=[{"type": "peace"}],
        )
    # Three courts scored, but each package-level input computed exactly ONCE.
    assert len(block["per_court_acceptance"]) == 3
    assert proj.call_count == 1
    assert ds.call_count == 1
    assert sps.call_count == 1


def test_balance_projection_param_falls_back_to_internal_compute_when_not_injected():
    world, inst = _three_court_world()
    kwargs = dict(
        war_id="war_rf", war_instance=inst,
        proposer_side="attackers", accepting_side="defenders",
        accepting_leader="Prussia", proposer_side_leader="France",
        covered_enemy_participants=["Britain", "Prussia", "Austria"],
        settlement_terms=[{"type": "peace"}],
    )
    # Not injected -> the scorer computes the projection internally (existing
    # single-call callers are unchanged).
    with patch.object(
        ss, "project_balance_after_settlement",
        wraps=ss.project_balance_after_settlement,
    ) as proj_spy:
        r_internal = calculate_common_peace_acceptance(world, **kwargs)
    assert proj_spy.call_count == 1

    # Injected -> the scorer uses it and skips the internal compute entirely,
    # and the score is identical to the internal-compute path.
    projection = project_balance_after_settlement(
        world, war_id="war_rf", settlement_terms=[{"type": "peace"}],
    )
    with patch.object(
        ss, "project_balance_after_settlement",
        wraps=ss.project_balance_after_settlement,
    ) as proj_spy2:
        r_injected = calculate_common_peace_acceptance(
            world, balance_projection=projection, **kwargs
        )
    assert proj_spy2.call_count == 0
    assert r_internal["score"] == r_injected["score"]


# ===========================================================================
# Godot source pins — the PROPOSE surface consumes the Slice 2 controls
# ===========================================================================


def test_godot_popup_renders_tier2_dial_coverage_and_delta_controls():
    from pathlib import Path

    repo = Path(__file__).resolve().parents[1]
    scripts = repo / "godot-client" / "project-sovereign" / "scripts"
    popup = (scripts / "proposal_confirm_popup.gd").read_text(encoding="utf-8")
    # Per-row affordances + coverage prompts are rendered as clickable buttons.
    assert "_add_settlement_tier2_buttons" in popup
    assert "_on_settlement_tier2_affordance" in popup
    assert "coverage_add_suggestions" in popup
    # Focused per-row Press/Ease dials are rendered as clickable buttons.
    assert "dial_actions" in popup
    # Live delta + voice-only targeted-posture advisory are surfaced.
    assert "delta_display" in popup
    assert "targeted_posture_advisory" in popup

    main_gd = (scripts / "main.gd").read_text(encoding="utf-8")
    # The structured `action_params` route exists for per-row affordances.
    assert "send_dialogue_response_with_params" in main_gd
    for verb in (
        "settlement_dial_harsher",
        "settlement_dial_generous",
        "settlement_cover_add",
        "settlement_cover_drop",
        "settlement_focus_court",
    ):
        assert verb in main_gd

    api_client = (scripts / "api_client.gd").read_text(encoding="utf-8")
    assert "func send_dialogue_response_with_params" in api_client
    assert "action_params" in api_client
