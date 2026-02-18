# Manpower Pools — Final Implementation Spec

> **Phase 6 Feature. Ready for implementation.**
> **Complexity:** Medium (1 session)
> **Prerequisites:** None (economy, recruitment, buildings, combat all complete)
> **Reviewed:** February 2026 — all numbers evaluated, edge cases resolved.

---

## Design Intent

Cavalry was the decisive arm of Napoleonic warfare — and the hardest to replace. France's cavalry never recovered after 1812 because *horses died faster than they could be bred*. This system makes cavalry feel precious: easy to lose, slow to rebuild, and strategically valuable enough that players think twice before committing charges.

The core tension: infantry marshals are cheap to reinforce; cavalry marshals are expensive, scarce, and slow to rebuild. Losing a cavalry marshal is a campaign-altering setback. Controlling horse-producing territory gives a lasting advantage.

**Cavalry is a unit type, not a composition.** Ney IS cavalry — always moves 2, always charges at full power. The scarcity comes from the pool, not from degrading what cavalry means.

**No artillery pool yet.** Artillery unit type doesn't exist. When it's built, its pool gets added with the same pattern.

---

## All Numbers (Final)

### Constants (define in `world_state.py`)

```python
# ═══════ MANPOWER POOL CONSTANTS ═══════
INFANTRY_RECRUIT_AMOUNT = 10000        # Troops per infantry recruit (unchanged)
CAVALRY_RECRUIT_AMOUNT = 5000          # Troops per cavalry recruit (half infantry — precious)
CAVALRY_RECRUIT_GOLD_COST_BASE = 300   # Gold cost for cavalry recruit (vs 200 infantry)
INFANTRY_BASE_REGEN = 5000             # Per nation per turn (fast — infantry isn't the bottleneck)
CAVALRY_BASE_REGEN = 500               # Per nation per turn (slow — this IS the bottleneck)
PLAINS_CAVALRY_REGEN = 500             # Bonus per plains region controlled
STABLES_CAVALRY_REGEN = 750            # Bonus per stables building owned
MAX_INFANTRY_POOL = 100000             # Pool cap
MAX_CAVALRY_POOL = 30000               # Pool cap
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

### Stables Building

| Property | Value |
|----------|-------|
| Gold cost | 300g |
| Build time | 2 turns |
| Allowed in | capital, major_city, city |
| Uses building slot | Yes (competes with Market, Depot, Fort, Training Ground) |
| Cavalry regen bonus | +750/turn to nation's cavalry pool |

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
    gold_cost = self._calculate_cavalry_recruit_cost(region, world)  # Base 300g
else:
    NEW_TROOPS = INFANTRY_RECRUIT_AMOUNT      # 10,000
    gold_cost = self._calculate_recruit_cost(region, world)          # Base 200g (existing)

# Check pool
pool = world.manpower_pools.get(acting_nation, {})
available = pool.get(recruit_type, 0)
if available < NEW_TROOPS:
    regen_rate = world.get_cavalry_regen_rate(acting_nation) if recruit_type == "cavalry" else INFANTRY_BASE_REGEN
    turns_until = max(1, (NEW_TROOPS - available + regen_rate - 1) // regen_rate)
    return {
        "success": False,
        "message": f"Insufficient {recruit_type} manpower! Pool: {available:,}, need: {NEW_TROOPS:,}. "
                   f"Recovering +{regen_rate:,}/turn — available in ~{turns_until} turn{'s' if turns_until > 1 else ''}."
    }

# Draw from pool
world.manpower_pools[acting_nation][recruit_type] -= NEW_TROOPS

# Existing morale dilution unchanged
# Existing gold deduction unchanged (using type-specific cost)
# Existing marshal.add_troops(NEW_TROOPS) unchanged
```

### Cavalry Gold Cost

```python
def _calculate_cavalry_recruit_cost(self, region, world) -> int:
    """Calculate cavalry recruitment gold cost. Same modifiers as infantry but higher base."""
    base_cost = CAVALRY_RECRUIT_GOLD_COST_BASE  # 300
    if region.region_type == "capital":
        return int(base_cost * 0.75)  # 225
    if 51 <= region.stability <= 75:
        return int(base_cost * 1.50)  # 450
    return base_cost  # 300
```

### Player says "recruit cavalry for Davout"?

If the player explicitly says "recruit cavalry" for an infantry marshal, soft clarification in the response:

```
Marshal Davout commands infantry. 10,000 infantry recruited.
```

The system ignores the type keyword and recruits based on marshal type. No error, no confusion — just a gentle correction.

---

## Regen Processing

### New method in `world_state.py`

```python
def _process_manpower_regen(self):
    """Regenerate manpower pools per nation. Called during advance_turn."""
    all_nations = [self.player_nation] + list(self.enemy_nations)
    for nation in all_nations:
        if nation not in self.manpower_pools:
            continue

        controlled = [r for r in self.regions.values() if r.controller == nation]

        # Infantry: generous base regen
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

### Helper for cavalry regen rate (used in error messages)

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

### AI Recruit Type

Trivial — derived from marshal type:

```python
recruit_type = "cavalry" if getattr(marshal, 'cavalry', False) else "infantry"
```

Add `"recruit_type": recruit_type` to AI recruit command dicts. The executor handles pool checks from there.

---

## Serialization

### WorldState

```python
# to_dict()
"manpower_pools": {k: v.copy() for k, v in self.manpower_pools.items()},

# from_dict()
world.manpower_pools = {k: v.copy() for k, v in data.get("manpower_pools", {}).items()}
# Backward compat: if no manpower_pools in save, initialize defaults
if not world.manpower_pools:
    world.manpower_pools = {
        "France": {"infantry": 80000, "cavalry": 15000},
        "Britain": {"infantry": 50000, "cavalry": 8000},
        "Prussia": {"infantry": 60000, "cavalry": 10000},
    }
```

### Marshal

No changes. `cavalry: bool` already serializes. No new fields.

**Run `pytest tests/test_serialization_enforcement.py -v` after implementation.**

---

## Parser Changes

### Mock Parser (llm_client.py)

No changes needed to the recruit block. The `recruit_type` is determined by marshal type in the executor, not parsed from the command. The existing `"recruit"` parsing stays as-is.

However, if we want the soft correction message ("Marshal Davout commands infantry"), the mock parser can optionally extract a `requested_type` for the executor to compare against:

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
    lines.append(f"  [WARNING] Cavalry pool too low to recruit! (need {CAVALRY_RECRUIT_AMOUNT:,})")
```

### Recruitment result messages

Infantry:
```
10,000 infantry recruited at Paris for Marshal Davout.
Infantry pool: 80,000 → 70,000. Cost: 200g.
Morale: 85% -> 82%
```

Cavalry:
```
5,000 cavalry recruited at Paris for Marshal Ney.
Cavalry pool: 15,000 → 10,000. Cost: 300g.
Morale: 90% -> 88%
```

---

## Godot Changes

Minimal — no new UI needed beyond what economy report shows. Manpower info rides on the existing economy text display. Error messages on failed recruitment explain the situation.

---

## Edge Case Resolutions

| Edge Case | Resolution |
|-----------|-----------|
| Player says "recruit cavalry for Davout" | Soft correction: "Marshal Davout commands infantry. 10,000 infantry recruited." Recruits infantry, no error. |
| Player says bare "recruit at Belgium" | Finds nearest marshal, determines type from `marshal.cavalry`. Works exactly as before. |
| Two marshals (1 cav, 1 inf) in same region | `find_nearest_marshal_to_region` picks one. Player can specify "recruit for Ney" for precision. |
| Cavalry pool empty, player tries to recruit for Ney | Blocked with clear message: "Insufficient cavalry manpower! Pool: 0, need: 5,000. Recovering +2,000/turn — available in ~3 turns." |
| Nation has no cavalry marshals (Prussia) | Cavalry pool exists but is never drawn from. Sits at cap. No harm. |
| Garrison detachments | Garrisons use `take_casualties()` as before. No pool interaction. Garrisons are static defenders, not recruitable. |
| Broken marshal (2k troops) recruited back to 7k | Pool drawn normally. No special cases for broken marshals. |

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

## Implementation Session

### Single Session (Sonnet)

**Scope:** manpower_pools on WorldState, modify recruit for pool drawing + type-based costs, stables building, economy display, AI stables + recruit type, mock parser tweaks.

**Files modified (7):**

| File | Changes |
|------|---------|
| `world_state.py` | `manpower_pools` init, `_process_manpower_regen()`, `get_cavalry_regen_rate()`, serialization, constants |
| `region.py` | Add `"stables"` to `BUILDING_TYPES` |
| `executor.py` | Modify `_execute_recruit` (pool drawing, type from marshal.cavalry, cavalry cost), `_extract_building_type` (stables keyword), `_execute_economy` (manpower section) |
| `enemy_ai.py` | `_should_build_stables()`, `_find_best_stables_region()`, priority 4.5 stables, recruit_type in command dicts |
| `llm_client.py` | Optional: extract `requested_type` for soft correction message |
| `prompt_builder.py` | Update few-shot examples (no recruit_type in output) |
| `main.py` | Verify recruit endpoint passes through correctly (likely no change needed) |

**No changes to:** `marshal.py`, `combat.py`, `battle_report.py`, `validation.py`

**Estimated tests: ~35-45**
- Starting pool initialization per nation
- Infantry marshal recruit draws from infantry pool (10k, 200g)
- Cavalry marshal recruit draws from cavalry pool (5k, 300g)
- Pool empty blocks recruitment (with helpful error message + regen rate + turns estimate)
- Cavalry recruit capital discount (225g)
- Cavalry recruit stability premium (450g)
- Pool regen: base rates correct
- Pool regen: plains bonus applied per region
- Pool regen: stables bonus applied per building
- Pool regen: multiple bonuses stack correctly
- Pool caps enforced (doesn't exceed max)
- Stables building: added to BUILDING_TYPES, construction, completion
- Stables keyword extraction ("stable", "horse")
- Serialization roundtrip (save/load preserves manpower_pools)
- Backward compat: old saves without manpower_pools get defaults
- Economy report shows infantry pool + regen rate
- Economy report shows cavalry pool + regen rate
- Economy report shows warning when cavalry pool too low
- "recruit cavalry for Davout" → recruits infantry with soft correction
- "recruit for Ney" → auto-cavalry
- "recruit at Paris" with cavalry marshal nearest → cavalry
- AI recruit type derived from marshal.cavalry
- AI builds stables when cavalry pool low + has cavalry marshal
- AI skips stables when no cavalry marshals in nation
- AI skips stables when cavalry pool healthy
- AI stables: prefers plains regions

**Smoke test gate:**
```bash
# Recruit for infantry marshal (should auto-infantry, draw from infantry pool)
curl -X POST http://127.0.0.1:8005/command -H "Content-Type: application/json" \
  -d '{"command": "recruit for Davout"}' | python -m json.tool

# Recruit for cavalry marshal (should auto-cavalry, draw from cavalry pool)
curl -X POST http://127.0.0.1:8005/command -H "Content-Type: application/json" \
  -d '{"command": "recruit for Ney"}' | python -m json.tool

# Economy report (should show manpower section)
curl -X POST http://127.0.0.1:8005/command -H "Content-Type: application/json" \
  -d '{"command": "economy"}' | python -m json.tool

# End turn and check regen
curl -X POST http://127.0.0.1:8005/command -H "Content-Type: application/json" \
  -d '{"command": "end turn"}' | python -m json.tool
```

---

## Testing Checklist

- [ ] Starting pool initialization per nation (France 80k/15k, Britain 50k/8k, Prussia 60k/10k)
- [ ] Infantry marshal recruit → infantry pool, 10k troops, 200g base
- [ ] Cavalry marshal recruit → cavalry pool, 5k troops, 300g base
- [ ] Pool empty → blocked with clear error (pool amount, need amount, regen rate, turns estimate)
- [ ] Cavalry recruit: capital discount (225g), stability premium (450g)
- [ ] Per-turn regen: infantry base rate (5,000)
- [ ] Per-turn regen: cavalry base rate (500)
- [ ] Per-turn regen: plains bonus (+500 per plains region)
- [ ] Per-turn regen: stables bonus (+750 per stables building)
- [ ] Pool caps enforced (100k infantry, 30k cavalry)
- [ ] Stables building: in BUILDING_TYPES, constructs, completes
- [ ] Stables keyword matching ("stable", "horse")
- [ ] Serialization roundtrip (manpower_pools survives save/load)
- [ ] Backward compat: old saves without manpower_pools get correct defaults
- [ ] Economy report: shows pools, regen rates, low-cavalry warning
- [ ] "recruit cavalry for Davout" → infantry recruited, soft correction message
- [ ] AI: derives recruit_type from marshal.cavalry
- [ ] AI: builds stables when cavalry pool < 60% cap + has cavalry marshal
- [ ] AI: skips stables when no cavalry marshals in nation
- [ ] AI: stables placement prefers plains regions
