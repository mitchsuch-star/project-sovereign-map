# Tactical Triangle — Design Spec

> **Status:** APPROVED — Ready for implementation
> **Ships as:** Two linked sessions (see Implementation Plan)
> **Prerequisite:** Phase 7 audit clean (Session 66 complete)
> **Estimated tests:** ~85
> **Model recommendation:** Opus (three cross-system features touching combat.py, executor.py, enemy_ai.py, objection_v2.py, marshal.py simultaneously)

---

## The Historical Problem

The Napoleonic tactical triangle was the central battlefield dilemma of the era:

- **Infantry in line** could pour devastating musket volleys into enemy formations — but was vulnerable to cavalry charges that could sweep through the thin ranks
- **Infantry in square** was nearly impervious to cavalry — horses refused to charge a wall of bayonets — but the packed formation was a perfect target for artillery
- **Artillery** could devastate squares and static positions — but was helpless against fast-moving cavalry that could overrun the gun crews

No formation was safe against everything. The commander who read the battlefield correctly — knowing when to form square, when to stay in line, when to advance the guns — won. The commander who guessed wrong watched his army disintegrate.

This spec completes that triangle in Ink & Iron.

---

## What Already Exists

| Interaction | Effect | Location | Status |
|-------------|--------|----------|--------|
| **Cavalry → Artillery** | +30% shock multiplier | `combat.py` | Shipped (Phase 6) |
| **Artillery bombardment** | Ranged damage, fort degradation | `executor.py` | Shipped (Sessions 48-52) |
| **Artillery can't-attack-after-move** | Blocks attack if `moved_this_turn` | `executor.py` | Shipped |
| **Artillery no-advance-on-win** | Stays at origin, no capture | `executor.py` | Shipped |
| **SUPPORT strategic order** | March to ally, follow, +5% dedicated bonus | `strategic.py` | Shipped |
| **HOLD auto-bombardment** | Artillery on HOLD fires at adjacent enemies | `strategic.py` | Shipped (Session 51) |

**What's missing:**
- Infantry has no counter to cavalry (cavalry charges are always devastating)
- Artillery on SUPPORT does nothing proactive — it just follows the supported ally around
- Artillery presence in a region provides no passive deterrent

---

## Feature 1: Square Formation

### The Player Experience

The player types: *"Davout, form square"*

Berthier responds: *"Davout orders the regiments into square! Bayonets bristle outward — cavalry charges will break against this wall, but the packed ranks invite artillery fire, Sire."*

Uxbridge's cavalry charges. The square holds. -40% to Uxbridge's attack. The cavalry wheels away, bloodied.

But then PrinceAugust's guns open up. +50% bombardment damage. The packed formation shudders under the shells.

The player must decide: stay in square and absorb the shelling, or break square and risk the cavalry returning?

**That's the game.** That's the Napoleonic dilemma made playable.

### Mechanics

**Command:** "form square" / "square formation" / "square up"
**Cost:** 1 AP (tactical stance, same as fortify)
**Who:** Infantry marshals only. Cavalry and artillery cannot form square.
**Persistence:** Across turns (like fortify). Not consumed on use.

**New field on Marshal:**
```python
self.square_formation: bool = False  # Serialized
```

**Effects while in square:**

| Effect | Value | Rationale |
|--------|-------|-----------|
| Cavalry attack damage reduction | -40% | Horses refuse to charge bayonet wall |
| Artillery melee damage bonus | +50% | Packed ranks, can't miss |
| Bombardment damage bonus | +50% | Same — concentrated target |
| Defense modifier | +5% | Tight formation, mutual support |
| Cannot attack | Auto-breaks on attack order | Square is defensive only |
| Cannot move | Auto-breaks on move order | Fixed position |

### Where Effects Live (Golden Rule #1)

The +5% defense bonus goes in `marshal.py::get_defense_modifier()` — it's a marshal-intrinsic modifier.

The -40% cavalry reduction and +50% artillery bonus are **target-type interactions** — they go in `combat.py::resolve_battle()` alongside the existing cavalry counter block. They are NOT in `get_defense_modifier()` because they depend on the *attacker's* type, not just the defender's state.

```
marshal.py  → +5% defense (square_formation flag)
combat.py   → -40% cavalry damage / +50% artillery damage (target-type interaction)
executor.py → +50% bombardment damage (bombardment path, separate from resolve_battle)
```

### Square Auto-Break

For smooth UX, square does NOT block actions — it auto-breaks:

```python
# In _execute_attack / _execute_move, early in the function:
if getattr(marshal, 'square_formation', False):
    marshal.square_formation = False
    # Prepend to message: "{name} breaks square and advances."
```

**Explicit break:** "break square" / "form line" = **free action (0 AP)**. Returning to default formation shouldn't cost an action.

**Forced break:** Square also breaks on:
- Forced retreat (morale collapse)
- Marshal broken
- NOT on being attacked (surviving attacks is the point)
- NOT on being bombarded (you suffer +50% but the square holds)

### Square + Fortify Interaction

**They stack.** A fortified square is historically accurate (redoubt + square formation). The combined bonuses make the position extremely hard to crack with infantry or cavalry alone — but artillery will devastate it. This is exactly the intended design pressure: it forces the attacker to bring guns.

### Serialization

`square_formation: bool` — serialized in `to_dict()`/`from_dict()`, default `False` for backward compat.

### Battle Report

New snapshot entries:
- Attacker modifier: "Square vulnerability (+50%)" when artillery attacks square
- Defender modifier: "Square formation (+5% defense)" and "Square vs cavalry (-40% damage)"

New Berthier observations (add to `battle_report.py`):
- `square_held_cavalry`: "Davout's square held firm against the cavalry charge. The bayonets did their work, Sire."
- `square_shelled`: "The enemy guns savaged Davout's square. The formation holds, but at terrible cost."
- `square_broke_cavalry_and_shelled`: "The square repelled the cavalry but drew the enemy's guns. A bitter trade, Sire."

### Objection Triggers (V2a)

| Personality | Trigger | Level | Flavor |
|-------------|---------|-------|--------|
| Aggressive infantry | Ordered to form square | MODERATE | "Square?! You want me to stand here like a target? Let me CHARGE them!" |
| Cautious infantry | Form square when enemy artillery adjacent but no cavalry | MILD | "Sire, their guns will punish us in square. I see no cavalry to warrant it." |
| Any infantry | Form square when already fortified | MILD | "We are already entrenched, Sire. The square adds little behind these walls." |

### AI Behavior

New priority: **P2.5 — Form Square** (between existing P2 engagement checks and P3 counter-punch):

```
IF infantry AND NOT in square AND NOT cavalry AND NOT artillery:
    adjacent_cavalry = enemy cavalry within 1 region
    adjacent_artillery = enemy artillery within 1 region

    IF adjacent_cavalry AND NOT adjacent_artillery:
        → form_square (clear choice: cavalry threatens, no artillery risk)

    IF adjacent_cavalry AND adjacent_artillery:
        → personality decision:
            cautious → form_square (survive the charge, accept shelling)
            aggressive → stay in line (prefer attacking)
            literal → form_square (default safe choice)

    IF in_square AND no adjacent cavalry:
        → break square (no longer needed)
```

**AI does NOT form square when:**
- Already fortified (fortify provides defense, square would make them an artillery target for little gain)
- Attacking (aggressive AI stays in line to attack)
- Only artillery threatens (square makes it WORSE)

---

## Feature 2: Artillery SUPPORT Auto-Bombardment

### The Player Experience

The player types: *"Drouot, support Ney"*

Drouot marches to Ney's position (existing SUPPORT behavior). Next turn, Ney attacks Wellington.

**Before** Ney's combat resolves, Drouot's guns open up on Wellington. A free bombardment softens the target. Then Ney charges into a weakened defender.

The player sees: *"Drouot's guns bombard Wellington's position in support of Ney's attack! [bombardment damage]. Ney then attacks..."*

This creates the historical combined-arms sequence: **soften with artillery, then charge with infantry/cavalry.**

### Mechanics

**Trigger:** Artillery marshal is on a SUPPORT order targeting marshal X. Marshal X initiates an attack. The artillery auto-bombards the **defender** of that attack before combat resolves.

**When it fires:** Inside `_execute_attack()`, AFTER coordination context is calculated but BEFORE `resolve_battle()`. The bombardment result is prepended to the combat output.

**What it uses:** The existing `_execute_bombardment()` code path. No new bombardment formula. Same terrain modifiers, same collateral rules, same per-turn limits.

**Constraints:**
- Artillery must be **adjacent to OR co-located with** the battle region (bombardment range = adjacent, same as normal)
- Artillery must NOT have `moved_this_turn` (same rule as manual bombardment)
- Artillery must have bombardments remaining this turn (`bombardments_this_turn < 2`)
- Artillery must NOT be broken/retreating/recovering
- Consumes one of the artillery's `bombardments_this_turn` (shared pool with manual and HOLD bombardment)
- Does NOT consume player AP (it's the artillery's autonomous action via SUPPORT order)
- Collateral damage rules still apply (friendly fire possible if allies in target region)

**What it does NOT do:**
- Auto-bombardment does NOT fire on defensive battles (only when the supported marshal is the **attacker**)
- Does NOT fire if the supported marshal's attack is an auto-charge (reckless cavalry) — only player-initiated or AI-initiated attacks
- Does NOT grant an extra bombardment beyond the 2/turn limit — it's spending one of its normal bombardments proactively

### Code Location

In `executor.py::_execute_attack()`, new block:

```
[existing: reinforcement calculation]
[existing: coordination context calculation]

── NEW: SUPPORT AUTO-BOMBARDMENT ──
For each same-nation artillery marshal with SUPPORT order targeting the attacker:
    IF eligible (adjacent/co-located, not moved, bombardments remaining, not broken):
        Execute bombardment against defender
        Append result to pre_battle_messages
        Defender takes bombardment damage BEFORE resolve_battle()

[existing: resolve_battle()]
```

### Interaction with Existing Systems

| System | Interaction |
|--------|-------------|
| **Bombardment limit** | Shares `bombardments_this_turn` pool. Manual + HOLD + auto-support = 2 max per turn. |
| **Collateral damage** | Same 40% chance, same friendly fire rules. If Ney is co-located with the defender, he could take collateral. |
| **Fort degradation** | Auto-bombardment degrades forts same as manual. |
| **Bombardment streak** | Increments normally (same target = streak builds). |
| **Combined arms** | Auto-bombardment does NOT add to combined arms type counting (bombardment already excluded per A-D6). The artillery's PRESENCE already counts for combined arms. |
| **Exhaustion** | Artillery is exempt from exhaustion. No change. |
| **HOLD + SUPPORT mutual exclusion** | Already enforced — one `strategic_order` field. SUPPORT replaces HOLD. Auto-bombardment replaces HOLD auto-bombardment. |
| **Coordination bonuses** | The artillery on SUPPORT already provides dedicated coordination. Auto-bombardment is an *additional* benefit. |

### Battle Report

Bombardment result appears as a preamble in the battle output:

```
"Drouot's guns soften the enemy position before the assault!"
[bombardment damage/details]
"Ney then attacks Wellington..."
[normal combat result]
```

New Berthier observations:
- `support_bombardment_effective`: "Drouot's preparatory bombardment was devastating. Ney's charge met a shaken enemy."
- `support_bombardment_minimal`: "Drouot's guns fired in support, though the terrain blunted their effect."

### AI Behavior

AI already uses SUPPORT (P4.75). No new AI priority needed — when AI artillery is on SUPPORT and the supported marshal attacks, auto-bombardment fires automatically through the same code path. Building Blocks.

---

## Feature 3: Artillery Overwatch

### The Player Experience

The player stations Drouot in a region. Enemy marshals in the same region suffer a passive combat debuff. No command needed — Drouot's guns are simply *there*, watching the field.

The player sees in the battle report: *"Artillery overwatch (Drouot): -3% attack"* on the enemy's modifier list.

This rewards keeping artillery positioned well — even when they're not actively bombarding, their presence suppresses enemy operations.

### Mechanics

**Effect:** Each friendly artillery marshal in a region applies a **-3% attack debuff** to all enemies attacking from or within that region.

**Stacking:** Multiple artillery in one region stack: 2 artillery = -6%. (Unlikely in Waterloo scenario with only Drouot, but scales correctly for 1805.)

**Clarified direction:** Overwatch is a **transient attacker debuff**. When the attacker's target region contains enemy (from attacker's perspective) artillery, the attacker suffers -3% per enemy artillery unit in the region.

In practice for the player: if Drouot is in Belgium and Wellington attacks Belgium, Wellington gets -3% attack. If Ney attacks a region where PrinceAugust is stationed, Ney gets -3%.

**Where it lives (Golden Rule #1):**

**New transient field on attacker:** `overwatch_penalty: float = 0.0`
Applied in `get_attack_modifier()` as `modifier *= (1.0 - self.overwatch_penalty)`

**Calculated in:** `_execute_attack()`, alongside coordination context. Count enemy artillery in the defender's region, set attacker's overwatch_penalty.

**Constraints:**
- Only non-broken, non-retreating, non-recovering artillery counts
- Artillery that `moved_this_turn` does NOT provide overwatch (guns not set up yet)
- Stacks up to 3 artillery max (-9% cap — prevents degenerate stacking in 1805)
- Does NOT apply to bombardment (ranged fire isn't affected by local overwatch)
- Does NOT apply to the artillery marshal itself defending in melee (that's already covered by the cavalry counter)

### Interaction with Existing Systems

| System | Interaction |
|--------|-------------|
| **Coordination hard cap** | Overwatch is NOT a coordination bonus — it's an enemy debuff. Does not count toward the +25%/+20% cap. |
| **Combined arms** | Independent. Combined arms rewards YOUR composition; overwatch punishes the ENEMY's exposure to your guns. |
| **Fortification** | Artillery in a fortified position still provides overwatch. Being dug in doesn't stop the guns from firing. |
| **AI combat assessment** | AI should factor overwatch into threat evaluation: attacking a region with artillery is costlier. Add to `_assess_battle_odds()` or equivalent. |
| **Fog of war** | Overwatch only applies if the artillery is actually there — fog doesn't matter because combat reveals positions. |

### Battle Report

Modifier list entry: "Artillery overwatch (Drouot): -3% attack" (penalty type)

Berthier observation (when overwatch contributed to a defensive victory):
- `overwatch_repelled`: "The enemy advance faltered under Drouot's watchful guns. Even without a full bombardment, the artillery's presence was felt."

---

## The Complete Triangle

```
             CAVALRY
            /        \
           / charges   \
          / (+30% vs    \
         /   artillery)  \
        /                 \
ARTILLERY ←─────────── SQUARE FORMATION
  bombards               blunts cavalry
  (+50% vs square)       (-40% cav damage)
  overwatch (-3% atk)    +5% defense
                          vulnerable to artillery
```

**Player decisions this creates:**

1. **Enemy has cavalry?** → Form square. But check for enemy artillery first.
2. **Enemy has cavalry AND artillery?** → The Napoleonic dilemma. Square saves you from cavalry but artillery will punish you. Stay in line and risk the charge? Or form square and pray the guns miss?
3. **Where to put your artillery?** → Behind the front line (overwatch + bombardment range). SUPPORT a key marshal for auto-bombardment. Or HOLD for sustained fire.
4. **Enemy formed square?** → Bring up the guns! Bombardment +50%. Or charge with cavalry anyway and accept the -40%.
5. **How to break a fortified square?** → Artillery is the ONLY efficient answer. Combined arms: bombard the square, then cavalry charges the shaken remnants.

---

## Implementation Plan

### Session Structure: Two Sessions

**Session 67: Square Formation (Part A, ~40 tests)**
- `marshal.py`: `square_formation` field + serialization + `get_defense_modifier()` +5%
- `combat.py`: cavalry -40% and artillery +50% in `resolve_battle()` (target-type interactions)
- `executor.py`: `_execute_form_square()`, auto-break on move/attack, +50% in `_execute_bombardment()`
- `validation.py`: `form_square` + `break_square` in VALID_ACTIONS
- `llm_client.py`: mock parser keywords
- `world_state.py`: AP cost (1 for form_square, 0 for break_square), clear on broken/retreat in `_process_tactical_states()`
- `battle_report.py`: snapshot entries + observations
- `objection_v2.py`: 3 triggers (aggressive + cautious + already-fortified)
- `enemy_ai.py`: P2.5 square formation logic

**Session 68: Auto-Bombardment + Overwatch (Parts B + C, ~45 tests)**
- `executor.py`: auto-bombardment block in `_execute_attack()` before `resolve_battle()`
- `battle_report.py`: support bombardment observations
- `marshal.py`: `overwatch_penalty` transient field, applied in `get_attack_modifier()`
- `executor.py`: overwatch calculation in `_execute_attack()` (count enemy artillery in defender's region)
- `battle_report.py`: overwatch modifier in snapshot
- `enemy_ai.py`: overwatch factor in combat assessment

### Files Touched

| File | Session | Changes |
|------|---------|---------|
| `marshal.py` | 67, 68 | `square_formation` (serialized), `overwatch_penalty` (transient), modifier methods |
| `combat.py` | 67 | Square vs cavalry (-40%), artillery vs square (+50%) in resolve_battle |
| `executor.py` | 67, 68 | `_execute_form_square()`, auto-break, support auto-bombardment, overwatch calculation |
| `battle_report.py` | 67, 68 | Snapshot entries, 5-6 new observations |
| `enemy_ai.py` | 67, 68 | P2.5 square formation, overwatch in combat assessment |
| `objection_v2.py` | 67 | 3 new triggers |
| `validation.py` | 67 | `form_square`, `break_square` |
| `llm_client.py` | 67 | Mock parser keywords |
| `world_state.py` | 67 | AP cost, clear square on broken/retreat |

### Test Checklist

**Session 67 — Square Formation (~40):**
- [ ] Only infantry can form square (cavalry rejected, artillery rejected)
- [ ] Square reduces cavalry attack damage by 40% (in resolve_battle)
- [ ] Square increases artillery melee damage by 50% (in resolve_battle)
- [ ] Square increases bombardment damage by 50% (in _execute_bombardment)
- [ ] Square gives +5% defense modifier (in get_defense_modifier)
- [ ] Auto-break on attack order (square=False, attack proceeds)
- [ ] Auto-break on move order (square=False, move proceeds)
- [ ] Break square is free (0 AP)
- [ ] Form square costs 1 AP
- [ ] Square breaks on forced retreat
- [ ] Square breaks on marshal broken
- [ ] Square does NOT break on being attacked
- [ ] Square does NOT break on being bombarded
- [ ] Square persists across turns
- [ ] Square + fortify stack (both active simultaneously)
- [ ] Cavalry vs non-square infantry: no -40% (baseline unchanged)
- [ ] Artillery vs non-square infantry: no +50% (baseline unchanged)
- [ ] Infantry vs square: no special modifier (only cavalry/artillery interact)
- [ ] Serialization round-trip preserves square_formation
- [ ] Backward compat: old save loads with square_formation=False
- [ ] Battle report snapshot includes square modifiers
- [ ] Berthier observation: square held vs cavalry
- [ ] Berthier observation: square shelled by artillery
- [ ] Objection: aggressive infantry objects to form square (MODERATE)
- [ ] Objection: cautious infantry warns when artillery adjacent but no cavalry (MILD)
- [ ] Objection: form square when already fortified (MILD)
- [ ] AI forms square when cavalry adjacent, no artillery adjacent
- [ ] AI cautious forms square even when both cavalry AND artillery adjacent
- [ ] AI aggressive does NOT form square when both adjacent
- [ ] AI breaks square when no cavalry adjacent
- [ ] AI does NOT form square when already fortified
- [ ] Combat message: square vs cavalry shows "-40% cavalry damage" text
- [ ] Combat message: artillery vs square shows "+50% artillery bonus" text
- [ ] int() wrapping on all modifier values sent to API

**Session 68 — Auto-Bombardment (~25):**
- [ ] Artillery on SUPPORT fires bombardment before supported marshal's attack
- [ ] Auto-bombardment uses existing bombardment formula (same damage, terrain mods)
- [ ] Auto-bombardment respects bombardments_this_turn limit (2 max shared pool)
- [ ] Auto-bombardment increments bombardments_this_turn
- [ ] Auto-bombardment does NOT fire if artillery moved_this_turn
- [ ] Auto-bombardment does NOT fire if artillery is broken/retreating/recovering
- [ ] Auto-bombardment does NOT fire on defensive battles (supported marshal is defender)
- [ ] Auto-bombardment does NOT fire if artillery is not adjacent/co-located with battle region
- [ ] Auto-bombardment does NOT consume player AP
- [ ] Collateral damage rules apply (friendly fire possible)
- [ ] Fort degradation applies
- [ ] Bombardment streak increments
- [ ] Defender takes bombardment damage BEFORE resolve_battle
- [ ] Auto-bombardment result appears in combat output as preamble
- [ ] Multiple SUPPORT artillery can fire (each spends their own bombardment slot)
- [ ] Auto-bombardment does NOT fire on auto-charge (reckless cavalry)
- [ ] Berthier observation: effective support bombardment
- [ ] AI artillery on SUPPORT also auto-bombards (Building Blocks)
- [ ] Bombardment result includes all standard fields (fort degradation, collateral, etc.)

**Session 68 — Overwatch (~20):**
- [ ] Enemy artillery in defender's region applies -3% attack to attacker
- [ ] Multiple enemy artillery stack (-6% for 2)
- [ ] Cap at 3 artillery (-9% max overwatch)
- [ ] Broken/retreating/recovering artillery does NOT provide overwatch
- [ ] Artillery that moved_this_turn does NOT provide overwatch
- [ ] Overwatch does NOT apply to bombardment (ranged attack)
- [ ] Overwatch penalty appears in attacker's modifier list in battle report
- [ ] Overwatch is NOT counted toward coordination hard cap (it's a debuff, not a bonus)
- [ ] Transient field `overwatch_penalty` resets after combat
- [ ] overwatch_penalty NOT serialized (transient)
- [ ] AI factors overwatch into combat assessment
- [ ] Berthier observation when overwatch contributed to defense
- [ ] Overwatch applies to both player and AI attacks (Building Blocks)
- [ ] Overwatch from fortified artillery still applies
- [ ] int() wrapping on overwatch penalty value

---

## Design Decisions & Rationale

### Why -40% cavalry damage, not +40% defense vs cavalry?

Because it's an attacker-side modifier. The cavalry charge is *less effective*, not the square *more defended*. This keeps the modifier in the right conceptual bucket and avoids stacking confusion with defense modifiers.

### Why +50% artillery bonus and not just "artillery ignores square defense"?

Because historically, squares were WORSE than line against artillery. The packed formation gave gunners a dense target they couldn't miss. +50% captures this — the square actively hurts you against guns, not just fails to help.

### Why auto-break instead of blocking?

UX. If the player types "Davout, attack" and Davout is in square, the intent is clear — break square and attack. Forcing a separate "break square" command first is tedious busy-work that doesn't add strategic depth. The AP to form square is already spent; breaking is free.

### Why auto-bombardment only on offensive actions?

If the supported marshal is the DEFENDER, the artillery shouldn't fire blindly — the situation is chaotic, friendly positions unclear. Historically, preparatory bombardment preceded YOUR attack, not the enemy's. For defensive situations, the existing HOLD auto-bombardment already covers it.

### Why -3% overwatch per artillery, not -5%?

Overwatch is passive and free — it requires no action, no AP, no order. It should be meaningful enough to reward good positioning but not so strong that parking artillery makes a region impregnable. At -3%, a single artillery unit is a nuisance; combined with bombardment, SUPPORT bonuses, and combined arms, the full artillery package becomes formidable. At -5% a single unit would be too punishing for early game where each side has one artillery marshal.

### Why cap overwatch at 3 artillery (-9%)?

For 1805 scaling. With 80+ regions and potentially many artillery marshals, uncapped overwatch could create impenetrable defensive zones. -9% is meaningful but not game-breaking, especially since the coordination hard cap already limits how much total bonus a defender can accumulate.

---

## Gotchas

| Issue | Solution |
|-------|----------|
| Auto-bombardment + collateral on own supported marshal | Supported marshal could take friendly fire if co-located with defender. Working as designed — artillery fire is dangerous. Berthier should warn. |
| Square + auto-break + coordination context timing | Square breaks at START of _execute_attack, BEFORE coordination context. The square modifier no longer applies. This is correct — you're attacking, not in square anymore. |
| HOLD artillery vs SUPPORT artillery priority | HOLD auto-bombards during strategic phase. SUPPORT auto-bombards during attack execution. Different timing, no conflict. |
| AI forms square then immediately breaks to attack | P2.5 fires BEFORE P3+ attack priorities. If AI forms square this turn, it can't attack until next turn (square blocks attack). AI should only form square when NOT planning to attack — the P2.5 priority check should be a defensive-only decision. |
| Overwatch penalty on attacker who is also providing coordination | Attacker's coordination bonus and overwatch penalty are independent. Both apply. Attacker could have +13% coordination and -3% overwatch = net +10% effective bonus. |
| Square formation during coordinated battle | Square only affects the specific marshal in square, not their allies. If Davout is in square and Ney is in line, cavalry gets -40% against Davout but full damage against Ney. |
| Auto-bombardment fires, then battle resolves with casualties to bombardment target | Bombardment damage reduces defender strength BEFORE resolve_battle. This means the defender is weaker in the subsequent melee. Working as designed — that's the whole point. |

---

## Claude Code Implementation Notes

**Use Opus.** Three features touching combat resolution, executor flow, AI priorities, and the objection system simultaneously. The auto-bombardment timing in `_execute_attack()` is particularly delicate — it must fire AFTER coordination context (so we know who's attacking whom) but BEFORE `resolve_battle()` (so bombardment damage applies first).

**Code review checkpoint:** After Session 67 (Square Formation) passes all tests, review before starting Session 68. Square formation changes combat.py which is load-bearing.

**Do NOT modify `_calculate_coordination_context()` for overwatch.** Overwatch is conceptually separate from coordination — it's an enemy debuff, not a friendly bonus. Calculate it in a new helper `_calculate_overwatch()` called alongside coordination context.
