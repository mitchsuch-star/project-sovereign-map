"""
Authority Tracker for Project Sovereign (Phase 2 - Disobedience)

Tracks Napoleon's perceived authority to prevent "always trust marshals" exploit.
If player always defers to marshals, authority erodes and marshals become less obedient.

V2b additions:
- Enriched recent_responses format: List[Dict] with {"choice": str, "turn": int}
- check_excessive_trust(): Ratio-based penalty replacing old count-based system
- modify_authority(): Clamped 0-100 setter for external callers
"""

from typing import Optional, Dict, List


class AuthorityTracker:
    """
    Tracks Napoleon's perceived authority.

    Prevents the "sycophancy exploit" where always trusting marshals
    becomes the optimal strategy. Instead:
    - Always trusting = authority drops = marshals less obedient
    - Always insisting = trust drops = marshals resent you
    - Balanced approach = healthy authority and trust

    Threshold Events:
    - Authority 70: "Whispers of Weakness" - minor warning
    - Authority 50: "Loss of Respect" - marshals start testing limits
    - Authority 30: "Emperor in Name Only" - open challenges

    Authority tiers for defiance (SEPARATE from get_obedience_modifier/get_severity_modifier):
    - >= 80: Strong leader (-10% defiance chance)
    - 50-79: Normal (0% defiance modifier)
    - < 50: Weak leader (+10% defiance chance)
    """

    # Authority threshold events
    THRESHOLD_EVENTS = {
        70: {
            'name': 'Whispers of Weakness',
            'description': 'Your marshals begin to question whether you truly command, or merely suggest.',
            'effect': 'trust_gains_reduced',
        },
        50: {
            'name': 'Loss of Respect',
            'description': 'The marshals no longer fear your displeasure. They debate openly.',
            'effect': 'obedience_reduced',
        },
        30: {
            'name': 'Emperor in Name Only',
            'description': 'Your commands are treated as suggestions. The marshals rule themselves.',
            'effect': 'severe_obedience_penalty',
        },
    }

    def __init__(self):
        """Initialize authority tracker."""
        self.authority: int = 100  # Napoleon starts fully authoritative
        # V2b: Enriched format — List[Dict] with {"choice": str, "turn": int}
        # Backward compat: from_dict handles bare strings (legacy saves)
        self.recent_responses: List[Dict] = []
        self._crossed_thresholds: List[int] = []  # Track which events have triggered

    def record_response(self, choice: str, current_turn: int = 0) -> Optional[Dict]:
        """
        Record player response to objection.

        V2b: Accepts current_turn for time-windowed penalty calculation.
        Stores enriched format {"choice": str, "turn": int}.

        Args:
            choice: 'trust', 'insist', or 'compromise'
            current_turn: Current game turn number (default 0 for backward compat)

        Returns:
            Event dict if threshold crossed, None otherwise
        """
        if choice not in ('trust', 'insist', 'compromise'):
            return None

        self.recent_responses.append({"choice": choice, "turn": int(current_turn)})
        if len(self.recent_responses) > 10:
            self.recent_responses.pop(0)

        # Apply excessive trust penalty (V2b, replaces old trust-ratio branch)
        penalty = check_excessive_trust(self, current_turn)
        if penalty != 0:
            self.authority = max(0, min(100, self.authority + penalty))

        self._evaluate_authority()

        return self._check_events()

    def _evaluate_authority(self) -> None:
        """
        Evaluate authority based on recent response pattern.

        V2b: Trust-ratio penalty REMOVED (replaced by check_excessive_trust
        in record_response). Only insist recovery and balanced recovery remain.
        """
        if len(self.recent_responses) < 5:
            return

        # Extract choices from enriched format
        choices = [r["choice"] if isinstance(r, dict) else r for r in self.recent_responses]
        total = len(choices)
        trust_ratio = choices.count('trust') / total
        insist_ratio = choices.count('insist') / total

        # V2b: Trust-ratio penalty REMOVED — handled by check_excessive_trust()
        # Only insist recovery and balanced recovery remain.

        # Always insisting = tyrant (but maintains authority)
        if insist_ratio > 0.80:
            # Authority stays high but trust suffers (handled elsewhere)
            self.authority = min(100, self.authority + 1)

        # Balanced approach = healthy leadership
        elif 0.30 <= trust_ratio <= 0.60:
            self.authority = min(100, self.authority + 1)

    def modify_authority(self, delta: int) -> None:
        """
        Modify authority by delta, clamped 0-100.

        Used by external callers (defiance outcomes, major victory/defeat).

        Args:
            delta: Amount to change (+/-)
        """
        self.authority = max(0, min(100, self.authority + delta))

    def get_trust_gain_modifier(self) -> float:
        """
        Get modifier for trust gains based on authority.

        When authority is low (player always trusts), trust gains are reduced
        because marshals see the player as a pushover.

        Returns:
            Multiplier for trust gains (0.5 to 1.0)
        """
        if len(self.recent_responses) < 5:
            return 1.0

        choices = [r["choice"] if isinstance(r, dict) else r for r in self.recent_responses]
        trust_ratio = choices.count('trust') / len(choices)

        if trust_ratio > 0.80:
            return 0.5  # Severe penalty for always trusting
        elif trust_ratio > 0.60:
            return 0.75  # Moderate penalty
        return 1.0

    def get_obedience_modifier(self) -> float:
        """
        Get modifier for obedience chance based on authority.

        High authority = marshals more likely to obey
        Low authority = marshals more likely to object

        Returns:
            Multiplier for obedience (0.9 to 1.1)
        """
        if self.authority >= 80:
            return 1.1  # Bonus for strong authority
        elif self.authority >= 50:
            return 1.0  # Normal
        else:
            return 0.9  # Penalty for weak authority

    def get_authority_label(self) -> str:
        """
        Get a human-readable label for the current authority level.

        Returns:
            Label string describing Napoleon's perceived authority.
        """
        if self.authority >= 90:
            return "Divine Right"
        elif self.authority >= 70:
            return "Commanding"
        elif self.authority >= 50:
            return "Respected"
        elif self.authority >= 30:
            return "Questionable"
        else:
            return "Emperor in Name Only"

    def get_severity_modifier(self) -> float:
        """
        Get modifier for objection severity based on authority.

        Low authority = marshals object more severely.

        Returns:
            Multiplier for severity (1.0 to 1.3)
        """
        if self.authority >= 80:
            return 1.0  # No modifier
        elif self.authority >= 50:
            return 1.1  # Slightly more severe objections
        else:
            return 1.25  # Much more severe objections

    def _check_events(self) -> Optional[Dict]:
        """
        Check for authority threshold events.

        Returns:
            Event dict if threshold crossed, None otherwise
        """
        for threshold, event in sorted(self.THRESHOLD_EVENTS.items(), reverse=True):
            if self.authority <= threshold and threshold not in self._crossed_thresholds:
                self._crossed_thresholds.append(threshold)
                return {
                    'type': 'authority_event',
                    'threshold': int(threshold),
                    'authority': int(self.authority),
                    **event
                }
        return None

    def reset_threshold_tracking(self) -> None:
        """Reset threshold tracking (useful for testing or game reset)."""
        self._crossed_thresholds = []

    def get_status(self) -> Dict:
        """
        Get current authority status.

        Returns:
            Dict with authority info
        """
        choices = [r["choice"] if isinstance(r, dict) else r for r in self.recent_responses]
        if len(choices) < 5:
            pattern = "insufficient_data"
        else:
            trust_ratio = choices.count('trust') / len(choices)
            if trust_ratio > 0.60:
                pattern = "permissive"
            elif trust_ratio < 0.30:
                pattern = "authoritarian"
            else:
                pattern = "balanced"

        return {
            'authority': int(self.authority),
            'recent_responses': self.recent_responses.copy(),
            'pattern': pattern,
            'trust_gain_modifier': self.get_trust_gain_modifier(),
            'obedience_modifier': self.get_obedience_modifier(),
        }

    def __repr__(self) -> str:
        return f"AuthorityTracker(authority={self.authority}, responses={len(self.recent_responses)})"

    def to_dict(self) -> dict:
        """Serialize authority tracker for save/load.

        V2b: recent_responses stored as List[Dict] with {"choice", "turn"}.
        """
        return {
            "authority": self.authority,
            "recent_responses": [
                r if isinstance(r, dict) else {"choice": r, "turn": 0}
                for r in self.recent_responses
            ],
            "_crossed_thresholds": self._crossed_thresholds.copy()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'AuthorityTracker':
        """Deserialize authority tracker from save/load data.

        V2b: Backward compatible — bare strings treated as legacy format.
        """
        tracker = cls()
        tracker.authority = data.get("authority", 100)
        raw = data.get("recent_responses", [])
        tracker.recent_responses = [
            r if isinstance(r, dict) else {"choice": r, "turn": 0}
            for r in raw
        ]
        tracker._crossed_thresholds = data.get("_crossed_thresholds", []).copy()
        return tracker


def check_excessive_trust(authority_tracker, current_turn: int) -> int:
    """Check if player is trusting too often (pushover behavior).

    Uses a 10-turn sliding window. Only fires when >= 3 responses in window.

    Returns authority penalty (0, -2, or -3).
    Called from record_response() after each objection response.
    """
    recent = [
        r for r in authority_tracker.recent_responses
        if isinstance(r, dict) and r.get("turn", 0) >= current_turn - 10
    ]

    total = len(recent)
    if total < 3:  # Not enough data to judge
        return 0

    trust_count = sum(1 for r in recent if r.get("choice") == "trust")
    ratio = trust_count / total

    if ratio > 0.80:    # 80%+ = egregious pushover
        return -3
    elif ratio > 0.65:  # 65%+ = concerning pattern
        return -2
    else:
        return 0
