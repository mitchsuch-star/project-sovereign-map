# Bug Fixes

> Broken-now implementation document.
> Treat the current findings as frozen truth until the open items below are fixed.
>
> Last Updated: April 11, 2026 (Session 2 follow-up IMPLEMENTED. `diplomatic_queue` eliminated, mailbox panel built in Godot, `GET /mailbox` + `POST /mailbox/activate` endpoints added, badge formula consolidated to `dialogue_manager.get_mailbox_count()`. 37 new tests, 8189 total passing.)

---

## How To Use This Doc

- This is the implementation source of truth for the current open PL items.
- Follow the session order below unless a direct dependency note inside an item says otherwise.
- Inspect only the exact implicated code surfaces and same-family helper paths for the active item.
- Use `docs/GPT_AUDIT_PLAN_RESULTS.md` for routing, collapse rules, and phase sequencing only.
- Use `docs/DESIGN_REFINEMENT.md` only to confirm what remains blocked.
- Update `docs/STATUS.md` whenever the open count, duplicate status, or active session changes.

---

## Scope Guard

- No new audit pass during this fix phase.
- No re-scoring, re-prioritizing, or widening of the problem space.
- No new PL items unless a direct code contradiction forces one.
- Same-family sibling failures on the same code path are absorbed into the owning PL item and called out explicitly below.
- `docs/DESIGN_REFINEMENT.md` stays blocked; do not pull design work into Sessions 1-8.

---

## Active Summary

| Session | Priority | ID | Status | Summary | Routing Note |
|---------|----------|----|--------|---------|--------------|
| 1 | P1 | PL-30 | **FIXED** | Godot null-instance crash on diplomacy button after a masked proposal result | Fixed Apr 10, 2026 |
| 1 | P1 | PL-31 | **FIXED** | Capital-loss instant defeat still live, with a false-negative regression test | Fixed Apr 10, 2026. Unblocks PL-28 |
| 2 | P2 | PL-27 | **FIXED** | Diplomacy interrupt contract: hard-stop/soft-stop taxonomy enforced, envoy recovery surface, typed responses | Fixed Apr 10, 2026 |
| 2 | P2 | PL-34 | **FIXED** | Queued proposals: arrival/expiry/overflow now logged in campaign log | Fixed Apr 10, 2026 |
| 2 | P2 | PL-33 | **CLOSED** (duplicate) | `status` works with soft-stop dialogue — verified as PL-27 duplicate | Closed Apr 10, 2026 |
| 2f | P2 | PL-27/34 | **COMPLETE** | Session 2 follow-up: mailbox inbox panel, `diplomatic_queue` eliminated, badge formula consolidated | Implemented Apr 11, 2026 |
| 3 | P2 | PL-32 | OPEN | Raw diplomacy labels can leak into popups because display ownership is split | **NEXT** — Session 2 follow-up contract is stable |
| 4 | P2 | PL-28 | OPEN | No defeat-imminent warning before game over | Depends on PL-31 defeat-rule truth |
| 4 | P2 | PL-26 | OPEN | Combat feels hopeless because the obvious opener teaches the wrong lesson | Treat as teaching/setup first, numbers second |
| 5 | P3 | PL-29 | OPEN | No new-game / restart endpoint | Leave last; QoL contract after core truth is stable |

**Duplicate handling rule:** PL-33 stays listed until the post-PL-27 verification pass is complete. If `status` works with no pending dialogue and with soft-stop diplomacy pending, close PL-33 as a duplicate of PL-27 instead of shipping separate code for it.

---

## Same-Family Decisions

- `PL-30` absorbs both diplomacy-wizard crash paths: Step 1 nation rendering and Step 2 preview rendering. Both failures come from the same masked-result plus coarse `dialogue_pending` contract and the same null-prone `add_output()` recovery path.
- `PL-27` absorbs the nearby same-family command-guard failures on `status`, `help`, `economy`, `treasury`, and `finances`, plus the active-envoy count mismatch, envoy-button recovery failure, and remaining popup handlers that still synthesize parser commands. `PL-33` remains only as a duplicate-candidate verification gate.
- Session 2 follow-up does not create a new PL item. It finishes the player-facing mailbox UX and folds in the same-family regressions found after Session 2 completion: browsable mailbox/inbox flow for 2+ pending items, defer/reopen UX, soft-stop reply routing drift, `/pending_envoy` payload shape drift, badge vs recovery mismatch when queued work exists behind a hard-stop, and the boundary between mailbox-worthy diplomacy and noisy top-bar notifications.
- `PL-34` is the queue/expiry branch of `PL-27`. Do not build a separate UX track for it.
- `PL-32` absorbs all duplicate proposal/clause display maps and raw-token fallback leaks on the active diplomacy popup paths.
- `PL-29` absorbs backend `/new_game`, pause-menu wiring, frontend local-state reset, and autosave semantics as one restart contract.

---

## Architecture Blocker Decision

- Sessions 6-8 do not move earlier as full sessions.
- Only the bug-owned slices needed to close the active PL items ship earlier:
  - Session 2: backend soft-stop taxonomy, authoritative active-plus-queued count contract, typed responses for affected popups
  - Session 2 follow-up: Godot mailbox inbox browsing, defer/reopen UX completion, and PL-27 same-family hardening found after the fix landed
  - Session 3: backend-owned display formatting for active diplomacy popups
- Broader `/command` unification, popup registry cleanup, scale-sensitive backend hardening, and renderer replacement remain in Sessions 6-8.

---

## Session Order

### Session 1 - Stability And Defeat Truth

**Items:** `PL-30`, `PL-31`

**Goal:** remove the crash and align defeat-state truth across code, tests, and docs.

**Exit criteria**

- Opening Diplomacy after a masked proposal result no longer crashes Godot.
- Capital capture no longer contradicts the intended rule or its regression coverage.
- `docs/STATUS.md` no longer implies the capital-loss issue is already fixed.

### Session 2 - Diplomacy Interrupt Contract

**Items:** `PL-27`, `PL-34`, `PL-33` duplicate check

**Goal:** enforce the hard-stop vs soft-stop split, provide a real recovery surface for soft-stop diplomacy, and stop silent expiry/drop behavior.

**Exit criteria**

- Soft-stop diplomacy no longer blocks ordinary commands.
- Active plus queued diplomatic work is visible and reopenable.
- Expiry and overflow no longer resolve unseen proposals silently.
- `status` is verified after the guard split and either closes as a duplicate or remains as a true separate bug.

### Session 2 Follow-Up - Mailbox UX Completion, Inbox Browsing, And Contract Hardening — COMPLETE

**Items:** follow-up slice under `PL-27` / `PL-34` only. No new PL id.

**Status: COMPLETE** (April 11, 2026). `diplomatic_queue` eliminated. Mailbox panel built in Godot. `GET /mailbox` + `POST /mailbox/activate` endpoints. Badge formula uses `dialogue_manager.get_mailbox_count()`. 37 new tests, 8189 total passing.

**Goal:** finish the player-facing mailbox UX so soft-stop diplomacy is actually deferrable and browsable in Godot, and harden the Session 2 transport contract where the audit found live regressions.

**Why this is a separate follow-up**

- Session 2 fixed the backend taxonomy and recovery surface, but Godot still treats incoming proposals as a modal dead-end.
- The shipped mailbox button/hitbox fix made a single pending item reliable, but `Mailbox (N)` is still opaque when `N > 1`; the player cannot inspect or choose among multiple pending diplomatic items.
- This follow-up stays inside the owning `PL-27` family. It does not reopen `PL-33` or create a new tracked PL item.
- `PL-32` should not start until the active proposal contract and recovery payload are stable again.

**Next implementation item**

- Build a formal browsable mailbox/inbox panel behind the mailbox button.
- Do this before `PL-32`, before any broad notification redesign, and before any more popup display cleanup.
- Treat the current mailbox button as an interim reliability fix, not the finished UX.

**Exact scope**

- Keep the existing local `Later` / `Ask Later` path in `godot-client/project-sovereign/scripts/incoming_proposal_popup.gd`.
- Add a mailbox panel/list in Godot instead of treating the mailbox button as "reopen one arbitrary pending item."
- Add a backend mailbox-list contract that returns the active soft-stop item plus queued soft-stop diplomacy in one ordered list.
- Add stable mailbox item identity (`mailbox_id`) for every pending diplomacy item that can appear in the mailbox.
- Add a backend activation contract so selecting a queued mailbox item makes it the active soft-stop item before the popup opens.
- Keep the pending dialogue alive when the player defers locally; the inbox is the mechanism for browsing, not implicit destruction or parser workarounds.
- Harden `backend/main.py` soft-stop reply routing so valid delayed replies still work through `/command`, including numeric choices and the common `accept` / `counter` / `reject` path.
- Fix `/pending_envoy` payload construction so it matches the `incoming_proposal_popup.gd` contract exactly instead of rebuilding a parallel shape.
- Eliminate `world.diplomatic_queue` — consolidate into `dialogue_manager` as the single pending-diplomacy queue.
- Fix badge formula to use `dialogue_manager.get_mailbox_count()` exclusively, eliminating the dual-source mismatch.
- Do not widen this slice into a general notification redesign. Record the clutter policy boundary, but keep the implementation focused on diplomacy inbox behavior.

**Mailbox behavior spec**

- **Dual-queue elimination (APPROVED):** The codebase has two separate pending-diplomacy queues. `world.diplomatic_queue` (world_state.py:443) holds raw AI proposals waiting for delivery — max 3, 3-turn expiry, drained by `_dequeue_best()` during end_turn. `dialogue_manager._queue` (dialogue_manager.py:75) holds delivered dialogues that couldn't become active — max 20, auto-promoted on pop. The current badge formula (main.py:170-172) counts `len(diplomatic_queue) + (1 if dm.is_soft_stop() else 0)` which counts undelivered proposals and ignores `dialogue_manager._queue`. `DialogueManager.get_soft_stop_count()` is broader than the mailbox because it includes hybrid soft-stops; the mailbox needs its own count contract. `diplomatic_queue` existed to throttle delivery to one-per-turn and defer acceptance-score calculation. Both purposes are obsolete: the mailbox IS the multi-proposal UI, and `POST /mailbox/activate` can recalculate acceptance scores at display time. **Eliminate `diplomatic_queue` entirely.** Deliver all AI proposals through `deliver_ai_proposal()` → `dialogue_manager.push()` at generation time. Remove the one-per-turn throttle in `turn_manager._process_ai_diplomatic_phase()`. Remove `_enqueue_proposal()`, `_dequeue_best()`, `_expire_queue()`, `try_deliver_queued_proposal()`, and the `diplomatic_queue` field from WorldState (including `to_dict`/`from_dict`). Migrate the PL-34 overflow/expiry ownership into `DialogueManager` itself — queue cap, any retained expiry sweep, and recorded outcomes must all come from the surviving queue, not from legacy raw-proposal helpers. Update all badge count formulas in main.py to use `dialogue_manager.get_mailbox_count()` exclusively (fix the 4 occurrences at lines ~170, ~498, ~858, ~1946). Remove `getattr(world, 'diplomatic_queue', [])` references in `main.py`, `diplomatic_ledger.py`, `meta_executor.py`.
- Mailbox badge count continues to mean: active soft-stop diplomacy item plus queued soft-stop diplomacy items. **Single source of truth: `dialogue_manager.get_mailbox_count()`** — counts `SOFT_STOP_MAILBOX_TYPES` in active slot + all items in `dialogue_manager._queue`. Exclude hybrid soft-stops from the count (see below).
- Clicking the mailbox with count `0` must produce a deterministic empty state, not a no-op.
- Clicking the mailbox with count `1+` opens a mailbox panel/list, not a proposal popup directly.
- True hard-stop modals still block mailbox interaction. Visible hybrid/local-planning popups that are not mailbox items also block mailbox open/activate; the inbox must not steal focus from them. The count may remain visible while blocked.
- The mailbox panel shows one row per pending diplomacy item with, at minimum:
  - `ACTIVE` vs `WAITING` state
  - source nation / actor
  - item type (`incoming_proposal`, `counter_offer`, `counter_offer_response`, `conflict_alert`)
  - arrival turn
  - short summary line suitable for list display
- **Hybrid soft-stop exclusion:** `sabotage_confrontation` and `vassal_rebellion_imminent` are counted by `is_soft_stop()` / `get_soft_stop_count()` but are NOT diplomacy proposals and must NOT appear in the mailbox panel or badge count. **Exclude hybrids from the count.** Add `get_mailbox_count()` to `DialogueManager` that counts `SOFT_STOP_MAILBOX_TYPES` only (not `HYBRID_SOFT_STOP_TYPES`). Use this for badge and `GET /mailbox`. Hybrids keep their own popup flows unchanged.
- **`conflict_alert` dispatch:** `conflict_alert` items currently route to `proposal_confirm_popup`, not `incoming_proposal_popup`. The mailbox panel must dispatch to the correct popup type based on `dialogue_type`. Add a type→popup mapping instead of assuming all items use `incoming_proposal_popup`.
- Ordering rule:
  - active soft-stop item first
  - then queued items by backend urgency/priority ascending
  - then FIFO within equal priority
  - preserve stable order across reopen, save/load, and non-diplomatic commands
- **Ordering metadata ownership:** When raw proposals become dialogues, copy the AI proposal urgency onto the dialogue (`mailbox_priority` or equivalent) and preserve a stable arrival sequence (`mailbox_id` seq or explicit `mailbox_order`) for FIFO ties. Do not rely on incidental list append order after save/load or activation swaps. Same-nation dedup must scan the active slot plus `dialogue_manager._queue`, not the removed `diplomatic_queue`.
- **Ordering consumer rule:** `mailbox_priority` / `mailbox_order` are the authoritative sort keys for both `GET /mailbox` and `DialogueManager._promote()` on `SOFT_STOP_MAILBOX_TYPES`. Keep `DIALOGUE_PRIORITY` only as fallback for non-mailbox types, and keep its mailbox-type fallback values aligned with the implementation order below (`counter_offer: 3`, `counter_offer_response: 3`, `conflict_alert: 4`).
- Selecting the active row simply reopens the current popup.
- Selecting a queued row must activate that item server-side before opening its popup. The previously active soft-stop item returns to the queue without data loss.
  - **Activation guard:** Only swap when the active slot is empty or already holds a `SOFT_STOP_MAILBOX` item. If the active slot holds a `HARD_STOP`, `HYBRID_SOFT_STOP`, or `LOCAL_PLANNING` type, both mailbox open and `POST /mailbox/activate` must return a blocked message instead of burying the active non-mailbox flow.
  - **Cache invalidation:** `world.incoming_proposal_popup` (main.py:1898-1904) caches the popup payload set at delivery time. `POST /mailbox/activate` must overwrite this cache with the newly activated item's data, or the recovery path (`/pending_envoy`, response polling) will show data for the wrong proposal. The same rule applies when an active item mutates in place (for example incoming proposal → `counter_offer`): rebuild the cached popup payload from the new terms, do not only flip flags such as `is_counter_offer`.
  - **Re-queued item lifetime:** When the previously active item is re-queued, preserve its original `turn_created`. Do not refresh the timestamp — this keeps `clear_stale` consistent and prevents indefinite keep-alive via repeated activation cycling.
- **Active popup-cache ownership:** `world.incoming_proposal_popup` is active-item-only state. Queued mailbox arrivals must NOT overwrite it just because a new item was pushed behind another current dialogue. Either store a popup-safe payload on each mailbox dialogue or guarantee `GET /mailbox` / `POST /mailbox/activate` / load-time recovery can rebuild it from dialogue context through one shared helper (including `counter_offer_response` created during `advance_turn`). On load or legacy `diplomatic_queue` migration, rebuild/validate the global cache from the active mailbox item only; ignore stale serialized popup data that points at a different mailbox item.
- **Mailbox identity continuity:** `mailbox_id`, `mailbox_order`, `mailbox_priority`, and the original arrival turn belong to the mailbox item, not to one specific dialogue type string. Preserve that metadata when the active item is enriched or replaced in place (for example `incoming_proposal` → `counter_offer` in `diplomatic_executor.py`) so the inbox row, dismissal state, and stale-selection handling still refer to the same pending item instead of a phantom "new" one.
- **Stale selection handling:** If a `mailbox_id` disappears between `GET /mailbox` and `POST /mailbox/activate` (expired, answered elsewhere, dropped on load cleanup), return a clean stale/not-found response with refreshed counts and leave the current active item untouched.
- `Ask Later` remains local and non-destructive:
  - close popup
  - re-enable normal input
  - keep the selected item pending
  - do not auto-consume or auto-reply
  - **Mailbox lifetime rule:** Do not inherit generic `clear_stale()` timeout behavior for mailbox items. Mailbox-eligible diplomacy is player-deferred, non-blocking inbox content and must not silently disappear on turn N+3. In this follow-up, remove generic mailbox expiry entirely. If any mailbox item ever gets an expiry later, it must be explicit on that item (`expires_on_turn` or equivalent), surfaced in the inbox UI, and covered by outcome logging/tests.
- The inbox panel, not repeated mailbox-button clicking, is the browsing mechanism for `Mailbox (2+)`.
- Accept / Counter / Reject always apply to the currently active item only. The activation step makes that deterministic.

**Recommended backend contract**

- Keep `/pending_envoy` for the simple "reopen current active item" path and backward compatibility, but make it active-item-only once the inbox exists. It must not silently choose a queued item. If there is no active mailbox item (queued-only state, or a hard-stop/hybrid/local-planning item is active with diplomacy queued behind it), return `has_pending = false` with an accurate `pending_envoy_count`; `GET /mailbox` is the authoritative browse surface for queued items.
- **Queued-only steady state:** After `diplomatic_queue` elimination, a mailbox-only queue with no active mailbox item should exist only when a non-mailbox current dialogue is in front, or during legacy-save migration before the first promotion pass. If the active slot is empty and only mailbox items remain, auto-promote the next mailbox item immediately instead of inventing a second long-lived steady state.
- Add `GET /mailbox` returning ordered mailbox-list summaries.
- Add `POST /mailbox/activate` with `mailbox_id`, returning the popup-safe payload for the now-active item.
- Add `mailbox_id` at proposal creation time and preserve it through:
  - `dialogue_manager.push()` (the sole queue after `diplomatic_queue` elimination)
  - delivery to active soft-stop
  - in-place enrichment / replacement of the active mailbox item (for example `incoming_proposal` → `counter_offer`)
  - re-queue of a previously active item
  - `counter_offer_response` items created during advance_turn (world_state.py:4488)
  - save/load serialization
- **`mailbox_id` generation:** Use `f"mb-{turn}-{seq}"` where `seq` is a per-turn monotonic counter on WorldState (e.g., `_next_mailbox_seq`). Serialize the counter. Avoids UUID dependency and stays deterministic for save/load. Reset per-turn is safe because `turn` prefix guarantees uniqueness.
- **Legacy-load metadata backfill:** On load, assign `mailbox_id` / `mailbox_order` / `mailbox_priority` to any restored mailbox dialogue that lacks them, including (a) current or queued `dialogue_manager` entries from pre-mailbox saves and (b) old `diplomatic_queue` items migrated during backward compat. After restoration/backfill, advance `_next_mailbox_seq` past every mailbox item already present for the current turn before generating new IDs, or a same-turn post-load arrival can collide with a restored item.
- Prefer preserving the original arrival metadata when an item is activated from queue; opening an old message should not make it look newly arrived.
- **Add `counter_offer` and `counter_offer_response` to `DIALOGUE_PRIORITY`** (dialogue_manager.py:66-71) as mailbox-type fallback values only. Currently these default to 99, causing incoming proposals (priority 3) to always sort before counter-offers whenever mailbox metadata is missing. Keep the fallback aligned with the ordering rule above: `counter_offer: 3`, `counter_offer_response: 3`, `conflict_alert: 4`.

**Recommended frontend contract**

- Mailbox button opens a lightweight inbox panel anchored to the existing top bar, not a full-screen modal.
- The panel should be non-destructive and easy to close; clicking outside or pressing the mailbox button again can dismiss it.
- Selecting a row triggers `activate -> popup open`.
- The panel should refresh after:
  - local defer
  - response submission
  - queue change from `/command` or `end turn`
  - save/load
- **End-turn rule:** Active mailbox soft-stops do NOT block `end turn` after this follow-up; only true hard-stop dialogues do. `end turn` should close the inbox panel first, then refresh mailbox state from the backend after turn advancement.
- **End-turn while panel open:** Close the inbox panel before submitting `end turn`. `advance_turn` can deliver new proposals, expire queue items, and clear stale dialogues — the panel would become stale. Simplest: close panel on any `/command` submission, reopen from fresh `GET /mailbox` after.
- If count drops to `0` while the panel is open, show an explicit empty state and close cleanly on next dismiss.
- **Replace `_dismissed_proposal_nation`** (main.gd:97): The current single-string tracker only suppresses one nation at a time. With the mailbox panel, either (a) disable auto-show entirely when the panel exists (preferred — the panel IS the browse mechanism), or (b) replace with a Set of dismissed `mailbox_id`s cleared on panel open.

- **Notification clear contract:** Once mailbox-eligible `DIPLOMATIC_PROPOSAL` notifications are suppressed/dismissed, the response/HUD path must explicitly clear the icon strip when none remain. Do not rely on omission of the `notifications` key to clear stale mailbox-related icons.

**Non-goals / adjacent note**

- Do not turn the mailbox into a generic notification center in this slice.
- Record the policy boundary for later HUD cleanup:
  - mailbox is for pending diplomatic decisions
  - mailbox-eligible diplomacy should not also create separate persistent `DIPLOMATIC_PROPOSAL` icon-strip entries once the inbox exists; use the mailbox badge plus campaign log/dispatch, and only a transient terminal/toast surface if an immediate arrival ping is still desired
  - persistent top-bar notifications should be reserved for action-required / strategically urgent items
  - routine combat/readiness notices such as `counterpunch ready` should be demoted later to event log, terminal feed, or transient toast instead of living indefinitely in the top-bar icon strip

**Exit criteria**

- The player can click `Later` on an incoming proposal and keep issuing commands immediately.
- Clicking the mailbox badge with multiple pending items opens a browsable inbox instead of one arbitrary proposal popup.
- The player can inspect and choose a specific pending diplomacy item when `Mailbox (2+)` is present.
- Clicking a queued mailbox row opens that chosen item, not whichever proposal happens to be active already.
- Delayed replies still work via typed popup buttons and through `/command` for `1/2/3`, `accept`, `counter`, and `reject`.
- `/pending_envoy` returns popup-safe data in the same display shape expected by `incoming_proposal_popup.gd` when an active reopenable mailbox item exists.
- Badge count and recovery behavior stay in sync for:
  - active soft-stop only
  - queued proposal only
  - active soft-stop plus queued proposals
  - five pending proposals in stable order
  - hard-stop active with queued proposals behind it
- No pending diplomacy item is lost, silently reordered, or spuriously consumed when the player browses the inbox.

**Regression test matrix**

- Extend Godot-facing popup tests for local defer behavior and re-enable-input flow.
- Add mailbox-list endpoint tests for:
  - active soft-stop only
  - queued-only (only when a non-mailbox current dialogue is in front, or during legacy-load migration before promotion)
  - active plus queue ordering
  - five pending items with stable order
  - hard-stop active with queued proposals still counted but not active
- Add activation tests proving a selected queued item becomes active and the previous active item is safely re-queued.
- Add endpoint tests for `/pending_envoy` covering:
  - active soft-stop returns reopenable popup payload
  - queued-only-behind-blocker (or pre-promotion legacy-load state) returns `has_pending = false` but keeps accurate `pending_envoy_count`
  - hard-stop-plus-queue returns no active popup payload and keeps accurate `pending_envoy_count`
- Add command-path tests proving soft-stop delayed replies still route for numeric and keyword inputs.
- Add save/load tests proving `mailbox_id` and queue order survive round-trip serialization.
- Add mailbox identity continuity tests proving:
  - `incoming_proposal` → `counter_offer` replacement keeps the same `mailbox_id` / `mailbox_order`
  - inbox refresh after a counter-offer still points at the same mailbox row instead of a duplicate/new item
- Add popup-cache ownership tests proving:
  - queued mailbox arrival does NOT overwrite the currently active item's popup payload
  - legacy-load / `diplomatic_queue` migration rebuilds the active popup cache from the promoted mailbox item, not stale serialized `incoming_proposal_popup`
  - `counter_offer_response` mailbox reopen/activation uses the same popup-safe builder as other mailbox items
- Add end-turn guard tests proving mailbox soft-stops do not block `end turn`, while true hard-stops still do.
- Add mailbox lifetime tests after `diplomatic_queue` removal:
  - deferred mailbox items are not force-cleared by generic `clear_stale()` timeout
  - active and queued mailbox items follow the same no-silent-expiry rule
  - if explicit per-item expiry is introduced later, it must be visible in inbox data and outcome logging
- Add hybrid soft-stop edge case tests:
  - hybrid active + diplomacy queued: badge count correct, mailbox shows only diplomacy
  - hybrid active does NOT appear in `GET /mailbox` response
  - hybrid active blocks mailbox open/activate instead of being swapped behind the inbox
- Add queue elimination migration tests:
  - all AI proposals reach `dialogue_manager._queue` after `diplomatic_queue` removal
  - badge count uses `get_mailbox_count()` exclusively (NOT `get_soft_stop_count()`)
  - PL-34 overflow logging fires from `DialogueManager`, not old `_enqueue_proposal` / `_expire_queue`
  - same-source dedup still works when the active item and queued item both live in `dialogue_manager`
  - `GET /mailbox` ordering and `DialogueManager._promote()` ordering both follow `mailbox_priority` + `mailbox_order`
  - no code calls `get_soft_stop_count()` for badge/UI purposes after `get_mailbox_count()` is added
  - `from_dict` backward compat: saved `diplomatic_queue` items are delivered into `dialogue_manager` on load, deduped by source+turn
  - legacy `dialogue_manager` mailbox items missing `mailbox_id` / `mailbox_order` are backfilled on load
  - `_next_mailbox_seq` is advanced past restored current-turn mailbox IDs before any new proposal is generated post-load
- Add `clear_stale` mailbox exemption tests:
  - `clear_stale()` skips `SOFT_STOP_MAILBOX_TYPES` in active slot regardless of `blocking` field value
  - mailbox item with `blocking=True` survives indefinitely (not force-cleared after `BLOCKING_TIMEOUT_TURNS`)
  - non-mailbox blocking dialogues still obey the existing safety valve timeout
- Add activation guard tests:
  - swap blocked when active slot holds `HARD_STOP`, `HYBRID_SOFT_STOP`, or `LOCAL_PLANNING`
  - `incoming_proposal_popup` cache updated on successful swap
  - `counter_offer` transition rebuilds cached popup clauses instead of only mutating `is_counter_offer`
  - re-queued item preserves original `turn_created`
  - stale `mailbox_id` activation fails cleanly without disturbing the current active item
- Add `counter_offer` priority ordering tests:
  - `counter_offer` vs `incoming_proposal` queue ordering after priority fix
- Add numeric-reply routing tests for soft-stop mailbox items:
  - "1" typed while soft-stop active matches first option
  - "2" typed while soft-stop active matches second option
  - numeric reply when no soft-stop active does NOT misroute
- Add dismiss-then-reopen tests for counter_offer_response:
  - "Dismiss" action on counter_offer_response keeps item pending
  - dismissed counter_offer_response reopenable from mailbox inbox
- Add dedup-after-elimination tests:
  - `_has_pending_proposal_from()` scans `dialogue_manager._queue` and active slot, not `diplomatic_queue`
  - same-nation proposal blocked when another from that nation is active or queued in dialogue_manager
- Add mailbox-vs-notification tests proving mailbox-eligible arrivals do not also leave behind duplicate persistent `DIPLOMATIC_PROPOSAL` icon-strip entries, and that the icon strip clears once no mailbox-related notifications remain.
- Re-run the existing Session 2 guard/count/history suite after the mailbox follow-up lands.

**Implementation trap warnings (sixth audit pass)**

These are concrete code paths that previous spec text covers implicitly but does not name. Missing any one will cause a runtime or logic bug:

- **`_has_pending_proposal_from()` (ai_diplomacy.py:277-301):** Scans `_get_queue(world)` for same-source dedup. After `diplomatic_queue` elimination, redirect this scan to `dialogue_manager._queue` (and active slot). Without this, duplicate proposals from the same nation will pile up.
- **`try_deliver_queued_proposal` import in turn_manager.py:302-303, call at 322-324:** Must be removed alongside the ai_diplomacy.py function body, or `ImportError` at runtime.
- **Inline `diplomatic_queue` expiry in world_state.py:4098-4101:** `self.diplomatic_queue = [q for q in self.diplomatic_queue if ...]` is a second expiry path outside `ai_diplomacy._expire_queue()`. Remove this block during step 0.
- **`meta_executor.py:2014-2016` debug cheat fallback:** Creates `world.diplomatic_queue` on demand and appends proposals directly. Redirect to `dialogue_manager.push()` with mailbox metadata.
- **`diplomatic_ledger.py:623`:** `len(getattr(world, 'diplomatic_queue', []))` — replace with `dialogue_manager.get_mailbox_count()` or equivalent pending-proposal query.
- **`diplomatic_executor.py:3217` `replace()` call (incoming_proposal → counter_offer):** Must copy `mailbox_id` / `mailbox_order` / `mailbox_priority` from the current dialogue onto the replacement dict. This is the only mailbox→mailbox `replace()` mutation; other `replace()` calls are local-planning flows that don't carry mailbox metadata.
- **`counter_offer_response` at world_state.py:4488-4514 sets `blocking: True`:** This type is in `SOFT_STOP_MAILBOX_TYPES`, so the step 4 `clear_stale` exemption must cover it specifically — without the exemption, the 2-turn safety valve force-clears it.
- **`_build_pending_envoy_popup_from_queue()` (main.py:1918-1929):** After queue elimination this helper has no callers. Remove it, and update the `elif result["pending_envoy_count"] > 0` branch at main.py:1964-1971 which uses it.
- **`is_soft_stop()` usage in badge formulas (main.py:172, 499, 859, 1947):** `is_soft_stop()` includes hybrids. All four sites must switch to the new `get_mailbox_count()`.

**Implementation order inside Session 2 follow-up**

0. **Eliminate `diplomatic_queue`:** Remove field from WorldState, remove `_enqueue_proposal`/`_dequeue_best`/`_expire_queue`/`try_deliver_queued_proposal` from ai_diplomacy.py, deliver all AI proposals via `deliver_ai_proposal()` → `dialogue_manager.push()` at generation time, and carry forward mailbox ordering/dedup metadata on the dialogue objects themselves. Remove one-per-turn throttle in `turn_manager._process_ai_diplomatic_phase()`. Migrate PL-34 overflow logging into DialogueManager (the 3-turn expiry from `advance_turn:4098` is removed entirely — mailbox items do not silently expire; overflow cap remains). Update all 4 badge formulas in main.py (`build_base_response:170`, `_include_popup_passthroughs:497`, end-turn response `:857`, `get_pending_envoy:1945`) to use `get_mailbox_count()`. Deprecate `get_soft_stop_count()` — it counts all queue items regardless of type and must not be used for badge/mailbox logic after `get_mailbox_count()` exists. Remove `diplomatic_queue` from `to_dict`/`from_dict` (add `from_dict` backward compat: if saved data has `diplomatic_queue`, deliver each item into `dialogue_manager` on load without duplicating already-active/queued items; dedup by source nation + turn since raw proposals lack `mailbox_id`). Suppress `DIPLOMATIC_PROPOSAL` persistent notification for mailbox-eligible proposals (`ai_diplomacy.py:905`) — use transient terminal arrival ping instead; the mailbox badge is the persistent surface. Also update: `_has_pending_proposal_from()` (ai_diplomacy.py:296), `meta_executor.py:2014-2016` cheat fallback, `diplomatic_ledger.py:623`, `turn_manager.py:302-324` import+call, and `world_state.py:4098-4101` inline expiry (see trap warnings above).
1. Add `counter_offer`/`counter_offer_response`/`conflict_alert` to `DIALOGUE_PRIORITY` (suggested: `counter_offer: 3`, `counter_offer_response: 3`, `conflict_alert: 4` — same-urgency as `incoming_proposal` for counter-offers, slightly lower for conflict alerts). Add `get_mailbox_count()` to `DialogueManager` that counts `SOFT_STOP_MAILBOX_TYPES` only (excludes hybrids).
   Use `mailbox_priority` / `mailbox_order` in both `DialogueManager._promote()` and `GET /mailbox`; `DIALOGUE_PRIORITY` is fallback only.
2. Add stable `mailbox_id` ownership (generation via `f"mb-{turn}-{seq}"` with per-turn counter on WorldState, serialization, presence on all mailbox-eligible dialogue types including `counter_offer_response` from advance_turn).
   Preserve mailbox metadata when the active item is replaced in place (`incoming_proposal` → `counter_offer`), and backfill missing mailbox metadata for restored legacy mailbox dialogues before advancing `_next_mailbox_seq`.
3. Add `GET /mailbox` plus `POST /mailbox/activate` (with cache invalidation for `incoming_proposal_popup`, activation guard for `HARD_STOP` / `HYBRID_SOFT_STOP` / `LOCAL_PLANNING`, re-queue with preserved `turn_created`). Lock ordering semantics with tests.
   Treat `incoming_proposal_popup` as active-item-only state: queued arrivals/load migration must rebuild per-item payloads instead of overwriting the active cache.
4. **Add type-based exemption in `clear_stale()` for `SOFT_STOP_MAILBOX_TYPES`:** skip clearing entirely when current dialogue type is in `SOFT_STOP_MAILBOX_TYPES`. Do NOT change the `blocking` field to `False` — that would trigger the non-blocking branch which clears on the very next turn. The `blocking=True` field is legacy; the type taxonomy is authoritative. Also confirm `is_blocking()` is not used in any guard path for soft-stops (it shouldn't be — guards use `is_hard_stop()`). Keep mailbox lifetime semantics inside the inbox contract. If explicit expiry is ever added later, make it per-item, visible in the inbox payload/UI, and logged.
5. Build the Godot mailbox panel/list. Wire mailbox button -> inbox open/close. Replace `_dismissed_proposal_nation` with panel-aware suppression. Add type→popup dispatch for `conflict_alert`.
6. Keep local defer behavior, but make inbox selection the authoritative "open this specific item" path.
7. Fix `/pending_envoy` shape and active-item-only backward-compat semantics so queued-only / hard-stop-plus-queue states are handled through `GET /mailbox`, not arbitrary queue reopening.
8. Fix soft-stop `/command` delayed-reply routing for numeric and keyword responses without widening back to global keyword misroutes. Specifically: add numeric-index matching (e.g. "1" → first option, "2" → second) against the active dialogue's `options` list for soft-stop dialogues (main.py:639-650), alongside the existing label/action text matching.
9. Lock the whole flow with mailbox browse/defer/select/respond-later regressions (including expanded test matrix above) before moving to `PL-32`.

### Session 3 - Diplomacy Display Contract

**Items:** `PL-32`

**Goal:** make the backend the single owner of player-facing diplomacy labels once the Session 2 follow-up transport contract is stable.

**Exit criteria**

- Incoming proposal, counter-offer, sabotage, and fallback popup text all come from the same backend formatter.
- Godot stops rebuilding proposal labels from raw identifiers.

### Session 4 - First-Hour Pressure Cleanup

**Items:** `PL-28`, `PL-26`

**Goal:** remove unfair defeat surprise and make the first combat lesson legible without flattening combat depth.

**Exit criteria**

- Players receive an explicit defeat-imminent warning before the live loss rule fires.
- The obvious early French attack line is no longer a hidden trap with no surfaced counterplay.

### Session 5 - Restart Flow

**Items:** `PL-29`

**Goal:** allow a clean restart from the live client/server flow without manual process kill or stale autosave leakage.

**Exit criteria**

- A supported `POST /new_game` contract exists.
- The pause menu exposes it.
- Autosave/restart behavior is explicit and regression-tested.

---

## Active Bug Specs

### PL-30: Godot crash after a masked proposal result

**Problem statement**

A proposal result can be hidden behind a higher-priority popup, then the next Diplomacy-button interaction crashes Godot with `attempt to call function add_output on a base null instance`.

**Confirmed evidence**

- Playtest Session D reproduction: send a proposal, let a higher-priority popup win, then open Diplomacy on the next turn and hit the crash.
- The current popup pipeline only forwards one winner per response cycle through `_include_popup_passthroughs()`.
- The frontend crash string points at a stale/null `add_output` path rather than a cleanly recoverable deferred result.
- `diplomacy_wizard.gd` has two matching fallback branches: `_render_nations()` and `_render_preview()` both close the wizard and call `get_node("/root/Main").add_output(...)` whenever `dialogue_pending` is true.
- `/command` still has an enemy-phase path that consumes `proposal_result_popup` outside the main response builder, so proposal-result ownership is already split.

**Root-cause notes**

- `_include_popup_passthroughs()` only surfaces one winning popup per response cycle, so lower-priority proposal results can remain pending after a different popup displays first.
- The diplomacy preview contract is too coarse. Step 1 preview in `backend/main.py` and Step 2 preview in `backend/game_logic/diplomacy.py` both collapse multiple states into `dialogue_pending`, even when the real condition is "recoverable proposal result is still pending."
- The frontend wizard treats that coarse flag as a fatal block and routes through a null-prone terminal logging path instead of a structured recovery surface.
- Step 1 and Step 2 are the same failure family and stay under `PL-30`; do not split them into separate work.

**Exact code surfaces**

- `backend/main.py` - `build_base_response()`, `_include_popup_passthroughs()`, enemy-phase `/command` proposal-result handling, `/diplomatic_preview`.
- `backend/game_logic/diplomacy.py` - `get_available_diplomatic_actions()`, `get_diplomatic_preview()`.
- `godot-client/project-sovereign/scripts/main.gd` - `add_output()`, `_on_proposal_result_dismissed()`, `_on_diplomacy_button_pressed()`, `_open_diplomacy_wizard()`.
- `godot-client/project-sovereign/scripts/diplomacy_wizard.gd` - `_render_nations()`, `_render_preview()`.

**Exact failure modes**

- A higher-priority popup wins the current response, leaving `proposal_result_popup` deferred.
- The player reopens diplomacy. Step 1 or Step 2 sees only `dialogue_pending = true`, not the real deferred-result state.
- The wizard closes itself and tries to log via `get_node("/root/Main").add_output(...)`.
- If that node lookup is invalid in the current tree state, Godot throws the observed null-instance crash.
- Even when no crash occurs, the deferred result is still on an ambiguous contract and can be lost or redisplayed incorrectly.

**Edge cases / sibling failure scan**

- Reopen diplomacy from the button and from any shortcut/hotkey path.
- Reopen on the same turn as the masked popup and after a turn advance.
- Reproduce both Step 1 nation-list rendering and Step 2 action preview rendering.
- Verify the flow when a proposal result is pending but a true blocking dialogue is not.
- Verify dismissal does not create double-delivery on the next response cycle.

**State-transition risks**

- Clearing or dismissing the proposal result must happen in one source of truth; otherwise the same popup can reappear after the wizard or after enemy phase.
- `_on_proposal_result_dismissed()` currently refreshes war data and input state only. If proposal-result ownership moves, the dismissal hook must clear the retained result state as well.
- Save/load and turn-advance flows must not resurrect a stale deferred result after it has been dismissed.

**Backend / frontend contract risks**

- `dialogue_pending` is not precise enough for the diplomacy wizard. The fix needs an explicit distinction between a blocking diplomacy dialogue and a recoverable deferred result.
- Wizard-side code should not depend on a hard-coded `/root/Main` lookup to report contract state.
- The fix should not pull full Session 6 popup-registry work earlier; it only needs to restore single-source ownership for proposal results.

**Acceptance criteria**

- Reproducing the original masked-result flow no longer crashes the client.
- A proposal result that loses popup priority remains recoverable until it is displayed or explicitly dismissed.
- Opening the Diplomacy wizard after a masked result distinguishes "blocking dialogue" from "deferred result" instead of treating both as generic `dialogue_pending`.
- Neither Step 1 nor Step 2 of the wizard calls the null-prone `get_node("/root/Main").add_output(...)` fallback for this flow.
- Lower-priority proposal results are not discarded just because another popup displayed first.

**Regression test matrix**

- Backend response test: a lower-priority `proposal_result_popup` survives a higher-priority popup cycle and remains present until dismissed.
- Backend preview test: `/diplomatic_preview` and the Step 2 preview path return a structured non-crashing state when a deferred proposal result exists.
- Frontend smoke: `proposal reply masked -> next turn diplomacy open` via diplomacy button.
- Frontend smoke: the same flow through Step 2 preview and result dismissal.
- Re-run popup contract suites after the ownership change.

**Dependencies / blockers**

- No upstream blocker.
- Re-check this flow after Session 2 if mailbox semantics touch the same proposal-result surfaces.

**Implementation order inside Session 1**

1. Normalize proposal-result ownership so `_include_popup_passthroughs()` and the `/command` enemy-phase path stop diverging.
2. Replace the coarse wizard gating path with an explicit backend/frontend distinction between blocking dialogue and deferred result.
3. Remove the null-prone `add_output()` recovery call from both Step 1 and Step 2 render paths.
4. Add persistence tests for masked results, then rerun the original repro flow manually.

---

### PL-31: Capital-loss instant defeat is still live, and its regression test is broken

**Problem statement**

The game still hard-loses when Paris falls, even though the project history and regression test claim that capital-loss defeat was removed.

**Confirmed evidence**

- `backend/game_logic/turn_manager.py::_check_victory_conditions()` still returns defeat on captured capital.
- `tests/test_playtest_bugfixes.py::TestCapitalLossNotDefeat` targets `Ile-de-France`, which is not a live region key, so the test passes vacuously.
- Direct reproduction with `world.regions["Paris"].controller = "Prussia"` returns `Your capital has fallen!`.
- Historical status text still contains a now-false March 9 claim that capital-loss defeat was removed.

**Root-cause notes**

- `_check_victory_conditions()` still contains the obsolete capital-capture defeat branch even though the intended rule and prior notes say capital loss should be survivable.
- The regression test never exercised the live branch because it points at a nonexistent region key.
- `docs/STATUS.md` inherited the false "already fixed" claim, so code, test, and docs all drifted together.

**Exact code surfaces**

- `backend/game_logic/turn_manager.py` - `_check_victory_conditions()`.
- `tests/test_playtest_bugfixes.py` - `TestCapitalLossNotDefeat`.
- `docs/STATUS.md` - current-phase summary plus the March 9 historical note that now needs a superseded marker.

**Exact failure modes**

- Capturing Paris immediately ends the campaign even while France still has armies and other regions.
- The false-negative regression test allows the obsolete branch to survive future refactors.
- Downstream warning work in `PL-28` would otherwise target the wrong defeat rule.

**Edge cases / sibling failure scan**

- Capital loss with surviving armies and surviving territory must continue the game.
- Zero armies must still lose.
- Zero controlled regions must still lose.
- Time-expiry victory/defeat logic must remain unchanged.

**State-transition risks**

- Removing the capital-loss branch must not weaken the existing `game_over` flow for the real defeat paths.
- Any defeat summary, dispatch text, or end-turn path that referenced capital loss as terminal must be aligned to the surviving rules before `PL-28` starts.

**Backend / frontend contract risks**

- The live defeat rule is backend-owned; frontend and docs must not preserve stale capital-loss wording after the code fix.
- The repaired regression test must target the real live region key so future refactors fail loudly if the branch returns.

**Acceptance criteria**

- Capturing Paris alone does not end the game while France still has territory or armies.
- The regression test targets `Paris` and fails if capital-loss defeat comes back.
- `docs/STATUS.md` no longer implies this bug is already resolved.
- PL-28 warning logic is based on the surviving defeat rules, not the obsolete capital-loss branch.

**Regression test matrix**

- Repair `tests/test_playtest_bugfixes.py` to use `Paris`.
- Add or keep a direct defeat-state test that proves capital loss alone is non-fatal.
- Re-run defeat-condition coverage around zero-territory, all-marshals-destroyed, and time-expiry paths.

**Dependencies / blockers**

- Unblocks PL-28.
- If design direction changes later and capital loss becomes fatal again, reopen PL-31 rather than silently changing the rule.

**Implementation order inside Session 1**

1. Remove the capital-loss defeat branch from `_check_victory_conditions()`.
2. Repair the regression test to target `Paris` and add a direct non-fatal capital-loss assertion.
3. Re-run defeat-path tests to confirm only the intended loss rules remain.
4. Update `docs/STATUS.md` so the historical note is explicitly marked as disproven rather than silently left in place.

---

### PL-27: Diplomacy interrupt contract is broken

**Problem statement**

Soft-stop diplomacy is still treated like a hard-stop crisis. Incoming AI proposals and related items block ordinary commands, the player has no authoritative mailbox/recovery surface, pending counts are wrong, and several popup buttons still route back through stringly parser commands.

**Confirmed evidence**

- `backend/commands/executor.py` and `backend/main.py` both hard-stop on any `pending_diplomatic_dialogue`.
- `backend/game_logic/ai_diplomacy.py` still delivers incoming proposals with `blocking = True`.
- `backend/main.py::build_base_response()` and `backend/game_logic/diplomatic_ledger.py` both derive `pending_envoy_count` from queue length only, ignoring an active pending dialogue.
- `godot-client/project-sovereign/scripts/main.gd::_on_envoy_clicked()` only prefills `Talleyrand, report on the waiting envoy`; it does not open a real recovery surface.
- `backend/campaign_log.py` does not retain proposal-arrival events, so masked or auto-rejected opportunities are not authoritatively recoverable from history.
- Remaining popup handlers still use parser-shaped command text instead of typed dialogue responses.

**Root-cause notes**

- Both backend command paths treat any `pending_diplomatic_dialogue` as a global blocker before ordinary command handling can continue.
- The codebase already has a blocking taxonomy signal (`dialogue.get("blocking")`, `dialogue_manager.is_blocking()`, `meta_executor` special-casing for `end_turn`), but that taxonomy is not enforced consistently across `/command`, executor routing, previews, or UI entry points.
- Incoming proposals are still delivered as `blocking = True`, which collapses mailbox-style diplomacy into crisis-style interruption.
- The pending-envoy badge is not authoritative because it ignores the active pending item and counts only queued items.
- Recovery is not authoritative because the envoy button only pre-fills parser text and several popup responses still synthesize English commands instead of stable option ids.
- Same-family command failures on `status`, `help`, `economy`, `treasury`, and `finances` belong here. Do not create new PL items for those paths unless a post-fix repro survives the contract cleanup.

**Exact code surfaces**

- `backend/commands/executor.py` - pending-dialogue guard in `execute()`.
- `backend/main.py` - `/command` dialogue guard, `build_base_response()`, typed dialogue endpoint.
- `backend/game_logic/ai_diplomacy.py` - incoming proposal delivery, cooldown/frequency behavior, queue handling.
- `backend/game_logic/diplomatic_ledger.py` - pending envoy count and related visibility.
- `backend/models/dialogue_manager.py` and `backend/models/world_state.py` - stale-dialogue clearing and turn-advance behavior.
- `backend/campaign_log.py` - diplomacy event whitelist/history retention.
- `godot-client/project-sovereign/scripts/main.gd` - incoming proposal response handlers, envoy click target, remaining `send_command` fallbacks.
- `godot-client/project-sovereign/scripts/top_bar.gd` and related diplomacy UI entry points - badge/count presentation for the mailbox surface.

**Exact failure modes**

- A soft-stop incoming proposal freezes `status` and other ordinary commands because the guard fires before command execution.
- The active pending proposal is invisible to the top-bar badge if the queue is empty.
- Clicking the envoy badge does not reopen the pending item; it only sends a parser phrase and depends on brittle keyword recovery.
- Popup handlers for incoming proposal, objection, sabotage, and rebellion still route through parser text, which can drift from valid dialogue option ids.
- Queue promotion, dismissal, and stale-dialogue cleanup can all happen without an authoritative mailbox/history record of what the player actually missed.

**Edge cases / sibling failure scan**

- No pending dialogue: normal command execution must remain unchanged.
- Hard-stop dialogue active: command blocking must remain intact for true hard-stop crises.
- Soft-stop dialogue active with no queue: read-only and ordinary non-dialogue commands must still work.
- Soft-stop dialogue active with queued items behind it: badge/count and recovery surface must show both active and queued work.
- `end_turn` remains special: it may still require explicit handling or auto-default behavior for certain dialogue families.
- Same-family nearby commands `status`, `help`, `economy`, `treasury`, and `finances` must all be verified under the new guard split.

**State-transition risks**

- Reclassifying dialogue types without aligning stale cleanup can cause items to clear unexpectedly on turn advance.
- Active-to-queued-to-history transitions must update the badge/count exactly once at each step.
- If only one backend command path is fixed, the parser and direct executor paths will drift and create inconsistent behavior.
- Typed popup responses must not bypass the same world-state transitions used by parser-driven dialogue handling.

**Backend / frontend contract risks**

- The response contract needs more than a coarse `dialogue_pending` boolean. The frontend needs an authoritative distinction between hard-stop dialogue, active soft-stop item, and queued mailbox items.
- The envoy badge must be derived from the same backend-owned count in every response path.
- Recovery should reuse the existing envoy/desk surface rather than inventing a second parallel inbox flow.
- Popup handlers should send stable response ids to `/respond_to_diplomatic_dialogue`, not synthesized English text.

**Acceptance criteria**

- Hard-stop vs soft-stop taxonomy is enforced in both backend command paths.
- For the current fix phase, the minimum taxonomy is:
  - hard-stop: `force_declare_war_confirmation`, `alliance_paradox`
  - soft-stop mailbox: `incoming_proposal`, `counter_offer`, `counter_offer_response`, `conflict_alert`
  - hybrid soft-stop with end-turn default: `sabotage_confrontation`, `vassal_rebellion_imminent`
  - local planning flow, not global blocker: `proposal_confirm`, `advisory`, `mission`, `terms_guidance`, `ultimatum_demand_wizard`
- Incoming proposals, counter-offers, conflict alerts, and similar soft-stop items no longer freeze ordinary commands.
- Soft-stop diplomacy has a visible mailbox or desk surface with a trustworthy badge/count.
- Pending envoy count includes both the active soft-stop item and queued items.
- Envoy click opens the recovery surface instead of only prefilling terminal text.
- Auto-reject, dismissal, and expiry outcomes are recorded in dispatch/history so the player can tell what happened.
- Popup choices for dialogue-shaped diplomacy flows use typed response ids instead of synthesized English commands.

**Regression test matrix**

- Extend `tests/test_dialogue_manager.py` for hard-stop vs soft-stop classification and stale-clear behavior.
- Extend `tests/test_bugfix_proposal_flow.py` for non-blocking proposals, mailbox recovery, queued visibility, and auto-outcome logging.
- Extend `tests/test_endpoint_wiring.py` or `tests/test_response_pipeline.py` for authoritative pending counts and mailbox payload shape.
- Add command-path regressions for `status`, `help`, `economy`, `treasury`, and `finances` with no dialogue, soft-stop dialogue, and hard-stop dialogue.
- Re-run popup response tests after migrating the affected handlers to typed response ids.

**Dependencies / blockers**

- Root dependency for PL-34 and PL-33.
- Blocks PL-32.
- Blocks diplomacy refinement items that need a trustworthy interrupt model, especially R162.

**Implementation order inside Session 2**

1. Normalize the blocking taxonomy and enforce it in both backend command paths before parser execution.
2. Reclassify incoming proposals and other soft-stop flows so they stop acting like hard-stop crises.
3. Make the pending-envoy count authoritative by including both the active soft-stop item and queued items in one backend-owned contract.
4. Wire the envoy badge to a real recovery surface and migrate the affected popup handlers to typed dialogue responses.
5. Add history/dispatch outcomes for arrival, dismissal, expiry, overflow, and auto-default behavior.
6. Run the `PL-33` duplicate verification pass last, after the guard split and recovery surface are both live.

---

### PL-34: Queued diplomatic proposals can expire unseen behind blockers

**Problem statement**

Queued proposals can age out or get dropped before the player ever sees them, so diplomacy is currently being resolved by hidden queue expiry and overflow rules instead of explicit player choice.

**Confirmed evidence**

- Queue expiry removes proposals after three turns.
- Queue overflow keeps only the top three items and silently drops the rest.
- Queued delivery expires items before attempting delivery.
- Blocking dialogues can linger until the stale-dialogue cleanup path, which lets unseen queued items die behind them.
- The focused reproduction showed a later Prussian proposal expiring before it was ever surfaced because an Austrian blocker remained active first.

**Root-cause notes**

- Queue age currently starts at generation time, not at first player visibility.
- `try_deliver_queued_proposal()` expires queued work before attempting delivery, so a proposal can die on the same turn it would otherwise become visible.
- Queue overflow silently drops lower-ranked items once `QUEUE_MAX_SIZE` is exceeded.
- There is no authoritative mailbox/history record at enqueue time, so "waiting envoy" state is invisible until delivery succeeds.
- This belongs under `PL-27` because the real fix is the mailbox/visibility contract, not a separate proposal subsystem.

**Exact code surfaces**

- `backend/game_logic/ai_diplomacy.py` - `_expire_queue()`, `_enqueue_proposal()`, `_dequeue_best()`, `try_deliver_queued_proposal()`.
- `backend/models/dialogue_manager.py` - stale-dialogue cleanup timing.
- `backend/models/world_state.py` - dialogue clear path on turn advance.
- `backend/game_logic/turn_manager.py` - delivery timing relative to turn flow.
- Mailbox/count surfaces introduced by PL-27.

**Exact failure modes**

- A queued proposal generated behind another blocker can expire before first surface.
- Overflow beyond queue capacity silently discards proposals with no player-visible record.
- Badge/count state does not reveal that proposals are waiting or that they were dropped/expired.
- Clearing a blocker does not guarantee the player can inspect what arrived while that blocker was active.

**Edge cases / sibling failure scan**

- One active soft-stop item plus one queued item.
- One hard-stop item plus queued proposals behind it.
- Queue reaches capacity and receives one more proposal.
- A blocker clears on the same turn an older queued item would otherwise expire.
- Expiry, dismissal, and promotion all occur around turn advance or stale-dialogue cleanup.

**State-transition risks**

- Making queued arrivals visible at enqueue time must not double-count the item when it later becomes active.
- Expiry and overflow outcomes must remove the item from badge counts exactly once.
- Delivery-order policy should stay stable while visibility/accounting changes; do not mix count fixes with a ranking rewrite.

**Backend / frontend contract risks**

- If the mailbox payload only exposes the active item, queued proposals will remain invisible and this bug will survive under a new badge.
- If expiry/overflow are only logged in history but not reflected in the active count, the top bar will drift out of sync.

**Acceptance criteria**

- Queued proposal arrival becomes visible immediately through the authoritative envoy/mailbox contract, even if another item is currently blocking delivery.
- Unseen soft-stop proposals do not disappear silently.
- Expiry and overflow create explicit recorded outcomes; they never remove an item without a player-visible record.
- Delivery after the blocker clears preserves the existing queue policy unless a direct test proves the policy itself is wrong.
- The player can review what arrived, what expired, and what was auto-rejected through the mailbox/history flow introduced by `PL-27`.

**Regression test matrix**

- Extend `tests/test_bugfix_proposal_flow.py` for blocker-behind-queue visibility, hidden-expiry conversion into recorded outcomes, and overflow recording.
- Extend `tests/test_dialogue_manager.py` for promotion and stale-clear timing around queued items.
- Add a regression proving that a queued proposal generated behind another soft-stop item is still visible in the mailbox and is either surfaced or explicitly logged before removal.

**Dependencies / blockers**

- Implement inside the PL-27 batch.
- Depends on the new soft-stop/mailbox contract.

**Implementation order inside Session 2**

1. After the `PL-27` mailbox contract exists, make queued arrivals visible at enqueue time.
2. Convert expiry and overflow into explicit recorded outcomes.
3. Verify badge/count transitions across active, queued, expired, and dismissed states.
4. Re-run the focused unseen-expiry repro before closing the item.

---

### PL-33: `status` is blocked by the diplomacy guard and recovery path

**Problem statement**

The first-hour command most players are likely to try, `status`, is currently being swallowed by the same diplomacy guard/recovery failure that blocks ordinary commands.

**Confirmed evidence**

- The parser already recognizes `status`.
- `_execute_status()` exists and returns a valid intel report.
- The observed failure path happened while an incoming diplomatic dialogue was active.
- Current evidence does not show a clean no-dialogue reproduction.

**Root-cause notes**

- Current evidence points to the same global-guard failure family as `PL-27`, not to a broken `status` implementation.
- `meta_executor._execute_status()` already exists and is valid; the likely fault is that the guard fires before the command reaches it.
- Same-family read-only commands should be verified together instead of patching `status` alone.

**Exact code surfaces**

- `backend/commands/executor.py` - pending-dialogue guard.
- `backend/main.py` - parser-side dialogue guard.
- `backend/commands/meta_executor.py` - `_execute_status()`.

**Exact failure modes**

- `status` is blocked when a soft-stop diplomacy item is pending.
- The same failure family can also swallow other read-only commands that should remain available.
- Shipping a separate `status` patch before the taxonomy fix risks treating the symptom and leaving the family bug alive.

**Edge cases / sibling failure scan**

- `status` with no dialogue pending.
- `status` with soft-stop dialogue pending.
- `status` with true hard-stop dialogue pending.
- The same matrix for `help`, `economy`, `treasury`, and `finances`.

**State-transition risks**

- If `status` is special-cased instead of fixing the guard contract, the next read-only command will fail in the same way.

**Backend / frontend contract risks**

- None beyond the `PL-27` guard split; this item should not create new contract surfaces unless a post-fix repro survives.

**Acceptance criteria**

- After `PL-27` lands, `status` works with no pending dialogue.
- After `PL-27` lands, `status` also works while soft-stop diplomacy is pending.
- True hard-stop dialogue still blocks `status` where intended.
- If a non-dialogue-guard failure still exists after those checks, keep `PL-33` open and split it into a true standalone bug.

**Regression test matrix**

- Add a focused command-path regression for `status` with no dialogue, with soft-stop dialogue, and with a true hard-stop dialogue.
- Add the same verification sweep for `help`, `economy`, `treasury`, and `finances` under the owning `PL-27` test family.

**Dependencies / blockers**

- Blocked on PL-27.
- Duplicate-candidate; do not ship separate code unless a post-PL-27 reproduction remains.

**Implementation order inside Session 2**

1. Leave `PL-33` untouched until the `PL-27` guard split, mailbox contract, and typed-response recovery path are live.
2. Run the focused read-only command matrix.
3. Close as duplicate if the matrix passes; keep open only if a non-guard repro remains.

---

### PL-32: Raw diplomacy labels can leak into popups

**Problem statement**

Proposal and clause display ownership is split across backend and Godot, so raw identifiers such as treaty enums or underscore tokens can leak into popups or degrade wording on fallback paths.

**Confirmed evidence**

- Backend and Godot both keep proposal display mappings.
- `backend/main.py` still formats fallback proposal text ad hoc.
- `backend/game_logic/diplomatic_dialogue.py` rebuilds clause display separately.
- `backend/models/world_state.py` builds counter-offer popup clauses directly from raw clause ids.
- `backend/commands/diplomatic_defiance.py` and `backend/game_logic/ai_diplomacy.py` still own separate formatting paths.

**Root-cause notes**

- Display ownership is split across `backend/display_names.py`, multiple backend helpers, and Godot popup scripts.
- The strongest live raw-leak path is counter-offer popup construction in `world_state.py`, which still builds clauses from raw ids.
- `_include_popup_passthroughs()`, `diplomatic_dialogue.py`, `ai_diplomacy.py`, and sabotage summary code all keep separate fallback formatting logic, so wording can drift even when raw ids do not leak.
- The duplicate Godot proposal-type map is part of the same family and belongs here rather than in a new frontend-only item.

**Exact code surfaces**

- `backend/display_names.py` - canonical display source.
- `backend/main.py` - popup safety-valve formatting.
- `backend/game_logic/diplomatic_dialogue.py` - proposal/clause rendering helpers.
- `backend/models/world_state.py` - counter-offer popup payload construction.
- `backend/commands/diplomatic_defiance.py` - sabotage proposal summary formatting.
- `backend/game_logic/ai_diplomacy.py` - secondary clause display map.
- `godot-client/project-sovereign/scripts/incoming_proposal_popup.gd` - duplicate proposal-type map and underscore fallback.

**Exact failure modes**

- Counter-offer popups can show raw clause ids such as `territory_cede`.
- Proposal type labels can diverge between backend and Godot because both sides keep their own display maps.
- Safety-valve fallback paths can degrade into inconsistent title-casing such as `Open_Borders` or `Non_Aggression`.
- Sabotage and AI proposal summaries can describe the same clause family differently from incoming-proposal popups.

**Edge cases / sibling failure scan**

- Unknown or newly added clause ids should still render through one centralized fallback instead of leaking raw tokens.
- Counter-offer, incoming proposal, sabotage, and fallback popup paths must all be tested together.
- Legacy save data or modded clause ids should degrade consistently through the same formatter.

**State-transition risks**

- Removing the Godot-side map before all backend payloads are normalized can make some popups go blank.
- If one popup path still ships raw ids after the formatter centralization, the bug will survive in a fallback path and be harder to detect.

**Backend / frontend contract risks**

- The backend should ship fully rendered labels plus canonical ids only where machine logic still needs them.
- Godot should render provided display strings, not rebuild labels from ids.

**Acceptance criteria**

- Backend becomes the only owner of human-readable proposal and clause labels.
- Incoming proposal, counter-offer, sabotage, and fallback popup paths all consume the same backend formatter.
- Godot no longer rebuilds proposal labels from enum names or underscore replacement.
- Unknown ids degrade through one centralized fallback formatter instead of leaking raw tokens.
- Popup payload tests fail on raw tokens such as `NON_AGGRESSION`, `territory_cede`, or `Open_borders`.

**Regression test matrix**

- Add backend formatter tests for proposal type and clause rendering.
- Extend popup payload contract tests so raw underscore or enum-style tokens fail.
- Re-run proposal-flow and popup suites after removing the Godot duplicate map.

**Dependencies / blockers**

- Depends on Session 2 transport cleanup so the popup contract is stable before display ownership is collapsed.

**Implementation order inside Session 3**

1. Centralize proposal-type and clause-label rendering in `backend/display_names.py`.
2. Replace backend duplicate formatters in `main.py`, `diplomatic_dialogue.py`, `world_state.py`, `diplomatic_defiance.py`, and `ai_diplomacy.py`.
3. Remove the duplicate Godot proposal-type map and fallback formatting.
4. Re-run popup payload tests, especially counter-offer and sabotage paths.

---

### PL-28: No defeat-imminent warning before game over

**Problem statement**

The player can cross from a damaged position into defeat without any clear "you are about to lose" warning in the notification or dispatch layer.

**Confirmed evidence**

- Current defeat-state rules are already inconsistent enough that the player cannot predict what will end the campaign.
- The playtest loss happened without visible warning.
- The fix must follow the surviving defeat rule after PL-31, not the obsolete capital-loss branch.

**Root-cause notes**

- `turn_manager.py` checks terminal defeat only; it has no near-defeat helper that can emit warnings before the loss condition fires.
- After `PL-31`, the live battlefield defeat rules are "all armies destroyed" and "all territory lost." Time-limit warning already has its own system and should stay separate.
- The current item should not expand into predictive enemy-intent simulation. It only needs a deterministic warning tied to the actual surviving defeat thresholds.

**Exact code surfaces**

- `backend/game_logic/turn_manager.py` - defeat evaluation order.
- `backend/models/world_state.py` - any surviving defeat-threshold tracking.
- `backend/notifications.py` - defeat-imminent notification type.
- `backend/game_logic/dispatch.py` - morning-dispatch warning surfacing.

**Exact failure modes**

- The player can step into terminal defeat with no prior warning when only one army or one region remains.
- Warning wording can drift toward the obsolete capital-loss rule if `PL-31` is not treated as the source of truth first.
- If warning logic mixes in time-limit or enemy-intent prediction, the result will spam or mislead instead of clarifying the live loss rule.

**Edge cases / sibling failure scan**

- Exactly one surviving marshal remains.
- Exactly one controlled region remains.
- The player recovers above the threshold after a warning and should not keep stale warning spam.
- Time-limit warning stays on its separate path and is not merged into this item.

**State-transition risks**

- Warning state must persist long enough to appear in both notifications and the next dispatch, but it must also clear if the player stabilizes.
- The warning should fire before defeat resolution, not after a terminal result has already been returned.

**Backend / frontend contract risks**

- The warning should reuse the existing notification and dispatch surfaces, not create a one-off popup path.
- Wording must match the live defeat rule after the capital-loss branch is removed.

**Acceptance criteria**

- After `PL-31`, a high-visibility warning is emitted when France is down to exactly one living marshal and/or exactly one controlled region.
- The player receives the warning before the live defeat rule fires.
- Warning wording matches the actual surviving defeat condition after `PL-31`.
- The warning appears in both notifications and the following dispatch/readout path while the condition persists.
- The warning clears or stops repeating once the player climbs back above the threshold.

**Regression test matrix**

- Add defeat-warning coverage around the surviving loss threshold.
- Add notification/dispatch assertions so the warning is emitted before the actual defeat result.
- Verify that time-limit warnings are unchanged and remain separate.

**Dependencies / blockers**

- Blocked on PL-31.

**Implementation order inside Session 4**

1. Remove the obsolete capital-loss path via `PL-31` first.
2. Add a deterministic near-defeat helper keyed to one remaining marshal and one remaining region.
3. Wire it into notifications and morning dispatch.
4. Add non-spam coverage for warning persistence and recovery above the threshold.

---

### PL-26: Combat feels hopeless because the obvious opener teaches the wrong lesson

**Problem statement**

The common early "Ney attacks Wellington" line is punishing before the game has taught bombardment, coordination, or setup counters, so the player learns "attacking is hopeless" instead of learning the system.

**Confirmed evidence**

- Repeated attacks in playtest produced defender victories or punishing stalemates.
- Existing audit synthesis says this is primarily a teaching/setup problem, not proof that the combat system lacks depth.
- The current opener surfaces defender stacking before it surfaces viable French preparation lines.

**Root-cause notes**

- The likely first-hour attack line (`Ney` into `Wellington`) presents stacked defensive advantages before the game teaches the counters.
- The old coordination preview is gone, and the first-time coordination tutorial only fires after the player already achieves combined arms.
- The existing bombardment advisory fires only after the player already used artillery correctly.
- This makes the current problem a teaching/order-of-information failure first. Narrow numeric tuning is the fallback only if guidance plus setup still leave the opener feeling hopeless.

**Exact code surfaces**

- `backend/game_logic/combat.py` - modifier surfacing and common-opener outcome messaging.
- `backend/commands/combat_executor.py` - first-time coordination tutorial, bombardment advisory, and any added opener guidance on the attack flow.
- `backend/models/marshal.py` and region/terrain data only if number tuning is still required after surfacing fixes.
- Any tutorial, advisory, dispatch, or wizard surface used to expose the better line.

**Exact failure modes**

- The naive `Ney, attack Wellington` line produces a punishing result before the player is told about bombardment, combined arms, or defender terrain advantages.
- The game teaches combined arms only after success instead of before commitment.
- The post-bombardment advisory is useful but arrives too late to teach the player what to try first.

**Edge cases / sibling failure scan**

- If `Drouot` is unavailable, advice should still surface a non-artillery preparation line rather than naming an impossible move.
- The added guidance should target the common first-hour opener, not spam every later battle.
- Prepared assaults should improve the outcome materially without making all direct attacks trivially safe.

**State-transition risks**

- Guidance added only after the battle result may still be too late if the first failed assault already ends the campaign.
- Broad stat nerfs or buffs could mask the teaching failure while flattening later combat depth.

**Backend / frontend contract risks**

- Reuse existing advisory, objection, tutorial, or result surfaces; this item does not need a new UI system.
- If the advice is conditional, the trigger conditions must stay deterministic enough for regression coverage.

**Acceptance criteria**

- At least one obvious early French preparation line is surfaced as materially better than the naive direct assault.
- The game exposes the key counters behind the Wellington opener before or at the point the player is likely to commit.
- The prepared line is measurably better in the deterministic regression scenario than the naive line.
- Combat depth stays intact; this item does not flatten the system into guaranteed attack wins.

**Regression test matrix**

- Add a deterministic scenario test for the common opener and one prepared alternative.
- If guidance is added to objections, dispatch, or preview text, add a regression that the surfaced advice names the relevant counterplay.
- If narrow number tuning is required, add a regression proving the prepared line improves while the naive unsupported line is still risky.

**Dependencies / blockers**

- No hard code dependency.
- Intentionally sequenced after Sessions 1-3 so crash/defeat/diplomacy noise does not contaminate first-hour tuning.

**Implementation order inside Session 4**

1. Add or restore pre-commit guidance on the common opener attack path.
2. Reuse the existing tutorial/advisory surfaces instead of adding new UI.
3. Build a deterministic naive-vs-prepared comparison test.
4. Only if guidance still leaves the opener hopeless, apply narrow opener-specific tuning and capture it in tests.

---

### PL-29: No supported new-game / restart endpoint

**Problem statement**

The player still has no clean restart path from the running build. Starting fresh requires server restarts and sometimes manual autosave cleanup.

**Confirmed evidence**

- No formal `POST /new_game` implementation exists in the live backend route set.
- The client pause flow exposes save/load only.
- Existing tests already call `/new_game` indirectly without making it a real supported contract.

**Root-cause notes**

- The backend world is initialized at startup only; there is no reset helper and no restart endpoint.
- The frontend already has save/load wiring, but the pause menu and API client never expose a restart path.
- Local client reset logic already exists in the load flow and should be reused instead of inventing a second partial reset path.
- The test suite already assumes `/new_game` exists, so the current state is a direct contract contradiction rather than a speculative feature request.

**Exact code surfaces**

- `backend/main.py` - new-game endpoint wiring and world reset.
- `backend/save_manager.py` - explicit autosave reset/retention behavior.
- `godot-client/project-sovereign/scripts/api_client.gd` - client call.
- `godot-client/project-sovereign/scripts/pause_menu.gd` and `godot-client/project-sovereign/scripts/main.gd` - pause-menu button and UI refresh.

**Exact failure modes**

- Starting fresh requires a process restart and can inherit stale autosave state.
- Existing tests can call `/new_game` even though the route is not supported.
- Frontend local state such as pending popups, dialogue state, or cached world data can leak across a manual restart unless the reset path is centralized.

**Edge cases / sibling failure scan**

- Restart immediately after unsaved play.
- Restart after a manual save/load round trip.
- Restart while popups or dialogues are active.
- Manual saves must remain intact.
- Autosave from the previous campaign must not resurrect stale state after restart.

**State-transition risks**

- Resetting the world must also reset dialogue/mailbox state, notifications, eliminated nations, and any singleton references kept by `backend/main.py`.
- The client must clear local popup/dialogue caches before hydrating the fresh world response.
- Restart and load should share as much UI reset code as possible to avoid parallel bugs.

**Backend / frontend contract risks**

- `/new_game` should return the same kind of hydrated response shape the client already knows how to consume.
- Autosave behavior must be explicit. For the current fix phase, write a fresh autosave immediately after creating the new world so stale autosave state cannot be restored by accident.

**Acceptance criteria**

- `POST /new_game` returns a fresh world state without restarting the process.
- The fresh world is equivalent to a new campaign start: starting regions and marshals restored, `current_turn` reset, no pending diplomacy/dialogue carry-over, eliminated nations cleared.
- Autosave handling on new game is explicit and consistent, and stale autosave state cannot resurrect the previous campaign.
- The pause menu exposes restart/new game and returns the player to a fresh turn-one state.
- Manual saves are preserved.

**Regression test matrix**

- Add formal endpoint coverage in `tests/test_endpoint_wiring.py` or equivalent.
- Add save/load interaction coverage so new-game does not accidentally reload stale autosave state.
- Add a client smoke or manual verification for the pause-menu flow if no Godot harness exists.
- Update or retain the existing `/new_game`-using tests so they now exercise a supported contract instead of an accidental assumption.

**Dependencies / blockers**

- No upstream blocker.
- Keep last in the fix phase because it is QoL, not game-truth or contract-critical.

**Implementation order inside Session 5**

1. Extract a backend world-reset helper that can be used at startup and by `/new_game`.
2. Implement `POST /new_game` and return a fully hydrated fresh-world response.
3. Persist a fresh autosave immediately after reset.
4. Reuse the frontend load-reset path for new-game hydration, then expose the action in the pause menu.
5. Add endpoint, autosave, and pause-flow regression coverage.

---

## Open Judgment Points

- `PL-30`: the exact null object in the crash stack should still be confirmed if the repro is rerun, but the implementation should harden both wizard render paths now rather than waiting on another trace.
- `PL-26`: if pre-commit guidance plus prepared-line verification still leaves the opener reading as hopeless, approve the narrow numeric tuning inside this item; do not jump straight to broad combat rebalance.

---

## Fixed Bug Archive

28 bugs fixed across playtest Sessions 1-12 and Sessions A-C.

| ID | Summary | Fixed In |
|----|---------|----------|
| PL-1 to PL-4 | Early combat/display bugs | Sessions 1-6 |
| PL-5 | Proposal race condition plus no feedback popup | Sessions 7-8 |
| PL-6 | "Harsher" terms on friendship pacts demanded territory | Session 7 |
| PL-7 | Counter-offer accept/reject missing AI cooldowns | Session 7 |
| PL-8 | Counter-offer popup looked like an unsolicited AI proposal | Session 9 |
| PL-9 | Acceptance mismatch between display and resolution | Session 10 |
| PL-10 | "More generous" downgraded proposal type | Session 10 |
| PL-11 | Incoming AI proposals hijacked player diplomatic commands (API-only) | Session 10 |
| PL-12 | Harsher terms increased acceptance estimate | Session 11 |
| PL-13 | Viable proposal falsely rejected as surpassed | Session 11 |
| PL-14 | Ultimatum delivery reworked into a conversational diplomacy tool | Session 12 |
| PL-15 | Ultimatum demand wizard replaced blind escalation | Session A |
| PL-16 | Harsher-demand multiplier retuned | Session A |
| PL-17 | Manpower demand zero-penalty bug absorbed into PL-18 | Session A |
| PL-18 | Typed manpower demands plus `DEMAND_VALUES` key fixes | Session A |
| PL-19 | Dynamic ultimatum relation penalty | Session B |
| PL-20 | Territory cost scaling plus elimination guards | Session B |
| PL-21 | Phantom `connections` attribute | Fixed in code |
| PL-22 | Phantom `income` attribute | Fixed in code |
| PL-23 | Authority-driven pushback, pen nudge, trust removal | Session C |
| PL-24 | Harshness scoring for all demand types | Session C |
| PL-25 | Term novelty: jitter, personality nudge, desire bias, flavor | Session C |
