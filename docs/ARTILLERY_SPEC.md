# Artillery Unit Type — Implementation Spec

> **Phase 6 Feature (final item). Ready for implementation.**
> **Complexity:** Medium (1 session, Opus)
> **Prerequisites:** Manpower Pools (DONE), Terrain (DONE), Combat modifiers (DONE)
> **Reviewed:** February 2026. All numbers evaluated, edge cases resolved, AI behavior specified.

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

**Movement captures work normally.** Artillery moving into an undefended enemy region captures it via standard movement rules (same as infantry/cavalry). The "no advance on win" rule only blocks the post-combat advance — where a winner teleports into the loser's region after winning from adjacent. Artillery that physically walks into a region controls it.

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

**Counter-punch timing:** If artillery is attacked on the enemy's turn and earns counter-punch, `moved_this_turn` resets at the start of the player's next turn. The artillery can then use the free counter-punch attack on its own turn without restriction. This is correct and intended — the guns weren't moved, they were attacked in place, and the crew fires back.

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

**Is this crackable?** YES, but it takes work:
- Artillery bombardment degrades the marshal's fortify bonus (-10% per attack, twice the normal rate). After 2 bombardments: fortify bonus eliminated.
- **BUT:** The fort building (+25%) and terrain (+15%) NEVER degrade. After cracking the fortify bonus, defender retains ~1.86x effective defense (terrain + building + stance + personality).
- Cavalry counter (+30%) against 1.86x residual = ~1.43x net defender advantage. Winnable but still a hard fight.
- The real counter to a max-stack artillery turtle is **combined-arms in sequence**: bombard to strip fortify bonus, THEN cavalry charge into the weakened position. Or bypass entirely — artillery can't pursue.
- This is the intended combined-arms puzzle. Head-on cavalry charges into fully fortified artillery will fail. Planning wins.

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

## Bombardment Loop & Personality Objections

Artillery's core gameplay loop is **repeated bombardment of the same target over multiple turns**. This interacts with the personality/objection system in ways that need explicit design.

### Berthier Bombardment Advisory

When artillery bombardment degrades a defender's `defense_bonus` to 0% AND the target region's `fortification_bonus` (fort building) has been degraded below 15% (i.e., building damaged or absent), Berthier should observe:

> "Sire, the enemy fortifications at {region} are crumbling. An infantry assault would now have favorable odds."

This is a **message only** (no mechanic change). It teaches players when to transition from bombardment to infantry assault. Implementation: check conditions in `_execute_attack` post-combat for artillery attackers, append to result message.

```python
# In executor.py, after artillery bombardment resolves:
if getattr(marshal, 'artillery', False) and battle_result.get("attacker_won"):
    defender_fort = getattr(target_marshal, 'defense_bonus', 0)
    region_fort = region.fortification_bonus if hasattr(region, 'fortification_bonus') else 0
    if defender_fort <= 0 and region_fort < 0.15:
        result["bombardment_advisory"] = (
            f"Sire, the enemy fortifications at {target_region} are crumbling. "
            f"An infantry assault would now have favorable odds."
        )
```

### Personality Objection Triggers for Bombardment

These are new V2a-style trigger entries for `objection_v2.py`, not new mechanics. They document how existing personality archetypes interact with the bombardment loop.

#### Aggressive Artillery — Impatient Bombardier

An aggressive artillery marshal objects to **sustained bombardment of the same target** when the target is weakened:

| Trigger | Condition | ConcernLevel | Message Template |
|---------|-----------|-------------|-----------------|
| `repeated_bombardment_same_target` | 3+ turns bombarding same target AND target `defense_bonus` <= 0.05 | MILD | "{marshal} grows restless. 'We've been shelling them for days — the position is softened, Sire. Let the infantry finish it!'" |
| `repeated_bombardment_strong_target` | 3+ turns bombarding same target AND target `defense_bonus` > 0.05 | None | No objection — the target is still fortified, bombardment is justified |

**Implementation:** Track `last_bombardment_target` and `bombardment_streak` on the marshal (or derive from event log). Fire trigger in V2a evaluation when streak >= 3 and target is sufficiently degraded.

```python
# New marshal fields:
self.last_bombardment_target: Optional[str] = None  # Region last bombarded
self.bombardment_streak: int = 0  # Consecutive turns bombarding same region
```

#### Cautious Artillery — Patient Gunner

A cautious artillery marshal objects to being **ordered to stop bombardment before the position is fully degraded**:

| Trigger | Condition | ConcernLevel | Message Template |
|---------|-----------|-------------|-----------------|
| `move_while_bombarding` | Ordered to move while `bombardment_streak` >= 1 AND adjacent target still has `defense_bonus` > 0 | MILD | "{marshal} hesitates. 'The defenses are still partially intact, Sire — one more barrage and they'll crumble.'" |
| `move_while_target_cracked` | Ordered to move while adjacent target has `defense_bonus` <= 0 | None | No objection — bombardment accomplished its goal |

#### Literal Artillery — No Opinion

Literal artillery marshals do not object to bombardment patterns. They fire when ordered, stop when ordered. "The Sage of the Grand Army" follows the plan.

#### Implementation Note

These triggers require tracking which target the artillery last bombarded and for how many consecutive turns. Add to marshal fields:

```python
# In marshal.py __init__:
self.last_bombardment_target: Optional[str] = None
self.bombardment_streak: int = 0

# In executor.py _execute_attack for artillery:
if getattr(marshal, 'artillery', False):
    target_region = target_marshal.location  # or the attacked region
    if target_region == getattr(marshal, 'last_bombardment_target', None):
        marshal.bombardment_streak += 1
    else:
        marshal.last_bombardment_target = target_region
        marshal.bombardment_streak = 1

# Reset on move:
# In executor.py _execute_move:
if getattr(marshal, 'artillery', False):
    marshal.last_bombardment_target = None
    marshal.bombardment_streak = 0
```

These fields must be added to `to_dict()`/`from_dict()` with `.get()` defaults for backward compatibility.

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

See **dedicated AI Artillery Behavior section** below for full decision tree with pseudo-code.

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
- **Strategic execution path verification:** Strategic MOVE_TO orders execute through `_execute_move()` in executor.py. Setting `moved_this_turn = True` inside `_execute_move()` automatically covers both direct player commands and strategic execution. Must test: strategic MOVE_TO for artillery sets `moved_this_turn` correctly.

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

**Artillery mirror matches:** Two cautious artillery marshals on adjacent hills create mutual bombardment that degrades both sides' fortify bonuses. Neither can advance. This naturally resolves as a stalemate on that front, freeing other marshals to operate elsewhere. Historically accurate — secondary fronts often stalemated while decisive action happened elsewhere. Not broken, but can be boring if it's a chokepoint. The answer is combined arms: bring infantry or cavalry to break the deadlock.

**Cavalry counter by artillery configuration:**

| Artillery Setup | Effective Defense | With Cavalry +30% | Verdict |
|----------------|-------------------|-------------------|---------|
| Exposed (no fort/fortify) | ~1.15x (stance only) | Cavalry advantage | Easy win |
| Fortified only | ~1.54x | Roughly even | Fair fight |
| Full stack (hills+fort+fortify) | ~2.37x | Still defender advantage (~1.82x) | Bombardment first |
| Full stack AFTER bombardment | ~1.86x | Mild defender advantage (~1.43x) | Winnable |

---

## AI Artillery Behavior

AI artillery behavior must be designed alongside the unit type. If the AI can't use artillery effectively, the player never faces competent artillery opposition and never learns why combined arms matters.

### Two-Turn Cycle Awareness

AI artillery operates on a **move → set up → attack** cycle. The AI must respect `moved_this_turn` and prefer attacking over repositioning when it has valid targets.

**Anti-oscillation rule:** If artillery has valid attack targets from its current position AND `moved_this_turn` is False, the AI must NOT move. Only reposition if there are zero valid targets in range.

```python
# In _evaluate_marshal, BEFORE P7 strategic movement:
if getattr(marshal, 'artillery', False) and not getattr(marshal, 'moved_this_turn', False):
    # Check if any valid bombardment targets exist
    adj_enemies = self._get_adjacent_enemies(marshal, nation, world)
    if adj_enemies:
        # DO NOT consider P7 movement — prefer staying and attacking
        # Fall through to P4 attack evaluation
        pass
```

### Target Selection for Bombardment

When AI artillery evaluates attack targets in `_find_attack_opportunity`, use a bombardment-specific sort order:

**Priority tiers (within threshold-passing targets):**
1. Fortified targets with fort buildings (`defense_bonus > 0` AND region has fortification building) — artillery's 10% degradation is most impactful here
2. Fortified targets without fort buildings (`defense_bonus > 0` only) — still valuable degradation
3. Unfortified targets — artillery CAN attack them, but provides less strategic value than infantry would

Within each tier, sort by nearest (prefer adjacent over range-2).

```python
def _artillery_target_sort_key(self, target: Marshal, world: WorldState) -> tuple:
    """Sort key for AI artillery target selection. Lower = higher priority."""
    target_region = world.get_region(target.location)
    has_fort_building = target_region.has_building("fortification") if target_region else False
    has_fortify_bonus = getattr(target, 'defense_bonus', 0) > 0

    # Priority tier: 0 = fort+fortify (best), 1 = fortify only, 2 = unfortified
    if has_fort_building and has_fortify_bonus:
        tier = 0
    elif has_fortify_bonus:
        tier = 1
    else:
        tier = 2

    return (tier, )  # Caller can append distance as tiebreaker
```

### Positioning Logic

When AI artillery DOES need to move (P7), use a scoring function for candidate positions:

```python
def _score_artillery_position(self, region_name: str, marshal: Marshal,
                                nation: str, world: WorldState) -> int:
    """Score a candidate position for AI artillery. Higher = better."""
    region = world.get_region(region_name)
    if not region:
        return -1000

    score = 0

    # Prefer hills terrain (+30 — best defensive terrain for guns)
    terrain = getattr(region, 'terrain', 'plains')
    if terrain == 'hills':
        score += 30
    elif terrain == 'mountains':
        score += 15  # Good defense but hard to move out of
    elif terrain == 'urban':
        score += 20  # Fort building potential

    # Prefer positions adjacent to fortified enemy positions (+25)
    for adj_name in region.adjacent_regions:
        adj_region = world.get_region(adj_name)
        if adj_region and adj_region.controller and adj_region.controller != nation:
            # Enemy territory adjacent — potential bombardment target
            score += 15
            # Bonus if enemy is fortified there
            for m in world.marshals.values():
                if m.location == adj_name and m.nation != nation:
                    if getattr(m, 'defense_bonus', 0) > 0:
                        score += 25  # High-value bombardment target

    # Prefer positions WITH friendly infantry screen (+20)
    for m in world.marshals.values():
        if m.name != marshal.name and m.nation == nation:
            if m.location == region_name and not getattr(m, 'cavalry', False):
                score += 20  # Friendly infantry in same region = screen
            elif m.location in region.adjacent_regions and not getattr(m, 'cavalry', False):
                score += 10  # Friendly infantry adjacent = nearby screen

    # AVOID positions adjacent to player cavalry without friendly screen (-30)
    has_friendly_infantry_screen = any(
        m.nation == nation and not getattr(m, 'cavalry', False)
        and (m.location == region_name or m.location in region.adjacent_regions)
        for m in world.marshals.values() if m.name != marshal.name
    )
    if not has_friendly_infantry_screen:
        for adj_name in region.adjacent_regions:
            for m in world.marshals.values():
                if m.nation != nation and getattr(m, 'cavalry', False):
                    if m.location == adj_name:
                        score -= 30  # Enemy cavalry nearby, no screen = danger

    # Own territory preferred (+10)
    if region.controller == nation:
        score += 10

    return score
```

### Screening Awareness (Defensive)

If AI artillery is exposed (no friendly infantry in same or adjacent region) and enemy cavalry is within 2 regions, the AI should prioritize retreating toward friendly infantry over continued bombardment.

```python
# In _evaluate_marshal, after P0 engagement check, before P4:
if getattr(marshal, 'artillery', False):
    has_screen = self._artillery_has_screen(marshal, nation, world)
    enemy_cav_nearby = self._enemy_cavalry_within_range(marshal, nation, world, range=2)

    if not has_screen and enemy_cav_nearby:
        # Find nearest friendly infantry and move toward them
        retreat_dest = self._find_nearest_friendly_infantry(marshal, nation, world)
        if retreat_dest and retreat_dest != marshal.location:
            ai_debug(f"  ARTILLERY SCREEN: {marshal.name} exposed to cavalry, retreating to screen")
            return ({
                "action": "move",
                "marshal_name": marshal.name,
                "target": retreat_dest,
            }, 2)  # Priority 2 — survival

def _artillery_has_screen(self, marshal, nation, world) -> bool:
    """Check if artillery has friendly infantry in same or adjacent region."""
    region = world.get_region(marshal.location)
    if not region:
        return False
    for m in world.marshals.values():
        if m.name != marshal.name and m.nation == nation and m.strength > 0:
            if not getattr(m, 'cavalry', False) and not getattr(m, 'artillery', False):
                if m.location == marshal.location or m.location in region.adjacent_regions:
                    return True
    return False

def _enemy_cavalry_within_range(self, marshal, nation, world, range=2) -> bool:
    """Check if enemy cavalry is within N regions."""
    region = world.get_region(marshal.location)
    if not region:
        return False
    # Check adjacent (range 1)
    checked = {marshal.location}
    frontier = set(region.adjacent_regions)
    for depth in range(1, range + 1):
        for rname in frontier:
            for m in world.marshals.values():
                if m.nation != nation and getattr(m, 'cavalry', False) and m.location == rname:
                    return True
            checked.add(rname)
        if depth < range:
            next_frontier = set()
            for rname in frontier:
                r = world.get_region(rname)
                if r:
                    next_frontier.update(n for n in r.adjacent_regions if n not in checked)
            frontier = next_frontier
    return False
```

### Integration with Priority Chain

Where artillery evaluation fits in the existing P0-P8 system:

| Priority | Artillery Behavior | Change from Base |
|----------|-------------------|-----------------|
| P0 (Engagement) | Unchanged — if enemies in region, fight or flee | No change |
| P1 (Retreat recovery) | Unchanged | No change |
| P2 (Critical survival) | **NEW:** If exposed to cavalry without screen, retreat to nearest friendly infantry | Add artillery screen check |
| P3 (Threat response) | Unchanged | No change |
| P3.25 (Counter-punch) | Works for artillery — cautious artillery can counter-bombard | No change |
| P4 (Attack) | **MODIFIED:** If artillery AND `moved_this_turn`: skip attack. If artillery AND NOT moved: use bombardment target selection (fortified-first sort). Apply normal personality threshold. | Add `moved_this_turn` check + artillery sort |
| P4.25 (Garrison assault) | Artillery CAN attack garrisons (garrison is in adjacent region) | No change |
| P4.5 (Undefended capture) | Artillery CAN capture by moving into undefended regions | No change |
| P5 (Fortify) | Artillery CAN fortify — natural fit, no cavalry limits apply | No change |
| P6 (Drill) | Artillery CAN drill — target practice | No change |
| P6.75 (Garrison) | Artillery CAN garrison — leaving guns to defend | No change |
| P7 (Strategic movement) | **MODIFIED:** Use `_score_artillery_position()` for destination selection instead of standard aggressive/cautious logic. Anti-oscillation: skip P7 if valid targets adjacent. | Add artillery positioning logic |
| P8 (Default) | Standard stance/wait fallback | No change |

### AI Cavalry Targeting Exposed Artillery

In `_find_attack_opportunity`, add a target preference for AI cavalry attacking unscreened artillery:

```python
# In _find_attack_opportunity, when evaluating targets:
if getattr(marshal, 'cavalry', False):
    # Prefer exposed artillery targets (+30% counter bonus makes them juicy)
    for target in valid_targets:
        if getattr(target, 'artillery', False):
            target_has_screen = self._target_has_infantry_screen(target, world)
            if not target_has_screen:
                ai_debug(f"    P4: Cavalry {marshal.name} targeting exposed artillery {target.name}")
                return {
                    "action": "attack",
                    "marshal_name": marshal.name,
                    "target": target.name,
                }
```

### AI Admin: No Stables for Artillery

Existing `_should_build_stables()` checks `marshal.cavalry` — artillery marshals return False. No change needed. AI should NOT build stables for artillery marshals.

AI admin should check artillery pool for artillery marshal recruitment:

```python
# In _pick_admin_action, recruit section:
if getattr(weakest_marshal, 'artillery', False):
    pool_key = 'artillery'
    batch = ARTILLERY_RECRUIT_AMOUNT  # 3000
    base_cost = ARTILLERY_RECRUIT_GOLD_COST_BASE  # 400
else:
    # ... existing infantry/cavalry logic
```

### Known Limitation: No Combined Arms Coordination

True combined arms coordination — "bombard with artillery THEN infantry follows up in coordinated assault on the same turn" — requires Phase 7 multi-marshal coordination systems. For Phase 6:

- AI artillery softens targets independently (degrades forts, causes casualties)
- AI infantry benefits when they attack the same region later (lower fortify bonus, fewer troops)
- This happens by coincidence, not coordination — when multiple AI marshals evaluate the same front, they'll naturally converge on the same targets
- The AI will NOT deliberately sequence "Drouot bombard turn N → infantry capture turn N+1"

**TODO for Phase 7:** Add multi-marshal coordination: after artillery bombardment reduces a target's `defense_bonus` to 0, flag the target region as "softened" for one turn. AI infantry evaluating that region gets a priority boost.

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
        "effect": "+2 fort degradation per bombardment (DEFERRED — Phase 6.5 ability wiring pass)"
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

**Ability wiring: DEFERRED to Phase 6.5.** Drouot's "Sage of the Grand Army" ability is defined in marshal data but NOT wired in combat.py during this implementation. This is consistent with all other marshals — Wellington's Reverse Slope Defense, Blucher's Vorwärts!, Uxbridge's Pursuit Master, and Gneisenau's Staff Work are all unwired. All abilities will be wired together in a single Phase 6.5 pass.

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
| `marshal.py` | `artillery: bool` field, `moved_this_turn: bool` field, `last_bombardment_target`/`bombardment_streak` fields, mutual exclusivity assert, -25% defense in `get_defense_modifier()` when moved, `to_dict/from_dict`, `__repr__` unit type, Drouot + PrinceAugust in starting marshals | 2/5 |
| `combat.py` | Cavalry-vs-artillery counter (+30%), artillery fort degradation (10% vs 5%), cavalry counter message, battle report context | 2/5 |
| `executor.py` | Can't-attack-after-moving check (early return), no-advance-on-win (skip `move_to` for artillery), block PURSUE auto-promotion for artillery, ban glorious charge for artillery, set `moved_this_turn=True` in `_execute_move`, bombardment streak tracking, Berthier bombardment advisory, artillery-specific battle messaging | 3/5 |
| `world_state.py` | Reset `moved_this_turn` at turn start in `_process_tactical_states`, artillery manpower pool constants + starting pools + regen + `get_artillery_regen_rate()` helper + cap, serialization | 2/5 |
| `enemy_ai.py` | P2 artillery screen check, P4 `moved_this_turn` gate + bombardment target sort, P7 `_score_artillery_position()` for positioning, anti-oscillation rule, cavalry targets exposed artillery, `_artillery_has_screen()`/`_enemy_cavalry_within_range()` helpers, pool-aware recruit for artillery type, skip stables for artillery | 4/5 |
| `llm_client.py` | "bombard"/"barrage"/"shell"/"cannonade" keywords → attack action | 1/5 |
| `prompt_builder.py` | Few-shot examples for artillery commands | 1/5 |
| `battle_report.py` | Artillery-specific observations (bombardment, fort degradation note, cavalry counter) | 1/5 |

**No changes to:** `region.py` (no artillery terrain table — defender terrain bonus is sufficient), `validation.py` (reuse "attack" action), `main.py` (verify passthrough only), `objection_v2.py` (bombardment triggers are V2a entries — wire during implementation alongside other trigger additions)

**Estimated tests: ~115**

---

## Implementation Difficulty Ratings

| Subsystem | Difficulty | Test Count | Notes |
|-----------|-----------|------------|-------|
| `marshal.artillery` bool + mutual exclusivity + serialization | 1/5 | ~8 | Follow cavalry pattern exactly |
| `moved_this_turn` field + reset at turn start | 1/5 | ~5 | Simple bool lifecycle |
| `last_bombardment_target` + `bombardment_streak` | 1/5 | ~5 | Track/reset in executor, serialize |
| Can't-attack-after-moving check | 1/5 | ~8 | Early return in `_execute_attack` |
| Win-without-advancing | 2/5 | ~8 | Skip `move_to` + capture for artillery in post-combat |
| Block PURSUE auto-promotion for artillery | 1/5 | ~5 | One check in range block |
| Fort degradation 10% vs 5% | 1/5 | ~5 | Conditional on attacker type |
| Cavalry counter +30% | 1/5 | ~5 | Same pattern as terrain cavalry effectiveness |
| Moved-this-turn -25% defense | 1/5 | ~5 | Add to `get_defense_modifier()` |
| Ban glorious charge for artillery | 1/5 | ~3 | Early return |
| AI artillery behavior | 4/5 | ~25 | Bombardment sort, positioning score, screen check, anti-oscillation, cavalry targeting |
| Bombardment advisory + personality triggers | 2/5 | ~8 | Berthier message + V2a trigger entries |
| Parser aliases (bombard/shell) | 1/5 | ~3 | Keyword additions |
| Manpower pool (artillery) | 2/5 | ~12 | Follow cavalry pool pattern exactly |
| Starting marshals (Drouot + PrinceAugust) | 1/5 | ~5 | Data entry |
| Battle report artillery observations | 1/5 | ~5 | Template additions |

**TOTAL: 1 session (Opus). ~115 tests.**

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
- [ ] AI artillery SKIPS attack at P4 when `moved_this_turn` is True
- [ ] AI artillery does NOT try to advance into enemy-held regions
- [ ] AI artillery prioritizes fortified targets over unfortified (bombardment sort)
- [ ] AI artillery with valid adjacent targets does NOT move (anti-oscillation)
- [ ] AI artillery exposed to cavalry retreats toward friendly infantry (screen check)
- [ ] AI artillery positions on hills when available (positioning score)
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

### Bombardment Tracking
- [ ] `bombardment_streak` increments when bombarding same target
- [ ] `bombardment_streak` resets when bombarding different target
- [ ] `bombardment_streak` resets when marshal moves
- [ ] `last_bombardment_target` tracks correctly across turns
- [ ] Berthier advisory fires when target fortify bonus = 0 and fort building < 15%
- [ ] Strategic MOVE_TO for artillery sets `moved_this_turn` correctly (strategic execution path)

### Serialization
- [ ] `test_serialization_enforcement.py` passes with new fields (artillery, moved_this_turn, last_bombardment_target, bombardment_streak)
- [ ] Old saves without artillery/moved_this_turn/bombardment fields load correctly (backward compat)
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
