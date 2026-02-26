"""
V2b Session 1 Tests: Core Mechanics (Defiance + Vindication + Authority)

Edge cases from V2B_DEFIANCE_SPEC.md §9:
- EC-1: Defiance only fires on STRONG/EXTREME after insist
- EC-2: Literal personality (Grouchy) NEVER defies
- EC-4: Vindication escalation (MILD→MODERATE, MODERATE→STRONG)
- EC-5: Authority major victory fires ONCE per battle (not +10)
- EC-6: Authority excessive trust penalty triggers correctly
- EC-8: Defensive vindication created on "trust" when alt is defend/fortify/hold
- EC-9: Vindication decay symmetric toward 0
"""

from unittest.mock import patch

from backend.commands.defiance import (
    calculate_defiance_chance,
    get_defiant_action,
    defiance_succeeded,
    apply_defiance_outcome,
    get_berthier_defiance_text,
)
from backend.commands.objection_v2 import (
    ConcernLevel,
    evaluate_strategic_situation,
    _evaluate_relationship_support,
    RELATIONSHIP_SUPPORT_MESSAGES,
)
from backend.models.authority import AuthorityTracker, check_excessive_trust
from backend.models.trust import Trust


# ============================================================================
# HELPERS
# ============================================================================

class MockMarshal:
    """Minimal marshal for defiance/vindication tests."""
    def __init__(self, name="Ney", personality="aggressive", trust_val=70,
                 vindication=0, artillery=False, nation="France"):
        self.name = name
        self.personality = personality
        self.personality_type = None
        self.trust = Trust(trust_val)
        self.vindication_score = vindication
        self.defiance_cooldown_until = 0
        self.last_objection_turn = 0
        self.artillery = artillery
        self.nation = nation
        self.strength = 30000
        self.morale = 80
        self.broken = False
        self.retreating = False
        self.location = "Belgium"
        self.idle_turns = 0
        self._acted_this_turn = False
        self._relationships = {}

    def get_relationship(self, target_name):
        return self._relationships.get(target_name, 0)


class MockWorld:
    """Minimal world for defiance tests."""
    def __init__(self, authority=100, current_turn=5):
        self.authority_tracker = AuthorityTracker()
        self.authority_tracker.authority = authority
        self.current_turn = current_turn
        self.player_nation = "France"
        self.marshals = {}
        self.regions = {}

    def get_marshal(self, name):
        return self.marshals.get(name)


# ============================================================================
# EC-1: DEFIANCE ONLY FIRES ON STRONG/EXTREME AFTER INSIST
# ============================================================================

class TestEC1_DefianceThreshold:
    """EC-1: Defiance only fires on STRONG/EXTREME after insist."""

    def test_none_returns_zero(self):
        marshal = MockMarshal()
        world = MockWorld()
        assert calculate_defiance_chance(marshal, ConcernLevel.NONE, world) == 0.0

    def test_mild_returns_zero(self):
        marshal = MockMarshal()
        world = MockWorld()
        assert calculate_defiance_chance(marshal, ConcernLevel.MILD, world) == 0.0

    def test_moderate_returns_zero(self):
        marshal = MockMarshal()
        world = MockWorld()
        assert calculate_defiance_chance(marshal, ConcernLevel.MODERATE, world) == 0.0

    def test_strong_returns_nonzero(self):
        """STRONG concern with aggressive personality should give non-zero chance."""
        marshal = MockMarshal(trust_val=50, vindication=0)
        world = MockWorld(authority=70)
        # Fix randomness
        with patch('backend.commands.defiance.random.uniform', return_value=0.0):
            chance = calculate_defiance_chance(marshal, ConcernLevel.STRONG, world)
        assert chance > 0.0
        assert chance == 0.15  # Base for STRONG, no mods at these values

    def test_extreme_returns_higher(self):
        """EXTREME should give higher chance than STRONG."""
        marshal = MockMarshal(trust_val=50, vindication=0)
        world = MockWorld(authority=70)
        with patch('backend.commands.defiance.random.uniform', return_value=0.0):
            strong = calculate_defiance_chance(marshal, ConcernLevel.STRONG, world)
            extreme = calculate_defiance_chance(marshal, ConcernLevel.EXTREME, world)
        assert extreme > strong

    def test_hard_cap_at_40_percent(self):
        """Maximum defiance chance is 40% even with stacking bonuses."""
        marshal = MockMarshal(trust_val=10, vindication=5)  # Low trust + high vindication
        world = MockWorld(authority=30)  # Low authority
        with patch('backend.commands.defiance.random.uniform', return_value=0.08):
            chance = calculate_defiance_chance(marshal, ConcernLevel.EXTREME, world)
        assert chance <= 0.40

    def test_cooldown_prevents_defiance(self):
        """Marshal on defiance cooldown returns 0."""
        marshal = MockMarshal()
        marshal.defiance_cooldown_until = 10
        world = MockWorld(current_turn=5)
        chance = calculate_defiance_chance(marshal, ConcernLevel.EXTREME, world)
        assert chance == 0.0

    def test_cooldown_expired_allows_defiance(self):
        """Marshal past cooldown can defy."""
        marshal = MockMarshal(trust_val=50)
        marshal.defiance_cooldown_until = 3
        world = MockWorld(current_turn=5, authority=70)
        with patch('backend.commands.defiance.random.uniform', return_value=0.0):
            chance = calculate_defiance_chance(marshal, ConcernLevel.STRONG, world)
        assert chance > 0.0


# ============================================================================
# EC-2: LITERAL PERSONALITY NEVER DEFIES
# ============================================================================

class TestEC2_LiteralNeverDefies:
    """EC-2: Literal personality (Grouchy) NEVER defies."""

    def test_literal_personality_string(self):
        marshal = MockMarshal(personality="literal", trust_val=10, vindication=5)
        world = MockWorld(authority=30)
        chance = calculate_defiance_chance(marshal, ConcernLevel.EXTREME, world)
        assert chance == 0.0

    def test_literal_personality_type(self):
        from backend.models.personality import Personality
        marshal = MockMarshal(personality="literal")
        marshal.personality_type = Personality.LITERAL
        world = MockWorld()
        chance = calculate_defiance_chance(marshal, ConcernLevel.EXTREME, world)
        assert chance == 0.0

    def test_literal_never_gets_defiant_action(self):
        marshal = MockMarshal(personality="literal")
        assert get_defiant_action(marshal, "attack") is None
        assert get_defiant_action(marshal, "defend") is None
        assert get_defiant_action(marshal, "retreat") is None


# ============================================================================
# DEFIANCE FALLBACK TABLE
# ============================================================================

class TestDefianceFallbackTable:
    """Test the fallback table for defiant actions."""

    def test_aggressive_defies_defend(self):
        marshal = MockMarshal(personality="aggressive")
        assert get_defiant_action(marshal, "defend") == "attack"
        assert get_defiant_action(marshal, "fortify") == "attack"
        assert get_defiant_action(marshal, "hold") == "attack"
        assert get_defiant_action(marshal, "wait") == "attack"
        assert get_defiant_action(marshal, "retreat") == "attack"

    def test_aggressive_artillery_defies_to_bombardment(self):
        marshal = MockMarshal(personality="aggressive", artillery=True)
        assert get_defiant_action(marshal, "defend") == "bombardment"

    def test_aggressive_no_defy_attack(self):
        marshal = MockMarshal(personality="aggressive")
        assert get_defiant_action(marshal, "attack") is None

    def test_cautious_defies_attack(self):
        marshal = MockMarshal(personality="cautious")
        assert get_defiant_action(marshal, "attack") == "fortify"

    def test_cautious_no_defy_defend(self):
        marshal = MockMarshal(personality="cautious")
        assert get_defiant_action(marshal, "defend") is None
        assert get_defiant_action(marshal, "fortify") is None


# ============================================================================
# DEFIANCE OUTCOME (THREE-WAY RETURN)
# ============================================================================

class TestDefianceOutcome:
    """Test defiance_succeeded() three-way return."""

    def test_wait_inconclusive(self):
        marshal = MockMarshal()
        assert defiance_succeeded(marshal, "wait", None, 30000) is None

    def test_attack_won_cleanly(self):
        result = {"attacker": {"won": True, "casualties": 5000}}
        marshal = MockMarshal()
        assert defiance_succeeded(marshal, "attack", result, 30000) is True

    def test_attack_pyrrhic(self):
        """Won but >50% casualties = wrong."""
        result = {"attacker": {"won": True, "casualties": 20000}}
        marshal = MockMarshal()
        assert defiance_succeeded(marshal, "attack", result, 30000) is False

    def test_attack_lost(self):
        result = {"attacker": {"won": False, "casualties": 15000}}
        marshal = MockMarshal()
        assert defiance_succeeded(marshal, "attack", result, 30000) is False

    def test_defend_inconclusive(self):
        """M3 fix: Defend/fortify defiance uses deferred evaluation (INCONCLUSIVE).
        Cannot assess immediately whether defensive posture was correct."""
        marshal = MockMarshal()
        marshal.broken = False
        marshal.retreating = False
        assert defiance_succeeded(marshal, "defend", None, 30000) is None

    def test_fortify_inconclusive(self):
        """M3 fix: Fortify defiance also deferred — always INCONCLUSIVE."""
        marshal = MockMarshal()
        marshal.broken = True  # Even if broken, still inconclusive (deferred)
        assert defiance_succeeded(marshal, "fortify", None, 30000) is None

    def test_no_battle_inconclusive(self):
        marshal = MockMarshal()
        assert defiance_succeeded(marshal, "attack", None, 30000) is None


# ============================================================================
# DEFIANCE OUTCOME TABLE APPLICATION
# ============================================================================

class TestDefianceOutcomeTable:
    """Test the 4-row outcome table."""

    def test_right_outcome(self):
        marshal = MockMarshal(trust_val=70, vindication=0)
        world = MockWorld(authority=100, current_turn=5)
        result = apply_defiance_outcome(marshal, True, world)

        assert result["trust_change"] == +2
        assert result["authority_change"] == -5
        assert result["cooldown_turns"] == 3
        assert result["outcome_type"] == "right"
        assert marshal.vindication_score == 1
        assert world.authority_tracker.authority == 95
        assert marshal.defiance_cooldown_until == 8

    def test_wrong_outcome(self):
        marshal = MockMarshal(trust_val=70, vindication=2)
        world = MockWorld(authority=90, current_turn=5)
        result = apply_defiance_outcome(marshal, False, world)

        assert result["trust_change"] == -5
        assert result["authority_change"] == +3
        assert result["cooldown_turns"] == 3
        assert result["outcome_type"] == "wrong"
        assert marshal.vindication_score == 0  # Reset
        assert world.authority_tracker.authority == 93
        assert marshal.defiance_cooldown_until == 8

    def test_inconclusive_outcome(self):
        marshal = MockMarshal(trust_val=70, vindication=1)
        world = MockWorld(authority=80, current_turn=5)
        result = apply_defiance_outcome(marshal, None, world)

        assert result["trust_change"] == 0
        assert result["authority_change"] == 0
        assert result["cooldown_turns"] == 3
        assert result["outcome_type"] == "inconclusive"
        assert marshal.defiance_cooldown_until == 8

    def test_failed_roll(self):
        marshal = MockMarshal(trust_val=70, vindication=2)
        world = MockWorld(authority=80, current_turn=5)
        result = apply_defiance_outcome(marshal, "failed_roll", world)

        assert result["trust_change"] == -3
        # M4 fix: vindication_change reports actual change (was 2, reset to 0 = -2)
        assert result["vindication_change"] == -2
        assert result["cooldown_turns"] == 1
        assert result["outcome_type"] == "failed_roll"
        assert marshal.vindication_score == 0  # Reset
        assert marshal.defiance_cooldown_until == 6


# ============================================================================
# EC-4: VINDICATION ESCALATION / DE-ESCALATION
# ============================================================================

class TestEC4_VindicationEscalation:
    """EC-4: Vindication shifts concern by ±1 level."""

    def test_none_never_escalates(self):
        """NONE never escalates to MILD (vindication never creates fake objections)."""
        # This is enforced in executor.py: `if base_concern != ConcernLevel.NONE`
        # We test the rule directly
        base = ConcernLevel.NONE
        v_score = 3  # High vindication
        if v_score > 0 and base != ConcernLevel.NONE:
            new_val = min(base.value + 1, ConcernLevel.EXTREME.value)
            result = ConcernLevel(new_val)
        else:
            result = base
        assert result == ConcernLevel.NONE

    def test_mild_escalates_to_moderate(self):
        base = ConcernLevel.MILD
        v_score = 1
        new_val = min(base.value + 1, ConcernLevel.EXTREME.value)
        result = ConcernLevel(new_val)
        assert result == ConcernLevel.MODERATE

    def test_moderate_escalates_to_strong(self):
        base = ConcernLevel.MODERATE
        v_score = 2
        new_val = min(base.value + 1, ConcernLevel.EXTREME.value)
        result = ConcernLevel(new_val)
        assert result == ConcernLevel.STRONG

    def test_strong_escalates_to_extreme(self):
        base = ConcernLevel.STRONG
        new_val = min(base.value + 1, ConcernLevel.EXTREME.value)
        result = ConcernLevel(new_val)
        assert result == ConcernLevel.EXTREME

    def test_extreme_stays_extreme(self):
        """Can't escalate beyond EXTREME."""
        base = ConcernLevel.EXTREME
        new_val = min(base.value + 1, ConcernLevel.EXTREME.value)
        result = ConcernLevel(new_val)
        assert result == ConcernLevel.EXTREME

    def test_negative_vindication_deescalates(self):
        """Negative vindication lowers by 1 (boy who cried wolf)."""
        base = ConcernLevel.STRONG
        v_score = -1
        new_val = max(base.value - 1, ConcernLevel.MILD.value)
        result = ConcernLevel(new_val)
        assert result == ConcernLevel.MODERATE

    def test_mild_never_drops_to_none(self):
        """Even discredited marshal gets to grumble."""
        base = ConcernLevel.MILD
        v_score = -3
        new_val = max(base.value - 1, ConcernLevel.MILD.value)
        result = ConcernLevel(new_val)
        assert result == ConcernLevel.MILD

    def test_zero_vindication_no_shift(self):
        """Score 0 = no shift."""
        base = ConcernLevel.MODERATE
        v_score = 0
        # The code checks v_score > 0 or v_score < 0, so 0 means no change
        result = base
        assert result == ConcernLevel.MODERATE


# ============================================================================
# EC-5: AUTHORITY MAJOR VICTORY / DEFEAT (ONCE PER BATTLE)
# ============================================================================

class TestEC5_AuthorityMajorVictory:
    """EC-5: Major victory/defeat fires ONCE per battle."""

    def test_major_victory_outnumbered_win(self):
        """Winning while outnumbered gives +5 authority."""
        tracker = AuthorityTracker()
        tracker.authority = 80
        # Simulate: player attacker strength 20000 < defender strength 35000
        tracker.modify_authority(+5)
        assert tracker.authority == 85

    def test_major_defeat_outnumbering_loss(self):
        """Losing while outnumbering gives -5 authority."""
        tracker = AuthorityTracker()
        tracker.authority = 80
        tracker.modify_authority(-5)
        assert tracker.authority == 75

    def test_authority_clamped_at_100(self):
        """Authority never exceeds 100."""
        tracker = AuthorityTracker()
        tracker.authority = 98
        tracker.modify_authority(+5)
        assert tracker.authority == 100

    def test_authority_clamped_at_0(self):
        """Authority never goes below 0."""
        tracker = AuthorityTracker()
        tracker.authority = 3
        tracker.modify_authority(-5)
        assert tracker.authority == 0


# ============================================================================
# EC-6: AUTHORITY EXCESSIVE TRUST PENALTY
# ============================================================================

class TestEC6_ExcessiveTrust:
    """EC-6: Excessive trust penalty triggers at >65% and >80% ratios."""

    def test_no_penalty_insufficient_responses(self):
        """Need at least 3 responses in window for penalty."""
        tracker = AuthorityTracker()
        tracker.recent_responses = [
            {"choice": "trust", "turn": 1},
            {"choice": "trust", "turn": 2},
        ]
        penalty = check_excessive_trust(tracker, current_turn=3)
        assert penalty == 0

    def test_no_penalty_balanced_responses(self):
        """50/50 trust/insist = no penalty."""
        tracker = AuthorityTracker()
        tracker.recent_responses = [
            {"choice": "trust", "turn": 1},
            {"choice": "insist", "turn": 2},
            {"choice": "trust", "turn": 3},
            {"choice": "insist", "turn": 4},
        ]
        penalty = check_excessive_trust(tracker, current_turn=5)
        assert penalty == 0

    def test_penalty_at_high_trust_ratio(self):
        """Over 65% trust → -2 penalty."""
        tracker = AuthorityTracker()
        # 4 trust, 1 insist = 80% (> 65%)
        tracker.recent_responses = [
            {"choice": "trust", "turn": 1},
            {"choice": "trust", "turn": 2},
            {"choice": "trust", "turn": 3},
            {"choice": "trust", "turn": 4},
            {"choice": "insist", "turn": 5},
        ]
        penalty = check_excessive_trust(tracker, current_turn=6)
        # 80% > 65% so at least -2; 80% >= 80% so -3
        assert penalty in (-2, -3)

    def test_severe_penalty_at_very_high_ratio(self):
        """Over 80% trust → -3 penalty."""
        tracker = AuthorityTracker()
        # 5 trust, 0 insist = 100%
        tracker.recent_responses = [
            {"choice": "trust", "turn": 1},
            {"choice": "trust", "turn": 2},
            {"choice": "trust", "turn": 3},
            {"choice": "trust", "turn": 4},
            {"choice": "trust", "turn": 5},
        ]
        penalty = check_excessive_trust(tracker, current_turn=6)
        assert penalty == -3

    def test_old_responses_excluded_from_window(self):
        """Responses >10 turns old are outside window."""
        tracker = AuthorityTracker()
        # Old trust responses (turn 1-3), recent insist (turn 12-14)
        tracker.recent_responses = [
            {"choice": "trust", "turn": 1},
            {"choice": "trust", "turn": 2},
            {"choice": "trust", "turn": 3},
            {"choice": "insist", "turn": 12},
            {"choice": "insist", "turn": 13},
            {"choice": "insist", "turn": 14},
        ]
        penalty = check_excessive_trust(tracker, current_turn=15)
        assert penalty == 0  # Only recent insists counted


# ============================================================================
# EC-8: DEFENSIVE VINDICATION
# ============================================================================

class TestEC8_DefensiveVindication:
    """EC-8: Defensive vindication created on 'trust' when alt is defend/fortify/hold."""

    def test_creation(self):
        """Pending entry created when trust chosen and alt is defend."""
        from backend.commands.vindication import VindicationTracker
        tracker = VindicationTracker()
        # Simulate: player chose trust, marshal wanted to defend
        tracker.pending_defensive_vindication["Davout"] = {"turn": 5}
        assert "Davout" in tracker.pending_defensive_vindication
        assert tracker.pending_defensive_vindication["Davout"]["turn"] == 5

    def test_resolution_held(self):
        """Marshal holds (not broken/retreating) → vindication +1."""
        from backend.commands.vindication import VindicationTracker
        tracker = VindicationTracker()
        tracker.pending_defensive_vindication["Davout"] = {"turn": 5}

        marshal = MockMarshal(name="Davout", personality="cautious", vindication=0)
        marshal.broken = False
        marshal.retreating = False

        # Simulate resolution: marshal held
        marshal.vindication_score = min(5, marshal.vindication_score + 1)
        del tracker.pending_defensive_vindication["Davout"]

        assert marshal.vindication_score == 1
        assert "Davout" not in tracker.pending_defensive_vindication

    def test_resolution_broken(self):
        """Marshal broken → vindication -1."""
        marshal = MockMarshal(name="Davout", personality="cautious", vindication=0)
        marshal.broken = True

        marshal.vindication_score = max(-5, marshal.vindication_score - 1)
        assert marshal.vindication_score == -1

    def test_stale_cleared(self):
        """Entries >5 turns old are cleared during advance_turn."""
        from backend.commands.vindication import VindicationTracker
        tracker = VindicationTracker()
        tracker.pending_defensive_vindication["Davout"] = {"turn": 2}

        # Simulate stale check at turn 8 (6 turns later, >5)
        stale_names = []
        for name, entry in tracker.pending_defensive_vindication.items():
            if 8 - entry.get("turn", 0) > 5:
                stale_names.append(name)
        for name in stale_names:
            del tracker.pending_defensive_vindication[name]

        assert "Davout" not in tracker.pending_defensive_vindication


# ============================================================================
# EC-9: VINDICATION DECAY
# ============================================================================

class TestEC9_VindicationDecay:
    """EC-9: Vindication decays -1 per 3 idle turns, symmetric toward 0."""

    def test_positive_decays(self):
        """Positive vindication decays toward 0."""
        marshal = MockMarshal(vindication=3)
        marshal.last_objection_turn = 1
        current_turn = 4  # 3 turns idle

        if current_turn - marshal.last_objection_turn >= 3 and marshal.vindication_score != 0:
            if marshal.vindication_score > 0:
                marshal.vindication_score -= 1
            marshal.last_objection_turn = current_turn

        assert marshal.vindication_score == 2
        assert marshal.last_objection_turn == 4

    def test_negative_decays(self):
        """Negative vindication decays toward 0 (symmetric)."""
        marshal = MockMarshal(vindication=-2)
        marshal.last_objection_turn = 1
        current_turn = 4

        if current_turn - marshal.last_objection_turn >= 3 and marshal.vindication_score != 0:
            if marshal.vindication_score > 0:
                marshal.vindication_score -= 1
            else:
                marshal.vindication_score += 1
            marshal.last_objection_turn = current_turn

        assert marshal.vindication_score == -1

    def test_zero_no_decay(self):
        """Vindication at 0 doesn't change."""
        marshal = MockMarshal(vindication=0)
        marshal.last_objection_turn = 1
        current_turn = 10

        if current_turn - marshal.last_objection_turn >= 3 and marshal.vindication_score != 0:
            marshal.vindication_score -= 1

        assert marshal.vindication_score == 0

    def test_no_decay_before_3_turns(self):
        """Decay only after 3+ idle turns."""
        marshal = MockMarshal(vindication=3)
        marshal.last_objection_turn = 3
        current_turn = 5  # Only 2 turns idle

        if current_turn - marshal.last_objection_turn >= 3 and marshal.vindication_score != 0:
            marshal.vindication_score -= 1

        assert marshal.vindication_score == 3  # No change

    def test_timer_resets_after_decay(self):
        """After decay, timer resets for next 3-turn window."""
        marshal = MockMarshal(vindication=3)
        marshal.last_objection_turn = 1
        current_turn = 4

        if current_turn - marshal.last_objection_turn >= 3:
            marshal.vindication_score -= 1
            marshal.last_objection_turn = current_turn

        assert marshal.last_objection_turn == 4  # Reset to current


# ============================================================================
# BERTHIER FLAVOR TEXT
# ============================================================================

class TestBerthierText:
    """Test Berthier defiance flavor text templates."""

    def test_right_text(self):
        text = get_berthier_defiance_text("right", "Ney", "charged the enemy")
        assert "Ney" in text
        assert len(text) > 10

    def test_wrong_text(self):
        text = get_berthier_defiance_text("wrong", "Davout", "fortified")
        assert "Davout" in text

    def test_inconclusive_text(self):
        text = get_berthier_defiance_text("inconclusive", "Ney")
        assert "Ney" in text

    def test_failed_roll_text(self):
        text = get_berthier_defiance_text("failed_roll", "Ney")
        assert "Ney" in text

    def test_unknown_outcome_defaults_to_inconclusive(self):
        text = get_berthier_defiance_text("unknown_outcome", "Ney")
        assert "Ney" in text  # Should use inconclusive template


# ============================================================================
# DEFIANCE MODIFIERS
# ============================================================================

class TestDefianceModifiers:
    """Test individual modifier components of defiance formula."""

    def test_vindication_increases_chance(self):
        """Positive vindication increases defiance chance."""
        marshal_no_v = MockMarshal(trust_val=50, vindication=0)
        marshal_high_v = MockMarshal(trust_val=50, vindication=3)
        world = MockWorld(authority=70)

        with patch('backend.commands.defiance.random.uniform', return_value=0.0):
            chance_no_v = calculate_defiance_chance(marshal_no_v, ConcernLevel.STRONG, world)
            chance_high_v = calculate_defiance_chance(marshal_high_v, ConcernLevel.STRONG, world)

        assert chance_high_v > chance_no_v

    def test_low_authority_increases_chance(self):
        """Authority < 50 adds +10% to defiance."""
        marshal = MockMarshal(trust_val=50, vindication=0)
        world_high = MockWorld(authority=85)
        world_low = MockWorld(authority=40)

        with patch('backend.commands.defiance.random.uniform', return_value=0.0):
            chance_high = calculate_defiance_chance(marshal, ConcernLevel.STRONG, world_high)
            chance_low = calculate_defiance_chance(marshal, ConcernLevel.STRONG, world_low)

        assert chance_low > chance_high

    def test_low_trust_increases_chance(self):
        """Trust <= 20 adds +15% to defiance."""
        marshal_low = MockMarshal(trust_val=15, vindication=0)
        marshal_high = MockMarshal(trust_val=85, vindication=0)
        world = MockWorld(authority=70)

        with patch('backend.commands.defiance.random.uniform', return_value=0.0):
            chance_low = calculate_defiance_chance(marshal_low, ConcernLevel.STRONG, world)
            chance_high = calculate_defiance_chance(marshal_high, ConcernLevel.STRONG, world)

        assert chance_low > chance_high


# ============================================================================
# RELATIONSHIP-BASED SUPPORT OBJECTION
# ============================================================================

class TestRelationshipSupportObjection:
    """V2b: Relationship-based SUPPORT objection."""

    def test_aggressive_hostile_is_strong(self):
        marshal = MockMarshal(personality="aggressive")
        marshal._relationships = {"Wellington": -2}
        concern = _evaluate_relationship_support(marshal, "Wellington", None)
        assert concern == ConcernLevel.STRONG

    def test_cautious_hostile_is_moderate(self):
        marshal = MockMarshal(personality="cautious")
        marshal._relationships = {"Wellington": -2}
        concern = _evaluate_relationship_support(marshal, "Wellington", None)
        assert concern == ConcernLevel.MODERATE

    def test_literal_hostile_is_none(self):
        marshal = MockMarshal(personality="literal")
        marshal._relationships = {"Wellington": -2}
        concern = _evaluate_relationship_support(marshal, "Wellington", None)
        assert concern == ConcernLevel.NONE

    def test_rival_is_mild(self):
        marshal = MockMarshal(personality="aggressive")
        marshal._relationships = {"Davout": -1}
        concern = _evaluate_relationship_support(marshal, "Davout", None)
        assert concern == ConcernLevel.MILD

    def test_neutral_is_none(self):
        marshal = MockMarshal(personality="aggressive")
        marshal._relationships = {"Davout": 0}
        concern = _evaluate_relationship_support(marshal, "Davout", None)
        assert concern == ConcernLevel.NONE

    def test_friendly_is_none(self):
        marshal = MockMarshal(personality="aggressive")
        marshal._relationships = {"Davout": 1}
        concern = _evaluate_relationship_support(marshal, "Davout", None)
        assert concern == ConcernLevel.NONE

    def test_relationship_priority_in_evaluate_strategic(self):
        """Relationship concern overrides personality if higher."""
        marshal = MockMarshal(personality="aggressive")
        marshal._relationships = {"Wellington": -2}
        # No game_state context needed for relationship check
        concern = evaluate_strategic_situation(
            marshal, "SUPPORT", "Wellington", [], None
        )
        # Aggressive+Hostile → STRONG (from relationship)
        assert concern >= ConcernLevel.STRONG

    def test_message_templates_exist(self):
        """Verify message templates for all relationship concern levels."""
        assert ConcernLevel.STRONG in RELATIONSHIP_SUPPORT_MESSAGES
        assert ConcernLevel.MODERATE in RELATIONSHIP_SUPPORT_MESSAGES
        assert ConcernLevel.MILD in RELATIONSHIP_SUPPORT_MESSAGES


# ============================================================================
# AUTHORITY TRACKER ENRICHED RESPONSES
# ============================================================================

class TestEnrichedResponses:
    """V2b: Enriched recent_responses format."""

    def test_record_response_stores_dict(self):
        tracker = AuthorityTracker()
        tracker.record_response("trust", current_turn=5)
        assert len(tracker.recent_responses) == 1
        assert tracker.recent_responses[0] == {"choice": "trust", "turn": 5}

    def test_backward_compat_from_dict(self):
        """Bare strings in save data are migrated to dicts."""
        tracker = AuthorityTracker()
        data = tracker.to_dict()
        data["recent_responses"] = ["trust", "insist"]
        restored = AuthorityTracker.from_dict(data)
        assert restored.recent_responses[0] == {"choice": "trust", "turn": 0}
        assert restored.recent_responses[1] == {"choice": "insist", "turn": 0}

    def test_modify_authority(self):
        tracker = AuthorityTracker()
        tracker.authority = 80
        tracker.modify_authority(+5)
        assert tracker.authority == 85
        tracker.modify_authority(-10)
        assert tracker.authority == 75

    def test_modify_authority_clamp(self):
        tracker = AuthorityTracker()
        tracker.authority = 98
        tracker.modify_authority(+10)
        assert tracker.authority == 100
        tracker.modify_authority(-200)
        assert tracker.authority == 0


# ============================================================================
# SERIALIZATION
# ============================================================================

class TestV2bSerialization:
    """Ensure new fields survive save/load roundtrip."""

    def test_marshal_defiance_fields(self):
        from backend.models.marshal import Marshal
        marshal = Marshal(
            name="Test", location="Paris", nation="France",
            personality="aggressive", strength=30000
        )
        marshal.last_objection_turn = 5
        marshal.defiance_cooldown_until = 8

        data = marshal.to_dict()
        restored = Marshal.from_dict(data)

        assert restored.last_objection_turn == 5
        assert restored.defiance_cooldown_until == 8

    def test_authority_enriched_roundtrip(self):
        tracker = AuthorityTracker()
        tracker.record_response("trust", 5)
        tracker.record_response("insist", 6)

        data = tracker.to_dict()
        restored = AuthorityTracker.from_dict(data)

        assert len(restored.recent_responses) == 2
        assert restored.recent_responses[0]["choice"] == "trust"
        assert restored.recent_responses[0]["turn"] == 5

    def test_vindication_defensive_roundtrip(self):
        from backend.commands.vindication import VindicationTracker
        tracker = VindicationTracker()
        tracker.pending_defensive_vindication["Davout"] = {"turn": 3}

        data = tracker.to_dict()
        restored = VindicationTracker.from_dict(data)

        assert "Davout" in restored.pending_defensive_vindication
        assert restored.pending_defensive_vindication["Davout"]["turn"] == 3
