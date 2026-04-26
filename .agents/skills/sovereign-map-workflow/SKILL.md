---
name: sovereign-map-workflow
description: Project-specific workflow for Project Sovereign / Ink & Iron repo work. Use when Codex is auditing or modifying this repository's Python backend, Godot client, tests, status docs, Memory and Pressure / DG-4 / C-lite specs, Balance of Europe, vassalization, commitment popup, notification rail, dispatch, or campaign-log behavior.
---

# Sovereign Map Workflow

Use this skill as the default operating procedure for work in `project-sovereign-map`.

## Preflight

Run these first for audits, fixes, or commits:

```powershell
git status --short
git log -1 --oneline
```

Use `rg` before broad file reads. Treat the worktree as potentially dirty and do not revert user changes. If committing fails with `.git/index.lock` permission errors, report the ACL issue and leave changes staged/unstaged as-is.

## Source Map

Primary backend areas:
- `backend/game_logic/diplomacy.py`: diplomatic states, war cascade, commitment paradox, acceptance components.
- `backend/game_logic/coalition.py`: Balance of Europe, bloc power, hegemony beats.
- `backend/game_logic/diplomatic_ledger.py`: ledger payloads for Godot.
- `backend/game_logic/commitments_routing.py`, `dispatch.py`, `campaign_log.py`, `notifications.py`: presentation routing.
- `backend/commands/meta_executor.py`: debug cheats.
- `backend/commands/diplomatic_executor.py`, `vassal_executor.py`: player diplomatic actions.
- `backend/models/world_state.py`: serialization and shared state.

Primary Godot areas:
- `godot-client/project-sovereign/scripts/diplomatic_ledger.gd`
- `godot-client/project-sovereign/scripts/notification_bar.gd`
- `godot-client/project-sovereign/scripts/commitment_paradox_popup.gd`
- `godot-client/project-sovereign/scripts/main.gd`

Spec/status sources:
- `docs/STATUS.md`
- `docs/RELIABILITY_COMMITMENTS_SPEC.md`
- `docs/COMMITMENTS_PRESENTATION_SPEC.md`
- `docs/SCALE_READINESS_PLAN.md`
- `docs/SAVE_FORMAT_REFERENCE.md`

## Verification

Run focused tests for the touched area, then broader tests when shared diplomatic state, serialization, or UI contracts changed.

Common focused suites:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_session8a_ledger_debug.py tests/test_session8b_ledger_ui.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_hegemony_engine.py tests/test_dg4_spec_closure.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_phase4_batch4_ledger.py tests/test_commitment_paradox_rename.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_c_lite_presentation_closure.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_bugfix_session4.py::TestDLF1VassalizableIcon -q
```

Always finish Python code/test changes with:

```powershell
.\.venv\Scripts\python.exe -m ruff check backend tests
```

Run full tests when touching shared diplomacy, coalition, serialization, or command routing:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ -q
```

## Smoke Tests

Useful in-game/debug smoke commands:

```text
cheat clear_dialogue
cheat trigger_commitment_paradox Prussia Austria
cheat seed_hard_reject Austria
cheat set_diplo_state Saxony OPEN_BORDERS
cheat create_vassal Saxony
```

Manual smoke checklist:
- Ledger Nations: Saxony shows `Vassalizable` from `OPEN_BORDERS`; Britain/Prussia do not.
- Vassal command: `make vassal Saxony` succeeds, then Saxony no longer shows `Vassalizable`.
- Balance of Europe: headline says active European bloc power, shows score, lists bloc members, and explains overlapping alliances.
- Balance rail: dismiss stale old notices before judging duplicates; fresh war/cascade should emit only the final settled Balance beat.
- Commitment popup: buttons read as political choices, e.g. `Honor Austria` and `Side with Prussia`.
- Notification rail `Open Ledger`: routes to the commitments ledger target.
- Campaign log/dispatch: no duplicated `commitment_paradox_resolved` or same-episode spam.

## Local Contracts

DG-4 / C-lite current phase should stay closed unless a new smoke failure proves otherwise. Do not reopen deferred items without explicit request:
- D1 advisory-first strategy.
- D2 broader non-France-hegemon generalization.
- D3 per-row bloc stamps/member badges.
- WB-* bargain-era presentation and war bargain mechanics.
- Richer later-callback architecture.

Godot `.uid` files are not tracked in this repo unless an existing tracked pattern appears. Treat new `.uid` sidecars as untracked generated files unless the user asks to include them.
