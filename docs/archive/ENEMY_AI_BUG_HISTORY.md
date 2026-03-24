# Enemy AI Bug Fix History

Archived from `backend/ai/enemy_ai.py` (Systems Audit Session 11).

## Bug Fixes (Jan 2026)

### Jan 20, 2026 — Wellington fortify/unfortify oscillation (1bd4e01)
**Problem:** Wellington unfortifies to attack, attack fails, re-fortifies, repeat.
**Fix:** Removed FORTIFICATION_ABANDON_THRESHOLD; attacks go through normal P4 only.

### Jan 20, 2026 — Enemy turn skipped on auto-advance (8e33b82)
**Problem:** Auto-advance skipped enemy AI phase entirely.
**Fix:** Ensure `_process_enemy_turns()` runs before `advance_turn()`.

### Jan 24, 2026 — Fortify/drill while engaged (bc9e936)
**Problem:** AI tries to fortify or drill while enemy in same region.
**Fix:** P0 engagement check runs FIRST, forces attack/retreat/wait.

### Jan 26, 2026 — Intent tracking for multi-step actions (c2ae6f8)
**Problem:** Unfortify-then-capture failed because AI forgot the capture step.
**Fix:** `_pending_intents` dict stores next action after unfortify.

### Jan 26, 2026 — Recovery destination oscillation (c2ae6f8)
**Problem:** Marshal retreats to A, next turn path says B is better, oscillates.
**Fix:** `recovery_destination` locks retreat target until recovery complete.

### Jan 26, 2026 — Blocked path attacks (c2ae6f8)
**Problem:** Distance-2 attacks attempted through enemy-occupied regions.
**Fix:** BFS path validation confirms path is clear before attack.

### Jan 27, 2026 — Within-turn oscillation (416ec12)
**Problem:** Marshal moves A→B then B→A within same turn.
**Fix:** `_marshal_visited_locations` tracks all visited locations per turn as sets.

### Jan 27, 2026 — Wait action spam (416ec12)
**Problem:** AI spams wait actions, never ends turn.
**Fix:** `_consecutive_waits` counter, marshal marked "done" after 2 waits.

### Jan 27, 2026 — Cautious stuck fortified forever (416ec12)
**Problem:** All capture targets "unsafe" due to strict counter-attack threshold.
**Fix:** Stale fortification relaxation — threshold decays after 3+ turns.

### Jan 27, 2026 — Prussia not capturing current region (416ec12)
**Problem:** `_find_undefended_capture` only checks adjacent, not current region.
**Fix:** P-1 priority captures undefended enemy region marshal is standing on.

### Jan 27, 2026 — Intent persists after failure (ef21ff6)
**Problem:** Failed unfortify left stale capture intent blocking new decisions.
**Fix:** `_pending_intents.pop()` on any failed action execution.

### Jan 27, 2026 — Fortify bonus distortion (ef21ff6)
**Problem:** Uncapped `fortify_bonus` in target evaluation could distort ratios.
**Fix:** Cap at `min(fortify_bonus, 0.20)` in `_evaluate_target_ratio()`.
