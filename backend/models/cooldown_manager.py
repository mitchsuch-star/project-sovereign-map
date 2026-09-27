"""
CooldownManager + PopupQueue — centralized cooldown and popup state management.

R6 Architecture Refactoring Session 7.
Replaces scattered cooldown decrement methods and popup field sprawl.
"""

from typing import Dict, Optional, Tuple


class CooldownManager:
    """Centralizes dict and scalar cooldown storage + decrement.

    Manages cooldowns that follow the standard pattern:
    decrement by 1 per turn, remove when ≤ 0.

    Registered cooldowns are decremented by decrement_all().
    Unregistered cooldowns are stored but must be managed externally.
    """

    def __init__(self):
        self._dict_cooldowns: Dict[str, Dict[str, int]] = {}
        self._scalar_cooldowns: Dict[str, int] = {}
        # Track which cooldowns participate in decrement_all()
        self._registered_dicts: set = set()
        self._registered_scalars: set = set()

    def register_dict(self, name: str):
        """Register a dict cooldown for automatic decrement."""
        self._registered_dicts.add(name)
        if name not in self._dict_cooldowns:
            self._dict_cooldowns[name] = {}

    def register_scalar(self, name: str):
        """Register a scalar cooldown for automatic decrement."""
        self._registered_scalars.add(name)
        if name not in self._scalar_cooldowns:
            self._scalar_cooldowns[name] = 0

    # ── Dict cooldown access ──

    def get_dict(self, name: str) -> Dict[str, int]:
        """Get the full dict for a named cooldown. Returns ref (mutable)."""
        if name not in self._dict_cooldowns:
            self._dict_cooldowns[name] = {}
        return self._dict_cooldowns[name]

    def set_dict(self, name: str, value: Dict[str, int]):
        """Replace the entire dict for a named cooldown."""
        self._dict_cooldowns[name] = value

    def get_dict_value(self, name: str, key: str) -> int:
        """Get a single value from a dict cooldown."""
        return self._dict_cooldowns.get(name, {}).get(key, 0)

    def set_dict_value(self, name: str, key: str, turns: int):
        """Set a single value in a dict cooldown."""
        if name not in self._dict_cooldowns:
            self._dict_cooldowns[name] = {}
        self._dict_cooldowns[name][key] = turns

    # ── Scalar cooldown access ──

    def get_scalar(self, name: str) -> int:
        """Get a scalar cooldown value."""
        return self._scalar_cooldowns.get(name, 0)

    def set_scalar(self, name: str, turns: int):
        """Set a scalar cooldown value."""
        self._scalar_cooldowns[name] = turns

    # ── Decrement ──

    def decrement_all(self):
        """Decrement all registered cooldowns by 1. Remove expired (≤ 0).

        Called ONCE per turn in advance_turn. Only decrements registered cooldowns.
        """
        # Dict cooldowns
        for name in self._registered_dicts:
            cd = self._dict_cooldowns.get(name, {})
            expired = []
            for key in cd:
                cd[key] -= 1
                if cd[key] <= 0:
                    expired.append(key)
            for key in expired:
                del cd[key]

        # Scalar cooldowns
        for name in self._registered_scalars:
            if self._scalar_cooldowns.get(name, 0) > 0:
                self._scalar_cooldowns[name] -= 1

    # ── Serialization ──

    def to_dict(self) -> dict:
        """Serialize. Returns internal structure for embedding in WorldState.to_dict()."""
        return {
            "dict_cooldowns": {
                name: {k: int(v) for k, v in cd.items()}
                for name, cd in self._dict_cooldowns.items()
            },
            "scalar_cooldowns": {
                name: int(v)
                for name, v in self._scalar_cooldowns.items()
            },
            "registered_dicts": sorted(self._registered_dicts),
            "registered_scalars": sorted(self._registered_scalars),
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'CooldownManager':
        """Deserialize from save data."""
        mgr = cls()
        mgr._dict_cooldowns = {
            name: {k: int(v) for k, v in cd.items()}
            for name, cd in data.get("dict_cooldowns", {}).items()
        }
        mgr._scalar_cooldowns = {
            name: int(v)
            for name, v in data.get("scalar_cooldowns", {}).items()
        }
        mgr._registered_dicts = set(data.get("registered_dicts", []))
        mgr._registered_scalars = set(data.get("registered_scalars", []))
        return mgr


class PopupQueue:
    """Priority-ordered popup queue for one-shot diplomatic popups.

    Only one popup is delivered per response cycle (highest priority wins).
    Lower-priority popups remain queued for subsequent cycles.
    """

    LEGACY_ALIASES = {
        "alliance_paradox_popup": "commitment_paradox_popup",
    }

    # Priority order: lower index = higher priority. One popup is delivered
    # per response cycle.
    #
    # PC15-10 B4a (PETITION_POPUP_REVISIT_SPEC §4 F8, §6 Q5 RULED): the
    # order, JUSTIFIED — each row says why it outranks the next.
    #
    #   1 diplomatic_sabotage_popup       an active betrayal discovery outranks
    #                                     everything routine
    #   2 vassal_rebellion_imminent_popup a state about to leave the empire
    #   3 proclamation_popup              a nation being born waits for a
    #                                     rebellion, not for mail (NA-6 §11.10-5)
    #   4 diplomatic_objection_popup      Talleyrand blocking a command the
    #                                     player has just given
    #   5 pending_marshal_petition        marshal drama outranks routine mail —
    #                                     the CRISIS tier only since B1 (an
    #                                     audience never enters the queue)
    #   6 incoming_proposal_popup         current-turn envoys: they lapse at the
    #                                     end of the turn
    #   7 incoming_settlement_offer_popup persistent mail, which outwaits the
    #                                     envoys (SC-5 reversal commit 2)
    #   8 proposal_result_popup           a RECEIPT, informational — never a
    #                                     modal (FA-S17-D9 retired its scene):
    #                                     the backend lifts it onto the notice
    #                                     rail and the peace-summary line
    #   9 commitment_paradox_popup        a modal follow-up that orders itself
    #
    # Two entries are RETIRED (Q5):
    #   * `coalition_popup` — no producer ever wrote it (the coalition's
    #     formation reaches the player on the notice rail; `form_coalition`'s
    #     popup dict is local to its result). The slot, its response key, the
    #     world property and the save key are gone; a legacy save's key is
    #     dropped at load. (Removing the ORDER entry alone would have left a
    #     restored value that nothing could ever pop, re-saved forever and
    #     invisible to the game-over sweep, which walks this list.)
    #   * the `alliance_paradox_popup` ORDER entry — unreachable: it
    #     canonicalizes to the commitment paradox's slot, which the `seen` set
    #     has already consumed. The ALIAS stays (a legacy save still pushes
    #     under the old name).
    PRIORITY_ORDER = [
        "diplomatic_sabotage_popup",
        "vassal_rebellion_imminent_popup",
        "proclamation_popup",
        "diplomatic_objection_popup",
        "pending_marshal_petition",
        "incoming_proposal_popup",
        "incoming_settlement_offer_popup",
        "proposal_result_popup",
        "commitment_paradox_popup",
    ]

    # The ONE documented exception to "one popup per response" (F8 — the
    # `proposal_result` decision procedure's fold). The END-TURN response
    # (it carries `enemy_phase`) defers every CHOICE popup, because the route
    # table would swallow the turn report, and instead CARRIES these slots
    # beside the report, each popped OUTSIDE `pop_highest` by
    # `main._apply_command_popup_contract`:
    #   * proposal_result_popup  -> `proposal_result` (informational, safe
    #     beside the report — PL-5A/PL-30; lands on the rail);
    #   * proclamation_popup     -> `nation_proclamation` (a landmark the
    #     client stashes and raises at control return — NA-6b);
    #   * pending_marshal_petition -> `deferred_marshal_petition` (the crisis
    #     card, stashed and raised behind the report — FA-5).
    # The same contract attaches the current hard stop as `deferred_dialogue`
    # and blanks `envoy_digest` (the letter-book is derived, never queued).
    ENEMY_PHASE_CARRIED = (
        "proposal_result_popup",
        "proclamation_popup",
        "pending_marshal_petition",
    )

    # World attr → response key mapping
    RESPONSE_KEYS = {
        "diplomatic_sabotage_popup": "diplomatic_sabotage",
        "vassal_rebellion_imminent_popup": "vassal_rebellion_imminent",
        "proclamation_popup": "nation_proclamation",
        "diplomatic_objection_popup": "diplomatic_objection",
        "pending_marshal_petition": "marshal_petition",
        "incoming_proposal_popup": "incoming_proposal",
        "incoming_settlement_offer_popup": "incoming_settlement_offer",
        "proposal_result_popup": "proposal_result",
        "commitment_paradox_popup": "commitment_paradox_popup",
        "alliance_paradox_popup": "commitment_paradox_popup",
    }

    def __init__(self):
        self._queue: Dict[str, Optional[dict]] = {}

    @classmethod
    def _canonicalize_popup_type(cls, popup_type: str) -> str:
        return cls.LEGACY_ALIASES.get(popup_type, popup_type)

    def push(self, popup_type: str, data: dict):
        """Add or overwrite a popup in the queue."""
        self._queue[self._canonicalize_popup_type(popup_type)] = data

    def get(self, popup_type: str) -> Optional[dict]:
        """Get popup data without removing it."""
        return self._queue.get(self._canonicalize_popup_type(popup_type))

    def pop_highest(self) -> Tuple[Optional[str], Optional[str], Optional[dict]]:
        """Pop the highest-priority popup.

        Returns:
            (popup_type, response_key, data) or (None, None, None)
        """
        seen = set()
        for ptype in self.PRIORITY_ORDER:
            canonical_type = self._canonicalize_popup_type(ptype)
            if canonical_type in seen:
                continue
            seen.add(canonical_type)
            if canonical_type in self._queue and self._queue[canonical_type] is not None:
                data = self._queue.pop(canonical_type)
                return canonical_type, self.RESPONSE_KEYS[ptype], data
        return None, None, None

    def has_pending(self) -> bool:
        """Any non-None popup in the queue?"""
        return any(v is not None for v in self._queue.values())

    def clear_type(self, popup_type: str):
        """Remove a popup type from the queue."""
        self._queue.pop(self._canonicalize_popup_type(popup_type), None)

    def set(self, popup_type: str, value: Optional[dict]):
        """Set a popup value (or None to clear it)."""
        canonical_type = self._canonicalize_popup_type(popup_type)
        if value is None:
            self._queue.pop(canonical_type, None)
        else:
            self._queue[canonical_type] = value

    # ── Inspection (NOT serialization) ──
    #
    # PC15-10 B2 (F10): `to_dict`/`from_dict` were a third serialization
    # path lying next to the two real ones and read by no production code —
    # a save persists the queue through the world's popup PROPERTIES
    # (`WorldState.to_dict`/`from_dict`), and the marshal petition through
    # its plain field plus the S9 re-prime. Deleted, so nobody wires a save
    # to the wrong one. `snapshot` is a read-only copy for inspection.

    def snapshot(self) -> dict:
        """A copy of the live queue, keyed by canonical type (inspection
        only — persistence rides the world's popup properties)."""
        return {self._canonicalize_popup_type(k): v
                for k, v in self._queue.items() if v is not None}
