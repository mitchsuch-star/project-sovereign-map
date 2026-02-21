"""
Notification system — EU4-style persistent alerts for important game events.

Notifications are lightweight alerts for events that are easy to miss:
side effects, milestones buried in tables, and consequences the player
didn't directly cause. They persist until the player dismisses them.

NOT for: Morning Dispatch events, Campaign Log entries, Battle Reports,
Enemy Phase Popup battles, or immediate terminal output.
"""

import uuid
from enum import IntEnum
from typing import Dict, List, Optional, Any


class NotificationPriority(IntEnum):
    """Priority levels for notifications. Higher value = more urgent."""
    NORMAL = 0
    HIGH = 1
    CRITICAL = 2


# Notification type constants
STRATEGIC_ORDER_COMPLETE = "strategic_order_complete"
FORCED_RETREAT_ORDER_VOIDED = "forced_retreat_order_voided"
FRIENDLY_FIRE_TRUST = "friendly_fire_trust"
RECKLESS_CAVALRY_ACTION = "reckless_cavalry_action"
COUNTER_PUNCH_EARNED = "counter_punch_earned"
MANPOWER_DEPLETED = "manpower_depleted"
MANPOWER_REPLENISHED = "manpower_replenished"
NATION_ELIMINATED = "nation_eliminated"
BANKRUPTCY_ESCALATION = "bankruptcy_escalation"
DRILL_CANCELLED = "drill_cancelled"


def create_notification(
    notification_type: str,
    priority: NotificationPriority,
    title: str,
    message: str,
    turn_created: int,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Create a notification dict.

    All numeric values are int()-wrapped per CLAUDE.md rule.
    """
    return {
        "id": str(uuid.uuid4()),
        "type": notification_type,
        "priority": int(priority),
        "title": title,
        "message": message,
        "turn_created": int(turn_created),
        "details": details or {},
    }


class NotificationCollector:
    """Collects and manages notifications attached to WorldState.

    Notifications persist across turns until the player dismisses them.
    Serialized with save/load via to_list() / from_list().
    """

    def __init__(self):
        self._pending: List[Dict[str, Any]] = []

    def add(self, notification: Dict[str, Any]) -> None:
        """Add a notification to the pending list."""
        self._pending.append(notification)

    def get_pending(self) -> List[Dict[str, Any]]:
        """Return all pending notifications, sorted by priority (CRITICAL first).

        Within same priority, newest first (highest turn_created).
        """
        return sorted(
            self._pending,
            key=lambda n: (n.get("priority", 0), n.get("turn_created", 0)),
            reverse=True,
        )

    def dismiss(self, notification_id: str) -> bool:
        """Dismiss a notification by ID. Returns True if found and removed."""
        for i, n in enumerate(self._pending):
            if n.get("id") == notification_id:
                self._pending.pop(i)
                return True
        return False

    def dismiss_all(self) -> int:
        """Dismiss all pending notifications. Returns count dismissed."""
        count = len(self._pending)
        self._pending.clear()
        return count

    def has_pending(self) -> bool:
        """Check if there are any pending notifications."""
        return len(self._pending) > 0

    def to_list(self) -> List[Dict[str, Any]]:
        """Serialize for save/load."""
        return [n.copy() for n in self._pending]

    @classmethod
    def from_list(cls, data: List[Dict[str, Any]]) -> 'NotificationCollector':
        """Deserialize from save/load data."""
        collector = cls()
        for item in data:
            collector._pending.append(item.copy())
        return collector
