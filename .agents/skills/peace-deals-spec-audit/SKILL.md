---
name: peace-deals-spec-audit
description: Repeatable audit of the Peace Deals spec suite. Scores Fun, Clarity, Work Segmentation, Contradiction-Freedom, and Completeness. Outputs numbered findings with fix steps and ends with GO / NO-GO. Run N times until all metrics hit threshold.
---

# Peace Deals Spec Audit

Run this audit against the Peace Deals spec suite to evaluate readiness for implementation. Each run produces a scored report with actionable findings. Repeat until all metrics pass.

## Audit Scope

Read these docs (in this order):

1. `docs/PEACE_DEALS_UMBRELLA_SPEC.md` (umbrella — dependency graph, gates, cross-cutting decisions)
2. `docs/BILATERAL_PEACE_HARDENING_SPEC.md` (BPH)
3. `docs/WAR_PURPOSE_SCORE_SEMANTICS_SPEC.md` (WPS)
4. `docs/WAR_BARGAIN_SPEC.md` (WB)
5. `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` (ally-aware settlement mechanics and historical implementation handoff)
6. `docs/SETTLEMENT_UI_CLEANUP_SPEC.md` (active cleanup readiness: routes, recovery, action visibility, incoming-offer exposure, Gate 4 smoke)
7. `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` (WSA executable slice order, test allocation, file ownership, gates)
8. `docs/STATUS.md` (landed counts, current cleanup status, gate records)

Also read for cross-doc consistency:

9. `docs/DIPLOMACY_SPEC.md` (acceptance formula, war score, diplomatic states)
10. `docs/COALITION_SPEC.md` (threat, coalition formation, balance of europe)
11. `docs/RELIABILITY_COMMITMENTS_SPEC.md` (betrayal memory, hegemony, acceptance modifiers)
12. `CLAUDE.md` (golden rules, modification patterns, file reference)

And verify against live code:

13. `backend/game_logic/diplomacy.py` — `calculate_acceptance()` components, `_process_armistice_expiration()`, war score formula
14. `backend/models/world_state.py` — existing serialization fields, `advance_turn()` processing order

Current-readiness audits must include every file above. If a run intentionally omits the cleanup spec, `STATUS.md`, or the WSA implementation plan, the verdict is limited to historical Peace Deals mechanics and must not claim cleanup-readiness GO.

## Metrics

Score each metric on a 1-10 scale. **Passing threshold: every metric >= 7. GO requires all five passing.**

### M1: Fun (1-10)

Does the spec suite produce gameplay that feels like Napoleon dictating or conceding terms?

Evaluate:
- Does the War Purpose popup create a meaningful choice moment, or is it just clicking through?
- Does ticking war score reward aggressive play without making wars drag?
- Does forced alliance feel like a historically resonant power move?
- Does the bargain mechanic create real "will I honor this?" tension?
- Does the peace preview make the player feel informed, not overwhelmed?
- Does the separate-peace fallout create genuine political drama?
- Is there at least one "I can't believe I can do that" moment in the design?
- Is there at least one "I regret doing that" consequence loop?

**Score 7+ requires:** At least 6 of 8 checks pass. The design creates both agency and consequence.

**Score < 5 means:** The system is mechanically correct but emotionally flat. Peace feels like paperwork.

### M2: Clarity (1-10)

Can an implementer read the specs and know exactly what to build without asking questions?

Evaluate:
- Every new data field has: name, type, default, serialization rule, and which slice adds it
- Every new endpoint change has: request shape, response shape, and which existing endpoint it extends
- Every formula has: all inputs named, all constants valued, edge cases specified (division by zero, empty collections, self-reference)
- Every UI surface has: what triggers it, what it shows, what actions dismiss it, which CanvasLayer
- Every campaign log / dispatch / notification event has: event type name, payload shape, one-liner format, fog rule
- No "TBD", "to be determined", "may", or "consider" in implementation-critical sections
- Cross-doc references are bidirectional (A references B, B references A)
- The umbrella spec's errata section covers every stale reference in sub-specs

**Score 7+ requires:** An implementer could write the first 20 tests from the specs alone without reading existing code beyond what the specs cite.

**Score < 5 means:** The specs describe intent but not behavior. Implementation will require constant design clarification.

### M3: Work Segmentation (1-10)

Are slices independently shippable, testable, and sized for single sessions?

Evaluate:
- Every slice has: a name, a test count estimate, a clear "done" definition
- No slice depends on an unfinished slice within the same phase (BPH-C should not need unfinished BPH-B state)
- No slice exceeds ~55 tests (the project's observed single-session ceiling is ~50-55 tests)
- The dependency graph has no hidden edges (slice X doesn't secretly need slice Y's data)
- Godot work is scoped per slice, not batched into a "do all Godot at the end" blob
- Each gate has concrete smoke criteria, not just "tests pass"
- The parallel BPH/WPS interleaving is safe: no file-level merge conflicts between any BPH slice and any WPS slice
- WB-C (52 tests) has explicit sub-division guidance for splitting if too large

**Score 7+ requires:** Every slice could be implemented by a different agent in a different session without coordination beyond reading the specs.

**Score < 5 means:** Slices have hidden coupling. Implementing one will break or block another.

### M4: Contradiction-Freedom (1-10)

Do the specs agree with each other and with the live codebase?

Evaluate:
- **Acceptance formula:** Every spec that references acceptance modifiers names the same terms as `calculate_acceptance()` in `diplomacy.py`. No implementation-critical references to dead modifiers (`direct_rivalry_mod`, `rival_conflict_mod`, `direct_concern_mod`, `concern_conflict_mod`, `political_commitment_mod`).
- **Armistice duration:** Every spec that references armistice timing agrees with the canonical 5-turn value and with `_process_armistice_expiration()`.
- **War score formula:** Every spec that references war score components agrees with DIPLOMACY_SPEC §6e and the live code. Ticking is the 5th additive component, not a replacement.
- **Composite floor:** Every spec that references the floor agrees on -60. No references to -40.
- **Power tier taxonomy:** Every spec uses `major / secondary / minor` (Phase 0 canonical), not `great_power / secondary_power / minor_power`.
- **Diplomatic state machine:** Every new clause type and state transition is compatible with the existing `VALID_TRANSITIONS` in `diplomacy.py`.
- **Serialization:** No two specs add the same field name to WorldState. No spec adds a field that conflicts with an existing field.
- **Deferred items:** No spec promises to implement something that the umbrella explicitly defers.
- **Test count:** Sum of all slice test estimates in sub-specs matches the umbrella's total. No orphaned tests.
- **Clause types:** `forced_alliance` and `war_bargain` do not collide with existing clause types in `diplomatic_templates.py`.

**Score 7+ requires:** Zero hard contradictions. At most 2 soft inconsistencies (wording differences that don't affect behavior).

**Score < 5 means:** Specs will produce implementation bugs from conflicting instructions.

### M5: Completeness (1-10)

Does the spec suite cover every identified gap without scope creep?

Evaluate:
- Every "Problem to Solve" in each sub-spec has a corresponding solution section
- Every solution section has a corresponding implementation slice assignment
- Every deferred item in the umbrella checklist has: a target phase, a rationale, and confirmation that no implementation slice secretly depends on it
- The umbrella's Gate criteria cover every sub-spec's "done" state
- Edge cases are specified: what happens when war score is 0? What happens when France has no allies? What happens when the named enemy is eliminated mid-bargain? What happens on save/load mid-peace-proposal?
- AI behavior is specified for every new player action (AI response to forced alliance, AI peace timing with ticking, AI bargain generation rules)
- The "Building Blocks" principle (CLAUDE.md Golden Rule 5) is respected: enemy AI uses the same executor paths for peace/objectives/bargains as the player
- No feature is half-specified (described in one section but missing from implementation sequence or test coverage)

**Score 7+ requires:** An implementer finishing all slices would have a complete, playable Peace Deals phase with no known gaps.

**Score < 5 means:** Significant gameplay paths are unspecified. Implementation will stall on "what should happen here?" questions.

## Audit Procedure

### Step 1: Read

Read every source listed in Audit Scope. Do not skim. Track every cross-reference.

### Step 2: Score

Score each metric M1-M5. For each score, list the specific checks that passed and failed.

### Step 3: Findings

For each failed check or identified issue, produce a numbered finding:

```
F-{N}: {one-line summary}
  Severity: CRITICAL | MAJOR | MINOR
  Location: {doc}:{section}
  Problem: {what is wrong}
  Fix: {exact steps to resolve — file, section, what to add/change/remove}
  Affected metrics: {which M1-M5 scores this impacts}
```

Severity guide:
- **CRITICAL:** Contradiction between specs, missing data that blocks implementation, formula error, stale reference to dead code. Must fix before GO.
- **MAJOR:** Ambiguity that will cause an implementer to guess, missing edge case for a common path, test gap for a shipped feature. Should fix before GO.
- **MINOR:** Wording improvement, missing cross-reference, cosmetic inconsistency. Can fix during implementation.

### Step 4: Improvement Steps

For each CRITICAL and MAJOR finding, write the exact edit needed. Be specific enough that an agent could apply the fix without further design discussion:

```
Step {N}: Fix F-{X}
  File: docs/{spec}.md
  Section: §{N}
  Action: {Add | Replace | Remove}
  Content: {the exact text or structure to add/change}
```

### Step 5: Verdict

```
============================================
PEACE DEALS SPEC AUDIT — RUN #{N}
Date: {date}
============================================

METRICS:
  M1 Fun:                    {score}/10  {PASS|FAIL}
  M2 Clarity:                {score}/10  {PASS|FAIL}
  M3 Work Segmentation:      {score}/10  {PASS|FAIL}
  M4 Contradiction-Freedom:  {score}/10  {PASS|FAIL}
  M5 Completeness:           {score}/10  {PASS|FAIL}

FINDINGS: {N} total ({C} critical, {M} major, {m} minor)

CRITICAL BLOCKERS:
  {list or "None"}

VERDICT: {GO | NO-GO}
  {If NO-GO: "Fix {N} critical and {M} major findings before next run."}
  {If GO: "All metrics >= 7. Spec suite is implementation-ready. Begin BPH-A."}
============================================
```

**GO requires:** All five metrics >= 7 AND zero CRITICAL findings.

**NO-GO with path:** If any metric is 5-6 with no CRITICAL findings, list the specific fixes that would bring it to 7+. This gives the fixer a bounded task, not an open-ended rewrite.

**NO-GO hard:** If any metric is < 5 or there are 3+ CRITICAL findings, the spec needs structural work before another audit run is useful. List what structural work is needed.

## Running the Audit

Invoke this as: `/peace-deals-spec-audit`

Or run via agent:

```
Agent({
  description: "Peace Deals spec audit run N",
  prompt: "Run the Peace Deals spec audit per .agents/skills/peace-deals-spec-audit/SKILL.md. This is run #{N}. Read every Audit Scope source, score M1-M5, produce numbered findings with severity, write improvement steps for CRITICAL/MAJOR, and end with GO/NO-GO verdict."
})
```

Each run should take 5-10 minutes of agent time. The audit is designed to converge: fixing CRITICAL findings first, then MAJOR, should bring all metrics above threshold within 2-4 runs.
