# Diplomacy System Audit — March 2026

**Date:** 2026-03-22
**Method:** 4 code review agents + automated test suite + live playtest
**Status:** ALL 43 BUGS FIXED
**Tests before:** 6,249 passed | **Tests after:** 6,361 passed (+112 audit tests)
**Total findings:** 43 (5 CRITICAL, 12 MAJOR, 23 MINOR, 3 DESIGN) — all resolved

---

## CRITICAL (5) — Game-Breaking or Data-Corrupting

### C1. Coalition Loyalty Penalty Formula Inverted — CONFIRMED LIVE
**File:** `backend/game_logic/coalition.py:449`

Formula is `max(-15 - we//10, -30)` but docstring says `min(-15 + we//10, 0)`. As war exhaustion increases, the penalty gets WORSE instead of BETTER. Completely inverts the strategic loop.

**Fix:** Change `-` to `+` in the formula: `max(COALITION_LOYALTY_BASE + we // 10, 0)`. Also change `max` to `min` with upper bound 0.
```python
# BEFORE:
penalty = max(COALITION_LOYALTY_BASE - we // 10, -30)
# AFTER (matches docstring):
penalty = min(COALITION_LOYALTY_BASE + we // 10, 0)
```

### C2. Vassal Courting Reads Non-Existent DP Attribute — CONFIRMED LIVE
**File:** `backend/game_logic/vassal.py:905,922`

Reads `diplomatic_points_nations` but WorldState uses `nation_dp`. Enemy AI can never court player vassals.

**Fix:** Change both occurrences of `diplomatic_points_nations` to `nation_dp`.
```python
# Line 905:
dp = getattr(world, 'nation_dp', {}).get(nation, 0)
# Line 922:
dp_nations = getattr(world, 'nation_dp', {})
```

### C3. classify_diplomatic_intent Blocks Vassal Diplomacy — CONFIRMED LIVE
**File:** `backend/game_logic/diplomatic_dialogue.py:231`

Uses static `KNOWN_NATIONS` instead of `get_known_nations(world)`. Vassal nations rejected as "unknown".

**Fix:**
```python
# BEFORE:
if target_nation and target_nation not in KNOWN_NATIONS:
# AFTER:
if target_nation and target_nation not in get_known_nations(world):
```

### C4. /cancel_order Missing Popup Passthroughs
**File:** `backend/main.py:1843-1876`

Endpoint never calls `_include_popup_passthroughs()`. Also missing try/except wrapper and game_state in early returns.

**Fix:** Wrap in try/except, add `_include_popup_passthroughs(response, world)` before every return, add `game_state` to early returns.

### C5. Fog-of-War Leak in Threat Assessment
**File:** `backend/game_logic/diplomatic_advisory.py:254-276`

`_compare_threats()` uses raw troop strength for ranking, bypassing fog of war.

**Fix:** Use fog-filtered strength from intel system instead of raw `_get_nation_total_strength()`. Or use `_get_military_advantage()` which already fog-filters.

---

## MAJOR (12)

### M1. Acceptance Feedback Missing 3 Military Components
**File:** `backend/game_logic/diplomacy.py:796-802` — CONFIRMED LIVE

`trackable` set missing `military_supremacy`, `battlefield_diplomacy`, `military_pressure`.

**Fix:** Add the 3 keys to the `trackable` set.

### M2. _format_proposal_summary Crashes on Dict Clauses
**File:** `backend/game_logic/ai_diplomacy.py:908-909`

Assumes all clauses are strings. Dict clauses cause `AttributeError`.

**Fix:** Add `if isinstance(c, dict): name = c.get("type", "clause"); continue` guard.

### M3. break_treaty Uses Player DP for All Nations
**File:** `backend/game_logic/diplomacy.py:1816-1818`

Always deducts from `world.diplomatic_points` even for AI nations.

**Fix:** Check `breaker_nation == world.player_nation` and use `world.nation_dp` for AI.

### M4. Sabotage Warnings Expose Raw Internal Type Keys
**File:** `backend/game_logic/diplomatic_ledger.py:579-590`

Raw keys like `softened`, `hardened`, `stalled` shown to player.

**Fix:** Add display name map: `{"softened": "Terms Weakened", "hardened": "Terms Hardened", "stalled": "Proposal Delayed", "ap_downgrade": "Authority Undermined", "unit_overpay": "Resources Wasted"}`.

### M5. Active Mission Progress Field Is Boolean Paused
**File:** `backend/game_logic/diplomatic_ledger.py:560`

Field named `progress` contains boolean `paused` value.

**Fix:** Rename to `paused` or change to actual progress value.

### M6. _state_map Missing vassalage and defensive_alliance
**File:** `backend/game_logic/diplomatic_dialogue.py:462-465`

DP cost display wrong for these proposal types.

**Fix:** Add `"vassalage": "VASSAL", "defensive_alliance": "ALLIANCE"` to `_state_map`.

### M7. Advisory Uses Static KNOWN_NATIONS
**File:** `backend/game_logic/diplomatic_advisory.py:250,506`

Ignores vassal/dynamic nations.

**Fix:** Replace `KNOWN_NATIONS` with `get_known_nations(world)` in both locations.

### M8. /respond_to_objection Exception Path Missing Popup Passthroughs
**File:** `backend/main.py:1113-1121`

**Fix:** Add `_include_popup_passthroughs(response, world)` in except block before return.

### M9. /respond_to_diplomatic_dialogue Exception Path Missing Popup Passthroughs
**File:** `backend/main.py:1157-1165`

**Fix:** Same as M8.

### M10. alliance_paradox_popup Has No Godot Handler
**File:** `backend/main.py:158` + `godot-client/`

Backend sets and clears the popup but Godot has no handler. Popup data silently lost.

**Fix:** Either create handler in main.gd or (simpler) convert to a notification instead of popup.

### M11. /cancel_order Has No try/except Wrapper
**File:** `backend/main.py:1843-1876`

**Fix:** Wrap in try/except matching other POST endpoints.

### M12. /command Game-Over and Empty-Command Guards Skip Popup Passthroughs
**File:** `backend/main.py:479-490`

**Fix:** Add `_include_popup_passthroughs()` to both early returns.

---

## MINOR (23)

| # | File | Line | Description | Fix |
|---|------|------|-------------|-----|
| m1 | diplomacy.py | 2024 | Continental System can drive gold negative | Add `max(0, ...)` floor |
| m2 | vassal.py | 917 | `ai_proposal_cooldowns` without getattr | Use `getattr(world, 'ai_proposal_cooldowns', {})` |
| m3 | vassal.py | 252 | Hardcoded nation list in process_vassal_loyalty | Use `[world.player_nation] + list(world.enemy_nations)` |
| m4 | vassal.py | 505 | Hardcoded nation list in check_defection_cascade | Same as m3 |
| m5 | vassal.py | 210/239 | Garrison bonus docstring says base=5, code uses 2 | Fix docstring to match code |
| m6 | ai_diplomacy.py | 654 | `ap_reduction` clause has no mechanical effect | Remove dead code or wire up |
| m7 | diplomacy.py | 1402 | Armistice docstring says 3 turns, code uses 5 | Fix docstring |
| m8 | ai_diplomacy.py | 970 | Counter-offer DP check bypassed when key missing | Use `.get(nation, 0)` |
| m9 | diplomatic_templates.py | 1153 | Hardcoded "France" instead of world.player_nation | Use `world.player_nation` |
| m10 | diplomatic_dialogue.py | 509 | Missing gold_lump demand type handler | Add handler |
| m11 | diplomatic_ledger.py | 252 | Relation trend threshold too loose | Change threshold from 3 to 2 |
| m12 | diplomatic_ledger.py | 353 | Armistice duration hardcoded as 5 | Extract constant |
| m13 | diplomatic_defiance.py | 471 | Talleyrand redemption no cooldown | Add cooldown or one-shot guard |
| m14 | diplomatic_defiance.py | 251 | _deep_copy_proposal only one level deep | Use `copy.deepcopy()` or recursive copy |
| m15 | diplomatic_defiance.py | 390 | _summarize_proposal exposes "Armistice Losing" | Strip internal suffixes |
| m16 | diplomatic_dialogue.py | 525 | Missing cavalry/artillery_manpower formatters | Add handlers |
| m17 | diplomatic_dialogue.py | 156 | resolve_nation_name substring matching | Use word boundary or exact match |
| m18 | diplomatic_ledger.py | 592 | History "last 20" not sliced | Add `[-20:]` slice |
| m19 | main.py | 581 | _DIALOGUE_RESPONSE_KEYWORDS missing keywords | Add yes/agree/start/more/no |
| m20 | main.py | 1054+ | Game-over guards skip popup passthroughs | Add passthroughs (low priority) |
| m21 | main.py | 2030 | Debug endpoints bypass Trust.modify() | Acceptable for debug, document |
| m22 | main.py | 1852,1855 | /cancel_order early returns missing game_state | Add game_state key |
| m23 | diplomatic_ledger.py | 163 | Dead branch for player nation in nations list | Remove dead code |

---

## DESIGN BUGS (3) — Upgraded from "Design Notes"

### D1. War Exhaustion Reset Exploitable
**File:** `backend/game_logic/diplomacy.py:488-491`

`cleanup_war_end` resets war_exhaustion for BOTH nations on ANY war end. If France is at war with Prussia AND Austria, making peace with Prussia resets Austria's exhaustion. Exploitable: peel off weak ally to reset strong one.

**Fix:** Only reset exhaustion for the specific war pair, not blanket reset.

### D2. Relation Requirement Off-By-One
**File:** `backend/game_logic/diplomacy.py:278`

`check_relation_requirement` uses `>` not `>=`. "Requires 40" means 41+ needed. Player sees "40 required", reaches 40, still blocked.

**Fix:** Change `relation > req` to `relation >= req`. Also update wizard check (line 2309) from `<=` to `<`.

### D3. AI Proposal Queue Silently Drops Proposals
**File:** `backend/game_logic/ai_diplomacy.py:300-316`

New proposal can be immediately dropped if queue is full of higher-priority items. No logging.

**Fix:** Add log message when proposal is dropped. Consider returning a flag to the caller.

---

## Fix Batches for Parallel Agents

### Batch A: Critical Fixes (C1-C5)
Files: coalition.py, vassal.py, diplomatic_dialogue.py, main.py, diplomatic_advisory.py

### Batch B: Major Engine Fixes (M1-M3, D1-D2)
Files: diplomacy.py, ai_diplomacy.py

### Batch C: Major UI/Wiring Fixes (M4-M12)
Files: diplomatic_ledger.py, diplomatic_dialogue.py, main.py, diplomatic_advisory.py

### Batch D: Minor Fixes (m1-m23, D3)
Files: All affected files, docstring corrections, guard additions
