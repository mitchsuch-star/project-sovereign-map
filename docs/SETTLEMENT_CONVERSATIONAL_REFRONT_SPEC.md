# Settlement Conversational Re-front Spec

**Status:** **v0.6 — APPROVED May 29, 2026.** Design gate cleared; implementation unblocked. **Slice 0 + Slice 1 + REFRONT-V voice LANDED (May 30); Slice 2 IMPLEMENTED + suite-green + audit fold folded on master; Slice 3 IMPLEMENTED May 30 (V1–V3 cross-court validity + P2/P3 picker filtering + REFRONT-8 + DWL-SET-SC5R-3 + adjust-terms-focused; suite `10309 passed, 1 skipped`; ruff clean; Godot 4.4.1 parse exit 0). All implementation slices done — the remaining gate is the Gate 4 manual settlement smoke; then Slice G AI-ally agency.**
(Follows the same gate convention as `JEALOUSY_SPEC.md`.)

**Date:** May 28–29, 2026 (v0.1 vision → v0.2 detailed → v0.3 second-audit cleanup → v0.4 third-audit cleanup → v0.5 May 29 fourth-audit consistency fold → **v0.6 May 29 fifth-audit synthesis fold**)
**Owner / sequencing:** Next-up priority for the Peace Deals / Imperial Settlement arc.
**Builds on (reuse, do not rebuild):** `DIPLOMACY_SPEC.md` (bilateral proposal flow), `SETTLEMENT_UI_CLEANUP_SPEC.md` (clause model, acceptance scorer, scoped draft store, ratification gate), `DIPLOMAT_VOICE_BIBLE.md` (settlement voice families).
**Supersedes as the player-facing front door:** the raw SC-5R-2 settlement editor form, which becomes the opt-in deep tier (see §6). **It does not revert SC-5R-2 or the `suspend_settlement_editor` Back Out fix — both stay landed.**
**Audit:** audited four times before approval — see the sibling note `docs/SETTLEMENT_CONVERSATIONAL_REFRONT_AUDIT.md`. v0.2 folded the first pass (verdict **GO-with-changes**); v0.3 folded a second independent run; **v0.4** folds a third independent run (Codex, initial verdict **NO-GO** — 1 CRITICAL + 4 MAJOR + 1 MINOR — all agreed and resolved): per-court baseline **direction** now driven by per-court `direct_scores` not the package side-pressure scalar (§8 OQ#5, the CRITICAL); `balance_projection` removed from the Slice-1 call contract (Slice-2 optimization only — §11.2/§15); contradictory §15 ratification row relabeled gate-vs-mutation; the "conference" branding walked back to comply with cleanup **SC-32 D5** (no player-facing conference/veto copy — §2/§14); the Slice-G deferral row given a concrete SC-32/Slice-G2 owner + absence test (§14); and OQ#7 given dedicated tests. **v0.5** folds a fourth run (Codex **NO-GO** — 1 CRITICAL + 3 MAJOR — plus the parallel Run-#3 items): §5's stale "ratification gate = unchanged" corrected to gate-EXTEND / mutation-REUSE (the CRITICAL); §17's worked-example direction wording fixed from "side-pressure" to `direct_scores[court]`; §11.2 prose reconciled with its compact schema (`feedback`/`top_components` are Tier-3 only); §8 OQ#5 baseline-target-vs-carry-gate holdout note added; §11.4 `carries` defined for null/hard-stop totals; the §17 "conference" internal-shorthand callout; and STATUS + audit-note version references realigned to v0.5. **v0.6** folds a fifth run — a synthesis of two independent passes (a Claude pass returning **NO-GO** with **1 CRITICAL + 1 MAJOR**, and a Codex pass returning GO with **2 MAJOR + 1 MINOR**); every finding was re-verified against live code and folded: the §8 OQ#5 per-court direction model corrected to the real `select_direct_score` contract (returns `Optional[Tuple[int, str]]`, **not** a `.score` object; `None` → per-court **hard-stop**, not the neutral floor — the CRITICAL) and to a war-score-scale `DIRECT_SCORE_DIRECTION_MARGIN` dead-band instead of the side-pressure constant `LOSING_SIDE_PRESSURE_THRESHOLD` (the Claude MAJOR); §15's acceptance-band-display reuse row corrected so the raw scorer returns only `verdict`/`feedback` while `_enrich_acceptance_display:274` derives `band`/`top_components` (Codex MAJOR); `raw_total_harshness` added to the §15 shared-score-pass list and the Slice-2 scale test renamed (Codex MINOR); the stale `v0.1` STATUS Quick-Stats block + audit-note top verdict realigned to v0.6 (Codex MAJOR); and the non-existent "Voice Bible Intro:7" cite plus the "`modify_harsh` is a function" framing corrected (Claude MINORs). The Claude pass's third finding (DWL-SET-SC5R-3 cited at cleanup `:589`) was **withdrawn on verification** — line 589 of `SETTLEMENT_UI_CLEANUP_SPEC.md` does contain the `Discard new clause` / `Replace active clause` controls, so the cite was correct.

> v0.1 was a high-level **vision** spec. v0.2 resolves every §8 open question into a locked decision, adds per-tier control-state + payload shapes, multi-party validity rules, the picker valid-by-construction contract, a slice plan with named behavior tests, and a concrete reuse map citing real functions. **v0.3 (second-audit cleanup):** pins the exact per-court `calculate_common_peace_acceptance` call signature (which args vary per court vs are shared — §11.2), bounds the Slice-1 leader→per-court fixture migration with an explicit enumeration + split escape hatch (§11.4/§14), adds the per-court no-generable-baseline → `{"type":"peace"}` floor (§8 OQ#5), makes the Slice-2 `balance_projection` param explicit (§15), and corrects the ratify line cite. **v0.4 (third-audit cleanup):** fixes the per-court **direction** model (it reads each court's `direct_scores`, not the single package side-pressure scalar — §8 OQ#5), removes `balance_projection` from the Slice-1 call contract so no Slice-1 call references a not-yet-existing param (§11.2/§15), disambiguates the §15 ratification rows (gate = EXTEND, mutation = REUSE), enforces the cleanup **SC-32 D5** terminology boundary (no player-facing "conference"/"veto" copy — §2/§14 Voice), gives Slice G a concrete owner + absence test (§14), and adds OQ#7 magnitude/identity tests. The audit verdicts are in the sibling note. **v0.6 (fifth-audit synthesis)** corrects the §8 OQ#5 per-court direction model to the real `select_direct_score` return contract (tuple-or-`None`; `None` → per-court hard-stop) and a war-score-scale direction dead-band (not the side-pressure constant), the §15 band-display reuse row, the §15 shared-pass harshness list, and the stale STATUS / audit-note version text. **The user approved v0.6 on May 29, 2026** — implementation is unblocked; Slice 0 + Slice 1 + the REFRONT-V voice have landed (May 30, master `ec1081d`) and Slice 2 is the active next slice.
>
> **v0.6 errata (sixth-audit consistency fold, May 29 — no design change):** a sixth audit pass (synthesis of a Codex run + a Claude run) found two MAJOR doc-accuracy items plus three minors, all folded in place: (1) the stale "**9-component**" acceptance-formula references (§7/§8 OQ#4/§11.4) corrected to the **live 10-component table** — G2 added `concession_credit` after the original nine (`settlement_scoring.py:2070-2081`, docstring step 10 at `:1917`); (2) §11.4's Slice-1 sizing note "**ten named tests**" corrected to the actual **16** in §14 (the 1a/1b split trigger was reading a stale count); (3) §10's PROPOSE end-turn test name unified to its §14 canonical `test_propose_does_not_block_end_turn_and_back_out_preserves_scoped_draft`; (4) audit-note scale-test name + (5) audit-note run-numbering key corrected (sibling note §12); **(6)** the §14 Slice G / AI-ally-agency deferral row reconciled against `STATUS.md` — the SC-32 / Slice G2 decision ledger (D1–D7) has **landed** (mostly as cuts), so the row now points at the genuinely-remaining owners (cleanup-spec **Slice G1** offer producer, **Slice G2** follow-through, **Slice H** petitions) instead of the already-closed SC-32 / Slice G2. The formula itself is **unchanged** — the re-front still does not redesign acceptance math; only stale prose was fixed.

---

## 1. Why this exists — the divergence

The SC-5R-2 settlement editor set out to fix a narrow bug (empty/no-clause common peace) and chose a "structured editor, no raw JSON" approach. In doing so it reimplemented only the **deepest, rawest tier** of the existing diplomacy flow — granular clause assembly — and shipped it as the **front door and the only door**, stripped of the three things that make that tier usable in normal diplomacy:

- no Talleyrand-proposed baseline (you face a blank form),
- no intent dials (Harsher / More generous),
- no live acceptance while authoring,
- pickers that are not valid-by-construction (e.g. a `liberation` clause defaults to *France liberates France from France* and is only rejected at Submit).

The invalid-combo bug found during Gate 4 smoke is a **symptom**: a naked raw form with no baseline and no guidance lets the player assemble contradictions. The cure is to restore the conversational spine that bilateral diplomacy already has.

**The machinery to do this right already exists and was verified line-by-line for v0.2** (see §15). This is mostly wiring, not net-new systems. The few genuinely-new pieces are flagged honestly in §15.

> **Verified during v0.2 authoring:** the picker contract that would have prevented the liberation bug is *already written into `SETTLEMENT_UI_CLEANUP_SPEC.md` line 601* ("If a clause type's picker has zero valid options, its Add Clause control is disabled… liberation with no valid vassal") **and** that spec names a test for it on line 618 (`test_clause_add_disabled_when_picker_filter_empty_for_each_live_clause`). Neither the implementation nor the test ever landed: `_build_clause_control_schema_for_review` hardcodes `"enabled": True` (`settlement_preview.py:3001`), liberation's vassal picker falls back to *all nations* (`vassal_options or nation_options or []`, `settlement_preview.py:2959`), and no such test exists in `tests/`. So the interim band-aid (§16) is not new design — it is landing a contract the cleanup spec already promised.

---

## 2. The coherent vision (one sentence)

> **A common-peace settlement is authored through the same conversational, Talleyrand-mediated flow as a bilateral peace proposal — extended to cover more than one enemy court at once.**

A settlement is simply *"a peace proposal that can name several courts."* Same spine, same verbs, same live acceptance feedback, same valid-by-construction guarantee — only the scope is multi-party.

**Thematic identity — a multi-court settlement table.** A multi-party settlement seats France and several courts at one table, each with its own grievances, holdings, and price; bilateral peace is the degenerate one-court case. The experience should feel like negotiating several courts at once, not a form submission.

> **Terminology boundary (cleanup SC-32 D5 — normative).** `SETTLEMENT_UI_CLEANUP_SPEC.md` SC-32 D5 (lines 69 / 1278) **CUT** conference/veto mechanics and mandates that **no player-facing copy implies a conference or veto**. This re-front honors that boundary: the word **"conference" is internal design shorthand only** in this doc; the re-front adds **no** Congress/round/veto mechanic and **no** player-facing label, voice line, dispatch line, or UI text containing "conference," "congress," or "veto." Per-court ratification is independent per-court scoring, **not** a voting/veto procedure. Committed player-facing copy uses "settlement," "the table," "these courts," "<court> holds out / signs." If a Congress System is ever wanted, it ships as its own spec per D5. (Voice tests enforce this — §14 Voice.)

### Principles
1. **Talleyrand is the spine, not a bolt-on.** Every tier is mediated by his voice and a recommendation.
2. **Never a blank form.** You always start from a sensible, valid, context-aware draft.
3. **Steer by intent, see the cost live.** You push (harsher) or yield (more generous) and watch acceptance move in real time — per court and overall.
4. **You can never author the illegal.** You can push on what is *allowed*; when something isn't, you're told why rather than discovering it at Submit.
5. **Multi-party is first-class.** Coverage, per-court acceptance, and cross-court trade-offs are part of the conversation, not an afterthought.
6. **The player requests; the advisor suggests — never random.** Specific terms (which region is ceded, how much gold, which clause) are **requested by the player** with full agency, exactly as in a bilateral peace. Talleyrand **suggests** logically from each court's desires and holdings and the military picture (`NATION_DESIRE_PROFILES` + war state) and explains *why* — but the system never randomly assigns or silently auto-fills a term. A suggestion is a starting point you can accept, change, or replace, not an imposition. (Territory and gold are requestable terms, not system-rolled outcomes.)
7. **Every conference feels novel — not a carbon copy per war score.** Novelty comes from **situational specificity** (which courts are at the table, what each covets and holds, relationships, betrayal memory, coalition posture) and from **conversational texture** (Talleyrand's per-conference read; per-court voice via the Voice Bible families), **not** from randomness and **not** from a rote `war_score → fixed template → identical screen` mapping. Mechanics stay deterministic per Golden Rule #6 — acceptance scoring and term effects are reproducible for a given full situation; "novel" is a property of input-richness and presentation, never of randomized outcomes. (See §8 OQ#6 for the locked enumeration of inputs and the explicit rejection of RNG/LLM-decided variation.)

---

## 3. The three-tier flow (mirror of bilateral diplomacy)

| Tier | Bilateral diplomacy today (**implemented**, see §15 for code cites) | Settlement re-front (this spec) |
| --- | --- | --- |
| **1 — Propose** | Talleyrand drafts smart terms (`generate_suggested_terms`, 5-stage, nation-aware, economically capped) | Talleyrand drafts a baseline settlement for the whole covered set — valid for every court by construction |
| **2 — Steer by intent** | `Send as suggested` / `Harsher terms` / `More generous`, each re-scoring acceptance live | Same verbs over the settlement package — applied to the **whole table by default or to a single focused court** ("press Prussia," "ease Britain") — with **per-court + overall acceptance** updating live. Talleyrand may also lead with a targeted posture recommendation; his targeting is advice/voice only |
| **3 — Push on specifics** | `Adjust terms` — guided step-by-step builder | The existing structured clause editor, now the **opt-in deep layer**, with **valid-by-construction** pickers |

The default landing is the **PROPOSE** surface (Tiers 1→2). The existing EDIT editor (Tier 3) is reached on demand via **`Adjust terms`**, exactly as the bilateral `adjust_terms` option sits beside `Harsher`/`More generous` (`diplomatic_templates.py:245`). Tier 3 inherits the same validity guarantee, so the liberation-style nonsense can't be built there either.

> **Coherence note (important, from the v0.2 audit):** the bilateral three-tier *steering* flow is a property of the **implementation** (`diplomatic_templates.py:226-296`, `diplomatic_executor.py` `modify_harsh`:3101 / `modify_generous`), **not** of `DIPLOMACY_SPEC.md`, which documents only the older two-turn propose→counter-offer flow. This spec mirrors the implemented terms-guidance flow and cites the code as its source of truth. The two are not in conflict — `DIPLOMACY_SPEC.md` simply predates the terms-guidance UI.

### 3a. State machine

```
War Detail "Open Settlement"
        │  (propose_common_peace; existing route)
        ▼
   ┌─────────────────────┐  Harsher / More generous (whole-table or focused court)
   │  PROPOSE  (Tier 1/2) │◄───────── re-draft + re-score, stay in PROPOSE
   │  baseline + per-court │  Coverage: add / drop court ──► re-draw baseline + re-score
   │  acceptance + dials   │
   └─────────┬─────────────┘
   Adjust    │  Submit for Review
   terms     │
   ▼         ▼
┌──────┐  ┌─────────────────────┐  Ratify (fresh rescore gate; existing)
│ EDIT │  │  REVIEW (existing)   │────────────────────────────► applies per-pair peace
│Tier 3│─►│  blocked if any court│
│      │  │  below threshold     │
└──────┘  └─────────────────────┘
  ▲  Submit for Review
  └── Back Out preserves the scoped draft (suspend_settlement_editor; unchanged)
```

Today the flow jumps straight from `propose_common_peace` to the blank EDIT editor (`open_editor_on_mount=true`). The re-front inserts **PROPOSE** as the default landing; EDIT becomes the `Adjust terms` branch. REVIEW and Ratify are unchanged.

---

## 4. The multi-party dimension (what is genuinely new vs. bilateral)

This is the heart of "works like other peace but allows multi-party":

1. **One settlement, a set of covered courts.** A settlement names `covered_enemy_participants` within a single war. Courts not covered stay at war.
2. **Per-court acceptance, never a blended number.** Each covered court has its own losses, war objectives, and burden, so each has its own acceptance — and its own baseline **direction** (demand vs concede), driven by **that court's direct war score** (`direct_scores[court]`), not by the single package-level side-pressure scalar (§8 OQ#5). The side-level `base_side_pressure` *component* of the acceptance formula is shared across courts (it is a side quantity by construction); per-court acceptance differentiation comes from the court-specific components `leader_own_losses`, that court's `war_objective_alignment`, and its `burdened_participant_penalty` (§11.2). The conversation surfaces *per-court* readings ("Britain will sign; Prussia will not unless you concede X"), plus an overall "does this settlement carry" summary. (Payload shape: §11.2.)
3. **Coverage is part of the conversation.** Adding or dropping a court re-draws the baseline, each court's terms, and who remains at war — and Talleyrand reasons about whether widening the net is wise. (Both the checklist and a conversational prompt write the same state — §8 OQ#2.)
4. **Cross-court validity.** Valid-by-construction spans the whole set: the same region can't be promised to two courts, a non-covered court can't be bound, and a clause's `from`/`to` must be real participants on the right side. (Rules: §12.)
5. **Talleyrand reasons across the table,** not clause-by-clause in isolation — he weighs the package against each court and flags the binding constraint. (Multi-court table voice: §14 Voice.)

Bilateral peace is then just the n=1 case of this same model.

---

## 5. Reuse summary (detail in §15)

This is mostly wiring. Tier-1 baseline = generalize the concession generator + borrow the bilateral demand-term selector. Live acceptance = the existing per-settlement scorer, called once per covered court over one shared score pass. Intent dials = the `modify_harsh`/`modify_generous` redraft-and-rescore pattern. Voice = the Voice Bible settlement families + the named-diplomat resolver. Deep editor = the SC-5R-2 editor with valid-by-construction pickers. Draft persistence and the ratification **mutation** path are reused unchanged; the ratification **gate decision** is **extended** per §11.4 to require every covered court (a deliberate mechanics change, not wiring — see §7 / §15). **Concrete function-level reuse map with file:line cites and a "new vs extend" column is §15.**

---

## 6. What changes / what stays

- **Front door changes:** blank raw form → Talleyrand-proposed baseline + intent dials + live per-court acceptance (the new **PROPOSE** surface).
- **The structured picker editor stays** — but becomes **Tier 3** (`Adjust terms`), reached on demand, with **valid-by-construction pickers** (this absorbs the liberation/invalid-combo class of bug and the deferred `DWL-SET-SC5R-3` inline-merge-conflict follow-up).
- **Backend clause/validation/ratification contracts stay.** We feed them from the conversational front instead of a naked form; the validator remains the source of truth, and pickers mirror it (`SETTLEMENT_UI_CLEANUP_SPEC.md:609`).
- **SC-5R-2 and `suspend_settlement_editor` are NOT reverted.** The editor scene/script, scoped-draft round-trip, active-vs-archived routing, and the non-destructive Back Out all stay landed; this spec re-fronts them.
- **Incoming AI offers** (the SC-5 / SC-30 path) read naturally as the inbound side of the same model and should converge on the same per-court presentation. (Out of scope to build here — see §7.)

---

## 7. Non-goals (this pass)

- Not redesigning the clause set or the **live common-peace acceptance component table** (the 10-component sum in `calculate_common_peace_acceptance:2070-2081` — including `concession_credit`, which G2 added after the original nine; its per-court math is unchanged). **In scope and deliberate:** extending the ratification *gate* from single-leader to per-covered-court (§11.4) — this is the one mechanics change the vision requires and is owned by a named requirement + test, not smuggled in as "wiring."
- Not building AI-side settlement agency — **Slice G stays a separate, later item** (blocked behind Gate 4 smoke per `STATUS.md`).
- Not building the inbound (incoming-offer) presentation convergence; this spec defines the **outbound** (player-authored) conference. Convergence is recorded as an owned follow-up (§14, row REFRONT-5) so it is not an orphan.
- Not removing Tier 3; the goal is to *front* it with guidance, not delete the power-user surface.

---

## 8. Resolved decisions (was "Open questions for approval")

Each former open question is now a locked decision with rationale. (v0.1 numbering retained.)

### OQ#1 — Dial scope → **LOCKED: BOTH (whole-table default + focused court), Tier-2 stays court-level, targeting is voice-only.**

- `Harsher terms` / `More generous` operate on the **whole settlement package by default** (re-draft + re-score every covered court).
- When a court is **focused** (the player selects a per-court row), the dial applies to **that court only** — "press Prussia," "ease Britain" — leaving the other courts' terms untouched.
- Talleyrand **may lead with a targeted posture recommendation** ("I'd press Prussia and ease Britain, Sire"). This is **advice/voice only**: it never silently retargets or applies the dial, and it is never LLM-decided mechanics. The player must click to apply. (`test_targeted_posture_is_voice_only_not_applied`.)
- **Tier 2 granularity is court-level.** Clause-level precision (which region, how much gold) is **Tier 3** only.
- Canonical labels mirror bilateral exactly: **`Harsher terms`** and **`More generous`** (a.k.a. "kinder"). Per-court phrasing in voice copy may read "press/ease <court>."
- **Rationale:** preserves the bilateral mental model (one dial on the active proposal) while making the multi-party case first-class; honors Golden Rule #6 (player requests, advisor suggests, deterministic application); avoids a combinatorial per-clause dial in Tier 2.

### OQ#2 — Coverage editing → **LOCKED: BOTH, unified on one backend state.**

- Coverage is editable two ways that both write the **same** `covered_enemy_participants` and trigger the **same** baseline re-draw + per-court re-score:
  1. the existing covered-enemies **checklist** (already in the editor — `settlement_editor_popup.gd` `_render_covered_enemies`), and
  2. a **conversational prompt** in PROPOSE — Talleyrand surfaces uncovered hostile courts as one-click "Also bring Prussia to the table?" / "Drop Britain from the settlement" suggestions that toggle the same checklist state (player-facing copy avoids "conference" per the §2 SC-32 D5 boundary).
- Both paths update `ignored_participants[]` / `remaining_wars[]` / the scope badge on the next preview (the cleanup spec already requires the checklist to do this — `SETTLEMENT_UI_CLEANUP_SPEC.md:594`). At least one covered enemy must remain (`:586`).
- **Rationale:** the checklist already exists and is the source of truth; the conversational prompt is a discoverability/voice layer over the *same* state, not a second store — no drift, no new persistence.

### OQ#3 — Tier-3 exposure → **LOCKED: always one click away (`Adjust terms`), never the default.**

- Tier 3 is reached via an **`Adjust terms`** affordance present in PROPOSE, mirroring the bilateral `adjust_terms` option (`diplomatic_templates.py:245`). It is one click away and always available, but the default landing is the conversational PROPOSE surface.
- `Adjust terms` may be invoked **focused on a specific court** (opens EDIT seeded to that court's slice) or unfocused (whole package).
- **Rationale:** mirrors bilateral exactly; "front it with guidance, don't delete it" (§7). Gating behind an "advanced" menu would diverge from bilateral and hide a surface that already shipped.

### OQ#4 — Per-court acceptance display detail → **LOCKED: progressive disclosure by tier.**

- **Tier 1/2 (per-court row):** acceptance **band** + `band_display` + a **one-line top blocker** when below threshold ("Prussia: refuses — territory demand too harsh"), plus the live **delta** on dial actions (previous band → current band). An **overall** summary line ("this peace carries" / "Prussia is the holdout"). This mirrors what bilateral shows (categorical outcome + largest-component feedback — `DIPLOMACY_SPEC.md` A2; the `acceptance_breakdown` result key built in `_execute_diplomatic_feasibility`, `diplomatic_executor.py:389-432`) and the cleanup spec's acceptance-trend contract (`:597`).
- **Tier 3 (focused court):** full **component breakdown** (the scorer's `feedback` / `top_components`, the full component table — 10 components incl. `concession_credit`) for the focused court — the editor's existing preview panel.
- **Rationale:** band + top blocker is enough to steer; the full component table is detail you only need when hand-shaping a clause. Reuses the scorer's existing output — no new math, all `int()` (Golden Rule #2).

### OQ#5 — Losing-side concession baseline generalized to multi-party → **LOCKED: per-court direction, both sides.**

- The Tier-1 baseline generalizes `_compute_concession_baseline` (`settlement_preview.py:1967`) into a per-court baseline (`compute_settlement_baseline`, §15) that:
  - loops over each covered court and produces that court's slice;
  - chooses **direction per court** from **that court's direct war score** — *not* the single package-level side-pressure scalar (which cannot express per-court direction; see the model note below). Compute `sel_court = select_direct_score(direct_scores[court])` (`settlement_scoring.py:243`). **Mind the real return contract (Run-#4 CRITICAL fix):** `select_direct_score` returns `Optional[Tuple[int, str]]` — a `(direct_score, source)` **tuple**, *not* an object with a `.score` attribute — and it returns `None` when the court has no active cross-side pair. Unpack as `direct_score, _ = sel_court` **after** a `None` guard, exactly as the live caller does at `settlement_scoring.py:352-358`. The input `direct_scores[court]` is that enemy's `{member: war_score}` map from `compute_direct_scores_by_enemy:192`. Direction is taken from the **sign of `direct_score` on the war-score scale**: **demand** where France leads the court (`direct_score > +DIRECT_SCORE_DIRECTION_MARGIN` — mirrors `generate_suggested_terms` demand-stage selection of border/coveted regions + calibrated gold) and **concede** where France is pressured by it (`direct_score < -DIRECT_SCORE_DIRECTION_MARGIN`, the existing peace→gold→territory escalation). `DIRECT_SCORE_DIRECTION_MARGIN` is a small war-score-scale dead-band set in Slice 1; it is **NOT** `LOSING_SIDE_PRESSURE_THRESHOLD` (`settlement_preview.py:1326`, value `-20`), which is calibrated for the *power-weighted side-pressure* scalar and must not be reused to threshold a raw per-court direct score (model note below);
  - so a mixed conference (winning vs Prussia, losing vs Britain) emits demands from Prussia *and* concessions to Britain in **one** baseline — exactly the §17 worked example;
  - **a court inside the dead-band — France neither clearly leads it nor is clearly pressured by it (`-DIRECT_SCORE_DIRECTION_MARGIN <= direct_score <= +DIRECT_SCORE_DIRECTION_MARGIN`) — falls back to the `{"type":"peace"}` neutral floor** (the cleanup-spec line-613 neutral start), so it still receives a valid slice;
  - **a court with no direct war score at all (`select_direct_score` returns `None` — no active cross-side pair) is NOT neutral-floored (Run-#4 CRITICAL fix):** it is surfaced as a per-court **hard-stop row**, matching the scorer's `HARD_STOP_NO_DIRECT_WAR_SCORE` branch (`settlement_scoring.py:353-356`) and the §11.4 rule that a hard-stopped court (`total=null`) blocks `carries`. This keeps the baseline consistent with the live scorer instead of inventing a peace the scorer would reject. (Distinguish the two cases: dead-band → neutral peace floor; `None` → hard-stop. They are not the same.)
  - targets each court at `near_acceptable`+ by default (the existing escalation already targets `near_acceptance_floor`) and **never** escalates past what the player would request — suggestions, not impositions. **Baseline target vs the §11.4 carry gate (resolves a Run-#3 finding):** a *demand-direction* court (France leads it) lands at/above the accept threshold by construction; a *concede-direction* court whose affordable concessions only reach `near_acceptable` (35–49) is seated as a **holdout** under the ≥50 carry gate — this is expected, not a defect. The default baseline guarantees a *valid, near-acceptable* start, **not** that every court auto-signs; the player eases such a holdout (focused `More generous`) or drops it (§11.4). So §17's per-court "will sign" readings hold for that example's specific courts, but the default baseline is **not** a blanket guarantee of `overall_acceptance.carries=true`. (`test_baseline_concede_court_at_near_acceptable_is_flagged_holdout_not_auto_carry`, Slice 1.)
- **Pressure model note (resolves the v0.4 CRITICAL).** Two distinct quantities, do not conflate them: (a) **`side_pressure_result["score"]`** (`compute_side_pressure_score:278`) is a **single power-weighted side-level scalar** for the whole covered set — it feeds the acceptance formula's `base_side_pressure` component and **stays package-level / shared across the per-court loop** (it does **not** gain a per-court scorer param); it **cannot** drive per-court direction. (b) the per-court **`direct_score`** (above, the `int` half of `select_direct_score(direct_scores[court])`) **is** per court and is what selects each court's demand/concede direction. So a mixed war demands from a led court and concedes to a pressuring court even though `base_side_pressure` is identical for both. **The direction *threshold* is likewise distinct (Run-#4 MAJOR fix):** direction uses a war-score-scale dead-band `DIRECT_SCORE_DIRECTION_MARGIN`, **not** `LOSING_SIDE_PRESSURE_THRESHOLD` (the side-pressure boundary, `settlement_preview.py:1326`). Reusing the side-pressure constant to threshold a raw direct score would re-introduce the very scale conflation this note exists to prevent. Tests: `test_settlement_baseline_per_court_direction_uses_per_court_direct_score_not_side_pressure` and `test_per_court_direction_threshold_is_war_score_margin_not_side_pressure_constant` (both Slice 1).
- **Rationale:** the worked example requires per-court direction; a losing-side-only baseline cannot express it. Generalizing reuses the escalation loop + scorer; the demand side reuses the proven bilateral selectors; per-court direction reuses the existing `select_direct_score` / `direct_scores` machinery, so no new pressure math is introduced.

### OQ#6 — Novelty sourcing → **LOCKED: deterministic input set only; bounded presentation-variation REJECTED for v0.2 (recorded as a default-CUT owned item).**

- Per-conference texture is sourced **entirely** from deterministic situational inputs already in world state: per-court desires (`NATION_DESIRE_PROFILES`), holdings (`get_nation_regions`), side-pressure / direct-scores, war objectives (WPS), relationships, betrayal memory, coalition posture/threat, leader losses, power tier.
- Talleyrand's per-conference read is **composed** from those inputs via the Voice Bible families. **Selection of which families/lines fire is deterministic** from the inputs (exactly as bilateral works). LLM may surface the prose (flavor) but never decides which mechanical situation obtains — Golden Rule #6, reinforced by `DIPLOMACY_SPEC.md` design-philosophy ("LLM explains, never decides").
- The optional "bounded, presentation-only variation for repeat conferences" is **NOT adopted in v0.2.** It is **not an orphan deferral**: it is recorded as an explicitly-owned, **default-CUT** item (§14, row REFRONT-6) with a completion definition and a guard test (`test_presentation_variation_never_changes_scored_result`) that any future implementation must satisfy. Reason it is cut: the deterministic input space is already large enough that exact repeats are rare, so the variation buys little and risks smuggling RNG into a deterministic engine.
- **Rationale:** keeps the gate clean and the engine deterministic; satisfies the "feels novel" claim through input richness + voice at zero mechanical cost.

### OQ#7 — Territory/gold request affordance → **LOCKED: identity in Tier 3, magnitude in Tier 2, advisor pre-fills the default.**

- Specific region / gold-amount **requests** are authored in **Tier 3** (the structured editor — region picker, numeric input), exactly as bilateral `Adjust terms` builds the offer step by step.
- The **Tier-1 baseline pre-fills the logical default** (suggested region from `NATION_DESIRE_PROFILES` / border logic; conservative payable gold) that the player can accept, change, or replace.
- **Tier-2 dials adjust magnitude at the court level** (harsher = larger/more demands; generous = fewer/smaller); the **specific identity** of the region/amount is a Tier-3 request.
- **Rationale:** matches bilateral exactly (magnitude in Tier 2, identity in Tier 3); preserves "player requests, advisor suggests" (principle 6 / Golden Rule #6).

---

## 9. Gate & sequencing

- **Status:** **v0.6 APPROVED May 29, 2026** (finished and audited five runs before approval; sibling note). The design gate is cleared — implementation is unblocked. **Slice 0 + Slice 1 + REFRONT-V voice have LANDED (May 30, master `ec1081d`); Slice 2 is the active next slice.**
- **This is the next-up priority** for the settlement arc (ahead of Slice G, which remains blocked and separate).
- **Now approved →** implement the remaining slices in §14 in order (Slice 0 LANDED; Slice 1 next). Gate 4 manual smoke re-runs against the re-fronted flow once Slices 1–2 land.
- **Interim de-risk (independent — §16): LANDED as Slice 0** (master `4ffdfcc` + `3c7a55e`). The picker-filtering band-aid shipped the cleanup-spec line-601 **backend** contract + its named test; its Godot consumer (REFRONT-8) folds into Slice 3, so Slice 0 alone does not fully unblock the Gate 4 pass — the re-front is the cure.

---

## 10. Surfaces & dialogue modes

The settlement dialogue family gains one new mode. All three modes live on the existing `settlement_confirm` dialogue contract (the cleanup spec already defines EDIT / REVIEW / BLOCKED_TERMINAL); PROPOSE is added in front.

| `dialogue_mode` | Surface | Tier | Blocking? | Reached from |
| --- | --- | --- | --- | --- |
| **`PROPOSE`** *(new)* | Conversational front: baseline + per-court acceptance + dials + coverage | 1–2 | **not a hard-stop** (authoring surface, like EDIT) | `propose_common_peace` (default landing) |
| `EDIT` *(existing)* | `settlement_editor_popup.gd` structured editor | 3 | not a hard-stop (end turn discards draft) | PROPOSE `Adjust terms`; revise routes |
| `REVIEW` *(existing)* | `proposal_confirm_popup.gd` `_build_settlement_content` | — | hard-stop | PROPOSE / EDIT `Submit for Review` |
| `BLOCKED_TERMINAL` *(existing)* | blocked-ratification banner + recovery | — | hard-stop | stale / unrecoverable |

**Why PROPOSE is *not* a hard-stop:** it is an **authoring** surface (Tiers 1–2), the same role EDIT plays, and the cleanup spec deliberately made settlement authoring non-blocking (`SETTLEMENT_UI_CLEANUP_SPEC.md:575` — "EDIT mode is not a hard stop… the player may end the turn from an editor draft"). Classifying PROPOSE like EDIT keeps the player from being trapped and avoids the asymmetry where `Adjust terms → EDIT` would become an end-turn escape hatch. End turn from PROPOSE discards the unsubmitted draft via the SC-2 discard-notice contract (identical to EDIT). **Back Out** from PROPOSE uses the non-destructive `suspend_settlement_editor` semantics already shipped (preserves the scoped draft for same-turn reopen). Only `REVIEW` / `BLOCKED_TERMINAL` (staged-decision surfaces) remain hard-stops. PROPOSE / EDIT / REVIEW remain one continuous authoring session over one scoped draft. *(Test: `test_propose_does_not_block_end_turn_and_back_out_preserves_scoped_draft` — the Slice 1 canonical name, §14; it asserts PROPOSE does not block end turn while REVIEW does, and Back Out preserves the scoped draft.)*

**Godot rendering.** PROPOSE renders per-court rows (court name, band, top blocker, direction summary) + the dial action rail. It either extends `proposal_confirm_popup.gd::_build_settlement_content` with a PROPOSE branch or adds a sibling `settlement_propose_popup` on a layer below the editor (112). The editor (Tier 3) stays exactly where it is. (Surface choice is an implementation detail for Slice 1; the **payload** is fixed below so backend work is unblocked either way.)

---

## 11. Per-tier control-state and payloads

### 11.1 PROPOSE control-state matrix

| Mode | Visible controls | Disabled / absent rules |
| --- | --- | --- |
| `PROPOSE` | Per-court acceptance rows (focusable); `Harsher terms`; `More generous`; per-court focus toggle; `Coverage` add/drop prompts; `Adjust terms` (→ EDIT, optionally focused); `Submit for Review`; Back Out | `Submit for Review` is disabled while a re-score is in flight, while `covered_enemy_participants` is empty, or while the baseline failed to generate. `Harsher`/`More generous` are disabled while a re-score is in flight. Below-threshold courts do **not** disable `Submit` — Submit into a blocked REVIEW is allowed (cleanup spec `:597`), but the click first renders the same inline below-threshold warning the editor uses. A focused dial is disabled for a court already at the band floor/ceiling (e.g. `More generous` on a court already at `accept` shows "already certain to sign"). Talleyrand's targeted-posture line is advisory text, never an auto-applied control. |

PROPOSE is an authoring surface — **not** a hard-stop (§10) — and shares EDIT's end-turn-discards-draft + Back Out-preserves-draft semantics (SC-2). Below-threshold **holdout** courts surface `Ease <court>` / `Drop <court>` (§11.4) so a holdout is never a dead-end. EDIT ↔ REVIEW ↔ PROPOSE cycles from normal revision are **not** SC-14b stale-reopen attempts and have no loop cap.

### 11.2 Per-court acceptance payload (`per_court_acceptance`)

Returned by PROPOSE preview and by every dial/coverage re-score. One entry per covered court, each produced by one `calculate_common_peace_acceptance` call (see §15 for the shared-score-pass scale design).

```
per_court_acceptance: List[{
  "nation": str,                      # covered court
  "band": str,                        # "accept" | "near_acceptable" | "reject"
  "band_display": str,                # humanized, Voice-Bible-consistent
  "total": int | null,               # int() per Golden Rule #2; null on hard-stop
  "threshold": int,                   # accept threshold (currently 50)
  "verdict": str,                     # mirrors scorer verdict
  "top_blocker_display": str | null, # one-line worst negative component when below threshold
  "direction_summary": str,           # "Demanded: Silesia + 200g" / "Conceded: white peace"
  "previous_band": str | null,       # for live delta; null on first paint
  "delta_display": str | null,       # "Prussia 78% → 44% (now refuses)" style; presentation only
  "hard_stops": List[Dict]            # per-court hard stops bubbled from the scorer
}]
overall_acceptance: {
  "carries": bool,                    # true iff every covered court is at/above threshold
  "holdout_courts": List[str],
  "summary_display": str              # "This peace carries" / "Prussia is the holdout"
}
```

`per_court_acceptance` is **derived from** the scorer's canonical preview shape: PROPOSE exposes `band` / `verdict` / `hard_stops` plus a one-line `top_blocker_display` (the scorer's top negative component — no new math); the full `feedback` / `top_components` table stays **Tier-3 detail** (OQ#4) and is **not** part of this compact payload. All numeric fields are `int()`. `delta_display` is **presentation-only** and never feeds the scored result (Golden Rule #6 / OQ#6).

**Per-court call signature (pinned).** Each `per_court_acceptance` entry is exactly one `calculate_common_peace_acceptance` call (`settlement_scoring.py:1884`, verified single-`accepting_leader` signature at `:1891`). To make the aggregator unambiguous:

- **Varies per court (one value per call):** `accepting_leader=<that court>`, and that court's `accepting_leader_regions_at_evaluation` / `accepting_leader_mapped_holdings_at_entry` (the scorer's per-leader holdings params, `:1898-1899`).
- **Held constant across the whole per-court loop:** `covered_enemy_participants=<the full covered set>` — **not** a singleton `{court}` — so every court's `burdened_participant_penalty` and `abandoned_by_ally_acceptance_mod` still reflect the entire table (this is what makes Talleyrand "reason across the table," principle 5 / §4.5, rather than scoring each court in isolation); plus `proposer_side` / `accepting_side` and the shared package-level inputs `direct_scores` / `side_pressure_result` / `raw_total_harshness`. Because `side_pressure_result` is shared, the acceptance **`base_side_pressure` component is package-level (the same side-level value for every court)** — it does **not** become a per-court scorer param; per-court acceptance differs only via the court-specific components below. (Per-court *baseline direction* uses `per_court_direct_score` from the same `direct_scores` map — §8 OQ#5 — which is a baseline-direction signal, not an acceptance param.)
- **`balance_projection` is NOT part of the Slice-1 call contract.** The live scorer has no `balance_projection` param (`calculate_common_peace_acceptance:1884-1901`); it computes the projection internally. **Slice 1's per-court calls pass nothing for it** and let the scorer recompute internally per call (correct, just O(N) projections per dial action). **Slice 2** adds the memoization param and shares one projection per dial action (§15) — the scale optimization, not a Slice-1 dependency. This removes any Slice-1 reference to a not-yet-existing param.
- **Therefore only the court-specific components differ between calls:** `leader_own_losses`, that court's `war_objective_alignment`, and its `burdened_participant_penalty`. Everything else is shared work computed once per dial/coverage action (the balance projection joins that shared set in Slice 2).

Test: `test_per_court_call_varies_leader_and_holdings_holds_covered_set` (Slice 1).

### 11.3 PROPOSE request/response and dial/coverage actions

PROPOSE reuses the settlement preview request shape (`SETTLEMENT_UI_CLEANUP_SPEC.md:543`) with `dialogue_mode="PROPOSE"`. New action verbs (all deterministic redraft-and-rescore, mirroring `modify_harsh`):

- `settlement_dial_harsher` — `{war_id, draft_key, scope: "table" | court_nation}`. Re-drafts the package harsher (whole table or one court) and returns `per_court_acceptance` + `overall_acceptance` + the new `settlement_terms`.
- `settlement_dial_generous` — same shape, opposite direction.
- `settlement_cover_add` / `settlement_cover_drop` — `{war_id, draft_key, nation}`. Mutates `covered_enemy_participants`, re-draws the baseline for the new set, re-scores, and updates `ignored_participants[]` / `remaining_wars[]`.
- `settlement_focus_court` — `{war_id, draft_key, nation | null}`. Presentation-only focus; does not mutate terms.
- `adjust_terms` (→ EDIT) and `propose_common_peace` (→ Submit for Review) reuse existing routes; `adjust_terms` carries optional `focused_court`.

Each dial/coverage response carries the same `per_court_acceptance` / `overall_acceptance` block so Godot re-renders identically regardless of which action fired.

### 11.4 Ratification gate — per-covered-court (the one deliberate mechanics change)

> **What changes from today.** The current settlement gate scores a **single `accepting_leader`** for the whole covered set (`build_settlement_preview` scores one leader at `settlement_preview.py:2431-2444`; ratify at `ratify_settlement_confirm:4583`); the acceptance formula (10 components, incl. `concession_credit`) lowers the *leader's* willingness when allies are burdened (`burdened_participant_penalty`), i.e. today's model is "the coalition leader signs for the bloc with ally sympathy." A multi-court settlement therefore ratifies if the leader accepts, even if a covered minor would refuse.

**v0.2 locks the per-court gate:**

- **`overall_acceptance.carries` is true iff *every* covered court has a non-null `total` at/above its threshold AND has no per-court `hard_stops`** (a hard-stopped court — `total=null`, §11.2 — always blocks `carries`, inheriting the cleanup hard-stop rule `SETTLEMENT_UI_CLEANUP_SPEC.md:570`). Ratification (`confirm_settlement`) is offered only when `carries` is true. A covered court below threshold is a **holdout** that blocks the settlement until it is **eased** (dialed/edited toward acceptance) or **dropped** from coverage (it stays at war). REVIEW omits `confirm_settlement` while any covered court is a holdout (extends the existing below-threshold-blocks-ratify rule, `SETTLEMENT_UI_CLEANUP_SPEC.md:570/597`, from "the score" to "every court's score").
- **A holdout is never a dead-end.** Every holdout court row exposes both `Ease <court>` (focused `More generous`, §11.3) and `Drop <court>` (focused `settlement_cover_drop`, §11.3) as one-click actions. Dropping leaves that pair at war.
- **REVIEW carries `per_court_acceptance` too**, not only PROPOSE — so the gate and the displayed blocking reason are the same data. (Today REVIEW carries a single `acceptance` object; it gains the per-court block.) The single `acceptance` object is retained for the n=1 bilateral case and as the leader-row summary.
- **Regression surface (call out for the implementer):** existing multi-court settlement tests/fixtures that assume leader-gating may change verdict under per-court gating. Updating them to per-court expectations is expected and is *not* a regression — the suite must still end green. Named owner test: `test_ratify_requires_all_covered_courts_at_or_above_threshold_not_just_leader`.
- **Migration bound (so Slice 1 stays single-session-sized).** The fixture-update scope is **enumerated**, not open-ended: `grep -rE "can_ratify|carries|confirm_settlement" tests/test_settlement_*.py tests/test_common_peace_*.py`, filtered to **multi-court** fixtures (≥2 covered courts). Update exactly those in the **same commit** as the gate change so the diff is legible (RR1). **Single-court / bilateral (n=1) fixtures are unaffected** — the lone covered court *is* the leader, so the gate verdict is identical; the scorer's component math (the bulk of `tests/test_common_peace_acceptance.py`) is untouched because the formula does not change, only the gate that reads it. **Escape hatch:** if the enumerated migration plus Slice 1's 16 named tests (§14) would exceed the project's ~55-test single-session ceiling, split the gate + REVIEW per-court block + migration into **Slice 1b**, leaving baseline + PROPOSE + routing in **Slice 1a** (1b depends only on 1a, no parallel coupling).

**Why per-court (historical + UX, answering the v0.2 design question).** *Historical analogue:* Napoleonic coalition wars ended by each court making its **own** peace, never a bloc signature — Pressburg (1805): Austria signed while Russia withdrew and Britain fought on; Tilsit (1807): Napoleon signed **separate** treaties with Russia (lenient) and Prussia (punitive). "Dropping a holdout" is exactly the historical "separate peace; the holdout fights on" (Britain is the archetype). The single-leader gate is the ahistorical one. *UX:* if the gate were single-leader, the per-court rows would be dishonest (showing "Prussia refuses" while the peace ratifies); per-court makes the displayed acceptance the real gate, and the ease/drop lever prevents any hard block.

---

## 12. Multi-party cross-court validity rules

Valid-by-construction spans the whole covered set. These rules are enforced in `validate_settlement_terms` (`settlement_preview.py:2180`, the source of truth) and **mirrored** by the pickers (§13). Each has a named test (§14).

- **V1 — No region promised to two courts.** Across all `territory_cede` clauses, each `region` appears at most once regardless of `from`/`to`. Violation → `region_double_promised` with both offending clause indices. (`test_no_region_promised_to_two_courts`.)
- **V2 — Cannot bind a non-covered court.** Every clause's `from`/`to` and dependency roles must be a participant that is proposer-side **or** a court in `covered_enemy_participants`. A clause referencing an uncovered enemy → `clause_target_uncovered` (the cleanup spec already defines this code, `:594`). Dropping a court invalidates clauses that reference it. (`test_clause_cannot_bind_uncovered_court`.)
- **V3 — from/to must match the correct war side.** Demand clauses burden the accepting side; concession clauses burden the proposer side; the burdened party's side must match its actual side in `war_instance` (reuse `_side_for_nation`, `settlement_preview.py:345`). Violation → `clause_side_mismatch`. (`test_clause_from_to_must_match_war_sides`.)
- **V4 — No self-reference.** `from != to`; a court cannot cede to or pay itself; for `liberation`, `vassal_nation`, `lord_nation`, `liberator` must be three distinct, correctly-sided nations (already enforced by `evaluate_liberation_eligibility`, `:1644`). This is the rule that kills *France-liberates-France*. (`test_settlement_no_self_referential_clause`.)
- **V5 — Coverage floor.** At least one covered enemy must remain (`:586`); an empty covered set → `no_covered_enemy_participants`.

V1, V3 (the "right side" generalization across a multi-court set) are the genuinely-multi-party additions; V2, V4, V5 already exist for the single-court path and extend to the set. All five run at POST-preview, at Submit revalidation, and inside the fresh-rescore ratify gate (defense in depth, mirroring SC-5R-1).

---

## 13. Picker valid-by-construction rules (the cure)

Pickers mirror the validator (§12) so the illegal cannot be **authored**, not merely rejected. Authority remains the validator (`SETTLEMENT_UI_CLEANUP_SPEC.md:609`); pickers are a filtered view of it.

- **P1 — Add Clause disabled when a clause type has no valid target.** `_build_clause_control_schema_for_review` (`settlement_preview.py:2976`) computes `enabled` **per clause type** from whether its required pickers have ≥1 valid option after filtering; sets `enabled=False` + `disabled_reason_display` otherwise. This implements the **backend** half of the cleanup-spec line-601 contract that was never wired (today it hardcodes `enabled=True` at `:3001`). Applies to: territory with no controlled regions, gold with no payable amount, dependency clauses with no valid target, same-side forced alliances, and **liberation with no valid vassal**. **Frontend half:** the Godot editor *consuming* these flags (greying the Add Clause control + surfacing the reason instead of opening an empty picker) is **REFRONT-8**, landing with the Tier-3 editor in **Slice 3** — Slice 0 lands only the backend computation.
- **P2 — Role pickers filtered to valid sides.** Each role picker offers only legal participants:
  - `liberation.vassal_nation` → **current vassals only** (`_vassal_control_options`, `:2832`); **the `vassal_options or nation_options` fallback at `:2959` is removed** so non-vassals (including France) can never appear.
  - `liberation.lord_nation` → the vassal's current lord; `liberation.liberator` → opposite-side participants (mirror `evaluate_liberation_eligibility`).
  - `territory_cede.region` → only regions the selected `from` controls; `from`/`to` filtered to opposite war sides.
  - `gold_indemnity` payer/payee filtered to opposite sides; `amount` max bounded by payer treasury.
  - `forced_alliance` → covered enemy targets not already in an equivalent alliance; same-side imposition disabled.
- **P3 — Pickers update on coverage/focus change.** Toggling `covered_enemy_participants` re-filters every picker and re-computes `enabled` (clauses referencing a now-uncovered court go invalid per V2).

P1 + the P2 liberation fallback removal are exactly the **interim band-aid** (§16); the rest of P2/P3 land with Slice 3.

---

## 14. Slice plan with named behavior tests

Per Golden Rule #9 / the docs deferral rule, every requirement names a behavior test, and every deferred/cut item has an owner row + landing slice + completion definition + test. The interim band-aid is **Slice 0** and is independently shippable (§16).

### Slice 0 — Interim picker band-aid (independent de-risk; lands the **backend** half of the cleanup-spec line-601 contract) — **LANDED at master `4ffdfcc`** (backend only; suite `10256 passed, 1 skipped`, ruff clean)
- **Scope:** P1 **backend computation** (`enabled` per clause type + `disabled_reason_display`) and the P2 liberation `vassal_options or nation_options` fallback removal in `settlement_preview.py`. **Backend-only by design.** The Godot editor's *consumption* of `enabled`/`disabled_reason_display` — greying/disabling the Add Clause control and surfacing the reason **instead of opening an empty picker** — is **not** Slice 0; it is owned as **REFRONT-8** and lands with the Tier-3 editor in **Slice 3**.
- **Tests:**
  - `test_clause_add_disabled_when_picker_filter_empty_for_each_live_clause` *(the cleanup-spec line-618 test that never landed)*
  - `test_liberation_vassal_picker_excludes_non_vassals`
  - `test_clause_control_schema_enabled_false_carries_disabled_reason`
  - `test_settlement_no_self_referential_clause` (liberation France-France-France not constructible **or** rejected pre-stage)
- **Completion:** no live clause type's schema row renders an *enabled* empty picker (disabled rows carry `enabled=False` + a humanized reason and stay schema keys so `available_clause_types[]` is unchanged); liberation offers only real vassals — and because the Godot picker faithfully renders that options list, **`vassal=France` is unconstructable end-to-end**; full suite green. **What Slice 0 does NOT close:** the full line-601 *editor UX* ("Add Clause control disabled instead of opening an empty picker") for other empty-picker clause types — that needs the Godot consumer in **REFRONT-8 / Slice 3**, so Slice 0 alone does **not** fully unblock the Gate 4 smoke pass.

### Slice 1 — Tier 1 baseline (multi-party, any side) + PROPOSE surface + per-court gate — **LANDED May 30, 2026** (full deterministic + default-random suites `10278 passed, 1 skipped`; ruff clean; Godot 4.4.1 headless parse exit 0; REFRONT-V voice landed with it)
- **Scope:** generalize `_compute_concession_baseline` → `compute_settlement_baseline` (per-court direction, OQ#5); add `dialogue_mode="PROPOSE"` + the `per_court_acceptance` / `overall_acceptance` payload (§11.2); add the **per-court ratification gate** (§11.4) — `carries` iff every covered court ≥ threshold, REVIEW carries `per_court_acceptance`, holdout courts surface ease/drop; render the PROPOSE surface; route `propose_common_peace` to land PROPOSE (not blank EDIT).
- **Implementation clarification (no design change):** the demand-direction baseline gates added demands on the **near-acceptance floor** (don't suggest a demand that would make a court *outright reject*), NOT the accept threshold as this section's OQ#5 prose literally read. Reason: `base_side_pressure` is **package-level** (§11.2), so in a *mixed* war a led court shares the package's middling pressure — an accept-threshold gate would back every demand off to peace, defeating "demands from winning courts." A demand court may therefore seat as a near-acceptable **holdout** the player eases/drops; the baseline **never suggests a demand that pushes a court below the near-acceptance floor** (`_demand_terms_for_court` scores each candidate and keeps it only while the court stays at/above the floor — a court whose white peace already rejects under the shared package pressure stays an ease/drop holdout regardless of terms), not a blanket `carries=true` (already the OQ#5 holdout posture). The PROPOSE→EDIT `Adjust terms` action is handled **client-side** in Godot (it mounts the Tier-3 editor and never round-trips); the bilateral terms-guidance flow keeps sole ownership of the backend `adjust_terms` action id.
- **Tests:**
  - `test_settlement_baseline_demands_from_winning_courts_concedes_to_losing`
  - `test_settlement_baseline_per_court_direction_uses_per_court_direct_score_not_side_pressure` (OQ#5 — the v0.4 CRITICAL fix: direction reads `direct_scores[court]`, not the package side-pressure scalar)
  - `test_per_court_direction_threshold_is_war_score_margin_not_side_pressure_constant` (Run-#4 MAJOR — direction dead-band is `DIRECT_SCORE_DIRECTION_MARGIN` on the war-score scale, not `LOSING_SIDE_PRESSURE_THRESHOLD`)
  - `test_settlement_baseline_court_with_no_demand_or_concession_uses_peace_floor` (OQ#5 dead-band → `{"type":"peace"}` neutral floor)
  - `test_settlement_baseline_no_direct_score_court_is_hard_stopped_not_peace_floored` (Run-#4 CRITICAL — `select_direct_score` returns `None` → per-court hard-stop row matching `HARD_STOP_NO_DIRECT_WAR_SCORE`, never neutral-floored)
  - `test_settlement_baseline_suggestions_are_valid_by_construction`
  - `test_settlement_baseline_is_deterministic_same_world_same_terms` (no RNG — OQ#6)
  - `test_propose_mode_payload_shape_per_court_and_overall`
  - `test_per_court_call_varies_leader_and_holdings_holds_covered_set` (§11.2 pinned call signature)
  - `test_ratify_requires_all_covered_courts_at_or_above_threshold_not_just_leader` (§11.4 gate change)
  - `test_review_payload_carries_per_court_acceptance`
  - `test_holdout_court_offers_ease_or_drop_not_dead_end`
  - `test_baseline_concede_court_at_near_acceptable_is_flagged_holdout_not_auto_carry` (Run-#3 — baseline target vs §11.4 carry gate)
  - `test_overall_carries_false_when_any_covered_court_hard_stopped_total_null` (Run-#3 — null/hard-stop `carries` edge)
  - `test_propose_does_not_block_end_turn_and_back_out_preserves_scoped_draft`
  - `test_propose_landing_replaces_blank_edit_as_default`
- **Completion:** opening settlement lands a populated, valid, per-court PROPOSE surface; per-court baseline direction reads `direct_scores` (not the package side-pressure scalar); ratification gates on every covered court; holdouts are ease/droppable; end turn discards, Back Out preserves; **the REFRONT-V multi-court voice resolver rule exists so PROPOSE per-court copy resolves to named diplomats (no anonymous beats)**; suite green (including any leader-gating fixtures updated to per-court — §11.4 regression surface).

### Slice 2 — Tier 2 intent dials + live per-court acceptance — **IMPLEMENTED May 30, 2026** (suite-green: full deterministic + default-random `10298 passed, 1 skipped`; ruff clean; Godot 4.4.1 parse 0 failures — audit fold applied: focused-seed clause-cap + symmetric proposer-leader guard)
- **Scope:** `settlement_dial_harsher` / `settlement_dial_generous` (whole-table + focused court); `settlement_cover_add` / `settlement_cover_drop`; `settlement_focus_court`; live band + delta; Talleyrand targeted-posture advisory line.
- **Landed as:** `_redial_settlement_terms` (magnitude/count redraft, identity-preserving — OQ#7), `_handle_settlement_tier2_action` (the five PROPOSE verbs, player-only), `_restage_settlement_after_redraw` (PROPOSE-preserving re-preview + `previous_bands` delta), `_settlement_targeted_posture_advisory` (voice-only), `_settlement_remaining_war_courts` (`ignored_participants`/`remaining_wars`), the `balance_projection` memoization param on `calculate_common_peace_acceptance` + the shared one-projection pass in `compute_per_court_acceptance` (§15 F-5), the per-row `dial_actions` focused `Press <court>` / `Ease <court>` affordances (OQ#1 / §17), and the `action_params` transport (executor dispatch tuple + `SETTLEMENT_DIALOGUE_DISPATCH_ACTION_IDS` + `/respond_to_diplomatic_dialogue` endpoint + Godot `SETTLEMENT_DIALOGUE_ACTIONS` + `proposal_confirm_popup.gd` per-row affordance buttons + `api_client.send_dialogue_response_with_params`). **Audit fold:** the focused-dial seed (the `len(scope)==1` untouched-court path) now honors `MAX_SETTLEMENT_CLAUSE_COUNT` (a maxed package yields a valid no-op redraft instead of an over-cap draft the restage revalidation would reject) and guards both seed shapes on a known proposer leader (no malformed `to:""` / `from:""` clause). Tests in `tests/test_settlement_refront_slice2.py` (18).
- **Tests:**
  - `test_harsher_dial_rescores_all_covered_courts`
  - `test_focused_dial_applies_to_single_court_only`
  - `test_per_court_acceptance_payload_band_and_top_blocker`
  - `test_dial_delta_previous_to_current_band_presentation_only`
  - `test_coverage_drop_court_rescores_and_updates_remaining_wars_and_ignored`
  - `test_coverage_add_court_redraws_baseline_for_new_set`
  - `test_targeted_posture_is_voice_only_not_applied`
  - `test_per_court_scoring_shares_one_direct_score_side_pressure_harshness_and_balance_projection_pass` (scale — Golden Rule #8; see §15 balance-projection memoization param)
  - `test_balance_projection_param_falls_back_to_internal_compute_when_not_injected` (§15 F-5 internal rewire preserves existing single-call callers)
  - `test_dial_changes_magnitude_without_silently_swapping_requested_identity` (OQ#7 — Tier-2 harsher/generous changes amount/region count, never the requested region/payer identity)
  - `test_focused_seed_honors_clause_cap_no_op_when_package_maxed` (audit fold — focused seed never exceeds `MAX_SETTLEMENT_CLAUSE_COUNT`; a maxed package is a valid no-op redraft, not an over-cap draft)
  - `test_focused_seed_skips_when_proposer_leader_unknown` (audit fold — an unknown proposer leader yields no seed in either direction, never a malformed empty-party clause)
- **Completion:** dials move per-court acceptance live, whole-table and focused; coverage edits re-score; advisory targeting never mutates terms; the per-court loop runs one shared score/projection pass; suite green. **Gate 4 manual smoke re-runs here.**
- **Deferred-with-owner (Golden Rule #9):** `settlement_focus_court` ships as a backend-ready, presentation-only handler (no term mutation, no re-score — tested by `test_settlement_focus_court_is_presentation_only_no_term_change`); its **UI trigger** (click a per-court row to focus → expand that court's full 10-component Tier-3 breakdown, OQ#4) lands with the **Slice 3** Tier-3 editor, since the focused-detail panel it drives is the Tier-3 surface. Focused *dialing* (the §17 "press Prussia" need) is already reachable in Slice 2 via per-row `dial_actions`, so the missing focus trigger does not block any Slice 2 behavior. **Split escape hatch (sizing):** if the dial + coverage + scale tests exceed the ~55-test single-session ceiling, split coverage editing (`settlement_cover_add` / `settlement_cover_drop` + their re-score/`remaining_wars` tests) into **Slice 2b**, leaving the dials + focus + advisory in **Slice 2a** (2b depends only on 2a, no parallel coupling).

### Slice 3 — Tier 3 valid-by-construction editor (folds in DWL-SET-SC5R-3) — **IMPLEMENTED May 30, 2026** (full deterministic + default-random suites `10309 passed, 1 skipped`; ruff clean; Godot 4.4.1 headless parse exit 0; **REFRONT-8 + DWL-SET-SC5R-3 flip to LANDED**)
- **Scope:** `Adjust terms` from PROPOSE → EDIT (optionally focused court); cross-court validity V1–V5 in `validate_settlement_terms`; full P2/P3 picker filtering; **REFRONT-8 — the Godot Tier-3 editor consumes `clause_control_schema[type].enabled` / `disabled_reason_display`** (greys/disables the Add Clause item for disabled types + surfaces the reason instead of opening an empty picker; closes the line-601 editor UX whose backend precondition Slice 0 landed); **DWL-SET-SC5R-3 inline merge-conflict `Discard new clause` / `Replace active clause` controls** (cleanup spec `:589`).
- **Landed as:** V1 `region_double_promised` (structural, always-on, returns both indices) + V2 `clause_target_uncovered` (gated on known `war_instance`/`proposer_side`/covered; liberation binds `lord_nation`/`liberator` only via `_clause_role_nations`, NOT the freed vassal) + V3 `clause_side_mismatch` (`_CROSS_SIDE_TRANSFER_CLAUSE_TYPES` via `_side_for_nation`, also kills `from==to`) in `validate_settlement_terms`; the `covered_enemy_participants` validator param threaded into POST-preview (`main.py`), EDIT Submit revalidation (`diplomatic_executor.py` — defense-in-depth), and the dial/coverage restage + replacement re-validations; `_nation_control_options` proposer-side+covered filtering (P2/P3) threaded via `_build_clause_control_schema_for_review` ← `build_settlement_confirm_dialogue`; `settlement_editor_popup.gd` REFRONT-8 (`_populate_add_clause_selector` greys disabled types + `set_item_disabled`, `_on_add_clause_pressed` surfaces the reason) + DWL-SET-SC5R-3 (`_find_conflict_for_new_clause` mirrors `CLAUSE_CONFLICT_MATRIX` + V1; `_on_discard_new_clause_pressed` / `_on_replace_active_clause_pressed`) + `focused_court` header. **The ratify gate stays type-only by design** (its staged terms use apply-format `regions` plural + `gold_lump` aliases the canonical validator rejects; authoring-time POST-preview + Submit is the V1–V3 enforcement contract). 11 tests in `tests/test_settlement_refront_slice3.py`.
- **Tests:**
  - `test_adjust_terms_from_propose_opens_edit_optionally_focused`
  - `test_no_region_promised_to_two_courts` (V1)
  - `test_clause_cannot_bind_uncovered_court` (V2)
  - `test_clause_from_to_must_match_war_sides` (V3)
  - `test_merge_conflict_discard_new_clause_control` (DWL-SET-SC5R-3)
  - `test_merge_conflict_replace_active_clause_control` (DWL-SET-SC5R-3)
  - `test_tier3_picker_refilters_on_coverage_change` (P3)
  - `test_tier1_default_identity_remains_replaceable_in_tier3` (OQ#7 — the Tier-1 pre-filled region/gold default can be changed or replaced in the editor)
  - `test_godot_editor_disables_add_clause_for_disabled_type_and_surfaces_reason` (REFRONT-8 — the Godot consumer of Slice 0's `enabled` / `disabled_reason_display`)
- **Completion:** Tier 3 cannot author any V1–V5 violation; the editor honors `enabled` / `disabled_reason_display` (REFRONT-8 — no disabled clause type opens an empty picker); merge-conflict controls work; `DWL-SET-SC5R-3` and `REFRONT-8` flip to LANDED; suite green.

### Voice — Multi-court settlement-table voice (NEW; closes Voice Bible gap B4) — **LANDED May 30, 2026 with Slice 1**
- **Landed as:** `resolve_multi_court_settlement_voice` (`diplomatic_templates.py`) + the `settlement_multi_court_*` template family; `DIPLOMAT_VOICE_BIBLE.md` §16.1a; wired into the per-court rows in `build_settlement_confirm_dialogue` (`voice_line` + `speaker_display` per row, `multi_court_table_narration` on the dialogue). Tests: the 3 §14 Voice tests + the PROPOSE integration pin in `tests/test_settlement_refront_slice1.py`.
- **Owner / landing:** the resolver rule + family **land before or with Slice 1's PROPOSE copy — not after** (otherwise Slice 1's per-court lines have no resolver contract and risk the anonymous-voice beats §13 forbids); Slice 2's dial copy extends the same family; tracked as spec row REFRONT-V. **Slice 1 completion depends on this resolver rule existing (see Slice 1 completion).**
- **Scope:** `DIPLOMAT_VOICE_BIBLE.md` gains a **multi-court settlement** section: each covered court's line resolves through its **named diplomat** (Castlereagh/Hardenberg/Metternich/Einsiedel) via the existing resolver/fallback chain (Voice Bible Cross-cast:239-243); **Talleyrand narrates the table** and flags the binding constraint. No anonymous voice at multi-court beats. **Per cleanup SC-32 D5 (§2 boundary), committed copy must not use "conference," "congress," or "veto"** — it uses "settlement," "the table," "these courts," "<court> holds out / signs."
- **Tests:**
  - `test_multi_court_per_court_voice_resolves_named_diplomat_or_chancery_fallback`
  - `test_talleyrand_narrates_table_and_binding_constraint`
  - `test_committed_multi_court_copy_avoids_conference_congress_veto_terms` (SC-32 D5 copy boundary)
- **Completion:** Voice Bible has an authored multi-court family; per-court lines resolve to named diplomats; no committed copy implies conference/veto; suite green.

### Deferred / cut items (owned, not orphaned)

| Row | Item | Decision | Landing / completion | Test |
| --- | --- | --- | --- | --- |
| **REFRONT-5** | Incoming-offer (SC-5/SC-30) presentation convergence onto per-court model | **DEFER** (post Slices 1–3) | Lands when SC-30 inbound UI is revisited; completion = incoming offers render the same `per_court_acceptance` block | `test_incoming_offer_uses_per_court_presentation` |
| **REFRONT-6** | Bounded presentation-only novelty variation for repeat conferences | **CUT (default)** | Only if ever wanted: a gated presentation slice; completion = variation provably never changes the scored result | `test_presentation_variation_never_changes_scored_result` |
| **REFRONT-7** | `_region_control_options` full-region scan hardening for full-Europe | **DEFER** (scale hardening) | Pre-filter region picker by participants' holdings via `get_nation_regions` instead of scanning all regions; completion = no all-regions scan in the Tier-3 schema build | `test_region_picker_options_scale_with_participants_not_world` |
| **REFRONT-8** | Godot Tier-3 editor *consumes* `clause_control_schema[type].enabled` / `disabled_reason_display` | **LANDED in Slice 3 (May 30, 2026)** — `settlement_editor_popup.gd::_populate_add_clause_selector` greys disabled types (`set_item_disabled`) + appends the reason; `_on_add_clause_pressed` surfaces `disabled_reason_display` instead of opening an empty picker | Closed: the editor honors `enabled`/`disabled_reason_display`; line-601 *editor UX* delivered | `test_godot_editor_disables_add_clause_for_disabled_type_and_surfaces_reason` ✓ |
| **DWL-SET-SC5R-3** | Inline merge-conflict Discard/Replace controls | **LANDED in Slice 3 (May 30, 2026)** — `_find_conflict_for_new_clause` (mirrors `CLAUSE_CONFLICT_MATRIX` + V1) holds a conflicting new clause; `_on_discard_new_clause_pressed` / `_on_replace_active_clause_pressed` resolve it inline | Closed: both controls land with tests | `test_merge_conflict_discard_new_clause_control`, `test_merge_conflict_replace_active_clause_control` ✓ |
| **Slice G / AI-ally agency** | AI-side settlement authoring + ally petitions | **SEPARATE / LATER.** The **SC-32 / Slice G2 decision ledger (D1–D7) already LANDED** (`STATUS.md`, May 28) — resolved mostly as **CUTs** (AI counterproposals D1, Wait-for-Offer + Ask-for-Terms D2, voluntary alliance D3, conference/veto D5, request_consultation/request_redress D4c) plus a thin advisory ally-petition substrate (D4a/D4b) and the same-war replace-confirm chooser (D6). The **still-unbuilt** AI-side work is owned **by the cleanup spec, not here**: **Slice G1** (AI settlement *offer producer* + Request Terms — gated behind **Gate 4 smoke + explicit SC-5 reversal**, `SETTLEMENT_UI_CLEANUP_SPEC.md:858`), the broader **Slice G2 follow-through** (gated behind Slice G1 + SC-29/SC-30/SC-31 closure, `:859`), and **Slice H** (deferred ally-petition types `request_reward_or_restoration` / `demand_bargain_honor`). | Completion: this re-front ships **no** AI-initiated settlement path — the new PROPOSE / dial / coverage routes are **player-only** (mirror the cleanup `can_edit_terms` / `caller_kind` rule, cleanup `:556`); AI agency lands or is explicitly cut in Slice G1 / Slice G2 / Slice H, **not here**. | `test_propose_and_dial_routes_reject_non_player_caller_kind` (absence test owned **here**) |

---

## 15. Concrete reuse map (verified file:line)

Every row was checked against the codebase during v0.2 authoring. "EXTEND" = call/wrap existing code; "FIX" = correct a divergence; "NEW" = genuinely net-new (flagged honestly).

| Need | Reuse (verified file:line) | New vs Extend |
| --- | --- | --- |
| Tier-1 baseline, concession direction | `_compute_concession_baseline` `settlement_preview.py:1967`; region pick `_concession_baseline_select_transferable_region:1392`; payer balance `:1333` | **EXTEND** into per-court loop `compute_settlement_baseline` |
| Tier-1 baseline, demand direction | `generate_suggested_terms` `diplomatic_templates.py:1889` (5-stage, `NATION_DESIRE_PROFILES`, border/coveted selection via cached `world.get_nation_regions()`) | **EXTEND** (borrow demand-stage selection per court) |
| Per-court live acceptance | `calculate_common_peace_acceptance` `settlement_scoring.py:1884` — already accepts memoized `direct_scores` (:1896) + `side_pressure_result` (:1895) + `raw_total_harshness` (:1897) | **EXTEND** — thin aggregator calls once per covered court over **one** shared `compute_direct_scores_by_enemy:192` + `compute_side_pressure_score:278` pass; **add** one new memoization param so the package-level `project_balance_after_settlement` (:1537) projection is shared across courts (see scale hook below) |
| Per-court ratification gate | `revalidate_staged_settlement:3877`, `ratify_settlement_confirm:4583`, `can_ratify`/`build_settlement_preview:2434` (today single `accepting_leader`) | **EXTEND** — gate on every covered court (§11.4); deliberate behavior change, regression surface |
| Intent dials | `modify_harsh` `diplomatic_executor.py:3101` (+ `modify_generous` `:3534`) — **action-string branches inside `_execute_diplomatic*`, not standalone functions**; option template `diplomatic_templates.py:226-296` | **EXTEND** — apply to settlement package; whole-table vs focused court |
| Acceptance band display | **raw scorer returns `verdict` + `feedback` only** (`calculate_common_peace_acceptance`, docstring steps 14-15); **`_enrich_acceptance_display` (`settlement_preview.py:274`) derives the display fields** `band` / `band_display` / `band_phrase` / `top_components` / `top_blocker_display` from that raw output; the `acceptance_breakdown` result key is built in `_execute_diplomatic_feasibility` (`diplomatic_executor.py:389-432`, R31 — a result key, not a standalone function). PROPOSE's compact `per_court_acceptance` exposes only `band` + `top_blocker_display` (OQ#4); the full `feedback`/`top_components` table stays Tier-3. | **REUSE** as-is |
| PROPOSE surface + payload | new `dialogue_mode="PROPOSE"`; `per_court_acceptance`/`overall_acceptance` block | **NEW** (thin; composed from scorer + baseline) |
| Per-court aggregator | wraps the scorer N times sharing one score pass | **NEW** (thin) |
| Tier-3 editor | `settlement_editor_popup.gd` (CanvasLayer 112); `_build_clause_control_schema_for_review` `settlement_preview.py:2976`; validator `validate_settlement_terms:2180` | **EXTEND** |
| Picker `enabled` computation | `_build_clause_control_schema_for_review:2976` (hardcodes `enabled=True` at `:3001`) | **FIX** — compute per picker emptiness (cleanup spec `:601`) |
| Liberation picker filter | `_clause_fields_for_review:2839`; bug at `:2959` (`vassal_options or nation_options`); `_vassal_control_options:2832`; validator `evaluate_liberation_eligibility:1644` | **FIX** — drop `or nation_options` fallback; filter roles to valid sides |
| Cross-court validity V1–V5 | `validate_settlement_terms:2180`; `_side_for_nation:345`; `_active_cross_side_pairs:360` | **EXTEND** (V1, V3 multi-court additions) |
| Coverage editing | `_render_covered_enemies` (Godot); `get_coverable_enemy_participants:1291`; checklist re-preview (cleanup spec `:594`) | **REUSE** + conversational prompt over same state |
| Draft persistence | `save/load/discard_scoped_settlement_draft` `settlement_preview.py:2676/2701/2721`; `pending_settlement_drafts_by_key` (world_state); `suspend_settlement_editor` handler | **REUSE** unchanged |
| Ratification **mutation** (post per-court gate) | `ratify_settlement_confirm` fresh-rescore `confirm_settlement` mutation path | **REUSE** — the mutation is unchanged; it runs only **after every covered court passes** the per-court gate. The gate *decision* itself is **EXTEND** (row above, §11.4); this row is the mutation that executes once the gate is satisfied. |
| Multi-court settlement voice | Voice Bible §16.1 families; named-diplomat resolver / fallback chain (Cross-cast:239-243) | **NEW** multi-court resolution rule (Voice Bible has no multi-court rule today); committed copy obeys the SC-32 D5 boundary (§2) — no "conference"/"veto" copy |

**Scale-readiness design hook (Golden Rule #8).** Per-court scoring is N calls (N = covered courts in **one** war, bounded — typically a handful), invoked on **user dial/coverage actions**, not in a per-turn AI hot path. Three of the scorer's heaviest inputs are **package-level** (identical across the per-court loop) and must be computed once per dial action and shared:
- `direct_scores` — `compute_direct_scores_by_enemy:192` (the scorer already accepts it memoized at :1896),
- `side_pressure_result` — `compute_side_pressure_score:278` (side-level quantity, identical across courts; memoized param at :1895),
- `raw_total_harshness` — `calculate_raw_treaty_harshness` (the scorer already accepts it memoized at :1897; the package's harshness is one value across the per-court loop),
- the balance projection — `project_balance_after_settlement:1537` takes `(world, *, war_id, settlement_terms)` and is **independent of `accepting_leader`** (verified signature has no leader arg), so it is identical across courts. The scorer currently calls it **internally** with **no** injection param (unlike the three above). **Slice 2 must do two things:** (1) add a `balance_projection: Optional[Mapping[str, Any]] = None` param to `calculate_common_peace_acceptance` mirroring the existing memoized-param pattern (`side_pressure_result:1895` / `direct_scores:1896` / `raw_total_harshness:1897`); and (2) **rewire the scorer's internal `project_balance_after_settlement(...)` call site** to use the injected value when supplied and fall back to computing it when `None` — so every existing single-call caller is unchanged (they pass nothing and still get a correct projection). The aggregator then computes the projection **once per dial/coverage action** and passes the same object to each per-court call. Test: `test_balance_projection_param_falls_back_to_internal_compute_when_not_injected` (Slice 2). **Slice 1 does not touch this:** its per-court calls omit `balance_projection`, the scorer recomputes internally (O(N) projections — correct, acceptable on current maps), and **no Slice-1 call references the not-yet-existing param** (resolves the cross-slice ordering — the param is purely the Slice-2 scale step).

With these shared, each per-court call only finalizes the court-specific components (`leader_own_losses`, that court's `war_objective_alignment`, its `burdened_participant_penalty`). No per-court re-scan of `world.regions`; lookups use cached `get_nation_regions()` / `get_active_nations()`. The one remaining all-regions scan (`_region_control_options:2816`, in the Tier-3 schema build) runs once per POST-preview (user-initiated, not per-turn) and is recorded as scale-hardening row REFRONT-7.

---

## 16. Interim de-risk band-aid (optional, independent)

Strictly a symptom patch that can ship **before** the full re-front to **de-risk** the current Gate 4 pass. It is **Slice 0** above and lands the **backend half** of a contract that already exists in `SETTLEMENT_UI_CLEANUP_SPEC.md` (line 601) but was never wired:

- Compute `enabled` per clause type in `_build_clause_control_schema_for_review` (P1) — **backend computation only.**
- Remove the `vassal_options or nation_options` fallback in liberation's `vassal_nation` field (`:2959`) so the picker offers only real vassals (P2 liberation). Because the Godot picker faithfully renders the options list, this lands **end-to-end**: `vassal=France` is unconstructable in the editor.
- Land the cleanup-spec line-618 test `test_clause_add_disabled_when_picker_filter_empty_for_each_live_clause` (it does not exist today).

It does **not** add the baseline, dials, per-court acceptance, or conversational front — that is the cure (Slices 1–3). **Nor does it close the line-601 *editor UX* in full:** the Godot editor does not yet *consume* `enabled`/`disabled_reason_display`, so a disabled clause type (other than the now-filtered liberation vassal pick) can still be selected and opens an empty picker rejected only at Submit. That Godot consumer is **REFRONT-8**, folded into **Slice 3** — so Slice 0 alone does **not** fully unblock Gate 4. The band-aid has no dependency on the re-front and can land first.

---

## 17. Worked example — war with three courts

France is in one coalition war against **Britain + Prussia + Austria**. France's leverage differs per court: winning decisively vs Prussia, roughly even vs Austria, behind at sea vs Britain. This is the peace conference the model is built for. *("Conference" here is internal design shorthand per §2; committed player-facing copy never uses "conference" / "congress" / "veto" — it says "settlement" / "the table".)*

**Tier 1 — Talleyrand proposes one baseline, calibrated per court (illustrative numbers):**

```
SETTLEMENT — War of the Third Coalition          Talleyrand proposes:
  Prussia   request Silesia + 200g indemnity        Prussia  78%  will sign
  Austria   status-quo peace (no demands)           Austria  56%  leaning yes
  Britain   white peace                             Britain  62%  will sign
                                          OVERALL:  this peace carries
```
Per-court direction is chosen from **each court's direct war score** (`direct_scores[court]`, OQ#5) — **not** the package-level side-pressure scalar (which feeds only the shared `base_side_pressure` acceptance component, identical across courts): demand from Prussia (France leads it), concede/neutral to Austria and Britain. Talleyrand explains *why* per court. Every clause is a **suggestion the player can change**, and every clause is legal by construction. Nothing was randomly assigned.

**Tier 2 — steer by intent, watch each court react live.** Clicking *Harsher terms* (whole table) re-drafts and **re-scores per court**: Prussia ~44% (now refuses), Austria ~29% (refuses), Britain ~16% (hard reject). One dial, three different consequences, shown before committing. Focusing Prussia and clicking *Harsher* presses only Prussia.

**Coverage lever (multi-party only).** The player **drops Britain** from the conference; Britain stays at war while Prussia + Austria settle. `ignored_participants[]` / `remaining_wars[]` update; Talleyrand reads the consequence ("Britain stands alone on the Continent").

**Tier 3 — request specifics for the swing court.** Austria is the wobbler. The player clicks *Adjust terms* focused on Austria, **requests** a smaller border region instead of the suggested one and adds a gold sweetener France pays → Austria climbs 56% → ~71%. Pickers only offer regions Austria actually holds; Austria's land cannot be promised to Prussia (V1); France cannot cede to itself (V4).

**Ratify.** `Submit for Review` → REVIEW (fresh rescore). With every covered court at/above threshold, Ratify applies each pair's peace transition. If a court is below threshold, REVIEW omits `confirm_settlement` and blocks until the player eases that court or drops it.

**Why per-court, not blended:** a single averaged number would hide that the same package is generous to Britain and ruinous to Prussia. The conference scores each court independently so the player can see — and shape — exactly where the peace holds or breaks.

**Why it feels novel each time:** the next conference has a different set of courts with different desires, holdings, grievances, and coalition posture, plus Talleyrand's situation-specific read — so it reads fresh without any randomness in the underlying mechanics (OQ#6).
