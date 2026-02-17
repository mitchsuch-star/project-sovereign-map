"""
Test suite for capture hint on move (Session 31).

After a marshal moves, if adjacent enemy regions are undefended and visible,
show a [HINT] suggesting the player attack to capture.
"""

import pytest
from backend.commands.executor import CommandExecutor
from backend.models.world_state import WorldState
from backend.models.intel import FULL, PARTIAL, STALE, UNKNOWN


# ════════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════════

def _setup():
    """Create a fresh world and executor for testing."""
    world = WorldState()
    game_state = {"world": world}
    executor = CommandExecutor()
    return world, game_state, executor


# ════════════════════════════════════════════════════════════════════════════════
# CAPTURE HINT TESTS
# ════════════════════════════════════════════════════════════════════════════════

class TestCaptureHint:
    """Test capture hints after successful move."""

    def test_hint_shown_for_undefended_enemy_region(self):
        """Moving next to an undefended enemy region shows [HINT]."""
        world, gs, executor = _setup()
        # Use Ney, move from Belgium to a region adjacent to an enemy region
        ney = world.marshals["Ney"]
        ney.location = "Belgium"

        # Make Netherlands enemy-controlled and undefended
        netherlands = world.regions["Netherlands"]
        netherlands.controller = "Britain"
        netherlands.garrison_strength = 0
        netherlands.garrison_detachment = False

        # Ensure FULL visibility on Netherlands
        intel = world.get_region_intel("Netherlands")
        intel.visibility = FULL

        # Move all enemies away from Netherlands
        for m in world.marshals.values():
            if m.nation != "France" and m.location == "Netherlands":
                m.location = "London"

        # Belgium is adjacent to Netherlands, so moving within Belgium wouldn't work
        # Ney is already in Belgium which is adjacent to Netherlands
        # Move Ney to a region NOT adjacent to Netherlands first, then move to Belgium
        ney.location = "Paris"
        result = executor._execute_move(ney, "Belgium", world, gs)

        assert result["success"] is True
        assert "[HINT]" in result["message"]
        assert "Netherlands" in result["message"]
        assert "capture_hints" in result
        assert "Netherlands" in result["capture_hints"]

    def test_no_hint_for_defended_region(self):
        """No hint when enemy region has defending marshals."""
        world, gs, executor = _setup()
        ney = world.marshals["Ney"]
        ney.location = "Paris"

        # Make Netherlands enemy-controlled with an enemy marshal present
        netherlands = world.regions["Netherlands"]
        netherlands.controller = "Britain"

        # Find an enemy marshal and place in Netherlands
        for m in world.marshals.values():
            if m.nation != "France":
                m.location = "Netherlands"
                break

        # Ensure FULL visibility
        intel = world.get_region_intel("Netherlands")
        intel.visibility = FULL

        result = executor._execute_move(ney, "Belgium", world, gs)
        assert result["success"] is True
        # Should not show Netherlands as capturable
        hints = result.get("capture_hints", [])
        assert "Netherlands" not in hints

    def test_no_hint_for_garrisoned_region(self):
        """No hint when enemy region has garrison >= 5000."""
        world, gs, executor = _setup()
        ney = world.marshals["Ney"]
        ney.location = "Paris"

        # Make Netherlands enemy-controlled with capital garrison
        netherlands = world.regions["Netherlands"]
        netherlands.controller = "Britain"
        netherlands.garrison_strength = 15000
        netherlands.garrison_detachment = False

        # Move all enemies out of Netherlands
        for m in world.marshals.values():
            if m.nation != "France" and m.location == "Netherlands":
                m.location = "London"

        intel = world.get_region_intel("Netherlands")
        intel.visibility = FULL

        result = executor._execute_move(ney, "Belgium", world, gs)
        assert result["success"] is True
        hints = result.get("capture_hints", [])
        assert "Netherlands" not in hints

    def test_no_hint_for_player_garrisoned_region(self):
        """No hint when enemy region has player-placed garrison > 0."""
        world, gs, executor = _setup()
        ney = world.marshals["Ney"]
        ney.location = "Paris"

        netherlands = world.regions["Netherlands"]
        netherlands.controller = "Britain"
        netherlands.garrison_strength = 2000
        netherlands.garrison_detachment = True

        for m in world.marshals.values():
            if m.nation != "France" and m.location == "Netherlands":
                m.location = "London"

        intel = world.get_region_intel("Netherlands")
        intel.visibility = FULL

        result = executor._execute_move(ney, "Belgium", world, gs)
        assert result["success"] is True
        hints = result.get("capture_hints", [])
        assert "Netherlands" not in hints

    def test_no_hint_for_friendly_region(self):
        """No hint for regions controlled by the same nation."""
        world, gs, executor = _setup()
        ney = world.marshals["Ney"]
        ney.location = "Paris"

        # Belgium is French-controlled — should not show as hint
        result = executor._execute_move(ney, "Belgium", world, gs)
        assert result["success"] is True
        hints = result.get("capture_hints", [])
        # No French-controlled region should appear
        for h in hints:
            region = world.regions.get(h)
            assert region is None or region.controller != "France"

    def test_adjacent_fogged_region_becomes_visible_after_move(self):
        """Adjacent enemy regions get PARTIAL visibility after moving,
        so capture hints fire for undefended adjacent regions.

        Previously, manually setting STALE would block hints. Now that
        calculate_visibility() runs after each move, adjacent regions
        always get at least PARTIAL from army adjacency.
        """
        world, gs, executor = _setup()
        ney = world.marshals["Ney"]
        ney.location = "Paris"

        netherlands = world.regions["Netherlands"]
        netherlands.controller = "Britain"
        netherlands.garrison_strength = 0

        for m in world.marshals.values():
            if m.nation != "France" and m.location == "Netherlands":
                m.location = "London"

        # Even if we set STALE, moving to Belgium refreshes adjacency → PARTIAL
        intel = world.get_region_intel("Netherlands")
        intel.visibility = STALE

        result = executor._execute_move(ney, "Belgium", world, gs)
        assert result["success"] is True
        hints = result.get("capture_hints", [])
        # Netherlands is now visible (PARTIAL from adjacency) so hint fires
        assert "Netherlands" in hints

    def test_hint_works_with_partial_visibility(self):
        """Hint shown when enemy region has PARTIAL visibility."""
        world, gs, executor = _setup()
        ney = world.marshals["Ney"]
        ney.location = "Paris"

        netherlands = world.regions["Netherlands"]
        netherlands.controller = "Britain"
        netherlands.garrison_strength = 0

        for m in world.marshals.values():
            if m.nation != "France" and m.location == "Netherlands":
                m.location = "London"

        intel = world.get_region_intel("Netherlands")
        intel.visibility = PARTIAL

        result = executor._execute_move(ney, "Belgium", world, gs)
        assert result["success"] is True
        hints = result.get("capture_hints", [])
        assert "Netherlands" in hints

    def test_no_hint_for_enemy_marshals(self):
        """Enemy marshals don't get capture hints."""
        world, gs, executor = _setup()
        # Find an enemy marshal
        enemy = None
        for m in world.marshals.values():
            if m.nation != "France":
                enemy = m
                break
        assert enemy is not None

        # Set up adjacent undefended French region
        enemy.location = "Netherlands"
        belgium = world.regions["Belgium"]
        belgium.controller = "France"
        belgium.garrison_strength = 0

        intel = world.get_region_intel("Belgium")
        intel.visibility = FULL

        result = executor._execute_move(enemy, "Belgium", world, gs)
        # Enemy move should not have capture_hints
        assert "capture_hints" not in result
