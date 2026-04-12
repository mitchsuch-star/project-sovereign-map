# Systems Audit V2 — Verification + Depth
**Started:** 2026-03-25
**Scope:** Fix verification, second-order bugs, unexplored territory, stress patterns
**Prior audit:** audit-report-systems.md (275 findings, all fixed)
**Purpose:** Verify fixes, find regressions, explore new areas, stress-test edge cases

---

## Phase 1: VERIFICATION SWEEP

### 1A: Post-Combat Pipeline Verification

### [V2-1] [COMBAT] No Shared Post-Combat Function Extracted — Triple Inline Duplication
- **Severity:** MAJOR
- **Category:** VERIFICATION
- **File:** executor.py:10226-10591, executor.py:3469-5100, world_state.py:5164-5500
- **Description:** The prior audit's top recommendation (P1-1, P13, P14) was to extract a shared `_process_post_combat()`. This was NOT done. Instead, each of the 3 combat paths (`_execute_attack`, `_execute_glorious_charge`, `_process_reckless_cavalry_turn_start`) contains its own inline copy of post-combat processing. Critical systems (forced retreat, destroyed marshal cleanup, territory conquest, coalition threat, war score, authority) ARE present in all 3 paths. However, multi-marshal coordination systems are missing from glorious charge and auto-charge:
- **Missing from glorious charge:** relationship processing, flanking, reinforcement, coordination context, casualty distribution, overwatch, auto-bombardment, combat notifications, battle report re-pick
- **Missing from auto-charge:** same as above, PLUS vindication
- **Evidence:** 3 independent ~300-line inline post-combat blocks with no shared function call. Comment at world_state.py:5248 acknowledges: "Auto-charge is a 6th resolve_battle path outside executor.py"
- **Assessment:** The critical bugs ARE fixed (dead marshals cleaned up, territory captured, coalition threat fires). The missing multi-marshal systems are arguably low-priority for solo cavalry charges. But the triple duplication means future post-combat changes need 3 updates. This is a DESIGN debt, not a regression.
- **Test Coverage:** Yes — 6930 tests pass

### [V2-2] [COMBAT] Glorious Charge Engagement Check Only Partial — Direct Command Bypasses
- **Severity:** MINOR
- **Category:** VERIFICATION
- **File:** executor.py:10226-10326
- **Description:** Normal flow (attack → recklessness popup → charge) is safe because engagement check runs in `_execute_attack` first (line 3887-3910). But direct `charge` command and `respond_to_glorious_charge` call `_execute_glorious_charge` directly without prior engagement checking. A leapfrog check (line 10305-10325) prevents charging THROUGH occupied regions, but not charging AWAY from enemies in current region.
- **Proposed Fix:** Add engagement check at top of `_execute_glorious_charge()`.
- **Test Coverage:** No specific test for direct charge command with enemies in same region

### [V2-3] [COMBAT] Advance-Toward-Enemy move_to() Fix — VERIFIED
- **Severity:** NOTE
- **Category:** VERIFICATION
- **File:** executor.py:3735, world_state.py:5493
- **Description:** Both `_execute_attack` advance path and reckless auto-move now use `marshal.move_to()` instead of direct location assignment. Cavalry tracking, Grouchy HOLD clearing, moved_this_turn flag all properly updated.
- **Test Coverage:** Yes

### [V2-4] [COMBAT] Auto-Charge Territory Capture Simplified — Skips Fortified Regions Entirely
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** world_state.py:5375
- **Description:** Auto-charge territory capture checks `not cap_region.has_building("fortification")` and skips entirely if fortified, while `_execute_attack` handles fort occupation properly via `_attempt_region_capture`. An auto-charge victory against the last defender of a fortified region won't capture the territory.
- **Proposed Fix:** Use `_attempt_region_capture` or equivalent logic.
- **Test Coverage:** No

### 1C: Fog + AI Parity Verification

### [V2-5] [FOG] LLM Prompt Still Receives Unfiltered Enemy Data — Fog Leak to AI Parser
- **Severity:** MAJOR
- **Category:** REGRESSION
- **File:** main.py:49-98, prompt_builder.py:527-546
- **Description:** `get_llm_game_state()` iterates ALL enemy marshals via `world.get_enemy_marshals()` and includes exact `location` and `strength` with zero fog/intel filtering. This data goes to `_format_enemies()` in prompt_builder.py which formats "Wellington (British) at Waterloo, 65K troops" into the LLM prompt. The P21-01 fix either was never applied or was reverted.
- **Impact:** When LLM_MODE=anthropic, the LLM receives perfect information about all enemies regardless of fog of war. In mock mode this is moot since the mock parser doesn't use enemy positions.
- **Proposed Fix:** Filter enemies through `world.intel` visibility, only include PARTIAL+ visibility, use strength bands for non-FULL.
- **Test Coverage:** No

### [V2-6] [FOG] Battle Report Strength Bands — NOT APPLICABLE (By Design)
- **Severity:** NOTE
- **Category:** VERIFICATION
- **File:** battle_report.py:770-815
- **Description:** Battle reports show exact casualty numbers for both sides. This is correct — combat happens when marshals are co-located, which grants FULL visibility. The P21-02 finding was a false positive in the original audit.
- **Test Coverage:** Yes

### [V2-7] [AI] Autonomous Marshal Command Format — VERIFIED
- **Severity:** NOTE
- **Category:** VERIFICATION
- **File:** enemy_ai.py:531-538
- **Description:** `decide_single_action()` correctly builds nested format `{"command": {"type": "specific", "marshal": ..., "action": ..., "target": ...}}` matching executor expectations.
- **Test Coverage:** Yes

### [V2-8] [AI] Futility Counter Decay/Reset — VERIFIED
- **Severity:** NOTE
- **Category:** VERIFICATION
- **File:** world_state.py:3790-3815, enemy_ai.py:829-831
- **Description:** Futility counters decrement by 1 per turn, entries at 0 removed. Reset when defender drops below 50% starting strength. Reset on successful attacks. Fix is correct and complete.
- **Test Coverage:** Yes

### [V2-9] [ECONOMY] Supply Attrition Cap Increased — VERIFIED
- **Severity:** NOTE
- **Category:** VERIFICATION
- **File:** world_state.py:2300-2352
- **Description:** Two-part cap: base excess-ratio capped at 3%, plus +1% per extra marshal stacking penalty. Total cap 6%. Death-ball penalty for 3+ marshals even under capacity. Replaces old flat 3%.
- **Test Coverage:** Yes

### [V2-10] [FOG] Marshal Trust Endpoint Nation-Gated — VERIFIED
- **Severity:** NOTE
- **Category:** VERIFICATION
- **File:** main.py:1493-1498
- **Description:** Enemy marshal trust queries blocked with "No intelligence available" message.
- **Test Coverage:** Yes

### [V2-11] [FOG] STALE Visibility in Ledger/Dispatch — VERIFIED
- **Severity:** NOTE
- **Category:** VERIFICATION
- **File:** ledger.py:263-358, dispatch.py:309-362
- **Description:** All visibility tiers (FULL/PARTIAL/STALE/LAST_KNOWN) handled consistently with strength bands at non-FULL.
- **Test Coverage:** Yes

### [V2-12] [COMBAT] Coalition Casualty Key Format — VERIFIED
- **Severity:** NOTE
- **Category:** VERIFICATION
- **File:** executor.py:4997-4998, executor.py:10515-10516
- **Description:** All paths now use correct `result.get("attacker", {}).get("casualties", 0)`. No instances of old flat key remain.
- **Test Coverage:** Yes

### [V2-13] [AI] is_at_war Filters — VERIFIED
- **Severity:** NOTE
- **Category:** VERIFICATION
- **File:** enemy_ai.py (40+ locations)
- **Description:** `is_at_war()` checks consistently applied across all major AI decision paths including target selection, threat assessment, retreat safety, and engagement checks.
- **Test Coverage:** Yes

### 1B: Turn Ordering + Economy Verification

### [V2-14] [ECONOMY] AP Treaty Penalty Ordering — VERIFIED
- **Severity:** NOTE
- **Category:** VERIFICATION
- **File:** world_state.py:3738-3761, 4412-4419
- **Description:** AP reset runs FIRST (lines 3738-3755), then `_process_treaty_clauses()` runs AFTER (line 3761). Comments at 3740-3746 explicitly document the ordering. Test in `test_deep_audit_session4.py` verifies non-compounding over 4 turns.
- **Test Coverage:** Yes

### [V2-15] [ECONOMY] Bankruptcy Check Timing — VERIFIED
- **Severity:** NOTE
- **Category:** VERIFICATION
- **File:** world_state.py:3718-3776
- **Description:** 6-step ordering: (1) base income, (2) trade income, (3) continental system, (4) treaty gold clauses, (5) vassal tribute, (6) bankruptcy check LAST. Docstring explicitly documents this.
- **Test Coverage:** Yes

### [V2-16] [TRUST] Dynamic Trust Attrs Still Creates Per-Turn Attributes — Save/Load Cap Bypass
- **Severity:** MINOR
- **Category:** REGRESSION
- **File:** executor.py:12079-12101
- **Description:** `_apply_diplomatic_trust_reactions()` still uses `setattr(m_obj, f"_diplomatic_trust_this_turn_{world.current_turn}", ...)` creating a NEW dynamic attribute per turn. NOT in `__init__`, `to_dict()`, or `from_dict()`. Accumulates forever (40 turns = 40 extra attrs per marshal). After mid-turn save/load, the per-turn cap resets to 0, allowing diplomatic trust changes to double-dip past the +/-5 cap. Was marked SKIP as "false positive" in fix plan, but unlike `overwatch_penalty` (single attr overwritten each combat), this creates unique attrs per turn.
- **Proposed Fix:** Use single field `diplomatic_trust_applied_this_turn` reset in advance_turn. Serialize it.
- **Test Coverage:** No

### [V2-17] [PACING] Early Defeat Condition — NOT IMPLEMENTED (Deferred)
- **Severity:** NOTE
- **Category:** VERIFICATION
- **File:** turn_manager.py:711-762
- **Description:** `_check_victory_conditions()` only checks: all marshals destroyed, total region conquest, time expiry. No capital-loss defeat trigger. Fix plan marked as DEFERRED to pre-EA roadmap. Not a regression — was a design recommendation that was intentionally deferred.
- **Test Coverage:** N/A

### [V2-18] [PACING] HOLD Fortification Immunity — VERIFIED
- **Severity:** NOTE
- **Category:** VERIFICATION
- **File:** world_state.py:4664-4710, 27-33
- **Description:** HOLD orders now slow decay (cautious 75% reduction, others 50%) but do NOT prevent it. `should_decay` applies to ALL non-cavalry marshals regardless of order. Every personality has explicit decay config. Fix is correct and complete.
- **Test Coverage:** Yes

---

### Phase 1 Summary

| ID | Finding | Status |
|----|---------|--------|
| V2-1 | Shared post-combat function | NOT EXTRACTED (triple duplication, but critical systems present) |
| V2-2 | Glorious charge engagement check | PARTIAL (direct command bypasses) |
| V2-3 | Advance-toward-enemy move_to() | **VERIFIED** |
| V2-4 | Auto-charge territory capture | NEW_BUG (skips fortified regions) |
| V2-5 | LLM prompt fog-filtered | **REGRESSION** (still leaks all enemy data) |
| V2-6 | Battle report strength bands | NOT APPLICABLE (by design) |
| V2-7 | Autonomous marshal command format | **VERIFIED** |
| V2-8 | AI futility decay/reset | **VERIFIED** |
| V2-9 | Supply attrition cap | **VERIFIED** |
| V2-10 | Marshal trust nation gate | **VERIFIED** |
| V2-11 | STALE visibility in ledger/dispatch | **VERIFIED** |
| V2-12 | Coalition casualty key format | **VERIFIED** |
| V2-13 | is_at_war filters in AI | **VERIFIED** |
| V2-14 | AP treaty penalty ordering | **VERIFIED** |
| V2-15 | Bankruptcy check timing | **VERIFIED** |
| V2-16 | Dynamic trust attrs | REGRESSION (per-turn attrs, save/load cap bypass) |
| V2-17 | Early defeat condition | DEFERRED (intentional) |
| V2-18 | HOLD fortification immunity | **VERIFIED** |

**Verified:** 11 | **Regression/New Bug:** 3 (V2-5, V2-16, V2-4) | **Partial:** 1 (V2-2) | **Not Applicable/Deferred:** 3

---

## Phase 2: SECOND-ORDER BUGS

### 2A: Post-Combat Duplication Deep-Read

### [V2-44] [COMBAT] Auto-Charge Attacker Forced Retreat Has No Surrounded Fallback — Zombie Marshal
- **Severity:** CRITICAL
- **Category:** NEW_BUG
- **File:** world_state.py:5332-5345
- **Description:** When auto-charging attacker needs forced retreat and `get_safe_retreat_destination` returns None (surrounded), the code does NOTHING — no broken state, no capital teleport, no strength reduction. Marshal stays in place at morale ≤25% as functional zombie. Defender path (5312-5329) and executor's `_apply_forced_retreat_or_break` handle this correctly.
- **Evidence:** Lines 5332-5345: `if retreat_to:` but NO `else:` branch.
- **Test Coverage:** No

### [V2-45] [COMBAT] Auto-Charge Missing Fortification Defense Bonus — Defenders Unprotected
- **Severity:** MAJOR
- **Category:** REGRESSION
- **File:** world_state.py:5240
- **Description:** `resolve_battle()` called without `fortification_bonus` parameter. Defenders in fortified regions get NO +25% defense during auto-charge. Both `_execute_attack` and `_execute_glorious_charge` correctly pass this.
- **Proposed Fix:** Calculate and pass `fortification_bonus` like other combat paths.
- **Test Coverage:** No

### [V2-46] [COMBAT] Auto-Charge Attacker Retreat Uses Post-Retreat Enemy Location — Retreats Toward Enemy
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** world_state.py:5333
- **Description:** Defender retreats first (5297-5329), changing `enemy.location`. Then attacker retreat (5333) uses `enemy.location` for directional retreat — but this is the defender's RETREAT destination. Attacker could retreat TOWARD the defender instead of away.
- **Proposed Fix:** Save original battle location before any retreats.
- **Test Coverage:** No

### [V2-47] [COMBAT] Auto-Charge Missing Leapfrog Check — Can Jump Over Enemy Armies
- **Severity:** MAJOR
- **Category:** REGRESSION
- **File:** world_state.py:5219
- **Description:** No check for enemy marshals blocking path when target is 2 regions away (cavalry range). Reckless cavalry can leapfrog over enemy armies during auto-charge. Both `_execute_attack` (4190-4205) and `_execute_glorious_charge` (10306-10325) have leapfrog prevention.
- **Test Coverage:** No

### [V2-48] [COMBAT] Auto-Charge Missing Decisive Victory Coalition Check
- **Severity:** MAJOR
- **Category:** REGRESSION
- **File:** world_state.py:5432-5434
- **Description:** When France wins as defender vs auto-charging enemy, missing decisive victory check (ratio > 2, casualties > 10000) that should add +5 threat and coalition shock. Both other combat paths have this.
- **Test Coverage:** No

### [V2-49] [COMBAT] Auto-Charge Simplified Retreat Missing 5+ State-Clearing Operations
- **Severity:** MAJOR
- **Category:** REGRESSION
- **File:** world_state.py:5296-5345
- **Description:** Inline forced retreat missing vs executor's `_apply_forced_retreat_or_break`: occupation state, artillery bombardment state, HOLD state clearing, movement attrition on retreat, voided strategic order notifications.
- **Test Coverage:** No

### [V2-50] [COMBAT] Glorious Charge + Auto-Charge Missing Win/Loss Relationship Processing
- **Severity:** MAJOR
- **Category:** REGRESSION
- **File:** executor.py:10226, world_state.py:5164
- **Description:** `process_battle_relationships()` only called in `_execute_attack` (line 4671). Neither glorious charge nor auto-charge calls it. Coordinated battles via these paths produce no relationship changes.
- **Test Coverage:** No

### [V2-51] [COMBAT] Glorious Charge Missing Flanking Recording and Bonus
- **Severity:** MINOR
- **Category:** REGRESSION
- **File:** executor.py:10226-10591
- **Description:** No `record_attack()` or `calculate_flanking_bonus()`. Charge won't count toward flanking for other attacks on same target, and won't benefit from existing flanking.
- **Test Coverage:** No

### [V2-52] [COMBAT] Auto-Charge Missing Vindication Resolution
- **Severity:** MINOR
- **Category:** REGRESSION
- **File:** world_state.py:5164-5534
- **Description:** Pending vindication entries for auto-charging marshal never resolved by auto-charge combat. Would remain pending indefinitely.
- **Test Coverage:** No

### [V2-53] [COMBAT] Auto-Charge Missing idle_turns Reset
- **Severity:** MINOR
- **Category:** REGRESSION
- **File:** world_state.py:5164-5534
- **Description:** `marshal.idle_turns` not reset to 0. Reckless cavalry fighting only via auto-charges accumulates idle turns, potentially triggering idle-related effects despite being active.
- **Test Coverage:** No

### [V2-54] [COMBAT] Glorious Charge Re-Assigns world Variable — Asymmetric None Guard
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** executor.py:10361
- **Description:** Re-assigns `world = game_state.get("world")` with `if world:` guard covering only `record_battle` call, while downstream code (10373+) uses `world` without the guard.
- **Test Coverage:** No

### 2D: Cross-System Interaction Bugs

### [V2-19] [AI] Enemy Phase try/except Swallows Partial State Mutations — Silent Board Changes
- **Severity:** MAJOR
- **Category:** REGRESSION
- **File:** turn_manager.py:530-544
- **Description:** The try/except catches `Exception` broadly around `process_nation_turn`. If a crash occurs partway through (e.g., after 3 of 4 actions), the world state has already been mutated (troops moved, combats resolved, regions captured) but `nation_results` is set to `[]` — making it appear nothing happened. The player sees no enemy activity while the board silently changed. This can mask real bugs during development.
- **Proposed Fix:** Either roll back state on exception (complex) or ensure partial results are captured. At minimum, log the error visibly to the player.
- **Test Coverage:** No

### [V2-20] [AI] Cooldowns Still Decrement 4x Per Game Turn — Per-Nation Not Per-Turn
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** enemy_ai.py:605
- **Description:** `_decrement_cooldowns(world)` is called inside `process_nation_turn()` at line 605, invoked once per enemy nation. With 4 enemy nations, all cooldowns tick 4x per game turn. A 2-turn cooldown effectively lasts 0.5 turns. Same root cause as prior audit P2-5 — NOT FIXED.
- **Proposed Fix:** Move cooldown decrement to turn_manager.py before nation loop, or track `last_decrement_turn`.
- **Test Coverage:** No

### [V2-21] [AI] Re-Fortify Cooldown Also Ticks 4x — Same Root Cause as V2-20
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** enemy_ai.py:607-615
- **Description:** `ai_refortify_cooldown` dict on WorldState is also decremented inside `process_nation_turn()` for every nation. Contributes to fortify/unfortify oscillation patterns.
- **Test Coverage:** No

### [V2-22] [AI] AI Stance Change Doesn't Verify Budget for Follow-Up Action
- **Severity:** MINOR
- **Category:** VERIFICATION
- **File:** enemy_ai.py:2289-2295
- **Description:** P4 attack logic returns stance_change without verifying nation has enough AP for stance (2 AP) PLUS follow-up attack (1 AP = 3 total). With only 2 AP left, stance change succeeds but the attack never happens — wasted action. Impact mitigated by most aggressive marshals starting in Aggressive stance.
- **Test Coverage:** No

### [V2-23] [AI] Authority Bonus from Autonomy — VERIFIED FIXED
- **Severity:** NOTE
- **Category:** VERIFICATION
- **File:** turn_manager.py:431
- **Description:** Correctly calls `self.world.authority_tracker.modify_authority(+10)` for spectacular autonomy tier.
- **Test Coverage:** Yes

### [V2-24] [AI] Overwatch Self-Count Still Not Fixed — Artillery Target Counts Itself
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** enemy_ai.py:1846-1856
- **Description:** Overwatch calculation counts target artillery as its own overwatch battery. No `m.name != target.name` exclusion. Inflates overwatch penalty by 3% when attacking artillery targets (-9% instead of -6% with 2 real overwatch units).
- **Proposed Fix:** Add `and m.name != target.name` to filter.
- **Test Coverage:** No

### [V2-25] [STRATEGIC] StrategicOrder last_contact Fields — VERIFIED FIXED
- **Severity:** NOTE
- **Category:** VERIFICATION
- **File:** marshal.py:135-136, 160-161, 190-191
- **Description:** `last_contact_enemy` and `last_contact_turn` properly declared as dataclass fields, included in to_dict/from_dict.
- **Test Coverage:** Yes

### [V2-26] [AI] Autonomous Marshal Phase Has No Error Handling — Crash = Broken End-Turn
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** turn_manager.py:332-384
- **Description:** Unlike enemy phase (try/except), `_process_autonomous_marshals` has zero error handling. If `decide_single_action()` throws, the entire end-turn fails and the player is stuck. Asymmetric with enemy phase resilience.
- **Proposed Fix:** Wrap per-marshal processing in try/except matching enemy phase pattern.
- **Test Coverage:** No

### 2C: Balance Changes Review

### [V2-27] [BALANCE] Davout Free Unfortify Resets Decay Timer — HOLD Decay Change Ineffective
- **Severity:** MAJOR
- **Category:** DESIGN
- **File:** executor.py:8981-8983, executor.py:8728-8731
- **Description:** When unfortifying, `turns_fortified` resets to 0. Re-fortifying starts decay timer fresh. For Davout (cautious), unfortify is FREE (no AP cost). Player can: fortify 7 turns (reaching ~20% defense), unfortify free on turn 7 before decay starts at turn 8, re-fortify same turn (1 AP). Decay timer resets. This makes the HOLD decay change largely irrelevant for the one marshal it was designed to constrain.
- **Proposed Fix:** Track cumulative fortification time that doesn't reset on unfortify, or add AP cost for cautious unfortify.
- **Test Coverage:** No

### [V2-28] [BALANCE] Cautious+HOLD Effective Decay Rate is 0.25%/Turn — Functionally Negligible
- **Severity:** MINOR
- **Category:** DESIGN
- **File:** world_state.py:4682-4684
- **Description:** Cautious personality: decay starts at turn 8, rate 0.01 (1%/turn). HOLD 75% reduction → 0.25%/turn. With max 20% and floor 5%, that's 60 turns to decay fully. Games rarely exceed 30-40 turns. The change from full immunity to 0.25%/turn decay is functionally equivalent to no change.
- **Test Coverage:** No

### [V2-29] [COMBAT] Supply Attrition Can Create 0-Strength Zombie Marshals — Never Cleaned Up
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** world_state.py:2343
- **Description:** `m.strength = max(0, m.strength - losses)` can reduce to exactly 0, but unlike combat (which calls `world.marshals.pop()`), supply attrition has NO cleanup logic. A 0-strength marshal remains in world, targetable by AI, showing in marshal lists. Same issue exists for bankruptcy desertions (line 2498). In practice rare due to int truncation at small values, but reachable with higher 6% cap. Pre-existing but worsened by balance change.
- **Proposed Fix:** After attrition loop, pop any marshals with strength <= 0.
- **Test Coverage:** No

### [V2-30] [GODOT] Strategic Ledger Economy Tab Omits Trade Income — Net Doesn't Add Up
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** strategic_ledger.gd:332-362
- **Description:** Backend `ledger.py` correctly includes `trade_income` in economy dict and Net calculation. But Godot `strategic_ledger.gd` `_render_economy()` displays Income, Upkeep, Net without ever reading/displaying trade_income. Player sees e.g. Income 400g, Upkeep 300g, Net +250g — the missing +150g is trade income. Visible in Diplomatic Ledger per-partner view but not as a total in the economy tab.
- **Proposed Fix:** Add trade income line between Income and Upkeep in `_render_economy()`.
- **Test Coverage:** No

### [V2-31] [BALANCE] Supply Attrition Stacking Penalty Cliff at 3 Marshals
- **Severity:** MINOR
- **Category:** DESIGN
- **File:** world_state.py:2328-2333
- **Description:** Under capacity: 2 marshals = 0% attrition, 3 marshals = 2% attrition. Abrupt cliff. Appears intentional (2 marshals isn't a "death ball") but feels arbitrary.
- **Test Coverage:** No

### [V2-32] [AI] Futility Creates Predictable 3-Turn Attack/Pause Oscillation
- **Severity:** MINOR
- **Category:** DESIGN
- **File:** world_state.py:3790-3815, enemy_ai.py:2136-2154
- **Description:** AI fails 3 attacks → futility = 3 → gives up → counter decays 1/turn → 3 turns later attacks again → cycle repeats. Mitigated by fort decay, AI strength loss, and 50% strength reset.
- **Test Coverage:** No

### [V2-33] [NOTIFICATIONS] Notification List Unbounded With HIGH/CRITICAL Only
- **Severity:** MINOR
- **Category:** DESIGN
- **File:** notifications.py:117-119
- **Description:** Cap of 50 only auto-dismisses NORMAL priority. If player never dismisses HIGH/CRITICAL, list grows without bound. In active diplomacy 40-turn game, could mean 100+ undismissed notifications.
- **Test Coverage:** No

### [V2-34] [ECONOMY] All New Balance Mechanics Properly Serialized
- **Severity:** NOTE
- **Category:** VERIFICATION
- **Description:** HOLD decay (uses existing turns_fortified), supply attrition (computed fresh each turn), AI futility (ai_attack_futility in world_state to_dict/from_dict), notification cap (constant, not state) — all clean.
- **Test Coverage:** Yes

### 2B: Test Quality Review

### [V2-35] [TESTS] 3 Test Classes Re-Implement Production Logic — Testing the Mock Not the Code
- **Severity:** MAJOR
- **Category:** DESIGN
- **File:** test_systems_audit_session12.py:26-88, test_systems_audit_session7.py:47-104
- **Description:** `TestFutilityFilterDecay` manually duplicates the futility decay loop instead of calling `advance_turn()`. `TestPursuitFloor` re-implements the pursuit damage formula. `test_pursuit_no_resurrect_below_floor` is a tautology (sets strength=500, asserts strength==500, calls no production code). If production logic changes, these tests still pass.
- **Test Coverage:** N/A — these ARE the tests

### [V2-36] [TESTS] Combat Tests With Conditional Assertions — May Never Execute
- **Severity:** MAJOR
- **Category:** DESIGN
- **File:** test_post_combat_pipeline.py:481,508, test_systems_audit_session7.py:128,143
- **Description:** Core assertions gated behind `if any(e.get("attacker_won") for e in events):` or `if result["outcome"] == "mutual_destruction":`. Combat randomness means these assertions may silently never execute. Tests pass trivially on unlucky dice. Should force deterministic outcomes via RNG seeding or mock dice.
- **Test Coverage:** N/A

### [V2-37] [TESTS] 46 Test Methods With Zero Assertions — Inflate Test Count
- **Severity:** MAJOR
- **Category:** DESIGN
- **File:** test_artillery.py, test_cautious_advance_cooldown.py, test_cavalry_recklessness.py, test_enemy_ai.py, etc.
- **Description:** 46 test methods have no `assert`, no `pytest.raises`, no `pytest.skip`. Names claim behavioral properties (e.g., "does_not_advance") that are never verified. These inflate the 6,933 count without providing verification.
- **Test Coverage:** N/A

### [V2-38] [TESTS] No Test for V2-5 (LLM Prompt Fog Filtering)
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** N/A (missing test)
- **Description:** No test verifies that `get_llm_game_state()` or `_format_enemies()` respects fog of war. The regression found in Phase 1 (V2-5) has zero test coverage.
- **Test Coverage:** No

### [V2-39] [TESTS] No Test for V2-16 (Dynamic Trust Attr Save/Load Cap Bypass)
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** N/A (missing test)
- **Description:** No test for the scenario where dynamically-added trust attributes bypass the +/-5 cap after save/load.
- **Test Coverage:** No

### [V2-40] [TESTS] No Test for 2 Reckless Marshals in Same Region
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** test_cavalry_recklessness.py:719
- **Description:** `test_multiple_reckless_cavalry_process_in_order` uses a single marshal (Ney). Comment says "Would need multiple aggressive cavalry marshals" — deferred and never updated.
- **Test Coverage:** No

### [V2-41] [TESTS] _make_marshal Helper Duplicated Across 30 Test Files
- **Severity:** MINOR
- **Category:** DESIGN
- **File:** 30+ test files
- **Description:** `_make_marshal()` copy-pasted with slight variations across 30+ files. No shared conftest.py fixture. If Marshal constructor changes, 30 helpers need updating. Some use `_suppress_output()`, some don't.
- **Test Coverage:** N/A

### [V2-42] [TESTS] Exact String Assertions on User-Facing Messages
- **Severity:** MINOR
- **Category:** DESIGN
- **File:** test_systems_audit_session7.py:238, test_true_flanking.py:121,155,193
- **Description:** Tests assert on exact message strings. Any text change breaks tests without behavioral change. Better to assert on `result["success"]` and check key words with `in`.
- **Test Coverage:** N/A

### [V2-43] [TESTS] Tests Assert on Docstring Content
- **Severity:** MINOR
- **Category:** DESIGN
- **File:** test_systems_audit_session7.py:341-351
- **Description:** `TestModifierDocstrings` asserts `get_attack_modifier.__doc__` contains "WARNING" and "side effect". Documentation quality should be enforced by code review, not unit tests that break on rewording.
- **Test Coverage:** N/A

---

## Phase 3: UNEXPLORED TERRITORY

### 3B: Parser Robustness

### [V2-55] [PARSER] Marshal Name "ney" Matches Inside Common Words — Substring Collision
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** llm_client.py:561,571-577
- **Description:** Mock parser extracts marshal names using `command_lower.find("ney")` — raw substring matching. "ney" appears inside "journey", "money", "honey", "kidney", "chimney", "attorney". Input "journey to Belgium" produces marshal=Ney, action=move, target=Belgium (interpreted as "Order Ney to move to Belgium").
- **Proposed Fix:** Use word-boundary regex `r'\bney\b'` for marshal extraction.
- **Test Coverage:** No

### [V2-56] [PARSER] "dig in" Maps to Fortify in Mock But HOLD in Strategic Parser — Semantic Conflict
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** llm_client.py:706 vs strategic_parser.py:180
- **Description:** "dig in" matched as `fortify` (1 AP immediate action) in mock parser but strategic parser also matches HOLD keyword, upgrading to a multi-turn standing order (2 AP). Player wanting to entrench gets a strategic HOLD instead of a tactical fortify.
- **Proposed Fix:** Remove "dig in" from strategic HOLD keywords.
- **Test Coverage:** No

### [V2-57] [PARSER] Strategic Parser Bare Verbs Partially Dead Code — "advance"/"push"/"head" Never Reach Strategic Detection
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** strategic_parser.py:164 vs llm_client.py:680-688
- **Description:** Strategic MOVE_TO bare verbs ("advance", "push", "head") don't match mock parser keywords (which require directional suffixes like "advance towards"). Since validation fails before strategic detection runs, these are dead code. Additionally "fall back"/"withdraw" (without "to") create action=retreat vs strategic_type=MOVE_TO conflicts.
- **Proposed Fix:** Either add bare verbs to mock parser, or remove from strategic keywords.
- **Test Coverage:** No

### [V2-58] [PARSER] "hold" Always Upgraded to Strategic — No Way to Issue Tactical One-Shot Defend
- **Severity:** MINOR
- **Category:** DESIGN
- **File:** llm_client.py:673-674, strategic_parser.py:179
- **Description:** Any command containing "hold" gets upgraded to strategic HOLD (2 AP) when world is provided. Parser.py documents "hold" as "alias for defend" (1 AP). Players typing "hold" expecting a quick defend pay double AP. No way to distinguish intent.
- **Test Coverage:** No

### [V2-59] [PARSER] "commands" Substring Check in Help Detection — False Positives
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** llm_client.py:633
- **Description:** Help detection uses `"commands" in command_lower` (substring). "issue commands to Davout" or "cancel commands for Ney" falsely trigger help action instead of being parsed as commands.
- **Test Coverage:** No

### [V2-60] [PARSER] Reynier Missing From Mock Parser known_marshals
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** llm_client.py:560-568
- **Description:** Saxony's marshal Reynier not in mock parser's `known_marshals` list (but IS in parser.py's `known_enemies`). "attack Reynier" requires fuzzy matching fallback instead of direct keyword match. Works but adds unnecessary latency.
- **Test Coverage:** No

### [V2-61] [PARSER] parse_multiple Splits on " and " Destroying Multi-Word Phrases
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** parser.py:551-574
- **Description:** `parse_multiple` splits on " and " to handle "Ney and Davout, attack". But also splits "fortify and hold Belgium" into two separate commands. "follow and destroy" (PURSUE keyword) similarly broken.
- **Test Coverage:** No

### [V2-62] [PARSER] "court " Keyword Matches "court martial" as Diplomatic Mission
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** llm_client.py:549
- **Description:** "court " with trailing space triggers diplomatic routing. "court martial Grouchy" would be parsed as diplomatic mission "court" with target containing "martial Grouchy".
- **Test Coverage:** No

### 3C: Multi-Turn Stress Simulation

### [V2-63] [PACING] Victory Threshold Mismatch — Two Formulas Will Diverge on Map Expansion
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** turn_manager.py:744 vs world_state.py:3874
- **Description:** `turn_manager._check_victory_conditions()` uses `int(total * 0.77)` while `world_state._advance_turn_internal()` uses `int(len(regions) * 0.75)`. Both yield 14 for 19 regions. With 21 regions (1805 map): 16 vs 15 — MISMATCH. Two independent victory checks with different formulas.
- **Proposed Fix:** Unify to single `VICTORY_REGION_FRACTION` constant.
- **Test Coverage:** No

### [V2-64] [PACING] Triple Victory Check Can Produce Conflicting Results
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** turn_manager.py:66-81, turn_manager.py:171, world_state.py:3870
- **Description:** Victory checked 3 times: (1) pre-enemy phase, (2) inside advance_turn(), (3) post-advance_turn. If auto-charge captures region inside advance_turn(), world_state sets `game_over=True, victory="victory"`. Then turn_manager re-checks and could override. Currently results agree, but fragile — any state change between checks could cause divergence.
- **Proposed Fix:** Single authoritative victory check point.
- **Test Coverage:** No

### [V2-65] [COMBAT] Broken Marshals Teleport to Enemy-Occupied Capital — Spawn Into Enemy Territory
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** executor.py:3042, world_state.py:5317
- **Description:** When surrounded and broken, marshals teleport to `spawn_location` (nation capital). No check that capital is still friendly. French marshal spawns into enemy-occupied Paris (with enemy garrison of up to 15k). Stuck in broken state in enemy territory. Same bug for all nations (e.g., Prussian marshal spawns to enemy-occupied Berlin).
- **Proposed Fix:** Check if capital is friendly; if not, find nearest friendly region.
- **Test Coverage:** No

### [V2-66] [SAVE] _capital_proximity_last_alert Not Serialized — Alert Dedup Lost on Load
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** turn_manager.py:708
- **Description:** Tracks which enemy/capital pairs already triggered alerts. Set on WorldState by TurnManager but NOT in to_dict/from_dict. After save/load, dedup state lost — player sees repeated capital proximity alerts.
- **Test Coverage:** No

### [V2-67] [SAVE] _prev_war_exhaustion Not Serialized — Trend Off After Load
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** world_state.py:3538
- **Description:** Dict snapshot for war exhaustion trends. Not serialized. Graceful degradation (getattr default {}), but trend = 0 for one turn after load.
- **Test Coverage:** No

### [V2-68] [SAVE] _relation_deltas_this_turn Not Serialized — Mid-Turn Save Loses Diplomatic Tracking
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** world_state.py:549-552
- **Description:** Per-turn relation change tracking for diplomatic display. Not serialized. Mid-turn save/load loses all relation change data for current turn.
- **Test Coverage:** No

### 3A: Godot Frontend Comprehensive Review

### [V2-69] [GODOT] api_client.gd Overrides `success` to `true` on Every HTTP 200 — Backend Errors Invisible
- **Severity:** CRITICAL
- **Category:** NEW_BUG
- **File:** api_client.gd:216
- **Description:** `_on_request_completed` unconditionally sets `response_data["success"] = true` for every HTTP 200. FastAPI backend returns `{"success": false, ...}` with HTTP 200 for application errors. ALL error paths in main.gd that check `response.success == false` can NEVER fire. Validation errors, "war is over", "no command given" — all silently appear as successes.
- **Proposed Fix:** Remove the `response_data["success"] = true` override. Let backend's success field pass through.
- **Test Coverage:** No

### [V2-70] [GODOT] Bombardment Report Double Percentage Conversion — Shows 8000% Instead of 80%
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** main.gd:1216-1236
- **Description:** Backend sends `terrain_modifier: int(terrain_mod * 100)` (e.g., 80). Godot reads with default `1.0` and does `int(terrain_mod * 100)` again → 8000. Same for `fort_old` and `fort_new`. Player sees wildly wrong percentages.
- **Proposed Fix:** Remove the second `* 100` in main.gd, or read backend values directly as integers.
- **Test Coverage:** No

### [V2-71] [GODOT] Load Game Missing AP, Diplomatic State, War Panel Restoration
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** main.gd:2367-2398
- **Description:** `/load` endpoint returns only `success`, `message`, `game_state`. Missing: `actions_remaining`, `max_actions`, `admin_actions_remaining`, `diplomatic_points`, `threat_level`, `active_wars`. AP counters show stale pre-load values. Diplomatic top bar update is no-op. War panel shows stale data.
- **Proposed Fix:** Include full state in load response, or make load trigger a state refresh endpoint.
- **Test Coverage:** No

### [V2-72] [GODOT] Connection Test Failure Leaves Input Permanently Disabled
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** main.gd:509-512
- **Description:** `_ready()` disables input. On successful connection, re-enables. On FAILURE — input never re-enabled. Player stuck with no retry mechanism, must restart Godot.
- **Proposed Fix:** Re-enable input on failure with retry prompt.
- **Test Coverage:** No

### [V2-73] [GODOT] Single HTTPRequest Race Condition — ERR_BUSY Leaves Input Disabled Forever
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** api_client.gd:5-12, 18-19
- **Description:** Single `HTTPRequest` node with single `pending_callback`. If second request issued while first in flight, `pending_callback` overwritten. `ERR_BUSY` from Godot only printed, not handled — callback never fires, input stays disabled forever. Edge cases: rapid clicking before disable takes effect, load dialog flow not returning early.
- **Test Coverage:** No

### [V2-74] [GODOT] Load Game Turn Display Shows "5" Instead of "5/40"
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** main.gd:2383
- **Description:** After load, `turn_value.text = str(current_turn)` loses the "/max_turns" suffix. Normal update path shows "5/40". Cosmetic until next command.
- **Test Coverage:** No

### [V2-75] [GODOT] Early Returns in _on_command_result Skip Diplomatic Top Bar Update
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** main.gd:770-892
- **Description:** 13+ early return paths (objections, popups, dialogues) all skip `_update_diplomatic_top_bar`. Diplomatic points, threat level, envoy count become stale during popup sequences.
- **Test Coverage:** No

### [V2-76] [GODOT] Pending State Not Cleared on Load — Stale Popup Data Persists
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** main.gd:48, 2367-2398
- **Description:** `_on_load_result` doesn't clear `pending_enemy_phase_response`, `pending_strategic_response`, `pending_dispatch_data`, `pending_redemption`, `interrupt_queue`, `_cached_wars`. Stale data persists across loads.
- **Test Coverage:** No

### [V2-77] [GODOT] Backend Keys `show_independent_command_report` and `tactical_events` Silently Dropped
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** main.gd (missing), main.py:954-962
- **Description:** Backend generates and includes these in /command response but main.gd never reads them. Supply attrition reports and independent command reports invisible to player.
- **Test Coverage:** No

### 3D: Code Quality Sweep

### [V2-78] [CODE] Hardcoded "Paris" in _exposes_capital() — Breaks Non-France Player Nations
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** personality.py:378
- **Description:** `capital = "Paris"` hardcoded. Used by disobedience system. Breaks if game supports non-France player nation. Should use `NATION_CAPITALS.get(marshal.nation, "Paris")`.
- **Test Coverage:** No

### [V2-79] [CODE] Hardcoded "Paris" in resolve_direction() — "move back" Always Goes to Paris
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** strategic_parser.py:106
- **Description:** "move back/home/rear" resolves to Paris unconditionally. Non-France marshals sent toward Paris instead of their capital. Should use `NATION_CAPITALS.get(world.player_nation, "Paris")`.
- **Test Coverage:** No

### [V2-80] [DOCS] SYSTEMS_REFERENCE Says Admin AP Gold = 75g — Code Uses 25g
- **Severity:** MAJOR
- **Category:** DESIGN
- **File:** SYSTEMS_REFERENCE.md:2196 vs world_state.py:2269
- **Description:** Doc says "Unused admin AP * 75 = gold bonus" but code uses `admin_actions_remaining * 25`. Was changed in Session 12 from 35g to 25g but doc never updated (shows original 75g which was likely never correct).
- **Proposed Fix:** Update SYSTEMS_REFERENCE to match code.
- **Test Coverage:** N/A

### [V2-81] [CODE] AI max_free_actions Safety Limit Assigned But Never Checked
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** enemy_ai.py:686
- **Description:** `max_free_actions = 2` intended as safety cap on free actions but `free_action_count` is never compared against it. Guard was planned but never wired.
- **Test Coverage:** No

### [V2-82] [DOCS] SAVE_FORMAT_REFERENCE Missing 3 Serialized WorldState Fields
- **Severity:** MINOR
- **Category:** DESIGN
- **File:** SAVE_FORMAT_REFERENCE.md
- **Description:** Missing: `ai_stagnation_turns`, `ai_attack_futility`, `last_redemption_turn`. Doc last updated 2026-03-08, hasn't been updated for systems audit sessions.
- **Test Coverage:** N/A

### [V2-83] [DOCS] SYSTEMS_REFERENCE Missing Session 11-12 Balance Changes
- **Severity:** MINOR
- **Category:** DESIGN
- **File:** SYSTEMS_REFERENCE.md
- **Description:** Not documented: VICTORY_REGION_FRACTION=0.75, British naval income scaling, infantry regen reduced by war exhaustion, futility decay 1/turn, admin AP gold 25g.
- **Test Coverage:** N/A

### [V2-84] [CODE] 7 Stale TODO Comments in diplomacy.py Reference Already-Wired Work
- **Severity:** NOTE
- **Category:** ARCHITECTURE
- **File:** diplomacy.py:1632-1651
- **Description:** TODOs reference "Session 5/7" work (defection cascade, vassal loyalty, rebellion, war exhaustion, threat, coalition) already implemented in world_state.py:advance_turn(). Misleadingly suggest work hasn't been done.

---

## Phase 4: STRESS PATTERNS

### 4A: Victory/Defeat Edge Cases

### [V2-85] [PACING] No Warning System for Time Running Out — Player Blindsided by Defeat
- **Severity:** MAJOR
- **Category:** DESIGN
- **File:** turn_manager.py:711, dispatch.py (absent)
- **Description:** Zero warning that time is running out. Turn counter shows "Turn X" with no reference to max_turns (40). Morning Dispatch has no time-pressure trigger. No notification type for turn limit. Player on turn 38 with 13 regions has no in-game signal they're about to lose.
- **Proposed Fix:** Add dispatch triggers at turns 35 ("5 turns remain"), 38 ("Final turns!"), 39 ("Last turn").
- **Test Coverage:** No

### [V2-86] [PACING] Victory Swallows Pending Diplomatic Popups — Lost Narrative Climax
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** main.py:982-989, main.gd:947-949
- **Description:** When enemy_phase is present (always on end_turn), diplomatic popups are DEFERRED. If victory fires same turn, the game_over guard blocks future commands. Deferred popups (coalition declarations, diplomatic proposals, sabotage discovery) are permanently lost — player never sees them. Game's narrative climax may be swallowed.
- **Test Coverage:** No

### [V2-87] [PACING] Auto-Charge Victory Does Not Short-Circuit advance_turn Processing
- **Severity:** MINOR
- **Category:** DESIGN
- **File:** world_state.py:5376, 3870
- **Description:** Auto-charge can capture winning region inside advance_turn(). Remaining ~300 lines of processing (coalition, income, manpower, etc.) still execute for a turn that effectively never begins. No early exit. Harmless but wastes cycles and could fire events on a won game.
- **Test Coverage:** No

### [V2-88] [PACING] Double Victory Check With Fragile Overwrite Ordering
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** world_state.py:3870-3878, turn_manager.py:171-175
- **Description:** world_state sets game_over inside advance_turn, then turn_manager sets it again after advance_turn returns. Currently agree, but if auto-charge destroyed last player marshal (defeat) while also holding enough regions for victory (time check), the world_state would set "victory" and turn_manager would overwrite with "defeat". Defeat SHOULD win, so the ordering is technically correct, but fragile.
- **Test Coverage:** No

### 4B: Simultaneous State Transitions

### [V2-89] [DIPLOMACY] pending_diplomatic_dialogue Is Single-Field — Multiple Systems Silently Overwrite
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** vassal.py:362, diplomacy.py:1104, diplomatic_defiance.py:772, coalition.py:598
- **Description:** `pending_diplomatic_dialogue` can only hold ONE blocking dialogue at a time. Four systems write to it during the same advance_turn: (1) alliance paradox from armistice expiration, (2) vassal rebellion imminent, (3) sabotage discovery from dispatch, (4) coalition formation can void it. Execution order determines which survives. **Alliance paradox dialogue — a blocking player choice to honor/break alliance — is always lost** because it fires earliest (diplomacy step) and gets overwritten by vassal/sabotage steps later.
- **Proposed Fix:** Use a dialogue queue (list) instead of single field, processed in priority order.
- **Test Coverage:** No

### [V2-90] [DIPLOMACY] Multiple Vassal Rebellions Overwrite Popup and Dialogue — First Lost
- **Severity:** MAJOR
- **Category:** NEW_BUG
- **File:** vassal.py:362-389
- **Description:** If two vassals both reach loyalty ≤10 in same `process_vassal_loyalty()`, each iteration overwrites `world.vassal_rebellion_imminent_popup` and `world.pending_diplomatic_dialogue`. First vassal's warning is silently lost. Realistic scenario: Puppet (-4/turn) and Satellite (-2/turn) both drifting toward crisis.
- **Test Coverage:** No

### [V2-91] [COMBAT] Auto-Charge Region Capture Changes Retreat Destinations for Later Charges
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** world_state.py:5295-5330, 5365-5378
- **Description:** Auto-charge A captures region (controller changes). Auto-charge B's target needs retreat — `get_safe_retreat_destination` reads LIVE controller state. Region that was "friendly" for retreat is now enemy-controlled, potentially causing encirclement (broken) when retreat was previously available.
- **Test Coverage:** No

### [V2-92] [COMBAT] Auto-Charge Can Double-Attack Retreating Marshal
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** world_state.py:5298-5311, 5205-5206
- **Description:** `_find_nearest_enemy_for_nation` doesn't filter retreating marshals. Auto-charge A forces enemy to retreat to region R. Auto-charge B targets same enemy at new location R. Already-wounded retreating marshal gets attacked again.
- **Test Coverage:** No

### [V2-93] [COMBAT] Broken Marshal Spawn at Battle Location Is No-Op — Stays in Enemy Territory
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** executor.py:3048
- **Description:** If spawn_location equals battle location (e.g., fighting in Paris when Paris is capital), `move_to(spawn_loc)` is a no-op. Broken marshal remains alongside victorious enemy. Rebuilds army in enemy-controlled territory.
- **Test Coverage:** No

### [V2-94] [DIPLOMACY] Sabotage Discovery Overwrites Vassal Rebellion Dialogue
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** dispatch.py:772, vassal.py:362
- **Description:** Dispatch runs AFTER advance_turn. If vassal rebellion set `pending_diplomatic_dialogue` during advance_turn, and sabotage discovery fires in dispatch, sabotage overwrites the vassal dialogue. When vassal popup eventually delivers, its dialogue handler finds a sabotage confrontation dialogue instead.
- **Test Coverage:** No

### [V2-95] [DIPLOMACY] Multiple Rebellion Cascades Apply Cumulative Loyalty Penalty
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** vassal.py:442-512, 477
- **Description:** Each rebellion applies -10 loyalty to all other vassals. Two simultaneous rebellions = -20 to remaining vassals, potentially triggering chain rebellion that's missed until next turn (rebellion list already collected).
- **Test Coverage:** No

### 4C+4D: Economy Extremes + AI Behavior

### [V2-96] [ECONOMY] AI Gets 75g Per Unused Admin AP vs Player's 25g — 3x Hidden Advantage
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** enemy_ai.py:4273 vs world_state.py:2269
- **Description:** AI gets `unused_ap * 75` gold bonus, player gets `admin_actions_remaining * 25`. If both save 2 admin AP: AI gets 150g, player gets 50g. Undocumented asymmetry. May be intentional to compensate for AI's inability to make nuanced economic decisions, but could surprise players who check the math.
- **Proposed Fix:** Align values or document the intentional asymmetry.
- **Test Coverage:** No

### [V2-97] [ECONOMY] Bankruptcy Desertion Loop Self-Limiting But Takes ~70 Turns
- **Severity:** NOTE
- **Category:** DESIGN
- **File:** world_state.py:2416-2527
- **Description:** 0-income nation with surviving marshals: upkeep halved (mercy), 5% desertion at bankruptcy_turns≥3. 30k marshal takes ~70 turns to shrink below 1000 (where upkeep=0). 40-turn game limit makes this academic. System is self-limiting, no infinite loop possible.
- **Test Coverage:** Yes (bankruptcy tests exist)

### [V2-98] [AI] Supply Awareness Priority Too Low — AI Stacks Before Checking Capacity
- **Severity:** MINOR
- **Category:** DESIGN
- **File:** enemy_ai.py:1539-1589
- **Description:** Supply check is P6.5 — lower than attack (P4), defense (P3), threat response (P3), homeland defense (P3.7). AI stacks 3+ marshals for combat first, considers relocating only if nothing else to do. At 6% max attrition, deathball of 100k loses 6k/turn. AI reliably stacks and takes attrition when priorities align.
- **Test Coverage:** No

### [V2-99] [ECONOMY] Continental System Floor Can Swallow Non-Trade Gold
- **Severity:** MINOR
- **Category:** NEW_BUG
- **File:** diplomacy.py:2300-2303
- **Description:** `max(0, nation_gold - blocked)` operates on total gold, not just trade portion. If member has low gold from other sources, Continental System penalty is effectively reduced by the floor. System is more lenient on poor nations than intended. Minor asymmetry.
- **Test Coverage:** No

---

## GRAND TOTAL

| Phase | CRITICAL | MAJOR | MINOR | NOTE | Total |
|-------|----------|-------|-------|------|-------|
| Phase 1: Verification | 0 | 2 | 2 | 14 | 18 |
| Phase 2: Second-Order | 1 | 13 | 9 | 3 | 26 |
| Phase 3: Unexplored | 2 | 11 | 14 | 4 | 31 |
| Phase 4: Stress | 0 | 4 | 9 | 11 | 24 |
| **TOTAL** | **3** | **30** | **34** | **32** | **99** |

### Top Priority Fixes

**CRITICAL (fix immediately):**
1. **V2-44** — Auto-charge attacker forced retreat has no surrounded fallback → zombie marshal
2. **V2-69** — api_client.gd overrides `success` to true on every HTTP 200 → backend errors invisible
3. *(V2-5 LLM fog leak is MAJOR, not critical — only affects anthropic mode)*

**MAJOR — Code Bugs (fix before playtest):**
4. **V2-5** — LLM prompt still leaks all enemy positions/strengths through fog of war
5. **V2-65** — Broken marshals teleport to enemy-occupied capital
6. **V2-45** — Auto-charge missing fortification defense bonus for defenders
7. **V2-46** — Auto-charge attacker retreat uses post-retreat enemy location (retreats toward enemy)
8. **V2-47** — Auto-charge missing leapfrog check (can jump over enemy armies)
9. **V2-50** — Glorious charge + auto-charge missing Win/Loss relationship processing
10. **V2-70** — Bombardment report double percentage conversion (shows 8000% instead of 80%)
11. **V2-71** — Load game doesn't restore AP, diplomatic state, or war panel
12. **V2-72** — Connection test failure leaves input permanently disabled
13. **V2-73** — Single HTTPRequest race condition can leave input permanently disabled
14. **V2-89** — pending_diplomatic_dialogue is single field — alliance paradox dialogue silently lost
15. **V2-90** — Multiple vassal rebellions overwrite popup/dialogue — first lost

**MAJOR — Design Issues (fix before EA):**
16. **V2-20/21** — AI cooldowns still tick 4x per turn (per-nation not per-turn)
17. **V2-27** — Davout free unfortify resets decay timer (HOLD decay change ineffective)
18. **V2-29** — Supply attrition can create 0-strength zombie marshals
19. **V2-30** — Strategic Ledger economy tab omits trade income
20. **V2-55** — Marshal name "ney" matches inside common words
21. **V2-56** — "dig in" maps to fortify in mock but HOLD in strategic parser
22. **V2-57** — Strategic parser bare verbs partially dead code
23. **V2-63** — Victory threshold mismatch (0.77 vs 0.75)
24. **V2-78/79** — Hardcoded "Paris" in personality + strategic parser
25. **V2-80** — SYSTEMS_REFERENCE documents wrong admin AP gold value
26. **V2-85** — No warning system for time running out
27. **V2-86** — Victory swallows pending diplomatic popups

**MAJOR — Test Quality:**
28. **V2-35** — 3 test classes re-implement production logic (testing the mock)
29. **V2-36** — Combat tests with conditional assertions (may never execute)
30. **V2-37** — 46 test methods with zero assertions

### Key Patterns Discovered

1. **Triple post-combat duplication** (V2-1, V2-44-54): The #1 root cause. `_execute_attack`, `_execute_glorious_charge`, and `_process_reckless_cavalry_turn_start` each have independent ~300-line post-combat blocks. Auto-charge is the most degraded copy (missing 8+ systems). Extracting a shared function would fix 12 bugs at once.

2. **pending_diplomatic_dialogue single-field overwrite** (V2-89, V2-90, V2-94): Multiple systems write to this field during the same advance_turn. Last writer wins. Alliance paradox (a blocking player choice) is always lost. Needs a dialogue queue.

3. **Godot success flag override** (V2-69): Masks ALL backend application errors. Single-line fix with massive impact on error visibility.

4. **Unserialized transient state** (V2-66, V2-67, V2-68): Several fields set by TurnManager on WorldState are not serialized. Graceful degradation but data loss on save/load.

5. **AI cooldown per-nation bug** (V2-20, V2-21): Original audit P2-5 was NOT fixed. Cooldowns tick 4x too fast. Simple fix: move decrement to before nation loop.

### Audit Closure

**Completed:** 4 phases, 15 subagent passes
**Total findings:** 99 (3 CRITICAL, 30 MAJOR, 34 MINOR, 32 NOTE)
**Prior audit fixes verified:** 11 confirmed, 3 regressions/unfixed, 1 N/A, 3 deferred
**Test suite:** 6,930 tests pass (3 skipped). 46 have zero assertions.

### Areas NOT Reached
- Modding system validation pipeline
- Performance profiling under 40+ turn conditions
- Accessibility review (color contrast, screen reader)
- api_client.gd full HTTPRequest queueing analysis
- Godot popup scene files (.tscn) structural review
