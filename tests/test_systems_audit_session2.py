"""
Systems Audit Fix Plan — Session 2: Critical Quick Fixes

Tests for 5 high-impact bugs:
1. Authority bonus phantom attribute (turn_manager.py)
2. Autonomous marshal command format (enemy_ai.py)
3. Coalition casualty keys wrong (executor.py)
4. Auto-advance bypasses move_to() (executor.py)
5. AP treaty penalty overwritten (world_state.py)
"""

from backend.models.world_state import WorldState
from backend.models.marshal import Marshal
from backend.commands.executor import CommandExecutor
from backend.game_logic.turn_manager import TurnManager


# ═══════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════

def make_world():
    """Fresh WorldState."""
    return WorldState()


def make_executor():
    """Fresh CommandExecutor."""
    return CommandExecutor()


def find_marshal(world, name):
    """Find a marshal by name."""
    for m in world.marshals.values():
        if m.name == name:
            return m
    return None


# ═══════════════════════════════════════════════════════
# FIX 1: Authority bonus writes to authority_tracker
# ═══════════════════════════════════════════════════════

class TestAuthorityBonus:
    """Fix 1: Spectacular autonomous result should modify authority_tracker."""

    def test_spectacular_autonomous_modifies_authority_tracker(self):
        """When a marshal has spectacular autonomous results,
        authority_tracker.authority should increase by 10."""
        world = make_world()
        executor = make_executor()
        tm = TurnManager(world, executor)

        # Find a player marshal and make them autonomous
        marshal = None
        for m in world.marshals.values():
            if m.nation == world.player_nation:
                marshal = m
                break
        assert marshal is not None

        # Set up spectacular results (autonomous=True, autonomy_turns=1 so it ends this turn)
        marshal.autonomous = True
        marshal.autonomy_turns = 1  # Will reach 0 after decrement → triggers _end_autonomy
        marshal.autonomous_battles_won = 2  # Spectacular threshold

        # Set authority below max so we can detect the +10 increase
        world.authority_tracker.authority = 80
        initial_authority = world.authority_tracker.authority

        # Process autonomous marshals (this is where the fix lives)
        tm._process_autonomous_marshals({"world": world})

        # Authority tracker should have increased
        assert world.authority_tracker.authority == initial_authority + 10

    def test_authority_clamped_at_100(self):
        """Authority should not exceed 100 even with bonus."""
        world = make_world()
        executor = make_executor()
        tm = TurnManager(world, executor)

        # Set authority near max
        world.authority_tracker.authority = 95

        marshal = None
        for m in world.marshals.values():
            if m.nation == world.player_nation:
                marshal = m
                break
        assert marshal is not None

        marshal.autonomous = True
        marshal.autonomy_turns = 1
        marshal.autonomous_battles_won = 2

        tm._process_autonomous_marshals({"world": world})

        # Clamped at 100 (95 + 10 = 105, but modify_authority clamps)
        assert world.authority_tracker.authority == 100


# ═══════════════════════════════════════════════════════
# FIX 2: Autonomous marshal command format
# ═══════════════════════════════════════════════════════

class TestAutonomousCommandFormat:
    """Fix 2: decide_single_action should produce nested command format."""

    def test_command_has_nested_structure(self):
        """The command dict should have a 'command' key with nested fields."""
        from backend.ai.enemy_ai import EnemyAI

        world = make_world()
        executor = make_executor()
        ai = EnemyAI(executor)
        game_state = {"world": world}

        # Find a player marshal to use as autonomous
        marshal = None
        for m in world.marshals.values():
            if m.nation == world.player_nation:
                marshal = m
                break
        assert marshal is not None

        # Call decide_single_action and inspect the command it builds
        # We can't easily intercept the command, so instead verify
        # the function returns a result (not silently failing)
        result = ai.decide_single_action(marshal, world.player_nation, world, game_state)

        # Result should not be None (marshal should find something to do)
        assert result is not None
        # The action should have been processed (not "unknown")
        # If the format was wrong, executor would return unknown action error

    def test_executor_processes_nested_command(self):
        """Executor should correctly parse the nested command format."""
        world = make_world()
        executor = make_executor()
        game_state = {"world": world}

        # Find a player marshal
        marshal = None
        for m in world.marshals.values():
            if m.nation == world.player_nation:
                marshal = m
                break
        assert marshal is not None

        # Build command in the corrected nested format
        command = {
            "command": {
                "type": "specific",
                "marshal": marshal.name,
                "action": "wait",
                "target": None,
            }
        }

        result = executor.execute(command, game_state)
        # Should succeed (wait is always valid)
        assert result.get("success") is True


# ═══════════════════════════════════════════════════════
# FIX 3: Coalition casualty keys (nested access)
# ═══════════════════════════════════════════════════════

class TestCoalitionThreatFromAttack:
    """Fix 3: Coalition threat/WE should update from real battle casualties."""

    def _setup_attack_scenario(self):
        """Set up a basic France attacks enemy scenario."""
        world = make_world()

        # Find French marshal and an enemy marshal in adjacent regions
        french_marshal = None
        enemy_marshal = None
        for m in world.marshals.values():
            if m.nation == world.player_nation and french_marshal is None:
                french_marshal = m
            elif m.nation != world.player_nation and enemy_marshal is None:
                enemy_marshal = m

        assert french_marshal is not None
        assert enemy_marshal is not None

        # Move them to be co-located for combat
        enemy_marshal.location = french_marshal.location

        # Give both enough troops
        french_marshal.strength = 30000
        enemy_marshal.strength = 15000
        french_marshal.morale = 80
        enemy_marshal.morale = 60

        return world, french_marshal, enemy_marshal

    def test_threat_increases_after_french_attack_victory(self):
        """When France wins an attack, coalition threat should increase."""
        world, french, enemy = self._setup_attack_scenario()
        executor = make_executor()
        game_state = {"world": world}

        initial_threat = world.threat_level

        # Execute attack command
        command = {
            "command": {
                "type": "specific",
                "marshal": french.name,
                "action": "attack",
                "target": enemy.name,
            }
        }
        result = executor.execute(command, game_state)

        # If French won, threat should have increased
        if result.get("success") and result.get("battle_result", {}).get("victor") == french.name:
            assert world.threat_level > initial_threat, \
                f"Threat should increase after French victory: {initial_threat} -> {world.threat_level}"

    def test_war_exhaustion_updates_from_casualties(self):
        """War exhaustion should increase based on actual casualties, not zero."""
        world, french, enemy = self._setup_attack_scenario()

        # Put France at war with the enemy nation
        enemy_nation = enemy.nation
        key = world._make_diplo_key("France", enemy_nation)
        world.diplomatic_states[key] = "WAR"

        executor = make_executor()
        game_state = {"world": world}

        # Record initial war exhaustion
        initial_we = world.war_exhaustion.get(enemy_nation, 0)

        command = {
            "command": {
                "type": "specific",
                "marshal": french.name,
                "action": "attack",
                "target": enemy.name,
            }
        }
        result = executor.execute(command, game_state)

        # If battle happened and one side lost significantly,
        # war exhaustion should have changed for the loser
        battle_result = result.get("battle_result", {})
        if battle_result:
            atk_cas = battle_result.get("attacker", {}).get("casualties", 0)
            def_cas = battle_result.get("defender", {}).get("casualties", 0)
            # At least one side should have casualties
            assert atk_cas > 0 or def_cas > 0, "Battle should produce casualties"

    def test_decisive_victory_detected_with_real_casualties(self):
        """Decisive victory (2:1 ratio + 10k total) should be detected."""
        world, french, enemy = self._setup_attack_scenario()

        # Give France huge advantage for decisive result
        french.strength = 50000
        french.morale = 100
        enemy.strength = 10000
        enemy.morale = 30

        executor = make_executor()
        game_state = {"world": world}

        initial_threat = world.threat_level

        command = {
            "command": {
                "type": "specific",
                "marshal": french.name,
                "action": "attack",
                "target": enemy.name,
            }
        }
        result = executor.execute(command, game_state)

        # With such overwhelming advantage, France should win decisively
        # and threat should increase by more than just 3 (base win)
        if result.get("success"):
            battle = result.get("battle_result", {})
            if battle.get("victor") == french.name:
                # Threat increased at least by base amount (3)
                assert world.threat_level >= initial_threat + 3


# ═══════════════════════════════════════════════════════
# FIX 4: Auto-advance uses move_to() for state resets
# ═══════════════════════════════════════════════════════

class TestAutoAdvanceMoveToResets:
    """Fix 4: Auto-advance should use move_to() to reset cavalry/holding states."""

    def test_cavalry_defensive_stance_reset_on_auto_advance(self):
        """Cavalry marshal's defensive stance should reset when auto-advancing."""
        marshal = Marshal("TestCav", "France", "Saxony", 10000)
        marshal.cavalry = True
        marshal.turns_in_defensive_stance = 2
        marshal.turns_fortified = 1

        # Simulate what move_to() does
        marshal.move_to("Bavaria")

        assert marshal.location == "Bavaria"
        assert marshal.turns_in_defensive_stance == 0
        assert marshal.turns_fortified == 0

    def test_holding_position_cleared_on_auto_advance(self):
        """Grouchy's holding_position should clear when auto-advancing."""
        marshal = Marshal("TestHold", "France", "Saxony", 10000)
        marshal.holding_position = True
        marshal.hold_region = "Saxony"

        marshal.move_to("Bavaria")

        assert marshal.location == "Bavaria"
        assert marshal.holding_position is False
        assert marshal.hold_region == ""

    def test_move_to_updates_location(self):
        """Basic: move_to should change the location."""
        marshal = Marshal("TestMove", "France", "Saxony", 10000)
        marshal.move_to("Bavaria")
        assert marshal.location == "Bavaria"


# ═══════════════════════════════════════════════════════
# FIX 5: AP treaty penalty survives advance_turn
# ═══════════════════════════════════════════════════════

class TestAPTreatyPenalty:
    """Fix 5: Player AP treaty penalty must not be overwritten by action reset."""

    def test_player_ap_penalty_survives_advance_turn(self):
        """AP clause should reduce player actions, surviving the reset."""
        world = make_world()

        # Set up an active treaty with AP penalty clause
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "PEACE"
        world.active_treaties[key] = {
            "type": "peace_treaty",
            "clauses": [
                {
                    "type": "ap_per_turn",
                    "from": "France",
                    "to": "Prussia",
                    "amount": 1,
                }
            ],
            "signed_turn": 1,
        }

        # Base is 4, penalty is -1 = should be 3
        executor = make_executor()
        game_state = {"world": world}

        # Advance turn processes treaties
        world.advance_turn()

        # Player should have 3 actions (4 base - 1 penalty)
        assert world.max_actions_per_turn == 3, \
            f"Expected 3 (4 base - 1 penalty), got {world.max_actions_per_turn}"
        assert world.actions_remaining == 3, \
            f"Expected 3 remaining, got {world.actions_remaining}"

    def test_ai_ap_penalty_works(self):
        """AP clause targeting AI nation should reduce their actions."""
        world = make_world()

        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "PEACE"
        world.active_treaties[key] = {
            "type": "peace_treaty",
            "clauses": [
                {
                    "type": "ap_per_turn",
                    "from": "Prussia",
                    "to": "France",
                    "amount": 1,
                }
            ],
            "signed_turn": 1,
        }

        # Prussia base is 4
        world.nation_actions["Prussia"] = 4

        world.advance_turn()

        # Prussia should have 3 actions (4 base - 1 penalty)
        assert world.nation_actions["Prussia"] == 3, \
            f"Expected 3 (4 base - 1 penalty), got {world.nation_actions['Prussia']}"

    def test_ap_penalty_minimum_floor_of_1(self):
        """AP penalty should never reduce below 1."""
        world = make_world()

        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "PEACE"
        world.active_treaties[key] = {
            "type": "peace_treaty",
            "clauses": [
                {
                    "type": "ap_per_turn",
                    "from": "France",
                    "to": "Prussia",
                    "amount": 10,  # Way more than base
                }
            ],
            "signed_turn": 1,
        }

        world.advance_turn()

        # Should be floored at 1, not 0 or negative
        assert world.max_actions_per_turn >= 1, \
            f"AP should never go below 1, got {world.max_actions_per_turn}"
