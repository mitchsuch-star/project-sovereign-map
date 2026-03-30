# Playtest Audit — March 29, 2026

> **Source:** 3 automated playtests (mock LLM mode), 25+ turns total.
> **Playtests:** "The Ney Gambit" (aggressive rush, defeat Turn 3), "The Diplomat's Game" (defensive + diplomacy, armistice by Turn 6), "The Iron Wall" (full turtle, war score +39 by Turn 10).

---

## Summary

| Severity | Count | Description |
|----------|-------|-------------|
| CRITICAL | 1 | Turn skip (KNOWN — C3 from March playtest, still unfixed) |
| MAJOR | 3 | Mock parser "status", armistice error messages (x2) |
| MINOR | 2 | Emoji encoding, AP warning |
| DESIGN | 1 | Aggressive play balance (discussion, not code fix) |

**Estimated sessions:** 2 required + 1 design discussion.

---

## Session 1: Turn Skip + Parser (3 bugs)

### PT-1: Turn Counter Skip (CRITICAL) — KNOWN BUG C3

**Reproduction:** Playtest 3, Turn 1. Player uses all 4 AP (Davout fortify 2 AP + Ney insist fortify 2 AP). Explicit "end turn" → "Turn 1 ended. Turn 3 begins!" Turn 2 never existed.

**Previous report:** `docs/PLAYTEST_REVIEW_2026_03.md` §C3 (Turn 2→4 skip). Same root cause, different trigger.

**Root cause:** `advance_turn()` called twice within a single end-turn cycle. The R20 idempotency guard (`_last_advanced_turn >= current_turn`) has a design flaw: it stamps with the pre-increment turn number, so after the first call completes (1→2), the second call sees `_last_advanced_turn=1, current_turn=2` → `1 >= 2` is false → runs again (2→3).

Three possible double-call paths:
1. Auto-end-turn in `executor.py:1378` fires when AP=0, THEN explicit `end_turn` fires again
2. Autonomous marshal processing (`turn_manager.py:181`) executes through a fresh CommandExecutor that triggers auto-end-turn
3. `force_end_turn()` in `world_state.py` called redundantly

**Fix approach:**
1. Replace the idempotency guard with a proper cycle flag: `_turn_advance_in_progress` set at the START of `advance_turn()`, cleared at end. Reject any re-entrant call.
2. Add debug logging before ALL 3 `advance_turn()` call sites in turn_manager.py (lines 72, 102, 151) + the auto-end-turn at executor.py:1378.
3. Verify with a test that explicitly triggers the scenario: consume all AP via insist, then end_turn.

**Files:** `world_state.py` (guard fix), `turn_manager.py` (logging), `executor.py` (auto-end-turn path audit)
**Tests:** ~8 (double-advance prevention, auto-end-turn + explicit end_turn interaction, idempotency guard correctness)

---

### PT-2: Mock Parser "status" Not Recognized (MAJOR)

**Reproduction:** Any turn in mock LLM mode. Command `"status"` → Berthier confusion message. `"help"` and `"end turn"` work fine.

**Root cause:** In `llm_client.py`, the meta_commands set `{"help", "debug", "end_turn", "status"}` at line 220 is checked in `_should_try_llm()` to SKIP LLM escalation. But `_parse_with_mock()` itself has no keyword matching path for "status". The fast parser returns `action="unknown"` for "status", and then `_should_try_llm()` correctly says "don't escalate" — but the command is already parsed as unknown.

**Fix:** Add "status" keyword matching in `_parse_with_mock()` alongside the existing "help" and "end turn" paths. Return `{"action": "status", "marshal": None, "target": None}`.

**Files:** `llm_client.py`
**Tests:** ~3 (parse "status", parse "Berthier status", parse "show status")

---

### PT-3: Emoji Encoding Broken in Cavalry Warning (MINOR)

**Reproduction:** Playtest 3, Turn 4. Cavalry restless warning shows `"�\xa0�\udc8f Ney's horses grow restless"` — garbled surrogate pair.

**Root cause:** The emoji literal in the source code likely uses a surrogate pair that doesn't survive JSON serialization through the FastAPI response pipeline.

**Fix:** Replace the emoji with a plain text marker or a known-safe unicode character. The game's aesthetic is text-based military dispatches — emoji are out of place anyway.

**Files:** Search for the cavalry restless warning string in `world_state.py` or `turn_manager.py`
**Tests:** ~1 (verify no surrogates in cavalry warning message)

---

## Session 2: Armistice Errors + AP Warning (3 bugs)

### PT-4: "Unknown target" During Armistice — Attack (MAJOR)

**Reproduction:** Playtest 2, Turn 7. After accepting armistice with Prussia, `"Davout, attack Gneisenau"` → `"Unknown target: Gneisenau"`. Should say something like "Cannot attack Gneisenau — armistice is in effect with Prussia."

**Root cause:** `combat_executor.py` calls `_fuzzy_match_enemy()` → `world_state.py:get_enemy_by_name_for_nation()` which filters by `is_at_war()`. During armistice, returns None. The error path then generates a generic "Unknown target" message without checking WHY the target wasn't found.

**Fix:** After fuzzy match fails, check if the target name matches ANY marshal (regardless of war status). If it matches a marshal whose nation is in armistice/peace, return a diplomatic-context error message: "Cannot attack {target} — {relation} with {nation} is in effect."

**Files:** `combat_executor.py` (attack validation), possibly `executor.py` (`_fuzzy_match_enemy`)
**Tests:** ~4 (attack during armistice, attack during peace, attack during war, attack unknown name)

---

### PT-5: Pursue Consumes AP Then Fails During Armistice (MAJOR)

**Reproduction:** Playtest 2, Turn 5. After armistice with Britain, `"Ney, pursue Wellington"` → "Wellington spotted at Waterloo! Engaging! Unknown target: Wellington" — contradictory messages, and 2 AP consumed for a failed action.

**Root cause:** `strategic_executor.py` calls `world.get_marshal(target)` (line 415) which is a generic lookup without war status filtering. Wellington is found → "spotted" message generated. Then when trying to resolve the pursuit, the war-status-aware lookup fails → "Unknown target" message.

**Fix:**
1. Pre-validate war status BEFORE AP consumption. If not at war with target's nation, return error with 0 AP cost.
2. Use `get_enemy_by_name_for_nation()` instead of `get_marshal()` for PURSUE target resolution.
3. Return diplomatic-context error: "Cannot pursue Wellington — armistice with Britain is in effect."

**Files:** `strategic_executor.py` (pursue validation)
**Tests:** ~4 (pursue during armistice, pursue during peace, pursue during war, SUPPORT during armistice)

---

### PT-6: No AP Warning on End Turn (MINOR — new feature)

**Reproduction:** Every playtest. Player types "end turn" with 4 AP remaining, turn ends silently with no warning about unused actions.

**Fix:** In `meta_executor.py:_execute_end_turn()`, check `world.actions_remaining > 0` or `world.admin_actions_remaining > 0`. If either has remaining actions, add a warning to the response message: "Warning: {N} action(s) unused this turn." The turn still ends (no confirmation needed — that would require dialogue state), but the message alerts the player.

**Files:** `meta_executor.py`
**Tests:** ~3 (warning with AP remaining, no warning with 0 AP, warning with only admin AP remaining)

---

## Design Discussion: Aggressive Play Balance

**NOT a code session — requires design gate approval first.**

**Problem:** Defensive play is overwhelmingly superior to aggressive play. Playtest 1 (aggressive rush) → defeat by Turn 3. Playtest 3 (full turtle) → war score +39 by Turn 10 without ever attacking until Turn 7.

**Evidence:**
- Fortify bonuses stack to +20% (Davout) with no meaningful counter
- Enemies attack into fortifications and break themselves, giving war score for free
- Aggressive personality gives +15% attack, but hills terrain gives +15% defense — cancels out
- No reward for capturing territory quickly (no momentum mechanic)
- Retreat recovery (3 turns) makes failed attacks catastrophic

**Potential design levers (need discussion):**
1. **Momentum bonus:** Consecutive successful attacks give stacking +5% attack (resets on loss)
2. **Shock value:** First attack on a region not attacked in 3+ turns gets +10% surprise bonus
3. **Blitz capture bonus:** Capturing a region gives gold/morale/war score multiplier
4. **Fortification degradation:** Fortifications decay without enemy pressure (use-it-or-lose-it)
5. **Bombardment fort counter:** Artillery degrades enemy fortifications faster (rewards combined arms offense)
6. **Pursuit devastation:** Attacking a retreating/broken enemy should deal massive damage (currently "Unknown target" during armistice blocks this; during war, broken enemies flee too far)
7. **War score for territory control:** Holding captured enemy territory should generate ongoing war score, rewarding offensive campaigns

**Decision needed:** Which levers to pull? This affects core balance philosophy (EU4-style "defend then counter" vs HOI4-style "blitz or die").

---

## Files Modified (estimated)

| File | Session | Changes |
|------|---------|---------|
| `world_state.py` | 1 | Idempotency guard redesign |
| `turn_manager.py` | 1 | Debug logging at advance_turn calls |
| `executor.py` | 1 | Auto-end-turn path audit |
| `llm_client.py` | 1 | "status" keyword in mock parser |
| `world_state.py` or source of cavalry warning | 1 | Remove garbled emoji |
| `combat_executor.py` | 2 | Diplomatic-context attack error |
| `strategic_executor.py` | 2 | Pursue war-status pre-validation |
| `meta_executor.py` | 2 | AP warning on end turn |

**Estimated tests:** ~25 new tests across 2 sessions.
