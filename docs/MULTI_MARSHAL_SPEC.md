# Phase 7: Multi-Marshal Coordination — Implementation Spec

> **Status:** FINAL IMPLEMENTATION SPEC
> **Sessions:** 57-66 (10 sessions)
> **Est. New Tests:** ~340
> **Baseline Tests:** 2987 (pre-Phase 7)
> **Last Updated:** February 19, 2026

---

## Table of Contents

1. [Design Principles](#1-design-principles)
2. [Combined Arms Detection](#2-combined-arms-detection)
3. [Coordination Bonus](#3-coordination-bonus)
4. [Dedicated Coordination Bonus](#4-dedicated-coordination-bonus)
5. [Adjacent Support Bonus](#5-adjacent-support-bonus)
6. [SUPPORT Strategic Objection](#6-support-strategic-objection)
7. [Adjacent Reinforcement](#7-adjacent-reinforcement)
8. [Casualty Distribution](#8-casualty-distribution)
9. [Win/Loss Relationship Formula](#9-winloss-relationship-formula)
10. [AI Enhancements](#10-ai-enhancements)
11. [Coordination Preview & Battle Reports](#11-coordination-preview--battle-reports)
12. [Godot UI: Tooltips, Readiness, Display](#12-godot-ui-tooltips-readiness-display)
13. [Supply Interaction](#13-supply-interaction)
14. [Popup & Information Architecture](#14-popup--information-architecture)
15. [Implementation Sessions](#15-implementation-sessions)
16. [Files Touched](#16-files-touched)
17. [Golden Rules & Gotchas](#17-golden-rules--gotchas)
18. [Deferred Items](#18-deferred-items)
19. [Phase 6.5 Sequencing](#19-phase-65-sequencing)
20. [Glossary](#20-glossary)

---

## 1. Design Principles

### Position IS Coordination

All coordination bonuses are **automatic and positional**. No new command syntax. The player types "Ney, attack Wellington" and gets bonuses if they positioned well. Zero new commands to learn.

### Bonus Hierarchy

```
PRIMARY:   Combined Arms  (+10-20% atk, +5-10% def) — unit type diversity
SECONDARY: Coordination   (+3% atk / +5% def per ally) — relationship-scaled
TERTIARY:  Dedicated Coordination (+5%/+5% flat) — time or AP investment
ADJACENT:  Adjacent Support (+2% atk per adjacent ally) — positional pressure

HARD CAP: +25% attack / +20% defense from ALL coordination sources combined
          (combined arms + per-ally coordination + dedicated + adjacent)
```

Flanking (different regions) and coordination (same region) are complementary **opposite** strategies. Both are valid. They never conflict — a marshal attacks from ONE region and gets bonuses from that context only.

### Building Blocks

Every coordination mechanic works identically for player and AI. Same formulas, same thresholds, same bonuses. The AI earns dedicated coordination through co-location duration, not through strategic commands it cannot issue.

### Golden Rule #1 Compliance

All coordination bonuses flow through `marshal.get_attack_modifier()` and `marshal.get_defense_modifier()` via transient fields. `combat.py` reads them, never recalculates. The single-source pattern is preserved.

---

## 2. Combined Arms Detection

### Unit Types

| Type | Current French | Current Coalition |
|------|---------------|-------------------|
| Infantry | Davout, Grouchy | Wellington, Blucher, Gneisenau |
| Cavalry | Ney | Uxbridge |
| Artillery | Drouot | PrinceAugust |

### Bonus Values

| Types Present | Attack Bonus | Defense Bonus |
|---------------|-------------|--------------|
| 1 of 3 | +0% | +0% |
| 2 of 3 | +10% | +5% |
| 3 of 3 | +20% | +10% |

### Rules

- NOT relationship-scaled. Unit type diversity, not marshal opinions.
- Check all non-broken, non-retreating, non-recovering same-nation marshals in region.
- Unit type PRESENCE confers bonus even if that type isn't the one attacking/defending.
- Garrison detachments (region property) do NOT count.
- **Fortified marshals STILL count** toward unit type for combined arms. Their presence (type) matters, not their posture.

### Implementation

```python
def _count_unit_types(self, region_name: str, nation: str, world: WorldState) -> int:
    """Count distinct unit types among eligible marshals in a region."""
    types = set()
    for m in world.marshals.values():
        if (m.location == region_name
                and m.nation == nation
                and m.strength > 0
                and not getattr(m, 'broken', False)
                and not getattr(m, 'retreated_this_turn', False)
                and getattr(m, 'retreat_recovery', 0) == 0):
            if getattr(m, 'artillery', False):
                types.add('artillery')
            elif getattr(m, 'cavalry', False):
                types.add('cavalry')
            else:
                types.add('infantry')
    return len(types)

def _get_combined_arms_bonus(self, type_count: int) -> tuple[float, float]:
    """Returns (attack_bonus, defense_bonus) as decimals."""
    if type_count >= 3:
        return (0.20, 0.10)
    elif type_count == 2:
        return (0.10, 0.05)
    return (0.0, 0.0)
```

### Transient Fields (marshal.py)

```python
# Added to __init__ — NOT serialized
self.combined_arms_attack_bonus: float = 0.0
self.combined_arms_defense_bonus: float = 0.0
```

Applied in `get_attack_modifier()` and `get_defense_modifier()` via `getattr` with 0.0 default:

```python
# At END of get_attack_modifier(), before return:
modifier *= (1.0 + getattr(self, 'combined_arms_attack_bonus', 0.0))
```

---

## 3. Coordination Bonus

### Per-Ally Bonus

For each eligible same-nation ally in the same region:

| Metric | Base Value |
|--------|-----------|
| Attack | +3% per ally |
| Defense | +5% per ally |

### Relationship Scaling

The bonus scales by what the **fighting marshal** thinks of the ally:

| Relationship | Value | Scaling | Effective Attack | Effective Defense |
|-------------|-------|---------|-----------------|------------------|
| Hostile | -2 | 0.00 (0%) | +0% | +0% |
| Rival | -1 | 0.50 (50%) | +1.5% | +2.5% |
| Professional | 0 | 1.00 (100%) | +3% | +5% |
| Friendly | +1 | 1.25 (125%) | +3.75% | +6.25% |
| Devoted | +2 | 1.50 (150%) | +4.5% | +7.5% |

### Eligibility Filters

An ally contributes coordination if ALL of:
- Same nation as fighting marshal
- Same region as fighting marshal
- `strength > 0`
- NOT `broken`
- NOT `retreated_this_turn`
- `retreat_recovery == 0`

### Fortification Rule

- **Fortified non-artillery marshals:** DEFENSE coordination only. They provide covering fire and fallback positions but are committed to defense, not available for offensive coordination. Attack coordination = 0.
- **Fortified artillery:** BOTH attack and defense coordination. Artillery fires from fixed positions regardless of fortification status.
- **Combined arms:** Unaffected by fortification — type presence still counts.

### Implementation

```python
def _calculate_coordination_bonus(self, marshal, allies, world) -> tuple[float, float]:
    """Calculate per-ally coordination bonus for a marshal."""
    total_atk = 0.0
    total_def = 0.0

    SCALING = {-2: 0.0, -1: 0.50, 0: 1.0, 1: 1.25, 2: 1.50}

    for ally in allies:
        rel = marshal.get_relationship(ally.name)
        scale = SCALING.get(rel, 1.0)

        is_fortified_non_artillery = (
            getattr(ally, 'fortified', False)
            and not getattr(ally, 'artillery', False)
        )

        # Attack coordination: skip fortified non-artillery
        if not is_fortified_non_artillery:
            total_atk += 0.03 * scale

        # Defense coordination: all eligible allies contribute
        total_def += 0.05 * scale

    return (total_atk, total_def)
```

### Transient Fields (marshal.py)

```python
self.coordination_attack_bonus: float = 0.0
self.coordination_defense_bonus: float = 0.0
```

---

## 4. Dedicated Coordination Bonus

### Definition

A flat +5% attack / +5% defense bonus representing marshals who have committed to operating together. Two paths to earn it — same mechanical bonus, different trigger:

### Path A — Co-Location Duration (Both Player and AI)

Two same-nation marshals co-located for **2 consecutive turns** automatically earn the bonus. No command needed. No AP cost. The cost is opportunity — that marshal spent 2 turns in one place instead of elsewhere.

### Path B — SUPPORT Strategic Order (Player Only, Immediate)

The SUPPORT strategic order grants the bonus **immediately** at co-location (turn 0). The 2 AP buys the ramp-up time. In a fast-moving battle, SUPPORT is worth the AP. In a static defensive position, wait 2 turns and save the AP.

### Architectural Note — AI Cannot Use Strategic Commands

The AI's architecture is fundamentally different from the player's:

```
PLAYER: Natural language → parser → _execute_strategic_command() → StrategicOrder
AI:     Priority tree → _evaluate_marshal() → _execute_action() → executor.execute()
```

The AI never touches the parser. Strategic commands (`SUPPORT`, `HOLD`, `MOVE_TO`, `PURSUE`) go through `executor._execute_strategic_command()`, triggered by the parser detecting strategic intent. The AI sends only immediate tactical actions (`attack`, `move`, `defend`, `fortify`, `drill`, `wait`, `stance_change`, `recruit`). The co-location duration path IS the Building Blocks equivalent for AI. This is correct and intentional.

### Tracking

New persistent field on Marshal:

```python
# marshal.py __init__
self.co_location_turns: Dict[str, int] = {}  # ally_name -> first turn of current streak
```

**Serialization required:**
```python
# to_dict():
"co_location_turns": self.co_location_turns.copy(),

# from_dict():
marshal.co_location_turns = data.get("co_location_turns", {})
```

### Per-Turn Update

In `world_state.py _process_tactical_states()` or new helper called from `advance_turn()`:

```python
def _update_co_location_tracking(self):
    """Update co-location turn counters for dedicated coordination bonus."""
    for marshal in self.marshals.values():
        if marshal.strength <= 0:
            marshal.co_location_turns = {}
            continue

        allies_here = {
            m.name for m in self.marshals.values()
            if m.location == marshal.location
            and m.nation == marshal.nation
            and m.name != marshal.name
            and m.strength > 0
            and not getattr(m, 'broken', False)
        }

        # Remove allies no longer co-located
        for name in list(marshal.co_location_turns.keys()):
            if name not in allies_here:
                del marshal.co_location_turns[name]

        # Add new co-located allies (start counting from this turn)
        for ally_name in allies_here:
            if ally_name not in marshal.co_location_turns:
                marshal.co_location_turns[ally_name] = self.current_turn
```

### Bonus Check (in coordination context calculation)

```python
def _has_dedicated_support(self, marshal, same_region_allies, world) -> bool:
    """Check if marshal qualifies for +5%/+5% dedicated coordination bonus."""
    # Path A: Co-location duration (2+ turns with any ally here)
    for ally in same_region_allies:
        start_turn = marshal.co_location_turns.get(ally.name)
        if start_turn is not None and world.current_turn - start_turn >= 2:
            return True

    # Path B: Active SUPPORT order targeting this marshal (immediate)
    for ally in same_region_allies:
        order = getattr(ally, 'strategic_order', None)
        if (order
                and order.command_type == "SUPPORT"
                and order.target == marshal.name):
            return True

    return False
```

### Self-Balancing

Hostile marshals co-located 2 turns get +5% dedicated bonus but 0% coordination scaling from each other. Total benefit: only +5% from dedicated, nothing from per-ally coordination. No special-casing needed — the relationship system handles it.

### Transient Field

```python
self.dedicated_coordination_bonus: float = 0.0  # Set to 0.05 when earned
```

---

## 5. Adjacent Support Bonus

### Definition

+2% attack per adjacent friendly marshal. Represents positional pressure from nearby forces without requiring co-location.

### Rules

- NOT relationship-scaled (purely positional).
- Calculated BEFORE reinforcement checks run.
- Marshals who arrive via reinforcement: **convert** from adjacent (+2%) to same-region (full coordination). Never both.
- Marshals who fail to arrive: **remain** in adjacent count (+2%).
- Same eligibility filters as coordination (not broken, not retreating, not recovering).
- Fortified and HOLD marshals contribute adjacent support (they're physically present in adjacent region even if dug in).

### Implementation Order in _execute_attack

```
1. Count adjacent friendly marshals → adjacent_support = count * 0.02
2. Run reinforcement checks (§7)
3. Arriving marshals: remove from adjacent count, add to same-region allies
4. Recalculate: adjacent_support = remaining_adjacent_count * 0.02
5. Calculate same-region coordination (§3) with updated ally list
```

### Transient Field

```python
self.adjacent_support_bonus: float = 0.0
```

---

## 6. SUPPORT Strategic Objection

### Already Implemented

Strategic objections to SUPPORT, HOLD, PURSUE, MOVE_TO are implemented in V2a Phase M. See `OBJECTION_V2.md` and `SYSTEMS_REFERENCE.md` §4 Strategic Commands.

What exists:
- `_execute_strategic_command()` calls `evaluate_strategic_situation()`
- Uses `world.pending_strategic_objection` (separate from tactical `world.pending_objection`)
- Cautious marshals object to SUPPORT through danger (path crosses enemy territory) — severity 0.65
- Full trust/insist/compromise wired

### Phase 7 Additions — Verify and Add If Missing

Check `objection_v2.py` `evaluate_strategic_situation()` for these triggers:

| Personality | Trigger | Severity | Message | Compromise |
|-------------|---------|----------|---------|------------|
| Aggressive (Ney) | Defensive SUPPORT (target is fortified/cautious/retreating ally) | 0.55 (Major) | "You want me to nursemaid Davout?!" | Offensive SUPPORT if enemy adjacent to target |
| Aggressive (Ney) | Offensive SUPPORT (target is attacking/aggressive ally) | No objection | N/A — he wants to fight | N/A |
| Cautious (Davout) | SUPPORT of reckless ally (target is aggressive + recklessness >= 2) | 0.50 (Major) | "Supporting Ney's recklessness risks us both." | Timed SUPPORT (3 turns) |

If these triggers are already present in the existing `evaluate_strategic_situation()`, document and move on. If missing, add them using the existing trigger pattern.

---

## 7. Adjacent Reinforcement

### Definition

Adjacent marshals can physically move to the battle region and participate BEFORE combat resolves.

### Arrival Score Formula

```python
def calculate_reinforcement_score(reinforcing_marshal, primary_combatant, world):
    """Deterministic base + small random variance."""
    base = 50
    logistics = reinforcing_marshal.skills.get("logistics", 5)
    logistics_bonus = logistics * 5

    rel = reinforcing_marshal.get_relationship(primary_combatant.name)
    RELATIONSHIP_MOD = {-2: -20, -1: -10, 0: 0, 1: +10, 2: +20}
    rel_mod = RELATIONSHIP_MOD.get(rel, 0)

    # Terrain of DEPARTING region (how hard is it to march out)
    departing_region = world.get_region(reinforcing_marshal.location)
    terrain = departing_region.terrain if departing_region else "plains"
    TERRAIN_PENALTY = {
        "plains": 0, "forest": -10, "hills": -5,
        "mountains": -20, "urban": 0, "river_crossing": -5
    }
    terrain_mod = TERRAIN_PENALTY.get(terrain, 0)

    # Personality modifier
    PERSONALITY_MOD = {
        "aggressive": +5,   # Wants to fight — charges toward cannon fire
        "cautious": -5,     # Cautious about rushing in
        "literal": 0,       # Handled by Grouchy Rule — never reaches here
        "balanced": 0,
        "loyal": +3,        # Follows the call of duty
    }
    personality_mod = PERSONALITY_MOD.get(reinforcing_marshal.personality, 0)

    # SUPPORT order targeting combatant: +10 (standing readiness)
    support_bonus = 0
    order = getattr(reinforcing_marshal, 'strategic_order', None)
    if (order
            and order.command_type == "SUPPORT"
            and order.target == primary_combatant.name):
        support_bonus = 10

    # Random variance: ±8
    variance = random.randint(-8, 8)

    score = base + logistics_bonus + rel_mod + terrain_mod + personality_mod + support_bonus + variance
    return score

# Threshold: score > 60 → arrives
```

### The Grouchy Rule (Most Important Mechanic in This Spec)

**Check personality BEFORE calculating arrival score.** If the marshal is Literal AND has no active SUPPORT order targeting the combatant AND has no PURSUE order targeting the same battle: skip arrival score entirely. Log failure with personality message.

```python
# In _calculate_reinforcements():
for candidate in adjacent_friendly_marshals:
    # ═══ THE GROUCHY RULE ═══
    if candidate.personality == "literal":
        has_relevant_order = False
        order = getattr(candidate, 'strategic_order', None)
        if order:
            if (order.command_type == "SUPPORT"
                    and order.target == primary_combatant.name):
                has_relevant_order = True
            elif (order.command_type == "PURSUE"
                    and order.target == defender.name):  # or attacker for defense
                has_relevant_order = True

        if not has_relevant_order:
            reinforcement_results.append({
                "marshal": candidate.name,
                "arrived": False,
                "reason": "literal_personality",
                "score": None,
                "message": (
                    f"{candidate.name} continues to follow standing orders. "
                    f"The sound of cannon fire grows louder behind him."
                )
            })
            continue

    # ═══ NORMAL ARRIVAL CHECK ═══
    score = calculate_reinforcement_score(candidate, primary_combatant, world)
    arrived = score > 60
    # ...
```

**Player counter:** Issue "Grouchy, support Ney" → SUPPORT order overrides Literal personality.

**AI Literal marshals:** Same rule. AI may choose not to spend actions positioning Literal marshals for SUPPORT, making them unreliable reinforcers. Thematically perfect.

### Reinforcement Eligibility

A marshal can reinforce if ALL of:
1. Same nation as primary combatant
2. In an adjacent region (at START of attack — chain reinforcement excluded)
3. `strength > 0`
4. NOT `broken`
5. NOT `retreated_this_turn`
6. `retreat_recovery == 0`
7. NOT `fortified` (dug in, can't march)
8. NOT on HOLD strategic order (`holding_position == True`)
9. NOT currently engaged (no enemy in their region)
10. NOT `drilling` or `drilling_locked`
11. NOT `reinforced_this_turn` (already reinforced another battle)

### Reinforcement Into Enemy Territory

Exception to normal movement rules. Skip territory control check from `_execute_move()`. The marshal enters to **fight**, not occupy. Territory control is determined by the battle outcome normally. The existing eligibility filters (above) handle all important restrictions.

Building Blocks: AI adjacent allies reinforce into player-controlled regions on identical terms.

### After Battle

- **Battle won:** Reinforcing marshal stays in the new region.
- **Battle lost + forced retreat:** Reinforcing marshal retreats WITH the primary combatant. Same retreat logic, same region selection.
- **Reinforcing marshal state:** `reinforced_this_turn = True` (prevents further orders this turn). Transient, cleared at turn start.

### Chain Reinforcement — EXCLUDED

Only marshals adjacent at the START of the attack get reinforcement checks. If Blucher reinforces Wellington (moving from Netherlands to Waterloo), Gneisenau (adjacent to Netherlands) does NOT get a secondary reinforcement check for the same battle.

### Inline-Dramatic Display

Reinforcement arrival/failure uses highlighted inline blocks in terminal output. NOT a popup dialog. Non-dismissable. Visually impossible to miss.

**Arrival (personality-flavored):**
```
┌─────────────────────────────────────────────────┐
│  REINFORCEMENT: Blucher arrives!                 │
│  "Marshal Forward" crashes through the tree      │
│  line with 55,000 Prussians.                     │
│  Devoted to Wellington: +20 arrival bonus        │
│  Combined arms: Infantry + Infantry (unchanged)  │
└─────────────────────────────────────────────────┘
```

**Failure — Grouchy Rule (gold border):**
```
┌─────────────────────────────────────────────────┐
│  GROUCHY CONTINUES EAST                          │
│  The marshal can hear the guns from Waterloo.    │
│  His orders are clear. He continues his march    │
│  as instructed.                                  │
│  [Literal personality: SUPPORT order required     │
│   to reinforce]                                  │
└─────────────────────────────────────────────────┘
```

**Failure — Low Score:**
```
┌─────────────────────────────────────────────────┐
│  Gneisenau fails to arrive                       │
│  The forest roads defeated even Gneisenau's      │
│  meticulous planning. Score: 58 (needed >60)     │
│  Logistics 9, Friendly +10, Forest -10           │
└─────────────────────────────────────────────────┘
```

### Coordination Failure Consequences

When a non-Literal, non-Hostile adjacent marshal **fails** arrival (low score, not personality refusal):
- Trust -3 on the failing marshal ("failed to march to the guns")

Exceptions (no penalty):
- Hostile refusals: principle-based, no penalty
- Literal non-arrivals: followed orders correctly, no penalty
- Fortified/HOLD marshals: not eligible, no check, no penalty

---

## 8. Casualty Distribution

### 2 Tiers Only

| Tier | Who | Share |
|------|-----|-------|
| **Participating** | All same-nation marshals in region at time of combat. Proportional by strength fraction. | Full proportional |
| **Non-Participating** | Hostile marshals (0% coordination scaling = refused to fight). | 0% — takes no casualties |

### Rules

- Adjacent reinforcements who ARRIVE = PARTICIPATING (they're physically in the region).
- Adjacent reinforcements who FAIL = not in region. 0% casualties.
- Primary combatant takes no extra share — already absorbs brunt through `resolve_battle()`.
- Hostile marshals in the region: dead weight. 0% coordination, 0% casualties, but eat supply.

### Implementation — resolve_battle Contract Change

**This is the highest-risk change in the spec.**

Add `apply_casualties: bool = True` parameter to `resolve_battle()`:

```python
def resolve_battle(
    self,
    attacker: Marshal,
    defender: Marshal,
    terrain: str = "open",
    flanking_bonus: int = 0,
    flanking_message: str = None,
    glorious_charge: bool = False,
    fortification_bonus: float = 0.0,
    apply_casualties: bool = True,  # NEW
) -> Dict:
```

When `apply_casualties=False`:
- Calculate casualties normally (all modifier math unchanged).
- Return `attacker_raw_casualties` and `defender_raw_casualties` in result dict.
- Do NOT modify `attacker.strength` or `defender.strength`.
- Do NOT trigger forced retreat or broken state.
- Caller is responsible for distributing and applying casualties.

**Call site audit (5 resolve_battle calls in executor.py + 1 charge):**

| Call Site | Location | Action Needed |
|-----------|----------|---------------|
| `_execute_attack` main battle | ~line 3211 | Change to `apply_casualties=False` when coordination active. Distribute after. |
| Sally attack 1 (HOLD aggressive) | ~line 5457 | Keep `apply_casualties=True`. Sally is single-marshal combat. |
| Sally attack 2 (cautious nearest) | ~line 5608 | Keep `apply_casualties=True`. Single-marshal. |
| Sally attack 3 (literal nearest) | ~line 5744 | Keep `apply_casualties=True`. Single-marshal. |
| Glorious Charge | ~line 8513 | Keep `apply_casualties=True`. Single-marshal charge. |
| Garrison combat | `_resolve_garrison_combat` | N/A — uses region property, not Marshal. |

**Only `_execute_attack` changes.** All other call sites are single-marshal combat and keep `apply_casualties=True`.

### Casualty Distribution Logic

```python
def _distribute_casualties(self, raw_casualties: int, participants: list[Marshal],
                           excluded_hostile: list[Marshal]) -> dict:
    """Distribute casualties proportionally among participating marshals."""
    if not participants:
        return {}

    total_strength = sum(m.strength for m in participants)
    if total_strength <= 0:
        return {}

    distribution = {}
    remaining = raw_casualties

    for i, marshal in enumerate(participants):
        if i == len(participants) - 1:
            # Last marshal gets remainder (avoids rounding errors)
            share = remaining
        else:
            fraction = marshal.strength / total_strength
            share = int(raw_casualties * fraction)
            remaining -= share

        share = min(share, marshal.strength)  # Can't lose more than you have
        marshal.strength = max(0, marshal.strength - share)
        distribution[marshal.name] = share

    return distribution
```

---

## 9. Win/Loss Relationship Formula

### Trigger

After `resolve_battle()` with 2+ same-nation marshals participating (via same-region coordination, SUPPORT, or reinforcement arrival). Each **pair** gets an independent check.

### Severity Definition

```python
def calculate_battle_severity(winner_casualties, loser_casualties):
    """Decisive / standard / narrow based on casualty exchange ratio."""
    if loser_casualties <= 0:
        return "decisive"
    ratio = winner_casualties / max(loser_casualties, 1)
    if ratio < 0.5:
        return "decisive"   # Winner took less than half loser's casualties
    elif ratio > 0.8:
        return "narrow"     # Close fight, nearly even
    else:
        return "standard"
```

### WIN Formula

```
score = BASE(30) + severity_bonus + rel_modifier + variance(±10)

severity_bonus:  decisive +15, standard 0, narrow -10
rel_modifier:    Hostile -20, Rival 0, Professional 0, Friendly -10, Devoted -20
variance:        random.randint(-10, 10)

Threshold: score > 50 → relationship improves +1
```

### LOSS Formula

```
score = BASE(15) + severity_bonus + rel_modifier + variance(±10)

severity_bonus:  decisive +10, standard 0, narrow -5
rel_modifier:    Hostile +15, Rival +5, Professional 0, Friendly 0, Devoted 0
variance:        random.randint(-10, 10)

Threshold: score > 50 → relationship degrades -1
```

### Asymmetry (Intentional)

Winning together builds bonds faster than losing destroys them. Decisive wins with Rivals sometimes improve (+15 + 0 ± 10 = 35-55 → ~30% chance). Hostile marshals almost never improve from wins (30 + 15 - 20 ± 10 = 15-35 → never). Losing together rarely degrades Professional+ relationships (15 + 0 + 0 ± 10 = 5-25 → never reaches 50).

### Caps

- ±1 per battle maximum.
- ±1 per 3 turns cooldown (track `last_relationship_change_turn: Dict[str, int]` per marshal). New serialized field.
- Existing [-2, +2] range cap remains.

### Rivalry Resolved — IN PHASE 7 (Not Deferred)

When Rival marshals fight together and win, the formula above handles it naturally. Decisive win: ~30% chance to improve to Professional. This is the highest narrative payoff of the relationship system at minimal implementation cost — the data is already computed in the coordination context.

### REPLACES Original §4 SUPPORT Relationship Effects

The original spec had 4 separate probabilistic systems for SUPPORT relationship changes (hostile degradation timer, rival improvement, friendly improvement, shared defeat). **All replaced** by this unified formula. SUPPORT marshals participate in the same battle → same formula. No separate SUPPORT relationship code.

### Implementation

```python
def check_shared_battle_relationship(marshal_a, marshal_b, battle_result, won: bool, world):
    """Check if shared battle changes relationship. Returns int change (-1, 0, +1)."""
    current_rel = marshal_a.get_relationship(marshal_b.name)

    # Cooldown check
    last_change = getattr(marshal_a, 'last_relationship_change_turn', {})
    last_turn = last_change.get(marshal_b.name, -99)
    if world.current_turn - last_turn < 3:
        return 0

    winner_cas = battle_result.get("attacker_casualties", 0)
    loser_cas = battle_result.get("defender_casualties", 0)
    # Swap if defender won
    if battle_result.get("victor") == battle_result.get("defender", {}).get("name"):
        winner_cas, loser_cas = loser_cas, winner_cas

    severity = calculate_battle_severity(winner_cas, loser_cas)

    if won:
        base = 30
        sev_bonus = {"decisive": 15, "standard": 0, "narrow": -10}[severity]
        rel_mod = {-2: -20, -1: 0, 0: 0, 1: -10, 2: -20}[current_rel]
    else:
        base = 15
        sev_bonus = {"decisive": 10, "standard": 0, "narrow": -5}[severity]
        rel_mod = {-2: 15, -1: 5, 0: 0, 1: 0, 2: 0}[current_rel]

    variance = random.randint(-10, 10)
    score = base + sev_bonus + rel_mod + variance

    if score > 50:
        change = 1 if won else -1
        marshal_a.modify_relationship(marshal_b.name, change)
        # Record cooldown
        if not hasattr(marshal_a, 'last_relationship_change_turn'):
            marshal_a.last_relationship_change_turn = {}
        marshal_a.last_relationship_change_turn[marshal_b.name] = world.current_turn
        return change

    return 0
```

### New Serialized Field

```python
# marshal.py __init__
self.last_relationship_change_turn: Dict[str, int] = {}

# to_dict():
"last_relationship_change_turn": self.last_relationship_change_turn.copy(),

# from_dict():
marshal.last_relationship_change_turn = data.get("last_relationship_change_turn", {})
```

---

## 10. AI Enhancements

### P4.6: Coordinated Attack Setup (NEW — between P4.5 and P4.75)

```python
def _find_coordinated_attack(self, marshal, nation, world):
    """Find opportunity for 2-marshal pincer attack."""
    # Never fires over undefended capture (P4.5 wins priority)

    allies = [
        m for m in world.marshals.values()
        if m.nation == nation
        and m.name != marshal.name
        and m.strength > 0
        and not getattr(m, 'broken', False)
        and marshal.get_relationship(m.name) >= -1  # Rival or better
    ]

    for ally in allies:
        # Find enemy reachable by both within 2 moves
        for enemy in world.marshals.values():
            if enemy.nation == nation or enemy.strength <= 0:
                continue

            my_dist = world.get_distance(marshal.location, enemy.location)
            ally_dist = world.get_distance(ally.location, enemy.location)

            if my_dist > 2 or ally_dist > 2:
                continue

            combined = marshal.strength + ally.strength
            solo_ratio = marshal.strength / max(enemy.strength, 1)
            combined_ratio = combined / max(enemy.strength, 1)

            # Only coordinate when combined gives 1.5:1 but solo doesn't
            if combined_ratio >= 1.5 and solo_ratio < 1.5:
                # Move toward enemy (staging position)
                if my_dist > 1:
                    path = world.find_path(marshal.location, enemy.location)
                    if path and len(path) > 1:
                        return {"marshal": marshal.name, "action": "move", "target": path[1]}

    return None
```

### P4.75 Modification: Relationship-Aware Ally Support

Modify existing `_find_ally_support_opportunity()`:

```python
# After checking ally needs support, BEFORE deciding to move:
rel = marshal.get_relationship(ally.name)
if rel == -2:  # Hostile — won't support
    continue

# Score allies by relationship — Devoted allies get priority
# (sort allies by relationship descending before the loop)
allies.sort(key=lambda a: marshal.get_relationship(a.name), reverse=True)
```

Wellington and Blucher are Devoted (+2). Each PRIORITIZES supporting the other when threatened.

### P4.76: Co-Location Persistence (NEW — after P4.75)

```python
def _should_maintain_co_location(self, marshal, nation, world):
    """Stay co-located with ally to earn dedicated coordination bonus."""
    for ally in world.marshals.values():
        if (ally.nation == nation
                and ally.name != marshal.name
                and ally.location == marshal.location
                and ally.strength > 0
                and marshal.get_relationship(ally.name) >= -1):  # Rival or better

            # Check if ally is threatened
            ally_region = world.get_region(ally.location)
            if not ally_region:
                continue
            enemies_near = any(
                e.location in ally_region.adjacent_regions or e.location == ally.location
                for e in world.marshals.values()
                if e.nation != nation and e.strength > 0
            )

            if enemies_near:
                # Co-located 1+ turn with threatened ally: STAY
                start = marshal.co_location_turns.get(ally.name)
                if start is not None and world.current_turn - start >= 1:
                    return True  # Stay for dedicated bonus next turn

    return False
```

This returns `True` to signal the AI should NOT move this marshal. Integrated into priority chain as a guard before P7 strategic movement.

### P4.77: Cross-Nation Adjacency Awareness (NEW)

In `_consider_strategic_move()`, add scoring for allied nation marshal proximity:

```python
# When evaluating candidate regions for strategic movement:
for ally in world.marshals.values():
    if (ally.nation != nation
            and ally.nation != world.player_nation  # Same side
            and ally.strength > 0):
        rel = marshal.get_relationship(ally.name)
        if rel >= 1:  # Friendly or Devoted
            if ally.location in candidate_region.adjacent_regions:
                score += rel * 3  # Devoted=+6, Friendly=+3
```

Wellington and Blucher independently decide to stay near each other via Devoted relationship. No cross-nation coordination needed — emergent from individual decisions.

### P4.78: Defensive Reinforcement Positioning (NEW — priority ~91.5, lowest)

```python
def _find_defensive_reinforcement_position(self, marshal, nation, world):
    """Position adjacent to threatened ally for reinforcement readiness."""
    for ally in world.marshals.values():
        if ally.nation != marshal.nation or ally.name == marshal.name:
            continue
        if ally.strength <= 0 or getattr(ally, 'broken', False):
            continue

        rel = marshal.get_relationship(ally.name)
        if rel < 0:  # Rival or worse — won't position for them
            continue

        ally_region = world.get_region(ally.location)
        if not ally_region:
            continue

        # Ally threatened?
        enemies_near = any(
            e.location in ally_region.adjacent_regions or e.location == ally.location
            for e in world.marshals.values()
            if e.nation == world.player_nation and e.strength > 0
        )
        if not enemies_near:
            continue

        # Already adjacent? Stay.
        if ally.location in world.get_region(marshal.location).adjacent_regions:
            return None

        # Can get adjacent in 1 move?
        for adj in ally_region.adjacent_regions:
            if world.get_distance(marshal.location, adj) <= marshal.movement_range:
                return {"marshal": marshal.name, "action": "move", "target": adj}

    return None
```

**Defer if scope pressure:** This is the lowest-priority AI enhancement. Cut if behind schedule.

### AI Coordination Estimate

When AI evaluates enemy defensive coordination, use **+8% per ally** (not +5%). Closer to realistic without making AI passive.

### AI Combined Arms Awareness

In P7 strategic movement, prefer destinations that complete unit type combinations:

```python
# Score candidate regions by combined arms potential
allies_at_dest = [m for m in world.marshals.values()
                  if m.location == candidate and m.nation == nation and m.strength > 0]
types_at_dest = set()
for a in allies_at_dest:
    types_at_dest.add('artillery' if getattr(a, 'artillery', False) else
                      'cavalry' if getattr(a, 'cavalry', False) else 'infantry')
# Add this marshal's type
my_type = 'artillery' if getattr(marshal, 'artillery', False) else \
          'cavalry' if getattr(marshal, 'cavalry', False) else 'infantry'
types_with_me = types_at_dest | {my_type}
# Score: 3 types = +10, 2 types (was 1) = +5
if len(types_with_me) > len(types_at_dest):
    score += 5 * (len(types_with_me) - len(types_at_dest))
```

### AI Ney-Davout Rule

AI never coordinates Ney and Davout. Their Hostile relationship means:
- 0% coordination bonus
- Ney will never reinforce Davout (Hostile → score base 50 + logistics - 20 = always fails)
- P4.75 filtered by `rel == -2` check → never moves to support Hostile marshal

### Gneisenau Staff Work

No special ability for Waterloo scenario. Deferred to 1805 full campaign. Greyed-out tooltip: "Staff Work — activates in full campaign."

---

## 11. Coordination Preview & Battle Reports

### Pre-Battle Coordination Preview

Shown **BEFORE** the player commits — inline terminal text, informational only.

**Timing in _execute_attack flow:**
```
validate → objection check → objection resolution → COORDINATION PREVIEW → resolve_battle
```

The preview calculates what bonuses will apply IF the player attacks:

```
═══ COORDINATION PREVIEW ═══
Combined Arms: Infantry + Cavalry (2/3) → +10% atk, +5% def
Coordination: Davout (+1.5% atk, +2.5% def — Rival)
Dedicated: YES (+5%/+5% — co-located 3 turns)
Adjacent: Drouot (1 region away, 72% reinforcement)
TOTAL ESTIMATED: +18.5% atk, +12.5% def
Cap applied: +18.5% atk (under +25% cap)
═══════════════════════════
```

Same-region only — no adjacent estimates in preview (those are in tooltip). The preview shows what IS guaranteed, not what MIGHT happen via reinforcement.

### Battle Report Integration

Expandable section in terminal output. NOT a separate screen.

**Collapsed (default):**
```
═══════════════════════════════════════
  BATTLE: Ney attacks Wellington
═══════════════════════════════════════
  RESULT: VICTORY — Wellington retreats!
  Casualties: Ney 3,200 / Wellington 5,800
  Combined Arms: Infantry + Cavalry (+10% atk)
  Coordination: Davout (+1.5% atk, Rival)
  Reinforcement: Blucher arrived! (+4.5% def for Wellington)
  [DETAIL] for full breakdown
═══════════════════════════════════════
```

**Expanded (button click in Godot):**
```
  ── MODIFIER BREAKDOWN ──
  Ney (attacker):
    Stance: Aggressive (+15%)
    Personality: +15% base attack
    Combined Arms: +10% (infantry + cavalry, 2/3)
    Coordination: +1.5% (Davout, Rival ×0.5)
    Dedicated: +5% (co-located 3 turns)
    Adjacent: +2% (Drouot, failed to arrive)
    TOTAL: ×1.49

  Wellington (defender):
    Stance: Defensive (+15%)
    Fortification: +12%
    Coordination: +7.5% (Blucher, Devoted ×1.5)
    Combined Arms: +5% (infantry + infantry, 1/3)
    TOTAL: ×1.40

  ── CASUALTY DISTRIBUTION ──
    Ney: 2,400 (primary)
    Davout: 800 (proportional)

  ── REINFORCEMENT ──
    Blucher: ARRIVED (score 92, threshold 60)
      Logistics 5 (+25), Devoted (+20), Plains (+0), Aggressive (+5)
    Drouot: FAILED (score 54, threshold 60)
      Logistics 4 (+20), Professional (+0), Forest (-10), Cautious (-5)

  ── BERTHIER'S OBSERVATION ──
  "Our combined arms proved decisive, Sire, though Davout's
   coordination was... reluctant."
```

### Berthier Observation Categories

Add to existing `battle_report.py` observation priorities:

| Priority | Category | Condition |
|----------|----------|-----------|
| P0.5 | `coordination_full_triangle` | All 3 unit types present |
| P0.7 | `coordination_reinforcement_arrival` | Any reinforcement arrived |
| P0.8 | `coordination_reinforcement_failure` | Any reinforcement failed (especially Grouchy) |
| P12 | `coordination_hostile_refused` | Hostile ally provided 0% coordination |
| P13 | `coordination_devoted_synergy` | Devoted ally provided 150% coordination |

These insert into the existing priority chain. P0.5-P0.8 fire BEFORE other observations (coordination is the big story). P12-P13 fire as fallback alternatives to default.

---

## 12. Godot UI: Tooltips, Readiness, Display

### Defensive Readiness Tooltip

When hovering a region with 2+ friendly marshals:

```
═══ RHINE ═══
Terrain: Hills (+15% def)
Control: France
Supply: 35,000 / 40,000

MARSHALS:
  Ney (Cavalry) — 25,000 | Morale 78%
  Davout (Infantry) — 30,000 | Morale 85%

COORDINATION READINESS:
  Combined Arms: 2/3 (Infantry + Cavalry) → +10% atk, +5% def
  Coordination: Ney↔Davout (Hostile) → +0% mutual
  Dedicated: Not yet (co-located 1 turn, need 2)
  Total if attacking: +10% atk
  Total if defending: +5% def

ADJACENT REINFORCEMENT:
  Drouot (Artillery, 1 region away)
    ● 72% arrival — Log 4, Professional, Hills -5
    Would complete triangle → +20% atk, +10% def
```

### Color coding

- Hostile/Rival: red
- Professional: white/default
- Friendly/Devoted: gold
- Reinforcement probability: green >80%, yellow 40-80%, red <40%

### Enemy Region (PARTIAL+ visibility)

```
═══ WATERLOO ═══
Terrain: Plains
Control: Britain

ENEMY FORCES:
  Wellington (Infantry, ~65k)
  Blucher (Infantry, ~55k)

EST. COORDINATION:
  Likely strong (Devoted pair)
  Combined Arms: 1/3 (Infantry only)
```

### Relationship Display in Marshal Tooltip

Add to existing marshal tooltip (below unit type, trust):

```
  Relationships:
    Davout: Hostile (-2) [red]
    Grouchy: Professional (0)
    Drouot: Professional (0)
```

### First-Time Coordination Tutorial (Inline-Dramatic)

Fires ONCE per campaign: the first time combined arms bonuses apply in any battle. Displayed as an inline-dramatic gold border block in terminal output, NOT a popup dialog (zero new popup types).

```
┌─────────────────────────────────────────────────┐
│  BERTHIER'S REPORT                               │
│                                                  │
│  "Sire, our marshals fight as one corps for the  │
│  first time! The combined arms of infantry and   │
│  cavalry proved decisive."                       │
│                                                  │
│  Position different unit types together for       │
│  combined arms bonuses. Coordination improves     │
│  with strong relationships between marshals.      │
└─────────────────────────────────────────────────┘
```

Track with `coordination_tutorial_shown: bool` on WorldState (serialized). Check before displaying inline-dramatic block.

---

## 13. Supply Interaction

### No New Supply Code Required

The existing supply system already punishes stacking. From `world_state.py:process_supply_attrition()`:

```python
total = sum(m.strength for m in marshals_here)
base_cap = region.supply_capacity
# Per-marshal attrition based on total excess
```

When 3 marshals (90k total) sit in a 40k capacity region, `excess_ratio = 125%`, all three take 5% attrition per turn. This IS the natural limiter on coordination stacking.

### Reinforcement and Supply

A reinforcing marshal joins the region and dilutes the supply pool for that turn's attrition check. This is natural — more troops, more supply strain. No exemption needed.

### Home Territory Bonus

Existing 1.5x supply capacity on home territory applies normally to coordinated stacks. Defending at home is more sustainable than attacking abroad.

---

## 14. Popup & Information Architecture

### The Rule

A coordination event gets a popup IF AND ONLY IF it requires a player **DECISION** or represents a **DRAMATIC TURNING POINT** worth interrupting for. Everything else is inline.

### Classification

| Event | Display Type | Justification |
|-------|-------------|---------------|
| SUPPORT objection (Hostile/Rival) | **REAL POPUP** (existing objection system) | Player must decide trust/insist/compromise |
| First-time coordination tutorial | **INLINE-DRAMATIC** (once per campaign, gold border) | Teaching moment, fires once. No decision needed → not a popup. |
| Reinforcement arrival (Blucher arrives) | **INLINE-DRAMATIC** (gold border block in terminal) | Dramatic but no decision needed |
| Reinforcement failure (Grouchy continues east) | **INLINE-DRAMATIC** (gold border block in terminal) | The game's signature moment |
| Coordination bonuses applied | INLINE TERMINAL TEXT | Math, not drama |
| Combined arms bonus | INLINE TERMINAL TEXT | One-line summary |
| Casualty distribution | INLINE TERMINAL TEXT | Numbers in battle result |
| Pre-battle coordination preview | INLINE TERMINAL TEXT | Informational, before battle |
| Adjacent support bonus | INLINE TERMINAL TEXT | One-line note |
| AI coordination observed | END-OF-TURN DIALOG (existing enemy phase) | One line in consolidated dialog |
| Relationship change | END-OF-TURN SUMMARY | One line: "Davout's opinion improved" |
| Supply warnings (stacking) | END-OF-TURN SUMMARY | One line if relevant |
| Detailed coordination math | LOG ONLY (campaign log) | For curious players |
| Co-location tracking updates | SILENT | Internal bookkeeping |
| AI positioning decisions | SILENT | Internal |

### Total New Popup Types: 0

Zero new dialog popups. The first-time coordination tutorial uses inline-dramatic (gold border block), not a popup — it requires no decision. All coordination information rides existing display channels. The only popup-producing events are SUPPORT objections, which use the existing V2a objection system.

---

## 15. Implementation Sessions

### Session 57: Combined Arms Detection

**Goal:** Detect unit type diversity in regions, apply bonuses through transient fields.

**Files:**
- `marshal.py` — Add transient fields: `combined_arms_attack_bonus`, `combined_arms_defense_bonus`. Add to `get_attack_modifier()` and `get_defense_modifier()` via `getattr`.
- `executor.py` — New `_calculate_coordination_context()` method (combined arms portion only). Call from `_execute_attack()` BEFORE `resolve_battle()`.
- `combat.py` — Add combined arms message to `tactical_prefix` (read-only, no recalculation).
- `battle_report.py` — Add combined arms to snapshot.

**Tests (~35):**
- 1/3, 2/3, 3/3 unit type detection
- Broken/retreating/recovering exclusion
- Garrison detachment exclusion
- Fortified marshals still count for type
- Bonus values correct
- Transient fields reset after combat
- Modifier integration (attack and defense)
- Both sides get independent combined arms
- Snapshot captures combined arms

**Godot Smoke Test:** `curl` attack with 2 marshals same region, verify combined arms message in response.

---

### Session 58: Coordination Bonus + Hard Cap

**Goal:** Per-ally relationship-scaled coordination. Hard cap on total coordination.

**Files:**
- `marshal.py` — Add transient fields: `coordination_attack_bonus`, `coordination_defense_bonus`. Apply in modifier methods.
- `executor.py` — Extend `_calculate_coordination_context()` with per-ally coordination calculation, relationship scaling, hard cap enforcement.

**Tests (~35):**
- Per-ally bonus values at each relationship level (-2 through +2)
- Asymmetric relationships (Ney→Davout vs Davout→Ney)
- Fortified non-artillery excluded from attack coordination
- Fortified artillery contributes both
- Multiple allies stack additively
- Hard cap: +25% attack enforced
- Hard cap: +20% defense enforced
- Cap applies AFTER all sources summed
- Solo marshal = 0 coordination

**Gate:** Combined arms + coordination visible in `curl` attack result.

---

### Session 59: Dedicated Coordination + Co-Location Tracking

**Goal:** +5%/+5% bonus from co-location duration or SUPPORT order. New serialized field.

**Files:**
- `marshal.py` — Add `co_location_turns: Dict[str, int]`, `last_relationship_change_turn: Dict[str, int]`, `dedicated_coordination_bonus` (transient). Serialize both persistent fields.
- `world_state.py` — Add `_update_co_location_tracking()` called from `advance_turn()`.
- `executor.py` — Extend `_calculate_coordination_context()` with dedicated bonus check.

**Tests (~30):**
- Co-location tracking: counter starts, increments, resets on separation
- 2-turn threshold: no bonus at 1 turn, bonus at 2 turns
- SUPPORT order grants immediate bonus (turn 0)
- Serialization round-trip for `co_location_turns`
- Serialization round-trip for `last_relationship_change_turn`
- Dead marshal counter cleared
- Broken marshal counter cleared
- Both paths produce same +5%/+5% value
- `test_serialization_enforcement.py` passes

---

### Session 60: Adjacent Support Bonus

**Goal:** +2% per adjacent friendly marshal, integration with coordination pipeline.

**Files:**
- `marshal.py` — Add `adjacent_support_bonus` transient field. Apply in `get_attack_modifier()`.
- `executor.py` — Extend `_calculate_coordination_context()` with adjacent ally counting. Calculate BEFORE reinforcement checks (Session 61).

**Tests (~20):**
- Adjacent count correct (1, 2, 3 adjacent allies)
- Non-adjacent allies excluded
- Broken/retreating excluded
- HOLD/fortified allies still count (physically present)
- Bonus is +2% per ally, correct value
- NOT relationship-scaled
- Enemy marshals excluded
- Adjacent bonus appears in attack modifier

**Gate:** `curl` attack with adjacent ally shows +2% adjacent bonus in result.

---

### Session 61: Adjacent Reinforcement

**Goal:** The Grouchy Rule. Adjacent marshals physically relocate to battle region.

**HIGHEST RISK SESSION.** Marshal state changes mid-turn. Physical relocation before combat.

**Files:**
- `executor.py` — New `_calculate_reinforcements()` method. The Grouchy Rule (Literal personality check). Arrival score formula. Physical relocation. `reinforced_this_turn` transient flag. Integration into `_execute_attack()` flow.
- `marshal.py` — Add `reinforced_this_turn: bool` (transient, not serialized). Cleared at turn start in `world_state.py`.
- `world_state.py` — Clear `reinforced_this_turn` at turn start.
- `combat.py` — No changes (reinforcement is pre-combat, not mid-combat).

**Tests (~45):**
- Grouchy Rule: Literal personality blocks reinforcement without SUPPORT
- Grouchy Rule: SUPPORT order overrides Literal block
- Grouchy Rule: PURSUE order targeting same battle overrides Literal block
- Arrival score formula: each component (logistics, relationship, terrain, personality, variance, SUPPORT bonus)
- Threshold >60: arrives
- Threshold <=60: fails
- Physical relocation: marshal location changes to battle region
- `reinforced_this_turn` prevents further orders
- Reinforcement into enemy territory: territory control unchanged
- Multiple reinforcements: each checked independently
- Chain reinforcement excluded: only pre-battle adjacency
- Eligibility filters: broken, retreating, fortified, HOLD, engaged, drilling excluded
- Defensive reinforcement: AI attacks player, adjacent ally reinforces
- Reinforcement + retreat: reinforcer retreats with primary if battle lost
- Adjacent → reinforcement conversion: +2% adjacent removed, full coordination added
- Trust -3 on non-Literal, non-Hostile failure
- No trust penalty on Literal or Hostile failures
- Fog of war: reinforcement events visible to player regardless of fog (physical presence)

**Gotcha — fog/event logging:** When reinforcing marshal relocates, fog of war intel must update. `update_intel_from_battle()` already fires after battle — confirm it sees the reinforcer's new position. If the reinforcer was in a different fog zone, their departure reveals intel about the departure region.

**Gotcha — `reinforced_this_turn` and strategic orders:** A marshal with an active strategic order (MOVE_TO, PURSUE) who reinforces a battle has their order disrupted. The reinforcement physically moves them. The strategic order's path is now invalid. After reinforcement, clear the strategic order: `marshal.strategic_order = None`. The marshal is now in a new region and needs new orders.

**Gate:** Godot smoke test with Literal marshal adjacent to battle. Verify inline-dramatic Grouchy message appears.

---

### Session 62: Casualty Distribution

**Goal:** Proportional casualties across participating marshals.

**SECOND HIGHEST RISK SESSION.** Changes `resolve_battle()` contract.

**Files:**
- `combat.py` — Add `apply_casualties: bool = True` parameter. When False, return raw casualties without modifying marshal strength. Do not trigger forced retreat/broken.
- `executor.py` — In `_execute_attack()` only: call with `apply_casualties=False` when coordination active. New `_distribute_casualties()`. Apply casualties, then check forced retreat/broken for each participant.
- Verify all other `resolve_battle()` call sites (5) keep `apply_casualties=True`.

**Tests (~40):**
- `apply_casualties=False`: raw casualties returned, strength unchanged
- `apply_casualties=True`: existing behavior preserved (regression)
- Distribution proportional by strength
- Hostile marshal: 0 casualties
- Reinforcement arrival: participating, takes casualties
- Reinforcement failure: not in region, no casualties
- Total distributed casualties == raw casualties (no rounding leakage)
- Each participant checks broken/retreat independently after distribution
- All 5 other call sites unaffected (regression tests)
- Solo marshal: no distribution (existing behavior)
- Strength can't go below 0

**Call site audit checklist (verify each):**
- [ ] `_execute_attack` main: `apply_casualties=False` when coordinated
- [ ] Sally 1 (HOLD aggressive): `apply_casualties=True` — single marshal
- [ ] Sally 2 (cautious nearest): `apply_casualties=True` — single marshal
- [ ] Sally 3 (literal nearest): `apply_casualties=True` — single marshal
- [ ] Glorious Charge: `apply_casualties=True` — single marshal
- [ ] Garrison combat: N/A (different function)

---

### Session 63: AI Enhancements

**Goal:** P4.6, P4.75 modification, P4.76, P4.77, P4.78, coordination estimates, combined arms awareness.

**Files:**
- `enemy_ai.py` — New `_find_coordinated_attack()` (P4.6), modify `_find_ally_support_opportunity()` (P4.75), new `_should_maintain_co_location()` (P4.76), cross-nation scoring in `_consider_strategic_move()` (P4.77), new `_find_defensive_reinforcement_position()` (P4.78). Update attack threshold estimates (+8% per ally).

**Tests (~35):**
- P4.6: coordinated attack setup fires when combined > 1.5x but solo < 1.5x
- P4.6: doesn't fire over undefended capture
- P4.6: relationship >= Rival required
- P4.75: Hostile marshal excluded from support
- P4.75: Devoted ally prioritized over Professional
- P4.76: stays co-located when ally threatened and been there 1+ turn
- P4.76: doesn't stay if no threat
- P4.77: cross-nation Devoted allies score higher for adjacency
- P4.78: positions adjacent to threatened ally (if reachable)
- P4.78: doesn't move if already adjacent
- AI coordination estimate: +8% per ally in defensive assessment
- Combined arms: AI moves to complete triangle when possible
- Ney-Davout: AI never coordinates them (Hostile filter)
- AI gets same coordination bonuses in battle (Building Blocks)
- AI earns dedicated bonus after 2 turns co-located

---

### Session 64: Win/Loss Relationship Formula

**Goal:** Shared battle → relationship check. Rivalry Resolved.

**Files:**
- `executor.py` — Call `check_shared_battle_relationship()` after coordinated battle resolves.
- New module or function in `marshal.py` / `executor.py` — Formula implementation.
- `marshal.py` — `last_relationship_change_turn` serialization (done in Session 59).

**Tests (~25):**
- WIN decisive + Rival → sometimes improves (~30%)
- WIN standard + Professional → never improves
- WIN decisive + Hostile → never improves
- LOSS decisive + Hostile → sometimes degrades (shared suffering mechanic)
- LOSS narrow + Professional → never degrades
- Cooldown: no change within 3 turns of last change
- Cap: ±1 per battle
- Range cap: can't exceed +2 or go below -2
- Asymmetric: A's relationship with B can change independently of B with A
- Multiple pairs: 3 marshals = 3 pair checks
- Loss degradation rarer than win improvement (asymmetry)
- Serialization of `last_relationship_change_turn`

---

### Session 65: Battle Reports & Berthier Coordination Observations

**Goal:** Coordination info in battle reports, Berthier observations, pre-battle preview.

**Files:**
- `battle_report.py` — New observation categories (P0.5 full triangle, P0.7 reinforcement arrival, P0.8 reinforcement failure, P12 hostile refusal, P13 devoted synergy). Snapshot coordination bonuses.
- `executor.py` — Pre-battle coordination preview (inline terminal text). Reinforcement inline-dramatic messages.
- `combat.py` — Coordination messages in `tactical_prefix`.

**Tests (~25):**
- Observation priority: full triangle wins over individual coordination
- Observation: Grouchy failure has specific template
- Observation: Devoted synergy noted
- Observation: Hostile refusal noted
- Preview: shows combined arms, coordination, estimated adjacent
- Preview: cap shown if applied
- Snapshot: all coordination fields captured
- Messages: combined arms, per-ally coordination, dedicated support

---

### Session 66: Godot UI + Integration Audit + Docs

**Goal:** Tooltips, tutorial inline-dramatic, display formatting, cross-system audit, doc updates.

**Files:**
- `map.gd` — Defensive readiness tooltip, relationship display, reinforcement probability, color coding.
- `main.gd` — Inline-dramatic display for reinforcement. Coordination preview display. Battle report expansion. First-time coordination tutorial (inline-dramatic, once per campaign).
- `world_state.py` — `coordination_tutorial_shown: bool` (serialized).
- `enemy_phase_dialog.gd` — AI coordination observations in enemy phase.
- All docs — Update CLAUDE.md, STATUS.md, ROADMAP.md, SYSTEMS_REFERENCE.md, SAVE_FORMAT_REFERENCE.md, ENEMY_AI_REFERENCE.md.

**Tests (~50):**
- Serialization enforcement: all new fields (co_location_turns, last_relationship_change_turn, coordination_tutorial_shown)
- Full integration: 3-marshal coordinated attack with combined arms, reinforcement, relationship check
- Full integration: defensive coordination with AI attack
- Full integration: Grouchy Rule + SUPPORT override
- Full integration: hostile ally dead weight (0 coordination, 0 casualties, eats supply)
- Full integration: hard cap enforcement at maximum stack
- Full integration: save/load round-trip preserves all coordination state
- Endpoint wiring: all new fields appear in API response
- int() wrapping: all numeric returns to Godot
- Edge case: all marshals in one region (supply attrition check)
- Edge case: artillery-only stack
- Edge case: 4 marshals, all hostile to each other

**Godot Smoke Test Checklist:**
- [ ] Combined arms message in battle result
- [ ] Coordination bonus shown for allies
- [ ] Inline-dramatic reinforcement arrival
- [ ] Inline-dramatic Grouchy failure
- [ ] Defensive readiness in tooltip
- [ ] Relationship display in marshal tooltip
- [ ] First-time coordination tutorial (inline-dramatic, once only)
- [ ] Enemy phase shows AI coordination
- [ ] Battle detail expandable section
- [ ] Supply attrition warning for large stacks

---

## 16. Files Touched

### Backend

| File | Sessions | Changes |
|------|----------|---------|
| `marshal.py` | 57-60, 64 | Transient fields (6), persistent fields (2), modifier method extensions, co-location tracking |
| `executor.py` | 57-62, 64-65 | `_calculate_coordination_context()`, `_calculate_reinforcements()`, `_distribute_casualties()`, pre-battle preview, relationship check calls |
| `combat.py` | 57, 62, 65 | Combined arms message, `apply_casualties` parameter, coordination messages |
| `battle_report.py` | 57, 65 | Coordination snapshots, 5 new observation categories |
| `enemy_ai.py` | 63 | P4.6, P4.75 mod, P4.76, P4.77, P4.78, coordination estimates |
| `world_state.py` | 59, 61, 66 | `_update_co_location_tracking()`, `reinforced_this_turn` clear, `coordination_tutorial_shown` |
| `objection_v2.py` | 59 | Verify/add SUPPORT personality triggers |
| `region.py` | — | No changes |
| `strategic.py` | — | No changes (SUPPORT already works) |

### Frontend

| File | Sessions | Changes |
|------|----------|---------|
| `map.gd` | 66 | Defensive readiness tooltip, relationship display, reinforcement probability, color coding |
| `main.gd` | 66 | Inline-dramatic display, coordination preview, battle report expansion, tutorial inline-dramatic |
| `enemy_phase_dialog.gd` | 66 | AI coordination observations |

### Docs

| File | Session | Changes |
|------|---------|---------|
| `CLAUDE.md` | 66 | Phase 7 complete, Phase 7b next, new file references |
| `STATUS.md` | 66 | Test count, session history, phase status |
| `ROADMAP.md` | 66 | Phase 7 table updated, Phase 7b deferred items |
| `SYSTEMS_REFERENCE.md` | 66 | New §11 Multi-Marshal Coordination |
| `SAVE_FORMAT_REFERENCE.md` | 66 | New serialized fields |
| `ENEMY_AI_REFERENCE.md` | 66 | P4.6, P4.76, P4.77, P4.78 |

---

## 17. Golden Rules & Gotchas

### Golden Rules

1. **Combat modifiers: SINGLE SOURCE in marshal.py.** All coordination bonuses applied via transient fields in `get_attack_modifier()` / `get_defense_modifier()`. `combat.py` reads them, never recalculates.

2. **All numbers to Godot: `int()`.** All coordination percentages, casualty counts, strength values.

3. **Transient fields: NOT serialized.** `combined_arms_attack_bonus`, `coordination_attack_bonus`, `dedicated_coordination_bonus`, `adjacent_support_bonus` — all cleared between combats. Only `co_location_turns` and `last_relationship_change_turn` are serialized.

4. **State clearing: AFTER reading.** Transient fields set by `_calculate_coordination_context()`, read by `get_*_modifier()`, cleared after `resolve_battle()` returns.

5. **Both sides get independent coordination.** Attacker coordination from attacker's allies. Defender coordination from defender's allies. Calculated separately.

### Gotchas

| Issue | Solution |
|-------|----------|
| Reinforcement relocates marshal mid-turn | Strategic order invalidated — clear `marshal.strategic_order = None` after relocation |
| Reinforced marshal in new fog zone | `update_intel_from_battle()` fires after battle, sees new positions |
| `apply_casualties=False` affects other call sites | ONLY change `_execute_attack`. All 5 other call sites keep `True`. |
| Casualty distribution rounding | Last participant gets remainder to prevent leakage |
| Hard cap race condition | Calculate ALL sources first, THEN cap before applying to transient fields |
| Co-location tracking after death | Dead marshal → clear their `co_location_turns` dict |
| SUPPORT order + reinforcement | SUPPORT marshal gets both: +5% dedicated AND arrival score +10 |
| HOLD + SUPPORT mutual exclusion | One `strategic_order` field. Issuing SUPPORT replaces HOLD. |
| Defensive reinforcement steals player agency | HOLD order blocks reinforcement. Player uses HOLD to prevent unwanted relocation. |
| Combined arms after reinforcement | Recalculate combined arms AFTER reinforcements arrive (new unit types may join) |
| Tutorial fires multiple times | `coordination_tutorial_shown` on WorldState (serialized), checked before inline-dramatic display |
| Coordination preview + objection timing | Preview calculates AFTER objection resolves, not before |
| AI P4.6 fires over undefended capture | P4.6 priority is AFTER P4.5 (undefended capture). Never supersedes free regions. |

---

## 18. Deferred Items

### Linked Group (Must Ship Together)

These three complete the tactical triangle. All must implement as a single unit:

| Feature | Phase | Description |
|---------|-------|-------------|
| **Square Formation** | 7b | Infantry anti-cavalry stance (-40% cav dmg), vulnerable to artillery (+50%) |
| **Artillery SUPPORT auto-bombardment** | 7b | Artillery on SUPPORT auto-bombards before supported marshal's combat |
| **Artillery Overwatch** | 7b | Passive -3% attack debuff on enemies in same region as friendly artillery |

**Documentation requirement:** List as "Tactical Triangle Completion" group in ROADMAP.md, STATUS.md, CLAUDE.md. When any one is picked up, all three come with it.

### Other Deferred Items

| Feature | Phase | Notes |
|---------|-------|-------|
| V2b: Defiance/Vindication | 7b | STRONG/EXTREME concerns trigger defiance. Scaffolding ready. |
| Jealousy system | 7b | Marshal getting all glory → others resent. Needs multi-marshal battle data from Phase 7. |
| Coalition Trigger | 7b | Threat level → war declarations. Core "France can't steamroll" mechanic. |
| Gneisenau Staff Work | 1805 | +10% ally bonus. Coalition-specific advantage for full campaign only. |

---

## 19. Phase 6.5 Sequencing

Phase 6.5 will be COMPLETE before Phase 7 implementation begins. All 10 remaining items ship first:

| 6.5 Feature | Phase 7 Interaction |
|-------------|-------------------|
| **Notification System** | Coordination events use notification infrastructure |
| **Strategic Ledger** | Multi-marshal positioning requires overview screen |
| **Marshal Management UI** | Relationship display needs a home |
| **Campaign Log** | Coordination events should log |
| **Tooltips** | Phase 7 adds coordination/relationship info to tooltips |
| **Campaign Briefing** | Coordination readiness in turn-start summary |
| **Marshal Report** | Per-turn coordination contributions |
| **Tutorial Infrastructure** | First-time coordination tutorial uses this |
| **Map Renderer** | Blocked on art commission — critical path for EA |
| **Wire Marshal Abilities** | Some abilities interact with coordination (Gneisenau deferred) |

Phase 7 Session 66 (Godot UI) depends on tooltip infrastructure existing. If tooltip system is built in Phase 6.5, Session 66 extends it. If not, Session 66 must build the tooltip foundation first (adds scope).

---

## 20. Glossary

| Term | Definition |
|------|-----------|
| **Combined Arms** | Bonus from having multiple unit types (infantry/cavalry/artillery) in same region |
| **Coordination** | Per-ally bonus, relationship-scaled |
| **Dedicated Coordination** | Flat +5%/+5% from 2-turn co-location or SUPPORT order |
| **Adjacent Support** | +2% attack per adjacent friendly marshal |
| **Hard Cap** | +25% attack / +20% defense maximum from all coordination sources |
| **The Grouchy Rule** | Literal personality marshals never auto-reinforce without explicit SUPPORT order |
| **Arrival Score** | Deterministic base + variance formula determining reinforcement success (threshold >60) |
| **Participating** | Marshals in region during combat — take proportional casualties |
| **Non-Participating** | Hostile marshals — 0% coordination, 0% casualties |
| **Building Blocks** | Player and AI use same actions, same executor, same rules |
| **Transient Field** | Marshal field set before combat, read by modifier methods, cleared after. NOT serialized. |
| **Tactical Triangle** | Infantry ↔ Cavalry ↔ Artillery rock-paper-scissors. Phase 7b completes it with Square Formation. |
