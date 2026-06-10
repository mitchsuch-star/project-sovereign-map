# Settlement Gate-4 Pre-flight Audit — losing/rejected scenarios + Re-front holistic review

**Status:** **PF-1 + PF-2 + PF-3 LANDED on master June 9, 2026** — defect ledger D1–D6 FIXED; D7 stays latent (structural cure is CH-5, §9). The `settlement_losing` smoke is UNBLOCKED (the fixture now opens to a validator-clean baseline with honest holdout bands and the DC-2 binding-constraint guidance; blocked ratifies re-attach with a rendered reason). Verification: `tests/test_settlement_gate4_preflight_pf1.py` (12), `tests/test_settlement_gate4_preflight_pf2.py` (4), `tests/test_settlement_baseline_scenario_matrix.py` (36 — the §6 standing harness); full suite green; ruff clean; Godot 4.4.1 parse 0 failures.
**Smoke re-sequencing (user decision, June 9, 2026):** the Gate 4 manual settlement smoke is deferred to run ONCE at the END of the settlement queue — after the Guided Terms gate (with §7 GT-A1..4 folded) and the remaining queued settlement items — NOT immediately after PF-1. Rationale: this pre-flight audit plus the PF-3 scenario matrix already caught the defect classes the per-slice manual smoke targeted; one consolidated end-of-queue smoke covers the integrated surface. The smoke retains its owner (Gate 4, `SETTLEMENT_UI_CLEANUP_SPEC.md` v0.32) and its completion definition (the §"Verification focus" scenarios incl. `settlement_rejected` + `settlement_losing`); only its position in the sequence changed.
**Date:** June 9, 2026 (audit); PF slices landed June 9, 2026
**Method:** Static trace + read-only in-memory simulation of the exact `SOVEREIGN_SMOKE_START` fixture worlds, driving the real staging/dial/submit/ratify handlers (no server, no file mutation), plus a Godot-layer render/routing audit and a diplo-wide design sweep. Headline defects (D1, D2 mechanism, D3 mechanism, D4) were re-verified line-by-line by hand; remaining cites are agent-traced (re-verify line numbers before patching — see §12 confidence key).
**Scope:** the Settlement Conversational Re-front (`SETTLEMENT_CONVERSATIONAL_REFRONT_SPEC.md` v0.6, Slices 0–3 + REFRONT-V landed) at its current Gate-4-smoke state, plus design / UX / code-health / diplo-wide commentary requested by the user.
**How to use this doc:** PF-1 (§4), PF-2 (§5), and PF-3 (§6) are LANDED — do not re-implement them. **GT-A1..4 are FOLDED (June 10, 2026)** into `docs/SETTLEMENT_GUIDED_TERMS_SPEC.md` **v0.2** together with the Guided Terms Run #1 audit (`docs/SETTLEMENT_GUIDED_TERMS_AUDIT.md`, GO-with-changes) — do not re-fold them. A fresh session should (1) obtain **user approval of Guided Terms v0.2** (design gate — DO NOT CODE without user approval; decision D4 needs explicit confirmation), (2) work the remaining settlement queue (REFRONT-9 folds into the Guided Terms expanded row per GT-A4; §9 code-health CH-1..7; then cleanup-spec Slice G1), (3) run the **single end-of-queue Gate 4 manual smoke** (`settlement_rejected` + `settlement_losing` + the v0.32 verification-focus scenarios), then Slice G. Defect ownership lives HERE (PF slices below), not in `BUG_FIXES.md` (closed queue with a no-new-PL-items scope guard).

---

## 1. Why this doc exists

Gate 4 manual settlement smoke is in progress. Smoke 1 (`settlement_multilateral`, France winning) surfaced six findings, all fixed on master (see `STATUS.md` May 30–31 entries). Before the human smokes the NEXT two scenarios (`settlement_losing`, `settlement_rejected`), this audit pre-flighted them end-to-end and found the losing path **blocked by two CRITICALs** that are the losing-direction mirror of the already-fixed winning-side bug (the May 30 package-harshness relaxation fixed demand courts only). It also captures the full design/UX/code-health review so those recommendations are not lost between sessions.

Fixtures (`backend/models/world_state.py`): `settlement_rejected` (:879) — France vs Britain+Prussia, `france_score=-70`, enemy exhaustion 5, France gold 800. `settlement_losing` (:893) — same war, `france_score=-85`, exhaustion 0, Waterloo planted as France's only non-home/non-capital cedeable region, France gold floored to 1500 (:904–917).

---

## 2. Defect ledger

| # | Sev | One-line symptom | Verified |
|---|-----|------------------|----------|
| D1 | **CRITICAL** | Talleyrand's losing-side auto-baseline is invalid-by-construction (region double-promised + treasury double-spend) yet shows "This peace carries" | by hand |
| D2 | **CRITICAL** | Submit→Ratify on that baseline is an infinite dead-end loop with a literal red `"Response processed"` and no popup | by hand (both ends) |
| D3 | MAJOR | Tier-2 dials (incl. holdout one-click Ease) brick as silent no-ops when restage revalidation fails | mechanism by hand |
| D4 | MAJOR | Back Out's "Settlement draft kept" is a broken promise — reopen never restores (draft-key scope mismatch) | by hand |
| D5 | MINOR | Carry hint instructs "use More generous until each accepts" in states where solvency makes that unreachable | agent |
| D6 | MINOR | Targeted-posture advisory says "I'd press Britain, Prussia, Sire" on a war France is losing −85/−85 | agent |
| D7 | MINOR | Latent true-orphan: replacement-stage validation failures (`re_author_with_concessions` / preset family) lack the Tier-2 re-attach net under a **blocking** REVIEW | agent, static |

### D1 — CRITICAL — losing baseline invalid-by-construction (false "carries")

- **Symptom:** Open Settlement on `settlement_losing` → PROPOSE shows Britain accept(62) / Prussia accept(62), "This peace carries" — but the package is `[peace, 1000g→Britain, cede Waterloo→Britain, 1000g→Prussia, cede Waterloo→Prussia]`: Waterloo promised to BOTH courts (V1 `region_double_promised`) and 2,000g committed from a 1,500g treasury (`gold_payment_budget_conflict`).
- **Root cause (hand-verified):** `compute_settlement_baseline`'s per-court loop carries **no cross-court state** (`settlement_preview.py:2479-2539`). `_concession_terms_for_court` sizes gold per court against the FULL treasury (`payer_balance - CONCESSION_BASELINE_TREASURY_RESERVE`, `:2605-2616`) and `_concession_baseline_select_transferable_region` (`:1475-1555`, called at `:2634-2646`) has no already-promised-region exclusion. `_relax_baseline_demands_for_package_harshness` (`:2316`) repairs the **demand** direction only (`_is_demand_clause` requires `from==court`, `:2356-2361`) — it never strips concessions, so it never repairs an over-conceding table. Neither `build_settlement_preview` (`:3752-3762`) nor `stage_settlement_confirm` (`:5554-5563`) validates a *generated* baseline; `compute_per_court_acceptance` is validation-blind, hence the false carry.
- **Generalizes:** any losing multi-court table with treasury > 1000 double-spends gold (2×(T−500) > T); any losing multi-court table with one prime cedeable region double-promises it.
- **Fix sketch:** thread a running gold budget + promised-region set through the court loop (split `treasury_candidate` across concede courts; pass `excluded_regions` into the region selector), and run `validate_settlement_terms` on every **generated** baseline before staging (PROPOSE mount + dial/coverage redraw). See PF-1.

### D2 — CRITICAL — Submit→Ratify infinite dead-end loop

- **Symptom:** Submit for Review re-stages the invalid package into REVIEW with `can_ratify=True` and a live Ratify button (the per-court §11.4 gate passes at 62/62; the `submit_settlement_for_review` arm `:7570-7605` does not validate). Ratify hits the Slice-3 V1–V5 defense-in-depth gate (`:6552-6580`) → correctly blocks → **dialogue popped with no `diplomatic_dialogue`, no `must_reopen`, and the handler's text not passed through**. `/respond_to_diplomatic_dialogue` then defaults `message="Response processed"` (`backend/main.py:1396`) and the PL-14 popup net fires only on `success=True` (`main.py:1402-1409`), so Godot prints literally "Response processed" in red (`main.gd:1280`) with no popup. Reopening from War Detail regenerates the SAME invalid baseline → loop. Only escape: manual repair in the Tier-3 editor (whose own submit-failure path DOES remount inline — `main.gd::_maybe_remount_settlement_editor_after_error`, `:1099-1119`).
- **Fix sketch:** D1's validate-at-stage removes the trigger; additionally (defense): a blocked ratify should return the staged dialogue (re-attach, like the Tier-2 net) + an `error_display` the client renders; `/respond_to_diplomatic_dialogue` should pass the handler's message through instead of defaulting. See PF-1 and the CH-5 invariant (§9).

### D3 — MAJOR — silent no-op dials

- **Symptom:** when a dial's restage revalidation fails, the popup blinks and nothing changes — no error anywhere. On `settlement_losing` every dial fails from the first click (D1's invalid package). On `settlement_rejected` turn 1 (gold 800) exactly one table-ease works (300→400 each = 800 = capacity), then all dials fail `gold_payment_budget_conflict`; on turn 2+ (gold ~1227) the regenerated baseline is itself over budget (727×2 > 1227) so **all dials, including the holdout row's one-click Ease, are dead from the first click**.
- **Root cause (mechanism hand-verified):** `_restage_settlement_after_redraw` failure (`:3221-3239`) is correctly re-attached by the Tier-2 safety net (`:7489-7499`, hand-verified) so the unchanged dialogue re-mounts — but `main.gd::_route_proposal_confirm_response` (`:969-976`) re-shows the popup and **returns before the error branch** (`:1183-1184` vs `:1280`), and neither the route nor `proposal_confirm_popup.show_dialogue` reads `error_display`. The popup hides on every affordance click (`proposal_confirm_popup.gd:1015-1027`) then repaints identical state.
- **Fix sketch:** render `error_display` (amber/red line) whenever the proposal-confirm route re-mounts a response with `success=False`; PF-1's budget fix removes the most common trigger.

### D4 — MAJOR — "draft kept" promise broken (scope-key mismatch)

- **Symptom:** PROPOSE → dial (e.g. 400/400) → Back Out ("Settlement draft kept. Reopen Settlement to continue editing.") → reopen same turn → progress silently reverts to a fresh baseline; `draft_restored_from_scope=None`.
- **Root cause (hand-verified):** suspend saves under `compute_settlement_draft_key(war, target, [Britain, Prussia])` (`settlement_preview.py:7510-7529`; key fn `:453-469`) AND dual-writes the legacy `pending_settlement_drafts[war_id]` store (`:7518-7522`). The only real reopen route sends `{target_nation, war_id}` with no covered list (`main.gd:3849-3857`) → `_execute_propose_common_peace` loads with `covered=[]` (`diplomatic_executor.py:2074-2098`, hand-verified) → different hash → miss; the legacy store is never consulted on load. The SC-5R-2 round-trip test passes `covered_enemy_participants` explicitly (`tests/test_settlement_sc5r2_godot_editor.py:405-414`) so the real client shape was never exercised.
- **Fix sketch:** make `load_scoped_settlement_draft` fall back to a `(war_id, target)`-prefix scoped lookup (or consult the legacy store), and add a "Draft kept" badge to War Detail so the promise is visible AND true. See PF-2.

### D5 — MINOR — carry hint promises the impossible

`_settlement_propose_carry_hint` (`:3121-3156`) says "Use 'More generous' (or ease a court) until each accepts, then 'Submit for Review'" even when the solvency ceiling caps reachable acceptance below threshold — steering the player into D3's silent wall. After PF-1, the hint should detect the budget-bound case and pivot to the binding-constraint guidance (DC-2, §7): drop a court or pay in land.

### D6 — MINOR — advisory presses the winners

`_settlement_targeted_posture_advisory` (`:3072+`) renders "I'd press Britain, Prussia, Sire — the table is yours to shape" on a −85/−85 war. Downstream of D1's false bands, but deserves its own guard: never recommend "press" on a concede-direction court.

### D7 — MINOR — latent orphan on replacement-stage failures

`_stage_replacement_settlement_terms` validation failure (`:7000-7015`) returns no `diplomatic_dialogue` while the **blocking** REVIEW stays mounted; the re-attach net (`:7489`) covers only the 5 Tier-2 verbs, not `re_author_with_concessions` / `author_*` / `keep_current_settlement_draft` / `apply_*_replacement`. Not reachable on the two pre-flighted fixtures (the legacy single-court presets validate) — flagged latent. The structural cure is CH-5 (§9), not another per-arm patch.

---

## 3. Verified-OK ledger (do not re-litigate during the smoke)

- `settlement_rejected` turn-1 PROPOSE renders correctly: concede baseline 300g+300g, both courts reject(−6), `direction_summary` "Conceded: 300g", holdout rows expose Ease+Drop, dialable rows expose Press, advisory + carry hint present. Press-to-zero drops the clause and the focused seed flips to "Demanded: 100g" without crashing (see DC-4 for the design note).
- **Blocked-REVIEW contract fully wired and 3-way consistent** (backend `handle_settlement_dialogue_action` arms ↔ executor dispatch `diplomatic_executor.py:2899-2961` ↔ Godot whitelist `main.gd:35-98`): `confirm_settlement` omitted from `options[]` AND `available_action_ids`; rail = Re-author with Concessions, Offer Gold Over Time, Return to terms, Make peace with Britain only, Armistice with Britain only, Open War Detail, Back Out. Exercised each: `return_to_settlement_terms` re-stages PROPOSE preserving terms; pair substitutes stage bilateral `proposal_confirm`; `open_war_detail` pops + returns `recovery_route(surface=war_detail)`; `back_out_settlement` discards.
- Coverage edits: Drop Britain re-drafts for [Prussia] with `ignored_participants` + "Britain remains at war"; last-court Drop hidden on the row AND blocked server-side with dialogue re-attach (the May-31 drop-stranding fix holds).
- End-turn lifecycle: mounted non-blocking PROPOSE does not survive `advance_turn`; both draft stores cleared; one-shot "Unratified settlement draft discarded at turn end." notice queued and rendered (`main.gd:1165-1169`); next-turn reopen regenerates cleanly.
- Transport: `CommandRequest` declares `settlement_terms`/`selected_target_nation`/`covered_enemy_participants` (`main.py:765-779`, forwarded `:984-989`); `/respond_to_diplomatic_dialogue` is a raw dict so `action_params` survives (`:1388-1391`); editor Submit failures remount the editor with inline error text.
- `<null>` regression fixed: `_safe_str` coalesces per-court fields (`proposal_confirm_popup.gd:490-495`).
- `_relax_baseline_demands_for_package_harshness` never strips concessions, as documented (by design — which is exactly why it cannot repair D1).
- Focused suites green at audit time: `test_settlement_carry_guidance_ux.py`, `test_smoke_start_settlement_multilateral.py`, `test_settlement_concession_baseline.py`, `test_settlement_refront_slice1/2/3.py` — 88 passed.
- REFRONT-9 (focused breakdown panel) intentionally unbuilt per spec; `settlement_focus_court` presentation-only and works — not a defect.

**The decisive test gap:** no test in the ~10,331 builds a **two-concede-court table with the real scorer**. The losing-smoke test pins only the LEGACY single-court `concession_baseline` (`tests/test_settlement_concession_baseline.py:602`); Slice-1's valid-by-construction test materializes at most one concede court (`tests/test_settlement_refront_slice1.py:222`). This is why six doc audits missed D1 (see DC-6).

---

## 4. Fix slice PF-1 — losing-baseline validity + failure-path visibility — **LANDED June 9, 2026**

- **Scope (backend):**
  1. Thread cross-court state through `compute_settlement_baseline`'s loop: a running gold budget (split `treasury_candidate` across concede courts — even split is fine for the baseline; the player redistributes via dials/Tier-3) and a promised-region exclusion set passed into `_concession_baseline_select_transferable_region`.
  2. Validate every **generated** baseline with `validate_settlement_terms` before staging (PROPOSE mount, dial/coverage redraw, `submit_settlement_for_review`). A baseline that cannot validate after relaxation degrades per court to the `{"type":"peace"}` floor for the unaffordable remainder (never stage invalid; never crash).
  3. Pass the handler's message through in `/respond_to_diplomatic_dialogue` (`main.py:1396`) instead of defaulting to "Response processed"; blocked-ratify returns re-attach the staged dialogue + `error_display`.
  4. D6 guard: advisory never recommends "press" on a concede-direction court.
- **Scope (Godot):** render `error_display` when the proposal-confirm route re-mounts a `success=False` response (`main.gd::_route_proposal_confirm_response`).
- **Completion:** `settlement_losing` opens to a VALID baseline (validator-clean), with honest per-court bands; an unaffordable table opens as holdouts with the binding-constraint guidance (DC-2), not a false carry; no settlement action can leave the player with neither a popup nor a rendered reason; full suite green; ruff clean; Godot parse exit 0.
- **Named tests:** `test_losing_multicourt_baseline_validates_clean` (runs the real `settlement_losing` fixture; fails pre-fix on `region_double_promised` + budget), `test_losing_baseline_splits_treasury_across_concede_courts`, `test_generated_baseline_is_validated_before_staging_propose_and_submit`, `test_blocked_ratify_reattaches_dialogue_with_error_display`, `test_dialogue_response_passes_handler_message_not_default`, `test_failed_dial_renders_error_display_not_silent_noop` (Godot source pin), `test_advisory_never_presses_concede_direction_court`.

## 5. Fix slice PF-2 — draft-restore honesty (D4) — **LANDED June 9, 2026** (suspend/dial lifecycle now single-store scoped; restore falls back (war, target)-prefix → war-prefix, most recent wins; cross-war isolation retained)

- **Scope:** `load_scoped_settlement_draft` falls back to a `(war_id, selected_target)`-prefix scoped lookup when the exact key misses (or consults the legacy `pending_settlement_drafts[war_id]` — then DELETE whichever store loses; do not keep both — CH-3); War Detail gains a "Draft kept" indicator when a same-turn scoped draft exists for that war.
- **Completion:** Back Out → reopen restores the dialed terms on the REAL client payload shape (no explicit covered list); the badge appears iff a draft would actually restore; suite green.
- **Named tests:** `test_reopen_without_covered_list_restores_scoped_draft` (HTTP-boundary shape, NOT executor-direct — the D4 lesson), `test_war_detail_exposes_draft_kept_indicator`, `test_single_draft_store_no_dual_write`.

## 6. PF-3 — scenario-matrix fixture harness (the systemic guard) — **LANDED June 9, 2026** (36 tests: 18 cells × {validity+honest-carry, Tier-2-verb invariant}; courts axis = COVERED courts of a multi-party war, since a strict 1v1 war is settlement-ineligible by design)

A standing parametrized suite: direction {winning, losing, mixed} × covered courts {1, 2, 3} × treasury {rich, poor}, asserting for every cell: (a) the generated baseline passes `validate_settlement_terms`; (b) `overall_acceptance.carries` claims match a fresh scorer pass; (c) every Tier-2 verb on the resulting table either succeeds or returns a dialogue + `error_display`. ~18 cheap tests that would have caught D1, D2, D3, and the May-30 5/-4 winning-side finding before any human smoked anything. **Owner:** lands with or immediately after PF-1. **Named test file:** `tests/test_settlement_baseline_scenario_matrix.py`.

---

## 7. Design commentary (fold into the relevant gates; do not lose)

- **DC-1 — The asymmetric validity guarantee is the real design lesson of D1.** The spec's core promise — "you can never author the illegal" — was implemented as a guarantee about the PLAYER (five validators, filtered pickers, submit revalidation, ratify defense-in-depth) while the system author was exempted. Talleyrand is currently the only actor who can put an illegal package on the table — and he does it with a "this peace carries." Principle to write into the spec: **valid-by-construction is a property of the draft STORE, not of the author** — one validation choke-point at staging, for everyone. (The May-30 winning-side 5/-4 finding was the same missing invariant: system-authored output scored differently than it was constructed.)
- **DC-2 — Carry gate × solvency is a design hole, not just a bug.** Even after PF-1 splits the budget honestly, carrying a full losing table can be genuinely unaffordable (750g each may leave both courts <50). The system's current answer is silence (D5's hint denies it). The right answer is already spec principle 5 — "Talleyrand reasons across the table and flags the binding constraint": *"Sire, we can afford peace with one of these courts, not both. Ease Prussia and let Britain fight on — or pay in land."* The Pressburg/Tilsit framing that justified the per-court gate cuts both ways: France in 1813 could not buy peace from everyone, and the game should SAY so. **Owner:** the binding-constraint voice line + budget-bound hint variant land with PF-1 (copy through the Voice Bible — error/constraint paths must stay in character too); the fuller per-court allocation UX belongs to the Guided Terms gate (GT-A1/GT-A2).
- **DC-3 — Per-court ratification gate: endorse without reservation.** Best single design decision in the arc — honest UI (displayed acceptance IS the gate), period-correct holdout drama, and Ease/Drop keeps it from ever hard-walling. The May-31 carry-UX fix (`propose_carry_hint` + `return_to_settlement_terms`) was the right repair to its one trap.
- **DC-4 — Dial semantics: clean, with one absurdist corner.** `_redial_settlement_terms` (`settlement_preview.py:2970-3069`) is a tidy magnitude/count-only transform honoring OQ#7. But pressing a court France is losing to, past zero concessions, makes the focused seed author `gold_indemnity from: court` (`:3055-3068`) — **demanding tribute from the nation that is beating you.** Legal (player agency; the scorer tanks it), but Talleyrand authors it wordlessly. One voice guard line ("They are not the ones suing for peace, Sire — but as you wish") turns an absurdity into characterization. **Owner:** REFRONT-V family extension, can ride PF-1 or GT-Slice-5.
- **DC-5 — Guided Terms spec (v0.1): approve the direction, with amendments before approval:**
  - **GT-A1 — Shared-budget as a first-class row concept.** When multiple courts take gold, the per-court rows must show allocation against ONE visible treasury line ("1,500g: Britain 750 / Prussia 750 / reserve 0"). Otherwise the guided flow recreates D1's over-commit invisibly, with the player driving.
  - **GT-A2 — Own the losing-multi-court allocation question as a new OQ.** Who gets eased first when you cannot afford both? Talleyrand's recommendation rule must be specified (determinism — Golden Rule #6 — means it cannot be vibes).
  - **GT-A3 — Lead §1 with the editor-blindness cure.** The current Tier-3 editor has NO live acceptance while authoring (you find out at REVIEW); the guided model's inline row mutations re-scoring live is the single biggest player-experience win in the document — a stronger selling point than the France/France default.
  - **GT-A4 — OQ-5 (fold REFRONT-9 into the expanded row): yes.** The focused breakdown was always going to be homeless on a surface scheduled for demolition.
  - Also: the merge/replace dissolution (§6) is the most elegant part of the spec — deleting the submit-blob deletes D7's entire latent-orphan class with it.
- **DC-6 — Spec-process meta: rebalance doc audits toward runtime fixtures.** The re-front spec was audited SIX times pre-approval, with real early yield (the `select_direct_score` tuple catch) but collapsing marginal value by run 5 (version-string drift). Both CRITICALs here were findable only by RUNNING the code on a fixture the tests didn't have (§3 test gap). Recommendation: cap doc audits at two; spend the savings on the PF-3 scenario matrix. A spec audit verifies the map; only a fixture verifies the territory.

---

## 8. UX/UI findings (Godot layer)

- **UX-1 — War Detail shows nothing about an existing draft.** No "draft kept" badge or resume affordance — also why D4 went unnoticed. Owner: PF-2.
- **UX-2 — REVIEW and PROPOSE render identically.** `_build_settlement_content` has no `dialogue_mode` branch; the only state signal is which buttons appear. REVIEW should read as a staged-decision surface (terms frozen, blockers promoted, dials gone). The May-31 "Submit looked like it failed" confusion was partly this. Owner: small Godot slice, can ride PF-1 or GT-Slice-3.
- **UX-3 — Editor picker defaults are silent** (`settlement_editor_popup.gd:443-459`): first option auto-selected, no "-- Select --" placeholder — the residual France/France hazard for direction-chosen roles (territory/gold), since only fixed-direction roles got side-disjoint lists. Moot if Guided Terms lands (the editor is retired); fix only if GT slips.
- **UX-4 — Null-guard coverage is partial:** `_safe_str` protects the per-court loop but not top-level fields — a null `war_label` renders "Settlement of <null>" (`proposal_confirm_popup.gd:234`). One-line guard.
- **UX-5 — Per-court table has no scroll container** (`proposal_confirm_popup.gd:497-558`) — fine at 2–3 courts, unbounded at full-1805 scale (Golden Rule #8 horizon). Owner: note on REFRONT-7's scale row or GT-Slice-3.
- **UX-6 — Error copy breaks voice.** "Response processed" (D2) and "The submitted terms failed validation; review and correct them" (shown for TALLEYRAND'S OWN draft) both blame the player. Voice Bible discipline should extend to error paths — errors are when the player most needs the advisor in character. Owner: PF-1 copy pass.
- **UX-7 — BBCode palette hardcoded per-popup**, drifting from `utils.gd` (R15's whole purpose). Owner: CH-6.
- **UX-8 — Editor REVIEW-handoff guard missing** (`main.gd:948-965`): if a backend response ever carried `open_editor_on_mount=true` on a REVIEW stage, the editor would re-mount over REVIEW. Cheap belt-and-suspenders gate on `dialogue_mode`.
- **UX-9 — Genuinely good (keep):** per-court rows with named-diplomat voice lines are the standout surface in the game; Tier-2 affordances are honest buttons (post the inert-pseudo-link fix); the amber carry hint placement works; the editor's inline submit-error remount works.

---

## 9. Code health & elegance recommendations

- **CH-1 — Split the 9,470-line `settlement_preview.py` god module** (~120 defs spanning validity, baseline, staging, dials, ratify/apply, draft stores, incoming offers, ally petitions, recurring payments). The def map shows clean seams: validators (~`:3389`), baseline generation (~`:2050-2790`), dialogue/staging (~`:4543-5639`), ratify/apply (~`:5671-6909`), offers/petitions (~`:8526+`), recurring payments (~`:9769`). Precedent: the R10–R13 executor split paid off; settlement deserves the same — five modules, mechanical move, zero behavior change. **Owner: post-Gate-4 refactor slice (do NOT interleave with the smoke).**
- **CH-2 — `handle_settlement_dialogue_action` is a ~950-line if-chain** (`:7426-8379`). Convert to a dispatch table (action → handler fn); rides CH-1.
- **CH-3 — Two draft stores must become one.** Legacy `pending_settlement_drafts[war_id]` + scoped `pending_settlement_drafts_by_key`: suspend dual-writes both (`:7518-7529`), reopen reads one with the wrong key — D4 is the direct cost of the duplication. PF-2 picks the survivor; CH-3 deletes the loser everywhere.
- **CH-4 — Legacy `_compute_concession_baseline` retained alongside its generalization** `compute_settlement_baseline` (used by the single-court preset/`re_author_with_concessions` family). Converge on the per-court generalization (n=1 is the degenerate case the spec itself promises) and delete the legacy path. Rides CH-1.
- **CH-5 — Replace accreting per-arm safety nets with ONE structural invariant:** *every settlement handler returns either a `diplomatic_dialogue` or a rendered `error_display` — never neither.* Each smoke finding so far (drop-stranding orphan, D2's "Response processed", D3's silent dials, D7's latent preset orphan) is this invariant violated at a different arm. Enforce it in one wrapper around `handle_settlement_dialogue_action` + a response-shape test, instead of the current 5-verb net (`:7489-7499`) plus future patches.
- **CH-6 — Centralize BBCode colors** (popups hardcode hex like `#e0c070`/`#e0a040` instead of a shared map next to `utils.gd` COLOR_ consts).
- **CH-7 — Test-shape rebalance.** The suite is enormous and rigorous (~10,331) but skewed: many source-grep pins and single-court fixtures; zero two-concede-court live-scorer fixtures (§3); HTTP-boundary shapes under-covered (the D4 test passed the field the client never sends; the May-31 Pydantic strip shipped for the same reason). Rules of thumb to adopt: every smoke fixture gets a test that drives the REAL fixture end-to-end; every client→backend contract gets at least one test through the actual HTTP boundary with the actual client payload shape; PF-3 is the standing harness.

---

## 10. Diplo & game-as-a-whole commentary

- **DW-1 — Settlement is the deepest, best-written surface in diplomacy — and it's a table only France can sit down at first.** The AI cannot open a settlement (cleanup Slice G1 unbuilt), AI proposal triggers P3–P6 (opportunism, alliance-breaking, preemptive coalition, breakaway peace) are deferred, and incoming offers have a producer but not the full lifecycle. The diplomatic world is REACTIVE. **After Gate 4, Slice G1 is the highest-leverage item in the entire diplo arc** — it converts the settlement machinery from a player tool into a living world where Hardenberg sues for peace before you ask.
- **DW-2 — Two acceptance models now coexist** (bilateral formula vs the 10-component settlement scorer). The spec frames bilateral as "n=1 of the same model" — true at the gate level, not the scoring level; every tuning pass pays the tax twice. Not urgent; queue a convergence note for the ROADMAP 8.EVAL pass.
- **DW-3 — Creative-audit (6.5/10) items, revisited:** Talleyrand-monotone is genuinely fixed — the Voice Bible per-court registers (Castlereagh institutional cold, Hardenberg "Prussia remembers", Metternich smiling calculus) are doing real characterization work in the settlement rows. The big open one remains **"diplomacy strategically optional vs military."** Settlement helps (peace now has texture and price), but strategic PARITY usually comes from economic diplomacy (subsidies, trade leverage, the Continental System as an actual lever) — specced-but-unbuilt. Point the post-8.EVAL design budget there.
- **DW-4 — Missing-feature shortlist ranked by leverage:** Slice G1 incoming offers ≫ AI P3–P6 opportunism > economic diplomacy > marriage alliances (flavor) > congress system (correctly CUT per SC-32 D5).
- **DW-5 — What deserves explicit praise (so this audit isn't read as gloom):** the deferral-ownership rule (Golden Rule #9) demonstrably works — the REFRONT-8/9 trail is the cleanest "we didn't build the thing" handling on record; the determinism rule held everywhere inspected (`delta_display` presentation-only, advisory voice-only, no RNG near mechanics); and grounding the per-court gate in Pressburg/Tilsit gives the game an identity, not just a feature list.

---

## 11. Recommended sequencing (updated June 9, 2026 — PF slices landed; smoke re-sequenced by user decision)

1. ~~**PF-1** (D1–D3 + DC-2 binding-constraint copy + D6 guard).~~ **LANDED.**
2. ~~**PF-2** (D4 + War Detail draft badge).~~ **LANDED.**
3. ~~**PF-3** scenario matrix.~~ **LANDED** (`tests/test_settlement_baseline_scenario_matrix.py`).
4. Approve **Guided Terms** with amendments GT-A1..A4 folded (design gate — user approval required before code).
5. Remaining settlement queue: Guided Terms implementation (REFRONT-9 folds into its expanded row per GT-A4), **CH-1/CH-2/CH-4** split slice, **CH-5** invariant (closes D7's latent class).
6. **Gate 4 manual smoke — ONCE, at the end of the queue** (user decision June 9, 2026): `settlement_rejected` + `settlement_losing` + the v0.32 verification-focus scenarios, then **Slice G1**.

## 12. Confidence & verification key

- **by hand** = re-verified line-by-line in source during this audit (D1 root cause; D2 both ends — submit-arm gap inferred from STATUS by-design notes + ratify-gate + `main.py:1396` swallow + PL-14 success-only net; D3 backend net + main.py; D4 save/load both ends; dial seed `:3055-3068`; Tier-2 re-attach net `:7489-7499`).
- **agent** = produced by a read-only audit agent driving the real handlers on the real fixtures; high confidence but re-verify exact line numbers before patching (the file will drift as PF slices land).
- Line numbers are accurate as of master `395914a` (June 9, 2026).
