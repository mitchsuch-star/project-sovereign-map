# Bombardment System Specification

<!-- v3 audit notes (Session 47):
  Changes from v2 → v3:
  - §3: Clarified routing does NOT apply to garrison combat (P4.25). Artillery cannot bombard garrisons.
  - §4.4: CUT area bombardment entirely. Targeted + collateral is sufficient. Removed area formula,
    parser region-name routing, and area_bombardment result field. "Drouot, bombard Waterloo" now
    auto-targets strongest enemy in region (or asks which if ambiguous).
  - §4.4: Added disambiguation rule: marshal names take priority over region names for target matching.
  - §4.4: Added note: collateral affects marshals only (not capital garrisons or detachments).
  - §4.4: Added note: friendly fire trust drop can trigger redemption event at threshold.
  - §4.5: Fixed reset location: advance_turn() per-marshal loop (alongside attacks_this_turn), NOT
    _process_tactical_states().
  - §8: Removed area_bombardment field from event log.
  - §9.3: Added arrival-turn note (marshal moves to position on turn 1, bombardment starts turn 2).
  - §9.6: Added note: bombardment_target clears gracefully on dangling reference (handled by lookup).
  - §10.1: Added note: P4.25 garrison assault skipped for ranged artillery. Added explicit P0 note.
  - §10.2: Added terrain_mod as tertiary sort key for target selection.
  - §12.1: Removed area_bombardment from Godot result dict.
  - §15: Removed parser.py from files-to-modify (no region-name routing needed).
  - §17: Removed area bombardment test cases. Added garrison-skip and redemption-threshold tests.
-->

> **Phase 6.5 — Artillery Bombardment Redesign**
> **Status:** DRAFT v3 — Second Audit Pass
> **Author:** Mitch + Claude (Opus), Sessions 45-47
> **Depends on:** Artillery Unit Type (Sessions 42-44), Combat System, Objection V2
> **Feeds into:** Berthier Reports, Event Log, Godot HUD, Strategic Commands, Enemy AI

---

## 1. Core Problem

Ranged bombardment (artillery attacking from an adjacent region) currently runs through the same `resolve_battle()` pipeline as a pitched melee engagement. This produces nonsensical outcomes:

- Artillery **"loses"** a bombardment it fired from safety
- Wellington earns **counter-punch** from being shelled (he wasn't in melee)
- Drouot takes a **morale hit** for "losing" when his guns were never in danger
- **20% casualties** from range when counter-battery fire should be minimal
- The **strength ratio** of the target inflates return fire unrealistically

**Fix:** Separate bombardment into its own resolution path. Same-region combat remains a full battle.

---

## 2. Design Philosophy

Artillery's identity in the unit type triangle:

| Unit Type | Role | Risk | Reward |
|-----------|------|------|--------|
| **Infantry** | Takes and holds ground, fights decisive battles | Medium | High — captures regions, wins battles |
| **Cavalry** | Fast strikes, devastating charges, physically commits | High | Very High — recklessness, glorious charge, 2-tile reach |
| **Artillery** | Grinds from range, cracks forts, softens targets | Low | Low-Medium — slow attrition, fort degradation, safe |

The player's strategic choice: commit artillery to a real battle (risky but decisive) or keep them safe bombarding (slow but low-risk). Artillery **clears the way**, infantry **captures**.

**Collateral principle:** Shells are imprecise. Bombardment is area-of-effect — it hits a region, not a general's tent. Multiple forces in the same region all take fire, including friendlies caught in the blast zone.

---

## 3. Routing Rule

**The executor decides which path based on location:**

```
IF artillery attacks AND attacker.location != defender.location:
    → Bombardment resolution (this spec)
ELSE:
    → Full resolve_battle() (unchanged)
```

**Command handling:** The player command is "attack" — the executor routes internally based on location. The parser treats "bombard," "shell," "barrage," and "cannonade" as synonyms for "attack" (existing mock parser keywords). No new action type in VALID_ACTIONS — bombardment is an attack variant, not a separate action.

**Garrison combat exclusion:** This routing rule only applies when the target is a marshal. Garrison attacks (target = region name) go through `_resolve_garrison_combat()` regardless of distance. Artillery **cannot bombard garrisons** — garrison combat requires physical presence (same-region). The AI's P4.25 garrison assault is skipped for artillery that hasn't moved into the target region (see §10.1).

This is transparent to the AI, parser, and player.

---

## 4. Bombardment Resolution

### 4.1 Terrain Bombardment Modifier

Terrain affects how effective bombardment is. Open terrain offers no protection from shells; forests and hills provide concealment and defilade; mountains provide significant cover behind ridgelines; urban areas have buildings to shelter in.

```python
TERRAIN_BOMBARDMENT_MODIFIER = {
    "plains": 1.10,          # +10% damage — open ground, no cover
    "forest": 0.80,          # -20% damage — trees obscure targets
    "hills": 0.75,           # -25% damage — defilade behind ridgelines
    "mountains": 0.60,       # -40% damage — deep cover, hard to range
    "urban": 0.70,           # -30% damage — buildings provide shelter
    "river_crossing": 1.0,   # No modifier — rivers don't help vs shells
}
```

**Single source of truth:** Define in `region.py` alongside existing terrain tables.

**Note:** This modifier applies ONLY to bombardment damage dealt to the defender. Return casualties (§4.3) are unaffected by terrain — counter-battery wear happens to the guns regardless.

### 4.2 Damage Dealt to Defender (Targeted Bombardment)

When the player targets a specific marshal ("Drouot, attack Wellington"), the primary target takes full bombardment damage:

```python
base_rate = 0.04  # 4% of defender's strength
shock_skill = artillery_marshal.get_effective_skill("shock")
damage_multiplier = 1.0 + (shock_skill / 15.0)
terrain_mod = TERRAIN_BOMBARDMENT_MODIFIER.get(defender_region.terrain, 1.0)

raw_damage = defender.strength * base_rate * damage_multiplier * terrain_mod
variance = random.uniform(0.80, 1.20)  # ±20% randomness
defender_casualties = int(raw_damage * variance)
```

**Example — Drouot (shock 7) bombards Wellington (68,000) on plains:**
- base: 68,000 × 0.04 = 2,720
- shock multiplier: 1.0 + (7 / 15) = 1.467
- terrain: plains = 1.10
- raw: 2,720 × 1.467 × 1.10 = 4,389
- with variance: ~3,511 to ~5,267 casualties per bombardment

**Example — Drouot bombards Wellington (68,000) in mountains:**
- raw: 2,720 × 1.467 × 0.60 = 2,394
- with variance: ~1,915 to ~2,873 (much less effective)

### 4.3 Return Casualties (Counter-Battery / Wear)

Fixed small percentage of **artillery's own** army:

```python
return_rate = 0.015  # 1.5% of own strength
variance = random.uniform(0.80, 1.20)
attacker_casualties = int(artillery.strength * return_rate * variance)
```

**Example — Drouot (25,000):**
- base: 25,000 × 0.015 = 375
- with variance: ~300 to ~450 casualties per bombardment

This represents counter-battery fire, gun wear, logistics attrition — not melee losses. Terrain does NOT affect return casualties.

### 4.4 Collateral Damage

Shells are imprecise. When bombardment hits a region, **other forces in that region** have a chance of taking collateral damage — including friendly units.

**All bombardment is targeted.** The player names a specific marshal to bombard. If the player names a region ("bombard Waterloo"), the parser auto-selects the strongest enemy marshal in that region as the primary target. If multiple enemies are present and ambiguity exists, Berthier asks which target. There is no separate "area bombardment" mode.

**Target disambiguation:** Marshal names always take priority over region names. If a target string matches both a marshal and a region (unlikely in base game but possible with mods), treat as targeted bombardment against the marshal.

#### Collateral Damage Formula

```python
# For each non-primary MARSHAL in target region:
collateral_chance = 0.40  # 40% chance per force
collateral_rate = 0.25    # 25% of primary damage

if random.random() < collateral_chance:
    collateral_raw = primary_raw_damage * collateral_rate
    collateral_variance = random.uniform(0.80, 1.20)
    collateral_casualties = int(collateral_raw * collateral_variance)
    force.take_casualties(collateral_casualties)
```

**Scope:** Collateral affects **marshals only**. Capital garrisons and player garrison detachments (region attributes, not marshal objects) are not affected by collateral. They are structural defenses, not field armies in the blast zone.

#### Friendly Fire

When collateral hits a friendly force:
- Casualties apply normally (no protection for being allied)
- Event log includes `"friendly_fire": True` flag
- Berthier observation: "Sire, our own forces at {region} were caught in {marshal}'s bombardment. {casualties} casualties from friendly fire."
- **Trust penalty:** Friendly marshal hit by bombardment loses -5 trust with the player (you shelled their troops)
- **Relationship penalty:** Friendly marshal hit takes -1 relationship with the artillery marshal
- **Redemption threshold note:** If the -5 trust drop pushes a marshal to trust <= 20, the normal redemption event fires. This is intentional — the player's bombardment triggered a trust crisis with their own marshal. Dramatic and fair.

#### Collateral Display

The bombardment result dict includes a `collateral` array:

```python
"collateral": [
    {"name": "Uxbridge", "nation": "Britain", "casualties": 998, "friendly_fire": False},
    {"name": "Davout", "nation": "France", "casualties": 750, "friendly_fire": True},
]
```

### 4.5 Bombardment Limit Per Turn

Artillery may fire a **maximum of 2 bombardments per turn**. Guns need time to cool, resupply ammunition, and reposition between salvos.

```python
# New field on Marshal
bombardments_this_turn: int = 0  # Reset to 0 at turn start

# In executor, before bombardment:
if marshal.bombardments_this_turn >= 2:
    return {
        "success": False,
        "message": f"{marshal.name}'s guns have expended their ammunition for today. "
                   f"The battery needs time to resupply. (Max 2 bombardments per turn)"
    }

# After successful bombardment:
marshal.bombardments_this_turn += 1
```

**Serialization:** Add `bombardments_this_turn` to `to_dict()` / `from_dict()` with `.get(key, 0)` default.

**Turn reset:** Clear in `world_state.py advance_turn()` in the per-marshal reset loop (line ~3022), alongside `attacks_this_turn` and `moved_this_turn`. **NOT** in `_process_tactical_states()` — the reset happens in the direct loop before that function is called.

### 4.6 No Battle Outcome

Bombardment produces **no winner or loser**. It is not a battle — it is shelling.

**Systems that DO NOT trigger from bombardment:**
- No victor/outcome determination
- No counter-punch (defender wasn't in melee)
- No forced retreat check (morale not affected enough per salvo)
- No `battles_won` / `battles_lost` increment
- No `recent_battles` list update
- No glorious charge interaction
- No flanking bonus
- No dice roll (damage is formula-based with variance)
- No cavalry counter (+30%) — not applicable at range
- No stance modifiers on damage calculation (bombardment is mechanical, not tactical posture)

**Systems that DO trigger from bombardment:**
- Terrain bombardment modifier (§4.1)
- Collateral damage (§4.4)
- Fort degradation (§5)
- Bombardment streak tracking (existing, for objections — persists across turns)
- Idle turn reset (artillery is active)
- `in_combat_this_turn` = True (for cannon fire interrupt detection)
- AP cost: **1 per bombardment** (same as standard attack — confirmed: `_action_costs["attack"] = 1`)
- Event log: new "bombardment" event type (§8)

### 4.7 Morale Effects

| Target | Morale Change | Rationale |
|--------|--------------|-----------|
| **Attacker (artillery)** | None | Guns fired safely, no risk |
| **Defender (primary)** | -3 per bombardment | Sustained shelling erodes morale slowly |
| **Collateral targets** | -1 per collateral hit | Shrapnel is demoralizing but less intense |

Sustained bombardment (2/turn × multiple turns) will grind defender morale down. At -3 per salvo, -6 per turn, a defender at 100% morale reaches forced retreat threshold (25%) after ~13 bombardments across ~7 turns. This makes bombardment a **slow siege tool**, not an instant win.

### 4.8 Defender Reduced to Zero

If bombardment casualties reduce the defender's strength to 0:

- Defender marshal is **destroyed** (same as in battle — `take_casualties` handles this)
- Defender goes through normal broken/retreat logic
- **Region is NOT captured** — artillery is not physically present
- Region becomes undefended (no controller change until someone moves in)
- A follow-up move by infantry/cavalry is needed to claim the region

This is good design: artillery clears, infantry captures.

---

## 5. Fort Degradation

Fort degradation is one of artillery's **primary purposes** and must still work under bombardment.

Currently in `combat.py` lines 617-625:
```python
if getattr(defender, 'defense_bonus', 0) > 0:
    degradation_amount = 0.10 if getattr(attacker, 'artillery', False) else 0.05
    defender.defense_bonus = max(0, round(defender.defense_bonus - degradation_amount, 2))
```

**In bombardment resolution:** Apply the same logic directly:

```python
fortification_degraded = False
fortification_old = 0.0
fortification_new = 0.0
if getattr(defender, 'defense_bonus', 0) > 0:
    fortification_old = defender.defense_bonus
    degradation_amount = 0.10  # Always artillery rate for bombardment
    defender.defense_bonus = max(0, round(defender.defense_bonus - degradation_amount, 2))
    fortification_new = defender.defense_bonus
    fortification_degraded = True
```

**Building fortification bonus** (`fortification_bonus` parameter from star forts) is NOT degraded by bombardment — only the marshal's personal `defense_bonus` from the fortify action. This matches current behavior.

---

## 6. Same-Region Battle (Unchanged)

When artillery IS in the same region as the enemy and attacks (or is attacked), the full `resolve_battle()` pipeline applies. No changes.

This represents guns being physically present on the battlefield:
- Cavalry counter (+30%) applies — charging gun lines is devastating
- `moved_this_turn` -25% defense applies — guns caught in transit
- Full casualty calculation, morale swings, winner/loser
- Artillery can be destroyed in melee

**Key interaction:** The `moved_this_turn` block already prevents artillery from attacking on the same turn they move. So same-region attacks happen when:
1. Artillery was already in the region (stationed there)
2. Enemy moved INTO the artillery's region (enemy attacks artillery)
3. Artillery moved last turn, attacks this turn

---

## 7. Artillery Objections

### Phase 6.5 (V2a) — Build Now

The current objection triggers for artillery are:
- **Impatient bombardier** (aggressive): streak >= 3 + target softened → MILD "Let the infantry finish it!"
- **Patient gunner** (cautious): moving while adjacent target still has forts → MILD "One more barrage!"

These are **replaced** by the triggers below.

#### 7.1 Cautious Artillery (Drouot) — "The Sage of the Grand Army"

Drouot is methodical, precise, and protective of his guns and ammunition. He objects when his professional judgment is overridden — not when asked to bombard (that's what he wants).

| Trigger | Condition | Level | Flavor |
|---------|-----------|-------|--------|
| **Ordered into melee** | Attack when in same region as enemy (real battle, not bombardment) | STRONG | "You would send my gunners into the bayonet line? These are artillerists, not infantry. We serve you best from range." |
| **Reckless repositioning** | Move order while bombardment_streak >= 2 AND adjacent target has defense_bonus > 0 | MODERATE | "One more barrage and their walls crumble, Sire! Moving now wastes everything we've achieved." |
| **Ordered to cease fire** | Defend/fortify order while adjacent enemy has defense_bonus > 0.05 AND bombardment_streak >= 1 | MODERATE | "You would have me silence my guns while their walls still stand? Give me one more day, Sire." |
| **Wasted fire** | Bombardment target has defense_bonus == 0 AND strength < 8,000 | MILD | "The target is already broken, Sire. Infantry can sweep them aside. My ammunition is better spent elsewhere." |
| **Last-shot advisory** | Bombardment when bombardments_this_turn == 1 (last shot) AND multiple valid adjacent targets | MILD | "One salvo remains today, Sire. The fortified position at {best_target} will feel it most keenly." |

**Note on streak persistence:** `bombardment_streak` persists across turns (only resets on move, target switch, retreat, or broken state). It is NOT reset at turn start. This means a streak of 2 builds over 2+ turns of sustained bombardment on the same target — the "cease fire" and "reckless repositioning" triggers work correctly with the HOLD strategic command (§9) since HOLD fires once per turn.

#### 7.2 Replacing Old Triggers

- `objection_v2.py` line 772-782: "Impatient bombardier" → **Replace** with "Wasted fire" (more specific, same level)
- `objection_v2.py` line 850-861: "Patient gunner" → **Replace** with "Reckless repositioning" (stronger, MODERATE)

### Phase 7 (V2b) — Deferred Triggers

#### 7.3 Aggressive Artillery (Future Marshals)

For future aggressive artillery marshals (not currently in game):

| Trigger | Condition | Level | Flavor |
|---------|-----------|-------|--------|
| **Ordered to hold fire** | Defend/fortify order when enemy is adjacent | MILD | "The enemy is RIGHT THERE! Let me fire, damn it! What good are guns that don't shoot?" |
| **Told to stop when winning** | Cancel/move order when target has morale < 50 OR strength < starting_strength × 0.4 | MILD | "They're reeling! One more salvo and they break — don't pull me away now!" |
| **Told to stay at range** | HOLD order when enemy is in same region | MODERATE | "I won't hide behind my guns when the enemy is at our throats! Let me advance!" |
| **Extended inactivity** | No targets adjacent for 3+ turns while enemies exist on map | MILD | "My guns rust while battles rage elsewhere! Send me where the fighting is, Sire!" |

#### 7.4 Cross-Marshal Objections (V2b Infrastructure)

These require V2b infrastructure (marshal A objecting to an order given to marshal B):

| Marshal | Trigger | Condition | Level | Flavor |
|---------|---------|-----------|-------|--------|
| **Ney** (aggressive cavalry) | Artillery wasting time | Drouot has bombardment_streak >= 3 AND Ney adjacent to same target AND favorable ratio | MILD | "Enough shells! My cavalry can break them in a single charge — let us ride, Sire!" |
| **Davout** (cautious infantry) | Artillery pulled away | Drouot receives move order AWAY from Davout AND Davout adjacent to enemy | MILD | "The guns provide valuable cover for my position. Without Drouot's support, we are exposed." |
| **Ney** (aggressive) | Shelling his target | Drouot bombards enemy Ney is pursuing (PURSUE order on same marshal) | MILD | "That's MY prey, Drouot! Stop tickling them with shells — I'm going in!" |
| **Any marshal** | Friendly fire victim | Marshal hit by collateral from friendly bombardment | MODERATE | "{name} is furious! 'Your guns just shelled MY men! Control your fire, Drouot!'" |

#### 7.5 Objection Flavor Text (disobedience.py)

New V1 flavor text entries for artillery objections:

```python
'cautious': {
    # ... existing entries ...
    'reckless_repositioning': [
        "\"{name} places a steadying hand on the nearest cannon. \"Sire, we have the range. "
        "Their fortifications are cracking. To move now abandons our advantage.\"",
        "\"{name} shakes his head firmly. \"The walls show fractures from our fire. "
        "One — perhaps two — more barrages and they will have no cover at all.\"",
    ],
    'ordered_into_melee': [
        "\"{name} pales visibly. \"Sire... these men serve the guns. In a bayonet fight, "
        "we are butchers sent to do a swordsman's work. I beg you, reconsider.\"",
        "\"{name} looks at his gunners, then back at you. \"If you order it, we go. "
        "But know that we lose the guns and the men who know how to fire them.\"",
    ],
    'ordered_to_cease_fire': [
        "\"{name} grips his telescope tightly. \"Sire, the fortifications crack more with each "
        "salvo. Silence my guns now and all that fire was for nothing.\"",
        "\"{name} gestures to the distant smoke. \"We have their measure, Sire. The walls "
        "will not survive another day of this. Why stop when we are so close?\"",
    ],
    'wasted_fire': [
        "\"{name} lowers his telescope. \"The position is already shattered, Sire. "
        "Sending more shells into rubble serves no purpose. Let the infantry advance.\"",
        "\"{name} gestures toward the distant target. \"Look — they have no walls left, "
        "and barely enough men to hold a picket line. Save my powder for a worthy target.\"",
    ],
    'last_shot_advisory': [
        "\"{name} calculates carefully. \"One salvo remains today, Sire. Might I suggest "
        "the fortified position? My guns will have the greatest effect there.\"",
        "\"{name} studies the field. \"A single shot left for the day. Let me place it "
        "where it counts — the enemy walls will crack if we strike true.\"",
    ],
}
```

---

## 8. Event Log

New event type for the turn events log:

```python
{
    "type": "bombardment",
    "attacker": "Drouot",
    "attacker_nation": "France",
    "defender": "Wellington",
    "defender_nation": "Britain",
    "attacker_location": "Paris",       # Where guns fired from
    "defender_location": "Waterloo",    # Where shells landed
    "attacker_casualties": 375,
    "defender_casualties": 3990,
    "terrain": "plains",
    "terrain_modifier": 1.10,
    "fort_degraded": True,
    "fort_old": 0.16,
    "fort_new": 0.06,
    "collateral": [                     # May be empty list
        {"name": "Uxbridge", "nation": "Britain", "casualties": 998, "friendly_fire": False},
    ],
}
```

**Fog of war filtering:** Bombardment events follow the same nation-based fog filter as battle events. Player sees their own bombardments. Enemy bombardments visible only if the target region is at PARTIAL+ visibility.

---

## 9. Strategic HOLD — Artillery Override

### 9.1 Concept

When artillery is given a HOLD strategic command, the personality-specific behavior is replaced with **automatic bombardment** — analogous to how aggressive marshals on HOLD sally out against adjacent enemies.

This is the artillery equivalent of Ney's sally: a free, automatic action each turn that doesn't cost the player AP but trades off player control for convenience. The artillery picks its own target based on personality.

### 9.2 Behavior Matrix

When an artillery marshal arrives at the HOLD position, behavior depends on personality:

| Personality | Bombardments/Turn | Target Selection | Switching |
|-------------|-------------------|------------------|-----------|
| **Cautious** (Drouot) | 1 | Highest defense_bonus (crack forts) | Switches only if new threat is 2x stronger |
| **Aggressive** (future) | 2 | Lowest strength (finish them off) | Switches every turn to weakest |
| **Literal** (future) | 1 | Same target always (sustained fire) | Never switches until target destroyed/moved |

**Key trade-offs vs. manual bombardment:**
- HOLD bombardment is **free** (no AP cost — `_strategic_execution = True`)
- HOLD bombardment fires **once per turn** for cautious (vs. 2/turn manual)
- HOLD bombardment is **not player-targeted** (artillery picks its own target)
- `bombardments_this_turn` still increments (prevents manual + strategic double-dipping if order is cancelled mid-turn)

### 9.3 Implementation in strategic.py

In `_execute_hold()`, add an artillery path **before** the existing personality checks (line ~1228):

```python
# AT HOLD POSITION — Check unit type first
if getattr(marshal, 'artillery', False):
    return self._execute_hold_bombardment(marshal, world, game_state)

# Then existing personality paths (aggressive sally, cautious fortify, etc.)
```

**Arrival-turn note:** On the turn the marshal moves to the hold position, the existing code returns an "arriving" message (line 1204-1212) **before** reaching this artillery check. The marshal does not bombard on the arrival turn. Bombardment begins the following turn when `moved_this_turn` has been reset. This is correct behavior but important to document: do not reorganize the code to move the artillery check before the position/arrival checks.

#### _execute_hold_bombardment Logic

```python
def _execute_hold_bombardment(self, marshal, world, game_state):
    """Artillery-specific HOLD: auto-bombard adjacent enemies."""
    order = marshal.strategic_order
    hold_position = order.target
    personality = marshal.personality

    # Check if already fired this turn (strategic + manual share the limit)
    if marshal.bombardments_this_turn >= 2:
        return {
            "marshal": marshal.name,
            "command": "HOLD",
            "action": "hold_artillery_spent",
            "order_status": "continues",
            "message": f"{marshal.name}'s guns have already fired today. Maintaining position."
        }

    # Find adjacent enemies
    region = world.get_region(marshal.location)
    if not region:
        return self._hold_no_targets(marshal, hold_position)

    targets = []
    for adj_name in region.adjacent_regions:
        for enemy in world.get_enemies_in_region(adj_name, marshal.nation):
            targets.append(enemy)

    if not targets:
        return self._hold_no_targets(marshal, hold_position)

    # Select target by personality
    if personality == "cautious":
        # Crack forts first, then biggest army
        targets.sort(key=lambda t: (-getattr(t, 'defense_bonus', 0), -t.strength))
    elif personality == "aggressive":
        # Finish the weak first
        targets.sort(key=lambda t: t.strength)
    else:  # literal
        # Same target as last time if possible
        locked = getattr(order, 'bombardment_target', None)
        if locked:
            locked_targets = [t for t in targets if t.name == locked]
            if locked_targets:
                targets = locked_targets

    target = targets[0]

    # Store target lock for literal/cautious consistency
    order.bombardment_target = target.name

    # Fire via executor (strategic execution = free)
    result = self.executor.execute(
        {"command": {
            "marshal": marshal.name,
            "action": "attack",
            "target": target.name,
            "_strategic_execution": True,
        }},
        game_state
    )

    # Build report
    cleaned = {k: v for k, v in result.items() if k != "new_state"} if result else {}
    return {
        "marshal": marshal.name,
        "command": "HOLD",
        "action": "hold_bombardment",
        "target": target.name,
        "order_status": "continues",
        "battle_details": cleaned,
        "message": f"{marshal.name}'s guns bombard {target.name}'s position from {hold_position}.",
    }
```

### 9.4 Personality Interactions

**Cautious Drouot on HOLD — The Artillery Grouchy Moment:**
- Drouot hears cannon fire from a nearby battle (cannon fire interrupt)
- He does NOT redirect fire. He stays on his assigned bombardment target
- This is the cautious, methodical choice — he trusts his orders, cracks the fort
- The player must spend 1 AP to cancel HOLD and redirect him
- This creates dramatic tension identical to the Grouchy Moment but for artillery

**Objection on receiving "HOLD" order:**
- Drouot does NOT object to HOLD. This is exactly what he wants — a clear, safe, methodical assignment
- ConcernLevel.NONE: "A fine position, Sire. My guns will make their presence known."

**Objection on CANCELLING HOLD:**
- If bombardment_streak >= 2 AND adjacent target has defense_bonus > 0: **MODERATE**
- "The walls are cracking, Sire! To silence my guns now abandons everything we've achieved."
- This uses the existing "ordered to cease fire" trigger from §7.1
- Streak persists across turns, so 2+ turns of sustained HOLD bombardment meets the threshold

### 9.5 Edge Cases

| Edge Case | Behavior |
|-----------|----------|
| Enemy enters artillery's region | HOLD order breaks. Report: "{marshal} reports: enemy forces have entered {region}! Requesting orders." Artillery can't bombard enemies in their own region. |
| All adjacent enemies retreat/destroyed | Report "no targets in range — maintaining readiness." Order continues (new targets may arrive). |
| Target switches region | Cautious: switch to next-best adjacent target. Literal: report "lost sight of {target}." Continue on next-best or wait. |
| Player manually bombards before strategic turn | `bombardments_this_turn` incremented by manual fire. Strategic HOLD respects the shared limit. If already at 2, strategic bombardment skips. |

### 9.6 Serialization

New field on StrategicOrder:

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `bombardment_target` | Optional[str] | None | Current locked target for HOLD bombardment |

Add to `StrategicOrder.to_dict()` / `from_dict()`.

**Dangling reference handling:** If `bombardment_target` references a marshal that was destroyed or left the area, the lookup in `_execute_hold_bombardment()` gracefully falls through to default target selection (the `locked_targets` list is empty, so the code uses the personality-based sort). No explicit cleanup is required, but the field will naturally clear when the order ends or the target is re-acquired.

---

## 10. Enemy AI — Artillery Bombardment

### 10.1 Changes Required

The spec's routing rule (§3) makes bombardment **transparent to the AI** — PrinceAugust issues an "attack" command, the executor routes to bombardment if the target is adjacent but not same-region. However, several AI behaviors need updating:

#### Bombardment Limit Check (REQUIRED)

In `_find_attack_opportunity()`, before selecting a bombardment target for artillery:

```python
# Artillery: check bombardment limit before attempting ranged attack
if getattr(marshal, 'artillery', False):
    if getattr(marshal, 'bombardments_this_turn', 0) >= 2:
        ai_debug(f"    P4: {marshal.name} at bombardment limit — skipping ranged attack")
        return None  # Fall through to P5+ (positioning)
```

Without this check, the AI wastes an evaluation cycle on a failed bombardment attempt.

#### P4.25 Garrison Assault — Skip for Ranged Artillery (REQUIRED)

Artillery cannot bombard garrisons (§3). Add a check in `_find_garrison_attack()`:

```python
# Artillery can't bombard garrisons — must be in same region (which requires prior move)
if getattr(marshal, 'artillery', False) and getattr(marshal, 'moved_this_turn', False):
    return None  # Can't move + attack in same turn
# Note: if artillery is already adjacent to a garrison and hasn't moved,
# it still can't "bombard" a garrison — the garrison combat path requires
# same-region presence. Skip P4.25 for artillery entirely.
if getattr(marshal, 'artillery', False):
    return None
```

**P0 engagement note:** P0 handles same-region combat. When artillery is engaged in the same region as an enemy, it uses the normal `resolve_battle()` path (melee), NOT bombardment. The mood-adjusted threshold applies normally. No changes needed for P0.

#### Lower Ratio Threshold for Bombardment (REQUIRED)

Bombardment costs 1.5% own strength per salvo — dramatically less risky than melee (15%+ casualties). The AI should bombard at ANY strength ratio since the risk/reward is always favorable:

```python
# In _find_attack_opportunity(), when evaluating artillery targets:
if getattr(marshal, 'artillery', False) and target.location != marshal.location:
    # Ranged bombardment — always worth it regardless of ratio
    # Skip the normal cautious ratio checks
    return {"marshal": marshal.name, "action": "attack", "target": target.name}
```

Current cautious personality thresholds (ratio >= 1.5 to attack) should be **bypassed for ranged bombardment only**. Same-region artillery combat still uses normal thresholds.

#### Skip Broken/Retreating Targets (REQUIRED)

```python
# Don't bombard marshals that are broken or retreating (waste of ammo)
if getattr(target, 'broken', False) or getattr(target, 'retreating', False):
    continue  # Skip this target
```

### 10.2 AI Target Selection Update

Current AI sorts artillery targets by fort value. With bombardment being a separate low-risk path, update the sort to also consider collateral opportunity:

```python
# ARTILLERY SORT for bombardment targets
if getattr(marshal, 'artillery', False):
    # Priority: fortified > multiple enemies in region > terrain effectiveness > unfortified
    def bombardment_value(enemy):
        fort = getattr(enemy, 'defense_bonus', 0)
        region = world.get_region(enemy.location)
        forces_in_region = len([m for m in world.get_marshals_in_region(enemy.location)
                                if m.nation != nation and m.strength > 0])
        terrain_mod = TERRAIN_BOMBARDMENT_MODIFIER.get(region.terrain, 1.0) if region else 1.0
        return (fort > 0, forces_in_region, fort, terrain_mod)  # Tuple sort: fort, density, fort level, terrain
    targets.sort(key=bombardment_value, reverse=True)
```

**Terrain as tiebreaker:** When two targets have equal fort value and force density, prefer the target on open terrain (higher terrain_mod = more damage per bombardment). A plains target (1.10) takes 1.83x more damage than a mountains target (0.60).

### 10.3 AI Does NOT Use Strategic HOLD

The AI evaluates each marshal each turn through the priority tree (P0-P8). Strategic HOLD is a **player convenience feature** to reduce micromanagement. The AI already achieves equivalent behavior through:
- P4: Attack (bombardment via executor routing)
- P7: Anti-oscillation (stay and bombard instead of repositioning)
- Position scoring (prefer spots adjacent to fortified enemies)

Adding strategic command usage to the AI would add complexity with zero behavioral change.

### 10.4 AI Edge Cases

| Edge Case | Current Behavior | Required Change |
|-----------|-----------------|-----------------|
| PrinceAugust at bombardment limit (2/turn) | AI tries attack, executor fails, AI falls through to P5+ | Add pre-check (§10.1) to skip cleanly |
| PrinceAugust bombards target to 0, region undefended | AI infantry captures via P4.5 | None — works correctly |
| PrinceAugust targets broken/retreating marshal | May waste bombardment on ineffective target | Add broken/retreating filter (§10.1) |
| PrinceAugust has no adjacent enemies after 2 bombardments | Falls through to P7 positioning | None — correct behavior |
| Two future AI artillery both target same enemy | Each evaluates independently, both bombard | None — concentrated fire is historically correct |
| Collateral hits AI's own forces | AI doesn't account for friendly fire risk | **Acceptable for now.** AI doesn't position allies to avoid collateral. Future: AI avoids area bombardment when friendlies are in target region. |

---

## 11. Berthier Report

### 11.1 New Bombardment Observations

Add to `battle_report.py` `_OBSERVATIONS` dict:

```python
"bombardment_effective": [
    "{marshal}'s guns thunder across the valley. The enemy position absorbs punishment, Sire.",
    "A methodical bombardment by {marshal}. Each salvo finds its mark.",
    "Smoke rises from {enemy}'s position. {marshal}'s fire is taking its toll.",
],
"bombardment_fort_cracking": [
    "{marshal}'s sustained fire is dismantling {enemy}'s fortifications. The walls cannot endure.",
    "Cracks spread through the enemy works under {marshal}'s bombardment. They weaken, Sire.",
],
"bombardment_ineffective": [
    "{marshal}'s guns fire into the mass, but {enemy}'s army is vast. The shells are pinpricks.",
    "The bombardment continues, but {enemy}'s numbers absorb our fire with barely a flinch.",
],
"bombardment_target_broken": [
    "{marshal}'s bombardment has shattered {enemy}'s position entirely. The way is clear for advance.",
    "The guns fall silent — there is nothing left to shell. {enemy}'s force is destroyed.",
],
"bombardment_terrain_difficulty": [
    "{marshal}'s guns struggle to find targets in the {terrain}. The land itself shields {enemy}.",
    "The {terrain} terrain hampers {marshal}'s fire. Shells fall wide of their marks.",
],
"bombardment_friendly_fire": [
    "Sire, our own forces were caught in {marshal}'s bombardment. Regrettable, but unavoidable.",
    "{marshal}'s shells struck friend as well as foe. The price of area bombardment.",
],
```

### 11.2 Selection Logic

```
IF defender reduced to 0 → "bombardment_target_broken"
ELIF collateral hit friendly → "bombardment_friendly_fire"
ELIF fort_degraded → "bombardment_fort_cracking"
ELIF terrain_modifier < 0.80 → "bombardment_terrain_difficulty"
ELIF defender_casualties < defender.strength * 0.03 → "bombardment_ineffective"
ELSE → "bombardment_effective"
```

**Note:** Threshold for "ineffective" raised from 0.02 to 0.03 so it fires more often against large armies, giving the player meaningful feedback about target selection.

---

## 12. Godot Frontend

### 12.1 Bombardment Result Display

The bombardment result dict returned to Godot differs from a battle result:

```python
{
    "success": True,
    "action": "bombardment",   # NOT "attack" — Godot uses this to choose display
    "message": "...",           # Narrative text
    "bombardment_result": {
        "attacker": {"name": "Drouot", "casualties": 375, "remaining": 24625},
        "defender": {"name": "Wellington", "casualties": 3990, "remaining": 64010, "morale": 97},
        "terrain": "plains",
        "terrain_modifier": 1.10,
        "fort_degraded": True,
        "fort_old": 0.16,
        "fort_new": 0.06,
        "bombardments_remaining": 1,  # How many more this turn
        "collateral": [...],           # Collateral damage array (§4.4)
        "berthier_observation": "...",
    }
}
```

### 12.2 HUD Advisory

When artillery has bombardments remaining and valid targets adjacent, the Berthier advisory system should note:

> "Drouot's guns are positioned to bombard Waterloo. (1 bombardment remaining today)"

When limit reached:

> "Drouot's battery has expended today's ammunition. Available to fire next turn."

---

## 13. Serialization

### 13.1 New Fields

| Field | Class | Type | Default | Purpose |
|-------|-------|------|---------|---------|
| `bombardments_this_turn` | Marshal | int | 0 | Tracks bombardments fired this turn (max 2) |
| `square_formation` | Marshal | bool | False | True when infantry is in anti-cavalry square |
| `bombardment_target` | StrategicOrder | Optional[str] | None | Locked target for HOLD bombardment |

### 13.2 Checklist

- [ ] Add `bombardments_this_turn` to `Marshal.__init__`
- [ ] Add `bombardments_this_turn` to `Marshal.to_dict()`
- [ ] Add `bombardments_this_turn` to `Marshal.from_dict()` with `.get('bombardments_this_turn', 0)`
- [ ] Reset `bombardments_this_turn` in `world_state.py advance_turn()` per-marshal loop (alongside `attacks_this_turn`, `moved_this_turn`)
- [ ] Add `square_formation` to `Marshal.__init__`, `to_dict()`, `from_dict()` with `.get('square_formation', False)`
- [ ] Process `square_formation` in `_process_tactical_states()` (clear on broken/retreating)
- [ ] Add `bombardment_target` to `StrategicOrder.__init__`, `to_dict()`, `from_dict()`
- [ ] Add `TERRAIN_BOMBARDMENT_MODIFIER` to `region.py`
- [ ] Extend `record_attack()` with `unit_type` field (no serialization needed — clears per turn)
- [ ] Run `pytest tests/test_serialization_enforcement.py -v`
- [ ] Update `docs/SAVE_FORMAT_REFERENCE.md`

---

## 14. Diminishing Returns (Future Consideration)

If playtesting reveals "park and shell" is still too dominant even with the 2/turn limit, add diminishing returns based on `bombardment_streak`:

```
streak 0-2: full damage (100%)
streak 3-4: 75% damage (target has dug in)
streak 5+:  50% damage (deeply entrenched)
```

This is NOT part of the initial implementation — flag for playtesting evaluation. The 2/turn limit + low per-shot damage + terrain modifier + 1 AP cost should be sufficient.

Pre-wire the streak check point in `_execute_bombardment()` so adding this later is a single constant change:

```python
# DIMINISHING RETURNS HOOK (not active — see §14)
# streak = marshal.bombardment_streak
# if streak >= 5: damage_multiplier *= 0.50
# elif streak >= 3: damage_multiplier *= 0.75
```

---

## 15. Implementation Sessions

### Session 48: Core Bombardment Resolution

**Foundation — everything else depends on this.**

| Item | Spec Section | Files |
|------|-------------|-------|
| `TERRAIN_BOMBARDMENT_MODIFIER` dict | §4.1 | `region.py` |
| `bombardments_this_turn` field + serialization | §4.5, §13 | `marshal.py` |
| `_execute_bombardment()` — damage formula, return casualties, morale, no-battle-outcome rules | §4.2, 4.3, 4.6, 4.7, 4.8 | `executor.py` |
| Routing rule in `_execute_attack()` | §3 | `executor.py` |
| Fort degradation in bombardment | §5 | `executor.py` |
| Turn reset in `advance_turn()` | §4.5 | `world_state.py` |
| Diminishing returns hook (commented) | §14 | `executor.py` |
| Remove dead code from `combat.py` | §16.1 | `combat.py` |
| Bombardment streak tracking (port from _execute_attack) | §4.6 | `executor.py` |

**Tests:** §17.1 (core bombardment) + §17.2 (terrain) + serialization round-trip.

**Verify:** curl test — Drouot bombards adjacent Wellington, confirm new path. Same-region attack still uses resolve_battle().

### Session 49: Collateral Damage + Event Log

**Builds on core bombardment. Adds the "shells are imprecise" identity.**

| Item | Spec Section | Files |
|------|-------------|-------|
| Collateral damage loop (40% chance, 25% of primary) | §4.4 | `executor.py` |
| Friendly fire trust/relationship penalties | §4.4 | `executor.py` |
| Region-name target auto-selection (strongest enemy) | §4.4 | `executor.py` or `parser.py` |
| Bombardment event type for turn log | §8 | `executor.py` |
| `main.py` pass-through for bombardment_result + collateral | §8 | `main.py` |

**Tests:** §17.3 (collateral) + region-name target + redemption threshold.

### Session 50: Enemy AI Bombardment

**Independent of collateral (collateral just happens). Depends on core routing existing.**

| Item | Spec Section | Files |
|------|-------------|-------|
| Bombardment limit check in `_find_attack_opportunity()` | §10.1 | `enemy_ai.py` |
| P4.25 garrison assault skip for artillery | §10.1 | `enemy_ai.py` |
| Ratio bypass for ranged bombardment | §10.1 | `enemy_ai.py` |
| Skip broken/retreating targets | §10.1 | `enemy_ai.py` |
| Target selection update (fort + density + terrain tiebreaker) | §10.2 | `enemy_ai.py` |

**Tests:** §17.5 (integration — AI uses bombardment correctly).

### Session 51: Strategic HOLD + Objections

**Thematically linked — both about Drouot's autonomous behavior and when he pushes back.**

| Item | Spec Section | Files |
|------|-------------|-------|
| `_execute_hold_bombardment()` in strategic.py | §9.3 | `strategic.py` |
| `bombardment_target` field on StrategicOrder + serialization | §9.6, §13 | `strategic.py`, marshal models |
| HOLD edge cases (enemy enters region, no targets, target leaves) | §9.5 | `strategic.py` |
| Replace V2a artillery triggers (cease fire, reckless repositioning, wasted fire, last-shot, melee) | §7.1, 7.2 | `objection_v2.py` |
| Add artillery flavor text | §7.5 | `disobedience.py` |

**Tests:** §17.4 (strategic HOLD) + objection trigger tests from §17.5.

### Session 52: Godot Frontend + Berthier + Docs

**Presentation layer. Depends on all backend sessions.**

| Item | Spec Section | Files |
|------|-------------|-------|
| `bombardment_result` display in terminal UI | §12.1 | `main.gd` |
| HUD advisory (bombardments remaining) | §12.2 | `main.gd` |
| Berthier bombardment observations | §11.1, 11.2 | `battle_report.py` |
| Doc updates | — | `SAVE_FORMAT_REFERENCE.md`, `SYSTEMS_REFERENCE.md`, `CLAUDE.md`, `STATUS.md` |
| Full manual curl test pass | §17.6 | — |

### Session 53: Combined Arms Bonus (Phase 7 — with Multi-Marshal Battles)

**Deferred to Phase 7.** Combined arms rewards coordinating unit types, which only matters when multiple marshals fight together. Build alongside multi-marshal battles and command structure.

**Rewards coordinating unit types in the same battle. Extends existing flanking infrastructure.**

The Napoleonic sequence — artillery preparation, infantry assault, cavalry exploitation — should be mechanically rewarded. When multiple unit types attack the same region in the same turn, later attackers benefit from the combined arms coordination.

#### Design

**Extend `record_attack()` in `world_state.py`:**

The existing `attack_record` dict gains a `unit_type` field:

```python
attack_record = {
    "attacker": attacker_name,
    "origin": origin_region,
    "timestamp": int(self._action_counter),
    "unit_type": unit_type,  # "infantry" | "cavalry" | "artillery"
}
```

Bombardment also records into `attacks_this_turn` via `record_attack()` so artillery preparation counts toward the combined arms bonus for later infantry/cavalry attacks.

**New method: `calculate_combined_arms_bonus(target_region)`:**

```python
def calculate_combined_arms_bonus(self, target_region: str) -> Dict:
    """Calculate bonus from multiple unit types attacking the same region."""
    if target_region not in self.attacks_this_turn:
        return {"bonus": 0.0, "unit_types": set(), "message": None}

    unit_types = set()
    for attack in self.attacks_this_turn[target_region]:
        unit_types.add(attack.get("unit_type", "infantry"))

    if len(unit_types) >= 3:
        bonus = 0.20  # +20% — full combined arms (all three branches)
    elif len(unit_types) >= 2:
        bonus = 0.10  # +10% — partial combined arms (two branches)
    else:
        bonus = 0.0

    return {"bonus": bonus, "unit_types": unit_types, "message": ...}
```

**Apply in `resolve_battle()` (combat.py):**

The combined arms bonus applies as an **attack multiplier** on the current attacker's shock calculation, alongside the existing flanking bonus on dice. This stacks with flanking (different axes of coordination):

```python
# After shock_multiplier calculation, before damage:
combined_arms = world.calculate_combined_arms_bonus(target_region)
if combined_arms["bonus"] > 0:
    shock_multiplier *= (1.0 + combined_arms["bonus"])
    combined_arms_message = f"Combined arms coordination! (+{int(combined_arms['bonus'] * 100)}% attack)"
```

**Bombardment contribution:** When `_execute_bombardment()` fires, it calls `record_attack()` with `unit_type="artillery"`. This means bombardment counts toward combined arms even though bombardment itself doesn't use `resolve_battle()`. The bonus applies to the NEXT melee attacker, not to the bombardment. This naturally creates the historical sequence: shell them, then charge.

**Key interactions:**
- Flanking (multi-direction) + combined arms (multi-type) stack. Maximum coordination: 3 unit types from 3 directions = +20% combined arms + flanking bonus 3 on dice. Devastating but requires committing your entire army.
- The first attacker of a new type gets no bonus (they establish the type). The second type gets +10%. The third gets +20%. Order matters.
- Same unit type attacking twice doesn't increase the bonus (set-based, not count-based).
- Combined arms message appears in battle report alongside flanking message.

| Item | Files |
|------|-------|
| Extend `record_attack()` with `unit_type` param | `world_state.py` |
| `calculate_combined_arms_bonus()` method | `world_state.py` |
| Pass `unit_type` from all `record_attack()` call sites (5 in executor.py) | `executor.py` |
| Bombardment calls `record_attack()` with `unit_type="artillery"` | `executor.py` |
| Apply combined arms multiplier in `resolve_battle()` | `combat.py` |
| Combined arms message in battle report | `combat.py`, `battle_report.py` |
| AI awareness: prefer attacking regions where allies of different types already struck | `enemy_ai.py` |
| Berthier observation: "The coordination of infantry, cavalry, and artillery proved decisive" | `battle_report.py` |

**Tests:**
- [ ] 2 unit types attacking same region → +10% for second attacker
- [ ] 3 unit types → +20% for third attacker
- [ ] Same type attacking twice → no bonus increase
- [ ] Bombardment counts as artillery type for combined arms
- [ ] Combined arms stacks with flanking bonus
- [ ] Combined arms bonus resets at turn start (via `attacks_this_turn` clear)
- [ ] Serialization: no new fields needed (`attacks_this_turn` already clears per turn)

### Session 54: Square Formation (Phase 7 — with Multi-Marshal Battles)

**Deferred to Phase 7.** Square formation is a response to multi-unit-type engagements — the tactical dilemma (square or line?) only arises when cavalry and artillery coordinate against infantry. Build alongside combined arms and multi-marshal battles.

**Infantry forms square to counter cavalry charges, but becomes an artillery target. Completes the Napoleonic tactical triangle.**

This is THE central tactical problem of Napoleonic warfare. Historically, infantry in square was nearly impervious to cavalry but a concentrated target for artillery. The decision — square or line? — depended entirely on what the enemy was sending at you.

#### The Triangle

```
        CAVALRY
       /        \
      / counters  \
     /    (+30%)   \
ARTILLERY ←-------- SQUARE
 counters          counters
  (+50%)           (-40% cav dmg)
```

- **Cavalry → Artillery:** Already exists (+30% cavalry counter)
- **Square → Cavalry:** New — infantry in square reduces cavalry attack damage by 40%
- **Artillery → Square:** New — bombardment and melee artillery deal +50% against square

Infantry in LINE formation (default) is the baseline — vulnerable to cavalry charges but not an artillery magnet.

#### Mechanics

**Command:** "Marshal Davout, form square" / "Davout, square formation"
**Cost:** 1 AP (same as fortify/drill — it's a tactical stance)
**Who:** Infantry marshals only. Cavalry and artillery cannot form square.

**New field on Marshal:**

```python
self.square_formation: bool = False  # True when in anti-cavalry square
```

**Effects while in square:**
- Cavalry attacks deal **-40% damage** (bristling bayonets, horses refuse to charge home)
- Artillery bombardment deals **+50% damage** (concentrated mass, can't miss)
- Artillery melee attacks deal **+50% damage** (same logic — packed formation)
- Marshal **cannot attack** (square is purely defensive — you can't advance in square)
- Marshal **cannot move** (square is a fixed position)
- Small defense bonus: **+5%** via `get_defense_modifier()` (tight formation, mutual support)
- **Stacks with fortify:** A fortified square is historically accurate (redoubt + square) but the combined bonuses make the marshal extremely hard to crack with infantry alone

**Square breaks automatically on:**
- Player orders move (break + move in one command, costs normal move AP)
- Player orders attack (break + attack, costs normal attack AP)
- Marshal is forced to retreat (broken by combat)
- Marshal is broken (morale collapse)
- Explicit "break square" / "form line" command (0 AP — free action, like stance change)

**Square does NOT break on:**
- Being attacked (the whole point is to endure attacks)
- Being bombarded (you suffer the +50% but the square holds)
- Turn end (persists across turns like fortify)

#### Implementation

**`_execute_form_square()` in executor.py:**

```python
def _execute_form_square(self, command, game_state, world, marshal):
    if getattr(marshal, 'cavalry', False) or getattr(marshal, 'artillery', False):
        return {"success": False, "message": f"{marshal.name} commands cavalry/artillery — only infantry can form square."}

    if getattr(marshal, 'square_formation', False):
        return {"success": False, "message": f"{marshal.name} is already in square formation."}

    marshal.square_formation = True
    return {
        "success": True,
        "message": f"{marshal.name} orders the infantry into square! "
                   f"Bayonets bristle outward — cavalry charges will break against this formation, "
                   f"but the packed ranks are vulnerable to artillery fire."
    }
```

**Blocking logic:** When `square_formation = True`, block attack and move actions with message: "{name}'s troops are in square formation. Break square first, or issue the order directly (square will break automatically)."

Actually — don't block. Auto-break on attack/move for smoother UX:

```python
# In _execute_attack / _execute_move, before main logic:
if getattr(marshal, 'square_formation', False):
    marshal.square_formation = False
    # Continue with attack/move normally
    # Add to message: "{name} breaks square formation and advances."
```

**Modifier integration (SINGLE SOURCE in marshal.py):**

```python
def get_defense_modifier(self):
    modifier = 0.0
    # ... existing modifiers ...
    if getattr(self, 'square_formation', False):
        modifier += 0.05  # +5% general defense in square
    return modifier
```

The cavalry damage reduction and artillery bonus are NOT in `get_defense_modifier` — they're target-type interactions applied in `combat.py` (same pattern as the existing cavalry counter):

```python
# In resolve_battle(), alongside cavalry counter block:

# SQUARE vs CAVALRY: Infantry square blunts cavalry charges
square_counter_message = None
if getattr(defender, 'square_formation', False) and getattr(attacker, 'cavalry', False):
    shock_multiplier *= 0.60  # -40% cavalry damage
    square_counter_message = f"{defender.name}'s square bristles with bayonets! {attacker.name}'s cavalry cannot break through. (-40% attack)"

# ARTILLERY vs SQUARE: Packed formation is a gunner's dream
square_vulnerability_message = None
if getattr(defender, 'square_formation', False) and getattr(attacker, 'artillery', False):
    shock_multiplier *= 1.50  # +50% artillery damage
    square_vulnerability_message = f"{defender.name}'s packed square is a perfect target for {attacker.name}'s guns! (+50% attack)"
```

**Bombardment integration:** In `_execute_bombardment()`, check for square:

```python
# After calculating raw_damage, before applying variance:
if getattr(defender, 'square_formation', False):
    raw_damage *= 1.50  # +50% — concentrated target
    square_vulnerability = True
```

#### Objection Triggers

| Marshal Type | Trigger | Level | Flavor |
|-------------|---------|-------|--------|
| **Aggressive infantry** (future) | Ordered to form square | MODERATE | "Square?! You want me to stand here like a sitting duck? Let me CHARGE them!" |
| **Cautious infantry** (Davout/Wellington) | Ordered to form square when no cavalry adjacent | MILD | "A prudent formation, Sire, though I see no cavalry to warrant it." |
| **Cautious infantry** | Ordered to form square when artillery adjacent | MILD | "Sire, their guns will make short work of us in square. Perhaps we should advance on the battery instead." |
| **Any infantry** | In square AND hit by bombardment | — (Berthier observation) | "The enemy artillery savages {name}'s square. The formation holds but the cost is terrible." |

#### AI Behavior

```python
# In enemy_ai.py, new check between P0 engagement and P3 counter-punch:

# P2.5: FORM SQUARE — defensive response to cavalry threat
if not getattr(marshal, 'cavalry', False) and not getattr(marshal, 'artillery', False):
    # Infantry only
    adjacent_cavalry = [e for e in adjacent_enemies if getattr(e, 'cavalry', False)]
    adjacent_artillery = [e for e in adjacent_enemies if getattr(e, 'artillery', False)]

    if adjacent_cavalry and not getattr(marshal, 'square_formation', False):
        # Form square if cavalry threatens AND no artillery threatens
        if not adjacent_artillery:
            return {"marshal": marshal.name, "action": "form_square"}
        # If BOTH cavalry and artillery threaten — the Napoleonic dilemma!
        # Cautious: form square (survive the charge, accept artillery damage)
        # Aggressive: stay in line (charge the cavalry back)
        if marshal.personality == "cautious":
            return {"marshal": marshal.name, "action": "form_square"}
        # Aggressive/literal: don't form square, prefer attacking
```

**AI break square:** If in square and no cavalry adjacent, break square (set `square_formation = False` directly in AI evaluation, or issue move/attack which auto-breaks).

| Item | Files |
|------|-------|
| `square_formation` field + serialization | `marshal.py` |
| `_execute_form_square()` | `executor.py` |
| Auto-break on move/attack | `executor.py` |
| `get_defense_modifier()` +5% in square | `marshal.py` |
| Square vs cavalry (-40%) in `resolve_battle()` | `combat.py` |
| Artillery vs square (+50%) in `resolve_battle()` | `combat.py` |
| Bombardment vs square (+50%) in `_execute_bombardment()` | `executor.py` |
| Process in `_process_tactical_states()` (clear on broken/retreat) | `world_state.py` |
| Add to `VALID_ACTIONS` + mock parser + AP cost | `validation.py`, `llm_client.py`, `world_state.py` |
| AI P2.5 square formation logic | `enemy_ai.py` |
| Square messages in battle report | `combat.py`, `battle_report.py` |
| Objection triggers | `objection_v2.py` |
| Godot display (square icon/indicator) | `main.gd`, `map.gd` |

**Tests:**
- [ ] Only infantry can form square (cavalry/artillery rejected)
- [ ] Square reduces cavalry attack damage by 40%
- [ ] Square increases artillery attack damage by 50%
- [ ] Square increases bombardment damage by 50%
- [ ] Square gives +5% defense modifier
- [ ] Cannot attack while in square (or auto-breaks before attack)
- [ ] Cannot move while in square (or auto-breaks before move)
- [ ] Square breaks on retreat/broken
- [ ] Square persists across turns
- [ ] "Break square" is free (0 AP)
- [ ] AI forms square when cavalry threatens and no artillery adjacent
- [ ] AI doesn't form square when artillery also threatens (personality-dependent)
- [ ] Serialization round-trip preserves `square_formation`
- [ ] Square + fortify stack correctly

---

## 16. Files to Modify (All Sessions)

| File | Changes |
|------|---------|
| `backend/models/region.py` | Add `TERRAIN_BOMBARDMENT_MODIFIER` dict |
| `backend/models/marshal.py` | Add `bombardments_this_turn`, `square_formation` fields, serialization |
| `backend/commands/executor.py` | Route ranged artillery to new `_execute_bombardment()` with terrain mod + collateral; `_execute_form_square()`; combined arms `record_attack()` calls; keep same-region in `_execute_attack()` |
| `backend/game_logic/combat.py` | Remove ranged bombardment 50% reduction (dead code); add combined arms multiplier, square vs cavalry (-40%), artillery vs square (+50%) |
| `backend/game_logic/battle_report.py` | Add bombardment, combined arms, and square observations |
| `backend/commands/objection_v2.py` | Replace artillery triggers per §7; add square formation triggers |
| `backend/commands/disobedience.py` | Add artillery flavor text per §7.5 |
| `backend/commands/strategic.py` | Add `_execute_hold_bombardment()` for artillery HOLD override (§9), add `bombardment_target` to StrategicOrder |
| `backend/models/world_state.py` | Reset `bombardments_this_turn` at turn start; `calculate_combined_arms_bonus()`; extend `record_attack()` with `unit_type`; process `square_formation` in `_process_tactical_states()` |
| `backend/ai/enemy_ai.py` | Add bombardment limit check, lower ratio threshold for ranged, skip broken/retreating targets, skip P4.25 for artillery (§10); P2.5 square formation; combined arms coordination awareness |
| `backend/ai/validation.py` | Add `form_square` to `VALID_ACTIONS` |
| `backend/ai/llm_client.py` | Add `form_square` keywords to mock parser |
| `backend/main.py` | Pass through bombardment result fields + collateral to API response |
| `godot-client/...main.gd` | Handle `bombardment_result` display including collateral; square formation indicator |
| `docs/SAVE_FORMAT_REFERENCE.md` | Document new fields |
| `docs/SYSTEMS_REFERENCE.md` | Document bombardment vs battle distinction, terrain modifier, collateral, combined arms, square formation |
| `CLAUDE.md` | Update artillery/combat mechanics references, add bombardment + square to troubleshooting |

---

## 16. Transition & Migration

### 16.1 Code Removal

The following code becomes **dead** once bombardment has its own path and should be removed:

| File | Lines | Code | Reason |
|------|-------|------|--------|
| `combat.py` | 406-423 | Ranged bombardment 50% return casualties block | Bombardment no longer goes through `resolve_battle()` |
| `combat.py` | 411 | `bombardment_range_message` variable | No longer generated by resolve_battle |
| `combat.py` | 544 | `bombardment_range_message` in tactical_prefix | Dead reference |
| `combat.py` | 662 | `"bombardment_range_message"` in result_dict | Dead field |

**Do NOT remove these until bombardment routing is confirmed working.** Implementation order:
1. Build `_execute_bombardment()` in executor
2. Add routing rule (§3) in `_execute_attack()`
3. Verify with curl tests that ranged attacks use new path
4. THEN remove dead code from combat.py
5. Run full test suite to confirm nothing breaks

### 16.2 Old Saves

- `bombardments_this_turn` defaults to 0 via `.get()` — no migration needed
- `TERRAIN_BOMBARDMENT_MODIFIER` is new code, not save data — no migration needed
- `bombardment_target` on StrategicOrder defaults to None via `.get()` — no migration needed
- Old saves with active ranged bombardment mid-turn: impossible (saves happen between turns)

### 16.3 Backward Compatibility

- The `bombardment_range_message` field in battle results stays until confirmed safe to remove (grep all Godot references first)
- Existing `bombardment_streak` / `last_bombardment_target` fields are unchanged — same semantics, now used by both manual and strategic bombardment
- The mock parser already handles "bombard" / "shell" / "barrage" keywords — no parser migration needed

---

## 17. Test Plan

### 17.1 Unit Tests — Core Bombardment

- [ ] Bombardment deals correct damage range (±20% variance around expected)
- [ ] Return casualties are ~1.5% of artillery strength
- [ ] 2/turn limit enforced (3rd bombardment fails with message)
- [ ] `bombardments_this_turn` resets at turn start
- [ ] Fort degradation applies (0.10 per bombardment)
- [ ] No counter-punch triggered from bombardment
- [ ] No morale change on attacker
- [ ] Defender morale drops by 3 per bombardment
- [ ] No `battles_won`/`battles_lost` increment
- [ ] Defender reduced to 0 → destroyed, region NOT captured
- [ ] Same-region attack still uses full `resolve_battle()`
- [ ] Cavalry counter (+30%) does NOT apply to bombardment
- [ ] Serialization round-trip preserves `bombardments_this_turn`

### 17.2 Unit Tests — Terrain

- [ ] Plains terrain gives +10% bombardment damage
- [ ] Forest terrain gives -20% bombardment damage
- [ ] Hills terrain gives -25% bombardment damage
- [ ] Mountains terrain gives -40% bombardment damage
- [ ] Urban terrain gives -30% bombardment damage
- [ ] River crossing gives no modifier
- [ ] Return casualties are NOT affected by terrain

### 17.3 Unit Tests — Collateral

- [ ] Targeted bombardment: 40% chance of collateral on each other force in region
- [ ] Collateral damage is 25% of primary damage
- [ ] Friendly forces take collateral damage
- [ ] Friendly fire triggers trust penalty (-5)
- [ ] Friendly fire triggers relationship penalty (-1 with artillery marshal)
- [ ] Friendly fire trust drop to <= 20 triggers redemption event
- [ ] Collateral array in result dict is correctly populated
- [ ] Collateral does NOT affect capital garrisons or player garrison detachments
- [ ] Region-name target ("bombard Waterloo") auto-selects strongest enemy in region

### 17.4 Unit Tests — Strategic HOLD

- [ ] Artillery on HOLD auto-bombards adjacent enemy
- [ ] Cautious fires 1/turn, picks highest fort target
- [ ] HOLD bombardment uses `_strategic_execution` (no AP cost)
- [ ] `bombardments_this_turn` increments from HOLD bombardment
- [ ] Manual bombardment after HOLD respects shared limit
- [ ] Enemy entering artillery's region breaks HOLD order
- [ ] No targets adjacent → "maintaining readiness" message
- [ ] Bombardment streak accumulates across turns during HOLD
- [ ] Cancelling HOLD with streak >= 2 triggers "cease fire" objection

### 17.5 Unit Tests — Combined Arms (Session 53)

- [ ] 2 unit types attacking same region → +10% for second attacker
- [ ] 3 unit types attacking same region → +20% for third attacker
- [ ] Same type attacking twice → no bonus increase
- [ ] Bombardment counts as artillery type for combined arms
- [ ] Combined arms stacks with flanking bonus
- [ ] Combined arms bonus resets at turn start (via `attacks_this_turn` clear)
- [ ] Combined arms message in battle report
- [ ] `record_attack()` includes `unit_type` field

### 17.6 Unit Tests — Square Formation (Session 54)

- [ ] Only infantry can form square (cavalry/artillery rejected)
- [ ] Square reduces cavalry attack damage by 40%
- [ ] Square increases artillery melee attack damage by 50%
- [ ] Square increases bombardment damage by 50%
- [ ] Square gives +5% defense modifier
- [ ] Auto-breaks on attack order (attack proceeds after breaking)
- [ ] Auto-breaks on move order (move proceeds after breaking)
- [ ] Square breaks on retreat/broken
- [ ] Square persists across turns
- [ ] "Break square" / "form line" is free (0 AP)
- [ ] AI forms square when cavalry threatens and no artillery adjacent
- [ ] AI cautious forms square even with artillery threat; aggressive does not
- [ ] Serialization round-trip preserves `square_formation`
- [ ] Square + fortify stack correctly

### 17.7 Integration Tests

- [ ] AI artillery (PrinceAugust) uses bombardment correctly
- [ ] AI skips bombardment when at 2/turn limit
- [ ] AI bombards regardless of strength ratio (low risk)
- [ ] AI skips broken/retreating targets
- [ ] AI skips P4.25 garrison assault for artillery (cannot bombard garrisons)
- [ ] AI P0 same-region engagement uses normal battle, not bombardment
- [ ] Bombardment streak tracks across turns
- [ ] Objection triggers fire correctly per §7
- [ ] Event log records bombardment events with terrain and collateral
- [ ] Fog of war filters bombardment events correctly
- [ ] Combined arms bonus applied in multi-type coordinated attacks
- [ ] AI coordinates unit types when possible (combined arms awareness)
- [ ] Square formation interacts correctly with cavalry counter and bombardment
- [ ] Full triangle: cavalry→artillery (+30%), artillery→square (+50%), square→cavalry (-40%)

### 17.8 Manual / Curl Tests

```bash
# Drouot bombards Wellington from adjacent region (targeted)
curl -X POST http://127.0.0.1:8005/command \
  -H "Content-Type: application/json" \
  -d '{"command": "Drouot, bombard Wellington"}' | python -m json.tool

# Region-name target — auto-selects strongest enemy in region
curl -X POST http://127.0.0.1:8005/command \
  -H "Content-Type: application/json" \
  -d '{"command": "Drouot, bombard Waterloo"}' | python -m json.tool

# Verify 3rd bombardment is blocked
# (after 2 successful bombardments in same turn)

# Verify same-region attack uses full battle
# (move Drouot to Wellington's region first)

# Verify HOLD auto-bombardment
curl -X POST http://127.0.0.1:8005/command \
  -H "Content-Type: application/json" \
  -d '{"command": "Drouot, hold position"}' | python -m json.tool
# Then end turn and verify bombardment in strategic report
```
