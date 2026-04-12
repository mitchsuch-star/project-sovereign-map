# Informational UI Plan

> **Status:** APPROVED - April 11, 2026
> **Phase:** Immediate pre-`PL-32` UI follow-up
> **Companion:** `docs/STATUS.md`, `docs/BUG_FIXES.md`
> **Purpose:** Make informational feedback lighter, stop the notification rail from interfering with the top bar, and land a small polish pass before `PL-32`.

---

## Executive Decision

Yes: ship this next, before `PL-32`.

The current diplomacy transport layer is stable enough to start the display-contract work, but there is still avoidable frontend friction in the informational notice path:

- informational-only popups still hard-stop control
- notification `!` icons sit in the top bar path and get in the way of Envoys and other controls
- multiple surfaces warn about pending envoys but do not offer a direct recovery action
- the mailbox is functional but still harder to scan than it should be

This is a real usability pass, but it is not a new PL item. It stays deliberately narrow and should not expand into the broader popup-registry or response-pipeline work reserved for Sessions 6-8.

---

## Scope Guard

- No new PL item.
- No widening into popup queue architecture or registry cleanup.
- Reuse the existing backend-owned notification system for persistent informational notices. Do not create a second frontend-only notice cache or local notice store.
- No backend display-label ownership work beyond text needed for this pass.
- No new Godot-side proposal / clause / notice display maps. Reuse backend-provided labels, notification types, and mailbox summaries instead of adding more local formatting ownership ahead of `PL-32`.
- Keep true choice-driven diplomacy modal:
  - `incoming_proposal`
  - `counter_offer`
  - `counter_offer_response`
  - objections
  - clarification / interrupt flows
- Keep `conflict_alert` out of the Envoys tray / mailbox. It remains a local planning warning, not an AI envoy item.
- Restrict this pass to light presentation and interaction improvements that reduce friction on the current UI.

---

## Problems To Fix

### 1. Informational notices still behave like blocking decisions

`proposal_result_popup` and `coalition_declaration_popup` are informational. They report what happened; they do not ask the player to choose. Today they still take full modal focus and stop input.

This is most visible after enemy phase, where a proposal result can interrupt the return-to-play flow even though the same turn context is already available through dispatch and the campaign log.

### 2. Notification `!` icons are in the wrong place

The notification icons currently live inside the top bar's right section. That creates two UI problems:

- they compete directly with `Envoys`, DP, threat, and Talleyrand status for horizontal space
- the expanded notification drawer anchors to the top-right of the viewport instead of to the icon cluster, so it can sit on top of nearby controls instead of feeling attached to the thing the player clicked

This is the user's current pain point: the notice strip is physically in the way and does not read as a clean HUD surface.

### 3. Envoy recovery is explained, but not always actionable

The diplomacy wizard and dispatch view both tell the player an unanswered envoy is waiting, but neither surface gives them a direct `Open Envoys` action.

That creates an unnecessary loop:

- player is warned
- player closes the current surface
- player then has to go find the Envoys button manually

### 4. The mailbox is accurate but not easy to scan

The current mailbox panel renders one BBCode list of clickable rows. It works, but it does not do enough visually to separate:

- `ACTIVE` vs `WAITING`
- source nation
- item family
- short summary
- arrival turn

This is good enough for correctness, but not good enough for quick use when multiple diplomatic items are pending.

### 5. A few small HUD / log surfaces still feel cramped or underspecified

Low-risk polish opportunities remain:

- long Talleyrand mission summaries can crowd the top bar
- the campaign log headers do not clearly indicate expanded vs collapsed state
- the informational surfaces do not consistently route the player toward the next useful action

---

## Planned Fixes

### A. Downgrade informational-only diplomacy feedback from modal popup to persistent notice

Primary targets:

- `proposal_result`
- `coalition_declaration`

Direction:

- stop treating these as full blocking modals
- surface them through a lighter persistent notice path owned by the existing notification / notice system
- keep them visible / reviewable until acknowledged
- do not disable command input just because one of these notices appeared

Presentation target:

- compact notice card or drawer item tied to the notification / Imperial box rail
- click to expand detail
- explicit dismiss / acknowledge action

Contract rule:

- if a notice is informational only, it should not block control
- if a surface requires an actual decision, it remains modal
- if an informational notice is directly related to the blocking popup currently on screen, fold that information into the popup instead of spawning a separate rail item
- if an informational notice is unrelated to the current blocking popup, queue it into the Imperial box / notice rail and surface it after that popup is dismissed
- do not use this pass to invent a new popup-precedence registry; keep the rule explicit and narrow

### B. Move the notification interaction out of the top bar traffic lane

Direction:

- remove the interactive notice cluster from the top bar's right-section flow
- place it in a dedicated notice rail just below the top bar or otherwise outside the Envoys / DP / threat line
- anchor any expanded drawer to that rail, not to the viewport corner

Minimum behavior changes:

- the notice rail must not cover `Envoys` or top-bar buttons during ordinary use
- expanded notice details must appear attached to the notice rail
- clicks outside should still close the drawer cleanly
- the rail should cap or fold excess icons instead of stretching into other controls

Light semantic upgrade:

- improve icon meaning beyond plain `!!`, `!`, `i` by using the existing backend notification `type` / priority contract, not by inventing new frontend-owned proposal label maps
- preserve the existing priority model, but make the categories easier to distinguish at a glance

### C. Add direct `Open Envoys` recovery actions wherever the UI warns about pending envoys

Required surfaces:

- diplomacy wizard blocked state
- dispatch view when `pending_envoy_count > 0`
- end-turn confirmation continues to offer `Open Envoys`

Direction:

- warning copy should be paired with a direct recovery button
- if exactly one envoy is pending, direct reopen remains acceptable
- if 2+ are pending, route into the mailbox panel
- in the diplomacy wizard, `Open Envoys` closes the wizard first, then opens the envoy tray
- the end-turn warning should expose a real `Open Envoys` action, not only instructional copy telling the player to click elsewhere

### D. Rebuild the mailbox list as real rows instead of one BBCode block

Direction:

- replace the single clickable `RichTextLabel` list with actual row controls
- one row per item
- clear `ACTIVE` / `WAITING` badge
- source nation
- item type
- one-line summary
- arrival turn
- full-row click target

Behavior:

- selecting the active row reopens it
- selecting a waiting row activates and opens it
- empty state remains deterministic
- tray contents remain limited to current-turn AI offer items (`incoming_proposal`, `counter_offer`, `counter_offer_response`)
- `conflict_alert` remains outside this panel and continues to route through the local planning popup path
- use the backend-provided mailbox `summary` field for the one-line summary instead of adding new frontend summary formatting logic

This should stay inside the existing mailbox contract. Do not widen this into queue logic changes.

### E. Small polish pass on adjacent HUD / log surfaces

Ship if time permits inside the same session:

- truncate top-bar Talleyrand summary with tooltip instead of letting it sprawl
- keep Envoys visible and readable at common widths
- add simple expand / collapse affordance to campaign-log turn headers

These are intentionally low-risk and should not delay the higher-value notice / envoy fixes.

---

## Contract Clarifications

- `proposal_result` and `coalition_declaration` should persist via the existing backend notification / notice contract, with only the narrow payload support needed for richer rail rendering.
- The Imperial box / notice rail is the persistent home for unrelated informational notices in this pass.
- Related informational context may be folded into an already-open blocking popup instead of generating a separate simultaneous rail item.
- `conflict_alert` is a player-initiated warning about a diplomatically conflicting action. It is local planning, not an AI envoy, so it does not belong in the Envoys tray, does not lapse like an unanswered offer, and does not create mailbox count noise.
- This pass may reuse existing backend fields and notification `type` data, but it must not become a general popup-routing cleanup or a display-ownership rewrite ahead of `PL-32`.

---

## Exact Code Surfaces

Primary frontend files:

- `godot-client/project-sovereign/scripts/notification_bar.gd`
- `godot-client/project-sovereign/scenes/notification_bar.tscn`
- `godot-client/project-sovereign/scripts/top_bar.gd`
- `godot-client/project-sovereign/scenes/top_bar.tscn`
- `godot-client/project-sovereign/scripts/main.gd`
- `godot-client/project-sovereign/scripts/proposal_result_popup.gd`
- `godot-client/project-sovereign/scenes/proposal_result_popup.tscn`
- `godot-client/project-sovereign/scripts/coalition_declaration_popup.gd`
- `godot-client/project-sovereign/scripts/mailbox_panel.gd`
- `godot-client/project-sovereign/scenes/mailbox_panel.tscn`
- `godot-client/project-sovereign/scripts/diplomacy_wizard.gd`
- `godot-client/project-sovereign/scripts/dispatch_view.gd`
- `godot-client/project-sovereign/scripts/campaign_log.gd`

Possible light-touch backend support only if needed:

- response fields already used for proposal result / coalition notice payloads
- no broader response-builder or popup-queue refactor in this pass

---

## Implementation Order

### 1. Notification rail cleanup

Do this first because it fixes the user's current obstruction problem and gives the non-modal informational notices somewhere sane to live.

### 2. Proposal result notice conversion

This is the clearest win and the lowest-risk informational popup to downgrade.

### 3. Coalition declaration notice conversion

Use the same lighter notice path, but preserve stronger visual treatment than routine results.

### 4. Envoy recovery affordances

Add `Open Envoys` actions in the diplomacy wizard and dispatch view.

### 5. Mailbox readability pass

Convert the mailbox panel into real rows / cards.

### 6. Optional light polish

Top-bar truncation and campaign-log header affordances only if the core items above are already stable.

---

## Exit Criteria

- Informational diplomacy notices no longer hard-stop control unnecessarily.
- Notification `!` interactions no longer sit on top of the top bar / Envoys path.
- Expanded notice details feel attached to the notice rail, not detached from it.
- The diplomacy wizard and dispatch view can route the player directly to Envoys.
- The mailbox is faster to scan with 2+ pending items.
- `PL-32` remains untouched as backend-owned display-contract work, ready to resume immediately after this pass.

---

## Verification

Manual verification is the primary check for this session.

Required manual checks:

1. Trigger a proposal result after enemy phase and confirm the result is visible without blocking input.
2. Trigger a coalition declaration and confirm it uses the lighter notice path rather than a stop-everything modal.
3. Open the notification drawer and confirm it does not cover the Envoys button or top-bar controls.
4. Trigger pending envoys, open the diplomacy wizard, and confirm the warning includes an actionable `Open Envoys` path.
5. Open dispatch with pending envoys and confirm the same recovery affordance exists there.
6. Populate the mailbox with 2+ items and confirm the player can identify and select the intended row quickly.
7. Trigger a blocking popup plus related informational context and confirm the context is folded into that popup rather than surfacing as a second simultaneous rail item.
8. Trigger an unrelated informational notice while a blocking popup is active and confirm it appears in the Imperial box / notice rail only after the blocker is dismissed.
9. Confirm `conflict_alert` still routes through the local planning popup path and does not appear in Envoys / mailbox count.
10. Confirm real choice-driven popups still remain modal.

Light automated coverage is acceptable where UI helpers can be tested cheaply, but this session should not stall on building new test harnesses.
