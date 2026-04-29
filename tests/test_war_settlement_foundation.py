"""Foundation tests for Imperial Settlement / Ally Participation scaffolding."""

from backend.models.dialogue_manager import DialogueManager
from backend.models.region import NATION_CAPITALS
from backend.models.world_state import WorldState


def test_settlement_home_capital_alias_uses_configured_mapped_capital():
    world = WorldState()

    assert world.get_settlement_home_capital("Britain") == NATION_CAPITALS["Britain"]
    assert world.get_settlement_home_capital("Britain") == "Netherlands"
    assert world.get_settlement_home_capital("Unconfigured Nation") is None


def test_settlement_home_capital_requires_region_in_current_world(monkeypatch):
    world = WorldState()

    monkeypatch.setitem(NATION_CAPITALS, "Fixture Nation", "Imaginary Capital")
    assert world.get_settlement_home_capital("Fixture Nation") is None

    world.regions.pop(NATION_CAPITALS["Britain"], None)
    assert world.get_settlement_home_capital("Britain") is None


def test_incoming_settlement_offer_has_mailbox_metadata():
    assert "incoming_settlement_offer" in DialogueManager.CURRENT_TURN_OFFER_TYPES
    assert DialogueManager.DIALOGUE_PRIORITY["incoming_settlement_offer"] == 3
    assert (
        DialogueManager.MAILBOX_SUMMARY_LABELS["incoming_settlement_offer"]
        == "Incoming settlement offer"
    )
