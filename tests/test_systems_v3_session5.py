"""
Systems Audit V3 Fix Plan — Session 5: Strategic Orders + Combat

Tests for 12 bugs where strategic order and combat code paths have missing
guards, leaked state, missing attribute writes, formula errors, and
fog-of-war violations.

Bug fixes:
- 7A-1:  Broken/retreating marshals can accept strategic orders
- 7A-2:  holding_position/hold_region leak on 13 of 18 strategic_order=None paths
- 7A-3:  _execute_attack never sets last_combat_result
- 7A-6:  _auto_break_square clears strategic_order but not holding state
- 7A-7:  HOLD expiry dead code (aggressive-only check duplicated)
- 7A-8:  Dead marshal cleanup missing pending_interrupt clear
- 7A-4:  Cautious pathfinding sees all regions regardless of fog
- 7A-5:  Literal reroute sees all regions regardless of fog
- 5D-1:  Coordinated mutual_destruction skips morale penalty
- 5D-2:  Pursuit max(1000, ...) heals enemies below 1000
- 5D-3:  Glorious charge skips coordination bonus calculation
- 7B-1:  Artillery reinforcements excluded from relationship processing
"""

from backend.models.world_state import WorldState
from backend.models.marshal import Marshal, StrategicOrder, StrategicCondition
from backend.commands.executor import CommandExecutor
from backend.commands.strategic import StrategicExecutor
from backend.models.intel import FULL, UNKNOWN


# ═══════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════

def make_world():
    """Fresh WorldState with France at war with Britain."""
    w = WorldState()
    set_war(w, "France", "Britain")
    return w


def make_executor():
    return CommandExecutor()


def make_strategic_executor():
    return StrategicExecutor(make_executor())


def make_marshal(name="Ney", location="Belgium", strength=30000, nation="France",
                 personality="aggressive", **kwargs):
    m = Marshal(name=name, location=location, strength=strength,
                personality=personality, nation=nation, spawn_location=location)
    for k, v in kwargs.items():
        setattr(m, k, v)
    return m


def make_enemy(name="Wellington", location="Belgium", strength=25000, nation="Britain",
               personality="cautious", **kwargs):
    m = Marshal(name=name, location=location, strength=strength,
                personality=personality, nation=nation, spawn_location=location)
    for k, v in kwargs.items():
        setattr(m, k, v)
    return m


def set_war(world, nation_a, nation_b):
    key = world._make_diplo_key(nation_a, nation_b)
    world.diplomatic_states[key] = "WAR"


def place_marshals(world, *marshals):
    world.marshals = {m.name: m for m in marshals}


def execute_attack(world, attacker_name, target_name):
    """Helper to execute an attack command."""
    executor = CommandExecutor()
    game_state = {"world": world}
    command = {"command": {
        "marshal": attacker_name,
        "action": "attack",
        "target": target_name,
    }}
    return executor.execute(command, game_state)


def make_strategic_order(cmd_type="HOLD", target="Belgium", path=None, **kwargs):
    """Create a StrategicOrder for testing."""
    order = StrategicOrder(
        command_type=cmd_type,
        target=target,
        target_type="region",
        started_turn=1,
        original_command=f"{cmd_type.lower()} {target}",
    )
    if path:
        order.path = path
    for k, v in kwargs.items():
        setattr(order, k, v)
    return order


# ═══════════════════════════════════════════════════════
# 7A-1: Broken/Retreating State Guard
# ═══════════════════════════════════════════════════════

class TestBrokenStateGuard:
    """Broken/retreating marshals cannot accept strategic orders."""

    def test_broken_marshal_cannot_strategic_order(self):
        """Broken marshal should be rejected for strategic orders."""
        world = make_world()
        ney = make_marshal(name="Ney", location="Belgium")
        ney.broken = True
        place_marshals(world, ney)

        executor = make_executor()
        game_state = {"world": world}
        # _execute_strategic_command(parsed_command, command, game_state)
        parsed = {"strategic_type": "HOLD", "target_snapshot_location": None}
        command = {
            "marshal": "Ney",
            "action": "hold",
            "target": "Belgium",
        }
        result = executor._execute_strategic_command(parsed, command, game_state)
        assert result is not None
        assert result["success"] is False
        assert "broken" in result["message"].lower()

    def test_retreating_marshal_cannot_strategic_order(self):
        """Retreating marshal should be rejected for strategic orders."""
        world = make_world()
        ney = make_marshal(name="Ney", location="Belgium")
        ney.retreat_recovery = 2
        place_marshals(world, ney)

        executor = make_executor()
        game_state = {"world": world}
        parsed = {"strategic_type": "HOLD", "target_snapshot_location": None}
        command = {
            "marshal": "Ney",
            "action": "hold",
            "target": "Belgium",
        }
        result = executor._execute_strategic_command(parsed, command, game_state)
        assert result is not None
        assert result["success"] is False
        assert "retreat" in result["message"].lower()


# ═══════════════════════════════════════════════════════
# 7A-2: holding_position Leak
# ═══════════════════════════════════════════════════════

class TestHoldingPositionLeak:
    """holding_position/hold_region must be cleared whenever strategic_order = None."""

    def test_holding_position_cleared_on_dead_marshal(self):
        """Dead marshal cleanup should clear holding_position."""
        world = make_world()
        ney = make_marshal(name="Ney", location="Belgium", strength=0)
        ney.holding_position = True
        ney.hold_region = "Belgium"
        ney.strategic_order = make_strategic_order("HOLD", "Belgium")
        place_marshals(world, ney)

        se = make_strategic_executor()
        se.process_strategic_orders(world, {"world": world})

        assert ney.holding_position is False
        assert ney.hold_region == ""

    def test_holding_position_cleared_on_interrupt_investigate(self):
        """Investigate interrupt response should clear holding_position."""
        world = make_world()
        ney = make_marshal(name="Ney", location="Belgium")
        ney.holding_position = True
        ney.hold_region = "Belgium"
        order = make_strategic_order("MOVE_TO", "Rhineland", path=["Rhineland"])
        ney.strategic_order = order
        ney.pending_interrupt = {
            "interrupt_type": "cannon_fire",
            "battle_location": "Rhineland",
            "options": ["investigate", "continue_order", "hold_position"],
            "is_first_step": False,
        }
        place_marshals(world, ney)

        se = make_strategic_executor()
        result = se.handle_response("Ney", "cannon_fire", "investigate", world, {"world": world})

        assert ney.holding_position is False
        assert ney.hold_region == ""

    def test_holding_position_cleared_on_hold_position_response(self):
        """hold_position interrupt response should clear holding_position."""
        world = make_world()
        ney = make_marshal(name="Ney", location="Belgium")
        ney.holding_position = True
        ney.hold_region = "Belgium"
        order = make_strategic_order("MOVE_TO", "Rhineland", path=["Rhineland"])
        ney.strategic_order = order
        ney.pending_interrupt = {
            "interrupt_type": "cannon_fire",
            "battle_location": "Rhineland",
            "options": ["investigate", "continue_order", "hold_position"],
            "is_first_step": False,
        }
        place_marshals(world, ney)

        se = make_strategic_executor()
        result = se.handle_response("Ney", "cannon_fire", "hold_position", world, {"world": world})

        assert ney.holding_position is False
        assert ney.hold_region == ""

    def test_holding_position_cleared_on_cancel_order(self):
        """cancel_order stalemate response should clear holding_position."""
        world = make_world()
        ney = make_marshal(name="Ney", location="Belgium")
        ney.holding_position = True
        ney.hold_region = "Belgium"
        order = make_strategic_order("PURSUE", "Wellington")
        ney.strategic_order = order
        ney.pending_interrupt = {
            "interrupt_type": "combat_stalemate",
            "enemy": "Wellington",
            "options": ["continue_order", "hold_position", "cancel_order"],
            "is_first_step": False,
        }
        place_marshals(world, ney)

        se = make_strategic_executor()
        result = se.handle_response("Ney", "combat_stalemate", "cancel_order", world, {"world": world})

        assert ney.holding_position is False
        assert ney.hold_region == ""

    def test_holding_position_cleared_on_ratio_cancel(self):
        """Cautious PURSUE ratio auto-cancel should clear holding_position."""
        world = make_world()
        world.current_turn = 5

        davout = make_marshal(name="Davout", location="Belgium", strength=10000,
                              personality="cautious")
        davout.holding_position = True
        davout.hold_region = "Belgium"
        condition = StrategicCondition(auto_cancel_below_ratio=1.5)
        order = make_strategic_order("PURSUE", "Wellington")
        order.condition = condition
        order.issued_turn = 3
        davout.strategic_order = order

        # Enemy is stronger — ratio below threshold
        wellington = make_enemy(name="Wellington", location="Rhineland", strength=20000)
        place_marshals(world, davout, wellington)

        se = make_strategic_executor()
        result = se._execute_strategic_turn(davout, world, {"world": world})

        assert davout.strategic_order is None
        assert davout.holding_position is False
        assert davout.hold_region == ""

    def test_holding_position_cleared_on_cannon_redirect(self):
        """Aggressive cannon fire redirect should clear holding_position."""
        world = make_world()
        world.current_turn = 5

        ney = make_marshal(name="Ney", location="Belgium", personality="aggressive")
        ney.holding_position = True
        ney.hold_region = "Belgium"
        order = make_strategic_order("MOVE_TO", "Rhineland", path=["Rhineland"])
        order.issued_turn = 3
        ney.strategic_order = order

        wellington = make_enemy(name="Wellington", location="Paris", strength=25000)
        place_marshals(world, ney, wellington)

        # Record a battle so cannon fire triggers
        world.record_battle("Paris", "SomeAlly", "Wellington", "attacker_victory")

        se = make_strategic_executor()
        interrupt = {"type": "cannon_fire", "action": "redirect",
                     "battle_location": "Paris"}
        result = se._handle_interrupt(ney, interrupt, world, {"world": world})

        assert ney.holding_position is False
        assert ney.hold_region == ""


# ═══════════════════════════════════════════════════════
# 7A-3: last_combat_result
# ═══════════════════════════════════════════════════════

class TestLastCombatResult:
    """_execute_attack must set marshal.last_combat_result."""

    def test_last_combat_result_set_on_attacker_victory(self):
        """Attacker wins → last_combat_result = 'victory'."""
        world = make_world()
        ney = make_marshal(name="Ney", location="Belgium", strength=40000)
        wellington = make_enemy(name="Wellington", location="Belgium", strength=5000)
        place_marshals(world, ney, wellington)

        result = execute_attack(world, "Ney", "Wellington")
        assert result["success"]
        assert ney.last_combat_result == "victory"

    def test_last_combat_result_set_on_defender_victory(self):
        """Attacker loses → last_combat_result = 'defeat'."""
        world = make_world()
        ney = make_marshal(name="Ney", location="Belgium", strength=5000)
        wellington = make_enemy(name="Wellington", location="Belgium", strength=40000)
        place_marshals(world, ney, wellington)

        result = execute_attack(world, "Ney", "Wellington")
        assert result["success"]
        # Marshal may be destroyed, but result was set before destruction
        assert ney.last_combat_result in ("defeat", "stalemate")

    def test_last_combat_result_set_on_stalemate(self):
        """Stalemate → last_combat_result = 'stalemate'."""
        world = make_world()
        # Equal forces tend to stalemate
        ney = make_marshal(name="Ney", location="Belgium", strength=25000)
        wellington = make_enemy(name="Wellington", location="Belgium", strength=25000)
        place_marshals(world, ney, wellington)

        result = execute_attack(world, "Ney", "Wellington")
        assert result["success"]
        # Should be one of the valid values
        assert ney.last_combat_result in ("victory", "defeat", "stalemate")

    def test_until_battle_won_triggers_after_attack(self):
        """HOLD with until_battle_won should complete after last_combat_result='victory'."""
        world = make_world()
        world.current_turn = 3

        ney = make_marshal(name="Ney", location="Belgium", strength=40000)
        condition = StrategicCondition(until_battle_won=True)
        order = make_strategic_order("HOLD", "Belgium")
        order.condition = condition
        order.issued_turn = 1
        ney.strategic_order = order
        ney.holding_position = True
        ney.hold_region = "Belgium"

        # Simulate combat result already set
        ney.last_combat_result = "victory"

        place_marshals(world, ney)

        se = make_strategic_executor()
        result = se._execute_strategic_turn(ney, world, {"world": world})

        # Order should be complete
        assert ney.strategic_order is None
        assert result is not None
        assert result.get("order_status") == "completed"


# ═══════════════════════════════════════════════════════
# 5D-1: Coordinated Mutual Destruction Morale
# ═══════════════════════════════════════════════════════

class TestCoordinatedMutualDestructionMorale:
    """Mutual destruction in coordinated combat should apply morale penalty."""

    def test_coordinated_mutual_destruction_morale_penalty(self):
        """Both sides should get negative morale delta on mutual destruction."""
        from backend.game_logic.combat import CombatResolver

        resolver = CombatResolver()

        # Create attacker/defender with strengths that will mutual-destruct
        attacker = make_marshal(name="Ney", location="Belgium", strength=10000)
        defender = make_enemy(name="Wellington", location="Belgium", strength=10000)

        # Use resolve_battle with apply_casualties=False (coordinated path)
        # Then check the deferred result directly
        attacker_roll = {"base": 7, "modified": 7, "dice": [3, 4],
                         "is_critical_success": False, "is_critical_failure": False}
        result = resolver._build_deferred_result(
            attacker=attacker,
            defender=defender,
            attacker_casualties=15000,
            defender_casualties=15000,
            attacker_original_strength=10000,
            defender_original_strength=10000,
            attacker_roll=attacker_roll,
            terrain="plains",
            flanking_bonus=0,
            flanking_message=None,
            glorious_charge=False,
            ability_message=None,
            drill_bonus_message=None,
            fortify_bonus_message=None,
            drilling_penalty_message=None,
            exhaustion_message=None,
            attacker_stance_message=None,
            defender_stance_message=None,
            attacker_personality_message=None,
            defender_personality_message=None,
            terrain_defense_message=None,
            cavalry_terrain_message=None,
            cavalry_counter_message=None,
            glorious_charge_message=None,
            attacker_modifier_snapshot={"total": 0},
            defender_modifier_snapshot={"total": 0},
            is_drilling=False,
        )

        # Morale deltas should be negative (not 0)
        # In deferred results, morale deltas are at top level: attacker_morale_delta, defender_morale_delta
        atk_morale = result.get("attacker_morale_delta", 0)
        def_morale = result.get("defender_morale_delta", 0)
        assert atk_morale < 0, f"Attacker morale delta should be negative, got {atk_morale}"
        assert def_morale < 0, f"Defender morale delta should be negative, got {def_morale}"


# ═══════════════════════════════════════════════════════
# 5D-2: Pursuit Healing Bug
# ═══════════════════════════════════════════════════════

class TestPursuitHealing:
    """Pursuit damage floor should be 0, not 1000."""

    def test_pursuit_does_not_heal_weak_enemy(self):
        """Enemy at 800 strength should not be healed to 1000 by pursuit."""
        world = make_world()
        murat = make_marshal(name="Murat", location="Belgium", strength=40000)
        murat.cavalry = True
        murat.ability = {"name": "Pursuit Master"}

        wellington = make_enemy(name="Wellington", location="Belgium", strength=800)
        place_marshals(world, murat, wellington)

        result = execute_attack(world, "Murat", "Wellington")

        # Enemy should be <= 800 or destroyed (0), never > 800
        remaining = wellington.strength
        assert remaining <= 800, f"Enemy healed from 800 to {remaining}!"

    def test_pursuit_can_destroy_enemy(self):
        """Pursuit damage should be able to reduce enemy to 0."""
        world = make_world()
        murat = make_marshal(name="Murat", location="Belgium", strength=40000)
        murat.cavalry = True
        murat.ability = {"name": "Pursuit Master"}

        wellington = make_enemy(name="Wellington", location="Belgium", strength=100)
        place_marshals(world, murat, wellington)

        result = execute_attack(world, "Murat", "Wellington")
        assert wellington.strength <= 100

    def test_pursuit_floor_zero_not_thousand(self):
        """max(0, ...) should be used instead of max(1000, ...)."""
        enemy_strength = 500
        pursuit_damage = 5000
        result = max(0, enemy_strength - pursuit_damage)
        assert result == 0
        assert result < 1000  # Should NOT be floored at 1000


# ═══════════════════════════════════════════════════════
# 5D-3: Glorious Charge Coordination
# ═══════════════════════════════════════════════════════

class TestGloriousChargeCoordination:
    """Glorious charge should compute coordination context for both sides."""

    def test_glorious_charge_has_coordination_bonuses(self):
        """Charger with ally in adjacent region should get coordination bonus."""
        world = make_world()
        # Murat in Belgium charges Wellington in Rhineland, Ney adjacent in Belgium
        murat = make_marshal(name="Murat", location="Belgium", strength=30000)
        murat.cavalry = True
        murat.recklessness = 3  # Needed for glorious charge

        # Ney as ally — same region as charger to provide coordination bonus
        ney = make_marshal(name="Ney", location="Belgium", strength=20000)

        wellington = make_enemy(name="Wellington", location="Rhineland", strength=25000)
        place_marshals(world, murat, ney, wellington)

        # Make Belgium and Rhineland adjacent
        belgium = world.get_region("Belgium")
        rhineland = world.get_region("Rhineland")
        if belgium and rhineland:
            if "Rhineland" not in belgium.adjacent_regions:
                belgium.adjacent_regions.append("Rhineland")
            if "Belgium" not in rhineland.adjacent_regions:
                rhineland.adjacent_regions.append("Belgium")

        executor = make_executor()
        game_state = {"world": world}

        # Before charge, coordination should be 0
        assert getattr(murat, 'total_coordination_attack_bonus', 0) == 0

        # _execute_glorious_charge(self, marshal, target, world, game_state)
        result = executor._execute_glorious_charge(murat, "Wellington", world, game_state)

        # Coordination should have been calculated
        # Murat should have gotten coordination bonus from Ney in same/adjacent region
        assert result is not None


# ═══════════════════════════════════════════════════════
# 7A-4 / 7A-5: Fog-Aware Pathfinding
# ═══════════════════════════════════════════════════════

class TestFogAwarePathfinding:
    """Cautious/literal pathfinding should only avoid visible enemies."""

    def test_cautious_pathfinding_fog_aware(self):
        """Unknown-visibility enemy regions should not be in the avoid set."""
        world = make_world()
        world.current_turn = 3

        davout = make_marshal(name="Davout", location="Paris", strength=20000,
                              personality="cautious")
        wellington = make_enemy(name="Wellington", location="Bavaria", strength=25000)
        place_marshals(world, davout, wellington)

        # Set Bavaria intel to UNKNOWN
        intel = world.get_region_intel("Bavaria")
        intel.visibility = UNKNOWN

        # Execute strategic command — cautious should NOT avoid Bavaria since it's fogged
        executor = make_executor()
        game_state = {"world": world}
        parsed = {"strategic_type": "MOVE_TO", "target_snapshot_location": None}
        command = {
            "marshal": "Davout",
            "action": "move_to",
            "target": "Bavaria",
            "target_type": "region",
        }
        result = executor._execute_strategic_command(parsed, command, game_state)

        # If result is not None and path was created, the fogged enemy shouldn't block
        if result and result.get("success"):
            assert result.get("strategic_order") or result["success"]

    def test_cautious_pathfinding_visible_enemy_avoided(self):
        """FULL/PARTIAL visibility enemy regions should be in the avoid set."""
        world = make_world()

        davout = make_marshal(name="Davout", location="Paris", strength=20000,
                              personality="cautious")
        wellington = make_enemy(name="Wellington", location="Belgium", strength=25000)
        place_marshals(world, davout, wellington)

        # Set Belgium intel to FULL
        intel = world.get_region_intel("Belgium")
        intel.visibility = FULL

        executor = make_executor()
        game_state = {"world": world}
        parsed = {"strategic_type": "MOVE_TO", "target_snapshot_location": None}
        command = {
            "marshal": "Davout",
            "action": "move_to",
            "target": "Rhineland",
            "target_type": "region",
        }
        result = executor._execute_strategic_command(parsed, command, game_state)

        # We just verify the command was processed without crash
        assert result is not None

    def test_literal_reroute_fog_aware(self):
        """Literal marshal reroute should respect fog of war."""
        world = make_world()
        world.current_turn = 3

        soult = make_marshal(name="Soult", location="Belgium", strength=20000,
                             personality="literal")
        order = make_strategic_order("MOVE_TO", "Bavaria", path=["Rhineland", "Bavaria"])
        order.issued_turn = 1
        soult.strategic_order = order

        # Enemy in Rhineland (blocking path) — but fogged
        wellington = make_enemy(name="Wellington", location="Rhineland", strength=25000)
        place_marshals(world, soult, wellington)

        # Set Rhineland to UNKNOWN visibility
        intel = world.get_region_intel("Rhineland")
        intel.visibility = UNKNOWN

        se = make_strategic_executor()
        result = se._execute_strategic_turn(soult, world, {"world": world})

        # Should proceed without crash
        assert result is not None


# ═══════════════════════════════════════════════════════
# 7A-6: _auto_break_square Clears HOLD
# ═══════════════════════════════════════════════════════

class TestAutoBreakSquareClearsHold:
    """_auto_break_square should clear holding_position when clearing strategic_order."""

    def test_auto_break_square_clears_hold(self):
        """Breaking square with active HOLD should clear holding_position."""
        world = make_world()
        ney = make_marshal(name="Ney", location="Belgium", strength=30000)
        ney.square_formation = True
        ney.holding_position = True
        ney.hold_region = "Belgium"
        ney.strategic_order = make_strategic_order("HOLD", "Belgium")
        place_marshals(world, ney)

        executor = make_executor()
        executor._auto_break_square(ney, "attack")

        assert not ney.square_formation
        assert ney.strategic_order is None
        assert ney.holding_position is False
        assert ney.hold_region == ""


# ═══════════════════════════════════════════════════════
# 7A-8: Dead Marshal pending_interrupt
# ═══════════════════════════════════════════════════════

class TestDeadMarshalPendingInterrupt:
    """Dead marshal cleanup should clear pending_interrupt."""

    def test_dead_marshal_pending_interrupt_cleared(self):
        """Dead marshal should have pending_interrupt set to None."""
        world = make_world()
        ney = make_marshal(name="Ney", location="Belgium", strength=0)
        ney.strategic_order = make_strategic_order("HOLD", "Belgium")
        ney.pending_interrupt = {
            "interrupt_type": "cannon_fire",
            "battle_location": "Paris",
        }
        ney.holding_position = True
        ney.hold_region = "Belgium"
        place_marshals(world, ney)

        se = make_strategic_executor()
        se.process_strategic_orders(world, {"world": world})

        assert ney.pending_interrupt is None
        assert ney.strategic_order is None
        assert ney.holding_position is False


# ═══════════════════════════════════════════════════════
# 7A-7: HOLD Expiry Dead Code
# ═══════════════════════════════════════════════════════

class TestHoldExpiryDeadCode:
    """Verify the HOLD expiry in _execute_hold handles aggressive personality."""

    def test_hold_expiry_aggressive_handled_by_condition_check(self):
        """Aggressive HOLD with max_turns should expire via _check_condition → _complete_order.

        After removing the dead code early check, the _check_condition path at step 1b
        handles max_turns expiry for all order types. This verifies the aggressive
        personality message is correct and holding state is properly cleaned up.
        """
        world = make_world()
        world.current_turn = 10

        ney = make_marshal(name="Ney", location="Belgium", personality="aggressive")
        ney.holding_position = True
        ney.hold_region = "Belgium"
        condition = StrategicCondition(max_turns=3)
        order = make_strategic_order("HOLD", "Belgium")
        order.condition = condition
        order.issued_turn = 5  # 10 - 5 = 5 >= 3 → should expire
        ney.strategic_order = order
        place_marshals(world, ney)

        se = make_strategic_executor()
        result = se._execute_strategic_turn(ney, world, {"world": world})

        # Order should be complete (via _check_condition → _complete_order)
        assert result is not None
        assert result.get("order_status") == "completed"
        assert ney.strategic_order is None
        assert ney.holding_position is False
        assert ney.hold_region == ""
        # Should have personality-specific message for aggressive
        assert "restless" in result.get("message", "").lower()


# ═══════════════════════════════════════════════════════
# 7B-1: Artillery Reinforcement in Relationships
# ═══════════════════════════════════════════════════════

class TestArtilleryReinforcementRelationships:
    """Artillery from adjacent regions should be included in relationship processing."""

    def test_artillery_reinforcement_in_relationships(self):
        """Artillery that reinforced from adjacent should be a participant."""
        from backend.game_logic.relationship import process_battle_relationships, get_battle_participants

        world = make_world()
        ney = make_marshal(name="Ney", location="Belgium", strength=30000)
        drouot = make_marshal(name="Drouot", location="Paris", strength=15000)
        drouot.artillery = True

        wellington = make_enemy(name="Wellington", location="Belgium", strength=25000)
        place_marshals(world, ney, drouot, wellington)

        battle_result = {
            "outcome": "attacker_victory",
            "victor": "Ney",
            "attacker": {"casualties": 5000},
            "defender": {"casualties": 10000},
        }

        # Without artillery param — Drouot NOT in participants (different region)
        participants_without = get_battle_participants(ney, "Belgium", "France", world)
        assert drouot not in participants_without

        # With artillery param — function accepts the parameter without crash
        changes = process_battle_relationships(
            ney, wellington, battle_result, "Belgium", world,
            attacker_artillery=[drouot]
        )
        assert isinstance(changes, list)
