# Systems Audit Fix Plan

**Source:** `audit-report-systems.md` (275 findings across 22 passes)
**Created:** March 24, 2026
**Audit scope:** All non-diplomacy systems + game design + code quality + exploits

## Overview

275 total findings. After deduplication (P13/P14 overlap heavily on the same root cause), ~140-150 unique issues.

| Category | Count | Action |
|----------|-------|--------|
| Unambiguous code bugs | ~45 | Fix after verifying |
| Probable bugs needing evaluation | ~25 | Evaluate first, decide |
| Balance/exploit (gameplay changes) | ~15 | Design gate required |
| Architecture/refactoring | ~25 | Optional, lower priority |
| Positive findings / observations | ~75 | No action |
| Future design features | ~15 | Future phase, not this plan |

---

## Decisions

### Balanced/Loyal personality placeholders — REMOVE from audit scope, CLEAN UP placeholders

These keep getting flagged across every audit (P1-23, P4-2, P4-13, P10-04 note). The pattern:

- `personality.py`: BALANCED and LOYAL exist in enum + `PERSONALITY_DESCRIPTIONS` + `PERSONALITY_TRIGGERS` (with TODO Phase 3 triggers)
- `personality_modifiers.py`: Empty combat modifier dicts for both
- `objection_v2.py`: `PERSONALITY_EVALUATORS` maps only aggressive/cautious/literal. Balanced/loyal hit `return ConcernLevel.NONE` with a comment saying "build when balanced/loyal marshals ship (1805 expansion)"
- `defiance.py`: Returns 0.0 defiance chance for non-mapped personalities

**No marshal in the game uses balanced or loyal.** They are phantom types that generate audit noise every time someone reviews the codebase. The previous deep audit (DEEP_AUDIT_FIX_PLAN) already decided: "Keep in enum (serialization + modding safety). No marshal uses them. Jealousy system is the natural time to fill or remove."

**This plan's decision:** Clean up the noise sources in Session 11:
1. Keep enum values (safe for serialization, modding, future use)
2. Remove `PERSONALITY_TRIGGERS` entries for BALANCED and LOYAL (all are TODO Phase 3 / 1805)
3. Remove `PERSONALITY_DESCRIPTIONS` entries for BALANCED and LOYAL (describe marshals that don't exist)
4. Add explicit comment at enum: `# BALANCED/LOYAL: Reserved for 1805 expansion. No current marshal uses these.`
5. Add explicit early return with comment in `objection_v2.py` instead of silent fallthrough

This eliminates the "zero triggers" / "no evaluator" / "personality-dead" findings permanently. When 1805 expansion ships, the enum is ready and the implementation work is clearly scoped.

**Findings resolved by this decision:** P1-23, P4-2, P4-13 (partial), P10-04 (partial — literal is separate).

### Other standing decisions

- **P1-6 (modifier side effects):** Evaluate in S7. Battle report snapshot already works around this. Likely add docstring warning rather than refactor.
- **P1-8 (square double-dip):** Evaluate in S7. May be intentional tactical triangle balance.
- **P1-14 (Ney ability in combat.py):** Document as intentional exception to Golden Rule #1. Not a bug.
- **P2-16 (AI strategic orders):** Marked INTENTIONAL IGNORE in audit. Skip.
- **P9-01 (executor God Object):** Real problem but high-risk refactoring. Phase E optional.
- **P10-04 (Literal personality hollow):** Design feature work, not a bug fix. Future phase.
- **P10-01/P10-02 (eras, diplomatic victory):** Design features. Future phase.

### Severity re-classifications

| Finding | Audit Severity | Reclassified | Reason |
|---------|---------------|--------------|--------|
| P1-23 (balanced/loyal combat) | DESIGN | SKIP | Placeholder cleanup, not a bug |
| P4-2 (balanced/loyal evaluator) | MAJOR | SKIP | Same — no marshal uses them |
| P1-14 (Ney ability location) | MINOR | SKIP | Documented intentional exception |
| P2-16 (AI strategic orders) | NOTE | SKIP | Marked intentional in audit |
| P4-5 (V1/V2 dual systems) | MINOR | DEFERRED | V1 still used for strategic objections |
| P9-01 through P9-25 (architecture) | Various | Phase E | Optional refactoring |
| P10-01 to P10-20 (game design) | Various | FUTURE | New features, not fixes |
| P11-01 to P11-18 (exploits) | Various | Session 8 | Design gate needed |

---

## Phase A: Critical Fixes (Sessions 1-3)

### Session 1: Post-Combat Pipeline — COMPLETE

**Theme:** The single biggest root cause in the audit. ~48 findings from one problem.
**Findings:** P1-1, P12-01→P12-04, P12-13, P13-01→P13-25, P14-01→P14-21

**Evaluation results:**
- Cataloged all 28 post-combat systems in `_execute_attack`. Glorious charge had 10, auto-charge had 11.
- Audit overcounted by ~40%: coordination, relationships, reinforcements, bombardment are N/A for solo 1v1 charge combat.
- ~10 systems genuinely missing per path (forced retreat, destroyed cleanup, territory capture, vindication, authority, coalition, idle, exhaustion, diplo record).
- Auto-charge lacked state guards (broken, retreating, drilling, dead could charge).

**Approach taken:** Added missing systems inline to both paths. Did NOT extract from `_execute_attack` (safer — avoids regression risk in the main combat path). Extraction deferred to Phase E.

**Changes:**
- `executor.py` `_execute_glorious_charge`: +9 systems (forced retreat, destroyed cleanup, territory capture, vindication, authority, coalition, idle reset, exhaustion tracking, capture choice passthrough)
- `world_state.py` `_process_reckless_cavalry_turn_start`: +5 state guards + 7 systems (diplo record, forced retreat simplified, destroyed cleanup, territory capture simplified, authority, coalition)
- Used correct nested casualty keys (`result["attacker"]["casualties"]`) — interaction with P1-2 noted

**Interaction discovered:** P1-2 (Session 2) — `_execute_attack` coalition code uses wrong casualty keys, causing threat/exhaustion to always be zero for ALL battles. New charge code uses correct keys.

**Tests:** 21 new in `tests/test_post_combat_pipeline.py`. 0 regressions (6707 → 6728 total).

---

### Session 2: Critical Quick Fixes — COMPLETE

**Theme:** 5 high-impact bugs with simple 1-10 line fixes each.

| # | Finding | Fix Applied |
|---|---------|-------------|
| 1 | **P1-2: Coalition threat always zero** | `executor.py:4995-4996` — Changed flat `battle_result.get("attacker_casualties")` → nested `battle_result.get("attacker", {}).get("casualties", 0)` |
| 2 | **P2-1: Authority bonus writes wrong attribute** | `turn_manager.py:449` — Changed `self.world.authority = ...` → `self.world.authority_tracker.modify_authority(+10)` |
| 3 | **P22-01: Autonomous marshal command format** | `enemy_ai.py:580-585` — Wrapped flat dict in nested `{"command": {...}}` matching `process_nation_turn` format |
| 4 | **P17-01: AP treaty penalty overwritten** | `world_state.py:3738-3740` — Moved player action reset BEFORE `_process_treaty_clauses()` so AP penalty applies |
| 5 | **P1-3: Advance-toward-enemy bypasses move_to()** | `executor.py:3733,7334` — Changed `marshal.location = x` → `marshal.move_to(x)` for cavalry/holding resets |

**Approach:** All 5 fixes applied as planned. No movement attrition added to auto-advance (implicit moves, not explicit commands). Existing test `test_autonomy.py` updated to use `authority_tracker` instead of phantom attribute.

**Tests:** 13 new in `tests/test_systems_audit_session2.py`. 0 regressions (6728 → 6741 total).

---

### Session 3: Fog of War Fixes — COMPLETE

**Theme:** Information leaks that defeat the fog system.

**Evaluation results:**
- **P5-1/P21-01 (LLM prompt leaks):** DEFERRED. LLM prompt is internal, not player-facing. In mock mode no LLM text is generated. In anthropic mode, LLM needs enemy data for command parsing ("attack Wellington"). Executor prevents acting on fogged info. Risk is cosmetic only.
- **P21-02 (battle report exact strength):** DEFERRED. Intentional — player just fought them. Post-battle numbers are battlefield intelligence ("counting bodies"), not a fog leak.
- **P5-2 (campaign log 5 missing event types):** FIXED. Added handler for war_declaration/cascade (PARTIAL+ on involved nations) and coalition events (always show — target France).
- **P21-03 (/marshal_trust enemy data):** FIXED. Added nation guard — enemy marshal requests return "No intelligence available."
- **P21-04→P21-06 (STALE exact numbers):** FIXED. Ledger, dispatch intelligence, and dispatch estimation all use `get_strength_band()` + `BAND_MIDPOINTS` for STALE instead of exact frozen values.

**Changes:**
- `campaign_log.py`: +17 lines — fog filter handler for war/cascade/coalition events
- `main.py`: +5 lines — nation guard on `/marshal_trust` endpoint
- `ledger.py`: −6/+3 lines — STALE display uses band, nation summary uses BAND_MIDPOINTS
- `dispatch.py`: −3/+5 lines — STALE intelligence uses band, estimation uses BAND_MIDPOINTS, added `get_strength_band` import
- `tests/test_dispatch.py`: Updated 1 existing test (STALE estimation now uses band midpoint)

**Tests:** 12 new in `tests/test_systems_audit_session3.py`. 0 regressions (6741 → 6753 total).

---

## Phase B: Major Bug Fixes (Sessions 4-7)

### Session 4: AI System Bugs — COMPLETE

**Theme:** Enemy AI behavior bugs that affect gameplay quality.
**Result:** 5 fixes, 6 false positives skipped, 12 new tests (6753 → 6765).

| # | Finding | Result |
|---|---------|--------|
| 1 | **P2-2: Missing is_at_war in 7+ locations** | **SKIP** — False positive. 30+ `is_at_war()` checks exist; `get_enemies_of_nation()` gatekeeps all targets. |
| 2 | **P2-3: Zero error handling in enemy phase** | **FIXED** — try/except around nation processing in turn_manager.py. Crash in one nation logs traceback and continues. |
| 3 | **P2-4: 2-AP stance transitions not budgeted** | **SKIP** — Executor enforces AP at execution time; failed-action tracking handles rejected attempts. |
| 4 | **P2-5: Cooldowns decrement per-nation (3x fast)** | **SKIP** — False positive. `_decrement_cooldowns()` called once per nation turn, correct behavior. |
| 5 | **P2-6: Overwatch self-counts target** | **SKIP** — False positive. Checks `m.nation != attacker.nation`, correctly excludes target. |
| 6 | **P2-7: Raw personality instead of effective** | **SKIP** — False positive. AI uses `_get_effective_personality()` consistently. |
| 7 | **P2-8: AI_DEBUG = True hardcoded** | **FIXED** — Now reads `AI_DEBUG` env var (default False). |
| 8 | **P2-9: Vassal courting events silently discarded** | **SKIP** — Not a bug. Notifications + dispatch events already created. Confirmed with test. |
| 9 | **P2-10: Capital proximity no dedup** | **FIXED** — Tracks `_capital_proximity_last_alert` per enemy; suppresses within 3 turns. |
| 10 | **P2-11: _last_enemy_phase_results dead state** | **FIXED** — Removed field from WorldState and write from turn_manager.py. |
| 11 | **P2-12/P6-9: start_turn() dead code** | **FIXED** — Removed `start_turn()` and `_generate_situation_report()` from TurnManager. Updated __main__ doctest. |

**Tests:** 12 new in `tests/test_systems_audit_session4.py`

---

### Session 5: Strategic Commands + Serialization — COMPLETE

**Theme:** Strategic order bugs + save/load gaps. 9 findings evaluated → 3 false positives, 6 fixed.

| # | Finding | Status |
|---|---------|--------|
| 1 | **P3-1: StrategicOrder missing last_contact serialization** | **FIXED** — Added `last_contact_enemy`/`last_contact_turn` as dataclass fields with to_dict/from_dict. |
| 2 | **P3-2: HOLD march ignores cavalry movement_range** | **FIXED** — Added movement_range loop matching MOVE_TO/PURSUE pattern. |
| 3 | **P3-3/P4-6/P8-10: Hardcoded "Paris" (3 locations)** | **FIXED** — All 3 fallbacks now use `NATION_CAPITALS.get(marshal.nation, 'Paris')`. |
| 4 | **P3-4: PURSUE path never stored on order.path** | **FIXED** — `order.path = list(path)` after path computation. |
| 5 | **P3-5: Triple HOLD expiry check** | **SKIP** — False positive (intentional defensive cascade across different code paths). |
| 6 | **P3-7: Substring vs regex inconsistency** | **SKIP** — False positive (by design: regex for word boundaries, substring for validated contexts). |
| 7 | **P3-8: issued_turn vs started_turn** | **FIXED** — Ledger field renamed from "issued_turn" to "started_turn". Added docstring clarifying both fields' distinct purposes. |
| 8 | **P20-01: Dynamic trust attrs leak memory** | **SKIP** — False positive (transient per-turn state, same pattern as overwatch_penalty). |
| 9 | **P20-02: War exhaustion thresholds not serialized** | **FIXED** — Promoted to proper `we_dispatched_thresholds` field on WorldState with init/to_dict/from_dict. Updated coalition.py refs and existing tests. |

**Tests:** 15 new in `tests/test_systems_audit_session5.py` (6765 → 6780 total)

---

### Session 6: Parser Fixes — COMPLETE

**Theme:** Command parsing bugs causing mis-routing. 7 fixes, 14 tests.

| # | Finding | Fix | Status |
|---|---------|-----|--------|
| 1 | **P8-1: "invest in" / "release" too broad** | Replaced bare "invest in " / "release " with nation-specific keywords | DONE |
| 2 | **P8-2: "help" matches "help Davout"** | Replaced substring match with exact whitelist ("help", "help me", "i need help") | DONE |
| 3 | **P8-3: "withdraw to" parsed as retreat** | Guarded retreat: `" to " not in command_lower`; added "withdraw to" to move keywords | DONE |
| 4 | **P8-4: parser.py valid_actions out of sync** | Added 10 missing entries: release_vassal, pursue, support, reinforce, march, 5 diplomatic meta-actions | DONE |
| 5 | **P8-5: known_enemies incomplete** | Added ArchdukeCharles, Schwarzenberg, Reynier (7 total) | DONE |
| 6 | **P8-6: "shell" trailing space** | Removed trailing space from "shell " in llm_client.py and parser.py BOMBARD_KEYWORDS | DONE |
| 7 | **P8-7: Nationality words cleared as invalid target** | Removed "Prussians"/"British" target mappings; auto-target handles correctly | DONE |

**Files:** `llm_client.py` (F1,F2,F3,F6,F7), `parser.py` (F4,F5,F6), `test_systems_audit_session6.py` (14 tests)
**Tests:** 14 new (6780 → 6794 total)

---

### Session 7: Minor Combat Bugs — COMPLETE

**Theme:** Combat edge cases and architectural cleanups.
**Result:** 7 real bugs fixed, 2 code smells (docstring/comment only), 1 refactor, 1 by-design skip. 15 new tests, 0 regressions (6794 → 6809 total). 3 existing tests updated for float→int conversion.

| # | Finding | Verdict | Fix |
|---|---------|---------|-----|
| P1-8 | Square double-dip artillery | **BY DESIGN** | Skipped — melee and bombardment are separate per spec |
| P1-5 | Pursuit resurrects dead marshals | **FIXED** | Guard changed to `strength > 1000`; clear pursuit_damage when guard fails |
| P1-9 | Mutual destruction skips morale | **FIXED** | Added morale loss + battles_lost for both sides |
| P1-10 | Zero casualty stalemate | **FIXED** | `max(1, ...)` floor in `_calculate_casualties` |
| P1-11 | FORCED_RETREAT_THRESHOLD local | **FIXED** | Moved to module-level constant |
| P1-12 | Exhaustion message hardcoded map | **FIXED** | Uses `marshal.get_exhaustion_info()` now |
| P1-15 | Form square missing retreat_recovery | **FIXED** | Added guard in `_execute_form_square` |
| P1-16 | Bombardment return fire no minimum | **FIXED** | `max(1, ...)` floor |
| P1-22 | Bombardment floats to Godot | **FIXED** | Wrapped `terrain_modifier`, `fort_old`, `fort_new` in `int(x * 100)` |
| P1-6 | get_*_modifier side effects | **DOCSTRING** | Added WARNING docstrings |
| P1-13 | Drill state cleared in combat.py | **COMMENT** | Added pragmatic-exception comment |

---

## Phase C: Balance & Design Gate (Session 8)

### Session 8: Balance Evaluation — COMPLETE

**Theme:** Gameplay balance changes. All 12 items evaluated with user, 10 implemented.

| # | Finding | Resolution |
|---|---------|------------|
| 1 | **P15-01: Davout Paris turtle** | FIXED: Defense modifier hard cap at 1.75x |
| 2 | **P15-04: HOLD decay immunity cautious-only** | FIXED: HOLD slows decay for all (cautious 75%, others 50%) |
| 3 | **P15-05: AI futility filter permanent** | FIXED: Decay -1 every 3 turns + reset when defender < 50% starting |
| 4 | **P15-06: Supply attrition cap 3%** | FIXED: +1% stacking penalty per marshal beyond 1st (cap 6% total) |
| 5 | **P15-03: No early defeat condition** | DEFERRED: Earmarked for roadmap before EA |
| 6 | **P6-2: Admin AP → gold exploit** | FIXED: Reduced 75g → 35g per unused AP |
| 7 | **P6-3: Victory threshold inconsistency** | FIXED: Consolidated to 14 regions |
| 8 | **P6-6: Manpower regen trivializes losses** | FIXED: Halved all rates (infantry 5000→2500, cavalry 500→250, artillery 300→150) |
| 9 | **P6-8: British naval income unconditional** | FIXED: Requires at least 1 controlled region |
| 10 | **P18-01: Trade income invisible** | FIXED: Added to dispatch situation + ledger economy sections |
| 11 | **P18-02: Bankruptcy check before trade income** | FIXED: Moved to after all income sources (trade, continental system, treaties, tribute) |
| 12 | **P4-4/P4-7: Failed defiance vindication reset** | WAI: Working as intended (harsh but thematic) |

**Tests:** 25 new in `test_systems_audit_session8.py`. 9 existing tests updated for new values. Total: 6834 passed.

---

## Phase D: Polish (Sessions 9-11)

### Session 9: Personality & Disobedience Bugs — COMPLETE

**Theme:** Vindication tracking bugs, strategic order processing fairness, SUPPORT duration.
**Result:** 4 real bugs fixed, 1 false positive, 1 by-design. 10 new tests, 1 existing test updated. 0 regressions (6846 → 6856 total).

| # | Finding | Status |
|---|---------|--------|
| 1 | **P4-3: Vindication last_change_turn always 0** | **FIXED** — `getattr()` on dict replaced with `game_state.current_turn` |
| 2 | **P4-8: Defensive vindication no narrative closure** | **FIXED** — Notification on stale cleanup (defiance/objection flavor) |
| 3 | **P4-9: _is_fortified checks region name not marshal** | **FALSE POSITIVE** — Code reads `marshal.fortified`, not region |
| 4 | **P3-6: Alphabetical processing starvation** | **FIXED** — Two-pass: non-interrupting first, then deferred interrupts |
| 5 | **P3-9: SUPPORT auto-completes with max_turns** | **FIXED** — Skip ally_safe auto-complete when `condition.max_turns` set |
| 6 | **P3-10: Cannon fire "continue" costs trust** | **BY DESIGN** — -2 trust matches insist pattern (override marshal's concern) |

**Tests:** 10 new in `tests/test_systems_audit_session9.py`, 1 existing test updated in `test_strategic_ui_comprehensive.py`.

---

### Session 10: Battle Report + Godot UX — **COMPLETE**

| # | Finding | Result |
|---|---------|--------|
| 1 | **P1-7: Wellington/Habsburg abilities missing from snapshots** | **FIXED** — Added Reverse Slope (+5%) and Habsburg Resolve (+3%) to `snapshot_defender_modifiers()` |
| 2 | **P1-17: Flawless victory gets generic observation** | **FIXED** — Added "won_flawless" template at priority 8.7 (zero casualties + enemy losses) |
| 3 | **P1-18: Relationship observations buried at priority 15** | **FIXED** — Promoted to priority 9.6 (above stalemate at 10) |
| 4 | **P1-19: Devoted ally synergy blocked by stalemate** | **FIXED** — Promoted to priority 9.5 (above stalemate at 10) |
| 5 | **P1-20: Cavalry overrun no attacker observation** | **FIXED** — Added "cavalry_overrun_attacker" template at priority 6d |
| 6 | **P7-2: _trim_old_messages strips BBCode** | **FIXED** — Use `.text` instead of `.get_parsed_text()`, join lines |
| 7 | **P7-3: Diplomatic top bar not updated in 5+ handlers** | **FIXED** — Added `_update_diplomatic_top_bar()` to capture_choice, interrupt, load handlers |
| 8 | **P7-4: Load doesn't restore war panel** | **FIXED** — Added `_update_diplomatic_top_bar()` + `_process_active_wars()` to `_on_load_result` |
| 9 | **P7-5: Tooltip off-screen** | **FALSE POSITIVE** — Godot 4 built-in `tooltip_text` auto-clamps to viewport |
| 10 | **P7-7: Debug prints in production** | **FIXED** — Added `DEBUG_VERBOSE` const, gated ~30 verbose gameplay prints behind it |

**Tests:** 9 new in `tests/test_systems_audit_session10.py` (ability snapshots, flawless victory, observation priority, cavalry overrun).

---

### Session 11: Cleanup, Placeholders, & Documentation — COMPLETE

**Result:** 6 fixes applied (items 2-4 already done in Session 4), 19 new tests (`test_systems_audit_session11.py`), 2 existing tests updated. 6904 total passing.

| # | Finding | Status |
|---|---------|--------|
| 1 | **Balanced/Loyal placeholder cleanup** | **FIXED** — Removed PERSONALITY_DESCRIPTIONS + PERSONALITY_TRIGGERS entries. Enum kept. Comment added. |
| 2 | **P2-8: AI_DEBUG = True** | Already fixed in Session 4 — SKIP |
| 3 | **P2-11: _last_enemy_phase_results dead state** | Already fixed in Session 4 — SKIP |
| 4 | **P2-12/P6-9: start_turn() dead code** | Already fixed in Session 4 — SKIP |
| 5 | **P9-23: Bug fix history comments** | **FIXED** — Archived to `docs/archive/ENEMY_AI_BUG_HISTORY.md` |
| 6 | **P19-01: Notification cap** | **FIXED** — 50-notification cap, auto-dismiss oldest NORMAL, HIGH/CRITICAL preserved |
| 7 | **P20-03/P20-04: Serialization test improvements** | **FIXED** — DiplomaticRepresentative roundtrip + field coverage tests |
| 8 | **P6-5: CLAUDE.md AP references outdated** | Deferred — current CLAUDE.md references strategic AP costs correctly |
| 9 | **P1-21: Tactical prefix duplication** | **FIXED** — Extracted `_build_tactical_prefix()` in combat.py, both call sites use it |
| 10 | **Docs updates** | **DONE** — STATUS.md, SYSTEMS_AUDIT_FIX_PLAN.md |

**Tests:** 19 new

---

## Phase F: Quality of Life (Session 12) — COMPLETE

### Session 12: Quality of Life Improvements — COMPLETE

**Result:** 6 fixes applied (items 2, 3, 5 already done in Session 8), 20 new tests (`test_systems_audit_session12.py`), 9 existing tests updated. 6904 total passing.

| # | Finding | Status |
|---|---------|--------|
| 1 | **P15-05: Futility filter per-turn decay** | **FIXED** — Changed from every-3-turn to every-turn decay. AI retries targets faster after situation changes. |
| 2 | **P18-01: Trade income in dispatch** | Already done in Session 8 — SKIP |
| 3 | **P18-02: Bankruptcy ordering** | Already done in Session 8 — SKIP |
| 4 | **P6-3: Victory threshold constant** | **FIXED** — Extracted `VICTORY_REGION_FRACTION = 0.75` to world_state.py. Both world_state.py and turn_manager.py use it dynamically. |
| 5 | **P15-04: HOLD decay all personalities** | Already done in Session 8 — SKIP |
| 6 | **P6-8: British naval income scaling** | **FIXED** — `150 + 50 * coastal_count` (max 300). Coastal regions: Netherlands, Normandy, Brittany, Bordeaux, Marseille. |
| 7 | **P6-6: Manpower regen war exhaustion** | **FIXED** — Infantry regen scaled by WE: halved at 100, zero at 200, floor 1000. Cavalry/artillery unaffected. |
| 8 | **P6-2: Admin AP gold rate** | **FIXED** — Reduced from 35g to 25g per unused admin AP (75g → 35g → 25g across sessions). |
| 9 | **Stagnation variety** | **FIXED** — `random.choice(fallback_dests)` replaces deterministic `[0]`. |

**Tests:** 20 new

---

## Phase E: Architecture — DEFERRED TO 1805 MAP EXPANSION (Sessions 13-14)

Deferred per user decision (March 24, 2026). Architecture refactoring makes more sense alongside the 80-region map rework that will restructure executor.py anyway. Added to `ROADMAP.md` EA 1805 section.

### Session 13: Executor Decomposition Part 1

- Extract `_execute_debug` → `commands/debug_commands.py` (867 lines)
- Extract `_process_dialogue_choice` → dispatch table (1,098 lines)
- ~2,000 lines out of executor.py
- **Risk:** HIGH — 125 inline imports, circular dependency resolution needed

### Session 14: Shared Helpers + AI Cleanup

- Extract recruit cost formula (P9-17, 3 locations)
- Extract drill check helper (P9-03, 3 locations)
- Extract auto-end-turn shared logic (P9-04)
- Replace 43 hand-rolled AI enemy queries with helper methods (P9-14)
- **Risk:** MEDIUM — behavioral equivalence must be tested

---

## Findings NOT addressed by this plan

| Category | Count | Reason |
|----------|-------|--------|
| Positive findings (NOTES) | ~50 | No action needed — good architecture |
| Design features (literal personality, diplomatic victory, eras, era pacing, AI feints, AI coordination) | ~6 | New feature work for future phase (9 simpler items moved to Phase F Session 12) |
| Godot deep dive (P23-P24 not reached in audit) | — | Separate frontend audit needed |
| P11 exploit strategies (deathball, sequential elimination) | ~5 | Addressed partially by Session 8 balance gate |
| P10-08 (vassal over-engineered) | 1 | Accept as pre-built for scale |
| P10-15 (35+ systems complexity) | 1 | Address via tutorial system (Pre-EA) |

---

## Session Estimates

| Phase | Sessions | Findings Fixed | New Tests |
|-------|----------|---------------|-----------|
| A: Critical Fixes | 1-3 | ~61 | 54 |
| B: Major Fixes | 4-7 | ~43 | 56 |
| C: Balance Gate | 8 | 10 | 25 |
| D: Polish | 9-11 | ~28 | 38 |
| F: Quality of Life | 12 | 6 | 20 |
| E: Architecture (optional) | 13-14 | TBD | TBD |
| **Total (Sessions 1-12)** | **12 core** | **~148** | **193** |

---

## Session Protocol (every session)

1. **Evaluate:** Read the actual code for every finding. Verify the bug exists. Check comments/tests for intentional behavior.
2. **Assess risk:** Could the fix break something else? What systems touch this code?
3. **Decide:** Fix, skip (intentional), or defer (needs design gate).
4. **Implement:** Minimal fix. Don't refactor adjacent code.
5. **Test:** Write tests that fail before fix, pass after. Run full suite.
6. **Document:** Update STATUS.md, mark findings in this doc.
