"""G2-Slice-3 Continuity behavior tests.

Closes SC-14, SC-14b, SC-14c, SC-14d, SC-14e, SC-7b, SC-26 per
`docs/SETTLEMENT_UI_CLEANUP_SPEC.md` §G2-Slice-3.

Each test maps explicitly to a spec row so a future audit can cross-walk
spec -> behavior fixture without re-reading the file.
"""

from __future__ import annotations

from backend.display_names import settlement_disabled_reason_display
from backend.game_logic.settlement_preview import (
    build_settlement_confirm_dialogue,
    build_settlement_preview,
    derive_settlement_review_target,
    handle_incoming_settlement_offer_action,
    is_war_archived,
    is_war_known,
    load_scoped_settlement_draft,
    mint_settlement_route_id,
    record_reopen_attempt,
    reopen_attempt_cap_exceeded,
    resolve_settlement_route_click,
    SETTLEMENT_FAMILY_DIALOGUE_TYPES,
    SETTLEMENT_REOPEN_MAX_ATTEMPTS,
    SETTLEMENT_ROUTE_NAMESPACE,
    stage_settlement_confirm,
)
from backend.game_logic.settlement_presentation import (
    SETTLEMENT_REVIEW_TARGET_ACTIVE,
    SETTLEMENT_REVIEW_TARGET_ARCHIVED,
    recent_settlement_summaries,
    settlement_notification_meta,
    settlement_review_target,
)
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import (
    make_synthetic_war_instance,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _install_war(
    world: WorldState,
    war_id: str = "war_1",
    *,
    attackers: list = None,
    defenders: list = None,
    attacker_leader: str = "France",
    defender_leader: str = "Austria",
) -> dict:
    if attackers is None:
        attackers = ["France", "Saxony"]
    if defenders is None:
        defenders = ["Austria", "Prussia"]
    war = make_synthetic_war_instance(
        war_id,
        attackers=attackers,
        defenders=defenders,
        attacker_leader=attacker_leader,
        defender_leader=defender_leader,
        created_turn=1,
        created_sequence=int(war_id.replace("war_", "") or "1") if war_id.startswith("war_") and war_id[4:].isdigit() else 1,
    )
    world.war_instances[war_id] = war
    for pair in war["active_diplo_keys"]:
        world.diplomatic_states[pair] = "WAR"
    world.invalidate_war_instance_indexes()
    return war


def _install_high_acceptance_war(world: WorldState, war_id: str = "war_1") -> dict:
    """High-acceptance fixture mirroring `_install_two_v_two_war` from
    `test_common_peace_c2_ratification.py`. Used by tests that need
    `ratify_settlement_confirm` to pass the SC-3 acceptance gate."""
    war = _install_war(world, war_id=war_id)
    for pair in war["active_diplo_keys"]:
        nations = pair.split("|")
        world.war_start_turns[pair] = world.current_turn
        first = nations[0]
        score = 100 if first not in ("France", "Saxony") else -100
        world.war_scores[pair] = -score
        world.battle_records[pair] = []
    world.war_exhaustion["Austria"] = 500
    world.war_exhaustion["Prussia"] = 500
    world.war_objectives = getattr(world, "war_objectives", {})
    world.war_objectives[war_id] = [{
        "type": "conquest",
        "declaring_nation": "France",
        "target_nation": "Austria",
        "side": "attackers",
    }]
    world.invalidate_war_instance_indexes()
    return war


def _stage(world: WorldState, *, war_id: str = "war_1") -> dict:
    return stage_settlement_confirm(
        world,
        war_id=war_id,
        covered_enemy_participants=["Austria"] if war_id == "war_1" else ["Prussia"],
    )


# ---------------------------------------------------------------------------
# SC-14c: route id format `settlement:{war_id}:{turn}:{seq}`
# ---------------------------------------------------------------------------


def test_route_id_uses_settlement_namespace_with_per_turn_seq():
    world = WorldState()
    _install_war(world)
    world.current_turn = 7
    preview = build_settlement_preview(world, war_id="war_1")
    dialogue = build_settlement_confirm_dialogue(world, preview)
    assert dialogue["route_id"] == "settlement:war_1:7:1"
    assert dialogue["route_id"].startswith(f"{SETTLEMENT_ROUTE_NAMESPACE}:")
    assert dialogue["route"]["route_id"] == "settlement:war_1:7:1"
    # Old format must not regress.
    assert dialogue["route_id"] != "war_1:7"


def test_route_id_seq_increments_for_two_same_turn_events_for_one_war():
    """SC-14c required test: two settlement events for one `(war_id, turn)`
    must not collide on the focus id."""
    world = WorldState()
    world.current_turn = 7
    _install_war(world, "war_1")
    a = mint_settlement_route_id(world, war_id="war_1")
    b = mint_settlement_route_id(world, war_id="war_1")
    assert a == "settlement:war_1:7:1"
    assert b == "settlement:war_1:7:2"
    # Different war on same turn does not share counter state.
    c = mint_settlement_route_id(world, war_id="war_2")
    assert c == "settlement:war_2:7:1"
    # Sequence persists on world state for serialization.
    assert world.settlement_route_seq["war_1"][7] == 2
    assert world.settlement_route_seq["war_2"][7] == 1


def test_route_id_resets_seq_for_a_new_turn():
    world = WorldState()
    world.current_turn = 5
    _install_war(world, "war_1")
    a = mint_settlement_route_id(world, war_id="war_1")
    world.current_turn = 6
    b = mint_settlement_route_id(world, war_id="war_1")
    assert a == "settlement:war_1:5:1"
    assert b == "settlement:war_1:6:1"


def test_route_id_consumers_all_read_staged_value():
    """SC-14c required test: staged dialogue, reaction event, result feedback,
    dispatch, ledger, and notification metadata all consume the same staged
    `route_id` in one fixture."""
    from backend.game_logic.settlement_preview import ratify_settlement_confirm

    world = WorldState()
    world.current_turn = 7
    _install_high_acceptance_war(world)
    staged = stage_settlement_confirm(
        world,
        war_id="war_1",
        covered_enemy_participants=["Austria"],
        # G2-Slice-W1 empty-Ratify gate: editor-staged empty drafts cannot
        # ratify. Continuity tests author a minimum legitimate peace
        # package to probe routing rather than the gate.
        settlement_terms=[{"type": "peace"}],
    )
    dialogue = staged["diplomatic_dialogue"]
    staged_route_id = dialogue["route_id"]
    assert staged_route_id.startswith("settlement:war_1:7:")

    result = ratify_settlement_confirm(world, dialogue)
    assert result["success"] is True, f"ratify failed: {result.get('error')}"
    # Reaction summary event reuses the staged id.
    summary_event = result["settlement_reactions"]["summary_event"]
    assert summary_event["route"]["route_id"] == staged_route_id
    # Result feedback consumes the same id.
    feedback = result["settlement_result_feedback"]
    assert feedback["route_id"] == staged_route_id
    assert feedback["review_route"]["route_id"] == staged_route_id
    # Dispatch event also carries it.
    dispatch_route_ids = [
        e.get("route", {}).get("route_id")
        for e in (world.pending_dispatch_events or [])
        if e.get("type") == "settlement_summary"
    ]
    assert staged_route_id in dispatch_route_ids


# ---------------------------------------------------------------------------
# SC-26: same-war and cross-war collision
# ---------------------------------------------------------------------------


def test_cross_war_settlement_collision_returns_humanized_rejection():
    world = WorldState()
    _install_war(world, "war_1")
    _install_war(
        world,
        "war_2",
        attackers=["France"],
        defenders=["Britain"],
        attacker_leader="France",
        defender_leader="Britain",
    )
    staged = _stage(world, war_id="war_1")
    assert staged["success"] is True
    active = world.pending_diplomatic_dialogue
    assert active["war_id"] == "war_1"

    # Attempt to stage a different war's settlement while war_1 is mounted.
    result = stage_settlement_confirm(world, war_id="war_2")
    assert result["success"] is False
    assert result["error"] == "cross_war_settlement_collision"
    assert result["error_display"] == settlement_disabled_reason_display(
        "cross_war_settlement_collision"
    )
    assert result["active_war_id"] == "war_1"
    assert result["incoming_war_id"] == "war_2"
    assert result["mutated"] is False
    # The active dialogue is unchanged.
    assert world.pending_diplomatic_dialogue["war_id"] == "war_1"


def test_same_war_restage_keeps_mounted_draft_as_single_source_of_truth():
    """GT-Slice-4 (Guided Terms §6) supersedes the SC-26 additive merge:
    there is no editor submit blob to reconcile, so a same-war same-scope
    refresh re-shows the MOUNTED dialogue's terms — incoming terms never
    append to a non-empty staged draft."""
    world = WorldState()
    _install_war(world)
    first = stage_settlement_confirm(
        world,
        war_id="war_1",
        covered_enemy_participants=["Austria"],
        settlement_terms=[
            {"type": "territory_cede", "from": "Austria", "to": "France", "region": "Bohemia"},
        ],
    )
    assert first["success"] is True
    assert "Bohemia" in {
        t.get("region")
        for t in world.pending_diplomatic_dialogue["settlement_terms"]
    }

    # Same war, different incoming clause -> the staged draft wins; the
    # refresh succeeds and the surface re-shows the mounted terms.
    second = stage_settlement_confirm(
        world,
        war_id="war_1",
        covered_enemy_participants=["Austria"],
        settlement_terms=[
            {"type": "gold_indemnity", "from": "Austria", "to": "France", "amount": 200, "turns": 0},
        ],
    )
    assert second["success"] is True
    refreshed_types = {
        t.get("type")
        for t in world.pending_diplomatic_dialogue["settlement_terms"]
    }
    assert refreshed_types == {"territory_cede"}
    # SC-2 draft store mirrors the kept draft (CH-3: the scoped store).
    draft_types = {
        t.get("type")
        for t in load_scoped_settlement_draft(
            world,
            war_id="war_1",
            selected_target_nation=world.pending_diplomatic_dialogue.get(
                "selected_target_nation"
            ),
            covered_enemy_participants=["Austria"],
        )
    }
    assert draft_types == {"territory_cede"}


def test_same_war_restage_with_differing_clause_keeps_active_draft_without_dead_end():
    """The old `same_war_merge_conflict` dead end retired with the editor
    (GT-Slice-4): a same-war refresh carrying a different gold amount keeps
    the active draft AND succeeds — the player is re-shown the staged
    settlement instead of hitting a conflict error."""
    world = WorldState()
    _install_war(world)
    stage_settlement_confirm(
        world,
        war_id="war_1",
        covered_enemy_participants=["Austria"],
        settlement_terms=[
            {"type": "gold_indemnity", "from": "Austria", "to": "France", "amount": 200, "turns": 0},
        ],
    )
    result = stage_settlement_confirm(
        world,
        war_id="war_1",
        covered_enemy_participants=["Austria"],
        settlement_terms=[
            {"type": "gold_indemnity", "from": "Austria", "to": "France", "amount": 500, "turns": 0},
        ],
    )
    assert result["success"] is True
    assert "merge_conflict" not in result
    # Active draft preserved (200, not 500).
    active_terms = world.pending_diplomatic_dialogue["settlement_terms"]
    assert any(
        t.get("type") == "gold_indemnity" and t.get("amount") == 200
        for t in active_terms
    )
    assert not any(
        t.get("type") == "gold_indemnity" and t.get("amount") == 500
        for t in active_terms
    )


def test_settlement_family_dialogue_types_match_canonical_set():
    """SC-18 (anchor for SC-26): the settlement-family dialogue type set
    covers hard stops, current-turn offers, the G2e same-war scope chooser,
    and the G4F-8 pair-substitute confirm chooser, so collision protection
    catches every settlement-family type."""
    assert SETTLEMENT_FAMILY_DIALOGUE_TYPES == frozenset(
        {
            "settlement_confirm",
            "incoming_settlement_offer",
            "settlement_scope_replace_confirm",
            "settlement_pair_substitute_confirm",
        }
    )


def test_collision_protection_does_not_treat_an_offer_as_a_mounted_draft():
    """FA slice 10 — CONSCIOUSLY FLIPPED (was
    `test_collision_protection_treats_incoming_offer_as_settlement_family`).

    SC-26's "family scope" decision counted an `incoming_settlement_offer`
    as a mounted settlement, so a letter from an enemy blocked the player
    from opening a settlement on a DIFFERENT war. That reading also made the
    accept and request-revision arms destroy the letter they were answering
    (FA-4 / FA-N4), made Submit-for-Review collide with the mail behind the
    draft (FA-N15), and made opening Settlement over a standing offer read
    the ENEMY's terms as our draft (FA-N18).

    An offer is MAIL — a soft-stop persistent mailbox item the player may
    hold for turns. It is not a settlement in progress, and it no longer
    blocks one. The collision guard itself is unchanged and still fires
    between two real DRAFTS (see the test below).
    """
    world = WorldState()
    _install_war(world, "war_1")
    _install_war(
        world,
        "war_2",
        attackers=["France", "Spain"],
        defenders=["Britain", "Prussia"],
        attacker_leader="France",
        defender_leader="Britain",
    )
    # Manually push a synthetic incoming_settlement_offer for war_1.
    world.dialogue_manager.replace({
        "type": "incoming_settlement_offer",
        "war_id": "war_1",
        "offer_id": "offer_1",
        "settlement_terms": [],
    })
    result = stage_settlement_confirm(world, war_id="war_2")
    assert result.get("error") != "cross_war_settlement_collision"
    # And the letter is not consumed by the staging that ran over it.
    remaining = [d.get("type") for d in
                 ([world.dialogue_manager.peek()]
                  if world.dialogue_manager.peek() else [])
                 + world.dialogue_manager.iter_queue()]
    assert "incoming_settlement_offer" in remaining


def test_collision_protection_still_fires_between_two_drafts():
    """The other direction of the same flip: SC-26 is intact for the case it
    was written for — a real staged draft for one war blocks staging a
    second war's."""
    world = WorldState()
    _install_war(world, "war_1")
    _install_war(
        world,
        "war_2",
        attackers=["France", "Spain"],
        defenders=["Britain", "Prussia"],
        attacker_leader="France",
        defender_leader="Britain",
    )
    world.dialogue_manager.replace({
        "type": "settlement_confirm",
        "war_id": "war_1",
        "settlement_terms": [],
    })
    result = stage_settlement_confirm(world, war_id="war_2")
    assert result["success"] is False
    assert result["error"] == "cross_war_settlement_collision"
    assert result["active_dialogue_type"] == "settlement_confirm"


# ---------------------------------------------------------------------------
# SC-14b: reopen attempt cap with per-turn reset
# ---------------------------------------------------------------------------


def test_reopen_attempt_cap_constant_is_three():
    assert SETTLEMENT_REOPEN_MAX_ATTEMPTS == 3


def test_reopen_attempt_cap_blocks_fourth_attempt_with_humanized_copy():
    """SC-14b: attempts 1..3 may reopen when the target is valid; attempt
    4 returns `must_reopen=False` and the choose-from-war-detail copy."""
    world = WorldState()
    _install_war(world)
    # First three attempts increment freely.
    assert record_reopen_attempt(world, war_id="war_1") == 1
    assert record_reopen_attempt(world, war_id="war_1") == 2
    assert record_reopen_attempt(world, war_id="war_1") == 3
    # The cap is reached after attempt 3.
    assert reopen_attempt_cap_exceeded(world, war_id="war_1") is True


def test_reopen_loop_resets_after_end_of_turn():
    """SC-14b required test: per-(war_id, turn) reopen attempt reset is
    intentional; consecutive-turn reopen attempts must still leave the
    player with the SC-14b visible escape each turn."""
    world = WorldState()
    world.current_turn = 5
    _install_war(world)
    record_reopen_attempt(world, war_id="war_1")
    record_reopen_attempt(world, war_id="war_1")
    record_reopen_attempt(world, war_id="war_1")
    assert reopen_attempt_cap_exceeded(world, war_id="war_1") is True
    # Turn advances -> world clears the per-turn store.
    world.advance_turn()
    assert reopen_attempt_cap_exceeded(world, war_id="war_1") is False


def test_reopen_attempt_cap_returns_no_reopen_payload_in_safe_response():
    """When the cap is exceeded, must_reopen is False and the reopen
    target falls back to war_detail with empty target_nation."""
    from backend.game_logic.settlement_routes import _safe_reopen_response

    world = WorldState()
    _install_war(world)
    # Burn the cap.
    record_reopen_attempt(world, war_id="war_1")
    record_reopen_attempt(world, war_id="war_1")
    record_reopen_attempt(world, war_id="war_1")
    payload = _safe_reopen_response(
        world,
        war_id="war_1",
        dialogue={
            "selected_target_nation": "Austria",
            "covered_enemy_participants": ["Austria"],
        },
    )
    assert payload["must_reopen"] is False
    assert payload["error"] == "reopen_attempt_cap_exceeded"
    assert payload["error_display"] == settlement_disabled_reason_display(
        "reopen_attempt_cap_exceeded"
    )


# ---------------------------------------------------------------------------
# SC-13: dual-empty reopen fallback
# ---------------------------------------------------------------------------


def test_dual_empty_reopen_returns_no_reopen_with_choose_from_war_detail_copy():
    """SC-13: empty selected target plus empty covered enemies returns a
    non-reopening choose-from-war-detail payload."""
    from backend.game_logic.settlement_routes import _safe_reopen_response

    world = WorldState()
    _install_war(world)
    payload = _safe_reopen_response(
        world,
        war_id="war_1",
        dialogue={"selected_target_nation": "", "covered_enemy_participants": []},
    )
    assert payload["must_reopen"] is False
    assert payload["error"] == "no_reopen_target_available"
    assert payload["reopen_target"]["surface"] == "war_detail"
    assert payload["reopen_target"]["target_nation"] == ""
    assert payload["reopen_target"]["nation"] == ""


# ---------------------------------------------------------------------------
# SC-7b: stale incoming offer accept paths
# ---------------------------------------------------------------------------


def test_incoming_offer_accept_with_archived_war_returns_archived_error():
    """SC-5 reversal (May 15, 2026 / Slice G1 commit 1): with the deferral
    flag off, the SC-7b archived-war branch reaches its canonical humanized
    error path. Accept does not promote a stale-archived offer to
    settlement_confirm."""
    world = WorldState()
    war = _install_war(world)
    war["ended_turn"] = 4
    world.dialogue_manager.replace({
        "type": "incoming_settlement_offer",
        "war_id": "war_1",
        "offer_id": "offer_1",
    })
    dialogue = world.pending_diplomatic_dialogue
    result = handle_incoming_settlement_offer_action(
        world, action="accept_settlement_offer", dialogue=dialogue,
    )
    assert result["success"] is False
    assert result["error"] == "incoming_offer_war_archived"
    assert result["error_display"] == settlement_disabled_reason_display(
        "incoming_offer_war_archived"
    )
    assert result["mutated"] is False
    assert result.get("war_archived") is True


def test_incoming_offer_accept_with_unknown_war_id_returns_invalid_error():
    """SC-5 reversal: SC-7b unknown-war_id branch reaches its canonical
    humanized error path with the deferral flag off."""
    world = WorldState()
    _install_war(world)
    world.dialogue_manager.replace({
        "type": "incoming_settlement_offer",
        "war_id": "war_unknown",
        "offer_id": "offer_x",
    })
    dialogue = world.pending_diplomatic_dialogue
    result = handle_incoming_settlement_offer_action(
        world, action="accept_settlement_offer", dialogue=dialogue,
    )
    assert result["success"] is False
    assert result["error"] == "incoming_offer_war_invalid"
    assert result["must_reopen"] is False
    assert result["mutated"] is False
    assert result.get("reopen_target", {}).get("surface") == "war_detail"


# ---------------------------------------------------------------------------
# SC-14, SC-14d, SC-14e: active-vs-archived re-resolution at click time
# ---------------------------------------------------------------------------


def test_review_target_active_when_war_is_live():
    world = WorldState()
    _install_war(world)
    assert is_war_archived(world, "war_1") is False
    assert is_war_known(world, "war_1") is True
    assert derive_settlement_review_target(world, war_id="war_1") == \
        SETTLEMENT_REVIEW_TARGET_ACTIVE


def test_review_target_archived_when_war_ended():
    world = WorldState()
    war = _install_war(world)
    war["ended_turn"] = 5
    assert is_war_archived(world, "war_1") is True
    assert derive_settlement_review_target(world, war_id="war_1") == \
        SETTLEMENT_REVIEW_TARGET_ARCHIVED


def test_settlement_review_target_re_resolves_at_click_time_with_world():
    """SC-14: active-vs-archived route decisions are resolved at click
    time. A row rendered while the war was active opens the archived
    ledger row if the war archives between render and click."""
    world = WorldState()
    war = _install_war(world)
    # Render-time: war is active, the event was stamped active.
    rendered_event = {
        "war_id": "war_1",
        "war_ended": False,
        "route": {"review_target": SETTLEMENT_REVIEW_TARGET_ACTIVE},
    }
    # Without world, the legacy stamped value wins.
    assert settlement_review_target(rendered_event) == \
        SETTLEMENT_REVIEW_TARGET_ACTIVE
    # War archives between render and click.
    war["ended_turn"] = 7
    # With world, click-time re-resolution overrides the stamped value.
    assert settlement_review_target(rendered_event, world=world) == \
        SETTLEMENT_REVIEW_TARGET_ARCHIVED


def test_notification_meta_re_resolves_review_target_with_live_world():
    """SC-14: notification click metadata must not keep a stale active
    branch when the war archives between render and click."""
    world = WorldState()
    war = _install_war(world)
    event = {
        "type": "settlement_summary",
        "war_id": "war_1",
        "turn": 7,
        "war_ended": False,
        "proposer_members": ["France"],
        "accepting_members": ["Austria"],
        "route": {
            "review_target": SETTLEMENT_REVIEW_TARGET_ACTIVE,
            "route_id": "settlement:war_1:7:1",
        },
    }
    war["ended_turn"] = 8
    meta = settlement_notification_meta(event, world=world)
    assert meta["review_target"] == SETTLEMENT_REVIEW_TARGET_ARCHIVED
    assert meta["route_id"] == "settlement:war_1:7:1"


def test_recent_settlement_rows_re_resolve_review_target_with_live_world():
    """SC-14/SC-14d: ledger rows built after archival use current world
    state rather than the event's stale stamped route target."""
    world = WorldState()
    war = _install_war(world)
    world.event_log.append({
        "type": "settlement_summary",
        "war_id": "war_1",
        "turn": 7,
        "war_ended": False,
        "proposer_members": ["France"],
        "accepting_members": ["Austria"],
        "covered_enemy_participants": ["Austria"],
        "applied_clauses": [],
        "participant_reactions": [],
        "terms_summary": [],
        "route": {
            "review_target": SETTLEMENT_REVIEW_TARGET_ACTIVE,
            "route_id": "settlement:war_1:7:1",
        },
    })
    war["ended_turn"] = 8
    rows = recent_settlement_summaries(world, "France")
    assert rows[0]["review_target"] == SETTLEMENT_REVIEW_TARGET_ARCHIVED
    assert rows[0]["route_id"] == "settlement:war_1:7:1"


def test_resolve_settlement_route_click_returns_active_for_live_war():
    world = WorldState()
    _install_war(world)
    routed = resolve_settlement_route_click(
        world, war_id="war_1", route_id="settlement:war_1:5:1",
    )
    assert routed["available"] is True
    assert routed["review_target"] == SETTLEMENT_REVIEW_TARGET_ACTIVE
    assert routed["war_archived"] is False


def test_resolve_settlement_route_click_returns_archived_after_war_ends():
    world = WorldState()
    war = _install_war(world)
    war["ended_turn"] = 5
    routed = resolve_settlement_route_click(
        world, war_id="war_1", route_id="settlement:war_1:5:1",
    )
    assert routed["available"] is True
    assert routed["review_target"] == SETTLEMENT_REVIEW_TARGET_ARCHIVED


def test_resolve_settlement_route_click_returns_invalid_for_unknown_war():
    world = WorldState()
    routed = resolve_settlement_route_click(
        world, war_id="war_unknown", route_id="settlement:war_unknown:5:1",
    )
    assert routed["available"] is False
    assert routed["error"] == "invalid_war_id"


def test_aged_out_dispatch_click_returns_no_longer_in_recent_window():
    """SC-14e: settlement history and dispatch can route to nothing over
    time. An old dispatch click that no longer matches any recent route
    must surface humanized copy instead of opening a blank focus."""
    world = WorldState()
    war = _install_war(world)
    war["ended_turn"] = 5
    # The recent window contains other events but not this stale id.
    routed = resolve_settlement_route_click(
        world,
        war_id="war_1",
        route_id="settlement:war_1:1:1",  # aged-out
        recent_window_route_ids=[
            "settlement:war_1:5:1",
            "settlement:war_2:5:1",
        ],
    )
    assert routed["available"] is False
    assert routed["error"] == "settlement_no_longer_in_recent_window"
    assert routed["error_display"] == settlement_disabled_reason_display(
        "settlement_no_longer_in_recent_window"
    )


def test_resolve_route_click_archived_in_window_routes_to_ledger():
    """An archived war whose route id is still present in the recent
    window opens the archived ledger row."""
    world = WorldState()
    war = _install_war(world)
    war["ended_turn"] = 5
    routed = resolve_settlement_route_click(
        world,
        war_id="war_1",
        route_id="settlement:war_1:5:1",
        recent_window_route_ids=["settlement:war_1:5:1"],
    )
    assert routed["available"] is True
    assert routed["review_target"] == SETTLEMENT_REVIEW_TARGET_ARCHIVED


# ---------------------------------------------------------------------------
# SC-14: ratify result feedback re-resolves at completion time
# ---------------------------------------------------------------------------


def test_ratify_result_feedback_routes_to_active_review_when_war_continues():
    """SC-14: active partial settlement result feedback routes to the live
    settlement review surface, not the archived ledger row."""
    from backend.game_logic.settlement_preview import ratify_settlement_confirm

    world = WorldState()
    _install_high_acceptance_war(world)
    staged = stage_settlement_confirm(
        world,
        war_id="war_1",
        covered_enemy_participants=["Austria"],  # partial: Prussia uncovered
        # G2-Slice-W1 empty-Ratify gate: editor-staged empty drafts cannot
        # ratify. Continuity tests author a minimum legitimate peace
        # package to probe routing rather than the gate.
        settlement_terms=[{"type": "peace"}],
    )
    dialogue = staged["diplomatic_dialogue"]
    result = ratify_settlement_confirm(world, dialogue)
    assert result["success"] is True
    assert result["war_ended"] is False  # partial — Prussia still at war
    feedback = result["settlement_result_feedback"]
    # Active partial settlement -> review_target should be settlement_review.
    assert feedback["review_route"]["review_target"] == \
        SETTLEMENT_REVIEW_TARGET_ACTIVE
    assert feedback["review_route"]["war_ended"] is False


def test_ratify_result_feedback_routes_to_ledger_when_war_ends():
    """SC-14: archived full-war settlements route to the ledger row."""
    from backend.game_logic.settlement_preview import ratify_settlement_confirm

    world = WorldState()
    _install_high_acceptance_war(world)
    # Cover both enemies -> war ends fully.
    staged = stage_settlement_confirm(
        world,
        war_id="war_1",
        covered_enemy_participants=["Austria", "Prussia"],
        # G2-Slice-W1 empty-Ratify gate: editor-staged empty drafts cannot
        # ratify. Continuity tests author a minimum legitimate peace
        # package to probe routing rather than the gate.
        settlement_terms=[{"type": "peace"}],
    )
    dialogue = staged["diplomatic_dialogue"]
    result = ratify_settlement_confirm(world, dialogue)
    assert result["success"] is True
    assert result["war_ended"] is True
    feedback = result["settlement_result_feedback"]
    assert feedback["review_route"]["review_target"] == \
        SETTLEMENT_REVIEW_TARGET_ARCHIVED
    assert feedback["review_route"]["war_ended"] is True


# ---------------------------------------------------------------------------
# SC-14b/SC-7b interplay with no_resolvable_pairs path
# ---------------------------------------------------------------------------


def test_no_resolvable_pairs_uses_safe_reopen_response():
    """SC-2/SC-3/SC-13: the `no_resolvable_pairs` failure must surface
    must_reopen=True only when a non-empty target exists; the SC-14b cap
    still applies."""
    from backend.game_logic.settlement_preview import ratify_settlement_confirm

    world = WorldState()
    _install_war(world)
    # Stage with a covered enemy but pass in settlement_terms that resolve
    # nothing (peace with no covered pair) — actually our build always has
    # covered=Austria, so this path is hard to hit via stage(). We test
    # the helper directly.
    dialogue = {
        "type": "settlement_confirm",
        "war_id": "war_1",
        "selected_target_nation": "Austria",
        "covered_enemy_participants": ["Austria"],
    }
    # Intentionally inject a dialogue that revalidate_staged_settlement
    # would fail; use the proposer_leader_changed path.
    staged = _stage(world)
    staged_dialogue = staged["diplomatic_dialogue"]
    # Mutate the war instance so revalidate fails on proposer leader.
    war = world.war_instances["war_1"]
    war["attacker_leader"] = "Saxony"
    result = ratify_settlement_confirm(world, staged_dialogue)
    # First failure: must_reopen=True (target exists).
    assert result["success"] is False
    assert result["error"] == "proposer_leader_changed"
    assert result["must_reopen"] is True
    target = result["reopen_target"]
    assert target["target_nation"] == "Austria"


def test_request_revision_routes_to_guided_propose_counter_surface():
    """SC-5 reversal commit 2 + GT-Slice-4 (OQ-4(b)):
    `request_settlement_revision` opens a real counter route by staging the
    guided PROPOSE `settlement_confirm` seeded with the offered terms. The
    original offer entry is removed; the staged dialogue carries the
    offer_id as counter provenance and the request-revision Voice Bible
    family as `talleyrand_text` so the popup heading reads as "answering
    with a counter draft" rather than the outgoing `Will they accept?`
    framing."""
    world = WorldState()
    _install_war(world)
    # Use a real covered enemy so stage_settlement_confirm can resolve
    # a selected target without falling into the dual-empty fallback.
    world.dialogue_manager.replace({
        "type": "incoming_settlement_offer",
        "war_id": "war_1",
        "offer_id": "offer_x",
        "selected_target_nation": "Austria",
        "covered_enemy_participants": ["Austria"],
        "settlement_terms": [{"type": "peace"}],
        "proposer_side": "defenders",
        "proposer_nation": "Austria",
        "accepting_side": "attackers",
        "accepting_leader": "France",
    })
    dialogue = world.pending_diplomatic_dialogue
    result = handle_incoming_settlement_offer_action(
        world, action="request_settlement_revision", dialogue=dialogue,
    )
    assert result["success"] is True
    assert result["action"] == "request_settlement_revision"
    assert result["dialogue_type"] == "settlement_confirm"
    assert result["offer_id"] == "offer_x"
    assert result["counter_to_offer_id"] == "offer_x"
    assert result["counter_seed_terms"] == [{"type": "peace"}]
    # The staged settlement_confirm is now the active dialogue, on the
    # guided PROPOSE surface (GT-Slice-4: no editor mount).
    current = world.dialogue_manager.peek()
    assert current is not None
    assert current.get("type") == "settlement_confirm"
    assert current.get("dialogue_mode") == "PROPOSE"
    assert "open_editor_on_mount" not in result
    # Request-revision heading appears on the staged dialogue.
    assert "counter draft" in str(current.get("talleyrand_text", "")).lower()


# ---------------------------------------------------------------------------
# SC-14c serialization of settlement_route_seq
# ---------------------------------------------------------------------------


def test_settlement_route_seq_round_trips_through_save_load():
    world = WorldState()
    world.current_turn = 7
    _install_war(world)
    mint_settlement_route_id(world, war_id="war_1")
    mint_settlement_route_id(world, war_id="war_1")
    mint_settlement_route_id(world, war_id="war_2")

    data = world.to_dict()
    assert data["settlement_route_seq"]["war_1"][7] == 2
    assert data["settlement_route_seq"]["war_2"][7] == 1

    restored = WorldState.from_dict(data)
    assert restored.settlement_route_seq["war_1"][7] == 2
    assert restored.settlement_route_seq["war_2"][7] == 1


def test_settlement_reopen_attempts_round_trips_through_save_load():
    world = WorldState()
    world.current_turn = 7
    _install_war(world)
    record_reopen_attempt(world, war_id="war_1")
    record_reopen_attempt(world, war_id="war_1")

    data = world.to_dict()
    assert data["settlement_reopen_attempts"]["war_1"][7] == 2

    restored = WorldState.from_dict(data)
    assert restored.settlement_reopen_attempts["war_1"][7] == 2
