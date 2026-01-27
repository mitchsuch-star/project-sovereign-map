# Phase 5.2 Implementation Plan: Strategic Commands

**Version:** 2.1
**Status:** IN PROGRESS - Phase A ✅ Phase B ✅ Phase C next
**Target:** Early Access (EA) - November 2025
**Created:** January 2025
**Last Revised:** January 2026 (Chain Audit Applied)

---

## CHAIN AUDIT REFERENCE

**See:** `docs/PHASE_5_2_CHAIN_AUDIT.md` for complete verification of:
- LLM Integration Chain (11 links verified)
- Strategic Execution → UI Chain (16 links verified)
- Interrupt/Clarification Chain (11 links - all to be created)
- Key Name Consistency Table
- Failure Mode Analysis

**Audit Status:** ✅ READY FOR IMPLEMENTATION
- All broken links documented with fixes
- All failure modes identified with handling code
- Total estimated new code: ~1700 lines

---

## HOW TO USE THIS DOCUMENT

**If you are a Claude session starting fresh:**
1. Read `PHASE_5_2_CHAIN_AUDIT.md` FIRST for integration overview
2. Read this ENTIRE document before writing any code
3. Follow the Implementation Order (Section 12) exactly
4. Check off items as you complete them
5. Reference the code snippets - they are production-ready
6. When in doubt, ask the user for clarification

**Key files to read BEFORE starting:**
- `backend/models/marshal.py` - Marshal state fields
- `backend/commands/executor.py` - How actions execute, action cost logic
- `backend/ai/enemy_ai.py` - Autonomous marshal logic
- `backend/models/personality.py` - Personality triggers
- `backend/models/trust.py` - Trust API (use `marshal.trust.modify(delta)`)

---

## 1. OVERVIEW

### What Phase 5.2 Accomplishes

Phase 5.2 adds **Strategic Commands** - multi-turn orders that marshals execute autonomously over several turns. This is distinct from tactical commands which execute immediately.

| Command Type | Action Cost | Duration | Examples |
|--------------|-------------|----------|----------|
| Tactical | 1 action | Immediate | "Attack Wellington", "Defend", "Move to Belgium" |
| Strategic | 2 actions (1 for LITERAL) | Multi-turn | "March to Vienna", "Pursue Blücher", "Hold Belgium" |

### The 4 Strategic Commands

| Command | Purpose | Completion Condition |
|---------|---------|---------------------|
| **MOVE_TO** | March to a region | Arrival at destination |
| **PURSUE** | Follow and attack target | Target destroyed OR player cancels |
| **HOLD** | Defend a position | Player cancels OR condition met |
| **SUPPORT** | Assist an ally | Ally safe OR battle won |

### Core Innovation

**Personality affects HOW orders are executed:**
- AGGRESSIVE: Auto-attacks, rushes to glory, never asks
- CAUTIOUS: Asks before risky actions, auto-fortifies
- LITERAL: Executes precisely, never adapts, gets bonuses for completion

---

## 2. DATA STRUCTURES

### 2.1 StrategicOrder (Add to marshal.py)

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class StrategicOrder:
    """
    Represents a multi-turn strategic command.

    Stored in marshal.strategic_order field.
    """
    command_type: str              # "MOVE_TO", "PURSUE", "HOLD", "SUPPORT"
    target: str                    # Region name, marshal name, or "generic"
    target_type: str               # "region", "marshal", "battle", "generic"
    started_turn: int              # Turn when order was issued
    original_command: str          # Raw command text for reference

    # Path for movement orders (MOVE_TO, PURSUE approaching, SUPPORT approaching)
    path: List[str] = field(default_factory=list)

    # SUPPORT-specific
    follow_if_moves: bool = True   # Follow supported ally if they move
    join_combat: bool = True       # Auto-join ally's battles

    # MOVE_TO-specific
    attack_on_arrival: bool = False  # Attack enemies at destination

    # Conditions (optional)
    condition: Optional['StrategicCondition'] = None

    # ═══════════════════════════════════════════════════════════════════
    # COMBAT LOOP PREVENTION (Issue #2 fix)
    # Tracks last combat to prevent infinite engagement loops
    # ═══════════════════════════════════════════════════════════════════
    last_combat_enemy: Optional[str] = None   # Name of last enemy fought
    last_combat_turn: Optional[int] = None    # Turn when combat occurred
    last_combat_result: Optional[str] = None  # "victory", "defeat", "stalemate"

    def to_dict(self) -> Dict:
        """Serialize for save/load."""
        return {
            "command_type": self.command_type,
            "target": self.target,
            "target_type": self.target_type,
            "started_turn": self.started_turn,
            "original_command": self.original_command,
            "path": self.path,
            "follow_if_moves": self.follow_if_moves,
            "join_combat": self.join_combat,
            "attack_on_arrival": self.attack_on_arrival,
            "condition": self.condition.to_dict() if self.condition else None,
            # Combat loop prevention
            "last_combat_enemy": self.last_combat_enemy,
            "last_combat_turn": self.last_combat_turn,
            "last_combat_result": self.last_combat_result,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'StrategicOrder':
        """Deserialize from save/load."""
        condition = None
        if data.get("condition"):
            condition = StrategicCondition.from_dict(data["condition"])
        return cls(
            command_type=data["command_type"],
            target=data["target"],
            target_type=data["target_type"],
            started_turn=data["started_turn"],
            original_command=data["original_command"],
            path=data.get("path", []),
            follow_if_moves=data.get("follow_if_moves", True),
            join_combat=data.get("join_combat", True),
            attack_on_arrival=data.get("attack_on_arrival", False),
            condition=condition,
            # Combat loop prevention
            last_combat_enemy=data.get("last_combat_enemy"),
            last_combat_turn=data.get("last_combat_turn"),
            last_combat_result=data.get("last_combat_result"),
        )
```

### 2.2 StrategicCondition (Add to marshal.py)

```python
@dataclass
class StrategicCondition:
    """
    Conditions that end strategic orders.

    Example: "Hold until Ney arrives" -> until_marshal_arrives = "Ney"
    """
    # Time-based
    max_turns: Optional[int] = None

    # Marshal-based
    until_marshal_arrives: Optional[str] = None
    until_marshal_destroyed: Optional[str] = None

    # Battle-based
    until_battle_won: bool = False
    until_relieved: bool = False

    def to_dict(self) -> Dict:
        return {
            "max_turns": self.max_turns,
            "until_marshal_arrives": self.until_marshal_arrives,
            "until_marshal_destroyed": self.until_marshal_destroyed,
            "until_battle_won": self.until_battle_won,
            "until_relieved": self.until_relieved
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'StrategicCondition':
        return cls(
            max_turns=data.get("max_turns"),
            until_marshal_arrives=data.get("until_marshal_arrives"),
            until_marshal_destroyed=data.get("until_marshal_destroyed"),
            until_battle_won=data.get("until_battle_won", False),
            until_relieved=data.get("until_relieved", False)
        )
```

### 2.3 Marshal Fields to Add (marshal.py __init__)

```python
# Strategic Order System (Phase 5.2)
self.strategic_order: Optional[StrategicOrder] = None

# LITERAL Precision Bonuses
self.explicit_order_active: bool = False
self.precision_bonus_available: bool = False
self.last_order_was_explicit: bool = False

# ═══════════════════════════════════════════════════════════════════
# BATTLE TRACKING (Issue #4, #5, #11 fix)
# Used for cannon fire detection and until_battle_won condition
# ═══════════════════════════════════════════════════════════════════
self.in_combat_this_turn: bool = False      # Set True when combat occurs
self.last_combat_turn: Optional[int] = None # Turn of last combat
self.last_combat_result: Optional[str] = None  # "victory", "defeat", "stalemate"
self.last_combat_location: Optional[str] = None  # Region where combat occurred

@property
def in_strategic_mode(self) -> bool:
    """Check if marshal has active strategic order."""
    return self.strategic_order is not None

@property
def strategic_command_type(self) -> Optional[str]:
    """Get current strategic command type if any."""
    if self.strategic_order:
        return self.strategic_order.command_type
    return None
```

### 2.4 WorldState Battle Tracking (Add to world_state.py)

```python
# In WorldState.__init__():
# ═══════════════════════════════════════════════════════════════════
# BATTLE TRACKING (Phase 5.2 - for cannon fire detection)
# ═══════════════════════════════════════════════════════════════════
self.battles_this_turn: List[Dict] = []  # Cleared at turn start

def record_battle(self, location: str, attacker: str, defender: str,
                  result: str) -> None:
    """
    Record a battle for cannon fire detection.

    Called by combat.py after resolve_combat().
    """
    self.battles_this_turn.append({
        "location": location,
        "attacker": attacker,
        "defender": defender,
        "result": result,
        "turn": self.current_turn
    })

def get_battles_within_range(self, location: str, max_distance: int) -> List[Dict]:
    """Get battles within max_distance regions of location."""
    nearby = []
    for battle in self.battles_this_turn:
        distance = self.get_distance(location, battle["location"])
        if distance <= max_distance:
            nearby.append(battle)
    return nearby

def clear_turn_battles(self) -> None:
    """Clear battle tracking at start of turn. Call in advance_turn()."""
    self.battles_this_turn = []
    # Also clear in_combat_this_turn flag on all marshals
    for marshal in self.marshals.values():
        marshal.in_combat_this_turn = False
```

---

## 3. GROUCHY (Literal) - Complete Specification

### 3.1 Design Philosophy

Grouchy doesn't argue about TACTICS (like Ney) or RISK (like Davout).
He argues about CLARITY. "Which enemy, Sire?" not "That's suicide!"

The core loop:
- **Vague orders** → Grouchy objects (uses existing objection popup)
- **Clear orders** → Grouchy executes with combat bonuses
- **Crystal clear + strategic orders** → Precision Execution (+1 all stats, 3 turns)

This means the LLM ambiguity score (already computed in ParseResult) drives
Grouchy's entire personality without any new parsing infrastructure.

### 3.2 Objection System - Unique Trigger

| Marshal | Objection Trigger | Objection Flavor |
|---------|-------------------|------------------|
| Ney | Risky tactics | "That's suicide!" |
| Davout | Reckless risk | "I counsel caution" |
| Grouchy | High ambiguity (>0.5) | "Which enemy, Sire?" |

Grouchy uses the EXISTING objection popup system. When LLM returns high
ambiguity (>0.5) for an order to Grouchy:

1. Grouchy objects with confusion flavor
2. LLM generates valid options based on context
3. Player picks an option OR insists (trust penalty, Grouchy picks literally/nearest)

### 3.3 Trust Mechanics

Grouchy participates in the normal trust system:

| Event | Trust Change |
|-------|-------------|
| Grouchy objects (vague order), player picks option | 0 |
| Grouchy objects, player insists | Same penalty as other marshals |
| Strategic order completed | +5 |
| Player cancels mid-execution | -3 (all marshals, not Grouchy-specific) |

**NOTE:** Order cancellation trust penalty (-3) does not exist yet in codebase.
It should be added in Phase 5.2 as a universal mechanic for all marshals when
strategic orders are implemented. This is NOT a Grouchy-specific feature.

Trust floor → autonomy decision → Grouchy becomes cautious AI (loses all
literal buffs). This is implemented in `_get_effective_personality()` in
`enemy_ai.py` (foundation work complete).

### 3.4 Ambiguity-Scaled Combat Buff

| Ambiguity (0-100) | Clarity | Combat Buff (atk+def) | Precision Execution? |
|-----------|---------|-------------|---------------------|
| 0 - 20 | Crystal clear | +15% | YES (if strategic_score > 60) |
| 21 - 40 | Clear | +10% | No |
| 41 - 60 | Vague (warning, not RNG) | +5% | No |
| 61+ | Very vague (triggers objection) | 0% | No |

**Implementation:** `_apply_grouchy_ambiguity_buff()` in executor.py. Applied on order receipt
(before execution). Sets `strategic_combat_bonus` AND `strategic_defense_bonus` on marshal.
Both are consumed after use in `get_attack_modifier()` / `get_defense_modifier()`.

### 3.5 Precision Execution (Special Ability)

When an order has BOTH:
- Very LOW ambiguity (≤20, crystal clear)
- AND high strategic value (strategic_score > 60)

Grouchy gets temporary skill boost:
- +1 to all general stats (attack, defense, tactics, etc.)
- Additive bonus
- Lasts 3 turns
- Each stat caps at 8
- Can stack with subsequent clear+strategic orders

This rewards players who give excellent orders. Grouchy's ceiling is highest
with skilled, precise commanders.

### 3.6 GROUCHY_MODIFIERS (personality_modifiers.py)

```python
# ════════════════════════════════════════════════════════════════════════════════
# GROUCHY (Literal) - Precision Execution
# ════════════════════════════════════════════════════════════════════════════════
GROUCHY_MODIFIERS = {
    # ═══════════════════════════════════════════════════════════
    # IMMOVABLE (existing - applies during combat while holding)
    # ═══════════════════════════════════════════════════════════
    "hold_position_defense_bonus": 0.15,  # +15% defense in hold combat

    # ═══════════════════════════════════════════════════════════
    # AMBIGUITY-SCALED COMBAT BUFF (new)
    # Applied based on LLM ambiguity score of the order
    # ═══════════════════════════════════════════════════════════
    "crystal_clear_bonus": 0.15,          # +15% at ambiguity < 0.2
    "clear_bonus": 0.10,                  # +10% at ambiguity 0.2-0.4
    "vague_bonus": 0.05,                  # +5% at ambiguity 0.4-0.6
    # No bonus at ambiguity >= 0.6

    # ═══════════════════════════════════════════════════════════
    # PRECISION EXECUTION (new - stat boost on clear+strategic)
    # ═══════════════════════════════════════════════════════════
    "precision_stat_boost": 1,            # +1 to all stats
    "precision_duration": 3,              # Lasts 3 turns
    "precision_stat_cap": 8,              # Max stat value
    "precision_ambiguity_threshold": 0.2, # Must be below this
    # Also requires high strategic_score from LLM

    # ═══════════════════════════════════════════════════════════
    # STRATEGIC EFFICIENCY (new - applies to order costs)
    # ═══════════════════════════════════════════════════════════
    "strategic_action_cost": 1,           # 1 action instead of 2
    "strategic_morale_immunity": True,    # No morale loss during strategic execution

    # ═══════════════════════════════════════════════════════════
    # TRUST (new - applied in disobedience.py)
    # ═══════════════════════════════════════════════════════════
    "strategic_completion_trust_bonus": 5, # +5 trust when strategic completes
}
```

### 3.7 Interrupt Behavior (Strategic Execution)

| Interrupt | Aggressive | Cautious | Literal |
|-----------|------------|----------|---------|
| Cannon fire | Auto-engage | "Investigate?" | **Ignores** |
| Ally attacked | Rush to help | "Support?" | **Ignores** |
| Path blocked | Attack blocker | "Engage?" | Reroutes silently |

Grouchy NEVER interrupts for cannon fire — this is "The Grouchy Moment",
the signature historical reference. Players who want Grouchy to respond to
nearby battles must give a new explicit order (costs 1 action).

### 3.8 Redirecting Grouchy Mid-Execution

No special "emergency override" mechanic. Player gives new clear order
(1 action). Old order cancelled. Trust penalty (-3) applies — same as
all other marshals (universal mechanic, not Grouchy-specific).

### 3.9 AI Personality Conversion (IMPLEMENTED)

When AI controls a literal marshal:
- **Enemy nation controlling literal marshal** → becomes cautious
- **Player's literal marshal goes autonomous** → becomes cautious

Implementation: `EnemyAI._get_effective_personality()` in `enemy_ai.py`.
All 8 decision-making personality reads in the class use this helper.
Module-level utility functions (scoring, priority, flavor text) use raw
personality since they don't affect tactical decisions.

**Stacking Rules:**
- Ambiguity combat buff + Precision Execution can stack (watch during playtesting)
- Immovable (+15%) is SEPARATE combat modifier, applies during combat while holding
- Final = ambiguity_buff × combat_modifier

---

## 4. PERSONALITY BEHAVIOR TABLES

### 4.1 MOVE_TO Behavior

| Aspect | AGGRESSIVE | CAUTIOUS | LITERAL |
|--------|------------|----------|---------|
| **Path selection** | Shortest (through enemies) | Safest (avoids enemies) | Shortest (around enemies) |
| **Enemy contact** | Auto-attack if favorable | Always ask player | Reroute silently |
| **Enemy adjacent** | Ignore, continue | Auto-fortify, pause | Ignore, continue |
| **Cannon fire** | Interrupt, rush to battle | Interrupt, ask player | **NEVER interrupt** |
| **Combat result** | Victory→continue, Defeat→break | Always ask after combat | Continue if path clear |
| **Action cost** | 2 actions | 2 actions | **1 action** |
| **Movement per turn** | movement_range (1 or 2) | movement_range | movement_range |

### 4.2 PURSUE Behavior

| Aspect | AGGRESSIVE | CAUTIOUS | LITERAL |
|--------|------------|----------|---------|
| **Target selection (generic)** | Nearest OR strongest | Weakest OR isolated | **MUST clarify** |
| **Combat engagement** | Always attack | Attack only if favorable | Attack when reaching target |
| **Target retreats** | Chase relentlessly | Ask: "Continue pursuit?" | Follow precisely |
| **Target destroyed** | Order completes | Order completes | Order completes |
| **Low morale** | Keep pursuing | Suggest withdrawal | Keep pursuing |

### 4.3 HOLD Behavior

| Aspect | AGGRESSIVE | CAUTIOUS | LITERAL |
|--------|------------|----------|---------|
| **Defense style** | Active (sallies out, returns) | Passive (auto-fortify) | Exact position (+15%) |
| **Enemy approaches** | Attack if favorable | Fortify, prepare | Hold position exactly |
| **Enemy attacks** | Counter-attack | Defend, then ask | Defend position |
| **Ally requests help** | Might leave to help | Ask player | **Never leave** |
| **Condition: until_relieved** | Leave when any ally arrives | Leave when ally arrives | Leave when ally arrives |
| **Sally behavior** | Attack then RETURN to hold | N/A | N/A |

### 4.4 SUPPORT Behavior

| Aspect | AGGRESSIVE | CAUTIOUS | LITERAL |
|--------|------------|----------|---------|
| **Target selection (generic)** | Ally in active combat | Most threatened ally | **MUST clarify** |
| **Ally in combat** | Rush to join, attack | Move to assist, defend | Join, mirror ally |
| **Ally moving** | Follow automatically | Ask: "Follow or hold?" | Follow precisely |
| **Ally destroyed** | Order breaks | Order breaks | Order breaks |
| **Supported ally wins** | Order completes | Order completes | Order completes |

---

## 5. INTERRUPT RULES

### 5.1 Interrupt Types

| Type | Definition | When Checked |
|------|------------|--------------|
| **CONTACT** | Enemy in NEXT region on path (blocking) | Before each move |
| **ADJACENT** | Enemy in neighboring region, NOT on path | After each move |
| **CANNON_FIRE** | Battle within 2 regions (uses `world.battles_this_turn`) | Start of strategic execution |
| **ALLY_COMBAT** | Supported ally enters combat | During SUPPORT |
| **CONDITION_MET** | Strategic condition satisfied | End of strategic execution |

### 5.2 Interrupt Response by Personality

| Interrupt | AGGRESSIVE | CAUTIOUS | LITERAL |
|-----------|------------|----------|---------|
| **CONTACT (favorable odds)** | Auto-attack | Ask player | Reroute around |
| **CONTACT (bad odds)** | Ask player | Ask player | Reroute around |
| **CONTACT (terrible odds)** | Auto-retreat, break | Auto-retreat, break | Report stuck, break |
| **ADJACENT** | Ignore | Auto-fortify, pause | Ignore |
| **CANNON_FIRE** | Interrupt, redirect | Interrupt, ask | **Never interrupt** |
| **ALLY_COMBAT** | Rush to join | Ask: "Assist?" | Join if SUPPORT order |

### 5.3 Combat Result → Order Status

| Combat Result | Order Status | Next Action |
|---------------|--------------|-------------|
| Victory | **Continues** | Path cleared, proceed |
| Defeat | **Breaks** | Marshal needs recovery |
| Stalemate | **Ask player** | "Continue or await orders?" |
| Tactical victory (either side) | **Ask player** | Situation unclear |

### 5.4 Combat Loop Prevention (Issue #2)

**Problem:** If marshal attacks, gets stalemate, player says "continue", next turn marshal auto-attacks SAME enemy again. Infinite loop.

**Solution:** Track last combat in StrategicOrder:
```python
# After combat, record it:
order.last_combat_enemy = enemy.name
order.last_combat_turn = world.current_turn
order.last_combat_result = outcome

# Before auto-attacking same enemy:
def _should_auto_attack(self, marshal, enemy, world) -> bool:
    """Check if should auto-attack or ask player instead."""
    order = marshal.strategic_order

    # If we fought this same enemy within 1 turn, ask player instead
    if (order.last_combat_enemy == enemy.name and
        order.last_combat_turn is not None and
        world.current_turn - order.last_combat_turn <= 1):
        return False  # Ask player instead of auto-attacking

    return True  # OK to auto-attack
```

---

## 6. COMMAND HANDLING CATEGORIES

### 6.1 Override vs Non-Override Commands (Issue #6)

When a marshal has an active strategic order, incoming commands are categorized:

```python
# Commands that CANCEL strategic order and execute immediately
STRATEGIC_OVERRIDE_COMMANDS = [
    "attack",    # Direct combat order overrides everything
    "move",      # Direct movement order overrides
    "defend",    # Direct defense order overrides
    "fortify",   # Fortify in place overrides
    "drill",     # Drill in place overrides
    "retreat",   # Emergency retreat overrides
]

# Commands that do NOT cancel strategic order
NON_OVERRIDE_COMMANDS = [
    "wait",          # Just skips this turn, order continues
    "scout",         # Information gathering, order continues
    "stance_change", # Stance adjustment, order continues
    "recruit",       # Reinforcing, order continues
]

# Explicit cancel commands (cost 1 action to cancel)
EXPLICIT_CANCEL_KEYWORDS = [
    "cancel", "halt", "stand down", "stop", "abort",
    "belay that", "as you were", "new orders"
]
```

### 6.2 Command Handling Logic (Add to executor.py)

```python
def _check_strategic_override(self, command: Dict, marshal, world) -> Dict:
    """
    Check if command should override/cancel active strategic order.

    Returns:
        {
            "should_override": bool,
            "cancel_cost": int,  # 0 for override commands, 1 for explicit cancel
            "message": str
        }
    """
    if not marshal.in_strategic_mode:
        return {"should_override": False, "cancel_cost": 0, "message": ""}

    action = command.get("action", "").lower()
    raw_command = command.get("raw_command", "").lower()

    # Check for explicit cancel keywords
    for keyword in EXPLICIT_CANCEL_KEYWORDS:
        if keyword in raw_command:
            return {
                "should_override": True,
                "cancel_cost": 1,
                "message": f"{marshal.name}'s strategic order cancelled."
            }

    # Check for override commands
    if action in STRATEGIC_OVERRIDE_COMMANDS:
        return {
            "should_override": True,
            "cancel_cost": 0,
            "message": f"{marshal.name}'s strategic order superseded by direct order."
        }

    # Non-override command - strategic continues
    if action in NON_OVERRIDE_COMMANDS:
        return {
            "should_override": False,
            "cancel_cost": 0,
            "message": f"{marshal.name} executes {action} while continuing strategic order."
        }

    # Unknown command - default to override for safety
    return {
        "should_override": True,
        "cancel_cost": 0,
        "message": f"Unknown command type - strategic order cancelled."
    }
```

### 6.3 Integration Point in executor.execute()

```python
# In execute() method, AFTER disobedience check, BEFORE action execution:

# Check if this command overrides an active strategic order
if marshal and marshal.in_strategic_mode:
    override_check = self._check_strategic_override(command, marshal, world)

    if override_check["should_override"]:
        # Cancel strategic order
        old_order = marshal.strategic_order
        marshal.strategic_order = None

        # Apply cancel cost if explicit cancel
        if override_check["cancel_cost"] > 0:
            if world.actions_remaining < override_check["cancel_cost"]:
                return {
                    "success": False,
                    "message": f"Cancelling strategic order costs {override_check['cancel_cost']} action."
                }
            world.use_action("cancel_strategic")

        # Log the cancellation
        print(f"  [STRATEGIC] {override_check['message']}")
```

---

## 7. STRATEGIC ACTION COST IMPLEMENTATION (Issue #3)

### 7.1 Where Action Cost is Applied

**File:** `backend/commands/executor.py`

**Location:** In the `_execute_strategic_command()` method (new method to create)

```python
def _execute_strategic_command(self, command: Dict, game_state: Dict) -> Dict:
    """
    Execute a strategic command (MOVE_TO, PURSUE, HOLD, SUPPORT).

    This is called when parser detects a strategic command.
    """
    world = game_state.get("world")
    marshal_name = command.get("marshal")
    marshal = world.get_marshal(marshal_name)

    if not marshal:
        return {"success": False, "message": "Marshal not found"}

    # ═══════════════════════════════════════════════════════════════════
    # STRATEGIC ACTION COST CALCULATION (Issue #3 fix)
    # LITERAL personality pays 1 action, others pay 2
    # ═══════════════════════════════════════════════════════════════════
    from backend.models.personality_modifiers import GROUCHY_MODIFIERS

    if marshal.personality == "literal":
        action_cost = GROUCHY_MODIFIERS.get("strategic_action_cost", 1)
    else:
        action_cost = 2  # Default strategic cost

    # Check if player has enough actions
    if world.actions_remaining < action_cost:
        return {
            "success": False,
            "message": f"Strategic command requires {action_cost} action(s), "
                      f"but only {world.actions_remaining} remaining."
                      f"{' (LITERAL marshals only cost 1)' if marshal.personality != 'literal' else ''}"
        }

    # Parse the strategic command details
    strategic_type = command.get("strategic_type")  # MOVE_TO, PURSUE, HOLD, SUPPORT
    target = command.get("target")
    target_type = command.get("target_type")
    condition = command.get("condition")
    attack_on_arrival = command.get("attack_on_arrival", False)

    # Create the strategic order
    order = StrategicOrder(
        command_type=strategic_type,
        target=target,
        target_type=target_type,
        started_turn=world.current_turn,
        original_command=command.get("raw_command", ""),
        attack_on_arrival=attack_on_arrival,
        condition=condition
    )

    # Calculate initial path for movement commands
    if strategic_type in ["MOVE_TO", "SUPPORT"]:
        if target_type == "region":
            order.path = world.find_path(marshal.location, target)
        elif target_type == "marshal":
            target_marshal = world.get_marshal(target)
            if target_marshal:
                order.path = world.find_path(marshal.location, target_marshal.location)

    # Assign order to marshal
    marshal.strategic_order = order

    # Consume actions
    for _ in range(action_cost):
        world.use_action("strategic_command")

    # Apply LITERAL trust bonus for explicit orders
    if marshal.personality == "literal" and target_type != "generic":
        marshal.explicit_order_active = True
        marshal.trust.modify(GROUCHY_MODIFIERS.get("explicit_order_trust_bonus", 2))

    return {
        "success": True,
        "message": f"{marshal.name} acknowledges strategic order: {strategic_type} {target}",
        "strategic_order": order.to_dict(),
        "action_cost": action_cost,
        "events": [{
            "type": "strategic_order_issued",
            "marshal": marshal.name,
            "command": strategic_type,
            "target": target,
            "action_cost": action_cost
        }]
    }
```

---

## 8. PARSER KEYWORDS

### 8.1 Strategic Command Detection

```python
# Add to llm_client.py

STRATEGIC_KEYWORDS = {
    "MOVE_TO": [
        "march to", "move to", "advance to", "head to", "go to",
        "proceed to", "travel to", "make for", "head toward",
        "march toward", "advance toward", "withdraw to", "fall back to",
        "secure", "take"  # "secure Vienna", "take the crossing"
    ],
    "PURSUE": [
        "pursue", "chase", "hunt", "follow", "track",
        "go after", "hunt down", "give chase", "intercept"
    ],
    "HOLD": [
        "hold", "defend", "guard", "protect", "secure",
        "maintain position", "hold position", "hold the line",
        "dig in", "fortify and hold"
    ],
    "SUPPORT": [
        "support", "reinforce", "assist", "aid", "help",
        "join", "link up with", "move to support", "back up"
    ]
}

CONDITION_PATTERNS = {
    "until_marshal_arrives": [
        r"until\s+(\w+)\s+arrives",
        r"until\s+relieved\s+by\s+(\w+)",
        r"wait\s+for\s+(\w+)"
    ],
    "until_destroyed": [
        r"until\s+destroyed",
        r"until\s+eliminated",
        r"to\s+destruction"
    ],
    "until_relieved": [
        r"until\s+relieved",
        r"until\s+reinforced"
    ],
    "max_turns": [
        r"for\s+(\d+)\s+turns?"
    ],
    "until_battle_won": [
        r"until\s+(?:the\s+)?battle\s+(?:is\s+)?won",
        r"until\s+victory"
    ]
}

GENERIC_INDICATORS = [
    "the enemy", "the enemies", "them", "hostile forces",
    "the prussians", "the british", "the austrians",
    "the battle", "the defense", "the front",
    "forward", "ahead", "onward"
]
```

### 8.2 Distance-Based Tactical→Strategic Conversion (Issue #8)

```python
def check_tactical_to_strategic(command_text: str, marshal, world) -> Optional[Dict]:
    """
    Check if a tactical command should be converted to strategic.

    Conversion triggers:
    - "Attack [region]" where region is 2+ regions away → MOVE_TO with attack_on_arrival
    - "Move to [region]" where region is 3+ regions away → MOVE_TO
    """
    text_lower = command_text.lower()

    # Check for attack + distant region
    if "attack" in text_lower:
        target = extract_target(command_text, "attack", world)

        # Is target a region (not a marshal)?
        if target and world.get_region(target):
            distance = world.get_distance(marshal.location, target)

            if distance >= 2:
                # Convert to MOVE_TO with attack_on_arrival
                return {
                    "convert_to": "strategic",
                    "command": "MOVE_TO",
                    "target": target,
                    "target_type": "region",
                    "attack_on_arrival": True,  # Issue #8 fix
                    "message": f"Target {target} is {distance} regions away. "
                              f"Converting to strategic march with attack on arrival."
                }

    # Check for move to distant region
    if "move to" in text_lower or "march to" in text_lower:
        target = extract_target(command_text, "move", world)

        if target and world.get_region(target):
            distance = world.get_distance(marshal.location, target)

            if distance >= 3:
                return {
                    "convert_to": "strategic",
                    "command": "MOVE_TO",
                    "target": target,
                    "target_type": "region",
                    "attack_on_arrival": False,
                    "message": f"Target {target} is {distance} regions away. "
                              f"Converting to strategic march."
                }

    return None  # No conversion needed
```

---

## 9. CLARIFICATION SYSTEM (Issue #9)

### 9.1 Clarification Option Generation

```python
def generate_clarification_options(command_type: str, marshal, world) -> Dict:
    """
    Generate clarification options for LITERAL marshal with generic command.

    Args:
        command_type: PURSUE, SUPPORT, etc.
        marshal: The marshal receiving the order
        world: WorldState for context

    Returns:
        {
            "options": [{"name": "Blücher", "details": "68,000 at Rhine"}, ...],
            "prompt": "Which shall I pursue?",
            "command_type": "PURSUE"
        }
    """
    options = []

    if command_type == "PURSUE":
        # Get all enemy marshals
        for enemy in world.marshals.values():
            if enemy.nation != marshal.nation and enemy.strength > 0:
                distance = world.get_distance(marshal.location, enemy.location)
                options.append({
                    "name": enemy.name,
                    "details": f"{enemy.strength:,} troops at {enemy.location} ({distance} regions)",
                    "value": enemy.name
                })

        # Sort by distance
        options.sort(key=lambda x: world.get_distance(marshal.location,
                     world.get_marshal(x["name"]).location))

        return {
            "options": options,
            "prompt": "Which enemy shall I pursue?",
            "command_type": command_type,
            "header": "CLARIFICATION REQUIRED"
        }

    elif command_type == "SUPPORT":
        # Get all friendly marshals (except self)
        for ally in world.marshals.values():
            if ally.nation == marshal.nation and ally.name != marshal.name and ally.strength > 0:
                # Check if ally is threatened
                threatened = _is_ally_threatened(ally, world)
                status = "THREATENED" if threatened else "secure"

                distance = world.get_distance(marshal.location, ally.location)
                options.append({
                    "name": ally.name,
                    "details": f"{ally.strength:,} troops at {ally.location} ({distance} regions) - {status}",
                    "value": ally.name,
                    "priority": 0 if threatened else 1
                })

        # Sort by threat status, then distance
        options.sort(key=lambda x: (x.get("priority", 1),
                     world.get_distance(marshal.location,
                     world.get_marshal(x["name"]).location)))

        return {
            "options": options,
            "prompt": "Which ally shall I support?",
            "command_type": command_type,
            "header": "CLARIFICATION REQUIRED"
        }

    elif command_type == "HOLD":
        # For HOLD, clarify which region to hold
        options = []

        # Current location is always an option
        options.append({
            "name": marshal.location,
            "details": "Current position",
            "value": marshal.location
        })

        # Adjacent regions
        region = world.get_region(marshal.location)
        for adj_name in region.adjacent_regions:
            adj_region = world.get_region(adj_name)
            controller = adj_region.controller if adj_region else "Unknown"
            options.append({
                "name": adj_name,
                "details": f"Adjacent ({controller} controlled)",
                "value": adj_name
            })

        return {
            "options": options[:5],  # Limit to 5 options
            "prompt": "Which position shall I hold?",
            "command_type": command_type,
            "header": "CLARIFICATION REQUIRED"
        }

    # Default empty
    return {"options": [], "prompt": "Please clarify your order.", "command_type": command_type}


def _is_ally_threatened(ally, world) -> bool:
    """Check if an ally has enemies adjacent."""
    region = world.get_region(ally.location)
    if not region:
        return False

    for adj_name in region.adjacent_regions:
        enemies = world.get_enemies_in_region(adj_name, ally.nation)
        if enemies:
            return True
    return False
```

---

## 10. CONDITION IMPLEMENTATION (Issue #5)

### 10.1 until_battle_won Implementation

```python
def _check_condition(self, marshal, condition, world) -> Tuple[bool, str]:
    """
    Check if strategic condition is met.

    Returns:
        (condition_met: bool, reason: str)
    """
    if condition.max_turns is not None:
        turns_active = world.current_turn - marshal.strategic_order.started_turn
        if turns_active >= condition.max_turns:
            return (True, f"Held for {condition.max_turns} turns as ordered")

    if condition.until_marshal_arrives:
        target_name = condition.until_marshal_arrives
        target = world.get_marshal(target_name)
        if target and target.location == marshal.location:
            return (True, f"{target_name} has arrived")

    if condition.until_marshal_destroyed:
        target_name = condition.until_marshal_destroyed
        target = world.get_marshal(target_name)
        if not target or target.strength <= 0:
            return (True, f"{target_name} has been destroyed")

    if condition.until_relieved:
        allies_here = [m for m in world.get_marshals_in_region(marshal.location)
                     if m.nation == marshal.nation and m.name != marshal.name]
        if allies_here:
            return (True, f"Relieved by {allies_here[0].name}")

    # ═══════════════════════════════════════════════════════════════════
    # until_battle_won IMPLEMENTATION (Issue #5 fix)
    # Check if supported ally's last combat was a victory
    # ═══════════════════════════════════════════════════════════════════
    if condition.until_battle_won:
        order = marshal.strategic_order

        # For SUPPORT orders, check the supported ally's last combat
        if order.command_type == "SUPPORT":
            ally = world.get_marshal(order.target)
            if ally and ally.last_combat_result == "victory":
                return (True, f"{ally.name} won the battle!")

        # For HOLD orders, check if marshal won a defensive battle
        elif order.command_type == "HOLD":
            if marshal.last_combat_result == "victory":
                return (True, "Battle won! Position secured.")

        # For any order, check if there was a battle at current location that we won
        for battle in world.battles_this_turn:
            if battle["location"] == marshal.location:
                if (battle["attacker"] == marshal.name or
                    battle["defender"] == marshal.name):
                    if battle["result"] in ["attacker_victory", "defender_victory"]:
                        # Check if we were the victor
                        if ((battle["result"] == "attacker_victory" and
                             battle["attacker"] == marshal.name) or
                            (battle["result"] == "defender_victory" and
                             battle["defender"] == marshal.name)):
                            return (True, "Victory achieved!")

    return (False, "")
```

---

## 11. FULL STRATEGIC EXECUTOR IMPLEMENTATION

```python
# backend/commands/strategic.py
"""
Strategic Command Execution for Phase 5.2

Handles multi-turn strategic orders: MOVE_TO, PURSUE, HOLD, SUPPORT
Called from turn_manager.py at start of each player turn.

IMPORTANT NOTES:
- Cavalry (movement_range=2) moves 2 regions per turn
- Infantry (movement_range=1) moves 1 region per turn
- Sally attacks do NOT move the marshal (sortie mechanic)
- Combat loop prevention via last_combat_* tracking
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Type hints for clarity
Marshal = 'backend.models.marshal.Marshal'
WorldState = 'backend.models.world_state.WorldState'


class StrategicExecutor:
    """
    Executes strategic orders during turn processing.

    Usage:
        executor = StrategicExecutor(command_executor)
        reports = executor.process_strategic_orders(world, game_state)
    """

    def __init__(self, command_executor):
        """
        Args:
            command_executor: CommandExecutor instance for action execution
        """
        self.executor = command_executor

    # ════════════════════════════════════════════════════════════════════════════
    # MAIN ENTRY POINT
    # ════════════════════════════════════════════════════════════════════════════

    def process_strategic_orders(self, world: WorldState, game_state: Dict) -> List[Dict]:
        """
        Process strategic orders for all player marshals.

        Called at START of player's turn:
        1. After enemy phase completes
        2. After turn advances
        3. Before player can issue new commands

        Returns:
            List of reports for UI display
        """
        reports = []

        # Process in alphabetical order for determinism
        marshals_with_orders = sorted(
            [m for m in world.marshals.values()
             if m.nation == world.player_nation and m.in_strategic_mode],
            key=lambda m: m.name
        )

        for marshal in marshals_with_orders:
            report = self._execute_strategic_turn(marshal, world, game_state)
            reports.append(report)

            # If report requires player input, stop processing
            if report.get("requires_input"):
                break

        return reports

    def _execute_strategic_turn(self, marshal: Marshal, world: WorldState,
                                 game_state: Dict) -> Dict:
        """Execute one turn of a marshal's strategic order."""
        order = marshal.strategic_order

        # 1. Check conditions first
        if order.condition:
            condition_met, reason = self._check_condition(marshal, order.condition, world)
            if condition_met:
                return self._complete_order(marshal, world, reason)

        # 2. Check for interrupts
        interrupt = self._check_interrupts(marshal, world)
        if interrupt:
            response = self._handle_interrupt(marshal, interrupt, world, game_state)
            if response:  # Interrupt was handled or needs input
                return response

        # 3. Execute command-specific logic
        handlers = {
            "MOVE_TO": self._execute_move_to,
            "PURSUE": self._execute_pursue,
            "HOLD": self._execute_hold,
            "SUPPORT": self._execute_support,
        }

        handler = handlers.get(order.command_type)
        if handler:
            return handler(marshal, world, game_state)

        return {"error": f"Unknown command type: {order.command_type}"}

    # ════════════════════════════════════════════════════════════════════════════
    # MOVE_TO EXECUTION
    # ════════════════════════════════════════════════════════════════════════════

    def _execute_move_to(self, marshal: Marshal, world: WorldState,
                          game_state: Dict) -> Dict:
        """
        Execute one turn of MOVE_TO.

        IMPORTANT: Respects marshal.movement_range (cavalry=2, infantry=1)

        Behavior:
        - Move along path toward destination
        - On arrival: complete order (or attack if attack_on_arrival)
        - On blocked: personality-dependent response
        """
        order = marshal.strategic_order

        # Check arrival
        if marshal.location == order.target:
            return self._handle_move_to_arrival(marshal, world, game_state)

        # Ensure we have a path
        if not order.path:
            order.path = self._calculate_path(marshal, order.target, world)

        if not order.path:
            return self._break_order(marshal, f"No valid path to {order.target}")

        # ═══════════════════════════════════════════════════════════════════
        # CAVALRY MOVEMENT FIX (Issue #1)
        # Move multiple regions based on movement_range
        # ═══════════════════════════════════════════════════════════════════
        regions_to_move = getattr(marshal, 'movement_range', 1)
        moves_made = []

        for move_num in range(regions_to_move):
            # Check if we've arrived
            if marshal.location == order.target:
                break

            # Check if path is exhausted
            if not order.path:
                break

            next_region = order.path[0]

            # Check for blocking enemies
            enemies = world.get_enemies_in_region(next_region, marshal.nation)
            if enemies:
                # If this is the first move and blocked, handle it
                if move_num == 0:
                    return self._handle_blocked_path(marshal, enemies, next_region, world, game_state)
                else:
                    # Already moved some - stop here and report partial progress
                    break

            # Execute move
            result = self.executor.execute({
                "marshal": marshal.name,
                "action": "move",
                "target": next_region,
                "_strategic_execution": True  # Flag to skip action cost
            }, game_state)

            if result.get("success"):
                order.path.pop(0)
                moves_made.append(next_region)
            else:
                # Move failed - stop
                break

        # Report movement
        if moves_made:
            turns_remaining = len(order.path)
            movement_desc = " -> ".join([marshal.location] + moves_made) if len(moves_made) > 1 else f"to {moves_made[0]}"

            return {
                "marshal": marshal.name,
                "command": "MOVE_TO",
                "action": "move",
                "regions_moved": moves_made,
                "destination": order.target,
                "turns_remaining": turns_remaining,
                "order_status": "continues",
                "message": f"{marshal.name} marches {movement_desc}. {turns_remaining} region(s) to {order.target}."
            }

        return {"marshal": marshal.name, "error": "Could not move", "order_status": "error"}

    def _handle_move_to_arrival(self, marshal: Marshal, world: WorldState,
                                 game_state: Dict) -> Dict:
        """Handle arrival at MOVE_TO destination."""
        order = marshal.strategic_order

        # Check attack_on_arrival
        if order.attack_on_arrival:
            enemies = world.get_enemies_in_region(marshal.location, marshal.nation)
            if enemies:
                target = enemies[0]
                result = self.executor.execute({
                    "marshal": marshal.name,
                    "action": "attack",
                    "target": target.name,
                    "_strategic_execution": True
                }, game_state)

                # Complete order after attack
                self._complete_order(marshal, world, "Arrived and engaged enemy")
                return {
                    "marshal": marshal.name,
                    "command": "MOVE_TO",
                    "action": "attack_on_arrival",
                    "target": target.name,
                    "combat_result": result,
                    "order_status": "completed",
                    "message": f"{marshal.name} arrives at {order.target} and attacks {target.name}!"
                }

        # Normal arrival
        return self._complete_order(marshal, world, f"Arrived at {order.target}")

    def _handle_blocked_path(self, marshal: Marshal, enemies: List,
                              blocked_region: str, world: WorldState,
                              game_state: Dict) -> Dict:
        """
        Handle enemy blocking the path.

        Behavior varies by personality:
        - AGGRESSIVE: Auto-attack if favorable odds (with combat loop check)
        - CAUTIOUS: Always ask player
        - LITERAL: Reroute silently
        """
        personality = marshal.personality
        order = marshal.strategic_order

        if personality == "literal":
            # Try to find alternate path
            new_path = world.find_path(
                marshal.location,
                order.target,
                avoid_enemies=True,
                marshal_nation=marshal.nation
            )

            if new_path:
                order.path = new_path
                return {
                    "marshal": marshal.name,
                    "command": "MOVE_TO",
                    "action": "reroute",
                    "avoiding": blocked_region,
                    "new_path": new_path,
                    "order_status": "continues",
                    "message": f"{marshal.name} adjusts route to avoid enemy at {blocked_region}."
                }
            else:
                return self._break_order(marshal, f"Path blocked at {blocked_region}. No alternate route.")

        elif personality == "aggressive":
            enemy = enemies[0]
            ratio = marshal.strength / max(1, enemy.strength)

            # ═══════════════════════════════════════════════════════════════════
            # COMBAT LOOP CHECK (Issue #2)
            # Don't auto-attack same enemy we just fought
            # ═══════════════════════════════════════════════════════════════════
            if not self._should_auto_attack(marshal, enemy, world):
                return {
                    "marshal": marshal.name,
                    "command": "MOVE_TO",
                    "requires_input": True,
                    "interrupt_type": "repeated_contact",
                    "enemy": enemy.name,
                    "message": f"{marshal.name} reports: {enemy.name} still blocks the path. "
                              f"We fought them last turn. Attack again or try another approach?",
                    "options": ["attack_again", "go_around", "hold_position", "cancel_order"]
                }

            if ratio >= 0.7:  # Favorable enough for aggressive
                # Auto-attack
                result = self.executor.execute({
                    "marshal": marshal.name,
                    "action": "attack",
                    "target": enemy.name,
                    "_strategic_execution": True
                }, game_state)

                return self._handle_combat_during_strategic(
                    marshal, enemy, result, world, game_state
                )
            else:
                # Bad odds - ask player
                return {
                    "marshal": marshal.name,
                    "command": "MOVE_TO",
                    "requires_input": True,
                    "interrupt_type": "contact_bad_odds",
                    "enemy": enemy.name,
                    "odds": f"{ratio:.1f}:1",
                    "message": f"{marshal.name} encounters {enemy.name} at {blocked_region}. Odds unfavorable ({ratio:.1f}:1).",
                    "options": ["attack_anyway", "go_around", "retreat", "cancel_order"]
                }

        else:  # cautious
            enemy = enemies[0]
            return {
                "marshal": marshal.name,
                "command": "MOVE_TO",
                "requires_input": True,
                "interrupt_type": "contact",
                "enemy": enemy.name,
                "location": blocked_region,
                "message": f"{marshal.name} reports: Enemy forces at {blocked_region}. How shall I proceed?",
                "options": ["attack", "go_around", "hold_position", "cancel_order"]
            }

    def _should_auto_attack(self, marshal: Marshal, enemy: Marshal, world: WorldState) -> bool:
        """
        Check if should auto-attack or ask player instead (combat loop prevention).

        Returns False if we fought this same enemy within 1 turn.
        """
        order = marshal.strategic_order

        if (order.last_combat_enemy == enemy.name and
            order.last_combat_turn is not None and
            world.current_turn - order.last_combat_turn <= 1):
            return False  # Ask player instead

        return True  # OK to auto-attack

    # ════════════════════════════════════════════════════════════════════════════
    # PURSUE EXECUTION
    # ════════════════════════════════════════════════════════════════════════════

    def _execute_pursue(self, marshal: Marshal, world: WorldState,
                         game_state: Dict) -> Dict:
        """
        Execute one turn of PURSUE.

        IMPORTANT: Respects marshal.movement_range (cavalry=2, infantry=1)

        Behavior:
        - Track target location each turn
        - Move toward target (up to movement_range regions)
        - Attack when in same region
        - Complete when target destroyed
        """
        order = marshal.strategic_order
        target_name = order.target

        # Find target
        target = world.get_marshal(target_name)
        if not target or target.strength <= 0:
            return self._complete_order(marshal, world, f"{target_name} has been destroyed")

        # Same region? Attack!
        if marshal.location == target.location:
            # Combat loop check
            if not self._should_auto_attack(marshal, target, world):
                return {
                    "marshal": marshal.name,
                    "command": "PURSUE",
                    "requires_input": True,
                    "interrupt_type": "repeated_combat",
                    "enemy": target.name,
                    "message": f"Fought {target.name} last turn with no decisive result. Attack again?",
                    "options": ["attack_again", "hold_position", "cancel_order"]
                }

            result = self.executor.execute({
                "marshal": marshal.name,
                "action": "attack",
                "target": target.name,
                "_strategic_execution": True
            }, game_state)

            return self._handle_combat_during_strategic(
                marshal, target, result, world, game_state
            )

        # Not same region - move toward target (respecting movement_range)
        order.path = world.find_path(marshal.location, target.location)

        if not order.path:
            return self._break_order(marshal, f"Cannot reach {target_name}")

        # Move up to movement_range regions
        regions_to_move = getattr(marshal, 'movement_range', 1)
        moves_made = []

        for _ in range(regions_to_move):
            if not order.path:
                break

            next_region = order.path[0]

            # Check for other enemies blocking
            enemies = world.get_enemies_in_region(next_region, marshal.nation)
            blocking_enemies = [e for e in enemies if e.name != target_name]

            if blocking_enemies:
                if moves_made:
                    break  # Already moved some, stop here
                return self._handle_blocked_path(marshal, blocking_enemies, next_region, world, game_state)

            # Move
            result = self.executor.execute({
                "marshal": marshal.name,
                "action": "move",
                "target": next_region,
                "_strategic_execution": True
            }, game_state)

            if result.get("success"):
                order.path.pop(0)
                moves_made.append(next_region)

                # Check if we caught up to target
                if marshal.location == target.location:
                    break
            else:
                break

        if moves_made:
            distance = world.get_distance(marshal.location, target.location)
            return {
                "marshal": marshal.name,
                "command": "PURSUE",
                "action": "move",
                "regions_moved": moves_made,
                "target": target_name,
                "target_location": target.location,
                "distance": distance,
                "order_status": "continues",
                "message": f"{marshal.name} pursues {target_name}. {distance} region(s) away."
            }

        return {"marshal": marshal.name, "error": "Could not move toward target"}

    # ════════════════════════════════════════════════════════════════════════════
    # HOLD EXECUTION
    # ════════════════════════════════════════════════════════════════════════════

    def _execute_hold(self, marshal: Marshal, world: WorldState,
                       game_state: Dict) -> Dict:
        """
        Execute one turn of HOLD.

        IMPORTANT: Sally attacks do NOT move the marshal (Issue #7 fix)

        Behavior varies by personality:
        - AGGRESSIVE: Active defense (sallies out but RETURNS)
        - CAUTIOUS: Passive defense (auto-fortify)
        - LITERAL: Exact position (Immovable bonus)
        """
        order = marshal.strategic_order
        personality = marshal.personality

        # Ensure marshal is at hold location
        if marshal.location != order.target:
            # Need to get there first - use movement
            order.path = world.find_path(marshal.location, order.target)
            if order.path:
                return self._execute_move_to(marshal, world, game_state)
            else:
                return self._break_order(marshal, f"Cannot reach {order.target} to hold it")

        # At hold location - personality-specific behavior
        if personality == "literal":
            # Activate Immovable
            marshal.holding_position = True
            marshal.hold_region = marshal.location
            return {
                "marshal": marshal.name,
                "command": "HOLD",
                "action": "hold_position",
                "location": marshal.location,
                "immovable": True,
                "order_status": "continues",
                "message": f"{marshal.name} holds {marshal.location} with iron discipline. (+15% defense)"
            }

        elif personality == "cautious":
            # Auto-fortify if not already
            if not getattr(marshal, 'fortified', False):
                result = self.executor.execute({
                    "marshal": marshal.name,
                    "action": "fortify",
                    "_strategic_execution": True
                }, game_state)

            return {
                "marshal": marshal.name,
                "command": "HOLD",
                "action": "fortify",
                "location": marshal.location,
                "order_status": "continues",
                "message": f"{marshal.name} fortifies position at {marshal.location}."
            }

        else:  # aggressive
            # Check for nearby enemies to attack
            hold_location = marshal.location  # Store before any action

            for adj_name in world.get_region(marshal.location).adjacent_regions:
                enemies = world.get_enemies_in_region(adj_name, marshal.nation)
                if enemies:
                    # Aggressive wants to sally out
                    enemy = enemies[0]
                    ratio = marshal.strength / max(1, enemy.strength)

                    if ratio >= 1.0:  # Favorable
                        # ═══════════════════════════════════════════════════════════════════
                        # SALLY FIX (Issue #7)
                        # Sally is a "sortie" - combat happens but position unchanged
                        # We execute attack but ensure marshal stays at hold location
                        # ═══════════════════════════════════════════════════════════════════

                        # Execute attack as sortie (don't advance on victory)
                        result = self.executor.execute({
                            "marshal": marshal.name,
                            "action": "attack",
                            "target": enemy.name,
                            "_strategic_execution": True,
                            "_sortie": True  # Flag to prevent position change
                        }, game_state)

                        # Ensure marshal returns to hold position
                        # (In case executor moved them)
                        if marshal.location != hold_location:
                            marshal.location = hold_location

                        return {
                            "marshal": marshal.name,
                            "command": "HOLD",
                            "action": "sally",
                            "target": enemy.name,
                            "combat_result": result,
                            "returned_to": hold_location,
                            "order_status": "continues",
                            "message": f"{marshal.name} sallies forth to attack {enemy.name}, then returns to {hold_location}!"
                        }

            # No opportunity - just hold
            return {
                "marshal": marshal.name,
                "command": "HOLD",
                "action": "active_defense",
                "location": marshal.location,
                "order_status": "continues",
                "message": f"{marshal.name} holds {marshal.location}, ready to strike."
            }

    # ════════════════════════════════════════════════════════════════════════════
    # SUPPORT EXECUTION
    # ════════════════════════════════════════════════════════════════════════════

    def _execute_support(self, marshal: Marshal, world: WorldState,
                          game_state: Dict) -> Dict:
        """
        Execute one turn of SUPPORT.

        IMPORTANT: Respects marshal.movement_range (cavalry=2, infantry=1)

        Behavior:
        - Move to ally's location
        - Join ally's battles
        - Follow if ally moves (personality-dependent)
        """
        order = marshal.strategic_order
        ally_name = order.target

        # Find ally
        ally = world.get_marshal(ally_name)
        if not ally or ally.strength <= 0:
            return self._break_order(marshal, f"{ally_name} has fallen")

        # Same location as ally?
        if marshal.location == ally.location:
            return self._execute_support_active(marshal, ally, world, game_state)

        # Need to reach ally
        # Check if ally is moving
        if ally.in_strategic_mode and ally.strategic_order.command_type == "MOVE_TO":
            return self._handle_ally_moving(marshal, ally, world, game_state)

        # Move toward ally (respecting movement_range)
        path = world.find_path(marshal.location, ally.location)
        if not path:
            return self._break_order(marshal, f"Cannot reach {ally_name}")

        regions_to_move = getattr(marshal, 'movement_range', 1)
        moves_made = []

        for _ in range(regions_to_move):
            if not path:
                break

            next_region = path[0]

            # Check for blocking enemies
            enemies = world.get_enemies_in_region(next_region, marshal.nation)
            if enemies:
                if moves_made:
                    break
                return self._handle_blocked_path(marshal, enemies, next_region, world, game_state)

            # Move
            result = self.executor.execute({
                "marshal": marshal.name,
                "action": "move",
                "target": next_region,
                "_strategic_execution": True
            }, game_state)

            if result.get("success"):
                path.pop(0)
                moves_made.append(next_region)

                # Check if we reached ally
                if marshal.location == ally.location:
                    break
            else:
                break

        if moves_made:
            distance = world.get_distance(marshal.location, ally.location)
            return {
                "marshal": marshal.name,
                "command": "SUPPORT",
                "action": "move_to_ally",
                "regions_moved": moves_made,
                "ally": ally_name,
                "ally_location": ally.location,
                "distance": distance,
                "order_status": "continues",
                "message": f"{marshal.name} moves to support {ally_name}. {distance} region(s) away."
            }

        return {"marshal": marshal.name, "error": "Could not move toward ally"}

    def _execute_support_active(self, marshal: Marshal, ally: Marshal,
                                 world: WorldState, game_state: Dict) -> Dict:
        """Handle support when already with ally."""
        order = marshal.strategic_order
        personality = marshal.personality

        # ═══════════════════════════════════════════════════════════════════
        # BATTLE DETECTION (Issue #11 fix)
        # Check if ally was in combat this turn
        # ═══════════════════════════════════════════════════════════════════
        if ally.in_combat_this_turn:
            # Ally just fought - check result for until_battle_won
            if ally.last_combat_result == "victory":
                return self._complete_order(marshal, world, f"{ally.name} won the battle!")

        # Check if ally is safe (no enemies adjacent)
        allies_safe = True
        for adj_name in world.get_region(ally.location).adjacent_regions:
            if world.get_enemies_in_region(adj_name, ally.nation):
                allies_safe = False
                break

        if allies_safe:
            return self._complete_order(marshal, world, f"{ally.name} is secure")

        # Support behavior based on personality
        if personality == "aggressive":
            return {
                "marshal": marshal.name,
                "command": "SUPPORT",
                "action": "supporting_offensive",
                "ally": ally.name,
                "order_status": "continues",
                "message": f"{marshal.name} supports {ally.name}, ready to join any attack."
            }
        elif personality == "cautious":
            # Auto-fortify in support
            if not getattr(marshal, 'fortified', False):
                self.executor.execute({
                    "marshal": marshal.name,
                    "action": "fortify",
                    "_strategic_execution": True
                }, game_state)
            return {
                "marshal": marshal.name,
                "command": "SUPPORT",
                "action": "supporting_defensive",
                "ally": ally.name,
                "order_status": "continues",
                "message": f"{marshal.name} fortifies position near {ally.name}."
            }
        else:  # literal
            return {
                "marshal": marshal.name,
                "command": "SUPPORT",
                "action": "supporting_precise",
                "ally": ally.name,
                "order_status": "continues",
                "message": f"{marshal.name} stays with {ally.name} exactly as ordered."
            }

    def _handle_ally_moving(self, marshal: Marshal, ally: Marshal,
                            world: WorldState, game_state: Dict) -> Dict:
        """Handle case where supported ally is moving."""
        personality = marshal.personality

        if personality == "cautious":
            # Ask player
            return {
                "marshal": marshal.name,
                "command": "SUPPORT",
                "requires_input": True,
                "interrupt_type": "ally_moving",
                "ally": ally.name,
                "ally_destination": ally.strategic_order.target,
                "message": f"{ally.name} is marching to {ally.strategic_order.target}. Follow or hold position?",
                "options": ["follow", "hold_current", "cancel_support"]
            }
        else:
            # Aggressive and Literal follow (respecting movement_range)
            path = world.find_path(marshal.location, ally.location)
            if path:
                regions_to_move = getattr(marshal, 'movement_range', 1)
                moves_made = []

                for _ in range(regions_to_move):
                    if not path:
                        break
                    next_region = path[0]
                    result = self.executor.execute({
                        "marshal": marshal.name,
                        "action": "move",
                        "target": next_region,
                        "_strategic_execution": True
                    }, game_state)

                    if result.get("success"):
                        path.pop(0)
                        moves_made.append(next_region)
                    else:
                        break

                if moves_made:
                    return {
                        "marshal": marshal.name,
                        "command": "SUPPORT",
                        "action": "following_ally",
                        "regions_moved": moves_made,
                        "ally": ally.name,
                        "order_status": "continues",
                        "message": f"{marshal.name} follows {ally.name}."
                    }

            return self._break_order(marshal, f"Lost contact with {ally.name}")

    # ════════════════════════════════════════════════════════════════════════════
    # INTERRUPT HANDLING
    # ════════════════════════════════════════════════════════════════════════════

    def _check_interrupts(self, marshal: Marshal, world: WorldState) -> Optional[Dict]:
        """
        Check for events that might interrupt strategic execution.

        Returns:
            Interrupt dict if interrupt detected, None otherwise
        """
        order = marshal.strategic_order
        personality = marshal.personality

        # LITERAL never gets interrupted by cannon fire
        if personality == "literal":
            return None

        # ═══════════════════════════════════════════════════════════════════
        # CANNON FIRE DETECTION (Issue #4 fix)
        # Uses world.battles_this_turn instead of non-existent _active_battles
        # ═══════════════════════════════════════════════════════════════════
        nearby_battles = world.get_battles_within_range(marshal.location, 2)

        for battle in nearby_battles:
            # Don't interrupt for battles we're involved in
            if battle["attacker"] == marshal.name or battle["defender"] == marshal.name:
                continue

            return {
                "type": "cannon_fire",
                "battle_location": battle["location"],
                "combatants": [battle["attacker"], battle["defender"]]
            }

        return None

    def _handle_interrupt(self, marshal: Marshal, interrupt: Dict,
                          world: WorldState, game_state: Dict) -> Optional[Dict]:
        """Handle an interrupt event."""
        personality = marshal.personality
        interrupt_type = interrupt.get("type")

        if interrupt_type == "cannon_fire":
            if personality == "aggressive":
                # Rush toward battle
                battle_location = interrupt.get("battle_location")
                return {
                    "marshal": marshal.name,
                    "interrupt": "cannon_fire",
                    "action": "redirecting",
                    "to": battle_location,
                    "order_status": "redirected",
                    "message": f"{marshal.name} hears cannon fire! Rushing to {battle_location}!"
                }
            else:  # cautious
                return {
                    "marshal": marshal.name,
                    "interrupt": "cannon_fire",
                    "requires_input": True,
                    "battle_location": interrupt.get("battle_location"),
                    "message": f"{marshal.name} reports: Battle at {interrupt.get('battle_location')}. Investigate or continue?",
                    "options": ["investigate", "continue_order", "hold_position"]
                }

        return None

    # ════════════════════════════════════════════════════════════════════════════
    # CONDITION CHECKING
    # ════════════════════════════════════════════════════════════════════════════

    def _check_condition(self, marshal: Marshal, condition, world: WorldState) -> Tuple[bool, str]:
        """
        Check if strategic condition is met.

        Returns:
            (condition_met: bool, reason: str)
        """
        if condition.max_turns is not None:
            turns_active = world.current_turn - marshal.strategic_order.started_turn
            if turns_active >= condition.max_turns:
                return (True, f"Held for {condition.max_turns} turns as ordered")

        if condition.until_marshal_arrives:
            target_name = condition.until_marshal_arrives
            target = world.get_marshal(target_name)
            if target and target.location == marshal.location:
                return (True, f"{target_name} has arrived")

        if condition.until_marshal_destroyed:
            target_name = condition.until_marshal_destroyed
            target = world.get_marshal(target_name)
            if not target or target.strength <= 0:
                return (True, f"{target_name} has been destroyed")

        if condition.until_relieved:
            allies_here = [m for m in world.get_marshals_in_region(marshal.location)
                         if m.nation == marshal.nation and m.name != marshal.name]
            if allies_here:
                return (True, f"Relieved by {allies_here[0].name}")

        # ═══════════════════════════════════════════════════════════════════
        # until_battle_won IMPLEMENTATION (Issue #5)
        # ═══════════════════════════════════════════════════════════════════
        if condition.until_battle_won:
            order = marshal.strategic_order

            # For SUPPORT orders, check the supported ally's last combat
            if order.command_type == "SUPPORT":
                ally = world.get_marshal(order.target)
                if ally and ally.last_combat_result == "victory":
                    return (True, f"{ally.name} won the battle!")

            # For HOLD orders, check if marshal won a defensive battle
            elif order.command_type == "HOLD":
                if marshal.last_combat_result == "victory":
                    return (True, "Battle won! Position secured.")

            # Check battles this turn for our involvement
            for battle in world.battles_this_turn:
                if battle["location"] == marshal.location:
                    is_attacker = battle["attacker"] == marshal.name
                    is_defender = battle["defender"] == marshal.name

                    if is_attacker or is_defender:
                        if ((battle["result"] == "attacker_victory" and is_attacker) or
                            (battle["result"] == "defender_victory" and is_defender)):
                            return (True, "Victory achieved!")

        return (False, "")

    # ════════════════════════════════════════════════════════════════════════════
    # COMBAT DURING STRATEGIC
    # ════════════════════════════════════════════════════════════════════════════

    def _handle_combat_during_strategic(self, marshal: Marshal, enemy: Marshal,
                                         combat_result: Dict, world: WorldState,
                                         game_state: Dict) -> Dict:
        """
        Handle combat result during strategic execution.

        Victory → Order continues (path cleared)
        Defeat → Order breaks (need recovery)
        Stalemate → Ask player
        """
        order = marshal.strategic_order
        outcome = combat_result.get("events", [{}])[0].get("outcome", "unknown")

        # Record combat for loop prevention
        order.last_combat_enemy = enemy.name
        order.last_combat_turn = world.current_turn
        order.last_combat_result = outcome

        # Also update marshal's combat tracking
        marshal.in_combat_this_turn = True
        marshal.last_combat_turn = world.current_turn
        marshal.last_combat_location = marshal.location

        if "victory" in outcome and "defender" not in outcome:
            # Attacker victory - continue
            marshal.last_combat_result = "victory"
            return {
                "marshal": marshal.name,
                "action": "combat",
                "target": enemy.name,
                "outcome": outcome,
                "order_status": "continues",
                "message": f"{marshal.name} defeats {enemy.name}! Continuing mission."
            }

        elif "defeat" in outcome or "defender_victory" in outcome:
            # Defeat - break order
            marshal.last_combat_result = "defeat"
            self._break_order(marshal, f"Defeated by {enemy.name}")
            return {
                "marshal": marshal.name,
                "action": "combat",
                "target": enemy.name,
                "outcome": outcome,
                "order_status": "breaks",
                "message": f"{marshal.name} defeated by {enemy.name}. Awaiting new orders."
            }

        else:
            # Stalemate or unclear - ask player
            marshal.last_combat_result = "stalemate"
            return {
                "marshal": marshal.name,
                "action": "combat",
                "target": enemy.name,
                "outcome": outcome,
                "requires_input": True,
                "message": f"Battle with {enemy.name} inconclusive. Continue mission or await orders?",
                "options": ["continue_order", "hold_position", "retreat", "cancel_order"]
            }

    # ════════════════════════════════════════════════════════════════════════════
    # ORDER COMPLETION/BREAKING
    # ════════════════════════════════════════════════════════════════════════════

    def _complete_order(self, marshal: Marshal, world: WorldState, reason: str) -> Dict:
        """
        Complete a strategic order successfully.

        Applies LITERAL completion bonus if applicable.
        """
        order = marshal.strategic_order
        marshal.strategic_order = None

        # LITERAL completion bonus
        if marshal.personality == "literal":
            marshal.precision_bonus_available = True
            # Use correct Trust API (Issue #10)
            marshal.trust.modify(5)  # +5 trust for completing strategic

        return {
            "marshal": marshal.name,
            "command": order.command_type,
            "order_status": "completed",
            "reason": reason,
            "message": f"{marshal.name}'s orders complete: {reason}",
            "precision_bonus": marshal.personality == "literal"
        }

    def _break_order(self, marshal: Marshal, reason: str) -> Dict:
        """
        Break a strategic order (could not complete).
        """
        order = marshal.strategic_order
        marshal.strategic_order = None

        return {
            "marshal": marshal.name,
            "command": order.command_type if order else "unknown",
            "order_status": "breaks",
            "reason": reason,
            "message": f"{marshal.name}'s orders cancelled: {reason}"
        }

    # ════════════════════════════════════════════════════════════════════════════
    # UTILITIES
    # ════════════════════════════════════════════════════════════════════════════

    def _calculate_path(self, marshal: Marshal, destination: str,
                        world: WorldState) -> Optional[List[str]]:
        """
        Calculate path based on personality.

        AGGRESSIVE: Shortest path (through enemies if needed)
        CAUTIOUS: Safest path (avoids enemies)
        LITERAL: Shortest path that avoids enemies
        """
        personality = marshal.personality

        if personality == "cautious":
            return world.find_path(
                marshal.location, destination,
                avoid_enemies=True, marshal_nation=marshal.nation
            )
        elif personality == "literal":
            # Try safe path first
            safe_path = world.find_path(
                marshal.location, destination,
                avoid_enemies=True, marshal_nation=marshal.nation
            )
            if safe_path:
                return safe_path
            # Fall back to any path
            return world.find_path(marshal.location, destination)
        else:  # aggressive
            return world.find_path(marshal.location, destination)
```

---

## 12. IMPLEMENTATION ORDER

**Follow this order exactly. Each step depends on previous steps.**

### Phase A: Data Structures (Estimated: 3-4 hours)

- [x] **A1.** Add `StrategicOrder` dataclass to `marshal.py` (with combat loop fields) ✅
- [x] **A2.** Add `StrategicCondition` dataclass to `marshal.py` ✅
- [x] **A3.** Add marshal fields: `strategic_order`, `precision_bonus_available`, combat tracking ✅
- [x] **A4.** Add `@property in_strategic_mode` to Marshal class ✅
- [x] **A5.** Update `GROUCHY_MODIFIERS` in `personality_modifiers.py` ✅
- [x] **A6.** Add battle tracking to `WorldState` (battles_this_turn, record_battle, etc.) ✅
- [x] **A7.** Test: Create marshal, set strategic_order, verify serialization ✅ (15 tests in test_strategic_order.py)

### Phase B: Parser Integration (Estimated: 4-5 hours)

- [x] **B1.** Create `backend/ai/strategic_parser.py` ✅ (placed in ai/ not commands/ — standalone detection module)
- [x] **B2.** Add `STRATEGIC_KEYWORDS` ✅ (in strategic_parser.py, not llm_client.py — cleaner separation)
- [x] **B3.** Add `detect_strategic_command()` + `_classify_target()` functions ✅
- [x] **B4.** Add `_parse_condition()` for "until X" patterns ✅
- [ ] **B5.** Add `is_explicit_order()` for LITERAL bonus detection (deferred to Phase H)
- [x] **B6.** Add target classification with auto-convert enemy MOVE_TO→PURSUE, attack_on_arrival ✅
- [x] **B7.** Test: 45 tests in test_strategic_parser.py + 4 integration tests through parser.py ✅

### Pre-Phase C: Dependencies ✅

- [x] `get_enemies_in_region(region, nation)` added to WorldState ✅
- [x] `find_path()` updated with `avoid_regions` parameter ✅
- [x] Tests for new methods (12 tests in test_world_state_strategic.py) ✅

### Phase C: Strategic Executor (Estimated: 6-8 hours)

- [ ] **C1.** Create `backend/commands/strategic.py`
- [ ] **C2.** Implement `StrategicExecutor` class
- [ ] **C3.** Implement `_execute_move_to()` with cavalry movement loop
- [ ] **C4.** Implement `_execute_pursue()` with target tracking and cavalry movement
- [ ] **C5.** Implement `_execute_hold()` with sally-return mechanic
- [ ] **C6.** Implement `_execute_support()` with ally tracking
- [ ] **C7.** Implement combat loop prevention (_should_auto_attack)
- [ ] **C8.** Test: Execute each command type with cavalry vs infantry

### Phase D: Interrupt & Condition System (Estimated: 4-5 hours)

- [ ] **D1.** Add `_check_interrupts()` with battle tracking
- [ ] **D2.** Implement CONTACT detection (blocking path)
- [ ] **D3.** Implement ADJACENT detection (nearby threat)
- [ ] **D4.** Implement CANNON_FIRE detection (using battles_this_turn)
- [ ] **D5.** Implement `until_battle_won` condition fully
- [ ] **D6.** Implement personality-based interrupt response
- [ ] **D7.** Implement combat result → order status logic
- [ ] **D8.** Test: Marshal encounters enemy during MOVE_TO, LITERAL ignores cannon fire

### Phase E: Command Override System (Estimated: 3-4 hours)

- [ ] **E1.** Add override/non-override/cancel command categories
- [ ] **E2.** Add `_check_strategic_override()` to executor.py
- [ ] **E3.** Integrate override check into execute() flow
- [ ] **E4.** Test: "Wait" doesn't cancel strategic, "Attack" does

### Phase F: Turn Integration (Estimated: 3-4 hours)

- [ ] **F1.** Modify `turn_manager.py` to call strategic executor
- [ ] **F2.** Add strategic report to end_turn result
- [ ] **F3.** Ensure strategic execution happens AFTER enemy phase, BEFORE autonomous
- [ ] **F4.** Add battle recording to combat.py (call world.record_battle)
- [ ] **F5.** Add clear_turn_battles() to advance_turn()
- [ ] **F6.** Test: Full turn cycle with strategic order active

### Phase G: Clarification System (Estimated: 3-4 hours)

- [ ] **G1.** Add clarification detection for LITERAL + generic commands
- [ ] **G2.** Implement `generate_clarification_options()` fully
- [ ] **G3.** Reuse objection popup with "CLARIFICATION REQUIRED" header
- [ ] **G4.** Handle clarification response in executor
- [ ] **G5.** Test: "Grouchy, pursue the enemy" triggers clarification with options

### Phase H: LITERAL Bonuses & Action Cost (Estimated: 3-4 hours)

- [ ] **H1.** Implement `_execute_strategic_command()` with action cost logic
- [ ] **H2.** Apply +10% attack/defense for explicit orders
- [ ] **H3.** Set precision_bonus on strategic completion
- [ ] **H4.** Consume precision bonus on next action (+20%)
- [ ] **H5.** Verify 1-action cost for LITERAL, 2 for others
- [ ] **H6.** Test: Grouchy completes MOVE_TO, gets +20% on next action

### Phase I: Save/Load Integration (Estimated: 2-3 hours)

- [ ] **I1.** Add StrategicOrder serialization to marshal save/load
- [ ] **I2.** Add battles_this_turn to world state save (or clear on load)
- [ ] **I3.** Test: Save with active strategic order, load, verify order persists

### Phase J: UI Updates (Estimated: 4-5 hours)

- [ ] **J1.** Add strategic order indicator to marshal display
- [ ] **J2.** Modify end_turn popup to show strategic reports
- [ ] **J3.** Add clarification popup variant (reuse objection popup)
- [ ] **J4.** Show "March to Vienna (Turn 2/4)" in status
- [ ] **J5.** Add GDScript integration for strategic responses
- [ ] **J6.** Test: Visual verification of strategic mode display

### Phase K: Integration Testing (Estimated: 4-5 hours)

- [ ] **K1.** Test MOVE_TO with all 3 personalities (cavalry and infantry)
- [ ] **K2.** Test PURSUE with target destruction
- [ ] **K3.** Test HOLD with "until relieved" condition
- [ ] **K4.** Test HOLD sally-return mechanic
- [ ] **K5.** Test SUPPORT with ally in combat (until_battle_won)
- [ ] **K6.** Test strategic order cancel via tactical override
- [ ] **K7.** Test explicit cancel command (costs 1 action)
- [ ] **K8.** Test Grouchy cannon fire (should NOT interrupt)
- [ ] **K9.** Test combat loop prevention (stalemate → continue → no auto-attack)
- [ ] **K10.** Test cavalry moves 2 regions per turn

**Total Estimated Time: 35-45 hours**

---

## 13. TEST CASES (Issue #12)

### 13.1 Critical Test Scenarios

```python
# test_strategic_commands.py
import pytest
from backend.models.marshal import Marshal, StrategicOrder, StrategicCondition
from backend.models.world_state import WorldState
from backend.commands.strategic import StrategicExecutor
from backend.commands.executor import CommandExecutor


class TestStrategicMoveTo:
    """Tests for MOVE_TO strategic command."""

    def test_move_to_arrival(self, game_state_fixture):
        """Marshal arrives at destination, order completes."""
        world = game_state_fixture["world"]
        ney = world.get_marshal("Ney")

        # Setup: Ney at Belgium, order MOVE_TO Vienna (3 regions away)
        ney.location = "Belgium"
        ney.strategic_order = StrategicOrder(
            command_type="MOVE_TO",
            target="Vienna",
            target_type="region",
            started_turn=1,
            original_command="March to Vienna"
        )

        # Execute: Process strategic orders for 3 turns (cavalry moves 2/turn)
        executor = StrategicExecutor(CommandExecutor())

        # Turn 1: Move 2 regions
        report = executor._execute_strategic_turn(ney, world, game_state_fixture)
        assert report["order_status"] == "continues"
        assert len(report.get("regions_moved", [])) == 2  # Cavalry moves 2

        # Turn 2: Arrive
        report = executor._execute_strategic_turn(ney, world, game_state_fixture)
        assert report["order_status"] == "completed"
        assert ney.location == "Vienna"
        assert ney.strategic_order is None

    def test_move_to_cavalry_vs_infantry(self, game_state_fixture):
        """Cavalry moves 2 regions per turn, infantry moves 1."""
        world = game_state_fixture["world"]

        # Setup cavalry (Ney, movement_range=2)
        ney = world.get_marshal("Ney")
        ney.movement_range = 2
        ney.location = "Paris"
        ney.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target="Vienna", target_type="region",
            started_turn=1, original_command="March to Vienna"
        )
        ney.strategic_order.path = ["Belgium", "Rhine", "Bavaria", "Vienna"]

        # Setup infantry (Davout, movement_range=1)
        davout = world.get_marshal("Davout")
        davout.movement_range = 1
        davout.location = "Paris"
        davout.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target="Vienna", target_type="region",
            started_turn=1, original_command="March to Vienna"
        )
        davout.strategic_order.path = ["Belgium", "Rhine", "Bavaria", "Vienna"]

        executor = StrategicExecutor(CommandExecutor())

        # Execute one turn each
        ney_report = executor._execute_move_to(ney, world, game_state_fixture)
        davout_report = executor._execute_move_to(davout, world, game_state_fixture)

        # Cavalry should move 2 regions
        assert len(ney_report.get("regions_moved", [])) == 2
        # Infantry should move 1 region
        assert len(davout_report.get("regions_moved", [])) == 1


class TestStrategicPursue:
    """Tests for PURSUE strategic command."""

    def test_pursue_target_destroyed(self, game_state_fixture):
        """Pursue completes when target destroyed."""
        world = game_state_fixture["world"]
        ney = world.get_marshal("Ney")
        blucher = world.get_marshal("Blucher")

        # Setup: Ney pursuing Blucher, Blucher has minimal troops
        blucher.strength = 100  # Will be destroyed in combat
        ney.location = blucher.location  # Same region
        ney.strategic_order = StrategicOrder(
            command_type="PURSUE", target="Blucher", target_type="marshal",
            started_turn=1, original_command="Pursue Blucher"
        )

        executor = StrategicExecutor(CommandExecutor())
        # After combat, Blucher should be destroyed
        blucher.strength = 0

        report = executor._execute_pursue(ney, world, game_state_fixture)
        assert report["order_status"] == "completed"
        assert "destroyed" in report["reason"]


class TestCombatLoopPrevention:
    """Tests for combat loop prevention (Issue #2)."""

    def test_no_auto_attack_after_stalemate(self, game_state_fixture):
        """After stalemate, don't auto-attack same enemy next turn."""
        world = game_state_fixture["world"]
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        # Setup: Ney just fought Wellington last turn
        ney.strategic_order = StrategicOrder(
            command_type="PURSUE", target="Wellington", target_type="marshal",
            started_turn=1, original_command="Pursue Wellington",
            last_combat_enemy="Wellington",
            last_combat_turn=world.current_turn - 1,
            last_combat_result="stalemate"
        )
        ney.location = wellington.location  # Same region

        executor = StrategicExecutor(CommandExecutor())

        # Should ask player instead of auto-attacking
        assert not executor._should_auto_attack(ney, wellington, world)


class TestHoldSally:
    """Tests for HOLD sally mechanic (Issue #7)."""

    def test_sally_returns_to_hold_position(self, game_state_fixture):
        """Sally attack returns marshal to hold position."""
        world = game_state_fixture["world"]
        ney = world.get_marshal("Ney")

        # Setup: Ney holding Belgium, enemy in adjacent region
        ney.location = "Belgium"
        ney.personality = "aggressive"
        ney.strategic_order = StrategicOrder(
            command_type="HOLD", target="Belgium", target_type="region",
            started_turn=1, original_command="Hold Belgium"
        )

        executor = StrategicExecutor(CommandExecutor())
        report = executor._execute_hold(ney, world, game_state_fixture)

        # After sally, should still be at Belgium
        assert ney.location == "Belgium"
        if report.get("action") == "sally":
            assert report.get("returned_to") == "Belgium"


class TestLiteralBonuses:
    """Tests for LITERAL personality bonuses."""

    def test_literal_one_action_cost(self, game_state_fixture):
        """LITERAL strategic commands cost 1 action, others cost 2."""
        from backend.models.personality_modifiers import GROUCHY_MODIFIERS

        # LITERAL cost should be 1
        assert GROUCHY_MODIFIERS.get("strategic_action_cost") == 1

        # In _execute_strategic_command, verify logic:
        # if marshal.personality == "literal":
        #     action_cost = 1
        # else:
        #     action_cost = 2

    def test_literal_completion_bonus(self, game_state_fixture):
        """LITERAL gets +20% precision bonus after completing strategic."""
        world = game_state_fixture["world"]
        grouchy = world.get_marshal("Grouchy")
        grouchy.personality = "literal"

        # Setup completed strategic order
        grouchy.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target="Vienna", target_type="region",
            started_turn=1, original_command="March to Vienna"
        )
        grouchy.location = "Vienna"  # Already arrived

        executor = StrategicExecutor(CommandExecutor())
        report = executor._complete_order(grouchy, world, "Arrived at Vienna")

        # Should have precision bonus available
        assert grouchy.precision_bonus_available == True
        assert report.get("precision_bonus") == True

    def test_literal_no_cannon_fire_interrupt(self, game_state_fixture):
        """LITERAL ignores cannon fire interrupts."""
        world = game_state_fixture["world"]
        grouchy = world.get_marshal("Grouchy")
        grouchy.personality = "literal"
        grouchy.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target="Vienna", target_type="region",
            started_turn=1, original_command="March to Vienna"
        )

        # Add a battle nearby
        world.battles_this_turn = [{
            "location": "Belgium",  # Adjacent to Grouchy
            "attacker": "Wellington",
            "defender": "Ney",
            "result": "ongoing",
            "turn": world.current_turn
        }]

        executor = StrategicExecutor(CommandExecutor())
        interrupt = executor._check_interrupts(grouchy, world)

        # LITERAL should have no interrupt
        assert interrupt is None


class TestConditions:
    """Tests for strategic conditions."""

    def test_until_battle_won_support(self, game_state_fixture):
        """SUPPORT order completes when ally wins battle."""
        world = game_state_fixture["world"]
        grouchy = world.get_marshal("Grouchy")
        ney = world.get_marshal("Ney")

        # Setup: Grouchy supporting Ney until battle won
        grouchy.strategic_order = StrategicOrder(
            command_type="SUPPORT", target="Ney", target_type="marshal",
            started_turn=1, original_command="Support Ney until battle won",
            condition=StrategicCondition(until_battle_won=True)
        )
        grouchy.location = ney.location

        # Ney just won a battle
        ney.last_combat_result = "victory"

        executor = StrategicExecutor(CommandExecutor())
        met, reason = executor._check_condition(grouchy, grouchy.strategic_order.condition, world)

        assert met == True
        assert "won the battle" in reason
```

---

## 14. GODOT UI CHANGES (Issue #14)

### 14.1 Strategic Order Indicator

Add to marshal status panel in `marshal_panel.gd`:

```gdscript
# In _update_marshal_display():

# Strategic order indicator
if marshal_data.has("strategic_order") and marshal_data.strategic_order != null:
    var order = marshal_data.strategic_order
    var turns_active = current_turn - order.started_turn

    # Calculate estimated turns remaining
    var turns_remaining = "?"
    if order.has("path"):
        turns_remaining = str(len(order.path))

    $StrategicIndicator.visible = true
    $StrategicIndicator/Label.text = "[%s → %s - Turn %d]" % [
        order.command_type,
        order.target,
        turns_active + 1
    ]

    # Color based on status
    match order.command_type:
        "MOVE_TO":
            $StrategicIndicator.modulate = Color(0.2, 0.6, 1.0)  # Blue
        "PURSUE":
            $StrategicIndicator.modulate = Color(1.0, 0.4, 0.2)  # Orange
        "HOLD":
            $StrategicIndicator.modulate = Color(0.4, 0.8, 0.3)  # Green
        "SUPPORT":
            $StrategicIndicator.modulate = Color(0.8, 0.6, 1.0)  # Purple
else:
    $StrategicIndicator.visible = false
```

### 14.2 End Turn Report - Strategic Section

In `end_turn_popup.gd`:

```gdscript
signal strategic_response_selected(marshal_name: String, response: String)

func _show_strategic_report(strategic_report: Array) -> void:
    """Display strategic order execution results."""
    if strategic_report.is_empty():
        return

    $StrategicSection.visible = true
    $StrategicSection/Title.text = "STRATEGIC ORDERS:"

    var report_text = ""
    for report in strategic_report:
        var status_icon = ""
        match report.get("order_status", ""):
            "continues": status_icon = "→"
            "completed": status_icon = "✓"
            "breaks": status_icon = "✗"

        report_text += "  %s %s: %s\n" % [
            status_icon,
            report.get("marshal", "Unknown"),
            report.get("message", "")
        ]

        # Check if player input required
        if report.get("requires_input", false):
            _show_strategic_decision(report)
            return  # Stop processing, wait for input

    $StrategicSection/ReportLabel.text = report_text

func _show_strategic_decision(report: Dictionary) -> void:
    """Show decision popup for strategic interrupt."""
    $StrategicDecision.visible = true
    $StrategicDecision/Message.text = report.get("message", "Decision required")

    # Clear existing buttons
    for child in $StrategicDecision/Options.get_children():
        child.queue_free()

    # Add option buttons
    for option in report.get("options", []):
        var button = Button.new()
        button.text = option.replace("_", " ").capitalize()
        button.pressed.connect(_on_strategic_option_pressed.bind(
            report.get("marshal"),
            option
        ))
        $StrategicDecision/Options.add_child(button)

func _on_strategic_option_pressed(marshal_name: String, option: String) -> void:
    $StrategicDecision.visible = false
    strategic_response_selected.emit(marshal_name, option)
```

### 14.3 Clarification Popup

Reuse objection popup with modifications in `objection_popup.gd`:

```gdscript
enum PopupMode { OBJECTION, CLARIFICATION }
var current_mode: PopupMode = PopupMode.OBJECTION

func show_clarification(marshal_name: String, clarification_data: Dictionary) -> void:
    """Show clarification popup for LITERAL personality."""
    current_mode = PopupMode.CLARIFICATION

    $Header.text = "CLARIFICATION REQUIRED"
    $Header.modulate = Color(0.3, 0.5, 1.0)  # Blue for clarification

    $MarshalName.text = marshal_name.to_upper()
    $Message.text = '"%s"' % clarification_data.get("prompt", "Please clarify.")

    # Show options
    $OptionsContainer.visible = true
    for child in $OptionsContainer.get_children():
        child.queue_free()

    for option in clarification_data.get("options", []):
        var btn = Button.new()
        btn.text = "%s\n(%s)" % [option.name, option.details]
        btn.pressed.connect(_on_clarification_option.bind(option.value))
        $OptionsContainer.add_child(btn)

    # Add cancel button
    var cancel_btn = Button.new()
    cancel_btn.text = "Cancel Order"
    cancel_btn.pressed.connect(_on_clarification_cancel)
    $OptionsContainer.add_child(cancel_btn)

    show()

signal clarification_selected(target: String)
signal clarification_cancelled()

func _on_clarification_option(target: String) -> void:
    hide()
    clarification_selected.emit(target)

func _on_clarification_cancel() -> void:
    hide()
    clarification_cancelled.emit()
```

### 14.4 Signal Integration in main.gd

```gdscript
# Connect strategic signals
func _ready():
    # ... existing connections ...
    $EndTurnPopup.strategic_response_selected.connect(_on_strategic_response)
    $ObjectionPopup.clarification_selected.connect(_on_clarification_selected)
    $ObjectionPopup.clarification_cancelled.connect(_on_clarification_cancelled)

func _on_strategic_response(marshal_name: String, response: String) -> void:
    """Handle player response to strategic decision."""
    var command = {
        "type": "strategic_response",
        "marshal": marshal_name,
        "response": response
    }
    _send_command(command)

func _on_clarification_selected(target: String) -> void:
    """Handle LITERAL clarification selection."""
    # Resend command with explicit target
    var command = pending_clarification_command.duplicate()
    command["target"] = target
    command["target_type"] = "explicit"
    pending_clarification_command = {}
    _send_command(command)

func _on_clarification_cancelled() -> void:
    pending_clarification_command = {}
```

---

## 15. SAVE/LOAD INTEGRATION (Issue #15)

### 15.1 Marshal Serialization

In `marshal.py`, update `to_dict()` and `from_dict()`:

```python
def to_dict(self) -> Dict:
    """Serialize marshal for save/load."""
    data = {
        # ... existing fields ...

        # Strategic Order System (Phase 5.2)
        "strategic_order": self.strategic_order.to_dict() if self.strategic_order else None,
        "explicit_order_active": self.explicit_order_active,
        "precision_bonus_available": self.precision_bonus_available,
        "last_order_was_explicit": self.last_order_was_explicit,

        # Combat tracking
        "in_combat_this_turn": self.in_combat_this_turn,
        "last_combat_turn": self.last_combat_turn,
        "last_combat_result": self.last_combat_result,
        "last_combat_location": self.last_combat_location,
    }
    return data

@classmethod
def from_dict(cls, data: Dict) -> 'Marshal':
    """Deserialize marshal from save/load."""
    marshal = cls(
        # ... existing constructor args ...
    )

    # ... existing field restoration ...

    # Strategic Order System (Phase 5.2)
    if data.get("strategic_order"):
        marshal.strategic_order = StrategicOrder.from_dict(data["strategic_order"])
    marshal.explicit_order_active = data.get("explicit_order_active", False)
    marshal.precision_bonus_available = data.get("precision_bonus_available", False)
    marshal.last_order_was_explicit = data.get("last_order_was_explicit", False)

    # Combat tracking
    marshal.in_combat_this_turn = data.get("in_combat_this_turn", False)
    marshal.last_combat_turn = data.get("last_combat_turn")
    marshal.last_combat_result = data.get("last_combat_result")
    marshal.last_combat_location = data.get("last_combat_location")

    return marshal
```

### 15.2 WorldState Serialization

In `world_state.py`:

```python
def to_dict(self) -> Dict:
    """Serialize world state for save/load."""
    return {
        # ... existing fields ...

        # NOTE: battles_this_turn is NOT saved
        # It's transient data that should be cleared on load
        # This is intentional - battles are per-turn events
    }

@classmethod
def from_dict(cls, data: Dict) -> 'WorldState':
    """Deserialize world state from save/load."""
    world = cls()
    # ... existing restoration ...

    # Clear transient battle data
    world.battles_this_turn = []

    return world
```

### 15.3 Integration Point

In `main.py` or wherever save/load is handled:

```python
def save_game(filepath: str, world: WorldState) -> None:
    """Save game to file."""
    import json

    save_data = {
        "version": "5.2",  # Update version for strategic commands
        "world": world.to_dict(),
        "marshals": {name: m.to_dict() for name, m in world.marshals.items()}
    }

    with open(filepath, 'w') as f:
        json.dump(save_data, f, indent=2)

def load_game(filepath: str) -> WorldState:
    """Load game from file."""
    import json

    with open(filepath, 'r') as f:
        save_data = json.load(f)

    world = WorldState.from_dict(save_data["world"])

    for name, marshal_data in save_data["marshals"].items():
        marshal = Marshal.from_dict(marshal_data)
        world.marshals[name] = marshal

    # Clear transient data after load
    world.battles_this_turn = []
    for marshal in world.marshals.values():
        marshal.in_combat_this_turn = False

    return world
```

---

## 16. COMMON ISSUES AND SOLUTIONS

| Issue | Cause | Solution |
|-------|-------|----------|
| Strategic order not executing | Not added to turn_manager flow | Check `_process_strategic_orders()` is called |
| Path is None | Regions not connected | Verify `find_path()` implementation |
| LITERAL getting interrupted | Interrupt check not respecting personality | Add `if personality == "literal": return None` in _check_interrupts |
| Action cost not working | `_strategic_execution` flag not checked | Add flag check in executor action cost logic |
| Combat breaks order incorrectly | Outcome parsing wrong | Check combat result outcome strings |
| Cavalry moves 1 region | movement_range not checked | Add loop `for _ in range(movement_range)` |
| Sally moves marshal | `_sortie` flag not handled | Check for flag, restore location after combat |
| Combat loop infinite | last_combat_* not being set | Ensure combat updates order.last_combat_* |
| Clarification no options | generate_clarification_options empty | Check enemy/ally detection logic |
| until_battle_won never triggers | ally.last_combat_result not set | Ensure combat.py sets marshal.last_combat_result |

---

## 17. GLOSSARY

| Term | Definition |
|------|------------|
| **Strategic order** | Multi-turn command (MOVE_TO, PURSUE, HOLD, SUPPORT) |
| **Tactical command** | Single-turn command (attack, move, defend) |
| **Contact** | Enemy blocking the path |
| **Adjacent** | Enemy nearby but not blocking |
| **Interrupt** | Event that may change order execution |
| **Precision bonus** | +20% effectiveness for LITERAL on next action after completing strategic |
| **Explicit order** | Command with specific target named |
| **Generic order** | Command without specific target |
| **Sally** | Attack from HOLD position that returns marshal to hold location |
| **Sortie** | Same as sally - attack without advancing |
| **Combat loop** | Infinite auto-attack cycle against same enemy |
| **Override command** | Tactical command that cancels active strategic order |

---

## 18. ADDITIONAL ISSUES FOUND DURING SELF-REVIEW

### 18.1 Missing `_sortie` Flag Handling in Executor

**Issue:** The `_execute_hold` sally mechanic sets a `_sortie: True` flag in the attack command, but the executor doesn't check for this flag.

**Fix:** Add to executor.py `_execute_attack()`:

```python
def _execute_attack(self, command: Dict, game_state: Dict) -> Dict:
    # ... existing code ...

    # After combat resolution, before advancing attacker:

    # ═══════════════════════════════════════════════════════════════════
    # SORTIE MECHANIC: Don't advance on victory if this was a sally
    # ═══════════════════════════════════════════════════════════════════
    is_sortie = command.get("_sortie", False)

    if attacker_won and not is_sortie:
        # Normal advance into enemy region
        marshal.location = target.location
    elif attacker_won and is_sortie:
        # Sally - stay at original position
        # marshal.location unchanged
        result["sortie"] = True
        result["message"] += " (Returned to defensive position)"
```

### 18.2 Missing Combat Recording in combat.py

**Issue:** The `_handle_combat_during_strategic` method expects `world.battles_this_turn` to be populated, but nothing calls `world.record_battle()`.

**Fix:** Add to `combat.py` after `resolve_combat()`:

```python
def resolve_combat(attacker, defender, world, ...):
    # ... existing combat logic ...

    # ═══════════════════════════════════════════════════════════════════
    # RECORD BATTLE FOR STRATEGIC SYSTEM (Phase 5.2)
    # ═══════════════════════════════════════════════════════════════════
    world.record_battle(
        location=defender.location,
        attacker=attacker.name,
        defender=defender.name,
        result=outcome  # "attacker_victory", "defender_victory", "stalemate"
    )

    # Also update marshal combat tracking
    attacker.in_combat_this_turn = True
    attacker.last_combat_turn = world.current_turn
    attacker.last_combat_location = defender.location
    attacker.last_combat_result = "victory" if "attacker" in outcome else ("defeat" if "defender" in outcome else "stalemate")

    defender.in_combat_this_turn = True
    defender.last_combat_turn = world.current_turn
    defender.last_combat_location = defender.location
    defender.last_combat_result = "victory" if "defender" in outcome else ("defeat" if "attacker" in outcome else "stalemate")

    return result
```

### 18.3 Missing `world.player_nation` Reference

**Issue:** Code references `world.player_nation` but this field may not exist in all WorldState configurations.

**Fix:** Ensure WorldState has this field:

```python
# In WorldState.__init__():
self.player_nation: str = "France"  # Default player nation
```

### 18.4 Personality Table Row Missing for LITERAL HOLD Ally Help

**Issue:** Table 4.3 says LITERAL "Never leave" for ally help, but no code enforces this.

**Fix:** Already handled by LITERAL not responding to ALLY_COMBAT interrupt (returns None from `_check_interrupts`). Document this in code:

```python
# In _check_interrupts:
# LITERAL never gets interrupted by cannon fire OR ally combat
# This is THE GROUCHY MOMENT - follows orders exactly, ignores everything
if personality == "literal":
    return None  # Never interrupt - follows orders exactly
```

### 18.5 Missing Error Handling for Invalid Targets

**Issue:** If player issues "Pursue Wellington" but Wellington doesn't exist, no graceful error.

**Fix:** Add validation in `_execute_strategic_command`:

```python
# Validate target exists
if target_type == "marshal":
    target_marshal = world.get_marshal(target)
    if not target_marshal:
        return {
            "success": False,
            "message": f"Unknown marshal: {target}. Valid targets: {', '.join(world.get_enemy_marshal_names())}"
        }
elif target_type == "region":
    target_region = world.get_region(target)
    if not target_region:
        return {
            "success": False,
            "message": f"Unknown region: {target}"
        }
```

---

## 19. CODE REVIEW CHECKPOINTS

**STOP AND REQUEST REVIEW at these points:**

1. **After Phase A (Data Structures)** - Before moving to parser
2. **After Phase C (Strategic Executor)** - Before interrupt system
3. **After Phase F (Turn Integration)** - Before UI work
4. **After Phase K (Integration Testing)** - Before marking complete

---

## DOCUMENT END

**Last updated:** January 2025
**Author:** Design locked via Claude Opus conversation
**Status:** Ready for implementation (Revision 2 - All director feedback addressed)
**Revision History:**
- v1.0: Initial design lock
- v2.0: Director feedback applied (15 issues + 5 self-review issues)

If you have questions, ask the user. Do not guess or improvise on design decisions.
