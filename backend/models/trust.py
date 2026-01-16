"""
Trust System for Project Sovereign (Phase 2 - Disobedience)

Marshal trust in the player affects obedience probability.
Trust is earned through good decisions and lost through poor ones.
"""

from typing import Tuple


class Trust:
    """
    Marshal trust in player (0-100).

    Trust Levels:
    - 81-100: Loyal - Will follow almost any order
    - 61-80: Reliable - Rarely questions orders
    - 41-60: Questioning - May object to risky orders
    - 21-40: Strained - Frequently objects
    - 0-20: Broken - Highly likely to disobey
    """

    def __init__(self, value: int = 70):
        """Initialize trust with a starting value (default 70 = Reliable)."""
        self._value: int = max(0, min(100, int(value)))

    @property
    def value(self) -> int:
        """Get current trust value."""
        return int(self._value)

    def modify(self, delta: int) -> int:
        """
        Modify trust, return actual change.

        Args:
            delta: Amount to change trust (+/-)

        Returns:
            Actual change applied (may be less if capped)
        """
        old = self._value
        self._value = max(0, min(100, self._value + int(delta)))
        return int(self._value - old)

    def set(self, value: int) -> None:
        """Set trust to a specific value (clamped to 0-100)."""
        self._value = max(0, min(100, int(value)))

    def get_label(self) -> str:
        """
        Get human-readable trust level.

        Returns:
            One of: "Loyal", "Reliable", "Questioning", "Strained", "Broken"
        """
        if self._value >= 81:
            return "Loyal"
        if self._value >= 61:
            return "Reliable"
        if self._value >= 41:
            return "Questioning"
        if self._value >= 21:
            return "Strained"
        return "Broken"

    def get_level_info(self) -> Tuple[str, str]:
        """
        Get trust level label and description.

        Returns:
            Tuple of (label, description)
        """
        if self._value >= 81:
            return ("Loyal", "Will follow almost any order without question")
        if self._value >= 61:
            return ("Reliable", "Rarely questions orders")
        if self._value >= 41:
            return ("Questioning", "May object to risky orders")
        if self._value >= 21:
            return ("Strained", "Frequently objects and questions judgment")
        return ("Broken", "Highly likely to disobey or ignore orders")

    def __repr__(self) -> str:
        return f"Trust({self._value}, '{self.get_label()}')"

    def __int__(self) -> int:
        return int(self._value)


def calculate_obedience_chance(trust_value: int) -> float:
    """
    Calculate probability of obeying an order based on trust.

    Non-linear curve that rewards building trust:
    - Trust 80+: 100% obey (no random disobedience at high trust)
    - Trust 60-79: 90-99% obey (reliable range)
    - Trust 40-59: 70-89% obey (questioning range)
    - Trust 20-39: 40-69% obey (strained range)
    - Trust <20: 20-39% obey (broken range)

    Args:
        trust_value: Current trust value (0-100)

    Returns:
        Probability of obeying (0.0 to 1.0)
    """
    trust_value = int(trust_value)

    if trust_value >= 80:
        # High trust = guaranteed obedience
        return 1.0
    elif trust_value >= 60:
        # Reliable: 90% base + 0.5% per point above 60
        return 0.90 + (trust_value - 60) * 0.005
    elif trust_value >= 40:
        # Questioning: 70% base + 1% per point above 40
        return 0.70 + (trust_value - 40) * 0.01
    elif trust_value >= 20:
        # Strained: 40% base + 1.5% per point above 20
        return 0.40 + (trust_value - 20) * 0.015
    else:
        # Broken: 20% base + 1% per point
        return 0.20 + trust_value * 0.01


# NOTE: get_trust_change_for_action() was removed as dead code (never called).
# The trust change logic is handled directly in disobedience.py handle_response().


# Test code
if __name__ == "__main__":
    print("=" * 60)
    print("TRUST SYSTEM TEST")
    print("=" * 60)

    # Test Trust class
    trust = Trust(70)
    print(f"\nInitial trust: {trust}")
    print(f"Label: {trust.get_label()}")
    print(f"Level info: {trust.get_level_info()}")

    # Test modification
    change = trust.modify(-15)
    print(f"\nAfter -15: {trust} (actual change: {change})")

    change = trust.modify(50)
    print(f"After +50: {trust} (actual change: {change})")

    # Test obedience curve
    print("\n" + "=" * 60)
    print("OBEDIENCE CURVE")
    print("=" * 60)

    test_values = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    for tv in test_values:
        chance = calculate_obedience_chance(tv)
        print(f"Trust {tv:3d}: {chance:.1%} obedience")

    print("\n" + "=" * 60)
    print("TEST COMPLETE!")
    print("=" * 60)
