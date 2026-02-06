# Session 8 Handoff Prompt

Paste this into a new Claude Code instance:

---

Read `CLAUDE.md` and `docs/STATUS.md` first. This is session 8 continuation. Here's what was done and what still needs attention:

## Bugs Fixed This Session (commit e51a458)

**6 files changed:** `executor.py`, `objection_v2.py`, `main.py`, `main.gd`, `test_objection_v2.py`, `CLAUDE.md`

### Fix 1: NoneType crash on stance_change with Anthropic LLM
- **Root cause:** `objection_v2.py` lines 707, 768 used `order.get('target', '').lower()`. Parser at `parser.py:297` explicitly sets `"target": None`. `.get('key', default)` returns `None` when key EXISTS with value `None` — default only applies for MISSING keys.
- **Fix:** Changed to `(order.get('target') or '').lower()` at both lines.
- **Tests:** 2 regression tests in `TestEvaluateAggressive` and `TestEvaluateCautious` passing `"target": None`.

### Fix 2: MILD "Field Dispatches" appearing on failed commands
- **Root cause:** `main.py:323` had `elif world.mild_concerns_this_turn:` fallback that sent stale MILD concerns on EVERY command response, not just end_turn. MILD added during objection eval persisted even when action failed.
- **Fix:** Removed the `elif` fallback. MILDs only sent via the end_turn result dict path (where executor saves them before advance_turn clears the list).

### Fix 3: Post-objection proceed consumed wrong AP for stance_change
- **Root cause:** `_execute_post_objection()` at line ~6642 used `world.use_action(action)` which always consumes 1 AP. But stance_change has variable cost (0-2 AP via `variable_action_cost`).
- **Fix:** Added `variable_action_cost` handling in `_execute_post_objection()` matching the pattern from the main execute path (lines 1236-1253).
- **Tests:** `test_post_objection_variable_cost_consumed` — verifies aggressive→defensive costs 2 AP via post-objection path.

### Fix 4: AP error after objection proceed (systemic)
- **Root cause:** AP was checked AFTER objection fired. Player could trigger objection for a 2 AP action with 1 AP left, then "proceed" fails with AP error.
- **Fix:** Added AP pre-check in the pre-validation block at executor.py ~line 926, BEFORE the V2 objection evaluation at line 938. Calculates expected AP cost (including variable stance_change cost) and returns "Not enough actions" if insufficient.
- **Tests:** `test_not_enough_ap_for_stance_change_no_objection` — with 1 AP, aggressive→defensive (costs 2) fails cleanly without triggering objection.

### Fix 5: Enemy turn summary not visible in command output
- **Root cause:** The summary text from `_execute_end_turn()` was displayed BEFORE the enemy phase dialog popped up. After dismissing the dialog, the user couldn't see it (already scrolled past).
- **Fix:** Added post-dismissal summary output in `main.gd:_on_enemy_phase_dismissed()` that writes the enemy phase summary to the command output area after the dialog closes.

### Fix 6: Already-in-stance MILD (verified not broken)
- Pre-validation at executor.py:862 catches "already in target stance" before objection evaluation runs. Added 2 regression tests confirming no MILD fires for this case.

## Two Open Issues to Investigate

### Issue A: MILD objection hard to trigger on Ney
User reports switching Ney into defensive repeatedly with no MILD appearing. This is EXPECTED behavior — `evaluate_aggressive()` at `objection_v2.py:710` requires BOTH `target_stance == 'defensive'` AND `_check_enemy_adjacent(marshal, game_state)`. If no enemy is adjacent to Ney's position, no MILD fires. Verify with user that they have an enemy adjacent. Also check: after first switch to defensive, subsequent "ney defensive" commands hit the already-in-stance pre-validation (success: False). User would need to go defensive→neutral→defensive to trigger again. Also max 1 MILD per marshal per turn (line 951 check).

Possible improvements to investigate:
- Should aggressive personality get MILD for `stance_change` to defensive even WITHOUT enemy adjacent? Currently `defend` action triggers MILD unconditionally but `stance_change` requires adjacency.
- The MILD message is prepended to the action result at executor.py:1278 (`mild_message + result["message"]`). Verify this actually shows in the Godot UI.

### Issue B: Enemy phase popup possibly not showing
User says "you removed popup that showed enemy turns." The popup code at `main.gd:476-484` was NOT modified. The dialog trigger logic is intact. Possible causes:
1. Enemies might not be taking actions (check backend console for `ENEMY PHASE DETECTED` print)
2. The `enemy_phase_dialog` node might be null (check for `ERROR: enemy_phase_dialog is NULL!` in Godot console)
3. The `total_actions` count might be 0 (enemy AI decided to do nothing)
4. Scene wiring issue — verify `enemy_phase_dialog` variable at `main.gd:31` is connected to the actual dialog node in the scene tree

To debug: end a turn with enemies present, check the Python backend console for `[ENEMY_PHASE_FINAL]` debug prints, and check Godot console for `ENEMY PHASE DETECTED`.

## Test Count: 1222 passed, 3 skipped, 0 failures

Known flakes (pass in isolation): `test_recklessness_2_blocks_defensive_stance`, `test_high_skill_wins_more_often` — statistical/test-ordering issues, not regressions.

## Key Files Modified This Session
- `backend/commands/executor.py` — AP pre-check, post-objection variable cost
- `backend/commands/objection_v2.py` — `.get()` vs `or` NoneType fix
- `backend/main.py` — removed stale mild_concerns fallback
- `godot-client/project-sovereign/scripts/main.gd` — enemy phase summary after dialog
- `tests/test_objection_v2.py` — 6 new regression tests
