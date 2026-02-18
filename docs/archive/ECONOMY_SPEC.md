# Phase 6.1: Economy System — Implementation Spec

> **Purpose:** Complete specification for Claude Code to review and implement.
> **Scope:** Fully functional economy at Waterloo 13-region scale. Designed to scale to 80-100 regions in 1805 without rewrite.
> **Depends on:** Nothing (first Phase 6 feature)
> **Feeds into:** Reinforcements (AI recruit), Buildings, Attrition, Sieges, War Damage

---

## 1. Two Action Point Pools

### Design Rationale

Napoleon commanded armies AND administered an empire simultaneously. One AP pool forces players to choose between fighting and managing — the wrong tension. Two pools let both happen in parallel, creating the right tension: "which MILITARY priority?" and separately "which ADMINISTRATIVE priority?"

### Implementation

**Command Points (CP):** Existing `actions_remaining` / `max_actions_per_turn` on WorldState. Military orders only. No changes to existing system.

**Administration Points (AdminAP):** New field on WorldState.

```python
# world_state.py
self.admin_actions_remaining = 2    # France base
self.max_admin_actions = 2
```

Per-nation base values (for 1805 expansion):

| Nation | CP | AdminAP | Notes |
|--------|-----|---------|-------|
| France | 4 | 2 | Current default |
| Britain | 3 | 3 | Naval/economic power |
| Austria | 4 | 2 | |
| Russia | 3 | 1 | Vast but slow bureaucracy |
| Prussia | 3 | 2 | |

Phase 9 (Advisors): `admin_actions = base + advisor_bonus`

### Unused Admin AP → Income Bonus

Each unused Admin AP at end of turn generates bonus gold: **+75 gold per unused AP.** Thematically: "Your administrators collect additional taxes." This creates a real trade-off — spending AP on buildings/recruitment has an opportunity cost.

Display at end of turn: `"Administration: 1 unused AP → +75 gold bonus"`

Phase 9 hook: Advisor stat modifies this rate (better finance advisor = more gold per unused AP).

### Actions by Pool

| Command Points (military) | Admin Points (economic) |
|---|---|
| Attack, Move, Defend | Recruit troops |
| Fortify, Drill, Scout | Build in region |
| Strategic orders (MOVE_TO, PURSUE, HOLD, SUPPORT) | Repair war damage |
| Stance changes | (Phase 8) Diplomacy actions |
| Cancel orders | (Phase 8) Send subsidies |

Free actions (no cost from either pool): status, help, end turn, wait, retreat, economy/treasury/finances.

### Turn Structure

**Interleaved.** Player can mix CP and AdminAP actions freely in any order. Same parser, same command input. The executor checks which pool to deduct from based on action type.

```python
# executor.py — action cost routing
ADMIN_ACTIONS = {"recruit", "build", "repair"}

def _get_action_pool(self, action: str) -> str:
    """Return which pool an action draws from."""
    if action in ADMIN_ACTIONS:
        return "admin"
    return "command"
```

Admin actions use a **separate `use_admin_action()` method** on WorldState, NOT the existing `use_action()`. This keeps the two pools cleanly separated. The executor checks action type → routes to correct pool method.

```python
# world_state.py
def use_admin_action(self, cost: int = 1) -> bool:
    """Consume admin action points. Returns False if insufficient."""
    if self.admin_actions_remaining < cost:
        return False
    self.admin_actions_remaining -= cost
    return True
```

### Enemy AI Admin Phase

Runs AFTER military actions in enemy turn. Uses same executor (building blocks). AI gets same AdminAP pool.

AI admin priority:
1. Any marshal below 40% starting strength AND treasury > recruit cost → recruit for weakest marshal
2. Border city unfortified AND treasury > 400 → build fortification
3. Damaged high-income region AND treasury > 150 → repair
4. Otherwise save (benefit from unused AP bonus)

AI should recruit toward a target army size per marshal (not dump everything into one). Target = starting strength or regional average, whichever is lower.

### Serialization

New fields on WorldState:
- `admin_actions_remaining: int`
- `max_admin_actions: int`

Add to `to_dict()`, `from_dict()` with `.get()` defaults (2 for both).

---

## 2. Region Income

### Current State

All 13 regions have flat `income_value = 100`. Only Paris is `is_capital = True`. `calculate_turn_income()` and `apply_turn_income()` exist and work. Capital bonus of +200 for Paris.

### Changes

Add `region_type` field to Region. Differentiate income by type:

| Region Type | Income | Waterloo Examples |
|-------------|--------|-------------------|
| `capital` | 300 | Paris |
| `major_city` | 200 | Brussels (make capital for Britain scenario), Lyon, Vienna |
| `city` | 150 | Milan, Marseille |
| `town` | 100 | Belgium, Rhine, Bavaria, Geneva |
| `rural` | 50 | Brittany, Bordeaux, Waterloo, Netherlands |

**Remove the separate +200 capital bonus from `calculate_turn_income()`.** Capital income (300) already reflects its importance. The old bonus was a placeholder.

### Income Modifiers

Raw income is modified by:

```python
effective_income = base_income * stability_modifier * war_damage_modifier
```

Where:
- `stability_modifier`: 0.0 to 1.0 based on stability score (see §4)
- `war_damage_modifier`: 0.5 to 1.0 based on damage level (see §7)

### Per-Nation Income

`calculate_turn_income()` must work for ANY nation, not just player. Currently hardcoded to `self.player_nation`. Refactor to accept a nation parameter:

```python
def calculate_turn_income(self, nation: str = None) -> Dict:
    """Calculate income for a nation. Defaults to player_nation."""
    nation = nation or self.player_nation
    # ... same logic but filtered by nation
```

Enemy AI calls this for its own nations during admin phase.

### Updated REGIONS_DATA

```python
REGIONS_DATA = {
    "Paris": {
        "adjacent": ["Belgium", "Waterloo", "Brittany", "Lyon"],
        "income": 300,
        "region_type": "capital",
        "is_capital": True
    },
    "Belgium": {
        "adjacent": ["Paris", "Netherlands", "Waterloo", "Rhine"],
        "income": 100,
        "region_type": "town"
    },
    "Netherlands": {
        "adjacent": ["Belgium"],
        "income": 50,
        "region_type": "rural"
    },
    "Waterloo": {
        "adjacent": ["Belgium", "Paris"],
        "income": 50,
        "region_type": "rural"
    },
    "Rhine": {
        "adjacent": ["Belgium", "Bavaria", "Lyon"],
        "income": 100,
        "region_type": "town"
    },
    "Bavaria": {
        "adjacent": ["Rhine", "Vienna", "Lyon"],
        "income": 100,
        "region_type": "town"
    },
    "Vienna": {
        "adjacent": ["Bavaria", "Milan"],
        "income": 200,
        "region_type": "major_city"
    },
    "Lyon": {
        "adjacent": ["Paris", "Rhine", "Bavaria", "Marseille", "Milan"],
        "income": 200,
        "region_type": "major_city"
    },
    "Milan": {
        "adjacent": ["Lyon", "Vienna", "Geneva"],
        "income": 150,
        "region_type": "city"
    },
    "Marseille": {
        "adjacent": ["Lyon", "Geneva"],
        "income": 150,
        "region_type": "city"
    },
    "Geneva": {
        "adjacent": ["Marseille", "Milan", "Bordeaux"],
        "income": 100,
        "region_type": "town"
    },
    "Brittany": {
        "adjacent": ["Paris", "Bordeaux"],
        "income": 50,
        "region_type": "rural"
    },
    "Bordeaux": {
        "adjacent": ["Brittany", "Geneva"],
        "income": 50,
        "region_type": "rural"
    }
}
```

France starting income (Paris, Waterloo, Brittany, Bordeaux, Lyon, Marseille — assuming standard setup): ~800/turn.
Coalition starting income: varies by scenario setup.

### Region Serialization

New field on Region:
- `region_type: str` (default "town")

Add to `to_dict()`, `from_dict()`.

---

## 3. Upkeep

### Formula

Per marshal, per turn:

```python
upkeep = (marshal.strength // 1000) * 5
```

A 30,000-strong army costs 150 gold/turn. A 50,000-strong army costs 250 gold/turn. A 10,000-strong army costs 50 gold/turn.

### Application

**Calculated during the income phase at end of turn** (see §12, steps 10-15). Upkeep is deducted from income to produce a net change. This means the player sees a single net result: `income - upkeep + admin_bonus = net change`.

```python
def calculate_turn_upkeep(self, nation: str = None) -> Dict:
    """Calculate total upkeep for a nation's armies."""
    nation = nation or self.player_nation
    total_upkeep = 0
    breakdown = []
    for marshal in self.marshals.values():
        if marshal.nation == nation and marshal.strength > 0:
            cost = (marshal.strength // 1000) * 5
            total_upkeep += cost
            breakdown.append({"marshal": marshal.name, "strength": marshal.strength, "upkeep": cost})
    return {"total": total_upkeep, "breakdown": breakdown}
```

### Net Income Display

Each turn shows: `"Income: 800 gold (6 regions). Upkeep: 375 gold (3 marshals). Admin bonus: +75 gold (1 unused AP). Net: +500 gold. Treasury: 2,000 gold."`

### Bankruptcy

If `gold < 0` after applying income minus upkeep:

**Grace period (2 turns):**
- Turn 1 of bankruptcy: Warning message. `"Sire, the treasury is empty! The men grow restless..."` Upkeep halved.
- Turn 2 of bankruptcy: Severe warning. `"Soldiers are looting villages to feed themselves. Desertion is rampant."` Upkeep halved.
- Turn 3+ of bankruptcy: **Desertion.** Each marshal loses 5% strength per turn. `"500 men deserted from Ney's corps overnight."`

Track bankruptcy duration on WorldState:
- `bankruptcy_turns: int` (0 = solvent, 1+ = consecutive bankrupt turns)
- Resets to 0 when gold >= 0 at end of income phase.
- A bankrupt player with gold >= 200 CAN still recruit — they're spending their way out of the hole. Gold check happens before deduction, not bankruptcy status.

### Future Hook: Bankruptcy → Authority Drop

When the authority system is implemented (Phase 8+), extended bankruptcy should reduce player authority. Concept: each turn of active bankruptcy (turns 3+, when desertion kicks in) reduces authority by 5-10 points. Thematically: "The army starves and the generals blame you." This is NOT implemented in Phase 6 — just a design note for future integration.

### Serialization

New fields on WorldState:
- `bankruptcy_turns: int` (default 0)

---

## 4. Region Stability

### Purpose

Conquered territory isn't "yours" immediately. Prevents blitz-and-benefit strategies. Makes peace treaties (Phase 8) genuinely valuable.

### Stability Score (0-100)

New field on Region: `stability: int`

| Range | Label | Income Modifier | Restrictions |
|-------|-------|-----------------|--------------|
| 0-25 | Hostile | 0% income | Can't build, can't recruit |
| 26-50 | Unrest | 25% income | Can't build, can't recruit |
| 51-75 | Settling | 75% income | Can build, can recruit at +50% cost |
| 76-100 | Stable | 100% income | Full benefits |

### Starting Stability Values

| Situation | Starting Stability |
|-----------|-------------------|
| Home region (game start) | 100 |
| Conquered + Plundered | 10 |
| Conquered + Secured | 25 |
| Ceded by peace treaty (Phase 8) | 70 |
| Reconquered own region | 60 |

### Stability Growth

Per turn, each region's stability increases:

```python
base_growth = 5  # per turn
garrison_bonus = 5 if marshal_present_in_region else 0
stability_growth = base_growth + garrison_bonus
region.stability = min(100, region.stability + stability_growth)
```

A conquered+secured region reaches "Settling" (51+) in ~6 turns without garrison, ~3 turns with. A plundered region takes ~9 turns without garrison, ~5 with.

### Stability Drop on Events

- Battle fought in region: -10 stability (war disrupts civilian life)
- Region plundered: set to 10 (see above)
- Region changes hands: stability resets based on situation

### Serialization

New field on Region:
- `stability: int` (default 100 for backward compat — existing regions are "home" regions)

---

## 5. Plunder vs Secure

### Trigger

When a marshal captures a region (moves into undefended enemy region, or wins battle and captures), the player is presented a choice:

**"Your forces have taken [Region]. How shall they behave?"**
- **Plunder:** "Let the men take their rewards." → +gold, devastation
- **Secure:** "Maintain discipline. This land is now ours." → no bonus, faster stability

### Effects

| | Plunder | Secure |
|---|---|---|
| Immediate gold | +100% of region's base income value | +0 |
| Starting stability | 10 (Hostile) | 25 (Unrest) |
| War damage | +0.35 (severe) | +0.0 (preserved) |
| Plundered flag | `plundered: True` on region (tracked for AI/flavor) | `plundered: False` |
| Buildings | All destroyed | Damaged (need repair) |
| Flavor | "Ney's troops rampage through Brussels" | "Davout posts guards at every door" |

**Plundered flag:** Captured regions that were plundered get `plundered: True` on the Region object. This flag is used by AI decision-making (see §11), flavor text, and stability calculation (plundered regions start at stability 10 vs 25 for secured). The flag persists until stability reaches 50+ (the region has "recovered"). No partisan uprising mechanic — the cost of plundering is the long stability/income recovery time and severe war damage.

**Balance comparison:** A plundered city (base 150 income) yields 150 gold immediately but the region produces near-zero income for ~9 turns (stability 10 → 51 with garrison) and has +0.35 war damage reducing income further. A secured city produces 37 gold/turn immediately (stability 25 = Unrest = 25% income, no war damage) and reaches full income in ~6 turns. Plunder is short-term gold; secure is reliable long-term value.

### Implementation

Uses the **same popup pattern as `pending_objection`** (see `objection_v2.py`). New field on WorldState: `pending_capture_choice: Optional[Dict]`. Contains `{"region": region_name, "capturer": marshal_name, "previous_controller": old_controller}`.

After capture, executor sets `world.pending_capture_choice` and returns `{"success": True, "pending_capture_choice": True, ...}`. Frontend shows plunder/secure dialog. Player responds via new endpoint `/capture_choice` with `{"choice": "plunder"}` or `{"choice": "secure"}`. Executor resumes, applies chosen effects, clears `pending_capture_choice`.

While `pending_capture_choice` is set, other commands are blocked (same as `pending_objection`). The executor checks for this at the top of `execute()`.

**Serialization:** `pending_capture_choice` added to WorldState `to_dict()`/`from_dict()` (default `None`). See §14.

**AI capture decision (by personality):**
- **Aggressive** (e.g., Blücher): Plunder — "Take what you can."
- **Cautious** (e.g., Wellington): Secure — "Discipline above all."
- **Literal** (e.g., Gneisenau): Secure — follows standard procedure.
- **Default / other**: Secure.

This uses existing `PersonalityType` enum. No new fields needed — just a lookup in the capture handler. AI capture decisions are applied directly (no popup, no blocking) — the AI processes multiple captures sequentially within its turn.

### Personality Moment (Phase 8.5 enhancement)

Marshal personality affects the default suggestion and flavor text:
- Ney suggests plunder (aggressive): "The men deserve their spoils, Sire!"
- Davout suggests secure (cautious): "Discipline, Sire. We need this city functional."
- Grouchy follows orders literally: no opinion.

For Phase 6: just the binary choice. No personality flavor yet.

---

## 6. Recruitment Rework

### Current State

`_execute_recruit()` exists. Costs 200 gold, adds 10,000 troops to a marshal. Uses Command Points. No location restriction.

### Changes

1. **Costs Admin AP** (not Command Points) — move to admin pool
2. **Fixed amount: 10,000 troops per recruit action** (unchanged from current). The penalties for recruitment are: gold cost + Admin AP cost + morale dilution. Three penalties are sufficient — do NOT scale troop amount by region type.
3. **Region-based:** Must specify a controlled region OR a marshal. If marshal specified, recruits at marshal's current location. Location must be controlled by player.
4. **Stability restriction:** Can't recruit in regions with stability < 50. At stability 51-75, recruitment costs +50% gold.
5. **Capital bonus:** Recruiting at capital costs 25% less.
6. **Morale dilution:** New troops have 40% base morale. Army morale becomes weighted average.

### Morale Dilution Formula

```python
recruit_morale = 40  # Green conscripts
new_morale = (
    (marshal.strength * marshal.morale + new_troops * recruit_morale) 
    / (marshal.strength + new_troops)
)
marshal.morale = int(new_morale)
```

Example: 20,000 veterans at 80% morale + 10,000 recruits at 40% morale → 30,000 at 67% morale.

### Cost Table

| Situation | Gold Cost |
|-----------|-----------|
| Base cost per 10,000 troops | 200 gold |
| At capital region | 150 gold (25% discount) |
| At stability 51-75 region | 300 gold (50% premium) |
| At stability < 50 region | **Blocked** |

### Updated Command Parsing

```
"recruit at Paris" → recruit 10k troops, add to nearest marshal to Paris, location = Paris
"recruit for Ney" → recruit 10k troops, add to Ney, location = Ney's current region
"recruit" → recruit at capital (default, existing behavior)
```

**Note:** "Recruit at [region]" uses the existing `find_nearest_marshal_to_region()` fallback in `_execute_recruit()`. The troops are raised at the named region but assigned to the nearest marshal. This is intentional — you don't need a marshal physically present to recruit, just a controlled region.

### AI Recruitment

Enemy AI can now recruit using same executor. AI admin phase priority #1 checks if any marshal is below 40% starting strength. If yes, recruit to that marshal's location if stable enough.

---

## 7. War Damage

### Purpose

Battles damage regional economies. Creates post-war reconstruction decisions.

### Damage Model

New field on Region: `war_damage: float` (0.0 = pristine, 0.5 = max damage)

Income modifier: `1.0 - war_damage` (so 0.5 war_damage = 50% income)

### Damage Sources

| Event | Damage Applied |
|-------|---------------|
| Battle in region (any size) | +0.10 |
| Major battle (combined 50k+ troops) | +0.20 |
| Plunder on capture | +0.25 |
| Scorched earth (future) | +0.40 |

Damage caps at 0.50 (minimum 50% income from war damage alone — stability stacks separately).

### Natural Recovery

War damage decreases by 0.02 per turn naturally. A region damaged by a single battle (0.10) recovers in 5 turns. A plundered region (0.25+) takes 12+ turns.

### Repair Action

Player can spend 1 Admin AP + 150 gold to repair a damaged region:
- Immediately reduces war_damage by 0.15
- Can be done multiple times (each costs 1 AP + 150 gold)

```
"repair Brussels" → 1 Admin AP + 150 gold, reduces war_damage by 0.15
```

### Combined Income Formula

```python
def get_effective_income(self) -> int:
    """Calculate actual income after all modifiers."""
    stability_mod = self._get_stability_modifier()  # 0.0, 0.25, 0.75, or 1.0
    damage_mod = 1.0 - self.war_damage              # 0.5 to 1.0
    return int(self.income_value * stability_mod * damage_mod)
```

### Serialization

New field on Region:
- `war_damage: float` (default 0.0)

---

## 8. Buildings

### Design

Light building system. Cities only (region_type in ["capital", "major_city", "city"]). One building slot per city, two for capitals. Buildings take multiple turns to construct.

### Building Types

| Building | Gold Cost | Admin AP | Build Time | Effect |
|----------|-----------|----------|------------|--------|
| Supply Depot | 300 | 1 | 2 turns | +50 income (flat), +10k supply capacity |
| Fortification | 400 | 1 | 3 turns | +25% defense for battles in this region, enables contested capture |
| Training Ground | 250 | 1 | 2 turns | Recruits here have 55% morale instead of 40% |
| Market | 350 | 1 | 2 turns | +25% income multiplier on base region income (after depot, before stability/damage) |

### Building Construction

```
"build supply depot at Lyon" → 1 Admin AP + 300 gold → construction begins
```

New fields on Region:
- `buildings: List[Dict]` — list of completed buildings
- `building_under_construction: Optional[Dict]` — current construction project

Construction dict: `{"type": "supply_depot", "turns_remaining": 2}`

Each turn, `turns_remaining` decrements. At 0, building moves to `buildings` list.

Only one construction at a time per region. Can't build in regions you don't control. Can't build in regions with stability < 50.

### Building Destruction

| Event | Effect |
|-------|--------|
| Region plundered | All buildings destroyed, construction cancelled |
| Region secured by conqueror | Buildings damaged (add `damaged: True`). Must repair before benefit applies. |
| Battle in region with fortification | 25% chance fortification is damaged. Major battle (50k+): always damaged. |

**Building under construction is cancelled on capture.** Resources (gold, Admin AP) spent on construction are lost. The conqueror does not inherit partial construction. Set `building_under_construction = None` when a region changes hands. This is intentional risk — building on the front line is a gamble.

Damaged buildings provide no benefit until repaired. Repair: 1 Admin AP + 150 gold.

### City Fortification + Contested Capture

When a region has a completed, undamaged Fortification building:

**Defense bonus:** All defenders in this region get +25% defense (stacks with marshal's personal fortify).

**Contested capture:** The region cannot be captured in a single turn. After winning a battle:
1. **No garrison (empty fortified city):** Occupying marshal must HOLD for 1 turn. If they leave or lose a battle, occupation resets.
2. **Garrison present (fortified + defended):** Must win the battle, THEN hold for 2 turns.

During occupation, the marshal can't take other actions (they're securing the fortress). They CAN still be attacked — if they lose, they're expelled and occupation resets.

**Movement through fortified cities:** Armies CAN move through enemy fortified regions, but take harassment attrition: lose 3-5% strength passing through. The garrison remains, the city stays enemy-controlled. This prevents gridlock at 13 regions while making fortified cities strategically costly to bypass.

### Serialization

New fields on Region:
- `buildings: list` (default [])
- `building_under_construction: dict or None` (default None)

### Income Calculation Examples (with Buildings)

**Paris (capital, 300 base income, stable, no damage):**
- No buildings: 300 * 1.0 * 1.0 = 300/turn
- With depot: (300 + 50) * 1.0 * 1.0 = 350/turn
- With market: int(300 * 1.25) * 1.0 * 1.0 = 375/turn
- With depot + market: int((300 + 50) * 1.25) * 1.0 * 1.0 = 437/turn

**Lyon (major_city, 200 base income, settling stability 60, war damage 0.10):**
- No buildings: 200 * 0.75 * 0.90 = 135/turn
- With market: int(200 * 1.25) * 0.75 * 0.90 = 168/turn
- With depot + market: int((200 + 50) * 1.25) * 0.75 * 0.90 = 211/turn

---

## 9. Supply Limits

### Purpose

Prevents deathball strategies. Forces army distribution across the map. Large armies in small regions eat themselves.

### Supply Capacity Per Region Type

| Region Type | Supply Capacity | With Supply Depot |
|-------------|----------------|-------------------|
| Capital | 50,000 | 60,000 |
| Major City | 40,000 | 50,000 |
| City | 30,000 | 40,000 |
| Town | 20,000 | 30,000 |
| Rural | 15,000 | 25,000 |

Supply capacity = total troops the region can support. If multiple marshals share a region, their combined strength is checked.

### Attrition When Over Limit

```python
total_troops_in_region = sum(m.strength for m in marshals_in_region)
excess_ratio = (total_troops_in_region - supply_capacity) / supply_capacity

if excess_ratio <= 0:
    attrition = 0
elif excess_ratio <= 0.25:
    attrition = 0.01  # 1%
elif excess_ratio <= 0.50:
    attrition = 0.03  # 3%
else:
    attrition = 0.05  # 5%

# Apply to each marshal in the region
for marshal in marshals_in_region:
    losses = int(marshal.strength * attrition)
    marshal.strength -= losses
```

Processed per turn during `_process_tactical_states()` or similar.

### Forced Retreat Overrides Supply Limits

**A retreating marshal can enter a region that is already at or over supply capacity.** Supply attrition kicks in on the next turn if the region remains over capacity. Rationale: you can't refuse a forced retreat because the destination is "full" — the troops pile in, then start starving. This prevents the pathological case where a broken army has nowhere to go because all friendly regions are at capacity.

### Supply Capacity (Computed Property)

`supply_capacity` is a **computed property** on Region, not a stored/serialized field:

```python
# region.py
SUPPLY_BY_TYPE = {
    "capital": 50000, "major_city": 40000, "city": 30000,
    "town": 20000, "rural": 15000
}

@property
def supply_capacity(self) -> int:
    base = SUPPLY_BY_TYPE.get(self.region_type, 20000)
    if any(b.get("type") == "supply_depot" and not b.get("damaged") for b in self.buildings):
        base += 10000
    return base
```

This means supply_capacity is **not serialized** — it derives from `region_type` and `buildings`, both of which are serialized.

### Depot Forward Logistics (Phase 6.2.H)

Supply depots **project** a logistics benefit to adjacent regions. If a marshal moves into a region where the destination itself or any adjacent region has a friendly undamaged supply depot, **movement attrition is halved** (0.5x multiplier applied after terrain).

Rules:
- **Does not stack.** One adjacent depot or five — same 0.5x benefit.
- **Depot must be in a region controlled by the marshal's nation** and undamaged.
- **Destination can be any controller** — enemy, neutral, friendly. That's the point: build depots in your territory to ease pushes into enemy land.
- **Does NOT affect retreat attrition** (retreats have their own 0.5x rate).
- **Does NOT affect harassment** (fortification garrison fire is separate).
- **Does NOT affect supply attrition** (overcrowding). The +10k capacity is a separate benefit.
- **Does NOT affect friendly stable territory exemption** (already 0 attrition).

```python
# executor.py — applied after terrain multiplier, before computing losses
if not is_retreat and has_depot_supply_bonus(world, destination, marshal.nation):
    rate *= 0.5  # halve march attrition
```

### Future Hook (Phase 9): Admin Generals + Army Size

Marshal "administration" stat raises personal supply efficiency — effectively increases the supply cap for regions they're in. For Phase 6, flat caps based on region type only.

**Implementation concept:** A marshal's admin stat adds a personal supply bonus to the region's base capacity when calculating *that marshal's* attrition. High-admin generals (e.g., Davout with admin 8) can field larger armies without triggering supply attrition. Low-admin generals (e.g., Ney with admin 3) struggle past the base limit.

```python
# Phase 9 concept — NOT for Phase 6
personal_supply_bonus = marshal.skills.get("administration", 4) * 2500  # 2500 per admin point
effective_capacity_for_marshal = region.supply_capacity + personal_supply_bonus
# Davout (admin 8): +20,000 personal supply — can field 50k where Ney struggles past 30k
```

This lets historically capable administrators command larger forces while making logistics-weak commanders a liability at scale.

---

## 10. Movement Attrition

### Purpose

Every march costs lives. Larger armies lose proportionally more (supply lines stretch). Creates cost to offensive maneuvers and advantages for defenders.

### Formula

```python
base_attrition = 0.01  # 1% per move
size_penalty = min(0.02, max(0, (marshal.strength - 20000) / 500000))  # 0-2% for large armies
move_attrition = base_attrition + size_penalty

losses = int(marshal.strength * move_attrition)
marshal.strength -= losses
```

A 20,000-strong army loses ~1% (200 troops) per move.
A 50,000-strong army loses ~1.6% (800 troops) per move (size penalty kicks in).
A 72,000-strong army loses ~2.04% (~1,470 troops) per move.
A 120,000+ army loses ~3% (capped) per move on plains.

**Friendly stable territory exemption:** No march attrition when moving through own regions with stability 76+ (Stable tier). This represents well-maintained supply lines and friendly population. Settling (51-75) and below still incur attrition — the region isn't secure enough for safe passage.

### Application

Applied in `_execute_move()` and `_execute_attack()` (for the movement component). Also applied during strategic order movement (MOVE_TO, PURSUE).

### Harassment Attrition (Fortified Cities)

Moving through an enemy region with a Fortification building (see §8): additional 3-5% strength loss. This is ON TOP of movement attrition.

```python
if target_region.controller != marshal.nation:
    if target_region.has_building("fortification"):
        harassment_loss = int(marshal.strength * 0.04)  # 4% average
        marshal.strength -= harassment_loss
        # Message: "Garrison at Brussels harasses Ney's column. 1,200 troops lost."
```

### Retreat Attrition

**Retreat causes half movement attrition** (0.5% base instead of 1%). Rationale: retreating troops lose some stragglers but aren't conducting a full march with supply trains. This prevents retreat-as-free-movement exploit while not destroying a fleeing army.

```python
if is_retreat:
    base_attrition = 0.005  # 0.5% per retreat move (half normal)
else:
    base_attrition = 0.01   # 1% per normal move
```

### Future Hook (Phase 6 Terrain)

Terrain type will multiply movement attrition. Mountains = 2x, Forest = 1.5x, Plains = 1x. For now, flat attrition.

---

## 11. Enemy AI Recruitment (New Priority)

### Current Enemy AI Priorities (P0-P8)

P0: Engagement check → P1: Threat response → P2: Fortify → P3: Attack opportunities → ... → P8: Default

### New: AI Admin Phase

After all military actions complete, each enemy nation runs an admin phase with its Admin AP:

```python
def execute_admin_phase(self, nation: str, world: WorldState, game_state: Dict) -> List[Dict]:
    """Execute economic actions for an enemy nation."""
    admin_ap = world.get_admin_ap(nation)
    results = []
    
    while admin_ap > 0:
        action = self._pick_admin_action(nation, world, admin_ap)
        if action is None:
            break  # Save remaining AP for income bonus
        result = self.executor.execute(action, game_state)
        if result.get("success"):
            admin_ap -= 1
            results.append(result)
        else:
            break  # Failed, stop trying
    
    # Unused AP → income bonus
    unused_bonus = admin_ap * 75
    world.nation_gold[nation] = world.nation_gold.get(nation, 0) + unused_bonus
    
    return results
```

### AI Admin Priority

```python
def _pick_admin_action(self, nation, world, admin_ap):
    # 1. Recruit for weakest marshal (if below 40% starting strength)
    weakest = self._find_weakest_marshal(nation, world)
    if weakest and weakest.strength < weakest.starting_strength * 0.4:
        if world.nation_gold.get(nation, 0) >= 200:
            return {"command": {"marshal": weakest.name, "action": "recruit"}}
    
    # 2. Build fortification at border city (if affordable)
    border_city = self._find_unfortified_border_city(nation, world)
    if border_city and world.nation_gold.get(nation, 0) >= 400:
        return {"command": {"action": "build", "target": border_city, "building": "fortification"}}
    
    # 3. Repair high-income damaged region
    damaged = self._find_damaged_region(nation, world)
    if damaged and world.nation_gold.get(nation, 0) >= 150:
        return {"command": {"action": "repair", "target": damaged}}
    
    # 4. Save AP for income bonus
    return None
```

### All Nations Use Identical Economic Rules

**Building blocks principle — no exceptions.** Every nation earns income, pays upkeep, goes bankrupt, suffers desertion, and can build/repair/recruit using the same formulas. The only difference is **starting gold**, which reflects historical economic power:

| Nation | Starting Gold | Rationale |
|--------|--------------|-----------|
| France | 600 | Dominant continental power |
| Britain | 800 | Naval/trade wealth |
| Prussia | 300 | Smaller economy |
| Austria | 500 | Large but stretched (1805 reference) |
| Russia | 400 | Vast but underdeveloped (1805 reference) |

Only France, Britain, and Prussia are relevant for the Waterloo scenario. Austria and Russia included for 1805 expansion reference.

**Future:** Phase 8 (Diplomacy) introduces British subsidies — Britain can fund allies with gold transfers, creating economic asymmetry through gameplay rather than rules exceptions.

### Nation Gold Tracking

Currently only `world.gold` exists (player only). Need per-nation gold:

```python
# world_state.py
self.nation_gold = {
    "France": 600,   # Player starting gold (replaces self.gold)
    "Britain": 800,  # Naval/trade wealth
    "Prussia": 300,  # Smaller economy
}
```

**No save migration needed** — no saves exist yet. Replace `self.gold` directly with `self.nation_gold[self.player_nation]`. Add a convenience property for readability:

```python
@property
def gold(self):
    """Convenience: player nation's gold."""
    return self.nation_gold.get(self.player_nation, 0)

@gold.setter
def gold(self, value):
    self.nation_gold[self.player_nation] = value
```

### AI Admin Scaling (Future Note)

For the Waterloo scenario (3 nations, 2-3 AI marshals each), the simple priority list above works. For the 1805 expansion (5+ nations, 5-8 marshals each), the AI admin phase will need scaling: budget allocation per-nation (don't blow all gold on one marshal), regional prioritization, and coordination between multiple AI nations. This is a Phase 9 concern — the current simple loop is correct for Phase 6.

### AI Starting Strength Tracking

`starting_strength` **already exists** on Marshal (`marshal.py:210`). Already serialized in `to_dict()` (line 887) and `from_dict()` (line 1008). No new field needed — the economy spec uses it for AI recruitment target calculation ("below 40% starting strength").

---

## 12. Turn Income Summary

### Revised Turn Flow

```
Player turn:
  1. Player issues CP + Admin AP actions (interleaved)
  2. Player ends turn

Turn resolution:
  3. Process tactical states (fortify, drill, construction timers)
  4. Process stability growth (all regions)
  5. Process war damage recovery (all regions)
  6. Process supply attrition (all regions)
  7. Process bankruptcy desertion (if applicable)

Enemy phase:
  8. Enemy military actions (existing)
  9. Enemy admin actions (NEW)

Income phase (ALL nations):
  10. Calculate income (regions × stability × war_damage modifiers)
  11. Calculate upkeep (marshal strength-based)
  12. Apply unused Admin AP bonus
  13. Apply net change to treasury
  14. Update bankruptcy counter
  15. Display summary to player
```

### Player-Facing Summary

```
═══════════════════════════════════
 TURN 4 FINANCIAL REPORT
═══════════════════════════════════
 Income:    650 gold  (5 regions)
   Paris (capital):      300
   Lyon:                 200
   Belgium (unrest):      25  ← stability 35%
   Brittany:              50
   Bordeaux:              50
   War damage penalty:   -25  ← Brussels damaged

 Upkeep:   -240 gold  (3 marshals)
   Ney (28,000):        -140
   Davout (15,000):      -75
   Grouchy (5,000):      -25

 Admin bonus: +75 gold  (1 unused AP)

 Net:      +485 gold
 Treasury: 1,985 gold
═══════════════════════════════════
```

This displays as a formatted message in the command output after end turn.

---

## 13. New Parser Commands

### Economy Commands (Admin AP)

```
"recruit at Paris"              → recruit action, location=Paris
"recruit for Ney"               → recruit action, marshal=Ney
"recruit"                       → recruit action, location=capital (existing)
"build fortification at Lyon"   → build action, building=fortification, target=Lyon
"build supply depot at Brussels" → build action, building=supply_depot, target=Brussels
"build training ground at Paris" → build action, building=training_ground, target=Paris
"repair Brussels"               → repair action, target=Brussels
```

### Free Economy Command (No AP Cost)

```
"economy"     → Display treasury, income, upkeep, net — same as end-of-turn report
"treasury"    → Same as "economy"
"finances"    → Same as "economy"
```

This is a **free action** (like status/help). Routed through executor as `_execute_economy()`. Returns the same financial summary shown at end of turn (see §12) but on demand. Add to free actions list in §1 and to `_action_costs` in `world_state.py` with cost 0.

### Mock Parser Keywords

Add to `llm_client.py` mock parser:
- "build" → build action (extract building type + target)
- "repair" → repair action (extract target)
- "recruit" already exists, just needs Admin AP routing

### Validation

Add to `VALID_ACTIONS` in `validation.py`:
- `build` — Build a building in a city you control
- `repair` — Repair war damage in a region you control

`recruit` already exists.

---

## 14. Serialization Fields Summary

> **No save migration needed.** No save files exist yet. All defaults in `from_dict()` are for forward-compat (future saves loading into newer code), not backward-compat with old saves.

### Region
| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `region_type` | str | "town" | capital/major_city/city/town/rural |
| `stability` | int | 100 | 0-100, home regions start at 100 |
| `war_damage` | float | 0.0 | 0.0-0.5 |
| `buildings` | list | [] | List of building dicts |
| `building_under_construction` | dict/None | None | Current construction |
| `plundered` | bool | False | Set on plunder, clears when stability >= 50 |
| `supply_capacity` | int | **not serialized** | Computed property from region_type + buildings (see §9) |

### WorldState
| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `admin_actions_remaining` | int | 2 | Current admin AP |
| `max_admin_actions` | int | 2 | Max admin AP per turn |
| `nation_gold` | dict | {"France": 600} | Per-nation treasury (see §11 starting gold table) |
| `bankruptcy_turns` | int | 0 | Consecutive bankrupt turns |
| `pending_capture_choice` | dict/None | None | Plunder/secure choice pending (see §5) |

### Marshal
| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `starting_strength` | int | strength | **Already exists** (marshal.py:210). No new field needed. Economy spec uses it for AI recruitment target calculation. |

---

## 15. Implementation Order

Recommended build sequence (each step is testable independently):

1. **Region types + differentiated income** — Update REGIONS_DATA, add region_type field, update calculate_turn_income. Tests: income by region type.
2. **Per-nation gold** — Replace world.gold with nation_gold dict, add convenience property. Tests: multi-nation gold tracking.
3. **Upkeep** — Calculate and apply per turn. Tests: upkeep formula, net income.
4. **Bankruptcy** — Grace period, desertion. Tests: bankruptcy progression.
5. **Admin AP pool** — New fields, action routing, unused AP bonus. Tests: admin vs command pool.
6. **Stability** — New field, growth per turn, income modifier. Tests: stability progression, income modification.
7. **War damage** — New field, damage on battle, recovery, income modifier. Tests: damage application and recovery.
8. **Morale dilution** — Update _execute_recruit() with weighted average. Tests: morale before/after recruit.
9. **Plunder vs Secure** — Capture choice, effects on stability/buildings/gold. Tests: both paths.
10. **Buildings** — Build action, construction timer, effects. Tests: build/complete/destroy cycle.
11. **Supply limits** — Per-region cap, attrition. Tests: over-limit attrition.
12. **Movement attrition** — Losses on move. Tests: strength after move.
13. **City fortification + contested capture** — Occupation timer, harassment. Tests: capture flow.
14. **Recruitment location restrictions** — Stability gate, capital discount. Tests: blocked/discounted recruit.
15. **Enemy AI admin phase** — AI recruit/build/repair. Tests: AI economic decisions.
16. **Parser additions + display names** — build, repair, economy commands. Add `_ACTION_DISPLAY_NAMES` entries for "build", "repair", "economy". Tests: parsing.
17. **Turn summary display** — Formatted financial report. Tests: summary format.
18. **Update MODDING_FORMAT.md** — Document new region fields (region_type, stability, war_damage, buildings), nation_gold, admin AP. Update example mod JSON.

Each step: implement → test → serialize → commit. Sonnet for all steps. Opus review after step 13 and after step 18.

---

## 16. Deferred / Future Design

| Feature | Deferred To | Notes |
|---------|-------------|-------|
| Cohesion (army quality stat) | FUTURE_DESIGN.md | Morale dilution covers recruitment penalty for now. Add when playtesting shows veteran/green armies feel identical. Simple addition: new field on Marshal, modifier in get_attack_modifier/get_defense_modifier. **Note:** Morale dilution is the Phase 6 abstraction for recruitment skill dilution. Green troops (40% morale) mixed into veteran armies (80%+ morale) creates a measurable quality drop that affects combat outcomes through morale-based retreat thresholds (25% = forced retreat) and morale recovery rates. If playtesting shows this doesn't sufficiently differentiate veteran vs green armies, cohesion adds a direct combat modifier layer. |
| Admin general supply bonus | Phase 9 | Marshal admin stat adds personal supply capacity. Davout fields 50k where Ney struggles past 30k. See §9. |
| Dismiss/downsize armies | Phase 10 | For now, attrition naturally thins armies. |
| Loans with interest | Phase 8/11 | Arrives via diplomacy (subsidies) and vassals (tribute). |
| Marshal admin stat raising supply cap | Phase 9 | Advisors modify admin effectiveness. |
| Economic advisor commenting on decisions | Phase 9 | Advisor personality reacts to spending. |
| Manpower pools (infantry/cavalry/artillery) | 1805 expansion | Single troop type for Waterloo scale. |
| Scorched earth | Post-EA | Defender destroys before retreating. |
| Plunder/secure personality flavor | Phase 8.5 | Marshal suggests based on personality. |
| Partisan uprising mechanic | Post-EA | Replaced by simpler plundered flag. If playtesting needs more consequence for plunder, re-add as % chance region flips. |
| Bankruptcy → authority drop | Phase 8 | Extended bankruptcy (turn 3+) reduces authority 5-10/turn. See §3 future hook. |
| AI admin budget scaling | Phase 9 / 1805 | Multi-nation budget allocation, regional priority, coordination. Simple loop sufficient for Waterloo. See §11. |
| Recruitment from specific manpower pools | 1805 expansion | Regional manpower where specific regions produce troops. |

---

## 17. Balance Notes (Waterloo Testbed)

### Starting Conditions (approximate)

| Nation | Regions | Income/Turn | Starting Gold | Marshals | Total Troops | Upkeep/Turn | Net/Turn |
|--------|---------|-------------|---------------|----------|--------------|-------------|----------|
| France | ~6 | ~800 | 600 | 3 (Ney, Davout, Grouchy) | ~75,000 | ~375 | ~+425 |
| Britain | ~4 | ~400 | 800 | 2 (Wellington, Uxbridge) | ~45,000 | ~225 | ~+175 |
| Prussia | ~3 | ~300 | 300 | 2 (Blucher, Gneisenau) | ~40,000 | ~200 | ~+100 |

France has the highest income (Paris + Lyon) and a comfortable surplus (~+425/turn). Britain starts gold-rich but has lower income. Prussia is resource-constrained. All nations have positive net income, meaning the economy rewards efficient play rather than punishing existence. Pressure comes from wanting to recruit (200 gold), build (250-400 gold), and repair — not from passive upkeep drain.

### Expected Game Length

10-15 turns. Economy should create meaningful decisions by turn 3-4 (first recruitment decision) and pressure by turn 7-8 (treasury running low if not expanding).

### Key Balance Levers

- Region income values (easy to tune)
- Upkeep rate (5 gold per 1000 troops — adjustable)
- Recruitment cost (200 gold base — adjustable)
- Admin AP count (2 — adjustable per nation)
- Unused AP bonus (75 gold — adjustable)
- Stability growth rate (5-10/turn — adjustable)
