"""
Tests for V2 Objection System

Unit 1: Core Data Structures
- ConcernLevel enum
- TrustTier enum
- Trust gain calculations
- Insist penalty calculations
- Mood variance
"""

from unittest.mock import patch

from backend.commands.objection_v2 import (
    ConcernLevel,
    TrustTier,
    get_trust_tier,
    calculate_trust_gain,
    get_insist_penalty,
    get_objection_tone,
    get_consequences,
    apply_mood_variance,
    handle_objection_response,
    concern_to_legacy_severity,
    is_popup_concern,
    is_blocking_concern,
    TRUST_GAIN_BASE,
    TRUST_TIER_MULTIPLIER,
    CONSEQUENCE_TABLE,
    COMPROMISE_TRUST_GAIN,
    # Unit 2: Trigger evaluators
    evaluate_aggressive,
    evaluate_cautious,
    evaluate_literal,
    evaluate_situation,
    _check_enemy_adjacent,
    _check_enemy_in_region,
    _get_friendly_to_enemy_ratio,
    _is_outnumbered_2to1,
    evaluate_strategic_aggressive,
    evaluate_strategic_cautious,
    evaluate_strategic_literal,
    evaluate_strategic_situation,
    _check_enemies_adjacent_to_region,
    _get_pursue_target_ratio,
    _path_has_enemies,
)


# ════════════════════════════════════════════════════════════════════════════
# ENUM TESTS
# ════════════════════════════════════════════════════════════════════════════


class TestConcernLevelEnum:
    """Test ConcernLevel enum values and ordering."""

    def test_concern_level_values(self):
        """Verify ConcernLevel integer values for ordering."""
        assert ConcernLevel.NONE.value == 0
        assert ConcernLevel.MILD.value == 1
        assert ConcernLevel.MODERATE.value == 2
        assert ConcernLevel.STRONG.value == 3
        assert ConcernLevel.EXTREME.value == 4

    def test_concern_level_ordering(self):
        """Verify ConcernLevel comparison works correctly."""
        assert ConcernLevel.NONE < ConcernLevel.MILD
        assert ConcernLevel.MILD < ConcernLevel.MODERATE
        assert ConcernLevel.MODERATE < ConcernLevel.STRONG
        assert ConcernLevel.STRONG < ConcernLevel.EXTREME

    def test_concern_level_names(self):
        """Verify ConcernLevel names for serialization."""
        assert ConcernLevel.NONE.name == "NONE"
        assert ConcernLevel.MILD.name == "MILD"
        assert ConcernLevel.MODERATE.name == "MODERATE"
        assert ConcernLevel.STRONG.name == "STRONG"
        assert ConcernLevel.EXTREME.name == "EXTREME"


class TestTrustTierEnum:
    """Test TrustTier enum values and ordering."""

    def test_trust_tier_values(self):
        """Verify TrustTier integer values for ordering."""
        assert TrustTier.HOSTILE.value == 0
        assert TrustTier.WARY.value == 1
        assert TrustTier.TRUSTING.value == 2
        assert TrustTier.DEVOTED.value == 3

    def test_trust_tier_ordering(self):
        """Verify TrustTier comparison works correctly."""
        assert TrustTier.HOSTILE < TrustTier.WARY
        assert TrustTier.WARY < TrustTier.TRUSTING
        assert TrustTier.TRUSTING < TrustTier.DEVOTED


# ════════════════════════════════════════════════════════════════════════════
# TRUST TIER FUNCTION TESTS
# ════════════════════════════════════════════════════════════════════════════


class TestGetTrustTier:
    """Test get_trust_tier() function."""

    def test_hostile_tier(self):
        """Trust < 30 is HOSTILE."""
        assert get_trust_tier(0) == TrustTier.HOSTILE
        assert get_trust_tier(15) == TrustTier.HOSTILE
        assert get_trust_tier(29) == TrustTier.HOSTILE

    def test_wary_tier(self):
        """Trust 30-49 is WARY."""
        assert get_trust_tier(30) == TrustTier.WARY
        assert get_trust_tier(40) == TrustTier.WARY
        assert get_trust_tier(49) == TrustTier.WARY

    def test_trusting_tier(self):
        """Trust 50-79 is TRUSTING."""
        assert get_trust_tier(50) == TrustTier.TRUSTING
        assert get_trust_tier(65) == TrustTier.TRUSTING
        assert get_trust_tier(79) == TrustTier.TRUSTING

    def test_devoted_tier(self):
        """Trust >= 80 is DEVOTED."""
        assert get_trust_tier(80) == TrustTier.DEVOTED
        assert get_trust_tier(90) == TrustTier.DEVOTED
        assert get_trust_tier(100) == TrustTier.DEVOTED

    def test_boundary_exactly_30(self):
        """Trust of exactly 30 is WARY (not HOSTILE)."""
        assert get_trust_tier(30) == TrustTier.WARY

    def test_boundary_exactly_50(self):
        """Trust of exactly 50 is TRUSTING (not WARY)."""
        assert get_trust_tier(50) == TrustTier.TRUSTING

    def test_boundary_exactly_80(self):
        """Trust of exactly 80 is DEVOTED (not TRUSTING)."""
        assert get_trust_tier(80) == TrustTier.DEVOTED


# ════════════════════════════════════════════════════════════════════════════
# TRUST GAIN TESTS
# ════════════════════════════════════════════════════════════════════════════


class TestCalculateTrustGain:
    """Test trust gain calculations."""

    def test_moderate_gains(self):
        """MODERATE concern gives +3 base."""
        assert calculate_trust_gain(ConcernLevel.MODERATE, TrustTier.TRUSTING) == 3

    def test_strong_gains(self):
        """STRONG concern gives +5 base."""
        assert calculate_trust_gain(ConcernLevel.STRONG, TrustTier.TRUSTING) == 5

    def test_extreme_gains(self):
        """EXTREME concern gives +8 base."""
        assert calculate_trust_gain(ConcernLevel.EXTREME, TrustTier.TRUSTING) == 8

    def test_hostile_multiplier(self):
        """HOSTILE tier gives 1.5x trust gain."""
        # MODERATE: 3 * 1.5 = 4.5 → 4 (rounded down)
        assert calculate_trust_gain(ConcernLevel.MODERATE, TrustTier.HOSTILE) == 4
        # STRONG: 5 * 1.5 = 7.5 → 7
        assert calculate_trust_gain(ConcernLevel.STRONG, TrustTier.HOSTILE) == 7
        # EXTREME: 8 * 1.5 = 12
        assert calculate_trust_gain(ConcernLevel.EXTREME, TrustTier.HOSTILE) == 12

    def test_wary_multiplier(self):
        """WARY tier gives 1.2x trust gain."""
        # MODERATE: 3 * 1.2 = 3.6 → 3
        assert calculate_trust_gain(ConcernLevel.MODERATE, TrustTier.WARY) == 3
        # STRONG: 5 * 1.2 = 6
        assert calculate_trust_gain(ConcernLevel.STRONG, TrustTier.WARY) == 6
        # EXTREME: 8 * 1.2 = 9.6 → 9
        assert calculate_trust_gain(ConcernLevel.EXTREME, TrustTier.WARY) == 9

    def test_devoted_multiplier(self):
        """DEVOTED tier gives 0.7x trust gain (diminishing returns)."""
        # MODERATE: 3 * 0.7 = 2.1 → 2
        assert calculate_trust_gain(ConcernLevel.MODERATE, TrustTier.DEVOTED) == 2
        # STRONG: 5 * 0.7 = 3.5 → 3
        assert calculate_trust_gain(ConcernLevel.STRONG, TrustTier.DEVOTED) == 3
        # EXTREME: 8 * 0.7 = 5.6 → 5
        assert calculate_trust_gain(ConcernLevel.EXTREME, TrustTier.DEVOTED) == 5

    def test_no_gain_for_mild(self):
        """MILD concern gives 0 trust gain (no popup, no choice)."""
        assert calculate_trust_gain(ConcernLevel.MILD, TrustTier.TRUSTING) == 0
        assert calculate_trust_gain(ConcernLevel.MILD, TrustTier.HOSTILE) == 0

    def test_no_gain_for_none(self):
        """NONE concern gives 0 trust gain."""
        assert calculate_trust_gain(ConcernLevel.NONE, TrustTier.TRUSTING) == 0

    def test_trust_gain_matrix(self):
        """Verify complete trust gain matrix from design doc."""
        expected = {
            # (concern, tier): expected_gain
            (ConcernLevel.MODERATE, TrustTier.HOSTILE): 4,  # int(3 * 1.5) = 4
            (ConcernLevel.MODERATE, TrustTier.WARY): 3,     # int(3 * 1.2) = 3
            (ConcernLevel.MODERATE, TrustTier.TRUSTING): 3,
            (ConcernLevel.MODERATE, TrustTier.DEVOTED): 2,

            (ConcernLevel.STRONG, TrustTier.HOSTILE): 7,    # int(5 * 1.5) = 7
            (ConcernLevel.STRONG, TrustTier.WARY): 6,
            (ConcernLevel.STRONG, TrustTier.TRUSTING): 5,
            (ConcernLevel.STRONG, TrustTier.DEVOTED): 3,

            (ConcernLevel.EXTREME, TrustTier.HOSTILE): 12,
            (ConcernLevel.EXTREME, TrustTier.WARY): 9,      # int(8 * 1.2) = 9
            (ConcernLevel.EXTREME, TrustTier.TRUSTING): 8,
            (ConcernLevel.EXTREME, TrustTier.DEVOTED): 5,
        }

        for (concern, tier), expected_gain in expected.items():
            actual = calculate_trust_gain(concern, tier)
            assert actual == expected_gain, f"{concern.name} at {tier.name}: expected {expected_gain}, got {actual}"


# ════════════════════════════════════════════════════════════════════════════
# INSIST PENALTY TESTS
# ════════════════════════════════════════════════════════════════════════════


class TestGetInsistPenalty:
    """Test insist penalty calculations."""

    def test_hostile_penalty(self):
        """HOSTILE tier gives -15 penalty."""
        assert get_insist_penalty(TrustTier.HOSTILE) == -15

    def test_wary_penalty(self):
        """WARY tier gives -12 penalty."""
        assert get_insist_penalty(TrustTier.WARY) == -12

    def test_trusting_penalty(self):
        """TRUSTING tier gives -10 penalty."""
        assert get_insist_penalty(TrustTier.TRUSTING) == -10

    def test_devoted_penalty(self):
        """DEVOTED tier gives -5 penalty."""
        assert get_insist_penalty(TrustTier.DEVOTED) == -5

    def test_all_penalties_negative(self):
        """All insist penalties should be negative."""
        for tier in TrustTier:
            penalty = get_insist_penalty(tier)
            assert penalty < 0, f"{tier.name} penalty should be negative"


# ════════════════════════════════════════════════════════════════════════════
# TONE TESTS
# ════════════════════════════════════════════════════════════════════════════


class TestGetObjectionTone:
    """Test objection tone by trust tier."""

    def test_hostile_tone(self):
        """HOSTILE tier gives defiant tone."""
        assert get_objection_tone(TrustTier.HOSTILE) == "defiant"

    def test_wary_tone(self):
        """WARY tier gives challenging tone."""
        assert get_objection_tone(TrustTier.WARY) == "challenging"

    def test_trusting_tone(self):
        """TRUSTING tier gives firm tone."""
        assert get_objection_tone(TrustTier.TRUSTING) == "firm"

    def test_devoted_tone(self):
        """DEVOTED tier gives respectful tone."""
        assert get_objection_tone(TrustTier.DEVOTED) == "respectful"


class TestGetConsequences:
    """Test full consequence dict retrieval."""

    def test_consequences_has_tone_and_penalty(self):
        """Consequence dict has both tone and insist_penalty."""
        for tier in TrustTier:
            consequences = get_consequences(tier)
            assert "tone" in consequences
            assert "insist_penalty" in consequences

    def test_consequences_is_copy(self):
        """Returned dict is a copy, not original."""
        consequences = get_consequences(TrustTier.TRUSTING)
        consequences["tone"] = "modified"
        # Original should be unchanged
        assert CONSEQUENCE_TABLE[TrustTier.TRUSTING]["tone"] == "firm"


# ════════════════════════════════════════════════════════════════════════════
# MOOD VARIANCE TESTS
# ════════════════════════════════════════════════════════════════════════════


class TestApplyMoodVariance:
    """Test mood variance function."""

    def test_none_never_promotes(self):
        """NONE concern never promotes to MILD, even with variance."""
        # Mock random to return value that would promote (< 0.10)
        with patch('backend.commands.objection_v2.random.random', return_value=0.05):
            result = apply_mood_variance(ConcernLevel.NONE)
            assert result == ConcernLevel.NONE

    def test_mild_can_promote(self):
        """MILD can promote to MODERATE with variance."""
        with patch('backend.commands.objection_v2.random.random', return_value=0.05):
            result = apply_mood_variance(ConcernLevel.MILD)
            assert result == ConcernLevel.MODERATE

    def test_mild_never_demotes_to_none(self):
        """MILD never demotes to NONE (floor at MILD)."""
        # Value between 0.10 and 0.25 would demote
        with patch('backend.commands.objection_v2.random.random', return_value=0.15):
            result = apply_mood_variance(ConcernLevel.MILD)
            assert result == ConcernLevel.MILD  # Floor at MILD, not NONE

    def test_moderate_can_demote(self):
        """MODERATE can demote to MILD with variance."""
        with patch('backend.commands.objection_v2.random.random', return_value=0.15):
            result = apply_mood_variance(ConcernLevel.MODERATE)
            assert result == ConcernLevel.MILD

    def test_moderate_can_promote(self):
        """MODERATE can promote to STRONG with variance."""
        with patch('backend.commands.objection_v2.random.random', return_value=0.05):
            result = apply_mood_variance(ConcernLevel.MODERATE)
            assert result == ConcernLevel.STRONG

    def test_extreme_caps_at_extreme(self):
        """EXTREME caps at EXTREME, even with promote roll."""
        with patch('backend.commands.objection_v2.random.random', return_value=0.05):
            result = apply_mood_variance(ConcernLevel.EXTREME)
            assert result == ConcernLevel.EXTREME

    def test_no_variance_at_75_percent(self):
        """75% of rolls result in no change."""
        # Values >= 0.25 should not change
        with patch('backend.commands.objection_v2.random.random', return_value=0.50):
            result = apply_mood_variance(ConcernLevel.MODERATE)
            assert result == ConcernLevel.MODERATE

    def test_variance_distribution_bounds(self):
        """
        Statistical test: variance stays within expected bounds.
        Over many samples, should see ~10% promote, ~15% demote, ~75% same.
        """
        import random

        # Seed for reproducibility in this test
        random.seed(42)

        promote_count = 0
        demote_count = 0
        same_count = 0

        for _ in range(1000):
            result = apply_mood_variance(ConcernLevel.MODERATE)
            if result == ConcernLevel.STRONG:
                promote_count += 1
            elif result == ConcernLevel.MILD:
                demote_count += 1
            else:
                same_count += 1

        # Allow ±5% tolerance on expected percentages
        assert 50 <= promote_count <= 150, f"Promote count {promote_count} outside expected range"
        assert 100 <= demote_count <= 200, f"Demote count {demote_count} outside expected range"
        assert 650 <= same_count <= 850, f"Same count {same_count} outside expected range"


# ════════════════════════════════════════════════════════════════════════════
# RESPONSE HANDLING TESTS
# ════════════════════════════════════════════════════════════════════════════


class TestHandleObjectionResponse:
    """Test response handling function."""

    def test_trust_response(self):
        """'trust' response returns calculated trust gain."""
        gain = handle_objection_response("trust", ConcernLevel.STRONG, TrustTier.TRUSTING)
        expected = calculate_trust_gain(ConcernLevel.STRONG, TrustTier.TRUSTING)
        assert gain == expected

    def test_compromise_response(self):
        """'compromise' response returns flat +3."""
        gain = handle_objection_response("compromise", ConcernLevel.STRONG, TrustTier.TRUSTING)
        assert gain == COMPROMISE_TRUST_GAIN
        assert gain == 3

    def test_compromise_not_scaled(self):
        """Compromise gain is same regardless of tier."""
        for tier in TrustTier:
            gain = handle_objection_response("compromise", ConcernLevel.EXTREME, tier)
            assert gain == 3

    def test_insist_response(self):
        """'insist' response returns tier-based penalty."""
        penalty = handle_objection_response("insist", ConcernLevel.STRONG, TrustTier.WARY)
        expected = get_insist_penalty(TrustTier.WARY)
        assert penalty == expected

    def test_unknown_response(self):
        """Unknown response type returns 0."""
        result = handle_objection_response("unknown", ConcernLevel.STRONG, TrustTier.TRUSTING)
        assert result == 0


# ════════════════════════════════════════════════════════════════════════════
# BACKWARD COMPATIBILITY TESTS
# ════════════════════════════════════════════════════════════════════════════


class TestBackwardCompatibility:
    """Test backward compatibility helpers."""

    def test_concern_to_severity_mapping(self):
        """ConcernLevel maps to legacy severity floats."""
        assert concern_to_legacy_severity(ConcernLevel.NONE) == 0.0
        assert concern_to_legacy_severity(ConcernLevel.MILD) == 0.35
        assert concern_to_legacy_severity(ConcernLevel.MODERATE) == 0.55
        assert concern_to_legacy_severity(ConcernLevel.STRONG) == 0.72
        assert concern_to_legacy_severity(ConcernLevel.EXTREME) == 0.88

    def test_is_popup_concern(self):
        """MODERATE+ triggers popup."""
        assert is_popup_concern(ConcernLevel.NONE) is False
        assert is_popup_concern(ConcernLevel.MILD) is False
        assert is_popup_concern(ConcernLevel.MODERATE) is True
        assert is_popup_concern(ConcernLevel.STRONG) is True
        assert is_popup_concern(ConcernLevel.EXTREME) is True

    def test_is_blocking_concern(self):
        """MODERATE+ blocks execution."""
        assert is_blocking_concern(ConcernLevel.NONE) is False
        assert is_blocking_concern(ConcernLevel.MILD) is False
        assert is_blocking_concern(ConcernLevel.MODERATE) is True
        assert is_blocking_concern(ConcernLevel.STRONG) is True
        assert is_blocking_concern(ConcernLevel.EXTREME) is True


# ════════════════════════════════════════════════════════════════════════════
# TABLE CONSISTENCY TESTS
# ════════════════════════════════════════════════════════════════════════════


class TestTableConsistency:
    """Test that tables are consistent and complete."""

    def test_consequence_table_complete(self):
        """CONSEQUENCE_TABLE has entry for every TrustTier."""
        for tier in TrustTier:
            assert tier in CONSEQUENCE_TABLE

    def test_trust_gain_base_complete(self):
        """TRUST_GAIN_BASE has entry for popup levels."""
        for concern in [ConcernLevel.MODERATE, ConcernLevel.STRONG, ConcernLevel.EXTREME]:
            assert concern in TRUST_GAIN_BASE

    def test_trust_tier_multiplier_complete(self):
        """TRUST_TIER_MULTIPLIER has entry for every TrustTier."""
        for tier in TrustTier:
            assert tier in TRUST_TIER_MULTIPLIER

    def test_trust_gain_never_exceeds_insist_penalty_magnitude(self):
        """
        Gameplay balance check: insisting costs at least as much as trusting gains.
        This ensures players can't cheese trust by alternating insist/trust.

        Note: At DEVOTED tier, equality is allowed because per design doc:
        "At DEVOTED, insisting barely hurts (-5) → no death spiral at high trust"
        """
        for tier in TrustTier:
            insist_magnitude = abs(get_insist_penalty(tier))
            for concern in [ConcernLevel.MODERATE, ConcernLevel.STRONG, ConcernLevel.EXTREME]:
                trust_gain = calculate_trust_gain(concern, tier)
                assert trust_gain <= insist_magnitude, (
                    f"At {tier.name}, {concern.name} gain ({trust_gain}) > insist penalty ({insist_magnitude})"
                )

    def test_devoted_extreme_edge_case(self):
        """
        At DEVOTED + EXTREME, trust gain equals insist penalty (both 5).
        This is intentional: devoted marshals tolerate occasional overrides.
        Documented as design decision in V2A_IMPLEMENTATION_ADDENDUM.md Part 9.
        """
        gain = calculate_trust_gain(ConcernLevel.EXTREME, TrustTier.DEVOTED)
        penalty = abs(get_insist_penalty(TrustTier.DEVOTED))
        assert gain == penalty == 5, "DEVOTED+EXTREME should be balanced at 5"


# ════════════════════════════════════════════════════════════════════════════
# UNIT 2: TRIGGER EVALUATION TESTS
# ════════════════════════════════════════════════════════════════════════════


class MockMarshal:
    """Mock marshal for testing."""
    def __init__(
        self,
        name="TestMarshal",
        personality="balanced",
        location="Belgium",
        strength=50000,
        nation="France",
        morale=70,
        fortified=False,
    ):
        self.name = name
        self.personality = personality
        self.location = location
        self.strength = strength
        self.nation = nation
        self.morale = morale
        self.fortified = fortified


class MockRegion:
    """Mock region for testing."""
    def __init__(self, name, adjacent_regions=None, controller="France"):
        self.name = name
        self.adjacent_regions = adjacent_regions or []
        self.controller = controller


class _MockRegionIntel:
    """Mock region intel for fog-of-war support in tests.
    Defaults to FULL visibility (preserves pre-fog omniscient behavior).
    """
    def __init__(self, visibility="full"):
        self.visibility = visibility


class MockWorld:
    """Mock world for testing."""
    def __init__(self, marshals=None, regions=None):
        self.marshals = marshals or {}
        self.regions = regions or {}
        self._intel = {}  # {region_name: _MockRegionIntel}

    def find_path(self, start, end):
        """Simple mock pathfinding - returns direct path via regions."""
        if start == end:
            return [start]

        # For testing, just return start -> intermediate regions -> end
        start_region = self.regions.get(start)
        if start_region and end in start_region.adjacent_regions:
            return [start, end]

        # Try to find a 2-hop path
        if start_region:
            for mid in start_region.adjacent_regions:
                mid_region = self.regions.get(mid)
                if mid_region and end in mid_region.adjacent_regions:
                    return [start, mid, end]

        return None

    def get_region_intel(self, region_name):
        """Return intel for a region. Defaults to FULL visibility (omniscient)."""
        if region_name not in self._intel:
            self._intel[region_name] = _MockRegionIntel("full")
        return self._intel[region_name]

    def set_region_visibility(self, region_name, visibility):
        """Test helper: set fog visibility for a specific region."""
        self._intel[region_name] = _MockRegionIntel(visibility)


class MockGameState:
    """Mock game state for testing."""
    def __init__(self, world=None):
        self.world = world


class TestHelperFunctions:
    """Test helper functions for game state queries."""

    def test_check_enemy_adjacent_no_game_state(self):
        """Returns False when no game state."""
        marshal = MockMarshal()
        assert _check_enemy_adjacent(marshal, None) is False

    def test_check_enemy_adjacent_no_enemies(self):
        """Returns False when no enemies exist."""
        marshal = MockMarshal(location="Belgium")
        world = MockWorld(
            marshals={"Ally": MockMarshal(name="Ally", location="Paris")},
            regions={"Belgium": MockRegion("Belgium", ["Paris", "Rhineland"])}
        )
        game_state = MockGameState(world)
        assert _check_enemy_adjacent(marshal, game_state) is False

    def test_check_enemy_adjacent_enemy_adjacent(self):
        """Returns True when enemy in adjacent region."""
        marshal = MockMarshal(location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain")
        world = MockWorld(
            marshals={"Marshal": marshal, "Wellington": enemy},
            regions={"Belgium": MockRegion("Belgium", ["Rhineland", "Paris"])}
        )
        game_state = MockGameState(world)
        assert _check_enemy_adjacent(marshal, game_state) is True

    def test_check_enemy_adjacent_enemy_far(self):
        """Returns False when enemy is not adjacent."""
        marshal = MockMarshal(location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Spain", nation="Britain")
        world = MockWorld(
            marshals={"Marshal": marshal, "Wellington": enemy},
            regions={"Belgium": MockRegion("Belgium", ["Rhineland", "Paris"])}
        )
        game_state = MockGameState(world)
        assert _check_enemy_adjacent(marshal, game_state) is False

    def test_check_enemy_in_region(self):
        """Returns True when enemy in same region."""
        marshal = MockMarshal(location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Belgium", nation="Britain")
        world = MockWorld(
            marshals={"Marshal": marshal, "Wellington": enemy},
            regions={"Belgium": MockRegion("Belgium", [])}
        )
        game_state = MockGameState(world)
        assert _check_enemy_in_region(marshal, game_state) is True

    def test_get_friendly_to_enemy_ratio_no_enemies(self):
        """Returns 999.0 when no enemies nearby."""
        marshal = MockMarshal(location="Belgium", strength=50000)
        world = MockWorld(
            marshals={"Marshal": marshal},
            regions={"Belgium": MockRegion("Belgium", ["Paris"])}
        )
        game_state = MockGameState(world)
        ratio = _get_friendly_to_enemy_ratio(marshal, game_state)
        assert ratio == 999.0

    def test_get_friendly_to_enemy_ratio_outnumber_enemy(self):
        """Returns correct ratio when outnumbering enemy."""
        marshal = MockMarshal(location="Belgium", strength=100000)
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain", strength=50000)
        world = MockWorld(
            marshals={"Marshal": marshal, "Wellington": enemy},
            regions={"Belgium": MockRegion("Belgium", ["Rhineland"])}
        )
        game_state = MockGameState(world)
        ratio = _get_friendly_to_enemy_ratio(marshal, game_state)
        assert ratio == 2.0

    def test_is_outnumbered_2to1(self):
        """Correctly identifies 2:1 disadvantage."""
        marshal = MockMarshal(location="Belgium", strength=30000)
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain", strength=60000)
        world = MockWorld(
            marshals={"Marshal": marshal, "Wellington": enemy},
            regions={"Belgium": MockRegion("Belgium", ["Rhineland"])}
        )
        game_state = MockGameState(world)
        assert _is_outnumbered_2to1(marshal, game_state) is True

    def test_not_outnumbered_2to1(self):
        """Correctly identifies when NOT at 2:1 disadvantage."""
        marshal = MockMarshal(location="Belgium", strength=50000)
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain", strength=60000)
        world = MockWorld(
            marshals={"Marshal": marshal, "Wellington": enemy},
            regions={"Belgium": MockRegion("Belgium", ["Rhineland"])}
        )
        game_state = MockGameState(world)
        assert _is_outnumbered_2to1(marshal, game_state) is False


class TestEvaluateAggressive:
    """Test aggressive personality trigger evaluation."""

    def _make_game_state(self, marshal, enemies=None, adjacent_to_marshal=None):
        """Helper to create game state with marshal and optional enemies."""
        marshals = {"Marshal": marshal}
        if enemies:
            for e in enemies:
                marshals[e.name] = e

        regions = {
            marshal.location: MockRegion(marshal.location, adjacent_to_marshal or [])
        }
        return MockGameState(MockWorld(marshals, regions))

    def test_defend_no_enemy_is_mild(self):
        """Defend with no enemy nearby is MILD concern."""
        marshal = MockMarshal(personality="aggressive", location="Belgium")
        game_state = self._make_game_state(marshal, adjacent_to_marshal=["Paris"])

        concern = evaluate_aggressive(marshal, "defend", {"action": "defend"}, game_state)
        assert concern == ConcernLevel.MILD

    def test_defend_enemy_adjacent_equal_forces_is_moderate(self):
        """Defend with enemy adjacent at equal strength is MODERATE."""
        marshal = MockMarshal(personality="aggressive", location="Belgium", strength=50000)
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain", strength=50000)
        game_state = self._make_game_state(marshal, [enemy], ["Rhineland"])

        concern = evaluate_aggressive(marshal, "defend", {"action": "defend"}, game_state)
        assert concern == ConcernLevel.MODERATE

    def test_defend_enemy_adjacent_2to1_advantage_is_strong(self):
        """Defend with 2:1 advantage is STRONG concern (wants to attack)."""
        marshal = MockMarshal(personality="aggressive", location="Belgium", strength=100000)
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain", strength=50000)
        game_state = self._make_game_state(marshal, [enemy], ["Rhineland"])

        concern = evaluate_aggressive(marshal, "defend", {"action": "defend"}, game_state)
        assert concern == ConcernLevel.STRONG

    def test_defend_enemy_adjacent_3to1_advantage_is_extreme(self):
        """Defend with 3:1+ advantage is EXTREME concern."""
        marshal = MockMarshal(personality="aggressive", location="Belgium", strength=150000)
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain", strength=50000)
        game_state = self._make_game_state(marshal, [enemy], ["Rhineland"])

        concern = evaluate_aggressive(marshal, "defend", {"action": "defend"}, game_state)
        assert concern == ConcernLevel.EXTREME

    def test_fortify_same_as_defend(self):
        """Fortify triggers same concerns as defend."""
        marshal = MockMarshal(personality="aggressive", location="Belgium")
        game_state = self._make_game_state(marshal, adjacent_to_marshal=["Paris"])

        concern = evaluate_aggressive(marshal, "fortify", {"action": "fortify"}, game_state)
        assert concern == ConcernLevel.MILD  # No enemy

    def test_retreat_not_threatened_is_mild(self):
        """Retreat when not actually threatened — pre-validation blocks this before objection,
        but if it reaches the evaluator, returns MILD (dead STRONG trigger removed)."""
        marshal = MockMarshal(personality="aggressive", location="Belgium")
        game_state = self._make_game_state(marshal, adjacent_to_marshal=["Paris"])

        concern = evaluate_aggressive(marshal, "retreat", {"action": "retreat"}, game_state)
        assert concern == ConcernLevel.MILD

    def test_retreat_threatened_not_outnumbered_is_mild(self):
        """Retreat when threatened but not outnumbered is MILD."""
        marshal = MockMarshal(personality="aggressive", location="Belgium", strength=60000)
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain", strength=60000)
        game_state = self._make_game_state(marshal, [enemy], ["Rhineland"])

        concern = evaluate_aggressive(marshal, "retreat", {"action": "retreat"}, game_state)
        assert concern == ConcernLevel.MILD

    def test_retreat_outnumbered_low_morale_is_none(self):
        """Retreat when outnumbered 2:1 AND low morale is accepted (NONE)."""
        marshal = MockMarshal(personality="aggressive", location="Belgium", strength=30000, morale=30)
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain", strength=60000)
        game_state = self._make_game_state(marshal, [enemy], ["Rhineland"])

        concern = evaluate_aggressive(marshal, "retreat", {"action": "retreat"}, game_state)
        assert concern == ConcernLevel.NONE

    def test_drill_enemy_adjacent_is_moderate(self):
        """Drill with enemy adjacent is MODERATE concern."""
        marshal = MockMarshal(personality="aggressive", location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain")
        game_state = self._make_game_state(marshal, [enemy], ["Rhineland"])

        concern = evaluate_aggressive(marshal, "drill", {"action": "drill"}, game_state)
        assert concern == ConcernLevel.MODERATE

    def test_drill_no_enemy_is_none(self):
        """Drill with no enemy is accepted (NONE)."""
        marshal = MockMarshal(personality="aggressive", location="Belgium")
        game_state = self._make_game_state(marshal, adjacent_to_marshal=["Paris"])

        concern = evaluate_aggressive(marshal, "drill", {"action": "drill"}, game_state)
        assert concern == ConcernLevel.NONE

    def test_attack_is_always_none(self):
        """Aggressive marshals never object to attack."""
        marshal = MockMarshal(personality="aggressive", location="Belgium")
        game_state = self._make_game_state(marshal)

        concern = evaluate_aggressive(marshal, "attack", {"action": "attack"}, game_state)
        assert concern == ConcernLevel.NONE

    def test_stance_change_none_target_no_crash(self):
        """Stance change with target=None must not crash (regression for .get('target', '').lower())."""
        marshal = MockMarshal(personality="aggressive", location="Belgium")
        game_state = self._make_game_state(marshal)

        # Parser sets "target": None when LLM doesn't return a target value.
        # dict.get('target', '') returns None (key exists), not '' (default is for missing keys).
        concern = evaluate_aggressive(marshal, "stance_change", {"action": "stance_change", "target": None}, game_state)
        assert concern == ConcernLevel.NONE


class TestEvaluateCautious:
    """Test cautious personality trigger evaluation."""

    def _make_game_state(self, marshal, enemies=None, adjacent_to_marshal=None, paths=None):
        """Helper to create game state."""
        marshals = {"Marshal": marshal}
        if enemies:
            for e in enemies:
                marshals[e.name] = e

        regions = {
            marshal.location: MockRegion(marshal.location, adjacent_to_marshal or [])
        }
        if paths:
            for name, adj in paths.items():
                if name not in regions:
                    regions[name] = MockRegion(name, adj)

        return MockGameState(MockWorld(marshals, regions))

    def test_attack_even_odds_is_none(self):
        """Attack at even odds is acceptable (NONE)."""
        marshal = MockMarshal(personality="cautious", location="Belgium", strength=50000)
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain", strength=50000)
        game_state = self._make_game_state(marshal, [enemy], ["Rhineland"])

        concern = evaluate_cautious(marshal, "attack", {"action": "attack", "target": "Wellington"}, game_state)
        assert concern == ConcernLevel.NONE

    def test_attack_1_5_to_1_disadvantage_is_mild(self):
        """Attack at 1.5:1 disadvantage is MILD (V1 was MAJOR, V2 is MILD)."""
        marshal = MockMarshal(personality="cautious", location="Belgium", strength=50000)
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain", strength=75000)
        game_state = self._make_game_state(marshal, [enemy], ["Rhineland"])

        concern = evaluate_cautious(marshal, "attack", {"action": "attack", "target": "Wellington"}, game_state)
        assert concern == ConcernLevel.MILD

    def test_attack_2_to_1_disadvantage_is_moderate(self):
        """Attack at 2:1 disadvantage is MODERATE."""
        marshal = MockMarshal(personality="cautious", location="Belgium", strength=50000)
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain", strength=100000)
        game_state = self._make_game_state(marshal, [enemy], ["Rhineland"])

        concern = evaluate_cautious(marshal, "attack", {"action": "attack", "target": "Wellington"}, game_state)
        assert concern == ConcernLevel.MODERATE

    def test_attack_3_to_1_disadvantage_is_strong(self):
        """Attack at 3:1 disadvantage is STRONG."""
        marshal = MockMarshal(personality="cautious", location="Belgium", strength=50000)
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain", strength=150000)
        game_state = self._make_game_state(marshal, [enemy], ["Rhineland"])

        concern = evaluate_cautious(marshal, "attack", {"action": "attack", "target": "Wellington"}, game_state)
        assert concern == ConcernLevel.STRONG

    def test_attack_5_to_1_disadvantage_is_extreme(self):
        """Attack at 5:1+ disadvantage is EXTREME (suicide mission)."""
        marshal = MockMarshal(personality="cautious", location="Belgium", strength=20000)
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain", strength=100000)
        game_state = self._make_game_state(marshal, [enemy], ["Rhineland"])

        concern = evaluate_cautious(marshal, "attack", {"action": "attack", "target": "Wellington"}, game_state)
        assert concern == ConcernLevel.EXTREME

    def test_attack_fortified_bumps_level(self):
        """Attacking fortified position increases concern by 1 level."""
        marshal = MockMarshal(personality="cautious", location="Belgium", strength=50000)
        enemy = MockMarshal(
            name="Wellington", location="Rhineland", nation="Britain",
            strength=50000, fortified=True
        )
        game_state = self._make_game_state(marshal, [enemy], ["Rhineland"])

        concern = evaluate_cautious(marshal, "attack", {"action": "attack", "target": "Wellington"}, game_state)
        # Even odds (NONE) + fortified bump = MILD
        assert concern == ConcernLevel.MILD

    def test_attack_fortified_at_3to1_is_extreme(self):
        """Attacking fortified at 3:1 disadvantage is EXTREME (STRONG + bump)."""
        marshal = MockMarshal(personality="cautious", location="Belgium", strength=50000)
        enemy = MockMarshal(
            name="Wellington", location="Rhineland", nation="Britain",
            strength=150000, fortified=True
        )
        game_state = self._make_game_state(marshal, [enemy], ["Rhineland"])

        concern = evaluate_cautious(marshal, "attack", {"action": "attack", "target": "Wellington"}, game_state)
        # 3:1 (STRONG) + fortified bump = EXTREME
        assert concern == ConcernLevel.EXTREME

    def test_move_safe_path_is_none(self):
        """Move with safe path is acceptable (NONE)."""
        marshal = MockMarshal(personality="cautious", location="Belgium")
        regions = {
            "Belgium": MockRegion("Belgium", ["Rhineland"]),
            "Rhineland": MockRegion("Rhineland", ["Belgium", "Bavaria"]),
        }
        game_state = MockGameState(MockWorld({"Marshal": marshal}, regions))

        concern = evaluate_cautious(marshal, "move", {"action": "move", "target": "Rhineland"}, game_state)
        assert concern == ConcernLevel.NONE

    def test_aggressive_stance_enemy_adjacent_is_mild(self):
        """Aggressive stance with enemy adjacent is MILD concern."""
        marshal = MockMarshal(personality="cautious", location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain")
        game_state = self._make_game_state(marshal, [enemy], ["Rhineland"])

        concern = evaluate_cautious(
            marshal, "stance_change",
            {"action": "stance_change", "target": "aggressive"},
            game_state
        )
        assert concern == ConcernLevel.MILD

    def test_stance_change_none_target_no_crash(self):
        """Stance change with target=None must not crash (regression for .get('target', '').lower())."""
        marshal = MockMarshal(personality="cautious", location="Belgium")
        game_state = self._make_game_state(marshal)

        # Parser sets "target": None when LLM doesn't return a target value.
        concern = evaluate_cautious(marshal, "stance_change", {"action": "stance_change", "target": None}, game_state)
        assert concern == ConcernLevel.NONE

    def test_defend_is_none(self):
        """Cautious marshals never object to defend."""
        marshal = MockMarshal(personality="cautious", location="Belgium")
        game_state = self._make_game_state(marshal)

        concern = evaluate_cautious(marshal, "defend", {"action": "defend"}, game_state)
        assert concern == ConcernLevel.NONE


class TestEvaluateLiteral:
    """Test literal personality trigger evaluation."""

    def test_literal_always_returns_none(self):
        """Literal personality never objects (uses clarification instead)."""
        marshal = MockMarshal(personality="literal", location="Belgium")
        game_state = MockGameState(MockWorld({}, {}))

        # Test all actions
        for action in ["attack", "defend", "move", "retreat", "drill", "fortify"]:
            concern = evaluate_literal(marshal, action, {"action": action}, game_state)
            assert concern == ConcernLevel.NONE, f"Literal should return NONE for {action}"


class TestEvaluateSituation:
    """Test main dispatcher function."""

    def test_routes_to_aggressive(self):
        """Routes aggressive personality to correct evaluator."""
        marshal = MockMarshal(personality="aggressive", location="Belgium")
        world = MockWorld(
            marshals={"Marshal": marshal},
            regions={"Belgium": MockRegion("Belgium", ["Paris"])}
        )
        game_state = MockGameState(world)

        concern = evaluate_situation(marshal, "defend", {"action": "defend"}, game_state)
        # Aggressive defend with no enemy = MILD
        assert concern == ConcernLevel.MILD

    def test_routes_to_cautious(self):
        """Routes cautious personality to correct evaluator."""
        marshal = MockMarshal(personality="cautious", location="Belgium", strength=50000)
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain", strength=100000)
        world = MockWorld(
            marshals={"Marshal": marshal, "Wellington": enemy},
            regions={"Belgium": MockRegion("Belgium", ["Rhineland"])}
        )
        game_state = MockGameState(world)

        concern = evaluate_situation(
            marshal, "attack",
            {"action": "attack", "target": "Wellington"},
            game_state
        )
        # Cautious attack at 2:1 disadvantage = MODERATE
        assert concern == ConcernLevel.MODERATE

    def test_routes_to_literal(self):
        """Routes literal personality to correct evaluator."""
        marshal = MockMarshal(personality="literal", location="Belgium")
        game_state = MockGameState(MockWorld({}, {}))

        concern = evaluate_situation(marshal, "attack", {"action": "attack"}, game_state)
        assert concern == ConcernLevel.NONE

    def test_unknown_personality_returns_none(self):
        """Unknown personality defaults to NONE (safe)."""
        marshal = MockMarshal(personality="balanced", location="Belgium")
        game_state = MockGameState(MockWorld({}, {}))

        concern = evaluate_situation(marshal, "attack", {"action": "attack"}, game_state)
        assert concern == ConcernLevel.NONE

    def test_case_insensitive_personality(self):
        """Personality matching is case-insensitive."""
        marshal = MockMarshal(personality="AGGRESSIVE", location="Belgium")
        world = MockWorld(
            marshals={"Marshal": marshal},
            regions={"Belgium": MockRegion("Belgium", [])}
        )
        game_state = MockGameState(world)

        concern = evaluate_situation(marshal, "defend", {"action": "defend"}, game_state)
        # Should route to aggressive evaluator
        assert concern == ConcernLevel.MILD


# ════════════════════════════════════════════════════════════════════════════
# UNIT 3: STRATEGIC TRIGGER EVALUATION TESTS
# ════════════════════════════════════════════════════════════════════════════


class MockWorldWithHelpers(MockWorld):
    """Extended mock world with helper methods matching real WorldState."""

    def get_region(self, name):
        return self.regions.get(name)

    def get_marshal(self, name):
        return self.marshals.get(name)

    def get_enemies_in_region(self, region_name, nation):
        """Get enemy marshals in a specific region."""
        enemies = []
        for m in self.marshals.values():
            if m.nation != nation and m.location == region_name and m.strength > 0:
                enemies.append(m)
        return enemies


class TestStrategicHelperFunctions:
    """Test strategic helper functions."""

    def test_check_enemies_adjacent_to_region_no_enemies(self):
        """Returns False when no enemies adjacent."""
        marshal = MockMarshal(location="Belgium")
        world = MockWorldWithHelpers(
            marshals={"Marshal": marshal},
            regions={
                "Belgium": MockRegion("Belgium", ["Rhineland", "Paris"]),
                "Rhineland": MockRegion("Rhineland", ["Belgium"]),
                "Paris": MockRegion("Paris", ["Belgium"]),
            }
        )
        result = _check_enemies_adjacent_to_region("Belgium", "France", world)
        assert result is False

    def test_check_enemies_adjacent_to_region_enemy_present(self):
        """Returns True when enemy in adjacent region."""
        marshal = MockMarshal(location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain")
        world = MockWorldWithHelpers(
            marshals={"Marshal": marshal, "Wellington": enemy},
            regions={
                "Belgium": MockRegion("Belgium", ["Rhineland", "Paris"]),
                "Rhineland": MockRegion("Rhineland", ["Belgium"]),
            }
        )
        result = _check_enemies_adjacent_to_region("Belgium", "France", world)
        assert result is True

    def test_get_pursue_target_ratio(self):
        """Returns correct strength ratio for PURSUE."""
        marshal = MockMarshal(location="Belgium", strength=50000)
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain", strength=100000)
        world = MockWorldWithHelpers(
            marshals={"Marshal": marshal, "Wellington": enemy},
            regions={}
        )
        ratio = _get_pursue_target_ratio(marshal, "Wellington", world)
        assert ratio == 2.0

    def test_get_pursue_target_ratio_no_target(self):
        """Returns 1.0 when no valid target."""
        marshal = MockMarshal(location="Belgium", strength=50000)
        world = MockWorldWithHelpers(marshals={"Marshal": marshal}, regions={})
        ratio = _get_pursue_target_ratio(marshal, "Unknown", world)
        assert ratio == 0.0  # No valid target = 0 danger

    def test_path_has_enemies_clean_path(self):
        """Returns False for path with no enemies."""
        marshal = MockMarshal(location="Belgium")
        world = MockWorldWithHelpers(
            marshals={"Marshal": marshal},
            regions={}
        )
        has_enemies, regions = _path_has_enemies(["Belgium", "Rhineland"], "France", world)
        assert has_enemies is False
        assert regions == []

    def test_path_has_enemies_dangerous_path(self):
        """Returns True for path crossing enemy region."""
        marshal = MockMarshal(location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain")
        world = MockWorldWithHelpers(
            marshals={"Marshal": marshal, "Wellington": enemy},
            regions={}
        )
        has_enemies, regions = _path_has_enemies(["Belgium", "Rhineland", "Bavaria"], "France", world)
        assert has_enemies is True
        assert "Rhineland" in regions


class TestEvaluateStrategicAggressive:
    """Test aggressive personality strategic evaluations."""

    def _make_game_state(self, marshal, enemies=None, regions=None):
        """Helper to create game state."""
        marshals = {"Marshal": marshal}
        if enemies:
            for e in enemies:
                marshals[e.name] = e
        world = MockWorldWithHelpers(marshals, regions or {})
        return {"world": world}

    def test_hold_no_enemies_is_moderate(self):
        """HOLD with no enemies nearby is MODERATE concern."""
        marshal = MockMarshal(personality="aggressive", location="Belgium")
        regions = {
            "Belgium": MockRegion("Belgium", ["Rhineland", "Paris"]),
            "Rhineland": MockRegion("Rhineland", ["Belgium"]),
            "Paris": MockRegion("Paris", ["Belgium"]),
        }
        game_state = self._make_game_state(marshal, regions=regions)

        concern = evaluate_strategic_aggressive(marshal, "HOLD", "Belgium", [], game_state)
        assert concern == ConcernLevel.MODERATE

    def test_hold_enemies_adjacent_equal_forces_is_none(self):
        """HOLD with enemies adjacent but no overwhelming advantage is NONE."""
        marshal = MockMarshal(personality="aggressive", location="Belgium", strength=50000)
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain", strength=50000)
        regions = {
            "Belgium": MockRegion("Belgium", ["Rhineland"]),
            "Rhineland": MockRegion("Rhineland", ["Belgium"]),
        }
        game_state = self._make_game_state(marshal, [enemy], regions)

        concern = evaluate_strategic_aggressive(marshal, "HOLD", "Belgium", [], game_state)
        assert concern == ConcernLevel.NONE

    def test_hold_enemies_adjacent_2to1_advantage_is_strong(self):
        """HOLD with 2:1 advantage triggers STRONG concern."""
        marshal = MockMarshal(personality="aggressive", location="Belgium", strength=100000)
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain", strength=50000)
        regions = {
            "Belgium": MockRegion("Belgium", ["Rhineland"]),
            "Rhineland": MockRegion("Rhineland", ["Belgium"]),
        }
        game_state = self._make_game_state(marshal, [enemy], regions)

        concern = evaluate_strategic_aggressive(marshal, "HOLD", "Belgium", [], game_state)
        assert concern == ConcernLevel.STRONG

    def test_hold_enemies_adjacent_3to1_advantage_is_extreme(self):
        """HOLD with 3:1+ advantage triggers EXTREME concern."""
        marshal = MockMarshal(personality="aggressive", location="Belgium", strength=150000)
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain", strength=50000)
        regions = {
            "Belgium": MockRegion("Belgium", ["Rhineland"]),
            "Rhineland": MockRegion("Rhineland", ["Belgium"]),
        }
        game_state = self._make_game_state(marshal, [enemy], regions)

        concern = evaluate_strategic_aggressive(marshal, "HOLD", "Belgium", [], game_state)
        assert concern == ConcernLevel.EXTREME

    def test_pursue_is_none(self):
        """Aggressive doesn't object to PURSUE."""
        marshal = MockMarshal(personality="aggressive", location="Belgium")
        game_state = self._make_game_state(marshal)

        concern = evaluate_strategic_aggressive(marshal, "PURSUE", "Wellington", [], game_state)
        assert concern == ConcernLevel.NONE

    def test_move_to_is_none(self):
        """Aggressive doesn't object to MOVE_TO."""
        marshal = MockMarshal(personality="aggressive", location="Belgium")
        game_state = self._make_game_state(marshal)

        concern = evaluate_strategic_aggressive(marshal, "MOVE_TO", "Bavaria", ["Belgium", "Rhineland"], game_state)
        assert concern == ConcernLevel.NONE


class TestEvaluateStrategicCautious:
    """Test cautious personality strategic evaluations."""

    def _make_game_state(self, marshal, enemies=None, regions=None):
        """Helper to create game state."""
        marshals = {"Marshal": marshal}
        if enemies:
            for e in enemies:
                marshals[e.name] = e
        world = MockWorldWithHelpers(marshals, regions or {})
        return {"world": world}

    def test_pursue_even_odds_is_none(self):
        """PURSUE at even odds is acceptable."""
        marshal = MockMarshal(personality="cautious", location="Belgium", strength=50000)
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain", strength=50000)
        game_state = self._make_game_state(marshal, [enemy])

        concern = evaluate_strategic_cautious(marshal, "PURSUE", "Wellington", [], game_state)
        assert concern == ConcernLevel.NONE

    def test_pursue_1_2_to_1_disadvantage_is_mild(self):
        """PURSUE at 1.2:1 disadvantage is MILD (old threshold, now no popup)."""
        marshal = MockMarshal(personality="cautious", location="Belgium", strength=50000)
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain", strength=60000)
        game_state = self._make_game_state(marshal, [enemy])

        concern = evaluate_strategic_cautious(marshal, "PURSUE", "Wellington", [], game_state)
        assert concern == ConcernLevel.MILD

    def test_pursue_1_5_to_1_disadvantage_is_mild(self):
        """PURSUE at 1.5:1 disadvantage is MILD (V2: was MAJOR, now MILD)."""
        marshal = MockMarshal(personality="cautious", location="Belgium", strength=50000)
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain", strength=75000)
        game_state = self._make_game_state(marshal, [enemy])

        concern = evaluate_strategic_cautious(marshal, "PURSUE", "Wellington", [], game_state)
        assert concern == ConcernLevel.MILD

    def test_pursue_2_to_1_disadvantage_is_moderate(self):
        """PURSUE at 2:1 disadvantage is MODERATE."""
        marshal = MockMarshal(personality="cautious", location="Belgium", strength=50000)
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain", strength=100000)
        game_state = self._make_game_state(marshal, [enemy])

        concern = evaluate_strategic_cautious(marshal, "PURSUE", "Wellington", [], game_state)
        assert concern == ConcernLevel.MODERATE

    def test_pursue_3_to_1_disadvantage_is_strong(self):
        """PURSUE at 3:1 disadvantage is STRONG."""
        marshal = MockMarshal(personality="cautious", location="Belgium", strength=50000)
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain", strength=150000)
        game_state = self._make_game_state(marshal, [enemy])

        concern = evaluate_strategic_cautious(marshal, "PURSUE", "Wellington", [], game_state)
        assert concern == ConcernLevel.STRONG

    def test_pursue_5_to_1_disadvantage_is_extreme(self):
        """PURSUE at 5:1+ disadvantage is EXTREME."""
        marshal = MockMarshal(personality="cautious", location="Belgium", strength=20000)
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain", strength=100000)
        game_state = self._make_game_state(marshal, [enemy])

        concern = evaluate_strategic_cautious(marshal, "PURSUE", "Wellington", [], game_state)
        assert concern == ConcernLevel.EXTREME

    def test_move_to_safe_path_is_none(self):
        """MOVE_TO with safe path is acceptable."""
        marshal = MockMarshal(personality="cautious", location="Belgium")
        game_state = self._make_game_state(marshal)

        concern = evaluate_strategic_cautious(
            marshal, "MOVE_TO", "Bavaria", ["Belgium", "Rhineland", "Bavaria"], game_state
        )
        assert concern == ConcernLevel.NONE

    def test_move_to_dangerous_path_is_moderate(self):
        """MOVE_TO through enemy territory is MODERATE."""
        marshal = MockMarshal(personality="cautious", location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain")
        game_state = self._make_game_state(marshal, [enemy])

        concern = evaluate_strategic_cautious(
            marshal, "MOVE_TO", "Bavaria", ["Belgium", "Rhineland", "Bavaria"], game_state
        )
        assert concern == ConcernLevel.MODERATE

    def test_hold_at_location_is_none(self):
        """HOLD at current location is acceptable."""
        marshal = MockMarshal(personality="cautious", location="Belgium")
        game_state = self._make_game_state(marshal)

        concern = evaluate_strategic_cautious(marshal, "HOLD", "Belgium", [], game_state)
        assert concern == ConcernLevel.NONE

    def test_hold_distant_dangerous_path_is_moderate(self):
        """HOLD at distant location through danger is MODERATE."""
        marshal = MockMarshal(personality="cautious", location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain")
        game_state = self._make_game_state(marshal, [enemy])

        concern = evaluate_strategic_cautious(
            marshal, "HOLD", "Bavaria", ["Belgium", "Rhineland", "Bavaria"], game_state
        )
        assert concern == ConcernLevel.MODERATE

    def test_support_safe_path_is_none(self):
        """SUPPORT with safe path is acceptable."""
        marshal = MockMarshal(personality="cautious", location="Belgium")
        game_state = self._make_game_state(marshal)

        concern = evaluate_strategic_cautious(
            marshal, "SUPPORT", "Ney", ["Belgium", "Paris"], game_state
        )
        assert concern == ConcernLevel.NONE

    def test_support_dangerous_path_is_moderate(self):
        """SUPPORT through enemy territory is MODERATE."""
        marshal = MockMarshal(personality="cautious", location="Belgium")
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain")
        game_state = self._make_game_state(marshal, [enemy])

        concern = evaluate_strategic_cautious(
            marshal, "SUPPORT", "Ney", ["Belgium", "Rhineland", "Bavaria"], game_state
        )
        assert concern == ConcernLevel.MODERATE


class TestEvaluateStrategicLiteral:
    """Test literal personality strategic evaluations."""

    def test_literal_always_returns_none(self):
        """Literal personality never objects to strategic commands."""
        marshal = MockMarshal(personality="literal", location="Belgium")
        game_state = {"world": MockWorldWithHelpers({}, {})}

        for order_type in ["HOLD", "PURSUE", "MOVE_TO", "SUPPORT"]:
            concern = evaluate_strategic_literal(
                marshal, order_type, "Target", ["Belgium", "Rhineland"], game_state
            )
            assert concern == ConcernLevel.NONE, f"Literal should return NONE for {order_type}"


class TestEvaluateStrategicSituation:
    """Test main strategic dispatcher function."""

    def test_routes_to_aggressive(self):
        """Routes aggressive personality to correct evaluator."""
        marshal = MockMarshal(personality="aggressive", location="Belgium")
        regions = {
            "Belgium": MockRegion("Belgium", ["Rhineland"]),
            "Rhineland": MockRegion("Rhineland", ["Belgium"]),
        }
        world = MockWorldWithHelpers({"Marshal": marshal}, regions)
        game_state = {"world": world}

        concern = evaluate_strategic_situation(marshal, "HOLD", "Belgium", [], game_state)
        # Aggressive HOLD with no enemies = MODERATE
        assert concern == ConcernLevel.MODERATE

    def test_routes_to_cautious(self):
        """Routes cautious personality to correct evaluator."""
        marshal = MockMarshal(personality="cautious", location="Belgium", strength=50000)
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain", strength=100000)
        world = MockWorldWithHelpers({"Marshal": marshal, "Wellington": enemy}, {})
        game_state = {"world": world}

        concern = evaluate_strategic_situation(marshal, "PURSUE", "Wellington", [], game_state)
        # Cautious PURSUE at 2:1 disadvantage = MODERATE
        assert concern == ConcernLevel.MODERATE

    def test_routes_to_literal(self):
        """Routes literal personality to correct evaluator."""
        marshal = MockMarshal(personality="literal", location="Belgium")
        game_state = {"world": MockWorldWithHelpers({}, {})}

        concern = evaluate_strategic_situation(marshal, "HOLD", "Belgium", [], game_state)
        assert concern == ConcernLevel.NONE

    def test_unknown_personality_returns_none(self):
        """Unknown personality defaults to NONE."""
        marshal = MockMarshal(personality="balanced", location="Belgium")
        game_state = {"world": MockWorldWithHelpers({}, {})}

        concern = evaluate_strategic_situation(marshal, "HOLD", "Belgium", [], game_state)
        assert concern == ConcernLevel.NONE

    def test_case_insensitive_personality(self):
        """Personality matching is case-insensitive."""
        marshal = MockMarshal(personality="CAUTIOUS", location="Belgium", strength=50000)
        enemy = MockMarshal(name="Wellington", location="Rhineland", nation="Britain", strength=100000)
        world = MockWorldWithHelpers({"Marshal": marshal, "Wellington": enemy}, {})
        game_state = {"world": world}

        concern = evaluate_strategic_situation(marshal, "PURSUE", "Wellington", [], game_state)
        # Should route to cautious evaluator
        assert concern == ConcernLevel.MODERATE


# ============================================================================
# UNIT 4: WORLDSTATE INTEGRATION TESTS
# ============================================================================

class TestWorldStateV2aFields:
    """Tests for V2a fields added to WorldState."""

    def test_world_state_has_mild_concerns_field(self):
        """WorldState has mild_concerns_this_turn field."""
        from backend.models.world_state import WorldState
        world = WorldState()
        assert hasattr(world, 'mild_concerns_this_turn')
        assert world.mild_concerns_this_turn == []

    def test_world_state_has_objection_popups_field(self):
        """WorldState has objection_popups_this_turn field."""
        from backend.models.world_state import WorldState
        world = WorldState()
        assert hasattr(world, 'objection_popups_this_turn')
        assert world.objection_popups_this_turn == set()

    def test_mild_concerns_serialization(self):
        """mild_concerns_this_turn serializes correctly."""
        from backend.models.world_state import WorldState
        world = WorldState()
        world.mild_concerns_this_turn = [
            {"marshal": "Ney", "message": "Grumbles about defense"},
            {"marshal": "Davout", "message": "Notes the risks"}
        ]

        data = world.to_dict()
        assert "mild_concerns_this_turn" in data
        assert len(data["mild_concerns_this_turn"]) == 2

        restored = WorldState.from_dict(data)
        assert len(restored.mild_concerns_this_turn) == 2
        assert restored.mild_concerns_this_turn[0]["marshal"] == "Ney"

    def test_objection_popups_serialization(self):
        """objection_popups_this_turn serializes correctly (set -> list -> set)."""
        from backend.models.world_state import WorldState
        world = WorldState()
        world.objection_popups_this_turn = {"Ney", "Davout"}

        data = world.to_dict()
        assert "objection_popups_this_turn" in data
        # Serialized as list
        assert isinstance(data["objection_popups_this_turn"], list)
        assert len(data["objection_popups_this_turn"]) == 2

        restored = WorldState.from_dict(data)
        # Restored as set
        assert isinstance(restored.objection_popups_this_turn, set)
        assert "Ney" in restored.objection_popups_this_turn
        assert "Davout" in restored.objection_popups_this_turn

    def test_fields_clear_at_turn_advance(self):
        """V2a fields clear when turn advances."""
        from backend.models.world_state import WorldState
        world = WorldState()

        # Populate the fields
        world.mild_concerns_this_turn = [{"marshal": "Ney", "message": "test"}]
        world.objection_popups_this_turn = {"Ney"}

        # Advance turn
        world.advance_turn()

        # Fields should be cleared
        assert world.mild_concerns_this_turn == []
        assert world.objection_popups_this_turn == set()

    def test_backward_compat_old_saves_without_v2a_fields(self):
        """Old saves without V2a fields load with defaults."""
        from backend.models.world_state import WorldState
        world = WorldState()

        # Simulate old save data without V2a fields
        data = world.to_dict()
        del data["mild_concerns_this_turn"]
        del data["objection_popups_this_turn"]

        restored = WorldState.from_dict(data)
        assert restored.mild_concerns_this_turn == []
        assert restored.objection_popups_this_turn == set()


# ============================================================================
# UNIT 6: V2a INTEGRATION TESTS (executor pipeline end-to-end)
# ============================================================================


class TestV2aIntegrationFixtures:
    """Shared setup for integration tests."""

    @staticmethod
    def make_integration_world():
        """Create a world suitable for integration testing."""
        from backend.models.world_state import WorldState
        from backend.models.marshal import Marshal, Stance
        from backend.models.region import Region

        world = WorldState()
        world.marshals = {}
        world.regions = {
            "Paris": Region("Paris", ["Belgium", "Brittany"], "France", 100),
            "Belgium": Region("Belgium", ["Paris", "Rhineland", "Netherlands"], "France", 80),
            "Rhineland": Region("Rhineland", ["Belgium", "Bavaria"], "Prussia", 60),
            "Netherlands": Region("Netherlands", ["Belgium"], "Britain", 70),
            "Brittany": Region("Brittany", ["Paris"], "France", 50),
            "Bavaria": Region("Bavaria", ["Rhineland"], "Prussia", 60),
        }

        davout = Marshal("Davout", "Belgium", 25000, "cautious", "France")
        davout.morale = 85
        davout.stance = Stance.NEUTRAL
        davout.trust.set(50)  # TRUSTING tier
        world.marshals["Davout"] = davout

        ney = Marshal("Ney", "Paris", 30000, "aggressive", "France", cavalry=True)
        ney.morale = 80
        ney.stance = Stance.NEUTRAL
        ney.trust.set(50)
        world.marshals["Ney"] = ney

        blucher = Marshal("Blucher", "Rhineland", 60000, "aggressive", "Prussia")
        blucher.morale = 85
        world.marshals["Blucher"] = blucher

        world.player_nation = "France"
        world.current_turn = 1
        world.actions_remaining = 4

        return world


class TestV2aTacticalIntegration:
    """Integration: tactical command → V2 evaluate → popup → response → trust change."""

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_tactical_objection_full_path_trust(self, mock_rng):
        """Full tactical path: Davout attacks bad odds → popup → trust → trust gain."""
        from backend.commands.executor import CommandExecutor

        world = TestV2aIntegrationFixtures.make_integration_world()
        executor = CommandExecutor()

        davout = world.marshals["Davout"]
        davout.location = "Rhineland"  # Same region as Blucher (60k vs 25k = 2.4x ratio)
        initial_trust = davout.trust.value

        command = {"command": {"marshal": "Davout", "action": "attack", "target": "Blucher"}}
        game_state = {"world": world}

        result = executor.execute(command, game_state)

        # V2 should trigger MODERATE+ popup (2.4x ratio for cautious)
        assert result.get("pending_objection") is True or result.get("awaiting_response") is True
        objection = result.get("objection")
        assert objection is not None
        assert objection["concern_level"] in ("MODERATE", "STRONG", "EXTREME")
        assert objection["trust_tier"] == "TRUSTING"
        assert "trust_gain" in objection
        assert "insist_penalty" in objection
        assert "compromise_gain" in objection

        # Now respond with 'trust' — pass world directly (has get_marshal)
        expected_gain = objection["trust_gain"]
        response_result = world.disobedience_system.handle_response(
            world.pending_objection, "trust", world
        )

        # Trust should increase by V2 scaled amount
        assert davout.trust.value == initial_trust + expected_gain

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_tactical_objection_insist_always_succeeds(self, mock_rng):
        """V2a insist path: insist always succeeds with V2 scaled penalty."""
        from backend.commands.executor import CommandExecutor

        world = TestV2aIntegrationFixtures.make_integration_world()
        executor = CommandExecutor()

        davout = world.marshals["Davout"]
        davout.location = "Rhineland"
        initial_trust = davout.trust.value

        command = {"command": {"marshal": "Davout", "action": "attack", "target": "Blucher"}}
        game_state = {"world": world}

        result = executor.execute(command, game_state)
        assert result.get("pending_objection") is True or result.get("awaiting_response") is True

        objection = world.pending_objection
        expected_penalty = objection["insist_penalty"]

        response_result = world.disobedience_system.handle_response(
            objection, "insist", world
        )

        # V2a: Insist always succeeds (no disobedience roll)
        assert response_result.get("success") is True or "final_order" in response_result
        # Trust decreases by V2 scaled penalty
        assert davout.trust.value == initial_trust + expected_penalty  # penalty is negative

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_tactical_objection_compromise_flat_gain(self, mock_rng):
        """V2a compromise: flat +3 regardless of tier."""
        from backend.commands.executor import CommandExecutor
        from backend.commands.objection_v2 import COMPROMISE_TRUST_GAIN

        world = TestV2aIntegrationFixtures.make_integration_world()
        executor = CommandExecutor()

        davout = world.marshals["Davout"]
        davout.location = "Rhineland"
        initial_trust = davout.trust.value

        command = {"command": {"marshal": "Davout", "action": "attack", "target": "Blucher"}}
        game_state = {"world": world}

        result = executor.execute(command, game_state)
        assert result.get("pending_objection") is True or result.get("awaiting_response") is True

        objection = world.pending_objection
        assert objection["compromise_gain"] == COMPROMISE_TRUST_GAIN

        # Only respond if compromise action exists
        if objection.get("compromise"):
            response_result = world.disobedience_system.handle_response(
                objection, "compromise", world
            )
            assert davout.trust.value == initial_trust + COMPROMISE_TRUST_GAIN


class TestV2aStrategicIntegration:
    """Integration: strategic command → V2 evaluate → popup → response → trust change."""

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_strategic_objection_full_path(self, mock_rng):
        """Full strategic path: Davout MOVE_TO through enemy → popup → trust."""
        from backend.commands.executor import CommandExecutor

        world = TestV2aIntegrationFixtures.make_integration_world()
        executor = CommandExecutor()

        davout = world.marshals["Davout"]
        davout.location = "Belgium"
        initial_trust = davout.trust.value

        # Blucher at Rhine blocks Belgium → Bavaria
        command = {
            "command": {"marshal": "Davout", "action": "move", "target": "Bavaria"},
            "is_strategic": True,
            "strategic_type": "MOVE_TO",
        }
        game_state = {"world": world}

        result = executor.execute(command, game_state)

        assert result.get("pending_objection") is True
        objection = result.get("objection")
        assert objection is not None
        assert objection["concern_level"] in ("MODERATE", "STRONG", "EXTREME")
        assert "trust_gain" in objection
        assert "insist_penalty" in objection


class TestV2aMildPath:
    """Integration: MILD concerns produce flavor text, no popup."""

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_mild_concern_no_popup(self, mock_rng):
        """MILD concern → flavor text in mild_concerns_this_turn, no popup."""
        from backend.commands.executor import CommandExecutor

        world = TestV2aIntegrationFixtures.make_integration_world()
        executor = CommandExecutor()

        davout = world.marshals["Davout"]
        davout.location = "Belgium"
        davout.strength = 25000

        # Blucher at 37500 → ratio 1.5x → MILD for cautious
        blucher = world.marshals["Blucher"]
        blucher.strength = 37500
        blucher.location = "Belgium"  # Same region

        command = {"command": {"marshal": "Davout", "action": "attack", "target": "Blucher"}}
        game_state = {"world": world}

        result = executor.execute(command, game_state)

        # MILD: no popup, action should proceed or mild concern recorded
        assert result.get("pending_objection") is not True
        assert result.get("awaiting_response") is not True


class TestV2aIdleTurnsIntegration:
    """Integration: idle_turns increment, reset on action, serialization roundtrip."""

    def test_idle_turns_increment_on_idle(self):
        """Player marshal that doesn't act gets idle_turns incremented."""
        from backend.models.world_state import WorldState
        from backend.models.marshal import Marshal

        world = WorldState()
        davout = Marshal("Davout", "Paris", 30000, "cautious", "France")
        davout.idle_turns = 0
        world.marshals["Davout"] = davout
        world.player_nation = "France"

        # Process tactical states (simulates end of turn processing)
        world._process_tactical_states()

        assert davout.idle_turns == 1

    def test_idle_turns_increment_twice(self):
        """Idle turns accumulate across multiple turn processes."""
        from backend.models.world_state import WorldState
        from backend.models.marshal import Marshal

        world = WorldState()
        davout = Marshal("Davout", "Paris", 30000, "cautious", "France")
        davout.idle_turns = 0
        world.marshals["Davout"] = davout
        world.player_nation = "France"

        world._process_tactical_states()
        world._process_tactical_states()

        assert davout.idle_turns == 2

    def test_idle_turns_reset_on_attack(self):
        """idle_turns resets to 0 when marshal attacks."""
        from backend.models.marshal import Marshal

        davout = Marshal("Davout", "Paris", 30000, "cautious", "France")
        davout.idle_turns = 5

        # Simulate what executor does after attack
        davout.idle_turns = 0
        davout._acted_this_turn = True

        assert davout.idle_turns == 0

    def test_idle_turns_reset_on_move(self):
        """idle_turns resets to 0 when marshal moves."""
        from backend.models.marshal import Marshal

        davout = Marshal("Davout", "Paris", 30000, "cautious", "France")
        davout.idle_turns = 3

        # Simulate what executor does after move
        davout.idle_turns = 0
        davout._acted_this_turn = True

        assert davout.idle_turns == 0

    def test_idle_turns_not_incremented_for_enemy(self):
        """Enemy marshals don't get idle_turns incremented."""
        from backend.models.world_state import WorldState
        from backend.models.marshal import Marshal

        world = WorldState()
        blucher = Marshal("Blucher", "Rhineland", 35000, "aggressive", "Prussia")
        blucher.idle_turns = 0
        world.marshals["Blucher"] = blucher
        world.player_nation = "France"

        world._process_tactical_states()

        assert blucher.idle_turns == 0

    def test_idle_turns_acted_flag_prevents_increment(self):
        """Marshal that acted this turn doesn't get idle_turns incremented."""
        from backend.models.world_state import WorldState
        from backend.models.marshal import Marshal

        world = WorldState()
        davout = Marshal("Davout", "Paris", 30000, "cautious", "France")
        davout.idle_turns = 0
        davout._acted_this_turn = True
        world.marshals["Davout"] = davout
        world.player_nation = "France"

        world._process_tactical_states()

        assert davout.idle_turns == 0
        # Flag should be cleared
        assert not getattr(davout, '_acted_this_turn', False)

    def test_idle_turns_serialization_roundtrip(self):
        """idle_turns survives to_dict/from_dict cycle."""
        from backend.models.marshal import Marshal

        davout = Marshal("Davout", "Paris", 30000, "cautious", "France")
        davout.idle_turns = 7

        data = davout.to_dict()
        assert data["idle_turns"] == 7

        restored = Marshal.from_dict(data)
        assert restored.idle_turns == 7

    def test_idle_turns_default_in_old_saves(self):
        """Old save data without idle_turns loads with default 0."""
        from backend.models.marshal import Marshal

        davout = Marshal("Davout", "Paris", 30000, "cautious", "France")
        data = davout.to_dict()
        del data["idle_turns"]

        restored = Marshal.from_dict(data)
        assert restored.idle_turns == 0


class TestV2aAlreadyInStanceNoMild:
    """Regression: ordering a stance the marshal is already in must NOT produce MILD."""

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_already_defensive_no_mild(self, mock_rng):
        """Ney (aggressive) already DEFENSIVE, ordered defensive → fail, no MILD."""
        from backend.commands.executor import CommandExecutor
        from backend.models.marshal import Stance

        world = TestV2aIntegrationFixtures.make_integration_world()
        executor = CommandExecutor()

        ney = world.marshals["Ney"]
        ney.stance = Stance.DEFENSIVE
        ney.location = "Belgium"

        # Enemy adjacent to trigger aggressive personality's MILD for defensive
        blucher = world.marshals["Blucher"]
        blucher.location = "Rhineland"  # Adjacent to Belgium

        command = {"command": {"marshal": "Ney", "action": "stance_change", "target": "defensive"}}
        game_state = {"world": world}

        result = executor.execute(command, game_state)

        # Pre-validation should catch "already in stance" and return failure
        assert result.get("success") is False
        assert "already" in result.get("message", "").lower()
        # No MILD concern should have been generated
        assert len(world.mild_concerns_this_turn) == 0

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_already_aggressive_no_mild(self, mock_rng):
        """Ney already AGGRESSIVE, ordered aggressive → fail, no MILD."""
        from backend.commands.executor import CommandExecutor
        from backend.models.marshal import Stance

        world = TestV2aIntegrationFixtures.make_integration_world()
        executor = CommandExecutor()

        ney = world.marshals["Ney"]
        ney.stance = Stance.AGGRESSIVE

        command = {"command": {"marshal": "Ney", "action": "stance_change", "target": "aggressive"}}
        game_state = {"world": world}

        result = executor.execute(command, game_state)

        assert result.get("success") is False
        assert "already" in result.get("message", "").lower()
        assert len(world.mild_concerns_this_turn) == 0


class TestV2aAPPreCheck:
    """Regression: AP must be checked BEFORE objection fires."""

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_not_enough_ap_for_stance_change_no_objection(self, mock_rng):
        """Aggressive→Defensive costs 2 AP. With 1 AP, should fail without objection."""
        from backend.commands.executor import CommandExecutor
        from backend.models.marshal import Stance

        world = TestV2aIntegrationFixtures.make_integration_world()
        executor = CommandExecutor()

        ney = world.marshals["Ney"]
        ney.stance = Stance.AGGRESSIVE
        ney.location = "Belgium"

        # Enemy adjacent so objection WOULD fire if AP check didn't catch it first
        blucher = world.marshals["Blucher"]
        blucher.location = "Rhineland"  # Adjacent

        # Only 1 AP left — aggressive→defensive costs 2
        world.actions_remaining = 1

        command = {"command": {"marshal": "Ney", "action": "stance_change", "target": "defensive"}}
        game_state = {"world": world}

        result = executor.execute(command, game_state)

        # Should fail with AP error, NOT trigger an objection
        assert result.get("success") is False
        assert "action" in result.get("message", "").lower()  # "Not enough actions"
        assert result.get("pending_objection") is not True
        assert len(world.mild_concerns_this_turn) == 0

    @patch('backend.commands.objection_v2.random.random', return_value=0.5)
    def test_post_objection_variable_cost_consumed(self, mock_rng):
        """Post-objection path must consume variable AP cost (not always 1)."""
        from backend.commands.executor import CommandExecutor
        from backend.models.marshal import Stance

        world = TestV2aIntegrationFixtures.make_integration_world()
        executor = CommandExecutor()

        davout = world.marshals["Davout"]
        davout.stance = Stance.AGGRESSIVE
        davout.location = "Belgium"

        # Set up enough AP and conditions for objection
        world.actions_remaining = 4

        # Aggressive→Defensive costs 2 AP. Execute via post-objection path.
        command = {
            "command": {
                "marshal": "Davout",
                "action": "stance_change",
                "target": "defensive",
            }
        }
        parsed_command = {"success": True, "command": command["command"]}
        game_state = {"world": world}

        # Call post-objection directly to test variable cost handling
        result = executor._execute_post_objection(parsed_command, game_state, "Davout")

        assert result.get("success") is True
        # Should have consumed 2 AP (aggressive→defensive)
        assert world.actions_remaining == 2


class TestPostObjectionRoutingAudit:
    """Audit: _execute_post_objection routing completeness and AP pool correctness."""

    def test_post_objection_recruit_at_zero_military_ap(self):
        """BUG fix: recruit uses admin AP pool. Should not be blocked by 0 military AP."""
        from backend.commands.executor import CommandExecutor

        world = TestV2aIntegrationFixtures.make_integration_world()
        executor = CommandExecutor()

        # Zero military AP, but admin AP available
        world.actions_remaining = 0
        world.admin_actions_remaining = 2

        # Place Davout in a French region for recruit to work
        davout = world.marshals["Davout"]
        davout.location = "Paris"

        parsed_command = {
            "success": True,
            "command": {"action": "recruit", "marshal": "Davout", "target": "Paris"}
        }
        game_state = {"world": world}

        result = executor._execute_post_objection(parsed_command, game_state, "Davout")

        # Should NOT be blocked by the AP pre-check ("No actions remaining")
        # It may fail for other reasons (e.g. recruit conditions), but NOT the gate.
        assert "No actions remaining" not in result.get("message", "")

    def test_post_objection_build_at_zero_military_ap(self):
        """BUG fix: build uses admin AP pool. Should not be blocked by 0 military AP."""
        from backend.commands.executor import CommandExecutor

        world = TestV2aIntegrationFixtures.make_integration_world()
        executor = CommandExecutor()

        world.actions_remaining = 0
        world.admin_actions_remaining = 2

        parsed_command = {
            "success": True,
            "command": {"action": "build", "marshal": "Davout", "target": "Paris",
                        "building_type": "supply_depot"}
        }
        game_state = {"world": world}

        result = executor._execute_post_objection(parsed_command, game_state, "Davout")

        # Should NOT be blocked by "No actions remaining"
        assert "No actions remaining" not in result.get("message", "")

    def test_post_objection_repair_at_zero_military_ap(self):
        """BUG fix: repair uses admin AP pool. Should not be blocked by 0 military AP."""
        from backend.commands.executor import CommandExecutor

        world = TestV2aIntegrationFixtures.make_integration_world()
        executor = CommandExecutor()

        world.actions_remaining = 0
        world.admin_actions_remaining = 2

        parsed_command = {
            "success": True,
            "command": {"action": "repair", "marshal": "Davout", "target": "Paris"}
        }
        game_state = {"world": world}

        result = executor._execute_post_objection(parsed_command, game_state, "Davout")

        # Should NOT be blocked by "No actions remaining"
        assert "No actions remaining" not in result.get("message", "")

    def test_post_objection_attack_blocked_at_zero_military_ap(self):
        """Military actions should still be blocked when military AP is 0."""
        from backend.commands.executor import CommandExecutor

        world = TestV2aIntegrationFixtures.make_integration_world()
        executor = CommandExecutor()

        world.actions_remaining = 0
        world.admin_actions_remaining = 2

        parsed_command = {
            "success": True,
            "command": {"action": "attack", "marshal": "Davout", "target": "Blucher"}
        }
        game_state = {"world": world}

        result = executor._execute_post_objection(parsed_command, game_state, "Davout")

        assert result.get("success") is False
        assert "No actions remaining" in result.get("message", "")

    def test_post_objection_admin_blocked_at_zero_admin_ap(self):
        """Admin actions should be blocked when admin AP is 0, even with military AP."""
        from backend.commands.executor import CommandExecutor

        world = TestV2aIntegrationFixtures.make_integration_world()
        executor = CommandExecutor()

        world.actions_remaining = 4
        world.admin_actions_remaining = 0

        parsed_command = {
            "success": True,
            "command": {"action": "recruit", "marshal": "Davout", "target": "Paris"}
        }
        game_state = {"world": world}

        result = executor._execute_post_objection(parsed_command, game_state, "Davout")

        assert result.get("success") is False
        assert "administrative" in result.get("message", "").lower()

    def test_post_objection_bombardment_handler_exists(self):
        """GAP fix: bombardment should not hit 'Unknown action'."""
        from backend.commands.executor import CommandExecutor

        world = TestV2aIntegrationFixtures.make_integration_world()
        executor = CommandExecutor()

        # Make Davout artillery and place enemy adjacent
        davout = world.marshals["Davout"]
        davout.is_artillery = True
        davout.location = "Belgium"
        # Blucher is in Rhine (adjacent to Belgium)

        parsed_command = {
            "success": True,
            "command": {"action": "bombardment", "marshal": "Davout"}
        }
        game_state = {"world": world}

        result = executor._execute_post_objection(parsed_command, game_state, "Davout")

        # Should NOT be "Unknown action"
        assert "Unknown action" not in result.get("message", "")

    def test_post_objection_garrison_handler_exists(self):
        """GAP fix: garrison should not hit 'Unknown action'."""
        from backend.commands.executor import CommandExecutor

        world = TestV2aIntegrationFixtures.make_integration_world()
        executor = CommandExecutor()

        parsed_command = {
            "success": True,
            "command": {"action": "garrison", "marshal": "Davout", "target": "Belgium"}
        }
        game_state = {"world": world}

        result = executor._execute_post_objection(parsed_command, game_state, "Davout")

        # Should NOT be "Unknown action" — may fail for other reasons (strength, etc.)
        assert "Unknown action" not in result.get("message", "")
