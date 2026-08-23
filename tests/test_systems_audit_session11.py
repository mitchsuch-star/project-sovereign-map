"""
Systems Audit Session 11: Cleanup, Placeholders, & Documentation.

Tests for:
1. Balanced/Loyal placeholder cleanup
2-4. (Already fixed in Session 4 — AI_DEBUG, dead state, dead code)
5. Bug fix history archival (no test — docs only)
6. Notification cap (50)
7. Serialization test improvements (DiplomaticRepresentative roundtrip)
8. CLAUDE.md AP references (no test — docs only)
9. Tactical prefix extraction (_build_tactical_prefix)
10. Docs updates (no test)
"""

from backend.models.personality import (
    Personality, PERSONALITY_DESCRIPTIONS, PERSONALITY_TRIGGERS,
    get_base_severity, get_personality,
)
from backend.notifications import (
    NotificationCollector, NotificationPriority, NOTIFICATION_CAP,
    create_notification,
)
from backend.game_logic.combat import _build_tactical_prefix
from backend.models.diplomat import DiplomaticRepresentative


# ============================================================================
# 1. Balanced/Loyal Placeholder Cleanup
# ============================================================================

class TestBalancedLoyalCleanup:
    """Verify BALANCED and LOYAL are reserved but have no active content."""

    def test_enum_values_still_exist(self):
        """Enum values preserved for serialization/modding safety."""
        assert Personality.BALANCED.value == "balanced"
        assert Personality.LOYAL.value == "loyal"

    def test_no_personality_descriptions(self):
        """BALANCED and LOYAL should not have description entries."""
        assert Personality.BALANCED not in PERSONALITY_DESCRIPTIONS
        assert Personality.LOYAL not in PERSONALITY_DESCRIPTIONS

    def test_no_personality_triggers(self):
        """BALANCED and LOYAL should not have trigger entries."""
        # They may have an empty dict or be absent entirely
        balanced_triggers = PERSONALITY_TRIGGERS.get(Personality.BALANCED, {})
        loyal_triggers = PERSONALITY_TRIGGERS.get(Personality.LOYAL, {})
        assert len(balanced_triggers) == 0, "BALANCED should have no triggers"
        assert len(loyal_triggers) == 0, "LOYAL should have no triggers"

    def test_get_base_severity_returns_none(self):
        """No trigger should fire for BALANCED or LOYAL."""
        assert get_base_severity(Personality.BALANCED, "certain_death") is None
        assert get_base_severity(Personality.LOYAL, "suicidal_order") is None

    def test_get_personality_fallback(self):
        """Unknown personality string falls back to BALANCED."""
        result = get_personality("unknown_personality_xyz")
        assert result == Personality.BALANCED


# ============================================================================
# 6. Notification Cap
# ============================================================================

class TestNotificationCap:
    """Verify 50-notification cap with auto-dismiss of oldest NORMAL."""

    def test_cap_constant_exists(self):
        assert NOTIFICATION_CAP == 50

    def test_under_cap_no_trimming(self):
        """49 notifications should all be kept."""
        collector = NotificationCollector()
        for i in range(49):
            collector.add(create_notification(
                "test_type", NotificationPriority.NORMAL,
                f"Title {i}", f"Message {i}", turn_created=i,
            ))
        assert len(collector.get_pending()) == 49

    def test_over_cap_trims_oldest_normal(self):
        """Adding 51st notification removes oldest NORMAL."""
        collector = NotificationCollector()
        for i in range(51):
            collector.add(create_notification(
                "test_type", NotificationPriority.NORMAL,
                f"Title {i}", f"Message {i}", turn_created=i,
            ))
        pending = collector.get_pending()
        assert len(pending) == 50
        # Oldest (turn 0) should be gone
        turns = [n["turn_created"] for n in pending]
        assert 0 not in turns

    def test_cap_preserves_critical_over_normal(self):
        """CRITICAL notifications never auto-dismissed even when over cap."""
        collector = NotificationCollector()
        # Add 1 CRITICAL
        collector.add(create_notification(
            "critical_type", NotificationPriority.CRITICAL,
            "Critical!", "Don't dismiss me", turn_created=0,
        ))
        # Fill to 50+ with NORMAL
        for i in range(1, 52):
            collector.add(create_notification(
                "normal_type", NotificationPriority.NORMAL,
                f"Normal {i}", f"Message {i}", turn_created=i,
            ))
        pending = collector.get_pending()
        assert len(pending) == 50
        # The CRITICAL one should survive
        critical_count = sum(1 for n in pending if n["priority"] == int(NotificationPriority.CRITICAL))
        assert critical_count == 1

    def test_cap_no_trim_when_all_high_priority_ARRIVED_TOGETHER(self):
        """A BURST of HIGH crises is still allowed to overflow the cap.

        CONSCIOUSLY FLIPPED, Aug 23, 2026 (UX23-R3, landing record
        `BUG_FIXES.md` §UX23-A). The original body spread `turn_created`
        across 0..54 and asserted 55 — i.e. it pinned "a HIGH row is never
        evicted, at any age", which is the defect: `DOTATION_EROSION` is HIGH
        and stands until the marshal is paid, so once the tray filled with
        HIGH rows the cap stopped working entirely and real news overflowed
        off the rail with nothing evictable to make room.

        The rule the test was reaching for survives and is what is pinned
        here: crises that break TOGETHER are all shown, even past the cap.
        Only a HIGH row the world has since moved on from
        (`HIGH_EVICTION_WINDOW_TURNS`) may be trimmed — pinned from the other
        side in `tests/test_ux23a_reward_where_he_stands.py`.
        """
        from backend.notifications import HIGH_EVICTION_WINDOW_TURNS

        collector = NotificationCollector()
        for i in range(55):
            collector.add(create_notification(
                "high_type", NotificationPriority.HIGH,
                f"High {i}", f"Message {i}", turn_created=7,
            ))
        assert len(collector.get_pending()) == 55

        # ...and the same 55 spread over a long campaign DO trim, because the
        # oldest of them are no longer news.
        aged = NotificationCollector()
        for i in range(55):
            aged.add(create_notification(
                "high_type", NotificationPriority.HIGH,
                f"High {i}", f"Message {i}",
                turn_created=i * HIGH_EVICTION_WINDOW_TURNS,
            ))
        assert len(aged.get_pending()) == 50


# ============================================================================
# 7. Serialization: DiplomaticRepresentative Roundtrip
# ============================================================================

class TestDiplomaticRepresentativeRoundtrip:
    """Ensure DiplomaticRepresentative serializes and deserializes correctly."""

    def test_roundtrip_preserves_all_fields(self):
        diplomat = DiplomaticRepresentative(
            name="Talleyrand",
            nation="France",
            personality="schemer",
            skill=10,
            biography="The devil's diplomat.",
        )
        data = diplomat.to_dict()
        restored = DiplomaticRepresentative.from_dict(data)

        assert restored.name == diplomat.name
        assert restored.nation == diplomat.nation
        assert restored.personality == diplomat.personality
        assert restored.skill == diplomat.skill
        assert restored.biography == diplomat.biography

    def test_from_dict_defaults(self):
        """Minimal dict produces valid diplomat with defaults."""
        minimal = {"name": "Test", "nation": "Prussia"}
        restored = DiplomaticRepresentative.from_dict(minimal)
        assert restored.personality == "loyalist"
        assert restored.skill == 5
        assert restored.biography == ""

    def test_all_fields_in_to_dict(self):
        """Every instance attribute should appear in to_dict output."""
        diplomat = DiplomaticRepresentative(
            name="Test", nation="France", personality="hawk",
            skill=7, biography="Bio",
        )
        data = diplomat.to_dict()
        for attr in vars(diplomat):
            if not attr.startswith('_'):
                assert attr in data, f"Missing from to_dict: {attr}"


# ============================================================================
# 9. Tactical Prefix Extraction
# ============================================================================

class TestTacticalPrefixBuilder:
    """Verify _build_tactical_prefix produces correct output."""

    def _make_mock_marshal(self, name="TestMarshal"):
        class MockMarshal:
            pass
        m = MockMarshal()
        m.name = name
        m._display_combined_arms_atk = 0.0
        m._display_combined_arms_def = 0.0
        m._display_adjacent_atk = 0.0
        return m

    def test_empty_messages_returns_empty(self):
        attacker = self._make_mock_marshal("Ney")
        defender = self._make_mock_marshal("Wellington")
        result = _build_tactical_prefix(attacker, defender)
        assert result == ""

    def test_single_message(self):
        attacker = self._make_mock_marshal("Ney")
        defender = self._make_mock_marshal("Wellington")
        result = _build_tactical_prefix(
            attacker, defender,
            attacker_stance_message="Aggressive stance!"
        )
        assert "Aggressive stance!" in result
        assert result.endswith("\n")

    def test_multiple_messages(self):
        attacker = self._make_mock_marshal("Ney")
        defender = self._make_mock_marshal("Wellington")
        result = _build_tactical_prefix(
            attacker, defender,
            attacker_stance_message="Attack!",
            defender_stance_message="Defend!",
            terrain_defense_message="Hill bonus!",
        )
        assert "Attack!" in result
        assert "Defend!" in result
        assert "Hill bonus!" in result

    def test_combined_arms_messages(self):
        attacker = self._make_mock_marshal("Ney")
        defender = self._make_mock_marshal("Wellington")
        attacker._display_combined_arms_atk = 0.15
        defender._display_combined_arms_def = 0.10
        result = _build_tactical_prefix(attacker, defender)
        assert "+15% attack" in result
        assert "+10% defense" in result

    def test_adjacent_support(self):
        attacker = self._make_mock_marshal("Ney")
        defender = self._make_mock_marshal("Wellington")
        attacker._display_adjacent_atk = 0.08
        result = _build_tactical_prefix(attacker, defender)
        assert "Adjacent allies bolster" in result
        assert "+8%" in result

    def test_glorious_charge(self):
        attacker = self._make_mock_marshal("Murat")
        defender = self._make_mock_marshal("Wellington")
        result = _build_tactical_prefix(
            attacker, defender,
            glorious_charge_message="GLORIOUS CHARGE!"
        )
        assert "GLORIOUS CHARGE!" in result
