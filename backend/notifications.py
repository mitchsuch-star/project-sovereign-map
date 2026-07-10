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
MARSHAL_DEFIED_ORDER = "marshal_defied_order"  # V2b: HIGH priority
# Vassal System notifications (Phase 8 Session 5)
VASSAL_REBELLION = "vassal_rebellion"              # CRITICAL: vassal rebelled
VASSAL_LOYALTY_CRITICAL = "vassal_loyalty_critical"  # HIGH: loyalty < 10
# Coalition System notifications (Phase 8 Session 7)
COALITION_THREAT_TENSION = "coalition_threat_tension"      # HIGH: threat reached 30+
COALITION_MURMURS = "coalition_murmurs"                    # HIGH: threat reached 40+
COALITION_BREWING = "coalition_brewing"                    # CRITICAL: brewing started (60+)
COALITION_DECLARED = "coalition_declared"                  # CRITICAL: coalition war declared
COALITION_MEMBER_PEACED = "coalition_member_peaced"        # NORMAL: member signed peace
COALITION_DISSOLVED = "coalition_dissolved"                # NORMAL: coalition dissolved
COALITION_COOLDOWN_ENDED = "coalition_cooldown_ended"      # NORMAL: new coalition can form
# B-Hegemony (v2.4.3 §7.3): balance-of-power band-crossing beat.
# Fires at 33 / 50 / 60 upward crossings AND same-band hegemon swaps.
# Priority is band-sensitive and presentation metadata is supplied by the
# shared commitments routing table.
BALANCE_OF_EUROPE_SHIFTED = "balance_of_europe_shifted"    # NORMAL/CRITICAL
CALL_TO_ARMS_REFUSED_OFFENSIVE = "call_to_arms_refused_offensive"  # CRITICAL
CALL_TO_ARMS_REFUSED_DEFENSIVE = "call_to_arms_refused_defensive"  # CRITICAL
CALL_TO_ARMS_HONORED_COSTLY = "call_to_arms_honored_costly"        # CRITICAL
# Diplomatic notifications (Phase 8 Session 8C)
DIPLOMATIC_PROPOSAL = "diplomatic_proposal"                    # HIGH: AI envoy arrived
TREATY_SIGNED = "treaty_signed"                                # MEDIUM: treaty ratified
TREATY_BROKEN = "treaty_broken"                                # HIGH: treaty broken
SABOTAGE_DISCOVERED = "sabotage_discovered"                    # HIGH: Talleyrand altered proposal
VASSAL_REBELLION_IMMINENT = "vassal_rebellion_imminent"         # HIGH: loyalty critical
ALLIANCE_CASCADE_WAR = "alliance_cascade_war"                  # HIGH: nation entered war via alliance
WAR_DECLARED = "war_declared"                                  # HIGH: nation declared war
VASSAL_COURTING_DETECTED = "vassal_courting_detected"          # MEDIUM: enemy courting vassal
DP_INSUFFICIENT = "dp_insufficient"                            # MEDIUM: not enough DP
DEFECTION_CASCADE = "defection_cascade"                        # HIGH: multiple vassals wavering
DIPLO_AUTO_DOWNGRADE = "diplo_auto_downgrade"                  # NORMAL: relations deteriorated
TURN_LIMIT_WARNING = "turn_limit_warning"                      # HIGH: campaign nearing end
DEFEAT_IMMINENT_WARNING = "defeat_imminent_warning"            # HIGH/CRITICAL: one marshal/region from defeat
DIPLOMATIC_PROPOSAL_RESULT = "diplomatic_proposal_result"     # NORMAL: player proposal resolved
# Memory and Pressure v2.4.3 — Make Amends repair gesture surface.
# Priority, icon, review routing, and committed copy are supplied by the
# shared commitments routing table.
AMENDS_OFFERED = "amends_offered"
# WB-D: War Bargain presentation extension.
# Priority, icon, review routing supplied by commitments routing table.
BARGAIN_FULFILLED = "bargain_fulfilled"          # HIGH: bargain honoured
BARGAIN_BREACHED = "bargain_breached"            # CRITICAL: bargain broken
BARGAIN_VOIDED = "bargain_voided"                # NORMAL: bargain lapsed
# SC-5 reversal commit 2 / Slice G1: incoming AI settlement offer
# arrival. The producer enforces cooldown + one-active-offer-per-war
# guards so the rail cannot spam; priority is HIGH because settlement
# offers touch entire wars and persist across turns until accept /
# reject. Review target routes to the incoming-settlement-offer popup.
INCOMING_SETTLEMENT_OFFER = "incoming_settlement_offer"
# SC-30 / Slice G1: the Request Terms lifecycle's resolution notice —
# a court refused to name terms, or the request lapsed with the war.
# (A GRANTED request produces a real incoming offer, which notifies
# through INCOMING_SETTLEMENT_OFFER above.)
SETTLEMENT_TERMS_REQUEST_RESULT = "settlement_terms_request_result"
# G2-Slice-G2b: advisory allied-court petition about settlement scope.
# It is mailbox-eligible and notification-visible, but never blocks the
# player's own settlement ratification.
ALLY_SETTLEMENT_PETITION = "ally_settlement_petition"
# ES-7 (Economy Revisit S7): dotation legibility beats. DOTATION_EROSION
# fires on a marshal's FIRST eroding turn (grace window elapsed with the
# expectation still unmet); ESTATE_LOST fires when an endowed province
# leaves the nation's hands (peace cede, recapture, rebellion, vassal grab).
DOTATION_EROSION = "dotation_erosion"                # HIGH: loyalty fraying
ESTATE_LOST = "estate_lost"                          # HIGH: estate pruned
# W6-8 (Spoils of War): an enemy conqueror CONFISCATED a player marshal's
# estate outright — fired at confiscation time because the region leaves the
# marshal's rolls immediately, so the prune's ESTATE_LOST never sees it.
ESTATE_CONFISCATED = "estate_confiscated"            # HIGH: estate seized


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


NOTIFICATION_CAP = 50  # Max notifications before auto-dismissing oldest NORMAL


class NotificationCollector:
    """Collects and manages notifications attached to WorldState.

    Notifications persist across turns until the player dismisses them.
    Serialized with save/load via to_list() / from_list().
    Auto-dismisses oldest NORMAL notifications when cap (50) is exceeded.
    """

    def __init__(self):
        self._pending: List[Dict[str, Any]] = []

    def add(self, notification: Dict[str, Any]) -> None:
        """Add a notification to the pending list. Auto-trims oldest NORMAL if over cap."""
        self._pending.append(notification)
        self._enforce_cap()

    def _enforce_cap(self) -> None:
        """Remove oldest NORMAL notifications if over NOTIFICATION_CAP."""
        while len(self._pending) > NOTIFICATION_CAP:
            # Find oldest NORMAL notification (lowest turn_created, NORMAL priority)
            oldest_normal_idx = None
            oldest_turn = float('inf')
            for i, n in enumerate(self._pending):
                if n.get("priority", 0) == int(NotificationPriority.NORMAL):
                    turn = n.get("turn_created", 0)
                    if turn < oldest_turn:
                        oldest_turn = turn
                        oldest_normal_idx = i
            if oldest_normal_idx is not None:
                self._pending.pop(oldest_normal_idx)
            else:
                # No NORMAL notifications to trim — allow overflow
                break

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

    def dismiss_by_type(self, notification_type: str, filter_fn=None) -> int:
        """Dismiss all notifications of a given type, optionally filtered.

        Args:
            notification_type: The notification type string to match.
            filter_fn: Optional callable(notification_dict) -> bool.
                       Only dismiss notifications where filter_fn returns True.
                       If None, dismisses all of the given type.

        Returns count dismissed.
        """
        before = len(self._pending)
        self._pending = [
            n for n in self._pending
            if not (
                n.get("type") == notification_type
                and (filter_fn is None or filter_fn(n))
            )
        ]
        return before - len(self._pending)

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
