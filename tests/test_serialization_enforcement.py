"""
Serialization enforcement tests.

These tests ensure that ALL instance attributes on game objects
are included in to_dict()/from_dict(). They fail CI when someone
adds a field but forgets serialization.

Run after adding ANY new field to ANY model class.

The rule: **"If it exists on the object, it must serialize."**
"""

import pytest
from typing import Set, Any, Type
from dataclasses import fields, is_dataclass

from backend.models.marshal import Marshal, StrategicOrder, StrategicCondition, Stance
from backend.models.world_state import WorldState
from backend.models.region import Region
from backend.models.trust import Trust
from backend.models.authority import AuthorityTracker
from backend.commands.vindication import VindicationTracker


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_instance_attributes(obj: Any) -> Set[str]:
    """
    Get all instance attributes, excluding private/dunder.

    For dataclasses, uses fields().
    For regular classes, uses vars().
    """
    if is_dataclass(obj):
        return {f.name for f in fields(obj)}
    return {k for k in vars(obj).keys() if not k.startswith('_')}


def get_serialized_keys(obj: Any) -> Set[str]:
    """Get keys from to_dict() output."""
    if not hasattr(obj, 'to_dict'):
        raise AttributeError(f"{type(obj).__name__} has no to_dict() method")
    return set(obj.to_dict().keys())


def create_fully_populated_marshal() -> Marshal:
    """
    Create marshal with ALL fields set to non-default values.

    This tests that to_dict captures every field, and from_dict
    can restore them.
    """
    marshal = Marshal(
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

    # Set ALL other fields to non-default values
    marshal.starting_strength = 55000
    marshal.morale = 85
    marshal.orders_overridden = 3
    marshal.battles_won = 5
    marshal.battles_lost = 2
    marshal.just_retreated = True

    # Disobedience system
    marshal.trust.set(65)
    marshal.vindication_score = 2
    marshal.recent_battles = ["victory", "defeat", "victory"]
    marshal.recent_overrides = [True, False, True, False, True]

    # Autonomy system
    marshal.autonomous = True
    marshal.autonomy_turns = 2
    marshal.autonomy_reason = "redemption"
    marshal.redemption_pending = True
    marshal.autonomous_battles_won = 2
    marshal.autonomous_battles_lost = 1
    marshal.autonomous_regions_captured = 1
    marshal.trust_warning_shown = True

    # Relationships
    marshal.relationships = {"Davout": 1, "Grouchy": -1}

    # Tactical state
    marshal.drilling = True
    marshal.drilling_locked = True
    marshal.drill_complete_turn = 5
    marshal.shock_bonus = 2
    marshal.strategic_combat_bonus = 1
    marshal.strategic_defense_bonus = 1

    # Precision execution
    marshal.precision_execution_active = True
    marshal.precision_execution_turns = 2

    # Strategic orders
    marshal.strategic_order = StrategicOrder(
        command_type="MOVE_TO",
        target="Vienna",
        target_type="region",
        started_turn=3,
        original_command="March to Vienna",
        path=["Paris", "Lyon", "Milan", "Vienna"]
    )
    marshal.pending_interrupt = {"type": "blocked_path", "location": "Rhine"}

    # Combat tracking
    marshal.in_combat_this_turn = True
    marshal.last_combat_turn = 4
    marshal.last_combat_result = "victory"
    marshal.last_combat_location = "Belgium"

    # Fortify state
    marshal.fortified = True
    marshal.fortify_expires_turn = 10
    marshal.defense_bonus = 15

    # Retreat state
    marshal.retreating = True
    marshal.retreat_recovery = 2
    marshal.retreated_this_turn = True

    # Broken state
    marshal.broken = True
    marshal.broken_recovery = 3

    # Stance
    marshal.stance = Stance.AGGRESSIVE

    # Cavalry-specific
    marshal.turns_in_defensive_stance = 2
    marshal.turns_fortified = 1
    marshal.turns_defensive = 3

    # Davout-specific
    marshal.counter_punch_available = True
    marshal.counter_punch_turns = 1

    # Grouchy-specific
    marshal.holding_position = True
    marshal.hold_region = "Waterloo"

    # Recklessness
    marshal.recklessness = 3
    marshal.pending_glorious_charge = True
    marshal.pending_charge_target = "Wellington"

    # Exhaustion
    marshal.attacks_this_turn = 2

    return marshal


# ============================================================================
# MARSHAL ENFORCEMENT
# ============================================================================

class TestMarshalSerializationEnforcement:
    """Ensure Marshal serialization stays complete as fields are added."""

    # Properties that are computed, not stored state
    KNOWN_EXCLUSIONS = {
        'is_reckless_cavalry',     # Computed property
        'in_strategic_mode',       # Computed property
        'strategic_command_type',  # Computed property
    }

    def test_all_marshal_fields_serialized(self):
        """Every Marshal instance attribute must be in to_dict()."""
        marshal = create_fully_populated_marshal()

        instance_attrs = get_instance_attributes(marshal)
        serialized_keys = get_serialized_keys(marshal)

        attrs_to_check = instance_attrs - self.KNOWN_EXCLUSIONS
        missing = attrs_to_check - serialized_keys

        assert not missing, (
            f"\n{'='*60}\n"
            f"SERIALIZATION INCOMPLETE: Marshal\n"
            f"{'='*60}\n"
            f"Fields not in to_dict(): {sorted(missing)}\n\n"
            f"Fix: Add these fields to Marshal.to_dict() AND from_dict()\n"
            f"Docs: Update docs/MODDING_FORMAT.md and docs/SAVE_FORMAT_REFERENCE.md\n"
            f"{'='*60}"
        )

    def test_marshal_roundtrip_preserves_all_fields(self):
        """Serialize -> deserialize must preserve every field."""
        original = create_fully_populated_marshal()

        data = original.to_dict()
        restored = Marshal.from_dict(data)

        original_attrs = get_instance_attributes(original) - self.KNOWN_EXCLUSIONS

        for attr in original_attrs:
            original_val = getattr(original, attr)
            restored_val = getattr(restored, attr)

            # Handle Trust objects
            if hasattr(original_val, 'value') and hasattr(restored_val, 'value'):
                assert restored_val.value == original_val.value, (
                    f"Field '{attr}' not preserved in roundtrip:\n"
                    f"  Original: {original_val.value}\n"
                    f"  Restored: {restored_val.value}"
                )
                continue

            # Handle StrategicOrder
            if hasattr(original_val, 'to_dict') and original_val is not None:
                original_dict = original_val.to_dict()
                restored_dict = restored_val.to_dict() if restored_val else None
                assert restored_dict == original_dict, (
                    f"Field '{attr}' not preserved in roundtrip:\n"
                    f"  Original: {original_dict}\n"
                    f"  Restored: {restored_dict}"
                )
                continue

            # Handle Stance enum
            if isinstance(original_val, Stance):
                assert restored_val == original_val, (
                    f"Field '{attr}' not preserved in roundtrip:\n"
                    f"  Original: {original_val}\n"
                    f"  Restored: {restored_val}"
                )
                continue

            assert restored_val == original_val, (
                f"Field '{attr}' not preserved in roundtrip:\n"
                f"  Original: {original_val!r}\n"
                f"  Restored: {restored_val!r}"
            )


# ============================================================================
# STRATEGIC ORDER ENFORCEMENT
# ============================================================================

class TestStrategicOrderSerializationEnforcement:
    """Ensure StrategicOrder serialization stays complete."""

    def test_all_strategic_order_fields_serialized(self):
        """Every StrategicOrder field must be in to_dict()."""
        order = StrategicOrder(
            command_type="PURSUE",
            target="Blucher",
            target_type="enemy_marshal",
            started_turn=1,
            original_command="Pursue Blucher",
            path=["Paris", "Rhine", "Berlin"],
            follow_if_moves=True,
            join_combat=True,
            target_snapshot_location="Berlin",
            attack_on_arrival=True,
            condition=StrategicCondition(
                max_turns=5,
                until_marshal_destroyed="Blucher",
                until_battle_won=True
            ),
            last_combat_enemy="Blucher",
            last_combat_turn=3,
            last_combat_result="stalemate"
        )

        instance_attrs = get_instance_attributes(order)
        serialized_keys = get_serialized_keys(order)

        missing = instance_attrs - serialized_keys

        assert not missing, (
            f"\n{'='*60}\n"
            f"SERIALIZATION INCOMPLETE: StrategicOrder\n"
            f"{'='*60}\n"
            f"Fields not in to_dict(): {sorted(missing)}\n\n"
            f"Fix: Add to StrategicOrder.to_dict() and from_dict()\n"
            f"{'='*60}"
        )

    def test_strategic_order_roundtrip(self):
        """Roundtrip must preserve all fields."""
        original = StrategicOrder(
            command_type="HOLD",
            target="Belgium",
            target_type="region",
            started_turn=2,
            original_command="Hold Belgium",
            path=["Paris", "Belgium"],
            condition=StrategicCondition(max_turns=3)
        )

        data = original.to_dict()
        restored = StrategicOrder.from_dict(data)

        for attr in get_instance_attributes(original):
            original_val = getattr(original, attr)
            restored_val = getattr(restored, attr)

            if hasattr(original_val, 'to_dict') and original_val:
                original_val = original_val.to_dict()
                restored_val = restored_val.to_dict() if restored_val else None

            assert restored_val == original_val, (
                f"StrategicOrder.{attr} not preserved: {original_val} != {restored_val}"
            )


# ============================================================================
# STRATEGIC CONDITION ENFORCEMENT
# ============================================================================

class TestStrategicConditionSerializationEnforcement:
    """Ensure StrategicCondition serialization stays complete."""

    def test_all_strategic_condition_fields_serialized(self):
        """Every StrategicCondition field must be in to_dict()."""
        condition = StrategicCondition(
            max_turns=5,
            until_marshal_arrives="Ney",
            until_marshal_destroyed="Wellington",
            until_battle_won=True,
            until_relieved=True
        )

        instance_attrs = get_instance_attributes(condition)
        serialized_keys = get_serialized_keys(condition)

        missing = instance_attrs - serialized_keys

        assert not missing, (
            f"StrategicCondition fields not in to_dict(): {sorted(missing)}"
        )


# ============================================================================
# WORLD STATE ENFORCEMENT
# ============================================================================

class TestWorldStateSerializationEnforcement:
    """Ensure WorldState serialization stays complete."""

    def test_all_world_state_fields_serialized(self):
        """Every WorldState field must be in to_dict()."""
        world = WorldState(player_nation="France")

        # Populate with some state
        world.current_turn = 5
        world.gold = 2000
        world.game_over = False
        world.victory = None
        world.actions_remaining = 2
        world.bonus_actions = 1
        world.pending_objection = {"type": "attack", "marshal": "Ney"}
        world.pending_redemption = {"marshal": "Davout", "options": []}
        world.battles_this_turn = [{"attacker": "Ney", "defender": "Wellington"}]
        world.command_history = [{"turn": 1, "command": "attack"}]

        instance_attrs = get_instance_attributes(world)
        serialized_keys = get_serialized_keys(world)

        # WorldState may have some internal state that shouldn't serialize
        KNOWN_EXCLUSIONS: Set[str] = set()
        # Add any computed properties here as needed

        attrs_to_check = instance_attrs - KNOWN_EXCLUSIONS
        missing = attrs_to_check - serialized_keys

        assert not missing, (
            f"\n{'='*60}\n"
            f"SERIALIZATION INCOMPLETE: WorldState\n"
            f"{'='*60}\n"
            f"Fields not in to_dict(): {sorted(missing)}\n\n"
            f"Fix: Add to WorldState.to_dict() and from_dict()\n"
            f"{'='*60}"
        )


# ============================================================================
# REGION ENFORCEMENT
# ============================================================================

class TestRegionSerializationEnforcement:
    """Ensure Region serialization stays complete."""

    def test_all_region_fields_serialized(self):
        """Every Region field must be in to_dict()."""
        region = Region(
            name="TestRegion",
            adjacent_regions=["Paris", "Lyon"],
            income_value=150,
            is_capital=True
        )
        region.controller = "France"
        region.garrison_strength = 5000

        instance_attrs = get_instance_attributes(region)
        serialized_keys = get_serialized_keys(region)

        missing = instance_attrs - serialized_keys

        assert not missing, (
            f"Region fields not in to_dict(): {sorted(missing)}"
        )


# ============================================================================
# TRUST ENFORCEMENT
# ============================================================================

class TestTrustSerializationEnforcement:
    """Ensure Trust serialization stays complete."""

    def test_all_trust_fields_serialized(self):
        """Every Trust field must be in to_dict()."""
        trust = Trust(75)

        # Trust uses _value internally, so check the public interface
        data = trust.to_dict()
        assert "value" in data, "Trust.to_dict() must include 'value'"

        restored = Trust.from_dict(data)
        assert restored.value == trust.value, "Trust roundtrip failed"


# ============================================================================
# AUTHORITY TRACKER ENFORCEMENT
# ============================================================================

class TestAuthorityTrackerSerializationEnforcement:
    """Ensure AuthorityTracker serialization stays complete."""

    def test_all_authority_tracker_fields_serialized(self):
        """Every AuthorityTracker field must be in to_dict()."""
        tracker = AuthorityTracker()
        tracker.authority = 85
        tracker.recent_responses = ["trust", "insist", "compromise"]

        instance_attrs = get_instance_attributes(tracker)
        serialized_keys = get_serialized_keys(tracker)

        # Exclude private attributes
        attrs_to_check = {a for a in instance_attrs if not a.startswith('_')}
        missing = attrs_to_check - serialized_keys

        assert not missing, (
            f"AuthorityTracker fields not in to_dict(): {sorted(missing)}"
        )


# ============================================================================
# VINDICATION TRACKER ENFORCEMENT
# ============================================================================

class TestVindicationTrackerSerializationEnforcement:
    """Ensure VindicationTracker serialization stays complete."""

    def test_all_vindication_tracker_fields_serialized(self):
        """Every VindicationTracker field must be in to_dict()."""
        tracker = VindicationTracker()
        tracker.pending = {"Ney": {"choice": "trust", "original_order": {}}}
        tracker.history = [{"marshal": "Ney", "result": "vindicated"}]

        instance_attrs = get_instance_attributes(tracker)
        serialized_keys = get_serialized_keys(tracker)

        missing = instance_attrs - serialized_keys

        assert not missing, (
            f"VindicationTracker fields not in to_dict(): {sorted(missing)}"
        )


# ============================================================================
# META TEST: ALL SERIALIZABLE CLASSES HAVE ENFORCEMENT
# ============================================================================

# List of all classes that should have serialization
# ADD NEW CLASSES HERE when created (diplomacy, vassals, etc.)
SERIALIZABLE_CLASSES: list[Type] = [
    Marshal,
    StrategicOrder,
    StrategicCondition,
    WorldState,
    Region,
    Trust,
    AuthorityTracker,
    VindicationTracker,
    # Future classes - uncomment when implemented:
    # Treaty,
    # Alliance,
    # Vassal,
    # Character,
]


class TestSerializationCoverage:
    """Ensure all serializable classes have required methods."""

    def test_all_classes_have_to_dict(self):
        """Every serializable class must have to_dict()."""
        missing = []
        for cls in SERIALIZABLE_CLASSES:
            if not hasattr(cls, 'to_dict'):
                missing.append(cls.__name__)

        assert not missing, (
            f"Classes without to_dict(): {missing}\n"
            f"Add to_dict() method to these classes."
        )

    def test_all_classes_have_from_dict(self):
        """Every serializable class must have from_dict()."""
        missing = []
        for cls in SERIALIZABLE_CLASSES:
            if not hasattr(cls, 'from_dict'):
                missing.append(cls.__name__)

        assert not missing, (
            f"Classes without from_dict(): {missing}\n"
            f"Add @classmethod from_dict() to these classes."
        )


# ============================================================================
# FUTURE MODEL TEMPLATE
# ============================================================================
# Copy this template when adding new serializable models:
#
# class TestNEWMODELSerializationEnforcement:
#     """Ensure NEWMODEL serialization stays complete."""
#
#     def test_all_newmodel_fields_serialized(self):
#         """Every NEWMODEL field must be in to_dict()."""
#         obj = NEWMODEL(...)
#
#         instance_attrs = get_instance_attributes(obj)
#         serialized_keys = get_serialized_keys(obj)
#
#         missing = instance_attrs - serialized_keys
#
#         assert not missing, (
#             f"NEWMODEL fields not in to_dict(): {sorted(missing)}"
#         )
#
# Then add NEWMODEL to SERIALIZABLE_CLASSES list above.


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
