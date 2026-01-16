# CLAUDE CODE PROMPT: Disobedience System Implementation

## Context
You are implementing the Disobedience System for Project Sovereign, a Napoleonic Wars strategy game. This is the CORE INNOVATION that differentiates the game - marshals negotiate orders rather than randomly disobeying.

Read `/mnt/project/DISOBEDIENCE_SYSTEM_V2.md` for complete design spec.

## Golden Rule
> "LLMs explain, react, and color events — they don't cause them."

This is Phase 2 (Mock Mode) - NO LLM API calls. All logic is deterministic with weighted randomness.

---

## Implementation Tasks

### Task 1: Core Data Structures (`backend/models/`)

Create or update the following:

#### `trust.py` - Trust System
```python
class Trust:
    """Marshal trust in player (0-100)."""
    
    def __init__(self, value: int = 70):
        self._value = max(0, min(100, value))
    
    @property
    def value(self) -> int:
        return self._value
    
    def modify(self, delta: int) -> int:
        """Modify trust, return actual change."""
        old = self._value
        self._value = max(0, min(100, self._value + delta))
        return self._value - old
    
    def get_label(self) -> str:
        """Human-readable trust level."""
        if self._value >= 81: return "Loyal"
        if self._value >= 61: return "Reliable"
        if self._value >= 41: return "Questioning"
        if self._value >= 21: return "Strained"
        return "Broken"


def calculate_obedience_chance(trust_value: int) -> float:
    """
    Non-linear obedience curve.
    
    Trust 80+ = 100% obey
    Trust 60-79 = 90-99% obey
    Trust 40-59 = 70-89% obey
    Trust 20-39 = 40-69% obey
    Trust <20 = 20-39% obey
    """
    if trust_value >= 80:
        return 1.0
    elif trust_value >= 60:
        return 0.90 + (trust_value - 60) * 0.005
    elif trust_value >= 40:
        return 0.70 + (trust_value - 40) * 0.01
    elif trust_value >= 20:
        return 0.40 + (trust_value - 20) * 0.015
    else:
        return 0.20 + trust_value * 0.01
```

#### `authority.py` - Authority Tracker (Anti-Sycophancy)
```python
class AuthorityTracker:
    """
    Tracks Napoleon's perceived authority.
    
    Prevents "always trust marshals" exploit.
    """
    
    def __init__(self):
        self.authority = 100  # Napoleon starts authoritative
        self.recent_responses = []  # Last 10 responses
    
    def record_response(self, choice: str):
        """Record 'trust', 'insist', or 'compromise'."""
        self.recent_responses.append(choice)
        if len(self.recent_responses) > 10:
            self.recent_responses.pop(0)
        self._evaluate_authority()
    
    def _evaluate_authority(self):
        if len(self.recent_responses) < 5:
            return
        
        trust_ratio = self.recent_responses.count('trust') / len(self.recent_responses)
        
        if trust_ratio > 0.80:
            self.authority = max(0, self.authority - 5)
        elif trust_ratio > 0.60:
            self.authority = max(0, self.authority - 2)
        elif 0.30 <= trust_ratio <= 0.60:
            self.authority = min(100, self.authority + 1)
    
    def get_trust_gain_modifier(self) -> float:
        if len(self.recent_responses) < 5:
            return 1.0
        trust_ratio = self.recent_responses.count('trust') / len(self.recent_responses)
        if trust_ratio > 0.80:
            return 0.5
        elif trust_ratio > 0.60:
            return 0.75
        return 1.0
    
    def get_obedience_modifier(self) -> float:
        if self.authority >= 80:
            return 1.1
        elif self.authority >= 50:
            return 1.0
        else:
            return 0.9
    
    def check_events(self) -> Optional[dict]:
        """Check for authority threshold events."""
        # Implementation: return event dicts at 70, 50, 30 thresholds
        pass
```

#### Update `marshal.py` - Add New Fields
```python
# Add to Marshal class:
self.trust = Trust(starting_trust)
self.vindication_score = 0  # -5 to +5
self.recent_battles = []  # Last 3 battle results
self.recent_overrides = []  # Last 5 override events
```

### Task 2: Personality System (`backend/models/personality.py`)

```python
from enum import Enum

class Personality(Enum):
    AGGRESSIVE = "aggressive"
    CAUTIOUS = "cautious"
    LITERAL = "literal"
    BALANCED = "balanced"
    LOYAL = "loyal"


PERSONALITY_TRIGGERS = {
    Personality.AGGRESSIVE: {
        'defend': 0.60,  # Base severity for defend orders
        'wait_with_enemy': 0.55,
    },
    Personality.CAUTIOUS: {
        'attack_outnumbered_2to1': 0.70,
        'attack_outnumbered_1.5to1': 0.45,
    },
    Personality.LITERAL: {
        'ambiguous_order': 0.40,
    },
    Personality.BALANCED: {
        'expose_capital': 0.50,
        'suicidal_order': 0.65,
    },
    Personality.LOYAL: {
        'suicidal_order': 0.40,
    },
}
```

### Task 3: Severity Calculator (`backend/commands/severity.py`)

Implement `calculate_objection_severity()` exactly as specified in design doc:
- Base severity from personality triggers
- Multiplicative modifiers: trust, vindication, performance, overrides
- Tiered variance (±3%, ±8%, ±12% based on severity level)
- Cap at 0.95

### Task 4: Objection Handler (`backend/commands/disobedience.py`)

```python
class DisobedienceSystem:
    MAX_MAJOR_OBJECTIONS_PER_TURN = 2
    
    def evaluate_order(self, marshal, order, game_state) -> Optional[dict]:
        """
        Evaluate order for objection.
        
        Returns:
            None - No objection
            dict with type='mild_objection' - Auto-resolve
            dict with type='major_objection' - Player choice required
        """
        severity = calculate_objection_severity(marshal, order, game_state)
        
        if severity < 0.20:
            return None
        elif severity < 0.50:
            return self._create_mild_objection(marshal, order, severity)
        else:
            return self._create_major_objection(marshal, order, severity, game_state)
    
    def _create_major_objection(self, marshal, order, severity, game_state):
        """Create major objection with player options."""
        alternative = self._generate_alternative(marshal, order, game_state)
        
        return {
            'type': 'major_objection',
            'marshal': marshal.name,
            'severity': severity,
            'original_order': order,
            'suggested_alternative': alternative,
            'message': self._generate_objection_message(marshal, order, alternative),
            'options': [
                {'id': 'trust', 'text': f"Trust {marshal.name}'s judgment"},
                {'id': 'insist', 'text': "Proceed as ordered"},
                {'id': 'compromise', 'text': "Find middle ground"},
            ]
        }
    
    def handle_response(self, objection, choice, game_state) -> dict:
        """Process player response to objection."""
        # Implement trust/insist/compromise handlers
        # Update authority tracker
        # Set up vindication tracking for post-battle
        pass


COMPROMISE_RULES = {
    ('defend', 'attack'): {'action': 'probe'},
    ('attack', 'defend'): {'action': 'hold'},
    ('move', 'attack'): {'action': 'advance'},
    ('wait', 'attack'): {'action': 'patrol'},
    ('attack', 'wait'): {'action': 'probe'},
}
```

### Task 5: Vindication Tracker (`backend/commands/vindication.py`)

```python
class VindicationTracker:
    """Track objection outcomes for marshal credibility."""
    
    def __init__(self):
        self.pending = {}  # marshal_name -> {choice, order}
    
    def record_choice(self, marshal_name: str, choice: str, order: dict):
        """Record player's choice for later vindication check."""
        self.pending[marshal_name] = {'choice': choice, 'order': order}
    
    def resolve_battle(self, marshal_name: str, result: str, game_state):
        """
        Called after battle to update vindication.
        
        Args:
            marshal_name: Marshal who fought
            result: 'victory', 'defeat', 'draw'
            game_state: Current game state
        """
        if marshal_name not in self.pending:
            return
        
        pending = self.pending.pop(marshal_name)
        marshal = game_state.world.get_marshal(marshal_name)
        authority = game_state.authority_tracker
        
        if pending['choice'] == 'trust':
            if result == 'victory':
                marshal.vindication_score = min(5, marshal.vindication_score + 1)
                marshal.trust.modify(+3)
            elif result == 'defeat':
                marshal.vindication_score = max(-5, marshal.vindication_score - 1)
        
        elif pending['choice'] == 'insist':
            if result == 'victory':
                marshal.vindication_score = max(-5, marshal.vindication_score - 1)
                authority.authority = min(100, authority.authority + 5)
            elif result == 'defeat':
                marshal.vindication_score = min(5, marshal.vindication_score + 1)
                authority.authority = max(0, authority.authority - 5)
```

### Task 6: Integration

Update `executor.py` to:
1. Call `disobedience_system.evaluate_order()` before execution
2. If major objection, return response requiring player choice
3. Process player choice via `handle_response()`
4. After battles, call `vindication_tracker.resolve_battle()`

Update `world_state.py` to:
1. Add `authority_tracker: AuthorityTracker` field
2. Add `vindication_tracker: VindicationTracker` field
3. Initialize both in constructor

---

## Testing Requirements

Create `tests/test_disobedience.py`:

```python
def test_severity_aggressive_defend():
    """Ney objects to defensive orders."""
    ney = create_marshal('Ney', personality='aggressive', trust=70)
    order = {'action': 'defend'}
    severity = calculate_objection_severity(ney, order, game_state)
    assert 0.55 <= severity <= 0.65  # Base 0.60 ± variance

def test_obedience_curve_reliable():
    """Trust 70 should give ~95% obedience."""
    chance = calculate_obedience_chance(70)
    assert 0.93 <= chance <= 0.97

def test_authority_sycophant_penalty():
    """Always trusting should reduce trust gains."""
    tracker = AuthorityTracker()
    for _ in range(8):
        tracker.record_response('trust')
    assert tracker.get_trust_gain_modifier() < 1.0

def test_vindication_updates():
    """Marshal vindication changes on battle outcome."""
    marshal = create_marshal('Ney', vindication=0)
    tracker = VindicationTracker()
    tracker.record_choice('Ney', 'trust', {'action': 'attack'})
    tracker.resolve_battle('Ney', 'victory', game_state)
    assert marshal.vindication_score == 1

def test_objection_cap():
    """Max 2 major objections per turn."""
    orders = [create_conflicting_order() for _ in range(5)]
    results = process_turn_orders(orders, game_state)
    major = [r for r in results if r.get('type') == 'awaiting_player_choice']
    assert len(major) <= 2
```

---

## File Structure

```
backend/
  models/
    trust.py           # NEW: Trust class, obedience curve
    authority.py       # NEW: AuthorityTracker
    personality.py     # NEW: Personality enum, triggers
    marshal.py         # UPDATE: Add trust, vindication fields
    world_state.py     # UPDATE: Add authority/vindication trackers
  
  commands/
    severity.py        # NEW: Severity calculation
    disobedience.py    # NEW: DisobedienceSystem class
    vindication.py     # NEW: VindicationTracker
    executor.py        # UPDATE: Integrate disobedience check

tests/
  test_disobedience.py # NEW: All disobedience tests
  test_trust.py        # NEW: Trust/obedience tests
  test_authority.py    # NEW: Authority system tests
```

---

## Critical Notes

1. **INT WRAPPING**: All API responses must use `int()` for Godot
2. **PORT 8005**: FastAPI runs on 8005, not 8000
3. **EXECUTOR PATTERN**: All state changes go through executor
4. **NO LLM CALLS**: This is Phase 2 - all mock/template based

## Success Criteria

- [ ] Severity calculation matches design spec
- [ ] Obedience curve is non-linear (trust 70 ≈ 95% obey)
- [ ] Authority drops when player always trusts
- [ ] Vindication updates after battles
- [ ] Max 2 major objections per turn
- [ ] All tests pass
- [ ] Integration with existing command flow works

---

*Implementation target: 7 days. Use Opus for initial architecture, Sonnet for iteration.*