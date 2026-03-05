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

## RANK 21+ — Narrative & Feel Improvements (NEEDS DESIGN, lower priority)

| # | Item | Description |
|---|------|-------------|
| R21 | **Treaty signing ceremonies** | Dramatic template when major treaty is ratified. Talleyrand presents, enemy diplomat reacts. |
| R22 | **Vassal personality events** | "Saxony requests more autonomy" dialogues, investment flavor, rebellion ultimatum. |
| R23 | **Continental System drama** | Smuggling events, economic hardship narratives, British countermeasures. |
| R24 | **Template variety expansion** | More VAGUE path templates, stalemate variants, historical references ("Remember Tilsit"). |
| R25 | **Marshal morale from diplomacy** | Aggressive marshals approve of war declarations (+trust). Cautious marshals approve of peace. |
| R26 | **Diplomatic history in ledger** | Past proposals with outcomes. "Proposed peace with Prussia Turn 8 — REJECTED." |
| R27 | **Strategic order auto-cancel on peace** | Wire §5b.4 — cancel PURSUE/MOVE_TO against now-peaceful nation's marshals. |
| R28 | **Acceptance score preview** | Show estimated score for a specific proposal before spending DP. |

---

## Items Considered but Deferred (Out of Scope)

These are design aspirations noted in the creative audit but deferred to future phases:

- **Marriage alliances** — Major new system, not refinement
- **Multi-party peace conferences** — Requires bilateral-to-multilateral architecture change
- **Ultimatums / coercive diplomacy** — New command type with new acceptance formula integration
- **Secret treaties** — Significant new mechanic
- **Dynastic succession / puppet rulers** — Phase 9+ content
- **Player-specified counter-offer terms** — Complex UX overhaul (stretch goal of R2)
- **AI diplomatic memory / trust history** — Nice but low impact for implementation cost
