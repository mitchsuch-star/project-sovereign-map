# Diplomacy Refinement & Cleanup

> **Created:** March 4, 2026
> **Status:** R1-R114: Phases 1-4 COMPLETE. R115-R140: Phase 5 IN PROGRESS (design gates passed March 8, 2026).
> **Source:** Creative audit (7.8/10) + code audit (March 5) + deep audit II (6-agent) + comprehensive creative audit (6-agent, 6.5/10, March 7)
> **Process:** Phases 1-4 DONE -> Phase 5 Design Depth IN PROGRESS -> UI test -> release

---

## Implementation Plan

7 phases of bug fixes, cleanup, balance, QoL, and design depth. Phase 2 split into 2A (diplomacy core) and 2B (vassal + AI-AI + war transitions). Phases 1-4 COMPLETE. Phase 5 adds design depth from comprehensive creative audit (March 7, 2026).

**165 total items.** 67 DONE (Phases 1-4 + R137/R120 + Wave 2.5), 38 APPROVED (Phase 5), R136 KILLED.

| Phase | Focus | Items | Scope |
|-------|-------|-------|-------|
| **Phase 1** | Critical wiring | R37/R41, R42, R40, R43, R2, R55, R61-R66, R74, R75, R96, R109 | ~16 fixes |
| **Phase 2A** | State cleanup — diplomacy core | R1a/b, R3, R5a/b, R44, R45, R47/R30, R48, R49, R51, R52/R64, R53, R54, R56, R57, R7, R67, R80, R82, R83 | ~19 fixes |
| **Phase 2B** | State cleanup — vassal, AI-AI, war | R46, R50, R60, R68-R73, R81, R97-R102, R105, R107-R108, R110-R111, R113-R114 | ~23 fixes |
| **Phase 3** | Balance tuning | R4a/b, R6, R8, R9, R11, R14-R16, R18, R20, R104, R106 | 13 changes, 44 tests |
| **Phase 4** | Commands, QoL, Popup architecture | R10, R21, R23, R29, R31, R34, R38, R17a-c, R12, R76-R79, R84, R87-R95, R103, R112 | ~27 fixes |
| **Phase 5** | Design depth (5 waves) | R115-R150 (R136 killed) | 50 items |
| **UI Test** | Manual playtest in Godot | R39, R85, R86, verify all fixes | Godot session |

---

## How This Works

1. Items marked **APPROVED** have passed the design gate and are ready to code
2. Items marked **DONE** were implemented during audit/refinement sessions
3. `[NEW]` = Found in March 5 code audit. `[DA2]` = Found in Deep Audit II (6-agent)
4. All 16 previously deferred items PROMOTED to Phase 5 (March 7, 2026)

---

# PHASES 1-4: COMPLETE (55 items, 326 tests)

> Collapsed for readability. For detailed problem/fix descriptions, see git history (March 4-7, 2026).

## Pre-Phase Fixes (Done During Initial Audit)

| # | Summary |
|---|---------|
| GAP-3 | Player break treaty command wired (keywords, 1 DP cost) |
| GAP-5 | Player voluntary downgrade command wired (keywords, 1 DP cost) |
| GAP-6 | AI-AI diplomatic states shown in ledger (fog-filtered) |

## Phase 1: Critical Wiring (16 fixes, 37 tests) — Mar 5

| # | Summary |
|---|---------|
| R37/R41 | Sabotage/redemption popups wired + executor handlers |
| R42 | Pre-proposal objection override actions wired |
| R40 | Coalition loyalty penalty formula fixed (min→max) |
| R43 | AI-AI proposal per-pair cooldown (5 turns) |
| R2 | Counter-offer 30-49 score → generate_counter_offer |
| R55 | Dialogue guard keyword list completed |
| R61 | original_nation serialized on Marshal |
| R62 | Rebellion clears original_nation + resets trust |
| R63 | break_treaty() adds +15/+25 threat |
| R64 | Continental System wired into turn loop |
| R65 | Advisory fog-filters enemy strength |
| R66 | Dispatch fog rule key fixed (target_nation→target) |
| R74 | Vassal rebellion popup sets pending_diplomatic_dialogue |
| R75 | Vassal rebellion choices routing fixed |
| R96 | VASSAL added to OPEN_MOVEMENT_STATES |
| R109 | defensive_alliance type preserved (not overwritten to alliance) |

## Phase 2A: Diplomacy Core (19 fixes, 69 tests) — Mar 6

New serialized fields: `nation_dp`, `armistice_turns`.

| # | Summary |
|---|---------|
| R1a | War score decay — prune battle records > 10 turns |
| R1b | Battle records cleared on peace |
| R3 | Treaty gold/turn clauses enforced in advance_turn |
| R5a | Armistice expiration after 5 turns |
| R5b | Armistice cooldowns set and decremented |
| R44 | AI nation DP stored in world.nation_dp |
| R45 | Downgrade removes old treaty from active_treaties |
| R47/R30 | Strategic orders cancelled on peace |
| R48 | Vassal auto-armistice with lord's allies on creation |
| R49 | War exhaustion reset on peace |
| R51 | Pending dialogue voided on coalition formation |
| R53 | Sweetener minimum 5 gold (was rounding to 0) |
| R54 | War score sign convention helper (single source) |
| R56 | modify_nation_relation self-guard added |
| R57 | Threat field dialogue context key fixed |
| R7 | Defensive alliance BASE_DISPOSITION entry (25) |
| R67 | Shallow copy → deepcopy for coalition serialization |
| R80 | Auto-downgrade dispatch event + notification |
| R82 | {rejection_reaction} template slot resolved |
| R83 | Coalition events dispatch calls added |

## Phase 2B: Vassal/AI-AI/War (22 fixes, 50 tests) + Confidence Fixes (5 fixes, 26 tests) — Mar 6

| # | Summary |
|---|---------|
| R46 | Vassal rebellion cleans active_treaties |
| R50 | CS membership cleaned on vassal release |
| R52/R64 | Duplicate CS deleted, wired into turn loop |
| R60 | Double-vassalization guard |
| R68 | Vassalizing coalition member → remove from coalition |
| R69 | cascade_triggered cleared on peace |
| R70 | Autonomy → AUTONOMOUS removes from CS |
| R71 | Hardcoded nation lists → world state |
| R72 | Vassal commands added to free_actions |
| R73 | /respond_to_diplomatic_dialogue popup pass-throughs |
| R81 | Ghost nation eliminated from diplomacy processing (+coalition cleanup) |
| R97 | declare_war/cascade cleans active_treaties |
| R98 | 4 unwired functions wired + jump transition DP costs |
| R99 | declare_war checks armistice cooldowns |
| R100 | War cascade applies -20 relation penalty |
| R101 | break_treaty validates breaker is party |
| R102 | Stale war_scores entries removed on peace |
| R105 | Mission hardcoded "France" → world.player_nation |
| R107 | AI-AI transition validation + unified ratification |
| R108 | AI-AI ratification creates active_treaties entry |
| R110 | Stalemate counter reset on war end |
| R111 | AI-AI "armistice" added to state_map |
| R113 | Counter-offer gold validated against treasury |
| R114 | Alliance conflict checks both directions |

## Phase 3: Balance (13 items, 44 tests)

| # | Summary |
|---|---------|
| R4a | Relation decay -1/turn toward 0 (skip WAR/ARMISTICE/vassal) |
| R4b | COURT_NATION base 8→5 |
| R6 | Trade income diminishing returns [1.0, 0.75, 0.50, 0.25] |
| R8 | Military pressure component in acceptance (+15 max) |
| R9 | Small battle (<1k casualties) excluded from war score |
| R11 | Coalition WE +8/turn (was +5), friction -2/turn |
| R14 | Vassal release 5-turn re-vassalize cooldown |
| R15 | AI-AI rivalry (-3 rel/turn adjacency, opportunistic downgrade) |
| R16 | +2 threat per non-starting French region |
| R18 | Continental System DP cost explicit (1) |
| R20 | Minor nation skill penalty capped at -8 |
| R104 | Sweetener value 0 explicit None check |
| R106 | P3 AI trigger wired (threat > 60 → seek alliance) |

## Phase 4: Commands/QoL/Popups (27 items, 100 tests)

| # | Summary |
|---|---------|
| R10 | War declaration command via Talleyrand (1 DP) |
| R21 | Ultimatums / coercive diplomacy (2 DP, casus belli on rejection) |
| R23 | Marshal trust reactions to diplomatic events (personality-based) |
| R29 | Diplomatic history in ledger (max 20 entries) |
| R31 | Acceptance score preview with component breakdown |
| R34 | AI diplomatic memory / reliability tracking |
| R38 | War score conditional display in templates |
| R17a-c | Ledger: war score components, cooldowns, treaty costs |
| R12 | Alliance paradox popup (honor/break choice) |
| R76 | Popup priority queue (multi-popup fix) |
| R77 | Coalition popup state display update |
| R78 | Popup early returns include top bar update |
| R79 | Sabotage popup preserves morning dispatch |
| R84 | Threat notifications dismissed on form/dissolve |
| R87 | 6 non-diplomatic early returns include popup pass-throughs |
| R88 | /respond_to_objection popup pass-throughs |
| R89 | Counter-offer DP failure re-sends dialogue |
| R90 | Mission against eliminated nation auto-cancels |
| R91 | Dispatch Trigger 1 proposes correct upgrade tier |
| R92 | Mission completion dispatch event |
| R93 | KNOWN_NATIONS includes carved vassals |
| R94 | int(null) guard in diplomatic ledger |
| R95 | _on_critical_pulse implemented or removed |
| R103 | Feedback includes coalition_penalty + harshness_bonus |
| R112 | Proposal popup hints use correct key ("components") |

## UI Test Phase (Deferred to Godot Session)

| # | Summary |
|---|---------|
| R39 | DP display investigation |
| R85 | Coalition leader periodic re-evaluation |
| R86 | relationship_with_lord dead code removal |

---

## Key Audit Patterns (Reference)

**State cleanup on transitions** was the #1 failure mode (10+ bugs across R45/R46/R47/R49/R50/R62/R68/R69/R70/R80). Every transition path (peace, war, rebellion, vassalization, autonomy change, coalition dissolution) had at least one field not cleaned up.

**Popup early-return cascade** was a systemic Godot issue (R76-R79, R87-R88). Popups return early, dropping other data. Fixed via popup queue + deferred processing.

**Vassal system** was the most under-wired subsystem (11 findings). Never received a proper wiring audit before Deep Audit II.

**Continental System** was entirely dead — never called from turn loop. Fixed in R64.

**Fog of war** had 2 confirmed leak points (R65 advisory, R66 dispatch key mismatch).

---

## FORMERLY DEFERRED — ALL PROMOTED TO PHASE 5

All 16 previously deferred items have been promoted to Phase 5 (Design Depth) following the comprehensive creative audit (March 7, 2026). See Phase 5 section below for full designs. R39 (DP Display Investigation) remains in UI Test phase.

---

# PHASE 5: DESIGN DEPTH

> **Source:** 6-agent comprehensive creative audit (March 7, 2026). Scored 6.5/10.
> **Decisions:** Design gates passed March 8, 2026.
> **Process:** Wave 1 (quick wins) -> Wave 2 (AI intelligence) -> Wave 2.5 (wartime peace) -> Wave 3 (player feedback) -> Wave 4 (decide gate features)

**Item count:** 50 live items (R136 KILLED). 10 Wave 1, 5 Wave 2, 10 Wave 2.5, 8 Wave 3, 17 Wave 4 (decide gate).

---

## WAVE 1: QUICK WINS (10 items)

Bugs, balance tweaks, and small content additions. No design ambiguity. Each < 30 min.

### R134: DEBUG_MODE Security Fix — BUG
`main.py:27` — `DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"` (was hardcoded True).

### R121: P2 Stalemate Trigger Fix — BUG (**SUPERSEDED by R149**)
`ai_diplomacy.py:517` — Add `and war_score <= 0` so winning AI doesn't propose stalemate armistice. **Superseded by R149 (Wave 2.5): threshold raised to `war_score <= 10`.**

### R137: "ally with" Parser Fix — BUG ✅ DONE
`llm_client.py` — Added "ally with/against", "become allies", "form alliance", plus 60+ additional diplomatic keywords for proposals, missions, war declarations, break treaties, ultimatums, and diplomat name alternatives. 85 tests in `test_diplo_parsing_expansion.py`.

### R120: Diplomatic Help Text — CONTENT ✅ DONE
`executor.py (_execute_help)` — DIPLOMACY section present with propose/assess/improve/declare war/break treaty/ultimatum commands + DP costs.

### R140: Relation Cap in Acceptance Formula — BALANCE
`diplomacy.py:556` — `relation_mod = max(-30, min(30, relation / 2))` (was ±50 uncapped).

### R139: AI DP Cap Raised — BALANCE
`diplomacy.py (calculate_dp)` — AI base DP 3, +1 for diplomat skill >= 8 (max 4). Was skill >= 10 for +1.

### R138: Counter-Offer Costs 1 DP for AI — BALANCE
`ai_diplomacy.py (generate_counter_offer)` — Deduct 1 DP from AI before generating counter. 0 DP → return None (reject).

### R135: Garrison Loyalty Cap at +4 — BALANCE
`vassal.py:239` — `garrison_bonus = min(4, 2 + min(garrison_troops // 5000, 3))`. Range +2 to +4.

### R58: Vindication Tracker Decay — FIX
`vindication.py` — `apply_decay(current_turn)`: -1 per 5 turns toward 0. New `last_change_turn` dict. Called from `advance_turn()`.

### R130: Confidence Levels in Advisory — CONTENT
`diplomatic_advisory.py` — Confidence based on fog visibility of target regions. Preamble text: high/medium/low.

---

## WAVE 2: AI INTELLIGENCE (5 items)

### R122: Coalition Posture Drives Enemy AI — DONE
`enemy_ai.py` — Coalition defensive/cautious posture enables fortify for any personality (P5 + _check_threats). Coalition aggressive posture enables drill for any personality (P6). 7 tests.

### R115: Personality-Driven AI Proposals — DONE
`ai_diplomacy.py` — PERSONALITY_PROPOSAL_MODIFIERS table: hawk (+50% gold demand, peace threshold -20), schemer (+2 patience), dove (-25% demand, threshold +20), loyalist (default). gold_mult param on _build_proposal_terms. 9 tests.

### R116: Aggressive Dominance P8 — DONE
`ai_diplomacy.py` — P8 trigger: war_score > 40 → harsh_peace with scaled gold (min 500, war_score*8). war_score > 60 → AP reduction clause. 6 tests.

### R125: Counter-Offer Personality Thresholds — DONE
`ai_diplomacy.py (generate_counter_offer)` — PERSONALITY_COUNTER_THRESHOLDS table: Hawk accept 60/floor 35, Dove accept 40/floor 25, Schemer/Loyalist 50/30. _try_add_desired_clauses uses accept_threshold. 7 tests.

### R126: Urgent Re-Proposal on Situation Change — DONE
`ai_diplomacy.py (_is_on_cooldown)` — Bypass nation cooldown when war_score drops 20+ since last proposal. Track `ai_proposal_metadata` on WorldState (serialized). 7 tests.

---

## WAVE 2.5: WARTIME PEACE REBALANCE (10 items, 27 tests) — DONE

Acceptance formula and AI proposal rebalance for wartime peace negotiations. Prevents mathematically impossible peace during prolonged wars.

### R141: Dampen Relation Weight During WAR — DONE
`diplomacy.py (_calculate_acceptance)` — During WAR: `max(-10, min(10, relation / 4))` instead of peacetime `max(-30, min(30, relation / 2))`. Prevents deep hatred from blocking all peace.

### R142: War Weariness Modifier — DONE
`diplomacy.py (_calculate_acceptance)` — `+2/turn at war, cap +20`. New `war_start_turns` dict on WorldState (diplo_key → turn war began). Cleared by `cleanup_war_end()`.

### R143: Stalemate Duration Modifier — DONE
`diplomacy.py (_calculate_acceptance)` — `+1/stalemate turn, cap +15`. Uses `ai_stalemate_counters`. Rewards patience in prolonged conflicts.

### R144: Territory Sweetener Value 5 to 8 — DONE
`diplomacy.py` — Territory cession sweetener raised from +5 to +8 per region. Makes territorial concessions more impactful.

### R145: Gold Lump Rate Doubled (1/200 to 1/100) — DONE
`diplomacy.py` — Gold lump sum sweetener rate doubled from +1 per 200 gold to +1 per 100 gold.

### R146: Sweetener Cap 30 to 40 — DONE
`diplomacy.py` — Sweetener cap raised from +30 to +40. Allows richer concession packages.

### R147: Territory Cession in generate_suggested_terms() — DONE
`diplomacy.py (generate_suggested_terms)` — AI considers territory cession when generating peace terms.

### R148: AP and Manpower Sweeteners in generate_suggested_terms() — DONE
`diplomacy.py (generate_suggested_terms)` — AI considers AP/turn and manpower sweeteners when building proposals.

### R149: P2 Stalemate Trigger war_score <= 10 (supersedes R121) — DONE
`ai_diplomacy.py` — P2 stalemate trigger raised from `war_score <= 0` to `war_score <= 10`. Slightly winning AI will still consider stalemate armistice. Supersedes R121.

### R150: Armistice Sweeteners When Losing — DONE
`ai_diplomacy.py` — AI adds sweeteners to armistice proposals when in a losing position.

---

## WAVE 3: PLAYER FEEDBACK (8 items)

### R118: Enhanced Acceptance Preview — DESIGN
`diplomacy.py (_generate_feedback)` — Show top 3 positive/negative components with labels. Talleyrand obstacle hints for worst factor.

### R119: Nations Remember Betrayal — DESIGN
`diplomacy.py` — `world.betrayal_history` dict. Escalating penalty: 1st -10, 2nd -20, 3rd+ -30 + AI hard reject. Hybrid: victim full, witnesses half. Redemption: 20 honored turns removes oldest. Record in break_treaty/declare_war.

### R131: Cooldown Pre-Check Warning — CONTENT
`executor.py` — Pre-check cooldown before proposal dialogue. Show remaining turns + Talleyrand message.

### R129: Override Feedback in Dispatch — CONTENT
`diplomatic_defiance.py` — Fix timing bug (line 741). Success: trust +2 + dispatch note. Failure: +1 concern boost + dispatch note.

### R128: Sabotage Consequence Feedback — CONTENT
`diplomatic_defiance.py` — Track sabotage outcome in `world.sabotage_history`. Dispatch note next turn. Trust +3 if Talleyrand was right.

### R132: Vassal Loyalty Transparency — CONTENT
`dispatch.py` — Lower warning threshold to 30. Show delta when |change| >= 2. `vassal.py` stores prev_loyalty. Ledger trend arrow.

### R17d-f: Ledger Enhancements (3 sub-items) — QOL
`diplomatic_ledger.py` — R17d: DP breakdown. R17e: Relation trend arrows (3-turn history). R17f: Mission progress projection.

---

## WAVE 4: DECIDE GATE (17 items)

> **Status: NEEDS DECIDED per-item before coding.**

| Item | Category | Summary |
|------|----------|---------|
| R22 | Marriage Alliances | Dynastic bonds: +20 rel, block war 5 turns, 3 DP |
| R32 | Peace Conferences | Multi-nation negotiations, 3 DP, +15 acceptance |
| R117 | Advisory Actionability | Advisory ends with executable options |
| R123 | Economic Strategy AI (P9) | Gold > 600 → subsidy offers, trade pressure |
| R124 | Diplomatic Isolation AI (P10) | Split enemy alliances with generous terms |
| R133 | Point of No Return Event | One-time Talleyrand popup at threat 40 |
| R28 | Talleyrand Voice Bank | 5-8 variants per situation type |
| R127 | Nation-Specific Intelligence | Per-nation personality lines in advisory |
| R24 | Treaty Signing Ceremonies | Talleyrand ceremony text on ratification |
| R25 | Vassal Personality Events | 3-4 random loyalty-gated events per game |
| R26 | Continental System Buff | Creative rethink on blowback balance |
| R27 | Secret Treaties | Hidden treaties, 10%/turn discovery chance |
| R33 | Puppet Rulers | Named rulers with personality, events |
| R35 | Player Counter-Offer Terms | Player specifies clauses (Godot popup) |
| R36 | Personal Summits | Face-to-face meetings, +15 acceptance 3 turns |
| R59 | Literal Personality Triggers | Audit and wire unwired triggers |
| ~~R136~~ | ~~DP Accumulation~~ | **KILLED** — DP stays use-it-or-lose-it |

---

## Implementation Summary

| Wave | Items | Est. Tests | Focus |
|------|-------|-----------|-------|
| Wave 1 | 10 | ~22 | Quick wins: bugs, balance, content |
| Wave 2 | 5 | ~19 | AI personality & intelligence |
| Wave 2.5 | 10 | 27 | Wartime peace rebalance — DONE |
| Wave 3 | 8 | ~21 | Player feedback & transparency |
| Wave 4 | 17 | TBD | Decide gate — approved per-item |

---

**Grand total (R1-R150 + GAP-3/5/6):** 165 items. 67 DONE (Phases 1-4 + R137/R120 + Wave 2.5), 38 APPROVED (Phase 5), R136 KILLED.
