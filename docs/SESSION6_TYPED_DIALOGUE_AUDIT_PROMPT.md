# Session 6 Typed Dialogue Audit Prompt

Audit the Session 6 typed-dialogue migration slice in `project-sovereign-map`.

Focus areas:

1. Backend typed objection path
   - `backend/main.py` `/respond_to_diplomatic_objection`
   - `backend/commands/diplomatic_executor.py` `handle_diplomatic_objection_response()`
   - Confirm direct `diplomatic_declare_war` / `diplomatic_ultimatum` objections use the confirmed-objection bypass and do not re-trigger the same popup on `proceed`.

2. Godot popup migration completeness
   - `godot-client/project-sovereign/scripts/main.gd`
   - `godot-client/project-sovereign/scripts/api_client.gd`
   - Confirm `talleyrand_objection`, `sabotage_discovery`, and `vassal_rebellion` no longer synthesize English command strings and now route through typed endpoints/actions.

3. Dialogue-state behavior
   - For dialogue-backed Talleyrand objections, confirm:
     - `proceed` routes to override/send
     - `modify` replays the dialogue popup instead of dropping state
     - `cancel` clears the pending dialogue cleanly

4. Response-contract coverage
   - `tests/test_response_pipeline.py`
   - `tests/test_endpoint_wiring.py`
   - Verify the new endpoint still returns the standard gameplay envelope, popup keys, diplomatic top-bar fields, and `active_wars`.
   - Verify the enemy-phase deferral test really proves queued popups survive the enemy-phase response and appear on the follow-up request.

Deliverables:

- List concrete findings first, ordered by severity.
- Call out any remaining parser-dependent diplomacy paths if they still exist.
- Note missing integration coverage if any typed popup path is still only indirectly tested.
- Briefly confirm whether Session 6 is ready to move on to popup routing registry cleanup.
