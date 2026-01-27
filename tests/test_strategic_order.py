"""
Tests for StrategicOrder and StrategicCondition dataclasses (Phase 5.2).

Run with: pytest tests/test_strategic_order.py -v
"""

import pytest
from backend.models.marshal import (
    Marshal, StrategicOrder, StrategicCondition
)
from backend.models.world_state import WorldState


class TestStrategicCondition:
    """Tests for StrategicCondition dataclass."""

    def test_condition_to_dict_roundtrip(self):
        """Condition serializes and deserializes correctly."""
        condition = StrategicCondition(
            max_turns=5,
            until_marshal_arrives="Ney",
            until_battle_won=True
        )
        data = condition.to_dict()
        restored = StrategicCondition.from_dict(data)

        assert restored.max_turns == 5
        assert restored.until_marshal_arrives == "Ney"
        assert restored.until_battle_won is True
        assert restored.until_relieved is False

    def test_condition_defaults(self):
        """Condition has correct defaults."""
        condition = StrategicCondition()
        assert condition.max_turns is None
        assert condition.until_marshal_arrives is None
        assert condition.until_battle_won is False


class TestStrategicOrder:
    """Tests for StrategicOrder dataclass."""

    def test_order_creation(self):
        """Can create a basic strategic order."""
        order = StrategicOrder(
            command_type="MOVE_TO",
            target="Vienna",
            target_type="region",
            started_turn=1,
            original_command="March to Vienna"
        )
        assert order.command_type == "MOVE_TO"
        assert order.target == "Vienna"
        assert order.path == []

    def test_order_with_condition(self):
        """Order can have a condition."""
        condition = StrategicCondition(max_turns=3)
        order = StrategicOrder(
            command_type="HOLD",
            target="Belgium",
            target_type="region",
            started_turn=1,
            original_command="Hold Belgium for 3 turns",
            condition=condition
        )
        assert order.condition.max_turns == 3

    def test_order_to_dict_roundtrip(self):
        """Order serializes and deserializes correctly."""
        condition = StrategicCondition(until_relieved=True)
        order = StrategicOrder(
            command_type="HOLD",
            target="Paris",
            target_type="region",
            started_turn=2,
            original_command="Hold Paris until relieved",
            path=["Belgium", "Paris"],
            attack_on_arrival=True,
            condition=condition
        )

        data = order.to_dict()
        restored = StrategicOrder.from_dict(data)

        assert restored.command_type == "HOLD"
        assert restored.target == "Paris"
        assert restored.path == ["Belgium", "Paris"]
        assert restored.attack_on_arrival is True
        assert restored.condition.until_relieved is True

    def test_order_combat_loop_fields(self):
        """Order tracks combat for loop prevention."""
        order = StrategicOrder(
            command_type="PURSUE",
            target="Wellington",
            target_type="marshal",
            started_turn=1,
            original_command="Pursue Wellington"
        )

        order.last_combat_enemy = "Wellington"
        order.last_combat_turn = 3
        order.last_combat_result = "stalemate"

        data = order.to_dict()
        restored = StrategicOrder.from_dict(data)

        assert restored.last_combat_enemy == "Wellington"
        assert restored.last_combat_turn == 3
        assert restored.last_combat_result == "stalemate"

    def test_order_marshal_target_snapshot(self):
        """MOVE_TO with marshal target stores snapshot location."""
        order = StrategicOrder(
            command_type="MOVE_TO",
            target="Ney",
            target_type="marshal",
            started_turn=1,
            original_command="Move to Ney",
            target_snapshot_location="Belgium"
        )

        assert order.target == "Ney"
        assert order.target_type == "marshal"
        assert order.target_snapshot_location == "Belgium"

        # Roundtrip
        data = order.to_dict()
        restored = StrategicOrder.from_dict(data)
        assert restored.target_snapshot_location == "Belgium"


class TestMarshalStrategicFields:
    """Tests for strategic fields on Marshal."""

    def test_in_strategic_mode_false_by_default(self):
        """Marshal not in strategic mode by default."""
        marshal = Marshal("Ney", "Paris", 10000, "aggressive")
        assert marshal.in_strategic_mode is False
        assert marshal.strategic_command_type is None

    def test_in_strategic_mode_true_with_order(self):
        """Marshal in strategic mode when order assigned."""
        marshal = Marshal("Ney", "Paris", 10000, "aggressive")
        marshal.strategic_order = StrategicOrder(
            command_type="MOVE_TO",
            target="Vienna",
            target_type="region",
            started_turn=1,
            original_command="March to Vienna"
        )
        assert marshal.in_strategic_mode is True
        assert marshal.strategic_command_type == "MOVE_TO"

    def test_marshal_serialization_with_strategic_order(self):
        """Marshal with strategic order serializes correctly."""
        marshal = Marshal("Grouchy", "Paris", 20000, "literal")
        marshal.strategic_order = StrategicOrder(
            command_type="PURSUE",
            target="Blucher",
            target_type="marshal",
            started_turn=1,
            original_command="Pursue the Prussians"
        )
        marshal.last_combat_result = "victory"

        data = marshal.to_dict()
        assert data.get("strategic_order") is not None
        assert data["strategic_order"]["command_type"] == "PURSUE"
        assert data["last_combat_result"] == "victory"

    def test_marshal_from_dict_roundtrip(self):
        """Marshal deserializes strategic order correctly."""
        marshal = Marshal("Grouchy", "Paris", 20000, "literal")
        marshal.strategic_order = StrategicOrder(
            command_type="HOLD",
            target="Belgium",
            target_type="region",
            started_turn=2,
            original_command="Hold Belgium"
        )
        marshal.last_combat_location = "Belgium"

        data = marshal.to_dict()
        restored = Marshal.from_dict(data)

        assert restored.in_strategic_mode is True
        assert restored.strategic_command_type == "HOLD"
        assert restored.last_combat_location == "Belgium"


class TestWorldStateBattleTracking:
    """Tests for battle tracking in WorldState."""

    def test_record_battle(self):
        """Can record a battle."""
        world = WorldState()
        world.record_battle(
            location="Belgium",
            attacker="Ney",
            defender="Wellington",
            result="attacker_victory"
        )

        assert len(world.battles_this_turn) == 1
        assert world.battles_this_turn[0]["location"] == "Belgium"
        assert world.battles_this_turn[0]["attacker"] == "Ney"

    def test_get_battles_within_range(self):
        """Can find battles within range."""
        world = WorldState()
        world.record_battle(
            location="Belgium",
            attacker="Ney",
            defender="Wellington",
            result="ongoing"
        )

        nearby = world.get_battles_within_range("Paris", 2)
        assert isinstance(nearby, list)
        # Belgium is adjacent to Paris (distance 1), so should be found
        assert len(nearby) >= 1

    def test_get_battles_out_of_range(self):
        """Battles out of range not returned."""
        world = WorldState()
        world.record_battle(
            location="Spain",
            attacker="Ney",
            defender="Wellington",
            result="ongoing"
        )

        nearby = world.get_battles_within_range("Rhine", 1)
        # Spain and Rhine are far apart
        assert len(nearby) == 0

    def test_clear_turn_battles(self):
        """clear_turn_battles resets tracking."""
        world = WorldState()
        world.record_battle("Belgium", "Ney", "Wellington", "victory")

        ney = world.get_marshal("Ney")
        if ney:
            ney.in_combat_this_turn = True

        world.clear_turn_battles()

        assert world.battles_this_turn == []
        if ney:
            assert ney.in_combat_this_turn is False
