"""WB-D: War bargain presentation extension tests.

Tests commitments routing, voiced templates, witness scope, notifications,
dispatch integration, response routes, and ledger badge rendering.
"""

from pathlib import Path

import pytest
from backend.game_logic.commitments_routing import (
    COMMITMENTS_ROUTES,
    commitments_label,
    commitments_notice_details,
    commitments_priority,
    commitments_route,
    format_commitments_notice,
)
from backend.game_logic.diplomacy import (
    _emit_bargain_event,
    _fulfill_bargain,
    _get_bargain_dominant_witness_scope,
    _get_bargain_witnesses,
    _get_live_bargains,
    _void_bargain,
    breach_bargain,
    create_war_bargain_commitment,
    get_all_bargains_for_ledger,
    get_live_bargains_for_ledger,
    process_bargain_lifecycle,
    set_diplomatic_state,
)
from backend.models.world_state import WorldState
from backend.notifications import (
    BARGAIN_BREACHED,
    BARGAIN_FULFILLED,
    BARGAIN_VOIDED,
)


def _wb_world() -> WorldState:
    world = WorldState()
    world.enemy_nations = ["Austria", "Prussia", "Britain", "Russia", "Saxony"]
    world.diplomatic_states = {}
    world.active_treaties = {}
    world.vassals = {}
    world.pending_dispatch_events = []
    world.event_log = []
    world.diplomatic_commitments = {}
    world.next_commitment_id = 1
    world.diplomatic_reliability = {"France": 50, "Prussia": 50, "Britain": 50}
    world.betrayal_history = {}
    world.current_turn = 5
    return world


def _create_live_bargain(world, status="active", **overrides):
    set_diplomatic_state(world, "France", "Prussia", "ALLIANCE", "setup")
    set_diplomatic_state(world, "France", "Britain", "WAR", "setup")
    rec = create_war_bargain_commitment(
        world, "France", "Prussia", "Britain", "Hanover",
        "treaty_clause", "France|Prussia",
    )
    if status == "triggered":
        rec["status"] = "triggered"
        rec["triggered_turn"] = int(world.current_turn)
        set_diplomatic_state(world, "Prussia", "Britain", "WAR", "setup")
    for k, v in overrides.items():
        rec[k] = v
    return rec


# ═══════════════════════════════════════════════════════
# ROUTING TABLE COMPLETENESS (3 tests)
# ═══════════════════════════════════════════════════════

_BARGAIN_EVENT_TYPES = [
    "bargain_fulfilled",
    "bargain_breached",
    "bargain_voided",
    "bargain_ratified",
    "bargain_triggered",
]


@pytest.mark.parametrize("event_type", _BARGAIN_EVENT_TYPES)
def test_bargain_event_in_routing_table(event_type):
    assert event_type in COMMITMENTS_ROUTES
    route = COMMITMENTS_ROUTES[event_type]
    assert route["icon"].startswith("icon_")
    assert route["label"]
    assert route["template"].startswith("commitments_notice_")
    assert route["speaker"]


@pytest.mark.parametrize("event_type", _BARGAIN_EVENT_TYPES)
def test_bargain_commitments_notice_details(event_type):
    details = commitments_notice_details(event_type, {"beneficiary": "Prussia"})
    assert details["event_type"] == event_type
    assert details["template_key"].startswith("commitments_notice_")
    assert details["icon"]
    assert details["label"]


def test_bargain_routing_priorities():
    assert commitments_priority("bargain_fulfilled") == "HIGH"
    assert commitments_priority("bargain_breached") == "CRITICAL"
    assert commitments_priority("bargain_voided") == "NORMAL"
    assert commitments_priority("bargain_ratified") == "NORMAL"
    assert commitments_priority("bargain_triggered") == "HIGH"


# ═══════════════════════════════════════════════════════
# TEMPLATE FORMATTING (4 tests)
# ═══════════════════════════════════════════════════════

def test_bargain_fulfilled_template():
    text = format_commitments_notice("bargain_fulfilled", {
        "beneficiary": "Prussia",
        "claim_region": "Hanover",
    })
    assert "Prussia" in text
    assert "Hanover" in text
    assert "belief" in text.lower()


def test_bargain_breached_french_fault_template():
    text = format_commitments_notice("bargain_breached", {
        "beneficiary": "Prussia",
        "claim_region": "Hanover",
        "end_reason_family": "french_breach",
        "injured_diplomat": "Hardenberg",
        "dominant_witness_scope": "ally",
    })
    assert "Hardenberg" in text
    assert "Hanover" in text
    assert "Prussia" in text
    assert "disappointment" in text.lower()


def test_bargain_breached_counterparty_template():
    text = format_commitments_notice("bargain_breached", {
        "beneficiary": "Prussia",
        "claim_region": "Hanover",
        "end_reason_family": "counterparty_reversal",
        "fault_nation": "Prussia",
    })
    assert "Prussia" in text
    assert "no fault" in text.lower()


def test_bargain_voided_template():
    text = format_commitments_notice("bargain_voided", {
        "beneficiary": "Prussia",
        "claim_region": "Hanover",
        "end_reason": "source_treaty_lost",
    })
    assert "Prussia" in text
    assert "Hanover" in text
    assert "alliance" in text.lower()


@pytest.mark.parametrize("reason", [
    "source_treaty_lost",
    "beneficiary_aligned_with_enemy",
    "beneficiary_joined_anti_promiser_coalition",
    "claim_basis_lost",
    "parties_at_war",
    "zombie_lapse",
])
def test_bargain_voided_template_covers_live_void_reasons(reason):
    text = format_commitments_notice("bargain_voided", {
        "beneficiary": "Prussia",
        "claim_region": "Hanover",
        "end_reason": reason,
    })

    assert "Circumstances rendered it moot" not in text
    assert "Prussia" in text
    assert "Hanover" in text


# ═══════════════════════════════════════════════════════
# WITNESS SCOPE CLASSIFICATION (3 tests)
# ═══════════════════════════════════════════════════════

def test_bargain_witnesses_include_scope_reason():
    world = _wb_world()
    bargain = _create_live_bargain(world)
    set_diplomatic_state(world, "Austria", "Prussia", "ALLIANCE", "setup")

    witnesses = _get_bargain_witnesses(world, bargain)
    assert isinstance(witnesses, list)
    for w in witnesses:
        assert "nation" in w
        assert "scope_reason" in w
    austria_w = [w for w in witnesses if w["nation"] == "Austria"]
    if austria_w:
        assert austria_w[0]["scope_reason"] == "ally"


def test_bargain_dominant_witness_scope_precedence():
    witnesses = [
        {"nation": "Austria", "scope_reason": "region_observer"},
        {"nation": "Russia", "scope_reason": "ally"},
        {"nation": "Saxony", "scope_reason": "rival"},
    ]
    assert _get_bargain_dominant_witness_scope(witnesses) == "ally"


def test_bargain_dominant_witness_scope_empty():
    assert _get_bargain_dominant_witness_scope([]) == ""


# ═══════════════════════════════════════════════════════
# NOTIFICATION EMISSION (3 tests)
# ═══════════════════════════════════════════════════════

def test_fulfilled_emits_notification():
    world = _wb_world()
    bargain = _create_live_bargain(world, status="triggered")
    region = world.regions.get("Hanover")
    if region:
        region.controller = "France"
    _fulfill_bargain(world, bargain)
    _emit_bargain_event(world, bargain, "bargain_fulfilled")
    pending = world.notifications.get_pending()
    fulfilled_notifs = [n for n in pending if n["type"] == BARGAIN_FULFILLED]
    assert len(fulfilled_notifs) == 1
    assert fulfilled_notifs[0]["priority"] == 1  # HIGH


def test_breached_emits_critical_notification():
    world = _wb_world()
    bargain = _create_live_bargain(world, status="triggered")
    breach_bargain(world, bargain, "explicit_repudiation")
    pending = world.notifications.get_pending()
    breached_notifs = [n for n in pending if n["type"] == BARGAIN_BREACHED]
    assert len(breached_notifs) == 1
    assert breached_notifs[0]["priority"] == 2  # CRITICAL


def test_voided_emits_normal_notification():
    world = _wb_world()
    bargain = _create_live_bargain(world)
    _void_bargain(world, bargain, {
        "reason": "source_treaty_lost",
        "family": "counterparty_reversal",
        "fault_nation": "Prussia",
    })
    _emit_bargain_event(world, bargain, "bargain_voided")
    pending = world.notifications.get_pending()
    voided_notifs = [n for n in pending if n["type"] == BARGAIN_VOIDED]
    assert len(voided_notifs) == 1
    assert voided_notifs[0]["priority"] == 0  # NORMAL


# ═══════════════════════════════════════════════════════
# DISPATCH INTEGRATION (2 tests)
# ═══════════════════════════════════════════════════════

def test_dispatch_uses_commitments_route_for_bargain_events():
    """Bargain events should be formatted through commitments routing, not raw templates."""
    from backend.game_logic.dispatch import _format_dispatch_event_text

    text = _format_dispatch_event_text("bargain_fulfilled", {
        "beneficiary": "Prussia",
        "claim_region": "Hanover",
    })
    assert "belief" in text.lower()


def test_dispatch_bargain_breached_uses_commitments_route():
    from backend.game_logic.dispatch import _format_dispatch_event_text

    text = _format_dispatch_event_text("bargain_breached", {
        "beneficiary": "Prussia",
        "claim_region": "Hanover",
        "end_reason_family": "french_breach",
        "injured_diplomat": "Hardenberg",
        "dominant_witness_scope": "rival",
    })
    assert "Hardenberg" in text
    assert "opportunity" in text.lower()


# ═══════════════════════════════════════════════════════
# RESPONSE ROUTES (1 test)
# ═══════════════════════════════════════════════════════

def test_bargain_breached_response_route():
    route = commitments_route("bargain_breached", {"end_reason_family": "french_breach"})
    assert route["review_target"] == "diplomacy_wizard"
    assert route["review_label"] == "Propose Redress"


# ═══════════════════════════════════════════════════════
# COUNTERPARTY BREACH ROUTING (2 tests)
# ═══════════════════════════════════════════════════════

def test_counterparty_breach_route_uses_override():
    route = commitments_route("bargain_breached", {"end_reason_family": "counterparty_reversal"})
    assert route["priority"] == "NORMAL"
    assert route["speaker"] == "talleyrand"
    assert route["review_target"] == "ledger_war_bargains"


def test_counterparty_breach_label_uses_period_copy():
    route = commitments_route("bargain_breached", {"end_reason_family": "counterparty_reversal"})
    assert route["label"] == "Bargain Broken by Other Court"
    assert "counterparty" not in route["label"].lower()


def test_counterparty_breach_priority_is_normal():
    assert commitments_priority("bargain_breached", {"end_reason_family": "counterparty_reversal"}) == "NORMAL"


# ═══════════════════════════════════════════════════════
# GODOT NOTIFICATION ROUTING (2 tests)
# ═══════════════════════════════════════════════════════

def test_godot_main_forwards_bargain_review_targets():
    root = Path(__file__).resolve().parents[1]
    main = (
        root / "godot-client" / "project-sovereign" / "scripts" / "main.gd"
    ).read_text(encoding="utf-8")

    assert 'review_target == "diplomacy_wizard"' in main
    assert "_open_diplomacy_wizard()" in main
    assert 'review_target.begins_with("ledger_")' in main
    assert "top_bar.open_diplomatic_ledger_review(review_target)" in main


def test_godot_notification_bar_recognizes_bargain_notices():
    root = Path(__file__).resolve().parents[1]
    notification_bar = (
        root / "godot-client" / "project-sovereign" / "scripts"
        / "notification_bar.gd"
    ).read_text(encoding="utf-8")

    for event_type in (
        "bargain_fulfilled",
        "bargain_breached",
        "bargain_voided",
        "bargain_ratified",
        "bargain_triggered",
    ):
        assert f'"{event_type}": true' in notification_bar

    for icon_key in (
        "icon_bargain_honoured",
        "icon_bargain_broken",
        "icon_bargain_lapsed",
        "icon_bargain_sealed",
        "icon_bargain_activated",
    ):
        assert f'"{icon_key}"' in notification_bar


# LEDGER BADGES (3 tests)

def test_ledger_live_bargains_no_badge():
    world = _wb_world()
    _create_live_bargain(world)
    entries = get_live_bargains_for_ledger(world)
    assert len(entries) == 1
    assert "badge" not in entries[0]


def test_ledger_all_bargains_includes_completed():
    world = _wb_world()
    bargain = _create_live_bargain(world, status="triggered")
    _fulfill_bargain(world, bargain)
    entries = get_all_bargains_for_ledger(world)
    fulfilled = [e for e in entries if e["status"] == "fulfilled"]
    assert len(fulfilled) == 1
    assert fulfilled[0]["badge"] == "honoured"


def test_ledger_all_bargains_badge_values():
    world = _wb_world()
    b1 = _create_live_bargain(world, status="triggered")
    _fulfill_bargain(world, b1)

    set_diplomatic_state(world, "France", "Austria", "ALLIANCE", "setup")
    set_diplomatic_state(world, "France", "Russia", "WAR", "setup")
    set_diplomatic_state(world, "Austria", "Russia", "WAR", "setup")
    b2 = create_war_bargain_commitment(
        world, "France", "Austria", "Russia", "Vienna",
        "treaty_clause", "France|Austria",
        validate=False,
    )
    b2["status"] = "triggered"
    breach_bargain(world, b2, "explicit_repudiation")

    entries = get_all_bargains_for_ledger(world)
    badges = {e["status"]: e.get("badge", "") for e in entries}
    assert badges.get("fulfilled") == "honoured"
    assert badges.get("breached") == "broken"


def test_ledger_bargain_created_turns_are_ints():
    world = _wb_world()
    live = _create_live_bargain(world)
    live["created_turn"] = "7"
    live_entries = get_live_bargains_for_ledger(world)
    assert live_entries[0]["created_turn"] == 7

    live["status"] = "fulfilled"
    live["ended_turn"] = "9"
    all_entries = get_all_bargains_for_ledger(world)
    completed = [e for e in all_entries if e["status"] == "fulfilled"]
    assert completed[0]["created_turn"] == 7
