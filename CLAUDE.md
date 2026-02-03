# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Reference (Read This First!)

```
MOST IMPORTANT FILES:
├── backend/models/marshal.py        ← Combat modifiers calculated HERE ONLY
├── backend/game_logic/combat.py     ← Combat resolution, messages (not modifiers!)
├── backend/commands/executor.py     ← Action handlers (_execute_*)
├── backend/models/world_state.py    ← Game state, turn processing
├── backend/commands/disobedience.py ← Objection system, trust values
├── backend/ai/enemy_ai.py           ← Enemy AI decision tree (P1-P8 priorities)
└── backend/ai/llm_client.py         ← LLM command parsing (fast parser + Anthropic)

LLM INTEGRATION FILES (Phase 4):
├── backend/ai/llm_client.py         ← Main entry: fast parser + LLM fallback
├── backend/ai/providers.py          ← Anthropic HTTP, Groq stub
├── backend/ai/validation.py         ← Catches hallucinations
├── backend/ai/prompt_builder.py     ← Context-aware prompts
├── backend/ai/schemas.py            ← ParseResult dataclass
├── backend/ai/feedback.py           ← Phase 5: Score→narrative text
└── backend/ai/README.md             ← Full LLM documentation

FEEDBACK DATA FLOW (Phase 5) - CRITICAL:
  LLMClient.parse_command() → ParseResult.to_dict() includes:
    - strategic_score (0-100)
    - ambiguity (0-100)
    - mode ("mock" | "live")

  parser.parse() MUST copy these to top-level return dict!
  main.py reads them for feedback generation.

  If feedback doesn't appear: check parser.py return dict construction.

GOLDEN RULES:
1. Combat modifiers: SINGLE SOURCE OF TRUTH in marshal.py
2. All numbers to Godot: wrap with int()
3. All marshals in ONE dict: world.marshals (not separate player/enemy)
4. State clearing: AFTER reading the value, not before
5. Enemy AI uses SAME executor as player (Building Blocks principle)
6. LLM never affects game mechanics: Parsing only, executor is deterministic

CURRENT PHASE: Phase 5.2 (Strategic Commands) 🔄 → Phase 3 (Fun Factor) 📋 NEXT
- Phase 1 ✅: Foundation (regions, marshals, combat, actions, turns)
- Phase 2 ✅: Combat & AI (disobedience, drill/fortify, Enemy AI, safety eval)
- Phase 2.5 ✅: Autonomy (AI control, narrative outcomes, admin role)
- Phase 2.9 ✅: Retreat System (ally cover, smart destination, AI targeting)
- Phase 4 ✅: LLM Integration (fast parser, Anthropic fallback, BYOK, validation)
- Phase 3 📋: Fun Factor (hearing guns, vindication, anti-tedium, pressure)
- Phase 5.2 🔄: Strategic Commands (MOVE_TO, PURSUE, HOLD, SUPPORT) - Phase A-I ✅, Phase J-K remaining
- Not implemented: diplomacy, supply lines (see Phase 5-6)
```

---

## Project Overview

Project Sovereign is a strategic turn-based military conquest game set in Napoleonic Western Europe. Players control France and manage marshals (Ney, Davout, Grouchy) to conquer 13 regions while managing an action economy system. Features natural language command parsing via Claude API (with mock fallback) and a Godot 4 frontend with FastAPI backend.

**Core Innovation:** Players don't click armies—they type commands like "Marshal Ney, attack Wellington" and AI marshals respond, question, or even disobey based on their personality.

## Commands

### Running the Backend
```bash
python backend/main.py
# FastAPI runs on http://127.0.0.1:8005 (NOT 8000!)
```

### Running Tests
```bash
pytest test_conquest_comprehensive.py -v  # Comprehensive gameplay test
python test_integration.py                 # System integration tests (14 tests)
```

### Testing Individual Modules
```bash
python backend/models/world_state.py
python backend/game_logic/combat.py
python backend/commands/parser.py
```

### Running the Frontend
Open `godot-client/project-sovereign/` in Godot 4 editor.

## Architecture

### Command Processing Pipeline
```
User Input → LLMClient → CommandParser → CommandExecutor → WorldState
```

1. **LLMClient** (`backend/ai/llm_client.py`): Parses natural language using mock keyword matching (default) or Claude API
2. **CommandParser** (`backend/commands/parser.py`): Converts NL to structured commands, validates marshals and actions
3. **CommandExecutor** (`backend/commands/executor.py`): Routes commands to action handlers, manages action economy
4. **WorldState** (`backend/models/world_state.py`): Central game state container

### Core Models (`backend/models/`)
- **WorldState**: Game state container, action economy, income calculation, BFS pathfinding
- **Region**: Territory model with 13 hardcoded regions, adjacency, income values
- **Marshal**: Commander with army strength, personality traits (aggressive/cautious/literal), morale

### Game Logic (`backend/game_logic/`)
- **CombatResolver** (`combat.py`): Deterministic battle system with morale multipliers, terrain modifiers, defender bonus (+20%)
- **TurnManager** (`turn_manager.py`): Turn progression, victory conditions (≥8 regions by turn 40 or all 13)

### Disobedience System (`backend/commands/disobedience.py`, `backend/models/personality.py`)

Marshals can object to orders based on their personality. This is the core innovation of the game.

**Personality Types:**
| Type | Objection Triggers | Examples |
|------|-------------------|----------|
| AGGRESSIVE | defend, wait, hold, retreat, fortify, drill (with enemy nearby), defensive stance | Ney, Murat |
| CAUTIOUS | risky attacks (outnumbered), aggressive stance, attacking fortified positions | Davout, Wellington |
| LITERAL | ambiguous orders, contradictory orders (Phase 3) | Grouchy |
| BALANCED | suicidal orders (3:1+ odds), exposing capital | Soult |
| LOYAL | only extreme cases (5:1+ odds, betraying emperor) | Lannes |

**Objection Actions:** Only these actions trigger objection checks:
```python
objection_actions = ["attack", "defend", "move", "scout", "recruit", "fortify",
                     "stance_change", "retreat", "drill", "wait", "hold"]
```

**Context-Aware Objections:**
- Retreat: Aggressive marshals object UNLESS outnumbered 2:1+ AND morale ≤40%
- Wait/Hold: Objection severity increases if enemy is nearby
- Attack: Cautious marshals' objection scales with odds (1.5:1, 2:1, 3:1, 5:1+)

**Retreat Recovery State:**
When a marshal retreats (forced or ordered), they enter recovery:
- **Blocked actions:** attack, fortify, drill, scout, aggressive_stance
- **Allowed actions:** move, wait, recruit, defend, defensive_stance, neutral_stance
- **No objections during recovery** - marshals are demoralized and compliant
- Recovery lasts 3 turns (decrements each turn)

**Forced Retreats:** Happen automatically when morale drops to 25% in combat. These bypass the objection system entirely since they're not player-ordered.

### Disobedience Decision Flowchart

```
Player issues command
        │
        ▼
┌───────────────────────┐
│ Is action in          │
│ objection_actions[]?  │
└───────────────────────┘
        │
   NO   │   YES
   ▼    │    ▼
Execute │  ┌───────────────────────┐
directly│  │ Is marshal in         │
        │  │ retreat_recovery?     │
        │  └───────────────────────┘
        │          │
        │     YES  │  NO
        │      ▼   │   ▼
        │   Execute│  ┌───────────────────────┐
        │   (no    │  │ Calculate objection   │
        │   check) │  │ probability:          │
        │          │  │ base_rate × personality│
        │          │  │ × context × (1-auth%) │
        │          │  └───────────────────────┘
        │          │           │
        │          │           ▼
        │          │  ┌───────────────────────┐
        │          │  │ Roll vs probability   │
        │          │  └───────────────────────┘
        │          │      │           │
        │          │  PASS│       FAIL│
        │          │      ▼           ▼
        │          │   Execute    ┌───────────────────────┐
        │          │              │ Marshal OBJECTS       │
        │          │              │ Player chooses:       │
        │          │              │ • Accept (+12 trust)  │
        │          │              │ • Insist (-10/-15)    │
        │          │              │ • Compromise (+3)     │
        │          │              └───────────────────────┘
```

**Key insight:** Authority reduces objection PROBABILITY, it never makes objection impossible. Even at 100 authority, there's still a small chance.

### Marshal State Machine

```
                    ┌─────────────────────────────────────────────────────────┐
                    │                    MARSHAL STATES                        │
                    │  (Multiple states can be active simultaneously)          │
                    └─────────────────────────────────────────────────────────┘

┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   STANCE    │     │  TACTICAL   │     │  RECOVERY   │     │   COMBAT    │
│  (1 of 3)   │     │  (flags)    │     │  (blocking) │     │  (temp)     │
├─────────────┤     ├─────────────┤     ├─────────────┤     ├─────────────┤
│ AGGRESSIVE  │     │ fortified   │     │ retreat_    │     │ broken      │
│ NEUTRAL     │     │ drilling    │     │ recovery=N  │     │ (morale<25%)│
│ DEFENSIVE   │     │ drilling_   │     │ (blocks     │     │             │
│             │     │   locked    │     │  attack,    │     │ Triggers    │
│ Affects:    │     │ holding_    │     │  fortify,   │     │ forced      │
│ -attack mod │     │   position  │     │  drill,     │     │ retreat     │
│ -defense mod│     │             │     │  scout,     │     │             │
│             │     │ Affects:    │     │  aggr.stance│     │             │
│             │     │ -defense    │     │             │     │             │
│             │     │ -attack     │     │ Decrements  │     │             │
│             │     │ -mobility   │     │ each turn   │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘

CAVALRY-SPECIFIC COUNTERS (only for cavalry=True marshals):
┌─────────────────────────────────────────────────────────────────────────┐
│ turns_in_defensive_stance: 0→1→2→3 (triggers auto-switch, -3 trust)    │
│ turns_fortified: 0→1→2→3 (triggers auto-unfortify, -3 trust)           │
│ Reset on: move(), stance change to non-defensive, unfortify            │
└─────────────────────────────────────────────────────────────────────────┘

STATE INTERACTIONS:
• retreat_recovery BLOCKS: fortify, drill, attack, scout, aggressive_stance
• drilling_locked BLOCKS: attack, move (until drill completes)
• fortified + move = lose fortify bonus
• broken → forced retreat → retreat_recovery=3

ALLY COVERS RETREAT (Phase 2.9):
┌─────────────────────────────────────────────────────────────────────────┐
│ retreated_this_turn: True if marshal retreated THIS turn                │
│                                                                         │
│ When attacked while retreated_this_turn=True:                          │
│   1. Check for covering ally (same region, same nation, not retreated) │
│   2. If ally exists → ALLY fights instead (swapped defender)           │
│   3. If no ally → EXPOSED (+30% AI targeting bonus)                    │
│                                                                         │
│ Cleared at: START of next player turn (protection lasts enemy phase)   │
│ Set by: Forced retreat, manual retreat                                  │
└─────────────────────────────────────────────────────────────────────────┘
```

### Retreat Destination Priority (Phase 2.9)

When a marshal is forced to retreat, destinations are evaluated in priority order:

| Priority | Destination Type | Description |
|----------|-----------------|-------------|
| 1 (Best) | Friendly + Ally | Adjacent friendly region WITH an allied marshal (COVERED on home turf) |
| 2 | Friendly Empty | Adjacent friendly region WITHOUT marshal (EXPOSED but safe territory) |
| 3 | Enemy + Ally | Adjacent enemy region WITH an allied marshal (at least you have cover) |
| 4 | Enemy Unoccupied | Adjacent enemy region WITHOUT anyone (DESPERATION - alone in enemy land) |
| 5 | None | No valid retreat = ENCIRCLED (army breaks, flees to capital) |

**Key points:**
- Uses `marshal.nation` for nation-aware checks (works for both player and AI)
- Friendly territory is ALWAYS preferred over enemy territory, even if ally present in enemy territory
- Unoccupied enemy region = enemy controls but no marshals defending
- Forced retreat uses `move_to()` method (not direct assignment)
- Within each priority, prefers regions FURTHEST from the attacker

### Marshal Personality Abilities (Phase 2.8)

Each marshal has combat modifiers and unique abilities based on their personality. These are defined in `backend/models/personality_modifiers.py` and integrated into `marshal.py` and `combat.py`.

**NEY (Aggressive) - "Bravest of the Brave"**
| Modifier | Value | Condition |
|----------|-------|-----------|
| Base attack bonus | +15% | Always |
| Aggressive stance attack | +5% additional | In aggressive stance (total +20%) |
| Drill synergy | +5% additional | After drill completes |
| Aggressive stance defense | -5% | In aggressive stance |
| Defensive stance defense | -5% off bonus | Gets +10% not +15% |
| Max fortify | 10% | Capped (impatient) |

**Unique Abilities:**
- **Cavalry Charge**: Can attack enemies 2 regions away (movement_range=2)
- **Fighting Retreat**: When retreating, can attack with +10% bonus (retreat_attack_bonus)
- **Cavalry Limits**: See [Cavalry Limits System](#cavalry-limits-system) - cannot hold defensive positions for long

**DAVOUT (Cautious) - "Iron Marshal"**
| Modifier | Value | Condition |
|----------|-------|-----------|
| Defensive stance defense | +5% additional | In defensive stance (total +20%) |
| Outnumbered defense | +10% | When strength < attacker strength |
| Aggressive stance attack | -5% | Hesitant in aggressive stance |
| Bad odds attack | -10% | When strength ratio < 1:1 |
| Fortify rate | +3%/turn | Instead of +2%/turn |
| Max fortify | 20% | Instead of 15% |
| Instant fortify | +5% | On first fortify turn |
| Scout range | +1 region | Extended reconnaissance |

**Unique Abilities:**
- **Free Unfortify**: Unfortify costs 0 actions (efficient camp breaking)
- **Counter-Punch**: After successfully defending, next attack is FREE (requires enemy AI to trigger naturally; use `/debug counter_punch Davout` to test)

**GROUCHY (Literal)**
| Modifier | Value | Condition |
|----------|-------|-----------|
| Hold position defense | +15% | When holding_position=True |
| Explicit order bonus | +15% | When given specific, unambiguous orders |

**Unique Abilities:**
- **Immovable**: Use `hold` command to set holding_position=True, grants +15% defense at that location. Lost when moving.

**Literal Personality Mechanics (Phase 2.5):**
- **Strategic commands cost 1 action** (not 2) - Grouchy follows orders efficiently
- **+15% effectiveness on explicit orders** - Clear commands like "Attack Wellington" or "Move to Belgium"
- **Stops when blocked, awaits new orders** - Won't improvise, waits for clarification
- **Clarification popup for vague orders** - "Hold the line" triggers popup asking for specifics (NOT an objection)

**State Tracking Fields (in Marshal class):**
```python
self.cavalry: bool = False                    # Enables 2-tile attacks, Fighting Retreat, cavalry limits
self.turns_in_defensive_stance: int = 0       # Cavalry: turns in defensive stance (triggers at 3)
self.turns_fortified: int = 0                 # Cavalry: turns fortified (triggers at 3)
self.turns_defensive: int = 0                 # Legacy counter (kept for compatibility)
self.counter_punch_available: bool = False    # Davout free attack flag
self.holding_position: bool = False           # Grouchy Immovable active
self.hold_region: str = ""                    # Region where Grouchy is holding
```

**Debug Commands:**
```
/debug counter_punch <marshal>  - Set counter_punch_available=True
/debug restless <marshal>       - Set turns_defensive=5 (trigger restlessness)
/debug cavalry <marshal>        - Toggle cavalry status
/debug hold <marshal>           - Set holding_position=True
```

**Turn Processing:**
- **Turn Start**: Cavalry limits check - auto-switch stance or unfortify after 3 turns (deterministic, -3 trust each)
- **Turn End**: Cavalry counters increment for cavalry units in defensive stance/fortified
- **Turn End**: Unused counter_punch expires

### API Endpoints
- `GET /test` - Connection test
- `POST /command` - Execute player commands
- `GET /status` - Current game state
- `GET /docs` - Interactive API docs

---

## Combat System Architecture

### Single-Source-of-Truth Pattern (CRITICAL!)

Combat modifiers are calculated in ONE place only. This prevents bugs where bonuses apply twice.

```
marshal.py                          combat.py
───────────────────────────────     ─────────────────────────────────
get_attack_modifier()               Uses marshal's modifier
  - Personality base bonus          Generates messages about bonuses
  - Stance modifier                 Handles state changes (drill consumed)
  - Drill/shock bonus               DOES NOT recalculate modifiers
  - Returns final multiplier

get_defense_modifier()              Uses marshal's modifier
  - Personality base bonus          Generates messages about bonuses
  - Stance modifier                 DOES NOT recalculate modifiers
  - Fortify bonus
  - Outnumbered bonus (Davout)
  - Returns final multiplier
```

**Why this matters:** Previous bugs had fortify bonus calculated in BOTH marshal.py AND combat.py, resulting in 1.6% bonus instead of 16%.

### Combat Modifier Reference Table

| Modifier | Value | Calculated In | Condition |
|----------|-------|---------------|-----------|
| **NEY (Aggressive)** |
| Base attack | +15% | marshal.py:266 | Always |
| Aggressive stance attack | +5% | marshal.py:270 | stance == AGGRESSIVE |
| Drill synergy | +5% | marshal.py:275 | shock_bonus > 0 |
| Aggressive stance defense | -5% | marshal.py:285 | stance == AGGRESSIVE |
| Defensive stance defense | +10% | marshal.py:291 | stance == DEFENSIVE (reduced from +15%) |
| Max fortify cap | 10% | personality_modifiers.py | Capped |
| **DAVOUT (Cautious)** |
| Defensive stance defense | +20% | marshal.py:291 | stance == DEFENSIVE (+5% extra) |
| Outnumbered defense | +10% | marshal.py:295 | strength < attacker_strength |
| Aggressive stance attack | -5% | marshal.py:270 | stance == AGGRESSIVE |
| Bad odds attack | -10% | marshal.py:275 | strength_ratio < 1.0 |
| Max fortify cap | 20% | personality_modifiers.py | Higher cap |
| Fortify rate | +3%/turn | executor.py | Instead of +2%/turn |
| **FORTIFY BONUS** |
| Defense bonus | +X% | marshal.py:277 | fortify_bonus stored as decimal (0.16 = 16%) |
| Display | X% | combat.py | `int(fortify_bonus * 100)` for display |
| **DRILL/SHOCK BONUS** |
| Attack bonus | +50% | marshal.py:275 | shock_bonus > 0, consumed after use |

### Key Implementation Pattern

```python
# CORRECT - combat.py reads modifier, generates message, handles state
def resolve_combat(attacker, defender, ...):
    # Get modifier from marshal (single source of truth)
    attack_modifier = attacker.get_attack_modifier()

    # Generate message BEFORE clearing state
    attacker_drill_bonus = getattr(attacker, 'shock_bonus', 0)
    if attacker_drill_bonus > 0:
        drill_message = f"+{int(attacker_drill_bonus * 100)}% shock bonus!"

    # Use modifier in calculations
    attacker_power = attacker.strength * attack_modifier

    # Clear state AFTER modifier calculation
    if attacker_drill_bonus > 0:
        attacker.shock_bonus = 0
        attacker.drilling = False

# WRONG - recalculating modifier in combat.py
def resolve_combat_BAD(attacker, defender, ...):
    attack_modifier = attacker.get_attack_modifier()
    # BAD: Adding drill bonus again here!
    if attacker.shock_bonus > 0:
        attack_modifier *= 1.5  # DUPLICATE!
```

---

## Cavalry Limits System

Cavalry units (like Ney) cannot hold defensive positions for extended periods. Horses need to move.

### Mechanics

| Counter | Triggers At | Effect | Trust Penalty |
|---------|-------------|--------|---------------|
| `turns_in_defensive_stance` | 3 turns | Auto-switch to AGGRESSIVE | -3 |
| `turns_fortified` | 3 turns | Auto-unfortify | -3 |

**Maximum penalty per turn:** -6 (if both trigger simultaneously)

### Turn Flow

```
TURN START
    │
    ├─► _check_cavalry_limits()
    │       │
    │       ├─► If cavalry in defensive stance for 3+ turns:
    │       │       - Switch to AGGRESSIVE
    │       │       - Reset turns_in_defensive_stance = 0
    │       │       - trust.modify(-3)
    │       │       - Return "cavalry_stance_forced" event
    │       │
    │       └─► If cavalry fortified for 3+ turns:
    │               - Set fortified = False
    │               - Reset defense_bonus = 0
    │               - Reset turns_fortified = 0
    │               - trust.modify(-3)
    │               - Return "cavalry_fortify_forced" event
    │
    └─► Events shown in tactical messages at turn start

TURN END (in _process_tactical_states)
    │
    └─► For cavalry in defensive stance:
            turns_in_defensive_stance += 1
        For cavalry that is fortified:
            turns_fortified += 1
```

### Movement Resets

When a cavalry unit moves, both counters reset:
```python
# marshal.py move_to()
if getattr(self, 'cavalry', False):
    self.turns_in_defensive_stance = 0
    self.turns_fortified = 0
```

### Event Types

| Event Type | Message Example |
|------------|-----------------|
| `cavalry_stance_forced` | "🐴 Ney's cavalry is too restless! Auto-switched to AGGRESSIVE. Trust -3" |
| `cavalry_fortify_forced` | "🐴 Ney's horses cannot stay still! Auto-unfortified. Trust -3" |
| `cavalry_restless_warning` | "🐴 Warning: Ney's cavalry growing restless (turn 3 of 3)..." |

---

## Trust and Authority System

### Trust Values (from disobedience.py)

| Player Action | Trust Change | Context |
|---------------|--------------|---------|
| Accept marshal's objection | +12 | Player listens to marshal's concerns |
| Insist (override objection) | -10 to -15 | Player forces order against marshal's judgment |
| Compromise | +3 | Player finds middle ground |
| Cavalry auto-switch/unfortify | -3 each | Marshal acts without orders (misuse of cavalry) |

### Authority Interaction

Authority affects the probability of marshal compliance:
- **High authority** → Higher chance marshal follows orders without objection
- **Low authority** → More frequent objections and potential disobedience

The disobedience system uses odds-based calculations where authority modifies thresholds:
```python
# From disobedience.py - simplified concept
base_objection_chance = get_personality_objection_rate(marshal, action)
modified_chance = base_objection_chance * (1 - (authority / 100))
```

### Trust Trajectory Warning (Phase 3)

When a marshal's trust drops below 40, a one-time warning is shown at turn start.

**Implementation:**
- `trust_warning_shown: bool` field in Marshal tracks if warning has been shown
- `_check_trust_warnings()` in WorldState checks at turn start
- Warning resets (can trigger again) if trust rises back above 40

**Turn Start Order:**
1. Clear retreated_this_turn flags
2. Process tactical states (drill, fortify, retreat)
3. Check cavalry limits
4. **Check trust warnings** ← New
5. Process reckless cavalry auto-charge
6. Store tactical events

**Message Format:**
> ⚠️ {Marshal}'s trust is faltering ({value}). Consider giving them more independence.

### Redemption System (Trust ≤ 20)

When a marshal's trust falls to 20 or below, a redemption event triggers. The player must choose how to handle the broken relationship.

**Available Options:**

| Option | Troops | Marshal | Bonus | Availability |
|--------|--------|---------|-------|--------------|
| **Grant Autonomy** | Keep | 3 turns independent, uses AI | Trust +5 to +40 based on performance | Always |
| **Administrative Role** | Frozen (stored) | Sidelined, restorable in Phase 4 | +1 action/turn | If ≥2 field marshals AND no existing admin |
| **Dismiss** | Transfer to ally ≤3 regions OR disband | Gone forever | +10 authority | If ≥2 field marshals |

**Key Rules:**
1. **Last Marshal Protection:** If only 1 field marshal remains, ONLY Grant Autonomy is available
2. **Admin Cap:** Maximum 1 marshal can be in administrative role at a time
3. **Admin Troops Frozen:** Troops stay with admin marshal (stored in `administrative_strength`)
4. **Dismiss Range Limit:** Troops only transfer to ally within 3 regions, otherwise disband

**State Fields (Marshal):**
```python
marshal.administrative = True           # In admin role
marshal.administrative_strength = 72000 # Stored troop count
marshal.administrative_location = "Belgium"  # Stored location
```

**State Fields (WorldState):**
```python
world.bonus_actions = 1                 # From admin role transfer
world.calculate_max_actions()           # Returns 4 + bonus_actions
```

**Helper Methods (WorldState):**
```python
world.get_field_marshals()              # French marshals not in admin
world.get_admin_marshals()              # French marshals in admin role
world.find_nearest_marshal_within_range(from_location, nation, max_distance)
```

---

## Key Implementation Files

### Core Systems

| File | Purpose | Key Functions |
|------|---------|---------------|
| `backend/models/marshal.py` | Marshal state, combat modifiers | `get_attack_modifier()`, `get_defense_modifier()`, `move_to()` |
| `backend/game_logic/combat.py` | Combat resolution, messages | `resolve_combat()` |
| `backend/commands/executor.py` | Action execution | `_execute_attack()`, `_execute_fortify()`, `_execute_drill()` |
| `backend/models/world_state.py` | Game state, turn processing | `_check_cavalry_limits()`, `_process_tactical_states()` |
| `backend/commands/disobedience.py` | Objection system | `check_objection()`, trust/authority calculations |
| `backend/models/personality.py` | Personality types | `PersonalityType` enum, objection triggers |
| `backend/models/personality_modifiers.py` | Combat bonuses by personality | Modifier definitions per personality |
| `backend/ai/enemy_ai.py` | Enemy AI decision tree | `process_nation_turn()`, `_find_best_action()`, P1-P8 handlers |
| `backend/game_logic/turn_manager.py` | Turn flow, enemy AI integration | `end_turn()`, `_process_enemy_turns()` |

### Disobedience System Reference

**Location:** `backend/commands/disobedience.py`

This file contains the core marshal objection logic:
- When marshals object to orders
- Trust modification values
- Authority calculations
- Compromise system

**Key patterns to maintain:**
1. All trust modifications go through `marshal.trust.modify(value)`
2. Authority affects objection probability, not elimination
3. Cavalry limits bypass objection (automatic, not player-ordered)

### Enemy AI System Reference

**Location:** `backend/ai/enemy_ai.py` (685 lines)

The Enemy AI system provides decision-making for enemy nations (Britain, Prussia) during their turn phase. **CRITICAL:** It follows the Building Blocks Principle - enemies use the SAME executor as player commands.

**Key Principles:**
1. All actions flow through `executor.execute()` - no special enemy code
2. Enemy marshals have same combat modifiers, abilities, states as player marshals
3. No disobedience for enemies (AI decides = AI executes)
4. 4 actions per NATION, not per marshal

**IMPORTANT - Personality Behaviors Apply to ALL Marshals of That Type:**
When modifying AI behavior based on personality (e.g., "cautious marshals do X"), the change affects:
- Wellington (Britain, cautious)
- Davout (France, cautious) - when autonomous
- Any future cautious marshals

The Enemy AI code uses `personality = getattr(marshal, 'personality', 'balanced')` to determine behavior. Changes to how "cautious" personality behaves will affect ALL cautious marshals across all nations.

**Fortification Opportunity Logic (P3.5):**
Fortified marshals will unfortify when:
1. **Undefended enemy region adjacent** - Always unfortify to capture (zero risk)
2. **"Defending nothing"** - No enemies adjacent → unfortify to reposition
3. **Reposition toward fight** - No capture/ally target, but moving toward nearest enemy reduces distance (Fix #3)

This prevents fortified marshals from becoming permanent "rocks" that enemies can walk around.

**Decision Tree Priorities (P0-P8):**

| Priority | Trigger | Behavior |
|----------|---------|----------|
| **P0** | **Enemy in SAME region** | **MUST attack/retreat/wait - NEVER fortify/drill/stance!** |
| P1 | `retreat_recovery > 0` | Limited to defensive stance + wait |
| P2 | `strength < 25%` | Retreat if enemy adjacent, else defend |
| P3 | Stronger enemy adjacent | Defensive stance + fortify (cautious) |
| P4 | Valid attack target | Attack if ratio meets personality threshold |
| P4.5 | Undefended enemy region adjacent | Attack region to capture |
| P4.75 | Ally in combat/outnumbered | Move to support ally |
| P4.8 | Too weak alone (ratio < 0.5) | Consolidate with strongest ally within 3 distance |
| P5 | No attack, cautious | Fortify position |
| P6 | No attack, aggressive | Drill for shock bonus |
| P7 | No immediate threats | Move toward enemy (aggressive), fallback (cautious) |
| P7.5 | Stagnation (2+ idle turns) | Graduated escalation: unfortify/move/lower threshold |
| P8 | Default | Stance adjustment or wait (retreat suppressed after P7 advance) |

**CRITICAL - P0 Engagement Check:**
When a marshal shares a region with an enemy, they are "engaged" and MUST deal with it:
```python
# P0 runs FIRST in _evaluate_marshal(), before all other priorities
if enemies_in_region:
    if can_attack and ratio >= threshold:
        return ATTACK      # Good odds - fight!
    elif can_attack and ratio < threshold:
        return RETREAT     # Bad odds - flee if possible, else WAIT
    elif fortified:
        return UNFORTIFY   # Can't attack while fortified
    else:
        return WAIT        # Drilling - wait it out
```
This prevents the "fortify loop" bug where AI wastes actions trying to fortify while engaged.

**Personality Attack Thresholds:**

| Personality | Threshold | Meaning |
|-------------|-----------|---------|
| Aggressive (Blucher) | 0.7 | Attacks even when outnumbered 30% |
| Cautious (Wellington) | 1.3 | Only attacks with 30% advantage |
| Others | 1.0 | Only attacks at even odds or better |

**State Checks Before Actions:**
```python
# Before attack:
- Cannot attack if drilling or drilling_locked
- Cannot attack if fortified (must unfortify first)
- Cannot attack if broken

# Before drill:
- Cannot drill if already drilling
- Cannot drill if already have shock_bonus
- Cannot drill with enemy in SAME region (engaged!)
- Cannot drill with enemy adjacent (nation-aware check!)

# Before fortify:
- Cannot fortify if already fortified at max
- Cannot fortify if drilling
- Must be in defensive stance

# Stance spam prevention (Phase 2.9):
- _stance_changed_this_turn tracks marshals who changed stance
- Skip duplicate stance changes for same marshal in same turn
- Tracked per process_nation_turn() call, resets each nation's turn
```

**Target Evaluation Bonuses (Phase 2.9):**
```python
# _evaluate_target_ratio() adjusts effective attack ratio:
- DRILLING target: +25% (they have -25% defense penalty)
- FORTIFIED target: penalty equal to fortify bonus
- LOW MORALE (<50): up to +50% bonus (scales with how low)
- EXPOSED RETREATING: +30% (retreated_this_turn AND no covering ally)
```

**Turn Flow:**
```
Player ends turn
       |
       v
turn_manager.end_turn()
       |
       v
_process_enemy_turns()
       |
       v
For each nation in world.enemy_nations:
    EnemyAI.process_nation_turn(nation, world, game_state)
       |
       v
    For each action (up to 4):
        _find_best_action() -> evaluate all marshals
        Execute via executor.execute() <- SAME AS PLAYER!
       |
       v
world.advance_turn()
```

**Critical Code Pattern - Enemy Actions Don't Consume Player Budget:**
```python
# In executor.py - check before consuming action
is_player_action = True
marshal_name = command.get("marshal")
if marshal_name:
    executing_marshal = world.get_marshal(marshal_name)
    if executing_marshal and executing_marshal.nation != world.player_nation:
        is_player_action = False  # Enemy AI action - skip player budget

if result.get("success") and action_costs_point and is_player_action:
    world.use_action(action)  # Only for player
```

**Safeguards Against Infinite Loops:**
```python
max_free_actions = 2        # Max "wait" actions per turn
max_total_actions = actions_remaining * 2  # Absolute safety limit
```

**Known TODOs (Future Work):**
- Flanking coordination (AI doesn't explicitly coordinate for flanking bonus)
- Enemy recruiting (requires economy system)
- Round-robin action distribution (currently greedy)
- Region fortifications (buildings that slow capture - future economy feature)
- Failed action cooldown (don't retry blocked actions for 1-2 turns)
- Alliance coordination (Britain/Prussia share intel)
- Strategic objectives (AI picks goals like "Capture Belgium")
- **NOT planned: Strategic commands for AI** — per-action re-evaluation is a strength (AI adapts every action), strategic orders would cause interrupt deadlocks, engagement lock, and wasted actions. Player-only feature.

**Anti-Stagnation Systems:**

| System | Location | Trigger | Behavior |
|--------|----------|---------|----------|
| P7→P8 retreat suppression | `_advanced_this_turn` set | Marshal moved toward enemy via P7 | P8 won't retreat them back same turn |
| P3.5 reposition toward fight | `_check_fortification_opportunity` | Fortified, no enemies/captures nearby | Unfortify if moving toward enemy reduces distance |
| P4.8 ally consolidation | `_consider_consolidation` | Strength ratio < 0.5 vs nearest enemy | Move toward strongest ally within 3 distance |
| Graduated stagnation | `world.ai_stagnation_turns` (persisted on WorldState) | 2+ consecutive idle turns | Turn 2: force unfortify+move; Turn 3+: lower attack threshold |

**Stagnation Counter Details:**
- **Persisted on WorldState** (`world.ai_stagnation_turns` dict, serialized in to_dict/from_dict)
- **"Idle"** = only waited, defended-while-already-fortified, or changed stance
- **"Meaningful"** = attack, move, drill, recruit, unfortify, retreat, first fortify
- **Resets** on any meaningful action
- **Turn 2**: Force unfortify + move toward nearest enemy (ignores risk assessment)
- **Turn 3+**: Lower attack threshold by 20% + 10% per turn beyond 3 (floor 0.3)
- **Never suicidal**: Won't walk into enemy-occupied regions

**Common AI Bugs & Fixes:**
| Bug | Cause | Fix |
|-----|-------|-----|
| Fortify loop (AI wastes actions) | No engagement check | P0 engagement check forces attack/retreat |
| Drill while engaged | Missing same-region check | Added `enemy.location == marshal.location` check |
| Cautious marshal sits when threatened | No fallback movement | P7 cautious fallback to friendly territory |
| Retreat picks wrong direction | No capital preference | Sort retreat destinations by distance to capital |
| P7→P8 ping-pong (advance then retreat) | P7 moves toward enemy, P8 retreats | `_advanced_this_turn` suppresses P8 retreat |
| Dead-end fortification (Netherlands) | No valid capture/ally destination | P3.5 now repositions toward nearest enemy |
| Weak marshal bounces aimlessly | No concept of linking up | P4.8 consolidation moves toward strongest ally |
| All marshals idle indefinitely | No escalation mechanism | Graduated stagnation counter forces action |
| Stagnation counter never resets (248ce85) | `process_nation_turn()` checked `r.get("action")` but executor results store action under `r["ai_action"]` | Read from `r.get("ai_action", {})` first, fallback to `r.get("action")` |

**Test Map Limitations (13 regions):**
- No London, Berlin, Moscow - use proxy "home" regions (Netherlands for Britain, Rhine for Prussia)
- `_get_nation_capital()` is map-aware - checks if region exists before using
- When adding full 1805 map, update capitals dict in `_get_nation_capital()`

**Full documentation:** See `docs/ENEMY_AI_REFERENCE.md`

**UI Status:** ✅ Enemy phase popup implemented (`enemy_phase_dialog.tscn/gd`). Shows full battle details in modal after end turn. See `docs/UI_TODO.md` for implementation notes.

---

## Before Modifying: Required Reading

**STOP! Before changing code, read the relevant files first.**

| If you're modifying... | You MUST read these files first |
|------------------------|--------------------------------|
| Combat damage/modifiers | `marshal.py` (get_attack_modifier, get_defense_modifier), `combat.py` (resolve_combat) |
| Marshal abilities | `personality_modifiers.py`, `marshal.py`, `combat.py` |
| Fortify/Drill mechanics | `executor.py` (_execute_fortify, _execute_drill), `marshal.py` (state fields), `world_state.py` (_process_tactical_states) |
| Disobedience/Trust | `disobedience.py`, `personality.py`, `marshal.py` (Trust class) |
| Cavalry limits | `world_state.py` (_check_cavalry_limits), `marshal.py` (cavalry counters, move_to) |
| Turn processing | `world_state.py` (advance_turn, _process_tactical_states), `executor.py` (_execute_end_turn) |
| Adding new actions | `executor.py`, `parser.py` (valid_actions), `world_state.py` (_action_costs) |
| Retreat/Broken state | `combat.py` (forced retreat logic), `marshal.py` (retreat_recovery), `executor.py` (_execute_retreat) |
| Enemy AI behavior | `enemy_ai.py` (decision tree), `turn_manager.py` (_process_enemy_turns), `executor.py` (is_player_action check) |

### Common Modification Patterns

**Adding a new combat modifier:**
```
1. Add state field to marshal.py __init__
2. Apply modifier in marshal.py get_attack_modifier() or get_defense_modifier()
3. Add message generation in combat.py (DO NOT recalculate modifier)
4. Add state clearing in combat.py if consumable (AFTER get_*_modifier call)
```

**Adding a new action:**
```
1. Add to VALID_ACTIONS in validation.py (single source of truth for LLM pipeline)
2. Add _execute_[action]() method in executor.py
3. Add action name to valid_actions list in parser.py
4. Add action cost to _action_costs in world_state.py
5. Add keywords to mock parser in llm_client.py (~line 416, search "ADD NEW ACTION")
6. Add few-shot example in prompt_builder.py if action is complex/ambiguous
7. If it can trigger objections, add to objection_actions in disobedience.py
8. Add to_dict/from_dict if new state fields are needed (see Serialization Enforcement)
```

**Adding a new marshal state:**
```
1. Add field to marshal.py __init__
2. Add state processing in world_state.py _process_tactical_states() if it changes per turn
3. Add blocking logic if it prevents certain actions
4. Update executor.py to check state before executing blocked actions
5. Document in Marshal State Machine diagram above
```

**Adding a new frontend-facing response field (popup, dialog, etc.):**
```
Backend → Frontend data flow:
  executor.py → main.py → api_client.gd → main.gd

CRITICAL: main.py must explicitly pass through new fields!

1. executor.py: Return the field in the result dict
   return {"success": False, "pending_something": True, "data": {...}}

2. main.py /command endpoint: Add early return to pass through the field
   # After objection check, before building response dict:
   if result.get("pending_something"):
       result["action_summary"] = world.get_action_summary()
       result["game_state"] = world.get_game_state_summary()
       return result  # Pass through full executor result

3. main.gd _on_command_result(): Check for the field and handle it
   if response.has("pending_something") and response.pending_something:
       _show_something_dialog(response)
       return

4. Create dialog scene (.tscn) and script (.gd) in godot-client/

SERIALIZATION WARNING: Executor results contain "new_state" (full WorldState
with circular references). NEVER embed raw executor results in report dicts
that reach the API response. Always strip first:
  cleaned = {k: v for k, v in result.items() if k != "new_state"}
If you don't, FastAPI silently drops the ENTIRE parent dict from the response.

DEBUG TIP: If frontend isn't receiving a field, test with curl first:
  curl -X POST http://127.0.0.1:8005/command \
    -H "Content-Type: application/json" \
    -d '{"command": "test command"}'
If field is missing in JSON response, the bug is in main.py (step 2).
If curl hangs or returns 500, check for circular references in the response.
```

**UI Wiring Rule (MANDATORY):**

Every backend feature that displays in UI must pass the 5-step chain:

1. Backend logic works (unit tests)
2. Return value includes data (not discarded)
3. Endpoint response includes data (curl verification)
4. Godot receives and parses data
5. Godot displays data

**Test with curl BEFORE assuming Godot is broken:**
```bash
curl -X POST http://127.0.0.1:8005/command \
  -H "Content-Type: application/json" \
  -d '{"command": "end turn"}' | python -m json.tool
```
If curl shows data but Godot doesn't, bug is in Godot.
If curl shows no data, bug is in backend wiring (most likely main.py not passing through executor result fields).

See: `docs/UI_WIRING_CHECKLIST.md`

---

## Serialization Enforcement (MANDATORY)

**Enforcement tests automatically fail CI when serialization is incomplete.**

The rule: **"If it exists on the object, it must serialize."**

### When Adding ANY New Field to ANY Model Class

```
1. Add field to __init__ (or as instance attribute)
2. Add to to_dict() method
3. Add to from_dict() method (with sensible default via .get())
4. Run: pytest tests/test_serialization_enforcement.py -v
5. Update docs/SAVE_FORMAT_REFERENCE.md
6. Update docs/MODDING_FORMAT.md (if modder-facing)
```

### When Adding a NEW Model Class

```
1. Implement to_dict() method
2. Implement @classmethod from_dict() method
3. Add class to SERIALIZABLE_CLASSES list in test_serialization_enforcement.py
4. Copy the enforcement test template for your class
5. Run: pytest tests/test_serialization_enforcement.py -v
6. Document in SAVE_FORMAT_REFERENCE.md
```

### What the Tests Catch

The enforcement tests (`tests/test_serialization_enforcement.py`) automatically detect:
- Fields that exist on an object but aren't in `to_dict()`
- Classes in `SERIALIZABLE_CLASSES` that lack `to_dict`/`from_dict`
- Roundtrip failures (field values that don't survive serialize → deserialize)

Example failure message:
```
SERIALIZATION INCOMPLETE: Marshal
Fields not in to_dict(): ['new_feature_flag', 'new_counter']

Fix: Add these fields to Marshal.to_dict() AND from_dict()
Docs: Update docs/MODDING_FORMAT.md and docs/SAVE_FORMAT_REFERENCE.md
```

### Serializable Classes (Add New Classes Here)

Current classes with serialization (in `SERIALIZABLE_CLASSES`):
- `Marshal` - Commander state (50+ fields)
- `StrategicOrder` - Multi-turn orders
- `StrategicCondition` - Order termination conditions
- `WorldState` - Complete game state
- `Region` - Territory state
- `Trust` - Marshal trust value
- `AuthorityTracker` - Player authority
- `VindicationTracker` - Marshal vindication history

Future classes to add when implemented:
- `Treaty` - Diplomatic agreements
- `Alliance` - Coalition membership
- `Vassal` - Puppet states
- `Character` - Leader/general characters

### Doc Generation

Generate field documentation from code:
```bash
python -m backend.modding.doc_generator marshal  # Marshal fields
python -m backend.modding.doc_generator all      # All classes
```

---

## Implementation Status

### Phase 1: Foundation ✅ COMPLETE
- [x] 13 regions with adjacency
- [x] 5 marshals (3 French, 2 enemy)
- [x] Basic combat (strength × morale)
- [x] Movement with adjacency validation
- [x] Action economy (4 actions/turn)
- [x] Turn progression with auto-advance
- [x] Victory/defeat conditions
- [x] Gold and income system
- [x] Godot UI with command input
- [x] Map visualization with colors
- [x] API connection (port 8005)

### Phase 2: Combat & AI ✅ COMPLETE
**✅ IMPLEMENTED:**
- [x] Combat dice system (2d6 + skill modifiers)
- [x] Marshal skills (6 skills per marshal)
- [x] Stance system (Aggressive/Defensive/Neutral)
- [x] Drill mechanic (+50% shock bonus after 2 turns)
- [x] Fortify mechanic (+2%/turn defense, max 15-20%)
- [x] Retreat system (forced at 25% morale, recovery periods)
- [x] Smart DEFEND command (context-aware: → stance or → fortify)
- [x] Disobedience as NEGOTIATION (Trust/Insist/Compromise)
- [x] Authority system (prevents "always trust" exploit)
- [x] Vindication tracking (marshal track record affects objections)
- [x] Redemption system (at trust floor: Grant Autonomy / Dismiss / Demand Obedience)
- [x] Enemy AI decision tree (P1-P8 priorities)
- [x] Personality-driven AI thresholds (Wellington 1.3, Blucher 0.7)
- [x] Smart AI safety evaluation (encirclement check before captures)
- [x] AI fortification opportunity check (unfortify for high-value targets)
- [x] Enemy Phase popup (full battle details in modal)
- [x] Attacker movement on victory (advances into captured region)
- [x] Counter-Punch ability (Davout gets free attack after defending)
- [x] Battle naming system ("Battle of [Region]")

### Phase 2.5: Autonomy Foundation ✅ COMPLETE

**Core Concept:** "Grant Autonomy" at redemption floor connects player marshals to Enemy AI decision tree.

**📋 TODO:**
- [ ] Grant Autonomy → marshal uses Enemy AI for action selection
- [ ] Autonomous marshal processing in turn flow
- [ ] Autonomy end evaluation (regain trust floor → return to player control)
- [ ] Communication cut-off (no path to capital = fully autonomous)

### Phase 5.2: Strategic Commands 🔄 IN PROGRESS

**CRITICAL: Read `docs/PHASE_5_2_IMPLEMENTATION_PLAN.md` before implementing!**

This phase adds multi-turn strategic orders (MOVE_TO, PURSUE, HOLD, SUPPORT) that marshals execute autonomously over several turns. Personality affects execution behavior.

**Key Design Decisions (locked):**
- Strategic orders cost 2 actions (1 for LITERAL personality)
- LITERAL (Grouchy) NEVER interrupts for cannon fire ("The Grouchy Moment")
- PURSUE completes after combat (any outcome) — order is fulfilled once marshal engages target
- HOLD/SUPPORT combat result → order status: Victory=continue, Defeat=break, Stalemate=ask
- Clarification system reuses objection popup for LITERAL + generic commands
- ONE strategic order per marshal at a time; new order silently replaces old
- "reinforce" = SUPPORT (no teleporting; removed as separate action)

#### What's Implemented (1010 tests, 0 failures)

**Strategic Command Pipeline (end-to-end):**
```
User: "Grouchy, march to Belgium"
  → llm_client fast parser: action="move"
  → parser.py: detect_strategic_command() → is_strategic=True, strategic_type=MOVE_TO
  → executor.py: strategic interception block (_skip_routing pattern)
  → _execute_strategic_command(): creates StrategicOrder, executes first step
  → turn_manager.py end_turn(): StrategicExecutor.process_strategic_orders()
  → strategic.py: _execute_move_to() moves marshal along path each turn
```

**Phase A — Data Structures (marshal.py):**
- `StrategicOrder` dataclass — command_type, target, target_type, path, conditions, combat tracking
- `StrategicCondition` dataclass — max_turns, until_marshal_arrives, until_battle_won, etc.
- `target_snapshot_location` field — for "Move to Ney" (friendly marshal snapshot)
- Marshal fields: `strategic_order`, `in_strategic_mode` property, precision tracking
- Full to_dict/from_dict serialization roundtrip

**Phase B — Parser Integration (strategic_parser.py + parser.py + schemas.py):**
- `detect_strategic_command()` — identifies MOVE_TO, PURSUE, HOLD, SUPPORT from natural language
- `_classify_target()` — region, marshal, cardinal direction, generic; direction auto-resolves via `REGION_POSITIONS` grid
- `resolve_direction()` — cardinal (north/south/east/west) + relative ("the front", "back") → adjacent region
- `_parse_condition()` — until_arrives, until_destroyed, max_turns, until_battle_won
- Enemy marshal MOVE_TO auto-converts to PURSUE
- "reinforce" and "support" keywords both route to strategic SUPPORT via parser
- Integrated into parser.py via `world=` parameter; main.py passes world

**Phase C — Strategic Executor (executor.py + strategic.py + turn_manager.py):**
- `_execute_strategic_command()` in executor.py — creates StrategicOrder, validates, first-step execution
- `_skip_routing` pattern — intercepts strategic commands before tactical routing
- `_strategic_execution=True` flag — skips action cost for per-turn autonomous moves
- `StrategicExecutor.process_strategic_orders()` in strategic.py — per-turn multi-step execution
- Handlers: `_execute_move_to`, `_execute_pursue`, `_execute_hold`, `_execute_support`
- Personality-aware: aggressive=auto-attack, cautious=safe paths, literal=exact+immovable
- HOLD sally mechanic: aggressive marshals attack adjacent enemies then return
- Generic target resolution for all 4 types: `_resolve_generic_target()` shared helper
- Grouchy clarification popup for all types (free action, includes `strategic_type` for Godot reissue)
- Turn manager hook: runs AFTER enemy phase, BEFORE advance_turn()

**Grouchy Ambiguity System (executor.py, enemy_ai.py):**
- `_get_effective_personality()` in enemy_ai.py — literal→cautious when AI-controlled
- `_apply_grouchy_ambiguity_buff()` in executor.py — combat buffs based on order clarity
- Ambiguity thresholds: 0-20 (+15%), 21-40 (+10%), 41-60 (+5% + warning), 61+ (no buff)
- `precision_execution_active/turns` fields — +1 all skills for 3 turns on crystal clear orders

**Battle Tracking (world_state.py):**
- `battles_this_turn` list — for cannon fire detection
- `record_battle()` / `get_battles_within_range()` / `clear_turn_battles()`
- `get_enemies_in_region(region, nation)` — finds enemies relative to nation
- `find_path(start, end, avoid_regions=)` — BFS pathfinding with region avoidance

**REMOVED: `_execute_reinforce` teleport action**
- "reinforce" keyword now maps to action="move" in fast parser
- Strategic parser detects "reinforce" as SUPPORT keyword → strategic_type=SUPPORT
- No separate routing, no teleporting — all support goes through strategic pipeline

#### Audit Issues (all 7 fixed in commit 7e3fa12)

| # | Status | Fix Summary |
|---|--------|-------------|
| 1 | ✅ FIXED | Sally now does move→attack→return (3 executor calls) |
| 2 | ✅ FIXED | Retreat recovery check at top of `_execute_strategic_turn()` |
| 3 | ✅ FIXED | `VALID_STRATEGIC_TYPES` validation in validation.py, falls back to tactical |
| 4 | ✅ FIXED | Shared `_get_personality_aware_path()` used by SUPPORT, MOVE_TO, PURSUE |
| 5 | ✅ FIXED | Personality-aware pathfinding in executor.py initial path + strategic.py recalc |
| 6 | ✅ VERIFIED | `to_dict()`/`from_dict()` already included all fields (false positive) |
| 7 | ✅ FIXED | `until_battle_won` triggers on both victory AND stalemate |

#### What's Next: Phase J-K-M

**Remaining phases (1022 tests passing):**
- Phase I: Serialization Validation ✅ COMPLETE (33 roundtrip tests)
- Phase J: UI Updates (Godot strategic status display, interrupt dialogs). NOTE: Backend currently emits interim `strategic_progress` events (type: `strategic_progress`, with `order_status`: active/continues/completed) into the main events list. Phase J should replace these with a persistent HUD showing active orders per marshal. Backend data is ready (`marshal`, `command`, `destination`, `turns_remaining`).
- Phase K: Integration testing (full end-to-end strategic command flow)
- Phase M: Strategic Objections — marshals object at issuance based on personality (Ney→HOLD, Davout→PURSUE bad odds). Check once at issuance only, never during execution. Uses existing `check_objection()` and objection popup. See `docs/PHASE_5_2_IMPLEMENTATION_PLAN.md` Phase M.

#### Phase I (Serialization Validation) ✅ COMPLETE
Full serialization audit and fix. All game state now survives roundtrip.
- Added `to_dict()`/`from_dict()` to: Trust, Region, AuthorityTracker, VindicationTracker, WorldState
- Fixed Marshal.to_dict(): expanded from 15 fields to 50+ fields
- 33 roundtrip tests in `tests/test_serialization.py`
- Documentation: `docs/SAVE_FORMAT_REFERENCE.md`
- Full save/load is Pre-EA feature; serialization validated and ready

**Modding Support (Extension to Phase I):**
- `WorldState.from_scenario(path)` — Load custom scenarios from JSON files
- `backend/modding/validator.py` — CLI validation tool for modders
- Minimal JSON support: Marshals need only `name`, `location`, `strength`; regions need only `name`, `adjacent_regions`
- Forward compatibility: Unknown fields are silently ignored
- 57 new tests (18 modding workflow + 9 forward compatibility + 7 scenario loading + 32 validator tests)
- Example mods: `mods/examples/` (battle_of_waterloo.json, custom_nations_scenario.json, etc.)
- Documentation: `docs/MODDING_FORMAT.md`

**Modder Workflow:**
```bash
# Validate your scenario
python -m backend.modding.validator mods/my_scenario.json

# Load in Python
from backend.models.world_state import WorldState
world = WorldState.from_scenario("mods/my_scenario.json")
```

#### Phase H (Literal Bonuses) ✅ COMPLETE (Design Variation)
Implemented via sustained precision execution rather than one-time completion bonus:
- `precision_execution_active/turns` fields on Marshal
- `get_effective_skill()` returns base skill +1 when precision active (capped at 8)
- Triggers on command issuance when ambiguity ≤20 AND strategic_score >60
- Lasts 3 turns, decays in `_process_tactical_states()`
- Combat integration: combat.py uses `get_effective_skill()` for tactical, shock, defense
- Tests: 8 tests in test_grouchy_ambiguity.py (TestPrecisionExecution, TestGetEffectiveSkill, TestPrecisionDecay)

#### Phase D (Interrupt Response Handling) ✅ COMPLETE
- `handle_response()` in strategic.py — processes player choices for interrupts
- Interrupt types: `cannon_fire`, `contact`, `contact_bad_odds`, `ally_moving`
- `pending_interrupt` field on Marshal — persists interrupt state
- Response options: attack, go_around, hold_position, cancel_order, investigate, continue_order
- Trust penalties: continue_order=-2, hold_position=-3 (mid-march), cancel_order=-3 (mid-march)

#### Phase E (Cancel Command) ✅ COMPLETE
- Keywords: "cancel", "halt", "stand down", "stop", "abort", "belay that"
- Cost: 1 action
- Trust: -3 (mid-march) or 0 (first-step cancel)
- Implementation: `_execute_cancel()` in executor.py
- Flavorful messages by order type:
  - MOVE_TO: "halts his march and awaits new orders"
  - PURSUE: "breaks off the pursuit"
  - HOLD: "abandons the position"
  - SUPPORT: "breaks off from supporting [ally]"

#### First-Step Blocked Path (Option B) ✅ COMPLETE
When strategic command is issued and first step is blocked:
- **AGGRESSIVE**: Auto-attacks if odds ≥ 0.7; else asks player
- **CAUTIOUS**: Always asks player
- **LITERAL**: Silently reroutes around ALL enemy regions
- First-step interrupt costs 1 AP (via `variable_action_cost`)
- First-step cancel has 0 trust penalty (`is_first_step` flag in pending_interrupt)
- Implementation: `_handle_first_step_blocked()` in executor.py

#### Cavalry First-Step Movement ✅ COMPLETE
- Cavalry (movement_range=2) now moves UP TO movement_range regions on first step
- Formula: `steps = min(movement_range, len(path))`
- Message: "Cavalry charges through Belgium -> Rhine" for multi-region moves
- Applies to MOVE_TO, PURSUE, HOLD, SUPPORT first-step execution

#### Implementation Order
- [x] Phase A: Data Structures ✅
- [x] Phase B: Parser Integration ✅
- [x] Pre-C: WorldState dependencies ✅
- [x] Phase C: Strategic Executor ✅
- [x] Phase F: Turn manager integration ✅ (included in Phase C)
- [x] Phase G: Clarification system ✅ (included in Phase C)
- [x] Phase L: LLM Strategic Integration ✅ (65 tests)
- [x] Phase D: Interrupt response handling ✅ (14 tests)
- [x] Phase E: Cancel command ✅ (14 tests + 7 first-step tests)
- [x] Phase H: Literal bonuses ✅ (8 tests — design variation: sustained +1 skills for 3 turns)
- [x] Phase I: Serialization Validation ✅ (33 tests — full roundtrip, see `docs/SAVE_FORMAT_REFERENCE.md`)
- [ ] Phase J: UI Updates (Godot strategic status display)
- [ ] Phase K: Integration testing
- [ ] Phase M: Strategic Objections (disobedience at issuance)

**📋 REMAINING (Phase 3+):**
- [ ] Grouchy literal mechanics (see below)
- [ ] Marshal rivalries affect coordination
- [ ] Flanking coordination system
- [ ] Post-battle casualty report

### Phase 3: LLM & Advisors (Planned)
- [ ] Real LLM command parsing (currently mock keyword matching)
- [ ] LLM marshal personality responses
- [ ] Advisor gates (Berthier, Talleyrand)
- [ ] Battle narration generation

**CONCEPTUAL (design only, no code):**
- Sections marked with "(CONCEPTUAL)" or "(Future)"
- Diplomacy system
- Supply/Logistics
- Coalition triggers
- Weather/Seasons
- Token monetization

When reading CLAUDE.md, skip CONCEPTUAL sections unless planning future features.

---

## Critical Code Patterns

### Type Safety (CRITICAL!)
All numeric returns MUST be wrapped with `int()` - Godot expects int, not float:
```python
# CORRECT:
return {"turn": int(self.current_turn), "gold": int(self.gold)}

# WRONG - will cause Godot errors:
return {"turn": self.current_turn}
```

### Marshal Storage (Unified)
All marshals (player + enemy) in single dict. Do NOT create separate dicts:
```python
# CORRECT:
world.marshals  # Contains Ney, Davout, Grouchy, Wellington, Blucher

# WRONG - causes persistence bugs:
self.player_marshals = {}
self.enemy_marshals = {}
```

### Early Returns Pattern
```python
# CORRECT:
if not world:
    return {"success": False, "message": "No world state"}
if not marshal:
    return {"success": False, "message": "Marshal not found"}
# ... main logic

# WRONG - deep nesting:
if world:
    if marshal:
        if enemy:
            # ... deeply nested
```

---

## Action Economy

### Current Implementation
- 4 actions per turn
- Auto-advance when actions exhausted
- Free actions: `status`, `help`, `end_turn`
- Paid actions: `attack`, `move`, `scout`, `recruit`, `defend` (cost 1 each)

> **Future expansion concepts (variable costs, nation-specific actions, overextension, stability) moved to `docs/FUTURE_DESIGN.md`.**

---

## Building Blocks Philosophy

The game uses a "building blocks" approach where all actions (player AND AI) go through the same executor. This is intentional:

### Existing Blocks (Complete)
| Block | Location | Notes |
|-------|----------|-------|
| attack | executor.py | With region conquest |
| defend | executor.py | +30% bonus next battle |
| move | executor.py | Adjacency validated |
| scout | executor.py | Range-limited intel |
| recruit | executor.py | 200 gold → 10,000 troops |
| support | strategic SUPPORT | March to ally marshal (multi-turn, "reinforce" keyword also works) |

### Planned Blocks (Future)
| Block | Priority | Notes |
|-------|----------|-------|
| propose_peace | High | Win condition beyond conquest |
| declare_war | High | Coalition dynamics |
| propose_alliance | High | Alliance tracking |
| siege | Medium | Fortified regions take time |
| forced_march | Medium | Move 2, morale penalty |
| blockade | Medium | Reduce enemy income (naval abstraction) |
| emergency_taxation | Low | Gold now, morale cost |
| intercept_messages | Low | Intelligence gathering |

### Adding New Blocks
1. Add to `VALID_ACTIONS` in `validation.py` (single source of truth for LLM)
2. Add handler method in `executor.py`: `_execute_[action_name]()`
3. Add action to `parser.py` valid_actions list
4. Add cost to `world_state.py` `_action_costs` dict
5. Update mock parser keywords in `llm_client.py` (search "ADD NEW ACTION")
6. Add few-shot example in `prompt_builder.py` if action has complex syntax

---

## Input Handling Architecture

**CRITICAL: Every user input MUST receive a response.** No input should ever be ignored or cause a crash.

> **Full InputRouter design (categories, detection patterns, response examples) moved to `docs/FUTURE_DESIGN.md`.** Currently, all input goes through LLMClient -> Parser -> Executor pipeline.

---

## LLM Integration Architecture

### Current State (Phase 4 ✅ COMPLETE)
- **Fast parser** (keyword matching) handles 90%+ of commands - FREE, instant
- **Anthropic fallback** for ambiguous commands - Haiku, ~$0.0004/request
- **BYOK support** - Users can bring their own API key
- **Validation layer** catches hallucinations

### Command Parsing Pipeline
```
User Input: "Ney, attack Wellington"
                |
                v
+===============================================+
|           LLMClient.parse_command()           |
|              (llm_client.py)                  |
+===============================================+
                |
                | STEP 1: Always run fast parser first
                v
+-----------------------------------------------+
|        Fast Parser (keyword matching)         |
|        _parse_with_mock()                     |
|                                               |
|  Returns ParseResult with confidence score:   |
|  - 0.95 = marshal + action + target           |
|  - 0.9  = action + one identifier             |
|  - 0.8  = action only                         |
|  - 0.5  = unknown (couldn't parse)            |
+-----------------------------------------------+
                |
                | STEP 2: Check if LLM fallback needed
                |
                | Skip LLM if:
                |   - Mock mode (LLM_MODE=mock)
                |   - High confidence (>= 0.7)
                |   - No game_state provided
                |   - Meta command (help, debug, etc.)
                |
                v
        [confidence < 0.7 AND live mode?]
               /              \
              NO              YES
              |                |
              v                v
     Return fast result   +-----------------------------------+
                          |   AnthropicProvider.parse()       |
                          |        (providers.py)             |
                          +-----------------------------------+
                                        |
                                        | HTTP POST to Anthropic
                                        v
                          +-----------------------------------+
                          |   validation.validate_parse_result|
                          |   (catches hallucinations)        |
                          +-----------------------------------+
                                        |
                              Return validated result
```

### LLM Files Reference

| File | Purpose |
|------|---------|
| `backend/ai/llm_client.py` | Main entry point. Fast parser + LLM fallback logic |
| `backend/ai/providers.py` | Provider abstraction (Anthropic, Groq stub) |
| `backend/ai/schemas.py` | ParseResult, ProviderConfig dataclasses |
| `backend/ai/validation.py` | Validates LLM output against game rules |
| `backend/ai/prompt_builder.py` | Builds context-aware prompts |
| `backend/ai/README.md` | Comprehensive documentation |

### Configuration

```bash
# .env file
LLM_MODE=mock          # mock | anthropic | groq (groq not yet implemented)
ANTHROPIC_API_KEY=sk-ant-api03-...   # Required if LLM_MODE=anthropic
```

### Cost Estimation (Anthropic Haiku)
- Per request: ~500 input + ~200 output tokens = **~$0.0004**
- 1,000 ambiguous commands = **~$0.40**
- Fast parser catches 90%+, so real cost is much lower

### Key Insight
**Executor stays rule-based.** LLM helps with parsing ambiguous commands, but game mechanics are 100% deterministic. No LLM randomness in combat, movement, or AI decisions.

### LLM Strategic Integration ✅ (Phase 5.2-L)

LLM fallback now understands strategic commands:
- **Prompt** teaches LLM about MOVE_TO, PURSUE, HOLD, SUPPORT keywords and conditions
- **Schema** includes `is_strategic`, `strategic_type`, `strategic_condition` in LLM output format
- **Ambiguity scoring** guide: 0-20 crystal clear, 61+ very vague (generic targets)
- **Few-shot examples** include 4 strategic + 2 tactical commands
- **Validation** no longer blocks `command_type="strategic"`, conditions, or standing orders
- **Fast parser** expanded: 50+ keyword phrases across all 4 strategic types
- Bare "defend" stays tactical; "defend and hold" is strategic HOLD

### Strategic Score + Ambiguity

ParseResult scoring fields drive gameplay mechanics:
- `strategic_score` (0-100): How complex/strategic the command is
- `ambiguity` (0-100): How unclear the command was

**Active effects (Phase 5.2):**
| Score | Effect |
|-------|--------|
| Ambiguity 0-20 | +15% combat buff (Grouchy explicit order bonus) |
| Ambiguity 21-40 | +10% combat buff |
| Ambiguity 41-60 | +5% combat buff + warning |
| Ambiguity 61+ | No buff, triggers Grouchy clarification popup |
| High strategic | +authority, +morale (Napoleon in his element) |

### Nation Tiers for LLM (Future)
```python
NATION_TIERS = {
    "great_power": {
        "llm_model": "claude-sonnet-4-20250514",
        "actions_per_turn": 4,
        "full_personality": True,
        "examples": ["France", "Britain", "Prussia", "Austria", "Russia"]
    },
    "secondary_power": {
        "llm_model": "claude-haiku-4-20250514",
        "actions_per_turn": 2,
        "examples": ["Spain", "Bavaria", "Netherlands"]
    },
    "minor_power": {
        "llm_model": None,  # Rule-based only
        "actions_per_turn": 1,
        "examples": ["Saxony", "Naples", "Denmark"]
    }
}
```

---

## Future Design Concepts

> **Diplomacy, Naval Abstraction, Colonial Power, EA Expansion Plans, Missing Design Elements, LLM Philosophy, LLM Flavor Systems, and Nation AI Decision Trees have been moved to `docs/FUTURE_DESIGN.md`.**
>
> These are CONCEPTUAL designs not yet implemented. Read them when planning future phases.

---

## Configuration

### Environment Variables (`.env`)
```
ANTHROPIC_API_KEY=sk-...  # Required only for real LLM mode
```

### Server Configuration
- Port: 8005 (NOT 8000!)
- Host: 127.0.0.1
- CORS enabled for Godot client
- Change port in BOTH `backend/main.py` AND `godot-client/.../api_client.gd`

---

## Map System

> **Map system details, transition strategy, and migration checklists moved to `docs/FUTURE_DESIGN.md`.**
> Current state: 13 hardcoded regions in `region.py`, programmatic circles in `map.gd`.

---

## Documentation Update Rules (MANDATORY)

**If you changed behavior, update the doc that describes it.**
**Every TODO/planned item MUST reference a phase in ROADMAP.md.** No orphan TODOs — if it doesn't belong to a phase, either add it to one or don't write it.

| Event | Update These Docs |
|-------|-------------------|
| Session ends | STATUS.md (test count, completed work, next steps) |
| Phase completed | ROADMAP.md (mark complete), STATUS.md |
| New system built | COMPLETED.md (how it works) |
| New code pattern | TECHNICAL.md (add to patterns) |
| Design idea documented | FUTURE_DESIGN.md |
| Enemy AI changes | AI_REFERENCE.md |
| Bug fixes | STATUS.md (Recently Completed section) |
| New tests added | STATUS.md (Test Count History) |

---

## Don't Do

- ❌ Don't use separate dicts for player/enemy marshals
- ❌ Don't return floats to Godot (always wrap with `int()`)
- ❌ Don't add features outside current phase scope
- ❌ Don't change port without updating api_client.gd
- ❌ Don't add naval ship combat (abstracted instead)
- ❌ Don't make executor LLM-dependent (keep deterministic)
- ❌ Don't store API keys in code (use .env)

---

## Project Phases

> **Detailed phase descriptions moved to `docs/ROADMAP.md` (timeline) and `docs/COMPLETED.md` (done systems).**
> Phase numbers ONLY exist in ROADMAP.md.

---

## Reference Documents

For detailed design decisions and architecture:
- **`docs/PHASE_5_2_IMPLEMENTATION_PLAN.md`** - Strategic Commands implementation (MOVE_TO, PURSUE, HOLD, SUPPORT) - **READ THIS FIRST for Phase 5.2 work!**
- **`docs/PHASE_5_2_CHAIN_AUDIT.md`** - Complete chain verification (LLM → Backend → UI) with broken links and fixes
- **`docs/SAVE_FORMAT_REFERENCE.md`** - Complete serialization format for all game objects
- **`docs/MODDING_FORMAT.md`** - Guide for creating custom scenarios, marshals, and regions
- `PM_REVIEW_AND_ROADMAP.md` - Full assessment and phase plans
- `LLM_INTEGRATION_ARCHITECTURE.md` - Technical LLM specs
- `CREATION_LOG.md` - Development history and bug fixes
- `command-based-design.md` - Core gameplay vision

---

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Godot float→int error | Wrap all numeric returns with `int()` |
| Enemy not persisting | Check using unified `world.marshals` dict |
| Port connection failed | Verify port 8005 in both backend and frontend |
| Command not recognized | Add to `valid_actions` in parser.py |
| Marshal selection wrong | Check `find_nearest_marshal_to_region()` filtering |
| Fortify bonus too small | Check modifier uses `(1.0 + bonus)` not `(1.0 + bonus * 0.10)` |
| Modifier applied twice | Search for duplicate calculations in marshal.py AND combat.py |
| Drill bonus not applying | Ensure state cleared AFTER `get_attack_modifier()` call |
| Display shows wrong % | Check using `* 100` not `* 10` for percentage display |
| Cavalry not resetting | Verify `move_to()` resets `turns_in_defensive_stance` and `turns_fortified` |
| Enemy AI crashing | Ensure game_state is dict `{"world": WorldState}`, not WorldState directly |
| AttributeError on property | Check if attribute is a @property (use underlying field or method) |
| Unicode error on Windows | Debug output has emoji; use UTF-8 encoding or suppress debug |
| is_reckless_cavalry not settable | It's a computed property from `cavalry` + `personality=="aggressive"` |
| AI fortify loop (wastes actions) | P0 engagement check missing - add check at start of `_evaluate_marshal` |
| AI drills while engaged | Check `_consider_drill` has same-region enemy check |
| AI doesn't attack when should | Check P4 attack threshold vs ratio; add `[P0 ENGAGEMENT]` debug prints |
| AI capital not found | Test map lacks London/Berlin - use proxy regions in `_get_nation_capital()` |
| AI stagnation never resets | `process_nation_turn()` result dicts have action under `ai_action` key, not `action` — fixed in 248ce85 |
| Strategic reports silently dropped | Executor results contain `new_state` (WorldState, circular refs). Strip with `{k:v for k,v in result.items() if k != "new_state"}` before embedding in any report dict that reaches the API response |
| Post-objection "Unknown action" | `_execute_post_objection` must handle ALL actions in `objection_actions` list + strategic routing. Check both when adding new actions |
| Duplicate buttons in popup | Backend should NOT add Cancel/Proceed options — Godot clarification_popup.gd adds its own "Cancel Order" button at line 66-69 |
| Sally battles never show | Do NOT use move→attack→return for sally. Executor blocks `move()` into enemy-occupied regions (silent fail). Use `attack` directly — executor handles adjacent attacks. See strategic.py sally comment |
| Strategic popups missing (auto-advance) | Auto-advance turn path in executor.py must copy ALL turn_result fields: `enemy_phase`, `tactical_events`, AND `strategic_reports`. Missing any one silently drops those popups |
| Post-objection costs 1 AP not 2 | `_execute_post_objection` must use `variable_action_cost` from strategic result, not single `use_action()` call. Strategic = 2 AP, literal = 1 AP |
| Strategic detection skipped | Verify `world` is passed to `parser.parse()`. Without it, strategic_parser never runs and commands fall through to tactical routing (e.g. HOLD becomes defend) |
| Contact interrupt loops forever | `_handle_blocked_path` triggers every turn if enemy persists. Must track `last_contact_enemy`/`last_contact_turn` on the order and suppress re-asking within 1 turn |
| Ally moving interrupt loops forever | REMOVED: ally_moving popup replaced with silent auto-follow. SUPPORT tracks ally.location dynamically each turn — no popup needed |
| Command executes for wrong marshal | Interrupt router in main.py matched keywords (e.g. "march to") in command addressed to different marshal. Fixed: router checks if command names a different marshal and skips |
| Interrupt report missing order_status | ALL return dicts from strategic handlers MUST include `order_status` field. Missing it causes `status=None` in debug output and may confuse Godot |
| Stale strategic order after forced retreat | Forced retreat now clears `marshal.strategic_order` in `_apply_forced_retreat_or_break()`. HOLD orders also clear `holding_position`/`hold_region`. Message reflects which order was broken |

---

## Combat Debugging Checklist

When combat modifiers seem wrong, check:

1. **Single source of truth**: Is the modifier calculated in only ONE place?
   - Attack: `marshal.get_attack_modifier()` only
   - Defense: `marshal.get_defense_modifier()` only

2. **Order of operations**: Are states cleared AFTER reading them?
   ```python
   # CORRECT order:
   bonus = getattr(marshal, 'shock_bonus', 0)
   modifier = marshal.get_attack_modifier()  # Uses shock_bonus
   marshal.shock_bonus = 0                    # Clear AFTER

   # WRONG order:
   marshal.shock_bonus = 0                    # Cleared too early!
   modifier = marshal.get_attack_modifier()  # Gets 0
   ```

3. **Display math**: Is the display using the right multiplier?
   - Stored as decimal: `0.16` = 16%
   - Display: `int(value * 100)` = "16%"

4. **Test with known values**:
   ```python
   # Sanity check expectations:
   # Ney aggressive + drill = 1.15 * 1.05 * 1.50 = 1.81 (rounded to 1.75-1.85)
   # Davout defensive + 16% fortify = 1.20 * 1.16 = 1.39 (rounds to 1.40)
   ```