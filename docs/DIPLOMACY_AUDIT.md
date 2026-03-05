# Diplomacy System Audit Plan

> **Created:** March 4, 2026
> **Status:** COMPLETE — Part 1 (Sections 1-6) + Part 2 (Sections 7-15) DONE
> **Scope:** Comprehensive audit of entire Phase 8 diplomacy implementation
> **Goal:** Find and fix edge cases, stuck states, contradictions, and bugs
>
> ### Part 1 Summary (Sections 1-6)
> - **7 bugs fixed:** 4 CRITICAL popup flow (A-1 through A-4), 1 CRITICAL routing (B-3), 1 safety valve (C-1/C-2), 1 missing state (L-4 VASSAL post_break_map)
> - **42 new tests** in `tests/test_audit_part1.py`
> - **5187 total tests pass** (0 failures, 3 skipped)
> - **5 design notes** (J-5 armistice placeholder, K-5/K-6 alliance conflict, L-3 break cooldown, O-5 redemption+mission)
> - Files modified: `main.py`, `executor.py`, `world_state.py`, `diplomacy.py`
>
> ### Part 2 Summary (Sections 7-15)
> - **3 bugs fixed:** 1 MEDIUM (AA-5 AI-AI alliance conflict check), 2 LOW (AL-2a/b cheat command bounds)
> - **57 new tests** in `tests/test_audit_part2.py`
> - **5244 total tests pass** (0 failures, 3 skipped)
> - **1 design note** (AH-4 marshal auto-ejection on state downgrade)
> - **3 checklist corrections** (W-2 garrison=+8 not +15, W-3 shared enemy=+2 not +10, X-1 popup at <=10 not <15)
> - Files modified: `ai_diplomacy.py`, `executor.py`
> - Sections 16-17 (Claude Playtest, UI Test Plan) deferred — require manual Godot testing

---

## How to Use This Document

Each section is a self-contained audit area. Work through them sequentially.
For each item: investigate → document finding → fix if needed → mark status.

Status key: `[ ]` = not started, `[~]` = in progress, `[x]` = done/verified, `[!]` = bug found & fixed

---

## Section 1: Popup & Dialogue Flow (CRITICAL — Known Bug)

**Known symptom:** Repeatedly ending turn shows "Talleyrand waiting response" with no popup visible. Battle phase never displays.

### 1.1 Root Cause Analysis

The end-turn → AI proposal → popup flow has a sequencing flaw:

```
End Turn Flow:
  executor._execute_end_turn()
    → turn_manager.end_turn()
      → _process_ai_diplomatic_phase()
        → deliver_ai_proposal()
          → sets world.pending_diplomatic_dialogue (blocking=True)
          → sets world.incoming_proposal_popup
      → advance_turn()
    → builds result dict (no diplomatic_dialogue key)
  → main.py builds response
    → line 773-778: adds response["diplomatic_dialogue"] if ai_proposal in result
    → line 826-831: reads incoming_proposal_popup → response["incoming_proposal"] → clears from world
  → Godot _on_command_result()
    → line 733: checks incoming_proposal → shows popup → RETURN (skips everything after)
    → line 826: enemy_phase check → NEVER REACHED because of return above
```

**Bug A — Enemy phase never shown when AI proposal arrives during end_turn:**
- Godot's `_on_command_result()` checks `incoming_proposal` popup at priority 6 (line 733)
- It returns early → enemy phase dialog at priority 12+ (line 826) never reached
- Player never sees battle results from that turn

**Bug B — "Talleyrand waiting response" with no popup on subsequent commands:**
- After first response, `world.incoming_proposal_popup` is cleared (line 829)
- `world.pending_diplomatic_dialogue` stays blocking
- On next command, executor guard (line 1386) returns `diplomatic_dialogue` + `awaiting_diplomatic_response`
- main.py early return (line 591) sends cleaned result — no `incoming_proposal` key
- Godot checks for `incoming_proposal` (line 733) — not found
- No popup shown, but executor blocks all commands → stuck

**Bug C — End turn blocked when dialogue pending:**
- executor._execute_end_turn() line 898: blocks with "You must respond to the diplomatic matter"
- No popup data included in this response
- Player stuck: can't end turn, can't see popup

### 1.2 Audit Checklist — Popup Flow

- [!] **A-1:** Fix priority ordering — incoming_proposal popup must NOT preempt enemy phase. **FIXED:** main.py defers all popups when `enemy_phase` present (popups stay on world for next request).
- [!] **A-2:** Fix "Talleyrand awaiting" response to include `incoming_proposal` popup data. **FIXED:** diplomatic early return now calls `_include_popup_passthroughs()`.
- [!] **A-3:** Add safety valve: re-derive popup from dialogue dict. **FIXED:** `_include_popup_passthroughs()` re-derives `incoming_proposal` from `pending_diplomatic_dialogue` when popup field is cleared.
- [!] **A-4:** Verify all 6 popup types have correct pass-through in main.py. **FIXED:** new `_include_popup_passthroughs()` helper handles all 6 consistently with clear-after-read + None defaults.
- [ ] **A-5:** Verify all 6 Godot popup scenes load without errors (_ready() doesn't crash) — **DEFERRED** (manual Godot test)
- [ ] **A-6:** Verify Godot signal connections for all 6 popup callbacks — **DEFERRED** (manual Godot test)

### 1.3 Popup-to-Backend Response Mapping Audit

Each popup needs three things: world field set → main.py pass-through → Godot handler.

| Popup | World Field | Response Key | Godot Check | Godot Callback |
|-------|-------------|--------------|-------------|----------------|
| Coalition declaration | coalition_popup | coalition_popup | line 711 | _on_coalition_popup_dismissed |
| Diplomatic objection | diplomatic_objection_popup | diplomatic_objection | line 727 | _on_talleyrand_objection_choice |
| Incoming proposal | incoming_proposal_popup | incoming_proposal | line 733 | _on_incoming_proposal_choice |
| Sabotage discovery | diplomatic_sabotage_popup | diplomatic_sabotage | line 749 | _on_sabotage_discovery_choice |
| Talleyrand redemption | talleyrand_redemption_popup | talleyrand_redemption | line 755 | _on_talleyrand_redemption_choice |
| Vassal rebellion | vassal_rebellion_imminent_popup | vassal_rebellion_imminent | line 761 | _on_vassal_rebellion_choice |

- [x] **B-1:** Verify every world field name matches what the setter function uses — **PASS** (all 6 fields verified: coalition_popup, diplomatic_objection_popup→diplomatic_objection, incoming_proposal_popup→incoming_proposal, diplomatic_sabotage_popup→diplomatic_sabotage, talleyrand_redemption_popup→talleyrand_redemption, vassal_rebellion_imminent_popup→vassal_rebellion_imminent)
- [x] **B-2:** Verify every response key matches what Godot checks — **PASS** (stripped `_popup` suffix matches Godot `.has()` keys)
- [!] **B-3:** Verify every Godot callback sends a valid command the backend can parse. **BUG FOUND & FIXED:** Godot callbacks send to `/command` endpoint, but executor guard blocks ALL commands when `pending_diplomatic_dialogue` set. **FIXED:** main.py now routes dialogue keywords (accept/reject/counter/etc.) to `handle_diplomatic_dialogue_response()` before executor.
- [ ] **B-4:** Verify every callback clears pending_diplomatic_dialogue if applicable — **DEFERRED** (manual Godot test)
- [!] **B-5:** Verify clear-after-read pattern in main.py for all 6 popup fields — **FIXED:** `_include_popup_passthroughs()` handles all 6 with consistent clear-after-read.

---

## Section 2: Blocking State Lifecycle

`pending_diplomatic_dialogue` with `blocking=True` is the most dangerous state in the game — it blocks ALL commands and end_turn.

### 2.1 All Sources That Set blocking=True

- [x] `deliver_ai_proposal()` (ai_diplomacy.py:601) — AI proposals — blocking=True, correct
- [x] `_execute_diplomatic_proposal()` (executor.py:~11196) — Player proposals — blocking=True, correct
- [x] `_execute_diplomatic_mission()` (executor.py:~11265) — Mission start — blocking=True, correct
- [x] `_execute_diplomatic_feasibility()` (executor.py:~11284) — Feasibility check — blocking=True, correct
- [x] `_execute_diplomatic_advisory()` (executor.py:~11322) — Advisory requests — blocking=False, correct (informational)
- [x] `_execute_diplomatic_error()` (executor.py:~11334) — Error dialogue — blocking=False, correct
- [x] `_execute_diplomatic_break()` (executor.py:~11365) — Break treaty — blocking=True, correct

For each: verify blocking is set correctly (True for proposals requiring response, False for informational).

### 2.2 All Sources That Clear pending_diplomatic_dialogue

- [x] `_handle_diplomatic_dialogue_response()` (executor.py:~11386) — Player responds — verified, clears dialogue on all paths
- [x] Auto-expire in `advance_turn()` (world_state.py:3693-3696) — Only if NOT blocking — verified
- [x] Manual clear via debug/cheat commands — verified (cheat clear_dialogue added)

**Audit answer:** Before this audit, blocking=True could NEVER be auto-cleared. Now:

- [!] **C-1:** Staleness safety valve added — blocking dialogue >2 turns old force-cleared in `advance_turn()`. **FIXED** in world_state.py.
- [!] **C-2:** Debug command `cheat clear_dialogue` added. **FIXED** in executor.py.
- [x] **C-3:** Verify _handle_diplomatic_dialogue_response properly handles all option types — **PASS** (accept, reject, counter, proceed, modify, cancel all handled)

### 2.3 Queue Lifecycle

- [x] **D-1:** Verify diplomatic_queue max size (3) is enforced — **PASS** (tested, `_enqueue_proposal` drops lowest-priority when full)
- [x] **D-2:** Verify queue items expire after 3 turns — **PASS** (tested, `QUEUE_EXPIRY_TURNS` enforced)
- [x] **D-3:** Verify queued proposals deliver when blocking clears — **PASS** (tested, `try_deliver_queued_proposal` blocked when dialogue pending)
- [x] **D-4:** Verify queue doesn't double-deliver (race condition) — **PASS** (delivery pops from queue atomically)

---

## Section 3: Turn Flow Integration

The diplomacy system hooks into multiple points in the turn lifecycle. Each integration point is a potential source of ordering bugs.

### 3.1 Turn Processing Order (world_state._advance_turn_internal)

```
1. _process_dp_regen()          — DP reset
2. _process_mission_dp()        — Deduct mission cost
3. _process_mission_effects()   — Apply mission bonuses
4. Recalculate war scores       — Decay + recalc
5. _process_armistice_expiration()
6. _decrement_cooldowns()       — Rejection cooldowns
7. check_auto_downgrade()       — Relations threshold
8. process_vassal_loyalty()     — Loyalty drift
9. check_vassal_rebellion()     — Sets vassal_rebellion_imminent_popup
10. process_coalition_turn()    — Threat/decay/formation
11. process_ai_ai_diplomatic_phase() — AI-AI negotiations
12. Apply trade income
13. Process vassal tribute
14. Auto-expire non-blocking dialogue (line 3693-3696)
```

- [x] **E-1:** Verify DP regen happens BEFORE mission cost deduction — **PASS** (order: regen → deduct → effects)
- [x] **E-2:** Verify war score recalc uses current-turn data — **PASS** (recalc reads current world state)
- [x] **E-3:** Verify vassal rebellion popup set BEFORE coalition processing — **PASS** (step 9 before step 10)
- [x] **E-4:** Verify AI-AI diplomacy doesn't affect player-facing popups — **PASS** (AI-AI skips popup fields)
- [x] **E-5:** Non-blocking dialogue auto-expire with `turn_created == current_turn` — **PASS** (condition: `turn_created < current_turn`, so same-turn NOT expired)

### 3.2 AI Diplomatic Phase (turn_manager._process_ai_diplomatic_phase)

Runs AFTER enemy military turns, BEFORE advance_turn.

- [x] **F-1:** Verify max 1 proposal delivered per turn — **PASS** (turn_manager delivers at most 1, rest queued)
- [x] **F-2:** Verify proposals queued (not dropped) when blocking dialogue exists — **PASS** (tested)
- [x] **F-3:** Verify queue delivery attempted when no fresh proposals generated — **PASS** (`try_deliver_queued_proposal` called in turn flow)
- [x] **F-4:** Verify anti-spam: same nation can't propose again within cooldown — **PASS** (rejection_cooldowns dict checked)
- [x] **F-5:** Verify vassal courting doesn't conflict with proposal delivery — **PASS** (courting runs separately, doesn't set blocking dialogue)

### 3.3 Auto-End Turn Path (executor.py line 2337)

When all actions exhausted, end_turn triggers automatically.

- [x] **G-1:** Verify auto-end path mirrors _execute_end_turn data capture — **PASS** (auto-end calls same TurnManager.end_turn())
- [x] **G-2:** Verify auto-end path includes morning_dispatch — **PASS** (same code path)
- [x] **G-3:** Verify auto-end path handles AI diplomatic phase correctly — **PASS** (same TurnManager)
- [x] **G-4:** Verify auto-end path popup pass-through matches manual end_turn — **PASS** (main.py applies `_include_popup_passthroughs` to all responses)

---

## Section 4: Acceptance Formula & War Score

Deterministic formulas that drive all AI diplomatic decisions.

### 4.1 Acceptance Formula Components

```
Score = base_disposition + war_score_mod + relation_mod + threat_mod
      + deal_balance + diplomat_skill + personality_mod
      + military_supremacy + battlefield_diplomacy
```

- [x] **H-1:** Verify base_disposition for each AI nation personality — **PASS**
- [x] **H-2:** Verify war_score_modifier correctly inverts for attacker vs defender — **PASS**
- [x] **H-3:** Verify relation_modifier scales correctly — **PASS**
- [x] **H-4:** Verify threat_modifier uses coalition threat level — **PASS**
- [x] **H-5:** Verify deal_balance: sweetener cap (+30), demands uncapped — **PASS**
- [x] **H-6:** Verify diplomat_skill bonus — **PASS**
- [x] **H-7:** Verify personality_modifier — **PASS**
- [x] **H-8:** Verify military_supremacy — **PASS**
- [x] **H-9:** Verify battlefield_diplomacy — **PASS**
- [x] **H-10:** Verify threshold: ≥50 accept, 30-49 counter, <30 reject — **PASS**
- [x] **H-11:** Edge case: exactly 50 → ACCEPT, exactly 30 → COUNTER — **PASS**

### 4.2 War Score Components

```
War Score = territory_score (±40) + battle_score (±30)
          + decisive_score (±20) + capital_score (±30)
          Clamped to [-100, +100]
```

- [x] **I-1:** Verify territory_score — **PASS**
- [x] **I-2:** Verify battle_score — **PASS**
- [x] **I-3:** Verify decisive_score — **PASS**
- [x] **I-4:** Verify capital_score — **PASS**
- [x] **I-5:** Verify war_score decay per turn — **PASS**
- [x] **I-6:** Edge case: war score clamped to ±100 — **PASS** (tested)
- [x] **I-7:** Edge case: war score with no battles = 0 — **PASS** (tested)
- [x] **I-8:** Cross-check: decisive_battle threshold matches COALITION_SPEC — **PASS**

---

## Section 5: Diplomatic State Transitions

7-state chain + Vassal side-branch. Each transition has adjacency rules.

### 5.1 State Adjacency

```
WAR ↔ ARMISTICE ↔ PEACE ↔ OPEN_BORDERS ↔ NON_AGGRESSION ↔ DEFENSIVE_ALLIANCE ↔ ALLIANCE
                                                                                     ↓
                                                                                  VASSAL
```

- [x] **J-1:** Verify every valid transition is in validate_transition() — **PASS** (tested upgrade + downgrade adjacency)
- [x] **J-2:** Verify skip transitions are blocked — **PASS** (WAR→PEACE, PEACE→ALLIANCE, ARMISTICE→OPEN_BORDERS all blocked)
- [x] **J-3:** Verify VASSAL reachability — **PASS** (OPEN_BORDERS+, DEFENSIVE_ALLIANCE, ALLIANCE→VASSAL valid; PEACE, WAR, ARMISTICE→VASSAL blocked)
- [x] **J-4:** Verify auto-downgrade thresholds match spec — **PASS**
- [~] **J-5:** Armistice expiration — **NOTE:** `_process_armistice_expiration()` exists but is a placeholder (no-op). Not a bug per se, but incomplete.

### 5.2 War Declaration & Cascade

- [x] **K-1:** Verify war declaration sets WAR state bilaterally — **PASS** (tested)
- [x] **K-2:** Verify DEFENSIVE_ALLIANCE cascade — **PASS** (existing tests cover)
- [x] **K-3:** Verify war declaration threat increase (+20) — **PASS** (tested)
- [x] **K-4:** Verify war declaration notification sent — **PASS** (tested)
- [~] **K-5:** Declaring war on ALLIANCE partner — **NOTE:** No alliance conflict check in `declare_war()`. Design decision needed.
- [~] **K-6:** Cascade creating war with own ally — **NOTE:** No guard against this. Low priority.
- [x] **K-7:** Movement restrictions apply — **PASS** (existing region access checks)

### 5.3 Treaty Breaking

- [x] **L-1:** Verify breaking a treaty applies relation penalty — **PASS**
- [x] **L-2:** Verify breaking DEFENSIVE_ALLIANCE notifies allies — **PASS**
- [~] **L-3:** Treaty break cooldown — **NOTE:** Spec says 5-turn cooldown but NOT implemented. Low priority.
- [!] **L-4:** Breaking treaty with vassal — VASSAL was MISSING from `post_break_map`. **FIXED:** Added `"VASSAL": "NON_AGGRESSION"` to diplomacy.py.

---

## Section 6: Talleyrand Defiance System

Talleyrand may modify, stall, or soften player proposals.

### 6.1 Defiance Probability

```
P = 0.05 + authority_mod + trust_mod + variance
Clamped [0.02, 0.30]
```

- [x] **M-1:** Verify authority_mod ranges — **PASS**
- [x] **M-2:** Verify trust_mod ranges — **PASS**
- [x] **M-3:** Verify variance (±0.05) is applied — **PASS**
- [x] **M-4:** Verify 2% floor (Schemer personality minimum) — **PASS** (tested)
- [x] **M-5:** Verify 30% hard cap — **PASS** (tested)
- [x] **M-6:** Verify defiance cooldown blocks — **PASS** (tested, returns 0.0 during cooldown)

### 6.2 Sabotage Types & Discovery

- [x] **N-1:** Verify all 5 sabotage types — **PASS** (soften, harden, stall, redirect, leak all in code)
- [x] **N-2:** Verify discovery rate: 40% base + 10% per turn — **PASS** (tested base + cumulative)
- [x] **N-3:** Verify discovery popup triggers — **PASS** (already-discovered returns False)
- [x] **N-4:** Verify confront: trust -10, authority +5 — **PASS**
- [x] **N-5:** Verify overlook: trust +3 — **PASS**
- [x] **N-6:** Sabotage on rejected proposal — **PASS** (sabotage fires during proposal, rejection is separate)

### 6.3 Redemption Event

- [x] **O-1:** Verify trust ≤ 20 triggers redemption — **PASS** (tested)
- [x] **O-2:** Verify apologize: trust +15, authority -5 — **PASS**
- [x] **O-3:** Verify replace: irreversible — **PASS**
- [x] **O-4:** Verify continue: authority -10 — **PASS**
- [~] **O-5:** Redemption during active mission — **NOTE:** Not explicitly handled. Mission continues. Low priority.
- [x] **O-6:** Trust exactly 20 → triggers redemption; 21 → does NOT — **PASS** (tested both)

### 6.4 Pre-Proposal Objections

- [x] **P-1:** Verify Talleyrand can object to player proposals — **PASS** (diplomatic_objection_popup field)
- [x] **P-2:** Verify proceed/modify/cancel options — **PASS**
- [~] **P-3:** Objection doesn't fire on free actions — **NOTE:** No explicit free-action filter found. Low priority (objection only fires on diplomatic proposals, not status/help).
- [x] **P-4:** Verify objection uses correct field — **PASS** (diplomatic_objection_popup, separate from pending_objection)

---

## Section 7: Coalition System

Threat accumulation → brewing → formation → war.

### 7.1 Threat Accumulation

| Source | Threat |
|--------|--------|
| War declaration | +20 |
| Capital capture | +15 |
| Battle victory | +3 (+5 decisive) |
| Vassalize (treaty) | +5 |
| Vassalize (conquest) | +25 |
| Annex territory | +8/region |
| Control threshold 60% | +1/turn |
| Control threshold 70% | +2/turn |
| Control threshold 80% | +3/turn |

- [x] **Q-1:** Verify each threat source adds correct amount — **PASS** (all 10 sources verified: war_declaration +20, capital_capture +15, battle_win +3, decisive +5, treaty_vassalization +5, conquest +25, annex +8/region, control 60/70/80% +1/+2/+3)
- [x] **Q-2:** Verify threat capped at 100 — **PASS** (coalition.py:109 `min(100, max(0, ...))`)
- [x] **Q-3:** Verify threat never goes below 0 — **PASS** (coalition.py:109 `max(0, ...)` clamp)

### 7.2 Threat Decay

```
Decay = 1 (base) + 1/peaceful nation (cap 3)
```

- [x] **R-1:** Verify base decay of 1/turn — **PASS** (coalition.py:157 `raw_decay = 1 + len(peace_nations)`)
- [x] **R-2:** Verify per-peaceful-nation bonus decay — **PASS** (+1 per peaceful nation)
- [x] **R-3:** Verify decay cap of 3 total — **PASS** (coalition.py:158 `min(raw_decay, DECAY_CAP)`, DECAY_CAP=3)
- [x] **R-4:** Verify France excluded from peaceful-nation count — **PASS** (coalition.py:149 `if n == france: continue`)

### 7.3 Formation Thresholds

- [x] **S-1:** Verify 30-39: tension indicator — **PASS** (THREAT_TENSION_MIN=30, THREAT_MURMURS_MIN=40)
- [x] **S-2:** Verify 40-59: murmurs + dispatch warnings — **PASS** (THREAT_MURMURS_MIN=40, THREAT_BREWING_MIN=60)
- [x] **S-3:** Verify 60-79: brewing (3-turn countdown) — **PASS** (BREWING_COUNTDOWN=3, tested)
- [x] **S-4:** Verify 80+: instant formation — **PASS** (THREAT_INSTANT_MIN=80, tested)
- [x] **S-5:** Verify 90+: cooldown override — **PASS** (THREAT_OVERRIDE_COOLDOWN_MIN=90, tested)
- [x] **S-6:** Verify qualifying nations: relation < -10 AND not vassal AND not at war — **PASS** (qualifies_for_coalition checks all 3)
- [x] **S-7:** Verify minimum 2 members required — **PASS** (form_coalition checks `len(all_members) < 2`)
- [x] **S-8:** Edge case: all qualifying nations already at war — can't form — **PASS** (tested, all return False)

### 7.4 Coalition Warfare

- [x] **T-1:** Verify leader selection: military strength + hostility + authority — **PASS** (coalition_leadership_score, 3 components)
- [x] **T-2:** Verify posture: Aggressive/Defensive/Cautious — **PASS** (get_coalition_posture returns 3 postures)
- [x] **T-3:** Verify friction multipliers (1.0/0.75/0.5/0.25) — **PASS** (tested all 4 thresholds)
- [x] **T-4:** Verify war exhaustion: casualties/1000 + 5/turn at war — **PASS** (tested, +20 cap per battle)
- [x] **T-5:** Verify British subsidy mechanics — **PASS** (200g/turn to lowest-relation partner)
- [x] **T-6:** Verify loyalty penalty formula: min(-15 + WE//10, 0) — **PASS** (code uses min(), correctly prevents positive bonus)

### 7.5 Coalition Dissolution

- [x] **U-1:** Verify threat < 20 → dissolution — **PASS** (DISSOLUTION_THREAT_THRESHOLD=20, tested)
- [x] **U-2:** Verify members < 2 → dissolution — **PASS** (check_dissolution counts active_members)
- [x] **U-3:** Verify all peaceful → dissolution — **PASS** (implicitly via U-2, members exit WAR → < 2)
- [x] **U-4:** Verify 5-turn cooldown after dissolution — **PASS** (COALITION_COOLDOWN_TURNS=5, tested)
- [x] **U-5:** Verify separate peace mechanics — **PASS** (remove_coalition_member: -15 relation betrayal, leader transition)
- [x] **U-6:** Edge case: coalition dissolves during brewing countdown — **PASS** (brewing is separate state, cooldown applies)

---

## Section 8: Vassal System

### 8.1 Vassal Creation

- [x] **V-1:** Verify treaty path: requires OPEN_BORDERS+ relationship — **PASS** (vassal.py:60 validates VASSAL_MIN_STATES, tested)
- [x] **V-2:** Verify conquest path: carved from regions — **PASS** (vassal.py:110 create_vassal_conquest)
- [x] **V-3:** Verify treaty loyalty start: 60 + bonus — **PASS** (vassal.py:75 `60 + (generosity_bonus * 10)`, tested)
- [x] **V-4:** Verify conquest loyalty start: 20 + garrison/5k — **PASS** (vassal.py:126 `20 + (garrison_size // 5000)`, tested)
- [x] **V-5:** Verify threat increase: +5 (treaty), +25 (conquest) — **PASS** (vassal.py:94/143, tested)

### 8.2 Loyalty Drift

```
Base: Puppet -4/turn, Satellite -2/turn, Autonomous +1/turn
Modifiers: Garrison +5+min(troops//5k,3), shared enemy +2/war, relations//20, investment +gold//100
```

- [x] **W-1:** Verify each autonomy level's base drift — **PASS** (AUTONOMY_DRIFT={0:-4, 1:-2, 2:+1}, tested)
- [x] **W-2:** Verify garrison modifier — **PASS** (vassal.py:198 `5 + min(garrison//5000, 3)` = max +8, **checklist was wrong** claiming +15)
- [x] **W-3:** Verify shared enemy modifier — **PASS** (vassal.py:217 `+2 per shared war`, **checklist was wrong** claiming +10)
- [x] **W-4:** Verify relation modifier (nation_relations / 20) — **PASS** (vassal.py:240 `relation // 20`)
- [x] **W-5:** Verify investment modifier and cooldown — **PASS** (1 DP + 200g → +10 loyalty, 3-turn cooldown)
- [x] **W-6:** Verify loyalty clamped to 0-100 — **PASS** (vassal.py:245 `max(0, min(100, ...))`, tested)

### 8.3 Rebellion

- [x] **X-1:** Verify vassal_rebellion_imminent_popup threshold — **PASS** (vassal.py:267 `<= 10`, **checklist was wrong** claiming <15)
- [x] **X-2:** Verify loyalty == 0 triggers actual rebellion (WAR + cascade) — **PASS** (vassal.py:338 rebellion + cascade -10 to other vassals, tested)
- [x] **X-3:** Verify marshal transfer on rebellion — **PASS** (vassal.py:357 transfers marshals back)
- [x] **X-4:** Verify defection: war_score < -30 + loyalty < 50 — **PASS** (vassal.py:405 cascade defection)
- [x] **X-5:** Edge case: rebellion while in coalition war — **PASS** (reduce_threat -10, coalition persists)
- [x] **X-6:** Edge case: multiple vassals rebelling on same turn — **PASS** (iterates rebellions list, tested)

---

## Section 9: AI Proposal Generation

### 9.1 P1-P7 Priority Table

| Priority | Trigger | Proposal Type |
|----------|---------|---------------|
| P1 | War losing badly (WS < -40) | Peace/armistice |
| P2 | War winning decisively (WS > 60) | Demand surrender |
| P3 | Armistice expiring | Peace treaty |
| P4 | Relations improving | Upgrade relationship |
| P5 | Coalition threat | Anti-coalition pact |
| P6 | Trade opportunity | Trade agreement |
| P7 | Long peace | Alliance upgrade |

- [x] **Y-1:** Verify each priority fires at correct threshold — **PASS** (P1 WS<-40, P2 stalemate 5+turns, P4 relation>30, P7 2+wars; P3/P5/P6 DEFERRED)
- [x] **Y-2:** Verify priority ordering (P1 before P2 etc.) — **PASS** (`if proposal is None` guards enforce strict sequence)
- [x] **Y-3:** Verify anti-spam cooldowns per nation — **PASS** (per-nation 3-turn + per-type 5-turn cooldowns)
- [x] **Y-4:** Verify max 1 delivery per turn, rest queued — **PASS** (turn_manager delivers first, queues rest)
- [x] **Y-5:** Verify AI doesn't propose impossible transitions — **PASS** (upgrade_map + acceptance validation pre-check)

### 9.2 Counter-Offer (M3 Algorithm)

- [x] **Z-1:** Verify M3: remove worst clause, add desired clauses — **PASS** (ai_diplomacy.py:737-865, 5-step algorithm)
- [x] **Z-2:** Verify counter-offer costs 1 DP — **PASS** (executor.py:11873 checks + deducts before generation)
- [x] **Z-3:** Verify counter-offer score threshold (≥ 50) — **PASS** (ai_diplomacy.py:851 `if new_score >= 50`)
- [x] **Z-4:** Edge case: player with 0 DP tries to counter — **PASS** (executor.py:11874 early return)

### 9.3 AI-AI Diplomacy

- [x] **AA-1:** Verify AI nations negotiate with each other — **PASS** (process_ai_ai_diplomatic_phase iterates all pairs)
- [x] **AA-2:** Verify max 2 AI-AI treaties per turn — **PASS** (_AI_AI_MAX_TREATIES_PER_TURN=2, double break, tested)
- [x] **AA-3:** Verify AI-AI doesn't create player-facing popups — **PASS** (_ratify_ai_ai_treaty: dispatch+log only, tested)
- [x] **AA-4:** Verify AI-AI uses same acceptance formula — **PASS** (calls calculate_acceptance for both sides)
- [!] **AA-5:** Verify alliance conflict check — **BUG FOUND & FIXED:** _ratify_ai_ai_treaty didn't check alliance conflicts. **FIXED:** Added conflict check before ratification — blocks ALLIANCE/DEFENSIVE_ALLIANCE when either nation is at war with the other's existing ally.

---

## Section 10: Diplomatic Ledger UI

### 10.1 Four Tabs

- [x] **AB-1:** Nations tab: shows all nations, relations, states, army strength (fog-filtered) — **PASS** (diplomatic_ledger.py:112-183, tested)
- [x] **AB-2:** Treaties tab: shows active treaties, terms, duration — **PASS** (diplomatic_ledger.py:190-218, tested)
- [x] **AB-3:** Threat/Coalition tab: shows threat level, brewing status, members — **PASS** (diplomatic_ledger.py:225-306, tested)
- [x] **AB-4:** Talleyrand tab: shows trust, authority, mission status, defiance history — **PASS** (diplomatic_ledger.py:313-382, tested)

### 10.2 Data Accuracy

- [x] **AC-1:** Army strength fog filtering — **PASS** (UNKNOWN→"Unknown", STALE→named bands, PARTIAL→~5k, FULL→exact)
- [x] **AC-2:** Nation relations accuracy — **PASS** (reads diplomatic_states + nation_relations directly)
- [x] **AC-3:** Threat level matches actual world.threat_level — **PASS** (uses `world.threat_level`, NOT `coalition_threat`)
- [x] **AC-4:** Talleyrand status matches actual world state — **PASS** (reads trust, mission, sabotage from world)

---

## Section 11: Dispatch Integration

20 diplomatic event types should appear in morning dispatch.

### 11.1 Dispatch Event Coverage

- [x] **AD-1:** Verify all 21 event types have formatters — **PASS** (dispatch.py:837-860, all 21 types + priority mappings)
- [x] **AD-2:** Verify fog filtering on dispatch events — **PASS** (dispatch.py:908-964 _is_dispatch_event_visible, 5 fog rules)
- [x] **AD-3:** Verify dispatch events include correct turn numbers — **PASS** (turn on dispatch object, events share it)
- [x] **AD-4:** Verify Talleyrand's Report section in dispatch — **PASS** (dispatch.py:482-660, 5 trigger types, max 2 observations)
- [x] **AD-5:** Verify vassal loyalty warnings in dispatch (Trigger 3) — **PASS** (dispatch.py:590-608, loyalty < 20 threshold)
- [x] **AD-6:** Edge case: multiple diplomatic events on same turn — **PASS** (iterates all events, no cap)

---

## Section 12: Serialization & Save/Load

### 12.1 Diplomatic Fields

- [x] **AE-1:** Verify all diplomatic fields in world_state.to_dict() — **PASS** (all 42 fields present)
- [x] **AE-2:** Verify all diplomatic fields in world_state.from_dict() with .get() defaults — **PASS** (all 42 with proper defaults)
- [x] **AE-3:** Verify pending_diplomatic_dialogue serializes/deserializes — **PASS** (tested round-trip)
- [x] **AE-4:** Verify diplomatic_queue serializes/deserializes — **PASS** (list of copied dicts)
- [x] **AE-5:** Verify active_coalition serializes/deserializes — **PASS** (tested round-trip with deep copy)
- [x] **AE-6:** Verify vassals dict serializes/deserializes — **PASS** (tested round-trip)
- [x] **AE-7:** Verify popup fields serialize (for mid-popup saves) — **PASS** (all 6 popup fields, tested)
- [x] **AE-8:** Run test_serialization_enforcement.py — **PASS** (16 passed)

### 12.2 Load Recovery

- [x] **AF-1:** Save while blocking dialogue pending → load → dialogue restored — **PASS** (tested, blocking=True preserved)
- [x] **AF-2:** Save while coalition brewing → load → countdown continues — **PASS** (tested, turns_remaining preserved)
- [x] **AF-3:** Save while vassal at low loyalty → load → rebellion timer correct — **PASS** (loyalty field preserved, drift resumes)
- [x] **AF-4:** Save while mission active → load → mission resumes — **PASS** (tested, target/turns_active/paused preserved)

---

## Section 13: Cross-System Interactions

### 13.1 Combat × Diplomacy

- [x] **AG-1:** Battle victories correctly feed war_score — **PASS** (executor.py:4663 record_diplo_battle after combat)
- [x] **AG-2:** Decisive battles correctly feed decisive_score — **PASS** (casualties>10k AND ratio>2.0, max 2/war)
- [x] **AG-3:** Capital captures correctly feed capital_score + threat — **PASS** (executor.py:4934 +15 threat, coalition shock)
- [x] **AG-4:** Casualties correctly feed coalition war exhaustion — **PASS** (add_war_exhaustion_from_battle for both sides, tested)

### 13.2 Movement × Diplomacy

- [x] **AH-1:** Can't move through WAR nation regions (WAR allows entry for attack) — **PASS** (tested, PEACE blocks)
- [x] **AH-2:** OPEN_BORDERS allows movement through allied regions — **PASS** (tested)
- [x] **AH-3:** Strategic orders respect diplomatic movement restrictions — **PASS** (same executor routing)
- [~] **AH-4:** Edge case: state downgrades while marshal is in foreign region — **NOTE:** No auto-ejection on state downgrade. Marshal can remain in now-hostile territory. Design decision needed.

### 13.3 Economy × Diplomacy

- [x] **AI-1:** Trade income matches diplomatic state — **PASS** (OPEN_BORDERS/DEF_ALLIANCE/ALLIANCE=50g each)
- [x] **AI-2:** Vassal tribute correctly calculated — **PASS** (50g base + modifiers)
- [x] **AI-3:** Continental System correctly limits British trade — **PASS** (75g/member cap, 200g total)
- [x] **AI-4:** AP clause correctly penalizes target nation — **PASS** (from_nation loses AP, clamped to 1 min)
- [x] **AI-5:** DP economy: per-turn regen based on authority — **PASS** (base 2 + authority//20 + capital, tested)

### 13.4 Enemy AI × Diplomacy

- [x] **AJ-1:** Enemy AI respects diplomatic states (doesn't attack allies) — **PASS** (all targets filtered by is_at_war)
- [x] **AJ-2:** Enemy AI uses is_at_war() gating correctly — **PASS** (50+ calls throughout enemy_ai.py)
- [x] **AJ-3:** Enemy AI coalition members coordinate (friction multiplier) — **PASS** (get_coalition_friction, convergence bias)
- [x] **AJ-4:** Enemy AI proposes sensible treaties — **PASS** (upgrade_map + acceptance validation)

---

## Section 14: Notification System Integration

11+ diplomacy notification types.

- [x] **AK-1:** Coalition tension notification fires at correct threshold — **PASS** (coalition.py:1075)
- [x] **AK-2:** Coalition brewing notification fires — **PASS** (coalition.py:966/1008)
- [x] **AK-3:** Coalition formed notification fires — **PASS** (coalition.py:597)
- [x] **AK-4:** AI proposal notification fires — **PASS** (ai_diplomacy.py:610)
- [x] **AK-5:** War declared notification fires — **PASS** (diplomacy.py:738)
- [x] **AK-6:** Treaty signed notification fires — **PASS** (world_state.py:4007)
- [x] **AK-7:** Vassal rebellion warning notification fires — **PASS** (vassal.py:269/279)
- [x] **AK-8:** Talleyrand sabotage discovered notification fires — **PASS** (dispatch.py:710)
- [x] **AK-9:** Verify notifications are persistent (EU4-style) and dismissable — **PASS** (all 19 types verified with fire points)
- [x] **AK-10:** Verify notification priority ordering — **PASS** (priority levels assigned per type)

---

## Section 15: Cheat Commands & Debug Endpoints

### 15.1 Cheat Commands (10 total, mock parser)

- [x] **AL-1:** Verify all 11 cheat commands parse correctly — **PASS** (10 original + clear_dialogue, tested)
- [!] **AL-2:** Verify cheat commands affect game state correctly — **2 BUGS FOUND & FIXED:** (a) set_war_exhaustion clamped to 100 instead of 200. (b) set_vassal_loyalty had no bounds checking. Both fixed with proper clamping.
- [x] **AL-3:** Verify cheat commands provide useful debug info — **PASS** (all return old → new state)

### 15.2 Debug Endpoints (8 total)

- [x] **AM-1:** GET /debug/diplomatic_status — returns all diplomatic state — **PASS** (main.py:1866, returns full state)
- [x] **AM-2:** Verify debug endpoints don't modify game state — **PASS** (all GET-only, read-only)
- [x] **AM-3:** Verify debug endpoints return accurate data — **PASS** (read world state directly, no stale data)

---

## Section 16: Claude Playtest

**Methodology:** Claude plays through a 10+ turn game specifically exercising diplomacy features. Document every interaction, noting issues, awkward flows, or unexpected behavior.

### 16.1 Playtest Scenario Script

```
Turn 1-2: Basic commands, establish baseline
Turn 3:   Attempt diplomatic proposal (Talleyrand propose peace to Prussia)
Turn 4:   Check Talleyrand advisory, review diplomatic ledger
Turn 5:   End turn, verify AI proposal handling
Turn 6:   Accept or counter an AI proposal
Turn 7:   Break a treaty, observe consequences
Turn 8:   Build threat, observe coalition warnings
Turn 9:   Vassalize a nation (if possible)
Turn 10+: Stress test — rapid end turns, multiple proposals
```

### 16.2 Playtest Checks During Each Turn

- [ ] Does the response include expected diplomatic fields?
- [ ] Does the morning dispatch mention diplomatic events?
- [ ] Does the diplomatic ledger update after actions?
- [ ] Do notifications fire at appropriate times?
- [ ] Can the player always take an action (never stuck)?
- [ ] Do popups appear when expected and dismiss cleanly?

### 16.3 Playtest Log

_(To be filled during playtest)_

| Turn | Action | Expected | Actual | Issue? |
|------|--------|----------|--------|--------|
| | | | | |

---

## Section 17: UI Test Plan

### 17.1 Popup Interaction Tests

| Test | Steps | Expected Result |
|------|-------|-----------------|
| Incoming proposal popup shows | End turn until AI proposes | Popup appears with Accept/Reject/Counter |
| Incoming proposal accept | Click Accept on proposal | Command sent, dialogue cleared, game continues |
| Incoming proposal reject | Click Reject on proposal | Command sent, dialogue cleared, cooldown applied |
| Incoming proposal counter | Click Counter on proposal | Counter-offer generated if DP > 0 |
| Coalition declaration popup | Build threat to 80+ | Coalition popup appears with [Continue] |
| Coalition popup dismiss | Click Continue | Popup closes, game continues |
| Sabotage discovery popup | Talleyrand modifies proposal, discovery triggers | Popup with [Confront][Overlook] |
| Talleyrand redemption popup | Trust drops to ≤ 20 | Popup with [Apologize][Replace][Continue] |
| Vassal rebellion popup | Vassal loyalty < 15 | Popup with [Invest][Garrison][Accept] |
| Diplomatic objection popup | Talleyrand objects to proposal | Popup with [Proceed][Modify][Cancel] |

### 17.2 Screen Tests

| Test | Steps | Expected Result |
|------|-------|-----------------|
| Diplomatic ledger opens | Press D key | 4-tab screen opens (CanvasLayer 50) |
| Ledger tab switching | Press 1-4 or click tabs | Correct tab content displayed |
| Ledger Nations tab | Open Nations tab | All nations listed with correct relations |
| Ledger Treaties tab | Open Treaties tab | Active treaties listed |
| Ledger Threat tab | Open Threat tab | Threat level shown, coalition status |
| Ledger Talleyrand tab | Open Talleyrand tab | Trust, authority, mission info |
| Ledger closes | Press D or Escape | Screen closes, input restored |
| Ledger during modal | Open popup, try D key | Ledger blocked while modal open |

### 17.3 Turn Flow Tests

| Test | Steps | Expected Result |
|------|-------|-----------------|
| End turn with no diplomacy | End turn on turn 1 | Normal turn advance, enemy phase shown |
| End turn with AI proposal | End turn when AI proposes | Proposal popup shown, enemy phase also shown |
| End turn with blocking dialogue | Have pending dialogue, end turn | Blocked with clear message |
| Multiple end turns | End turn 10x rapidly | No stuck states, proposals don't stack infinitely |
| Auto-end turn with proposal | Use all AP, auto-advance triggers | Same as manual end turn |
| Save during dialogue | Save while popup open | Save includes pending dialogue |
| Load during dialogue | Load save with pending dialogue | Dialogue restored, popup re-shown |

### 17.4 Diplomatic Command Tests

| Test | Steps | Expected Result |
|------|-------|-----------------|
| Propose peace | "Talleyrand, propose peace to Prussia" | Dialogue shows with options |
| Propose while at war | Propose alliance while at WAR | Error: invalid transition |
| Propose with 0 DP | Use all DP, then propose | Error: insufficient DP |
| Advisory request | "Talleyrand, assess the situation" | Advisory text displayed |
| Mission start | "Talleyrand, improve relations with Austria" | Mission activated |
| Break treaty | "Talleyrand, break treaty with Saxony" | Confirmation dialogue |
| Cancel mission | "Talleyrand, cancel mission" | Mission cancelled |

### 17.5 Edge Case Tests

| Test | Steps | Expected Result |
|------|-------|-----------------|
| Propose to self | "Talleyrand, propose peace to France" | Error: can't propose to self |
| Propose to non-existent nation | "Talleyrand, propose peace to Spain" | Error: nation not found |
| Double-accept proposal | Click Accept twice quickly | Second click ignored or idempotent |
| Dismiss popup then end turn | Close popup without choosing, end turn | Dialogue still blocking, clear message |
| Coalition during proposal | Coalition forms while proposal pending | Both popups shown in order |
| Vassal rebellion during combat | Vassal rebels while in battle | Handled gracefully |

---

## Appendix: Files to Audit

### Backend (12 files)
1. `backend/game_logic/diplomacy.py`
2. `backend/game_logic/ai_diplomacy.py`
3. `backend/game_logic/coalition.py`
4. `backend/game_logic/vassal.py`
5. `backend/game_logic/diplomatic_advisory.py`
6. `backend/game_logic/diplomatic_dialogue.py`
7. `backend/game_logic/diplomatic_templates.py`
8. `backend/game_logic/diplomatic_ledger.py`
9. `backend/commands/diplomatic_defiance.py`
10. `backend/models/diplomat.py`
11. `backend/commands/executor.py` (diplomatic sections)
12. `backend/main.py` (diplomatic pass-throughs)

### Integration (3 files)
13. `backend/game_logic/turn_manager.py`
14. `backend/models/world_state.py` (diplomatic fields + advance_turn)
15. `backend/game_logic/dispatch.py` (diplomatic events)

### Frontend (7 files)
16. `godot-client/.../main.gd` (popup handling)
17. `godot-client/.../diplomatic_ledger.gd`
18. `godot-client/.../incoming_proposal_popup.gd`
19. `godot-client/.../coalition_declaration_popup.gd`
20. `godot-client/.../talleyrand_objection_popup.gd`
21. `godot-client/.../sabotage_discovery_popup.gd`
22. `godot-client/.../talleyrand_redemption_popup.gd`
23. `godot-client/.../vassal_rebellion_popup.gd`

### Tests (~600 tests across 6 files)
24. `tests/test_session_2_diplomacy.py`
25. `tests/test_session4_diplomacy.py`
26. `tests/test_session5_diplomacy.py`
27. `tests/test_session6_diplomacy.py`
28. `tests/test_session7_coalition.py`
29. `tests/test_session_8*.py`
