"""
Tests for Grouchy ambiguity combat buff system (Phase 5.2).

Covers:
- Ambiguity-scaled combat buffs (+15%, +10%, +5%, 0%)
- Precision Execution trigger and skill boost
- Precision Execution decay over turns
- get_effective_skill() helper

Run with: pytest tests/test_grouchy_ambiguity.py -v
"""

import pytest
from backend.models.world_state import WorldState
from backend.models.marshal import Marshal
from backend.commands.executor import CommandExecutor


class TestAmbiguityCombatBuff:
    """Test _apply_grouchy_ambiguity_buff() sets correct bonuses."""

    def setup_method(self):
        self.executor = CommandExecutor()
        self.grouchy = Marshal("Grouchy", "Paris", 30000, "literal", nation="France")

    def test_crystal_clear_gives_15_percent(self):
        """Ambiguity 0-20 → +15% attack and defense bonus."""
        self.executor._apply_grouchy_ambiguity_buff(self.grouchy, ambiguity=10, strategic_score=50, action="attack")
        assert self.grouchy.strategic_combat_bonus == 15
        assert self.grouchy.strategic_defense_bonus == 15

    def test_clear_gives_10_percent(self):
        """Ambiguity 21-40 → +10% bonus."""
        self.executor._apply_grouchy_ambiguity_buff(self.grouchy, ambiguity=30, strategic_score=50, action="attack")
        assert self.grouchy.strategic_combat_bonus == 10
        assert self.grouchy.strategic_defense_bonus == 10

    def test_vague_gives_5_percent(self):
        """Ambiguity 41-60 → +5% bonus."""
        self.executor._apply_grouchy_ambiguity_buff(self.grouchy, ambiguity=55, strategic_score=50, action="attack")
        assert self.grouchy.strategic_combat_bonus == 5
        assert self.grouchy.strategic_defense_bonus == 5

    def test_very_vague_gives_no_bonus(self):
        """Ambiguity 61+ → 0% bonus."""
        self.executor._apply_grouchy_ambiguity_buff(self.grouchy, ambiguity=75, strategic_score=50, action="attack")
        assert self.grouchy.strategic_combat_bonus == 0
        assert self.grouchy.strategic_defense_bonus == 0

    def test_non_combat_action_no_bonus(self):
        """Non-combat actions don't set combat bonus even with low ambiguity."""
        self.executor._apply_grouchy_ambiguity_buff(self.grouchy, ambiguity=10, strategic_score=50, action="move")
        assert self.grouchy.strategic_combat_bonus == 0
        assert self.grouchy.strategic_defense_bonus == 0


class TestPrecisionExecution:
    """Test Precision Execution trigger and decay."""

    def setup_method(self):
        self.executor = CommandExecutor()
        self.grouchy = Marshal("Grouchy", "Paris", 30000, "literal", nation="France")

    def test_precision_triggers_on_low_ambiguity_high_strategic(self):
        """ambiguity<=20 AND strategic_score>60 → precision active for 3 turns."""
        self.executor._apply_grouchy_ambiguity_buff(self.grouchy, ambiguity=15, strategic_score=70, action="attack")
        assert self.grouchy.precision_execution_active is True
        assert self.grouchy.precision_execution_turns == 3

    def test_precision_does_not_trigger_low_strategic(self):
        """Low ambiguity but low strategic_score → no precision."""
        self.executor._apply_grouchy_ambiguity_buff(self.grouchy, ambiguity=15, strategic_score=40, action="attack")
        assert self.grouchy.precision_execution_active is False

    def test_precision_does_not_trigger_high_ambiguity(self):
        """High ambiguity even with high strategic → no precision."""
        self.executor._apply_grouchy_ambiguity_buff(self.grouchy, ambiguity=50, strategic_score=80, action="attack")
        assert self.grouchy.precision_execution_active is False


class TestGetEffectiveSkill:
    """Test get_effective_skill() with and without precision execution."""

    def setup_method(self):
        self.grouchy = Marshal("Grouchy", "Paris", 30000, "literal", nation="France")

    def test_base_skill_without_precision(self):
        """Without precision, returns base skill value."""
        base = self.grouchy.skills.get("tactical", 5)
        assert self.grouchy.get_effective_skill("tactical") == base

    def test_skill_boosted_with_precision(self):
        """With precision active, skill is +1."""
        base = self.grouchy.skills.get("tactical", 5)
        self.grouchy.precision_execution_active = True
        self.grouchy.precision_execution_turns = 3
        assert self.grouchy.get_effective_skill("tactical") == min(8, base + 1)

    def test_skill_capped_at_8(self):
        """Skill cannot exceed 8 even with precision."""
        self.grouchy.skills["tactical"] = 8
        self.grouchy.precision_execution_active = True
        self.grouchy.precision_execution_turns = 3
        assert self.grouchy.get_effective_skill("tactical") == 8


class TestPrecisionDecay:
    """Test precision execution countdown in world_state turn processing."""

    def setup_method(self):
        self.world = WorldState()

    def test_precision_decrements_each_turn(self):
        """Precision turns count down during _process_tactical_states."""
        grouchy = self.world.marshals.get("Grouchy")
        if grouchy is None:
            pytest.skip("Grouchy not in default world state")
        grouchy.precision_execution_active = True
        grouchy.precision_execution_turns = 3

        self.world._process_tactical_states()
        assert grouchy.precision_execution_turns == 2
        assert grouchy.precision_execution_active is True

    def test_precision_expires_at_zero(self):
        """Precision deactivates when turns reach 0."""
        grouchy = self.world.marshals.get("Grouchy")
        if grouchy is None:
            pytest.skip("Grouchy not in default world state")
        grouchy.precision_execution_active = True
        grouchy.precision_execution_turns = 1

        self.world._process_tactical_states()
        assert grouchy.precision_execution_turns == 0
        assert grouchy.precision_execution_active is False
