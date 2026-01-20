# Project Sovereign - External Reference

**Purpose:** Context document for external Claude chats working on this project.

---

## What Is This Game?

A **Napoleonic strategy game** where you command French marshals through **natural language**.

```
Instead of:     You type:
[Click army]    "Marshal Ney, attack Wellington"
[Click move]    "Davout, move to Belgium"
[Click menu]    "What's the situation?"
```

**Core Innovation:** Marshals have personalities. They can **object, question, or disobey** based on their traits.

---

## Current State (January 2025)

### FULLY IMPLEMENTED (Working Code)

| System | Status | Key Files |
|--------|--------|-----------|
| Combat resolution | ✅ Complete | `combat.py`, `marshal.py` |
| Combat modifiers | ✅ Complete | Personality-based attack/defense bonuses |
| Disobedience system | ✅ Complete | `disobedience.py` - marshals object to orders |
| Trust/Authority | ✅ Complete | Affects objection probability |
| Action economy | ✅ Complete | 4 actions/turn |
| Drill mechanic | ✅ Complete | +50% shock bonus, consumed on attack |
| Fortify mechanic | ✅ Complete | +2-3%/turn defense, personality caps |
| Cavalry limits | ✅ Complete | 3-turn max defensive stance/fortify |
| Retreat system | ✅ Complete | Forced at 25% morale, recovery period |
| Victory/Defeat | ✅ Complete | Win conditions checked each turn |
| 13-region map | ✅ Complete | Simplified Western Europe |
| FastAPI backend | ✅ Complete | Port 8005 |
| Godot 4 frontend | ✅ Complete | Terminal-style UI |
| **Enemy AI** | ✅ Complete | `enemy_ai.py` - personality-driven decisions |
| **Enemy Phase Popup** | ✅ Complete | `enemy_phase_dialog.gd` - modal with battle details |
| **Attacker Movement** | ✅ Complete | Attacker advances into captured region |
| **AI Safety Evaluation** | ✅ Complete | Encirclement check before captures |

### NOT YET IMPLEMENTED

| System | Priority | Notes |
|--------|----------|-------|
| LLM command parsing | Medium | Using keyword matching currently |
| LLM marshal responses | Medium | Personality dialogue |
| Diplomacy | Medium | Peace, alliances, betrayal |
| Enemy recruiting | Medium | Requires economy system |
| Region fortifications | Low (EA) | Buildings that slow capture |
| Full Europe map | Low (EA) | 200-400 provinces |
| Supply/Logistics | Low (EA) | Attrition system |
| Coalition system | Low (EA) | Dynamic alliances |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     COMMAND FLOW                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  PLAYER TURN:                                                │
│  User Input                                                  │
│      │                                                       │
│      ▼                                                       │
│  LLMClient (parser) ─── Currently mock keyword matching      │
│      │                                                       │
│      ▼                                                       │
│  CommandParser ──────── Validates marshal, action, target    │
│      │                                                       │
│      ▼                                                       │
│  Disobedience Check ─── Marshal may object based on          │
│      │                  personality + authority              │
│      │                                                       │
│      ▼                                                       │
│  CommandExecutor ────── _execute_attack(), _execute_move()   │
│      │                  Same executor for player AND enemy   │
│      │                                                       │
│      ▼                                                       │
│  WorldState ─────────── Central game state                   │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ENEMY TURN (after player ends turn):                        │
│                                                              │
│  EnemyAI.process_nation_turn()                               │
│      │                                                       │
│      ▼                                                       │
│  Decision Tree ──────── Priority-based action selection      │
│      │                  (P1-P8: recovery, survival, attack)  │
│      │                                                       │
│      ▼                                                       │
│  CommandExecutor ────── SAME executor as player!             │
│      │                  No special enemy code                │
│      │                                                       │
│      ▼                                                       │
│  WorldState ─────────── Same state, same rules               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Design Principles

### 1. Single Source of Truth (Combat)
```
marshal.py          combat.py
─────────────       ─────────────────
Calculates          Uses the modifier
modifiers           Generates messages
                    NEVER recalculates
```

### 2. Building Blocks (Actions)
All actions (player AND enemy) go through same executor:
```python
executor.execute({"marshal": "Ney", "action": "attack", "target": "Wellington"})
executor.execute({"marshal": "Wellington", "action": "attack", "target": "Ney"})
# Same code path!
```

### 3. Unified Marshal Storage
```python
world.marshals = {
    "Ney": ...,        # Player
    "Davout": ...,     # Player
    "Wellington": ..., # Enemy
    "Blucher": ...     # Enemy
}
# NOT separate dicts!
```

### 4. Type Safety for Godot
```python
return {"value": int(some_float)}  # Always wrap numbers
```

---

## Marshal Personalities

| Marshal | Type | Combat Style | Objection Triggers |
|---------|------|--------------|-------------------|
| Ney | AGGRESSIVE | +15% attack, -5% defense | Defend, fortify, wait |
| Davout | CAUTIOUS | +20% defense when outnumbered | Risky attacks |
| Grouchy | LITERAL | +15% when holding position | Ambiguous orders |
| Wellington | CAUTIOUS | Defensive specialist | (Enemy) |
| Blucher | AGGRESSIVE | Attacks often | (Enemy) |

---

## File Structure

```
backend/
├── models/
│   ├── marshal.py          ← Combat modifiers HERE
│   ├── world_state.py      ← Game state, turn processing
│   ├── region.py           ← 13 regions with adjacency
│   └── personality.py      ← Personality types
├── game_logic/
│   ├── combat.py           ← Battle resolution
│   └── turn_manager.py     ← Turn flow, enemy AI calls, victory check
├── commands/
│   ├── executor.py         ← Action handlers (player AND enemy)
│   ├── parser.py           ← Command parsing
│   └── disobedience.py     ← Objection system (player only)
└── ai/
    ├── llm_client.py       ← Mock parser (real LLM later)
    └── enemy_ai.py         ← Enemy AI decision tree

docs/
├── ENEMY_AI_REFERENCE.md   ← Full AI documentation
├── DISOBEDIENCE_SYSTEM_REFERENCE.md
└── UI_TODO.md              ← Enemy Phase Popup requirements

godot-client/
└── project-sovereign/
    └── scripts/
        └── main.gd         ← Terminal UI, API calls
```

---

## Vision: Early Access (Future)

### Full Europe Map
- 200-400 provinces (EU4 style)
- Historical 1805 borders
- Terrain effects (mountains, rivers)

### Campaign Scope
- 1805-1815 timeline
- Monthly turns (120 total)
- Historical events

### Enhanced Systems
- Supply lines and attrition
- Coalition formation
- Diplomacy with AI nations
- Marshal death/replacement
- Naval abstraction (no ship combat)

---

## Enemy AI System (Implemented)

### How It Works
1. Player ends turn -> `turn_manager.end_turn()`
2. `_process_enemy_turns()` iterates through `world.enemy_nations`
3. `EnemyAI.process_nation_turn()` picks best actions via decision tree
4. Actions executed through SAME executor as player
5. Results returned in `enemy_phase` dict

### Decision Tree Priorities
| Priority | Check | Example |
|----------|-------|---------|
| P1 | Retreat Recovery | Limited actions during recovery |
| P2 | Critical Survival | Retreat if strength < 25% |
| P3 | Threat Response | Fortify if stronger enemy adjacent |
| P4 | Attack Opportunity | Attack if ratio meets threshold |
| P4.5 | Capture Undefended | Attack adjacent undefended enemy region |
| P5 | Fortification | Cautious marshals fortify |
| P6 | Drilling | Aggressive marshals drill |
| P7 | Strategic Movement | Move toward enemy |
| P8 | Default | Stance adjustment or wait |

### Personality Thresholds
| Personality | Attack Threshold | Behavior |
|-------------|------------------|----------|
| Wellington (Cautious) | 1.3 | Only attacks with 30% advantage |
| Blucher (Aggressive) | 0.7 | Attacks even when outnumbered |

### Key Files
- `backend/ai/enemy_ai.py` - Decision tree and action selection
- `backend/game_logic/turn_manager.py` - `_process_enemy_turns()` integration
- `docs/ENEMY_AI_REFERENCE.md` - Full technical documentation

---

## Quick Test Commands

```bash
# Run backend
python backend/main.py

# Test combat math
python backend/game_logic/combat.py

# Test turn manager
python backend/game_logic/turn_manager.py

# Full test suite
pytest test_conquest_comprehensive.py -v
```

---

## Common Pitfalls

| Problem | Cause | Solution |
|---------|-------|----------|
| Modifier applied twice | Calculated in marshal.py AND combat.py | Only calculate in marshal.py |
| Godot type error | Returning float | Wrap with `int()` |
| Enemy not found | Separate marshal dicts | Use unified `world.marshals` |
| State read as 0 | Cleared before reading | Clear AFTER using value |

---

*Last updated: January 2025*
*For full details, see CLAUDE.md in the repository*
