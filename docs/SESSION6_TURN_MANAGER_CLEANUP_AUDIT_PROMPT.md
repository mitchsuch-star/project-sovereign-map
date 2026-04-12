# Session 6 Turn-Manager Cleanup Audit Prompt

Audit the Session 6 turn-manager popup-cleanup slice in `project-sovereign-map`.

Scope:

1. Turn-manager game-over cleanup
   - `backend/game_logic/turn_manager.py`
   - Read the early game-over return paths in `end_turn()`.
   - Confirm the old popup-flush workaround is gone.
   - Confirm game-over-invalid modal state is now cleared explicitly instead of being copied into the raw `end_turn()` result.

2. Game-over response behavior
   - `backend/main.py`
   - `tests/test_response_pipeline.py`
   - Confirm `POST /command` on end-turn victory/defeat now goes straight to the game-over state without surfacing stale modal choice popups from turn-manager.
   - Confirm this cleanup does not break the existing enemy-phase popup deferral contract.

3. Godot HUD-sync dedup
   - `godot-client/project-sovereign/scripts/main.gd`
   - `tests/test_popup_routing_registry.py`
   - Confirm `_on_command_result()` now relies on `_sync_response_hud()` for the normal fall-through path instead of repeating the same status/gold/manpower/map/notification updates.
   - Confirm `_route_redemption_response()` no longer duplicates that HUD sync.

4. Regression coverage
   - `tests/test_systems_audit_v2_session4.py`
   - `tests/test_response_pipeline.py`
   - `tests/test_popup_routing_registry.py`
   - Confirm the updated tests pin the intended behavior and that no previous coverage was weakened by simply deleting the old workaround.

Changed files in this slice:

- `backend/game_logic/turn_manager.py`
- `godot-client/project-sovereign/scripts/main.gd`
- `tests/test_systems_audit_v2_session4.py`
- `tests/test_response_pipeline.py`
- `tests/test_popup_routing_registry.py`
- `docs/STATUS.md`
- `docs/BUG_FIXES.md`
- `CLAUDE.md`
- `docs/SESSION6_TURN_MANAGER_CLEANUP_AUDIT_PROMPT.md`

Deliverables:

- List concrete findings first, ordered by severity.
- Call out any game-over-state edge case where stale modal data could still leak through.
- Note any missing regression coverage around enemy victory, player victory, or redemption timing.
- If you find no blocking or major issues, stage the files from this slice, commit them, and push:
  - `git add -- backend/game_logic/turn_manager.py godot-client/project-sovereign/scripts/main.gd tests/test_systems_audit_v2_session4.py tests/test_response_pipeline.py tests/test_popup_routing_registry.py docs/STATUS.md docs/BUG_FIXES.md CLAUDE.md docs/SESSION6_TURN_MANAGER_CLEANUP_AUDIT_PROMPT.md`
  - `git commit -m "Remove Session 6 turn-manager popup workaround"`
  - `git push origin master`
- After the audit, briefly confirm whether Session 6 is ready for the remaining `/command` manual-field-layering reduction follow-up.
