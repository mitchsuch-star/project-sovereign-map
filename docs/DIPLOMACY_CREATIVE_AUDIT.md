# Diplomacy System — Creative Audit

> **Created:** March 4, 2026
> **Scope:** Design quality, balance, historical accuracy, fun, missing features, edge cases
> **Method:** 5 parallel deep-dive analyses across balance, history/fun, missing features, AI/formulas, and edge cases
> **Previous audit:** `DIPLOMACY_AUDIT.md` (mechanical bugs — 20 fixed, 145 tests). This audit is creative/design-focused.

---

## Overall Scores (1-10)

| Dimension | Score | Key Strength | Key Gap |
|---|---|---|---|
| **Fun Factor** | 8 | Conversational Talleyrand layer is genre-defining | Counter-offer lacks player input |
| **Historical Accuracy** | 8 | Coalition dynamics, Tilsit mechanics, Austria as swing state | No marriage alliances, no Spain/Russia |
| **Surprise Factor** | 7 | Coalition brewing, defection cascade (Leipzig moment) | Sabotage too rare at 2% floor to feel real |
| **Player Agency** | 8 | 6 mission types, clause building, free feasibility checks | Counter-offer is a black box; missing commands |
| **AI Believability** | 7 | Metternich armed mediation, personality variety | Same decision tree for all; no long-term AI plans |
| **Narrative Richness** | 8 | 56+ templates, personality-specific diplomat voices | Treaty signing anticlimactic; routine events silent |
| **Strategic Depth** | 9 | Multiple viable strategies, economic-diplomatic feedback loops | One dominant "court everyone" optimal path |
| **Emotional Impact** | 7 | Talleyrand redemption event, Leipzig cascade | Vassal rebellion mechanical; alliance success uncelebrated |
| **Pacing** | 7 | 1-turn transit tension, DP use-or-lose, brewing countdown | WAR-to-ALLIANCE takes 6+ turns; cooldown dead zones |
| **Combat Integration** | 9 | War score → acceptance, decisive battles, alliance cascade | Near-perfect — deepest system interconnection |

**Overall: 7.8/10** — An ambitious, largely successful diplomatic system that captures Napoleonic statecraft better than most grand strategy games. The conversational Talleyrand layer is genuinely innovative.

---

## PART 1: CRITICAL BUGS (Code Issues Found During Creative Audit)

These are mechanical problems discovered while analyzing design quality. Fix before any design work.

### BUG-1: War Score Decay Is a No-Op (CRITICAL)

**Files:** `diplomacy.py` lines 332, 1071-1072

`process_diplomacy_turn()` calls `recalculate_war_scores()` (computes from scratch using `battle_records`) then `apply_war_score_decay()` (subtracts 2). Next turn, `recalculate_war_scores()` overwrites the decayed value. Decay is immediately nullified. Battle records are NEVER pruned — a battle from turn 5 still contributes +3 at turn 50.

**Impact:** War scores are permanently sticky. Early military dominance creates infinite diplomatic leverage.

**Fix:** Prune `battle_records` older than 10 turns in `apply_war_score_decay()`, or apply decay to the records themselves (reduce old records' contribution).

### BUG-2: Battle Records Persist Across Wars (CRITICAL)

**Files:** `diplomacy.py` lines 962-1009, 254-329

`record_battle()` appends to `world.battle_records[diplo_key]` but records are never cleared when war ends. Peace → re-declare war → start new war with old battle score banked.

**Exploit:** Fight, peace, fight again. Each cycle banks permanent war score. Competitive player wins trivially.

**Fix:** Clear `battle_records[key]` and `decisive_battles[key]` when transitioning out of WAR state.

### BUG-3: Counter-Offer Path Treats Counter as Rejection (CRITICAL)

**Files:** `world_state.py` line 3855

When player proposals score 30-49 (COUNTER_OFFER range), the code treats it as REJECT:
```python
elif outcome == "COUNTER_OFFER":
    # Stub: treat as REJECT with hint (Session 4 adds full counter-offer)
```
Comment says "Session 4 adds full counter-offer" — never completed. Player spends DP, waits a turn, gets flat rejection with cooldown. The acceptance formula's most interesting outcome (negotiation!) is broken.

### BUG-4: Armistice Expiration Unimplemented (HIGH)

**Files:** `diplomacy.py` lines 1157-1162

`_process_armistice_expiration()` is a complete stub returning `[]`. Armistices never expire. Once ARMISTICE state is set, it persists indefinitely. No timer, no notification, no automatic transition.

### BUG-5: Armistice Cooldowns Never Written (HIGH)

**Files:** `world_state.py` line 370

`armistice_cooldowns` dict is initialized but **no code ever writes to it**. The 5-turn cooldown between armistices (§5b.2) is specified but never enforced.

### BUG-6: Treaty Clause Gold Enforcement Unimplemented (HIGH)

**Files:** `diplomacy.py` line 1092

`# TODO: 11. Treaty obligation checks (Session 3)` — gold-per-turn clauses from treaties are stored but **never actually transfer gold**. Every financial clause in every treaty is meaningless.

### BUG-7: Treaty Clause Gold Has No Floor (MEDIUM)

**Files:** `world_state.py` lines 4064-4066

`_process_treaty_clauses` does raw subtraction with no floor check. Treaty clause gold can drive a nation's gold to negative infinity.

### BUG-8: Defensive Alliance Uses Alliance Base Disposition (MEDIUM)

**Files:** `ai_diplomacy.py` lines 383-384, `diplomacy.py` lines 95-103

`_build_proposal_terms()` sets `terms["type"] = "alliance"` for defensive alliance proposals. No `"defensive_alliance"` entry in `BASE_DISPOSITION`. Defensive alliances are exactly as hard to achieve as full alliances.

**Fix:** Add `"defensive_alliance": 25` to `BASE_DISPOSITION`.

---

## PART 2: BALANCE ISSUES

### BAL-1: COURT_NATION Relation Speed Is Too Fast (HIGH)

COURT_NATION gives +8/turn base. With Talleyrand skill 10 (1.5x), that's +12/turn. Austria goes from -30 to +42 (ALLIANCE threshold) in **6 turns**. The player can ally with every nation by turn 20.

**The dominant strategy:** Always be courting. COURT_NATION → flip nation → COURT_NATION next target → repeat. No relation decay means permanent advantages with zero maintenance.

| Turn | Austria Relation | Unlocked State |
|------|-----------------|----------------|
| 1 | -18 | PEACE |
| 3 | +6 | NON_AGGRESSION eligible |
| 5 | +30 | DEFENSIVE_ALLIANCE eligible |
| 6 | +42 | ALLIANCE eligible |

**Fix options:**
- (A) Reduce COURT_NATION to +5/turn
- (B) Diminishing returns: -1 cumulative per turn on same target (turn 1: +12, turn 2: +11... floor +4)
- (C) Add rival jealousy: improving relations with A degrades relations with A's enemies by -2
- (D) Add passive relation decay toward 0 when no active mission

### BAL-2: No Relation Decay Creates Permanent Advantages (HIGH)

Relations only change via explicit events. No passive drift toward neutral. Once at +100, stays forever. Early diplomatic investment has infinite ROI. After turn 10, the player never needs to think about diplomacy again.

**Fix:** Add -1/turn passive drift toward 0 for relations > +10 or < -10, skipping pairs with active missions.

### BAL-3: Trade Income Snowball (HIGH)

ALLIANCE gives 200g/turn bilateral. Two alliances = 400g/turn. France's base income is ~1,100g/turn. Trade nearly doubles it. More gold → more armies → more victories → more favorable treaties → more alliances → more gold. No cap, no diminishing returns.

**Fix:** Per-nation trade income cap (400g max from all partners), or diminishing returns: 1st partner 200g, 2nd 150g, 3rd 100g, 4th 50g.

### BAL-4: Coalition Stalemate Duration (HIGH)

War exhaustion at +5/turn means coalition must persist 30 turns before separate peace becomes viable. In a 40-turn game, that's 75% of game time in a stalemate.

**Fix options:**
- Increase passive WE to +8/turn
- Add stalemate auto-armistice: if war score stays -10 to +10 for 8+ turns, coalition offers armistice
- Add internal friction escalation: coalition members lose -2 mutual relation/turn (historical infighting)

### BAL-5: DP Asymmetry — France 4 vs AI 2-3 (MEDIUM)

France has 33-100% more diplomatic resources than any AI nation. Combined with non-accumulation, France can sustain COURT_NATION + proposals simultaneously while AI can barely afford one action.

### BAL-6: War Score Farming via Small Battles (MEDIUM)

Every battle win gives +3 regardless of scale. A 500-casualty skirmish = a 50,000-casualty engagement. Send a strong marshal to stomp weak forces repeatedly.

**Fix:** Add minimum casualty threshold (2000) for battle records to count toward war score.

### BAL-7: Continental System Underwhelming (MEDIUM)

Costs 2 DP/turn (40-50% of diplomatic budget). Blocks 75g/nation (200g cap) from British income. Britain earns ~600g/turn total — blocking 200g is a 33% reduction but COURT_NATION at the same DP cost gives much more strategic value. CS is a trap choice.

**Fix:** Add diplomatic blocking effect: CS members apply -10 acceptance to any British proposal. Or reduce CS cost to 1 DP/turn.

### BAL-8: Vassal Shuffle Threat Exploit (MEDIUM)

Vassalize Saxony (+5 threat) → Release (+20 relation, -8 threat) = net -3 threat per cycle. Player can grind threat down indefinitely.

**Fix:** Track per-nation release cooldown (5 turns), or reduce voluntary release threat reduction to 3.

### BAL-9: AI-AI Diplomacy Reaches Static Equilibrium (MEDIUM)

AI-AI diplomacy has 4 triggers, 3 push toward higher states. No AI-AI downgrade or betrayal logic. By turn 20, all AI nations are at DEFENSIVE_ALLIANCE+ with each other. World becomes static.

**Fix:** Add AI-AI rivalry trigger (competition over border regions: -3 relation/turn) and opportunistic downgrade trigger (strong nation downgrades weak ally).

### BAL-10: Threat Sweet Spot Enables Infinite Expansion (MEDIUM)

Max threat decay is 3-4/turn. Battle win adds +5. Fighting one battle every 2 turns = ~2.5 threat/turn average, below decay rate. France can conquer indefinitely by spacing battles.

**Fix:** Add +2 threat per region captured (not just passive thresholds at 60/70/80%).

---

## PART 3: MISSING FEATURES & DESIGN GAPS

### HIGH Impact

| # | Gap | Description | Difficulty |
|---|-----|-------------|------------|
| GAP-1 | **Player counter-offer terms** | Player cannot specify counter-offer terms. M3 algorithm is a black box. Should open clause-selection UI. | HARD |
| GAP-2 | **Player war declaration command** | `declare_war()` exists but no player-facing command. Can only declare war by marching into territory. | MEDIUM |
| GAP-3 | **Player treaty cancellation** | `break_treaty()` fully implemented, ledger shows cancel_cost, but no executor route. | EASY |
| GAP-4 | **Acceptance score preview** | Player can't see estimated acceptance for a specific proposal before spending DP. Feasibility gives qualitative tiers only. | MEDIUM |
| GAP-5 | **Player voluntary downgrade** | `execute_downgrade()` exists but no player command. Can't step down alliances that aren't serving you. | EASY |
| GAP-6 | **AI-AI state visibility in ledger** | Ledger only shows player's diplomatic states. Austria-Prussia alliance invisible. Critical for strategy. | EASY |

### MEDIUM Impact

| # | Gap | Description | Difficulty |
|---|-----|-------------|------------|
| GAP-7 | Ultimatum/coercive diplomacy | No "accept or face war" mechanic. Napoleon used coercive diplomacy constantly. | HARD |
| GAP-8 | Proposal history | No display of past proposals with outcomes. After 20 turns, player can't review diplomatic history. | MEDIUM |
| GAP-9 | Cooldown timer display | Player discovers proposal cooldowns only when blocked. Should show in Talleyrand tab. | EASY |
| GAP-10 | War score component display | Player can't see territory/battle/capital breakdown. Must guess why they're winning/losing diplomatically. | EASY |
| GAP-11 | IMPROVE_RELATIONS progress projection | No "5 more turns to reach OPEN_BORDERS threshold." Player flies blind. | EASY |
| GAP-12 | Treaty ongoing costs display | Ledger shows clause text but no "costing you 100g/turn" breakdown. | EASY |
| GAP-13 | Auto-downgrade popup | Alliance silently downgrading is a major event. Should trigger popup, not just dispatch text. | MEDIUM |
| GAP-14 | AI defensive alliance popup | When AI nations form DEFENSIVE_ALLIANCE against player mid-war — should warn dramatically. | MEDIUM |
| GAP-15 | Diplomatic events → marshal trust | Declaring war, signing peace, making vassals have zero impact on marshal morale. Cross-system blind spot. | MEDIUM |
| GAP-16 | Vassal courting visibility in ledger | No section showing "nations actively courting your vassals." | EASY |
| GAP-17 | DP generation rate display | Talleyrand tab shows remaining DP but not what factors affect generation. | EASY |
| GAP-18 | Relation trend indicator | No "trending up/down/stable" to anticipate auto-downgrades. | EASY |

---

## PART 4: HISTORICAL ACCURACY GAPS

### Missing Historical Moments (Cannot Happen in This System)

| Historical Event | Why It Can't Happen | Impact |
|---|---|---|
| **Marriage alliances** | No personal diplomacy. Napoleon's marriage to Marie Louise (1810) secured 3 years of peace. | HIGH |
| **Multi-party peace conferences** | All diplomacy is bilateral. No Congress of Vienna mechanic. | MEDIUM |
| **Spain & Peninsular War** | Not modeled. Napoleon's greatest diplomatic catastrophe is absent. | LOW (scope) |
| **Russia & 1812** | Not modeled. The eastern dimension of Napoleonic diplomacy is entirely missing. | LOW (scope) |
| **Secret treaties** | All treaties are public. Tilsit's secret articles can't happen. | MEDIUM |
| **Personal summits** | No "raft on the Niemen" moments. No face-to-face negotiation mechanic. | LOW |
| **Spy networks & bribery** | Only GATHER_INTEL mission. No bribing enemy court officials or generals. | LOW |
| **Hostage exchange** | Historical standard for treaty compliance. Not modeled. | LOW |
| **Dynastic succession** | Can't install family members as puppet rulers — Napoleon's primary vassal management tool. | MEDIUM |

---

## PART 5: AI BEHAVIOR ISSUES

### AI-1: P3 and P5 Triggers Deferred but Critical (HIGH)

P3 (threat > 60, seek alliance) and P5 (gold < 200, economic deals) are commented out. Nations don't proactively seek alliances when France threatens. Austria, which historically maneuvered before coalitions formed, waits passively.

### AI-2: Relation Penalty Dominates Wartime Proposals (HIGH)

Relation modifier is `relation / 2`. France-Prussia at -40 = permanent -20 penalty. Military victories improve war_score but NOT relations. Even with war_score 80 + capital held, peace only scores ~37 without sweeteners. Winning militarily should partially offset diplomatic hostility.

**Fix:** Add "military pressure" modifier: `max(0, war_score * 0.15)` when proposer winning. Up to +15 at war_score 100.

### AI-3: Diplomat Skill Penalty Cripples Minor Nations (MEDIUM)

Saxony (skill 4) proposing to France (skill 10): penalty is (4-10)*2 = -12. Combined with low base, Saxony proposals ALWAYS land in counter-offer zone, never auto-succeed.

**Fix:** Cap skill differential penalty at -8.

### AI-4: Coalition Members Don't Coordinate Attacks (MEDIUM)

Each coalition member runs independently. No "pile on" behavior. France can defeat them in detail (which is historically accurate as a possibility, but should be harder to exploit).

**Fix:** When a coalition member engages a French marshal, flag that target for +15 priority bonus for other coalition members.

### AI-5: AI Never Voluntarily Breaks Treaties (MEDIUM)

No code for AI-initiated treaty breaking or downgrade. Nations in unfavorable alliances are trapped forever.

### AI-6: AI Has No Memory of Player Diplomatic Behavior (LOW)

No "trust history." If the player always breaks treaties, nations should become harder to negotiate with (beyond the relation penalty).

---

## PART 6: EDGE CASE SCENARIOS

### EDGE-1: Alliance Paradox (MEDIUM)

France allied with Austria AND Saxony. Austria declares war on Saxony. The cascade code silently breaks France-Austria alliance with no popup, no choice, no warning. Player invested DP in both alliances and gets zero agency.

**Fix:** Show popup: "Austria has attacked your ally Saxony. Honor alliance with Saxony (war with Austria) or break alliance with Saxony?" Also have AI check for shared alliance partners before declaring war.

### EDGE-2: Ghost Nation / No Elimination (MEDIUM)

All Prussian regions captured, peace signed. Prussia has 0 regions, 0 income, marshals stranded in enemy territory unable to move. Nation continues generating DP, being processed by AI diplomacy, potentially declaring war with 0 troops. Gold goes to negative infinity from upkeep.

**Fix:** If nation has 0 regions AND 0 army strength → mark eliminated, skip processing, disband marshals. Floor nation gold at 0.

### EDGE-3: Strategic Order Auto-Cancel on Peace Not Implemented (LOW)

§5b.4 specifies auto-cancellation of military orders against now-peaceful nations. Not implemented. Movement restriction compensates (pathfinding fails), but marshal wastes a turn.

### EDGE-4: Cascade Cascade — No Issue (NONE)

France at war with Britain, declares war on Austria, Prussia already at war with France. The `is_at_war` guard correctly prevents duplicate processing. Working as designed.

### EDGE-5: Dead Diplomat — Working as Designed (NONE)

Loyalist replacement + lost capital + low authority = 1 DP/turn. Can only accept/reject/counter incoming proposals. Cannot initiate anything. Intended crippling effect that incentivizes recapturing Paris.

### EDGE-6: Sabotage Peace — Working as Designed (NONE)

Talleyrand sabotages terms → softer terms accepted → discovered after signing. Treaty stands. Discovery is about trust, not undoing outcomes. Matches historical Talleyrand behavior.

### EDGE-7: Multi-Vassal Cascade — Working as Designed (LOW)

Sequential cascade penalty. Pre-built rebellion list prevents infinite chain. Cascade-induced zero-loyalty vassals deferred to next turn. Minor ordering effect is acceptable.

---

## PART 7: NARRATIVE & FEEL

### What's Missing Narratively

1. **Treaty signing is anticlimactic.** After turns of negotiation, result is "Treaty ratified." No ceremony, no drama. Should have a template — Talleyrand presenting the treaty, enemy diplomat's reaction.

2. **Alliance success feels unearned.** No celebration when you achieve ALLIANCE after 6 turns of courting. Just a state change.

3. **Routine diplomacy is narratively empty.** No flavor for: relation changes, mission progress milestones, tribute collection, envoy departures.

4. **Continental System lacks drama.** Should generate smuggling events, economic hardship narratives, British countermeasures. Currently just a gold counter modifier.

5. **Vassal narrative is thin.** No vassal personality, no unique events, no "Saxony requests autonomy" dialogues, no investment flavor text. Rebellion is a threshold, not a story.

6. **Template repetition risk.** ~56 unique text blocks. In a 50-turn game with 2-3 diplomatic interactions/turn = 100-150 displays. Noticeable repetition by turn 25.

7. **No historical references.** Talleyrand never says "Remember Tilsit" or references specific precedents.

---

## PART 8: THE COMPETITIVE PLAYER'S EXPLOIT PATH

A min-maxing player would:

1. **Turns 1-6:** COURT_NATION Austria. Relation: -30 → +42.
2. **Turn 7:** Propose ALLIANCE with Austria. Accepted.
3. **Turns 7-12:** COURT_NATION Saxony (+40 → +100). Propose VASSAL.
4. **Meanwhile:** Win battles against Prussia/Britain. Each win banks permanent +3 war score (never cleared — BUG-2).
5. **Turns 13-18:** COURT_NATION Prussia while at war. Propose armistice at high war score. Sign harsh peace. Battle records carry over for next war.
6. **Turns 18-24:** Trade income from alliances (+400g/turn) funds massive armies.
7. **Turn 25+:** Re-declare war on weakened Prussia, starting with banked war score. Quick victory.

This exploits: no relation decay (BAL-2), no battle record clearing (BUG-2), trade income stacking (BAL-3), and COURT_NATION speed (BAL-1). **Fixing BUG-1, BUG-2, BAL-1, and BAL-2 together breaks this optimal path.**

---

## PART 9: PRIORITY RANKING

### Tier 1 — Fix Now (Broken Mechanics)

| # | Issue | Type |
|---|-------|------|
| BUG-1 | War score decay no-op | Code bug |
| BUG-2 | Battle records persist across wars | Code bug |
| BUG-3 | Counter-offer treated as rejection | Incomplete feature |
| BUG-6 | Treaty clause gold enforcement unimplemented | Incomplete feature |

### Tier 2 — Fix Soon (Major Design Issues)

| # | Issue | Type |
|---|-------|------|
| BUG-4 | Armistice expiration unimplemented | Incomplete feature |
| BUG-5 | Armistice cooldowns never written | Incomplete feature |
| BAL-1 | COURT_NATION too fast | Balance |
| BAL-2 | No relation decay | Balance |
| BAL-3 | Trade income snowball | Balance |
| GAP-3 | Player treaty cancellation (easy wire) | Missing command |
| GAP-5 | Player voluntary downgrade (easy wire) | Missing command |
| GAP-6 | AI-AI state visibility in ledger | Missing info |

### Tier 3 — Improve (Design Enhancement)

| # | Issue | Type |
|---|-------|------|
| GAP-1 | Player counter-offer terms | Major UX |
| GAP-2 | Player war declaration command | Missing command |
| GAP-4 | Acceptance score preview | Missing info |
| AI-1 | P3/P5 AI triggers deferred | AI behavior |
| AI-2 | Relation penalty dominates wartime | Formula balance |
| BAL-4 | Coalition stalemate duration | Balance |
| EDGE-1 | Alliance paradox — no player choice | Edge case |
| EDGE-2 | Ghost nation / no elimination | Edge case |

### Tier 4 — Polish (Nice to Have)

| # | Issue | Type |
|---|-------|------|
| GAP-7 through GAP-18 | Various info gaps and missing tools | UX |
| BAL-5 through BAL-10 | Various balance tweaks | Balance |
| AI-3 through AI-6 | AI behavior improvements | AI |
| Narrative items | Treaty ceremonies, vassal personality, CS drama | Feel |

---

## What Could Be Better (Design Aspirations, Not Bugs)

Carried forward from previous audit + expanded:

1. **Counter-offer mechanic needs player agency** — currently a black box algorithm. Player should specify counter-terms.
2. **Vassal loyalty feedback could be richer** — currently just numbers. No personality, no events, no story.
3. **Continental System should generate stories** — smuggling events, economic hardship, British countermeasures.
4. **Marriage alliances are the biggest historical gap** — Napoleon's most consequential diplomatic tool is absent.
5. **Template variety needs expansion** for 50+ turn games (especially VAGUE path stalemate templates).
6. **Talleyrand's long game** — he should have an evolving agenda, not just random sabotage rolls. Secret correspondence with foreign courts, positioning for a post-Napoleon future.
7. **Treaty signing ceremonies** — dramatic template when a major treaty is ratified.
8. **Multi-party peace conferences** — bilateral-only diplomacy misses the Congress dynamic.
9. **Diplomatic red lines and ultimatums** — coercive diplomacy is entirely absent.
10. **Diplomatic events should affect marshal morale** — declaring war should excite aggressive marshals, dismay cautious ones.
