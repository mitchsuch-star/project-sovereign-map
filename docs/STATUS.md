# Ink & Iron: Current Status

> **Updated every session by Claude Code.**
> **Last Updated:** February 21, 2026 (Notification System)

---

## Quick Stats

| Metric | Value |
|--------|-------|
| **Tests Passing** | **3190** (verified, 3 skipped) |

| **Current Phase** | Phase 6.5 **IN PROGRESS** (Bombardment COMPLETE, Pause Menu COMPLETE, Wire Marshal Abilities COMPLETE, Campaign Log COMPLETE, Morning Dispatch COMPLETE, Notification System COMPLETE + AUDITED, 5 items remaining). **Next up: Top Bar Framework + Dispatch (Session A), Strategic Ledger (Session B).** Spec: `docs/TOP_BAR_SPEC.md`. Remaining after: Marshal Management UI, Tooltips, Tutorial Infrastructure, Map Renderer. **Phase 7 Core SCOPED** — 6 sessions (57-61, 64), ~190 new tests. |
| **Blockers** | None |
| **Code Coverage** | ~71% (backend/) |

---

## Next Steps

1. **Top Bar Framework + Dispatch Re-read (Session A)** — Unified top bar (CanvasLayer 75), campaign log refactor (layer 50), notification bar repositioning, input blocking refactor (terminal stays active), dispatch re-read screen, Generals placeholder. Spec: `docs/TOP_BAR_SPEC.md`. ~5 backend tests.
2. **Strategic Ledger (Session B)** — `ledger.py` with 5 sections (forces, territories, economy, intel, manpower), `GET /ledger` endpoint, sub-tabbed Godot screen. ~40 backend tests. Spec: `docs/TOP_BAR_SPEC.md`.
3. **Phase 6.5 remaining after Sessions A+B** — Marshal Management UI, Tooltips, Tutorial Infrastructure, Map Renderer
4. **Phase 7 Core: Multi-Marshal Coordination** — 6 sessions (57-61, 64), ~190 new tests. "Position IS Coordination" — combined arms (+10-20%), relationship-scaled coordination (+3%/+5% per ally), dedicated coordination (+5%/+5% from co-location or SUPPORT), adjacent support (+2% per adjacent), reinforcement (Grouchy Rule), win/loss relationship formula (dynamic relationships). Hard cap: +25% atk/+20% def. Each session includes basic combat display messages. Highest risk: Session 61 (reinforcement + physical relocation). First session: Combined Arms Detection (S57). Spec in `MULTI_MARSHAL_SPEC.md` + `PHASE7_SPEC_AMENDMENTS.md` (audit corrections still apply to all sessions including deferred ones).
5. **Phase 7b (immediately after 7 Core):** Casualty Distribution (S62 — `resolve_battle()` contract change, deferred for playtest data), AI Coordination Enhancements (S63 — P4.6/P4.76/P4.77/P4.78), Full Battle Reports + Berthier Observations (S65), Godot Tooltips + Tutorial + Integration Audit (S66), Tactical Triangle Completion (Square Formation + Artillery SUPPORT auto-bombardment + Artillery Overwatch — linked group), V2b Defiance/Vindication, Jealousy system, Coalition Trigger, Cross-nation coordination (Britain/Prussia), Gneisenau Staff Work (1805 only).

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
- **Manpower Pools:** Nation-level infantry/cavalry reserves gate recruitment. Marshal type auto-determines pool (infantry 10k/200g, cavalry 5k/300g). Stables building (+750 cavalry regen). AI pool/cost awareness. Berthier voice throughout.
- **Artillery Unit Type (Sessions 42-44):** Third marshal type (Drouot/France, PrinceAugust/Prussia). Can't attack after moving, no advance on win, cavalry counter (+30%), 2x fort degradation, -25% defense when moved. Glorious Charge banned, PURSUE blocked. Ranged bombardment: 50% return casualties from adjacent regions. Artillery manpower pool (3k batch, 400g, 300+200 urban regen, 20k cap). Session 2: exhaustion exemption, bombardment streak tracking, Berthier advisory, personality objections, AI positioning/screening/anti-oscillation. Session 3: Godot HUD wiring, full audit, ranged bombardment. 127 tests.

---

## Recent Sessions

### Feb 21 (Notification System Audit — Phase 6.5)

**Post-implementation audit of notification system. 4 bugs fixed, 2 features added.**

**Bug 1 (MEDIUM) — Dispatch whitelist mismatch:** Whitelist referenced `cavalry_defensive_reset` / `cavalry_fortify_reset` but world_state.py emits `cavalry_stance_forced` / `cavalry_fortify_forced`. Cavalry events never appeared in Morning Dispatch. Fixed whitelist + severity list + tests.

**Bug 2 (MEDIUM) — Missing notification passthrough:** 3 endpoints (`respond_to_objection`, `respond_to_glorious_charge`, `strategic_response`) didn't include notifications in response. Combat notifications from these paths were delayed until next `/command`. Fixed: added `world.notifications.has_pending()` check to all 3.

**Bug 3 (LOW) — Notification accumulation:** Bankruptcy notifications fired every turn at same tier (5 turns = 5 notifications). Nation eliminated fired every enemy phase. Fixed: `last_bankruptcy_notification_tier` (resets when bankruptcy ends) and `eliminated_nations_notified` set (first detection only). Both serialized.

**Bug 4 (LOW) — Dead whitelist entries:** Removed `fortify_complete` and `fortify_started` from dispatch whitelist (never emitted by any backend code).

**Feature: Turn display in Godot:** Expanded notification panel now shows "(Turn X)" between title and dismiss button.

**Feature: Manpower auto-dismiss:** `dismiss_by_type(type, filter_fn)` method on NotificationCollector. When `manpower_replenished` fires, auto-dismisses matching `manpower_depleted` notification for same pool type.

**Tests:** 19 new (6 cavalry whitelist, 5 bankruptcy tier-change, 3 nation-eliminated, 3 dismiss_by_type, 2 manpower auto-dismiss). **3190 total passing**, 3 skipped, 0 regressions. Serialization enforcement 16/16.

### Feb 21 (Notification System — Phase 6.5)

**EU4-style persistent notification bar for important game events.**

**New files:**
- `backend/notifications.py` — `NotificationPriority` enum (NORMAL/HIGH/CRITICAL), `create_notification()` factory, `NotificationCollector` class (add, dismiss, serialize). 10 notification type constants.
- `godot-client/project-sovereign/scenes/notification_bar.tscn` + `scripts/notification_bar.gd` — Control node (not CanvasLayer) at top-right below LOG button. Color-coded icon buttons per priority (red/orange/blue). Click to expand details panel, X to dismiss. Calls backend dismiss endpoint.
- `tests/test_notifications.py` — 51 tests covering priority enum, factory, collector, WorldState integration, 6 trigger integration tests, dispatch severity/whitelist.

**Backend — 9 notification triggers:**
1. Strategic order complete (HIGH) — `strategic.py _complete_order()`
2. Forced retreat + order voided (CRITICAL) — `executor.py _apply_forced_retreat_or_break()`, both retreat and broken paths
3. Friendly fire trust (HIGH) — `executor.py _execute_bombardment()` collateral loop
4. Reckless cavalry action (CRITICAL) — `world_state.py _process_reckless_cavalry_turn_start()`, both charge and move
5. Counter-punch earned (HIGH) — `combat.py` flag in result_dict → `executor.py _process_combat_notifications()`
6. Manpower depleted/replenished (HIGH/NORMAL) — `executor.py _execute_recruit()` + `world_state.py _process_manpower_regen()`
7. Enemy nation eliminated (NORMAL) — `turn_manager.py`
8. Bankruptcy tier escalation (HIGH tier 1, CRITICAL tier 2-3) — `world_state.py process_bankruptcy_desertion()`
9. Drill cancelled (HIGH) — `combat.py` flag → `executor.py _process_combat_notifications()`

**API wiring:**
- Notifications included in ALL `/command` response paths (8 early-return paths + final response)
- `POST /notifications/dismiss` — dismiss by ID or "all"
- `GET /notifications` — get pending list

**Dispatch fixes (Task 1 & 2):**
- Fixed severity: 7 types promoted to warning (fortify_decayed, fortify_collapsed, counter_punch_expired, capital_proximity_alert, auto_glorious_charge, reckless_move, reckless_no_target), 1 to good (broken_recovered)
- Wired `_DISPATCH_EVENT_TYPES` whitelist filter (was dead code), expanded from 14 to 28 event types

**Godot wiring:**
- `api_client.gd`: `dismiss_notification()`, `dismiss_all_notifications()`
- `main.gd`: notification bar loaded in `_ready()`, updated in `_on_command_result()` before enemy phase check

**Tests:** 51 new. **3171 total passing**, 3 skipped, 0 regressions.

### Feb 20 (Morning Dispatch — Phase 6.5)

**Berthier's Morning Dispatch: structured turn-start briefing rendered as terminal output.**

Replaces "Campaign Briefing" and "Marshal Report" roadmap items with a single integrated dispatch.

**New file:** `backend/game_logic/dispatch.py` — `build_morning_dispatch(world)` returns structured dict with four sections:
- **SITUATION:** Player/enemy region counts, treasury with delta, fog-filtered enemy strength ratio (estimated from intel band midpoints for PARTIAL/STALE, exact for FULL, zero for UNKNOWN). Bankrupt flag.
- **MARSHAL STATUS:** Per-French-marshal table: name, location, strength, derived status (broken > retreating > strategic > drilling > fortified > artillery > idle_restless > awaiting), trust/morale warnings.
- **INTELLIGENCE:** Fog-filtered enemy sightings aggregated from RegionIntel. Deduplicated by marshal name (best visibility wins). Strength displayed as exact number (FULL), band string (PARTIAL), or frozen snapshot (STALE).
- **Berthier's closing note:** Priority-based template: broken marshal > bankrupt > treasury bleeding > aggressive idle 4+ > all ready > default.

**Wiring:** Both end-turn paths (manual `_execute_end_turn` and auto-advance when AP exhausted) build and attach `morning_dispatch` to result. `main.py` passes through to Godot. Godot `_display_morning_dispatch()` renders with BBCode in `_display_result()` after `_display_turn_change()`.

**Godot:** `COLOR_BERTHIER` and `COLOR_OBSERVATION` promoted to class-level constants. ASCII status icons (safe for all fonts). Column alignment via space padding.

**Design decisions:**
- Enemy strength is fog-filtered (band midpoints for PARTIAL/STALE) — intentionally underestimates when visibility is low (cost of poor intelligence). Shown as "Estimated enemy strength: X% of French forces."
- Neutral regions (controller=None) counted as neither player nor enemy.
- Broken/retreating marshals excluded from French strength total.
- No new endpoints, no new Godot scenes — terminal output only.

**Display ordering:** Dispatch renders LAST (after enemy phase popup dismiss and strategic reports), right before player gets control. Tactical events (attrition, construction, etc.) absorbed into dispatch's TURN EVENTS section — no more ugly standalone lines. Enemy phase text removed from terminal (popup is sufficient, campaign log has the full record).

**Tests:** 57 new (situation, fog-filtered strength, marshal status, intelligence, turn events, Berthier note, integration, no-floats enforcement). **3120 total passing**, 3 skipped, 0 regressions.

### Feb 20 (Campaign Log Polish — Phase 6.5)

**Fixed expand/collapse bug, added nation tags to one-liners, improved event formatting.**

**Godot fix (campaign_log.gd):**
- **Expand/collapse bug:** `queue_free()` on re-open left dying nodes in tree, causing name collisions. New nodes got auto-renamed, so `get_node_or_null()` found the wrong (dying) container. Fix: `remove_child()` before `queue_free()` so names are immediately freed.
- **Empty turn hiding:** Turns with 0 visible events after fog filtering are now skipped entirely.
- **Turn 0 display:** Shows "Turn 0 — Setup" instead of plain "Turn 0".

**One-liner formatting (campaign_log.py):**
- **Nation tags on all marshal names:** `Ney (France) attacked Wellington (Britain)` — player can identify friend/foe at a glance without memorizing rosters. Uses `_name_tag()` helper; graceful fallback when nation field is missing.
- **Battle:** Now shows both sides' casualties: `(8,000 / 5,000 casualties)` instead of just attacker losses.
- **Retreat:** Includes destination: `retreated from Waterloo to Paris`.
- **Marshal recovered:** Includes location when available.
- **Region captured:** Shows method: `Brussels captured by France (secure)`.
- **Objection:** Shows action and resolution: `Ney objected to attack (overruled)`.
- **Strategic order:** Humanized order type: `move to` instead of `MOVE_TO`.

**Endpoint (main.py):**
- Empty turns (0 events) filtered from response before sending to Godot.

**Tests:** 3063 passing (57 campaign log, updated assertions), 3 skipped. Zero regressions.

### Feb 20 (Campaign Log — Phase 6.5)

**Fog-filtered campaign event log with Godot overlay. Player can browse all narrative events grouped by turn.**

**New files:**
- `backend/campaign_log.py` — 14-type whitelist, fog filter (reuses `get_region_intel()`), category mapping, one-liner formatter with safe `.get()` defaults
- `godot-client/project-sovereign/scenes/campaign_log.tscn` + `scripts/campaign_log.gd` — CanvasLayer 102 overlay, turn-grouped expandable sections, BBCode events with category-colored icons, click-to-close
- `tests/test_campaign_log.py` — 57 tests (type whitelist, fog filtering, one-liner formatting, safe defaults, endpoint structure)

**Backend:**
- `GET /campaign_log` endpoint — groups events by turn descending, strips `battle_report`, wraps numbers in `int()`, adds `display` one-liner + `category`
- Bankruptcy events always shown (public knowledge — the world would know)
- Added `location` field to `marshal_recovered` and `desertion` events in `world_state.py` — previously these enemy events were invisible in the campaign log due to missing region data for fog checks

**Godot:**
- LOG button (top-right, gold text) + L key toggle + Esc to close
- Expand/collapse per turn (most recent expanded by default)
- Blocked while pause menu open and vice versa
- `api_client.gd` — `get_campaign_log()` method

**Event categories (14 types):**
- Combat: battle, bombardment, retreat, marshal_broken, marshal_recovered
- Territory: region_captured
- Economy: recruitment, building_started, building_completed, building_damaged, bankruptcy, desertion
- Command: objection, strategic_order

**Fog rules:** Player events always shown. Battles need player marshal OR FULL visibility. Retreat/broken/recovered need PARTIAL+. Enemy economy needs PARTIAL+. Bankruptcy always visible. Objections/strategic orders always visible.

**Tests:** 3063 passing (+57 new), 3 skipped. Zero regressions.

---

### Feb 20 (Wire Marshal Abilities)

- **Drouot "Sage of the Grand Army":** Fort degradation 10% → 15% on attack (combat.py degradation block)
- **Wellington "Reverse Slope Defense":** +5% flat defense always (marshal.py get_defense_modifier, Golden Rule #1)
- **Blucher "Vorwärts!":** +3k pursuit casualties on enemy forced retreat, floor 1000 (combat.py pursuit block)
- **Uxbridge "Pursuit Master":** +5k pursuit casualties on retreat, cavalry-only, floor 1000 (combat.py pursuit block)
- **Gneisenau "Staff Work":** Deferred to Phase 7 Session 58 (needs coordination transient fields)
- Updated all ability effect strings from TODO to actual descriptions
- New result dict fields: `drouot_ability_triggered`, `pursuit_damage`, `pursuit_message`
- Moved `attacker_won`/`attacker_lost` computation earlier in resolve_battle() for pursuit access
- Tests: 36 → 54 in test_marshal_abilities.py (+18 new tests), full suite 3006 passed
- Map Renderer roadmap expanded to 43-item transition plan (art, sprites, code refactor)

### Feb 20 (Phase 7 Scope Decision — Core/7b Split)

**Scoped Phase 7 from 10 sessions to 6-session Core + deferred 7b.**

**Phase 7 Core (6 sessions):** 57 (Combined Arms), 58 (Coordination + Hard Cap), 59 (Dedicated Coordination), 60 (Adjacent Support), 61 (Reinforcement + Grouchy Rule), 64 (Win/Loss Relationships). ~190 tests. Each session includes basic combat display messages — no separate presentation session.

**Deferred to Phase 7b:** 62 (Casualty Distribution — `resolve_battle()` contract change, benefit from playtest data), 63 (AI Coordination Enhancements — AI benefits passively from co-location already), 65 (Full Battle Reports), 66 (Godot Tooltips/Tutorial/Audit).

**Rationale:** Core delivers all player-facing coordination mechanics + the Grouchy Rule + dynamic relationships. Session 62 deferred because (a) highest-risk contract change in the spec, (b) coordination works without it (allies provide bonuses, primary combatant absorbs casualties), (c) playtest data should inform proportional distribution. Session 63 deferred because AI already benefits from passive coordination — deliberate coordination matters more at 80+ regions. Session 64 kept because static relationships undermine the "marshals as personalities" thesis — dynamic arcs (Rival→Professional through shared victories) are core to the game's identity at minimal implementation cost (25 tests, self-contained formula).

**Phase 7b ships immediately after 7 Core playtesting,** before Phase 8 (Diplomacy).

**Docs updated:** CLAUDE.md, ROADMAP.md, STATUS.md. No new amendment file — scope decisions live in planning docs. Spec (`MULTI_MARSHAL_SPEC.md`) and amendments (`PHASE7_SPEC_AMENDMENTS.md`) unchanged — their technical content applies regardless of scheduling.

**Tests:** 2987 passed, 3 skipped. No code changes — planning only.

---

### Feb 20 (Phase 7 Pre-Implementation Audit)

**Comprehensive audit of Phase 7 Multi-Marshal Coordination spec against existing codebase.**

**New file:** `docs/PHASE7_SPEC_AMENDMENTS.md` — authoritative amendments document. Where it conflicts with original spec, amendments win.

**Audit scope:** Verified all integration points across `marshal.py`, `combat.py`, `executor.py`, `world_state.py`, `enemy_ai.py`, `objection_v2.py`, `region.py`, `battle_report.py`, `test_serialization_enforcement.py`.

**Findings (20 total):**
- **3 Critical:** (C1) `resolve_battle()` has 5 side-effect categories, not 2 — `apply_casualties=False` must defer morale, battles_won/lost, counter_punch, recklessness in addition to strength and retreat. (C2) Victor determination is wrong when `apply_casualties=False` — must use projected strength, not actual. (C3) Wellington-Blucher coordination example impossible — different nations can't coordinate in Phase 7.
- **7 Design Gaps:** (D1) `holding_position` bug when SUPPORT replaces HOLD. (D2) Who gets battles_won/lost in coordinated battles. (D3) Hostile + SUPPORT = Participating for casualties but 0% coordination. (D4) Ordered pairs for relationship formula. (D5) Transient fields bypass serialization via getattr pattern. (D6) Tutorial fires player-side only. (D7) Reinforcer retreat location timing.
- **3 Interesting (keep):** (I1) France exclusive 3/3 combined arms. (I2) Ney-Davout 15% from hatred. (I3) Devoted reinforcement 95% reliable with 1-in-20 fumble roll.
- **7 Minor:** Formula wording, threshold notes, cap documentation, serialization pattern, template placeholders, cross-nation TODO comment.

**Session readiness:** Sessions 57-60 ready immediately. Sessions 61-62 (highest risk) require C1/C2 amendments. All findings documented with specific session tags.

**Tests:** 2987 passed, 3 skipped. No code changes — audit only.

---

### Feb 19 (Session 56: Pause Menu — Phase 6.5)

**Implemented Smart Esc pause menu overlay.**

**New files:**
- `pause_menu.tscn` + `pause_menu.gd` — CanvasLayer 101, modal overlay with darkened background
- 4 buttons: Save Game (quicksave via existing endpoint), Load Game (opens existing load dialog), Settings (stub label), Quit to Desktop

**Smart Esc logic (main.gd `_unhandled_input`):**
- If command_input focused → unfocus it (existing behavior, unchanged)
- If pause menu open → close it
- If no dialog open → open pause menu
- All hotkeys (E, Tab) blocked while pause menu is open

**Visual style:** Matches existing Ink & Iron theme — dark panel (0.08, 0.1, 0.15), gold border (0.85, 0.75, 0.55), cream text, Quit button in muted red. Click outside modal closes it.

**Tests:** 2987 passed, 3 skipped. Zero regressions (backend-only tests, Godot changes are frontend-only).

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
| Marshal ability dicts mostly decorative | Low | Only Ney's "Bravest of the Brave" wired in combat.py. All others (Drouot, Wellington, Blucher, Uxbridge, Gneisenau) planned for Phase 6.5 ability wiring pass. |
| `full_game.py` dead code with stale terrain | Low | 3 `resolve_battle()` calls hardcode `terrain="open"`. File is dead code. |
| Multi-nation battle report perspective | Low | combat.py hardcodes player_nation="France". Post-EA requires threading world.player_nation. |
| France hardcoded as player nation | Low | Multiple systems assume France. Post-EA multi-nation play requires threading player_nation throughout. |
| ~~`holding_position` not cleared on strategic order replacement~~ | ~~Medium~~ | **FIXED** (Feb 20). `executor.py:4172-4178` now clears `holding_position` and `hold_region` when HOLD is replaced by another strategic order. Regression test added. See `PHASE7_SPEC_AMENDMENTS.md` D1. |
| `resolve_battle()` has 5 categories of side effects | High | When Phase 7 adds `apply_casualties=False`, must defer: strength, morale, battles_won/lost, counter_punch, recklessness. Spec originally only identified 2. See `PHASE7_SPEC_AMENDMENTS.md` C1. |
| Cross-nation coordination impossible (Britain/Prussia) | Medium | All coordination eligibility requires same nation. Wellington-Blucher Devoted relationship is decorative in Phase 7. Deferred to Phase 7b with Coalition Trigger. See `PHASE7_SPEC_AMENDMENTS.md` C3. |
| Missing SUPPORT objection triggers | Low | `objection_v2.py` only has SUPPORT path danger check (cautious). Missing: aggressive objects to defensive SUPPORT, cautious objects to supporting reckless ally. Add in Phase 7 Session 59. |

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
| Phase 7 spec | `MULTI_MARSHAL_SPEC.md` |
| Phase 7 audit amendments | `PHASE7_SPEC_AMENDMENTS.md` |
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
