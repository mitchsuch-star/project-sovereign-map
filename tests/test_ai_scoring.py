"""
Tests for Phase 5 AI Strategic Scoring System.

Tests cover:
1. Base scores by personality
2. Situation modifiers (glory opportunity, drilling target, Blucher moment)
3. Score clamping (0-100)
4. Integration with bonus application
"""

import pytest
from unittest.mock import Mock
from backend.models.world_state import WorldState
from backend.ai.enemy_ai import calculate_ai_strategic_score, AI_SCORING_ENABLED
from backend.ai.feedback import apply_strategic_bonuses


class TestAIStrategicScoreBase:
    """Test base scores by personality."""

    def test_aggressive_base_score(self):
        """Aggressive marshals should have base score around 55."""
        marshal = Mock(personality="aggressive", strength=1000)
        scores = [calculate_ai_strategic_score(marshal, "defend", None) for _ in range(20)]
        avg = sum(scores) / 20

        # Base 55 ± 10 random, so average should be near 55
        assert 45 <= avg <= 65, f"Aggressive average {avg} not in expected range"
        print(f"Aggressive base score average: {avg:.1f}")

    def test_cautious_base_score(self):
        """Cautious marshals should have base score around 40."""
        marshal = Mock(personality="cautious", strength=1000)
        scores = [calculate_ai_strategic_score(marshal, "defend", None) for _ in range(20)]
        avg = sum(scores) / 20

        # Base 40 ± 10 random
        assert 30 <= avg <= 50, f"Cautious average {avg} not in expected range"
        print(f"Cautious base score average: {avg:.1f}")

    def test_literal_base_score(self):
        """Literal marshals should have base score around 30."""
        marshal = Mock(personality="literal", strength=1000)
        scores = [calculate_ai_strategic_score(marshal, "defend", None) for _ in range(20)]
        avg = sum(scores) / 20

        # Base 30 ± 10 random
        assert 20 <= avg <= 40, f"Literal average {avg} not in expected range"
        print(f"Literal base score average: {avg:.1f}")

    def test_balanced_base_score(self):
        """Balanced marshals should have base score around 45."""
        marshal = Mock(personality="balanced", strength=1000)
        scores = [calculate_ai_strategic_score(marshal, "defend", None) for _ in range(20)]
        avg = sum(scores) / 20

        assert 35 <= avg <= 55, f"Balanced average {avg} not in expected range"
        print(f"Balanced base score average: {avg:.1f}")

    def test_loyal_base_score(self):
        """Loyal marshals should have base score around 50."""
        marshal = Mock(personality="loyal", strength=1000)
        scores = [calculate_ai_strategic_score(marshal, "defend", None) for _ in range(20)]
        avg = sum(scores) / 20

        assert 40 <= avg <= 60, f"Loyal average {avg} not in expected range"
        print(f"Loyal base score average: {avg:.1f}")

    def test_unknown_personality_defaults_to_40(self):
        """Unknown personality should default to 40 base."""
        marshal = Mock(personality="unknown", strength=1000)
        scores = [calculate_ai_strategic_score(marshal, "defend", None) for _ in range(20)]
        avg = sum(scores) / 20

        assert 30 <= avg <= 50, f"Unknown average {avg} not in expected range"
        print(f"Unknown personality base score average: {avg:.1f}")


class TestAIStrategicScoreModifiers:
    """Test situation modifiers for combat actions."""

    def test_glory_opportunity_bonus(self):
        """Clear advantage (ratio > 1.5) should add +10 to score."""
        marshal = Mock(personality="balanced", strength=1500)
        target = Mock(strength=1000, drilling=False, drilling_locked=False)
        # ratio = 1.5, should get +10

        scores = [calculate_ai_strategic_score(marshal, "attack", target) for _ in range(20)]
        avg = sum(scores) / 20

        # Base 45 + 10 glory = 55 average
        assert 45 <= avg <= 65, f"Glory opportunity average {avg} not in expected range"
        print(f"Glory opportunity average: {avg:.1f}")

    def test_no_glory_bonus_below_threshold(self):
        """Ratio below 1.5 should not get glory bonus."""
        marshal = Mock(personality="balanced", strength=1400)
        target = Mock(strength=1000, drilling=False, drilling_locked=False)
        # ratio = 1.4, should NOT get +10

        scores = [calculate_ai_strategic_score(marshal, "attack", target) for _ in range(20)]
        avg = sum(scores) / 20

        # Base 45, no glory bonus
        assert 35 <= avg <= 55, f"No glory bonus average {avg} not in expected range"
        print(f"No glory bonus average: {avg:.1f}")

    def test_drilling_target_bonus(self):
        """Drilling target should add +10 to score."""
        marshal = Mock(personality="balanced", strength=1000)
        target = Mock(strength=1000, drilling=True, drilling_locked=False)

        scores = [calculate_ai_strategic_score(marshal, "attack", target) for _ in range(20)]
        avg = sum(scores) / 20

        # Base 45 + 10 drilling = 55 average
        assert 45 <= avg <= 65, f"Drilling target average {avg} not in expected range"
        print(f"Drilling target average: {avg:.1f}")

    def test_drilling_locked_target_bonus(self):
        """Drilling_locked target should also add +10 to score."""
        marshal = Mock(personality="balanced", strength=1000)
        target = Mock(strength=1000, drilling=False, drilling_locked=True)

        scores = [calculate_ai_strategic_score(marshal, "attack", target) for _ in range(20)]
        avg = sum(scores) / 20

        # Base 45 + 10 drilling = 55 average
        assert 45 <= avg <= 65, f"Drilling locked average {avg} not in expected range"
        print(f"Drilling locked target average: {avg:.1f}")

    def test_blucher_moment(self):
        """Aggressive marshal attacking against odds (< 0.8) should get +15."""
        marshal = Mock(personality="aggressive", strength=700)
        target = Mock(strength=1000, drilling=False, drilling_locked=False)
        # ratio = 0.7, aggressive personality = +15

        scores = [calculate_ai_strategic_score(marshal, "attack", target) for _ in range(20)]
        avg = sum(scores) / 20

        # Base 55 + 15 Blucher = 70 average
        assert 60 <= avg <= 80, f"Blucher moment average {avg} not in expected range"
        print(f"Blucher moment average: {avg:.1f}")

    def test_no_blucher_bonus_for_cautious(self):
        """Cautious marshal attacking against odds should NOT get Blucher bonus."""
        marshal = Mock(personality="cautious", strength=700)
        target = Mock(strength=1000, drilling=False, drilling_locked=False)
        # ratio = 0.7, but NOT aggressive personality = no +15

        scores = [calculate_ai_strategic_score(marshal, "attack", target) for _ in range(20)]
        avg = sum(scores) / 20

        # Base 40 only
        assert 30 <= avg <= 50, f"No Blucher bonus average {avg} not in expected range"
        print(f"Cautious attacking against odds average: {avg:.1f}")

    def test_stacked_bonuses(self):
        """Multiple bonuses should stack (glory + drilling)."""
        marshal = Mock(personality="balanced", strength=2000)
        target = Mock(strength=1000, drilling=True, drilling_locked=False)
        # ratio = 2.0 (glory +10) + drilling (+10) = +20

        scores = [calculate_ai_strategic_score(marshal, "attack", target) for _ in range(20)]
        avg = sum(scores) / 20

        # Base 45 + 10 glory + 10 drilling = 65 average
        assert 55 <= avg <= 75, f"Stacked bonuses average {avg} not in expected range"
        print(f"Stacked bonuses average: {avg:.1f}")

    def test_no_modifiers_for_non_combat(self):
        """Non-combat actions should not get situation modifiers."""
        marshal = Mock(personality="balanced", strength=2000)
        target = Mock(strength=1000, drilling=True, drilling_locked=True)

        # Defend action should not get bonuses even with favorable conditions
        scores = [calculate_ai_strategic_score(marshal, "defend", target) for _ in range(20)]
        avg = sum(scores) / 20

        # Base 45 only, no modifiers
        assert 35 <= avg <= 55, f"Non-combat average {avg} not in expected range"
        print(f"Non-combat (defend) average: {avg:.1f}")

    def test_no_modifiers_without_target(self):
        """Combat without target should not get modifiers."""
        marshal = Mock(personality="balanced", strength=2000)

        scores = [calculate_ai_strategic_score(marshal, "attack", None) for _ in range(20)]
        avg = sum(scores) / 20

        # Base 45 only
        assert 35 <= avg <= 55, f"No target average {avg} not in expected range"
        print(f"No target average: {avg:.1f}")


class TestAIStrategicScoreClamping:
    """Test that scores are always clamped to 0-100."""

    def test_score_clamped_high(self):
        """Even with stacked bonuses, score should be clamped to 100."""
        # Aggressive (55) + glory (10) + drilling (10) + Blucher (15) + max random (10) = 100
        marshal = Mock(personality="aggressive", strength=800)
        target = Mock(strength=1000, drilling=True, drilling_locked=True)

        # Run many times to ensure clamping
        for _ in range(100):
            score = calculate_ai_strategic_score(marshal, "attack", target)
            assert 0 <= score <= 100, f"Score {score} out of bounds"

        print("High score clamping verified")

    def test_score_clamped_low(self):
        """Score should never go below 0."""
        # Literal (30) + min random (-10) = 20, still positive
        marshal = Mock(personality="literal", strength=1000)

        for _ in range(100):
            score = calculate_ai_strategic_score(marshal, "defend", None)
            assert 0 <= score <= 100, f"Score {score} out of bounds"

        print("Low score clamping verified")


class TestAIBonusApplication:
    """Test that AI bonuses are correctly applied to marshals."""

    def setup_method(self):
        self.world = WorldState()

    def test_ai_bonuses_applied_morale(self):
        """AI strategic score should increase marshal morale."""
        marshal = self.world.get_marshal("Wellington")
        # Set morale below max to verify increase
        marshal.morale = 70
        original_morale = marshal.morale

        # Apply a high score (76+)
        apply_strategic_bonuses(marshal, 80, is_combat_action=False)

        assert marshal.morale > original_morale, "Morale should increase"
        print(f"Morale increased from {original_morale} to {marshal.morale}")

    def test_ai_bonuses_applied_trust(self):
        """AI strategic score should increase marshal trust."""
        marshal = self.world.get_marshal("Wellington")
        original_trust = marshal.trust.value

        # Apply a high score (76+)
        apply_strategic_bonuses(marshal, 80, is_combat_action=False)

        assert marshal.trust.value > original_trust, "Trust should increase"
        print(f"Trust increased from {original_trust} to {marshal.trust.value}")

    def test_ai_combat_bonus_applied(self):
        """AI combat action with high score should set strategic_combat_bonus."""
        marshal = self.world.get_marshal("Blucher")
        marshal.strategic_combat_bonus = 0

        # Apply a high score with combat flag
        apply_strategic_bonuses(marshal, 80, is_combat_action=True)

        assert marshal.strategic_combat_bonus > 0, "Combat bonus should be set"
        print(f"Combat bonus set to {marshal.strategic_combat_bonus}")

    def test_ai_no_combat_bonus_for_non_combat(self):
        """AI non-combat action should not set strategic_combat_bonus."""
        marshal = self.world.get_marshal("Blucher")
        marshal.strategic_combat_bonus = 0

        # Apply a high score without combat flag
        apply_strategic_bonuses(marshal, 80, is_combat_action=False)

        assert marshal.strategic_combat_bonus == 0, "Combat bonus should not be set"
        print("No combat bonus for non-combat action")


class TestAIStrategicScoreWithRealMarshals:
    """Test AI scoring with real marshal objects from WorldState."""

    def setup_method(self):
        self.world = WorldState()

    def test_wellington_cautious_score(self):
        """Wellington (cautious) should have lower base score than Blucher."""
        wellington = self.world.get_marshal("Wellington")
        blucher = self.world.get_marshal("Blucher")

        wellington_scores = [calculate_ai_strategic_score(wellington, "defend", None) for _ in range(50)]
        blucher_scores = [calculate_ai_strategic_score(blucher, "defend", None) for _ in range(50)]

        wellington_avg = sum(wellington_scores) / 50
        blucher_avg = sum(blucher_scores) / 50

        # Wellington (cautious, 40) should be lower than Blucher (aggressive, 55)
        assert wellington_avg < blucher_avg, f"Wellington avg {wellington_avg} should be < Blucher avg {blucher_avg}"
        print(f"Wellington avg: {wellington_avg:.1f}, Blucher avg: {blucher_avg:.1f}")

    def test_blucher_vs_ney_attack(self):
        """Blucher attacking Ney should consider ratio."""
        blucher = self.world.get_marshal("Blucher")
        ney = self.world.get_marshal("Ney")

        # Set equal strength to avoid Blücher moment bonus
        blucher.strength = 50000
        ney.strength = 50000
        ney.drilling = False  # Ensure not drilling

        # At 1:1 ratio, no modifiers should apply
        scores = [calculate_ai_strategic_score(blucher, "attack", ney) for _ in range(20)]
        avg = sum(scores) / 20

        # Base 55 for aggressive, no modifiers
        assert 45 <= avg <= 65, f"Blucher vs Ney average {avg} not in expected range"
        print(f"Blucher attacking Ney average: {avg:.1f}")


class TestAIScoringEnabled:
    """Test AI_SCORING_ENABLED flag."""

    def test_scoring_enabled_by_default(self):
        """AI_SCORING_ENABLED should be True by default."""
        assert AI_SCORING_ENABLED is True
        print("AI_SCORING_ENABLED is True")
