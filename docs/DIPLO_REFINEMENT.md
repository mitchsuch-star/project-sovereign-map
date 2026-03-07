# Diplomacy Refinement & Cleanup

> **Created:** March 4, 2026
> **Status:** R1-R114: Phases 1-4 COMPLETE. R115-R140: Phase 5 APPROVED (creative audit gate March 7, 2026).
> **Source:** Creative audit (7.8/10) + code audit (March 5) + deep audit II (6-agent) + comprehensive creative audit (6-agent, 6.5/10, March 7)
> **Process:** Phases 1-4 DONE -> Phase 5 Design Depth IN PROGRESS -> UI test -> release

---

## Implementation Plan

7 phases of bug fixes, cleanup, balance, QoL, and design depth. Phase 2 split into 2A (diplomacy core) and 2B (vassal + AI-AI + war transitions). Phases 1-4 COMPLETE. Phase 5 adds design depth from comprehensive creative audit (March 7, 2026).

**155 total items.** 55 DONE, 59 APPROVED (Phases 1-4 remaining + Phase 5), 0 DEFERRED (all promoted to Phase 5).

| Phase | Focus | Items | Scope |
|-------|-------|-------|-------|
| **Phase 1** | Critical wiring | R37/R41, R42, R40, R43, R2, R55, R61-R66, R74, R75, R96, R109 | ~16 fixes |
| **Phase 2A** | State cleanup — diplomacy core | R1a/b, R3, R5a/b, R44, R45, R47/R30, R48, R49, R51, R52/R64, R53, R54, R56, R57, R7, R67, R80, R82, R83 | ~19 fixes |
| **Phase 2B** | State cleanup — vassal, AI-AI, war | R46, R50, R60, R68-R73, R81, R97-R102, R105, R107-R108, R110-R111, R113-R114 | ~23 fixes |
| **Phase 3** | Balance tuning | R4a/b, R6, R8, R9, R11, R14-R16, R18, R20, R104, R106 | 13 changes, 44 tests |
| **Phase 4** | Commands, QoL, Popup architecture | R10, R21, R23, R29, R31, R34, R38, R17a-c, R12, R76-R79, R84, R87-R95, R103, R112 | ~27 fixes |
| **Phase 5A** | Core design features | R22, R115-R120, R32 | 8 items |
| **Phase 5B** | AI intelligence & behavior | R121-R126 | 6 items |
| **Phase 5C** | Narrative & presentation | R28, R24-R26, R127-R133 | 11 items |
| **Phase 5D** | Bug fixes & balance | R134-R140 | 7 items |
| **Phase 5E** | Promoted deferred features | R27, R33, R35-R36, R17d-f, R58-R59 | 9 items |
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

# PHASE 5: DESIGN DEPTH & CREATIVE ENHANCEMENTS

> **Source:** 6-agent comprehensive creative audit (March 7, 2026). Scored 6.5/10 overall.
> **Goal:** Elevate diplomacy from "functional system" to "compelling gameplay pillar."
> **Status:** APPROVED — ready for implementation.
> **Scope:** 41 items (R115-R155). Promoted deferred features + new design recommendations + remaining fixes.
> **Process:** Design features FIRST (5A-5C), then fixes (5D), then content (5E).

All 16 previously-deferred items (R22-R36, R17d-f, R58-R59) are PROMOTED into Phase 5. New items R115-R155 from creative audit.

---

## Phase 5A: Core Design Features (Highest Impact)

These create new gameplay mechanics that make diplomacy a strategic pillar, not a side activity.

---

### R22: Marriage Alliances — PROMOTED from DEFERRED

**Problem:** Missing entire dimension of Napoleonic diplomacy. Marie Louise marriage secured 3 years of peace. No mechanic for dynastic bonds.

**Design:**
- Cost: 3 DP + requires ALLIANCE state
- Effect: +20 relation (permanent while married), war declaration blocked for 5 turns, +5 acceptance bonus on all proposals to married nation
- Limit: 1 marriage per nation pair, max 2 active marriages
- Break: Declaring war on married nation costs double threat (+10 extra), -30 relation, "Betrayed Marriage" modifier lasts 20 turns
- AI behavior: AI proposes marriage when relation > +60 and ALLIANCE for 5+ turns
- Talleyrand voice: "A dynastic union, Sire. The strongest treaty is written in blood, not ink."
- Keywords: "marry", "marriage", "dynastic union", "propose marriage"

**Files:** `diplomacy.py` (marriage state), `executor.py` (command), `ai_diplomacy.py` (AI trigger), `diplomatic_templates.py` (T35-T37)

### R115: Personality-Driven AI Proposal Generation — NEW

**Problem:** Metternich (Schemer) uses identical triggers to Hardenberg (Hawk). All AI nations propose the same way. Personality only affects acceptance formula, not WHAT the AI proposes. Diplomats feel interchangeable.

**Design:**
- **Hawk** (Castlereagh, Hardenberg): +10 war_score requirement for peace proposals (only propose peace when losing badly). Demand harsher terms (+50% gold demands). Propose ultimatums when winning.
- **Schemer** (Metternich): Wait 2 extra turns before proposing (patience as strategy). Propose asymmetric counter-offers (take more, give less). Higher proposal quality threshold (score 30+ vs 20+).
- **Dove** (Einsiedel): Propose peace eagerly (war_score threshold -20 instead of -40). Offer more generous terms (-25% gold demands). Accept lower-value alliances.
- **Loyalist** (Talleyrand replacement): No personality modifier — follows pure formula.

**Implementation:**
```python
def _apply_personality_to_proposal(terms, diplomat_personality, war_score):
    if diplomat_personality == "hawk":
        for demand in terms.get("demands", []):
            if demand["type"] == "gold_per_turn":
                demand["value"] = int(demand["value"] * 1.5)
    elif diplomat_personality == "schemer":
        for sweetener in terms.get("sweeteners", []):
            if sweetener["type"] == "gold_per_turn":
                sweetener["value"] = int(sweetener["value"] * 0.7)
    elif diplomat_personality == "dove":
        for demand in terms.get("demands", []):
            if demand["type"] == "gold_per_turn":
                demand["value"] = int(demand["value"] * 0.75)
```

**Files:** `ai_diplomacy.py` (process_diplomatic_phase, _build_proposal_terms)

### R116: Aggressive Dominance AI Trigger (P8) — NEW

**Problem:** No trigger for AI to capitalize on winning. When AI has war_score > +40, it never demands harsh terms, territorial concessions, or vassalage. Only defensive/desperate triggers exist (P1-P4).

**Design:**
- **P8 trigger:** When `war_score > 40` AND at war → propose harsh peace with territorial demands / gold reparations / AP reduction clause
- **P8b trigger:** When `war_score > 60` AND at peace with non-ally → propose vassalage or tribute extraction
- Scale demands by war_score: `gold_demand = min(500, war_score * 8)`
- Personality modifier: Hawk demands +50%, Dove demands -25%

**Files:** `ai_diplomacy.py` (add P8/P8b to process_diplomatic_phase)

### R117: Advisory Actionability — Execute Recommendations — NEW

**Problem:** Talleyrand gives multi-paragraph assessments ending with "Tell me more" or "Dismiss." No bridge to action. Player must manually infer and type the next command.

**Design:**
- Advisory dialogues end with action options: `[1] "Begin courting them" [2] "Propose [type]" [3] "Tell me more" [4] "Dismiss"`
- Option 1/2 → Launches mission/proposal dialogue directly (0-cost transition, no separate command needed)
- Talleyrand: "Shall I begin diplomatic overtures to {nation}, Sire? Or do you wish to hear more?"

**Files:** `diplomatic_advisory.py` (add action options to assessment), `executor.py` (handle advisory→proposal transition)

### R118: Acceptance Score Preview (Enhanced) — Extends R31

**Problem:** R31 added basic acceptance preview. Creative audit found players still can't see WHY proposals fail. Need component breakdown with Talleyrand interpretation.

**Design:**
- Show all 7+ components: "Relations: -15 (hostile). Military pressure: +12 (we're winning). Diplomat skill: -8 (Metternich outclasses us). Coalition penalty: -20. **Net: 35 (Counter-offer likely)**"
- Talleyrand interprets: "The key obstacle is coalition solidarity. If we could peel Austria away first..."
- Show special desire hints: "Prussia particularly values Saxony (+10 if included)"

**Files:** `diplomacy.py` (_generate_feedback), `diplomatic_advisory.py` (interpretation layer)

### R119: Nations Remember Betrayal — Extends R34

**Problem:** R34 added diplomatic_reliability field (+/-10 max). Creative audit found this is too weak. Breaking alliances has no lasting "fool me twice" consequence.

**Design:**
- **Betrayal memory:** Per-nation `betrayal_history` list. Each entry: `{turn, type, severity}`
- **Escalating penalty:** 1st betrayal: -10 acceptance for 10 turns. 2nd: -20 for 15 turns. 3rd+: -30 permanent
- **AI reaction:** After 2+ betrayals, AI refuses proposals outright (score floor of REJECT regardless of formula)
- **Talleyrand warning:** "Sire, {nation} remembers our last betrayal. They will not trust us easily."
- **Redemption path:** 20+ turns of honored treaties reduces betrayal count by 1

**Files:** `diplomacy.py` (betrayal tracking), `world_state.py` (serialization), `ai_diplomacy.py` (refusal check)

### R120: Diplomatic Help Text — NEW

**Problem:** Zero diplomatic commands in help text. executor.py has 130+ lines covering military commands, literally nothing about Talleyrand, proposals, DP, or diplomatic actions. Players discover diplomacy only by accident.

**Design:**
Add DIPLOMACY section to help text:
```
DIPLOMACY (via Talleyrand):
  "Talleyrand, propose peace to Prussia"     Propose treaty (2 DP)
  "Talleyrand, propose alliance with Saxony" Propose alliance (2 DP)
  "Talleyrand, assess Austria"               Threat assessment (free)
  "Talleyrand, improve relations with Austria" Start mission (1 DP/turn)
  "declare war on Prussia"                   Declare war (1 DP)
  "break treaty with Austria"                Break treaty (1 DP)
  "ultimatum to Prussia"                     Coercive demand (2 DP)
  Press D for Diplomatic Ledger. Available nations: Britain, Prussia, Austria, Saxony.
```

**Files:** `executor.py` (_execute_help)

### R32: Multi-Party Peace Conferences — PROMOTED from DEFERRED

**Problem:** Real Napoleonic diplomacy featured congresses (Vienna, Tilsit). No mechanic for multi-nation negotiations.

**Design:**
- Cost: 4 DP + requires 2+ nations at war
- Mechanic: Propose conference. All parties receive invitation. If 2+ accept, conference begins (3-turn negotiation window)
- During conference: each nation proposes terms (AI auto-generates). Player reviews all proposals. Accepts/rejects per-nation.
- Advantage: conference bonus +15 acceptance (nations are "at the table")
- Limit: 1 conference per 10 turns
- Keywords: "peace conference", "congress", "convene", "negotiate all parties"

**Files:** `diplomacy.py` (conference state), `executor.py`, `ai_diplomacy.py` (AI conference terms)

---

## Phase 5B: AI Intelligence & Behavior

These make the AI feel like it has personality and strategic thinking, not just formula outputs.

---

### R121: P2 Stalemate Trigger Fix — NEW (Bug)

**Problem:** P2 fires even when AI is slightly winning (war_score +5, within -10..+10 band). A winning nation should NOT propose armistice.

**Fix:** Add condition `and war_score <= 0` — only losing/even nations propose stalemate peace.

**File:** `ai_diplomacy.py:516-521`

### R122: Coalition Defensive Posture → Enemy AI Priority — NEW (Bug)

**Problem:** Coalition posture (Aggressive/Defensive/Cautious) is calculated and stored on `world.active_coalition["strategic_posture"]`, but enemy_ai.py never reads it. Defensive posture doesn't actually boost P5/P6 (defend/hold) priority. Coalition members always follow the same priority order regardless of posture.

**Fix:** In `enemy_ai.py`, read `world.active_coalition["strategic_posture"]` and apply:
- Aggressive: P1 (attack) +10 priority, convergence bias active
- Defensive: P5/P6 (defend/hold) +10 priority, convergence bias halved
- Cautious: P2/P3 (defend) +5, no convergence bias

**Files:** `enemy_ai.py` (priority scoring), `coalition.py` (verify posture is set)

### R123: Economic Strategy AI — Subsidy & Trade Pressure — NEW

**Problem:** Wealthy AI never "buys loyalty" with subsidies. No proposal like "I'll give you 300g/turn if you break your alliance with France." No economic warfare beyond the non-functional Continental System.

**Design:**
- **P9 trigger:** When AI nation gold > 600 AND target relation > -20 AND not allied → offer gold subsidy proposal (+100-200g/turn for NON_AGGRESSION or better)
- **Trade pressure:** When AI has ALLIANCE with target → "If you don't help in our war, we'll reconsider our trade arrangement" → -15 acceptance penalty on future proposals
- **Coalition subsidy upgrade:** British subsidy scales dynamically: +100g if coalition winning (war_score > +20), -100g if losing (< -20)

**Files:** `ai_diplomacy.py` (P9 trigger), `coalition.py` (dynamic subsidy)

### R124: Diplomatic Isolation AI — Split Enemy Alliances — NEW

**Problem:** AI never tries to "split" enemy alliances with targeted diplomacy. One of the most interesting Talleyrand strategies historically. No trigger like "offer peace to Austria to isolate France."

**Design:**
- **P10 trigger:** When AI is at war with France AND France has an ally → propose generous terms to France's ally (PEACE + gold sweetener + open_borders) to break their alliance
- Acceptance bonus: +10 "isolation offer" (target knows they're being wooed)
- Cooldown: 5 turns per target
- Narrative: "Metternich approaches Saxony: 'Austria offers friendship. France offers only servitude.'"

**Files:** `ai_diplomacy.py` (P10 trigger), `diplomatic_templates.py` (isolation templates)

### R125: AI Counter-Offer Personality — NEW

**Problem:** All diplomats use same M3 counter-offer algorithm. Hawk should demand more. Dove should accept lower scores. Schemer should propose tricky asymmetric deals.

**Design:**
- **Hawk:** Counter-offer threshold 60 (instead of 50). Add extra demand clause.
- **Dove:** Counter-offer threshold 40. Remove harshest demand.
- **Schemer:** Counter-offer threshold 50. Swap demanded clause type to one that benefits them more (gold→AP reduction, territory→gold_per_turn).

**Files:** `ai_diplomacy.py` (generate_counter_offer)

### R126: Urgent Re-Proposal on Situation Change — NEW

**Problem:** If AI proposes peace at war_score -35 and score drops to -55 next turn, AI doesn't re-propose immediately. Same cooldown regardless of desperation.

**Fix:** Bypass nation cooldown (not type cooldown) when war_score drops 20+ points since last proposal. Allow urgent re-proposal with sweetened terms.

**Files:** `ai_diplomacy.py` (cooldown check)

---

## Phase 5C: Narrative & Presentation

These make diplomacy FEEL dramatic and memorable. Template improvements, voice variety, consequence visibility.

---

### R28: Talleyrand Voice Bank — PROMOTED from DEFERRED + EXPANDED

**Problem:** Every proposal opens "Sire, [assessment]. [Facts]. [Options]." No frustration, wit, dark humor, or vindication. After 5 conversations, template fatigue sets in.

**Design:** Create 5-8 variants per situation type, randomly selected:

**Winning peace proposal:**
```python
TALLEYRAND_WINNING_PEACE = [
    "Sire, we have them at our mercy. The question is not whether to strike, but how hard.",
    "They are beaten, Sire. Now comes the delicate part — extracting concessions without driving them to desperation.",
    "The moment is ours. What shall we demand?",
    "Our triumph is complete — now we must ensure it lasts. Shall we show mercy, or remind them of their place?",
    "Victory belongs to France, Sire. The courts of Europe watch to see how we wield it.",
]
```

**Losing peace proposal:**
```python
TALLEYRAND_LOSING_PEACE = [
    "I will not sugarcoat it, Sire — we must negotiate now, while we still have cards to play.",
    "Pride is a luxury we cannot afford when armies bleed. Let us seek terms.",
    "The situation deteriorates by the day. But even from weakness, Talleyrand can find leverage.",
    "Sire, the mathematics of war are against us. The mathematics of diplomacy, however...",
]
```

- Limit "Sire" usage to 40% of lines. Mix in "Your Majesty," direct statements, and no-title variants.
- Add emotional color: frustration (after rejected proposals), vindication (after sabotage proves right), dark humor (after betrayal).

**Files:** `diplomatic_templates.py` (voice bank arrays), template resolver (random selection)

### R127: Nation-Specific Diplomatic Intelligence — NEW

**Problem:** Austria, Prussia, Saxony, and Britain receive identical template text. Talleyrand never references national characteristics. No "Prussia respects only strength" or "Saxony will follow whoever looks strongest."

**Design:** Per-nation intelligence lines in advisory:
```python
NATION_INTELLIGENCE = {
    "Prussia": "Prussia respects only strength, Sire. Show hesitation, and they will demand more.",
    "Austria": "Austria values tradition above all. A proposal that honors their dignity has better chances.",
    "Britain": "Britain fights with gold, not men. Their weakness is on land, not at sea.",
    "Saxony": "Saxony is caught between the great powers. They will follow whoever looks strongest.",
}
```

- Surface in Talleyrand advisory: "I have studied their court, Sire. {intelligence_line}"
- Surface in proposal dialogue: hint text after proposal type selection
- Surface special desires: "Prussia particularly values Saxony acquisition (+10 bonus)"

**Files:** `diplomatic_advisory.py`, `diplomatic_templates.py`

### R128: Sabotage Consequence Feedback — NEW

**Problem:** When sabotage is discovered, player confronts/overlooks. But no consequence is shown — did the modified terms succeed? Was Talleyrand right? Sabotage is an event, not a story.

**Design:**
- Next turn's dispatch: "Berthier reports: {nation} accepted Talleyrand's modified peace proposal. The softer terms secured their agreement." OR "Berthier reports: {nation} rejected the proposal despite Talleyrand's modifications. His judgment proved mistaken."
- Track sabotage outcome in `world.sabotage_history`: `{turn, target, original_terms, modified_terms, outcome}`
- If Talleyrand was right (modified terms accepted, original would have failed): Trust +3 bonus
- If Talleyrand was wrong (modified terms rejected anyway): No penalty, but next objection has lower concern level

**Files:** `diplomatic_defiance.py`, `dispatch.py` (sabotage outcome event), `world_state.py` (sabotage_history)

### R129: "I Was Right" Override Feedback — NEW

**Problem:** Player overrides Talleyrand's warning and succeeds — no affirmation. System records data but doesn't narratively connect to gameplay. Talleyrand is rewarded for caution, never for being overridden successfully.

**Design:**
- When player override succeeds → dispatch note: "Your judgment regarding {nation} proved sound, Sire." + Trust +2
- When player override fails → dispatch note: "Talleyrand's concerns regarding {nation} were, perhaps, not unfounded." + No trust penalty, but next Talleyrand objection has +1 concern level
- Fix timing bug: `get_override_dispatch_note()` fires on wrong turn offset (line 741 checks `turn < current_turn - 1`)

**Files:** `diplomatic_defiance.py` (override tracking), `dispatch.py` (outcome notes)

### R24: Treaty Signing Ceremonies — PROMOTED from DEFERRED

**Problem:** After turns of negotiation, treaty accepted — "Treaty ratified." Flat. No ceremony, no Talleyrand voice, no moment of achievement.

**Design:**
- On treaty ratification, Talleyrand delivers ceremony line (personality-appropriate):
  ```
  "Sire, the treaty is sealed. {nation} has agreed to {terms_summary}.
   History will record this day. Whether it records it kindly... that depends on what comes next."
  ```
- Ceremony text varies by treaty type (peace vs alliance vs vassalage)
- War-ending peace gets special treatment: casualty summary, territory changes, gold terms
- Notification: "Treaty of [Capital]" with treaty details

**Files:** `diplomatic_templates.py` (T38-T42 ceremony templates), `executor.py` (ceremony trigger)

### R130: Confidence Levels in Advisory — NEW

**Problem:** Advisory context includes "confidence_level" (high/medium/low) but it's never expressed to the player. Talleyrand never says "I am certain" or "my intelligence is incomplete."

**Design:**
- High confidence (70+): "Sire, I am confident in this assessment. My sources are reliable."
- Medium (40-69): "Sire, our intelligence is adequate, though gaps remain."
- Low (<40): "I must warn you — my information on this matter is incomplete. Proceed with caution."
- Tie to fog of war: confidence = best visibility tier for target nation's regions

**Files:** `diplomatic_advisory.py` (express confidence in text)

### R131: Cooldown Pre-Check Warning — NEW

**Problem:** Player discovers cooldown mid-conversation. Tries "propose peace to Austria" → Talleyrand says "Austria's court is still discussing." Feels like an invisible wall.

**Fix:**
- Pre-check cooldown BEFORE launching proposal dialogue
- If on cooldown → Talleyrand: "Sire, Austria's court still deliberates on our last proposal. {X} turns remain. Shall I propose a different type, or shall we wait?"
- Option: `[1] Different proposal type [2] Wait [3] Dismiss`

**Files:** `executor.py` (pre-validation), `diplomatic_dialogue.py`

### R132: Vassal Loyalty Transparency — NEW

**Problem:** Vassal loyalty silently decays (-1/turn from drift), then suddenly "CRITICAL!" popup appears. No intermediate visibility.

**Fix:**
- Show loyalty change in morning dispatch when |delta| >= 2 OR loyalty <= 30 (lower threshold than current 20)
- Format: "Saxony loyalty: 65 (-2 from autonomy drift, +1 from shared enemy)"
- Show in diplomatic ledger: loyalty trend arrow (up/down/stable)

**Files:** `dispatch.py` (loyalty section), `diplomatic_ledger.py` (trend display)

### R133: "Point of No Return" Dramatic Moment — NEW

**Problem:** Threat at 40+ is "getting dangerous" but there's no special event. Coalition brewing starts at 60 — by then it may be too late to defuse.

**Design:**
- At threat 40 (first time): Special Talleyrand advisory popup (not dispatch — this is important):
  "Sire, the courts of Europe grow restless. I hear whispers of coalition. We have time — but not much. Shall I begin diplomatic overtures?"
- Options: `[1] "Court the most hostile nation" [2] "Assess the situation" [3] "Let them whisper"`
- One-time event per game (flag `threat_40_warning_shown`)

**Files:** `coalition.py` (trigger), `diplomatic_templates.py` (T43), `executor.py` (popup)

### R25: Vassal Personality Events — PROMOTED from DEFERRED

**Problem:** Vassals are numbers, not characters. No drama, no personality, no "Saxony's regent is plotting."

**Design:**
- 3-4 vassal events per game (random, loyalty-gated):
  - **Loyal vassal request** (loyalty > 60): "Saxony requests trade privileges." Accept: +5 loyalty, -50g/turn. Reject: -5 loyalty.
  - **Disloyal vassal plot** (loyalty < 30): "Intelligence suggests Saxony is negotiating with Austria." Confront: -10 loyalty, +5 authority. Ignore: risk of cascade.
  - **Vassal contribution** (loyalty > 80): "Saxony volunteers 5,000 reinforcements." Accept: +5k troops. Decline: -3 loyalty.

**Files:** `vassal.py` (event generation), `executor.py` (event handling), `dispatch.py` (event reporting)

### R26: Continental System Strengthening — PROMOTED from DEFERRED

**Problem:** CS is a trap choice — 2 DP/turn for ~200g blocked from Britain. COURT_NATION at same cost yields +8 relation/turn. CS needs to be worth activating.

**Design (extends R18):**
- **Reduce CS cost:** 1 DP/turn (was 2, technically fixed by R18 but still too expensive)
- **Increase CS impact:** Block 100g/nation/turn (was 75g). With 3 CS members: 300g blocked (50% of British income)
- **Add CS benefit:** +2 relation/turn with all CS members (solidarity against Britain)
- **Add CS risk:** -3 relation/turn with Britain (escalating hostility)
- **British retaliation:** When CS active, Britain gets +5 acceptance for aggressive proposals against CS members
- **Player decision:** CS is now meaningful: weaken Britain's economy at cost of British hostility + DP

**Files:** `diplomacy.py` (CS mechanics), `coalition.py` (CS-subsidy interaction)

---

## Phase 5D: Bug Fixes & Balance (From Creative Audit)

Remaining bugs found by creative audit not covered in R1-R114.

---

### R134: DEBUG_MODE Hardcoded to True — Security Fix — NEW

**Problem:** `main.py:27` has `DEBUG_MODE = True` with comment "Set to False for production." 10 diplomatic debug endpoints leak all game state. Any HTTP client can call `/debug/acceptance_preview`, `/debug/coalition_status`, etc.

**Fix:** `DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"`

**File:** `main.py:27`

### R135: Garrison Trivializes Vassal Loyalty — Balance — NEW

**Problem:** 15k garrison completely offsets puppet autonomy drift (-4/turn) with +8 loyalty/turn. Loyalty system becomes "garrison system" — station troops, never worry about loyalty again.

**Fix:** Cap garrison loyalty bonus at +4/turn (was +5 base + troops//5000 up to +8). Garrison still helps, but can't fully offset puppet drift. Player must also invest DP or improve relations.

**Files:** `vassal.py` (garrison bonus calculation)

### R136: DP Use-It-Or-Lose-It Economy — Balance — NEW

**Problem:** DP doesn't accumulate between turns. Generate 4 DP/turn, use 2, waste 2. Creates perverse incentive to spend DP on suboptimal actions. No "saving for a big move."

**Fix:** Allow DP accumulation up to max 12. `world.diplomatic_points = min(12, current + generated)`. Enables saving for conferences (4 DP), marriage proposals (3 DP), or burst diplomacy.

**Files:** `diplomacy.py` (DP processing), `world_state.py` (serialization)

### R137: "ally with Prussia" Parser Ambiguity — NEW

**Problem:** "ally" is in military_keywords (ambiguous), not diplomatic. "ally with Prussia" might fail to route to diplomatic parser. Must say "propose alliance with Prussia."

**Fix:** Add "ally with", "ally against", "become allies" to diplomatic keyword detection (higher priority than military "ally" keyword).

**Files:** `llm_client.py` (keyword priority)

### R138: Counter-Offers Free for AI — Balance — NEW

**Problem:** Counter-offers cost 0 DP. AI can counter-offer endlessly with no resource cost. In real negotiation, crafting a counter is work.

**Fix:** Counter-offers cost 1 DP for AI nations. Player counter-offers remain free (player already invested in initial proposal).

**Files:** `diplomacy.py` (counter-offer DP cost)

### R139: AI DP Cap Too Low — Balance — NEW

**Problem:** France generates 4 DP/turn vs AI's 2-3 DP max. France has 2x diplomatic resource advantage by default. AI can barely afford 1 action per turn.

**Fix:** Raise AI DP cap to 4 (same as France base). AI nations with high authority or skill 8+ diplomats should match France's diplomatic capacity.

**Files:** `diplomacy.py` (calculate_dp for AI nations)

### R140: Relation Cap in Acceptance Formula — Balance — NEW

**Problem:** Relation modifier contributes ±50 to acceptance score, dominating all other factors. Military victory (+15 max from pressure) is mathematically irrelevant when relation is -100.

**Fix:** Cap relation modifier at ±30 (was ±50). This preserves relation importance while allowing military and other factors to matter.

**Files:** `diplomacy.py` (calculate_acceptance, relation_mod calculation)

---

## Phase 5E: Promoted Deferred Features (Lower Priority)

Previously deferred to "post-UI-test design session." Now promoted but lower priority within Phase 5.

---

### R27: Secret Treaties — PROMOTED from DEFERRED

**Design:**
- Cost: 3 DP + requires OPEN_BORDERS minimum
- Mechanic: Secret treaty invisible to other nations. Discovered via spy missions or when activated.
- Types: Secret alliance (join war when triggered), partition plan (divide a third nation), non-aggression (secret promise not to attack)
- Discovery: 10%/turn chance of discovery by each nation. Discovered: -20 relation with all non-party nations, +15 threat
- Keywords: "secret treaty", "secret alliance", "secret pact"

### R33: Dynastic Succession / Puppet Rulers — PROMOTED from DEFERRED

**Design:**
- On vassalization: install puppet ruler (named, generated). Ruler personality affects loyalty drift.
- Puppet ruler events: assassination attempt, popular uprising, ruler defection
- Replace ruler: 2 DP + 200g. New ruler, reset loyalty to 40.
- Connects to marriage system (married vassals get loyalty floor of 30)

### R35: Player-Specified Counter-Offer Terms — PROMOTED from DEFERRED

**Design:**
- When AI counter-offers: show counter terms + option `[Modify and Re-Send]`
- Player can adjust: add/remove clauses, change gold amounts, swap territory
- Re-send costs 1 DP (negotiation overhead)
- Max 2 rounds of back-and-forth per proposal

### R36: Personal Summits — PROMOTED from DEFERRED

**Design:**
- Cost: 3 DP + both nations at PEACE minimum
- Effect: Face-to-face meeting with nation leader. +15 acceptance bonus for 3 turns. Special dialogue with leader personality.
- Limit: 1 per nation per 15 turns
- Historical: Tilsit, Erfurt — personal chemistry mattered

### R17d-f: Ledger Enhancements — PROMOTED from DEFERRED

| Sub-item | Description |
|----------|-------------|
| R17d | DP generation factors in ledger (base, skill, authority, capital breakdown) |
| R17e | Relation trend arrows in ledger (improving/declining/stable per nation) |
| R17f | Mission progress projection (estimated turns remaining, relation at completion) |

### R58: Vindication Tracker Decay — PROMOTED from DEFERRED

**Fix:** Vindication tracker values decay by 1 per 5 turns toward 0. Prevents permanent vindication from a single event.

### R59: Literal Personality Triggers — PROMOTED from DEFERRED

**Fix:** Wire literal personality triggers that never fire. Literal marshals should generate unique objection text when given vague/ambiguous orders.

---

## Phase 5 Cross-Reference

| Item | Category | Priority | Phase |
|------|----------|----------|-------|
| R22 | Marriage Alliances | DESIGN | 5A |
| R115 | Personality AI Proposals | DESIGN | 5A |
| R116 | Aggressive Dominance P8 | DESIGN | 5A |
| R117 | Advisory Actionability | DESIGN | 5A |
| R118 | Acceptance Preview Enhanced | DESIGN | 5A |
| R119 | Nations Remember Betrayal | DESIGN | 5A |
| R120 | Diplomatic Help Text | DESIGN | 5A |
| R32 | Peace Conferences | DESIGN | 5A |
| R121 | P2 Stalemate Fix | BUG | 5B |
| R122 | Coalition Posture → AI | BUG | 5B |
| R123 | Economic Strategy AI | DESIGN | 5B |
| R124 | Diplomatic Isolation AI | DESIGN | 5B |
| R125 | Counter-Offer Personality | DESIGN | 5B |
| R126 | Urgent Re-Proposal | DESIGN | 5B |
| R28 | Talleyrand Voice Bank | CONTENT | 5C |
| R127 | Nation-Specific Intelligence | CONTENT | 5C |
| R128 | Sabotage Consequence Feedback | CONTENT | 5C |
| R129 | Override Feedback | CONTENT | 5C |
| R24 | Treaty Ceremonies | CONTENT | 5C |
| R130 | Confidence Levels | CONTENT | 5C |
| R131 | Cooldown Pre-Check | CONTENT | 5C |
| R132 | Vassal Loyalty Transparency | CONTENT | 5C |
| R133 | Point of No Return | CONTENT | 5C |
| R25 | Vassal Events | CONTENT | 5C |
| R26 | Continental System Buff | CONTENT | 5C |
| R134 | DEBUG_MODE Security | BUG | 5D |
| R135 | Garrison Loyalty Cap | BALANCE | 5D |
| R136 | DP Accumulation | BALANCE | 5D |
| R137 | Parser Ambiguity | BUG | 5D |
| R138 | Counter-Offer DP Cost | BALANCE | 5D |
| R139 | AI DP Cap | BALANCE | 5D |
| R140 | Relation Cap | BALANCE | 5D |
| R27 | Secret Treaties | DESIGN | 5E |
| R33 | Puppet Rulers | DESIGN | 5E |
| R35 | Player Counter Terms | DESIGN | 5E |
| R36 | Personal Summits | DESIGN | 5E |
| R17d-f | Ledger Enhancements | QOL | 5E |
| R58 | Vindication Decay | FIX | 5E |
| R59 | Literal Triggers | FIX | 5E |

---

**Grand total (R1-R140 + GAP-3/5/6):** 155 items. 55 DONE, 59 APPROVED, 0 DEFERRED. Phase 5 (41 items) is next.
