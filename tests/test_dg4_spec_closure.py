from pathlib import Path

from backend.campaign_log import format_event_oneliner
from backend.game_logic.coalition import _calculate_defensive_refusal_memory_threat
from backend.game_logic.diplomacy import (
    declare_war,
    emit_call_to_arms_refused_defensive,
    set_diplomatic_state,
)
from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
from backend.game_logic.dispatch import (
    _build_diplomatic_events_section,
    queue_dispatch_event,
)
from backend.models.world_state import WorldState


def _isolated_world() -> WorldState:
    world = WorldState()
    world.enemy_nations = ["Austria", "Prussia", "Britain", "Saxony", "Russia"]
    world.diplomatic_states = {}
    world.active_treaties = {}
    world.vassals = {}
    world.pending_dispatch_events = []
    world.event_log = []
    return world


def test_dg4_war_cascade_is_direct_only_no_transitive_allies():
    world = _isolated_world()
    set_diplomatic_state(world, "Austria", "Prussia", "ALLIANCE", "setup")
    set_diplomatic_state(world, "Prussia", "Britain", "ALLIANCE", "setup")

    result = declare_war(world, "France", "Austria")

    assert result["success"] is True
    assert world.get_diplomatic_state("Prussia", "France") == "WAR"
    assert world.get_diplomatic_state("Britain", "France") == "PEACE"
    assert "Britain" not in {
        entry["nation"] for entry in result["war_entry_ledger"]
    }


def test_dg4_direct_defender_vassal_auto_joins_and_records_ledger():
    world = _isolated_world()
    world.vassals = {"Saxony": {"lord": "Austria", "loyalty": 60, "autonomy": 1}}

    result = declare_war(world, "France", "Austria")

    assert result["success"] is True
    assert world.get_diplomatic_state("Saxony", "France") == "WAR"
    entry = next(
        ledger for ledger in result["war_entry_ledger"]
        if ledger["nation"] == "Saxony"
    )
    assert entry["path"] == "honored"
    assert entry["side"] == "defender_vassal"
    assert entry["treaty_state"] == "VASSAL"


def test_dg4_defensive_refusal_notification_uses_routing_contract():
    world = _isolated_world()

    result = emit_call_to_arms_refused_defensive(
        world, breaker="Russia", victim="Austria",
    )

    notice = next(
        n for n in world.notifications.get_pending()
        if n["type"] == "call_to_arms_refused_defensive"
    )
    assert notice["priority"] == 2
    assert notice["title"] == "Ally Abandoned"
    assert notice["details"]["template_key"] == (
        "commitments_notice_call_refused_defensive"
    )
    assert notice["details"]["review_target"] == "ledger_commitments"
    assert notice["details"]["speaker"] == "envoy_to_victim_diplomat"
    event = next(
        e for e in world.event_log
        if e.get("episode_id") == result["episode_id"]
    )
    assert event["speaker_attribution"] == "envoy"
    assert event["speaker_target_nation"] == "Austria"


def test_defensive_refusal_coalition_threat_uses_refusal_moment_snapshot():
    world = _isolated_world()
    set_diplomatic_state(world, "France", "Austria", "ALLIANCE", "setup")
    set_diplomatic_state(world, "Prussia", "Austria", "NON_AGGRESSION", "setup")

    emit_call_to_arms_refused_defensive(
        world, breaker="France", victim="Austria",
    )
    set_diplomatic_state(world, "Prussia", "Austria", "PEACE", "after_refusal")

    assert _calculate_defensive_refusal_memory_threat(world) == 1


def test_defensive_refusal_coalition_threat_does_not_add_late_partners():
    world = _isolated_world()
    set_diplomatic_state(world, "France", "Austria", "ALLIANCE", "setup")

    emit_call_to_arms_refused_defensive(
        world, breaker="France", victim="Austria",
    )
    set_diplomatic_state(world, "Prussia", "Austria", "NON_AGGRESSION", "late")

    assert _calculate_defensive_refusal_memory_threat(world) == 0


def test_dg4_routing_snapshot_and_notifications_survive_save_load():
    world = _isolated_world()
    set_diplomatic_state(world, "France", "Austria", "ALLIANCE", "setup")
    set_diplomatic_state(world, "Prussia", "Austria", "NON_AGGRESSION", "setup")
    emit_call_to_arms_refused_defensive(
        world, breaker="France", victim="Austria",
    )

    restored = WorldState.from_dict(world.to_dict())

    refusal = next(
        event for event in restored.event_log
        if event.get("type") == "call_to_arms_refused_defensive"
    )
    assert refusal["coalition_threat_partners_at_refusal"] == ["Prussia"]
    assert "severity_factors" in refusal
    notice = next(
        n for n in restored.notifications.get_pending()
        if n["type"] == "call_to_arms_refused_defensive"
    )
    assert notice["details"]["template_key"] == (
        "commitments_notice_call_refused_defensive"
    )


def test_dg4_severity_includes_power_tier_and_war_exposure_factors():
    world = _isolated_world()

    result = emit_call_to_arms_refused_defensive(
        world,
        breaker="Russia",
        victim="Austria",
        call_context={
            "enemy": "France",
            "aggressor_power_ratio": 2.0,
            "capital_threat": True,
        },
    )

    assert result["reliability_delta"] < -18
    assert result["severity_factors"]["power_tier_multiplier"] == 1.15
    assert result["severity_factors"]["war_exposure_multiplier"] > 1.0


def test_dispatch_collapses_same_episode_witness_strikes():
    world = _isolated_world()
    for witness in ("Prussia", "Britain", "Saxony"):
        queue_dispatch_event(
            world,
            "witness_strike_recorded",
            {
                "episode_id": "call_1",
                "victim_nation": "Austria",
                "perpetrator_nation": "Russia",
                "witness_nation": witness,
                "scope_reason": "ally",
            },
            "always",
        )

    events = _build_diplomatic_events_section(world, world.player_nation)

    witness_rows = [
        event for event in events
        if event["type"] == "witness_strike_recorded"
    ]
    assert len(witness_rows) == 1
    assert witness_rows[0]["witness_count"] == 3
    assert "3 courts" in witness_rows[0]["text"]


def test_balance_of_europe_payload_and_campaign_log_route_are_live():
    world = _isolated_world()
    set_diplomatic_state(world, "France", "Austria", "ALLIANCE", "setup")

    ledger = build_diplomatic_ledger(world)

    assert "balance_of_europe" in ledger
    assert "threat_coalition" in ledger
    balance = ledger["balance_of_europe"]
    assert isinstance(balance.get("bloc_members"), list)
    assert isinstance(balance.get("hegemon_power"), int)
    assert isinstance(balance.get("total_power"), int)
    assert "all active European courts" in balance.get("power_basis", "")
    assert balance["headline_case"] in {
        "NO_HEGEMON",
        "HEGEMON_NO_COALITION",
        "BREWING",
        "ACTIVE_COALITION",
        "COOLDOWN",
    }

    line = format_event_oneliner({
        "type": "balance_of_europe_shifted",
        "label": "French System",
        "share": 0.52,
        "counterplay_hint": "Break the alignment.",
    })
    assert "French System" in line


def test_godot_notification_and_ledger_sources_expose_commitments_hooks():
    root = Path(__file__).resolve().parents[1]
    notification_bar = (
        root / "godot-client" / "project-sovereign" / "scripts"
        / "notification_bar.gd"
    ).read_text(encoding="utf-8")
    diplomatic_ledger = (
        root / "godot-client" / "project-sovereign" / "scripts"
        / "diplomatic_ledger.gd"
    ).read_text(encoding="utf-8")

    assert '"call_to_arms_refused_defensive": "ALY"' in notification_bar
    assert "notification_review_requested" in notification_bar
    assert 'cached_data.get("balance_of_europe", {})' in diplomatic_ledger
    assert "BALANCE OF EUROPE" in diplomatic_ledger
    assert "active European bloc power" in diplomatic_ledger
    assert "Alliance networks can overlap" in diplomatic_ledger
    assert "Warning bands: 33% noticed, 50% alarming, 60% crisis" in diplomatic_ledger
