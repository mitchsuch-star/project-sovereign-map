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

DEBUG TIP: If frontend isn't receiving a field, test with curl first:
  curl -X POST http://127.0.0.1:8005/command \
    -H "Content-Type: application/json" \
    -d '{"command": "test command"}'
If field is missing in JSON response, the bug is in main.py (step 2).
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
- Combat result → order status: Victory=continue, Defeat=break, Stalemate=ask
- Clarification system reuses objection popup for LITERAL + generic commands
- ONE strategic order per marshal at a time; new order silently replaces old
- "reinforce" = SUPPORT (no teleporting; removed as separate action)

#### What's Implemented (667 tests, 0 failures)

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
- `_classify_target()` — region, friendly marshal (snapshot), enemy marshal (→PURSUE), generic
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
- Grouchy clarification gate for generic/ambiguous targets
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

#### What's Next: Phase J-K

**Remaining phases (806 tests passing):**
- Phase I: Serialization Validation ✅ COMPLETE (33 roundtrip tests)
- Phase J: UI Updates (Godot strategic status display, interrupt dialogs)
- Phase K: Integration testing (full end-to-end strategic command flow)

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

### Future Expansion (Early Access) - CONCEPTUAL/TBD

```python
# Variable action costs
ACTION_COSTS = {
    "attack": 2,           # Major commitment
    "probe_attack": 1,     # Light engagement  
    "move": 1,
    "forced_march": 2,     # Move 2 regions, take casualties
    "scout": 1,
    "deep_reconnaissance": 2,
    "recruit": 1,
    "mass_conscription": 3,    # Double troops, morale penalty
    "defend": 1,
    "fortify": 2,
    "diplomatic_mission": 1,
    "negotiate_treaty": 2,
}
```

### Nation-Specific Action Counts (CONCEPTUAL)
Different nations have different administrative capacity:
```python
BASE_NATION_ACTIONS = {
    "France": 5,      # Corps system, centralized command
    "Prussia": 4,     # Efficient but smaller
    "Britain": 4,     # Parliamentary delays but competent
    "Austria": 3,     # Bureaucratic, multi-ethnic complexity
    "Russia": 3,      # Vast but slow
    "Spain": 2,       # Guerrilla focus, weak central command
    "Ottoman": 2,     # Declining administration
}
```

### Action Modifiers (CONCEPTUAL)
Actions can be gained or lost based on game state:

**Gaining Actions:**
```python
ACTION_BONUSES = {
    "tech_administration": +1,      # Administrative reforms
    "tech_military_theory": +1,     # Staff college system
    "leader_trait_organizer": +1,   # Napoleon's personal skill
    "stable_government": +1,        # No revolts, high legitimacy
}
```

**Losing Actions:**
```python
ACTION_PENALTIES = {
    "overextension": -1,           # Controlling too many non-core regions
    "instability": -1,             # Low stability score
    "war_exhaustion": -1,          # Long wars drain administration
    "revolt_ongoing": -1,          # Must divert attention to rebels
    "regency_council": -2,         # No strong leader
    "coalition_against": -1,       # Diplomatic pressure
}

# Example: France at peak vs struggling
# Peak Napoleon: 5 base + 2 bonuses = 7 actions/turn
# 1813 Napoleon: 5 base - 3 penalties = 2 actions/turn
```

### Overextension System (CONCEPTUAL)
```python
def calculate_overextension(nation):
    """
    Overextension = (non-core regions) / (core regions) * 100
    
    Effects at thresholds:
    - 0-25%:   No penalty
    - 25-50%:  -1 action, +10% revolt risk
    - 50-100%: -2 actions, +25% revolt risk, -20% income
    - 100%+:   -3 actions, +50% revolt risk, -50% income
    
    Reduced by:
    - Time (regions become cores after ~10 turns)
    - Cultural acceptance events
    - Puppet states (don't count as direct control)
    """
    pass
```

### Stability System (CONCEPTUAL)
```python
STABILITY_LEVELS = {
    3: {"name": "Triumphant", "action_bonus": +1, "revolt_risk": -50%},
    2: {"name": "Stable", "action_bonus": 0, "revolt_risk": -25%},
    1: {"name": "Uncertain", "action_bonus": 0, "revolt_risk": 0},
    0: {"name": "Unstable", "action_bonus": -1, "revolt_risk": +25%},
    -1: {"name": "Chaotic", "action_bonus": -1, "revolt_risk": +50%},
    -2: {"name": "Collapsing", "action_bonus": -2, "revolt_risk": +100%},
    -3: {"name": "Civil War", "action_bonus": -3, "revolt_risk": "automatic"},
}

# Stability changes from:
# + Major battle victories
# + Successful treaties
# + Leader events
# - Defeats
# - Breaking treaties
# - Overextension
# - War exhaustion
# - Leader death
```

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

### Input Classification System

```
User Input → Input Router → Classifier → Appropriate Handler → Response
```

### Input Categories

| Category | Examples | Handler | Action Cost |
|----------|----------|---------|-------------|
| **COMMAND** | "Ney, attack Wellington" | executor.execute() | Varies |
| **QUERY** | "Where is Davout?", "How much gold?" | query_handler | 0 (free) |
| **ADVICE** | "What should I do?", "Recommend strategy" | advisor_handler | 0 (free) |
| **LORE** | "Tell me about Wellington", "What happened at Austerlitz?" | lore_handler | 0 (free) |
| **ROLEPLAY** | "Ney, how are you feeling?" | roleplay_handler | 0 (free) |
| **META** | "help", "save", "settings", "quit" | meta_handler | 0 (free) |
| **CLARIFICATION** | "attack" (attack what?), "move him" (who?) | clarification_handler | 0 (free) |
| **INVALID** | "asdfghjkl", gibberish | invalid_handler | 0 (free) |
| **INAPPROPRIATE** | Off-topic, out of scope | redirect_handler | 0 (free) |

### Implementation: InputRouter Class

```python
# backend/commands/input_router.py

class InputRouter:
    """Routes ALL user input to appropriate handler. Never crashes."""
    
    def route(self, user_input: str, game_state: dict) -> dict:
        """Main entry point. ALWAYS returns a response."""
        text = user_input.strip().lower()
        
        # 1. META commands (help, save, quit)
        if self._is_meta(text):
            return self._handle_meta(text)
        
        # 2. QUERY patterns (where, how much, what is)
        if self._is_query(text):
            return self._handle_query(text, game_state)
        
        # 3. ADVICE requests (what should I, recommend)
        if self._is_advice(text):
            return self._handle_advice(game_state)
        
        # 4. Try to parse as COMMAND
        parsed = self.parser.parse(user_input)
        if parsed.get("success"):
            return self.executor.execute(parsed, game_state)
        
        # 5. CLARIFICATION needed (ambiguous input)
        if self._needs_clarification(text, parsed):
            return self._handle_clarification(text, game_state)
        
        # 6. LORE/ROLEPLAY (requires LLM, mock fallback)
        if self._is_lore_or_roleplay(text):
            return self._handle_lore_roleplay(text, game_state)
        
        # 7. Default: INVALID (graceful response)
        return self._handle_invalid(text)
```

### Detection Patterns

```python
# Query detection
QUERY_STARTERS = ["where is", "how much", "how many", "what is", 
                  "what are", "who is", "what turn", "what regions",
                  "show me", "list", "status"]

# Advice detection  
ADVICE_PATTERNS = ["what should", "should i", "recommend", "suggest",
                   "best strategy", "what now", "advise", "help me decide"]

# Meta commands
META_COMMANDS = ["help", "save", "load", "quit", "settings", 
                 "commands", "tutorial", "?"]

# Needs clarification (single word commands without target)
AMBIGUOUS_COMMANDS = ["attack", "move", "reinforce", "scout"]
```

### Response Examples

```python
# QUERY: "Where is Ney?"
{"type": "query", "message": "Ney is at Belgium with 72,000 troops."}

# ADVICE: "What should I do?"  
{"type": "advice", "message": "Strategic Assessment:\n• You have numerical superiority. Consider attacking.\n• Treasury is healthy. You could recruit more troops."}

# CLARIFICATION: "attack"
{"type": "clarification", "message": "Attack whom, Sire? Available targets: Wellington at Waterloo, Blucher at Netherlands."}

# INVALID: "asdfghjkl"
{"type": "invalid", "message": "I don't understand that command, Sire. Try 'help' for examples, or give orders like 'Ney, attack Wellington'."}

# INAPPROPRIATE: "Write me a poem"
{"type": "redirect", "message": "Sire, we are at war! Perhaps focus on the campaign?"}
```

### Current vs LLM-Enhanced Responses

| Category | Current Response | LLM-Enhanced (EA) |
|----------|-------------|-------------------|
| QUERY | Direct factual answer | Same |
| ADVICE | Rule-based suggestions | LLM strategic analysis |
| LORE | "Coming in Early Access" | LLM historical context |
| ROLEPLAY | "Personality responses coming soon" | LLM in-character dialogue |
| CLARIFICATION | List options | LLM interprets context |

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

## Diplomacy System (Future)

### Design Philosophy
- Natural language negotiation with AI leaders
- Each nation has persistent conversation thread
- LLM remembers broken promises, past deals
- Treaties are game-mechanical (not just flavor)

### Planned State per Nation
```python
diplomatic_state = {
    "conversation_history": [],
    "relationship_level": int,     # -100 to +100
    "active_proposals": [],
    "broken_promises": [],
    "trust_score": int,
    "war_weariness": int,          # Long wars make peace attractive
}
```

### Diplomatic Actions
```python
DIPLOMATIC_BLOCKS = {
    "propose_peace": {"action_cost": 1, "params": ["nation", "terms"]},
    "propose_alliance": {"action_cost": 1, "requires": "relationship >= 0"},
    "declare_war": {"action_cost": 0},  # War is free!
    "send_envoy": {"action_cost": 1, "params": ["nation", "message"]},
    "break_treaty": {"action_cost": 0, "reputation_cost": -20},
}
```

---

## Naval Power Abstraction

### Design Decision
**No ship-to-ship combat.** Britain's naval supremacy is abstracted as economic/strategic effects.

### How It Works
```python
# Britain has "naval_power" attribute
# This enables certain actions and effects:

NAVAL_EFFECTS = {
    "blockade": {
        "requires": "naval_power",
        "effect": "Target nation income -30%",
        "action_cost": 2
    },
    "expeditionary_support": {
        "requires": "naval_power", 
        "effect": "Can reinforce any coastal region",
    },
    "trade_dominance": {
        "passive": True,
        "effect": "+100 gold/turn from trade"
    }
}

# France can counter with:
# - Continental System (reduce Britain trade income)
# - Coastal fortifications (block expeditions)
# - Alliance with naval powers (unlikely but possible)
```

### Why This Design
- Naval combat is complex to simulate
- Napoleonic Wars were decided on land
- Britain's power was economic/strategic, not tactical
- Keeps focus on land command gameplay

---

## Colonial Power Abstraction

### Design Decision
**Colonies are abstracted as a "Colonial Power" score**, not individually simulated. This explains Britain's wealth without simulating the entire colonial system.

### Colonial Power Mechanics (CONCEPTUAL)

```python
# Colonial Power is a nation attribute (0-100 scale)
COLONIAL_POWER = {
    "Britain": 100,      # Dominant colonial empire
    "France": 40,        # Caribbean, some Africa/India (pre-Napoleon losses)
    "Spain": 60,         # Americas (declining)
    "Portugal": 35,      # Brazil, Africa
    "Netherlands": 30,   # East Indies
    "Austria": 0,        # Landlocked, no colonies
    "Prussia": 0,        # No significant colonies
    "Russia": 5,         # Alaska, mostly land expansion
}

# Effects of Colonial Power:
def calculate_colonial_income(nation, colonial_power):
    """
    Colonial Power directly affects income.
    Britain's wealth comes from colonies, not European land.
    """
    base_colonial_income = colonial_power * 5  # Up to +500 gold/turn for Britain
    return base_colonial_income
```

### What Reduces Colonial Power

```python
COLONIAL_POWER_PENALTIES = {
    "european_instability": -10,    # Per stability level below 0
    "war_exhaustion_high": -15,     # Over 50% war exhaustion
    "blockaded_by_enemy": -20,      # If France blockades Britain (rare)
    "lost_naval_battle": -10,       # If fleet destroyed (event-based)
    "colonial_revolt": -25,         # Random event, more likely when unstable
    "overextension": -5,            # Per 25% overextension
}

# Example: Britain at war for 10 years
# Colonial Power: 100 - 15 (war exhaustion) - 10 (instability) = 75
# Income: 75 * 5 = +375 gold/turn (down from +500)
```

### What Increases Colonial Power

```python
COLONIAL_POWER_BONUSES = {
    "naval_victory": +5,            # Defeating enemy fleet
    "trade_treaty": +10,            # Commercial agreement
    "colonial_conquest": +15,       # Taking enemy colonies (event)
    "stability_high": +5,           # Per stability level above 0
    "continental_system_broken": +10,  # If France's system fails
}
```

### Strategic Implications

```python
# Why this matters for gameplay:

# 1. Britain can fund coalitions indefinitely... unless weakened
#    Napoleon's best strategy: Continental System + exhaust Britain economically

# 2. France capturing colonies is abstracted
#    "Colonial expedition" action: 
#    - Costs 2 actions, 500 gold
#    - Success chance based on naval power difference
#    - Reduces target colonial power by 10-20

# 3. AI behavior driven by colonial power
#    - Low colonial power = more willing to negotiate
#    - High colonial power = can afford long wars

# 4. Victory condition modifier
#    - Controlling all Europe means nothing if Britain funds resistance
#    - Must either: conquer Britain OR reduce their colonial power below 30
```

### Integration with Other Systems

```python
# Colonial Power affects:
colonial_effects = {
    "income": "colonial_power * 5 gold/turn",
    "war_capacity": "High = can fund longer wars",
    "coalition_strength": "Britain funds allies based on colonial power",
    "peace_willingness": "Low colonial power = more willing to negotiate",
    "stability": "Colonial revolts can destabilize home nation",
}

# Player (France) goals regarding colonial power:
# - Continental System reduces British trade (colonial power -2/turn while active)
# - Naval raids (expensive, risky, but can reduce colonial power)
# - Force Britain to overextend in Europe (drains colonial focus)
# - Wait them out (war exhaustion eventually hurts colonial power)
```

---

## Early Access Expansion Plans

### Timeline Change (EA 1.0)
- Current: 40 turns (100 days)
- EA: Year-based (1805-1815), monthly turns
- Each year = 12 turns
- Full campaign = ~120 turns

### Character Death System
```python
# Marshals can die from:
DEATH_CAUSES = {
    "battle": 0.05,      # 5% chance per major defeat
    "illness": 0.02,     # 2% per year, increases with age
    "old_age": 0.10,     # 10% per year over 60
    "assassination": 0.01,  # Rare, plot-driven
}

# When marshal dies:
# 1. LLM generates death narrative
# 2. LLM generates replacement marshal with new personality
# 3. Replacement has lower initial trust/effectiveness
```

### Vassal System
```python
# Conquered nations become vassals with autonomy levels:
AUTONOMY_LEVELS = {
    "puppet": 0,      # Full control, 1 action/turn
    "satellite": 25,  # Some autonomy, may refuse orders
    "ally": 50,       # Equal partner, negotiated actions
    "independent": 100,  # No control
}

# Vassal loyalty affected by:
# - War weariness
# - French defeats
# - Distance from Paris
# - Local nationalism
```

---

## Missing Design Elements (EA Priority)

### CRITICAL: Must Have for Early Access

#### 1. Supply & Logistics System
```python
# Napoleon lost 400,000 men to attrition in Russia, not combat
# Armies NEED supply lines to function

SUPPLY_SYSTEM = {
    "supply_range": 3,  # Regions from friendly territory
    "effects_when_unsupplied": {
        "attrition": "5% strength loss per turn",
        "morale_loss": "-10 per turn",
        "combat_penalty": "-30% effectiveness",
        "forced_retreat": "After 3 turns unsupplied",
    },
    
    # Supply sources:
    "supply_sources": [
        "Friendly controlled regions",
        "Depot buildings (can be built)",
        "Foraging (hostile territory, damages relations)",
    ],
    
    # Strategic implications:
    # - Can't just march to Moscow without supply chain
    # - Cutting enemy supply = winning without fighting
    # - Depots are high-value targets
}
```

#### 2. Manpower Pool System
```python
# France had ~30M people, not infinite soldiers
# Recruitment depletes national manpower

MANPOWER_SYSTEM = {
    "national_pools": {
        "France": 300_000,      # Available for recruitment
        "Prussia": 150_000,
        "Austria": 250_000,
        "Russia": 500_000,      # Vast but slow to mobilize
        "Britain": 100_000,     # Small but professional
    },
    
    "recovery_rate": "2% of max per turn (peacetime)",
    "wartime_recovery": "0.5% per turn",
    
    "recruitment_cost": {
        "gold": 200,
        "manpower": 10_000,     # Deducted from pool
    },
    
    # When manpower exhausted:
    # - Cannot recruit normally
    # - Emergency conscription: -stability, -morale
    # - Scraping the barrel: Low quality troops
}
```

#### 3. Coalition Trigger System
```python
# Why did everyone gang up on Napoleon?
# Coalitions form based on threat + diplomacy

COALITION_TRIGGERS = {
    "threat_level": {
        "calculation": "regions_controlled + recent_conquests + army_size",
        "thresholds": {
            50: "Minor powers nervous",
            75: "Great powers consider coalition",
            100: "Coalition likely forms",
            125: "Coalition certain",
        },
    },
    
    "trigger_events": [
        "Player conquers 3+ regions in one year",
        "Player breaks major treaty",
        "Player defeats great power decisively",
        "Player crowns themselves Emperor",
    ],
    
    "coalition_formation": {
        "lead_time": "2-4 turns warning",
        "can_prevent": "Diplomacy, releasing conquests, tribute",
        "members": "Based on who feels threatened",
    },
}
```

#### 4. Fog of War System
```python
# What does the player actually KNOW vs guess?

FOG_OF_WAR = {
    "visibility_levels": {
        "full": "Own regions, adjacent to own armies",
        "partial": "Scouted regions (decays over time)",
        "rumor": "2+ regions away, vague info",
        "unknown": "No information",
    },
    
    "information_types": {
        "full": ["Army location", "Army size", "Commander", "Morale"],
        "partial": ["Army location", "Approximate size (±20%)"],
        "rumor": ["Army reported in area", "Size unknown"],
        "unknown": ["???"],
    },
    
    "intel_gathering": [
        "Scout action (1 action, reveals 1 region fully)",
        "Spy network (passive, slow intel on enemy)",
        "Captured dispatches (random event)",
        "Allied reports (shared intel)",
    ],
}
```

#### 5. Terrain System
```python
# Mountains, rivers, fortresses matter enormously

TERRAIN_TYPES = {
    "plains": {
        "movement_cost": 1,
        "defender_bonus": 0,
        "attrition": 0,
    },
    "hills": {
        "movement_cost": 1.5,
        "defender_bonus": +20,
        "attrition": 0,
    },
    "mountains": {
        "movement_cost": 2,
        "defender_bonus": +40,
        "attrition": 2,  # % per turn
    },
    "forest": {
        "movement_cost": 1.5,
        "defender_bonus": +15,
        "cavalry_penalty": -30,
    },
    "marsh": {
        "movement_cost": 2,
        "defender_bonus": +10,
        "attrition": 3,
    },
    "river_crossing": {
        "attacker_penalty": -25,
        "requires": "Bridge or ford",
    },
    "fortress": {
        "defender_bonus": +50,
        "requires_siege": True,
        "siege_duration": "3-6 turns",
    },
}
```

#### 6. Attrition System
```python
# Armies lose men just by existing, especially in bad conditions

ATTRITION_FACTORS = {
    "base_attrition": 0.5,  # % per turn just existing
    
    "modifiers": {
        "winter": +3.0,           # % additional
        "hostile_territory": +1.0,
        "unsupplied": +5.0,
        "forced_march": +2.0,
        "mountain_terrain": +2.0,
        "disease_outbreak": +5.0,  # Event
        "over_supply_limit": +2.0, # Too many troops in region
    },
    
    "mitigation": {
        "high_morale": -0.5,
        "experienced_troops": -0.5,
        "supply_depot": -1.0,
        "winter_quarters": -2.0,  # Defensive stance in winter
    },
    
    # Historical example:
    # Napoleon enters Russia: 600,000 troops
    # Reaches Moscow: 100,000 troops
    # Most losses = attrition, not combat
}
```

### IMPORTANT: Should Have for EA

#### 7. Weather & Seasons
```python
SEASONS = {
    "spring": {"months": [3,4,5], "modifier": "normal"},
    "summer": {"months": [6,7,8], "modifier": "optimal_campaigning"},
    "autumn": {"months": [9,10,11], "modifier": "mud_season", "movement": -1},
    "winter": {"months": [12,1,2], "modifier": "harsh", "attrition": +3},
}

# Winter in Russia = death sentence
# Mud season = armies stuck
# Summer = optimal for offense
```

#### 8. Siege Mechanics
```python
SIEGE_SYSTEM = {
    "fortress_levels": {
        1: {"garrison": 5000, "duration": 2},
        2: {"garrison": 10000, "duration": 4},
        3: {"garrison": 20000, "duration": 6},  # Major fortress
    },
    
    "siege_options": {
        "starve_out": "Slow but safe, requires blockade",
        "assault": "Fast but costly, 50% casualties",
        "bombardment": "Moderate speed, requires artillery",
        "negotiate": "Offer terms, may succeed if morale low",
    },
    
    "relief_force": "Breaks siege if arrives",
}
```

#### 9. War Goals & Peace Terms
```python
# What can you demand in peace?

WAR_GOALS = {
    "annex_territory": {
        "warscore_cost": "10-50 per region",
        "aggressive_expansion": "+10 per region",
    },
    "puppet_state": {
        "warscore_cost": "50-100 for whole nation",
        "creates_vassal": True,
    },
    "war_reparations": {
        "warscore_cost": "20-40",
        "gold_received": "500-2000",
    },
    "trade_rights": {
        "warscore_cost": "10-20",
        "income_bonus": "+50 gold/turn",
    },
    "release_nation": {
        "warscore_cost": "30-60",
        "creates_new_nation": True,
    },
}

# Warscore earned from:
# - Battles won
# - Regions occupied
# - Enemy capital held
# - Time at war (ticking warscore if winning)
```

### NICE TO HAVE: Post-EA

- Espionage network system
- Trade route mechanics  
- Legitimacy/government stability
- Religion mechanics (minor for this era)
- Detailed economic simulation
- Leader personality traits affecting army
- Naval battle events (not simulation)

---

## LLM Philosophy: The Golden Rule

> **LLMs explain, react, and color events — they don't cause them.**

### What This Means

```
RULES do:           LLM does:
─────────────       ──────────────────────
Combat math         Battle aftermath narrative
Movement validation Movement flavor text
Economy calculation Treasury warnings in-character
State changes       Explaining state changes
AI action EXECUTION AI action SELECTION (constrained)
```

### Why AI Action Selection IS Safe (Our Approach)

```python
# ChatGPT says: "🚫 AI action selection" - TOO CONSERVATIVE

# Their fear:
llm_output = "destroy_france()"  # LLM invents invalid action
game.execute(llm_output)          # Game breaks

# Our reality:
llm_output = ai_engine.decide(game_state)  # LLM picks from menu
validated = executor.validate(llm_output)   # Executor checks validity
if not validated:
    llm_output = fallback_rules(game_state) # Rule-based backup
result = executor.execute(llm_output)       # Rules handle execution

# LLM can't break anything because:
# 1. Can only choose from VALID building blocks
# 2. Executor validates before executing
# 3. Fallback to rules if LLM fails
# 4. Worst case = suboptimal AI play, not crashes
```

### The Spectrum of LLM Safety

```
SAFE ──────────────────────────────────────────────────► DANGEROUS

Flavor text    Diplomatic    AI action    Combat      State
only           letters       selection    resolution  mutation
                             (constrained)

     ◄── We use these ──►    ◄── Our     ◄── NEVER
                                 limit
```

---

## LLM Flavor Systems (Immersion Layer)

### 1. Dynamic Diplomatic Writing

**Instead of:** "France refuses peace."

**You get:**
> "The French court rejects your proposal with barely concealed contempt. 
> Marshal Berthier hints that Vienna will soon beg on far worse terms."

```python
DIPLOMATIC_LETTER_PROMPT = """
Write a diplomatic letter from {sender} to {recipient}.

Context:
- Relations: {relation_score} (-100 to +100)
- War score: {war_score} (who's winning)
- Recent events: {events}
- Sender personality: {personality}

The letter should:
- Match the sender's national character
- Reflect the power balance
- Be 2-4 sentences
- Sound period-appropriate (1800s formal)

Letter:
"""
```

### 2. Newspapers & Gazettes (Same Event, Different Spin)

**One battle, four perspectives:**

```python
NEWSPAPER_PROMPT = """
Write a brief newspaper excerpt about this event:
{event_description}

Write from the perspective of: {nation}
National bias: {bias_description}
Tone: {winning/losing/neutral}

Keep it to 2-3 sentences. Sound like 1800s journalism.
"""

# Example outputs for "France wins Battle of Austerlitz":

# FRENCH MONITEUR:
# "The Emperor's genius shines again! The armies of the Tsar 
# and Emperor Francis flee in disorder. Europe trembles before France!"

# BRITISH TIMES:
# "Reports from the continent suggest French forces prevailed 
# at Austerlitz. Our coalition allies regroup. The struggle continues."

# AUSTRIAN GAZETTE:
# "Our brave soldiers fought valiantly against overwhelming odds. 
# A tactical withdrawal preserves the army for future operations."

# RUSSIAN BULLETIN:
# "Fog and Austrian incompetence led to temporary setback. 
# The Tsar's armies remain unbroken in spirit."
```

### 3. AI Introspection (Illusion of Intelligence)

**After rule-based AI acts, LLM explains "why":**

```python
# RULES decided: Prussia moves army to Saxony
# LLM explains the "reasoning":

AI_INTROSPECTION_PROMPT = """
You are {nation}'s war council. Explain why you took these actions:
{actions_taken}

Context:
- Your goals: {strategic_goals}
- Current threats: {threats}
- Your personality: {personality}

Speak as if YOU decided this (even though rules did).
2-3 sentences, in-character.
"""

# Output:
# "The Prussian General Staff recognizes the threat to our 
# southern flank. By securing Saxony, we deny the French 
# a staging ground and protect Berlin. Discipline and 
# preparation shall carry the day."
```

**This creates the illusion of strategic thinking while rules do everything.**

### 4. Advisor Commentary (Biased, Not Optimal)

```python
ADVISOR_PERSONALITIES = {
    "marshal": {
        "bias": "aggressive",
        "concerns": ["glory", "victory", "honor"],
        "blind_spots": ["logistics", "politics", "cost"],
    },
    "treasurer": {
        "bias": "conservative", 
        "concerns": ["gold", "debt", "economy"],
        "blind_spots": ["military necessity", "honor"],
    },
    "diplomat": {
        "bias": "cautious",
        "concerns": ["reputation", "alliances", "treaties"],
        "blind_spots": ["military advantage", "decisive action"],
    },
    "spymaster": {
        "bias": "paranoid",
        "concerns": ["threats", "conspiracies", "information"],
        "blind_spots": ["opportunities", "trust"],
    },
}

# KEY RULE: Advisors give BIASED advice, not OPTIMAL advice
# They disagree with each other
# Player must weigh perspectives

ADVISOR_PROMPT = """
You are the {role} advising {ruler}.

Situation: {situation}
Your personality: {personality}
Your concerns: {concerns}

Give your perspective in 1-2 sentences.
Be biased toward your concerns. You may be wrong.
"""

# Example - "Should we attack Austria?"

# MARSHAL: "Strike now while they're divided! 
#           Glory awaits those who seize the moment!"

# TREASURER: "Another war? The treasury barely survived the last. 
#             Perhaps negotiation serves us better."

# DIPLOMAT: "An attack now would alarm Prussia and Russia. 
#            Consider the coalition this might provoke."
```

### 5. Pattern-Based Player Reputation

```python
# Track player behavior patterns
PLAYER_PATTERNS = {
    "treaties_broken": 0,
    "wars_started": 0,
    "allies_betrayed": 0,
    "mercy_shown": 0,
    "ruthless_actions": 0,
}

# Flavor text shifts based on patterns
REPUTATION_FLAVOR = {
    "betrayer": "Other nations eye your ambassadors with suspicion...",
    "warmonger": "Europe whispers of the 'Corsican Ogre'...",
    "merciful": "Even enemies speak grudgingly of your honor...",
    "cautious": "Some call it wisdom. Others, timidity...",
}

# AI nations reference this in diplomatic text
# Creates consequences without mechanical changes
```

### 6. Turn-End Narrative Summary

```python
TURN_SUMMARY_PROMPT = """
Summarize this turn's events as a historical narrator.

Events: {all_turn_events}
Current situation: {situation}
Dramatic tension: {what's at stake}

Write 3-4 sentences. Be dramatic but accurate.
End with a hook about what might happen next.
Sound like a history documentary narrator.
"""

# Output:
# "The summer of 1805 drew to a close with French eagles 
# advancing across Bavaria. Vienna trembled as Napoleon's 
# Grande Armée swept aside all opposition. Yet in the north, 
# Prussian drums began to beat. The Tsar's armies marched west. 
# The decisive hour approached..."
```

### 7. Battle Aftermath Reports

```python
BATTLE_AFTERMATH_PROMPT = """
Write a brief battle aftermath report.

Battle: {battle_name}
Victor: {winner}
Casualties: {attacker_casualties}, {defender_casualties}
Outcome: {outcome_type}

Write as a field report to the commanding general.
Include: the human cost, morale impact, strategic meaning.
2-3 sentences. Period-appropriate tone.
"""

# Output:
# "The fields outside Ulm are littered with the wreckage of 
# victory. We hold the ground, but the ranks are thin and 
# the men exhausted. The Austrians flee south. Shall we pursue?"
```

### LLM Call Budget (Realistic)

```python
LLM_CALL_BUDGET = {
    "per_turn_max": 3,          # Keep costs manageable
    "cache_duration": "1_turn",  # Reuse expensive calls
    
    # Priority order (if budget limited):
    "priority": [
        "turn_summary",          # 1 call, high impact
        "marshal_response",      # Player-facing
        "ai_introspection",      # Makes AI feel smart
        "newspaper",             # Can skip if tight
    ],
}

# One prompt can generate multiple outputs:
# "Write newspaper excerpts for France, Britain, Austria, Prussia"
# = 1 LLM call → 4 different texts
```

---

## Nation AI: Decision Trees + Dynamic Relevance

### The Hybrid Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    NATION AI SYSTEM                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Every nation has: DECISION TREE (always runs)             │
│   Some nations get: LLM ENHANCEMENT (based on relevance)    │
│                                                              │
│   Relevance is DYNAMIC, not static tiers!                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### The Problem with Static Tiers

```python
# WRONG - Static tiers miss the chaos of history:

STATIC_TIERS = {
    "great_power": ["France", "Britain", "Prussia", "Austria", "Russia"],
    "secondary": ["Spain", "Bavaria", "Netherlands"],
    "minor": ["Saxony", "Naples", "Portugal"],  # ← WRONG! Portugal was CRITICAL
}

# In reality:
# - Portugal 1807: Minor backwater
# - Portugal 1808: CRITICAL (Peninsular War begins, Wellington lands)
# - Saxony 1813: Minor German state
# - Saxony 1813 (Leipzig): PIVOTAL (defection changes battle outcome)
# - Bavaria 1805: French ally
# - Bavaria 1813: Switches sides, opens southern Germany
```

### Dynamic Relevance System

```python
# backend/ai/relevance_engine.py

class RelevanceEngine:
    """
    Calculates which nations deserve LLM attention THIS TURN.
    Relevance is contextual, not permanent.
    """
    
    def calculate_relevance(self, nation: str, game_state: dict) -> float:
        """
        Returns 0.0-1.0 relevance score.
        High relevance = gets LLM call.
        """
        score = 0.0
        
        # Base relevance (great powers start higher)
        score += BASE_RELEVANCE.get(nation, 0.1)
        
        # ESCALATION TRIGGERS (can make anyone important)
        score += self._war_involvement(nation, game_state)
        score += self._border_tension(nation, game_state)
        score += self._player_interaction(nation, game_state)
        score += self._strategic_position(nation, game_state)
        score += self._recent_events(nation, game_state)
        score += self._diplomatic_crisis(nation, game_state)
        score += self._betrayal_potential(nation, game_state)
        
        return min(1.0, score)  # Cap at 1.0


BASE_RELEVANCE = {
    # Great powers always somewhat relevant
    "France": 0.4, "Britain": 0.4, "Prussia": 0.4, 
    "Austria": 0.4, "Russia": 0.4,
    
    # Secondary powers - moderate base
    "Spain": 0.2, "Bavaria": 0.2, "Netherlands": 0.2,
    
    # Minor powers - low base, but CAN escalate
    "Saxony": 0.1, "Naples": 0.1, "Portugal": 0.1,
    "Württemberg": 0.1, "Baden": 0.1, "Denmark": 0.1,
}
```

### Escalation Triggers (What Makes Nations Important)

```python
ESCALATION_TRIGGERS = {
    
    # ════════════════════════════════════════════════════════
    # MILITARY ESCALATION
    # ════════════════════════════════════════════════════════
    
    "at_war_with_player": +0.5,        # Actively fighting player
    "at_war_with_great_power": +0.3,   # In a major war
    "army_in_combat_zone": +0.2,       # Troops near fighting
    "just_won_battle": +0.2,           # Recent victory (momentum)
    "just_lost_battle": +0.2,          # Recent defeat (desperate)
    "being_invaded": +0.4,             # Existential threat
    
    # ════════════════════════════════════════════════════════
    # GEOGRAPHIC ESCALATION  
    # ════════════════════════════════════════════════════════
    
    "borders_active_war": +0.3,        # War on their doorstep
    "strategic_chokepoint": +0.2,      # Controls key territory
    "player_army_adjacent": +0.3,      # Player threatening them
    "between_two_powers": +0.2,        # Caught in the middle
    
    # ════════════════════════════════════════════════════════
    # DIPLOMATIC ESCALATION
    # ════════════════════════════════════════════════════════
    
    "alliance_offer_pending": +0.3,    # Someone wants them
    "betrayal_imminent": +0.4,         # About to switch sides
    "war_declaration_considering": +0.3,  # Might join war
    "peace_negotiation_key": +0.3,     # Critical to peace deal
    "player_demanded_something": +0.4, # Player interacted directly
    
    # ════════════════════════════════════════════════════════
    # CHAOS ESCALATION (Random History Moments)
    # ════════════════════════════════════════════════════════
    
    "succession_crisis": +0.3,         # Leadership unstable
    "revolution_brewing": +0.4,        # Internal chaos
    "foreign_intervention": +0.3,      # Outside power meddling
    "unexpected_alliance": +0.3,       # Diplomatic surprise
    "key_figure_died": +0.2,           # Leadership change
}

def _war_involvement(self, nation: str, game_state: dict) -> float:
    """How involved is this nation in current wars?"""
    score = 0.0
    
    if game_state.is_at_war(nation, game_state.player_nation):
        score += 0.5  # Fighting the player = very relevant
    
    if game_state.is_at_war_with_any_great_power(nation):
        score += 0.3
    
    if game_state.has_army_in_combat_zone(nation):
        score += 0.2
    
    return score

def _player_interaction(self, nation: str, game_state: dict) -> float:
    """Has the player been interacting with this nation?"""
    score = 0.0
    
    recent_turns = game_state.get_recent_interactions(nation, turns=3)
    
    if "diplomatic_message" in recent_turns:
        score += 0.3  # Player sent them something
    
    if "demand" in recent_turns:
        score += 0.4  # Player demanded something
    
    if "war_declared" in recent_turns:
        score += 0.5  # Player declared war
    
    if "army_moved_adjacent" in recent_turns:
        score += 0.2  # Player moved army nearby
    
    return score

def _betrayal_potential(self, nation: str, game_state: dict) -> float:
    """Is this nation likely to switch sides?"""
    score = 0.0
    
    # Check for historical "betrayal moments"
    loyalty = game_state.get_alliance_loyalty(nation)
    war_weariness = game_state.get_war_weariness(nation)
    losing_side = game_state.is_on_losing_side(nation)
    
    if loyalty < 30 and war_weariness > 50:
        score += 0.3
    
    if losing_side and loyalty < 50:
        score += 0.2  # Might defect like Saxony at Leipzig
    
    if game_state.has_been_bribed(nation):
        score += 0.2
    
    return score
```

### The Relevance Threshold

```python
class NationController:
    """Decides which nations get LLM calls each turn."""
    
    # How relevant must a nation be to get LLM call?
    LLM_THRESHOLD = 0.5
    
    # Maximum LLM calls per turn (budget control)
    MAX_LLM_CALLS = 5
    
    def process_all_nations(self, game_state: dict) -> dict:
        """Process all nations, allocate LLM calls by relevance."""
        
        # Calculate relevance for everyone
        relevance_scores = {}
        for nation in game_state.all_nations:
            relevance_scores[nation] = self.relevance_engine.calculate_relevance(
                nation, game_state
            )
        
        # Sort by relevance
        sorted_nations = sorted(
            relevance_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Allocate LLM calls to most relevant
        llm_budget = self.MAX_LLM_CALLS
        results = {}
        
        for nation, relevance in sorted_nations:
            if relevance >= self.LLM_THRESHOLD and llm_budget > 0:
                # HIGH RELEVANCE: LLM decides + explains
                results[nation] = self._process_with_llm(nation, game_state)
                llm_budget -= 1
            else:
                # LOW RELEVANCE: Rules only
                results[nation] = self._process_with_rules(nation, game_state)
        
        return results
```

### Example: Portugal Escalation

```python
# Turn 1: Portugal is irrelevant
# relevance("Portugal") = 0.1 (base) = 0.1
# Result: Decision tree only, template text

# Turn 5: France invades Spain, threatens Portugal
# relevance("Portugal") = 0.1 (base) 
#                       + 0.3 (borders active war)
#                       + 0.3 (player army adjacent)
#                       = 0.7
# Result: LLM call! Portugal gets personality, makes decisions

# Portugal's LLM response:
# "The court in Lisbon watches French armies cross the Pyrenees 
#  with growing alarm. Prince Regent João weighs impossible choices:
#  submit to Napoleon's demands, or flee to Brazil and resist.
#  Britain promises naval support... but can they truly protect us?"

# Turn 8: Britain lands troops, Portugal joins coalition
# relevance("Portugal") = 0.1 (base)
#                       + 0.5 (at war with player)
#                       + 0.3 (alliance offer accepted)
#                       + 0.2 (strategic chokepoint)
#                       = 1.0+ (capped at 1.0)
# Result: Full LLM treatment, major player in the war
```

### Example: Saxony at Leipzig (Betrayal)

```python
# Turn 20: Saxony is French ally (minor)
# relevance("Saxony") = 0.1 (base)
#                     + 0.2 (army in combat zone)
#                     = 0.3
# Result: Decision tree, follows France

# Turn 22: Battle of Leipzig begins, France losing
# relevance("Saxony") = 0.1 (base)
#                     + 0.2 (army in combat zone)
#                     + 0.4 (betrayal imminent - losing side, low loyalty)
#                     + 0.3 (between two powers)
#                     = 1.0
# Result: LLM call for CRITICAL decision moment

# LLM prompt includes:
# - Saxony's war weariness (high)
# - Alliance loyalty to France (crumbling)
# - Coalition offers (Prussia promising territory)
# - Battle situation (France surrounded)

# LLM might decide: DEFECT
# "In the chaos of battle, Saxon regiments wheel about. 
#  Their guns, once aimed at Prussians, now fire into 
#  French ranks. King Frederick Augustus watches in silence
#  as his kingdom changes sides. Necessity, he tells himself.
#  Not betrayal. Necessity."
```

### Decision Tree Structure (Always Runs)

```python
class NationDecisionTree:
    """
    Rule-based decisions for ALL nations.
    LLM enhances but never replaces this.
    """
    
    def decide(self, nation: str, game_state: dict) -> list[Action]:
        """Priority-based decision tree."""
        
        personality = NATION_PERSONALITIES[nation]
        situation = self._analyze_situation(nation, game_state)
        
        # ══════════════════════════════════════════════════
        # PRIORITY 1: SURVIVAL (always checked first)
        # ══════════════════════════════════════════════════
        if situation.capital_threatened:
            return self._survival_mode(nation, game_state)
        
        if situation.army_destroyed:
            return self._desperate_measures(nation, game_state)
        
        # ══════════════════════════════════════════════════
        # PRIORITY 2: ACTIVE WAR DECISIONS
        # ══════════════════════════════════════════════════
        if situation.at_war:
            # Should we seek peace?
            if self._should_seek_peace(nation, situation, personality):
                return [Action("propose_peace", target=situation.strongest_enemy)]
            
            # Should we betray our allies?
            if self._should_switch_sides(nation, situation, personality):
                return [Action("defect", target=situation.current_alliance)]
            
            # Fight or defend?
            if personality["aggression"] > 0.5 and situation.military_advantage:
                return self._offensive_operations(nation, game_state)
            else:
                return self._defensive_operations(nation, game_state)
        
        # ══════════════════════════════════════════════════
        # PRIORITY 3: PEACE BUT THREATENED
        # ══════════════════════════════════════════════════
        if situation.neighbor_at_war:
            # Prepare for war spreading
            return self._mobilization(nation, game_state)
        
        if situation.player_threatening:
            # Player army nearby, diplomacy needed
            if personality["courage"] < 0.4:
                return [Action("appease", target="player")]
            else:
                return [Action("prepare_defense")]
        
        # ══════════════════════════════════════════════════
        # PRIORITY 4: OPPORTUNISM
        # ══════════════════════════════════════════════════
        opportunity = self._find_opportunity(nation, game_state)
        if opportunity and personality["opportunism"] > 0.5:
            return [Action("exploit_opportunity", target=opportunity)]
        
        # ══════════════════════════════════════════════════
        # PRIORITY 5: PEACETIME DEVELOPMENT
        # ══════════════════════════════════════════════════
        return self._peacetime_actions(nation, game_state)
    
    def _should_switch_sides(self, nation, situation, personality) -> bool:
        """
        The Saxony-at-Leipzig calculation.
        When do nations betray their allies?
        """
        # Factors that increase betrayal chance:
        betrayal_score = 0
        
        # Losing the war badly
        if situation.alliance_war_score < -30:
            betrayal_score += 30
        
        # Low loyalty to current alliance
        betrayal_score += (100 - situation.alliance_loyalty) * 0.3
        
        # High war weariness
        betrayal_score += situation.war_weariness * 0.3
        
        # Been offered good terms by enemy
        if situation.enemy_offering_terms:
            betrayal_score += 20
        
        # Personality factors
        betrayal_score *= personality["pragmatism"]
        betrayal_score *= (1 - personality["honor"])
        
        # Random factor (history is chaotic)
        betrayal_score += random.randint(-10, 10)
        
        return betrayal_score > 60  # Threshold for defection


NATION_PERSONALITIES = {
    # Great Powers
    "France": {
        "aggression": 0.8, "courage": 0.9, "pragmatism": 0.6,
        "honor": 0.4, "opportunism": 0.7,
    },
    "Britain": {
        "aggression": 0.4, "courage": 0.7, "pragmatism": 0.8,
        "honor": 0.6, "opportunism": 0.5,
    },
    "Prussia": {
        "aggression": 0.6, "courage": 0.8, "pragmatism": 0.5,
        "honor": 0.7, "opportunism": 0.4,
    },
    "Austria": {
        "aggression": 0.3, "courage": 0.5, "pragmatism": 0.8,
        "honor": 0.6, "opportunism": 0.6,
    },
    "Russia": {
        "aggression": 0.5, "courage": 0.7, "pragmatism": 0.4,
        "honor": 0.5, "opportunism": 0.3,
    },
    
    # Secondary/Minor - more likely to bend
    "Bavaria": {
        "aggression": 0.3, "courage": 0.4, "pragmatism": 0.9,  # Very pragmatic
        "honor": 0.3, "opportunism": 0.8,  # Switched sides twice historically
    },
    "Saxony": {
        "aggression": 0.2, "courage": 0.3, "pragmatism": 0.8,
        "honor": 0.4, "opportunism": 0.7,  # Leipzig defection
    },
    "Portugal": {
        "aggression": 0.3, "courage": 0.6, "pragmatism": 0.5,
        "honor": 0.7, "opportunism": 0.3,  # Loyal to Britain historically
    },
    "Spain": {
        "aggression": 0.5, "courage": 0.8, "pragmatism": 0.2,
        "honor": 0.9, "opportunism": 0.2,  # Proud, resisted to the end
    },
}
```

### Random Historical Events (Chaos Generator)

```python
class ChaosEngine:
    """
    Generates random events that make minor nations suddenly important.
    Simulates the unpredictability of history.
    """
    
    CHAOS_EVENTS = [
        {
            "name": "Succession Crisis",
            "description": "The {nation} throne is disputed",
            "relevance_boost": +0.4,
            "effects": ["instability", "foreign_intervention_possible"],
            "weight": 0.02,  # 2% chance per nation per turn
        },
        {
            "name": "Popular Uprising",
            "description": "The people of {nation} rise against their rulers",
            "relevance_boost": +0.5,
            "effects": ["instability", "potential_revolution"],
            "weight": 0.01,
        },
        {
            "name": "Secret Alliance Revealed",
            "description": "{nation} has been negotiating with {enemy}",
            "relevance_boost": +0.3,
            "effects": ["diplomatic_crisis", "trust_broken"],
            "weight": 0.02,
        },
        {
            "name": "Key General Dies",
            "description": "{nation}'s best commander has died",
            "relevance_boost": +0.2,
            "effects": ["military_weakness", "mourning"],
            "weight": 0.03,
        },
        {
            "name": "Economic Collapse",
            "description": "{nation}'s treasury is empty",
            "relevance_boost": +0.3,
            "effects": ["desperate", "seeking_peace_or_plunder"],
            "weight": 0.02,
        },
        {
            "name": "Foreign Gold Arrives",
            "description": "{nation} receives substantial subsidies",
            "relevance_boost": +0.2,
            "effects": ["emboldened", "might_enter_war"],
            "weight": 0.03,
        },
        {
            "name": "Nationalist Awakening",  
            "description": "Patriotic fervor sweeps {nation}",
            "relevance_boost": +0.3,
            "effects": ["resistance_to_occupation", "won't_surrender"],
            "weight": 0.02,
        },
    ]
    
    def roll_for_chaos(self, game_state: dict) -> list[Event]:
        """Check each nation for random events."""
        events = []
        
        for nation in game_state.all_nations:
            for event_template in self.CHAOS_EVENTS:
                if random.random() < event_template["weight"]:
                    # Chaos strikes!
                    event = self._create_event(nation, event_template, game_state)
                    events.append(event)
                    
                    # Boost nation's relevance
                    game_state.add_relevance_modifier(
                        nation, 
                        event_template["relevance_boost"],
                        duration=3  # Lasts 3 turns
                    )
        
        return events
```

### Summary: The Complete Flow

```
TURN START
    │
    ▼
┌─────────────────────────────────────────┐
│  CHAOS ENGINE                           │
│  Roll for random events                 │
│  (Succession crisis, uprising, etc.)    │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  RELEVANCE ENGINE                       │
│  Calculate relevance for ALL nations    │
│  (Base + Escalation triggers + Chaos)   │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  SORT BY RELEVANCE                      │
│  Top 5 get LLM calls                    │
│  Rest use decision trees only           │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  FOR EACH NATION:                       │
│                                         │
│  if relevance >= 0.5 AND budget > 0:    │
│      LLM suggests actions               │
│      LLM explains "reasoning"           │
│  else:                                  │
│      Decision tree chooses actions      │
│      Template text for explanation      │
│                                         │
│  Executor validates all actions         │
│  Rules execute all actions              │
└─────────────────────────────────────────┘
    │
    ▼
TURN END
```

### What LLM Should NEVER Do

```python
LLM_FORBIDDEN = [
    "Calculate combat results",      # Rules only
    "Determine movement validity",   # Rules only  
    "Compute economy/income",        # Rules only
    "Mutate game state directly",    # Rules only
    "Generate random numbers",       # Use seeded RNG
    "Make final decisions",          # Can suggest, rules decide
]

# If it changes numbers → RULES ONLY
# If it generates text → LLM OK
```

### Token Monetization & LLM Options (EA)

**Three ways users can access LLM features:**

```python
LLM_ACCESS_MODES = {
    # ============================================================
    # 1. FREE TIER (Always Available)
    # ============================================================
    "free_tier": {
        "mock_parsing": True,           # Keyword matching always works
        "llm_responses": False,         # No personality dialogue
        "ai_nations": "rule_based",     # Simple AI, no LLM
        "turn_summaries": False,        # No narrative generation
        "diplomatic_chat": False,       # No LLM negotiation
        "cost": "Free forever",
    },
    
    # ============================================================
    # 2. IN-HOUSE TOKEN PACKAGES (Buy in UI)
    # ============================================================
    "token_packages": {
        "description": "Purchase tokens through game UI",
        "payment": "Stripe/PayPal integration",
        "tokens_stored": "Server-side per user account",
        
        "packages": {
            "starter": {
                "price": "$2.99",
                "tokens": 50_000,        # ~50 full games
                "per_game": "~$0.06",
            },
            "standard": {
                "price": "$9.99",
                "tokens": 200_000,       # ~200 games
                "per_game": "~$0.05",
            },
            "enthusiast": {
                "price": "$24.99",
                "tokens": 600_000,       # ~600 games
                "per_game": "~$0.04",
            },
        },
        
        "ui_features": [
            "Token balance shown in settings",
            "Low balance warning (< 5000 tokens)",
            "Purchase button in-game",
            "Usage tracking per feature",
        ],
    },
    
    # ============================================================
    # 3. BRING YOUR OWN KEY (BYOK)
    # ============================================================
    "byok": {
        "description": "Use your own Anthropic API key",
        "cost_to_us": "$0",
        "cost_to_user": "Their API costs (~$0.50-1.00/game)",
        
        "setup": [
            "User enters API key in settings",
            "Key stored locally (never sent to our servers)",
            "All LLM calls go direct to Anthropic",
            "No token limits",
        ],
        
        "advantages": [
            "Power users who want unlimited access",
            "Developers testing/modding",
            "Users with existing Anthropic accounts",
            "No ongoing cost to us",
        ],
        
        "ui_features": [
            "API key input field (masked)",
            "Key validation on entry",
            "Clear 'using your key' indicator",
            "Easy switch back to token mode",
        ],
    },
}
```

### Backend Architecture for Token System

```python
# backend/ai/token_manager.py

class TokenManager:
    """Manages LLM access modes and token consumption."""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.mode = self._determine_mode()
    
    def _determine_mode(self) -> str:
        """Determine which LLM mode to use."""
        if self._has_byok_key():
            return "byok"
        elif self._has_tokens():
            return "in_house"
        else:
            return "free"
    
    def can_use_llm(self, feature: str) -> bool:
        """Check if user can use LLM for a feature."""
        if self.mode == "free":
            return False
        if self.mode == "byok":
            return True  # No limits
        if self.mode == "in_house":
            estimated_cost = self._estimate_tokens(feature)
            return self.get_balance() >= estimated_cost
        return False
    
    def consume_tokens(self, actual_usage: int) -> bool:
        """Deduct tokens after LLM call."""
        if self.mode != "in_house":
            return True  # BYOK doesn't track
        
        current = self.get_balance()
        if current < actual_usage:
            return False
        
        self._update_balance(current - actual_usage)
        return True
    
    def get_llm_client(self):
        """Return appropriate LLM client based on mode."""
        if self.mode == "byok":
            return LLMClient(api_key=self._get_byok_key())
        elif self.mode == "in_house":
            return LLMClient(api_key=MASTER_API_KEY)  # Our key
        else:
            return MockLLMClient()  # Free tier fallback

# Token costs by feature (estimated)
TOKEN_COSTS = {
    "command_parse": 200,        # Haiku, cheap
    "marshal_response": 800,     # Sonnet, personality
    "ai_nation_turn": 1500,      # Sonnet, strategy
    "turn_summary": 1000,        # Sonnet, narrative
    "diplomatic_chat": 1200,     # Sonnet, negotiation
    "lore_query": 600,           # Sonnet, historical
}
```

### UI Requirements for Token System

```gdscript
# Settings screen needs:
# 1. Current mode indicator ("Free" / "Tokens: 45,230" / "Using Your Key")
# 2. Token purchase button (opens payment modal)
# 3. BYOK key input field
# 4. Usage history/stats
# 5. Mode switch controls

# In-game indicators:
# - Subtle token balance in corner (if using tokens)
# - "LLM Enhanced" badge on features using real LLM
# - Warning when balance low
```

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

### Current State (Testing)
- 13 hardcoded regions in `region.py`
- Programmatic circles + lines in `map.gd`
- Simplified Western Europe
- **Purpose:** Test gameplay mechanics, not final map

### Future Vision (Early Access)
**EU4-style 2D map of 1805 Europe**

```python
# Target scope:
MAP_VISION = {
    "style": "EU4 political map",      # 2D, colored provinces
    "time_period": "1805",              # Pre-Austerlitz Europe
    "region_count": "200-400",          # Full Europe granularity
    "visual_approach": "Polygon2D",     # Real borders, not circles
    
    # Geographic coverage:
    "regions": {
        "western_europe": ["France", "Spain", "Portugal", "Britain"],
        "central_europe": ["Prussia", "Austria", "Bavaria", "Saxony", "Poland"],
        "eastern_europe": ["Russia", "Ottoman"],
        "italian_states": ["Piedmont", "Milan", "Venice", "Naples", "Papal States"],
        "minor_states": ["Switzerland", "Netherlands", "Denmark", "Sweden"],
    }
}
```

### Map Implementation Phases

**Phase 1 (Current):** Testing map
- 13 regions, circles
- Validate gameplay loop
- No art investment yet

**Phase 2 (Pre-EA):** Enhanced testing map
- Same 13 regions
- Polygon2D real shapes
- Dynamic colors on conquest
- Flash animations

**Phase 3 (Early Access):** Full Europe
- Historical 1805 borders
- Province-level granularity
- EU4-style aesthetic
- Zoomable/pannable
- Region tooltips with info

---

## Map Transition Strategy

### When to Commission Real Map Art

**DO NOT commission art until:**
1. ✅ Core gameplay loop is FUN and validated
2. ✅ Action economy feels right
3. ✅ Combat/conquest mechanics finalized
4. ✅ Region count decided (200? 300? 400?)
5. ✅ EA feature scope locked
6. ⏳ You have players saying "this is fun but the map is ugly"

**Recommended timing:**
- **Now:** Keep testing with circles/programmatic
- **After playtesting:** Get player feedback
- **Pre-EA (2-4 weeks before):** Commission map art
- **EA Launch:** Ship with real map

### How to Source the Map

**Option 1: Commission Artist (Recommended)**
```
Cost: $300-800 for EU4-style political map
Where: Fiverr, ArtStation, DeviantArt commissions
Deliverable: SVG or layered PSD with individual provinces
Time: 2-4 weeks typically

Requirements to specify:
- EU4/Victoria aesthetic
- 1805 historical borders
- Each province as separate path/layer
- Consistent art style
- Color-neutral (you'll recolor in code)
```

**Option 2: Historical Map + Trace**
```
Cost: $0-100 (your time or cheap trace)
Source: Public domain 1805 maps
Process: Trace provinces in Inkscape/Illustrator
Deliverable: SVG with path IDs matching region names
Time: 10-20 hours of work

Pros: Historically accurate
Cons: Time consuming, may look amateur
```

**Option 3: Procedural Generation**
```
Cost: Development time only
Process: Generate Voronoi regions, fit to coastlines
Tools: Godot + algorithms
Deliverable: Runtime-generated map

Pros: Infinitely scalable, moddable
Cons: Doesn't look historical, more dev work
```

**Recommendation:** Option 1 for EA. Commission when you know exact region count.

### Graceful Code Transition

**Key Principle:** Map data is SEPARATE from map rendering.

```python
# backend/models/region.py - Data layer (doesn't care about visuals)

# Current (13-region test map):
REGIONS_DATA = {
    "Paris": {"adjacent": ["Belgium", "Lyon"], "income": 100},
    # ... 13 regions
}

# Future (EA): Just add more regions, same structure
REGIONS_DATA = {
    "Ile-de-France": {"adjacent": ["Champagne", "Normandy"], "income": 150},
    "Champagne": {"adjacent": ["Ile-de-France", "Lorraine"], "income": 80},
    # ... 200+ regions
}

# The executor, combat, pathfinding don't care how many regions exist
# They just query the data structure
```

```gdscript
# godot-client/scenes/map.gd - Visual layer

# Step 1: Abstract region rendering (do this NOW)
class_name MapRenderer

# Instead of hardcoded positions:
var region_visuals = {}  # region_name -> visual_node

func load_map_data(data_source: String):
    """Load map from external file, not hardcoded."""
    var data = load_region_data(data_source)
    for region_name in data:
        var visual = create_region_visual(data[region_name])
        region_visuals[region_name] = visual

func create_region_visual(region_data: Dictionary) -> Node2D:
    """Create visual for a region. Override for different map styles."""
    # Current: Circle at position
    # Future: Polygon2D from vertex data
    pass

func update_region_color(region_name: String, color: Color):
    """Update any region regardless of visual style."""
    if region_visuals.has(region_name):
        region_visuals[region_name].set_color(color)
```

### Data File Structure for Real Map

```json
// assets/maps/europe_1805.json
{
    "map_id": "europe_1805",
    "version": "1.0",
    "regions": {
        "Ile-de-France": {
            "display_name": "Île-de-France",
            "polygon_points": [[100,200], [150,180], [180,220], ...],
            "center": [140, 200],
            "label_position": [140, 195],
            "adjacent": ["Champagne", "Normandy", "Orleans", "Burgundy"],
            "income": 150,
            "is_capital": true,
            "culture": "French",
            "terrain": "plains"
        },
        // ... 200+ more regions
    },
    "sea_zones": {
        "English_Channel": {
            "polygon_points": [...],
            "adjacent_land": ["Normandy", "Picardy", "Kent", "Sussex"]
        }
    },
    "visual_settings": {
        "default_scale": 1.0,
        "min_zoom": 0.5,
        "max_zoom": 3.0
    }
}
```

### Migration Checklist

```markdown
## Pre-Migration (Now)
- [ ] Abstract region rendering in map.gd
- [ ] Move region data to external JSON file
- [ ] Create MapRenderer class with override points
- [ ] Test that gameplay works with any region count

## Migration Day (When art ready)
- [ ] Import new map JSON with 200+ regions
- [ ] Update backend REGIONS_DATA to match
- [ ] Test pathfinding with larger graph
- [ ] Verify all region names match between frontend/backend
- [ ] Performance test with full region count
- [ ] Add zoom/pan controls for larger map

## Post-Migration
- [ ] Adjust balance for more granular regions
- [ ] Update AI pathfinding weights
- [ ] Add region tooltips
- [ ] Add minimap for navigation
```

### Why EU4 Style?
- Proven readable at strategic scale
- Works with many regions
- Players understand the visual language
- Supports mod-friendly data files
- 2D is much simpler than 3D

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

### Phase 1: Foundation ✅ COMPLETE
- ✅ Core gameplay loop
- ✅ Action economy (4 actions/turn)
- ✅ Combat resolution
- ✅ Victory/defeat conditions
- ✅ Full turn cycle working

### Phase 2: Combat & AI ✅ COMPLETE
- ✅ Disobedience system (Trust/Insist/Compromise)
- ✅ Authority & Vindication tracking
- ✅ Drill/Fortify/Stance mechanics
- ✅ Enemy AI (personality-driven decision tree)
- ✅ Enemy Phase popup UI
- ✅ Smart AI safety evaluation
- ✅ Attacker movement on victory

### Phase 2.5: Autonomy Foundation ✅ COMPLETE
- ✅ Grant Autonomy → marshal uses Enemy AI decision tree
- ✅ Autonomous marshal processing in turn flow
- ✅ Autonomy narrative outcomes (success/neutral/failure text with relative trust gains)
- ✅ Administrative Role option (sidelined marshal → +1 action/turn)
- ✅ Redemption system overhaul (removed Demand Obedience, added dynamic option availability)

### Phase 3: Fun Factor & Historical Drama 📋 PLANNED

**Target: May 2026 | Design Goal: 8.5/10 fun rating**

#### 3.1 Hearing the Guns System (SIGNATURE FEATURE)
The "Grouchy moment" - marshals detect nearby battles and respond based on personality.

```python
# Event broadcast when battle starts
EVENT_BLOCKS["hearing_the_guns"] = {
    "trigger": "battle_starts_within_2_regions",
    "text": "{marshal} hears cannon fire from {location}!",
    "personality_response": {
        "aggressive": "I hear the guns! Let me march to join the battle!",
        "cautious": "Battle rages at {location}. Should I hold or intervene?",
        "literal": "I hear cannon fire, but my orders are clear. I continue as directed."
    },
    "player_options": [
        {"id": "redirect", "text": "March to the guns!", "cancels_current_order": True},
        {"id": "continue", "text": "Continue as ordered"},
        {"id": "judgment", "text": "Use your judgment", "triggers": "personality_default"}
    ]
}

# If no player response by turn end:
# - Aggressive: auto-redirects to battle
# - Cautious: holds position
# - Literal: continues original order (THE GROUCHY MOMENT)
```

#### 3.2 Vindication & Causality System
Make disobedience feel two-sided - player learns when marshals were right.

**Post-Battle Counterfactual (opt-in):**
```
"Battle of Waterloo - Analysis:
- You insisted on attacking despite Davout's objection
- Davout's alternative (fortify) would have resulted in ~40% fewer casualties
- Davout's vindication score: +1"
```

**Trust Trajectory Warnings:**
```
At trust 40 (dropping): "Ney's trust has fallen 25 points over 6 turns. Consider his counsel."
```

**Marshal Memory Callbacks:**
```
When similar situation arises:
"Sire, the last time you ordered a frontal assault at these odds, we lost half our force."
```

**Reconciliation Events (at trust 35, recovering from <20):**
```
"Sire... I may have been too proud. Your counsel at [battle] was wiser than I admitted."
Options: [Accept gracefully +8 trust, +2 authority] [Rub it in +3 trust, +8 authority]
```

#### 3.3 Grouchy Ambiguity Detection
Implement the LITERAL personality's core mechanic.

```python
# Vague order triggers clarification
"Sire, you say 'handle the Prussians.' Do you mean:
- Pursue and destroy them
- Pin them in place
- Scout their movements
I await specific orders."

# Clear explicit orders give +15% bonus
# "Use your judgment" → conservative/suboptimal interpretation
```

#### 3.4 Personality Failure Modes (Telegraphed)
Dramatic moments that emerge from personality, NOT random punishment.

| Marshal | Trigger | Warning | Failure Mode |
|---------|---------|---------|--------------|
| Ney | recklessness >= 3 | "Ney's blood is up!" | Glorious Charge: 2x damage dealt AND taken |
| Davout | wins defense | None (positive) | May refuse pursuit ("Hold the line!") |
| Grouchy | battle within 2 regions | Hearing the Guns | Ignores unless explicitly redirected |

**Recklessness builds predictably:**
```python
if ney.stance == AGGRESSIVE and ney.consecutive_attacks >= 2:
    ney.recklessness += 1

if ney.recklessness >= 3:
    # Player sees warning, can ALLOW or RESTRAIN (-5 trust)
```

#### 3.5 Anti-Tedium Improvements
Quality of life fixes for every-turn friction.

| Issue | Fix |
|-------|-----|
| Fortify grinding | Front-load: +5% turn 1, +2% after (max 13-18% by personality) |
| Retreat recovery | Allow limited actions: hold, recruit, defensive stance |
| Objection spam | Reduce severity on repeat situations (more auto-resolve) |
| Stance management | Add "All marshals, [stance]!" army-wide command |

#### 3.6 Dominant Strategy Pressure (Simplified)
Break turtling and alpha-strike without complex event systems.

**Fortify Pressure (escalating, predictable):**
```
Turn 3: "The men grow restless behind these walls." (warning)
Turn 5: "Supplies run low." → forage (opinion -20) OR ration (strength -10)
Turn 7: "Paris demands action." → authority -10, political_pressure flag
Turn 9 (if flag): "Paris recalls you." → game over
```

**Attack Exhaustion:**
```python
if marshal.consecutive_attacks >= 2:
    marshal.exhaustion += 1
if marshal.exhaustion >= 2:
    "Troops exhausted. Attack at -20%, or rest 1 turn?"
```

#### 3.7 Redemption System Improvements
- Autonomy uses Enemy AI (marshal actually acts)
- Narrative outcomes: Success +30 trust, Neutral +15, Failure +5
- Spectacular success (capture region or 2+ wins): trust → 70, +10 authority
- Remove "Demand Obedience" option (trap choice)
- Add "Administrative Role": marshal removed, +1 action/turn for France

#### Phase 3 File Changes
| File | Changes |
|------|---------|
| `world_state.py` | Event broadcast system, hearing_the_guns trigger |
| `disobedience.py` | Vindication tracking, reconciliation events, memory callbacks |
| `executor.py` | Army-wide stance command, administrative role transfer |
| `enemy_ai.py` | Autonomy processing improvements |
| `marshal.py` | recklessness counter, exhaustion counter |
| `turn_manager.py` | Fortify pressure escalation, exhaustion decay |

### Phase 4: Strategic Commands & Polish → REPLACED BY Phase 5.2
**NOTE:** Strategic commands moved to Phase 5.2 with full implementation plan.
See `docs/PHASE_5_2_IMPLEMENTATION_PLAN.md` for detailed specs.

- [x] Design locked: MOVE_TO, PURSUE, HOLD, SUPPORT commands
- [ ] Implementation pending (follows Phase 5.2 plan)
- Battle momentum (pursue vs consolidate choice)
- Coalition pressure visibility ("Prussia negotiating with Austria")

### Phase 5: Diplomacy & Fog of War
- Natural language negotiation with AI nations
- Treaty system
- Reputation tracking
- Coalition triggers
- Fog of war (last-known positions)

### Phase 6: Early Access Polish
- Year-based timeline (1805-1815)
- Character death/replacement
- Vassal system
- Token monetization (BYOK or purchase)
- Full Europe map (200+ regions)

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