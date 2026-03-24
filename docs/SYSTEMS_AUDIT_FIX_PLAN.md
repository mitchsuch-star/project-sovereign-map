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

### Session 4: AI System Bugs

**Theme:** Enemy AI behavior bugs that affect gameplay quality.

| # | Finding | Evaluate | Risk |
|---|---------|----------|------|
| 1 | **P2-2: Missing is_at_war in 7+ locations** | Check each location — are neutrals actually causing problems in current diplomatic start? | Medium — could change AI behavior in diplomatic scenarios |
| 2 | **P2-3: Zero error handling in enemy phase** | Check if crashes actually happen in testing | Medium — try/except could mask real bugs |
| 3 | **P2-4: 2-AP stance transitions not budgeted** | Verify AP cost table for Def→Agg | Low |
| 4 | **P2-5: Cooldowns decrement per-nation (3x fast)** | Verify per-nation vs per-turn loop structure | Low |
| 5 | **P2-6: Overwatch self-counts target** | Verify missing name exclusion | Low |
| 6 | **P2-7: Raw personality instead of effective** | Verify `_get_effective_personality` exists and differs | Low |
| 7 | **P2-8: AI_DEBUG = True hardcoded** | Trivial | None |
| 8 | **P2-9: Vassal courting events silently discarded** | Verify events generated but never stored | Low |
| 9 | **P2-10: Capital proximity no dedup** | Verify repeated alerts | Low |
| 10 | **P2-11: _last_enemy_phase_results dead state** | Verify never read | None |
| 11 | **P2-12/P6-9: start_turn() dead code** | Verify never called in production | None |

**P2-2 needs most care:** At game start, France is at war with Britain+Prussia but not Austria/Saxony. If AI is already checking war status in attack decisions, adding is_at_war to defender/presence checks is correct. But verify: does Austria ever have marshals adjacent to French marshals at start? If not, the bug is dormant.

**P2-3 approach:** Use try/except with `logging.error()` + continue, NOT silent pass. Log the full traceback so bugs surface in testing.

**Tests:** ~15-20 new

---

### Session 5: Strategic Commands + Serialization

**Theme:** Strategic order bugs + save/load gaps.

| # | Finding | Evaluate | Risk |
|---|---------|----------|------|
| 1 | **P3-1: StrategicOrder missing last_contact serialization** | Verify fields are dynamic `setattr` not dataclass | Low |
| 2 | **P3-2: HOLD march ignores cavalry movement_range** | Compare HOLD march code with MOVE_TO march code | Low |
| 3 | **P3-3/P4-6/P8-10: Hardcoded "Paris" (3 locations)** | Verify all 3 use literal "Paris" | None |
| 4 | **P3-4: PURSUE path never stored on order.path** | Verify ledger shows 0 turns for PURSUE | Low |
| 5 | **P3-5: Triple HOLD expiry check** | Evaluate: consolidate or just document? | Low |
| 6 | **P3-7: Substring vs regex inconsistency** | Check if edge cases exist in practice | Low |
| 7 | **P3-8: issued_turn vs started_turn** | Verify which field is correct authority | Low |
| 8 | **P20-01: Dynamic trust attrs leak memory** | Verify with `dir(marshal)` after 5 turns | Low — clean fix |
| 9 | **P20-02: War exhaustion thresholds not serialized** | Verify `_we_dispatched_thresholds` is set on world | Low |

**Tests:** ~12-15 new

---

### Session 6: Parser Fixes

**Theme:** Command parsing bugs causing mis-routing.

| # | Finding | Evaluate | Risk |
|---|---------|----------|------|
| 1 | **P8-1: "invest in" / "release" too broad** | Test: does "invest in defenses" route to vassal? | Medium — tightening could break valid vassal commands |
| 2 | **P8-2: "help" matches "help Davout"** | Test the collision | Low |
| 3 | **P8-3: "withdraw to" parsed as retreat** | Test ordering | Low |
| 4 | **P8-4: parser.py valid_actions out of sync** | Compare lists | None |
| 5 | **P8-5: known_enemies hardcoded and incomplete** | Check if it affects fuzzy matching in practice | Low |
| 6 | **P8-6: "shell" trailing space** | Test "Drouot, shell" | Low |
| 7 | **P8-7: Nationality words cleared as invalid target** | Test "attack the Prussians" | Low |

**Evaluate P8-1 carefully:** What ARE the valid vassal commands? What keywords do they need? Remove only the bare "invest in " — keep "invest in vassal", "invest in [nation_name]".

**Tests:** ~10-12 new

---

### Session 7: Minor Combat Bugs

**Theme:** Combat edge cases and architectural cleanups.

| # | Finding | Evaluate | Risk |
|---|---------|----------|------|
| 1 | **P1-5: Bombardment resurrects dead marshals (1000 troops)** | Verify the strength<=0 → retreat → 1000 path | Low |
| 2 | **P1-8: Square double-dip artillery** | **Careful:** Is +50% melee AND +50% bombardment intentional? Check TACTICAL_TRIANGLE_SPEC. If spec says both, it's by design. | Could change balance |
| 3 | **P1-9: Mutual destruction skips morale/counters** | Verify the path | Low |
| 4 | **P1-10: Zero casualty stalemate (tiny armies)** | Verify `int(1 * 0.15) = 0` | Low |
| 5 | **P1-11: FORCED_RETREAT_THRESHOLD duplicated** | Trivial | None |
| 6 | **P1-12: Exhaustion message hardcoded map** | Verify maps align | None |
| 7 | **P1-15: Form square missing retreat_recovery** | Verify missing guard | Low |
| 8 | **P1-16: Bombardment return fire no minimum** | Verify no floor | Low |
| 9 | **P1-22: Bombardment floats to Godot** | Verify unwrapped values | None |
| 10 | **P1-6: get_*_modifier side effects** | **Careful:** Battle report snapshot already works around this. Is refactoring worth the risk? Likely: add prominent docstring + idempotency test instead of refactoring. | Medium if refactored |
| 11 | **P1-13: Drill state cleared in combat.py** | **Evaluate:** Is this a pragmatic exception to Golden Rule #1? Likely: extract `clear_drill_state()` on Marshal, call from combat.py. Low risk, cleaner. | Low |

**P1-8 is the key evaluation:** Read `TACTICAL_TRIANGLE_SPEC.md` to see if square's vulnerability to artillery is designed as total vulnerability (melee+bombardment) or just melee. If spec says both, skip the fix.

**Tests:** ~12-15 new

---

## Phase C: Balance & Design Gate (Session 8)

### Session 8: Balance Evaluation — REQUIRES USER APPROVAL

**Theme:** Gameplay balance changes. Each item presented for approval before coding.

**Evaluate-only items (present findings, user decides):**

| # | Finding | Question for user |
|---|---------|-------------------|
| 1 | **P15-01: Davout Paris turtle (110k effective defense)** | Is permanent invincibility a problem or Davout's identity? |
| 2 | **P15-04: HOLD decay immunity cautious-only** | Should HOLD slow decay for all, or keep as cautious perk? |
| 3 | **P15-05: AI futility filter permanent** | Add decay (reduce by 1 every 3 turns)? Reset on defender weakness? |
| 4 | **P15-06: Supply attrition cap 3%** | Raise to 5-8%? Add per-marshal stacking penalty? |
| 5 | **P15-03: No early defeat condition** | Add capital loss = defeat? Or capital loss = 3-turn countdown? |
| 6 | **P6-2: Admin AP → gold exploit (150g/turn free)** | Reduce rate? Cap at 1 unused AP? Remove? |
| 7 | **P6-3: Victory threshold inconsistency (15 vs 14)** | Which threshold is correct? Consolidate to one. |
| 8 | **P6-6: Infantry manpower regen trivializes losses** | Reduce rate? Add war exhaustion modifier? |
| 9 | **P6-8: British naval income unconditional** | Scale with regions? Require 1+ region? |
| 10 | **P18-01: Trade income invisible** | Add trade line to income summary / dispatch? |
| 11 | **P18-02: Bankruptcy check before trade income** | Move after all income sources? |
| 12 | **P4-4/P4-7: Failed defiance vindication reset** | Is reset-on-obedience intentional harsh punishment, or unfair? |

**Protocol:** Evaluate each finding with code evidence. Present to user. Only implement what's approved. Some may be deferred or marked "working as intended."

---

## Phase D: Polish (Sessions 9-11)

### Session 9: Personality & Disobedience Bugs

| # | Finding | Notes |
|---|---------|-------|
| 1 | **P4-3: Vindication last_change_turn always 0** | Dict `.get()` used with `getattr` — wrong accessor |
| 2 | **P4-8: Defensive vindication no narrative closure** | Add Berthier observation on stale cleanup |
| 3 | **P4-9: _is_fortified checks region name not marshal** | V1 path — may skip if V1 deprecated |
| 4 | **P3-6: Alphabetical processing starvation** | Process all non-interrupting first, then present interrupts |
| 5 | **P3-9: SUPPORT auto-completes with max_turns** | Don't auto-complete "ally safe" when max_turns set |
| 6 | **P3-10: Cannon fire "continue" costs trust** | Evaluate: is -2 trust for exercising command intentional? |

**Tests:** ~8-10 new

---

### Session 10: Battle Report + Godot UX

| # | Finding | Notes |
|---|---------|-------|
| 1 | **P1-7: Wellington/Habsburg abilities missing from snapshots** | Add snapshot blocks for Reverse Slope (+5%) and Habsburg Resolve (+3%) |
| 2 | **P1-17: Flawless victory gets generic observation** | Add "won_flawless" template before "won_decisively" |
| 3 | **P1-18: Relationship observations buried at priority 15** | Promote to ~4.5 or append as secondary |
| 4 | **P1-19: Devoted ally synergy blocked by stalemate** | Move devoted check above stalemate (~9.5) |
| 5 | **P1-20: Cavalry overrun no attacker observation** | Add attacker-side cavalry counter observation |
| 6 | **P7-2: _trim_old_messages strips BBCode** | Use `output_display.text` instead of `get_parsed_text()` |
| 7 | **P7-3: Diplomatic top bar not updated in 5+ handlers** | Add `_update_diplomatic_top_bar(response)` to all handlers |
| 8 | **P7-4: Load doesn't restore war panel** | Add missing calls after load |
| 9 | **P7-5: Tooltip off-screen** | Clamp against viewport rect |
| 10 | **P7-7: Debug prints in production** | Remove or gate behind DEBUG flag |

**Tests:** ~8-10 new

---

### Session 11: Cleanup, Placeholders, & Documentation

| # | Finding | Notes |
|---|---------|-------|
| 1 | **Balanced/Loyal placeholder cleanup** | Remove PERSONALITY_TRIGGERS and PERSONALITY_DESCRIPTIONS entries. Keep enum. Add "reserved for 1805" comments. Fix silent fallthrough in objection_v2.py. |
| 2 | **P2-8: AI_DEBUG = True** | Set False, use env var |
| 3 | **P2-11: _last_enemy_phase_results dead state** | Remove field |
| 4 | **P2-12/P6-9: start_turn() dead code** | Remove method + __main__ block |
| 5 | **P9-23: Bug fix history comments** | Move to `docs/archive/ENEMY_AI_BUG_HISTORY.md` |
| 6 | **P19-01: Notification cap** | Add 50-notification cap, auto-dismiss oldest NORMAL |
| 7 | **P20-03/P20-04: Serialization test improvements** | Add _-prefix field allowlist, diplomacy roundtrip assertions |
| 8 | **P6-5: CLAUDE.md AP references outdated** | Update "3 AP" → "4 military + 2 admin" |
| 9 | **P1-21: Tactical prefix duplication** | Extract `_build_tactical_prefix()` |
| 10 | **Docs updates** | STATUS.md, SYSTEMS_REFERENCE.md, SAVE_FORMAT_REFERENCE.md |

**Tests:** ~5-8 new

---

## Phase F: Quality of Life (Session 12)

Gameplay improvements surfaced by audit design findings (P6, P10, P11, P15, P18). Mostly 1-15 line changes that make the game noticeably better. Grouped into Tier 1 (trivial, 1-5 lines each) and Tier 2 (small, 5-20 lines each).

### Session 12: Quality of Life Improvements

#### Tier 1 — Trivial fixes (1-5 lines each)

| # | Finding | Location | What to do |
|---|---------|----------|------------|
| 1 | **P15-05: Futility filter never decays** | `enemy_ai.py:877-881` (increment), `enemy_ai.py:2185-2200` (filter) | Futility counter goes up when attacking a fortified region fails but never goes back down. After enough turns, add decay: in the increment block at line 877, add per-turn decay logic — if a marshal did NOT attack a specific target this turn, decrement that key's counter by 1 (min 0). This allows AI to retry regions after the situation changes (e.g. fort degrades, reinforcements arrive). Add decay at the START of the futility tracking block (before incrementing). |
| 2 | **P18-01: Trade income invisible in dispatch** | `dispatch.py:112-118` (income section), `world_state.py:calculate_turn_income()` at line 2037 | The dispatch income section shows region income and naval income but NOT trade income. Player can't see where gold comes from. Fix: In `dispatch.py` `_build_situation()`, after computing `income_data`, also call `process_trade_income()` in dry-run mode or compute trade total. Simplest approach: add a `trade_income` field to the income_data returned by `calculate_turn_income()` by computing trade from `diplomacy.py:calculate_trade_income()`, then display it in the dispatch like naval income. |
| 3 | **P18-02: Bankruptcy checked before trade income** | `world_state.py:3694-3701` (advance_turn ordering) | `process_income_phase()` (line 3695) checks bankruptcy INSIDE itself (line 2229 `_update_bankruptcy`). `process_trade_income()` runs AFTER at line 3701. So if a nation is at -50 gold after income but trade would bring them to +100, they still get flagged bankrupt for a turn. Fix: move the `_update_bankruptcy(nation)` call OUT of `process_income_phase()` and into `advance_turn()` AFTER `process_trade_income()` runs. This means adding a loop over all nations calling `self._update_bankruptcy(nation)` at ~line 3702. Remove the call from inside `process_income_phase()`. |
| 4 | **P6-3: Victory threshold — verify consistency** | `world_state.py:3805`, `turn_manager.py:665` | Both currently use `math.ceil(len(regions) * 0.75)`. Verify they are consistent (they appear to be). If consistent, extract to a shared constant `VICTORY_REGION_FRACTION = 0.75` in `world_state.py` and reference it from both. If NOT consistent, pick the correct value and consolidate. |

#### Tier 2 — Small improvements (5-20 lines each)

| # | Finding | Location | What to do |
|---|---------|----------|------------|
| 5 | **P15-04: HOLD order decay for all personalities** | `strategic.py:606-625` (aggressive-only HOLD expiry) | Currently only aggressive marshals abandon HOLD orders after `max_turns`. Other personalities hold forever, which means cautious AI marshals can sit on a HOLD order indefinitely while the battle moves on. Fix: Add personality-specific HOLD durations. Aggressive: keep current `max_turns` behavior. Cautious: hold up to `max_turns + 2` extra turns, then expire with "reluctantly relinquishes" message. Literal: hold exactly `max_turns`, then expire with "considers orders fulfilled" message. If no `max_turns` condition, add a global fallback: 6 turns for aggressive, 8 for cautious, 10 for literal. Keep the per-personality messaging. |
| 6 | **P6-8: British naval income unconditional** | `world_state.py:2061` (`naval_income = 300 if nation == "Britain" else 0`) | Britain gets 300 naval income even if they control zero coastal regions. Fix: make naval income scale with coastal region count. Britain base: 150 + 50 per coastal region controlled (max 300). Other nations: 0 (leave unchanged). Define coastal regions: check `region.terrain == "coastal"` or define a set of coastal region names (Holland, Piedmont, etc. — check REGIONS_DATA for regions with ports/coast). |
| 7 | **P6-6: Manpower regen unaffected by war exhaustion** | `world_state.py:2174-2203` (`get_manpower_regen_rates`) | Manpower regen is constant regardless of how exhausted a nation is from war. Fix: scale infantry regen by war exhaustion. At the end of `get_manpower_regen_rates()`, before the return, apply a penalty: `exhaustion = self.war_exhaustion.get(nation, 0)` then reduce infantry regen by `exhaustion * 0.5%` (so at 100 exhaustion, infantry regen is halved; at 200 it's zero). Cap minimum regen at 1000. Do NOT scale cavalry/artillery — they're already bottlenecked. |
| 8 | **P6-2: Admin AP → gold exploit (reduce rate)** | `world_state.py:2256` (`return int(... * 75)`) | 75 gold per unused admin AP is too generous. A player who uses zero admin actions gets 150 gold/turn for free (2 admin AP × 75), which removes the tension from admin actions. Fix: reduce to **25 gold per unused admin AP**. Change `* 75` → `* 25`. This makes hoarding AP still slightly rewarding but not worth skipping recruiting or diplomacy for. |
| 9 | **Stagnation variety — deterministic fallback** | `enemy_ai.py:2947-2954` (`_get_stagnation_action` fallback) | When the stagnation breaker can't find a move toward the enemy, it picks `fallback_dests[0]` deterministically, which means AI always moves to the same adjacent region. Fix: replace `fallback = fallback_dests[0]` with `fallback = random.choice(fallback_dests)`. Import `random` if not already imported at top of `enemy_ai.py`. This small change makes stagnation-broken AI less predictable. |

**Tests:** ~10-15 new (bankruptcy ordering, futility decay, HOLD expiry per personality, naval income scaling, manpower exhaustion scaling, admin gold rate, stagnation randomness)

---

## Phase E: Architecture — OPTIONAL (Sessions 13-14)

Only pursue if user decides maintainability refactoring is worth the risk.

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

| Phase | Sessions | Findings Fixed | New Tests (est.) |
|-------|----------|---------------|-----------------|
| A: Critical Fixes | 1-3 | ~61 | ~50-60 |
| B: Major Fixes | 4-7 | ~43 | ~50-62 |
| C: Balance Gate | 8 | ~12 (after approval) | ~10-15 |
| D: Polish | 9-11 | ~34 | ~20-28 |
| F: Quality of Life | 12 | ~9 | ~10-15 |
| E: Architecture (optional) | 13-14 | ~25 | ~10 |
| **Total** | **12 core + 2 optional** | **~184** | **~150-190** |

---

## Session Protocol (every session)

1. **Evaluate:** Read the actual code for every finding. Verify the bug exists. Check comments/tests for intentional behavior.
2. **Assess risk:** Could the fix break something else? What systems touch this code?
3. **Decide:** Fix, skip (intentional), or defer (needs design gate).
4. **Implement:** Minimal fix. Don't refactor adjacent code.
5. **Test:** Write tests that fail before fix, pass after. Run full suite.
6. **Document:** Update STATUS.md, mark findings in this doc.
