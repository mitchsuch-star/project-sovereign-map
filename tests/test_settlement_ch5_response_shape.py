"""CH-5 — the ONE structural invariant for settlement dialogue responses.

Pre-flight audit §9 CH-5: *every settlement handler failure returns a
re-attached ``diplomatic_dialogue`` AND a rendered ``error_display`` —
never neither.* Every settlement defect class found at the Gate-4
pre-flight (the drop-stranding orphan, D2's "Response processed", D3's
silent dials, D7's latent replacement-stage orphan) was this invariant
violated at a different arm. The cure is one wrapper at the dispatch
boundary (``handle_settlement_dialogue_action`` →
``_enforce_settlement_response_shape``) instead of the retired per-arm
Tier-2 re-attach net — covering the replacement-stage preset family the
old net never reached, and every future arm by construction.
"""

from __future__ import annotations

from unittest.mock import patch

from backend.game_logic.settlement_preview import (
    SETTLEMENT_EDITOR_CALLER_KIND,
    handle_settlement_dialogue_action,
    stage_settlement_confirm,
)
from backend.game_logic.settlement_actions import (
    _enforce_settlement_response_shape,
)
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import (
    make_synthetic_war_instance,
)


def _set_pair_score_for_france(world, opponent: str, score_for_france: int):
    pair = "|".join(sorted(("France", opponent)))
    first = pair.split("|")[0]
    world.war_scores[pair] = (
        score_for_france if first == "France" else -score_for_france
    )


def _two_court_world(score_for_france: int = 60):
    """France (attacker) vs Britain + Prussia (defenders), both pairs at
    ``score_for_france`` — the minimal settlement-eligible shape."""
    world = WorldState()
    war = make_synthetic_war_instance(
        "war_ch5",
        attackers=["France"],
        defenders=["Britain", "Prussia"],
        attacker_leader="France",
        defender_leader="Britain",
        created_turn=1,
        created_sequence=1,
    )
    world.war_instances["war_ch5"] = war
    for opponent in ("Britain", "Prussia"):
        pair = "|".join(sorted(("France", opponent)))
        world.diplomatic_states[pair] = "WAR"
        _set_pair_score_for_france(world, opponent, score_for_france)
    world.nation_gold["France"] = 5000
    world.invalidate_war_instance_indexes()
    return world, war


def _stage_propose(world, covered):
    staged = stage_settlement_confirm(
        world,
        war_id="war_ch5",
        actor_nation="France",
        selected_target_nation=covered[0],
        covered_enemy_participants=covered,
        caller_kind="player_editor",
        dialogue_mode="PROPOSE",
    )
    assert staged.get("success"), staged
    return staged["diplomatic_dialogue"]


_PLAYER_DIALOGUE = {
    "type": "settlement_confirm",
    "caller_kind": SETTLEMENT_EDITOR_CALLER_KIND,
    "war_id": "war_ch5",
}


# ---------------------------------------------------------------------------
# Unit — the enforcer itself
# ---------------------------------------------------------------------------


def test_enforcer_attaches_dialogue_and_error_display_to_bare_failure():
    """The D2 class: a bare ``{"success": False}`` gains BOTH halves."""
    shaped = _enforce_settlement_response_shape(
        {"success": False, "error": "unknown_settlement_action", "mutated": False},
        _PLAYER_DIALOGUE,
    )
    assert shaped["diplomatic_dialogue"] == _PLAYER_DIALOGUE
    assert shaped["awaiting_diplomatic_response"] is True
    assert shaped["error_display"]


def test_enforcer_synthesizes_error_display_from_error_code():
    """The D3 class: a failure that re-attached its dialogue but rendered
    nothing gains a humanized ``error_display`` from the error code."""
    shaped = _enforce_settlement_response_shape(
        {
            "success": False,
            "error": "no_covered_enemy_participants",
            "diplomatic_dialogue": dict(_PLAYER_DIALOGUE),
        },
        _PLAYER_DIALOGUE,
    )
    assert shaped["error_display"]
    # Never the raw internal code (display-map or humanized fallback).
    assert shaped["error_display"] != "no_covered_enemy_participants"


def test_enforcer_does_not_attach_dialogue_for_non_player_caller():
    """Slice-G boundary: a non-player staging has no popup to strand — no
    re-attach, but the failure still renders."""
    ai_dialogue = dict(_PLAYER_DIALOGUE, caller_kind="ai_system")
    shaped = _enforce_settlement_response_shape(
        {"success": False, "error": "unknown_settlement_action"},
        ai_dialogue,
    )
    assert not shaped.get("diplomatic_dialogue")
    assert shaped["error_display"]


def test_enforcer_leaves_success_untouched():
    """Dialogue-closing successes (back out / suspend / ratify) pass through
    identically — the wrapper never force-reattaches a closed surface."""
    closing_success = {
        "success": True,
        "action": "back_out",
        "cancelled": True,
        "mutated": False,
    }
    shaped = _enforce_settlement_response_shape(closing_success, _PLAYER_DIALOGUE)
    assert shaped is closing_success
    assert "diplomatic_dialogue" not in shaped
    assert "error_display" not in shaped


def test_enforcer_passes_non_mapping_through():
    assert _enforce_settlement_response_shape(None, _PLAYER_DIALOGUE) is None


def test_enforcer_preserves_existing_failure_fields():
    """An already-shaped failure is not overwritten — arm-rendered copy wins."""
    failure = {
        "success": False,
        "error": "dial_scope_not_covered",
        "error_display": "Denmark is not part of this settlement, Sire.",
        "diplomatic_dialogue": {"type": "settlement_confirm"},
    }
    shaped = _enforce_settlement_response_shape(failure, _PLAYER_DIALOGUE)
    assert shaped["error_display"] == "Denmark is not part of this settlement, Sire."
    assert shaped["diplomatic_dialogue"] == {"type": "settlement_confirm"}


# ---------------------------------------------------------------------------
# End-to-end — the public dispatch wrapper
# ---------------------------------------------------------------------------


def test_unknown_action_failure_is_shaped_end_to_end():
    """The dispatch fallthrough returns a bare failure; through the public
    wrapper it must re-mount the popup and render the reason."""
    world, _ = _two_court_world()
    _stage_propose(world, ["Britain", "Prussia"])
    mounted = world.dialogue_manager.peek()
    result = handle_settlement_dialogue_action(
        world,
        action="definitely_not_a_settlement_action",
        dialogue=mounted,
        action_params={},
    )
    assert result.get("success") is False
    assert result.get("error") == "unknown_settlement_action"
    assert result.get("diplomatic_dialogue"), result
    assert result.get("error_display"), result
    assert world.dialogue_manager.peek() is not None


def test_d7_replacement_stage_failure_reattaches_dialogue():
    """D7 regression (pre-flight §2): the replacement-stage preset family
    fails validation → pre-CH-5 the response carried no
    ``diplomatic_dialogue`` while the mounted dialogue stayed up (latent
    orphan, outside the old five-verb net). Whichever replacement-family
    failure branch fires, the wrapper now guarantees the shape."""
    world, _ = _two_court_world(score_for_france=-60)  # losing → concession family
    _stage_propose(world, ["Britain", "Prussia"])
    mounted = world.dialogue_manager.peek()
    assert mounted is not None
    with patch(
        "backend.game_logic.settlement_ratify.validate_settlement_terms",
        return_value={
            "valid": False,
            "error": "region_double_promised",
            "error_index": 1,
            "disabled_reason_display": "forced invalid (test)",
        },
    ):
        result = handle_settlement_dialogue_action(
            world,
            action="apply_concession_baseline_replacement",
            dialogue=mounted,
            action_params={},
        )
    assert result.get("success") is False
    assert result.get("diplomatic_dialogue"), (
        "replacement-stage failure orphaned the popup (D7): %r" % (result,)
    )
    assert result.get("error_display"), result
    assert world.dialogue_manager.peek() is not None


def test_suspend_settlement_editor_close_success_not_reattached():
    """The non-destructive suspend pops the dialogue ON PURPOSE — the wrapper
    must not re-attach a surface the player just closed."""
    world, _ = _two_court_world()
    _stage_propose(world, ["Britain", "Prussia"])
    mounted = world.dialogue_manager.peek()
    result = handle_settlement_dialogue_action(
        world,
        action="suspend_settlement_editor",
        dialogue=mounted,
        action_params={},
    )
    assert result.get("success") is True
    assert not result.get("diplomatic_dialogue")


def test_dial_scope_failure_still_shaped_after_net_removal():
    """Regression for the retired per-arm net: the Tier-2 rejection that
    motivated it (dial scoped off-table) keeps its re-attach + reason."""
    world, _ = _two_court_world()
    _stage_propose(world, ["Britain", "Prussia"])
    mounted = world.dialogue_manager.peek()
    result = handle_settlement_dialogue_action(
        world,
        action="settlement_dial_generous",
        dialogue=mounted,
        action_params={"action": "settlement_dial_generous", "scope": "Denmark"},
    )
    assert result.get("success") is False
    assert result.get("error") == "dial_scope_not_covered"
    assert result.get("diplomatic_dialogue"), result
    assert result.get("error_display"), result
    assert world.dialogue_manager.peek() is not None
