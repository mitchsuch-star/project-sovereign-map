"""
Mock-based tests for LLM strategic command parsing integration.

Tests verify:
1. Fast parser detects expanded strategic keywords
2. LLM response parsing populates strategic fields in ParseResult
3. Strategic parser processes LLM results correctly
4. End-to-end: command text → ParseResult with strategic fields

Run: pytest tests/test_llm_strategic.py -v
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ai.schemas import ParseResult
from backend.ai.providers import json_to_parse_result
from backend.ai.strategic_parser import (
    detect_strategic_command, _detect_strategic_type, _classify_target,
    _add_interpretation, _parse_condition
)
from backend.models.world_state import WorldState


# ══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def world():
    return WorldState()


# ══════════════════════════════════════════════════════════════════════════════
# FAST PARSER: EXPANDED KEYWORD DETECTION
# ══════════════════════════════════════════════════════════════════════════════

class TestExpandedKeywords:
    """Test that expanded STRATEGIC_KEYWORDS catch more phrases."""

    # MOVE_TO expansions
    @pytest.mark.parametrize("phrase", [
        "campaign toward vienna",
        "push toward the rhine",
        "sweep toward belgium",
        "press toward bavaria",
        "drive toward lyon",
        "advance toward marseille",
        "march toward milan",
        "head toward geneva",
        "deploy to vienna",
        "press on to bavaria",
        "make your way to rhine",
    ])
    def test_move_to_new_keywords(self, phrase):
        result = _detect_strategic_type(phrase)
        assert result == "MOVE_TO", f"'{phrase}' should detect as MOVE_TO, got {result}"

    # PURSUE expansions
    @pytest.mark.parametrize("phrase", [
        "hunt down wellington",
        "track down the prussians",
        "run down blucher",
        "follow and destroy wellington",
        "harry the enemy",
        "hound the retreating forces",
        "shadow wellington",
        "drive against blucher",
    ])
    def test_pursue_new_keywords(self, phrase):
        result = _detect_strategic_type(phrase)
        assert result == "PURSUE", f"'{phrase}' should detect as PURSUE, got {result}"

    # HOLD expansions
    @pytest.mark.parametrize("phrase", [
        "hold at all costs",
        "stand fast at belgium",
        "stand firm",
        "maintain position at rhine",
        "anchor at lyon",
        "secure and hold vienna",
        "hold your ground",
        "don't give ground",
        "defend and hold belgium",
    ])
    def test_hold_new_keywords(self, phrase):
        result = _detect_strategic_type(phrase)
        assert result == "HOLD", f"'{phrase}' should detect as HOLD, got {result}"

    # SUPPORT expansions
    @pytest.mark.parametrize("phrase", [
        "rally to ney",
        "come to the aid of davout",
        "bolster ney's position",
        "shore up the defense",
        "combine with davout",
        "move to reinforce ney",
    ])
    def test_support_new_keywords(self, phrase):
        result = _detect_strategic_type(phrase)
        assert result == "SUPPORT", f"'{phrase}' should detect as SUPPORT, got {result}"

    # Ensure bare "defend" is NOT strategic
    def test_bare_defend_is_not_strategic(self):
        result = _detect_strategic_type("defend")
        assert result is None, "Bare 'defend' should NOT be strategic"

    def test_defend_position_is_not_strategic(self):
        """'defend my position' without HOLD keywords stays tactical."""
        result = _detect_strategic_type("defend my position")
        assert result is None, "'defend my position' should NOT be strategic"

    def test_defend_and_hold_is_strategic(self):
        """'defend and hold' IS strategic HOLD."""
        result = _detect_strategic_type("defend and hold belgium")
        assert result == "HOLD"


# ══════════════════════════════════════════════════════════════════════════════
# LLM RESPONSE PARSING: STRATEGIC FIELDS
# ══════════════════════════════════════════════════════════════════════════════

class TestLLMResponseParsing:
    """Test json_to_parse_result maps strategic fields correctly."""

    def test_strategic_move_to_from_llm(self):
        """LLM returns strategic MOVE_TO, fields populate ParseResult."""
        llm_json = {
            "matched": True,
            "command_type": "strategic",
            "marshals": ["Ney"],
            "action": "move",
            "target": "Vienna",
            "is_strategic": True,
            "strategic_type": "MOVE_TO",
            "strategic_condition": None,
            "ambiguity": 15,
            "strategic_score": 60,
            "interpretation": "Standing order: Ney marches to Vienna",
        }
        result = json_to_parse_result(llm_json, "Ney, march to Vienna", "anthropic")

        assert result.matched is True
        assert result.is_strategic is True
        assert result.strategic_type == "MOVE_TO"
        assert result.action == "move"
        assert result.target == "Vienna"
        assert result.ambiguity == 15
        assert result.mode == "anthropic"

    def test_strategic_pursue_with_condition_from_llm(self):
        """LLM returns PURSUE with until_marshal_destroyed condition."""
        llm_json = {
            "matched": True,
            "command_type": "strategic",
            "marshals": ["Grouchy"],
            "action": "attack",
            "target": "Blucher",
            "is_strategic": True,
            "strategic_type": "PURSUE",
            "strategic_condition": {"until_marshal_destroyed": "Blucher"},
            "ambiguity": 10,
            "strategic_score": 75,
            "interpretation": "Pursue Blucher until destroyed",
        }
        result = json_to_parse_result(llm_json, "Pursue Blucher until destroyed", "anthropic")

        assert result.is_strategic is True
        assert result.strategic_type == "PURSUE"
        assert result.strategic_condition == {"until_marshal_destroyed": "Blucher"}

    def test_strategic_hold_with_condition_from_llm(self):
        """LLM returns HOLD with until_marshal_arrives condition."""
        llm_json = {
            "matched": True,
            "command_type": "strategic",
            "marshals": ["Davout"],
            "action": "hold",
            "target": "Belgium",
            "is_strategic": True,
            "strategic_type": "HOLD",
            "strategic_condition": {"until_marshal_arrives": "Ney"},
            "ambiguity": 10,
            "strategic_score": 70,
        }
        result = json_to_parse_result(llm_json, "Hold Belgium until Ney arrives", "anthropic")

        assert result.is_strategic is True
        assert result.strategic_type == "HOLD"
        assert result.strategic_condition["until_marshal_arrives"] == "Ney"

    def test_tactical_command_from_llm(self):
        """LLM returns tactical command, is_strategic=False."""
        llm_json = {
            "matched": True,
            "command_type": "tactical",
            "marshals": ["Ney"],
            "action": "attack",
            "target": "Wellington",
            "is_strategic": False,
            "ambiguity": 5,
            "strategic_score": 40,
        }
        result = json_to_parse_result(llm_json, "Ney attack Wellington", "anthropic")

        assert result.is_strategic is False
        assert result.strategic_type is None
        assert result.action == "attack"

    def test_high_ambiguity_generic_target(self):
        """LLM returns high ambiguity for generic target."""
        llm_json = {
            "matched": True,
            "command_type": "strategic",
            "marshals": ["Grouchy"],
            "action": "attack",
            "target": "the enemy",
            "is_strategic": True,
            "strategic_type": "PURSUE",
            "ambiguity": 70,
            "strategic_score": 50,
        }
        result = json_to_parse_result(llm_json, "Pursue the enemy", "anthropic")

        assert result.ambiguity == 70
        assert result.is_strategic is True

    def test_missing_strategic_fields_default_false(self):
        """LLM omits strategic fields → defaults to not strategic."""
        llm_json = {
            "matched": True,
            "marshals": ["Ney"],
            "action": "attack",
            "target": "Wellington",
            "ambiguity": 10,
        }
        result = json_to_parse_result(llm_json, "attack", "anthropic")

        assert result.is_strategic is False
        assert result.strategic_type is None
        assert result.strategic_condition is None


# ══════════════════════════════════════════════════════════════════════════════
# STRATEGIC PARSER INTEGRATION WITH LLM RESULTS
# ══════════════════════════════════════════════════════════════════════════════

class TestStrategicParserIntegration:
    """Test strategic_parser.py processes commands that LLM would catch."""

    def test_classify_target_region(self, world):
        """_classify_target identifies known regions."""
        result = _classify_target("belgium", "Ney", world)
        assert result["target"] == "Belgium"
        assert result["target_type"] == "region"

    def test_classify_target_enemy_marshal(self, world):
        """_classify_target identifies enemy marshals and sets convert_to_pursue."""
        result = _classify_target("wellington", "Ney", world)
        assert result["target"] == "Wellington"
        assert result["target_type"] == "marshal"
        assert result["convert_to_pursue"] is True

    def test_classify_target_friendly_marshal(self, world):
        """_classify_target identifies friendly marshals with snapshot."""
        result = _classify_target("davout", "Ney", world)
        assert result["target"] == "Davout"
        assert result["target_type"] == "marshal"
        assert result["convert_to_pursue"] is False
        assert result["target_snapshot_location"] is not None

    def test_classify_target_generic(self, world):
        """_classify_target identifies generic enemy references."""
        result = _classify_target("the enemy", "Ney", world)
        assert result["target_type"] == "generic"

    def test_classify_target_unknown_becomes_region(self, world):
        """Unknown target defaults to region type."""
        result = _classify_target("some place", "Ney", world)
        assert result["target_type"] == "region"

    def test_add_interpretation_pursue_generic(self, world):
        """_add_interpretation picks nearest enemy for PURSUE generic."""
        result = {
            "target_type": "generic",
            "strategic_type": "PURSUE",
            "target": "the enemy",
        }
        enriched = _add_interpretation(result, "Ney", world)
        # Should have picked an enemy marshal
        assert enriched.get("interpreted_target") is not None
        assert enriched.get("interpretation_reason") == "nearest"
        assert isinstance(enriched.get("alternatives", []), list)

    def test_add_interpretation_skips_specific(self, world):
        """_add_interpretation does NOT modify specific targets."""
        result = {
            "target_type": "region",
            "strategic_type": "MOVE_TO",
            "target": "Belgium",
        }
        enriched = _add_interpretation(result, "Ney", world)
        assert "interpreted_target" not in enriched

    def test_full_detect_strategic_command(self, world):
        """End-to-end: detect_strategic_command parses creative phrasing."""
        result = detect_strategic_command(
            "campaign toward vienna", "Ney", world
        )
        assert result is not None
        assert result["is_strategic"] is True
        assert result["strategic_type"] == "MOVE_TO"

    def test_full_detect_pursue_with_condition(self, world):
        """End-to-end: detect with condition."""
        result = detect_strategic_command(
            "hunt down wellington until destroyed", "Ney", world
        )
        assert result is not None
        assert result["is_strategic"] is True
        assert result["strategic_type"] == "PURSUE"
        assert result.get("condition", {}).get("until_marshal_destroyed") is not None

    def test_full_detect_hold_with_condition(self, world):
        """End-to-end: hold until arrives."""
        result = detect_strategic_command(
            "stand firm at belgium until ney arrives", "Davout", world
        )
        assert result is not None
        assert result["is_strategic"] is True
        assert result["strategic_type"] == "HOLD"

    def test_full_detect_support_rally(self, world):
        """End-to-end: rally to = SUPPORT."""
        result = detect_strategic_command(
            "rally to ney", "Grouchy", world
        )
        assert result is not None
        assert result["is_strategic"] is True
        assert result["strategic_type"] == "SUPPORT"


# ══════════════════════════════════════════════════════════════════════════════
# CONDITION PARSING
# ══════════════════════════════════════════════════════════════════════════════

class TestConditionParsing:
    """Test _parse_condition extracts conditions from command text."""

    def test_until_marshal_arrives(self):
        result = _parse_condition("hold until ney arrives", "Belgium")
        assert result["until_marshal_arrives"] == "Ney"

    def test_until_relieved(self):
        result = _parse_condition("hold until relieved", "Belgium")
        assert result["until_relieved"] is True

    def test_until_destroyed(self):
        result = _parse_condition("pursue until destroyed", "Wellington")
        assert result["until_marshal_destroyed"] == "Wellington"

    def test_for_n_turns(self):
        result = _parse_condition("hold for 3 turns", "Belgium")
        assert result["max_turns"] == 3

    def test_until_battle_won(self):
        result = _parse_condition("hold until battle won", "Belgium")
        assert result["until_battle_won"] is True

    def test_no_condition(self):
        result = _parse_condition("march to vienna", "Vienna")
        assert result is None


# ══════════════════════════════════════════════════════════════════════════════
# PARSE RESULT SERIALIZATION
# ══════════════════════════════════════════════════════════════════════════════

class TestParseResultRoundtrip:
    """Test ParseResult to_dict/from_dict preserves strategic fields."""

    def test_strategic_parse_result_roundtrip(self):
        """Strategic ParseResult survives to_dict → from_dict."""
        original = ParseResult(
            matched=True,
            command_type="strategic",
            marshals=["Grouchy"],
            action="move",
            target="Rhine",
            is_strategic=True,
            strategic_type="MOVE_TO",
            strategic_condition={"max_turns": 5},
            ambiguity=15,
            strategic_score=60,
            interpreted_target="Rhine",
            interpretation_reason="nearest enemy position",
            alternatives=["Bavaria", "Belgium"],
            mode="anthropic",
            raw_command="march to Rhine",
        )

        d = original.to_dict()
        assert d["is_strategic"] is True
        assert d["strategic_type"] == "MOVE_TO"
        assert d["strategic_condition"] == {"max_turns": 5}
        assert d["interpreted_target"] == "Rhine"
        assert d["alternatives"] == ["Bavaria", "Belgium"]

        restored = ParseResult.from_dict(d)
        assert restored.is_strategic is True
        assert restored.strategic_type == "MOVE_TO"
        assert restored.strategic_condition == {"max_turns": 5}
        assert restored.interpreted_target == "Rhine"
        assert restored.alternatives == ["Bavaria", "Belgium"]

    def test_tactical_parse_result_roundtrip(self):
        """Tactical ParseResult is_strategic=False survives roundtrip."""
        original = ParseResult(
            matched=True,
            marshals=["Ney"],
            action="attack",
            target="Wellington",
            is_strategic=False,
            ambiguity=5,
        )

        d = original.to_dict()
        assert d["is_strategic"] is False
        assert "strategic_type" not in d  # Not included when is_strategic=False

        restored = ParseResult.from_dict(d)
        assert restored.is_strategic is False
        assert restored.strategic_type is None


# ══════════════════════════════════════════════════════════════════════════════
# VALIDATION ALLOWS STRATEGIC
# ══════════════════════════════════════════════════════════════════════════════

class TestValidationAllowsStrategic:
    """Test that validation.py no longer blocks strategic commands."""

    def test_strategic_command_type_passes_validation(self):
        from backend.ai.validation import validate_parse_result
        result = ParseResult(
            matched=True,
            command_type="strategic",
            marshals=["Ney"],
            action="move",
            target="Vienna",
            is_strategic=True,
            strategic_type="MOVE_TO",
        )
        validated = validate_parse_result(
            result,
            valid_marshals=["Ney", "Davout", "Grouchy"],
            valid_regions=["Paris", "Belgium", "Vienna"],
            valid_targets=["Paris", "Belgium", "Vienna", "Wellington", "Blucher"],
        )
        assert validated.matched is True, "Strategic commands should pass validation"

    def test_condition_passes_validation(self):
        from backend.ai.validation import validate_parse_result
        result = ParseResult(
            matched=True,
            marshals=["Davout"],
            action="hold",
            target="Belgium",
            condition="until Ney arrives",
        )
        validated = validate_parse_result(
            result,
            valid_marshals=["Ney", "Davout", "Grouchy"],
            valid_regions=["Paris", "Belgium"],
            valid_targets=["Paris", "Belgium", "Wellington"],
        )
        assert validated.matched is True, "Conditional commands should pass validation"

    def test_standing_order_passes_validation(self):
        from backend.ai.validation import validate_parse_result
        result = ParseResult(
            matched=True,
            marshals=["Ney"],
            action="move",
            standing_order="pursue",
        )
        validated = validate_parse_result(
            result,
            valid_marshals=["Ney", "Davout", "Grouchy"],
            valid_regions=["Paris"],
            valid_targets=["Paris", "Wellington"],
        )
        assert validated.matched is True, "Standing orders should pass validation"
