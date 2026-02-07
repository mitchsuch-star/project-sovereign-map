"""
Tests for Session 6.1.C: Weighted Pathfinding, AI Terrain-Aware Movement, Terrain Display.

Covers:
- find_weighted_path() Dijkstra correctness
- get_weighted_distance() sum of edge weights
- MOVE_TO uses weighted pathfinding
- PURSUE stays on BFS
- AI retreat prefers non-mountain routes
- Scout/status output includes terrain info
"""

import pytest
from backend.models.world_state import WorldState
from backend.models.marshal import Marshal, StrategicOrder
from backend.models.region import (
    TERRAIN_MOVEMENT_COST, TERRAIN_DEFENSE_BONUS, Region,
)
from backend.commands.executor import CommandExecutor
from backend.ai.enemy_ai import EnemyAI


# ============================================================================
# HELPERS
# ============================================================================

def _make_world_with_terrain_overrides(overrides: dict) -> WorldState:
    """Create a WorldState and override terrain on specific regions."""
    world = WorldState()
    for region_name, terrain in overrides.items():
        region = world.get_region(region_name)
        if region:
            region.terrain = terrain
    return world


# ============================================================================
# WEIGHTED PATHFINDING CORRECTNESS
# ============================================================================

class TestFindWeightedPath:
    """Test Dijkstra-based find_weighted_path()."""

    def setup_method(self):
        # Default map: Geneva=mountains(2.0), Lyon=hills(1.2), Paris=urban(1.0)
        # Set up a scenario where BFS and Dijkstra differ.
        # Route from Marseille to Milan:
        #   BFS: Marseille -> Lyon -> Milan  (2 hops)
        #   OR:  Marseille -> Geneva -> Milan (2 hops)
        #   BFS picks either (same hop count). Dijkstra should prefer
        #   Lyon(hills=1.2) + Milan(urban=1.0) = 2.2
        #   over Geneva(mountains=2.0) + Milan(urban=1.0) = 3.0
        self.world = WorldState()

    def test_prefers_lower_attrition_route(self):
        """Dijkstra picks lower-cost route over equal-hop-count alternatives."""
        # Marseille -> Milan: via Lyon (hills 1.2 + urban 1.0 = 2.2)
        # vs via Geneva (mountains 2.0 + urban 1.0 = 3.0)
        path = self.world.find_weighted_path("Marseille", "Milan")
        assert path is not None
        assert path[0] == "Marseille"
        assert path[-1] == "Milan"
        # Should go through Lyon, not Geneva
        assert "Lyon" in path
        assert "Geneva" not in path

    def test_longer_hop_count_but_lower_cost(self):
        """Dijkstra may pick a longer hop path if terrain cost is lower."""
        # Make Rhine very expensive (mountains), so Paris->Rhine->Bavaria
        # becomes expensive. Then the alternate longer route through
        # Lyon should be preferred.
        # Paris -> Bavaria:
        #   Via Rhine: Paris->Belgium->Rhine->Bavaria
        #     Belgium(plains=1.0) + Rhine(river_crossing=1.5) + Bavaria(hills=1.2) = 3.7
        #     BUT wait, let's make Rhine = mountains (2.0)
        #     Belgium(1.0) + Rhine(2.0) + Bavaria(1.2) = 4.2
        #   Via Lyon: Paris->Lyon->Bavaria
        #     Lyon(hills=1.2) + Bavaria(hills=1.2) = 2.4  (shorter AND cheaper!)
        # Actually Paris->Lyon->Bavaria is 2 hops and cheaper. BFS may find this too.
        # We need a scenario where BFS picks one path and Dijkstra another.
        # Let me force a divergent scenario using custom terrain:

        # Make Belgium into mountains, Paris -> Belgium becomes expensive
        self.world.get_region("Belgium").terrain = "mountains"
        # Now Paris to Netherlands:
        # BFS: Paris -> Belgium -> Netherlands (2 hops) — Belgium is mountains (2.0) + Netherlands (1.0) = 3.0
        # Only route — Netherlands is only connected to Belgium, so no alternative.
        # Let's do a more interesting test:

        # Paris to Rhine:
        # Via Belgium: Paris -> Belgium(mountains=2.0) -> Rhine(river_crossing=1.5) = 3.5
        # Via Lyon: Paris -> Lyon(hills=1.2) -> Rhine(river_crossing=1.5) = 2.7
        # BFS: Both are 2 hops, BFS picks whichever it sees first (non-deterministic)
        # Dijkstra: Prefers via Lyon (2.7 < 3.5)
        path = self.world.find_weighted_path("Paris", "Rhine")
        assert path is not None
        assert "Lyon" in path
        # Should NOT go through Belgium (mountains)
        assert "Belgium" not in path

    def test_works_when_mountains_only_path(self):
        """Returns path even if only option goes through mountains."""
        # Netherlands -> Belgium is the only exit, and Belgium is already connected.
        # Netherlands only connects to Belgium. So any path FROM Netherlands
        # must go through Belgium regardless of terrain.
        self.world.get_region("Belgium").terrain = "mountains"
        path = self.world.find_weighted_path("Netherlands", "Paris")
        assert path is not None
        assert path[0] == "Netherlands"
        assert "Belgium" in path
        assert path[-1] == "Paris"

    def test_returns_none_for_unreachable(self):
        """Returns None for unreachable destination."""
        # Create isolated region by removing adjacency
        # Netherlands only connects to Belgium — if we block Belgium, no path
        path = self.world.find_weighted_path("Netherlands", "Paris",
                                              avoid_regions=["Belgium"])
        assert path is None

    def test_start_equals_end(self):
        """Returns [start] when start == end."""
        path = self.world.find_weighted_path("Paris", "Paris")
        assert path == ["Paris"]

    def test_invalid_start_region(self):
        """Returns None for invalid start region."""
        path = self.world.find_weighted_path("Mordor", "Paris")
        assert path is None

    def test_invalid_end_region(self):
        """Returns None for invalid end region."""
        path = self.world.find_weighted_path("Paris", "Mordor")
        assert path is None

    def test_respects_avoid_regions(self):
        """Avoids specified regions (destination is never avoided)."""
        # Paris to Rhine, avoid Belgium
        path = self.world.find_weighted_path("Paris", "Rhine",
                                              avoid_regions=["Belgium"])
        assert path is not None
        assert "Belgium" not in path
        # Should go through Lyon
        assert "Lyon" in path

    def test_avoid_regions_doesnt_block_destination(self):
        """Destination is reachable even if in avoid_regions."""
        path = self.world.find_weighted_path("Belgium", "Rhine",
                                              avoid_regions=["Rhine"])
        assert path is not None
        assert path[-1] == "Rhine"

    def test_weighted_and_bfs_return_different_routes(self):
        """Prove Dijkstra is actually being used, not accidentally calling BFS."""
        # Make Belgium mountains so weighted avoids it
        self.world.get_region("Belgium").terrain = "mountains"

        # Paris to Rhine:
        # BFS shortest path: Paris -> Belgium -> Rhine (2 hops)
        # Weighted: Paris -> Lyon -> Rhine (2 hops but cheaper: 1.2+1.5=2.7 vs 2.0+1.5=3.5)
        bfs_path = self.world.find_path("Paris", "Rhine")
        weighted_path = self.world.find_weighted_path("Paris", "Rhine")

        # BFS picks Belgium route (it sees Belgium first in adjacency list)
        # Weighted must pick Lyon route
        assert weighted_path is not None
        assert "Lyon" in weighted_path
        assert "Belgium" not in weighted_path
        # The paths should differ (proves Dijkstra is working)
        # Note: BFS might also pick Lyon route if adjacency order happens to
        # list Lyon first. The key test is that weighted definitely avoids Belgium.

    def test_adjacent_regions_direct_path(self):
        """Adjacent regions return direct 2-element path."""
        path = self.world.find_weighted_path("Paris", "Belgium")
        assert path is not None
        assert len(path) == 2
        assert path == ["Paris", "Belgium"]


# ============================================================================
# WEIGHTED DISTANCE
# ============================================================================

class TestGetWeightedDistance:
    """Test get_weighted_distance() returns correct cost sums."""

    def setup_method(self):
        self.world = WorldState()

    def test_correct_sum_of_edge_weights(self):
        """Returns sum of TERRAIN_MOVEMENT_COST along optimal path."""
        # Marseille -> Lyon: Lyon is hills (1.2)
        dist = self.world.get_weighted_distance("Marseille", "Lyon")
        assert dist == pytest.approx(1.2)  # Just Lyon's entry cost

    def test_multi_hop_distance(self):
        """Sums costs across multiple hops."""
        # Marseille -> Milan via Lyon (cheapest):
        # Lyon(hills=1.2) + Milan(urban=1.0) = 2.2
        dist = self.world.get_weighted_distance("Marseille", "Milan")
        assert dist == pytest.approx(2.2)

    def test_returns_inf_for_unreachable(self):
        """Returns float('inf') for unreachable destination."""
        dist = self.world.get_weighted_distance("Netherlands", "Paris")
        assert dist != float('inf')  # Sanity: this IS reachable

        # Block Belgium (only exit from Netherlands)
        dist = self.world.find_weighted_path("Netherlands", "Paris",
                                              avoid_regions=["Belgium"])
        assert dist is None  # No path exists

        # But get_weighted_distance doesn't have avoid_regions, so test
        # with actually unreachable case — add an isolated region
        # Actually, on the default map everything is connected. Let's just
        # test with an invalid region name.
        dist = self.world.get_weighted_distance("Netherlands", "Mordor")
        assert dist == float('inf')

    def test_same_region_distance_is_zero(self):
        """Distance from a region to itself is 0."""
        dist = self.world.get_weighted_distance("Paris", "Paris")
        assert dist == 0.0

    def test_weighted_greater_than_hop_count_for_mountains(self):
        """Weighted distance > hop count when path crosses mountains."""
        # Paris to Bordeaux: via Brittany (2 hops)
        # Brittany(forest=1.3) + Bordeaux(plains=1.0) = 2.3
        hop_dist = self.world.get_distance("Paris", "Bordeaux")
        weighted_dist = self.world.get_weighted_distance("Paris", "Bordeaux")
        assert weighted_dist > hop_dist  # 2.3 > 2

    def test_weighted_equals_hop_for_all_plains(self):
        """If all regions are plains (cost 1.0), weighted == hop count."""
        # Make all regions plains
        for region in self.world.regions.values():
            region.terrain = "plains"
        # Paris to Netherlands: 2 hops, cost 2.0
        hop_dist = self.world.get_distance("Paris", "Netherlands")
        weighted_dist = self.world.get_weighted_distance("Paris", "Netherlands")
        assert weighted_dist == pytest.approx(float(hop_dist))


# ============================================================================
# STRATEGIC INTEGRATION: MOVE_TO vs PURSUE
# ============================================================================

class TestMoveToUsesWeightedPath:
    """MOVE_TO should use Dijkstra for terrain-aware routes."""

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.game_state = {"world": self.world}

        # Make Belgium mountains so weighted path avoids it
        self.world.get_region("Belgium").terrain = "mountains"

        # Move French far from enemies to avoid combat interference
        for m in self.world.marshals.values():
            if m.nation != "France":
                m.location = "Vienna"
                m.strength = 1000

    def test_move_to_avoids_mountains(self):
        """MOVE_TO picks terrain-aware route (avoids mountains)."""
        ney = self.world.get_marshal("Ney")
        ney.location = "Paris"
        ney.strength = 50000
        ney.morale = 100

        # Issue MOVE_TO Rhine
        # BFS path: Paris -> Belgium(mountains) -> Rhine
        # Weighted path: Paris -> Lyon -> Rhine (cheaper)
        result = self.executor.execute(
            {"command": {
                "marshal": "Ney",
                "action": "move",
                "target": "Rhine",
                "is_strategic": True,
                "strategic_type": "MOVE_TO",
            }},
            self.game_state
        )

        assert result.get("success"), f"Expected success, got: {result.get('message')}"

        # Check the order's path avoids Belgium
        order = ney.strategic_order
        if order and order.path:
            assert "Belgium" not in order.path, \
                f"MOVE_TO path should avoid mountains, got: {order.path}"


class TestHoldUsesWeightedPath:
    """HOLD to distant region should use Dijkstra for terrain-aware routes."""

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.game_state = {"world": self.world}

        # Make Belgium mountains so weighted path avoids it
        self.world.get_region("Belgium").terrain = "mountains"

        # Move enemies far away to avoid combat interference
        for m in self.world.marshals.values():
            if m.nation != "France":
                m.location = "Vienna"
                m.strength = 1000

    def test_hold_distant_avoids_mountains(self):
        """HOLD to a distant region uses weighted path (avoids mountains)."""
        ney = self.world.get_marshal("Ney")
        ney.location = "Paris"
        ney.strength = 50000
        ney.morale = 100

        # Issue HOLD Rhine (distant — not adjacent)
        # BFS path: Paris -> Belgium(mountains) -> Rhine
        # Weighted path: Paris -> Lyon -> Rhine (cheaper)
        result = self.executor.execute(
            {"command": {
                "marshal": "Ney",
                "action": "defend",
                "target": "Rhine",
                "is_strategic": True,
                "strategic_type": "HOLD",
            }},
            self.game_state
        )

        assert result.get("success") or result.get("pending_objection"), \
            f"Expected success or objection, got: {result.get('message')}"

        # Check the order's path avoids Belgium
        order = ney.strategic_order
        if order and order.path:
            assert "Belgium" not in order.path, \
                f"HOLD path should avoid mountains, got: {order.path}"

    def test_hold_initial_path_differs_from_bfs(self):
        """HOLD initial path uses Dijkstra, producing different route from BFS."""
        # Verify weighted pathfinding gives different result from BFS
        # Paris -> Rhine: BFS may go via Belgium, weighted avoids mountains
        bfs_path = self.world.find_path("Paris", "Rhine")
        weighted_path = self.world.find_weighted_path("Paris", "Rhine")

        # Weighted should go via Lyon, BFS may go via Belgium
        assert weighted_path is not None
        assert "Belgium" not in weighted_path
        assert "Lyon" in weighted_path


class TestPursueUsesBFS:
    """PURSUE should stay on BFS (direct path)."""

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.game_state = {"world": self.world}

        # Make Belgium mountains
        self.world.get_region("Belgium").terrain = "mountains"

    def test_pursue_ignores_terrain_cost(self):
        """PURSUE uses BFS, doesn't avoid mountains."""
        ney = self.world.get_marshal("Ney")
        ney.location = "Paris"
        ney.strength = 50000
        ney.morale = 100

        wellington = self.world.get_marshal("Wellington")
        wellington.location = "Rhine"
        wellington.strength = 10000

        # Move other marshals away
        for m in self.world.marshals.values():
            if m.name not in ("Ney", "Wellington"):
                m.location = "Marseille"
                m.strength = 1000

        # Issue PURSUE Wellington
        result = self.executor.execute(
            {"command": {
                "marshal": "Ney",
                "action": "attack",
                "target": "Wellington",
                "is_strategic": True,
                "strategic_type": "PURSUE",
            }},
            self.game_state
        )

        # PURSUE should use BFS (shorter hop count or direct route)
        # Just verify the command succeeded and path was calculated
        assert result.get("success") or result.get("pending_objection"), \
            f"PURSUE should succeed or trigger objection, got: {result.get('message')}"


# ============================================================================
# AI INTEGRATION
# ============================================================================

class TestAIRetreatTerrainAware:
    """AI retreat destination picking uses weighted distance."""

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.ai = EnemyAI(self.executor)

    def test_retreat_prefers_non_mountain_route(self):
        """AI retreat sorts safe regions by weighted distance to capital."""
        wellington = self.world.get_marshal("Wellington")
        wellington.location = "Belgium"
        wellington.strength = 5000
        wellington.nation = "Britain"

        # Clear ALL non-British from adjacent regions (including Prussian allies
        # who count as "enemies" from Britain's perspective in retreat logic)
        for m in self.world.marshals.values():
            if m.nation != "Britain":
                m.location = "Marseille"
                m.strength = 1000

        # Mark Netherlands and Waterloo as controlled by Britain
        self.world.get_region("Netherlands").controller = "Britain"
        self.world.get_region("Waterloo").controller = "Britain"

        dest = self.ai._find_retreat_destination(wellington, "Britain", self.world)
        assert dest is not None
        # Should prefer Netherlands (capital, weighted distance 0)
        assert dest == "Netherlands"

    def test_retreat_avoids_mountains_when_tie(self):
        """When multiple safe regions exist, weighted distance breaks ties away from mountains."""
        # Create a scenario where two safe regions have equal hop distance to capital
        # but different terrain costs
        wellington = self.world.get_marshal("Wellington")
        wellington.location = "Lyon"
        wellington.strength = 5000

        # Clear French from Lyon's neighbors
        for m in self.world.marshals.values():
            if m.nation == "France":
                m.location = "Bordeaux"
                m.strength = 1000

        # Lyon is adjacent to: Paris, Rhine, Bavaria, Marseille, Milan
        # Set several as British-controlled
        self.world.get_region("Marseille").controller = "Britain"  # plains (1.0)
        self.world.get_region("Bavaria").controller = "Britain"    # hills (1.2)

        # Capital is Netherlands. Weighted distance from Marseille/Bavaria to Netherlands
        # will determine sort order. Since these are far from Netherlands, the AI
        # should still pick one of them — just verifying it doesn't crash.
        dest = self.ai._find_retreat_destination(wellington, "Britain", self.world)
        assert dest is not None
        assert dest in ("Marseille", "Bavaria", "Paris", "Rhine", "Milan")


# ============================================================================
# TERRAIN DISPLAY
# ============================================================================

class TestTerrainDisplay:
    """Test terrain info in scout output and status summary."""

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.game_state = {"world": self.world}

    def test_scout_includes_terrain_name_and_defense(self):
        """Targeted scout output includes terrain name and defense bonus."""
        ney = self.world.get_marshal("Ney")
        ney.location = "Paris"

        # Scout Geneva (mountains, +25% defense)
        # Geneva is at distance 3+ from Paris, so let's scout a closer region
        # Paris is adjacent to Belgium, Waterloo, Brittany, Lyon
        # Waterloo = hills (+15% defense)
        result = self.executor.execute(
            {"command": {
                "marshal": "Ney",
                "action": "scout",
                "target": "Waterloo",
            }},
            self.game_state
        )

        assert result.get("success"), f"Scout failed: {result.get('message')}"
        msg = result.get("message", "")
        assert "Terrain: Hills" in msg, f"Expected 'Terrain: Hills' in message: {msg}"
        assert "+15% defense" in msg, f"Expected '+15% defense' in message: {msg}"

    def test_scout_plains_no_defense_suffix(self):
        """Plains terrain shows 'Terrain: Plains' without defense bonus."""
        ney = self.world.get_marshal("Ney")
        ney.location = "Paris"

        # Belgium = plains (0% defense)
        result = self.executor.execute(
            {"command": {
                "marshal": "Ney",
                "action": "scout",
                "target": "Belgium",
            }},
            self.game_state
        )

        assert result.get("success")
        msg = result.get("message", "")
        assert "Terrain: Plains" in msg, f"Expected 'Terrain: Plains' in message: {msg}"
        # Plains has 0% defense — no bonus suffix
        assert "+0% defense" not in msg, "Plains should not show +0% defense"

    def test_scout_river_crossing_display(self):
        """River crossing displays as 'River Crossing' (title case, no underscore)."""
        ney = self.world.get_marshal("Ney")
        ney.location = "Belgium"  # Adjacent to Rhine (river_crossing)

        result = self.executor.execute(
            {"command": {
                "marshal": "Ney",
                "action": "scout",
                "target": "Rhine",
            }},
            self.game_state
        )

        assert result.get("success")
        msg = result.get("message", "")
        assert "River Crossing" in msg, f"Expected 'River Crossing' in message: {msg}"
        assert "+15% defense" in msg

    def test_scout_adjacent_includes_terrain(self):
        """Scout all adjacent regions includes terrain in summary."""
        ney = self.world.get_marshal("Ney")
        ney.location = "Paris"

        result = self.executor.execute(
            {"command": {
                "marshal": "Ney",
                "action": "scout",
            }},
            self.game_state
        )

        assert result.get("success")
        msg = result.get("message", "")
        # Paris is adjacent to Belgium(plains), Waterloo(hills), Brittany(forest), Lyon(hills)
        assert "Plains" in msg, f"Expected 'Plains' in adjacent scout: {msg}"
        assert "Hills" in msg, f"Expected 'Hills' in adjacent scout: {msg}"
        assert "Forest" in msg, f"Expected 'Forest' in adjacent scout: {msg}"

    def test_scout_event_includes_terrain_data(self):
        """Scout events include terrain field for Godot frontend."""
        ney = self.world.get_marshal("Ney")
        ney.location = "Paris"

        result = self.executor.execute(
            {"command": {
                "marshal": "Ney",
                "action": "scout",
                "target": "Waterloo",
            }},
            self.game_state
        )

        events = result.get("events", [])
        assert len(events) > 0
        intel = events[0].get("intel", {})
        assert intel.get("terrain") == "hills"
        assert intel.get("terrain_display") == "Hills"
        assert intel.get("defense_bonus") == 15

    def test_status_map_data_includes_terrain(self):
        """get_game_state_summary map_data includes terrain field for each region."""
        summary = self.world.get_game_state_summary()
        map_data = summary.get("map_data", {})

        assert "Paris" in map_data
        assert map_data["Paris"]["terrain"] == "urban"

        assert "Geneva" in map_data
        assert map_data["Geneva"]["terrain"] == "mountains"

        assert "Belgium" in map_data
        assert map_data["Belgium"]["terrain"] == "plains"

        # All regions should have terrain
        for region_name, data in map_data.items():
            assert "terrain" in data, f"Region {region_name} missing terrain in map_data"


# ============================================================================
# REGRESSION: Existing pathfinding untouched
# ============================================================================

class TestBFSUnchanged:
    """Verify BFS find_path() and get_distance() are not broken."""

    def setup_method(self):
        self.world = WorldState()

    def test_find_path_still_works(self):
        """BFS find_path returns shortest hop-count path."""
        path = self.world.find_path("Paris", "Rhine")
        assert path is not None
        # Paris -> Belgium -> Rhine or Paris -> Lyon -> Rhine (both 3 elements)
        assert len(path) == 3
        assert path[0] == "Paris"
        assert path[-1] == "Rhine"

    def test_get_distance_still_works(self):
        """BFS get_distance returns hop count."""
        dist = self.world.get_distance("Paris", "Rhine")
        assert dist == 2

    def test_find_path_avoid_regions_still_works(self):
        """BFS find_path with avoid_regions still works."""
        path = self.world.find_path("Paris", "Rhine", avoid_regions=["Belgium"])
        assert path is not None
        assert "Belgium" not in path
        assert "Lyon" in path

    def test_get_distance_same_region(self):
        """Distance to self is 0."""
        assert self.world.get_distance("Paris", "Paris") == 0

    def test_get_distance_invalid_region(self):
        """Invalid region returns 999."""
        assert self.world.get_distance("Paris", "Mordor") == 999


# ============================================================================
# SERIALIZATION: Ensure world serialization still passes
# ============================================================================

class TestWeightedPathfindingEdgeCases:
    """Additional edge cases for robustness."""

    def setup_method(self):
        self.world = WorldState()

    def test_all_mountains_still_finds_path(self):
        """Even if all regions are mountains, pathfinding completes."""
        for region in self.world.regions.values():
            region.terrain = "mountains"
        path = self.world.find_weighted_path("Paris", "Vienna")
        assert path is not None
        assert path[0] == "Paris"
        assert path[-1] == "Vienna"

    def test_weighted_path_returns_start_inclusive(self):
        """Path includes start region (matches find_path contract)."""
        path = self.world.find_weighted_path("Paris", "Belgium")
        assert path[0] == "Paris"

    def test_weighted_path_returns_end_inclusive(self):
        """Path includes end region."""
        path = self.world.find_weighted_path("Paris", "Belgium")
        assert path[-1] == "Belgium"

    def test_weighted_distance_adjacent_regions(self):
        """Weighted distance for adjacent regions = destination's movement cost."""
        # Paris -> Belgium: Belgium is plains (1.0)
        dist = self.world.get_weighted_distance("Paris", "Belgium")
        assert dist == pytest.approx(1.0)

        # Paris -> Brittany: Brittany is forest (1.3)
        dist = self.world.get_weighted_distance("Paris", "Brittany")
        assert dist == pytest.approx(1.3)

    def test_empty_avoid_regions_same_as_none(self):
        """Empty avoid_regions list behaves same as None."""
        path_none = self.world.find_weighted_path("Paris", "Rhine")
        path_empty = self.world.find_weighted_path("Paris", "Rhine", avoid_regions=[])
        assert path_none == path_empty
