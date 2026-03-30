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

## Session 1: Turn Skip + Parser + Emoji (3 bugs)

### PT-1: Turn Counter Skip (CRITICAL) — KNOWN BUG C3

**Reproduction:** Playtest 3, Turn 1. Player uses all 4 AP (Davout fortify 2 AP + Ney insist fortify 2 AP). Explicit "end turn" → "Turn 1 ended. Turn 3 begins!" Turn 2 never existed.

**Previous report:** `docs/PLAYTEST_REVIEW_2026_03.md` §C3 (Turn 2→4 skip). Same root cause, different trigger.

**Root cause:** `advance_turn()` called twice within a single end-turn cycle. Two guards exist but both are insufficient:

1. **R20 idempotency guard** (`world_state.py:3872`): `_last_advanced_turn >= current_turn` stamps with the pre-increment turn number. After the first call completes (1→2), the second call sees `_last_advanced_turn=1, current_turn=2` → `1 >= 2` is false → runs again (2→3).
2. **turn_manager local `_advanced` flag** (`turn_manager.py:68`): Only protects within a single `end_turn()` call. Does NOT protect when auto-end-turn at `executor.py:1378` creates a fresh TurnManager instance — the new instance has `_advanced=False`.

Three confirmed double-call paths:
1. Auto-end-turn in `executor.py:1378` fires when AP=0, THEN explicit `end_turn` fires again from the same player input
2. Autonomous marshal processing (`turn_manager.py:181`) executes through a fresh CommandExecutor that triggers auto-end-turn — new TurnManager has a fresh `_advanced=False` flag
3. `force_end_turn()` in `world_state.py` called redundantly

**Fix approach:**
1. Replace the R20 idempotency guard in `world_state.py` with a proper re-entrancy flag: `_turn_advance_in_progress` set at the START of `advance_turn()`, cleared at end. Reject any re-entrant call regardless of turn number.
2. Add debug logging before ALL 3 `advance_turn()` call sites in `turn_manager.py` (lines 72, 102, 151) + the auto-end-turn at `executor.py:1378`.
3. Verify with a test that explicitly triggers the scenario: consume all AP via insist, then explicit end_turn.

**Files:** `world_state.py` (guard fix), `turn_manager.py` (logging), `executor.py` (auto-end-turn path audit)
**Tests:** ~8 (double-advance prevention, auto-end-turn + explicit end_turn interaction, fresh TurnManager re-entrancy, idempotency guard correctness)

---

### PT-2: Mock Parser "status" Not Recognized (MAJOR)

**Reproduction:** Any turn in mock LLM mode. Command `"status"` → Berthier confusion message. `"help"` and `"end turn"` work fine.

**Root cause:** Two separate bugs combine to break "status" in mock mode:

1. **Mock parser has no keyword path for "status"** (`llm_client.py`): `_parse_with_mock()` handles "help", "end turn", and other commands via keyword matching, but has no matching path for "status". Returns `action="unknown"`.
2. **Mock mode skips LLM fallback** (`llm_client.py:202`): `_should_fallback_to_llm()` returns `False` in mock mode, so the `action="unknown"` result goes straight to the caller without any chance to recover via LLM parsing.

The meta_commands set at line 220 (`{"help", "debug", "end_turn", "status"}`) only controls whether `_should_try_llm()` skips LLM escalation — it does NOT affect mock parser keyword matching, which is a completely separate code path.

Additionally, `parser.py` valid_actions list (lines 44-93) should be checked to confirm "status" is present there as well.

**Fix:**
1. Add "status" keyword matching in `_parse_with_mock()` alongside the existing "help" and "end turn" paths. Return `{"action": "status", "marshal": None, "target": None}`.
2. Verify "status" is in `parser.py` valid_actions list — add if missing.

**Files:** `llm_client.py`, possibly `parser.py`
**Tests:** ~4 (parse "status" in mock mode, parse "Berthier status", parse "show status", verify valid_actions includes "status")

---

### PT-3: Emoji Encoding Broken in Cavalry Warning (MINOR)

**Reproduction:** Playtest 3, Turn 4. Cavalry restless warning shows `"�\xa0�\udc8f Ney's horses grow restless"` — garbled surrogate pair.

**Root cause:** Cavalry-related messages in `world_state.py` (lines 5186-5541) use literal Unicode emoji characters: ⚠️ (lines 5186, 5201), 🐴 (lines 5450, 5475), 🐴🔥 (line 5541). These are multi-byte characters that may not survive Windows CP-1252 encoding or JSON serialization through the FastAPI response pipeline, producing garbled surrogate pairs.

**Fix:** Replace all emoji in cavalry warning messages with plain text markers or ASCII art. The game's aesthetic is text-based military dispatches — emoji are out of place anyway. Specific replacements:
- ⚠️ → `[!]` or `WARNING:`
- 🐴 → `[Cavalry]`
- 🐴🔥 → `[Cavalry Critical]`

**Files:** `world_state.py` (lines 5186-5541, cavalry warning messages)
**Tests:** ~2 (verify no surrogates in cavalry warning messages, verify no emoji in any world_state message strings)

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

**Root cause:** `strategic_executor.py` calls `world.get_marshal(target)` (line 414) which is a generic lookup without war status filtering. Wellington is found → "spotted at" message generated at `strategic_executor.py:940`. Then when trying to resolve the pursuit via war-status-aware lookup, it fails → "Unknown target" message. AP is consumed at `executor.py:1806-1809` AFTER the initial target resolution succeeds but BEFORE the war-status check fails.

**Fix:**
1. Pre-validate war status BEFORE AP consumption. In `strategic_executor.py`, check `world.is_at_war(executing_marshal.nation, target_marshal.nation)` immediately after resolving the target marshal. If not at war, return error with 0 AP cost.
2. Use `get_enemy_by_name_for_nation()` instead of `get_marshal()` for PURSUE target resolution, or add an explicit war-status check before generating the "spotted at" message.
3. Return diplomatic-context error: "Cannot pursue Wellington — armistice with Britain is in effect."

**Files:** `strategic_executor.py` (pursue validation, line ~414 + ~940)
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

### Existing Anti-Turtle Mechanics (already implemented)

Before adding new mechanics, note what already exists:

| Mechanic | Details |
|----------|---------|
| **Fortification natural decay** | Kicks in after 4-8 cumulative turns (personality-dependent). Aggressive: turn 4, 2%/turn, floor 0%. Cautious (Davout): turn 8, 1%/turn, floor 5%. |
| **Combat fort degradation** | Every battle degrades defender's fort by -5% (infantry/cavalry) or -10% (artillery). Drouot: -15% in combat. |
| **Bombardment degradation** | -10% per bombardment (max 2/turn). |
| **Defense hard cap** | 1.75x total defense modifier cap prevents invincible turtling. |
| **Cavalry fortify limit** | Cavalry auto-unfortify after 3 turns (-3 trust). Can't hold positions. |

The problem isn't missing penalties — it's missing **offensive rewards**.

### EU4 War Score Reference

EU4 uses three independent war score sources, each capped:

| Source | Cap | Mechanic |
|--------|-----|----------|
| **Battles** | ±40% | Based on army size destroyed. Large decisive battles matter most. |
| **Occupation** | Based on % of total development | Forts give credit for zone of control (neighboring provinces). |
| **Ticking war score** | ±25% | +0.1%/month for holding the war goal province. Creates urgency — attacker who holds objective slowly wins even without fighting. |

Key insight: occupation alone can't reach 100%. You need battles + occupation + time. The **ticking war score on objectives** is what makes offense mandatory — pure defense means slowly losing.

### Potential Design Levers

1. **Momentum bonus:** Consecutive successful attacks give stacking +5% attack (resets on loss). Thematic — Napoleon's entire strategy was momentum-based. Needs cap (+15-20%) to avoid snowball.
2. **Shock value:** First attack on a region not attacked in 3+ turns gets +10% surprise bonus. Interesting but niche.
3. **Blitz capture bonus:** Capturing a region gives gold/morale/war score multiplier. Risk of snowball if combined with momentum.
4. ~~**Fortification degradation:**~~ **ALREADY EXISTS** — natural decay after 4-8 turns + combat/bombardment degradation. See table above.
5. ~~**Bombardment fort counter:**~~ **ALREADY EXISTS** — -10% per bombardment. See artillery improvements below for ways to strengthen this.
6. **Pursuit devastation:** Attacking a retreating/broken enemy should deal massive damage. Currently pursuit damage is only a base mechanic with no cavalry-specific bonus for non-ability marshals. During armistice, "Unknown target" blocks pursuit entirely (PT-5 bug).
7. **War score for territory control (EU4-style ticking):** Holding captured enemy territory generates ongoing war score. **Needs careful tuning** — flat +1/turn per region would snowball on a 19-region map. Options: (a) only capitals/key strategic regions count, (b) diminishing returns per region, (c) 3-turn hold delay before scoring starts, (d) hard cap at +3/turn total.

### Artillery Improvements (Strengthen Offensive Siege)

Current artillery vs fortification rates:

| Attacker | Combat Degradation | Bombardment |
|----------|-------------------|-------------|
| Infantry | -5% | Can't bombard |
| Cavalry | -5% | Can't bombard |
| Artillery | -10% | -10% |
| **Drouot** | **-15%** (ability) | **-10% (BUG: ability doesn't apply!)** |

**Proposed improvements:**
1. **Fix Drouot bombardment gap:** "Sage of the Grand Army" should apply -15% on bombardment too, not just regular combat. The ability description says "precise artillery fire degrades fortifications faster" — bombardment IS precise artillery fire.
2. **Bombardment streak scaling:** First bombard = -10%, second consecutive bombard on same target = -15%, third = -20%. Rewards sustained siege, punishes passive turtling. Streak tracking already exists (`marshal.bombardment_streak`).
3. **Bombardment morale damage vs fortified:** Currently -3 morale per bombard (-18 vs square). Add extra morale damage vs fortified targets — breaking the defender's will to hold.

### Cavalry Strategic Role (Underdeveloped)

Cavalry combat mechanics are solid (recklessness system, terrain effectiveness, glorious charge, +30% vs artillery, square formation interactions). But their **strategic role** is underdeveloped — historically cavalry were the eyes, flanks, and finishers of the army.

**Current cavalry strengths:**
- Movement range 2 (infantry = 1)
- Recklessness system (+5-20% attack, auto-charge at level 4)
- Glorious Charge (2x casualties both ways)
- +30% vs artillery, +20% on plains
- Can't be turtled (auto-unfortify after 3 turns)

**Current cavalry gaps:**
- **No base pursuit bonus:** Pursuit damage on retreat is a generic mechanic — cavalry gets no inherent advantage over infantry when chasing broken enemies. Historically cavalry pursuit was where the real casualties happened (Waterloo, Jena).
- **No screening/reconnaissance advantage:** Scouting isn't cavalry-specific. Could give cavalry +1 scout range or auto-reveal adjacent regions each turn.
- **No interception:** Cavalry can't block or delay enemy movement. Historically light cavalry screened army movements and delayed enemy advances.
- **No raiding:** Light cavalry raided supply lines and disrupted logistics. Could tie to the supply attrition system — cavalry in enemy territory increases attrition for nearby enemy marshals.

**Recommended cavalry addition:** Base pursuit damage for ALL cavalry marshals (+2k casualties when forcing retreat), on top of existing personality abilities. This is the most thematic and directly rewards offensive cavalry play.

### Recommended Package

**Tier 1 (highest impact, implement first):**
- Fix Drouot bombardment ability gap (low-hanging fruit, arguably a bug)
- Base cavalry pursuit damage (+2k for all cavalry on forced retreat)
- Momentum bonus (+5% stacking per consecutive win, cap at +15%, reset on loss)

**Tier 2 (needs tuning, implement second):**
- Ticking war score for key territory (capitals only? 3-turn delay? hard cap?)
- Bombardment streak scaling (-10%/-15%/-20% on consecutive bombards)

**Tier 3 (nice-to-have, later):**
- Cavalry screening (auto-reveal adjacent regions)
- Bombardment morale bonus vs fortified

**Decision needed:** Which package to approve? This affects core balance philosophy (EU4-style "defend then counter" vs HOI4-style "blitz or die"). Napoleonic warfare was highly offensive — the game should reward aggression more than it currently does.

---

## Files Modified (estimated)

| File | Session | Changes |
|------|---------|---------|
| `world_state.py` | 1 | Re-entrancy guard redesign + cavalry emoji removal |
| `turn_manager.py` | 1 | Debug logging at advance_turn calls |
| `executor.py` | 1 | Auto-end-turn path audit |
| `llm_client.py` | 1 | "status" keyword in mock parser |
| `parser.py` | 1 | Verify/add "status" to valid_actions |
| `combat_executor.py` | 2 | Diplomatic-context attack error |
| `strategic_executor.py` | 2 | Pursue war-status pre-validation (line ~414, ~940) |
| `meta_executor.py` | 2 | AP warning on end turn |

**Estimated tests:** ~30 new tests across 2 sessions.
