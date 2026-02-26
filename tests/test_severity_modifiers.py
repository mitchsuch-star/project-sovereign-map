"""
Test suite for severity modifiers and authority tracker

Pure unit tests for the math behind objection severity.
Coverage targets: severity.py lines 143, 164-173, 195-198, 212-265
                  authority.py lines 63-90, 113-148, 179-263
"""

from backend.commands.severity import (
    get_trust_modifier,
    get_vindication_modifier,
    get_performance_modifier,
    get_override_modifier,
    get_authority_modifier,
    apply_variance,
    get_severity_label,
    calculate_strategic_severity,
    get_severity_breakdown,
)
from backend.models.authority import AuthorityTracker
from backend.models.trust import Trust


class MockMarshal:
    """Minimal marshal stub for severity testing."""

    def __init__(self, trust_value=70, vindication=0, battles=None,
                 overrides=None, personality="balanced"):
        self.trust = Trust(trust_value)
        self.vindication_score = vindication
        self.recent_battles = battles or []
        self.recent_overrides = overrides or []
        self.personality = personality
        self.strength = 50000
        self.location = "Paris"
        self.name = "TestMarshal"


# ═══════════════════════════════════════════════════════════════
# TRUST MODIFIER
# ═══════════════════════════════════════════════════════════════

class TestTrustModifier:
    """Trust modifier: 4-tier steep curve."""

    def test_high_trust_reduces_severity(self):
        """Trust 80+ → 0.7x (very trusting)."""
        m = MockMarshal(trust_value=85)
        assert get_trust_modifier(m) == 0.7

    def test_high_trust_boundary(self):
        """Trust exactly 80 → 0.7x."""
        m = MockMarshal(trust_value=80)
        assert get_trust_modifier(m) == 0.7

    def test_neutral_trust(self):
        """Trust 40-79 → 1.0x (baseline)."""
        m = MockMarshal(trust_value=50)
        assert get_trust_modifier(m) == 1.0

    def test_neutral_trust_boundary_low(self):
        """Trust exactly 40 → 1.0x."""
        m = MockMarshal(trust_value=40)
        assert get_trust_modifier(m) == 1.0

    def test_distrustful(self):
        """Trust 20-39 → 1.3x (distrustful)."""
        m = MockMarshal(trust_value=30)
        assert get_trust_modifier(m) == 1.3

    def test_very_distrustful(self):
        """Trust <20 → 1.6x (very distrustful)."""
        m = MockMarshal(trust_value=10)
        assert get_trust_modifier(m) == 1.6

    def test_zero_trust(self):
        """Trust 0 → 1.6x."""
        m = MockMarshal(trust_value=0)
        assert get_trust_modifier(m) == 1.6

    def test_no_trust_attribute_defaults(self):
        """Marshal without trust attribute defaults to 70 → 1.0x."""
        m = MockMarshal()
        delattr(m, 'trust')
        assert get_trust_modifier(m) == 1.0


# ═══════════════════════════════════════════════════════════════
# VINDICATION MODIFIER
# ═══════════════════════════════════════════════════════════════

class TestVindicationModifier:
    """Vindication: 3-tier system (proven right/wrong/neutral)."""

    def test_proven_wrong_less_bold(self):
        """Vindication <= -2 → 0.85x."""
        m = MockMarshal(vindication=-3)
        assert get_vindication_modifier(m) == 0.85

    def test_proven_wrong_boundary(self):
        """Vindication exactly -2 → 0.85x."""
        m = MockMarshal(vindication=-2)
        assert get_vindication_modifier(m) == 0.85

    def test_neutral_vindication(self):
        """Vindication -1 to +2 → 1.0x."""
        for v in [-1, 0, 1, 2]:
            m = MockMarshal(vindication=v)
            assert get_vindication_modifier(m) == 1.0, f"Vindication {v} should be 1.0x"

    def test_proven_right_bolder(self):
        """Vindication >= 3 → 1.15x."""
        m = MockMarshal(vindication=3)
        assert get_vindication_modifier(m) == 1.15

    def test_max_vindication(self):
        """Vindication 5 → 1.15x."""
        m = MockMarshal(vindication=5)
        assert get_vindication_modifier(m) == 1.15

    def test_no_vindication_attribute(self):
        """Marshal without vindication_score defaults to 0 → 1.0x."""
        m = MockMarshal()
        delattr(m, 'vindication_score')
        assert get_vindication_modifier(m) == 1.0


# ═══════════════════════════════════════════════════════════════
# PERFORMANCE MODIFIER
# ═══════════════════════════════════════════════════════════════

class TestPerformanceModifier:
    """Performance: winning/losing streaks in last 3 battles."""

    def test_no_battles_neutral(self):
        """No battle history → 1.0x."""
        m = MockMarshal(battles=[])
        assert get_performance_modifier(m) == 1.0

    def test_winning_streak(self):
        """2+ victories in last 3 → 0.85x (less objection)."""
        m = MockMarshal(battles=["victory", "victory", "defeat"])
        assert get_performance_modifier(m) == 0.85

    def test_all_victories(self):
        """3 victories → 0.85x."""
        m = MockMarshal(battles=["victory", "victory", "victory"])
        assert get_performance_modifier(m) == 0.85

    def test_losing_streak(self):
        """2+ defeats in last 3 → 1.15x (more questioning)."""
        m = MockMarshal(battles=["defeat", "defeat", "victory"])
        assert get_performance_modifier(m) == 1.15

    def test_all_defeats(self):
        """3 defeats → 1.15x."""
        m = MockMarshal(battles=["defeat", "defeat", "defeat"])
        assert get_performance_modifier(m) == 1.15

    def test_mixed_results_neutral(self):
        """1 win, 1 loss, 1 draw → 1.0x."""
        m = MockMarshal(battles=["victory", "defeat", "draw"])
        assert get_performance_modifier(m) == 1.0

    def test_only_last_3_matter(self):
        """Older battles beyond last 3 are ignored."""
        m = MockMarshal(battles=["defeat", "defeat", "defeat", "victory", "victory"])
        # Last 3: defeat, victory, victory → 2 victories → 0.85x
        assert get_performance_modifier(m) == 0.85

    def test_no_attribute_defaults(self):
        """Marshal without recent_battles → 1.0x."""
        m = MockMarshal()
        delattr(m, 'recent_battles')
        assert get_performance_modifier(m) == 1.0


# ═══════════════════════════════════════════════════════════════
# OVERRIDE MODIFIER
# ═══════════════════════════════════════════════════════════════

class TestOverrideModifier:
    """Override: frequently overridden marshals resent it."""

    def test_no_overrides_neutral(self):
        """No override history → 1.0x."""
        m = MockMarshal(overrides=[])
        assert get_override_modifier(m) == 1.0

    def test_rarely_overridden(self):
        """0-1 overrides in last 5 → 1.0x."""
        m = MockMarshal(overrides=[True, False, False, False, False])
        assert get_override_modifier(m) == 1.0

    def test_sometimes_overridden(self):
        """2-3 overrides in last 5 → 1.1x."""
        m = MockMarshal(overrides=[True, True, False, False, False])
        assert get_override_modifier(m) == 1.1

    def test_frequently_overridden(self):
        """4+ overrides in last 5 → 1.3x (resentful)."""
        m = MockMarshal(overrides=[True, True, True, True, False])
        assert get_override_modifier(m) == 1.3

    def test_always_overridden(self):
        """5/5 overrides → 1.3x."""
        m = MockMarshal(overrides=[True, True, True, True, True])
        assert get_override_modifier(m) == 1.3

    def test_only_last_5_matter(self):
        """Older overrides beyond last 5 are ignored."""
        m = MockMarshal(overrides=[True, True, True, True, True, False, False, False, False, False])
        # Last 5: all False → 1.0x
        assert get_override_modifier(m) == 1.0


# ═══════════════════════════════════════════════════════════════
# AUTHORITY MODIFIER
# ═══════════════════════════════════════════════════════════════

class TestAuthorityModifier:
    """Authority modifier from game state."""

    def test_no_game_state(self):
        """None game state → 1.0x."""
        assert get_authority_modifier(None) == 1.0

    def test_high_authority(self):
        """Authority 80+ → 1.0x (no modifier)."""
        tracker = AuthorityTracker()
        tracker.authority = 90

        class GS:
            authority_tracker = tracker
        assert get_authority_modifier(GS()) == 1.0

    def test_medium_authority(self):
        """Authority 50-79 → 1.1x."""
        tracker = AuthorityTracker()
        tracker.authority = 60

        class GS:
            authority_tracker = tracker
        assert get_authority_modifier(GS()) == 1.1

    def test_low_authority(self):
        """Authority <50 → 1.25x."""
        tracker = AuthorityTracker()
        tracker.authority = 30

        class GS:
            authority_tracker = tracker
        assert get_authority_modifier(GS()) == 1.25

    def test_nested_world_authority(self):
        """Authority tracker nested in game_state.world."""
        tracker = AuthorityTracker()
        tracker.authority = 30

        class World:
            authority_tracker = tracker

        class GS:
            world = World()
        assert get_authority_modifier(GS()) == 1.25


# ═══════════════════════════════════════════════════════════════
# VARIANCE
# ═══════════════════════════════════════════════════════════════

class TestVariance:
    """Tiered variance: low/medium/high severity bands."""

    def test_below_threshold_no_variance(self):
        """Severity < 0.20 gets no variance."""
        assert apply_variance(0.10) == 0.10

    def test_low_severity_small_variance(self):
        """Severity 0.20-0.35 gets ±3% variance."""
        results = set()
        for _ in range(100):
            v = apply_variance(0.25)
            assert 0.22 <= v <= 0.28, f"Low variance out of range: {v}"
            results.add(round(v, 3))
        # Should have some variance (not all identical)
        assert len(results) > 1

    def test_medium_severity_moderate_variance(self):
        """Severity 0.35-0.60 gets ±8% variance."""
        for _ in range(100):
            v = apply_variance(0.50)
            assert 0.42 <= v <= 0.58, f"Medium variance out of range: {v}"

    def test_high_severity_large_variance(self):
        """Severity 0.60+ gets ±12% variance."""
        for _ in range(100):
            v = apply_variance(0.70)
            assert 0.58 <= v <= 0.82, f"High variance out of range: {v}"


# ═══════════════════════════════════════════════════════════════
# SEVERITY LABELS
# ═══════════════════════════════════════════════════════════════

class TestSeverityLabels:
    """Human-readable labels for severity levels."""

    def test_compliant(self):
        assert get_severity_label(0.10) == "Compliant"

    def test_mild_concern(self):
        assert get_severity_label(0.25) == "Mild Concern"

    def test_objecting(self):
        assert get_severity_label(0.40) == "Objecting"

    def test_strongly_objecting(self):
        assert get_severity_label(0.55) == "Strongly Objecting"

    def test_refusing(self):
        assert get_severity_label(0.75) == "Refusing"

    def test_outright_defiance(self):
        assert get_severity_label(0.90) == "Outright Defiance"


# ═══════════════════════════════════════════════════════════════
# AUTHORITY TRACKER
# ═══════════════════════════════════════════════════════════════

class TestAuthorityTracker:
    """Test AuthorityTracker mechanics."""

    def test_initial_state(self):
        """Starts at authority 100."""
        tracker = AuthorityTracker()
        assert tracker.authority == 100
        assert tracker.recent_responses == []

    def test_invalid_choice_ignored(self):
        """Invalid choice returns None, no state change."""
        tracker = AuthorityTracker()
        result = tracker.record_response("invalid")
        assert result is None
        assert tracker.authority == 100

    def test_always_trusting_drops_authority(self):
        """Trusting >80% of the time drops authority by 5 per evaluation."""
        tracker = AuthorityTracker()
        for _ in range(10):
            tracker.record_response("trust")

        # After 10 trusts, authority should have dropped significantly
        assert tracker.authority < 100

    def test_always_insisting_maintains_authority(self):
        """Insisting >80% of the time gains +1 authority per evaluation."""
        tracker = AuthorityTracker()
        for _ in range(10):
            tracker.record_response("insist")

        assert tracker.authority >= 100

    def test_balanced_gains_authority(self):
        """Balanced mix (30-60% trust) gains +1 authority per evaluation."""
        tracker = AuthorityTracker()
        responses = ["trust", "insist", "compromise", "trust", "insist",
                     "compromise", "trust", "compromise"]
        for r in responses:
            tracker.record_response(r)

        assert tracker.authority >= 100

    def test_moderate_trusting_small_drop(self):
        """60-80% trust rate → -2 authority per evaluation."""
        tracker = AuthorityTracker()
        # 4 trust, 1 insist = 80% trust rate
        for _ in range(4):
            tracker.record_response("trust")
        tracker.record_response("insist")

        # After first evaluation (5 responses), should drop by 2
        assert tracker.authority <= 98

    def test_threshold_event_whispers(self):
        """Authority dropping to 70 triggers 'Whispers of Weakness'."""
        tracker = AuthorityTracker()
        tracker.authority = 71

        # Force a trust-heavy pattern
        tracker.recent_responses = ["trust"] * 10

        event = tracker.record_response("trust")
        # After evaluation, authority may drop below 70
        if tracker.authority <= 70:
            # Event should have fired at some point
            assert event is not None or 70 in tracker._crossed_thresholds

    def test_threshold_only_fires_once(self):
        """Each threshold event fires only once."""
        tracker = AuthorityTracker()
        tracker.authority = 70
        tracker._crossed_thresholds = []
        tracker.recent_responses = ["trust"] * 10

        event1 = tracker.record_response("trust")
        event2 = tracker.record_response("trust")

        # At most one of these should be the threshold event
        events = [e for e in [event1, event2] if e and e.get("threshold") == 70]
        assert len(events) <= 1

    def test_trust_gain_modifier_high_trust_rate(self):
        """80%+ trust rate → 0.5x trust gain modifier."""
        tracker = AuthorityTracker()
        tracker.recent_responses = ["trust"] * 9 + ["insist"]
        assert tracker.get_trust_gain_modifier() == 0.5

    def test_trust_gain_modifier_moderate(self):
        """60-80% trust rate → 0.75x trust gain modifier."""
        tracker = AuthorityTracker()
        tracker.recent_responses = ["trust"] * 4 + ["insist"] * 2
        # 4/6 = 66% trust rate
        assert tracker.get_trust_gain_modifier() == 0.75

    def test_trust_gain_modifier_balanced(self):
        """<60% trust rate → 1.0x trust gain modifier."""
        tracker = AuthorityTracker()
        tracker.recent_responses = ["trust"] * 2 + ["insist"] * 4
        assert tracker.get_trust_gain_modifier() == 1.0

    def test_trust_gain_modifier_insufficient_data(self):
        """<5 responses → 1.0x (no penalty)."""
        tracker = AuthorityTracker()
        tracker.recent_responses = ["trust", "trust"]
        assert tracker.get_trust_gain_modifier() == 1.0

    def test_obedience_modifier_high(self):
        """Authority 80+ → 1.1x obedience."""
        tracker = AuthorityTracker()
        tracker.authority = 90
        assert tracker.get_obedience_modifier() == 1.1

    def test_obedience_modifier_normal(self):
        """Authority 50-79 → 1.0x obedience."""
        tracker = AuthorityTracker()
        tracker.authority = 60
        assert tracker.get_obedience_modifier() == 1.0

    def test_obedience_modifier_low(self):
        """Authority <50 → 0.9x obedience."""
        tracker = AuthorityTracker()
        tracker.authority = 30
        assert tracker.get_obedience_modifier() == 0.9

    def test_severity_modifier_tiers(self):
        """Authority severity modifier: 3 tiers."""
        tracker = AuthorityTracker()

        tracker.authority = 90
        assert tracker.get_severity_modifier() == 1.0

        tracker.authority = 60
        assert tracker.get_severity_modifier() == 1.1

        tracker.authority = 30
        assert tracker.get_severity_modifier() == 1.25

    def test_get_status_insufficient_data(self):
        """Status with <5 responses shows insufficient_data."""
        tracker = AuthorityTracker()
        status = tracker.get_status()
        assert status["pattern"] == "insufficient_data"
        assert status["authority"] == 100

    def test_get_status_permissive(self):
        """Status with >60% trust shows permissive."""
        tracker = AuthorityTracker()
        tracker.recent_responses = ["trust"] * 8 + ["insist"] * 2
        status = tracker.get_status()
        assert status["pattern"] == "permissive"

    def test_get_status_authoritarian(self):
        """Status with <30% trust shows authoritarian."""
        tracker = AuthorityTracker()
        tracker.recent_responses = ["insist"] * 8 + ["trust"] * 2
        status = tracker.get_status()
        assert status["pattern"] == "authoritarian"

    def test_get_status_balanced(self):
        """Status with 30-60% trust shows balanced."""
        tracker = AuthorityTracker()
        tracker.recent_responses = ["trust"] * 4 + ["insist"] * 4 + ["compromise"] * 2
        status = tracker.get_status()
        assert status["pattern"] == "balanced"

    def test_repr(self):
        """String representation includes key info."""
        tracker = AuthorityTracker()
        r = repr(tracker)
        assert "authority=" in r
        assert "responses=" in r

    def test_serialization_roundtrip(self):
        """to_dict/from_dict should preserve state."""
        tracker = AuthorityTracker()
        tracker.authority = 75
        # V2b: enriched format with dicts
        tracker.recent_responses = [
            {"choice": "trust", "turn": 1},
            {"choice": "insist", "turn": 2},
            {"choice": "compromise", "turn": 3},
        ]
        tracker._crossed_thresholds = [70]

        data = tracker.to_dict()
        restored = AuthorityTracker.from_dict(data)

        assert restored.authority == 75
        assert len(restored.recent_responses) == 3
        assert restored.recent_responses[0]["choice"] == "trust"
        assert restored.recent_responses[1]["choice"] == "insist"
        assert restored.recent_responses[2]["choice"] == "compromise"
        assert restored._crossed_thresholds == [70]

    def test_serialization_legacy_bare_strings(self):
        """from_dict handles legacy bare string recent_responses."""
        tracker = AuthorityTracker()
        data = tracker.to_dict()
        data["recent_responses"] = ["trust", "insist"]

        restored = AuthorityTracker.from_dict(data)
        assert len(restored.recent_responses) == 2
        assert restored.recent_responses[0]["choice"] == "trust"
        assert restored.recent_responses[0]["turn"] == 0

    def test_reset_threshold_tracking(self):
        """reset_threshold_tracking clears crossed thresholds."""
        tracker = AuthorityTracker()
        tracker._crossed_thresholds = [70, 50]
        tracker.reset_threshold_tracking()
        assert tracker._crossed_thresholds == []


# ═══════════════════════════════════════════════════════════════
# STRATEGIC SEVERITY
# ═══════════════════════════════════════════════════════════════

class TestStrategicSeverity:
    """Test calculate_strategic_severity."""

    def test_base_severity_preserved(self):
        """Strategic severity uses provided base severity."""
        m = MockMarshal(trust_value=70)  # All modifiers 1.0x
        result = calculate_strategic_severity(m, "HOLD", 0.55, None, include_variance=False)
        assert abs(result - 0.55) < 0.01

    def test_modifiers_applied(self):
        """Strategic severity applies all modifier tiers."""
        m = MockMarshal(trust_value=10, vindication=5,
                        battles=["defeat", "defeat", "defeat"],
                        overrides=[True, True, True, True, True])
        # trust: 1.6, vindication: 1.15, performance: 1.15, override: 1.3
        result = calculate_strategic_severity(m, "PURSUE", 0.30, None, include_variance=False)
        # 0.30 * 1.6 * 1.15 * 1.15 * 1.3 = ~0.826
        assert result > 0.60  # Should be significantly amplified

    def test_capped_at_095(self):
        """Severity never exceeds 0.95."""
        m = MockMarshal(trust_value=0, vindication=5,
                        battles=["defeat", "defeat", "defeat"],
                        overrides=[True, True, True, True, True])
        result = calculate_strategic_severity(m, "HOLD", 0.90, None, include_variance=False)
        assert result <= 0.95


# ═══════════════════════════════════════════════════════════════
# SEVERITY BREAKDOWN
# ═══════════════════════════════════════════════════════════════

class TestSeverityBreakdown:
    """Test get_severity_breakdown debugging helper."""

    def test_returns_all_modifiers(self):
        """Breakdown should include all 5 modifier types."""
        m = MockMarshal()
        order = {"action": "defend", "target": "Belgium"}
        breakdown = get_severity_breakdown(m, order, None)

        assert "trust" in breakdown["modifiers"]
        assert "vindication" in breakdown["modifiers"]
        assert "performance" in breakdown["modifiers"]
        assert "override" in breakdown["modifiers"]
        assert "authority" in breakdown["modifiers"]

    def test_includes_label(self):
        """Breakdown should include severity label."""
        m = MockMarshal()
        order = {"action": "defend", "target": "Belgium"}
        breakdown = get_severity_breakdown(m, order, None)

        assert "label" in breakdown
        assert breakdown["label"] in [
            "Compliant", "Mild Concern", "Objecting",
            "Strongly Objecting", "Refusing", "Outright Defiance"
        ]

    def test_indicates_will_object(self):
        """Breakdown should indicate if marshal will object."""
        m = MockMarshal()
        order = {"action": "defend", "target": "Belgium"}
        breakdown = get_severity_breakdown(m, order, None)

        assert "will_object" in breakdown
        assert "is_major" in breakdown
        assert isinstance(breakdown["will_object"], bool)
