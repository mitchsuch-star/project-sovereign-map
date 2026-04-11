"""DialogueManager — centralized dialogue state management (R12).

Replaces scattered pending_diplomatic_dialogue/pending_dialogue_queue
field assignments with structured push/pop/peek operations.

Session 2 follow-up: Mailbox infrastructure added. DialogueManager is
now the SINGLE pending-diplomacy queue (diplomatic_queue eliminated).
"""

import copy
from typing import Dict, List, Optional, Callable


class DialogueManager:
    """Manages the active dialogue slot and priority queue.

    API:
        push(dialogue)         — set current if empty, queue if occupied
        replace(dialogue)      — overwrite current (enrichment / clear-then-set)
        pop()                  — clear current, auto-promote from queue
        peek()                 — read current without side effects
        is_blocking()          — True if current dialogue blocks commands
        is_hard_stop()         — True if current dialogue blocks ALL commands
        is_soft_stop()         — True if current is mailbox/hybrid soft-stop
        clear_stale(turn)      — auto-dismiss expired dialogues
        promote_if_empty()     — promote from queue when current is None
        remove_matching(pred)  — filter queue + current by predicate
        get_mailbox_count()    — count of mailbox-eligible items (active + queued)
        get_mailbox_items()    — ordered list of mailbox items for inbox panel
        activate_mailbox_item(id) — swap a queued item into the active slot
    """

    QUEUE_CAP = 20
    BLOCKING_TIMEOUT_TURNS = 2  # turn_created + 2 < current → force-clear

    # ── PL-27: Dialogue type taxonomy (Session 2) ────────────────────
    # Hard-stop: blocks ALL commands until resolved.
    HARD_STOP_TYPES = frozenset({
        "force_declare_war_confirmation",
        "alliance_paradox",
    })
    # Soft-stop mailbox: does NOT block ordinary commands. Player can
    # issue orders while a proposal waits. Visible via envoy badge.
    SOFT_STOP_MAILBOX_TYPES = frozenset({
        "incoming_proposal",
        "counter_offer",
        "counter_offer_response",
        "conflict_alert",
    })
    # Hybrid soft-stop: does NOT block ordinary commands, but end_turn
    # should auto-default or warn if unresolved.
    HYBRID_SOFT_STOP_TYPES = frozenset({
        "sabotage_confrontation",
        "vassal_rebellion_imminent",
    })
    # Local planning flow: player-initiated, never a global blocker.
    LOCAL_PLANNING_TYPES = frozenset({
        "proposal_confirm",
        "advisory",
        "mission",
        "terms_guidance",
        "ultimatum_demand_wizard",
        "pushback_confirm",
        "proposal_execute",
        "proposal_options",
        "feasibility",
        "ultimatum_confirm",
    })

    # Single source of truth for dialogue priority (lower = higher priority).
    # Unlisted types (counter_offer_response, advisory, etc.) default to 99.
    DIALOGUE_PRIORITY: Dict[str, int] = {
        "alliance_paradox": 0,
        "vassal_rebellion_imminent": 1,
        "sabotage_confrontation": 2,
        "incoming_proposal": 3,
        "counter_offer": 3,
        "counter_offer_response": 3,
        "conflict_alert": 4,
    }

    def __init__(self):
        self._current: Optional[Dict] = None
        self._queue: List[Dict] = []
        self._next_mailbox_id: int = 1  # monotonic ID for mailbox items

    # ── Core API ──────────────────────────────────────────────────────

    def _assign_mailbox_metadata(self, dialogue: dict) -> None:
        """Stamp mailbox_id and mailbox_order on mailbox-eligible dialogues."""
        dtype = dialogue.get("type", "")
        if dtype in self.SOFT_STOP_MAILBOX_TYPES and "mailbox_id" not in dialogue:
            dialogue["mailbox_id"] = self._next_mailbox_id
            dialogue["mailbox_order"] = self._next_mailbox_id
            dialogue["mailbox_priority"] = self.DIALOGUE_PRIORITY.get(dtype, 99)
            self._next_mailbox_id += 1

    def push(self, dialogue: dict) -> None:
        """Add dialogue. If current slot is empty, set it; otherwise queue."""
        self._assign_mailbox_metadata(dialogue)
        if self._current is None:
            self._current = dialogue
        else:
            if len(self._queue) < self.QUEUE_CAP:
                self._queue.append(dialogue)

    def replace(self, dialogue: dict) -> None:
        """Overwrite current dialogue regardless of state.

        Use for enrichment (modify/expand an active dialogue) or
        clear-then-set patterns where the new dialogue must become current.
        """
        previous = self._current
        new_type = dialogue.get("type", "")
        if previous is not None:
            previous_type = previous.get("type", "")
            if (
                previous_type in self.SOFT_STOP_MAILBOX_TYPES
                and new_type in self.SOFT_STOP_MAILBOX_TYPES
            ):
                if "mailbox_id" not in dialogue and "mailbox_id" in previous:
                    dialogue["mailbox_id"] = previous["mailbox_id"]
                if "mailbox_order" not in dialogue and "mailbox_order" in previous:
                    dialogue["mailbox_order"] = previous["mailbox_order"]
                if "mailbox_priority" not in dialogue:
                    dialogue["mailbox_priority"] = self.DIALOGUE_PRIORITY.get(
                        new_type, previous.get("mailbox_priority", 99)
                    )
            elif new_type in self.SOFT_STOP_MAILBOX_TYPES and "mailbox_id" not in dialogue:
                self._assign_mailbox_metadata(dialogue)
        elif new_type in self.SOFT_STOP_MAILBOX_TYPES and "mailbox_id" not in dialogue:
            self._assign_mailbox_metadata(dialogue)

        self._current = dialogue

    def pop(self) -> Optional[Dict]:
        """Remove and return current dialogue. Auto-promotes highest-priority
        item from queue if available."""
        result = self._current
        self._current = None
        self._promote()
        return result

    def peek(self) -> Optional[Dict]:
        """Read current dialogue without removing it."""
        return self._current

    def is_blocking(self) -> bool:
        """True if current dialogue has blocking=True."""
        return (self._current is not None
                and self._current.get("blocking", False))

    def is_hard_stop(self) -> bool:
        """True if current dialogue is a hard-stop type that blocks ALL commands.

        PL-27: Only hard-stop dialogues should prevent ordinary command execution.
        """
        if self._current is None:
            return False
        dtype = self._current.get("type", "")
        return dtype in self.HARD_STOP_TYPES

    def is_soft_stop(self) -> bool:
        """True if current dialogue is a soft-stop type (mailbox or hybrid).

        PL-27: Soft-stop dialogues do NOT block ordinary commands.
        """
        if self._current is None:
            return False
        dtype = self._current.get("type", "")
        return dtype in self.SOFT_STOP_MAILBOX_TYPES or dtype in self.HYBRID_SOFT_STOP_TYPES

    def is_local_planning(self) -> bool:
        """True if current dialogue is a player-initiated local planning flow."""
        if self._current is None:
            return False
        dtype = self._current.get("type", "")
        return dtype in self.LOCAL_PLANNING_TYPES

    def get_soft_stop_count(self) -> int:
        """Count of active soft-stop dialogue (0 or 1) plus queued items.

        PL-27: Authoritative envoy count for the top-bar badge.
        Retained for backward compatibility — prefer get_mailbox_count().
        """
        count = len(self._queue)
        if self.is_soft_stop():
            count += 1
        return count

    def get_mailbox_count(self) -> int:
        """Count of mailbox-eligible items (active + queued).

        Session 2 follow-up: Single source of truth for the mailbox badge.
        Counts SOFT_STOP_MAILBOX_TYPES only — excludes hybrid soft-stops.
        """
        count = 0
        if self._current and self._current.get("type", "") in self.SOFT_STOP_MAILBOX_TYPES:
            count += 1
        for item in self._queue:
            if item.get("type", "") in self.SOFT_STOP_MAILBOX_TYPES:
                count += 1
        return count

    def get_mailbox_items(self) -> List[Dict]:
        """Return ordered list of mailbox items for the inbox panel.

        Returns dicts with: mailbox_id, state (ACTIVE/WAITING), source_nation,
        item_type, arrival_turn, summary. Active item first, then by
        mailbox_priority asc, mailbox_order asc.
        """
        items = []

        def _make_summary(d: dict) -> dict:
            ctx = d.get("context", {})
            source = d.get("target_nation", ctx.get("source", "Unknown"))
            dtype = d.get("type", "unknown")
            turn = d.get("turn_created", 0)
            terms = ctx.get("counter_terms") or ctx.get("proposal") or ctx.get("terms") or {}
            ptype = terms.get("type", dtype)
            return {
                "mailbox_id": d.get("mailbox_id", 0),
                "state": "ACTIVE" if d is self._current else "WAITING",
                "source_nation": source,
                "item_type": dtype,
                "proposal_type": ptype,
                "arrival_turn": int(turn),
                "summary": f"{source} — {ptype.replace('_', ' ').title()}",
            }

        # Active mailbox item first
        if self._current and self._current.get("type", "") in self.SOFT_STOP_MAILBOX_TYPES:
            items.append(_make_summary(self._current))

        # Queued mailbox items sorted by priority then order
        queued = [
            q for q in self._queue
            if q.get("type", "") in self.SOFT_STOP_MAILBOX_TYPES
        ]
        queued.sort(key=lambda d: (
            d.get("mailbox_priority", 99),
            d.get("mailbox_order", 999999),
        ))
        for q in queued:
            items.append(_make_summary(q))

        return items

    def activate_mailbox_item(self, mailbox_id: int) -> Optional[Dict]:
        """Swap a queued mailbox item into the active slot.

        The previously active soft-stop item returns to the queue without
        data loss. Returns the newly activated dialogue, or None if the
        mailbox_id was not found or activation is blocked.
        """
        # Guard: only swap when active slot is empty or holds a mailbox item
        if self._current is not None:
            current_type = self._current.get("type", "")
            if current_type in self.HARD_STOP_TYPES:
                return None
            if current_type in self.HYBRID_SOFT_STOP_TYPES:
                return None
            if current_type in self.LOCAL_PLANNING_TYPES:
                return None

        # Find the target in queue
        target_idx = None
        for i, item in enumerate(self._queue):
            if item.get("mailbox_id") == mailbox_id:
                target_idx = i
                break

        if target_idx is None:
            # Also check if the active item already has this id
            if self._current and self._current.get("mailbox_id") == mailbox_id:
                return self._current
            return None

        target = self._queue.pop(target_idx)

        # Re-queue the current active item if it's a mailbox type
        if self._current is not None:
            current_type = self._current.get("type", "")
            if current_type in self.SOFT_STOP_MAILBOX_TYPES:
                # Preserve original turn_created — no refresh
                self._queue.append(self._current)

        self._current = target
        return target

    # ── Lifecycle ─────────────────────────────────────────────────────

    def clear_stale(self, current_turn: int) -> Optional[Dict]:
        """Auto-dismiss expired dialogues. Returns cleared dialogue if any.

        - Mailbox items: EXEMPT from generic stale clearing (player-deferred inbox content)
        - Non-blocking non-mailbox: dismiss if turn_created < current_turn
        - Blocking: force-clear if turn_created + BLOCKING_TIMEOUT_TURNS < current_turn
        """
        if not self._current:
            return None

        # Session 2 follow-up: Mailbox items never auto-expire
        dtype = self._current.get("type", "")
        if dtype in self.SOFT_STOP_MAILBOX_TYPES:
            return None

        turn_created = self._current.get("turn_created", 0)
        is_blocking = self._current.get("blocking", False)

        # Non-blocking: dismiss if older than current turn
        if not is_blocking and turn_created < current_turn:
            return self.pop()

        # Blocking: safety valve
        if is_blocking and turn_created + self.BLOCKING_TIMEOUT_TURNS < current_turn:
            return self.pop()

        return None

    def promote_if_empty(self) -> bool:
        """If current is None and queue has items, promote highest-priority.

        Returns True if promotion occurred. Use at turn-start to drain
        queue items from prior turns.
        """
        if self._current is not None or not self._queue:
            return False
        self._promote()
        return True

    def remove_matching(self, predicate: Callable[[Dict], bool]) -> int:
        """Remove queue items (and current if matched) by predicate.

        Returns count of items removed. Auto-promotes from queue if
        current was removed.
        """
        removed = 0
        # Filter queue
        before = len(self._queue)
        self._queue = [d for d in self._queue if not predicate(d)]
        removed += before - len(self._queue)
        # Check current
        if self._current and predicate(self._current):
            self._current = None
            removed += 1
            self._promote()
        return removed

    # ── Internals ─────────────────────────────────────────────────────

    def _promote(self) -> None:
        """Promote highest-priority queue item to current slot.

        Mailbox types use (mailbox_priority, mailbox_order) for stable sort.
        Non-mailbox types use DIALOGUE_PRIORITY as before.
        """
        if not self._queue:
            return
        self._queue.sort(
            key=lambda d: (
                d.get("mailbox_priority", self.DIALOGUE_PRIORITY.get(d.get("type", ""), 99)),
                d.get("mailbox_order", 999999),
            )
        )
        self._current = self._queue.pop(0)

    @property
    def queue_size(self) -> int:
        return len(self._queue)

    # ── Serialization ─────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "current": copy.deepcopy(self._current) if self._current else None,
            "queue": [copy.deepcopy(d) for d in self._queue],
            "next_mailbox_id": self._next_mailbox_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DialogueManager":
        dm = cls()
        dm._current = copy.deepcopy(data.get("current")) if data.get("current") else None
        dm._queue = [copy.deepcopy(d) for d in data.get("queue", [])]
        dm._next_mailbox_id = data.get("next_mailbox_id", 1)
        # Legacy migration: stamp mailbox_id on any mailbox items missing it
        for item in ([dm._current] if dm._current else []) + dm._queue:
            if item and item.get("type", "") in cls.SOFT_STOP_MAILBOX_TYPES and "mailbox_id" not in item:
                item["mailbox_id"] = dm._next_mailbox_id
                item["mailbox_order"] = dm._next_mailbox_id
                item["mailbox_priority"] = cls.DIALOGUE_PRIORITY.get(item.get("type", ""), 99)
                dm._next_mailbox_id += 1
        return dm
