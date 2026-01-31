# Ink & Iron: Current Status

> **Updated every session by Claude Code.**
> **Last Updated:** January 31, 2026
> **Last Session:** PURSUE completion fix, code review, Phase M design

---

## Quick Stats

| Metric | Value |
|--------|-------|
| **Tests Passing** | **1022** (verified Jan 31, 2026) |
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

### Jan 31 (this session)
- **Bug fix:** `pending_interrupt` overwrite — lines 562/578 in strategic.py clobbered correctly-set interrupt dicts, causing "Invalid choice" errors on interrupt responses
- **Design fix:** PURSUE now completes after combat (any outcome) — no more stalemate popup for PURSUE; order is fulfilled once marshal engages target
- **Code review fixes:** HOLD `_complete_order` now clears `holding_position` (was leaking +15% defense); HOLD sally now checks `_should_auto_attack` (was infinite loop); dead code cleanup (unreachable breaks, unused vars, dead `join_combat` check)
- **Phase M designed:** Strategic Objections — disobedience at strategic command issuance (see PHASE_5_2_IMPLEMENTATION_PLAN.md)
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
| Jan 31, 2026 | **1022** | PURSUE completion fix, code review fixes |
| Jan 30, 2026 | 981 | Doc cleanup session |
| Jan 28, 2026 | 705 | Phase D+E complete |
| Jan 25, 2026 | 667 | Phase 5.2 core complete |

---

## Known Issues

| Issue | Severity | Notes |
|-------|----------|-------|
| Phase J (UI) not started | Low | Strategic status display in Godot |
| Phase M not started | Low | Strategic objections — designed, see PHASE_5_2_IMPLEMENTATION_PLAN.md |
| Godot smoke test pending | Low | Need manual verification |

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
