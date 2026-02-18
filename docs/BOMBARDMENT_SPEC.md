# Bombardment System Specification

> **Phase 6.5 — Artillery Bombardment Redesign**
> **Status:** DRAFT — Awaiting review
> **Author:** Mitch + Claude (Opus), Session 45
> **Depends on:** Artillery Unit Type (Sessions 42-44), Combat System, Objection V2
> **Feeds into:** Berthier Reports, Event Log, Godot HUD

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

---

## 3. Routing Rule

**The executor decides which path based on location:**

```
IF artillery attacks AND attacker.location != defender.location:
    → Bombardment resolution (this spec)
ELSE:
    → Full resolve_battle() (unchanged)
```

This is transparent to the AI, parser, and player. The command is still "attack" — the executor routes internally.

---

## 4. Bombardment Resolution

### 4.1 Damage Dealt to Defender

Base damage as percentage of **defender's** army (not strength ratio):

```
base_rate = 0.04  (4% of defender's strength)
shock_skill = artillery_marshal.get_effective_skill("shock")
damage_multiplier = 1.0 + (shock_skill / 15.0)

raw_damage = defender.strength * base_rate * damage_multiplier
variance = random.uniform(0.80, 1.20)  # ±20% randomness
defender_casualties = int(raw_damage * variance)
```

**Example — Drouot (shock 7) bombards Wellington (68,000):**
- base: 68,000 × 0.04 = 2,720
- multiplier: 1.0 + (7 / 15) = 1.467
- raw: 2,720 × 1.467 = 3,990
- with variance: ~3,192 to ~4,788 casualties per bombardment

**Example — PrinceAugust (shock 6) bombards Davout (48,000):**
- base: 48,000 × 0.04 = 1,920
- multiplier: 1.0 + (6 / 15) = 1.40
- raw: 1,920 × 1.40 = 2,688
- with variance: ~2,150 to ~3,226

### 4.2 Return Casualties (Counter-Battery / Wear)

Fixed small percentage of **artillery's own** army:

```
return_rate = 0.015  (1.5% of own strength)
variance = random.uniform(0.80, 1.20)
attacker_casualties = int(artillery.strength * return_rate * variance)
```

**Example — Drouot (25,000):**
- base: 25,000 × 0.015 = 375
- with variance: ~300 to ~450 casualties per bombardment

This represents counter-battery fire, gun wear, logistics attrition — not melee losses.

### 4.3 Bombardment Limit Per Turn

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

**Turn reset:** Clear in `world_state.py _process_tactical_states()` alongside `attacks_this_turn` and `moved_this_turn`.

### 4.4 No Battle Outcome

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
- No terrain defense bonus — shells fall regardless of terrain
- No stance modifiers on damage calculation (bombardment is mechanical, not tactical posture)

**Systems that DO trigger from bombardment:**
- Fort degradation (§5)
- Bombardment streak tracking (existing, for objections)
- Idle turn reset (artillery is active)
- `in_combat_this_turn` = True (for cannon fire interrupt detection)
- AP cost: 1 per bombardment (standard attack cost)
- Event log: new "bombardment" event type (§8)

### 4.5 Morale Effects

| Target | Morale Change | Rationale |
|--------|--------------|-----------|
| **Attacker (artillery)** | None | Guns fired safely, no risk |
| **Defender** | -3 per bombardment | Sustained shelling erodes morale slowly |

Sustained bombardment (2/turn × multiple turns) will grind defender morale down. At -3 per salvo, -6 per turn, a defender at 100% morale reaches forced retreat threshold (25%) after ~13 bombardments across ~7 turns. This makes bombardment a **slow siege tool**, not an instant win.

### 4.6 Defender Reduced to Zero

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

## 7. Artillery Objections (Revised)

The current objection triggers for artillery are:
- **Impatient bombardier** (aggressive): streak >= 3 + target softened → MILD "Let the infantry finish it!"
- **Patient gunner** (cautious): moving while adjacent target still has forts → MILD "One more barrage!"

These need revision to reflect the new bombardment system and add more flavorful artillery personality.

### 7.1 Cautious Artillery (Drouot) — "The Sage of the Grand Army"

Drouot is methodical, precise, and protective of his guns. He objects when:

| Trigger | Condition | Level | Flavor |
|---------|-----------|-------|--------|
| **Bombard the strong** | Bombardment target has > 50,000 troops AND Drouot has < 20,000 | MILD | "The enemy force is vast, Sire. Our shells will sting but not wound. A smaller target would feel our fire more keenly." |
| **Reckless repositioning** | Move order while bombardment streak >= 2 AND adjacent fort not yet cracked | MODERATE | "One more barrage and their walls crumble, Sire! Moving now wastes everything we've achieved." |
| **Ordered into melee** | Attack when in same region as enemy (real battle, not bombardment) | STRONG | "You would send my gunners into the bayonet line? These are artillerists, not infantry. We serve you best from range." |
| **Wasted fire** | Bombardment target already has 0 fort bonus AND < 10,000 troops | MILD | "The target is already broken, Sire. Infantry can sweep them aside. My ammunition is better spent elsewhere." |
| **No targets adjacent** | Attack order but no valid bombardment targets in range | N/A (pre-validation fail, not objection) | Standard "no enemies in range" message |

### 7.2 Aggressive Artillery (Hypothetical / Future Marshals)

For future aggressive artillery marshals (not currently in game, but future-proofing):

| Trigger | Condition | Level | Flavor |
|---------|-----------|-------|--------|
| **Ordered to hold fire** | Defend/hold/fortify when enemy is adjacent | MILD | "The enemy is RIGHT THERE and you want me to sit idle? Let me fire!" |
| **Bombardment too cautious** | Ordered to stop bombarding when target is weakened | MILD | "We have them reeling! One more salvo finishes this!" |

### 7.3 Removing Old Triggers

The following existing triggers should be **replaced** by the new ones above:

- `objection_v2.py` line 772-782: "Impatient bombardier" → Replace with §7.1 "Wasted fire" (more specific)
- `objection_v2.py` line 850-861: "Patient gunner" move hesitancy → Replace with §7.1 "Reckless repositioning" (stronger, MODERATE instead of MILD)

### 7.4 Objection Flavor Text (disobedience.py)

New V1 flavor text entries for artillery objections:

```python
'cautious': {
    # ... existing entries ...
    'bombard_the_strong': [
        "\"{name} adjusts his telescope. \"That is a vast encampment, Sire. Our guns will harass them, "
        "but true damage requires a softer target.\"",
        "\"{name} calculates quietly. \"At this range, against those numbers... we will expend much "
        "powder for little effect. Might I suggest a more vulnerable position?\"",
    ],
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
    'wasted_fire': [
        "\"{name} lowers his telescope. \"The position is already shattered, Sire. "
        "Sending more shells into rubble serves no purpose. Let the infantry advance.\"",
        "\"{name} gestures toward the distant target. \"Look — they have no walls left, "
        "and barely enough men to hold a picket line. Save my powder for a worthy target.\"",
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
    "fort_degraded": True,
    "fort_old": 0.16,
    "fort_new": 0.06,
}
```

**Fog of war filtering:** Bombardment events follow the same nation-based fog filter as battle events. Player sees their own bombardments. Enemy bombardments visible only if the target region is at PARTIAL+ visibility.

---

## 9. Berthier Report

### 9.1 New Bombardment Observations

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
```

### 9.2 Selection Logic

```
IF defender reduced to 0 → "bombardment_target_broken"
ELIF fort_degraded → "bombardment_fort_cracking"
ELIF defender_casualties < defender.strength * 0.02 → "bombardment_ineffective"
ELSE → "bombardment_effective"
```

---

## 10. Godot Frontend

### 10.1 Bombardment Result Display

The bombardment result dict returned to Godot differs from a battle result:

```python
{
    "success": True,
    "action": "bombardment",   # NOT "attack" — Godot uses this to choose display
    "message": "...",           # Narrative text
    "bombardment_result": {
        "attacker": {"name": "Drouot", "casualties": 375, "remaining": 24625},
        "defender": {"name": "Wellington", "casualties": 3990, "remaining": 64010, "morale": 97},
        "fort_degraded": True,
        "fort_old": 0.16,
        "fort_new": 0.06,
        "bombardments_remaining": 1,  # How many more this turn
        "berthier_observation": "...",
    }
}
```

### 10.2 HUD Advisory

When artillery has bombardments remaining and valid targets adjacent, the Berthier advisory system should note:

> "Drouot's guns are positioned to bombard Waterloo. (1 bombardment remaining today)"

When limit reached:

> "Drouot's battery has expended today's ammunition. Available to fire next turn."

---

## 11. Serialization

### 11.1 New Fields

| Field | Class | Type | Default | Purpose |
|-------|-------|------|---------|---------|
| `bombardments_this_turn` | Marshal | int | 0 | Tracks bombardments fired this turn (max 2) |

### 11.2 Checklist

- [ ] Add to `Marshal.__init__`
- [ ] Add to `Marshal.to_dict()`
- [ ] Add to `Marshal.from_dict()` with `.get('bombardments_this_turn', 0)`
- [ ] Reset in `world_state.py` turn processing (alongside `attacks_this_turn`)
- [ ] Run `pytest tests/test_serialization_enforcement.py -v`
- [ ] Update `docs/SAVE_FORMAT_REFERENCE.md`

---

## 12. Diminishing Returns (Future Consideration)

If playtesting reveals "park and shell" is still too dominant even with the 2/turn limit, add diminishing returns based on `bombardment_streak`:

```
streak 0-2: full damage (100%)
streak 3-4: 75% damage (target has dug in)
streak 5+:  50% damage (deeply entrenched)
```

This is NOT part of the initial implementation — flag for playtesting evaluation. The 2/turn limit + low per-shot damage + 1 AP cost should be sufficient.

---

## 13. Files to Modify

| File | Changes |
|------|---------|
| `backend/models/marshal.py` | Add `bombardments_this_turn` field, serialization |
| `backend/commands/executor.py` | Route ranged artillery to new `_execute_bombardment()`, keep same-region in `_execute_attack()` |
| `backend/game_logic/combat.py` | Remove ranged bombardment 50% reduction (no longer needed — bombardment doesn't use resolve_battle) |
| `backend/game_logic/battle_report.py` | Add bombardment observations, bombardment report generator |
| `backend/commands/objection_v2.py` | Replace artillery triggers per §7 |
| `backend/commands/disobedience.py` | Add artillery flavor text per §7.4 |
| `backend/models/world_state.py` | Reset `bombardments_this_turn` at turn start |
| `backend/main.py` | Pass through bombardment result fields to API response |
| `godot-client/...main.gd` | Handle `bombardment_result` display |
| `docs/SAVE_FORMAT_REFERENCE.md` | Document new field |
| `docs/SYSTEMS_REFERENCE.md` | Document bombardment vs battle distinction |
| `CLAUDE.md` | Update artillery mechanics references, add bombardment to troubleshooting |

---

## 14. Test Plan

### 14.1 Unit Tests

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

### 14.2 Integration Tests

- [ ] AI artillery (PrinceAugust) uses bombardment correctly
- [ ] Bombardment streak tracks across turns
- [ ] Objection triggers fire correctly per §7
- [ ] Event log records bombardment events
- [ ] Fog of war filters bombardment events correctly

### 14.3 Manual / Curl Tests

```bash
# Drouot bombards Wellington from adjacent region
curl -X POST http://127.0.0.1:8005/command \
  -H "Content-Type: application/json" \
  -d '{"command": "Drouot, bombard Wellington"}' | python -m json.tool

# Verify 3rd bombardment is blocked
# (after 2 successful bombardments in same turn)

# Verify same-region attack uses full battle
# (move Drouot to Wellington's region first)
```

---

## 15. Migration Notes

- Old saves: `bombardments_this_turn` defaults to 0 via `.get()` — no migration needed
- The `ranged bombardment 50% return casualties` code in `combat.py` lines 406-423 should be **removed** once bombardment has its own path (dead code otherwise)
- The `bombardment_range_message` field in battle results becomes unused for ranged attacks but stays for backward compat until confirmed safe to remove
