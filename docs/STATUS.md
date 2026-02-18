# Ink & Iron: Current Status

> **Updated every session by Claude Code.**
> **Last Updated:** February 17, 2026

---

## Quick Stats

| Metric | Value |
|--------|-------|
| **Tests Passing** | **2629** (verified, 3 skipped) |
| **Current Phase** | Phase 6: **IN PROGRESS** (2 items remaining: Manpower Pools, Artillery Unit Type) |
| **Blockers** | None |
| **Code Coverage** | **71%** (backend/) |

---

## Next Steps

1. **Manpower Pools** (Medium) — Separate pool types: Infantry, Cavalry, Artillery
2. **Artillery Unit Type** (Medium) — Combat buffs like cavalry system
3. **Pause menu** — Phase 6.5, Esc → Save/Load/Settings/Quit

---

## Phase 6 Summary

All major Phase 6 features shipped:

- **Terrain (6.1):** 6 terrain types, weighted pathfinding, cavalry terrain scaling, charge blocking
- **Economy (6.2):** Region types, income/upkeep, stability, war damage, recruitment rework, buildings (4 types), supply limits, movement attrition, contested capture, AI admin phase — audited and balanced (Session 26)
- **Save/Load:** Manual save/load + autosave, pause menu deferred to 6.5
- **Berthier Parse Recovery:** In-character error messages for unparseable commands
- **Battle Reports:** Template-based post-battle analysis with modifier snapshots, perspective-aware observations
- **Turn Events Log:** 13 event types, structured logging, hardened (EL1-EL5)
- **Fog of War (Sessions 33-36):** Intel data model, visibility tiers (FULL/PARTIAL/STALE/LAST_KNOWN/UNKNOWN), decay, watchtower building, strategic fog filtering, scout persistence, map visualization with fog overlay + fogged icons
- **Reinforcements, Attrition, City Fortification**
- **Player Garrison Command:** 2 AP, cap 3/nation, map overlay
- **Enemy AI Garrison (P6.75):** Building Blocks, 20k threshold, 1/nation/turn, P4.25 sub-5k awareness

---

## Recent Sessions

### Feb 17 (Session 39: Strategic Reroute Wastes 2 Turns)

**3 bugs fixed, 4 new tests.**

**Bug 1 — Auto-upgrade init skips reroute (executor.py):**
- When a move auto-upgraded to MOVE_TO and the first step was blocked, the code just `break`ed without calling `_handle_first_step_blocked()`. Order created with blocked path, wasting the init turn. Fix: calls `_handle_first_step_blocked()` (same as older init path), updates local `path` reference after reroute for cavalry correctness.

**Bug 2 — Strategic MOVE_TO/PURSUE reroute doesn't move (strategic.py):**
- Turn-by-turn handler called `_handle_blocked_path()` and returned immediately after reroute. Path updated but no movement — wasted another turn. Fix: after literal reroute (`action == "reroute"`), attempts move on first step of new path before returning. Applied to both MOVE_TO and PURSUE handlers.

**Bug 3 — Reroute ignores just-discovered blocked region (strategic.py):**
- `_handle_blocked_path` used fog-aware `_get_enemy_occupied_regions` for avoid list, which could miss the blocked region if fog hadn't been updated yet. Physical encounter is authoritative. Fix: always include `blocked_region` in avoid list.

**Combined effect:** Literal marshal rerouting now reroutes AND moves on the same turn (1 turn instead of 3).

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

### Feb 15 (Session 31: Playtest Balance Fixes)

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

## Known Issues

| Issue | Severity | Notes |
|-------|----------|-------|
| V1 global objection cap still active for strategic path | Low | `disobedience.py:25` MAX_MAJOR_OBJECTIONS_PER_TURN=2. V2 per-marshal cap is now authoritative; V1 cap is redundant backstop. Remove in V2b cleanup. |
| No mid-objection save/load roundtrip test | Low | Serialization enforcement confirms fields exist, but no test with populated V2 pending_objection. |
| Missing AI test coverage for P3, P4.75, P7 | Medium | P3 (threat response), P4.75 (ally support), P7 (strategic movement) have zero direct unit tests. |
| Residual 2-turn fortify oscillation possible | Low | `_unfortified_this_turn` only prevents same-turn re-fortify. Stagnation counter is backstop. TODO in `enemy_ai.py` at P3.5. |
| `requires_input` interrupt blocks later marshals | Low | `strategic.py:119` stops processing ALL further marshals when one requires input. TODO in `strategic.py`. |
| Marshal ability dicts mostly decorative | Low | Only Ney's "Bravest of the Brave" wired in combat.py; others are TODO. |
| `full_game.py` dead code with stale terrain | Low | 3 `resolve_battle()` calls hardcode `terrain="open"`. File is dead code. |
| Multi-nation battle report perspective | Low | combat.py hardcodes player_nation="France". Post-EA requires threading world.player_nation. |
| France hardcoded as player nation | Low | Multiple systems assume France. Post-EA multi-nation play requires threading player_nation throughout. |

---

## Quick Commands

```bash
pytest tests/ -v                          # Full suite
pytest tests/ -v --tb=no -q              # Quick count
pytest tests/test_objection_v2.py -v     # V2 tests only
python backend/main.py                    # Backend on port 8005
```

---

## Document Map

| Need | Read |
|------|------|
| Phase timeline | `ROADMAP.md` |
| Game systems reference | `SYSTEMS_REFERENCE.md` |
| Enemy AI | `ENEMY_AI_REFERENCE.md` |
| V2b objection preview | `OBJECTION_V2.md` |
| Save format | `SAVE_FORMAT_REFERENCE.md` |
| Fog of war spec | `FOG_OF_WAR_SPEC.md` |
| Adding content | `ADDING_CONTENT.md` |
| Game vision | `VISION.md` |
| Future concepts | `FUTURE_DESIGN.md` |
| Modding | `MODDING_FORMAT.md` |
| Manual testing | `MANUAL_TEST_PLAN.md` |
| Tutorial content | `TUTORIAL_SCRIPT.md` |
| Playtest prompt | `PLAYTEST_EVALUATION_PROMPT.md` |
| Session history (archived) | `archive/SESSION_HISTORY.md` |
