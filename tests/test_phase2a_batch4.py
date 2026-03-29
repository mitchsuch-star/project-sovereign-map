"""Phase 2A Batch 4 tests: Dispatch Events + Templates.

R80: Auto-downgrade fires dispatch event + notification
R82: rejection_reaction template slot resolved
R83: Coalition dispatch templates
R51: Void pending dialogue when target joins coalition
"""
from backend.models.world_state import WorldState
from backend.game_logic.diplomacy import check_auto_downgrade
from backend.game_logic.diplomatic_templates import resolve_template_text
from backend.game_logic.dispatch import _DIPLOMATIC_EVENT_TEMPLATES


def make_world():
    return WorldState()


# ═══════════════════════════════════════════════════════
# R80: Auto-downgrade dispatch event + notification
# ═══════════════════════════════════════════════════════

class TestAutoDowngradeEvents:
    """R80: Auto-downgrade fires queue_dispatch_event + notification."""

    def test_dispatch_event_on_auto_downgrade(self):
        world = make_world()
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "ALLIANCE"
        world.nation_relations[key] = -50  # Well below 40 threshold, gap = 90
        world.turns_below_threshold[key] = 4  # Will trigger on 5th
        events_before = len(world.pending_dispatch_events)
        check_auto_downgrade(world)
        assert len(world.pending_dispatch_events) > events_before
        event = world.pending_dispatch_events[-1]
        assert event["type"] == "diplomatic_auto_downgrade"

    def test_notification_on_auto_downgrade(self):
        world = make_world()
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "ALLIANCE"
        world.nation_relations[key] = -50
        world.turns_below_threshold[key] = 4
        notifs_before = len(world.notifications.get_pending())
        check_auto_downgrade(world)
        assert len(world.notifications.get_pending()) > notifs_before


# ═══════════════════════════════════════════════════════
# R82: rejection_reaction template slot
# ═══════════════════════════════════════════════════════

class TestRejectionReaction:
    """R82: {rejection_reaction} resolved based on relation."""

    def test_cold_fury_when_hostile(self):
        world = make_world()
        key = world._make_diplo_key("France", "Prussia")
        world.nation_relations[key] = -60
        text = resolve_template_text("{rejection_reaction}", world, target_nation="Prussia")
        assert text == "cold fury"

    def test_displeasure_when_moderately_hostile(self):
        world = make_world()
        key = world._make_diplo_key("France", "Austria")
        world.nation_relations[key] = -20
        text = resolve_template_text("{rejection_reaction}", world, target_nation="Austria")
        assert text == "barely concealed displeasure"

    def test_composure_when_positive(self):
        world = make_world()
        key = world._make_diplo_key("France", "Austria")
        world.nation_relations[key] = 20
        text = resolve_template_text("{rejection_reaction}", world, target_nation="Austria")
        assert text == "diplomatic composure"

    def test_composure_at_zero(self):
        world = make_world()
        key = world._make_diplo_key("France", "Austria")
        world.nation_relations[key] = 0
        text = resolve_template_text("{rejection_reaction}", world, target_nation="Austria")
        assert text == "diplomatic composure"


# ═══════════════════════════════════════════════════════
# R83: Coalition dispatch templates
# ═══════════════════════════════════════════════════════

class TestCoalitionDispatchTemplates:
    """R83: Coalition events have dispatch templates."""

    def test_coalition_formed_template_exists(self):
        assert "diplomatic_coalition_formed" in _DIPLOMATIC_EVENT_TEMPLATES

    def test_coalition_dissolved_template_exists(self):
        assert "diplomatic_coalition_dissolved" in _DIPLOMATIC_EVENT_TEMPLATES

    def test_coalition_brewing_template_exists(self):
        assert "diplomatic_coalition_brewing" in _DIPLOMATIC_EVENT_TEMPLATES

    def test_coalition_formed_dispatched(self):
        """form_coalition should queue a dispatch event."""
        from backend.game_logic.coalition import form_coalition
        world = make_world()
        events_before = len(world.pending_dispatch_events)
        form_coalition(["Austria"], world)
        found = any(
            e["type"] == "diplomatic_coalition_formed"
            for e in world.pending_dispatch_events[events_before:]
        )
        assert found

    def test_coalition_dissolved_dispatched(self):
        """dissolve_coalition should queue a dispatch event."""
        from backend.game_logic.coalition import form_coalition, dissolve_coalition
        world = make_world()
        form_coalition(["Austria"], world)
        events_before = len(world.pending_dispatch_events)
        dissolve_coalition(world, "test")
        found = any(
            e["type"] == "diplomatic_coalition_dissolved"
            for e in world.pending_dispatch_events[events_before:]
        )
        assert found


# ═══════════════════════════════════════════════════════
# R51: Void dialogue when target joins coalition
# ═══════════════════════════════════════════════════════

class TestVoidDialogueOnCoalition:
    """R51: pending_diplomatic_dialogue voided if target is coalition member."""

    def test_dialogue_voided(self):
        from backend.game_logic.coalition import form_coalition
        world = make_world()
        world.dialogue_manager.replace({
            "type": "proposal",
            "target_nation": "Austria",
            "blocking": True,
        })
        form_coalition(["Austria"], world)
        assert world.pending_diplomatic_dialogue is None

    def test_unrelated_dialogue_kept(self):
        from backend.game_logic.coalition import form_coalition
        world = make_world()
        world.dialogue_manager.replace({
            "type": "proposal",
            "target_nation": "Saxony",
            "blocking": True,
        })
        form_coalition(["Austria"], world)
        # Saxony is not a coalition member, dialogue should be kept
        assert world.pending_diplomatic_dialogue is not None
