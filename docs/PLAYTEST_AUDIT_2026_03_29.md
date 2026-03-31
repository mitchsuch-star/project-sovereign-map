# Playtest Audit — March 29, 2026

> **Source:** 3 automated playtests (mock LLM mode), 25+ turns total.
> **Playtests:** "The Ney Gambit" (aggressive rush, defeat Turn 3), "The Diplomat's Game" (defensive + diplomacy, armistice by Turn 6), "The Iron Wall" (full turtle, war score +39 by Turn 10).

---

## Summary

| Severity | Count | Description |
|----------|-------|-------------|
| CRITICAL | 1 | Turn skip (KNOWN — C3 from March playtest, still unfixed) |
| MAJOR | 4 | Mock parser "status", armistice error messages (x2), SUPPORT armistice vulnerability |
| MINOR | 2 | Emoji encoding (40+ instances across 7 files), bombardment_streak dead tracking |
| ENHANCEMENT | 1 | AP warning on end turn (new feature) |
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

Additionally, "status" is **confirmed missing from `parser.py` valid_actions list** (lines 44-93, 45 actions listed, no "status"). This means even in LLM mode, the parser would reject "status" as an invalid action.

**Fix:**
1. Add "status" keyword matching in `_parse_with_mock()` alongside the existing "help" and "end turn" paths. Return `{"action": "status", "marshal": None, "target": None}`.
2. Add "status" to `parser.py` valid_actions list (confirmed missing).

**Files:** `llm_client.py`, `parser.py`
**Tests:** ~4 (parse "status" in mock mode, parse "Berthier status", parse "show status", verify valid_actions includes "status")

---

### PT-3: Emoji Encoding Broken in Cavalry Warning (MINOR)

**Reproduction:** Playtest 3, Turn 4. Cavalry restless warning shows `"�\xa0�\udc8f Ney's horses grow restless"` — garbled surrogate pair.

**Root cause:** Literal Unicode emoji characters throughout the backend. Multi-byte emoji may not survive Windows CP-1252 encoding or JSON serialization through the FastAPI response pipeline, producing garbled surrogate pairs.

**Scope:** 40+ emoji occurrences across 7 backend files (not just cavalry warnings):

| File | Count | Emoji Used |
|------|-------|------------|
| `combat_executor.py` | 13 | ⚠️, 💀, 🐴, ⛔, ⚔️, 🛡️ |
| `world_state.py` | 15 | ⚠️, 🐴, 🔥, 💀, 🎯 |
| `combat.py` | 9 | 🐴, ⚔️, ⚠️, 🔥 |
| `meta_executor.py` | 2 | ⚠️, 🐴 |
| `executor.py` | 1 | 💀 |
| `movement_executor.py` | 1 | ⚠️ |
| `tactical_executor.py` | 1 | ⚠️ |
| `enemy_ai.py` | 2 | 🎯 (debug only — low priority) |

**Fix:** Replace all player-facing emoji with plain text markers. The game's aesthetic is text-based military dispatches — emoji are out of place anyway. Specific replacements:
- ⚠️ → `[!]` or `WARNING:`
- 🐴 → `[Cavalry]`
- 🐴🔥 → `[Cavalry Critical]`
- 🐴⚔️ → `[Cavalry Charge]`
- 🐴⛔ → `[Cavalry Blocked]`
- 🐴⚠️ → `[Cavalry Warning]`
- 💀 → `[Destroyed]`
- ⚔️ → `[Combat]`
- 🛡️ → `[Defend]`
- 🎯 in `enemy_ai.py` — debug-only, can keep or replace last

**Files:** `world_state.py`, `combat_executor.py`, `combat.py`, `meta_executor.py`, `executor.py`, `movement_executor.py`, `tactical_executor.py`
**Tests:** ~3 (grep all backend .py files for emoji codepoints, verify no surrogates in any message strings, verify replacement markers render in Godot)

---

## Session 2: Armistice Errors + AP Warning + Cleanup (5 findings)

### PT-4: "Unknown target" During Armistice — Attack (MAJOR)

**Reproduction:** Playtest 2, Turn 7. After accepting armistice with Prussia, `"Davout, attack Gneisenau"` → `"Unknown target: Gneisenau"`. Should say something like "Cannot attack Gneisenau — armistice is in effect with Prussia."

**Root cause:** `combat_executor.py` calls `_fuzzy_match_enemy()` → `world_state.py:get_enemy_by_name_for_nation()` which filters by `is_at_war()`. During armistice, returns None. The error path then generates a generic "Unknown target" message without checking WHY the target wasn't found.

**Fix:** After fuzzy match fails, check if the target name matches ANY marshal (regardless of war status). If it matches a marshal whose nation is in armistice/peace, return a diplomatic-context error message: "Cannot attack {target} — {relation} with {nation} is in effect."

**Files:** `combat_executor.py` (attack validation), possibly `executor.py` (`_fuzzy_match_enemy`)
**Tests:** ~4 (attack during armistice, attack during peace, attack during war, attack unknown name)

---

### PT-5: Pursue/Support Use Generic Lookup — Bypass Armistice (MAJOR)

**Reproduction:** Playtest 2, Turn 5. After armistice with Britain, `"Ney, pursue Wellington"` → "Wellington spotted at Waterloo! Engaging! Unknown target: Wellington" — contradictory messages, and 2 AP consumed for a failed action.

**Root cause:** `strategic_executor.py` calls `world.get_marshal(target)` at both line 415 (PURSUE) and line 459 (SUPPORT) — a generic lookup without war status filtering. For PURSUE: Wellington is found → "spotted at" message generated at line 940 → then war-status-aware combat lookup fails → "Unknown target" message. AP is consumed when the strategic order is created, before the combat-phase war-status check runs.

SUPPORT has the same vulnerability at line 459: `world.get_marshal(target)` resolves any marshal regardless of diplomatic status.

**Fix:**
1. Pre-validate diplomatic status BEFORE AP consumption. In `strategic_executor.py`, after resolving the target marshal via `get_marshal()`, check hostility: `world.is_at_war(executing_marshal.nation, target_marshal.nation)` for PURSUE, or appropriate ally check for SUPPORT. If invalid, return error with 0 AP cost.
2. Do NOT replace `get_marshal()` with `get_enemy_by_name_for_nation()` for PURSUE — the generic lookup is fine for finding the marshal, but needs a war-status gate before proceeding.
3. Return diplomatic-context error: "Cannot pursue Wellington — armistice with Britain is in effect."

**Files:** `strategic_executor.py` (line ~415 PURSUE validation, line ~459 SUPPORT validation, line ~940 "spotted at" message)
**Tests:** ~6 (pursue during armistice, pursue during peace, pursue during war, SUPPORT during armistice, SUPPORT allied marshal during war, SUPPORT enemy marshal error)

---

### PT-6: No AP Warning on End Turn (ENHANCEMENT)

**Observation:** Every playtest. Player types "end turn" with 4 AP remaining, turn ends silently with no warning about unused actions. This is new behavior, not a bug fix.

**Fix:** In `meta_executor.py:_execute_end_turn()`, check `world.actions_remaining > 0` or `world.admin_actions_remaining > 0`. If either has remaining actions, add a warning to the response message: "Warning: {N} action(s) unused this turn." The turn still ends (no confirmation needed — that would require dialogue state), but the message alerts the player. Note: strategic orders (MOVE_TO, PURSUE, etc.) consume AP on issuance, not per-turn — so remaining AP genuinely means unused actions.

**Files:** `meta_executor.py`
**Tests:** ~3 (warning with AP remaining, no warning with 0 AP, warning with only admin AP remaining)

---

### PT-7: `bombardment_streak` Tracked But Never Used (MINOR)

**Discovery:** Code review during audit. `marshal.py` initializes `bombardment_streak` (line 418), resets it per-turn (line 540), and serializes it (line 1158/1308) — but `_execute_bombardment` in `combat_executor.py` (lines 1502-1512) uses a fixed `0.10` degradation amount and never reads the streak value.

**Root cause:** Field was added in anticipation of bombardment streak scaling but the mechanic was never wired. Dead tracking code wastes serialization space.

**Fix:** Two options:
1. **Remove** the field entirely (if bombardment streak scaling is deferred) — delete from `__init__`, `to_dict`, `from_dict`, turn reset.
2. **Wire it** as part of the Design Discussion's "bombardment streak scaling" proposal — but that requires design gate approval first.

**Recommendation:** Keep the field but document it as "reserved for bombardment streak scaling" in a comment. Remove if the design discussion rejects streak scaling.

**Files:** `marshal.py` (lines 418, 540, 1158, 1308), `combat_executor.py` (lines 1502-1512)
**Tests:** ~1 (verify bombardment_streak resets correctly, or verify removal doesn't break serialization)

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

### Current War Score System

Four components, each independently capped. Total capped at ±100. Recalculated every turn.

| Component | Cap | How Earned |
|-----------|-----|------------|
| **Territory** | ±40 | +5 per enemy starting region you control |
| **Battles** | ±30 | +3 per battle won (records pruned after 10 turns) |
| **Decisive battles** | ±20 | +10 per decisive battle won |
| **Capital** | ±30 | +20 for holding enemy capital, +10 for contesting it |

**Decay:** -2/turn toward 0 when no battles for 3+ turns. Decisive battle bonuses don't decay.

**How it's used:**
- Peace deal acceptance formula: `war_score * 0.3` modifier
- Military pressure on acceptance: `min(15, war_score * 0.15)`
- Vassalage demands require war_score > 80
- AI behavior shifts at ±20 (winning/losing thresholds)

**What's missing:** No ticking component. A stalemate trends toward 0 via decay. Defensive wins give the same +3 as offensive wins. A turtle who wins defensive battles and holds their own territory can reach +30 battle score without ever attacking. An attacker who captures regions gets territory score but their battle score decays if they pause. The system doesn't punish passivity.

### EU4 War Score Reference

EU4 uses three independent war score sources, each capped:

| Source | Cap | Mechanic |
|--------|-----|----------|
| **Battles** | ±40% | Based on army size destroyed. Large decisive battles matter most. |
| **Occupation** | % of enemy total development | Forts give credit for zone of control (neighboring provinces). Full occupation of all enemy land → 100% war score. |
| **Ticking war score** | ±25% | +0.1%/month for holding the war goal province. Creates urgency — attacker who holds objective slowly wins even without fighting. |

Key insight: EU4 occupation alone CAN reach 100% if you take all their land — total conquest = total war score. But partial occupation alone can't force a peace deal; you need battles + occupation + time. The **ticking war score on objectives** is what makes offense mandatory — pure defense means slowly losing.

### War Objectives (Lightweight Alternative to Casus Belli)

A full EU4-style casus belli system (fabricate claims, CB types, stability hits) would be overengineering here. The game already covers the same ground through lighter systems:
- **Coalition threat** = aggressive expansion penalty (declaring war adds threat → coalition formation)
- **DP cost** = political capital gate (war declaration costs 1 DP)
- **Treaty-breaking confirmation** = unjustified war penalty (popup + trust hit for breaking armistice/non-aggression)
- **Trust reactions** = diplomatic consequences from other nations/marshals

What's actually missing is the **war goal** concept — "what are you fighting FOR?" Currently wars are just "France vs Prussia" with no objective. This matters because:
1. It's where ticking war score attaches (hold the objective → slowly win)
2. It defines what "winning" looks like
3. It gives the player a clear strategic target

#### War Goal Types

**Player-chosen at war declaration** (presented by Talleyrand in the declaration dialogue):

| Objective | Available When | Ticking Target | Ticking Rate | Cap |
|-----------|----------------|----------------|--------------|-----|
| **Conquest** | Always (you declare war) | Enemy capital | +2/turn while held | +20 |
| **Subjugation** | Target power ≤ 50% yours (Vassalage Power Cap) | Enemy capital | +3/turn while held | +25 |
| **Forced Alliance** | Always | Enemy capital | +2/turn while held | +20 |

**Auto-assigned** (no player choice):

| Objective | Set When | Ticking Target | Ticking Rate | Cap |
|-----------|----------|----------------|--------------|-----|
| **Defense** | They declare war on you | Any 1 enemy region you hold | +1/turn while held | +15 |
| **Liberation** | Coalition war vs nation with vassals | Vassal's capital region | +1/turn per liberated region held | +20 |

#### Key Design Decisions

**War goals only drive ticking score, NOT peace term constraints.** What you can *demand* at the peace table is already fully dynamic through Talleyrand's `_build_base_terms()` pipeline, which scales with war score, war exhaustion, relations, and duration. A "Conquest" war goal doesn't prevent you from demanding vassalage if you hit war_score 80 and the power cap passes — Talleyrand will naturally suggest it.

**War goals don't change mid-war.** Set at declaration, locked for the duration. The peace terms system already handles escalation/de-escalation dynamically. The war goal is a strategic commitment that determines ticking score, not a limit on what you can negotiate.

**Ticking war score is the 5th component** of `calculate_war_score()`, capped at ±25 (matching EU4). Independent of the other four components.

**Subjugation is double-gated:** Target must pass Vassalage Power Cap (≤50% of your power) AND you must hold their capital for ticking to accumulate. Ticking stacks on top of existing score but only while capital is held — lose the capital, ticking pauses (accumulated score remains).

#### Forced Alliance — Napoleon's Primary War Goal

Historically, Napoleon's wars were rarely about conquest — he fought to force nations into his system. Austria after Austerlitz, Russia at Tilsit, Prussia after Jena. The goal was alliance + Continental System membership, not annexation.

**Forced Alliance** demands a diplomatic state transition (WAR → ALLIANCE) as a peace term. The acceptance formula already handles this via war score + duration + exhaustion. When war score is high enough, Talleyrand can propose alliance terms that the enemy must accept.

**Continental System rider:** When France forces an alliance, the Continental System could be included as an automatic rider clause. The Continental System trade penalty mechanics are already implemented (`diplomacy.py:2223-2276`) — vassal auto-enrollment works, trade income reduction works — but **there is currently no way to activate it** (the mission is a skeleton with DP cost but no handler). Forced Alliance provides the missing activation path.

**Implementation note:** "forced_alliance" does not exist as a clause type yet. Needs to be added to the clause system. The acceptance formula would treat it like a harsh demand (high base resistance, requiring high war score + exhaustion to force through).

#### Liberation — Freeing Vassals

Liberation is specifically about **freeing a vassal nation** from an overlord. If France has vassalized Saxony and a coalition forms, the coalition's war goal is "Liberate Saxony."

On success (coalition holds vassal's capital region and wins peace):
- Vassal released via existing `release_vassal()` mechanic
- Liberated nation enters DEFENSIVE_ALLIANCE with the liberating nation (auto `set_diplomatic_state()`)
- Liberated nation's loyalty resets (no lingering vassalage resentment)

If the target nation has **no vassals**, coalition uses Conquest instead (hold enemy capital).

**Ticking target:** The vassal's capital region (e.g., Dresden for Saxony). Coalition must capture and hold it. Each liberated vassal's capital held ticks +1/turn independently, up to the +20 cap.

#### UX Integration — Talleyrand Dialogue Flow

**Player declares war (existing dialogue, extended):**
```
Player: "Declare war on Prussia"
    ↓
Talleyrand (war_declaration dialogue):
  "Are you certain, Sire? This will cost 1 DP.

   What is our objective?
   [1] Conquest — Hold Berlin, press for territory and concessions
   [2] Subjugation — Force Prussia into vassalage
       (Power: Prussia 400 ≤ 500 cap ✓)
   [3] Forced Alliance — Compel Prussia into our system

   [Cancel]"
```

Subjugation only appears if the Vassalage Power Cap passes. Forced Alliance always available.

**AI declares war on you (auto-assigned, morning dispatch):**
```
Morning Dispatch:
  "Prussia has declared war! Talleyrand advises we secure
   a foothold in Prussian territory to strengthen our
   negotiating position."

   War objective: Defense (hold 1 enemy region)
```

**War status panel additions:**
```python
# In build_active_wars() return dict, per war:
{
    "war_objective": {
        "type": "conquest",        # conquest/subjugation/forced_alliance/defense/liberation
        "target": "Berlin",        # ticking target region
        "ticking": True,           # currently earning ticking score?
        "ticking_score": 6,        # accumulated so far
        "ticking_cap": 20,         # max for this objective type
    },
    "breakdown": {
        "territory": 10,
        "battles": 5,
        "decisive": 8,
        "capital": 2,
        "ticking": 6,              # NEW 5th component
    },
}
```

#### Talleyrand's War Progress Reports (Morning Dispatch)

Talleyrand reports on war progress **abstractly** — no raw numbers. Uses existing morning dispatch system (`dispatch.py`).

| Condition | Talleyrand Says |
|-----------|----------------|
| Ticking active, early war | "Our position at Berlin strengthens our hand in any future negotiations." |
| Ticking active, long war | "The longer we hold Berlin, the more Prussia's resolve weakens." |
| Enemy WE > 60 | "Their armies grow weary. I sense an overture may come soon." |
| Enemy WE > 80 | "Prussia is near breaking. Now is the time to press our demands." |
| Stalemate 5+ turns | "This war drags on without resolution. Perhaps terms could be arranged." |
| War score > 60 | "We hold every advantage. A generous peace now would buy lasting goodwill — or we could press further." |
| Short war, high demands | "We have barely drawn swords — they will not concede much at this stage." |
| Forced Alliance ticking | "Each day we hold Berlin, the Prussian court grows more amenable to... cooperation." |
| Liberation ticking | "The people of Saxony see their liberators at the gates of Dresden." |

War duration naturally affects what Talleyrand suggests through the existing acceptance formula: `war_weariness_mod = min(20, turns_at_war * 2)`. Short wars produce low acceptance scores — Talleyrand's terms reflect this ("they will not concede much").

#### Existing Systems That Support War Goals (No New Mechanics Needed)

| System | Already Handles | War Goals Add |
|--------|-----------------|---------------|
| **War exhaustion** (0-200) | Infantry regen penalty, AI peace triggers, coalition defection | Context for Talleyrand's abstract reports |
| **War duration** (+2/turn acceptance, cap +20) | Longer wars → easier peace deals | Short war penalty is already built in |
| **Dynamic peace terms** (`_build_base_terms()`) | Scales demands/offers with war score | War goal doesn't constrain terms |
| **AI peace proposals** (P1/P2/P8) | AI offers peace when losing/stalemate/winning | Unaffected by war goal type |
| **Acceptance formula** (14 components) | War score, relations, exhaustion, duration, etc. | Ticking score feeds into war_score component |
| **Continental System** (trade penalties) | Vassal auto-enrollment, income reduction | Forced Alliance provides activation path |

#### Continental System Gap

The Continental System is **half-implemented**: trade penalty mechanics work, vassal auto-enrollment works, but there is no player-facing way to activate it. Current state:

| Feature | Status |
|---------|--------|
| Trade income reduction (members ↔ Britain) | Implemented (`diplomacy.py:2223-2276`) |
| Vassal auto-join (puppet/satellite) | Implemented (`diplomacy.py:2237-2248`) |
| Coalition threat decay bonus (+2 members) | Implemented (`coalition.py:160-162`) |
| Mission activation (DP cost) | Skeleton only — no handler |
| Treaty clause type | Not implemented |
| Forced Alliance rider | Not implemented (proposed above) |

**Recommendation:** Wire Continental System activation through Forced Alliance. When France forces an alliance, the target auto-joins the Continental System. This is historically accurate (Tilsit forced Russia into the system) and provides the missing activation path without building a separate mission system.

### Vassalage Power Cap (EU4-Inspired)

**Problem:** Currently vassalage demands only require war_score > 80. This means France could subjugate Austria — a 4-region great power — with the same ease as Saxony. Historically, Napoleon could puppet Saxony and Bavaria but could only force Austria into unfavorable peace terms, never full subjugation.

**Solution:** Vassalage requires the target's **National Power** to be ≤ 50% of your own. Inspired by EU4's development-based vassalization cap.

#### National Power Formula

**National Power = sum of base income values of currently controlled regions + partial vassal contribution.**

Region income values (already in `region.py`):
- Capital: 300
- Major City: 200
- City: 150
- Town: 100
- Rural: 50

Vassal contribution: **50% of vassal's power** added to lord's power. Prevents snowball (each vassal makes the next one easier) while still rewarding expansion.

#### Starting Power Table

| Nation | Regions | Income Breakdown | Base Power |
|--------|---------|-----------------|------------|
| **France** | 7 | Paris(300) + Lyon(200) + Marseille(150) + Strasbourg(150) + Normandy(50) + Bordeaux(50) + Champagne(100) | **1,000** |
| **Austria** | 4 | Vienna(300) + Bohemia(100) + Prague(150) + Tyrol(100) | **650** |
| **Saxony** | 2 | Dresden(300) + Leipzig(150) | **450** |
| **Britain** | 3 | Netherlands(300) + Hannover(50) + Hamburg(100) | **450** |
| **Prussia** | 2 | Berlin(300) + Waterloo(100) | **400** |

#### Vassalage Eligibility at Game Start (France = 1,000 power, cap = 500)

| Target | Power | ≤ 50% of France? | Eligible? |
|--------|-------|-------------------|-----------|
| Prussia | 400 | 400 ≤ 500 | YES |
| Britain | 450 | 450 ≤ 500 | YES |
| Saxony | 450 | 450 ≤ 500 | YES |
| Austria | 650 | 650 ≤ 500 | **NO** |

#### Dynamic Examples

**France conquers 1 Austrian region (Bohemia, 100):** France power = 1,100, cap = 550. Austria power = 550. Still NO (550 ≤ 550 is borderline — use strict `<` to keep it clean).

**France vassalizes Saxony first:** Saxony power = 450, 50% contribution = 225. France effective power = 1,000 + 225 = 1,225, cap = 612. Austria (650) still NO. Prevents snowball — puppeting small nations doesn't automatically unlock large ones.

**France conquers 2 Austrian regions:** France power = 1,250 (base) + maybe vassals. Austria power = 350. YES — Austria is now small enough. This represents actually defeating Austria militarily, not just winning a few battles.

**France loses Normandy + Bordeaux to coalition:** France power = 900, cap = 450. Now even Britain (450) is borderline. Losing territory has real consequences.

#### Implementation Notes

- **Where:** Gate in `vassal.py` `make_vassal()` + `validate_ap_clause()` in `diplomacy.py` (AP clause already checks war_score > 80)
- **Calculation:** New function `calculate_national_power(world, nation)` in `diplomacy.py` or `world_state.py`. Uses current region control (dynamic), not starting regions.
- **Existing data:** All needed data exists — `get_nation_regions()`, `Region.region_type`, `INCOME_BY_TYPE`, vassal dict with lord tracking. No new fields needed.
- **Display:** Show in Diplomatic Ledger nations tab — "Power: 1,000" and "Vassalage eligible: Yes/No" (already has `vassal_eligible` field)
- **Vassal contribution rate (50%)** should be a constant, not hardcoded — easy to tune later.

### Potential Design Levers

1. **Momentum bonus:** Consecutive successful attacks give stacking +5% attack (resets on loss). Thematic — Napoleon's entire strategy was momentum-based. Needs cap (+15-20%) to avoid snowball.
2. **Shock value:** First attack on a region not attacked in 3+ turns gets +10% surprise bonus. Interesting but niche.
3. **Blitz capture bonus:** Capturing a region gives gold/morale/war score multiplier. Risk of snowball if combined with momentum.
4. ~~**Fortification degradation:**~~ **ALREADY EXISTS** — natural decay after 4-8 turns + combat/bombardment degradation. See table above.
5. ~~**Bombardment fort counter:**~~ **ALREADY EXISTS** — -10% per bombardment. See artillery improvements below for ways to strengthen this.
6. **Pursuit devastation:** Attacking a retreating/broken enemy should deal massive damage. Currently pursuit damage is only a base mechanic with no cavalry-specific bonus for non-ability marshals. During armistice, "Unknown target" blocks pursuit entirely (PT-5 bug).
7. ~~**War score for territory control (EU4-style ticking):**~~ **Superseded by War Objectives above** — ticking war score now tied to specific objectives rather than generic territory control. Avoids snowball on 19-region map.

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

**Tier 2 (needs design gate, implement second):**
- War Objectives + ticking war score (5th component, Talleyrand dialogue integration)
- Vassalage Power Cap (50% threshold, dynamic, vassal 50% contribution)
- Forced Alliance war goal + Continental System activation path
- Bombardment streak scaling (-10%/-15%/-20% on consecutive bombards)

**Tier 3 (nice-to-have, later):**
- Cavalry screening (auto-reveal adjacent regions)
- Bombardment morale bonus vs fortified

**Decision needed:** Which package to approve? This affects core balance philosophy (EU4-style "defend then counter" vs HOI4-style "blitz or die"). Napoleonic warfare was highly offensive — the game should reward aggression more than it currently does.

---

## Files Modified (estimated)

| File | Session | Changes |
|------|---------|---------|
| `world_state.py` | 1 | Re-entrancy guard redesign + emoji removal (15 instances) |
| `turn_manager.py` | 1 | Debug logging at advance_turn calls |
| `executor.py` | 1 | Auto-end-turn path audit + emoji removal (1 instance) |
| `llm_client.py` | 1 | "status" keyword in mock parser |
| `parser.py` | 1 | Add "status" to valid_actions |
| `combat_executor.py` | 2 | Diplomatic-context attack error + emoji removal (13 instances) |
| `combat.py` | 2 | Emoji removal (9 instances) |
| `strategic_executor.py` | 2 | Pursue/Support war-status pre-validation (lines ~415, ~459, ~940) |
| `meta_executor.py` | 2 | AP warning on end turn + emoji removal (2 instances) |
| `movement_executor.py` | 2 | Emoji removal (1 instance) |
| `tactical_executor.py` | 2 | Emoji removal (1 instance) |
| `marshal.py` | 2 | bombardment_streak: document or remove |

**Estimated tests:** ~35 new tests across 2 sessions.
