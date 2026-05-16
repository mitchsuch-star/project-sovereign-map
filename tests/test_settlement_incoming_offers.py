"""SC-5 reversal (May 15, 2026 / Slice G1 commit 1) — backend producer
+ package-preserving accept/reject handler behavior.

Scope (commit 1 of 2):

- The AI settlement-offer producer
  (`ai_diplomacy.process_settlement_offer_phase`) is the canonical
  emitter of `incoming_settlement_offer` dialogues. It fires for
  active multi-party war_instances where the player participates,
  respects a per-`war_id` cooldown via `world.ai_settlement_cooldowns`,
  enforces a one-active-offer-per-war guard, assigns a stable
  `offer_id="settlement_offer:{war_id}:{turn}:{seq}"`, and stores
  the offer in `world.pending_settlement_dialogues` (NOT in
  `dialogue_manager`).
- The handler
  `settlement_preview.handle_incoming_settlement_offer_action`
  consumes the offer on accept / reject. Accept preserves the
  offered `settlement_terms`, `covered_enemy_participants`, and
  `selected_target_nation` through `stage_settlement_confirm(...)`
  so the staged review carries the exact offered package through
  live re-preview. Reject removes the offer without mutation.
  `request_settlement_revision` returns a counter / edit hint
  without mutation (real counter / edit wiring lands in commit 2).
- Stale `war_id` (empty / invalid / archived) on accept returns the
  documented humanized error and never calls
  `stage_settlement_confirm`.

Out of scope (commit 2):

- Dialogue-manager taxonomy re-add, mailbox / pending-envoy /
  notification / dispatch / popup-queue / Godot popup routing,
  Voice Bible §16.1 incoming-offer families, request-revision
  counter / edit route, request-terms lifecycle.

Pairs with `tests/test_incoming_offer_deferral_no_leaks.py`, which
keeps the no-UI-exposure assertions until commit 2 lands.
"""

from __future__ import annotations

from typing import Dict

import pytest

from backend.game_logic.ai_diplomacy import (
    SETTLEMENT_OFFER_BASE_GOLD_AMOUNT,
    SETTLEMENT_OFFER_COOLDOWN_TURNS,
    SETTLEMENT_OFFER_MIN_WAR_DURATION_TURNS,
    SETTLEMENT_OFFER_MULTI_PARTY_MIN_PARTICIPANTS,
    SETTLEMENT_OFFER_PER_DURATION_BONUS,
    process_settlement_offer_phase,
)
from backend.game_logic.settlement_preview import (
    handle_incoming_settlement_offer_action,
)
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import (
    make_synthetic_war_instance,
)


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _install_multi_party_war(
    world: WorldState,
    *,
    war_id: str = "war_1",
    attackers=("France", "Saxony"),
    defenders=("Austria", "Britain"),
    attacker_leader: str = "France",
    defender_leader: str = "Austria",
    created_turn: int = 1,
) -> Dict:
    war = make_synthetic_war_instance(
        war_id,
        attackers=list(attackers),
        defenders=list(defenders),
        attacker_leader=attacker_leader,
        defender_leader=defender_leader,
        created_turn=created_turn,
    )
    world.war_instances[war_id] = war
    # Stamp diplomatic_states so `is_war_known` and downstream checks pass.
    for atk in attackers:
        for dfd in defenders:
            key = "|".join(sorted([atk, dfd]))
            world.diplomatic_states[key] = "WAR"
    return war


def _world_at_turn(turn: int) -> WorldState:
    world = WorldState()
    world.current_turn = turn
    return world


# ---------------------------------------------------------------------------
# Section 1 — Producer emission, gates, cooldown, one-active-offer guard
# ---------------------------------------------------------------------------


def test_ai_settlement_offer_producer_emits_into_pending_settlement_dialogues():
    """The producer creates a real `incoming_settlement_offer` entry
    on a multi-party war where the player participates."""
    world = _world_at_turn(5)
    _install_multi_party_war(world)

    produced = process_settlement_offer_phase(world)

    assert len(produced) == 1
    offer = produced[0]
    assert offer["type"] == "incoming_settlement_offer"
    assert offer["dialogue_type"] == "incoming_settlement_offer"
    assert offer["war_id"] == "war_1"
    assert offer["proposer_nation"] == "Austria"
    assert offer["proposer_side"] == "defenders"
    assert offer["accepting_side"] == "attackers"
    assert offer["accepting_leader"] == "France"
    assert sorted(offer["covered_enemy_participants"]) == ["Austria", "Britain"]
    assert offer["turn_created"] == 5
    # Settlement terms have at least one material clause beyond peace.
    assert any(clause.get("type") == "peace" for clause in offer["settlement_terms"])
    assert any(
        clause.get("type") == "gold_indemnity" for clause in offer["settlement_terms"]
    )
    # Persisted on world.pending_settlement_dialogues, NOT in dialogue_manager.
    assert world.pending_settlement_dialogues == [offer]
    assert world.dialogue_manager._current is None
    assert world.dialogue_manager._queue == []


def test_producer_only_fires_for_multi_party_wars_with_player_participant():
    """Bilateral wars and wars without the player are skipped."""
    world = _world_at_turn(5)
    # Multi-party war without the player participating.
    _install_multi_party_war(
        world,
        war_id="war_no_player",
        attackers=("Saxony", "Bavaria"),
        defenders=("Austria", "Britain"),
        attacker_leader="Saxony",
        defender_leader="Austria",
    )
    # Bilateral war with the player (1v1).
    bilateral = make_synthetic_war_instance(
        "war_bilateral",
        attackers=["France"],
        defenders=["Russia"],
        attacker_leader="France",
        defender_leader="Russia",
        created_turn=1,
    )
    world.war_instances["war_bilateral"] = bilateral
    world.diplomatic_states["France|Russia"] = "WAR"

    produced = process_settlement_offer_phase(world)

    assert produced == []
    assert world.pending_settlement_dialogues == []


def test_producer_skips_archived_war_instances():
    """`ended_turn` set means the war is terminal / archived."""
    world = _world_at_turn(5)
    war = _install_multi_party_war(world)
    war["ended_turn"] = 4

    produced = process_settlement_offer_phase(world)

    assert produced == []


def test_producer_skips_wars_younger_than_min_duration():
    """SC-30: wait `SETTLEMENT_OFFER_MIN_WAR_DURATION_TURNS` after
    war creation before producing the first offer."""
    world = _world_at_turn(1)
    _install_multi_party_war(world, created_turn=1)
    # current_turn - created_turn = 0 < SETTLEMENT_OFFER_MIN_WAR_DURATION_TURNS

    produced = process_settlement_offer_phase(world)

    assert produced == []

    # At exactly min-duration, the producer fires.
    world.current_turn = 1 + SETTLEMENT_OFFER_MIN_WAR_DURATION_TURNS
    produced = process_settlement_offer_phase(world)
    assert len(produced) == 1


def test_producer_respects_cooldown_per_war_id():
    """Once an offer fires for a war_id, no second offer fires until
    `SETTLEMENT_OFFER_COOLDOWN_TURNS` turns later."""
    world = _world_at_turn(5)
    _install_multi_party_war(world)

    first = process_settlement_offer_phase(world)
    assert len(first) == 1
    # Remove the existing pending offer so the one-active-offer guard
    # is not what is gating the second tick.
    world.pending_settlement_dialogues.clear()

    for delta in range(1, SETTLEMENT_OFFER_COOLDOWN_TURNS):
        world.current_turn = 5 + delta
        assert process_settlement_offer_phase(world) == [], (
            f"cooldown should block at delta {delta}"
        )

    world.current_turn = 5 + SETTLEMENT_OFFER_COOLDOWN_TURNS
    second = process_settlement_offer_phase(world)
    assert len(second) == 1
    assert second[0]["offer_id"] != first[0]["offer_id"]


def test_producer_enforces_one_active_offer_per_war_guard():
    """If an existing offer for `war_id` already sits in
    `pending_settlement_dialogues`, no second offer fires regardless
    of cooldown state."""
    world = _world_at_turn(5)
    _install_multi_party_war(world)

    first = process_settlement_offer_phase(world)
    assert len(first) == 1

    # Reset cooldown to force the producer past the cooldown gate.
    world.ai_settlement_cooldowns.clear()

    second = process_settlement_offer_phase(world)
    assert second == []
    assert len(world.pending_settlement_dialogues) == 1


def test_producer_assigns_stable_offer_id_per_war_turn_seq():
    """`offer_id` format is `settlement_offer:{war_id}:{turn}:{seq}`."""
    world = _world_at_turn(7)
    _install_multi_party_war(world, war_id="war_alpha")
    _install_multi_party_war(
        world,
        war_id="war_beta",
        attackers=("France", "Bavaria"),
        defenders=("Prussia", "Russia"),
        attacker_leader="France",
        defender_leader="Prussia",
    )

    produced = process_settlement_offer_phase(world)

    # Deterministic iteration order keyed by sorted war_id.
    offer_ids = [offer["offer_id"] for offer in produced]
    assert offer_ids == [
        "settlement_offer:war_alpha:7:1",
        "settlement_offer:war_beta:7:1",
    ]


def test_producer_offer_terms_amount_scales_with_war_age():
    """Older wars produce higher-stakes offers."""
    world = _world_at_turn(5)
    _install_multi_party_war(world, created_turn=1)
    young = process_settlement_offer_phase(world)
    young_amount = next(
        clause["amount"]
        for clause in young[0]["settlement_terms"]
        if clause["type"] == "gold_indemnity"
    )
    expected_young = (
        SETTLEMENT_OFFER_BASE_GOLD_AMOUNT
        + (5 - 1) * SETTLEMENT_OFFER_PER_DURATION_BONUS
    )
    assert young_amount == expected_young

    # An older war produces a higher amount.
    world2 = _world_at_turn(15)
    _install_multi_party_war(world2, created_turn=1)
    old = process_settlement_offer_phase(world2)
    old_amount = next(
        clause["amount"]
        for clause in old[0]["settlement_terms"]
        if clause["type"] == "gold_indemnity"
    )
    assert old_amount > young_amount


def test_producer_constants_are_named_and_sane():
    """Sanity / contract check on the named constants so downstream
    audits can quote them by name."""
    assert SETTLEMENT_OFFER_MULTI_PARTY_MIN_PARTICIPANTS == 3
    assert SETTLEMENT_OFFER_COOLDOWN_TURNS >= 2
    assert SETTLEMENT_OFFER_MIN_WAR_DURATION_TURNS >= 1
    assert SETTLEMENT_OFFER_BASE_GOLD_AMOUNT > 0
    assert SETTLEMENT_OFFER_PER_DURATION_BONUS >= 0


# ---------------------------------------------------------------------------
# Section 2 — Handler: accept (package preservation)
# ---------------------------------------------------------------------------


def test_incoming_offer_accept_preserves_offer_id_and_settlement_terms_through_live_preview():
    """SC-5 §G2-Slice-4 package-preservation: accept stages
    `settlement_confirm` with the exact offered `settlement_terms`."""
    world = _world_at_turn(5)
    _install_multi_party_war(world)
    [offer] = process_settlement_offer_phase(world)

    result = handle_incoming_settlement_offer_action(
        world, action="accept_settlement_offer", dialogue=offer,
    )

    assert result["success"] is True
    assert result["action"] == "accept_settlement_offer"
    assert result["dialogue_type"] == "settlement_confirm"
    assert result["offer_id"] == offer["offer_id"]
    # `accepted_offer_terms` echoes the preserved package on the result.
    assert result["accepted_offer_terms"] == offer["settlement_terms"]
    # Staged dialogue carries the exact offered terms.
    staged = world.dialogue_manager._current
    assert staged is not None
    assert staged.get("dialogue_type") == "settlement_confirm"
    assert staged.get("settlement_terms") == offer["settlement_terms"]
    # Pending entry was removed so the one-active-offer guard re-opens.
    assert world.pending_settlement_dialogues == []


def test_incoming_offer_accept_stages_settlement_confirm_for_correct_war_id_and_covered_scope():
    """The staged review targets the same `war_id` and covers the
    same enemy participants as the offer."""
    world = _world_at_turn(5)
    _install_multi_party_war(world)
    [offer] = process_settlement_offer_phase(world)

    result = handle_incoming_settlement_offer_action(
        world, action="accept_settlement_offer", dialogue=offer,
    )

    assert result["success"] is True
    staged = world.dialogue_manager._current
    assert staged.get("war_id") == offer["war_id"]
    # Selected target defaults to the original offering leader when it
    # is one of the covered enemies; otherwise the first covered enemy.
    assert staged.get("selected_target_nation") == "Austria"
    # Covered scope is preserved verbatim.
    staged_covered = sorted(staged.get("covered_enemy_participants") or [])
    assert staged_covered == sorted(offer["covered_enemy_participants"])


def test_incoming_offer_accept_with_empty_war_id_returns_humanized_error_and_does_not_stage():
    """SC-7b empty-`war_id` path: humanized rejection without staging."""
    world = _world_at_turn(5)
    _install_multi_party_war(world)
    [offer] = process_settlement_offer_phase(world)
    offer_no_war = dict(offer)
    offer_no_war["war_id"] = ""

    result = handle_incoming_settlement_offer_action(
        world, action="accept_settlement_offer", dialogue=offer_no_war,
    )

    assert result["success"] is False
    assert result["error"] == "invalid_war_id"
    assert isinstance(result.get("error_display"), str) and result["error_display"]
    assert result["mutated"] is False
    # Defensive cleanup removed the original entry by offer_id fallback.
    assert world.pending_settlement_dialogues == []


def test_incoming_offer_accept_with_unknown_war_id_returns_humanized_error_and_does_not_stage():
    """SC-7b unknown `war_id` path: humanized rejection plus
    war-detail reopen target, no `stage_settlement_confirm` call.

    The stale dialogue uses an entirely synthetic `offer_id` so the
    handler's offer-id cleanup does not collide with the real
    pending entry; we only want to assert handling of the unknown
    `war_id` field."""
    world = _world_at_turn(5)
    _install_multi_party_war(world)
    [real_offer] = process_settlement_offer_phase(world)

    stale_offer = {
        "type": "incoming_settlement_offer",
        "dialogue_type": "incoming_settlement_offer",
        "offer_id": "settlement_offer:stale_war:9:1",
        "war_id": "war_nonexistent",
        "proposer_nation": "Austria",
        "proposer_side": "defenders",
        "accepting_side": "attackers",
        "accepting_leader": "France",
        "covered_enemy_participants": ["Austria"],
        "settlement_terms": [{"type": "peace"}],
        "turn_created": 4,
    }

    result = handle_incoming_settlement_offer_action(
        world, action="accept_settlement_offer", dialogue=stale_offer,
    )

    assert result["success"] is False
    assert result["error"] == "incoming_offer_war_invalid"
    assert result["mutated"] is False
    assert result.get("reopen_target", {}).get("surface") == "war_detail"
    # Original real offer entry untouched — different offer_id and
    # different war_id mean neither match branch of the cleanup
    # helper fires.
    assert len(world.pending_settlement_dialogues) == 1
    assert world.pending_settlement_dialogues[0]["offer_id"] == real_offer["offer_id"]


def test_incoming_offer_accept_with_tampered_offer_id_does_not_clear_real_offer_by_war_id():
    """A mismatched `offer_id` must not fall back to `war_id` and remove
    a legitimate pending offer. `war_id` cleanup fallback exists only for
    stale-save entries that have no stable offer id."""
    world = _world_at_turn(5)
    _install_multi_party_war(world)
    [real_offer] = process_settlement_offer_phase(world)

    tampered_offer = dict(real_offer)
    tampered_offer["offer_id"] = "settlement_offer:tampered:5:1"
    tampered_offer["settlement_terms"] = [{"type": "peace"}]

    result = handle_incoming_settlement_offer_action(
        world, action="accept_settlement_offer", dialogue=tampered_offer,
    )

    assert result["dialogue_type"] == "settlement_confirm"
    assert len(world.pending_settlement_dialogues) == 1
    assert world.pending_settlement_dialogues[0]["offer_id"] == real_offer["offer_id"]
    assert world.pending_settlement_dialogues[0]["settlement_terms"] == real_offer["settlement_terms"]


def test_incoming_offer_accept_with_archived_war_id_returns_archived_error():
    """SC-7b archived `war_id`: humanized archived rejection."""
    world = _world_at_turn(5)
    war = _install_multi_party_war(world)
    [offer] = process_settlement_offer_phase(world)

    war["ended_turn"] = 4  # archive after producer ran

    result = handle_incoming_settlement_offer_action(
        world, action="accept_settlement_offer", dialogue=offer,
    )

    assert result["success"] is False
    assert result["error"] == "incoming_offer_war_archived"
    assert result.get("war_archived") is True
    assert result["mutated"] is False


def test_incoming_offer_accept_with_unknown_action_returns_unknown_error():
    world = _world_at_turn(5)
    _install_multi_party_war(world)
    [offer] = process_settlement_offer_phase(world)

    result = handle_incoming_settlement_offer_action(
        world, action="frobnicate_settlement_terms", dialogue=offer,
    )

    assert result["success"] is False
    assert result["error"] == "unknown_settlement_offer_action"
    assert result["mutated"] is False


# ---------------------------------------------------------------------------
# Section 3 — Handler: reject + request revision
# ---------------------------------------------------------------------------


def test_incoming_offer_reject_removes_entry_without_mutation():
    """Reject removes the pending offer without mutating world state
    and clears the one-active-offer guard so a future producer tick
    can re-fire after cooldown."""
    world = _world_at_turn(5)
    _install_multi_party_war(world)
    [offer] = process_settlement_offer_phase(world)

    diplo_snapshot = dict(world.diplomatic_states)

    result = handle_incoming_settlement_offer_action(
        world, action="reject_settlement_offer", dialogue=offer,
    )

    assert result["success"] is True
    assert result["action"] == "reject_settlement_offer"
    assert result["mutated"] is False
    assert result["offer_id"] == offer["offer_id"]
    assert world.pending_settlement_dialogues == []
    # Diplomatic state is untouched.
    assert dict(world.diplomatic_states) == diplo_snapshot


def test_incoming_offer_request_revision_returns_counter_edit_hint_without_mutation():
    """SC-30 commit 1: `request_settlement_revision` returns a counter
    / edit hint that names the offer_id, war_id, offered terms, and
    covered scope so commit 2's UI layer can seed a real counter-edit
    route. No mutation. The pending entry is intentionally kept so
    the player can also accept / reject the original package."""
    world = _world_at_turn(5)
    _install_multi_party_war(world)
    [offer] = process_settlement_offer_phase(world)

    result = handle_incoming_settlement_offer_action(
        world, action="request_settlement_revision", dialogue=offer,
    )

    assert result["success"] is True
    assert result["action"] == "request_settlement_revision"
    assert result["mutated"] is False
    assert result["offer_id"] == offer["offer_id"]
    hint = result.get("counter_edit_hint")
    assert isinstance(hint, dict)
    assert hint["war_id"] == offer["war_id"]
    assert hint["offer_id"] == offer["offer_id"]
    assert hint["seed_settlement_terms"] == offer["settlement_terms"]
    assert sorted(hint["covered_enemy_participants"]) == sorted(
        offer["covered_enemy_participants"]
    )
    # Pending entry stays so the player can still accept / reject.
    assert len(world.pending_settlement_dialogues) == 1


# ---------------------------------------------------------------------------
# Section 4 — Commit-1 invariant: no UI leakage until commit 2
# ---------------------------------------------------------------------------


def test_pending_settlement_dialogues_offer_entries_do_not_surface_in_mailbox_or_pending_envoy_until_ui_layer_lands():
    """Until commit 2 promotes `pending_settlement_dialogues` into the
    dialogue_manager, the produced offer is invisible to mailbox and
    pending-envoy paths because the dialogue-manager taxonomy excludes
    `incoming_settlement_offer`."""
    world = _world_at_turn(5)
    _install_multi_party_war(world)
    process_settlement_offer_phase(world)

    assert len(world.pending_settlement_dialogues) == 1
    # Dialogue manager has no awareness of the offer.
    dm = world.dialogue_manager
    assert dm.get_mailbox_count() == 0
    assert dm.get_mailbox_items() == []
    assert dm._current is None
    assert dm._queue == []


def test_pending_settlement_dialogues_offer_entries_do_not_emit_notifications_dispatch_or_popup_until_ui_layer_lands():
    """The producer is a side-channel writer: it does not push
    notifications, dispatch events, or popup-queue entries. Commit 2
    is what wires those surfaces."""
    world = _world_at_turn(5)
    _install_multi_party_war(world)

    before_notifications = list(world.notifications.get_pending())
    before_dispatch = list(world.pending_dispatch_events)
    before_popup_queue = world._popup_queue.to_dict()

    process_settlement_offer_phase(world)

    assert list(world.notifications.get_pending()) == before_notifications
    assert list(world.pending_dispatch_events) == before_dispatch
    assert world._popup_queue.to_dict() == before_popup_queue


# ---------------------------------------------------------------------------
# Section 5 — Save / load round-trip
# ---------------------------------------------------------------------------


def test_pending_settlement_offer_survives_save_load_round_trip():
    """`pending_settlement_dialogues` already round-trips through
    `WorldState.to_dict()` / `from_dict()`. Confirm that an offer
    survives the trip with all preserved fields, so commit 2's UI
    layer can promote it cleanly even after a save / load."""
    world = _world_at_turn(5)
    _install_multi_party_war(world)
    [offer] = process_settlement_offer_phase(world)

    snapshot = world.to_dict()
    rehydrated = WorldState.from_dict(snapshot)

    restored = rehydrated.pending_settlement_dialogues
    assert len(restored) == 1
    restored_offer = restored[0]
    for field in (
        "type",
        "dialogue_type",
        "offer_id",
        "war_id",
        "proposer_nation",
        "proposer_side",
        "accepting_side",
        "accepting_leader",
        "settlement_terms",
        "turn_created",
    ):
        assert restored_offer.get(field) == offer.get(field), field
    assert sorted(restored_offer["covered_enemy_participants"]) == sorted(
        offer["covered_enemy_participants"]
    )


# ---------------------------------------------------------------------------
# Section 6 — Cooldown serialization
# ---------------------------------------------------------------------------


def test_ai_settlement_cooldowns_survive_save_load_round_trip():
    """`ai_settlement_cooldowns` is a save-format field. After save /
    load, the producer must still respect the cooldown set on the
    previous tick."""
    world = _world_at_turn(5)
    _install_multi_party_war(world)
    process_settlement_offer_phase(world)
    assert world.ai_settlement_cooldowns.get("war_1") == 5 + SETTLEMENT_OFFER_COOLDOWN_TURNS

    snapshot = world.to_dict()
    rehydrated = WorldState.from_dict(snapshot)
    assert (
        rehydrated.ai_settlement_cooldowns.get("war_1")
        == 5 + SETTLEMENT_OFFER_COOLDOWN_TURNS
    )

    # On the next turn, cooldown still gates production.
    rehydrated.current_turn = 6
    # Clear the pending entry so the one-active-offer guard does not
    # also gate the producer.
    rehydrated.pending_settlement_dialogues.clear()
    assert process_settlement_offer_phase(rehydrated) == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
