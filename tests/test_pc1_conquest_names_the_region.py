"""PC-1 — a province falls and the game announces a MARSHAL was captured.
(quiet-France played campaign, August 3 2026.)

`_execute_attack` builds its battle event with
`"region_name": resolved_target if conquered else None`. But `resolved_target`
is only ever reassigned to a region name inside the fuzzy-region branch. When
the target is a marshal, the `enemy_by_name` branch sets
`target_location = enemy_by_name.location` and leaves `resolved_target`
holding the *man's* name — and the enemy AI targets marshals by name at every
attack rung (`enemy_ai.py:2396` and siblings).

Both clients treat the key as a place:

    enemy_phase_dialog.gd:291   var region = event.get("region_name", "territory")
    main.gd:1977-1978           "⚑ " + region_name + " captured! ⚑"

so every AI conquest reported "⚑ Ney captured! ⚑" — which a player reads as
losing a marshal to captivity, not a province changing hands.

Measured in a live 42-turn campaign on the shipped 1805 board: **8 of 8**
conquest events carried a marshal's name —

    region_name='Deroy'      Battle of Munich          (Munich fell)
    region_name='Ney'        Second Battle of Vienna
    region_name='Massena'    Battle of Lyonnais        (Lyonnais fell)
    region_name='Paget'      Battle of Bearn           (Bearn fell)
    region_name='Bernadotte' Seventh Battle of Franconia
    ...

The file already knew: the comment above the capture block reads "Use
target_location (the region) not resolved_target (which might be marshal
name)". IGR-X8 edited this same event dict to attach `capture_choice` and did
not notice the sibling key. Nothing pinned it.
"""
import pytest

from backend.commands.combat_executor import CombatExecutor  # noqa: F401
from backend.commands.executor import CommandExecutor

from tests.conftest import MarshalFactory, WorldFactory


def _battle_events(result):
    """Every battle event in an executor result, wherever it is nested."""
    found = []

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "battle":
                found.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(result)
    return found


@pytest.fixture()
def attack_world():
    ney = MarshalFactory.infantry(name="Ney", location="Paris",
                                  strength=60000, personality="aggressive")
    mack = MarshalFactory.enemy(name="Mack", location="Belgium",
                                nation="Austria", strength=1200,
                                personality="cautious")
    world = WorldFactory.with_marshals([ney, mack])
    key = "|".join(sorted(["France", "Austria"]))
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = world.current_turn
    world.get_region("Belgium").controller = "Austria"
    return world


def _attack(world, target):
    executor = CommandExecutor()
    return executor.execute(
        {"success": True,
         "command": {"marshal": "Ney", "action": "attack", "target": target}},
        {"world": world})


def test_conquest_by_marshal_target_names_the_province(attack_world):
    """Attacking a MARSHAL by name and taking his province must report the
    province. This is the shape the enemy AI always produces."""
    result = _attack(attack_world, "Mack")
    conquests = [e for e in _battle_events(result) if e.get("region_conquered")]
    assert conquests, "the attack did not conquer — fixture no longer exercises the seam"
    for event in conquests:
        assert event["region_name"] == "Belgium", (
            f"conquest reported region_name={event['region_name']!r}; the client "
            f"renders that as '⚑ {event['region_name']} captured! ⚑'")


def test_conquest_by_region_target_still_names_the_province(attack_world):
    """Counter-example: the region-named path was already correct and must
    stay correct — the fix must not swap one wrong noun for another."""
    result = _attack(attack_world, "Belgium")
    conquests = [e for e in _battle_events(result) if e.get("region_conquered")]
    assert conquests, "the attack did not conquer — fixture no longer exercises the seam"
    for event in conquests:
        assert event["region_name"] == "Belgium"


def test_region_name_is_never_a_marshal_name(attack_world):
    """Falsifiable in the general form: whatever the target vocabulary, the
    key must never hold something that resolves to a marshal."""
    result = _attack(attack_world, "Mack")
    marshal_names = set(attack_world.marshals.keys())
    for event in _battle_events(result):
        name = event.get("region_name")
        if name:
            assert name not in marshal_names, (
                f"region_name={name!r} is a marshal, not a province")
            assert attack_world.get_region(name) is not None, (
                f"region_name={name!r} does not resolve to a region")


def test_no_conquest_leaves_region_name_none(attack_world):
    """The `else None` half is unchanged: a battle that takes nothing must
    not name a province at all."""
    attack_world.get_marshal("Mack").strength = 90000
    attack_world.get_marshal("Ney").strength = 1000
    result = _attack(attack_world, "Mack")
    for event in _battle_events(result):
        if not event.get("region_conquered"):
            assert event.get("region_name") is None
