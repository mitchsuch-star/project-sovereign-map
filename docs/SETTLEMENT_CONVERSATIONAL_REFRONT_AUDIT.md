# Settlement Conversational Re-front — v0.2 Audit Note

**Audits:** `docs/SETTLEMENT_CONVERSATIONAL_REFRONT_SPEC.md` **v0.2**
**Date:** May 28, 2026
**Verdict:** **GO-with-changes → GO.** The audit found **4 material change items**; all four were **folded into v0.2** during this pass. With them folded, v0.2 is **GO-ready for user approval** (it remains a design gate — `NEEDS APPROVAL`; no code until approved).

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
**Finding.** The current settlement gate scores a **single `accepting_leader`** for the whole covered set (`build_settlement_preview` at `settlement_preview.py:2431-2444`; ratify `ratify_settlement_confirm:4583`); the 9-component formula's `burdened_participant_penalty` lowers the *leader's* willingness when allies are burdened. So today's design is "the coalition leader signs for the bloc with ally sympathy," and a multi-court settlement ratifies on the leader alone. The vision ("Prussia is the holdout," "never a blended number," §17 "with every covered court at/above threshold, Ratify") **requires** per-court gating. That is a **ratification-mechanics change**, not wiring, and it collided with the v0.1 §7 non-goal "not redesigning… ratification mechanics."
**Resolution (folded).** New **§11.4** locks the per-court gate (`carries` iff every covered court ≥ threshold; holdouts block but expose ease/drop; REVIEW carries `per_court_acceptance`). **§7** narrowed to "not redesigning the 9-component *formula*; the *gate* extension is in-scope and owned." Named test `test_ratify_requires_all_covered_courts_at_or_above_threshold_not_just_leader` added to Slice 1; the regression surface (existing leader-gated fixtures change verdict) is called out so a green-suite update is not mistaken for breakage. **User-approved** during authoring on UX + historical-analogue grounds (separate Napoleonic peaces; Britain fights on).

### C2 — PROPOSE hard-stop classification created an asymmetry. **[FOLDED]**
**Finding.** v0.1/early-v0.2 implied PROPOSE should block commands "like REVIEW." But the cleanup spec deliberately made settlement authoring **non-blocking** (`SETTLEMENT_UI_CLEANUP_SPEC.md:575`: "EDIT mode is not a hard stop… the player may end the turn from an editor draft"). Making PROPOSE a hard-stop while EDIT is not would turn `Adjust terms → EDIT` into an end-turn escape hatch and trap the player on the front surface.
**Resolution (folded).** **§10** classifies PROPOSE as an authoring surface — **not** a hard-stop, matching EDIT (end turn discards draft; Back Out preserves via `suspend_settlement_editor`). Only REVIEW/BLOCKED_TERMINAL remain hard-stops. Test `test_propose_does_not_block_end_turn_and_back_out_preserves_scoped_draft`.

### C3 — Per-court scoring didn't share the (package-level) balance projection. **[FOLDED]**
**Finding.** The scorer already accepts memoized `direct_scores` (:1896), `side_pressure_result` (:1895), and `raw_total_harshness` (:1897) — all package-level and shareable across the per-court loop. But `project_balance_after_settlement` (:1537) is also package-level (`(world, war_id, settlement_terms)`, independent of `accepting_leader`) yet has **no injection param**, so a naïve per-court loop would recompute it N times — an O(active_nations) snapshot per court per dial action. Acceptable today (small maps, user-initiated), but a scale smell for full Europe.
**Resolution (folded).** **§15** scale hook documents the three shared inputs and specifies **Slice 2 adds one memoization param** (`balance_projection=…`) mirroring the existing pattern, so the projection is computed once per dial action. Test renamed to `test_per_court_scoring_shares_one_direct_score_side_pressure_and_balance_projection_pass`.

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
