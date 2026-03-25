# Systems Audit V2 — Fix Plan

**Created:** 2026-03-25
**Source:** `audit-report-systems-v2.md` (99 findings across 4 phases)
**Verification:** 6 sub-agents confirmed findings against live code

---

## Verification Summary

| Category | Audit Claimed | Confirmed TRUE | FALSE/Downgraded | Notes |
|----------|---------------|----------------|------------------|-------|
| CRITICAL | 3 | 2 + 1 upgraded | 0 | V2-27 upgraded from MAJOR |
| MAJOR code | 24 | 21 | 3 partial | V2-57 dead code, V2-71 partial, V2-86 partial |
| MAJOR design/docs | 6 | 6 | 0 | |
| MAJOR test quality | 3 | — | — | Not code-verified (separate scope) |
| MINOR | 34 | 27 | 4 false/partial | V2-52, V2-54, V2-58 (see §V2-58), V2-91, V2-99 |
| NOTE | 32 | N/A | N/A | Verified/deferred/informational |

### Findings Marked FALSE

- **V2-91** (FALSE) — Auto-charge loop uses `list(self.marshals.values())` snapshot. Controller mutations mid-loop do not affect the marshal iteration. Safe.
- **V2-99** (PARTIAL → not a bug) — Continental System `max(0, nation_gold - blocked)` operates on total gold, which is correct. You can't lose more gold than you have.

### Findings Downgraded

- **V2-52** (PARTIAL) — Vindication is processed at turn-start via `_process_vindication_decay()`, not per-battle. Auto-charge not calling vindication is consistent with design, though an architectural gap.
- **V2-54** (PARTIAL) — Asymmetric `world` None guard in glorious charge is a code smell. `game_state.get("world")` should never return None in production. Low risk.
- **V2-57** (PARTIAL) — Strategic parser bare verbs ("advance", "push", "head") are unreachable because mock parser requires directional suffixes. Dead code, not causing errors. Cleanup only.

### Findings Upgraded

- **V2-27** (MAJOR → CRITICAL) — Davout free unfortify exploit. Player can fortify 7 turns (max defense), unfortify free (0 AP for cautious), re-fortify same turn (1 AP). Decay timer resets to 0. Infinite max defense with no decay ever triggering. Actively exploitable.

### V2-58 Deep Dive: "hold" Strategic Upgrade

**Audit claim:** Any "hold" command always upgrades to strategic HOLD (2 AP), no way to issue 1 AP tactical defend.

**Verification agent verdict:** FALSE — claimed conditions must be present for upgrade.

**Actual code analysis:** The verification agent was **incorrect**. Tracing the full flow:

1. Player types: `"Ney, hold"`
2. Mock parser (`llm_client.py:673`): `"hold" in command_lower` → `action = "hold"` (tactical)
3. Parser validates successfully
4. Strategic detection runs (`parser.py:422`): `detect_strategic_command("Ney, hold", "Ney", world)`
5. Inside `strategic_parser.py`:
   - `_strip_marshal_prefix("ney, hold", "Ney")` → `"hold"`
   - `_detect_strategic_type("hold")` → word-boundary match on "hold" in HOLD keywords (line 179) → returns `"HOLD"`
   - `_extract_target_text("hold", "HOLD")` → splits `"hold"` by `"hold"` → after = `""` → returns `None`
   - Fallback (line 241): `strategic_type == "HOLD"` AND `marshal_name` AND `world` exist → returns strategic dict with `target = marshal.location`, `condition = None`
6. Parser applies upgrade: `result["is_strategic"] = True`, `result["strategic_type"] = "HOLD"`

**Result:** Bare "hold" IS upgraded to strategic HOLD (2 AP), even with no condition.

**However, this is a MINOR design issue, not a MAJOR bug**, because:
- `"defend"` is NOT in the strategic HOLD keywords list — players CAN still issue 1 AP tactical defend by saying "Ney, defend"
- The semantic distinction ("hold position" = ongoing, "defend" = immediate) is arguably correct
- The misleading comment at `strategic_parser.py:195` (`"hold" → tactical hold (1 action)`) should be updated to reflect actual behavior

**Final verdict:** TRUE but downgraded to MINOR. Fix: update the comment at line 195 to document that "hold" is strategic and "defend" is the tactical alternative. Optionally add a player-facing hint when HOLD order is issued.

---

## Root Cause Patterns

### Pattern 1: Triple Post-Combat Duplication (12 bugs)
`_execute_attack`, `_execute_glorious_charge`, and `_process_reckless_cavalry_turn_start` each have independent ~300-line inline post-combat blocks. Auto-charge is the most degraded copy, missing 8+ systems. **V2-44, V2-45, V2-46, V2-47, V2-48, V2-49, V2-50, V2-51, V2-53, V2-4, V2-2, V2-92.**

### Pattern 2: Single-Field Dialogue Overwrite (4 bugs)
`pending_diplomatic_dialogue` holds ONE blocking dialogue. Six systems write to it during `advance_turn`. Last writer wins. Alliance paradox (a blocking player choice) is always lost. **V2-89, V2-90, V2-94, V2-86.**

### Pattern 3: Godot Success Override (cascading)
`api_client.gd` forces `success = true` on every HTTP 200, masking ALL backend application errors. Every error-handling path in `main.gd` is dead code. **V2-69**, with downstream effects on V2-72, V2-73.

### Pattern 4: Per-Nation Loop Side Effects (2 bugs)
Code inside `process_nation_turn()` (called once per enemy nation) decrements global cooldowns. With 4 nations, cooldowns tick 4x too fast. **V2-20, V2-21.**

### Pattern 5: Unserialized Transient State (4 bugs)
Fields set by TurnManager on WorldState are not in `to_dict`/`from_dict`. Graceful degradation but data loss on save/load. **V2-16, V2-66, V2-67, V2-68.**

---

## Session Plan

### Session 1: Auto-Charge & Glorious Charge Post-Combat [P0 — CRITICAL]

**Root cause fix — 12 bugs. Largest session.**

| Bug | Sev | Description | Fix |
|-----|-----|-------------|-----|
| V2-44 | CRIT | Zombie marshal — no surrounded fallback | Add else branch: broken state, strength reduction, capital teleport |
| V2-45 | MAJ | Missing fortification defense bonus | Calculate fort_bonus, pass to resolve_battle |
| V2-46 | MAJ | Retreat uses post-retreat enemy location | Save `battle_location` before any retreats, use for both |
| V2-47 | MAJ | Missing leapfrog check (cavalry jumps armies) | Add middle-region enemy check from _execute_attack |
| V2-48 | MAJ | Missing decisive victory coalition check | Add ratio/casualty check in defender-win branch |
| V2-49 | MAJ | Retreat missing 20+ state-clearing ops | Call `_apply_forced_retreat_or_break` or replicate all clears |
| V2-50 | MAJ | Missing Win/Loss relationship processing | Call `process_battle_relationships()` |
| V2-51 | MIN | Missing flanking/record_attack | Add `record_attack()` + `calculate_flanking_bonus()` |
| V2-53 | MIN | idle_turns not reset | Add `marshal.idle_turns = 0` |
| V2-4 | MIN | Territory capture skips fortified regions | Use `_attempt_region_capture` or equivalent |
| V2-2 | MIN | Glorious charge missing same-region engagement check | Add enemy-in-region check at top |
| V2-92 | MIN | Auto-charge targets retreated marshals | Filter `retreating`/`retreat_recovery` in `_find_nearest_enemy` |

**Files:** `world_state.py`, `executor.py`
**Approach:** Patch inline (safer than extracting shared function — refactor can be a future session).
**Tests:** ~15-20 new tests
**Risk:** HIGH — touches core combat. Thorough test coverage essential.

---

### Session 2: Godot Frontend Fixes [P0 — CRITICAL]

**1 CRITICAL + 5 MAJOR + 4 MINOR. Blocks playtesting.**

| Bug | Sev | Description | Fix |
|-----|-----|-------------|-----|
| V2-69 | CRIT | `success=true` override on HTTP 200 | Remove `response_data["success"] = true` line |
| V2-70 | MAJ | Bombardment shows 8000% instead of 80% | Remove second `* 100` in main.gd |
| V2-72 | MAJ | Connection failure leaves input disabled | Add `set_input_enabled(true)` in failure branch |
| V2-73 | MAJ | HTTPRequest race → ERR_BUSY → frozen input | Add request queue or busy guard with callback |
| V2-30 | MAJ | Strategic Ledger missing trade income line | Add `trade_income` display in `_render_economy()` |
| V2-71 | MAJ | Load game missing AP/diplo/war panel restore | Verify nested `game_state` extraction; add missing fields |
| V2-74 | MIN | Turn display "5" not "5/40" after load | Format as `str(current_turn) + "/" + str(max_turns)` |
| V2-75 | MIN | Early returns skip diplomatic top bar update | Add `_update_diplomatic_top_bar(response)` to early returns |
| V2-76 | MIN | Load doesn't clear pending state | Clear all `pending_*` fields in `_on_load_result` |
| V2-77 | MIN | `tactical_events` and `command_report` silently dropped | Read and display these backend keys |

**Files:** `api_client.gd`, `main.gd`, `strategic_ledger.gd`
**Tests:** curl verification for backend; manual Godot testing
**Risk:** MEDIUM — mostly isolated UI fixes, except V2-73 (request queue) which needs careful design.

---

### Session 3: AI + Economy + Turn Manager [P1 — Before EA] ✅ COMPLETE

**5 MAJOR + 4 MINOR. All 9 bugs fixed, 20 new tests (6,967 total).**

| Bug | Sev | Description | Fix |
|-----|-----|-------------|-----|
| V2-5 | MAJ | LLM prompt leaks all enemy data through fog | Filter `get_enemy_marshals()` through `world.intel` visibility |
| V2-20/21 | MAJ | AI cooldowns tick 4x per turn (per-nation loop) | Move `_decrement_cooldowns` + refortify decrement to `turn_manager.py` before nation loop |
| V2-19 | MAJ | Enemy phase try/except swallows state mutations | Log error visibly; capture partial results before exception |
| V2-29 | MAJ | Supply attrition creates 0-strength zombie marshals | Pop marshals at `strength <= 0` after attrition loop |
| V2-26 | MIN | Autonomous marshal phase has no error handling | Add try/except matching enemy phase pattern |
| V2-81 | MIN | `max_free_actions = 2` assigned but never checked | Wire up `free_action_count >= max_free_actions` guard |
| V2-24 | MIN | Overwatch self-count inflates penalty | Add `m.name != target.name` exclusion |
| V2-96 | MIN | AI gets 75g vs player 25g per unused admin AP | Document asymmetry or align values (design decision) |

**Files:** `main.py`, `prompt_builder.py`, `enemy_ai.py`, `turn_manager.py`, `world_state.py`
**Tests:** ~10-12 new tests
**Risk:** MEDIUM — V2-20/21 is a targeted move; V2-5 needs careful fog integration.

---

### Session 4: Diplomacy State + Pacing [P1 — Before EA] ✅ COMPLETE

**7 MAJOR + 1 MINOR. 8 bugs fixed, 25 new tests (6,992 total).**

| Bug | Sev | Description | Status |
|-----|-----|-------------|--------|
| V2-89 | MAJ | `pending_diplomatic_dialogue` is single field — 6 writers overwrite | **FIXED** — Added `pending_dialogue_queue` list. Writers during advance_turn append to queue. Priority-based pop (alliance_paradox > vassal > sabotage > ai_proposal). Auto-pop in `_include_popup_passthroughs()`. |
| V2-90 | MAJ | Multiple vassal rebellions overwrite popup/dialogue | **FIXED** — Added `vassal_rebellion_imminent_popups` list. Auto-pops to singular field. Release clears from both list and queue. |
| V2-65 | MAJ | Broken marshals teleport to enemy-occupied capital | **FIXED** — Added `find_safe_spawn()` BFS helper. Applied at all 3 teleport sites (executor.py, world_state.py x2). |
| V2-85 | MAJ | No turn-limit warning system | **FIXED** — `_build_turn_limit_warning()` in dispatch.py. Fires at turns 35 (5 left), 38 (2 left), 39 (final). Notification via TURN_LIMIT_WARNING type. |
| V2-86 | MAJ | Victory swallows pending diplomatic popups | **FIXED** — `_flush_pending_popups_into()` on both pre-enemy and enemy victory return paths. |
| V2-63 | MAJ | Victory threshold mismatch (0.77 vs 0.75) | **FIXED** — `_check_victory_conditions()` now uses `VICTORY_REGION_FRACTION` constant. |
| V2-64 | MAJ | Triple victory check can conflict | **FIXED** — Removed victory check from `advance_turn()`. Turn manager is single authority. |
| V2-16 | MIN | Dynamic trust attrs bypass cap on save/load | **FIXED** — Replaced `setattr(marshal, f"_diplomatic_trust_this_turn_{turn}", ...)` with `world.diplomatic_trust_applied` dict. Serialized + cleared per turn. |

**Files:** `turn_manager.py`, `world_state.py`, `executor.py`, `dispatch.py`, `ai_diplomacy.py`, `diplomacy.py`, `vassal.py`, `coalition.py`, `main.py`, `notifications.py`
**Tests:** 25 new tests in `test_systems_audit_v2_session4.py`
**Risk:** HIGH — dialogue queue is a structural change touching 6 writer sites + 3 reader sites. Needs careful serialization.

**Dialogue Queue Design Notes:**
```python
# Current (broken):
world.pending_diplomatic_dialogue = {...}  # Single dict, last writer wins

# Proposed:
world.pending_dialogue_queue = []  # List of dicts, priority-ordered
# Writers append; reader pops first item; serialize the queue
# Priority: alliance_paradox > vassal_rebellion > sabotage_discovery > ai_proposal
```

---

### Session 5: Parser Fixes [P2 — Quality of Life] ✅ COMPLETE

**2 MAJOR + 6 MINOR. All 8 bugs fixed, 26 new tests (7,018 total).**

| Bug | Sev | Description | Fix |
|-----|-----|-------------|-----|
| V2-55 | MAJ | "ney" matches inside "journey", "money" | Use word-boundary regex `r'\bney\b'` for all marshal extraction |
| V2-56 | MAJ | "dig in" → fortify vs HOLD conflict | Remove "dig in" from strategic HOLD keywords |
| V2-59 | MIN | "commands" substring false positive | Change to exact match or `r'\bcommands\b'` at start/end |
| V2-60 | MIN | Reynier missing from mock parser | Add `("reynier", "Reynier")` to `known_marshals` |
| V2-61 | MIN | `parse_multiple` splits on " and " naively | Only split on " and " between marshal names, not mid-phrase |
| V2-62 | MIN | "court " matches "court martial" | Use `r'\bcourt\b'` instead of `"court "` |
| V2-57 | MIN | Bare verbs dead code in strategic parser | Remove "advance", "push", "head" from MOVE_TO bare verbs |
| V2-22 | MIN | AI stance change doesn't verify follow-up budget | Add AP budget check before returning stance_change |

**Files:** `llm_client.py`, `strategic_parser.py`, `parser.py`, `enemy_ai.py`
**Tests:** ~8-10 new tests
**Risk:** LOW — isolated string matching changes. Easy to test.

---

### Session 6: Hardcoded Values + Serialization + Dead Code + Cleanup [P2 — Polish]

**1 CRITICAL (design) + 1 MAJOR + 10 MINOR + docs.**

| Bug | Sev | Description | Fix |
|-----|-----|-------------|-----|
| V2-27 | CRIT | Davout free unfortify resets decay timer | Track `cumulative_fortification_turns` that persists through unfortify cycles |
| V2-78/79 | MAJ | Hardcoded "Paris" (2 locations) | Use `NATION_CAPITALS.get(nation, "Paris")` |
| V2-66 | MIN | `_capital_proximity_last_alert` not serialized | Add to WorldState `to_dict`/`from_dict` |
| V2-67 | MIN | `_prev_war_exhaustion` not serialized | Add to `to_dict`/`from_dict` |
| V2-68 | MIN | `_relation_deltas_this_turn` not serialized | Add to `to_dict`/`from_dict` |
| V2-93 | MIN | Broken marshal spawn = battle location is no-op | Find nearest friendly region if capital == battle site |
| V2-80 | MIN | SYSTEMS_REFERENCE says 75g, code uses 25g | Update doc to match code |
| V2-82 | MIN | SAVE_FORMAT missing 3 fields | Add `ai_stagnation_turns`, `ai_attack_futility`, `last_redemption_turn` |
| V2-83 | MIN | SYSTEMS_REFERENCE missing S11-12 changes | Document VICTORY_REGION_FRACTION, naval scaling, futility decay, etc. |
| V2-84 | NOTE | 7 stale TODO comments in diplomacy.py | Remove references to completed Sessions 3/5/7 |
| V2-58 | MIN | "hold" dead code + misleading comment | See below |

**V2-58 Detail: "hold" tactical dead code cleanup.**
- `_execute_hold()` at `executor.py:5342` is unreachable in gameplay. The strategic parser intercepts bare "hold" (via `strategic_parser.py:179` keyword match) and upgrades it to strategic HOLD (2 AP) before the tactical routing at `executor.py:2526` can fire. The only way `_execute_hold()` runs is if `world` is None (test-only path).
- **Fix steps:**
  1. Remove `_execute_hold()` from executor.py (dead code)
  2. Remove the `elif action == "hold"` routing at `executor.py:2526-2528`
  3. In mock parser (`llm_client.py:673-674`), change `action = "hold"` to `action = "defend"` so bare "hold" maps to defend (1 AP tactical) as the base action before strategic upgrade
  4. Update comment at `strategic_parser.py:195` to accurately document: "hold" is always upgraded to strategic HOLD (2 AP). Players wanting 1 AP tactical defend should use "defend"
  5. Grouchy's Immovable bonus (the only unique thing in `_execute_hold`) must be preserved — move the `holding_position = True` / `hold_region` logic into the strategic HOLD path at `executor.py:6129-6137` where it already partially exists
- **Impact:** Removes ~50 lines of dead code, eliminates player confusion about hold vs defend AP costs

**Files:** `personality.py`, `strategic_parser.py`, `world_state.py`, `executor.py`, `marshal.py`, `llm_client.py`, docs
**Tests:** ~6-8 new tests + serialization enforcement pass
**Risk:** LOW — mostly isolated fixes and doc updates. V2-58 needs care to preserve Grouchy Immovable.

---

### Session 7 (Optional): Test Quality Hardening [P3]

**3 MAJOR test issues + coverage gaps. Does not fix gameplay bugs.**

| Bug | Sev | Description | Fix |
|-----|-----|-------------|-----|
| V2-35 | MAJ | 3 test classes re-implement production logic | Rewrite to call `advance_turn()` / production functions |
| V2-36 | MAJ | Combat tests with conditional assertions | Force deterministic outcomes via mock RNG |
| V2-37 | MAJ | 46 test methods with zero assertions | Add assertions or delete; net count may decrease |
| V2-38/39 | MAJ | Missing tests for V2-5 (fog), V2-16 (trust cap) | Write targeted tests |
| V2-40 | MIN | No test for 2 reckless marshals same region | Write multi-cavalry test |
| V2-41 | MIN | `_make_marshal` duplicated across 30 files | Create shared `conftest.py` fixture |
| V2-42/43 | MIN | Exact string + docstring assertions | Replace with behavioral `in` checks |

**Files:** `tests/` directory
**Tests:** Net reduction (removing hollow tests) + new meaningful coverage
**Risk:** LOW — test-only changes, no production code.

---

## Session Priority & Dependencies

```
Session 1 (Auto-Charge)  ──┐
                            ├── P0: Blocks playtesting
Session 2 (Godot)        ──┘

Session 3 (AI/Economy)   ──┐
                            ├── P1: Before EA
Session 4 (Diplomacy)    ──┘

Session 5 (Parser)        ──┐
                            ├── P2: Quality polish
Session 6 (Cleanup)       ──┘

Session 7 (Tests)          ── P3: Optional hardening
```

Sessions 1 and 2 are independent (backend vs frontend) and can run in parallel if desired.
Sessions 3 and 4 are independent and can run in parallel.
Sessions 5 and 6 are independent and can run in parallel.
Session 7 has no dependencies.

---

## Estimated Totals

| Metric | Count |
|--------|-------|
| Confirmed bugs to fix | 56 |
| New tests (estimated) | 65-75 |
| Files touched | ~25 |
| Required sessions | 6 |
| Optional sessions | 1 |

---

## Session Completion Protocol

**After completing each session, Claude MUST:**

1. Update this file: mark the session DONE with date, bug count, test count
2. Update `docs/STATUS.md`: mark the session done, change "UP NEXT" to the next session number
3. Run full test suite and record pass count
4. If a session is split across multiple conversations, note where you left off

### Progress Tracker

| Session | Status | Date | Bugs Fixed | Tests Added |
|---------|--------|------|------------|-------------|
| S1: Auto-Charge | **COMPLETE** | 2026-03-25 | 12 | 17 |
| S2: Godot | **COMPLETE** | 2026-03-25 | 10 | 0 (GDScript) |
| S3: AI/Economy | **COMPLETE** | 2026-03-25 | 9 | 20 |
| S4: Diplomacy/Pacing | **COMPLETE** | 2026-03-25 | 8 | 25 |
| S5: Parser | **COMPLETE** | 2026-03-25 | 8 | 26 |
| S6: Cleanup/Dead Code | PENDING | — | — | — |
| S7: Test Quality | PENDING (optional) | — | — | — |

---

## Excluded From Plan

These findings are verified correct / intentional / deferred:

| ID | Reason |
|----|--------|
| V2-1 | Design debt (triple duplication). Session 1 patches inline; full extraction deferred. |
| V2-3, V2-6-V2-15, V2-17-V2-18, V2-23, V2-25, V2-34 | Verified fixed / N/A / deferred by design |
| V2-28 | Cautious+HOLD 0.25%/turn decay — design note, V2-27 addresses root cause |
| V2-31 | Supply stacking cliff at 3 marshals — intentional design |
| V2-32 | Futility 3-turn oscillation — mitigated by existing systems |
| V2-33 | Notification list unbounded for HIGH/CRITICAL — acceptable for 40-turn games |
| V2-87 | Auto-charge victory doesn't short-circuit advance_turn — harmless |
| V2-88 | Double victory check ordering — technically correct (defeat wins) |
| V2-91 | FALSE — loop snapshot protects against mutation |
| V2-94 | Sabotage overwrites vassal dialogue — subsumed by V2-89 dialogue queue fix |
| V2-95 | Cumulative loyalty penalty from cascading rebellions — subsumed by V2-90 |
| V2-97 | Bankruptcy desertion loop — self-limiting, 40-turn cap makes it academic |
| V2-98 | AI supply awareness priority — design choice, acceptable |
| V2-99 | Continental System floor — correct behavior |
