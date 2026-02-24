# Ink & Iron: Current Status

> **Updated every session by Claude Code.**
> **Last Updated:** February 23, 2026 (Session 62: Casualty Distribution)

---

## Quick Stats

| Metric | Value |
|--------|-------|
| **Tests Passing** | **3647** (3644 passed, 3 skipped — verified Feb 23) |

| **Current Phase** | Phase 7b **IN PROGRESS** (Session 62 complete, remaining: S63, S65, S66, Tactical Triangle, V2b, Coalition Trigger, Jealousy, Gneisenau). |
| **Blockers** | None |
| **Code Coverage** | ~71% (backend/) |

---

## Next Steps

1. **Phase 7 Core: COMPLETE.** All 7 sessions shipped (57-61b + 64). ~212 new tests.
2. **Phase 7b: IN PROGRESS.** Session 62 (Casualty Distribution) complete. Next: AI Coordination Enhancements (S63), Full Battle Reports (S65), Godot Tooltips/Tutorial (S66), Tactical Triangle, V2b, Coalition Trigger, Jealousy, Gneisenau Staff Work.
3. **Phase 6.5 remaining** — Map Renderer only (art-blocked). Tooltips absorbed into Map Renderer. Tutorial deferred to Pre-EA.

---

## Phase 6 Summary

All major Phase 6 features shipped:

- **Terrain (6.1):** 6 terrain types, weighted pathfinding, cavalry terrain scaling, charge blocking
- **Economy (6.2):** Region types, income/upkeep, stability, war damage, recruitment rework, buildings (4 types), supply limits, movement attrition, contested capture, AI admin phase — audited and balanced
- **Save/Load:** Manual save/load + autosave
- **Berthier Parse Recovery:** In-character error messages for unparseable commands
- **Battle Reports:** Template-based post-battle analysis with modifier snapshots, perspective-aware observations
- **Turn Events Log:** 13 event types, structured logging, hardened (EL1-EL5)
- **Fog of War:** Intel data model, visibility tiers, decay, watchtower building, strategic fog filtering, scout persistence, map visualization with fog overlay + fogged icons
- **Reinforcements, Attrition, City Fortification**
- **Player Garrison Command:** 2 AP, cap 3/nation, map overlay
- **Enemy AI Garrison (P6.75):** Building Blocks, 20k threshold, 1/nation/turn, P4.25 sub-5k awareness
- **Manpower Pools:** Nation-level infantry/cavalry/artillery reserves gate recruitment. Stables building. AI pool/cost awareness.
- **Artillery Unit Type:** Third marshal type (Drouot/PrinceAugust). Can't attack after moving, no advance on win, cavalry counter, 2x fort degradation. Bombardment system with terrain modifiers, collateral damage, AI bombardment. 127+ tests.

---

## Phase 7b Sessions

### Feb 23 — Session 62: Casualty Distribution

**47 new tests, 3647 total (3 skipped). Multi-marshal battles now distribute casualties proportionally among participants. First Phase 7b session.**

- **`resolve_battle(apply_casualties=False)`:** New contract per C1/C2. Computes all combat math but defers 5 side effect categories (casualties, morale, battles_won/lost, counter-punch, recklessness) to caller. Returns raw casualties, morale deltas (as int), and projected-strength outcome.
- **Fortification degradation KEPT** inside resolve_battle (battle-triggered per C1).
- **C2 projected-strength victor:** Uses `attacker.strength - casualties` for outcome determination. 1.5 threshold matches normal path.
- **`_distribute_casualties()`:** Proportional by strength fraction. Remainder to strongest marshal. Cap at marshal strength. Sum matches raw total exactly.
- **`_get_casualty_participants()`:** Mirrors `get_battle_participants()` for D3 Hostile+SUPPORT detection. Must run BEFORE strategic orders cleared.
- **Per-participant effects:** Uniform morale delta (psychological), individual battles_won/lost, independent forced retreat check.
- **Primary-only effects:** Recklessness (attacker), counter-punch (defender), counter-punch mastery (Davout).
- **Pursuit damage** handled in executor for coordinated battles (primary attacker ability vs primary defender).

**Files modified:** `combat.py` (apply_casualties parameter + `_build_deferred_result`), `executor.py` (`_distribute_casualties`, `_get_casualty_participants`, `_execute_attack` coordination branch).
**Files created:** `tests/test_casualty_distribution.py` (47 tests, 6 classes).

---

## Phase 7 Core Sessions

### Feb 23 — Session 64: Win/Loss Relationship Formula

**34 new tests, 3600 total (3 skipped). Shared battles now trigger relationship checks between co-located same-nation marshals. Phase 7 Core COMPLETE.**

- **`calculate_battle_severity()`:** Categorizes battles as decisive (ratio < 0.5), standard (0.5–0.8), or narrow (> 0.8) based on winner/loser casualty ratio.
- **`check_shared_battle_relationship()`:** WIN formula (base 30 + severity + rel_mod + variance ±10) and LOSS formula (base 15 + severity + rel_mod + variance ±10). Threshold strict `> 50` (M2). Returns ±1 or 0.
- **Ordered pairs (D4):** Uses `itertools.permutations` — 3 marshals = 6 independent checks. Cooldown is per-direction (A→B independent of B→A).
- **Intentional asymmetry (M1/M2):** Hostile WIN max=35 (never improves). Devoted WIN max=35 (never improves). Hostile LOSS max=50 (never degrades — strict > 50). Rival decisive WIN ~24% improvement chance.
- **Cooldown:** 3 turns per direction, tracked in `last_relationship_change_turn` (serialized in S59).
- **Participants:** Same-nation marshals in battle region, excluding Hostile without SUPPORT. Primary always included.
- **Event logging:** Relationship changes logged via `world.log_event()` with type `"relationship_change"`.
- **Files created:** `backend/game_logic/relationship.py`, `tests/test_relationship_formula.py` (34 tests).
- **Files modified:** `backend/commands/executor.py` (wired into `_execute_attack()` after combat notifications, before destruction check).

### Feb 23 — Session 61b: Reinforcement Edge Cases + SUPPORT Objection Triggers

**22 new tests, 3566 total (3 skipped). Edge cases for reinforcement eligibility, Grouchy Rule upgrade, Berthier advisory, and SUPPORT objection triggers.**

- **Rule #12 — moved_this_turn (A-D2):** Marshals that already moved this turn cannot reinforce (prevents force-marching twice). Blocks artillery that moved from reinforcing.
- **Rule #13 — Hostile exclusion (A-D4):** Hostile marshals (relationship -2) without a SUPPORT order targeting the primary combatant are excluded from auto-reinforcement. Hostile WITH SUPPORT still passes eligibility (arrives for casualties, 0% coordination per D3).
- **Grouchy Rule PURSUE region-match (A-D1):** Upgraded from name-match to region-match. Grouchy with `PURSUE Wellington` now arrives at a battle where Wellington is present, even if the primary defender is Blucher.
- **Berthier fortified SUPPORT advisory (A-M3):** When SUPPORT is issued to a fortified marshal, Berthier warns they cannot march to reinforce. Informational only — does not block the order.
- **§6 SUPPORT objection triggers:** Two new triggers in `objection_v2.py`: aggressive personality objects to defensive SUPPORT (target fortified/cautious/broken → MODERATE), cautious personality objects to reckless SUPPORT (target aggressive + recklessness ≥ 2 → MODERATE).
- **Files modified:** `executor.py` (rules 12-13, PURSUE region-match, Berthier advisory), `objection_v2.py` (SUPPORT triggers), `test_reinforcement.py` (updated hostile trust test for A-D4).
- **Files created:** `tests/test_reinforcement_edge_cases.py` (22 tests across 7 classes).

### Feb 23 — Session 61a: Adjacent Reinforcement (Arrival Score & Base Reinforcement)

**49 new tests, 3544 total (3 skipped, 1 pre-existing flaky). Adjacent marshals physically reinforce into ongoing battles.**

- **Reinforcement system:** Adjacent same-nation marshals automatically attempt to join ongoing battles. 11 eligibility rules (same nation, adjacent, strength > 0, not broken, not retreated, not recovering, not fortified, not on HOLD, not engaged, not drilling, not already reinforced).
- **Grouchy Rule (personality gate):** Literal-personality marshals CANNOT reinforce unless they have a SUPPORT or PURSUE order targeting a battle participant. Checked before arrival score.
- **Arrival score formula:** `base(50) + logistics*5 + relationship_mod + terrain_mod + personality_mod + support_bonus + variance(±8)`. Variable threshold: 60 with SUPPORT/PURSUE order, 65 without.
- **Fumble roll (I3):** 5% failure chance even when score > 80 (`random.randint(1,20) == 1`).
- **Physical relocation:** Successful reinforcers move to battle region, set `reinforced_this_turn = True`, join coordination calculation. Strategic orders preserved through coordination, then cleared after (A-C2 ordering).
- **Path B2 dedicated support:** Arrived-via-SUPPORT reinforcers count for `_has_dedicated_support()` coordination check.
- **Trust penalty:** -3 trust on failed reinforcement (except Literal and Hostile personalities).
- **Both sides reinforced:** Attacker and defender independently receive reinforcements (Building Blocks — AI uses identical code).
- **Serialization (M4):** `reinforced_this_turn` field serialized, cleared at turn start.
- **Files modified:** `executor.py` (+`_is_reinforcement_eligible`, `_calculate_arrival_score`, `_calculate_reinforcements`, extended `_execute_attack`, extended `_calculate_coordination_context`, extended `_has_dedicated_support`), `marshal.py` (+`reinforced_this_turn`), `world_state.py` (turn-start clearing).
- **Files created:** `tests/test_reinforcement.py` (49 tests across 12 classes).
- **Regression fixes:** 3 existing integration tests needed isolation from reinforcement side effects (reinforcement pulls adjacent marshals during AI attacks). Fixed by marking test-specific marshals as `reinforced_this_turn = True` or relocating enemies.

### Feb 23 — Session 60: Adjacent Support

**23 new tests, 3495 total (3 skipped). Adjacent-region coordination bonus (attack-only).**

- **Adjacent support bonus:** Marshals in regions adjacent to a battle provide +2% attack per ally. Purely positional — NOT relationship-scaled. Fortified and HOLD marshals count (physically present). Same eligibility as coordination (not broken, not retreating, not recovering, strength > 0).
- **Attack-only (A-M2):** Adjacent support adds to `raw_atk` ONLY. Defenders benefit only from same-region allies, not adjacent ones.
- **Pipeline integration:** `_count_adjacent_allies()` calculates ONCE per battle (shared value for all marshals in region), added to coordination sum BEFORE hard cap. Display field `_display_adjacent_atk` set on all eligible marshals, already in `COORDINATION_FIELDS` cleanup list.
- **Future-proofing (S61):** `exclude_names` parameter on `_count_adjacent_allies()` for Session 61 reinforcement (arriving marshals removed from adjacent count).
- **Combat message:** Adjacent support displays in tactical prefix when active.
- **Battle report:** `_display_adjacent_atk` captured in attacker snapshot as "Adjacent support" modifier.
- **Files modified:** `executor.py` (+`_count_adjacent_allies`, extended `_calculate_coordination_context`), `combat.py` (adjacent support message), `battle_report.py` (adjacent support snapshot).
- **Files created:** `tests/test_adjacent_support.py` (23 tests across 7 test classes).

### Feb 23 — Session 59: Dedicated Coordination

**31 new tests, 3472 total (3 skipped). Co-location tracking + dedicated coordination bonus.**

- **Co-location tracking:** `_update_co_location_tracking()` in `world_state.py` runs per-turn BEFORE turn increment (A-D7). Tracks `co_location_turns` dict on each marshal: ally_name → start_turn of co-location streak. Clears on separation, death, or broken status.
- **Dedicated bonus (Path A):** After 2+ consecutive co-located turns (`current_turn - start_turn >= 2`), marshal earns flat +5% attack / +5% defense. Doesn't scale with relationship or stack with multiple qualifying allies.
- **Dedicated bonus (Path B):** Active SUPPORT order targeting a marshal grants immediate +5%/+5%. One-directional per A-D3 — only the target gets the bonus, not the supporter. Mutual SUPPORT (4 AP) gives both.
- **Pipeline integration:** Dedicated bonus added to raw sum in `_calculate_coordination_context()` (combined arms + per-ally + dedicated), then hard-capped at +25% atk / +20% def. Display fields `_display_dedicated_atk`/`_display_dedicated_def` set on marshal, already in cleanup list.
- **Forward-compatibility field:** `last_relationship_change_turn` dict added to marshal (empty until Session 64 populates it). Serialization-enforced.
- **Files modified:** `marshal.py` (2 new Dict fields in `__init__`/`to_dict`/`from_dict`), `world_state.py` (+`_update_co_location_tracking`, call site in `_process_tactical_states`), `executor.py` (+`_has_dedicated_support`, extended `_calculate_coordination_context`), `tests/test_serialization_enforcement.py` (fixture updated).
- **Files created:** `tests/test_dedicated_coordination.py` (31 tests across 8 test classes).

### Feb 23 — Session 58: Per-Ally Coordination Bonuses

**44 new tests, 3438 total (3 skipped). Per-ally relationship-scaled coordination.**

- **Per-ally coordination:** Each eligible ally contributes +3% attack / +5% defense, scaled by relationship: Hostile(0.0) → Rival(0.5) → Professional(1.0) → Friendly(1.25) → Devoted(1.5). Asymmetric — each marshal gets their OWN total based on their relationships.
- **Fortification rule:** Fortified non-artillery allies give defense coordination only (0% attack). Fortified artillery gives both.
- **Hard cap enforced:** Combined arms + per-ally coordination summed, then capped at +25% attack / +20% defense. 3/3 France CA (20%) + 2 Professional allies (6%) = 26% → capped at 25%.
- **S57 tests updated:** 4 tests updated to account for per-ally coordination being additive with combined arms.
- **Files modified:** `executor.py` (+`_calculate_per_ally_coordination`, `_RELATIONSHIP_SCALING`, extended `_calculate_coordination_context` for per-marshal asymmetric calculation), `tests/test_combined_arms.py` (4 updated tests).
- **Files created:** `tests/test_coordination_bonus.py` (44 tests across 11 test classes).

### Feb 23 — Session 57: Combined Arms Detection

**43 new tests, 3394 total (3 skipped). Phase 7 Core begins.**

- **Combined arms detection:** Count distinct unit types (infantry/cavalry/artillery) among eligible same-nation marshals in a region. 2 types = +10% atk / +5% def. 3 types = +20% atk / +10% def. France is the only nation capable of 3/3 (structural player advantage).
- **Transient field pattern (D5):** Coordination bonuses set dynamically via `_calculate_coordination_context()`, read via `getattr(self, field, 0.0)`, cleared after combat. NOT in `__init__`, NOT serialized.
- **Single multiplier (A-C1):** `total_coordination_attack_bonus` / `total_coordination_defense_bonus` — one line each in `get_attack_modifier()` / `get_defense_modifier()`. All future coordination sources (per-ally, dedicated, adjacent) sum into this single field, then cap at +25% atk / +20% def.
- **Both sides calculated (A-C3):** `_calculate_coordination_context()` called for attacker AND defender independently before `resolve_battle()`.
- **Bombardment excluded (A-D6):** Coordination not wired into bombardment path.
- **Files modified:** `executor.py` (+`_count_unit_types`, `_get_combined_arms_bonus`, `_calculate_coordination_context`, `_clear_coordination_fields`, attack wiring), `marshal.py` (1 line each in atk/def modifiers), `combat.py` (combined arms tactical_prefix message), `battle_report.py` (snapshot captures CA + total coordination).
- **Files created:** `tests/test_combined_arms.py` (43 tests across 8 test classes).

---

## Phase 6.5 Sessions

### Feb 22 (Davout Counter-Punch Mastery + Special Abilities Evaluation)

**Davout's "Counter-Punch Mastery" ability wired. 22 new tests, 3351 total.**

- **Ability:** +20% attack on next attack after Davout is attacked (any combat outcome, any target). Boolean `counter_punch_ready` field — set when defender in combat (if survived), consumed on next `get_attack_modifier()` call, cleared at turn end if unused.
- **Files modified:** `marshal.py` (field + ability definition + modifier), `combat.py` (trigger + result flag), `battle_report.py` (snapshot label), `marshal_overview.py` (`_WIRED_ABILITY_MARSHALS` + unit specifics), `world_state.py` (turn-end clearing + game state summary), `executor.py` (broken state clearing).
- **6 wired abilities total:** Ney (+2 shock), Davout (+20% counter-punch), Drouot (15% fort degradation), Wellington (+5% defense), Blucher (+3k pursuit), Uxbridge (+5k pursuit).
- **Special Abilities Evaluation complete:** `docs/SPECIAL_ABILITIES_EVALUATION.md` — 3 Davout designs proposed, existing abilities reviewed (all balanced for Phase 7), UI surface audit (5 manual / 6 auto), 1805 roster planning principles and candidate lists documented.
- **ADDING_CONTENT.md expanded:** "Wiring a Special Ability" 16-step checklist, common mistakes table, file audit.

---

### Feb 22 (Phase 6.5 UI Audit)

**Code quality audit of all Phase 6.5 menu systems. 9 new tests, 1 pre-existing fix, 3354 total.**

- **Audit scope:** Pause Menu, Campaign Log, Morning Dispatch, Notification Bar, Top Bar, Strategic Ledger, Marshal Management. Checked int() wrapping, serialization, input blocking, CanvasLayer ordering, edge cases, endpoints, test coverage, consistency.
- **Fixes (bugs):** `/campaign_log` endpoint missing `"success"` key + game state guard. `GET /notifications` missing game state guard. `test_marshal_overview.py::test_endpoint_no_game_returns_error` called `game_state.clear()` without restore, poisoning subsequent tests (caused pre-existing `test_recklessness_2_blocks_defensive_stance` failure).
- **Fixes (comments):** `campaign_log.gd` layer comment corrected (102 -> 50).
- **New tests:** 5 endpoint tests for `/campaign_log`, 4 endpoint tests for `/notifications`.
- **Tech debt documented:** `_format_number()` duplication (3 files), color palette duplication (3+ files), marshal scroll hardcoded 320px/card. All tagged for Map Renderer refactor. Added to ROADMAP.md Tech Debt table.
- **Hooks fix:** `.claude/settings.local.json` PostToolUse/PreToolUse hooks had bash `$(...)` quoting bug with nested Python parentheses — split into variable assignments.

---

### Feb 21 (Marshal Management UI)

**Card-based read-only marshal management screen. 68 new tests, 3320 total.**

- `backend/game_logic/marshal_overview.py` — `build_marshal_overview(world)` returns per-marshal data cards (identity, ability, combat stats, trust/standing, status, unit specifics, relationships). All values int()-wrapped.
- `backend/models/marshal.py` — `biography` field added to `__init__`, `to_dict()`, `from_dict()`. Historical blurbs set for all 9 marshals (Berthier's voice).
- `marshal_management.gd/tscn` — CanvasLayer 50, vertical scrollable card list, BBCode rendering, number keys 1-N jump to marshal.
- `main.py`: `GET /marshal_overview` endpoint.
- `api_client.gd`: `get_marshal_overview()` method.
- `top_bar.gd`: Generals button enabled, wired to marshal management screen.
- `main.gd`: Marshal management scene loaded and registered with top bar.
- Ability active derivation hardcoded by name (Ney/Drouot/Wellington/Blucher/Uxbridge = active). TODO: Replace with proper `Marshal.ability_wired` field (Phase 7b or Pre-EA).

---

### Feb 21 (Session B: Strategic Ledger)

**5-section strategic ledger backend + sub-tabbed Godot screen. 54 new tests, 3252 total.**

- `backend/game_logic/ledger.py` — forces, territories, economy, intel, manpower sections. Fog-filtered intel. `BAND_MIDPOINTS` for estimated strength.
- `strategic_ledger.gd/tscn` — CanvasLayer 50, 5 sub-tabs (number keys 1-5), color coding.
- `world_state.py`: `get_manpower_regen_rates(nation)` extracted as single source of truth.
- `main.py`: `GET /ledger` endpoint.

---

### Feb 21 (Session A: Top Bar Framework + Dispatch)

**Unified top bar UI framework. 8 new tests, 3198 total.**

- `top_bar.gd/tscn` — CanvasLayer 75 controller (Event Log, Ledger, Generals, Dispatch), notification area, turn counter.
- `dispatch_view.gd/tscn` — CanvasLayer 50 dispatch re-read (D key). `last_morning_dispatch` stored on WorldState.
- Campaign log refactored to layer 50, notification bar reparented into top bar.
- Input refactor: `_is_modal_dialog_open()`, `_is_screen_open()`, `_is_hotkey_blocked()`.
- Hotkeys: L (Event Log), T (Ledger), G (Generals placeholder), D (Dispatch).

---

### Feb 21 (Notification System + Audit)

**EU4-style persistent notification bar. 9 triggers, 3 priority tiers. 70 tests total (51 + 19 audit).**

- `backend/notifications.py` — NotificationCollector, 10 notification types, priority enum.
- `notification_bar.gd/tscn` — color-coded icons, expand/dismiss, backend sync.
- 9 triggers: strategic complete, forced retreat, friendly fire, reckless cavalry, counter-punch, manpower, elimination, bankruptcy, drill cancelled.
- Audit fixes: whitelist mismatch, missing passthrough (3 endpoints), accumulation prevention, auto-dismiss.

### Feb 20 (Morning Dispatch)

**Berthier's Morning Dispatch: structured turn-start briefing. 57 new tests, 3120 total.**

- `backend/game_logic/dispatch.py` — SITUATION, MARSHAL STATUS, INTELLIGENCE, Berthier note.
- Fog-filtered enemy strength ratio. Tactical events absorbed into dispatch. Both end-turn paths wired.

### Feb 20 (Campaign Log + Polish)

**Fog-filtered campaign event log with Godot overlay. 57 tests.**

- `backend/campaign_log.py` — 14-type whitelist, fog filter, one-liner formatter.
- `campaign_log.gd/tscn` — CanvasLayer overlay, turn-grouped expandable sections, L key toggle.
- Polish: nation tags on names, both-sides casualties, expand/collapse fix, empty turn hiding.

### Feb 20 (Wire Marshal Abilities + Phase 7 Prep)

- Drouot 15% fort degradation, Wellington +5% defense, Blucher 3k pursuit, Uxbridge 5k pursuit.
- Phase 7 pre-implementation audit: 20 findings (3 critical, 7 design gaps). `PHASE7_SPEC_AMENDMENTS.md` created.
- Phase 7 scoped to 6-session Core + deferred 7b.

### Feb 19 (Session 56: Pause Menu)

- Smart Esc pause menu overlay (CanvasLayer 101). Save/Load/Settings stub/Quit.

---

## Known Issues

| Issue | Severity | Notes |
|-------|----------|-------|
| V1 global objection cap still active for strategic path | Low | `disobedience.py:25` MAX_MAJOR_OBJECTIONS_PER_TURN=2. Remove in V2b cleanup. |
| No mid-objection save/load roundtrip test | Low | Serialization enforcement confirms fields exist, but no test with populated V2 pending_objection. |
| Missing AI test coverage for P3, P4.75, P7 | Medium | P3 (threat response), P4.75 (ally support), P7 (strategic movement) have zero direct unit tests. |
| Residual 2-turn fortify oscillation possible | Low | `_unfortified_this_turn` only prevents same-turn re-fortify. Stagnation counter is backstop. |
| `requires_input` interrupt blocks later marshals | Low | `strategic.py:119` stops processing ALL further marshals when one requires input. |
| `full_game.py` dead code with stale terrain | Low | 3 `resolve_battle()` calls hardcode `terrain="open"`. File is dead code. |
| France hardcoded as player nation | Low | Multiple systems assume France. Post-EA multi-nation play requires threading player_nation. |
| `ability_active` hardcoded by marshal name | Low | `marshal_overview.py` derives ability_active from `_WIRED_ABILITY_MARSHALS` set. Replace with proper `Marshal.ability_wired` field. Pre-EA or Phase 7b. |
| `resolve_battle()` has 5 categories of side effects | High | Phase 7 `apply_casualties=False` must defer all 5. See `PHASE7_SPEC_AMENDMENTS.md` C1. |
| Cross-nation coordination impossible (Britain/Prussia) | Medium | Deferred to Phase 7b with Coalition Trigger. See `PHASE7_SPEC_AMENDMENTS.md` C3. |
| Missing SUPPORT objection triggers | Low | Add in Phase 7 Session 59. |

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
| Phase 7 spec | `MULTI_MARSHAL_SPEC.md` |
| Phase 7 audit amendments | `PHASE7_SPEC_AMENDMENTS.md` |
| Game systems reference | `SYSTEMS_REFERENCE.md` |
| Enemy AI | `ENEMY_AI_REFERENCE.md` |
| V2b objection preview | `OBJECTION_V2.md` |
| Save format | `SAVE_FORMAT_REFERENCE.md` |
| Fog of war spec | `FOG_OF_WAR_SPEC.md` |
| Adding content | `ADDING_CONTENT.md` |
| Game vision | `VISION.md` |
| Future concepts | `FUTURE_DESIGN.md` |
| Modding | `MODDING_FORMAT.md` |
| Manual testing | `MANUAL_TEST_PLAN.md` |
| Tutorial content | `TUTORIAL_SCRIPT.md` |
| Playtest prompt | `PLAYTEST_EVALUATION_PROMPT.md` |
| Session history (archived) | `archive/SESSION_HISTORY.md` |
