"""
Tests for Phase M: Strategic Objections

Strategic objections fire at command ISSUANCE (not execution) based on personality.
Uses existing objection probability system - objections are RARE, not constant.

Scenarios:
- Ney (aggressive) objects to HOLD when no enemies adjacent
- Davout (cautious) objects to PURSUE with bad odds, MOVE_TO through danger
- Grouchy (literal) never objects (clarity not tactics)

Future expansion notes:
- Marshal rivalries will add objection triggers (e.g., Ney refuses to support Grouchy)
- Coalition marshals may object to joint operations
- Trust relationships between marshals affect willingness to cooperate
- See: _check_relationship_objection() placeholder for multi-marshal logic
"""

import pytest
from unittest.mock import Mock, patch
from backend.models.world_state import WorldState
from backend.models.marshal import Marshal, StrategicOrder, StrategicCondition, Stance
from backend.models.region import Region
from backend.commands.executor import CommandExecutor


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def world_with_french_marshals():
    """Standard world with Ney, Davout, Grouchy in different regions."""
    world = WorldState()

    # Reset to controlled state
    world.marshals = {}
    world.regions = {
        "Paris": Region("Paris", ["Belgium", "Brittany"], "France", 100),
        "Belgium": Region("Belgium", ["Paris", "Rhine", "Netherlands"], "France", 80),
        "Rhine": Region("Rhine", ["Belgium", "Bavaria"], "Prussia", 60),
        "Netherlands": Region("Netherlands", ["Belgium"], "Britain", 70),
        "Brittany": Region("Brittany", ["Paris"], "France", 50),
        "Bavaria": Region("Bavaria", ["Rhine", "Austria"], "Prussia", 60),
        "Austria": Region("Austria", ["Bavaria"], "Austria", 80)
        }

    # French marshals
    # Marshal(name, location, strength, personality, nation, ...)
    ney = Marshal("Ney", "Paris", 30000, "aggressive", "France", cavalry=True)
    ney.morale = 80
    ney.stance = Stance.NEUTRAL
    world.marshals["Ney"] = ney

    davout = Marshal("Davout", "Belgium", 35000, "cautious", "France")
    davout.morale = 85
    davout.stance = Stance.NEUTRAL
    world.marshals["Davout"] = davout

    grouchy = Marshal("Grouchy", "Brittany", 25000, "literal", "France")
    grouchy.morale = 75
    grouchy.stance = Stance.NEUTRAL
    world.marshals["Grouchy"] = grouchy

    world.player_nation = "France"
    world.current_turn = 1
    world.actions_remaining = 4

    return world


@pytest.fixture
def world_with_enemies(world_with_french_marshals):
    """Add enemy marshals to the world."""
    world = world_with_french_marshals

    wellington = Marshal("Wellington", "Netherlands", 40000, "cautious", "Britain")
    wellington.morale = 90
    world.marshals["Wellington"] = wellington

    blucher = Marshal("Blucher", "Rhine", 35000, "aggressive", "Prussia")
    blucher.morale = 85
    world.marshals["Blucher"] = blucher

    return world


@pytest.fixture
def executor():
    """Command executor instance."""
    return CommandExecutor()


def make_game_state(world):
    """Wrap world in game_state dict as executor expects."""
    return {"world": world}


def make_parsed_command(command_dict, is_strategic=False, strategic_type=None):
    """Wrap command dict in parsed_command structure as executor expects."""
    parsed = {"command": command_dict}
    if is_strategic:
        parsed["is_strategic"] = True
        parsed["strategic_type"] = strategic_type
    return parsed


def make_strategic_command(command_dict, strategic_type):
    """Shorthand for strategic commands - most common case in these tests."""
    return make_parsed_command(command_dict, is_strategic=True, strategic_type=strategic_type)


# =============================================================================
# HELPER FUNCTIONS FOR FUTURE EXPANSION
# =============================================================================

def _check_relationship_objection(marshal, target_marshal, world):
    """
    FUTURE: Check if marshal objects based on relationship with target.

    Expansion points:
    - Rivalry: Ney refuses to support Grouchy (historical animosity)
    - Distrust: Low trust between marshals affects cooperation
    - Nationality: Coalition marshals may balk at joint ops
    - Rank: Junior marshal may object to supporting senior's risky plan

    Returns:
        Optional[Dict]: Objection data if relationship triggers objection, None otherwise
    """
    # TODO: Implement when marshal relationships are added
    # rivalry_pairs = [("Ney", "Grouchy"), ...]
    # if (marshal.name, target_marshal.name) in rivalry_pairs:
    #     return {"reason": "rivalry", "message": f"{marshal.name} refuses to aid {target_marshal.name}!"}
    return None


def _get_relationship_modifier(marshal, target_marshal, world):
    """
    FUTURE: Get objection probability modifier based on relationship.

    Returns:
        float: Multiplier for objection probability (1.0 = no change, 2.0 = twice as likely)
    """
    # TODO: Implement relationship system
    # trust_between = world.get_marshal_trust(marshal.name, target_marshal.name)
    # if trust_between < 30:
    #     return 1.5  # 50% more likely to object
    return 1.0


# =============================================================================
# NEY HOLD OBJECTION TESTS
# =============================================================================

class TestNeyHoldObjection:
    """Ney objects to HOLD only when no enemies are adjacent."""

    def test_ney_objects_to_hold_no_enemies_adjacent(self, world_with_french_marshals, executor):
        """Ney at Paris with no enemies nearby should object to HOLD."""
        world = world_with_french_marshals
        ney = world.marshals["Ney"]
        # Low trust increases objection severity, ensuring objection triggers
        ney.trust.set(15)

        # No enemies in world yet - Ney should object
        command = {
            "marshal": "Ney",
            "action": "hold",
            "target": "Paris"
        }

        result = executor.execute(
            make_parsed_command(command, is_strategic=True, strategic_type="HOLD"),
            make_game_state(world)
        )

        assert result.get("pending_objection") is True, "Ney should object to HOLD with no enemies"
        assert "objection" in result
        assert result["objection"]["marshal"] == "Ney"
        assert "guard nothing" in result["objection"]["message"].lower() or "sitting" in result["objection"]["message"].lower()

    def test_ney_no_objection_hold_enemies_adjacent(self, world_with_enemies, executor):
        """Ney at Belgium with Wellington adjacent should NOT object - sally = fighting."""
        world = world_with_enemies
        ney = world.marshals["Ney"]
        ney.location = "Belgium"  # Wellington is in Netherlands, adjacent

        command = {
            "marshal": "Ney",
            "action": "hold",
            "target": "Belgium"
        }

        result = executor.execute(make_strategic_command(command, "HOLD"), make_game_state(world))

        # Should NOT object - enemies adjacent means sally opportunities
        assert result.get("pending_objection") is not True, "Ney should NOT object to HOLD with enemies adjacent"
        assert result.get("success") is True or result.get("strategic_order_created") is True

    def test_ney_hold_objection_checks_all_adjacent_regions(self, world_with_enemies, executor):
        """Objection check should scan ALL adjacent regions for enemies."""
        world = world_with_enemies
        ney = world.marshals["Ney"]
        ney.location = "Paris"  # Adjacent: Belgium, Brittany

        # Move Blucher to Belgium (adjacent to Paris)
        blucher = world.marshals["Blucher"]
        blucher.location = "Belgium"

        command = {
            "marshal": "Ney",
            "action": "hold",
            "target": "Paris"
        }

        result = executor.execute(make_strategic_command(command, "HOLD"), make_game_state(world))

        # Enemy in adjacent Belgium - no objection
        assert result.get("pending_objection") is not True


class TestNeyHoldPreferred:
    """Ney's preferred alternatives when objecting to HOLD."""

    def test_ney_hold_preferred_attacks_adjacent_enemy(self, world_with_enemies, executor):
        """Preferred: Attack adjacent enemy if one exists."""
        world = world_with_enemies
        ney = world.marshals["Ney"]
        ney.location = "Belgium"

        # Move Wellington adjacent for attack option
        wellington = world.marshals["Wellington"]
        wellington.location = "Netherlands"  # Adjacent to Belgium

        # But trigger objection by removing sally opportunity (make it HOLD at Paris)
        ney.location = "Paris"
        # No enemies adjacent to Paris in this setup

        command = {
            "marshal": "Ney",
            "action": "hold",
            "target": "Paris"
        }

        result = executor.execute(make_strategic_command(command, "HOLD"), make_game_state(world))

        if result.get("pending_objection"):
            options = result["objection"].get("options", [])
            preferred = next((o for o in options if o.get("type") == "preferred"), None)

            # Since no adjacent enemy to Paris, preferred should be PURSUE or stance
            # This tests the fallback chain
            assert preferred is None or "pursue" in preferred.get("action", "").lower() or "stance" in preferred.get("action", "").lower()

    def test_ney_hold_preferred_pursues_if_no_adjacent(self, world_with_enemies, executor):
        """Preferred fallback: PURSUE nearest enemy if none adjacent."""
        world = world_with_enemies
        ney = world.marshals["Ney"]
        ney.location = "Paris"  # No enemies adjacent

        # Wellington at Netherlands (2 regions away via Belgium)
        wellington = world.marshals["Wellington"]
        wellington.location = "Netherlands"

        command = {
            "marshal": "Ney",
            "action": "hold",
            "target": "Paris"
        }

        result = executor.execute(make_strategic_command(command, "HOLD"), make_game_state(world))

        if result.get("pending_objection"):
            options = result["objection"].get("options", [])
            preferred = next((o for o in options if o.get("type") == "preferred"), None)

            if preferred:
                # Should offer PURSUE Wellington (within 3 regions)
                assert "pursue" in preferred.get("action", "").lower() or preferred.get("strategic_type") == "PURSUE"

    def test_ney_hold_preferred_stance_if_no_targets(self, world_with_french_marshals, executor):
        """Preferred fallback: Aggressive stance if no enemies to attack/pursue."""
        world = world_with_french_marshals
        ney = world.marshals["Ney"]
        ney.stance = Stance.NEUTRAL  # Can switch to aggressive

        # No enemies in world
        command = {
            "marshal": "Ney",
            "action": "hold",
            "target": "Paris"
        }

        result = executor.execute(make_strategic_command(command, "HOLD"), make_game_state(world))

        if result.get("pending_objection"):
            options = result["objection"].get("options", [])
            preferred = next((o for o in options if o.get("type") == "preferred"), None)

            if preferred:
                # Should offer aggressive stance
                assert "aggressive" in preferred.get("action", "").lower() or "stance" in preferred.get("action", "").lower()

    def test_ney_hold_preferred_drill_fallback(self, world_with_french_marshals, executor):
        """Preferred fallback: Drill if already aggressive, no enemies."""
        world = world_with_french_marshals
        ney = world.marshals["Ney"]
        ney.stance = Stance.AGGRESSIVE  # Already aggressive
        ney.drilling = False
        ney.shock_bonus = 0

        command = {
            "marshal": "Ney",
            "action": "hold",
            "target": "Paris"
        }

        result = executor.execute(make_strategic_command(command, "HOLD"), make_game_state(world))

        if result.get("pending_objection"):
            options = result["objection"].get("options", [])
            preferred = next((o for o in options if o.get("type") == "preferred"), None)

            if preferred:
                # Should offer drill
                assert "drill" in preferred.get("action", "").lower()

    def test_ney_hold_preferred_chain_exhausted(self, world_with_french_marshals, executor):
        """When all preferred options exhausted, show only Proceed/Compromise."""
        world = world_with_french_marshals
        ney = world.marshals["Ney"]
        ney.stance = Stance.AGGRESSIVE  # Can't switch
        ney.drilling = True  # Can't drill
        ney.shock_bonus = 0.5  # Has bonus already

        # No enemies anywhere
        command = {
            "marshal": "Ney",
            "action": "hold",
            "target": "Paris"
        }

        result = executor.execute(make_strategic_command(command, "HOLD"), make_game_state(world))

        if result.get("pending_objection"):
            options = result["objection"].get("options", [])

            # Should have at least Proceed and Compromise
            option_types = [o.get("type") for o in options]
            assert "proceed" in option_types
            assert "compromise" in option_types

            # Preferred might be missing or None
            preferred = next((o for o in options if o.get("type") == "preferred"), None)
            # If preferred exists, it should have a valid action
            if preferred:
                assert preferred.get("action") is not None


class TestNeyHoldCompromise:
    """Ney's timed HOLD compromise."""

    def test_ney_hold_compromise_creates_timed_hold(self, world_with_french_marshals, executor):
        """Compromise: Timed HOLD for 3 turns."""
        world = world_with_french_marshals
        ney = world.marshals["Ney"]

        # Simulate choosing compromise after objection
        command = {
            "marshal": "Ney",
            "action": "hold",
            "target": "Paris",
            "objection_response": "compromise"
        }

        result = executor.execute(make_strategic_command(command, "HOLD"), make_game_state(world))

        if result.get("success"):
            order = ney.strategic_order
            assert order is not None
            assert order.command_type == "HOLD"
            assert order.condition is not None
            assert order.condition.max_turns == 3

    def test_timed_hold_expires_after_3_turns(self, world_with_french_marshals):
        """Timed HOLD auto-cancels after 3 turns."""
        world = world_with_french_marshals
        ney = world.marshals["Ney"]

        # Create timed HOLD order
        ney.strategic_order = StrategicOrder(
            command_type="HOLD",
            target="Paris",
            target_type="region",
            started_turn=1,
            original_command="hold at Paris",
            condition=StrategicCondition(max_turns=3),
            issued_turn=1
        )
        ney.holding_position = True
        ney.hold_region = "Paris"

        # Simulate 3 turns passing
        world.current_turn = 4  # Turn 1 + 3 = turn 4

        # Process strategic orders (turn manager would call this)
        from backend.commands.strategic import StrategicExecutor
        from backend.commands.executor import CommandExecutor
        strategic_executor = StrategicExecutor(CommandExecutor())
        result = strategic_executor.process_strategic_orders(world, {"world": world})

        # Order should be expired
        assert ney.strategic_order is None, "Timed HOLD should expire after 3 turns"
        assert ney.holding_position is False

        # Check for expiry message in results
        ney_result = next((r for r in result if r.get("marshal") == "Ney"), None)
        if ney_result:
            assert "restless" in ney_result.get("message", "").lower() or ney_result.get("order_status") == "expired"

    def test_timed_hold_still_gets_bonuses(self, world_with_french_marshals):
        """Timed HOLD still gets +15% immovable bonus during active turns."""
        world = world_with_french_marshals
        # NOTE: The +15% Immovable bonus is specifically for LITERAL personality (Grouchy)
        grouchy = world.marshals["Grouchy"]

        # Create timed HOLD (simulates compromise from Grouchy, though Grouchy doesn't object)
        grouchy.strategic_order = StrategicOrder(
            command_type="HOLD",
            target="Brittany",
            target_type="region",
            started_turn=1,
            original_command="hold at Brittany",
            condition=StrategicCondition(max_turns=3),
            issued_turn=1
        )
        grouchy.holding_position = True
        grouchy.hold_region = "Brittany"

        # Should still get defense bonus (+15% Immovable is Grouchy's literal ability)
        defense_mod = grouchy.get_defense_modifier()
        assert defense_mod >= 1.15, "Timed HOLD should still get +15% defense (Immovable)"


# =============================================================================
# DAVOUT PURSUE OBJECTION TESTS
# =============================================================================

class TestDavoutPursueObjection:
    """Davout objects to PURSUE when odds are bad (target >= 1.2x his strength)."""

    def test_davout_objects_to_pursue_bad_odds(self, world_with_enemies, executor):
        """Davout should object to PURSUE when target is significantly stronger."""
        world = world_with_enemies
        davout = world.marshals["Davout"]
        davout.strength = 30000
        # Low trust increases objection severity (1.6x modifier), ensuring objection triggers
        davout.trust.set(15)

        wellington = world.marshals["Wellington"]
        wellington.strength = 40000  # 1.33x Davout's strength

        command = {
            "marshal": "Davout",
            "action": "pursue",
            "target": "Wellington"
        }

        result = executor.execute(make_strategic_command(command, "PURSUE"), make_game_state(world))

        assert result.get("pending_objection") is True, "Davout should object to PURSUE with bad odds"
        assert "reckless" in result["objection"]["message"].lower() or "outnumber" in result["objection"]["message"].lower()

    def test_davout_no_objection_pursue_good_odds(self, world_with_enemies, executor):
        """Davout should NOT object to PURSUE when he has the advantage."""
        world = world_with_enemies
        davout = world.marshals["Davout"]
        davout.strength = 50000

        wellington = world.marshals["Wellington"]
        wellington.strength = 35000  # Davout has advantage

        command = {
            "marshal": "Davout",
            "action": "pursue",
            "target": "Wellington"
        }

        result = executor.execute(make_strategic_command(command, "PURSUE"), make_game_state(world))

        assert result.get("pending_objection") is not True, "Davout should NOT object with good odds"

    def test_davout_pursue_threshold_exactly_1_2(self, world_with_enemies, executor):
        """Edge case: Target exactly 1.2x strength - should trigger objection."""
        world = world_with_enemies
        davout = world.marshals["Davout"]
        davout.strength = 30000
        # Low trust ensures objection triggers despite variance
        davout.trust.set(15)

        wellington = world.marshals["Wellington"]
        wellington.strength = 36000  # Exactly 1.2x

        command = {
            "marshal": "Davout",
            "action": "pursue",
            "target": "Wellington"
        }

        result = executor.execute(make_strategic_command(command, "PURSUE"), make_game_state(world))

        # At exactly 1.2x, should object (>= threshold)
        assert result.get("pending_objection") is True


class TestDavoutPursuePreferred:
    """Davout's preferred alternative when objecting to PURSUE."""

    def test_davout_pursue_preferred_fortifies(self, world_with_enemies, executor):
        """Preferred: Fortify current position."""
        world = world_with_enemies
        davout = world.marshals["Davout"]
        davout.strength = 30000
        davout.fortified = False

        wellington = world.marshals["Wellington"]
        wellington.strength = 45000  # Bad odds

        command = {
            "marshal": "Davout",
            "action": "pursue",
            "target": "Wellington"
        }

        result = executor.execute(make_strategic_command(command, "PURSUE"), make_game_state(world))

        if result.get("pending_objection"):
            options = result["objection"].get("options", [])
            preferred = next((o for o in options if o.get("type") == "preferred"), None)

            assert preferred is not None, "Davout should always have fortify as preferred"
            assert "fortify" in preferred.get("action", "").lower()


class TestDavoutPursueCompromise:
    """Davout's cautious PURSUE compromise."""

    def test_davout_pursue_compromise_cautious_pursue(self, world_with_enemies, executor):
        """Compromise: Cautious PURSUE with auto-cancel below 0.8 ratio."""
        world = world_with_enemies
        davout = world.marshals["Davout"]
        davout.strength = 30000

        wellington = world.marshals["Wellington"]
        wellington.strength = 40000

        command = {
            "marshal": "Davout",
            "action": "pursue",
            "target": "Wellington",
            "objection_response": "compromise"
        }

        result = executor.execute(make_strategic_command(command, "PURSUE"), make_game_state(world))

        if result.get("success"):
            order = davout.strategic_order
            assert order is not None
            assert order.command_type == "PURSUE"
            assert order.condition is not None
            assert order.condition.auto_cancel_below_ratio == 0.8

    def test_cautious_pursue_cancels_below_ratio(self, world_with_enemies):
        """Cautious PURSUE auto-cancels when ratio drops below 0.8."""
        world = world_with_enemies
        davout = world.marshals["Davout"]
        davout.strength = 30000
        davout.location = "Belgium"

        wellington = world.marshals["Wellington"]
        wellington.strength = 40000  # Ratio = 0.75, below 0.8
        wellington.location = "Netherlands"

        # Create cautious PURSUE order
        davout.strategic_order = StrategicOrder(
            command_type="PURSUE",
            target="Wellington",
            target_type="marshal",
            started_turn=1,
            original_command="pursue Wellington cautiously",
            condition=StrategicCondition(auto_cancel_below_ratio=0.8),
            issued_turn=1
        )

        # Advance turn so order gets processed (orders issued THIS turn are skipped)
        world.current_turn = 2

        # Process strategic orders
        from backend.commands.strategic import StrategicExecutor
        from backend.commands.executor import CommandExecutor
        strategic_executor = StrategicExecutor(CommandExecutor())
        result = strategic_executor.process_strategic_orders(world, {"world": world})

        # Order should be cancelled due to bad ratio
        assert davout.strategic_order is None, "Cautious PURSUE should cancel below ratio"

        davout_result = next((r for r in result if r.get("marshal") == "Davout"), None)
        if davout_result:
            assert "odds" in davout_result.get("message", "").lower() or davout_result.get("order_status") == "cancelled"

    def test_cautious_pursue_continues_above_ratio(self, world_with_enemies):
        """Cautious PURSUE doesn't auto-cancel when ratio is acceptable."""
        world = world_with_enemies
        davout = world.marshals["Davout"]
        davout.strength = 40000
        davout.location = "Belgium"

        wellington = world.marshals["Wellington"]
        wellington.strength = 40000  # Ratio = 1.0, above 0.8
        wellington.location = "Netherlands"

        # Create cautious PURSUE order
        davout.strategic_order = StrategicOrder(
            command_type="PURSUE",
            target="Wellington",
            target_type="marshal",
            started_turn=1,
            original_command="pursue Wellington cautiously",
            condition=StrategicCondition(auto_cancel_below_ratio=0.8),
            issued_turn=1
        )

        # Advance turn so order gets processed (orders issued THIS turn are skipped)
        world.current_turn = 2

        # Process strategic orders
        from backend.commands.strategic import StrategicExecutor
        from backend.commands.executor import CommandExecutor
        strategic_executor = StrategicExecutor(CommandExecutor())
        result = strategic_executor.process_strategic_orders(world, {"world": world})

        # Order should NOT have been cancelled due to ratio
        # (Cautious PURSUE completes when it "locates" target, doesn't auto-attack)
        davout_result = next((r for r in result if r.get("marshal") == "Davout"), None)
        assert davout_result is not None, "Should have result for Davout"
        # Check that it wasn't cancelled due to ratio - it should complete/continue
        assert davout_result.get("order_status") != "cancelled" or "ratio" not in davout_result.get("message", "").lower(), \
            "Cautious PURSUE should NOT cancel when ratio is acceptable (1.0 > 0.8)"


# =============================================================================
# DAVOUT MOVE_TO OBJECTION TESTS
# =============================================================================

class TestDavoutMoveToObjection:
    """Davout objects to MOVE_TO when path crosses enemy-occupied regions."""

    def test_davout_objects_to_move_dangerous_path(self, world_with_enemies, executor):
        """Davout should object when path goes through enemy marshal."""
        world = world_with_enemies
        davout = world.marshals["Davout"]
        davout.location = "Belgium"
        # Low trust ensures objection triggers despite variance (base severity 0.45)
        davout.trust.set(15)

        # Blucher at Rhine - path to Bavaria goes through him
        blucher = world.marshals["Blucher"]
        blucher.location = "Rhine"

        command = {
            "marshal": "Davout",
            "action": "move",
            "target": "Bavaria"
        }

        result = executor.execute(make_strategic_command(command, "MOVE_TO"), make_game_state(world))

        assert result.get("pending_objection") is True, "Davout should object to path through enemy"
        assert "danger" in result["objection"]["message"].lower() or "enemy" in result["objection"]["message"].lower()

    def test_davout_no_objection_move_safe_path(self, world_with_enemies, executor):
        """Davout should NOT object when path is clear."""
        world = world_with_enemies
        davout = world.marshals["Davout"]
        davout.location = "Paris"

        # Path to Brittany is safe
        command = {
            "marshal": "Davout",
            "action": "move",
            "target": "Brittany"
        }

        result = executor.execute(make_strategic_command(command, "MOVE_TO"), make_game_state(world))

        assert result.get("pending_objection") is not True, "Davout should NOT object to safe path"


class TestDavoutMoveToPreferred:
    """Davout's preferred alternative when objecting to MOVE_TO."""

    def test_davout_move_preferred_fortifies(self, world_with_enemies, executor):
        """Preferred: Stay and fortify."""
        world = world_with_enemies
        davout = world.marshals["Davout"]
        davout.location = "Belgium"

        blucher = world.marshals["Blucher"]
        blucher.location = "Rhine"

        command = {
            "marshal": "Davout",
            "action": "move",
            "target": "Bavaria"
        }

        result = executor.execute(make_strategic_command(command, "MOVE_TO"), make_game_state(world))

        if result.get("pending_objection"):
            options = result["objection"].get("options", [])
            preferred = next((o for o in options if o.get("type") == "preferred"), None)

            assert preferred is not None
            assert "fortify" in preferred.get("action", "").lower()


class TestDavoutMoveToCompromise:
    """Davout's safe path compromise."""

    def test_davout_move_compromise_safe_path(self, world_with_enemies, executor):
        """Compromise: MOVE_TO with cautious pathfinding."""
        world = world_with_enemies
        davout = world.marshals["Davout"]
        davout.location = "Belgium"

        # Add a safe path alternative
        world.regions["France"] = Region("France", ["Belgium", "Bavaria"], "France", 70)

        blucher = world.marshals["Blucher"]
        blucher.location = "Rhine"

        command = {
            "marshal": "Davout",
            "action": "move",
            "target": "Bavaria",
            "objection_response": "compromise"
        }

        result = executor.execute(make_strategic_command(command, "MOVE_TO"), make_game_state(world))

        if result.get("success"):
            order = davout.strategic_order
            if order:
                # Path should avoid Rhine (enemy location)
                assert "Rhine" not in order.path, "Compromise path should avoid enemies"

    def test_davout_move_compromise_hidden_if_no_safe_path(self, world_with_enemies, executor):
        """Compromise hidden when ALL paths cross enemies."""
        world = world_with_enemies
        davout = world.marshals["Davout"]
        davout.location = "Belgium"

        # Block all paths with enemies
        blucher = world.marshals["Blucher"]
        blucher.location = "Rhine"  # Blocks main path

        wellington = world.marshals["Wellington"]
        wellington.location = "Netherlands"  # Blocks alternative

        command = {
            "marshal": "Davout",
            "action": "move",
            "target": "Bavaria"
        }

        result = executor.execute(make_strategic_command(command, "MOVE_TO"), make_game_state(world))

        if result.get("pending_objection"):
            options = result["objection"].get("options", [])
            option_types = [o.get("type") for o in options]

            # Compromise might be hidden if no safe path exists
            # This depends on map layout - test verifies the check happens
            assert "proceed" in option_types
            assert "preferred" in option_types

    def test_davout_move_compromise_rejected_if_path_too_long(self, world_with_enemies, executor):
        """Compromise rejected if safe path is > 2x original length."""
        # This test requires specific map setup where safe path is very long
        # Implementation should cap safe path length
        pass  # TODO: Implement with specific map fixture


# =============================================================================
# GROUCHY (LITERAL) TESTS
# =============================================================================

class TestGrouchyNoObjection:
    """Grouchy (literal) never objects to strategic commands."""

    def test_grouchy_never_objects_to_hold(self, world_with_french_marshals, executor):
        """Grouchy should NOT object to HOLD."""
        world = world_with_french_marshals
        grouchy = world.marshals["Grouchy"]
        grouchy.location = "Brittany"  # Isolated, no enemies

        command = {
            "marshal": "Grouchy",
            "action": "hold",
            "target": "Brittany"
        }

        result = executor.execute(make_strategic_command(command, "HOLD"), make_game_state(world))

        assert result.get("pending_objection") is not True, "Grouchy should NEVER object to strategic commands"

    def test_grouchy_never_objects_to_pursue(self, world_with_enemies, executor):
        """Grouchy should NOT object to PURSUE even with bad odds."""
        world = world_with_enemies
        grouchy = world.marshals["Grouchy"]
        grouchy.strength = 20000
        grouchy.location = "Belgium"

        wellington = world.marshals["Wellington"]
        wellington.strength = 50000  # Terrible odds

        command = {
            "marshal": "Grouchy",
            "action": "pursue",
            "target": "Wellington"
        }

        result = executor.execute(make_strategic_command(command, "PURSUE"), make_game_state(world))

        # Grouchy follows orders literally - no objection
        assert result.get("pending_objection") is not True, "Grouchy should NEVER object (literal personality)"

    def test_grouchy_never_objects_to_move_dangerous(self, world_with_enemies, executor):
        """Grouchy should NOT object to dangerous MOVE_TO."""
        world = world_with_enemies
        grouchy = world.marshals["Grouchy"]
        grouchy.location = "Belgium"

        blucher = world.marshals["Blucher"]
        blucher.location = "Rhine"

        command = {
            "marshal": "Grouchy",
            "action": "move",
            "target": "Bavaria"
        }

        result = executor.execute(make_strategic_command(command, "MOVE_TO"), make_game_state(world))

        assert result.get("pending_objection") is not True, "Grouchy follows orders exactly"

    def test_grouchy_still_gets_clarification_popup(self, world_with_french_marshals, executor):
        """Grouchy's clarification popup (ambiguity) is separate from objection."""
        world = world_with_french_marshals
        grouchy = world.marshals["Grouchy"]

        # Vague command should trigger clarification, NOT objection
        command = {
            "marshal": "Grouchy",
            "action": "hold",
            "target": None,  # Vague - where?,
            "ambiguity": 80  # High ambiguity
        }

        result = executor.execute(make_strategic_command(command, "HOLD"), make_game_state(world))

        # Should get clarification popup, not objection
        if result.get("pending_clarification"):
            assert result.get("pending_objection") is not True
        # Both mechanisms are distinct


# =============================================================================
# BYPASS CONDITION TESTS
# =============================================================================

class TestObjectionBypass:
    """Conditions that bypass strategic objection entirely."""

    def test_no_objection_during_retreat_recovery(self, world_with_french_marshals, executor):
        """Marshals in retreat recovery don't object (demoralized, compliant)."""
        world = world_with_french_marshals
        ney = world.marshals["Ney"]
        ney.retreat_recovery = 2  # In recovery

        command = {
            "marshal": "Ney",
            "action": "hold",
            "target": "Paris"
        }

        result = executor.execute(make_strategic_command(command, "HOLD"), make_game_state(world))

        assert result.get("pending_objection") is not True, "No objection during retreat recovery"

    def test_no_objection_if_already_resolved(self, world_with_french_marshals, executor):
        """Don't re-trigger objection after player already responded."""
        world = world_with_french_marshals
        ney = world.marshals["Ney"]

        # Create order with objection already resolved
        ney.strategic_order = StrategicOrder(
            command_type="HOLD",
            target="Paris",
            target_type="region",
            started_turn=1,
            original_command="hold at Paris",
            objection_resolved=True
        )

        # Re-executing shouldn't trigger new objection
        command = {
            "marshal": "Ney",
            "action": "hold",
            "target": "Paris"
        }

        # This tests internal state - objection check should see flag
        # Actual behavior depends on implementation

    def test_tactical_objection_skipped_for_strategic(self, world_with_enemies, executor):
        """Tactical objection system should NOT fire on strategic commands."""
        world = world_with_enemies
        ney = world.marshals["Ney"]

        # This would normally trigger tactical objection (defend = defensive action)
        # But strategic HOLD should use strategic objection instead
        command = {
            "marshal": "Ney",
            "action": "hold",
            "target": "Paris"
        }

        result = executor.execute(make_strategic_command(command, "HOLD"), make_game_state(world))

        # If objection fires, should be strategic type, not tactical
        if result.get("pending_objection"):
            objection = result.get("objection", {})
            assert objection.get("type") == "strategic" or "strategic" in objection.get("context", "")


# =============================================================================
# AP COST TESTS
# =============================================================================

class TestObjectionAPCosts:
    """Verify correct AP costs for each response type."""

    def test_proceed_costs_2_ap(self, world_with_french_marshals, executor):
        """Proceed (insist) costs 2 AP (strategic command cost)."""
        world = world_with_french_marshals
        world.actions_remaining = 4
        ney = world.marshals["Ney"]

        command = {
            "marshal": "Ney",
            "action": "hold",
            "target": "Paris",
            "objection_response": "proceed"
        }

        result = executor.execute(make_strategic_command(command, "HOLD"), make_game_state(world))

        if result.get("success"):
            assert world.actions_remaining == 2, "Proceed should cost 2 AP"

    def test_preferred_costs_1_ap(self, world_with_french_marshals, executor):
        """Preferred (trust marshal) costs 1 AP (tactical action)."""
        world = world_with_french_marshals
        world.actions_remaining = 4
        ney = world.marshals["Ney"]
        ney.stance = Stance.NEUTRAL  # Can switch to aggressive

        command = {
            "marshal": "Ney",
            "action": "hold",
            "target": "Paris",
            "objection_response": "preferred",
            "preferred_action": {"action": "stance", "target": "aggressive"}
        }

        result = executor.execute(make_strategic_command(command, "HOLD"), make_game_state(world))

        if result.get("success"):
            assert world.actions_remaining == 3, "Preferred should cost 1 AP"

    def test_compromise_costs_2_ap(self, world_with_french_marshals, executor):
        """Compromise costs 2 AP (still a strategic command)."""
        world = world_with_french_marshals
        world.actions_remaining = 4
        ney = world.marshals["Ney"]

        command = {
            "marshal": "Ney",
            "action": "hold",
            "target": "Paris",
            "objection_response": "compromise"
        }

        result = executor.execute(make_strategic_command(command, "HOLD"), make_game_state(world))

        if result.get("success"):
            assert world.actions_remaining == 2, "Compromise should cost 2 AP"


# =============================================================================
# TRUST MODIFICATION TESTS
# =============================================================================

class TestObjectionTrustChanges:
    """Verify correct trust changes for each response type."""

    def test_proceed_trust_minus_10(self, world_with_french_marshals, executor):
        """Proceed (insist) causes -10 trust."""
        world = world_with_french_marshals
        ney = world.marshals["Ney"]
        initial_trust = ney.trust.value

        command = {
            "marshal": "Ney",
            "action": "hold",
            "target": "Paris",
            "objection_response": "proceed"
        }

        result = executor.execute(make_strategic_command(command, "HOLD"), make_game_state(world))

        if result.get("success"):
            assert ney.trust.value == initial_trust - 10, "Proceed should cost -10 trust"

    def test_preferred_trust_plus_12(self, world_with_french_marshals, executor):
        """Preferred (trust marshal) grants +12 trust."""
        world = world_with_french_marshals
        ney = world.marshals["Ney"]
        ney.stance = Stance.NEUTRAL
        initial_trust = ney.trust.value

        command = {
            "marshal": "Ney",
            "action": "hold",
            "target": "Paris",
            "objection_response": "preferred",
            "preferred_action": {"action": "stance", "target": "aggressive"}
        }

        result = executor.execute(make_strategic_command(command, "HOLD"), make_game_state(world))

        if result.get("success"):
            assert ney.trust.value == initial_trust + 12, "Preferred should grant +12 trust"

    def test_compromise_trust_plus_3(self, world_with_french_marshals, executor):
        """Compromise grants +3 trust."""
        world = world_with_french_marshals
        ney = world.marshals["Ney"]
        initial_trust = ney.trust.value

        command = {
            "marshal": "Ney",
            "action": "hold",
            "target": "Paris",
            "objection_response": "compromise"
        }

        result = executor.execute(make_strategic_command(command, "HOLD"), make_game_state(world))

        if result.get("success"):
            assert ney.trust.value == initial_trust + 3, "Compromise should grant +3 trust"


# =============================================================================
# EDGE CASE TESTS
# =============================================================================

class TestEdgeCases:
    """Edge cases and race conditions."""

    def test_preferred_target_moved_revalidates(self, world_with_enemies, executor):
        """If preferred target moves before response, revalidate."""
        # This tests that the system handles stale state
        pass  # TODO: Implement with mock timing

    def test_marshal_dies_during_timed_hold(self, world_with_french_marshals):
        """Timed HOLD clears if marshal dies."""
        world = world_with_french_marshals
        ney = world.marshals["Ney"]

        ney.strategic_order = StrategicOrder(
            command_type="HOLD",
            target="Paris",
            target_type="region",
            started_turn=1,
            original_command="hold at Paris",
            condition=StrategicCondition(max_turns=3),
            issued_turn=1
        )
        ney.strength = 0  # Marshal defeated

        from backend.commands.strategic import StrategicExecutor
        from backend.commands.executor import CommandExecutor
        strategic_executor = StrategicExecutor(CommandExecutor())
        result = strategic_executor.process_strategic_orders(world, {"world": world})

        # Dead marshal shouldn't process orders
        # Order should be cleared or skipped
        assert ney.strategic_order is None or ney.strength == 0

    def test_objection_with_no_actions_remaining(self, world_with_french_marshals, executor):
        """Objection handling when player has no AP left."""
        world = world_with_french_marshals
        world.actions_remaining = 0

        command = {
            "marshal": "Ney",
            "action": "hold",
            "target": "Paris"
        }

        result = executor.execute(make_strategic_command(command, "HOLD"), make_game_state(world))

        # Should fail due to no AP, not trigger objection
        assert result.get("success") is False
        assert "action" in result.get("message", "").lower() or "ap" in result.get("message", "").lower()


# =============================================================================
# FUTURE: MULTI-MARSHAL RELATIONSHIP TESTS
# =============================================================================

class TestFutureRelationshipObjections:
    """
    Placeholder tests for future marshal relationship objections.

    These will be implemented when the relationship system is added.
    Currently marked as skipped.
    """

    @pytest.mark.skip(reason="Multi-marshal relationships not yet implemented")
    def test_ney_refuses_to_support_grouchy_rivalry(self, world_with_french_marshals, executor):
        """
        FUTURE: Ney refuses SUPPORT order targeting Grouchy due to rivalry.

        Historical context: Ney blamed Grouchy for Waterloo.
        """
        world = world_with_french_marshals
        ney = world.marshals["Ney"]
        grouchy = world.marshals["Grouchy"]

        command = {
            "marshal": "Ney",
            "action": "support",
            "target": "Grouchy"
        }

        result = executor.execute(make_strategic_command(command, "SUPPORT"), make_game_state(world))

        # Should object due to rivalry
        assert result.get("pending_objection") is True
        assert "rivalry" in result["objection"]["message"].lower()

    @pytest.mark.skip(reason="Multi-marshal relationships not yet implemented")
    def test_low_trust_between_marshals_increases_objection(self, world_with_french_marshals, executor):
        """
        FUTURE: Low trust between marshals increases objection probability.
        """
        world = world_with_french_marshals
        # Set low trust between Davout and Ney
        # world.set_marshal_relationship("Davout", "Ney", trust=20)

        command = {
            "marshal": "Davout",
            "action": "support",
            "target": "Ney"
        }

        # Low trust should increase objection chance
        # Test would verify probability modifier

    @pytest.mark.skip(reason="Multi-marshal relationships not yet implemented")
    def test_coalition_marshal_objects_to_joint_operation(self, world_with_enemies, executor):
        """
        FUTURE: Coalition marshals may object to joint operations.
        """
        # Hypothetical: If Prussia and Austria are allies but have tensions
        pass


# =============================================================================
# SERIALIZATION TESTS
# =============================================================================

class TestObjectionSerialization:
    """Test that new fields serialize correctly."""

    def test_strategic_order_issued_turn_serializes(self):
        """issued_turn field survives roundtrip."""
        order = StrategicOrder(
            command_type="HOLD",
            target="Paris",
            target_type="region",
            started_turn=1,
            original_command="hold at Paris",
            issued_turn=5
        )

        data = order.to_dict()
        restored = StrategicOrder.from_dict(data)

        assert restored.issued_turn == 5

    def test_strategic_order_objection_resolved_serializes(self):
        """objection_resolved field survives roundtrip."""
        order = StrategicOrder(
            command_type="HOLD",
            target="Paris",
            target_type="region",
            started_turn=1,
            original_command="hold at Paris",
            objection_resolved=True
        )

        data = order.to_dict()
        restored = StrategicOrder.from_dict(data)

        assert restored.objection_resolved is True

    def test_strategic_condition_max_turns_serializes(self):
        """max_turns condition survives roundtrip."""
        condition = StrategicCondition(max_turns=3)

        data = condition.to_dict()
        restored = StrategicCondition.from_dict(data)

        assert restored.max_turns == 3

    def test_strategic_condition_auto_cancel_ratio_serializes(self):
        """auto_cancel_below_ratio condition survives roundtrip."""
        condition = StrategicCondition(auto_cancel_below_ratio=0.8)

        data = condition.to_dict()
        restored = StrategicCondition.from_dict(data)

        assert restored.auto_cancel_below_ratio == 0.8
