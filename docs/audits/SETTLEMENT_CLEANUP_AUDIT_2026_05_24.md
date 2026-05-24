# Settlement UI Cleanup — Comprehensive Audit (May 24, 2026)

> **Scope:** All landed work on the Settlement UI Cleanup feature (SC-1 through SC-33, G2-Slice-1 through G2-Slice-9, G2-Slice-W1, G2-Slice-6 recovery, G2-Gate4-Repair-1, G2-Slice-1b-Repair-1). 4 parallel audit dimensions: (A) Contract & claim verification, (B) SC-32 / Slice G2 scope discovery, (C) Code quality / tech debt, (D) End-to-end UX.
>
> **Top-line verdict:** The feature is largely in good shape. Every claimed helper, constant, test name, and wiring point in `STATUS.md` exists in code. The biggest gaps are (1) **five Voice Bible §16.1 families authored as hard-coded f-strings instead of resolved templates** (P1 UX), (2) a **float leak** on `balance_post_share` in the forced-alliance toggle differential payload (P1 code), (3) **6 stale test counts** in STATUS.md, and (4) the **SC-32 / Slice G2** decisions required to land or formally cut every remaining hidden affordance.

---

## Section A — Contract & Claim Verification

### A.1 Stale test counts in STATUS.md (P1 doc drift, 6 rows)

Verified by grep `^def test_` per file:

| Suite | STATUS claims | Actual | Fix locations |
|---|---|---|---|
| `tests/test_incoming_offer_deferral_no_leaks.py` | **24** | **28** | `docs/STATUS.md:8`, `:11`, `:70` |
| `tests/test_settlement_pair_substitute_ctas.py` | **17** | **19** | `docs/STATUS.md:12` (DWL row) |
| `tests/test_settlement_dependency_clauses.py` | **36** / **35** | **39** | `docs/STATUS.md:14`, `:32`, `:47` |
| `tests/test_settlement_recurring_gold.py` | **24** / **27** | **27** | `docs/STATUS.md:30` (reconcile to 27) |
| `tests/test_settlement_concession_baseline.py` | **10** / **11** | **16** | `docs/STATUS.md:50`, `:76` |
| `tests/test_settlement_white_peace.py` | **10** | **12** | `docs/STATUS.md:80` |

### A.2 Stale Python line refs in STATUS.md:24 (P2 doc drift, 3 refs)

| Symbol | STATUS says | Actual | Fix |
|---|---|---|---|
| `compute_forced_alliance_continental_toggle_differential` | `settlement_scoring.py:1693` | `:1780` | `docs/STATUS.md:24` |
| `_resolve_pair_state_transitions` | `settlement_preview.py:3545` | `:3487` | `docs/STATUS.md:24` |
| `WorldState._ratify_treaty` | `world_state.py:6537` | `:5974` | `docs/STATUS.md:24` |

### A.3 Stale spec line ref + masthead date (P3 doc drift)

- `docs/STATUS.md:24` says "spec line 783" — actual is **line 785** in `SETTLEMENT_UI_CLEANUP_SPEC.md`.
- `docs/SETTLEMENT_UI_CLEANUP_SPEC.md:8` masthead says "Last spec update: May 15, 2026" — spec body cites May 17, 2026 commit 2 (line 1067). Update masthead to **May 17, 2026** (or May 18 to cover audit-repair).

### A.4 SC-30 required-test-count contradiction (P3 doc drift)

- Spec ledger row at `docs/SETTLEMENT_UI_CLEANUP_SPEC.md:49` lists **5** required tests.
- STATUS DWL row at `docs/STATUS.md:13` says **4** spec required tests.
- Both subsets exist in `tests/test_incoming_offer_deferral_no_leaks.py`. Recommend: list all 5 in STATUS DWL to match the spec.

### A.5 Clean rows (verified, no drift)

- All claimed helpers exist with claimed signatures (`promote_pending_settlement_offers`, `build_incoming_settlement_offer_popup`, `evaluate_pair_peace_substitute_eligibility`, `_compute_surrender_preset`, `process_recurring_settlement_payments`, `compute_forced_alliance_continental_toggle_differential`, `evaluate_war_detail_actionability`, `evaluate_subjugation_eligibility`, `evaluate_vassalage_eligibility`, `evaluate_liberation_eligibility`).
- All claimed constants present at claimed values (`FORCED_ALLIANCE_CONTINENTAL_SYSTEM_THREAT_SURCHARGE=10`, `GOLD_PER_TURN_MIN_AMOUNT=10`, `GOLD_PER_TURN_MIN_TURNS=1`, `GOLD_PER_TURN_MAX_TURNS=20`, `SETTLEMENT_LIVE_CLAUSE_TYPES`, `CLAUSE_CONTROL_SCHEMA`, `PERSISTENT_MAILBOX_TYPES`, `SOFT_STOP_MAILBOX_TYPES`).
- `PopupQueue.PRIORITY_ORDER` length **9** with `incoming_settlement_offer_popup` between `incoming_proposal_popup` and `proposal_result_popup` (`backend/models/cooldown_manager.py:145-155`).
- DWL-SET-SC32 ACTIVE_DEFERRED — spec contains no claim it landed.
- All 4 DWL-SET-SC5 through SC-33 LANDED rows match real code.

---

## Section B — SC-32 / Slice G2 Scope Discovery

### B.1 Authoritative SC-32 contract

`docs/SETTLEMENT_UI_CLEANUP_SPEC.md:648` (gap-inventory row):
> "AI counterproposals, ally petitions/advisories, conference mechanics, veto-like systems, and voluntary alignment offers must either ship with payload/UI/voice/tests or be explicitly removed from player-facing scope in this spec and `docs/STATUS.md`."

Slice budget: **30-42** focused tests across the sub-slice plan (`SETTLEMENT_UI_CLEANUP_SPEC.md:839`).

Spec-named gating test: `test_settlement_agency_landing_ledger_has_no_unowned_backlog_controls` (`SETTLEMENT_UI_CLEANUP_SPEC.md:1260`).

Conference/veto are **pre-committed CUT** unless SC-32 reverses (`SETTLEMENT_UI_CLEANUP_SPEC.md:1256`).

### B.2 Orphan deferrals discovered

| Item | Source | Recommendation |
|---|---|---|
| `wait_for_enemy_offer_visible=False` flag | `settlement_preview.py:5429` | **Assign G2d** (ship or remove) |
| `ask_for_terms_visible=False` flag | `settlement_preview.py:5430` | **Assign G2d** |
| `wait_for_enemy_offer_unavailable` display string | `display_names.py:578` | Remove if G2d CUTs; keep if SHIPs |
| Same-war different-scope replace-confirm chooser | `SETTLEMENT_UI_CLEANUP_SPEC.md:465` | **Assign G2e** (ship — explicitly bounded) |
| "Future voluntary alignment offer needs its own product decision" | `SETTLEMENT_UI_CLEANUP_SPEC.md:266` | **Assign G2f** |
| "Future SC-30b/c slice" wording | `STATUS.md:92` (DWL Notes) | Fold into SC-32 sub-slices (no SC-30b/c row exists) |
| Parent-plan Slice G ally petition taxonomy (6 types) | `WSA_IMPLEMENTATION_PLAN.md:533` | **Assign G2b** (adopt subset, cut rest) |
| `INCOMING_OFFERS_DEFERRED` named flag | `settlement_preview.py:81` | Leave alone — defensive infrastructure |
| `DWL-DIP-CONFERENCE` Congress System | `STATUS.md:105` | Already SUPERSEDED; SC-32 should re-state the cut |

### B.3 Proposed SC-32 sub-slice plan (6 sub-slices, ordered)

1. **G2-Slice-G2a — Cut/keep decision pass** (S, 4-6 tests). Doc-only. Spec/STATUS record SHIP/CUT for every named agency surface. Spec-named test `test_settlement_agency_landing_ledger_has_no_unowned_backlog_controls`.
2. **G2-Slice-G2e — Same-war replace-confirm chooser** (S, 6-8 tests). Player chooses Replace/Keep when restaging different-scope draft. New `settlement_scope_replace_confirm` dialogue type. Smallest, lowest-risk demo of SHIP path.
3. **G2-Slice-G2d — Wait/Ask-for-Terms lifecycle decision** (M ship / S cut). Today the two `_visible=False` flags are structural promises with no lifecycle. SHIP adds `request_terms_state` + subscription; CUT removes the flags and `display_names.py:578` row.
4. **G2-Slice-G2b — Ally petition substrate + 2 petition types** (M, 12-16 tests). New `ally_settlement_petition` dialogue type. Adopt `request_open_settlement` + `warn_against_sellout` from `WSA_IMPLEMENTATION_PLAN.md:533`. Defer/cut the other 4. Allies never ratify or bypass side-leader.
5. **G2-Slice-G2c — AI counterproposal lifecycle decision** (M ship / S cut). Distinct from SC-5 commit-2 player-side `Request Revision` (already shipped). SHIP: AI side-leader counters player-staged-rejected offers within N turns; reuses incoming-offer producer + mailbox. CUT: settlement rejection emits no counter.
6. **G2-Slice-G2f — Voluntary alignment offer decision** (M ship / S cut). Player offers `voluntary_alliance` clause; ratification creates Alliance state with `alliance_origins[pair]="voluntary"`. Largest validator/ratification delta; lands last.

### B.4 Decision points (must resolve before implementation)

1. AI counterproposals: ship (G2c SHIP) or cut (G2c CUT)?
2. Wait-for-Enemy-Offer + Ask-for-Terms: ship lifecycle or formally remove the two flags?
3. Voluntary alignment offers: ship or formally cut?
4. Ally petition coverage: 2 types now + rest deferred, or different subset?
5. Conference/veto: confirm CUT (already pre-committed in spec line 1256)?
6. Same-war replace-confirm chooser: confirm ship?
7. Petitions unsolicited vs solicited?

### B.5 Recommended landing order

**G2a → G2e → G2d → G2b → G2c → G2f.** G2a locks SHIP/CUT outcomes (gates everything). G2e is smallest demo of SHIP path. G2d closes orphan flags before more dialogue types are added. G2b/c grow the agency substrate. G2f lands last (largest clause-system delta).

---

## Section C — Code Quality / Tech Debt

### C.1 Golden rule violations

**P1 — Rule 2 (Floats to Godot) — `balance_post_share` shipped as float to API boundary.**
- `backend/game_logic/settlement_scoring.py:1843` returns `"balance_post_share": float(...)` in `compute_forced_alliance_continental_toggle_differential(...)`.
- Field surfaced at `settlement_preview.py:2913` and `settlement_presentation.py:947`.
- Godot does not yet read the field (no matches), but the docstring at `:1810` advertises it as float.
- **Fix:** expand to `balance_post_share_pct = int(post_share * 100)` or wrap in deliberately-typed sub-dict that popup opts into. Latent crash risk the moment a Godot script reads it raw.

**P2 — Rule 8 (No per-region scans in hot paths) — `_concession_baseline_select_transferable_region`.**
- `backend/game_logic/settlement_preview.py:1269` runs `for name, region in regions.items()` filtering by `region.controller in proposer_set`.
- Not per-turn but per `/diplomatic_preview?mode=settlement` call on losing-side draft. At 1805 scale this iterates hundreds of regions.
- **Fix:** iterate `world.get_nation_regions(participant) for participant in proposer_set` and union. Same pattern already used in `settlement_scoring.py:1589`.

**Clean checks:**
- No LLM in mechanics (zero hits for `llm_client|anthropic|claude` in settlement modules).
- No premature state-clearing.
- `process_recurring_settlement_payments` uses no region scan; iterates only `world.recurring_settlement_payments`.
- All eligibility helpers (`evaluate_war_detail_actionability`, `evaluate_pair_peace_substitute_eligibility`, `evaluate_subjugation_eligibility`) use cached lookups.

### C.2 Comment bloat (style violation)

Task-tracker comments (`# SC-NN`, `# G2-Slice-N`) violate CLAUDE.md's "no WHAT comments" rule. Counts:
- `settlement_preview.py`: **47**
- `settlement_presentation.py`: **12**
- `settlement_scoring.py`: **10**
- `settlement_helpers.py`: **10**
- `settlement_reactions.py`: **4**
- Godot: `proposal_confirm_popup.gd` **9**, `main.gd` **10**

Most could be deleted. A handful that name a spec line (e.g. `spec §6.3 line 1186`) should keep the spec ref but drop the slice tag.

### C.3 Tech debt

- `settlement_helpers.py:1-65` module docstring describes implementation history — belongs in STATUS.md.
- `settlement_preview.py:354` reads `getattr(getattr(world, "dialogue_manager", None), "_queue", [])` — circumvents public API. Add `dialogue_manager.iter_queue()` or `peek_queue()`.
- `INCOMING_OFFERS_DEFERRED` flag comment (`settlement_preview.py:5527-5530`) reads "safety belt: if a future session ever flips it back to True" — open-ended deferral wording. Golden rule 9 prohibits; either delete the flag (SC-5 has landed) or name the landing slice that retires it.
- `_format_concession_reasoning` (`settlement_preview.py:1297`) and `_compute_surrender_preset` reasoning strings (`:1621-1629`) build Talleyrand voice as inline f-strings — see UX P1 finding below.

### C.4 Magic numbers / drift

- `0.08 * (amount * turns / 100)` recurring-gold harshness weight appears inline 3× in `diplomatic_templates.py:2373, 2398, 2410`. Other inline coefficients: 0.1, 0.3, 0.15, 0.4, 0.5. **Fix:** named constants (`GOLD_INDEMNITY_HARSHNESS_PER_100`, etc.) co-located.
- `acceptance_gap * 100` at `settlement_preview.py:1837` — name as `GOLD_PER_ACCEPTANCE_POINT = 100`.
- Recurring-gold `_bounded_int` upper cap `10_000` at `settlement_preview.py:1710-1716` — no constant.

### C.5 Architecture observations (for SC-32 design)

`settlement_preview.py` is **6106 lines**. Clean split candidates:
- `settlement_route.py` — route minting, reopen attempt cap, click resolution (~350 lines, lines 716-1064).
- `settlement_eligibility.py` — all `evaluate_*_eligibility` helpers (~600-700 lines, lines 333-1525).
- `settlement_concession.py` — `_concession_baseline_*`, `_compute_surrender_preset`, `_compute_recurring_gold_preset` (~600 lines, lines 1168-1758).
- `settlement_recurring.py` — payment processor and helpers (~400 lines, lines 5840-6101 + 138-227).

Worth proposing as a refactor slice during SC-32 (e.g., after G2a, before G2e).

`diplomatic_executor.py` at 5297 lines — out of scope for settlement refactor but worth flagging.

Dispatch divergence: `settlement_summary` / `settlement_digest` use their own fog filter (per spec Slice E note). Documented contract, not a bug.

---

## Section D — End-to-End UX

### D.1 Per-fixture findings (6 fixtures)

| Fixture | Status | Key UX findings |
|---|---|---|
| `settlement_multilateral` | Solid | Winning-side authoring delivers 4 preset draft buttons but no free-form clause picker (scoped to SC-32). Acceptance band + top pressure render cleanly. |
| `settlement_losing` | **P1 voice gaps** | Concession baseline draft banner uses hard-coded f-string instead of `settlement_concession_authored_talleyrand` (template missing in `diplomatic_templates.py`). No `settlement_losing_side_pressure_explained_talleyrand` either. |
| `settlement_rejected` | **P1 terminal-recovery gap** | Substitute CTAs and `Open War Detail` route correctly. But `terminal_recovery_copy` (the chancery's "no alternative route" line for dead-end states) is computed backend-side and never rendered by Godot (zero hits for the field in `godot-client/`). |
| `settlement_multiwar_ambiguity` | **P1 no in-wizard rescue** | Wizard disables `Open Settlement` with long inline error text. No "Pick War" sub-step, no clickable rescue. Player must close wizard and use War Status HUD. |
| `settlement_surrender` | **P1 voice not wired** | `settlement_surrender_preset_authored_talleyrand` template exists (`diplomatic_templates.py:1177`) but is **never called** — popup banner uses hard-coded f-string from `_compute_surrender_preset:1621-1628`. Also: double draft banner cluster when preset applies. |
| `settlement_recurring_gold` | **P1 voice not wired** | Same pattern: `settlement_recurring_gold_authored_talleyrand` (`:1241`) exists but never called; banner uses inline f-string from `_compute_recurring_gold_preset:1742-1745`. |

### D.2 Cross-fixture findings

**5 Voice Bible §16.1 families authored as code-side f-strings instead of resolved templates** (P1 unified finding):

| Family | Status | Surface |
|---|---|---|
| `settlement_concession_authored_talleyrand` | **Missing in code** | F2 concession banner |
| `settlement_losing_side_pressure_explained_talleyrand` | **Missing in code** | F2 losing-side empty-draft heading |
| `settlement_surrender_preset_authored_talleyrand` | Exists, never called | F5 surrender banner |
| `settlement_recurring_gold_authored_talleyrand` | Exists, never called | F6 recurring-gold banner |
| `settlement_no_alternative_route_chancery` | Resolved backend, never displayed in popup | F3 dead-end terminal copy |

Also missing template entries: `settlement_white_peace_heading_talleyrand` (referenced at `preview.py:2541` but no template — falls through to default), `settlement_white_peace_blocked_talleyrand` (`:2548` — same).

**Other findings:**
- **Authoring agency narrow.** 4-5 preset buttons (Demand Gold, Demand Gold Over Time, Re-author w/ Concessions, Author Surrender, Offer Gold Over Time). No free-form clause picker — scoped to SC-32.
- **Incoming-offer popup ignores non-gold clauses.** `build_incoming_settlement_offer_popup` only formats `peace` and `gold_indemnity` cleanly; others fall through to `ttype.replace("_", " ").title()`. Voice templates also only slot `amount`. Region cessions or forced alliance clauses render misleadingly.
- **Empty `Demand Gold` flows hardcoded.** `author_gold_indemnity_terms` (200) and `author_gold_per_turn_terms` (50/3) at `settlement_preview.py:4368-4406` cannot be tuned. Acceptable for current scope (SC-32 owns broader authoring).
- **No raw-key leaks observed** in any rendered popup path. Component names route through `ACCEPTANCE_COMPONENT_DISPLAY`, warning codes through `WARNING_CODE_DISPLAY`. Good.
- **Same-war draft preservation** consistent across re-author + substitute-CTA flows.

### D.3 Severity-tagged punch list

- **P1** — 5 §16.1 voice families not wired (D.2 table). Fix in `_compute_*_preset` calls + add 2 missing templates.
- **P1** — `terminal_recovery_copy` never rendered in Godot (`proposal_confirm_popup.gd:_build_settlement_content`). Add a block rendering it after `ratify_blocked_reason`.
- **P1** — Multi-war ambiguity has no in-wizard rescue. Add "Pick War" sub-step or "Open War Status" link.
- **P2** — Surrender double banner (`proposal_confirm_popup.gd:364-375`).
- **P2** — Incoming-offer popup ignores non-gold clauses.
- **P2** — Empty Demand Gold flows hardcoded (acceptable scope).
- **P3** — "Top pressure" line under "Acceptable" band reads as conflicting. Cosmetic.

---

## Aggregate Severity Summary

| Severity | Count | Owners |
|---|---|---|
| P1 | **9** | Code: 1 (float leak). UX: 5 voice + 1 recovery + 1 multi-war + 1 missing templates. |
| P2 | **6** | Code: 1 (region scan). UX: 3 (surrender double-banner, incoming-offer clauses, hardcoded amounts). Doc: 2 (line-refs, masthead). |
| P3 | **7** | Mostly doc drift + cosmetic. |
| **Total** | **22** | |

## Recommended fix order

1. **Doc drift sweep** (P1+P2 doc, ~10 minutes of Edits). Bump 6 test counts, fix 3 Python line-refs, fix 1 spec line-ref, update spec masthead, reconcile SC-30 test count. No code changes; just brings docs back in sync with reality.
2. **Voice wiring fix** (P1 UX, ~1-2 hours). Author 2 missing templates, route 3 hard-coded f-strings through the existing template resolver. Pure refactor — no new behavior.
3. **`terminal_recovery_copy` render** (P1 UX, ~30 min). Single Godot block in `proposal_confirm_popup.gd`.
4. **`balance_post_share` float fix** (P1 code, ~20 min). Latent crash prevention.
5. **Multi-war ambiguity wizard rescue** (P1 UX, ~1-2 hours). Add a "Pick War" sub-step or clickable rescue.
6. **Concession baseline region scan** (P2 code, ~30 min). Single-loop replacement.
7. **SC-32 / Slice G2 planning** (separate work session). User answers 7 decision points, then implementation slices land per recommended order.

Tech-debt items (comment bloat, magic numbers, `settlement_preview.py` split) are best folded into SC-32 sub-slices rather than bundled into a standalone refactor commit.
