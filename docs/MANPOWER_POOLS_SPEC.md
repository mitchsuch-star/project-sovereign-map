# Manpower Pools — Final Implementation Spec

> **Phase 6 Feature. Ready for implementation.**
> **Complexity:** Medium (1 session)
> **Prerequisites:** None (economy, recruitment, buildings, combat all complete)
> **Reviewed:** February 2026 — all numbers evaluated, edge cases resolved.
> **Post-review fixes (Feb 2026):** AI pool/cost awareness, Berthier voice, dynamic messages, unified cost method, robust backward compat. See §Review Fixes Applied.

---

## Design Intent

Cavalry was the decisive arm of Napoleonic warfare — and the hardest to replace. France's cavalry never recovered after 1812 because *horses died faster than they could be bred*. This system makes cavalry feel precious: easy to lose, slow to rebuild, and strategically valuable enough that players think twice before committing charges.

The core tension: infantry marshals are cheap to reinforce; cavalry marshals are expensive, scarce, and slow to rebuild. Losing a cavalry marshal is a campaign-altering setback. Controlling horse-producing territory gives a lasting advantage.

**Cavalry is a unit type, not a composition.** Ney IS cavalry — always moves 2, always charges at full power. The scarcity comes from the pool, not from degrading what cavalry means.

**No artillery pool yet.** Artillery unit type doesn't exist. When it's built, its pool gets added with the same pattern.

**Emergent morale bonus:** Cavalry recruits (5k) dilute veteran morale less than infantry recruits (10k). This is intentional — the smaller batch means cavalry marshals recover battle-readiness faster after reinforcement, partially compensating for the cost premium.

---

## All Numbers (Final)

### Constants (define in `world_state.py`)

```python
# ═══════ MANPOWER POOL CONSTANTS ═══════
INFANTRY_RECRUIT_AMOUNT = 10000        # Troops per infantry recruit (unchanged)
CAVALRY_RECRUIT_AMOUNT = 5000          # Troops per cavalry recruit (half infantry — precious)
INFANTRY_RECRUIT_GOLD_COST_BASE = 200  # Gold cost for infantry recruit (existing behavior)
CAVALRY_RECRUIT_GOLD_COST_BASE = 300   # Gold cost for cavalry recruit (vs 200 infantry)
INFANTRY_BASE_REGEN = 5000             # Per nation per turn (fast — infantry isn't the bottleneck)
CAVALRY_BASE_REGEN = 500               # Per nation per turn (slow — this IS the bottleneck)
PLAINS_CAVALRY_REGEN = 500             # Bonus per plains region controlled
STABLES_CAVALRY_REGEN = 750            # Bonus per stables building owned
MAX_INFANTRY_POOL = 100000             # Pool cap
MAX_CAVALRY_POOL = 30000               # Pool cap

# Default starting pools (also used for backward compat)
DEFAULT_MANPOWER_POOLS = {
    "France": {"infantry": 80000, "cavalry": 15000},
    "Britain": {"infantry": 50000, "cavalry": 8000},
    "Prussia": {"infantry": 60000, "cavalry": 10000},
}
```

### How Marshal Type Determines Recruitment

| Marshal type | Pool drawn from | Batch size | Gold cost | Charge |
|-------------|----------------|-----------|-----------|--------|
| `cavalry: True` (Ney, Uxbridge) | cavalry pool | 5,000 | 300g base | 2x (flat, always) |
| `cavalry: False` (everyone else) | infantry pool | 10,000 | 200g base | N/A |

**Cost per effective soldier:** Cavalry = 0.06g/troop. Infantry = 0.02g/troop. **3x premium.**

No choice needed — the system derives recruit type from `marshal.cavalry`. The player's strategic choice is **which marshal to reinforce**, not what troop type.

### Starting Pools (Reserve — NOT deployed troops)

| Nation | Infantry Pool | Cavalry Pool | Rationale |
|--------|--------------|-------------|-----------|
| France | 80,000 | 15,000 | 3 full cavalry recruits. Largest nation. |
| Britain | 50,000 | 8,000 | Small elite cavalry. ~1.5 recruits. |
| Prussia | 60,000 | 10,000 | Decent tradition, 2 recruits. |

### Regen Scenarios (Waterloo map: 4 plains regions)

| Nation | Plains | Base Regen | Total (no stables) | +1 Stables | +2 Stables |
|--------|--------|-----------|-------------------|-----------|-----------|
| France | 3 (Belgium, Marseille, Bordeaux) | 500 | 2,000/turn | 2,750/turn | 3,500/turn |
| Britain | 1 (Netherlands) | 500 | 1,000/turn | 1,750/turn | 2,500/turn |
| Prussia | 0 | 500 | 500/turn | 1,250/turn | 2,000/turn |

> **Note:** Stables columns require controlling a capital/major_city/city region with a free building slot. On the Waterloo map, Britain starts with only Netherlands (rural, 0 building slots) — stables require conquering a city first.

### Stables Building

| Property | Value |
|----------|-------|
| Gold cost | 300g |
| Build time | 2 turns |
| Allowed in | capital, major_city, city |
| Uses building slot | Yes (competes with Market, Depot, Fort, Training Ground) |
| Cavalry regen bonus | +750/turn to nation's cavalry pool |
| Damaged stables | Do NOT contribute to regen (`has_building` defaults to `functional_only=True`) |
| Under construction | Do NOT contribute to regen (not yet in `buildings` list) |

---

## Balance Verification (Math)

### Scenario 1: France reinforces Ney 3 times after charges

Ney starts: 72,000 troops. Each glorious charge: ~15% base casualties × 2 (charge) = ~30% losses.

| After battle | Ney strength | Recruit | Pool before → after |
|-------------|-------------|---------|-------------------|
| Battle 1 | ~50,400 | +5k cavalry | 15,000 → 10,000 |
| Battle 2 | ~38,780 | +5k cavalry | 10,000 → 5,000 |
| Battle 3 | ~30,646 | +5k cavalry | 5,000 → 0 |

**Pool drained after 3 recruits.** Ney is at ~35k and CANNOT be reinforced until pool regens.

Recovery with 0 stables: 2,000/turn → 2.5 turns per recruit.
Recovery with 2 stables: 3,500/turn → 1.4 turns per recruit.

**Verdict:** 3 charges drains the pool. Ney is still dangerous (moves 2, charges at 2x) but can't be topped up. Stables investment halves recovery time.

### Scenario 2: Britain loses Uxbridge entirely

Uxbridge broken (3-10% survival at ~1,800 troops). Britain needs to rebuild.
Pool: 8,000. First recruit: 5,000, pool → 3,000. Second: blocked (need 5,000).
Britain regen: 1,000/turn (base + 1 plains). Wait 2 turns for next recruit.
With 1 stables: 1,750/turn → ~1.1 turns.

**Verdict:** Losing Uxbridge is a major setback. Historically accurate — British cavalry was small and irreplaceable.

### Scenario 3: Prussia (zero plains, no stables)

Regen: 500/turn base only. Pool: 10,000. But Prussia has NO cavalry marshals (Blucher and Gneisenau are both `cavalry: False`). Cavalry pool sits unused.

**Verdict:** Correct — Prussia's strength is infantry mass, not cavalry. Pool exists for future scenario expansion (1805 with Prussian cavalry marshals).

### Scenario 4: France, 2 stables + 3 plains

Regen: 3,500/turn. Can sustain one cavalry recruit every 1.4 turns.
Moderate cavalry usage (occasional charge, recruit after) is sustainable.
Heavy charging still drains faster than regen.

**Verdict:** Investment pays off but doesn't make cavalry unlimited.

### Scenario 5: Player must choose — reinforce Ney or Davout?

France has 500g. Ney (cavalry, 45k) and Davout (infantry, 30k) both need troops.

- Reinforce Ney: 300g for 5k. Ney → 50k. Davout stays at 30k. 200g left.
- Reinforce Davout: 200g for 10k. Davout → 40k. 300g left (can reinforce Ney too if pool allows).
- Both: 500g total, Davout gets 10k + Ney gets 5k. Tight on gold.

**Verdict:** Real strategic decision. Davout gives more troops per gold. Ney gives mobility + charge power. No obvious right answer.

---

## Data Model

### Nation-Level Pools (WorldState)

```python
# In WorldState.__init__
self.manpower_pools: Dict[str, Dict[str, int]] = {
    "France": {"infantry": 80000, "cavalry": 15000},
    "Britain": {"infantry": 50000, "cavalry": 8000},
    "Prussia": {"infantry": 60000, "cavalry": 10000},
}
```

### No New Fields on Marshal

The existing `cavalry: bool` field determines recruit type. No `cavalry_ratio` needed. No changes to Marshal class, constructor, or serialization.

---

## Recruitment Changes

### Modified `_execute_recruit` (executor.py)

```python
# Determine recruit type from marshal
recruit_type = "cavalry" if getattr(marshal, 'cavalry', False) else "infantry"

# Set batch size and cost based on type
if recruit_type == "cavalry":
    NEW_TROOPS = CAVALRY_RECRUIT_AMOUNT       # 5,000
    gold_cost = self._calculate_recruit_cost(region, world, base_cost=CAVALRY_RECRUIT_GOLD_COST_BASE)
else:
    NEW_TROOPS = INFANTRY_RECRUIT_AMOUNT      # 10,000
    gold_cost = self._calculate_recruit_cost(region, world, base_cost=INFANTRY_RECRUIT_GOLD_COST_BASE)

# Check pool
pool = world.manpower_pools.get(acting_nation, {})
available = pool.get(recruit_type, 0)
if available < NEW_TROOPS:
    regen_rate = world.get_cavalry_regen_rate(acting_nation) if recruit_type == "cavalry" else INFANTRY_BASE_REGEN
    turns_until = max(1, (NEW_TROOPS - available + regen_rate - 1) // regen_rate)
    return {
        "success": False,
        "message": f"Berthier consults his ledgers. 'Sire, our {recruit_type} reserves are insufficient. "
                   f"Pool: {available:,}, need: {NEW_TROOPS:,}. "
                   f"Recovering +{regen_rate:,}/turn — available in ~{turns_until} turn{\"s\" if turns_until > 1 else \"\"}.'"
    }

# Draw from pool
world.manpower_pools[acting_nation][recruit_type] -= NEW_TROOPS

# Update base_message to reflect actual recruit type and amount
# (replaces all three existing hardcoded "10,000 troops" message templates)
type_label = recruit_type
if marshal_specified:
    base_message = f"{marshal.name} recruits {NEW_TROOPS:,} {type_label} at {marshal.location}"
elif location_specified:
    base_message = f"{marshal.name} recruits {NEW_TROOPS:,} {type_label} for {location_specified} ({distance} regions away)"
else:
    base_message = f"{marshal.name} recruits {NEW_TROOPS:,} {type_label} (nearest to capital)"

# Existing morale dilution unchanged
# Existing gold deduction unchanged (using type-specific cost)
# Existing marshal.add_troops(NEW_TROOPS) unchanged
```

### Unified Gold Cost Method (replaces separate cavalry/infantry methods)

```python
def _calculate_recruit_cost(self, region, world, base_cost: int = 200) -> int:
    """Calculate recruitment gold cost based on region properties.

    Priority: Capital discount wins over settling premium.
    Parameterized base_cost: 200 for infantry, 300 for cavalry.
    """
    # Capital discount: 25% off (checked first — always wins)
    if region.region_type == "capital":
        return int(base_cost * 0.75)  # 150 infantry / 225 cavalry

    # Settling stability premium: 50% more (stability 51-75)
    if 51 <= region.stability <= 75:
        return int(base_cost * 1.50)  # 300 infantry / 450 cavalry

    return base_cost  # 200 infantry / 300 cavalry
```

**Note:** This replaces the existing `_calculate_recruit_cost` (add `base_cost` parameter with default 200 for backward compat) and removes the need for a separate `_calculate_cavalry_recruit_cost`.

### Soft Correction: Player says "recruit cavalry for Davout"

If the player explicitly says "recruit cavalry" for an infantry marshal, Berthier provides a gentle correction:

```
Berthier notes: 'Marshal Davout commands infantry, Sire.' 10,000 infantry recruited at Lyon.
```

The system ignores the type keyword and recruits based on marshal type. No error, no confusion — just an in-character clarification.

### Berthier Voice for ALL Recruit Errors

All recruitment failure messages should use Berthier's voice, matching the garrison pattern:

| Error | Message |
|-------|---------|
| Pool empty | `"Berthier consults his ledgers. 'Sire, our cavalry reserves are insufficient. Pool: 0, need: 5,000. Recovering +2,000/turn — available in ~3 turns.'"` |
| Insufficient gold | `"Berthier shakes his head. 'The treasury cannot support this, Sire. Need 300 gold, have 250.'"` |
| Wrong controller | `"Berthier frowns. 'We do not control {region}, Your Majesty. Recruitment is impossible there.'"` |
| Unstable region | `"Berthier advises caution. '{region} is in {label} (stability {n}/100). The populace will not answer our call until stability exceeds 50.'"` |
| No marshal available | `"Berthier scans the dispatches. 'No marshal is available to receive reinforcements at {region}, Sire.'"` |

---

## Regen Processing

### New method in `world_state.py`

```python
def _process_manpower_regen(self):
    """Regenerate manpower pools per nation. Called during advance_turn.

    Nations with 0 regions still get base regen (represents national reserves,
    overseas recruitment, etc.). Territory bonuses require actual control.
    """
    all_nations = [self.player_nation] + list(self.enemy_nations)
    for nation in all_nations:
        if nation not in self.manpower_pools:
            continue

        controlled = [r for r in self.regions.values() if r.controller == nation]

        # Infantry: generous base regen (no territory dependency)
        inf_regen = INFANTRY_BASE_REGEN

        # Cavalry: slow base + territory bonuses
        cav_regen = CAVALRY_BASE_REGEN
        for region in controlled:
            if region.terrain == "plains":
                cav_regen += PLAINS_CAVALRY_REGEN
            if region.has_building("stables"):
                cav_regen += STABLES_CAVALRY_REGEN

        pool = self.manpower_pools[nation]
        pool["infantry"] = min(pool["infantry"] + inf_regen, MAX_INFANTRY_POOL)
        pool["cavalry"] = min(pool["cavalry"] + cav_regen, MAX_CAVALRY_POOL)
```

### Helper for cavalry regen rate (used in error messages + AI decisions)

```python
def get_cavalry_regen_rate(self, nation: str) -> int:
    """Calculate current cavalry regen rate for a nation (for display/error messages)."""
    controlled = [r for r in self.regions.values() if r.controller == nation]
    rate = CAVALRY_BASE_REGEN
    for region in controlled:
        if region.terrain == "plains":
            rate += PLAINS_CAVALRY_REGEN
        if region.has_building("stables"):
            rate += STABLES_CAVALRY_REGEN
    return rate
```

### Placement in `advance_turn`

Add `self._process_manpower_regen()` in `_advance_turn_internal()`, AFTER income phase, BEFORE cavalry limits check:

```python
# INCOME PHASE
for nation in all_nations:
    self.process_income_phase(nation)

# MANPOWER REGEN (after income, before action resets)
self._process_manpower_regen()

# Reset actions...
```

---

## Stables Building

### Add to `BUILDING_TYPES` in `region.py`

```python
"stables": {"gold_cost": 300, "build_time": 2, "allowed_in": ["capital", "major_city", "city"]},
```

### Mock Parser: building type extraction (executor.py `_extract_building_type`)

Add before the fallback:
```python
elif "stable" in raw or "horse" in raw:
    return "stables"
```

Note: don't match "cavalry" here — it would collide with "recruit cavalry" parsing.

### AI Stables Building Priority

Add to `_pick_admin_action` in `enemy_ai.py` as Priority 4.5 (after market/depot, before generic fortification):

```python
# Priority 4.5: Build stables if cavalry pool low and nation has cavalry marshals
if "build" not in skip_actions and treasury >= 300:
    if self._should_build_stables(nation, world):
        stables_region = self._find_best_stables_region(nation, world)
        if stables_region:
            return {"action": "build", "target": stables_region, "building_type": "stables"}
```

```python
def _should_build_stables(self, nation: str, world) -> bool:
    """Check if nation should invest in stables."""
    has_cavalry_marshal = any(
        getattr(m, 'cavalry', False)
        for m in world.marshals.values()
        if m.nation == nation
    )
    if not has_cavalry_marshal:
        return False
    pool = world.manpower_pools.get(nation, {})
    return pool.get("cavalry", 0) < MAX_CAVALRY_POOL * 0.6

def _find_best_stables_region(self, nation: str, world) -> Optional[str]:
    """Find region to build stables. Prefer plains (thematic), then highest-income."""
    candidates = []
    for name, region in world.regions.items():
        if region.controller != nation:
            continue
        if region.region_type not in ("capital", "major_city", "city"):
            continue
        if region.has_building("stables", functional_only=False):
            continue
        if getattr(region, 'building_under_construction', None):
            continue
        if region.available_building_slots() <= 0:
            continue
        score = region.income_value
        if region.terrain == "plains":
            score += 500  # Strong preference for thematic placement
        candidates.append((score, name))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]
```

### AI Recruit: Pool + Cost Awareness

**Critical fix:** AI must check pool availability AND use correct gold costs before attempting recruit. Without this, a failed cavalry recruit adds `"recruit"` to `skip_actions`, blocking ALL recruitment (including affordable infantry) for the rest of the turn.

Modify `_pick_admin_action` recruit cost estimation (both Priority 1 and Priority 7):

```python
# In _pick_admin_action, when evaluating recruit:
if weakest:
    is_cavalry = getattr(weakest, 'cavalry', False)

    # Check pool availability BEFORE attempting
    recruit_type = "cavalry" if is_cavalry else "infantry"
    needed = CAVALRY_RECRUIT_AMOUNT if is_cavalry else INFANTRY_RECRUIT_AMOUNT
    pool = world.manpower_pools.get(nation, {})
    if pool.get(recruit_type, 0) < needed:
        weakest = None  # Pool empty — skip this marshal, try others

if weakest:
    is_cavalry = getattr(weakest, 'cavalry', False)
    base_cost = CAVALRY_RECRUIT_GOLD_COST_BASE if is_cavalry else INFANTRY_RECRUIT_GOLD_COST_BASE

    region = world.get_region(weakest.location)
    recruit_cost = base_cost
    if region and getattr(region, 'is_capital', False):
        recruit_cost = int(base_cost * 0.75)
    elif region and 51 <= getattr(region, 'stability', 100) <= 75:
        recruit_cost = int(base_cost * 1.50)

    if treasury >= recruit_cost and region and getattr(region, 'stability', 100) > 50:
        return {
            "action": "recruit",
            "marshal": weakest.name,
            "target": weakest.location
        }
```

**Also modify `_find_weakest_marshal_for_admin`** to skip marshals whose pool is empty:

```python
def _find_weakest_marshal_for_admin(self, nation: str, world, threshold: float = None) -> Optional['Marshal']:
    """Find the weakest marshal below recruitment threshold.

    Skips marshals whose manpower pool can't support a recruit.
    """
    if threshold is None:
        threshold = self.AI_RECRUITMENT_THRESHOLD
    weakest = None
    lowest_ratio = threshold

    for marshal in world.marshals.values():
        if marshal.nation != nation or marshal.strength <= 0:
            continue
        starting = getattr(marshal, 'starting_strength', marshal.strength)
        if starting <= 0:
            continue
        ratio = marshal.strength / starting
        if ratio < threshold and ratio < lowest_ratio:
            # Check pool availability
            recruit_type = "cavalry" if getattr(marshal, 'cavalry', False) else "infantry"
            needed = CAVALRY_RECRUIT_AMOUNT if recruit_type == "cavalry" else INFANTRY_RECRUIT_AMOUNT
            pool = world.manpower_pools.get(nation, {})
            if pool.get(recruit_type, 0) < needed:
                continue  # Pool can't support this marshal's recruit type

            region = world.get_region(marshal.location)
            if region and region.controller == nation:
                lowest_ratio = ratio
                weakest = marshal

    return weakest
```

**Why this matters:** The AI admin loop (`execute_admin_phase`) adds failed action types to `skip_actions`. If cavalry recruit fails → `"recruit"` is skipped entirely → AI can't recruit infantry either. Pool pre-check prevents this cascade.

---

## Serialization

### WorldState

```python
# to_dict()
"manpower_pools": {k: v.copy() for k, v in self.manpower_pools.items()},

# from_dict() — robust backward compat
raw_pools = data.get("manpower_pools", {})
world.manpower_pools = {k: v.copy() for k, v in raw_pools.items()}
# Fill missing nations or missing pool types from defaults
for nation, defaults in DEFAULT_MANPOWER_POOLS.items():
    if nation not in world.manpower_pools:
        world.manpower_pools[nation] = defaults.copy()
    else:
        for pool_type, default_val in defaults.items():
            if pool_type not in world.manpower_pools[nation]:
                world.manpower_pools[nation][pool_type] = default_val
```

### Marshal

No changes. `cavalry: bool` already serializes. No new fields.

**Run `pytest tests/test_serialization_enforcement.py -v` after implementation.**

---

## Parser Changes

### Mock Parser (llm_client.py)

No changes needed to the recruit block. The `recruit_type` is determined by marshal type in the executor, not parsed from the command. The existing `"recruit"` parsing stays as-is.

However, if we want the soft correction message ("Berthier notes: Marshal Davout commands infantry"), the mock parser can optionally extract a `requested_type` for the executor to compare against:

```python
# Optional: extract what the player ASKED for (for soft correction message)
if any(kw in command_lower for kw in ["cavalry", "horse", "rider", "horsemen"]):
    requested_type = "cavalry"
elif "infantry" in command_lower or "foot" in command_lower:
    requested_type = "infantry"
else:
    requested_type = None  # player didn't specify
```

This is purely for flavor messaging, not mechanics.

**Known quirk:** "reinforce" is checked before "recruit" in the mock parser elif chain (`llm_client.py:575`). Commands like "recruit reinforcements" will match "reinforce" (substring of "reinforcements") and route to strategic SUPPORT instead of recruit. This is pre-existing behavior. Players should use "recruit for Ney" or "recruit at Paris", not "reinforce."

### LLM Parser (prompt_builder.py)

Update few-shot examples to reflect that recruit type is auto-determined:
```
"recruit at Paris" -> {"action": "recruit", "target": "Paris"}
"recruit for Ney" -> {"action": "recruit", "marshal": "Ney"}
"recruit at Lyon" -> {"action": "recruit", "target": "Lyon"}
```

No `recruit_type` field needed in parsed output.

### validation.py

No changes — "recruit" is already in VALID_ACTIONS.

---

## Display / Economy Report

### Add manpower section to `_execute_economy` (executor.py)

After the treasury section, before the closing line:

```python
nation = world.player_nation
pool = world.manpower_pools.get(nation, {})
inf_pool = pool.get("infantry", 0)
cav_pool = pool.get("cavalry", 0)
cav_regen = world.get_cavalry_regen_rate(nation)

lines.append(f"\n  ═══════ MANPOWER ═══════")
lines.append(f"  Infantry Pool: {inf_pool:,} (+{INFANTRY_BASE_REGEN:,}/turn)")
lines.append(f"  Cavalry Pool:  {cav_pool:,} (+{cav_regen:,}/turn)")
if cav_pool < CAVALRY_RECRUIT_AMOUNT:
    lines.append(f"  Berthier warns: 'Cavalry reserves dangerously low, Sire.' (need {CAVALRY_RECRUIT_AMOUNT:,} to recruit)")
```

### Recruitment result messages

Infantry:
```
Berthier reports: 10,000 infantry recruited at Paris for Marshal Davout.
Infantry pool: 80,000 → 70,000. Cost: 200g.
Morale: 85% -> 82%
```

Cavalry:
```
Berthier reports: 5,000 cavalry recruited at Paris for Marshal Ney.
Cavalry pool: 15,000 → 10,000. Cost: 300g.
Morale: 90% -> 88%
```

Pool status line after recruit (append to success message):
```
{recruit_type.title()} pool: {available:,} → {available - NEW_TROOPS:,}
```

---

## Godot Changes

Minimal — no new UI needed beyond what economy report shows. Manpower info rides on the existing economy text display. Error messages on failed recruitment explain the situation.

---

## Edge Case Resolutions

| Edge Case | Resolution |
|-----------|-----------|
| Player says "recruit cavalry for Davout" | Soft correction via Berthier: "Marshal Davout commands infantry, Sire." Recruits infantry, no error. |
| Player says bare "recruit at Belgium" | Finds nearest marshal, determines type from `marshal.cavalry`. Works exactly as before. |
| Two marshals (1 cav, 1 inf) in same region | `find_nearest_marshal_to_region` picks one. Player can specify "recruit for Ney" for precision. |
| Cavalry pool empty, player tries to recruit for Ney | Blocked with Berthier message: pool amount, need amount, regen rate, turns estimate. |
| Nation has no cavalry marshals (Prussia) | Cavalry pool exists but is never drawn from. Sits at cap. No harm. |
| Garrison detachments | Garrisons use `take_casualties()` as before. No pool interaction. Garrisons are static defenders, not recruitable. |
| Broken marshal (2k troops) recruited back to 7k | Pool drawn normally. No special cases for broken marshals. |
| Nation with 0 regions | Still gets base regen (500 cavalry, 5000 infantry). Represents national reserves. No territory bonuses. |
| Player says "reinforce Ney's troops" | Pre-existing: "reinforce" matches strategic SUPPORT before "recruit". Use "recruit for Ney" instead. |
| AI cavalry recruit costs more than infantry | AI checks `marshal.cavalry` and uses correct base cost (300 vs 200) before attempting. Prevents skip_actions cascade. |
| AI pool empty for one type but not other | `_find_weakest_marshal_for_admin` skips marshals whose pool can't support them. Infantry recruit still works if cavalry pool is empty. |
| Damaged stables | `has_building("stables")` defaults to `functional_only=True` — damaged stables don't contribute regen. |
| Stables under construction | Not yet in `buildings` list — no regen bonus until construction completes. |
| Partial/corrupted save data | `from_dict` fills missing nations and pool types from `DEFAULT_MANPOWER_POOLS`. |

---

## What This Does NOT Include

- Artillery manpower pool (no artillery unit type yet — same pattern when built)
- Horse trading between nations (future diplomacy feature)
- Cavalry_ratio or troop composition tracking (cavalry is a unit type, not a mix)
- Charge scaling with composition (charges are flat 2x — cavalry IS cavalry)
- Any changes to the cavalry personality system (defensive stance limits, etc.)
- Any changes to combat.py (no split casualties, no charge modifications)
- 1805 scenario parameterization (hardcode for Waterloo; add TODO comments for later)

---

## 1805 Scaling Notes

Current numbers are tuned for the 13-region Waterloo map (4 plains regions). For 1805 with 80-100 regions:

- **Plains regions will be abundant** (Hungarian Plain, North German Plain, Russian Steppe, Po Valley). With 20+ plains, the +500/region bonus would give 10,000+ cavalry regen — too generous.
- **Solution:** Scenario-parameterize regen rates. For now, hardcode current values with `# TODO: Scenario-parameterize for 1805` comments.
- **Stables remain relevant** even with many plains, because building slots are scarce.
- **Pool caps may need scaling** — 30k cavalry cap may be low for nations with 10+ marshals.
- **Infantry pools may actually matter** at 1805 scale with 6-8 nations and massive armies.
- **More nations will have cavalry marshals** — Murat, Poniatowski, Pajol for France; cavalry generals for Austria, Russia.

---

## Review Fixes Applied

Fixes from post-review (February 2026). Each addresses a specific finding from the spec review.

| # | Severity | Fix | Section |
|---|----------|-----|---------|
| 1 | Critical | AI checks `marshal.cavalry` for correct gold cost (300 vs 200) before attempting recruit | §AI Recruit: Pool + Cost Awareness |
| 2 | Critical | AI checks pool availability in `_find_weakest_marshal_for_admin` — skips marshals whose pool is empty | §AI Recruit: Pool + Cost Awareness |
| 3 | Critical | Dynamic `{NEW_TROOPS:,} {type_label}` in all three `base_message` templates (was hardcoded "10,000 troops") | §Modified `_execute_recruit` |
| 4 | Important | Unified `_calculate_recruit_cost(region, world, base_cost=200)` — one method with parameterized base, not two | §Unified Gold Cost Method |
| 5 | Important | All recruit errors use Berthier voice (matches garrison pattern in executor.py) | §Berthier Voice for ALL Recruit Errors |
| 6 | Important | Robust backward compat: fills missing nations AND missing pool types, not just fully-absent key | §Serialization |
| 7 | Minor | Documented "reinforce" vs "recruit" parser ordering quirk | §Parser Changes, §Edge Cases |
| 8 | Minor | Documented damaged/under-construction stables don't give regen | §Stables Building, §Edge Cases |
| 9 | Minor | Documented 0-region base regen as intentional | §Regen Processing, §Edge Cases |
| 10 | Minor | Added `INFANTRY_RECRUIT_GOLD_COST_BASE = 200` constant (was magic number, now explicit) | §Constants |
| 11 | Minor | Removed dead `"recruit_type"` from AI command dicts (executor ignores it — derives from marshal.cavalry) | §AI Recruit |
| 12 | Minor | Added emergent morale dilution note to Design Intent | §Design Intent |
| 13 | Minor | Stables regen table footnote about Britain needing to conquer cities first | §Regen Scenarios |

---

## Implementation Session

### Single Session (Sonnet)

**Scope:** manpower_pools on WorldState, modify recruit for pool drawing + type-based costs, stables building, economy display, AI pool/cost-aware recruit, Berthier voice errors, mock parser tweaks.

**Files modified (7):**

| File | Changes |
|------|---------|
| `world_state.py` | `manpower_pools` init, `DEFAULT_MANPOWER_POOLS`, `_process_manpower_regen()`, `get_cavalry_regen_rate()`, serialization (robust backward compat), constants |
| `region.py` | Add `"stables"` to `BUILDING_TYPES` |
| `executor.py` | Modify `_execute_recruit` (pool drawing, type from marshal.cavalry, dynamic messages, Berthier voice errors), parameterize `_calculate_recruit_cost(base_cost=200)`, `_extract_building_type` (stables keyword), `_execute_economy` (manpower section) |
| `enemy_ai.py` | `_should_build_stables()`, `_find_best_stables_region()`, priority 4.5 stables, pool+cost-aware recruit in `_pick_admin_action` and `_find_weakest_marshal_for_admin` |
| `llm_client.py` | Optional: extract `requested_type` for soft correction message |
| `prompt_builder.py` | Update few-shot examples (no recruit_type in output) |
| `main.py` | Verify recruit endpoint passes through correctly (likely no change needed) |

**No changes to:** `marshal.py`, `combat.py`, `battle_report.py`, `validation.py`

**Estimated tests: ~40-50**

**Smoke test gate:**
```bash
# Recruit for infantry marshal (should auto-infantry, draw from infantry pool)
curl -X POST http://127.0.0.1:8005/command -H "Content-Type: application/json" \
  -d '{"command": "recruit for Davout"}' | python -m json.tool

# Recruit for cavalry marshal (should auto-cavalry, draw from cavalry pool)
curl -X POST http://127.0.0.1:8005/command -H "Content-Type: application/json" \
  -d '{"command": "recruit for Ney"}' | python -m json.tool

# Economy report (should show manpower section with Berthier warning if low)
curl -X POST http://127.0.0.1:8005/command -H "Content-Type: application/json" \
  -d '{"command": "economy"}' | python -m json.tool

# End turn and check regen
curl -X POST http://127.0.0.1:8005/command -H "Content-Type: application/json" \
  -d '{"command": "end turn"}' | python -m json.tool
```

---

## Testing Checklist

### Core Functionality
- [ ] Starting pool initialization per nation (France 80k/15k, Britain 50k/8k, Prussia 60k/10k)
- [ ] Infantry marshal recruit → infantry pool, 10k troops, 200g base
- [ ] Cavalry marshal recruit → cavalry pool, 5k troops, 300g base
- [ ] Pool empty → blocked with Berthier error (pool amount, need amount, regen rate, turns estimate)
- [ ] Cavalry recruit: capital discount (225g), stability premium (450g)
- [ ] Pool doesn't go negative (5000 pool, 5000 recruit → 0)
- [ ] Dynamic message shows correct troop count and type ("5,000 cavalry" / "10,000 infantry")

### Regen
- [ ] Per-turn regen: infantry base rate (5,000) regardless of territory
- [ ] Per-turn regen: cavalry base rate (500)
- [ ] Per-turn regen: plains bonus (+500 per plains region)
- [ ] Per-turn regen: stables bonus (+750 per stables building)
- [ ] Per-turn regen: multiple bonuses stack correctly
- [ ] Pool caps enforced (100k infantry, 30k cavalry)
- [ ] Damaged stables excluded from regen
- [ ] Under-construction stables excluded from regen
- [ ] Regen after territory loss (lose plains → lower cavalry regen)
- [ ] Nation with 0 regions still gets base regen
- [ ] `get_cavalry_regen_rate` returns same value as `_process_manpower_regen` computes

### Stables
- [ ] Stables building: in BUILDING_TYPES, constructs, completes
- [ ] Stables keyword matching ("stable", "horse")

### Serialization
- [ ] Serialization roundtrip (manpower_pools survives save/load)
- [ ] Backward compat: old saves without manpower_pools get correct defaults
- [ ] Backward compat: partial saves (missing nation or pool type) get filled from defaults

### Display
- [ ] Economy report: shows pools, regen rates, Berthier low-cavalry warning
- [ ] Recruit success message includes pool change line
- [ ] All recruit errors use Berthier voice

### Player Parsing
- [ ] "recruit cavalry for Davout" → infantry recruited, Berthier soft correction
- [ ] "recruit for Ney" → auto-cavalry
- [ ] "recruit at Paris" with cavalry marshal nearest → cavalry

### AI Behavior
- [ ] AI recruit uses correct gold cost for cavalry marshals (300 base, not 200)
- [ ] AI skips recruit when pool empty for that marshal's type
- [ ] AI can still recruit infantry after cavalry pool is empty (no skip_actions cascade)
- [ ] AI builds stables when cavalry pool < 60% cap + has cavalry marshal
- [ ] AI skips stables when no cavalry marshals in nation
- [ ] AI skips stables when cavalry pool healthy
- [ ] AI stables: prefers plains regions

### Interaction Tests
- [ ] Two recruits same turn: infantry for Davout + cavalry for Ney (both pools drain independently)
- [ ] Morale dilution: 5k cavalry into 50k army vs 10k infantry into 30k army (different results)
- [ ] Unified cost method: `_calculate_recruit_cost(region, world, base_cost=300)` returns 225 at capital
