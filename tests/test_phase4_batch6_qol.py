"""
Phase 4 Batch 6: Misc QoL Tests

Covers:
- R84: Dismiss TENSION/MURMURS on coalition formation, COALITION_DECLARED on dissolution
- R90: Auto-cancel diplomatic mission when target nation eliminated
- R94: Null-guard int() calls in diplomatic_ledger.py
"""

from backend.models.world_state import WorldState
from backend.notifications import (
    create_notification, NotificationPriority, COALITION_THREAT_TENSION, COALITION_MURMURS, COALITION_DECLARED,
    COALITION_DISSOLVED,
)
from backend.game_logic.coalition import (
    form_coalition, dissolve_coalition,
)
from backend.game_logic.diplomacy import (
    _check_mission_target_eliminated,
)
from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def _make_world(**overrides):
    """Create a WorldState with sensible defaults for testing."""
    world = WorldState()
    world.current_turn = 5
    for k, v in overrides.items():
        setattr(world, k, v)
    return world


def _set_at_war(world, nation_a, nation_b):
    """Set two nations to WAR state."""
    key = "|".join(sorted([nation_a, nation_b]))
    world.diplomatic_states[key] = "WAR"


def _set_relation(world, nation_a, nation_b, value):
    """Set relation between two nations."""
    key = "|".join(sorted([nation_a, nation_b]))
    world.nation_relations[key] = value


# ═══════════════════════════════════════════════════════════════════════════
# R84: COALITION NOTIFICATION DISMISSAL
# ═══════════════════════════════════════════════════════════════════════════

class TestR84CoalitionNotificationDismissal:
    """R84: Dismiss superseded notifications on coalition form/dissolve."""

    def test_tension_dismissed_on_coalition_formation(self):
        """TENSION notification should be dismissed when coalition forms."""
        world = _make_world()

        # Add a TENSION notification
        world.notifications.add(create_notification(
            COALITION_THREAT_TENSION,
            NotificationPriority.HIGH,
            "Diplomatic Tension",
            "Threat level rising.",
            int(world.current_turn),
        ))
        assert any(n["type"] == COALITION_THREAT_TENSION
                    for n in world.notifications.get_pending())

        # Set up qualifying nations at war
        _set_relation(world, "France", "Prussia", -20)
        _set_relation(world, "France", "Austria", -20)
        _set_at_war(world, "France", "Prussia")

        # Form coalition
        result = form_coalition(["Prussia", "Austria"], world)
        assert result.get("success")

        # TENSION should be gone
        assert not any(n["type"] == COALITION_THREAT_TENSION
                       for n in world.notifications.get_pending())

    def test_murmurs_dismissed_on_coalition_formation(self):
        """MURMURS notification should be dismissed when coalition forms."""
        world = _make_world()

        # Add a MURMURS notification
        world.notifications.add(create_notification(
            COALITION_MURMURS,
            NotificationPriority.HIGH,
            "European Courts Concerned",
            "Murmurs in the courts.",
            int(world.current_turn),
        ))
        assert any(n["type"] == COALITION_MURMURS
                    for n in world.notifications.get_pending())

        # Set up qualifying nations
        _set_relation(world, "France", "Prussia", -20)
        _set_relation(world, "France", "Austria", -20)
        _set_at_war(world, "France", "Prussia")

        result = form_coalition(["Prussia", "Austria"], world)
        assert result.get("success")

        # MURMURS should be gone
        assert not any(n["type"] == COALITION_MURMURS
                       for n in world.notifications.get_pending())

    def test_coalition_declared_dismissed_on_dissolution(self):
        """COALITION_DECLARED notification should be dismissed on dissolution."""
        world = _make_world()

        # Set up an active coalition with its notification
        world.active_coalition = {
            "id": "coalition_5",
            "name": "The Austria Coalition",
            "leader": "Austria",
            "members": ["Austria", "Prussia"],
            "formed_turn": 3,
            "strategic_posture": "defensive",
            "posture_last_updated": 3,
        }
        world.notifications.add(create_notification(
            COALITION_DECLARED,
            NotificationPriority.CRITICAL,
            "Coalition Declared!",
            "The Austria Coalition has declared war.",
            3,
        ))
        assert any(n["type"] == COALITION_DECLARED
                    for n in world.notifications.get_pending())

        # Dissolve
        events = dissolve_coalition(world, "low_threat")

        # COALITION_DECLARED should be gone
        assert not any(n["type"] == COALITION_DECLARED
                       for n in world.notifications.get_pending())
        # But COALITION_DISSOLVED should be present
        assert any(n["type"] == COALITION_DISSOLVED
                    for n in world.notifications.get_pending())

    def test_both_tension_and_murmurs_dismissed_on_formation(self):
        """Both TENSION and MURMURS should be dismissed if both present."""
        world = _make_world()

        # Add both notifications
        world.notifications.add(create_notification(
            COALITION_THREAT_TENSION,
            NotificationPriority.HIGH,
            "Tension",
            "Tension desc.",
            4,
        ))
        world.notifications.add(create_notification(
            COALITION_MURMURS,
            NotificationPriority.HIGH,
            "Murmurs",
            "Murmurs desc.",
            4,
        ))
        assert len([n for n in world.notifications.get_pending()
                     if n["type"] in (COALITION_THREAT_TENSION, COALITION_MURMURS)]) == 2

        # Form coalition
        _set_relation(world, "France", "Prussia", -20)
        _set_relation(world, "France", "Austria", -20)
        _set_at_war(world, "France", "Prussia")

        result = form_coalition(["Prussia", "Austria"], world)
        assert result.get("success")

        # Both should be gone
        remaining = [n for n in world.notifications.get_pending()
                     if n["type"] in (COALITION_THREAT_TENSION, COALITION_MURMURS)]
        assert len(remaining) == 0


# ═══════════════════════════════════════════════════════════════════════════
# R90: MISSION AUTO-CANCEL ON NATION ELIMINATION
# ═══════════════════════════════════════════════════════════════════════════

class TestR90MissionAutoCancelElimination:
    """R90: Auto-cancel diplomatic mission when target nation eliminated."""

    def test_mission_cancelled_when_target_has_no_regions_no_marshals(self):
        """Mission should be cancelled if target has 0 regions and 0 marshals."""
        world = _make_world()
        world.active_diplomatic_mission = {
            "type": "COURT_NATION",
            "target": "Saxony",
            "turns_active": 2,
            "paused": False,
            "completed": False,
        }
        world.talleyrand_state = "ON_MISSION"

        # Ensure Saxony has no regions
        for region in world.regions.values():
            if region.controller == "Saxony":
                region.controller = "France"

        # Ensure Saxony has no living marshals
        for m in list(world.marshals.values()):
            if m.nation == "Saxony":
                m.strength = 0

        events = _check_mission_target_eliminated(world)

        assert len(events) == 1
        assert events[0]["type"] == "diplomatic_mission_cancelled"
        assert events[0]["reason"] == "nation_eliminated"
        assert "Saxony" in events[0]["message"]
        assert world.active_diplomatic_mission is None
        assert world.talleyrand_state == "IDLE"

    def test_mission_not_cancelled_when_target_has_regions(self):
        """Mission should NOT be cancelled if target still has regions."""
        world = _make_world()
        world.active_diplomatic_mission = {
            "type": "COURT_NATION",
            "target": "Prussia",
            "turns_active": 1,
            "paused": False,
            "completed": False,
        }
        world.talleyrand_state = "ON_MISSION"

        # Prussia should have regions by default (Berlin, Rhineland)
        has_prussia_regions = any(
            r.controller == "Prussia" for r in world.regions.values()
        )
        assert has_prussia_regions, "Test setup: Prussia should have regions"

        events = _check_mission_target_eliminated(world)

        assert len(events) == 0
        assert world.active_diplomatic_mission is not None
        assert world.talleyrand_state == "ON_MISSION"

    def test_mission_not_cancelled_when_target_has_marshals(self):
        """Mission should NOT be cancelled if target still has living marshals."""
        world = _make_world()
        world.active_diplomatic_mission = {
            "type": "COURT_NATION",
            "target": "Austria",
            "turns_active": 1,
            "paused": False,
            "completed": False,
        }
        world.talleyrand_state = "ON_MISSION"

        # Remove Austria's regions but keep marshals alive
        for region in world.regions.values():
            if region.controller == "Austria":
                region.controller = "France"

        # Verify Austria has living marshals
        has_austria_marshals = any(
            m.nation == "Austria" and m.strength > 0
            for m in world.marshals.values()
        )
        assert has_austria_marshals, "Test setup: Austria should have marshals"

        events = _check_mission_target_eliminated(world)

        assert len(events) == 0
        assert world.active_diplomatic_mission is not None

    def test_no_crash_when_no_active_mission(self):
        """No crash or events when there is no active mission."""
        world = _make_world()
        world.active_diplomatic_mission = None

        events = _check_mission_target_eliminated(world)
        assert len(events) == 0


# ═══════════════════════════════════════════════════════════════════════════
# R94: NULL-GUARD INT() CALLS IN DIPLOMATIC LEDGER
# ═══════════════════════════════════════════════════════════════════════════

class TestR94NullGuardIntCalls:
    """R94: Null values in ledger data don't crash int() calls."""

    def test_ledger_with_none_threat_level(self):
        """Ledger should not crash if threat_level is None."""
        world = _make_world()
        world.threat_level = None

        # Should not raise TypeError
        result = build_diplomatic_ledger(world)
        assert result["balance_of_europe"]["threat_level"] == 0

    def test_ledger_with_none_diplomatic_points(self):
        """Ledger should not crash if diplomatic_points is None."""
        world = _make_world()
        world.diplomatic_points = None
        world.max_diplomatic_points = None

        result = build_diplomatic_ledger(world)
        assert result["talleyrand"]["dp_remaining"] == 0
        assert result["talleyrand"]["dp_max"] == 0

    def test_ledger_with_none_war_exhaustion(self):
        """Ledger should not crash if war_exhaustion entry is None."""
        world = _make_world()
        world.active_coalition = {
            "id": "coalition_5",
            "name": "Test Coalition",
            "leader": "Prussia",
            "members": ["Prussia"],
            "formed_turn": 3,
            "strategic_posture": "defensive",
            "posture_last_updated": 3,
        }
        world.war_exhaustion["Prussia"] = None

        result = build_diplomatic_ledger(world)
        tc = result["balance_of_europe"]
        assert tc["active_coalition"] is not None
        # Should have converted None to 0
        for member in tc["active_coalition"]["members"]:
            if member["nation"] == "Prussia":
                assert member["war_exhaustion"] == 0

    def test_ledger_with_none_mission_turns_active(self):
        """Ledger should not crash if mission turns_active is None."""
        world = _make_world()
        world.active_diplomatic_mission = {
            "type": "COURT_NATION",
            "target": "Prussia",
            "turns_active": None,
            "paused": False,
        }

        result = build_diplomatic_ledger(world)
        mission = result["talleyrand"]["active_mission"]
        assert mission is not None
        assert mission["duration"] == 0

    def test_ledger_with_none_proposal_eta(self):
        """Ledger should not crash if proposal ETA values are None."""
        world = _make_world()
        world.proposal_in_transit = {
            "target": "Prussia",
            "eta": None,
            "delivery_turn": None,
        }

        result = build_diplomatic_ledger(world)
        pit = result["talleyrand"]["proposal_in_transit"]
        assert pit is not None
        assert pit["eta"] == 0

    def test_ledger_with_none_sabotage_turn(self):
        """Ledger should not crash if sabotage turn is None."""
        world = _make_world()
        world.undetected_sabotages = [
            {"target": "Prussia", "type": "altered_terms", "turn": None},
        ]

        result = build_diplomatic_ledger(world)
        warnings = result["talleyrand"]["sabotage_warnings"]
        assert len(warnings) == 1
        assert warnings[0]["turn"] == 0

    def test_ledger_with_none_relation(self):
        """Ledger should not crash if nation_relations value is None."""
        world = _make_world()
        # Set a relation to None explicitly
        key = world._make_diplo_key("France", "Prussia")
        world.nation_relations[key] = None

        result = build_diplomatic_ledger(world)
        # Should not have crashed; relation should be 0
        for nation in result["nations"]:
            if nation["name"] == "Prussia":
                assert nation["relation"] == 0
