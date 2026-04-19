import pytest

from tests.conftest import MarshalFactory, WorldFactory
from backend.ai.enemy_ai import EnemyAI, get_marshal_priority
from backend.commands.executor import CommandExecutor


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


def test_live_visibility_cache_rebuilds_after_marshal_index_refresh():
    world = WorldFactory.basic(player_nation="France")
    own_region, visible_enemy_region = _find_border_region(world, "Prussia")
    scout = MarshalFactory.enemy(name="Blue Scout", nation="Prussia", location=own_region)

    temp_world = WorldFactory.with_marshals([scout], player_nation="France")
    temp_world.regions = world.regions
    initial_visible_regions = temp_world.get_live_visible_regions_for_nation("Prussia")
    hidden_enemy_region = next(
        region_name for region_name in temp_world.regions
        if region_name not in initial_visible_regions
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

    assert not world.get_live_visible_enemies_in_region(hidden_enemy_region, "Prussia")

    scout.location = hidden_enemy_region
    world.refresh_marshal_indexes()

    visible_names = {
        marshal.name for marshal in world.get_live_visible_enemies_in_region(hidden_enemy_region, "Prussia")
    }

    assert "Hidden Austrian" in visible_names


def test_ai_artillery_helpers_refresh_indexes_for_direct_calls():
    artillery = MarshalFactory.artillery(name="Drouot", location="Paris", nation="France")
    screen = MarshalFactory.infantry(name="Soult", location="Paris", nation="France")
    enemy_cavalry = MarshalFactory.cavalry(
        name="Uxbridge",
        location="Belgium",
        nation="Prussia",
    )
    world = WorldFactory.with_marshals(
        [artillery, screen, enemy_cavalry],
        player_nation="France",
    )
    _set_war(world, "France", "Prussia")
    world._marshals_by_region = {}

    ai = EnemyAI(CommandExecutor())

    assert ai._artillery_has_screen(artillery, "France", world) is True
    assert ai._enemy_cavalry_within_range(artillery, "France", world, max_range=1) is True


def test_ai_target_ratio_refreshes_indexes_for_direct_calls():
    target = MarshalFactory.infantry(name="Davout", location="Belgium", nation="Prussia")
    overwatch = MarshalFactory.artillery(name="Drouot", location="Belgium", nation="Prussia")
    world = WorldFactory.with_marshals(
        [target, overwatch],
        player_nation="France",
    )
    _set_war(world, "France", "Prussia")
    world._marshals_by_region = {}

    ai = EnemyAI(CommandExecutor())
    effective_ratio = ai._evaluate_target_ratio(1.0, target, world)

    assert effective_ratio == pytest.approx(0.97)


def test_ai_decide_single_action_refreshes_indexes_before_evaluation():
    world = WorldFactory.basic(player_nation="France")
    ai = EnemyAI(CommandExecutor())
    game_state = {"world": world, "debug_mode": True}
    ney = world.get_marshal("Ney")
    starting_location = ney.location
    world._marshals_by_region = {}

    result = ai.decide_single_action(ney, "France", world, game_state)

    assert result is not None
    assert world._marshals_by_region
    assert starting_location in world._marshals_by_region


def test_ai_coordinated_attack_refreshes_indexes_for_direct_calls():
    attacker = MarshalFactory.infantry(
        name="Ney",
        location="Belgium",
        strength=25000,
        nation="Coalition",
        personality="aggressive",
    )
    ally = MarshalFactory.infantry(
        name="Blucher",
        location="Waterloo",
        strength=15000,
        nation="Coalition",
        personality="cautious",
    )
    defender = MarshalFactory.enemy(
        name="Davout",
        location="Rhineland",
        strength=20000,
        nation="France",
    )
    attacker.set_relationship("Blucher", 0)
    world = WorldFactory.with_marshals(
        [attacker, ally, defender],
        player_nation="France",
    )
    _set_war(world, "Coalition", "France")
    world.get_region("Belgium").controller = "Coalition"
    world.get_region("Waterloo").controller = "Coalition"
    world._marshals_by_region = {}

    ai = EnemyAI(CommandExecutor())
    action = ai._find_coordinated_attack(attacker, "Coalition", world)

    assert action is not None
    assert action["action"] == "move"


def test_ai_artillery_position_scoring_refreshes_indexes_for_direct_calls():
    screened_artillery = MarshalFactory.artillery(
        name="Drouot",
        location="Belgium",
        nation="Coalition",
    )
    screen = MarshalFactory.infantry(
        name="Soult",
        location="Belgium",
        nation="Coalition",
    )
    enemy = MarshalFactory.enemy(
        name="Davout",
        location="Rhineland",
        nation="France",
    )
    screened_world = WorldFactory.with_marshals(
        [screened_artillery, screen, enemy],
        player_nation="France",
    )
    _set_war(screened_world, "Coalition", "France")
    screened_world.get_region("Belgium").controller = "Coalition"
    screened_world.get_region("Rhineland").controller = "France"
    screened_world._marshals_by_region = {}

    unscreened_artillery = MarshalFactory.artillery(
        name="Drouot",
        location="Belgium",
        nation="Coalition",
    )
    enemy_copy = MarshalFactory.enemy(
        name="Davout",
        location="Rhineland",
        nation="France",
    )
    unscreened_world = WorldFactory.with_marshals(
        [unscreened_artillery, enemy_copy],
        player_nation="France",
    )
    _set_war(unscreened_world, "Coalition", "France")
    unscreened_world.get_region("Belgium").controller = "Coalition"
    unscreened_world.get_region("Rhineland").controller = "France"
    unscreened_world._marshals_by_region = {}

    ai = EnemyAI(CommandExecutor())
    screened_score = ai._score_artillery_position("Belgium", screened_artillery, "Coalition", screened_world)
    unscreened_score = ai._score_artillery_position("Belgium", unscreened_artillery, "Coalition", unscreened_world)

    assert screened_score > unscreened_score


def test_ai_co_location_guard_refreshes_indexes_for_direct_calls():
    marshal = MarshalFactory.infantry(
        name="Ney",
        location="Belgium",
        strength=30000,
        nation="Coalition",
        personality="aggressive",
    )
    ally = MarshalFactory.infantry(
        name="Blucher",
        location="Belgium",
        strength=25000,
        nation="Coalition",
        personality="cautious",
    )
    enemy = MarshalFactory.enemy(
        name="Davout",
        location="Rhineland",
        strength=40000,
        nation="France",
    )
    marshal.moved_this_turn = False
    world = WorldFactory.with_marshals(
        [marshal, ally, enemy],
        player_nation="France",
    )
    _set_war(world, "Coalition", "France")
    world._marshals_by_region = {}

    ai = EnemyAI(CommandExecutor())

    assert ai._should_maintain_co_location(marshal, "Coalition", world) is True


def test_ai_defensive_reinforcement_refreshes_indexes_for_direct_calls():
    marshal = MarshalFactory.infantry(
        name="Ney",
        location="Paris",
        strength=30000,
        nation="Coalition",
        personality="aggressive",
    )
    ally = MarshalFactory.infantry(
        name="Blucher",
        location="Rhineland",
        strength=20000,
        nation="Coalition",
        personality="cautious",
    )
    enemy = MarshalFactory.enemy(
        name="Wellington",
        location="Bavaria",
        strength=30000,
        nation="France",
    )
    marshal.set_relationship("Blucher", 0)
    world = WorldFactory.with_marshals(
        [marshal, ally, enemy],
        player_nation="France",
    )
    _set_war(world, "Coalition", "France")
    world.get_region("Paris").controller = "Coalition"
    world.get_region("Belgium").controller = "Coalition"
    world.get_region("Lyon").controller = "Coalition"
    world.get_region("Rhineland").controller = "Coalition"
    world._marshals_by_region = {}

    ai = EnemyAI(CommandExecutor())
    action = ai._find_defensive_reinforcement_position(marshal, "Coalition", world)

    assert action is not None
    assert action["action"] == "move"
    assert action["target"] in ("Belgium", "Lyon")


def test_ai_ally_support_refreshes_indexes_for_direct_calls():
    supporter = MarshalFactory.infantry(
        name="Ney",
        location="Lyon",
        strength=30000,
        nation="Coalition",
        personality="aggressive",
    )
    ally = MarshalFactory.infantry(
        name="Blucher",
        location="Paris",
        strength=10000,
        nation="Coalition",
        personality="cautious",
    )
    enemy = MarshalFactory.enemy(
        name="Davout",
        location="Paris",
        strength=30000,
        nation="France",
    )
    supporter.set_relationship("Blucher", 1)
    world = WorldFactory.with_marshals(
        [supporter, ally, enemy],
        player_nation="France",
    )
    _set_war(world, "Coalition", "France")
    world._marshals_by_region = {}

    ai = EnemyAI(CommandExecutor())
    action = ai._find_ally_support_opportunity(supporter, "Coalition", world)

    assert action is not None
    assert action["action"] == "attack"
    assert action["target"] == "Davout"
    assert {marshal.name for marshal in world.get_marshals_in_region_indexed("Paris")} == {
        "Blucher",
        "Davout",
    }


def test_ai_ally_adjacency_bonus_refreshes_indexes_for_direct_calls():
    marshal = MarshalFactory.infantry(
        name="Ney",
        location="Paris",
        strength=30000,
        nation="Coalition",
        personality="aggressive",
    )
    ally = MarshalFactory.infantry(
        name="Soult",
        location="Belgium",
        strength=25000,
        nation="Coalition",
        personality="cautious",
    )
    marshal.set_relationship("Soult", 0)
    world = WorldFactory.with_marshals(
        [marshal, ally],
        player_nation="France",
    )
    world._marshals_by_region = {}

    ai = EnemyAI(CommandExecutor())

    assert ai._get_ally_adjacency_bonus("Paris", marshal, "Coalition", world) == 5


def test_ai_combined_arms_bonus_refreshes_indexes_for_direct_calls():
    infantry = MarshalFactory.infantry(name="Soult", location="Belgium", nation="France")
    cavalry = MarshalFactory.cavalry(name="Murat", location="Belgium", nation="France")
    artillery = MarshalFactory.artillery(name="Drouot", location="Paris", nation="France")
    world = WorldFactory.with_marshals(
        [infantry, cavalry, artillery],
        player_nation="France",
    )
    world._marshals_by_region = {}

    ai = EnemyAI(CommandExecutor())

    assert ai._get_combined_arms_bonus("Belgium", artillery, "France", world) == 20


def test_ai_stagnation_refreshes_indexes_for_direct_calls():
    marshal = MarshalFactory.infantry(
        name="Wellington",
        location="Waterloo",
        strength=50000,
        nation="Britain",
        personality="cautious",
    )
    adjacent_regions = WorldFactory.basic().get_region("Waterloo").adjacent_regions
    weakest_enemy_name = "French 1"
    enemies = [
        MarshalFactory.enemy(
            name=f"French {index}",
            location=region_name,
            strength=20000 + (index * 5000),
            nation="France",
        )
        for index, region_name in enumerate(adjacent_regions, start=1)
    ]
    world = WorldFactory.with_marshals(
        [marshal, *enemies],
        player_nation="France",
    )
    _set_war(world, "Britain", "France")
    world._marshals_by_region = {}

    ai = EnemyAI(CommandExecutor())
    action = ai._get_stagnation_action(marshal, "Britain", world, 5, "cautious")

    assert action is not None
    assert action["action"] == "attack"
    assert action["target"] == weakest_enemy_name
    weakest_enemy_region = next(enemy.location for enemy in enemies if enemy.name == weakest_enemy_name)
    assert {
        enemy.name for enemy in world.get_hostile_marshals_in_region_indexed(weakest_enemy_region, "Britain")
    } == {weakest_enemy_name}


def test_ai_fortification_opportunity_refreshes_indexes_for_direct_calls():
    marshal = MarshalFactory.infantry(
        name="Wellington",
        location="Belgium",
        strength=60000,
        nation="Britain",
        personality="cautious",
    )
    marshal.fortified = True
    marshal.defense_bonus = 0.10
    enemy = MarshalFactory.enemy(
        name="Davout",
        location="Belgium",
        strength=10000,
        nation="France",
    )
    world = WorldFactory.with_marshals(
        [marshal, enemy],
        player_nation="France",
    )
    _set_war(world, "Britain", "France")
    world._marshals_by_region = {}

    ai = EnemyAI(CommandExecutor())
    action = ai._check_fortification_opportunity(marshal, "Britain", world)

    assert action is not None
    assert action["action"] == "unfortify"
    assert world.ai_refortify_cooldown["Wellington"] == 2
    assert {m.name for m in world.get_hostile_marshals_in_region_indexed("Belgium", "Britain")} == {
        "Davout"
    }


def test_ai_homeland_defense_refreshes_indexes_for_direct_calls():
    marshal = MarshalFactory.infantry(
        name="Wellington",
        location="Paris",
        strength=35000,
        nation="Britain",
        personality="aggressive",
    )
    world = WorldFactory.with_marshals([marshal], player_nation="France")
    _set_war(world, "Britain", "France")
    world.nation_starting_regions["Britain"] = ["Belgium"]
    world.get_region("Belgium").controller = "France"
    world._marshals_by_region = {}

    ai = EnemyAI(CommandExecutor())
    ai._recapture_targets_claimed = set()
    ai._recapture_marshal_assignments = {}

    action = ai._find_homeland_defense(marshal, "Britain", world)

    assert action is not None
    assert action["action"] == "attack"
    assert action["target"] == "Belgium"


def test_ai_undefended_capture_refreshes_indexes_for_direct_calls():
    marshal = MarshalFactory.infantry(
        name="Wellington",
        location="Paris",
        strength=30000,
        nation="Britain",
        personality="aggressive",
    )
    world = WorldFactory.with_marshals([marshal], player_nation="France")
    _set_war(world, "Britain", "France")
    world.get_region("Belgium").controller = "France"
    world._marshals_by_region = {}

    ai = EnemyAI(CommandExecutor())
    action = ai._find_undefended_capture(marshal, "Britain", world)

    assert action is not None
    assert action["action"] == "attack"
    assert action["target"] == "Belgium"


def test_ai_consolidation_refreshes_indexes_for_direct_calls():
    marshal = MarshalFactory.infantry(
        name="Ney",
        location="Paris",
        strength=10000,
        nation="Coalition",
        personality="cautious",
    )
    ally = MarshalFactory.infantry(
        name="Blucher",
        location="Lyon",
        strength=30000,
        nation="Coalition",
        personality="aggressive",
    )
    enemy = MarshalFactory.enemy(
        name="Davout",
        location="Belgium",
        strength=30000,
        nation="France",
    )
    world = WorldFactory.with_marshals([marshal, ally, enemy], player_nation="France")
    _set_war(world, "Coalition", "France")
    world._marshals_by_region = {}

    ai = EnemyAI(CommandExecutor())
    action = ai._consider_consolidation(marshal, "Coalition", world)

    assert action is not None
    assert action["action"] == "move"
    assert action["target"] == "Lyon"


def test_ai_default_action_refreshes_indexes_for_direct_calls():
    marshal = MarshalFactory.infantry(
        name="Wellington",
        location="Paris",
        strength=30000,
        nation="Britain",
        personality="cautious",
    )
    enemy = MarshalFactory.enemy(
        name="Davout",
        location="Paris",
        strength=10000,
        nation="France",
    )
    world = WorldFactory.with_marshals([marshal, enemy], player_nation="France")
    _set_war(world, "Britain", "France")
    world._marshals_by_region = {}

    ai = EnemyAI(CommandExecutor())
    action = ai._get_default_action(marshal, world)

    assert action is not None
    assert action["action"] == "attack"
    assert action["target"] == "Davout"


def test_ai_retreat_destination_refreshes_indexes_for_direct_calls():
    marshal = MarshalFactory.infantry(
        name="Ney",
        location="Paris",
        strength=12000,
        nation="France",
        personality="aggressive",
    )
    marshal_region = WorldFactory.basic().get_region("Paris")
    safe_region = marshal_region.adjacent_regions[0]
    blocked_region = marshal_region.adjacent_regions[1]
    blocker = MarshalFactory.enemy(
        name="Wellington",
        location=blocked_region,
        strength=25000,
        nation="Britain",
    )
    world = WorldFactory.with_marshals([marshal, blocker], player_nation="France")
    _set_war(world, "France", "Britain")

    for adj_name in marshal_region.adjacent_regions:
        world.get_region(adj_name).controller = "Neutral"
    world.get_region(safe_region).controller = "France"
    world.get_region(blocked_region).controller = "France"
    world._marshals_by_region = {}

    ai = EnemyAI(CommandExecutor())
    destination = ai._find_retreat_destination(marshal, "France", world)

    assert destination == safe_region


def test_ai_path_blocked_refreshes_indexes_for_direct_calls():
    blocker = MarshalFactory.enemy(
        name="Wellington",
        location="Belgium",
        strength=25000,
        nation="Britain",
    )
    world = WorldFactory.with_marshals([blocker], player_nation="France")
    _set_war(world, "France", "Britain")
    world._marshals_by_region = {}

    ai = EnemyAI(CommandExecutor())
    is_blocked, blocker_name = ai._path_is_blocked(["Paris", "Belgium", "Rhineland"], "France", world)

    assert is_blocked is True
    assert blocker_name == "Wellington"


def test_ai_capture_safety_refreshes_indexes_for_direct_calls():
    marshal = MarshalFactory.infantry(
        name="Wellington",
        location="Paris",
        strength=30000,
        nation="Britain",
        personality="cautious",
    )
    target_region = WorldFactory.basic().get_region("Belgium")
    friendly_support_region = target_region.adjacent_regions[0]
    hostile_region = target_region.adjacent_regions[1]
    supporter = MarshalFactory.infantry(
        name="Blucher",
        location=friendly_support_region,
        strength=20000,
        nation="Britain",
        personality="aggressive",
    )
    enemy = MarshalFactory.enemy(
        name="Davout",
        location=hostile_region,
        strength=20000,
        nation="France",
    )
    world = WorldFactory.with_marshals([marshal, supporter, enemy], player_nation="France")
    _set_war(world, "Britain", "France")
    world.get_region("Belgium").controller = "France"
    world._marshals_by_region = {}

    ai = EnemyAI(CommandExecutor())
    is_safe, _reason = ai._evaluate_capture_safety(marshal, "Belgium", "Britain", world)

    assert is_safe is True


def test_get_marshal_priority_refreshes_indexes_for_direct_calls():
    marshal = MarshalFactory.infantry(
        name="Wellington",
        location="Paris",
        strength=30000,
        nation="Britain",
        personality="aggressive",
    )
    enemy = MarshalFactory.enemy(
        name="Davout",
        location="Paris",
        strength=10000,
        nation="France",
    )
    world = WorldFactory.with_marshals([marshal, enemy], player_nation="France")
    _set_war(world, "Britain", "France")
    world._marshals_by_region = {}

    priority = get_marshal_priority(marshal, world)

    assert priority == 40


# --- Phase 2.1 scale-up coverage: 100-region synthetic graph ------------------
# Plan §2.1 requires a benchmark on a 100-region synthetic graph plus the
# adjacency-topology-only invariance contract. The standalone benchmark lives at
# tools/benchmark_distance_cache.py; the tests below assert the same invariants
# and a conservative cache-speedup lower bound so CI catches regressions.


def _build_synthetic_world(side: int = 10):
    """Return a WorldState whose regions form a side x side grid with 4-neighbor adjacency."""
    from tools.benchmark_distance_cache import build_grid, make_synthetic_world
    world = make_synthetic_world() if side == 10 else None
    if world is None:
        from backend.models.world_state import WorldState
        world = WorldState()
        world.regions = build_grid(side)
        world.invalidate_distance_cache()
    return world


def test_distance_cache_scales_to_100_region_synthetic_graph():
    world = _build_synthetic_world(side=10)

    assert len(world.regions) == 100

    corner_to_corner = world.get_distance("R_0_0", "R_9_9")
    assert corner_to_corner == 18  # Manhattan distance on 4-neighbor grid

    assert world.get_distance("R_9_9", "R_0_0") == 18  # symmetric
    cache_key = tuple(sorted(("R_0_0", "R_9_9")))
    assert cache_key in world._distance_cache


def test_distance_cache_is_adjacency_topology_only_on_100_region_graph():
    world = _build_synthetic_world(side=10)

    distance = world.get_distance("R_0_0", "R_9_9")
    cache_size = len(world._distance_cache)

    # Controller change is not a topology change; cache must survive.
    world.regions["R_0_0"].controller = "SomeNation"
    assert world.get_distance("R_0_0", "R_9_9") == distance
    assert len(world._distance_cache) == cache_size

    # Explicit invalidation is the only sanctioned clear.
    world.invalidate_distance_cache()
    assert world._distance_cache == {}


def test_distance_cache_measurably_faster_on_100_region_graph():
    """Conservative perf gate: cached path must beat uncached on a 100-region graph.

    Threshold is a 2x lower bound to avoid CI flakiness; in practice the speedup
    is 20-100x (see tools/benchmark_distance_cache.py).
    """
    import random
    from time import perf_counter

    world = _build_synthetic_world(side=10)
    names = list(world.regions.keys())
    rng = random.Random(42)
    pairs = [(rng.choice(names), rng.choice(names)) for _ in range(500)]

    t0 = perf_counter()
    for a, b in pairs:
        world.invalidate_distance_cache()
        world.get_distance(a, b)
    t_uncached = perf_counter() - t0

    world.invalidate_distance_cache()
    for a, b in pairs:
        world.get_distance(a, b)  # warm
    t0 = perf_counter()
    for a, b in pairs:
        world.get_distance(a, b)
    t_cached = perf_counter() - t0

    assert t_cached * 2 < t_uncached, (
        f"Cached path must be at least 2x faster on 100-region graph; "
        f"got uncached={t_uncached * 1000:.1f}ms vs cached={t_cached * 1000:.1f}ms"
    )
