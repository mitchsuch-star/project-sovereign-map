# Ink & Iron: Current Status

> **Updated every session by Claude Code.**
> **Last Updated:** February 2, 2026
> **Last Session:** Post-objection strategic routing fix, UI/UX improvements (hold tooltip, Grouchy clarification, sally battle display)

---

## Quick Stats

| Metric | Value |
|--------|-------|
| **Tests Passing** | **1022** (verified Feb 2, 2026) |
| **Current Phase** | 6 (Core Campaign Systems) — not started |
| **Blockers** | None |
| **Phases Complete** | 1, 2, 2.5, 2.9, 3, 4, 5.1, 5.2, 5.3 |

---

## Active Work

Phase 5.2/5.3 fully complete. Next: Phase 6 design.

- [ ] Smoke test strategic commands in Godot (Phase K)
- [ ] Phase M: Strategic Objections (disobedience at issuance) — designed, not yet implemented
- [ ] Begin Phase 6 design (Economy, Terrain, Fog, Manpower)
- [ ] See ROADMAP.md for full Phase 6 scope

---

## Recently Completed

### Feb 2 (this session)
- **Bug fix:** Strategic commands (HOLD, MOVE_TO, PURSUE, SUPPORT) failed with "Unknown action" after player insisted on objection. Post-objection executor was missing strategic routing and hold/wait handlers. Also propagated `is_strategic`/`strategic_type` into command dict so they survive objection storage.
- **UI fix:** Strategic HOLD tooltip — any marshal with active HOLD order now shows "HOLDING POSITION at [region]" in hover tooltip. Grouchy still shows "(Immovable): +15% defense".
- **UX fix:** Grouchy attack clarification — literal marshals no longer silently auto-move when given "attack" with no nearby target. Instead shows clarification popup offering to upgrade to PURSUE with target selection.
- **UX fix:** Sally battle display — extracted combat outcome/message from sally `combat_result` into top-level report fields. Strategic report popup now shows battle narrative and outcome inline. Text output also logs sally battle details.
- **Bug fix (root cause):** Sally battles never reached frontend — `new_state` (full WorldState with circular references) was embedded in executor attack results inside `combat_result`/`battle_details`. FastAPI JSON serializer silently dropped entire `strategic_reports`. Fixed by stripping `new_state` from combat results in sally and MOVE_TO attack_on_arrival reports.
- **Bug fix:** Duplicate cancel buttons in clarification popup — backend included Cancel/Proceed options that Godot popup already adds natively. Also fixed "Proceed as ordered" sending `"insist"` as target.
- **Improvement:** Sally target selection now evaluates all adjacent enemies and picks best strength ratio (lowest morale tiebreaker) instead of first-found.
- Test count: **1022 passed, 0 failures**

### Jan 31
- **Bug fix:** `pending_interrupt` overwrite — lines 562/578 in strategic.py clobbered correctly-set interrupt dicts, causing "Invalid choice" errors on interrupt responses
- **Design fix:** PURSUE now completes after combat (any outcome) — no more stalemate popup for PURSUE; order is fulfilled once marshal engages target
- **Code review fixes:** HOLD `_complete_order` now clears `holding_position` (was leaking +15% defense); HOLD sally now checks `_should_auto_attack` (was infinite loop); dead code cleanup (unreachable breaks, unused vars, dead `join_combat` check)
- **Phase M designed:** Strategic Objections — disobedience at strategic command issuance (see PHASE_5_2_IMPLEMENTATION_PLAN.md)
- **Bug fix:** Strategic commands cost 1 AP instead of 2 — pre-check didn't calculate required actions, `_execute_strategic_command` didn't return `variable_action_cost`. Literal personality correctly costs 1.
- **Bug fix:** Auto-upgrade exploit — "move to [distant]" and "attack [out of range]" auto-upgraded to strategic orders for only 1 AP. Now pre-checks AP inside `_execute_move` and `_execute_attack` before auto-upgrading, plus safety net in `variable_action_cost` loop.
- **Fix:** Case-insensitive marshal lookup — `get_marshal()` now falls back to case-insensitive search; `_fuzzy_match_marshal` searches all marshals (not just player).
- **Bug fix:** AI fortify/unfortify infinite loop — P3.5 unfortified to reposition but couldn't move (unsafe), P5 re-fortified immediately, repeat forever. Fixed: `_unfortified_this_turn` set now tracks ALL unfortifies (P3.5 + P7.5), P5 guard blocks re-fortify.
- **Bug fix:** Enemy marshals invisible on map — `marshals_data.append()` was inside the `if m.nation == player_nation` block, so only French marshals appeared in `map_data`.
- Test count: **1022 passed, 0 failures**

### Jan 30
- Documentation cleanup: deleted 12 obsolete files, merged 2 pairs, created VISION.md
- Trimmed CLAUDE.md from ~3500 to ~1565 lines (conceptual sections to FUTURE_DESIGN.md)
- Reconciled 55 TODOs: 3 stale removed, 21 updated with doc references, rest valid
- Verified test count: **981 passed, 0 failures**

### Previous Sessions
- Phase 5.2 Strategic Commands: 100% complete (MOVE_TO, PURSUE, HOLD, SUPPORT)
- Phase 5.3 Enemy AI fixes: stagnation counter, oscillation fixes
- Modding system: 66 tests, validator tool, example mods
- Serialization enforcement: 33 roundtrip tests

---

## Test Count History

| Date | Tests | Notes |
|------|-------|-------|
| Feb 2, 2026 | **1022** | Post-objection fix, UI/UX improvements, sally serialization fix |
| Jan 31, 2026 | 1022 | PURSUE completion fix, code review fixes |
| Jan 30, 2026 | 981 | Doc cleanup session |
| Jan 28, 2026 | 705 | Phase D+E complete |
| Jan 25, 2026 | 667 | Phase 5.2 core complete |

---

## Known Issues

| Issue | Severity | Notes |
|-------|----------|-------|
| Phase J (UI) not started | Low | Strategic status display in Godot |
| Phase M not started | Low | Strategic objections — designed, see PHASE_5_2_IMPLEMENTATION_PLAN.md. Note: Ney currently objects to HOLD via tactical objection system (aggressive vs defensive), works but message is generic. Phase M should replace with strategic-aware objection ("I'd rather attack!"). |
| Godot smoke test pending | Low | Need manual verification |
| Clarification popup for other literal actions | Low | Currently only triggers for attack-without-target. Could extend to move/scout with no target for Grouchy. |

---

## Next Session Priorities

1. Finish testing strategic commands in Godot
2. Phase M implementation (strategic objections) when ready
3. Begin Phase 6 design

---

## Quick Commands

```bash
# Run all tests
pytest tests/ -v

# Quick test count
pytest tests/ -v --tb=no -q 2>&1 | tail -3

# Start backend
python backend/main.py

# Validate mod file
python -m backend.modding.validator path/to/mod.json
```

---

## Document Map

| Need | Read |
|------|------|
| What phase are we in? | ROADMAP.md |
| How does X system work? | COMPLETED.md |
| Code patterns/rules | TECHNICAL.md |
| Enemy AI behavior | ENEMY_AI_REFERENCE.md |
| Core concept/vision | VISION.md |
| Future design concepts | FUTURE_DESIGN.md |
| Adding a marshal | MARSHAL_ADDITION_GUIDE.md |
| Save format | SAVE_FORMAT_REFERENCE.md |
| Modding | MODDING_FORMAT.md |
