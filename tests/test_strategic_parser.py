"""
Tests for strategic command parsing (Phase 5.2-B).

Tests detection of MOVE_TO, PURSUE, HOLD, SUPPORT commands,
target classification, condition parsing, and auto-conversion logic.

Run with: pytest tests/test_strategic_parser.py -v
"""

import pytest
from backend.ai.strategic_parser import (
    detect_strategic_command,
    _detect_strategic_type,
    _classify_target,
    _parse_condition,
    _extract_target_text,
)
from backend.models.world_state import WorldState
from backend.commands.parser import CommandParser


class TestStrategicTypeDetection:
    """Tests for _detect_strategic_type()."""

    def test_march_to_is_move_to(self):
        assert _detect_strategic_type("march to vienna") == "MOVE_TO"

    def test_advance_to_is_move_to(self):
        assert _detect_strategic_type("advance to belgium") == "MOVE_TO"

    def test_fall_back_to_is_move_to(self):
        assert _detect_strategic_type("fall back to paris") == "MOVE_TO"

    def test_pursue_detected(self):
        assert _detect_strategic_type("pursue wellington") == "PURSUE"

    def test_chase_detected(self):
        assert _detect_strategic_type("chase the enemy") == "PURSUE"

    def test_hunt_down_detected(self):
        assert _detect_strategic_type("hunt down blucher") == "PURSUE"

    def test_hold_detected(self):
        assert _detect_strategic_type("hold belgium") == "HOLD"

    def test_hold_position_detected(self):
        assert _detect_strategic_type("hold position at belgium") == "HOLD"

    def test_guard_detected(self):
        assert _detect_strategic_type("guard paris") == "HOLD"

    def test_support_detected(self):
        assert _detect_strategic_type("support ney") == "SUPPORT"

    def test_link_up_detected(self):
        assert _detect_strategic_type("link up with davout") == "SUPPORT"

    def test_attack_is_not_strategic(self):
        """Tactical 'attack' should NOT be detected as strategic."""
        assert _detect_strategic_type("attack wellington") is None

    def test_move_is_not_strategic(self):
        """Tactical 'move to' is NOT in strategic keywords."""
        # "move to" is intentionally tactical, "march to" is strategic
        assert _detect_strategic_type("move to belgium") is None

    def test_plain_defend_is_not_strategic(self):
        """Bare 'defend' without strategic context is not strategic."""
        # "defend" alone is not in STRATEGIC_KEYWORDS
        assert _detect_strategic_type("defend") is None


class TestTargetClassification:
    """Tests for _classify_target() with WorldState."""

    def setup_method(self):
        self.world = WorldState()

    def test_region_target(self):
        """Region name classified as target_type='region'."""
        result = _classify_target("Belgium", "Grouchy", self.world)
        assert result["target"] == "Belgium"
        assert result["target_type"] == "region"
        assert result["convert_to_pursue"] is False

    def test_region_case_insensitive(self):
        """Region matching is case-insensitive."""
        result = _classify_target("belgium", "Grouchy", self.world)
        assert result["target"] == "Belgium"
        assert result["target_type"] == "region"

    def test_friendly_marshal_gets_snapshot(self):
        """Friendly marshal target gets snapshot of their current location."""
        # Ney is French (same as Grouchy), located somewhere on the map
        ney = self.world.get_marshal("Ney")
        result = _classify_target("Ney", "Grouchy", self.world)
        assert result["target"] == "Ney"
        assert result["target_type"] == "marshal"
        assert result["target_snapshot_location"] == ney.location
        assert result["convert_to_pursue"] is False

    def test_enemy_marshal_converts_to_pursue(self):
        """Enemy marshal target sets convert_to_pursue=True."""
        result = _classify_target("Wellington", "Grouchy", self.world)
        assert result["target"] == "Wellington"
        assert result["target_type"] == "marshal"
        assert result["target_snapshot_location"] is None
        assert result["convert_to_pursue"] is True

    def test_generic_target(self):
        """Generic phrases classified as target_type='generic'."""
        result = _classify_target("the enemy", "Grouchy", self.world)
        assert result["target_type"] == "generic"

    def test_prussians_generic(self):
        result = _classify_target("the prussians", "Grouchy", self.world)
        assert result["target_type"] == "generic"

    def test_unknown_target_defaults_to_region(self):
        """Unknown target treated as region (may fail at execution)."""
        result = _classify_target("mordor", "Grouchy", self.world)
        assert result["target_type"] == "region"
        assert result["target"] == "Mordor"  # Title-cased


class TestConditionParsing:
    """Tests for _parse_condition()."""

    def test_until_marshal_arrives(self):
        result = _parse_condition("hold belgium until ney arrives", "Belgium")
        assert result is not None
        assert result["until_marshal_arrives"] == "Ney"

    def test_until_relieved(self):
        result = _parse_condition("hold until relieved", "Belgium")
        assert result is not None
        assert result["until_relieved"] is True

    def test_until_destroyed(self):
        result = _parse_condition("pursue until destroyed", "Wellington")
        assert result is not None
        assert result["until_marshal_destroyed"] == "Wellington"

    def test_to_destruction(self):
        result = _parse_condition("pursue wellington to destruction", "Wellington")
        assert result is not None
        assert result["until_marshal_destroyed"] == "Wellington"

    def test_max_turns(self):
        result = _parse_condition("hold belgium for 3 turns", "Belgium")
        assert result is not None
        assert result["max_turns"] == 3

    def test_until_battle_won(self):
        result = _parse_condition("support ney until battle won", "Ney")
        assert result is not None
        assert result["until_battle_won"] is True

    def test_until_victory(self):
        result = _parse_condition("support until victory", "Ney")
        assert result is not None
        assert result["until_battle_won"] is True

    def test_no_condition(self):
        """Command without condition returns None."""
        result = _parse_condition("march to vienna", "Vienna")
        assert result is None


class TestFullDetection:
    """Integration tests for detect_strategic_command()."""

    def setup_method(self):
        self.world = WorldState()

    def test_march_to_region(self):
        """'march to Vienna' → strategic MOVE_TO region."""
        result = detect_strategic_command("Grouchy, march to Vienna", "Grouchy", self.world)
        assert result is not None
        assert result["is_strategic"] is True
        assert result["strategic_type"] == "MOVE_TO"
        assert result["target"] == "Vienna"
        assert result["target_type"] == "region"

    def test_march_to_friendly_marshal(self):
        """'march to Ney' → MOVE_TO with snapshot."""
        ney = self.world.get_marshal("Ney")
        result = detect_strategic_command("Grouchy, march to Ney", "Grouchy", self.world)
        assert result is not None
        assert result["strategic_type"] == "MOVE_TO"
        assert result["target"] == "Ney"
        assert result["target_type"] == "marshal"
        assert result["target_snapshot_location"] == ney.location

    def test_march_to_enemy_becomes_pursue(self):
        """'march to Wellington' auto-converts to PURSUE."""
        result = detect_strategic_command("Grouchy, march to Wellington", "Grouchy", self.world)
        assert result is not None
        assert result["strategic_type"] == "PURSUE"
        assert result["target"] == "Wellington"
        assert result["target_type"] == "marshal"
        assert result["target_snapshot_location"] is None

    def test_pursue_enemy(self):
        """'pursue Wellington' → PURSUE."""
        result = detect_strategic_command("Grouchy, pursue Wellington", "Grouchy", self.world)
        assert result is not None
        assert result["strategic_type"] == "PURSUE"
        assert result["target"] == "Wellington"

    def test_hold_region_with_condition(self):
        """'hold Belgium until Ney arrives' → HOLD with condition."""
        result = detect_strategic_command(
            "Grouchy, hold Belgium until Ney arrives", "Grouchy", self.world
        )
        assert result is not None
        assert result["strategic_type"] == "HOLD"
        assert result["target"] == "Belgium"
        assert result["target_type"] == "region"
        assert result["condition"] is not None
        assert result["condition"]["until_marshal_arrives"] == "Ney"

    def test_hold_no_target_uses_current_location(self):
        """'hold' with no target uses marshal's current location."""
        grouchy = self.world.get_marshal("Grouchy")
        result = detect_strategic_command("Grouchy, hold position", "Grouchy", self.world)
        assert result is not None
        assert result["strategic_type"] == "HOLD"
        assert result["target"] == grouchy.location

    def test_support_friendly(self):
        """'support Ney until battle won' → SUPPORT with condition."""
        result = detect_strategic_command(
            "Grouchy, support Ney until battle won", "Grouchy", self.world
        )
        assert result is not None
        assert result["strategic_type"] == "SUPPORT"
        assert result["target"] == "Ney"
        assert result["condition"]["until_battle_won"] is True

    def test_attack_not_strategic(self):
        """'attack Wellington' is tactical, not strategic."""
        result = detect_strategic_command("Grouchy, attack Wellington", "Grouchy", self.world)
        assert result is None

    def test_attack_on_arrival(self):
        """'march to Belgium and attack' sets attack_on_arrival."""
        result = detect_strategic_command(
            "Grouchy, march to Belgium and attack", "Grouchy", self.world
        )
        assert result is not None
        assert result["attack_on_arrival"] is True

    def test_pursue_until_destroyed(self):
        """'pursue Wellington until destroyed'."""
        result = detect_strategic_command(
            "Grouchy, pursue Wellington until destroyed", "Grouchy", self.world
        )
        assert result is not None
        assert result["strategic_type"] == "PURSUE"
        assert result["condition"]["until_marshal_destroyed"] == "Wellington"

    def test_hold_for_turns(self):
        """'hold Belgium for 3 turns'."""
        result = detect_strategic_command(
            "Grouchy, hold Belgium for 3 turns", "Grouchy", self.world
        )
        assert result is not None
        assert result["condition"]["max_turns"] == 3

    def test_generic_target(self):
        """'pursue the enemy' → generic target."""
        result = detect_strategic_command(
            "Grouchy, pursue the enemy", "Grouchy", self.world
        )
        assert result is not None
        assert result["strategic_type"] == "PURSUE"
        assert result["target_type"] == "generic"


class TestParserIntegration:
    """Tests that strategic detection works through the full parser flow."""

    def setup_method(self):
        self.parser = CommandParser(use_real_llm=False)
        self.world = WorldState()

    def test_parser_detects_strategic_with_world(self):
        """Parser marks strategic commands when world is provided."""
        result = self.parser.parse("Grouchy, march to Vienna", world=self.world)
        assert result["success"] is True
        assert result.get("is_strategic") is True
        assert result.get("strategic_type") == "MOVE_TO"

    def test_parser_no_strategic_without_world(self):
        """Without world, no strategic detection (backward compat)."""
        result = self.parser.parse("Grouchy, march to Vienna")
        assert result["success"] is True
        assert result.get("is_strategic") is not True

    def test_parser_tactical_stays_tactical(self):
        """Tactical 'attack' not marked strategic even with world."""
        result = self.parser.parse("Ney, attack Wellington", world=self.world)
        assert result["success"] is True
        assert result.get("is_strategic") is not True

    def test_parser_strategic_overrides_target(self):
        """Strategic parser provides canonical target name."""
        result = self.parser.parse("Grouchy, march to Belgium", world=self.world)
        assert result["success"] is True
        assert result["command"]["target"] == "Belgium"
        assert result.get("is_strategic") is True
