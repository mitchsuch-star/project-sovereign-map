# Ink & Iron: Current Status

> **Updated every session by Claude Code.**
> **Last Updated:** February 11, 2026
> **Last Session:** Session 29 — Berthier's After-Action Report

---

## Quick Stats

| Metric | Value |
|--------|-------|
| **Tests Passing** | **1988** (verified, 3 skipped) |
| **Current Phase** | Phase 6: Post-Battle Analysis **COMPLETE** |
| **Blockers** | None |
| **Phases Complete** | 1, 2, 2.5, 2.9, 3, 4, 5.1, 5.2, 5.3, M, V2a, 6.1, 6.2, 6-Save/Load, 6-Berthier, 6-BattleReport |

---

## Active Work

**Phase 6: Core Campaign — Terrain 6.1 COMPLETE. Economy 6.2 COMPLETE + AUDITED. Save/Load COMPLETE.**

- [x] Economy spec design (3 review rounds, 1025 lines, 17 sections)
- [x] Cohesion assessment → deferred to FUTURE_DESIGN.md
- [x] COHESION_FUTURE_DESIGN.md deleted (content merged into FUTURE_DESIGN.md)
- [x] Terrain spec design (TERRAIN_SPEC.md — 569 lines, 14 sections)
- [x] Terrain codebase analysis (5 findings, all resolved)
- [x] Terrain final design review (6 types confirmed, GO verdict)
- [x] **Session 6.1.A: Terrain Data Layer** — constants, Region field, computed properties, REGIONS_DATA, 59 tests
- [x] **Session 6.1.B: Combat Integration** — defense bonuses, cavalry terrain scaling, charge blocking, 5 executor call sites, 43 tests
- [x] **6.1.B Opus Code Review** — found 3 bugs (auto-charge terrain, full_game.py dead code, charge safety net)
- [x] **6.1.B Bug Fixes** — all 3 bugs fixed, 10 regression tests, full suite green (1334 pass)
- [x] **6.1.B Smoke Test** — 3 Godot smoke test bugs fixed, charge redirect popup added, 13 regression tests (1347 pass)
- [x] **6.1.B Polish** — cavalry terrain flavor in Godot battle UI, recklessness color tags, charge redirect sort logic, auto-charge message bug fix
- [x] **Session 6.1.C: Weighted Pathfinding** — Dijkstra pathfinding, MOVE_TO+HOLD terrain-aware routing, AI retreat weighted distance, terrain display in scout/status, 39 tests (1386 total)
- [x] **Session 6.2.A: Region Types + Income + Gold** — 5 region types, differentiated income, per-nation gold tracking, 46 tests (1432 total)
- [x] **Session 6.2.B: Upkeep + Bankruptcy + Admin AP** — upkeep calculation, bankruptcy desertion, admin AP pool, income phase refactor, 59 tests (1491 total)
- [x] **Session 6.2.C: Stability + War Damage** — region stability tiers, war damage, combined income modifiers, battle effects, turn resolution, 78 tests (1569 total)
- [x] **Session 6.2.D: Recruitment Rework** — morale dilution, stability gates, capital discount, updated events, 48 tests (1617 total)
- [x] **Session 6.2.E: Plunder/Secure + Buildings** — capture choice popup, plunder/secure effects, building system (3 types), fortification combat bonus, training ground morale, repair command, 72 tests (1689 total)
- [x] **Session 21: Polish** — market building (4th type), region hover tooltip, fortification spelling robustness, battle damage fix, 48 tests (1737 total)
- [x] **Session 22: Phase 6.2.F** — supply limits, movement attrition, contested capture, 43 tests (1780 total)
- [x] **Session 22b: 6.2.F Polish** — friendly stable attrition exemption, occupation popup timing fix, debug commands, 47 tests (1784 total)
- [x] **Session 23: Phase 6.2.G** — AI admin phase, economy command, turn summary financial report, occupation UI wiring, 29 tests (1813 total)
- [x] **Session 24: Economy Audit Fixes** — Coalition territory viability (Britain/Prussia get Milan/Bavaria/Vienna), starting gold rebalance (Britain 1500, Prussia 800), plunder 1.75x multiplier, AI recruitment threshold 0.50, training ground +30% buff, AI market/depot building, AI supply attrition P0.5 check, 30 tests (1844 total), Geneva→Britain, gold expenditure tracking, two-tier AI recruitment
- [x] **Session 25: Phase 6.2.H + Bugfixes** — Supply depot forward logistics (0.5x attrition), AI border depot placement, 16 tests (1863 total). Smoke test bugfixes: recruit targeting, build parser, supply attrition display, enemy phase labels, bankruptcy warning wiring, build typo tolerance

---

## Recently Completed

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
- Naval abstraction deferred to Post-EA, Britain as off-map funder
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

---

## Known Issues

| Issue | Severity | Notes |
|-------|----------|-------|
| ~~V1 `handle_objection_response` still uses V1 trust values~~ | ~~Fixed~~ | Unit 6 Gap 3: Wired V2 scaled trust gain/penalty into objection dicts |
| ~~Strategic objections still use V1 `check_strategic_objection()`~~ | ~~Fixed~~ | Unit 6 Gap 6: V2 `evaluate_strategic_situation()` now authoritative. V1 retained only for option extraction. |
| ~~V1 `evaluate_order()` still called for alternative generation~~ | ~~Fixed~~ | Unit 6 Gap 5: Replaced with direct `_generate_alternative()` + `_find_compromise()` calls |
| V1 global objection cap still active for strategic path | Low | `disobedience.py:25` MAX_MAJOR_OBJECTIONS_PER_TURN=2. V2 per-marshal cap is now authoritative for strategic; V1 cap is redundant backstop. Remove in V2b cleanup. |
| ~~No integration tests for V2 tactical pipeline~~ | ~~Fixed~~ | Unit 6: 13 integration tests cover full tactical path, strategic path, MILD path, insist path, idle turns |
| No mid-objection save/load roundtrip test | Low | Serialization enforcement confirms fields exist, but no test saves/loads with populated V2 pending_objection. |
| Missing AI test coverage for P3, P4.75, P7 | Medium | P3 (threat response), P4.75 (ally support), P7 (strategic movement) have zero direct unit tests. |
| Residual 2-turn fortify oscillation possible | Low | `_unfortified_this_turn` only prevents same-turn re-fortify. Next-turn re-fortify→P3.5 unfortify cycle possible. Stagnation counter is backstop. TODO in `enemy_ai.py` at P3.5. |
| `requires_input` interrupt blocks later marshals | Low | `strategic.py:119` stops processing ALL further marshals when one requires player input. Later marshals' strategic orders starve if early marshal always has interrupts. TODO in `strategic.py`. |
| ~~Clarification popup for other literal actions~~ | ~~Fixed~~ | Works for all strategic types + attack-without-target (verified Feb 5) |
| ~~Windows Store Python broken~~ | ~~Fixed~~ | venv working, tests run from CLI |
| Marshal ability dicts mostly decorative | Low | Only Ney's "Bravest of the Brave" is wired up in combat.py; others are TODO (personality mechanics DO work separately) |
| `full_game.py` dead code with stale terrain | Low | 3 `resolve_battle()` calls hardcode `terrain="open"`. File is dead code (nothing imports it). TODO comments added at all 3 sites. |
| ~~Battle report not shown during enemy phase~~ | ~~Fixed~~ | Added `_format_berthier_report()` to `enemy_phase_dialog.gd`. Battle reports now display in enemy phase dialog. |
| ~~Auto-charge battle report not displayed~~ | ~~Fixed~~ | Hoisted `battle_report` from tactical events to result level in both `_execute_end_turn()` and auto-advance path in `executor.py`. |
| Multi-nation battle report perspective | Low | combat.py hardcodes player_nation="France" default. When Coalition nations become playable (Post-EA), thread world.player_nation through resolve_battle() into generate_battle_report(). See test_combat_resolver_uses_default_france for exact wiring point. |
| France hardcoded as player nation | Low | Multiple systems assume France is the player nation (world_state.py player_nation default, combat.py battle report perspective, AI decision tree). Post-EA multi-nation play requires threading player_nation throughout. |

---

## Next Session Priorities

1. ~~**Post-Battle Analysis**~~ — **DONE** (Session 29). battle_report.py module with 15 observation priorities, perspective-aware for attacker/defender, 65 tests, 2 perspective bugs fixed. Known wiring gap: combat.py hardcodes player_nation="France" — documented for post-EA multi-nation.
2. **Phase 6 remaining items** — Fog of War, Manpower Pools, Artillery Unit Type, Turn Events Log (see ROADMAP.md Phase 6 table). War Score and Threat Indicator moved to Phase 8 (Diplomacy).
3. **Pause menu planning** — Phase 6.5 needs Esc → Save/Load/Settings/Quit menu before 1805 EA. Plan scope.
4. Commission Europe map art (start search for artist).

### Phase 6.2 Economy Audit Findings

| # | Priority | Finding | Details |
|---|----------|---------|---------|
| 1 | **CRITICAL** | Coalition economy nonviable | Britain nets -330/turn, Prussia -400/turn. Spec balance table (Section 17 of ECONOMY_SPEC.md) assumed ~400/turn Britain income, ~300/turn Prussia — actual map gives Britain 100/turn (2 rural regions) and Prussia 100/turn (1 town). Prussia bankrupt turn 1, Britain by turn 3. Options: more starting territory, smaller Coalition armies, subsidy mechanic, or lower upkeep. |
| 2 | ~~HIGH~~ | ~~AI admin break-on-failure~~ | **FIXED in Session 23.** Changed `break` to `skip_actions` set pattern in `enemy_ai.py:3308`. |
| 3 | **MEDIUM** | Reconquest stability bonus missing | `capture_region()` in `world_state.py` always sets stability to 25. Spec says reconquering your OWN territory should set stability 60 (citizens welcome you back). Check `capture_region()` and `_apply_occupation_capture_effects()`. |
| 4 | **MEDIUM** | Plunder gold too low | Plunder gives 100% base income. Secure yields ~935g over 10 turns vs Plunder's ~515g — not a real tradeoff. Raise to 150-200% base income. See `_apply_plunder()` in `executor.py`. |
| 5 | **LOW** | AI recruitment threshold too conservative | AI only recruits below 40% starting strength (`enemy_ai.py:_find_weakest_marshal_for_admin`). Wellington must fall to 27k (from 68k) before AI recruits. Raise to 50-60%. |
| 6 | **LOW** | Training Ground underwhelming | +15% morale on recruits (40%->55%) translates to ~4% morale difference in practice. Consider secondary benefit (e.g., +5% morale recovery/turn for armies in region). See `executor.py:_execute_recruit`. |
| 7 | **LOW** | AI only builds fortifications | `_find_unfortified_border_region` in `enemy_ai.py` only builds forts. AI never builds markets/depots. Coalition needs markets more than forts given their income crisis. |

---

## Queued Design Items

*All 3 items from Session 20 implemented in Session 21. Section cleared.*

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
| Terrain spec (Phase 6.1) | `TERRAIN_SPEC.md` |
| Economy spec (Phase 6.2) | `ECONOMY_SPEC.md` |
| Phase 6 implementation plan | `PHASE6_IMPLEMENTATION_PLAN.md` |
| Phase timeline | `ROADMAP.md` |
| Game systems reference | `SYSTEMS_REFERENCE.md` |
| Enemy AI | `ENEMY_AI_REFERENCE.md` |
| V2 objection design | `OBJECTION_V2.md` |
| Save format | `SAVE_FORMAT_REFERENCE.md` |
| Adding content | `ADDING_CONTENT.md` |
| Game vision | `VISION.md` |
| Future concepts | `FUTURE_DESIGN.md` |
| Modding | `MODDING_FORMAT.md` |
