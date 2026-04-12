# Session 7 Scale-Sensitive Backend Hardening Audit Prompt

Audit the Session 7 scale-sensitive backend hardening slice in `project-sovereign-map`.

Scope:

1. Shared nation-config routing
   - `backend/nation_config.py`
   - `backend/models/world_state.py`
   - `backend/main.py`
   - `backend/game_logic/dispatch.py`
   - Confirm runtime nation defaults no longer live as scattered inline dicts in the touched Session 7 paths.
   - Confirm non-France campaigns preserve `player_nation` through world init, save migration fallback, and `POST /new_game`.
   - Confirm debug/reporting surfaces in this slice no longer silently read France-only state when `world.player_nation != "France"`.

2. Diplomacy player-nation correctness
   - `backend/game_logic/diplomatic_dialogue.py`
   - `backend/game_logic/diplomatic_advisory.py`
   - `backend/game_logic/diplomatic_templates.py`
   - `backend/commands/diplomatic_executor.py`
   - `backend/commands/diplomatic_defiance.py`
   - Confirm proposal ownership, diplomatic-state lookups, relation lookups, war-score reads, and alliance-paradox text all use the active player nation in the touched flows.
   - Confirm the slice does not regress existing France-default behavior.

3. Scale-sensitive AI contact query seam
   - `backend/ai/enemy_ai.py`
   - Confirm raw scale-sensitive `world.get_enemies_of_nation()` call sites now route through the cached helper surface.
   - Confirm the helper uses fog-aware `get_visible_enemies()` only for player-side AI views and leaves enemy-nation views on the omniscient path until a real multi-perspective intel model exists.
   - Call out any remaining hot-path enemy scans outside the helper in this file.

4. Scenario/runtime support validation
   - `backend/modding/validator.py`
   - `backend/models/world_state.py`
   - `mods/examples/custom_nations_scenario.json`
   - Confirm unsupported nation rosters now fail before `WorldState.from_scenario()` loads them.
   - Confirm supported in-map scenarios still validate and load.
   - Confirm the validator errors are specific enough for modders to act on.

5. Regression coverage
   - `tests/test_session7_backend_hardening.py`
   - `tests/test_restart_flow.py`
   - `tests/test_audit_minor_2026_03.py`
   - `tests/test_systems_v3_session7.py`
   - `tests/test_deep_audit_session7.py`
   - `tests/test_session8d_dispatch_polish.py`
   - Confirm the new tests actually pin:
     - non-France world defaults
     - non-France restart persistence
     - non-France dispatch behavior
     - AI contact caching / fog seam behavior
     - scenario validation completeness
   - Note any missing regression coverage around save/load migration, player-nation authority defaults, or diplomacy counter-offer flows.

6. Workspace temp-directory issue
   - `git status --short`
   - There is an inaccessible directory warning in the working tree:
     - `warning: could not open directory 'tmp6qp71c0z/': Permission denied`
   - Determine whether this is:
     - only a local workspace hygiene issue caused by temp-dir permissions
     - or a repeatable repo-side problem introduced by the Session 7 work
   - Verify whether any tracked files live under that path.
   - Recommend the smallest safe cleanup or ignore strategy. Do not suggest destructive broad resets.

Changed files in this slice:

- `backend/nation_config.py`
- `backend/models/world_state.py`
- `backend/main.py`
- `backend/game_logic/dispatch.py`
- `backend/game_logic/diplomatic_dialogue.py`
- `backend/game_logic/diplomatic_advisory.py`
- `backend/game_logic/diplomatic_templates.py`
- `backend/commands/diplomatic_executor.py`
- `backend/commands/diplomatic_defiance.py`
- `backend/ai/enemy_ai.py`
- `backend/modding/validator.py`
- `tests/test_session7_backend_hardening.py`
- `tests/test_restart_flow.py`
- `docs/STATUS.md`
- `docs/BUG_FIXES.md`
- `docs/SESSION7_SCALE_HARDENING_AUDIT_PROMPT.md`

Verification already run in this slice:

- `tests/test_session7_backend_hardening.py`
- `tests/test_restart_flow.py`
- `tests/test_audit_minor_2026_03.py`
- `tests/test_systems_v3_session7.py`
- `tests/test_deep_audit_session7.py`
- `tests/test_session8d_dispatch_polish.py`
- Manual scenario validation via local Python harness for:
  - supported `player_nation="Prussia"` scenario load
  - rejection of `mods/examples/custom_nations_scenario.json`

Environment caveat:

- `pytest` cases that rely on `tmp_path` are currently permission-blocked in this environment because both the default temp root and custom `--basetemp` cleanup hit `Access is denied`.
- Treat that as an audit item: determine whether the code is still correct despite the local test-harness limitation, and whether the inaccessible temp directory warning is related.

Deliverables:

- List concrete findings first, ordered by severity.
- Call out any player-nation regression risk that still assumes France in untouched adjacent systems.
- Explicitly classify the `tmp6qp71c0z/` issue as code bug, test-harness issue, or local environment residue.
- If you find no blocking or major issues, stage the files from this slice, commit them, and push:
  - `git add -- backend/nation_config.py backend/models/world_state.py backend/main.py backend/game_logic/dispatch.py backend/game_logic/diplomatic_dialogue.py backend/game_logic/diplomatic_advisory.py backend/game_logic/diplomatic_templates.py backend/commands/diplomatic_executor.py backend/commands/diplomatic_defiance.py backend/ai/enemy_ai.py backend/modding/validator.py tests/test_session7_backend_hardening.py tests/test_restart_flow.py docs/STATUS.md docs/BUG_FIXES.md docs/SESSION7_SCALE_HARDENING_AUDIT_PROMPT.md`
  - `git commit -m "Complete Session 7 backend hardening"`
  - `git push origin master`
- After the audit, briefly confirm whether Session 7 is fully complete and whether the repo is ready to move on to Session 8 renderer cutover prep.
