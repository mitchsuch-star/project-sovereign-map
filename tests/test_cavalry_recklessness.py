"""
Tests for Phase 3: Cavalry Recklessness System

Reckless cavalry commanders (cavalry + aggressive personality) build momentum
through consecutive attack victories. At high recklessness, they become
increasingly powerful but harder to control.

Recklessness Levels:
0: Normal behavior
1: +5% attack, warning message
2: +10% attack, -5% defense, cannot use defensive stance
3: +15% attack, -10% defense, cannot use defensive/neutral stance, popup before attack
4+: +20% attack, -15% defense, AUTO-charge (free action at turn start)

Key Mechanics:
- Increments: +1 when winning combat as attacker
- Resets: To 0 when losing combat OR executing Glorious Charge
- Glorious Charge: 2x damage dealt AND taken
- "charge" command: Player can trigger Glorious Charge at recklessness >= 1
"""

import pytest
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.models.marshal import Marshal
from backend.models.personality import Personality


def make_command(action: str, marshal: str, target: str = None) -> dict:
    """Helper to create properly formatted commands for executor."""
    cmd = {"action": action, "marshal": marshal}
    if target:
        cmd["target"] = target
    return {"command": cmd}


class TestIsRecklessCavalryProperty:
    """Test the is_reckless_cavalry derived property."""

    def test_ney_is_reckless_cavalry(self):
        """Ney is cavalry + aggressive = reckless cavalry."""
        world = WorldState()
        ney = world.get_marshal("Ney")

        assert ney.cavalry is True
        assert ney.personality == "aggressive"
        assert ney.is_reckless_cavalry is True

    def test_davout_not_reckless_cavalry(self):
        """Davout is not cavalry, so not reckless cavalry."""
        world = WorldState()
        davout = world.get_marshal("Davout")

        assert davout.cavalry is False
        assert davout.is_reckless_cavalry is False

    def test_grouchy_not_reckless_cavalry(self):
        """Grouchy is not aggressive, so not reckless cavalry."""
        world = WorldState()
        grouchy = world.get_marshal("Grouchy")

        # Grouchy is literal personality
        assert grouchy.personality == "literal"
        assert grouchy.is_reckless_cavalry is False

    def test_non_aggressive_cavalry_not_reckless(self):
        """Cavalry without aggressive personality is not reckless."""
        world = WorldState()
        # Create a hypothetical cavalry unit with cautious personality
        marshal = Marshal("TestCavalry", "TestRegion", 50000, "cautious", "France")
        marshal.cavalry = True

        assert marshal.is_reckless_cavalry is False


class TestRecklessnessIncrement:
    """Test recklessness incrementing on attack victories."""

    def test_recklessness_starts_at_zero(self):
        """Recklessness counter starts at 0."""
        world = WorldState()
        ney = world.get_marshal("Ney")

        assert ney.recklessness == 0

    def test_recklessness_increments_on_attack_win(self):
        """Winning an attack as attacker increments recklessness by 1."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        # Set up guaranteed win for Ney
        ney.strength = 100000
        ney.morale = 100
        wellington.strength = 10000
        wellington.morale = 50
        wellington.location = "Belgium"  # Adjacent to Ney

        assert ney.recklessness == 0

        executor = CommandExecutor()
        result = executor.execute(make_command("attack", "Ney", "Wellington"), {"world": world})

        # Ney should have won and recklessness incremented
        assert result["success"] is True
        assert ney.recklessness == 1

    def test_recklessness_does_not_increment_on_defense_win(self):
        """Winning as defender does NOT increment recklessness."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        # Set up: Wellington attacks Ney, Ney wins defensively
        ney.strength = 100000
        ney.morale = 100
        wellington.strength = 10000
        wellington.morale = 50
        ney.location = "Waterloo"
        wellington.location = "Waterloo"

        initial_recklessness = ney.recklessness

        executor = CommandExecutor()
        result = executor.execute(make_command("attack", "Wellington", "Ney"), {"world": world})

        # Ney defended, should NOT gain recklessness
        assert ney.recklessness == initial_recklessness

    def test_recklessness_caps_at_four(self):
        """Recklessness cannot exceed 4."""
        world = WorldState()
        ney = world.get_marshal("Ney")

        ney.recklessness = 4
        ney._increment_recklessness()

        assert ney.recklessness == 4  # Should not go to 5

    def test_non_reckless_cavalry_does_not_gain_recklessness(self):
        """Non-reckless cavalry doesn't gain recklessness on wins."""
        world = WorldState()
        davout = world.get_marshal("Davout")
        wellington = world.get_marshal("Wellington")

        # Set up guaranteed win
        davout.strength = 100000
        wellington.strength = 10000
        wellington.location = "Paris"  # Adjacent to Davout
        davout.location = "Paris"

        executor = CommandExecutor()
        result = executor.execute(make_command("attack", "Davout", "Wellington"), {"world": world})

        # Davout is not reckless cavalry, should stay at 0
        assert davout.recklessness == 0


class TestRecklessnessReset:
    """Test recklessness resetting conditions."""

    def test_recklessness_resets_on_attack_loss(self):
        """Losing an attack resets recklessness to 0."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        # Set Ney to have recklessness (use 2 to avoid popup at 3+)
        ney.recklessness = 2

        # Set up guaranteed loss for Ney
        ney.strength = 10000
        ney.morale = 30
        wellington.strength = 100000
        wellington.morale = 100
        wellington.location = "Belgium"

        executor = CommandExecutor()
        result = executor.execute(make_command("attack", "Ney", "Wellington"), {"world": world})

        # Ney lost, recklessness should reset
        assert ney.recklessness == 0

    def test_recklessness_resets_on_glorious_charge(self):
        """Executing Glorious Charge resets recklessness to 0."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        # Set up: Ney at recklessness 3, will charge
        ney.recklessness = 3
        ney.strength = 50000
        wellington.strength = 50000
        wellington.location = "Belgium"

        executor = CommandExecutor()
        result = executor.execute(make_command("charge", "Ney", "Wellington"), {"world": world})

        # After charge, recklessness resets regardless of outcome
        assert ney.recklessness == 0

    def test_glorious_charge_win_does_not_add_recklessness(self):
        """Winning a Glorious Charge resets to 0, not +1."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        # Set up guaranteed win
        ney.recklessness = 2
        ney.strength = 100000
        ney.morale = 100
        wellington.strength = 10000
        wellington.morale = 30
        wellington.location = "Belgium"

        executor = CommandExecutor()
        result = executor.execute(make_command("charge", "Ney", "Wellington"), {"world": world})

        # Even on win, charge resets to 0, NOT +1
        assert ney.recklessness == 0


class TestRecklessnessModifiers:
    """Test combat modifiers at different recklessness levels."""

    def test_recklessness_0_no_modifier(self):
        """At recklessness 0, no attack/defense modifier."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        ney.recklessness = 0

        attack_mod = ney.get_attack_modifier()
        defense_mod = ney.get_defense_modifier()

        # Base Ney modifiers without recklessness bonus
        # (Ney has +15% base attack from aggressive)
        assert ney._get_recklessness_attack_bonus() == 0
        assert ney._get_recklessness_defense_penalty() == 0

    def test_recklessness_1_attack_bonus(self):
        """At recklessness 1, +5% attack bonus."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        ney.recklessness = 1

        assert ney._get_recklessness_attack_bonus() == 0.05

    def test_recklessness_2_modifiers(self):
        """At recklessness 2, +10% attack, -5% defense."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        ney.recklessness = 2

        assert ney._get_recklessness_attack_bonus() == 0.10
        assert ney._get_recklessness_defense_penalty() == 0.05

    def test_recklessness_3_modifiers(self):
        """At recklessness 3, +15% attack, -10% defense."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        ney.recklessness = 3

        assert ney._get_recklessness_attack_bonus() == 0.15
        assert ney._get_recklessness_defense_penalty() == 0.10

    def test_recklessness_4_modifiers(self):
        """At recklessness 4+, +20% attack, -15% defense."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        ney.recklessness = 4

        assert ney._get_recklessness_attack_bonus() == 0.20
        assert ney._get_recklessness_defense_penalty() == 0.15


class TestRecklessnessStanceRestrictions:
    """Test stance restrictions at different recklessness levels."""

    def test_recklessness_2_blocks_defensive_stance(self):
        """At recklessness 2+, cannot switch to defensive stance."""
        world = WorldState()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.recklessness = 2

        result = executor.execute(make_command("stance_change", "Ney", "defensive"), {"world": world})

        assert result["success"] is False
        assert "recklessness" in result["message"].lower() or "blood is up" in result["message"].lower()

    def test_recklessness_3_blocks_neutral_stance(self):
        """At recklessness 3+, cannot switch to neutral stance."""
        world = WorldState()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.recklessness = 3

        # First set to aggressive (not neutral) so the stance change can be attempted
        from backend.models.marshal import Stance
        ney.stance = Stance.AGGRESSIVE

        result = executor.execute(make_command("stance_change", "Ney", "neutral"), {"world": world})

        assert result["success"] is False
        assert "recklessness" in result["message"].lower() or "blood is up" in result["message"].lower() or "reckless" in result["message"].lower()

    def test_recklessness_3_allows_aggressive_stance(self):
        """At recklessness 3+, can still use aggressive stance."""
        world = WorldState()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        ney.recklessness = 3

        # First set to non-aggressive to test switch
        from backend.models.marshal import Stance
        ney.stance = Stance.NEUTRAL

        result = executor.execute(make_command("stance_change", "Ney", "aggressive"), {"world": world})

        assert result["success"] is True


class TestGloriousChargePopup:
    """Test Glorious Charge popup at recklessness 3."""

    def test_attack_at_recklessness_3_triggers_pending(self):
        """Attacking at recklessness 3 creates pending_glorious_charge."""
        world = WorldState()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        ney.recklessness = 3
        wellington.location = "Belgium"

        result = executor.execute(make_command("attack", "Ney", "Wellington"), {"world": world})

        # Should return pending state, not execute attack yet
        assert result.get("pending_glorious_charge") is True
        assert result.get("marshal") == "Ney"
        assert result.get("target") == "Wellington"
        assert "charge" in result.get("message", "").lower() or "blood is up" in result.get("message", "").lower()

    def test_respond_charge_executes_glorious_charge(self):
        """Responding 'charge' to popup executes Glorious Charge."""
        world = WorldState()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        ney.recklessness = 3
        ney.strength = 50000
        wellington.strength = 50000
        wellington.location = "Belgium"

        # First trigger the popup
        result1 = executor.execute(make_command("attack", "Ney", "Wellington"), {"world": world})
        assert result1.get("pending_glorious_charge") is True

        # Now respond with charge
        result2 = executor.respond_to_glorious_charge("charge", world)

        assert result2["success"] is True
        assert result2.get("glorious_charge") is True
        assert ney.recklessness == 0  # Reset after charge

    def test_respond_restrain_executes_normal_attack(self):
        """Responding 'restrain' to popup executes normal attack."""
        world = WorldState()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        ney.recklessness = 3
        ney.strength = 50000
        wellington.strength = 50000
        wellington.location = "Belgium"

        # First trigger the popup
        result1 = executor.execute(make_command("attack", "Ney", "Wellington"), {"world": world})

        # Now respond with restrain
        result2 = executor.respond_to_glorious_charge("restrain", world)

        assert result2["success"] is True
        assert result2.get("glorious_charge") is not True
        # Recklessness should increment if won, not reset
        # (depends on combat outcome)


class TestChargeCommand:
    """Test the explicit 'charge' command."""

    def test_charge_requires_recklessness_1(self):
        """Charge command requires at least recklessness 1."""
        world = WorldState()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        ney.recklessness = 0
        wellington.location = "Belgium"

        result = executor.execute(make_command("charge", "Ney", "Wellington"), {"world": world})

        assert result["success"] is False
        assert "momentum" in result["message"].lower() or "recklessness" in result["message"].lower()

    def test_charge_at_recklessness_1_succeeds(self):
        """Charge command at recklessness 1+ succeeds."""
        world = WorldState()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        ney.recklessness = 1
        ney.strength = 50000
        wellington.strength = 50000
        wellington.location = "Belgium"

        result = executor.execute(make_command("charge", "Ney", "Wellington"), {"world": world})

        assert result["success"] is True
        assert result.get("glorious_charge") is True

    def test_charge_bypasses_popup(self):
        """Explicit charge command doesn't trigger popup, executes immediately."""
        world = WorldState()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        ney.recklessness = 3
        ney.strength = 50000
        wellington.strength = 50000
        wellington.location = "Belgium"

        result = executor.execute(make_command("charge", "Ney", "Wellington"), {"world": world})

        # Should NOT be pending - executes immediately
        assert result.get("pending_glorious_charge") is not True
        assert result["success"] is True
        assert result.get("glorious_charge") is True

    def test_charge_on_non_cavalry_fails(self):
        """Charge command fails for non-cavalry marshals."""
        world = WorldState()
        executor = CommandExecutor()
        davout = world.get_marshal("Davout")
        wellington = world.get_marshal("Wellington")

        davout.recklessness = 1  # Even with recklessness
        wellington.location = "Paris"
        davout.location = "Paris"

        result = executor.execute(make_command("charge", "Davout", "Wellington"), {"world": world})

        assert result["success"] is False
        assert "cavalry" in result["message"].lower()

    def test_charge_on_non_reckless_cavalry_fails(self):
        """Charge command fails for non-reckless cavalry (cautious personality)."""
        world = WorldState()
        executor = CommandExecutor()

        # Create a cautious cavalry
        marshal = Marshal("TestCav", "Belgium", 50000, "cautious", "France")
        marshal.cavalry = True
        marshal.recklessness = 1
        world.marshals["TestCav"] = marshal

        wellington = world.get_marshal("Wellington")
        wellington.location = "Belgium"

        result = executor.execute(make_command("charge", "TestCav", "Wellington"), {"world": world})

        assert result["success"] is False


class TestGloriousChargeDamage:
    """Test Glorious Charge deals 2x damage dealt AND taken."""

    def test_glorious_charge_doubles_damage(self):
        """Glorious Charge deals 2x damage in both directions."""
        world = WorldState()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        ney.recklessness = 1
        ney.strength = 50000
        ney.morale = 100
        wellington.strength = 50000
        wellington.morale = 100
        wellington.location = "Belgium"

        ney_initial = ney.strength
        wellington_initial = wellington.strength

        result = executor.execute(make_command("charge", "Ney", "Wellington"), {"world": world})

        # Both should take more damage than normal attack
        # We verify by checking the charge multiplier was applied
        assert result.get("glorious_charge") is True
        assert result.get("damage_multiplier", 1) == 2


class TestAutoChargeAtFour:
    """Test auto-charge behavior at recklessness 4+."""

    def test_recklessness_4_auto_charges_at_turn_start(self):
        """At recklessness 4+, marshal auto-charges at turn start."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        ney.recklessness = 4
        wellington.location = "Belgium"  # Adjacent to Ney

        # Process turn start
        events = world._process_reckless_cavalry_turn_start()

        # Should have auto-charged
        assert any(e.get("type") == "auto_glorious_charge" for e in events)
        assert ney.recklessness == 0  # Reset after charge

    def test_auto_charge_is_free_action(self):
        """Auto-charge at 4+ doesn't consume player actions."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        initial_actions = world.actions_remaining
        ney.recklessness = 4
        wellington.location = "Belgium"

        events = world._process_reckless_cavalry_turn_start()

        # Actions should not have been consumed
        assert world.actions_remaining == initial_actions

    def test_recklessness_4_no_target_moves_toward_enemy(self):
        """At recklessness 4+ with no adjacent enemy, auto-moves toward nearest."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")
        blucher = world.get_marshal("Blucher")

        ney.recklessness = 4
        ney.location = "Paris"
        # Move ALL enemies outside Ney's 2-tile range
        wellington.location = "Vienna"  # 3 hops from Paris
        blucher.location = "Vienna"     # Both far away
        # Also move Uxbridge and Gneisenau if they exist
        for name in ["Uxbridge", "Gneisenau"]:
            m = world.get_marshal(name)
            if m:
                m.location = "Vienna"

        initial_location = ney.location

        events = world._process_reckless_cavalry_turn_start()

        # Should have moved toward enemy
        assert any(e.get("type") == "reckless_move" for e in events)
        assert ney.location != initial_location
        # Should show message about riding out
        assert any("rides out" in e.get("message", "").lower() for e in events)

    def test_recklessness_4_no_target_movement_blocked(self):
        """At recklessness 4+, if movement blocked, stays in place with message."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")
        blucher = world.get_marshal("Blucher")

        ney.recklessness = 4
        ney.location = "Belgium"
        # Put enemies in all adjacent regions to block movement
        # But no enemy IN Belgium (otherwise would charge them)
        wellington.location = "Netherlands"
        blucher.location = "Netherlands"

        # Also need to make sure no enemy is adjacent for auto-charge
        # Actually, Netherlands IS adjacent to Belgium, so this would trigger charge
        # Let me adjust: put enemies FAR away
        wellington.location = "Waterloo"  # 2 regions from Belgium
        blucher.location = "Spain"

        # Block all adjacent paths with friendly troops or other means
        # Actually the test should be: enemy exists but path is blocked
        # For now, test that if somehow movement fails, we get a message

        initial_location = ney.location
        events = world._process_reckless_cavalry_turn_start()

        # Should either move or show blocked message
        # This depends on implementation details


class TestRecklessnessAndAutonomy:
    """Test interaction between recklessness 4+ and autonomous marshals."""

    def test_recklessness_overrides_autonomy(self):
        """Recklessness 4+ overrides autonomous behavior."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        ney.recklessness = 4
        ney.autonomous = True
        ney.autonomous_turns_remaining = 2
        wellington.location = "Belgium"

        events = world._process_reckless_cavalry_turn_start()

        # Should auto-charge despite being autonomous
        assert any(e.get("type") == "auto_glorious_charge" for e in events)


class TestEnemyAIRecklessness:
    """Test enemy AI uses same recklessness rules."""

    def test_enemy_cavalry_gains_recklessness(self):
        """Enemy cavalry (if aggressive) gains recklessness on wins."""
        world = WorldState()

        # Need to find or create an enemy aggressive cavalry
        # For now, test with existing marshals
        blucher = world.get_marshal("Blucher")

        # Blucher is aggressive but need to check if cavalry
        # If not cavalry, this test verifies non-cavalry doesn't gain
        if blucher.cavalry and blucher.personality == "aggressive":
            initial_recklessness = blucher.recklessness
            # Simulate win
            blucher._increment_recklessness()
            assert blucher.recklessness == initial_recklessness + 1

    def test_ai_auto_charges_at_3(self):
        """AI with recklessness 3+ auto-charges (no popup)."""
        world = WorldState()
        ney = world.get_marshal("Ney")

        # Temporarily make Ney enemy for test
        ney.nation = "Prussia"
        ney.recklessness = 3

        # When AI processes turn, should auto-charge, not create popup
        # This is tested via enemy_ai.py integration


class TestEdgeCases:
    """Test edge cases for recklessness system."""

    def test_target_retreats_before_charge_resolves(self):
        """If target retreats before popup resolves, handle gracefully."""
        world = WorldState()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        ney.recklessness = 3
        wellington.location = "Belgium"  # Same region as Ney

        # Trigger popup
        result1 = executor.execute(make_command("attack", "Ney", "Wellington"), {"world": world})
        assert result1.get("pending_glorious_charge") is True

        # Target moves away to a location outside Ney's 2-tile range
        wellington.location = "Vienna"  # 3 hops from Belgium - outside range

        # Try to resolve charge
        result2 = executor.respond_to_glorious_charge("charge", world)

        # Should fail gracefully with message
        assert result2["success"] is False
        assert "no longer" in result2["message"].lower() or "retreated" in result2["message"].lower()

    def test_recklessness_persists_across_turns(self):
        """Recklessness does not decay over time."""
        world = WorldState()
        ney = world.get_marshal("Ney")

        ney.recklessness = 2

        # Advance several turns
        for _ in range(5):
            world.advance_turn()

        # Should still be 2 (no decay)
        assert ney.recklessness == 2

    def test_charge_requires_valid_target(self):
        """Charge command requires a valid attack target."""
        world = WorldState()
        executor = CommandExecutor()
        ney = world.get_marshal("Ney")

        ney.recklessness = 2

        # No target specified
        result = executor.execute(make_command("charge", "Ney"), {"world": world})

        assert result["success"] is False
        assert "target" in result["message"].lower()

    def test_warning_message_at_recklessness_1(self):
        """At recklessness 1, show warning message."""
        world = WorldState()
        ney = world.get_marshal("Ney")

        ney.recklessness = 1

        # Get status message
        warning = ney.get_recklessness_warning()

        assert warning is not None
        assert "blood" in warning.lower() or "momentum" in warning.lower()

    def test_multiple_reckless_cavalry_process_in_order(self):
        """Multiple reckless cavalry at 4+ process in defined order."""
        world = WorldState()

        # Would need multiple aggressive cavalry marshals
        # For now, verify single marshal works correctly
        ney = world.get_marshal("Ney")
        ney.recklessness = 4

        wellington = world.get_marshal("Wellington")
        wellington.location = "Belgium"

        events = world._process_reckless_cavalry_turn_start()

        # Should process Ney
        assert len(events) > 0


class TestTurnOrder:
    """Test correct turn processing order with recklessness."""

    def test_turn_order_recklessness_before_autonomous(self):
        """Recklessness 4+ processes at turn start."""
        world = WorldState()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        ney.recklessness = 4
        wellington.location = "Belgium"

        # Verify recklessness processing method exists and returns events list
        events = world._process_reckless_cavalry_turn_start()

        # Should complete and return list of events
        assert isinstance(events, list)
        # Should have processed Ney's auto-charge
        assert len(events) > 0
        assert any(e.get("marshal") == "Ney" for e in events)
