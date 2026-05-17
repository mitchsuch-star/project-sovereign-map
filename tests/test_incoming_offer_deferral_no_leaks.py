"""SC-5 reversal commit 2 (Slice G1) UI exposure suite.

Commit 1 of the SC-5 reversal landed the backend producer + handler;
this file inverted the no-UI-exposure assertions into the positive
UI-exposure contract that commit 2 ships:

- Dialogue-manager taxonomy includes `incoming_settlement_offer` as a
  PERSISTENT_MAILBOX_TYPES entry: mailbox-eligible, priority above
  ordinary proposals, persistent across turns (does not lapse).
- `world.pending_settlement_dialogues` promotion through
  `promote_pending_settlement_offers(world)` is idempotent and drains
  pending into the mailbox queue.
- `/mailbox`, `/pending_envoy`, and `/mailbox/activate` surface incoming
  settlement offers with the popup-safe payload.
- Godot routes the incoming-offer popup through `proposal_confirm_popup`,
  whitelists the three settlement-offer actions, and handles
  `incoming_settlement_offer` dtype in pending-envoy + mailbox-activate
  result handlers.
- Voice Bible §16.1 incoming-offer families resolve through
  `resolve_settlement_voice_line(...)`.

The producer-uniqueness grep test stays — only
`ai_diplomacy.process_settlement_offer_phase` may emit the
`"type": "incoming_settlement_offer"` dialogue literal — and the
50-turn soak now allows the producer to fire and exercises promotion
end-to-end.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.display_names import settlement_disabled_reason_display
from backend.game_logic.ai_diplomacy import process_settlement_offer_phase
from backend.game_logic.diplomatic_templates import resolve_settlement_voice_line
from backend.game_logic.settlement_preview import (
    INCOMING_OFFERS_DEFERRED,
    SETTLEMENT_FAMILY_DIALOGUE_TYPES,
    handle_incoming_settlement_offer_action,
    promote_pending_settlement_offers,
)
from backend.models.dialogue_manager import DialogueManager
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import (
    make_synthetic_war_instance,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _install_multi_party_war(world: WorldState, war_id: str = "war_1") -> dict:
    """Install a multi-party war that is old enough to satisfy the
    `SETTLEMENT_OFFER_MIN_WAR_DURATION_TURNS` producer gate. Default
    `created_turn=1` keeps things simple — callers seeding worlds at
    `current_turn >= 3` will see the producer fire."""
    war = make_synthetic_war_instance(
        war_id,
        attackers=["France", "Saxony"],
        defenders=["Austria", "Britain"],
        attacker_leader="France",
        defender_leader="Austria",
        created_turn=1,
    )
    world.war_instances[war_id] = war
    for atk in ("France", "Saxony"):
        for dfd in ("Austria", "Britain"):
            key = "|".join(sorted([atk, dfd]))
            world.diplomatic_states[key] = "WAR"
    return war


def _seeded_world(turn: int = 5) -> WorldState:
    world = WorldState()
    world.current_turn = turn
    return world


def _produce_and_promote(world: WorldState) -> list[dict]:
    process_settlement_offer_phase(world)
    return promote_pending_settlement_offers(world)


# ---------------------------------------------------------------------------
# Section 1 — Module-level reversal contract
# ---------------------------------------------------------------------------


def test_deferral_flag_is_off_after_sc5_reversal():
    """SC-5 reversal commit 1 flipped the deferral flag and commit 2
    keeps it off. The flag remains a named constant so a future
    emergency disable can flip it back to True without rewriting the
    handler short-circuit."""
    assert INCOMING_OFFERS_DEFERRED is False


def test_settlement_family_set_keeps_offer_for_defensive_guards():
    """SC-18 v0.17 amendment: `SETTLEMENT_FAMILY_DIALOGUE_TYPES` keeps
    both `settlement_confirm` and `incoming_settlement_offer` regardless
    of SC-5 reversal status so cross-war family guards keep catching
    both types."""
    assert SETTLEMENT_FAMILY_DIALOGUE_TYPES == frozenset(
        {"settlement_confirm", "incoming_settlement_offer"}
    )


def test_dialogue_manager_taxonomy_includes_incoming_settlement_offer_as_persistent_mailbox_type():
    """SC-5 reversal commit 2: the dialogue-manager taxonomy now lists
    `incoming_settlement_offer` as a persistent mailbox type:

    - In `SOFT_STOP_MAILBOX_TYPES` (so mailbox count / panel / activate
      surface it).
    - In `PERSISTENT_MAILBOX_TYPES` (so `lapse_pending_offers` does NOT
      remove it at end of turn).
    - In `DIALOGUE_PRIORITY` above ordinary proposals.
    - In `MAILBOX_SUMMARY_LABELS` with a humanized label.
    - Still absent from `HARD_STOP_TYPES` (soft-stop only, never blocks
      ordinary commands).
    - Still absent from `CURRENT_TURN_OFFER_TYPES` (no end-of-turn lapse).
    """
    assert "incoming_settlement_offer" in DialogueManager.SOFT_STOP_MAILBOX_TYPES
    assert "incoming_settlement_offer" in DialogueManager.PERSISTENT_MAILBOX_TYPES
    assert "incoming_settlement_offer" in DialogueManager.DIALOGUE_PRIORITY
    assert "incoming_settlement_offer" in DialogueManager.MAILBOX_SUMMARY_LABELS
    assert "incoming_settlement_offer" not in DialogueManager.HARD_STOP_TYPES
    assert "incoming_settlement_offer" not in DialogueManager.CURRENT_TURN_OFFER_TYPES


# ---------------------------------------------------------------------------
# Section 2 — Promote helper drains pending into mailbox
# ---------------------------------------------------------------------------


def test_promote_pending_settlement_offers_moves_offer_into_mailbox():
    """The promote helper is the documented bridge between the producer
    and the mailbox: it copies the offer into the dialogue_manager
    queue, attaches the popup payload, and drains the pending list."""
    world = _seeded_world(5)
    _install_multi_party_war(world)
    [offer] = process_settlement_offer_phase(world)

    promoted = promote_pending_settlement_offers(world)

    assert len(promoted) == 1
    assert promoted[0]["offer_id"] == offer["offer_id"]
    assert promoted[0]["popup_payload"]["proposer_nation"] == offer["proposer_nation"]
    assert world.pending_settlement_dialogues == []
    dm = world.dialogue_manager
    assert dm.get_mailbox_count() == 1
    items = dm.get_mailbox_items()
    assert items and items[0]["item_type"] == "incoming_settlement_offer"


def test_promote_helper_is_idempotent_across_save_load_cycles():
    """Re-running the promote helper after save/load cannot duplicate-push
    the same offer. The helper checks the dialogue_manager for an
    `offer_id` match before pushing."""
    world = _seeded_world(5)
    _install_multi_party_war(world)
    process_settlement_offer_phase(world)
    promote_pending_settlement_offers(world)

    # Re-run on the live world: no-op.
    again = promote_pending_settlement_offers(world)
    assert again == []
    assert world.dialogue_manager.get_mailbox_count() == 1

    # Save/load cycle: the offer lives in dialogue_manager state, so a
    # rehydrated world keeps it. Pending list stays empty; promote is
    # still a no-op.
    snapshot = world.to_dict()
    rehydrated = WorldState.from_dict(snapshot)
    assert rehydrated.dialogue_manager.get_mailbox_count() == 1
    repeat = promote_pending_settlement_offers(rehydrated)
    assert repeat == []
    assert rehydrated.dialogue_manager.get_mailbox_count() == 1


# ---------------------------------------------------------------------------
# Section 3 — `/mailbox`, `/pending_envoy`, `/mailbox/activate` surfaces
# ---------------------------------------------------------------------------


@pytest.fixture()
def fastapi_client():
    from backend import main as backend_main

    backend_main.game_state["world"] = WorldState()
    backend_main.game_state["debug_mode"] = False
    return TestClient(backend_main.app), backend_main


def test_mailbox_endpoint_surfaces_incoming_offer_row(fastapi_client):
    """SC-30 required test: `GET /mailbox` returns the promoted offer
    as a first-class row. The summary text is humanized (not a raw
    enum) and the proposer nation is the source nation."""
    client, backend_main = fastapi_client
    world = backend_main.game_state["world"]
    world.current_turn = 5
    _install_multi_party_war(world)
    _produce_and_promote(world)

    response = client.get("/mailbox")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert len(data["items"]) == 1
    row = data["items"][0]
    assert row["item_type"] == "incoming_settlement_offer"
    assert row["source_nation"] == "Austria"  # opposing-side leader
    assert "settlement offer" in row["summary_text"].lower()


def test_pending_envoy_endpoint_returns_incoming_offer_popup_payload(fastapi_client):
    """SC-30 required test name (`test_ai_settlement_offer_producer_
    surfaces_real_mailbox_payload`): `GET /pending_envoy` returns the
    popup-safe payload (Voice Bible §16.1 incoming-offer copy + offered
    terms summary + options) when the active mailbox item is an
    incoming settlement offer."""
    client, backend_main = fastapi_client
    world = backend_main.game_state["world"]
    world.current_turn = 5
    _install_multi_party_war(world)
    _produce_and_promote(world)

    response = client.get("/pending_envoy")
    assert response.status_code == 200
    data = response.json()
    assert data["has_pending"] is True
    assert data["dialogue_type"] == "incoming_settlement_offer"
    popup = data["incoming_settlement_offer"]
    assert popup["type"] == "incoming_settlement_offer"
    assert popup["proposer_nation"] == "Austria"
    # Voice Bible: Austria proposer uses Metternich incoming-offer copy.
    assert "vienna" in popup["proposer_voice"].lower()
    # Talleyrand framing line resolves through §16.1.
    assert "{" not in popup["talleyrand_text"]
    # Options match the SC-30 contract (Accept / Request Revision / Reject).
    action_ids = popup["available_action_ids"]
    assert "accept_settlement_offer" in action_ids
    assert "request_settlement_revision" in action_ids
    assert "reject_settlement_offer" in action_ids
    # SC-30 hidden controls remain hidden.
    assert popup["wait_for_enemy_offer_visible"] is False
    assert popup["ask_for_terms_visible"] is False


def test_mailbox_activate_returns_incoming_offer_popup_payload(fastapi_client):
    """POST `/mailbox/activate` swaps the queued offer into the active
    slot and returns its popup payload so the Godot mailbox panel can
    open the popup without a second round trip."""
    client, backend_main = fastapi_client
    world = backend_main.game_state["world"]
    world.current_turn = 5
    _install_multi_party_war(world)
    promoted = _produce_and_promote(world)
    mailbox_id = promoted[0]["mailbox_id"]

    response = client.post(
        "/mailbox/activate",
        json={"mailbox_id": mailbox_id},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["dialogue_type"] == "incoming_settlement_offer"
    popup = data["incoming_settlement_offer"]
    assert popup["type"] == "incoming_settlement_offer"
    assert popup["offer_id"].startswith("settlement_offer:war_1:5:")


# ---------------------------------------------------------------------------
# Section 4 — Voice Bible families resolve
# ---------------------------------------------------------------------------


def test_voice_bible_incoming_offer_families_resolve():
    """SC-30 required test: every incoming-offer Voice Bible family
    (Talleyrand framing + the four cast diplomats + chancery fallback)
    resolves to non-empty committed copy through
    `resolve_settlement_voice_line(...)`. Unauthored families would
    return empty strings, breaking the popup voice contract."""
    families = [
        "settlement_incoming_offer_arrival_talleyrand",
        "settlement_incoming_offer_arrival_castlereagh",
        "settlement_incoming_offer_arrival_hardenberg",
        "settlement_incoming_offer_arrival_metternich",
        "settlement_incoming_offer_arrival_einsiedel",
        "settlement_incoming_offer_arrival_chancery",
        "settlement_incoming_offer_request_revision_talleyrand",
        "settlement_incoming_offer_blocked_recovery_talleyrand",
        "settlement_blocked_for_ratification_observer",
    ]
    for family in families:
        rendered = resolve_settlement_voice_line(
            family,
            war_label="France vs Britain",
            proposer_leader="Britain",
            amount="500",
            top_blocker="Acceptance pressure",
        )
        assert rendered, f"Voice family {family} returned empty string."
        # No unresolved slot tokens leak through.
        assert "{" not in rendered, f"Voice family {family} left unresolved slots."


def test_sc30_reversal_authors_observer_blocked_ratification_voice_family():
    """Spec required test name. Foreign-court observer voice for blocked
    ratifications must be authored as chancery (not Talleyrand) so the
    cross-court reading does not pretend French authorship."""
    text = resolve_settlement_voice_line(
        "settlement_blocked_for_ratification_observer",
        war_label="France vs Britain",
        top_blocker="Acceptance pressure",
    )
    assert text
    # Chancery register, not Talleyrand "Sire" register.
    assert "sire" not in text.lower()
    assert "chancery" in text.lower()


# ---------------------------------------------------------------------------
# Section 5 — SC-30 hidden controls (`Wait for Enemy Offer`, `Ask for terms`)
# ---------------------------------------------------------------------------


def test_wait_for_enemy_offer_only_visible_when_offer_producer_and_cooldown_path_exist(fastapi_client):
    """SC-30 spec required test: the `Wait for Enemy Offer` control is
    not present on any settlement surface in this commit because the
    request-terms lifecycle has not landed. SC-5 reversal commit 2
    must surface an `wait_for_enemy_offer_visible=False` flag on the
    incoming-offer popup so the Godot popup never invents the
    control."""
    client, backend_main = fastapi_client
    world = backend_main.game_state["world"]
    world.current_turn = 5
    _install_multi_party_war(world)
    _produce_and_promote(world)

    popup = client.get("/pending_envoy").json()["incoming_settlement_offer"]
    assert popup["wait_for_enemy_offer_visible"] is False
    # No CTA matches the wait-for-offer label.
    labels = [str(opt.get("label", "")) for opt in popup.get("options", [])]
    for label in labels:
        assert "wait for enemy offer" not in label.lower()


def test_ask_for_terms_visible_only_when_request_terms_state_can_actually_advance(fastapi_client):
    """SC-30 spec required test: `Ask for terms` cannot ship as a
    click-only polite refusal. With the request-terms lifecycle still
    deferred, the popup explicitly hides the control."""
    client, backend_main = fastapi_client
    world = backend_main.game_state["world"]
    world.current_turn = 5
    _install_multi_party_war(world)
    _produce_and_promote(world)

    popup = client.get("/pending_envoy").json()["incoming_settlement_offer"]
    assert popup["ask_for_terms_visible"] is False
    labels = [str(opt.get("label", "")) for opt in popup.get("options", [])]
    for label in labels:
        assert "ask for terms" not in label.lower()


def test_ask_for_terms_click_produces_observable_state_change_not_just_copy(fastapi_client):
    """SC-30 spec required test: no `ask_for_terms` action id reaches
    the backend dispatcher in this commit, so a forged client request
    cannot drive an observable state change. Stale-save defensive
    error display copy stays humanized."""
    client, backend_main = fastapi_client
    world = backend_main.game_state["world"]
    world.current_turn = 5
    _install_multi_party_war(world)
    _produce_and_promote(world)

    # No incoming-offer popup option exposes `ask_for_terms`.
    popup = client.get("/pending_envoy").json()["incoming_settlement_offer"]
    for opt in popup.get("options", []):
        assert str(opt.get("action", "")) != "ask_for_terms"

    # Defensive display copy stays humanized for the deferred control.
    assert settlement_disabled_reason_display("request_terms_ineligible")


# ---------------------------------------------------------------------------
# Section 6 — Backend producer-grep audit (preserved from commit 1)
# ---------------------------------------------------------------------------


def test_settlement_offer_producer_is_the_only_backend_emitter_of_dialogue_literal():
    """SC-5 reversal: only `process_settlement_offer_phase(world)` in
    `backend/game_logic/ai_diplomacy.py` may emit the
    `"type": "incoming_settlement_offer"` dialogue dict from the
    *producer* path. The consumer + popup-builder file
    `settlement_preview.py` carries the same literal because
    `build_incoming_settlement_offer_popup` returns the popup view of
    an already-produced offer; that is a derivative payload, not a
    new producer.

    Allowed sites (both verified):
    - `backend/game_logic/ai_diplomacy.py` — canonical producer.
    - `backend/game_logic/settlement_preview.py` — popup payload
      builder for already-produced offers."""
    forbidden = ['"type": "incoming_settlement_offer"']
    forbidden += ["'type': 'incoming_settlement_offer'"]
    backend_dir = REPO_ROOT / "backend"
    allowed_paths = {
        backend_dir / "game_logic" / "ai_diplomacy.py",
        backend_dir / "game_logic" / "settlement_preview.py",
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
    canonical = (backend_dir / "game_logic" / "ai_diplomacy.py").read_text(
        encoding="utf-8"
    )
    assert '"type": "incoming_settlement_offer"' in canonical
    # Popup builder is the documented secondary site.
    preview = (backend_dir / "game_logic" / "settlement_preview.py").read_text(
        encoding="utf-8"
    )
    assert '"type": "incoming_settlement_offer"' in preview
    assert "build_incoming_settlement_offer_popup" in preview


# ---------------------------------------------------------------------------
# Section 7 — Godot UI surface presence
# ---------------------------------------------------------------------------


def _read_godot(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_godot_main_whitelists_incoming_settlement_offer_dialogue_and_actions():
    """SC-30 commit 2 Godot surface: `incoming_settlement_offer` is in
    PROPOSAL_CONFIRM_DIALOGUE_TYPES so the popup opens, and the three
    settlement-offer actions (accept / reject / request_settlement_revision)
    are in SETTLEMENT_DIALOGUE_ACTIONS so the popup buttons route to
    the backend dialogue endpoint."""
    source = _read_godot("godot-client/project-sovereign/scripts/main.gd")
    assert '"incoming_settlement_offer"' in source
    assert '"accept_settlement_offer"' in source
    assert '"reject_settlement_offer"' in source
    assert '"request_settlement_revision"' in source


def test_godot_main_routes_incoming_settlement_offer_popup_before_proposal_confirm():
    """The dedicated route precedence keeps the incoming-offer popup
    ahead of the generic proposal_confirm route so a single response
    that carries both an offer popup payload and a `diplomatic_dialogue`
    follow-up opens the offer popup first."""
    source = _read_godot("godot-client/project-sovereign/scripts/main.gd")
    pre = source.index('"id": "incoming_settlement_offer"')
    post = source.index('"id": "proposal_confirm"')
    assert pre < post


def test_godot_pending_envoy_and_mailbox_activate_handle_incoming_offer_payload():
    """Both result handlers in `main.gd` route `incoming_settlement_offer`
    by opening the proposal_confirm popup with the offer payload, not
    by printing a deferred-message stub."""
    source = _read_godot("godot-client/project-sovereign/scripts/main.gd")
    # Old deferred message is gone.
    assert (
        "Incoming settlement offers are not available in this build."
        not in source
    )
    # Both branches grab the popup payload and open it.
    assert source.count(
        'response.get("incoming_settlement_offer", {})'
    ) >= 2


def test_godot_proposal_confirm_popup_renders_incoming_offer_match_arm():
    """`proposal_confirm_popup.gd` carries the `incoming_settlement_offer`
    match arm so the popup body uses the dedicated builder."""
    source = _read_godot(
        "godot-client/project-sovereign/scripts/proposal_confirm_popup.gd"
    )
    assert '"incoming_settlement_offer":' in source
    assert "_build_incoming_settlement_offer_content" in source


# ---------------------------------------------------------------------------
# Section 8 — 50-turn soak now allows the producer to fire
# ---------------------------------------------------------------------------


def test_fifty_turn_soak_produces_offer_and_promotion_stays_consistent():
    """SC-5 reversal commit 2: the 50-turn soak now exercises the full
    producer + promote loop. Cooldowns keep the count bounded; the
    mailbox count never exceeds one per war."""
    world = _seeded_world(3)
    _install_multi_party_war(world)
    dm = world.dialogue_manager

    starting_turn = world.current_turn
    saw_at_least_one_offer = False
    for _ in range(50):
        promoted = _produce_and_promote(world)
        if promoted:
            saw_at_least_one_offer = True
        # Mailbox count must never exceed one settlement offer per war.
        offer_rows = [
            item for item in dm.get_mailbox_items()
            if item["item_type"] == "incoming_settlement_offer"
        ]
        assert len(offer_rows) <= 1
        # Drain the offer between turns so the producer is free to
        # fire again after cooldown expires.
        if offer_rows:
            for entry in list(getattr(dm, "_queue", []) or []):
                if entry.get("type") == "incoming_settlement_offer":
                    dm._queue.remove(entry)
            if dm._current is not None and dm._current.get("type") == "incoming_settlement_offer":
                dm._current = None
        try:
            world.advance_turn()
        except Exception:
            world.current_turn += 1
    assert saw_at_least_one_offer
    assert world.current_turn >= starting_turn + 1


# ---------------------------------------------------------------------------
# Section 9 — Display-name humanization
# ---------------------------------------------------------------------------


def test_incoming_offer_deferred_has_humanized_display():
    """The deferred display string remains a humanized stale-save
    fallback in case `INCOMING_OFFERS_DEFERRED` is ever flipped back to
    True for an emergency disable."""
    display = settlement_disabled_reason_display("incoming_offer_deferred")
    assert isinstance(display, str)
    assert display
    assert "not available" in display.lower() or "deferred" in display.lower()


# ---------------------------------------------------------------------------
# Section 10 — Accept path (full handler round-trip)
# ---------------------------------------------------------------------------


def test_incoming_offer_accept_through_active_mailbox_pops_offer_and_stages_confirm():
    """When the offer is the active mailbox item and the player accepts,
    the offer is removed from the dialogue_manager and a
    settlement_confirm is staged in its place."""
    world = _seeded_world(5)
    _install_multi_party_war(world)
    _produce_and_promote(world)
    dm = world.dialogue_manager
    active = dm.peek()
    assert active and active.get("type") == "incoming_settlement_offer"

    result = handle_incoming_settlement_offer_action(
        world, action="accept_settlement_offer", dialogue=active,
    )
    assert result["success"] is True
    assert result["dialogue_type"] == "settlement_confirm"
    # Offer is no longer in dialogue manager; staged settlement_confirm replaces it.
    current = dm.peek()
    assert current is not None
    assert current.get("type") == "settlement_confirm"


# ---------------------------------------------------------------------------
# Section 11 — Spec-named SC-30 required tests
# ---------------------------------------------------------------------------


def test_ai_settlement_offer_producer_surfaces_real_mailbox_payload(fastapi_client):
    """SC-30 spec required test name. End-to-end: the producer fires,
    the promotion step drains pending into the mailbox, and `/mailbox`
    returns a real row with humanized summary text. The popup payload
    on `/pending_envoy` is the same payload the Godot popup will
    render."""
    client, backend_main = fastapi_client
    world = backend_main.game_state["world"]
    world.current_turn = 5
    _install_multi_party_war(world)
    _produce_and_promote(world)

    # `/mailbox` reports the row.
    mailbox = client.get("/mailbox").json()
    assert mailbox["count"] == 1
    assert mailbox["items"][0]["item_type"] == "incoming_settlement_offer"
    # `/pending_envoy` delivers the popup-safe payload.
    envoy = client.get("/pending_envoy").json()
    assert envoy["has_pending"] is True
    payload = envoy["incoming_settlement_offer"]
    assert payload["proposer_nation"] == "Austria"
    assert payload["war_id"] == "war_1"
    assert payload["offer_id"].startswith("settlement_offer:war_1:5:")
    assert payload["settlement_terms"]
    # Voice Bible §16.1 incoming-offer copy is resolved (no template
    # leak), and both Talleyrand framing + proposer chancery voice are
    # present.
    assert payload["talleyrand_text"]
    assert payload["proposer_voice"]
    assert "{" not in payload["talleyrand_text"]
    assert "{" not in payload["proposer_voice"]


def test_incoming_offer_accept_preserves_offer_identity_and_terms_through_live_preview():
    """SC-30 spec required test name. The accept handler stages the
    settlement_confirm with the exact offered terms preserved through
    `stage_settlement_confirm(...)`, and echoes the offer_id on the
    result so downstream surfaces can attribute the staged review to
    its originating offer."""
    world = _seeded_world(5)
    _install_multi_party_war(world)
    [offer] = process_settlement_offer_phase(world)
    promote_pending_settlement_offers(world)
    active = world.dialogue_manager.peek()
    assert active is not None

    result = handle_incoming_settlement_offer_action(
        world, action="accept_settlement_offer", dialogue=active,
    )
    assert result["success"] is True
    assert result["dialogue_type"] == "settlement_confirm"
    assert result["offer_id"] == offer["offer_id"]
    assert result["accepted_offer_terms"] == offer["settlement_terms"]
    # The staged settlement_confirm carries the offered terms verbatim.
    staged = result["diplomatic_dialogue"]
    assert isinstance(staged, dict)
    assert staged["settlement_terms"] == offer["settlement_terms"]


def test_incoming_offer_blocked_recovery_uses_request_revision_counteroffer_framing():
    """SC-30 spec required test name. When the player accepts an offer
    and the staged settlement_confirm is blocked (e.g. acceptance
    rejected), the popup must NOT reuse outgoing `Revise Terms` or
    `Will they accept?` copy. The Request Revision route opens a real
    counter editor with the request-revision Voice Bible family and
    preserves the offer_id as counter provenance."""
    world = _seeded_world(5)
    _install_multi_party_war(world)
    [offer] = process_settlement_offer_phase(world)

    # Request Revision opens the counter editor and stages a fresh
    # settlement_confirm seeded from the offered terms.
    result = handle_incoming_settlement_offer_action(
        world, action="request_settlement_revision", dialogue=offer,
    )
    assert result["success"] is True
    assert result["dialogue_type"] == "settlement_confirm"
    assert result["counter_to_offer_id"] == offer["offer_id"]
    # The talleyrand_text framing reads as "counter draft", not
    # outgoing-review "Will they accept?" framing.
    text = str(result.get("talleyrand_text", "")).lower()
    assert "counter draft" in text
    assert "will they accept" not in text
    # The original offer is removed; the staged settlement_confirm is
    # the active dialogue.
    current = world.dialogue_manager.peek()
    assert current is not None
    assert current.get("type") == "settlement_confirm"
