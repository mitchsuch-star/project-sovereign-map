"""
Authority Tracker for Project Sovereign (Phase 2 - Disobedience)

Tracks Napoleon's perceived authority to prevent "always trust marshals" exploit.
If player always defers to marshals, authority erodes and marshals become less obedient.
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
        self.recent_responses: List[str] = []  # Last 10 responses
        self._crossed_thresholds: List[int] = []  # Track which events have triggered

    def record_response(self, choice: str) -> Optional[Dict]:
        """
        Record player response to objection.

        Args:
            choice: 'trust', 'insist', or 'compromise'

        Returns:
            Event dict if threshold crossed, None otherwise
        """
        if choice not in ('trust', 'insist', 'compromise'):
            return None

        self.recent_responses.append(choice)
        if len(self.recent_responses) > 10:
            self.recent_responses.pop(0)

        self._evaluate_authority()

        return self._check_events()

    def _evaluate_authority(self) -> None:
        """Evaluate authority based on recent response pattern."""
        if len(self.recent_responses) < 5:
            return

        trust_ratio = self.recent_responses.count('trust') / len(self.recent_responses)
        insist_ratio = self.recent_responses.count('insist') / len(self.recent_responses)

        # Always trusting = weak leader
        if trust_ratio > 0.80:
            self.authority = max(0, self.authority - 5)
        elif trust_ratio > 0.60:
            self.authority = max(0, self.authority - 2)

        # Always insisting = tyrant (but maintains authority)
        elif insist_ratio > 0.80:
            # Authority stays high but trust suffers (handled elsewhere)
            self.authority = min(100, self.authority + 1)

        # Balanced approach = healthy leadership
        elif 0.30 <= trust_ratio <= 0.60:
            self.authority = min(100, self.authority + 1)

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

        trust_ratio = self.recent_responses.count('trust') / len(self.recent_responses)

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
        if len(self.recent_responses) < 5:
            pattern = "insufficient_data"
        else:
            trust_ratio = self.recent_responses.count('trust') / len(self.recent_responses)
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
        """Serialize authority tracker for save/load."""
        return {
            "authority": self.authority,
            "recent_responses": self.recent_responses.copy(),
            "_crossed_thresholds": self._crossed_thresholds.copy()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'AuthorityTracker':
        """Deserialize authority tracker from save/load data."""
        tracker = cls()
        tracker.authority = data.get("authority", 100)
        tracker.recent_responses = data.get("recent_responses", []).copy()
        tracker._crossed_thresholds = data.get("_crossed_thresholds", []).copy()
        return tracker


# Test code
if __name__ == "__main__":
    print("=" * 60)
    print("AUTHORITY TRACKER TEST")
    print("=" * 60)

    tracker = AuthorityTracker()
    print(f"\nInitial: {tracker}")
    print(f"Status: {tracker.get_status()}")

    # Simulate always trusting
    print("\n" + "=" * 60)
    print("SIMULATING ALWAYS TRUSTING")
    print("=" * 60)

    for i in range(10):
        event = tracker.record_response('trust')
        print(f"Response {i+1}: trust -> Authority: {tracker.authority}")
        if event:
            print(f"  EVENT: {event['name']} - {event['description']}")

    print(f"\nFinal status: {tracker.get_status()}")
    print(f"Trust gain modifier: {tracker.get_trust_gain_modifier()}")
    print(f"Obedience modifier: {tracker.get_obedience_modifier()}")

    # Reset and test balanced approach
    print("\n" + "=" * 60)
    print("SIMULATING BALANCED APPROACH")
    print("=" * 60)

    tracker = AuthorityTracker()
    responses = ['trust', 'insist', 'compromise', 'trust', 'insist',
                 'compromise', 'trust', 'compromise', 'insist', 'trust']

    for i, response in enumerate(responses):
        event = tracker.record_response(response)
        print(f"Response {i+1}: {response} -> Authority: {tracker.authority}")
        if event:
            print(f"  EVENT: {event['name']}")

    print(f"\nFinal status: {tracker.get_status()}")

    print("\n" + "=" * 60)
    print("TEST COMPLETE!")
    print("=" * 60)
