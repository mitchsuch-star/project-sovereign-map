"""
Tests for WorldState methods added for Phase 5.2 strategic commands.

Tests get_enemies_in_region() and find_path(avoid_regions=).

Run with: pytest tests/test_world_state_strategic.py -v
"""

import pytest
from backend.models.world_state import WorldState


class TestGetEnemiesInRegion:
    """Tests for get_enemies_in_region()."""

    def setup_method(self):
        self.world = WorldState()

    def test_finds_enemies_in_region(self):
        """Returns enemy marshals in specified region."""
        # Wellington is British, at Waterloo
        enemies = self.world.get_enemies_in_region("Waterloo", "France")
        names = [m.name for m in enemies]
        assert "Wellington" in names

    def test_excludes_friendly_marshals(self):
        """Does not return marshals of same nation."""
        # Move Grouchy to Waterloo alongside Wellington
        self.world.marshals["Grouchy"].location = "Waterloo"
        enemies = self.world.get_enemies_in_region("Waterloo", "France")
        names = [m.name for m in enemies]
        assert "Grouchy" not in names
        assert "Wellington" in names

    def test_excludes_dead_marshals(self):
        """Does not return marshals with strength <= 0."""
        # Zero out all enemy marshals at Waterloo
        for m in self.world.marshals.values():
            if m.location == "Waterloo" and m.nation != "France":
                m.strength = 0
        enemies = self.world.get_enemies_in_region("Waterloo", "France")
        assert len(enemies) == 0

    def test_empty_region_returns_empty(self):
        """Returns empty list if no enemies in region."""
        enemies = self.world.get_enemies_in_region("Paris", "France")
        assert enemies == []

    def test_perspective_matters(self):
        """Same region returns different results based on perspective nation."""
        # From France's perspective, Wellington is enemy
        fr_enemies = self.world.get_enemies_in_region("Waterloo", "France")
        assert len(fr_enemies) > 0
        # From Britain's perspective, Wellington is friendly
        br_enemies = self.world.get_enemies_in_region("Waterloo", "Britain")
        assert all(m.name != "Wellington" for m in br_enemies)

    def test_multiple_enemies_in_region(self):
        """Returns all enemy marshals when multiple present."""
        # Move Blucher to Waterloo with Wellington
        self.world.marshals["Blucher"].location = "Waterloo"
        enemies = self.world.get_enemies_in_region("Waterloo", "France")
        names = [m.name for m in enemies]
        assert "Wellington" in names
        assert "Blucher" in names


class TestFindPathAvoidRegions:
    """Tests for find_path() with avoid_regions parameter."""

    def setup_method(self):
        self.world = WorldState()

    def test_empty_avoid_list_finds_shortest(self):
        """With no avoid regions, finds normal shortest path."""
        path_normal = self.world.find_path("Paris", "Belgium")
        path_empty_avoid = self.world.find_path("Paris", "Belgium", avoid_regions=[])
        assert path_normal == path_empty_avoid

    def test_none_avoid_finds_shortest(self):
        """None avoid_regions (default) finds normal shortest path."""
        path_default = self.world.find_path("Paris", "Belgium")
        path_none = self.world.find_path("Paris", "Belgium", avoid_regions=None)
        assert path_default == path_none

    def test_avoids_specified_regions(self):
        """Path goes around avoided regions."""
        # Get the normal path
        normal_path = self.world.find_path("Paris", "Belgium")
        assert normal_path is not None

        # If normal path goes through some intermediate region, avoid it
        if len(normal_path) > 2:
            intermediate = normal_path[1]  # First hop after start
            alt_path = self.world.find_path("Paris", "Belgium", avoid_regions=[intermediate])
            if alt_path is not None:
                assert intermediate not in alt_path[1:-1]  # Not in middle of path

    def test_destination_never_avoided(self):
        """Destination is reachable even if in avoid list."""
        path = self.world.find_path("Paris", "Belgium", avoid_regions=["Belgium"])
        assert path is not None
        assert path[-1] == "Belgium"

    def test_returns_none_if_no_safe_path(self):
        """Returns None if all paths blocked by avoided regions."""
        # Get all regions adjacent to Paris
        paris = self.world.regions["Paris"]
        all_adjacent = list(paris.adjacent_regions)
        # Block all adjacent regions (except destination if it's adjacent)
        # This should block all paths from Paris to a distant region
        path = self.world.find_path("Paris", "Vienna", avoid_regions=all_adjacent)
        assert path is None

    def test_start_equals_end_ignores_avoid(self):
        """Same start and end returns immediately regardless of avoid list."""
        path = self.world.find_path("Paris", "Paris", avoid_regions=["Paris"])
        assert path == ["Paris"]
