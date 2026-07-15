"""PF-5 (Combat Overhaul Phase 6 — Parser & Play-Friction Cleanup).

Persistent NOTE spam: three notification families ("Treaty with Y", "Action
Accepted/Rejected/Dispatched", "Marshal X expects reward") were added once per
event but never dismissed, so they piled up and re-rendered every turn. The fix
dismisses-by-type (scoped by counterparty/marshal) BEFORE re-adding, so at most
one live notice per counterparty/marshal survives. The unmet-marshal reward
roll-up (morning dispatch) is additionally tagged `changed` so an unchanged,
re-rendered row can be de-emphasized.
"""
from pathlib import Path

from backend.models.world_state import WorldState
from backend.notifications import (
    create_notification, NotificationPriority,
    TREATY_SIGNED, DIPLOMATIC_PROPOSAL, DIPLOMATIC_PROPOSAL_RESULT,
    DOTATION_EXPECTATION,
)
from backend.main import _queue_informational_diplomacy_notices

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
    / "assets" / "maps" / "europe_1805.json"
)


def _pending_of_type(world, ntype):
    return [n for n in world.notifications.get_pending() if n.get("type") == ntype]


def _proposal_response(target, ptype="alliance"):
    return {"proposal_result": {
        "target_nation": target, "proposal_type": ptype,
        "message": f"{target} has responded.", "outcome": "ACCEPT"}}


# ── Part 1: production dedup of the proposal-result rail ─────────────────────

def test_proposal_result_dedup_same_target():
    world = WorldState()
    _queue_informational_diplomacy_notices(_proposal_response("Prussia"), world)
    _queue_informational_diplomacy_notices(_proposal_response("Prussia"), world)
    assert len(_pending_of_type(world, DIPLOMATIC_PROPOSAL_RESULT)) == 1


def test_proposal_result_two_targets_both_survive():
    world = WorldState()
    _queue_informational_diplomacy_notices(_proposal_response("Prussia"), world)
    _queue_informational_diplomacy_notices(_proposal_response("Austria"), world)
    assert len(_pending_of_type(world, DIPLOMATIC_PROPOSAL_RESULT)) == 2


def test_proposal_result_dedup_preserves_other_types():
    """FALSIFIABLE NEGATIVE: dismissing a proposal RESULT must not also dismiss
    a pending proposal (envoy-arrived) — a different type."""
    world = WorldState()
    world.notifications.add(create_notification(
        DIPLOMATIC_PROPOSAL, NotificationPriority.HIGH,
        "Prussia proposes", "An envoy has arrived.", 1,
        details={"target_nation": "Prussia"}))
    _queue_informational_diplomacy_notices(_proposal_response("Prussia"), world)
    _queue_informational_diplomacy_notices(_proposal_response("Prussia"), world)
    assert len(_pending_of_type(world, DIPLOMATIC_PROPOSAL)) == 1
    assert len(_pending_of_type(world, DIPLOMATIC_PROPOSAL_RESULT)) == 1


# ── Part 1: the shared details-filter dedup mechanism (TREATY_SIGNED /
#            DOTATION_EXPECTATION rely on the identical pattern) ─────────────

def test_dismiss_by_type_details_filter_collapses_same_key():
    world = WorldState()
    for _ in range(3):
        world.notifications.dismiss_by_type(
            TREATY_SIGNED,
            filter_fn=lambda n: n.get("details", {}).get("counterpart") == "Prussia")
        world.notifications.add(create_notification(
            TREATY_SIGNED, NotificationPriority.NORMAL, "Treaty with Prussia",
            "signed", 1, details={"counterpart": "Prussia"}))
    # Same counterparty collapses to one; a different one is independent.
    world.notifications.add(create_notification(
        TREATY_SIGNED, NotificationPriority.NORMAL, "Treaty with Austria",
        "signed", 1, details={"counterpart": "Austria"}))
    kept = _pending_of_type(world, TREATY_SIGNED)
    counterparts = sorted(n["details"]["counterpart"] for n in kept)
    assert counterparts == ["Austria", "Prussia"]


# ── Part 1: PRODUCTION-PATH guards for the other two families (review fix —
#            reverting either dismiss_by_type must now fail a test) ──────────

def _sign_peace(world, target):
    world._ratify_treaty({"type": "peace", "proposer_nation": "France",
                          "target_nation": target, "sweeteners": [],
                          "demands": [], "clauses": []})


def test_treaty_signed_dedup_via_ratify_treaty():
    """Drive the real _ratify_treaty path (a WAR->PEACE signing fires
    TREATY_SIGNED): two signings with the SAME counterparty collapse to one; a
    different counterparty stays independent. Prussia and Britain boot at WAR."""
    world = WorldState(player_nation="France")
    world.diplomatic_states[world._make_diplo_key("France", "Prussia")] = "WAR"
    world.diplomatic_states[world._make_diplo_key("France", "Austria")] = "WAR"
    _sign_peace(world, "Prussia")                       # fires (WAR->PEACE)
    # Reset Prussia to WAR and re-sign -> a SECOND TREATY_SIGNED for Prussia
    # that the dedup must collapse.
    world.diplomatic_states[world._make_diplo_key("France", "Prussia")] = "WAR"
    _sign_peace(world, "Prussia")                       # fires again -> dedup
    _sign_peace(world, "Austria")                       # independent counterparty
    counts = {}
    for n in _pending_of_type(world, TREATY_SIGNED):
        cp = n.get("details", {}).get("counterpart")
        counts[cp] = counts.get(cp, 0) + 1
    assert counts.get("Prussia") == 1  # deduped across two signings
    assert counts.get("Austria") == 1  # independent counterparty


def test_dotation_expectation_dedup_via_process():
    """Drive the real _process_dotation_state path: a met->unmet re-open keeps at
    most one live reward-expectation notice per marshal."""
    world = WorldState.from_scenario(str(SCENARIO_PATH))
    marshal = next(m for m in world.marshals.values()
                   if m.nation == "France" and m.strength > 0)
    marshal.battles_won = 5      # expectation 200
    marshal.dotation_regions = []
    marshal.pension = 0
    marshal.expectation_grace_turn = -1

    world._process_dotation_state()                 # first unmet -> fires
    marshal.expectation_grace_turn = -1             # simulate met->unmet re-open
    world._dotation_processed_turn = None           # allow a second reconcile
    world._process_dotation_state()                 # fires again -> must dedup

    notices = [n for n in _pending_of_type(world, DOTATION_EXPECTATION)
               if n.get("details", {}).get("marshal") == marshal.name]
    assert len(notices) == 1


