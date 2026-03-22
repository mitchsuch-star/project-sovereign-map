# Diplomacy Design Audit — March 2026

**Date:** 2026-03-22
**Methodology:** 4 parallel code-review agents covering exploits/economics, AI behavior/dead mechanics, UX/feedback, and asymmetric rules. ~335k tokens of analysis across `diplomacy.py`, `ai_diplomacy.py`, `coalition.py`, `vassal.py`, `diplomatic_templates.py`, `diplomatic_advisory.py`, `diplomatic_ledger.py`, `diplomatic_defiance.py`, `enemy_ai.py`.

**Previous audit:** `DIPLOMACY_AUDIT_2026_03.md` (code bugs, 43 found/fixed, 112 tests). This audit focuses on **design-level** issues: exploitable mechanics, dead systems, AI blindness, UX confusion, and strategic imbalances.

---

## EXPLOITS (5 findings)

### E1. Threat Decay Gaming — Peace/War Cycling
**EXPLOIT — CRITICAL**
`coalition.py:139-165`

Threat decays -3/turn when at peace with multiple nations. Player can sign peace treaties (4 DP total cycle), farm decay for 5 turns (-15 threat), then re-declare war (+20 threat). Net cost: ~+5 threat per conquest cycle. No cooldown on re-declaring war against the same nation after armistice expires.

**Why real:** Player can conquer indefinitely without ever triggering coalition by spacing out wars. The 80-threat instant coalition becomes unreachable with disciplined play.

### E2. Vassal Investment Has No Cooldown
**EXPLOIT — MAJOR**
`vassal.py:598-652`

Cost: 1 DP + 200g for +10 loyalty. No cooldown. Loyalty decays -5 to -15/turn from various sources. Player can just re-invest every 2-3 turns indefinitely. With 5 DP/turn, player can maintain 4 vassals + still do diplomacy.

**Why real:** Vassal rebellion becomes a trivial gold tax rather than a strategic threat. The rebellion popup at loyalty 10 never fires if player invests mechanically.

### E3. No Treaty-Breaking Reliability Tracker for Player
**EXPLOIT — MAJOR**
`diplomacy.py:738-741, 1808-1931`

AI nations track `diplomatic_reliability` which penalizes acceptance of future proposals. Player has no equivalent tracker. Player can break treaties repeatedly with only a flat -10 to -20 relation penalty per break, which naturally drifts back.

**Why real:** Player can sign defensive alliances for threat decay benefits, break them when convenient, and face no cumulative reputation cost.

### E4. War Declaration → Treaty Spam Cycle
**EXPLOIT — MODERATE**
`diplomacy.py:914-1000`, `coalition.py:95-114`

Full war→peace cycle costs 4 DP (declare 1 + armistice 1 + peace 2). Player generates 5 DP/turn. Armistice has 5-turn minimum but no "can't re-declare within X turns" cooldown after peace is signed. Combined with E1, this creates a predictable conquest metronome.

### E5. Vassal Cession as Diplomatic Sweetener Loophole
**EXPLOIT — MODERATE**
`diplomacy.py:630-658`, `vassal.py`

Player can offer "return" of vassal home region as a treaty sweetener in acceptance formula, while retaining the vassal relationship and assimilated marshals. Appears magnanimous while maintaining strategic control.

---

## DEAD MECHANICS (8 findings)

### D1. Coalition Posture Is Cosmetic
**DEAD — CRITICAL**
`coalition.py:272-309`, `enemy_ai.py:5289`

`get_coalition_posture()` returns aggressive/defensive/cautious. Only affects `convergence_bias` (+12/+4/+0 movement toward France). Does NOT affect: attack thresholds, target selection, fortification decisions, retreat thresholds, or recruitment. An aggressive-personality marshal in a "cautious" coalition still charges at 1.4:1 odds.

**Why it matters:** Coalition posture is calculated every turn and shown in the ledger but creates zero behavioral difference in actual AI military decisions.

### D2. Diplomat Personality Is a ±5 Modifier in a ±100 System
**DEAD — MAJOR**
`diplomacy.py:577`, `ai_diplomacy.py:106-111, 983-989`

Hawk vs dove diplomat changes acceptance by ±5 points. War score alone swings ±50+. Relations swing ±30. Personality determines one trigger threshold (P1 fires at -60 for hawk vs -20 for dove) but this just means doves propose peace one time more per war. Replacing any personality with any other produces near-identical gameplay.

### D3. Trade Income Is Strategically Irrelevant
**DEAD — MAJOR**
`diplomacy.py:1519-1561`

Maximum trade income (4 ALLIANCE partners): ~350 gold/turn. Typical army upkeep: ~750 gold/turn. Single region conquest: 50-200 gold/turn forever. Diplomacy is mathematically inferior to conquest for income. The diminishing returns curve (1.0, 0.75, 0.50, 0.25) further punishes diplomatic play.

### D4. British Subsidy = ~10 Troops Per Coalition
**DEAD — MODERATE**
`coalition.py:325-369`

200g/turn to lowest-relation coalition member. Over an 8-10 turn coalition war, that's 1600-2000g total = ~10 infantry. Average marshal has 5000+ troops. The subsidy doesn't change AI recruitment decisions or target selection. Removing it entirely wouldn't change coalition behavior.

### D5. Coalition Friction Only Affects One Support Bonus
**DEAD — MODERATE**
`coalition.py:409-426`, `enemy_ai.py:5268-5272`

Friction multiplier (0.25-1.0 based on mutual relation) applies only to P4.75 ally-support movement bonus. Doesn't affect: attack decisions, coordination, target selection, or anything else. Two coalition members at -30 relation attack France with the same effectiveness as two at +40.

### D6. Advisory System Is Flavor Text
**DEAD — MODERATE**
`diplomatic_advisory.py:83-300`

Advisory conversations cost 0 DP, affect nothing mechanically, and give the same template regardless of advisor personality. No effectiveness tracking, no failure states, no strategic impact. It's a read-only information display dressed as dialogue.

### D7. Coalition Brewing Is Just a Countdown Timer
**DEAD — MODERATE**
`coalition.py:950-1062`

3-turn countdown between threat 60-79. During brewing: no behavior changes, no coordination, no diplomatic restrictions. Just a timer. Player gets perfect information about when coalition forms and can plan accordingly.

### D8. Treaty Upgrade Path Never Skips Steps
**DEAD — MINOR**
`ai_diplomacy.py:474-505`

AI always crawls PEACE → OPEN_BORDERS → NON_AGGRESSION → DEFENSIVE_ALLIANCE → ALLIANCE (1 step per proposal). Never skips tiers even when relation supports jumping. Takes 4+ turns minimum to reach alliance. Makes mid-tier treaties (OPEN_BORDERS, NON_AGGRESSION) feel like mandatory waiting rooms rather than strategic choices.

---

## AI BLINDNESS (5 findings)

### A1. AI Builds Proposals It Knows Will Be Rejected
**AI_BLIND — CRITICAL**
`ai_diplomacy.py:654-670`

P8 (winning, war_score > 40) builds harsh peace with gold demands. Then checks acceptance score < 20 and silently rejects its own proposal. No retry with softer terms, no alternative approach. AI stays silent when winning instead of demanding surrender.

**Why it matters:** Player never faces "accept terms or be destroyed" ultimatums. Coalition military dominance has no diplomatic translation.

### A2. AI Doesn't Consider Coalition Consequences of Peace
**AI_BLIND — MAJOR**
`ai_diplomacy.py:596-607`

P1 (losing badly) proposes peace instantly without checking: Am I in a coalition? Does peace break the alliance? Am I getting British subsidy? Are my allies counting on me? AI members defect from coalitions mid-war with zero strategic calculation.

### A3. War Exhaustion Invisible to AI Decision-Making
**AI_BLIND — MAJOR**
`coalition.py:465-478`, `diplomacy.py:600-605`

War exhaustion accumulates from casualties and applies -5 acceptance penalty per 50 WE. But AI decision logic (P1-P8 triggers) doesn't factor WE into proposal timing. AI can't anticipate "my WE is high, peace proposals become more acceptable next turn." AI defects from coalitions seemingly randomly.

### A4. Harsh Peace Gold Formula Is Self-Defeating
**AI_BLIND — MODERATE**
`ai_diplomacy.py:465-469`

Gold demand = `max(500, war_score * 8 * mult)`. At war_score 50, demand = 500g. This feeds into acceptance formula as ~-16 penalty. Combined with war-score positive bonus (+15 to +30), net is usually <20 = auto-rejected. The only "winning" proposal type is mathematically unusable.

### A5. AI-to-AI Proposals Lack Pre-Screening
**AI_BLIND — MINOR**
`ai_diplomacy.py:1370`

Player gets acceptance preview in wizard. AI builds proposals blind — no iterative improvement loop. Counter-offer system (M3) is sophisticated but only triggers on rejection, never proactively.

---

## UX MISMATCHES (3 findings)

### U1. Acceptance Component Labels Missing for 3 Military Factors
**UX_MISMATCH — MODERATE**
`diplomacy.py:2615-2632`

`military_supremacy`, `battlefield_diplomacy`, `military_pressure` (worth up to +25/+10/+15) have no entries in `_COMPONENT_LABELS`. They auto-generate as "Military Supremacy" instead of thematic descriptions. The `FEEDBACK_STRINGS` dict (line 189-204) has good descriptions but isn't wired to the wizard.

### U2. Armistice Cooldown Shows Different Reasons in Wizard vs Terminal
**UX_MISMATCH — MODERATE**
`diplomacy.py:2433`, `diplomatic_ledger.py:352-358`

Wizard shows "Declare War disabled" with "Insufficient DP" reason. Terminal shows "Armistice: X turns remaining." Two different messages for the same blocking condition depending on interface used.

### U3. Likelihood Descriptors Have Unclear Boundaries
**UX_MISMATCH — MINOR**
`diplomacy.py:2081-2098`

Score 49 = "Uncertain — may counter", score 50 = "Favorable". The 15-point "Unlikely" band (15-29) is too wide. Players can't intuit how close they are to threshold boundaries.

---

## SILENT EVENTS (5 findings)

### S1. DP Regeneration Is Completely Silent
**SILENT — HIGH**
`diplomacy.py:1486-1517`

DP resets every turn based on diplomat skill + authority + capital. No notification of: how much was generated, why it changed, or what factors affect it. If player loses capital (-1 DP/turn), they discover it by noticing the counter changed.

### S2. Relation Changes from Coalition/Reliability Have No Dispatch Events
**SILENT — HIGH**
`coalition.py:624` (coalition loyalty penalty), `diplomacy.py:2051-2074` (reliability decay)

Relations can drop -50 from coalition penalties or reliability decay with zero explanation. Player sees "Prussia hates us now" with no dispatch event explaining why.

### S3. Vassal Loyalty Warnings Only Fire at 10 (Too Late)
**SILENT — HIGH**
`vassal.py:307-330`

Rebellion imminent popup fires at loyalty ≤10. No warnings at 30, 20, or any intermediate level. A vassal at loyalty 45 losing -6/turn reaches rebellion in 6 turns with zero player feedback until the emergency popup.

### S4. War Exhaustion Is Never Displayed
**SILENT — MODERATE**
`coalition.py`, `executor.py`

War exhaustion affects acceptance formula but appears nowhere: not in morning dispatch, not in diplomatic ledger, not in battle reports, not in notifications. Players can't see why peace proposals are accepted/rejected based on WE.

### S5. Threat Accumulation History Lost
**SILENT — MODERATE**
`coalition.py:95-114`, `diplomatic_ledger.py:394-410`

Ledger shows "Threat sources this turn" but no cumulative history. Player can't see: "I'm at 55 threat, one more war declaration pushes me to 75 (brewing range)." Must do mental math from current value.

---

## ASYMMETRIC RULES (4 findings)

### R1. AI Pays Zero DP for Proposals
**ASYMMETRIC — CRITICAL**
`ai_diplomacy.py:526-658`

Player proposals cost 2-5 DP. AI proposals cost 0 DP. AI can spam proposals indefinitely (limited only by cooldowns). Player must budget scarce DP between proposals, investments, and war declarations.

### R2. Coalition System Only Targets Player Nation
**ASYMMETRIC — STRUCTURAL**
`coalition.py:144, 177, 193, 213, 252, 509, 698, 887`

All coalition functions hardcode `france = world.player_nation`. AI nations never accumulate threat, never face coalitions. Player military success self-limits; AI military dominance carries no equivalent penalty.

### R3. Talleyrand Sabotage Is Player-Only Risk
**ASYMMETRIC — MAJOR**
`diplomatic_defiance.py:165-249`

Player's diplomat can sabotage proposals (5-30% chance). AI diplomats have 100% fidelity — zero sabotage risk. One-way diplomatic risk that only affects player.

### R4. Acceptance Formula Has Player-Specific Threat Penalty
**ASYMMETRIC — MAJOR**
`diplomacy.py:617-620`

When France proposes: threat × -0.3 penalty. When AI proposes to non-France: threat × +0.2 bonus. When AI proposes to France: 0 modifier. Player's coalition threat actively sabotages their own diplomacy.

---

## Summary

| Category | Count | Critical | Major | Moderate | Minor |
|----------|-------|----------|-------|----------|-------|
| EXPLOIT | 5 | 1 | 2 | 2 | 0 |
| DEAD | 8 | 1 | 2 | 4 | 1 |
| AI_BLIND | 5 | 1 | 2 | 1 | 1 |
| UX_MISMATCH | 3 | 0 | 0 | 2 | 1 |
| SILENT | 5 | 3 (HIGH) | 0 | 2 | 0 |
| ASYMMETRIC | 4 | 1 | 2 | 0 | 0 |
| **Total** | **30** | **7** | **8** | **11** | **3** |

### Top 5 Design-Impacting Issues

1. **E1 + E4**: Threat decay gaming + war/peace cycling = coalition is avoidable. Removes core strategic pressure.
2. **D1 + D5**: Coalition posture + friction are cosmetic. Coalition fights like uncoordinated individuals.
3. **A1 + A4**: AI can't propose when winning. Removes diplomatic tension from military defeat.
4. **R1 + R2**: AI has no DP cost + coalition only targets player. Fundamental asymmetry in diplomatic pressure.
5. **D3**: Trade income irrelevant. Diplomacy has no economic incentive vs conquest.

### Notes on Intentional Asymmetries

Some asymmetries (R2, R3, R4) may be **intentional design** — the player is Napoleon, and the game is designed around France vs. Europe. Coalition targeting only France is historically accurate. Talleyrand sabotage is a character-specific mechanic. The threat penalty on French proposals reflects European suspicion of Napoleonic diplomacy.

These should be evaluated as design questions ("Is this fun?") rather than bugs ("Is this wrong?").
