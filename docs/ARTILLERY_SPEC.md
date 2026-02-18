# Artillery Unit Type — Implementation Spec

> **Phase 6 Feature (final item). Ready for implementation.**
> **Complexity:** Medium (1 session, Opus)
> **Prerequisites:** Manpower Pools (DONE), Terrain (DONE), Combat modifiers (DONE)
> **Reviewed:** February 2026. All numbers evaluated, edge cases resolved.

---

## Design Intent

Artillery is the third marshal type alongside infantry and cavalry. It follows the same binary pattern: `marshal.artillery = True`, like `marshal.cavalry = True`. A marshal IS artillery or they aren't.

Artillery is a **positional attack platform** that rewards planning and punishes hasty movement. It can bombard adjacent regions to soften enemy positions but never advances to capture territory. Strong at cracking fortifications and holding ground, but vulnerable when caught moving or without screening infantry.

**The strategic fantasy:** Position your guns adjacent to the enemy's fortified position. Bombard them turn after turn, degrading their defenses twice as fast as infantry could. Then your infantry walks in for the kill. The player who positions artillery well controls the battlefield.

**The core tension:** Artillery CANNOT capture territory. It softens positions but always needs infantry or cavalry to follow up and take the ground. This creates natural combined arms — artillery alone can never win a campaign. But infantry without artillery has to chew through fortifications the hard way.

**Why this matters for the era:** Napoleonic warfare without artillery is chess without bishops. Napoleon's Grand Battery at Waterloo, the bombardment at Austerlitz, the massed guns at Wagram — artillery was the decisive arm. The game currently has infantry slugfests and cavalry charges. Artillery adds the third dimension that makes real combined-arms strategy possible.

---

## All Numbers (Final)

### Core Properties

| Property | Value | Rationale |
|----------|-------|-----------|
| `artillery: bool` | True | Binary type flag (same pattern as cavalry) |
| `movement_range` | 1 | Same as infantry — guns are heavy |
| Attack range | 1 | Can attack adjacent regions (same range as infantry) |
| Can attack after moving? | NO | Must set up. Fundamental constraint. |
| Advances on win? | NO | Positional platform — never captures territory |
| Engagement-locked? | YES | If enemies in own region, must fight them (existing mechanic) |
| Glorious Charge? | BANNED | Guns don't charge |
| Scout? | ALLOWED | Forward observers, ranging shots |
| Garrison? | ALLOWED | Leaving guns to defend a position — historical |
| Fortify? | ALLOWED | Digging in gun emplacements — natural fit |
| Drill? | ALLOWED | Target practice, improving accuracy — historical |

### How Artillery Differs from Infantry

Artillery and infantry share `movement_range=1` and attack range 1. The differences:

| Behavior | Infantry | Artillery |
|----------|----------|-----------|
| Attack after moving? | YES | NO (must set up first) |
| Advance on win? | YES (captures territory) | NO (stays in position) |
| Fort degradation per attack | 5% | 10% (twice as effective) |
| Cavalry counter? | No bonus | +30% cavalry attack bonus vs artillery |
| Defense when moved this turn | Normal | -25% (guns not set up) |
| PURSUE strategic order? | Allowed | BANNED |
| Glorious Charge? | N/A (infantry) | BANNED |

### Mutual Exclusivity

A marshal can be exactly ONE type:
- `cavalry=False, artillery=False` → Infantry
- `cavalry=True, artillery=False` → Cavalry
- `cavalry=False, artillery=True` → Artillery
- `cavalry=True, artillery=True` → **INVALID** (assert in `__init__`)

### Cavalry vs Artillery Counter

When cavalry attacks artillery: **+30% attack bonus**.

Applied in `combat.py` (not `marshal.py`) because it's a target-type interaction, not a marshal-intrinsic modifier. Same pattern as `TERRAIN_CAVALRY_EFFECTIVENESS` adjustment.

```python
# In combat.py, after shock_multiplier calculation:
if getattr(attacker, 'cavalry', False) and getattr(defender, 'artillery', False):
    shock_multiplier *= 1.30  # Cavalry devastates unscreened artillery
    cavalry_counter_message = f"{attacker.name}'s cavalry overruns {defender.name}'s gun line! (+30% attack)"
```

### Artillery Fort Degradation

When artillery attacks a fortified target, the defender's `defense_bonus` degrades by **10%** instead of the normal 5%. This stacks with existing degradation mechanics.

```python
# In combat.py, fortification degradation block:
degradation_amount = 0.10 if getattr(attacker, 'artillery', False) else 0.05
defender.defense_bonus = max(0, round(defender.defense_bonus - degradation_amount, 2))
```

After 2 artillery attacks: 20% fort degradation. Compare to 4 regular attacks for the same effect. Artillery is THE answer to turtling.

### Reduced Defense When Moved This Turn

If artillery moved this turn and gets attacked: **-25% defense penalty**. Same magnitude as the drilling penalty (caught unprepared).

Applied in `marshal.py get_defense_modifier()`:

```python
# Artillery moved this turn — caught in transit, guns not set up
if getattr(self, 'artillery', False) and getattr(self, 'moved_this_turn', False):
    modifier *= 0.75  # -25%
```

### Can't Attack After Moving

New field: `marshal.moved_this_turn: bool = False`
- Set to `True` when marshal moves (in `_execute_move`)
- Reset to `False` at turn start (in `_process_tactical_states`)
- Only blocks attacks for artillery marshals

```python
# In executor.py _execute_attack, early check:
if getattr(marshal, 'artillery', False) and getattr(marshal, 'moved_this_turn', False):
    return {
        "success": False,
        "message": f"{marshal.name}'s artillery is still setting up after repositioning. "
                   f"Available to fire next turn."
    }
```

### Win Without Advancing

When artillery wins combat:
- Defender takes casualties/retreats as normal
- Artillery stays in its original region (no `marshal.move_to()`)
- The target region is NOT captured — must be taken by infantry/cavalry
- Message: "{marshal.name}'s bombardment forces {defender.name} to retreat from {region}. Region must be secured by infantry to complete the capture."

When artillery attacks an enemy in the SAME region and wins:
- Enemy retreats, artillery holds the region
- If artillery already controlled the region, it remains under control
- This is the defensive use case — artillery holds ground

### Engagement Lock (Existing Mechanic)

If enemies are in the artillery's own region, the artillery can ONLY attack those enemies. It cannot attack adjacent targets while engaged. This is how ALL marshal types already work — no new code needed for this rule.

### Out-of-Range Attack Handling

If player orders artillery to attack a target beyond range 1:
- Currently, out-of-range attacks auto-promote to PURSUE strategic order
- For artillery: block the PURSUE promotion with a clear message
- "Target out of range. {marshal.name}'s artillery can only engage adjacent regions."

```python
# In executor.py, inside the `if distance > marshal.movement_range:` block:
if getattr(marshal, 'artillery', False):
    return {
        "success": False,
        "message": f"Target out of range. {marshal.name}'s artillery can only engage adjacent regions."
    }
# ... existing PURSUE auto-upgrade for non-artillery
```

---

## Personality × Artillery Interactions

### Aggressive Artillery

**Viable but risky.** An aggressive artillery marshal is a glass cannon.

| Mechanic | Interaction | Assessment |
|----------|-------------|------------|
| +15% attack in aggressive stance | Amplifies bombardment | FUN — risk/reward |
| -10% defense in aggressive stance | More vulnerable to cavalry | BALANCED — meaningful trade-off |
| Idle turn objection (2-3 turns → MILD, 4+ → MODERATE) | **Attacking counts as activity** — resets idle_turns | CORRECT — existing behavior |
| Recklessness system | Does NOT apply — `is_reckless_cavalry` requires `cavalry AND aggressive`. Artillery is not cavalry. | CORRECT — no interaction |

**Verdict:** Works cleanly. Aggressive artillery = high bombardment damage but vulnerable if caught.

### Cautious Artillery (Drouot)

**Natural fit.** This is the "park next to the enemy and wear them down" personality.

| Mechanic | Interaction | Assessment |
|----------|-------------|------------|
| +20% defense in defensive stance | Strong prepared position | INTENDED |
| Outnumbered bonus (+10%) | Artillery formations are smaller, usually outnumbered | THEMATIC |
| Counter-punch after defending | Cautious artillery counter-bombards next turn for free | ALLOWED — earned by surviving |
| Resists orders to move | Cautious artillery refusing to leave position | HISTORICALLY ACCURATE |

**Verdict:** Perfect fit. Cautious + artillery is the strongest defensive combination but has natural limits (can't capture anything).

### Literal Artillery

**Safe and predictable.** Does exactly what you order.

| Mechanic | Interaction | Assessment |
|----------|-------------|------------|
| Hold position (+15% defense) | Holding + artillery = strong prepared defense | BALANCED |
| Precision Execution (+1 all skills) | Clear orders boost accuracy | THEMATIC |
| No complaints about positioning | Sits where you put it | RELIABLE |

**Verdict:** Good "utility" choice. Reliable but not exciting.

### Max Defensive Stack Calculations

**Cautious artillery on hills + fortified + fort building + defensive stance:**

| Modifier | Source | Value |
|----------|--------|-------|
| Terrain defense bonus | Hills (defender's region) | +15% |
| Fort building | Fortification building | +25% |
| Fortify bonus | Marshal's defense_bonus | +16% (typical after 2 turns) |
| Defensive stance | Stance modifier | ×1.15 |
| Cautious + defensive | Personality modifier | ×1.15 additional |
| Cautious outnumbered | Personality modifier | ×1.10 |

**Total: base × (1 + 0.15 + 0.25) × 1.15 × (1 + 0.16) × 1.15 × 1.10 ≈ base × 2.37**

**Is this crackable?** YES:
- Cavalry counter (+30%) cuts through the stack
- Artillery bombardment degrades the fortify bonus (-10% per attack, twice the normal rate)
- 2-3 bombardments + cavalry charge = position cracked
- This is EXACTLY the combined-arms gameplay we want

**Compare to current infantry max:** ~2.11x (same stack minus hills terrain affinity). The 12% difference from hills is meaningful but not game-breaking.

---

## Stance Interactions

### Fortified + Artillery
- ALLOWED. Historically accurate (digging in gun emplacements).
- Strong but crackable (see max stack above).
- Cavalry defensive limits (3 turns → auto-switch) do NOT apply to artillery. Artillery SHOULD want to sit fortified. Don't penalize artillery for being artillery.

### Aggressive + Artillery
- ALLOWED. Glass cannon — high attack, weak defense.
- Cavalry counter + aggressive defense penalty = very vulnerable if caught.
- No recklessness interaction (recklessness requires `cavalry AND aggressive`).

### Defensive + Artillery
- ALLOWED. Natural fit.
- No "3 turns defensive → auto-switch" penalty. That's cavalry-only.

### Drill + Artillery
- ALLOWED. "Drilling artillery" = target practice, improving accuracy. Historically accurate.
- Drill bonus (+20% attack) applies to bombardment.
- If caught drilling when attacked: -25% defense (existing mechanic).

### Banned Actions
- **Glorious Charge:** BANNED. Check `marshal.artillery` in `_execute_glorious_charge()` early return.
- **PURSUE:** BANNED. Artillery doesn't chase retreating enemies. Block in strategic command handling.
- **Scout:** ALLOWED. Forward observers, ranging shots.
- **Garrison:** ALLOWED. Leaving guns behind to defend a position.

---

## Edge Cases — Resolved

### Engagement Lock
**Decision: Use existing mechanic.** When enemies are in artillery's region, artillery can ONLY fight them. Cannot fire at adjacent targets while engaged. This already works for all marshal types — zero new code.

### Out-of-Range Attacks
**Decision: Block with error, don't auto-promote to PURSUE.** Artillery cannot PURSUE (banned). Intercept in the `if distance > marshal.movement_range:` block before the PURSUE auto-upgrade code path.

### Win-Without-Advancing + Strategic Orders

| Order | Artillery Behavior | Decision |
|-------|-------------------|----------|
| PURSUE | **BANNED for artillery.** Strategic parser rejects PURSUE for artillery marshals with clear message. | Simple rule |
| MOVE_TO | Works normally. Can't attack on arrival turn (`moved_this_turn`). | No special handling |
| HOLD | **Perfect for artillery.** No issues. | Natural fit |
| SUPPORT | ALLOWED. Artillery moves toward supported marshal using standard SUPPORT logic. If enemies are adjacent, can attack them (if not moved this turn). | Standard behavior |

### Attack-on-Arrival for Strategic MOVE_TO
- `attack_on_arrival` flag on MOVE_TO orders: **BLOCKED for artillery.** Artillery can't attack on the turn it arrives (moved_this_turn = True). Order completes at destination, next turn artillery can fire.

### AI Behavior
- AI artillery: move → wait (set up) → attack adjacent. Two-turn setup cycle handled naturally by `moved_this_turn`.
- AI artillery does NOT advance into enemy-occupied regions (since attack doesn't capture and moving INTO enemies is blocked when visible).
- AI artillery target selection: prioritize fortified targets (highest fort degradation value), then nearest.
- AI cavalry prioritizes exposed artillery targets (target selection preference).
- AI won't build stables for artillery marshals (existing `_should_build_stables` checks `marshal.cavalry`).

### Manpower Pool
- Artillery pool: same pattern as cavalry pool. `{"infantry": X, "cavalry": Y, "artillery": Z}`
- Starting pools: France 10,000, Britain 5,000, Prussia 5,000
- Regen: base 300/turn + bonus per urban region controlled (+200). Urban = arsenals/foundries.
- Recruit batch: 3,000 (smaller than infantry 10,000 and cavalry 5,000)
- Gold cost: 400g base (most expensive — trained artillerists are rare)
- Cap: 20,000

### Marshal Death and Respawn
- Same as other types: respawn at capital with minimal strength, recruit from artillery pool.

### Moved-This-Turn and Strategic Orders
- MOVE_TO: artillery moves each turn. `moved_this_turn = True` on each move. Cannot attack during movement phase. On arrival (order complete), cannot attack that turn either.
- Next turn after arrival: `moved_this_turn` resets, artillery can fire.

### Interaction with Existing Systems
- **Glorious Charge:** `is_reckless_cavalry` requires `cavalry AND aggressive`. Artillery is not cavalry. No recklessness, no charge popup, no auto-charge. Clean separation.
- **Cavalry defensive limits:** 3-turn defensive stance auto-switch and 3-turn fortify auto-unfortify are cavalry-only. Artillery is unaffected. Artillery SHOULD want to sit defensive/fortified.
- **Exhaustion system:** Normal. Multiple attacks in one turn still accumulate exhaustion penalty. (Unlikely for artillery since can't-attack-after-moving limits to 1 attack/turn in most cases, but counter-punch could create a second.)

---

## Balance Assessment

### Is Artillery OP?

**Can't capture territory:**
- Every turn spent bombarding is a turn NOT conquering. The game has victory conditions based on territory control, not kill count. Without infantry follow-up, artillery bombardment is strategically wasteful.

**Can't attack after moving:**
- Repositioning costs a full turn of no combat. The player who has to constantly reposition their artillery is losing tempo.

**Engagement lock:**
- If enemies enter artillery's region, artillery must fight them directly — no firing at adjacent targets. This prevents artillery from being used offensively while enemies are present.

**Verdict: NOT OP.** No capture + can't-move-and-shoot + engagement lock = artillery rewards planning but doesn't dominate.

### Is Artillery UP?

**Movement 1 + can't attack on move turn = slow repositioning:**
- This is the POINT. Artillery rewards planning. The player who positions well wins. Historical accuracy — repositioning guns was a major commitment.

**Cavalry counter is harsh:**
- +30% is strong but not instant death. Fortified artillery on hills still has 2.37x defense multiplier. The counter is: DON'T LET CAVALRY REACH YOUR GUNS (screen with infantry).

**Can't capture means can't win alone:**
- Correct — artillery needs combined arms. This is a feature, not a bug. It makes team composition matter.

**Verdict: NOT UP.** Artillery has clear strengths (fort degradation, defensive bonuses, positional warfare) and clear weaknesses (slow, cavalry-vulnerable, can't capture). Every unit type answers something different.

### Combined Arms Triad

| Situation | Best Unit | Why |
|-----------|----------|-----|
| Crack fortified position | Artillery | 10% fort degradation per attack (2x infantry rate) |
| Capture open territory | Cavalry | Speed, range-2 movement, advances on win |
| Hold territory | Infantry | Cheap, captures on win, strong general defense |
| Break cavalry | Infantry | No cavalry counter bonus against infantry |
| Destroy artillery | Cavalry | +30% counter bonus, speed to close distance |
| Defend a key region | Artillery | Fort degradation on attackers, no-advance holds ground |

**Degenerate strategies:**
- All artillery: CAN'T WIN — can't capture territory
- All cavalry: Loses to fortified infantry, expensive to reinforce
- All infantry: Works but struggles against fortified positions — slow grinding
- 2 infantry + 1 artillery + 1 cavalry: The ideal Waterloo comp. Davout holds, Drouot softens, Ney flanks, Grouchy follows orders.

---

## Historical Evaluation

### Does this feel like Napoleonic artillery?

| Historical Event | Mechanic | Assessment |
|-----------------|----------|------------|
| Grand Battery at Waterloo (80 guns) | Adjacent bombardment + fort degradation | YES — positioned adjacent, softened Allied line |
| Austerlitz (Pratzen Heights) | Hills terrain defense bonus for artillery position | YES — elevated position dominates |
| Wagram (concentrated breakthrough) | Artillery softens → infantry advances to capture | YES — combined arms |
| Wellington's reverse slopes | Retreat/reposition as counterplay to bombardment | SUFFICIENT |
| Counter-battery fire | Artillery vs artillery resolves normally | YES — mutual bombardment |

### Waterloo Scenario Marshals

**France — Add Drouot:**

```python
"Drouot": Marshal(
    name="Drouot",
    location="Paris",
    strength=25000,        # Smaller than infantry corps
    personality="cautious", # "The Sage of the Grand Army" — methodical, precise
    nation="France",
    movement_range=1,
    tactical_skill=8,
    skills={
        "tactical": 8,      # Excellent artillerist
        "shock": 7,          # Effective bombardment
        "defense": 6,        # Reasonable defense
        "logistics": 7,      # Well-organized
        "administration": 6, # Competent
        "command": 7         # Respected
    },
    ability={
        "name": "Sage of the Grand Army",
        "description": "Drouot's precise artillery fire is devastatingly accurate",
        "trigger": "when_attacking_fortified",
        "effect": "+2 fort degradation per bombardment (TODO: Wire ability)"
    },
    starting_trust=80,
    artillery=True,
    spawn_location="Paris"
)
```

**Prussia — Add PrinceAugust (AI testing marshal):**

```python
"PrinceAugust": Marshal(
    name="PrinceAugust",
    location="Netherlands",   # With Blucher's army
    strength=20000,            # Smaller artillery corps
    personality="cautious",    # Methodical Prussian gunnery
    nation="Prussia",
    movement_range=1,
    tactical_skill=7,
    skills={
        "tactical": 7,      # Good artillerist
        "shock": 6,          # Decent bombardment
        "defense": 6,        # Reasonable defense
        "logistics": 6,      # Organized
        "administration": 5, # Average
        "command": 6         # Competent
    },
    ability={
        "name": "Prussian Gunnery",
        "description": "Disciplined Prussian artillery fire",
        "trigger": "when_attacking_fortified",
        "effect": "Standard artillery (no special bonus)"
    },
    starting_trust=70,
    artillery=True,
    spawn_location="Netherlands"
)
```

**Rationale:** PrinceAugust gives the AI an artillery marshal for testing AI bombardment logic, positioning, cavalry-targeting-artillery, and manpower pool behavior. Can be kept permanently (gives Prussia combined arms) or removed after testing if balance is wrong. France still has the advantage: Drouot (skill 8, trust 80) vs PrinceAugust (skill 7, trust 70) + France has better artillery production (Paris urban regen).

**Starting lineup:**
- France (4 marshals): Ney (cav/aggressive), Davout (inf/cautious), Grouchy (inf/literal), Drouot (art/cautious)
- Britain (2 marshals): Wellington (inf/cautious), Uxbridge (cav/aggressive)
- Prussia (3 marshals): Blucher (inf/aggressive), Gneisenau (inf/cautious), PrinceAugust (art/cautious)
- **Total: 4 vs 5.** Coalition has numbers, France has quality. Historically accurate.

---

## Files to Modify

### Single Session (Opus)

| File | Changes | Difficulty |
|------|---------|------------|
| `marshal.py` | `artillery: bool` field, `moved_this_turn: bool` field, mutual exclusivity assert, -25% defense in `get_defense_modifier()` when moved, `to_dict/from_dict`, `__repr__` unit type, Drouot + PrinceAugust in starting marshals | 2/5 |
| `combat.py` | Cavalry-vs-artillery counter (+30%), artillery fort degradation (10% vs 5%), cavalry counter message, battle report context | 2/5 |
| `executor.py` | Can't-attack-after-moving check (early return), no-advance-on-win (skip `move_to` for artillery), block PURSUE auto-promotion for artillery, ban glorious charge for artillery, set `moved_this_turn=True` in `_execute_move`, artillery-specific battle messaging | 3/5 |
| `world_state.py` | Reset `moved_this_turn` at turn start in `_process_tactical_states`, artillery manpower pool constants + starting pools + regen + `get_artillery_regen_rate()` helper + cap, serialization | 2/5 |
| `enemy_ai.py` | Artillery can't-attack-after-moving awareness, no advance into enemy regions, prioritize fortified targets, cavalry targets exposed artillery, pool-aware recruit, skip stables for artillery | 3/5 |
| `llm_client.py` | "bombard"/"barrage"/"shell"/"cannonade" keywords → attack action | 1/5 |
| `prompt_builder.py` | Few-shot examples for artillery commands | 1/5 |
| `battle_report.py` | Artillery-specific observations (bombardment, fort degradation note, cavalry counter) | 1/5 |

**No changes to:** `region.py` (no artillery terrain table — defender terrain bonus is sufficient), `validation.py` (reuse "attack" action), `main.py` (verify passthrough only)

**Estimated tests: ~100**

---

## Implementation Difficulty Ratings

| Subsystem | Difficulty | Test Count | Notes |
|-----------|-----------|------------|-------|
| `marshal.artillery` bool + mutual exclusivity + serialization | 1/5 | ~8 | Follow cavalry pattern exactly |
| `moved_this_turn` field + reset at turn start | 1/5 | ~5 | Simple bool lifecycle |
| Can't-attack-after-moving check | 1/5 | ~8 | Early return in `_execute_attack` |
| Win-without-advancing | 2/5 | ~8 | Skip `move_to` + capture for artillery in post-combat |
| Block PURSUE auto-promotion for artillery | 1/5 | ~5 | One check in range block |
| Fort degradation 10% vs 5% | 1/5 | ~5 | Conditional on attacker type |
| Cavalry counter +30% | 1/5 | ~5 | Same pattern as terrain cavalry effectiveness |
| Moved-this-turn -25% defense | 1/5 | ~5 | Add to `get_defense_modifier()` |
| Ban glorious charge for artillery | 1/5 | ~3 | Early return |
| AI artillery behavior | 3/5 | ~20 | Bombardment logic, target priorities, positioning |
| Parser aliases (bombard/shell) | 1/5 | ~3 | Keyword additions |
| Manpower pool (artillery) | 2/5 | ~12 | Follow cavalry pool pattern exactly |
| Starting marshals (Drouot + PrinceAugust) | 1/5 | ~5 | Data entry |
| Battle report artillery observations | 1/5 | ~5 | Template additions |

**TOTAL: 1 session (Opus). ~97 tests.**

---

## Smoke Test Gates

```bash
# 1. Artillery can't attack after moving
curl -X POST http://127.0.0.1:8005/command -H "Content-Type: application/json" \
  -d '{"command": "Drouot move to Belgium"}' | python -m json.tool
curl -X POST http://127.0.0.1:8005/command -H "Content-Type: application/json" \
  -d '{"command": "Drouot attack Wellington"}' | python -m json.tool
# Expected: "artillery is still setting up"

# 2. Artillery attacks adjacent, doesn't advance
# (After next turn, Drouot at Belgium, Wellington at Waterloo — adjacent)
curl -X POST http://127.0.0.1:8005/command -H "Content-Type: application/json" \
  -d '{"command": "Drouot attack Wellington"}' | python -m json.tool
# Expected: combat resolves, Drouot stays at Belgium

# 3. Out-of-range attack blocked (not promoted to PURSUE)
curl -X POST http://127.0.0.1:8005/command -H "Content-Type: application/json" \
  -d '{"command": "Drouot attack Blucher"}' | python -m json.tool
# Expected: "out of range, can only engage adjacent"

# 4. Economy report shows artillery pool
curl -X POST http://127.0.0.1:8005/command -H "Content-Type: application/json" \
  -d '{"command": "economy"}' | python -m json.tool
# Expected: Infantry/Cavalry/Artillery pools shown

# 5. Recruit for artillery marshal
curl -X POST http://127.0.0.1:8005/command -H "Content-Type: application/json" \
  -d '{"command": "recruit for Drouot"}' | python -m json.tool
# Expected: 3,000 artillery recruited, pool decrements

# 6. AI artillery behavior (end turn, observe enemy phase)
curl -X POST http://127.0.0.1:8005/command -H "Content-Type: application/json" \
  -d '{"command": "end turn"}' | python -m json.tool
# Expected: PrinceAugust positions/bombards sensibly
```

---

## What This Does NOT Include (Cut / Deferred)

| Feature | Status | Rationale |
|---------|--------|-----------|
| Range-2 bombardment | CUT | Same-range-as-infantry with no-advance is simpler, sufficient, and more historically grounded |
| Separate "bombard" action type | CUT | Reuse "attack" with context messaging. Avoid 8-step action pattern. |
| Artillery terrain effectiveness table | CUT | Defender's terrain defense bonus already handles combat terrain. One modifier layer is enough. |
| Infantry sustained combat weakness | CUT | Over-engineering. Existing constraints are sufficient. |
| Blind bombardment (STALE/UNKNOWN fog) | CUT | Same fog rules as all other attacks. PARTIAL+ only. |
| Artillery-vs-artillery counter-battery bonus | CUT | Normal combat is fine. No special modifier needed. |
| AI screening coordination | DEFERRED to Phase 7 | Requires multi-marshal coordination system. |
| Arsenal building (artillery regen) | DEFERRED | Urban terrain bonus is sufficient for now. Evaluate for 1805. |
| 1805 nation artillery marshals | DEFERRED | Add during 1805 data entry phase. |

---

## Testing Checklist

### Core Type
- [ ] `marshal.artillery = True` sets correctly
- [ ] `cavalry=True, artillery=True` raises assertion error
- [ ] `movement_range = 1` for artillery marshals
- [ ] `to_dict/from_dict` roundtrip for artillery + moved_this_turn
- [ ] `moved_this_turn` resets at turn start
- [ ] `__repr__` shows "artillery" unit type

### Attack Behavior
- [ ] Artillery can attack adjacent region (distance 1)
- [ ] Artillery CANNOT attack distance 2+ (blocked with error, NOT promoted to PURSUE)
- [ ] Artillery engagement-locked when enemies in own region (existing mechanic, verify)
- [ ] Infantry can attack at distance 1 (unchanged)
- [ ] Cavalry can attack at distance 1 and 2 (unchanged)

### Can't Attack After Moving
- [ ] Artillery moves → attack same turn → blocked with Berthier message
- [ ] Artillery moves → next turn → attack works
- [ ] Infantry moves → attack same turn → works (no restriction)
- [ ] Cavalry moves → attack same turn → works (no restriction)
- [ ] Strategic MOVE_TO: artillery can't attack during movement turns
- [ ] Strategic MOVE_TO with attack_on_arrival: blocked for artillery

### Win Without Advancing
- [ ] Artillery wins adjacent attack → stays in original region, target NOT captured
- [ ] Artillery wins same-region attack → enemy retreats, artillery holds region
- [ ] Infantry wins → advances and captures (unchanged)
- [ ] Cavalry wins → advances and captures (unchanged)
- [ ] Message indicates region must be secured by infantry (adjacent attack)

### Cavalry Counter
- [ ] Cavalry attacking artillery gets +30% attack bonus
- [ ] Cavalry attacking infantry gets NO bonus (unchanged)
- [ ] Infantry attacking artillery gets NO bonus
- [ ] Battle report shows cavalry counter message

### Fort Degradation
- [ ] Artillery attack degrades defender fort by 10% (not 5%)
- [ ] Regular (non-artillery) combat still degrades fort by 5%
- [ ] Fort building (fortification_bonus) NOT affected by either

### Personality
- [ ] Aggressive artillery: +15% attack stance works
- [ ] Cautious artillery: counter-punch works after defending
- [ ] Literal artillery: hold position +15% defense works
- [ ] No recklessness on artillery (is_reckless_cavalry = False)
- [ ] Cavalry defensive limits do NOT apply to artillery

### Banned Actions
- [ ] Glorious charge blocked for artillery with clear message
- [ ] PURSUE strategic order blocked for artillery with clear message

### Moved This Turn Defense
- [ ] Artillery moved + attacked by enemy → -25% defense
- [ ] Artillery NOT moved + attacked → normal defense
- [ ] Non-artillery marshal moved + attacked → no penalty (unchanged)

### AI Behavior
- [ ] AI artillery attacks adjacent enemies when not moved this turn
- [ ] AI artillery does NOT try to advance into enemy-held regions
- [ ] AI artillery prioritizes fortified targets
- [ ] AI cavalry prioritizes exposed artillery targets
- [ ] AI does not build stables for artillery marshals
- [ ] AI checks artillery pool before recruiting for artillery marshal
- [ ] AI positions artillery adjacent to front, not in enemy territory

### Manpower Pool
- [ ] Artillery pool initializes correctly per nation (France 10k, Britain 5k, Prussia 5k)
- [ ] Artillery recruit draws from artillery pool (3,000 troops)
- [ ] Artillery recruit costs 400g base
- [ ] Pool regen: base 300 + 200 per urban region
- [ ] Economy report shows all three pools
- [ ] HUD shows artillery pool count
- [ ] Pool cap enforced (20,000)

### Parser
- [ ] "bombard Wellington" → attack action targeting Wellington
- [ ] "shell the position" → attack action
- [ ] "cannonade" → attack action
- [ ] Recruit for artillery marshal → auto-artillery pool

### Serialization
- [ ] `test_serialization_enforcement.py` passes with new fields
- [ ] Old saves without artillery/moved_this_turn fields load correctly (backward compat)
- [ ] Old saves without artillery manpower pool get correct defaults

---

## Manpower Pool Constants

```python
# ═══════ ARTILLERY POOL CONSTANTS ═══════
ARTILLERY_RECRUIT_AMOUNT = 3000          # Smallest batch — trained crews are rare
ARTILLERY_RECRUIT_GOLD_COST_BASE = 400   # Most expensive — guns + training
ARTILLERY_BASE_REGEN = 300               # Per nation per turn (slow — foundries)
URBAN_ARTILLERY_REGEN = 200              # Bonus per urban region controlled (arsenals)
MAX_ARTILLERY_POOL = 20000               # Pool cap

DEFAULT_MANPOWER_POOLS = {
    "France": {"infantry": 80000, "cavalry": 15000, "artillery": 10000},
    "Britain": {"infantry": 50000, "cavalry": 8000, "artillery": 5000},
    "Prussia": {"infantry": 60000, "cavalry": 10000, "artillery": 5000},
}
```

### Regen Scenarios (Waterloo map: 3 urban regions — Paris, Vienna, Milan)

| Nation | Urban Controlled (start) | Base Regen | Urban Bonus | Total |
|--------|--------------------------|-----------|-------------|-------|
| France | 1 (Paris) | 300 | +200 | 500/turn |
| Britain | 0 | 300 | 0 | 300/turn |
| Prussia | 0 | 300 | 0 | 300/turn |

France rebuilds faster due to Paris (arsenal capital). Historically accurate — France had the best artillery production infrastructure.

### Regen Helper

```python
def get_artillery_regen_rate(self, nation: str) -> int:
    """Calculate current artillery regen rate for a nation."""
    controlled = [r for r in self.regions.values() if r.controller == nation]
    rate = ARTILLERY_BASE_REGEN
    for region in controlled:
        if region.terrain == "urban":
            rate += URBAN_ARTILLERY_REGEN
    return rate
```
