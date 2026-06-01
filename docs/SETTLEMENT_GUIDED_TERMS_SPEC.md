# Settlement Guided Terms Spec

**Version:** v0.1 DRAFT
**Date:** 2026-05-31
**Status:** ⛔ **DESIGN GATE — NEEDS USER APPROVAL — DO NOT CODE.**
**Sequencing:** Tackle **after the Gate 4 manual settlement smoke completes** (see `docs/STATUS.md`). This spec retires a surface the smoke is partly exercising; finishing the smoke first shakes out the non-editor flows (PROPOSE / dials / ratification / losing / rejected) before we rebuild authoring on top of them.
**Supersedes:** the **Tier-3 freeform clause editor** of `SETTLEMENT_CONVERSATIONAL_REFRONT_SPEC.md` (the `settlement_editor_popup` + from/to identity pickers). It does **not** touch Tier-1 (Talleyrand baseline) or Tier-2 (intent dials) — those stay and become the foundation this builds on.

---

## 1. Why replace the freeform editor

The Tier-3 "Adjust terms" editor is a blank, freeform clause assembler: for every clause you pick both ends from identity pickers ("Ceding court" → "Receiving court"), the magnitude, and the asset. Three problems surfaced in the Gate 4 smoke:

1. **It defaults to `France` / `France` for everything.** Both ends of every clause default to the first nation in the list (the player). The most natural first action — clicking through — authors self-referential nonsense (France vassalizes France) that's only caught at Submit.
2. **It's vague.** A blank clause table gives no signal about what a *good* or even *valid* demand looks like. You assemble in the dark and find out at Submit.
3. **It diverges from every other peace surface in the game.** Normal two-way peace deals never use identity pickers. The bilateral `terms_guidance` flow ([backend/commands/diplomatic_executor.py:3858](../backend/commands/diplomatic_executor.py)) is a **guided, Talleyrand-led** sequence: Talleyrand *suggests* a concrete, valid region ("I suggest Silesia — [reason]"), you `Offer this` / `Not this one` / `That's enough`, then it walks you through gold and Action Points. **Direction is implied** by whether you're winning or losing (`war_score`/relation) — you never pick "who cedes to whom," so a self-referential clause is structurally impossible.

The two transport/validation bugs found alongside this (authored terms dropped at the `/command` Pydantic boundary; submit-time validation errors silent) were fixed at commit `067e431`. This spec addresses the deeper finding: **the editor's authoring *model* is wrong.** The fix is to make settlement authoring work like the rest of the game — guided, suggestion-driven, direction-implied — generalized to settlement's multi-party shape.

---

## 2. Design decisions (this gate)

| ID | Decision | Source |
|----|----------|--------|
| **D1** | **Replace the freeform editor entirely.** Guided per-court demands become the *only* term-shaping surface beyond Tier-1/Tier-2. The `settlement_editor_popup` + identity-picker schema are retired. | User, 2026-05-31 |
| **D2** | **Fold authoring into the existing per-court rows** on the PROPOSE surface. Each covered-enemy court row gains an inline, guided "demand" affordance — no separate screen. (Author's recommendation; user deferred.) | This spec §3 |
| **D3** | **Cover all *valid* clause types** via the per-court model, direction always implied. Same-side enemy↔enemy transfers are already invalid (validator V3 `clause_side_mismatch`), so there is no exotic free-direction case to support — every valid transfer straddles *your side ↔ one enemy court*. (Author's recommendation; user deferred.) | This spec §4 |

**Why D2 (per-court rows, not a separate wizard):** the per-court rows already exist (Tier-2: per-court acceptance band, direction, top blocker, named-diplomat voice, Press/Ease + holdout Ease/Drop). They are already the multi-party generalization of the bilateral single-target wizard. Folding demand authoring into them keeps everything on one screen with live re-scoring, and avoids a modal-on-modal. The bilateral flow is sequential only because it has one target; settlement has many, so a *row per court* is the right shape.

**Why D3 (all valid types, direction implied):** in a settlement you are dictating as the winner, every value transfer goes *enemy court → you*; dependency clauses make the *enemy court* the subject and *you* the lord/imposer; liberation is an action *against* the overlord court (free its vassal, you as liberator). There is never a need to pick identities. When you are *losing* a given court (its `direct_score` is negative — the concede direction already computed by `compute_settlement_baseline`), that court's row flips from demands to **offers** (*you → court*), exactly as the bilateral flow flips on `war_score`.

---

## 3. The guided flow (concrete)

### 3.1 Surface

The PROPOSE surface (Slice 1/2, already shipped) is unchanged in structure:

- **Talleyrand framing line** (voice).
- **Per-court table** — one row per covered enemy court.
- **Whole-table rail** — Harsher / More generous dials, coverage add/drop, `Submit for Review`, `Back Out`.

This spec **adds demand authoring inside each court row**:

- The row shows the **current demands on that court** as plain lines (e.g. "Cede Silesia", "300 gold") each with a magnitude control where relevant and a `Remove`.
- The row gains an **`Add demand`** affordance. It opens a **compact inline expansion** (not a new screen) listing Talleyrand-suggested, valid, *fully-formed* options for that court:
  - `Take [Silesia ▾] from Prussia` — region pre-picked (best border candidate), dropdown lists only regions Prussia controls (cedeable; `rank_cession_candidates` analogue).
  - `Demand [300] gold from Prussia` — amount pre-filled to an affordable default; magnitude adjustable.
  - `Demand [50]/turn for [3] turns from Prussia` — recurring gold.
  - `Vassalize Prussia` — shown **only if** `evaluate_vassalage_eligibility` passes (power cap, not already a vassal, at war).
  - `Subjugate Prussia` — shown only if `evaluate_subjugation_eligibility` passes.
  - `Force Prussia into alliance` `[☐ Continental System]`.
  - `Free Prussia's vassal [X]` — shown **only if** Prussia currently holds a vassal; liberator defaults to France.
- Adding, removing, or adjusting a demand **mutates the staged draft and re-scores live** — the court's acceptance band updates immediately — exactly like the Tier-2 dials already do (`action_params` over `/respond_to_diplomatic_dialogue`).
- **Direction is always implied**: the court is the conceder/subject; France (proposer) is the recipient/lord/imposer/liberator. No identity pickers exist. `France`/`France` is structurally impossible.
- **Options are valid-by-construction**: eligibility-gated options simply don't appear when invalid (mirroring `rank_cession_candidates` only ever offering cedeable regions). The validator (V1–V5) remains the authority as defense-in-depth, but should rarely fire.

### 3.2 Losing / concession direction

If France is **losing** a given court (that court's `direct_score < -DIRECT_SCORE_DIRECTION_MARGIN`, the concede direction from `compute_settlement_baseline`), that court's row shows **offers** instead of demands: `Offer [region ▾] to Prussia`, `Offer [N] gold to Prussia` — France is the conceder (regions drawn from France's holdings via the bilateral `rank_cession_candidates` path). The per-court direction is already computed; it simply selects demand vs. offer copy and candidate source. This is the home for the **losing-side concession authoring** the Gate 4 smoke exercises (it currently routes through the editor; it moves here).

### 3.3 Worked example (the smoke scenario: France vs Britain + Prussia, France winning)

1. Open Settlement → PROPOSE. Talleyrand proposes the baseline; the table shows **Britain** (near-acceptable) and **Prussia** (holdout).
2. On **Prussia's** row, click `Add demand` → inline options. Pick `Take [Silesia ▾] from Prussia`. The row gains "Cede Silesia"; Prussia's band drops and re-scores instantly.
3. Decide it's too harsh — click `Remove` on "Cede Silesia". It's gone; band recovers. (No merge, no re-add — the draft *is* the live state.)
4. On **Britain's** row, `Add demand` → `Demand [300] gold from Britain`. Bump magnitude to 400 with the row control; re-scores live.
5. Use whole-table `More generous` once to ease both courts toward carry.
6. `Submit for Review` → REVIEW → ratify (per-court gate, unchanged).

No identity pickers, no France/France, no "submit a blob then reconcile."

---

## 4. Clause → per-court demand mapping

Direction is fixed by the court's role; nothing below exposes an identity picker.

| Clause type | Demand copy (winning) | Offer copy (losing) | Direction (implied) | Valid-by-construction gate |
|---|---|---|---|---|
| `peace` | implicit on every covered court | — | — | always |
| `territory_cede` | Take [region] from `<court>` | Offer [region] to `<court>` | court → France (win) / France → court (lose) | region ∈ that court's cedeable regions (`rank_cession_candidates`) |
| `gold_indemnity` | Demand [N] gold from `<court>` | Offer [N] gold to `<court>` | court → France / France → court | affordable-amount default; solvency at validate |
| `gold_per_turn` | Demand [N]/turn × [T] from `<court>` | Offer [N]/turn × [T] to `<court>` | court → France / France → court | `GOLD_PER_TURN_*` bounds |
| `vassalage` | Vassalize `<court>` | (n/a — losing France can't vassalize) | court = subject, France = lord | `evaluate_vassalage_eligibility` |
| `subjugation` | Subjugate `<court>` | (n/a) | court = subject, France = lord | `evaluate_subjugation_eligibility` |
| `forced_alliance` | Force `<court>` into alliance | (n/a) | court = subject, France = imposer | court is covered enemy |
| `liberation` | Free `<court>`'s vassal [X] | (n/a) | lord = `<court>`, liberator = France | `<court>` holds a vassal; `evaluate_liberation_eligibility` |

**No exotic free-direction case remains.** A transfer between two enemy courts (both on the accepting side) already fails validator V3 (`clause_side_mismatch`), so it was never a valid clause — its absence from the guided flow is *correct*, not a deferral.

---

## 5. What is removed (explicit, per Golden Rule #9)

These are **removed**, not deferred — each has a landing slice (§7):

- `godot-client/project-sovereign/scenes/settlement_editor_popup.tscn` and `scripts/settlement_editor_popup.gd` — the freeform editor surface.
- The **identity-picker** half of the Tier-3 schema: the `from`/`to`/region identity pickers in `_clause_fields_for_review`, `_nation_control_options`, `_side_partitioned_options`, and the `clause_control_schema` / `available_clause_types` payload that fed the editor. (The **eligibility + candidate-generation** helpers — `rank_cession_candidates`, the `evaluate_*_eligibility` functions, the affordable-indemnity logic — are **kept and reused** for the guided suggestions.)
- The editor's **Submit-for-Review structured `propose_common_peace` POST** path, and the now-dead `settlement_terms` / `selected_target_nation` / `covered_enemy_participants` fields on `CommandRequest` (added at `067e431` to fix the live editor during the smoke; they become unused once authoring moves to `action_params`).
- The **same-war additive merge** of editor-submitted terms in `stage_settlement_confirm` (the `merge_same_war_settlement_drafts` call on the editor-submit path) — the merge-vs-replace question dissolves (§6). (The merge helper itself may still serve reopen; that is verified during GT-Slice-4 and removed if dead.)
- `DWL-SET-SC5R-3` inline merge-conflict controls (Discard new / Replace active) — no submit-blob means no merge conflict to resolve.

---

## 6. Why the merge/replace problem dissolves

The merge-vs-replace tension only exists because the editor is a **separate blob you assemble and then submit** — at submit time the backend has to reconcile your blob against the previously-staged draft (today: an additive `merge_same_war_settlement_drafts` that re-adds clauses you removed; a "replace" would discard concurrent state). 

In the guided model there is **no submit blob**. Every `Add demand` / `Remove` / magnitude change is an `action_params` mutation against the staged `settlement_confirm` (the Tier-2 dial transport, already shipped), and the **staged draft is the single source of truth**, re-scored on each action. `Submit for Review` is purely a PROPOSE→REVIEW state transition for ratification — it carries no terms to reconcile. So removals stick, edits apply, and there is nothing to merge or replace.

---

## 7. Backend reuse map

| Need | Reuse (verified to exist) |
|---|---|
| Per-court direction (demand vs offer vs peace floor vs hard-stop) | `compute_settlement_baseline` (Slice 1, `settlement_preview.py`) |
| Region candidates for a court | `rank_cession_candidates` (`diplomatic_executor.py:3846`) |
| Affordable indemnity default | the demand-stage logic in `compute_settlement_baseline` / `generate_suggested_terms` |
| Dependency/liberation eligibility gates | `evaluate_vassalage_eligibility`, `evaluate_subjugation_eligibility`, `evaluate_liberation_eligibility` |
| Live per-court re-score | `compute_per_court_acceptance` → `calculate_common_peace_acceptance` (Slice 2) |
| Per-court-row action transport | `action_params` on `/respond_to_diplomatic_dialogue` (Slice 2) |
| Authority on final validity | `validate_settlement_terms` V1–V5 (unchanged, defense-in-depth) |

New work is thin: per-court **demand-mutation verbs** (analogous to the existing `settlement_dial_*` / `settlement_cover_*` handlers) plus a per-court **suggestion payload** the rows render.

---

## 8. Open questions

- **OQ-1 — region choice UX.** For a court with several cedeable regions, offer a **dropdown of valid regions** in the inline expansion (rec) vs. the bilateral one-at-a-time `suggest → skip` loop. Rec: dropdown — it's a panel, not a wizard, so showing the valid set at once is lighter.
- **OQ-2 — keep whole-table dials?** Harsher / More-generous (whole-table + focused) vs. redundant once per-court authoring is explicit. Rec: **keep** — a fast "tune everything" pass over the explicit demands; they compose.
- **OQ-3 — liberation liberator.** Default liberator = France (player). Is a non-France liberator ever a real player goal in the guided flow? Rec: **no — France only**; a different liberator is an explicit out-of-scope cut.
- **OQ-4 — incoming offers & concession authoring.** Confirm that retiring the editor also re-homes (a) the **losing-side concession** authoring and (b) any **incoming-offer review** path that mounted editor surfaces, onto the guided per-court flow (§3.2). Must be settled before GT-Slice-4 removes the editor.
- **OQ-5 — REFRONT-9 fold.** The OQ#4 focused per-court component breakdown (re-front spec, owned as REFRONT-9) naturally becomes the expanded state of a per-court row here. Confirm we fold REFRONT-9 into GT-Slice-3 rather than landing it on the old editor.

---

## 9. Implementation slices (each: owner / landing / completion / tests — Golden Rule #9)

> All slices are **gated on approval of this spec** and **sequenced after the Gate 4 smoke**.

- **GT-Slice-1 — Per-court demand mutation (backend).** New dialogue verbs `settlement_demand_add` / `settlement_demand_remove` / `settlement_demand_set_magnitude`, resolved via `action_params` against the staged `settlement_confirm`; each applies the court's implied direction, mutates the draft, and re-scores live. **Completion:** a player can add/remove/adjust a demand per court and see live per-court re-scoring; direction never inverts identity; validator stays authority. **Tests:** add-territory-appears-and-rescores; remove-sticks; magnitude-adjust; eligibility-gated vassalize rejected when ineligible; losing court uses offer direction; player-only (Slice-G boundary).
- **GT-Slice-2 — Per-court suggestion payload.** Each per-court row carries `demand_suggestions[]` (valid, fully-formed, direction-correct options for that court) + `current_demands[]` with magnitude metadata. **Completion:** PROPOSE rows expose suggestions + current demands; suggestions are valid-by-construction. **Tests:** suggestions eligibility-gated; no identity fields exposed; France-self impossible; losing-court suggestions are offers.
- **GT-Slice-3 — Godot per-court demand UI.** `proposal_confirm_popup.gd` renders the inline `Add demand` expansion, current-demand lines, and magnitude controls per row, routed through `send_dialogue_response_with_params`. Folds **REFRONT-9** (focused breakdown = expanded row). **Completion:** in-game per-court authoring on one screen; Godot 4.4.1 parse exit 0. **Tests:** Godot source pins + parse harness; REFRONT-9 breakdown test.
- **GT-Slice-4 — Retire the freeform editor.** Remove the surfaces/fields/merge path in §5; repurpose retained candidate/eligibility helpers; migrate or delete the SC-5R-2 editor tests; remove the dead `CommandRequest` settlement fields. **Completion:** no freeform editor or identity-picker schema remains; `Adjust terms` replaced by the per-court flow; suite green; no dead code; OQ-4 re-homing verified. **Tests:** absence tests; concession-authoring-routes-to-guided-flow; incoming-offer-routes-correctly.
- **GT-Slice-5 — Voice.** Talleyrand suggests demands in-character; affected named diplomats react (REFRONT-V family). **Completion:** suggestion + reaction copy resolves to named diplomats (chancery fallback), no anonymous beats; `DIPLOMAT_VOICE_BIBLE.md` updated. **Tests:** voice resolution pins.

---

## 10. Non-goals / boundaries

- **Slice G AI-ally settlement agency** stays separate and later (unchanged by this spec).
- **Tier-1 baseline and Tier-2 dials** are reused, not redesigned.
- **The per-court ratification gate** (re-front §11.4) is unchanged.
- **Mechanics are unchanged** — this is an authoring-surface redesign; `validate_settlement_terms`, scoring, and apply paths are reused as-is.

---

## 11. Status tracking

On approval, add a `Settlement Guided Terms` row to `docs/STATUS.md` Active Settlement Gate with per-slice landing/audit lines, and a Design Gate entry in `CLAUDE.md`. Until approved, this doc is the sole owner of the redesign and **no code lands**.
