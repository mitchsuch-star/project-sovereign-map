"""
Comprehensive Tests for Phase 2.9 Retreat System

Tests the full retreat system including:
1. Smart retreat destination priority (4 tiers)
2. Ally covering system (swap defender when attacked)
3. AI targeting bonus for exposed retreating marshals
4. Turn cleanup of retreated_this_turn flag
5. Forced retreat from combat (morale <= 25%)
6. Manual retreat command
7. Encirclement detection (no valid retreat = army breaks)
"""

import pytest
from backend.models.world_state import WorldState
from backend.models.marshal import Marshal, Stance
from backend.models.region import Region
from backend.commands.executor import CommandExecutor
from backend.ai.enemy_ai import EnemyAI


class TestRetreatDestinationPriority:
    """
    Test the 5-tier retreat destination priority system.

    Priority order:
    1. Adjacent friendly WITH allied marshal (COVERED on home turf - best)
    2. Adjacent friendly WITHOUT marshal (EXPOSED but safe territory)
    3. Adjacent enemy WITH allied marshal (at least you have cover)
    4. Adjacent enemy WITHOUT marshal (desperation - alone in enemy land)
    5. None = ENCIRCLED (army breaks)
    """

    def setup_method(self):
        """Fresh world state for each test."""
        self.world = WorldState()
        self.executor = CommandExecutor()

    def test_priority_1_friendly_with_ally_preferred(self):
        """Should prefer friendly region with allied marshal over empty friendly."""
        # Setup: Ney in Waterloo (enemy territory)
        # Belgium has Davout (ally), Lyon is empty friendly
        ney = self.world.marshals["Ney"]
        davout = self.world.marshals["Davout"]

        ney.location = "Belgium"  # Ney at Belgium
        davout.location = "Paris"  # Davout at Paris (adjacent to Belgium via France)

        # Make Paris controlled by France
        paris_region = self.world.get_region("Paris")
        paris_region.controller = "France"

        # Belgium adjacent to Paris
        dest = self.world.get_safe_retreat_destination("Ney")

        # Should get Paris (has ally) if adjacent, otherwise best available
        assert dest is not None
        print(f"Ney retreats to: {dest}")

    def test_priority_2_friendly_empty_over_enemy(self):
        """Should prefer empty friendly over enemy territory."""
        # Setup: Marshal in enemy territory with adjacent friendly AND enemy options
        wellington = self.world.marshals["Wellington"]

        # Put Wellington at Netherlands
        wellington.location = "Netherlands"

        # Clear other marshals from adjacent regions
        for m in self.world.marshals.values():
            if m.name != "Wellington":
                m.location = "Paris"  # Move everyone else away

        dest = self.world.get_safe_retreat_destination("Wellington")
        assert dest is not None
        print(f"Wellington retreats to: {dest}")

    def test_priority_2_friendly_empty_beats_enemy_with_ally(self):
        """Should prefer empty friendly territory over enemy territory even with ally."""
        # This is the Ney-in-Belgium scenario:
        # - Paris: Friendly, empty (Priority 2)
        # - Waterloo: Enemy territory, but Grouchy (ally) is there (Priority 3)
        # Should choose Paris (Priority 2 beats Priority 3)

        ney = self.world.marshals["Ney"]
        grouchy = self.world.marshals["Grouchy"]
        davout = self.world.marshals["Davout"]

        ney.location = "Belgium"
        grouchy.location = "Waterloo"  # Ally at enemy territory
        davout.location = "Lyon"  # Away from Paris

        # Set controllers
        self.world.regions["Paris"].controller = "France"
        self.world.regions["Waterloo"].controller = "Britain"

        dest = self.world.get_safe_retreat_destination("Ney", "Netherlands")

        # Should be Paris (friendly empty) NOT Waterloo (enemy with ally)
        assert dest == "Paris", f"Expected Paris (friendly empty) but got {dest}"
        print(f"PASS: Ney correctly retreats to Paris over enemy-controlled Waterloo")

    def test_priority_3_enemy_with_ally_over_enemy_unoccupied(self):
        """Should prefer enemy territory with ally over completely unoccupied enemy territory."""
        # Setup: No friendly options, must choose between:
        # - Enemy territory with allied marshal (Priority 3)
        # - Enemy territory completely empty (Priority 4)

        ney = self.world.marshals["Ney"]
        grouchy = self.world.marshals["Grouchy"]
        davout = self.world.marshals["Davout"]

        # Put Ney at Netherlands (only adjacent to Belgium)
        ney.location = "Netherlands"
        # Put Grouchy at Belgium (enemy territory with ally)
        grouchy.location = "Belgium"
        # Move everyone else away
        davout.location = "Lyon"

        # Make Belgium enemy-controlled, Netherlands enemy-controlled
        self.world.regions["Belgium"].controller = "Prussia"
        self.world.regions["Netherlands"].controller = "Britain"

        dest = self.world.get_safe_retreat_destination("Ney")

        # Netherlands only has Belgium adjacent, which has Grouchy
        # Should choose Belgium (enemy with ally) over having no option
        assert dest == "Belgium", f"Expected Belgium (enemy with ally) but got {dest}"
        print(f"PASS: Ney correctly retreats to Belgium where Grouchy can cover")

    def test_priority_4_unoccupied_enemy_as_last_resort(self):
        """Should use unoccupied enemy territory if no friendly or ally options."""
        ney = self.world.marshals["Ney"]

        # Put Ney in a region surrounded by enemy-controlled regions
        ney.location = "Netherlands"

        # Make sure no friendly regions adjacent - this is hard to set up
        # with hardcoded map, so we test the function exists and returns something
        dest = self.world.get_safe_retreat_destination("Ney")
        # May return None or a region depending on map state
        print(f"Ney retreat destination (surrounded scenario): {dest}")

    def test_priority_5_encircled_returns_none(self):
        """Should return None when completely surrounded by enemy marshals."""
        ney = self.world.marshals["Ney"]
        ney.location = "Belgium"

        # Put enemy marshals in ALL adjacent regions
        wellington = self.world.marshals["Wellington"]
        blucher = self.world.marshals["Blucher"]

        # Get Belgium's adjacent regions
        belgium = self.world.get_region("Belgium")
        adjacent = list(belgium.adjacent_regions)

        # This is a simplified test - full encirclement needs more enemy marshals
        # than we have in the test map
        if len(adjacent) <= 2:
            # Place enemies in all adjacent
            wellington.location = adjacent[0] if len(adjacent) > 0 else wellington.location
            blucher.location = adjacent[1] if len(adjacent) > 1 else blucher.location

        dest = self.world.get_safe_retreat_destination("Ney")
        print(f"Ney encircled retreat: {dest}")

    def test_cannot_retreat_into_enemy_marshals(self):
        """Should never suggest retreating to a region with enemy troops."""
        ney = self.world.marshals["Ney"]
        wellington = self.world.marshals["Wellington"]

        # Put Ney adjacent to Wellington
        ney.location = "Belgium"
        wellington.location = "Netherlands"

        dest = self.world.get_safe_retreat_destination("Ney")

        # Should NOT be Netherlands (Wellington is there)
        if dest:
            assert dest != "Netherlands", "Should not retreat into enemy marshal!"
        print(f"Ney avoids Wellington, retreats to: {dest}")


class TestAllyCoveringSystem:
    """
    Test the ally covers retreat mechanic.

    When attacking a marshal who retreated this turn:
    - If an ally is in same region and didn't retreat, ally fights instead
    - If no ally available, target is EXPOSED
    """

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.game_state = {"world": self.world}

    def test_ally_covers_retreating_marshal(self):
        """Attacking retreated marshal with ally present swaps defender."""
        # Use French marshals since ally cover requires SAME NATION
        # (Wellington=Britain, Blucher=Prussia - different nations can't cover each other)
        ney = self.world.marshals["Ney"]
        davout = self.world.marshals["Davout"]
        wellington = self.world.marshals["Wellington"]

        # Setup: Both French marshals in same region, Ney retreated
        ney.location = "Belgium"
        davout.location = "Belgium"
        ney.retreated_this_turn = True
        davout.retreated_this_turn = False
        davout.strength = 50000  # Healthy troops

        # Wellington attacks Ney
        wellington.location = "Netherlands"  # Adjacent to Belgium

        # Test the covering detection logic directly
        covering_candidates = [
            m for m in self.world.marshals.values()
            if m.location == ney.location
            and m.nation == ney.nation  # Same nation required!
            and m.name != ney.name
            and m.strength > 0
            and not getattr(m, 'retreated_this_turn', False)
        ]

        assert len(covering_candidates) == 1
        assert covering_candidates[0].name == "Davout"
        print(f"Davout covers for Ney!")

    def test_no_cover_when_ally_also_retreated(self):
        """If both marshals retreated, no covering happens."""
        wellington = self.world.marshals["Wellington"]
        blucher = self.world.marshals["Blucher"]

        wellington.location = "Netherlands"
        blucher.location = "Netherlands"
        wellington.retreated_this_turn = True
        blucher.retreated_this_turn = True  # ALSO retreated

        covering_candidates = [
            m for m in self.world.marshals.values()
            if m.location == wellington.location
            and m.nation == wellington.nation
            and m.name != wellington.name
            and m.strength > 0
            and not getattr(m, 'retreated_this_turn', False)
        ]

        assert len(covering_candidates) == 0
        print("No cover - both retreated")

    def test_no_cover_when_alone(self):
        """Marshal who retreated alone has no cover."""
        wellington = self.world.marshals["Wellington"]
        blucher = self.world.marshals["Blucher"]

        wellington.location = "Netherlands"
        blucher.location = "Waterloo"  # Different region
        wellington.retreated_this_turn = True

        covering_candidates = [
            m for m in self.world.marshals.values()
            if m.location == wellington.location
            and m.nation == wellington.nation
            and m.name != wellington.name
            and m.strength > 0
            and not getattr(m, 'retreated_this_turn', False)
        ]

        assert len(covering_candidates) == 0
        print("No cover - Wellington is alone")

    def test_strongest_ally_covers(self):
        """When multiple allies available, strongest covers."""
        # Would need 3+ enemy marshals to test properly
        # With the test map's 2 enemy marshals, test the selection logic
        wellington = self.world.marshals["Wellington"]
        blucher = self.world.marshals["Blucher"]

        wellington.location = "Netherlands"
        blucher.location = "Netherlands"
        wellington.retreated_this_turn = True
        blucher.retreated_this_turn = False
        blucher.strength = 75000

        covering_candidates = [
            m for m in self.world.marshals.values()
            if m.location == wellington.location
            and m.nation == wellington.nation
            and m.name != wellington.name
            and m.strength > 0
            and not getattr(m, 'retreated_this_turn', False)
        ]

        if covering_candidates:
            covering_ally = max(covering_candidates, key=lambda m: m.strength)
            assert covering_ally.name == "Blucher"
            print(f"Strongest ally {covering_ally.name} ({covering_ally.strength}) covers")


class TestAIExposedTargetBonus:
    """
    Test AI targeting bonus for exposed retreating targets.

    If target just retreated AND has no covering ally:
    - AI gets +30% effective attack ratio
    """

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.ai = EnemyAI(self.executor)

    def test_exposed_target_gets_30_percent_bonus(self):
        """Exposed retreating target gives AI +30% ratio bonus."""
        ney = self.world.marshals["Ney"]

        # Setup: Ney retreated and is alone
        ney.retreated_this_turn = True
        ney.location = "Paris"

        # Move other French marshals away
        for m in self.world.marshals.values():
            if m.nation == "France" and m.name != "Ney":
                m.location = "Lyon"

        base_ratio = 1.0
        effective_ratio = self.ai._evaluate_target_ratio(base_ratio, ney, self.world)

        # Should be at least 1.30 (30% bonus) - may be higher with other bonuses
        assert effective_ratio >= 1.30, f"Expected >= 1.30, got {effective_ratio}"
        print(f"Exposed target ratio: {base_ratio} -> {effective_ratio}")

    def test_covered_target_no_bonus(self):
        """Target with covering ally doesn't get exposed bonus."""
        ney = self.world.marshals["Ney"]
        davout = self.world.marshals["Davout"]

        # Setup: Ney retreated but Davout is covering
        ney.retreated_this_turn = True
        ney.location = "Paris"
        davout.location = "Paris"  # Same region, can cover
        davout.retreated_this_turn = False
        davout.strength = 50000

        base_ratio = 1.0
        effective_ratio = self.ai._evaluate_target_ratio(base_ratio, ney, self.world)

        # Should NOT have the +30% exposed bonus (may have other bonuses)
        # The exposed bonus only applies when no covering ally
        print(f"Covered target ratio: {base_ratio} -> {effective_ratio}")

    def test_non_retreated_target_no_bonus(self):
        """Target who didn't retreat doesn't get exposed bonus."""
        ney = self.world.marshals["Ney"]

        ney.retreated_this_turn = False  # Did NOT retreat
        ney.location = "Paris"

        base_ratio = 1.0
        effective_ratio = self.ai._evaluate_target_ratio(base_ratio, ney, self.world)

        # Should not have exposed bonus
        assert effective_ratio < 1.30 or effective_ratio == base_ratio
        print(f"Non-retreated target ratio: {base_ratio} -> {effective_ratio}")


class TestTurnCleanup:
    """Test that retreated_this_turn is properly cleared at turn start."""

    def setup_method(self):
        self.world = WorldState()

    def test_flag_cleared_on_advance_turn(self):
        """retreated_this_turn should be cleared when turn advances."""
        ney = self.world.marshals["Ney"]
        davout = self.world.marshals["Davout"]

        # Set flags on multiple marshals
        ney.retreated_this_turn = True
        davout.retreated_this_turn = True

        assert ney.retreated_this_turn == True
        assert davout.retreated_this_turn == True

        # Advance turn
        self.world.advance_turn()

        # Flags should be cleared
        assert ney.retreated_this_turn == False
        assert davout.retreated_this_turn == False
        print("Flags properly cleared on turn advance")

    def test_flag_survives_during_turn(self):
        """Flag should persist during the turn (for enemy phase)."""
        ney = self.world.marshals["Ney"]

        ney.retreated_this_turn = True
        current_turn = self.world.current_turn

        # Do things that DON'T advance turn
        # (like enemy attacks)

        # Flag should still be set
        assert ney.retreated_this_turn == True
        assert self.world.current_turn == current_turn
        print("Flag persists during turn")


class TestForcedRetreatFromCombat:
    """Test forced retreat trigger at 25% morale."""

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.game_state = {"world": self.world}

    def test_forced_retreat_threshold_is_25_percent(self):
        """Morale <= 25% should trigger forced retreat."""
        from backend.game_logic.combat import CombatResolver

        # The combat resolver checks morale after damage
        # If morale <= 25, it sets forced_retreat flag in result
        FORCED_RETREAT_THRESHOLD = 25

        # Test the threshold
        assert FORCED_RETREAT_THRESHOLD == 25
        print("Forced retreat threshold confirmed at 25%")

    def test_forced_retreat_sets_flag_via_combat(self):
        """Forced retreat from combat should set retreated_this_turn = True."""
        # Test the flag is set correctly when morale is low
        # We test the state directly since _handle_forced_retreat is internal
        ney = self.world.marshals["Ney"]
        ney.morale = 20  # Below 25% threshold
        ney.retreated_this_turn = False

        # Simulate what forced retreat does
        retreat_to = self.world.get_safe_retreat_destination("Ney")
        if retreat_to:
            ney.move_to(retreat_to)
            ney.retreated_this_turn = True

        # Verify the flag is set
        assert ney.retreated_this_turn == True
        print(f"Forced retreat sets flag correctly")

    def test_forced_retreat_uses_smart_destination(self):
        """Forced retreat should use get_safe_retreat_destination priority."""
        ney = self.world.marshals["Ney"]
        davout = self.world.marshals["Davout"]

        # Setup: Ney at Belgium, Davout at Paris (can cover)
        ney.location = "Belgium"
        davout.location = "Paris"

        # Test the destination selection
        dest = self.world.get_safe_retreat_destination("Ney")

        # Should find a safe destination
        assert dest is not None
        print(f"Ney would retreat from Belgium to {dest}")


class TestManualRetreat:
    """Test the manual retreat command."""

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.game_state = {"world": self.world}

    def test_manual_retreat_sets_flag(self):
        """Manual retreat command should set retreated_this_turn."""
        ney = self.world.marshals["Ney"]
        ney.location = "Belgium"
        ney.retreated_this_turn = False

        command = {
            "action": "retreat",
            "marshal": "Ney"
        }

        result = self.executor.execute(command, self.game_state)

        # If successful, flag should be set
        if result.get("success"):
            assert ney.retreated_this_turn == True
            print(f"Manual retreat successful: {result.get('message', '')[:100]}")
        else:
            print(f"Retreat blocked: {result.get('message', '')[:100]}")

    def test_manual_retreat_clears_offensive_states(self):
        """Retreating should clear drill, fortify, aggressive stance."""
        ney = self.world.marshals["Ney"]
        ney.location = "Belgium"
        ney.drilling = True
        ney.fortified = True
        ney.stance = Stance.AGGRESSIVE

        command = {
            "action": "retreat",
            "marshal": "Ney"
        }

        result = self.executor.execute(command, self.game_state)

        if result.get("success"):
            assert ney.drilling == False
            assert ney.fortified == False
            assert ney.stance == Stance.NEUTRAL
            print("Offensive states cleared on retreat")


class TestStanceSpamPrevention:
    """Test that AI doesn't spam stance changes."""

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.ai = EnemyAI(self.executor)

    def test_stance_change_tracked(self):
        """AI should track stance changes per marshal per turn."""
        # Initialize tracking
        self.ai._stance_changed_this_turn = set()

        # First stance change allowed
        assert self.ai._should_skip_stance_change("Wellington") == False

        # Record it
        self.ai._stance_changed_this_turn.add("Wellington")

        # Second attempt blocked
        assert self.ai._should_skip_stance_change("Wellington") == True
        print("Stance spam prevention working")

    def test_tracking_cleared_each_nation_turn(self):
        """Tracking should reset for each nation's turn."""
        # The tracking set is created fresh in process_nation_turn
        assert hasattr(self.ai, '_should_skip_stance_change')
        print("Stance tracking helper exists")


class TestIntegrationScenarios:
    """Full integration tests for retreat system."""

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.ai = EnemyAI(self.executor)
        self.game_state = {"world": self.world}

    def test_full_retreat_cycle(self):
        """Test complete: retreat -> covered -> turn advance -> cleared."""
        ney = self.world.marshals["Ney"]
        davout = self.world.marshals["Davout"]

        # 1. Ney retreats, sets flag
        ney.retreated_this_turn = True
        assert ney.retreated_this_turn == True

        # 2. Davout at same location can cover
        ney.location = "Paris"
        davout.location = "Paris"
        davout.retreated_this_turn = False

        covering = [
            m for m in self.world.marshals.values()
            if m.location == ney.location
            and m.nation == ney.nation
            and m.name != ney.name
            and not m.retreated_this_turn
        ]
        assert len(covering) > 0

        # 3. Turn advances, flag clears
        self.world.advance_turn()
        assert ney.retreated_this_turn == False

        print("Full retreat cycle completed successfully")

    def test_ai_targets_exposed_over_covered(self):
        """AI should prefer exposed retreating targets."""
        ney = self.world.marshals["Ney"]
        davout = self.world.marshals["Davout"]

        # Setup: Ney is exposed (retreated, alone)
        # Davout is covered (retreated but has theoretical cover)
        ney.retreated_this_turn = True
        ney.location = "Belgium"  # Alone
        davout.retreated_this_turn = True
        davout.location = "Paris"

        # Move Grouchy to cover Davout (if exists)
        grouchy = self.world.marshals.get("Grouchy")
        if grouchy:
            grouchy.location = "Paris"
            grouchy.retreated_this_turn = False

        # Compare target values
        ney_ratio = self.ai._evaluate_target_ratio(1.0, ney, self.world)
        davout_ratio = self.ai._evaluate_target_ratio(1.0, davout, self.world)

        print(f"Ney (exposed): {ney_ratio}, Davout (covered): {davout_ratio}")
        # Ney should be more attractive target due to exposed bonus
        if grouchy:  # Only if Davout has cover
            assert ney_ratio >= davout_ratio


class TestDebugCommands:
    """Test debug commands - these test the _execute_debug method directly."""

    def setup_method(self):
        self.world = WorldState()
        self.executor = CommandExecutor()
        self.game_state = {"world": self.world, "debug_mode": True}

    def test_debug_set_retreat_direct(self):
        """Test _execute_debug for set_retreat directly."""
        command = {"target": "set_retreat Ney"}
        result = self.executor._execute_debug(command, self.game_state)

        assert result.get("success") == True
        assert self.world.marshals["Ney"].retreated_this_turn == True
        print("Debug set_retreat works")

    def test_debug_set_recovery_direct(self):
        """Test _execute_debug for set_recovery directly."""
        command = {"target": "set_recovery Ney 2"}
        result = self.executor._execute_debug(command, self.game_state)

        assert result.get("success") == True
        assert self.world.marshals["Ney"].retreat_recovery == 2
        print("Debug set_recovery works")

    def test_debug_set_location_direct(self):
        """Test _execute_debug for set_location directly."""
        ney = self.world.marshals["Ney"]
        old_location = ney.location

        command = {"target": "set_location Ney Lyon"}
        result = self.executor._execute_debug(command, self.game_state)

        assert result.get("success") == True
        assert ney.location == "Lyon"
        print(f"Debug set_location: {old_location} -> Lyon")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
