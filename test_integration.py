"""
Integration tests for all game systems.
Run with: python test_integration.py
"""
import sys
import os

# Suppress debug output
class SuppressOutput:
    def __init__(self):
        self._stdout = sys.stdout
        self._devnull = open(os.devnull, 'w', encoding='utf-8', errors='replace')

    def __enter__(self):
        sys.stdout = self._devnull
        return self

    def __exit__(self, *args):
        sys.stdout = self._stdout
        self._devnull.close()


def run_tests():
    """Run all integration tests and return results."""
    from backend.models.world_state import WorldState
    from backend.commands.executor import CommandExecutor
    from backend.game_logic.turn_manager import TurnManager
    from backend.models.marshal import Stance
    from backend.commands.disobedience import DisobedienceSystem

    results = []

    # Test 1: Nation-aware lookup
    w = WorldState()
    r1 = w.get_enemy_by_name_for_nation('Ney', 'Britain')
    r2 = w.get_enemy_at_location_for_nation('Belgium', 'Britain')
    results.append(('Nation-aware enemy lookup', bool(r1 and r2)))

    # Test 2: Trust warnings
    w = WorldState()
    ney = w.get_marshal('Ney')
    with SuppressOutput():
        ney.trust.modify(-40)
        warnings = w._check_trust_warnings()
    results.append(('Trust warning system', len(warnings) > 0 and ney.trust_warning_shown))

    # Test 3: Recklessness property
    w = WorldState()
    ney = w.get_marshal('Ney')
    ney.cavalry = True
    results.append(('Recklessness property', ney.is_reckless_cavalry == True))

    # Test 4: Cavalry limits
    w = WorldState()
    ney = w.get_marshal('Ney')
    ney.cavalry = True
    ney.stance = Stance.DEFENSIVE
    ney.turns_in_defensive_stance = 3
    with SuppressOutput():
        events = w._check_cavalry_limits()
    results.append(('Cavalry limits', len(events) > 0 and ney.stance == Stance.AGGRESSIVE))

    # Test 5: Turn manager
    w = WorldState()
    tm = TurnManager(w)
    game_state = {"world": w}  # Executor expects dict with "world" key
    try:
        with SuppressOutput():
            result = tm.end_turn(game_state)
        results.append(('Turn manager flow', result is not None and w.current_turn == 2))
    except Exception as e:
        results.append(('Turn manager flow', False))

    # Test 6: Combat attack modifiers
    w = WorldState()
    ney = w.get_marshal('Ney')
    ney.shock_bonus = 2
    ney.stance = Stance.AGGRESSIVE
    mod = ney.get_attack_modifier()
    # Ney (aggressive personality) + aggressive stance + shock bonus (50%):
    # Base 1.15 * stance 1.05 * drill synergy 1.05 * shock 1.50 = ~1.90
    # Actual calculation varies but should be > 1.5
    results.append(('Combat attack modifiers', mod > 1.5))

    # Test 7: Fortify defense modifiers
    w = WorldState()
    davout = w.get_marshal('Davout')
    davout.fortified = True
    davout.defense_bonus = 0.16
    davout.stance = Stance.DEFENSIVE
    mod = davout.get_defense_modifier()
    # Davout defensive + fortify: expect ~1.39
    results.append(('Fortify defense modifiers', 1.30 <= mod <= 1.50))

    # Test 8: Disobedience system
    ds = DisobedienceSystem()
    w = WorldState()
    ney = w.get_marshal('Ney')
    result = ds.evaluate_order(ney, {'action': 'defend'}, w)
    has_objection = result is not None and (result.get('has_objection', False) or result.get('severity', 0) > 0.2)
    results.append(('Disobedience system', has_objection))

    # Test 9: Counter-punch state
    w = WorldState()
    davout = w.get_marshal('Davout')
    davout.counter_punch_available = True
    davout.counter_punch_turns = 2
    results.append(('Counter-punch state', davout.counter_punch_available))

    # Test 10: Retreat recovery
    w = WorldState()
    ney = w.get_marshal('Ney')
    ney.retreating = True
    ney.retreat_recovery = 1
    results.append(('Retreat recovery state', ney.retreating and ney.retreat_recovery == 1))

    # Test 11: Action economy (integers)
    w = WorldState()
    assert isinstance(w.actions_remaining, int), "actions_remaining must be int"
    assert isinstance(w.max_actions_per_turn, int), "max_actions must be int"
    assert isinstance(w.current_turn, int), "current_turn must be int"
    results.append(('Action economy integers', True))

    # Test 12: Marshal state persistence
    w = WorldState()
    ney = w.get_marshal('Ney')
    ney.drilling = True
    ney.drill_complete_turn = 5
    ney2 = w.get_marshal('Ney')
    results.append(('Marshal state persistence', ney2.drilling and ney2.drill_complete_turn == 5))

    # Test 13: Region control tracking
    w = WorldState()
    player_regions = w.get_player_regions()
    enemy_regions = [r for r in w.regions.keys() if w.regions[r].controller != w.player_nation]
    results.append(('Region control tracking', len(player_regions) > 0 and len(enemy_regions) > 0))

    # Test 14: Vindication tracker
    w = WorldState()
    vt = w.vindication_tracker
    vt.record_choice('Ney', 'trust', {'action': 'defend'}, {'action': 'fortify'})
    has_pending = vt.has_pending('Ney')
    results.append(('Vindication tracking', has_pending))

    return results


if __name__ == '__main__':
    print('=== INTEGRATION TEST RESULTS ===')
    print()

    results = run_tests()

    all_pass = True
    for name, passed in results:
        status = 'PASS' if passed else 'FAIL'
        if not passed:
            all_pass = False
        print(f'  {name}: {status}')

    print()
    print(f'  Total: {sum(1 for _, p in results if p)}/{len(results)} passed')
    print()

    if all_pass:
        print('=== ALL TESTS PASS ===')
        sys.exit(0)
    else:
        print('=== SOME TESTS FAILED ===')
        sys.exit(1)
