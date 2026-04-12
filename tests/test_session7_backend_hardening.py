from pathlib import Path
from unittest.mock import MagicMock

import pytest

from backend.ai.enemy_ai import EnemyAI
from backend.game_logic.dispatch import build_morning_dispatch
from backend.game_logic.diplomatic_dialogue import generate_feasibility_dialogue
from backend.game_logic.diplomatic_templates import generate_suggested_terms
from backend.modding.validator import validate_scenario
from backend.nation_config import validate_scenario_runtime_support
from backend.models.world_state import WorldState


def test_non_france_world_defaults_shift_enemy_roster_and_ai_budgets():
    world = WorldState(player_nation="Prussia")

    assert world.player_nation == "Prussia"
    assert set(world.enemy_nations) == {"France", "Britain", "Austria", "Saxony"}
    assert "Prussia" not in world.enemy_nations
    assert set(world.nation_actions) == {"France", "Britain", "Austria", "Saxony"}
    assert world.nation_actions["France"] == 4
    assert "Prussia" not in world.nation_actions
    assert set(world.nation_authority) == {"France", "Britain", "Austria", "Saxony"}


def test_dispatch_uses_player_nation_marshals_for_non_france_campaign():
    world = WorldState(player_nation="Prussia")

    dispatch = build_morning_dispatch(world)
    marshal_names = {entry["name"] for entry in dispatch["marshals"]}
    player_marshal_names = {
        marshal.name for marshal in world.marshals.values() if marshal.nation == "Prussia"
    }
    non_player_marshal_names = {
        marshal.name for marshal in world.marshals.values() if marshal.nation != "Prussia"
    }

    assert marshal_names == player_marshal_names
    assert marshal_names.isdisjoint(non_player_marshal_names)


def test_feasibility_dialogue_uses_player_nation_context():
    world = WorldState(player_nation="Prussia")
    prussia_key = world._make_diplo_key("Prussia", "Austria")
    france_key = world._make_diplo_key("France", "Austria")
    world.nation_relations[prussia_key] = 35
    world.nation_relations[france_key] = -60

    dialogue = generate_feasibility_dialogue(
        {"target_nation": "Austria", "proposal_type": "open_borders"},
        world,
    )

    assert dialogue["context"]["relation"] == 35


def test_suggested_terms_stamp_dynamic_proposer_nation():
    world = WorldState(player_nation="Prussia")

    terms = generate_suggested_terms("Austria", "peace", world)

    assert terms["proposer_nation"] == "Prussia"


def test_enemy_ai_player_contacts_use_visible_enemy_cache():
    world = WorldState(player_nation="France")
    ai = EnemyAI(executor=None)
    visible_enemy = next(marshal for marshal in world.marshals.values() if marshal.nation != "France")

    world.get_visible_enemies = MagicMock(return_value=[visible_enemy])
    world.get_enemies_of_nation = MagicMock(return_value=[])

    assert ai._get_enemy_contacts("France", world) == [visible_enemy]
    assert ai._get_enemy_contacts("France", world) == [visible_enemy]
    world.get_visible_enemies.assert_called_once_with("France")
    world.get_enemies_of_nation.assert_not_called()


def test_enemy_ai_non_player_contacts_use_omniscient_cache():
    world = WorldState(player_nation="France")
    ai = EnemyAI(executor=None)
    player_marshal = next(marshal for marshal in world.marshals.values() if marshal.nation == "France")

    world.get_visible_enemies = MagicMock(return_value=[])
    world.get_enemies_of_nation = MagicMock(return_value=[player_marshal])

    assert ai._get_enemy_contacts("Britain", world) == [player_marshal]
    assert ai._get_enemy_contacts("Britain", world) == [player_marshal]
    world.get_enemies_of_nation.assert_called_once_with("Britain")
    world.get_visible_enemies.assert_not_called()


def test_runtime_support_validator_accepts_supported_large_scenario():
    world = WorldState(player_nation="Prussia")

    assert validate_scenario_runtime_support(world.to_dict()) == []


def test_runtime_support_validator_rejects_unsupported_custom_nations_example():
    scenario_path = Path("mods/examples/custom_nations_scenario.json")

    validation = validate_scenario(str(scenario_path))

    assert validation.is_valid is False
    runtime_messages = [error.message for error in validation.errors if error.path == "runtime_support"]
    assert any("Venice: missing capital mapping" in message for message in runtime_messages)
    assert any("Milan: missing diplomat config" in message for message in runtime_messages)

    with pytest.raises(ValueError, match="Invalid scenario"):
        WorldState.from_scenario(str(scenario_path))
