"""Settlement Guided Terms — GT-Slice-1 behavior tests.

`docs/SETTLEMENT_GUIDED_TERMS_SPEC.md` v0.2 §9 GT-Slice-1: the three
per-court demand-mutation verbs (`settlement_demand_add` /
`settlement_demand_remove` / `settlement_demand_set_magnitude`) resolved
via `action_params` against the staged `settlement_confirm`, each applying
the option's FIXED direction (D3/D4 — no identity ever crosses the
transport), mutating the draft through `_restage_settlement_after_redraw`
and re-scoring live; the §3.5 `authored_by` provenance tag + dial
composition rule; the §3.4 treasury line + table-scoped suggestion
defaults; and the §7 wiring/guard/failure contract (player-only,
PROPOSE-only, failures re-attach via the CH-5 wrapper).

Fixture idioms mirror `tests/test_settlement_refront_slice2.py`: a
synthetic France vs Britain + Prussia + Austria war with per-pair scores
chosen so the three live directions coexist (Prussia=demand,
Britain=concede, Austria=peace dead-band); the scorer is patched for
band-independent wiring tests and REAL for the D4 concession-credit pin.
"""

from __future__ import annotations

from unittest.mock import patch

from backend.game_logic.settlement_preview import (
    CONCESSION_BASELINE_GOLD_FLOOR,
    _guided_gold_offer_default,
    _guided_region_offer_candidate,
    compute_settlement_treasury_line,
    handle_settlement_dialogue_action,
    load_scoped_settlement_draft,
    stage_settlement_confirm,
)
from backend.game_logic.settlement_scoring import (
    MAX_SETTLEMENT_CLAUSE_COUNT,
    calculate_common_peace_acceptance,
)
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import (
    make_synthetic_war_instance,
)

_SCORER_PATH = "backend.game_logic.settlement_preview.calculate_common_peace_acceptance"


# ===========================================================================
# Helpers (slice-2 idioms)
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


def _terms_of(dialogue):
    return [dict(t) for t in (dialogue.get("settlement_terms") or [])]


# ===========================================================================
# Add / remove / adjust (§3.1, D3/D4 fixed direction)
# ===========================================================================


def test_add_territory_demand_appears_and_rescores():
    """§3.1: an added demand lands in the restaged terms with the option's
    fixed direction (court → France), carries the §3.5 provenance tag, and
    the table re-scores live (one scorer pass per covered court)."""
    world, _ = _three_court_world()
    dialogue = _stage_propose(world, terms=[{"type": "peace"}])
    seen = []
    base = _make_scorer({})

    def _spy(world=None, *, accepting_leader=None, **kw):
        seen.append(accepting_leader)
        return base(world, accepting_leader=accepting_leader, **kw)

    result = _demand_verb(
        world, dialogue, "settlement_demand_add",
        {"nation": "Prussia", "group": "demand", "clause_type": "territory_cede"},
        scorer=_spy,
    )
    assert result.get("success"), result
    nd = result["diplomatic_dialogue"]
    assert nd["dialogue_mode"] == "PROPOSE"
    added = [t for t in _terms_of(nd) if t.get("type") == "territory_cede"]
    assert len(added) == 1, _terms_of(nd)
    clause = added[0]
    # Direction fixed per option — never from params (D3).
    assert clause["from"] == "Prussia"
    assert clause["to"] == "France"
    # The default region is a real Prussian holding (demand-side selector).
    assert clause["region"] in set(world.get_nation_regions("Prussia"))
    # §3.5 provenance.
    assert clause.get("authored_by") == "player"
    # Live re-score touched every covered court.
    assert {"Britain", "Prussia", "Austria"} <= set(seen)


def test_remove_sticks_in_dialogue_and_scoped_draft():
    """§6: there is no merge blob — a removal mutates the single staged
    draft AND its persisted scoped copy, so nothing can re-add it."""
    world, _ = _three_court_world()
    world.nation_gold["Prussia"] = 2000
    terms = [
        {"type": "peace"},
        {"type": "gold_indemnity", "from": "Prussia", "to": "France", "amount": 200},
    ]
    dialogue = _stage_propose(world, terms=terms)
    result = _demand_verb(
        world, dialogue, "settlement_demand_remove",
        {"clause_index": 1, "expected_type": "gold_indemnity"},
    )
    assert result.get("success"), result
    nd = result["diplomatic_dialogue"]
    assert [t.get("type") for t in _terms_of(nd)] == ["peace"]
    # The scoped draft store holds the same post-removal truth (PF-2).
    persisted = load_scoped_settlement_draft(
        world,
        war_id="war_gt",
        selected_target_nation=str(nd.get("selected_target_nation") or ""),
        covered_enemy_participants=list(nd.get("covered_enemy_participants") or []),
    )
    assert persisted is not None
    assert [t.get("type") for t in persisted] == ["peace"]


def test_set_magnitude_adjusts_amount_only():
    """Identity is immutable (D3): `settlement_demand_set_magnitude` moves
    gold magnitude, never payer/payee, and marks the line player-authored."""
    world, _ = _three_court_world()
    world.nation_gold["Prussia"] = 2000
    terms = [
        {"type": "peace"},
        {"type": "gold_indemnity", "from": "Prussia", "to": "France", "amount": 200},
    ]
    dialogue = _stage_propose(world, terms=terms)
    result = _demand_verb(
        world, dialogue, "settlement_demand_set_magnitude",
        {"clause_index": 1, "amount": 350, "expected_type": "gold_indemnity"},
    )
    assert result.get("success"), result
    clause = _terms_of(result["diplomatic_dialogue"])[1]
    assert clause["amount"] == 350
    assert clause["from"] == "Prussia"
    assert clause["to"] == "France"
    # §3.5: a hand-set magnitude is player intent — the dials now protect it.
    assert clause.get("authored_by") == "player"


def test_set_magnitude_rejects_identity_bearing_clause():
    """Region/payer changes are remove + add — magnitude on a territory
    line fails with a rendered reason and the dialogue re-attached."""
    world, _ = _three_court_world()
    prussian_region = sorted(world.get_nation_regions("Prussia"))[0]
    terms = [
        {"type": "peace"},
        {
            "type": "territory_cede", "from": "Prussia", "to": "France",
            "region": prussian_region,
        },
    ]
    dialogue = _stage_propose(world, terms=terms)
    result = _demand_verb(
        world, dialogue, "settlement_demand_set_magnitude",
        {"clause_index": 1, "amount": 300},
    )
    assert result.get("success") is False
    assert result.get("error") == "magnitude_not_adjustable"
    assert result.get("error_display")
    assert result.get("diplomatic_dialogue")


def test_eligibility_gated_vassalize_rejected_when_ineligible():
    """§3.1/§4: eligibility-gated options reject BEFORE authoring — an
    already-vassal court cannot be vassalized, the refusal renders, and
    the dialogue re-attaches (never an invalid draft at the validator)."""
    world, _ = _three_court_world()
    world.vassals["Prussia"] = {"lord": "Austria", "loyalty": 50}
    dialogue = _stage_propose(world, terms=[{"type": "peace"}])
    result = _demand_verb(
        world, dialogue, "settlement_demand_add",
        {"nation": "Prussia", "group": "demand", "clause_type": "vassalage"},
    )
    assert result.get("success") is False
    assert result.get("error") == "dependency_target_already_vassal"
    assert result.get("error_display")
    assert result.get("diplomatic_dialogue")
    # Nothing was authored.
    assert [t.get("type") for t in _terms_of(result["diplomatic_dialogue"])] == ["peace"]


def test_losing_court_default_group_is_offer_and_demand_stays_legal():
    """§3.2/§3.3 + D5: on a concede-direction court an unqualified add lands
    on the OFFER arm (France pays — the court leads with offers), while an
    explicit demand-group add stays legal (press-past-zero agency)."""
    world, _ = _three_court_world()
    world.nation_gold["France"] = 5000
    world.nation_gold["Britain"] = 2000
    dialogue = _stage_propose(world, terms=[{"type": "peace"}])
    offered = _demand_verb(
        world, dialogue, "settlement_demand_add",
        {"nation": "Britain", "clause_type": "gold_indemnity", "amount": 150},
    )
    assert offered.get("success"), offered
    clause = [
        t for t in _terms_of(offered["diplomatic_dialogue"])
        if t.get("type") == "gold_indemnity"
    ][0]
    # Direction-led default on a losing court: France → Britain (offer).
    assert clause["from"] == "France"
    assert clause["to"] == "Britain"

    pressed = _demand_verb(
        world, offered["diplomatic_dialogue"], "settlement_demand_add",
        {
            "nation": "Britain", "group": "demand",
            "clause_type": "gold_indemnity", "amount": 100,
        },
    )
    assert pressed.get("success"), pressed
    demands = [
        t for t in _terms_of(pressed["diplomatic_dialogue"])
        if t.get("type") == "gold_indemnity" and t.get("from") == "Britain"
    ]
    assert len(demands) == 1  # D5: pressing the winning court is priced, not blocked.


def test_demand_direction_row_can_author_proposer_paid_sweetener_and_concession_credit_applies():
    """D4 (user-confirmed at approval): a France-paid sweetener on a
    DEMAND-direction court is legal, validates clean, and is mechanically
    rewarded — the REAL scorer's `concession_credit` component credits the
    court (0 → +8 for 200g: `min(40, amount // 25)`), the lever Tier 3's
    retirement would otherwise orphan."""
    world, inst = _three_court_world()
    world.nation_gold["France"] = 5000

    def _prussia_components(terms):
        return calculate_common_peace_acceptance(
            world,
            war_id="war_gt",
            war_instance=inst,
            proposer_side="attackers",
            accepting_side="defenders",
            accepting_leader="Prussia",
            proposer_side_leader="France",
            covered_enemy_participants=["Britain", "Prussia", "Austria"],
            settlement_terms=terms,
        )["components"]

    assert _prussia_components([{"type": "peace"}])["concession_credit"] == 0

    # Stage with the real scorer, then author the sweetener on Prussia's row.
    staged = stage_settlement_confirm(
        world,
        war_id="war_gt",
        actor_nation="France",
        settlement_terms=[{"type": "peace"}],
        covered_enemy_participants=["Britain", "Prussia", "Austria"],
        selected_target_nation="Austria",
        caller_kind="player_editor",
        dialogue_mode="PROPOSE",
    )
    assert staged.get("success"), staged
    result = handle_settlement_dialogue_action(
        world,
        action="settlement_demand_add",
        dialogue=staged["diplomatic_dialogue"],
        action_params={
            "action": "settlement_demand_add",
            "nation": "Prussia",
            "group": "offer",
            "clause_type": "gold_indemnity",
            "amount": 200,
        },
    )
    assert result.get("success"), result
    nd = result["diplomatic_dialogue"]
    sweetener = [
        t for t in _terms_of(nd) if t.get("type") == "gold_indemnity"
    ][0]
    assert (sweetener["from"], sweetener["to"]) == ("France", "Prussia")
    assert sweetener.get("authored_by") == "player"
    # The live scorer rewards the sweetener: min(40, 200 // 25) = +8.
    assert _prussia_components(_terms_of(nd))["concession_credit"] == 8


# ===========================================================================
# §3.5 — dial composition rule
# ===========================================================================


def test_whole_table_generous_does_not_silently_delete_player_authored_demand():
    """§3.5: ONE whole-table `More generous` click must not delete a
    hand-authored territory demand (the probe-verified hazard). The line
    survives, the skip is named in the response message, and suggested
    lines keep easing."""
    world, _ = _three_court_world()
    world.nation_gold["Prussia"] = 2000
    prussian_region = sorted(world.get_nation_regions("Prussia"))[0]
    terms = [
        {"type": "peace"},
        {
            "type": "territory_cede", "from": "Prussia", "to": "France",
            "region": prussian_region, "authored_by": "player",
        },
        # Talleyrand-suggested gold (no tag) keeps full legacy dial semantics.
        {"type": "gold_indemnity", "from": "Prussia", "to": "France", "amount": 300},
    ]
    dialogue = _stage_propose(world, terms=terms)
    result = _demand_verb(
        world, dialogue, "settlement_dial_generous", {"scope": "table"},
    )
    assert result.get("success"), result
    nd = result["diplomatic_dialogue"]
    survivors = _terms_of(nd)
    territory = [t for t in survivors if t.get("type") == "territory_cede"]
    assert len(territory) == 1, survivors  # the player's line stands
    assert territory[0]["region"] == prussian_region
    assert territory[0].get("authored_by") == "player"
    suggested_gold = [t for t in survivors if t.get("type") == "gold_indemnity"]
    assert suggested_gold and suggested_gold[0]["amount"] == 200  # eased 300 → 200
    # The protection is never invisible (§3.5 skip note).
    assert f"Your demand for {prussian_region} stands, Sire." in str(
        result.get("message") or ""
    )


def test_generous_dial_floors_player_authored_gold_instead_of_dropping():
    """§3.5: player-authored gold shrinks toward — never past — the dial
    step floor, where an untagged line would drop at zero."""
    world, _ = _three_court_world()
    world.nation_gold["Prussia"] = 2000
    terms = [
        {"type": "peace"},
        {
            "type": "gold_indemnity", "from": "Prussia", "to": "France",
            "amount": 100, "authored_by": "player",
        },
    ]
    dialogue = _stage_propose(world, terms=terms)
    result = _demand_verb(
        world, dialogue, "settlement_dial_generous", {"scope": "table"},
    )
    assert result.get("success"), result
    gold = [
        t for t in _terms_of(result["diplomatic_dialogue"])
        if t.get("type") == "gold_indemnity"
    ]
    assert gold, "player-authored gold line was dropped by the dial"
    assert gold[0]["amount"] == 100  # floored at the step, not dropped
    assert "stands, Sire." in str(result.get("message") or "")


# ===========================================================================
# §3.4 — one treasury, many courts
# ===========================================================================


def test_guided_gold_suggestion_caps_at_remaining_table_budget():
    """§3.4: the gold-OFFER default is TABLE-scoped — committed France-paid
    gold elsewhere in the package shrinks what a new offer may pre-fill,
    regardless of which court takes it."""
    world, _ = _three_court_world()
    world.nation_gold["France"] = 700  # reserve 500 → remaining 200
    no_commitments = []
    assert _guided_gold_offer_default(
        world, proposer_side_leader="France", settlement_terms=no_commitments,
    ) == 200
    committed = [
        {"type": "gold_indemnity", "from": "France", "to": "Britain", "amount": 100},
    ]
    # 700 − 100 committed − reserve(min(500, 600)=500) → 100 remaining.
    assert _guided_gold_offer_default(
        world, proposer_side_leader="France", settlement_terms=committed,
    ) == 100
    # A rich treasury is still bounded by the modest-default floor const.
    world.nation_gold["France"] = 5000
    assert _guided_gold_offer_default(
        world, proposer_side_leader="France", settlement_terms=no_commitments,
    ) == CONCESSION_BASELINE_GOLD_FLOOR
    # End-to-end: the authored offer carries the table-scoped default.
    world.nation_gold["France"] = 700
    dialogue = _stage_propose(world, terms=[{"type": "peace"}])
    result = _demand_verb(
        world, dialogue, "settlement_demand_add",
        {"nation": "Britain", "group": "offer", "clause_type": "gold_indemnity"},
    )
    assert result.get("success"), result
    clause = [
        t for t in _terms_of(result["diplomatic_dialogue"])
        if t.get("type") == "gold_indemnity"
    ][0]
    assert clause["amount"] == 200
    assert (clause["from"], clause["to"]) == ("France", "Britain")


def test_guided_region_suggestion_excludes_already_promised_regions():
    """§3.4: region-offer candidates exclude regions already promised
    ANYWHERE in the staged package (table-scoped V1), via the concede-side
    selector's exclusion param."""
    world, _ = _three_court_world()
    # France must hold captured (non-home, NON-CAPITAL) regions to have a
    # transferable offer candidate — the concede-side selector keeps
    # capitals and proposer home territory. Capture two real foreign
    # non-capital regions for France.
    captured = [
        name
        for name, region in sorted(world.regions.items())
        if not bool(getattr(region, "is_capital", False))
        and str(getattr(region, "controller", "")) != "France"
    ][:2]
    assert len(captured) == 2, captured
    for name in captured:
        world.regions[name].controller = "France"
    world.invalidate_active_nations_cache()
    free_pick = _guided_region_offer_candidate(
        world,
        court="Britain",
        proposer_side_participants=["France"],
        settlement_terms=[],
    )
    assert free_pick in captured
    # Promise the free pick elsewhere in the package — the candidate must
    # move to the other captured region, never double-promise.
    promised_terms = [
        {"type": "territory_cede", "from": "France", "to": "Austria", "region": free_pick},
    ]
    second_pick = _guided_region_offer_candidate(
        world,
        court="Britain",
        proposer_side_participants=["France"],
        settlement_terms=promised_terms,
    )
    assert second_pick in captured
    assert second_pick != free_pick


def test_treasury_line_is_int_block_on_propose_only():
    """§3.4: the PROPOSE payload carries the 4-int allocation block (Golden
    Rule #2); REVIEW (a frozen staged-decision surface) does not."""
    world, _ = _three_court_world()
    world.nation_gold["France"] = 1500
    terms = [
        {"type": "peace"},
        {"type": "gold_indemnity", "from": "France", "to": "Britain", "amount": 750},
        {"type": "gold_indemnity", "from": "France", "to": "Prussia", "amount": 750},
    ]
    dialogue = _stage_propose(world, terms=terms)
    line = dialogue.get("treasury_line")
    assert line == {"treasury": 1500, "committed": 1500, "reserve": 0, "remaining": 0}
    assert all(type(v) is int for v in line.values())
    # The §3.6 worked-example shape: untouched treasury keeps the reserve.
    fresh = compute_settlement_treasury_line(
        world, proposer_side_leader="France", settlement_terms=[{"type": "peace"}],
    )
    assert fresh == {"treasury": 1500, "committed": 0, "reserve": 500, "remaining": 1000}
    # Recurring obligations commit amount × turns.
    recurring = compute_settlement_treasury_line(
        world,
        proposer_side_leader="France",
        settlement_terms=[
            {"type": "gold_per_turn", "from": "France", "to": "Britain",
             "amount": 100, "turns": 5},
        ],
    )
    assert recurring["committed"] == 500
    review = _stage_propose(world, terms=[{"type": "peace"}], dialogue_mode="REVIEW")
    assert not review.get("treasury_line")


# ===========================================================================
# §3.1 clause cap + §7 guards / failure contract
# ===========================================================================


def test_add_demand_disabled_at_clause_cap_with_reason():
    """§3.1 (audit GT-R1-14): at `MAX_SETTLEMENT_CLAUSE_COUNT` the add verb
    rejects with the humanized reason — it never authors an over-cap draft
    for the restage validator to bounce."""
    world, _ = _three_court_world()
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
    result = _demand_verb(
        world, dialogue, "settlement_demand_add",
        {
            "nation": "Prussia", "group": "demand",
            "clause_type": "gold_indemnity", "amount": 100,
        },
    )
    assert result.get("success") is False
    assert result.get("error") == "max_clause_count_exceeded"
    assert "eight clauses" in str(result.get("error_display") or "")
    assert result.get("diplomatic_dialogue")
    assert len(_terms_of(result["diplomatic_dialogue"])) == MAX_SETTLEMENT_CLAUSE_COUNT


def test_demand_verbs_rejected_in_review_mode_with_error_display():
    """§7 guard (audit GT-R1-5): REVIEW is a frozen staged-decision surface —
    every mutation verb is rejected SERVER-SIDE (not by absent buttons),
    renders its reason, and re-attaches the mounted dialogue."""
    world, _ = _three_court_world()
    world.nation_gold["Prussia"] = 2000
    terms = [
        {"type": "peace"},
        {"type": "gold_indemnity", "from": "Prussia", "to": "France", "amount": 200},
    ]
    dialogue = _stage_propose(world, terms=terms, dialogue_mode="REVIEW")
    for action, params in (
        ("settlement_demand_add", {
            "nation": "Prussia", "group": "demand",
            "clause_type": "gold_indemnity", "amount": 100,
        }),
        ("settlement_demand_remove", {"clause_index": 1}),
        ("settlement_demand_set_magnitude", {"clause_index": 1, "amount": 300}),
    ):
        result = _demand_verb(world, dialogue, action, params)
        assert result.get("success") is False, (action, result)
        assert result.get("error") == "settlement_demand_requires_propose", action
        assert result.get("error_display"), action
        assert result.get("diplomatic_dialogue"), action
        # The staged decision is untouched.
        assert len(_terms_of(result["diplomatic_dialogue"])) == 2, action


def test_demand_verb_failure_reattaches_dialogue_never_silent():
    """§7 failure contract: whether the rejection is pre-checked (stale
    index, hard-stopped court) or comes back from the restage validator
    (insolvent demand), the response carries BOTH the re-attached dialogue
    and a rendered `error_display` — never neither (CH-5)."""
    world, _ = _three_court_world()
    world.nation_gold["Prussia"] = 100  # cannot pay a large demand
    dialogue = _stage_propose(world, terms=[{"type": "peace"}])

    # (a) restage-validator failure: an insolvent explicit demand.
    insolvent = _demand_verb(
        world, dialogue, "settlement_demand_add",
        {
            "nation": "Prussia", "group": "demand",
            "clause_type": "gold_indemnity", "amount": 99999,
        },
    )
    assert insolvent.get("success") is False
    assert insolvent.get("error_display"), insolvent
    assert insolvent.get("diplomatic_dialogue"), insolvent
    assert world.dialogue_manager.peek() is not None

    # (b) pre-checked failure: a stale clause index.
    stale = _demand_verb(
        world, dialogue, "settlement_demand_remove", {"clause_index": 99},
    )
    assert stale.get("success") is False
    assert stale.get("error") == "invalid_clause_index"
    assert stale.get("error_display")
    assert stale.get("diplomatic_dialogue")

    # (c) §3.3 hard-stop court: no authoring affordance, rendered reason.
    tweaked = dict(dialogue)
    tweaked["per_court_acceptance"] = [
        dict(row, direction="hard_stop")
        if str(row.get("nation")) == "Austria" else dict(row)
        for row in dialogue.get("per_court_acceptance") or []
    ]
    hard_stopped = _demand_verb(
        world, tweaked, "settlement_demand_add",
        {
            "nation": "Austria", "group": "demand",
            "clause_type": "gold_indemnity", "amount": 50,
        },
    )
    assert hard_stopped.get("success") is False
    assert hard_stopped.get("error") == "demand_court_hard_stopped"
    assert hard_stopped.get("error_display")
    assert hard_stopped.get("diplomatic_dialogue")


def test_propose_and_demand_routes_reject_non_player_caller_kind():
    """Slice-G boundary: the demand verbs are PLAYER-only — a non-player
    staging is refused before any mutation (and no popup re-attach is
    forced for a caller that has no popup to strand)."""
    world, _ = _three_court_world()
    dialogue = _stage_propose(world, terms=[{"type": "peace"}], caller_kind="ai_system")
    for action, params in (
        ("settlement_demand_add", {
            "nation": "Prussia", "group": "demand",
            "clause_type": "gold_indemnity", "amount": 100,
        }),
        ("settlement_demand_remove", {"clause_index": 0}),
        ("settlement_demand_set_magnitude", {"clause_index": 0, "amount": 100}),
    ):
        result = _demand_verb(world, dialogue, action, params)
        assert result.get("success") is False, (action, result)
        assert result.get("error") == "settlement_action_not_player_authored", action
        assert result.get("error_display"), action
        assert not result.get("diplomatic_dialogue"), action


def test_offer_group_rejected_for_demand_only_clause_types():
    """§4: dependency / forced-alliance / liberation clauses have no offer
    arm (a losing player cannot force the victor; France self-vassalage is
    not a player verb)."""
    world, _ = _three_court_world()
    dialogue = _stage_propose(world, terms=[{"type": "peace"}])
    for clause_type in ("vassalage", "subjugation", "forced_alliance", "liberation"):
        result = _demand_verb(
            world, dialogue, "settlement_demand_add",
            {"nation": "Prussia", "group": "offer", "clause_type": clause_type},
        )
        assert result.get("success") is False, clause_type
        assert result.get("error") == "offer_group_not_available", clause_type
        assert result.get("error_display"), clause_type


def test_peace_clause_is_not_removable():
    """§4: `peace` is the shared package clause, never a per-court line —
    striking it is refused with a rendered reason."""
    world, _ = _three_court_world()
    dialogue = _stage_propose(world, terms=[{"type": "peace"}])
    result = _demand_verb(
        world, dialogue, "settlement_demand_remove", {"clause_index": 0},
    )
    assert result.get("success") is False
    assert result.get("error") == "peace_clause_not_removable"
    assert result.get("error_display")
    assert result.get("diplomatic_dialogue")


# ===========================================================================
# §3.5 serialization — provenance survives save/load
# ===========================================================================


def test_authored_by_survives_save_load_round_trip():
    """§3.5 serialization rule: the provenance tag rides the scoped draft
    store through `to_dict` / `from_dict` unchanged."""
    world, _ = _three_court_world()
    world.nation_gold["Prussia"] = 2000
    dialogue = _stage_propose(world, terms=[{"type": "peace"}])
    result = _demand_verb(
        world, dialogue, "settlement_demand_add",
        {
            "nation": "Prussia", "group": "demand",
            "clause_type": "gold_indemnity", "amount": 200,
        },
    )
    assert result.get("success"), result
    restored = WorldState.from_dict(world.to_dict())
    drafts = getattr(restored, "pending_settlement_drafts_by_key", {}) or {}
    tagged = [
        clause
        for draft in drafts.values()
        for clause in draft
        if isinstance(clause, dict) and clause.get("authored_by") == "player"
    ]
    assert tagged, drafts
    assert tagged[0]["type"] == "gold_indemnity"
    assert tagged[0]["amount"] == 200
