"""
R8 — Campaign Log Enforcement Tests (Architecture Refactoring Session 6)

Prevents the silent-drop bug pattern:
- Every event type logged via log_event() must be in CAMPAIGN_LOG_TYPES
- Every whitelisted type must have a format handler in format_event_oneliner()
- Every whitelisted type must have a category in CATEGORY_MAP
"""
import os
import re

import pytest

from backend.campaign_log import CAMPAIGN_LOG_TYPES, CATEGORY_MAP, format_event_oneliner


# ============================================================================
# Helpers — extract all event type strings from backend source
# ============================================================================

def _find_logged_event_types():
    """Scan all backend .py files for log_event() calls and extract type strings.

    Matches patterns like:
        log_event({"type": "some_type", ...})
        log_event({ "type": "some_type", ...})
        world.log_event({"type": "some_type"...})
    """
    backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
    backend_dir = os.path.normpath(backend_dir)

    # Match: log_event({...  "type": "value"  or  'type': 'value'
    type_pattern = re.compile(
        r'log_event\s*\(\s*\{[^}]*["\']type["\']\s*:\s*["\']([a-z_]+)["\']',
        re.DOTALL,
    )

    logged_types = set()
    for root, _dirs, files in os.walk(backend_dir):
        for fname in files:
            if not fname.endswith('.py'):
                continue
            filepath = os.path.join(root, fname)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            for match in type_pattern.finditer(content):
                logged_types.add(match.group(1))

    return logged_types


# ============================================================================
# Tests
# ============================================================================

class TestAllEventTypesWhitelisted:
    """Every event type used in log_event() must be in CAMPAIGN_LOG_TYPES."""

    def test_no_silent_drops(self):
        """log_event() types not in CAMPAIGN_LOG_TYPES are silently dropped —
        invisible to players. This test prevents that."""
        logged_types = _find_logged_event_types()
        assert logged_types, "Should find at least some log_event() calls"

        missing = logged_types - CAMPAIGN_LOG_TYPES
        if missing:
            pytest.fail(
                f"Event type(s) logged but NOT in CAMPAIGN_LOG_TYPES "
                f"(invisible to players): {sorted(missing)}"
            )

    def test_minimum_event_types_found(self):
        """Sanity check: we should find a reasonable number of event types."""
        logged_types = _find_logged_event_types()
        # We know there are 40+ unique types; if we find fewer than 30,
        # the regex might be broken
        assert len(logged_types) >= 30, (
            f"Only found {len(logged_types)} event types — regex may be broken. "
            f"Found: {sorted(logged_types)}"
        )


class TestAllWhitelistedTypesHaveFormatStrings:
    """Every whitelisted type must have a handler in format_event_oneliner()."""

    @pytest.mark.parametrize("event_type", sorted(CAMPAIGN_LOG_TYPES))
    def test_format_handler_exists(self, event_type):
        """Passing a minimal event dict should NOT produce the fallback
        'Event: {type}' string — that means no handler exists."""
        event = {"type": event_type}
        result = format_event_oneliner(event)
        assert not result.startswith("Event: "), (
            f"Event type '{event_type}' has no format handler in "
            f"format_event_oneliner() — got fallback: '{result}'"
        )


class TestAllWhitelistedTypesHaveCategories:
    """Every whitelisted type must have a category in CATEGORY_MAP."""

    @pytest.mark.parametrize("event_type", sorted(CAMPAIGN_LOG_TYPES))
    def test_category_exists(self, event_type):
        """Missing category means the event can't be filtered by category."""
        assert event_type in CATEGORY_MAP, (
            f"Event type '{event_type}' is in CAMPAIGN_LOG_TYPES but has "
            f"no category in CATEGORY_MAP"
        )


class TestNoDuplicateSemantics:
    """Flag event types that might represent the same game event."""

    KNOWN_OVERLAPS = {
        # diplomatic_war_declared is used for dispatch events;
        # war_declaration is the actual log_event type.
        # Both kept for backward compatibility.
        ("diplomatic_war_declared", "war_declaration"),
    }

    def test_war_declaration_types_documented(self):
        """Both war declaration types should exist and be documented as known overlap."""
        assert "diplomatic_war_declared" in CAMPAIGN_LOG_TYPES
        assert "war_declaration" in CAMPAIGN_LOG_TYPES
        # Verify both have format handlers
        for t in ("diplomatic_war_declared", "war_declaration"):
            result = format_event_oneliner({"type": t})
            assert not result.startswith("Event: "), f"No handler for {t}"


class TestDisplayNameRegistryCompleteness:
    """R7 — Verify display name maps cover all known values."""

    def test_action_display_covers_all_actions(self):
        """Every action in objection/defiance maps should also be in action display."""
        from backend.display_names import ACTION_DISPLAY, OBJECTION_DISPLAY, DEFIANCE_DISPLAY
        for action in OBJECTION_DISPLAY:
            assert action in ACTION_DISPLAY or action == "bombardment", (
                f"Action '{action}' in OBJECTION_DISPLAY but missing from ACTION_DISPLAY"
            )
        for action in DEFIANCE_DISPLAY:
            assert action in ACTION_DISPLAY or action == "bombardment", (
                f"Action '{action}' in DEFIANCE_DISPLAY but missing from ACTION_DISPLAY"
            )

    def test_objection_and_defiance_maps_aligned(self):
        """Both maps should cover the same set of actions."""
        from backend.display_names import OBJECTION_DISPLAY, DEFIANCE_DISPLAY
        assert set(OBJECTION_DISPLAY.keys()) == set(DEFIANCE_DISPLAY.keys()), (
            f"Mismatch: OBJECTION has {set(OBJECTION_DISPLAY) - set(DEFIANCE_DISPLAY)}, "
            f"DEFIANCE has {set(DEFIANCE_DISPLAY) - set(OBJECTION_DISPLAY)}"
        )

    def test_state_display_maps_aligned(self):
        """STATE_DISPLAY and STATE_NARRATIVE_DISPLAY should cover the same states."""
        from backend.display_names import STATE_DISPLAY, STATE_NARRATIVE_DISPLAY
        assert set(STATE_DISPLAY.keys()) == set(STATE_NARRATIVE_DISPLAY.keys()), (
            f"Mismatch: STATE has {set(STATE_DISPLAY) - set(STATE_NARRATIVE_DISPLAY)}, "
            f"NARRATIVE has {set(STATE_NARRATIVE_DISPLAY) - set(STATE_DISPLAY)}"
        )

    def test_display_function_never_returns_raw(self):
        """The display() function should always translate or format gracefully."""
        from backend.display_names import display
        # Known values
        assert display("action", "attack") == "attacks"
        assert display("state", "WAR") == "At War"
        assert display("personality", "aggressive") == "Aggressive"
        # Unknown values get title-cased
        assert display("action", "unknown_action") == "Unknown Action"
        # Fallback override
        assert display("action", "unknown_action", "Custom") == "Custom"

    def test_all_personality_types_have_display(self):
        """All personality types from the enum should have display names."""
        from backend.display_names import PERSONALITY_DISPLAY
        from backend.models.personality import Personality
        for p in Personality:
            assert p.value in PERSONALITY_DISPLAY, (
                f"Personality '{p.value}' missing from PERSONALITY_DISPLAY"
            )

    def test_all_stances_have_display(self):
        """All stance types should have display names."""
        from backend.display_names import STANCE_DISPLAY
        from backend.models.marshal import Stance
        for s in Stance:
            assert s.value in STANCE_DISPLAY, (
                f"Stance '{s.value}' missing from STANCE_DISPLAY"
            )
