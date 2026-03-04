# Diplomacy System Audit Plan

> **Created:** March 4, 2026
> **Status:** IN PROGRESS
> **Scope:** Comprehensive audit of entire Phase 8 diplomacy implementation
> **Goal:** Find and fix edge cases, stuck states, contradictions, and bugs

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

- [ ] **A-1:** Fix priority ordering — incoming_proposal popup must NOT preempt enemy phase
- [ ] **A-2:** Fix "Talleyrand awaiting" response to include `incoming_proposal` popup data (not just `diplomatic_dialogue`)
- [ ] **A-3:** Add safety valve: if pending_diplomatic_dialogue is blocking but incoming_proposal_popup is None, re-derive popup data from the dialogue dict
- [ ] **A-4:** Verify all 6 popup types have correct pass-through in main.py
- [ ] **A-5:** Verify all 6 Godot popup scenes load without errors (_ready() doesn't crash)
- [ ] **A-6:** Verify Godot signal connections for all 6 popup callbacks

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

- [ ] **B-1:** Verify every world field name matches what the setter function uses
- [ ] **B-2:** Verify every response key matches what Godot checks (`.has("key")`)
- [ ] **B-3:** Verify every Godot callback sends a valid command the backend can parse
- [ ] **B-4:** Verify every callback clears pending_diplomatic_dialogue if applicable
- [ ] **B-5:** Verify clear-after-read pattern in main.py for all 6 popup fields

---

## Section 2: Blocking State Lifecycle

`pending_diplomatic_dialogue` with `blocking=True` is the most dangerous state in the game — it blocks ALL commands and end_turn.

### 2.1 All Sources That Set blocking=True

- [ ] `deliver_ai_proposal()` (ai_diplomacy.py:601) — AI proposals
- [ ] `_execute_diplomatic_proposal()` (executor.py:~11196) — Player proposals
- [ ] `_execute_diplomatic_mission()` (executor.py:~11265) — Mission start
- [ ] `_execute_diplomatic_feasibility()` (executor.py:~11284) — Feasibility check
- [ ] `_execute_diplomatic_advisory()` (executor.py:~11322) — Advisory requests
- [ ] `_execute_diplomatic_error()` (executor.py:~11334) — Error dialogue
- [ ] `_execute_diplomatic_break()` (executor.py:~11365) — Break treaty

For each: verify blocking is set correctly (True for proposals requiring response, False for informational).

### 2.2 All Sources That Clear pending_diplomatic_dialogue

- [ ] `_handle_diplomatic_dialogue_response()` (executor.py:~11386) — Player responds
- [ ] Auto-expire in `advance_turn()` (world_state.py:3693-3696) — Only if NOT blocking
- [ ] Manual clear via debug/cheat commands

**Audit question:** If `blocking=True`, can it EVER be auto-cleared? If no, what's the safety valve?

- [ ] **C-1:** Add a staleness safety valve — if blocking dialogue is >2 turns old, force-clear it
- [ ] **C-2:** Add debug command to clear stuck diplomatic dialogue
- [ ] **C-3:** Verify _handle_diplomatic_dialogue_response properly handles all option types (accept, reject, counter, proceed, modify, cancel)

### 2.3 Queue Lifecycle

- [ ] **D-1:** Verify diplomatic_queue max size (3) is enforced
- [ ] **D-2:** Verify queue items expire after 3 turns
- [ ] **D-3:** Verify queued proposals deliver when blocking clears
- [ ] **D-4:** Verify queue doesn't double-deliver (race condition)

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

- [ ] **E-1:** Verify DP regen happens BEFORE mission cost deduction (not after)
- [ ] **E-2:** Verify war score recalc uses current-turn data (not stale)
- [ ] **E-3:** Verify vassal rebellion popup set BEFORE coalition processing (order matters for multiple popups)
- [ ] **E-4:** Verify AI-AI diplomacy doesn't affect player-facing popups
- [ ] **E-5:** Verify non-blocking dialogue auto-expire logic handles edge case: `turn_created == current_turn` (should NOT expire same turn)

### 3.2 AI Diplomatic Phase (turn_manager._process_ai_diplomatic_phase)

Runs AFTER enemy military turns, BEFORE advance_turn.

- [ ] **F-1:** Verify max 1 proposal delivered per turn
- [ ] **F-2:** Verify proposals queued (not dropped) when blocking dialogue exists
- [ ] **F-3:** Verify queue delivery attempted when no fresh proposals generated
- [ ] **F-4:** Verify anti-spam: same nation can't propose again within cooldown
- [ ] **F-5:** Verify vassal courting doesn't conflict with proposal delivery

### 3.3 Auto-End Turn Path (executor.py line 2337)

When all actions exhausted, end_turn triggers automatically.

- [ ] **G-1:** Verify auto-end path mirrors _execute_end_turn data capture (mild_concerns, gold_spent)
- [ ] **G-2:** Verify auto-end path includes morning_dispatch
- [ ] **G-3:** Verify auto-end path handles AI diplomatic phase correctly
- [ ] **G-4:** Verify auto-end path popup pass-through matches manual end_turn

---

## Section 4: Acceptance Formula & War Score

Deterministic formulas that drive all AI diplomatic decisions.

### 4.1 Acceptance Formula Components

```
Score = base_disposition + war_score_mod + relation_mod + threat_mod
      + deal_balance + diplomat_skill + personality_mod
      + military_supremacy + battlefield_diplomacy
```

- [ ] **H-1:** Verify base_disposition for each AI nation personality
- [ ] **H-2:** Verify war_score_modifier correctly inverts for attacker vs defender
- [ ] **H-3:** Verify relation_modifier scales correctly (-100 to +100 → modifier range)
- [ ] **H-4:** Verify threat_modifier uses coalition threat level
- [ ] **H-5:** Verify deal_balance: sweetener cap (+30), demands uncapped
- [ ] **H-6:** Verify diplomat_skill bonus uses Talleyrand's skill vs target diplomat
- [ ] **H-7:** Verify personality_modifier: Schemer +5, Hawk -5, Dove +10
- [ ] **H-8:** Verify military_supremacy: +25 only when war_score ≥ 70 AND capital held
- [ ] **H-9:** Verify battlefield_diplomacy: +10 when war_score > 20
- [ ] **H-10:** Verify threshold: ≥50 accept, 30-49 counter, <30 reject
- [ ] **H-11:** Edge case: what happens at exactly 50? Exactly 30?

### 4.2 War Score Components

```
War Score = territory_score (±40) + battle_score (±30)
          + decisive_score (±20) + capital_score (±30)
          Clamped to [-100, +100]
```

- [ ] **I-1:** Verify territory_score: regions held vs starting
- [ ] **I-2:** Verify battle_score: weighted by casualty ratio
- [ ] **I-3:** Verify decisive_score: decisive battle threshold
- [ ] **I-4:** Verify capital_score: +30 if holding enemy capital, -30 if yours held
- [ ] **I-5:** Verify war_score decay per turn
- [ ] **I-6:** Edge case: war score at ±100 clamping
- [ ] **I-7:** Edge case: war score with no battles fought
- [ ] **I-8:** Cross-check: does decisive_battle threshold match COALITION_SPEC value?

---

## Section 5: Diplomatic State Transitions

7-state chain + Vassal side-branch. Each transition has adjacency rules.

### 5.1 State Adjacency

```
WAR ↔ ARMISTICE ↔ PEACE ↔ OPEN_BORDERS ↔ NON_AGGRESSION ↔ DEFENSIVE_ALLIANCE ↔ ALLIANCE
                                                                                     ↓
                                                                                  VASSAL
```

- [ ] **J-1:** Verify every valid transition (upgrade + downgrade) is in validate_transition()
- [ ] **J-2:** Verify skip transitions are blocked (e.g., WAR → PEACE directly)
- [ ] **J-3:** Verify VASSAL can only be reached from ALLIANCE or via conquest
- [ ] **J-4:** Verify auto-downgrade thresholds match spec
- [ ] **J-5:** Verify armistice duration (5 turns?) and auto-transition to PEACE

### 5.2 War Declaration & Cascade

- [ ] **K-1:** Verify war declaration sets WAR state bilaterally
- [ ] **K-2:** Verify DEFENSIVE_ALLIANCE cascade: all allies of target join the war
- [ ] **K-3:** Verify war declaration threat increase (+20)
- [ ] **K-4:** Verify war declaration notification sent
- [ ] **K-5:** Edge case: declaring war on a nation you have ALLIANCE with
- [ ] **K-6:** Edge case: cascade creating war with your own ally
- [ ] **K-7:** Verify movement restrictions immediately apply (can't enter WAR nation regions freely)

### 5.3 Treaty Breaking

- [ ] **L-1:** Verify breaking a treaty applies relation penalty
- [ ] **L-2:** Verify breaking DEFENSIVE_ALLIANCE notifies allies
- [ ] **L-3:** Verify breaking treaty has appropriate cooldown
- [ ] **L-4:** Edge case: breaking treaty with vassal (should trigger rebellion?)

---

## Section 6: Talleyrand Defiance System

Talleyrand may modify, stall, or soften player proposals.

### 6.1 Defiance Probability

```
P = 0.05 + authority_mod + trust_mod + variance
Clamped [0.02, 0.30]
```

- [ ] **M-1:** Verify authority_mod ranges (-0.05 to +0.15)
- [ ] **M-2:** Verify trust_mod ranges (-0.05 to +0.10)
- [ ] **M-3:** Verify variance (±0.05) is applied
- [ ] **M-4:** Verify 2% floor (Schemer personality minimum)
- [ ] **M-5:** Verify 30% hard cap
- [ ] **M-6:** Verify defiance cooldown (5 turns after confrontation)

### 6.2 Sabotage Types & Discovery

- [ ] **N-1:** Verify all 5 sabotage types (soften, harden, stall, redirect, leak)
- [ ] **N-2:** Verify discovery rate: 40% base + 10% per turn cumulative
- [ ] **N-3:** Verify discovery popup (sabotage_discovery_popup) triggers correctly
- [ ] **N-4:** Verify confront: trust -10, authority +5
- [ ] **N-5:** Verify overlook: trust +3
- [ ] **N-6:** Edge case: sabotage on a proposal that gets rejected anyway

### 6.3 Redemption Event

- [ ] **O-1:** Verify trust ≤ 20 triggers redemption popup
- [ ] **O-2:** Verify apologize: trust +15, authority -5
- [ ] **O-3:** Verify replace: irreversible, skill → 6, defiance floor → 0%
- [ ] **O-4:** Verify continue: authority -10
- [ ] **O-5:** Edge case: redemption during active mission (what happens to mission?)
- [ ] **O-6:** Edge case: trust exactly 20 vs below 20

### 6.4 Pre-Proposal Objections

- [ ] **P-1:** Verify Talleyrand can object to player proposals (diplomatic_objection_popup)
- [ ] **P-2:** Verify proceed/modify/cancel options work correctly
- [ ] **P-3:** Verify objection doesn't fire on free actions (status, help)
- [ ] **P-4:** Verify objection uses correct field (diplomatic_objection_popup, not pending_objection)

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

- [ ] **Q-1:** Verify each threat source adds correct amount
- [ ] **Q-2:** Verify threat capped at 100
- [ ] **Q-3:** Verify threat never goes below 0

### 7.2 Threat Decay

```
Decay = 1 (base) + 1/peaceful nation (cap 3)
```

- [ ] **R-1:** Verify base decay of 1/turn
- [ ] **R-2:** Verify per-peaceful-nation bonus decay
- [ ] **R-3:** Verify decay cap of 3 total
- [ ] **R-4:** Verify France excluded from peaceful-nation count (Coalition Spec audit finding)

### 7.3 Formation Thresholds

- [ ] **S-1:** Verify 30-39: tension indicator
- [ ] **S-2:** Verify 40-59: murmurs + dispatch warnings
- [ ] **S-3:** Verify 60-79: brewing (3-turn countdown)
- [ ] **S-4:** Verify 80+: instant formation
- [ ] **S-5:** Verify 90+: cooldown override
- [ ] **S-6:** Verify qualifying nations: relation < -10 AND not vassal AND not at war (with France)
- [ ] **S-7:** Verify minimum 2 members required
- [ ] **S-8:** Edge case: all qualifying nations already at war — can't form

### 7.4 Coalition Warfare

- [ ] **T-1:** Verify leader selection: military strength + hostility + authority
- [ ] **T-2:** Verify posture: Aggressive/Defensive/Cautious
- [ ] **T-3:** Verify friction multipliers (1.0/0.75/0.5/0.25)
- [ ] **T-4:** Verify war exhaustion: casualties/1000 + 5/turn at war
- [ ] **T-5:** Verify British subsidy mechanics
- [ ] **T-6:** Verify loyalty penalty formula: max(-15 + WE/10, 0)

### 7.5 Coalition Dissolution

- [ ] **U-1:** Verify threat < 20 → dissolution
- [ ] **U-2:** Verify members < 2 → dissolution
- [ ] **U-3:** Verify all peaceful → dissolution
- [ ] **U-4:** Verify 5-turn cooldown after dissolution
- [ ] **U-5:** Verify separate peace mechanics
- [ ] **U-6:** Edge case: coalition dissolves during brewing countdown

---

## Section 8: Vassal System

### 8.1 Vassal Creation

- [ ] **V-1:** Verify treaty path: requires OPEN_BORDERS+ relationship
- [ ] **V-2:** Verify conquest path: carved from regions
- [ ] **V-3:** Verify treaty loyalty start: 60 + bonus
- [ ] **V-4:** Verify conquest loyalty start: 20 + garrison/5k
- [ ] **V-5:** Verify threat increase: +5 (treaty), +25 (conquest)

### 8.2 Loyalty Drift

```
Base: Puppet -4/turn, Satellite -2/turn, Autonomous +1/turn
Modifiers: Garrison +15, shared enemy +10, relations +5, investment +10/turn
```

- [ ] **W-1:** Verify each autonomy level's base drift
- [ ] **W-2:** Verify garrison modifier
- [ ] **W-3:** Verify shared enemy modifier
- [ ] **W-4:** Verify relation modifier (nation_relations / 20)
- [ ] **W-5:** Verify investment modifier and cooldown
- [ ] **W-6:** Verify loyalty clamped to 0-100

### 8.3 Rebellion

- [ ] **X-1:** Verify loyalty < 15 triggers vassal_rebellion_imminent_popup
- [ ] **X-2:** Verify loyalty == 0 triggers actual rebellion (WAR + cascade)
- [ ] **X-3:** Verify marshal transfer on rebellion
- [ ] **X-4:** Verify defection: war_score < -30 + loyalty < 50
- [ ] **X-5:** Edge case: rebellion while in coalition war
- [ ] **X-6:** Edge case: multiple vassals rebelling on same turn

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

- [ ] **Y-1:** Verify each priority fires at correct threshold
- [ ] **Y-2:** Verify priority ordering (P1 before P2 etc.)
- [ ] **Y-3:** Verify anti-spam cooldowns per nation
- [ ] **Y-4:** Verify max 1 delivery per turn, rest queued
- [ ] **Y-5:** Verify AI doesn't propose impossible transitions (e.g., WAR → ALLIANCE)

### 9.2 Counter-Offer (M3 Algorithm)

- [ ] **Z-1:** Verify M3: remove worst clause, add desired clauses
- [ ] **Z-2:** Verify counter-offer costs 1 DP
- [ ] **Z-3:** Verify counter-offer score threshold (≥ 50)
- [ ] **Z-4:** Edge case: player with 0 DP tries to counter

### 9.3 AI-AI Diplomacy

- [ ] **AA-1:** Verify AI nations negotiate with each other
- [ ] **AA-2:** Verify max 2 AI-AI treaties per turn
- [ ] **AA-3:** Verify AI-AI doesn't create player-facing popups
- [ ] **AA-4:** Verify AI-AI uses same acceptance formula
- [ ] **AA-5:** Verify alliance conflict check (can't ally with nation at war with existing ally)

---

## Section 10: Diplomatic Ledger UI

### 10.1 Four Tabs

- [ ] **AB-1:** Nations tab: shows all nations, relations, states, army strength (fog-filtered)
- [ ] **AB-2:** Treaties tab: shows active treaties, terms, duration
- [ ] **AB-3:** Threat/Coalition tab: shows threat level, brewing status, members
- [ ] **AB-4:** Talleyrand tab: shows trust, authority, mission status, defiance history

### 10.2 Data Accuracy

- [ ] **AC-1:** Army strength fog filtering: only show what player has intel on
- [ ] **AC-2:** Nation relations accuracy: matches actual diplomatic_states
- [ ] **AC-3:** Threat level matches actual world.coalition_threat
- [ ] **AC-4:** Talleyrand status matches actual world.talleyrand_state

---

## Section 11: Dispatch Integration

20 diplomatic event types should appear in morning dispatch.

### 11.1 Dispatch Event Coverage

- [ ] **AD-1:** Verify all 20 event types have formatters
- [ ] **AD-2:** Verify fog filtering on dispatch events (don't reveal fogged information)
- [ ] **AD-3:** Verify dispatch events include correct turn numbers
- [ ] **AD-4:** Verify Talleyrand's Report section in dispatch
- [ ] **AD-5:** Verify vassal loyalty warnings in dispatch (Trigger 3)
- [ ] **AD-6:** Edge case: multiple diplomatic events on same turn

---

## Section 12: Serialization & Save/Load

### 12.1 Diplomatic Fields

- [ ] **AE-1:** Verify all diplomatic fields in world_state.to_dict()
- [ ] **AE-2:** Verify all diplomatic fields in world_state.from_dict() with .get() defaults
- [ ] **AE-3:** Verify pending_diplomatic_dialogue serializes/deserializes
- [ ] **AE-4:** Verify diplomatic_queue serializes/deserializes
- [ ] **AE-5:** Verify active_coalition serializes/deserializes
- [ ] **AE-6:** Verify vassals dict serializes/deserializes
- [ ] **AE-7:** Verify popup fields serialize (for mid-popup saves)
- [ ] **AE-8:** Run test_serialization_enforcement.py — verify all pass

### 12.2 Load Recovery

- [ ] **AF-1:** Save while blocking dialogue pending → load → dialogue restored?
- [ ] **AF-2:** Save while coalition brewing → load → countdown continues?
- [ ] **AF-3:** Save while vassal at low loyalty → load → rebellion timer correct?
- [ ] **AF-4:** Save while mission active → load → mission resumes?

---

## Section 13: Cross-System Interactions

### 13.1 Combat × Diplomacy

- [ ] **AG-1:** Battle victories correctly feed war_score
- [ ] **AG-2:** Decisive battles correctly feed decisive_score
- [ ] **AG-3:** Capital captures correctly feed capital_score + threat
- [ ] **AG-4:** Casualties correctly feed coalition war exhaustion

### 13.2 Movement × Diplomacy

- [ ] **AH-1:** Can't move through WAR nation regions (unless bypassed)
- [ ] **AH-2:** OPEN_BORDERS allows movement through allied regions
- [ ] **AH-3:** Strategic orders respect diplomatic movement restrictions
- [ ] **AH-4:** Edge case: state downgrades while marshal is in foreign region

### 13.3 Economy × Diplomacy

- [ ] **AI-1:** Trade income matches diplomatic state
- [ ] **AI-2:** Vassal tribute correctly calculated
- [ ] **AI-3:** Continental System correctly limits British trade
- [ ] **AI-4:** AP clause correctly penalizes target nation
- [ ] **AI-5:** DP economy: per-turn regen based on authority

### 13.4 Enemy AI × Diplomacy

- [ ] **AJ-1:** Enemy AI respects diplomatic states (doesn't attack allies)
- [ ] **AJ-2:** Enemy AI uses is_at_war() gating correctly
- [ ] **AJ-3:** Enemy AI coalition members coordinate (friction multiplier)
- [ ] **AJ-4:** Enemy AI proposes sensible treaties (not impossible transitions)

---

## Section 14: Notification System Integration

11+ diplomacy notification types.

- [ ] **AK-1:** Coalition tension notification fires at correct threshold
- [ ] **AK-2:** Coalition brewing notification fires
- [ ] **AK-3:** Coalition formed notification fires
- [ ] **AK-4:** AI proposal notification fires
- [ ] **AK-5:** War declared notification fires
- [ ] **AK-6:** Treaty signed notification fires
- [ ] **AK-7:** Vassal rebellion warning notification fires
- [ ] **AK-8:** Talleyrand sabotage discovered notification fires
- [ ] **AK-9:** Verify notifications are persistent (EU4-style) and dismissable
- [ ] **AK-10:** Verify notification priority ordering

---

## Section 15: Cheat Commands & Debug Endpoints

### 15.1 Cheat Commands (10 total, mock parser)

- [ ] **AL-1:** Verify all 10 cheat commands parse correctly
- [ ] **AL-2:** Verify cheat commands don't affect game state incorrectly
- [ ] **AL-3:** Verify cheat commands provide useful debug info

### 15.2 Debug Endpoints (8 total)

- [ ] **AM-1:** GET /debug/diplomatic_status — returns all diplomatic state
- [ ] **AM-2:** Verify debug endpoints don't modify game state
- [ ] **AM-3:** Verify debug endpoints return accurate data

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
