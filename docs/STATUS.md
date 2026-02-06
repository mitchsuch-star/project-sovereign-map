# Ink & Iron: Current Status

> **Updated every session by Claude Code.**
> **Last Updated:** February 5, 2026
> **Last Session:** Session 6 — Bug Fixes + Roadmap

---

## Quick Stats

| Metric | Value |
|--------|-------|
| **Tests Passing** | **1216** (verified, 3 skipped) |
| **Current Phase** | V2a **COMPLETE** — Begin Phase 6 |
| **Blockers** | None |
| **Phases Complete** | 1, 2, 2.5, 2.9, 3, 4, 5.1, 5.2, 5.3, M, V2a |

---

## Active Work

**V2a Objection Refactor: COMPLETE** (all 7 units done).

- [x] Phase M: Strategic Objections
- V2a: Objection System Refactor — **COMPLETE**
  - [x] Unit 1: Core Data Structures (ConcernLevel, TrustTier, trust/penalty calculations) — 53 tests
  - [x] Unit 2: Tactical Trigger Evaluators (aggressive, cautious, literal) — 36 tests
  - [x] Unit 3: Strategic Trigger Evaluators (HOLD, PURSUE, MOVE_TO, SUPPORT) — 30 tests
  - [x] Unit 4: Pipeline Integration (V2 evaluators wired into executor.py) — 6 tests
  - [x] Unit 5: Vindication Extension (pending_defensive_vindication) — 2 tests
  - [x] Unit 6: Integration Wiring + Test Migration — 13 new tests, 6 gaps resolved
  - [x] Unit 7: Godot Frontend (tone-based styling, MILD "Field Dispatches", trust previews)
- [ ] Begin Phase 6 design

---

## Recently Completed

### Feb 5 (Session 6: Bug Fixes + Roadmap)

**Bug fixes:**
- **BUG FIX:** Defend order allowed when already in defensive stance + fortified. `_execute_defend()` returned `success: True` with `variable_action_cost: 0` (wasted no AP but gave misleading feedback). Now returns `success: False` with clear message.
- **BUG FIX:** Post-turn strategic reports missing after insist/proceed on objection. `/respond_to_objection` endpoint was not passing `strategic_reports` from executor result. Added `strategic_reports` to response dict.

**Roadmap:**
- Moved Voice-to-Text from Post-EA (LOW) to Pre-EA Polish (killer feature). Added architecture notes: Whisper API or browser SpeechRecognition -> existing parser pipeline. ~$0.012/game cost.

### Feb 5 (Session 5: V2a Unit 6 — Integration Wiring)

**Unit 6: V2a Integration Wiring + Test Migration (6 gaps resolved):**
- **Gap 1 (Doc):** Compromise math note for DEVOTED+MODERATE in OBJECTION_V2.md §2.3
- **Gap 2 (idle_turns):** Added `idle_turns` field to Marshal — increments per turn if idle, resets on attack/move. Serialization roundtrip tested. V2b will use for idle objection triggers.
- **Gap 3 (V2 trust scaling):** Wired `calculate_trust_gain()`, `get_insist_penalty()`, `COMPROMISE_TRUST_GAIN` into tactical and strategic objection dicts. Replaced all hard-coded +12/-10/-15/+3 values.
- **Gap 4 (Insist bypass):** Removed V1 disobedience roll from `handle_response()`. Insist always succeeds in V2a. V2b comment block preserved for future defiance mechanic.
- **Gap 5 (V1 evaluate_order shim):** Replaced V1 `evaluate_order()` call with direct `_generate_alternative()` + `_find_compromise()` calls, bypassing V1 severity calculation entirely.
- **Gap 6 (Strategic V2 wiring):** Replaced V1 `check_strategic_objection()` with V2 `evaluate_strategic_situation()` + `apply_mood_variance()`. Added per-marshal popup cap, MILD path for strategic, V1 helpers retained only for option extraction.
- **Test migration:** 9 V1 tests updated to V2 semantics (mock mood variance, relaxed message assertions → concern_level checks). 1 test in `test_strategic_bugfixes.py` updated.
- **Integration tests:** 13 new tests — tactical full path (trust/insist/compromise), strategic full path, MILD no-popup, idle turns (increment/reset/enemy skip/acted flag/serialization/backward compat)
- **Test count: 1216 passed, 3 skipped, 0 failures**

**Unit 7: Godot Frontend:**
- Tone-based objection dialog: border color + header text by trust tier (respectful/firm/challenging/defiant)
- Trust change previews on all tactical objection buttons
- V2 field passthrough: tone, concern_level, trust_gain, insist_penalty, compromise_gain
- MILD "Field Dispatches" in turn log after enemy phase (warm gold, atmosphere text)

**V2a Objection Refactor: COMPLETE** — all 7 units shipped.

### Feb 5 (Session 4: EA Readiness & Vision Assessment)

- EA Readiness audit: full doc review, roadmap restructure
- Map decision: Option C (commission Europe, wire partial ~80-100 regions)
- Map approach: EU4-style bitmap color map (not SVG)
- Coalitions split from Phase 8 to Phase 7
- Phase 12 (Communication cutoff) deferred to Post-EA
- Naval abstraction deferred to Post-EA, Britain as off-map funder
- Phase 9 (Advisors) minimized: stats + flavor, no action gating
- Phase 11 reworked: vassals + authority-based loyalty, no naval
- Save/Load moved from Pre-EA to Phase 6
- Berthier Parse Recovery moved from Phase 8.5 to Phase 6
- New features added: Campaign Briefing, Marshal Report, Post-battle Analysis, Idle Marshal Objection, Grouchy Moment LLM, Intercepted Dispatches, Napoleon Comparison, LLM feature toggles, Short Waterloo Scenario
- Created TUTORIAL_SCRIPT.md (living document)
- ROADMAP.md fully restructured

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
| Feb 5, 2026 | **1216** | V2a Unit 6 complete, 13 new integration tests |
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
| ~~V1 `handle_objection_response` still uses V1 trust values~~ | ~~Fixed~~ | Unit 6 Gap 3: Wired V2 scaled trust gain/penalty into objection dicts |
| ~~Strategic objections still use V1 `check_strategic_objection()`~~ | ~~Fixed~~ | Unit 6 Gap 6: V2 `evaluate_strategic_situation()` now authoritative. V1 retained only for option extraction. |
| ~~V1 `evaluate_order()` still called for alternative generation~~ | ~~Fixed~~ | Unit 6 Gap 5: Replaced with direct `_generate_alternative()` + `_find_compromise()` calls |
| V1 global objection cap still active for strategic path | Low | `disobedience.py:25` MAX_MAJOR_OBJECTIONS_PER_TURN=2. V2 per-marshal cap is now authoritative for strategic; V1 cap is redundant backstop. Remove in V2b cleanup. |
| ~~No integration tests for V2 tactical pipeline~~ | ~~Fixed~~ | Unit 6: 13 integration tests cover full tactical path, strategic path, MILD path, insist path, idle turns |
| No mid-objection save/load roundtrip test | Low | Serialization enforcement confirms fields exist, but no test saves/loads with populated V2 pending_objection. |
| Missing AI test coverage for P3, P4.75, P7 | Medium | P3 (threat response), P4.75 (ally support), P7 (strategic movement) have zero direct unit tests. |
| Residual 2-turn fortify oscillation possible | Low | `_unfortified_this_turn` only prevents same-turn re-fortify. Next-turn re-fortify→P3.5 unfortify cycle possible. Stagnation counter is backstop. TODO in `enemy_ai.py` at P3.5. |
| `requires_input` interrupt blocks later marshals | Low | `strategic.py:119` stops processing ALL further marshals when one requires player input. Later marshals' strategic orders starve if early marshal always has interrupts. TODO in `strategic.py`. |
| ~~Clarification popup for other literal actions~~ | ~~Fixed~~ | Works for all strategic types + attack-without-target (verified Feb 5) |
| ~~Windows Store Python broken~~ | ~~Fixed~~ | venv working, tests run from CLI |
| Marshal ability dicts mostly decorative | Low | Only Ney's "Bravest of the Brave" is wired up in combat.py; others are TODO (personality mechanics DO work separately) |

---

## Next Session Priorities

1. **Godot smoke test** — Launch game, trigger objection, verify tone styling + dispatches
2. **Begin Phase 6 design** — Core Campaign (save/load, Berthier Parse Recovery)
3. Commission Europe map art (start search for artist)

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
