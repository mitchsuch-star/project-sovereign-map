# Bug Fixes

> **Consolidated bug tracker.** All open bugs from playtest reviews, audits, and design fixes live here.
> Iterate sessions until clean, then move to `DESIGN_REFINEMENT.md`.
>
> **Last Updated:** April 7, 2026

---

## Summary

| Priority | Count | Status |
|----------|-------|--------|
| P1 — MAJOR | 0 | PL-9 FIXED (Session 10) — acceptance mismatch |
| P2 — MINOR | 0 | PL-10 FIXED (Session 10) — "more generous" downgrades proposal type |
| P3 — API-ONLY | 0 | PL-11 FIXED (Session 10) — incoming proposals hijack commands |
| P1 — MAJOR | 1 | PL-5 Part A FIXED (Session 8) |
| P1 — MAJOR | 1 | PL-5 Part B+C FIXED (Session 7), PL-6 FIXED (Session 7) |
| P2 — MINOR | 0 | PL-8 (counter-offer UX) FIXED (Session 9) |
| P2 — MINOR | 0 | PL-7 FIXED (Session 7, as PL-5 Part C) |
| P1 — MAJOR | 1 | PL-12 OPEN — harshness increases acceptance |
| P1 — MAJOR | 1 | PL-13 OPEN — viable proposal falsely rejected as "surpassed" |
| **Total** | **2 OPEN** | |

**Prior bugs:** 28 bugs fixed across Sessions 1-6 (~163 tests). All P0/P1/P2/P3 resolved before these new findings.

**Session 10 (Apr 6):** All 3 remaining bugs FIXED. 13 new tests (7938 total). PL-9: Two-part fix — (A) warning text for borderline 50-75% proposals in `_enrich_proposal_summary`, (B) acceptance snapshot stored at send time + tolerance band (reject only if score drops >15 from snapshot) in `_process_proposal_in_transit`. PL-10: Force proposal type preservation in `modify_generous` and `modify_harsh` — `suggested["type"] = proposal_type` instead of `.get()` fallback that allowed `generate_suggested_terms` to override. PL-11: Improved dialogue guard error message with nation name and `/respond_to_diplomatic_dialogue` API hint.

**Session 9 (Apr 6):** Counter-offer UX COMPLETE. Visual differentiation in `incoming_proposal_popup.gd`: distinct "COUNTER-OFFER" header (blue), context line ("In response to your X proposal..."), steel-blue border, adapted button labels. Redundant assessment text removed from backend. Counter-offer logic audited — M3 algorithm confirmed solid (score 30-49 triggers counter, removes worst clause, adds nation-specific sweeteners). No new backend bugs found.

**Session 7 (Apr 6):** Backend cooldown fixes COMPLETE. 16 new tests (7915 total). Fixed: AI dedup gap, cooldowns in all 4 resolution paths (+1 decrement timing compensation), game-over guard, counter-offer accept/reject cooldowns, type-aware modify_harsh (friendship vs war/coercive).

**Spec review (Apr 6):** Deep code analysis verified all root causes. PL-5 redesigned: keep 1-turn deferral (thematic), add result popup + AI dedup + cooldown fixes. Found additional sub-bugs: accept-path cooldown gap (c), AI dedup gap (e), reject_counter_offer missing AI cooldown, cooldown-decrement timing in advance_turn, failed counter-offer cooldown gap (f), stale rejection missing all cooldowns (g), game-over leakage (h). All line numbers verified against code.

---

## Implementation Plan

### Session 7 — Backend Cooldown Fixes (PL-5 Part B + C, PL-6, PL-7) ✓ COMPLETE
Pure Python, all testable with pytest. Fixed the race condition and gameplay bugs.
- **PL-5 Part B:** Dedup guard in `_has_pending_proposal_from`, cooldowns in all 4 resolution paths (ACCEPT/REJECT/failed-counter/stale), game-over guard, +1 cooldown compensation for decrement timing
- **PL-5 Part C / PL-7:** `accept_counter_offer` + `reject_counter_offer` cooldown wiring in `diplomatic_executor.py`
- **PL-6:** Type-aware `modify_harsh` — split friendship vs war resolution vs coercive categories
- **Files:** `world_state.py`, `ai_diplomacy.py`, `diplomatic_executor.py`
- **Tests:** 16 new (tests/test_bugfix_session7.py), 2 existing updated

### Session 8 — Proposal Result Popup (PL-5 Part A)
Crosses backend/frontend. UX improvement — popup so results aren't buried in dispatch.
- **Backend:** New `proposal_result_popup` in PopupQueue (PRIORITY_ORDER + RESPONSE_KEYS), WorldState property + serialization, set popup in all 4 resolution paths
- **Frontend:** New `proposal_result_popup.gd` + `.tscn` (extends PopupBase, [Continue] button), register in `main.gd`, wire in `_on_command_result()`
- **Files:** `cooldown_manager.py`, `world_state.py`, `main.gd`, new Godot scene + script
- **Est. Tests:** ~4 + manual verification

**Priority:** Session 7 is higher — eliminates the race condition and nonsensical demands. Session 8 is polish. If Session 7 ships alone, the game is correct even if results are still only in dispatch text.

---

## P1 — MAJOR

### PL-9: Acceptance Mismatch — Displayed % Doesn't Match Resolution ✓ FIXED (Session 10)
- **Source:** Playtest (Apr 6)
- **Summary:** Player sees 67-72% acceptance when reviewing a proposal, but the proposal is rejected because acceptance is recalculated at resolution time with changed world state. Player gets "Saxony agreed in principle, but the diplomatic situation has changed" despite high displayed odds.
- **Root cause:** Acceptance is calculated twice — once at proposal review time (`diplomatic_dialogue.py:427`) for display, and again at turn resolution (`world_state.py:4392` inside `_process_proposal_in_transit`). Between these two calculations, `advance_turn` runs: relations decay (`diplomacy.py:2226`, ±1/turn), war scores recalculate (`diplomacy.py:437`), war weariness accumulates (+2/turn). A 67% score can easily drop below 50 after these changes.
- **Reproduction:** Propose alliance to Saxony at 67-72% displayed acceptance with default relations (~40). End turn. Proposal rejected.
- **Design note:** The recalculation is arguably correct — conditions DO change while Talleyrand travels. The real problem is player expectation: a displayed 72% that fails feels like a lie. Two-part fix:
- **Proposed fix — Part A (UX mitigation):** Add Talleyrand warning text to the proposal confirmation screen. When acceptance is in the borderline range (50-75%), Talleyrand says something like: *"This estimate reflects current conditions, Sire. Much may change during my journey — a battle lost, a relation soured. I would counsel a wider margin if you wish certainty."* This sets player expectations that the % is a snapshot, not a guarantee. Add `acceptance_warning` field to dialogue data in `_enrich_proposal_summary` when score is 50-75%.
- **Proposed fix — Part B (tolerance band):** Reduce the volatility gap. Options (pick one):
  - (i) Snapshot: store `acceptance_score` in `proposal_in_transit` at send time, use it at resolution instead of recalculating. Displayed % = actual %. Simple but removes the "things changed" dynamic entirely.
  - (ii) Tolerance band: at resolution, reject only if recalculated score drops below `displayed_score - 15` (i.e., a 67% proposal needs to drop to 52 to actually fail). Preserves dynamism but prevents marginal rejections.
  - (iii) Weighted average: resolve with `0.7 * snapshot + 0.3 * recalculated`. Mostly honors the displayed score while allowing extreme changes to matter.
- **Recommendation:** Part A (warning text) is quick, thematic, and always valuable. Part B option (ii) tolerance band is the best gameplay fix — keeps the system dynamic while preventing frustrating near-miss rejections.
- **Files:** `diplomatic_dialogue.py` (warning text in `_enrich_proposal_summary`), `diplomatic_executor.py` (store snapshot), `world_state.py` (`_process_proposal_in_transit` — tolerance band)
- **Est. Tests:** ~5

### PL-10: "More Generous" Downgrades Proposal Type ✓ FIXED (Session 10)
- **Source:** Playtest (Apr 6)
- **Summary:** Making a vassalage or alliance proposal "more generous" converts it to a Peace Treaty — a LOWER diplomatic state than the current relationship. E.g., player has Open Borders with Saxony, proposes Alliance, clicks "more generous", proposal becomes Peace Treaty with gold sweetener. Since Peace < Open Borders, Saxony rejects with "current relations have already surpassed the proposed terms."
- **Root cause:** The generous handler (`diplomatic_executor.py:1103-1112`) adds sweeteners but the proposal type downgrades. The `modify_generous` logic likely rebuilds the proposal using `generate_suggested_terms` or similar, which picks a "safer" proposal type at generous harshness levels. The resulting proposal type doesn't respect the floor of the current diplomatic state.
- **Reproduction:** With Saxony at Open Borders (or higher), propose alliance. Click "More generous" once. Observe proposal type changes from "Full Alliance" to "Peace Treaty."
- **Proposed fix:** In `modify_generous`, never downgrade proposal type below the current diplomatic state. If the player proposed alliance, generous terms should add sweeteners (gold, protection) while keeping the alliance type. Clamp `proposal_type` to be >= current diplomatic state in the hierarchy.
- **Files:** `diplomatic_executor.py` (modify_generous handler), `diplomatic_dialogue.py` (generate_dialogue)
- **Est. Tests:** ~4

### PL-13: Viable Proposal Falsely Rejected as "Surpassed"
- **Source:** Playtest A3 (Apr 7) — Proposal result popup after end turn
- **Summary:** Player proposes Non-Aggression to Saxony (currently at OPEN_BORDERS) with 76% acceptance estimate. Next turn, proposal resolves as REJECTED with message: "The diplomatic situation with Saxony has changed — our proposal is no longer viable" and "The current relations have already surpassed the proposed terms." But Saxony is still at OPEN_BORDERS — relations did NOT surpass Non-Aggression level.
- **Repro:** F1 → Saxony → Propose Non-Aggression → send terms → end turn → PROPOSAL REJECTED popup with false "surpassed" reason
- **Root cause (code-verified):**
  - The surpassed check at `world_state.py:4354-4357` compares `_UPGRADE_ORDER` indices: `if tgt_idx <= curr_idx` → reject. Uses `_proposal_to_state` mapping (line 4346-4352) to convert proposal type to state.
  - `_UPGRADE_ORDER` in `diplomacy.py:29-32`: WAR(0)→ARMISTICE(1)→PEACE(2)→OPEN_BORDERS(3)→NON_AGGRESSION(4)→DEFENSIVE_ALLIANCE(5)→ALLIANCE(6). Higher index = better.
  - For OPEN_BORDERS(3)→NON_AGGRESSION(4): `4 <= 3` = FALSE. **The comparison logic itself is correct and should NOT reject.**
  - **Key: `process_diplomacy_turn()` runs BEFORE `_process_proposal_in_transit()`** (world_state.py:4080 vs 4088). Several sub-steps can change diplomatic state between send and resolution:
    - `_process_mission_effects()` (diplomacy.py:1589) — mission could upgrade state
    - `check_auto_downgrade()` (diplomacy.py:1614) — unlikely (requires 5 turns of low relations)
    - `_process_armistice_expiration()` — could change state for warring nations
    - **Most likely: AI diplomatic phase** runs in `turn_manager.py` BEFORE `advance_turn()`. If AI proposes same type and it auto-resolves (AI-to-AI path), state could advance past NON_AGGRESSION before the player's proposal resolves. PL-5 race condition is relevant here.
  - **Alternative theory:** proposal.get("type") returns wrong value — must verify the exact string stored in `proposal_in_transit.proposal.type` during debugging
- **Debugging approach:** Add temporary logging to `_process_proposal_in_transit()` to print `current_state`, `target_state`, `curr_idx`, `tgt_idx` at resolution time. This will immediately reveal whether the state changed during transit or the mapping is wrong.
- **Priority:** P1 (MAJOR). 76% acceptance proposals should not be auto-rejected. Core diplomacy loop is broken — player invests DP, waits a turn, gets false rejection.
- **Files:** `world_state.py` (_process_proposal_in_transit lines 4342-4389, surpassed check), `diplomacy.py` (_UPGRADE_ORDER line 29, process_diplomacy_turn line 1561), `turn_manager.py` (AI phase timing)
- **Est. Tests:** ~4

---

### PL-12: Harsher Terms INCREASE Acceptance Estimate (Inverted Harshness)
- **Source:** Playtest A3 (Apr 7) — Godot diplomacy wizard, proposal to Saxony
- **Summary:** Clicking "Even Harsher" in the proposal confirm popup raises acceptance from 72% to 76%. Harsher terms should DECREASE acceptance, not increase it.
- **Repro:** F1 → Saxony → Propose Non-Aggression → click "Even Harsher" → acceptance estimate goes UP
- **Root cause (code-verified):**
  - **`harshness_bonus` (diplomacy.py:809-815)** only checks `world.previous_treaties` for historical harshness > 0.3. Adds flat +5 if found. Never checks current proposal's harshness. This bonus is a constant regardless of how harsh the current proposal is.
  - **`modify_harsh` (diplomatic_executor.py:1003-1096)** for friendship types (non_aggression): escalates existing demands by 1.5x, adds gold_per_turn 100 if no demands, removes all sweeteners. BUT gold_per_turn rate is only -0.02/gold (`DEMAND_VALUES` at diplomacy.py:159), so 100 gold = **-2 deal_balance** — negligible.
  - **`is_harsh` check (diplomacy.py:758-762):** `demand_total < -10` triggers harsh personality modifier. For 100 gold demand: `demand_total = -2`, so `is_harsh` stays False. Saxony's dove diplomat gets `peace_mod = +10` (diplomacy.py:123) in BOTH the initial and harsh proposals.
  - **Why acceptance goes UP:** The initial terms from `generate_suggested_terms` may include sweeteners that the formula values at < 0 net (due to demand/sweetener interaction). When `modify_harsh` removes sweeteners and adds a small gold demand, the net deal_balance change is minimal (~-2), but other formula components may shift slightly upward on recalculation (relation_mod, reliability). The core problem: **there is no explicit harshness penalty** — the formula literally cannot distinguish between a generous and harsh version of the same proposal type.
  - **`calculate_treaty_harshness()` (diplomatic_templates.py:1722-1736)** exists and works correctly, but its output is only used for cosmetic display labels in `_enrich_proposal_summary()` (diplomatic_dialogue.py:406-407). It is never passed to `calculate_acceptance()`.
  - **Data flow gap:** `_enrich_proposal_summary()` (diplomatic_dialogue.py:418-429) builds `proposal_for_calc` with demands/sweeteners and calls `calculate_acceptance()`, but doesn't include a harshness score. The formula has no parameter for it.
- **Priority:** P1 (MAJOR). Core diplomacy mechanic is inverted. Player feedback loop is wrong — encourages harsher terms instead of creating a risk/reward tradeoff.
- **Proposed fix:** Add explicit harshness penalty to `calculate_acceptance()`: call `calculate_treaty_harshness()` on the current proposal's terms, apply penalty proportional to harshness (e.g., -15 per 0.1 above 0.2 threshold). Also review `harshness_bonus` from previous treaties — the +5 "more pliable" bonus (display_names.py:211-214) is thematically questionable and should likely be inverted to a penalty or removed.
- **Files:** `diplomacy.py` (calculate_acceptance lines 627-839, harshness_bonus lines 809-815, DEMAND_VALUES line 158), `diplomatic_dialogue.py` (_enrich_proposal_summary lines 418-429), `diplomatic_templates.py` (calculate_treaty_harshness line 1722), `diplomatic_executor.py` (modify_harsh lines 1003-1096)
- **Est. Tests:** ~5

---

### PL-11: Incoming AI Proposals Hijack Player Diplomatic Commands (API-Only) ✓ FIXED (Session 10)
- **Source:** Playtest (Apr 6) — curl/API playtest, NOT Godot
- **Summary:** When player sends a diplomatic command via `/command` API while an AI incoming_proposal is pending in the dialogue queue, the dialogue guard blocks the command and returns the AI proposal instead.
- **Godot impact: NONE.** Verified that Godot handles this correctly:
  - Incoming proposals arrive as **modal popups** (`incoming_proposal_popup.gd`) that block input until dismissed
  - The **diplomacy wizard** (`diplomacy_wizard.gd:210-216`) checks `dialogue_pending` flag from `/diplomatic_preview` and **gracefully closes** before issuing commands
  - Player input is **disabled** during popup display (`main.gd` line 2770)
  - The dialogue guard in `executor.py:461` only triggers via raw API calls that bypass Godot's popup system
- **Root cause:** The executor dialogue guard (`executor.py:460-470`) blocks ALL `/command` calls when `pending_diplomatic_dialogue` exists. This is correct safety behavior for the API, but confusing when using curl.
- **Priority:** P3 (API-only). No gameplay impact. Only affects automated testing and curl playtesting.
- **Proposed fix (low priority):** Improve the error message to say "An incoming proposal from {nation} requires your attention first. Use /respond_to_diplomatic_dialogue to handle it." Currently the message is generic and doesn't explain why the player's intended action was blocked.
- **Files:** `executor.py` (improve guard message)
- **Est. Tests:** ~2

---

### PL-5: Player Proposal — No Feedback Popup, Race Condition with AI
- **Source:** Playtest (Apr 6)
- **Summary:** Player sends a diplomatic proposal (e.g., non-aggression to Saxony). Gets "Expect a response by next turn." Result is buried in morning dispatch (easily missed). Meanwhile, the AI generates its OWN proposal of the same type on the same end-turn, creating a confusing race condition where Saxony rejects the player's harsh terms then immediately proposes a clean non-aggression pact.
- **Root cause:** `execute_proposal` (diplomatic_executor.py:895-994) sets `proposal_in_transit` and `talleyrand_state = "IN_TRANSIT"`. Resolution deferred to `_process_proposal_in_transit()` (world_state.py:4300-4493) which runs inside `advance_turn`. AI proposal generation runs BEFORE `advance_turn` (turn_manager.py:124-129), so AI generates proposals with no awareness that the player's proposal is pending.
- **Execution order (root of race):**
  1. Turn N: Player sends proposal → `proposal_in_transit = {turn_sent: N}`
  2. End turn: AI diplomatic phase runs (turn_manager.py:129) → AI proposes same type
  3. `advance_turn()` runs (turn_manager.py:151) → increments turn to N+1
  4. `_process_proposal_in_transit()` runs inside advance_turn (world_state.py:4066) → resolves player proposal
  5. Player sees both rejection AND the AI's new proposal — confusing
- **Sub-bugs:**
  - (a) No popup feedback: result is only in morning dispatch text, easily missed. Should be a popup like other diplomatic events.
  - (b) AI cooldown gap on rejection: when player's proposal is rejected, `player_proposal_cooldowns` blocks the *player* from re-proposing, but the AI's `_is_on_cooldown` (ai_diplomacy.py:222-239) only checks `ai_proposal_cooldowns` — AI immediately re-proposes same type
  - (c) AI cooldown gap on acceptance: when player's proposal is ACCEPTED in `_process_proposal_in_transit` (world_state.py:4355-4381), NO cooldown is set at all — not `player_proposal_cooldowns`, not `ai_proposal_cooldowns`. AI can propose next upgrade immediately
  - (d) `accept_counter_offer` path (diplomatic_executor.py:1773) doesn't call `apply_acceptance_cooldown` — this is PL-7
  - (e) AI dedup gap: `_has_pending_proposal_from` (ai_diplomacy.py:267-286) checks dialogues and queue but does NOT check `proposal_in_transit`. AI can propose to a nation the player already has a proposal in transit to.
  - (f) Failed counter-offer cooldown gap: when counter-offer generation fails (world_state.py:4454-4465), `player_proposal_cooldowns` set but NO `ai_proposal_cooldowns`. AI can immediately re-propose.
  - (g) Stale rejection cooldown gap: when proposal rejected as stale (world_state.py:4331-4346), NO cooldowns set at all — neither player nor AI. Both can immediately re-propose.
  - (h) Game-over leakage: `_process_proposal_in_transit` has no `game_over` guard — proposal resolves and queues a popup after victory/defeat screen.
- **Design decision:** Keep 1-turn deferral (Talleyrand "travels" to deliver — thematic). Fix the race via dedup + cooldowns. Add a popup so the result is unmissable.
- **Proposed fix — 3 parts:**
  - **Part A — Proposal result popup:** When `_process_proposal_in_transit` resolves (ACCEPT or REJECT), set a new `proposal_result_popup` on WorldState with the outcome. This popup fires on the next turn start via the existing PopupQueue priority system (`build_base_response` → `_include_popup_passthroughs`). Counter-offers already have a popup (incoming_proposal_popup with `is_counter_offer: true`) — no change needed for that path.
    - New popup type: `proposal_result_popup` — add to `PopupQueue.PRIORITY_ORDER` (below `incoming_proposal_popup`) and `RESPONSE_KEYS`
    - New WorldState property: `proposal_result_popup` (get/set via `_popup_queue`, same pattern as other popups)
    - Add to `to_dict`/`from_dict` for serialization
    - New Godot scene: `proposal_result_popup.tscn` + `proposal_result_popup.gd` — extends `PopupBase`, informational [Continue] button, same pattern as `coalition_declaration_popup.gd`
    - Popup data: `{ "target_nation": str, "proposal_type": str, "outcome": "ACCEPT"|"REJECT", "message": str, "feedback": str }`
    - Set in `_process_proposal_in_transit` after ACCEPT (line 4377), REJECT (line 4474), failed counter-offer (line 4460), AND stale rejection (line 4336) paths — all four resolution outcomes need the popup
    - Register in `main.gd` `_ready()` via `dialog_manager.register()`, wire in `_on_command_result()`
    - Dispatch events (`queue_dispatch_event`) stay as-is — dispatch is a text log, popup is the unmissable notification. No double-report concern since they serve different purposes.
  - **Part B — AI dedup + cooldowns:** Prevent the race condition.
    - `_has_pending_proposal_from` (ai_diplomacy.py:267): Add check — if `world.proposal_in_transit` exists and `proposal_in_transit["target"] == nation`, return True. Prevents AI from proposing to a nation the player already has a proposal targeting.
    - `_process_proposal_in_transit` ACCEPT path (world_state.py:4355-4381): Add `apply_acceptance_cooldown(target, self)` after `_ratify_treaty`. Uses the existing `ai_proposal_cooldowns` system so AI's `_is_on_cooldown` sees it.
    - `_process_proposal_in_transit` REJECT path (world_state.py:4468-4481): Already sets `player_proposal_cooldowns`. Additionally add AI cooldown: call `apply_rejection_cooldowns(target, ptype, self)` so the AI can't immediately re-propose the same type.
    - `_process_proposal_in_transit` failed counter-offer path (world_state.py:4454-4465): When counter-offer generation fails (counter_terms is None), the fallback treats it as rejection and sets `player_proposal_cooldowns` but NOT `ai_proposal_cooldowns`. Add `apply_rejection_cooldowns(target, ptype, self)` after line 4465 — same pattern as full REJECT.
    - `_process_proposal_in_transit` stale rejection path (world_state.py:4331-4346): When proposal is rejected as stale (diplomatic state changed during transit), NO cooldowns are set at all — neither player nor AI. Add `self.player_proposal_cooldowns[target] = 3` and `apply_rejection_cooldowns(target, proposal.get("type", ""), self)` before the early return at line 4346. Without this, the player can immediately re-propose and the AI can spam-propose to France after a stale rejection.
    - Both cooldown functions already exist in `ai_diplomacy.py` (lines 242-264) — just need to import and call them.
  - **Part C — PL-7 fix:** `accept_counter_offer` (diplomatic_executor.py:1785) — add `apply_acceptance_cooldown(source_nation, world)`. See PL-7 entry.
- **Edge cases:**
  - Popup priority: If proposal resolves on the same turn as a coalition declaration or sabotage discovery, the higher-priority popup shows first. The proposal result stays queued and shows on the next response cycle. This is correct — coalition is more urgent.
  - Stalled sabotage: Still defers by +1 turn (diplomatic_executor.py:952-955). Dedup check in Part B prevents AI from proposing during the extended transit. Popup fires when it finally resolves.
  - Counter-offer path: Already uses `incoming_proposal_popup` with `is_counter_offer: true` (world_state.py:4441-4451) and pushes a blocking dialogue (line 4403). No new popup needed — counter-offers already have proper UI.
  - Counter-offer rejected by player → then what? `reject_counter_offer` (diplomatic_executor.py:1802) sets `player_proposal_cooldowns`. Should also set AI cooldown. Add `apply_rejection_cooldowns(source_nation, ptype, world)` in `reject_counter_offer` handler.
  - Cooldown timing: Cooldowns set during `advance_turn` (inside `_process_proposal_in_transit`) are decremented in the SAME `advance_turn` call at line 4074 (`decrement_all`). So NATION_ACCEPTANCE_COOLDOWN=2 effectively becomes 1 turn of protection. Check: does `_process_proposal_in_transit` (line 4066) run BEFORE `decrement_all` (line 4074)? Yes — so cooldown is set to 2, then decremented to 1 in the same call. Effective protection = 1 turn. This may be too short — consider setting NATION_ACCEPTANCE_COOLDOWN=3 for the deferred path to get 2 effective turns. Or move decrement before proposal resolution. Simpler: just set cooldown to `NATION_ACCEPTANCE_COOLDOWN + 1` in the deferred path to compensate.
  - Stale proposal check (lines 4311-4346): Already handled — if diplomatic state changed during the deferred turn, proposal is rejected as stale. Popup fires for stale rejections too (player needs to know why their proposal failed). Cooldowns set in stale path (Part B) prevent immediate re-proposal.
  - Failed counter-offer (lines 4454-4465): When counter-offer generation fails, treated as rejection. Popup fires (Part A) and AI cooldowns set (Part B) so the AI can't immediately re-propose.
  - Proposal result popup vs morning dispatch: Both fire. Dispatch is the text log ("Talleyrand returns from Saxony..."), popup is the unmissable modal. Different purposes — no conflict.
  - Game-over state: If `world.game_over = True` during `advance_turn`, `_process_proposal_in_transit` still runs (no guard). A proposal could resolve and queue a popup after victory/defeat. Add `if self.game_over: self.proposal_in_transit = None; return []` as the first guard in `_process_proposal_in_transit` — discard in-transit proposals on game end, player won't need them.
  - PopupQueue serialization: `PopupQueue.to_dict()`/`from_dict()` serialize the entire `_queue` dict generically. Adding `proposal_result_popup` to `PRIORITY_ORDER` and `RESPONSE_KEYS` is sufficient — no separate serialization code needed.
  - Save/load mid-transit: `proposal_in_transit` serialized in `to_dict()` (line 3097) and `from_dict()` (line 3333). If player saves mid-transit and loads, proposal stays in transit and resolves normally on next end-turn. No bug.
- **Files:**
  - `world_state.py` — new `proposal_result_popup` property, set in ALL FOUR `_process_proposal_in_transit` resolution paths (ACCEPT/REJECT/failed-counter/stale), add cooldown calls in all four paths, game-over early return guard, to_dict/from_dict
  - `ai_diplomacy.py` — `_has_pending_proposal_from` dedup fix (add `proposal_in_transit` check)
  - `diplomatic_executor.py` — `accept_counter_offer` add acceptance cooldown, `reject_counter_offer` add AI rejection cooldown
  - `cooldown_manager.py` — add `proposal_result_popup` to PopupQueue PRIORITY_ORDER + RESPONSE_KEYS
  - `main.py` — no change needed (build_base_response handles popup passthrough automatically via R4)
  - `main.gd` — register new popup, wire in `_on_command_result`
  - New: `proposal_result_popup.gd` + `proposal_result_popup.tscn` (extends PopupBase, [Continue] button)
- **Scope:** Medium — no core flow changes. New popup + cooldown wiring + dedup guard.
- **Est. Tests:** ~12 new + ~4 existing tests updated

### PL-6: "Harsher" Terms on Friendship Pacts Demand Territory — Nonsensical
- **Source:** Playtest (Apr 6)
- **Summary:** Player proposes non-aggression pact to friendly Saxony (OPEN_BORDERS state, positive relations). Clicks "harsher" twice. System demands 150g/turn gold AND 1 territory cession from Saxony — for a *non-aggression pact*. This is extortion, not diplomacy. Saxony reasonably rejects. Player perceives acceptance odds barely changing because demand impact is tiny relative to base disposition.
- **Root cause:** `modify_harsh` handler (diplomatic_executor.py:996-1060) is proposal-type-blind. It extracts `proposal_type` at line 999 but never uses it for any type-aware logic. Lines 1015-1025 blindly add `gold_per_turn` (100g) and `territory_cede` (1 region on round 2) regardless of proposal type. The demand value rates in `DEMAND_VALUES` (diplomacy.py:158) are also weak: gold_per_turn = -0.02/gold (100g = -2 acceptance points), territory_cede = -5/region. Two rounds of escalation only subtract ~7 points from a base of ~30-50, barely perceptible.
- **Sub-bugs:**
  - (a) Type-blind escalation: territory demands make no thematic sense for non_aggression, open_borders, defensive_alliance, or alliance proposals
  - (b) Weak demand impact: 100g gold demand = -2 acceptance points. Player clicks "harsher" and sees acceptance barely move. 300g + 2 territory = -16 points — actually significant.
- **Proposal type categories:**
  - Friendship types: `non_aggression`, `open_borders`, `defensive_alliance`, `alliance` — demands are signing conditions, not reparations
  - War resolution types: `peace`, `armistice`, `armistice_losing`, `armistice_winning` — demands are war reparations, territory + gold make sense
  - Coercive types: `vassalage` — demands are subjugation terms, gold + territory make sense
- **Proposed fix:** Split `modify_harsh` by proposal type category (lines 1010-1025):
  - **Friendship types:** Round 1: add modest gold demand (100g). Round 2: BLOCKED — hide "Even harsher" button after round 1 (change `modify_count < 2` to `modify_count < 1` for friendship types), show message "A {proposal_type} cannot bear heavier demands, Sire." NO territory demands ever — strip any `territory_cede` from demands list as safety.
  - **War resolution types:** Round 1: add gold demand 300g (up from 100g). Round 2: add territory_cede value 2 (up from 1). 1.5x escalation of existing demands stays.
  - **Vassalage:** Same as war resolution (territory + gold are thematic for subjugation).
- **Pattern to follow:** `modify_generous` handler (lines 1103-1112) already type-checks proposal_type — uses `gold_per_turn` for war types and `gold_lump` for friendship types. Same pattern applies here.
- **Edge cases:**
  - `modify_count` is shared between harsh and generous directions. If player clicks generous then harsh, they hit the cap with fewer harsh rounds. Acceptable — 2 total modifications regardless of direction.
  - `_build_base_terms` for friendship types adds NO demands (confirmed: non_aggression is `pass`, alliance/defensive_alliance/open_borders add only `open_borders` clause). So the only demands for friendship types come from `modify_harsh` — clean separation.
  - `territory_cede` demand with no territory to cede: `_ratify_treaty` silently skips transfer if target doesn't control the region (lines 4666-4679). No crash, but confusing. Mitigated by not allowing territory demands on friendship types.
  - Acceptance formula `harshness_bonus` (+5 at line 837): applies when demands are detected. For friendship types with a 100g gold demand, the +5 bonus could counteract the -2 demand penalty, making harsh terms paradoxically better. Acceptable — the bonus represents intimidation factor, it's a design feature not a bug.
- **Files:** `diplomatic_executor.py` (modify_harsh handler lines 996-1060)
- **Est. Tests:** ~5

---

## P2 — MINOR

### PL-7: Counter-Offer Accept/Reject Missing AI Cooldowns
- **Source:** Playtest (Apr 6)
- **Summary:** When player accepts an AI counter-offer via `accept_counter_offer` (diplomatic_executor.py:1773), no `apply_acceptance_cooldown` is called. When player rejects via `reject_counter_offer` (line 1802), no AI cooldown is set either. The AI has no cooldown preventing it from immediately proposing again.
- **Root cause:** The `accept_ai_proposal` path (line 2163) correctly calls `apply_acceptance_cooldown(source_nation, world)`, but the `accept_counter_offer` path (line 1785) only calls `_ratify_treaty` without setting any AI cooldown. The `reject_counter_offer` path sets `player_proposal_cooldowns` but not `ai_proposal_cooldowns`.
- **Fix:**
  - `accept_counter_offer` (line ~1786): Add `apply_acceptance_cooldown(source_nation, world)`. Same pattern as `_handle_accept_ai_proposal` line 2164.
  - `reject_counter_offer` (line ~1815): Add `apply_rejection_cooldowns(source_nation, ptype, world)` so the AI can't immediately re-propose the same type. Counter-offers originate from the AI, so rejection should cool down the AI.
- **Edge cases:**
  - `source_nation` comes from `context.get("source_nation", target_nation)` — set correctly at `_process_proposal_in_transit` line 4424 (`"source_nation": target`), always the AI nation.
  - If `_ratify_treaty` returns a failure event, should cooldown still apply? Yes — match `_handle_accept_ai_proposal` which applies cooldown unconditionally. Prevents spam even on failed ratification.
  - No other acceptance paths are missing cooldowns: `accept_with_conflict` (line 1629) routes through `_handle_accept_ai_proposal` which has the cooldown. Verified all 3 acceptance paths.
  - This is also PL-5 Part C — the cooldown gaps feed into the race condition.
- **Files:** `diplomatic_executor.py` (lines ~1786 and ~1815, inside counter-offer handlers)
- **Est. Tests:** ~3

### PL-8: Counter-Offer Popup Looks Like Unsolicited AI Proposal ✓ FIXED (Session 9)
- **Source:** Playtest (Apr 6)
- **Summary:** When the player sends a proposal and the AI counter-offers, the result appears via `incoming_proposal_popup` — visually identical to an unsolicited AI proposal.
- **Fix (Session 9):** Visual differentiation in `incoming_proposal_popup.gd`:
  - Header: "[color=#7eb8da]COUNTER-OFFER[/color]" (blue) instead of "DIPLOMATIC ENVOY"
  - Context: "In response to your {type} proposal, {nation} offers modified terms:"
  - Border: Steel-blue (#7eb8da) instead of default gold
  - Labels: "Revised Terms" instead of "Terms", "Accept Terms"/"Reject Terms" buttons
  - Counter button hidden (no counter-counter — already worked)
  - Backend: Removed redundant "This is a counter-proposal..." from assessment text (popup itself now communicates this)
- **Counter-offer logic audit:** M3 algorithm confirmed working correctly. Score 30-49 triggers counter. Removes clause AI hates most, adds nation-specific sweeteners from NATION_DESIRES. Personality thresholds modify behavior (hawk stricter, dove lenient). Failed counters fall through to rejection with proper cooldowns. No bugs found.
