# Bug Fixes

> **Consolidated bug tracker.** All open bugs from playtest reviews, audits, and design fixes live here.
> Iterate sessions until clean, then move to `DESIGN_REFINEMENT.md`.
>
> **Last Updated:** April 5, 2026

---

## Summary

| Priority | Count | Status |
|----------|-------|--------|
| P0 — CRITICAL | 0 | All fixed |
| P1 — MAJOR | 10 | Open (DLF-7, DLF-11, DLF-12 closed) |
| P2 — MINOR | 8 | Open |
| P3 — BALANCE | 4 | Open |
| **Total** | **22** | |

**Estimated new tests:** ~118

**Duplicates resolved:** PT-1 = C3 (merged into C3). DLF-6 superseded by DLF-12 (13-site consolidation).

**Closed this audit:**
- **C1** (Armistice Stranded Marshal Deadlock): FIXED — `is_at_war()` guards added, `_force_retreat_displaced_marshals()` in diplomacy.py:466
- **C2** (Same-Nation Self-Combat): FIXED — guard in `resolve_battle()` (combat.py:178), `get_enemy_by_name_for_nation()` prevents same-nation matches
- **C3** (Turn Counter Skip): FIXED — `_last_advanced_turn` idempotency guard in world_state.py:3872
- **M1** (Raw Internal State Name): FIXED — `PROPOSAL_TYPE_DISPLAY` in display_names.py:122, used in diplomatic_executor.py
- **M3** (No Recruit Type/Amount Control): BY DESIGN — marshals always recruit their own unit type (artillery/cavalry/infantry). This is intentional identity design, not a bug. Documented in SYSTEMS_REFERENCE.md §Recruitment and CLAUDE.md troubleshooting
- **N2** (Offensive Alliance Cascade): FIXED — aggressor ALLIANCE cascade in diplomacy.py:1235-1280
- **B3** (Enemy AI AP Rebalancing): REJECTED — deferred to post-full-map. See DESIGN_REFINEMENT.md
- **B4** (Gold Accumulates): DESIGN GATE — already tracked in DESIGN_REFINEMENT.md
- **DLF-11** (Eliminated Nations Not Filtered): FIXED — `get_active_nations()` helper on WorldState, 23 sites updated across 9 files, vassals always active. 17 new tests
- **DLF-7** (Eliminated Nations in War Cascades): FIXED — already resolved by DLF-11's `get_active_nations()` at diplomacy.py:1182. 3 verification tests added
- **DLF-12** (AI Movement Missing Diplomatic Permission): FIXED — `_can_ai_move_to()` helper on EnemyAI wrapping `can_enter_territory()`. 17 movement destination sites patched in enemy_ai.py. Capital recapture exempt. 16 new tests

---

## P0 — CRITICAL (Game-Breaking)

All P0 bugs resolved. See "Closed this audit" above.

---

## P1 — MAJOR

### M2: "recruit infantry at Paris" Fails to Parse
- **Source:** Playtest Review (Mar 24)
- **Summary:** Natural phrasing without marshal name fails. "Davout recruit at Paris" works.
- **Fix:** Add "recruit [type] at [location]" pattern to mock parser; auto-assign to highest-strength marshal at location.
- **Files:** `llm_client.py`, `parser.py`
- **Est. Tests:** ~5

### PT-2: Mock Parser "status" Not Recognized
- **Source:** Playtest Audit (Mar 29)
- **Summary:** "status" command returns Berthier confusion. Missing from mock parser and parser.py valid_actions.
- **Fix:** Add "status" keyword to `_parse_with_mock()` and `parser.py` valid_actions.
- **Files:** `llm_client.py`, `parser.py`
- **Est. Tests:** ~4

### PT-4: Armistice Attack Shows "Unknown target"
- **Source:** Playtest Audit (Mar 29)
- **Summary:** "Davout, attack Gneisenau" during armistice returns "Unknown target" instead of diplomatic context error.
- **Fix:** After fuzzy match fails, check if target matches any marshal regardless of war status. If armistice/peace, return diplomatic error.
- **Files:** `executor.py` (_fuzzy_match_enemy ~line 280), `combat_executor.py`
- **Est. Tests:** ~4

### PT-5: Pursue/Support Bypass Armistice, Waste AP
- **Source:** Playtest Audit (Mar 29)
- **Summary:** "Ney, pursue Wellington" during armistice consumes 2 AP before war-status check. Contradictory message ("spotted... engaging... unknown target").
- **Root cause (CONFIRMED):** Order creation (strategic_executor.py:414-430) only checks target *existence*, not war status. AP is consumed in executor.py:1336 on successful return. War-status validation happens next turn in strategic.py:938-941, which cancels the order — but AP is already spent.
- **Fix:** Add `world.is_at_war(marshal.nation, target.nation)` check in strategic_executor.py PURSUE/SUPPORT target validation (~line 414), BEFORE order creation. Return diplomatic error with `variable_action_cost: 0`.
- **Files:** `strategic_executor.py` (~line 414 PURSUE validation, ~line 376 SUPPORT validation)
- **Est. Tests:** ~6

### DLF-1: Vassalizable Icon Shows Ineligible Nations
- **Source:** Diplo Ledger Fixes
- **Summary:** Icon shows for any nation with relation < -10 OR at_war, ignoring diplomatic state requirements.
- **Fix:** Add `VASSAL_MIN_STATES` check — icon only when state in {WAR, OPEN_BORDERS, NON_AGGRESSION, DEFENSIVE_ALLIANCE, ALLIANCE}.
- **Files:** `diplomatic_ledger.py`
- **Est. Tests:** ~2

### DLF-2: UNDERMINE_ALLIANCE Mission Has No Effect
- **Source:** Diplo Ledger Fixes
- **Summary:** Mission accepts commands, deducts 2 DP/turn, but per-turn effect (-3 relation between target pair) never applied. Stub at diplomacy.py:1947.
- **Fix:** Add conversational ally-selection dialogue, store `target_pair`, apply -3/turn relation reduction, auto-cancel if alliance breaks. Update tracker display.
- **Files:** `diplomatic_executor.py`, `diplomacy.py`, `diplomatic_ledger.py`
- **Est. Tests:** ~8

### DLF-3: AI-AI Relations Display Scaling
- **Source:** Diplo Ledger Fixes
- **Summary:** Nations tab lists all AI relations inline — unreadable wall of text at scale.
- **Fix:** Filter to notable states only (WAR, ALLIANCE, DEFENSIVE_ALLIANCE, OPEN_BORDERS, NON_AGGRESSION). Hide PEACE. Empty case: "At peace with all".
- **Files:** `diplomatic_ledger.py`, `diplomatic_ledger.gd`
- **Est. Tests:** ~3

### DLF-4: COURT_NATION Blowback Never Processes
- **Source:** Diplo Ledger Fixes
- **Summary:** COURT_NATION costs 2 DP/turn for 20% blowback risk, but blowback stub never fires. Currently a strictly worse IMPROVE_RELATIONS.
- **Fix:** Process 20% blowback in `_process_mission_effects()` — fixed -3 penalty (not skill-scaled), queue incident event.
- **Files:** `diplomacy.py`
- **Est. Tests:** ~7

### DLF-5: GATHER_INTEL Completes But Reveals Nothing
- **Source:** Diplo Ledger Fixes
- **Summary:** Auto-completes after 3 turns with congratulations but zero intel. Player spends 3 DP for a message.
- **Fix:** Grant temporary FULL visibility on target nation's army strength for 5 turns post-completion. New `intel_grants` field on WorldState with expiry. Serialization required.
- **Files:** `diplomacy.py`, `diplomatic_ledger.py`, `world_state.py`
- **Est. Tests:** ~7

### ~~DLF-7: Eliminated Nations in War Cascades~~ FIXED
- **Source:** Diplo Ledger Fixes
- **Summary:** `_process_war_cascade()` iterates all nations without filtering eliminated ones. Dead nations pulled into phantom wars.
- **Fix:** Already resolved by DLF-11 — `get_active_nations()` at diplomacy.py:1182 filters both cascade loops. 3 verification tests added.
- **Files:** `diplomacy.py` (already patched by DLF-11)
- **Tests:** 3 in `test_bugfix_session2.py`

### DLF-9: P3 Proposal Skips Upgrade Path Validation
- **Source:** Diplo Ledger Fixes
- **Summary:** P3 (Threat > 60) proposes states directly based on relation thresholds without checking valid upgrade path. Also off-by-one on boundary.
- **Fix:** Replace manual checks with `_determine_upgrade_type()` call (same as P4).
- **Files:** `ai_diplomacy.py`
- **Est. Tests:** ~6

### ~~DLF-11: Eliminated Nations Not Filtered (23 Sites)~~ FIXED
- **Source:** Diplo Ledger Fixes + Exhaustive Sweep (Apr 5)
- **Summary:** 23 nation-iteration sites process eliminated nations — phantom behavior accumulates (relation changes, manpower regen, income, war cascades, UI). Helper `_is_nation_eliminated()` exists in diplomacy.py:1625 but is only used in 2 sites.
- **Fix:** Add `get_active_nations()` helper to WorldState; replace raw nation lists at all 23 sites. Use existing `_is_nation_eliminated()` or promote to shared utility.
- **Files (23 sites across 9 files):**
  - `world_state.py` — manpower regen ~line 2436, income ~line 4081, bankruptcy ~lines 3984/4134, treaty ratification ~line 4509 (5 sites)
  - `diplomacy.py` — war declaration penalties ~line 1038, defensive cascade ~line 1184, offensive cascade ~line 1236, downgrade penalties ~line 1348, treaty break penalties ~line 2044, relation decay ~line 2182 (6 sites)
  - `vassal.py` — vassal conflicts ~line 198, loyalty ~line 269, enemy check ~line 549 (3 sites)
  - `coalition.py` — war exhaustion ~line 928 (1 site)
  - `diplomatic_advisory.py` — threat comparison ~line 242, treaty status ~line 511, proposals context ~line 696 (3 sites)
  - `diplomatic_ledger.py` — nations tab ~line 143, nested relations ~line 202 (2 sites)
  - `dispatch.py` — diplomatic observations ~line 637 (1 site)
  - `turn_manager.py` — AI diplomatic phase ~line 289, victory check ~line 720 (2 sites)
- **Est. Tests:** ~18

### ~~DLF-12: AI Movement Missing Diplomatic Permission (17 Sites)~~ FIXED
- **Source:** Diplo Ledger Fixes (supersedes DLF-6)
- **Summary:** AI never calls `can_enter_territory()` in movement selection. 17 paths pick destinations by enemy presence/distance but skip diplomatic permission. Executor rejects, AI wastes action.
- **Fix:** Added `_can_ai_move_to()` helper on EnemyAI wrapping `can_enter_territory()` with region lookup. Patched all 17 movement destination selection sites. Capital recapture exempt (sovereign right). Recovery lock clears when dest becomes blocked.
- **Files:** `enemy_ai.py` (helper + 17 sites)
- **Tests:** 16 in `test_bugfix_session2.py`

---

## P2 — MINOR

### m1: "trust" Doesn't Parse via /command
- **Source:** Playtest Review (Mar 24)
- **Summary:** Typing "trust" into /command returns parse error; must use separate endpoint.
- **Fix:** Route objection keywords in /command endpoint.
- **Files:** `main.py`, `llm_client.py`
- **Est. Tests:** ~3

### m2: Duplicate Counter-Punch Notifications
- **Source:** Playtest Review (Mar 24)
- **Summary:** Davout earned 2 separate counter-punch notifications same turn; stale entries accumulate.
- **Fix:** Dedup logic for counter-punch notifications.
- **Files:** `notifications.py`
- **Est. Tests:** ~2

### m3: Artillery Morale Collapse Without Combat
- **Source:** Playtest Review (Mar 24)
- **Summary:** Drouot (25k) morale dropped to 6% without direct fighting.
- **Root cause (CONFIRMED):** Bombardment (`_execute_bombardment` in combat_executor.py:1526) applies -3 morale base (-18 with square formation) per hit WITHOUT going through `resolve_battle()`. Collateral hits (combat_executor.py:1558) add -1 per stray shell at 40% chance. Chaining 2 bombardments/turn can drain ~6-36 morale/turn. Supply attrition (world_state.py:2600) only affects strength, NOT morale — so supply is not the cause.
- **Fix:** Cap minimum morale from bombardment at forced-retreat threshold (25%), OR add diminishing returns on repeated bombardment morale loss against same target.
- **Files:** `combat_executor.py` (_execute_bombardment ~line 1526, collateral ~line 1558)
- **Est. Tests:** ~3

### m4: Redundant Route Description for Adjacent Move
- **Source:** Playtest Review (Mar 24)
- **Summary:** "Grouchy march to Paris" shows "Route: Paris. Moves to Paris." for 1-hop move.
- **Fix:** Skip route description for adjacent destinations.
- **Files:** `strategic_executor.py`
- **Est. Tests:** ~2

### PT-3: Emoji Encoding Broken (Windows)
- **Source:** Playtest Audit (Mar 29)
- **Summary:** Cavalry warnings show garbled surrogate pairs on Windows. 40+ emoji across 7 files.
- **Fix:** Replace all player-facing emoji with text markers: `[!]`, `[Cavalry]`, `[Combat]`, `[Destroyed]`, etc.
- **Files:** `combat_executor.py`, `world_state.py`, `combat.py`, `meta_executor.py`, `executor.py`, `movement_executor.py`, `tactical_executor.py`
- **Est. Tests:** ~3

### PT-7: bombardment_streak Tracked But Never Used
- **Source:** Playtest Audit (Mar 29)
- **Summary:** Field initialized, serialized, reset per-turn, but bombardment uses fixed 0.10 degradation. Dead code.
- **Fix:** Remove field entirely (or keep with comment if design wants streak scaling later).
- **Files:** `marshal.py`, `combat_executor.py`
- **Est. Tests:** ~1

### DLF-8: Opportunistic Downgrade Doesn't Exclude VASSAL
- **Source:** Diplo Ledger Fixes
- **Summary:** VASSAL missing from downgrade exclusion list. Code fails silently finding VASSAL in `_DOWNGRADE_ORDER`.
- **Fix:** Add VASSAL to exclusion set.
- **Files:** `ai_diplomacy.py`
- **Est. Tests:** ~2

### DLF-10: Armistice Cooldown Missing VASSAL Exclusion
- **Source:** Diplo Ledger Fixes
- **Summary:** Armistice allow-list missing VASSAL. Should be blocked during active armistice.
- **Fix:** Rewrite as inclusive allow-list with VASSAL excluded.
- **Files:** `diplomacy.py`
- **Est. Tests:** ~4

---

## P3 — BALANCE / ENHANCEMENT

### PT-6: No AP Warning on End Turn
- **Source:** Playtest Audit (Mar 29)
- **Summary:** Player ends turn with AP remaining, no warning about unused actions.
- **Fix:** Check actions_remaining > 0 in `_execute_end_turn()`; add warning message. Turn still ends.
- **Files:** `meta_executor.py`
- **Est. Tests:** ~3

### B1: Wellington Defense Stack (~75-85%)
- **Source:** Playtest Review (Mar 24)
- **Summary:** Combined defense modifiers make Wellington nearly unbeatable. 2:1 casualty ratios even with numerical advantage.
- **Spec:** APPROVED — fortify cap 12/8/12, bombardment strips fortification. See `docs/SYSTEMS_REFERENCE.md` §23.
- **Files:** `marshal.py` (get_defense_modifier), `combat_executor.py` (_execute_bombardment), `personality_modifiers.py`
- **Est. Tests:** ~5

### B2: Supply Attrition Death Spiral
- **Source:** Playtest Review (Mar 24)
- **Summary:** Belgium supply cap 25k; 2-3 marshals (80-100k) cause ~4k losses/turn. Staging area destroys army.
- **Spec:** APPROVED — supply caps increased. See `docs/SYSTEMS_REFERENCE.md` §23.
- **Files:** `region.py` (supply_capacity), `world_state.py` (process_supply_attrition)
- **Est. Tests:** ~3

### N3: Coalition Friction in Attack Scoring
- **Source:** Diplomacy Design Fixes (DA-3)
- **Summary:** Coalition friction only affects ally-support movement, not attack scoring. Cross-coalition allies excluded from co-location bonus entirely.
- **Spec:** APPROVED — co-location friction modulated by coalition friction coefficient. See `docs/SYSTEMS_REFERENCE.md` §23 and `docs/COALITION_SPEC.md`.
- **Files:** `enemy_ai.py`, `coalition.py`
- **Est. Tests:** ~5

---

## Suggestions (UX Polish)

### S1: Clearer Feedback for Simple Commands
- **Source:** Playtest (Apr 5)
- **Summary:** Simple commands like "recruit" give minimal feedback. Add clearer confirmation messages showing what happened (e.g., "Davout recruited 2,000 infantry at Paris").
- **Files:** `economy_executor.py`, `tactical_executor.py`, `movement_executor.py`
- **Est. Tests:** ~0 (message-only)

### S2: Auto-Focus Command Input on Terminal Restore
- **Source:** Playtest (Apr 5)
- **Summary:** When returning to the terminal from a screen/popup, the command input field doesn't auto-focus. Player must click it before typing.
- **Files:** `main.gd`
- **Est. Tests:** ~0 (UI-only)

---

## V3 Session 11 — Optional Polish

~15 trivial items (dead code, cosmetics, dedup). No bugs, pure cleanup. See `docs/archive/SYSTEMS_AUDIT_V3_FIX_PLAN.md` Session 11 for full list. Zero new tests.

---

## Session Plan

| Session | Items | Focus | Est. Tests |
|---------|-------|-------|------------|
| 1 | DLF-11 | `get_active_nations()` helper + 23-site eliminated-nation sweep | ~18 |
| 2 | DLF-7, DLF-12 | Cascade filter (uses Session 1 helper) + AI movement permission | ~12 |
| 3 | PT-2, PT-4, PT-5, m1 | Parse + diplomatic error messages | ~17 |
| 4 | M2, m4 | Recruitment parse + movement message polish | ~7 |
| 5 | DLF-2 | UNDERMINE_ALLIANCE mission (dialogue + target_pair + per-turn effect) | ~8 |
| 6 | DLF-4, DLF-5 | COURT blowback + GATHER_INTEL visibility grant | ~14 |
| 7 | DLF-1, DLF-3, DLF-8, DLF-9, DLF-10 | Ledger display + diplomacy guards | ~17 |
| 8 | PT-3, PT-7, m2, m3 | Emoji + dead code + minor fixes | ~9 |
| 9 | B1, B2, N3, PT-6 | Balance (specs approved) + AP warning | ~16 |

**Total: ~9 sessions, ~118 new tests.**

**Dependencies:** Session 1 MUST complete before Session 2 (DLF-7 and DLF-12 use the helper). All other sessions are independent — run in any order after Session 2.

---

### Session Briefings

Each session is self-contained. Clear context between sessions. Paste the briefing below as the session prompt.

#### Session 1 — Eliminated Nations Helper (DLF-11)
> Read: `docs/BUG_FIXES.md` (DLF-11 entry), `CLAUDE.md`
> Task: Add `get_active_nations()` helper to `world_state.py` that filters eliminated nations (0 controlled regions). Replace raw nation iteration at 23 sites across 9 files: `world_state.py` (5), `diplomacy.py` (6), `vassal.py` (3), `coalition.py` (1), `diplomatic_advisory.py` (3), `diplomatic_ledger.py` (2), `dispatch.py` (1), `turn_manager.py` (2). Existing `_is_nation_eliminated()` in diplomacy.py:1625 has the logic. ~18 tests.

#### Session 2 — Cascade Filter + AI Movement (DLF-7, DLF-12)
> Read: `docs/BUG_FIXES.md` (DLF-7, DLF-12 entries), `CLAUDE.md`
> Prereq: Session 1 complete (uses `get_active_nations()` helper).
> Task: DLF-7 — filter eliminated nations in `_process_war_cascade()` in `diplomacy.py`. DLF-12 — add `_can_ai_move_to()` helper in `enemy_ai.py`, insert as first filter in all 13 adjacent-region movement loops. Special cases: capital recapture, retreat fallback. ~12 tests.

#### Session 3 — Parse + Diplomatic Errors (PT-2, PT-4, PT-5, m1)
> Read: `docs/BUG_FIXES.md` (PT-2, PT-4, PT-5, m1 entries), `CLAUDE.md`
> Task: PT-2 — add "status" to mock parser + valid_actions. PT-4 — fallback target match ignoring war status, return diplomatic error. PT-5 — add `is_at_war()` check at strategic_executor.py ~line 414 BEFORE order creation for PURSUE/SUPPORT. m1 — route "trust" keyword in /command endpoint. ~17 tests.

#### Session 4 — Recruitment Parse + Message Polish (M2, m4)
> Read: `docs/BUG_FIXES.md` (M2, m4 entries), `CLAUDE.md`
> Task: M2 — add "recruit [type] at [location]" pattern to mock parser, auto-assign to highest-strength marshal at location. m4 — skip route description for 1-hop adjacent moves in strategic_executor.py. ~7 tests.

#### Session 5 — UNDERMINE_ALLIANCE Mission (DLF-2)
> Read: `docs/BUG_FIXES.md` (DLF-2 entry), `CLAUDE.md`, `docs/DIPLOMACY_SPEC.md` (missions section)
> Task: Implement UNDERMINE_ALLIANCE per-turn effect. Add ally-selection dialogue in diplomatic_executor.py, store `target_pair` on mission, apply -3/turn relation reduction in `_process_mission_effects()` (diplomacy.py), auto-cancel if alliance breaks, update tracker display in diplomatic_ledger.py. ~8 tests.

#### Session 6 — Mission Effects: COURT + GATHER_INTEL (DLF-4, DLF-5)
> Read: `docs/BUG_FIXES.md` (DLF-4, DLF-5 entries), `CLAUDE.md`
> Task: DLF-4 — process 20% blowback in `_process_mission_effects()` (diplomacy.py), fixed -3 penalty, queue incident event. DLF-5 — new `intel_grants` dict on WorldState with expiry, grant FULL visibility on target for 5 turns post-completion, add to `to_dict`/`from_dict`, update SAVE_FORMAT_REFERENCE.md. ~14 tests.

#### Session 7 — Ledger Display + Diplomacy Guards (DLF-1, DLF-3, DLF-8, DLF-9, DLF-10)
> Read: `docs/BUG_FIXES.md` (DLF-1/3/8/9/10 entries), `CLAUDE.md`
> Task: DLF-1 — add VASSAL_MIN_STATES check to vassalizable icon. DLF-3 — filter AI-AI relations to notable states only. DLF-8 — add VASSAL to downgrade exclusion. DLF-9 — replace P3 manual checks with `_determine_upgrade_type()`. DLF-10 — rewrite armistice allow-list excluding VASSAL. ~17 tests.

#### Session 8 — Emoji + Dead Code + Minor Fixes (PT-3, PT-7, m2, m3)
> Read: `docs/BUG_FIXES.md` (PT-3, PT-7, m2, m3 entries), `CLAUDE.md`
> Task: PT-3 — replace 40+ player-facing emoji with text markers across 7 files. PT-7 — remove `bombardment_streak` field (marshal.py, combat_executor.py) + update SAVE_FORMAT_REFERENCE.md. m2 — dedup counter-punch notifications. m3 — cap bombardment morale drain at forced-retreat threshold (25%) in combat_executor.py ~line 1526. ~9 tests.

#### Session 9 — Balance + AP Warning (B1, B2, N3, PT-6)
> Read: `docs/BUG_FIXES.md` (B1/B2/N3/PT-6 entries), `docs/SYSTEMS_REFERENCE.md` §23, `docs/COALITION_SPEC.md`, `CLAUDE.md`
> Task: B1 — fortify cap 12/8/12 + bombardment strips fortification. B2 — increase supply caps per spec. N3 — expand co-location check to include cross-nation coalition allies modulated by friction. PT-6 — AP remaining warning in `_execute_end_turn()`. Playtest after all 4. ~16 tests.

---

## Source Documents (Archived Reference)

These docs are now superseded by this consolidated tracker. Keep for implementation detail reference:

| Document | Items Moved Here |
|----------|-----------------|
| `docs/archive/PLAYTEST_REVIEW_2026_03.md` | C1-C3, M1-M3, m1-m4, B1-B4 |
| `docs/archive/PLAYTEST_AUDIT_2026_03_29.md` | PT-1 through PT-7 |
| `docs/archive/DIPLO_LEDGER_FIXES_SPEC.md` | DLF-1 through DLF-12 |
| `docs/archive/DIPLOMACY_DESIGN_FIXES.md` | DA-3 (N2, N3) |
| `docs/archive/SYSTEMS_AUDIT_V3_FIX_PLAN.md` | Session 11 (optional) |
