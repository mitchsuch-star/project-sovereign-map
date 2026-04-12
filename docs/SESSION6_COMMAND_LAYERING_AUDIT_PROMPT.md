# Session 6 /command Layering Audit Prompt

Audit the Session 6 `/command` response-tail cleanup slice in `project-sovereign-map`.

Scope:

1. `/command` post-processing consolidation
   - `backend/main.py`
   - Read `_apply_command_result_layers()` and the helper functions it delegates to.
   - Confirm `execute_command()` no longer hand-layers the long response tail inline after `_build_command_response()`.
   - Confirm the helper still covers the previous `/command` contract:
     - bombardment result + action marker
     - redemption event state handoff
     - enemy-phase serialization + fog filtering
     - strategic reports
     - tactical events
     - independent command report
     - popup deferral / proposal-result exception
     - notification inclusion

2. Enemy-phase popup + notification behavior
   - `backend/main.py`
   - `tests/test_response_pipeline.py`
   - Confirm enemy-phase responses still defer choice popups by leaving them queued on `world`.
   - Confirm notifications are still included on the same enemy-phase response.
   - Confirm only informational proposal results remain allowed alongside `enemy_phase`.

3. Regression guardrails
   - `tests/test_response_pipeline.py`
   - Confirm the new source-level assertion actually pins delegation to `_apply_command_result_layers()` and is not trivially satisfied.
   - Confirm the new positive regression uses a real choice popup path and proves the popup arrives on the follow-up request after the enemy-phase response.

Changed files in this slice:

- `backend/main.py`
- `tests/test_response_pipeline.py`
- `docs/STATUS.md`
- `docs/BUG_FIXES.md`
- `CLAUDE.md`
- `docs/SESSION6_COMMAND_LAYERING_AUDIT_PROMPT.md`

Deliverables:

- List concrete findings first, ordered by severity.
- Call out any response field that may have been dropped or behaviorally changed during the consolidation.
- Note any missing regression coverage around fog-hidden enemy phases, enemy victory, or proposal-result coexistence.
- If you find no blocking or major issues, stage the files from this slice, commit them, and push:
  - `git add -- backend/main.py tests/test_response_pipeline.py docs/STATUS.md docs/BUG_FIXES.md CLAUDE.md docs/SESSION6_COMMAND_LAYERING_AUDIT_PROMPT.md`
  - `git commit -m "Finish Session 6 command response cleanup"`
  - `git push origin master`
- After the audit, briefly confirm whether Session 6 response/popup hardening is fully complete and the repo is ready to move on to the next planned slice.
