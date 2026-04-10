"""DialogueManager — centralized dialogue state management (R12).

Replaces scattered pending_diplomatic_dialogue/pending_dialogue_queue
field assignments with structured push/pop/peek operations.
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
        clear_stale(turn)      — auto-dismiss expired dialogues
        promote_if_empty()     — promote from queue when current is None
        remove_matching(pred)  — filter queue + current by predicate
    """

    QUEUE_CAP = 20
    BLOCKING_TIMEOUT_TURNS = 2  # turn_created + 2 < current → force-clear

    # Single source of truth for dialogue priority (lower = higher priority).
    # Unlisted types (counter_offer_response, advisory, etc.) default to 99.
    DIALOGUE_PRIORITY: Dict[str, int] = {
        "alliance_paradox": 0,
        "vassal_rebellion_imminent": 1,
        "sabotage_confrontation": 2,
        "incoming_proposal": 3,
    }

    def __init__(self):
        self._current: Optional[Dict] = None
        self._queue: List[Dict] = []

    # ── Core API ──────────────────────────────────────────────────────

    def push(self, dialogue: dict) -> None:
        """Add dialogue. If current slot is empty, set it; otherwise queue."""
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

    # ── Lifecycle ─────────────────────────────────────────────────────

    def clear_stale(self, current_turn: int) -> Optional[Dict]:
        """Auto-dismiss expired dialogues. Returns cleared dialogue if any.

        - Non-blocking: dismiss if turn_created < current_turn
        - Blocking: force-clear if turn_created + BLOCKING_TIMEOUT_TURNS < current_turn
        """
        if not self._current:
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
        """Promote highest-priority queue item to current slot."""
        if not self._queue:
            return
        self._queue.sort(
            key=lambda d: self.DIALOGUE_PRIORITY.get(d.get("type", ""), 99)
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
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DialogueManager":
        dm = cls()
        dm._current = copy.deepcopy(data.get("current")) if data.get("current") else None
        dm._queue = [copy.deepcopy(d) for d in data.get("queue", [])]
        return dm
