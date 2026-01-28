"""
Serialization Roundtrip Tests for Project Sovereign

Validates that all game state can be perfectly reconstructed from serialized data.
This is foundational work for a future save/load system.

Key validation:
1. StrategicCondition - All fields survive roundtrip
2. StrategicOrder - All fields including nested StrategicCondition
3. Marshal - ALL fields (50+), including nested Trust, StrategicOrder
4. Region - All fields including control state
5. Trust - Value survives roundtrip
6. AuthorityTracker - All fields including history
7. VindicationTracker - Pending and history
8. WorldState - Complete game state
"""

import pytest
from typing import Dict, Any
from backend.models.marshal import (
    Marshal, StrategicCondition, StrategicOrder, Stance,
    create_starting_marshals, create_enemy_marshals
)
from backend.models.region import Region, create_regions
from backend.models.trust import Trust
from backend.models.authority import AuthorityTracker
from backend.models.world_state import WorldState
from backend.commands.vindication import VindicationTracker


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def assert_field_equal(restored, original, field_name: str, obj_name: str = "object"):
    """
    Assert two fields are equal with clear error message.

    Handles special cases:
    - Trust objects: Compare .value
    - Stance enums: Compare directly
    - None values: Both must be None
    """
    orig_val = getattr(original, field_name, "__MISSING__")
    rest_val = getattr(restored, field_name, "__MISSING__")

    # Handle Trust objects
    if hasattr(orig_val, 'value') and hasattr(rest_val, 'value'):
        assert rest_val.value == orig_val.value, \
            f"{obj_name}.{field_name}: {rest_val.value} != {orig_val.value}"
        return

    assert rest_val == orig_val, \
        f"{obj_name}.{field_name}: {rest_val!r} != {orig_val!r}"


def create_full_marshal() -> Marshal:
    """Create a marshal with ALL fields set to non-default values."""
    m = Marshal(
        name="TestMarshal",
        location="Paris",
        strength=50000,
        personality="aggressive",
        nation="France",
        movement_range=2,
        tactical_skill=8,
        skills={
            "tactical": 7,
            "shock": 9,
            "defense": 4,
            "logistics": 5,
            "administration": 4,
            "command": 8
        },
        ability={
            "name": "Test Ability",
            "description": "Test description",
            "trigger": "when_attacking",
            "effect": "+2 test"
        },
        starting_trust=75,
        cavalry=True,
        spawn_location="Lyon"
    )

    # Set all game state fields to non-default values
    m.morale = 85
    m.orders_overridden = 3
    m.battles_won = 5
    m.battles_lost = 2
    m.just_retreated = True

    # Disobedience system
    m.trust.set(65)
    m.vindication_score = 2
    m.recent_battles = ["victory", "defeat", "victory"]
    m.recent_overrides = [True, False, True, True, False]

    # Autonomy system
    m.autonomous = True
    m.autonomy_turns = 2
    m.autonomy_reason = "redemption"
    m.redemption_pending = True
    m.autonomous_battles_won = 3
    m.autonomous_battles_lost = 1
    m.autonomous_regions_captured = 2
    m.trust_warning_shown = True

    # Relationships
    m.relationships = {"Davout": -1, "Grouchy": 1}

    # Tactical state - Drill
    m.drilling = True
    m.drilling_locked = False
    m.drill_complete_turn = 5
    m.shock_bonus = 2
    m.strategic_combat_bonus = 10
    m.strategic_defense_bonus = 15

    # Precision execution
    m.precision_execution_active = True
    m.precision_execution_turns = 2

    # Strategic order
    m.strategic_order = StrategicOrder(
        command_type="MOVE_TO",
        target="Belgium",
        target_type="region",
        started_turn=3,
        original_command="march to Belgium",
        path=["Paris", "Belgium"],
        target_snapshot_location="Belgium",
        attack_on_arrival=True,
        condition=StrategicCondition(
            max_turns=5,
            until_marshal_arrives="Davout",
            until_battle_won=True
        ),
        last_combat_enemy="Wellington",
        last_combat_turn=4,
        last_combat_result="victory"
    )

    # Pending interrupt
    m.pending_interrupt = {
        "interrupt_type": "cannon_fire",
        "battle_region": "Belgium",
        "is_first_step": True
    }

    # Combat tracking
    m.in_combat_this_turn = True
    m.last_combat_turn = 4
    m.last_combat_result = "victory"
    m.last_combat_location = "Belgium"

    # Fortify state
    m.fortified = True
    m.fortify_expires_turn = 10
    m.defense_bonus = 0.16

    # Retreat state
    m.retreating = True
    m.retreat_recovery = 2
    m.retreated_this_turn = True

    # Broken state
    m.broken = False
    m.broken_recovery = 0

    # Stance
    m.stance = Stance.AGGRESSIVE

    # Cavalry-specific
    m.turns_in_defensive_stance = 1
    m.turns_fortified = 2
    m.turns_defensive = 3

    # Davout-specific
    m.counter_punch_available = True
    m.counter_punch_turns = 1

    # Grouchy-specific
    m.holding_position = True
    m.hold_region = "Paris"

    # Recklessness
    m.recklessness = 2
    m.pending_glorious_charge = True
    m.pending_charge_target = "Wellington"

    # Exhaustion
    m.attacks_this_turn = 2

    return m


# ============================================================================
# STRATEGIC CONDITION TESTS
# ============================================================================

class TestStrategicConditionSerialization:
    """Roundtrip tests for StrategicCondition dataclass."""

    def test_empty_condition_roundtrip(self):
        """Condition with all defaults."""
        original = StrategicCondition()
        data = original.to_dict()
        restored = StrategicCondition.from_dict(data)

        assert restored.max_turns == original.max_turns
        assert restored.until_marshal_arrives == original.until_marshal_arrives
        assert restored.until_marshal_destroyed == original.until_marshal_destroyed
        assert restored.until_battle_won == original.until_battle_won
        assert restored.until_relieved == original.until_relieved

    def test_full_condition_roundtrip(self):
        """Condition with all fields set."""
        original = StrategicCondition(
            max_turns=10,
            until_marshal_arrives="Ney",
            until_marshal_destroyed="Wellington",
            until_battle_won=True,
            until_relieved=True
        )
        data = original.to_dict()
        restored = StrategicCondition.from_dict(data)

        assert restored.max_turns == 10
        assert restored.until_marshal_arrives == "Ney"
        assert restored.until_marshal_destroyed == "Wellington"
        assert restored.until_battle_won is True
        assert restored.until_relieved is True

    def test_partial_condition_roundtrip(self):
        """Condition with some fields set."""
        original = StrategicCondition(
            max_turns=5,
            until_battle_won=True
        )
        data = original.to_dict()
        restored = StrategicCondition.from_dict(data)

        assert restored.max_turns == 5
        assert restored.until_marshal_arrives is None
        assert restored.until_battle_won is True


# ============================================================================
# STRATEGIC ORDER TESTS
# ============================================================================

class TestStrategicOrderSerialization:
    """Roundtrip tests for StrategicOrder dataclass."""

    def test_move_to_region_roundtrip(self):
        """MOVE_TO targeting a region."""
        original = StrategicOrder(
            command_type="MOVE_TO",
            target="Belgium",
            target_type="region",
            started_turn=3,
            original_command="march to Belgium",
            path=["Paris", "Belgium"],
            attack_on_arrival=True
        )
        data = original.to_dict()
        restored = StrategicOrder.from_dict(data)

        assert restored.command_type == "MOVE_TO"
        assert restored.target == "Belgium"
        assert restored.target_type == "region"
        assert restored.started_turn == 3
        assert restored.original_command == "march to Belgium"
        assert restored.path == ["Paris", "Belgium"]
        assert restored.attack_on_arrival is True
        assert restored.condition is None

    def test_move_to_marshal_with_snapshot_roundtrip(self):
        """MOVE_TO targeting friendly marshal (snapshot location)."""
        original = StrategicOrder(
            command_type="MOVE_TO",
            target="Ney",
            target_type="marshal",
            started_turn=2,
            original_command="march to Ney",
            path=["Paris", "Belgium"],
            target_snapshot_location="Belgium"
        )
        data = original.to_dict()
        restored = StrategicOrder.from_dict(data)

        assert restored.target == "Ney"
        assert restored.target_type == "marshal"
        assert restored.target_snapshot_location == "Belgium"

    def test_pursue_roundtrip(self):
        """PURSUE with dynamic tracking."""
        original = StrategicOrder(
            command_type="PURSUE",
            target="Wellington",
            target_type="marshal",
            started_turn=1,
            original_command="pursue Wellington",
            path=["Belgium", "Waterloo"],
            last_combat_enemy="Wellington",
            last_combat_turn=2,
            last_combat_result="stalemate"
        )
        data = original.to_dict()
        restored = StrategicOrder.from_dict(data)

        assert restored.command_type == "PURSUE"
        assert restored.target == "Wellington"
        assert restored.last_combat_enemy == "Wellington"
        assert restored.last_combat_turn == 2
        assert restored.last_combat_result == "stalemate"

    def test_hold_with_conditions_roundtrip(self):
        """HOLD with multiple conditions."""
        condition = StrategicCondition(
            max_turns=10,
            until_marshal_arrives="Davout",
            until_relieved=True
        )
        original = StrategicOrder(
            command_type="HOLD",
            target="Belgium",
            target_type="region",
            started_turn=5,
            original_command="hold Belgium until relieved",
            condition=condition
        )
        data = original.to_dict()
        restored = StrategicOrder.from_dict(data)

        assert restored.command_type == "HOLD"
        assert restored.condition is not None
        assert isinstance(restored.condition, StrategicCondition)
        assert restored.condition.max_turns == 10
        assert restored.condition.until_marshal_arrives == "Davout"
        assert restored.condition.until_relieved is True

    def test_support_roundtrip(self):
        """SUPPORT following ally."""
        original = StrategicOrder(
            command_type="SUPPORT",
            target="Davout",
            target_type="marshal",
            started_turn=4,
            original_command="support Davout",
            path=["Paris", "Lyon"],
            follow_if_moves=True,
            join_combat=True
        )
        data = original.to_dict()
        restored = StrategicOrder.from_dict(data)

        assert restored.command_type == "SUPPORT"
        assert restored.follow_if_moves is True
        assert restored.join_combat is True


# ============================================================================
# MARSHAL SERIALIZATION TESTS
# ============================================================================

class TestMarshalSerialization:
    """Roundtrip tests for Marshal serialization."""

    def test_minimal_marshal_roundtrip(self):
        """Marshal with only required fields (defaults)."""
        original = Marshal(
            name="TestMarshal",
            location="Paris",
            strength=50000,
            personality="balanced"
        )
        data = original.to_dict()
        restored = Marshal.from_dict(data)

        assert restored.name == "TestMarshal"
        assert restored.location == "Paris"
        assert restored.strength == 50000
        assert restored.personality == "balanced"

    def test_full_marshal_roundtrip(self):
        """Marshal with ALL fields populated - the comprehensive test."""
        original = create_full_marshal()
        data = original.to_dict()
        restored = Marshal.from_dict(data)

        # Core identity
        assert_field_equal(restored, original, "name", "Marshal")
        assert_field_equal(restored, original, "location", "Marshal")
        assert_field_equal(restored, original, "strength", "Marshal")
        assert_field_equal(restored, original, "personality", "Marshal")
        assert_field_equal(restored, original, "nation", "Marshal")
        assert_field_equal(restored, original, "spawn_location", "Marshal")
        assert_field_equal(restored, original, "movement_range", "Marshal")
        assert_field_equal(restored, original, "tactical_skill", "Marshal")
        assert_field_equal(restored, original, "starting_strength", "Marshal")

        # Skills
        assert_field_equal(restored, original, "skills", "Marshal")

        # Ability
        assert_field_equal(restored, original, "ability", "Marshal")

        # Game state
        assert_field_equal(restored, original, "morale", "Marshal")
        assert_field_equal(restored, original, "orders_overridden", "Marshal")
        assert_field_equal(restored, original, "battles_won", "Marshal")
        assert_field_equal(restored, original, "battles_lost", "Marshal")
        assert_field_equal(restored, original, "just_retreated", "Marshal")

        # Trust (special handling for Trust object)
        assert_field_equal(restored, original, "trust", "Marshal")

        # Disobedience system
        assert_field_equal(restored, original, "vindication_score", "Marshal")
        assert_field_equal(restored, original, "recent_battles", "Marshal")
        assert_field_equal(restored, original, "recent_overrides", "Marshal")

        # Autonomy system
        assert_field_equal(restored, original, "autonomous", "Marshal")
        assert_field_equal(restored, original, "autonomy_turns", "Marshal")
        assert_field_equal(restored, original, "autonomy_reason", "Marshal")
        assert_field_equal(restored, original, "redemption_pending", "Marshal")
        assert_field_equal(restored, original, "autonomous_battles_won", "Marshal")
        assert_field_equal(restored, original, "autonomous_battles_lost", "Marshal")
        assert_field_equal(restored, original, "autonomous_regions_captured", "Marshal")
        assert_field_equal(restored, original, "trust_warning_shown", "Marshal")

        # Relationships
        assert_field_equal(restored, original, "relationships", "Marshal")

        # Tactical state - Drill
        assert_field_equal(restored, original, "drilling", "Marshal")
        assert_field_equal(restored, original, "drilling_locked", "Marshal")
        assert_field_equal(restored, original, "drill_complete_turn", "Marshal")
        assert_field_equal(restored, original, "shock_bonus", "Marshal")
        assert_field_equal(restored, original, "strategic_combat_bonus", "Marshal")
        assert_field_equal(restored, original, "strategic_defense_bonus", "Marshal")

        # Precision execution
        assert_field_equal(restored, original, "precision_execution_active", "Marshal")
        assert_field_equal(restored, original, "precision_execution_turns", "Marshal")

        # Strategic order (verify it's proper object, not dict)
        assert restored.strategic_order is not None
        assert isinstance(restored.strategic_order, StrategicOrder)
        assert restored.strategic_order.command_type == original.strategic_order.command_type
        assert restored.strategic_order.target == original.strategic_order.target

        # Pending interrupt
        assert_field_equal(restored, original, "pending_interrupt", "Marshal")

        # Combat tracking
        assert_field_equal(restored, original, "in_combat_this_turn", "Marshal")
        assert_field_equal(restored, original, "last_combat_turn", "Marshal")
        assert_field_equal(restored, original, "last_combat_result", "Marshal")
        assert_field_equal(restored, original, "last_combat_location", "Marshal")

        # Fortify state
        assert_field_equal(restored, original, "fortified", "Marshal")
        assert_field_equal(restored, original, "fortify_expires_turn", "Marshal")
        assert_field_equal(restored, original, "defense_bonus", "Marshal")

        # Retreat state
        assert_field_equal(restored, original, "retreating", "Marshal")
        assert_field_equal(restored, original, "retreat_recovery", "Marshal")
        assert_field_equal(restored, original, "retreated_this_turn", "Marshal")

        # Broken state
        assert_field_equal(restored, original, "broken", "Marshal")
        assert_field_equal(restored, original, "broken_recovery", "Marshal")

        # Stance
        assert_field_equal(restored, original, "stance", "Marshal")

        # Cavalry-specific
        assert_field_equal(restored, original, "cavalry", "Marshal")
        assert_field_equal(restored, original, "turns_in_defensive_stance", "Marshal")
        assert_field_equal(restored, original, "turns_fortified", "Marshal")
        assert_field_equal(restored, original, "turns_defensive", "Marshal")

        # Davout-specific (counter-punch)
        assert_field_equal(restored, original, "counter_punch_available", "Marshal")
        assert_field_equal(restored, original, "counter_punch_turns", "Marshal")

        # Grouchy-specific (holding position)
        assert_field_equal(restored, original, "holding_position", "Marshal")
        assert_field_equal(restored, original, "hold_region", "Marshal")

        # Recklessness
        assert_field_equal(restored, original, "recklessness", "Marshal")
        assert_field_equal(restored, original, "pending_glorious_charge", "Marshal")
        assert_field_equal(restored, original, "pending_charge_target", "Marshal")

        # Exhaustion
        assert_field_equal(restored, original, "attacks_this_turn", "Marshal")

    def test_marshal_with_strategic_order_nested_condition(self):
        """Marshal with strategic order containing nested condition."""
        original = Marshal(
            name="Ney",
            location="Belgium",
            strength=72000,
            personality="aggressive"
        )
        original.strategic_order = StrategicOrder(
            command_type="HOLD",
            target="Belgium",
            target_type="region",
            started_turn=1,
            original_command="hold until Davout arrives",
            condition=StrategicCondition(
                until_marshal_arrives="Davout",
                until_battle_won=True
            )
        )

        data = original.to_dict()
        restored = Marshal.from_dict(data)

        # Verify nested condition is proper type
        assert restored.strategic_order is not None
        assert restored.strategic_order.condition is not None
        assert isinstance(restored.strategic_order.condition, StrategicCondition)
        assert restored.strategic_order.condition.until_marshal_arrives == "Davout"
        assert restored.strategic_order.condition.until_battle_won is True

    def test_marshal_with_pending_interrupt(self):
        """Marshal awaiting player response to interrupt."""
        original = Marshal(
            name="Grouchy",
            location="Waterloo",
            strength=33000,
            personality="literal"
        )
        original.pending_interrupt = {
            "interrupt_type": "contact",
            "enemy_marshal": "Wellington",
            "enemy_strength": 68000,
            "is_first_step": False,
            "options": ["attack", "go_around", "cancel_order"]
        }

        data = original.to_dict()
        restored = Marshal.from_dict(data)

        assert restored.pending_interrupt is not None
        assert restored.pending_interrupt["interrupt_type"] == "contact"
        assert restored.pending_interrupt["enemy_marshal"] == "Wellington"

    def test_marshal_stance_enum_roundtrip(self):
        """Stance enum survives roundtrip as proper enum."""
        for stance in [Stance.NEUTRAL, Stance.AGGRESSIVE, Stance.DEFENSIVE]:
            original = Marshal(
                name="Test",
                location="Paris",
                strength=50000,
                personality="balanced"
            )
            original.stance = stance

            data = original.to_dict()
            restored = Marshal.from_dict(data)

            assert restored.stance == stance
            assert isinstance(restored.stance, Stance)

    def test_starting_marshals_roundtrip(self):
        """All starting French marshals survive roundtrip."""
        marshals = create_starting_marshals()

        for name, original in marshals.items():
            data = original.to_dict()
            restored = Marshal.from_dict(data)

            assert restored.name == original.name
            assert restored.location == original.location
            assert restored.strength == original.strength
            assert restored.personality == original.personality
            assert restored.nation == original.nation

    def test_enemy_marshals_roundtrip(self):
        """All enemy marshals survive roundtrip."""
        enemies = create_enemy_marshals()

        for name, original in enemies.items():
            data = original.to_dict()
            restored = Marshal.from_dict(data)

            assert restored.name == original.name
            assert restored.nation == original.nation


# ============================================================================
# TRUST SERIALIZATION TESTS
# ============================================================================

class TestTrustSerialization:
    """Roundtrip tests for Trust class."""

    def test_trust_default_roundtrip(self):
        """Trust with default value."""
        original = Trust()
        data = original.to_dict()
        restored = Trust.from_dict(data)

        assert restored.value == original.value
        assert restored.value == 70  # Default

    def test_trust_custom_value_roundtrip(self):
        """Trust with custom value."""
        original = Trust(85)
        data = original.to_dict()
        restored = Trust.from_dict(data)

        assert restored.value == 85

    def test_trust_modified_value_roundtrip(self):
        """Trust after modification."""
        original = Trust(70)
        original.modify(-25)

        data = original.to_dict()
        restored = Trust.from_dict(data)

        assert restored.value == 45


# ============================================================================
# REGION SERIALIZATION TESTS
# ============================================================================

class TestRegionSerialization:
    """Roundtrip tests for Region class."""

    def test_basic_region_roundtrip(self):
        """Region with basic fields."""
        original = Region(
            name="Paris",
            adjacent_regions=["Belgium", "Lyon"],
            income_value=100,
            is_capital=True
        )

        data = original.to_dict()
        restored = Region.from_dict(data)

        assert restored.name == "Paris"
        assert restored.adjacent_regions == ["Belgium", "Lyon"]
        assert restored.income_value == 100
        assert restored.is_capital is True

    def test_region_with_controller_roundtrip(self):
        """Region with controller set."""
        original = Region(
            name="Belgium",
            adjacent_regions=["Paris", "Netherlands"],
            income_value=100
        )
        original.controller = "France"
        original.garrison_strength = 5000

        data = original.to_dict()
        restored = Region.from_dict(data)

        assert restored.controller == "France"
        assert restored.garrison_strength == 5000

    def test_all_regions_roundtrip(self):
        """All game regions survive roundtrip."""
        regions = create_regions()

        for name, original in regions.items():
            data = original.to_dict()
            restored = Region.from_dict(data)

            assert restored.name == original.name
            assert restored.adjacent_regions == original.adjacent_regions


# ============================================================================
# AUTHORITY TRACKER SERIALIZATION TESTS
# ============================================================================

class TestAuthorityTrackerSerialization:
    """Roundtrip tests for AuthorityTracker class."""

    def test_fresh_tracker_roundtrip(self):
        """Fresh tracker with defaults."""
        original = AuthorityTracker()
        data = original.to_dict()
        restored = AuthorityTracker.from_dict(data)

        assert restored.authority == 100
        assert restored.recent_responses == []

    def test_tracker_with_responses_roundtrip(self):
        """Tracker after recording responses."""
        original = AuthorityTracker()
        original.record_response('trust')
        original.record_response('insist')
        original.record_response('trust')
        original.record_response('compromise')
        original.record_response('trust')

        data = original.to_dict()
        restored = AuthorityTracker.from_dict(data)

        assert restored.authority == original.authority
        assert restored.recent_responses == original.recent_responses

    def test_tracker_with_crossed_thresholds_roundtrip(self):
        """Tracker that has crossed authority thresholds."""
        original = AuthorityTracker()
        # Force low authority
        original.authority = 45
        original._crossed_thresholds = [70, 50]
        original.recent_responses = ['trust'] * 8 + ['insist'] * 2

        data = original.to_dict()
        restored = AuthorityTracker.from_dict(data)

        assert restored.authority == 45
        assert restored._crossed_thresholds == [70, 50]


# ============================================================================
# VINDICATION TRACKER SERIALIZATION TESTS
# ============================================================================

class TestVindicationTrackerSerialization:
    """Roundtrip tests for VindicationTracker class."""

    def test_empty_tracker_roundtrip(self):
        """Fresh tracker with no pending vindications."""
        original = VindicationTracker()
        data = original.to_dict()
        restored = VindicationTracker.from_dict(data)

        assert restored.pending == {}
        assert restored.history == []

    def test_tracker_with_pending_roundtrip(self):
        """Tracker with pending vindication."""
        original = VindicationTracker()
        original.record_choice(
            marshal_name="Ney",
            choice="insist",
            original_order={"action": "attack", "target": "Wellington"},
            alternative={"action": "defend"}
        )

        data = original.to_dict()
        restored = VindicationTracker.from_dict(data)

        assert "Ney" in restored.pending
        assert restored.pending["Ney"]["choice"] == "insist"

    def test_tracker_with_history_roundtrip(self):
        """Tracker with vindication history."""
        original = VindicationTracker()
        original.history = [
            {"marshal": "Ney", "choice": "trust", "outcome": "vindicated"},
            {"marshal": "Davout", "choice": "insist", "outcome": "player_right"}
        ]

        data = original.to_dict()
        restored = VindicationTracker.from_dict(data)

        assert len(restored.history) == 2
        assert restored.history[0]["marshal"] == "Ney"


# ============================================================================
# WORLD STATE SERIALIZATION TESTS
# ============================================================================

class TestWorldStateSerialization:
    """Roundtrip tests for complete WorldState."""

    def test_fresh_world_roundtrip(self):
        """Fresh game state."""
        original = WorldState()
        data = original.to_dict()
        restored = WorldState.from_dict(data)

        assert restored.current_turn == original.current_turn
        assert restored.player_nation == original.player_nation
        assert restored.gold == original.gold

    def test_mid_game_world_roundtrip(self):
        """Game in progress with modifications."""
        original = WorldState()

        # Modify turn state
        original.current_turn = 15
        original.gold = 750
        original.actions_remaining = 2  # WorldState uses actions_remaining, not actions_used

        # Modify a marshal
        ney = original.marshals["Ney"]
        ney.location = "Belgium"
        ney.strength = 65000
        ney.morale = 80
        ney.stance = Stance.AGGRESSIVE

        # Modify region control
        original.regions["Belgium"].controller = "France"

        data = original.to_dict()
        restored = WorldState.from_dict(data)

        assert restored.current_turn == 15
        assert restored.gold == 750
        assert restored.actions_remaining == 2

        # Verify marshal state
        restored_ney = restored.marshals["Ney"]
        assert restored_ney.location == "Belgium"
        assert restored_ney.strength == 65000
        assert restored_ney.morale == 80
        assert restored_ney.stance == Stance.AGGRESSIVE

        # Verify region control
        assert restored.regions["Belgium"].controller == "France"

    def test_world_with_active_strategic_orders(self):
        """World state with marshals executing strategic orders."""
        original = WorldState()

        # Set up strategic order
        ney = original.marshals["Ney"]
        ney.strategic_order = StrategicOrder(
            command_type="PURSUE",
            target="Wellington",
            target_type="marshal",
            started_turn=5,
            original_command="pursue Wellington relentlessly",
            path=["Belgium", "Waterloo"]
        )

        data = original.to_dict()
        restored = WorldState.from_dict(data)

        restored_ney = restored.marshals["Ney"]
        assert restored_ney.strategic_order is not None
        assert isinstance(restored_ney.strategic_order, StrategicOrder)
        assert restored_ney.strategic_order.command_type == "PURSUE"
        assert restored_ney.strategic_order.target == "Wellington"

    def test_world_all_marshals_preserved(self):
        """All marshals (player + enemy) survive roundtrip."""
        original = WorldState()

        data = original.to_dict()
        restored = WorldState.from_dict(data)

        # Check all original marshals exist
        for name in original.marshals:
            assert name in restored.marshals, f"Marshal {name} missing after roundtrip"

        # Check counts match
        assert len(restored.marshals) == len(original.marshals)


# ============================================================================
# PARSE RESULT SERIALIZATION TESTS (already has to_dict/from_dict)
# ============================================================================

class TestParseResultSerialization:
    """Verify ParseResult serialization (already implemented)."""

    def test_tactical_command_roundtrip(self):
        """Tactical command parse result."""
        from backend.ai.schemas import ParseResult

        original = ParseResult(
            matched=True,
            command_type="tactical",
            marshals=["Ney"],
            action="attack",
            target="Wellington",
            confidence=0.95,
            mode="mock",
            raw_command="Ney attack Wellington"
        )

        data = original.to_dict()
        restored = ParseResult.from_dict(data)

        assert restored.action == "attack"
        assert restored.target == "Wellington"
        assert restored.confidence == 0.95

    def test_strategic_command_roundtrip(self):
        """Strategic command parse result."""
        from backend.ai.schemas import ParseResult

        original = ParseResult(
            matched=True,
            command_type="strategic",
            marshals=["Ney"],
            action="move",
            target="Belgium",
            is_strategic=True,
            strategic_type="MOVE_TO",
            strategic_condition={"max_turns": 5},
            ambiguity=15,
            strategic_score=70
        )

        data = original.to_dict()
        restored = ParseResult.from_dict(data)

        assert restored.is_strategic is True
        assert restored.strategic_type == "MOVE_TO"
        assert restored.strategic_condition == {"max_turns": 5}


# ============================================================================
# MODDING WORKFLOW TESTS
# ============================================================================
# Tests that verify modders can write minimal JSON files and get working
# game objects with sensible defaults applied.

class TestModdingWorkflow:
    """Tests for modding-friendly from_dict behavior."""

    def test_minimal_marshal_creation(self):
        """
        Modders should only need to specify name, location, strength.
        All other 50+ fields should get sensible defaults.
        """
        minimal_json = {
            "name": "CustomMarshal",
            "location": "Paris",
            "strength": 30000
        }

        marshal = Marshal.from_dict(minimal_json)

        # Required fields applied
        assert marshal.name == "CustomMarshal"
        assert marshal.location == "Paris"
        assert marshal.strength == 30000

        # Defaults applied
        assert marshal.personality == "balanced"
        assert marshal.nation == "France"
        assert marshal.movement_range == 1
        assert marshal.morale == 70
        assert marshal.trust.value == 70
        assert marshal.stance == Stance.NEUTRAL
        assert marshal.cavalry is False
        assert marshal.drilling is False
        assert marshal.fortified is False
        assert marshal.retreat_recovery == 0
        assert marshal.autonomous is False

    def test_minimal_region_creation(self):
        """
        Modders should only need to specify name and adjacent_regions.
        """
        minimal_json = {
            "name": "CustomProvince",
            "adjacent_regions": ["Paris", "Lyon"]
        }

        region = Region.from_dict(minimal_json)

        # Required fields applied
        assert region.name == "CustomProvince"
        assert region.adjacent_regions == ["Paris", "Lyon"]

        # Defaults applied
        assert region.income_value == 100
        assert region.is_capital is False
        assert region.controller is None
        assert region.garrison_strength == 0

    def test_minimal_trust_creation(self):
        """Trust can be created with no fields (uses default 70)."""
        trust = Trust.from_dict({})
        assert trust.value == 70

    def test_minimal_strategic_condition_creation(self):
        """All StrategicCondition fields are optional."""
        condition = StrategicCondition.from_dict({})

        assert condition.max_turns is None
        assert condition.until_marshal_arrives is None
        assert condition.until_marshal_destroyed is None
        assert condition.until_battle_won is False
        assert condition.until_relieved is False

    def test_partial_marshal_with_nation(self):
        """Modder specifies nation for enemy marshal."""
        partial_json = {
            "name": "EnemyGeneral",
            "location": "Vienna",
            "strength": 45000,
            "nation": "Austria",
            "personality": "cautious"
        }

        marshal = Marshal.from_dict(partial_json)

        assert marshal.name == "EnemyGeneral"
        assert marshal.nation == "Austria"
        assert marshal.personality == "cautious"
        # Defaults still applied for unspecified fields
        assert marshal.morale == 70
        assert marshal.cavalry is False

    def test_partial_marshal_with_skills(self):
        """Modder specifies custom skills."""
        partial_json = {
            "name": "SkilledMarshal",
            "location": "Paris",
            "strength": 40000,
            "skills": {
                "tactical": 8,
                "shock": 7,
                "defense": 6,
                "logistics": 5,
                "administration": 4,
                "command": 9
            }
        }

        marshal = Marshal.from_dict(partial_json)

        assert marshal.skills["tactical"] == 8
        assert marshal.skills["command"] == 9

    def test_partial_region_with_capital(self):
        """Modder specifies a capital region."""
        partial_json = {
            "name": "CustomCapital",
            "adjacent_regions": ["Province1", "Province2"],
            "income_value": 200,
            "is_capital": True,
            "controller": "CustomNation"
        }

        region = Region.from_dict(partial_json)

        assert region.name == "CustomCapital"
        assert region.income_value == 200
        assert region.is_capital is True
        assert region.controller == "CustomNation"

    def test_minimal_world_state_creation(self):
        """WorldState with only player_nation specified."""
        minimal_json = {
            "player_nation": "Prussia"
        }

        world = WorldState.from_dict(minimal_json)

        assert world.player_nation == "Prussia"
        # Defaults applied
        assert world.current_turn == 1
        assert world.max_turns == 40
        assert world.gold == 1200
        assert world.game_over is False
        assert world.actions_remaining == 4

    def test_custom_scenario_marshals(self):
        """Load custom scenario with custom marshals."""
        scenario_json = {
            "player_nation": "France",
            "current_turn": 1,
            "gold": 2000,
            "marshals": {
                "Napoleon": {
                    "name": "Napoleon",
                    "location": "Paris",
                    "strength": 100000,
                    "personality": "aggressive",
                    "tactical_skill": 10
                },
                "Murat": {
                    "name": "Murat",
                    "location": "Lyon",
                    "strength": 50000,
                    "cavalry": True
                }
            }
        }

        world = WorldState.from_dict(scenario_json)

        assert world.player_nation == "France"
        assert world.gold == 2000
        assert "Napoleon" in world.marshals
        assert "Murat" in world.marshals
        assert world.marshals["Napoleon"].strength == 100000
        assert world.marshals["Napoleon"].tactical_skill == 10
        assert world.marshals["Murat"].cavalry is True


# ============================================================================
# FORWARD COMPATIBILITY TESTS (Unknown Fields)
# ============================================================================
# Tests that verify unknown fields in JSON are silently ignored.
# This allows save files from newer versions to load in older versions.

class TestForwardCompatibility:
    """Tests for unknown field handling (future-proofing)."""

    def test_marshal_ignores_unknown_fields(self):
        """Marshal.from_dict should ignore fields from future versions."""
        json_with_extras = {
            "name": "FutureMarshal",
            "location": "Paris",
            "strength": 40000,
            # Future fields that don't exist yet
            "future_field_1": "some_value",
            "future_field_2": 12345,
            "future_nested": {"a": 1, "b": 2},
            "future_list": [1, 2, 3]
        }

        # Should not raise an error
        marshal = Marshal.from_dict(json_with_extras)

        assert marshal.name == "FutureMarshal"
        assert marshal.strength == 40000
        # Unknown fields silently ignored (no crash)

    def test_region_ignores_unknown_fields(self):
        """Region.from_dict should ignore unknown fields."""
        json_with_extras = {
            "name": "FutureRegion",
            "adjacent_regions": ["Paris"],
            "future_terrain_type": "mountains",
            "future_resource": "iron"
        }

        region = Region.from_dict(json_with_extras)

        assert region.name == "FutureRegion"
        assert region.adjacent_regions == ["Paris"]

    def test_trust_ignores_unknown_fields(self):
        """Trust.from_dict should ignore unknown fields."""
        json_with_extras = {
            "value": 85,
            "future_loyalty_type": "fanatical"
        }

        trust = Trust.from_dict(json_with_extras)
        assert trust.value == 85

    def test_strategic_condition_ignores_unknown_fields(self):
        """StrategicCondition.from_dict should ignore unknown fields."""
        json_with_extras = {
            "max_turns": 5,
            "future_condition": True,
            "future_trigger": "on_battle_start"
        }

        condition = StrategicCondition.from_dict(json_with_extras)
        assert condition.max_turns == 5

    def test_strategic_order_ignores_unknown_fields(self):
        """StrategicOrder.from_dict should ignore unknown fields."""
        json_with_extras = {
            "command_type": "MOVE_TO",
            "target": "Paris",
            "target_type": "region",
            "started_turn": 1,
            "original_command": "move to Paris",
            "future_priority": "high",
            "future_stealth_mode": True
        }

        order = StrategicOrder.from_dict(json_with_extras)
        assert order.command_type == "MOVE_TO"
        assert order.target == "Paris"

    def test_world_state_ignores_unknown_fields(self):
        """WorldState.from_dict should ignore unknown top-level fields."""
        json_with_extras = {
            "player_nation": "France",
            "current_turn": 5,
            "future_weather": "rain",
            "future_season": "winter",
            "future_diplomatic_state": {"Britain": "hostile"}
        }

        world = WorldState.from_dict(json_with_extras)
        assert world.player_nation == "France"
        assert world.current_turn == 5

    def test_authority_tracker_ignores_unknown_fields(self):
        """AuthorityTracker.from_dict should ignore unknown fields."""
        json_with_extras = {
            "authority": 85,
            "recent_responses": ["trust", "insist"],
            "future_reputation": 100
        }

        tracker = AuthorityTracker.from_dict(json_with_extras)
        assert tracker.authority == 85
        assert len(tracker.recent_responses) == 2

    def test_vindication_tracker_ignores_unknown_fields(self):
        """VindicationTracker.from_dict should ignore unknown fields."""
        json_with_extras = {
            "pending": {},
            "history": [],
            "future_karma": 50
        }

        tracker = VindicationTracker.from_dict(json_with_extras)
        assert tracker.pending == {}
        assert tracker.history == []

    def test_nested_unknown_fields_preserved_in_dicts(self):
        """When restoring dict fields, unknown nested keys are preserved."""
        # Test with marshal relationships which is a dict
        json_data = {
            "name": "TestMarshal",
            "location": "Paris",
            "strength": 40000,
            "relationships": {
                "Davout": 50,
                "unknown_future_marshal": 30
            }
        }

        marshal = Marshal.from_dict(json_data)
        # The relationships dict preserves all keys
        assert marshal.relationships.get("Davout") == 50
        assert marshal.relationships.get("unknown_future_marshal") == 30


# ============================================================================
# SCENARIO LOADING TESTS
# ============================================================================
# Tests for WorldState.from_scenario() method

class TestScenarioLoading:
    """Tests for loading scenario files via WorldState.from_scenario()."""

    def test_load_minimal_scenario(self, tmp_path):
        """Load scenario with only player_nation specified."""
        import json

        scenario_file = tmp_path / "minimal.json"
        scenario_data = {"player_nation": "Prussia"}
        scenario_file.write_text(json.dumps(scenario_data))

        world = WorldState.from_scenario(str(scenario_file))

        assert world.player_nation == "Prussia"
        # Should have default regions loaded
        assert "Paris" in world.regions
        assert "Belgium" in world.regions
        # Should have default marshals loaded
        assert len(world.marshals) > 0

    def test_load_custom_marshals_scenario(self, tmp_path):
        """Load scenario with custom marshals."""
        import json

        scenario_data = {
            "player_nation": "France",
            "gold": 5000,
            "marshals": {
                "Napoleon": {
                    "name": "Napoleon",
                    "location": "Paris",
                    "strength": 200000,
                    "personality": "aggressive"
                },
                "Wellington": {
                    "name": "Wellington",
                    "location": "Belgium",
                    "strength": 100000,
                    "nation": "Britain",
                    "personality": "cautious"
                }
            }
        }

        scenario_file = tmp_path / "custom_marshals.json"
        scenario_file.write_text(json.dumps(scenario_data))

        world = WorldState.from_scenario(str(scenario_file))

        assert world.gold == 5000
        assert "Napoleon" in world.marshals
        assert "Wellington" in world.marshals
        assert world.marshals["Napoleon"].strength == 200000
        assert world.marshals["Wellington"].nation == "Britain"
        # Should have default regions
        assert "Paris" in world.regions

    def test_load_custom_regions_scenario(self, tmp_path):
        """Load scenario with custom regions."""
        import json

        scenario_data = {
            "player_nation": "France",
            "regions": {
                "CustomCapital": {
                    "name": "CustomCapital",
                    "adjacent_regions": ["CustomProvince"],
                    "income_value": 200,
                    "is_capital": True,
                    "controller": "France"
                },
                "CustomProvince": {
                    "name": "CustomProvince",
                    "adjacent_regions": ["CustomCapital"],
                    "income_value": 100
                }
            },
            "marshals": {
                "TestMarshal": {
                    "name": "TestMarshal",
                    "location": "CustomCapital",
                    "strength": 50000
                }
            }
        }

        scenario_file = tmp_path / "custom_regions.json"
        scenario_file.write_text(json.dumps(scenario_data))

        world = WorldState.from_scenario(str(scenario_file))

        assert "CustomCapital" in world.regions
        assert "CustomProvince" in world.regions
        assert world.regions["CustomCapital"].is_capital is True
        assert world.regions["CustomCapital"].income_value == 200
        # Default regions should NOT be present
        assert "Paris" not in world.regions

    def test_scenario_file_not_found(self):
        """Should raise FileNotFoundError for missing scenario."""
        with pytest.raises(FileNotFoundError):
            WorldState.from_scenario("/nonexistent/path/scenario.json")

    def test_scenario_invalid_json(self, tmp_path):
        """Should raise JSONDecodeError for malformed JSON."""
        import json

        scenario_file = tmp_path / "invalid.json"
        scenario_file.write_text("{ not valid json }")

        with pytest.raises(json.JSONDecodeError):
            WorldState.from_scenario(str(scenario_file))

    def test_scenario_wrong_type(self, tmp_path):
        """Should raise ValueError if root is not an object."""
        import json

        scenario_file = tmp_path / "array.json"
        scenario_file.write_text(json.dumps([1, 2, 3]))

        with pytest.raises(ValueError, match="must be a JSON object"):
            WorldState.from_scenario(str(scenario_file))

    def test_scenario_with_metadata(self, tmp_path):
        """Scenario metadata fields should be ignored gracefully."""
        import json

        scenario_data = {
            "scenario_name": "Battle of Waterloo",
            "scenario_description": "The final confrontation",
            "scenario_author": "ModderName",
            "scenario_version": "1.0",
            "player_nation": "France"
        }

        scenario_file = tmp_path / "with_metadata.json"
        scenario_file.write_text(json.dumps(scenario_data))

        world = WorldState.from_scenario(str(scenario_file))

        # Should load successfully, ignoring unknown metadata fields
        assert world.player_nation == "France"


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
