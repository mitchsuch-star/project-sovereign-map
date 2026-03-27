# Final Audit — Fix Plan

**Created:** 2026-03-26
**Source:** `audit-report-final.md` (21 findings → 13 confirmed bugs, 8 false positives)
**Status:** NOT STARTED
**Estimated:** 2 sessions, ~13 bugs, ~22 tests

---

## Triage Results

### Confirmed Real Bugs (13)

| # | ID | Severity | System | Summary |
|---|-----|----------|--------|---------|
| 1 | FINAL-9 | CRITICAL | Endgame | No defeat on capital loss / 0 regions — zombie state |
| 2 | FINAL-10 | MINOR | Endgame | Turn 41 off-by-one (`>` should be `>=`) |
| 3 | FINAL-11 | MAJOR | Endgame | No victory on total enemy elimination |
| 4 | FINAL-7 | MAJOR | Fog | Turn events leak enemy marshal activity (fortify/attrition) |
| 5 | FINAL-8 | MAJOR | Contract | fortification_old/new are floats — Golden Rule #2 violation |
| 6 | FINAL-16 | MAJOR | Fog | Campaign log retreat events leak destination region |
| 7 | FINAL-17 | MINOR | Endgame | AI sends diplomatic proposals to defeated nations |
| 8 | FINAL-1 | MAJOR | Diplomacy | Coalition void never refunds DP (dp_cost not stored in proposal_in_transit) |
| 9 | FINAL-2 | MAJOR | Diplomacy | Vassal rebellion cascade breaks armistice lock |
| 10 | FINAL-20 | MAJOR | AI | Enemy AI targets nations in armistice |
| 11 | FINAL-13 | MAJOR | Contract | Missing `is_counter_offer` field in incoming proposal popup |
| 12 | FINAL-6 | MINOR | Contract | POST /load missing `_include_popup_passthroughs()` |
| 13 | FINAL-21 | MINOR | Parser | Diplomatic command without target nation parses as None |

### False Positives (8) — No Action Needed

| ID | Original Claim | Why It's False |
|----|----------------|----------------|
| FINAL-3 | Exhaustion before coordination modifier order | Intentional design — comments at marshal.py:891 confirm exhaustion is "applied AFTER other modifiers (multiplicative)" by design |
| FINAL-4 | Coalition doesn't clear pending_diplomatic_dialogue | Code DOES clear it at coalition.py:598-602 — audit missed the existing fix |
| FINAL-5 | Continental System gold goes negative | Already marked FP in report — `max(0, ...)` floor exists |
| FINAL-12 | STALE intel shows "no forces" for PARTIAL-origin | STALE snapshots DO contain `strength` field — `.get("strength", 0)` is correct defensive coding |
| FINAL-14 | `_intel_events_this_turn` not serialized | Intentionally transient — cleared and rebuilt every turn, not save-worthy state |
| FINAL-15 | Campaign log shows enemy construction at PARTIAL | PARTIAL visibility is correct per fog design — scouts/adjacent observation detects construction |
| FINAL-18 | AI division-by-zero in attack evaluation | Already guarded — `enemy.strength > 0` filter at line 2135 runs before division at line 2158 |
| FINAL-19 | AI min() on empty list in stagnation handler | All `min(enemies, ...)` calls are guarded by `if enemies:` checks |

---

## Session 1: Endgame + Fog + Contract (7 bugs, ~12 tests)

**Priority:** P0 (CRITICAL endgame) + P1 (fog leaks, contract violations)
**Files:** `turn_manager.py`, `executor.py`, `combat.py`, `campaign_log.py`, `ai_diplomacy.py`

### Bug 1 — FINAL-9: Defeat on capital loss / 0 regions [CRITICAL]
- **File:** `backend/game_logic/turn_manager.py` → `_check_victory_conditions()`
- **Problem:** Only checks "all marshals destroyed" for defeat. No check for capital captured or total territory loss. Player can lose Paris + all regions and continue playing in a zombie state.
- **Fix:** Add two defeat checks after the existing marshal-destruction check:
  1. **Total territory loss:** `len(player_regions) == 0` → defeat ("All territory lost!")
  2. **Capital loss:** `NATION_CAPITALS.get(player_nation)` controller != player → defeat ("Your capital has fallen!")
- **Order matters:** Check territory loss first (more severe), then capital loss.
- **Tests (3):** Capital lost triggers defeat; 0 regions triggers defeat; temporary capital loss with other regions → no premature defeat (allow reconquest).

### Bug 2 — FINAL-10: Turn 41 off-by-one [MINOR]
- **File:** `backend/game_logic/turn_manager.py:832`
- **Problem:** `if self.world.current_turn > self.world.max_turns` — turn 40 doesn't trigger (40 > 40 = False), game continues to turn 41.
- **Fix:** Change `>` to `>=`.
- **Tests (1):** Game ends at exactly turn 40.

### Bug 3 — FINAL-11: Victory on total enemy elimination [MAJOR]
- **File:** `backend/game_logic/turn_manager.py` → `_check_victory_conditions()`
- **Problem:** Only region-count threshold checked for victory. No check for all enemy nations eliminated.
- **Fix:** After region-count check, add: if all enemy-nation marshals have strength ≤ 0 AND no regions controlled by enemy nations → victory ("All enemies defeated!").
- **Tests (2):** All enemies eliminated → victory; enemies eliminated but neutral regions remain → still victory (neutrals aren't enemies).

### Bug 4 — FINAL-7: Turn events fog leak [MAJOR]
- **File:** `backend/commands/executor.py` (`_execute_end_turn`) or `backend/main.py` (response building)
- **Problem:** `tactical_events` array returned to frontend includes enemy fortify_strengthened and supply_attrition events without fog filtering. Morning Dispatch filters them, but raw API response leaks them.
- **Fix:** Filter `tactical_events` in the response path — remove events for non-player marshals unless the event's region has PARTIAL+ visibility for the player.
- **Tests (2):** Enemy fortify event filtered from response; enemy attrition event filtered from response.

### Bug 5 — FINAL-8: fortification floats [MAJOR]
- **File:** `backend/game_logic/combat.py` (return points for fortification_old/new)
- **Problem:** `fortification_old` and `fortification_new` initialized as `0.0` (float) and returned without `int()` wrapping. Floats reach Godot → potential crash.
- **Fix:** Wrap with `int()` at combat.py return point: `int(fortification_old * 100)`, `int(fortification_new * 100)`. Also verify executor.py attack path wraps them (bombardment path already does).
- **Tests (1):** Battle result fortification values are always `int` type.

### Bug 6 — FINAL-16: Retreat destination fog leak [MAJOR]
- **File:** `backend/campaign_log.py` → `format_event_oneliner()` (~line 425)
- **Problem:** Fog filter checks SOURCE region visibility but formatter displays both `from` and `to`. Destination region may be UNKNOWN — player learns where enemy retreated to.
- **Fix:** In the fog filter or formatter, check destination region visibility. If destination not PARTIAL+, strip `to` from the formatted message (show "retreated from X" without destination).
- **Tests (2):** Fogged destination hidden in retreat message; visible destination shown normally.

### Bug 7 — FINAL-17: Diplomacy after effective defeat [MINOR]
- **File:** `backend/game_logic/ai_diplomacy.py` (proposal generation)
- **Problem:** AI generates proposals targeting nations with 0 regions or lost capital — bizarre UX.
- **Fix:** In AI proposal generation, skip nations that have 0 regions or whose capital is captured. Depends on FINAL-9 defeat logic (but AI should also not propose to effectively dead nations even if game hasn't ended yet).
- **Tests (1):** AI doesn't generate proposals for nations with 0 regions.

---

## Session 2: Diplomacy + AI + Parser (6 bugs, ~10 tests)

**Priority:** P1 (diplomacy state bugs, AI targeting) + P2 (contract, parser)
**Files:** `executor.py`, `coalition.py`, `vassal.py`, `enemy_ai.py`, `ai_diplomacy.py`, `main.py`, `llm_client.py`

### Bug 8 — FINAL-1: Coalition DP refund broken [MAJOR]
- **File:** `backend/commands/executor.py:12482` (proposal_in_transit creation) + `backend/game_logic/coalition.py:562` (refund code)
- **Problem:** `dp_cost` never stored in `proposal_in_transit` dict. Refund code reads `pit.get("proposal", {}).get("dp_cost", 0)` → always 0. Player permanently loses DP when coalition voids their in-transit proposal.
- **Fix:**
  1. In executor.py, add `"dp_cost": cost` to `proposal_in_transit` dict.
  2. In coalition.py, read from `pit.get("dp_cost", 0)` (top-level, not nested in proposal).
  3. Also add `dp_cost` to serialization if `proposal_in_transit` is saved.
- **Tests (2):** DP refunded when coalition voids in-transit proposal; no refund when dp_cost is 0.

### Bug 9 — FINAL-2: Vassal rebellion breaks armistice [MAJOR]
- **File:** `backend/game_logic/vassal.py` → `check_vassal_rebellion()` (~line 455)
- **Problem:** Sets `diplomatic_states[key] = "WAR"` unconditionally when vassal rebels. Doesn't check if pair is in ARMISTICE (5-turn lock).
- **Fix:** Before setting WAR, check current diplomatic state. If ARMISTICE, skip the war declaration (rebellion still fires — vassal becomes independent — but armistice between lord and vassal is respected until it expires naturally).
- **Tests (2):** Rebellion during armistice doesn't break armistice; rebellion without armistice triggers war normally.

### Bug 10 — FINAL-20: AI armistice targeting [MAJOR]
- **File:** `backend/ai/enemy_ai.py` → `_find_attack_opportunity()` (~line 2125)
- **Problem:** Gets enemies via `get_enemies_of_nation()` but never checks armistice state. AI can target nations it has armistice with.
- **Fix:** Add armistice check in the enemy iteration loop: `if world.get_diplomatic_state(nation, enemy.nation) == "ARMISTICE": continue`.
- **Tests (2):** AI skips armistice targets; AI targets non-armistice enemies normally.

### Bug 11 — FINAL-13: Missing is_counter_offer field [MAJOR]
- **File:** `backend/game_logic/ai_diplomacy.py` → popup creation (~line 917)
- **Problem:** `incoming_proposal_popup` dict missing `is_counter_offer` field for normal (non-counter) proposals. Only added ad-hoc in executor for counter-offers. Godot expects it always present.
- **Fix:** Add `"is_counter_offer": False` to the popup dict in `format_incoming_proposal()` or wherever the initial popup is created.
- **Tests (1):** Incoming proposal popup always has `is_counter_offer` field.

### Bug 12 — FINAL-6: Load missing active_wars [MINOR]
- **File:** `backend/main.py` → POST /load handler (~line 1757)
- **Problem:** /load success path returns response without calling `_include_popup_passthroughs()`. After loading mid-war, war status panel won't update until next /command.
- **Fix:** Add `_include_popup_passthroughs(response, world)` to /load success path.
- **Tests (1):** Loading a game with active wars includes active_wars in response.

### Bug 13 — FINAL-21: Diplomatic command without target [MINOR]
- **File:** `backend/ai/llm_client.py` (~line 930)
- **Problem:** Commands like "Talleyrand, propose peace" (no nation) parse with `target_nation=None` and `confidence=0.95`. None propagates downstream causing potential crashes.
- **Fix:** After `extract_nation_from_command()`, if `target_nation is None` for actions that require a target (propose, negotiate, send diplomat), return error ParseResult: "Please specify a nation — e.g., 'Talleyrand, propose peace to Prussia'".
- **Tests (2):** Command without target returns helpful error message; command with target parses normally.

---

## Verification Checklist

After each session:
- [ ] `".venv\Scripts\python.exe" -m pytest tests/ -v --tb=no -q` — all tests pass
- [ ] New test file passes: `test_final_audit_s1.py` / `test_final_audit_s2.py`
- [ ] Update `docs/STATUS.md` — mark session complete, indicate next
- [ ] Update `docs/FINAL_AUDIT_FIX_PLAN.md` — mark bugs as FIXED
- [ ] Update `CLAUDE.md` "Current Phase" — add Final Audit progress

After both sessions complete:
- [ ] Update `docs/SYSTEMS_REFERENCE.md` if endgame conditions section exists
- [ ] Full test suite green
- [ ] Mark Final Audit as COMPLETE in STATUS.md
