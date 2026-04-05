# Playtest Review — March 2026

> **Date:** March 24, 2026
> **Method:** Backend-only via curl, 16 turns played, LLM_MODE=mock
> **Reviewer:** Claude Code (automated playtest with gameplay examples)
> **Fun Rating:** 6.5/10 (significant upside potential once bugs fixed)

---

## Summary

The core loop — commanding marshals with natural language, navigating personality-driven objections, managing a multi-front Napoleonic war — is genuinely compelling. The diplomacy system is impressively deep. But several critical bugs seriously undermine the experience, and combat balance makes the opening moves feel punishing in a way that isn't fun.

---

## CRITICAL BUGS (3)

### C1: Armistice Stranded Marshal Deadlock (Game-Breaking)

**What happened:**
Turn 6: Signed armistice with Prussia. Gneisenau (Prussia, 17k troops) was physically located in Belgium (French territory). He never retreated home. For the rest of the game (10+ turns), he remained stranded in Belgium.

**Gameplay impact:**
```
> Drouot bombard Waterloo
"Cannot attack elsewhere while engaged with enemy forces! Gneisenau must be dealt with first."

> Ney attack Gneisenau
"Unknown target: Gneisenau"   (armistice blocks attack)
```

Complete deadlock: 3 French marshals in Belgium couldn't attack outward (engagement check), couldn't attack Gneisenau (armistice blocks it), couldn't do anything but end turn. Gneisenau sat there for 10+ turns taking supply attrition but never leaving.

**Root cause (confirmed via code review):**
1. `executor.py:~3898` — The engagement check uses `m.nation != marshal.nation` without checking `world.is_at_war()`. The movement check at `executor.py:~6800` DOES check `is_at_war()` — inconsistency.
2. `diplomacy.py:cleanup_war_end()` — Clears battle records, cancels strategic orders, but does NOT force-retreat displaced enemy marshals from player territory.
3. `enemy_ai.py` — No priority to voluntarily retreat from enemy territory when peace/armistice is signed.

**Fix plan:**
1. **Immediate:** Change attack engagement check from `m.nation != marshal.nation` to `world.is_at_war(marshal.nation, m.nation)` (consistent with move check)
2. **Proper:** Add `_force_retreat_displaced_marshals()` call in `cleanup_war_end()` — find all enemy marshals in our territory (or vice versa) for the now-peaceful pair, auto-retreat them to nearest friendly region
3. **Belt-and-suspenders:** Add enemy AI Priority 0.5 — "if in hostile territory and not at war, retreat to nearest friendly region"

**Files to modify:**
- `backend/commands/executor.py` (~line 3898) — engagement check
- `backend/game_logic/diplomacy.py` (`cleanup_war_end()`) — force retreat
- `backend/ai/enemy_ai.py` — peace retreat priority (optional)

---

### C2: Same-Nation Self-Combat (Wellington vs Wellington)

**What happened:**
Campaign log from turns 9-11 shows British forces fighting themselves:
```
Turn 11: Wellington (Britain) vs Wellington (Britain) at Belgium -> stalemate
Turn 11: Uxbridge (Britain) vs Wellington (Britain) at Belgium -> defender_tactical_victory
Turn 11: Wellington (Britain) vs Wellington (Britain) at Belgium -> defender_tactical_victory
Turn 10: Wellington (Britain) vs Wellington (Britain) at Belgium -> defender_tactical_victory
Turn 10: Uxbridge (Britain) vs Uxbridge (Britain) at Belgium -> stalemate
```

This happened dozens of times across multiple turns. British forces were self-destructing.

**Gameplay impact:**
- Wellington's strength declined from 52k to 37k partly due to fighting himself
- Campaign log is filled with nonsensical entries
- AI behavior becomes unpredictable and unreliable
- Player loses trust in the game's simulation

**Root cause analysis:**
1. `combat.py:resolve_battle()` has NO validation preventing same-nation combat — accepts any attacker/defender pair
2. The enemy AI target selection in `enemy_ai.py` uses `world.get_enemies_of_nation()` which correctly filters by nation+war — but something bypasses this during execution
3. Most likely: region-based target resolution at `executor.py:~3945` uses a weaker filter (`m.nation != marshal.nation`) that may fail when nation assignments change mid-phase, or when the region contains only same-nation marshals and the filter returns empty → fallback picks wrong target
4. Possible: Multiple enemy nations sharing a region (Wellington + Gneisenau in Belgium) could cause cross-wiring in target resolution

**Fix plan:**
1. **Immediate guard:** Add to `resolve_battle()` in `combat.py`:
   ```python
   if attacker.nation == defender.nation:
       return {"outcome": "cancelled", "reason": "same-nation combat prevented"}
   ```
2. **Root cause:** Audit `_fuzzy_match_enemy()` and region-based target resolution in `executor.py` to ensure same-nation marshals are never selected as targets
3. **Enemy AI guard:** Add same-nation check before `executor.execute()` call in `enemy_ai.py`

**Files to modify:**
- `backend/game_logic/combat.py` (`resolve_battle()`) — hard guard
- `backend/commands/executor.py` (`_fuzzy_match_enemy`, region-based resolution) — root cause
- `backend/ai/enemy_ai.py` — pre-execution validation

---

### C3: Turn Counter Skip (Turn 2 → Turn 4)

**What happened:**
After ending Turn 2, the game jumped directly to Turn 4. Turn 3 never existed.

```
End turn response: "Turn 2 ended. Turn 4 begins!"
Campaign log turns: [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
```

Turn 3 is completely absent from every record.

**Gameplay impact:**
- Player loses a full turn of action economy (4 AP + 2 admin AP)
- Diplomatic timers advance incorrectly (armistice duration, treaty durations)
- Construction timers may complete early
- Income/upkeep applied for a phantom turn
- Breaks any turn-counting strategy the player uses

**Root cause analysis:**
`turn_manager.py:end_turn()` has 3 separate `advance_turn()` calls:
- Line 70: Pre-enemy victory early return
- Line 94: Enemy victory during their turn early return
- Line 138: Normal flow

`world_state.py:_advance_turn_internal()` increments `current_turn += 1` at line 3566.

The double-increment likely happens when:
1. The normal `end_turn()` flow calls `advance_turn()` at line 138 (turn 2→3)
2. AND something else calls `advance_turn()` again in the same cycle (turn 3→4)

Possible triggers:
- Auto-end-turn at `executor.py:2406` firing for a player action in the same request cycle
- `force_end_turn()` at `world_state.py:5542` being called redundantly
- A sub-function within `_advance_turn_internal()` (vassal/diplomacy/coalition processing) triggering a secondary advance

**Fix plan:**
1. **Debug:** Add logging before each `advance_turn()` call with a stack trace to identify which path fires twice
2. **Guard:** Add a `_turn_advanced_this_cycle` flag to WorldState that prevents double-advancement:
   ```python
   def advance_turn(self):
       if getattr(self, '_turn_advanced_this_cycle', False):
           print("[WARNING] Double advance_turn prevented!")
           return
       self._turn_advanced_this_cycle = True
       self._advance_turn_internal()
   ```
   Reset the flag at the START of `_execute_end_turn()`.
3. **Root cause:** Trace the exact code path using the debug logging

**Files to modify:**
- `backend/game_logic/turn_manager.py` — debug logging, possibly restructure
- `backend/models/world_state.py` — double-advance guard
- `backend/commands/executor.py` — check auto-end-turn interaction

---

## MAJOR BUGS (3)

### M1: Raw Internal State Name in Diplomacy Message

**What happened:**
```
> Talleyrand, declare war on Prussia
"Sire! We have a Armistice Losing with Prussia."
```

Two issues:
- "Armistice Losing" is a raw internal type name (should be "an armistice")
- "a Armistice" — wrong article (should be "an")

**Fix:** Add display name mapping for diplomatic state types. Use `PROPOSAL_TYPE_DISPLAY` or similar dict. Fix article selection ("a" vs "an").

**Files:** `backend/commands/executor.py` or `backend/game_logic/diplomacy.py` (wherever war declaration confirmation is built)

---

### M2: "recruit infantry at Paris" Fails to Parse

**What happened:**
```
> recruit infantry at Paris
"Berthier peers at the dispatch with concern. I cannot make sense of this, Sire."

> Davout recruit at Paris    ← This works!
"Davout recruits 10,000 infantry at Paris"
```

Natural phrasing with troop type specified should work. The parser requires a marshal name prefix but players will naturally say "recruit infantry at Paris."

**Fix:** Update mock parser keyword matching in `llm_client.py` to handle "recruit [type] at [location]" pattern. Auto-assign to highest-strength marshal at the location.

**Files:** `backend/ai/llm_client.py` (mock parser), `backend/commands/parser.py`

---

### M3: Ney Auto-Recruits Cavalry Only, No Player Control Over Type/Amount

**What happened:**
```
> recruit at Belgium
"Ney recruits 5,000 cavalry for Belgium - Cost: 300 gold"
```

The player has no way to specify:
- Troop type (infantry/cavalry/artillery) — auto-chosen by marshal type
- Amount — always 5k cavalry, 10k infantry, or 4k artillery
- Which marshal at a location with multiple marshals

**Impact:** Player can't strategically choose to recruit infantry for a cavalry marshal, or control spending.

**Fix:** Allow "recruit infantry for Ney" or "recruit 3000 at Belgium". Parse type and amount from command.

**Files:** `backend/commands/executor.py` (`_execute_recruit`), `backend/ai/llm_client.py` (parser)

---

## MINOR BUGS (4)

### m1: "trust" Doesn't Parse as Objection Response via /command

When Ney objects to drilling, typing "trust" into the `/command` endpoint returns a parse error. Must use the separate `/respond_to_objection` endpoint with `{"choice": "trust"}`. In the Godot UI this may use buttons, but the text command interface should also handle "trust", "insist", "compromise" as keywords.

**Files:** `backend/main.py` (command routing), `backend/ai/llm_client.py` (keyword detection)

---

### m2: Duplicate Counter-Punch Notifications

Davout earned 2 separate counter-punch notifications on the same turn (turn 2) that were never auto-dismissed. The notification list accumulated stale entries.

**Files:** `backend/notifications.py` (dedup logic)

---

### m3: Artillery Morale Collapse Without Combat

Drouot (artillery, 25k) morale dropped to 6% without ever directly fighting. Likely caused by being in Belgium during enemy attacks on other marshals, or supply attrition chain effects. Artillery shouldn't suffer extreme morale loss just from proximity.

**Files:** `backend/game_logic/combat.py` (bystander morale loss), `backend/models/world_state.py` (supply attrition morale effects)

---

### m4: Grouchy "march to Paris" Route Shows "Paris" When Already Adjacent

```
> Grouchy march to Paris
"Grouchy begins march to Paris. Route: Paris. Moves to Paris."
```

The route description is redundant when the destination is 1 move away. Should just say "Grouchy moves to Paris" without the strategic order overhead.

**Files:** `backend/commands/executor.py` (strategic order vs direct move detection)

---

## BALANCE CONCERNS (4)

### B1: Wellington's Defense Stack Is Overwhelming (~75-85% total)

Breakdown observed in combat messages:
- Hills terrain: +15% defense
- Cautious personality: +10% (outnumbered bonus)
- "Iron Marshal" ability: +20% total
- Defensive stance: +15%
- Fortification: +12-20% (grows per turn)
- Combined arms coordination: +5%
- Square formation: cavalry -40% when active

**Total: ~77-85% defense modifier stacking.**

Result: Ney (72k) attacks Wellington (52k) and LOSES with 2:1 casualty ratios. After 5+ attacks across multiple turns with 100k+ combined French forces, Waterloo was never taken. Wellington's strength barely decreased.

**Recommendation:** Cap total defense modifier at ~50%, or make fortification degrade faster under repeated assaults, or give the attacker meaningful ways to counter (bombardment should strip fortification before assault).

---

### B2: Supply Attrition Creates Death Spiral at Belgium

Belgium supply cap: 25,000. Having 2-3 marshals there (80k-100k troops) causes ~4,000 losses per turn. Combined with battle casualties, the player's staging area actively destroys their army.

**Recommendation:** Increase supply cap for towns, or allow "supply depot" building to meaningfully increase capacity, or reduce attrition to 1% instead of 2%.

---

### B3: Enemy AI Gets Too Many Attacks Per Turn

Gneisenau attacked Davout 4 times in a single turn (Turn 5). Wellington made 3-4 attacks per turn. Each enemy nation appears to get 3-4 military actions, and with 3 enemy nations that's 9-12 enemy actions vs the player's 4 AP.

**Recommendation:** Ensure enemy action budget is visible/transparent, or reduce enemy actions to match player pacing.

---

### B4: Gold Accumulates With No Outlet

By Turn 12: 8,700g treasury, climbing ~700g/turn. Building is limited (1 per region, 2-turn delay). Recruitment is 1 per admin action. No way to spend gold fast enough.

**Recommendation:** Allow multiple recruits per turn, or add expensive but impactful options (mercenaries, forced march supplies, diplomatic gifts).

---

## WHAT WORKS WELL

1. **Marshal Personalities** — Ney's aggression vs Davout's caution creates real dilemmas. Ney objecting to drilling and suggesting attack instead? Perfect characterization.

2. **Objection System** — "Ney firmly objects: 'I have concerns about this order, Sire.'" Trust/Insist/Compromise is a meaningful choice. Trusting Ney led to him attacking Uxbridge and winning — vindication system rewarded the trust.

3. **Diplomacy Depth** — Saxony proposing non-aggression on Turn 2, Britain begging for armistice by Turn 5, Talleyrand suggesting we cede Belgium ("our least valuable territory") when we're losing. Smart, contextual, feels alive.

4. **Information Systems** — Morning dispatch, strategic ledger (6 tabs), marshal overview, diplomatic ledger (4 tabs), fog bands ("large force" / "substantial force"). Excellent situational awareness.

5. **Economy Model** — Stability decay from battles, war damage, supply capacity, building system. Belgium's stability dropped from 100 to 10 after repeated fighting — meaningful consequence.

6. **Error Messages** — Berthier's in-character responses: "Sire, I must confess this order eludes me." Charming, helpful, never breaks immersion.

7. **Talleyrand Commentary** — "They are desperate, Sire. We could demand far more." Context-aware diplomacy advice. "I've selected our least valuable border territory for cession." Excellent.

8. **Fog of War** — Only seeing "large force near Waterloo" instead of exact numbers. Forces real decision-making under uncertainty.

---

## SESSION PLAN: Playtest Bug Fixes

**Priority order:** Critical bugs first (game-breaking), then major, then balance.

### Session 1: Critical Bug Fixes (C1 + C2 + C3)

| Bug | Fix | Est. Tests |
|-----|-----|-----------|
| C1: Armistice deadlock | Engagement check → `is_at_war()`, force-retreat in `cleanup_war_end()` | ~15 |
| C2: Self-combat | Guard in `resolve_battle()`, audit target resolution | ~10 |
| C3: Turn skip | Debug logging, double-advance guard, trace root cause | ~8 |

### Session 2: Major Bug Fixes (M1 + M2 + M3)

| Bug | Fix | Est. Tests |
|-----|-----|-----------|
| M1: Raw state name | Display name mapping for diplomatic types | ~3 |
| M2: Parse "recruit infantry" | Mock parser keyword update | ~5 |
| M3: Recruit type/amount control | Parser + executor updates | ~8 |

### Session 3: Minor Fixes + Balance Pass (m1-m4, B1-B4)

| Item | Fix | Est. Tests |
|------|-----|-----------|
| m1: "trust" keyword | Route objection keywords in /command | ~3 |
| m2: Duplicate notifications | Dedup counter-punch | ~2 |
| m3: Artillery morale | Cap bystander morale loss | ~3 |
| m4: Redundant route | Direct move for 1-hop | ~2 |
| B1: Wellington defense cap | Cap total defense at 50% | ~5 |
| B2: Supply attrition | Reduce to 1% or increase town caps | ~3 |
| B3: Enemy action count | Review/reduce per-nation budget | ~3 |
| B4: Gold outlet | Multiple recruits or new spending options | ~5 |

**Total estimated: ~75 new tests across 3 sessions.**
