# Settlement Guided Terms Spec

**Version:** v0.2 (audit fold)
**Date:** 2026-05-31 (v0.1 DRAFT) → 2026-06-10 (v0.2 — Run #1 audit fold)
**Status:** ⛔ **DESIGN GATE — NEEDS USER APPROVAL — DO NOT CODE.** v0.2 folds the Run #1 design-gate audit (`docs/SETTLEMENT_GUIDED_TERMS_AUDIT.md` — GO-with-changes; 0 CRITICAL / 9 MAJOR / 6 MINOR, all folded) plus the four mandatory pre-flight amendments **GT-A1..4** (`docs/SETTLEMENT_GATE4_PREFLIGHT_AUDIT.md` §7). **One decision changed by the fold and needs explicit user confirmation at approval: D4 (mixed-direction rows — §2).** Everything else is fold work on the approved direction.
**Sequencing (updated June 9–10, 2026):** this design gate is the **immediate next settlement action**; the GT-A1..4 amendments and the audit findings are folded (this version). The Gate 4 manual smoke is **re-sequenced to run ONCE at the END of the settlement queue**, after this spec's slices land — it smokes the guided surface, not the editor it replaces. (v0.1's "tackle after the Gate 4 smoke completes" predated the June 9 re-sequencing and is superseded.)
**Supersedes:** the **Tier-3 freeform clause editor** of `SETTLEMENT_CONVERSATIONAL_REFRONT_SPEC.md` (the `settlement_editor_popup` + from/to identity pickers). It does **not** touch Tier-1 (Talleyrand baseline) or Tier-2 (intent dials) — those stay and become the foundation this builds on.
**Audit:** `docs/SETTLEMENT_GUIDED_TERMS_AUDIT.md` (Run #1, June 9–10, 2026, against live master `6edeb6f` post-PF-1/2/3, with five executed fixture probes). Per DC-6 the doc-audit budget is MAX 2 runs; run #2 is a targeted fold-verification of this v0.2 diff only.

---

## 1. Why replace the freeform editor

The Tier-3 "Adjust terms" editor is a blank, freeform clause assembler. Four problems, in order of player cost:

1. **The editor is blind while you author.** Tier-3 has **no live acceptance** — you assemble clauses, Submit, and discover the verdict at REVIEW. Every other settlement surface already re-scores live (the Tier-2 dials re-draft + re-score per court on every click); the deep tier where you do the most precise work is the only place you fly blind. **The guided rows re-score the affected court on every Add / Remove / magnitude change — live per-court feedback while authoring is the single biggest player win in this redesign.**
2. **It defaults to `France` / `France` for everything.** Both ends of every clause default to the first nation in the list (the player). The most natural first action — clicking through — authors self-referential nonsense (France vassalizes France) that's only caught at Submit.
3. **It's vague.** A blank clause table gives no signal about what a *good* or even *valid* demand looks like. You assemble in the dark and find out at Submit.
4. **It diverges from every other peace surface in the game.** Normal two-way peace deals never use identity pickers. The bilateral `terms_guidance` flow ([backend/commands/diplomatic_executor.py:3858-3888](../backend/commands/diplomatic_executor.py)) is a **guided, Talleyrand-led** sequence: Talleyrand *suggests* a concrete, valid region ("I suggest Silesia — [reason]"), you `Offer this` / `Not this one` / `That's enough`, then it walks you through gold and Action Points. **Direction is implied** by whether you're winning or losing (`war_score`/relation) — you never pick "who cedes to whom," so a self-referential clause is structurally impossible.

The two transport/validation bugs found alongside this (authored terms dropped at the `/command` Pydantic boundary; submit-time validation errors silent) were fixed at commit `067e431`. This spec addresses the deeper finding: **the editor's authoring *model* is wrong.** The fix is to make settlement authoring work like the rest of the game — guided, suggestion-driven, direction-implied — generalized to settlement's multi-party shape, with live per-court re-scoring as the headline.

---

## 2. Design decisions (this gate)

| ID | Decision | Source |
|----|----------|--------|
| **D1** | **Replace the freeform editor entirely.** Guided per-court demands become the *only* term-shaping surface beyond Tier-1/Tier-2. The `settlement_editor_popup` + identity-picker schema are retired. | User, 2026-05-31 |
| **D2** | **Fold authoring into the existing per-court rows** on the PROPOSE surface. Each covered-enemy court row gains an inline, guided "demand" affordance — no separate screen. | User-deferred → audit-endorsed (Run #1 lens A) |
| **D3** | **Cover all *valid* clause types via the per-court model; direction sets the DEFAULTS, ORDERING, and COPY of each row's menu — not the verb set** (amended by audit GT-R1-1; see D4). Same-side enemy↔enemy transfers are already invalid (validator V3 `clause_side_mismatch`), so every valid transfer straddles *your side ↔ one enemy court* — identities never need picking; each offered option is fully formed with its direction fixed per option. | This spec §3–§4; amended 2026-06-10 |
| **D4** | **Mixed-direction rows: every court row exposes BOTH option groups** — demands (court → France) *and* offers/sweeteners (France → court) — with the court's war-score direction choosing which group leads and is pre-expanded. **⚠ Changed by the audit fold — confirm at approval.** Probe-verified rationale: a France-pays sweetener on a demand-direction court is legal, validates clean, and is mechanically rewarded by the live `concession_credit` component (probe: Prussia 35 → 43); the re-front's own §17 worked example performs exactly this move in Tier 3, and with Tier 3 retired no other surface can author it (the focused-Ease dial seed fires only on a court with no live clauses). A one-direction-per-row model would silently delete that agency. | Audit GT-R1-1, 2026-06-10 (recommendation applied; **user confirms at approval**) |
| **D5** | **Press-past-zero / direction-flip authoring stays** (DC-4): the player may deliberately author a demand on a court that is beating France — via the row's demand group (D4) or the existing dial seed. The scorer prices it; Talleyrand voices it (the DC-4 guard line, owned by GT-Slice-V). The dial seed's behavior is unchanged. | Audit GT-R1-8 + pre-flight DC-4, 2026-06-10 |

**Why D2 (per-court rows, not a separate wizard):** the per-court rows already exist (Tier-2: per-court acceptance band, direction, top blocker, named-diplomat voice, Press/Ease + holdout Ease/Drop). They are already the multi-party generalization of the bilateral single-target wizard. Folding demand authoring into them keeps everything on one screen with live re-scoring, and avoids a modal-on-modal. The bilateral flow is sequential only because it has one target; settlement has many, so a *row per court* is the right shape.

**Why D3+D4 (all valid types, direction-led but not direction-locked):** in the common case you are dictating as the winner and every value transfer goes *enemy court → you*; dependency clauses make the *enemy court* the subject and *you* the lord/imposer; liberation is an action *against* the overlord court. Direction therefore picks the menu's lead group and the pre-filled defaults. But the validator (V3) constrains *sides*, not *per-court direction* — a package may legally both demand Silesia from Prussia and sweeten Prussia with gold, and the scorer rewards the sweetener (`calculate_concession_credit`, `settlement_scoring.py:1273`). The per-court row presentation already renders the mixed read (`_court_direction_summary`, `settlement_preview.py:2892` — "Demanded: X; Conceded: Y"). So the row offers both groups; direction means you rarely need the trailing one.

---

## 3. The guided flow (concrete)

### 3.1 Surface

The PROPOSE surface (Slice 1/2, already shipped) is unchanged in structure:

- **Talleyrand framing line** (voice).
- **Treasury line** (new — §3.4): one visible allocation line for the proposer's gold across the whole table.
- **Per-court table** — one row per covered enemy court.
- **Whole-table rail** — Harsher / More generous dials, coverage add/drop, `Submit for Review`, `Back Out`.

This spec **adds demand authoring inside each court row**:

- The row shows the **current demands and offers on that court** as plain lines (e.g. "Cede Silesia", "300 gold", "France pays 200 gold") each with a magnitude control where relevant and a `Remove`. Line copy reuses the cleanup-spec direction-tag vocabulary (`Demanded` / `Conceded` / `Mutual`, cleanup `:602`).
- The row gains an **`Add demand`** affordance. It opens a **compact inline expansion** (not a new screen) listing Talleyrand-suggested, valid, *fully-formed* options for that court, **each with a one-line `reason_display`** (the bilateral flow's signature beat — "I suggest Silesia — {reason}", `diplomatic_executor.py:3900`; concede-side reasons via `_format_concession_reasoning`, `settlement_preview.py:1567`). The expansion lists the **direction-led group first** (D4):
  - `Take [Silesia ▾] from Prussia` — region pre-picked (best border candidate), dropdown lists only regions Prussia controls (demand-side selector — §7).
  - `Demand [300] gold from Prussia` — amount pre-filled to an affordable default **for Prussia as payer**, bounded by the cross-table rules (§3.4); magnitude adjustable.
  - `Demand [50]/turn for [3] turns from Prussia` — recurring gold, pre-fill bounded by **Prussia's capacity** (gold + income × turns — §4).
  - `Vassalize Prussia` — shown **only if** `evaluate_vassalage_eligibility` passes (direction, war state, not-already-vassal, power cap — `settlement_preview.py:1716`).
  - `Subjugate Prussia` — shown only if `evaluate_subjugation_eligibility` (`:1671`) passes.
  - `Force Prussia into alliance` `[☐ Continental System]` — the existing optional `includes_continental_system` clause field (`settlement_scoring.py:98`), no new mechanic.
  - `Free Prussia's vassal [X]` — shown **only if** Prussia currently holds a vassal; liberator is France (OQ-3).
  - **Offer group (trailing, collapsed by default on a demand court — D4):** `Offer [N] gold to Prussia` / `Offer [region ▾] to Prussia` — France pays/cedes; the sweetener lever (`concession_credit`).
- Adding, removing, or adjusting a demand **mutates the staged draft and re-scores live** — the court's acceptance band updates immediately — exactly like the Tier-2 dials already do (`action_params` over `/respond_to_diplomatic_dialogue`). The mutation rides the same restage helper the dials use (`_restage_settlement_after_redraw`, `settlement_preview.py:3409` — implementers must reuse it, not hand-roll staging), which already validates, persists the PF-2 scoped draft, and re-attaches with `error_display` on failure.
- **Direction is always implied per option**: every offered option is fully formed with its from/to fixed. No identity pickers exist. `France`/`France` is structurally impossible.
- **Options are valid-by-construction at TABLE scope** (§3.4): eligibility-gated options simply don't appear when invalid, and gold/region suggestions are computed against the *remaining* table budget and the *unpromised* region set — never row-locally. The validator (V1–V5) remains the authority as defense-in-depth at the restage choke point; per DC-1, valid-by-construction is a property of the draft **store**, not of the author.
- **At the clause cap** (`MAX_SETTLEMENT_CLAUSE_COUNT = 8`, `settlement_scoring.py:148`): `Add demand` renders disabled with a humanized reason ("The settlement already carries eight clauses, Sire — remove one before adding another."), mirroring the Slice-2 focused-seed fold (`settlement_preview.py:3204-3215`) — it never authors an over-cap draft for the restage validator to bounce.

### 3.2 Losing / concession direction

If France is **losing** a given court (that court's `direct_score < -DIRECT_SCORE_DIRECTION_MARGIN`, the concede direction from `compute_settlement_baseline`), that court's row **leads with the offer group**: `Offer [region ▾] to Prussia`, `Offer [N] gold to Prussia` — France is the conceder. Region candidates come from the settlement concede-side selector `_concession_baseline_select_transferable_region` (`settlement_preview.py:1475`), which already takes the PF-1 `excluded_regions` param — **not** the bilateral `rank_cession_candidates` (that ranks the player's regions for the bilateral flow and has no cross-table exclusion). Gold offers are bounded by the §3.4 treasury line. The demand group trails, collapsed (D4/D5 — pressing a winning court is legal; Talleyrand voices the caution). The per-court direction is already computed; it selects which group leads, the candidate sources, and the copy. This is the home for the **losing-side concession authoring** the Gate 4 smoke exercises (it currently routes through the editor; it moves here).

### 3.3 Per-court row states (the four live directions)

The direction enum is four-valued (`_court_direction_from_selection`, `settlement_preview.py:2872-2889`); the row contract covers all four:

| `direction` | Row authoring state |
| --- | --- |
| `demand` (France leads) | Both groups; demand group leads/pre-expanded (§3.1) |
| `concede` (France pressured) | Both groups; offer group leads/pre-expanded (§3.2) |
| `peace` (dead-band) | Both groups, neither pre-expanded; baseline slice is the `{"type":"peace"}` neutral floor. This is where the re-front §17 "sweeten the wobbler" move lives. |
| `hard_stop` (no cross-side pair — `select_direct_score` returns `None`) | **`Add demand` absent/disabled** with `disabled_reason_display` — no clause can move a `total=null` court (the scorer hard-stops it; probe-verified: the row renders `total=null`, no terms, `carries=false`). The row exposes **Drop** only; voice = the existing `settlement_multi_court_court_hard_stop` family (Voice Bible §16.1a). |

### 3.4 One treasury, many courts (GT-A1 — shared budget as a first-class row concept)

Multiple courts can take France's gold; the treasury is ONE pool. Probe-verified at the gate: on the real `settlement_losing` fixture (France gold 1,500), two *individually affordable* 1,000g offers validate alone but the pair is rejected only by the table-level `gold_payment_budget_conflict` (`_check_gold_payment_budget_conflict`, `settlement_preview.py:164-252`). Without a visible budget the guided flow re-creates D1's over-commit with the player driving — discovering it as rejection spam at the choke point.

- **The PROPOSE payload gains a `treasury_line` block:** `{"treasury": int, "committed": int, "reserve": int, "remaining": int}` (all `int()` — Golden Rule #2), computed from the proposer leader's gold, the staged package's France-paid gold clauses, and `CONCESSION_BASELINE_TREASURY_RESERVE`. Rendered as one allocation line above the rows: `"1,500g: Britain 750 / Prussia 750 / reserve 0 / remaining 0"`.
- **Suggestion generation is table-scoped:** gold-offer defaults cap at `remaining`; region-offer candidates exclude regions already promised elsewhere in the staged package (the same `promised_regions` exclusion PF-1 threads through the baseline loop, `settlement_preview.py:2576/2625-2627`); demand-side suggestions are likewise checked against the assembled table (V1) before being offered.
- **The restage validator + `error_display` re-attach is the backstop, not the UX** — it exists and renders (`:3446-3464`; `main.gd:981-984`), but a player following the suggestions should never hit it.

### 3.5 Dial composition rule (Tier-2 dials × player-authored lines)

The dials and the guided rows write the same staged draft, so composition must be defined (probe-verified hazard: under the live `_redial_settlement_terms` semantics, ONE whole-table `More generous` click deletes a hand-authored territory demand and shrinks hand-set gold). **Rule:** clauses authored via `Add demand` are tagged `"authored_by": "player"` in the staged draft (new serializable clause field — serialization rule applies, `to_dict`/`from_dict` + `tests/test_serialization_enforcement.py`). **Dials never silently DROP a player-authored clause:** gold shrinks toward (not past) the dial step floor; player-authored territory/identity clauses are skipped by the dial sweep, with the skip noted in the response message ("Your demand for Silesia stands, Sire."). Talleyrand-suggested (baseline/seed) clauses keep today's full dial semantics. Per-line `Remove` is the player's deletion verb; the dial is a tuning verb. (`test_whole_table_generous_does_not_silently_delete_player_authored_demand`, GT-Slice-1.)

### 3.6 Worked example (the smoke scenario: France vs Britain + Prussia, France winning)

1. Open Settlement → PROPOSE. Talleyrand proposes the baseline; the treasury line reads `"5,000g: committed 0 / remaining 4,500"`; the table shows **Britain** (near-acceptable) and **Prussia** (holdout).
2. On **Prussia's** row, click `Add demand` → inline options, each with a reason line. Pick `Take [Silesia ▾] from Prussia`. The row gains "Cede Silesia"; Prussia's band drops and re-scores instantly.
3. Decide it's too harsh — click `Remove` on "Cede Silesia". It's gone; band recovers. (No merge, no re-add — the draft *is* the live state.)
4. Prussia still wavers. Open the trailing **Offer** group and add `Offer [200] gold to Prussia` — the sweetener. Prussia re-scores up (`concession_credit`); the treasury line updates to `committed 200`.
5. On **Britain's** row, `Add demand` → `Demand [300] gold from Britain`. Bump magnitude to 400 with the row control; re-scores live.
6. Use whole-table `More generous` once to ease both courts toward carry — the player-authored lines survive per §3.5; suggested lines ease.
7. `Submit for Review` → REVIEW → ratify (per-court gate, unchanged).

No identity pickers, no France/France, no "submit a blob then reconcile."

---

## 4. Clause → per-court option mapping

Direction is fixed **per option**; nothing below exposes an identity picker. Each row offers the demand group and the offer group (D4); direction chooses which leads (§3.3).

| Clause type | Demand option (court → France) | Offer option (France → court) | Valid-by-construction gate |
|---|---|---|---|
| `peace` | implicit on every covered court (the shared package peace) | — | always |
| `territory_cede` | Take [region] from `<court>` | Offer [region] to `<court>` | demand: region ∈ court's controlled regions (demand-side selector, §7); offer: region from `_concession_baseline_select_transferable_region:1475` with the §3.4 `promised_regions` exclusion; both checked against V1 across the table |
| `gold_indemnity` | Demand [N] gold from `<court>` | Offer [N] gold to `<court>` | demand: default ≤ court treasury − reserve; offer: default ≤ §3.4 `remaining`; solvency validated at restage |
| `gold_per_turn` | Demand [N]/turn × [T] from `<court>` | Offer [N]/turn × [T] to `<court>` | **capacity rule, not just bounds:** pre-fill ≤ payer capacity = `current_gold + max(0, net_income) × turns`, net of existing recurring obligations (`_check_gold_payment_budget_conflict:164-252`); payer = the court (demand) or France (offer, joins §3.4); `GOLD_PER_TURN_*` floor/turn bounds apply; one income estimate per court per preview (the estimator scans regions, `:140-161` — compute once, reuse across options) |
| `vassalage` | Vassalize `<court>` | (n/a — France self-vassalage is not a player verb) | `evaluate_vassalage_eligibility:1716` |
| `subjugation` | Subjugate `<court>` | (n/a) | `evaluate_subjugation_eligibility:1671` |
| `forced_alliance` | Force `<court>` into alliance `[☐ Continental System]` | (n/a — a losing player cannot force the victor; cleanup `:616`) | court is covered enemy; not already equivalently allied |
| `liberation` | Free `<court>`'s vassal [X] | (n/a) | `<court>` holds a vassal; `evaluate_liberation_eligibility:1736`; liberator = France (OQ-3) |

**No exotic free-direction case remains at the SIDE level.** A transfer between two enemy courts (both on the accepting side) already fails validator V3 (`clause_side_mismatch`), so it was never a valid clause — its absence from the guided flow is *correct*, not a deferral. (Per-court *mixed direction* — demand AND offer touching one court — is valid, rewarded, and covered by D4; do not confuse the two.)

---

## 5. What is removed / retargeted (explicit, per Golden Rule #9)

These are **removed or re-pointed**, not deferred — each has a landing slice (§9). The inventory below is the complete set of editor producers/consumers/copy sites verified live at `6edeb6f` (audit GT-R1-4):

| Item | Live cite | Disposition (lands in GT-Slice-4 unless noted) |
| --- | --- | --- |
| `settlement_editor_popup.tscn` / `settlement_editor_popup.gd` | Godot scene/script (CanvasLayer 112) | **Removed.** |
| Identity-picker half of the Tier-3 schema (`_clause_fields_for_review`, `_nation_control_options`, `_side_partitioned_options`, `clause_control_schema` / `available_clause_types` payload) | `settlement_preview.py:4517/:4402/:4474/:4705` | **Removed.** The **eligibility + candidate-generation** helpers (`evaluate_*_eligibility`, the selectors in §7, the affordable-indemnity logic) are **kept and reused** for the guided suggestions. Retiring the schema build also retires the `_region_control_options:4451` all-regions scan — **REFRONT-7 closes as moot** (its test is deleted or re-pointed at the suggestion source). |
| Editor Submit-for-Review structured `propose_common_peace` POST path + the `settlement_terms` / `selected_target_nation` / `covered_enemy_participants` fields on `CommandRequest` (added at `067e431`) | `main.py:777-779` | **Removed after a verify-dead pass** (no non-editor producer exists; `target_nation` at `main.py:768` predates them and stays — the PF-2 reopen path uses it). |
| Same-war additive merge of editor-submitted terms | the ONLY `merge_same_war_settlement_drafts` call site, `settlement_preview.py:5777` (inside `stage_settlement_confirm`'s editor-submit path) | **Removed with the submit path** (§6). The merge helper itself is deleted if no caller remains. |
| `DWL-SET-SC5R-3` inline merge-conflict controls (Discard new / Replace active) | `settlement_editor_popup.gd` | **Removed** — no submit-blob means no merge conflict to resolve. |
| `open_editor_on_mount` producer: `apply_concession_baseline_replacement` | `settlement_preview.py:7409-7414` | **Re-pointed:** stages the replacement and re-stages **guided PROPOSE** (no editor mount). |
| `open_editor_on_mount` producer: `re_author_with_concessions` (blocked-REVIEW rail, normative in cleanup v0.32) | `settlement_preview.py:8430-8431` | **Re-pointed:** the concession baseline re-stages **guided PROPOSE** seeded from the baseline (the rail action survives; only its destination changes). Its legacy-store write (`:8404-8408`) is removed with CH-3. |
| `open_editor_on_mount` producer: incoming-offer `request_settlement_revision` (counter-authoring) | `settlement_preview.py:9948-9957` | **Re-pointed:** counter-authoring lands on **guided PROPOSE seeded from the offered terms** (`counter_to_offer_id` / `counter_seed_terms` provenance preserved). Resolves OQ-4(b). |
| Godot consumers: client-side `adjust_terms` branch, `open_editor_on_mount` routing, `_maybe_remount_settlement_editor_after_error` | `main.gd:41-44` + routing | **Removed/re-pointed:** `Adjust terms` disappears as a rail verb (the rows ARE the deep tier); error remounts target the PROPOSE popup path (which already renders `error_display`). |
| Cleanup-spec REVIEW row `Revise Terms … only when it returns the staged package to an edit-capable route` | `SETTLEMENT_UI_CLEANUP_SPEC.md:570` | **Re-pointed (doc edit, GT-Slice-4):** "edit-capable route" = the guided PROPOSE surface. |
| PF-1 budget-bound carry hint "use **'Adjust terms'** to pay in land instead" | `settlement_preview.py:3367-3370` | **Re-pointed:** "add a territory offer on the court's row." |
| Voice Bible `settlement_incoming_offer_request_revision_talleyrand` ("I shall open the offered terms … for our own hand") | Voice Bible §16.1 | **Copy retarget** (GT-Slice-V): same beat, lands on the guided table. |

---

## 6. Why the merge/replace problem dissolves

The merge-vs-replace tension only exists because the editor is a **separate blob you assemble and then submit** — at submit time the backend has to reconcile your blob against the previously-staged draft (today: an additive `merge_same_war_settlement_drafts` that re-adds clauses you removed; a "replace" would discard concurrent state).

In the guided model there is **no submit blob**. Every `Add demand` / `Remove` / magnitude change is an `action_params` mutation against the staged `settlement_confirm` (the Tier-2 dial transport, already shipped), and the **staged draft is the single source of truth**, re-scored on each action. `Submit for Review` is purely a PROPOSE→REVIEW state transition for ratification — it carries no terms to reconcile (and the PF-1 submit-arm validation, `settlement_preview.py:7901-7931`, still runs on the staged draft). So removals stick, edits apply, and there is nothing to merge or replace.

**Scope honesty (audit GT-R1-4):** this retires the merge **call site only** (`:5777`). The blocked-REVIEW **replacement-stage preset family** (`_stage_replacement_settlement_terms:7298` + the `author_*` arms) is a different blob path that survives the editor's death — **D7's latent orphan class is NOT deleted by this spec**; CH-5 (the one-structural-invariant wrapper) remains D7's cure and is the natural companion slice.

---

## 7. Backend reuse map

| Need | Reuse (verified live at `6edeb6f`) |
|---|---|
| Per-court direction (demand vs offer vs peace floor vs hard-stop) | `compute_settlement_baseline:2480` + `_court_direction_from_selection:2872` (`settlement_preview.py`) |
| Region candidates — demand direction (court cedes) | `_demand_baseline_select_region` (`settlement_preview.py:2222`) / `generate_suggested_terms`' demand stage (`diplomatic_templates.py:2023`) |
| Region candidates — offer direction (France cedes) | `_concession_baseline_select_transferable_region` (`settlement_preview.py:1475` — already takes PF-1's `excluded_regions`). *Not* the bilateral `rank_cession_candidates` (`diplomatic_templates.py:2422`; its executor call site `diplomatic_executor.py:3849` ranks the player's regions for the bilateral flow and has no cross-table exclusion — v0.1 cited it in the wrong file and for the wrong direction). |
| Affordable indemnity defaults | the demand/concede gold sizing in `_demand_terms_for_court:2779` / `_concession_terms_for_court:2682`, bounded by §3.4 |
| Suggestion reasons | `_format_concession_reasoning:1567`; bilateral ranked-candidate reasons (`diplomatic_executor.py:3895-3900`); `NATION_DESIRE_PROFILES` rationale |
| Dependency/liberation eligibility gates | `evaluate_vassalage_eligibility:1716`, `evaluate_subjugation_eligibility:1671`, `evaluate_liberation_eligibility:1736` |
| Live per-court re-score | `compute_per_court_acceptance:2941` → `calculate_common_peace_acceptance` (one shared score pass + injected `balance_projection`, `:3012-3020`) |
| Mutation staging / draft persistence / failure re-attach | `_restage_settlement_after_redraw:3409` (validates, persists the PF-2 scoped store, returns `error_display` on failure) — **the new verbs MUST route through it** |
| Per-court-row action transport | `action_params` on `/respond_to_diplomatic_dialogue` (Slice 2) |
| Authority on final validity | `validate_settlement_terms:3613` V1–V5 (unchanged, defense-in-depth) |

**New-verb wiring + failure contract (audit GT-R1-5 — name every point, the D2/D3 lesson):** the three new verbs `settlement_demand_add` / `settlement_demand_remove` / `settlement_demand_set_magnitude` must each join:

1. the settlement dialogue dispatch tuple (`settlement_preview.py:7798-7804`) **and its re-attach net** (`:7820-7831` — a failed/blocked action re-attaches the mounted dialogue + `error_display`, never neither; if CH-5's wrapper lands first, join that instead and say so in the slice notes);
2. the executor's `_SETTLEMENT_TIER2_ACTION_IDS` frozenset + dispatch list (`diplomatic_executor.py:21-29`, `:2923`);
3. the Godot whitelist `SETTLEMENT_DIALOGUE_ACTIONS` (`main.gd:35-57`);
4. **guards:** player-only (`caller_kind == SETTLEMENT_EDITOR_CALLER_KIND`, the Slice-G boundary) AND `dialogue_mode == "PROPOSE"`-only (server-side — REVIEW is a frozen staged-decision surface; today's dials rely on absent buttons, the new verbs guard explicitly).

New work remains thin: the three demand-mutation verbs (analogous to the existing `settlement_dial_*` handlers, riding the same restage helper) plus the per-court **suggestion payload** (§9 GT-Slice-2) and the **treasury line** (§3.4).

---

## 8. Resolved questions

- **OQ-1 — region choice UX → LOCKED: dropdown.** For a court with several cedeable regions, the inline expansion offers a dropdown of valid regions (with the top pick's `reason_display`), not the bilateral one-at-a-time `suggest → skip` loop — it's a panel, not a wizard, so showing the valid set at once is lighter.
- **OQ-2 — keep whole-table dials? → LOCKED: keep, with the §3.5 composition rule.** Harsher / More-generous (whole-table + focused) remain the fast "tune everything" pass; they compose with explicit authoring under the stated rule (dials tune suggested lines; they never silently delete player-authored ones).
- **OQ-3 — liberation liberator → LOCKED: France only.** A non-France liberator is an explicit out-of-scope cut (no owner row needed — it is not a player-facing promise; the clause schema supports it if a future spec wants it).
- **OQ-4 — incoming offers & concession authoring → RESOLVED (audit trace, 2026-06-10).** The three editor mount points are enumerated in §5 with dispositions: (a) **losing-side concession authoring** re-homes onto the guided per-court flow (§3.2); (b) **incoming-offer counter-authoring** (`request_settlement_revision`, `settlement_preview.py:9948-9957`) re-points to guided PROPOSE seeded from the offered terms; (c) the **blocked-REVIEW re-author/preset arms** (`re_author_with_concessions:8430`, `apply_concession_baseline_replacement:7409`) re-stage guided PROPOSE instead of mounting EDIT. Verified before GT-Slice-4 removes the editor (absence + routing tests, §9).
- **OQ-5 — REFRONT-9 fold → LOCKED: yes (GT-A4).** The focused per-court component breakdown (re-front spec §14 row REFRONT-9) lands as the **expanded state of a per-court row** in GT-Slice-3; the focus trigger transport is the existing presentation-only `settlement_focus_court` handler (`settlement_preview.py:7619-7648`); the test `test_tier3_focused_court_expands_full_component_breakdown` re-homes to the row expansion. The re-front §14 REFRONT-9 row's landing pointer is updated to say so.
- **OQ-6 — losing-multi-court allocation (NEW, GT-A2) → LOCKED: deterministic cheapest-signature rule.** When the treasury cannot satisfy every concede-direction holdout (the live PF-1 detector `_settlement_budget_bound_constraint:3285` is the trigger), Talleyrand's recommendation is computed, never vibes (Golden Rule #6): **rank concede-direction holdouts by `gap_to_threshold` ascending (cheapest signature first); recommend concentrating the remaining budget on the cheapest court(s) whose gaps are coverable, and name the most expensive holdout as the court to set aside (Drop)** — tie-break by larger `abs(direct_score)`, then lexicographic court name. Advice only; the player clicks. In-character defense: Pressburg logic — you buy the peace you can afford and let the dearest enemy fight on; Britain is the archetype. Voice extends `settlement_budget_bound_constraint_talleyrand` (Voice Bible §16.1a). Test: `test_budget_bound_recommendation_ranks_cheapest_signature_first_deterministically` (GT-Slice-2).

---

## 9. Implementation slices (each: owner / landing / completion / tests — Golden Rule #9)

> All slices are **gated on user approval of this spec (v0.2)**. The Gate 4 manual smoke runs ONCE at the END of the settlement queue, after these slices (June 9 re-sequencing). Voice lands **before or with GT-Slice-3** (the REFRONT-V lesson — copy never lands ahead of its resolver rule).

- **GT-Slice-1 — Per-court demand mutation (backend).** New dialogue verbs `settlement_demand_add` / `settlement_demand_remove` / `settlement_demand_set_magnitude`, resolved via `action_params` against the staged `settlement_confirm`; each applies the option's fixed direction, mutates the draft **through `_restage_settlement_after_redraw`**, and re-scores live. Includes the §3.5 `authored_by` clause tag (+ serialization), the §3.4 treasury-line computation, and the full §7 wiring/guards. **Completion:** a player can add/remove/adjust a demand or offer per court and see live per-court re-scoring + the treasury line; direction never inverts identity; both guards hold; every failure re-attaches with `error_display`; validator stays authority. **Tests:** add-territory-appears-and-rescores; remove-sticks; magnitude-adjust; eligibility-gated vassalize rejected when ineligible; losing court leads with offers; `test_demand_direction_row_can_author_proposer_paid_sweetener_and_concession_credit_applies` (D4); `test_whole_table_generous_does_not_silently_delete_player_authored_demand` (§3.5); `test_guided_gold_suggestion_caps_at_remaining_table_budget` + `test_guided_region_suggestion_excludes_already_promised_regions` (§3.4); `test_add_demand_disabled_at_clause_cap_with_reason` (§3.1); `test_demand_verbs_rejected_in_review_mode_with_error_display` + `test_demand_verb_failure_reattaches_dialogue_never_silent` (§7 guards/CH-5); `test_propose_and_demand_routes_reject_non_player_caller_kind` (Slice-G boundary); **`test_settlement_matrix_demand_verbs_succeed_or_reattach_with_error_display`** — a parametrized extension of the standing PF-3 harness (`tests/test_settlement_baseline_scenario_matrix.py`) driving every new verb across the direction × coverage × treasury cells.
- **GT-Slice-2 — Per-court suggestion payload.** Each per-court row carries `demand_suggestions[]` (valid, fully-formed, direction-correct options for that court, **table-scoped** per §3.4, each with `reason_display`) + `current_demands[]` with magnitude metadata + the `treasury_line`. Includes the OQ-6 budget-bound recommendation. **Completion:** PROPOSE rows expose suggestions + current demands + reasons; suggestions are valid at table scope; all numerics `int()`. **Tests:** suggestions eligibility-gated; no identity fields exposed; France-self impossible; losing-court suggestions lead with offers; hard-stop row exposes no authoring (`test_hard_stop_court_row_disables_authoring_with_reason`, §3.3); dead-band row offers both groups (`test_dead_band_court_offers_both_directions`); `test_demand_suggestions_are_deterministic_same_world` (Golden Rule #6); `test_suggestion_payload_numerics_are_int` (Golden Rule #2); `test_gold_per_turn_prefill_respects_payer_capacity` (§4); OQ-6 determinism test.
- **GT-Slice-V — Voice (lands before or with GT-Slice-3 — re-ordered per audit GT-R1-12).** Talleyrand suggests demands in-character (`reason_display` register); affected named diplomats react (extends the §16.1a families); the **DC-4 guard line** lands here verbatim from the pre-flight audit ("They are not the ones suing for peace, Sire — but as you wish."), fired whenever a demand is authored/seeded on a concede-direction court (D5); the §5 incoming-offer revision copy retarget. **Completion:** suggestion + reaction copy resolves to named diplomats (chancery fallback), no anonymous beats, SC-32 D5 boundary held; `DIPLOMAT_VOICE_BIBLE.md` updated. **Tests:** voice resolution pins; `test_demand_on_concede_direction_court_fires_talleyrand_caution_voice`; the existing D5 copy test extends to the new lines.
- **GT-Slice-3 — Godot per-court demand UI.** `proposal_confirm_popup.gd` renders the inline `Add demand` expansion (reason lines, magnitude controls, both groups per §3.3), the treasury line, and per-row `Remove`, routed through `send_dialogue_response_with_params`. Folds **REFRONT-9** (focused breakdown = expanded row, per OQ-5/GT-A4). Owns **UX-2** (a `dialogue_mode` render branch — REVIEW reads as a staged-decision surface: terms frozen, authoring affordances absent, blockers promoted) and **UX-5** (a scroll container around the per-court table with the expansion designed to a row-height budget) — both verified absent at `6edeb6f`. **Completion:** in-game per-court authoring on one screen; REVIEW visually distinct; Godot 4.4.1 parse exit 0. **Tests:** Godot source pins + parse harness; REFRONT-9 breakdown test (`test_tier3_focused_court_expands_full_component_breakdown`, re-homed); UX-2/UX-5 source pins; **one HTTP-boundary test posting the exact Godot `action_params` shape for `settlement_demand_add` through `/respond_to_diplomatic_dialogue`** (the D4-lesson test — executor-direct shapes do not count).
- **GT-Slice-4 — Retire the freeform editor.** Execute the full §5 inventory (removals + re-points); repurpose retained candidate/eligibility helpers; remove the dead `CommandRequest` settlement fields after the verify-dead pass; close REFRONT-7 as moot. **Editor-test disposition (enumerated):** in `tests/test_settlement_sc5r2_godot_editor.py` and adjacent files — *migrate* the draft-lifecycle/round-trip/suspend-reopen tests onto the guided surface; *delete* the picker-schema and editor-widget pins; *keep* backend validity-contract tests that don't reference the editor. **UX-3 closes as moot with the editor** (pre-flight audit §8). **Completion:** no freeform editor or identity-picker schema remains; every §5 re-point routes correctly (absence + routing tests); suite green; no dead code. **Tests:** absence tests; concession-authoring-routes-to-guided-flow; incoming-offer-counter-routes-to-guided-propose; re-author-arms-stage-guided-propose-not-editor; carry-hint-copy-points-at-row-offer.

---

## 10. Non-goals / boundaries

- **Slice G AI-ally settlement agency** stays separate and later (unchanged by this spec; the new verbs are player-only).
- **Tier-1 baseline and Tier-2 dials** are reused, not redesigned (§3.5 adds only the composition rule + the `authored_by` tag).
- **The per-court ratification gate** (re-front §11.4) is unchanged.
- **Mechanics are unchanged** — this is an authoring-surface redesign; `validate_settlement_terms`, scoring, and apply paths are reused as-is. (`includes_continental_system` is an existing clause field, not a new mechanic.)
- **Period levers deliberately NOT exposed** (audit lens B — each exclusion named, none orphaned):
  - *Army-limitation clauses* (the 1808 Convention of Paris capped Prussia at 42,000 men) — no clause type exists; adding one is a mechanics change outside this gate. Candidate future clause type via its own design gate.
  - *Occupation-until-paid* (Prussia 1807–08) — approximated by `gold_per_turn`; no separate mechanic.
  - *Dynastic marriage* — already ranked flavor/cut (pre-flight DW-4).
  - *Recognition-of-title clauses* (Joseph in Naples, the Confederation) — partially expressible via vassalage/liberation; no separate clause.
  - *Maritime/colonial returns* (Amiens-style) — off-map; out of scope.
- **CH-5** (the one-structural-invariant wrapper) is the cure for D7's surviving orphan class (§6) — owned by the pre-flight audit's code-health ledger, recommended as the companion slice to GT-Slice-1.

---

## 11. Status tracking

On approval, add a `Settlement Guided Terms` row to `docs/STATUS.md` Active Settlement Gate with per-slice landing/audit lines, and update the Design Gate entry in `CLAUDE.md`. Until approved, this doc is the sole owner of the redesign and **no code lands**.

### Changelog

- **v0.2 (2026-06-10)** — Run #1 audit fold (`docs/SETTLEMENT_GUIDED_TERMS_AUDIT.md`, GO-with-changes, 9 MAJOR + 6 MINOR, all folded) + the four pre-flight amendments: **GT-A1** shared treasury as a first-class row concept (§3.4); **GT-A2** losing-multi-court allocation locked as OQ-6's deterministic cheapest-signature rule; **GT-A3** §1 re-led with the editor-blindness cure; **GT-A4** OQ-5 locked (REFRONT-9 = expanded row). Major folds: **D4 mixed-direction rows** (GT-R1-1 — ⚠ confirm at approval) + **D5 press-past-zero kept with the DC-4 voice guard** (GT-R1-8); table-scoped suggestion validity (GT-R1-2); the §3.5 dial composition rule (GT-R1-3); the complete §5 retirement inventory incl. the three `open_editor_on_mount` producers, the `Revise Terms`/carry-hint re-points, the D7-survives honesty note, and REFRONT-7-closes-moot (GT-R1-4); the §7 new-verb wiring/guard/failure contract (GT-R1-5); the §3.3 four-direction row contract (GT-R1-6); sequencing corrected to the June-9 re-sequencing (GT-R1-7); the PF-3 matrix extension + HTTP-boundary + determinism/int tests and the enumerated editor-test disposition + UX-3 mootness (GT-R1-9); selector cites corrected per direction (GT-R1-10); the `gold_per_turn` capacity rule (GT-R1-11); voice re-ordered before/with GT-Slice-3 (GT-R1-12); UX-2/UX-5 owned by GT-Slice-3 (GT-R1-13); clause-cap behavior (GT-R1-14); `reason_display` per suggestion (GT-R1-15).
- **v0.1 (2026-05-31)** — initial DRAFT against pre-PF code.
