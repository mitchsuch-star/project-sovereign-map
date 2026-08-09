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


@pytest.fixture(autouse=True)
def _no_mood_variance(monkeypatch):
    """CA9 row 2 made the muster gate cautious-only, so this file's fixture
    marshal is cautious — and `apply_mood_variance` promotes his MILD odds
    concern to a blocking MODERATE 10% of the time, meaning he objects and
    the gate this file needs raised never arms. The function's own docstring
    prescribes mocking it; the promotion is pinned as real behaviour in
    test_ca9_row2_muster_gate_scope.py::TestMoodVarianceCanPreEmptTheGate.
    """
    monkeypatch.setattr("backend.commands.executor.apply_mood_variance",
                        lambda concern: concern)


def _bad_odds_world():
    # CA9 row 2 (Aug 9 2026): the muster gate now arms only for an
    # `unfavorable` band AND a *cautious* marshal, so this fixture's
    # attacker changed from Ney (aggressive) to Davout — otherwise
    # `_raise_muster_gate` below has no gate to raise and every test in
    # this file would be testing nothing. The keyword-routing behaviour
    # under test is unchanged and personality-independent.
    # 30k (not 20k) vs 50k: at 2.5:1 a cautious marshal objects first and
    # the muster gate never arms. 1.67:1 is `unfavorable` with only MILD
    # concern, which is the band the gate actually owns.
    davout = MarshalFactory.infantry(name="Davout", location="Belgium",
                                     strength=30000, personality="cautious")
    mack = MarshalFactory.enemy(name="Mack", location="Belgium",
                                nation="Austria", strength=50000,
                                personality="cautious")
    world = WorldFactory.with_marshals([davout, mack])
    _war(world)
    # A cautious marshal objects on poor intel alone, and that objection
    # pre-empts the muster gate this file needs raised.
    world.calculate_visibility()
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
         "command": {"marshal": "Davout", "action": "attack", "target": "Mack"}},
        main_module.game_state)
    davout = main_module.world.get_marshal("Davout")
    assert result.get("requires_input") is True
    assert davout.pending_interrupt is not None
    assert "attack_anyway" in davout.pending_interrupt.get("options", [])
    assert "continue_order" not in davout.pending_interrupt.get("options", [])
    return davout


def test_press_on_resolves_attack_anyway(endpoint):
    client, m = endpoint
    _raise_muster_gate(m)
    mack_before = m.world.get_marshal("Mack").strength
    data = client.post("/command", json={"command": "press on"}).json()
    assert data.get("success") is True
    assert m.world.get_marshal("Davout").pending_interrupt is None
    assert m.world.get_marshal("Mack").strength < mack_before


def test_continue_resolves_attack_anyway(endpoint):
    client, m = endpoint
    _raise_muster_gate(m)
    data = client.post("/command", json={"command": "continue"}).json()
    assert data.get("success") is True
    assert m.world.get_marshal("Davout").pending_interrupt is None


def test_continue_order_still_preferred_when_offered(endpoint):
    """FALSIFIABLE NEGATIVE: when an interrupt DOES offer continue_order,
    the continue-family must keep resolving to it, not to attack_anyway."""
    client, m = endpoint
    davout = m.world.get_marshal("Davout")
    # A synthetic march interrupt of the kind that offers both choices.
    davout.pending_interrupt = {
        "marshal": "Davout", "interrupt_type": "enemy_spotted",
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
    assert m.world.get_marshal("Davout").pending_interrupt is None
    assert m.world.get_marshal("Mack").strength == mack_before
