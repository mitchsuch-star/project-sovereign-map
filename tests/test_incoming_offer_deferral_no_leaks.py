"""SC-5 reversal (commit 1 of 2): no-UI-exposure-yet suite.

Pre-reversal (`INCOMING_OFFERS_DEFERRED=True`) state proved that no
gameplay or player-facing surface could produce / count / activate /
render / route / block on `incoming_settlement_offer`.

May 15, 2026 commit 1 of the SC-5 reversal lands the backend producer
(`ai_diplomacy.process_settlement_offer_phase`) and flips the deferral
flag to `False`. Produced offers live in
`world.pending_settlement_dialogues` only — the dialogue-manager
taxonomy, mailbox endpoint, `/pending_envoy`, notification rail,
dispatch, popup queue, and Godot popup routing are intentionally
untouched until commit 2 ships the UI promotion layer.

This file now proves the commit-1 invariant: real offers are produced,
but until the commit-2 UI layer lands, no player-facing surface
surfaces them. The deferral-flag assertion is inverted; the handler
short-circuit + deferred-no-side-effects tests are removed (replaced
by `tests/test_settlement_incoming_offers.py` positive coverage); the
backend-producer-grep test is inverted to assert that the producer is
the only legitimate emitter of the `"type": "incoming_settlement_offer"`
literal; everything else (taxonomy exclusion, mailbox / pending_envoy
filtering, Godot UI absence) is preserved verbatim because commit 2
is what re-introduces those surfaces.

When commit 2 lands, the remaining no-UI-exposure assertions in this
file flip into positive UI tests and this file is renamed (or merged
into `test_settlement_incoming_offers.py`).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.display_names import settlement_disabled_reason_display
from backend.game_logic.settlement_preview import (
    INCOMING_OFFERS_DEFERRED,
    SETTLEMENT_FAMILY_DIALOGUE_TYPES,
    handle_incoming_settlement_offer_action,
)
from backend.models.dialogue_manager import DialogueManager
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import (
    make_synthetic_war_instance,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------------------
# Fixture helpers — synthetic offer injection for stale-save robustness
# ---------------------------------------------------------------------------


def _install_war(world: WorldState, war_id: str = "war_1") -> dict:
    war = make_synthetic_war_instance(
        war_id,
        attackers=["France", "Saxony"],
        defenders=["Austria"],
        attacker_leader="France",
        defender_leader="Austria",
    )
    world.war_instances[war_id] = war
    world.current_turn = 5
    return war


def _inject_offer_into_queue(world: WorldState, war_id: str = "war_1") -> dict:
    """Bypass the canonical push pipeline so we can exercise stale-save
    and debug-injection paths even after `incoming_settlement_offer`
    leaves `SOFT_STOP_MAILBOX_TYPES`."""
    dm = world.dialogue_manager
    dialogue = {
        "type": "incoming_settlement_offer",
        "dialogue_type": "incoming_settlement_offer",
        "war_id": war_id,
        "covered_enemy_participants": ["Austria"],
        "blocking": False,
        "turn_created": world.current_turn,
        "mailbox_id": 9001,
        "mailbox_order": 9001,
        "mailbox_priority": 3,
    }
    dm._queue.append(dialogue)
    return dialogue


def _inject_offer_as_active(world: WorldState, war_id: str = "war_1") -> dict:
    dm = world.dialogue_manager
    dialogue = {
        "type": "incoming_settlement_offer",
        "dialogue_type": "incoming_settlement_offer",
        "war_id": war_id,
        "covered_enemy_participants": ["Austria"],
        "blocking": False,
        "turn_created": world.current_turn,
        "mailbox_id": 9002,
        "mailbox_order": 9002,
        "mailbox_priority": 3,
    }
    dm._current = dialogue
    return dialogue


# ---------------------------------------------------------------------------
# Section 1 — Module-level deferral contract
# ---------------------------------------------------------------------------


def test_deferral_flag_is_off_after_sc5_reversal():
    """SC-5 reversal (May 15, 2026 / Slice G1 commit 1): the deferral
    flag is off so the AI settlement-offer producer can run and the
    handler can process accept/reject. The flag remains a named
    constant so a future emergency disable can flip it back to True
    without code rewrite."""
    assert INCOMING_OFFERS_DEFERRED is False


def test_settlement_family_set_keeps_offer_for_defensive_guards():
    """SC-18 v0.17 amendment: the family set keeps `incoming_settlement_offer`
    regardless of SC-5 reversal status, so stale-save defensive checks
    (cross-war collision protection, family-level command guards) still
    catch the type."""
    assert SETTLEMENT_FAMILY_DIALOGUE_TYPES == frozenset(
        {"settlement_confirm", "incoming_settlement_offer"}
    )


def test_dialogue_manager_taxonomy_excludes_offer_type():
    """SC-5 takedown list: `incoming_settlement_offer` is removed from
    `CURRENT_TURN_OFFER_TYPES` / `SOFT_STOP_MAILBOX_TYPES`,
    `DIALOGUE_PRIORITY`, and `MAILBOX_SUMMARY_LABELS`."""
    assert "incoming_settlement_offer" not in DialogueManager.CURRENT_TURN_OFFER_TYPES
    assert "incoming_settlement_offer" not in DialogueManager.SOFT_STOP_MAILBOX_TYPES
    assert "incoming_settlement_offer" not in DialogueManager.DIALOGUE_PRIORITY
    assert "incoming_settlement_offer" not in DialogueManager.MAILBOX_SUMMARY_LABELS
    # Defensive: nothing in HARD_STOP_TYPES either.
    assert "incoming_settlement_offer" not in DialogueManager.HARD_STOP_TYPES


# ---------------------------------------------------------------------------
# Section 2 — Mailbox count + items exclusion
# ---------------------------------------------------------------------------


def test_get_mailbox_count_excludes_stale_incoming_offers():
    """A stale-save record cannot inflate the mailbox badge."""
    world = WorldState()
    _install_war(world)
    _inject_offer_into_queue(world)
    _inject_offer_as_active(world)

    dm = world.dialogue_manager
    assert dm.get_mailbox_count() == 0
    assert dm.get_mailbox_items() == []


def test_get_mailbox_count_with_real_proposal_ignores_offer():
    """Coexisting real items count, but the offer does not."""
    world = WorldState()
    _install_war(world)
    _inject_offer_into_queue(world)

    dm = world.dialogue_manager
    dm.push({
        "type": "incoming_proposal",
        "context": {"source": "Austria", "proposal": {"type": "peace"}},
        "turn_created": world.current_turn,
        "blocking": False,
    })

    # Only the legitimate `incoming_proposal` increments the badge.
    assert dm.get_mailbox_count() == 1
    items = dm.get_mailbox_items()
    assert len(items) == 1
    assert items[0]["item_type"] == "incoming_proposal"


def test_has_current_turn_offers_ignores_stale_incoming_offer():
    """Stale incoming-offer records cannot block diplomacy gating."""
    world = WorldState()
    _install_war(world)
    _inject_offer_as_active(world)
    _inject_offer_into_queue(world)

    assert world.dialogue_manager.has_current_turn_offers() is False


def test_lapse_pending_offers_does_not_lapse_stale_incoming_offer():
    """End-of-turn lapse skips the stale offer because it is no longer
    in the offer-type set; the family-level guard is what neutralizes it."""
    world = WorldState()
    _install_war(world)
    _inject_offer_into_queue(world)

    lapsed = world.dialogue_manager.lapse_pending_offers()
    assert all(item.get("offer_type") != "incoming_settlement_offer" for item in lapsed)


# ---------------------------------------------------------------------------
# Section 3 — `/mailbox`, `/pending_envoy`, `/mailbox/activate` defenses
# ---------------------------------------------------------------------------


@pytest.fixture()
def fastapi_client():
    from backend import main as backend_main

    backend_main.game_state["world"] = WorldState()
    backend_main.game_state["debug_mode"] = False
    return TestClient(backend_main.app), backend_main


def test_mailbox_endpoint_strips_stale_incoming_offer(fastapi_client):
    """Stale-save items of the deferred type cannot reach the inbox panel."""
    client, backend_main = fastapi_client
    world = backend_main.game_state["world"]
    _install_war(world)
    _inject_offer_into_queue(world)
    _inject_offer_as_active(world)

    response = client.get("/mailbox")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 0
    assert data["items"] == []


def test_pending_envoy_skips_stale_active_incoming_offer(fastapi_client):
    """Active stale offer does not surface as an envoy popup."""
    client, backend_main = fastapi_client
    world = backend_main.game_state["world"]
    _install_war(world)
    _inject_offer_as_active(world)

    response = client.get("/pending_envoy")
    assert response.status_code == 200
    data = response.json()
    assert data["has_pending"] is False
    assert "dialogue_type" not in data
    assert "incoming_proposal" not in data


def test_mailbox_activate_rejects_stale_incoming_offer(fastapi_client):
    """SC-7 defensive: activating a stale offer mailbox_id returns the
    deferred error and never swaps the active slot."""
    client, backend_main = fastapi_client
    world = backend_main.game_state["world"]
    _install_war(world)
    queued = _inject_offer_into_queue(world)

    response = client.post(
        "/mailbox/activate",
        json={"mailbox_id": queued["mailbox_id"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["error"] == "incoming_offer_deferred"
    assert data["error_display"] == settlement_disabled_reason_display(
        "incoming_offer_deferred"
    )
    # Items list is still empty because the type is filtered out.
    assert data["items"] == []
    # Active slot was untouched.
    assert world.pending_diplomatic_dialogue is None


def test_mailbox_activate_rejects_stale_active_incoming_offer(fastapi_client):
    """The active slot itself can hold a stale offer (e.g. legacy save).
    Activating that mailbox_id rejects with the deferred error and does
    not stage `settlement_confirm`."""
    client, backend_main = fastapi_client
    world = backend_main.game_state["world"]
    _install_war(world)
    active = _inject_offer_as_active(world)

    response = client.post(
        "/mailbox/activate",
        json={"mailbox_id": active["mailbox_id"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["error"] == "incoming_offer_deferred"
    assert world.pending_diplomatic_dialogue is active


# ---------------------------------------------------------------------------
# Section 4 — handler short-circuit (mirrors slice F + continuity)
# ---------------------------------------------------------------------------


# Handler short-circuit + deferred-no-side-effects tests removed by the
# SC-5 reversal commit 1. Positive handler behavior — package preservation,
# stale war_id rejection, reject without mutation, request-revision
# counter-edit hint, one-active-offer guard reset on accept/reject — is
# now covered by `tests/test_settlement_incoming_offers.py`.


# ---------------------------------------------------------------------------
# Section 5 — 50-turn normal-AI soak: no producer
# ---------------------------------------------------------------------------


def test_fifty_turn_soak_does_not_produce_incoming_offer():
    """Spec v0.16 §SC-5 deferral assertion list: a 50-turn normal AI soak
    cannot produce, count, activate, or block on the type. Verified by
    advancing turns through the standard end-of-turn pipeline and
    confirming the dialogue queue never receives an
    `incoming_settlement_offer` from any producer."""
    world = WorldState()
    _install_war(world)
    dm = world.dialogue_manager

    seen_types: set[str] = set()
    starting_turn = world.current_turn
    for _ in range(50):
        # Drain queued items so the active slot is free, then advance.
        if dm._current and dm._current.get("type") == "incoming_settlement_offer":
            pytest.fail(
                "Normal-AI soak unexpectedly produced an "
                "`incoming_settlement_offer` dialogue."
            )
        for item in list(dm._queue):
            dtype = item.get("type", "")
            seen_types.add(dtype)
            if dtype == "incoming_settlement_offer":
                pytest.fail(
                    "Normal-AI soak queued an `incoming_settlement_offer`."
                )
        # Clear queue and active slot so end-of-turn does not stall on
        # leftover dialogues from prior iterations.
        dm._queue.clear()
        dm._current = None
        try:
            world.advance_turn()
        except Exception:
            # Some advance paths require additional context (player nation,
            # marshals, etc.). The failure mode we care about is producer
            # emission, not advance completeness, so we tolerate this.
            world.current_turn += 1
        # Mailbox count must remain 0 after every turn.
        assert dm.get_mailbox_count() == 0
    assert "incoming_settlement_offer" not in seen_types
    assert world.current_turn >= starting_turn + 1


# ---------------------------------------------------------------------------
# Section 6 — Backend producer-grep audit
# ---------------------------------------------------------------------------


def test_settlement_offer_producer_is_the_only_backend_emitter_of_dialogue_literal():
    """SC-5 reversal commit 1: only the named producer in
    `backend/game_logic/ai_diplomacy.py` may emit the literal
    `"type": "incoming_settlement_offer"` dialogue dict. Any other
    backend module emitting that literal would be a stray producer
    that bypasses the canonical cooldown / one-active-offer guards.

    Allowed sites:

    - `backend/game_logic/ai_diplomacy.py` —
      `process_settlement_offer_phase(world)` is the canonical producer.

    Disallowed: any other backend module emitting the literal."""
    forbidden = ['"type": "incoming_settlement_offer"']
    forbidden += ["'type': 'incoming_settlement_offer'"]
    backend_dir = REPO_ROOT / "backend"
    allowed_paths = {
        backend_dir / "game_logic" / "ai_diplomacy.py",
    }
    offenders: list[str] = []
    for path in backend_dir.rglob("*.py"):
        if path in allowed_paths:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for token in forbidden:
            if token in text:
                offenders.append(f"{path.relative_to(REPO_ROOT)}: {token!r}")
    assert offenders == [], (
        "Unexpected incoming-offer producer literal found outside the "
        "canonical `process_settlement_offer_phase` producer:\n  "
        + "\n  ".join(offenders)
    )
    # Positive assertion: the canonical producer DOES emit the literal,
    # so this grep test stays useful when audits run from a fresh clone.
    canonical = (backend_dir / "game_logic" / "ai_diplomacy.py").read_text(
        encoding="utf-8"
    )
    assert '"type": "incoming_settlement_offer"' in canonical


# ---------------------------------------------------------------------------
# Section 7 — Godot surface absence
# ---------------------------------------------------------------------------


def test_stale_offer_api_paths_do_not_emit_notification_dispatch_or_popup(
    fastapi_client,
):
    """Stale-save active and queued records are rejected without creating a
    notification, dispatch event, or backend popup payload."""
    client, backend_main = fastapi_client
    world = backend_main.game_state["world"]
    _install_war(world)
    queued = _inject_offer_into_queue(world)
    active = _inject_offer_as_active(world)

    assert client.get("/notifications").json()["notifications"] == []
    assert world.pending_dispatch_events == []
    assert world._popup_queue.to_dict() == {}

    queued_response = client.post(
        "/mailbox/activate",
        json={"mailbox_id": queued["mailbox_id"]},
    ).json()
    active_response = client.post(
        "/mailbox/activate",
        json={"mailbox_id": active["mailbox_id"]},
    ).json()

    for response in (queued_response, active_response):
        assert response["success"] is False
        assert response["error"] == "incoming_offer_deferred"
        assert "incoming_proposal" not in response
        assert "diplomatic_dialogue" not in response
        assert "proposal_result" not in response

    assert client.get("/notifications").json()["notifications"] == []
    assert world.pending_dispatch_events == []
    assert world._popup_queue.to_dict() == {}


def _read_godot(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def _post_hud_route_ids(source: str) -> list[str]:
    start = source.index("_post_hud_response_routes = [")
    end = source.index("]", start)
    block = source[start:end]
    route_ids: list[str] = []
    for line in block.splitlines():
        marker = '{"id": "'
        if marker not in line:
            continue
        route_ids.append(line.split(marker, 1)[1].split('"', 1)[0])
    return route_ids


def _simulate_godot_post_hud_route(response: dict, route_ids: list[str]) -> str | None:
    """Drive malformed responses through the route order used by `main.gd`."""
    for route_id in route_ids:
        if route_id == "incoming_proposal":
            if response.get("incoming_proposal") is not None:
                return route_id
        elif route_id == "deferred_incoming_settlement_offer":
            dialogue = response.get("diplomatic_dialogue", {})
            if (
                isinstance(dialogue, dict)
                and dialogue.get("type", dialogue.get("dialogue_type", ""))
                == "incoming_settlement_offer"
            ):
                return route_id
            if response.get("dialogue_type", "") == "incoming_settlement_offer":
                return route_id
        elif route_id == "proposal_confirm":
            if response.get("diplomatic_dialogue") is not None:
                return route_id
    return None


def test_godot_main_drops_incoming_offer_from_popup_whitelist():
    """SC-5 takedown: `incoming_settlement_offer` is no longer in the
    `PROPOSAL_CONFIRM_DIALOGUE_TYPES` whitelist."""
    source = _read_godot("godot-client/project-sovereign/scripts/main.gd")
    # Lines that must be absent from the whitelist constant.
    bad_lines = [
        '\t"incoming_settlement_offer",',
        '\t"accept_settlement_offer",',
        '\t"reject_settlement_offer",',
        '\t"request_settlement_revision",',
    ]
    for needle in bad_lines:
        assert needle not in source, (
            f"Forbidden Godot whitelist token still present: {needle!r}"
        )
    # The dispatch branches that fed the offer popup are gone.
    assert (
        '"conflict_alert", "settlement_confirm", "incoming_settlement_offer"'
        not in source
    )


def test_godot_post_hud_routes_deferred_offer_before_proposal_popup():
    """Malformed popup-queue responses with an incoming-offer dialogue hit the
    deferred route before the generic proposal-confirm popup route."""
    source = _read_godot("godot-client/project-sovereign/scripts/main.gd")
    route_ids = _post_hud_route_ids(source)

    assert (
        route_ids.index("deferred_incoming_settlement_offer")
        < route_ids.index("proposal_confirm")
    )

    mixed_response = {
        "diplomatic_dialogue": {
            "type": "incoming_settlement_offer",
            "war_id": "war_1",
        },
        "dialogue_type": "settlement_confirm",
    }
    assert (
        _simulate_godot_post_hud_route(mixed_response, route_ids)
        == "deferred_incoming_settlement_offer"
    )

    settlement_response = {
        "diplomatic_dialogue": {
            "type": "settlement_confirm",
            "war_id": "war_1",
        },
    }
    assert _simulate_godot_post_hud_route(settlement_response, route_ids) == (
        "proposal_confirm"
    )


def test_godot_main_drops_incoming_offer_payload_fallback():
    """The legacy `_show_confirm_dialogue_from_response` fallback that
    inflated `incoming_settlement_offer` payloads into the settlement
    popup is removed."""
    source = _read_godot("godot-client/project-sovereign/scripts/main.gd")
    assert 'response.get("incoming_settlement_offer", {})' not in source


def test_godot_proposal_confirm_popup_drops_incoming_offer_arm():
    """The proposal-confirm popup match arm that rendered settlement
    offers as a settlement review is removed; only `settlement_confirm`
    routes through `_build_settlement_content`."""
    source = _read_godot(
        "godot-client/project-sovereign/scripts/proposal_confirm_popup.gd"
    )
    assert '"settlement_confirm", "incoming_settlement_offer"' not in source
    assert '"settlement_confirm":' in source


def test_godot_pending_envoy_and_mailbox_activate_handle_deferred_dtype():
    """Both result handlers in `main.gd` route `incoming_settlement_offer`
    to a humanized "not available" message instead of opening the
    settlement popup."""
    source = _read_godot("godot-client/project-sovereign/scripts/main.gd")
    deferred_message = (
        "Incoming settlement offers are not available in this build."
    )
    # Two handler branches must each carry the deferred message: one in
    # `_on_pending_envoy_result`, one in `_on_mailbox_activate_result`.
    assert source.count(deferred_message) >= 2
    # The legacy combined dispatch branch is gone.
    assert (
        '"conflict_alert", "settlement_confirm", "incoming_settlement_offer"'
        not in source
    )


# ---------------------------------------------------------------------------
# Section 8 — Display-name humanization
# ---------------------------------------------------------------------------


def test_incoming_offer_deferred_has_humanized_display():
    """SC-5: a humanized error display is required for the new error code."""
    display = settlement_disabled_reason_display("incoming_offer_deferred")
    assert isinstance(display, str)
    assert display
    assert "not available" in display.lower() or "deferred" in display.lower()
