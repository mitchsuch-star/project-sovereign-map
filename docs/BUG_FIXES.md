# Bug Fixes

> **Consolidated bug tracker.** All open bugs from playtest reviews, audits, and design fixes live here.
> Iterate sessions until clean, then move to `DESIGN_REFINEMENT.md`.
>
> **Last Updated:** April 5, 2026

---

## Summary

| Priority | Count | Status |
|----------|-------|--------|
| P0 — CRITICAL | 3 | Open |
| P1 — MAJOR | 18 | Open |
| P2 — MINOR | 7 | Open |
| P3 — BALANCE | 4 | Open |
| **Total** | **32** | |

**Estimated new tests:** ~165

**Duplicates resolved:** PT-1 = C3 (merged into C3). DLF-6 superseded by DLF-12 (13-site consolidation).

---

## P0 — CRITICAL (Game-Breaking)

### C1: Armistice Stranded Marshal Deadlock
- **Source:** Playtest Review (Mar 24)
- **Summary:** After armistice, enemy marshal (Gneisenau, 17k) stranded in French territory 10+ turns. French forces deadlocked — can't attack due to armistice, can't leave due to engagement check.
- **Fix:**
  - Change engagement check from `m.nation != marshal.nation` to `world.is_at_war(marshal.nation, m.nation)`
  - Add `_force_retreat_displaced_marshals()` in `cleanup_war_end()` to auto-retreat enemies from now-peaceful territory
  - Optional: AI Priority 0.5 retreat trigger when in hostile territory and not at war
- **Files:** `executor.py` (~line 3898), `diplomacy.py` (cleanup_war_end), `enemy_ai.py`
- **Est. Tests:** ~15

### C2: Same-Nation Self-Combat
- **Source:** Playtest Review (Mar 24)
- **Summary:** British forces fighting themselves (Wellington vs Wellington, Uxbridge vs Wellington) across multiple turns. Wellington strength dropped 52k to 37k partly from self-combat.
- **Fix:**
  - Hard guard in `resolve_battle()`: if attacker.nation == defender.nation, return cancelled
  - Audit `_fuzzy_match_enemy()` and region-based target resolution for same-nation selection
  - Pre-execution validation in enemy AI before `executor.execute()`
- **Files:** `combat.py` (resolve_battle), `executor.py` (_fuzzy_match_enemy), `enemy_ai.py`
- **Est. Tests:** ~10

### C3: Turn Counter Skip (Turn 2 to 4)
- **Source:** Playtest Review (Mar 24) + Playtest Audit PT-1 (Mar 29)
- **Summary:** Turn ends, game skips a full turn. Player loses entire turn of action economy. Multiple trigger paths confirmed: auto-end-turn + explicit end_turn same cycle, autonomous marshal fresh TurnManager, redundant force_end_turn.
- **Fix:**
  - Replace R20 idempotency guard with `_turn_advance_in_progress` re-entrancy flag
  - Set at START of `advance_turn()`, clear at end; reject re-entrant calls
  - Debug logging before all 3 `advance_turn()` sites in turn_manager.py + auto-end-turn in executor.py
- **Files:** `world_state.py`, `turn_manager.py`, `executor.py`
- **Est. Tests:** ~8

---

## P1 — MAJOR

### M1: Raw Internal State Name in Diplomacy Message
- **Source:** Playtest Review (Mar 24)
- **Summary:** Message shows "Armistice Losing" (raw internal type) with wrong article ("a Armistice").
- **Fix:** Use `PROPOSAL_TYPE_DISPLAY` dict; fix article selection.
- **Files:** `executor.py` or `diplomacy.py`
- **Est. Tests:** ~3

### M2: "recruit infantry at Paris" Fails to Parse
- **Source:** Playtest Review (Mar 24)
- **Summary:** Natural phrasing without marshal name fails. "Davout recruit at Paris" works.
- **Fix:** Add "recruit [type] at [location]" pattern to mock parser; auto-assign to highest-strength marshal at location.
- **Files:** `llm_client.py`, `parser.py`
- **Est. Tests:** ~5

### M3: No Recruit Type/Amount Control
- **Source:** Playtest Review (Mar 24)
- **Summary:** Recruitment auto-chosen by marshal type, no player control over type or amount.
- **Fix:** Allow "recruit infantry for Ney" or "recruit 3000 at Belgium"; parse type and amount.
- **Files:** `economy_executor.py`, `llm_client.py`
- **Est. Tests:** ~8

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
- **Files:** `combat_executor.py`, `executor.py`
- **Est. Tests:** ~4

### PT-5: Pursue/Support Bypass Armistice, Waste AP
- **Source:** Playtest Audit (Mar 29)
- **Summary:** "Ney, pursue Wellington" during armistice consumes 2 AP before war-status check. Contradictory message ("spotted... engaging... unknown target").
- **Fix:** Pre-validate diplomatic status BEFORE AP consumption in strategic_executor.py. Return diplomatic error with 0 AP cost.
- **Files:** `strategic_executor.py`
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

### DLF-7: Eliminated Nations in War Cascades
- **Source:** Diplo Ledger Fixes
- **Summary:** `_process_war_cascade()` iterates all nations without filtering eliminated ones. Dead nations pulled into phantom wars.
- **Fix:** Filter eliminated nations at cascade loop start.
- **Files:** `diplomacy.py`
- **Est. Tests:** ~3

### DLF-9: P3 Proposal Skips Upgrade Path Validation
- **Source:** Diplo Ledger Fixes
- **Summary:** P3 (Threat > 60) proposes states directly based on relation thresholds without checking valid upgrade path. Also off-by-one on boundary.
- **Fix:** Replace manual checks with `_determine_upgrade_type()` call (same as P4).
- **Files:** `ai_diplomacy.py`
- **Est. Tests:** ~6

### DLF-11: Eliminated Nations Not Filtered (13 Sites)
- **Source:** Diplo Ledger Fixes
- **Summary:** 13+ nation-iteration sites process eliminated nations (relation changes, manpower regen, income, ledger). Phantom behavior accumulates.
- **Fix:** Add `get_active_nations()` helper to WorldState; replace raw nation lists at 13 sites across 5 files.
- **Files:** `world_state.py`, `diplomacy.py`, `ai_diplomacy.py`, `diplomatic_ledger.py`, `vassal.py`
- **Est. Tests:** ~11

### DLF-12: AI Movement Missing Diplomatic Permission (13 Sites)
- **Source:** Diplo Ledger Fixes (supersedes DLF-6)
- **Summary:** AI never calls `can_enter_territory()` in movement selection. All 13 paths pick destinations by enemy presence/distance but skip diplomatic permission. Executor rejects, AI wastes action.
- **Fix:** Add `_can_ai_move_to()` helper; insert as first filter in all 13 adjacent-region loops. Special cases for capital recapture, retreat fallback, coordinated staging.
- **Files:** `enemy_ai.py`
- **Est. Tests:** ~9

### N2: Offensive Alliance Cascade on War Declaration
- **Source:** Diplomacy Design Fixes (DA-3)
- **Summary:** Only defender's allies auto-join wars. Aggressor's ALLIANCE allies don't join. ALLIANCE is "offensive + defensive" per spec but only defensive half coded.
- **Fix:** Expand `_process_war_cascade()` — nations with ALLIANCE (not DA) with aggressor join war against target. Handle recursion, vassal skip, alliance paradox popup.
- **Files:** `diplomacy.py`
- **Est. Tests:** ~7

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
- **Summary:** Drouot (25k) morale dropped to 6% without direct fighting. Likely proximity/supply attrition chain.
- **Fix:** Cap bystander morale loss from proximity/supply attrition.
- **Files:** `combat.py`, `world_state.py`
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
- **Fix:** Cap total defense modifier at ~50%, OR reduce fortification degradation, OR bombardment strips fortification before assault.
- **Files:** Combat system
- **Est. Tests:** ~5

### B2: Supply Attrition Death Spiral
- **Source:** Playtest Review (Mar 24)
- **Summary:** Belgium supply cap 25k; 2-3 marshals (80-100k) cause ~4k losses/turn. Staging area destroys army.
- **Fix:** Increase supply cap for towns, OR add meaningful supply depot building, OR reduce attrition to 1%.
- **Files:** Supply system
- **Est. Tests:** ~3

### B3: Enemy AI Gets Too Many Attacks Per Turn
- **Source:** Playtest Review (Mar 24)
- **Summary:** 3 enemies = 9-12 actions/turn vs player's 4 AP. Gneisenau attacked 4x/turn.
- **Fix:** Ensure enemy action budget visible/transparent, OR reduce per-turn actions.
- **Files:** `enemy_ai.py`
- **Est. Tests:** ~3

### B4: Gold Accumulates With No Outlet
- **Source:** Playtest Review (Mar 24)
- **Summary:** 8,700g treasury climbing 700g/turn. Building limited, recruitment capped. No fast gold sink.
- **Fix:** Allow multiple recruits, OR add mercenaries/diplomatic gifts/forced march supplies.
- **Files:** Economy system
- **Est. Tests:** ~5

### N3: Coalition Friction in Attack Scoring
- **Source:** Diplomacy Design Fixes (DA-3)
- **Summary:** Coalition friction only affects ally-support movement, not attack scoring. Cross-coalition allies excluded from co-location bonus entirely.
- **Fix:** Expand co-location check to include cross-nation coalition allies modulated by friction.
- **Files:** `enemy_ai.py`, `coalition.py`
- **Est. Tests:** ~5

---

## V3 Session 11 — Optional Polish

~15 trivial items (dead code, cosmetics, dedup). No bugs, pure cleanup. See `docs/SYSTEMS_AUDIT_V3_FIX_PLAN.md` Session 11 for full list. Zero new tests.

---

## Session Plan

Sessions should be grouped by priority and file proximity. Suggested groupings:

| Session | Items | Focus | Est. Tests |
|---------|-------|-------|------------|
| 1 | C1, C2, C3 | Critical game-breakers | ~33 |
| 2 | PT-2, PT-4, PT-5, M1 | Parse + diplomatic error messages | ~17 |
| 3 | M2, M3, m1 | Recruitment + command routing | ~16 |
| 4 | DLF-11, DLF-7, DLF-12 | Eliminated nations + AI movement (systemic) | ~23 |
| 5 | DLF-2, DLF-4, DLF-5 | Mission stubs (UNDERMINE, COURT, GATHER_INTEL) | ~22 |
| 6 | DLF-1, DLF-3, DLF-8, DLF-9, DLF-10 | Ledger display + diplomacy guards | ~17 |
| 7 | N2, PT-3, PT-7, m2, m3, m4 | Cascade + emoji + minor fixes | ~20 |
| 8 | B1-B4, N3, PT-6 | Balance + enhancement | ~24 |

**Total: ~8 sessions, ~165 new tests.**

---

## Source Documents (Archived Reference)

These docs are now superseded by this consolidated tracker. Keep for implementation detail reference:

| Document | Items Moved Here |
|----------|-----------------|
| `docs/PLAYTEST_REVIEW_2026_03.md` | C1-C3, M1-M3, m1-m4, B1-B4 |
| `docs/PLAYTEST_AUDIT_2026_03_29.md` | PT-1 through PT-7 |
| `docs/DIPLO_LEDGER_FIXES_SPEC.md` | DLF-1 through DLF-12 |
| `docs/DIPLOMACY_DESIGN_FIXES.md` | DA-3 (N2, N3) |
| `docs/SYSTEMS_AUDIT_V3_FIX_PLAN.md` | Session 11 (optional) |
