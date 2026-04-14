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

    # Priority order: lower index = higher priority
    PRIORITY_ORDER = [
        "coalition_popup",
        "diplomatic_sabotage_popup",
        "vassal_rebellion_imminent_popup",
        "diplomatic_objection_popup",
        "incoming_proposal_popup",
        "proposal_result_popup",
        "alliance_paradox_popup",
    ]

    # World attr → response key mapping
    RESPONSE_KEYS = {
        "coalition_popup": "coalition_popup",
        "diplomatic_sabotage_popup": "diplomatic_sabotage",
        "vassal_rebellion_imminent_popup": "vassal_rebellion_imminent",
        "diplomatic_objection_popup": "diplomatic_objection",
        "incoming_proposal_popup": "incoming_proposal",
        "proposal_result_popup": "proposal_result",
        "alliance_paradox_popup": "alliance_paradox_popup",
    }

    def __init__(self):
        self._queue: Dict[str, Optional[dict]] = {}

    def push(self, popup_type: str, data: dict):
        """Add or overwrite a popup in the queue."""
        self._queue[popup_type] = data

    def get(self, popup_type: str) -> Optional[dict]:
        """Get popup data without removing it."""
        return self._queue.get(popup_type)

    def pop_highest(self) -> Tuple[Optional[str], Optional[str], Optional[dict]]:
        """Pop the highest-priority popup.

        Returns:
            (popup_type, response_key, data) or (None, None, None)
        """
        for ptype in self.PRIORITY_ORDER:
            if ptype in self._queue and self._queue[ptype] is not None:
                data = self._queue.pop(ptype)
                return ptype, self.RESPONSE_KEYS[ptype], data
        return None, None, None

    def has_pending(self) -> bool:
        """Any non-None popup in the queue?"""
        return any(v is not None for v in self._queue.values())

    def clear_type(self, popup_type: str):
        """Remove a popup type from the queue."""
        self._queue.pop(popup_type, None)

    def set(self, popup_type: str, value: Optional[dict]):
        """Set a popup value (or None to clear it)."""
        if value is None:
            self._queue.pop(popup_type, None)
        else:
            self._queue[popup_type] = value

    # ── Serialization ──

    def to_dict(self) -> dict:
        """Serialize popup queue state."""
        return {k: v for k, v in self._queue.items()}

    @classmethod
    def from_dict(cls, data: dict) -> 'PopupQueue':
        """Deserialize from save data."""
        q = cls()
        q._queue = {k: v for k, v in data.items() if v is not None}
        return q
