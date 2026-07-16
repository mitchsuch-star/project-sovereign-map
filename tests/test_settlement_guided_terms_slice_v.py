"""Settlement Guided Terms — GT-Slice-V behavior tests (voice).

`docs/SETTLEMENT_GUIDED_TERMS_SPEC.md` v0.2 §9 GT-Slice-V: Talleyrand
suggests demands in-character (the `settlement_guided_reason_*_talleyrand`
families resolve every suggestion `reason_display`); affected named
diplomats react to authored lines (the §16.1a `settlement_multi_court_
demand_received` / `offer_received` families, resolved through
`resolve_named_diplomat` with chancery fallback — never anonymous); the
DC-4 guard line lands VERBATIM from the Gate-4 pre-flight audit and fires
whenever a demand is authored (demand-group add) or seeded (focused-
Harsher dial seed) on a concede-direction court (D5); the OQ-6
budget-bound recommendation extends `settlement_budget_bound_constraint_
talleyrand` in the advisory slot; and the §5 incoming-offer revision copy
retargets onto the guided table. SC-32 D5 boundary (no conference /
congress / veto) holds across all new committed copy.

Fixture idioms mirror `tests/test_settlement_guided_terms_slice1.py`.
"""

from __future__ import annotations

from unittest.mock import patch

from backend.game_logic.diplomatic_templates import (
    SETTLEMENT_VOICE_TEMPLATES,
    get_settlement_voice_template,
    resolve_settlement_voice_line,
)
from backend.game_logic.settlement_preview import (
    handle_settlement_dialogue_action,
    stage_settlement_confirm,
)
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import (
    make_synthetic_war_instance,
)

_SCORER_PATH = "backend.game_logic.settlement_scoring.calculate_common_peace_acceptance"

# The DC-4 guard line, verbatim from `docs/SETTLEMENT_GATE4_PREFLIGHT_AUDIT.md`
# §DC-4 as folded into the Guided Terms spec §9 GT-Slice-V.
_DC4_GUARD_LINE = "They are not the ones suing for peace, Sire — but as you wish."


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


def _make_scorer(score_by_leader: dict, default: int = 60):
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


def _stage_propose(world, *, war_id="war_gt", terms=None, covered=None, scorer=None):
    scorer = scorer or _make_scorer({})
    covered = covered or ["Britain", "Prussia", "Austria"]
    with patch(_SCORER_PATH, side_effect=scorer):
        staged = stage_settlement_confirm(
            world,
            war_id=war_id,
            actor_nation="France",
            settlement_terms=terms,
            covered_enemy_participants=covered,
            selected_target_nation=covered[-1],
            caller_kind="player_editor",
            dialogue_mode="PROPOSE",
        )
    assert staged.get("success"), staged
    return staged["diplomatic_dialogue"]


def _settlement_action(world, dialogue, action, params, scorer=None):
    scorer = scorer or _make_scorer({})
    with patch(_SCORER_PATH, side_effect=scorer):
        return handle_settlement_dialogue_action(
            world,
            action=action,
            dialogue=dialogue,
            action_params={"action": action, **params},
        )


def _beats(result, kind=None):
    beats = list(result.get("authoring_voice_beats") or [])
    if kind is not None:
        beats = [b for b in beats if b.get("kind") == kind]
    return beats


# ===========================================================================
# DC-4 guard line (D5 press-past-zero — authored OR seeded)
# ===========================================================================


def test_demand_on_concede_direction_court_fires_talleyrand_caution_voice():
    """Spec-pinned (§9 GT-Slice-V): an explicit demand-group add on a court
    that is BEATING France (Britain, concede direction) fires the DC-4
    guard line verbatim, on both the result and the restaged dialogue."""
    world, _ = _three_court_world()
    dialogue = _stage_propose(world, terms=[{"type": "peace"}])
    result = _settlement_action(
        world, dialogue, "settlement_demand_add",
        {"nation": "Britain", "group": "demand", "clause_type": "gold_indemnity",
         "amount": 150},
    )
    assert result.get("success"), result
    cautions = _beats(result, kind="talleyrand_caution")
    assert len(cautions) == 1
    assert cautions[0]["line"] == _DC4_GUARD_LINE
    assert cautions[0]["speaker"] == "Talleyrand"
    assert cautions[0]["nation"] == "Britain"
    # The beat rides the restaged dialogue (the popup renders from it).
    dialogue_beats = [
        b for b in (result["diplomatic_dialogue"].get("authoring_voice_beats") or [])
        if b.get("kind") == "talleyrand_caution"
    ]
    assert dialogue_beats and dialogue_beats[0]["line"] == _DC4_GUARD_LINE
    # The demand itself was authored (legal agency — voiced, not blocked).
    added = [
        t for t in result["diplomatic_dialogue"]["settlement_terms"]
        if t.get("type") == "gold_indemnity"
    ]
    assert added and added[0]["from"] == "Britain"


def test_demand_on_demand_direction_court_fires_no_caution():
    """Pressing the court France is beating (Prussia) is the ordinary case —
    no guard line; the named-court reaction still fires."""
    world, _ = _three_court_world()
    world.nation_gold["Prussia"] = 2000
    dialogue = _stage_propose(world, terms=[{"type": "peace"}])
    result = _settlement_action(
        world, dialogue, "settlement_demand_add",
        {"nation": "Prussia", "group": "demand", "clause_type": "gold_indemnity",
         "amount": 150},
    )
    assert result.get("success"), result
    assert _beats(result, kind="talleyrand_caution") == []
    assert len(_beats(result, kind="court_reaction")) == 1


def test_offer_on_concede_court_fires_no_caution_but_court_reaction():
    """The §3.2 default arm on a losing court is the OFFER — France pays;
    nothing absurd to voice. The court still reacts (offer_received)."""
    world, _ = _three_court_world()
    world.nation_gold["France"] = 5000
    dialogue = _stage_propose(world, terms=[{"type": "peace"}])
    result = _settlement_action(
        world, dialogue, "settlement_demand_add",
        {"nation": "Britain", "clause_type": "gold_indemnity", "amount": 150},
    )
    assert result.get("success"), result
    assert _beats(result, kind="talleyrand_caution") == []
    reactions = _beats(result, kind="court_reaction")
    assert len(reactions) == 1
    assert reactions[0]["nation"] == "Britain"
    expected = resolve_settlement_voice_line(
        "settlement_multi_court_offer_received",
        speaker=reactions[0]["speaker"],
        court="Britain",
        offer_label="150 gold from France",
        demand_label="150 gold from France",
    )
    assert reactions[0]["line"] == expected


def test_focused_harsher_seed_on_concede_court_fires_caution():
    """DC-4's original corner: a focused `Press <court>` on a court with no
    live clause SEEDS a demand; on a concede-direction court Talleyrand no
    longer authors it wordlessly."""
    world, _ = _three_court_world()
    dialogue = _stage_propose(world, terms=[{"type": "peace"}])
    result = _settlement_action(
        world, dialogue, "settlement_dial_harsher", {"scope": "Britain"},
    )
    assert result.get("success"), result
    cautions = _beats(result, kind="talleyrand_caution")
    assert len(cautions) == 1
    assert cautions[0]["line"] == _DC4_GUARD_LINE
    assert cautions[0]["nation"] == "Britain"


def test_focused_seed_fires_no_caution_on_demand_court_or_ease():
    """The guard is specific: a harsher seed on the DEMAND-direction court is
    ordinary pressing; a generous (ease) seed is France paying — neither
    is the DC-4 absurdity."""
    world, _ = _three_court_world()
    dialogue = _stage_propose(world, terms=[{"type": "peace"}])
    pressed = _settlement_action(
        world, dialogue, "settlement_dial_harsher", {"scope": "Prussia"},
    )
    assert pressed.get("success"), pressed
    assert _beats(pressed, kind="talleyrand_caution") == []

    world2, _ = _three_court_world()
    world2.nation_gold["France"] = 5000
    dialogue2 = _stage_propose(world2, terms=[{"type": "peace"}])
    eased = _settlement_action(
        world2, dialogue2, "settlement_dial_generous", {"scope": "Britain"},
    )
    assert eased.get("success"), eased
    assert _beats(eased, kind="talleyrand_caution") == []


def test_caution_beats_are_one_shot_dropped_by_next_restage():
    """The beats describe ONE mutation: the next restage rebuilds the
    dialogue without them (the popup never replays a stale caution)."""
    world, _ = _three_court_world()
    world.nation_gold["Prussia"] = 2000
    dialogue = _stage_propose(world, terms=[{"type": "peace"}])
    first = _settlement_action(
        world, dialogue, "settlement_demand_add",
        {"nation": "Britain", "group": "demand", "clause_type": "gold_indemnity",
         "amount": 150},
    )
    assert _beats(first, kind="talleyrand_caution")
    second = _settlement_action(
        world, first["diplomatic_dialogue"], "settlement_demand_add",
        {"nation": "Prussia", "group": "demand", "clause_type": "gold_indemnity",
         "amount": 100},
    )
    assert second.get("success"), second
    new_dialogue = second["diplomatic_dialogue"]
    kinds = [b.get("kind") for b in (new_dialogue.get("authoring_voice_beats") or [])]
    assert "talleyrand_caution" not in kinds
    # Only the Prussia reaction from THIS mutation remains.
    reactions = [
        b for b in (new_dialogue.get("authoring_voice_beats") or [])
        if b.get("kind") == "court_reaction"
    ]
    assert [b["nation"] for b in reactions] == ["Prussia"]


# ===========================================================================
# Named-court reactions (§16.1a resolver rule — never anonymous)
# ===========================================================================


def test_demand_add_fires_named_court_reaction():
    """The affected court answers through its NAMED diplomat: Prussia is
    Hardenberg's voice (the §16.1a resolver rule)."""
    world, _ = _three_court_world()
    world.nation_gold["Prussia"] = 2000
    dialogue = _stage_propose(world, terms=[{"type": "peace"}])
    result = _settlement_action(
        world, dialogue, "settlement_demand_add",
        {"nation": "Prussia", "group": "demand", "clause_type": "gold_indemnity",
         "amount": 200},
    )
    assert result.get("success"), result
    reactions = _beats(result, kind="court_reaction")
    assert len(reactions) == 1
    assert "Hardenberg" in reactions[0]["speaker"]
    assert reactions[0]["line"]
    assert reactions[0]["speaker"] in reactions[0]["line"]


def test_court_reaction_resolves_chancery_fallback_never_anonymous():
    """A covered court with no named envoy (Russia) resolves to its chancery
    — a voice, never an anonymous beat."""
    world = WorldState()
    inst = make_synthetic_war_instance(
        "war_gt",
        attackers=["France"],
        defenders=["Britain", "Prussia", "Russia"],
        attacker_leader="France",
        defender_leader="Britain",
    )
    world.war_instances["war_gt"] = inst
    _set_war_score(world, "France", "Prussia", 70)
    _set_war_score(world, "France", "Britain", -70)
    _set_war_score(world, "France", "Russia", 70)
    world.invalidate_war_instance_indexes()
    world.nation_gold["Russia"] = 2000  # the demanded gold must be payable
    dialogue = _stage_propose(
        world, terms=[{"type": "peace"}],
        covered=["Britain", "Prussia", "Russia"],
    )
    result = _settlement_action(
        world, dialogue, "settlement_demand_add",
        {"nation": "Russia", "group": "demand", "clause_type": "gold_indemnity",
         "amount": 100},
    )
    assert result.get("success"), result
    reactions = _beats(result, kind="court_reaction")
    assert len(reactions) == 1
    assert reactions[0]["speaker"] == "The Chancery of Russia"
    assert reactions[0]["line"]


# ===========================================================================
# In-character suggestion reasons (settlement_guided_reason_* families)
# ===========================================================================


def test_guided_suggestion_reasons_resolve_committed_templates():
    """Every suggestion `reason_display` resolves through a committed
    `settlement_guided_reason_*_talleyrand` template — no f-string copy
    survives in the payload path. Pinned exactly for the gold demand."""
    world, _ = _three_court_world()
    world.nation_gold["Prussia"] = 2000
    world.nation_gold["France"] = 5000
    dialogue = _stage_propose(world, terms=[{"type": "peace"}])
    rows = {
        r["nation"]: r for r in dialogue["per_court_acceptance"]
    }
    prussia = rows["Prussia"]
    suggestions = prussia["demand_suggestions"]
    assert suggestions
    for suggestion in suggestions:
        assert suggestion["reason_display"], suggestion
    gold = next(
        s for s in suggestions
        if s["clause_type"] == "gold_indemnity" and s["group"] == "demand"
    )
    expected = resolve_settlement_voice_line(
        "settlement_guided_reason_gold_demand_talleyrand",
        court="Prussia",
        amount=int(gold["action_params"]["amount"]),
    )
    assert gold["reason_display"] == expected
    # And the offer-side sweetener resolves its own family on the concede
    # court (Britain leads with offers — §3.2).
    britain = rows["Britain"]
    gold_offer = next(
        s for s in britain["demand_suggestions"]
        if s["clause_type"] == "gold_indemnity" and s["group"] == "offer"
    )
    expected_offer = resolve_settlement_voice_line(
        "settlement_guided_reason_gold_offer_talleyrand",
        court="Britain",
        amount=int(gold_offer["action_params"]["amount"]),
    )
    assert gold_offer["reason_display"] == expected_offer


# ===========================================================================
# OQ-6 budget-bound recommendation voice extension
# ===========================================================================


def test_budget_bound_recommendation_carries_talleyrand_voice_extension():
    """OQ-6 (GT-A2): the computed cheapest-signature recommendation gains an
    in-character `recommendation_voice` that EXTENDS the binding-constraint
    line in the advisory slot (constraint first, then the allocation)."""
    # France losing BOTH covered courts (concede direction) with the treasury
    # exhausted by a staged France-paid clause — the slice-2 OQ-6 fixture.
    world, _ = _three_court_world(prussia=-70, britain=-70)
    world.nation_gold["France"] = 1000
    terms = [
        {"type": "peace"},
        {"type": "gold_indemnity", "from": "France", "to": "Britain", "amount": 950},
    ]
    dialogue = _stage_propose(
        world, terms=terms, covered=["Britain", "Prussia"],
        scorer=_make_scorer({"Prussia": 40, "Britain": 20}),
    )
    rec = dialogue["budget_bound_recommendation"]
    assert rec.get("budget_bound") is True
    expected_voice = resolve_settlement_voice_line(
        "settlement_budget_bound_recommendation_talleyrand",
        concentrate_names="Prussia",
        set_aside_court="Britain",
    )
    assert rec["recommendation_voice"] == expected_voice
    advisory = dialogue["targeted_posture_advisory"]
    # Constraint line first, recommendation appended (one advisory string).
    assert "cannot satisfy" in advisory
    assert expected_voice in advisory
    assert advisory.index("cannot satisfy") < advisory.index("cheapest signatures")


# ===========================================================================
# §5 incoming-offer revision copy retarget
# ===========================================================================


def test_incoming_offer_revision_copy_retargeted_to_guided_table():
    """Guided Terms §5 (GT-Slice-V): the Request Revision beat survives but
    lands on the guided table — the committed copy no longer references
    opening an editor."""
    template = get_settlement_voice_template(
        "settlement_incoming_offer_request_revision_talleyrand",
    )
    assert template
    assert "on our own table" in template
    assert "editor" not in template.lower()
    assert "open the offered terms" not in template
    resolved = resolve_settlement_voice_line(
        "settlement_incoming_offer_request_revision_talleyrand",
        war_label="France vs Britain",
        proposer_leader="Britain",
    )
    assert "France vs Britain" in resolved
    assert "Britain" in resolved


# ===========================================================================
# SC-32 D5 copy boundary over the new families
# ===========================================================================


def test_guided_terms_voice_families_hold_sc32_d5_copy_boundary():
    """The D5 boundary (no conference/congress/veto) extends over every
    GT-Slice-V family: guided reasons, the DC-4 caution, the authoring
    reactions, and the budget-bound recommendation variants."""
    banned = ("conference", "congress", "veto")
    covered_prefixes = (
        "settlement_guided_reason_",
        "settlement_demand_on_concede_court_caution",
        "settlement_multi_court_demand_received",
        "settlement_multi_court_offer_received",
        "settlement_budget_bound_recommendation",
    )
    walked = 0
    for key, template in SETTLEMENT_VOICE_TEMPLATES.items():
        if not key.startswith(covered_prefixes):
            continue
        walked += 1
        lowered = template.lower()
        assert not any(word in lowered for word in banned), key
    # 11 guided reasons + caution + 2 reactions + 3 recommendation variants;
    # VS-5 (July 16, 2026) added the vassal_transfer guided reason (+1 = 18).
    assert walked == 18
