# Ink & Iron: Completed Systems

> **Reference for done features. How things work.**  
> **Last Updated:** January 30, 2026

---

## Quick Reference

| System | Phase | Tests | Key File |
|--------|-------|-------|----------|
| Strategic Commands | 5.2 | ~350 | `commands/strategic.py` |
| Grouchy/Literal | 5.2 | ~30 | `executor.py` |
| Modding | 5.2 | 66 | `modding/validator.py` |
| Serialization | 5.2 | 45 | `marshal.py`, `world_state.py` |
| Tactical Feedback | 5.1 | 64 | `ai/feedback.py` |
| Enemy AI | 2 + 5.3 | 91 | `ai/enemy_ai.py` |
| Disobedience | 2 | ~30 | `disobedience.py` |
| Combat | 1-2 | ~40 | `game_logic/combat.py` |
| LLM Integration | 4 | ~60 | `ai/llm_client.py` |

---

## Strategic Commands ✅ (Phase 5.2)

### The 4 Command Types

| Command | Purpose | Completion |
|---------|---------|------------|
| MOVE_TO | March to distant region or marshal | Arrival |
| PURSUE | Chase and attack enemy | Target destroyed |
| HOLD | Defend position | Condition met or cancelled |
| SUPPORT | Follow and assist ally | Ally safe or battle won |

### Personality Behaviors

| Command | Aggressive | Cautious | Literal |
|---------|------------|----------|---------|
| Blocked path | Auto-attack | Ask player | Reroute silently |
| Cannon fire | Rush to join! | Ask player | **IGNORE** |
| HOLD behavior | Sally out, return | Fortify | Immovable (+15%) |

### Interrupt System

| Interrupt | Trigger | Options |
|-----------|---------|---------|
| cannon_fire | Battle within 2 regions | investigate, continue, hold |
| blocked_path | Enemy in path | attack, go_around, hold, cancel |
| ally_moving | SUPPORT target moves | follow, hold_current, cancel |

### Cancel System

| Timing | Trust Penalty |
|--------|---------------|
| First step (same turn) | 0 |
| Mid-march (after movement) | -3 |

**Keywords:** "halt", "stop", "cancel", "abort", "stand down"

---

## Grouchy (Literal Personality) ✅

**Core:** Grouchy argues about CLARITY, not tactics.

### Ambiguity Buffs

| Ambiguity | Combat Buff |
|-----------|-------------|
| 0-20 | +15% (crystal clear) |
| 21-40 | +10% (clear) |
| 41-60 | +5% (somewhat vague) |
| 61+ | 0% (clarification popup) |

### Precision Execution
- **Trigger:** ambiguity ≤20, strategic_score > 60, literal personality
- **Effect:** +1 to ALL skills for 3 turns

### The Grouchy Moment
**Literal personality NEVER interrupts for cannon fire.** Even when Waterloo erupts nearby, Grouchy continues his orders exactly.

---

## Modding System ✅ (Phase 5.2)

### Usage

```bash
# Validate mod
python -m backend.modding.validator path/to/mod.json

# Load scenario
world = WorldState.from_scenario("path/to/scenario.json")
```

### Minimal Marshal JSON

```json
{
  "name": "Murat",
  "nation": "France",
  "location": "Paris"
}
```

All other fields have defaults.

**Docs:** `docs/MODDING_FORMAT.md`, `docs/SAVE_FORMAT_REFERENCE.md`

---

## Enemy AI Priority System ✅

| Priority | Situation | Score |
|----------|-----------|-------|
| P0 | Combat engagement | 50 |
| P1 | Escape needed | 60 |
| P2 | Crush opportunity (2:1) | 70 |
| P3 | Attack opportunity | 75 |
| P3.5 | Fortification opportunity | 77 |
| P4.5 | Undefended capture | 80 |
| P4.6 | Consolidate with allies | 78 |
| P5 | Standard positioning | 85 |
| P6 | Drill | 90 |
| P7 | Move toward enemy | 92 |
| P8 | Tactical fallback | 95 |

### Features
- `_marshals_done_this_turn` — Prevents monopolization
- Critical override (≤60) skips round-robin
- Graduated stagnation counter (5.3)

---

## Disobedience System ✅ (Phase 2)

### Player Choices

| Choice | Trust | Authority | Outcome |
|--------|-------|-----------|---------|
| Trust | +12 | -3 | Marshal's alternative |
| Insist | -10 | +2 | Original (may disobey) |
| Compromise | +3 | -1 | Middle ground |

### Redemption (Trust ≤20)

| Option | Effect |
|--------|--------|
| Grant Autonomy | 3 turns AI-controlled |
| Administrative | Sidelined, +1 action/turn |
| Dismiss | Gone, +10 authority |

---

## Combat System ✅ (Phase 1-2)

### Dice Mechanics

```
Base roll: 2d6
Attacker: roll + tactical + shock + stance + recklessness - exhaustion
Defender: roll + tactical + defense + stance + terrain (+20% defender bonus)
Critical: 12 = +50% damage, 2 = -50% damage
```

### Cavalry Recklessness

| Level | Attack | Defense |
|-------|--------|---------|
| 0 | - | - |
| 1 | +10% | -5% |
| 2 | +20% | -10% |
| 3 | +30% | -15% |
| 4 | +30% | -20% (auto-charge) |

**+1 on attack victory, reset on loss or Glorious Charge**

---

## Tactical Feedback ✅ (Phase 5.1)

### Strategic Score Bonuses

| Score | Effect |
|-------|--------|
| 51+ | +3 morale |
| 76+ | +2 trust |
| 90+ | +5% combat bonus |

### Repetition Penalty
- Exact repeat within 5 turns: -20 score
- Similar command: -10 score

---

## LLM Integration ✅ (Phase 4)

### Modes
- `mock`: Fast parser only (free)
- `anthropic`: Haiku fallback for low confidence

### Architecture
1. Fast Parser (keywords, confidence 0-1)
2. LLM Fallback (Haiku for parsing)
3. Sonnet for personality dialogue

---

## Fuzzy Matching ✅ (Phase 5.2)

| Score | Behavior |
|-------|----------|
| 80+ | Auto-correct silently |
| 60-79 | Suggest correction |
| <60 | Error |

**Coverage:** Parser, executor, strategic parser

---

## Serialization ✅ (Phase 5.2)

**Every field must serialize.** Tests auto-fail if field missing from `to_dict()` or `from_dict()`.

### Enforced Classes
- Marshal (50+ fields)
- StrategicOrder
- StrategicCondition
- WorldState
- Region
- Trust
- AuthorityTracker
- VindicationTracker
