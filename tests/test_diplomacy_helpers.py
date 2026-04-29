from backend.game_logic.diplomacy import get_relation
from backend.models.world_state import WorldState


def test_get_relation_reads_unordered_pair_key():
    world = WorldState()
    key = world._make_diplo_key("France", "Prussia")
    world.nation_relations[key] = -42

    assert get_relation(world, "France", "Prussia") == -42
    assert get_relation(world, "Prussia", "France") == -42


def test_get_relation_self_and_missing_values_are_stable():
    world = WorldState()

    assert get_relation(world, "France", "France") == 100
    assert get_relation(world, "France", "Atlantis") == 0
    assert get_relation(world, "", "France") == 0
