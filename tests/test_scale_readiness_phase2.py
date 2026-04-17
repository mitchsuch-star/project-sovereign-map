from tests.conftest import MarshalFactory, WorldFactory


def _set_war(world, nation_a, nation_b):
    key = "|".join(sorted([nation_a, nation_b]))
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = world.current_turn


def _find_border_region(world, nation):
    for region_name, region in world.regions.items():
        if region.controller != nation:
            continue
        for adjacent_name in region.adjacent_regions:
            adjacent_region = world.get_region(adjacent_name)
            if adjacent_region and adjacent_region.controller != nation:
                return region_name, adjacent_name
    raise AssertionError(f"No border region found for {nation}")


def test_get_distance_uses_symmetric_cache():
    world = WorldFactory.basic()

    distance = world.get_distance("Paris", "Belgium")
    cache_key = tuple(sorted(("Paris", "Belgium")))

    assert distance == world.get_distance("Belgium", "Paris")
    assert len(world._distance_cache) == 1
    assert cache_key in world._distance_cache


def test_distance_cache_requires_explicit_invalidation_for_topology_change():
    world = WorldFactory.basic()
    start = "Paris"
    neighbor = world.get_region(start).adjacent_regions[0]

    assert world.get_distance(start, neighbor) == 1

    world.regions[start].controller = "Prussia"
    assert world.get_distance(start, neighbor) == 1

    world.get_region(start).adjacent_regions.remove(neighbor)
    world.get_region(neighbor).adjacent_regions.remove(start)

    assert world.get_distance(start, neighbor) == 1

    world.invalidate_distance_cache()

    assert world.get_distance(start, neighbor) != 1


def test_live_visible_enemies_use_adjacency_for_ai_nations():
    world = WorldFactory.basic(player_nation="France")
    own_region, visible_enemy_region = _find_border_region(world, "Prussia")
    scout = MarshalFactory.enemy(name="Blue Scout", nation="Prussia", location=own_region)

    temp_world = WorldFactory.with_marshals([scout], player_nation="France")
    temp_world.regions = world.regions
    visible_regions = temp_world.get_live_visible_regions_for_nation("Prussia")
    hidden_enemy_region = next(
        region_name for region_name in temp_world.regions
        if region_name not in visible_regions
    )

    visible_enemy = MarshalFactory.enemy(
        name="Visible Austrian",
        nation="Austria",
        location=visible_enemy_region,
    )
    hidden_enemy = MarshalFactory.enemy(
        name="Hidden Austrian",
        nation="Austria",
        location=hidden_enemy_region,
    )
    world = WorldFactory.with_marshals(
        [scout, visible_enemy, hidden_enemy],
        player_nation="France",
    )
    _set_war(world, "Prussia", "Austria")

    visible_names = {marshal.name for marshal in world.get_live_visible_enemies("Prussia")}

    assert "Visible Austrian" in visible_names
    assert "Hidden Austrian" not in visible_names


def test_watchtower_expands_live_visibility_without_friendly_marshal_presence():
    world = WorldFactory.with_marshals([], player_nation="France")
    own_region, watched_region = _find_border_region(world, "Prussia")
    enemy = MarshalFactory.enemy(name="Watchtower Target", nation="Austria", location=watched_region)
    world.marshals = {enemy.name: enemy}
    _set_war(world, "Prussia", "Austria")

    assert watched_region not in world.get_live_visible_regions_for_nation("Prussia")

    world.get_region(own_region).watchtower = "active"

    visible_names = {marshal.name for marshal in world.get_live_visible_enemies("Prussia")}

    assert watched_region in world.get_live_visible_regions_for_nation("Prussia")
    assert "Watchtower Target" in visible_names
