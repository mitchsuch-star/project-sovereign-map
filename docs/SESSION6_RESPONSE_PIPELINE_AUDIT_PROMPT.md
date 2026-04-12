# Session 6 Response Pipeline Audit Prompt

> Copy everything below the line into a fresh audit session.

---

## PROMPT START

You are auditing the Session 6 response-pipeline slice for "Ink & Iron" in the current local repository.

Do not write code. Do not widen this into a broad project audit. The target is **Session 6 slice 1 only**: `/command` response-pipeline hardening.

## Goal

Determine whether `/command` now truly starts from the shared `build_base_response()` contract while preserving the one legitimate divergence on that path: enemy-phase popup/notification deferral.

You must verify:

1. The successful `/command` path no longer hand-builds the standard gameplay envelope (`success`, `message`, `events`, `game_state`, `action_summary`, top-bar fields, `active_wars`).
2. `build_base_response()` now owns `active_wars` directly instead of piggy-backing on popup passthrough logic.
3. `/command` uses the shared builder without accidentally draining deferred popups or notifications before enemy-phase post-processing runs.
4. The existing enemy-phase deferral behavior still works: choice-requiring popups stay deferred when `enemy_phase` is present, while informational proposal-result popups remain safe to surface.
5. The new regression tests actually cover the refactor instead of just restating old response-shape assertions.

## Read First

- `docs/STATUS.md`
- `backend/main.py`
- `tests/test_response_pipeline.py`
- `tests/test_endpoint_wiring.py`

Read other files only if needed to confirm or challenge a finding.

## Audit Rules

1. Treat docs as claims to verify, not truth.
2. Stay on the response-pipeline slice. Do not drift into typed-dialogue migration, popup-registry redesign, AI scale, or renderer work.
3. Separate structural success from behavioral regressions. A cleanup that changes popup/notification timing is not automatically safe.
4. Prefer current code and targeted probes over historical assumptions.
5. If you cannot verify a behavior dynamically, say so explicitly and label it as code-inspection confidence only.

## Required Checks

### A. Shared Builder Ownership

Verify whether `build_base_response()` is now the real owner of:

- base gameplay fields
- diplomatic top-bar fields
- `active_wars`
- optional popup passthrough inclusion
- optional informational-notice queuing
- optional notification draining

Check whether the new optional flags are coherent and narrowly scoped, or whether they create a second accidental contract.

### B. `/command` Main Path

Verify whether the main successful `/command` path:

- starts from the shared builder
- disables popup / notice / notification draining at the initial build step
- layers only command-specific extras afterward
- still handles `enemy_phase`, `tactical_events`, strategic reports, and dispatch correctly

### C. Enemy-Phase Deferral Safety

Verify:

- deferred choice popups are not consumed too early
- informational proposal-result popups still surface safely beside `enemy_phase`
- notifications are not double-queued or accidentally dropped

### D. Test Quality

Verify whether the new tests meaningfully cover:

- builder skip-flags preserving deferred world state
- `/command` actually calling `build_base_response()` on the main success path
- no regression in endpoint response shape

## Suggested Probes

Use targeted probes where practical:

- monkeypatch or spy on `build_base_response()` during a successful `/command`
- set a pending popup / notification on world, call the builder with skip flags, and confirm state remains pending
- inspect an `end turn` response path for `enemy_phase` + popup deferral behavior

If you run tests, keep them focused on:

- `tests/test_response_pipeline.py`
- `tests/test_endpoint_wiring.py`

Name exactly which commands you used.

## Output Format

Organize the audit as:

### 1. Baseline Snapshot

- date
- branch / commit if available
- clean vs dirty tree
- files inspected
- tests/probes run

### 2. Executive Verdict

Answer directly:

- Is the Session 6 response-pipeline slice actually fixed?
- Does `/command` now use the shared builder in a real way?
- Did the refactor preserve enemy-phase popup deferral safely?
- What is still risky?

### 3. Findings

List findings ordered by severity.

For each finding include:

- title
- severity
- evidence with file references
- why it matters
- smallest credible fix direction

### 4. Verification Matrix

Cover:

- shared builder ownership
- `active_wars` ownership
- `/command` builder usage
- popup deferral preservation
- notification / notice timing
- test sufficiency

### 5. Residual Risk / Next Step Note

Call out any unresolved risk that should shape the **next Session 6 slice**, which is typed dialogue migration.

## Severity Rubric

### Critical

The refactor silently changes popup/notification behavior, breaks enemy-phase ordering, or leaves `/command` still bypassing the shared contract in practice.

### Major

The structure is improved, but one important response field family still has split ownership or unreliable timing.

### Moderate

The slice mostly works, but one edge path or test seam remains weak.

### Low

Clarity or maintainability issue with low regression risk.

## Final Constraint

Do not turn this into a full Session 6 audit. This audit is only about the response-pipeline slice that landed now.

## PROMPT END
