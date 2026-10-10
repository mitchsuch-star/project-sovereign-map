"""
Vindication Tracker for Project Sovereign (Phase 2 - Disobedience)

Tracks objection outcomes to determine if marshal or player was "right".
- Marshal objects, player trusts marshal, battle wins = marshal vindicated
- Marshal objects, player insists, battle wins = player vindicated
- Opposite outcomes hurt credibility

Vindication affects future objection severity and trust changes.
"""

import re
from typing import Dict, Optional, List


# ════════════════════════════════════════════════════════════════════════════
# SR-2e AAR-11 (Score Mandate, September 26, 2026) — THE VERDICT IS BOUND TO
# ITS ORDER.
#
# The Creative AAR: turn 3, Massena objected to `fortify` and the player
# insisted; turn 8 he ATTACKED Archduke Charles on the player's own order (no
# objection) and lost — "[Vindication] Massena's concerns were justified." The
# pending entry was keyed on the marshal's NAME alone, so it judged whatever
# battle he next fought as the attacker, on any order, any number of turns
# later (measured: a trust-to-retreat verdict fired on an unrelated victory
# four turns on; a compromise on a stance change judged his next attack).
#
# The rule: the answered order owns the verdict.
#   * an entry records the order that actually ran (`executed_order`) and
#     the turn;
#   * only an order that can FIGHT — an attack, a charge, a pursuit, a march
#     to a place — can be judged; a fortify, a drill, a stance, a retreat is
#     never stored (its test is not a battle he leads);
#   * a battle resolves the entry only when it is that order's own — its
#     defender is the order's target, or it is fought at the order's
#     province;
#   * the player's next successful order to the marshal EXPIRES it (the
#     executor holds the entry aside while the new order runs, so the new
#     order's own battle cannot answer the old question);
#   * a defiance replaces the order, so the entry is cleared;
#   * a legacy entry (no `executed_order` — a save from before this slice)
#     is dropped, never resolved.
# Lever False restores the name-keyed tracker byte for byte.
# ════════════════════════════════════════════════════════════════════════════

# The orders a battle he leads can answer.
BINDABLE_ACTIONS = frozenset({"attack", "charge", "pursue", "move", "march"})

# A caller that does not bind at all (the tracker's own unit callers, written
# against the name-keyed API) passes neither the executed order nor the
# battle's identity; it keeps the name-keyed behaviour. The production record
# site (`DisobedienceSystem.handle_response`) and the production resolve site
# (the post-combat pipeline's step 11) always bind — pinned by census in
# `tests/test_sr2e_standing_orders_reliable.py`.
_UNBOUND = object()


def _squash(text) -> str:
    """Normalise a name for matching ("Archduke Charles" == "ArchdukeCharles")."""
    return re.sub(r"[^a-z0-9]", "", str(text or "").lower())


def order_can_be_judged(order) -> bool:
    """True when `order` (a command dict) is one a battle he leads can answer:
    a fighting verb with a target."""
    if not isinstance(order, dict):
        return False
    action = str(order.get("action") or "").lower()
    return action in BINDABLE_ACTIONS and bool(_squash(order.get("target")))


def battle_answers_order(order, defender_name=None, battle_region=None) -> bool:
    """True when a battle (its defender's name and its province) is the
    bound order's own: the defender is the order's target, or the battle is
    fought at the order's province."""
    if not order_can_be_judged(order):
        return False
    target = _squash(order.get("target"))
    return target in ({_squash(defender_name), _squash(battle_region)} - {""})


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
        # V2a: Track defensive vindication for successful defenses
        self.pending_defensive_vindication: Dict[str, Dict] = {}
        # R58: Track last change turn for decay calculation
        self.last_change_turn: Dict[str, int] = {}  # marshal_name -> turn of last score change

    def record_choice(
        self,
        marshal_name: str,
        choice: str,
        original_order: Dict,
        alternative: Optional[Dict] = None,
        *,
        executed_order=_UNBOUND,
        turn: Optional[int] = None,
    ) -> None:
        """
        Record player's choice for later vindication check.

        Args:
            marshal_name: Name of marshal who objected
            choice: 'trust', 'insist', or 'compromise'
            original_order: The order player gave
            alternative: Marshal's suggested alternative (if any)
            executed_order: SR-2e AAR-11 — the order the answer actually ran
                (the original on insist, the alternative on trust, the
                compromise on compromise). Only an order a battle can answer
                is stored; any other clears the marshal's entry.
            turn: the turn the answer was given.
        """
        if executed_order is not _UNBOUND:
            if not order_can_be_judged(executed_order):
                self.pending.pop(marshal_name, None)
                return
            self.pending[marshal_name] = {
                'choice': choice,
                'original_order': original_order,
                'alternative': alternative,
                'executed_order': dict(executed_order),
                'turn_recorded': turn,
            }
            return
        self.pending[marshal_name] = {
            'choice': choice,
            'original_order': original_order,
            'alternative': alternative,
            'turn_recorded': None,  # Could track turn number
        }

    def hold_aside(self, marshal_name: str) -> Optional[Dict]:
        """SR-2e AAR-11: take the marshal's entry off the tracker while a NEW
        order of the player's runs, so that order's own battle cannot answer
        the old question. `settle_held` hands it back if the new order was
        refused, and lets it go if the order was carried out."""
        return self.pending.pop(marshal_name, None)

    def settle_held(self, marshal_name: str, held: Optional[Dict],
                    new_order_ran: bool) -> None:
        """The other half of `hold_aside`: a new order that ran EXPIRES the
        held entry; a refused one leaves the old order — and its question —
        standing (unless the refused command recorded a fresh answer)."""
        if held is None or new_order_ran:
            return
        self.pending.setdefault(marshal_name, held)

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
        game_state,
        *,
        defender_name=_UNBOUND,
        battle_region=_UNBOUND,
    ) -> Optional[Dict]:
        """
        Called after battle to update vindication.

        Args:
            marshal_name: Marshal who fought
            result: 'victory', 'defeat', or 'draw'
            game_state: Current game state (for marshal/authority access)
            defender_name / battle_region: SR-2e AAR-11 — the battle's
                defender and province; the entry resolves only when this
                battle is the answered order's own.

        Returns:
            Vindication result dict or None if no pending
        """
        if marshal_name not in self.pending:
            return None

        if ((defender_name is not _UNBOUND
                     or battle_region is not _UNBOUND)):
            if defender_name is _UNBOUND:
                defender_name = None
            if battle_region is _UNBOUND:
                battle_region = None
            entry = self.pending[marshal_name]
            order = entry.get('executed_order')
            if order is None:
                # A save from before the rule: the entry names no order, so
                # no battle can be shown to be its own. Let it go unjudged.
                self.pending.pop(marshal_name, None)
                return None
            if not battle_answers_order(order, defender_name, battle_region):
                # Another battle: the answered order is still out (a
                # pursuit, a march) and keeps its question.
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
                message = "The compromise led to stalemate. Cooperation continues."

        # Apply vindication change (capped at -5 to +5)
        if hasattr(marshal, 'vindication_score'):
            old_vindication = marshal.vindication_score
            marshal.vindication_score = max(-5, min(5, marshal.vindication_score + vindication_change))
            vindication_change = marshal.vindication_score - old_vindication
            # R58: Track last change turn for decay
            if vindication_change != 0:
                # Get current turn from game_state (WorldState or wrapper)
                current_turn = 0
                if hasattr(game_state, 'current_turn'):
                    current_turn = game_state.current_turn
                elif hasattr(game_state, 'world') and hasattr(game_state.world, 'current_turn'):
                    current_turn = game_state.world.current_turn
                self.last_change_turn[marshal_name] = current_turn

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
            "history": [h.copy() for h in self.history],
            "pending_defensive_vindication": {
                k: v.copy() for k, v in self.pending_defensive_vindication.items()
            },
            "last_change_turn": dict(self.last_change_turn),
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'VindicationTracker':
        """Deserialize vindication tracker from save/load data."""
        tracker = cls()
        tracker.pending = {k: v.copy() for k, v in data.get("pending", {}).items()}
        tracker.history = [h.copy() for h in data.get("history", [])]
        tracker.pending_defensive_vindication = {
            k: v.copy() for k, v in data.get("pending_defensive_vindication", {}).items()
        }
        tracker.last_change_turn = dict(data.get("last_change_turn", {}))
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
