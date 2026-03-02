# Tactical Triangle — Design Spec

> **Status:** APPROVED — Ready for implementation
> **Ships as:** Two linked sessions (see Implementation Plan)
> **Prerequisite:** Phase 7 audit clean (Session 66 complete)
> **Estimated tests:** ~95
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

But then enemy guns open up. +50% bombardment damage. The packed formation shudders under the shells.

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
| Bombardment morale penalty | -15 extra morale loss | Men packed shoulder-to-shoulder watch shells tear through their ranks. Devastating to will. |
| Defense modifier | +5% | Tight formation, mutual support |
| Any active order | Auto-breaks square | Square is pure passive defense — any action means reorganizing |

### Where Effects Live (Golden Rule #1)

The +5% defense bonus goes in `marshal.py::get_defense_modifier()` — it's a marshal-intrinsic modifier.

The -40% cavalry reduction and +50% artillery bonus are **target-type interactions** — they go in `combat.py::resolve_battle()` alongside the existing cavalry counter block. They are NOT in `get_defense_modifier()` because they depend on the *attacker's* type, not just the defender's state.

```
marshal.py  → +5% defense (square_formation flag)
combat.py   → -40% cavalry damage / +50% artillery damage (target-type interaction)
executor.py → +50% bombardment damage + -15 extra morale loss (bombardment path, separate from resolve_battle)
```

### Square Auto-Break

**Any active order breaks square.** Square is pure passive defense — the instant a marshal does anything, the formation dissolves. For smooth UX, square does NOT block actions — it auto-breaks and the action proceeds:

```python
# At the TOP of every _execute_* function (attack, move, fortify, drill, recruit,
# garrison, stance_change — but NOT form_square, break_square, wait, end_turn):
if getattr(marshal, 'square_formation', False):
    marshal.square_formation = False
    # Prepend to message: "{name} breaks square formation."
```

**Actions that do NOT break square:**
- `form_square` (you're already in square)
- `break_square` (explicit break, handled separately)
- `wait` (the absence of action — staying in square IS waiting)
- `end_turn` (meta-action, not a marshal order)

**Actions that auto-break square:**
- Attack (breaks square, then attacks)
- Move (breaks square, then moves)
- Fortify (breaks square, then begins fortifying — they are mutually exclusive stances)
- Drill (breaks square, then drills)
- Recruit (breaks square, absorbs recruits)
- Garrison (breaks square, detaches garrison)
- Stance change (breaks square, changes stance)
- Any strategic command (breaks square, begins strategic order)

**Explicit break:** "break square" / "form line" = **free action (0 AP)**. Returning to default formation shouldn't cost an action.

**Forced break:** Square also breaks on:
- Forced retreat (morale collapse)
- Marshal broken
- NOT on being attacked (surviving attacks is the point)
- NOT on being bombarded (you suffer +50% and -15 morale but the square holds)

### Square + Fortify Interaction

**Mutually exclusive.** Forming square auto-breaks fortification; fortifying auto-breaks square. They represent different physical postures — a square is a tight packed formation with bayonets outward, while fortification is troops spread across entrenchments. You can't be in both.

This is a core strategic tradeoff:
- **Fortify:** Higher raw defense (up to +20%), good against everything, but no cavalry-specific counter. Requires multiple turns to build.
- **Square:** Lower base defense (+5%), but the -40% cavalry damage reduction is devastating against mounted charges. Instant (1 AP). Extremely vulnerable to artillery (+50% damage, -15 morale on bombardment).

The player must read the battlefield and commit to one posture. This prevents the degenerate case of a fortified square with ~2.0x defense that would make positions truly impregnable.

### Square + Coordination

**Defense coordination only.** A marshal in square follows the same coordination rule as fortified marshals (MULTI_MARSHAL_SPEC §3 Fortification Rule): they provide **defense** coordination to allies but are excluded from **attack** coordination. A marshal locked into a tight defensive square cannot coordinate offensive operations — they're focused entirely on holding the bayonet wall.

- Combined arms: square marshal's unit type still counts (physical presence)
- Per-ally coordination: defense contribution only (attack contribution = 0)
- Dedicated coordination: defense only
- Adjacent support: 0% (marshal in square cannot project offensive pressure to adjacent regions)

### Square + Strategic Orders

**Forming square cancels any active strategic order.** SUPPORT, MOVE_TO, PURSUE, and HOLD all require the ability to move or engage. A marshal committing to square is committing to fixed passive defense, which is incompatible with any strategic order.

```python
# In _execute_form_square():
if marshal.strategic_order:
    order_type = marshal.strategic_order.command_type
    marshal.strategic_order = None
    if order_type == "HOLD":
        marshal.holding_position = False
        marshal.hold_region = ""
    # Message: "{name} abandons {order_type} orders to form square."
```

Berthier advisory when this happens: *"Sire, {name} has abandoned the {order_type} order to form square. They cannot march while in this formation."*

### Square + Reinforcement

**A marshal in square cannot reinforce.** Add reinforcement eligibility rule #15:

> *"15. NOT `square_formation` — a marshal in square is locked into fixed defensive posture and cannot march to reinforce"*

Consistent with rule #7 (fortified marshals can't reinforce). If the player wants the marshal available for reinforcement, they must break square first (free action, 0 AP) before the next battle.

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
| Cautious infantry | Form square when already fortified | MILD | "We've spent days building these earthworks, Sire. The square would abandon them for less protection." |
| Any infantry | Form square when enemy artillery adjacent AND cavalry adjacent | MILD | "Both cavalry and guns threaten us, Sire. The square stops the horses but invites the shells." |

### AI Behavior

New priority: **P2.5 — Form Square** (between existing P2 engagement checks and P3 counter-punch):

```
IF infantry AND NOT cavalry AND NOT artillery:

    # ─── BREAK SQUARE CHECK (always first) ───
    IF in_square:
        adjacent_cavalry = enemy cavalry within 1 region
        IF NOT adjacent_cavalry:
            → break_square (no longer needed)
            RETURN  # Don't re-form on the same turn

    # ─── FORM SQUARE CHECK ───
    IF NOT in_square:
        # Anti-oscillation: cooldown after breaking square
        IF ai_square_cooldown > 0:
            → skip (recently broke square, wait before re-forming)

        adjacent_cavalry = enemy cavalry within 1 region
        adjacent_artillery = enemy artillery within 1 region

        IF adjacent_cavalry AND NOT adjacent_artillery:
            → form_square (clear choice: cavalry threatens, no artillery risk)

        IF adjacent_cavalry AND adjacent_artillery:
            → personality decision:
                cautious → form_square (survive the charge, accept shelling)
                aggressive → stay in line (prefer attacking)
                literal → form_square (default safe choice)
```

**Anti-oscillation field:** `ai_square_cooldown: int = 0` on Marshal (transient, NOT serialized). Set to 2 when AI breaks square. Decremented each turn in `_process_tactical_states()`. Prevents the form→break→form loop that wastes 1 AP per cycle. Mirrors the existing `ai_refortify_cooldown` pattern.

```python
# In _process_tactical_states(), alongside refortify cooldown:
if getattr(marshal, 'ai_square_cooldown', 0) > 0:
    marshal.ai_square_cooldown -= 1
```

**AI does NOT form square when:**
- Already fortified (fortify provides defense, square would abandon those earthworks and make them an artillery target)
- Attacking (aggressive AI stays in line to attack)
- Only artillery threatens (square makes it WORSE)
- `ai_square_cooldown > 0` (recently broke square — wait for situation to stabilize)
- Broken, retreating, or recovering

**AI square under sustained bombardment:** If an AI marshal is in square AND has taken bombardment damage this turn (via `bombardment_received_this_turn` flag or similar), cautious AI should break square next turn even if cavalry is still adjacent. Being shelled in square is devastating — better to risk the cavalry than continue absorbing +50% bombardment + -15 morale per hit. Aggressive AI breaks square immediately (prefers to attack). Literal AI stays in square (follows the formation as ordered).

```
# Post-bombardment square evaluation (inside P2.5):
IF in_square AND took_bombardment_this_turn:
    IF aggressive → break_square (going to attack the guns)
    IF cautious AND bombardment_casualties > 10% strength → break_square (unsustainable)
    IF literal → stay in square (orders are orders)
```

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
        IF defender in square: apply -15 extra morale penalty to defender
        Append result to pre_battle_messages
        Defender takes bombardment damage BEFORE resolve_battle()

        ── EARLY-EXIT: DEAD-DEFENDER CHECK (inside loop) ──
        IF defender.strength <= 0:
            Break loop — no point shelling a dead force.

── POST-LOOP: DEAD-DEFENDER CHECK ──
IF defender.strength <= 0 after auto-bombardment loop:
    Skip resolve_battle() entirely.
    Declare attacker victory with 0 attacker casualties.
    Handle advance/capture normally.
    Message: "The preparatory bombardment destroyed {defender}. {attacker} advances unopposed."
    Return early — no need for combat resolution.

[existing: resolve_battle()]
```

**Bombardment morale punishment vs square:** When a marshal in square is bombarded (auto-bombardment or manual), they suffer an extra **-15 morale penalty** on top of normal morale loss. This is applied in `_execute_bombardment()` when `defender.square_formation == True`:

```python
# In _execute_bombardment(), after applying damage:
if getattr(defender, 'square_formation', False):
    defender.adjust_morale(-15)  # Extra morale shock from shelling packed ranks
    # Message: "The packed square shudders under the bombardment — men break and run!"
```

At -15 per bombardment, a marshal starting at 75 morale hits forced retreat threshold (25) after ~3 bombardments even without other combat. Combined with the +50% damage bonus, being in square under artillery fire is catastrophic. This creates intense pressure to break square when guns open up — which is exactly the Napoleonic dilemma.

**Fog of war note:** When auto-bombardment fires from an adjacent region, the defender gains PARTIAL intel on the source region (shells came from that direction). Update defender's intel store: `update_intel_from_bombardment(source_region, PARTIAL)`.

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

In practice for the player: if Drouot is in Belgium and Wellington attacks Belgium, Wellington gets -3% attack. If Ney attacks a region where enemy artillery is stationed, Ney gets -3%.

**Where it lives (Golden Rule #1):**

**New transient field on attacker:** `overwatch_penalty: float = 0.0`
Applied in `get_attack_modifier()` as `modifier *= (1.0 - self.overwatch_penalty)`

**Calculated in:** `_execute_attack()`, alongside coordination context, via new helper `_calculate_overwatch()`. Count enemy artillery in the defender's region, set overwatch_penalty on the **primary attacker AND all same-nation attacking allies** in the battle. The entire attacking force suffers overwatch, not just the commander.

```python
def _calculate_overwatch(self, attacker, attacking_allies, defender_region, world):
    """Count enemy artillery in defender's region, apply overwatch to all attackers."""
    enemy_artillery_count = 0
    for m in world.marshals.values():
        if (m.location == defender_region
                and m.nation != attacker.nation
                and getattr(m, 'artillery', False)
                and m.strength > 0
                and not getattr(m, 'broken', False)
                and not getattr(m, 'retreated_this_turn', False)
                and getattr(m, 'retreat_recovery', 0) == 0
                and not getattr(m, 'moved_this_turn', False)):
            enemy_artillery_count += 1

    capped = min(enemy_artillery_count, 3)
    penalty = capped * 0.03

    # Apply to ALL attackers — the guns suppress the entire assault
    for combatant in [attacker] + attacking_allies:
        combatant.overwatch_penalty = penalty
```

**Constraints:**
- Only non-broken, non-retreating, non-recovering artillery counts
- Artillery that `moved_this_turn` does NOT provide overwatch (guns not set up yet)
- Stacks up to 3 artillery max (-9% cap — prevents degenerate stacking in 1805)
- Does NOT apply to bombardment (ranged fire isn't affected by local overwatch)
- Does NOT apply to the artillery marshal itself defending in melee (that's already covered by the cavalry counter)
- **Two-artillery mutual overwatch:** If Drouot and another artillery are co-located, Drouot provides overwatch when the other is attacked and vice versa. Each artillery is excluded only from its own defense, not from providing overwatch for allies.

### Interaction with Existing Systems

| System | Interaction |
|--------|-------------|
| **Coordination hard cap** | Overwatch is NOT a coordination bonus — it's an enemy debuff. Does not count toward the +25%/+20% cap. |
| **Combined arms** | Independent. Combined arms rewards YOUR composition; overwatch punishes the ENEMY's exposure to your guns. |
| **Fortification** | Artillery in a fortified position still provides overwatch. Being dug in doesn't stop the guns from firing. |
| **AI combat assessment** | AI factors overwatch into `_evaluate_target_ratio()`: `overwatch_count = min(enemy_artillery_in_target, 3); effective_ratio *= (1.0 - overwatch_count * 0.03)`. This makes AI less eager to attack regions with artillery — -3% per gun in the threat math. |
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
2. **Enemy has cavalry AND artillery?** → The Napoleonic dilemma. Square saves you from cavalry but artillery will devastate you (+50% damage, -15 morale per bombardment). Stay in line and risk the charge? Or form square and pray the guns miss? Or fortify instead for general defense and accept the cavalry risk?
3. **Square or Fortify?** → They're mutually exclusive. Square is instant anti-cavalry but fragile under bombardment. Fortify takes turns but provides stronger overall defense. The correct choice depends on what's threatening you RIGHT NOW.
4. **Where to put your artillery?** → Behind the front line (overwatch + bombardment range). SUPPORT a key marshal for auto-bombardment. Or HOLD for sustained fire.
5. **Enemy formed square?** → Bring up the guns! Bombardment +50%, -15 morale. After 2-3 bombardments the square's morale collapses into forced retreat. Then cavalry charges the shaken remnants.

---

## Implementation Plan

### Session Structure: Two Sessions

**Session 67: Square Formation (Part A, ~45 tests)**
- `marshal.py`: `square_formation` field + serialization + `get_defense_modifier()` +5%
- `combat.py`: cavalry -40% and artillery +50% in `resolve_battle()` (target-type interactions)
- `executor.py`: `_execute_form_square()` (cancel strategic orders, break fortify), auto-break on ALL active actions (attack/move/fortify/drill/recruit/garrison/stance_change), +50% damage + -15 morale in `_execute_bombardment()`, reinforcement eligibility rule #15
- `validation.py`: `form_square` + `break_square` in VALID_ACTIONS
- `llm_client.py`: mock parser keywords
- `world_state.py`: AP cost (1 for form_square, 0 for break_square), clear on broken/retreat in `_process_tactical_states()`, `ai_square_cooldown` decrement
- `battle_report.py`: snapshot entries + observations
- `objection_v2.py`: 4 triggers (aggressive + cautious-no-cavalry + cautious-loses-fortify + both-threats)
- `enemy_ai.py`: P2.5 square formation logic + anti-oscillation cooldown + bombardment break evaluation

**Session 68: Auto-Bombardment + Overwatch (Parts B + C, ~50 tests)**
- `executor.py`: auto-bombardment block in `_execute_attack()` before `resolve_battle()`, dead-defender check after auto-bombardment, fog intel update for adjacent bombardment source
- `battle_report.py`: support bombardment observations
- `marshal.py`: `overwatch_penalty` transient field, applied in `get_attack_modifier()`
- `executor.py`: `_calculate_overwatch()` helper — count enemy artillery in defender's region, apply to ALL attacking participants
- `battle_report.py`: overwatch modifier in snapshot
- `enemy_ai.py`: overwatch factor in `_evaluate_target_ratio()` (concrete -3% per gun formula)

### Files Touched

| File | Session | Changes |
|------|---------|---------|
| `marshal.py` | 67, 68 | `square_formation` (serialized), `overwatch_penalty` (transient), `ai_square_cooldown` (transient), modifier methods |
| `combat.py` | 67 | Square vs cavalry (-40%), artillery vs square (+50%) in resolve_battle |
| `executor.py` | 67, 68 | `_execute_form_square()` (cancel strategic orders, break fortify), auto-break in ALL _execute_* functions, +50% damage + -15 morale in bombardment, reinforcement eligibility rule #15, support auto-bombardment, dead-defender check, `_calculate_overwatch()`, fog intel update |
| `battle_report.py` | 67, 68 | Snapshot entries, 7-8 new observations |
| `enemy_ai.py` | 67, 68 | P2.5 square formation + anti-oscillation + bombardment break evaluation, overwatch in `_evaluate_target_ratio()` |
| `objection_v2.py` | 67 | 4 new triggers |
| `validation.py` | 67 | `form_square`, `break_square` |
| `llm_client.py` | 67 | Mock parser keywords |
| `world_state.py` | 67 | AP cost, clear square on broken/retreat, `ai_square_cooldown` decrement in `_process_tactical_states()` |

### Test Checklist

**Session 67 — Square Formation (~45):**

*Core mechanics:*
- [ ] Only infantry can form square (cavalry rejected, artillery rejected)
- [ ] Square reduces cavalry attack damage by 40% (in resolve_battle)
- [ ] Square increases artillery melee damage by 50% (in resolve_battle)
- [ ] Square increases bombardment damage by 50% (in _execute_bombardment)
- [ ] Square bombardment applies -15 extra morale penalty (in _execute_bombardment)
- [ ] Square gives +5% defense modifier (in get_defense_modifier)
- [ ] Break square is free (0 AP)
- [ ] Form square costs 1 AP
- [ ] Square persists across turns (if no action taken)
- [ ] Cavalry vs non-square infantry: no -40% (baseline unchanged)
- [ ] Artillery vs non-square infantry: no +50% (baseline unchanged)
- [ ] Infantry vs square: no special modifier (only cavalry/artillery interact)
- [ ] Auto-charge cavalry into square: -40% applies (resolve_battle path)

*Auto-break — any active order breaks square:*
- [ ] Auto-break on attack order (square=False, attack proceeds)
- [ ] Auto-break on move order (square=False, move proceeds)
- [ ] Auto-break on fortify order (square=False, fortify proceeds)
- [ ] Auto-break on drill order (square=False, drill proceeds)
- [ ] Auto-break on recruit order (square=False, recruit proceeds)
- [ ] Auto-break on garrison order (square=False, garrison proceeds)
- [ ] Auto-break on stance change (square=False, stance changes)
- [ ] Auto-break on strategic command (square=False, order set, Berthier advisory)
- [ ] Square breaks on forced retreat
- [ ] Square breaks on marshal broken
- [ ] Square does NOT break on being attacked
- [ ] Square does NOT break on being bombarded (suffers +50% and -15 morale, but holds)

*Mutual exclusion with fortify:*
- [ ] Form square while fortified: breaks fortify, enters square, message warns
- [ ] Fortify while in square: breaks square, begins fortifying
- [ ] Square + fortify NEVER simultaneously true

*Strategic order interaction:*
- [ ] Form square cancels active SUPPORT order
- [ ] Form square cancels active MOVE_TO order
- [ ] Form square cancels active PURSUE order
- [ ] Form square cancels active HOLD order (clears holding_position + hold_region)
- [ ] Berthier advisory when strategic order canceled by square

*Coordination interaction:*
- [ ] Square marshal provides defense-only coordination (like fortified)
- [ ] Square marshal provides 0% attack coordination
- [ ] Square marshal provides 0% adjacent support (can't project offensive pressure)
- [ ] Square marshal unit type still counts for combined arms

*Reinforcement interaction:*
- [ ] Marshal in square cannot reinforce (eligibility rule #15 blocks)

*Serialization:*
- [ ] Serialization round-trip preserves square_formation
- [ ] Backward compat: old save loads with square_formation=False

*Battle report:*
- [ ] Battle report snapshot includes square modifiers
- [ ] Berthier observation: square held vs cavalry
- [ ] Berthier observation: square shelled by artillery
- [ ] Combat message: square vs cavalry shows "-40% cavalry damage" text
- [ ] Combat message: artillery vs square shows "+50% artillery bonus" text

*Objections:*
- [ ] Objection: aggressive infantry objects to form square (MODERATE)
- [ ] Objection: cautious infantry warns when artillery adjacent but no cavalry (MILD)
- [ ] Objection: cautious infantry warns when losing fortification to square (MILD)
- [ ] Objection: any infantry warned when both cavalry and artillery adjacent (MILD)

*AI behavior:*
- [ ] AI forms square when cavalry adjacent, no artillery adjacent
- [ ] AI cautious forms square even when both cavalry AND artillery adjacent
- [ ] AI aggressive does NOT form square when both adjacent
- [ ] AI breaks square when no cavalry adjacent
- [ ] AI does NOT form square when already fortified
- [ ] AI anti-oscillation: does NOT re-form square within 2 turns of breaking
- [ ] AI cautious breaks square after heavy bombardment (>10% casualties)
- [ ] AI aggressive breaks square after any bombardment

*Safety:*
- [ ] int() wrapping on all modifier values sent to API

**Session 68 — Auto-Bombardment (~28):**
- [ ] Artillery on SUPPORT fires bombardment before supported marshal's attack
- [ ] Auto-bombardment uses existing bombardment formula (same damage, terrain mods)
- [ ] Auto-bombardment vs square: +50% damage AND -15 extra morale
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
- [ ] Dead-defender check: if defender.strength <= 0 after bombardment, skip resolve_battle, declare victory
- [ ] Auto-bombardment result appears in combat output as preamble
- [ ] Multiple SUPPORT artillery can fire (each spends their own bombardment slot)
- [ ] Auto-bombardment does NOT fire on auto-charge (reckless cavalry)
- [ ] Berthier observation: effective support bombardment
- [ ] AI artillery on SUPPORT also auto-bombards (Building Blocks)
- [ ] Bombardment result includes all standard fields (fort degradation, collateral, etc.)
- [ ] Fog: auto-bombardment from adjacent region gives defender PARTIAL intel on source region

**Session 68 — Overwatch (~22):**
- [ ] Enemy artillery in defender's region applies -3% attack to attacker
- [ ] Overwatch applies to ALL attacking participants (primary + allies), not just primary
- [ ] Multiple enemy artillery stack (-6% for 2)
- [ ] Cap at 3 artillery (-9% max overwatch)
- [ ] Broken/retreating/recovering artillery does NOT provide overwatch
- [ ] Artillery that moved_this_turn does NOT provide overwatch
- [ ] Overwatch does NOT apply to bombardment (ranged attack)
- [ ] Overwatch penalty appears in attacker's modifier list in battle report
- [ ] Overwatch is NOT counted toward coordination hard cap (it's a debuff, not a bonus)
- [ ] Transient field `overwatch_penalty` resets after combat
- [ ] overwatch_penalty NOT serialized (transient)
- [ ] Two-artillery mutual overwatch: artillery A provides overwatch when B is attacked
- [ ] AI uses overwatch in `_evaluate_target_ratio()` (-3% per gun in ratio calculation)
- [ ] Berthier observation when overwatch contributed to defense
- [ ] Overwatch applies to both player and AI attacks (Building Blocks)
- [ ] Overwatch from fortified artillery still applies
- [ ] Overwatch from square artillery: N/A (artillery cannot form square)
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

### Why are square and fortify mutually exclusive?

They represent physically different formations. A square is troops packed tight with bayonets facing outward in every direction. Fortification is troops spread across earthworks, trenches, and prepared positions. You cannot be in a tight packed square inside a trench — the geometry doesn't work.

Mechanically, stacking them would create ~2.0x defense modifiers that make positions truly impregnable against non-artillery attacks. Mutual exclusion forces a real choice: instant anti-cavalry protection (square) or gradual strong defense (fortify). This tradeoff is the core of Napoleonic tactical decision-making.

### Why -15 morale penalty for bombardment vs square?

Being shelled in a packed square is among the most psychologically devastating experiences in Napoleonic warfare. Men stand shoulder-to-shoulder watching cannonballs tear through their ranks, unable to spread out or take cover because the cavalry is waiting for them to break formation. The -15 morale penalty (on top of +50% damage) means a square under sustained bombardment will hit forced retreat threshold (morale 25) within 2-3 hits. This creates intense pressure to break square — which is exactly the Napoleonic dilemma. The player must decide: break square and risk the cavalry, or hold square and watch morale collapse under the guns.

### Why does any action break square?

Square formation is a pure defensive posture. The moment you order troops to do anything — attack, dig in, drill, march — they must reorganize out of the tight square. There is no "I'll stay in square while also fortifying" — those are contradictory physical actions. This also prevents exploit stacking (form square, then fortify on top, etc.) and keeps square as the temporary reactive formation it historically was.

---

## Gotchas

| Issue | Solution |
|-------|----------|
| Auto-bombardment + collateral on own supported marshal | Supported marshal could take friendly fire if co-located with defender. Working as designed — artillery fire is dangerous. Berthier should warn. |
| Square + auto-break + coordination context timing | Square breaks at START of _execute_attack, BEFORE coordination context. The square modifier no longer applies. This is correct — you're attacking, not in square anymore. |
| HOLD artillery vs SUPPORT artillery priority | HOLD auto-bombards during strategic phase. SUPPORT auto-bombards during attack execution. Different timing, no conflict. |
| AI forms square then immediately breaks to attack | P2.5 fires BEFORE P3+ attack priorities. If AI forms square this turn, it can't attack until next turn (all actions break square). AI should only form square when NOT planning to attack — the P2.5 priority check should be a defensive-only decision. |
| Overwatch penalty on attacker who is also providing coordination | Attacker's coordination bonus and overwatch penalty are independent. Both apply. Attacker could have +13% coordination and -3% overwatch = net +10% effective bonus. |
| Square formation during coordinated battle | Square only affects the specific marshal in square, not their allies. If Davout is in square and Ney is in line, cavalry gets -40% against Davout but full damage against Ney. |
| Auto-bombardment fires, then battle resolves with casualties to bombardment target | Bombardment damage reduces defender strength BEFORE resolve_battle. This means the defender is weaker in the subsequent melee. Working as designed — that's the whole point. |
| Auto-bombardment destroys defender (strength → 0) | Early-exit inside bombardment loop (break on first kill), then post-loop dead-defender check skips resolve_battle. Declare attacker victory with 0 casualties, handle advance/capture normally. |
| `wait` action breaks square | It must NOT. `wait` is the absence of action — staying in square IS waiting. Exclude `wait`, `end_turn`, `form_square`, `break_square` from auto-break. |
| Multiple SUPPORT artillery overkill dead target | Early-exit inside the for-each loop: `if defender.strength <= 0: break`. Remaining artillery keep their bombardment slot unspent. |
| Square + fortify attempted simultaneously | Mutually exclusive — forming square breaks fortify, fortifying breaks square. Cannot stack. |
| AI square oscillation (form → break → form) | `ai_square_cooldown = 2` set on break. Prevents re-forming for 2 turns. Mirrors `ai_refortify_cooldown`. |
| AI shelled in square and stuck | Post-bombardment evaluation: cautious AI breaks after >10% casualties from bombardment, aggressive AI breaks immediately. Literal AI stays (orders are orders). |
| Square marshal reinforces battle (contradiction) | Eligibility rule #15 blocks. Square marshal cannot march. Break square first (free, 0 AP). |
| Square + SUPPORT/MOVE_TO order | Form square cancels any active strategic order. Berthier advisory warns. |
| Square + coordination: attack or defense? | Defense coordination only (like fortified). Square marshal cannot coordinate attacks or provide adjacent support. Combined arms type still counts. |
| Overwatch applies to primary only | Set `overwatch_penalty` on ALL attacking participants, not just primary. Enemy guns suppress the entire attacking force. |
| Same-side artillery mutual overwatch | Artillery A provides overwatch when B is attacked. Each excluded from its own defense only. |
| Auto-bombardment from adjacent + fog | Defender gains PARTIAL intel on artillery's source region. |

---

## Claude Code Implementation Notes

**Use Opus.** Three features touching combat resolution, executor flow, AI priorities, and the objection system simultaneously. The auto-bombardment timing in `_execute_attack()` is particularly delicate — it must fire AFTER coordination context (so we know who's attacking whom) but BEFORE `resolve_battle()` (so bombardment damage applies first).

**Code review checkpoint:** After Session 67 (Square Formation) passes all tests, review before starting Session 68. Square formation changes combat.py which is load-bearing.

**Do NOT modify `_calculate_coordination_context()` for overwatch.** Overwatch is conceptually separate from coordination — it's an enemy debuff, not a friendly bonus. Calculate it in a new helper `_calculate_overwatch()` called alongside coordination context.

**Auto-break pattern:** The square auto-break check must go at the TOP of every `_execute_*` function (attack, move, fortify, drill, recruit, garrison, stance_change). **Explicitly excluded:** `form_square`, `break_square`, `wait`, `end_turn`. Extract to a shared helper to avoid code duplication:

```python
def _auto_break_square(self, marshal) -> str:
    """Break square formation if active. Returns message or empty string."""
    if getattr(marshal, 'square_formation', False):
        marshal.square_formation = False
        return f"{marshal.name} breaks square formation. "
    return ""
```

**Fortify mutual exclusion:** In `_execute_form_square()`, check and clear fortification state. In `_execute_fortify()`, the auto-break helper handles it (square breaks on fortify action). But the form_square direction also needs explicit fortify clearing:

```python
# In _execute_form_square():
if getattr(marshal, 'fortified', False):
    marshal.fortified = False
    marshal.defense_bonus = 0.0
    # Message: "{name} abandons fortified position to form square."
```

**AI anti-oscillation:** Add `ai_square_cooldown` as a transient field (NOT serialized, NOT in `__init__`). Set via `setattr` when AI breaks square, read via `getattr(..., 0)`. Decrement in `_process_tactical_states()`. Same pattern as `ai_refortify_cooldown`.

**Morale penalty implementation:** The -15 morale penalty for bombardment vs square is applied in `_execute_bombardment()` AFTER damage calculation, guarded by `defender.square_formation`. This is separate from the +50% damage modifier (which affects strength). Both apply: the square makes you take more physical damage AND more psychological damage from shelling.

**Dead-defender check:** Early-exit INSIDE the auto-bombardment for-each loop: `if defender.strength <= 0: break`. Then after the loop, check `defender.strength <= 0`. If true, construct a victory result dict manually (mirror the structure of resolve_battle's return dict) and skip the resolve_battle call entirely. Handle advance/capture with existing post-battle logic. The inner break prevents wasting bombardment slots on a dead force; the outer check triggers the skip-resolve path.

**Estimated tests after changes:** Session 67 ~45, Session 68 ~50. Total ~95 (up from ~85).
