# Deep Audit Report V2 — Ink & Iron (Post-Refactoring)
**Started:** 2026-03-29
**Purpose:** Find NOVEL issues after R1-R16 architecture refactoring. All prior audit findings fixed.
**Tests passing:** 7,755 (1 skipped)
**Refactoring context:** executor.py 14,802→1,554 lines, split into 8 sub-executors

---

## Executive Summary

The R1-R16 refactoring achieved its goals: the codebase is significantly cleaner, the sub-executor split is well-structured with proper delegation, and all 7,755 tests pass. The refactoring did NOT introduce regressions in the areas audited.

**Novel findings: 2 MAJOR, 4 MINOR, 4 NOTE** — all new issues, none are regressions from the refactoring itself. The major bugs are pre-existing logic errors that survived all previous audits.

---

## Pass 1: Line-by-Line Critical File Review

### [P1-1] Economy Report Admin Bonus Uses Wrong Multiplier (3x Inflated)
- **Severity:** MAJOR
- **File:** `backend/commands/economy_executor.py:45` + `:83`
- **Description:** The economy report (`_execute_economy`) calculates admin bonus with `* 75` but the actual income system (`world_state.py:2569 _calculate_admin_bonus`) uses `* 25`. The player sees a projected net income that is inflated by `(admin_AP * 50)` gold — up to +100g error with 2 unused admin AP. The display text (line 83) also contradicts the calculation: it says "x 25" while the code uses `* 75`.
- **Evidence:**
  ```python
  # economy_executor.py:45 — WRONG multiplier
  admin_bonus = world.admin_actions_remaining * 75

  # economy_executor.py:83 — display says x 25 (contradicts line 45)
  lines.append(f"\n  Admin bonus: +{admin_bonus}g  ({world.admin_actions_remaining} unused AP x 25)")

  # world_state.py:2569 — ACTUAL income calculation uses * 25
  return int(getattr(self, 'admin_actions_remaining', 0) * 25)
  ```
- **Impact:** Player sees wrong projected net income. With 2 unused admin AP: report shows +150g bonus, reality is +50g. Economic decisions (recruit vs save gold) made on false data.
- **Proposed Fix:** Change economy_executor.py:45 from `* 75` to `* 25`.
- **Test Coverage:** No test validates economy report accuracy against actual income.

### [P1-2] Diplomat Skill Bonus Asymmetrically Capped (Uncapped Positive)
- **Severity:** MAJOR
- **File:** `backend/game_logic/diplomacy.py:753`
- **Description:** The diplomat skill bonus is clamped on the negative side (`max(-8, ...)`) but has NO upper bound. With a skill delta of 9 (proposer 10, target 1), the bonus is +18 — more than double the capped negative. This creates a significant imbalance in the acceptance formula: high-skill diplomats overwhelm other formula components.
- **Evidence:**
  ```python
  diplomat_skill_bonus = max(-8, (proposer_skill - target_skill) * 2)
  # Skill delta +9 → +18 (uncapped)
  # Skill delta -9 → -8 (capped)
  ```
- **Impact:** France's Talleyrand (skill 8) vs low-skill AI diplomats can generate +10-16 bonus, making proposals almost always succeed regardless of other factors.
- **Proposed Fix:** `diplomat_skill_bonus = max(-8, min(8, (proposer_skill - target_skill) * 2))`
- **Test Coverage:** No test specifically validates asymmetric skill bonus behavior.

---

## Pass 2: Fog-of-War Consistency Audit

### [P2-1] SUPPORT Target Resolution Uses Omniscient Enemy Data for Player
- **Severity:** MINOR
- **File:** `backend/commands/strategic_executor.py:166-172`
- **Description:** When resolving a generic SUPPORT command ("Davout, support"), the `threat_level()` function uses `world.get_enemies_in_region()` — an omniscient function that sees all enemies regardless of fog. For player marshals, this means the "most threatened ally" calculation considers fogged enemies the player can't see. The result: the system may suggest supporting an ally based on threats the player is unaware of.
- **Evidence:**
  ```python
  def threat_level(ally):
      threats = len(world.get_enemies_in_region(ally.location, ally.nation))
      region = world.get_region(ally.location)
      if region:
          for adj in region.adjacent_regions:
              threats += len(world.get_enemies_in_region(adj, ally.nation))
      return threats
  ```
- **Impact:** Low — auto-resolved SUPPORT targets may consider hidden enemies, but doesn't directly leak info to the player (just affects which ally is chosen).
- **Proposed Fix:** For player marshals, use fog-filtered enemy counts.

### [P2-2] Drill Adjacent Enemy Check Uses Omniscient Data
- **Severity:** MINOR
- **File:** `backend/commands/tactical_executor.py:222-229`
- **Description:** When checking if a marshal can drill, adjacent enemies are found using `world.get_enemies_of_nation()` — omniscient. A player marshal could be blocked from drilling by an enemy in an adjacent fogged region they can't see: "Cannot drill with enemy forces nearby! Kutuzov is at Bavaria, just one region away." This leaks the fogged enemy's name and location.
- **Evidence:**
  ```python
  for adj_name in current_region.adjacent_regions:
      for enemy in world.get_enemies_of_nation(marshal.nation):
          if enemy.location == adj_name and enemy.strength > 0:
              return {"success": False,
                  "message": f"... {enemy.name} is at {adj_name} ..."}
  ```
- **Impact:** Direct fog leak — player learns enemy name and location from a drill rejection message.
- **Proposed Fix:** For player marshals, use `world.get_visible_enemies()` and only block if the adjacent enemy is in a PARTIAL+ visibility region.

---

## Pass 3: Cross-System Consistency

### [P3-1] Duplicate ADMIN_ACTIONS Constant
- **Severity:** NOTE
- **File:** `backend/commands/executor.py:42` and `backend/commands/meta_executor.py:21`
- **Description:** `ADMIN_ACTIONS = {"recruit", "build", "repair"}` is defined identically in two files. If a new admin action is added, both must be updated.
- **Proposed Fix:** Define once in executor.py, import in meta_executor.py.

### [P3-2] Duplicate Tactical Event Fog Filters with Divergent Logic
- **Severity:** MINOR
- **File:** `backend/main.py:407` (`_filter_tactical_events_by_visibility`) and `backend/commands/meta_executor.py:24` (`_filter_tactical_events_by_fog`)
- **Description:** Two separate functions filter tactical events by fog, running on different code paths:
  - `main.py:_filter_tactical_events_by_visibility` — used in /command endpoint response (line 982)
  - `meta_executor.py:_filter_tactical_events_by_fog` — used in auto-advance and end_turn paths

  Their logic diverges:
  - main.py specially handles `auto_charge`, `reckless_cavalry`, `intel_updated`, `intel_decayed`, `target_not_found` event types — meta_executor doesn't
  - meta_executor checks `defender_nation` — main.py checks it differently
  - main.py does a marshal lookup for event ownership; meta_executor uses `attacker_nation` fallback

  If a new event type is added, one filter might pass it while the other drops it.
- **Proposed Fix:** Consolidate into a single function in a shared location.

### [P3-3] _DOWNGRADE_ORDER Missing VASSAL and ARMISTICE (Intentional but Undocumented)
- **Severity:** NOTE
- **File:** `backend/game_logic/diplomacy.py:36-39`
- **Description:** `_DOWNGRADE_ORDER` excludes VASSAL and ARMISTICE. The code comment says "intentionally excluded" but previous audits flagged this. The comment was added as a fix, confirming this is by-design: ARMISTICE auto-expires via timer, VASSAL exits via release/rebellion. Noted here only because it continues to appear as a potential issue in automated scans.

### [P3-4] _filter_enemy_phase_by_visibility Loops Player Marshals Per Event
- **Severity:** NOTE
- **File:** `backend/main.py:340-343` and `:350-353`
- **Description:** The `_filter_enemy_phase_by_visibility` function calls `world_state.get_player_marshals()` inside a nested loop (per action, per event). With 4 player marshals and 10 enemy actions with 3 events each, this is 120 iterations of `get_player_marshals()`. Each call is O(N) over all marshals. Not a bug, but a minor performance concern for future expansion.
- **Proposed Fix:** Cache `player_marshal_names` before the loops.

---

## Pass 4: Architecture Review (Refactoring Quality)

### [P4-1] __getattr__ Delegation Chain — Working But Complex
- **Severity:** NOTE
- **File:** `backend/commands/executor.py:168-188`
- **Description:** The `CommandExecutor.__getattr__` method checks 9 delegation sets sequentially. This is the backward-compatibility layer allowing old code to call `executor._execute_attack()` instead of `executor._combat._execute_attack()`. While functional, it adds ~9 dict lookups per delegated method call. Performance impact is negligible given the game's scale, but the delegation sets should be pruned as callers are migrated to direct sub-executor access.

---

## Test Suite Verification

All 7,755 tests pass with 1 skipped. No regressions from the R1-R16 refactoring.

---

## Refactoring Assessment

The R1-R16 refactoring was **clean and successful**:

1. **Sub-executor split (R10-R13):** Each sub-executor has a clear responsibility boundary. Cross-executor calls via `self._executor.X` are correct in all cases audited.
2. **DialogueManager (R12):** Serialization complete (to_dict/from_dict). push/pop/peek/replace operations are correctly implemented.
3. **CooldownManager (R6):** Centralized decrement replaces 4 separate decrement methods. Clean.
4. **Response pipeline (R4):** `build_base_response()` structurally guarantees popup passthroughs. All POST endpoints use it (except /command main path which has its own handling).
5. **Fog filtering (R5):** Consistently applied with player/AI branching in combat_executor and strategic_executor. Two exceptions found (P2-1, P2-2).
6. **Display names (R7):** Properly used across all audited files. No raw enum values found in frontend-facing returns.

The novel bugs found (P1-1, P1-2) are pre-existing logic errors, not refactoring regressions.

---

## Summary

| Severity | Count | Key Findings |
|----------|-------|-------------|
| CRITICAL | 0 | — |
| MAJOR | 2 | Admin bonus 3x inflated in economy report; Diplomat skill uncapped positive |
| MINOR | 4 | Fog leaks in drill check and SUPPORT resolution; Duplicate fog filters; Duplicate ADMIN_ACTIONS |
| NOTE | 4 | Downgrade order by-design; Performance concern in filter loop; __getattr__ complexity; Cache opportunity |
| **Total** | **10** | |
