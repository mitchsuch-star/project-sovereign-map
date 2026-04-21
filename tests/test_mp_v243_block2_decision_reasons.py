from backend.display_names import diplomatic_decision_reason_display
from backend.game_logic.diplomacy import (
    determine_ai_offer_decision_reason,
    determine_counterparty_decision_reason,
)
from backend.game_logic.mailbox_payloads import build_pending_envoy_popup_from_terms
from backend.models.world_state import WorldState


def _make_world() -> WorldState:
    world = WorldState(player_nation="France")
    world.enemy_nations = []
    return world


def test_ai_offer_reason_uses_hegemony_pressure_when_threat_or_wars_are_high():
    world = _make_world()
    world.threat_level = 65

    assert determine_ai_offer_decision_reason("Britain", "alliance", world) == "hegemony_pressure"


def test_ai_offer_reason_uses_unknown_baseline_when_no_pressure_is_detected():
    world = _make_world()
    world.threat_level = 0

    assert determine_ai_offer_decision_reason("Prussia", "alliance", world) == "unknown_baseline"


def test_counterparty_reason_uses_hegemony_pressure_as_the_default_branch():
    world = _make_world()
    proposal = {
        "proposer_nation": "France",
        "target_nation": "Austria",
        "type": "alliance",
    }

    assert determine_counterparty_decision_reason(proposal, world, acceptance_result={"components": {}}) == "hegemony_pressure"


def test_decision_reason_display_keeps_legacy_rival_pressure_as_alias():
    assert diplomatic_decision_reason_display("hegemony_pressure") == "hegemony pressure"
    assert diplomatic_decision_reason_display("unknown_baseline") == "unknown baseline"
    assert diplomatic_decision_reason_display("rival_pressure") == "hegemony pressure"
    assert diplomatic_decision_reason_display("concern_pressure") == "hegemony pressure"


def test_pending_envoy_popup_displays_legacy_rival_pressure_with_canonical_label():
    popup = build_pending_envoy_popup_from_terms(
        _make_world(),
        nation="Prussia",
        terms={"type": "peace", "demands": [], "sweeteners": [], "clauses": []},
        decision_reason="rival_pressure",
    )

    assert popup["decision_reason"] == "rival_pressure"
    assert popup["decision_reason_display"] == "hegemony pressure"
