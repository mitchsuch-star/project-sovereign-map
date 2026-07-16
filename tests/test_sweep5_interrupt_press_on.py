"""Sweep-5 live finding #2 (Combat Overhaul, Parsing/UX sweep, July 16 2026).

A `contact_bad_odds` / `muster_confirm` interrupt offers `attack_anyway` but
not `continue_order`, so a natural typed "press on" / "continue" fell through
main.py's interrupt keyword map to a fresh (bewildered) LLM parse. When the
order can only continue THROUGH the enemy, pressing on IS attacking anyway —
the continue-family keywords now fall back to `attack_anyway` when
`continue_order` is absent.
"""
import pytest
from fastapi.testclient import TestClient

from backend.commands.executor import CommandExecutor
from backend.commands.parser import CommandParser

from tests.conftest import MarshalFactory, WorldFactory


def _war(world, a="France", b="Austria"):
    key = "|".join(sorted([a, b]))
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = world.current_turn


def _bad_odds_world():
    ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                  strength=20000, personality="aggressive")
    mack = MarshalFactory.enemy(name="Mack", location="Belgium",
                                nation="Austria", strength=50000,
                                personality="cautious")
    world = WorldFactory.with_marshals([ney, mack])
    _war(world)
    return world


@pytest.fixture()
def endpoint():
    import backend.main as main_module

    original_parser = main_module.parser
    original_world = main_module.world
    original_game_state = main_module.game_state
    original_executor = main_module.executor
    main_module.parser = CommandParser(use_real_llm=False)
    main_module.world = _bad_odds_world()
    main_module.game_state = {"world": main_module.world}
    main_module.executor = CommandExecutor()
    try:
        yield TestClient(main_module.app), main_module
    finally:
        main_module.parser = original_parser
        main_module.world = original_world
        main_module.game_state = original_game_state
        main_module.executor = original_executor


def _raise_muster_gate(main_module):
    """Store the real muster_confirm interrupt via the production attack path."""
    result = main_module.executor.execute(
        {"success": True,
         "command": {"marshal": "Ney", "action": "attack", "target": "Mack"}},
        main_module.game_state)
    ney = main_module.world.get_marshal("Ney")
    assert result.get("requires_input") is True
    assert ney.pending_interrupt is not None
    assert "attack_anyway" in ney.pending_interrupt.get("options", [])
    assert "continue_order" not in ney.pending_interrupt.get("options", [])
    return ney


def test_press_on_resolves_attack_anyway(endpoint):
    client, m = endpoint
    _raise_muster_gate(m)
    mack_before = m.world.get_marshal("Mack").strength
    data = client.post("/command", json={"command": "press on"}).json()
    assert data.get("success") is True
    assert m.world.get_marshal("Ney").pending_interrupt is None
    assert m.world.get_marshal("Mack").strength < mack_before


def test_continue_resolves_attack_anyway(endpoint):
    client, m = endpoint
    _raise_muster_gate(m)
    data = client.post("/command", json={"command": "continue"}).json()
    assert data.get("success") is True
    assert m.world.get_marshal("Ney").pending_interrupt is None


def test_continue_order_still_preferred_when_offered(endpoint):
    """FALSIFIABLE NEGATIVE: when an interrupt DOES offer continue_order,
    the continue-family must keep resolving to it, not to attack_anyway."""
    client, m = endpoint
    ney = m.world.get_marshal("Ney")
    # A synthetic march interrupt of the kind that offers both choices.
    ney.pending_interrupt = {
        "marshal": "Ney", "interrupt_type": "enemy_spotted",
        "enemy": "Mack", "location": "Belgium",
        "options": ["continue_order", "hold_position", "cancel_order"],
    }
    from backend.commands.strategic import StrategicOrderProcessor
    calls = {}
    original = StrategicOrderProcessor.handle_response

    def spy(self, marshal_name, interrupt_type, choice, world, game_state):
        calls["choice"] = choice
        return {"success": True, "message": "ok"}

    StrategicOrderProcessor.handle_response = spy
    try:
        client.post("/command", json={"command": "keep going"})
    finally:
        StrategicOrderProcessor.handle_response = original
    assert calls.get("choice") == "continue_order"


def test_cancel_still_routes_to_cancel(endpoint):
    client, m = endpoint
    _raise_muster_gate(m)
    mack_before = m.world.get_marshal("Mack").strength
    client.post("/command", json={"command": "belay that"})
    assert m.world.get_marshal("Ney").pending_interrupt is None
    assert m.world.get_marshal("Mack").strength == mack_before
