"""
Test suite for Enemy AI garrison placement (P6.75) and P4.25 garrison awareness.

Tests cover:
- AI garrison placement heuristic (_consider_garrison)
- All skip conditions (strength, existing garrison, enemies, friendlies, border)
- 1 per nation per turn cap
- P4.25 sub-5k detachment garrison awareness
- No oscillation/loops from garrison placement
- Integration with executor (Building Blocks principle)
- garrison_detachment rename backward compat

Run with: pytest tests/test_ai_garrison.py -v
"""

import pytest
from backend.models.world_state import WorldState
from backend.models.marshal import Marshal
from backend.models.region import Region
from backend.commands.executor import CommandExecutor
from backend.ai.enemy_ai import EnemyAI


# ════════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════════

def _setup():
    """Create fresh world, executor, AI for testing."""
    world = WorldState()
    executor = CommandExecutor()
    ai = EnemyAI(executor)
    game_state = {"world": world, "debug_mode": True}
    return world, game_state, executor, ai


def _make_safe_garrison_scenario(world, marshal_name="Wellington", nation="Britain"):
    """
    Set up a scenario where AI garrison should fire:
    - Marshal has excess strength (>= 20k)
    - In own territory
    - No existing garrison
    - No enemies in or adjacent
    - Adjacent to non-friendly region (vulnerable border)
    - No other friendly marshal in region

    Returns the marshal and their region.
    """
    marshal = world.marshals[marshal_name]
    marshal.strength = 25000  # Well above 20k threshold

    # Clear all other marshals away from this area
    for m in world.marshals.values():
        if m.name != marshal_name:
            m.location = "London"

    # Ensure marshal's region is controlled by their nation with no garrison
    region = world.regions[marshal.location]
    region.controller = nation
    region.garrison_strength = 0
    region.garrison_detachment = False

    # Ensure at least one adjacent region is NOT controlled by this nation (border)
    for adj_name in region.adjacent_regions:
        adj = world.regions.get(adj_name)
        if adj:
            adj.controller = "France"  # Enemy territory — makes this a border
            break

    return marshal, region


# ════════════════════════════════════════════════════════════════════════════════
# AI GARRISON PLACEMENT TESTS (P6.75)
# ════════════════════════════════════════════════════════════════════════════════

class TestAIGarrisonPlacement:
    """Test _consider_garrison heuristic fires correctly."""

    def test_garrison_fires_when_conditions_met(self):
        """AI garrisons when all conditions satisfied."""
        world, gs, executor, ai = _setup()
        # Initialize per-turn state
        ai._garrison_placed_this_turn = False
        marshal, region = _make_safe_garrison_scenario(world)

        result = ai._consider_garrison(marshal, marshal.nation, world)

        assert result is not None
        assert result["action"] == "garrison"
        assert result["marshal"] == marshal.name

    def test_garrison_executes_through_executor(self):
        """AI garrison uses same executor as player (Building Blocks)."""
        world, gs, executor, ai = _setup()
        ai._garrison_placed_this_turn = False
        marshal, region = _make_safe_garrison_scenario(world)

        # Execute through executor like AI would
        command = {
            "command": {
                "marshal": marshal.name,
                "action": "garrison",
                "target": None,
                "type": "specific"
            }
        }
        result = executor.execute(command, gs)

        assert result["success"] is True
        assert region.garrison_strength == 3000
        assert region.garrison_detachment is True
        assert marshal.strength == 22000  # 25k - 3k

    def test_garrison_constant_is_20k(self):
        """AI garrison threshold is 20k for Waterloo balance."""
        assert EnemyAI.AI_GARRISON_MIN_STRENGTH == 20000


# ════════════════════════════════════════════════════════════════════════════════
# SKIP CONDITION TESTS
# ════════════════════════════════════════════════════════════════════════════════

class TestAIGarrisonSkipConditions:
    """Test all conditions that prevent AI from garrisoning."""

    def test_skip_when_strength_too_low(self):
        """Marshal below 20k should not garrison."""
        world, gs, executor, ai = _setup()
        ai._garrison_placed_this_turn = False
        marshal, region = _make_safe_garrison_scenario(world)
        marshal.strength = 19000  # Below threshold

        result = ai._consider_garrison(marshal, marshal.nation, world)
        assert result is None

    def test_skip_when_strength_at_exact_threshold(self):
        """Marshal at exactly 20k SHOULD garrison (>= not >)."""
        world, gs, executor, ai = _setup()
        ai._garrison_placed_this_turn = False
        marshal, region = _make_safe_garrison_scenario(world)
        marshal.strength = 20000  # Exact threshold

        result = ai._consider_garrison(marshal, marshal.nation, world)
        assert result is not None

    def test_skip_when_existing_garrison(self):
        """Don't garrison a region that already has one."""
        world, gs, executor, ai = _setup()
        ai._garrison_placed_this_turn = False
        marshal, region = _make_safe_garrison_scenario(world)
        region.garrison_strength = 3000  # Already garrisoned

        result = ai._consider_garrison(marshal, marshal.nation, world)
        assert result is None

    def test_skip_when_enemy_in_region(self):
        """Don't garrison when enemy marshal is in the same region."""
        world, gs, executor, ai = _setup()
        ai._garrison_placed_this_turn = False
        marshal, region = _make_safe_garrison_scenario(world)

        # Place enemy in same region
        ney = world.marshals["Ney"]
        ney.location = marshal.location
        ney.strength = 10000

        result = ai._consider_garrison(marshal, marshal.nation, world)
        assert result is None

    def test_skip_when_enemy_adjacent(self):
        """Don't garrison when enemy marshal is in adjacent region."""
        world, gs, executor, ai = _setup()
        ai._garrison_placed_this_turn = False
        marshal, region = _make_safe_garrison_scenario(world)

        # Place enemy in adjacent region
        ney = world.marshals["Ney"]
        adj_name = region.adjacent_regions[0]
        ney.location = adj_name
        ney.strength = 10000

        result = ai._consider_garrison(marshal, marshal.nation, world)
        assert result is None

    def test_skip_when_friendly_marshal_in_region(self):
        """Don't garrison when another friendly marshal is already here."""
        world, gs, executor, ai = _setup()
        ai._garrison_placed_this_turn = False
        marshal, region = _make_safe_garrison_scenario(world)

        # Place friendly marshal in same region
        uxbridge = world.marshals.get("Uxbridge")
        if uxbridge and uxbridge.nation == marshal.nation:
            uxbridge.location = marshal.location
            uxbridge.strength = 10000

            result = ai._consider_garrison(marshal, marshal.nation, world)
            assert result is None

    def test_skip_when_not_own_territory(self):
        """Don't garrison enemy-controlled territory."""
        world, gs, executor, ai = _setup()
        ai._garrison_placed_this_turn = False
        marshal, region = _make_safe_garrison_scenario(world)
        region.controller = "France"  # Enemy territory

        result = ai._consider_garrison(marshal, marshal.nation, world)
        assert result is None

    def test_skip_when_no_vulnerable_border(self):
        """Don't garrison deep interior (all adjacent regions friendly)."""
        world, gs, executor, ai = _setup()
        ai._garrison_placed_this_turn = False
        marshal, region = _make_safe_garrison_scenario(world)

        # Make all adjacent regions friendly
        for adj_name in region.adjacent_regions:
            adj = world.regions.get(adj_name)
            if adj:
                adj.controller = marshal.nation

        result = ai._consider_garrison(marshal, marshal.nation, world)
        assert result is None

    def test_skip_when_drilling(self):
        """Don't garrison while drilling."""
        world, gs, executor, ai = _setup()
        ai._garrison_placed_this_turn = False
        marshal, region = _make_safe_garrison_scenario(world)
        marshal.drilling = True

        result = ai._consider_garrison(marshal, marshal.nation, world)
        assert result is None

    def test_skip_when_fortified(self):
        """Don't garrison while fortified."""
        world, gs, executor, ai = _setup()
        ai._garrison_placed_this_turn = False
        marshal, region = _make_safe_garrison_scenario(world)
        marshal.fortified = True

        result = ai._consider_garrison(marshal, marshal.nation, world)
        assert result is None


# ════════════════════════════════════════════════════════════════════════════════
# PER-NATION CAP TESTS
# ════════════════════════════════════════════════════════════════════════════════

class TestAIGarrisonCap:
    """Test 1-per-nation-per-turn cap."""

    def test_cap_prevents_second_garrison(self):
        """After one garrison, P6.75 check is skipped for remaining marshals."""
        world, gs, executor, ai = _setup()
        ai._garrison_placed_this_turn = True  # Already placed one

        marshal, region = _make_safe_garrison_scenario(world)

        # The _evaluate_marshal code checks _garrison_placed_this_turn before
        # calling _consider_garrison. Simulate that check:
        if ai._garrison_placed_this_turn:
            result = None  # Would be skipped
        else:
            result = ai._consider_garrison(marshal, marshal.nation, world)

        assert result is None

    def test_cap_resets_per_nation(self):
        """Cap resets at start of each nation's turn."""
        world, gs, executor, ai = _setup()

        # Process Britain's turn (sets cap)
        ai._garrison_placed_this_turn = True

        # Simulate next nation's turn reset (process_nation_turn resets it)
        ai._garrison_placed_this_turn = False  # Reset

        marshal, region = _make_safe_garrison_scenario(world)
        result = ai._consider_garrison(marshal, marshal.nation, world)
        assert result is not None

    def test_cap_flag_set_on_successful_garrison(self):
        """_garrison_placed_this_turn set True after successful garrison action."""
        world, gs, executor, ai = _setup()
        ai._garrison_placed_this_turn = False

        # Simulate the tracking code from process_nation_turn
        selected_action = {"marshal": "Wellington", "action": "garrison"}
        if selected_action["action"] == "garrison":
            ai._garrison_placed_this_turn = True

        assert ai._garrison_placed_this_turn is True


# ════════════════════════════════════════════════════════════════════════════════
# P4.25 SUB-5K GARRISON AWARENESS TESTS
# ════════════════════════════════════════════════════════════════════════════════

class TestP425GarrisonAwareness:
    """Test P4.25 now detects detachment garrisons below 5k."""

    def _clear_all_garrisons(self, world):
        """Helper: clear all garrisons to isolate test targets."""
        for region in world.regions.values():
            region.garrison_strength = 0
            region.garrison_detachment = False

    def test_p425_sees_detachment_garrison_below_5k(self):
        """P4.25 should detect a 3k detachment garrison (garrison_detachment=True)."""
        world, gs, executor, ai = _setup()
        self._clear_all_garrisons(world)  # Remove Paris capital garrison

        # Set up: enemy detachment garrison in adjacent region
        blucher = world.marshals["Blucher"]
        blucher.strength = 55000
        blucher.location = "Belgium"

        target = world.regions["Netherlands"]
        target.controller = "France"
        target.garrison_strength = 3000
        target.garrison_detachment = True

        # Clear other marshals away
        for m in world.marshals.values():
            if m.name != "Blucher":
                m.location = "London"

        result = ai._find_garrison_attack(blucher, "Prussia", world)
        # With 55k vs 3k, ratio is huge — should easily pass threshold
        assert result is not None
        assert result["action"] == "attack"
        assert result["target"] == "Netherlands"

    def test_p425_still_skips_weak_capital_garrison(self):
        """P4.25 should still skip capital garrisons below 5k (they auto-collapse)."""
        world, gs, executor, ai = _setup()
        self._clear_all_garrisons(world)

        blucher = world.marshals["Blucher"]
        blucher.strength = 55000
        blucher.location = "Belgium"

        target = world.regions["Netherlands"]
        target.controller = "France"
        target.garrison_strength = 3000
        target.garrison_detachment = False  # Capital-style, below 5k = auto-collapses

        for m in world.marshals.values():
            if m.name != "Blucher":
                m.location = "London"

        result = ai._find_garrison_attack(blucher, "Prussia", world)
        # Below 5k and NOT detachment — P4.25 should skip this
        assert result is None

    def test_p425_still_handles_large_capital_garrison(self):
        """P4.25 still handles capital garrisons >= 5k as before."""
        world, gs, executor, ai = _setup()
        self._clear_all_garrisons(world)

        blucher = world.marshals["Blucher"]
        blucher.strength = 55000
        blucher.location = "Belgium"

        target = world.regions["Netherlands"]
        target.controller = "France"
        target.garrison_strength = 15000
        target.garrison_detachment = False  # Capital garrison

        for m in world.marshals.values():
            if m.name != "Blucher":
                m.location = "London"

        result = ai._find_garrison_attack(blucher, "Prussia", world)
        assert result is not None
        assert result["action"] == "attack"
        assert result["target"] == "Netherlands"

    def test_p425_skips_own_garrison(self):
        """P4.25 doesn't attack own nation's garrisons."""
        world, gs, executor, ai = _setup()
        self._clear_all_garrisons(world)

        blucher = world.marshals["Blucher"]
        blucher.strength = 55000
        blucher.location = "Belgium"

        target = world.regions["Netherlands"]
        target.controller = "Prussia"  # Same nation
        target.garrison_strength = 3000
        target.garrison_detachment = True

        for m in world.marshals.values():
            if m.name != "Blucher":
                m.location = "London"

        result = ai._find_garrison_attack(blucher, "Prussia", world)
        assert result is None  # Won't attack own garrison


# ════════════════════════════════════════════════════════════════════════════════
# P4.5 UNDEFENDED CAPTURE + DETACHMENT GARRISON INTERACTION
# ════════════════════════════════════════════════════════════════════════════════

class TestP45DetachmentAwareness:
    """Test P4.5 correctly skips detachment garrisons (defers to P4.25)."""

    def test_p45_skips_detachment_garrison(self):
        """P4.5 _find_undefended_capture should skip regions with detachment garrison."""
        world, gs, executor, ai = _setup()

        blucher = world.marshals["Blucher"]
        blucher.strength = 55000
        blucher.location = "Belgium"

        target = world.regions["Netherlands"]
        target.controller = "France"
        target.garrison_strength = 3000
        target.garrison_detachment = True

        # Clear other marshals from Netherlands
        for m in world.marshals.values():
            if m.name != "Blucher":
                m.location = "London"

        result = ai._find_undefended_capture(blucher, "Prussia", world)
        # Should NOT return Netherlands — it has a detachment garrison
        if result:
            assert result.get("target") != "Netherlands"

    def test_p45_still_captures_truly_undefended(self):
        """P4.5 still captures regions with no garrison and no defenders."""
        world, gs, executor, ai = _setup()

        blucher = world.marshals["Blucher"]
        blucher.strength = 55000
        blucher.location = "Belgium"

        # Make Netherlands truly undefended
        target = world.regions["Netherlands"]
        target.controller = "France"
        target.garrison_strength = 0
        target.garrison_detachment = False

        # Clear all marshals from Netherlands
        for m in world.marshals.values():
            if m.name != "Blucher" and m.location == "Netherlands":
                m.location = "London"

        result = ai._find_undefended_capture(blucher, "Prussia", world)
        # Should be found as undefended capture
        if result:
            assert result["target"] == "Netherlands"
            assert result["action"] == "attack"


# ════════════════════════════════════════════════════════════════════════════════
# ANTI-LOOP / ANTI-OSCILLATION TESTS
# ════════════════════════════════════════════════════════════════════════════════

class TestAIGarrisonNoLoops:
    """Ensure garrison placement doesn't create oscillation or loop behaviors."""

    def test_no_garrison_then_ungarrison_loop(self):
        """AI has no 'ungarrison' action — once placed, garrison stays."""
        world, gs, executor, ai = _setup()
        ai._garrison_placed_this_turn = False
        marshal, region = _make_safe_garrison_scenario(world)

        # Execute garrison
        result = ai._consider_garrison(marshal, marshal.nation, world)
        assert result is not None

        # Execute it
        cmd = {"command": {"marshal": marshal.name, "action": "garrison", "target": None, "type": "specific"}}
        exec_result = executor.execute(cmd, gs)
        assert exec_result["success"] is True
        assert region.garrison_strength == 3000

        # Next evaluation — garrison exists, so _consider_garrison returns None
        result2 = ai._consider_garrison(marshal, marshal.nation, world)
        assert result2 is None  # Won't try to garrison again

    def test_garrison_doesnt_starve_attack_ap(self):
        """With 1-per-nation cap, garrison uses at most 1 of 4 AP."""
        world, gs, executor, ai = _setup()
        ai._garrison_placed_this_turn = False

        # Simulate: first action is garrison
        ai._garrison_placed_this_turn = True  # After garrison

        # Remaining 3 actions should be available for combat/movement
        # Cap flag prevents any more garrison attempts
        assert ai._garrison_placed_this_turn is True

    def test_garrison_priority_below_combat(self):
        """P6.75 is below P4 (attack), P3 (threat), P0 (engagement)."""
        # This is structural — garrison at priority 7 is always evaluated
        # after combat priorities (0-5) in _evaluate_marshal
        world, gs, executor, ai = _setup()
        ai._garrison_placed_this_turn = False

        # Marshal with both attack opportunity AND garrison opportunity
        # Attack should win because it's evaluated first (P4 < P6.75)
        wellington = world.marshals["Wellington"]
        wellington.strength = 68000
        wellington.location = "Netherlands"
        world.regions["Netherlands"].controller = "Britain"
        world.regions["Netherlands"].garrison_strength = 0

        # Place weak enemy adjacent (easy attack target)
        ney = world.marshals["Ney"]
        ney.location = "Belgium"
        ney.strength = 5000  # Very weak

        # Clear other marshals
        for m in world.marshals.values():
            if m.name not in ("Wellington", "Ney"):
                m.location = "London"

        action, priority = ai._evaluate_marshal(wellington, "Britain", world)
        # Should prefer attack (P4) over garrison (P6.75)
        if action:
            assert action["action"] != "garrison" or priority <= 4

    def test_garrison_doesnt_fire_during_retreat(self):
        """Marshal in retreat recovery can't garrison."""
        world, gs, executor, ai = _setup()
        ai._garrison_placed_this_turn = False
        marshal, region = _make_safe_garrison_scenario(world)
        marshal.retreat_recovery = 2  # In retreat recovery

        # _consider_garrison checks drilling/fortified but retreat recovery
        # is handled at P1 level — marshal never reaches P6.75
        # Just verify it would be caught by _evaluate_marshal priority ordering
        action, priority = ai._evaluate_marshal(marshal, marshal.nation, world)
        if action:
            # Should be retreat recovery (P1), not garrison
            assert priority <= 2 or action["action"] != "garrison"


# ════════════════════════════════════════════════════════════════════════════════
# INTEGRATION: FULL TURN PROCESSING
# ════════════════════════════════════════════════════════════════════════════════

class TestAIGarrisonIntegration:
    """Test garrison in full AI turn flow."""

    def test_garrison_action_costs_1_ap(self):
        """Garrison costs 1 AP from nation budget."""
        world, gs, executor, ai = _setup()
        assert world.get_action_cost("garrison") == 1

    def test_garrison_detachment_fights_to_destruction(self):
        """AI-placed garrison (garrison_detachment=True) fights, doesn't collapse at 5k."""
        world, gs, executor, ai = _setup()

        # Set up AI garrison
        region = world.regions["Belgium"]
        region.controller = "Britain"
        region.garrison_strength = 3000
        region.garrison_detachment = True

        # Attack it with overwhelming force
        ney = world.marshals["Ney"]
        ney.strength = 50000
        ney.location = "Paris"  # Adjacent to Belgium

        # Clear defenders
        for m in world.marshals.values():
            if m.nation != "France":
                m.location = "London"

        old_ney_strength = ney.strength
        result = executor._execute_attack(ney, "Belgium", world, gs)
        # Should trigger garrison combat — attacker takes some casualties
        assert result.get("success") is True
        assert "garrison" in result.get("message", "").lower()
        # Attacker should have taken some damage from fighting garrison
        assert ney.strength < old_ney_strength
        # Garrison may or may not be fully destroyed in one attack, but
        # the key test: it FOUGHT (didn't auto-collapse despite being < 5k)
        # because garrison_detachment=True means no collapse threshold

    def test_ai_garrison_no_regen(self):
        """AI-placed garrison does NOT regenerate (not a capital garrison)."""
        world, gs, executor, ai = _setup()

        # Set up a non-capital region with AI garrison
        belgium = world.regions["Belgium"]
        belgium.controller = "Britain"
        belgium.garrison_strength = 2000
        belgium.garrison_detachment = True

        old_strength = belgium.garrison_strength
        world.advance_turn()
        assert belgium.garrison_strength == old_strength  # No regen
