# Settlement G2-Slice-G2e Audit Prompt

Audit the pushed `master` commit that lands **G2-Slice-G2e - same-war replace-confirm chooser SHIP** for Project Sovereign / Ink & Iron.

Use a code-review stance. Report **GO / GO-with-followup / NO-GO**. Findings must lead the report, ordered by severity, with concrete `file:line` references and repair patches. Treat `docs/SETTLEMENT_UI_CLEANUP_SPEC.md` v0.32 D6 and line 484 as the contract.

Verify:

1. Same-war same-scope restaging still merges compatible terms through SC-26 and still preserves active drafts on merge conflict.
2. Same-war different-scope restaging returns `settlement_scope_replace_confirm`, not `same_war_scope_collision`, and does not mutate the current draft before the player chooses.
3. `Replace current draft` clears the prior scoped `draft_key`, stages the new selected target / covered-enemy scope, and preserves the incoming terms only.
4. `Keep current draft` restores the prior `settlement_confirm` popup unchanged.
5. Outer cancel is treated as keep.
6. Click-time revalidation handles a scope flip between chooser creation and click without clobbering the current draft.
7. `compute_settlement_draft_key(...)` follows the spec: `settlement_draft:{war_id}:{selected_target_key}:{covered_scope_hash}`, where `covered_scope_hash` is the first 16 hex chars of SHA-256 over compact ASCII JSON for sorted unique `covered_enemy_participants`.
8. `settlement_scope_replace_confirm` is included in settlement-family collision guards but does not break incoming-offer defensive guards.
9. Backend dispatch, Godot `SETTLEMENT_DIALOGUE_ACTIONS`, and `proposal_confirm_popup.gd` all route/render `replace_current_scope_draft`, `keep_current_scope_draft`, and `settlement_scope_replace_confirm`.
10. Voice uses `settlement_scope_replace_confirm_talleyrand`; no inline fallback is the primary happy path.
11. The landed tests match D6 names exactly:
    - `test_same_war_different_scope_restage_returns_scope_replace_confirm`
    - `test_scope_replace_confirm_accept_replace_clears_existing_draft`
    - `test_scope_replace_confirm_accept_keep_is_no_op_restoring_prior_popup`
    - `test_scope_replace_confirm_outer_cancel_treated_as_keep`
    - `test_scope_replace_confirm_click_time_revalidation_handles_scope_flip`
12. Test budget remains within spec line 1282: 6-8 tests for G2e.
13. `docs/STATUS.md` and `docs/SETTLEMENT_UI_CLEANUP_SPEC.md` correctly mark G2e landed and name G2-Slice-G2d as next.
14. No unrelated backend, Godot, tests, or docs drift beyond the G2e slice and its status/audit prompt.

Run and report:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_settlement_scope_replace_confirm.py -q
.\.venv\Scripts\python.exe -m pytest tests\test_settlement_scope_replace_confirm.py tests\test_settlement_continuity_slice.py tests\test_settlement_foundation_slice.py tests\test_settlement_recovery_g2_slice6.py -q
.\.venv\Scripts\python.exe -m pytest tests\test_godot_parse_harness.py -q
.\.venv\Scripts\python.exe -m pytest tests/ -p no:randomly -q
.\.venv\Scripts\python.exe -m pytest tests/ -q
.\.venv\Scripts\python.exe -m ruff check backend tests
```

Also note whether the headless Godot parser was actually rerun. If it was not, verify `tools/godot_parse_report.json` transparently says the timestamp was refreshed and asks for a future parser rerun.
