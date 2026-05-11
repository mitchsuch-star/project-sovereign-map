# Settlement UI Cleanup Spec

> **QUALITY BAR:** This feature must work as a player-usable settlement system. No handwaving, no "wired but not usable" completion, and no deferring visible broken or misleading behavior without explicit product approval. Quality always beats schedule.

> **Status:** v0.22 SPEC READINESS NO-GO / IMPLEMENTATION NO-GO - Codex + Claude settlement UX review incorporated, and the re-audit fixes are folded in: blocked Ratify remains absent rather than disabled; direct armistice/enemy-offer substitutes remain hidden only while their concrete landing rows SC-29 / SC-30 / SC-31 / SC-32 remain unshipped; valid below-threshold drafts may Submit into blocked REVIEW but cannot Ratify; scoped draft keys use a stable cross-runtime hash contract; review payloads require concrete player-comprehension sections; parent incoming-offer smoke wording is superseded; Slice 0 comes before Foundation; branch reconciliation, recorded review traceability, SC-27 scan, and Gate 4 smoke remain required
> **Owner:** Project Sovereign / Ink & Iron settlement feature
> **Created:** May 5, 2026
> **Last spec update:** May 8, 2026

## Purpose

The Imperial Settlement / Common Peace feature reached normal UI paths, but the Slice F closeout exposed a product-quality gap: some settlement controls are technically wired while not delivering the player action their labels promise. This spec is a cleanup gate before Slice G or any broader settlement agency work.

The opening blocker is `Revise Terms`: the button currently routes through typed dialogue plumbing and reopens the same review, but it does not open an editor or change the draft package. A player-facing `Revise Terms` action that cannot revise terms is not complete.

The broader blocker is now explicit: the common-peace UI currently behaves like a one-button white-peace lever while displaying settlement, terms, acceptance, pressure, and revision affordances that imply a richer treaty system. The approved product direction is the full treaty-settlement path: the player must be able to author, preview, negotiate/revise, and ratify concrete treaty terms. Temporary hiding/removal is still allowed to protect the player from broken affordances while this is implemented, but the cleanup target is not a permanent white-peace rebrand.

This spec exists to find and close every adjacent gap of the same class. The desired end state is not a technically reachable popup; it is a settlement flow a player can use, understand, revise where promised, be refused when acceptance fails, and trust.

- Button exists, but does not perform the player-visible action.
- UI path exists, but falls back to typed command text, generic mailbox text, or nation-picker recovery.
- Payload fields exist, but player surfaces still omit the reason, beneficiary, ignored party, stale-state cause, or remaining-war context.
- Tests assert source strings or schema fragments while missing the behavior a player actually uses.

## Non-Negotiable Rule

No settlement UI slice is complete because a route exists. It is complete only when the player-facing surface does the named action, shows the necessary state to understand the outcome, and has behavioral coverage that would fail if the action became a no-op.

Settlement ratification must respect the same acceptance verdict and hard stops the review surface advertises. A popup that displays `Acceptance: 12 / 50 - Unlikely` or a red `HARD_STOP` warning and then ratifies anyway fails this spec unless the product explicitly rebrands the feature as a non-consensual diktat and removes misleading acceptance language.

Common peace must not pretend to be a treaty-settlement system while only supporting an empty/no-clause package. The approved target is real treaty authoring: draft clauses, preview acceptance and political consequences, revise/counter terms, preserve incoming-offer packages, and revalidate before mutation. Until those parts are implemented, incomplete controls must be hidden or omitted rather than shipped as visible promises. Disabled placeholder buttons for unavailable settlement systems are forbidden because they still read like promised player agency.

Deferral policy:

- A visible broken or misleading settlement behavior cannot be deferred silently.
- A defer decision must name the player impact, hide or remove the broken affordance when possible, and be explicitly accepted in status/spec text before coding proceeds.
- Every interim hide must record four artifacts before code starts: owning SC row, restoring implementation slice, `docs/STATUS.md` tracking line, and a CI/test gate that fails if the owning slice closes while the affordance remains hidden.
- No deferred settlement affordance may point at an unnamed row or vague backlog. It must appear in the Deferred Work Landing Ledger below with an owning SC row, a landing slice, a completion definition, and at least one behavior test that fails if the landing slice closes while the work is still absent.
- The landing ledger is not a waiver. It is the backlog contract for player-facing work that is hidden during cleanup. A ledger item can leave the backlog only by shipping the named behavior and tests, or by a recorded product decision in this spec and `docs/STATUS.md` that removes the player-facing promise from the game entirely.
- If there is a conflict between finishing quickly and making the settlement feature actually usable, choose quality.

### Deferred Work Landing Ledger

This ledger is mandatory for every hidden settlement affordance. The cleanup slices may hide these controls to avoid false promises, but the work is not unowned or open-ended.

| Hidden / deferred player-facing work | Why hidden during cleanup | Owning row | Landing slice | Work that must land | Required tests / smoke |
| --- | --- | --- | --- | --- | --- |
| Direct rejected-popup pair actions: `Seek Armistice Instead`, `Seek Bilateral Peace`, and settlement-family wrappers around `propose_armistice` / `propose_peace` | The rejected settlement popup is war-scoped, while armistice and bilateral peace are pair-scoped; exposing these now would lack target scope, eligibility, handoff, collision, and draft-invalidation rules. | SC-29 | G2-Slice-7 - Pair-Scoped Peace Substitute CTAs | Selected-pair scope, payload `{action, war_id, selected_target_nation, scope="selected_pair"}`, shared eligibility helper, War Detail / popup handoff, SC-13 selected-target inheritance, SC-14b no-reopen-attempt consumption, SC-26 collision behavior, draft stale/invalidation rules, and SC-19 voice copy. | `test_seek_armistice_instead_creates_per_pair_armistice_with_selected_target_only`, `test_seek_bilateral_peace_instead_creates_per_pair_peace_with_selected_target_only`, `test_pair_substitute_eligibility_helper_matches_backend_refusal_codes`, `test_pair_substitute_handoff_preserves_or_invalidates_scoped_draft_correctly`. |
| Enemy-offer waiting and request-terms actions: `Wait for Enemy Offer`, `Ask for terms`, current-turn incoming settlement offer UI, and request-revision/counteroffer flow | A wait/request label promises an AI offer producer and mailbox/pending-envoy lifecycle that cleanup does not currently ship. | SC-30 | Slice G1 - AI Settlement Offer Producer And Request Terms | Gameplay AI offer producer, cooldowns, one-active-offer gate, mailbox and pending-envoy payloads, stable offer identity, incoming voice, accept/reject/request-revision handlers, package preservation through live preview, request-terms action that creates a real AI response path or humanized refusal, and no generic offer fallback. | `test_ai_settlement_offer_producer_surfaces_real_mailbox_payload`, `test_wait_for_enemy_offer_only_visible_when_offer_producer_and_cooldown_path_exist`, `test_ask_for_terms_creates_request_terms_state_or_humanized_refusal`, `test_incoming_offer_accept_preserves_offer_identity_and_terms_through_live_preview`. |
| `Surrender terms` and dependency surrender presets | Surrender copy implies vassalage/subjugation or equivalent dependency consequences, preview, mutation, voice, and aftermath. Cleanup-scope concessions use gold/territory/peace only. | SC-31 | G2-Slice-8 - Dependency And Surrender Terms Restoration | Live `vassalage` / `subjugation` / liberation dependency clauses where supported, losing-side surrender preset, preview of dependency consequences, ratification mutation, history/dispatch/ledger copy, AI acceptance impact, and surrender-specific Talleyrand / foreign-court voice. | `test_surrender_terms_absent_until_dependency_clause_restoration`, then `test_surrender_terms_authors_dependency_clause_with_preview_and_mutation`, `test_surrender_terms_voice_and_history_explain_dependency_consequence`. |
| Two-way negotiation, AI counter-proposals, ally petitions/advisories, conference mechanics, and any veto-like settlement agency | These are broader settlement-agency systems, not cleanup controls, but they must not stay as vague "later" prose. | SC-32 | Slice G2 - Settlement Agency Follow-Through | Concrete AI counterproposal loop or explicit no-counterproposal product decision, ally petition/advisory actions with no veto unless deliberately implemented, conference/veto decision recorded, payloads, cooldowns, voice, notification/mailbox routes, and behavior tests. | `test_settlement_agency_landing_ledger_has_no_unowned_future_controls`, plus per-action behavior tests before any agency CTA appears. |
| `gold_per_turn` recurring-indemnity clause | Canonical in the Settlement Clause Schema (`type`, `from`, `to`, `amount`, `turns`) and in the SC-1 editor vocabulary, but outside the G2-Slice-1 required first-slice floor (`peace` / `territory_cede` / `gold_indemnity` / `forced_alliance`). Interim-hide artifacts: structured editor control disabled, `gold_per_turn` removed from `available_clause_types[]` in POST preview responses, presets/quick-clause helpers do not advertise it, and CI guard rejects any UI label that exposes it before this row ships. | SC-33 | G2-Slice-9 - Recurring Indemnity Clause Landing | Structured editor control (payer/recipient pickers, integer amount `1..payer current gold`, integer turn count), POST preview validation matching the canonical schema, ratification mutation (per-turn gold transfer with payer-balance clamp and breach handling on default), `applied_clauses_preview[]` row shape (`amount`, `turns`), dispatch/ledger/notification copy, AI acceptance impact, Voice Bible §16.1 line if a new voice family is required, and discard/cleanup of the cap once breached. | `test_gold_per_turn_clause_authors_with_amount_and_turns`, `test_gold_per_turn_preview_acceptance_reflects_total_burden`, `test_gold_per_turn_ratification_transfers_first_payment_and_records_recurring_obligation`, `test_gold_per_turn_default_handles_payer_insolvency_humanized`, `test_gold_per_turn_hidden_with_interim_artifacts_until_slice_lands`. |

## Scope

Included:

- `settlement_confirm` actions and presentation.
- Common-peace entry from diplomacy wizard, war detail, coalition detail, notification rail, dispatch, and ledger.
- Incoming AI settlement-offer review and response actions.
- Settlement stale-state recovery, route focus, and result feedback.
- One-to-one war settlement affordances versus bilateral peace / armistice.
- Tests that claim UI routing or button behavior is covered.

Out of cleanup visible scope, but not unowned:

- Full Slice G AI treaty authorship, ally petitions, conference mechanics, or veto systems are assigned to SC-32 and Slice G2 in the Deferred Work Landing Ledger.
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
13. Can the player author or change treaty clauses through the approved full treaty flow?
14. Does `Ratify Settlement` block on rejection and hard stops before mutation?
15. If incoming settlement offers are exposed in mailbox/top-bar routes, can gameplay naturally produce one?
16. If a nation shares multiple wars with the player, does the wizard disambiguate rather than choosing a sorted first `war_id`?
17. If a typed/free-text settlement command lacks `war_id`, does it reject multi-war ambiguity instead of choosing a silent fallback?
18. Can stale-state recovery or `must_reopen` loop indefinitely while `settlement_confirm` remains a hard stop?
19. Does blocked acceptance suppress misleading numeric score copy such as `0 / 50 - Blocked` and show the hard-stop reason instead?
20. Does incoming-offer copy use incoming-offer framing, or does it reuse outgoing "Will they accept?" settlement review copy?
21. Do active partial settlements route back to live war context instead of archived/recent-settlement ledger focus?
22. Is every Godot settlement script at least parse/load checked, and are button/signal paths executable rather than source-string-only?
23. When `Ratify Settlement` is blocked, does the popup expose an edit route, recovery route, archived-history route, or explicit terminal close copy instead of a false disabled action?
24. Can a losing-side player author concessionary peace through the same editor pipeline, with acceptance scoring rewarding concessions from the accepting side's perspective?
25. Are concessionary clauses visually distinguished from demanded clauses in both editor and review mode?

## Known Blocker: Revise Terms

Current behavior:

- `revise_settlement_terms` returns a typed backend response with `must_reopen=True`, `reopen_target`, unchanged `settlement_terms`, and `mutated=False`.
- Godot now avoids command-box fallback and reopens the settlement review by calling the normal war-settlement entry path.
- That entry path re-stages from scratch and does not preserve or mutate draft terms.
- Godot's reopen call currently forwards only `war_id` and `target_nation`; even if the backend returns `settlement_terms`, `_on_war_settlement_clicked(...)` drops them and sends a fresh `propose_common_peace` request.
- No term editor, draft-package builder, or term mutation surface is opened.

Root-cause diagnosis:

- The original Slice F closeout treated "no command-box fallback" as the Revise Terms fix. That solved the wrong layer: the button stopped synthesizing typed text, but still had no editor, no draft mutation, and no terms-preserving route.
- The interim safety decision then hid `Revise Terms` rather than rendering it disabled. That was valid for SC-2 in isolation, but it created the rejected-popup dead end once `Ratify Settlement` became unavailable: the only available player action became `Back Out`.
- Tests pinned the presence/absence and backend response shape around ratification and revise handling, but no behavior test asserted the player-facing rejected-popup action set. A rejected `settlement_confirm` payload with no real recovery route therefore passed.
- Future fixes must test the whole popup contract, not only the individual button contract: when ratification is blocked, the payload must provide at least one honest next-step affordance or an explicit, approved temporary no-next-step deferral with player impact recorded in `docs/STATUS.md`.

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

## Critical Synthesis

These are the non-deferrable product issues for the cleanup gate:

1. The common-peace player path currently opens and ratifies an empty/no-clause package unless external code passes `settlement_terms`. The approved fix is draft term authoring with real preview/revision/ratification flow. This is the root P0 because it makes every term, harshness, projection, and revision affordance suspect.
2. `Revise Terms` and incoming-offer `Request Revision` are false revision affordances until a real editor or negotiation route exists.
3. `Ratify Settlement` must not mutate state when the displayed acceptance verdict rejects the proposal or when hard stops exist.
4. `incoming_settlement_offer` is registered and handler-tested, but current code comments state there is no gameplay producer. Handler scaffolding is not shipped offer functionality.
5. Multi-war and coalition settlement entry points must preserve the exact war context instead of guessing, choosing a sorted first war, dead-ending, or routing the player to a generic ledger/popup.
6. Typed/free-text settlement entry is part of the same route-safety contract as the wizard: when no `war_id` is supplied and multiple shared wars exist, it must reject with a humanized ambiguity message rather than picking a legacy fallback.
7. Result feedback must route active partial settlements to live war/settlement context. Sending `war_ended=False` outcomes to archived/recent-settlement ledger focus hides the remaining war from the player.
8. Incoming-offer `Accept` must preserve the offered package. Rebuilding a fresh generic `settlement_confirm` from live state while dropping offered clauses is not accepting an offer; it is restaging a different common-peace review.
9. Settlement command-fallback protection must be keyed by dialogue family/type, not by a drift-prone local action whitelist. A new settlement action id must not be able to fall through to synthesized natural-language command text.
10. Source-string tests are not enough. Every player-facing settlement action needs behavioral coverage, and Godot scripts need parse/load or executable coverage before manual smoke.
11. Failed settlement confirmation must not replace one false affordance with another. When acceptance, score, or hard stops block ratification, `confirm_settlement` is absent from `options[]`; the popup renders a settlement-blocked voice banner plus real routes such as edit/re-author when available or `Open War Detail` for live war reassessment. War Detail may expose Bilateral Peace or Armistice only through their own pair-scoped eligibility rules; the rejected settlement popup itself must not emit direct substitute peace actions. This is the canonical v0.22 ratify decision: blocked ratification is explained by banner, body copy, and recovery routes, not by a disabled `Ratify Settlement` button.

### Product Decision - Full Treaty Settlement

The product decision as of May 6, 2026 is **Full Treaty Settlement**, not permanent `Common White Peace`.

Required shape:

- Settlement entry opens a war-scoped draft package, not a bare empty-package confirmation.
- The player can add, remove, or change concrete treaty clauses before ratification.
- Every draft change re-runs common-peace preview: acceptance, hard stops, warnings, beneficiaries, ignored parties, remaining wars, political costs, and clause mutations.
- `Revise Terms` and incoming-offer `Request Revision` are real editor/counter routes, or absent until they are real.
- Incoming AI settlement offers preserve offer identity and exact offered clauses through accept/review/revision.
- `Ratify Settlement` is only available after the displayed acceptance verdict and hard-stop gate pass, and the backend enforces the same rule even if called directly.
- Settlement authoring uses the same conversational diplomacy standard as normal treaties: the player is choosing demands and offers through structured controls, Talleyrand explains why a court will or will not sign, and foreign-court copy answers in diplomatic voice rather than exposing scorer/debug state.

The existing one-to-one peace/proposal flow is the nearest UX and engineering analogue. Reuse its proven author -> preview -> adjust -> confirm pattern where possible, but keep common-peace state war-scoped (`war_id`, proposer side, accepting side/leader, covered enemies, selected target, route id, and draft terms).

Temporary hide/remove decisions are still valid when an implementation slice cannot complete the full route in one pass, but the hidden affordance and player impact must be recorded explicitly. Do not solve SC-1 by permanently rebranding the feature to white peace without a new product decision.

Two-way AI-to-player negotiation, AI counter-proposals, conference rounds, and ally veto systems are assigned to SC-30 / SC-32 and the landing slices in the Deferred Work Landing Ledger. This cleanup still must feel complete and usable: it delivers player-authored treaty terms with iterative acceptance preview, consequence preview, revise/re-author loops, and hard-stop refusal as the negotiation feedback loop. SC-5 defer-and-hide ensures no two-way negotiation controls are exposed until the AI counterpart exists end to end.

### Player-Facing Vocabulary

The player-facing term is **Settlement**. UI copy should use `Settlement`, `Open Settlement`, `Ratify Settlement`, `Settlement History`, and clause-specific treaty language inside the settlement flow. `common peace` remains an internal/backend command concept and save-compatible implementation term; it must not appear as the normal player-facing label for this flow. `treaty` may describe concrete authored clauses or stored records, but it must not be used interchangeably with the top-level CTA or route name.

### Routing Boundary

Three peace paths exist, and the player must always know which one applies:

- **Settlement** covers multi-party wars with more than two total participants. It is the only path that can resolve some hostile pairs while leaving others active.
- **Bilateral Peace** covers one-to-one wars. It ends that war in one transaction.
- **Armistice** covers any war as a temporary cease-fire that does not transition the war to peace.

Settlement controls must not appear on one-to-one wars; SC-10 enforces this on war-detail and war-status rows. Bilateral peace controls must not appear as the default multi-party war settlement path unless the player explicitly drops into an approved single-pair scope.

When SC-10 hides Settlement controls on a one-to-one war row or detail surface, the same player surface must still expose the appropriate substitute peace affordance: `propose_peace` / Bilateral Peace and `propose_armistice` where eligible. Hiding Settlement without a reachable bilateral peace or armistice path on war detail and war status fails this spec, because it regresses the player from a visible but wrong CTA to no usable peace CTA.

Rejected multi-party settlement recovery is different: `Open War Detail` is a route back to live war context, not a promise that a bilateral peace or armistice action exists for the selected pair. War Detail renders pair-scoped Bilateral Peace / Armistice controls only if their own eligibility probes pass for the selected target; otherwise it renders humanized no-current-pair-alternative copy and leaves the player in the live war context. Direct rejected-popup CTAs such as `Seek Armistice Instead`, `Seek Bilateral Peace`, or settlement-family wrappers around those actions remain forbidden until SC-29 lands scope, handoff payload, eligibility helper, voice, and behavior tests.

### Canonical Settlement Clause Schema

All settlement editor writers, backend preview validators, staging code, merge logic, presentation, and ratification readers use this exact wire schema. Aliases such as `target`, `imposer`, `payer`, or `recipient_nation` are forbidden unless this table is explicitly amended. Unknown or alias-only keys must fail POST preview with `disabled_reason_display` and an offending clause index.

| Clause type | Required keys | Optional keys | Merge identity |
| --- | --- | --- | --- |
| `peace` | `type` | none | `(type)` |
| `territory_cede` | `type`, `from`, `to`, `region` | none | `(type, from, to, region)` |
| `gold_indemnity` | `type`, `from`, `to`, `amount` | none | `(type, from, to)` |
| `gold_per_turn` | `type`, `from`, `to`, `amount`, `turns` | none | `(type, from, to)` |
| `forced_alliance` | `type`, `from`, `to` | `includes_continental_system` | `(type, from, to)` |
| `vassalage` | `type`, `from`, `to` | none | `(type, from, to)` |
| `subjugation` | `type`, `from`, `to` | none | `(type, from, to)` |
| `liberation` | `type`, `vassal_nation`, `lord_nation`, `liberator` | none | `(type, vassal_nation, lord_nation, liberator)` |

Clause ordering within `settlement_terms[]` is presentation-only. Preview, acceptance scoring, and mutation must produce the same result regardless of clause order. The editor may reorder clauses for display grouping without changing outcome.

### Clause Display Vocabulary

The wire keys above are not player-facing labels. The editor, preview, dispatch, and ledger must use clause-specific vocabulary so `from` / `to` never leak as field labels.

| Clause type | Player-facing field labels | Direction display |
| --- | --- | --- |
| `peace` | no fields | "End hostilities (no material change)" |
| `territory_cede` | `Ceding nation`, `Receiving nation`, `Region` | "Offered to <them>" when the player is ceding; "Demanded from <them>" when the enemy is ceding |
| `gold_indemnity` | `Payer`, `Recipient`, `Amount` | "Offered to <them>" when the player pays; "Demanded from <them>" when the enemy pays |
| `gold_per_turn` | `Payer`, `Recipient`, `Amount per turn`, `Turns` | same as gold indemnity |
| `forced_alliance` | `Nation forced into alliance`, `Alliance imposed by`, `Continental System inclusion` | "Imposed on <them>"; any future voluntary alignment offer needs its own product decision and cannot reuse forced-alliance copy |
| `vassalage` | `Nation becoming vassal`, `Lord nation` | "Submits to <lord>" |
| `subjugation` | `Nation being subjugated`, `Subjugating nation` | "Forced under <lord>" |
| `liberation` | `Vassal to liberate`, `Current lord`, `Liberator` | "Liberate <vassal>" |

Behavior tests must fail if editor controls, preview rows, or generated settlement copy show literal `from` / `to` labels to the player, or if structured-control labels use internal enum phrasing instead of this table.

### Concession And Treaty Conversation Contract

Losing-side peace is owned by SC-1's first editor floor, not by a future unowned "ask for terms" feature. Concessionary authoring requires no new clause types. The existing clause schema supports concessions when authored direction benefits the accepting side: France can be the `from` / payer / ceding nation, and the enemy can be the recipient. The editor presents this as an offer-mode conversation, not as a new clause type, incoming-offer wait, mailbox action, or free-text command.

Required behavior:

- The editor exposes a clear demand/offer direction for every live material clause. `territory_cede` and `gold_indemnity` must support player-as-ceder and player-as-payer packages in G2-Slice-1.
- The player can request a Talleyrand concession baseline while losing. This is a draft-suggestion affordance using existing MVP clauses (`peace`, `territory_cede`, `gold_indemnity`), not an incoming AI offer, not a mailbox route, and not a free-text command.
- Acceptance scoring evaluates each term from the accepting side's perspective. Clauses that benefit the accepting side reduce effective harshness or add a named `concession_credit` component; clauses that burden the accepting side increase harshness. Direction must be visible in the component explanation.
- The concession baseline uses only complete canonical clauses and must be deterministic from fixture state. The `settlement_losing` / `settlement_rejected` smoke fixture must publish a transferable non-capital `concession_region`, France must have at least 1500 gold or an explicitly documented lower fixture amount, and the Talleyrand baseline attempts, in order: `{"type": "peace"}`, a `gold_indemnity` from France to the accepting leader for the lesser of 1500 or the fixture's documented safe concession amount, and one `territory_cede` from France to the accepting side for `concession_region` if gold alone does not reach `near_acceptable`. Any lower amount or missing region is a fixture failure, not a reason to silently weaken the concession test.
- Peace-only losing drafts are valid previews but must not pretend to be concessionary. If a losing-side `{"type": "peace"}`-only draft stays below threshold, the preview panel shows humanized guidance such as "This package offers no material change. Authoring concessions may improve acceptance." This is copy guidance only, not an AI-offer wait or separate action.
- Invalid concession attempts fail POST preview with humanized `disabled_reason_display`; they must not silently flip direction, strip the clause, or render a court response as if a valid offer exists.
- The review voice mirrors standard treaty conversations: Talleyrand names the strongest blocker or concession, foreign-court lines answer the package in their register, and no raw `from` / `to`, `verdict`, or component ids appear in player copy.

Required tests: `test_losing_side_authored_concession_draft_can_reach_accept_band_with_realistic_war_state`, `test_concession_terms_move_acceptance_in_accepting_side_direction`, `test_talleyrand_concession_baseline_uses_existing_clause_schema`, `test_losing_peace_only_preview_prompts_concession_without_offer_wait`, and `test_concession_review_uses_treaty_conversation_voice_not_debug_terms`.

### Spec Review Gate

Any dedicated settlement/peace UX spec review before implementation, smoke, or branch-target reconciliation uses the established scoring categories: Fun, Clarity, Work Segmentation, Contradiction-Freedom, and Completeness. Each category must score at least 8/10. Any unresolved P0 or P1 finding makes the verdict NO-GO regardless of scores. The review must name the reviewer, date, target branch/commit, current cleanup spec version, and review-session reference. The GO/NO-GO result must be recorded in `docs/STATUS.md`; a GO entry must name the exact spec version and review-session reference, while a NO-GO entry must name the minimum spec edits blocking Gate 1. Three consecutive NO-GO reviews on the same scope escalate to a product decision: reduce scope, rewrite the contract, or explicitly accept a hidden/deferred player impact in this spec and `docs/STATUS.md`.

### Hard Gate Before Implementation

The cleanup implementation may not start Slice G or broader settlement agency until these issues are closed by implementation or by hiding/removing the broken affordance:

1. **Common peace must become real editable treaty settlement.** Ship war-scoped term authoring, preview, revision/counter, and ratification gating. Hide incomplete authoring affordances while building them; do not claim completion from empty/no-clause white peace.
2. **`Ratify Settlement` must obey the displayed acceptance verdict and hard stops.** Both the UI payload and `ratify_settlement_confirm` must enforce the same gate.
3. **Settlement resource costs must be explicit and cannot hide on the opener.** `Open Settlement`, draft preview, Submit, Revise Terms, Back Out, failed ratification, stale recovery, and hard-stop refusal cost 0 DP/AP/gold. The cleanup default is also 0-cost successful ratification; any future non-zero ratification cost must be recorded in this spec and `docs/STATUS.md` before coding, live on `confirm_settlement`, and be charged only after the same acceptance/hard-stop gate passes.
4. **`Revise Terms` must revise terms or disappear.** A reopen loop is not revision. Until an edit-capable route is advertised with `can_edit_terms=true`, concrete `available_clause_types[]`, and the current staged package, `revise_settlement_terms` is absent from `options[]`; a disabled "Term editor not available yet" button is a false affordance and fails this gate.
5. **Incoming settlement offers must be end-to-end usable or fully hidden.** A mailbox-visible offer type with no producer or popup payload is not allowed.
6. **Every normal entry path must preserve or require a specific `war_id`.** Wizard, war detail, coalition detail, notifications, result feedback, ledger focus, stale reopen, and typed/free-text command entry must not choose the wrong war by sorting or fallback.
7. **Coalition settlement controls must be eligibility-gated and actionable.** `Open Whole-War Settlement` cannot appear just because rows share a `war_id`; it must respect settlement eligibility, and multi-war coalitions need per-war buttons or approved hidden/no-action copy.
8. **Active settlement routes must not collapse into archived ledger focus.** `war_ended=False` routes to an active settlement review or war detail; `war_ended=True` routes to the ledger row.
9. **Stale recovery must have an escape path.** `must_reopen` cannot loop indefinitely or strand a hard-stop dialogue; repeated/irrecoverable stale state must pop or surface a humanized back-out path.
10. **Incoming-offer accept/request actions must preserve offer identity.** `Accept` cannot drop the offered `settlement_terms` and restage a fresh generic common-peace package; `Request Revision` cannot be exposed unless it opens a real counter/edit route.
11. **Settlement action fallback must be family-level safe.** Settlement dialogues must never synthesize natural-language command text for unknown/new action ids; unknown settlement actions must re-show the popup or surface a hard UI error.
12. **Godot coverage must prove execution, not just source presence.** Settlement-critical Godot scripts must parse/load, button signals must execute, and tests must fail when a visible settlement action becomes a no-op or command-text fallback.
13. **Settlement entry must carry authored terms end to end.** `_execute_propose_common_peace` and every structured Godot settlement entry path must forward authored `settlement_terms` into `stage_settlement_confirm(...)`; an editor that previews terms but ratifies an empty package fails this gate.
14. **Cross-war settlement collisions must not clobber the active review.** Only one settlement-family hard-stop may own the active popup at a time; a second settlement for a different `war_id` must return `cross_war_settlement_collision` with humanized "resolve current settlement first" copy without replacing the current dialogue or queuing a hidden mailbox defer.
15. **G2-Slice-1 must ship a minimum live authorable clause set.** The first treaty editor slice cannot close as a peace-only or empty-shell editor. At minimum, `peace`, `territory_cede`, `gold_indemnity`, and `forced_alliance` must be enabled, previewable, submittable, and ratifiable when valid. Other canonical clauses may be interim-hidden only through the four-artifact protocol.
16. **Submit must revalidate authored terms before staging.** `_execute_propose_common_peace` must re-run the SC-1 POST preview / conflict-matrix validation on submitted `settlement_terms` before `stage_settlement_confirm(...)`. Validation failure returns `error="submitted_terms_failed_revalidation"` with humanized copy, `success=False`, and no staged dialogue.
17. **Settlement-family safety covers hard stops and current-turn offers.** SC-14 live-route foregrounding, SC-18 command-fallback safety, and SC-26 same-war/cross-war collision rules apply to every settlement-family dialogue, including hard-stop `settlement_confirm` and current-turn-offer `incoming_settlement_offer` if SC-5 is explicitly reversed.
18. **Failed settlement confirmation must offer an understandable next step.** A rejected or blocked `settlement_confirm` is only a ratification gate, not a treaty editor, not a surrender menu, not a bilateral armistice action, and not an incoming-offer mailbox. If acceptance, score, or hard stops block ratification, `confirm_settlement` is absent from `options[]` and `available_action_ids[]`; the popup renders `settlement_blocked_for_ratification_talleyrand` as the primary banner and then shows only real next-step actions. `Revise Terms` is visible only when it opens a real editor/re-author route. `Open War Detail` is the recovery route back to live war context; War Detail, not the settlement popup, may expose pair-scoped Bilateral Peace / Armistice where their own eligibility allows. The settlement popup must not emit `propose_armistice`, `propose_peace`, `seek_armistice_instead`, disabled Ratify, disabled Revise placeholders, `wait_for_enemy_offer`, `ask_for_terms`, `surrender_terms`, or any enemy-offer waiting action while their owning systems are deferred.

If a short interim patch ships before full treaty authoring, it must hide or neutralize incomplete treaty-authoring implications: `Revise Terms`, term harshness rows, projected-hegemony / Balance pressure rows, forced-alliance threat preview, vassalage / liberation / gold clause preview, and any Terms section copy that implies clauses beyond the actually editable draft. This is an interim safety measure, not the approved end state.

If incoming settlement offers are deferred, the cleanup patch must remove the player-facing scaffolding together: drop `incoming_settlement_offer` from hard-stop and mailbox type taxonomies, mailbox summary labels, Godot proposal/settlement popup type lists, and settlement action lists, or put them behind a disabled feature flag. The handler may remain only if tests prove no normal gameplay or mailbox path can expose it. Any enemy-offer waiting action or label is a visible promise and fails SC-5 while the producer is deferred. Required behavior test: `test_rejected_settlement_popup_with_sc5_deferred_does_not_render_enemy_offer_waiting_control`.

### Rejected Settlement / Losing-Side UX Contract

The common settlement confirmation popup is a ratification checkpoint. It reviews a concrete settlement package and asks whether the accepting side will take it. It is not, by itself, a treaty editor, a surrender menu, or an incoming-offer mailbox. When acceptance fails, the UI must explain that the proposed package cannot be ratified in its current form and then route the player toward the real peace tools that exist.

Required interim behavior before full treaty authoring:

- Omit `confirm_settlement` from `options[]` and `available_action_ids[]` when verdict is reject/blocked, score is below `acceptance.threshold`, or hard stops exist. The renderer must not assume Ratify is present.
- Render `settlement_blocked_for_ratification_talleyrand` or the equivalent Voice Bible 16.1 blocked-ratification family as the primary banner, with exact blocker copy in the popup body.
- Do not render `Ratify Settlement` as a disabled placeholder. Blocked-ratification reason belongs in the banner/body and recovery routes. A disabled Ratify button is a false affordance because it reads like a future click target inside the same popup.
- Do not show a working `Revise Terms` action unless it opens an edit-capable draft route that preserves `war_id`, covered participants, selected target, and current `settlement_terms`.
- If revision is not yet implemented, hide `Revise Terms` entirely and record the temporary hide with owning SC row, restoring slice, STATUS line, and CI gate. Disabled placeholder buttons are forbidden because they read like a player action. Do not route it to a no-op reopen loop.
- If the war is active, include `Open War Detail` as a structured recovery route back to the exact live war context. War Detail may show Bilateral Peace or Armistice only when the selected pair is eligible under those systems' own probes; otherwise it must show humanized no-current-pair-alternative copy. Do not surface a direct armistice or bilateral-peace action from `settlement_confirm`; settlement is war-scoped and armistice / bilateral peace are separate pair-scoped flows.
- If the war has archived, include `Open Settlement History` when a route id exists. Only malformed payloads with no recoverable active or archived target may collapse to `Back Out` alone, and they must show humanized recovery copy.
- If AI settlement offers are deferred, do not imply that waiting will produce one. Enemy-offer waiting must not appear as an action, disabled action, label, route, or recovery hint while SC-5 is deferred.

Failure-state control table:

| State | Required visible controls, in order | Required body copy |
| --- | --- | --- |
| Acceptance fails, editor available | active `Revise Terms`; `Open War Detail`; `Back Out` | Explain the current package cannot be ratified, identify the top acceptance blockers, and explain that War Detail can reassess live pair-scoped peace / armistice options where those systems are eligible. |
| Acceptance fails, editor unavailable | `Open War Detail`; `Back Out` | Explain that this review cannot alter terms in the current route; do not show a disabled `Revise Terms` control or "editor not available yet" placeholder. |
| Hard stop active | `Open War Detail`; `Back Out` | Explain the hard stop and why no ratification action is available until scope/state changes. |
| Active war, no editor route | `Open War Detail`; `Back Out` | Explain that this popup cannot alter terms, and route the player to live War Detail for eligible pair-scoped alternatives or no-current-pair-alternative copy. |
| Archived war | `Open Settlement History`; `Back Out` | Explain the war changed after staging and route to the archived settlement/history row. |
| Stale or leader-change rescore failure | `Revise Terms` only if editor route still valid; `Open War Detail` or `Open Settlement History`; `Back Out` | Show previous score/verdict, current score/verdict, and the top components or hard stops that changed. |

Required behavior tests: `test_failed_ratification_popup_omits_ratify_action_in_options_array`, `test_rejected_settlement_popup_renders_required_control_set_for_each_blocked_state`, and `test_failed_settlement_popup_shows_war_detail_route_when_no_popup_peace_action_exists`.

Rejected-settlement recovery affordance contract:

| Affordance | Payload field | Action id | Eligibility source | Click behavior | Voice family |
| --- | --- | --- | --- | --- | --- |
| Return to editor | `options[]` entry plus `editor_route` | `revise_settlement_terms` | `can_edit_terms=true`, non-empty `available_clause_types[]`, staged `settlement_terms`, `war_id`, `covered_enemy_participants`, and `selected_target_nation` present | Switches the same settlement popup back to `EDIT` mode with the staged package and scope preserved; no mutation, cost, mailbox, or typed command fallback | `settlement_blocked_for_ratification_talleyrand` plus editor voice for the selected clause |
| Open War Detail | `options[]` entry plus `recovery_route` | `open_war_detail` | Active `war_id` still exists or can be resolved from the mounted settlement route | Backgrounds the rejected review without discard-confirm, preserves a non-empty draft under the scoped settlement draft key, opens War Detail for the exact `war_id` and selected target, and lets War Detail expose pair-scoped Bilateral Peace / Armistice only through their own costs, eligibility, and disabled reasons | `settlement_open_war_detail_recovery_talleyrand` |
| Open Settlement History | `options[]` entry plus `recovery_route` | `open_settlement_history` | War archived or ended and non-empty `route_id` exists | Closes the stale review and opens the merged `PEACE & SETTLEMENT HISTORY` row identified by `route_id`; no mutation and no draft carry-forward | `settlement_open_history_recovery_talleyrand` |
| Terminal close | synthetic close/back-out option plus `terminal_recovery_copy` | `back_out_settlement` or `close_settlement_review` | No editor route, active war route, or archived route can be resolved from the payload | Closes the popup with humanized copy explaining that the settlement details cannot be recovered and the player must reassess from live war surfaces; this is allowed only for malformed or unrecoverable payloads | `settlement_no_alternative_route_chancery` |

`recommended_alternatives[]` is allowed only as explanatory metadata for the real routes above. It must not contain direct `propose_armistice`, `propose_peace`, `seek_armistice_instead`, `seek_bilateral_peace`, `wait_for_enemy_offer`, `ask_for_terms`, `surrender_terms`, disabled Ratify, disabled Revise, or any settlement-family wrapper around bilateral tools. War Detail owns Bilateral Peace and Armistice selection. Required behavior tests: `test_blocked_settlement_recovery_affordance_schema`, `test_blocked_ratify_is_absent_and_blocked_banner_explains_reason`, `test_no_wait_for_enemy_offer_affordance_while_incoming_offers_deferred`, `test_rejected_settlement_recommended_alternatives_do_not_include_direct_pair_action_wrappers`, and `test_blocked_settlement_with_no_alternatives_shows_terminal_copy_and_close`.

War Detail recovery contract:

- The recovery action id is `open_war_detail`, with `recovery_route={"surface": "war_detail", "war_id": str, "selected_target_nation": str | null, "covered_enemy_participants": List[str], "source_route_id": str | null, "reason": str}`. Archived recovery uses `{"surface": "settlement_history", "route_id": str}`.
- The settlement popup never emits `propose_armistice`, `propose_peace`, or a settlement-family wrapper for those actions. War Detail owns those structured controls and their normal costs, cooldowns, target pickers, and disabled reasons.
- Choosing `Open War Detail` is a background-and-preserve transition, not ordinary Back Out. It preserves a non-empty unratified draft in `pending_settlement_drafts[draft_key]` without showing discard-confirm, because the player is following the spec-provided recovery route rather than abandoning the draft. This transition does not consume a SC-14b settlement reopen attempt; the substitute live-war surface is a different action family.
- If the player completes bilateral peace or armistice from War Detail, any preserved settlement draft whose `draft_key` covers the affected pair becomes stale. Reopening Settlement must run fresh POST preview before any ratification path appears; if the war state no longer supports the draft, the player sees a stale-draft notice and may discard or re-author.
- If the player cancels or fails the bilateral peace / armistice flow, returning to Settlement restores the draft as previous/stale and requires preview refresh before Submit or Ratify.
- One-to-one wars should not normally reach `settlement_confirm`; if a stale save or debug path does, the same `Open War Detail` route is required so the proper Bilateral Peace / Armistice controls are reachable.
Required behavior tests: `test_failed_settlement_open_war_detail_preserves_draft_without_pair_action`, `test_open_war_detail_recovery_preserves_non_empty_draft_without_discard_prompt`, `test_open_war_detail_recovery_does_not_promise_ineligible_pair_action`, `test_bilateral_armistice_success_invalidates_only_matching_scoped_settlement_draft_with_notice`, `test_seek_armistice_instead_cta_absent_until_owned_by_future_row`, and `test_one_to_one_stale_settlement_routes_to_war_detail_bilateral_tools`.

Draft identity contract:

- `draft_key` is `settlement_draft:{war_id}:{selected_target_key}:{covered_scope_hash}`. `selected_target_key` is the selected target nation or the literal `_none`. `covered_scope_hash` is the first 16 hex chars of SHA-256 over the ASCII JSON array of sorted unique `covered_enemy_participants` using compact separators. Do not use Python/Godot built-in hash functions, locale-dependent joins, unsorted input order, or duplicate-sensitive scope strings.
- Same-war same-scope restaging may merge compatible terms through SC-26. Same-war different-scope restaging is not the same draft; it must either open a chooser/replace-confirm path or return a humanized `same_war_scope_collision` with the existing draft unchanged.
- `pending_settlement_drafts` serializes as a dict keyed by `draft_key`. Each record stores `war_id`, `selected_target_nation`, sorted `covered_enemy_participants`, `settlement_terms`, `created_turn`, `updated_turn`, and `last_preview_hash`.
- Required behavior tests: `test_same_war_different_selected_target_drafts_do_not_merge_or_clobber`, `test_scoped_settlement_draft_key_round_trips_save_load`, `test_scoped_draft_key_is_stable_across_order_duplicates_save_load_and_client_roundtrip`, and `test_same_war_same_scope_merge_uses_sc26_clause_identity`.

Draft-discard notice contract:

- End-turn discard writes a one-shot `pending_settlement_draft_notices[]` entry or an explicitly equivalent dispatch/campaign-log notice with `war_id`, `turn_discarded`, `draft_clause_count`, `selected_target_nation`, and `message_display`.
- The notice survives save/load until rendered once, then clears. It must not restore the discarded draft or allow ratification from stale data.
- Required behavior test: `test_load_after_end_turn_does_not_silently_drop_draft_without_player_signal`.

Required final behavior for losing-side peace:

- The player must be able to seek peace while losing. Settlement agency cannot depend on first becoming the winning side.
- Losing-side treaty packages must support concessionary terms through the same war-scoped authoring/preview/ratification pipeline. Cleanup-scope losing peace means player-authored concessions using canonical clauses, especially player-as-payer / player-as-ceder `gold_indemnity` and `territory_cede`, plus the neutral `peace` floor. `Ask for terms` belongs to SC-30's AI offer/request-terms landing slice; `Surrender terms` belongs to SC-31's dependency/surrender landing slice. Neither label may appear as a cleanup payload action, mailbox wait, backend command text, or editor preset before its landing slice ships.
- "Concession" is primarily an authoring and presentation direction, not a new required clause type. The canonical schema already supports concessions when a clause uses `from=France` / `to=<enemy>` or otherwise benefits the accepting side. The editor must surface per-clause `direction_display` such as "Demanded from <them>" versus "Offered to <them>" and acceptance scoring must treat the sign consistently through `concession_credit` / reduced harshness components.
- The first editor slice must include a discoverable concession baseline or suggestion affordance for losing players, such as `Generate concession baseline` or a Talleyrand suggestion using existing MVP clauses (`territory_cede`, `gold_indemnity`, `peace`). Without that, losing-side peace is technically possible but practically invisible.
- G2-Slice-1 includes peace-with-concessions in the live floor: the `territory_cede` and `gold_indemnity` controls must support player-as-ceder and player-as-payer packages, and those packages must run through the same preview, acceptance, and ratification gates as winner-favored demands.
- Acceptance scoring may make harsh player-favored terms impossible while losing, but it must not strand the player without any peace-seeking route.
- Incoming AI offers/counter-offers may complement losing-side peace only if SC-5 is explicitly reversed; they cannot be the only way for a losing player to pursue peace.
Required behavior test: `test_losing_side_authored_concession_draft_can_reach_accept_band_with_realistic_war_state`, using a losing France fixture with player-authored gold/territory concessions to Britain and asserting the preview reaches `accept` or `near_acceptable`. Absence tests: `test_ask_for_terms_absent_while_incoming_offers_deferred` and `test_surrender_terms_absent_until_dependency_clause_restoration`.

Rejected-popup presentation co-landings:

- `proposal_confirm_popup.gd::_build_settlement_content` must not render the outgoing "Will <leader> accept this settlement?" header when `can_ratify=false`. Blocked/rejected reviews render the Voice Bible 16.1 blocked-ratification banner followed by `ratify_blocked_reason`.
- Blocked hard-stop acceptance suppresses numeric `0 / 50 - Reject/Blocked` copy. Backend acceptance display should use null/absent `total` and `threshold` for hard-stop blocked states, and Godot must render blocker copy instead of coercing null to `0`.
- Production Godot must not show developer text such as `Settlement payload incomplete: missing ...`. Malformed settlement payloads render humanized recovery copy: "Settlement details could not be loaded; reopen from War Status."
- Incoming and outgoing settlement voices are split, or incoming settlement offers remain hidden under SC-5.
- Production surfaces must not show backlog-copy labels such as "Term editor not available yet", "Wait for Enemy Offer", "Seek Armistice Instead", "Ask for terms", or "Surrender terms" unless the owning landing row for that exact action is implemented end to end with tests.

### Full Treaty Settlement Flow

The normal player path is: (1) wizard, war detail, or coalition detail emits `settlement_clicked(war_id, target_nation)`; (2) Godot opens the editor on the existing `proposal_confirm_popup.gd` settlement surface in `EDIT` mode; (3) clause-add, clause-remove, and clause-edit commits trigger `POST /diplomatic_preview?mode=settlement` with the current `settlement_terms` and `covered_enemy_participants` and refresh acceptance, warnings, hard stops, and `disabled_reason_display`; (4) Submit sends `/command` with `action=propose_common_peace`, `target_nation`, `war_id`, `selected_target_nation`, `covered_enemy_participants`, `settlement_terms`, and player-editor caller context after one final POST preview; (5) `_execute_propose_common_peace` revalidates the submitted terms and covered-enemy scope against the SC-1 POST preview taxonomy, then forwards `settlement_terms`, `covered_enemy_participants`, `selected_target_nation`, and `caller_kind="player_editor"` into `stage_settlement_confirm(...)`; (6) `settlement_confirm` transitions the same popup to `REVIEW` mode and reviews the same package and scope; (7) `Revise Terms` returns the same package and covered-enemy scope to `EDIT` mode only when an edit-capable route exists; (8) only review-mode `Ratify Settlement` can mutate, and it re-runs `calculate_common_peace_acceptance(...)` fresh before mutation. Editor-mode ratification shortcuts are forbidden in this cleanup phase; editor mode submits to review, and review mode owns ratification.

Canonical payload schemas:

- POST settlement preview request: `{"mode": "settlement", "war_id": str, "actor_nation": str, "selected_target_nation": str, "covered_enemy_participants": List[str], "settlement_terms": List[Clause], "caller_kind": "player_editor", "draft_key": str | null}`.
- POST settlement preview response: `{"success": bool, "valid": bool, "draft_key": str, "dialogue_mode": "EDIT", "can_submit": bool, "available_clause_types": List[str], "validation_errors": List[{"clause_index": int | null, "field": str | null, "code": str, "disabled_reason_display": str}], "acceptance": {"band": str, "band_display": str, "total": int | null, "threshold": int | null, "top_components": List[Dict], "previous_band": str | null, "delta_display": str | null}, "hard_stops": List[Dict], "warnings": List[Dict], "review_sections": ReviewSections}`. Alias keys such as `accept_threshold` may exist inside the scorer only; presentation and ratification consumers read `threshold`.
- Submit command request: `{"action": "propose_common_peace", "target_nation": str, "war_id": str, "selected_target_nation": str, "covered_enemy_participants": List[str], "settlement_terms": List[Clause], "draft_key": str, "caller_kind": "player_editor"}`. The executor reruns POST-preview validation before staging and returns `submitted_terms_failed_revalidation` without staging on mismatch.
- `settlement_confirm` REVIEW payload: top-level `type="settlement_confirm"`, `dialogue_mode="REVIEW"`, `war_id`, `route_id`, `draft_key`, `selected_target_nation`, `covered_enemy_participants`, `settlement_terms`, `acceptance`, `hard_stops`, `can_ratify`, `can_edit_terms`, `options[]`, `available_action_ids[]`, `editor_route` when editable, and `recovery_route` when blocked/stale.
- `options[]` entries use `{"action": str, "label": str, "available": bool, "disabled_reason_display": str | null, "editor_route": Dict | null, "recovery_route": Dict | null}`. For blocked ratification, no `confirm_settlement` option exists; disabled Ratify entries are forbidden.
- `ReviewSections` is an exact player-comprehension schema, not an opaque dict: `{"beneficiaries": List[{"nation": str, "reason_display": str}], "ignored_participants": List[{"nation": str, "reason_display": str}], "remaining_wars": List[{"war_id": str, "war_label": str, "reason_display": str}], "applied_clauses_preview": List[Dict], "third_party_reactions": List[{"nation": str, "reaction_display": str, "effect_preview": Dict}], "awe_tag_displays": List[str]}`. Empty lists are allowed only when the fixture/state has no matching data; omitting the key is a schema failure.
- Required behavior tests: `test_settlement_preview_submit_and_review_payload_schema_rejects_alias_keys_and_missing_scope` and `test_settlement_review_payload_requires_player_comprehension_sections_and_mutation_preview`.

Control-state matrix:

| Mode | Visible controls | Disabled / absent rules |
| --- | --- | --- |
| `EDIT` | Add Clause, per-clause edit controls, Preview refresh, Submit, Back Out | Submit / Preview are disabled while clause validation errors exist or POST preview is pending. Editor mode never shows `Ratify Settlement`; the player must submit into REVIEW mode before any mutation-capable control appears. Back Out and every popup dismiss path use SC-2 empty/non-empty discard semantics. |
| `REVIEW` | Ratify Settlement when ratifiable; Revise Terms when edit-capable; Open War Detail or Open Settlement History when blocked/stale; Back Out | Ratify Settlement is absent from `options[]` when the fresh verdict rejects, score is below `acceptance.threshold`, or hard stops exist. In that case the popup renders the blocked-ratification banner and the remaining real controls only. Revise Terms is visible only when it returns the staged package to an edit-capable route and is absent otherwise. Back Out pops review while preserving same-turn draft state under SC-2. |
| Blocked / stale recovery | Close or Back Out plus the pinned recovery route | A zero-action settlement payload must still include the synthetic close/back-out option. Recovery must not synthesize typed command text, generic proposal text, or an empty `must_reopen` target. |

### Editor Layout Contract

The settlement editor is not just a route to POST preview. It uses this panel map inside the existing settlement popup surface:

| Vertical band | EDIT mode | REVIEW mode |
| --- | --- | --- |
| Header | Settlement title, war label, selected target, voice line, mode badge `Editing draft` | Settlement title, war label, selected target, voice line, mode badge `Reviewing draft` |
| Clause package | Left column clause list with validation state, remove/reorder affordances, and selected-clause focus | Read-only clause summary with applied-clause preview links |
| Clause controls | Right column structured Add Clause controls and inline editor for the selected clause | Hidden; replaced by beneficiaries / ignored parties / remaining-war summary |
| Preview panel | Acceptance, hard stops, warnings, beneficiaries, ignored parties, political cost, mutation preview, stale/previous marker | Same preview panel, locked to the staged package unless Revise Terms returns to EDIT |
| Action rail | Back Out, Preview refresh, Submit | Back Out, Revise Terms only when edit-capable, Ratify Settlement only when active per SC-3/SC-4, recovery route when ratification is blocked |

- Add Clause controls: structured controls for each live clause type; no raw JSON or free-text clause entry.
- Inline clause editor: per-type fields use pickers, numeric inputs, toggles, and disabled reasons tied to the canonical clause schema.
- Preview network state: while a POST settlement preview is in flight, the acceptance/preview panel shows pending state, Submit is disabled, no editor-mode ratification control appears, and stale values are visibly marked as previous results. Preview failure preserves the last valid acceptance display with a visible stale marker and humanized "Could not preview this draft - try again" copy; it must not silently swallow the failure or show stale acceptance as current.
- Acceptance trend: after each completed clause commit that triggers POST preview, the editor renders the previous band, current band, and humanized delta. If a clause edit drops the package below `acceptance.threshold`, the band transition is visible before Submit. A structurally valid below-threshold draft may still Submit into REVIEW so the player can see the blocked-review explanation and recovery routes; REVIEW then omits `confirm_settlement` and blocks mutation per SC-3 / SC-4.
- 1080p reachability: all live clause types can be reached in a 1920x1080 viewport without controls being covered by another panel; scroll is allowed only when the focused control can be fully scrolled into view.
- A clause is committed for POST preview only when all required keys for its type are populated. Clauses with missing required keys remain editor-local `in_progress`, show an inline incomplete indicator, and do not trigger POST preview until complete. Picker open/close with no selection and invalid numeric blur do not POST; they update local validation state.
- If a clause type's picker has zero valid options, its Add Clause control is disabled with `disabled_reason_display` instead of opening an empty picker. This applies to territory with no controlled regions, gold with no payable amount, dependency clauses with no valid target, same-side forced alliances, and liberation with no valid vassal.
- Every authored clause renders a direction indicator in both editor and review mode: `Demanded` when the accepting side is burdened, `Conceded` when the player/proposer side offers value to the accepting side, and `Mutual` for `peace` or other no-material-change clauses. Color and wording must be consistent across the clause list, preview rows, and final review.
- Required behavior tests: `test_editor_acceptance_panel_shows_band_transition_after_clause_commit` and `test_below_threshold_valid_draft_can_submit_to_blocked_review_without_ratify`.
- Scene/source checks must prove all named panels exist under `_build_settlement_content`, toggle by `dialogue_mode in {"EDIT", "REVIEW"}`, and use the Clause Display Vocabulary table for labels.

### First-Slice Clause Eligibility Matrix

The G2-Slice-1 editor floor cannot rely on UI authors guessing legal targets. Each live first-slice clause uses this eligibility matrix for picker contents, preview validation, submit revalidation, display copy, and mutation. The source of truth is the POST settlement preview validator; Godot pickers mirror it but do not become the authority.

| Clause type | Picker source of truth | Valid `from` | Valid `to` | Value bounds / extra fields | Losing-side concession behavior | Invalid or empty-picker behavior |
| --- | --- | --- | --- | --- | --- | --- |
| `peace` | Active covered hostile/suspended pairs in `war_instance.active_diplo_keys` after current `covered_enemy_participants` filtering | none | none | No extra fields. One `peace` clause may exist; duplicates merge by `(type)`. | Talleyrand concession baseline may start with `{"type": "peace"}` as the neutral floor before adding material concessions. | If no coverable enemy remains, POST preview returns `no_coverable_enemy` / `no_covered_enemy_participants` with humanized copy and no editor Submit. |
| `territory_cede` | Current region controllers plus settlement home/capital safety helpers and coverable participant lists | Any current war participant that controls the region and is either proposer-side or covered accepting-side, depending on demand/offer direction | Any opposing-side participant or same-side eligible beneficiary allowed by settlement beneficiary rules | `region.controller == from`; region must be transferable under existing territory mutation rules; capitals/home regions follow the same hard stops as bilateral territory terms unless the spec explicitly authorizes a cession. | Offer mode must allow France/player-side `from` when losing, with `to` set to the accepting side or a valid accepting-side beneficiary. Direction display reads "Offered to <them>"; scoring applies reduced harshness or `concession_credit`. | Empty region picker is disabled with `disabled_reason_display`; tampered payload returns offending clause index plus `field="region"` or the participant field. The validator never silently flips `from`/`to` or strips the clause. |
| `gold_indemnity` | Nation treasury/economy data and active participant lists | Any active participant that can legally pay, including France/player-side in offer mode | Opposing-side participant or valid same-side beneficiary, according to demand/offer direction | `amount` is a positive integer, clamped by authored max display but never silently clamped on submit; submitted over-max returns validation error. | Offer mode must allow France/player-side payer packages while losing. Talleyrand baseline may choose a conservative payable amount that moves acceptance toward `near_acceptable` without bankrupting the player unless the fixture intentionally tests bankruptcy. | Zero payable amount disables Add Clause for payer-specific gold offers; invalid amount blur stays editor-local until corrected; tampered submit returns offending clause index plus `field="amount"`. |
| `forced_alliance` | Covered enemy participants, proposer-side leader/beneficiary rules, existing alliance state, WPS forced-alliance legality, and Balance of Europe threat preview | Covered enemy participant that is not already in an equivalent alliance/treaty state with the proposed imposer | Proposer-side leader or valid proposer-side beneficiary/imposer under current settlement rules | `includes_continental_system` toggle defaults to the bilateral forced-alliance default unless explicitly set. Threat preview uses the forced-alliance projection helper. | Demand-only in the first cleanup slice. Losing-side offer mode must hide forced-alliance when it would imply the losing player can force the victor into alliance. Any voluntary alignment offer belongs to SC-32 if the product wants it; it cannot reuse forced-alliance copy. | Same-side forced alliances, already-allied targets, losing-side unavailable imposition, and no covered enemy target disable or reject with humanized reasons. |

Required behavior tests: `test_first_slice_clause_picker_matrix_matches_post_preview_validator`, `test_losing_side_talleyrand_concession_baseline_uses_peace_gold_and_territory_only`, `test_gold_indemnity_over_max_rejects_without_silent_clamp`, `test_forced_alliance_losing_side_does_not_imply_unavailable_imposition`, `test_editor_renders_clause_direction_labels`, and `test_clause_add_disabled_when_picker_filter_empty_for_each_live_clause`.

## Gap Inventory

Every row needs a decision before implementation: implement now, hide/remove now, rename now, or explicitly defer with the broken affordance hidden. Deferral without hiding the player-facing affordance fails this spec. The `Priority` column is authoritative where table order differs.

| ID | Priority | Surface | Suspected Gap | Required Decision | Coverage Required |
| --- | --- | --- | --- | --- | --- |
| SC-4b | P2 | Settlement resource-cost contract | The cleanup spec previously inherited `Open Settlement` at `DP=0` only from the older implementation plan, while leaving ratification economics implicit. Verified anchors: `_execute_propose_common_peace` stages at `backend/commands/diplomatic_executor.py:2041` with no settlement resource contract, and `ratify_settlement_confirm` gates at `backend/game_logic/settlement_preview.py:1044` before mutation at `:1128` without an explicit DP/AP/gold decision. | The cleanup default is zero resource cost for `Open Settlement`, GET/POST preview, Submit, Revise Terms, Back Out, failed ratification, stale recovery, hard-stop refusal, and successful `confirm_settlement` ratification. A later non-zero ratification cost is allowed only after a new product decision is recorded in this spec and `docs/STATUS.md`; if added, it must live on `confirm_settlement`, be displayed before ratification, be charged exactly once after the fresh acceptance/hard-stop gate passes, and never be charged for failed or blocked ratification. No settlement opener, preview, or editor action may hide a resource charge. | Behavior test `test_settlement_resource_cost_contract` proves open/preview/submit/revise/back-out/failure paths leave DP/AP/gold unchanged, accepted ratification follows the approved cost contract exactly once, and an insufficient-resource ratification path if a future non-zero cost is approved returns `success=False`, `mutated=False`, humanized copy, and no resource delta. Wizard and typed-entry tests prove `open_settlement` remains available at `DP=0` and does not show a ghost cost. |
| SC-1 | P0 | Open Settlement / `settlement_confirm` | Player can only ratify empty/no-clause common peace from normal UI. `main.gd`, `diplomacy_wizard.gd`, `_execute_propose_common_peace` (`backend/commands/diplomatic_executor.py:2041`), and settlement preview GET paths pass no `settlement_terms`; `GET /diplomatic_preview?mode=settlement` hard-codes `settlement_terms=[]` (`backend/main.py:2228`), while POST accepts terms but no normal UI calls it. The popup still presents settlement terms, acceptance pressure, awe, and revision affordances as if authored clauses exist. `build_settlement_review` masks empty packages by injecting a fake `End hostilities` Terms row at `backend/game_logic/settlement_presentation.py:806-808` (the rendered review fallback) AND `backend/game_logic/settlement_presentation.py:411-417` (`_term_display` fallback for unknown type strings). | Implement the approved full treaty path. Add a war-scoped draft editor and route populated packages through POST preview / staging. `_execute_propose_common_peace` must accept and forward `settlement_terms` and the authored `covered_enemy_participants` scope, and the Godot wizard/revision flows must use POST preview for populated packages before staging `propose_common_peace`. If SC-5 is explicitly reversed, incoming-offer promotion must use the same POST-preview package-preservation path; under the default defer-and-hide decision, incoming-offer no-exposure tests replace that path. The existing GET path may remain only as a read-only baseline, not the normal authoring route. Authored `{"type": "peace"}` clauses render as `type_display="Peace"` and `display_label="End hostilities (no material change)"`; empty `settlement_terms=[]` renders no Terms row at all. Remove BOTH `End hostilities` fallbacks (the `build_settlement_review` empty-`enriched_terms` path AND the `_term_display` no-`type` path) rather than relocating them. The editor layout is inline edit mode on the existing settlement review popup (`proposal_confirm_popup.gd::_build_settlement_content`); every live clause type must be reachable in one 1080p editor session without obscured scroll, and any non-live canonical clause type must be hidden with four-artifact interim-hide tracking. Additional requirements: editor validation errors render inline, Submit/Preview are disabled while errors exist, editor-mode ratification is absent, invalid clauses are not auto-stripped, and GET settlement preview must never stage, persist drafts, invalidate caches, or mutate world/dialogue state. | Editable behavior test: normal UI opens a draft editor, POST preview with a distinctive clause preserves `settlement_terms` and exact `covered_enemy_participants`, and acceptance differs from empty-package baseline by the expected harshness/effect component. Partial-scope test proves author -> preview -> revise -> submit -> ratify preserves a selected covered enemy list and keeps non-covered hostile participants at war. Empty-terms preview test proves no fake Terms row hides the no-clause state. Authored-peace render test proves bare `End hostilities` appears nowhere in Terms rows and `End hostilities (no material change)` appears only for authored `{"type": "peace"}`. Godot source/executable test proves every live clause-type structured control is reachable from the editor entry surface and hidden canonical clauses have interim-hide artifacts. Add a baseline test pinning today's `_execute_propose_common_peace(...)` empty-terms behavior so the cleanup decision has an enforceable before/after contract. Additional tests: max-clause/duplicate/conflict editor errors disable Submit until corrected, editor-mode ratification is absent, and 100 GET preview calls leave `dialogue_manager`, `pending_settlement_drafts`, `war_instances`, `diplomatic_states`, and caches unchanged. |
| SC-2 | P0 | `settlement_confirm` | `Revise Terms` does not revise terms. Verified anchors: `backend/game_logic/settlement_preview.py:409` (the `Revise Terms` option emitted from `build_settlement_confirm_dialogue`), `backend/game_logic/settlement_preview.py:1249` (`revise_settlement_terms` handler — `world.dialogue_manager.pop()` runs, then returns `must_reopen=True` plus a dead-letter `settlement_terms` echo that no client reads), `godot-client/project-sovereign/scripts/main.gd:934` (the `must_reopen` branch — calls `_on_war_settlement_clicked(rt_war_id, rt_nation)` which sends a fresh `propose_common_peace` body with no `settlement_terms` field). `_on_war_settlement_clicked` has no terms argument and the structured POST body has no `settlement_terms` field, so both surfaces must change together if revision is implemented. | Hide/remove, rename to review-only with explicit approval, or implement real draft mutation. If implementing, expose `can_edit_terms=true` plus a concrete `editor_route`; the editor opens with the staged package, lets the player change clauses, then re-previews acceptance before restaging. The Godot route must change with the backend: `settlement_clicked` / `_on_war_settlement_clicked` must accept draft `settlement_terms` or editor route metadata, and `send_structured_command` must forward that package in the POST body. If the action is hidden in the interim, the dead-letter `settlement_terms` field must also be removed from the `revise_settlement_terms` response so it does not advertise a missing capability. A pure "Review Again" loop is acceptable only with explicit product approval and visible value. Draft storage contract: unratified drafts live in `world.pending_settlement_drafts[draft_key]`, serialize through save/load, restore only for the same war/selected-target/covered-scope in the same turn, and are discarded on end turn, ratification, or explicit discard-confirm. | End-to-end revise test proving terms change/preserve into the next dialogue, or proving the action is absent from `dialogue.options` and removed from Godot settlement action lists. Add a test that asserts the structured POST body for `propose_common_peace` carries `settlement_terms` when the backend response provides them (currently absent). Source checks that only prove no command-box fallback are insufficient. Additional tests: scoped draft save/load round-trip preserves clauses; same-war different-scope drafts do not merge or clobber; end-turn discard removes unratified drafts; discard-confirm clears while cancel preserves. |
| SC-3 | P0 | `settlement_confirm` ratification | `Ratify Settlement` ignores displayed acceptance verdict and can mutate on rejection. Verified anchors: `backend/game_logic/settlement_preview.py:409` (always includes `confirm_settlement` today), `:469-470` (current revalidation checks proposer-side leader only), `:1044` (first-line gate), and `:1128` (`_apply_settlement_terms(...)` mutation entry). `revalidate_staged_settlement` does not recompute acceptance from current world state. The current scorer payload uses `accept_threshold`; the cleanup contract standardizes on `threshold` before presentation/ratification consumers read it. | Ratification must call `calculate_common_peace_acceptance(...)` fresh from current world state immediately before the gate. `confirm_settlement` is absent from `options[]` and `available_action_ids[]` when the fresh verdict is `reject` / `blocked`, score is below `acceptance.threshold`, or hard stops exist. Backend must enforce the same gate before mutation, including accepting-side leader changes that rescore below threshold. Additional requirements: scorer returns `threshold`; either rename current `accept_threshold` to `threshold` or explicitly alias it in the accepted payload before any SC-3 consumer reads it; no settlement file hardcodes accept/near thresholds outside scorer tuning; rescore failure uses `acceptance_changed_after_staging` and keeps the dialogue mounted with refreshed acceptance when possible; blocked-ratification popup shows the Voice Bible 16.1 blocker banner and refusal/blocked voice with reduced controls. | Direct behavior test: stage or synthesize a rejected/hard-stopped or newly rescored-below-threshold settlement, call `ratify_settlement_confirm`, and assert `success=False`, `mutated=False`, unchanged `world.diplomatic_states`, `war_instances`, `active_treaties`, `regions[*].controller`, `nation_relations`, `coalition_threat`, and `event_log` except approved refusal feedback. Additional tests: acceptance payload includes non-null `threshold` even when current scorer internals still expose `accept_threshold`; literal-threshold scan rejects hardcoded 50/35 outside scorer; score 51 -> world change -> score 49 returns `acceptance_changed_after_staging` with refreshed acceptance or valid reopen; rejected popup shows the blocked-ratification banner, omits `confirm_settlement` from `options[]` and `available_action_ids[]`, and suppresses "Will they accept" framing. |
| SC-4 | P0 | `settlement_confirm` hard stops | Red `HARD_STOP` warnings can be displayed while `Ratify Settlement` remains available and mutates. Same anchor set as SC-3 (`backend/game_logic/settlement_preview.py:409`, `:1044`, `:1128`) — treat as the hard-stop slice of the same gate. | Omit `confirm_settlement` from `options[]` and `available_action_ids[]` when hard stops exist, and enforce the same block server-side before mutation. The hard-stop check must run inside the same `revalidate_staged_settlement` gate that SC-3 uses, so a single fix site closes both rows. | Payload test for absent ratify option plus direct handler test with `score=10` AND `hard_stops=["coverage_violation"]` proving either condition is sufficient to block mutation, even if the client calls `confirm_settlement` directly. |
| SC-5 | P1 | Incoming settlement offers | `incoming_settlement_offer` is registered in `DialogueManager` hard-stop/mailbox taxonomy, mailbox labels, Godot popup type lists, and handler tests, but there is no gameplay producer and no mailbox/pending-envoy settlement popup payload path. Verified anchors: `backend/game_logic/settlement_preview.py:1276` (handler comment "as of Slice F there is no producer of `incoming_settlement_offer` dialogues yet"), `godot-client/project-sovereign/scripts/proposal_confirm_popup.gd:55` (popup match arm `"settlement_confirm", "incoming_settlement_offer": _build_settlement_content(data)`). The current producer audit finds the type only in taxonomy/state/dispatch/handler scaffolding, not in natural gameplay production. | Implement AI offer production plus settlement-specific mailbox/popup payloads this cleanup, or hide/remove all player-facing registration until a producer lands. Deferral takedown list: remove from `CURRENT_TURN_OFFER_TYPES` / mailbox count, `MAILBOX_SUMMARY_LABELS`, `DIALOGUE_PRIORITY`, any hard-stop/mailbox registration if present, Godot `PROPOSAL_CONFIRM_DIALOGUE_TYPES`, Godot `SETTLEMENT_DIALOGUE_ACTIONS` offer actions, the proposal-confirm settlement match arm for incoming offers (`proposal_confirm_popup.gd:55`), and settlement offer dispatch/player-facing routes. The handler may remain only if dead from normal gameplay and covered by tests. | If deferred, tests prove `incoming_settlement_offer` cannot increment mailbox count, block turns, or activate from `/mailbox`. If implemented, production-emitter test outside debug plus `/pending_envoy` and `/mailbox/activate` tests proving active and queued offers return populated settlement review payloads and options. |
| SC-6 | P1 | Incoming offer actions | `Request Revision` is a false revision affordance; accept/reject/request must not use stale or generic popup payloads. Verified anchors: `backend/game_logic/settlement_preview.py:1298` (`request_settlement_revision` handler — pops dialogue, returns `must_reopen=True`, no editor/counter route), `backend/game_logic/settlement_preview.py:1326` (`accept_settlement_offer` calls `stage_settlement_confirm(world, war_id=war_id, actor_nation=actor, density="medium")` with NO `settlement_terms` or `covered_enemy_participants` from the offered dialogue). Existing `tests/test_settlement_ui_slice_f_behavior.py::test_handle_incoming_offer_accept_restages_settlement_confirm` asserts successful restaging and dialogue type replacement, but does not assert package/clause preservation because the offer fixture carries no distinctive terms; the test must be augmented with a distinctive offered clause and a `settlement_terms` preservation assertion before SC-6 can pass. Incoming offers also need different player-facing copy than outgoing settlement review. | Implement real counterproposal/revision flow, or hide request revision. Every offer action must address a stable `offer_id` and exact offered package. Accept promotes through live preview with `offer_id`, proposer/accepting sides, covered enemies, and offered terms preserved and revalidated, or returns a visible stale error. Reject marks only that offer rejected and removes it without touching other offers or rebuilding a generic popup. Request Revision opens a counter/editor seeded from that offer's exact clauses and records revision/cooldown state against the same `offer_id`, or the action is hidden. Incoming-offer rendering must not ask "Will they accept?" when the player is the accepting side; if incoming offers are deferred, remove `incoming_settlement_offer` from the popup type list (`proposal_confirm_popup.gd:55`). | Incoming-offer behavior test for accept/reject/request plus `/pending_envoy` and `/mailbox/activate` payload tests. Distinctive-offer tests with `offer_id`, sides, covered enemies, and a clause such as `territory_cede: France->Britain, Belgium` prove accept preserves the package into `settlement_confirm` and acceptance harshness, reject removes only that offer with no mutation, and request revision opens a counter/editor seeded with the same package or is absent. Rendering test proves incoming-offer heading uses incoming-offer voice/copy or the type is absent. |
| SC-7 | P1 | Mailbox / envoy routes | `/pending_envoy` and `/mailbox/activate` count settlement offers through mailbox taxonomy but only build popup payloads for ordinary proposals. There are currently zero settlement-offer branches that build a `build_settlement_review`-shaped payload. Activating an injected `incoming_settlement_offer` can return success with no settlement popup data, pushing Godot toward generic alert-missing copy. | Build settlement-offer popup payloads in both endpoints or keep settlement offers out of mailbox taxonomy. If hidden, `/mailbox/activate` must defensively reject any stale/injected `incoming_settlement_offer` item instead of returning a generic success, and `/pending_envoy` must not advertise it. | API tests proving active and queued `incoming_settlement_offer` either return populated settlement review payloads and options, or never appear in mailbox count/items while deferred; defensive activation test rejects injected records. |
| SC-7b | P1 | Incoming offer accept failure | `handle_incoming_settlement_offer_action(... accept_settlement_offer ...)` pops the offer on missing/invalid `war_id`, returns `must_reopen=True`, and omits `reopen_target`. Verified anchor: `backend/game_logic/settlement_preview.py:1313-1324` — `world.dialogue_manager.pop()` runs and the response sets `must_reopen=True` with no `reopen_target`. Godot's `main.gd:934` must-reopen branch then reports "the backend did not provide a valid target", leaving no popup, mailbox row, or recovery path. Existing `tests/test_settlement_ui_slice_f_behavior.py::test_handle_incoming_offer_accept_with_empty_war_id_signals_must_reopen` asserts `success=False`, the error code, and `error_display` presence, but does not assert non-empty `reopen_target` or mounted-dialogue recovery; SC-7b cannot pass until that test asserts a non-empty `reopen_target` AND `error_display`, OR proves the dialogue stayed mounted with humanized error copy. | Implement stale-offer recovery. Derive `reopen_target` from offer identity before popping, or do not pop the dialogue when the offer cannot be promoted. The player must see a humanized stale/invalid-offer state with a safe route back or a visible close path. If incoming offers are hidden while authoring work lands, tests must prove this path is unreachable from gameplay. | Behavior test: stale incoming offer accept either returns non-empty `reopen_target` and `error_display`, or leaves the dialogue mounted with `success=False`, `mutated=False`. Godot test proves the missing-target dead-end text is not emitted for settlement-offer accept failures. |
| SC-8 | P1 | Diplomacy wizard multi-war entry | Wizard chooses `sorted(common_wars)[0]` for Open Settlement when the same nation shares multiple wars. Verified anchor: `backend/game_logic/diplomacy.py:9821-9826` (`common_wars = sorted(player_wars & target_wars); settlement_war_id = common_wars[0] if common_wars else None`). | Replace the auto-pick with either a war chooser carrying `available_wars[]`, or `available=False` plus a humanized "select a specific war from war detail" reason. War detail can remain the disambiguated path because it already carries `war_instance_id`. The wizard render path must not show a single `Open Settlement` button for a multi-war target. | Behavior test that multi-war shared pairs expose a chooser state or hide the action with humanized reason; single-war shared pair remains directly available. |
| SC-8b | P1 | Typed/free-text common-peace entry | `propose common peace with <nation>` can enter `_execute_propose_common_peace` without `war_id`. Verified anchor: `backend/game_logic/settlement_helpers.py:1924` (`existing = _find_active_war_instance_for_pair(world, pair)` — returns the first active match by iteration order when no `war_id` is supplied). Existing baseline `tests/test_settlement_ui_slice_f_behavior.py::test_resolve_without_war_id_falls_back_to_legacy_path` pins this behavior and must be inverted in Gate 3 before SC-8b can pass. | Reject ambiguous no-`war_id` settlement commands with humanized copy and `available_wars[]`, or route to the same chooser used by the wizard. Do not silently pick a war by sorted id, dict insertion order, or legacy fallback. The single-shared-war path stays valid. | Behavior test with two France/Austria shared wars calling the executor without `war_id`; assert `success=False`, `mutated=False`, and message names the ambiguity / asks the player to choose a specific war. |
| SC-9 | P2 | Diplomacy wizard default-start/backfill | Disabled reason can say one-to-one war when the real condition is missing/default war-instance plumbing because the no-common-war fallback maps to `one_to_one_war`. This can mislabel a multi-party/default-start war that simply lacks a `war_instance` record. | Dry-run/backfill enough to report the true reason, or let executor return the real error. Do not use `one_to_one_war` as a catch-all for "no current shared war instance"; introduce a humanized missing/backfillable war-instance reason if needed. | Required behavior test: `test_default_start_war_without_instance_shows_real_disabled_reason_not_one_to_one` proves multi-party/default-start war-instance gaps do not display one-to-one copy and instead show the real backfill/war-state reason. |
| SC-10 | P1 | Diplomacy wizard / war detail / war-status rows | Common-peace controls must appear only for multi-party settlement-eligible war contexts. `war_status.py` currently risks deriving `settlement_available` from unique nation count through `is_common_settlement_worth_showing`, which can remain true after a partial settlement leaves only one active hostile pair. `backend/game_logic/diplomacy.py` also appends `Open Settlement` for every `WAR`, including one-to-one wars where the correct player action is Bilateral Peace / Armistice. | War-status row construction and diplomacy-wizard settlement availability must call `evaluate_open_settlement_eligibility(world, war_id=..., actor_nation=player)` or an equivalent non-mutating active-pair eligibility helper, not unique-nation count or raw `WAR` state. If cached, eligibility must invalidate on `world.invalidate_war_instance_indexes()` or an equivalent same-turn hook and cannot survive partial settlement / pair resolution / merge / archive. When Settlement is hidden on a one-to-one wizard, row, or detail surface, eligible Bilateral Peace (`propose_peace`) and Armistice (`propose_armistice`) controls remain reachable on that same surface through structured commands. | Backend behavior test: 4-party war with all but one hostile pair resolved yields `settlement_available=False` in `build_active_wars`, matching eligibility helper. Same-turn invalidation test proves a cached value refreshes after partial settlement. Godot executable/source guard that ineligible war detail omits settlement CTA. Wizard one-to-one behavior test proves `Open Settlement` is absent or hidden on one-to-one WAR while structured Bilateral Peace / Armistice substitutes remain available. |
| SC-11 | P1 | Coalition detail | `Open Whole-War Settlement` appears whenever rows share a war id, without checking each row's `settlement_available` / backend eligibility. Verified anchors: `godot-client/project-sovereign/scripts/war_detail_popup.gd:97` (`_add_settlement_button(shared_war_id, _current_nation, ...)` is gated only on `shared_war_id != ""`), `:478-489` (`_shared_coalition_war_id` returns the shared id when every in-coalition row matches; no per-row `settlement_available` check). | Gate by the shared war's settlement eligibility across included rows. `_shared_coalition_war_id` must require every in-coalition row to have `settlement_available=True` before returning a non-empty id. If any included row is ineligible, hide the CTA or show an approved humanized reason; do not make the player click through to backend failure. | Behavior/source test that degenerate one-to-one or otherwise ineligible coalition detail hides whole-war settlement; row fixture with one `settlement_available=False` must not render `Open Whole-War Settlement`. |
| SC-11b | P1 | Coalition detail selected target | `show_coalition()` sets `_current_nation` to the coalition leader and emits that value as `target_nation` for `Open Whole-War Settlement`, even when the player entered detail from a different member. Verified anchor: `godot-client/project-sovereign/scripts/war_detail_popup.gd:83-99` (`show_coalition` line 85 sets `_current_nation = str(coalition_data.get("leader", ""))`; line 99 `_add_settlement_button(shared_war_id, _current_nation, "Open Whole-War Settlement")` emits the leader as the selected target). War-id resolution may still work, but copy, offer identity, and stale/revise reopen targets can name the wrong court. | Coalition settlement entry must pass structured context: `war_id`, `covered_enemy_participants[]`, and `selected_target_nation` derived from the focused member or an explicit chooser. Do not auto-pass coalition leader as the selected target unless the leader is actually the selected enemy. | Coalition fixture with leader=Russia and focused member=Austria; clicking whole-war settlement stages/reopens `selected_target_nation == "Austria"` or opens a chooser, never silently targets Russia. |
| SC-12 | P1 | Coalition detail multi-war state | Multi-war coalition shows a static explainer label instead of actionable per-war settlement routes. Verified anchor: `godot-client/project-sovereign/scripts/war_detail_popup.gd:455-463` (`_add_coalition_settlement_explainer` adds non-clickable copy). | Replace dead-end label with one settlement button per eligible coalition war. When SC-11b focused row is set, the focused enemy per-war button is primary and other eligible per-war buttons are secondary; without focus, all eligible per-war buttons render at equal weight. If the focused row is ineligible, render it disabled with `disabled_reason_display` and still show eligible secondary buttons; if no row is eligible, use approved hidden/no-action copy with alternate war-detail affordances. Interim no-action copy is allowed only with approved deferral and clickable `Open war detail` affordances per eligible war. | Behavior test that multi-war coalition emits actionable routes per eligible war, with focused enemy primary and others secondary, each carrying clicked `war_id` and `selected_target_nation`; or approved hidden/no-action copy with alternate route instructions. Focused-ineligible fixture: Austria disabled with reason while eligible Russia remains actionable as secondary. |
| SC-13 | P1 | Reopen target | `_reopen_target` uses first covered enemy, which can alphabetically change the player's selected context. `build_settlement_confirm_dialogue` currently emits no top-level `selected_target_nation`. | Store and preserve the player-selected enemy/route target in the staged dialogue as `selected_target_nation`, and preserve authored `covered_enemy_participants` as the settlement scope. Both fields are populated by wizard, war-detail, coalition-detail, typed/free-text unambiguous command, notification reopen, dispatch reopen, result-feedback review, and incoming-offer promotion if SC-5 is reversed. `_execute_propose_common_peace`, `_on_war_settlement_clicked`, `diplomacy_wizard.gd` structured payloads, `war_detail_popup.gd` settlement signals, coalition `_add_settlement_button`, notification handlers, and dispatch handlers must write both fields into the structured request and staged dialogue. `build_settlement_confirm_dialogue(...)` refuses production staging when selected target or covered-enemy scope is empty. `_reopen_target` must read selected target first, fall back to the accepting leader only when no selection exists, and never use alphabetic first covered enemy as the normal path. | Entry-path matrix test runs every production emitter and asserts `dialogue["selected_target_nation"]` equals the focused enemy and `dialogue["covered_enemy_participants"]` equals the authored scope. Guard test fails if a production staged dialogue omits either field. Revise/stale reopen preserves original selected target and covered-enemy scope, not alphabetic first covered enemy or recomputed all-enemy scope. |
| SC-14 | P1 | Result feedback / notification route focus | Settlement result feedback and notification handling can collapse active `settlement_review` routes into `ledger_settlements`, even when `war_ended=False`; `main.gd` currently flattens both review targets into `open_diplomatic_ledger_review("ledger_settlements", ...)`. | Mirror the event-side route decision: active war review/war-detail/live-settlement route for `war_ended=False`, archived ledger route for ended wars. `war_ended=False` payloads must carry `review_target="settlement_review"` distinct from `ledger_settlements`; Godot notice/result handlers must dispatch each branch to its own surface instead of flattening it. | Test that `war_ended=False` opens exact active war context and `war_ended=True` opens archived ledger row, covering result feedback and notification click paths. |
| SC-14b | P2 | Stale-state recovery | `settlement_confirm` is a hard stop, and repeated `must_reopen` responses can restage into the same stale condition or strand the player if the popup is gone/invisible. There is no call-site attempt counter in Godot today. | Add an explicit stale-recovery escape: irrecoverable validation errors pop or offer `Back Out`; Godot and backend cap repeated reopen attempts with `SETTLEMENT_REOPEN_MAX_ATTEMPTS = 3` per `(war_id, turn)`. Attempts 1-3 may reopen with a valid target; attempt 4 returns `must_reopen=False`, humanized copy, and a structured `recovery_route` to active War Detail or archived Settlement History. | Behavior test that a permanently stale staged dialogue cannot produce an infinite reopen loop; attempt 4 stops reopening, clears/escapes the stale dialogue, and leaves the player with the pinned clickable path out. |
| SC-14c | P1 | Route id uniqueness / source of truth | Settlement route ids currently use `{war_id}:{turn}`, which can collide for two same-war settlement events in one turn and focus the wrong ledger row/notification. Verified anchor: `backend/game_logic/settlement_preview.py:376` (`route_id = f"{war_id}:{int(getattr(world, 'current_turn', 0) or 0)}"` in `build_settlement_confirm_dialogue`); `:1183-1187` (ratify falls back to the same `f"{war_id}:{turn}"` format). The staged dialogue route id and post-ratification feedback can also diverge because result feedback prefers the reaction summary route id. | Route ids must be unique within a turn while still carrying `war_id`; include a monotonic settlement sequence, event id, or equivalent stable suffix. Compute one stable route id once at staging time and persist it through staging, reaction event, result feedback, dispatch, notification meta, and ledger row. Do not rely on turn number alone or recompute incompatible ids later. | Behavior test that two same-turn settlement events for the same `war_id` produce different `route_id` values and each route focuses the correct row. Continuity test proving staged dialogue, summary event, result feedback, notification meta, and ledger row all share the same id for one ratification. |
| SC-14d | P1 | Recent Settlements row cap | `recent_settlement_summaries` defaults to five rows. Verified anchors: `backend/game_logic/settlement_presentation.py:60` (`SETTLEMENT_LEDGER_DEFAULT_ROWS = 5`), `:1127` (`recent_settlement_summaries(world, player_nation, *, limit: int = SETTLEMENT_LEDGER_DEFAULT_ROWS)`). A clicked/focused settlement outside that cap can be silently absent from the ledger section, so route focus opens to no matching row and gives no overflow affordance. | Focused settlement rows must not be trimmed. Either raise/bypass the cap when `route_id` or `war_id` focus is supplied, sort focused rows to the front before capping, or emit a humanized overflow/expander row that carries the focus link. The cap constant may stay at 5 for the default render, but the focused-row override must run before the trim. | Fixture with seven same-turn settlement events and focus on the seventh; recent-settlement output must include the focus row or an actionable overflow row, and Godot focus must not open an empty section. |
| SC-14e | P2 | Cross-turn dispatch re-read | Dispatch re-read can store settlement route ids that no longer exist in the rolling Recent Settlements window or whose war has since archived. Clicking an old dispatch settlement line can open ledger focus to nothing. | Re-resolve stale dispatch clicks by `war_id` and current archival state, or surface "this settlement is no longer in the recent window" copy instead of opening a blank focused ledger. Old route ids must fail gracefully. | Cross-turn route test: an aged-out dispatch settlement click either resolves to a valid current/archived row by `war_id` or returns humanized no-longer-available copy; it never opens an empty focus. |
| SC-15 | P1 | Result popup / live review content | Player must know resolved pairs, unresolved pairs, beneficiaries, ignored/shut-out participants, accepted/rejected reasons, mutated clauses, and live set-piece/awe stakes. Current preview does not explicitly explain beneficiary reasons, ignored coalition members, or the exact mutations each clause will perform; live preview also passes `awe_tags=[]`, so awe-tag UI is dead before ratification. Archived settlement review also loses the ratification-time acceptance verdict because event review is built with `acceptance=None`, and pre-ratification overflow copy can promise warnings are "in the ledger" before they exist there. | Add explicit sections: `beneficiaries[]` with reason, `shut_out_allies[]` / ignored participants, `applied_clauses_preview[]` naming mutations, unresolved/remaining-war rows, full blocker details when rejected/blocked, live `awe_tag_displays` from settlement set-piece detection, and an `acceptance_snapshot` on post-ratification `settlement_summary` events. Pre-ratification overflow must expand inline or use neutral copy such as "+N more concerns"; it must not promise ledger access before ratification. | Presentation tests for resolved/unresolved pairs, beneficiaries and reasons, ignored parties, hard-stop reasons, applied/mutation-preview clauses, and a live awe fixture proving `build_settlement_preview` emits `review_sections.awe_tag_displays` before ratification. Archived recent-settlement test proves acceptance is preserved and rendered. Popup overflow test proves pre-ratification copy does not say hidden warnings are already in the ledger. |
| SC-15b | P2 | Blocked acceptance display | Structurally blocked settlement acceptance can render like a numeric low-score proposal, e.g. `0 / 50 - Blocked`, which suggests score tuning rather than a hard impossibility. | Backend acceptance payloads with `band == "blocked"` must omit `total` and `threshold` or set both to `null`, and must populate `band_display="Blocked"` plus a humanized blocker display. Popup, tooltip, ledger, dispatch, and future surfaces must read this same payload contract rather than each suppressing numeric blocked copy separately. | Backend payload test proving blocked acceptance has no numeric `total` / `threshold` and carries blocker display; render test proving no surface shows `0 / 50` or `\d+ / \d+ - Blocked`. |
| SC-16 | P2 | Pre-ratification political cost | Forced-alliance threat, projected hegemony, and balance impact are not clearly surfaced before ratification. These are essential for the approved full treaty path because authored clauses can change political cost. | Surface threat delta / balance projection when terms can cause those effects. If a term type is temporarily unavailable, hide its controls instead of showing dead projection rows. | Payload/render test for forced-alliance term showing threat delta and balance projection rows; unavailable-term test proving hidden controls do not leave dead projection rows. |
| SC-17 | P2 | Raw labels/debug copy | Raw ids/enums and debug strings can leak. Verified anchors: `backend/game_logic/settlement_preview.py:377` (`talleyrand_text = f"Review the settlement of {war_label}. Acceptance: {verdict} ({score if score is not None else 'blocked'})."` — leaks raw verdict enum like `near_acceptable`), `godot-client/project-sovereign/scripts/proposal_confirm_popup.gd:178-184` (`Settlement payload incomplete: missing ...` developer text), `backend/game_logic/settlement_presentation.py:864-866` (`war_scope_display = "Bilateral row"` raw label), `backend/game_logic/settlement_presentation.py:372-385` (dispatch `_humanize_term` strips underscores instead of using `clause_display_name`), `backend/game_logic/settlement_preview.py:407` (production payload field named `debug_action_ids`). | Humanize every player surface. Malformed payloads should fail gracefully or be rejected before popup with player copy such as "We could not prepare this settlement review; please reopen from war detail." Dialogue copy must use acceptance band display/phrase and settlement voice, not raw verdict enums. Replace "Bilateral row" (`settlement_presentation.py:865`) with player copy. `_humanize_term` (`settlement_presentation.py:372-385`) must delegate type labels to `clause_display_name(ttype)`; only the unknown-type path may fall back to underscore-stripping. Every warning/hard-stop row reaching Godot must carry `code_display` and `detail`; the popup must not use raw-enum capitalization as production fallback. Rename `debug_action_ids` to `available_action_ids` derived at emission time from `options[]` (`[opt["action"] for opt in options if opt.get("available", True)]`), or remove it if unused. | Raw-enum scan plus behavior fixture for malformed settlement payload copy; staged-dialogue test that `talleyrand_text` contains no raw acceptance enum (`near_acceptable`, `reject`, `blocked`, `acceptable`, `accept`); hard-stop fixture with raw codes proving rendered BBCode uses humanized copy; scope-copy test rejects "Bilateral row"; dispatch term test for a `territory_cede` term proves the rendered text uses `clause_display_name("territory_cede")` (not `territory cede`); payload tests proving `debug_action_ids` is absent or replaced with an options-derived production key and `test_available_action_ids_is_derived_from_options_array` proves equality with available `options[]`. |
| SC-18 | P2 | Command fallback / malformed popup routing | Generic proposal-confirm fallback can synthesize natural-language commands for unknown actions; current settlement protection depends on a local `SETTLEMENT_DIALOGUE_ACTIONS` whitelist that can drift. Verified anchors: `godot-client/project-sovereign/scripts/main.gd:29` (`const SETTLEMENT_DIALOGUE_ACTIONS := [...]` whitelist), `:3068` (`if action in SETTLEMENT_DIALOGUE_ACTIONS:` guard inside `_on_proposal_confirm_choice`), `:3098` (`var command = "Talleyrand, %s the %s proposal" % [keyword, target]` natural-language synthesis fallback). Settlement payloads often lack `target_nation`, so the fallback can synthesize `Talleyrand, <action> the Unknown proposal`. Backend hard-stop free-text fallback remains in scope for family-level settlement safety. | Guard by dialogue family/type before any fallback: if `data.type` / `dialogue_type` is `settlement_confirm` or `incoming_settlement_offer`, never synthesize `send_command`, regardless of action id. The family-level guard must run BEFORE the whitelist check at line 3068 — an unknown settlement action id in either family must re-show the popup or surface a hard UI error, not fall through to line 3098. Validate settlement payloads before opening the popup; missing required settlement fields should show humanized "could not prepare review" copy or keep the prior route, not a developer warning or generic proposal popup. Canonical family home: backend owns `backend/models/dialogue_manager.py::SETTLEMENT_FAMILY_DIALOGUE_TYPES`, and Godot mirrors it as `SETTLEMENT_FAMILY_DIALOGUE_TYPES`. | Godot handler test with malformed/new settlement option proving no `send_command` fallback even if action id is absent from a local whitelist; fake `frobnicate_settlement_terms` action in `dialogue_type=settlement_confirm` must not emit "Unknown proposal" command text. Popup-route test proves malformed settlement payload is rejected/humanized before display. Backend hard-stop test proving unknown settlement response does not execute arbitrary parsed command fallback. Source scan proves every backend family type exists in the Godot mirror and every Godot member exists in the backend constant. |
| SC-19 | P1 | Settlement voice / perspective | Settlement heading is hard-coded mechanical copy instead of the settlement voice family, and incoming-offer copy reuses outgoing "Will they accept?" framing. Verified anchors: `backend/game_logic/settlement_preview.py:377` (`talleyrand_text = f"Review the settlement of {war_label}. Acceptance: {verdict} ({score if score is not None else 'blocked'})."` — raw verdict f-string), `godot-client/project-sovereign/scripts/proposal_confirm_popup.gd:194` (shared `[b][color=#e0c070]Will %s accept this settlement?[/color][/b]` heading branch used for both `settlement_confirm` and `incoming_settlement_offer`). Foreign-court fog-visible settlements also route through Talleyrand-family summary copy even when France is neither proposer nor accepting member. | Use backend-resolved settlement voice line for outgoing review. If incoming offers ship, give them a separate incoming-offer voice/template or backend-resolved heading branch; if deferred, remove incoming-offer popup routing. Cross-court fog-visible settlement summaries must use chancery/observer voice, not French Talleyrand authorship. At minimum, humanize the verdict with `acceptance_band_display`, but the full fix is Voice Bible 16.1 settlement family copy. Voice Bible 16.1 copy for each required settlement family must be authored, reviewed, and committed as production copy; placeholder strings, TODO copy, or helper fallback text fail this row. Required rejected/loss families include `settlement_blocked_for_ratification_talleyrand`, `settlement_open_war_detail_recovery_talleyrand`, `settlement_open_history_recovery_talleyrand`, `settlement_no_alternative_route_chancery`, and `settlement_concession_authored_talleyrand`. | Presentation/render test that heading comes from settlement voice copy for common-peace review, staged `talleyrand_text` contains no raw verdict enum (`near_acceptable`, `reject`, `blocked`, `acceptable`, `accept`), incoming-offer heading does not use outgoing acceptance framing, a foreign-only visible settlement does not use Talleyrand-family copy, and `test_voice_bible_section_16_1_contains_authored_copy_for_each_required_family` / `test_settlement_voice_family_routing_table_covers_rejected_path` fail on missing, placeholder, or wrong-trigger voice strings. |
| SC-20 | P2 | Acceptance phrase consistency | Acceptance band display and phrase can produce awkward duplicate copy such as "Unlikely (Likely to reject)." The current render appends phrase whenever it differs from display, and they differ for negative/near bands by design. | Either show phrases consistently or stop carrying redundant phrases; choose one source of player-facing acceptance wording per band. | Parametrized presentation/render test across accept, near, unlikely, reject, blocked proving exactly one acceptance label/phrase is rendered. |
| SC-21 | P3 | Behavioral tests | Slice F tests rely heavily on source-string assertions. Source guards prove text is present, not that actions execute or mutate/block correctly. Verified anchors include `tests/test_settlement_ui_slice_f_source.py:172`, `tests/test_common_peace_c2_preview.py:101`, `tests/test_common_peace_c2_preview.py:116-120`, `tests/test_settlement_ui_slice_f_behavior.py:143-154`, `tests/test_settlement_ui_slice_f_behavior.py:626-640`, and `tests/test_settlement_presentation.py:1173-1178`. | Add behavior twins for each source-string guard or retire weak source-only coverage. Each slice closure must list exact `test_<name>` functions to invert/retire with file references, including no-`war_id` fallback, exact `{war_id}:{turn}` route ids, archived empty acceptance sections, empty-term completion, `debug_action_ids`, and the `_reopen_target` first-covered fallback. | Tests fail if a button is present but signal/action does not execute the named behavior; direct tests cover SC-2 revise preservation/absence, SC-3/SC-4 fresh rejection/hard-stop block, SC-6 incoming-offer package preservation, SC-7/SC-7b stale recovery, SC-8/SC-8b disambiguation, SC-13 selected-target-first reopen, SC-14c/SC-14d route focus, SC-15/15b content, SC-17 raw-label scan, SC-18 family guard, and SC-26 cross-war collision. Required coverage includes baseline `test_reopen_target_falls_back_to_first_covered_today`, then inversion to `test_reopen_target_reads_selected_target_nation_first`. |
| SC-22 | P3 | Godot parse/load coverage | Critical settlement scripts can regress at parse/load/signal level without CI failure. Settlement-touching scripts on every cleanup slice include `main.gd`, `diplomacy_wizard.gd`, `war_detail_popup.gd`, `proposal_confirm_popup.gd`, `diplomatic_ledger.gd`, `top_bar.gd`, `notification_bar.gd`, and `mailbox_panel.gd`. | Add headless Godot parse/load or executable harness. If Godot 4 headless `--check-only` or equivalent is unavailable in CI, explicitly document the tooling block in `docs/STATUS.md` AND require manual smoke (Gate 4 script) before any settlement-touching merge. The blocked-tooling deferral must be re-validated each slice; do not let it become silent permanent waiver. | `test_critical_settlement_scripts_parse_without_error` over all eight critical scripts above, OR explicit blocked-tooling evidence plus mandatory manual smoke recorded in `STATUS.md` for the slice. |
| SC-23 | P2 | Diplomatic ledger / dispatch peace sections | The ledger can expose both Recent Settlements and legacy Recent Peace Ratifications. Common-peace focus targets only the settlement branch, while bilateral peace uses the legacy branch, and the labels can read like overlapping outcomes. `diplomatic_ledger.gd` also leaves the header as `ACTIVE TREATIES` when opened to `ledger_settlements`, and Morning Dispatch can co-render bilateral `PEACE SETTLEMENTS` with common-peace event lines without a clear precedence/type distinction. | Merge into one reverse-chronological `PEACE & SETTLEMENT HISTORY` surface with row-level type tags. Each ratification event is its own row; per-war dedup is off. The combined default cap is `PEACE_HISTORY_DEFAULT_ROWS = 5` across common settlements and bilateral peaces. Route-id namespaces for settlement and bilateral peace must be distinct. When `_open_review_target == "ledger_settlements"`, the ledger header must name settlements/history, not `ACTIVE TREATIES`. Dispatch must use the same typed, deduplicated surface. | Mixed-history fixture with 3 common settlements and 3 bilateral peaces in interleaved turns renders the top 5 by reverse chronology with correct type tags. Settlement focus ids find settlement rows, bilateral focus ids find bilateral rows, and no event double-renders. |
| SC-24 | P2 | Treaty metadata harshness | Common-peace treaty records can use a different harshness scale than C1b acceptance scoring. This is mostly downstream metadata, but it can mislead ledger/AI readers if not explicit. | Store both raw common-peace harshness and legacy clamped harshness under separate fields. Raw consumers: `backend/game_logic/diplomatic_ledger.py`, `backend/game_logic/ai_diplomacy.py` proposal generation, `backend/game_logic/coalition.py` threat interpretation, `backend/game_logic/dispatch.py` one-liners, and `backend/game_logic/notifications.py` warnings. Legacy bilateral consumers may keep the clamped field. | Ratification test with multi-clause harshness greater than 1.0 proving treaty metadata stores raw and clamped values. Consumer-by-consumer tests assert each named common-peace consumer reads raw harshness, not the clamped field. |
| SC-25 | P1 | Settlement vocabulary | Player-facing copy currently mixes `Open Settlement`, common peace, treaty settlement, and typed `propose common peace` language. This lets implementation close routing while teaching the player three names for one flow. | Use **Settlement** as the player-facing route and feature term. `common peace` remains internal/backend terminology only; `treaty` describes authored clauses or stored records, not the top-level CTA. Update CTA labels, popup headings, voice templates, help/tutorial text, dispatch, ledger, and notifications to use the chosen vocabulary consistently while preserving backend type strings for save compatibility. `Open Whole-War Settlement` is allowed as a coalition scope qualifier; no CTA may use `Common Peace` or `Treaty` as the top-level label. Historical free-form `event_log[].message` text from old saves is not migrated and may render as historical text; new generated renders must use Settlement vocabulary. | Render/source scan proving one player view does not mix `common peace`, `settlement`, and `treaty` as interchangeable route names; CTA and voice-template tests proving the settlement route uses the chosen term. Coalition CTA test proves `Open Whole-War Settlement` and `Open Settlement` both route to the same editor contract. Old-save fixture proves old free-form messages render unchanged while new `compose_summary_oneliner`, dispatch, notification, and ledger text uses Settlement vocabulary. |
| SC-26 | P1 | Cross-war / same-war settlement collision | A second settlement entry can preempt the active `settlement_confirm` dialogue via `world.dialogue_manager.replace(dialogue)` (`backend/game_logic/settlement_preview.py:443-447`), silently clobbering the existing review. SC-5 default-defer mitigates incoming-offer collision only while incoming offers stay hidden; outgoing settlements can still race. Same-war restaging can also overwrite authored draft state. | `stage_settlement_confirm` must reject preemption when a different settlement-family hard-stop is already active for another `war_id`. Cross-war restaging returns `error="cross_war_settlement_collision"` with humanized "resolve current settlement first" copy; it is not queued through the mailbox. Same-war restaging refreshes the mounted dialogue and merges only non-conflicting authored draft terms through `pending_settlement_drafts`. If the merged draft would fail POST preview under the SC-1 conflict matrix, the merge returns `error="merge_conflict"`, names the offending clause in `error_display`, and preserves the active draft unchanged. The current dialogue must remain active unless the player backs out, ratifies, or explicitly chooses to replace it through an approved product flow. | Stage `settlement_confirm` for `war_1`, then call `_execute_propose_common_peace` for `war_2`; assert `war_1` remains active, `war_2` returns `cross_war_settlement_collision`, and no queue/defer/clobber occurs. Same-war tests: restage `war_1` with compatible authored `gold_indemnity` and prove merged draft; then restage with a conflicting clause and prove `merge_conflict`, humanized conflict copy, and active draft unchanged. Add same-family collision coverage for incoming offers if SC-5 is ever reversed. |
| SC-27 | P1 | Doc maintenance / supersession | `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` still contains older Slice F instructions that contradict this cleanup spec: route id format pinned as `settlement_summary:{war_id}:{staged_turn}` and minimal incoming-offer routing mandated for Slice F. Active `docs/STATUS.md` phase/next-step rows can also drift back to Slice F / Slice G / minimal incoming-offer instructions even when the lead status block is correct. A downstream implementer can read an older plan or current-status table first and reintroduce behavior this spec forbids. | Before Gate 2 Slice 1 starts, fold supersession callouts into the implementation plan or remove/replace the contradicting paragraphs. The route-id paragraph must be marked `SUPERSEDED BY SETTLEMENT_UI_CLEANUP_SPEC.md SC-14c`; the incoming-offer paragraph must be marked `SUPERSEDED BY SETTLEMENT_UI_CLEANUP_SPEC.md SC-5`. `docs/STATUS.md` must also record that those markers exist and every active current-phase / next-step row must name the cleanup spec as the next settlement gate, not Slice F, Slice G, or minimal incoming-offer routing. Historical STATUS entries may remain if clearly historical. | Source-string scan proves each contradicting implementation-plan paragraph is removed/replaced or carries the required same-line `SUPERSEDED BY SETTLEMENT_UI_CLEANUP_SPEC.md SC-*` marker. STATUS scan proves active current-phase / next-step rows do not point implementation at Slice F, Slice G, or minimal incoming-offer scaffolding before cleanup closure. |
| SC-28 | P1 | Rejected settlement / losing-side recovery | The rejected settlement popup can satisfy SC-3/SC-4 by removing Ratify but still fail player comprehension if no owned row defines the remaining action set, terminal close state, draft-preserving recovery behavior, and losing-side concession baseline. Direct popup-level `Seek Armistice`, `Seek Bilateral Peace`, disabled Ratify, disabled Revise, and `Wait for Enemy Offer` would reintroduce the same false-affordance class as `Revise Terms`. | Own the Rejected Settlement / Losing-Side UX Contract. Blocked ratify is absent, not disabled. The popup exposes only real settlement-family actions: edit/re-author when `can_edit_terms=true`, `Open War Detail` for active-war recovery, `Open Settlement History` for archived recovery, or terminal close copy when no target is recoverable. War Detail owns Bilateral Peace and Armistice. SC-5 defer-and-hide forbids enemy-offer waiting copy. Losing-side peace uses canonical concessionary clauses and the deterministic Talleyrand concession baseline. End-turn draft discard emits a one-shot player notice. Voice families include blocked-ratify, war-detail recovery, history recovery, no-alternative terminal copy, and concession-authored copy. | Behavior tests prove the recovery affordance schema, absent blocked ratify with banner/body reason, no enemy-offer wait while SC-5 is deferred, Open War Detail draft preservation without discard prompt, terminal no-alternative close copy, losing-side concession baseline reaching accept/near-accept in the smoke fixture, clause direction tags, peace-only losing hint, draft-discard notice after load, and required SC-19 voice-family routing. |
| SC-28b | P1 | Direct armistice / bilateral substitute CTAs | A rejected settlement popup could reintroduce the Revise Terms class miss by adding `Seek Armistice Instead`, `Seek Bilateral Peace`, or a disabled backlog variant without pair scope, eligibility helper, handoff payload, route/focus preservation, or tests. | During cleanup these direct substitute CTAs are absent. `Open War Detail` is the only active-war recovery route. The work lands in SC-29 / G2-Slice-7, not an unnamed placeholder. Until SC-29 ships, no popup payload, recommended alternative, disabled placeholder, mailbox hint, or Godot branch may expose the substitute labels. | Absence test `test_seek_armistice_instead_cta_absent_until_sc29_lands`. SC-29 owns the positive behavior tests. |
| SC-29 | P1 | Pair-scoped peace substitute CTAs | Hidden direct pair actions need a real implementation home so cleanup does not become permanent omission. | Implement G2-Slice-7 Pair-Scoped Peace Substitute CTAs from the Deferred Work Landing Ledger. Add `scope="selected_pair"`, payload `{action, war_id, selected_target_nation, scope}`, `evaluate_pair_peace_substitute_eligibility(world, *, war_id, actor_nation, target_nation, action)` or equivalent shared helper, SC-13 selected-target inheritance, SC-14b no-reopen-attempt consumption, SC-26 collision behavior, scoped-draft stale/invalidation rules, and SC-19 voice. | Required tests: `test_seek_armistice_instead_creates_per_pair_armistice_with_selected_target_only`, `test_seek_bilateral_peace_instead_creates_per_pair_peace_with_selected_target_only`, `test_pair_substitute_eligibility_helper_matches_backend_refusal_codes`, and `test_pair_substitute_handoff_preserves_or_invalidates_scoped_draft_correctly`. |
| SC-30 | P1 | AI settlement offer producer / request terms | `Wait for Enemy Offer`, `Ask for terms`, and incoming settlement offers are false affordances without an AI producer, cooldown, mailbox/pending-envoy lifecycle, package identity, and response handling. | Implement Slice G1 AI Settlement Offer Producer And Request Terms from the Deferred Work Landing Ledger before any wait/request/incoming-offer label appears. SC-5 remains defer-and-hide only until this row ships. | Required tests: `test_ai_settlement_offer_producer_surfaces_real_mailbox_payload`, `test_wait_for_enemy_offer_only_visible_when_offer_producer_and_cooldown_path_exist`, `test_ask_for_terms_creates_request_terms_state_or_humanized_refusal`, and `test_incoming_offer_accept_preserves_offer_identity_and_terms_through_live_preview`. |
| SC-31 | P1 | Dependency / surrender terms | `Surrender terms` implies dependency consequences and cannot ride on gold/territory concessions. | Implement G2-Slice-8 Dependency And Surrender Terms Restoration before `Surrender terms` copy, preset, command text, or mailbox labels can appear. This row owns live dependency clauses, losing-side surrender preset, preview/mutation/history/dispatch/ledger consequences, and voice. | Required tests: `test_surrender_terms_absent_until_dependency_clause_restoration`, then `test_surrender_terms_authors_dependency_clause_with_preview_and_mutation` and `test_surrender_terms_voice_and_history_explain_dependency_consequence`. |
| SC-32 | P2 | Settlement agency follow-through | Broader settlement-agency language can otherwise remain as vague Slice G intent. | Implement Slice G2 Settlement Agency Follow-Through. AI counterproposals, ally petitions/advisories, conference mechanics, veto-like systems, and voluntary alignment offers must either ship with payload/UI/voice/tests or be explicitly removed from player-facing scope in this spec and `docs/STATUS.md`. | Required test `test_settlement_agency_landing_ledger_has_no_unowned_backlog_controls`, plus per-action behavior tests before any agency CTA appears. |

### Binding Row Tightenings

These amendments tighten the table rows above and override any looser wording in the row body. They are the canonical source after the history-prose removal; no implementation checklist should cite removed review prose.

- **SC-1:** G2-Slice-1 includes losing-side peace-with-concessions in the live floor. `territory_cede` and `gold_indemnity` controls must support player-as-ceder and player-as-payer packages, preview must show direction displays, and `test_losing_side_authored_concession_draft_can_reach_accept_band_with_realistic_war_state` must prove a realistic losing-side concession can reach `accept` or `near_acceptable`.
- **SC-1:** Losing-side peace uses editor offer-mode on the canonical clause schema. Cleanup-scope concession presets use neutral labels such as `Generate concession baseline`; they are not incoming-offer waits, mailbox actions, new backend command text, or new clause types.
- **SC-1:** Cleanup-scope losing peace is player-authored concessionary clauses only. `Ask for terms` is owned by SC-30 and `Surrender terms` is owned by SC-31. Both labels must be absent from cleanup payloads and editor presets until their landing slices ship.
- **SC-1:** Settlement drafts are keyed by `draft_key`, not raw `war_id`. Same-war different selected targets or covered-enemy scopes must not merge or overwrite each other.
- **SC-1:** The editor acceptance panel shows previous band, current band, and delta after each POST-previewed clause commit. The player must see a package fall below threshold before Submit. Acceptance failure alone does not disable Submit for a structurally valid draft; it progresses to REVIEW with Ratify absent, blocked-copy visible, and edit/recovery controls available.
- **SC-1:** The first-slice `forced_alliance` control is demand-only. Losing-side offer mode hides it when it would imply the losing player can force the victor into alliance; "Offered alignment" is not a forced-alliance alias.
- **SC-1 / SC-3:** Rejected editor-mode and review-mode ratification use the same absent-ratify contract. If fresh acceptance or hard stops block ratification, no `confirm_settlement` option is emitted; the surface renders blocker copy plus edit/recovery controls.
- **SC-1:** The editor layout is the panel map in the Editor Layout Contract, not a loose "controls exist somewhere" requirement. Source/Godot checks must prove the header, clause package, clause controls, preview panel, and action rail exist and toggle between EDIT and REVIEW mode.
- **SC-1:** Clause commits trigger POST preview only after all required keys for that clause type are populated. In-progress clauses stay local and show incomplete validation. Required test: `test_clause_in_progress_does_not_trigger_post_preview_until_required_keys_populated`.
- **SC-1:** When a clause picker has zero valid options, the Add Clause control is disabled with `disabled_reason_display`; it does not open an empty picker or create an invalid draft. Required test: `test_clause_add_disabled_when_picker_filter_empty_for_each_canonical_clause`.
- **SC-1:** Editor and review rows display direction tags for authored clauses: `Demanded`, `Conceded`, or `Mutual`. Required test: `test_editor_renders_clause_direction_labels`.
- **SC-2:** Back Out from a draft with zero authored clauses pops the dialogue immediately without discard-confirm and without writing `world.pending_settlement_drafts`. Back Out from a non-empty authored draft uses discard-confirm.
- **SC-2:** Popup close via Escape key, window chrome, or clicking outside the modal is equivalent to Back Out and follows the same empty/non-empty discard path. No popup-close mechanism may bypass discard-confirm for a non-empty draft. Required test: `test_popup_close_with_non_empty_draft_triggers_discard_confirm`.
- **SC-2:** Save/load must not silently drop an in-flight settlement draft. If end-turn discard remains the product decision, loading a save after the discard must surface a notice such as "Last turn's settlement draft was abandoned at turn end. Reopen Settlement to start fresh." Required test: `test_load_after_end_turn_does_not_silently_drop_draft_without_player_signal`.
- **SC-2:** `Revise Terms` is absent until an edit-capable route exists. Required test: `test_revise_terms_is_absent_until_editor_lands`, failing if any payload contains `revise_settlement_terms` without editor capability and live `available_clause_types[]`.
- **SC-3:** Rescore failure must include an actionable delta payload: previous score/verdict, current score/verdict, threshold, changed hard stops, and top acceptance components that changed enough to explain the block. Required test: `test_rescore_failure_remount_includes_actionable_delta_and_top_components`.
- **SC-7b:** If SC-5 is reversed and incoming offers ship, stale incoming-offer reopen target preference is: valid `war_id` to war detail, proposer nation in the diplomacy wizard only if war detail is unavailable, then SC-14b choose-from-war-detail fallback. No stale incoming-offer path may return `must_reopen=True` with empty target.
- **SC-13:** If both `selected_target_nation` and `covered_enemy_participants` are empty, settlement-family reopen handlers return `must_reopen=False` with the SC-14b choose-from-war-detail fallback. They must not emit `target_nation=""` inside a `must_reopen=True` response.
- **SC-14:** Active-vs-archived route decisions resolve at click time. If a war archives between row render and player click, the click follows the current archived ledger/history branch.
- **SC-14b:** Attempt 4 after `SETTLEMENT_REOPEN_MAX_ATTEMPTS` must return a structured `recovery_route`: `{"surface": "war_detail", "war_id": str}` while the war is active, or `{"surface": "settlement_history", "route_id": str}` after archival. Godot renders this as `Open War Detail` or `Open Settlement History`; pure prose "choose from war detail" is not enough. Required test: `test_reopen_cap_attempt_four_returns_recovery_route_with_clickable_war_detail_target`.
- **SC-22:** Each slice closure entry in `docs/STATUS.md` must explicitly record shipped Godot parse/load or executable coverage, or a still-active tooling-block deferral with manual smoke evidence for that slice. Silent carry-over of the deferral fails the row.
- **SC-23:** Bilateral peace history rows are emitted by the bilateral peace ratification path, currently `_ratify_treaty(...)` / `cleanup_war_end(...)`, or its documented replacement. Bilateral route ids use a namespace distinct from settlement ids, such as `peace:{participants_signature}:{turn}:{seq}` versus `settlement:{war_id}:{turn}:{seq}`. Both producers write into the same merged ledger/dispatch surface.
- **SC-25:** Vocabulary scans include SC-19 settlement voice templates and backend-resolved settlement voice helper output. A settlement-family voice template must not use `Common Peace` / `common peace` as the top-level route phrase.
- **SC-25:** Vocabulary scans include editor structured-control labels and any clause-label registry added for the editor. Tests must fail if player-facing controls show internal field labels such as `from`, `to`, or enum-derived phrases such as `forced_alliance from`. Required test: `test_clause_editor_picker_labels_use_player_vocabulary_not_from_to`.
- **SC-26:** Same-war restaging merges only non-conflicting authored draft terms through `pending_settlement_drafts`. If the merged draft would fail POST preview under the SC-1 conflict matrix, the merge is rejected with `error="merge_conflict"`, humanized copy naming the offending clause, and the active draft preserved unchanged. Cross-war restaging during an active settlement-family hard stop is rejected with `error="cross_war_settlement_collision"` and humanized "resolve current settlement first" copy; it is not queued through the mailbox. AI-driven cross-war offers that hit this rejection retry next turn rather than creating a hidden mailbox defer.
- **SC-26:** Same-war merge conflicts render in the editor preview-panel banner with the offending clause highlighted and an explicit resolution choice: discard the new conflicting clause, or intentionally replace the active clause through an approved `Replace this clause` affordance. Required test: `test_same_war_merge_conflict_renders_inline_resolution_choice`.
- **SC-27:** The table row's two-example marker list is not sufficient. The doc-scan must fail if any paragraph in `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` containing `incoming_settlement_offer` lacks same-paragraph `SUPERSEDED BY SETTLEMENT_UI_CLEANUP_SPEC.md SC-5`, unless that paragraph has been removed/replaced or explicitly scoped to post-cleanup Slice G after SC-5 reversal. The doc-scan must also fail if any paragraph pins `settlement_summary:{war_id}:{staged_turn}` or another forbidden route-id shape without `SUPERSEDED BY SETTLEMENT_UI_CLEANUP_SPEC.md SC-14c`.
- **SC-27:** The doc-scan also covers `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md`, not only the implementation plan. Stale examples such as `settlement_summary:war_12:24`, `settlement_summary:{war_id}:{turn}`, or `settlement_digest:{war_id}:{turn}` must be removed, replaced with the staged `settlement:{war_id}:{turn}:{seq}` namespace, or superseded in the same paragraph by `SETTLEMENT_UI_CLEANUP_SPEC.md SC-14c`.
- **SC-27 / STATUS:** `docs/STATUS.md` must name the current cleanup spec version before implementation starts and must not claim SC-27 closure unless the current doc-scan passes. A STATUS line that still names an older audit pass as the current gate, or says all supersession markers exist while the scan fails, is itself a SPEC READINESS blocker.
- **SC-27 / STATUS:** Active `docs/STATUS.md` current-phase rows must match the latest landed cleanup-slice commit state before any new spec amendment or smoke pass. Required check: `test_status_md_current_phase_row_does_not_advertise_completed_slice_as_next`.
- **SC-27:** Fail if `tests/test_settlement_ui_slice_f_*` files still exist after `docs/STATUS.md` claims SC-27 or the cleanup spec is closed.
- **SC-1:** G2-Slice-1 cannot close as a peace-only editor. `peace`, `territory_cede`, `gold_indemnity`, and `forced_alliance` must be the required first-slice live clause floor, Submit must revalidate submitted terms before staging, `stage_settlement_confirm(...)` must receive explicit `caller_kind`, and territory picker control means `region.controller == from`.
- **SC-3:** Proposer-side and accepting-side leader changes share the same fresh-rescore rule; neither side causes automatic `must_reopen` when the rescored package still passes. The popup must render 0/1/2/3 settlement option counts gracefully.
- **SC-13:** `_execute_propose_common_peace` and `stage_settlement_confirm(...)` must explicitly forward and persist `selected_target_nation` and `covered_enemy_participants`; production staging fails closed if either required field is missing.
- **SC-14:** "Mounted" means current hard-stop `settlement_confirm` for the same `war_id`; queued or dismissed settlement-family items do not foreground as live route targets. The reopen-attempt reset is per turn by design and must not auto-fire without player action.
- **SC-15 / SC-23:** `applied_clauses_preview[]` must structurally equal the actual mutation set, including clause-specific value fields, third-party reaction previews must be shown before ratification, and failed ratifications must be blocked at settlement-summary producer sites as well as at the ratification handler.
- **SC-15:** `settlement_summary` event payloads store both `acceptance_at_staging` for audit context and fresh ratification-time `acceptance_snapshot` for archived review. `docs/SAVE_FORMAT_REFERENCE.md` must document both event fields before SC-15 closes.
- **SC-5 / SC-7:** Deferred incoming-offer tests must enumerate no-exposure assertions across mailbox, pending envoy, notification/notice rail, dispatch, popup queue, Godot routes, and a 50-turn normal-producer soak. If SC-5 is reversed, mailbox and pending-envoy offer payloads must use the `settlement_confirm` review schema plus stable offer identity.
- **SC-19 / SC-25:** Voice families have fixed trigger-to-template mappings, and vocabulary scans classify surface families instead of scanning undifferentiated prose.
- **SC-19:** Required settlement voice families include losing-side pressure explanation and recovery copy: `settlement_losing_side_pressure_explained_talleyrand`, `settlement_open_war_detail_recovery_talleyrand`, `settlement_open_history_recovery_talleyrand`, `settlement_no_alternative_route_chancery`, and `settlement_concession_authored_talleyrand`. Future direct substitute CTAs must add committed Voice Bible copy before exposure.
- **SC-22:** Godot parse/load or executable coverage must land by G2-Slice-3, or a new explicit product decision in this spec and `docs/STATUS.md` is required. Settlement-critical scripts include `notification_bar.gd` and `mailbox_panel.gd`.
- **SC-26:** Same-war draft merge uses type-specific identity keys; same-key differing values conflict, cross-key non-conflicting values append. Collision protection applies to any settlement-family dialogue, hard stop or current-turn offer.
- **SC-27:** The doc-scan token list includes incoming-offer action ids and natural-language variants such as `AI-to-player common-peace offer`, `AI war-leader ... offer`, `Incoming AI settlement offer`, and `synthetic/debug staged offer`, not only exact `incoming_settlement_offer`.
- **SC-27:** The doc-scan token list also includes rejected-settlement false-affordance phrases: `Wait for Enemy Offer`, `Seek Armistice Instead`, `Seek Bilateral Peace`, `Back Out is the only`, `Term editor not available yet`, `Ask for terms`, and `Surrender terms`. Any active occurrence outside the cleanup spec's explicit absence/defer language must carry a same-paragraph supersession marker naming the owning SC row.
- **SC-28:** Rejected/blocked `settlement_confirm` payloads use the recovery affordance contract. They do not render disabled Ratify, direct `Seek Armistice`, direct `Seek Bilateral Peace`, disabled Revise placeholders, or `Wait for Enemy Offer` while SC-5 is deferred.
- **SC-28:** `Open War Detail` is a background-and-preserve transition. It does not use ordinary Back Out discard-confirm semantics, and it preserves non-empty drafts until bilateral peace/armistice success invalidates them or the player explicitly discards them.
- **SC-28 / SC-28b / SC-29:** `Open War Detail` is a live-war recovery route, not a promise that a pair action exists. War Detail renders pair-scoped Bilateral Peace / Armistice controls only when their own eligibility probes pass, and otherwise renders no-current-pair-alternative copy. Direct substitute CTAs remain absent until SC-29 ships scope, helper, handoff, voice, and behavior tests.
- **SC-28:** If no edit, active-war, or archived-history route can be recovered, the popup renders `settlement_no_alternative_route_chancery` terminal copy plus a close/back-out option. This is allowed only for malformed/unrecoverable payloads and must not be used as normal rejected-settlement UX.
- **SC-28:** End-turn draft discard produces a one-shot player notice through `pending_settlement_draft_notices[]` or an explicitly equivalent dispatch/campaign-log notice, and loading after discard must not silently drop the draft without a signal.
- **STATUS:** `docs/STATUS.md` must name the latest cleanup spec version before implementation starts and must not claim SC-27 closure unless the current doc-scan passes.
- **SC-4b:** The settlement resource-cost contract is part of G2-Slice-1 Foundation. Unless a later product decision explicitly records a non-zero `confirm_settlement` cost in this spec and `docs/STATUS.md`, all settlement entry, editor, refusal, and successful ratification paths cost 0 DP/AP/gold. Any future non-zero cost is charged only after SC-3/SC-4 acceptance and hard-stop gates pass, and failed/blocked ratification consumes nothing.
- **STATUS:** `docs/STATUS.md` must name this cleanup spec as v0.22 / Codex-Claude UX synthesis before the next smoke or implementation step, and must not claim SC-27 closure unless the current doc-scan passes. A GO claim must include a review-session reference.

## Implementation Gates

### Gate 1 - Spec Completion

Before code:

- Decide for each gap whether the immediate cleanup is implement, hide, remove, or rename.
- Record any explicit deferral in this spec and `docs/STATUS.md`, including the player impact and the affordance that will be hidden while deferred.
- Record the full treaty-authoring implementation slice plan before touching `Revise Terms`: draft editor, preview refresh, revise/counter route, incoming-offer package preservation, and ratification gate. Any temporary hide/remove choice must name the hidden affordance and why it is only interim.
- Incoming-offer decision is pre-set for cleanup: defer + hide by default. Record any reversal explicitly before code starts; reversal requires producer + mailbox + popup + action handling together, not handler scaffolding alone. Otherwise remove or feature-flag the exposed type from hard-stop/mailbox/Godot player surfaces while deferred.
- Update `docs/STATUS.md` so the next settlement step is this cleanup spec, not Slice G.
- Close SC-27 by marking or replacing the superseded route-id and incoming-offer paragraphs in `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` and stale route-id examples in `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` before implementation or smoke begins.
- Do not mark SC-27 closed in `docs/STATUS.md` until a doc-scan proves every contradicting implementation-plan and parent-spec paragraph is marked, removed, replaced, or explicitly scoped to post-cleanup Slice G.
- Verify `docs/STATUS.md` references this spec as v0.22 / Codex-Claude UX synthesis and does not claim stale seventh-pass, eighth-pass, ninth-pass-only, tenth-pass-only, v0.18-only, v0.19-only, v0.20-only, or v0.21-only readiness as the current gate.
- Verify active `docs/STATUS.md` current-phase / next-step rows do not point implementation at old Slice F, Slice G, or minimal incoming-offer scaffolding before cleanup closure; historical entries must be clearly historical.
- Verify every implementation checklist cites canonical requirements only: SC rows, gate bullets, required tests, or required inversions.

### Post-Landing Verification Delta

`docs/STATUS.md` currently records G2-Slice-1 through G2-Slice-5 as referenced implementation commits, while the active `codex/settlement-smoke-start` branch is a docs/smoke-start repair branch where the latest implementation commit may not be an ancestor of `HEAD`. The next work is branch-target reconciliation plus verification and smoke, not a fresh G2-Slice-1 implementation restart from this docs branch.

Gate 4 has two distinct evidence phases:

- **Pre-smoke branch verification:** before manual smoke starts, use the chosen integration/smoke target to prove branch ancestry, doc scans, focused automated tests, and save-format/status alignment. A "smoke note" cannot satisfy pre-smoke evidence because smoke has not run yet.
- **Gate 4 manual smoke evidence:** after pre-smoke verification passes, record the manual smoke outcomes for the 12-step script below. Smoke notes close Gate 4; they do not replace pre-smoke automated evidence.

Before Gate 4 manual smoke can start, each row below must have current pre-smoke evidence from the chosen integration/smoke target or be reopened explicitly.

| Verification item | Required evidence before smoke |
| --- | --- |
| SC-1 editor floor | A current automated behavior test, executable Godot check, or explicit tooling-block record accepted in `docs/STATUS.md` before smoke proves the normal Settlement CTA opens EDIT mode with `peace`, `territory_cede`, `gold_indemnity`, and demand-only `forced_alliance` controls; a losing France fixture can use the concession baseline or offer-mode controls to author player-as-payer/ceder terms. Future/manual smoke notes cannot substitute for this pre-smoke evidence. |
| SC-2 revise route | `Revise Terms` is either absent, or opens the same editor with staged package, `war_id`, `covered_enemy_participants`, `selected_target_nation`, and route metadata preserved. No disabled placeholder is allowed. |
| SC-3 / SC-4 ratification gate | Blocked/rejected review omits `confirm_settlement` from `options[]` and `available_action_ids[]`; direct backend ratification refuses mutation under the same fresh acceptance/hard-stop gate. |
| SC-5 / SC-6 / SC-7 incoming offers | Default state is defer-and-hide. Evidence must prove no normal gameplay, mailbox, pending-envoy, notification, dispatch, popup queue, or Godot branch exposes incoming settlement offers unless a new product reversal records producer + payload + UI + tests together. |
| SC-8 through SC-13 entry safety | Wizard, war detail, coalition detail, typed command, notification, dispatch, ledger, and stale/revise reopen paths preserve or require `war_id`; multi-war ambiguity is not resolved by sorted fallback. |
| SC-14 through SC-14e continuity | Active partial settlements route to live war context, archived settlements route to history, route ids use the staged source of truth, and stale recovery attempt 4 returns a structured recovery route. |
| SC-15 through SC-25 presentation | Player copy uses Settlement vocabulary, Talleyrand/foreign-court settlement voice families, humanized clause labels, no raw ids/enums/debug payloads, and merged `PEACE & SETTLEMENT HISTORY` semantics. |
| SC-26 collision | Cross-war restaging returns `cross_war_settlement_collision` without clobbering the mounted settlement; same-war merges are deterministic and conflict-safe. |
| SC-27 doc maintenance | Doc scan proves older incoming-offer, route-id, rejected-settlement alternative, and backlog-copy instructions in both `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` and `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` are removed, replaced, superseded on the same paragraph, or explicitly scoped to the concrete landing rows SC-29 / SC-30 / SC-31 / SC-32. |
| SC-28 / SC-28b rejected/losing recovery | Blocked/rejected reviews follow the recovery affordance contract: absent blocked Ratify, real editor/recovery/history/terminal-close routes only, no enemy-offer wait while SC-5 is deferred, no direct `Seek Armistice Instead` or pair-action wrapper, Open War Detail preserves scoped drafts, and losing-side concession baseline is testable. |
| STATUS alignment | `docs/STATUS.md` names v0.22 verification + branch reconciliation + Gate 4 smoke as the active gate, names the rejected/losing smoke fixture, records the latest spec-review result or NO-GO edits, and does not claim SC-27 closure until the scan above passes. |

If any P0/P1 row lacks evidence, Gate 4 is NO-GO and the row reopens for a focused repair before smoke. This delta is deliberately verification-shaped: implementers should not re-run the old slice plan unless the evidence proves a row is actually missing or regressed.

### Gate 2 - Ordered Cleanup Slices

Gate 2 is not one bundled patch. The cleanup must proceed in this dependency order so presentation polish cannot land on top of a misleading or unusable treaty flow.

Slice dependency rationale:

- Spec Synthesis And Doc Contract comes first because stale parent-plan instructions and STATUS drift can send implementation back to forbidden false affordances before code starts.
- Foundation comes second because route safety does not matter while the destination is still an empty/no-clause settlement shell.
- Entry Safety comes third because continuity tests need stable `war_id`, selected-target, and eligibility contracts.
- Continuity comes fourth because result, notification, dispatch, and ledger focus must preserve the exact route produced by safe entry.
- Incoming Offers comes fifth because offer exposure depends on the same draft package, stale-state, and route-preservation contracts.
- Presentation And Metadata comes sixth so copy polish and ledger semantics describe a real, gated settlement flow.
- Rejected / Losing Recovery Repair comes last because it verifies the player-facing failure modes after authoring, entry, continuity, incoming-offer exposure, and presentation have all been reconciled on the chosen integration target.

Slice closure template:

- Every SC row named by the slice has behavior tests green.
- The relevant focused test files and any required legacy test inversions are updated in the same slice.
- At most one of the slice's named SC rows may remain in interim-hide state at slice closure. A second interim-hide blocks slice closure unless this spec and `docs/STATUS.md` record explicit product approval. The SC-5/SC-6/SC-7 incoming-offer defer-and-hide decision counts as one approved incoming-offer deferral package only when all no-exposure tests pass together.
- The full pytest suite is green unless an explicit unrelated existing failure is recorded in `docs/STATUS.md`.
- `ruff check backend tests` is clean when backend/tests are touched.
- `docs/STATUS.md` records the completed slice, names the next slice, and records any interim-hide artifacts still active.
- No intermediate cleanup slice is player-releasable merely because its own tests pass. Normal player-visible settlement surfaces must remain hidden, omitted, or explicitly approved in `docs/STATUS.md` until the visible path is no longer misleading across authoring, entry safety, continuity, presentation, recovery, and Godot coverage.

#### G2-Slice-0 - Spec Synthesis And Doc Contract

Close the v0.22 Codex-Claude synthesis before any code implementation resumes. This is code-equivalent planning work, not optional cleanup.

Required closure:

- Consolidate still-binding audit-history amendments into canonical SC rows, gate bullets, required tests, and required inversions. Anything left as provenance must be under a clearly non-normative historical heading.
- Update `docs/STATUS.md` with the current spec version, review-session reference, NO-GO/GO result, and minimum remaining spec edits.
- Run the SC-27 doc scan over the implementation plan and parent spec, including incoming-offer, incoming-offer smoke-branch, route-id, rejected-settlement alternative, direct-pair-action, and backlog-copy tokens.
- Prove no active instruction points implementation at disabled Ratify, disabled Revise, direct `Seek Armistice Instead`, `Wait for Enemy Offer`, `Ask for terms`, `Surrender terms`, raw `pending_settlement_drafts[war_id]` merge semantics, or smoke-note-only pre-smoke evidence.

Required tests / checks:

- `test_status_md_current_phase_names_cleanup_spec_v022_and_review_session`
- `test_doc_scan_flags_rejected_settlement_unmarked_alternatives`
- `test_doc_scan_flags_incoming_ai_offer_smoke_step_without_sc5_supersession`
- `test_spec_sc_rows_do_not_allow_direct_pair_action_wrappers_from_settlement_confirm`
- `test_spec_pre_smoke_evidence_cannot_be_satisfied_by_future_smoke_note`

#### G2-Slice-1 - Foundation

Close SC-1, SC-2, SC-3, SC-4, and SC-4b first, including the SC-1 empty-dispatch one-line presentation anchor at `settlement_presentation.py:494`.

Internal sub-gates:

- **G2-1a Editor and draft shell:** editor layout contract recorded, structured controls for required first-slice clauses, draft storage created, empty/non-empty Back Out behavior, save/load defaults, and Save Format Reference updates.
- **G2-1b Preview and validation:** POST preview schema, canonical clause conflict matrix, validation taxonomy, GET non-mutation property, and Submit revalidation.
- **G2-1c Ratification gates:** fresh acceptance rescore, `threshold`/`accept_threshold` reconciliation, hard-stop refusal, absent `confirm_settlement` option when blocked, SC-4b resource-cost contract, and direct backend no-mutation enforcement.
- **G2-1d Mode transitions and recovery:** EDIT -> REVIEW -> EDIT revise flow, rescore-failure UX, option-count rendering, draft preservation, and required inversions.

G2-Slice-1 is not closed until every sub-gate above is green; partial sub-gate completion is implementation progress, not slice closure.

Required closure:

- Common peace becomes a real war-scoped term-authoring settlement system with populated draft packages from normal UI paths.
- The editor recognizes the canonical clause vocabulary (`peace`, `territory_cede`, `gold_indemnity`, `gold_per_turn`, `forced_alliance`, `vassalage`, `subjugation`, and `liberation`) and exposes the currently live subset only through structured controls.
- G2-Slice-1 closure requires at least `peace`, `territory_cede`, `gold_indemnity`, and `forced_alliance` live and not interim-hidden.
- Every supported clause uses structured controls; free-text JSON clause entry is forbidden.
- The editor lives on the existing `proposal_confirm_popup.gd::_build_settlement_content` settlement popup surface unless this spec records a different product decision.
- The chosen editor layout is recorded in this spec and `docs/STATUS.md`; every live clause type is reachable in one 1080p editor session without obscured scroll, and every hidden canonical clause type has the four interim-hide artifacts.
- Wizard, war-detail, coalition-detail, and revise authoring paths use POST settlement preview for draft-dependent state; GET settlement preview remains read-only/eligibility baseline. Incoming-offer authoring/promotion paths are required here only if SC-5 is explicitly reversed; under the default defer-and-hide decision, no-exposure tests replace incoming-offer authoring requirements.
- `_execute_propose_common_peace` and every structured Godot settlement entry path preserve authored `settlement_terms`, `covered_enemy_participants`, and `selected_target_nation` through staging.
- Submit revalidates submitted `settlement_terms` against the SC-1 POST preview taxonomy before staging; failed revalidation returns `submitted_terms_failed_revalidation` and stages nothing.
- `stage_settlement_confirm(...)` receives explicit caller kind so player-editor draft writes cannot be confused with AI/system staging.
- Unratified authored drafts persist only in `world.pending_settlement_drafts[draft_key]` after successful POST preview, round-trip through save/load, restore within the same turn for the same war/selected-target/covered-scope, and are discarded on turn end, ratification, or explicit discard-confirm.
- Empty-draft Back Out pops immediately without discard-confirm or draft write; non-empty draft Back Out uses discard-confirm.
- Editor validation errors render inline, disable Submit/Preview, keep editor-mode ratification absent, and are not auto-stripped.
- Pending POST preview renders a visible pending state, disables Submit, keeps editor-mode ratification absent, and never presents previous acceptance as current. Failed POST preview preserves the draft and last valid preview as stale/previous, shows humanized retry copy, and does not stage or mutate.
- POST preview enforces the SC-1 conflict matrix and points each editor error to the offending clause.
- `Revise Terms` opens real draft mutation/preservation or is absent. Disabled placeholder variants such as "Term editor not available yet" are forbidden.
- `Ratify Settlement` is absent from `options[]` and `available_action_ids[]` on rejection, below-threshold score, or hard stops, and direct backend ratification refuses mutation under the same fresh acceptance/hard-stop gate.
- Ratification re-runs `calculate_common_peace_acceptance(...)` from current world state; it does not trust the staged acceptance snapshot.
- Settlement entry, GET/POST preview, Submit, Revise Terms, Back Out, failed ratification, stale recovery, hard-stop refusal, and successful ratification follow the SC-4b zero-cost default unless a later product decision records a non-zero `confirm_settlement` cost in this spec and `docs/STATUS.md`.
- `calculate_common_peace_acceptance(...)` returns `threshold`, and settlement ratification/presentation code consumes that field without hardcoded literal thresholds outside scorer tuning.
- Rescore failures keep the dialogue mounted with refreshed acceptance when possible, or return a valid reopen target with `acceptance_changed_after_staging`.
- Accepting-side leader changes trigger live re-score, not automatic reopen, unless the rescored package fails.
- Slice 1 does not change one-to-one diplomacy-wizard, war-detail, or war-status CTA visibility unless the same patch also preserves the eligible SC-10 Bilateral Peace / Armistice substitutes on that surface.
- Update `docs/SAVE_FORMAT_REFERENCE.md` for scoped `pending_settlement_drafts`, `settlement_route_seq`, and any other new world-state fields added in this slice.
- `settlement_route_seq` serialization shape is `Dict[str, Dict[int, int]]` or an explicitly documented serialized equivalent, default `{}`, with old-save migration and reset/continuity behavior covered by save/load tests.
- The scorer's current `accept_threshold` return key is renamed to `threshold` or explicitly aliased before SC-3 presentation and ratification consumers read it.

Required tests:

- End-to-end author -> preview -> revise -> ratify behavior test with at least one distinctive material clause.
- Structured executor test proving `_execute_propose_common_peace` forwards a distinctive `settlement_terms` package into the staged dialogue.
- POST preview validation taxonomy tests for foreign actor, proposer-side mismatch, clause-count overflow, duplicate/conflicting clauses, empty authored draft, and a valid draft.
- Parametrized POST preview tests for the eight SC-1 conflict-matrix cases, each proving `disabled_reason_display` and offending-clause index/field.
- Clause ordering test proving two drafts with the same valid clauses in different order produce identical acceptance payloads, validation results, and mutation preview.
- Godot editor source/executable guard proving structured controls exist for each live clause type and raw JSON clause entry is absent.
- Authored peace display test proving `type_display="Peace"` and `display_label="End hostilities (no material change)"`; empty package test proves no fake Terms row is injected.
- Godot editor reachability test proving every live clause type can be reached from the chosen editor layout in one 1080p session, and any hidden canonical type has four-artifact interim-hide tracking.
- Editor error-state test proving invalid clauses show inline errors and disable Submit until fixed.
- Preview pending/failure test proving Submit is disabled and editor-mode ratification remains absent while POST preview is in flight, a failed preview keeps the draft in EDIT mode, last valid acceptance is visibly stale, and no staging or mutation occurs.
- Draft write-on-preview, scoped same-war save/load round-trip, autosave-before-end-turn, and end-turn discard tests.
- Empty-draft Back Out test proving no discard prompt and no `pending_settlement_drafts` write.
- Popup-close test proving Escape/window-close/click-outside with a non-empty draft triggers the same discard-confirm path as Back Out and cannot silently drop the draft.
- GET preview non-mutation property test proving no staging, no draft persistence, no dialogue changes, and no cache invalidation after repeated calls.
- Baseline empty-term common-peace test for today's behavior, then inverted when SC-1 closes.
- Dispatch one-liner test proving empty `terms_summary` does not render `settlement ratified` after SC-1 closes.
- Direct backend ratification tests proving fresh rescored rejection, accepting-side leader change rejection, threshold-field gating, and hard stops leave diplomatic state, treaties, regions, relations, threat, event log, and dialogue state unmutated except for approved refusal feedback.
- Settlement resource-cost contract test proving open/preview/submit/revise/back-out/failure paths consume no DP/AP/gold, successful ratification follows the approved zero-cost default exactly, and any future non-zero `confirm_settlement` cost is displayed, charged once only after acceptance/hard-stop gates pass, and never charged on failure.
- Serialization enforcement test proving scoped `pending_settlement_drafts` and `settlement_route_seq` save/load round-trip, old-save defaults, and `docs/SAVE_FORMAT_REFERENCE.md` documentation.
- Proposer-side leader-change test proving a still-acceptable rescored package ratifies without forced reopen.
- Blocked-ratification popup render test proving blocked/rejected payloads show the Voice Bible 16.1 blocked banner, omit `confirm_settlement` from `options[]` and `available_action_ids[]`, surface `Open War Detail` or `Open Settlement History` recovery when available, and suppress outgoing acceptance framing.
- Popup option-count render test over 0, 1, 2, 3, 4, and 5 settlement options.
- Required first-slice clause availability and submit/stage behavior tests for `peace`, `territory_cede`, `gold_indemnity`, and `forced_alliance`.
- Payload schema test proving preview, submit, and review payloads use the canonical v0.22 keys and fail on alias-only scope or acceptance fields.
- Scoped draft identity test proving same-war different selected-target or covered-scope drafts do not merge or clobber.
- Submit revalidation test proving a conflict-matrix failure returns `submitted_terms_failed_revalidation` and no staged dialogue.
- Caller-kind test proving AI/system staging does not write `pending_settlement_drafts`.

Required inversions:

- Invert `tests/test_common_peace_c2_preview.py` assertions that pin always-present `Ratify Settlement` on rejected/hard-stopped payloads, including the `options[0]["label"] == "Ratify Settlement"` expectation near `tests/test_common_peace_c2_preview.py:122`.
- Invert any baseline empty-term tests once the editor enforces explicit `peace` or material clauses.
- Invert `debug_action_ids` medium-payload assertions near `tests/test_common_peace_c2_preview.py:116-120` when SC-17 lands in this or a later slice.

#### G2-Slice-2 - Entry Safety

Close SC-8, SC-8b, SC-10, SC-11, SC-11b, SC-12, and SC-13.

Required closure:

- Wizard and typed/free-text settlement entry never auto-pick a war under multi-war ambiguity.
- War-status and war-detail CTAs use active hostile-pair settlement eligibility, not unique-nation count, and the eligibility cache invalidates on `world.invalidate_war_instance_indexes()`.
- War-status, wizard, and POST preview use `evaluate_open_settlement_eligibility(world, *, war_id, actor_nation)` as the shared eligibility probe.
- Coalition settlement CTAs are eligibility-gated and never auto-pick coalition leader, alphabetic target, or hidden wrong-court context; focused-row per-war buttons are primary and other eligible per-war buttons are secondary.
- Focused ineligible coalition rows render disabled with reason while eligible secondary routes remain actionable.
- Staged dialogues carry top-level `selected_target_nation` and authored `covered_enemy_participants` from every production entry path, and reopen routing reads selected target first while preserving the covered-enemy scope.
- `_execute_propose_common_peace`, `stage_settlement_confirm(...)`, and `build_settlement_confirm_dialogue(...)` all forward and persist `selected_target_nation` and `covered_enemy_participants`; production staging fails closed if selected target is empty or covered-enemy scope is missing.
- Eligibility probe remains CTA-only; POST preview remains the authoring path; both share disabled-reason display taxonomy.

Required tests:

- Multi-war wizard and typed/free-text disambiguation tests.
- War-status partial-settlement eligibility test plus same-turn invalidation test after pair resolution.
- Coalition chooser/focused-row test with leader different from selected target and multi-war primary/secondary per-war buttons.
- Focused-ineligible coalition fixture proving the focused row is disabled with reason and an eligible secondary row remains actionable.
- Entry-path matrix proving wizard, war-detail, coalition-detail, typed command, notification reopen, dispatch reopen, and result feedback all stage top-level `selected_target_nation` and exact `covered_enemy_participants`; include incoming-offer promotion only if SC-5 is explicitly reversed.
- Executor plumbing test proving structured `selected_target_nation` and `covered_enemy_participants` reach the staged dialogue.

Required inversions:

- Invert `tests/test_settlement_ui_slice_f_behavior.py::test_resolve_without_war_id_falls_back_to_legacy_path` so no-`war_id` multi-war settlement rejects ambiguity instead of using legacy fallback.

#### G2-Slice-3 - Continuity

Close SC-14, SC-14b, SC-14c, SC-14d, SC-14e, SC-7b, and SC-26.

Required closure:

- Active partial settlement result feedback routes to live war/settlement context; archived full-war settlements route to the ledger row.
- Stale recovery cannot loop indefinitely or strand the player.
- Stale recovery uses `SETTLEMENT_REOPEN_MAX_ATTEMPTS = 3` per `(war_id, turn)` and attempt 4 returns the pinned choose-from-war-detail copy.
- Every `must_reopen=True` settlement-family response has non-empty `reopen_target.target_nation` and `error_display`, or returns a non-reopen humanized fallback / mounted-dialogue error.
- Reopen handlers return the SC-14b choose-from-war-detail fallback when both `selected_target_nation` and `covered_enemy_participants` are empty.
- Staged route id is the source of truth through reaction event, result feedback, dispatch, notification metadata, and ledger row.
- Staged route ids use `settlement:{war_id}:{turn}:{seq}` and the per-turn sequence is persisted on world state.
- Focused rows cannot be trimmed by Recent Settlements row caps.
- Archived/aged-out dispatch clicks fail gracefully instead of opening blank focus.
- Incoming-offer accept failures cover missing `war_id`, invalid `war_id`, and archived-since-offer-creation.
- Cross-war settlement entries cannot clobber the active settlement-family hard-stop for another `war_id`; same-war restaging cannot overwrite authored draft state.
- Active result/review routes foreground a mounted same-war settlement popup first, otherwise open war detail; they never open the wizard as a live-route target.
- Mounted means current hard-stop `settlement_confirm` for the same `war_id`; queued, dismissed, or non-current settlement-family items do not count.
- Same-war same-scope restaging refreshes the mounted dialogue and merges only non-conflicting authored draft terms through the scoped `pending_settlement_drafts[draft_key]`; same-war different-scope restaging returns `same_war_scope_collision` or an explicit replace/chooser flow, and merge conflicts are rejected with active draft unchanged.
- Cross-war restaging rejects with `cross_war_settlement_collision` and humanized copy; it is not queued through the mailbox.
- Collision protection applies to every settlement-family dialogue, including current-turn offers if SC-5 is reversed.
- Active-vs-archived result, notification, and dispatch links re-resolve current war state at click time.

Required tests:

- Active-vs-archived routing test for result feedback and notification clicks.
- Live-route precedence test: mounted same-war dialogue is foregrounded; no mounted dialogue opens war detail; archived settlement opens ledger by route id.
- Mounted-definition negative test proving a queued-but-not-current same-war settlement item opens war detail or fallback, not foreground.
- Dispatch-click active-vs-archived routing test using the same branch.
- Stale-recovery loop cap test proving attempts 1-3 may reopen and attempt 4 returns `must_reopen=False` with an actionable `recovery_route` to War Detail or Settlement History.
- Outgoing revise/confirm stale test proving no `must_reopen=True` response can carry empty `reopen_target.target_nation`.
- Dual-empty reopen test proving empty selected target plus empty covered enemies returns non-reopening choose-from-war-detail copy.
- Same-turn route-id uniqueness and continuity test proving `_emit_settlement_summary_event` consumes staged route id.
- Route-id format test proving same-turn ids are `settlement:war_1:7:1` and `settlement:war_1:7:2`, and reaction/dispatch/ledger/notification consume them verbatim.
- Recent-row cap focus test and aged-out dispatch-click test.
- Click-time re-resolution test proving a link rendered while active opens archived ledger/history if the war archives before click.
- Stale incoming-offer accept test for empty, invalid, and archived war ids.
- Cross-war collision test: stage `war_1`, then attempt to stage `war_2`; `war_1` remains active and `war_2` returns `cross_war_settlement_collision` with humanized rejection, not queue/defer.
- Same-war collision tests: stage `war_1` with authored `territory_cede`, restage `war_1` with compatible `gold_indemnity`, and prove one active dialogue plus merged draft; then restage with a conflicting clause and prove `merge_conflict`, humanized conflict copy, and active draft unchanged.
- Same-war different-scope collision test: stage `war_1` for Britain, then attempt to stage `war_1` for Prussia with a different covered scope; assert no silent merge/clobber and a humanized choose/replace/collision path.
- Same-war merge-semantics tests proving same-key different gold amounts conflict, while compatible cross-key terms append.
- If SC-5 is reversed, incoming-offer collision test proving a war-2 offer does not clobber a war-1 settlement-family item.

Required inversions:

- Invert tests that pin `route_id == "{war_id}:{turn}"`, including `tests/test_settlement_ui_slice_f_behavior.py:626-640`.
- Invert archived recent-settlement tests that expect acceptance sections to be empty, including `tests/test_settlement_presentation.py:1173-1178`.

#### G2-Slice-4 - Incoming Offers

Close SC-5, SC-6, and SC-7 by the default defer-and-hide decision unless a new explicit product reversal is recorded in this spec and `docs/STATUS.md` before code starts.

Required closure:

- If implemented, incoming settlement offers are naturally producible by gameplay, mailbox/pending-envoy routes return settlement-shaped popup payloads, accept preserves exact offer identity and clauses through live re-preview, and request revision opens a real counter/edit route.
- If deferred, all player-facing incoming-offer taxonomy and Godot popup/action routes are hidden or feature-flagged, stale save/debug-injected offers fail gracefully, and tests prove normal gameplay cannot expose, count, activate, or block on them.
- The default SC-5/SC-6/SC-7 defer-and-hide path is one incoming-offer deferral package, not three independent interim hides; it may close only when the full no-exposure matrix passes together.
- Deferred-offer tests must enumerate mailbox count, mailbox activation, pending-envoy, notification/notice rail, dispatch, popup queue, Godot route branches, and 50-turn normal-producer soak assertions.
- If implemented, mailbox and pending-envoy offer payloads use the normal settlement review schema plus stable offer identity and exact offered terms.

Required tests:

- If implemented: producer/50-turn soak test; distinctive-clause offer accept preservation test proving `offer_id`, sides, covered enemies, and exact `settlement_terms` survive live re-preview; request-revision counter/editor test; `/pending_envoy` and `/mailbox/activate` settlement payload tests.
- If implemented: mailbox-activate payload-shape test proving the payload matches `settlement_confirm` review plus `offer_id`, `offered_settlement_terms`, side context, covered enemies, selected target, and incoming-offer voice perspective.
- If deferred: no-exposure mailbox/top-bar/pending-envoy test; no-exposure normal-turn producer audit; request-revision/accept action absence test; `/pending_envoy` and `/mailbox/activate` tests proving stale or injected incoming offers do not surface as usable player offers; notification/notice rail, dispatch, popup queue, and Godot branch tests proving the type is absent or feature-flagged off.

Required inversions:

- If deferred, replace incoming-offer scaffolding expectations with no-exposure tests across mailbox, pending-envoy, notification, dispatch, Godot popup routing, and normal-turn producer audit.

#### G2-Slice-5 - Presentation And Metadata

Close SC-15, SC-15b, SC-16, SC-17, SC-19, SC-20, SC-23, SC-24, and SC-25 after the treaty, entry, continuity, and incoming-offer decisions are no longer misleading.

Required closure:

- `settlement_confirm` explains beneficiaries, ignored parties, remaining wars, acceptance blockers, hard stops, political costs, live awe/set-piece stakes, and exact clause mutations before ratification.
- `applied_clauses_preview[]` structurally matches the actual ratification mutation set by clause, region, payer, recipient, dependency target, amount, turns, `includes_continental_system`, threat delta, and pair-state transition.
- Live preview includes third-party reaction previews for projected commitment grievances, shut-out allies, threat deltas, and notification beats.
- Archived settlement review renders the fresh ratification-time `acceptance_snapshot`, not the stale staging preview.
- Failed ratification does not emit settlement-summary/history events from any producer path.
- Blocked acceptance suppresses misleading numeric score copy.
- Forced-alliance threat preview uses `compute_forced_alliance_threat_preview(...)`.
- Raw ids/enums/debug labels do not reach player surfaces, and normal production payloads do not include `debug_action_ids`.
- Incoming and outgoing settlement voices are distinct or incoming-offer surfaces are hidden.
- Blocked-ratify, rescore-failure, discard-confirm, collision, reopen-cap, war-detail recovery, history recovery, no-alternative terminal recovery, concession-authored, and foreign-observer copy routes through the SC-19 voice families.
- Each SC-19 voice family is bound to its specified trigger and surface; using any Voice Bible settlement family on the wrong trigger fails the row.
- Ledger/dispatch peace and settlement history is merged into one reverse-chronological `PEACE & SETTLEMENT HISTORY` surface with row-level type tags, per-event rows, distinct route namespaces, and a combined cap of 5.
- Bilateral peace history rows have a named producer and route-id namespace distinct from settlement rows.
- Treaty harshness metadata stores both raw common-peace harshness and legacy clamped harshness under explicit fields, and named common-peace consumers read raw harshness.
- Player-facing copy uses `Settlement` as the route/feature term and does not mix `common peace`, `settlement`, and `treaty` as interchangeable labels.
- Vocabulary tests target route/CTA/headline labels, voice-template strings, and backend-resolved settlement voice output; they do not ban lowercase prose-body noun usage.
- Vocabulary scans classify surface families: CTA button text, popup headings, dialog titles, mailbox summary labels, dispatch headlines, ledger section titles, route labels, and voice-template top-level lines.
- Old-save free-form `event_log[].message` text is historical and not migrated; all new generated settlement renders use the new vocabulary.

Required tests:

- Presentation payload tests for resolved/unresolved pairs, beneficiaries, ignored parties, mutation-preview clauses including gold amount/turns and `includes_continental_system`, preview/mutation structural equivalence, third-party reaction previews, live awe, ratification-time acceptance snapshot, failed-ratification no-history behavior, blocked copy, forced-alliance threat projection, raw-label scan, voice perspective and required voice-family trigger routing, reverse-chronological merged history with bilateral and settlement producer namespaces, treaty harshness consumer fields, and route-label/voice-template settlement vocabulary including old-save/new-render behavior and surface-family classification.

Required inversions:

- Invert `debug_action_ids` tests to expect `available_action_ids` or no production action-id list.
- Invert ledger precedence tests to expect the merged `PEACE & SETTLEMENT HISTORY` surface with type tags.
- Invert treaty harshness tests to assert both raw and legacy clamped fields.
- Rename `tests/test_settlement_ui_slice_f_*` to `tests/test_settlement_ui_cleanup_*` or another non-slice-F name when this cleanup spec closes.

#### G2-Slice-6 - Rejected / Losing Recovery Repair

Close SC-28, SC-28b, and the v0.22 SC-27 parent-spec route-id / rejected-alternative extension after Slices 1-5 are reachable on the chosen integration/smoke target. This is a focused repair slice, not a restart of the earlier G2 ladder.

Required closure:

- Blocked/rejected `settlement_confirm` payloads omit `confirm_settlement` from `options[]` and `available_action_ids[]`; the blocked banner and body copy explain the reason.
- The only blocked-review actions are real settlement-family routes: edit/re-author when available, `open_war_detail`, `open_settlement_history`, and terminal close/back-out for malformed unrecoverable payloads.
- `open_war_detail` preserves a non-empty scoped draft without discard-confirm and opens the exact `war_id` plus selected target; War Detail, not the settlement popup, owns Bilateral Peace and Armistice controls when their own pair-scoped eligibility passes.
- No payload, option label, disabled placeholder, recovery hint, mailbox item, notification, dispatch line, or Godot branch mentions enemy-offer waiting, `Seek Armistice Instead`, `Seek Bilateral Peace`, `Ask for terms`, or `Surrender terms` while their landing rows SC-29 / SC-30 / SC-31 are unshipped.
- Losing-side concession baseline is deterministic for the smoke fixture and uses only canonical clauses.
- End-turn draft discard produces a one-shot player notice or an explicitly equivalent dispatch/campaign-log notice.
- `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` no longer contains unsuperseded stale route-id examples.

Required tests:

- `test_blocked_settlement_recovery_affordance_schema`
- `test_blocked_ratify_is_absent_and_blocked_banner_explains_reason`
- `test_no_wait_for_enemy_offer_affordance_while_incoming_offers_deferred`
- `test_seek_armistice_instead_cta_absent_until_sc29_lands`
- `test_open_war_detail_recovery_preserves_non_empty_draft_without_discard_prompt`
- `test_open_war_detail_recovery_does_not_promise_ineligible_pair_action`
- `test_blocked_settlement_with_no_alternatives_shows_terminal_copy_and_close`
- `test_losing_side_talleyrand_concession_baseline_uses_peace_gold_and_territory_only`
- `test_editor_renders_clause_direction_labels`
- `test_losing_peace_only_preview_prompts_concession_without_offer_wait`
- `test_load_after_end_turn_does_not_silently_drop_draft_without_player_signal`
- SC-27 doc scan covering both settlement implementation plan and parent settlement spec route-id examples.

#### G2-Slice-7 - Pair-Scoped Peace Substitute CTAs

Close SC-29 after G2-Slice-6. This slice exists because hidden direct pair actions must land somewhere concrete rather than becoming permanent invisible backlog.

Required closure:

- Rejected/blocked settlement review can expose `Seek Armistice Instead` and `Seek Bilateral Peace` only when the selected target pair is eligible and the payload is explicitly pair-scoped.
- The handoff payload includes `{action, war_id, selected_target_nation, scope="selected_pair"}` and never targets all covered enemies by implication.
- `evaluate_pair_peace_substitute_eligibility(...)` or an equivalent shared helper is the single source of truth for Godot visibility and backend refusal.
- Clicking a substitute CTA preserves or invalidates the current scoped settlement draft according to the War Detail recovery contract; other hostile pairs remain unchanged.
- SC-13, SC-14b, SC-19, and SC-26 interactions are covered: selected target inheritance, no settlement reopen-attempt consumption, voice copy, and same/cross-war collision behavior.

Required tests:

- `test_seek_armistice_instead_creates_per_pair_armistice_with_selected_target_only`
- `test_seek_bilateral_peace_instead_creates_per_pair_peace_with_selected_target_only`
- `test_pair_substitute_eligibility_helper_matches_backend_refusal_codes`
- `test_pair_substitute_handoff_preserves_or_invalidates_scoped_draft_correctly`

#### G2-Slice-8 - Dependency And Surrender Terms Restoration

Close SC-31 before any `Surrender terms` label, preset, backend command, or mailbox row appears. This slice may run after Slice 7 or be absorbed into a larger dependency-clause restoration branch, but it remains a named landing target.

Required closure:

- Dependency clauses used for surrender are live, previewable, ratifiable, and recorded in settlement history.
- Surrender presets produce concrete canonical clauses rather than prose-only surrender intent.
- Preview explains dependency consequences, accepting-side benefit, player loss of agency, relevant third-party reactions, and any Balance of Europe / threat effects.
- Ratification mutation, ledger/history/dispatch copy, and Voice Bible §16.1 surrender/dependency families land in the same slice.

Required tests:

- `test_surrender_terms_absent_until_dependency_clause_restoration`
- `test_surrender_terms_authors_dependency_clause_with_preview_and_mutation`
- `test_surrender_terms_voice_and_history_explain_dependency_consequence`

#### Slice G1 - AI Settlement Offer Producer And Request Terms

Close SC-30 before any `Wait for Enemy Offer`, `Ask for terms`, incoming-settlement-offer mailbox row, or request-revision/counteroffer control appears.

Required closure:

- Normal gameplay can produce an incoming settlement offer with stable offer identity and concrete settlement terms.
- The producer is cooldown-gated, one-active-offer safe, and covered by mailbox/pending-envoy activation tests.
- `Ask for terms` creates a real request-terms state or returns a humanized refusal; it is not a passive wait label.
- Accept/reject/request-revision preserve package identity, live-preview before mutation, and avoid generic proposal fallback.
- SC-5 no-exposure tests invert only in the same slice that lands the producer, payload, UI, voice, and behavior tests.

Required tests:

- `test_ai_settlement_offer_producer_surfaces_real_mailbox_payload`
- `test_wait_for_enemy_offer_only_visible_when_offer_producer_and_cooldown_path_exist`
- `test_ask_for_terms_creates_request_terms_state_or_humanized_refusal`
- `test_incoming_offer_accept_preserves_offer_identity_and_terms_through_live_preview`

#### Slice G2 - Settlement Agency Follow-Through

Close SC-32 after G1. This slice owns broader settlement-agency promises so they cannot remain vague Slice G prose.

Required closure:

- AI counterproposals, ally petitions/advisories, conference mechanics, veto-like systems, and voluntary alignment offers each have one of two outcomes: shipped with payload/UI/voice/tests, or explicitly removed from player-facing scope in this spec and `docs/STATUS.md`.
- No settlement-agency CTA can appear from layout tolerance, mailbox scaffolding, debug state, or old parent-spec text before its behavior lands.
- If conference or veto systems are not part of the product direction, the row records that removal and ensures no player-facing copy implies them.

Required tests:

- `test_settlement_agency_landing_ledger_has_no_unowned_backlog_controls`
- Per-action behavior tests before any agency CTA appears.

### Gate 3 - Behavioral Coverage Upgrade

Required tests:

- Backend behavior tests for every settlement dialogue action: confirm, revise, back out, accept offer, reject offer, request revision.
- Godot source guards only as supplements, not as the primary proof of behavior.
- A Godot parse/load or executable harness for touched settlement scripts, or a per-slice `docs/STATUS.md` tooling-block record with manual smoke evidence if the toolchain is unavailable. This deferral cannot extend past G2-Slice-3 without a new explicit product decision in this spec and `docs/STATUS.md`.
- Godot critical script coverage includes `main.gd`, `diplomacy_wizard.gd`, `war_detail_popup.gd`, `proposal_confirm_popup.gd`, `diplomatic_ledger.gd`, `top_bar.gd`, `notification_bar.gd`, and `mailbox_panel.gd`.
- Same-nation multi-war route tests proving `war_id` disambiguates wizard, war-detail, coalition-detail, reopen, notification, result feedback, and ledger routes.
- Same-turn settlement route-id uniqueness tests proving two settlement events for one `war_id` do not share a focus id.
- Typed/free-text multi-war route tests proving no-`war_id` settlement commands reject ambiguity instead of choosing a war.
- Test inversion or replacement for legacy expectations so no test pins no-`war_id` multi-war settlement to first-match resolver behavior, `route_id == "{war_id}:{turn}"`, archived settlement acceptance sections being empty, or empty-term common peace as a completed authored treaty path.
- Incoming offer stale-state tests proving accept promotes through live settlement preview or returns a visible stale error.
- Incoming offer package-preservation tests proving accept carries offered terms into the promoted `settlement_confirm` instead of rebuilding an empty/no-clause package.
- If incoming offers are deferred, mailbox and 50-turn soak/producer-audit tests proving normal gameplay cannot produce, count, activate, or block on `incoming_settlement_offer`.
- Stale-recovery loop tests proving repeated `must_reopen` cannot strand the player in a hard-stop dialogue.
- Client response-failure recovery test proving a settlement popup hidden before a failed dialogue response is remounted or replaced with a humanized retry/back-out route, not left as an invisible hard stop.
- Acceptance enforcement tests proving rejection and hard stops block mutation.
- Settlement resource-cost tests proving the approved cost contract is honored and no failed, blocked, stale, preview, revise, or back-out path consumes DP/AP/gold.
- Term-authoring tests proving the normal UI can author, preview, revise, and preserve concrete clauses without advertising unavailable controls.
- Live-awe preview test proving a settlement set-piece appears before ratification when applicable.
- Baseline empty-term common-peace test for today's behavior, inverted by the full treaty implementation so empty packages no longer masquerade as complete settlement authoring.
- Godot action-routing tests proving settlement actions never call natural-language command fallback, including a fake/new settlement action id that is intentionally absent from the local whitelist.
- Popup/presentation behavior tests proving raw acceptance enums, malformed-payload debug text, misleading blocked numeric copy, disabled Ratify placeholders, disabled Revise placeholders, arbitrary settlement option counts, no-alternative terminal copy, and incoming/outgoing voice inversions do not reach player-facing copy.
- Coalition-detail behavior tests proving multi-war coalitions produce actionable per-war routes or approved hidden/no-action copy.
- Ledger precedence tests proving the merged `PEACE & SETTLEMENT HISTORY` surface uses row-level type tags and focuses the correct row.
- Treaty metadata harshness-scale test proving recorded common-peace harshness matches the spec decision.
- Settlement vocabulary tests proving rendered player surfaces use `Settlement` consistently.
- SC-28 behavior tests proving rejected/blocked reviews expose real recovery routes or terminal close copy, not direct armistice/peace wrappers, enemy-offer waits, or disabled placeholder buttons.

### Gate 4 - Manual Smoke

Manual smoke cannot pass until Gate 2 and Gate 3 are green.

Smoke script:

1. Open a multi-party war settlement from the diplomacy wizard. Confirm that no command-box text is generated by settlement buttons and that multi-war cases disambiguate or hide the wizard action.
2. Open the same war from war detail. Confirm the same `war_id` and selected target are staged.
3. Open coalition detail. Confirm eligible shared-war settlements show the right CTA, one-to-one/shared-ineligible contexts hide it, and multi-war coalitions provide actionable per-war routes or approved no-action copy.
4. Open a one-to-one war. Confirm common-peace controls are absent and structured Bilateral Peace / Armistice controls remain reachable on the same war-detail or war-status surface with their real costs/disabled reasons.
5. Open Settlement through the player-facing CTA per SC-25. Confirm the flow has real editable draft terms and no empty-package treaty review masquerading as authored settlement.
6. Try `Revise Terms` / request revision if visible. Confirm it opens a real editor or is absent because the entry path already authored terms on the same editor surface. After ratifying an accepted settlement, reopen the same war's settlement path and re-author terms; confirm the editor accepts a fresh draft, re-runs preview, and does not carry ghost terms from the prior session.
7. Force an acceptance rejection and a hard stop. Confirm `confirm_settlement` is absent from `options[]` and `available_action_ids[]`, no disabled `Ratify Settlement` button is rendered, the blocked-ratification banner names the blocker, and the backend refuses mutation even if called directly.
8. From the same blocked popup, confirm SC-28 / SC-28b recovery behavior: active war payloads show `Open War Detail` or a valid edit route; archived payloads show `Open Settlement History`; malformed unrecoverable payloads show terminal close copy. Confirm the popup does not emit direct `propose_armistice`, direct `propose_peace`, `Seek Armistice Instead`, `Seek Bilateral Peace`, disabled Revise, disabled Ratify, `Ask for terms`, `Surrender terms`, or enemy-offer waiting controls. From War Detail, confirm pair-scoped Bilateral Peace / Armistice controls appear only when eligible, and otherwise show no-current-pair-alternative copy.
9. Run the rejected/losing smoke variant (`SOVEREIGN_SMOKE_START=settlement_losing` or `settlement_rejected`). With France losing badly against a Britain-led coalition, open Settlement, attempt a winner-favored package and observe rejection, then use the editor's concession baseline or offer-mode controls to author a concessionary package with France as payer/ceder. Confirm acceptance moves toward accept/near-accept, clause copy reads as an offer/concession in treaty voice, direction labels distinguish demanded and conceded clauses, and no enemy-offer waiting, ask-for-terms, surrender, or direct pair-action control appears while SC-5 / SC-28b are deferred.
10. Trigger stale state before confirm. Confirm the popup shows a humanized stale reason, includes an actionable recovery route such as `Open War Detail` or `Open Settlement History`, and does not strand the player in an invisible hard stop.
11. Incoming-offer branch. If SC-5 is implemented by explicit reversal, confirm the offer is naturally produced, mailbox/pending-envoy routes render settlement review, and accept/reject/request revision avoid generic fallback. If SC-5 remains deferred, confirm mailbox count, top-bar/pending-envoy, notification rail, dispatch, popup queue, and Godot routes expose no incoming settlement offer, no enemy-offer waiting control, and no offer-blocked turn state; a stale/debug-injected offer must fail gracefully without becoming a usable player offer.
12. Ratify an accepted settlement. Confirm result feedback names mutations, unresolved pairs, beneficiaries/ignored parties, and routes active wars to war detail while archived settlements focus the ledger row.

If any smoke step fails, the spec returns to NO-GO and re-enters the relevant Gate 2 slice. Smoke pass requires all 12 steps green.

## Interim-Hide Artifact Example

Worked example: hiding `Revise Terms` during G2-Slice-1 while the editor is being built.

- Owning SC row: SC-2.
- Restoring implementation slice: G2-Slice-1 Foundation.
- `docs/STATUS.md` tracking line: "Revise Terms hidden pending real settlement editor; restore in G2-Slice-1 before slice closure."
- CI/test gate: a focused test fails if `Revise Terms` appears without `can_edit_terms=true` and an edit-capable route, and also fails if G2-Slice-1 is marked complete while `Revise Terms` remains hidden without an explicit product deferral.

## Completion Criteria

This spec is complete only when:

- No visible settlement button is a no-op or misleading label.
- Common peace is a real term-authoring settlement system: the player can author, preview, revise/counter, and ratify concrete war-scoped terms.
- G2-Slice-1 ships at least the required first-slice live clause set: `peace`, `territory_cede`, `gold_indemnity`, and `forced_alliance`.
- Submit revalidates authored terms before staging and cannot drift from the preview/conflict-matrix contract.
- Unratified settlement drafts have a scoped backend storage, serialization, and end-turn discard contract keyed by `war_id`, selected target, and covered-enemy scope; drafts are not lost, silently merged across different scopes, or silently carried stale across turns.
- End-turn draft discard produces a one-shot player notice or equivalent dispatch/campaign-log signal; loading after discard does not silently erase player-authored work without explanation.
- `Ratify Settlement` cannot mutate when the displayed acceptance verdict rejects or hard stops exist.
- The ratify option is absent from `options[]` and `available_action_ids[]` whenever the backend would reject for acceptance, below-threshold score, or hard stops; blocked copy and recovery routes replace the false affordance.
- Ratification consumes acceptance `threshold` from the scorer and surfaces acceptance-changed-after-staging failures through the pinned player UX.
- Ratification and all settlement entry/editor/refusal paths follow the approved SC-4b resource-cost contract; no opener, preview, revise, back-out, stale, blocked, or failed path hides a DP/AP/gold charge.
- Proposer-side and accepting-side leader changes both use fresh rescore rather than asymmetric automatic reopen behavior.
- Accepted ratification is atomic: previewed mutations match actual mutations, and failed ratifications do not emit settlement history.
- Common peace is absent from one-to-one war surfaces.
- Settlement UI actions cannot fall back to natural-language command text.
- Settlement UI command-fallback protection is keyed by dialogue family/type, so newly added or malformed settlement action ids cannot bypass the guard by missing a local whitelist entry.
- `route_id`, `war_id`, selected target nation, and active-vs-archived `review_target` survive confirmation, revise/stale reopen, result feedback, notification, dispatch, and ledger focus.
- Every production entry path writes top-level `selected_target_nation`; first-covered-enemy fallback is diagnostic-only.
- Executor and staging code explicitly forward `selected_target_nation`; the field is not only a Godot-side promise.
- Settlement `route_id` values are unique enough to focus the correct row when multiple settlements occur for the same `war_id` in the same turn.
- Selected target nation survives revise/stale reopen instead of falling back to alphabetic covered enemy.
- Wizard and typed/free-text common-peace entry both reject or disambiguate multiple shared wars instead of choosing a sorted/legacy fallback.
- Coalition settlement CTAs respect backend eligibility and multi-war coalition routes are actionable or explicitly hidden with approved no-action copy.
- War-detail and war-status settlement CTAs respect active hostile-pair eligibility after partial settlements; unique-nation count alone is not enough.
- Stale-state recovery cannot loop indefinitely or strand the player in an invisible hard-stop dialogue; attempt 4 for the same `(war_id, turn)` uses the pinned choose-from-war-detail escape.
- Attempt-4 stale recovery returns a structured clickable recovery route to War Detail or Settlement History; pure prose recovery copy is not enough.
- Rejected/blocked settlement reviews follow SC-28 / SC-28b: real editor, war-detail, history, or terminal close routes only; no disabled Ratify, disabled Revise, direct popup armistice/peace, `Seek Armistice Instead`, `Ask for terms`, `Surrender terms`, or enemy-offer wait while the owning systems are deferred.
- Same-war restaging cannot overwrite an active authored settlement draft; compatible same-scope terms merge, different-scope attempts choose/replace/reject without clobber, conflicts reject with the active draft unchanged, and cross-war restaging rejects rather than queues or clobbers.
- Same-war merge semantics are type-keyed and deterministic; same-key differing values conflict instead of silently summing or replacing.
- Incoming settlement offers are either naturally producible and safe against stale state / wrong-popup fallback, or their player-facing affordances are hidden with explicit deferral.
- Incoming-offer no-exposure tests enumerate mailbox, pending-envoy, notification, dispatch, popup queue, Godot branches, and producer soak; if incoming offers ship, mailbox payloads use settlement review schema plus stable offer identity.
- Incoming settlement-offer accept preserves offered terms and offer identity through live re-preview; request revision is a real counter/edit route or hidden.
- `settlement_confirm` explains beneficiaries, ignored parties, unresolved wars, acceptance blockers, hard stops, political costs, live awe/set-piece stakes, and clauses that will mutate.
- Losing-side concession authoring uses canonical clauses with visible `Demanded` / `Conceded` / `Mutual` direction labels, a deterministic Talleyrand baseline in the losing smoke fixture, and acceptance components that move in the accepting side's direction.
- Blocked acceptance displays hard-stop reasons without misleading `0 / 50` score copy.
- Settlement player surfaces do not show raw verdict enums, developer payload errors, outgoing voice for incoming offers, or production metadata named as debug-only.
- Tests include behavior-level coverage for the player paths that regressed, and source-string tests have behavior twins or are retired.
- Critical Godot settlement scripts parse/load or have a per-slice explicit, approved tooling deferral in `docs/STATUS.md` plus manual smoke evidence.
- Godot tooling deferral does not silently extend past G2-Slice-3.
- Diplomatic ledger and dispatch merge settlement and bilateral peace history into one reverse-chronological `PEACE & SETTLEMENT HISTORY` surface with row-level type tags, a combined cap, no overlapping-nomenclature sections, and route focus landing on the intended row.
- Common-peace treaty metadata stores documented raw settlement harshness and legacy clamped harshness under separate fields, and named common-peace consumers read the raw field.
- Player-facing settlement copy uses `Settlement` consistently; `common peace` remains internal/backend terminology.
- Old save free-form event-log text is historical and stable; new generated settlement renders use the approved vocabulary.
- `docs/STATUS.md` records v0.22 review traceability, SC-27 scan status, and the cleanup as complete only then reopens Slice G / later settlement agency work.
