# DIPLOMACY SPEC AUDIT RESULTS

> **Auditor:** Independent design review (Claude Code)
> **Spec Version:** DIPLOMACY_SPEC.md v2.0
> **Benchmark:** JEALOUSY_SPEC.md v3.1
> **Date:** February 27, 2026

---

## Overall Score: 58/80

## Grade: B (minor revisions, no structural issues)

> The spec's self-audit claimed 68/80 (Grade A). This independent audit scores 58/80 — a 10-point gap driven by underestimated implementation risk, incomplete implementation-level detail, historically inaccurate Metternich characterization, and player experience concerns around formula opacity. The spec is ambitious, historically grounded in most areas, and structurally sound. No CRITICAL exploits found. Revisions are achievable within 1-2 focused passes before implementation begins.

---

## Category Scores

| # | Category | Score | Self-Audit | Delta | Notes |
|---|----------|-------|------------|-------|-------|
| 1 | Internal Consistency | 7/10 | 8 | -1 | DP threshold contradiction, harshness formula underspecified |
| 2 | System Integration | 8/10 | 8 | 0 | Strong Building Blocks, good wiring. Missing dispatch/notification detail |
| 3 | Exploit Resistance | 8/10 | 9 | -1 | All major vectors blocked. Saxony Turn-1 vassalization and uncapped sweetener are minor gaps |
| 4 | Edge Cases | 8/10 | 9 | -1 | 34 existing cases is impressive. 15 additional found (below). Some cascade termination gaps |
| 5 | Historical Plausibility | 7/10 | 9 | -2 | Tilsit achievable, Continental System properly leaky, Talleyrand arc strong. **Metternich as "Dove" is historically inaccurate** — was a calculating opportunist (see Appendix A) |
| 6 | Player Experience | 7/10 | 8 | -1 | Good difficulty curve. Formula opacity may frustrate. 7+ information screens risk overload |
| 7 | Implementation Risk | 6/10 | 8 | -2 | Session 1 & 3 risk underestimated. Map expansion and parser routing are HIGH risk |
| 8 | Spec Completeness | 7/10 | 9 | -2 | War score inline is good. Missing: dispatch event types, notification templates, harshness algorithm, counter-offer algorithm, save migration plan |
| | **Total** | **58** | **68** | **-10** | |

---

## Critical Issues (MUST fix before implementation)

### C1: DP Authority Threshold Contradiction
**§4a** says `Authority >= 60: +1 bonus DP`. **§10c** (Integration Points) says `Authority > 80 → +1 DP`. These are different thresholds (60 vs 80). One is wrong. If 60 is correct (matches the worked example showing 4 DP at game start with authority ~100), then §10c must be fixed. If 80 is correct, then the game starts at 3 DP and the §4a worked example is wrong.

**Recommendation:** Fix §10c to say `Authority >= 60 → +1 DP` (matches the detailed specification in §4a and the worked example).

### C2: Harshness Formula Undefined
**§7b** introduces a `harshness` score: `(value_demanded - value_offered) / total_deal_value`. But `value_demanded`, `value_offered`, and `total_deal_value` are never defined algorithmically. How is the "value" of territory calculated? Of AP/turn? Of manpower? The Dove/Hawk personality modifiers depend on harshness thresholds (< 0.3, > 0.6), but without a value calculation, these thresholds are meaningless. Talleyrand's defiance also depends on harshness (§3b: `original_proposal.harshness > 0.7`).

**Recommendation:** Define a value table for each clause type (e.g., region = 500 value, 100g/turn = 300 value, 1000 cavalry = 200 value, 1 AP/turn = 1000 value). Then harshness can be calculated deterministically. This is implementation-blocking.

### C3: Session 1 Risk Severely Underrated
The spec rates Session 1 (Map Expansion) as **LOW RISK**. This is incorrect. Expanding from 13 to 19 regions:
- Changes every existing test that references specific regions, starting positions, or adjacency
- Breaks the AI decision tree (enemy_ai.py has hardcoded region references in P1-P8)
- Changes garrison combat (capital regions change)
- Alters supply attrition calculations (new region layout)
- Changes fog of war calculations (new adjacency patterns)
- Potentially breaks save compatibility entirely (13-region saves cannot load into 19-region world)

**Recommendation:** Rate Session 1 as **HIGH RISK**. Add a pre-session step: audit all hardcoded region references across the entire codebase. Estimate 100+ test updates. Plan for a save-breaking version bump.

---

## Major Issues (SHOULD fix before implementation)

### M1: Missing Dispatch Event Types
JEALOUSY_SPEC (benchmark) provides exact event type names: `jealousy_restlessness`, `jealousy_fired`, `jealousy_autonomous_warning`, etc. The DIPLOMACY_SPEC describes dispatch events in prose ("Morning Dispatch: Talleyrand reports...") but never enumerates event type strings for the dispatch whitelist. This forces the implementer to invent names.

**Recommendation:** Add a table like JEALOUSY_SPEC §11:

| Event Type | When | Template |
|---|---|---|
| `diplomatic_proposal_sent` | Talleyrand departs | "Talleyrand has departed for the {nation} court." |
| `diplomatic_proposal_returned` | Talleyrand returns | "Talleyrand returns from {nation} with a response." |
| `diplomatic_sabotage_discovered` | Sabotage detected | "Talleyrand altered your proposal to {nation}..." |
| `diplomatic_treaty_signed` | Treaty ratified | "{nation_a} and {nation_b} have signed a {type}." |
| `diplomatic_war_declared` | War declaration | "{nation} has declared war." |
| `diplomatic_vassal_unrest` | Loyalty < 40 | "Talleyrand reports unrest in {nation}." |
| `diplomatic_vassal_rebellion` | Loyalty = 0 | "{nation} has rebelled!" |
| `diplomatic_ai_proposal` | AI sends proposal | "A {nation} envoy has arrived." |
| `diplomatic_mission_progress` | Mission running | "Talleyrand's efforts in {nation} continue." |
| `diplomatic_mission_paused` | DP insufficient | "Talleyrand's efforts curtailed — insufficient resources." |

### M2: Missing Notification Templates
§13 (New Files) mentions `DIPLOMATIC_PROPOSAL, TREATY_SIGNED, SABOTAGE_DISCOVERED` notification types but doesn't specify priority levels or template strings. The existing notification system (per V2b) specifies these explicitly.

**Recommendation:** Enumerate all notification types with priority and template:
- `DIPLOMATIC_PROPOSAL` (HIGH): "{nation} envoy: {proposal_type}"
- `TREATY_SIGNED` (MEDIUM): "Treaty with {nation}: {type}"
- `SABOTAGE_DISCOVERED` (HIGH): "Diplomatic discrepancy detected"
- `VASSAL_REBELLION_IMMINENT` (HIGH): "{nation}: IMMINENT REBELLION"
- `VASSAL_REBELLION` (HIGH): "{nation} has broken free!"
- `ALLIANCE_CASCADE_WAR` (HIGH): "{nation} enters war via alliance"

### M3: Counter-Offer Generation Algorithm Undefined
§9b says AI generates counter-offers by "removes most expensive clause" or "adds a clause they want." Neither "most expensive" nor "what they want" is defined. The implementer must invent a valuation system for clause comparison and an AI desire model.

**Recommendation:** Define counter-offer generation explicitly:
1. Calculate per-clause acceptance impact (using deal_sweetener values from §6b)
2. Remove the single clause with the largest NEGATIVE impact on the AI
3. If still in counter-offer range: add the cheapest clause the AI would like (from a per-nation desire table derived from §6d special bonuses)
4. Present the modified package

### M4: Vassal Marshal Transition Mechanics Underspecified
When Saxony becomes a French vassal (PUPPET/SATELLITE), Reynier becomes player-controlled (§EC-K). But the spec doesn't specify:
- Does Reynier get a Trust value? (Existing marshals have Trust from game start)
- Does Reynier join `world.marshals` dict? (Golden Rule #3 requires this)
- Does Reynier maintain his existing relationships with other Saxony entities?
- What personality modifiers does Reynier use when player-controlled?
- Can Reynier be commanded to attack his former allies?

**Recommendation:** Add a "Vassal Marshal Assimilation" section specifying: Trust starts at 40 (reluctant service), joins `world.marshals`, existing relationships preserved, biography updated, personality unchanged, can attack former allies (loyalty to new lord is mechanical, not emotional).

### M5: Conflicting Alliance Obligations Not Addressed
If France allies with Prussia, but Prussia has an existing alliance with Britain (who France is at war with), what happens? Does Prussia have to choose? Does the France-Prussia alliance override the Britain-Prussia alliance? This is the most historically significant diplomatic scenario (Napoleon constantly tried to separate coalition members) and it's not specified.

**Recommendation:** Add an explicit rule: "A nation cannot maintain ALLIANCE or DEFENSIVE_ALLIANCE with two nations that are at WAR with each other. When a new alliance creates this conflict, the nation must choose which alliance to maintain (AI: choose the alliance with the higher-relation partner; Player: confrontation popup)."

### M6: Session 3 Risk Underrated
Session 3 modifies **parser.py, executor.py, llm_client.py, enemy_ai.py, and main.py** — the five most critical files in the backend. Adding diplomat-vs-marshal routing to the parser is novel code with high regression risk. The spec rates this MEDIUM; it should be HIGH.

**Recommendation:** Rate Session 3 as HIGH. Consider splitting into Session 3a (parser routing + basic execution, no AI) and Session 3b (AI proposals + popup flow).

### M7: No Save Migration Plan
The map expansion from 13 to 19 regions is a save-breaking change. Old saves reference regions that no longer exist at the same coordinates, have different adjacency, and lack the new nations. The spec says nothing about save compatibility.

**Recommendation:** Add a "Save Compatibility" section stating: "Phase 8 is save-incompatible with Phase 7 saves. Old saves cannot be loaded. Increment save format version. Add version check in save_manager.py that rejects pre-Phase-8 saves with a clear error message."

### M8: AI-AI Diplomacy Scope Conflict
§9c describes AI-AI diplomacy as a core system ("makes the world feel alive"). The Session Plan defers it to Session 6 (Polish). But the Walking Skeleton (§14) doesn't include it either. The spec needs to decide: is AI-AI diplomacy part of the core experience or polish? If core, it belongs in Sessions 3-5. If polish, §9c should be marked as deferred.

**Recommendation:** Mark §9c as DEFERRED TO SESSION 6 explicitly. Add a note that the Walking Skeleton plays without AI-AI diplomacy — nations only interact with the player. This is acceptable for initial playtesting.

---

## Minor Issues (CAN fix during implementation)

### m1: §4a Authority Annotation Misleading
§4a says "authority ~60" in the game-start example. Authority starts at 100 (per existing system). The bonus triggers at ≥60, and the result (4 DP) is correct, but "~60" suggests that's the starting authority value.

### m2: Starting Economy Table Incomplete
§1d economy table shows region income + upkeep but doesn't include trade income from starting PEACE relationships. France at PEACE with Austria (+50 bilateral) and Saxony (+50 bilateral) = +100g/turn additional income not reflected in the table.

### m3: Vassal Courting Not Assigned to Session
§8e says "APPROVED: Include in v1 (simplified form)" for enemy nations courting player vassals. But the Session Plan (§14) doesn't assign vassal courting to any specific session scope. It would logically be Session 4 but isn't listed.

### m4: Continental System Participation Check Underspecified
§5d says participation requires "acceptance formula check each turn" but doesn't specify which formula parameters apply. Is this the full §6 acceptance formula or a simplified version? What's the base disposition for "continue participating"? How do deal_sweetener and personality_modifier apply to a non-proposal action?

### m5: War Score "Starting Regions" Source Undefined
§6e territory score uses "enemy starting region currently held by you." How are "starting regions" defined? Per the initial §1b table? Reconstructed from static data? If a region changes hands multiple times, does it still count as a "starting region"? JEALOUSY_SPEC §9b addresses this for enemy home regions; diplomacy spec should reference the same pattern.

### m6: DiplomaticRepresentative to_dict/from_dict Not Specified
§13 shows the class definition and says "Serialization: to_dict() / from_dict() required" but doesn't show the implementation pattern (unlike JEALOUSY_SPEC §12 which provides exact field lists with types and defaults for every new field).

### m7: Godot int() Wrapping Not Mentioned
Golden Rule #2 ("All numbers to Godot: int()") is not referenced anywhere in the spec. New numeric fields (DP, relations, war score, loyalty, threat level) all need int() wrapping before API responses. Should be noted in §14 under implementation patterns.

### m8: Nation-Level Relations vs Marshal-Level Relationships
The spec introduces nation-level relations (§1e, range -100 to +100) which are conceptually separate from marshal-level relationships (range -2 to +2, existing system). The naming similarity could cause confusion during implementation. Consider explicitly distinguishing them: "nation relations" vs "marshal relationships" consistently throughout.

---

## Exploits Found

| # | Exploit | Severity | Spec Blocks? | Fix |
|---|---------|----------|-------------|-----|
| E1 | Treaty-break-repropose loop | LOW | Yes (relation math self-corrects) | — |
| E2 | Armistice chaining | LOW | Yes (§5b.2 cooldown) | — |
| E3 | Turn-1 Saxony vassalization | **MEDIUM** | Partially (intentional for Saxony?) | Consider requiring at least OPEN_BORDERS state before vassalage proposals, OR require war score > 0 for treaty vassalage, OR add "first diplomatic contact" delay |
| E4 | Uncapped deal sweetener | **MEDIUM** | Partially (gold scarcity) | Add explicit cap: max +30 from all sweetener clauses combined |
| E5 | Alliance flip-flop | LOW | Yes (severe penalties) | — |
| E6 | Decisive battle farming | LOW | Yes (±20 cap per war) | — |
| E7 | Defiance avoidance at max stats | LOW | Designed (2% floor) | Consider raising floor to 5% for more gameplay visibility |
| E8 | Free protection guarantee | LOW | Contextual | Reduce protection bonus (+5 → +3) when guarantor is already at war with all of target's enemies |
| E9 | Trade income cycling | LOW | No exploit (monotonic) | — |
| E10 | Continental System overstack | LOW | Capped (200g total) | — |
| E11 | Post-treaty-break state ambiguous | LOW | Undefined | Clarify: breaking treaty returns to PEACE (or WAR for armistice) |

---

## Edge Cases Identified

The spec covers 34 edge cases (EC-A through EC-HH). Below are 15 additional:

| # | Edge Case | Recommended Resolution |
|---|-----------|----------------------|
| EC-1 | **Player cedes Paris in a treaty.** Can the player voluntarily give up their capital? | Allow with EXTREME Talleyrand objection. If ceded: -1 DP permanent, skill -2 until recaptured. Relocation of Talleyrand to nearest French city. |
| EC-2 | **Cross-proposal (France→Prussia while Prussia→France simultaneously).** | First-to-resolve wins. If both in transit same turn: merge into single negotiation with both proposals visible. Higher-DP-cost proposal takes priority. |
| EC-3 | **Vassal marshal transition (Reynier becomes player-controlled).** | See M4 above. Trust 40, joins world.marshals, personality preserved, relationships reset to Professional(0) with all French marshals. |
| EC-4 | **Breaking armistice (declaring war during armistice).** | Treat as treaty-break: -30 relation target, -10 all, +15 threat. Plus -20 additional "armistice violator" penalty (breaking a ceasefire is worse than breaking a trade deal). |
| EC-5 | **French treaties apply to vassal territory?** | Yes. France's OPEN_BORDERS with Austria applies to Saxony (French vassal). But PUPPET/SATELLITE vassals can't independently grant military access. AUTONOMOUS vassals can. |
| EC-6 | **Nation goes bankrupt (gold < 0) from treaty obligations.** | Gold floor at 0. If a nation cannot pay a gold/turn clause: clause defaults, -5 relation, treaty clause auto-suspended (Morning Dispatch: "{nation} has defaulted on payments"). |
| EC-7 | **Mission target declares war on France.** | Mission auto-cancels. Morning Dispatch: "Talleyrand's courtship of Austria is moot — they have declared war." DP investment lost. |
| EC-8 | **Decisive battle records after peace + re-war.** | Records persist in world.decisive_battles for Diplomatic Ledger display (historical record). But per-war decisive_bonus counter resets to 0 for war score calculation (EC-W). |
| EC-9 | **Conflicting alliance obligations (France allies Prussia while Prussia allies Britain, France at war with Britain).** | See M5 above. The conflicting nation must choose. Cannot maintain alliances with two nations at war with each other. |
| EC-10 | **Continental System member conquered by Britain.** | Conquered nation exits Continental System automatically. continental_system_members list updated when nation sovereignty changes. |
| EC-11 | **Talleyrand sabotage produces better outcome (player wanted harsh, Talleyrand softened, target accepted).** | This is a "successful sabotage." Discovery confrontation still fires. Player choice: confront (trust -10, "I didn't want peace on THOSE terms") or overlook (trust +3, sabotage validated). The key insight: the player may DISAGREE with a good outcome if it wasn't their intent. |
| EC-12 | **All vassals deteriorate simultaneously from military losses.** | This is intended. Lord losing wars: -2 per loss per vassal per turn. Multiple vassals amplify the consequences of military failure. The cascade risk is the price of empire. |
| EC-13 | **DP generation drops below mission cost.** | §EC-S already covers auto-pause. Add: when DP generation drops, Morning Dispatch warns on the turn BEFORE the first mission pause: "Talleyrand warns: our diplomatic capacity is declining. Current mission may be interrupted." |
| EC-14 | **Defensive alliance cascade creates infinite loop.** | Add termination condition: each nation processes alliance cascade once per war declaration. A nation already processed (already at war or already checked) is skipped. Prevents A→B→C→A loops. |
| EC-15 | **Continental System member's sovereignty changes (conquered, vassalized, etc.).** | Membership is per-sovereign-nation. Conquered regions don't participate. Vassalized nations: PUPPET/SATELLITE auto-join if lord is in Continental System. AUTONOMOUS: independent choice (relation check). |

---

## Top 3 Strengths

### 1. Historically Grounded Design
The acceptance formula, with its Military Supremacy modifier, produces historically plausible outcomes. The Treaty of Tilsit is achievable through the same conditions that produced it historically (crushing military victory + hold capital). The Continental System leaks. Britain can't be conquered. Talleyrand sabotages from within. The design team clearly studied the period.

### 2. Building Blocks Principle Rigorously Applied
The same acceptance formula evaluates both player and AI proposals. AI nations generate DP using the same formula. AI diplomatic behavior uses the same costs and cooldowns. There are no AI cheats. This is the standard the JEALOUSY_SPEC also met, and it's essential for player trust in the system.

### 3. Exploit Resistance After v2.0 Audit
The self-audit revision addressed the major exploit vectors: armistice chaining (5-turn cooldown), proposal spam (symmetrical cooldowns), PUPPET extraction (doubled drift), Continental System (200g cap), and Talleyrand nullification (2% Schemer floor). No CRITICAL exploits remain. The remaining MEDIUM-severity findings (Turn-1 Saxony, uncapped sweetener) are balance questions, not system-breaking.

---

## Top 3 Weaknesses

### 1. Implementation-Level Detail Gaps (vs JEALOUSY_SPEC benchmark)
Compared to the JEALOUSY_SPEC, which provides exact event type names, explicit field-by-field serialization patterns, and precise timing for every evaluation point, the DIPLOMACY_SPEC leaves several algorithms undefined: harshness calculation, counter-offer generation, Continental System participation check, and the value tables underlying deal sweeteners. An implementer would need to invent these, which means the spec isn't fully deterministic despite claiming to be.

### 2. Session 1 & 3 Implementation Risk
The map expansion (13→19 regions) touches the foundational data model. The parser routing change (diplomat vs marshal) touches the core command pipeline. Both are rated LOW-MEDIUM in the spec but should be HIGH. An implementation that underestimates these will burn sessions on regression fixes rather than new features.

### 3. Metternich Mischaracterized as "Dove"
Historical research confirms Metternich was NOT a dove. He was a calculating realist who used armed neutrality, played both sides simultaneously, and timed Austria's entry into the Sixth Coalition for maximum impact. His "armed mediation" at Dresden (1813) — where he presented deliberately harsh terms, secretly committed to the Allies, and waited for Napoleon to reject — is the opposite of dovish behavior. A more accurate personality type would be **Schemer** (like Talleyrand) or a new type: **Calculator/Opportunist** — someone who delays to build leverage, joins the winning side, and maximizes Austria's position regardless of outcome. The current "Dove" label gives Austria an unearned +10 on peace/alliance proposals, which is historically backwards — Metternich used diplomacy as a weapon, not as a path to peace.

### 4. Player Formula Opacity
The acceptance formula has 7 components with different scales and signs. The player never sees this math. Talleyrand's "assessment" provides flavor but not actionable feedback. When a proposal fails, the player knows it failed but not WHY or HOW to improve it. This may lead to trial-and-error frustration. The JEALOUSY_SPEC provides Berthier pre-warnings that give the player agency to prevent problems; the DIPLOMACY_SPEC needs an equivalent mechanism for diplomatic feedback.

---

## Recommendations (ordered by priority)

1. **Define the harshness value table (C2).** This blocks Talleyrand's defiance, Dove/Hawk personality modifiers, and treaty evaluation. Cannot be deferred.

2. **Fix the DP threshold contradiction (C1).** Simple fix — update §10c to match §4a.

3. **Upgrade Session 1 risk rating to HIGH (C3).** Add a pre-session codebase audit of hardcoded region references. Estimate test migration scope. Plan for save-breaking version bump.

4. **Add dispatch event type table (M1).** Follow JEALOUSY_SPEC pattern exactly.

5. **Add notification templates with priorities (M2).** Follow existing notification system pattern.

6. **Define counter-offer generation algorithm (M3).** Must be deterministic for Building Blocks compliance.

7. **Specify vassal marshal transition mechanics (M4).** Trust, relationship, and dict membership.

8. **Add conflicting alliance resolution rule (M5).** This is the most historically significant diplomatic scenario and it's unaddressed.

9. **Add deal sweetener cap of +30 (E4).** Simple, prevents edge-case gold dumping.

10. **Consider adding acceptance formula feedback.** Talleyrand's assessment should include one specific actionable hint: "Relations are too hostile" or "They fear our military strength" — mapping to the largest negative component in the formula. This gives the player a direction without revealing the math.

11. **Mark AI-AI diplomacy as explicitly deferred (M8).** Remove ambiguity about Walking Skeleton scope.

12. **Add save migration plan (M7).** Even if it's just "old saves incompatible, version check added."

---

## Comparison to JEALOUSY_SPEC (Benchmark)

| Dimension | JEALOUSY_SPEC v3.1 | DIPLOMACY_SPEC v2.0 | Gap |
|-----------|--------------------|--------------------|-----|
| Formula precision | Exact thresholds, worked examples | Exact formula but missing harshness/value tables | DIPLOMACY needs value tables |
| Event types | Enumerated with exact strings | Described in prose | DIPLOMACY needs enumeration |
| Serialization | Field-by-field with types and defaults | Fields listed but new class (Diplomat) underspecified | Minor gap |
| Edge cases | ~20, all with explicit resolutions | 34 + 15 found, most with resolutions | DIPLOMACY ahead on quantity |
| Implementation sessions | 3+1, risk-rated, gates defined | 5+1, risk-rated but underestimated | DIPLOMACY needs risk re-rating |
| Walking skeleton | Clearly defined, playtest-able | Clearly defined, playtest-able | Comparable |
| Building Blocks | Enemy jealousy with authority proxy | AI same formula, same costs | Comparable |
| Deferred items | Explicit table with impact | Explicit table with impact | Comparable |
| Historical grounding | Detailed marshal-by-marshal references | Strong nation-level grounding | Comparable |
| Player feedback | Berthier pre-warnings give agency | Talleyrand assessment gives flavor, not direction | DIPLOMACY needs actionable feedback |

---

*Audit complete. The spec is solid at B-grade (58/80). The 13 recommendations above — particularly C1-C3 and M1-M5 — would bring it to A-grade territory (65+). No structural rework needed. The design is historically authentic, exploit-resistant, and well-integrated with existing systems. Implementation can begin after addressing the Critical and Major issues.*

---

## Appendix A: Historical Verification Results

Independent historical research was conducted across 35+ sources to validate the spec's claims. Key findings:

### Treaty Verification (Acceptance Formula Stress Test)

| Treaty | Historical Context | Spec Formula Prediction | Match? |
|--------|-------------------|------------------------|--------|
| **Tilsit (Prussia, 1807)** | Jena/Auerstedt destroyed army, Berlin held, Friedland decisive win. Prussia lost ~50% territory, 154.5M franc indemnity, army capped at 42k. | War score ~90 (territory+battles+decisive+capital). Base 30 + war_score 27 + supremacy 25 + skill 8 = 90 (before relation penalty). Even at -60 relation: **60 → ACCEPT**. | YES — dictated peace achievable |
| **Pressburg (Austria, 1805)** | Austerlitz decisive. Austria lost Venetia, Tyrol. 40M franc indemnity. | War score ~70 (decisive+capital contested). Base 30 + war_score 21 + supremacy 25 + skill ~6 = 82 (before relation). | YES — harsh terms achievable |
| **Schönbrunn (Austria, 1809)** | Wagram decisive but costly. Harsher than Pressburg. 85-400M franc indemnity. | War score ~60 (one loss at Aspern-Essling, one decisive win at Wagram). Base 30 + 18 + no supremacy (capital not held for full war) = lower. Would need territory concessions and sweetener. | PLAUSIBLE — requires additional leverage |

**Conclusion:** The Military Supremacy modifier (§6b.1) is essential and historically validated. Without it, Tilsit-type dictated peace is impossible. The formula produces historically plausible outcomes across all three tested treaties.

### Talleyrand Arc Verification

| Spec Claim | Historical Reality | Match? |
|------------|-------------------|--------|
| "Course correction, not betrayal" (§3b) | Debatable. Talleyrand accepted bribes from Austria and Russia while Foreign Minister. At Erfurt (1808), he secretly coached Tsar Alexander against Napoleon. But he consistently framed his actions as serving France's long-term interests. | PARTIALLY — spec slightly understates the betrayal element. Bribery-for-intelligence is more treasonous than "course correction" |
| Starting trust 55 (§2b) | Napoleon suspected Talleyrand but kept him close. The famous "shit in a silk stocking" tirade (Jan 1809) occurred after discovery of succession plotting, yet Napoleon still didn't arrest him. | GOOD FIT — reflects mutual dependency despite suspicion |
| Defiance increases as authority drops (§3a) | Talleyrand became more active after the Spanish adventure (1807-08), which marked the shift from consolidation to overextension. Peak betrayal (Erfurt) coincided with peak overextension. | EXCELLENT FIT — authority decline → increased sabotage is historically exact |
| 2% Schemer minimum floor (§3a) | Even at Napoleon's peak, Talleyrand was quietly positioning. He resigned as Foreign Minister in August 1807 (peak authority period). | GOOD FIT — Talleyrand was never fully tamed, even during French dominance |

### Metternich Characterization

| Spec Claim | Historical Reality | Match? |
|------------|-------------------|--------|
| "Dove" personality (§2a-2b) | Metternich was a calculating realist. He arranged Napoleon's marriage to Marie Louise (1810) as a stalling tactic. His "armed mediation" (1813) was a deliberate trap — he presented harsh terms, secretly committed to the Allies, and waited for Napoleon to reject them. He chose Austria's moment to strike for maximum leverage. | **POOR FIT** — "Dove" significantly undersells Metternich's strategic cunning |
| Skill 8 | Metternich was among the greatest diplomats in European history. He outmaneuvered Napoleon at Prague, managed Austria's transition from French ally to coalition leader without provoking premature war, and dominated the Congress of Vienna. | GOOD FIT — skill 8 is appropriate |
| +10 on peace/alliance, -10 on harsh demands | Metternich's harsh terms at Dresden (1813) were deliberately designed to be rejected. He used peace proposals as weapons. A Dove's -10 on harsh demands would penalize historically accurate Metternich behavior. | **POOR FIT** — Metternich should not be penalized for harsh demands |

**Recommendation:** Replace Metternich's personality with either: (a) A new type — **Opportunist** (bonuses to proposals when the target is weakened, penalties when the target is strong; represents Metternich's preference for acting from leverage), or (b) **Schemer** with different flavor text (Austria's Schemer is strategic rather than self-serving). This is a balance concern, not just a flavor concern, because the Dove +10/-10 modifiers directly affect the acceptance formula for the most important swing state in the game.

### Saxon Loyalty Verification

| Spec Claim | Historical Reality | Match? |
|------------|-------------------|--------|
| Relation +40 "French-leaning" (§1e) | Saxony was one of Napoleon's most loyal German allies. Frederick Augustus I joined the Confederation of the Rhine in 1806, committed 20k troops, and refused to break with Napoleon even in 1813. Saxon troops defected during Leipzig — but this was a battlefield decision by commanders, not the king. | EXCELLENT FIT |
| "Open to alliance/vassalage" (§1a) | Saxony functionally WAS a French vassal state via the Confederation of the Rhine. They administered the Duchy of Warsaw on Napoleon's behalf. | EXCELLENT FIT |
| Prussia covets Saxony (§6d, +10 bonus) | At the Congress of Vienna, Prussia demanded ALL of Saxony. The crisis nearly caused a war between the victorious allies (Austria/Britain/France vs Prussia/Russia). Prussia received only 40% of Saxony in the compromise. | EXCELLENT FIT — if anything, +10 is conservative |

### Continental System Verification

| Spec Claim | Historical Reality | Match? |
|------------|-------------------|--------|
| Cap at 200g, Britain retains 100g minimum (§5d) | British exports fell 14-25% at peak impact, but global trade compensated. The system hurt Napoleon's allies more than Britain. Britain's average exports actually ROSE from 25.4M to 35M pounds/year between the decades. | EXCELLENT FIT — the cap reflects historical ineffectiveness |
| Nations may refuse each turn (§5d) | Holland refused (annexed 1810). Russia refused (1810, triggering 1812 invasion). Portugal refused (triggering 1807 invasion). | EXCELLENT FIT — compliance was always tenuous |
| Relation requirement: France > +10, Britain < +30 (§5d) | Nations participated based on French military pressure AND genuine anti-British sentiment (or lack thereof). | GOOD FIT — though military threat was the primary driver, not diplomatic relations |

### Coalition Formation Patterns

| Spec Claim | Historical Reality | Match? |
|------------|-------------------|--------|
| Threat level feeds coalition formation (§5c) | Each French conquest raised threat: Austerlitz → Third Coalition collapse but seeds Fourth. Jena → Prussia destroyed but Russia fights on. Wagram → Austria beaten but plots comeback. Russia 1812 → cascade formation of Sixth Coalition. | EXCELLENT FIT |
| Britain is the constant (§1a, always at WAR) | Britain was at war with France from 1793-1802 and 1803-1815, with only a 14-month peace (Amiens). Britain financed every coalition with subsidies of 1.25M pounds per 100,000 troops/year. | EXCELLENT FIT |

### Vassal Patterns

| Spec Claim | Historical Reality | Match? |
|------------|-------------------|--------|
| PUPPET: -4/turn drift, needs garrison (§8b) | Westphalia (Jerome Bonaparte) required constant French military presence. Conscription revolts. Of 25,000 sent to Russia, only 600 returned. | GOOD FIT |
| AUTONOMOUS: +1/turn drift (§8b) | Bavaria managed its own affairs, stayed loyal for years, but defected first (Treaty of Ried, Oct 1813) when the opportunity arose. | PARTIAL FIT — autonomy didn't prevent defection, but it delayed it |
| Cascade rebellion (§8d, -10 per rebellion) | Bavaria's defection (Ried) triggered a cascade. Württemberg, Saxony, and others defected at Leipzig within days. | EXCELLENT FIT |

### Bernadotte at Jena Verification

The spec uses this as the inspiration for the jealousy system's Aggressive autonomous attack. Historical research confirms: the order was genuinely ambiguous (Berthier's postscript was discretionary), but Bernadotte's personal rivalry with Davout is widely considered a contributing factor. Napoleon reportedly drew up court-martial papers but withdrew them. The incident is appropriately modeled as jealousy-contributed disobedience rather than pure insubordination.

---

## Appendix B: Historical Design Suggestions

Based on the research, the following design additions would improve historical plausibility without expanding scope:

1. **British subsidy mechanic:** Britain historically financed coalitions. Consider adding a treaty clause where Britain offers gold/turn to coalition partners as an AI diplomatic behavior (Britain spends gold to improve relations and encourage war declarations against France). This is already partially modeled by trade income from alliances but could be more explicit.

2. **Vassal defection cascade timing:** Historically, vassals defected at the tipping point (Leipzig), not gradually. Consider adding a "tipping point" threshold: when France's war score drops below -30 against ANY enemy, all vassals with loyalty < 50 make a simultaneous loyalty check. This would create a dramatic "the empire crumbles" moment rather than slow individual rebellions.

3. **Metternich's "armed mediation":** The current Dove personality doesn't capture Metternich's signature move — using peace negotiations as a delay tactic while rearming. Consider a Dove (or Opportunist) ability: "If peace negotiation fails, the proposing nation gains +5 to their next war declaration's coalition bonus." This captures how Metternich used failed peace talks as a casus belli.

4. **Escalating treaty harshness:** Historically, each successive treaty against the same nation was harsher (Pressburg 1805 < Schönbrunn 1809). Consider a modifier: "If target nation was previously defeated (had a treaty imposed), acceptance of harsh terms is +5 easier." This creates the historical pattern where breaking a nation once makes it easier to break again.
