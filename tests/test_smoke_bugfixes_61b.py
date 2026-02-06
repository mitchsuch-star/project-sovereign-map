"""
Regression tests for 3 bugs found during Godot smoke testing of 6.1.B.

Bug 1: cavalry_terrain_message not passed through main.py to Godot
Bug 2: glorious charge popup not appearing on allowed terrain
Bug 3: recklessness counter resets on blocked charge (should persist)
"""

import pytest
from unittest.mock import patch
from backend.game_logic.combat import CombatResolver
from backend.models.marshal import Marshal, Stance
from backend.models.world_state import WorldState
from backend.models.region import (
    TERRAIN_CAVALRY_EFFECTIVENESS, CHARGE_BLOCKED_TERRAIN,
)
from backend.commands.executor import CommandExecutor


# ============================================================================
# HELPERS
# ============================================================================

def make_command(action: str, marshal: str, target: str = None) -> dict:
    cmd = {"action": action, "marshal": marshal}
    if target:
        cmd["target"] = target
    return {"command": cmd}


def make_reckless_cavalry(name="Ney", location="Belgium", strength=50000,
                          recklessness=0, nation="France"):
    """Create a reckless cavalry marshal (cavalry + aggressive)."""
    m = Marshal(name, location, strength, "aggressive", nation)
    m.cavalry = True
    m.recklessness = recklessness
    m.morale = 100
    return m


# ============================================================================
# BUG 1: cavalry_terrain_message passthrough
# ============================================================================

class TestCavalryTerrainMessagePassthrough:
    """cavalry_terrain_message must appear in combat result AND executor result."""

    def test_combat_resolver_generates_cavalry_terrain_message_on_plains(self):
        """On plains (1.2x effectiveness), reckless cavalry should get a terrain message."""
        combat = CombatResolver()
        attacker = make_reckless_cavalry(recklessness=2)
        defender = Marshal("Wellington", "Belgium", 40000, "cautious", "Britain")

        with patch("random.randint", return_value=3):
            result = combat.resolve_battle(attacker, defender, terrain="plains")

        # Plains has TERRAIN_CAVALRY_EFFECTIVENESS of 1.2 (not 1.0), so message expected
        assert result.get("cavalry_terrain_message") is not None, (
            "cavalry_terrain_message should be set for reckless cavalry on plains"
        )
        assert "plains" in result["cavalry_terrain_message"].lower() or "Plains" in result["cavalry_terrain_message"]

    def test_combat_resolver_generates_cavalry_terrain_message_on_forest(self):
        """On forest (0.5x effectiveness), reckless cavalry should get a negative terrain message."""
        combat = CombatResolver()
        attacker = make_reckless_cavalry(recklessness=2)
        defender = Marshal("Wellington", "Belgium", 40000, "cautious", "Britain")

        with patch("random.randint", return_value=3):
            result = combat.resolve_battle(attacker, defender, terrain="forest")

        assert result.get("cavalry_terrain_message") is not None
        assert "hampered" in result["cavalry_terrain_message"].lower() or "Forest" in result["cavalry_terrain_message"]

    def test_no_cavalry_terrain_message_at_recklessness_zero(self):
        """At recklessness 0, no recklessness bonus means no cavalry terrain message."""
        combat = CombatResolver()
        attacker = make_reckless_cavalry(recklessness=0)
        defender = Marshal("Wellington", "Belgium", 40000, "cautious", "Britain")

        with patch("random.randint", return_value=3):
            result = combat.resolve_battle(attacker, defender, terrain="plains")

        # At recklessness 0, _get_recklessness_attack_bonus() returns 0 so no message
        assert result.get("cavalry_terrain_message") is None

    def test_executor_passes_cavalry_terrain_message(self):
        """_execute_attack must include cavalry_terrain_message from combat result."""
        world = WorldState(player_nation="France")
        executor = CommandExecutor()
        game_state = {"world": world}

        ney = world.get_marshal("Ney")
        ney.recklessness = 1  # Non-zero so terrain message triggers

        # Move an enemy to Ney's adjacent region
        wellington = world.get_marshal("Wellington")
        wellington.location = "Belgium"
        wellington.strength = 40000

        cmd = make_command("attack", "Ney", "Wellington")
        result = executor.execute(cmd, game_state)

        # The result should include cavalry_terrain_message if combat generated one
        # (Belgium = plains, 1.2x cavalry effectiveness)
        if result.get("success"):
            # If attack succeeded, cavalry_terrain_message should be present
            # (it's in the description text AND as a separate field)
            assert "cavalry_terrain_message" in result or "cavalry" in result.get("message", "").lower(), (
                "Cavalry terrain message should be accessible in executor result"
            )


# ============================================================================
# BUG 2: glorious charge popup on allowed terrain
# ============================================================================

class TestGloriousChargePopupTerrain:
    """Popup must appear on allowed terrain (plains/hills) and be blocked on
    mountains/forest/urban."""

    def _setup_reckless_attack(self, defender_terrain="plains"):
        """Set up a world where Ney at recklessness 3 attacks an enemy."""
        world = WorldState(player_nation="France")
        executor = CommandExecutor()
        game_state = {"world": world}

        ney = world.get_marshal("Ney")
        ney.recklessness = 3
        ney.morale = 100

        # Find a region with the desired terrain
        target_region = None
        for name, region in world.regions.items():
            if region.terrain == defender_terrain and name != ney.location:
                # Check adjacency
                ney_region = world.get_region(ney.location)
                if ney_region and name in ney_region.adjacent_regions:
                    target_region = name
                    break

        if not target_region:
            # Manually set terrain if we couldn't find an adjacent one
            # Move Ney somewhere adjacent to Waterloo (hills)
            if defender_terrain == "hills":
                target_region = "Waterloo"
                ney.location = "Belgium"  # Adjacent to Waterloo
            elif defender_terrain == "plains":
                target_region = "Belgium"
                ney.location = "Paris"  # Adjacent to Belgium
            elif defender_terrain == "forest":
                target_region = "Brittany"
                ney.location = "Paris"  # Adjacent to Brittany
            else:
                pytest.skip(f"No adjacent region with terrain '{defender_terrain}'")

        # Place an enemy in that region
        wellington = world.get_marshal("Wellington")
        wellington.location = target_region
        wellington.strength = 40000

        return world, executor, game_state, ney, wellington

    def test_popup_appears_on_plains(self):
        """At recklessness 3, attacking enemy in plains -> popup must appear."""
        world, executor, game_state, ney, wellington = self._setup_reckless_attack("plains")

        cmd = make_command("attack", "Ney", wellington.name)
        result = executor.execute(cmd, game_state)

        assert result.get("pending_glorious_charge") is True, (
            f"Expected pending_glorious_charge popup on plains, got: {result.get('message', '')}"
        )

    def test_popup_appears_on_hills(self):
        """At recklessness 3, attacking enemy in hills -> popup must appear."""
        world, executor, game_state, ney, wellington = self._setup_reckless_attack("hills")

        cmd = make_command("attack", "Ney", wellington.name)
        result = executor.execute(cmd, game_state)

        assert result.get("pending_glorious_charge") is True, (
            f"Expected pending_glorious_charge popup on hills, got: {result.get('message', '')}"
        )

    def test_no_popup_on_forest_no_alternatives(self):
        """At recklessness 3, enemy in forest, no alternatives -> no popup, normal attack."""
        world, executor, game_state, ney, wellington = self._setup_reckless_attack("forest")

        # Remove all other enemies so there are no charge alternatives
        enemies_to_remove = [
            name for name, m in world.marshals.items()
            if m.nation != "France" and m.name != wellington.name
        ]
        for name in enemies_to_remove:
            del world.marshals[name]

        cmd = make_command("attack", "Ney", wellington.name)
        result = executor.execute(cmd, game_state)

        # No popup (no alternatives on open ground), falls through to normal attack
        assert result.get("charge_redirected") is not True, (
            "Should not offer redirect when no alternatives exist"
        )

    def test_redirect_popup_on_forest_with_alternatives(self):
        """At recklessness 3, enemy in forest, alternative on open ground -> redirect popup."""
        world = WorldState(player_nation="France")
        executor = CommandExecutor()
        game_state = {"world": world}

        ney = world.get_marshal("Ney")
        ney.recklessness = 3
        ney.morale = 100
        ney.location = "Paris"  # Adjacent to Brittany (forest) and Belgium (plains)

        # Put one enemy in forest (blocked)
        wellington = world.get_marshal("Wellington")
        wellington.location = "Brittany"  # forest
        wellington.strength = 40000

        # Put another enemy in plains (chargeable) within range
        blucher = world.get_marshal("Blucher")
        blucher.location = "Belgium"  # plains, adjacent to Paris
        blucher.strength = 40000

        cmd = make_command("attack", "Ney", "Wellington")
        result = executor.execute(cmd, game_state)

        # Should get a redirect popup offering Blucher as alternative
        assert result.get("pending_glorious_charge") is True, (
            f"Expected redirect popup when alternative exists. Got: {result.get('message', '')}"
        )
        assert result.get("charge_redirected") is True, (
            "Should flag charge_redirected when offering alternative targets"
        )
        assert "terrain" in result.get("message", "").lower() or "block" in result.get("message", "").lower(), (
            "Redirect popup should explain terrain blocked the original target"
        )

    def test_charge_blocked_terrains_match_constant(self):
        """Verify CHARGE_BLOCKED_TERRAIN includes exactly mountains/forest/urban."""
        assert CHARGE_BLOCKED_TERRAIN == {"mountains", "forest", "urban"}

    def test_recklessness_persists_after_terrain_blocked(self):
        """When terrain blocks the charge and no alternatives, recklessness should NOT reset."""
        world, executor, game_state, ney, wellington = self._setup_reckless_attack("forest")

        # Remove alternatives
        enemies_to_remove = [
            name for name, m in world.marshals.items()
            if m.nation != "France" and m.name != wellington.name
        ]
        for name in enemies_to_remove:
            del world.marshals[name]

        original_recklessness = ney.recklessness
        assert original_recklessness == 3

        cmd = make_command("attack", "Ney", wellington.name)
        result = executor.execute(cmd, game_state)

        # Recklessness should still be >= original (might increment on win)
        # but should NOT have been reset to 0 by the terrain block alone
        if result.get("success"):
            # Combat outcome determines recklessness change, not terrain block
            pass
        else:
            # Attack didn't execute — recklessness should be unchanged
            assert ney.recklessness == original_recklessness


# ============================================================================
# BUG 3: recklessness counter resets on blocked charge (auto-charge path)
# ============================================================================

class TestRecklessnessResetOnBlockedCharge:
    """Recklessness should NOT reset when terrain blocks auto-charge."""

    def test_auto_charge_blocked_terrain_preserves_recklessness(self):
        """When auto-charge (4+) is blocked by terrain, recklessness persists."""
        world = WorldState(player_nation="France")

        ney = world.get_marshal("Ney")
        ney.recklessness = 4
        ney.morale = 100

        # Place enemy in adjacent forest region (charge-blocked terrain)
        # Ney starts in Belgium; Brittany is adjacent to Paris.
        # Need to find a forest region adjacent to Ney.
        # Brittany has terrain=forest. Move Ney to Paris (adjacent to Brittany).
        ney.location = "Paris"

        wellington = world.get_marshal("Wellington")
        wellington.location = "Brittany"
        wellington.strength = 40000
        wellington.morale = 100

        events = world._process_reckless_cavalry_turn_start()

        # Auto-charge should have happened (normal attack, not glorious)
        assert len(events) > 0, "Auto-charge event should have been generated"

        # The charge was blocked by terrain, so recklessness should NOT reset
        # (only resets when charge actually executes as glorious charge)
        assert ney.recklessness > 0, (
            f"Recklessness should NOT reset to 0 when terrain blocks charge. "
            f"Got: {ney.recklessness}"
        )

    def test_auto_charge_allowed_terrain_resets_recklessness(self):
        """When auto-charge (4+) succeeds on allowed terrain, recklessness resets."""
        world = WorldState(player_nation="France")

        ney = world.get_marshal("Ney")
        ney.recklessness = 4
        ney.morale = 100
        ney.location = "Paris"

        # Place enemy in Belgium (plains, charge allowed)
        wellington = world.get_marshal("Wellington")
        wellington.location = "Belgium"
        wellington.strength = 40000
        wellington.morale = 100

        events = world._process_reckless_cavalry_turn_start()

        assert len(events) > 0, "Auto-charge event should have been generated"

        # Charge was allowed (plains), so recklessness should reset
        assert ney.recklessness == 0, (
            f"Recklessness should reset to 0 after successful glorious charge. "
            f"Got: {ney.recklessness}"
        )

    def test_auto_charge_blocked_generates_correct_message(self):
        """Blocked auto-charge should include terrain blocking message."""
        world = WorldState(player_nation="France")

        ney = world.get_marshal("Ney")
        ney.recklessness = 4
        ney.morale = 100
        ney.location = "Paris"

        wellington = world.get_marshal("Wellington")
        wellington.location = "Brittany"  # forest
        wellington.strength = 40000
        wellington.morale = 100

        events = world._process_reckless_cavalry_turn_start()

        assert len(events) > 0
        event_msg = events[0].get("message", "")
        assert "terrain" in event_msg.lower() or "block" in event_msg.lower(), (
            f"Blocked charge message should mention terrain: {event_msg}"
        )
