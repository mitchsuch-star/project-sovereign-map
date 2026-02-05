# Ink & Iron: Current Status

> **Updated every session by Claude Code.**
> **Last Updated:** February 5, 2026
> **Last Session:** V2a Units 4-5 complete, doc consolidation

---

## Quick Stats

| Metric | Value |
|--------|-------|
| **Tests Passing** | **1203** (verified Feb 5, 2026) |
| **Current Phase** | V2a (Objection Refactor) — then Phase 6 |
| **Blockers** | None |
| **Phases Complete** | 1, 2, 2.5, 2.9, 3, 4, 5.1, 5.2, 5.3, M |

---

## Active Work

V2a Objection Refactor in progress: Units 1-5 complete, Units 6-7 remaining.

- [x] Phase M: Strategic Objections
- V2a: Objection System Refactor
  - [x] Unit 1: Core Data Structures (ConcernLevel, TrustTier, trust/penalty calculations) — 53 tests
  - [x] Unit 2: Tactical Trigger Evaluators (aggressive, cautious, literal) — 36 tests
  - [x] Unit 3: Strategic Trigger Evaluators (HOLD, PURSUE, MOVE_TO, SUPPORT) — 30 tests
  - [x] Unit 4: Pipeline Integration (V2 evaluators wired into executor.py) — 6 tests
  - [x] Unit 5: Vindication Extension (pending_defensive_vindication) — 2 tests
  - [ ] Unit 6: Test Migration (update existing tests asserting severity floats)
  - [ ] Unit 7: Godot Frontend (tone-based styling, MILD flavor in turn log)
- [ ] Begin Phase 6 design after V2a ships

---

## Recently Completed

### Feb 5

**V2a Units 4 & 5 (commit e04405b):**
- **Unit 4:** Pipeline integration — V2 evaluators wired into executor.py
  - `evaluate_situation()` + `apply_mood_variance()` replace V1 `evaluate_order()`
  - MILD concerns → append to `world.mild_concerns_this_turn`, continue execution
  - MODERATE+ → per-marshal popup cap, tone/insist_penalty from trust tier
  - WorldState: `mild_concerns_this_turn`, `objection_popups_this_turn` fields
  - main.py: mild_concerns passthrough in response
- **Unit 5:** Added `pending_defensive_vindication` to VindicationTracker
- **Opus 4.6 review fixes:**
  - Fix: `"order"` → `"original_order"` key mismatch (would crash on insist)
  - Fix: `game_state` variable shadowing dropping `debug_mode` key
  - Fix: Removed unused `target` variables in message generators

**V2a Units 1-3:**
- Core data structures (ConcernLevel, TrustTier enums, trust gain/penalty tables)
- Tactical trigger evaluators (personality × situation → ConcernLevel)
- Strategic trigger evaluators (evaluate_strategic_situation dispatcher)
- 119 new tests

**Documentation consolidation:**
- CLAUDE.md trimmed from 1661 → 268 lines
- docs/ consolidated from 21 → 11 active files + 3 archived
- New merged docs: SYSTEMS_REFERENCE.md, OBJECTION_V2.md, ADDING_CONTENT.md

### Feb 4

- Timed HOLD expiry fix, redundant HOLD blocking, Davout HOLD auto-fortify
- Personality-specific HOLD completion messages
- `/debug freeze_enemies` command
- Test count: **1066 passed, 3 skipped**

### Feb 3

- Phase M complete: Strategic Objections (47 tests)
- Strategic objections use probability system (trust, authority, vindication)

### Feb 2

- Phase K playtesting: 8 bugs found and fixed during Godot smoke testing
- SUPPORT auto-follow, morale scaling, sally battle fixes
- Test count: **1004 passed**

### Previous Sessions

- Phase 5.2 Strategic Commands: 100% complete (MOVE_TO, PURSUE, HOLD, SUPPORT)
- Phase 5.3 Enemy AI fixes: stagnation counter, oscillation fixes
- Modding system: 66 tests, validator tool, example mods
- Serialization enforcement: 33 roundtrip tests

---

## Test Count History

| Date | Tests | Notes |
|------|-------|-------|
| Feb 5, 2026 | **1203** | V2a Units 1-5 complete, Opus review fixes |
| Feb 5, 2026 | 1195 | V2a Units 1-3 (119 new tests) |
| Feb 4, 2026 | 1066 | HOLD improvements, personality benefits |
| Feb 3, 2026 | 1066 | Phase M complete |
| Feb 2, 2026 | 1004 | Phase K playtesting fixes |
| Jan 31, 2026 | 1022 | PURSUE completion fix, code review |
| Jan 30, 2026 | 981 | Doc cleanup session |

---

## Known Issues

| Issue | Severity | Notes |
|-------|----------|-------|
| V1 `handle_objection_response` still uses V1 trust values | Medium | Wire V2 scaled trust gain/penalty in Unit 6 |
| Strategic objections still use V1 `check_strategic_objection()` | Low | Migrate to V2 `evaluate_strategic_situation()` follow-up |
| Clarification popup for other literal actions | Low | Only attack-without-target currently |

---

## Next Session Priorities

1. **Unit 6: Test Migration** — Update existing tests that assert severity floats
2. **Unit 7: Godot Frontend** — Tone-based styling, MILD flavor in turn log
3. Begin Phase 6 design after V2a ships

**V2 objection design doc:** `docs/OBJECTION_V2.md`

---

## Quick Commands

```bash
pytest tests/ -v                          # Full suite
pytest tests/ -v --tb=no -q              # Quick count
pytest tests/test_objection_v2.py -v     # V2 tests only
python backend/main.py                    # Backend on port 8005
```

---

## Document Map

| Need | Read |
|------|------|
| Phase timeline | `ROADMAP.md` |
| Game systems reference | `SYSTEMS_REFERENCE.md` |
| Enemy AI | `ENEMY_AI_REFERENCE.md` |
| V2 objection design | `OBJECTION_V2.md` |
| Save format | `SAVE_FORMAT_REFERENCE.md` |
| Adding content | `ADDING_CONTENT.md` |
| Game vision | `VISION.md` |
| Future concepts | `FUTURE_DESIGN.md` |
| Modding | `MODDING_FORMAT.md` |
