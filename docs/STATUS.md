# Ink & Iron: Current Status

> **Updated every session by Claude Code.**
> **Last Updated:** February 5, 2026
> **Last Session:** Audit fix session — bug fixes, dead code removal, cleanup

---

## Quick Stats

| Metric | Value |
|--------|-------|
| **Tests Passing** | **~1203** (needs verification — venv broken in CLI, run in PyCharm) |
| **Current Phase** | V2a (Objection Refactor) — then Phase 6 |
| **Blockers** | Windows Store Python broken — run tests from PyCharm |
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

### Feb 5 (Session 3: Audit Triage)

**Triaged 15 findings from Enemy AI + V2a audits (3 fixed, 12 tracked):**
- **BUG FIX:** `_failed_action_cooldowns` destroyed every turn — EnemyAI was recreated each turn, resetting cooldowns. Moved to `WorldState.ai_failed_action_cooldowns` (same pattern as `ai_stagnation_turns`). Cooldowns now persist across turns.
- **BUG FIX:** Aggressive retreat: outnumbered 2:1 + high morale fell through to NONE (no concern). Now returns MILD.
- **DOC FIX:** Trust gain spec table in OBJECTION_V2.md used rounded values but code uses `int()` truncation. Updated spec to match code.
- **Tracked:** 7 items to STATUS.md Known Issues, 3 items to ROADMAP.md phase notes, 6 code TODOs added

### Feb 5 (Session 2: Audit Fixes)

**Architecture audit fix session:**
- **BUG FIX:** Cavalry double-increment of `turns_fortified` — was reaching 3-turn limit in 2 turns
- **BUG FIX:** `active_battles` participants used Python `set` (not JSON-serializable) → changed to `list`
- **BUG FIX:** `defense_bonus` type annotation was `int`, actual usage is `float` (0.16 = 16%)
- **BUG FIX:** `just_retreated` legacy flag removed — forced retreat now uses proper `retreating`/`retreat_recovery` system
- **BUG FIX:** Debug command `/debug restless` was setting wrong field (`turns_defensive` instead of `turns_in_defensive_stance`)
- **Dead code removed:** `PERSONALITY_TRAITS` dict, `_action_bonuses`, `turns_defensive` legacy field, `fortify_expires_turn` (always -1), `__main__` test block
- **Serialization:** `_recovery_destination` formalized in `__init__`, `to_dict()`, `from_dict()`
- **Debug prints:** 150+ bare `print()` in world_state.py, turn_manager.py, combat.py → gated behind `debug_print()` (set `INK_DEBUG=0` to silence)
- **Duplicates consolidated:** `ordinal()` function → `backend/utils/__init__.py`; `decay_config` dict → module-level `FORTIFY_DECAY_CONFIG` constant
- **getattr cleanup:** 20+ unnecessary `getattr(self, 'field', default)` → direct `self.field` in marshal.py
- **Doc fixes:** SYSTEMS_REFERENCE.md shock bonus +50% → +20%, `until_destroyed` → `until_marshal_destroyed`, `target_type` values corrected
- **Godot fixes:** Removed unused `fortify_expires_turn` var from map.gd, renamed `turns_defensive` → `turns_in_defensive_stance`

### Feb 5 (Session 1: V2a + Docs)

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
| Feb 5, 2026 | **~1203** | Audit fixes (need PyCharm verification) |
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
| Strategic objections still use V1 `check_strategic_objection()` | High | V2 strategic evaluators (30 tests) exist but aren't wired into executor.py:2607. Migrate in Unit 6. The 30 strategic V2 tests provide false confidence — they test functions the game never calls. |
| V1 `evaluate_order()` still called for alternative generation | Medium | executor.py:892 calls V1 to extract alternatives for V2 popups. Replace with V2-native alternatives in Unit 6. |
| V1 global objection cap still active for strategic path | Medium | `disobedience.py:25` MAX_MAJOR_OBJECTIONS_PER_TURN=2. V2 says per-marshal cap only. Remove when strategic objections migrate to V2. |
| No integration tests for V2 tactical pipeline | Medium | 127 V2 tests cover evaluators in isolation; no test verifies full executor→evaluate→popup→response path. Add in Unit 6. |
| No mid-objection save/load roundtrip test | Low | Serialization enforcement confirms fields exist, but no test saves/loads with populated V2 pending_objection. |
| Missing AI test coverage for P3, P4.75, P7 | Medium | P3 (threat response), P4.75 (ally support), P7 (strategic movement) have zero direct unit tests. |
| Residual 2-turn fortify oscillation possible | Low | `_unfortified_this_turn` only prevents same-turn re-fortify. Next-turn re-fortify→P3.5 unfortify cycle possible. Stagnation counter is backstop. TODO in `enemy_ai.py` at P3.5. |
| `requires_input` interrupt blocks later marshals | Low | `strategic.py:119` stops processing ALL further marshals when one requires player input. Later marshals' strategic orders starve if early marshal always has interrupts. TODO in `strategic.py`. |
| ~~Clarification popup for other literal actions~~ | ~~Fixed~~ | Works for all strategic types + attack-without-target (verified Feb 5) |
| Windows Store Python broken | Env | venv can't find base python — run tests from PyCharm |
| Marshal ability dicts mostly decorative | Low | Only Ney's "Bravest of the Brave" is wired up in combat.py; others are TODO (personality mechanics DO work separately) |

---

## Next Session Priorities

1. **Run full test suite in PyCharm** — verify audit fixes didn't break anything
2. **Unit 6: Test Migration** — Update existing tests that assert severity floats
3. **Unit 7: Godot Frontend** — Tone-based styling, MILD flavor in turn log
4. Begin Phase 6 design after V2a ships

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
