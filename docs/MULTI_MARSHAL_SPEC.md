# Phase 7: Multi-Marshal Coordination Spec

> **Design Principle: "Position IS Coordination"**
> All coordination bonuses are automatic and positional. No new command syntax.
> The player's skill is maneuvering marshals into position. The AI's skill is its positioning logic.
> Both benefit identically from the same passive bonuses — Building Blocks principle.

> **Last Updated:** February 19, 2026
> **Phase:** 7 — Multi-Marshal Coordination
> **Sessions:** 57–65 (estimated 9 sessions)

---

## Table of Contents

1. [Design Summary](#1-design-summary)
2. [Combined Arms Bonus](#2-combined-arms-bonus)
3. [Coordination Bonus](#3-coordination-bonus)
4. [SUPPORT Order Enhancement](#4-support-order-enhancement)
5. [Adjacent Reinforcement](#5-adjacent-reinforcement)
6. [Casualty Distribution](#6-casualty-distribution)
7. [Supply Interaction](#7-supply-interaction)
8. [AI Coordination — P4.6](#8-ai-coordination--p46)
9. [Battle Reports & UI](#9-battle-reports--ui)
10. [Session Plan](#10-session-plan)
11. [Deferred Items](#11-deferred-items)
12. [Gotchas & Implementation Notes](#12-gotchas--implementation-notes)

---

## 1. Design Summary

### Bonus Hierarchy

| Priority | Bonus | Source | Relationship-Scaled? |
|----------|-------|--------|---------------------|
| **PRIMARY** | Combined arms | Unit type diversity in region | No |
| **SECONDARY** | Coordination | Per-ally stat-based bonus | Yes |
| **TERTIARY** | SUPPORT order | Flat bonus from explicit order | No (flat) |

### Core Rules

- **Flanking** (attacks from different regions) and **coordination** (same-region stacking) are complementary opposites — both valid, no double-dipping concern.
- A flanking attack CAN also benefit from coordination bonuses if allies are co-located with the attacker.
- **Both sides** get coordination bonuses — attackers benefit from allies in their region, defenders benefit from allies in their region.
- Broken, retreating, and retreat-recovering marshals contribute **nothing** to coordination or combined arms.
- Garrison detachments (player or capital) do NOT count for combined arms or coordination.

---

## 2. Combined Arms Bonus

### Design

The tactical triangle: Infantry ↔ Cavalry ↔ Artillery. Having diverse unit types in the same region creates combined arms synergy. This is the **largest** coordination bonus and represents Napoleonic combined-arms doctrine.

### Detection Logic

For a given marshal about to fight, count the **distinct unit types** among all eligible friendly marshals in the same region (including the fighting marshal):

```python
def get_combined_arms_in_region(marshal, world):
    """Count distinct unit types among eligible allies in marshal's region."""
    types = set()
    for m in world.marshals.values():
        if (m.location == marshal.location
                and m.nation == marshal.nation
                and m.strength > 0
                and not getattr(m, 'broken', False)
                and not getattr(m, 'retreated_this_turn', False)
                and not getattr(m, 'retreat_recovery', 0) > 0):
            if getattr(m, 'artillery', False):
                types.add('artillery')
            elif getattr(m, 'cavalry', False):
                types.add('cavalry')
            else:
                types.add('infantry')
    return types
```

### Bonus Values

| Unit Types Present | Attack Bonus | Defense Bonus |
|-------------------|-------------|--------------|
| 1 of 3 | +0% | +0% |
| 2 of 3 | +10% | +5% |
| 3 of 3 (all types) | +20% | +10% |

### Rules

- **NOT relationship-scaled** — unit types coordinate regardless of personal feelings between marshals.
- Applies to **whoever is attacking/defending** from that region. A non-artillery marshal benefits from artillery presence.
- Garrison detachments do NOT count toward combined arms (they're a regional property, not a marshal).
- Broken, retreating, and retreat-recovering marshals do NOT count.
- The fighting marshal's own type counts (a solo infantry marshal has 1 type present).

### Implementation

Combined arms bonus feeds into `get_attack_modifier()` and `get_defense_modifier()` via new transient fields set before combat:

```python
# Set on marshal BEFORE combat resolution
marshal.combined_arms_attack_bonus = 0.0   # 0.0, 0.10, or 0.20
marshal.combined_arms_defense_bonus = 0.0  # 0.0, 0.05, or 0.10
```

These are transient — calculated fresh before each battle, never serialized.

---

## 3. Coordination Bonus

### Design

Per-ally bonus for each friendly marshal in the same region. Scaled by the relationship between the fighting marshal and each supporting ally.

### Bonus Values (Per Supporting Ally)

| Bonus | Base Value |
|-------|-----------|
| Attack | +3% per ally |
| Defense | +5% per ally |

### Relationship Scaling

The relationship is **asymmetric** — what the fighting marshal thinks of the ally determines the scaling:

| Relationship | Value | Scaling | Attack (per ally) | Defense (per ally) |
|---|---|---|---|---|
| Hostile | -2 | 0% | +0% | +0% |
| Rival | -1 | 50% | +1.5% | +2.5% |
| Professional | 0 | 100% | +3% | +5% |
| Friendly | +1 | 125% | +3.75% | +6.25% |
| Devoted | +2 | 150% | +4.5% | +7.5% |

### Scaling Formula

```python
RELATIONSHIP_SCALING = {
    -2: 0.0,    # Hostile — refuses to coordinate
    -1: 0.50,   # Rival — grudging
    0:  1.0,    # Professional — standard
    1:  1.25,   # Friendly — seamless
    2:  1.50,   # Devoted — fight as one
}

def calculate_coordination_bonus(marshal, world):
    """Calculate total coordination attack/defense bonus from same-region allies."""
    atk_bonus = 0.0
    def_bonus = 0.0

    for ally in world.marshals.values():
        if (ally.name != marshal.name
                and ally.location == marshal.location
                and ally.nation == marshal.nation
                and ally.strength > 0
                and not getattr(ally, 'broken', False)
                and not getattr(ally, 'retreated_this_turn', False)
                and not getattr(ally, 'retreat_recovery', 0) > 0):
            rel = marshal.get_relationship(ally.name)
            scale = RELATIONSHIP_SCALING.get(rel, 1.0)
            atk_bonus += 0.03 * scale
            def_bonus += 0.05 * scale

    return atk_bonus, def_bonus
```

### Rules

- Broken/retreating/recovering marshals: contribute **0%** coordination.
- Just-retreated marshals: no bonuses until retreat recovery completes (existing recovery system).
- Fortified marshals: DO contribute coordination bonuses to attackers in the same region (you're fortified, but your cannons still provide covering fire). Exception: fortification's own defense bonus is unchanged.
- No hard stacking cap — supply attrition (§7) is the natural limiter.

### Implementation

Like combined arms, coordination bonus feeds into modifier methods via transient fields:

```python
# Set on marshal BEFORE combat resolution
marshal.coordination_attack_bonus = 0.0   # Sum of per-ally bonuses
marshal.coordination_defense_bonus = 0.0  # Sum of per-ally bonuses
```

Transient, never serialized.

---

## 4. SUPPORT Order Enhancement

### Current State

The SUPPORT strategic order (`strategic.py:_execute_support`) moves a marshal toward an allied marshal and auto-follows. When co-located, the support marshal stays with the ally. Currently provides **zero combat bonus** beyond co-location.

### Enhancement

SUPPORT-ordered marshals who are co-located with their target get a flat bonus **on top of** passive coordination:

| Bonus | Value | Relationship-Scaled? |
|-------|-------|---------------------|
| Attack | +5% | No — player spent 2 AP, order is complied with |
| Defense | +5% | No |

**Total SUPPORT ally contribution (Professional relationship):**
- Attack: +3% (coordination) + 5% (SUPPORT) = +8%
- Defense: +5% (coordination) + 5% (SUPPORT) = +10%

**Total SUPPORT ally contribution (Devoted relationship):**
- Attack: +4.5% (coordination) + 5% (SUPPORT) = +9.5%
- Defense: +7.5% (coordination) + 5% (SUPPORT) = +12.5%

### Detection

When calculating coordination bonuses, check if the ally has a `StrategicOrder` of type `SUPPORT` targeting the fighting marshal AND is in the same region:

```python
# In coordination calculation, after base coordination:
if ally has active SUPPORT order targeting marshal AND ally.location == marshal.location:
    atk_bonus += 0.05
    def_bonus += 0.05
```

### SUPPORT Relationship Effects (Deterministic with Variance)

SUPPORT orders between marshals with different relationships affect relationship trajectory over time. These use deterministic thresholds + small random variance (same principle as the objection system):

| Condition | Effect | Mechanism |
|-----------|--------|-----------|
| Hostile marshal forced into SUPPORT | Relationship degrades -1 every 3 turns on SUPPORT | Deterministic counter |
| Rival on SUPPORT + win battle together | 30% ± 10% chance relationship improves to Professional | Threshold + variance |
| Friendly/Devoted on SUPPORT + win together | 15% ± 5% chance relationship improves +1 | Threshold + variance |
| Any SUPPORT + lose battle together | 10% ± 5% chance relationship degrades -1 ("blamed for failure") | Threshold + variance |

Relationship changes capped at [-2, +2] (existing system).

### SUPPORT Objection Tie-in

When a SUPPORT order is issued between low-relationship marshals, the V2a objection system evaluates:
- Hostile (-2): STRONG objection ("I will NOT serve under that fool!")
- Rival (-1): MODERATE objection ("Must I really march alongside him?")
- Professional (0): No objection
- Friendly/Devoted: No objection, positive flavor text

This uses the existing `pending_strategic_objection` field and V2a infrastructure. Full V2b defiance escalation is deferred (see §11).

### AI and SUPPORT

**AI does NOT have explicit SUPPORT command.** AI gets coordination bonuses through POSITIONING only (P4.75, P4.8, P4.6). This is the Building Blocks principle — same mechanical bonuses, different interface.

However, AI marshals who are co-located due to P4.75 (ally support) positioning get a **random chance** to benefit from SUPPORT-equivalent coordination:

```python
# In AI coordination calculation:
# If AI ally moved to this region specifically to support (P4.75 intent):
# 25% chance per turn of "clicking" into dedicated support posture
# Once active, provides the +5%/+5% SUPPORT bonus
# Tracked via marshal field: ai_support_posture (bool, transient)
```

This is surfaced in Berthier end-of-turn reports: "Intelligence suggests Blucher has organized his forces to directly support Wellington's defense."

### Artillery on SUPPORT — Auto-Bombardment (TODO)

**Deferred.** When implemented:
- Artillery on SUPPORT auto-bombards before supported marshal's combat (pre-battle bombardment)
- Full collateral/friendly-fire rules apply
- No extra AP cost (part of the SUPPORT order)
- Pairs with square formation design — artillery bombards infantry in square = tactical triangle completion

See §11 Deferred Items.

---

## 5. Adjacent Reinforcement

### Design

Adjacent friendly marshals have a chance to physically arrive at the battle region before combat resolves. This represents rapid forced marches to the sound of the guns (Blucher at Waterloo being the canonical example).

### Arrival Score Formula

```
arrival_score = BASE + (logistics_skill × 5) + relationship_mod + terrain_penalty + random_variance

BASE = 50
THRESHOLD = 60 (must exceed to arrive)
```

| Component | Values |
|-----------|--------|
| Base | 50 |
| Logistics skill | +5 per point (range: +5 to +25 for skill 1-5) |
| Relationship: Hostile (-2) | -20 |
| Relationship: Rival (-1) | -10 |
| Relationship: Professional (0) | +0 |
| Relationship: Friendly (+1) | +10 |
| Relationship: Devoted (+2) | +20 |
| Terrain: Plains/Urban/River | +0 |
| Terrain: Forest | -10 |
| Terrain: Hills | -10 |
| Terrain: Mountains | -20 |
| Random variance | ±8 (uniform) |

### Examples

| Marshal | Logistics | Relationship | Terrain | Score Range | Arrives? |
|---------|-----------|-------------|---------|-------------|----------|
| Blucher (log 4, Devoted to Wellington) | +20 | +20 | Plains 0 | 82-98 | Always |
| Grouchy (log 3, Professional to Ney) | +15 | 0 | Forest -10 | 47-63 | Sometimes |
| Ney (log 2, Hostile to Davout) | +10 | -20 | Plains 0 | 32-48 | Never |
| Davout (log 5, Rival to Ney) | +25 | -10 | Hills -10 | 47-63 | Sometimes |

### Rules

1. **Physical movement:** Arriving marshal physically relocates to the battle region. They stay there after battle — permanent repositioning.
2. **Timing:** Reinforcement check happens BEFORE `resolve_battle()`. Arriving marshals get full same-region coordination and combined arms bonuses for that battle.
3. **Defense too:** Works on defense. If Wellington is attacked and Blucher is adjacent, Blucher gets a reinforcement check to join the defense.
4. **Multiple arrivals:** Each adjacent friendly marshal gets an independent arrival check. Multiple reinforcements possible.
5. **Eligibility filters:**
   - Must be adjacent (1 region away)
   - Must be same nation
   - Must have strength > 0
   - Must NOT be broken, retreating, or in retreat recovery
   - Must NOT have already acted this turn (for player marshals, AP-consuming actions)
   - Must NOT be engaged (enemy in same region)
   - Must NOT be fortified (dug in, not mobile)
6. **Terrain penalty:** Based on terrain of the region the reinforcing marshal is LEAVING (marching out of mountains is hard).
7. **No AP cost:** Reinforcement is reactive, not a player command. It's a check that happens automatically.
8. **Berthier reporting:**
   - Success: "Blucher's corps arrives on Wellington's flank! [Devoted: +20 logistics bonus]"
   - Failure: "Grouchy fails to arrive in time, Your Majesty. [Forest terrain: -10 penalty]"

### Implementation Location

Reinforcement calculation happens in `executor.py` inside `_execute_attack`, BEFORE the call to `resolve_battle()`. The flow:

```
1. Validate attack (existing)
2. Calculate adjacent reinforcements (NEW)
   - For each adjacent friendly marshal, compute arrival score
   - If score > 60, move marshal to battle region
3. Calculate combined arms (NEW) — now includes any arriving marshals
4. Calculate coordination bonuses (NEW) — now includes any arriving marshals
5. Set transient bonus fields on attacker and defender
6. Call resolve_battle() (existing — uses modifier methods that read transient fields)
7. Distribute casualties (NEW — §6)
8. Clear transient fields
```

---

## 6. Casualty Distribution

### Design

When a marshal fights with allies in the same region, casualties are distributed among all participating marshals rather than falling entirely on the primary combatant.

### Distribution Rules

| Ally Type | Casualty Share |
|-----------|---------------|
| Same-region passive ally | Proportional by strength fraction |
| SUPPORT-ordered ally | Half-proportional (support posture, not front line) |
| Adjacent reinforcement | 40-60% of proportional (arrived late) |
| Hostile ally (0% coordination) | 0% casualties — they refused to participate |

### Proportional Calculation

```python
# After resolve_battle() returns total casualties for the side:
total_casualties = battle_result["attacker_casualties"]  # or defender

# Calculate each marshal's share
participating = []  # List of (marshal, weight)
for ally in same_region_allies:
    if ally is SUPPORT-ordered:
        weight = ally.strength * 0.5   # Half-proportional
    elif ally arrived via reinforcement:
        weight = ally.strength * 0.5   # 40-60%, use 0.5 as midpoint
    elif ally.get_relationship(primary.name) == -2:  # Hostile
        weight = 0  # Refused to participate
    else:
        weight = ally.strength  # Full proportional

# Primary combatant
participating.append((primary, primary.strength))

total_weight = sum(w for _, w in participating)
for marshal, weight in participating:
    if total_weight > 0:
        share = total_casualties * (weight / total_weight)
        marshal.strength -= int(share)
        marshal.strength = max(0, marshal.strength)
```

### Edge Cases

- **Primary combatant does NOT take an extra share.** The primary already absorbs the brunt through `resolve_battle()`. Supporting casualties are ADDITIONAL spread.

Wait — clarification needed. `resolve_battle()` returns casualties for the attacker side. Those casualties are currently applied entirely to the primary combatant. With casualty distribution, those same casualties get spread across all participants. The primary combatant's individual casualties go DOWN, while allies absorb part of the total. The total damage to the side remains the same.

```
Before: Primary takes 100% of 5000 casualties = 5000
After:  Primary (20k, weight 20k) + Ally (10k, weight 10k) = 30k total weight
        Primary: 5000 * (20/30) = 3333
        Ally:    5000 * (10/30) = 1667
```

- **Marshal reaches 0 strength:** Uses existing `_apply_forced_retreat_or_break()` for consistent break behavior.
- **Hostile ally at 0% scaling / 0% casualties:** They are physically present but not participating. They don't take casualties and don't provide bonuses. This creates a situation where a Hostile marshal is dead weight in the region — eating supply but contributing nothing.

### Morale Distribution

Supporting marshals who take casualties also take a morale hit:
- -1 morale per 1000 casualties absorbed (same rate as primary combatant)
- Minimum morale 0 (existing floor)

---

## 7. Supply Interaction

### Design

No new supply systems needed. The existing supply capacity system naturally limits stacking.

### How It Works

- Region `supply_capacity` (from `region.py`) is **shared** across all marshals in the region.
- At end of turn, `process_supply_attrition()` in `world_state.py` divides region capacity equally among all marshals present.
- A reinforcing marshal who joins a region immediately dilutes the supply pool for that turn's end-of-turn attrition calculation.
- No attrition exemption for reinforcement — they arrived, they eat supply.

### Emergent Balance

- A region comfortably supplying 2 marshals becomes strained when a 3rd arrives.
- Cycling marshals in and out bleeds everyone's supply each cycle.
- Natural pressure to redistribute after battle: the stack is expensive to maintain.
- Works identically for offensive and defensive reinforcement — consistent rule.
- **No new code required** — existing supply math handles this automatically.

---

## 8. AI Coordination — P4.6

### New Priority: Coordinated Attack Setup

**Position in priority chain:** Between P4.5 (undefended capture) and P4.75 (ally support).

P4.6 never fires over an undefended capture opportunity — free regions always take priority.

### Trigger Conditions

```python
def _find_coordinated_attack_opportunity(self, marshal, nation, world):
    """P4.6: Proactively position for coordinated attack with nearby ally."""

    # 1. Find same-nation allies within 2 regions
    nearby_allies = []
    for ally in world.marshals.values():
        if (ally.name != marshal.name
                and ally.nation == nation
                and ally.strength > 0
                and not getattr(ally, 'broken', False)
                and not getattr(ally, 'retreated_this_turn', False)):
            distance = world.get_distance(marshal.location, ally.location)
            if distance is not None and 1 <= distance <= 2:
                # Relationship check: Rival (-1) or better
                rel = marshal.get_relationship(ally.name)
                if rel >= -1:
                    nearby_allies.append((ally, distance))

    if not nearby_allies:
        return None

    # 2. Find viable enemy targets reachable by both
    for ally, ally_dist in nearby_allies:
        combined_strength = marshal.strength + ally.strength
        # Check regions adjacent to both marshal and ally
        for target_region in self._get_shared_targets(marshal, ally, world):
            enemies = world.get_enemies_in_region(target_region, nation)
            if not enemies:
                continue
            enemy_strength = sum(e.strength for e in enemies)

            # 3. Combined gives 1.5:1 advantage where solo doesn't
            solo_ratio = marshal.strength / max(enemy_strength, 1)
            combined_ratio = combined_strength / max(enemy_strength, 1)
            if combined_ratio >= 1.5 and solo_ratio < 1.5:
                # 4. Move toward staging position
                return self._plan_coordinated_move(marshal, ally, target_region, world)

    return None
```

### AI Combined Arms Awareness

The AI actively tries to group unit types for combined arms bonus when positioning:

```python
# In P4.6 and P7 strategic move scoring:
# Prefer destinations where combined arms types would be present
types_at_destination = get_unit_types_in_region(destination, nation, world)
marshal_type = get_unit_type(marshal)
if marshal_type not in types_at_destination and len(types_at_destination) >= 1:
    score += 8  # Moving here creates combined arms
if len(types_at_destination) >= 2 and marshal_type not in types_at_destination:
    score += 15  # Moving here completes the triangle
```

### AI Assessment of Player Coordination

When the AI evaluates whether to attack a region (P0, P4), it must factor in the player's coordination bonuses:

```python
# In _find_attack_opportunity and P0 engagement:
# Estimate defender's coordination bonus
defender_allies_in_region = count eligible allies
estimated_defense_boost = 1.0 + (defender_allies_in_region * 0.05)  # Conservative
# Use estimated_defense_boost in ratio calculation
effective_enemy_strength = enemy_strength * estimated_defense_boost
```

This prevents the AI from charging into well-coordinated defenses.

### AI SUPPORT-Equivalent Posture

AI marshals positioned together via P4.75 have a 25% chance per turn of achieving "dedicated support posture" — a transient flag that grants the +5%/+5% SUPPORT bonus. This is surfaced in Berthier reports.

```python
# On AI marshal co-located with ally due to P4.75 positioning:
# At start of enemy phase, 25% chance:
if random.random() < 0.25:
    ai_marshal.ai_support_posture = True  # Transient, cleared each turn
```

---

## 9. Battle Reports & UI

### Berthier Coordination Report

After every battle involving coordination, Berthier reports a concise summary. This is a **new observation category** in `battle_report.py`, not a replacement for existing observations.

**Format (single summary line per battle):**

```
"Davout's corps provided supporting fire (+3% attack). Combined arms: infantry + artillery (+10% attack, +5% defense)."
```

```
"Wellington fights alone — Blucher's Prussians failed to arrive from Belgium (forest terrain, -10 penalty)."
```

```
"Three corps converge! Ney, Davout, and Drouot fight together. Combined arms bonus: all three types present (+20% attack, +10% defense). Davout provides reluctant support (Rival: +1.5% attack, +2.5% defense)."
```

### Coordination Report Categories

| Category | Priority | Trigger |
|----------|----------|---------|
| `coordination_full_triangle` | 1 | All 3 unit types + 2+ allies |
| `coordination_combined_arms` | 2 | 2+ unit types present |
| `coordination_reinforcement_success` | 3 | Adjacent marshal arrived |
| `coordination_reinforcement_failure` | 4 | Adjacent marshal failed to arrive |
| `coordination_hostile_refusal` | 5 | Hostile ally in region, 0% scaling |
| `coordination_devoted_synergy` | 6 | Devoted ally, 150% scaling |
| `coordination_basic` | 7 | Any coordination bonus active |

### Pre-Battle Coordination Preview

Before the player commits to an attack, show a preview of coordination bonuses. This is returned in the attack validation response (when attack is valid but before execution):

```json
{
  "coordination_preview": {
    "allies_in_region": [
      {"name": "Davout", "relationship": "Rival", "atk_bonus": 1.5, "def_bonus": 2.5},
      {"name": "Drouot", "relationship": "Friendly", "atk_bonus": 3.75, "def_bonus": 6.25}
    ],
    "combined_arms": {"types": ["infantry", "cavalry", "artillery"], "atk_bonus": 20, "def_bonus": 10},
    "support_bonus": {"active": true, "marshal": "Drouot", "atk_bonus": 5, "def_bonus": 5},
    "adjacent_reinforcements": [
      {"name": "Murat", "estimated_arrival": "likely", "logistics": 3, "relationship": "Professional"}
    ],
    "total_estimated_atk_bonus": 30.25,
    "total_estimated_def_bonus": 22.75
  }
}
```

This is displayed in Godot BEFORE the attack resolves, allowing the player to understand the positioning advantage.

### Marshal Relationship Display

Relationships MUST be visible in the UI. Add to existing marshal hover tooltip in `map.gd`:

```
MARSHAL NEY (France)
Strength: 25,000 | Morale: 78%
CAVALRY: Can attack 2 tiles away
Trust: 65 (Moderate)
---
Relationships:
  Davout: Hostile (-2) ⊘
  Drouot: Professional (0)
  Murat: Friendly (+1) ★
```

Icons: ⊘ (hostile/rival warning), ★ (friendly/devoted indicator). Color-coded: red for hostile/rival, white for professional, gold for friendly/devoted.

---

## 10. Session Plan

### Session 57: Combined Arms Detection & Bonus Application

**Goal:** Detect unit types in a region and apply combined arms bonus to combat.

**Files Modified:**
| File | Changes |
|------|---------|
| `backend/models/marshal.py` | Add transient fields: `combined_arms_attack_bonus`, `combined_arms_defense_bonus`, `coordination_attack_bonus`, `coordination_defense_bonus`, `support_order_bonus` (all default 0.0). Wire into `get_attack_modifier()` and `get_defense_modifier()`. |
| `backend/game_logic/combat.py` | Add combined arms message to tactical_prefix when bonus > 0. |
| `backend/commands/executor.py` | Add `_calculate_coordination_context()` helper. Call before `resolve_battle()` in `_execute_attack`. Set transient fields on both attacker and defender. Clear after battle. |
| `backend/models/world_state.py` | Add `get_allied_marshals_in_region(marshal)` and `get_unit_types_in_region(region, nation)` helpers. |

**New Files:**
| File | Purpose |
|------|---------|
| `tests/test_combined_arms.py` | Combined arms detection, bonus application, edge cases |

**Tests (~45):**
- Unit type detection: infantry, cavalry, artillery identification (3)
- 1 type → no bonus (3)
- 2 types → +10%/+5% (6: each pair of types × attack/defense)
- 3 types → +20%/+10% (3)
- Broken marshal excluded (3)
- Retreating marshal excluded (3)
- Retreat-recovering marshal excluded (3)
- Garrison detachment excluded (3)
- Modifier integration: combined arms feeds into get_attack_modifier (3)
- Modifier integration: combined arms feeds into get_defense_modifier (3)
- Both sides get bonuses independently (2)
- Solo marshal: no combined arms (1)
- Combined arms message in combat tactical_prefix (3)
- Serialization: transient fields NOT serialized (2)
- Full integration: attack with combined arms through executor (4)

**Smoke Test Gate:** `curl -X POST http://127.0.0.1:8005/command -H "Content-Type: application/json" -d '{"command": "Ney attack Wellington"}'` with Drouot in same region → battle report shows combined arms bonus.

---

### Session 58: Coordination Bonus (Relationship-Scaled)

**Goal:** Per-ally coordination bonuses with relationship scaling.

**Files Modified:**
| File | Changes |
|------|---------|
| `backend/commands/executor.py` | Extend `_calculate_coordination_context()` to compute per-ally coordination bonuses with relationship scaling. |
| `backend/models/marshal.py` | Coordination transient fields already added in S57. Verify `get_attack_modifier()` and `get_defense_modifier()` apply them correctly. |
| `backend/game_logic/combat.py` | Add coordination message to tactical_prefix when bonus > 0. Include relationship labels. |
| `backend/game_logic/battle_report.py` | Add coordination observation categories (§9 table). |

**New Files:**
| File | Purpose |
|------|---------|
| `tests/test_coordination_bonus.py` | Relationship scaling, per-ally calculation, stacking |

**Tests (~50):**
- Hostile (0% scaling): 0 bonus (3)
- Rival (50% scaling): half bonus (3)
- Professional (100%): full bonus (3)
- Friendly (125%): 1.25x bonus (3)
- Devoted (150%): 1.5x bonus (3)
- Asymmetric relationships: A→B hostile, B→A professional (4)
- Multiple allies: bonuses stack additively (4)
- Combined arms + coordination interact correctly (multiplicative in modifier) (4)
- Defender gets coordination from their allies (4)
- Attacker gets coordination from their allies (4)
- Broken ally: 0 contribution (2)
- Fortified ally: still contributes coordination (2)
- Retreat-recovering ally: 0 contribution (2)
- Coordination message in combat output (3)
- Battle report coordination observations (6 categories × 1 test) (6)
- Integration: full attack with coordination through executor (3)

**Smoke Test Gate:** Attack with Davout (Rival to Ney) in same region → battle report shows "Davout provides reluctant support (Rival: +1.5% attack)."

---

### Session 59: SUPPORT Order Enhancement

**Goal:** SUPPORT order provides flat +5%/+5% bonus. Relationship effects on SUPPORT. SUPPORT objection for hostile/rival.

**Files Modified:**
| File | Changes |
|------|---------|
| `backend/commands/executor.py` | In `_calculate_coordination_context()`, detect active SUPPORT orders targeting the fighting marshal. Apply +5%/+5% flat bonus. |
| `backend/commands/strategic.py` | Track SUPPORT relationship effects: degradation counter for hostile, improvement chance on battle win. New helper `_process_support_relationship_effects()` called after battle involving SUPPORT marshal. |
| `backend/commands/objection_v2.py` | New SUPPORT objection triggers: Hostile → STRONG, Rival → MODERATE. Add to `evaluate_strategic_objection()`. |
| `backend/commands/disobedience.py` | SUPPORT objection flavor text (hostile refusal, rival reluctance). |

**New Files:**
| File | Purpose |
|------|---------|
| `tests/test_support_enhancement.py` | SUPPORT bonus, relationship effects, objections |

**Tests (~40):**
- SUPPORT ally: +5%/+5% on top of coordination (4)
- SUPPORT not relationship-scaled (3)
- SUPPORT detection: must have active order targeting this marshal (3)
- SUPPORT detection: must be co-located (3)
- No SUPPORT order: no extra bonus (2)
- SUPPORT + coordination + combined arms stacking (3)
- Hostile degradation: -1 every 3 turns on SUPPORT (3)
- Rival improvement: ~30% on shared victory (3)
- Friendly improvement: ~15% on shared victory (2)
- Shared defeat degradation: ~10% chance (2)
- Relationship changes respect [-2, +2] cap (2)
- SUPPORT objection: Hostile → STRONG (3)
- SUPPORT objection: Rival → MODERATE (3)
- SUPPORT objection: Professional → no objection (1)
- Objection flavor text exists for hostile/rival (2)
- Integration: full SUPPORT flow through strategic.py (2)

---

### Session 60: Adjacent Reinforcement

**Goal:** Adjacent marshals can arrive before combat. Deterministic arrival score + variance.

**Files Modified:**
| File | Changes |
|------|---------|
| `backend/commands/executor.py` | Add `_calculate_reinforcements()` in `_execute_attack`, called BEFORE `resolve_battle()`. Arriving marshals physically relocate. Results feed into coordination/combined arms calculation. |
| `backend/models/world_state.py` | Add `get_adjacent_friendly_marshals(marshal)` helper. Add `calculate_reinforcement_score(reinforcing_marshal, target_marshal)` with the full formula. |
| `backend/models/region.py` | Add `TERRAIN_REINFORCEMENT_PENALTY` dict (mirrors movement cost concept). |
| `backend/game_logic/battle_report.py` | Reinforcement success/failure observation categories. |

**New Files:**
| File | Purpose |
|------|---------|
| `tests/test_reinforcement.py` | Arrival score, terrain, relationship, edge cases |

**Tests (~55):**
- Base score calculation (3)
- Logistics skill bonus: skill 1-5 range (5)
- Relationship modifiers: all 5 levels (5)
- Terrain penalties: all 6 terrains (6)
- Random variance within ±8 (3)
- Threshold: score > 60 arrives, ≤ 60 doesn't (4)
- Physical relocation: marshal moves to battle region (3)
- Permanent positioning: marshal stays after battle (2)
- Defense reinforcement: works when player is defender (4)
- Multiple adjacent marshals: independent checks (3)
- Eligibility: broken excluded (2)
- Eligibility: retreating excluded (2)
- Eligibility: engaged (enemy in same region) excluded (2)
- Eligibility: fortified excluded (2)
- Eligibility: already acted this turn excluded (2)
- Arriving marshal gets full coordination + combined arms (3)
- Berthier success message (2)
- Berthier failure message (2)
- No eligible adjacent marshals: no check (1)
- Integration: full attack with reinforcement through executor (4)

**Smoke Test Gate:** Curl attack with Blucher adjacent to Wellington. Blucher (Devoted, high logistics) should arrive reliably. Battle report shows arrival.

---

### Session 61: Casualty Distribution

**Goal:** Casualties spread across participating marshals proportionally.

**Files Modified:**
| File | Changes |
|------|---------|
| `backend/commands/executor.py` | Add `_distribute_casualties()` called AFTER `resolve_battle()`. Replaces direct strength subtraction with proportional distribution. |
| `backend/game_logic/combat.py` | `resolve_battle()` returns raw casualties but does NOT apply them directly to marshal strength when coordination flag is set. Returns `{..., "apply_casualties": False}` when caller will handle distribution. |
| `backend/game_logic/battle_report.py` | Casualty distribution details in report. |

**New Files:**
| File | Purpose |
|------|---------|
| `tests/test_casualty_distribution.py` | Proportional, SUPPORT, reinforcement, hostile, edge cases |

**Tests (~40):**
- Proportional by strength: 20k + 10k → 2/3 and 1/3 (4)
- SUPPORT marshal: half-proportional weight (4)
- Adjacent reinforcement: 50% weight (4)
- Hostile marshal: 0 weight, 0 casualties (3)
- Primary combatant casualty reduction (3)
- Marshal reaches 0 strength → break system (3)
- Morale hit on supporting marshals: -1 per 1000 (3)
- Single marshal (no allies): existing behavior unchanged (3)
- Total casualties remain the same (conservation check) (3)
- Three marshals: complex proportional (3)
- SUPPORT + passive + reinforcement mixed distribution (3)
- Integration: full battle with casualty distribution (4)

---

### Session 62: AI P4.6 — Coordinated Attack Setup

**Goal:** Enemy AI proactively positions for coordinated attacks. AI considers coordination bonuses in attack decisions.

**Files Modified:**
| File | Changes |
|------|---------|
| `backend/ai/enemy_ai.py` | Add `_find_coordinated_attack_opportunity()` at P4.6. Add combined arms awareness to P7 scoring. Add coordination bonus estimation to P0/P4 attack strength assessment. Add AI support posture chance (25% per turn). |
| `backend/game_logic/turn_manager.py` | Clear `ai_support_posture` flags at start of enemy phase. |

**New Files:**
| File | Purpose |
|------|---------|
| `tests/test_ai_coordination.py` | P4.6 triggers, combined arms grouping, coordination assessment |

**Tests (~45):**
- P4.6 trigger: ally within 2 regions + viable target + combined ratio ≥ 1.5 (4)
- P4.6 skip: solo ratio already ≥ 1.5 (no need for coordination) (2)
- P4.6 skip: ally too far (distance > 2) (2)
- P4.6 skip: Hostile relationship (2)
- P4.6 priority: fires after P4.5 undefended capture (3)
- P4.6 priority: fires before P4.75 ally support (2)
- Combined arms awareness: AI prefers completing triangle (4)
- Combined arms awareness: AI groups artillery with infantry (3)
- Attack assessment: defender coordination factored in (4)
- Attack assessment: solo attack discouraged against coordinated defense (3)
- AI support posture: 25% activation chance (3)
- AI support posture: provides +5%/+5% when active (2)
- AI support posture: cleared each turn (2)
- Wellington-Blucher coordination: Devoted pair coordinates (4)
- Ney-Davout: Hostile pair never coordinates (3)
- Full integration: AI turn with P4.6 positioning (2)

---

### Session 63: Battle Reports & Berthier Integration

**Goal:** Coordination bonuses surface in battle reports, Berthier observations, and turn summaries.

**Files Modified:**
| File | Changes |
|------|---------|
| `backend/game_logic/battle_report.py` | 7 new coordination observation categories with templates. Coordination summary line in `generate_battle_report()`. |
| `backend/commands/executor.py` | Pass coordination context to `generate_battle_report()`. Include coordination_preview in attack validation response. |
| `backend/main.py` | Pass through `coordination_preview` and `coordination_report` fields in API response. |

**New Files:**
| File | Purpose |
|------|---------|
| `tests/test_coordination_reports.py` | Report generation, observation selection, preview format |

**Tests (~35):**
- Coordination summary line format (4)
- Observation priority ordering (7 categories) (7)
- Combined arms message variants (3)
- Reinforcement success/failure messages (4)
- Hostile refusal message (2)
- Devoted synergy message (2)
- Coordination preview JSON structure (4)
- Preview includes all bonus sources (3)
- Preview with no coordination: empty/null (2)
- Integration: full battle → report includes coordination (4)
- AI battle reports surface coordination (2)
- Berthier AI SUPPORT posture observation (2)

---

### Session 64: Godot Frontend — Coordination Display

**Goal:** Player sees coordination bonuses in tooltips, pre-battle preview, and battle reports.

**Files Modified:**
| File | Changes |
|------|---------|
| `godot-client/.../map.gd` | Add relationship display to marshal tooltip. Show coordination indicators on map (visual cue when multiple friendly marshals in region). |
| `godot-client/.../main.gd` | Handle `coordination_preview` in command response — display before attack executes. Handle `coordination_report` in battle result display. |

**Tests:** Backend-only tests from prior sessions cover data. Godot changes are manual smoke test.

**Smoke Test Gate (MANDATORY — test ALL of these with curl + Godot):**
1. Marshal tooltip shows relationships with color coding
2. Attack with ally in region → coordination preview displayed before result
3. Battle report shows coordination summary line
4. Reinforcement arrival displayed in battle result
5. Reinforcement failure displayed in battle result
6. Combined arms indicator visible in attack with multiple unit types
7. Enemy turn report shows AI coordination when applicable

---

### Session 65: Integration Audit & Edge Cases

**Goal:** Full system audit, edge case fixes, documentation updates.

**Files Modified:**
| File | Changes |
|------|---------|
| `docs/SYSTEMS_REFERENCE.md` | Add §11 Multi-Marshal Coordination section |
| `docs/SAVE_FORMAT_REFERENCE.md` | Document any new serialized fields |
| `docs/ENEMY_AI_REFERENCE.md` | Add P4.6, combined arms awareness, coordination assessment |
| `docs/TUTORIAL_SCRIPT.md` | Add coordination tutorial content |
| `docs/MANUAL_TEST_PLAN.md` | Add coordination manual test scenarios |

**New Files:**
| File | Purpose |
|------|---------|
| `tests/test_coordination_integration.py` | Cross-system integration, save/load, AI full game |

**Tests (~30):**
- Save/load: coordination-relevant state survives roundtrip (4)
- Serialization enforcement: new fields (if any) pass enforcement test (2)
- AI full turn: P4.6 fires, coordination bonuses apply, casualties distribute (4)
- Player full turn: attack + SUPPORT + reinforcement + combined arms (4)
- Both sides coordinated: attacker and defender coordination (3)
- Fortified ally contributes coordination to attacker (2)
- Retreat into coordinated region: no immediate bonus (2)
- Strategic order conflicts: SUPPORT + MOVE_TO (2)
- Flanking + coordination: both apply without conflict (3)
- Supply pressure: 3+ marshals in region → attrition (2)
- Edge: all marshals broken → no coordination (1)
- Edge: single marshal in region → no coordination bonus (1)

**Final Audit Checklist:**
- [ ] All `int()` wrapping for Godot values
- [ ] Serialization enforcement passes
- [ ] No floats in API responses
- [ ] Enemy AI gets identical bonuses (Building Blocks)
- [ ] SUPPORT bonus is flat (not relationship-scaled)
- [ ] Combined arms is NOT relationship-scaled
- [ ] Broken/retreating excluded from all bonuses
- [ ] Garrison detachments excluded from combined arms
- [ ] Battle reports surface all coordination info
- [ ] Relationship display in marshal tooltip
- [ ] Pre-battle preview shows coordination

---

## 11. Deferred Items

Items explicitly NOT in this spec. Track in ROADMAP.md.

| Item | Deferred To | Reason |
|------|-------------|--------|
| **Square Formation** | Phase 7b or later | Full tactical triangle (infantry squares vs cavalry, vulnerable to artillery). Pairs with artillery SUPPORT auto-bombardment. Design pending. |
| **Artillery SUPPORT Auto-Bombardment** | With Square Formation | Pre-battle bombardment from SUPPORT artillery. Needs square formation for the triangle to close. Full collateral rules apply. |
| **V2b Defiance/Vindication** | Phase 7b | STRONG/EXTREME concerns trigger defiance. Spec in OBJECTION_V2.md. Scaffolding from V2a ready. |
| **Jealousy System** | Phase 7b | Marshal getting all glory → others resent. Needs multi-marshal combat data to calculate. |
| **Coalition Trigger** | Phase 7b or Phase 8 | Threat level → war declarations. Moved from Phase 8 but not in coordination spec. |
| **Gneisenau Staff Work** | 1805 Campaign | "+10% ally bonus" — Coalition-specific advantage. Greyed-out tooltip in current UI: "Staff Work — activates in full campaign." |
| **Rivalry Resolved Event** | Phase 7b | Rival marshals fight successfully → trust boost. Needs multi-marshal battle data. |
| **Strategic Ledger** | Phase 6.5 remaining | Full strategic overview UI. |
| **AP Scaling for 1805** | 1805 Campaign | Per-nation AP varies by bureaucratic capacity. |
| **AI Fog of War** | 1805 Campaign | AI gets fog at 80+ regions. |

---

## 12. Gotchas & Implementation Notes

### Golden Rule #1 Compliance

All coordination bonuses MUST flow through `get_attack_modifier()` / `get_defense_modifier()` in `marshal.py`. These methods currently don't take a `world` parameter. The solution:

**Pre-calculate and set transient fields** before combat in `executor.py`:

```python
# In _execute_attack, BEFORE resolve_battle():
context = self._calculate_coordination_context(attacker, defender, world)
attacker.combined_arms_attack_bonus = context["attacker_ca_atk"]
attacker.combined_arms_defense_bonus = context["attacker_ca_def"]
attacker.coordination_attack_bonus = context["attacker_coord_atk"]
attacker.coordination_defense_bonus = context["attacker_coord_def"]
# ... same for defender ...

result = resolve_battle(attacker, defender, ...)

# AFTER resolve_battle():
self._distribute_casualties(attacker, defender, context, result)

# Clear transient fields
attacker.combined_arms_attack_bonus = 0.0
# ... etc ...
```

This avoids changing the signature of modifier methods.

### Modifier Application in marshal.py

Add to the END of `get_attack_modifier()`:

```python
# Multi-marshal coordination bonuses (set externally before combat)
ca_bonus = getattr(self, 'combined_arms_attack_bonus', 0.0)
if ca_bonus > 0:
    modifier *= (1.0 + ca_bonus)

coord_bonus = getattr(self, 'coordination_attack_bonus', 0.0)
if coord_bonus > 0:
    modifier *= (1.0 + coord_bonus)

support_bonus = getattr(self, 'support_order_bonus', 0.0)
if support_bonus > 0:
    modifier *= (1.0 + support_bonus)
```

Using `getattr` with defaults means existing tests don't need the fields — they default to 0.0 (no bonus).

### Serialization Warning

Transient coordination fields (`combined_arms_attack_bonus`, `coordination_attack_bonus`, etc.) are calculated fresh before each battle and cleared after. They MUST NOT be serialized. The `test_serialization_enforcement.py` test will flag them if accidentally added to `to_dict()`.

However, if any NEW persistent fields are added (e.g., `ai_support_posture`), they MUST be serialized. Review list:
- `ai_support_posture` (bool, transient — cleared each enemy phase, no serialization needed)
- Relationship changes from SUPPORT are persisted through existing `relationships` dict serialization.

### Combat.py Casualty Application

Currently `resolve_battle()` directly modifies `attacker.strength` and `defender.strength`. With casualty distribution, we need `resolve_battle()` to return casualties WITHOUT applying them when a coordination flag is set. Two options:

**Option A (recommended):** Add `apply_casualties=True` parameter to `resolve_battle()`. When `False`, return casualties in result dict but don't modify marshal strength. Executor handles distribution.

**Option B:** Always apply to primary, then redistribute (swap casualties between primary and allies). More complex, harder to reason about.

Go with Option A. Minimal change to combat.py, clean separation.

### AI Action Ordering

AI marshals act in priority order (highest priority first, via `get_marshal_priority()`). If AI Marshal A gets a coordination bonus from Marshal B being nearby, and then Marshal B moves away, the bonus was "real" because B was there when A fought. The existing priority system handles this:
- Combat-engaged marshals act first (P0)
- Marshals currently in combat zones get high priority
- P4.6 positioning actions happen AFTER immediate combat priorities

Verify during Session 62 that the ordering doesn't create paradoxes.

### Reinforcement and Turn Actions

A marshal who reinforces an adjacent battle has NOT "acted" in the formal AP sense — reinforcement is reactive, not a player command. However, the marshal physically moved to a new region. This creates a question: can that marshal still act on their own AP?

**Rule:** A marshal who reinforces is marked as `reinforced_this_turn = True` (transient flag). This:
- Prevents them from also being ordered to attack/move (they already moved)
- Does NOT consume player AP (the reinforcement was automatic)
- Is cleared at turn start

### Pre-Battle Preview Flow

The coordination preview must happen AFTER attack validation but BEFORE execution. The current flow in `_execute_attack` is:

```
validate → resolve_battle → return result
```

We need:

```
validate → calculate coordination preview → return preview to frontend
(player sees preview, command auto-continues)
→ resolve_battle with coordination → return result
```

**Implementation:** The preview is calculated as part of the attack response. It doesn't pause for player confirmation — it's informational only, displayed alongside the battle result. This avoids adding a new back-and-forth API call.

### Supply Impact Verification

Verify that `process_supply_attrition()` in `world_state.py` already divides supply capacity among all marshals in a region. If it calculates per-marshal independently, the stacking penalty is already there. If not, this is the one place in §7 that needs a code change.

Current code (verify during Session 57): `process_supply_attrition()` iterates marshals per region and checks if `marshal.strength > supply_capacity`. If multiple marshals share a region, each is checked against the full capacity independently. **This needs to change** — capacity should be divided among all marshals present.

### Test Count Summary

| Session | New Tests | Running Total |
|---------|-----------|---------------|
| 57: Combined Arms | ~45 | ~3032 |
| 58: Coordination Bonus | ~50 | ~3082 |
| 59: SUPPORT Enhancement | ~40 | ~3122 |
| 60: Adjacent Reinforcement | ~55 | ~3177 |
| 61: Casualty Distribution | ~40 | ~3217 |
| 62: AI P4.6 | ~45 | ~3262 |
| 63: Battle Reports | ~35 | ~3297 |
| 64: Godot Frontend | 0 (manual) | ~3297 |
| 65: Integration Audit | ~30 | ~3327 |
| **Total Phase 7** | **~340** | **~3327** |

---

## Appendix: Modifier Stack Example

**Scenario:** Ney (cavalry, aggressive) attacks Wellington. Davout (infantry, Rival to Ney) is in same region on SUPPORT. Drouot (artillery, Friendly to Ney) is in same region passively. Murat (cavalry, Professional to Ney) reinforces from adjacent region.

**Combined Arms:** Infantry (Davout) + Cavalry (Ney, Murat) + Artillery (Drouot) = 3/3 → +20% attack, +10% defense

**Coordination (Ney's perspective):**
- Davout (Rival, 50%): +1.5% atk, +2.5% def
- Drouot (Friendly, 125%): +3.75% atk, +6.25% def
- Murat (Professional, 100%): +3% atk, +5% def
- Total: +8.25% atk, +13.75% def

**SUPPORT (Davout on SUPPORT for Ney):**
- +5% atk, +5% def (flat)

**Ney's Total Coordination Bonus:**
- Attack: 20% (CA) + 8.25% (coord) + 5% (SUPPORT) = +33.25%
- Defense: 10% (CA) + 13.75% (coord) + 5% (SUPPORT) = +28.75%

**Plus Ney's existing modifiers:** aggressive stance (+15% atk), personality (+15% atk base), recklessness, etc.

**Casualty Distribution (if 5000 total attacker casualties):**
- Ney: 25k strength, weight 25k → 25/62.5 = 40% → 2000
- Davout: 20k strength, weight 10k (SUPPORT half) → 10/62.5 = 16% → 800
- Drouot: 15k strength, weight 15k → 15/62.5 = 24% → 1200
- Murat: 25k strength, weight 12.5k (reinforcement 50%) → 12.5/62.5 = 20% → 1000
- Total: 5000 ✓
