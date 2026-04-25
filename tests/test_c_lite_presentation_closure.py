from pathlib import Path

import pytest

from backend.game_logic.commitments_routing import (
    commitments_notice_details,
    commitments_route,
    format_commitments_notice,
)
from backend.game_logic.diplomacy import (
    _emit_hard_reject_posture_triggered,
    emit_call_to_arms_honored_costly,
    emit_call_to_arms_refused_defensive,
)
from backend.game_logic.diplomatic_templates import (
    TALLEYRAND_COMMENTARY,
    resolve_named_diplomat,
)
from backend.models.world_state import WorldState


def _world() -> WorldState:
    world = WorldState()
    world.enemy_nations = ["Austria", "Prussia", "Britain", "Saxony", "Russia"]
    world.diplomatic_states = {}
    world.active_treaties = {}
    world.pending_dispatch_events = []
    world.event_log = []
    return world


@pytest.mark.parametrize(
    ("nation", "expected"),
    [
        ("France", "Talleyrand"),
        ("Britain", "Castlereagh"),
        ("Prussia", "Hardenberg"),
        ("Austria", "Metternich"),
        ("Saxony", "Einsiedel"),
    ],
)
def test_resolve_named_diplomat_uses_active_cast(nation, expected):
    assert resolve_named_diplomat("envoy", nation, _world()) == expected


def test_resolve_named_diplomat_uses_chancery_when_world_lacks_envoy():
    world = _world()
    world.diplomats.pop("Britain", None)

    assert (
        resolve_named_diplomat("envoy", "Britain", world)
        == "The Chancery of Britain"
    )
    assert (
        resolve_named_diplomat("foreign_office", "Austria", world)
        == "The Chancery of Austria"
    )
    assert resolve_named_diplomat("system", "Austria", world) == ""


def test_commitments_routes_cover_live_presentation_rows():
    rows = {
        "commitment_paradox": {},
        "balance_of_europe_shifted": {"band": 2},
        "amends_offered": {},
        "hard_reject_posture_triggered": {},
        "hard_reject_posture_cleared": {},
        "diplomatic_treaty_broken": {"end_reason_family": "french_breach"},
        "commitment_paradox_resolved": {},
        "witness_strike_recorded": {},
        "call_to_arms_refused_offensive": {},
        "call_to_arms_refused_defensive": {},
        "call_to_arms_honored_costly": {},
    }

    for event_type, payload in rows.items():
        details = commitments_notice_details(event_type, payload)
        assert details["template_key"].startswith("commitments_notice_")
        assert details["icon"].startswith("icon_")
        assert details["label"]
        assert "speaker" in details

    french_breach = commitments_route(
        "diplomatic_treaty_broken",
        {"end_reason_family": "french_breach"},
    )
    assert french_breach["priority"] == "CRITICAL"
    assert french_breach["template"] == "commitments_notice_breach_french"


def test_hard_reject_transition_emits_routed_notification():
    world = _world()

    _emit_hard_reject_posture_triggered(
        world,
        perpetrator="France",
        victim="Austria",
        episode_id="episode_1",
    )

    notice = next(
        n for n in world.notifications.get_pending()
        if n.get("type") == "hard_reject_posture_triggered"
    )
    assert int(notice["priority"]) == 2
    assert notice["title"] == "The Chancery Shut"
    assert notice["details"]["template_key"] == (
        "commitments_notice_hard_reject_triggered"
    )
    assert notice["details"]["review_target"] == "ledger_commitments"


def test_dg4_cascade_profile_overrides_severity_and_roundtrips():
    world = _world()
    world.cascade_profile["defensive_refusal_severity_multiplier"] = 2.0
    world.cascade_profile["anti_renewal_window_turns"] = 7

    result = emit_call_to_arms_refused_defensive(
        world,
        breaker="Russia",
        victim="Austria",
    )

    assert result["reliability_delta"] == -20
    assert result["anti_renewal_cooldown_turns"] == 7
    assert (
        result["severity_factors"]["defensive_refusal_severity_multiplier"]
        == 2.0
    )

    restored = WorldState.from_dict(world.to_dict())
    assert restored.cascade_profile["anti_renewal_window_turns"] == 7
    assert (
        restored.cascade_profile["defensive_refusal_severity_multiplier"]
        == 2.0
    )


def test_costly_honor_notice_uses_france_chancery_target():
    world = _world()

    emit_call_to_arms_honored_costly(
        world,
        honorer="Prussia",
        victim="Austria",
    )

    event = next(
        e for e in world.event_log
        if e.get("type") == "call_to_arms_honored_costly"
    )
    assert event["speaker_attribution"] == "foreign_office"
    assert event["speaker_target_nation"] == "France"
    notice = next(
        n for n in world.notifications.get_pending()
        if n.get("type") == "call_to_arms_honored_costly"
    )
    assert notice["details"]["speaker"] == "foreign_office_chancery_france"
    assert "Chancery of France" in notice["message"]


def test_british_generic_commentary_no_longer_hardcodes_castlereagh():
    for (nation, _reason), text in TALLEYRAND_COMMENTARY.items():
        if nation == "Britain":
            assert "Castlereagh" not in text


def test_commitments_notice_copy_for_paradox_resolution_is_not_dispatch_only():
    text = format_commitments_notice(
        "commitment_paradox_resolved",
        {
            "player_nation": "France",
            "chosen_nation": "Austria",
            "spurned_nation": "Prussia",
            "reliability_before": 0,
            "reliability_after": -10,
        },
    )

    assert "Austria" in text
    assert "Prussia" in text
    assert "0 -> -10" in text


def test_godot_sources_wire_review_target_and_commitments_antispam():
    root = Path(__file__).resolve().parents[1]
    notification_bar = (
        root / "godot-client" / "project-sovereign" / "scripts"
        / "notification_bar.gd"
    ).read_text(encoding="utf-8")
    diplomatic_ledger = (
        root / "godot-client" / "project-sovereign" / "scripts"
        / "diplomatic_ledger.gd"
    ).read_text(encoding="utf-8")
    main = (
        root / "godot-client" / "project-sovereign" / "scripts" / "main.gd"
    ).read_text(encoding="utf-8")
    top_bar = (
        root / "godot-client" / "project-sovereign" / "scripts" / "top_bar.gd"
    ).read_text(encoding="utf-8")
    incoming_popup = (
        root / "godot-client" / "project-sovereign" / "scripts"
        / "incoming_proposal_popup.gd"
    ).read_text(encoding="utf-8")
    paradox_popup = (
        root / "godot-client" / "project-sovereign" / "scripts"
        / "commitment_paradox_popup.gd"
    ).read_text(encoding="utf-8")

    assert "MAX_VISIBLE_COMMITMENTS_PER_TURN := 2" in notification_bar
    assert "_visible_notifications_for_rail" in notification_bar
    assert '"hard_reject_posture_triggered": "HRT"' in notification_bar
    assert "open_to_commitments" in diplomatic_ledger
    assert "current_tab = tab_index" in diplomatic_ledger
    assert "open_diplomatic_ledger_review" in main
    assert "open_diplomatic_ledger_review" in top_bar
    assert 'decision_reason != "" and decision_reason_display == ""' in incoming_popup
    assert "_show_after_choice_aside" in paradox_popup
    assert "attacker_diplomat" in paradox_popup
    assert "defender_diplomat" in paradox_popup
