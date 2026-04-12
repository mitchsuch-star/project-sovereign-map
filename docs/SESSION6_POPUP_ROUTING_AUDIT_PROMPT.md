# Session 6 Popup Routing Audit Prompt

Audit the Session 6 popup-routing-registry slice in `project-sovereign-map`.

Scope:

1. Registry-driven modal ordering in Godot
   - `godot-client/project-sovereign/scripts/main.gd`
   - Read `_configure_response_routes()`, `_route_response_ui()`, and `_on_command_result()`.
   - Confirm modal precedence now lives in the ordered route registries instead of inline popup branches inside `_on_command_result()`.

2. Behavior parity across the refactor
   - Verify objection and glorious-charge routes still fire before `_sync_response_hud()`.
   - Verify the remaining modal routes still fire after `_sync_response_hud()`.
   - Confirm `show_load_dialog` remains non-blocking and still does not consume the rest of the response.
   - Confirm redemption still stays deferred when `enemy_phase` is present.

3. Route completeness and future drift
   - Confirm the registry covers the current blocking/modal response paths:
     - objection
     - glorious charge
     - alliance paradox
     - capture choice
     - diplomatic objection
     - incoming proposal
     - proposal confirm / diplomatic dialogue
     - clarification
     - interrupt
     - diplomatic sabotage
     - vassal rebellion
     - redemption event
   - Confirm any future popup addition to `_on_command_result()` would naturally belong in the registry rather than as a new ad hoc early return.

4. Test guardrails
   - `tests/test_popup_routing_registry.py`
   - `tests/test_response_pipeline.py`
   - `tests/test_deep_audit_session6.py`
   - Confirm the new source-level tests actually pin the intended structure and are not too weak or trivially satisfiable.

Changed files in this slice:

- `godot-client/project-sovereign/scripts/main.gd`
- `tests/test_popup_routing_registry.py`
- `docs/STATUS.md`
- `docs/BUG_FIXES.md`
- `CLAUDE.md`

Deliverables:

- List concrete findings first, ordered by severity.
- Call out any behavior regression risk around response ordering, HUD sync timing, or hidden modal interactions.
- Note any missing regression coverage that should land before the next Session 6 slice.
- If you find no blocking or major issues, stage the files from this slice, commit them, and push:
  - `git add -- godot-client/project-sovereign/scripts/main.gd tests/test_popup_routing_registry.py docs/STATUS.md docs/BUG_FIXES.md CLAUDE.md docs/SESSION6_POPUP_ROUTING_AUDIT_PROMPT.md`
  - `git commit -m "Complete Session 6 popup routing registry cleanup"`
  - `git push origin master`
- After the audit, briefly confirm whether Session 6 is ready to move on to turn-manager popup-flush workaround cleanup.
