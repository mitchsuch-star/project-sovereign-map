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
- `/diplomatic_preview` and the diplomacy wizard still treat any pending dialogue as a blanket stop
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
- record a campaign-log line such as `Saxony's alliance offer lapsed unanswered`
- surface the lapse in the next turn-start report / summary so the player sees what was forfeited
- by default, apply no automatic trust / relation penalty beyond the lost opportunity itself
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

> **Are you sure? You have N unanswered envoy(s) that will lapse if you end the turn now.**
> `[End Turn]` `[Open Envoys]`

- `End Turn` proceeds normally — offers lapse per §3
- `Open Envoys` cancels the end-turn and opens the envoy tray immediately

`[Review]` is an acceptable fallback label if opening the tray directly is awkward in Godot, but direct tray-open is preferred.

This prevents accidental lapse. It is a soft gate, not a hard block — the player can always choose to let offers lapse deliberately.

Implementation: this confirmation must cover all player-facing end-turn entry points: button click, hotkey, and typed `end turn`. The backend should still permit end turn when only current-turn offers are pending; only true hard-stop dialogues should block end turn server-side.

Design note: the perceived quality of this warning depends heavily on AI proposal frequency. If AI offers occur on too many turns, the warning becomes click-through tax instead of a safety net. Proposal frequency should be tuned before adding more confirmation friction.

### 6. Reopen Surface

The player must be able to reopen unresolved current-turn offers before ending the turn.

The existing mailbox panel can be reused, but its meaning changes:

- it is a **current-turn envoy tray**, not a cross-turn archive
- it empties automatically at turn end for unanswered offer items
- when exactly one offer is pending, the reopen interaction should be as lightweight as possible (direct reopen is preferred over forcing a full tray view)
- when two or more offers are pending, the full tray / list view is appropriate

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
  - for counter-chain replies: `Austria has responded to your proposal. This response will lapse at end of turn.`
- add blocked-diplomacy reason text:
  - `An unanswered envoy awaits your reply.`

- add end-turn confirmation prompt:
  - `Are you sure? You have N unanswered envoy(s) that will lapse if you end the turn now.`
  - preferred secondary button text: `Open Envoys`
- add next-turn lapse summary copy:
  - `The following envoy offers lapsed unanswered last turn: Saxony alliance offer, Bavaria trade offer.`

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

Default consequence rule:

- lapse means missed opportunity and visible feedback, not a hidden trust / relation penalty
- any future "ignoring an envoy is a diplomatic slight" system is outside this refactor

### Blocking Rule

`get_available_diplomatic_actions()` and any equivalent preview surface should block only when a relevant unresolved diplomacy item exists, not merely because any pending dialogue dict exists.

That block should key off:

- active current-turn diplomatic offer
- queued current-turn diplomatic offer
- active local planning flow already in progress
- true hard-stop dialogue

It should not be a blanket `pending_diplomatic_dialogue is not None` rule.

This same predicate must drive:

- diplomacy wizard nation list / preview surfaces
- diplomacy button and hotkey enablement
- backend preview APIs
- any non-diplomatic command guards that currently key off any pending dialogue

### Cleanup Rule

`clear_stale()` and a successor helper must split responsibilities cleanly.

Current behavior:

- mailbox items never auto-expire (explicit exemption at `dialogue_manager.py` `clear_stale()`)

Target behavior:

- unresolved current-turn offer items lapse on end turn
- local planning popups still clear when dismissed
- hard-stop safety-valve behavior remains unchanged

The lapse must happen during end-turn processing, not during `clear_stale()` generic expiry. The preferred hook point is at the start of `TurnManager.end_turn()`, before enemy phase, AI diplomacy, or turn-counter advance. Call a dedicated `lapse_pending_offers()` on the dialogue manager there, use its return value for campaign-log recording, and clear any paired incoming-popup cache at the same time.

`clear_stale()` should remain responsible for generic cleanup only:

- local-planning dismissal rules
- non-offer non-blocking stale cleanup
- hard-stop safety-valve timeout

### Save/Load Migration

Old saves may contain persistent mailbox items with no turn boundary. On load:

- any dialogue items with types in the current-turn offer family should be treated as current-turn items for the loaded turn
- normalize their `turn_created` to the loaded turn so the tray shows them as current-turn arrivals
- normalize their old mailbox-era blocking semantics so they no longer hard-block end turn or ordinary commands
- they follow the same lapse-on-end-turn rule as newly created offers
- no special migration field is needed — the type alone determines the lifetime rule

Legacy `conflict_alert` mailbox items should not survive as envoy-tray content. They should either be discarded on load or converted into local planning state if that is trivial and safe.

### Logging Rule

When an offer lapses, log it explicitly. Silent disappearance is not acceptable.

Minimum visibility requirement:

- record each lapsed offer in campaign / diplomatic history
- also surface the lapsed offers in the next turn-start report, summary, or equivalent turn-opening notification

If multiple offers lapse together, the summary should list each nation and offer type clearly enough that the player understands what opportunities were lost.

---

## Frontend Behavior Contract

### Offer Popup

Incoming-offer popups should show:

- `Accept`
- `Reject`
- `Counter`
- `Not Now`

`Not Now` closes the popup and returns control to the main screen.

Counter-chain responses should restate the lifetime rule explicitly so the player does not assume a fresh full-turn grace period just because they initiated the negotiation.

### Envoy Tray

The current mailbox panel may remain as the reopen surface with lighter semantics:

- shows unresolved current-turn offer items only
- clears at turn end
- does not imply save/load permanence
- should behave like a lightweight reopen button in the common one-offer case
- should expand into a browsable list only when multiple offers are pending

If a visible rename is cheap, prefer `Envoys` over `Mailbox`.

### End-Turn Confirmation

Client-side gate per §5. Before sending the `end turn` command, check for pending current-turn diplomatic offers via the envoy count. If any exist, show a confirmation dialog:

- `[End Turn]` sends the command
- `[Open Envoys]` cancels and opens the envoy tray
- `[Review]` may be used only as a fallback label if direct tray-open is awkward

The copy should read as a clear lapse warning, not a generic confirmation. It should explicitly tell the player that the unanswered offers will be lost if they proceed.

This must apply consistently to:

- end-turn button
- end-turn hotkey
- typed `end turn`

The backend must not independently hard-block end turn for current-turn offer types.

### Diplomacy Button State

While unresolved current-turn offers exist:

- diplomacy button disabled
- tooltip / objection text points the player back to the envoy tray

When the turn advances and the offers lapse:

- diplomacy button re-enables automatically

### Turn-Start Report

If one or more offers lapsed because the player ended the turn, the next turn's opening report / summary should call that out explicitly.

- this is in addition to campaign-log history, not a replacement for it
- if only one offer lapsed, a single concise line naming the nation and offer type is enough
- if multiple offers lapsed, summarize them as a short list

---

## Exact Implementation Scope

Primary code surfaces:

- `backend/models/dialogue_manager.py`
- `backend/game_logic/diplomacy.py`
- `backend/main.py`
- `backend/game_logic/turn_manager.py`
- `backend/commands/meta_executor.py`
- `backend/commands/diplomatic_executor.py`
- `godot-client/project-sovereign/scripts/main.gd`
- `godot-client/project-sovereign/scripts/diplomacy_wizard.gd`
- `godot-client/project-sovereign/scripts/incoming_proposal_popup.gd`
- `godot-client/project-sovereign/scripts/mailbox_panel.gd`
- `godot-client/project-sovereign/scripts/proposal_confirm_popup.gd`
- `godot-client/project-sovereign/scripts/top_bar.gd`

Secondary but real surfaces:

- `backend/game_logic/diplomatic_ledger.py`
- `godot-client/project-sovereign/scripts/diplomatic_ledger.gd`

Implementation notes:

- `conflict_alert` is currently created with `blocking=True` and classified as `SOFT_STOP_MAILBOX_TYPE`. Both must change: move it to local planning types and ensure dismiss clears it immediately.
- `get_available_diplomatic_actions()` in `diplomacy.py` currently blocks on `pending_diplomatic_dialogue is not None`. `/diplomatic_preview` and `diplomacy_wizard.gd` also use blanket `dialogue_pending` checks. All must be narrowed together behind one shared rule.
- `ask_later` handler in `diplomatic_executor.py` currently relies on NOT popping the dialogue. `Not Now` can keep this mechanic — the item stays in the dialogue manager until end-turn lapse.
- `/mailbox` and `/mailbox/activate` endpoints in `main.py` continue to work but now return only current-turn items. `/pending_envoy` recovery endpoint remains for popup re-display.
- `meta_executor._execute_end_turn()` currently blocks on any pending dialogue with `blocking=True`. That must be narrowed so current-turn offers do not backend-block end turn.
- `WorldState.from_dict()` / `DialogueManager.from_dict()` need explicit load normalization for current-turn offer types; type-only classification is not enough if old saves preserve stale `turn_created` and `blocking` values.
- `/cancel_order` and any similar non-diplomatic command guards must stop keying off any pending dialogue if the active item is only a current-turn offer.
- end-turn lapse handling should retain enough structured info to populate the next turn-start report, not just the long-term history log.
- common-case one-offer reopen UX should not force unnecessary tray navigation if the same direct-reopen behavior can be delivered more simply.

Primary test surfaces:

- `tests/test_mailbox_system.py`
- `tests/test_diplomacy_button.py`
- `tests/test_session2_bugfixes.py`
- `tests/test_session4_diplomacy.py`
- `tests/test_audit_session4.py`

Additional likely break surfaces:

- `tests/test_dialogue_manager.py`
- `tests/test_systems_v3_session6.py`
- `tests/test_audit_part1.py`

---

## Acceptance Criteria

- unresolved `incoming_proposal` / `counter_offer` / `counter_offer_response` items can be dismissed with `Not Now` and reopened during the same turn
- those items automatically lapse on end turn if unanswered
- diplomacy initiation stays blocked while those unanswered items exist during the current turn
- diplomacy wizard, backend preview, diplomacy button, and diplomacy hotkey all use the same narrowed block rule
- ordinary non-diplomatic commands remain usable while those items are pending
- `end turn` with pending offers shows a confirmation prompt before advancing on button, hotkey, and typed-command paths
- the confirmation copy explicitly warns that the offers will lapse if the player proceeds
- the spec explicitly treats proposal frequency as a tuning dependency for the warning's UX quality
- backend end turn is not hard-blocked by current-turn offers; only true hard-stop dialogues still block it
- `conflict_alert` is treated as local planning — dismiss clears it, no envoy tray entry, no lapse log
- `/pending_envoy`, `/mailbox`, tray count, and ledger pending-envoy count exclude `conflict_alert`
- `proposal_confirm`-family planning popups are not stored as cross-turn envoy items
- `proposal_result` still persists until acknowledged
- the top-bar count and tray contents clear correctly after turn-end lapse
- single-offer reopen remains lightweight, while multi-offer turns still have a browsable tray
- counter-chain responses explicitly warn that they lapse at end of turn
- loaded saves normalize current-turn offer items to the loaded turn and do not preserve old hard-block semantics
- lapse events are recorded instead of disappearing silently
- the next turn-start report / summary tells the player exactly which nation + offer type lapsed
- unanswered-offer lapse has no hidden trust / relation penalty in this refactor

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
2. Rework backend lifetime cleanup: add `lapse_pending_offers()` to dialogue manager and call it from `TurnManager.end_turn()` before enemy phase / AI diplomacy. Keep `clear_stale()` focused on generic local-planning cleanup and hard-stop timeout behavior.
3. Reclassify `conflict_alert` from `SOFT_STOP_MAILBOX_TYPES` to local planning. Remove `blocking=True` from its creation in `diplomatic_executor.py`.
4. Tighten diplomacy gating: `get_available_diplomatic_actions()`, preview APIs, wizard gating, and diplomacy-button state all block on current-turn offer types and true hard-stops only, not blanket `pending_diplomatic_dialogue`.
5. Rename the defer action to `Not Now` across the relevant popup paths.
6. Reuse the existing mailbox panel as the same-turn envoy tray and clear it automatically at turn end.
7. Add end-turn confirmation in Godot client for button, hotkey, and typed-command paths, and narrow backend end-turn blocking so current-turn offers do not stop it.
8. Add regression tests for same-turn reopen, end-turn lapse, diplomacy re-enable, conflict_alert dismiss, save/load migration, and campaign-log recording.
