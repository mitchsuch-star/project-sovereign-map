# Session 5 Audit Prompt

> Copy everything below the line into a fresh audit session.

---

## PROMPT START

You are auditing the Session 5 restart-flow implementation for "Ink & Iron" in the current local repository.

Do not write code. Do not widen this into a broad full-project audit. The target is `PL-29` only: supported new-game / restart flow.

## Goal

Determine whether restart is now a real, safe contract across backend state, autosave/manual-save semantics, and Godot client reset/hydration.

You must verify:

1. `POST /new_game` is a supported backend contract, not a test-only assumption.
2. Restart resets the active campaign state cleanly without restarting the backend process.
3. Autosave is refreshed immediately after restart, and stale autosave cannot resurrect the prior campaign by accident.
4. Manual saves remain intact.
5. Frontend restart wiring reuses a single world-swap hydration/reset path instead of adding a divergent second path.
6. Save/load path resolution is consistent with `save_manager.SAVE_DIR` and does not silently read/write a different directory.

## Read First

- `docs/BUG_FIXES.md` section `PL-29`
- `docs/STATUS.md`
- `backend/main.py`
- `backend/save_manager.py`
- `godot-client/project-sovereign/scripts/main.gd`
- `godot-client/project-sovereign/scripts/pause_menu.gd`
- `godot-client/project-sovereign/scripts/api_client.gd`
- `godot-client/project-sovereign/scenes/pause_menu.tscn`
- `tests/test_restart_flow.py`

Read other files only if needed to confirm or challenge a finding.

## Audit Rules

1. Treat docs as claims to verify, not truth.
2. Prefer current code and targeted probes over historical assumptions.
3. Separate backend state-reset issues from frontend stale-UI issues.
4. Call out contract mismatches, especially where one save/load path uses a different directory or response shape than another.
5. If you cannot run Godot, say so explicitly and classify frontend findings as code-inspection findings unless you have a real probe.

## Required Checks

### A. Backend Reset Contract

Verify whether restart clears or recreates the relevant state cleanly:

- turn / AP / admin AP
- marshals and regions
- mailbox / pending diplomatic dialogue
- notifications
- eliminated nations tracking
- game-over / victory state
- singleton references in `backend/main.py`

### B. Save Semantics

Verify:

- `POST /new_game` writes a fresh autosave immediately
- manual saves remain untouched
- loading autosave after restart restores the new campaign, not the previous one
- filename validation and `/load` / `/delete_save` resolve through the same save-root contract

### C. Frontend World-Swap Contract

Inspect whether load and new-game now share one reset/hydration path.

Check for clearing or rehydrating:

- modal dialogs
- top-bar screens
- war-panel cache
- pending response caches
- envoy/mailbox badge state
- notification rail
- terminal history/output expectations

### D. Pause Menu Wiring

Verify:

- pause menu exposes a restart/new campaign action
- the button routes to the API client correctly
- result handling rehydrates from backend response instead of trying to fake local reset

## Suggested Probes

Use targeted probes where practical:

- mutate live world state, call `/new_game`, compare with a fresh `WorldState`
- create a manual save plus autosave, restart, then inspect both files
- load autosave immediately after restart
- inspect or probe save-root behavior when `save_manager.SAVE_DIR` is redirected

If you run tests, keep them focused on the restart flow and name exactly which ones you used.

## Output Format

Organize the audit as:

### 1. Baseline Snapshot

- date
- branch / commit if available
- clean vs dirty tree
- files inspected
- probes/tests run

### 2. Executive Verdict

Answer directly:

- Is `PL-29` actually fixed?
- Is the backend reset contract safe?
- Are autosave/manual-save semantics correct?
- Is the frontend reset/hydration path coherent?
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

- backend reset
- autosave overwrite
- manual save preservation
- save-root consistency
- pause-menu wiring
- frontend stale-state clearing

### 5. Open Questions / Residual Risk

Call out anything not directly verified, especially Godot runtime behavior if you could not execute it.

## Severity Rubric

### Critical

Restart can restore stale campaign state, destroy manual saves, or leave backend/frontend state contradictory.

### Major

Restart mostly works but leaves live stale UI state, inconsistent save roots, or backend singleton drift.

### Moderate

Usable but rough; one surface still diverges from the main reset contract.

### Low

Polish or clarity issue with little risk of corrupting state.

## Final Constraint

Do not drift into general architecture feedback. Stay on restart-flow correctness, regression risk, and contract clarity.

## PROMPT END
