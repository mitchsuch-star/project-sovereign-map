# Diplomatic Offer Lifetime Refactor Spec

> **Status:** APPROVED - April 11, 2026
> **Phase:** Frozen bug-fix follow-up under `PL-27` / `PL-34`, before `PL-32`
> **Companion:** `docs/BUG_FIXES.md`, `docs/STATUS.md`
> **Purpose:** Replace the cross-turn diplomatic mailbox model with a current-turn offer model that is simpler, less gameable, and easier to explain to the player

---

## Executive Decision

Yes: this is a good refactor.

The current mailbox design is technically functional, but it is not elegant for this game. It creates three problems at once:

- unresolved AI offers can linger across turns
- `Ask Later` means persistence in some flows and simple dismissal in others
- the code says mailbox diplomacy is a soft-stop, but the diplomacy wizard still shuts off while any pending dialogue exists

The cleaner model is:

- AI diplomatic offers are **current-turn items**, not long-lived mailbox content
- `Ask Later` becomes **`Not Now`**
- `Not Now` closes the popup but keeps the offer reopenable until turn end
- unanswered offers **lapse automatically at end turn**
- diplomacy stays blocked **for that turn only** while unresolved offer items exist

This preserves the anti-exploit goal without requiring indefinite inbox persistence, stale-offer rules, or target-scoped invalidation logic.

---

## Why This Is Better

This model is better than the current persistent mailbox for the live game because it makes one clear promise:

- deal with the envoy now, or let the offer lapse at turn end

That is easier to understand than:

- some diplomacy waits forever in a mailbox
- some popups are just local planning
- some deferred items still block diplomacy
- some do not

It also avoids the obvious exploit where the player can freeze a favorable proposal while changing the board state.

This is still forgiving enough if the player can reopen the offer during the same turn. Without that same-turn reopen surface, `Not Now` would be too close to accidental rejection.

---

## Current Contradiction To Fix

The current implementation contains a live design contradiction:

- `DialogueManager` classifies `incoming_proposal`, `counter_offer`, `counter_offer_response`, and `conflict_alert` as mailbox soft-stops that do not block ordinary commands (note: this refactor reclassifies `conflict_alert` as local planning — see §7)
- `get_available_diplomatic_actions()` still returns no diplomacy actions whenever `pending_diplomatic_dialogue` exists at all
- mailbox items are exempt from generic stale clearing, so they can persist indefinitely

The result is a system that is neither a clean modal interruption nor a clean asynchronous inbox.

This refactor resolves that contradiction by making diplomatic offers:

- non-blocking for ordinary commands
- blocking for new diplomacy only
- reopenable during the current turn only
- automatically lapsed at turn end

---

## Final Player-Facing Rules

### 1. Offer Families

The following dialogue types become **current-turn diplomatic offers**:

- `incoming_proposal`
- `counter_offer`
- `counter_offer_response`

These are no longer treated as indefinite mailbox content.

`conflict_alert` is **not** in this bucket. It is a player-initiated safety gate ("you are about to violate a treaty"), not an AI-initiated envoy offer. Dismissing a conflict alert simply cancels the conflicting action. It belongs in the local planning family (§6), not the envoy tray.

### 2. `Not Now`

Replace `Ask Later` / `Later` with `Not Now` on AI-offer flows.

`Not Now` means:

- close the popup
- keep the item available in the envoy list for the rest of the turn
- do not auto-accept
- do not auto-reject
- do not clear the item immediately

### 3. Turn-End Lapse

At end turn, any unresolved current-turn diplomatic offer lapses automatically.

Lapse means:

- remove the offer from active dialogue / queue state
- clear any reopenable envoy-list entry for that item
- record a campaign-log line such as `Saxony's proposal lapsed unanswered`
- unblock diplomacy on the next turn

### 4. Diplomacy Blocking

While any unresolved current-turn diplomatic offer exists, the player **cannot initiate new diplomacy**.

That block applies to:

- diplomacy wizard actions
- diplomacy button / hotkey
- backend preview/action lists that would start a new diplomacy flow

That block does **not** apply to ordinary commands such as:

- `status`
- economy / treasury views
- military orders
- non-diplomatic read commands

### 5. End-Turn Confirmation

If the player issues `end turn` while unresolved current-turn diplomatic offers exist, the game must show a confirmation prompt before advancing:

> **You have N unanswered envoy(s) that will lapse. End turn anyway?**
> `[End Turn]` `[Review]`

- `End Turn` proceeds normally — offers lapse per §3
- `Review` cancels the end-turn and returns control so the player can reopen the envoy tray

This prevents accidental lapse. It is a soft gate, not a hard block — the player can always choose to let offers lapse deliberately.

Implementation: this is a client-side confirmation before the `/command` POST fires, not a backend blocking rule. The backend still processes end-turn unconditionally.

### 6. Reopen Surface

The player must be able to reopen unresolved current-turn offers before ending the turn.

The existing mailbox panel can be reused, but its meaning changes:

- it is a **current-turn envoy tray**, not a cross-turn archive
- it empties automatically at turn end for unanswered offer items

### 7. Planning vs Offer Separation

Player-planning dialogue types remain local and disposable:

- `proposal_confirm`
- `proposal_execute`
- `proposal_options`
- `pushback_confirm`
- `terms_guidance`
- `advisory`
- `mission`
- `ultimatum_*`
- `conflict_alert`

Closing these should clear them immediately. They do not belong in the envoy tray.

`conflict_alert` is listed here because it is a player-initiated safety gate, not an AI envoy. Dismissing it cancels the conflicting action with no lapse, no logging, and no envoy-tray entry.

### 8. Result Popups

`proposal_result` remains persistent until acknowledged. It is feedback, not pending diplomacy.

---

## UX Text Changes

Minimum required wording changes:

- replace `Ask Later` with `Not Now`
- replace `Mailbox` user-facing text with `Envoys` or `Pending Envoys`
- add helper copy on incoming-offer popups:
  - `This offer will lapse at end of turn.`
- add blocked-diplomacy reason text:
  - `An unanswered envoy awaits your reply.`

- add end-turn confirmation prompt:
  - `You have N unanswered envoy(s) that will lapse. End turn anyway?`

The important point is semantic clarity: this is a same-turn pending-offer system, not an inbox archive.

---

## Backend Behavior Contract

### Dialogue Taxonomy

Keep the hard-stop / hybrid / local-planning split, but change the meaning of the current mailbox bucket:

- current bucket becomes **current-turn diplomatic offers** (`incoming_proposal`, `counter_offer`, `counter_offer_response`)
- `conflict_alert` moves OUT of this bucket into local planning (see §7) — it is player-initiated, not an AI envoy
- they are not indefinite mailbox items
- they are exempt from ordinary-command blocking
- they are not exempt from turn-end cleanup

### Lifetime Rule

Current-turn diplomatic offers survive:

- local popup dismissal via `Not Now`
- ordinary command usage during the same turn
- reopening via the envoy tray

Current-turn diplomatic offers do not survive:

- turn advance without a reply
- world changes that explicitly void them

### Blocking Rule

`get_available_diplomatic_actions()` and any equivalent preview surface should block only when a relevant unresolved diplomacy item exists, not merely because any pending dialogue dict exists.

That block should key off:

- active current-turn diplomatic offer
- queued current-turn diplomatic offer
- active local planning flow already in progress
- true hard-stop dialogue

It should not be a blanket `pending_diplomatic_dialogue is not None` rule.

### Cleanup Rule

`clear_stale()` or a successor helper must change for current-turn offer items.

Current behavior:

- mailbox items never auto-expire (explicit exemption at `dialogue_manager.py` `clear_stale()`)

Target behavior:

- unresolved current-turn offer items lapse on end turn
- local planning popups still clear when dismissed
- hard-stop safety-valve behavior remains unchanged

The lapse must happen during end-turn processing, not during `clear_stale()` generic expiry. The cleanest hook point is inside `advance_turn()` in `world_state.py`, before the turn counter increments — call a dedicated `lapse_pending_offers()` on the dialogue manager that pops all current-turn offer types and returns them for campaign-log recording.

### Save/Load Migration

Old saves may contain persistent mailbox items with no turn boundary. On load:

- any dialogue items with types in the current-turn offer family should be treated as current-turn items for the loaded turn
- they follow the same lapse-on-end-turn rule as newly created offers
- no special migration field is needed — the type alone determines the lifetime rule

### Logging Rule

When an offer lapses, log it explicitly. Silent disappearance is not acceptable.

---

## Frontend Behavior Contract

### Offer Popup

Incoming-offer popups should show:

- `Accept`
- `Reject`
- `Counter`
- `Not Now`

`Not Now` closes the popup and returns control to the main screen.

### Envoy Tray

The current mailbox panel may remain as the reopen surface with lighter semantics:

- shows unresolved current-turn offer items only
- clears at turn end
- does not imply save/load permanence

If a visible rename is cheap, prefer `Envoys` over `Mailbox`.

### End-Turn Confirmation

Client-side gate per §5. Before sending the `end turn` command, check for pending current-turn diplomatic offers via the envoy count. If any exist, show a confirmation dialog:

- `[End Turn]` sends the command
- `[Review]` cancels and returns focus to the terminal

This is purely frontend — the backend processes end-turn unconditionally regardless.

### Diplomacy Button State

While unresolved current-turn offers exist:

- diplomacy button disabled
- tooltip / objection text points the player back to the envoy tray

When the turn advances and the offers lapse:

- diplomacy button re-enables automatically

---

## Exact Implementation Scope

Primary code surfaces:

- `backend/models/dialogue_manager.py`
- `backend/game_logic/diplomacy.py`
- `backend/main.py`
- `backend/game_logic/turn_manager.py`
- `backend/commands/diplomatic_executor.py`
- `godot-client/project-sovereign/scripts/main.gd`
- `godot-client/project-sovereign/scripts/incoming_proposal_popup.gd`
- `godot-client/project-sovereign/scripts/mailbox_panel.gd`
- `godot-client/project-sovereign/scripts/proposal_confirm_popup.gd`

Implementation notes:

- `conflict_alert` is currently created with `blocking=True` and classified as `SOFT_STOP_MAILBOX_TYPE`. Both must change: move it to local planning types and ensure dismiss clears it immediately.
- `get_available_diplomatic_actions()` in `diplomacy.py` currently blocks on `pending_diplomatic_dialogue is not None`. Must be narrowed to block only on current-turn offer types and hard-stop types.
- `ask_later` handler in `diplomatic_executor.py` currently relies on NOT popping the dialogue. `Not Now` can keep this mechanic — the item stays in the dialogue manager — but the mailbox exemption in `clear_stale()` must be removed so the item lapses at turn end.
- `/mailbox` and `/mailbox/activate` endpoints in `main.py` continue to work but now return only current-turn items. `/pending_envoy` recovery endpoint remains for popup re-display.

Primary test surfaces:

- `tests/test_mailbox_system.py`
- `tests/test_diplomacy_button.py`
- `tests/test_session2_bugfixes.py`
- `tests/test_session4_diplomacy.py`
- `tests/test_audit_session4.py`

---

## Acceptance Criteria

- unresolved `incoming_proposal` / `counter_offer` / `counter_offer_response` items can be dismissed with `Not Now` and reopened during the same turn
- those items automatically lapse on end turn if unanswered
- diplomacy initiation stays blocked while those unanswered items exist during the current turn
- ordinary non-diplomatic commands remain usable while those items are pending
- `end turn` with pending offers shows a confirmation prompt before advancing
- `conflict_alert` is treated as local planning — dismiss clears it, no envoy tray entry, no lapse log
- `proposal_confirm`-family planning popups are not stored as cross-turn envoy items
- `proposal_result` still persists until acknowledged
- the top-bar count and tray contents clear correctly after turn-end lapse
- lapse events are recorded instead of disappearing silently

---

## Out Of Scope

This refactor does not include:

- a broader diplomacy legitimacy redesign
- same-target invalidation rules for long-lived pending offers
- a general notification-system overhaul
- changes to `PL-32` display-label ownership beyond text needed for this refactor

Those concerns become less urgent once cross-turn offer persistence is removed.

---

## Recommended Implementation Order

1. Change the documented semantics first: current-turn envoy items, not persistent mailbox items.
2. Rework backend lifetime cleanup: add `lapse_pending_offers()` to dialogue manager, call from `advance_turn()`, remove mailbox exemption from `clear_stale()`.
3. Reclassify `conflict_alert` from `SOFT_STOP_MAILBOX_TYPES` to local planning. Remove `blocking=True` from its creation in `diplomatic_executor.py`.
4. Tighten diplomacy gating: `get_available_diplomatic_actions()` blocks on current-turn offer types and hard-stops only, not blanket `pending_diplomatic_dialogue`.
5. Rename the defer action to `Not Now` across the relevant popup paths.
6. Reuse the existing mailbox panel as the same-turn envoy tray and clear it automatically at turn end.
7. Add end-turn confirmation in Godot client: prompt when pending offers exist before sending end-turn command.
8. Add regression tests for same-turn reopen, end-turn lapse, diplomacy re-enable, conflict_alert dismiss, save/load migration, and campaign-log recording.
