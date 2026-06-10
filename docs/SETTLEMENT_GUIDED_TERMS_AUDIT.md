# Settlement Guided Terms — Design-Gate Audit Note (v0.1)

**Audits:** `docs/SETTLEMENT_GUIDED_TERMS_SPEC.md` **v0.1 DRAFT** — Run #1 (doc-audit run 1 of MAX 2 per DC-6).
**Date:** June 9, 2026. Audited against live `master` at **`6edeb6f`** (post-PF-1/PF-2/PF-3) — the spec was drafted May 31 against pre-PF code, so every section was swept against the post-PF reality per the audit charter.
**Method:** Structured review against the four lenses (design/creative, historical, edges/correctness, spec-process), with every checkable claim verified at file:line on live code, **plus five executed fixture probes** (DC-6: "a spec audit verifies the map; only a fixture verifies the territory") run in-memory against the real `SOVEREIGN_SMOKE_START=settlement_losing` world and synthetic matrix-style worlds, driving the real generator / validator / scorer / `_redial_settlement_terms` — no acceptance patching. Probe transcripts are summarized inline at each finding.
**Fold status: ALL FINDINGS + GT-A1..4 FOLDED into spec v0.2 on June 10, 2026 (same-day fold session; see §11).** The spec remains `NEEDS USER APPROVAL`; the one decision changed by the fold (GT-R1-1 → spec D4, mixed-direction rows) is flagged for explicit user confirmation at approval.
**Verdict: GO-with-changes.** The direction is right — guided, suggestion-driven, direction-implied authoring folded into the live per-court rows is exactly the user's documented preference and the natural completion of the re-front (DC-5 endorsed the direction; this audit concurs). But v0.1 cannot be approved as written: **0 CRITICAL, 9 MAJOR, 6 MINOR** findings below, plus the four mandatory pre-approval amendments **GT-A1..4** (pre-flight audit §7) which v0.1 does not yet contain. All findings carry verbatim-applicable fixes; fold them and GT-A1..4 into a **v0.2**, then take user approval. Follow-up work continues on **master** (no feature branches). A second full doc audit is **not** recommended (DC-6 budget) — a fold-verification pass over the v0.2 diff suffices.

> The biggest single player win in this redesign — **live per-court re-scoring while authoring** (today the Tier-3 editor is blind; you find out at REVIEW) — is buried in a §3.1 bullet. GT-A3 makes it the headline. The biggest single risk is the inverse of the spec's own pitch: "direction is implied" quietly became "direction is the only verb," which forecloses a live, mechanically-rewarded move (the sweetener — GT-R1-1, probe-verified) that the re-front's own worked example depends on.

---

## 1. Verdict summary

| Dimension | Result |
| --- | --- |
| Direction vs user preference (guided / suggestion-driven / direction-implied, per `terms_guidance`) | **PASS** — faithful to the bilateral model where it matters (no identity pickers, suggested defaults, live feedback); one fidelity gap (no per-suggestion reason line — GT-R1-15) |
| Coherence vs re-front spec v0.6 (per-court rows, dials, per-court gate, PROPOSE/REVIEW) | **PASS with findings** — composition with Tier-2 dials under-specified (GT-R1-3); peace/hard-stop directions unmapped (GT-R1-6) |
| Coherence vs cleanup spec v0.32 (blocked-REVIEW rail, draft lifecycle, SC-32 D5) | **PASS with findings** — retirement inventory misses three editor mount points incl. the blocked-REVIEW re-author arms and incoming-offer counter-authoring (GT-R1-4); no D5 copy violation anywhere in the spec |
| Post-PF reality sweep (the spec predates PF-1/2/3) | **FINDINGS** — sequencing stale (GT-R1-7); PF-1 failure-path contract / CH-5 not inherited by the new verbs (GT-R1-5); PF-1 carry-hint copy points at the surface being retired (GT-R1-4); DC-4 voice guard unowned (GT-R1-8) |
| Golden Rule #6 (deterministic; suggestions never random) | **PASS in intent, untested** — no determinism test named for `demand_suggestions[]` (GT-R1-9) |
| Golden Rule #8 (scale-ready) | **PASS** — all new work user-initiated, N = covered courts; one per-preview income-estimate reuse note (GT-R1-11); retiring the editor also retires the REFRONT-7 all-regions scan (state its disposition — GT-R1-4 fix) |
| Golden Rule #9 (no orphan deferrals) | **PASS with findings** — §5 removals are owned, but the inventory is incomplete (GT-R1-4) and UX-3/UX-2/UX-5/DC-4 dispositions are unstated |
| Reuse map exists at cited locations | **MOSTLY** — one wrong-file + wrong-direction cite (GT-R1-10); everything else verified at 6edeb6f (see §9) |
| GT-A1..4 absorbed | **NOT YET** — v0.1 predates them; clean fold targets identified for all four (§7), no conflicts |

---

## 2. Findings ledger

No finding without evidence; every probe was actually executed on 6edeb6f.

| ID | Sev | Spec § | One-line finding |
| --- | --- | --- | --- |
| GT-R1-1 | **MAJOR** | §2 D3, §3.1–3.2, §4 | One-direction-per-court forecloses mixed packages; the France-pays sweetener on a demand court is live, legal, and mechanically rewarded (`concession_credit`), and becomes unauthorable once Tier-3 is retired |
| GT-R1-2 | **MAJOR** | §3.1, §4 | Per-row valid-by-construction is provably insufficient — suggestion validity must be TABLE-scoped (shared gold budget + promised-region exclusion) or the guided flow re-creates D1 with the player driving (GT-A1's code half) |
| GT-R1-3 | **MAJOR** | §8 OQ-2 | Dial × authored-demand composition undefined; live semantics DELETE a hand-authored territory demand in one whole-table `More generous` click |
| GT-R1-4 | **MAJOR** | §5, §6, §8 OQ-4 | Editor-retirement inventory incomplete: three live `open_editor_on_mount` producers, the Godot consumers, the cleanup-spec `Revise Terms` row, and PF-1's "pay in land via 'Adjust terms'" copy are unowned; §6's dissolution does NOT retire D7's orphan class |
| GT-R1-5 | **MAJOR** | §7, §9 GT-Slice-1 | New-verb wiring + failure-path contract unstated: the verbs must join the dispatch tuple, the re-attach net (CH-5), the executor frozenset, the Godot whitelist, and gain mode/player guards — D2/D3's defect classes otherwise reopen on the new surface |
| GT-R1-6 | **MAJOR** | §3.2, §4 | The two other live directions — `peace` (dead-band) and `hard_stop` (no cross-side pair) — have no authoring-affordance contract; probe shows a hard-stop court renders `total=null` with no terms |
| GT-R1-7 | **MAJOR** | header, §9 | Sequencing is stale-vs-routing: "tackle after the Gate 4 smoke completes" deadlocks against the June-9 re-sequencing (this gate now PRECEDES the single end-of-queue smoke) |
| GT-R1-8 | **MAJOR** | §3.2, §9 GT-Slice-5 | Press-past-zero (DC-4) undecided for the guided model, and the DC-4 voice guard is unowned (verified not landed in PF-1) |
| GT-R1-9 | **MAJOR** | §9 | Test plan ignores the post-PF rules of thumb: no PF-3 matrix extension, no HTTP-boundary test (the D4 lesson), no determinism/int() pins for the suggestion payload, editor-test disposition vague, UX-3 mootness unstated |
| GT-R1-10 | MINOR | §1, §7 | `rank_cession_candidates` cited in the wrong file and for the wrong direction; the demand-side and settlement-concede-side selectors are different, already-existing functions |
| GT-R1-11 | MINOR | §4 | `gold_per_turn` gate understated — the binding rule is the capacity formula (gold + income × turns), not the `GOLD_PER_TURN_*` bounds; pre-fill must derive from the COURT's capacity |
| GT-R1-12 | MINOR | §9 | Voice slice sequenced last — the exact anti-pattern REFRONT-V was re-ordered to avoid; suggestion copy lands in Slices 2–3 unvoiced |
| GT-R1-13 | MINOR | §9 GT-Slice-3 | UX-2 (REVIEW renders identically to PROPOSE) and UX-5 (no scroll container) are unowned; both verified still true at 6edeb6f and both get worse with inline row expansions |
| GT-R1-14 | MINOR | §3.1 | `Add demand` state at `MAX_SETTLEMENT_CLAUSE_COUNT` (= 8) unspecified; the Slice-2 audit fold set the precedent (no-op/disabled, never over-cap) |
| GT-R1-15 | MINOR | §3.1 | Suggestions carry no reason line — the bilateral flow's signature beat is "I suggest Silesia — [reason]"; the guided options as drafted are mute |

### GT-R1-1 — MAJOR — one-direction-per-court forecloses the sweetener (probe-verified)

- **Claim under test:** §2 D3 / §3.1–3.2 / §4 lock "direction is always implied" with exactly one verb set per court row (demands when winning, offers when losing). §4's closing line: "No exotic free-direction case remains."
- **Probe (executed):** synthetic France vs Britain+Prussia, both pairs +60, France gold 5000. Baseline demands `[Rhineland + 300g from Prussia, 300g from Britain]`; Prussia scores **35** (`near_acceptable`). Adding `{"gold_indemnity", from: France, to: Prussia, amount: 200}` — a France-pays sweetener on a DEMAND-direction court — **validates clean** and moves Prussia to **43**, with the scorer's `concession_credit` component going **0 → 8**. The mixed-direction package per court is legal (V3 only enforces cross-SIDE transfer, either direction) and mechanically rewarded by the live 10-component formula (`calculate_concession_credit`, `settlement_scoring.py:1273`).
- **Why it matters:** the re-front's own §17 worked example is exactly this move ("adds a gold sweetener France pays → Austria climbs 56% → ~71%") — authored in Tier 3. GT retires Tier 3. The dials cannot reach it either: the focused-Ease seed (`_redial_settlement_terms`, `settlement_preview.py:3204-3225`) fires **only when the dial left the court untouched**, so a court with live demand clauses can never gain a sweetener without first destroying its demands. Post-GT, "demand Silesia AND sweeten with gold" is unauthorable anywhere — an agency regression dressed as guidance, and the presentation layer already supports the mixed read (`_court_direction_summary:2892` renders "Demanded: X; Conceded: Y").
- **Fix (apply verbatim):** in §3.1/§3.2, make direction select the **defaults, ordering, and copy** of the row menu — not the verb set. A demand-direction court's `Add demand` expansion lists demand options first plus an `Offer a sweetener` group (gold / region France pays, same candidates as §3.2); a concede-direction court mirrors it. Amend §2 D3's rationale ("there is never a need to pick identities" stays true — both option groups are still fully formed, direction-fixed per option). Add a named test: `test_demand_direction_row_can_author_proposer_paid_sweetener_and_concession_credit_applies`. If the user instead prefers the hard one-direction cut, the spec must say so explicitly WITH the §17-example regression named and a rationale — silence is not an option (Golden Rule #9 spirit).

### GT-R1-2 — MAJOR — suggestion validity must be table-scoped, not row-scoped (probe-verified; GT-A1's code half)

- **Probe (executed, real `settlement_losing` fixture):** France gold 1500, two concede courts. The PF-1 baseline is valid (500g→Britain + Waterloo→Britain + 500g→Prussia, honest 36/36 holdouts). A player-shaped over-commit `[1000g→Britain, 1000g→Prussia]` — **each row individually affordable** (a lone 1000g row validates) — is rejected **only** by the table-level `gold_payment_budget_conflict` (`_check_gold_payment_budget_conflict`, `settlement_preview.py:164-252`) at the restage choke point.
- **Why it matters:** §3.1 promises "options are valid-by-construction… the validator should rarely fire." With per-row affordable defaults and N rows, the validator will fire **routinely** on exactly D1's defect class, now with the player driving (the pre-flight audit predicted this — GT-A1). Same for regions: PF-1 threads a `promised_regions` exclusion set through the baseline loop (`:2576`, `:2625-2627`, `_concession_baseline_select_transferable_region:1475` takes `excluded_regions`) precisely because row-local candidate generation double-promises; a guided suggestion source that doesn't inherit the exclusion re-creates V1 violations at the suggestion layer.
- **Fix:** fold with GT-A1 (§7 below): (a) the PROPOSE payload gains a `treasury_line` (`{"treasury": int, "committed": int, "reserve": int, "remaining": int}`, all `int()`), rendered as one visible allocation line above the rows; (b) GT-Slice-2's suggestion generator takes `(remaining_gold_budget, promised_regions)` computed across the whole staged table, so offered defaults are affordable **after** existing commitments and never offer an already-promised region; (c) name the restage validator + `error_display` re-attach as the defense-in-depth backstop (it exists and renders — verified `:3446-3464` + `main.gd:981-984`). Tests: `test_guided_gold_suggestion_caps_at_remaining_table_budget`, `test_guided_region_suggestion_excludes_already_promised_regions`.

### GT-R1-3 — MAJOR — dial × authored-demand composition is undefined and destructive (probe-verified)

- **Probe (executed):** package `[peace, Prussia cedes Rhineland (hand-authored), Britain pays 400g (hand-authored)]`; ONE whole-table `More generous` click → `[peace, Britain 300g]`. The hand-picked territory demand is **deleted** (territory is binary in `_redial_settlement_terms:3193-3199`: generous drops a demand clause touching the court) and the gold shrank by the 100 step.
- **Why it matters:** §8 OQ-2's entire treatment is "keep — they compose." The live composition rule destroys authored work silently; the §3.3 worked example even invites it (step 4 authors a demand, step 5 clicks whole-table generous). The two systems write the same staged draft; the rule must be stated, decided, and tested — especially since the guided flow makes hand-authoring the headline activity.
- **Fix:** add a "Dial composition rule" block to §3.1 (or OQ-2): EITHER (recommended) **dials never drop a clause the player explicitly authored via `Add demand`** — they shrink gold to its floor and skip authored territory/identity clauses (tag authored clauses in the staged draft: `"authored_by": "player"` — serialization rule applies), with Talleyrand noting the skip; OR dials treat all clauses identically and each removal is surfaced in `delta_display` (the cheap option, but it makes `More generous` a destructive verb next to per-line `Remove`, which is redundant and worse). Named test either way: `test_whole_table_generous_does_not_silently_delete_player_authored_demand` (or its inverse with the delta assertion).

### GT-R1-4 — MAJOR — the retirement inventory is incomplete, and §6 does not retire D7

- **Evidence (all live at 6edeb6f):** §5 removes the editor scene/script, the identity-picker schema, the editor POST path, the merge call, and DWL-SET-SC5R-3. Not in the list:
  - **Three `open_editor_on_mount` producers:** `apply_concession_baseline_replacement` (`settlement_preview.py:7409-7414`), `re_author_with_concessions` (`:8430-8431` — a blocked-REVIEW rail action, normative in cleanup v0.32), and the incoming-offer `request_settlement_revision` counter-authoring route (`:9948-9957` — "mount EDIT immediately"). OQ-4 gestures at (c) but not (a)/(b).
  - **Godot consumers:** the client-side `adjust_terms` branch (`main.gd:41-44` — handled client-side, mounts the editor, never round-trips), the `open_editor_on_mount` routing, and `_maybe_remount_settlement_editor_after_error`.
  - **Copy/contract retargets:** the cleanup-spec REVIEW row's `Revise Terms … only when it returns the staged package to an edit-capable route` (`SETTLEMENT_UI_CLEANUP_SPEC.md:570`); PF-1's budget-bound carry hint "use **'Adjust terms'** to pay in land instead" (`settlement_preview.py:3367-3370`) — a player-facing dead pointer the day the editor dies; the Voice Bible incoming-offer line `settlement_incoming_offer_request_revision_talleyrand` ("I shall open the offered terms … for our own hand").
  - **D7 honesty:** §6's dissolution retires the only `merge_same_war_settlement_drafts` call site (`:5777`, inside `stage_settlement_confirm`'s editor-submit path — verified single call site, so the §6 claim is true as scoped). But D7's latent orphan class lives in the **replacement-stage preset family** (`_stage_replacement_settlement_terms:7298` + the `author_*` arms, e.g. `:8011-8047`), which are blocked-REVIEW recovery actions that survive the editor's death. DC-5's "deleting the submit-blob deletes D7's entire latent-orphan class" is optimistic — **CH-5 remains D7's cure.** Bonus to state while here: retiring the identity-picker schema also retires the `_region_control_options:4451` all-regions scan, so **REFRONT-7 closes as moot** — say so, with its test re-pointed or deleted.
- **Fix:** §5 becomes a complete inventory table: every producer/consumer/copy site above, each with its named post-retirement route (`re_author_with_concessions` / `apply_concession_baseline_replacement` re-stage **guided PROPOSE** rows seeded from the preset; incoming-offer counter-authoring lands on guided PROPOSE seeded from the offered terms — resolving OQ-4(b); `Revise Terms`/cleanup `:570` re-points to "returns the staged package to the guided PROPOSE surface"; the carry hint's "pay in land" re-points to "add a territory offer on the court's row"). Add one sentence to §6: "This retires the merge call site only; the replacement-stage preset family and its D7 exposure remain, cured by CH-5." Add REFRONT-7 disposition.

### GT-R1-5 — MAJOR — the new verbs' wiring and failure-path contract is unstated

- **Evidence:** the five Tier-2 verbs are wired at exactly four points the spec never names: the handler dispatch tuple (`settlement_preview.py:7798-7804`), the **re-attach net** (`:7820-7831` — a failed/blocked action re-attaches the mounted dialogue so the popup never orphans; this is the D2/D3 cure and CH-5's seed), the executor's `_SETTLEMENT_TIER2_ACTION_IDS` frozenset + dispatch list (`diplomatic_executor.py:21-29`, `:2923`), and the Godot whitelist (`main.gd:35-57`). `_handle_settlement_tier2_action` guards `caller_kind` only (`:7592-7605`) — there is no `dialogue_mode` guard, so the spec's new mutation verbs should add one explicitly (REVIEW is a frozen staged-decision surface — UX-2 boundary; today only the absence of rail affordances protects it).
- **Why it matters:** every settlement defect class found so far (drop-stranding, D2's "Response processed", D3's silent dials, D7) is the same invariant violated at a new arm. A spec that adds three mutation verbs without naming the invariant invites the fourth recurrence. The memory-file bug class ("new dialogue types need whitelist wiring") is the same lesson one layer down.
- **Fix:** GT-Slice-1 scope gains a "wiring + failure contract" block: the three verbs (a) join the dispatch tuple, the re-attach net (or the CH-5 wrapper if CH-5 lands first — name the dependency either way), `_SETTLEMENT_TIER2_ACTION_IDS`, and `SETTLEMENT_DIALOGUE_ACTIONS`; (b) are player-only AND `dialogue_mode == "PROPOSE"`-only (server-side guard, not just absent buttons); (c) on any validation/eligibility failure return the re-attached dialogue + `error_display` — never neither. Named tests: `test_demand_verbs_rejected_in_review_mode_with_error_display`, `test_demand_verb_failure_reattaches_dialogue_never_silent` (plus the matrix extension in GT-R1-9).

### GT-R1-6 — MAJOR — `peace` and `hard_stop` rows have no authoring contract (probe-verified)

- **Probe (executed):** France vs Britain+Prussia+Austria with Austria's cross-side pair removed: Austria renders `direction="hard_stop"`, `total=None`, `band="reject"`, hard-stop reason bubbled, no baseline terms, `carries=False`. The live direction enum is four-valued (`_court_direction_from_selection:2872-2889`: demand / concede / peace / hard_stop); §3.2/§4 specify menus for two.
- **Fix:** add both rows to §4: **dead-band (`peace`) court** → per GT-R1-1's resolution, both option groups (demand + offer), neutral default `{"type":"peace"}` (this is also where the §17 "sweeten the wobbler Austria" move lives); **hard-stop court** → `Add demand` absent/disabled with `disabled_reason_display` (any clause cannot move a `total=null` court; the scorer hard-stops it), row exposes Drop only, voice = the existing `settlement_multi_court_court_hard_stop` family (Voice Bible §16.1a). Tests: `test_hard_stop_court_row_disables_authoring_with_reason`, `test_dead_band_court_offers_both_directions` (name per resolution).

### GT-R1-7 — MAJOR — sequencing text deadlocks against the June-9 re-sequencing

- **Evidence:** header line 6 ("Tackle **after the Gate 4 manual settlement smoke completes**") and §9 ("All slices are … **sequenced after the Gate 4 smoke**") vs the user's June 9 decision (CLAUDE.md / STATUS / pre-flight audit §0): the Guided Terms gate is **next**, and the smoke runs **once at the END of the settlement queue**. An implementer following the spec literally waits for a smoke that is scheduled after them.
- **Fix (verbatim):** header → "**Sequencing (updated June 9, 2026):** this design gate is the immediate next settlement action; fold the Gate-4 pre-flight amendments GT-A1..4 (`SETTLEMENT_GATE4_PREFLIGHT_AUDIT.md` §7) before user approval. The Gate 4 manual smoke is re-sequenced to run ONCE at the END of the settlement queue, after this spec's slices land — it smokes the guided surface, not the editor it replaces." §9 mirror. Also refresh §1's framing that the smoke "is partly exercising" the editor (the remaining smoke will exercise the guided flow).

### GT-R1-8 — MAJOR — press-past-zero (DC-4) is undecided and its voice guard unowned

- **Probe (executed):** losing world, `[peace, 100g France→Britain]`; focused `Harsher` click 1 → `[peace]` (concession dropped); click 2 → seed authors `{"gold_indemnity", from: Britain, to: France, amount: 100}` — **a demand on the court that is beating France**, wordlessly. Grep confirms no DC-4 guard line ("not the ones suing for peace") exists in `backend/` — PF-1 did not take it (its owner row said "PF-1 **or** GT-Slice-5").
- **Fix:** §3.2 gains a decision: the guided model **keeps** direction-flip authoring (player agency; the scorer prices it — consistent with GT-R1-1's both-groups resolution, which makes the flip an explicit `Add demand` on a concede court rather than a dial accident), and GT-Slice-5 owns the DC-4 voice guard verbatim from the pre-flight audit ("They are not the ones suing for peace, Sire — but as you wish."), fired whenever a demand is authored/seeded on a concede-direction court. Named test: `test_demand_on_concede_direction_court_fires_talleyrand_caution_voice`. (If instead the dial seed is changed to never flip direction, that is a Tier-2 behavior change and must be owned as its own row — do not leave it implicit.)

### GT-R1-9 — MAJOR — the test plan predates the post-PF rules of thumb

- **Evidence:** GT-Slice-1/2 name good behavior tests but: no **PF-3 matrix extension** (the standing harness `tests/test_settlement_baseline_scenario_matrix.py` exists precisely so every new verb is driven across direction × coverage × treasury cells and either succeeds or returns dialogue + `error_display`); no **HTTP-boundary test** with the actual client payload shape (the D4 lesson — the SC-5R-2 round-trip test passed a field the real client never sends and the bug shipped); no `test_demand_suggestions_are_deterministic_same_world` (Golden Rule #6) nor an `int()` pin for the new payload numerics (Golden Rule #2); GT-Slice-4 says "migrate or delete the SC-5R-2 editor tests" with no enumeration rule; UX-3's mootness (pre-flight: "moot if Guided Terms lands") is never stated.
- **Fix:** GT-Slice-1 adds `test_settlement_matrix_demand_verbs_succeed_or_reattach_with_error_display` as a parametrized extension of the PF-3 file; GT-Slice-3 adds one `/respond_to_diplomatic_dialogue` HTTP-boundary test posting the exact Godot `action_params` shape for `settlement_demand_add`; GT-Slice-2 adds the determinism + `int()` tests; GT-Slice-4's completion enumerates the editor-test disposition by file (`tests/test_settlement_sc5r2_godot_editor.py` → migrate the draft-lifecycle/round-trip tests to the guided surface, delete the picker-schema pins; the contract tests for retained backend validity stay) and one line: "UX-3 closes as moot with the editor."

### GT-R1-10 — MINOR — reuse-map cites: wrong file, wrong direction

- **Evidence:** §7 cites "`rank_cession_candidates` (`diplomatic_executor.py:3846`)" — the function lives at **`diplomatic_templates.py:2422`**; `diplomatic_executor.py:3846-3849` is a call site. More substantively, `rank_cession_candidates(world, player_nation, target_nation)` ranks the **player's** cedeable regions (the bilateral losing/concede direction). The §3.1 demand-direction dropdown ("regions Prussia controls") needs the demand-side selectors — `_demand_baseline_select_region` (`settlement_preview.py:2222`) or `generate_suggested_terms`' demand stage (`diplomatic_templates.py:2023`). The settlement concede-side selector with PF-1's exclusion param is `_concession_baseline_select_transferable_region:1475` and should be preferred over the bilateral fn for §3.2 (it already takes `excluded_regions`).
- **Fix:** correct the §7 row to name all three selectors by direction with the file:line cites above; fix the §1 terms_guidance cite to `diplomatic_executor.py:3858-3888` (verified accurate region).

### GT-R1-11 — MINOR — `gold_per_turn` is gated by capacity, not just bounds

- **Evidence:** the binding rule is `capacity = current_gold + max(0, net_income) × max_turns` over new + existing recurring obligations (`_check_gold_payment_budget_conflict:164-252`); `GOLD_PER_TURN_*` are only floor/turn bounds (10g, 1–20 turns). For demand-direction recurring gold the payer is the **court**, so the §3.1 pre-fill must derive from the court's capacity (and join GT-R1-2's table budget when France pays). `_estimate_payer_net_income_per_turn:140-161` scans `world.regions` per call — fine user-initiated, but the suggestion payload should compute it once per court per preview, not per option.
- **Fix:** §4 `gold_per_turn` row: "pre-fill ≤ payer capacity (gold + income × turns, `:164-252`), net of existing recurring obligations; one income estimate per court per preview."

### GT-R1-12 — MINOR — voice last repeats the anti-pattern REFRONT-V fixed

- **Evidence:** re-front §14 Voice: the resolver rule "lands **before or with** Slice 1's PROPOSE copy — not after," and Slice 1's completion depended on it. GT-Slice-5 is sequenced last while the suggestion copy ships in Slices 2–3. The §16.1a family + resolver exist, so the risk is smaller than REFRONT-V's (no anonymous beats), but suggestion lines would land unvoiced or ad-hoc.
- **Fix:** re-order: GT-Slice-5's resolver/family extension lands **before or with GT-Slice-3**; GT-Slice-3's completion gains "suggestion + reaction copy resolves through the §16.1a families." DC-4's guard line (GT-R1-8) rides it.

### GT-R1-13 — MINOR — UX-2 and UX-5 must be owned by GT-Slice-3

- **Evidence (verified at 6edeb6f):** `proposal_confirm_popup.gd` contains **no** `dialogue_mode` branch (REVIEW renders identically to PROPOSE — UX-2) and **no** `ScrollContainer` (UX-5). Inline `Add demand` expansions + current-demand lines make rows substantially taller, worsening both.
- **Fix:** GT-Slice-3 scope gains: (a) a `dialogue_mode` render branch — REVIEW reads as a staged-decision surface (terms frozen, authoring affordances absent, blockers promoted); (b) a scroll container around the per-court table with the expansion designed to a row-height budget (UX-5 / Golden Rule #8 horizon). Tests: source pins for both.

### GT-R1-14 — MINOR — `Add demand` at the clause cap

- **Evidence:** `MAX_SETTLEMENT_CLAUSE_COUNT = 8` (`settlement_scoring.py:148`); the Slice-2 audit fold made the focused-dial seed cap-honoring (`settlement_preview.py:3204-3215` — no-op rather than over-cap). The guided `Add demand` needs the same contract.
- **Fix:** §3.1: at cap, `Add demand` renders disabled with a humanized reason ("The settlement already carries eight clauses, Sire — remove one before adding another."); never authors an over-cap draft for the restage validator to bounce. Test: `test_add_demand_disabled_at_clause_cap_with_reason`.

### GT-R1-15 — MINOR — suggestions are mute; bilateral's signature beat is the reason line

- **Evidence:** the bilateral flow the spec claims as its model always explains itself — "I suggest {candidate} — {reason}" (`diplomatic_executor.py:3900`); the settlement concede path has `_format_concession_reasoning:1567`. §3.1's option list (`Take [Silesia ▾] from Prussia`) carries no why.
- **Fix:** GT-Slice-2's `demand_suggestions[]` entries each carry `reason_display` (deterministic, from the existing reasoning helpers / `NATION_DESIRE_PROFILES` rationale), rendered as the option's subtitle; Talleyrand's row voice references the top suggestion's reason. This is the difference between a conversation and a form wearing a wig.

---

## 3. Lens A — Design / creative

- **Does it read as a conversation?** Mostly yes, with two amendments. The inline expansion of fully-formed, eligibility-gated options with live per-court re-scoring is the multi-party generalization of `terms_guidance`'s suggest→accept/skip loop, and folding it into the rows (D2) is the right call — the rows already carry voice, band, direction, and dial affordances; a modal-on-modal wizard would have been worse. What's missing for the conversational read: the **reason line per suggestion** (GT-R1-15) and **voice landing with the surface** (GT-R1-12). With both, this is Talleyrand proposing; without, it is a tidy form.
- **Is the headline win front and center?** No — GT-A3 stands. §1 leads with the France/France default; the editor-blindness cure (live per-court re-scoring while authoring vs find-out-at-REVIEW) is the single biggest player-experience change in the document and currently lives in a §3.1 bullet.
- **Agency / railroading.** The probe evidence says the v0.1 model railroads in one real place: mixed-direction packages per court (GT-R1-1). Every clause type is otherwise reachable, eligibility gates mirror the validator rather than tightening it, and deliberately harsh authoring stays available (press-past-zero survives via dials — GT-R1-8 makes it a legible choice instead of a dial accident). With GT-R1-1/6/8 resolved, guided agency is a strict superset of today's editor agency minus nothing but the invalid.
- **Merge/replace dissolution (§6).** Genuinely elegant and verified: one merge call site (`:5777`), on the path being retired; no submit-blob → no reconcile → DWL-SET-SC5R-3's controls become dead scope correctly removed. But the dissolution does **not** delete D7's latent orphan class (the replacement-stage preset family survives — GT-R1-4); the spec should say so plainly so approval doesn't bank a fix it isn't buying. CH-5 remains the structural cure and is the natural companion slice.
- **Tier-2 vs guided rows.** Distinct and complementary — dials are court-level magnitude sweeps, rows are clause-level identity+magnitude — PROVIDED the composition rule is stated (GT-R1-3). OQ-2's "keep" is right; "they compose" without semantics is where the next smoke finding lives.
- **REFRONT-9 home (GT-A4 / OQ-5).** Coherent — the expanded per-court row is the natural progressive-disclosure site for the 10-component breakdown, far better than a panel on a surface scheduled for demolition. Confirm as locked.

## 4. Lens B — Historical

- **Menu shape: period-strong.** The §4 mapping covers all 8 live clause types (verified vs `CANONICAL_CLAUSE_TYPES`, `settlement_scoring.py:93-102`): indemnities (lump + recurring tribute — the post-Tilsit Prussian contributions), border cessions, liberation of client states, forced alliance **with the Continental System accession toggle** (an existing optional field, `includes_continental_system`, `settlement_scoring.py:98` / apply at `settlement_preview.py:6504-6541` — Tilsit's Russia clause in game terms; not a new mechanic), vassalage/subjugation (satellite-state texture). Nothing in the menu reads anachronistic.
- **Magnitudes and asymmetries: plausible at game scale.** Winner-side defaults are deliberately modest (gold floor 300, territory only above direct score +30 — `DEMAND_TERRITORY_DIRECT_SCORE`, `:1391`) while loser-side escalation runs to `gap × 100` capped at 1,500 against treasuries of ~800–5,000 — the right shape: indemnities scale with leverage, and a Pressburg-grade extraction is a meaningful fraction of a treasury, not a rounding error. The probe's losing baseline (500g + 500g + one border region from a 1,500 treasury) reads as a Lunéville/Amiens-style negotiated defeat — cede the periphery, pay, keep the core — not modern UI haggling.
- **Missing period levers (each needs the one-line exclusion, currently silent):** *army-limitation clauses* (the 1808 Convention of Paris capped Prussia at 42,000 men) — no clause type exists; exclude under §10 mechanics-unchanged, candidate future clause type via its own gate; *occupation-until-paid* (Prussia 1807–08) — approximated by `gold_per_turn`, exclude with that note; *dynastic marriage* — already ranked flavor/cut (DW-4); *recognition-of-title clauses* (Joseph in Naples, the Confederation) — partially expressible via vassalage/liberation, exclude; *maritime/colonial returns* (Amiens) — off-map, exclude. Add these five lines to §10.
- **GT-A2's recommendation rule, in character.** Talleyrand-the-character would defend "buy the cheapest signatures; let the dearest enemy fight on" — it is arithmetic with manners, and it is what 1805–13 practice actually was (Austria signs at Pressburg because Austria can be bought; Britain fights on because it cannot). The deterministic rule proposed in §7 below encodes exactly that.
- **SC-32 D5:** no "conference"/"congress"/"veto" appears anywhere in the spec's proposed player-facing copy; the per-court holdout texture (separate peaces, the holdout fights on) is the *opposite* of Congress framing. The §16.1a copy test already enforces it for new lines. Clean.

## 5. Lens C — Edges / correctness

Covered by GT-R1-1/2/3/5/6/8/11/14 above (each probe-grounded). Additional sweeps that came back clean are in §9 (verified-OK). Two notes that are neither findings nor clean:

- **Draft persistence:** guided mutations ride `_restage_settlement_after_redraw`, which already persists through the PF-2 single scoped store (`:3497-3507`), so Back Out / War Detail "Draft kept" badge / end-turn discard / save-load all inherit correctly **as long as the new verbs reuse the restage helper** — make that reuse explicit in GT-Slice-1's scope (one sentence) so an implementer doesn't hand-roll staging. If GT-R1-3's fix adds an `authored_by` clause tag, the serialization rule (`to_dict`/`from_dict` + `test_serialization_enforcement.py`) applies — name it.
- **Typed-path:** none of the findings above are typed-command-only; all are reachable from the F1 wizard / War Detail routes (per the settlement-surface memory rule, typed `propose common peace` edge cases were not audited).

## 6. Lens D — Spec-process / buildability

- **Slices are sized and ordered buildably** (backend verbs → payload → UI → retirement → voice), each with named behavior tests and completion definitions — with the corrections: voice moves earlier (GT-R1-12), GT-Slice-1 gains the wiring/failure block (GT-R1-5), GT-Slice-4 gains the full inventory (GT-R1-4), and the test plan gains the matrix/HTTP/determinism rows (GT-R1-9).
- **Golden Rule #9:** §5's removals are owned with a landing slice — good — but completeness is the gap (GT-R1-4), and four pre-flight dispositions are unstated (UX-2, UX-3, UX-5, DC-4). OQ-1/2/3 recommendations are sound (dropdown over wizard-loop; keep dials; France-only liberator with the cut named). OQ-4 must be **resolved at this gate** — §2 of this note supplies the trace (the three mount producers + the SC-1 losing-side flow) so the fold can lock it rather than defer it into GT-Slice-4. OQ-5 → locked per GT-A4.
- **DC-1 inheritance:** the spec's §3.1 "validator remains the authority as defense-in-depth" is the right instinct; strengthen it to the DC-1 sentence ("valid-by-construction is a property of the draft STORE, not of the author — one validation choke point at staging, for everyone"), which the post-PF code now actually implements (`_degrade_generated_baseline_to_valid:2426` for the system author; restage validation for the player).

---

## 7. GT-A1..4 fold plan (exact targets + text direction)

All four absorb cleanly; no conflicts with the v0.1 structure.

| Amendment | Fold target | Text direction |
| --- | --- | --- |
| **GT-A1** (shared budget first-class) | New **§3.4 "One treasury, many courts"** + §4 gold rows + §11.2-style payload note | The PROPOSE surface renders one allocation line — `"1,500g: Britain 750 / Prussia 750 / reserve 0 / remaining 0"` — sourced from a new `treasury_line` payload block (`{"treasury","committed","reserve","remaining"}`, all `int()`). Suggestion generation is **table-scoped** (GT-R1-2): gold defaults cap at `remaining`, region candidates exclude `promised_regions`. The restage validator + `error_display` re-attach is the backstop, not the UX. Tests as named in GT-R1-2. Without this row concept the guided flow re-creates D1's over-commit with the player driving — probe-verified at §2. |
| **GT-A2** (losing-multi-court allocation OQ) | New **OQ-6** + a `settlement_budget_bound_constraint_talleyrand` voice extension (GT-Slice-5) | "When the treasury cannot satisfy every concede-direction holdout, whom does Talleyrand recommend easing/keeping?" **Locked deterministic rule (Golden Rule #6, no vibes):** rank concede-direction holdouts by `gap_to_threshold` ascending (cheapest signature first); recommend concentrating the remaining budget on the cheapest court(s) whose gaps are coverable, and **naming the most expensive holdout as the court to set aside** (Drop) — tie-break by larger `abs(direct_score)`, then lexicographic court name. Rendered as advice only (player clicks). In-character defense: Pressburg logic — you buy the peace you can afford and let the dearest enemy fight on; Britain is the archetype. Reuses the live PF-1 detector (`_settlement_budget_bound_constraint:3285`) as the trigger. Test: `test_budget_bound_recommendation_ranks_cheapest_signature_first_deterministically`. |
| **GT-A3** (lead with the editor-blindness cure) | §1 restructure | Problem #1 becomes: "**The editor is blind while you author.** Tier-3 has no live acceptance — you assemble, Submit, and discover the verdict at REVIEW. The guided rows re-score the affected court on every Add/Remove/adjust — the same live feedback Tier-2 dials already have." The France/France default and vagueness become items 2–3. The §3.1 live-rescore bullet is promoted into the §2 design-decision rationale. |
| **GT-A4** (REFRONT-9 fold) | §8 OQ-5 → locked decision; GT-Slice-3 scope | Flip OQ-5 from open question to **LOCKED: yes** — REFRONT-9's focused-court 10-component breakdown + focus trigger land as the **expanded state of the per-court row** in GT-Slice-3 (re-front §14 REFRONT-9 row updates its landing pointer); the test `test_tier3_focused_court_expands_full_component_breakdown` re-homes to the row expansion. The existing presentation-only `settlement_focus_court` handler (`:7619-7648`) is the trigger transport. |

---

## 8. Ranked top-5 "fix before approval"

1. **GT-R1-1** — decide mixed-direction-per-court (the sweetener). This is the one finding that needs a **user decision**, because it changes the §2 D3 design decision itself; everything else is fold work. Recommended: both option groups per row, direction sets defaults.
2. **GT-R1-2 + GT-A1** — table-scoped suggestion validity + the visible treasury line. Without it the new surface's first poor-treasury multi-court session reproduces D1's class as player-facing rejection spam.
3. **GT-R1-4** — the complete retirement inventory (+ D7 honesty + OQ-4 resolution). This is the difference between "retire the editor" and "strand five routes that mount it."
4. **GT-R1-3** — the dial composition rule. One generous click currently deletes hand-authored work; the guided flow makes hand-authoring the headline activity.
5. **GT-R1-7** — the sequencing text. Trivial to fix, but it is the one item that misroutes an implementer on day one.

(GT-R1-5/6/8/9 are mandatory folds too — they rank 6–9 only because their failure modes surface at implementation/audit time rather than at approval time.)

---

## 9. Verified-OK ledger (a second run should NOT re-litigate)

- **PF-1 is real and live:** treasury split across concede courts + `promised_regions` threading + degrade-to-valid in `compute_settlement_baseline` (`:2552-2576`, `:2616-2627`, `:2661-2672`); the `settlement_losing` fixture opens to a **valid** baseline (`[peace, 500g→Britain, Waterloo→Britain, 500g→Prussia]`) with honest 36/36 `near_acceptable` holdouts and `carries=False` (probe-executed).
- **The failure-path contract exists for the new verbs to join:** restage validation failure returns `error_display` (`:3446-3464`); the Tier-2 re-attach net (`:7820-7831`); Godot renders `transient_error_display` (`main.gd:981-984`) and the validation-detail join (`:1076-1085`); `submit_settlement_for_review` validates pre-REVIEW with re-attach (`:7901-7931`).
- **§7 reuse rows verified at 6edeb6f** (except the GT-R1-10 row): `compute_settlement_baseline:2480`; `compute_per_court_acceptance:2941` with the one-shared-pass + injected `balance_projection` (`:3012-3020`); `validate_settlement_terms:3613`; `evaluate_subjugation_eligibility:1671` / `evaluate_vassalage_eligibility:1716` (delegates to subjugation: direction, war state, not-already-vassal, power cap — the §3.1 claim is accurate) / `evaluate_liberation_eligibility:1736`; the `action_params` transport end-to-end (`diplomatic_executor.py:21-29`, `:2736`, `:2923`; `main.gd:35-57`, `:3376`).
- **§4 covers the complete live clause set** — all 8 `CANONICAL_CLAUSE_TYPES`; `includes_continental_system` is an existing optional field, so the §3.1 checkbox adds no mechanic (§10 boundary holds).
- **§5's CommandRequest removal is clean in principle:** `target_nation` (`main.py:768`) predates 067e431 and stays (the PF-2 reopen path uses it); the three 067e431 fields (`:777-779`) have no non-editor producer; commit `067e431` exists ("Fix Gate-4 settlement editor: authored terms dropped + validation silent"). GT-Slice-4's verify-then-remove stands.
- **§6's merge claim is true as scoped:** exactly one `merge_same_war_settlement_drafts` call site (`:5777`), on the editor-submit path being retired. (The D7 caveat is GT-R1-4, not a correction of §6's own sentence.)
- **§2 D3's side premise is true:** every valid transfer is cross-side (V3 / `_CROSS_SIDE_TRANSFER_CLAUSE_TYPES`); only the per-court single-direction *inference* is wrong (GT-R1-1).
- **No fog gating proposed** (diplomacy has no fog — correct); **no SC-32 D5 violation** in any proposed copy; **player-only boundary** named in GT-Slice-1's tests (the R6-M2 lesson learned).
- **Scale:** all new work is user-initiated and bounded by covered-court count; no per-turn hot-path region scans proposed; the dial/restage cost model is unchanged from Slice 2.
- **Worked example magnitudes** match live constants (300 = `CONCESSION_BASELINE_GOLD_FLOOR`; dial step 100 = `SETTLEMENT_DIAL_GOLD_STEP`).
- **DC-3 (per-court gate) untouched** — §10 correctly leaves the ratification gate alone; the probe's REVIEW path was not re-audited (re-front Run #6 + PF-1 own it).

---

## 10. Bottom line

The Guided Terms redesign is the right cure for the right disease, verified against the code it must land on: the direction-implied, suggestion-driven model matches both the user's documented preference and the bilateral flow's actual shape (`diplomatic_executor.py:3836-3910`), the per-court-row fold reuses machinery that all exists where claimed (one cite error), and the merge/replace dissolution is real. What v0.1 is missing is the post-PF world: the shared-budget row concept (GT-A1 / GT-R1-2), the failure-path + wiring contract PF-1 built (GT-R1-5), the full inventory of what "retire the editor" actually touches (GT-R1-4), and three places where "direction is implied" hardened into "direction is the only verb" against live mechanics that say otherwise (GT-R1-1/6/8 — all probe-verified). None of it is structural; all of it is foldable.

**Verdict: GO-with-changes — fold the 15 findings + GT-A1..4 into v0.2, obtain user approval (GT-R1-1 is the one open user decision), then implement on master.** Per DC-6 this was doc-audit run 1 of 2; spend run 2 only as a targeted fold-verification of the v0.2 diff, not a fresh full pass.

---

## 11. Fold record (v0.1 → v0.2, June 10, 2026)

All 15 findings and GT-A1..4 were folded into `docs/SETTLEMENT_GUIDED_TERMS_SPEC.md` **v0.2** in the same session (user-delegated fold). Where each landed:

| Finding / amendment | Folded into (spec v0.2) |
| --- | --- |
| GT-R1-1 (mixed-direction rows) | §2 **D4** (⚠ flagged for user confirmation at approval) + §3.1 offer group + §3.3 + §4 two-group mapping + GT-Slice-1 sweetener test |
| GT-R1-2 + GT-A1 (table-scoped validity, treasury line) | §3.4 "One treasury, many courts" + §4 gold gates + GT-Slice-1/2 tests |
| GT-R1-3 (dial composition) | §3.5 rule (`authored_by` tag; dials never silently drop player-authored clauses) + OQ-2 re-lock + named test |
| GT-R1-4 (retirement inventory + D7 honesty + REFRONT-7 moot) | §5 full inventory table + §6 scope-honesty paragraph + GT-Slice-4 routing tests |
| GT-R1-5 (verb wiring/guards/failure contract) | §7 "New-verb wiring + failure contract" block + GT-Slice-1 guard tests |
| GT-R1-6 (peace/hard-stop rows) | §3.3 four-direction row contract + GT-Slice-2 tests |
| GT-R1-7 (stale sequencing) | header Sequencing block + §9 preamble (verbatim from this note's fix) |
| GT-R1-8 + DC-4 (press-past-zero + voice guard) | §2 **D5** + GT-Slice-V (guard line verbatim) |
| GT-R1-9 (test plan) | GT-Slice-1 PF-3 matrix extension + GT-Slice-3 HTTP-boundary test + GT-Slice-2 determinism/int tests + GT-Slice-4 enumerated editor-test disposition + UX-3 mootness |
| GT-R1-10 (selector cites) | §1 cite fix + §7 per-direction selector rows |
| GT-R1-11 (gold_per_turn capacity) | §4 `gold_per_turn` row |
| GT-R1-12 (voice ordering) | GT-Slice-5 renamed **GT-Slice-V**, lands before/with GT-Slice-3 |
| GT-R1-13 (UX-2/UX-5) | GT-Slice-3 scope + source-pin tests |
| GT-R1-14 (clause cap) | §3.1 cap behavior + named test |
| GT-R1-15 (reason lines) | §3.1 `reason_display` + §7 reasons row + GT-Slice-2 payload |
| GT-A2 (allocation rule) | new **OQ-6**, locked deterministic cheapest-signature rule + voice extension + test |
| GT-A3 (lead with editor blindness) | §1 restructured (blindness is problem #1, live re-scoring the headline win) |
| GT-A4 (REFRONT-9 fold) | OQ-5 → LOCKED; GT-Slice-3 owns the expanded-row breakdown; re-front §14 REFRONT-9 row's landing pointer updated |

Companion doc updates in the same fold: re-front spec §14 REFRONT-9 landing pointer + stale header sequencing line; `STATUS.md` Active Settlement Gate + June 10 session entry; `CLAUDE.md` Guided Terms routing/Design-Gate lines. Run #2 (the final budgeted audit pass) should verify this fold diff only.
