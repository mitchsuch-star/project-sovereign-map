# Diplomacy Refinement & Cleanup

> **Created:** March 4, 2026
> **Status:** IN PROGRESS — Design phase
> **Source:** `docs/DIPLOMACY_CREATIVE_AUDIT.md` (5-agent creative audit, 7.8/10 overall)
> **Process:** Design gate approval → Implementation (possibly multi-session)
> **Next phase:** "Finish Design on Diplo Refinement & Cleanup" → then implementation sessions

---

## How This Works

1. Items marked **NEEDS DESIGN** require user approval before coding
2. Items marked **DONE** were fixed during the audit session
3. Items are ranked by overall value: gameplay impact × feasibility × fun improvement
4. Bug cross-references map to `DIPLOMACY_CREATIVE_AUDIT.md` PART 1

## Bug Cross-Reference (Audit → Refinement)

| Audit Bug | Severity | Refinement Item | Status |
|-----------|----------|-----------------|--------|
| BUG-1: War score decay no-op | CRITICAL | R1a | NEEDS DESIGN |
| BUG-2: Battle records persist across wars | CRITICAL | R1b | NEEDS DESIGN |
| BUG-3: Counter-offer treated as rejection | CRITICAL | R2 | NEEDS DESIGN |
| BUG-4: Armistice expiration unimplemented | HIGH | R5a | NEEDS DESIGN |
| BUG-5: Armistice cooldowns never written | HIGH | R5b | NEEDS DESIGN |
| BUG-6: Treaty clause gold unenforced | HIGH | R3 | NEEDS DESIGN |
| BUG-7: Treaty clause gold no floor | MEDIUM | R3 (included) | NEEDS DESIGN |
| BUG-8: Defensive alliance base disposition | MEDIUM | R7 | NEEDS DESIGN |
| BUG-9: Talleyrand sabotage/redemption popups unresolvable | CRITICAL | R37 | NEEDS DESIGN |
| BUG-10: Talleyrand proposal terms show "war score 0" | MEDIUM | R38 | NEEDS DESIGN |
| BUG-11: DP not visibly displayed in game | INVESTIGATION | R39 | NEEDS DESIGN |
4. Implementation phase will work through approved items, possibly across multiple sessions

---

## DONE (Fixed During Audit Session)

| # | Item | What Was Done |
|---|------|---------------|
| GAP-3 | **Player treaty cancellation command** | Wired `break_treaty()` to executor, parser, mock parser, validation. Keywords: "break treaty", "cancel treaty", "renounce treaty", "end treaty", "abrogate". 1 DP cost. |
| GAP-5 | **Player voluntary downgrade command** | Wired `execute_downgrade()` to executor, parser, mock parser, validation. Keywords: "downgrade", "reduce commitment", "step down", "withdraw from", "lower relations", "cool relations". 1 DP cost. |
| GAP-6 | **AI-AI diplomatic states in ledger** | Added `ai_relations` field to each nation in diplomatic ledger nations tab. Shows AI-AI states fog-filtered (PARTIAL+ intel on either nation). |

All 5290 tests pass after changes. 5 files modified, 106 lines added.

---

## RANK 1 — War Score & Battle Record Fixes (CRITICAL bugs, clear fix)

### R1a: War Score Decay No-Op — NEEDS DESIGN

**Problem:** `recalculate_war_scores()` overwrites decay every turn. Battle records from turn 5 still contribute +3 at turn 50.

**Proposed fix:** Prune battle records older than 10 turns in `apply_war_score_decay()`. Records older than 10 turns are removed from `world.battle_records[diplo_key]`. This makes the battle component time-sensitive — recent victories matter, old ones fade.

**Alternative:** Apply a decay multiplier — records from N turns ago contribute `3 * max(0, 1 - (age / 15))` instead of flat 3. Gradual fade vs hard cutoff.

**Example:**
```
Turn 5: Win battle vs Prussia (+3 battle score)
Turn 10: Still contributing +3 (5 turns old, under 10)
Turn 16: Pruned (11 turns old, over 10). Battle score drops.
Decisive battles: same 10-turn pruning (no special exemption)
```

### R1b: Battle Records Persist Across Wars — NEEDS DESIGN

**Problem:** Peace → re-declare war → start with old battle score banked.

**Proposed fix:** Clear `battle_records[diplo_key]` and `decisive_battles[diplo_key]` when transitioning OUT of WAR state (in `_ratify_treaty()` or `diplomacy.py` state transition code).

**Example:**
```
Turn 5: France wins 4 battles vs Prussia (+12 battle score)
Turn 8: Peace signed. battle_records["France|Prussia"] cleared.
Turn 12: War re-declared. War score starts at 0. Fresh war, fresh scorecard.
```

---

## RANK 2 — Counter-Offer System (Most impactful UX fix)

### R2: Player Counter-Offer Treated as Rejection — NEEDS DESIGN

**Problem:** Acceptance scores 30-49 are stubbed as REJECT. The most interesting diplomatic outcome (negotiation) is completely broken.

**Proposed fix (two-part):**

**Part A — Backend:** When `calculate_acceptance()` returns score 30-49, run the M3 counter-offer algorithm (`generate_counter_offer()` already exists in `ai_diplomacy.py`). Return the modified terms in the dialogue popup data so the player sees: "Original terms vs. Their counter-terms."

**Part B — Player choice:** The popup offers:
- **[Accept Counter]** — Ratify their version (0 DP, per spec §2d)
- **[Reject]** — Walk away (relation -5, cooldown starts)
- **[Renegotiate]** — Costs 1 DP, Talleyrand departs again with player's original terms adjusted

This matches the existing spec §2d exactly — the code just never implemented it.

**Stretch (GAP-1):** Let the player specify counter-offer terms manually instead of re-sending originals. Opens clause-selection in the renegotiate path. Much harder — requires a new command flow.

---

## RANK 3 — Treaty Clause Gold Enforcement (Critical missing mechanic)

### R3: Treaty Clause Gold/Turn Never Transfers — NEEDS DESIGN

**Problem:** `# TODO: Session 3` — gold-per-turn treaty clauses are stored but never enforced. Every financial clause is meaningless.

**Proposed fix:** In `advance_turn()`, after trade income processing, iterate `world.active_treaties` and transfer gold-per-turn amounts between nations. Add gold floor check (nation gold cannot go below 0 from treaty obligations — if can't pay, treaty violation event fires).

**Example:**
```python
# In advance_turn, after trade income:
for treaty in world.active_treaties:
    for clause in treaty.get("clauses", []):
        if clause["type"] == "gold_per_turn":
            from_nation = clause["from"]
            to_nation = clause["to"]
            amount = int(clause["amount"])
            available = max(0, world.nation_gold.get(from_nation, 0))
            transfer = min(amount, available)
            world.nation_gold[from_nation] -= transfer
            world.nation_gold[to_nation] += transfer
            if transfer < amount:
                # Treaty violation — can't pay
                queue_dispatch_event(world, "treaty_obligation_failed", ...)
```

Also add gold floor: `world.nation_gold[nation] = max(0, ...)` in `_process_treaty_clauses`.

---

## RANK 4 — Relation Decay & COURT_NATION Speed (Breaks dominant strategy)

### R4a: No Relation Decay — NEEDS DESIGN

**Problem:** Relations never drift. Once at +100, stays forever. Zero-maintenance diplomacy after turn 10.

**Proposed fix:** Add passive relation decay of -1/turn toward 0 for relations > +10 or < -10. Skip pairs where an active diplomatic mission targets them. Skip vassal pairs (vassal loyalty is separate).

**Example:**
```
France-Austria at +50, no active mission → +49 next turn
France-Austria at +50, IMPROVE_RELATIONS targeting Austria → stays +50 (mission counteracts)
France-Prussia at -40, no mission → -39 next turn (drift toward 0)
```

This means alliances require ongoing diplomatic attention — REASSURE_ALLY mission (1 DP/turn, +3 relation) becomes essential to maintain high relations.

### R4b: COURT_NATION Too Fast — NEEDS DESIGN

**Problem:** +12 relation/turn with Talleyrand. Austria flips in 6 turns.

**Proposed fix options (pick one):**

**(A) Reduce base effect:** COURT_NATION base +5/turn (from +8). With skill 10: +8/turn (from +12). Austria takes 9 turns instead of 6. Simplest fix.

**(B) Diminishing returns:** Each consecutive COURT_NATION turn on the SAME target gives -1 cumulative. Turn 1: +12, Turn 2: +11, Turn 3: +10... floor at +4. Switching targets resets the counter. Encourages rotating diplomatic attention.

**(C) Rival jealousy (pairs well with decay):** When France's relation with nation A improves, nations HOSTILE to A (at WAR or relation < -20) get -2 toward France. Courting Austria makes Britain angrier. Forces diplomatic tradeoffs.

**My recommendation:** (A) + R4a decay together. Simple, effective, breaks the exploit.

---

## RANK 5 — Armistice System (Two stubs that need filling)

### R5a: Armistice Expiration — NEEDS DESIGN

**Problem:** `_process_armistice_expiration()` returns `[]`. Armistices never expire.

**Proposed fix:** Track `armistice_turns[diplo_key]` counting turns in ARMISTICE state. After minimum 3 turns, transition to PEACE automatically (per spec §5b). Generate dispatch event: "The armistice with Prussia has concluded. A fragile peace takes hold." If relations < -60, transition to WAR instead of PEACE (armistice collapses).

### R5b: Armistice Cooldowns — NEEDS DESIGN

**Problem:** Cooldowns initialized but never set.

**Proposed fix:** In `_ratify_treaty()`, when transitioning TO ARMISTICE: `world.armistice_cooldowns[diplo_key] = 5`. Block new armistice proposals when cooldown > 0. Decrement in `_decrement_cooldowns()` (already called in advance_turn).

---

## RANK 6 — Trade Income Cap (Prevents economic snowball)

### R6: Trade Income Snowball — NEEDS DESIGN

**Problem:** ALLIANCE = 200g/turn bilateral. 4 alliances = 800g/turn. Nearly doubles France's income.

**Proposed fix — Diminishing returns per nation:**
```
1st trade partner:  full income (200g for ALLIANCE)
2nd trade partner:  75% income (150g)
3rd trade partner:  50% income (100g)
4th trade partner:  25% income (50g)
```

Total max from 4 ALLIANCE partners: 200+150+100+50 = 500g (vs current 800g). Still strong but not game-breaking. Partners sorted by state level (highest-value first gets full rate).

**Alternative:** Hard cap at 400g total trade income per nation.

---

## RANK 7 — Defensive Alliance Base Disposition (Simple formula fix)

### R7: Defensive Alliance Uses Alliance Base — NEEDS DESIGN

**Problem:** No `"defensive_alliance"` entry in `BASE_DISPOSITION`. Uses 20 (same as ALLIANCE).

**Proposed fix:** Add `"defensive_alliance": 25` to `BASE_DISPOSITION` dict. Defensive alliances are lesser commitments — should be slightly easier to achieve.

---

## RANK 8 — AI Relation Penalty in Wartime (Formula improvement)

### R8: Relation Penalty Dominates Wartime Proposals — NEEDS DESIGN

**Problem:** France-Prussia relation -40 = permanent -20 acceptance penalty. Military victories don't offset this. Even crushing military dominance can't force peace without sweeteners.

**Proposed fix:** Add "military pressure" modifier to acceptance formula:
```
military_pressure = max(0, war_score * 0.15) when proposer is winning
```
Up to +15 at war_score 100. Partially offsets relation penalty during active wars. Does NOT stack with Military Supremacy modifier — use whichever is higher.

**Example:** France-Prussia war, score +60, relation -40:
- Current: relation_mod = -20, total acceptance suffers
- With fix: military_pressure = +9, partially offsetting the -20

---

## RANK 9 — War Score Farming Protection (Balance)

### R9: Small Battle War Score Farming — NEEDS DESIGN

**Problem:** Every battle win = +3 regardless of scale. 500-casualty skirmish counts same as Austerlitz.

**Proposed fix:** Minimum casualty threshold of 2000 total for `record_battle()` to count toward war score:
```python
def record_battle(...):
    total = attacker_casualties + defender_casualties
    if total < 2000:
        return  # Skirmish — no diplomatic impact
```

---

## RANK 10 — Player War Declaration Command (Missing command)

### R10: No War Declaration via Talleyrand — NEEDS DESIGN

**Problem:** `declare_war()` exists but no player command. Can only declare war by attacking.

**Proposed fix:** Wire similar to break_treaty/downgrade:
- Keywords: "declare war on", "war against", "attack nation" (when targeting a nation, not a marshal)
- Cost: 1 DP (per spec §5c)
- Talleyrand objects (STRONG) if target is neutral and threat > 50
- Calls `declare_war()` with full relation/threat penalties

---

## RANK 11 — Coalition Stalemate Duration (Balance)

### R11: Coalition Stalemates Last Too Long — NEEDS DESIGN

**Problem:** War exhaustion +5/turn → 30 turns to reach separate-peace threshold.

**Proposed fix options:**
- **(A)** Increase passive WE to +8/turn (19 turns instead of 30)
- **(B)** Add stalemate auto-armistice: war score stays -10 to +10 for 8+ consecutive turns → coalition offers armistice automatically
- **(C)** Add coalition internal friction: members lose -2 mutual relation/turn (historical infighting eventually breaks alliances)

**My recommendation:** (A) + (C) together. Faster WE + internal friction creates coalition lifecycle of ~12-15 turns instead of 30.

---

## RANK 12 — Alliance Paradox Edge Case (MEDIUM)

### R12: Alliance Paradox — Silent Breaking — NEEDS DESIGN

**Problem:** Allied with Austria + Saxony. Austria attacks Saxony. France-Austria alliance silently broken. No popup, no choice.

**Proposed fix:** When war cascade would force player into war against an allied nation, show popup: "Austria has attacked your ally Saxony. Honor your alliance with Saxony? [Yes — war with Austria] [No — break alliance with Saxony]"

---

## RANK 13 — Ghost Nation / Elimination (Edge case)

### R13: No Nation Elimination — NEEDS DESIGN

**Problem:** Nation with 0 regions, 0 army continues processing. Zombie marshals, infinite negative gold.

**Proposed fix:** In `advance_turn`, if nation has 0 regions AND total army strength = 0:
- Mark eliminated (`eliminated_nations.add(nation)`)
- Skip AI/diplomacy processing
- Disband stranded marshals
- Floor nation gold at 0
- Dispatch: "{nation} has been eliminated as a political entity."

---

## RANK 14 — Vassal Shuffle Exploit (Balance)

### R14: Vassal Release/Re-Vassalize Threat Exploit — NEEDS DESIGN

**Problem:** Vassalize (+5 threat) → Release (-8 threat) = net -3 per cycle.

**Proposed fix:** Add per-nation `vassal_release_cooldown`: cannot re-vassalize a nation for 5 turns after release. Track in `world.vassal_release_cooldowns`.

---

## RANK 15 — AI-AI Static Equilibrium (Balance)

### R15: AI-AI Diplomacy Never Degrades — NEEDS DESIGN

**Problem:** By turn 20, all AI nations are allied with each other. No betrayals, no downgrades.

**Proposed fix:** Add two AI-AI triggers:
- **Rivalry:** If two AI nations border the same uncontrolled/contested region AND both have relation > 0, -3 relation/turn (competing over territory)
- **Opportunistic downgrade:** If nation A military > 2x nation B AND relation < +30, consider downgrade one step (the strong bully the weak)

---

## RANK 16 — Threat Sweet Spot Expansion (Balance)

### R16: Infinite Slow Expansion via Threat Sweet Spot — NEEDS DESIGN

**Problem:** 1 battle every 2 turns = below threat decay rate. Indefinite expansion.

**Proposed fix:** Add +2 threat per region captured (new controller != starting controller). Currently only passive thresholds at 60/70/80%. Per-capture threat closes the sweet spot.

---

## RANK 17 — Ledger Information Gaps (Easy UX wins)

### R17: Various Ledger Improvements — NEEDS DESIGN

Bundle of easy additions to diplomatic ledger:

| Sub-item | Description |
|----------|-------------|
| R17a | **War score components** — Show territory/battle/decisive/capital breakdown |
| R17b | **Proposal cooldowns** — Show remaining turns before can propose to each nation |
| R17c | **Treaty ongoing costs** — Show gold/turn breakdown per treaty |
| R17d | **DP generation factors** — Show what contributes to DP rate |
| R17e | **Relation trend** — Arrow up/down/stable based on last turn's change |
| R17f | **Mission progress projection** — "5 more turns to reach NON_AGGRESSION threshold" |

---

## RANK 18 — Continental System Buff (Balance/fun)

### R18: Continental System Too Weak for Its Cost — NEEDS DESIGN

**Problem:** 2 DP/turn for modest gold reduction. Always worse than COURT_NATION.

**Proposed fix options:**
- **(A)** Reduce CS cost to 1 DP/turn (half the investment, same return)
- **(B)** Add diplomatic blocking: CS members apply -10 acceptance to British proposals (prevents British alliance-building)
- **(C)** Add coalition delay: CS with 2+ members slows coalition formation by 1 extra turn

---

## RANK 19 — AI Behavior Improvements (Deeper gameplay)

### R19: Deferred AI Triggers P3/P5 — NEEDS DESIGN

**Problem:** AI nations don't seek alliances when threatened (P3) or negotiate when broke (P5).

**Proposed fix:** Implement the P3 and P5 triggers from the spec's decision tree. P3: when threat > 60, AI seeks non-aggression/alliance with other anti-France nations. P5: when gold < 200, AI proposes trade deals or tribute offers.

---

## RANK 20 — Diplomat Skill Cap (Formula tweak)

### R20: Minor Nation Skill Penalty Too Harsh — NEEDS DESIGN

**Problem:** Saxony (skill 4) vs France (skill 10): -12 acceptance penalty. Minor nation proposals always fail.

**Proposed fix:** Cap skill differential penalty at -8: `diplomat_skill_bonus = max(-8, (proposer_skill - target_skill) * 2)`.

---

## RANK 21 — Ultimatums / Coercive Diplomacy — NEEDS DESIGN

**Problem:** No "accept peace or I declare war" mechanic. Napoleon used coercive diplomacy constantly — Metternich's armed mediation is already in the AI but the player has no equivalent tool. All proposals are neutral requests.

**Proposed design:** New command type: "Talleyrand, deliver ultimatum to Prussia: accept peace or face war."
- Cost: 2 DP (major diplomatic action)
- Acceptance formula gets a `military_threat` bonus: +15 when player has marshals adjacent to target's territory, +10 otherwise
- Relation hit regardless of outcome: -10 (ultimatums are aggressive)
- If REJECTED: player gets a casus belli (halved war declaration penalties per §5c)
- Talleyrand objects (STRONG) if threat > 50 — "Ultimatums are how coalitions are born, Sire"
- Keywords: "ultimatum", "demand... or else", "threaten", "final offer"

**Why ranked here:** Adds significant strategic depth and historical accuracy. Napoleon's diplomacy was fundamentally coercive — "negotiate from strength" should be a core tool. Medium implementation difficulty (new acceptance modifier + command wiring + casus belli tracking).

---

## RANK 22 — Marriage Alliances — NEEDS DESIGN

**Problem:** Napoleon's marriage to Marie Louise of Austria (1810) was perhaps the most consequential diplomatic act of his reign, securing 3 years of peace. This system has no personal diplomacy at all. The biggest historical gap.

**Proposed design:** One-shot diplomatic action, not an ongoing system. Marriage is a special clause in alliance proposals.
- Command: "Talleyrand, propose marriage alliance with Austria"
- Prerequisite: PEACE or above with target nation. Target must have a royal family (Austria, Prussia, Saxony — not Britain, who has no capital on map).
- Cost: 3 DP (major commitment)
- Acceptance formula bonus: +20 (marriages are highly desirable for minor nations seeking protection)
- Effects on acceptance:
  - Auto-upgrades to ALLIANCE if not already
  - Relation +30 (family bond)
  - 5-turn "honeymoon" immunity — neither side can declare war or downgrade for 5 turns
  - Threat reduction: -10 (France seen as integrating, not conquering)
  - Coalition brewing pauses for 3 turns (diplomatic reset)
- Limit: ONE marriage alliance active at a time. Divorcing (breaking the marriage) costs -50 relation with target, -20 with ALL nations, +25 threat. Historically devastating — Napoleon's divorce of Josephine was scandalous, remarriage was strategic.
- Talleyrand's role: Schemer personality means he LOVES marriage alliances — no objection, +5 acceptance bonus from Talleyrand's enthusiasm.

**Why ranked here:** Highest historical impact of any missing feature. Creates a dramatic one-time diplomatic event with lasting consequences. Medium-hard difficulty (new clause type, honeymoon state, divorce mechanic).

---

## RANK 23 — Marshal Morale from Diplomacy — NEEDS DESIGN

**Problem:** Declaring war, signing peace, making vassals, breaking alliances — zero impact on marshal trust or morale. Cross-system blind spot. Aggressive marshals should cheer war declarations; cautious marshals should approve of peace.

**Proposed design:** Personality-based trust reactions to diplomatic events:

| Event | Aggressive Marshal | Cautious Marshal | Literal Marshal |
|-------|-------------------|-----------------|-----------------|
| War declared | +3 trust | -3 trust | 0 (follows orders) |
| Peace signed (winning) | -2 trust ("why stop?") | +2 trust | 0 |
| Peace signed (losing) | -5 trust ("coward!") | +3 trust ("wise") | 0 |
| Alliance formed | 0 | +2 trust | 0 |
| Vassal acquired (conquest) | +3 trust | -2 trust | 0 |
| Vassal acquired (treaty) | -1 trust ("soft") | +2 trust | 0 |
| Treaty broken | +2 trust ("bold") | -3 trust ("dishonorable") | 0 |

Capped at ±5 trust per turn from diplomatic events. Applied during advance_turn after diplomatic processing.

**Why ranked here:** Creates meaningful cross-system interaction. Marshals should feel like people who have opinions about the war, not just combat units. Easy-medium implementation (trust.modify calls in diplomatic event handlers).

---

## RANK 24 — Treaty Signing Ceremonies — NEEDS DESIGN

**Problem:** After potentially turns of negotiation, the result is "Treaty ratified" — a notification. No ceremony, no drama. The moment should feel earned.

**Proposed design:** When a major treaty is ratified (PEACE, ALLIANCE, VASSAL), generate a ceremony template:
- Talleyrand presents the treaty with personality-flavored commentary
- Enemy diplomat reacts (personality-keyed: Hawk grudgingly accepts, Dove celebrates, Schemer calculates)
- Campaign log entry marked as a "historic event"
- Example: "At the signing in Paris, Talleyrand presented the Treaty of Berlin with characteristic grace. Hardenberg, jaw clenched, affixed his seal. 'Prussia remembers,' he muttered. Talleyrand smiled. 'I should hope so.'"

3-4 ceremony templates per diplomat personality × proposal type. ~20 new templates total.

**Why ranked here:** High emotional payoff for relatively low implementation cost (template writing + dispatch event type).

---

## RANK 25 — Vassal Personality Events — NEEDS DESIGN

**Problem:** Vassal management is numbers-only. No personality, no unique events, no "Saxony requests autonomy" dialogues. Rebellion is a threshold, not a story.

**Proposed design:** 4-5 vassal event types that fire based on loyalty thresholds:
- **Loyalty 60+:** "Saxony celebrates the alliance" — flavor dispatch, +3 loyalty
- **Loyalty 40-59:** "Saxon merchants petition for lower tribute" — choice: reduce tribute (-25% for 3 turns, +10 loyalty) or refuse (-5 loyalty)
- **Loyalty 20-39:** "Reynier reports Saxon officers meeting secretly" — choice: investigate (spend 1 DP, reveal courting nation) or ignore
- **Loyalty <20:** "Saxon delegation demands autonomy" — popup: grant autonomy upgrade (+15 loyalty) or refuse (-10 loyalty, +5 threat from oppression narrative)
- Max 1 event per vassal per 5 turns (no spam)

**Why ranked here:** Vassal system is mechanically complete but narratively empty. Events would make vassals feel like political entities rather than tribute machines.

---

## RANK 26 — Continental System Drama — NEEDS DESIGN

**Problem:** CS is currently "spend DP, reduce a gold counter." Should generate stories.

**Proposed design:**
- **Smuggling events** (1 per 3 turns while CS active): Random participant caught trading with Britain. Choice: confront (-10 relation, -5 vassal loyalty if vassal, participant withdraws from CS) or overlook (CS effectiveness -25g for that nation, trust +2 from Talleyrand approving pragmatism)
- **British countermeasures:** When CS has 2+ members, Britain spends extra DP to UNDERMINE one CS participant per turn. Player sees dispatch: "British agents in Dresden encourage trade violations."
- **Economic hardship:** After 5+ turns of CS, participating nations get -5 relation with France per turn from economic pain. Creates the historical tension where the CS worked but was self-defeating.

**Why ranked here:** The Continental System was Napoleon's most ambitious project AND greatest strategic failure. It should generate stories, not just modify a counter.

---

## RANK 27 — Secret Treaties — NEEDS DESIGN

**Problem:** All treaties are public. Tilsit's secret articles — dividing Europe into French and Russian spheres — can't happen. Reduces diplomatic intrigue.

**Proposed design:** New clause type: "Secret article" in proposals.
- Cost: +1 DP on top of proposal cost (secrecy is expensive)
- Secret clauses are not announced in Morning Dispatch or campaign log
- AI-AI secret treaties are hidden from the player entirely until discovered via GATHER_INTEL mission
- Discovery: 20% chance per turn that a secret clause is leaked. Leaked clauses cause -15 relation with all nations ("they were dealing behind our backs")
- Player secret clauses: Talleyrand loves them (Schemer +5 acceptance). If discovered, Talleyrand takes the blame or credit depending on outcome.
- Example: "Talleyrand, propose peace with Prussia, with a secret article: Prussia withdraws from British alliance within 3 turns"

**Why ranked here:** Adds significant intrigue and replayability. Medium difficulty (new clause flag, visibility filtering, discovery mechanic).

---

## RANK 28 — Template Variety Expansion — NEEDS DESIGN

**Problem:** ~56 unique text blocks. In a 50-turn game: noticeable repetition by turn 25. VAGUE path stalemate templates are most vulnerable (only 3-5 variants).

**Proposed fix:** Add 15-20 new templates:
- 5 additional VAGUE+WAR templates (war-weariness, flanking opportunity, supply concerns, morale observations, weather/season references)
- 3 additional VAGUE+PEACE templates (trade opportunity, cultural exchange, border tensions)
- 5 counter-offer variants per diplomat personality
- Historical reference library: Talleyrand occasionally references precedents ("This is Austerlitz all over again", "Remember what happened at Tilsit, Sire")
- Seasonal flavor: "Winter is no time for grand campaigns, Sire. Let us negotiate instead."

**Why ranked here:** Pure content work, no systems changes. High polish value for long games.

---

## RANK 29 — Diplomatic History in Ledger — NEEDS DESIGN

**Problem:** After 20 turns, player can't review past diplomatic interactions. No proposal history.

**Proposed fix:** Track `world.diplomatic_history` list: `[{"turn": 5, "type": "proposal", "from": "France", "to": "Prussia", "proposal_type": "peace", "outcome": "REJECT"}, ...]`. Display in Talleyrand tab or new Tab 5 in diplomatic ledger. Most recent first, max 20 entries.

---

## RANK 30 — Strategic Order Auto-Cancel on Peace — NEEDS DESIGN

**Problem:** §5b.4 specifies auto-cancellation of PURSUE/MOVE_TO orders against now-peaceful nations. Not implemented. Movement restriction compensates but marshal wastes a turn.

**Proposed fix:** In `_ratify_treaty()`, when transitioning from WAR to non-WAR: iterate marshals, cancel PURSUE orders targeting the now-peaceful nation's marshals, cancel MOVE_TO with attack_on_arrival targeting their regions.

---

## RANK 31 — Acceptance Score Preview — NEEDS DESIGN

**Problem:** Player can't see estimated acceptance for a specific proposal config before spending DP. Feasibility gives qualitative tiers only.

**Proposed fix:** Enhance feasibility response to include numerical breakdown when player asks about a specific proposal type + target: "Talleyrand estimates: base 30, relations -20, war score +9, skill +8, personality -5 = **22** (REJECT). Key obstacle: relations." Show components, not just tier.

---

## RANK 32 — Multi-Party Peace Conferences — NEEDS DESIGN

**Problem:** All diplomacy is bilateral. No Congress of Vienna mechanic where 3+ nations negotiate simultaneously.

**Proposed design:** Special action: "Talleyrand, convene a peace conference"
- Cost: 4 DP (entire turn's diplomatic budget)
- Prerequisite: France at war with 2+ nations simultaneously
- All nations at war with France are invited. Each runs acceptance formula independently.
- Nations that accept: ceasefire for conference duration (2 turns). Nations that reject: war continues.
- Conference produces a bundled peace proposal addressing all parties simultaneously
- Player builds one set of terms that applies to all participants (can offer different clauses per nation)
- Historical: Congress of Erfurt, Congress of Vienna, Treaty of Amiens all involved multiple parties

**Why ranked here:** Architecturally ambitious but historically essential for late-game scenarios. Hard difficulty.

---

## RANK 33 — Dynastic Succession / Puppet Rulers — NEEDS DESIGN

**Problem:** Can't install family members as puppet rulers. Napoleon's primary vassal management tool (Joseph in Spain, Louis in Holland, Jerome in Westphalia, Murat in Naples).

**Proposed design:** When creating a vassal (conquest or treaty), option to "install a Bonaparte":
- Cost: +1 DP on top of vassalization cost
- Effect: +15 starting loyalty (family member is loyal by blood), +1 loyalty/turn passive bonus
- Downside: -10 relation with ALL other nations (nepotism perceived as arrogance), +5 threat
- Limit: max 2 Bonaparte rulers at once (Napoleon only had so many brothers)
- If vassal rebels with Bonaparte installed: dramatic narrative event, Bonaparte captured/exiled

**Why ranked here:** Historical flavor but niche mechanic. Only matters for conquest-heavy playstyles.

---

## RANK 34 — AI Diplomatic Memory / Trust History — NEEDS DESIGN

**Problem:** If the player always breaks treaties with a nation, that nation treats next proposal identically. No "fool me twice" mechanic.

**Proposed fix:** Track per-nation `diplomatic_reliability` score: +5 for honoring treaty 10+ turns, -10 for breaking a treaty. Feed into acceptance formula as ±10 max modifier.

---

## RANK 35 — Player-Specified Counter-Offer Terms — NEEDS DESIGN

**Problem:** When responding to AI proposals, "Counter-offer" runs M3 algorithm — player gets no input on what the counter looks like. Black box.

**Proposed fix:** Stretch goal of R2. When player selects [Renegotiate], open clause-selection interface (same as player-initiated proposals). Player builds their counter-terms, Talleyrand carries them, acceptance formula evaluates. Turns counter-offers from "reroll the negotiation" to "I specifically want THIS."

**Why ranked here:** Most impactful UX improvement for diplomacy but requires significant UI work (clause builder in response context, not just proposal context). Hard difficulty.

---

## RANK 36 — Personal Summits — NEEDS DESIGN

**Problem:** No "raft on the Niemen" moments. No face-to-face negotiation where Napoleon's personality directly affects outcomes.

**Proposed design:** Special action: "Talleyrand, arrange a summit with [leader]"
- Cost: 2 DP + 1 turn of transit
- Prerequisite: PEACE or ARMISTICE with target
- Effect: +20 acceptance bonus to any proposal made during the summit turn (personal charisma)
- Risk: If authority < 40, summit can backfire (Napoleon appears weak → -10 acceptance instead)
- Talleyrand objects if he thinks the summit is premature
- One summit per game per nation (diminishing returns on personal meetings)
- Narrative: Special summit template with dramatic location description

**Why ranked here:** Cool historical flavor but situational. One-per-nation limit constrains impact.

---

## RANK 37 — Talleyrand Sabotage/Redemption Popups Unresolvable (CRITICAL bug)

### R37: Sabotage Discovery & Redemption Popups Cannot Be Resolved — NEEDS DESIGN

**Problem:** When Talleyrand's sabotage is discovered (or redemption triggers), the popup NEVER appears. Instead, the content dumps into the chat log as plain text. The player cannot interact with it (no Confront/Overlook/Apologize/Replace/Continue buttons), making the sabotage/redemption system completely non-functional. Additionally, the executor has no handlers for these actions even if the popup were shown.

**Root cause (3 layers):**

1. **Popup never triggers in Godot**: The sabotage/redemption data reaches the API response but Godot renders it as chat text instead of triggering the dedicated popup scenes (`sabotage_discovery_popup.gd`, `talleyrand_redemption_popup.gd`). Either `main.gd` doesn't check for the popup fields in the response, or the check runs after the text is already rendered to chat.

2. **Missing action map entries** (`executor.py`, `_process_dialogue_choice()`): Even if the popup were shown, the `action_map` dict has NO entries for sabotage/redemption actions. Keywords "confront", "overlook", "apologize", "replace", "continue" are in `_DIALOGUE_RESPONSE_KEYWORDS` but the executor doesn't know what to do with `confront_sabotage`, `overlook_sabotage`, `redemption_apologize`, `redemption_replace`, or `redemption_continue` actions.

3. **Missing handler functions**: No `_handle_confront_sabotage()`, `_handle_overlook_sabotage()`, etc. exist in the executor. The logic EXISTS in `diplomatic_defiance.py` (`resolve_confrontation()` at line ~416, `apply_redemption_choice()` at line ~544) but is never wired. On failure, `pending_diplomatic_dialogue` is NOT cleared → stuck state.

**Proposed fix:**

1. **Fix popup triggering in Godot**: Ensure `main.gd` checks for `diplomatic_sabotage` / `talleyrand_redemption` fields in the response and calls the popup BEFORE rendering chat text. Verify popup scene nodes are connected in the scene tree.

2. Add entries to `action_map` in `_process_dialogue_choice()`:
   ```python
   "confront": "confront_sabotage",
   "overlook": "overlook_sabotage",
   "apologize": "redemption_apologize",
   "replace": "redemption_replace",
   "continue": "redemption_continue",
   ```

3. Implement handler functions that call existing `diplomatic_defiance.py` logic:
   - `_handle_confront_sabotage()` → calls `resolve_confrontation()`
   - `_handle_overlook_sabotage()` → calls `resolve_confrontation()`
   - `_handle_redemption_*()` → calls `apply_redemption_choice()`

4. Each handler must clear: `world.pending_diplomatic_dialogue = None`, `world.diplomatic_sabotage_popup = None` / `world.talleyrand_redemption_popup = None`

5. Add failure fallback: if action lookup fails, still clear `pending_diplomatic_dialogue` to prevent stuck state

**Priority:** CRITICAL — sabotage/redemption system entirely non-functional. Should be fixed before any balance work.

---

## RANK 38 — Talleyrand Proposal Terms Phrasing (MEDIUM bug)

### R38: Talleyrand's Terms Show "War Score: 0" and Read Awkwardly — NEEDS DESIGN

**Problem:** Template T6 (`diplomatic_templates.py:176-179`) for proposal confirmation reads:

```
"Sire, for a {proposal_type} proposal to {target_nation},
I suggest the following terms. War score: {war_score}, relation: {relation}."
```

Two issues:

1. **"War score: 0" when not at war**: The slot resolver (`diplomatic_templates.py:1118`) looks up `world.war_scores.get(diplo_key, 0)`. When not at WAR, the key doesn't exist → defaults to 0. Showing "War score: 0" for a peace-time proposal is confusing and nonsensical.

2. **Mechanical phrasing**: "War score: {war_score}, relation: {relation}" reads like debug output, not like Talleyrand speaking. Compare with T1 (line ~26) which uses "War score stands at..." — still mechanical but slightly better. Talleyrand should frame these as diplomatic context, not raw numbers.

**Proposed fix:**

**(A) Conditional war score display:** Only show war score when nations are AT_WAR:
```python
if diplomatic_state == "WAR":
    terms_context = f"The military situation favors {'us' if war_score > 0 else 'them'} — war score {war_score}."
else:
    terms_context = ""  # No war score display in peacetime
```

**(B) Rephrase in Talleyrand's voice:** Replace mechanical format with character-appropriate language:
- High war score: "Our military position is strong, Sire. They will be... receptive."
- Low war score: "Our negotiating position is weak. Generous terms may be necessary."
- Peacetime: "Relations with {nation} stand at {relation}. {qualifier based on value}."

**(C) Move raw numbers to ledger:** Remove numeric war score from Talleyrand's dialogue entirely. Players who want numbers check the Diplomatic Ledger. Talleyrand gives qualitative assessment only.

**My recommendation:** (A) + (C). Hide war score from peacetime proposals, keep qualitative assessment in dialogue, raw numbers stay in the ledger.

---

## RANK 39 — DP Display Investigation (Potential UI bug)

### R39: DP (Diplomatic Points) Not Visibly Displayed — NEEDS DESIGN

**Problem:** User reports DP is not displayed during gameplay.

**Code investigation shows DP IS fully wired:**

| Layer | Status | Location |
|-------|--------|----------|
| Backend tracking | ✓ | `world_state.py:351-352` — `diplomatic_points`, `max_diplomatic_points` |
| API responses | ✓ | `main.py:432-433` (GET /test), `main.py:758-759` (POST /command) |
| Diplomatic ledger data | ✓ | `diplomatic_ledger.py:355-356` — `dp_remaining`, `dp_max` in Talleyrand tab |
| Top bar display | ✓ | `top_bar.gd:22` — `DPLabel` node, `top_bar.gd:235-240` — update function |
| Diplomatic ledger display | ✓ | `diplomatic_ledger.gd:17` — `dp_display` node, lines 140-144 |
| Update path | ✓ | `main.gd:1598-1614` — `_update_diplomatic_top_bar()` called on poll + command |

**Possible causes (need in-game investigation):**

1. **Scene tree mismatch**: `DPLabel` node path in `top_bar.gd` (`$BarContainer/BarBG/BarLayout/RightSection/DPLabel`) may not match the actual .tscn scene tree → null reference, label never updates
2. **Label hidden/overlapped**: DPLabel exists but is positioned off-screen or hidden behind another element
3. **Update not triggering**: `_update_diplomatic_top_bar()` might not fire if the `/test` endpoint response doesn't include diplomatic fields before the game is fully initialized
4. **Default max mismatch**: API uses `getattr(world, 'max_diplomatic_points', 3)` as default (3) but actual starting value is 5 — if world isn't initialized, display shows "DP: 0/3"

**Next step:** Manual testing required — run the game and check:
- Does the DPLabel node exist in the top_bar.tscn scene?
- Does `/test` endpoint return `diplomatic_points` field?
- Is the label visible but showing wrong values?
