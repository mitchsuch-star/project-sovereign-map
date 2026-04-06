# Bug Fixes

> **Consolidated bug tracker.** All open bugs from playtest reviews, audits, and design fixes live here.
> Iterate sessions until clean, then move to `DESIGN_REFINEMENT.md`.
>
> **Last Updated:** April 6, 2026

---

## Summary

| Priority | Count | Status |
|----------|-------|--------|
| P1 — MAJOR | 1 | PL-5 Part A (popup) OPEN |
| P1 — MAJOR | 1 | PL-5 Part B+C FIXED (Session 7), PL-6 FIXED (Session 7) |
| P2 — MINOR | 0 | PL-7 FIXED (Session 7, as PL-5 Part C) |
| **Total** | **1** | **1 open (PL-5 Part A — Session 8)** |

**Prior bugs:** 28 bugs fixed across Sessions 1-6 (~163 tests). All P0/P1/P2/P3 resolved before these new findings.

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
