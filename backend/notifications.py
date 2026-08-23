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
NATION_FORMED = "nation_formed"                                # HIGH: a nation was proclaimed (NA-6)
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
# ES-7 second pass (§0.6.8): fired when a shortfall first OPENS (the grace
# clock starts) — the player's action window, announced at its start.
DOTATION_EXPECTATION = "dotation_expectation"        # NORMAL: reward expected
# W6-8 (Spoils of War): an enemy conqueror CONFISCATED a player marshal's
# estate outright — fired at confiscation time because the region leaves the
# marshal's rolls immediately, so the prune's ESTATE_LOST never sees it.
ESTATE_CONFISCATED = "estate_confiscated"            # HIGH: estate seized
# Jealousy v3.2 (docs/JEALOUSY_SPEC.md §11): the petition popup families —
# the notification is the mailbox record; the popup itself rides the
# marshal_petition channel.
JEALOUSY_CONFRONTATION = "jealousy_confrontation"    # HIGH: grievance aired
RIVALRY_CONFRONTATION = "rivalry_confrontation"      # HIGH: rivalry event
# ESP-4 (Jealousy v3.2 build): the treasury could not cover a rente — it
# lapsed unpaid and the marshal holds worthless paper.
RENTE_DEFAULTED = "rente_defaulted"                  # HIGH: rente lapsed
# Marshal recruitment: a new commander joined the roster (both the player's
# commissions and — fog willing — word of enemy ones).
MARSHAL_COMMISSIONED = "marshal_commissioned"        # NORMAL: new marshal
# PT-J4 "The Bench Speaks": the FIRST time the treasury covers a bench
# commission the executor's gate would grant, one notification says so —
# once per campaign (world.commission_hint_shown latch), never a nag.
COMMISSION_AVAILABLE = "commission_available"        # NORMAL: once-latched
# HC-G "Le Moniteur": an issue published — the one-line notice on the
# rail (no popup class, no queue slot, never a modal).
GAZETTE_PUBLISHED = "gazette_published"              # NORMAL: new issue
# WO slice 8 damage-legibility follow-up: a battle in one of OUR provinces
# wrecked civilian works. Nothing announced this — the campaign log kept a
# row, but the player learned of it only by hovering the province or
# opening the ledger's Territories tab, and the region panel (which
# carries the Repair chip) did not mention it at all.
#
# ONE per region per damage pass, never one per building: a 50k battle
# marks every civilian work plus the watchtower at once, and a per-building
# title would defeat the collector's repeat-collapse AND spray the 50-row
# cap. `details["region"]` is a `_SUBJECT_KEYS` member, so repeats across
# turns collapse for free.
#
# NORMAL, deliberately: it is a recurring economic beat, and NORMAL is the
# only priority the cap will evict — a HIGH spray would starve the tray.
BUILDINGS_DAMAGED = "buildings_damaged"              # NORMAL: works wrecked


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
        # PC-9 (quiet-France played campaign, Aug 3 2026): the tray reached
        # its 50-alert cap with SEVEN rows reading "Ney is cornered". The
        # rendered title carries the repeat marker, so the stable identity is
        # kept separately — otherwise the second repeat stops matching the
        # first and the collapse only ever works once.
        "base_title": title,
        "repeat_count": 1,
    }


NOTIFICATION_CAP = 50  # Max notifications before auto-dismissing oldest NORMAL

# UX23-R3: how far behind the tray's newest row a HIGH notice must be standing
# before the cap may evict it. `_enforce_cap` trimmed NORMAL rows ONLY, so a
# HIGH row was immortal — N eroding marshals produced N permanent rows that
# crowded real news off a full rail with no way to lose any of them. The
# window is what stops a same-turn BURST of crises from truncating itself:
# only a grievance that has been standing while the world moved on is stale
# enough to drop. CRITICAL is never evicted at any age.
HIGH_EVICTION_WINDOW_TURNS = 10


class NotificationCollector:
    """Collects and manages notifications attached to WorldState.

    Notifications persist across turns until the player dismisses them.
    Serialized with save/load via to_list() / from_list().
    Auto-dismisses oldest NORMAL notifications when cap (50) is exceeded.
    """

    def __init__(self):
        self._pending: List[Dict[str, Any]] = []

    # PC-9: the SUBJECT a notification is about, in the order producers write
    # it. Two rows sharing a type and a headline are the same live fact only
    # if they are about the same party — "alliance Accepted" for Prussia and
    # for Austria are two facts (PF-5 pins exactly that), while "Ney is
    # cornered" twice is one.
    _SUBJECT_KEYS = ("marshal", "counterpart", "target_nation", "nation",
                     "vassal", "region", "war_id")

    @classmethod
    def _identity(cls, notification: Dict[str, Any]) -> tuple:
        """Stable (type, headline, subject) identity for repeat collapsing.

        Falls back to `title` so notifications restored from a pre-PC-9 save
        still collapse.
        """
        details = notification.get("details") or {}
        subject = ""
        for key in cls._SUBJECT_KEYS:
            value = details.get(key)
            if value:
                subject = f"{key}={value}"
                break
        return (
            notification.get("type", ""),
            notification.get("base_title") or notification.get("title", ""),
            subject,
        )

    def add(self, notification: Dict[str, Any]) -> None:
        """Add a notification, collapsing an un-dismissed repeat of itself.

        PC-9: a re-fired alert REFRESHES the row it duplicates rather than
        adding another. The tray is a list of things still true, not a log —
        the campaign log is the log — so seven identical "Ney is cornered"
        rows conveyed exactly as much as one, while filling the 50-row cap
        that then silently starved everything else. The surviving row keeps
        the newest message and turn, takes the higher priority of the two,
        and carries the count in its title so the repetition is still visible.

        Auto-trims oldest NORMAL if over cap.
        """
        identity = self._identity(notification)
        for existing in self._pending:
            if self._identity(existing) != identity:
                continue
            count = int(existing.get("repeat_count", 1)) + 1
            base = existing.get("base_title") or existing.get("title", "")
            existing["repeat_count"] = count
            existing["base_title"] = base
            existing["title"] = f"{base} (x{count})"
            existing["message"] = notification.get("message", existing.get("message", ""))
            existing["turn_created"] = int(notification.get("turn_created",
                                                           existing.get("turn_created", 0)))
            existing["priority"] = max(int(existing.get("priority", 0)),
                                       int(notification.get("priority", 0)))
            if notification.get("details"):
                existing["details"] = notification["details"]
            return
        self._pending.append(notification)
        self._enforce_cap()

    def refresh(self, notification: Dict[str, Any]) -> bool:
        """Re-state a standing notification IN PLACE, keeping its id.

        UX23-R2. `create_notification` mints a fresh uuid on every call and
        `notification_bar.gd` dedupes the desk bell on that id — so a row
        re-stated with live figures every turn rang the bell every turn, per
        marshal, forever. Measured at the reported live state: four unmet
        marshals, four extra chimes a turn until paid. That is why the Aug-23
        reward fix was deliberately dismiss-only rather than re-post.

        `add` already updates a matching row in place (PC-9), but it also
        increments `repeat_count` and re-titles to "(x2)" — a REFRESH is not
        a repeat, so producers dismissed-then-added to dodge that, and threw
        the id away with it. This is the third door: same identity match, no
        repeat marker, same uuid.

        `turn_created` is deliberately NOT bumped. It is when the fact
        BEGAN, which is the honest thing for the row's "T3" stamp to say, and
        it is what lets `_enforce_cap` tell a ten-turn-old grievance from
        this morning's crisis (UX23-R3). The re-stated numbers live in
        `message` and `details`.

        Returns True if an existing row was refreshed, False if this was a
        first statement (in which case it is added normally).
        """
        identity = self._identity(notification)
        for existing in self._pending:
            if self._identity(existing) != identity:
                continue
            existing["message"] = notification.get(
                "message", existing.get("message", ""))
            existing["priority"] = int(notification.get(
                "priority", existing.get("priority", 0)))
            if notification.get("details"):
                existing["details"] = notification["details"]
            return True
        self._pending.append(notification)
        self._enforce_cap()
        return False

    def _oldest_index_at(self, priority: int) -> Optional[int]:
        """Index of the oldest pending row at exactly `priority`, or None."""
        oldest_idx = None
        oldest_turn = float('inf')
        for i, n in enumerate(self._pending):
            if int(n.get("priority", 0)) != int(priority):
                continue
            turn = n.get("turn_created", 0)
            if turn < oldest_turn:
                oldest_turn = turn
                oldest_idx = i
        return oldest_idx

    def _stale_high_index(self) -> Optional[int]:
        """Index of the oldest HIGH row that the world has moved on from.

        UX23-R3. "Stale" is measured against the tray's OWN newest row rather
        than against the world clock, so the collector stays self-contained
        and a save reloaded mid-campaign needs no turn injected. A burst of
        crises that all opened on the same turn is therefore never evictable
        by this arm — which is the point: the rail may drop a grievance the
        player has been ignoring for ten turns, never one that arrived with
        the news beside it.
        """
        if not self._pending:
            return None
        newest = max(int(n.get("turn_created", 0)) for n in self._pending)
        oldest_idx = None
        oldest_turn = float('inf')
        for i, n in enumerate(self._pending):
            if int(n.get("priority", 0)) != int(NotificationPriority.HIGH):
                continue
            turn = int(n.get("turn_created", 0))
            if newest - turn < HIGH_EVICTION_WINDOW_TURNS:
                continue
            if turn < oldest_turn:
                oldest_turn = turn
                oldest_idx = i
        return oldest_idx

    def _enforce_cap(self) -> None:
        """Trim to NOTIFICATION_CAP: oldest NORMAL first, then a stale HIGH.

        UX23-R3: this used to consider NORMAL rows and nothing else, so once
        the tray filled with HIGH rows it stopped trimming entirely and every
        new alert overflowed past the cap. `DOTATION_EROSION` is HIGH and
        stands until the marshal is paid, so a campaign with several
        neglected marshals accumulated permanent, un-evictable rows.
        CRITICAL is still never evicted, and neither is a HIGH row younger
        than `HIGH_EVICTION_WINDOW_TURNS`.
        """
        while len(self._pending) > NOTIFICATION_CAP:
            idx = self._oldest_index_at(int(NotificationPriority.NORMAL))
            if idx is None:
                idx = self._stale_high_index()
            if idx is None:
                # Nothing evictable (all CRITICAL, or every HIGH is current
                # news) — allow overflow rather than drop a live crisis.
                break
            self._pending.pop(idx)

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
