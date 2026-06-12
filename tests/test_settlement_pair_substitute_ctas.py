"""SC-29 / G2-Slice-7 pair-scoped peace substitute CTA tests.

The rejected settlement popup may surface `Seek Bilateral Peace` and
`Seek Armistice Instead` only after SC-29 / G2-Slice-7 lands, and only
when the selected target pair is eligible under
`evaluate_pair_peace_substitute_eligibility(...)`. These tests pin the
spec-required behavior from `docs/SETTLEMENT_UI_CLEANUP_SPEC.md` SC-29
section, the Pair substitute eligibility helper schema, and the
G2-Slice-7 required-tests list at the bottom of the slice budget table.
"""

from __future__ import annotations

from backend.game_logic.settlement_preview import (
    build_settlement_confirm_dialogue,
    build_settlement_preview,
    evaluate_pair_peace_substitute_eligibility,
    get_reopen_attempts,
    handle_settlement_dialogue_action,
    load_scoped_settlement_draft,
    PAIR_SUBSTITUTE_REFUSAL_CODES,
    PAIR_SUBSTITUTE_TEMPORAL_REFUSAL_CODES,
    save_scoped_settlement_draft,
    stage_settlement_confirm,
)
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import (
    make_synthetic_war_instance,
)


def _install_rejected_war(world: WorldState) -> dict:
    war = make_synthetic_war_instance(
        "war_1",
        attackers=["France", "Saxony"],
        defenders=["Austria", "Prussia"],
        attacker_leader="France",
        defender_leader="Austria",
        created_turn=1,
        created_sequence=1,
    )
    world.war_instances["war_1"] = war
    for pair in war["active_diplo_keys"]:
        a, _ = pair.split("|")
        world.diplomatic_states[pair] = "WAR"
        # Heavy losing-side scores so the staged dialogue blocks ratify.
        world.war_scores[pair] = 80 if a != "France" else -80
    world.war_exhaustion["Austria"] = 5
    world.invalidate_war_instance_indexes()
    return war


def _stage_rejected_dialogue(world: WorldState, selected_target: str = "Austria") -> dict:
    """Return the dialogue dict staged from a rejected-war fixture."""
    staged = stage_settlement_confirm(
        world,
        war_id="war_1",
        covered_enemy_participants=["Austria", "Prussia"],
        selected_target_nation=selected_target,
    )
    return staged["diplomatic_dialogue"]


# ───────────────────────────────────────────────────────────────────────
# Helper schema + closed taxonomy (spec line 455-460)
# ───────────────────────────────────────────────────────────────────────


def test_pair_substitute_eligibility_helper_schema_matches_canonical_keys():
    world = WorldState()
    _install_rejected_war(world)

    result = evaluate_pair_peace_substitute_eligibility(
        world,
        war_id="war_1",
        actor_nation="France",
        target_nation="Austria",
        action="seek_bilateral_peace",
    )

    assert set(result.keys()) == {
        "eligible",
        "refusal_code",
        "disabled_reason_display",
        "selected_pair",
    }
    assert result["selected_pair"] == {
        "actor": "France",
        "target": "Austria",
        "war_id": "war_1",
    }
    assert result["eligible"] is True
    assert result["refusal_code"] is None
    assert result["disabled_reason_display"] is None


def test_pair_substitute_refusal_code_taxonomy_is_closed_set():
    """Every refusal code returned by the helper must come from the spec's
    closed taxonomy in `PAIR_SUBSTITUTE_REFUSAL_CODES`."""
    expected = {
        "already_at_peace",
        "already_in_armistice",
        "pair_not_at_war",
        "war_archived",
        "actor_not_at_war_with_target",
        "target_not_selected_pair",
        "target_not_in_war",
        "settlement_collision_active",
        "cooldown_active",
        "insufficient_resources",
        "malformed_route",
    }
    assert PAIR_SUBSTITUTE_REFUSAL_CODES == expected
    # Helper must never invent a code outside the closed taxonomy.
    world = WorldState()
    _install_rejected_war(world)
    # Force every code we can reach from helper inputs and confirm each
    # one is inside the closed taxonomy.
    for action in ("seek_bilateral_peace", "seek_armistice_instead"):
        for nations in (
            ("", "Austria"),
            ("France", ""),
            ("France", "France"),
            ("France", "Spain"),  # non-participant
            ("Spain", "Austria"),  # actor not participant
            ("France", "Saxony"),  # same-side pair
        ):
            result = evaluate_pair_peace_substitute_eligibility(
                world,
                war_id="war_1",
                actor_nation=nations[0],
                target_nation=nations[1],
                action=action,
            )
            if result["eligible"]:
                continue
            assert result["refusal_code"] in expected, result


def test_pair_substitute_resolved_pair_maps_to_closed_refusal_code():
    """Resolved-pair metadata must not escape the SC-29 closed taxonomy."""
    world = WorldState()
    war = _install_rejected_war(world)
    pair = world._make_diplo_key("France", "Austria")
    war["resolved_diplo_keys"] = [pair]
    war["diplo_key_meta"][pair]["pair_status"] = "resolved"

    result = evaluate_pair_peace_substitute_eligibility(
        world,
        war_id="war_1",
        actor_nation="France",
        target_nation="Austria",
        action="seek_bilateral_peace",
    )

    assert result["eligible"] is False
    assert result["refusal_code"] == "pair_not_at_war"
    assert result["refusal_code"] in PAIR_SUBSTITUTE_REFUSAL_CODES


def test_pair_substitute_eligibility_helper_matches_backend_refusal_codes():
    """The displayed reasons round-trip through the settlement display map
    and never expose raw internal enum strings."""
    world = WorldState()
    _install_rejected_war(world)

    result = evaluate_pair_peace_substitute_eligibility(
        world,
        war_id="war_archived_id",
        actor_nation="France",
        target_nation="Austria",
        action="seek_bilateral_peace",
    )
    # Unknown / non-active war id surfaces malformed_route.
    assert result["eligible"] is False
    assert result["refusal_code"] == "malformed_route"
    assert isinstance(result["disabled_reason_display"], str)
    assert result["disabled_reason_display"]
    assert "malformed_route" not in result["disabled_reason_display"]


# ───────────────────────────────────────────────────────────────────────
# Disabled vs Hidden Affordance Policy (spec lines 208-218)
# ───────────────────────────────────────────────────────────────────────


def test_pair_substitute_temporal_refusal_codes_render_disabled_with_reason():
    world = WorldState()
    _install_rejected_war(world)
    # cooldown_active is the only temporal refusal code per the policy.
    world.player_proposal_cooldowns["Austria"] = 3

    dialogue = _stage_rejected_dialogue(world)
    options = dialogue["options"]
    by_action = {opt["action"]: opt for opt in options}

    # SC-29 + Disabled vs Hidden Policy: temporal refusal renders disabled.
    assert "seek_bilateral_peace" in by_action
    disabled_option = by_action["seek_bilateral_peace"]
    assert disabled_option.get("available") is False
    assert disabled_option["disabled_reason_display"]
    assert "cooldown_active" not in disabled_option["disabled_reason_display"]
    # `available_action_ids[]` only lists actionable controls; disabled
    # temporal buttons stay in `options[]` for display.
    assert "seek_bilateral_peace" not in dialogue["available_action_ids"]


def test_pair_substitute_terminal_refusal_codes_render_absent():
    world = WorldState()
    _install_rejected_war(world)
    # Mark the Austria pair as already at peace — terminal refusal,
    # substitute action must be hidden, not disabled.
    world.diplomatic_states["Austria|France"] = "PEACE"

    dialogue = _stage_rejected_dialogue(world)
    options = dialogue["options"]
    actions = [opt["action"] for opt in options]
    assert "seek_bilateral_peace" not in actions
    assert "seek_armistice_instead" not in actions


# ───────────────────────────────────────────────────────────────────────
# Rejected popup integration (spec lines 1160-1166, 406)
# ───────────────────────────────────────────────────────────────────────


def test_post_sc29_rejected_popup_renders_substitute_ctas_below_re_author_above_war_detail_within_1080p():
    """Order per failure-state control table:
    Re-author -> Revise Terms -> Seek Bilateral Peace ->
    Seek Armistice Instead -> Open War Detail -> Back Out.
    """
    world = WorldState()
    _install_rejected_war(world)

    dialogue = _stage_rejected_dialogue(world)
    assert dialogue["can_ratify"] is False
    order = [opt["action"] for opt in dialogue["options"]]

    # No disabled Ratify; substitute CTAs appear below Re-author (when
    # eligible) and above Open War Detail.
    assert "confirm_settlement" not in order
    assert "seek_bilateral_peace" in order
    assert "seek_armistice_instead" in order
    assert "open_war_detail" in order
    assert order.index("seek_bilateral_peace") < order.index("seek_armistice_instead")
    assert order.index("seek_armistice_instead") < order.index("open_war_detail")
    if "re_author_with_concessions" in order:
        assert order.index("re_author_with_concessions") < order.index("seek_bilateral_peace")


def test_rejected_popup_substitute_peace_absent_before_sc29_present_with_pair_scope_after_sc29():
    """Post-SC-29 substitute CTAs are present with scope='selected_pair'.
    The absent-before-SC-29 branch is enforced structurally: a target
    pair that is already at peace / archived hides the substitute action
    instead of rendering a disabled placeholder (the same code path that
    was the entire pre-SC-29 default before the feature shipped)."""
    world = WorldState()
    _install_rejected_war(world)

    # Post-SC-29 with selected target: substitute CTAs are present,
    # explicitly pair-scoped, and carry the selected target.
    dialogue = _stage_rejected_dialogue(world)
    by_action = {opt["action"]: opt for opt in dialogue["options"]}
    for action_id in ("seek_bilateral_peace", "seek_armistice_instead"):
        assert action_id in by_action
        entry = by_action[action_id]
        assert entry["scope"] == "selected_pair"
        assert entry["war_id"] == "war_1"
        assert entry["selected_target_nation"] == "Austria"

    # Hidden path (terminal refusal) — proves substitute CTAs disappear
    # cleanly without leaving disabled placeholders. This is the same
    # absence guarantee that protected pre-SC-29 cleanup popups.
    world.diplomatic_states["Austria|France"] = "PEACE"
    world.diplomatic_states["Prussia|France"] = "PEACE"
    hidden = stage_settlement_confirm(
        world,
        war_id="war_1",
        covered_enemy_participants=["Austria", "Prussia"],
        selected_target_nation="Austria",
    )["diplomatic_dialogue"]
    actions_hidden = [opt["action"] for opt in hidden["options"]]
    assert "seek_bilateral_peace" not in actions_hidden
    assert "seek_armistice_instead" not in actions_hidden


# ───────────────────────────────────────────────────────────────────────
# Click-time eligibility re-validation (spec line 1163)
# ───────────────────────────────────────────────────────────────────────


def test_pair_substitute_click_time_reresolution_blocks_when_pair_state_changed():
    """If the pair becomes ineligible between render and click, the
    handler refuses to mutate, does not pop the dialogue's war_id from
    the dialogue manager mid-flow, and returns a humanized refusal."""
    world = WorldState()
    _install_rejected_war(world)

    dialogue = _stage_rejected_dialogue(world)
    assert "seek_bilateral_peace" in [opt["action"] for opt in dialogue["options"]]

    # Pair flips to peace between render and click.
    world.diplomatic_states["Austria|France"] = "PEACE"

    result = handle_settlement_dialogue_action(
        world, action="seek_bilateral_peace", dialogue=dialogue,
    )
    assert result["success"] is False
    assert result["mutated"] is False
    assert result["error"] == "already_at_peace"
    assert isinstance(result["error_display"], str) and result["error_display"]
    # Pair substitute eligibility payload is echoed so the popup can
    # render the refusal without re-fetching state.
    assert result["pair_substitute_eligibility"]["refusal_code"] == "already_at_peace"


def test_pair_substitute_clicks_do_not_consume_reopen_attempts():
    """SC-14b reopen attempts are for settlement reopen paths, not SC-29
    direct pair-substitute handoffs or click-time refusals."""
    world = WorldState()
    _install_rejected_war(world)
    dialogue = _stage_rejected_dialogue(world)

    assert get_reopen_attempts(world, war_id="war_1") == 0
    success = handle_settlement_dialogue_action(
        world, action="seek_bilateral_peace", dialogue=dialogue,
    )
    assert success["success"] is True
    assert get_reopen_attempts(world, war_id="war_1") == 0

    refused_world = WorldState()
    _install_rejected_war(refused_world)
    refused_dialogue = _stage_rejected_dialogue(refused_world)
    refused_world.diplomatic_states["Austria|France"] = "PEACE"

    refusal = handle_settlement_dialogue_action(
        refused_world, action="seek_bilateral_peace", dialogue=refused_dialogue,
    )
    assert refusal["success"] is False
    assert get_reopen_attempts(refused_world, war_id="war_1") == 0


# ───────────────────────────────────────────────────────────────────────
# Successful pair-scoped substitution staging (spec lines 1169-1170)
# ───────────────────────────────────────────────────────────────────────


def _confirm_pair_substitute(world, first_result):
    """G4F-8: the substitute mounts a confirm chooser first (the joint
    draft survives until Proceed). Drive the second beat and return the
    handoff result the pre-G4F-8 pins asserted on."""
    assert first_result["success"] is True, first_result.get("error_display")
    chooser = first_result["diplomatic_dialogue"]
    assert chooser["type"] == "settlement_pair_substitute_confirm"
    return handle_settlement_dialogue_action(
        world, action="confirm_pair_substitute", dialogue=chooser,
    )


def test_seek_bilateral_peace_instead_creates_per_pair_peace_with_selected_target_only():
    """The substitute CTA stages a proposal_confirm dialogue scoped to
    the selected pair only. Other hostile pairs in the same war remain
    untouched."""
    world = WorldState()
    _install_rejected_war(world)

    dialogue = _stage_rejected_dialogue(world)
    result = _confirm_pair_substitute(world, handle_settlement_dialogue_action(
        world, action="seek_bilateral_peace", dialogue=dialogue,
    ))
    assert result["success"] is True
    assert result["mutated"] is False
    assert result["scope"] == "selected_pair"
    assert result["selected_target_nation"] == "Austria"
    assert result["proposal_type"] == "peace"
    # Other hostile pairs remain at WAR; no broad mutation occurred.
    assert world.diplomatic_states["Austria|France"] == "WAR"
    assert world.diplomatic_states["France|Prussia"] == "WAR"
    # The settlement dialogue has been popped and replaced.
    assert world.pending_diplomatic_dialogue is not None
    assert world.pending_diplomatic_dialogue.get("type") == "proposal_confirm"
    assert world.pending_diplomatic_dialogue.get("target_nation") == "Austria"
    assert world.pending_diplomatic_dialogue.get("context", {}).get("proposal_type") == "peace"
    assert result["recovery_route"]["target"] == "proposal_confirm"
    assert result["recovery_route"]["target_nation"] == "Austria"


def test_seek_armistice_instead_creates_per_pair_armistice_with_selected_target_only():
    world = WorldState()
    _install_rejected_war(world)

    dialogue = _stage_rejected_dialogue(world)
    result = _confirm_pair_substitute(world, handle_settlement_dialogue_action(
        world, action="seek_armistice_instead", dialogue=dialogue,
    ))
    assert result["success"] is True
    assert result["mutated"] is False
    assert result["scope"] == "selected_pair"
    assert result["selected_target_nation"] == "Austria"
    assert result["proposal_type"] == "armistice"
    assert world.pending_diplomatic_dialogue is not None
    assert world.pending_diplomatic_dialogue.get("type") == "proposal_confirm"
    assert world.pending_diplomatic_dialogue.get("target_nation") == "Austria"
    assert world.pending_diplomatic_dialogue.get("context", {}).get("proposal_type") == "armistice"
    assert result["recovery_route"]["target"] == "proposal_confirm"
    assert result["recovery_route"]["target_nation"] == "Austria"
    # Other hostile pairs remain at WAR.
    assert world.diplomatic_states["Austria|France"] == "WAR"
    assert world.diplomatic_states["France|Prussia"] == "WAR"
    # No vassalage / forced-alliance / region transfer occurred.
    assert world.diplomatic_states["Austria|Saxony"] == "WAR"


# ───────────────────────────────────────────────────────────────────────
# Draft preservation / invalidation (spec line 1164, lines 429-433)
# ───────────────────────────────────────────────────────────────────────


def test_pair_substitute_handoff_preserves_or_invalidates_scoped_draft_correctly():
    """A successful pair substitute that covers the target pair makes
    the existing scoped settlement draft stale (cleanup keys drafts by
    war_id). A pair substitute against a target outside the draft's
    covered scope leaves the draft intact."""
    world = WorldState()
    _install_rejected_war(world)

    # Draft covering Austria — pair substitute on Austria invalidates it.
    terms = [{"type": "gold_indemnity", "from": "Austria", "to": "France", "amount": 50}]
    dialogue = _stage_rejected_dialogue(world, selected_target="Austria")
    save_scoped_settlement_draft(
        world,
        war_id="war_1",
        selected_target_nation=dialogue.get("selected_target_nation"),
        covered_enemy_participants=dialogue.get("covered_enemy_participants"),
        settlement_terms=list(terms),
    )
    result = _confirm_pair_substitute(world, handle_settlement_dialogue_action(
        world, action="seek_bilateral_peace", dialogue=dialogue,
    ))
    assert result["success"] is True
    assert result["draft_invalidated"] is True
    assert load_scoped_settlement_draft(
        world,
        war_id="war_1",
        selected_target_nation=dialogue.get("selected_target_nation"),
        covered_enemy_participants=dialogue.get("covered_enemy_participants"),
    ) is None

    # Preservation branch: dialogue's covered scope does NOT include the
    # substitute target. Per spec line 1164, draft invalidation is
    # scope-keyed — if the affected pair is outside the draft's covered
    # scope, the saved draft remains valid for the OTHER pairs.
    world2 = WorldState()
    _install_rejected_war(world2)
    save_scoped_settlement_draft(
        world2,
        war_id="war_1",
        selected_target_nation="Prussia",
        covered_enemy_participants=["Austria"],
        settlement_terms=list(terms),
    )
    dialogue_off_scope = {
        "type": "settlement_confirm",
        "war_id": "war_1",
        "war_label": "war_1",
        "selected_target_nation": "Prussia",
        "covered_enemy_participants": ["Austria"],  # not including Prussia
        "settlement_terms": [],
        "caller_kind": "player_editor",
    }
    result_off_scope = _confirm_pair_substitute(
        world2,
        handle_settlement_dialogue_action(
            world2, action="seek_bilateral_peace", dialogue=dialogue_off_scope,
        ),
    )
    # Substitute action succeeds against Prussia; Prussia is NOT in the
    # dialogue's covered scope (which lists only Austria), so the saved
    # draft (scoped to this dialogue's Austria coverage) is preserved.
    assert result_off_scope["success"] is True
    assert result_off_scope["draft_invalidated"] is False
    assert load_scoped_settlement_draft(
        world2,
        war_id="war_1",
        selected_target_nation="Prussia",
        covered_enemy_participants=["Austria"],
    ) == terms


def test_pair_substitute_cross_war_collision_uses_closed_refusal_code():
    """A mounted settlement review for another war blocks substitute handoff
    without staging a second settlement-family route."""
    world = WorldState()
    _install_rejected_war(world)
    _stage_rejected_dialogue(world)

    war_2 = make_synthetic_war_instance(
        "war_2",
        attackers=["France"],
        defenders=["Britain"],
        attacker_leader="France",
        defender_leader="Britain",
        created_turn=1,
        created_sequence=2,
    )
    world.war_instances["war_2"] = war_2
    for pair in war_2["active_diplo_keys"]:
        world.diplomatic_states[pair] = "WAR"

    result = evaluate_pair_peace_substitute_eligibility(
        world,
        war_id="war_2",
        actor_nation="France",
        target_nation="Britain",
        action="seek_bilateral_peace",
    )

    assert result["eligible"] is False
    assert result["refusal_code"] == "settlement_collision_active"
    assert result["refusal_code"] in PAIR_SUBSTITUTE_REFUSAL_CODES


# ───────────────────────────────────────────────────────────────────────
# Voice family routing (spec lines 1174-1175)
# ───────────────────────────────────────────────────────────────────────


def test_seek_bilateral_peace_instead_routes_through_committed_voice_family_not_generic_fallback():
    world = WorldState()
    _install_rejected_war(world)

    dialogue = _stage_rejected_dialogue(world)
    by_action = {opt["action"]: opt for opt in dialogue["options"]}
    entry = by_action["seek_bilateral_peace"]
    assert entry["voice_family"] == (
        "settlement_seek_bilateral_peace_instead_talleyrand"
    )
    assert "Austria" in entry["talleyrand_text"]
    # The confirmed handoff stamps the voice family.
    result = _confirm_pair_substitute(world, handle_settlement_dialogue_action(
        world, action="seek_bilateral_peace", dialogue=dialogue,
    ))
    assert result["voice_family"] == (
        "settlement_seek_bilateral_peace_instead_talleyrand"
    )
    assert "Austria" in result["talleyrand_text"]


def test_seek_armistice_instead_routes_through_committed_voice_family_not_generic_fallback():
    world = WorldState()
    _install_rejected_war(world)

    dialogue = _stage_rejected_dialogue(world)
    by_action = {opt["action"]: opt for opt in dialogue["options"]}
    entry = by_action["seek_armistice_instead"]
    assert entry["voice_family"] == "settlement_seek_armistice_instead_talleyrand"
    assert "Austria" in entry["talleyrand_text"]
    result = _confirm_pair_substitute(world, handle_settlement_dialogue_action(
        world, action="seek_armistice_instead", dialogue=dialogue,
    ))
    assert result["voice_family"] == "settlement_seek_armistice_instead_talleyrand"
    assert "Austria" in result["talleyrand_text"]


# ───────────────────────────────────────────────────────────────────────
# Helper isolation (spec line 444)
# ───────────────────────────────────────────────────────────────────────


def test_settlement_helper_signatures_are_distinct_and_not_substituted():
    """Pair substitute eligibility must not collapse into War Detail
    actionability or Open Settlement eligibility."""
    world = WorldState()
    _install_rejected_war(world)

    # Pair substitute helper takes per-pair actor/target + action.
    pair_result = evaluate_pair_peace_substitute_eligibility(
        world,
        war_id="war_1",
        actor_nation="France",
        target_nation="Austria",
        action="seek_bilateral_peace",
    )
    assert "eligible" in pair_result
    # Distinct schema from war-detail actionability.
    assert "actionable" not in pair_result
    assert "actionable_kind" not in pair_result
    # The closed temporal refusal set covers only cooldown_active.
    assert PAIR_SUBSTITUTE_TEMPORAL_REFUSAL_CODES == {"cooldown_active"}
    # G4F-16: the disabled-with-reason render set widens to the
    # player-actionable states; everything else stays hidden.
    from backend.game_logic.settlement_validation import (
        PAIR_SUBSTITUTE_DISABLED_RENDER_CODES,
    )
    assert PAIR_SUBSTITUTE_DISABLED_RENDER_CODES == {
        "cooldown_active",
        "already_in_armistice",
        "insufficient_resources",
    }


# ───────────────────────────────────────────────────────────────────────
# G2-Gate4-Repair-1: Dispatch reaches handler through executor entry
# ───────────────────────────────────────────────────────────────────────


def test_dialogue_response_routes_seek_bilateral_peace_through_executor_dispatch():
    """Gate 4 smoke regression: clicking the rejected-popup substitute
    CTA arrives at the executor through `/respond_to_diplomatic_dialogue`,
    which calls `DiplomaticExecutor.handle_diplomatic_dialogue_response`
    with the 1-based option index. The action must reach
    `handle_settlement_dialogue_action` instead of falling through to
    "Unknown dialogue action: seek_bilateral_peace".

    Pre-repair, the dispatch tuple in `_process_dialogue_choice` only
    routed four ids; this test would have failed with a fall-through
    "Unknown dialogue action" message. The unit tests in this file
    called `handle_settlement_dialogue_action` directly and never
    exercised the dispatch arm — which is exactly how the regression
    shipped past Gate 3."""
    from backend.commands.diplomatic_executor import DiplomaticExecutor

    world = WorldState()
    _install_rejected_war(world)
    dialogue = _stage_rejected_dialogue(world)
    # Find the 1-based option index for seek_bilateral_peace in the
    # staged dialogue's options list, exactly as Godot would.
    options = dialogue.get("options", [])
    target_idx = None
    for idx, opt in enumerate(options, start=1):
        if opt.get("action") == "seek_bilateral_peace":
            target_idx = idx
            break
    assert target_idx is not None, (
        f"Staged rejected dialogue does not expose seek_bilateral_peace "
        f"in options; got actions {[o.get('action') for o in options]}"
    )

    executor = DiplomaticExecutor(None)
    result = executor.handle_diplomatic_dialogue_response(
        target_idx, {"world": world}
    )

    # The handler must NOT report Unknown dialogue action.
    message = str(result.get("message", ""))
    assert "Unknown dialogue action" not in message, (
        f"Executor dispatch fell through to 'Unknown dialogue action' "
        f"for seek_bilateral_peace: {result}"
    )
    # Positive contract: the substitute handler popped the settlement
    # dialogue and staged a proposal_confirm for the pair.
    assert result.get("success") is True, result
    assert result.get("scope") == "selected_pair"
    assert result.get("selected_target_nation") == "Austria"
    assert result.get("proposal_type") == "peace"


def test_dialogue_response_routes_seek_armistice_instead_through_executor_dispatch():
    """Symmetric Gate 4 regression for `seek_armistice_instead`."""
    from backend.commands.diplomatic_executor import DiplomaticExecutor

    world = WorldState()
    _install_rejected_war(world)
    dialogue = _stage_rejected_dialogue(world)
    options = dialogue.get("options", [])
    target_idx = None
    for idx, opt in enumerate(options, start=1):
        if opt.get("action") == "seek_armistice_instead":
            target_idx = idx
            break
    assert target_idx is not None

    executor = DiplomaticExecutor(None)
    result = executor.handle_diplomatic_dialogue_response(
        target_idx, {"world": world}
    )

    message = str(result.get("message", ""))
    assert "Unknown dialogue action" not in message, result
    assert result.get("success") is True
    assert result.get("scope") == "selected_pair"
    assert result.get("proposal_type") == "armistice"
