"""
Tests for Movement Through Enemies Bug Fix

Rule: If an enemy marshal occupies your current region, you can only move to
regions controlled by your nation (retreat/disengage). Cannot advance through enemies.

Tests cover:
1. Cannot move to enemy territory while engaged with enemy
2. Can move to friendly territory while engaged (retreat/disengage)
3. Normal movement when no enemy present
4. Cavalry extended range still works when disengaging
5. Enemy AI follows same rules (building blocks principle)
"""

import pytest
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor


def make_command(action: str, marshal: str, target: str = None) -> dict:
    """Helper to create properly formatted commands for executor."""
    cmd = {"action": action, "marshal": marshal}
    if target:
        cmd["target"] = target
    return {"command": cmd}


class TestMoveThroughEnemyToEnemyBlocked:
    """Test that moving to enemy territory while engaged is blocked."""

    def test_move_to_enemy_territory_blocked_when_engaged(self):
        """Cannot advance to enemy territory while enemy marshal in same region."""
        world = WorldState()
        executor = CommandExecutor()

        # Setup: Move Wellington to Belgium (same region as Ney)
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")
        wellington.location = "Belgium"  # Now both in Belgium

        # Belgium is adjacent to Netherlands (British territory)
        # Ney tries to move to Netherlands while engaged with Wellington
        command = make_command("move", "Ney", "Netherlands")

        result = executor.execute(command, {"world": world})

        assert result["success"] is False
        assert "Cannot advance while engaged with enemy forces" in result["message"]
        assert "friendly territory" in result["message"]
        assert ney.location == "Belgium"  # Ney didn't move

    def test_move_to_enemy_territory_blocked_error_includes_engaged_with(self):
        """Error response includes which enemy marshal is engaging."""
        world = WorldState()
        executor = CommandExecutor()

        wellington = world.get_marshal("Wellington")
        wellington.location = "Belgium"

        command = make_command("move", "Ney", "Netherlands")

        result = executor.execute(command, {"world": world})

        assert result["success"] is False
        assert "engaged_with" in result
        assert "Wellington" in result["engaged_with"]


class TestMoveThroughEnemyToFriendlyAllowed:
    """Test that moving to friendly territory while engaged is allowed (retreat)."""

    def test_move_to_friendly_territory_allowed_when_engaged(self):
        """Can retreat to friendly territory while enemy marshal in same region."""
        world = WorldState()
        executor = CommandExecutor()

        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")
        wellington.location = "Belgium"  # Engage with Ney

        # Belgium is adjacent to Paris (French territory)
        # Ney should be able to retreat to Paris
        command = make_command("move", "Ney", "Paris")

        result = executor.execute(command, {"world": world})

        assert result["success"] is True
        assert ney.location == "Paris"

    def test_cavalry_can_use_extended_range_when_disengaging(self):
        """Cavalry (like Ney) can still use 2-region movement when retreating."""
        world = WorldState()
        executor = CommandExecutor()

        # Setup: Ney at Belgium, enemy at Belgium
        ney = world.get_marshal("Ney")
        assert ney.movement_range == 2  # Ney is cavalry

        wellington = world.get_marshal("Wellington")
        wellington.location = "Belgium"

        # Belgium -> Paris -> Lyon (2 hops, Lyon is French)
        # Lyon should be accessible via cavalry range
        command = make_command("move", "Ney", "Lyon")

        result = executor.execute(command, {"world": world})

        assert result["success"] is True
        assert ney.location == "Lyon"


class TestMoveNoEnemyNormalRules:
    """Test that normal movement rules apply when no enemy present."""

    def test_can_move_to_enemy_territory_when_not_engaged(self):
        """Can move to enemy territory when no enemy in current region."""
        world = WorldState()
        executor = CommandExecutor()

        ney = world.get_marshal("Ney")
        # Ney is at Belgium, Wellington is at Waterloo (not same region)
        wellington = world.get_marshal("Wellington")
        assert wellington.location == "Waterloo"
        assert ney.location == "Belgium"

        # Belgium is adjacent to Netherlands (British territory)
        # Should be allowed since no enemy in Belgium
        command = make_command("move", "Ney", "Netherlands")

        result = executor.execute(command, {"world": world})

        assert result["success"] is True
        assert ney.location == "Netherlands"

    def test_can_move_to_friendly_territory_when_not_engaged(self):
        """Normal movement to friendly territory works."""
        world = WorldState()
        executor = CommandExecutor()

        ney = world.get_marshal("Ney")

        command = make_command("move", "Ney", "Paris")

        result = executor.execute(command, {"world": world})

        assert result["success"] is True
        assert ney.location == "Paris"


class TestEnemyAIFollowsSameRules:
    """Test that enemy AI is subject to same movement restrictions."""

    def test_enemy_blocked_from_advancing_when_engaged(self):
        """Enemy marshal cannot advance through player marshal."""
        world = WorldState()
        executor = CommandExecutor()

        # Setup: Move Ney to Waterloo (British territory, Wellington's starting region)
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")
        ney.location = "Waterloo"  # Ney engages Wellington

        # Wellington at Waterloo, Ney at Waterloo (engaged)
        # Waterloo is adjacent to Belgium (French) and Paris (French)
        # Wellington should not be able to advance to French territory
        command = make_command("move", "Wellington", "Belgium")  # French territory

        result = executor.execute(command, {"world": world})

        assert result["success"] is False
        assert "Cannot advance while engaged with enemy forces" in result["message"]
        assert wellington.location == "Waterloo"

    def test_enemy_can_retreat_to_own_territory_when_engaged(self):
        """Enemy marshal can retreat to friendly territory when engaged."""
        world = WorldState()
        executor = CommandExecutor()

        # Setup: Move Ney to Waterloo (British territory)
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")
        ney.location = "Waterloo"  # Ney engages Wellington

        # Waterloo adjacent to Belgium (French) and Paris (French)
        # Wellington has no friendly retreat option from Waterloo in default map
        # Let's make Belgium British-controlled for this test
        world.regions["Belgium"].controller = "Britain"

        command = make_command("move", "Wellington", "Belgium")  # Now British territory

        result = executor.execute(command, {"world": world})

        assert result["success"] is True
        assert wellington.location == "Belgium"


class TestAttackWhileEngaged:
    """Test that you cannot attack elsewhere while engaged with enemy in your region."""

    def test_cannot_attack_distant_enemy_while_engaged(self):
        """If enemy in your region, cannot attack enemy in different region."""
        world = WorldState()
        executor = CommandExecutor()

        # Setup: Ney at Belgium, Wellington also at Belgium, Blucher at Netherlands
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")
        blucher = world.get_marshal("Blucher")

        wellington.location = "Belgium"  # Enemy in Ney's region
        blucher.location = "Netherlands"  # Different region

        # Ney tries to attack Blucher but is engaged with Wellington
        command = make_command("attack", "Ney", "Blucher")

        result = executor.execute(command, {"world": world})

        assert result["success"] is False
        assert "engaged" in result["message"].lower()
        assert "Wellington" in result["engaged_with"]

    def test_can_attack_enemy_in_same_region(self):
        """Can attack enemy that is in the same region (fighting them!)."""
        world = WorldState()
        executor = CommandExecutor()

        # Setup: Ney and Wellington both at Belgium
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")
        wellington.location = "Belgium"

        # Ney attacks Wellington - this should work
        command = make_command("attack", "Ney", "Wellington")

        result = executor.execute(command, {"world": world})

        # Should succeed (combat happens)
        assert result["success"] is True

    def test_enemy_ai_cannot_attack_elsewhere_while_engaged(self):
        """Enemy AI follows same rule - cannot attack elsewhere while engaged."""
        world = WorldState()
        executor = CommandExecutor()

        # Setup: Wellington at Belgium (with Ney), Davout at Paris
        wellington = world.get_marshal("Wellington")
        ney = world.get_marshal("Ney")
        davout = world.get_marshal("Davout")

        wellington.location = "Belgium"  # Engaged with Ney
        davout.location = "Paris"

        # Wellington tries to attack Davout but is engaged with Ney
        command = make_command("attack", "Wellington", "Davout")

        result = executor.execute(command, {"world": world})

        assert result["success"] is False
        assert "engaged" in result["message"].lower()


class TestCavalryCannotLeapfrog:
    """Test that cavalry cannot attack through enemies (leapfrog)."""

    def test_cavalry_charge_blocked_by_enemy_in_path(self):
        """Cavalry cannot charge 2 regions if enemy in middle region."""
        world = WorldState()
        executor = CommandExecutor()

        # Setup: Ney (cavalry) at Belgium, Grouchy at Paris, Wellington at Lyon
        # Belgium -> Paris -> Lyon is 2 hops
        ney = world.get_marshal("Ney")
        assert ney.movement_range == 2  # Cavalry

        grouchy = world.get_marshal("Grouchy")
        grouchy.location = "Paris"  # Enemy in the path

        wellington = world.get_marshal("Wellington")
        wellington.location = "Lyon"  # Target 2 regions away

        # Ney tries to charge Wellington but Grouchy blocks the path
        # Wait - Grouchy is French, not an enemy to Ney
        # Let me fix this - put an ENEMY in the path
        blucher = world.get_marshal("Blucher")
        blucher.location = "Paris"  # Enemy in the path

        command = make_command("attack", "Ney", "Wellington")

        result = executor.execute(command, {"world": world})

        assert result["success"] is False
        assert "blocks the path" in result["message"] or "Cannot charge through" in result["message"]
        assert ney.location == "Belgium"  # Ney didn't move

    def test_cavalry_charge_allowed_if_path_clear(self):
        """Cavalry can charge 2 regions if no enemy in middle region."""
        world = WorldState()
        executor = CommandExecutor()

        # Setup: Ney at Belgium, Wellington at Lyon (2 hops via Paris)
        # Paris is French-controlled with no enemies
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")
        wellington.location = "Lyon"

        # Verify path is clear (no enemies in Paris)
        enemies_in_paris = [
            m for m in world.get_marshals_in_region("Paris")
            if m.nation != "France"
        ]
        assert len(enemies_in_paris) == 0

        command = make_command("attack", "Ney", "Wellington")

        result = executor.execute(command, {"world": world})

        # Should succeed (combat happens)
        assert result["success"] is True
        assert "cavalry" in result["message"].lower() or "charge" in result["message"].lower()


class TestEdgeCases:
    """Edge cases for movement through enemies."""

    def test_multiple_enemies_in_region(self):
        """Movement blocked even with multiple enemies in region."""
        world = WorldState()
        executor = CommandExecutor()

        # Put both Wellington and Blucher in Belgium
        wellington = world.get_marshal("Wellington")
        blucher = world.get_marshal("Blucher")
        wellington.location = "Belgium"
        blucher.location = "Belgium"

        command = make_command("move", "Ney", "Netherlands")  # British territory

        result = executor.execute(command, {"world": world})

        assert result["success"] is False
        # Both enemies should be listed
        assert "Wellington" in result["engaged_with"]
        assert "Blucher" in result["engaged_with"]

    def test_friendly_marshal_in_region_does_not_block(self):
        """Having a friendly marshal in region doesn't trigger engagement check."""
        world = WorldState()
        executor = CommandExecutor()

        # Move Davout to Belgium (both French marshals together)
        davout = world.get_marshal("Davout")
        davout.location = "Belgium"

        # Ney should still be able to move to Netherlands (enemy territory)
        # since Davout is friendly, not an enemy
        command = make_command("move", "Ney", "Netherlands")

        result = executor.execute(command, {"world": world})

        assert result["success"] is True

    def test_suggestion_lists_friendly_regions(self):
        """Error message suggests available friendly retreat options."""
        world = WorldState()
        executor = CommandExecutor()

        wellington = world.get_marshal("Wellington")
        wellington.location = "Belgium"

        command = make_command("move", "Ney", "Netherlands")

        result = executor.execute(command, {"world": world})

        assert result["success"] is False
        assert "suggestion" in result
        # Paris should be in the suggestion (French territory adjacent to Belgium)
        assert "Paris" in result["suggestion"]
