# Settlement UI Cleanup Spec

> **QUALITY BAR:** This feature must work as a player-usable settlement system. No handwaving, no "wired but not usable" completion, and no deferring visible broken or misleading behavior without explicit product approval. Quality always beats schedule.

> **Status:** v0.1 draft - cleanup gate before further settlement coding
> **Owner:** Project Sovereign / Ink & Iron settlement feature
> **Created:** May 5, 2026

## Purpose

The Imperial Settlement / Common Peace feature reached normal UI paths, but the Slice F closeout exposed a product-quality gap: some settlement controls are technically wired while not delivering the player action their labels promise. This spec is a cleanup gate before Slice G or any broader settlement agency work.

The opening blocker is `Revise Terms`: the button currently routes through typed dialogue plumbing and reopens the same review, but it does not open an editor or change the draft package. A player-facing `Revise Terms` action that cannot revise terms is not complete.

This spec exists to find and close every adjacent gap of the same class. The desired end state is not a technically reachable popup; it is a settlement flow a player can use, understand, revise where promised, and trust.

- Button exists, but does not perform the player-visible action.
- UI path exists, but falls back to typed command text, generic mailbox text, or nation-picker recovery.
- Payload fields exist, but player surfaces still omit the reason, beneficiary, ignored party, stale-state cause, or remaining-war context.
- Tests assert source strings or schema fragments while missing the behavior a player actually uses.

## Non-Negotiable Rule

No settlement UI slice is complete because a route exists. It is complete only when the player-facing surface does the named action, shows the necessary state to understand the outcome, and has behavioral coverage that would fail if the action became a no-op.

Deferral policy:

- A visible broken or misleading settlement behavior cannot be deferred silently.
- A defer decision must name the player impact, hide or remove the broken affordance when possible, and be explicitly accepted in status/spec text before coding proceeds.
- If there is a conflict between finishing quickly and making the settlement feature actually usable, choose quality.

## Scope

Included:

- `settlement_confirm` actions and presentation.
- Common-peace entry from diplomacy wizard, war detail, coalition detail, notification rail, dispatch, and ledger.
- Incoming AI settlement-offer review and response actions.
- Settlement stale-state recovery, route focus, and result feedback.
- One-to-one war settlement affordances versus bilateral peace / armistice.
- Tests that claim UI routing or button behavior is covered.

Excluded:

- Full Slice G AI treaty authorship, ally petitions, conference mechanics, or veto systems.
- New settlement term economics unless needed to make an existing button truthful.
- Broad redesign of the diplomacy wizard outside settlement actions.

## Cleanup Audit Questions

Run these before coding:

1. Does every visible settlement button have a concrete player-visible effect?
2. Does the label match the effect? If not, should the button be renamed, hidden, or implemented?
3. Can any settlement action still synthesize or drop text into the Imperial command box?
4. Can any settlement action fall back to a generic nation picker, generic mailbox, or generic proposal popup?
5. Can a stale popup or stale mailbox offer mutate current state without live revalidation?
6. Can route recovery lose `war_id`, `route_id`, active nation, or popup target?
7. Are one-to-one wars shown common-peace controls anywhere instead of bilateral peace / armistice controls?
8. Do notification, dispatch, and ledger focus routes open the exact settlement row or war context the player clicked?
9. Does `settlement_confirm` explain who benefits, who is ignored, who remains at war, and why acceptance succeeds or fails?
10. Are disabled reasons, warning labels, standing labels, awe tags, acceptance bands, and route names humanized on every player surface?
11. Do tests execute behavior, or merely check that strings appear in source files?
12. Would a Godot script parse/load failure or disconnected signal fail CI before manual smoke?

## Known Blocker: Revise Terms

Current behavior:

- `revise_settlement_terms` returns a typed backend response with `must_reopen=True`, `reopen_target`, unchanged `settlement_terms`, and `mutated=False`.
- Godot now avoids command-box fallback and reopens the settlement review.
- No term editor, draft-package builder, or term mutation surface is opened.

Required cleanup decision:

- Either implement a real term revision flow, or remove/hide the button until such a flow exists.
- Renaming to `Review Again` is acceptable only if the action remains a review-only loop and the product wants that loop.
- Keeping the label `Revise Terms` without an editor fails this spec.

Minimum acceptable fix:

- `settlement_confirm` must not expose `Revise Terms` unless the payload declares an actual editable draft flow, such as `can_edit_terms=true` plus a concrete route target.
- Tests must fail if `Revise Terms` appears without an edit-capable route.

Full fix:

- Add a settlement draft editor reachable from `settlement_confirm`.
- Preserve `war_id`, accepting leader, proposer side, covered enemies, draft terms, and route metadata.
- Re-preview acceptance and warnings after draft changes before ratification.
- Confirm still revalidates live state and never mutates from stale preview data.

## Gap Inventory

Fill this before implementation. Every row needs a decision: fix now, remove/rename now, or explicitly defer with the button hidden.

| ID | Surface | Suspected Gap | Required Decision | Coverage Required |
| --- | --- | --- | --- | --- |
| SC-1 | `settlement_confirm` | `Revise Terms` does not revise terms | Remove/hide, rename, or implement editor | Behavioral test proving no false `Revise Terms` affordance |
| SC-2 | Diplomacy wizard | `Open Settlement` must preserve `war_id` and never compile-fail from stray GDScript | Keep wired and parse-guarded | Godot parse/load or executable harness guard |
| SC-3 | War detail | Common-peace button must appear only for multi-party war contexts | Keep hidden for one-to-one wars | Backend eligibility plus Godot source/behavior guard |
| SC-4 | Coalition detail | Whole-war/separate-front context must not be inferred from names when `war_id` exists | Keep explicit route | Behavior test for same-nations multiple-war contexts |
| SC-5 | Notification/dispatch/ledger | Route focus must preserve `route_id` and `war_id` through result feedback | Keep exact focus | Behavioral payload test and Godot route guard |
| SC-6 | Incoming AI offer | Accept/reject/request revision must not use stale mailbox payload or generic fallback | Live revalidate or visible stale error | Backend dialogue-manager behavior test |
| SC-7 | Result popup | Player must know what changed and what remains unresolved | Keep named summary | Presentation test for resolved/unresolved pairs |
| SC-8 | Raw labels | No raw enum leakage on player settlement surfaces | Keep humanized | Raw-enum scan plus behavior fixture |

Add rows as audit discovers more.

## Implementation Gates

### Gate 1 - Spec Completion

Before code:

- Complete the gap inventory above with every discovered settlement UI no-op or misleading affordance.
- Decide for each gap whether the immediate cleanup is implement, hide, remove, or rename.
- Update `docs/STATUS.md` so the next settlement step is this cleanup spec, not Slice G.

### Gate 2 - Minimal Cleanup Patch

Required fixes:

- Close SC-1 so `Revise Terms` is no longer a false promise.
- Ensure no settlement action can fall back to command-box text.
- Ensure one-to-one wars do not show common-peace affordances from any normal UI path.
- Add at least one behavioral test that would have caught the prior `Revise Terms` no-op.

### Gate 3 - Behavioral Coverage Upgrade

Required tests:

- Backend behavior tests for every settlement dialogue action.
- Godot source guards only as supplements, not as the primary proof of behavior.
- A Godot parse/load or executable harness for touched settlement scripts, if available in the repo toolchain.
- Same-nation multi-war route test proving `war_id` disambiguates the selected war.
- Incoming offer stale-state test proving accept promotes through live settlement preview or returns a visible stale error.

### Gate 4 - Manual Smoke

Manual smoke cannot pass until Gate 2 and Gate 3 are green.

Smoke script:

1. Open a multi-party war settlement from the diplomacy wizard. Confirm that no command-box text is generated by settlement buttons.
2. Open the same war from war detail. Confirm the same `war_id` is staged.
3. Open a coalition-detail settlement. Confirm whole-war versus separate-front language is visible.
4. Open a one-to-one war. Confirm common-peace controls are absent and bilateral peace / armistice remains the relevant path.
5. Open `settlement_confirm`. Confirm every visible action either performs the named action or is absent.
6. Trigger stale state before confirm. Confirm the popup shows a humanized stale reason and routes back to the same war context.
7. Trigger incoming settlement offer handling if feasible. Confirm accept/reject/request revision avoid generic mailbox fallback.
8. Ratify a settlement. Confirm result feedback, notification, dispatch, and ledger all focus the same settlement route.

## Completion Criteria

This spec is complete only when:

- No visible settlement button is a no-op or misleading label.
- Common peace is absent from one-to-one war surfaces.
- Settlement UI actions cannot fall back to natural-language command text.
- `route_id` and `war_id` survive confirmation, result feedback, notification, dispatch, and ledger focus.
- Incoming settlement offers are safe against stale state and wrong-popup fallback.
- `settlement_confirm` explains beneficiaries, ignored parties, unresolved wars, acceptance blockers, and hard stops.
- Tests include behavior-level coverage for the player paths that regressed.
- `docs/STATUS.md` records the cleanup as complete and only then reopens Slice G / later settlement agency work.
