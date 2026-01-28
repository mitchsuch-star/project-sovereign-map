"""
Vindication Tracker for Project Sovereign (Phase 2 - Disobedience)

Tracks objection outcomes to determine if marshal or player was "right".
- Marshal objects, player trusts marshal, battle wins = marshal vindicated
- Marshal objects, player insists, battle wins = player vindicated
- Opposite outcomes hurt credibility

Vindication affects future objection severity and trust changes.
"""

from typing import Dict, Optional, List


class VindicationTracker:
    """
    Tracks objection outcomes for marshal credibility.

    When a marshal objects and player makes a choice:
    1. Record the choice (trust/insist/compromise)
    2. After battle, compare outcome to choice
    3. Update vindication scores and trust accordingly

    Vindication Score Range: -5 to +5
    - Positive: Marshal has been proven right, more bold in objections
    - Negative: Marshal has been proven wrong, less bold in objections
    """

    def __init__(self):
        """Initialize vindication tracker."""
        self.pending: Dict[str, Dict] = {}  # marshal_name -> pending vindication
        self.history: List[Dict] = []  # Historical vindication events

    def record_choice(
        self,
        marshal_name: str,
        choice: str,
        original_order: Dict,
        alternative: Optional[Dict] = None
    ) -> None:
        """
        Record player's choice for later vindication check.

        Args:
            marshal_name: Name of marshal who objected
            choice: 'trust', 'insist', or 'compromise'
            original_order: The order player gave
            alternative: Marshal's suggested alternative (if any)
        """
        self.pending[marshal_name] = {
            'choice': choice,
            'original_order': original_order,
            'alternative': alternative,
            'turn_recorded': None,  # Could track turn number
        }

    def has_pending(self, marshal_name: str) -> bool:
        """Check if marshal has pending vindication."""
        return marshal_name in self.pending

    def get_pending(self, marshal_name: str) -> Optional[Dict]:
        """Get pending vindication info for marshal."""
        return self.pending.get(marshal_name)

    def resolve_battle(
        self,
        marshal_name: str,
        result: str,
        game_state
    ) -> Optional[Dict]:
        """
        Called after battle to update vindication.

        Args:
            marshal_name: Marshal who fought
            result: 'victory', 'defeat', or 'draw'
            game_state: Current game state (for marshal/authority access)

        Returns:
            Vindication result dict or None if no pending
        """
        if marshal_name not in self.pending:
            return None

        pending = self.pending.pop(marshal_name)
        choice = pending['choice']

        # Get marshal from game state
        marshal = None
        if hasattr(game_state, 'world'):
            marshal = game_state.world.get_marshal(marshal_name)
        elif hasattr(game_state, 'get_marshal'):
            marshal = game_state.get_marshal(marshal_name)
        elif hasattr(game_state, 'marshals'):
            marshal = game_state.marshals.get(marshal_name)

        if marshal is None:
            return None

        # Get authority tracker
        authority = None
        if hasattr(game_state, 'authority_tracker'):
            authority = game_state.authority_tracker
        elif hasattr(game_state, 'world') and hasattr(game_state.world, 'authority_tracker'):
            authority = game_state.world.authority_tracker

        # Calculate vindication changes
        vindication_change = 0
        trust_change = 0
        authority_change = 0
        message = ""

        if choice == 'trust':
            # Player trusted marshal's judgment
            if result == 'victory':
                # Marshal was right!
                vindication_change = +1
                trust_change = +3
                message = f"{marshal_name}'s judgment was vindicated! Victory proves the wisdom of trust."
            elif result == 'defeat':
                # Marshal was wrong, but player trusted them
                vindication_change = -1
                trust_change = 0  # No trust penalty for defeat when trusting
                message = f"{marshal_name}'s alternative did not succeed. Perhaps the original order was better..."
            else:  # draw
                vindication_change = 0
                trust_change = +1
                message = f"The battle was inconclusive. {marshal_name}'s judgment remains untested."

        elif choice == 'insist':
            # Player insisted on original order
            if result == 'victory':
                # Player was right to insist!
                vindication_change = -1  # Marshal was wrong to object
                authority_change = +5
                message = f"Your insistence paid off! {marshal_name} must acknowledge your strategic vision."
            elif result == 'defeat':
                # Marshal was right to object!
                vindication_change = +1  # Marshal was right
                trust_change = -5
                authority_change = -5
                message = f"{marshal_name}'s concerns were justified. The defeat could have been avoided."
            else:  # draw
                vindication_change = 0
                trust_change = -1
                message = f"The battle proved nothing. {marshal_name} may still question your judgment."

        elif choice == 'compromise':
            # Player and marshal found middle ground
            if result == 'victory':
                vindication_change = 0  # Shared credit
                trust_change = +3
                authority_change = +2
                message = f"The compromise worked! Both you and {marshal_name} can claim credit."
            elif result == 'defeat':
                vindication_change = 0  # Shared blame
                trust_change = -2
                authority_change = -2
                message = f"The compromise failed. The blame is shared between you and {marshal_name}."
            else:  # draw
                vindication_change = 0
                trust_change = +2
                message = f"The compromise led to stalemate. Cooperation continues."

        # Apply vindication change (capped at -5 to +5)
        if hasattr(marshal, 'vindication_score'):
            old_vindication = marshal.vindication_score
            marshal.vindication_score = max(-5, min(5, marshal.vindication_score + vindication_change))
            vindication_change = marshal.vindication_score - old_vindication

        # Apply trust change (with authority modifier)
        if hasattr(marshal, 'trust'):
            trust_modifier = 1.0
            if authority and hasattr(authority, 'get_trust_gain_modifier'):
                trust_modifier = authority.get_trust_gain_modifier()

            # Only modify positive trust gains based on authority
            if trust_change > 0:
                trust_change = int(trust_change * trust_modifier)

            actual_trust_change = marshal.modify_trust(trust_change)
        else:
            actual_trust_change = 0

        # Apply authority change
        if authority and authority_change != 0:
            authority.authority = max(0, min(100, authority.authority + authority_change))

        # Record battle result
        if hasattr(marshal, 'recent_battles'):
            marshal.recent_battles.append(result)
            if len(marshal.recent_battles) > 3:
                marshal.recent_battles.pop(0)

        # Record override (if player insisted)
        if hasattr(marshal, 'recent_overrides'):
            marshal.recent_overrides.append(choice == 'insist')
            if len(marshal.recent_overrides) > 5:
                marshal.recent_overrides.pop(0)

        # Create result dict
        vindication_result = {
            'marshal': marshal_name,
            'choice': choice,
            'result': result,
            'vindication_change': int(vindication_change),
            'trust_change': int(actual_trust_change),
            'authority_change': int(authority_change),
            'message': message,
            'new_vindication': int(getattr(marshal, 'vindication_score', 0)),
            'new_trust': int(marshal.trust.value) if hasattr(marshal, 'trust') else 70,
        }

        # Add to history
        self.history.append(vindication_result)

        return vindication_result

    def clear_pending(self, marshal_name: str) -> None:
        """Clear pending vindication for a marshal (e.g., if they don't fight)."""
        if marshal_name in self.pending:
            del self.pending[marshal_name]

    def clear_all_pending(self) -> None:
        """Clear all pending vindications (e.g., at turn end)."""
        self.pending.clear()

    def get_history(self, marshal_name: Optional[str] = None) -> List[Dict]:
        """
        Get vindication history.

        Args:
            marshal_name: Filter by marshal name (optional)

        Returns:
            List of vindication events
        """
        if marshal_name:
            return [h for h in self.history if h['marshal'] == marshal_name]
        return self.history.copy()

    def get_vindication_data(self, marshal_name: str) -> Dict:
        """
        Get vindication data for a specific marshal (for debug display).

        Args:
            marshal_name: Name of marshal

        Returns:
            Dict with:
            - score: Vindication score (-5 to +5)
            - recent_overrides: List of recent overrides
            - recent_battles: List of recent battle results
            - history: Recent vindication events
        """
        # Get history for this marshal
        marshal_history = self.get_history(marshal_name)

        # Extract recent overrides and battles from history
        recent_overrides = []
        recent_battles = []

        for event in marshal_history[-5:]:  # Last 5 events
            recent_overrides.append(event.get('choice') == 'insist')
            recent_battles.append(event.get('result', 'unknown'))

        return {
            'score': marshal_history[-1].get('new_vindication', 0) if marshal_history else 0,
            'recent_overrides': recent_overrides,
            'recent_battles': recent_battles,
            'history': marshal_history[-3:]  # Last 3 events
        }

    def __repr__(self) -> str:
        return f"VindicationTracker(pending={len(self.pending)}, history={len(self.history)})"

    def to_dict(self) -> dict:
        """Serialize vindication tracker for save/load."""
        return {
            "pending": {k: v.copy() for k, v in self.pending.items()},
            "history": [h.copy() for h in self.history]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'VindicationTracker':
        """Deserialize vindication tracker from save/load data."""
        tracker = cls()
        tracker.pending = {k: v.copy() for k, v in data.get("pending", {}).items()}
        tracker.history = [h.copy() for h in data.get("history", [])]
        return tracker


# Test code
if __name__ == "__main__":
    from backend.models.trust import Trust

    print("=" * 60)
    print("VINDICATION TRACKER TEST")
    print("=" * 60)

    # Create mock game state
    class MockMarshal:
        def __init__(self, name):
            self.name = name
            self.trust = Trust(70)
            self.vindication_score = 0
            self.recent_battles = []
            self.recent_overrides = []

    class MockAuthority:
        def __init__(self):
            self.authority = 100

        def get_trust_gain_modifier(self):
            return 1.0

    class MockWorld:
        def __init__(self):
            self.marshals = {'Ney': MockMarshal('Ney')}
            self.authority_tracker = MockAuthority()

        def get_marshal(self, name):
            return self.marshals.get(name)

    class MockGameState:
        def __init__(self):
            self.world = MockWorld()
            self.authority_tracker = self.world.authority_tracker

    game_state = MockGameState()
    tracker = VindicationTracker()

    print(f"\nInitial state: {tracker}")
    ney = game_state.world.get_marshal('Ney')
    print(f"Ney trust: {ney.trust}, vindication: {ney.vindication_score}")

    # Test: Trust marshal, they win
    print("\n" + "-" * 40)
    print("TEST 1: Trust marshal, they win")
    tracker.record_choice('Ney', 'trust', {'action': 'attack'})
    result = tracker.resolve_battle('Ney', 'victory', game_state)
    print(f"Result: {result['message']}")
    print(f"Vindication change: {result['vindication_change']:+d}")
    print(f"Trust change: {result['trust_change']:+d}")
    print(f"New trust: {ney.trust}, vindication: {ney.vindication_score}")

    # Test: Insist on order, lose
    print("\n" + "-" * 40)
    print("TEST 2: Insist on order, lose")
    tracker.record_choice('Ney', 'insist', {'action': 'defend'})
    result = tracker.resolve_battle('Ney', 'defeat', game_state)
    print(f"Result: {result['message']}")
    print(f"Vindication change: {result['vindication_change']:+d}")
    print(f"Trust change: {result['trust_change']:+d}")
    print(f"Authority change: {result['authority_change']:+d}")
    print(f"New trust: {ney.trust}, vindication: {ney.vindication_score}")

    # Test: Compromise, draw
    print("\n" + "-" * 40)
    print("TEST 3: Compromise, draw")
    tracker.record_choice('Ney', 'compromise', {'action': 'probe'})
    result = tracker.resolve_battle('Ney', 'draw', game_state)
    print(f"Result: {result['message']}")
    print(f"Trust change: {result['trust_change']:+d}")

    print("\n" + "-" * 40)
    print("HISTORY:")
    for event in tracker.get_history():
        print(f"  {event['choice']} -> {event['result']}: {event['message'][:50]}...")

    print("\n" + "=" * 60)
    print("TEST COMPLETE!")
    print("=" * 60)
