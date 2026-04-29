# Ink & Iron: Session History Archive

> Archived sessions from STATUS.md. Sessions 1-55 (Feb 2 - Feb 19, 2026).
> For recent sessions, see `docs/STATUS.md`.

---

### Feb 19 (Session 55: Bugfix Batch — Fort Degradation Reports + Decimal Cleanup)

**Fixed enemy attack fort degradation missing from end-of-turn reports. Cleaned up all decimal/float display across Godot UI.**

**Fort Degradation in Enemy Attacks (combat.py, executor.py, enemy_phase_dialog.gd):**
- `log_battle_event` dict in combat.py now includes `fortification_degraded`, `fortification_old`, `fortification_new` fields
- Attack result `events` list in executor.py now includes the same three fort degradation fields
- Enemy phase dialog `_format_battle()` now displays fort degradation: "Fort degraded: X% -> Y%" or "Fortifications DESTROYED!"
- Previously enemy attacks that degraded player fortifications showed no fort info in the end-of-turn popup

**Decimal/Float Cleanup (map.gd, main.gd, enemy_phase_dialog.gd):**
- Root cause: GDScript JSON parser can return floats for integer JSON values (e.g., `0` becomes `0.0`)
- Fixed "Bombardments: 2.0/2 remaining" — `int()` wrap on `bombardments_this_turn` subtraction
- Wrapped 20+ tooltip display values with `int()`: morale, movement range, skills, trust, vindication, drill turn, shock bonus, fort percentage, fortify floor, cavalry turns, retreat stage, broken recovery, restless turns, income, stability, war damage, building slots, construction turns, garrison strength, recklessness, autonomy turns
- Made all three `_format_number()` functions accept untyped input with internal `int()` conversion — prevents comma-formatting from breaking on float strings like "72000.0"

**Tests:** 2986 passed, 3 skipped, 1 pre-existing flaky (probabilistic dice test). Zero regressions.

### Feb 19 (Session 54: Enemy AI Total Inaction Fix + Bombardment Display)

**Fixed 5 interconnected bugs causing enemy AI to take 0 meaningful actions after ~4 turns. Fixed fog filter suppressing all enemy battle/bombardment reports. Added bombardment display to enemy phase popup.**

**Enemy AI Fixes (enemy_ai.py):**
- **P3 refortify guards:** `_check_threats()` now checks `_unfortified_this_turn` and `ai_refortify_cooldown` before fortifying. Previously P3 bypassed all anti-oscillation guards, causing fortify→unfortify→fortify loops that consumed all AP.
- **Artillery P3 exemption:** Artillery marshals skip P3 fortify and fall through to P4 bombardment. Previously PrinceAugust would fortify instead of bombarding.
- **P8 refortify guard:** `_get_default_action()` refortify check expanded to include `_unfortified_this_turn` (was only checking cooldown).
- **P8 wait fallback:** Returns `wait` instead of `None` when refortify is blocked, preventing "all marshals skip → 0 actions" pattern.
- **Surrounded attack fallback:** When stagnation >= 3 and all adjacent regions have enemies (can't move), marshal attacks weakest adjacent enemy as desperate breakout.

**Fog Filter Fixes (main.py):**
- **Dict/string comparison bug:** Battle events store attacker/defender as dicts (`{"name": ..., "casualties": ...}`), but fog filter compared them directly as strings. `pm.name in (attacker, defender)` was always False. Now extracts `.get("name")` before comparison.
- **Bombardment events ignored:** Fog filter only checked `type == "battle"`, missing `type == "bombardment"`. Enemy bombardments on player marshals were silently suppressed.

**Bombardment Display (enemy_phase_dialog.gd):**
- Enemy phase popup now handles bombardment event type (was only battle/conquest)
- Action label shows "bombards" instead of "attacks" for bombardment actions
- New `_format_bombardment()` for event details and `_format_bombardment_report()` for structured report

**Bombardment Colors (main.gd):**
- Player-side bombardment report replaced uniform CCCCCC (near-white) with differentiated colors: enemy casualties red, own casualties green, terrain warm gray, fort degradation orange

### Feb 18 (Session 53: UI Polish — Help, Unit Types, Minimize, Ammo)

**Help command, unit type labels, minimizable terminal, bombardment ammo display.**

**Help Command Update (executor.py):**
- Added bombardment command with usage examples and terrain note
- Added garrison command (2 AP, cap 3/nation, fights to destruction)
- Added strategic commands section: march, pursue, support, hold, cancel with AP costs
- Added build stables example, artillery recruit cost (3k/400g)
- Added Drouot marshal abilities section (can't move+attack, bombardment, 2x fort degradation, exhaustion exempt)
- Updated Davout/Ney descriptions with unit type labels

**Unit Type Labels (world_state.py + map.gd):**
- Backend sends `artillery` flag and `bombardments_this_turn` in `tactical_state` dict
- Tooltip now shows unit type for ALL player marshals:
  - Ney/Murat: "CAVALRY: Can attack 2 tiles away" (orange)
  - Davout/Grouchy: "INFANTRY" (steel blue)
  - Drouot: "ARTILLERY: Cannot attack after moving" (copper)
- Removed duplicate standalone cavalry line (now unified in unit type display)

**Bombardment Ammo Display (map.gd):**
- Artillery marshals show "Bombardments: X/2 remaining" in tooltip
- Color-coded: green (2 remaining), yellow (1 remaining), red (0 remaining)

**Minimizable Terminal (main.tscn + main.gd):**
- "—" minimize button in header title row
- "Open Terminal (Tab)" restore button appears when minimized
- Tab key toggles terminal panel visibility (when command input not focused)
- Full panel collapses (header, output, input) and restores cleanly

**Auto-Assign Fixes (parser.py + executor.py):**
- `bombard Rhine` (no marshal) now auto-selects nearest artillery marshal with bombardments remaining
  - Future-proof: supports multiple artillery marshals (sorts by distance, picks nearest in range)
  - Error messages for: exhausted bombardments, no artillery in range, no target
  - `barrage` / `shell` / `cannonade` keywords also route correctly
- `scout Rhine` (no marshal) now auto-selects nearest marshal within scout range
  - Respects personality scout range bonus (Davout +1)
  - Filters broken/retreating marshals
  - Error messages for: no marshals in range
- Parser fix: words matching existing target (e.g., "Rhine") no longer fuzzy-match to marshal names
- Added `bombard`, `barrage`, `shell`, `cannonade`, `garrison` to fuzzy match skip_words

**Tests:** 2987 passing, 3 skipped. Zero regressions. 5 targeted auto-assign pipeline tests verified.

---

### Feb 18 (Session 52: Bombardment Part 5 — Godot Frontend + Berthier Observations)

**Berthier bombardment observations and Godot frontend display for bombardment results.**

**Berthier Observations (battle_report.py):**
- 6 new observation categories: `bombardment_effective` (3 variants), `bombardment_fort_cracking` (2), `bombardment_ineffective` (2), `bombardment_target_broken` (2), `bombardment_terrain_difficulty` (2), `bombardment_friendly_fire` (2)
- Priority-based selection: destroyed > friendly_fire > fort_cracking > terrain_difficulty (< 0.80) > ineffective (< 3%) > effective
- `_pick_bombardment_observation()` + `generate_bombardment_report()` functions
- Observation embedded in `bombardment_result.berthier_observation` (no separate report dict needed — casualty/terrain/fort data already in bombardment_result)

**Executor Wiring (executor.py `_execute_bombardment`):**
- Calls `generate_bombardment_report()` after casualties and fort degradation applied
- `berthier_observation` string added to `bombardment_result` dict
- Passes: attacker/defender names, casualties, terrain, terrain_modifier, fort_degraded, collateral

**Godot Frontend (main.gd):**
- `"bombardment"` event type in `_display_result()` match block
- `_display_bombardment_report()` function: terrain effectiveness (±% label), enemy/return fire casualties with remaining strength and morale, fort degradation (percentage change or "DESTROYED!"), collateral damage list with friendly fire highlighting (red), bombardments remaining, Berthier observation quote
- Bombardment advisory still shown separately after report (fort crumbling)

**Edge Cases Covered:**
- Empty/None collateral, collateral without friendly fire, fort destroyed vs partially degraded
- Terrain modifier at exact 0.80 boundary (NOT < 0.80), underscore terrain names replaced
- Float terrain_modifier/fort values handled via int(value * 100) in Godot
- Zero defender original (no division by zero), ineffective at exactly 3% boundary
- Strategic HOLD auto-bombardment (same executor path, observation generated)

**Tests:** 37 new tests in `test_bombardment_report.py` (6 template existence, 8 selection priority, 4 priority ordering, 3 generate function, 10 edge cases, 6 executor integration). Total: 2987 passing, 3 skipped. Zero regressions. Serialization 16/16.

---

### Feb 18 (Session 51: Bombardment Part 4 — Strategic HOLD + Objections)

**Artillery-specific HOLD behavior and 5 new objection triggers per BOMBARDMENT_SPEC.md §9, §7.**

**Strategic HOLD Bombardment (strategic.py `_execute_hold_bombardment`):**
- Artillery on HOLD auto-bombards adjacent enemies instead of sally/fortify
- Target selection: cautious=crack forts first, aggressive=finish weak first, literal=lock on previous target
- Shared bombardment limit (strategic + manual = 2/turn max)
- Enemy contact in same region breaks HOLD with request-for-orders
- Broken/retreating/dead targets excluded, executor failure gracefully handled
- `bombardment_target` field on StrategicOrder for literal personality target lock (serialized)

**5 New Artillery Objection Triggers (objection_v2.py):**
- `ordered_into_melee` — STRONG when cautious artillery ordered to attack in same region
- `reckless_repositioning` — MODERATE when cautious artillery moves with streak >= 2 and adjacent fortified target
- `ordered_to_cease_fire` — MODERATE when cautious artillery defend/fortify with streak >= 1 and adjacent fort
- `wasted_fire` — MILD (cautious + aggressive) when target has no forts and < 8k strength
- `last_shot_advisory` — MILD when cautious artillery on last bombardment with multiple targets

**Artillery Flavor Text (disobedience.py):**
- 5 new flavor text keys under cautious personality with 2 variants each

**Edge Case Audit:**
- Timed expiry checked BEFORE artillery dispatch (correct)
- Not-at-position checked BEFORE artillery dispatch (correct)
- Retreat recovery pauses BEFORE HOLD handler (correct)
- Last-shot advisory filters retreating enemies consistently with target selection

**Tests:** 42 new tests in `test_strategic_bombardment.py`. Total: 2950 passing.

### Feb 18 (Session 50: Bombardment Part 3 — Enemy AI Bombardment)

**AI artillery behavior improvements per BOMBARDMENT_SPEC.md §10.**

**Bombardment Limit Pre-Check (enemy_ai.py `_find_attack_opportunity`):**
- Artillery at bombardments_this_turn >= 2 returns None early from P4
- Prevents wasted AI evaluation cycle (executor would catch it, but this is cleaner)
- Non-artillery marshals completely unaffected

**P4.25 Garrison Assault Skip (enemy_ai.py `_find_garrison_attack`):**
- Artillery returns None immediately — cannot bombard garrisons from range
- Garrison combat requires same-region physical presence
- Infantry/cavalry garrison assault unchanged

**Ratio Bypass for Ranged Bombardment (enemy_ai.py `_find_attack_opportunity`):**
- Artillery bypasses cautious/aggressive ratio threshold for ranged targets
- Bombardment costs only 1.5% own strength — always favorable risk/reward
- Same-region artillery combat (handled by P0) still uses normal thresholds
- Non-artillery marshals still filtered by personality threshold

**Skip Broken/Retreating Targets (enemy_ai.py `_find_attack_opportunity`):**
- Artillery skips broken or retreating targets at range (distance > 0)
- Prevents wasting bombardments on already-defeated forces
- Same-region targets (distance == 0) unaffected (P0 handles, guard is defensive)
- Non-artillery marshals unaffected (filter is artillery + ranged only)

**Enhanced Target Selection (enemy_ai.py `_find_attack_opportunity`):**
- Artillery sort key updated: fort tier → force density → distance → terrain modifier
- Force density: count of other enemies in target region (collateral opportunity)
- Terrain tiebreaker: plains (1.10) preferred over mountains (0.60) for more effective bombardment
- Fort + building (tier 0) > fortified only (tier 1) > unfortified (tier 2) preserved from Session 43

**Tests:** 24 new tests in `test_ai_bombardment.py` (4 limit pre-check, 3 garrison skip, 3 ratio bypass, 5 broken/retreating, 5 target selection, 2 P0 integration, 2 full AI integration). **2908 total passing**, 3 skipped. Zero regressions. Serialization 16/16.

---

### Feb 18 (Session 49: Bombardment Part 2 — Collateral Damage + Event Log)

**Collateral damage system, friendly fire penalties, and region-name targeting.**

**Collateral Damage (executor.py `_execute_bombardment`):**
- After primary bombardment resolves, iterates all non-primary marshals in target region
- 40% chance per force, 25% of primary raw damage (±20% variance)
- Collateral morale penalty: -1 per hit
- Broken/retreating/dead marshals excluded from collateral
- Collateral target destroyed → uses `_apply_forced_retreat_or_break()` for consistent break behavior
- Scope: marshal objects only — capital garrisons and player garrison detachments unaffected

**Friendly Fire Penalties:**
- When collateral hits a marshal of same nation as artillery:
  - Trust -5 on the hit marshal
  - Relationship -1 between hit marshal and artillery marshal
  - Redemption threshold check: trust <= 20 triggers normal redemption event
- Narrative message clearly labels friendly fire vs enemy collateral

**Region-Name Target Auto-Selection (executor.py `_execute_attack`):**
- "Bombard Waterloo" (region name) auto-selects strongest enemy marshal as primary target
- Weaker enemies at same location become collateral candidates
- Only triggers for artillery bombarding from different region

**Event Log & Result Dict:**
- `collateral` array populated (was `[]` stub from Session 48)
- Each entry: `{name, nation, casualties, friendly_fire}`
- Collateral in both event log and `bombardment_result` nested object

**main.py Pass-Through:**
- Added redemption event handler in main command response builder
- Bombardment-triggered friendly fire redemption now flows to Godot

**Tests:** 23 new tests in `test_bombardment.py` (TestCollateralDamage: 16 tests, TestRegionNameTargeting: 1 test, TestCollateralTargetDestruction: 2 tests, TestRedemptionEventStructure: 1 test, TestBombardmentEndpointWiring: 3 tests). **2884 total passing**, 3 skipped. Zero regressions.

---

### Feb 18 (Session 48: Bombardment Part 1 — Core Resolution & Terrain)

**New dedicated bombardment resolution system replacing the old 50% return casualties hack in combat.py.**

**Core Bombardment (`_execute_bombardment` in executor.py):**
- New method: ~180 lines, handles all ranged bombardment resolution
- Damage formula: 4% of defender strength × shock skill multiplier × terrain modifier × variance(0.80-1.20)
- Return casualties: 1.5% of attacker strength × variance (independent of terrain)
- Fort degradation: 0.10 per bombardment (always artillery rate)
- Morale: -3 to defender per bombardment, no change to attacker
- No winner/loser, no counter-punch, no battles_won/lost increment
- 2 bombardments per turn limit (new `bombardments_this_turn` field)
- Bombardment streak tracking carried forward from Session 43
- Defender destroyed → reuses `_apply_forced_retreat_or_break` for consistent break system
- Region NOT captured on destruction — artillery doesn't advance

**Terrain Bombardment Modifiers (region.py):**
- `TERRAIN_BOMBARDMENT_MODIFIER` dict covering all 6 valid terrains
- Plains +10%, Forest -20%, Hills -25%, Mountains -40%, Urban -30%, River Crossing neutral
- Only affects offensive damage; return casualties are terrain-independent

**Routing Rule (executor.py):**
- Transparent routing in `_execute_attack`: if artillery + different region → `_execute_bombardment()`
- Same-region artillery combat still uses full `resolve_battle()` (melee)
- Enemy AI gets bombardment automatically (same executor, Building Blocks principle)
- Engagement check correctly blocks bombardment when enemies in artillery's region

**Dead Code Removal (combat.py):**
- Removed old ranged bombardment 50% return casualties block
- Removed `bombardment_range_message` from result dict and tactical prefix
- Added note pointing to new system in BOMBARDMENT_SPEC.md §3

**Integration:**
- `_acted_this_turn` flag for idle system
- `record_battle()` for cannon fire detection
- `record_attack()` for flanking system
- `update_intel_from_battle()` for fog of war
- `log_event()` with type "bombardment" for event history
- `bombardment_result` + `bombardment_advisory` pass-through in main.py
- Serialization: `bombardments_this_turn` in marshal `__init__`, `to_dict()`, `from_dict()`
- Reset in `advance_turn()` alongside existing per-turn counters

**Tests:** 37 new tests in `test_bombardment.py` (core, terrain, serialization, edge cases). 6 updated in `test_artillery.py`. **2861 total passing**, 3 skipped. Serialization enforcement 16/16.

---

### Feb 18 (Session 44: Artillery Session 3 — Godot Frontend + Full Audit)

**Godot frontend wiring for artillery + comprehensive backend audit.**

**Godot: Artillery Pool Display (main.gd, main.tscn):**
- Added `art_value` @onready reference and `artillery_pool` variable
- Extended `_apply_manpower()` to extract artillery from response
- Extended `_update_manpower_display()` with artillery label, value, and color warnings (orange < 8k, red < 3k)
- Added ArtLabel + ArtValue nodes to ManpowerDisplay HBoxContainer in main.tscn

**Godot: Bombardment Advisory Handler (main.gd):**
- Added handler in `_display_result()` to display `bombardment_advisory` string
- Uses COLOR_DISPATCH (warm gold) with Berthier quote format, matching cavalry_terrain_message pattern

**Backend Bug Fix — Artillery Pool Missing from API:**
- `world_state.py` `get_filtered_game_state_summary()` and `main.py` `/test` endpoint both omitted artillery from manpower_pools sent to Godot
- Fixed: added `"artillery": int(...)` to both locations
- Without this fix, the new Godot artillery display would always show 0

**Full Artillery Audit (all 7 backend files):**
- Verified: marshal.py, combat.py, executor.py, enemy_ai.py, objection_v2.py, world_state.py, battle_report.py
- All `getattr` guards present, serialization round-trip correct, combat modifiers at single source
- Edge cases noted (not fixed — design decisions):
  - Artillery advances when garrison collapses (inconsistent with no-advance, but garrison combat is a special path)
  - PURSUE strategic order on artillery wastes turns (AI blocks it, player doesn't)
- Parser issue found: Drouot/PrinceAugust not in `parser.py` valid_marshals list (pre-existing, blocks curl testing)

**Post-Audit Fixes:**
- Parser: Added Drouot to `valid_marshals` in `parser.py` — was rejected as unknown marshal in mock mode
- Executor: Blocked PURSUE strategic orders for artillery in `_execute_strategic_command()` — returns helpful message suggesting `move to`

**Ranged Bombardment — Reduced Return Damage (combat.py, battle_report.py):**
- Artillery attacking from adjacent region (different location from defender) takes only 50% return casualties
- Guns fire from behind the line, not in the melee — thematic and balanced
- Battle messages explain the mechanic: "guns bombard from range — return fire inflicts reduced casualties (50%)"
- Battle report snapshot includes ranged bombardment modifier
- Same-region artillery and non-artillery marshals are unaffected
- 6 new tests covering: casualty ratio, message presence, description text, same-region no-reduction, infantry no-reduction, snapshot

**Tests:** 2827 passed, 3 skipped (+6 new ranged bombardment tests)

---

### Feb 18 (Session 43: Artillery Session 2 — Intelligence & Behavior)

**Artillery transforms from functional to intelligent: bombardment streaks, Berthier advisory, personality objections, AI positioning/screening, exhaustion exemption.**

**Exhaustion Exemption (marshal.py, combat.py, battle_report.py):**
- Artillery exempt from exhaustion penalty — `_get_exhaustion_penalty()` returns 0.0
- Combat messages skip exhaustion display for artillery attackers
- Battle report snapshots skip exhaustion for artillery

**Bombardment Streak (marshal.py, executor.py):**
- `last_bombardment_target` + `bombardment_streak` fields with full serialization
- Streak increments on same target, resets on different target or move
- Cleared on broken state recovery

**Berthier Bombardment Advisory (executor.py):**
- After bombardment: if defender defense_bonus=0 and region fort<15%, advisory fires
- "Sire, the enemy fortifications are crumbling. An infantry assault would now have favorable odds."

**Personality Objections (objection_v2.py):**
- Aggressive: MILD `repeated_bombardment_same_target` at streak>=3 + weak target
- Cautious: MILD `move_while_bombarding` at streak>=1 + adjacent fortified target

**AI Artillery Behavior (enemy_ai.py):**
- P2 screen check: exposed artillery retreats toward friendly infantry when cavalry within 2
- P4 bombardment sort: artillery prefers fortified targets; cavalry prefers exposed artillery
- P7 anti-oscillation: artillery with adjacent targets stays and bombards
- 4 helper functions: `_artillery_has_screen`, `_enemy_cavalry_within_range`, `_score_artillery_position`, `_find_nearest_friendly_infantry`

**Audit Fixes:**
- Renamed misleading test (`test_artillery_same_region_attack_still_blocked`)
- Broken state handler clears `moved_this_turn`, `last_bombardment_target`, `bombardment_streak`
- Advisory suppressed when enemy destroyed (no "send infantry" to empty battlefield)
- Advisory checks `has_building("fortification")` not nonexistent `fortification_bonus` attribute
- Advisory wired through `main.py` to API response (was dead code)
- Forced retreat clears bombardment streak (not just broken state)
- Broken-state test exercises production code path (not vacuous)

**Tests:** 38 new tests in `test_artillery_session2.py` + 1 rename, 2821 total (3 skipped)

---

### Feb 18 (Session 42: Artillery Unit Type — Core Mechanics)

**Full implementation: artillery as third marshal type alongside infantry/cavalry.**

**Core System (marshal.py):**
- `artillery: bool` flag, mutually exclusive with cavalry via assert
- `moved_this_turn: bool` lifecycle: set on move, blocks attack, -25% defense, reset at turn start
- Starting marshals: Drouot (France/Paris/25k/cautious), PrinceAugust (Prussia/Netherlands/20k/cautious)
- Serialization: to_dict/from_dict with backward compat defaults

**Combat (combat.py):**
- Cavalry counter: +30% shock_multiplier when cavalry attacks artillery
- Fort degradation: 10% for artillery attacker (vs 5% for non-artillery)
- cavalry_counter_message in tactical_prefix and result_dict

**Executor (executor.py):**
- Can't attack after moving (early return with Berthier message)
- No advance on win: artillery stays at origin, target NOT captured
- Glorious Charge banned, PURSUE auto-promotion blocked
- Recruit type determination: artillery → cavalry → infantry priority order
- Economy display includes artillery pool with regen rate

**World State (world_state.py):**
- Constants: ARTILLERY_RECRUIT_AMOUNT=3000, ARTILLERY_RECRUIT_GOLD_COST_BASE=400, ARTILLERY_BASE_REGEN=300, URBAN_ARTILLERY_REGEN=200, MAX_ARTILLERY_POOL=20000
- Artillery regen: 300 base + 200 per urban region controlled
- moved_this_turn reset at turn start

**Enemy AI (enemy_ai.py):**
- moved_this_turn gate in `_find_attack_opportunity`
- Pool-aware recruit and cost-aware admin actions

**Parser/Reports:**
- Artillery keywords (bombard, barrage, shell, cannonade) → attack action
- Drouot/PrinceAugust in mock parser known_marshals
- 4 artillery observation templates in battle_report.py

**Tests:** 86 new tests across 14 categories, 2783 total (3 skipped)

---

### Feb 17 (Session 41: Manpower Pools Implementation)

**Full feature implementation: nation-level infantry/cavalry reserve pools gating recruitment.**

**Core System (world_state.py):**
- Nation-level `manpower_pools` dict: `{nation: {infantry: int, cavalry: int}}`
- Starting pools: France 80k/15k, Britain 50k/8k, Prussia 60k/10k
- Per-turn regen: infantry +5k (per controlled region), cavalry +500 (base) +500 (plains) +750 (stables)
- Caps: infantry 100k, cavalry 30k
- Constants: `INFANTRY_RECRUIT_AMOUNT=10000`, `CAVALRY_RECRUIT_AMOUNT=5000`, `INFANTRY_RECRUIT_GOLD_COST_BASE=200`, `CAVALRY_RECRUIT_GOLD_COST_BASE=300`

**Recruitment Rework (executor.py):**
- Marshal type (`cavalry: bool`) auto-determines pool, batch size, and gold cost
- Pool check BEFORE gold check — Berthier voice for all errors
- Parameterized `_calculate_recruit_cost(base_cost=200)` for both types
- Soft correction when player requests wrong type ("infantry" for cavalry marshal)
- Pool status line in recruit success message

**Stables Building (region.py):**
- New building type: 300g, 2-turn build, allowed in capital/major_city/city
- Boosts cavalry regen by +750/turn in that region

**AI Awareness (enemy_ai.py):**
- Pool availability check before recruit attempts (prevents `skip_actions` cascade)
- Type-aware gold cost in P1 and P7
- New P4.5: stables building (when cavalry pool < 60% cap and nation has cavalry marshals)
- `_should_build_stables()` and `_find_best_stables_region()` helpers

**Parser (llm_client.py + schemas.py):**
- `requested_type` field on ParseResult for cavalry/infantry keyword extraction
- Economy report shows infantry/cavalry pools with regen rates, low-cavalry Berthier warning

**Permanent HUD Display (main.tscn + main.gd):**
- `Inf: 80,000  Cav: 15,000` in status bar next to Gold
- Color warnings: green → orange → red as pools deplete
- Updates across all 10 response handlers (mirrors gold pattern)
- `/debug set_manpower <nation> <infantry|cavalry> <amount>` for testing

**Tests:** 2697 passing (+68 new, 0 regressions), 3 skipped. All 39 existing test regressions fixed (Ney cavalry math, gold costs, morale dilution). 18 integration tests for AI multi-turn behavior, endpoint wiring, and debug commands.

---

### Feb 17 (Session 40: Strategic Reroute Wastes 2 Turns)

**3 bugs fixed, 4 new tests.**

**Bug 1 — Auto-upgrade init skips reroute (executor.py):**
- When a move auto-upgraded to MOVE_TO and the first step was blocked, the code just `break`ed without calling `_handle_first_step_blocked()`. Order created with blocked path, wasting the init turn. Fix: calls `_handle_first_step_blocked()` (same as older init path), updates local `path` reference after reroute for cavalry correctness.

**Bug 2 — Strategic MOVE_TO/PURSUE reroute doesn't move (strategic.py):**
- Turn-by-turn handler called `_handle_blocked_path()` and returned immediately after reroute. Path updated but no movement — wasted another turn. Fix: after literal reroute (`action == "reroute"`), attempts move on first step of new path before returning. Applied to both MOVE_TO and PURSUE handlers.

**Bug 3 — Reroute ignores just-discovered blocked region (strategic.py):**
- `_handle_blocked_path` used fog-aware `_get_enemy_occupied_regions` for avoid list, which could miss the blocked region if fog hadn't been updated yet. Physical encounter is authoritative. Fix: always include `blocked_region` in avoid list.

**Bug 4 — Strategic interrupt shows in action log not popup (main.py + main.gd):**
- `pending_interrupt` field from executor was dropped by both `/command` (missing early return) and `/respond_to_objection` (not included in response dict) endpoints. Godot's `_on_objection_response` also lacked a `pending_interrupt` check. User's scenario: Davout objects → "proceed" → blocked path → interrupt text in log instead of popup. Fix: added early return in `/command`, passthrough in `/respond_to_objection`, and popup trigger in `_on_objection_response`. Audit confirmed all other popup-triggering fields are properly wired.

**Combined effect:** Literal marshal rerouting now reroutes AND moves on the same turn (1 turn instead of 3). Non-literal interrupt popups now display correctly.

**Tests:** 2629 passing (+4), 3 skipped

---

### Feb 17 (Session 38b: Bug Batch — Scout, Attrition Fog, Pursue Reroute, Stale Icons)

**5 bugs fixed, 9 new tests.**

**Bug 1 — Scout typo "acout" parsed as attack (llm_client.py):**
- Mock parser had no fuzzy matching for scout. Added "acout", "scou", "recon" as scout keyword aliases.

**Bug 2 — Enemy attrition visible to player (world_state.py + main.py):**
- Supply attrition events lacked `nation` field. Fog filter couldn't identify enemy attrition and leaked it at PARTIAL visibility. Fix: added `nation: m.nation` to attrition event dict.

**Bug 3 — PURSUE blocked at issuance for literal marshals (executor.py + strategic.py):**
- When PURSUE/SUPPORT orders hit a blocked path and tried to reroute, `destination = order.target` used the marshal name (e.g. "Wellington") as a region name for pathfinding. `find_path("Belgium", "Wellington")` → None → "Path blocked, no alternate route". Fixed in 6 locations across executor.py and strategic.py — all now resolve marshal names to their locations.

**Bug 4 — Stale intel icons not showing (world_state.py):**
- `get_filtered_game_state_summary()` only iterated live marshals per region. For STALE regions where enemies moved away, `fogged_forces` was always empty. Fix: inject frozen `intel.known_marshals` snapshot into `fogged_forces` for STALE regions. Dedup pass prevents ghost duplicates when enemy is visible at FULL/PARTIAL elsewhere.

**Not a bug — Adjacent intel decay:**
- Adjacency continuously refreshes intel each turn (by design). Intel only decays after the adjacent marshal moves away.

**Tests:** 2625 passing (+9), 3 skipped

---

### Feb 17 (Fog of War Audit — Full Coverage)

**Comprehensive fog audit across all tactical + strategic commands. All player-facing paths now fog-aware.**

**Bug 1 — Move command fog leak (executor.py):**
- Direct "move to X" checked for enemies at destination WITHOUT fog filtering, revealing fogged enemy positions
- Fix: player marshals moving to a fogged destination (below PARTIAL) now walk in blind. On arrival they discover enemies ("ENEMY FORCES DISCOVERED!") and are engaged. Visible destinations still block with "use ATTACK" prompt.

**Bug 2 — Strategic destination-blocked for ALL personalities (strategic.py):**
- Literal/aggressive/cautious marshals would offer "go around" when enemy held the destination itself
- Fix: all three personality branches in `_handle_blocked_path` now check `blocked_region == destination`. At destination: literal halts, aggressive auto-attacks or halts (no go_around), cautious halts (no go_around). Mid-path rerouting unchanged. New interrupt type: `destination_blocked`.

**Bug 3 — Attack suggestion fog leak (executor.py):**
- Out-of-range attack error listed "Targets in range" using global omniscient scan, revealing fogged enemies
- Literal popup listed all enemies for pursue alternatives, same global scan
- Null-target attack auto-found nearest enemy omnisciently, named them in messages
- Fix: all three paths now fog-filtered (PARTIAL+ only) for player marshals. `find_nearest_enemy` accepts optional `filter_fn` for visibility check.

**Audit result:** All remaining omniscient checks are intentional — same-region (physical co-location), adjacent (PARTIAL guaranteed), combat resolution, AI logic, LLM context.

**Tests:** 2611 passing, 3 skipped

---

### Feb 17 (Garrison Balance + Map Overlay)

**Garrison balance nerf (cap + AP cost) and map overlay UI.**

**Balance:**
- **AP cost raised to 2** (from 1) — garrison is now a real commitment, unified across player and AI
- **Nation cap of 3 garrisons** — includes capital garrisons (France has Paris = 1 used, 2 remaining). Berthier warning on cap, no AP consumed on rejection
- **BUGFIX: AP pre-validation** — executor hardcoded `required_actions = 1` for all military actions; now uses `world.get_action_cost(action)` so variable-cost actions (garrison=2) are correctly blocked when insufficient AP

**Godot Map Overlay:**
- **Garrison shield indicator** — colored rectangle below region circle with strength text ("3k", "15k", "?"). Dimmed under fog (PARTIAL/STALE). Nation-colored.
- **Region tooltip garrison line** — "Garrison: 15,000" or "Garrison: Present (unknown strength)" with [Detachment] tag
- **Map data pipeline** — garrison_strength + garrison_detachment in map_data, fog-filtered (FULL=exact, PARTIAL/STALE=sentinel -1 + band, UNKNOWN=hidden)

**Tests:** 2602 passing (+14 new: cap validation, AP cost, AP pre-validation bugfix, map_data, fog filtering), 3 skipped

---

### Feb 16 (AI Garrison Implementation)

**Enemy AI garrison placement + garrison system polish. Three changes:**

**1. `garrison_player_placed` → `garrison_detachment` rename:**
Rename across all source, tests, and docs. Flag now describes behavior (marshal detachment) not origin (player). Backward compat: `from_dict` accepts both old and new key. Zero test regressions.

**2. P4.25 sub-5k garrison awareness:**
`_find_garrison_attack()` now evaluates detachment garrisons of any size (not just >= 5k). P4.5 `_find_undefended_capture()` skips detachment garrisons, deferring to P4.25's conscious strength-ratio evaluation.

**3. AI Garrison Placement (P6.75):**
New `_consider_garrison()` in `enemy_ai.py`. Priority between drill/supply (P6-6.5) and strategic movement (P7). Conditions: strength >= 20k, own territory, no existing garrison, no enemies in/adjacent, no friendly marshal already defending, adjacent to non-friendly region (vulnerable border). Max 1 per nation per turn. AI garrisons use `garrison_detachment=True` (fight to destruction, no regen). Building Blocks principle — same `_execute_garrison` as player.

**Tests:** 2588 passing (+29 new AI garrison tests), 3 skipped

---

### Feb 15 (Session 39: Balance & AI Fixes)

**Playtest-driven balance fixes addressing 4 meta-game issues: AI passivity, supply attrition dominance, Grouchy vulnerability, and Paris defense.**

**Balance Changes:**
- **Grouchy start moved from Waterloo to Belgium** — no longer instantly destroyed by Wellington+Blucher
- **Home territory supply bonus (1.5x capacity)** — defending your own territory is now more sustainable, reduces turtling advantage
- **Victory threshold raised from 8 to 10 regions** — timed victory requires more aggressive play
- **Capital garrison system** — all capitals start with 15,000 garrison troops; must be reduced below 5,000 before capture; garrison gets terrain + fort bonuses; regenerates +2,000/turn (capped at 15,000)

**AI Improvements:**
- **Cautious advance** — cautious AI marshals now advance toward nearest enemy when not threatened and stagnation >= 1 (prevents Wellington/Blucher camping)
- **Re-fortify cooldown** — 2-turn cooldown after stagnation forces unfortify, prevents fortify→unfortify oscillation
- **Garrison assault (P4.25)** — AI evaluates garrison attacks based on strength ratio vs personality threshold
- **Capital proximity alerts** — player warned when enemy marshals are adjacent to their capital

**Garrison Combat System:**
- Simplified combat without pseudo-marshal (garrison is region property, not marshal)
- Garrison effective defense = strength × (1 + terrain_bonus) × (1 + fort_bonus where fort_bonus = 0.25)
- Proportional damage exchange with caps (attacker 35%, garrison 50%)
- Minimum losses enforced (2% attacker, 10% garrison) to prevent stalemates
- Below 5,000 threshold: garrison collapses, capture proceeds
- AI P-1 and P4.5 updated to respect garrison strength

**Tests:** 2497 passing (8 test files updated for Grouchy location change and supply bonus, 3 new test files with 63 tests for garrison/supply/AI coverage), 3 skipped

---

### Feb 15 (Session 31b: Playtest Balance Fixes)

**6 playtest-driven fixes addressing UX issues, combat realism, and new garrison command.**

**Fixes:**
- **Fix 500 Error:** Replaced emoji in print statements (14 total across main.py, executor.py, disobedience.py) that caused UnicodeEncodeError on Windows, crashing the /respond_to_objection endpoint
- **Fortification Degradation:** Defender's defense_bonus degrades -5% per battle in combat.py. Berthier observations added (4 categories: degraded/destroyed x attacker/defender). 19 tests
- **Garrison Command:** New "garrison" action — detach 3,000 troops to defend a controlled region. Uses existing garrison_strength + new garrison_player_placed bool. Player garrisons don't regen and fight to destruction (no 5k collapse). Full 8-step action pattern (validation.py, executor.py, parser.py, world_state.py, llm_client.py, prompt_builder.py, region.py serialization). 22 tests
- **Morale Warning:** Recruitment result shows [WARNING] at <40% morale, [DANGER] at <25%. 6 tests
- **Capture Hint:** After move, [HINT] shown for adjacent undefended enemy regions with FULL/PARTIAL visibility. Fog-aware, checks garrison. 8 tests
- **Occupy Alias:** "occupy" keyword in mock parser maps to "attack" action (word boundary regex, NOT in VALID_ACTIONS). LLM few-shot example added. 5 tests

**Tests:** 2558 passing (+61 from Session 39), 3 skipped

---

### Feb 15 (Session 38: Fog of War Map Visualization)

**Implemented fog of war visual rendering in Godot map — region fog overlay and fogged enemy marshal icons.**

**Backend:**
- Added `visibility_status` field per-region in `get_filtered_game_state_summary()` — sends fog level string directly to Godot

**Frontend (map.gd):**
- **Region fog overlay:** Semi-transparent dark overlay on region circles by visibility (FULL=bright, PARTIAL=slight dim, STALE=grey, LAST_KNOWN=dark, UNKNOWN=near-black). Border and label colors also dim.
- **Fogged enemy icons:** `fogged_forces[]` (previously ignored) now renders as dimmed nation-colored silhouettes with "?" overlay. PARTIAL more visible, STALE more faded.
- **Fogged enemy tooltip:** Name, nation, strength band ("large force"), intel quality indicator
- **Region tooltip fog-awareness:** UNKNOWN/LAST_KNOWN show minimal tooltip ("No intelligence"). PARTIAL/STALE show intel quality line.
- Removed debug print statements from `update_all_regions()`

**Tests:** 2434 passing (no regressions — frontend-only changes)

---

### Feb 15 (Session 37: Dev Tooling, Test Coverage, Bugfix)

**Added dev tooling (ruff, pytest-cov), Claude Code hooks, 5 new test files (170 tests), ruff auto-fix across backend, and fixed `get_authority_label` bug.**

**Dev tooling:**
- Added `pytest-cov` and `ruff` to dev dependencies
- Configured Claude Code hooks: PostToolUse auto-lint (ruff on .py edits), PreToolUse pre-commit test gate
- Ruff auto-fix: 148 safe fixes across 21 backend files (F541 f-strings, F401 unused imports)

**New test files:**
- `test_auto_assign_attack.py` (25 tests) — `_execute_auto_assign_attack`, `_execute_general_attack`, `_execute_general_retreat`
- `test_severity_modifiers.py` (72 tests) — severity tiers, variance bands, labels, AuthorityTracker lifecycle, strategic severity
- `test_fog_endpoint_filters.py` (22 tests) — `_filter_enemy_phase_by_visibility`, `_filter_tactical_events_by_visibility`
- `test_vindication_system.py` (27 tests) — all 9 outcome combos (trust/insist/compromise x victory/defeat/draw), edge cases, serialization
- `test_endpoint_wiring.py` (24 tests) — FastAPI TestClient for 11 endpoints, int value enforcement for Godot

**Bugfix:**
- `AuthorityTracker.get_authority_label()` was missing (called by `/authority_status` endpoint in main.py:1004)
- Added method to `authority.py` with 5 Napoleonic-themed labels (Divine Right → Emperor in Name Only)
- `/authority_status` endpoint no longer crashes with 500

**Tests:** 170 new (2434 total passing, 3 skipped), coverage 68% → 71%

---

### Feb 13 (Session 36: Fog of War Polish + Edge Cases + Audit)

**Final fog session. Edge case validation, contact interrupt discovery messages, Davout PURSUE fog-aware objection, V2b TODO markers, documentation updates, comprehensive audit.**

**Edge case tests (all passing — verified existing code handles correctly):**
- Broken marshal visibility: Step 0 grants FULL (strength > 0 after break with 3-10% survivors)
- Forced retreat into unknown region: `calculate_visibility()` at turn end grants FULL via marshal-present
- Own region behind enemy lines: PARTIAL military intel (band only), FULL economic data
- Multiple enemies same region at PARTIAL: combined strength → single aggregate band
- Occupied own region: standard PARTIAL per spec §2.3

**Contact interrupt fog-discovery messages (strategic.py):**
- `_handle_blocked_path()` checks region visibility before building messages
- Below FULL: "Enemy forces discovered!" discovery language
- FULL: standard "Enemy at [region]" messages
- All 3 personality branches updated (literal reroute, aggressive bad odds, cautious ask)
- `fog_discovery` flag in result dict for frontend differentiation

**Davout PURSUE fog-aware objection (disobedience.py):**
- FULL visibility: objects on exact odds (ratio >= 1.2) — unchanged behavior
- PARTIAL: objects on strength band comparison (target band > our band)
- STALE/LAST_KNOWN/UNKNOWN: objects on staleness ("X-day-old intelligence") if intel age >= 3 turns
- New reason: `davout_pursue_stale_intel` for staleness objections

**V2b TODO markers (objection_v2.py):**
- TODO (V2b) comments at all 12 helper functions documenting fog integration needed
- `get_visible_enemies_near()` helper added — returns omniscient data now, swappable to fog-filtered in V2b
- Updated TODO at disobedience.py Davout PURSUE section

**Integration tests:**
- Multi-turn decay: FULL → STALE (turn 3) → LAST_KNOWN (turn 5)
- Stale snapshot persistence: frozen data survives enemy movement
- Full turn cycle: scout → verify FULL → broken marshal → verify visibility

**Tests:** 20 new (2264 total passing, 3 skipped)

---

### Feb 13 (Session 34B: Strategic Fog of War + Display Filtering)

**All fog-of-war API responses now respect visibility. Strategic commands, enemy phase, and tactical events are fog-filtered.**

**Pre-implementation fix:**
- Added `RegionIntel` to `SERIALIZABLE_CLASSES` in `test_serialization_enforcement.py` (2 new tests)

**Prerequisite helpers on WorldState:**
- `get_last_known_location(marshal_name)` — scans intel store, returns `(region, turn, visibility)` or None
- `get_visible_enemies_in_region(region_name, nation)` — fog-filtered enemy data (FULL=exact, PARTIAL/STALE=band, UNKNOWN=empty)

**PURSUE fog validation (strategic.py):**
- PURSUE reads target location from intel store, not raw marshal data
- UNKNOWN target → reject ("No intelligence on [target]'s position, Sire.")
- STALE target → pathfind toward last known location
- Empty arrival → auto-cancel with intel age message + `target_not_found` event
- AI pursuits remain omniscient (spec §9.1)

**SUPPORT safety check (strategic.py):**
- Adjacent enemy scan uses `get_visible_enemies_in_region()` for player marshals
- Fogged enemies don't affect ally safety assessment

**Cautious pathfinding (strategic.py):**
- `_get_enemy_occupied_regions()` gains `fog_aware` parameter
- Player cautious marshals only avoid PARTIAL+ visible enemies
- AI pathfinding stays omniscient
- All 4 callers updated: cautious path, go_around, literal reroute, personality-aware path

**Enemy phase display filtering (main.py):**
- `_filter_enemy_phase_by_visibility()` — battles involving player always shown, FULL region actions shown, below-FULL suppressed, missing fields suppressed (safe default)

**Tactical event filtering (main.py):**
- `_filter_tactical_events_by_visibility()` — player events always shown, enemy events require PARTIAL+ visibility, fog events (intel_updated/intel_decayed/target_not_found) always shown

**Event log types (world_state.py):**
- `intel_updated` emitted in `calculate_visibility()` on actual visibility upgrades
- `intel_decayed` emitted in `decay_intel()` on downgrades
- `target_not_found` logged on PURSUE empty arrival
- All events appended to `_last_tactical_events` during `_advance_turn_internal()`

**Tests:** 45 new (2228 total passing, 3 skipped)
- 2 serialization enforcement (RegionIntel)
- 43 in `test_fog_34b.py`: helpers, PURSUE fog, SUPPORT fog, cautious pathfinding, enemy phase filtering, tactical event filtering, event log types, integration

**Next session: 36** — Edge cases, Godot smoke test, Davout PURSUE fix, V2b TODO markers, doc updates.

---

### Feb 13 (Session 34B-prep: Fog of War Pre-Implementation Review)

**Thorough audit of all fog-of-war code before Session 34B implementation. Documentation-only session — no code changes.**

**Findings:**
- All 147 fog-specific tests pass (57 fog_of_war + 40 intel_report + 53 watchtower = 147 across 3 test files)
- 2183 total tests passing, 3 skipped — unchanged from Session 35
- Sessions 33, 34A, and 35 are solid — no bugs or issues found in implemented code
- Confirmed: Session 34B has ZERO code written (no `get_last_known_location`, no `get_visible_enemies_in_region`, no `_filter_enemy_phase_by_visibility`, no fog awareness in strategic.py or turn_manager.py)
- **Serialization gap found:** `RegionIntel` missing from `SERIALIZABLE_CLASSES` in `test_serialization_enforcement.py`. Must fix before 34B starts.
- **Cavalry fog research completed:** Cavalry moves 2 regions/turn, charge range 2, auto-charge range 2. Intermediate-region omniscience accepted for Phase 6 (physical encounter, not intel). Sally is adjacent-only (no cavalry extension). Auto-charge omniscient by design (spec §9.2). Full findings documented in `FOG_IMPLEMENTATION_PLAN.md` §34B-R.

**Documentation updated:**
- `FOG_IMPLEMENTATION_PLAN.md` — Session 34B section: added pre-implementation fix (RegionIntel serialization), cavalry fog research results (§34B-R), `fog_aware` parameter design for cautious pathfinding, expanded `get_visible_enemies_in_region` return spec (FULL vs PARTIAL vs UNKNOWN), expanded `get_last_known_location` return type (tuple), test list expanded to ~35, safe-default rule for enemy phase filtering
- `FOG_OF_WAR_SPEC.md` — Added §5.0 "Mechanics vs Display" principle, cavalry 2-range fog note in §5.1, `target_not_found` event details in §10
- `STATUS.md` — This entry
- `CLAUDE.md` — Added strategic commands fog entry to "Before Modifying" table, added RegionIntel to serializable classes list

**Next session: 34B** — Pre-implementation fix (RegionIntel serialization), then PURSUE fog validation, SUPPORT visibility, cautious pathfinding, enemy phase filtering, tactical event filtering, event log types. ~35 new tests expected.

---

### Feb 12 (Session 35: Fog of War Watchtower Building)

**Watchtower as dedicated building type, bypasses slot system. Construction, visibility, scout synergy, damage/repair, AI building logic.**

**Watchtower building (dedicated Region field):**
- `watchtower` field: "none" / "under_construction" / "active" / "damaged"
- `watchtower_turns_remaining` field: construction/repair countdown
- Cost: 250 gold, 2 turns. All region types allowed (no slot needed)
- Added to Region `to_dict()`/`from_dict()` with backward compat defaults

**Visibility (calculate_visibility Step 3):**
- Active watchtower in player-controlled region → PARTIAL on all adjacent regions
- Source = "watchtower" (priority 1 in INTEL_SOURCE_PRIORITY, already existed)
- Does not override higher-priority sources (marshal_present, own_territory, adjacent)
- Refreshes each turn while watchtower is active (no decay while maintained)

**Scout synergy:**
- Scouting a watchtower-covered region: FULL expires after turn 3 instead of turn 2
- Implemented via `_has_watchtower_coverage()` helper + `last_updated_turn` bump

**Damage/destruction:**
- Battle: active → damaged (major always, normal 25% chance). Under construction → destroyed
- Plunder: watchtower destroyed (set to "none")
- Secure: active → damaged, under construction → destroyed

**Repair:**
- `_execute_repair()` handles watchtower: damaged → under_construction (2 turns, 150 gold)
- Construction timer handles watchtower completion alongside regular buildings

**AI building (enemy_ai.py):**
- Priority 6.5 (after repair, before low-priority recruit) in `_pick_admin_action()`
- `_find_best_watchtower_region()`: prefers border regions, scored by enemy adjacency + income
- `_find_damaged_building_region()`: now also detects damaged watchtowers for AI repair

**API/display:**
- `get_game_state_summary()`: includes watchtower/watchtower_turns_remaining in map_data
- `get_filtered_game_state_summary()`: shows watchtower for own/FULL regions, hides for fogged
- Debug command `add_building` updated to support watchtower (sets field directly)

**Files modified:**
- `backend/models/region.py` — watchtower + watchtower_turns_remaining fields
- `backend/models/world_state.py` — visibility Step 3, construction timer, scout synergy, capture effects, game state summary
- `backend/commands/executor.py` — build watchtower, repair watchtower, battle damage, plunder/secure, keyword extraction, debug
- `backend/ai/enemy_ai.py` — P6.5 watchtower building, helper, damaged finder
- `tests/test_watchtower.py` (NEW) — 53 tests
- `docs/STATUS.md`, `docs/FOG_IMPLEMENTATION_PLAN.md`, `docs/SAVE_FORMAT_REFERENCE.md`, `docs/ROADMAP.md`, `CLAUDE.md`

**Tests:** 53 new (2183 total passing, 3 skipped).

**⚠️ NEXT SESSION: 34B** — PURSUE fog validation, SUPPORT visibility, cautious pathfinding, enemy phase filtering, tactical event filtering, event log types. Independent of Session 35 (no dependency). Then Session 36 (edge cases + polish).

---

### Feb 12 (Session 34A: Fog of War Intel Report + Filtering Infrastructure)

**Berthier's Intelligence Report, filtered game state summary, scout persistence, battle reveal wiring. After this session, the status command shows fog-filtered intel, scouts persist FULL visibility, battles reveal regions, and all 29 API call sites serve fog-filtered data.**

**New file: `backend/intel_report.py`**
- `generate_intel_report(world)` — structured report grouped by visibility tier
- Sections: YOUR FORCES (always full), CONFIRMED (FULL), RECENT REPORTS (PARTIAL/STALE), LAST KNOWN, NO INTELLIGENCE (UNKNOWN)
- Formatted text output for terminal display + structured data for Godot

**`get_filtered_game_state_summary()` on WorldState:**
- Wraps `get_game_state_summary()`, redacts enemy data by intel visibility
- UNKNOWN: enemies hidden from map_data and enemies dict entirely
- PARTIAL/STALE: enemies moved to `fogged_forces[]` (not `marshals[]`) to prevent Godot rendering "0 troops" map icons
- FULL: enemies shown with exact data (unchanged from pre-fog behavior)
- Own region economic data always shown; enemy economic data only at FULL
- Controller and terrain always public (political/geographic knowledge)
- All 29 call sites replaced (26 in main.py, 3 in executor.py)

**Status command wiring:**
- New `_execute_status()` in executor.py calls `generate_intel_report()`
- `/status` GET endpoint returns Berthier's Intelligence Report + filtered game state
- "status" action routed in executor command routing block

**Scout persistence (C2 fix):**
- Targeted scout → `update_intel_from_scout()` → FULL on target region
- Adjacent scan → PARTIAL refresh on each adjacent region via `intel.refresh()`
- Scout data now persists to intel store (was previously ephemeral in API response only)

**Battle reveal wiring (6 sites):**
- `executor.py`: 5 sites (main attack, general attack, sally 2, sally 3, glorious charge)
- `world_state.py`: 1 site (auto-charge in `_process_reckless_cavalry_turn_start()`)
- All battles grant FULL visibility on battle region via `update_intel_from_battle()`

**Files modified:**
- `backend/intel_report.py` (NEW) — Berthier Intelligence Report
- `backend/models/world_state.py` — `get_filtered_game_state_summary()`, battle reveal wiring at auto-charge site
- `backend/commands/executor.py` — `_execute_status()`, status routing, scout persistence, battle reveal at 5 sites
- `backend/main.py` — 26 call sites replaced, `/status` endpoint rewritten
- `tests/test_intel_report.py` (NEW) — 39 tests (report, filtering, fogged_forces, integration)
- `docs/STATUS.md` — this entry
- `docs/FOG_IMPLEMENTATION_PLAN.md` — Session 34A marked COMPLETE

**Issues found during implementation:**
- Scout on own-territory regions: `update_intel_from_scout()` correctly fires but `own_territory` source takes priority (higher in INTEL_SOURCE_PRIORITY). This is correct behavior — own territory source is more authoritative than a scout. The FULL visibility is still granted.
- Adjacent scan source: Set to "scout" (not "adjacent") since the player actively ordered the scan. This gives adjacent-scan intel slightly higher source priority than passive adjacency from `calculate_visibility()`, which is correct — an ordered reconnaissance is more deliberate than passive line-of-sight.
- `_execute_attack()` signature is `(self, marshal, target, world, game_state)` not `(self, command, game_state)` — documented for future test writers.

**Tests:** 39 new (2130 total passing, 3 skipped).

---

### Feb 12 (Session 33: Fog of War Intel Data Layer + Visibility Core)

**Backend data layer for fog of war. RegionIntel model, visibility calculation, decay system, serialization. Game is functionally unchanged — nothing reads the intel store yet (filtering comes in Session 34A).**

**New file: `backend/models/intel.py`**
- `RegionIntel` class with visibility constants (FULL, PARTIAL, STALE, LAST_KNOWN, UNKNOWN)
- Strength bands: no forces, screening force (<5K), small (5-15K), substantial (15-40K), large (40-70K), massive (70K+)
- `refresh()` method: upgrade-only, stores live marshal data, resets `last_updated_turn`
- `decay()` method: frozen snapshot, only downgrades visibility level based on age
- Intel source priority: own_territory (5) > marshal_present (4) > scout (3) > battle (2) > watchtower (1) > adjacent (0)
- Full `to_dict()` / `from_dict()` serialization

**WorldState additions (`backend/models/world_state.py`):**
- `self.intel: Dict[str, RegionIntel]` — intel store for all 13 regions
- `calculate_visibility()` — Steps 0-3: marshal-present → own region → adjacent → watchtower placeholder. Tracks `_refreshed_regions_this_turn` set for decay to skip.
- `decay_intel()` — Degrades non-refreshed regions: FULL/PARTIAL → STALE at 3 turns → LAST_KNOWN at 5 turns
- `get_region_intel(region_name)` — Returns current intel (creates UNKNOWN entry if missing)
- `update_intel_from_scout(region_name, turn)` — Sets FULL with live data, sets `last_scouted_turn`
- `update_intel_from_battle(region_name, turn)` — Sets FULL with live data (no `last_scouted_turn`)
- `_build_marshal_snapshot(marshal, visibility)` — Creates marshal dict for intel (exact strength for FULL, band for PARTIAL)
- Wired at END of `_advance_turn_internal()` (after all processing), at end of `__init__()`, and after save load

**Key design decisions implemented (from Session 32c):**
- **Marshal-present → FULL (H6):** Grouchy in British Waterloo gets FULL visibility on Wellington — sees exact strength, morale, stance
- **Timing (H5):** End of turn, after broken retreats, auto-charges, income — player sees clean picture
- **PARTIAL decay (M1):** Same timeline as FULL, offset from `last_updated_turn`
- **Stale snapshots intentionally wrong:** When enemies leave, stale intel still shows them there

**Files modified:**
- `backend/models/intel.py` (NEW) — RegionIntel class, visibility constants, strength bands
- `backend/models/world_state.py` — intel dict, 6 new methods, wiring at 3 locations
- `backend/save_manager.py` — `calculate_visibility()` after load for backward compat
- `tests/test_fog_of_war.py` (NEW) — 55 tests
- `docs/SAVE_FORMAT_REFERENCE.md` — RegionIntel format section, intel field in WorldState
- `docs/STATUS.md` — this entry

**Tests:** 55 new (2091 total passing, 3 skipped).

---

### Feb 11 (Session 32b: Fog of War Fresh-Eyes Review)

**Opus fresh-eyes review of spec + implementation plan. 6 design decisions resolved. No code touched.**

**Design decisions resolved:**
- **Game init visibility:** `calculate_visibility()` called at end of `WorldState.__init__()` so turn 1 starts with French regions FULL, rest UNKNOWN.
- **Status command:** New `backend/intel_report.py` module (Berthier Intelligence Report) — fog-filtered status view grouped by visibility tier.
- **Session 34 split:** Original session 34 had ~12 items — split into 34A (filtering infra) and 34B (strategic commands + display filtering).
- **Reckless cavalry auto-charge:** Ignores fog entirely — thematically correct, reckless cavalry charges whatever is nearby.
- **Cautious pathfinding:** Only avoids VISIBLE enemies (PARTIAL+) — fog creates surprise encounters for cautious marshals.
- **PURSUE empty-arrival:** Simplified — no new interrupt type. Auto-cancels if no enemies found; existing personality vectors handle adjacent encounters.
- **Cannon fire in fog:** Non-issue — every battle involves a player marshal, fogged cannon fire impossible in 2-faction design.

**Doc updates:** Spec §3.3, §4.3, §5.2, §5.3, §7.1, §7.4, §9 (3 new subsections), §12, §14, §16 (7 new resolved questions). Implementation plan: all C/H issues annotated, 5-session structure, updated test estimates (~142-160 new → ~2178-2196 total), internal dependency table. AI Fog of War added to ROADMAP.md 1805 section.

**Files modified:** FOG_OF_WAR_SPEC.md, FOG_IMPLEMENTATION_PLAN.md, ROADMAP.md, STATUS.md.

**Tests:** 2036 (unchanged — no code touched).

---

### Feb 11 (Session 32: Fog of War Spec Review + Implementation Plan)

**Architectural review of FOG_OF_WAR_SPEC.md. Created FOG_IMPLEMENTATION_PLAN.md. No code touched.**

**Spec Review (6 parallel explore agents across all backend files):**
- **3 CRITICAL issues found:** (C1) `get_game_state_summary()` exposes ALL enemy data via 12+ API endpoints — need single filtering point. (C2) Scout action does NOT persist intel to WorldState — currently ephemeral in API response only. (C3) Enemy phase display in main.py reveals all enemy actions — must be filtered alongside status command.
- **5 HIGH issues found:** (H1) Watchtower keyword missing from `_extract_building_type()`. (H2) Watchtower field pattern diverges from building list — repair/damage handlers need extending. (H3) PURSUE/SUPPORT have 5+ direct enemy location accesses needing fog filtering. (H4) Objection system has 8+ fog-unaware enemy data helpers. (H5) Visibility calculation timing not specified in turn pipeline.
- **6 MEDIUM issues:** PARTIAL decay timeline unspecified, watchtower construction timer, multiple enemies display, map_data marshal filtering, AI watchtower priority chain, own-region PARTIAL split.
- **4 LOW issues:** RegionIntel class vs dict, intel source overlap, backward compat first load, event type documentation.

**Implementation Plan (5 Sonnet sessions + 1 Opus review) — updated in Session 32b:**
- Session 33: Intel data layer + visibility + decay + serialization + game init (~45 tests)
- Session 34A: Intel report + filtered game state + scout persistence + battle reveals (~30 tests)
- Session 34B: PURSUE fog + SUPPORT/HOLD fog + cautious pathfinding + display filtering (~25 tests)
- Session 35: Watchtower building + visibility + AI + repair + synergy (~30 tests)
- Session 36: Edge cases + Davout PURSUE + V2b markers + smoke test + docs (~20 tests)
- Opus code review gate after Session 36
- Total estimated: ~142-160 new tests → ~2178-2196 total

**Deferred items routed:**
- AI fog of war → FUTURE_DESIGN.md (Post-EA, 80+ regions)
- V2b fog triggers → OBJECTION_V2.md §8 (Phase 7)
- Spy network, captured dispatches, allied intel → FOG_OF_WAR_SPEC.md §15 (deferred)
- Fog tutorial content → TUTORIAL_SCRIPT.md (11 entries added)
- Fog sketches in FUTURE_DESIGN.md → marked as "IMPLEMENTED, see spec"

**Files modified:** FOG_IMPLEMENTATION_PLAN.md (NEW), FUTURE_DESIGN.md, OBJECTION_V2.md, TUTORIAL_SCRIPT.md, ROADMAP.md, STATUS.md, CLAUDE.md.

**Tests:** 2036 (unchanged — no code touched).

---

### Feb 11 (Session 31: Event Log Hardening EL1-EL5)

**Cleared 5 hardening TODOs from Session 30. Found and fixed 2 bugs (EL4 + float leak). 9 new tests.**

**EL1 (sally battle):** Test confirms `_execute_general_attack_combat` logs battle event via `_log_battle_event`. All 3 sally `resolve_battle` call sites share this wiring — 1 test covers the pattern.

**EL2 (glorious charge):** Test confirms `_execute_glorious_charge` logs battle event with correct location at recklessness 3+.

**EL3 (AI occupation capture):** Test confirms `_apply_occupation_capture_effects` logs `region_captured` event when AI completes occupation. Verifies `captured_by`, `captured_from`, and `method` fields. Cautious AI (Wellington) secures rather than plunders.

**EL4 (auto-charge): BUG FOUND.** `_process_reckless_cavalry_turn_start` in `world_state.py` was a 6th `resolve_battle` path that never logged battle events to `world.event_log`. The combat result contained `log_battle_event` data but it was only embedded in the tactical event dict, never passed to `world.log_event()`. Fixed by extracting and logging the event after `resolve_battle()`, matching the pattern used by `executor._log_battle_event()`.

**EL5 (API response audit): CONFIRMED SAFE.** `main.py` builds API responses by selectively picking keys — never references `log_battle_event`. The key (which contains floats in `battle_report.modifier_breakdown`) cannot reach Godot. Two tests verify: (1) source code of `/command` endpoint contains no reference to `log_battle_event`, (2) known response keys do not include it.

**Session 31b: Auto-charge float leak (follow-up investigation).**
Traced the auto-charge tactical event path: `_process_reckless_cavalry_turn_start()` → `tactical_events` → `_last_tactical_events` → `executor` → `main.py:491` (`response["tactical_events"] = result["tactical_events"]`) → Godot. The raw `combat_result` dict was embedded in the `auto_glorious_charge` tactical event and shipped to Godot. It contained `attacker_roll.multiplier` (a float, e.g. `1.025`). Godot's `_display_tactical_events()` has no `auto_glorious_charge` handler so it was inert — but a future handler would crash on the floats. **Fixed** by removing `combat_result` from the tactical event dict. The event already has `message` (human-readable) and `battle_report` (int-safe) as separate fields. 2 tests added: no `combat_result` key, recursive float scan on entire event dict.

**Files modified:**
- `backend/models/world_state.py` — EL4 fix (log_event call ~line 2955) + stripped `combat_result` from auto-charge tactical event (~line 3019)
- `tests/test_event_log_hardening.py` — 9 new tests (1 EL1 + 1 EL2 + 1 EL3 + 1 EL4 + 2 float leak + 3 EL5)

**Tests:** 9 new (2036 total passing, 3 skipped).

---

### Feb 11 (Session 30: Turn Events Log)

**Structured event log on WorldState recording all significant game events. Data-only plumbing — no UI. Consumed by Phase 6.5 Campaign Log, Phase 8.5 Gazette, etc.**

**What it does:**
- `world.event_log` — list of dicts accumulating across full game, never cleared
- Helper methods: `log_event()`, `get_events_for_turn()`, `get_events_since_turn()`, `get_events_by_type()`, `get_latest_events()`
- Full serialization (save/load) with backward compat for old saves (empty list default)

**Event types logged (13):**
- **Combat:** battle (with full battle_report), retreat, marshal_broken, marshal_recovered
- **Territory:** region_captured (with method: plunder/secure/occupation)
- **Economy:** recruitment, building_started, building_completed, building_damaged (battle/plunder causes), bankruptcy, desertion
- **Command:** objection (MODERATE+ only, not MILD), strategic_order

**Logging approach:**
- combat.py returns pre-built battle event in result dict (Option A — stateless combat)
- executor.py calls `world.log_event()` after each `resolve_battle()` (5 call sites)
- Retreat/broken events logged in `_apply_forced_retreat_or_break()` where destination is known
- Recovery events logged alongside existing tactical events in `_process_tactical_states()`
- Territory/economy/command events logged at their respective execution points

**Tests:** 39 new (2027 total)

**Known TODOs (Session 30 — event log hardening): ALL RESOLVED (Session 31)**
- [x] **TODO-EL1: Test sally battle event logging** — Test added: `test_sally_battle_logs_event`. Sally path via `_execute_general_attack_combat` confirmed logging correctly.
- [x] **TODO-EL2: Test glorious charge event logging** — Test added: `test_glorious_charge_logs_battle_event`. Charge at recklessness 3+ logs battle event with correct location.
- [x] **TODO-EL3: Test AI occupation capture event logging** — Test added: `test_ai_occupation_capture_logs_region_captured`. Cautious AI secures, event has correct captured_by/method.
- [x] **TODO-EL4: Verify auto-charge battle path logs events** — **BUG FOUND AND FIXED.** `_process_reckless_cavalry_turn_start` was a 6th unwired `resolve_battle` path — it never called `log_event()` for battle events. Added `log_event()` call after `resolve_battle()` in `world_state.py`. Test added: `test_auto_charge_logs_battle_event`.
- [x] **TODO-EL5: Audit `log_battle_event` key in API responses** — **CONFIRMED SAFE.** `main.py` builds responses by selectively picking keys (`success`, `message`, `battle_report`, etc.) — never references `log_battle_event`. 2 tests added: source code audit of `/command` endpoint + known-keys verification.

---

### Feb 11 (Session 29: Berthier's After-Action Report)

**Template-based battle report after every player-visible combat. Shows modifier breakdown, casualty summary, and one Berthier observation. Perspective-aware for attacker/defender.**

**What it does:**
- Read-only modifier snapshots taken BEFORE state-consuming get_attack_modifier()/get_defense_modifier() calls
- `snapshot_attacker_modifiers()` captures: stance, drill/shock, strategic bonus (peek only), personality, recklessness, exhaustion, cavalry terrain, flanking, glorious charge
- `snapshot_defender_modifiers()` captures: stance, fortify bonus, strategic defense (peek only), drilling penalty, personality, recklessness, terrain defense, fortification building
- `generate_battle_report()` returns modifier_breakdown, casualty_summary, and observation string
- 15 observation priorities (first match wins, 2-3 template variants each): mutual destruction, lost into fortification, lost fort overrun, lost bad stance (attacker/defender variants), lost terrain disadvantage, lost despite terrain, won heavy casualties, won broke fortification, won fort held, won drilled, lost narrow no drill, lost costly (catch-all), won decisively, stalemate, default
- All numeric values int()-wrapped for Godot safety

**Perspective-aware observations:**
- Observations always from Napoleon's (player's) perspective, not the attacker's
- When enemy attacks French marshal, "we won" = defender (French) won, "we lost" = defender lost
- `combat.py` includes `attacker_nation`/`defender_nation` in result dict
- `_pick_observation()` takes `player_nation` param, flips win/loss/modifier logic based on which side is the player
- Templates use `{marshal}` and `{enemy}` placeholders instead of hardcoded "we"/"our"
- Perspective-aware template selection: lost_bad_stance splits into attacking/defending variants, terrain checks both our_mods and their_mods, fort observations cover both attacker and defender

**Perspective bugs found and fixed:**
- **Bug 1 (HIGH):** Loss observations not firing when enemy attacks and wins. Three root causes: (a) terrain check only looked at their_mods but terrain defense is on defender's mods, (b) stance type filter rejected defender aggressive stance (snapshotted as "penalty" not "bonus"), (c) no catch-all for heavy losses — devastating defeats fell through to "standard affair"
- **Bug 2 (LOW):** Defender stance templates assumed attacker perspective ("reckless advance"). Split into attacker/defender variant lists

**Files created:**
- `backend/game_logic/battle_report.py` — snapshot functions + report generator + perspective-aware observation picker
- `tests/test_battle_report.py` — 65 tests (12 attacker snapshot, 7 defender snapshot, 6 report generation, 8 observation priority, 6 integration, 26 perspective flip + regression)

**Files modified:**
- `backend/game_logic/combat.py` — snapshot calls inserted before get_attack_modifier(), return dict extended with attacker/defender original strength + modifier_snapshot + battle_report + attacker_nation/defender_nation
- `backend/commands/executor.py` — 5 passthrough sites (attack, 3 sally events, charge)
- `backend/models/world_state.py` — 1 passthrough site (auto-charge event)
- `backend/main.py` — 1 passthrough block (battle_report in response)
- `godot-client/project-sovereign/scripts/main.gd` — `_display_berthier_report()` function with BBCode coloring, `_format_number()` helper for comma-separated thousands

**Tests:** 1988 total passing, 3 skipped.

### Feb 11 (Session 28: Berthier Parse Recovery)

**In-character error messages for unparseable commands. Berthier replaces raw errors.**

**What it does:**
- Generic "Unknown action" and "Marshal 'None' not found" errors replaced with in-character Berthier (chief of staff) responses
- Mock mode: template responses using real marshal/enemy names from game state, 3 categories x 2-3 variants
- Live mode (Anthropic): one LLM call with Berthier character prompt, falls back to mock on failure
- Berthier reacts to the Emperor's tone (insults, rudeness, absurdity) with flustered dignity
- Partial parse info (recognized marshal/target) forwarded to recovery for context-aware suggestions

**Files modified:**
- `backend/ai/prompt_builder.py`: `build_berthier_recovery_prompt()` — system + user prompt tuple
- `backend/ai/llm_client.py`: `generate_berthier_recovery()` + `_berthier_mock_response()` on LLMClient
- `backend/commands/parser.py`: `partial_marshal` / `partial_target` fields in validation failure dicts
- `backend/main.py`: Two early-return intercept blocks (before executor for parse failures, after executor for marshal-None failures)

**What it does NOT change:** No new actions, popups, state changes, serialization, or executor changes. Same `success: False` response shape — Godot needs no changes.

**Tests:** 20 new tests in `test_berthier_recovery.py`:
- Mock templates (8): non-empty, Berthier reference, recognized marshal/target, valid actions, variation, empty game state
- Prompt builder (5): system prompt character, raw command, partial parse, valid actions, return type
- Integration (7): gibberish→Berthier, valid→bypass, typo→fuzzy match, response format, partial marshal forwarding, marshal-None executor errors (scout, move)

**Tests:** 1923 total passing, 3 skipped.

### Feb 10 (Session 27: Phase 6 Save/Load System)

**Full game state persistence: manual save, manual load, autosave every turn.**

**Backend:**
- New `backend/save_manager.py` module: `save_game()`, `load_game()`, `autosave()`, `list_saves()`, `delete_save()`
- Save format: JSON with metadata (format_version, save_name, saved_at, turn, player_nation) + world_state (from `to_dict()`)
- Save directory: `saves/` relative to backend working directory, 1 autosave + up to 10 manual slots
- Autosave triggers at end of every turn (both `_execute_end_turn()` and auto-advance path)
- Autosave is non-blocking: turn doesn't fail if autosave fails
- Transient data cleared on load: `battles_this_turn`, `in_combat_this_turn`
- 4 new API endpoints: `POST /save`, `POST /load`, `GET /saves`, `POST /delete_save`
- Load endpoint replaces global `world` and `game_state["world"]`, returns `get_game_state_summary()` for Godot refresh

**Terminal Commands:**
- "save" / "save My Campaign" — saves with optional custom name, no AP cost
- "load" — lists available saves and shows load dialog, no AP cost
- Mock parser routes save/load as `meta_command` action before other keyword matching
- Executor handles meta_commands before AP checks, objection checks, and marshal resolution

**Godot Frontend:**
- `api_client.gd`: 3 new functions (`save_game`, `load_game`, `list_saves`)
- New `load_dialog.tscn` + `load_dialog.gd`: scrollable panel with save slot buttons, follows capture_choice_dialog pattern
- `main.gd`: load dialog wiring (scene load, signal connections, display refresh on successful load)
- Successful load refreshes: map, gold, turn, actions, admin AP

**Tests:** 38 new tests in `test_save_load.py`:
- File I/O (7): save creates file, custom filepath, filename sanitization, load restores, transient data cleared, autosave create/overwrite
- List/Delete (5): list returns all, sorted newest first, empty dir, skips corrupt, delete works + autosave blocked
- Error handling (3): missing file, corrupt JSON, missing world_state
- Roundtrip integrity (6): turn, gold, marshal state, region state, economy state, transient data
- Backward compatibility (4): missing metadata, old format version, extra fields ignored, missing fields get defaults
- API endpoints (4): save returns success, load replaces world, list returns saves, bad filename error
- Commands (2): save via executor, load shows saves
- Mock parser (4): save/load parsed as meta_command
- Autosave integration (1): end_turn triggers autosave

**Pause menu (Esc → Save/Load/Settings/Quit) deferred to Phase 6.5** — terminal commands + load popup sufficient for now.

**Parser fix:** `meta_command` action was rejected by `_validate_command()` in `parser.py` — added early return to bypass validation for meta commands. Also added `meta_command` to `meta_actions` list in `_apply_fuzzy_matching()` to skip marshal resolution. Both fixes required for save/load to work in-game.

**Smoke tested:** Save and load confirmed working in-game via Godot client.

**Tests:** 1903 total passing, 3 skipped.

### Feb 10 (Session 26: Phase 6.2 Opus Audit + Fixes)

**Phase 6.2 Economy: AUDITED AND CLOSED.** Fresh-instance Opus audit across 7 parallel research agents.

**10 P0 bugs found and fixed:**
- **Auto-advance data loss (P0-1/2/3):** Turn auto-advance path (executor.py:1426) was incomplete copy of `_execute_end_turn()`. Missing: `turn_end` financial event, `mild_concerns`, `independent_command_report`, `gold_spent_this_turn`. All four now captured before `advance_turn()` clears them.
- **AI plunder credits wrong nation (P0-4):** `_apply_plunder()` used `world.gold` (always player). Now takes `nation` param; AI path passes `marshal.nation`.
- **Float-to-Godot crashes (P0-5/6/7):** `war_damage` sent as raw float in every API response via `get_game_state_summary()`. Plus `remaining_damage` in repair events and `severity` in objection endpoint. All wrapped with `int(value * 100)`.
- **Mock parser keyword collisions (P0-8/9/10):** `"charge"` eaten by attack check (dead code). `"pass"` substring matched "pass through" as wait. `"dig in"` caught by hold before fortify. Fixed with word-boundary regex, reordering, and removal of dead code.

**10 P1 risks resolved:**
- Income breakdown `war_damage` float, fuzzy match `score` floats, debug `affects_trust_gains` float — all wrapped with `int()`.
- Godot `_display_tactical_events()` missing `construction_complete`, `occupation_complete/continues/abandoned` handlers — added.
- Admin AP exhausted message now mentions military commands still available.
- Supply capacity div-by-zero guard for modded `cap=0`.
- Mock parser substring risks: `move`/`raise`/`support` now use `\b` word boundaries.

**7 P2 cleanups:**
- WorldState and Region roundtrip serialization tests added (was key-presence only).
- Economy comments in `world_state.py` corrected (France upkeep 765 not 700, Britain income 350 not 250).
- Dead `_get_map_data()` (110 lines) removed from `main.py`.
- Enemy phase dialog now shows plunder/secure choice on AI captures.
- Conquest events include `capture_choice` field for Godot display.

**Defensive comments added** at auto-advance path, `_apply_plunder`, int() wrapping sites, and mock parser ordering to prevent recurrence.

**Economy balance observations (for 1805 rebalance):**
- France income 850, upkeep 765, net +85 (+235 with admin bonus). Cannot go bankrupt.
- Coalition runs deficits without admin bonus. Admin AP trap: spending AP costs 150g opportunity + action cost.
- Plunder/secure tradeoff well-tuned at 1.75x — plunder only optimal for short-term or desperate plays.
- Buildings affordable for France, major investment for Coalition.
- All acceptable for tutorial scenario; flagged for 1805 rebalance in ROADMAP.md.

**Tests:** 2 new roundtrip tests, 2 existing tests updated for war_damage format change. 1865 total passing, 3 skipped.

### Feb 10 (Session 25: Phase 6.2.H + Smoke Test Bugfixes)

**Supply depots now project logistics benefits to adjacent regions.**

- Depot forward logistics: moving into a region with a friendly undamaged depot nearby (destination or adjacent) halves movement attrition (0.5x after terrain)
- Does NOT stack, does NOT affect retreat/harassment/supply attrition/friendly stable exemption
- AI depot placement updated: within each priority tier (capital > major_city > city), prefers regions adjacent to enemy territory
- Attrition messages updated to show "forward supply lines reduce losses" when depot bonus active
- 16 new tests in `tests/test_depot_forward_logistics.py` (core projection, non-interaction, AI placement)
- Docs updated: ECONOMY_SPEC, SYSTEMS_REFERENCE, ENEMY_AI_REFERENCE

**Smoke test bugfixes (6 issues resolved):**

- **Recruit targeting (Bug C):** `find_nearest_marshal_to_region` now sorts by (distance, -strength) instead of (-strength, distance) — recruits go to nearest marshal, not strongest
- **Build parser (Bug G):** "build training ground" was parsed as drill ("train" substring match). Moved build keyword check before drill in mock parser
- **Supply attrition display (Bug I):** Backend produced `tactical_events` but Godot never read them. Added `_display_tactical_events()` in main.gd
- **Enemy phase labels:** enemy_phase_dialog.gd missing build/repair in match block; admin actions (no marshal) showed "Unknown". Added build/repair cases + nation fallback
- **Bankruptcy warning:** `turn_end_event` was missing `bankruptcy_turns` field; Godot had no display code. Fixed both backend event and frontend display (tiered warnings + per-marshal desertion messages)
- **Build typo tolerance:** Added common typos (bould, biuld, buld, buid) to mock parser build keyword list

### Feb 8 (Session 24: Economy Audit Fixes)

**Phase 6.2 Economy: Audit findings from Sonnet's review. 8 tasks, all complete.**

**Task 1: Coalition Territory Viability (world_state.py):**
- Reassigned territories: Bavaria + Vienna → Prussia, Milan → Britain
- Britain: 3 regions (Netherlands, Waterloo, Milan), 250 income, net -180/turn (was -330)
- Prussia: 3 regions (Rhine, Bavaria, Vienna), 400 income, net +100/turn (was -400)
- Starting gold increased: Britain 800→1500, Prussia 300→800
- Austria removed as active nation (territories absorbed into Coalition)

**Task 3: Plunder Gold Multiplier (executor.py):**
- New constant: `PLUNDER_GOLD_MULTIPLIER = 1.75`
- Paris plunder: 300 → 525 gold. Makes plunder meaningfully different from secure.

**Task 4: AI Recruitment Threshold (enemy_ai.py):**
- Changed `AI_RECRUITMENT_THRESHOLD` from 0.40 to 0.50
- AI now recruits when marshal below 50% starting strength (was 40%)

**Task 5: Training Ground Morale Buff (executor.py):**
- Recruit morale with training ground: 55% → 70% (+30% bonus, was +15%)
- At 70%: zero morale dilution into 70%+ armies — genuinely valuable building

**Task 7: AI Market/Depot Building (enemy_ai.py):**
- Added `_find_best_market_region()`: highest-income buildable region without market
- Added `_find_best_depot_region()`: prioritizes capital > major_city > city
- Admin priority chain now: recruit (P1) > market (P2) > depot (P3) > fortification (P4) > repair (P5)

**Task 8: AI Supply Attrition Survival (enemy_ai.py):**
- New P0.5 check in `_evaluate_marshal()`: between engagement (P0) and retreat recovery (P1)
- Triggers when supply excess > 50% (5% attrition tier)
- AI moves to adjacent friendly region with best supply margin

**Documentation:**
- Task 2: Core Territories section added to FUTURE_DESIGN.md
- Task 6: Market building documented in ECONOMY_SPEC.md
- ENEMY_AI_REFERENCE.md updated with P0.5 and admin priority changes

**Tests:** 30 new tests in `test_economy_audit_fixes.py` + 1 existing test updated (1844 total passing, 3 skipped).

**Follow-up fixes (discussion with user):**
- Two-tier AI recruitment: urgent (P1, below 50%) + rebuild (P7, 50%-100%). Enemies can reach 100% strength.
- Supply awareness moved from P0.5 (panic) to P6.5 (mild). AI attacks/threats first, relocates only when idle.
- Geneva reassigned from Neutral to Britain (4 British regions now: Netherlands, Waterloo, Milan, Geneva).
- Gold expenditure tracking: `gold_spent_this_turn` dict on WorldState, recorded in recruit/build/repair, shown in turn summary and economy command. Serialized.

### Feb 8 (Session 23: Phase 6.2.G AI Admin Phase, Economy Command, Turn Summary)

**Phase 6.2 Economy: COMPLETE.** All 7 sub-phases (6.2.A-G) shipped.

**AI Admin Phase (enemy_ai.py):**
- `execute_admin_phase()` — main entry point with 7 methods (main entry + 5 helpers + `_pick_admin_action`)
- Priority chain: recruit weak marshals (< 40% strength) > build fortification at border regions > repair damaged buildings > repair war damage > save AP (+75g/unused AP)
- Uses same executor as player (Building Blocks principle)
- `_acting_nation` field in command dict lets executor check correct nation's control and treasury
- Wired into `turn_manager.py` after enemy military phase, before strategic orders
- Fixed executor admin commands (recruit/build/repair) to work for AI nations via `_acting_nation` field

**Economy Command (executor.py):**
- `_execute_economy()` — free action (0 AP), displays nation's financial summary
- Aliases: `economy`, `treasury`, `finances`
- Wired in parser (`valid_actions`), validation (`VALID_ACTIONS`), mock parser (keywords)

**Turn Summary Financial Report:**
- `_execute_end_turn()` appends financial report showing income, upkeep, net gold, and balance

**UI Wiring:**
- Added `occupation_region`, `occupation_turns_held`, `occupation_turns_required` to `tactical_state` dict in `main.py::_get_map_data()` for Godot marshal tooltip

**Tests:** 29 new tests in `test_ai_admin_economy.py` (1813 total passing, 3 skipped).

### Feb 7 (Session 22: Phase 6.2.F Supply Limits, Movement Attrition, Contested Capture)

**Supply Limits (region.py + world_state.py):**
- `SUPPLY_BY_TYPE` constant: capital 50k, major_city 40k, city 30k, town 20k, rural 15k
- `supply_capacity` computed property on Region: base + supply depot bonus (+10k) * terrain modifier
- `process_supply_attrition()`: runs during turn resolution, 3 tiers (1%/3%/5% based on excess)

**Movement Attrition (executor.py):**
- `_calculate_movement_attrition()` helper: base 1% (retreat 0.5%), size penalty for >20k, terrain multiplier, +4% harassment through enemy fortification
- Wired into: `_execute_move()` (1-tile and 2-tile cavalry), `_execute_attack()` (undefended + post-battle advance), `_execute_retreat_action()`, `_apply_forced_retreat_or_break()`, `_execute_glorious_charge()` advance
- Broken army flee to capital: no attrition (already shattered)

**Contested Capture (executor.py + world_state.py + marshal.py + enemy_ai.py):**
- 3 occupation fields on Marshal: `occupation_region`, `occupation_turns_held`, `occupation_turns_required`
- `_attempt_region_capture()` helper: checks fortification, starts occupation or instant capture
- Replaced all 4 `world.capture_region()` call sites in executor.py with helper
- Occupation blocking: marshal can only wait/retreat/end_turn during occupation
- `_process_tactical_states()`: occupation tick — abandon if left, complete + capture if held
- `_apply_occupation_capture_effects()` on WorldState: handles AI plunder/secure decision
- AI skip: `_evaluate_marshal()` returns None for occupying marshals
- Cleared occupation on forced retreat/break paths
- Updated serialization test fixture

**Test fix:** `test_bankruptcy_desertion_before_income` — reduced Ney's strength to avoid supply attrition interference

**Tests:** 43 new tests in `test_supply_movement_contested.py` (9 supply capacity, 8 supply attrition, 12 movement attrition, 13 contested capture, 1 serialization)

### Feb 7 (Session 21: Region Tooltip, Market Building, Fortification Spelling)

**Market building (4th building type, region.py + executor.py):**
- New `market` entry in `BUILDING_TYPES`: 350 gold, 2 turns, capital/major_city/city
- +25% base income multiplier in `get_effective_income()` (after supply depot flat bonus, before stability/damage)
- Income examples: Paris 300->375, Lyon 200->250, Milan 150->187. Stacking with depot: Paris (300+50)*1.25=437
- "market" and "trade" keywords added to `_extract_building_type()` in executor.py

**Fortification spelling robustness (executor.py + prompt_builder.py):**
- Added "wall" and "defense" as aliases for fortification in `_extract_building_type()`
- Added 2 building few-shot examples in `prompt_builder.py` (build fortification, build market)

**Region hover tooltip (world_state.py + map.gd):**
- Backend: `map_data` now includes `buildings`, `building_under_construction`, `max_building_slots` per region
- Frontend: `hovered_region` / `region_full_data` vars in map.gd (same pattern as `hovered_marshal`)
- Region hover detection via distance check in `_draw_regions()` (radius 30)
- `_draw_region_tooltip()`: name, controller (nation color), type+terrain, income (effective/base), stability (color-coded by tier), war damage (if >0), buildings with DAMAGED tag, under-construction with turns remaining
- Marshal tooltip takes priority when hovering marshal icon inside region

**Debug command fix (executor.py):**
- `/debug damage_building`, `/debug set_stability`, `/debug set_gold` were unreachable — placed after marshal resolution block which tried to match region names as marshals
- Moved all 3 economy debug commands above the marshal resolution block (they take regions/values, not marshals)

**Battle damage fix (executor.py):**
- Battles now damage civilian buildings (markets, depots, training grounds) instead of fortifications
- Fortifications are immune to battle damage — they're built to withstand combat
- Fort value is the contested capture holdout (6.2.F): region holds out even after defending army retreats
- Plunder/secure still affect all buildings (including forts) — that's deliberate demolition, not combat

**Tests:** 48 new tests in `test_market_building_and_tooltip.py` (1737 total passing).

### Feb 7 (Session 20: 6.2.E Smoke Test Bug Fixes)

**5 bugs found during first Godot smoke test of Phase 6.2 (A-E), all fixed:**

**BUG FIX 1: Plunder/Secure popup never appeared in Godot frontend.**
- Backend fully implemented but frontend completely missing (no dialog, no handler, no API method)
- Root cause: Recurring wiring gap — backend returns popup data, Godot never checks for the field
- Fix: NEW `capture_choice_dialog.tscn` + `.gd`, added `send_capture_choice_response()` to api_client.gd, wired `pending_capture_choice` check + 3 handler methods in main.gd

**BUG FIX 2: `build fortification in Paris` returned "marshal none" error.**
- Parser fuzzy matching tried to match "fortification" against marshal names
- Root cause: `build` and `repair` not in `meta_actions` skip list in `parser.py:_apply_fuzzy_matching()`
- Fix: Added `"build", "repair"` to meta_actions list

**BUG FIX 2b: Build command returned "unknown building type" after marshal fix.**
- `_extract_building_type()` checks `command.get("raw_command")` but parser never included it in command dict
- Root cause: `parser.py` built command_dict with only marshal/action/target/confidence/type — no `raw_command`
- Fix: Added `"raw_command": llm_result.get("raw_command", command_text)` to command_dict in parser.py

**BUG FIX 3: "TURN X BEGINS" banner never appeared.**
- Godot `_display_turn_change()` expects event with `type: "turn_end"` + `old_turn`/`new_turn`/`income`
- Backend never generated this event — the events array only contained tactical events
- Fix: Inject `turn_end` event at start of events array in `_execute_end_turn()`

**BUG FIX 4: Auto turn-end only checked command AP, not admin AP.**
- `use_action()` flagged `should_end_turn` when `actions_remaining <= 0`, ignoring admin AP pool
- Admin action path hardcoded `should_end_turn: False`
- Fix: Both checks now require `actions_remaining <= 0 AND admin_actions_remaining <= 0`

**Debug commands added (Phase 6.2 testing):**
- `/debug damage_building <region>` — damage first building for repair testing
- `/debug set_stability <region> <0-100>` — set region stability
- `/debug set_gold <amount>` — set player gold

**Tests:** 1689 passed, 3 skipped, 0 failures.

### Feb 7 (Session 19: Phase 6.2.E Plunder/Secure + Buildings)

**Plunder/Secure capture choice (executor.py, main.py):**
- Player captures trigger `pending_capture_choice` popup (blocks commands until resolved)
- Plunder: stability 10, war_damage +0.35, plundered flag, gold = base income, buildings destroyed
- Secure: stability 25, no extra damage, buildings damaged (not destroyed)
- AI captures auto-decide by personality (aggressive → plunder, others → secure)
- New `/capture_choice` endpoint in main.py (same pattern as `/respond_to_objection`)
- All 4 capture paths in executor.py modified (undefended move, post-battle, auto-assigned battle, auto-assigned undefended)

**Building system (region.py, executor.py):**
- 3 building types: Supply Depot (300g/2t, +50 income), Fortification (400g/3t, +25% defense), Training Ground (250g/2t, 55% recruit morale)
- Slot limits: capital 2, city/major_city 1, town/rural 0
- Construction timers in `process_construction_timers()` (called during turn resolution)
- `_execute_build()` with 8 validation checks (slots, stability, gold, duplicates, etc.)
- Supply depot bonus applies to BASE income before stability/damage modifiers

**Fortification combat bonus (combat.py, executor.py):**
- New `fortification_bonus` parameter on `resolve_battle()` (stacks additively with terrain)
- All 5 resolve_battle call sites updated with fortification check

**Building damage (executor.py):**
- Battles damage fortifications: 100% for major (50k+), 25% chance for normal
- Plunder destroys all buildings; secure damages all buildings
- Construction cancelled on any capture

**Repair command (executor.py):**
- Repair war damage: 1 admin AP + 150 gold, -0.15 war_damage
- Repair building: 1 admin AP + 150 gold, damaged → functional

**Parser integration (validation.py, parser.py, llm_client.py):**
- build/repair added to VALID_ACTIONS, parser valid_actions, mock parser keywords
- build/repair added to ADMIN_ACTIONS set in executor.py

**Tests:** 72 new tests (test_plunder_secure.py, test_buildings.py), 1689 total passing.
**Bug hunt:** 7-step audit — all checks pass (serialization, gold accounting, stability boundaries, admin AP routing, turn flow, cross-system integration).

### Feb 7 (Session 18: Phase 6.2.D Recruitment Rework)

**Morale dilution (executor.py):**
- Green conscripts have 40% base morale (RECRUIT_MORALE constant)
- Weighted average: `new_morale = int((old_strength * old_morale + 10000 * 40) / (old_strength + 10000))`
- Morale set BEFORE `add_troops()` call (add_troops only modifies strength)
- Truncation via `int()`, not rounding: 66.67 → 66
- Below-40% armies get morale RAISED by recruiting (correct: fresh troops improve devastated army)

**Gold cost modifiers (executor.py):**
- `_calculate_recruit_cost(region, world)` — new helper method
- Capital: 150 gold (25% discount)
- Settling (stability 51-75): 300 gold (50% premium)
- Stable (stability 76+): 200 gold (base)
- Capital discount takes priority over settling premium (mutually exclusive flags)

**Stability gate (executor.py):**
- Blocked in Hostile (0-25) and Unrest (26-50) regions: `region.stability <= 50`
- Spec says "< 50" but we block entire Unrest tier (≤50) to match tier boundaries from 6.2.C
- Error message includes stability value and requirement ("Need stability 51+")

**Controller check (executor.py):**
- Recruitment location must be controlled by player's nation
- "recruit for Ney" when Ney is in enemy territory → blocked

**Updated return values:**
- Events now include: `morale_before`, `morale_after`, `gold_cost`, `stability_premium`, `capital_discount`
- All numeric values wrapped in `int()` for Godot
- Message includes cost breakdown and morale change: "Cost: 150 gold (capital discount). Morale: 80% → 66%"

**Admin AP:** Already routed in 6.2.B. No changes needed — executor routing layer handles AP deduction.

**Existing test fix:** `test_fuzzy_matching.py::test_recruit_with_marshal_typo` — moved Grouchy from Waterloo (British-controlled) to Paris so fuzzy match is tested, not controller check.

**Deprecation:** `full_game.py::_execute_recruit()` marked as deprecated with pointer to executor.py.

**Tests:** 48 new tests in `test_recruitment_rework.py` (1617 total)

---

### Feb 6 (Session 17: Phase 6.2.C Stability + War Damage)

**Region stability (region.py):**
- `stability: int = 100` — 0-100 range, affects income via tiered modifier
- Stability tiers: Hostile (0-25, 0% income), Unrest (26-50, 25%), Settling (51-75, 75%), Stable (76-100, 100%)
- Boundary values fall into LOWER tier (stability=25 → Hostile, stability=50 → Unrest, etc.)
- `get_stability_label()`, `_get_stability_modifier()` helpers
- Capture sets stability to 25 (TODO 6.2.E: plunder=10 vs secure=25 choice)

**War damage (region.py):**
- `war_damage: float = 0.0` — 0.0-0.5 range, reduces income
- `apply_war_damage(amount)` — adds damage, caps at 0.50
- `recover_war_damage(0.02)` — natural recovery per turn
- Normal battle: +0.10, Major battle (50k+ combined pre-battle troops): +0.20

**Combined income formula (region.py):**
- `get_effective_income()` = `int(income_value * stability_modifier * (1.0 - war_damage))`
- `calculate_turn_income()` now uses `get_effective_income()` instead of raw `income_value`
- Income breakdown includes per-region stability, damage, effective income details
- `get_game_state_summary()` map_data includes: effective_income, stability, stability_label, war_damage

**Battle effects (executor.py):**
- `_apply_battle_effects_to_region()` helper: war damage + stability hit (-10) per battle
- Uses pre-battle troop counts for 50k major battle threshold (not post-battle)
- Applied at ALL 6 `resolve_battle()` call sites in executor.py
- Applied at auto-charge in `world_state.py` and 3 legacy sites in `full_game.py`
- Two battles in same region stack damage (0.10 + 0.10 = 0.20)

**Turn resolution (world_state.py):**
- `process_stability_growth()` — +5/turn base, +5 garrison bonus (friendly marshal present)
- `process_war_damage_recovery()` — -0.02/turn natural recovery
- `_has_marshal_in_region(region_name, nation)` — garrison check helper
- Runs in `_advance_turn_internal()` BEFORE bankruptcy/income phase
- Stability capped at 100, war damage floored at 0.0

**Serialization:**
- `stability`, `war_damage` in Region `to_dict()`/`from_dict()`
- Backward compat: missing stability defaults to 100, missing war_damage defaults to 0.0
- Serialization enforcement tests pass

**Tests:** 78 new tests in `test_economy_stability_war_damage.py` (1569 total)

---

### Feb 6 (Session 16: Phase 6.2.B Upkeep + Bankruptcy + Admin AP)

**Upkeep calculation (world_state.py):**
- `calculate_turn_upkeep(nation)` — formula: `(marshal.strength // 1000) * 5` per marshal
- Upkeep halved during bankruptcy (mercy mechanic)
- Returns breakdown with per-marshal cost detail

**Income phase refactor (world_state.py):**
- `process_income_phase(nation)` — full income cycle: income - upkeep + admin bonus = net
- `apply_turn_income()` now wraps `process_income_phase()` for backward compat
- `_advance_turn_internal()` processes ALL nations (player + enemies), not just player
- Admin bonus: unused admin AP * 75 gold (player nation only)

**Bankruptcy system (world_state.py):**
- `nation_bankruptcy_turns: Dict[str, int]` — per-nation tracking (same pattern as `nation_gold`)
- `bankruptcy_turns` convenience property for player nation
- `_update_bankruptcy(nation)` — increments counter when gold < 0, resets to 0 when solvent
- `process_bankruptcy_desertion(nation)` — runs BEFORE income phase using PREVIOUS turn's counter
  - Turn 1: warning, upkeep halved
  - Turn 2: severe warning, upkeep halved
  - Turn 3+: desertion (5% strength loss per marshal, rounded down)

**Admin AP infrastructure (world_state.py + executor.py):**
- `admin_actions_remaining` / `max_admin_actions` fields (default 2/2)
- `use_admin_action()` — consumes from admin pool, returns False if insufficient
- Admin AP resets at turn start alongside CP
- `get_action_summary()` includes admin AP fields
- `ADMIN_ACTIONS = {"recruit"}` in executor.py — recruit now uses admin AP, not CP
- Pre-check and consumption routing in executor for admin vs military actions

**Serialization:**
- `admin_actions_remaining`, `max_admin_actions`, `nation_bankruptcy_turns` in to_dict/from_dict
- Backward compat: missing fields default to 2/2/{} respectively
- Serialization enforcement tests pass

**Tests:** 59 new tests in `test_economy_upkeep_bankruptcy.py` (1491 total)

---

### Feb 6 (Session 15: Phase 6.2.A Region Types + Economy Foundations)

**Region types (region.py):**
- Added `region_type` field: capital, major_city, city, town, rural
- `VALID_REGION_TYPES` set and `REGION_TYPE_INCOME` dict as single source of truth
- Updated all 13 REGIONS_DATA entries with types and differentiated income values
- Validation: invalid region_type raises ValueError
- Serialization: `to_dict()`/`from_dict()` with `"town"` backward compat default

**Differentiated income (region.py REGIONS_DATA):**
- Paris: capital (300), Vienna/Lyon: major_city (200), Milan/Marseille: city (150)
- Belgium/Rhine/Bavaria/Geneva: town (100), Netherlands/Waterloo/Brittany/Bordeaux: rural (50)
- Removed +200 hardcoded capital bonus from calculate_turn_income — capital type income (300) replaces it

**Per-nation gold (world_state.py):**
- `nation_gold` dict: France 600, Britain 800, Prussia 300
- `world.gold` property wrapper for backward compat — all 22+ existing references work unchanged
- `calculate_turn_income(nation=None)` works for any nation, defaults to player
- `apply_turn_income(nation=None)` adds income to specified nation's gold
- Serialization: `nation_gold` dict in to_dict, backward compat from_dict (old `gold` field → player nation)

**Tests:** 46 new tests in `test_economy_foundations.py` (1432 total)

---

### Feb 6 (Session 14: Phase 6.1.C Weighted Pathfinding + Terrain Display)

**Phase 6.1 Terrain: COMPLETE.** All 3 sessions (A, B, C) done.

**Weighted pathfinding (world_state.py):**
- `find_weighted_path()` — Dijkstra using `TERRAIN_MOVEMENT_COST` as edge weight. Heapq with counter tiebreaker.
- `get_weighted_distance()` — Returns total weighted cost of optimal path (float('inf') if unreachable).
- Existing BFS methods (`find_path()`, `get_distance()`) untouched.

**Strategic integration (strategic.py, executor.py):**
- MOVE_TO and HOLD now use `find_weighted_path()` — avoids mountains/expensive terrain when possible
- PURSUE stays on BFS — chasing doesn't pick scenic routes
- SUPPORT stays on BFS — following allies directly
- All MOVE_TO/HOLD path calculation sites updated: initial path, recalculation, per-turn movement, reroute (go_around), literal reroute, cautious compromise, auto-upgrade

**AI integration (enemy_ai.py):**
- `_find_retreat_destination()` sorts safe regions by `get_weighted_distance()` to capital — AI retreats avoid mountains
- All other AI distance checks remain BFS (single-hop adjacency comparisons, range checks)

**Terrain display (executor.py, world_state.py):**
- Targeted scout includes "Terrain: Hills (+15% defense)" in message
- Adjacent scout summary includes terrain type for each region
- Scout events include terrain data for Godot frontend (terrain, terrain_display, defense_bonus)
- `get_game_state_summary()` map_data includes `terrain` field per region

**Bug fix (main.py):**
- Fixed emoji `print()` statements that crashed on Windows console encoding (charmap codec). Replaced emoji prefixes with ASCII `[OBJECTION]` tag.

**Tests (39 new in `test_terrain_pathfinding.py`):**
- TestFindWeightedPath (11): route preference, mountains, unreachable, avoid_regions, BFS/Dijkstra divergence
- TestGetWeightedDistance (6): correct sums, inf for unreachable, comparison with hop count
- TestMoveToUsesWeightedPath (1): MOVE_TO avoids mountains
- TestHoldUsesWeightedPath (2): HOLD avoids mountains, path differs from BFS
- TestPursueUsesBFS (1): PURSUE uses BFS
- TestAIRetreatTerrainAware (2): retreat weighted distance
- TestTerrainDisplay (7): scout text format, event data, map_data terrain field
- TestBFSUnchanged (5): regression tests for existing BFS
- TestWeightedPathfindingEdgeCases (4): all-mountains, inclusive paths, adjacent distance

**Total: 1386 tests passing, 3 skipped.**

---

### Feb 6 (Session 13: Phase 6.1.B Smoke Test Bug Fixes)

**3 bugs found during Godot smoke testing, all fixed:**
- **BUG 1 (cavalry_terrain_message passthrough):** Cavalry terrain flavor message (e.g. "Cavalry thrives on Plains!") generated in `combat.py` but not forwarded through `executor.py` → `main.py` to Godot as a separate field. Added passthrough in both files.
- **BUG 2 (glorious charge popup on blocked terrain):** When terrain blocks a cavalry charge (forest/mountains/urban), popup never appeared. Now scans for alternative chargeable enemies within cavalry range (2 regions) on allowed terrain. If alternatives found: offers redirect popup. If no alternatives: falls through to normal attack with terrain message.
- **BUG 3 (recklessness reset on blocked charge):** `world_state.py` auto-charge path unconditionally reset recklessness to 0 even when terrain blocked the charge. Now only resets when charge actually executes (conditional `if not charge_blocked`).

**Charge redirect popup (new feature from Bug 2 fix):**
- When reckless cavalry (level 3) attacks enemy on blocked terrain, executor searches for enemies within range on chargeable terrain
- If found: returns `pending_glorious_charge=True, charge_redirected=True` with alternative target info
- If not found: falls through to normal attack, prints terrain blocking message
- At recklessness 4+ (auto-charge), blocked terrain downgrades to normal attack without reset

**Regression tests (13 new, in `test_smoke_bugfixes_61b.py`):**
- TestCavalryTerrainMessagePassthrough (4 tests): plains message, forest message, no message at recklessness 0, executor passthrough
- TestGloriousChargePopupTerrain (6 tests): popup on plains, popup on hills, no popup on forest without alternatives, redirect popup on forest with alternatives, CHARGE_BLOCKED_TERRAIN constant check, recklessness persists after terrain block
- TestRecklessnessResetOnBlockedCharge (3 tests): blocked terrain preserves recklessness, allowed terrain resets it, blocked generates correct message

**Also fixed:** `test_terrain_combat_integration.py` test renamed to `test_recklessness_popup_suppressed_on_blocked_terrain_no_alternatives` with enemy cleanup to prevent false redirect popup trigger.

**Verified:** 2 prior Opus review bugs (full_game.py dead code, charge safety net fallthrough) already fixed in commit 10624a3.

**Test count: 1347 passed, 3 skipped, 0 failures**

**Follow-up polish (same session):**
- **Godot cavalry terrain flavor:** `main.gd` `_display_battle_result()` now shows cavalry terrain message as a distinct warm-gold line (e.g. "🐴 Ney's cavalry thrives on Plains terrain!"). Field added to battle event dict in `executor.py`.
- **Recklessness color tags:** All recklessness reset/change messages now use `[color=#cd6b6b]...[/color]` BBCode for visual distinction in Godot's RichTextLabel.
- **BUG FIX (auto-charge message):** `world_state.py` auto-charge event always said "Recklessness reset to 0" even when terrain blocked the charge (recklessness NOT actually reset). Now shows "Recklessness unchanged (4)" when blocked.
- **Charge redirect sort:** Alternatives now sorted by `(distance, strength)` — nearest first, weakest as tiebreaker. Previously arbitrary dict iteration order.

### Feb 6 (Session 12: Phase 6.1 Terrain Implementation)

**Session 6.1.A — Terrain Data Layer (59 tests):**
- Added 7 terrain constants to `region.py`: `VALID_TERRAINS`, `TERRAIN_DEFENSE_BONUS`, `TERRAIN_MOVEMENT_COST`, `TERRAIN_SUPPLY_MODIFIER`, `TERRAIN_CAVALRY_EFFECTIVENESS`, `TERRAIN_CAVALRY_ATTRITION_BONUS`, `CHARGE_BLOCKED_TERRAIN`
- Added `terrain` field to Region model with validation, `to_dict()`, `from_dict()` (defaults to "plains" for backward compat)
- 4 computed properties: `defense_bonus`, `movement_cost`, `supply_modifier`, `cavalry_effectiveness`
- All 13 REGIONS_DATA entries assigned terrain. Distribution: plains(4), hills(3), urban(3), mountains(1), forest(1), river_crossing(1)
- Updated serialization enforcement fixture, doc_generator, SAVE_FORMAT_REFERENCE.md

**Session 6.1.B — Combat Integration + Cavalry Terrain (43 tests):**
- `combat.py`: `_get_terrain_bonus()` reads from `TERRAIN_DEFENSE_BONUS` (single source in region.py). Legacy terrain values still work.
- `combat.py`: Cavalry recklessness attack bonus scaled by `TERRAIN_CAVALRY_EFFECTIVENESS` (plains 1.2x boost, mountains 0.3x gut)
- `executor.py`: All 5 `resolve_battle()` call sites read terrain from defender's region
- `executor.py`: Charge blocking at two layers — popup suppression + safety net in `_execute_glorious_charge()`
- Combat messages: terrain defense message, cavalry terrain message

**Opus Code Review — 3 bugs found:**
- BUG 1 (HIGH): `world_state.py:2248` auto-charge path called `resolve_battle()` without terrain and without charge blocking
- BUG 2: `full_game.py` (dead code, nothing imports it) had 3 hardcoded `terrain="open"` sites
- BUG 3 (LOW): `executor.py` charge safety net said "attack proceeds" but returned `success: False` (no attack happened)

**Bug Fixes (10 regression tests):**
- BUG 1: Auto-charge now reads terrain from defender's region + blocks charge bonus on mountains/forest/urban (downgrades to normal attack)
- BUG 2: Added `# TODO: Wire terrain from region if this file is revived` to all 3 `full_game.py` sites
- BUG 3: Safety net now falls through to `_execute_attack()` so attack happens without charge bonus

**Test count: 1334 passed, 3 skipped, 0 regressions** (1 pre-existing flaky dice test)

### Feb 6 (Session 11: Terrain Review + Phase 6 Implementation Plan)

**Terrain codebase analysis (5 findings):**
- Finding 1: `cavalry_ratio: float` doesn't exist — only `marshal.cavalry: bool`. Decision: use boolean proxy.
- Finding 2: Glorious charge blocking must go in executor.py, not combat.py.
- Finding 3: 5 `resolve_battle()` call sites in executor.py (not 1 as spec implied), including `_execute_glorious_charge()` missing terrain param entirely.
- Finding 4: Pathfinding has 3 BFS implementations (world_state.get_distance, world_state.find_path, enemy_ai._get_shortest_path). Decision: add weighted alongside, don't replace.
- Finding 5: Region constructor changes won't break tests (terrain has default).

**Terrain design review:**
- 6 terrain types confirmed (GO verdict). All passed one-sentence differentiation test.
- Evaluated 4-type reduction — decided to keep 6 to prep for 1805 map.

**Implementation plan:**
- Created `docs/PHASE6_IMPLEMENTATION_PLAN.md` — 10 sessions (3 terrain + 7 economy)
- Methodology: bottom-up with integration tests at each layer
- 4 review checkpoints, 6 stop-and-test gates
- Updated TERRAIN_SPEC.md §14, STATUS.md, CLAUDE.md, SYSTEMS_REFERENCE.md, ROADMAP.md

### Feb 6 (Sessions 8-10: Economy Spec Design)

**3 design review rounds across 3 sessions (context continuations):**

**Session 8 — Initial Economy Spec + Cohesion Assessment:**
- Created `docs/ECONOMY_SPEC.md` — complete economy implementation spec (17 sections)
- Reviewed spec against 18 codebase files for conflicts, serialization gaps, edge cases
- Assessed `docs/COHESION_FUTURE_DESIGN.md` → verdict: defer, morale dilution sufficient for now
- Appended cohesion content to `docs/FUTURE_DESIGN.md` under "Army Cohesion (Deferred)"

**Session 9 — 12 Design Updates + Comprehensive Review:**
- Deleted `docs/COHESION_FUTURE_DESIGN.md` (content folded into FUTURE_DESIGN.md)
- Applied 12 design decisions: halved upkeep rate (* 5), nerfed plunder (+0.35 war_damage), buffed secure (0.0 war_damage), pending_capture_choice pattern, all nations use identical economy, retreat half-attrition, construction cancelled on capture, separate use_admin_action(), morale dilution note, admin generals future hook
- 6-angle design review: fun factor, historical flavor, edge cases/exploits, documentation quality, system interactions, scalability

**Session 10 — Final 10 Patches + Edge Case Clarifications:**
- Patch 1: Replaced partisan uprising with simpler `plundered: bool` flag
- Patch 2: AI plunder/secure by personality (aggressive→plunder, cautious→secure)
- Patch 3: `supply_capacity` as computed property (not serialized)
- Patch 4: Added economy/treasury/finances free command
- Patch 5: Fixed upkeep timing to income phase at end of turn
- Patch 6: Removed save migration notes (no saves exist)
- Patch 7: Added `_ACTION_DISPLAY_NAMES` requirement to implementation step 16
- Patch 8: Added step 18 for MODDING_FORMAT.md update
- Patch 9: Added bankruptcy → authority drop future hook (§3 + §16)
- Patch 10: Added AI admin scaling note (§11 + §16)
- Clarified 4 edge cases: recruit-without-marshal, multiple AI captures, front-line building risk, bankrupt recruiting
- Final review: 7 questions answered, no remaining contradictions, all serialization accounted for

**Economy spec final state:** 1025 lines, 18 implementation steps, 14 deferred features, all edge cases resolved.

### Feb 5 (Session 7: V2a Smoke Test Bug Fixes)

**4 bugs found during V2a Godot smoke testing, all fixed:**
- **BUG FIX:** Enemy actions showing raw internal names (`stance_change`, `fortify`) in command box. Summary in `turn_manager.py` and independent command report in `executor.py` were using raw action strings. Added `_ACTION_DISPLAY_NAMES` translation dict. Also added missing `unfortify`, `recruit`, `scout` to Godot enemy phase dialog match statement.
- **BUG FIX:** MILD "Field Dispatches" never appearing. `world.advance_turn()` cleared `mild_concerns_this_turn` BEFORE `_execute_end_turn()` could capture them. Fix: save copy before calling `turn_manager.end_turn()`, include in result dict.
- **BUG FIX:** NoneType crash on stance change (`'NoneType' object has no attribute 'lower'`). Parser could return None for stance field. Added guard clause returning clear error instead of crashing.
- **BUG FIX:** Objection firing for impossible actions (defend when already fortified). V2 objection evaluator ran BEFORE action validation. Added pre-validation block for already-defended, already-fortified, already-drilling.

**Proactive pattern hunt (3 additional fixes):**
- **BUG FIX:** Independent command report used raw action names → now uses `_action_display_name()`.
- **BUG FIX:** `_execute_wait()` called with wrong signature in post-objection path (would crash as TypeError). Fixed to match `(marshal, world, game_state)` signature.
- **BUG FIX:** Fortify and drill could trigger objections when already active. Promoted validation before objection check.
- **BUG FIX:** Stance change to current stance (e.g. aggressive while aggressive) could trigger objection before failing. Added already-in-stance pre-validation.

**Defensive comments added** at all fix sites explaining why the code was wrong.

**Follow-up fixes from continued smoke testing (2 bugs):**
- **BUG FIX:** MILD "Field Dispatches" appearing below failed commands (e.g. "ney grumbles" shown even when defend fails). `main.py` had `elif world.mild_concerns_this_turn` fallback that sent stale MILD concerns on every command response. Removed fallback — MILD dispatches now only sent via end_turn result dict path.
- **BUG FIX:** NoneType crash still occurring with Anthropic LLM mode on "ney nuertral". Root cause: `objection_v2.py` used `order.get('target', '').lower()` — but `parser.py:297` explicitly sets `"target": None`, and `.get()` default only applies for MISSING keys, not None values. `None.lower()` crashed. Fixed both instances (lines 707, 768) to `(order.get('target') or '').lower()`. Added 2 regression tests.
- **Test count: 1218 passed, 3 skipped, 0 failures**

**Follow-up fixes from second smoke test round (3 bugs):**
- **BUG FIX:** Post-objection proceed for stance_change consumed only 1 AP instead of variable cost. `_execute_post_objection()` used `world.use_action()` (always 1 AP), ignoring `variable_action_cost`. Now handles variable costs (0-2 AP) matching main execute path.
- **BUG FIX:** AP not checked before objection fires. Player could trigger objection for a 2 AP action with only 1 AP, then "proceed" would fail with AP error. Added AP pre-check in pre-validation block before V2 objection evaluation. Systemic fix: applies to all actions including stance_change variable costs.
- **BUG FIX:** Enemy turn summary not visible in command output after enemy phase dialog dismissed. Added post-dismissal summary output to `_on_enemy_phase_dismissed()` in main.gd so player has text record in command history.
- **Verified:** Already-in-stance pre-validation prevents MILD objection from firing (2 regression tests added).
- **Test count: 1222 passed, 3 skipped, 0 failures**

### Feb 5 (Session 6: Bug Fixes + Roadmap)

**Bug fixes:**
- **BUG FIX:** Defend order allowed when already in defensive stance + fortified. `_execute_defend()` returned `success: True` with `variable_action_cost: 0` (wasted no AP but gave misleading feedback). Now returns `success: False` with clear message.
- **BUG FIX:** Post-turn strategic reports missing after insist/proceed on objection. `/respond_to_objection` endpoint was not passing `strategic_reports` from executor result. Added `strategic_reports` to response dict.

**Roadmap:**
- Moved Voice-to-Text from Post-EA (LOW) to Pre-EA Polish (killer feature). Added architecture notes: Whisper API or browser SpeechRecognition -> existing parser pipeline. ~$0.012/game cost.

### Feb 5 (Session 5: V2a Unit 6 — Integration Wiring)

**Unit 6: V2a Integration Wiring + Test Migration (6 gaps resolved):**
- **Gap 1 (Doc):** Compromise math note for DEVOTED+MODERATE in OBJECTION_V2.md §2.3
- **Gap 2 (idle_turns):** Added `idle_turns` field to Marshal — increments per turn if idle, resets on attack/move. Serialization roundtrip tested. V2b will use for idle objection triggers.
- **Gap 3 (V2 trust scaling):** Wired `calculate_trust_gain()`, `get_insist_penalty()`, `COMPROMISE_TRUST_GAIN` into tactical and strategic objection dicts. Replaced all hard-coded +12/-10/-15/+3 values.
- **Gap 4 (Insist bypass):** Removed V1 disobedience roll from `handle_response()`. Insist always succeeds in V2a. V2b comment block preserved for future defiance mechanic.
- **Gap 5 (V1 evaluate_order shim):** Replaced V1 `evaluate_order()` call with direct `_generate_alternative()` + `_find_compromise()` calls, bypassing V1 severity calculation entirely.
- **Gap 6 (Strategic V2 wiring):** Replaced V1 `check_strategic_objection()` with V2 `evaluate_strategic_situation()` + `apply_mood_variance()`. Added per-marshal popup cap, MILD path for strategic, V1 helpers retained only for option extraction.
- **Test migration:** 9 V1 tests updated to V2 semantics (mock mood variance, relaxed message assertions → concern_level checks). 1 test in `test_strategic_bugfixes.py` updated.
- **Integration tests:** 13 new tests — tactical full path (trust/insist/compromise), strategic full path, MILD no-popup, idle turns (increment/reset/enemy skip/acted flag/serialization/backward compat)
- **Test count: 1216 passed, 3 skipped, 0 failures**

**Unit 7: Godot Frontend:**
- Tone-based objection dialog: border color + header text by trust tier (respectful/firm/challenging/defiant)
- Trust change previews on all tactical objection buttons
- V2 field passthrough: tone, concern_level, trust_gain, insist_penalty, compromise_gain
- MILD "Field Dispatches" in turn log after enemy phase (warm gold, atmosphere text)

**V2a Objection Refactor: COMPLETE** — all 7 units shipped.

### Feb 5 (Session 4: EA Readiness & Vision Assessment)

- EA Readiness audit: full doc review, roadmap restructure
- Map decision: Option C (commission Europe, wire partial ~80-100 regions)
- Map approach: EU4-style bitmap color map (not SVG)
- Coalitions split from Phase 8 to Phase 7
- Phase 12 (Communication cutoff) deferred to Post-EA
- Naval abstraction deferred to Post-EA, Britain as map-absent funder
- Phase 9 (Advisors) minimized: stats + flavor, no action gating
- Phase 11 reworked: vassals + authority-based loyalty, no naval
- Save/Load moved from Pre-EA to Phase 6
- Berthier Parse Recovery moved from Phase 8.5 to Phase 6
- New features added: Campaign Briefing, Marshal Report, Post-battle Analysis, Idle Marshal Objection, Grouchy Moment LLM, Intercepted Dispatches, Napoleon Comparison, LLM feature toggles, Short Waterloo Scenario
- Created TUTORIAL_SCRIPT.md (living document)
- ROADMAP.md fully restructured

### Feb 5 (Session 3: Audit Triage)

**Triaged 15 findings from Enemy AI + V2a audits (3 fixed, 12 tracked):**
- **BUG FIX:** `_failed_action_cooldowns` destroyed every turn — EnemyAI was recreated each turn, resetting cooldowns. Moved to `WorldState.ai_failed_action_cooldowns` (same pattern as `ai_stagnation_turns`). Cooldowns now persist across turns.
- **BUG FIX:** Aggressive retreat: outnumbered 2:1 + high morale fell through to NONE (no concern). Now returns MILD.
- **DOC FIX:** Trust gain spec table in OBJECTION_V2.md used rounded values but code uses `int()` truncation. Updated spec to match code.
- **Tracked:** 7 items to STATUS.md Known Issues, 3 items to ROADMAP.md phase notes, 6 code TODOs added

### Feb 5 (Session 2: Audit Fixes)

**Architecture audit fix session:**
- **BUG FIX:** Cavalry double-increment of `turns_fortified` — was reaching 3-turn limit in 2 turns
- **BUG FIX:** `active_battles` participants used Python `set` (not JSON-serializable) → changed to `list`
- **BUG FIX:** `defense_bonus` type annotation was `int`, actual usage is `float` (0.16 = 16%)
- **BUG FIX:** `just_retreated` legacy flag removed — forced retreat now uses proper `retreating`/`retreat_recovery` system
- **BUG FIX:** Debug command `/debug restless` was setting wrong field (`turns_defensive` instead of `turns_in_defensive_stance`)
- **Dead code removed:** `PERSONALITY_TRAITS` dict, `_action_bonuses`, `turns_defensive` legacy field, `fortify_expires_turn` (always -1), `__main__` test block
- **Serialization:** `_recovery_destination` formalized in `__init__`, `to_dict()`, `from_dict()`
- **Debug prints:** 150+ bare `print()` in world_state.py, turn_manager.py, combat.py → gated behind `debug_print()` (set `INK_DEBUG=0` to silence)
- **Duplicates consolidated:** `ordinal()` function → `backend/utils/__init__.py`; `decay_config` dict → module-level `FORTIFY_DECAY_CONFIG` constant
- **getattr cleanup:** 20+ unnecessary `getattr(self, 'field', default)` → direct `self.field` in marshal.py
- **Doc fixes:** SYSTEMS_REFERENCE.md shock bonus +50% → +20%, `until_destroyed` → `until_marshal_destroyed`, `target_type` values corrected
- **Godot fixes:** Removed unused `fortify_expires_turn` var from map.gd, renamed `turns_defensive` → `turns_in_defensive_stance`

### Feb 5 (Session 1: V2a + Docs)

**V2a Units 4 & 5 (commit e04405b):**
- **Unit 4:** Pipeline integration — V2 evaluators wired into executor.py
  - `evaluate_situation()` + `apply_mood_variance()` replace V1 `evaluate_order()`
  - MILD concerns → append to `world.mild_concerns_this_turn`, continue execution
  - MODERATE+ → per-marshal popup cap, tone/insist_penalty from trust tier
  - WorldState: `mild_concerns_this_turn`, `objection_popups_this_turn` fields
  - main.py: mild_concerns passthrough in response
- **Unit 5:** Added `pending_defensive_vindication` to VindicationTracker
- **Opus 4.6 review fixes:**
  - Fix: `"order"` → `"original_order"` key mismatch (would crash on insist)
  - Fix: `game_state` variable shadowing dropping `debug_mode` key
  - Fix: Removed unused `target` variables in message generators

**V2a Units 1-3:**
- Core data structures (ConcernLevel, TrustTier enums, trust gain/penalty tables)
- Tactical trigger evaluators (personality × situation → ConcernLevel)
- Strategic trigger evaluators (evaluate_strategic_situation dispatcher)
- 119 new tests

**Documentation consolidation:**
- CLAUDE.md trimmed from 1661 → 268 lines
- docs/ consolidated from 21 → 11 active files + 3 archived
- New merged docs: SYSTEMS_REFERENCE.md, OBJECTION_V2.md, ADDING_CONTENT.md

### Feb 4

- Timed HOLD expiry fix, redundant HOLD blocking, Davout HOLD auto-fortify
- Personality-specific HOLD completion messages
- `/debug freeze_enemies` command
- Test count: **1066 passed, 3 skipped**

### Feb 3

- Phase M complete: Strategic Objections (47 tests)
- Strategic objections use probability system (trust, authority, vindication)

### Feb 2

- Phase K playtesting: 8 bugs found and fixed during Godot smoke testing
- SUPPORT auto-follow, morale scaling, sally battle fixes
- Test count: **1004 passed**

### Previous Sessions

- Phase 5.2 Strategic Commands: 100% complete (MOVE_TO, PURSUE, HOLD, SUPPORT)
- Phase 5.3 Enemy AI fixes: stagnation counter, oscillation fixes
- Modding system: 66 tests, validator tool, example mods
- Serialization enforcement: 33 roundtrip tests

---

## Test Count History

| Date | Tests | Notes |
|------|-------|-------|
| Feb 19, 2026 | **2986** | Session 55: Fort degradation reports + decimal cleanup. |
| Feb 19, 2026 | **2987** | Session 54: AI total inaction fix + bombardment display. |
| Feb 18, 2026 | **2987** | Session 53: UI polish (help, unit types, minimize, ammo). |
| Feb 18, 2026 | **2987** | Session 52: Bombardment Part 5 — Godot + Berthier. 37 new tests. |
| Feb 18, 2026 | **2950** | Session 51: Bombardment Part 4 — HOLD + objections. 42 new tests. |
| Feb 18, 2026 | **2908** | Session 50: Bombardment Part 3 — AI bombardment. 24 new tests. |
| Feb 18, 2026 | **2884** | Session 49: Bombardment Part 2 — collateral damage. 23 new tests. |
| Feb 18, 2026 | **2861** | Session 48: Bombardment Part 1 — core resolution. 37 new tests. |
| Feb 18, 2026 | **2827** | Session 44: Artillery frontend + audit. 6 new tests. |
| Feb 18, 2026 | **2821** | Session 43: Artillery intelligence & behavior. 38 new tests. |
| Feb 18, 2026 | **2783** | Session 42: Artillery core mechanics. 86 new tests. |
| Feb 17, 2026 | **2697** | Session 41: Manpower pools. 68 new tests. |
| Feb 17, 2026 | **2629** | Session 40: Strategic reroute fix. 4 new tests. |
| Feb 17, 2026 | **2625** | Session 38b: Bug batch (scout, attrition fog, stale icons). 9 new tests. |
| Feb 17, 2026 | **2611** | Fog of War audit — full coverage. |
| Feb 17, 2026 | **2602** | Garrison balance + map overlay. 14 new tests. |
| Feb 16, 2026 | **2588** | AI Garrison implementation. 29 new tests. |
| Feb 15, 2026 | **2558** | Session 31b: Playtest balance fixes (garrison command, fort degradation). 61 new tests. |
| Feb 15, 2026 | **2497** | Session 39: Balance & AI fixes, capital garrison. 63 new tests. |
| Feb 15, 2026 | **2434** | Session 38: Fog of War map visualization (frontend only). |
| Feb 15, 2026 | **2434** | Session 37: Dev tooling, 5 test files (170 new), ruff, coverage 68%→71%. |
| Feb 12, 2026 | **2130** | Session 34A: Fog of War intel report + filtering + fogged_forces separation. 39 new tests. |
| Feb 12, 2026 | **2091** | Session 33: Fog of War intel data layer + visibility core. 55 new tests (RegionIntel, visibility, decay, serialization). |
| Feb 11, 2026 | **2036** | Session 31: Event log hardening (EL1-EL5) + float leak fix. 9 new tests, 2 bugs fixed. |
| Feb 11, 2026 | **2027** | Session 30: Turn Events Log. 39 new tests (13 event types, 5 helpers, serialization). |
| Feb 11, 2026 | **1988** | Session 29 final: Perspective bugs fixed + fort defender observations. 65 battle report tests total. |
| Feb 11, 2026 | **1962** | Session 29: Berthier's After-Action Report. 39 new tests (snapshots, report generation, observations, integration). |
| Feb 11, 2026 | **1923** | Session 28: Berthier Parse Recovery. 20 new tests (mock templates, prompt builder, integration). |
| Feb 10, 2026 | **1903** | Session 27: Save/Load system. 38 new tests (file I/O, roundtrip, backward compat, API, parser, autosave). |
| Feb 10, 2026 | **1865** | Session 26: Opus audit — 10 P0, 10 P1, 7 P2 fixes. 2 new roundtrip tests, 2 updated. |
| Feb 10, 2026 | **1863** | Session 25: Phase 6.2.H depot forward logistics + smoke test bugfixes. 16 new tests |
| Feb 8, 2026 | **1813** | Phase 6.2.G: AI admin phase, economy command, turn summary financial report. 29 new tests |
| Feb 7, 2026 | **1784** | Phase 6.2.F polish: friendly stable attrition exemption, occupation popup timing, debug commands. 47 new tests |
| Feb 7, 2026 | **1737** | Polish: market building, region hover tooltip, fortification spelling, battle damage fix. 48 new tests |
| Feb 7, 2026 | **1617** | Phase 6.2.D: recruitment rework (morale dilution, stability gates, capital discount). 48 new tests |
| Feb 6, 2026 | **1569** | Phase 6.2.C: stability, war damage, combined income modifiers. 78 new tests |
| Feb 6, 2026 | **1491** | Phase 6.2.B: upkeep, bankruptcy, admin AP. 59 new tests |
| Feb 6, 2026 | **1432** | Phase 6.2.A: region types, income, per-nation gold. 46 new tests |
| Feb 6, 2026 | **1347** | Smoke test bug fixes: cavalry terrain msg, charge redirect, recklessness reset. 13 new tests |
| Feb 6, 2026 | **1334** | Phase 6.1 terrain: 59 data layer + 43 combat + 10 review bug regression tests |
| Feb 6, 2026 | **1222** | AP pre-check, post-objection variable cost, enemy summary, 4 regression tests |
| Feb 5, 2026 | **1218** | Smoke test follow-up: NoneType + stale MILD fixes, 2 regression tests |
| Feb 5, 2026 | **1216** | V2a Unit 6 complete, 13 new integration tests |
| Feb 5, 2026 | **~1203** | Audit fixes (need PyCharm verification) |
| Feb 5, 2026 | **1203** | V2a Units 1-5 complete, Opus review fixes |
| Feb 5, 2026 | 1195 | V2a Units 1-3 (119 new tests) |
| Feb 4, 2026 | 1066 | HOLD improvements, personality benefits |
| Feb 3, 2026 | 1066 | Phase M complete |
| Feb 2, 2026 | 1004 | Phase K playtesting fixes |
| Jan 31, 2026 | 1022 | PURSUE completion fix, code review |
| Jan 30, 2026 | 981 | Doc cleanup session |

