# Fog of War Specification

> **Phase 6 — Fog of War System**
> **Status:** REVIEWED — Ready for implementation (Sessions 33-36)
> **Author:** Mitch + Claude (Opus), Session 31c
> **Reviewed:** Session 32b (Opus) — fresh-eyes review, all design decisions resolved
> **Depends on:** Terrain (6.1), Economy (6.2), Scout action (existing), Buildings (6.2.E)
> **Feeds into:** V2b Objection Triggers (Phase 7), Campaign Log (6.5), Gazette (8.5), Map Renderer (6.5)

---

## 1. Core Philosophy

Napoleonic warfare was defined by uncertainty. Commanders made decisions based on dispatches that were hours or days old. The fog of war system transforms the game from an optimization puzzle (perfect information → calculate best move) into a personality negotiation under uncertainty (incomplete information → trust your marshals or gamble).

**Design principles:**
- Intel never fully vanishes — it degrades from precise to vague to stale
- All commands into fog are allowed — armies marched into the unknown constantly
- Fog creates new objection triggers that are dramatically richer than visible-but-risky situations
- The system scales naturally: adjacency covers a fixed radius, not a percentage of the map
- AI is omniscient on 19 regions (too small for AI fog to matter), revisit at 80+

---

## 2. Visibility Levels

Five tiers of intel, each with defined information access:

| Level | Source | Duration | What You See |
|-------|--------|----------|-------------|
| **FULL** | Own region w/ army / scouted / post-battle | **Ephemeral** (marshal present), 2 turns (scouted/battle), PARTIAL (own w/o army) | Commander names, exact troop counts, morale, stance, fortification, buildings, stability, terrain |
| **PARTIAL** | Adjacent to your army / watchtower | Refreshes each turn while adjacent | Commander names, strength band, terrain. No morale/stance/fortification/buildings |
| **STALE** | Formerly FULL, 3-4 turns old | Turns 3-4 after last scout | Commander names (may have moved), strength band (degraded from exact), terrain. Marked "[3 turns ago]" |
| **LAST_KNOWN** | Formerly FULL/PARTIAL, 5+ turns old | Persists indefinitely | "Last seen: Wellington, large force, Waterloo (7 turns ago)." Position likely wrong. |
| **UNKNOWN** | Never scouted, no adjacency | Until scouted or entered | Region exists on map. Controller shown (political knowledge is public). No military intel. |

### 2.1 Strength Bands (for PARTIAL and STALE)

| Band | Range | Display |
|------|-------|---------|
| Screening force | < 5,000 | "a screening force" |
| Small force | 5,000 – 14,999 | "a small force" |
| Substantial army | 15,000 – 39,999 | "a substantial army" |
| Large army | 40,000 – 69,999 | "a large army" |
| Massive army | 70,000+ | "a massive army" |

Combined forces in the same region show aggregate band: "Wellington and Blücher command a massive combined force."

### 2.2 Intel Degradation Timeline

```
Turn 0: Scout Waterloo → FULL (exact: "Wellington: 42,300 troops, defensive stance, fortified")
Turn 1: Still FULL (fresh intel)
Turn 2: Still FULL (last fresh turn)
Turn 3: → STALE ("Wellington: a substantial army at Waterloo [3 turns ago]")
Turn 4: → STALE (still usable, increasingly risky)
Turn 5: → LAST_KNOWN ("Wellington: last seen at Waterloo, 5 turns ago")
Turn 10: → LAST_KNOWN (still shown, but essentially useless — "10 turns ago")
```

### 2.3 Own Region Visibility Rules

- Regions controlled by the player: Always FULL economic data (income, stability, buildings, war damage)
- Military intel in own regions: FULL if a friendly army is present or adjacent. PARTIAL if no army present or adjacent (local administrators report enemy presence as name + strength band, but not detailed military intel)
- This prevents "enemy sneaks through your entire empire unnoticed" while keeping fog meaningful on flanks
- **Occupied own region edge case:** If an enemy is occupying your region (contested capture mechanic), administrators are under siege. They still report the occupier's presence but the strength band may be less precise — treat as standard PARTIAL (name + band) rather than upgraded intel. The siege situation doesn't grant better military intelligence.

---

## 3. Intel Data Model

### 3.1 Per-Region Intel Record

```python
class RegionIntel:
    """Tracks what the player knows about a single region."""
    region_name: str
    visibility: str  # "full", "partial", "stale", "last_known", "unknown"
    
    # Military intel (populated at PARTIAL or above)
    known_marshals: list  # [{"name": "Wellington", "nation": "Britain", ...}]
    strength_band: str    # "small_force", "substantial_army", etc. (PARTIAL/STALE)
    exact_strength: dict  # {"Wellington": 42300} (FULL only)
    morale: dict          # {"Wellington": 65} (FULL only)
    stance: dict          # {"Wellington": "defensive"} (FULL only)
    
    # Economic intel (own regions: always. enemy: FULL only)
    economic_intel: dict  # stability, buildings, war_damage (FULL only for enemy)
    
    # Timestamps
    last_scouted_turn: int   # Turn when last at FULL visibility
    last_updated_turn: int   # Turn when any update occurred
    intel_source: str        # "scout", "adjacent", "battle", "own_territory", "watchtower"
```

### 3.2 Intel Store on WorldState

```python
class WorldState:
    # New field
    intel: dict  # {region_name: RegionIntel} — player's knowledge of each region
```

### 3.3 Visibility Calculation (per turn)

Recalculate visibility at:
1. **Game initialization** — so turn 1 starts with correct visibility (player regions FULL, rest UNKNOWN)
2. **During `_advance_turn_internal()`** — at the END, after all processing
3. **After each player move** — so destination and adjacents are visible immediately

```
Pre-pass: Ephemeral marshal_present downgrade
  - Any region FULL from marshal_present where marshal has left:
    - If scouted/battled within 2 turns → fall back to scout FULL (persistent)
    - Otherwise → downgrade to PARTIAL (main loop may re-upgrade)

For each region:
  0. Marshal present → FULL (ephemeral — only while standing there)
  1. Own region → FULL economic always; FULL military if army present, else PARTIAL
  2. Adjacent to a friendly army → PARTIAL (refresh each turn)
  3. Adjacent to a watchtower in own region → PARTIAL (refresh each turn)
  4. Has FULL intel from scouting/battle → check age:
     - Age 0-2 turns → FULL (persistent)
     - Age 3-4 turns → STALE (degrade exact_strength to band)
     - Age 5+ turns → LAST_KNOWN
  5. Previously PARTIAL but no longer adjacent → starts aging from last_updated_turn
  6. Never had any intel → UNKNOWN
```

Priority: if multiple sources apply, use the best visibility level.

**Own marshal positions are always known.** The player always sees their own marshals regardless of fog — broken, retreating, behind enemy lines. Fog applies to enemy marshals only.

### 3.4 Serialization

RegionIntel must serialize to dict / deserialize from dict (standard pattern). Add to SAVE_FORMAT_REFERENCE.md. Old saves without intel field default to UNKNOWN for all regions (backward compat).

---

## 4. Information Filtering

### 4.1 Status Command — Berthier's Intelligence Report

Currently shows all marshals and regions. With fog, the status command becomes an intelligence briefing — the reduced information feels like a feature of the game's voice rather than something missing:

```
=== BERTHIER'S INTELLIGENCE REPORT ===

YOUR FORCES:
  Ney (Quatre Bras): 25,000 troops, morale 72, aggressive stance
  Davout (Ligny): 30,000 troops, morale 80, defensive stance

CONFIRMED (scouted this turn):
  Wellington: 42,300 troops at Waterloo, defensive stance, 71% morale

RECENT REPORTS (2 turns ago):
  Blücher: a substantial army near Wavre

LAST KNOWN:
  Hill: last seen near Hal, 6 turns ago

NO INTELLIGENCE:
  Antwerp, Ghent, Liège — no recent reports
```

### 4.2 Enemy Phase Display

Currently shows all enemy actions. With fog, filter by visibility:

- Actions in FULL regions: Show full action display (as now)
- Actions in STALE/LAST_KNOWN/UNKNOWN regions: Not shown
- Exception: If an enemy moves INTO a region you can see, you see them arrive but not where they came from ("Wellington's forces appear at Brussels")

**Polish tier (not in initial implementation):** A middle tier for PARTIAL regions — "Reports indicate movement near Waterloo" — showing something happened without specifics. Creates the Napoleonic "couriers arriving with fragments" feel. Prevents enemy phase from feeling empty on early turns. Implement after core fog is stable.

### 4.3 Scout Action Enhancement

The existing scout action becomes much more valuable. Currently it reveals everything — that stays the same, but now it's the ONLY way to get FULL intel on non-adjacent enemy regions.

Scout mechanics stay the same (range 2, Davout +1 = range 3, costs 1 AP, reveals region fully), but **scout results must now persist to the intel store.** Currently `_execute_scout()` returns intel ephemerally in the API response without storing it. Phase 6 adds `update_intel_from_scout(region, turn)` calls to persist FULL visibility.

**Scout range and intel:** Only the targeted region gets FULL. Intermediate regions are unaffected. The scouting marshal's army position still provides PARTIAL on adjacent regions as normal (army adjacency), but the scout action itself only grants FULL on its target.

### 4.4 Battle Reveals

Fighting in a region immediately grants FULL visibility of that region. This includes all enemy marshals present, exact strengths, morale, stance. The intel timestamp resets — the battle IS your scouting.

After the battle, normal decay applies (2 turns fresh, then stale, etc.).

---

## 5. Command Interactions

### 5.0 Mechanics vs Display Principle

**"Fog filters information, not mechanics."** Game mechanics (sally ratios, combat damage, pathfinding costs, contact interrupts) use real world data — the executor is deterministic (Golden Rule #6). Fog only filters what the player **sees** in messages and UI. The simulation is accurate; the player's view is filtered.

Exceptions where fog affects mechanics (not just display):
- **PURSUE pathfinding** uses last-known location from intel store (marshal genuinely doesn't know where the target is)
- **Cautious pathfinding** only avoids visible enemies (marshal can't route around forces they don't know about)

Everything else — combat resolution, sally ratio checks, contact interrupts when physically entering a region — uses real data.

### 5.1 Movement and Attack

| Command | Into Fog? | Behavior |
|---------|-----------|----------|
| MOVE | Yes | Move to region. If destination fogged (below PARTIAL), marshal walks in blind and discovers enemies on arrival ("ENEMY FORCES DISCOVERED!"). If destination visible, blocked with "use ATTACK" prompt. |
| ATTACK | Yes | Attack into region. Combat resolves normally — you learn enemy strength the hard way. |
| MOVE_TO (strategic) | Yes | Location-based. Pathfinding works regardless of fog. Literal marshals reroute around mid-path enemies but HALT at destination if enemy holds it (interrupt: "destination blocked, awaiting orders"). |
| HOLD | N/A | Hold current position. No fog interaction. |
| SUPPORT | Needs target | Target marshal must be at known or stale location. Fails if unknown. |
| PURSUE (strategic) | Needs target | Target must be at known or stale location. Heads toward last known position. If target has moved, marshal arrives at empty region → "Target not found. Awaiting orders." interrupt. |
| SCOUT | Into partial/unknown | Reveals target region to FULL. Existing mechanics unchanged. |

**Transit intel:** When an army passes through a region without stopping (cavalry 2-tile moves, strategic multi-step movement), the transit region receives PARTIAL visibility with an enemy snapshot (names + strength band). This applies to: direct cavalry moves (intermediate region), cavalry charges (middle region), and all strategic movement handlers (MOVE_TO, PURSUE, SUPPORT) where cavalry covers 2+ regions per turn. Only the final destination gets FULL from marshal presence; transit regions get PARTIAL. Player marshals only — AI is omniscient. The `refresh()` "only upgrade" rule prevents transit PARTIAL from downgrading existing FULL intel.

**Cavalry 2-range and fog (researched Session 34B-prep):** Cavalry moves 2 regions per turn (infantry: 1). The intermediate-region enemy check uses omniscient data (`get_enemies_in_region`), meaning cavalry "senses" hidden enemies in regions they pass through. This is **accepted for Phase 6** — the cavalry physically passes through the region, so encountering forces there is a physical constraint, not an intelligence one. The contact interrupt handles it gracefully. Auto-charge (reckless 4+) also scans at range 2, but is omniscient by design (spec §9.2). Sally from HOLD is adjacent-only (no cavalry extension). **TODO for 1805:** fog-aware intermediate checks with surprise encounter interrupt at 80+ regions.

### 5.2 PURSUE into Stale Intel

PURSUE reads the target's location from the **intel store** (last known position), NOT from the raw marshal data. This is the core fog change: `world.get_marshal(target).location` → `intel.get_last_known_location(target)`.

When PURSUE target is at a STALE or LAST_KNOWN location:
- Marshal heads toward last known position
- If target is still there → engagement as normal
- If target has moved → marshal arrives, finds empty region. Two outcomes:

**No enemies in region or adjacent:** Order auto-cancels. Message: "[Marshal] arrives at [region] but finds no sign of [target]. Last intelligence was [X] turns old. Awaiting orders, Sire." Player issues new orders on their turn. The marshal now has FULL on current region + PARTIAL on adjacent — fresh intel for the player's next decision.

**Enemies detected adjacent (via PARTIAL from arrival):** PURSUE continues toward the target's new visible position. The existing personality-based contact vectors handle the encounter — aggressive marshals push in, cautious marshals report and may scout first, literal marshals continue as ordered. No new interrupt type needed; the existing strategic contact interrupt system handles this.

This creates a natural "fog chase" mechanic that's historically perfect — Napoleon's entire Waterloo campaign involved chasing armies whose positions were uncertain. The arrival itself is the scouting — adjacency reveals nearby enemies.

### 5.3 SUPPORT into Fog

SUPPORT targets a friendly marshal. Since you always know where your own marshals are, SUPPORT always works. The fog applies to enemies in the destination region — the supporting marshal might arrive to find a much larger force than expected.

**Note:** SUPPORT's "ally safety" check in `strategic.py` scans adjacent regions for enemies. With fog, this scan must be visibility-aware — only report enemies the player can see. If enemies are hidden in fog, SUPPORT cannot assess safety.

---

## 6. Objection System Integration (V2b — Phase 7)

> **NOTE:** These triggers are DOCUMENTED HERE for design completeness but NOT IMPLEMENTED in Phase 6. They require V2b (Phase 7). Add TODO markers at wiring points.

### 6.1 New Fog-of-War Objection Triggers

| Situation | Cautious (Davout) | Aggressive (Ney) | Literal (Grouchy) |
|-----------|-------------------|-------------------|--------------------|
| Attack into UNKNOWN region | MODERATE → STRONG | No concern | Follows orders |
| Attack on STALE intel (3+ turns) | MODERATE | MILD at most | Follows orders |
| Refuse to attack when scout shows weakness | No concern | MODERATE → STRONG | No concern |
| PURSUE target with no intel | STRONG | MILD | Depends on order clarity |

### 6.2 Vindication Scenarios

The vindication payoffs are particularly strong with fog because the uncertainty is genuine — neither the player nor the marshal knows what's in the fog. When the cautious marshal is proven right about a blind attack, it feels earned.

- Cautious objects to attack into fog → you insist → find 60k troops, get crushed → **marshal vindicated** (trust boost, "I told you so" moment)
- Aggressive wants to attack into fog → you refuse → scout reveals lightly defended region → **marshal vindicated** (missed opportunity)
- These are dramatically richer than current triggers because they involve genuine uncertainty rather than visible-but-risky situations

### 6.3 Existing Davout PURSUE Fix

Currently in `disobedience.py`, Davout objects to PURSUE with bad odds against ANY enemy regardless of distance. With fog:
- **If target is FULL visibility:** Object as now (he can see the odds are bad)
- **If target is PARTIAL:** Object based on strength band comparison only
- **If target is STALE/LAST_KNOWN/UNKNOWN:** Cannot object on odds (doesn't know them). May object on staleness instead ("Three-day-old intelligence, Sire.")

TODO marker at `disobedience.py` PURSUE section (already exists, reference this spec).

---

## 7. Watchtower Building

### 7.1 Specification

| Property | Value |
|----------|-------|
| **Name** | Watchtower |
| **Cost** | 250 gold |
| **Build time** | 2 turns |
| **Effect** | Provides permanent PARTIAL visibility on all adjacent regions |
| **Scout synergy** | Scouting a watchtower-visible region: FULL expires after turn 3 instead of turn 2 (one extra turn of freshness) |
| **Destruction** | Damaged by battle in region or plunder (same as other buildings). If under construction when damaged, destroyed (reverts to "none" — consistent with `building_under_construction = None` pattern) |
| **Repair** | Same as other buildings (existing repair command) |
| **AI builds** | On border regions, priority between depot (P3) and fortification (P4) in admin chain |

### 7.2 Dedicated Watchtower Slot

Watchtowers do NOT use the building slot system. They are separate — a dedicated field on Region:

```python
# On Region model
watchtower: str  # "none", "under_construction", "active", "damaged"
watchtower_turns_remaining: int  # countdown during construction/repair
```

Every region type (rural, town, city, capital) can have exactly one watchtower regardless of building slots. This is thematically correct — watchtowers are fortified hilltop posts, not urban infrastructure. They don't compete with markets, depots, or fortifications for slots.

The UI shows watchtower status alongside other region info: "Watchtower: active", "Watchtower: damaged", or nothing if none built.

### 7.3 Strategic Value

- On 19 regions: 3-4 watchtowers on border regions can cover most of the map via adjacency. Fog is thin but watchtowers still cost gold and build time. Acceptable — the design scales correctly even if less impactful at small scale.
- On 80+ regions: Watchtower networks become essential infrastructure. Building a "picket line" along your frontier is a real strategic investment. You can't watchtower the whole border, so you choose where to invest.
- Creates build priority tension: fortify the border (fortification) or watch it (watchtower)? Both cost gold and AP.

### 7.4 Watchtower + Scout Synergy

If you scout a region already visible via watchtower:
- You get FULL intel (exact counts, morale, stance) — the watchtower only gives PARTIAL
- The FULL intel lasts one extra turn — expires after turn 3 instead of turn 2 (watchtower maintains the observation post, keeping intel fresher)
- This rewards investing in BOTH passive and active scouting

---

## 8. Economy Interaction

| Data Type | Own Region | Enemy FULL | Enemy PARTIAL+ | Enemy UNKNOWN |
|-----------|-----------|------------|-----------------|---------------|
| Controller | Always | Always | Always | Always (political knowledge is public) |
| Terrain | Always | Always | Always | Always (geography is known) |
| Stability | Always | Yes | No | No |
| War damage | Always | Yes | No | No |
| Buildings | Always | Yes | No | No |
| Income | Always | Yes | No | No |
| Troop strength | Always | Exact | Band | Hidden |
| Morale | Always | Yes | No | No |
| Stance | Always | Yes | No | No |

---

## 9. AI Behavior

### 9.1 Current Phase (13 Regions)

**AI is omniscient.** The enemy AI sees all player positions, strengths, and movements with perfect information. This is intentional:
- 19 regions is too small for AI fog to create meaningful decisions
- AI already struggles with decision-making; information constraints would make it worse
- France historically had the best intelligence network — asymmetry is thematically justified
- The Building Blocks principle (AI uses same systems as player) is preserved for ACTIONS, not for INFORMATION

### 9.2 Reckless Cavalry and Fog

**Reckless cavalry auto-charge ignores fog.** The `_process_reckless_cavalry_turn_start()` function remains omniscient — reckless cavalry finds and charges enemies regardless of visibility. This is intentional:
- Reckless cavalry IS reckless — they ride out and find trouble. That's the entire mechanic.
- Historically perfect — Ney's cavalry famously charged without orders or intel at Waterloo.
- The resulting battle grants FULL intel via battle reveal. The recklessness becomes unintentional scouting — the player gets punished (uncontrolled charge) but also learns enemy positions.
- Implementation: zero fog changes needed in auto-charge path. The battle calls `update_intel_from_battle()` to persist the reveal.

### 9.3 Cautious Pathfinding and Fog

`strategic.py:_get_enemy_occupied_regions()` scans all regions for enemies to route cautious marshals around them. **With fog, cautious marshals can only avoid VISIBLE enemies** (PARTIAL+ visibility). If an enemy is in a fogged region, the cautious marshal doesn't know to avoid it and may walk into an encounter.

This is correct behavior — cautious marshals get surprised when intel is bad. The existing contact interrupt system handles the surprise: marshal hits hidden enemy → blocked path interrupt fires → player gets "attack / go around / hold / cancel" options.

### 9.4 Cannon Fire and Fog

Cannon fire interrupts only trigger when a French marshal is involved in a battle. Since the player already knows about every battle involving their marshals, cannon fire from a fogged region cannot happen in the current design. Deferred to post-EA when multi-nation conflicts (e.g., Prussia vs Austria without French involvement) could produce battles the player doesn't know about.

### 9.5 Future (80+ Regions — EA 1805)

At scale, omniscient AI feels unfair. Design options for later:
- AI gets fog but with bonuses (wider adjacency range, faster intel updates)
- AI fog is "softer" — PARTIAL everywhere instead of UNKNOWN
- Nation-specific intelligence quality (Britain best due to spy networks, Russia worst in distant theaters)

> **Deferred to FUTURE_DESIGN.md.** Do not implement AI fog in Phase 6.

---

## 10. Event Log Integration

New event types for the event log system (Session 30):

| Event Type | Data | When Logged |
|------------|------|-------------|
| `intel_updated` | region, new_visibility, source (scout/adjacent/battle/watchtower) | When visibility changes for a region |
| `intel_decayed` | region, old_visibility, new_visibility | When intel degrades (full→stale, stale→last_known) |
| `target_not_found` | marshal, target, region, intel_age | When PURSUE arrives at empty region (auto-cancels order, message: "[Marshal] arrives at [region] but finds no sign of [target]. Last intelligence was [X] turns old.") |

`target_not_found` is NOT a separate interrupt type — it reuses the PURSUE auto-cancel flow. The event is logged for Campaign Log (6.5) and Gazette (8.5). The `intel_age` field is `current_turn - last_updated_turn` from the intel store.

These feed into Phase 6.5 Campaign Log and Phase 8.5 Gazette ("Reports from the front grow stale — Wellington's position is uncertain").

---

## 11. Godot UI Implications (Phase 6 Backend + Phase 6.5 Frontend)

### 11.1 Phase 6 (Backend Only)

No Godot changes in Phase 6. All fog logic is backend — the API responses are filtered based on visibility BEFORE reaching Godot. Godot receives pre-filtered data and displays it as-is.

This means:
- `/command` response already filters marshal lists by visibility
- `/status` (or status command) returns only visible intel
- End-turn tactical events are filtered by visibility
- Enemy phase actions are filtered by visibility

### 11.2 Map Visualization (Implemented — Session 38)

Backend sends `visibility_status` per region. Godot `map.gd` renders fog:
- FULL regions: Normal rendering, full detail on hover (**DONE**)
- PARTIAL regions: Slightly dimmed, hover shows limited info + "Intel: Partial" (**DONE**)
- STALE regions: Greyed out, hover shows timestamped old info + "Intel: Stale" (**DONE**)
- LAST_KNOWN regions: Dark, hover shows "Last known (outdated)" (**DONE**)
- UNKNOWN regions: Dark/fog overlay, hover shows "No intelligence" (**DONE**)
- Fogged enemies (PARTIAL/STALE): Dimmed silhouette icons with "?" + strength band tooltip (**DONE**)
- Watchtower icon on regions with watchtower building (deferred to EU4 map)
- Scout action animated reveal (nice-to-have, deferred to EU4 map)

---

## 12. Implementation Plan

> **Canonical plan is in `docs/FOG_IMPLEMENTATION_PLAN.md`.** This section is a summary only. Session 32 was the design review (this spec + the plan). Implementation is Sessions 33-36 with 34 split into 34A/34B.

| Session | Scope | Tests |
|---------|-------|-------|
| **33** | Intel data layer: RegionIntel model, visibility calculation, decay, serialization, game init | ~45 |
| **34A** | Intel report module, status command rewrite, `get_filtered_game_state_summary()`, scout persistence, battle reveal wiring | ~30 |
| **34B** | PURSUE fog validation, SUPPORT visibility, cautious pathfinding, enemy phase filtering, tactical/strategic report filtering, event log types | ~25 |
| **35** | Watchtower building: dedicated field, construction, visibility, scout synergy, AI building, repair, damage | ~30 |
| **36** | Edge cases, Godot smoke test, Davout PURSUE fix, V2b TODO markers, doc updates | ~20 |
| **Review** | Opus code review gate before Manpower/Artillery | 0 |

See `FOG_IMPLEMENTATION_PLAN.md` for full checklists, ordering dependencies, and risk assessment.

---

## 13. Testing Strategy

| Category | Examples | Count |
|----------|----------|-------|
| Visibility calculation | Own region = FULL, adjacent = PARTIAL, nothing = UNKNOWN | ~15 |
| Intel decay | Fresh → stale → last_known, correct turn thresholds | ~10 |
| Strength bands | Edge cases at band boundaries, combined forces | ~8 |
| Status filtering | Hidden enemies don't appear, stale shows timestamp | ~10 |
| Scout persistence | Scout updates intel store, persists across turns | ~8 |
| Battle reveals | Combat grants FULL visibility, resets timer | ~5 |
| PURSUE fog | Known target works, stale target → may find empty, unknown fails | ~10 |
| Watchtower | Adjacent visibility, scout synergy, destruction | ~10 |
| Response filtering | Enemy phase filtered, tactical events filtered | ~10 |
| Serialization | Round-trip, backward compat, old saves | ~5 |
| Event log | intel_updated, intel_decayed, target_not_found | ~6 |
| Edge cases | Broken marshal, retreat into fog, auto-charge | ~8 |
| **Total estimated** | | **~105-125** |

---

## 14. Files Modified

| File | Changes |
|------|---------|
| `backend/models/intel.py` | **NEW** — RegionIntel class |
| `backend/models/world_state.py` | Add intel dict, calculate_visibility(), decay_intel() |
| `backend/models/region.py` | Add watchtower field (dedicated slot, separate from buildings) |
| `backend/intel_report.py` | **NEW** — Berthier Intelligence Report (fog-filtered status view) |
| `backend/commands/executor.py` | Wire scout → intel update, battle → intel update, watchtower build/repair |
| `backend/commands/strategic.py` | PURSUE validation against visibility, cautious pathfinding fog-aware, SUPPORT safety fog-aware |
| `backend/commands/disobedience.py` | Davout PURSUE: check visibility before odds objection |
| `backend/game_logic/combat.py` | Return intel update with battle result |
| `backend/game_logic/turn_manager.py` | Call calculate_visibility() + decay_intel() each turn |
| `backend/main.py` | Filter API responses by visibility |
| `backend/ai/enemy_ai.py` | Watchtower building logic (AI remains omniscient) |
| `backend/save_manager.py` | Intel serialization (automatic via WorldState.to_dict) |
| `tests/test_fog_of_war.py` | **NEW** — comprehensive test suite |
| `tests/test_watchtower.py` | **NEW** — watchtower building tests |

### Docs Updated

| Doc | Changes |
|-----|---------|
| `CLAUDE.md` | Current Phase updated, fog of war in remaining items |
| `STATUS.md` | Session entries, test counts |
| `ROADMAP.md` | Fog of War marked COMPLETE, watchtower noted |
| `SYSTEMS_REFERENCE.md` | New fog of war section |
| `TUTORIAL_SCRIPT.md` | Fog of war teaching moments |
| `FUTURE_DESIGN.md` | Fog sketches → "implemented", AI fog notes for 80+ |
| `SAVE_FORMAT_REFERENCE.md` | RegionIntel serialization format |
| `ADDING_CONTENT.md` | If building types section exists, add watchtower |
| `OBJECTION_V2.md` | Note fog-of-war triggers as V2b planned items |

---

## 15. Deferred / Out of Scope

| Item | Reason | When |
|------|--------|------|
| AI fog of war | 19 regions too small, AI too fragile | EA 1805 (80+ regions) |
| V2b objection triggers | Requires V2b system (Phase 7) | Phase 7 |
| Spy network (passive intel) | Complexity, no existing system to hook into | Phase 8.5 (Events) or Post-EA |
| Captured dispatches | Requires Events system | Phase 8.5 |
| Allied intel sharing | Requires Coalition/Diplomacy systems | Phase 8+ |
| Godot map fog rendering | Requires Map Renderer | Phase 6.5 |
| Fog-aware Campaign Briefing | Requires Campaign Briefing | Phase 6.5 |

---

## 16. Open Questions (Resolve Before Implementation)

1. **~~Should adjacent visibility refresh if the enemy moves away?~~** **RESOLVED:** Losing adjacency starts the STALE decay clock from the last turn you had adjacency. Adjacency refreshes PARTIAL each turn while maintained.

2. **~~Watchtower in enemy territory after capture?~~** **RESOLVED:** Yes, like other buildings. Captured watchtower gives the new controller the adjacent visibility.

3. **~~Multiple visibility sources — does watchtower + army adjacency stack?~~** **RESOLVED:** No stacking needed. Both provide PARTIAL. The benefit of having both is redundancy (if your army moves away, the watchtower maintains coverage).

4. **~~Should the player be told "you don't know" or just see silence?~~** **RESOLVED:** Execute silently for direct commands (attack/move). For strategic commands (PURSUE), give the warning because the commitment is larger.

5. **~~Watchtower slot system?~~** **RESOLVED:** Dedicated watchtower field on Region, separate from building slots. Every region type can have one. No slot competition.

6. **~~Reckless cavalry auto-charge in fog?~~** **RESOLVED (Session 32b review):** Auto-charge ignores fog entirely. Reckless cavalry is reckless — they find and charge enemies regardless of visibility. The resulting battle grants FULL intel via battle reveal. Zero fog changes needed in auto-charge path. Thematically perfect (Ney at Waterloo).

7. **~~Cautious pathfinding in fog?~~** **RESOLVED (Session 32b review):** Cautious marshals only avoid VISIBLE enemies (PARTIAL+). If an enemy is fogged, the cautious marshal doesn't know to avoid it. Walking into a trap because intel was bad is a fog moment. Existing contact interrupt handles the surprise encounter.

8. **~~Cannon fire from fogged battles?~~** **RESOLVED (Session 32b review):** Non-issue. Every battle in the current game involves a player marshal. Cannon fire interrupts only trigger for nearby player marshals hearing battles their side is in. No fogged cannon fire is possible. Deferred to post-EA multi-nation conflicts.

9. **~~PURSUE arrives at empty region — interrupt type?~~** **RESOLVED (Session 32b review):** Not a new interrupt type. If target not found AND no enemies adjacent: order auto-cancels with message. If enemies detected adjacent via PARTIAL: existing personality-based contact vectors handle the encounter (aggressive charges, cautious reports/scouts, literal continues). The arrival itself provides fresh intel (FULL on current region, PARTIAL on adjacent).

10. **~~Watchtower under construction + battle damage?~~** **RESOLVED (Session 32b review):** Destroyed — reverts to "none". Consistent with how `building_under_construction = None` works for regular buildings.

11. **~~Scout range and intermediate regions?~~** **RESOLVED (Session 32b review):** Only the targeted region gets FULL. Intermediate regions untouched. The scouting marshal's army position provides PARTIAL on adjacent regions via normal adjacency rules.

12. **~~Status command implementation?~~** **RESOLVED (Session 32b review):** New `backend/intel_report.py` module produces the Berthier Intelligence Report. Reads WorldState + intel store, returns structured report grouped by visibility tier. Executor calls it for "status" action. `/status` endpoint calls it. Reusable by Campaign Briefing (6.5).
