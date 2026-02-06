# Phase 6.1: Terrain System — Implementation Spec

> **Purpose:** Add terrain types to regions. Affects combat defense, cavalry effectiveness, and provides integration hooks for economy (Phase 6.2).
> **Scope:** New field on Region, updated combat modifiers, cavalry terrain rules, weighted pathfinding, REGIONS_DATA assignments.
> **Complexity:** Small-medium — ~5-7 files touched, Sonnet work.
> **Implements before:** Phase 6.2 (Economy) which builds on terrain for supply capacity, building eligibility, and movement attrition multipliers.

---

## 1. Terrain Types

Six terrain types covering all Napoleonic-era battlefield conditions:

| Terrain | Defense Bonus | Attrition Multiplier | Supply Modifier | Cavalry Effectiveness | Description |
|---------|--------------|---------------------|-----------------|----------------------|-------------|
| `plains` | +0% | 1.0x | 1.0 | 1.2x (bonus!) | Open ground. Cavalry country. Best terrain for mounted warfare. |
| `forest` | +10% | 1.3x | 0.8 | 0.5x | Wooded terrain. Defender cover. Cavalry can't form up. |
| `hills` | +15% | 1.2x | 0.9 | 0.8x | Elevated ground. Strong defense. Cavalry somewhat limited. |
| `mountains` | +25% | 2.0x | 0.5 | 0.3x | Alpine terrain. Massive defense. Cavalry nearly useless. Devastating attrition. |
| `urban` | +20% | 1.0x | 1.2 | 0.5x | Cities/built-up areas. Strong defense. Cavalry limited in streets. Easy movement (roads). |
| `river_crossing` | +15% | 1.5x | 1.0 | 0.6x | Major river barriers. Attackers cross under fire. Horses vulnerable in water. |

### Design Notes

- **Defense bonus** applies to the DEFENDER in that region. The defender chose this ground.
- **Attrition multiplier** multiplies base movement attrition (Phase 6.2). NOT an AP cost — moving into any region always costs 1 CP regardless of terrain. Terrain determines how many troops you *lose* getting there. Mountains don't take longer, they kill more men on the march.
- **Supply modifier** multiplies the region's base supply capacity (Phase 6.2). Mountains halve supply. Urban boosts it. Stored as data now, consumed in 6.2.
- **Cavalry effectiveness** multiplies cavalry_ratio's contribution to combat. Plains BOOST cavalry (open ground for charges). Mountains nearly eliminate it.
- `terrain` is separate from `region_type` (economic importance). A capital can be urban terrain. A town can be on plains. Independent axes.
- **Future hook (1805):** When CP pools are larger (5-6 per nation), consider making mountains cost 2 CP to enter. Simple integer tier. For Waterloo's 4 CP, everything costs 1 CP.

---

## 2. Region Field Addition

### New Field

```python
# region.py
class Region:
    def __init__(self, name, adjacent_regions, income_value=100, 
                 is_capital=False, terrain="plains"):
        # ... existing fields ...
        self.terrain = terrain  # plains, forest, hills, mountains, urban, river_crossing
```

### Valid Terrain Values

```python
VALID_TERRAINS = {"plains", "forest", "hills", "mountains", "urban", "river_crossing"}
```

Add validation in `__init__` or `from_dict()`:
```python
if terrain not in VALID_TERRAINS:
    raise ValueError(f"Invalid terrain '{terrain}'. Must be one of: {VALID_TERRAINS}")
```

### Serialization

Add to `to_dict()`:
```python
"terrain": self.terrain,
```

Add to `from_dict()`:
```python
region.terrain = data.get("terrain", "plains")  # Default plains for backward compat
```

---

## 3. Updated REGIONS_DATA

Assign terrain to all 13 Waterloo regions based on actual geography:

```python
REGIONS_DATA = {
    "Paris": {
        "adjacent": ["Belgium", "Waterloo", "Brittany", "Lyon"],
        "income": 100,
        "is_capital": True,
        "terrain": "urban"
    },
    "Belgium": {
        "adjacent": ["Paris", "Netherlands", "Waterloo", "Rhine"],
        "income": 100,
        "terrain": "plains"         # Flemish lowlands — cavalry country
    },
    "Netherlands": {
        "adjacent": ["Belgium"],
        "income": 100,
        "terrain": "plains"         # Dutch flatlands
    },
    "Waterloo": {
        "adjacent": ["Belgium", "Paris"],
        "income": 100,
        "terrain": "hills"          # Rolling hills south of Brussels — historically decisive terrain
    },
    "Rhine": {
        "adjacent": ["Belgium", "Bavaria", "Lyon"],
        "income": 100,
        "terrain": "river_crossing" # Rhine river — major barrier
    },
    "Bavaria": {
        "adjacent": ["Rhine", "Vienna", "Lyon"],
        "income": 100,
        "terrain": "hills"          # Bavarian highlands
    },
    "Vienna": {
        "adjacent": ["Bavaria", "Milan"],
        "income": 100,
        "terrain": "urban"          # Major imperial capital
    },
    "Lyon": {
        "adjacent": ["Paris", "Rhine", "Bavaria", "Marseille", "Milan"],
        "income": 100,
        "terrain": "hills"          # Rhône valley foothills
    },
    "Milan": {
        "adjacent": ["Lyon", "Vienna", "Geneva"],
        "income": 100,
        "terrain": "urban"          # Major city in Po Valley
    },
    "Marseille": {
        "adjacent": ["Lyon", "Geneva"],
        "income": 100,
        "terrain": "plains"         # Mediterranean coast flatlands
    },
    "Geneva": {
        "adjacent": ["Marseille", "Milan", "Bordeaux"],
        "income": 100,
        "terrain": "mountains"      # Swiss Alps
    },
    "Brittany": {
        "adjacent": ["Paris", "Bordeaux"],
        "income": 100,
        "terrain": "forest"         # Dense Breton woodland
    },
    "Bordeaux": {
        "adjacent": ["Brittany", "Geneva"],
        "income": 100,
        "terrain": "plains"         # Aquitaine basin
    }
}
```

### Terrain Distribution

- **Plains (4):** Belgium, Netherlands, Marseille, Bordeaux — open campaigning ground, cavalry dominant
- **Hills (3):** Waterloo, Bavaria, Lyon — elevated defensive positions
- **Urban (3):** Paris, Vienna, Milan — major cities with built-up defenses
- **Mountains (1):** Geneva — Alpine barrier, devastating to cross
- **Forest (1):** Brittany — wooded Breton countryside
- **River Crossing (1):** Rhine — major river barrier into German territories

Every terrain type appears at least once. Strategic implications are real: Ney's cavalry dominates on Belgian plains but is nearly useless attacking Geneva through the Alps.

---

## 4. Combat Integration

### Current State

`_get_terrain_bonus()` in combat.py returns a hardcoded dict: `{"open": 0.0, "fortified": 0.3, "mountain": 0.2, "river": 0.15}`. `resolve_battle()` takes `terrain: str = "open"`. The executor currently always passes `"open"`.

### Changes

**Step 1:** Update `_get_terrain_bonus()` with new terrain types:

```python
def _get_terrain_bonus(self, terrain: str) -> float:
    """Get defender bonus based on terrain type."""
    terrain_modifiers = {
        "plains": 0.0,
        "forest": 0.10,
        "hills": 0.15,
        "mountains": 0.25,
        "urban": 0.20,
        "river_crossing": 0.15,
        # Legacy values (backward compat for tests/mods)
        "open": 0.0,
        "fortified": 0.30,
    }
    return terrain_modifiers.get(terrain, 0.0)
```

Keep "open" and "fortified" as legacy aliases for backward compatibility with existing tests and modding system.

**Step 2:** Update executor to pass region terrain to `resolve_battle()`:

In `_execute_attack()`, where `resolve_battle()` is called, change from hardcoded `"open"` to reading from the region:

```python
# Read terrain from defender's region (defender chose this ground)
region = world.get_region(defender.location)
terrain = region.terrain if region else "plains"
result = combat.resolve_battle(attacker, defender, terrain=terrain)
```

**Step 3:** Add terrain to combat result messages:

```python
# In resolve_battle(), add terrain message to result
if terrain_bonus > 0:
    terrain_name = terrain.replace("_", " ").title()
    terrain_message = f"{defender.name} benefits from {terrain_name} terrain (+{int(terrain_bonus * 100)}% defense)"
    # Add to result dict alongside other combat messages
```

### Single-Source Compliance

Terrain defense bonus stays in `combat.py` (`_get_terrain_bonus()`), NOT in `marshal.py`. This is correct — terrain is a regional/environmental modifier, not a marshal modifier. Follows the established pattern:

```
marshal.py → marshal-specific modifiers (stance, personality, fortify, cavalry)
combat.py  → environmental modifiers (terrain, Phase 6.2 Star Fort building)
```

---

## 5. Cavalry Terrain Rules

### Design Rationale

Napoleon's cavalry dominated on plains but was useless in mountains and forests. Army composition should matter per-region. Ney's cavalry-heavy corps excels on Belgian plains but struggles attacking into Geneva. Davout's infantry-heavy corps is better for mountain campaigns. This creates real strategic decisions about matching the right marshal to the right terrain.

### Cavalry Effectiveness Multiplier

New constant dict:

```python
TERRAIN_CAVALRY_EFFECTIVENESS = {
    "plains": 1.2,          # Cavalry country — bonus for open maneuver
    "forest": 0.5,          # Can't form up in trees
    "hills": 0.8,           # Somewhat limited on slopes
    "mountains": 0.3,       # Nearly useless on mountain paths
    "urban": 0.5,           # City streets limit cavalry
    "river_crossing": 0.6,  # Horses vulnerable crossing water
}
```

### Application in Combat

The game already uses `cavalry_ratio` in combat calculations. The terrain multiplier modifies how much cavalry contributes:

```python
# In combat resolution, where cavalry_ratio affects combat:
terrain_cavalry_mult = TERRAIN_CAVALRY_EFFECTIVENESS.get(terrain, 1.0)
effective_cavalry_ratio = marshal.cavalry_ratio * terrain_cavalry_mult
```

The exact integration point depends on how cavalry_ratio currently feeds into combat modifiers. The implementer should trace the cavalry_ratio usage in combat.py and marshal.py, then apply the terrain multiplier at the point where cavalry_ratio is read. The key principle: cavalry_ratio's contribution to attack power is scaled by terrain.

### Glorious Charge Terrain Restriction

Glorious charge (2x damage dealt AND taken) is blocked on terrain where cavalry charges are physically impossible:

```python
CHARGE_BLOCKED_TERRAIN = {"mountains", "forest", "urban"}

# In the glorious charge check (combat.py):
if glorious_charge and terrain in CHARGE_BLOCKED_TERRAIN:
    glorious_charge = False
    charge_blocked_message = (
        f"{attacker.name}'s cavalry cannot charge in {terrain.replace('_', ' ')} terrain! "
        f"The attack proceeds without the charge bonus."
    )
```

Glorious charge IS allowed on: plains (ideal), hills (cavalry can charge downhill), river_crossing (charge across the ford). These are historical — cavalry charges at Austerlitz crossed frozen lakes, and charges on hills were common.

### Cavalry Mountain Attrition (Data for Phase 6.2)

Cavalry-heavy armies take extra attrition in mountains. Horses die on mountain paths — this is historically critical (Napoleon lost thousands of horses crossing the Alps in 1800).

New constant:

```python
TERRAIN_CAVALRY_ATTRITION_BONUS = {
    "mountains": 0.5,   # +50% additional attrition based on cavalry ratio
    # Other terrain: no cavalry-specific attrition bonus
}
```

**Not consumed in Phase 6.1.** Phase 6.2 applies this when implementing movement attrition:

```python
# Phase 6.2 movement attrition calculation:
base_attrition = 0.01
terrain_mult = region.movement_cost  # 1.0-2.0x from terrain
cavalry_attrition_bonus = TERRAIN_CAVALRY_ATTRITION_BONUS.get(terrain, 0.0) * marshal.cavalry_ratio
total_attrition = base_attrition * terrain_mult + cavalry_attrition_bonus
```

A cavalry-heavy marshal (cavalry_ratio 0.6) crossing mountains: `0.01 * 2.0 + 0.5 * 0.6 = 0.02 + 0.30 = 0.32` — 32% losses. Devastating, as it should be. An infantry-heavy marshal (cavalry_ratio 0.1): `0.01 * 2.0 + 0.5 * 0.1 = 0.02 + 0.05 = 0.07` — 7% losses. Painful but survivable.

---

## 6. Weighted Pathfinding

### Problem

Current pathfinding (BFS) picks shortest-hop routes. With terrain, a 2-hop path through mountains may cost far more troops than a 3-hop path through plains. Strategic orders (MOVE_TO) and enemy AI need to pick least-attrition routes, not least-hop routes.

### Solution

Replace BFS with Dijkstra using attrition multiplier as edge weight.

```python
def find_weighted_path(self, start: str, end: str, regions: dict) -> List[str]:
    """
    Find least-attrition path between two regions using Dijkstra.
    
    Edge weight = destination region's attrition multiplier.
    Returns list of region names from start to end (inclusive).
    """
    import heapq
    
    # Priority queue: (cumulative_cost, region_name, path)
    queue = [(0.0, start, [start])]
    visited = set()
    
    while queue:
        cost, current, path = heapq.heappop(queue)
        
        if current == end:
            return path
        
        if current in visited:
            continue
        visited.add(current)
        
        region = regions.get(current)
        if not region:
            continue
            
        for neighbor_name in region.adjacent_regions:
            if neighbor_name not in visited:
                neighbor = regions.get(neighbor_name)
                if neighbor:
                    edge_cost = TERRAIN_MOVEMENT_COST.get(neighbor.terrain, 1.0)
                    heapq.heappush(queue, (cost + edge_cost, neighbor_name, path + [neighbor_name]))
    
    return []  # No path found
```

### Integration Points

**MOVE_TO strategic orders:** Currently uses shortest-path to determine next step. Replace with `find_weighted_path()`. The marshal still moves 1 region per turn, but chooses the path that minimizes total attrition.

**Enemy AI pathfinding:** AI's `_find_retreat_destination()` and strategic movement logic use path distance. Replace with weighted pathfinding so AI armies also avoid marching through the Alps unless it's the only route.

**PURSUE strategic orders:** PURSUE follows the target directly — it does NOT use weighted pathfinding. You're chasing, not choosing a scenic route. The attrition is the price of pursuit.

**Future hook (V2b):** PURSUE through high-attrition terrain (mountains, river crossings) should trigger a marshal objection popup. "Sire, the enemy retreats into the Alps. My cavalry will be destroyed on those mountain paths..." Player decides: pursue or hold. This is a natural personality-driven decision moment. Not Phase 6.1.

### Existing get_distance() Method

If `get_distance()` exists on WorldState, it should also be updated to use weighted distances (or a new `get_weighted_distance()` added alongside it). The old hop-count distance is still useful for adjacency checks and simple range calculations — keep both.

---

## 7. Terrain Constants (Centralized)

All terrain data in one place for easy tuning:

```python
# region.py (or backend/constants/terrain.py if preferred)

VALID_TERRAINS = {"plains", "forest", "hills", "mountains", "urban", "river_crossing"}

TERRAIN_DEFENSE_BONUS = {
    "plains": 0.0,
    "forest": 0.10,
    "hills": 0.15,
    "mountains": 0.25,
    "urban": 0.20,
    "river_crossing": 0.15,
}

TERRAIN_MOVEMENT_COST = {
    "plains": 1.0,
    "forest": 1.3,
    "hills": 1.2,
    "mountains": 2.0,
    "urban": 1.0,
    "river_crossing": 1.5,
}

TERRAIN_SUPPLY_MODIFIER = {
    "plains": 1.0,
    "forest": 0.8,
    "hills": 0.9,
    "mountains": 0.5,
    "urban": 1.2,
    "river_crossing": 1.0,
}

TERRAIN_CAVALRY_EFFECTIVENESS = {
    "plains": 1.2,
    "forest": 0.5,
    "hills": 0.8,
    "mountains": 0.3,
    "urban": 0.5,
    "river_crossing": 0.6,
}

TERRAIN_CAVALRY_ATTRITION_BONUS = {
    "mountains": 0.5,
    # Other terrain: 0.0 (no cavalry-specific attrition)
}

CHARGE_BLOCKED_TERRAIN = {"mountains", "forest", "urban"}
```

`combat.py` imports `TERRAIN_DEFENSE_BONUS` and `CHARGE_BLOCKED_TERRAIN`. Other constants imported by Phase 6.2 (economy) and pathfinding.

---

## 8. Terrain Display

### Status Command

When querying region status or scouting, terrain appears:

```
"Waterloo — Controlled by Britain. Terrain: Hills (+15% defense). Garrison: Wellington (68,000 troops)."
```

### Combat Messages

Terrain info included in battle results (§4 Step 3). Additionally, cavalry terrain messages:

```
"Ney's cavalry is hampered by Mountain terrain (30% effectiveness)"
"Ney's cavalry cannot charge in Mountain terrain! The attack proceeds without the charge bonus."
```

---

## 9. Computed Properties on Region (Data for Phase 6.2)

```python
@property
def movement_cost(self) -> float:
    """Attrition multiplier for entering this region. NOT an AP cost."""
    return TERRAIN_MOVEMENT_COST.get(self.terrain, 1.0)

@property
def supply_modifier(self) -> float:
    """Supply capacity modifier from terrain."""
    return TERRAIN_SUPPLY_MODIFIER.get(self.terrain, 1.0)

@property
def cavalry_effectiveness(self) -> float:
    """Cavalry combat effectiveness multiplier in this terrain."""
    return TERRAIN_CAVALRY_EFFECTIVENESS.get(self.terrain, 1.0)
```

These are NOT serialized — computed on access from terrain field. Phase 6.2 consumes movement_cost and supply_modifier. cavalry_effectiveness is consumed in Phase 6.1 combat.

---

## 10. Serialization Summary

### Region — New Fields

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `terrain` | str | "plains" | One of VALID_TERRAINS |

### Not Serialized (Computed Properties)

| Property | Derived From | Used In |
|----------|-------------|---------|
| `movement_cost` | terrain | Phase 6.2 movement attrition |
| `supply_modifier` | terrain | Phase 6.2 supply capacity |
| `cavalry_effectiveness` | terrain | Phase 6.1 combat (cavalry ratio modifier) |

---

## 11. Implementation Order

All Sonnet. Should fit in one session.

1. **Add terrain constants** — Create centralized terrain dicts (§7). Either in region.py or a new constants file.
2. **Add terrain field to Region** — New field, validation against VALID_TERRAINS, to_dict/from_dict.
3. **Update REGIONS_DATA** — Assign terrain to all 13 regions per §3.
4. **Add computed properties** — movement_cost, supply_modifier, cavalry_effectiveness on Region.
5. **Update _get_terrain_bonus()** — New terrain types in combat.py, keep legacy aliases.
6. **Update executor** — Read region.terrain when calling resolve_battle().
7. **Add cavalry terrain rules** — Cavalry effectiveness multiplier in combat, glorious charge terrain blocking.
8. **Add terrain combat messages** — Terrain defense info and cavalry restriction messages in battle results.
9. **Implement weighted pathfinding** — Dijkstra by attrition cost. Update MOVE_TO and AI pathfinding. Keep PURSUE on direct path.
10. **Update terrain display** — Show terrain in region status/scout output.
11. **Update serialization tests** — Add terrain to Region fixtures in test_serialization_enforcement.py.
12. **Update MODDING_FORMAT.md** — Document terrain field and valid values for modders.

### Testing

- Test each terrain type gives correct defense bonus in combat
- Test executor passes region terrain (not hardcoded "open") to resolve_battle()
- Test cavalry effectiveness is modified by terrain
- Test glorious charge blocked in mountains/forest/urban, allowed in plains/hills/river_crossing
- Test weighted pathfinding prefers lower-attrition routes (e.g., avoids mountains when alternate path exists)
- Test weighted pathfinding still works when mountains are the only path
- Test PURSUE ignores weighted pathfinding (follows directly)
- Test terrain serialization round-trips correctly
- Test backward compat: regions without terrain field default to "plains"
- Test legacy terrain values ("open", "fortified") still work in combat

---

## 12. Integration Points for Phase 6.2 (Economy)

When implementing the economy system, these terrain connections need wiring:

| Economy Feature | Terrain Integration | How |
|----------------|---------------------|-----|
| Movement attrition | Terrain multiplies base attrition | `attrition *= region.movement_cost` |
| Cavalry mountain attrition | Extra losses for cavalry in mountains | `attrition += CAVALRY_ATTRITION_BONUS * cavalry_ratio` |
| Supply capacity | Terrain modifies base supply cap | `capacity = int(base_capacity * region.supply_modifier)` |
| Star Fort defense bonus | +25% stacks ADDITIVELY with terrain | `total_bonus = terrain_bonus + star_fort_bonus` |
| Star Fort building eligibility | Only in cities (region_type), also blocked in mountains | Check both region_type AND terrain |
| Training Ground eligibility | Blocked in mountains (need flat ground) | Check terrain != "mountains" |
| Supply Depot eligibility | Blocked in mountains (logistics impossible) | Check terrain != "mountains" |

### Star Fort + Terrain Stacking (Phase 6.2)

```python
terrain_bonus = self._get_terrain_bonus(terrain)        # 0.0 to 0.25
star_fort_bonus = 0.25 if region_has_star_fort else 0.0  # +25%
total_defense_bonus = terrain_bonus + star_fort_bonus
defender_effective *= (1 + total_defense_bonus)
```

Urban (+20%) + Star Fort (+25%) = +45% defense. Mountains (+25%) + Star Fort (+25%) = +50% defense. Strong but beatable with drill, flanking, shock skills, and numerical superiority.

---

## 13. Economy Spec Update Required

After this spec is implemented, the ECONOMY_SPEC.md needs one rename applied throughout:

**Rename "Fortification" building → "Star Fort"** in all references:
- §8 (Buildings) — building type name, descriptions, costs
- §8 (City Fortification + Contested Capture) — rename section
- §12 (Integration Points) — Star Fort references
- §16 (Deferred) — any fortification mentions

Rationale: Avoids confusion with marshal "fortify" action (temporary field entrenchments) vs Star Fort building (permanent city fortification). "Star Fort" is period-accurate (Vauban-style fortifications were everywhere in Napoleonic Europe).

---

## 14. Pre-Implementation Decisions (Confirmed)

Decisions made during codebase analysis and design review, February 2026.

### cavalry_ratio → Boolean Proxy
The spec originally assumed `cavalry_ratio: float` existed on Marshal. Analysis confirmed only `marshal.cavalry: bool` exists.
**Decision: Use boolean proxy for Phase 6.1. Defer cavalry_ratio: float to 1805 expansion.**
- `cavalry=True` → TERRAIN_CAVALRY_EFFECTIVENESS multiplier applies to recklessness attack bonus
- `cavalry=False` → terrain cavalry rules have zero effect
- TERRAIN_CAVALRY_EFFECTIVENESS constants created as data hooks for future use
- cavalry_ratio: float will emerge naturally when manpower pools (infantry/cavalry/artillery) are implemented

### Glorious Charge Blocking Location
**Decision: Charge blocking check goes in executor.py, NOT combat.py.**
- Recklessness popup check (~line 1620): suppress popup if terrain in CHARGE_BLOCKED_TERRAIN
- _execute_glorious_charge() (~line 5846): safety net rejection
- resolve_battle() receives terrain for defense bonus only (separate concern)

### All 5 resolve_battle() Call Sites
Analysis found 5 call sites in executor.py (not 1 as spec implied):
1. _execute_attack() main path (~line 2018)
2. Strategic sally #1 (~line 3983)
3. Strategic sally #2 (~line 4109)
4. Strategic sally #3 (~line 4220)
5. _execute_glorious_charge() (~line 5922) — was missing terrain param entirely

All updated to read terrain from defender's region.

### Pathfinding Strategy
**Decision: Add weighted pathfinding ALONGSIDE existing BFS. Don't replace.**
- New: find_weighted_path() (Dijkstra), get_weighted_distance()
- Keep: find_path() (BFS), get_distance() (hop count)
- MOVE_TO + enemy AI → weighted
- PURSUE + auto-charge + adjacency → BFS

### Terrain Type Count
**Decision: 6 types confirmed. No merges, no additions for Waterloo.**
- All 6 passed the "one-sentence differentiation test"
- Closest pair (hills/river_crossing) distinguished by attrition cost (1.2x vs 1.5x)
- marsh/swamp identified as candidate for 1805 expansion (Austerlitz, Berezina)
- desert/steppe/coastal rejected — covered by existing types or out of scope

### Known Integration Points Found During Analysis
- Wellington's "Reverse Slope Defense" TODO (combat.py:161) now has terrain hook
- _execute_glorious_charge() also missing flanking_bonus/flanking_message params (separate issue, not 6.1 scope)
- Pre-existing Region constructor bugs in test_objection_v2.py and test_strategic_objections.py (passing "France" as income_value) — not broken by terrain changes but should be fixed eventually
- backend/modding/doc_generator.py:124 constructs example Region — needs terrain in example

---

## 15. Future Terrain Enhancements (Not Phase 6.1)

| Feature | Phase | Notes |
|---------|-------|-------|
| PURSUE mountain/river objection popup | V2b | Marshal objects to chasing through brutal terrain. Personality-driven moment. |
| Mountains cost 2 CP to enter | 1805 | When CP pools are 5-6, integer movement costs. Weighted pathfinding already handles this. |
| Terrain affects attacker (not just defender) | Post-EA | Mountains could penalize attacker beyond defender bonus. |
| Weather + terrain interaction | Post-EA | Rain + river_crossing = +25% defense instead of +15%. Winter mountains = impassable. |
| Seasonal terrain changes | Post-EA | Mud season, frozen rivers, etc. |
| Terrain-specific combat narratives | Phase 7 | LLM-generated: "Ney's cavalry struggles up the muddy slopes." |
| Visual terrain on map | EU4 map | Different colors/textures per terrain type on the real map. |
| Terrain revealed by scouting | Phase 6.5 | Unknown terrain until scouted (fog of war). |
| Marshal terrain affinity | Phase 9 | Some marshals fight better in specific terrain (mountain specialists, etc.). |
