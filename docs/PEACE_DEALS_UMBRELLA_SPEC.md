# Peace Deals — Umbrella Spec

> **Status:** Draft v1.0
> **Date:** April 25, 2026
> **Phase placement:** After Memory and Pressure v2.4.3 (complete). Before Ally Participation + Common Peace.
> **Companion docs:** `BILATERAL_PEACE_HARDENING_SPEC.md`, `WAR_PURPOSE_SCORE_SEMANTICS_SPEC.md`, `WAR_BARGAIN_SPEC.md`, `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` (deferred follow-up)

---

## 1. Purpose

This spec is the umbrella for the Peace Deals phase. It defines the implementation order, dependency graph, cross-cutting decisions, milestone gates, and deferred carry-forward checklist that the four sub-specs do not individually own.

The three implementation-ready sub-specs are:

- **Bilateral Peace Hardening (BPH)** — make the existing bilateral peace flow legible, previewable, and politically consequential.
- **War Purpose + Score Semantics (WPS)** — give wars declared purpose, ticking score, settlement tiers, forced alliance, liberation, and a vassalage power cap.
- **War Bargains (WB)** — add a named-enemy bilateral promise mechanic with lifecycle, ally-entry integration, and breach/fulfillment consequences.

The fourth doc, **War Settlement + Ally Participation**, is a deferred follow-up draft. It is explicitly out of scope for this phase but must be accounted for in interface design.

---

## 2. What Peace Deals is NOT

- Not multi-party peace. Common peace, ally beneficiaries, contribution-based settlement, and conference flow belong to Ally Participation (later phase).
- Not a mechanics rewrite. The existing acceptance formula, pairwise war state, and bilateral treaty system remain intact. Peace Deals makes them honest.
- Not a new diplomatic action vocabulary. BPH adds zero new verbs. WPS adds one clause type (`forced_alliance`) and one popup (War Purpose). WB adds one clause type (`war_bargain`) and one action (`repudiate_bargain`).

---

## 3. Dependency Graph

```
Memory and Pressure v2.4.3 (COMPLETE)
         │
         ├──► BPH ─────────┐
         │                  ├──► WB-A/B/C ──► WB-D
         └──► WPS ─────────┘
                                              │
                                              ▼
                                    Ally Participation
                                    (later phase)
```

**BPH and WPS are parallel-safe.** BPH R5 says "either order works." WPS §14.3 extends BPH §8.1 with optional fields. Neither blocks the other for implementation. Interleaving their slices saves sessions.

**WB is hard-gated on both BPH and WPS.** WB needs BPH's peace-breach warning plumbing (WB R4) and WPS's war-objective settlement hook (WB §2).

**WB-D (bargain presentation) is gated on WB-A/B/C.** Spotlights, split-voice copy, and response routes require live bargain state.

**Ally Participation is gated on the full Peace Deals phase.** It cannot start until bilateral peace is legible (BPH), wars have purpose (WPS), and bargains work mechanically (WB-A/B/C).

---

## 4. Cross-Cutting Decisions

### 4.1 Armistice duration: canonized at 5 turns

DIPLOMACY_SPEC is internally inconsistent: §5a/§5b.2/§7d say 5 turns, but the turn-order processing, EC-Z, and design decisions table say 3 turns. Both BPH §12.2 and WB R6 flag this without resolving it.

**Resolution:** 5 turns is canonical. Code already uses 5 (`_process_armistice_expiration` at `diplomacy.py:5188` checks `turns < 5`; `armistice_cooldowns` are set to 5). The conflicting "3 turn" doc references in DIPLOMACY_SPEC must be corrected as a cleanup task before or during BPH-A.

This affects:
- BPH §12.1 armistice preview (reads whatever `ARMISTICE_MIN_TURNS` the code uses — that's 5)
- WPS §7.6 ticking pause during armistice (pauses for the full 5 turns)
- WB §8.9.B zombie clock (counts turns at ARMISTICE; 5-turn minimum means zombie clock cannot fire before armistice expires unless both sides reach ARMISTICE simultaneously through separate paths)

### 4.2 Acceptance modifier reconciliation (canonical)

Earlier WAR_BARGAIN_SPEC drafts referenced the superseded rivalry-based modifier model. WAR_BARGAIN_SPEC §7.2 and §9 now align with this canonical model; this umbrella section remains the source of truth if future wording drifts.

The Memory and Pressure v2.4.3 hegemony refactor superseded the rivalry-based modifier model. The live acceptance layer in `calculate_acceptance()` (`diplomacy.py:3215-3409`) is:

| Modifier | Source | Range | Description |
|----------|--------|-------|-------------|
| `hegemony_target_mod` | B-B1-lite | per-pair | Cross-bloc friction starting at 30% share |
| `bilateral_betrayal_mod` | v2.4.3 substrate | per-pair | Graduated penalty from active betrayal strikes |
| `grievance_modifier` | B-B4 | per-pair | -30 per active durable grievance flag, cap -90 |
| composite floor | B-B4 | synthetic | `max(-60, hegemony + betrayal + grievance)` |

There is no legacy rivalry composite in the codebase. The older modifier names belong to a superseded spec revision.

**WB-A integration:**

WAR_BARGAIN_SPEC §9.1 (`bargain_value_mod`) and §9.2 (`bargain_conflict_penalty`) extend the live model:

- `bargain_value_mod` (+10/+15/+25) integrates as a fourth political-pressure term alongside the existing three. It is positive (sweetener), so it naturally counteracts the negative political pressure from hegemony/betrayal/grievance.
- `bargain_conflict_penalty` (§9.2, `-8` for a live bargain against target) feeds into the political subtotal before the composite floor clamp. The floor of `-60` still applies.
- §9.3 composite re-cap references the live `-60` floor.

Updated political subtotal:

```python
political_subtotal_raw = (
    hegemony_target
    + bilateral_betrayal
    + grievance
    + bargain_conflict_penalty   # NEW: -8 when live bargain targets this nation
    + bargain_value_mod           # NEW: +10/+15/+25 sweetener
)
political_subtotal_clamped = max(-60, political_subtotal_raw)
```

The `war_entry_score` (WB §9.4) is a separate dedicated formula for ally-entry evaluation, not an extension of `calculate_acceptance()`. It remains as specified, with the understanding that its `bilateral betrayal strikes: -8 each, cap -24` term reads from the same `betrayal_history` store that `bilateral_betrayal_mod` reads from.

### 4.3 `threat_coalition` compatibility layer

`threat_coalition` remains in the diplomatic ledger payload as a compatibility layer beside the live `balance_of_europe` payload (per STATUS.md April 25, 2026).

**Decision:** Do not retire `threat_coalition` during BPH or WPS. Schedule a compatibility retirement decision after Gate 2 (BPH + WPS complete), before the first WB ledger expansion. At that point, either:

- Retire it in a focused cleanup pass (preferred if playtest confirms `balance_of_europe` carries the information)
- Carry it through WB with explicit compatibility tests

This prevents the Peace Deals phase from accumulating a third parallel ledger payload.

### 4.4 Godot surface strategy

Each sub-spec has Godot work: BPH changes the wizard confirmation step, WPS adds a War Purpose popup, WB adds a Bargain Review stage and counter-bargain blocking mode.

**Strategy:** Backend-first per slice, Godot per slice. Each slice lands backend logic and curl-verifies the endpoint before touching Godot. This matches the project's established pattern (curl test BEFORE assuming Godot is broken) and mitigates the known risk of agent errors in .gd bulk replacements.

Godot work per slice:
- BPH-A: Render annotated terms in wizard confirmation step
- BPH-B: Replace generic confirmation with Peace Preview Panel for peace proposals
- BPH-C: Wire warnings into Peace Preview Panel Section 3
- BPH-D: Render ratification summary, dispatch integration
- WPS-A: War Purpose popup at declaration time (CanvasLayer 110, modal)
- WPS-B: Power cap display in wizard and War Purpose popup
- WPS-C: Forced alliance / liberation UI surface changes
- WPS-D: War Status Panel extension (objective, ticking, tier), tier mismatch warnings
- WB-C: Bargain Review stage in proposal_confirm, counter-bargain blocking mode, war-entry preview
- WB-D: Spotlight/split-voice rendering, response routes

### 4.5 Save format migration

All new WorldState fields use `.get(key, default)` migration. No destructive save-format changes. Pre-Peace-Deals saves load cleanly with empty defaults.

Cumulative new WorldState fields:

| Field | Spec | Slice | Default |
|-------|------|-------|---------|
| `peace_ratification_log: List[Dict]` | BPH §14.1 | BPH-D | `[]` |
| `war_objectives: Dict[str, Dict]` | WPS §12.1 | WPS-A | `{}` |
| `alliance_origins: Dict[str, str]` | WPS §12.1 | WPS-C | `{}` |
| `diplomatic_commitments: Dict[str, Dict]` | WB §12.1 | WB-A | `{}` |
| `next_commitment_id: int` | WB §12.1 | WB-A | `0` |

Already shipped fields consumed by Peace Deals (no migration needed):
- `betrayal_history`, `next_episode_id`, `reparations_cooldown`, `anti_renewal_cooldown` (Memory and Pressure v2.4.3)

Each slice that adds fields must update `SAVE_FORMAT_REFERENCE.md` and pass `test_serialization_enforcement.py`.

---

## 5. Implementation Sequence

### Phase A: Bilateral legibility (BPH + WPS, parallel-safe)

BPH and WPS slices can be interleaved. No ordering constraint between them.

**BPH-A: Term ownership + display labels (~15 tests)**
- Annotated clause model with `from_nation`, `to_nation`, `term_direction`, `display_label`
- Display label generation for all clause types
- `peace_ratified` campaign log event type
- Prerequisite cleanup: fix DIPLOMACY_SPEC armistice duration references to 5 turns

**BPH-B: Peace preview panel + war context (~18 tests)**
- War context snapshot at proposal time
- Extend `GET /diplomatic_preview` for peace-class proposals
- Godot: Peace Preview Panel in wizard (war summary + terms review + empty consequences section)
- Armistice preview additions

**BPH-C: Fallout preview + commitment conflicts (~20 tests)**
- Separate-peace ally fallout warnings with severity bands
- `get_peace_commitment_conflicts()` interface (paradox + hegemony conflict types for now)
- Strategic order cancellation preview
- Relation penalty on ratification

**BPH-D: Ratification summary + dispatch (~12 tests)**
- `peace_ratification_summary` generation
- `peace_ratification_log` on WorldState with serialization
- Morning Dispatch peace settlement section
- AI peace proposal enrichment
- Armistice expiration dispatch warning

**WPS-A: War objectives + ticking score (~22 tests)**
- `war_objectives` on WorldState with serialization
- Five objective types (conquest, subjugation, forced_alliance, defense, liberation)
- War Purpose popup at declaration time
- Ticking accumulation in `advance_turn()`
- Ticking as 5th war score component
- Armistice ticking pause

**WPS-B: Vassalage power cap (~15 tests)**
- `calculate_national_power()` function
- Hard gate on treaty and conquest vassalage
- Post-cession power evaluation
- Power cap display in wizard and War Purpose popup

**WPS-C: Forced alliance + liberation (~20 tests)**
- `forced_alliance` clause type + ratification mechanics
- `alliance_origins` tracking with serialization
- Auto-downgrade pressure (-10/turn relation drift)
- Threat generation (+15)
- `liberation` clause type + ratification mechanics
- Coalition liberation interaction

**WPS-D: War score legibility + AI + surface polish (~18 tests)**
- Settlement tier mapping and display
- War Status Panel extension
- Peace preview extension with objective + tier data
- Tier mismatch warnings
- AI peace timing with ticking pressure

**Phase A total: ~140 tests, ~7 sessions**

### Gate 1: BPH + WPS complete

Required before WB begins. See §7 for gate criteria.

### Compatibility decision: `threat_coalition` retirement

Evaluate after Gate 1. Decide: retire in focused cleanup, or carry through WB with tests.

### Phase B: War Bargains (WB, gated on Phase A)

**WB-A: Data model + creation + validation (~22 tests)**
- `diplomatic_commitments` + `next_commitment_id` on WorldState with serialization
- `war_bargain` clause type in acceptance/display
- Bargain validation (named enemy, claim region, caps, contradictions)
- Activate `region_observer` witness scope branch
- **Acceptance modifier reconciliation:** integrate `bargain_value_mod` and `bargain_conflict_penalty` into the live `calculate_acceptance()` political subtotal per §4.2 above

**WB-B: Lifecycle — fulfillment + breach + void (~32 tests)**
- Status transitions (active → triggered → fulfilled / void / breached)
- Zombie-bargain void clock with serialized counter
- Fulfillment check in `advance_turn()` per turn-order rule
- `fulfillment_snapshot` write
- Breach detection (treaty break, normalization, contradictory bargain, repudiate)
- Void detection (counterparty_reversal vs obsolescence_or_external)
- Cooldowns (6-turn breach, 4-turn void)
- Dispatch + campaign log events

**WB-C: War-entry integration + Bargain Review + AI (~52 tests)**
- Bargain picker in diplomacy wizard
- Mandatory Bargain Review stage in proposal_confirm
- Offensive ally-entry `join_opportunity` surface (replaces silent cascade)
- Defensive honor call handling
- `war_entry_counter_bargain` flow with blocking mode
- `war_entry_score` dedicated formula
- Counter-bargain reroll determinism
- AI bargain generation, anti-spam, refusal behavior
- Ledger: live bargains display
- `repudiate_bargain` confirm surface

**Phase B total: ~106 tests, ~3-4 sessions**

### Gate 2: WB-A/B/C complete

Required before WB-D and before Ally Participation planning. See §7 for gate criteria.

### Phase C: Bargain presentation (WB-D, gated on Phase B)

**WB-D: Bargain-era presentation extension (~18 tests)**
- `bargain_fulfilled` spotlight + Talleyrand vindication + N+1 callback
- `bargain_breached` split-voice spotlight + N+1 aftermath
- `dominant_witness_scope`-branched breach copy
- Response routes (Propose redress / Deepen the bond / Attempt to reopen the chancery)
- Bargain ratified/triggered/voided notices with period labels

**Phase C total: ~18 tests, ~1 session**

### Total budget: ~264 tests, ~11-12 sessions

---

## 6. Deferred Carry-Forward Checklist

Every item deferred from Memory and Pressure v2.4.3 or identified during Peace Deals design that does not land in the implementation sequence above must be tracked here. No item may vanish as vague "later polish."

### Items with concrete slice assignments (will ship in Peace Deals)

| Item | Assigned Slice | Notes |
|------|---------------|-------|
| Region-observer witness scope activation | WB-A | WB §12.4 — stub exists in substrate, lights up when bargain store exists |
| Bargain creation / validation | WB-A | WB §8.1–§8.5 |
| Bargain lifecycle (fulfillment / breach / void) | WB-B | WB §8.8–§8.9 |
| War-entry decision surface (replaces silent cascade) | WB-C | WB §8.7 |
| Bargain Review mandatory surface | WB-C | WB §10.1 |
| `bargain_value_mod` acceptance integration | WB-A | §4.2 reconciliation above |
| Bargain fulfillment/breach spotlights | WB-D | WB §10.5 |
| Scope-branched witness copy for bargain breach | WB-D | WB §10.5 |
| Response routes (redress / deepen / reopen chancery) | WB-D | WB §10.5 |
| Bargain ratified/triggered/voided notices | WB-D | WB §10.5 |

### Items explicitly deferred to Ally Participation (later phase)

| Item | Rationale |
|------|-----------|
| Ally-beneficiary land promises ("Prussia gets Saxony") | Requires common peace and contribution tracking (WAR_SETTLEMENT spec §13) |
| Common peace / conference settlement flow | Requires war_instance grouping, contribution scores, settlement shares (WAR_SETTLEMENT spec §7–§12) |
| Multi-party settlement allocation | Cannot work without ally seat/consult/beneficiary model (WAR_SETTLEMENT spec §11) |
| Settlement grievance (`shut_out_in_settlement`) | Requires contribution tracking to evaluate "shut out" (WAR_SETTLEMENT spec §14) |
| War contribution score (`war_contribution_score`) | New per-ally settlement number; bilateral phase does not need it (WAR_SETTLEMENT spec §9) |
| `war_instance` grouping container | Groups bilateral wars into one political conflict; bilateral phase works pairwise (WAR_SETTLEMENT spec §7) |
| Extended battle records with multi-participant attribution | Requires contribution tracking (WAR_SETTLEMENT spec §9.4) |

### Items explicitly deferred to later phases (not Peace Deals, not Ally Participation)

| Item | Target Phase | Rationale |
|------|-------------|-----------|
| D1 advisory-first strategy | Nation Agendas | Strategic advisory surface, not peace mechanics |
| D2 non-France-hegemon generalization | Scale / Scenario | Requires multi-scenario testing with non-France player |
| Dynamic power tiers (runtime recomputation) | Nation Agendas | `power_tier` stays authored scenario data per Phase 0 taxonomy |
| Multi-objective wars | War System v2 | Complexity not justified in v0.1 (WPS §4) |
| AI-chosen offensive war objectives | War System v2 | Conquest/Subjugation/Forced Alliance are the player's toolkit (WPS §13.1) |
| Coalition generalization (non-France war_bloc actors) | Coalition v2 | WB §7.3 keeps helpers parameterized for this |
| AI-to-AI bargains | War Bargains v2 | Excluded in v0.1 (WB §6) |
| Bargain icons (Godot visual assets) | Peace Deals polish | No icon art exists; functional UI ships first |
| War bargain deadline / suspension model | Cut | WB §15 Gate 4 resolved: no deadlines, no suspension |

### Items requiring design decision before implementation

| Item | Decision Point | Options |
|------|---------------|---------|
| `threat_coalition` retirement | After Gate 1 (BPH + WPS complete) | Retire in cleanup pass OR carry through WB with tests |
| Bargain presentation voice (WB-D diplomat attribution) | Before WB-D starts | Confirm Voice Bible coverage for bargain-specific lines |

---

## 7. Milestone Gates

### Gate 1: Bilateral peace is legible + wars have purpose (after BPH + WPS)

**Required before WB-A begins.**

Smoke criteria:

1. **Term ownership:** `curl POST /command` with a peace proposal returns `annotated_terms` where every clause has `from_nation`, `to_nation`, `display_label`.
2. **Peace preview:** `curl GET /diplomatic_preview` for a WAR→PEACE proposal returns `war_context_snapshot` with war score components, battle record, and regions held.
3. **Fallout warnings:** Separate peace proposal against a nation whose ally is still fighting returns `fallout_warnings` with severity bands.
4. **Ratification summary:** Peace ratification response includes `peace_ratification_summary` with `war_outcome` classification.
5. **War Purpose popup:** War declaration flow opens objective selection; Subjugation is unavailable for Austria at game start (power 59% > 50% cap).
6. **Ticking score:** After declaring Conquest against Prussia and holding Berlin for 3 turns, `war_score` includes a positive ticking component.
7. **Settlement tiers:** War Status Panel shows named tier ("Dictated Terms") alongside numeric score.
8. **Forced alliance:** `forced_alliance` clause ratification jumps state to ALLIANCE, resets relation to 0, and adds origin tag.
9. **No regressions:** Full test suite green. Existing acceptance formula, coalition formation, and diplomatic ledger tests pass unchanged.

### Gate 2: Bargains work mechanically (after WB-A/B/C)

**Required before WB-D and before Ally Participation planning begins.**

Smoke criteria:

1. **Bargain creation:** Alliance treaty with `war_bargain` clause creates a tracked commitment in `diplomatic_commitments`.
2. **Bargain trigger:** Co-belligerence against named enemy transitions bargain to `triggered`.
3. **Bargain fulfillment:** France captures claimed region while bargain is triggered → `fulfilled` + `fulfillment_snapshot`.
4. **Bargain breach:** Peace with named enemy after surfaced warning → `breached` + relation penalty + reliability loss + cooldown.
5. **Bargain void:** Beneficiary breaks source treaty → `void` (counterparty_reversal) + no French penalty.
6. **Counter-bargain:** Offensive ally-entry with ally in 25-49 war_entry_score band opens counter-bargain flow.
7. **War entry score:** `+25` bonus when valid bargain targets named enemy shifts ally from counter-bargain to join band.
8. **Acceptance integration:** `bargain_value_mod` and `bargain_conflict_penalty` appear in `calculate_acceptance()` components.
9. **Ledger:** Diplomatic Ledger shows live bargains with named enemy, claim region, status.
10. **Save/load:** All new WorldState fields survive round-trip. Pre-Peace-Deals saves load with empty defaults.
11. **No regressions:** Full test suite green.

### Phase gate: Peace Deals complete (after WB-D)

**Required before Ally Participation can begin.**

Smoke criteria:

1. **Integrated scenario (10-turn playtest path):**
   - Declare war with Conquest objective against Prussia
   - Create bargain with Austria (named enemy: Prussia, claim: Berlin) in alliance treaty
   - Hold Berlin for 5 turns → ticking accumulates
   - Austria enters war as co-belligerent → bargain triggers
   - France captures Berlin → bargain fulfills
   - Sign peace with enriched preview showing term ownership + war context + ally fallout + settlement tier
   - Ratification summary shows war outcome
   - Campaign log shows complete trail: objective declared → ticking started → bargain ratified → bargain triggered → bargain fulfilled → peace ratified
2. **Breach scenario:** Sign peace with named enemy while bargain is active → breach fires with relation penalty, reliability loss, campaign log entry.
3. **Forced alliance scenario:** Declare war with Forced Alliance objective → hold capital → propose forced alliance clause → ratification jumps to ALLIANCE + Continental System.
4. **WB-D presentation:** Bargain fulfillment and breach events render with spotlight/split-voice copy and offer response routes.
5. **All gates 1-2 criteria still hold.**
6. **Full test suite green. No regressions in any existing system.**

---

## 8. Risks

### R1. Forced alliance is the highest-coupling addition

WPS-C's `forced_alliance` clause touches the acceptance formula, diplomatic state machine (state jump to ALLIANCE), threat system (+15), and Continental System simultaneously. The deep diplomacy audit (March 22, 2026) found 43 bugs in the existing system — forced alliance will probe every interaction boundary.

**Mitigation:** WPS-C gets the most thorough test coverage of any slice. Gate 1 explicitly tests forced alliance ratification. Consider a mini-playtest after WPS-C lands before continuing to WPS-D.

### R2. WB-C is the largest single slice

WB-C (war-entry integration + Bargain Review + AI) is estimated at 52 tests and touches multiple systems: diplomacy wizard, proposal_confirm flow, ally-entry pipeline, war_entry_score formula, AI proposal generation, ledger display. This is the riskiest slice for scope creep.

**Mitigation:** WB-C can be sub-divided if needed: (C1) war-entry pipeline + join_opportunity + defensive honor, (C2) counter-bargain flow + reroll determinism, (C3) AI rules + ledger + repudiate. Budget flexibility: 52 tests total, but sub-slice boundaries are natural if the slice proves too large.

### R3. BPH and WPS parallel execution creates merge friction

If BPH and WPS are implemented in the same session, they may touch overlapping files (diplomatic_executor.py, diplomacy.py). Merge conflicts are unlikely (they modify different sections) but possible.

**Mitigation:** Interleave at the slice level, not within a slice. Complete BPH-A, then WPS-A, then BPH-B, etc. Never have two incomplete slices in flight.

File-level partition guidance:

- BPH owns peace-preview enrichment helpers such as `_enrich_peace_proposal()`, `_build_peace_preview()`, `_build_fallout_warnings()`, and term annotation / ratification-summary plumbing.
- WPS owns war-objective and settlement-legibility helpers such as `_validate_war_objective()`, ticking-score accumulation, power-cap validation, and `_execute_forced_alliance_clause()`.
- Shared files (`diplomatic_executor.py`, `diplomacy.py`, `world_state.py`) should be touched by only one active slice at a time; if BPH and WPS are worked by separate agents, they should split by the helper ownership above and merge one completed slice before starting the next.

### R4. Acceptance modifier reconciliation may reveal formula balance issues

Adding `bargain_value_mod` (+10/+15/+25) and `bargain_conflict_penalty` (-8) to the political subtotal changes the acceptance landscape. The +25 war-entry sweetener is particularly powerful.

**Mitigation:** The composite floor at -60 caps downside. The +25 is intentionally large — it's the whole point of making a political promise. Test coverage must verify that the floor still functions correctly with 5 terms instead of 3 feeding into it.

### R5. War Purpose popup creates analysis paralysis risk

Three objectives (plus greyed Subjugation) at declaration time may slow the game down. WPS §16 R5 already acknowledges this.

**Mitigation:** Objectives are simple single-sentence descriptions. The popup is one choice, not a configuration screen. Playtest at Gate 1 will reveal whether this is actually a problem.

---

## 9. Sub-Spec Errata

Items in the sub-specs that this umbrella supersedes, corrects, or has reconciled:

### WAR_BARGAIN_SPEC.md

- **§7.2 "Implementation note"** — reconciled to the live `hegemony_target_mod` + `bilateral_betrayal_mod` + `grievance_modifier` model with composite floor at -60. See §4.2 above.
- **§9.2** — reconciled as `bargain_conflict_penalty` feeding into the live political subtotal.
- **§9.3** — reconciled to the live `-60` composite floor and inline political subtotal used by `calculate_acceptance()`.
- **§7.2 "commitment_paradox rename"** — already shipped (B-B3). No longer a prerequisite.

### WAR_PURPOSE_SCORE_SEMANTICS_SPEC.md

- **§8.1 `calculate_national_power()`** — the implementation should avoid iterating `world.regions.values()` in a hot path per CLAUDE.md Golden Rule 8. Cache the result if called more than once per turn, or compute only at vassalage-proposal time as the spec already suggests.

### BILATERAL_PEACE_HARDENING_SPEC.md

- **§12.2** — armistice duration contradiction resolved: 5 turns is canonical. See §4.1 above.

---

## 10. Resolved Design Calls

- **BPH ∥ WPS parallel execution:** Yes. No hard dependency between them. Interleave at slice level.
- **WB gated on both BPH and WPS:** Yes. WB R4 + WB §2 are hard dependencies.
- **Acceptance modifier reconciliation approach:** Extend the live model (hegemony + betrayal + grievance + floor). Do not resurrect the legacy rivalry-composite model.
- **Armistice duration:** 5 turns. Fix docs, do not change code.
- **`threat_coalition` retirement timing:** After Gate 1, before first WB ledger expansion. Not during BPH or WPS.
- **Godot strategy:** Backend-first per slice, curl-verify, then Godot per slice.
- **Save migration:** All `.get(key, default)` pattern. No destructive changes.
- **Ally Participation timing:** After full Peace Deals phase gate. Not interleaved.

---

## 11. Changelog

- **April 25, 2026** — v1.0 drafted. Covers dependency graph, 3-phase implementation sequence (BPH+WPS parallel → WB-A/B/C → WB-D), cross-cutting decisions (armistice canonized at 5 turns, acceptance modifier reconciliation against live v2.4.3 model, threat_coalition retirement scheduling, Godot surface strategy, cumulative data model delta), deferred carry-forward checklist with concrete slice assignments, 3 milestone gates with smoke criteria, 5 risks, sub-spec errata for stale WAR_BARGAIN_SPEC references. Total budget: ~264 tests, ~11-12 sessions.
