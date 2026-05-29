# Settlement Conversational Re-front — Cumulative Audit Note (v0.2 → v0.6)

**Audits:** `docs/SETTLEMENT_CONVERSATIONAL_REFRONT_SPEC.md` **v0.2 → v0.6** (cumulative — §2 = first pass → v0.2; §8 = Run #1 → v0.3; §9 = Run #2 → v0.4; §10 = Run #3 → v0.5; §11 = Run #4 → v0.6; §12 = Run #5 → v0.6 errata)

> **Numbering key (resolves a cross-doc drift):** this note leaves the unnumbered "first pass" uncounted, so its section label "**Run #k**" = audit pass **#(k+1)**. The spec changelog + CLAUDE.md count the first pass as audit #1, so they call v0.6 the "**fifth audit**" (= this note's Run #4) and the v0.6-errata pass the "**sixth audit**" (= this note's Run #5). Both schemes describe the same passes; use this key to reconcile.
**Date:** May 28–29, 2026
**Verdict (latest, Run #5 → v0.6 errata): GO; 2 MAJOR + 3 MINOR doc-accuracy items folded in place (no design change) — see §12.** The prior Run #4 (→ v0.6) verdict was also GO-after-fold. Run #4 synthesized two independent passes — a Claude pass returning **NO-GO** (1 CRITICAL + 1 MAJOR) and a Codex pass returning **GO** (2 MAJOR + 1 MINOR). Every finding was re-verified against live code and **folded into v0.6**; one Claude finding (DWL-SET-SC5R-3 cited at cleanup `:589`) was **withdrawn on verification** as a correct cite. With the rest folded, **v0.6 carries zero known CRITICAL/MAJOR** and is GO-ready for user approval (design gate — `NEEDS APPROVAL`; no code until approved). *History (first pass): GO-with-changes — 4 material change items folded into v0.2; details below.*

> This is a structured review pass against the project's coherence + Golden-Rule criteria, performed against the live codebase (every reuse claim was checked at file:line). It is not an independent third-party review; findings err toward surfacing risk rather than rubber-stamping.

---

## 1. Verdict summary

| Dimension | Result |
| --- | --- |
| Coherence vs `DIPLOMACY_SPEC.md` (bilateral flow) | **PASS** (with one framing correction, folded) |
| Coherence vs `SETTLEMENT_UI_CLEANUP_SPEC.md` (clause model, scorer, scoped draft, ratify gate) | **PASS** (with the per-court gate change surfaced + owned, folded) |
| Golden Rule #6 — deterministic mechanics (novelty presentation-only) | **PASS (strong)** |
| Golden Rule #8 — scale-ready (no per-turn hot-path region scans) | **PASS (with one shared-projection param added, folded)** |
| Reuse actually exists + extensible | **PASS** (all rows verified file:line) |
| No orphan deferrals (Golden Rule #9) | **PASS** |
| Interim band-aid scoped as independent de-risk | **PASS** |

---

## 2. Change items found (all folded into v0.2)

### C1 — Per-court ratification was understated as "wiring." **[FOLDED]**
**Finding.** The current settlement gate scores a **single `accepting_leader`** for the whole covered set (`build_settlement_preview` at `settlement_preview.py:2431-2444`; ratify `ratify_settlement_confirm:4583`); the acceptance formula's `burdened_participant_penalty` lowers the *leader's* willingness when allies are burdened. So today's design is "the coalition leader signs for the bloc with ally sympathy," and a multi-court settlement ratifies on the leader alone. The vision ("Prussia is the holdout," "never a blended number," §17 "with every covered court at/above threshold, Ratify") **requires** per-court gating. That is a **ratification-mechanics change**, not wiring, and it collided with the v0.1 §7 non-goal "not redesigning… ratification mechanics."
**Resolution (folded).** New **§11.4** locks the per-court gate (`carries` iff every covered court ≥ threshold; holdouts block but expose ease/drop; REVIEW carries `per_court_acceptance`). **§7** narrowed to "not redesigning the acceptance *formula*; the *gate* extension is in-scope and owned." Named test `test_ratify_requires_all_covered_courts_at_or_above_threshold_not_just_leader` added to Slice 1; the regression surface (existing leader-gated fixtures change verdict) is called out so a green-suite update is not mistaken for breakage. **User-approved** during authoring on UX + historical-analogue grounds (separate Napoleonic peaces; Britain fights on).

### C2 — PROPOSE hard-stop classification created an asymmetry. **[FOLDED]**
**Finding.** v0.1/early-v0.2 implied PROPOSE should block commands "like REVIEW." But the cleanup spec deliberately made settlement authoring **non-blocking** (`SETTLEMENT_UI_CLEANUP_SPEC.md:575`: "EDIT mode is not a hard stop… the player may end the turn from an editor draft"). Making PROPOSE a hard-stop while EDIT is not would turn `Adjust terms → EDIT` into an end-turn escape hatch and trap the player on the front surface.
**Resolution (folded).** **§10** classifies PROPOSE as an authoring surface — **not** a hard-stop, matching EDIT (end turn discards draft; Back Out preserves via `suspend_settlement_editor`). Only REVIEW/BLOCKED_TERMINAL remain hard-stops. Test `test_propose_does_not_block_end_turn_and_back_out_preserves_scoped_draft`.

### C3 — Per-court scoring didn't share the (package-level) balance projection. **[FOLDED]**
**Finding.** The scorer already accepts memoized `direct_scores` (:1896), `side_pressure_result` (:1895), and `raw_total_harshness` (:1897) — all package-level and shareable across the per-court loop. But `project_balance_after_settlement` (:1537) is also package-level (`(world, war_id, settlement_terms)`, independent of `accepting_leader`) yet has **no injection param**, so a naïve per-court loop would recompute it N times — an O(active_nations) snapshot per court per dial action. Acceptable today (small maps, user-initiated), but a scale smell for full Europe.
**Resolution (folded).** **§15** scale hook documents the three shared inputs and specifies **Slice 2 adds one memoization param** (`balance_projection=…`) mirroring the existing pattern, so the projection is computed once per dial action. Test renamed to `test_per_court_scoring_shares_one_direct_score_side_pressure_harshness_and_balance_projection_pass` (the `harshness` segment was added in the Run #4 fold — see §11 R4-m1; this §3 line is retained as the original C3 record).

### C4 — REVIEW needed the per-court block too, not just PROPOSE. **[FOLDED]**
**Finding.** If only PROPOSE carried `per_court_acceptance` and REVIEW kept the single `acceptance` object, the *gate* (REVIEW/ratify) and the *displayed reason* would diverge — the player could see "Prussia refuses" in PROPOSE but a single blended verdict at REVIEW.
**Resolution (folded).** **§11.4** requires REVIEW to carry `per_court_acceptance` (single `acceptance` retained for the n=1 bilateral case and as the leader-row summary). Test `test_review_payload_carries_per_court_acceptance`.

---

## 3. Coherence checks (detail)

### vs `DIPLOMACY_SPEC.md`
- **3-tier steering flow is a code property, not a DIPLOMACY_SPEC property.** That doc describes the older 2-turn propose→counter-offer flow; the `Harsher`/`More generous`/`Adjust terms` terms-guidance UI lives in `diplomatic_templates.py:226-296` + `diplomatic_executor.py` `modify_harsh:3101`. **No contradiction** — DIPLOMACY_SPEC simply predates the terms-guidance UI. v0.2 §3 adds an explicit coherence note and cites the code as source of truth. ✔
- **Transparency.** DIPLOMACY_SPEC's base flow hides the raw score/bands; the settlement re-front surfaces per-court bands. This is *more* transparent, not contradictory, and has precedent in `acceptance_breakdown` (`diplomatic_executor.py:392-432`) which already exposes score+components for feasibility. ✔
- **LLM never decides (design-philosophy / §6a).** Honored by §8 OQ#6 — novelty is deterministic input-richness + voice; LLM surfaces prose only. ✔
- **Target validity / self-reference.** DIPLOMACY_SPEC does **not** document these for bilateral. §12 V1–V5 are therefore net-new contract (the cure for the liberation bug), not inherited. Note (out of scope): bilateral diplomacy may have analogous unspecified gaps — a candidate future bilateral-hardening item, not a blocker here. ✔

### vs `SETTLEMENT_UI_CLEANUP_SPEC.md`
- **Picker contract already exists, never landed.** Line 601 mandates "Add Clause disabled when a clause type's picker has zero valid options… liberation with no valid vassal"; line 618 names `test_clause_add_disabled_when_picker_filter_empty_for_each_live_clause`. Verified in code: `_build_clause_control_schema_for_review` hardcodes `"enabled": True` (`settlement_preview.py:3001`); liberation's vassal field uses `vassal_options or nation_options or []` (`:2959`); the named test is **absent** from `tests/`. The §16 band-aid lands exactly this contract — **strong coherence** (the re-front finishes the cleanup spec's own intent). ✔
- **PROPOSE as a 4th mode** sits cleanly in front of the existing EDIT/REVIEW/BLOCKED_TERMINAL family; classified non-hard-stop to match EDIT's deliberate non-blocking (C2). ✔
- **Below-threshold gate.** §11.4 extends the existing "below threshold blocks ratify / omits `confirm_settlement`" rule (`:570/:597`) from a single score to every covered court — a generalization of an existing rule, not a new mechanic class. ✔
- **Payload reuse.** PROPOSE reuses the cleanup-spec preview request shape (`:543`); `per_court_acceptance` is additive; the single `acceptance` object is retained for n=1. ✔
- **Unchanged contracts.** Scoped draft store (`save/load/discard_scoped_settlement_draft:2676/2701/2721`), `suspend_settlement_editor`, and the fresh-rescore `ratify_settlement_confirm` gate are reused unchanged (gate logic extended per C1, not rewritten). ✔

---

## 4. Golden Rule compliance

- **#2 (ints to Godot):** §11.2 specifies all numeric payload fields via `int()`. ✔
- **#6 (deterministic; LLM never affects mechanics):** §8 OQ#6 enumerates the deterministic input set, **rejects** RNG/LLM-decided variation, marks `delta_display` presentation-only, and names `test_settlement_baseline_is_deterministic_same_world_same_terms`. The default-CUT presentation-variation item (REFRONT-6) carries a guard test that any future implementation must keep the scored result identical. **Strong.** ✔
- **#8 (scale-ready):** per-court scoring is user-initiated (not a per-turn AI loop), N = covered courts in one war (bounded), and shares one `direct_scores` + one `side_pressure` + one balance projection per dial action (C3). No per-court `world.regions` scan. Residual all-regions scan in the Tier-3 schema build is user-initiated and owned by REFRONT-7. ✔

---

## 5. Orphan-deferral check (Golden Rule #9)

All deferred/cut items have owner row + landing + completion + test:

| Item | Status | Owned where |
| --- | --- | --- |
| Incoming-offer per-court convergence | DEFER | §14 REFRONT-5 + test |
| Presentation-only novelty variation | CUT (default) | §14 REFRONT-6 + guard test |
| Region-scan scale hardening | DEFER | §14 REFRONT-7 + test |
| Inline merge-conflict Discard/Replace (`DWL-SET-SC5R-3`) | FOLDED into Slice 3 | §14 Slice 3 tests |
| Multi-court conference voice (Voice Bible gap B4) | NEW, owned | §14 Voice slice (REFRONT-V) + tests |
| AI-ally settlement agency (Slice G) | SEPARATE/LATER | unchanged, blocked behind Gate 4 |

No vague "future work" / disabled placeholder / unowned promise remains. ✔

---

## 6. Residual risks (accepted; not blockers)

- **RR1 — Regression surface (from C1).** Existing multi-court settlement tests/fixtures assume leader-gating and will change verdict under per-court gating. Updating them is expected; the suite must end green. Owned in §11.4 + Slice 1 completion. *Mitigation:* land Slice 1 with the fixture updates in the same commit so the diff is legible.
- **RR2 — Bilateral validity gaps (A4).** Bilateral diplomacy never formalized self-reference/target-validity rules; the re-front adds them only for settlement. Out of scope; candidate future bilateral-hardening item.
- **RR3 — REFRONT-7 deferred.** The Tier-3 all-regions scan stays until full-Europe; acceptable because it is user-initiated, once per POST-preview.
- **RR4 — Voice Bible conference family is net-new** (B4: the Bible has no multi-court rule). Owned by REFRONT-V with named tests; must be authored before Slice 1/2 copy is final.

---

## 7. Bottom line

v0.2 is coherent with both reference specs, deterministic and scale-ready by the Golden Rules, reuses verified machinery (with the genuinely-new pieces flagged), and has no orphan deferrals. The single real mechanics change (per-court ratification gate) is now surfaced, justified (UX + historical analogue), user-approved, and owned by a named test with its regression surface called out. The interim band-aid is correctly scoped as an independent de-risk that lands a contract the cleanup spec already promised.

**Verdict: GO-with-changes, changes folded → GO-ready for user approval.** The spec remains flagged `NEEDS APPROVAL`; implementation begins only after the user approves v0.2.

---

## 8. Run #1 — independent re-audit (May 28, 2026, folded into v0.3)

A second, independent audit pass was run against v0.2 under the `peace-deals-spec-audit` methodology (M1–M5, GO requires all ≥7 + zero CRITICAL). Every `file:line` reuse claim was **re-verified against the live code** (not trusted from the v0.2 note above). All cites held except the ratify location (see F-3). **Verdict: GO** (M1 Fun 8, M2 Clarity 7, M3 Segmentation 7, M4 Contradiction-Freedom 8, M5 Completeness 7; zero CRITICAL). Six findings were folded into **v0.3**:

| ID | Severity | Summary | Folded into |
| --- | --- | --- | --- |
| F-1 | MAJOR | Per-court scorer call signature under-specified (which args vary per court vs are shared, and that `covered_enemy_participants` stays the full set). | §11.2 "Per-court call signature (pinned)" + Slice 1 test `test_per_court_call_varies_leader_and_holdings_holds_covered_set` |
| F-2 | MAJOR | Slice 1 overloaded; leader→per-court fixture migration unbounded. | §11.4 "Migration bound" (grep enumeration, n=1 unaffected, Slice 1a/1b split escape hatch) |
| F-3 | MINOR | Internal contradiction: §11.4 + this note cited ratify at `:4776`; actual `ratify_settlement_confirm` is `:4583` (§15 was already correct). | corrected in §11.4 and §2 C1 above |
| F-4 | MINOR | Per-court no-generable-baseline edge case unspecified. | §8 OQ#5 `{"type":"peace"}` floor + Slice 1 test `test_settlement_baseline_court_with_no_demand_or_concession_uses_peace_floor` |
| F-5 | MINOR | `balance_projection` is net-new on the scorer **and** needs an internal call-site rewire; v0.2 said only "adds one param". | §15 two-step (add param + rewire internal call, fall back when `None`) + Slice 2 test `test_balance_projection_param_falls_back_to_internal_compute_when_not_injected` |
| F-6 | MINOR | Tier-1/2 Godot surface choice deferred to Slice 1 impl. | accepted as-is (payload is fixed; surface is an implementation detail) — no change |

Re-verified-accurate cites (sample): `calculate_common_peace_acceptance:1884` (single `accepting_leader:1891`, memoized `side_pressure_result:1895`/`direct_scores:1896`/`raw_total_harshness:1897`), `project_balance_after_settlement:1537` (no leader arg), `_build_clause_control_schema_for_review:2976` (hardcodes `enabled=True` at `:3001`), liberation `vassal_options or nation_options` at `:2959`, `_region_control_options:2816` (all-regions scan, REFRONT-7), cleanup-spec lines 543/570/575/586/589/594/597/601/609/618, Voice Bible §16.1 with no multi-court family. The three new named tests were confirmed absent from `tests/`.

---

## 9. Run #2 — independent re-audits of v0.3 (folded into v0.4)

v0.3 was audited twice, independently, under the same methodology. **A second-personality structured pass (Codex) returned NO-GO** with the stricter findings below; a parallel agent pass scored GO with four MINORs. All findings from both were evaluated against the live code — the two load-bearing Codex findings (F-1, F-4) were **verified true** before agreeing — and **all were folded into v0.4**.

**Codex pass (binding): NO-GO** — M1 6 / M2 6 / M3 6 / M4 4 / M5 6; 1 CRITICAL + 4 MAJOR + 1 MINOR.

| ID | Severity | Summary (verified) | Folded into v0.4 |
| --- | --- | --- | --- |
| C-F1 | **CRITICAL** | Per-court *direction* cannot come from the package side-pressure scalar. **Verified:** `compute_side_pressure_score:278` returns one side-level `score`; `compute_direct_scores_by_enemy:192` returns a per-enemy map. v0.3 OQ#5 wrongly said direction reads "that court's side-pressure." | §8 OQ#5 now derives direction from `per_court_direct_score = select_direct_score(direct_scores[court])` (`:243`); a pressure-model note states `base_side_pressure` stays package-level (no per-court scorer param). §4.2 clarified. Renamed test `test_settlement_baseline_per_court_direction_uses_per_court_direct_score_not_side_pressure`. |
| C-F2 | MAJOR | Slice 1 referenced a `balance_projection` scorer param that §15 only adds in Slice 2. **Verified:** the param does not exist on `calculate_common_peace_acceptance:1884-1901`. | §11.2/§15: `balance_projection` removed from the Slice-1 call contract (scorer recomputes internally in Slice 1; param + sharing is the Slice-2 scale step). |
| C-F3 | MAJOR | §15 had two ratification rows: one "EXTEND," one "REUSE unchanged." | §15: second row relabeled "Ratification **mutation** (post per-court gate) … REUSE; runs only after every court passes; gate decision is EXTEND above." |
| C-F4 | MAJOR | "Peace conference"/"conference voice" branding violates cleanup **SC-32 D5**. **Verified:** cleanup lines 69/1278 CUT conference/veto and mandate "no player-facing copy implies conference or veto." | §2 terminology boundary added ("conference" = internal shorthand only; no Congress/veto/round mechanic or player-facing copy). Voice slice renamed "multi-court settlement-table voice"; tests renamed; added `test_committed_multi_court_copy_avoids_conference_congress_veto_terms`. Fixed one mock button + one cross-ref. |
| C-F5 | MAJOR | Slice G deferral row was orphan-shaped ("owned by Slice G spec"). | §14 row now names the concrete owner (`SETTLEMENT_UI_CLEANUP_SPEC.md` SC-32 / Slice G2 ledger), completion, and a named absence test `test_propose_and_dial_routes_reject_non_player_caller_kind`. |
| C-F6 | MINOR | OQ#7 had no dedicated test. | Added `test_dial_changes_magnitude_without_silently_swapping_requested_identity` (Slice 2) + `test_tier1_default_identity_remains_replaceable_in_tier3` (Slice 3). |

**Agent pass (corroborating): GO** — 4 MINORs, also folded into v0.4: `acceptance_breakdown` relabeled to the `_execute_diplomatic_feasibility` result key (`diplomatic_executor.py:389-432`); `adjust_terms` cite `:243`→`:245`; Slice 2 split escape hatch added; Voice slice ordering pinned to land before/with Slice 1 (Slice 1 completion now depends on the resolver rule).

With these folded, v0.4 carries zero known CRITICAL/MAJOR. The spec remains a DESIGN GATE pending user approval of v0.4; a fresh audit run against v0.4 is advisable before implementation.

---

## 10. Run #3 — independent re-audit of v0.4 (folded into v0.5)

v0.4 was audited a fourth time. A structured **Codex pass returned NO-GO** (M1 8 / M2 6 / M3 7 / M4 5 / M5 6; **1 CRITICAL + 3 MAJOR**); a parallel agent pass returned GO (all metrics ≥7, zero CRITICAL) but surfaced 1 MAJOR + 2 MINOR clarity items. Every finding was **re-verified against the live code** before folding — `calculate_common_peace_acceptance:1884` (single `accepting_leader:1891`, memoized `side_pressure_result:1895`/`direct_scores:1896`/`raw_total_harshness:1897`, **no** `balance_projection` param), single-leader preview scoring `:2434-2444`, ratify `:4583`, `enabled=True` hardcode `:3001`, liberation fallback `:2959` all re-confirmed exact. All findings were folded into **v0.5**:

| ID | Severity | Summary (verified) | Folded into v0.5 |
| --- | --- | --- | --- |
| R3-C1 | **CRITICAL** | §5 reuse summary said "Draft persistence + ratification gate = unchanged," flatly contradicting §7/§11.4/§15 (the per-court gate is the one deliberate mechanics change; §15 even splits gate-EXTEND from mutation-REUSE). | §5 rewritten: "ratification **mutation** path reused unchanged; the **gate decision** is EXTENDED per §11.4 to require every covered court." |
| R3-M1 | MAJOR | §17 worked example still chose per-court direction from "side-pressure" — the exact wording the v0.4 CRITICAL fix removed from OQ#5. Side pressure is package-level; direction must read `direct_scores[court]`. | §17 reworded to `direct_scores[court]`; side pressure named only as the shared `base_side_pressure` acceptance component. |
| R3-M2 | MAJOR | §11.2 prose claimed the payload "reuses the scorer shape (`band`/`verdict`/`feedback`/`top_components`)," but the schema omits `feedback`/`top_components` (Tier-3 per OQ#4). | §11.2 prose reconciled: PROPOSE exposes `band`/`verdict`/`hard_stops` + one-line `top_blocker_display`; `feedback`/`top_components` stay Tier-3. |
| R3-M3 | MAJOR | STATUS.md still said "v0.2" / "USER APPROVAL of v0.2" / "conference-voice slice" / ratify `:4776`; this audit note title said "v0.2" though it contains the v0.3/v0.4 runs. | STATUS.md gained a May 29 v0.5 superseding paragraph (correct ratify `:4583`, "multi-court settlement-table voice"); this note retitled cumulative v0.2→v0.5; CLAUDE.md version tokens realigned. |
| R3-M4 | MAJOR | Baseline target (`near_acceptable`+, ≥35) sits below the §11.4 carry gate (accept, ≥50), so a concede-direction court can be a default holdout — §17's "this peace carries" over-promised the general case. | §8 OQ#5 gained the baseline-target-vs-carry-gate holdout note + Slice-1 test `test_baseline_concede_court_at_near_acceptable_is_flagged_holdout_not_auto_carry`. |
| R3-m1 | MINOR | §11.4 `carries` was undefined for hard-stopped courts (`total=null`). | §11.4 `carries` redefined: every court non-null `total` ≥ threshold AND no per-court `hard_stops`; Slice-1 test added. |
| R3-m2 | MINOR | §17 / Principle 7 "conference" prose could leak into committed copy despite the §2 SC-32 D5 ban. | §17 gained an internal-shorthand callout. |

With these folded, **v0.5** carried zero known CRITICAL/MAJOR and all five metrics re-audited ≥7 at the time of Run #3. (Run #4 below then found a residual CRITICAL in the OQ#5 direction model and folded it into v0.6.)

---

## 11. Run #4 — synthesis of independent v0.5 passes (folded into v0.6)

v0.5 was audited a fifth time as a **synthesis of two independent passes**, both re-verified against live code before folding:

- **Claude pass (binding): NO-GO** — M1 8 / M2 6 / M3 7 / M4 5 / M5 7; **1 CRITICAL + 1 MAJOR + 3 MINOR** (one MINOR withdrawn on verification).
- **Codex pass (corroborating): GO** — all metrics ≥7, zero CRITICAL; **2 MAJOR + 1 MINOR**.

The Claude CRITICAL is the load-bearing find — **Codex missed it** — and is exactly why synthesizing both passes mattered: the OQ#5 per-court direction model (untouched by Codex) still did not match the cited function's real signature.

| ID | Severity | Summary (verified against live code) | Folded into v0.6 |
| --- | --- | --- | --- |
| R4-C1 (Claude) | **CRITICAL** | §8 OQ#5 read `per_court_direct_score[court].score`, but `select_direct_score` (`settlement_scoring.py:243`) returns `Optional[Tuple[int, str]]` — a `(direct_score, source)` tuple with **no `.score` attribute** — and returns `None` for a court with no active cross-side pair. The spec also implied that case neutral-floors, but live code hard-stops it (`HARD_STOP_NO_DIRECT_WAR_SCORE`, `:353-356`). Verified: the live caller unpacks `direct_score, source = selection` after a `None` guard at `:352-358`. | §8 OQ#5 rewritten: unpack the tuple after a `None` guard; **dead-band → `{"type":"peace"}` floor**, **`None` → per-court hard-stop row** (matching the scorer + §11.4 `carries`). New Slice-1 tests `test_settlement_baseline_no_direct_score_court_is_hard_stopped_not_peace_floored`. |
| R4-M1 (Claude) | MAJOR | §8 OQ#5 thresholded the per-court **direct** score with `LOSING_SIDE_PRESSURE_THRESHOLD` (= `-20`, `settlement_preview.py:1326`), a constant live code uses **only** against `side_pressure_score` (`:1748/:1865/:2004`). This re-imports the exact direction-vs-side-pressure conflation the v0.4 CRITICAL removed. | §8 OQ#5 + pressure-model note: direction now uses a war-score-scale `DIRECT_SCORE_DIRECTION_MARGIN` dead-band, explicitly **not** the side-pressure constant; constant file cite corrected to `settlement_preview.py:1326`. New test `test_per_court_direction_threshold_is_war_score_margin_not_side_pressure_constant`. |
| R4-M2 (Codex) | MAJOR | §15 "Acceptance band display" row said the **scorer** provides `band`/`top_components`. Verified: the raw scorer returns `verdict`/`feedback` only; `_enrich_acceptance_display` (`settlement_preview.py:274`) derives `band`/`band_display`/`band_phrase`/`top_components`/`top_blocker_display`. | §15 row rewritten to that split; PROPOSE compact payload exposes only `band` + `top_blocker_display` (OQ#4). |
| R4-M3 (Codex) | MAJOR | Stale `v0.1`/`v0.2` text: STATUS Quick-Stats "Current Phase" still said v0.1 / "resolve §8 into a v0.2" / "Slices 1-3"; this audit-note title + top verdict still said v0.2 GO-ready. | STATUS Quick-Stats realigned to v0.6 (per-court gate, Slices 0-3 + multi-court voice); this note retitled v0.2→v0.6 with a latest-run top verdict; CLAUDE.md tokens realigned. |
| R4-m1 (Codex) | MINOR | §15 shared-score-pass list omitted `raw_total_harshness` though §11.2 + the §15 reuse row cite it as shared. | §15 scale-hook bullet adds `raw_total_harshness` (:1897); Slice-2 scale test renamed `..._direct_score_side_pressure_harshness_and_balance_projection_pass`. |
| R4-m2 (Claude) | MINOR | §14/§15 cited the resolver at "Voice Bible Intro:7"; no such anchor exists (resolver/fallback chain is at `:239-243`). | "Intro:7" dropped; "Cross-cast:239-243" retained. |
| R4-m3 (Claude) | MINOR | §15 "Intent dials" row read `modify_harsh`/`modify_generous` as functions; they are action-string branches (`diplomatic_executor.py:3101/:3534`). | Caveat "(action-string branches … not standalone functions)" added. |
| R4-w1 (Claude) | — WITHDRAWN | Claimed DWL-SET-SC5R-3 was cited at the wrong cleanup line (`:589`). | **Verified:** `SETTLEMENT_UI_CLEANUP_SPEC.md:589` *does* contain the `Discard new clause` / `Replace active clause` controls — the cite is correct; no change. |

**Re-verified-accurate cites this run:** `calculate_common_peace_acceptance:1884` (single `accepting_leader:1891`; memoized `side_pressure_result:1895` / `direct_scores:1896` / `raw_total_harshness:1897`; **no** `balance_projection` param), `select_direct_score:243` (`Optional[Tuple[int,str]]`, `None`→hard-stop at `:352-358`), `compute_direct_scores_by_enemy:192`, `compute_side_pressure_score:278`, `project_balance_after_settlement:1537` (no leader arg), `_build_clause_control_schema_for_review:2976` (`enabled=True` at `:3001`), liberation fallback `:2959`, `build_settlement_preview` single-leader scoring `:2431-2444`, `ratify_settlement_confirm:4583`, `_enrich_acceptance_display:274`, `SETTLEMENT_LIVE_CLAUSE_TYPES:131`, `adjust_terms` at `diplomatic_templates.py:245`; cleanup-spec `:543/:556/:570/:575/:586/:589/:594/:597/:601/:609/:613/:618/:69/:1278`; Voice Bible §16.1 present with **no** multi-court rule.

With these folded, **v0.6 carries zero known CRITICAL/MAJOR** and all five metrics re-audit ≥7. On a GO, the next step is **begin Slice 0 / Slice 1**. The spec remains a DESIGN GATE pending **user approval of v0.6**.

---

## 12. Run #5 — sixth audit pass of v0.6 (folded as v0.6 errata)

v0.6 was audited a sixth time (Run #5 by this note's scheme — see the header numbering key). Two independent passes were synthesized — a **Codex pass** (GO; 2 MAJOR + 1 MINOR) and a **Claude pass** (GO; verdict GO, all five metrics ≥7, 3 MINOR). Every cite was **re-verified against live code** before folding. The headline find is a Codex MAJOR the Claude pass missed: the spec's "9-component acceptance formula" is stale — live code sums **10** components.

**Verdict: GO** (both passes ≥7 on all metrics, zero CRITICAL). Findings folded **in place as a v0.6 errata** (doc-accuracy only; no design change, so no version bump and no CLAUDE.md/STATUS.md token churn):

| ID | Severity | Summary (verified against live code) | Folded |
| --- | --- | --- | --- |
| R5-M1 (Codex) | **MAJOR** | "**9-component acceptance formula**" is false: `calculate_common_peace_acceptance` sums **10** components — `concession_credit` was added by G2 after the original nine. **Verified:** `components` dict `settlement_scoring.py:2070-2081` lists 10 keys incl. `concession_credit`; docstring numbers it step 10 at `:1917`; `calculate_concession_credit:1273`; cleanup spec permits it (`settlement_scoring.py:404`). | §7 / §8 OQ#4 / §11.4 reworded to "live 10-component table incl. `concession_credit`"; this note §2 C1 reworded. Non-blocking (the re-front does not touch the formula), but a real spec-vs-code contradiction. |
| R5-M2 (Codex) | **MAJOR** | §11.4 sizing note "Slice 1's **ten** named tests" undercounts: §14 lists **16**, so the 1a/1b split trigger read a stale count. **Verified:** §14 Slice 1 enumerates 16 tests. | §11.4 → "16 named tests (§14)". The split escape hatch itself was already sound; only its trigger count was wrong. |
| R5-m1 (Codex) | MINOR | PROPOSE end-turn test name drift: §10 `..._while_review_does` vs §14 / §2 C2 `..._and_back_out_preserves_scoped_draft`. | §10 unified to the §14 canonical name (implementation owner + matches the C2 fold record); prose retains the REVIEW-asymmetry assertion. |
| R5-m2 (Claude) | MINOR | §3 C3 named the Slice-2 scale test without `harshness`; §11 R4-m1 + §14 include it. | §3 C3 annotated; canonical name is the `harshness`-inclusive one. |
| R5-m3 (Claude) | MINOR | Run-numbering scheme mismatch: this note's "Run #4 → v0.6" vs spec/CLAUDE.md "fifth audit". | Header numbering key added; this section labeled §12 = Run #5. |

**Re-verified-accurate this run:** the 10-component sum (`:2070-2081`), `select_direct_score:243` (`Optional[Tuple[int,str]]`, `None`→hard-stop unpacked at `:352-358`), `compute_direct_scores_by_enemy:192`, `calculate_common_peace_acceptance:1884` (single `accepting_leader:1891`; memoized `:1895/:1896/:1897`; **no** `balance_projection`), `project_balance_after_settlement:1537` (no leader arg), `build_settlement_preview` single-leader scoring `:2431-2444`, `ratify_settlement_confirm:4583`, `_enrich_acceptance_display:274`, `_build_clause_control_schema_for_review` `enabled=True` `:3001`, liberation fallback `:2959`; cleanup-spec `:575/:589/:594/:597/:601/:609/:613/:618/:69`; the line-618 test + new Slice-1 tests confirmed **absent** from `tests/`. With these folded, **v0.6 (errata) carries zero known CRITICAL/MAJOR**; next step on GO is **begin Slice 0 / Slice 1**.
