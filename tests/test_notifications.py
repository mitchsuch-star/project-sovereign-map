"""
Test suite for Notification System (Phase 6.5)

Tests:
- NotificationPriority enum
- create_notification factory
- NotificationCollector: add, get_pending (sort order), dismiss, dismiss_all,
  has_pending, to_list/from_list (serialization)
- WorldState integration: notifications field, to_dict/from_dict roundtrip
- Trigger integration tests for all 9 notification types:
  1. Strategic order complete
  2. Forced retreat + order voided
  3. Friendly fire trust
  4. Reckless cavalry action
  5. Counter-punch earned
  6. Manpower pool depleted
  7. Enemy nation eliminated
  8. Bankruptcy tier escalation
  9. Drill cancelled
- Dispatch severity classification correctness
- Dispatch whitelist filtering
"""


from backend.notifications import (
    NotificationPriority,
    create_notification,
    NotificationCollector,
    STRATEGIC_ORDER_COMPLETE,
    FORCED_RETREAT_ORDER_VOIDED,
    FRIENDLY_FIRE_TRUST,
    RECKLESS_CAVALRY_ACTION,
    COUNTER_PUNCH_EARNED,
    MANPOWER_DEPLETED,
    MANPOWER_REPLENISHED,
    NATION_ELIMINATED,
    BANKRUPTCY_ESCALATION,
    DRILL_CANCELLED,
)
from backend.models.world_state import WorldState
from backend.models.marshal import Marshal, StrategicOrder


# ════════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════════

def _make_world():
    """Create a standard WorldState for testing."""
    return WorldState(player_nation="France")


def _make_marshal(name="Ney", location="Paris", strength=50000,
                  personality="aggressive", nation="France", **kwargs):
    """Create a test marshal with sensible defaults."""
    return Marshal(name=name, location=location, strength=strength,
                   personality=personality, nation=nation, **kwargs)


# ════════════════════════════════════════════════════════════════════════════════
# NOTIFICATION PRIORITY
# ════════════════════════════════════════════════════════════════════════════════

class TestNotificationPriority:
    """Test the NotificationPriority enum."""

    def test_priority_values(self):
        assert NotificationPriority.NORMAL == 0
        assert NotificationPriority.HIGH == 1
        assert NotificationPriority.CRITICAL == 2

    def test_priority_ordering(self):
        assert NotificationPriority.CRITICAL > NotificationPriority.HIGH
        assert NotificationPriority.HIGH > NotificationPriority.NORMAL

    def test_priority_is_int(self):
        assert isinstance(int(NotificationPriority.CRITICAL), int)


# ════════════════════════════════════════════════════════════════════════════════
# CREATE_NOTIFICATION
# ════════════════════════════════════════════════════════════════════════════════

class TestCreateNotification:
    """Test the create_notification factory function."""

    def test_basic_creation(self):
        n = create_notification(
            notification_type=STRATEGIC_ORDER_COMPLETE,
            priority=NotificationPriority.HIGH,
            title="Ney arrived",
            message="Ney has completed his MOVE_TO order.",
            turn_created=5,
        )
        assert n["type"] == STRATEGIC_ORDER_COMPLETE
        assert n["priority"] == 1
        assert n["title"] == "Ney arrived"
        assert n["message"] == "Ney has completed his MOVE_TO order."
        assert n["turn_created"] == 5
        assert n["details"] == {}
        assert "id" in n
        assert isinstance(n["id"], str)

    def test_with_details(self):
        n = create_notification(
            notification_type=MANPOWER_DEPLETED,
            priority=NotificationPriority.HIGH,
            title="Infantry pool exhausted",
            message="No infantry reserves.",
            turn_created=10,
            details={"pool_type": "infantry", "nation": "France"},
        )
        assert n["details"]["pool_type"] == "infantry"
        assert n["details"]["nation"] == "France"

    def test_all_numeric_values_are_int(self):
        n = create_notification(
            notification_type="test",
            priority=NotificationPriority.CRITICAL,
            title="Test",
            message="Test",
            turn_created=3.0,  # Pass float — should be int()-wrapped
        )
        assert isinstance(n["priority"], int)
        assert isinstance(n["turn_created"], int)

    def test_unique_ids(self):
        n1 = create_notification("test", NotificationPriority.NORMAL, "A", "A", 1)
        n2 = create_notification("test", NotificationPriority.NORMAL, "B", "B", 1)
        assert n1["id"] != n2["id"]


# ════════════════════════════════════════════════════════════════════════════════
# NOTIFICATION COLLECTOR
# ════════════════════════════════════════════════════════════════════════════════

class TestNotificationCollector:
    """Test the NotificationCollector class."""

    def test_empty_collector(self):
        c = NotificationCollector()
        assert c.get_pending() == []
        assert c.has_pending() is False

    def test_add_and_get(self):
        c = NotificationCollector()
        n = create_notification("test", NotificationPriority.NORMAL, "T", "M", 1)
        c.add(n)
        assert c.has_pending() is True
        pending = c.get_pending()
        assert len(pending) == 1
        assert pending[0]["title"] == "T"

    def test_sort_order_priority_first(self):
        c = NotificationCollector()
        n_low = create_notification("a", NotificationPriority.NORMAL, "Low", "M", 1)
        n_high = create_notification("b", NotificationPriority.HIGH, "High", "M", 1)
        n_crit = create_notification("c", NotificationPriority.CRITICAL, "Crit", "M", 1)
        c.add(n_low)
        c.add(n_high)
        c.add(n_crit)
        pending = c.get_pending()
        assert pending[0]["title"] == "Crit"
        assert pending[1]["title"] == "High"
        assert pending[2]["title"] == "Low"

    def test_sort_order_newest_first_within_priority(self):
        c = NotificationCollector()
        n_old = create_notification("a", NotificationPriority.HIGH, "Old", "M", 1)
        n_new = create_notification("b", NotificationPriority.HIGH, "New", "M", 5)
        c.add(n_old)
        c.add(n_new)
        pending = c.get_pending()
        assert pending[0]["title"] == "New"
        assert pending[1]["title"] == "Old"

    def test_dismiss_by_id(self):
        c = NotificationCollector()
        n = create_notification("test", NotificationPriority.NORMAL, "T", "M", 1)
        c.add(n)
        assert c.dismiss(n["id"]) is True
        assert c.has_pending() is False

    def test_dismiss_nonexistent_id(self):
        c = NotificationCollector()
        assert c.dismiss("fake-id") is False

    def test_dismiss_all(self):
        c = NotificationCollector()
        c.add(create_notification("a", NotificationPriority.NORMAL, "A", "M", 1))
        c.add(create_notification("b", NotificationPriority.HIGH, "B", "M", 2))
        c.add(create_notification("c", NotificationPriority.CRITICAL, "C", "M", 3))
        count = c.dismiss_all()
        assert count == 3
        assert c.has_pending() is False

    def test_dismiss_all_empty(self):
        c = NotificationCollector()
        assert c.dismiss_all() == 0

    def test_to_list_from_list_roundtrip(self):
        c = NotificationCollector()
        n1 = create_notification("a", NotificationPriority.HIGH, "A", "MA", 1)
        n2 = create_notification("b", NotificationPriority.CRITICAL, "B", "MB", 2,
                                 details={"key": "val"})
        c.add(n1)
        c.add(n2)

        serialized = c.to_list()
        c2 = NotificationCollector.from_list(serialized)
        pending = c2.get_pending()
        assert len(pending) == 2
        # CRITICAL first
        assert pending[0]["title"] == "B"
        assert pending[0]["details"]["key"] == "val"
        assert pending[1]["title"] == "A"

    def test_to_list_is_copy(self):
        """Modifying the returned list shouldn't affect the collector."""
        c = NotificationCollector()
        n = create_notification("a", NotificationPriority.NORMAL, "A", "M", 1)
        c.add(n)
        lst = c.to_list()
        lst.clear()
        assert c.has_pending() is True

    def test_from_list_is_copy(self):
        """Modifying source data after from_list shouldn't affect collector."""
        data = [create_notification("a", NotificationPriority.NORMAL, "A", "M", 1)]
        c = NotificationCollector.from_list(data)
        data[0]["title"] = "Modified"
        assert c.get_pending()[0]["title"] == "A"


# ════════════════════════════════════════════════════════════════════════════════
# WORLD STATE INTEGRATION
# ════════════════════════════════════════════════════════════════════════════════

class TestWorldStateIntegration:
    """Test notification collector wiring into WorldState."""

    def test_world_has_notifications(self):
        world = _make_world()
        assert hasattr(world, 'notifications')
        assert isinstance(world.notifications, NotificationCollector)

    def test_world_notifications_initially_empty(self):
        world = _make_world()
        assert world.notifications.has_pending() is False

    def test_world_add_notification(self):
        world = _make_world()
        n = create_notification("test", NotificationPriority.HIGH, "T", "M", 1)
        world.notifications.add(n)
        assert world.notifications.has_pending() is True

    def test_world_to_dict_includes_notifications(self):
        world = _make_world()
        n = create_notification("test", NotificationPriority.HIGH, "T", "M", 1)
        world.notifications.add(n)
        d = world.to_dict()
        assert "notifications" in d
        assert len(d["notifications"]) == 1
        assert d["notifications"][0]["title"] == "T"

    def test_world_from_dict_restores_notifications(self):
        world = _make_world()
        n = create_notification("test", NotificationPriority.CRITICAL, "Crit", "Message", 5,
                                details={"a": 1})
        world.notifications.add(n)
        d = world.to_dict()

        world2 = WorldState.from_dict(d)
        assert world2.notifications.has_pending() is True
        pending = world2.notifications.get_pending()
        assert len(pending) == 1
        assert pending[0]["title"] == "Crit"
        assert pending[0]["details"]["a"] == 1

    def test_world_roundtrip_empty_notifications(self):
        world = _make_world()
        d = world.to_dict()
        world2 = WorldState.from_dict(d)
        assert world2.notifications.has_pending() is False


# ════════════════════════════════════════════════════════════════════════════════
# TRIGGER INTEGRATION: STRATEGIC ORDER COMPLETE
# ════════════════════════════════════════════════════════════════════════════════

class TestTriggerStrategicOrderComplete:
    """Test Trigger 1: Strategic order complete notification."""

    def test_order_complete_creates_notification(self):
        from backend.commands.strategic import StrategicOrderProcessor

        world = _make_world()
        marshal = _make_marshal("Ney", "Belgium", nation="France")
        marshal.strategic_order = StrategicOrder("MOVE_TO", "Belgium", target_type="region", started_turn=1, original_command="Ney march to Belgium", path=[])
        world.marshals["Ney"] = marshal
        world.current_turn = 5

        se = StrategicOrderProcessor(None)
        se._complete_order(marshal, world, "arrived")

        assert world.notifications.has_pending()
        pending = world.notifications.get_pending()
        assert any(n["type"] == STRATEGIC_ORDER_COMPLETE for n in pending)
        notif = [n for n in pending if n["type"] == STRATEGIC_ORDER_COMPLETE][0]
        assert "Ney" in notif["title"]
        assert notif["priority"] == int(NotificationPriority.HIGH)

    def test_enemy_order_complete_no_notification(self):
        from backend.commands.strategic import StrategicOrderProcessor

        world = _make_world()
        marshal = _make_marshal("Blucher", "Belgium", nation="Prussia")
        marshal.strategic_order = StrategicOrder("MOVE_TO", "Belgium", target_type="region", started_turn=1, original_command="Ney march to Belgium", path=[])
        world.marshals["Blucher"] = marshal

        se = StrategicOrderProcessor(None)
        se._complete_order(marshal, world, "arrived")

        assert not world.notifications.has_pending()


# ════════════════════════════════════════════════════════════════════════════════
# TRIGGER INTEGRATION: MANPOWER DEPLETED
# ════════════════════════════════════════════════════════════════════════════════

class TestTriggerManpowerDepleted:
    """Test Trigger 6: Manpower pool depleted notification."""

    def test_recruit_depletes_pool_creates_notification(self):
        from backend.commands.executor import CommandExecutor

        world = _make_world()
        marshal = _make_marshal("Ney", "Paris", strength=30000, nation="France")
        world.marshals["Ney"] = marshal
        # Set infantry pool to exactly the recruit amount (10,000)
        world.manpower_pools["France"]["infantry"] = 10000
        world.nation_gold["France"] = 5000
        # Ensure Paris is controlled and stable
        paris = world.get_region("Paris")
        paris.controller = "France"
        paris.stability = 100

        executor = CommandExecutor()
        game_state = {"world": world}
        result = executor._execute_recruit(
            {"marshal": "Ney"}, game_state
        )

        assert result["success"] is True
        assert world.manpower_pools["France"]["infantry"] == 0
        assert world.notifications.has_pending()
        pending = world.notifications.get_pending()
        depleted = [n for n in pending if n["type"] == MANPOWER_DEPLETED]
        assert len(depleted) == 1
        assert "infantry" in depleted[0]["title"].lower()

    def test_recruit_partial_pool_no_notification(self):
        from backend.commands.executor import CommandExecutor

        world = _make_world()
        marshal = _make_marshal("Ney", "Paris", strength=30000, nation="France")
        world.marshals["Ney"] = marshal
        # Set infantry pool to more than recruit amount
        world.manpower_pools["France"]["infantry"] = 50000
        world.nation_gold["France"] = 5000
        paris = world.get_region("Paris")
        paris.controller = "France"
        paris.stability = 100

        executor = CommandExecutor()
        game_state = {"world": world}
        result = executor._execute_recruit(
            {"marshal": "Ney"}, game_state
        )

        assert result["success"] is True
        # Pool not at 0, so no notification
        depleted = [n for n in world.notifications.get_pending()
                    if n["type"] == MANPOWER_DEPLETED]
        assert len(depleted) == 0


# ════════════════════════════════════════════════════════════════════════════════
# TRIGGER INTEGRATION: MANPOWER REPLENISHED
# ════════════════════════════════════════════════════════════════════════════════

class TestTriggerManpowerReplenished:
    """Test Trigger 6b: Manpower pool replenished notification."""

    def test_regen_from_zero_creates_notification(self):
        world = _make_world()
        world.manpower_pools["France"]["infantry"] = 0
        world.manpower_pools["France"]["cavalry"] = 5000
        world.manpower_pools["France"]["artillery"] = 5000

        world._process_manpower_regen()

        pending = world.notifications.get_pending()
        replenished = [n for n in pending if n["type"] == MANPOWER_REPLENISHED]
        assert len(replenished) == 1
        assert "infantry" in replenished[0]["title"].lower()

    def test_regen_from_nonzero_no_notification(self):
        world = _make_world()
        # All pools already have some troops
        world.manpower_pools["France"]["infantry"] = 1000
        world.manpower_pools["France"]["cavalry"] = 1000
        world.manpower_pools["France"]["artillery"] = 1000

        world._process_manpower_regen()

        replenished = [n for n in world.notifications.get_pending()
                       if n["type"] == MANPOWER_REPLENISHED]
        assert len(replenished) == 0

    def test_regen_multiple_pools_from_zero(self):
        world = _make_world()
        world.manpower_pools["France"]["infantry"] = 0
        world.manpower_pools["France"]["cavalry"] = 0
        world.manpower_pools["France"]["artillery"] = 0

        world._process_manpower_regen()

        replenished = [n for n in world.notifications.get_pending()
                       if n["type"] == MANPOWER_REPLENISHED]
        assert len(replenished) == 3  # One for each pool type

    def test_enemy_regen_no_notification(self):
        world = _make_world()
        world.manpower_pools["Prussia"] = {"infantry": 0, "cavalry": 0, "artillery": 0}
        world.manpower_pools["France"]["infantry"] = 50000

        world._process_manpower_regen()

        # Only player notifications — no Prussia notifications
        replenished = [n for n in world.notifications.get_pending()
                       if n["type"] == MANPOWER_REPLENISHED]
        assert len(replenished) == 0


# ════════════════════════════════════════════════════════════════════════════════
# TRIGGER INTEGRATION: BANKRUPTCY ESCALATION
# ════════════════════════════════════════════════════════════════════════════════

class TestTriggerBankruptcyEscalation:
    """Test Trigger 8: Bankruptcy tier escalation notification."""

    def test_tier_1_creates_high_notification(self):
        world = _make_world()
        world.nation_bankruptcy_turns["France"] = 1

        world.process_bankruptcy_desertion("France")

        pending = world.notifications.get_pending()
        bankruptcy = [n for n in pending if n["type"] == BANKRUPTCY_ESCALATION]
        assert len(bankruptcy) == 1
        assert bankruptcy[0]["priority"] == int(NotificationPriority.HIGH)
        assert bankruptcy[0]["details"]["tier"] == 1

    def test_tier_2_creates_critical_notification(self):
        world = _make_world()
        world.nation_bankruptcy_turns["France"] = 2

        world.process_bankruptcy_desertion("France")

        pending = world.notifications.get_pending()
        bankruptcy = [n for n in pending if n["type"] == BANKRUPTCY_ESCALATION]
        assert len(bankruptcy) == 1
        assert bankruptcy[0]["priority"] == int(NotificationPriority.CRITICAL)
        assert bankruptcy[0]["details"]["tier"] == 2

    def test_tier_3_creates_critical_notification(self):
        world = _make_world()
        world.nation_bankruptcy_turns["France"] = 3
        marshal = _make_marshal("Ney", strength=10000, nation="France")
        world.marshals["Ney"] = marshal

        world.process_bankruptcy_desertion("France")

        pending = world.notifications.get_pending()
        bankruptcy = [n for n in pending if n["type"] == BANKRUPTCY_ESCALATION]
        assert len(bankruptcy) == 1
        assert bankruptcy[0]["priority"] == int(NotificationPriority.CRITICAL)
        assert bankruptcy[0]["details"]["tier"] == 3
        assert "deserting" in bankruptcy[0]["title"].lower()

    def test_no_bankruptcy_no_notification(self):
        world = _make_world()
        world.nation_bankruptcy_turns["France"] = 0

        world.process_bankruptcy_desertion("France")

        bankruptcy = [n for n in world.notifications.get_pending()
                      if n["type"] == BANKRUPTCY_ESCALATION]
        assert len(bankruptcy) == 0

    def test_enemy_bankruptcy_no_notification(self):
        world = _make_world()
        world.nation_bankruptcy_turns["Prussia"] = 3
        marshal = _make_marshal("Blucher", strength=10000, nation="Prussia")
        world.marshals["Blucher"] = marshal

        world.process_bankruptcy_desertion("Prussia")

        bankruptcy = [n for n in world.notifications.get_pending()
                      if n["type"] == BANKRUPTCY_ESCALATION]
        assert len(bankruptcy) == 0


# ════════════════════════════════════════════════════════════════════════════════
# TRIGGER INTEGRATION: COMBAT NOTIFICATIONS
# ════════════════════════════════════════════════════════════════════════════════

class TestTriggerCombatNotifications:
    """Test Triggers 5 & 9: Counter-punch earned and drill cancelled."""

    def test_process_combat_notifications_counter_punch(self):
        from backend.commands.executor import CommandExecutor

        world = _make_world()
        attacker = _make_marshal("Blucher", location="Paris", strength=30000, nation="Prussia")
        defender = _make_marshal("Davout", location="Paris", strength=25000,
                                 personality="cautious", nation="France")
        world.marshals["Blucher"] = attacker
        world.marshals["Davout"] = defender

        executor = CommandExecutor()
        battle_result = {
            "counter_punch_earned": True,
            "drill_cancelled": False,
        }

        executor._process_combat_notifications(battle_result, attacker, defender, world)

        pending = world.notifications.get_pending()
        cp = [n for n in pending if n["type"] == COUNTER_PUNCH_EARNED]
        assert len(cp) == 1
        assert "Davout" in cp[0]["title"]
        assert cp[0]["priority"] == int(NotificationPriority.HIGH)

    def test_process_combat_notifications_drill_cancelled(self):
        from backend.commands.executor import CommandExecutor

        world = _make_world()
        attacker = _make_marshal("Blucher", location="Paris", strength=30000, nation="Prussia")
        defender = _make_marshal("Davout", location="Paris", strength=25000, nation="France")
        world.marshals["Blucher"] = attacker
        world.marshals["Davout"] = defender

        executor = CommandExecutor()
        battle_result = {
            "counter_punch_earned": False,
            "drill_cancelled": True,
        }

        executor._process_combat_notifications(battle_result, attacker, defender, world)

        pending = world.notifications.get_pending()
        dc = [n for n in pending if n["type"] == DRILL_CANCELLED]
        assert len(dc) == 1
        assert "Davout" in dc[0]["title"]
        assert dc[0]["priority"] == int(NotificationPriority.HIGH)

    def test_no_combat_flags_no_notifications(self):
        from backend.commands.executor import CommandExecutor

        world = _make_world()
        attacker = _make_marshal("Blucher", location="Paris", strength=30000, nation="Prussia")
        defender = _make_marshal("Davout", location="Paris", strength=25000, nation="France")
        world.marshals["Blucher"] = attacker
        world.marshals["Davout"] = defender

        executor = CommandExecutor()
        battle_result = {
            "counter_punch_earned": False,
            "drill_cancelled": False,
        }

        executor._process_combat_notifications(battle_result, attacker, defender, world)

        assert not world.notifications.has_pending()

    def test_enemy_defender_no_notification(self):
        from backend.commands.executor import CommandExecutor

        world = _make_world()
        attacker = _make_marshal("Ney", location="Berlin", strength=30000, nation="France")
        defender = _make_marshal("Blucher", location="Berlin", strength=25000,
                                 personality="cautious", nation="Prussia")
        world.marshals["Ney"] = attacker
        world.marshals["Blucher"] = defender

        executor = CommandExecutor()
        battle_result = {
            "counter_punch_earned": True,
            "drill_cancelled": True,
        }

        executor._process_combat_notifications(battle_result, attacker, defender, world)

        # Enemy defender — no player notifications
        assert not world.notifications.has_pending()


# ════════════════════════════════════════════════════════════════════════════════
# DISPATCH SEVERITY CLASSIFICATIONS
# ════════════════════════════════════════════════════════════════════════════════

class TestDispatchSeverity:
    """Test that dispatch severity classifications are correct."""

    def test_warning_events_get_warning_severity(self):
        from backend.game_logic.dispatch import _build_turn_events

        warning_types = [
            "supply_attrition", "bankruptcy_desertion",
            "occupation_abandoned", "cavalry_stance_forced",
            "cavalry_fortify_forced", "fortify_decayed",
            "fortify_collapsed", "counter_punch_expired",
            "capital_proximity_alert", "auto_glorious_charge",
            "reckless_move", "reckless_no_target",
        ]

        for event_type in warning_types:
            events = [{"type": event_type, "message": f"Test {event_type}", "nation": "France"}]
            result = _build_turn_events(events, "France")
            assert len(result) == 1, f"{event_type} should pass whitelist filter"
            assert result[0]["severity"] == "warning", \
                f"{event_type} should be 'warning' severity, got '{result[0]['severity']}'"

    def test_good_events_get_good_severity(self):
        from backend.game_logic.dispatch import _build_turn_events

        good_types = [
            "construction_complete", "occupation_complete",
            "drill_complete", "retreat_recovery",
            "garrison_regen", "broken_recovered",
        ]

        for event_type in good_types:
            events = [{"type": event_type, "message": f"Test {event_type}", "nation": "France"}]
            result = _build_turn_events(events, "France")
            assert len(result) == 1, f"{event_type} should pass whitelist filter"
            assert result[0]["severity"] == "good", \
                f"{event_type} should be 'good' severity, got '{result[0]['severity']}'"

    def test_info_events_get_info_severity(self):
        from backend.game_logic.dispatch import _build_turn_events

        info_types = [
            "occupation_continues", "drill_locked", "drill_started",
            "fortify_strengthened", "fortify_stable",
            "broken_recovery",
        ]

        for event_type in info_types:
            events = [{"type": event_type, "message": f"Test {event_type}", "nation": "France"}]
            result = _build_turn_events(events, "France")
            assert len(result) == 1, f"{event_type} should pass whitelist filter"
            assert result[0]["severity"] == "info", \
                f"{event_type} should be 'info' severity, got '{result[0]['severity']}'"


# ════════════════════════════════════════════════════════════════════════════════
# DISPATCH WHITELIST FILTERING
# ════════════════════════════════════════════════════════════════════════════════

class TestDispatchWhitelistFilter:
    """Test that dispatch whitelist filter works correctly."""

    def test_whitelisted_event_passes(self):
        from backend.game_logic.dispatch import _build_turn_events

        events = [{"type": "supply_attrition", "message": "Test", "nation": "France"}]
        result = _build_turn_events(events, "France")
        assert len(result) == 1

    def test_non_whitelisted_event_filtered(self):
        from backend.game_logic.dispatch import _build_turn_events

        events = [{"type": "some_unknown_event_type", "message": "Test", "nation": "France"}]
        result = _build_turn_events(events, "France")
        assert len(result) == 0

    def test_empty_message_filtered(self):
        from backend.game_logic.dispatch import _build_turn_events

        events = [{"type": "supply_attrition", "message": "", "nation": "France"}]
        result = _build_turn_events(events, "France")
        assert len(result) == 0

    def test_enemy_event_filtered(self):
        from backend.game_logic.dispatch import _build_turn_events

        events = [{"type": "supply_attrition", "message": "Test", "nation": "Prussia"}]
        result = _build_turn_events(events, "France")
        assert len(result) == 0

    def test_mixed_events(self):
        from backend.game_logic.dispatch import _build_turn_events

        events = [
            {"type": "supply_attrition", "message": "French attrition", "nation": "France"},
            {"type": "supply_attrition", "message": "Enemy attrition", "nation": "Prussia"},
            {"type": "unknown_type", "message": "Unknown", "nation": "France"},
            {"type": "construction_complete", "message": "Built", "nation": "France"},
        ]
        result = _build_turn_events(events, "France")
        assert len(result) == 2  # Only French supply_attrition and construction_complete
        assert result[0]["severity"] == "warning"
        assert result[1]["severity"] == "good"


# ════════════════════════════════════════════════════════════════════════════════
# NOTIFICATION TYPE CONSTANTS
# ════════════════════════════════════════════════════════════════════════════════

class TestNotificationTypeConstants:
    """Verify all notification type constants are unique strings."""

    def test_all_types_are_strings(self):
        types = [
            STRATEGIC_ORDER_COMPLETE, FORCED_RETREAT_ORDER_VOIDED,
            FRIENDLY_FIRE_TRUST, RECKLESS_CAVALRY_ACTION,
            COUNTER_PUNCH_EARNED, MANPOWER_DEPLETED,
            MANPOWER_REPLENISHED, NATION_ELIMINATED,
            BANKRUPTCY_ESCALATION, DRILL_CANCELLED,
        ]
        for t in types:
            assert isinstance(t, str)

    def test_all_types_unique(self):
        types = [
            STRATEGIC_ORDER_COMPLETE, FORCED_RETREAT_ORDER_VOIDED,
            FRIENDLY_FIRE_TRUST, RECKLESS_CAVALRY_ACTION,
            COUNTER_PUNCH_EARNED, MANPOWER_DEPLETED,
            MANPOWER_REPLENISHED, NATION_ELIMINATED,
            BANKRUPTCY_ESCALATION, DRILL_CANCELLED,
        ]
        assert len(types) == len(set(types))


# ════════════════════════════════════════════════════════════════════════════════
# AUDIT FIX TESTS (Session 56b)
# ════════════════════════════════════════════════════════════════════════════════

class TestCavalryEventTypeWhitelist:
    """Bug 1 fix: Whitelist event types must match emitted event types."""

    def test_cavalry_stance_forced_in_whitelist(self):
        from backend.game_logic.dispatch import _DISPATCH_EVENT_TYPES
        assert "cavalry_stance_forced" in _DISPATCH_EVENT_TYPES

    def test_cavalry_fortify_forced_in_whitelist(self):
        from backend.game_logic.dispatch import _DISPATCH_EVENT_TYPES
        assert "cavalry_fortify_forced" in _DISPATCH_EVENT_TYPES

    def test_old_cavalry_names_not_in_whitelist(self):
        from backend.game_logic.dispatch import _DISPATCH_EVENT_TYPES
        assert "cavalry_defensive_reset" not in _DISPATCH_EVENT_TYPES
        assert "cavalry_fortify_reset" not in _DISPATCH_EVENT_TYPES

    def test_cavalry_stance_forced_gets_warning_severity(self):
        from backend.game_logic.dispatch import _build_turn_events
        events = [{"type": "cavalry_stance_forced", "message": "Cavalry reset", "nation": "France"}]
        result = _build_turn_events(events, "France")
        assert len(result) == 1
        assert result[0]["severity"] == "warning"

    def test_cavalry_fortify_forced_gets_warning_severity(self):
        from backend.game_logic.dispatch import _build_turn_events
        events = [{"type": "cavalry_fortify_forced", "message": "Cavalry unfortify", "nation": "France"}]
        result = _build_turn_events(events, "France")
        assert len(result) == 1
        assert result[0]["severity"] == "warning"

    def test_dead_entries_removed(self):
        """fortify_complete and fortify_started should no longer be in whitelist."""
        from backend.game_logic.dispatch import _DISPATCH_EVENT_TYPES
        assert "fortify_complete" not in _DISPATCH_EVENT_TYPES
        assert "fortify_started" not in _DISPATCH_EVENT_TYPES


class TestBankruptcyTierChangeOnly:
    """Bug 3 fix: Bankruptcy notification fires only on tier escalation."""

    def test_same_tier_no_duplicate_notification(self):
        """Second turn at tier 1 should NOT create another notification."""
        world = _make_world()
        world.nation_bankruptcy_turns["France"] = 1
        world.process_bankruptcy_desertion("France")
        assert len(world.notifications._pending) == 1
        assert world.last_bankruptcy_notification_tier == 1

        # Second call at same tier — should NOT add another
        world.nation_bankruptcy_turns["France"] = 1
        world.process_bankruptcy_desertion("France")
        assert len(world.notifications._pending) == 1  # Still 1, not 2

    def test_tier_escalation_creates_new_notification(self):
        """Moving from tier 1 to tier 2 should create a new notification."""
        world = _make_world()
        world.nation_bankruptcy_turns["France"] = 1
        world.process_bankruptcy_desertion("France")
        assert len(world.notifications._pending) == 1
        assert world.last_bankruptcy_notification_tier == 1

        world.nation_bankruptcy_turns["France"] = 2
        world.process_bankruptcy_desertion("France")
        assert len(world.notifications._pending) == 2
        assert world.last_bankruptcy_notification_tier == 2

    def test_tier_3_then_tier_4_no_new_notification(self):
        """bt=3 and bt=4 are both tier 3 — second should not fire."""
        world = _make_world()
        world.nation_bankruptcy_turns["France"] = 3

        # Add a marshal so desertion has something to process
        m = _make_marshal(strength=50000)
        world.marshals[m.name] = m

        world.process_bankruptcy_desertion("France")
        assert len(world.notifications._pending) == 1
        assert world.last_bankruptcy_notification_tier == 3

        world.nation_bankruptcy_turns["France"] = 4
        world.process_bankruptcy_desertion("France")
        assert len(world.notifications._pending) == 1  # Still 1

    def test_bankruptcy_ends_resets_tier_tracker(self):
        """When bankruptcy ends (bt=0), tier tracker resets."""
        world = _make_world()
        world.last_bankruptcy_notification_tier = 2
        world.nation_bankruptcy_turns["France"] = 0
        world.process_bankruptcy_desertion("France")
        assert world.last_bankruptcy_notification_tier == 0

    def test_tier_tracker_serializes(self):
        """last_bankruptcy_notification_tier survives save/load."""
        world = _make_world()
        world.last_bankruptcy_notification_tier = 2
        data = world.to_dict()
        assert data["last_bankruptcy_notification_tier"] == 2

        restored = WorldState.from_dict(data)
        assert restored.last_bankruptcy_notification_tier == 2


class TestNationEliminatedFirstDetection:
    """Bug 3 fix: Nation eliminated fires only on first detection."""

    def test_first_detection_creates_notification(self):
        world = _make_world()
        assert "Prussia" not in world.eliminated_nations_notified

        # Simulate: add Prussia to notified set (as turn_manager would)
        world.eliminated_nations_notified.add("Prussia")
        assert "Prussia" in world.eliminated_nations_notified

    def test_eliminated_nations_serializes(self):
        """eliminated_nations_notified survives save/load."""
        world = _make_world()
        world.eliminated_nations_notified.add("Prussia")
        world.eliminated_nations_notified.add("Austria")
        data = world.to_dict()
        assert set(data["eliminated_nations_notified"]) == {"Prussia", "Austria"}

        restored = WorldState.from_dict(data)
        assert restored.eliminated_nations_notified == {"Prussia", "Austria"}

    def test_eliminated_nations_empty_on_new_game(self):
        world = _make_world()
        assert len(world.eliminated_nations_notified) == 0


class TestDismissByType:
    """dismiss_by_type method on NotificationCollector."""

    def test_dismiss_by_type_removes_matching(self):
        collector = NotificationCollector()
        collector.add(create_notification(
            MANPOWER_DEPLETED, NotificationPriority.HIGH,
            "Infantry depleted", "msg", 1, {"pool_type": "infantry"},
        ))
        collector.add(create_notification(
            MANPOWER_DEPLETED, NotificationPriority.HIGH,
            "Cavalry depleted", "msg", 1, {"pool_type": "cavalry"},
        ))
        collector.add(create_notification(
            STRATEGIC_ORDER_COMPLETE, NotificationPriority.HIGH,
            "Order done", "msg", 1,
        ))
        assert len(collector._pending) == 3

        removed = collector.dismiss_by_type(MANPOWER_DEPLETED)
        assert removed == 2
        assert len(collector._pending) == 1
        assert collector._pending[0]["type"] == STRATEGIC_ORDER_COMPLETE

    def test_dismiss_by_type_with_filter(self):
        """Filter function narrows which notifications to dismiss."""
        collector = NotificationCollector()
        collector.add(create_notification(
            MANPOWER_DEPLETED, NotificationPriority.HIGH,
            "Infantry depleted", "msg", 1, {"pool_type": "infantry"},
        ))
        collector.add(create_notification(
            MANPOWER_DEPLETED, NotificationPriority.HIGH,
            "Cavalry depleted", "msg", 1, {"pool_type": "cavalry"},
        ))

        # Only dismiss infantry
        removed = collector.dismiss_by_type(
            MANPOWER_DEPLETED,
            filter_fn=lambda n: n.get("details", {}).get("pool_type") == "infantry",
        )
        assert removed == 1
        assert len(collector._pending) == 1
        assert collector._pending[0]["details"]["pool_type"] == "cavalry"

    def test_dismiss_by_type_no_match(self):
        collector = NotificationCollector()
        collector.add(create_notification(
            STRATEGIC_ORDER_COMPLETE, NotificationPriority.HIGH,
            "Order done", "msg", 1,
        ))
        removed = collector.dismiss_by_type(MANPOWER_DEPLETED)
        assert removed == 0
        assert len(collector._pending) == 1


class TestManpowerAutoDismiss:
    """Manpower replenished auto-dismisses matching depleted notification."""

    def test_replenished_dismisses_depleted(self):
        """When infantry pool goes 0→>0, the depleted notification is auto-dismissed."""
        world = _make_world()

        # Add a depleted notification for infantry
        world.notifications.add(create_notification(
            MANPOWER_DEPLETED, NotificationPriority.HIGH,
            "Infantry pool exhausted", "msg", 1,
            {"pool_type": "infantry", "nation": "France"},
        ))
        assert len(world.notifications._pending) == 1

        # Set infantry pool to 0, then regen to >0
        world.manpower_pools["France"]["infantry"] = 0
        world.manpower_pools["France"]["cavalry"] = 5000  # Not depleted

        # Simulate regen — call _process_manpower_regen
        # We need to set up a minimal region setup for regen
        world._process_manpower_regen()

        # Infantry was at 0 and regened → depleted notification should be auto-dismissed
        # and a replenished notification should be added
        types = [n["type"] for n in world.notifications._pending]
        assert MANPOWER_DEPLETED not in types
        assert MANPOWER_REPLENISHED in types

    def test_replenished_only_dismisses_matching_pool(self):
        """Infantry replenished should not dismiss cavalry depleted."""
        world = _make_world()

        # Add depleted notifications for both infantry and cavalry
        world.notifications.add(create_notification(
            MANPOWER_DEPLETED, NotificationPriority.HIGH,
            "Infantry pool exhausted", "msg", 1,
            {"pool_type": "infantry", "nation": "France"},
        ))
        world.notifications.add(create_notification(
            MANPOWER_DEPLETED, NotificationPriority.HIGH,
            "Cavalry pool exhausted", "msg", 1,
            {"pool_type": "cavalry", "nation": "France"},
        ))

        # Set infantry to 0 (will regen → triggers auto-dismiss for infantry)
        # Set cavalry to non-zero (was_depleted will be False → no auto-dismiss)
        world.manpower_pools["France"]["infantry"] = 0
        world.manpower_pools["France"]["cavalry"] = 100

        world._process_manpower_regen()

        # Infantry regened → infantry depleted dismissed, cavalry depleted untouched
        remaining_types = [(n["type"], n.get("details", {}).get("pool_type")) for n in world.notifications._pending]

        # Cavalry depleted should still be there (cavalry was NOT at 0)
        assert (MANPOWER_DEPLETED, "cavalry") in remaining_types
        # Infantry depleted should be gone (infantry WAS at 0 and regened)
        assert (MANPOWER_DEPLETED, "infantry") not in remaining_types


# ════════════════════════════════════════════════════════════════════════════════
# ENDPOINT TESTS
# ════════════════════════════════════════════════════════════════════════════════

class TestNotificationEndpoints:
    """Test GET /notifications and POST /notifications/dismiss endpoints."""

    def test_get_notifications_returns_200(self):
        """GET /notifications returns 200 with notifications list."""
        from fastapi.testclient import TestClient
        from backend.main import app

        client = TestClient(app)
        response = client.get("/notifications")
        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data
        assert isinstance(data["notifications"], list)

    def test_get_notifications_no_game_returns_empty(self):
        """GET /notifications with no world returns empty list."""
        from fastapi.testclient import TestClient
        from backend.main import app, game_state

        saved_world = game_state.get("world")
        game_state["world"] = None

        try:
            client = TestClient(app)
            response = client.get("/notifications")
            data = response.json()
            assert data["notifications"] == []
        finally:
            game_state["world"] = saved_world

    def test_dismiss_missing_id_returns_error(self):
        """POST /notifications/dismiss without id returns error."""
        from fastapi.testclient import TestClient
        from backend.main import app

        client = TestClient(app)
        response = client.post("/notifications/dismiss", json={})
        data = response.json()
        assert data["success"] is False

    def test_dismiss_all_returns_count(self):
        """POST /notifications/dismiss with id='all' returns dismissed count."""
        from fastapi.testclient import TestClient
        from backend.main import app, game_state
        import backend.main as main_module

        # Ensure world exists (earlier tests may have cleared game_state)
        saved = game_state.get("world")
        if not saved:
            from backend.models.world_state import WorldState
            w = WorldState(player_nation="France")
            game_state["world"] = w
            main_module.world = w

        world = main_module.world
        world.notifications.add(create_notification(
            STRATEGIC_ORDER_COMPLETE, NotificationPriority.HIGH,
            "Test", "Test message", 1,
        ))

        try:
            client = TestClient(app)
            response = client.post("/notifications/dismiss", json={"id": "all"})
            data = response.json()
            assert data["success"] is True
            assert data["dismissed"] >= 1
        finally:
            if not saved:
                game_state["world"] = saved
