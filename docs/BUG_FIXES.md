# Bug Fixes

> **Consolidated bug tracker.** All open bugs from playtest reviews, audits, and design fixes live here.
> Iterate sessions until clean, then move to `DESIGN_REFINEMENT.md`.
>
> **Last Updated:** April 6, 2026

---

## Summary

| Priority | Count | Status |
|----------|-------|--------|
| P0 — CRITICAL | 0 | All fixed |
| P1 — MAJOR | 2 | PL-5, PL-6 OPEN |
| P2 — MINOR | 1 | PL-7 OPEN |
| P3 — BALANCE | 0 | All fixed (Session 5) |
| P2 — MINOR | 0 | All fixed (Session 6: PL-1, PL-2, PL-3, PL-4) |
| **Total** | **3** | **3 open** |

**Estimated new tests:** ~99

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
- **M2** (Recruit Without Marshal Name): FIXED — "recruit" added to meta_actions bypass in parser.py. `requested_type` propagated. 5 tests
- **PT-2** (Status Not Recognized): FIXED — "status" keyword added to mock parser with exact match. 4 tests
- **PT-4** (Armistice Attack Unknown Target): FIXED — secondary fallback in `_fuzzy_match_enemy()` + diplomatic_block check in combat_executor. 4 tests
- **PT-5** (Pursue Bypass Armistice): FIXED — war-status check before order creation in strategic_executor, `variable_action_cost: 0`. 6 tests

---

## P0 — CRITICAL (Game-Breaking)

All P0 bugs resolved. See "Closed this audit" above.

---

## P1 — MAJOR

### PL-5: Player Proposal Resolves Next Turn — No Feedback, Race Condition
- **Source:** Playtest (Apr 6)
- **Summary:** Player sends a diplomatic proposal (e.g., non-aggression to Saxony). Gets "Expect a response by next turn." No indication of accept/reject until morning dispatch (easily missed). Meanwhile, the AI generates its OWN proposal of the same type on the same end-turn, creating a confusing race condition where Saxony rejects the player's harsh terms then immediately proposes a clean non-aggression pact.
- **Root cause:** `execute_proposal` (diplomatic_executor.py:895-994) sets `proposal_in_transit` and `talleyrand_state = "IN_TRANSIT"`. Resolution deferred to `_process_proposal_in_transit()` (world_state.py:4300-4493) which runs inside `advance_turn`. AI proposal generation (`ai_diplomacy.py` P4 check) also runs during `advance_turn` with no awareness that the player just proposed the same thing.
- **Sub-bugs:**
  - (a) No same-turn feedback: player can't tell if proposal was accepted or rejected until next turn's dispatch
  - (b) AI cooldown gap: when player's proposal is rejected, `player_proposal_cooldowns` blocks the *player* from re-proposing, but the AI's separate cooldown system (`_is_on_cooldown` in ai_diplomacy.py) is untouched — AI immediately re-proposes same type
  - (c) `accept_counter_offer` path (diplomatic_executor.py:1773) doesn't call `apply_acceptance_cooldown` — no cooldown after accepting counter-offers
- **Proposed fix:** Resolve player proposals instantly in `execute_proposal` instead of deferring to `advance_turn`. Extract resolution logic from `_process_proposal_in_transit` into a reusable `resolve_proposal_immediately()` method on WorldState. Exception: "stalled" sabotage (Talleyrand deliberately delayed delivery) still defers. Also apply AI cooldowns on player-proposal rejection. Also add `apply_acceptance_cooldown` to counter-offer acceptance.
- **Files:** `diplomatic_executor.py` (execute_proposal + send_override paths), `world_state.py` (new resolve method + _process_proposal_in_transit refactor)
- **Scope:** Large — changes core diplomacy flow. Needs design gate.
- **Est. Tests:** ~8 new + ~6 existing tests updated

### PL-6: "Harsher" Terms on Friendship Pacts Demand Territory — Nonsensical
- **Source:** Playtest (Apr 6)
- **Summary:** Player proposes non-aggression pact to friendly Saxony (OPEN_BORDERS state, positive relations). Clicks "harsher" twice. System demands 150g/turn gold AND 1 territory cession from Saxony — for a *non-aggression pact*. This is extortion, not diplomacy. Saxony reasonably rejects. Player perceives acceptance odds barely changing because demand impact is tiny relative to base disposition.
- **Root cause:** `modify_harsh` handler (diplomatic_executor.py:996-1060) is proposal-type-blind. It blindly adds `gold_per_turn` (100g) and `territory_cede` (1 region) regardless of whether the proposal is a war reparation or a friendship pact. The demand value rates in `DEMAND_VALUES` (diplomacy.py:158) are also weak: gold_per_turn = -0.02/gold (100g = -2 acceptance points), territory_cede = -5/region. Two rounds of escalation only subtract ~7 points from a base of ~40-50, which is barely perceptible.
- **Sub-bugs:**
  - (a) Type-blind escalation: territory demands make no thematic sense for non_aggression, open_borders, defensive_alliance, or alliance proposals
  - (b) Weak demand impact: 100g gold demand = -2 acceptance points. Player clicks "harsher" and sees acceptance barely move.
- **Proposed fix:** Split `modify_harsh` by proposal type category. War resolution (peace, armistice): keep current behavior — gold + territory demands are war reparations. Friendship types (non_aggression, open_borders, defensive_alliance, alliance): cap at modest gold demand (~100g), NO territory demands ever, cap at 1 round of escalation with message "A non-aggression pact cannot bear heavier demands, Sire." For war types, increase gold demand to 300g and territory to 2 so the impact is actually visible.
- **Files:** `diplomatic_executor.py` (modify_harsh handler ~line 996)
- **Est. Tests:** ~5

### ~~M2: "recruit infantry at Paris" Fails to Parse~~ FIXED
- **Source:** Playtest Review (Mar 24)
- **Summary:** Natural phrasing without marshal name fails. "Davout recruit at Paris" works.
- **Fix:** Added "recruit" to `meta_actions` in parser.py (bypasses fuzzy marshal matching). Propagated `requested_type` from LLM result to command dict.
- **Files:** `parser.py`
- **Tests:** 5 in `test_bugfix_session3.py`

### ~~PT-2: Mock Parser "status" Not Recognized~~ FIXED
- **Source:** Playtest Audit (Mar 29)
- **Summary:** "status" command returns Berthier confusion. Missing from mock parser keyword matching.
- **Fix:** Added `elif command_lower.strip() == "status":` to `_parse_with_mock()` in llm_client.py. Exact match prevents false positives.
- **Files:** `llm_client.py`
- **Tests:** 4 in `test_bugfix_session3.py`

### ~~PT-4: Armistice Attack Shows "Unknown target"~~ FIXED
- **Source:** Playtest Audit (Mar 29)
- **Summary:** "Davout, attack Gneisenau" during armistice returns "Unknown target" instead of diplomatic context error.
- **Fix:** Added secondary fallback in `_fuzzy_match_enemy()` (executor.py) that searches all marshals ignoring war status. Returns diplomatic error with armistice turns remaining. Added `diplomatic_block` check in `combat_executor.py` to surface the error before region fallback.
- **Files:** `executor.py`, `combat_executor.py`
- **Tests:** 4 in `test_bugfix_session3.py`

### ~~PT-5: Pursue/Support Bypass Armistice, Waste AP~~ FIXED
- **Source:** Playtest Audit (Mar 29)
- **Summary:** "Ney, pursue Wellington" during armistice consumes 2 AP before war-status check.
- **Root cause:** Order creation (strategic_executor.py) only checks target existence, not war status. AP consumed before next-turn validation cancels the order.
- **Fix:** Added `is_at_war()` check in PURSUE validation (strategic_executor.py) before order creation. Returns diplomatic error with `variable_action_cost: 0` (no AP consumed). SUPPORT already rejects enemy targets.
- **Files:** `strategic_executor.py`
- **Tests:** 6 in `test_bugfix_session3.py`

### ~~DLF-1: Vassalizable Icon Shows Ineligible Nations~~ FIXED
- **Source:** Diplo Ledger Fixes
- **Summary:** Icon shows for any nation with relation < -10 OR at_war, ignoring diplomatic state requirements.
- **Fix:** Added `diplomatic_state in VASSAL_MIN_STATES` check to `vassal_eligible` condition.
- **Files:** `diplomatic_ledger.py`
- **Tests:** 2 in `test_bugfix_session4.py`

### ~~DLF-2: UNDERMINE_ALLIANCE Mission Has No Effect~~ FIXED
- **Source:** Diplo Ledger Fixes
- **Summary:** Mission accepts commands, deducts 2 DP/turn, but per-turn effect (-3 relation between target pair) never applied.
- **Fix:** Added ally-selection dialogue (auto-select single, present options for multiple), `target_ally` in mission dict, -3/turn skill-scaled relation reduction between targets, auto-cancel when alliance breaks.
- **Files:** `diplomatic_dialogue.py`, `diplomatic_executor.py`, `diplomacy.py`, `diplomatic_ledger.py`
- **Tests:** 8 in `test_bugfix_session4.py`

### ~~DLF-3: AI-AI Relations Display Scaling~~ FIXED
- **Source:** Diplo Ledger Fixes
- **Summary:** Nations tab lists all AI relations inline — unreadable wall of text at scale.
- **Fix:** Filtered to notable states only (WAR, ALLIANCE, DEFENSIVE_ALLIANCE, OPEN_BORDERS, NON_AGGRESSION). PEACE entries skipped.
- **Files:** `diplomatic_ledger.py`
- **Tests:** 3 in `test_bugfix_session4.py`

### ~~DLF-4: COURT_NATION Blowback Never Processes~~ FIXED
- **Source:** Diplo Ledger Fixes
- **Summary:** COURT_NATION costs 2 DP/turn for 20% blowback risk, but blowback stub never fires.
- **Fix:** Added 20% blowback roll in `_process_mission_effects()` — fixed -3 penalty (not skill-scaled), dispatch event queued, blowback event emitted.
- **Files:** `diplomacy.py`
- **Tests:** 7 in `test_bugfix_session4.py`

### ~~DLF-5: GATHER_INTEL Completes But Reveals Nothing~~ FIXED
- **Source:** Diplo Ledger Fixes
- **Summary:** Auto-completes after 3 turns with congratulations but zero intel. Player spends 3 DP for a message.
- **Fix:** Added `intel_grants` field to WorldState (serialized). On completion, grants FULL visibility on all target regions for 5 turns via `update_intel_from_scout()`. Decay protected during grant window, expired grants cleaned up.
- **Files:** `diplomacy.py`, `world_state.py`
- **Tests:** 7 in `test_bugfix_session4.py`

### ~~DLF-7: Eliminated Nations in War Cascades~~ FIXED
- **Source:** Diplo Ledger Fixes
- **Summary:** `_process_war_cascade()` iterates all nations without filtering eliminated ones. Dead nations pulled into phantom wars.
- **Fix:** Already resolved by DLF-11 — `get_active_nations()` at diplomacy.py:1182 filters both cascade loops. 3 verification tests added.
- **Files:** `diplomacy.py` (already patched by DLF-11)
- **Tests:** 3 in `test_bugfix_session2.py`

### ~~DLF-9: P3 Proposal Skips Upgrade Path Validation~~ FIXED
- **Source:** Diplo Ledger Fixes
- **Summary:** P3 (Threat > 60) proposes states directly based on relation thresholds without checking valid upgrade path.
- **Fix:** Replaced hardcoded relation thresholds with `_determine_upgrade_type()` call (same as P4). Follows PEACE→OPEN_BORDERS→NON_AGGRESSION→DEFENSIVE_ALLIANCE→ALLIANCE path.
- **Files:** `ai_diplomacy.py`
- **Tests:** 6 in `test_bugfix_session4.py`

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

### PL-7: Counter-Offer Acceptance Missing AI Cooldown
- **Source:** Playtest (Apr 6)
- **Summary:** When player accepts an AI counter-offer via `accept_counter_offer` (diplomatic_executor.py:1773), no `apply_acceptance_cooldown` is called. The AI has no cooldown preventing it from immediately proposing the next upgrade type.
- **Root cause:** The `accept_ai_proposal` path (line 2163) correctly calls `apply_acceptance_cooldown(source_nation, world)`, but the `accept_counter_offer` path (line 1785) only calls `_ratify_treaty` without setting any AI cooldown.
- **Fix:** Add `apply_acceptance_cooldown(source_nation, world)` call in the `accept_counter_offer` handler after ratification.
- **Files:** `diplomatic_executor.py` (line ~1790)
- **Est. Tests:** ~2

### ~~m1: "trust" Doesn't Parse via /command~~ FIXED
- **Source:** Playtest Review (Mar 24)
- **Summary:** Typing "trust" into /command returns parse error; must use separate endpoint.
- **Fix:** Added dialogue-keyword detection in the no-dialogue branch of `/command`. When a keyword like "trust" is typed with no active dialogue, returns Berthier message instead of falling through to parser.
- **Files:** `main.py`
- **Tests:** 3 in `test_bugfix_session5.py`

### ~~m2: Duplicate Counter-Punch Notifications~~ FIXED
- **Source:** Playtest Review (Mar 24)
- **Summary:** Davout earned 2 separate counter-punch notifications same turn; stale entries accumulate.
- **Fix:** Added dedup check before creating COUNTER_PUNCH_EARNED notification — checks if one already exists for same marshal + turn.
- **Files:** `combat_executor.py`
- **Tests:** 2 in `test_bugfix_session5.py`

### ~~m3: Artillery Morale Collapse Without Combat~~ FIXED
- **Source:** Playtest Review (Mar 24)
- **Summary:** Drouot (25k) morale dropped to 6% without direct fighting.
- **Fix:** Added morale floor at FORCED_RETREAT_THRESHOLD (25%) after bombardment morale hits and collateral morale hits. Bombardment alone cannot collapse armies below retreat threshold.
- **Files:** `combat_executor.py`
- **Tests:** 3 in `test_bugfix_session5.py`

### ~~m4: Redundant Route Description for Adjacent Move~~ FIXED
- **Source:** Playtest Review (Mar 24)
- **Summary:** "Grouchy march to Paris" shows "Route: Paris. Moves to Paris." for 1-hop move.
- **Fix:** Skip "Route:" prefix when `remaining == 0` (adjacent destination already reached in first step).
- **Files:** `strategic_executor.py`
- **Tests:** 2 in `test_bugfix_session5.py`

### ~~PT-3: Emoji Encoding Broken (Windows)~~ FIXED
- **Source:** Playtest Audit (Mar 29)
- **Summary:** Cavalry warnings show garbled surrogate pairs on Windows. 40+ emoji across 7 files.
- **Fix:** Replaced all player-facing emoji with text markers: `[!]`, `[Cavalry]`, `[Combat]`, `[BROKEN]`, `[Vindication]`, `[Shield]`, `[Blocked]`. Debug/comment emoji untouched.
- **Files:** `combat_executor.py`, `world_state.py`, `combat.py`, `meta_executor.py`, `executor.py`, `movement_executor.py`, `tactical_executor.py`
- **Tests:** 3 in `test_bugfix_session5.py`

### ~~PT-7: bombardment_streak Tracked But Never Used~~ FIXED
- **Source:** Playtest Audit (Mar 29)
- **Summary:** Field initialized, serialized, reset per-turn, but bombardment uses fixed 0.10 degradation. Dead code.
- **Fix:** Removed `bombardment_streak` and `last_bombardment_target` fields from Marshal. Removed all tracking code in combat_executor, movement_executor, objection_v2. Removed related objection triggers (artillery reckless repositioning, cease fire).
- **Files:** `marshal.py`, `combat_executor.py`, `movement_executor.py`, `objection_v2.py`
- **Tests:** 3 in `test_bugfix_session5.py`

### ~~DLF-8: Opportunistic Downgrade Doesn't Exclude VASSAL~~ FIXED
- **Source:** Diplo Ledger Fixes
- **Summary:** VASSAL missing from downgrade exclusion list. Code fails silently finding VASSAL in `_DOWNGRADE_ORDER`.
- **Fix:** Added `state != "VASSAL"` to the opportunistic downgrade condition.
- **Files:** `ai_diplomacy.py`
- **Tests:** 2 in `test_bugfix_session5.py`

### ~~DLF-10: Armistice Cooldown Missing VASSAL Exclusion~~ FIXED
- **Source:** Diplo Ledger Fixes
- **Summary:** Armistice allow-list missing VASSAL. Should not block VASSAL transition during armistice.
- **Fix:** Added `"VASSAL"` to armistice cooldown allow-list tuple.
- **Files:** `diplomacy.py`
- **Tests:** 4 in `test_bugfix_session5.py`

### ~~PL-1: Emoji Regression — Unicode Escapes in Combat Prefix~~ FIXED
- **Source:** Playtest (Apr 6)
- **Summary:** PT-3 replaced literal emoji with text markers, but `_build_tactical_prefix()` in `combat.py:35-65` uses unicode escape sequences (`\U0001f525`, `\U0001f6e1\ufe0f`, `\U0001f613`, `\U0001f3d4\ufe0f`, `\u2694\ufe0f`, `\U0001f40e`, `\U0001f4a5`, `\U0001f3f0`, `\u26a0\ufe0f`) that render as emoji at runtime but bypass the PT-3 source-file scanner test (test reads text, escape sequences appear as ASCII). Lines 56-64 also have emoji for combined arms / adjacent ally messages.
- **Fix:** Replaced all 16 unicode escape emoji in `_build_tactical_prefix()` with text markers (`[Combat]`, `[Shield]`, `[Fort]`, `[Warning]`, `[Alert]`, `[Terrain]`, `[Cavalry]`, `[Explosion]`). Updated PT-3 scanner to detect `\U0001f`/`\u26`/`\u27`/`\u2694`/`\ufe0f` escape sequences.
- **Files:** `combat.py` (lines 34-64), `test_bugfix_session5.py` (scanner update)
- **Tests:** 2 in `test_bugfix_session6.py`

### ~~PL-2: Counter-Punch Notification Dedup Incomplete~~ FIXED
- **Source:** Playtest (Apr 6)
- **Summary:** 5 duplicate `counter_punch_earned` notifications accumulated for Davout across turns. m2 fix deduped within a single turn's combat, but notifications from different turns pile up because the dedup check only looks at same-turn events, not existing notification queue.
- **Fix:** Removed `turn_created` from dedup check — now checks for existing COUNTER_PUNCH_EARNED notification for same marshal regardless of turn. Expiry tracked separately by `counter_punch_turns`.
- **Files:** `combat_executor.py` (line 742)
- **Tests:** 2 in `test_bugfix_session6.py`

### ~~PL-3: Incoming AI Proposal Shows "Unknown diplomat"~~ FIXED
- **Source:** Playtest (Apr 6)
- **Summary:** Saxony's AI proposal popup shows `diplomat_name: "Unknown diplomat"` and `diplomat_personality: "Unknown"` instead of "Einsiedel" / "moderate". The diplomat data exists on the world state but isn't being populated into the incoming_proposal response dict.
- **Fix:** Added diplomat lookup in `generate_dialogue()` context builder — populates `diplomat_name` and `diplomat_personality` from `world.diplomats[target_nation]`. Safety valve in main.py now reads real diplomat data.
- **Files:** `diplomatic_dialogue.py` (line 342)
- **Tests:** 2 in `test_bugfix_session6.py`

### ~~PL-4: Enemy Phase Invisible When Fog Hides All Actions~~ FIXED
- **Source:** Playtest (Apr 6)
- **Summary:** When all enemy actions occur in regions with only PARTIAL visibility (e.g., enemies retreated to their homeland), `_filter_enemy_phase_by_visibility()` strips everything and `enemy_phase` is omitted entirely from the response. Player sees zero indication that enemies acted for 8+ consecutive turns, which feels like the AI is broken. Turn events (fortify_strengthened, retreat_recovery, construction_complete) prove the AI IS acting — the display just hides it.
- **Root cause:** `main.py:925` — `if cleaned_phase.get("total_actions", 0) > 0` skips the entire enemy_phase when fog hides all actions. No fallback message.
- **Fix:** When fog filters all actions but raw `total_actions > 0`, backend adds `fog_hidden_summary` list with per-nation Berthier messages. Godot `enemy_phase_dialog.gd` checks for `fog_hidden_summary` and renders it instead of "No enemy actions this turn."
- **Files:** `main.py` (lines 919-935), `enemy_phase_dialog.gd` (line 60)
- **Tests:** 3 in `test_bugfix_session6.py`

---

## P3 — BALANCE / ENHANCEMENT

### ~~PT-6: No AP Warning on End Turn~~ FIXED
- **Source:** Playtest Audit (Mar 29)
- **Summary:** Player ends turn with AP remaining, no warning about unused actions.
- **Fix:** Added `actions_remaining > 0` check before turn processing. Warning appended to turn-end message. Turn still ends.
- **Files:** `meta_executor.py`
- **Tests:** 3 in `test_bugfix_session5.py`

### ~~B1: Wellington Defense Stack (~75-85%)~~ FIXED
- **Source:** Playtest Review (Mar 24)
- **Summary:** Combined defense modifiers make Wellington nearly unbeatable. 2:1 casualty ratios even with numerical advantage.
- **Fix:** Updated fortify caps to match approved spec: Aggressive 10%→8%, Cautious 20%→12%, Default 15%→12%. Bombardment already strips fortification at 10%/hit.
- **Files:** `personality_modifiers.py`
- **Tests:** 5 in `test_bugfix_session5.py`

### ~~B2: Supply Attrition Death Spiral~~ FIXED
- **Source:** Playtest Review (Mar 24)
- **Summary:** Belgium supply cap 25k; 2-3 marshals (80-100k) cause ~4k losses/turn. Staging area destroys army.
- **Fix:** Updated supply caps to match approved spec: City 30k→40k, Town 25k→35k.
- **Files:** `region.py`
- **Tests:** 3 in `test_bugfix_session5.py`

### ~~N3: Coalition Friction in Attack Scoring~~ VERIFIED (already fixed)
- **Source:** Diplomacy Design Fixes (DA-3)
- **Summary:** Coalition friction only affects ally-support movement, not attack scoring.
- **Status:** Code already applies friction to co-location bonus (`enemy_ai.py:2177-2178`). Verification tests confirm correct behavior.
- **Tests:** 3 in `test_bugfix_session5.py`

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

| Session | Items | Focus | Tests |
|---------|-------|-------|-------|
| 1 | DLF-11 | `get_active_nations()` helper + 23-site eliminated-nation sweep | 17 |
| 2 | DLF-7, DLF-12 | Cascade filter (uses Session 1 helper) + AI movement permission | 19 |
| 3 | PT-2, M2, PT-4, PT-5 | Parse fixes + armistice validation | 25 |
| 4 | DLF-1, DLF-2, DLF-3, DLF-4, DLF-5, DLF-9 | All remaining P1s: vassal icon, undermine alliance, AI relations, blowback, intel grants, upgrade path | 33 |
| 5 | m1, m2, m3, m4, PT-3, PT-6, PT-7, DLF-8, DLF-10, B1, B2, N3 | All 12 remaining: parse, dedup, morale floor, route, emoji, AP warning, dead code, VASSAL guards, fortify caps, supply caps, friction verification | 36 |

**Sessions 1-5: 154 tests. ALL PRIOR BUGS RESOLVED.**

| 6 | PL-1, PL-2, PL-3, PL-4 | Emoji escape regression, counter-punch dedup, diplomat name, fog enemy phase message | 9 |

**Sessions 1-6: 163 tests. ALL BUGS RESOLVED.**

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

#### Session 10 — Playtest Regressions (PL-1, PL-2, PL-3, PL-4)
> Read: `docs/BUG_FIXES.md` (PL-1/2/3/4 entries), `CLAUDE.md`
> Task: PL-1 — replace unicode escape emoji in `_build_tactical_prefix()` (combat.py:35-65) with text markers, update PT-3 test to catch escape sequences. PL-2 — dedup counter-punch notifications across turns, not just within same turn. PL-3 — populate diplomat_name/personality from world.diplomats in incoming AI proposal dict. PL-4 — when fog hides all enemy actions but raw total_actions > 0, emit Berthier fog summary per nation instead of omitting enemy_phase entirely. ~9 tests.

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
