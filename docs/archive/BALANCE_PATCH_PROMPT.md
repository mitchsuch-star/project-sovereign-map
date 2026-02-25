# Balance Patch — Session Prompt

**Context:** A full playtest (3 games, ~25 turns) revealed critical balance issues. This document contains the raw findings from that playtest, proposed fixes, and known root causes. **Your job is NOT to blindly implement these proposals.** Read CLAUDE.md first for project rules, then:

## YOUR MANDATE

1. **Review every issue and proposed fix below.** For each one, tell me whether you agree with the diagnosis, whether the proposed fix is the right approach, and whether there's a better solution. Push back if something seems wrong.

2. **Think about the bigger map.** The current 13-region map is a stepping stone. We're building toward a larger campaign map. Fixes must scale — don't hard-code solutions that only work for this specific layout. If attrition rates are wrong, fix the formula, don't patch individual regions.

3. **Look for related issues we missed.** The playtest found these problems, but they may be symptoms of deeper issues. For example: if the AI never defends rear territory, is that JUST a missing priority, or is the entire AI evaluation structure flawed in a way that will cause other problems on a bigger map? If supply attrition is too punishing, are there OTHER systems (morale recovery, recruitment costs, building effectiveness) that compound the problem?

4. **Check for cascade effects.** Changing attrition rates affects the AI too — will the Prussian deathball become MORE dominant if they stop bleeding? Nerfing Wellington's strength changes combat math — does that break other balance assumptions? Trace each change through the system.

5. **Propose a coherent plan.** Don't just fix each issue in isolation. Tell me how the fixes interact and what the game should feel like after the patch. Then implement.

The core problems are:
- **Attrition is too high across the board** — it dominates tactics on the current map and will be even worse on a bigger map with more chokepoints
- **The AI is too stupid** — it doesn't defend territory, doesn't split forces, gets stuck in fortify loops, and has no strategic awareness beyond "attack nearest enemy"
- **The economy punishes the player for existing** — France starts negative and captured territory gives almost nothing

These are CORE SYSTEM issues, not number tweaks. Fix them as systems.

---

## PLAYTEST FINDINGS & PROPOSED FIXES

### TASK 1: AI Rear Territory Defense & Deathball Splitting (CRITICAL)

### Problem
The enemy AI never defends territory behind its front line. In playtesting, the player abandoned Belgium, sent Ney through Lyon → Rhine → Bavaria → Vienna capturing all 5 Prussian/British rear territories **completely unopposed**. The Prussian 3-marshal stack (120k troops) captured Belgium on turn 1 and then **sat there for the entire game**, never sending a single marshal to defend Rhine, Bavaria, or Vienna.

### Root Cause (from investigation of `backend/ai/enemy_ai.py`)

1. **No homeland defense priority exists.** The AI priority system (P0-P8) has zero logic for detecting when friendly territories are being captured. All territory logic is offensive:
   - P4.5 (Undefended Capture, ~line 2158-2247): Only captures ENEMY territory (`adj_region.controller != nation`)
   - P7 (Strategic Move, ~line 2884-3107): Only advances TOWARD enemies or falls back FROM enemies
   - No priority checks "which regions did I own that I don't own now?"

2. **The deathball never splits.** `_find_best_action()` (~line 560-820) uses greedy single-best-action selection: for each of the nation's 4 actions per turn, it picks THE single best action across all marshals. When 3 marshals are co-located, they all evaluate the same target and the system picks one, then repeats. No force distribution, no rotation, no secondary objectives.

3. **Stagnation system fails because fortify counts as "meaningful."** The `meaningful_actions` set (~line 854) includes `"fortify"`, so a cautious marshal that fortifies every turn never triggers the stagnation counter (≥2 idle turns). The cycle:
   - Turn 1: P5 → FORTIFY (stagnation resets to 0)
   - Turn 2: Already fortified → WAIT (stagnation = 1)
   - Turn 3: P7.5 stagnation ≥ 2 → UNFORTIFY
   - Turn 4: Cooldown blocks re-fortify → WAIT
   - Turn 5: Cooldown expires → P5 → FORTIFY again (stagnation resets)
   - **Infinite loop.** Marshal never advances.

4. **Cautious advance fails when all adjacent regions don't reduce distance to enemy.** P7 cautious advance (~line 3071-3087) requires `dist < current_dist` — if no adjacent region is closer to the nearest enemy, it returns None and falls through to P8 which just waits.

### Required Fix

**A. New Priority: P3.7 "Homeland Defense" (between P3 and P4)**

When a nation has lost regions it previously controlled, redirect the nearest available marshal to recapture them. Logic:

```
For each marshal being evaluated:
  1. Get list of regions this nation controlled at game start but doesn't now
  2. Filter to regions that are adjacent to or within 2 moves of this marshal
  3. If any lost regions exist AND this marshal isn't engaged/broken/retreating:
     - If lost region is adjacent and undefended: MOVE to capture it (like P4.5 but for OWN territory)
     - If lost region is adjacent and defended: evaluate ATTACK if ratio is favorable
     - If lost region is 2 moves away: MOVE toward it
  4. Priority: Higher than P4 (attack opportunity) but lower than P3 (threat response)
```

Track starting territory per nation — add a `starting_regions` dict to WorldState or compute from the known control_map in `_setup_initial_control()`.

**B. Force Distribution: Limit same-marshal consecutive actions**

In `process_nation_turn` / `_find_best_action()`, add a soft penalty: if a marshal acted in the previous action slot this turn, apply a priority penalty (e.g., +1 to their priority score) so other marshals get a chance. This doesn't prevent the best marshal from acting but encourages splitting when multiple marshals have similar priorities.

**C. Fix Stagnation Counter**

Remove `"fortify"` from `meaningful_actions` (~line 854). Fortifying when no enemy is nearby is NOT a meaningful action — it's the core of the stagnation loop. Alternatively, only count fortify as meaningful if an enemy is within 2 regions.

**D. Fix Cautious Advance Fallback**

In the P7 cautious advance block (~line 3071-3105), when no adjacent region reduces distance to nearest enemy, add a fallback: pick any adjacent friendly region the marshal hasn't visited in the last 3 turns. This prevents the "no valid move" dead end.

### Test Plan
- Test: Start game, abandon Belgium, rush south. AI should detect lost Rhine/Bavaria/Vienna and send at least 1 marshal to recapture.
- Test: Prussian 3-marshal stack should split when they have both a frontline target AND lost rear territory.
- Test: Wellington should not fortify-loop indefinitely at Waterloo. After 3-4 turns, stagnation should force actual movement.
- Test: Existing AI behavior (P0 engagement, P4 attacks, P4.5 captures) must not regress.
- Run full test suite: `".venv\Scripts\python.exe" -m pytest tests/ -v`

---

## TASK 2: Supply Attrition Tuning (HIGH)

### Problem
Supply attrition dominates all other mechanics. Both sides lose more troops to overcrowding than to combat. Belgium (20k capacity) holds 105k French troops at game start = 5% attrition/turn = 5,250 losses. The Prussian deathball suffers similarly after taking Belgium.

### Current System (`backend/models/world_state.py`, `process_supply_attrition()` ~line 2141)

```python
excess_ratio = (total - cap) / cap
if excess_ratio <= 0.25:    attrition = 0.01   # 1%
elif excess_ratio <= 0.50:  attrition = 0.03   # 3%
else:                       attrition = 0.05   # 5%
```

Home territory bonus: 1.5x effective capacity.

Supply capacities from `region.py` (`SUPPLY_BY_TYPE` ~line 101):
- capital: 50,000 (Paris effective: 60k after urban 1.2x)
- major_city: 40,000 (Lyon: 36k after hills 0.9x, Vienna: 48k after urban 1.2x)
- city: 30,000 (Marseille: 30k, Milan: 36k)
- town: 20,000 (Belgium: 20k, Rhine: 20k, Bavaria: 18k, Geneva: 10k after mountain 0.5x)
- rural: 15,000 (Netherlands: 15k, Waterloo: 13.5k, Brittany: 12k, Bordeaux: 15k)

### Required Fix: Balanced Tuning

Apply TWO changes:

**A. Raise the town supply base from 20,000 to 25,000** in `SUPPLY_BY_TYPE` (region.py ~line 101). This gives Belgium 25k base × 1.5 home = 37.5k effective (up from 30k). Excess ratio for 105k French: (105k-37.5k)/37.5k = 1.8, still hitting the top tier but with lower rate.

**B. Lower the attrition rates and widen thresholds** (world_state.py ~line 2168):

```python
# OLD:
if excess_ratio <= 0.25:    attrition = 0.01
elif excess_ratio <= 0.50:  attrition = 0.03
else:                       attrition = 0.05

# NEW:
if excess_ratio <= 0.50:    attrition = 0.005   # Was 1% at 0.25 → now 0.5% at 0.50
elif excess_ratio <= 1.00:  attrition = 0.02    # Was 3% at 0.50 → now 2% at 1.00
else:                       attrition = 0.03    # Was 5% → now 3%
```

**Net effect on Belgium (French, 105k in 37.5k effective):**
- Old: 5% = 5,250 losses/turn
- New: excess ratio 1.8 → 3% = 3,150 losses/turn (40% reduction)
- Still meaningful — you should spread out, but it's not an instant death sentence

**Net effect on Paris (French, 73k in 90k effective):**
- Old: under capacity → 0 attrition ✓
- New: same → 0 attrition ✓ (Paris can hold Davout + Drouot comfortably)

### Test Plan
- Verify Belgium attrition with Ney+Grouchy is ~3% not 5%
- Verify Paris with Davout+Drouot has 0 attrition (under 90k effective)
- Verify enemy stacks also benefit (Prussians in Netherlands/Belgium)
- Run: `".venv\Scripts\python.exe" -m pytest tests/ -v`

---

## TASK 3: Wellington Starting Strength Reduction (MEDIUM)

### Problem
Wellington at 68,000 with Hills terrain (+15%), Cautious outnumbered (+10%), and Reverse Slope (+5%) is nearly unkillable. Three consecutive combined-arms attacks barely dented him. Reducing starting strength makes him beatable without removing his defensive identity.

### Fix
In `backend/models/marshal.py`, `create_enemy_marshals()` (~line 1417):

```python
# OLD:
strength=68000,

# NEW:
strength=52000,
```

This brings Wellington from 68k to 52k. With his ~30% stacked defense bonuses, his effective defensive strength is still ~67k (52k × 1.30), making him tough but beatable by a committed 2-marshal assault. Ney (72k) can now realistically fight him 1v1 with a drill bonus.

### Test Plan
- Verify Wellington's starting strength is 52,000
- Run tests that reference Wellington's starting strength (search for "68000" in tests/)
- Run: `".venv\Scripts\python.exe" -m pytest tests/ -v`

---

## TASK 4: French Starting Economy Fix (HIGH)

### Problem
France starts at -40 gold/turn (income 850, upkeep 890). With 600 starting gold, this guarantees a slow bleed toward bankruptcy. The problem compounds when Paris stability drops from enemy attacks (-10 per battle), reducing Paris income from 300 to 75 (at 50 stability = 25% modifier).

Paris stability drops NOT from enemy adjacency but from repeated combat in the region. Each battle costs -10 stability. After the enemy takes Belgium, they attack Paris every few turns, cratering stability.

### Fix: Reduce French upkeep to break-even

The simplest fix: **reduce Grouchy's starting strength from 33,000 to 28,000.** This:
- Reduces French upkeep by ~25g (at 5g per 1000 troops)
- Brings net from -40 to roughly -15 (slightly negative but survivable)
- Also helps Belgium supply: 72k + 28k = 100k vs 105k (slight improvement)
- Grouchy at 28k is still a useful force (historical Grouchy had a smaller corps anyway)

In `backend/models/marshal.py`, `create_starting_marshals()` (~line 1306):
```python
# OLD:
strength=33000,

# NEW:
strength=28000,
```

Additionally, **increase France starting gold from 600 to 800.** This gives a 5-turn buffer before economic pressure hits, enough to capture 1-2 territories.

In `backend/models/world_state.py`, find the French starting gold initialization and change 600 → 800.

### Test Plan
- Verify turn 1 economy is near break-even (within ±20g)
- Verify Grouchy starts at 28,000
- Search tests for "33000" and "600" gold references
- Run: `".venv\Scripts\python.exe" -m pytest tests/ -v`

---

## TASK 5: "stance neutral" Parse Fix (LOW)

### Problem
`"Ney, stance neutral"` fails to parse. The mock parser in `backend/ai/llm_client.py` (~line 616) checks for `"neutral stance"` but not `"stance neutral"`. The fallback regex at ~line 626 has an explicit exclusion: `and "stance" not in command_lower`, which blocks "stance neutral" from matching.

### Fix
In `backend/ai/llm_client.py` (~line 616), add `"stance neutral"` to the keyword list:

```python
# OLD:
elif any(kw in command_lower for kw in ["neutral stance", "go neutral", "adopt neutral",
                                          "return to neutral", "take neutral",
                                          "switch to neutral"]):

# NEW:
elif any(kw in command_lower for kw in ["neutral stance", "stance neutral", "go neutral",
                                          "adopt neutral", "return to neutral", "take neutral",
                                          "switch to neutral"]):
```

Also add `"stance defensive"` and `"stance aggressive"` to their respective blocks for consistency (~lines 608-614 and 600-606).

### Test Plan
- Test "Ney, stance neutral" parses to stance_change with target "neutral"
- Test "Davout, stance defensive" still works
- Test "Ney, stance aggressive" still works
- Run: `".venv\Scripts\python.exe" -m pytest tests/ -v`

---

## TASK 6: First-Time Fortify Cost Hint (LOW)

### Problem
When a player fortifies from neutral stance, it auto-shifts to defensive + fortifies (2 AP total). The `[Auto-shifted to DEFENSIVE stance first]` prefix appears but doesn't explain WHY it cost 2 AP. New players get confused when they burn 2 AP unexpectedly.

### Fix
In `backend/commands/executor.py`, in the `_execute_fortify` method (~line 7874), enhance the auto-shift message:

```python
# OLD:
stance_message = "[Auto-shifted to DEFENSIVE stance first] "

# NEW:
stance_message = "[Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] "
```

This is a one-line change. The message only appears when the auto-shift actually happens (neutral → defensive before fortify), so experienced players who are already in defensive stance won't see it.

### Test Plan
- Verify the message appears when fortifying from neutral
- Verify the message does NOT appear when already in defensive stance
- Run: `".venv\Scripts\python.exe" -m pytest tests/ -v`

---

## Priority Order

1. **Task 1** (AI homeland defense + deathball splitting) — eliminates dominant exploit
2. **Task 2** (Supply attrition tuning) — makes the game less punishing
3. **Task 4** (French economy fix) — removes death spiral
4. **Task 3** (Wellington nerf) — enables offensive play
5. **Task 5** (Stance neutral parse) — trivial bugfix
6. **Task 6** (Fortify hint) — trivial UX improvement

Tasks 5 and 6 are one-line fixes that should be done first as warmup. Task 1 is the largest and most impactful.

---

## Key Files to Read First

- `backend/ai/enemy_ai.py` — AI decision tree (5000+ lines, the core of Task 1)
- `backend/models/world_state.py` — supply attrition, economy, starting state
- `backend/models/marshal.py` — marshal starting stats (create_starting_marshals, create_enemy_marshals)
- `backend/models/region.py` — supply capacity constants
- `backend/ai/llm_client.py` — mock parser (stance fix)
- `backend/commands/executor.py` — fortify message

## Rules Reminder
- All numbers to Godot must be `int()`
- Combat modifiers: SINGLE SOURCE in `marshal.py`
- Run serialization test if new fields added: `".venv\Scripts\python.exe" -m pytest tests/test_serialization_enforcement.py -v`
- Update `docs/SYSTEMS_REFERENCE.md` if system behavior changes
- Update `docs/SAVE_FORMAT_REFERENCE.md` if new fields added

---

## PLAYTEST RAW DATA (for reference)

### Game 1: Aggressive Opening (disaster)
- Turn 1: Ney attacks Waterloo from Belgium. 10,780 French casualties vs 7,009 Wellington. Both remain.
- Turn 1: Grouchy attacks Waterloo. 8,810 Grouchy casualties vs 2,652 Wellington. Ney retreats to Belgium.
- Turn 1: Davout moves to Belgium. End turn.
- Turn 2: All 3 attack Paris (Wellington captured it during enemy phase). Three attacks with combined arms couldn't break Wellington at urban terrain (+20%).
- Result: France lost ~78k troops in 2 turns. Paris captured. Drouot went from 25k to 4k from Belgium attrition. Death spiral.

### Game 2: Defensive Opening (Belgium falls)
- Turn 1: Davout fortifies Paris. Ney moves to Paris. Grouchy couldn't fortify (2 AP needed, 1 remaining). End turn.
- Turn 2: All French in Paris = 168k in 90k effective capacity = 5% attrition bleeding everyone.
- Turn 2: Spread to Lyon. Grouchy left in Belgium alone (31k).
- Turn 3: Prussian deathball (120k) destroyed Grouchy. Belgium captured. Grouchy reduced to 1k.
- Turns 3-5: Davout repeatedly attacked in Paris, stability cratered from 100→50, income from 300→39.
- Result: Economy collapsed to -85/turn. Grouchy destroyed. Death spiral.

### Game 3: Southern Bypass (dominant meta — worked)
- Turn 1: Evacuate Belgium (Grouchy strategic march, Ney moves to Paris). Davout defends.
- Turn 2: Spread Ney+Drouot to Lyon. Belgium falls to Prussia (expected).
- Turn 3: Ney captures Rhine (unopposed). Grouchy captures Geneva (unopposed).
- Turn 4: Ney captures Bavaria (unopposed). Grouchy captures Milan (unopposed).
- Turn 5: Ney captures Vienna (unopposed). France controls 10/13 regions.
- Turn 6-9: Economy stabilizes. Counterattack on weakened Prussians (57k down from 120k due to Belgium attrition). Wellington down to 13k. Uxbridge destroyed entirely.
- Result: France wins by turn 9 via flanking empty territory. AI never defended rear.

### Enemy Force Degradation (Game 3, Turn 9)
- Wellington: 68k → 13.6k (attacked Paris repeatedly, bled from combat + Waterloo supply)
- Uxbridge: 18k → destroyed (presumably attacked Paris and died)
- Blucher: 55k → 8.4k, morale 65 (Belgium supply attrition for 8 turns)
- Gneisenau: 45k → 9.6k, morale 14 (Belgium supply attrition)
- PrinceAugust: 20k → 9.5k, morale 34 (Belgium supply attrition)
- **The AI lost more troops to supply attrition than to any player action.**

### Key Insight
The "Southern Bypass" strategy works because:
1. Belgium is indefensible (105k French vs 120k Prussians, supply bleeding both)
2. All enemy rear territory is completely undefended
3. The AI deathball captures Belgium and then NEVER splits or advances
4. Supply attrition destroys the deathball while it sits in Belgium doing nothing
5. The player captures 5 regions without a single battle

This is the ONLY viable strategy. All others lead to death spirals. On a bigger map, this pattern would be even more extreme — the AI would cluster on the front line while the player runs around capturing everything behind it.

---

## QUESTIONS FOR YOU TO ANSWER BEFORE IMPLEMENTING

1. **Attrition rates:** The proposed fix (0.5%/2%/3%) is a 40-60% reduction. Is that enough? Too much? Should attrition scale differently — e.g., proportional to excess rather than tiered? Would a continuous formula like `attrition = min(0.03, excess_ratio * 0.02)` be better than hard tiers?

2. **AI force splitting:** The proposed "soft penalty for repeated marshal action" is gentle. Should it be harder — e.g., "no marshal can take more than 2 actions per turn"? Or should the AI have explicit "assign marshals to theaters" logic?

3. **Homeland defense priority:** P3.7 is proposed as a static priority check. But on a bigger map with 30+ regions, checking all lost territory every marshal evaluation could be expensive. Is there a smarter architecture — e.g., a nation-level "strategic threat assessment" that runs once per turn and assigns objectives?

4. **Economy:** France starting at -40 net is clearly wrong. But is reducing Grouchy's strength the right lever? Or should upkeep rates be lower across the board (affects ALL nations)? Should captured territory income scale faster?

5. **Stability recovery:** Captured regions start at 25 stability (0% income). Should secure give 40 stability (25% income immediately)? Should there be a "pacification" mechanic where garrisoning a marshal speeds recovery?

6. **What else is broken that the playtest didn't catch?** You have access to the full codebase. Are there other systems (morale, recruitment, buildings, strategic commands) that have similar balance problems waiting to surface on a bigger map?
