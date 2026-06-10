"""Settlement Guided Terms — GT-Slice-2 behavior tests.

`docs/SETTLEMENT_GUIDED_TERMS_SPEC.md` v0.2 §9 GT-Slice-2: every per-court
PROPOSE row carries `demand_suggestions[]` (valid, fully-formed,
direction-correct options for that court, TABLE-scoped per §3.4, each with
a `reason_display`) + `current_demands[]` with magnitude metadata + the
shared `treasury_line`, plus the §8 OQ-6 budget-bound cheapest-signature
recommendation. Suggestions carry the EXACT `action_params` the GT-Slice-1
add verb accepts, so a suggestion click can never author an invalid draft
(valid-by-construction at the suggestion source; the validator stays the
authority at the restage choke point).

Fixture idioms mirror `tests/test_settlement_guided_terms_slice1.py`: a
synthetic France vs Britain + Prussia + Austria war with per-pair scores
chosen so the three live directions coexist (Prussia=demand,
Britain=concede, Austria=peace dead-band); a fourth covered court with no
live WAR pair (Russia) exercises the §3.3 hard-stop row; the scorer is
patched for band-independent payload tests.
"""

from __future__ import annotations

from typing import Mapping
from unittest.mock import patch

from backend.game_logic.settlement_preview import (
    compute_settlement_treasury_line,
    handle_settlement_dialogue_action,
    stage_settlement_confirm,
)
from backend.game_logic.settlement_baseline import (
    _payer_net_income_estimate,
)
from backend.game_logic.settlement_staging import (
    _DEMAND_CLAUSE_CAP_REASON,
)
from backend.game_logic.settlement_scoring import (
    CONCESSION_GOLD_DIVISOR,
    GOLD_PER_TURN_MIN_AMOUNT,
    MAX_SETTLEMENT_CLAUSE_COUNT,
)
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import (
    make_synthetic_war_instance,
)

_SCORER_PATH = "backend.game_logic.settlement_scoring.calculate_common_peace_acceptance"
_POWER_CAP_PATH = "backend.game_logic.diplomacy.check_vassalage_power_cap"


# ===========================================================================
# Helpers (slice-1 idioms)
# ===========================================================================


def _set_war_score(world: WorldState, frm: str, to: str, score: int) -> None:
    key = world._make_diplo_key(frm, to)
    world.diplomatic_states[key] = "WAR"
    if sorted([frm, to])[0] == frm:
        world.war_scores[key] = int(score)
    else:
        world.war_scores[key] = -int(score)


def _three_court_world(*, prussia: int = 70, britain: int = -70, austria: int = 0):
    """France (attacker) vs Britain + Prussia + Austria (defenders).

    Default pair scores give all three live directions at once: Prussia
    +70 (demand), Britain -70 (concede), Austria 0 (peace dead-band).
    """
    world = WorldState()
    inst = make_synthetic_war_instance(
        "war_gt",
        attackers=["France"],
        defenders=["Britain", "Prussia", "Austria"],
        attacker_leader="France",
        defender_leader="Austria",
    )
    world.war_instances["war_gt"] = inst
    _set_war_score(world, "France", "Prussia", prussia)
    _set_war_score(world, "France", "Britain", britain)
    _set_war_score(world, "France", "Austria", austria)
    world.invalidate_war_instance_indexes()
    return world, inst


def _four_court_world_with_hard_stop():
    """Three live directions + Russia covered with NO live France WAR pair
    (`select_direct_score` returns None — the §3.3 hard-stop row). Russia
    stays coverable through the instance's `diplo_key_meta` while the live
    `diplomatic_states` carries no WAR entry for the pair."""
    world = WorldState()
    inst = make_synthetic_war_instance(
        "war_gt",
        attackers=["France"],
        defenders=["Britain", "Prussia", "Austria", "Russia"],
        attacker_leader="France",
        defender_leader="Austria",
    )
    world.war_instances["war_gt"] = inst
    _set_war_score(world, "France", "Prussia", 70)
    _set_war_score(world, "France", "Britain", -70)
    _set_war_score(world, "France", "Austria", 0)
    world.invalidate_war_instance_indexes()
    return world, inst


def _make_scorer(score_by_leader: dict, default: int = 60):
    """Patched `calculate_common_peace_acceptance` keyed on accepting_leader."""

    def _side_effect(world=None, *, accepting_leader=None, **kwargs):
        score = score_by_leader.get(accepting_leader, default)
        verdict = "accept" if (score or 0) >= 50 else (
            "near_acceptable" if (score or 0) >= 35 else "reject"
        )
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


def _stage_propose(
    world,
    *,
    terms=None,
    covered=None,
    scorer=None,
    caller_kind="player_editor",
    dialogue_mode="PROPOSE",
):
    scorer = scorer or _make_scorer({})
    with patch(_SCORER_PATH, side_effect=scorer):
        staged = stage_settlement_confirm(
            world,
            war_id="war_gt",
            actor_nation="France",
            settlement_terms=terms,
            covered_enemy_participants=covered or ["Britain", "Prussia", "Austria"],
            selected_target_nation=(covered or ["Austria"])[-1],
            caller_kind=caller_kind,
            dialogue_mode=dialogue_mode,
        )
    assert staged.get("success"), staged
    return staged["diplomatic_dialogue"]


def _demand_verb(world, dialogue, action, params, scorer=None):
    scorer = scorer or _make_scorer({})
    with patch(_SCORER_PATH, side_effect=scorer):
        return handle_settlement_dialogue_action(
            world,
            action=action,
            dialogue=dialogue,
            action_params={"action": action, **params},
        )


def _row_of(dialogue, nation):
    for row in dialogue.get("per_court_acceptance") or []:
        if str(row.get("nation")) == nation:
            return row
    raise AssertionError(f"no per-court row for {nation}")


def _suggestions_of(dialogue, nation):
    return list(_row_of(dialogue, nation).get("demand_suggestions") or [])


def _assert_no_floats(node, path="root"):
    if isinstance(node, bool):
        return
    assert not isinstance(node, float), f"float leaked at {path}: {node!r}"
    if isinstance(node, Mapping):
        for key, value in node.items():
            _assert_no_floats(value, f"{path}.{key}")
    elif isinstance(node, (list, tuple)):
        for idx, value in enumerate(node):
            _assert_no_floats(value, f"{path}[{idx}]")


# ===========================================================================
# Completion contract: rows expose suggestions + current demands + reasons
# ===========================================================================


def test_propose_rows_expose_suggestions_current_demands_and_reasons():
    """§9 GT-Slice-2 completion: PROPOSE rows expose suggestions (each with
    a non-empty `reason_display`), current demand lines keyed by
    `clause_index`, and the row authoring state."""
    world, _ = _three_court_world()
    world.nation_gold["France"] = 2000
    world.nation_gold["Prussia"] = 1000
    terms = [
        {"type": "peace"},
        {"type": "gold_indemnity", "from": "Prussia", "to": "France", "amount": 200},
    ]
    dialogue = _stage_propose(world, terms=terms)
    prussia = _row_of(dialogue, "Prussia")
    assert prussia["can_author"] is True
    assert prussia["lead_group"] == "demand"
    assert prussia["authoring_disabled_reason_display"] == ""
    suggestions = prussia["demand_suggestions"]
    assert suggestions, "demand court must offer suggestions"
    for suggestion in suggestions:
        assert suggestion["label"]
        assert suggestion["reason_display"], suggestion
        assert suggestion["action"] == "settlement_demand_add"
        assert suggestion["group"] in ("demand", "offer")
        assert suggestion["action_params"]["nation"] == "Prussia"
        assert suggestion["war_id"] == "war_gt"
        assert suggestion["draft_key"] == dialogue["draft_key"]
    # The direction-led group leads the list (§3.3).
    assert suggestions[0]["group"] == "demand"
    # Territory suggestion: top pick pre-filled + the OQ-1 dropdown of
    # valid regions, every option a real holding of the court.
    territory = [s for s in suggestions if s["clause_type"] == "territory_cede"
                 and s["group"] == "demand"]
    assert territory
    holdings = set(world.get_nation_regions("Prussia"))
    assert territory[0]["action_params"]["region"] in holdings
    assert territory[0]["region_options"]
    assert set(territory[0]["region_options"]) <= holdings
    # Current demand lines: the staged gold clause renders with index,
    # direction tag, magnitude metadata, and both mutation affordances.
    lines = prussia["current_demands"]
    assert len(lines) == 1
    line = lines[0]
    assert line["clause_index"] == 1
    assert line["clause_type"] == "gold_indemnity"
    assert line["direction_tag"] == "Demanded"
    assert line["line_display"] == "200 gold"
    assert line["magnitude"]["amount"] == 200
    assert line["remove_action"]["action"] == "settlement_demand_remove"
    assert line["remove_action"]["action_params"] == {
        "clause_index": 1, "expected_type": "gold_indemnity",
    }
    assert line["set_magnitude_action"]["action"] == "settlement_demand_set_magnitude"
    # The treasury line rides the same dialogue (§3.4, computed once).
    assert dialogue["treasury_line"] == compute_settlement_treasury_line(
        world, proposer_side_leader="France", settlement_terms=terms,
    )


def test_losing_court_suggestions_lead_with_offers():
    """§3.2: a concede-direction court leads with the offer group — France
    is the conceder — while the demand group still trails (D4)."""
    world, _ = _three_court_world()
    world.nation_gold["France"] = 2000
    dialogue = _stage_propose(world, terms=[{"type": "peace"}])
    britain = _row_of(dialogue, "Britain")
    assert britain["direction"] == "concede"
    assert britain["lead_group"] == "offer"
    suggestions = britain["demand_suggestions"]
    assert suggestions
    assert suggestions[0]["group"] == "offer"
    groups = [s["group"] for s in suggestions]
    assert "demand" in groups, "D4: the demand group must still be offered"
    # The offer group is contiguous at the head; demands trail collapsed.
    first_demand = groups.index("demand")
    assert all(g == "offer" for g in groups[:first_demand])


def test_dead_band_court_offers_both_directions():
    """§3.3: the dead-band (`peace`) row offers BOTH groups with neither
    pre-expanded — the re-front §17 'sweeten the wobbler' home."""
    world, _ = _three_court_world()
    world.nation_gold["France"] = 2000
    world.nation_gold["Austria"] = 1000
    dialogue = _stage_propose(world, terms=[{"type": "peace"}])
    austria = _row_of(dialogue, "Austria")
    assert austria["direction"] == "peace"
    assert austria["can_author"] is True
    assert austria["lead_group"] == ""
    groups = {s["group"] for s in austria["demand_suggestions"]}
    assert groups == {"demand", "offer"}


def test_hard_stop_court_row_disables_authoring_with_reason():
    """§3.3: a hard-stopped court (no live cross-side pair — `total=null`)
    exposes NO authoring: no suggestions, no current-demand affordances,
    `Add demand` disabled with the rendered reason (Drop is the row's only
    verb, owned by the holdout affordances)."""
    world, _ = _four_court_world_with_hard_stop()
    world.nation_gold["France"] = 2000
    dialogue = _stage_propose(
        world,
        terms=[{"type": "peace"}],
        covered=["Britain", "Prussia", "Austria", "Russia"],
    )
    russia = _row_of(dialogue, "Russia")
    assert russia["direction"] == "hard_stop"
    assert russia["total"] is None
    assert russia["can_author"] is False
    assert "Russia" in russia["authoring_disabled_reason_display"]
    assert russia["demand_suggestions"] == []
    assert russia["current_demands"] == []
    # The live rows around it still author.
    assert _row_of(dialogue, "Prussia")["can_author"] is True


def test_review_mode_and_non_player_rows_expose_no_authoring():
    """§7 guards, payload half (UX-2 server side): REVIEW is a frozen
    staged-decision surface and a non-player staging never gets authoring
    affordances (the Slice-G boundary)."""
    world, _ = _three_court_world()
    world.nation_gold["France"] = 2000
    review = _stage_propose(
        world, terms=[{"type": "peace"}], dialogue_mode="REVIEW",
    )
    for row in review["per_court_acceptance"]:
        assert row["can_author"] is False, row["nation"]
        assert row["demand_suggestions"] == [], row["nation"]
        assert row["current_demands"] == [], row["nation"]
    world2, _ = _three_court_world()
    world2.nation_gold["France"] = 2000
    ai_staged = _stage_propose(
        world2, terms=[{"type": "peace"}], caller_kind="ai_system",
    )
    for row in ai_staged["per_court_acceptance"]:
        assert row["can_author"] is False, row["nation"]
        assert row["demand_suggestions"] == [], row["nation"]
        assert row["current_demands"] == [], row["nation"]


def test_clause_cap_disables_add_but_keeps_remove_affordances():
    """§3.1: at the clause cap `Add demand` renders disabled with the
    SHARED humanized reason (the same string the add verb rejects with),
    suggestions vanish — but the current lines KEEP their Remove
    affordances, because removal is the way back under the cap."""
    world, _ = _three_court_world()
    world.nation_gold["France"] = 2000
    filler = [
        {
            "type": "territory_cede", "from": "Prussia", "to": "France",
            "region": f"Province {i}",
        }
        for i in range(MAX_SETTLEMENT_CLAUSE_COUNT - 1)
    ]
    terms = [{"type": "peace"}] + filler
    assert len(terms) == MAX_SETTLEMENT_CLAUSE_COUNT
    dialogue = _stage_propose(world, terms=terms)
    prussia = _row_of(dialogue, "Prussia")
    assert prussia["can_author"] is False
    assert prussia["authoring_disabled_reason_display"] == _DEMAND_CLAUSE_CAP_REASON
    assert prussia["demand_suggestions"] == []
    lines = prussia["current_demands"]
    assert len(lines) == MAX_SETTLEMENT_CLAUSE_COUNT - 1
    assert all(line["remove_action"] for line in lines)


# ===========================================================================
# Valid-by-construction (§3.4 table scope, D3 identity, eligibility gates)
# ===========================================================================


def test_no_identity_fields_exposed_and_france_self_impossible():
    """D3/§3.1: no suggestion exposes a from/to identity field — direction
    is fixed per option by the court + group — and no suggestion can ever
    target France itself (rows exist only for covered enemy courts)."""
    world, _ = _three_court_world()
    world.nation_gold["France"] = 2000
    world.nation_gold["Prussia"] = 1000
    dialogue = _stage_propose(world, terms=[{"type": "peace"}])
    for row in dialogue["per_court_acceptance"]:
        assert row["nation"] != "France"
        for suggestion in row.get("demand_suggestions") or []:
            params = suggestion["action_params"]
            assert "from" not in params, suggestion
            assert "to" not in params, suggestion
            assert params["nation"] == row["nation"]
            assert params["nation"] != "France"


def test_suggestions_eligibility_gated_for_dependency_clauses():
    """§4: vassalage/subjugation options run the live eligibility
    evaluators BEFORE rendering — an already-vassal court offers neither;
    an eligible court offers both."""
    world, _ = _three_court_world()
    world.nation_gold["France"] = 2000
    with patch(
        _POWER_CAP_PATH,
        return_value={"allowed": True, "lord_power": 100, "target_power": 30, "pct": 30},
    ):
        dialogue = _stage_propose(world, terms=[{"type": "peace"}])
    types = {s["clause_type"] for s in _suggestions_of(dialogue, "Prussia")}
    assert "vassalage" in types
    assert "subjugation" in types

    world2, _ = _three_court_world()
    world2.nation_gold["France"] = 2000
    world2.vassals["Prussia"] = {"lord": "Austria", "loyalty": 50}
    with patch(
        _POWER_CAP_PATH,
        return_value={"allowed": True, "lord_power": 100, "target_power": 30, "pct": 30},
    ):
        dialogue2 = _stage_propose(world2, terms=[{"type": "peace"}])
    types2 = {s["clause_type"] for s in _suggestions_of(dialogue2, "Prussia")}
    assert "vassalage" not in types2
    assert "subjugation" not in types2


def test_liberation_suggestion_gated_on_court_holding_a_vassal():
    """§4: `Free <court>'s vassal [X]` appears only when the court holds a
    vassal (liberator fixed to France per OQ-3), with the eligible vassal
    set exposed as dropdown options."""
    world, _ = _three_court_world()
    world.nation_gold["France"] = 2000
    world.vassals["Saxony"] = {"lord": "Prussia", "loyalty": 50}
    dialogue = _stage_propose(world, terms=[{"type": "peace"}])
    liberation = [
        s for s in _suggestions_of(dialogue, "Prussia")
        if s["clause_type"] == "liberation"
    ]
    assert liberation
    assert liberation[0]["action_params"]["vassal_nation"] == "Saxony"
    assert liberation[0]["vassal_options"] == ["Saxony"]
    # No vassal — no option (Britain holds none).
    assert not [
        s for s in _suggestions_of(dialogue, "Britain")
        if s["clause_type"] == "liberation"
    ]


def test_guided_suggestion_region_options_exclude_promised_regions():
    """§3.4 table scope: a region already promised by ANY staged
    `territory_cede` clause is excluded from every region dropdown — the
    suggestion source can never author a V1 double-promise."""
    world, _ = _three_court_world()
    world.nation_gold["France"] = 2000
    baseline = _stage_propose(world, terms=[{"type": "peace"}])
    territory = [
        s for s in _suggestions_of(baseline, "Prussia")
        if s["clause_type"] == "territory_cede" and s["group"] == "demand"
    ]
    assert territory
    promised = territory[0]["action_params"]["region"]
    terms = [
        {"type": "peace"},
        {
            "type": "territory_cede", "from": "Prussia", "to": "France",
            "region": promised,
        },
    ]
    world2, _ = _three_court_world()
    world2.nation_gold["France"] = 2000
    dialogue2 = _stage_propose(world2, terms=terms)
    territory2 = [
        s for s in _suggestions_of(dialogue2, "Prussia")
        if s["clause_type"] == "territory_cede" and s["group"] == "demand"
    ]
    for suggestion in territory2:
        assert suggestion["action_params"]["region"] != promised
        assert promised not in suggestion["region_options"]


def test_gold_per_turn_prefill_respects_payer_capacity():
    """§4 capacity rule: the recurring-gold pre-fill is bounded by
    `current_gold + max(0, net_income) × turns`, NET of existing recurring
    obligations — never an unpayable tribute. A payer drowning in existing
    obligations gets no recurring suggestion at all."""
    world, _ = _three_court_world()
    world.nation_gold["France"] = 2000
    world.nation_gold["Prussia"] = 0
    income = _payer_net_income_estimate(world, "Prussia")
    assert income >= GOLD_PER_TURN_MIN_AMOUNT, (
        "fixture sanity: Prussia must earn enough for a minimal tribute"
    )
    dialogue = _stage_propose(world, terms=[{"type": "peace"}])
    recurring = [
        s for s in _suggestions_of(dialogue, "Prussia")
        if s["clause_type"] == "gold_per_turn" and s["group"] == "demand"
    ]
    assert recurring
    amount = recurring[0]["action_params"]["amount"]
    turns = recurring[0]["action_params"]["turns"]
    assert amount * turns <= 0 + income * turns
    assert amount >= GOLD_PER_TURN_MIN_AMOUNT
    assert recurring[0]["magnitude"]["amount"] == amount
    assert recurring[0]["magnitude"]["turns"] == turns

    # Existing recurring obligations consume the capacity (net rule).
    world2, _ = _three_court_world()
    world2.nation_gold["France"] = 2000
    world2.nation_gold["Prussia"] = 0
    world2.recurring_settlement_payments = [{
        "from": "Prussia", "to": "Russia",
        "amount_per_turn": 100000, "turns_remaining": 20,
    }]
    dialogue2 = _stage_propose(world2, terms=[{"type": "peace"}])
    assert not [
        s for s in _suggestions_of(dialogue2, "Prussia")
        if s["clause_type"] == "gold_per_turn" and s["group"] == "demand"
    ]


def test_suggestion_action_params_round_trip_through_add_verb():
    """The valid-by-construction proof: a suggestion's `action_params` fed
    VERBATIM to the GT-Slice-1 add verb succeeds, authors the suggested
    clause with its fixed direction, and the restaged row's
    `current_demands` renders the new line."""
    world, _ = _three_court_world()
    world.nation_gold["France"] = 2000
    dialogue = _stage_propose(world, terms=[{"type": "peace"}])
    territory = [
        s for s in _suggestions_of(dialogue, "Prussia")
        if s["clause_type"] == "territory_cede" and s["group"] == "demand"
    ][0]
    result = _demand_verb(
        world, dialogue, "settlement_demand_add", dict(territory["action_params"]),
    )
    assert result.get("success"), result
    restaged = result["diplomatic_dialogue"]
    added = [
        t for t in restaged["settlement_terms"]
        if t.get("type") == "territory_cede"
    ]
    assert added and added[0]["from"] == "Prussia" and added[0]["to"] == "France"
    assert added[0]["region"] == territory["action_params"]["region"]
    prussia = _row_of(restaged, "Prussia")
    assert any(
        line["clause_type"] == "territory_cede"
        and line["direction_tag"] == "Demanded"
        for line in prussia["current_demands"]
    )

    # And the offer arm: a France-paid sweetener suggestion on the losing
    # court round-trips the same way (D4).
    gold_offer = [
        s for s in _suggestions_of(restaged, "Britain")
        if s["clause_type"] == "gold_indemnity" and s["group"] == "offer"
    ][0]
    result2 = _demand_verb(
        world, restaged, "settlement_demand_add", dict(gold_offer["action_params"]),
    )
    assert result2.get("success"), result2
    britain = _row_of(result2["diplomatic_dialogue"], "Britain")
    assert any(
        line["direction_tag"] == "Conceded"
        and "France pays" in line["line_display"]
        for line in britain["current_demands"]
    )


# ===========================================================================
# Golden Rules #2 / #6 — int payloads, deterministic regeneration
# ===========================================================================


def test_demand_suggestions_are_deterministic_same_world():
    """Golden Rule #6: the same world stages the same suggestion payload —
    no vibes, no ordering drift."""
    def _build():
        world, _ = _three_court_world()
        world.nation_gold["France"] = 2000
        world.nation_gold["Prussia"] = 1000
        world.vassals["Saxony"] = {"lord": "Prussia", "loyalty": 50}
        dialogue = _stage_propose(world, terms=[{"type": "peace"}])
        return {
            str(row["nation"]): (
                row["demand_suggestions"], row["current_demands"],
                row["lead_group"], row["can_author"],
            )
            for row in dialogue["per_court_acceptance"]
        }

    assert _build() == _build()


def test_suggestion_payload_numerics_are_int():
    """Golden Rule #2: every numeric in the guided payload — suggestions,
    magnitude metadata, treasury line, recommendation — is int()."""
    world, _ = _three_court_world()
    world.nation_gold["France"] = 2000
    world.nation_gold["Prussia"] = 1000
    terms = [
        {"type": "peace"},
        {"type": "gold_per_turn", "from": "Prussia", "to": "France",
         "amount": 50, "turns": 3},
    ]
    dialogue = _stage_propose(world, terms=terms)
    for row in dialogue["per_court_acceptance"]:
        _assert_no_floats(row.get("demand_suggestions"), f"{row['nation']}.suggestions")
        _assert_no_floats(row.get("current_demands"), f"{row['nation']}.current")
    _assert_no_floats(dialogue.get("treasury_line"), "treasury_line")
    _assert_no_floats(
        dialogue.get("budget_bound_recommendation"), "budget_bound_recommendation",
    )


# ===========================================================================
# §8 OQ-6 — the budget-bound cheapest-signature recommendation
# ===========================================================================


def _budget_bound_world(*, france_gold: int, scores: dict, prussia_war: int = -70,
                        britain_war: int = -70):
    """France losing two covered courts with the treasury exhausted by a
    staged France-paid clause, so the PF-1 detector reports budget-bound
    (one more dial step would breach solvency)."""
    world, _ = _three_court_world(prussia=prussia_war, britain=britain_war)
    world.nation_gold["France"] = france_gold
    terms = [
        {"type": "peace"},
        {
            "type": "gold_indemnity", "from": "France", "to": "Britain",
            "amount": france_gold - 50,
        },
    ]
    dialogue = _stage_propose(
        world,
        terms=terms,
        covered=["Britain", "Prussia"],
        scorer=_make_scorer(scores),
    )
    return world, dialogue


def test_budget_bound_recommendation_ranks_cheapest_signature_first_deterministically():
    """OQ-6 (GT-A2): concede holdouts rank by `gap_to_threshold` ascending;
    the pool concentrates on coverable gaps cheapest-first at the live
    credit rate; the most expensive holdout is named the set-aside. Same
    world, same recommendation."""
    # Prussia gap 10 (40 vs 50), Britain gap 30 (20 vs 50). Pool = 1000
    # treasury - 50 reserve = 950. Prussia needs 10 * divisor (250) ->
    # coverable; Britain needs 750 > 700 left -> set aside.
    world, dialogue = _budget_bound_world(
        france_gold=1000, scores={"Prussia": 40, "Britain": 20},
    )
    rec = dialogue["budget_bound_recommendation"]
    assert rec.get("budget_bound") is True
    ranked = rec["ranked_holdouts"]
    assert [h["nation"] for h in ranked] == ["Prussia", "Britain"]
    assert ranked[0]["gap_to_threshold"] == 10
    assert ranked[0]["gold_needed"] == 10 * CONCESSION_GOLD_DIVISOR
    assert ranked[0]["coverable"] is True
    assert ranked[1]["gap_to_threshold"] == 30
    assert ranked[1]["coverable"] is False
    assert rec["concentrate_courts"] == ["Prussia"]
    assert rec["set_aside_court"] == "Britain"
    assert "Prussia" in rec["recommendation_display"]
    assert "Britain" in rec["recommendation_display"]

    # Deterministic regeneration (Golden Rule #6).
    _, dialogue2 = _budget_bound_world(
        france_gold=1000, scores={"Prussia": 40, "Britain": 20},
    )
    assert dialogue2["budget_bound_recommendation"] == rec


def test_budget_bound_recommendation_tie_breaks_on_abs_direct_score_then_name():
    """OQ-6 tie-break: equal gaps rank by larger `abs(direct_score)` first
    (the court pressing France hardest is the dearer peace), then name."""
    world, dialogue = _budget_bound_world(
        france_gold=1000,
        scores={"Prussia": 40, "Britain": 40},
        prussia_war=-30, britain_war=-70,
    )
    rec = dialogue["budget_bound_recommendation"]
    ranked = rec["ranked_holdouts"]
    assert [h["nation"] for h in ranked] == ["Britain", "Prussia"]
    assert ranked[0]["gap_to_threshold"] == ranked[1]["gap_to_threshold"] == 10
    assert abs(ranked[0]["direct_score"]) == 70
    # Pool 950 covers both 250-gold gaps -> nothing is set aside.
    assert rec["concentrate_courts"] == ["Britain", "Prussia"]
    assert rec["set_aside_court"] == ""


def test_budget_bound_recommendation_absent_when_not_bound():
    """OQ-6 trigger honesty: a treasury that can still raise the offer
    yields NO recommendation block (the targeted-posture advisory keeps
    the slot)."""
    world, _ = _three_court_world()
    world.nation_gold["France"] = 50000
    dialogue = _stage_propose(
        world,
        terms=[{"type": "peace"}],
        scorer=_make_scorer({"Prussia": 40, "Britain": 20}),
    )
    assert dialogue["budget_bound_recommendation"] == {}
