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
# ⚠ The constant name MUST be the upper-case of its value, or the
# two-directional rail census mis-classifies it (REV-V3).
SAVE_FAILED = "save_failed"                        # CRITICAL: not saving
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
# REV-V3 (Aug 31, 2026): three types the game has always emitted as bare
# string literals at the producer, so the constant list above under-reported
# what a player can actually receive by three rows — and the rail census that
# reads this module could not see them. Values are unchanged; only the
# producers now name them here.
#
# `marshal_last_stand` is NOT sovereign-only: the encircled-Emperor arm and
# the ordinary cornered-marshal arm both raise it, and both ask the player to
# answer before the man is taken.
ARMISTICE_EXPIRED = "armistice_expired"              # HIGH/CRITICAL: truce ran out
MARSHAL_LAST_STAND = "marshal_last_stand"            # CRITICAL: encircled, decide
VINDICATION_EXPIRED = "vindication_expired"          # NORMAL: window passed


# ── The rail-exempt set (REV-V3) ────────────────────────────────────────────
# Every notification type a player can receive must carry a label AND a glyph
# on the notice rail (`notification_bar.gd`'s TYPE_ICONS / TYPE_ICON_SVGS), or
# stand here with its reason. The distinction matters because a census cannot
# otherwise tell "deliberately exempt" from "forgotten", which is how 33 types
# came to arrive as the anonymous priority pill.
#
# Membership is checked BOTH ways by `tests/test_rev_followups_2026_08_31.py`:
# a type here that acquires a producer fails the pin, and a producible type
# missing from the maps fails it too. So reviving one of these means joining
# the rail in the same commit.
RAIL_EXEMPT_TYPES = {
    JEALOUSY_CONFRONTATION: (
        "Declared for the Jealousy v3.2 petition families, but no producer "
        "ever called create_notification with it — the grievance reaches the "
        "player through the marshal-petition channel (a popup + its dialogue "
        "kind), and the string is live there, not here."),
    RIVALRY_CONFRONTATION: (
        "The same: a marshal_petition_dialog kind, never a rail row."),
    VASSAL_LOYALTY_CRITICAL: (
        "Superseded before it shipped by VASSAL_REBELLION_IMMINENT, which is "
        "produced, mapped, and says the same thing with a threshold behind "
        "it. Nothing has ever emitted this one."),
}


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

    @staticmethod
    def _currency(notification: Dict[str, Any]) -> int:
        """The turn this row last said something true.

        `turn_created` for a row nobody has re-stated (which is every row but
        the two reward families), `turn_refreshed` for one that is being kept
        live. Old saves have no `turn_refreshed` and fall back, so a loaded
        campaign behaves exactly as it did before this field existed.
        """
        created = int(notification.get("turn_created", 0))
        return max(created, int(notification.get("turn_refreshed", created)))

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
            # `max`, matching `add` (:249). UX23-A review round: these are
            # the collector's TWO in-place-update doors and they disagreed —
            # a plain assignment here can silently DE-escalate a standing row,
            # and since the cap evicts HIGH but never CRITICAL, a downgrade is
            # also a change in evictability. Unreachable through today's two
            # producers (each posts a fixed priority for its type), which is
            # why the sweep found the old line dead; bound now by a unit-level
            # pin rather than left as a divergence for a third caller to find.
            existing["priority"] = max(
                int(existing.get("priority", 0)),
                int(notification.get("priority", existing.get("priority", 0))))
            # `title` is deliberately NOT recomputed. The review round filed
            # it as a second divergence from `add`, and it is not one:
            # `_identity` matches on `base_title`, and `refresh` never moves
            # `repeat_count`, so re-deriving the title can only ever produce
            # the string already there. A first cut added that line, the
            # mutation sweep found it INERT, and it was deleted rather than
            # given a test that proves nothing. (The priority half of the same
            # finding IS real and is fixed above.)
            if notification.get("details"):
                existing["details"] = notification["details"]
            # UX23-A review round. `turn_created` stays put — it is when the
            # fact BEGAN, and that is what the row's "T3" stamp should say.
            # But two other things read it, and freezing it broke both:
            # `get_pending` sorts by it (so a live, re-stated grievance sank
            # below every HIGH notice that arrived later and fell off the
            # six-icon rail — the row this whole slice exists to put a button
            # on), and `_stale_high_index` measures staleness by it (so the
            # ONE row being re-stated every turn looked like the stalest
            # thing in the tray and was evicted first, then re-appended next
            # turn with a fresh uuid, ringing the very bell UX23-R2 silenced).
            # `turn_refreshed` separates "when it began" from "when it was
            # last true", and those two readers use the latter.
            existing["turn_refreshed"] = int(notification.get(
                "turn_created", existing.get("turn_created", 0)))
            return True
        self._pending.append(notification)
        self._enforce_cap()
        return False

    def _eviction_candidate(self) -> Optional[int]:
        """Index of the row the cap should shed, or None.

        UX23-R3, corrected by the UX23-A review round. The rule is "drop the
        least current thing that is safe to drop":

        * CRITICAL is never dropped, at any age.
        * A HIGH row is only a candidate once the tray has moved on from it by
          `HIGH_EVICTION_WINDOW_TURNS`. That window is what keeps a burst of
          crises breaking on one turn from truncating itself — and, since the
          clock is `_currency`, it also protects a grievance that is being
          re-stated every turn, which the first cut evicted FIRST.
        * NORMAL is always a candidate, but no longer unconditionally the
          first: the first cut spent "the oldest NORMAL" even when that was
          the row that had just arrived, so a fresh NORMAL alert dropped into
          a tray of fifty ten-turn-old grievances died on the same call that
          added it. Oldest wins; NORMAL only breaks a tie.
        """
        if not self._pending:
            return None
        newest = max(self._currency(n) for n in self._pending)
        best = None          # (currency, is_high, index)
        for i, n in enumerate(self._pending):
            priority = int(n.get("priority", 0))
            if priority >= int(NotificationPriority.CRITICAL):
                continue
            is_high = priority >= int(NotificationPriority.HIGH)
            currency = self._currency(n)
            if is_high and newest - currency < HIGH_EVICTION_WINDOW_TURNS:
                continue
            key = (currency, is_high)
            if best is None or key < best[0]:
                best = (key, i)
        return None if best is None else best[1]

    def _enforce_cap(self) -> None:
        """Trim to NOTIFICATION_CAP, shedding the least current safe row.

        UX23-R3: this used to consider NORMAL rows and nothing else, so once
        the tray filled with HIGH rows it stopped trimming entirely and every
        new alert overflowed past the cap. `DOTATION_EROSION` is HIGH and
        stands until the marshal is paid, so a campaign with several
        neglected marshals accumulated permanent, un-evictable rows.
        """
        while len(self._pending) > NOTIFICATION_CAP:
            idx = self._eviction_candidate()
            if idx is None:
                # Nothing safe to drop (all CRITICAL, or every HIGH is still
                # current news) — overflow rather than lose a live crisis.
                break
            self._pending.pop(idx)

    def get_pending(self) -> List[Dict[str, Any]]:
        """Return all pending notifications, sorted by priority (CRITICAL first).

        Within same priority, newest first (highest turn_created).
        """
        return sorted(
            self._pending,
            key=lambda n: (n.get("priority", 0), self._currency(n)),
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


def dismiss_marshal_ask(world, marshal_name: str) -> int:
    """Retire a marshal's standing "decide his fate" rail row(s).

    FA-N68 (slice 2, Sept 4 2026): the W6-7 last-stand notice is an ASK, and
    it must die with the question — whichever way the question dies. Before
    this helper the rule lived in two inline copies (the answer arm in
    `strategic.handle_response` and `WorldState.capture_marshal`) and in
    NEITHER of the other two roads a question can end on: `destroy_marshal`
    (the corps annihilated with the ask standing — measured, the CRITICAL
    row sat at the top of the rail forever, and CRITICAL is never evicted)
    and the unanswered-ask resolution FA-1 adds. One helper, eight call
    sites (the slice-2 claims audit counted seven; the review round's own
    `_retire_dead_decision` made it eight, as the slice-3 audit noted).

    Returns the number of rows retired (0 when the world carries no rail).
    """
    try:
        collector = getattr(world, "notifications", None)
        if collector is None:
            return 0
        return int(collector.dismiss_by_type(
            MARSHAL_LAST_STAND,
            lambda n: (n.get("details") or {}).get("marshal") == marshal_name))
    except Exception:
        return 0


def report_save_failure(world, detail: str, turn) -> bool:
    """Put the failed autosave on the rail, once, until it saves again.

    FA-S15-2. A failed autosave reached the SERVER CONSOLE and nobody else:
    `print(f"Autosave warning: ...")` at two call sites, no notification, no
    dispatch line, no client key. The player kept playing.

    ⚠ And the harm is not "there is no save" — measured on the shipped
    board, the file EXISTS and goes STALE: world turn 4, slot turn 2. It sits
    in the Load menu looking plausible, and the menu's Continue reads the
    NEWEST save, so a player who lost saving mid-campaign is silently resumed
    several turns back. The copy says that, because it is what happens.

    CRITICAL, so the cap can never evict it. `refresh` rather than `add`, so
    a campaign that cannot save rings the desk bell ONCE instead of every
    turn (UX23-R2's lesson) and `turn_created` stays pinned to the turn
    saving broke. No new serialized field: the collector IS the latch, and
    because it rides the save, a reload from an older good file correctly
    re-warns.
    """
    try:
        collector = getattr(world, "notifications", None)
        if collector is None:
            return False
        collector.refresh(create_notification(
            notification_type=SAVE_FAILED,
            priority=NotificationPriority.CRITICAL,
            title="The campaign is not being saved",
            message=(
                "The autosave could not be written. The slot in the Load "
                "menu is now STALE — resuming from it would put you back at "
                f"an earlier turn. {detail}"),
            turn_created=int(turn or 0),
            details={"detail": str(detail)},
        ))
        return True
    except Exception:
        return False


def clear_save_failure(world) -> int:
    """Retire the warning once a save succeeds.

    Structurally inert when no row stands: `dismiss_by_type` rebuilds an
    identical list, returns 0, and nothing aliases `_pending`.
    """
    try:
        collector = getattr(world, "notifications", None)
        if collector is None:
            return 0
        return int(collector.dismiss_by_type(SAVE_FAILED))
    except Exception:
        return 0
