# Full Diplomacy Phase Audit — Cross-Document Review

**Date:** 2026-02-27
**Documents reviewed:** DIPLOMACY_SPEC.md v2.1, CONVERSATIONAL_DIPLOMACY_DESIGN.md v1.1
**Supporting docs:** CLAUDE.md, SYSTEMS_REFERENCE.md, V2B_DEFIANCE_SPEC.md, ROADMAP.md, STATUS.md
**Code reviewed:** executor.py, world_state.py, marshal.py, dispatch.py, enemy_ai.py

---

## Executive Summary

**Overall Grade: 79/100**

This is an ambitious, innovative design that no strategy game has attempted: conversational diplomacy with a character who has opinions, biases, and his own agenda. The two specs work together surprisingly well — SPEC provides a rock-solid deterministic engine, DESIGN wraps it in a conversation layer that makes the mechanics feel like talking to Talleyrand. The acceptance formula is clean, the state machine is well-defined, and the 51+ edge cases show serious engineering discipline.

The main risks are not conceptual — they're in the seams. DP deduction timing across the conversation flow is under-specified. Strategic military orders don't auto-cancel on diplomatic state changes. The `pending_diplomatic_proposal` field in SPEC conflicts with `pending_diplomatic_dialogue` in DESIGN. And the 10-session implementation plan, while individually scoped well, has concentrated risk in Sessions 1A/1B (map expansion breaking 100+ existing tests).

The fun factor is genuinely high (8/10 in the 15-turn walkthrough). The Schemer bias mechanic — where Talleyrand's advice is 70% honest and 30% self-serving — is the killer feature. No other strategy game makes you question your own advisor. Fix the 5 critical findings and this ships clean.

---

## Task 1: Cross-Document Integration (22/30)

### Dimension 1: Mechanical Handoff (7/10)

**Every conversation endpoint must map to exactly one executor action.** I traced all paths:

| Path | Flow | Maps to SPEC... | Status |
|------|------|-----------------|--------|
| VAGUE | player → proposal_options → pick → proposal_confirm → "Send it" | §2d proposal transit | OK |
| MEDIUM | player → proposal_confirm → "Send it" | §2d proposal transit | OK |
| SPECIFIC + agree | player → fast-track T7 → "Send" | §2d proposal transit | OK |
| SPECIFIC + object | player → T8/T26 → "Send my terms" → defiance roll | §3a defiance | OK |
| Incoming accept | AI popup → "Accept" | §9a accept (0 DP) | OK |
| Incoming reject | AI popup → "Reject" | §9a reject (-5 relation) | OK |
| Incoming counter | AI popup → "Accept counter" / "Renegotiate" | §9a counter flow | OK |
| Advisory | question → assessment → [no action] | — (informational) | OK |
| Feasibility | "what would it take" → assessment | §2g feasibility | OK |
| Sabotage confrontation | discover → confront/overlook | §3c discovery | OK |
| Proactive suggestion | dispatch → elaborate → proposal_options | Loops to VAGUE path | OK |

**Gaps found:**

**GAP-1 (Critical): DP Deduction Timing.** SPEC §2d says "Turn 1: Player issues command, DP spent." But DESIGN adds 1-3 conversation exchanges BETWEEN "player types command" and "Send it" (the actual proposal dispatch). When exactly is DP spent?

- If DP is spent when the conversation starts → player loses DP even if they cancel mid-conversation.
- If DP is spent when "Send it" fires → correct, but neither spec explicitly states this.
- Current state: DESIGN §9b lists `execute_proposal → proposal transit` as the action, suggesting DP is spent at execution. But this needs to be explicit.

**Fix:** Add to DESIGN §9b: "DP is deducted when `execute_proposal` fires (when player confirms 'Send it'), NOT when the conversation begins. Cancelling a conversation costs 0 DP."

**GAP-2 (Major): "Specify your own" dead-end.** DESIGN §9b says `modify_harsh` and `modify_generous` options cap at 2 iterations, then are "replaced with 'specify your own.'" DESIGN §3b mentions "Let me specify" opens a clause-selection flow. But this clause-selection flow is never fully defined — it's described as "bridging conversational and mechanical interfaces" without specifying how the player actually selects individual clauses in a terminal/text UI. Does the player type each clause? Get a numbered list? This path needs concrete UI specification.

**GAP-3 (Minor): Proactive suggestion → elaborate → options loop.** DESIGN §5d says "[Ask Talleyrand to elaborate]" opens a `proposal_options` dialogue. But proactive suggestions can be about threats, loyalty, or opportunities — not all of which have proposal options. A threat assessment suggestion shouldn't loop into proposal_options; it should loop into advisory. The trigger-to-dialogue-type mapping needs specification.

### Dimension 2: State Consistency (7/10)

**State fields in play:**
- `pending_objection` (existing) — combat/tactical objection
- `pending_strategic_objection` (existing) — strategic order objection
- `pending_diplomatic_dialogue` (DESIGN §2b) — conversation state
- `pending_diplomatic_proposal` (SPEC §S13) — proposal popup
- `proposal_in_transit` (SPEC §S13) — transit state

**GAP-4 (Critical): Field conflict — `pending_diplomatic_proposal` vs `pending_diplomatic_dialogue`.** SPEC §S13 defines `pending_diplomatic_proposal: Optional[Dict]` as a WorldState field. DESIGN replaces SPEC §9a (AI proposal popups) with the dialogue system, meaning AI proposals are now delivered via `pending_diplomatic_dialogue` with type=`incoming_proposal`. These two fields serve overlapping purposes. Which is canonical?

- If both exist: save/load could have one set but not the other, creating inconsistent state.
- If DESIGN supersedes: `pending_diplomatic_proposal` should be REMOVED from SPEC §S13 field list.
- If both serve different purposes (e.g., `pending_diplomatic_proposal` for raw data, `pending_diplomatic_dialogue` for presentation): the relationship must be explicit.

**Fix:** SPEC §S13 should remove `pending_diplomatic_proposal`. All proposal presentation routes through `pending_diplomatic_dialogue`. The raw proposal data lives in `proposal_in_transit` (for outgoing) or `diplomatic_queue` (for incoming AI proposals awaiting presentation).

**GAP-5 (Major): Save/load mid-conversation.** DESIGN §2b says `pending_diplomatic_dialogue` is serializable (all primitive types). But the load-side display trigger is unspecified. When the game loads with an active dialogue, the Godot client must detect `pending_diplomatic_dialogue` and re-display the popup. Current pattern: `pending_objection` display is triggered by checking the field after load. Same pattern should apply here, but DESIGN doesn't specify the Godot-side load handler.

**GAP-6 (Minor): Staleness on load.** DESIGN §2b includes `turn_created` for staleness (auto-dismiss after 1 turn for non-blocking). If a player saves turn 5, loads turn 5 three days later — the dialogue is "fresh" (same turn). But what about blocking dialogues that should persist? `incoming_proposal` and `sabotage_confrontation` are blocking and don't auto-dismiss. This seems correct — blocking dialogues survive indefinitely until resolved.

**Priority hierarchy (DESIGN §9c) is well-defined:**
```
1. pending_objection (combat)
2. pending_strategic_objection (strategic)
3. pending_diplomatic_dialogue (blocking=True)
4. pending_diplomatic_dialogue (blocking=False)
```

Strategic per-turn execution (`_strategic_execution=True`) ignores diplomatic dialogue entirely. This is correct — a MOVE_TO step shouldn't be blocked by an unfinished conversation.

### Dimension 3: Formula Integration (8/10)

**Template-to-formula mapping:**
- DESIGN templates reference difficulty tiers: "Virtually certain" (≥70), "Achievable" (50-69), "Challenging" (35-49), "Very difficult" (20-34), "Nearly impossible" (<20). These map 1:1 to SPEC §2g tiers. ✓
- `_suggest_gold_per_turn()` in DESIGN §4c iterates gold amounts and projects acceptance scores via the SPEC §6 formula. Single-source call. ✓
- Schemer bias (DESIGN §5c) shifts REPORTED tier only, not the formula output. Explicit: "Bias NOT applied to actual formula." ✓

**GAP-7 (Major): Schemer bias in MEDIUM path has mechanical side-effects.** DESIGN §3b says "Schemer bias may inflate concessions" when Talleyrand fills in terms for the MEDIUM path. If Talleyrand suggests terms that are MORE generous than needed (because Schemer bias wants restrained France), and the player says "Send it" without checking the Ledger — the player actually sends overly generous terms. The formula evaluates the actual terms sent, so the acceptance score is higher than necessary, and France gives away more than it needed to.

This means Schemer bias is NOT purely cosmetic in the MEDIUM path — it affects the actual treaty terms through the player's trust. This is almost certainly *intentional* (it's the game — trust vs verify), but it should be explicitly documented as a designed asymmetry, not left implicit.

**GAP-8 (Minor): Acceptance score rounding.** SPEC §6 formula uses multipliers that produce floats (`war_score * 0.3`, `relation / 2`, `threat * -0.3`). The final acceptance score is compared to thresholds (≥50, 30-49, <30). If the result is 49.7, is that ACCEPT or COUNTER_OFFER? SPEC doesn't specify rounding. Since Golden Rule #2 requires int() for Godot, the formula should explicitly `int()` the final score. Recommendation: `int(round(score))` to avoid systematic bias from truncation.

---

## Task 2: Edge Case Stress Test (23 cases found)

### Given Scenarios

**EC-1: 4 Systems Competing (Talleyrand IN_TRANSIT + advisory + strategic + AI proposal)**
- Trace: IN_TRANSIT means no new proposals, but advisory works (SPEC §2d). Strategic fires with `_strategic_execution=True`, ignores dialogue (DESIGN §9c). AI proposal queued in `diplomatic_queue`, delivered at NEXT turn start (SPEC §9a EC-C).
- Resolution order: turn start → dispatch (with advisory if asked) → AI proposal delivered as blocking dialogue → player responds → commands available → strategic fires at end-turn.
- **Verdict: No conflict.** Systems are temporally separated. Clean.

**EC-2: Save During Sabotage Confrontation**
- Trace: `pending_diplomatic_dialogue` with `blocking=True`, type=`sabotage_confrontation`. DESIGN §2b says all primitive types, serializable.
- **Gap:** Load-side display trigger. Godot must check `pending_diplomatic_dialogue` after loading game state and re-render the popup. Pattern exists for `pending_objection` but DESIGN doesn't specify the Godot handler.
- **Severity: Major.** Fix: Add to DESIGN §9a: "On game load, check `pending_diplomatic_dialogue`. If present and blocking, display popup immediately."

**EC-3: PURSUE + Defied Proposal in Transit**
- Trace: Player proposes peace to Prussia. Talleyrand defies (softens terms). Player also has PURSUE order against Prussia. PURSUE fires during turn processing → marshal attacks Prussian forces. Meanwhile, softened proposal arrives at Prussia next turn.
- **Critical gap:** If peace is ACCEPTED (based on Talleyrand's softened terms), diplomatic state transitions to ARMISTICE/PEACE. But the PURSUE strategic order is still active against a nation you're now at peace with. PURSUE should auto-cancel when the target nation's diplomatic state changes to non-WAR.
- SPEC §2e mentions "mission target declares war: mission auto-cancels" for diplomatic missions, but there's NO equivalent auto-cancellation for STRATEGIC MILITARY ORDERS when diplomatic state changes.
- **Severity: Critical.** Fix: Add to SPEC §5b: "When diplomatic state transitions FROM WAR to any non-WAR state, all active strategic orders (PURSUE, MOVE_TO with attack_on_arrival) targeting that nation's marshals are automatically cancelled. Campaign log entry: 'Peace with [nation] — [marshal]'s orders cancelled.'"

**EC-4: Vassal Rebellion + Proactive Suggestion Same Turn**
- Trace: Loyalty checked at START of turn (SPEC EC-F, §8d). Rebellion fires at loyalty 0. Proactive suggestions fire in Morning Dispatch (DESIGN §5d), which builds AFTER loyalty processing.
- **Gap:** If vassal rebels at turn start, the proactive suggestion trigger (loyalty < 40) would fire for an entity that just ceased to be a vassal. The suggestion builder must check vassal existence BEFORE generating the suggestion.
- **Severity: Minor.** Fix: Add guard in proactive trigger: "Check vassal still exists in `world.vassals` before generating loyalty suggestion."

**EC-5: 0 DP + Vague Dialogue → Costly Options**
- Trace: Player at 0 DP opens vague conversation. Talleyrand presents options (peace = 2 DP, alliance = 2 DP, non-aggression = 1 DP). Player picks one. Transitions to proposal_confirm. Player confirms "Send it." DP check at execution time → fails.
- **Gap:** Player went through 2-3 exchanges of conversation only to fail at the DP check. Frustrating UX.
- **Severity: Major.** Fix: DESIGN §3a should specify: "Options display DP cost. Options costing more than current DP show '(insufficient DP)' and selecting them triggers Talleyrand: 'We lack the diplomatic capital for that, Sire. Perhaps something... more modest.' Options that cost 0 DP (advisory, feasibility, mission cancel) are always available." Alternatively, options could be greyed out with cost displayed.

**EC-6: Acceptance Score Exactly 50**
- Trace: SPEC §6a: ≥50 = ACCEPT. Tier: 50-69 = "Achievable." DESIGN T14: "Achievable (50+ projected)."
- **No mismatch.** Score 50 = ACCEPT = "Achievable." Aligned across both specs.
- **Minor concern:** Float rounding (see GAP-8). If raw score is 49.7 and rounds to 50, it's ACCEPT. If truncated to 49, it's COUNTER_OFFER. The threshold behavior depends on rounding policy. Add explicit `int(round(score))`.
- **Severity: Minor.**

**EC-7: Diplomatic Fallback Then Military Command**
- Trace: Player types "Talleyrand, attack Prussia" → DESIGN §2d M6 guard fires: not diplomatic, Talleyrand deflects with message. No `pending_diplomatic_dialogue` is set — it's a message-only response.
- Player then types "Ney, attack Prussia" → parser routes to military. No blocking state. Military command executes normally.
- **Verdict: No conflict.** The M6 guard is correctly message-only. Clean.

**EC-8: Coalition Mid-Conversation**
- Coalition trigger is DEFERRED (SPEC §S15: "Coalition trigger — separate COALITION_SPEC.md"). Out of scope for this audit.
- **Noted:** When coalition is implemented, it must check for and handle active `pending_diplomatic_dialogue`. Add to SPEC §S15: "Coalition trigger must respect dialogue blocking hierarchy."
- **Severity: Deferred (document the interaction point).**

**EC-9: Two AI Proposals Same Turn**
- Trace: SPEC §9a: "Max 1 AI proposal/turn to player." Priority queue P1-P7 determines which fires. Second is suppressed.
- **Gap:** Where does the suppressed proposal go? It stays in the AI's decision state — if conditions still hold next turn, AI re-evaluates and may propose again. But there's no explicit queue for deferred player-targeted proposals.
- **Severity: Minor.** The system works (AI re-evaluates each turn), but could document: "Suppressed proposals are not queued; AI re-evaluates conditions each turn."

**EC-10: Trust Spiral — 3 Overrides**
- Trace through the math:
  - Override 1: Trust 55, insist on MODERATE → trust -10 = 45. Defiance: 5% base + 0 + 0 + variance = ~5%.
  - Override 2: Trust 45, insist on MODERATE → trust -10 = 35. Defiance: 5% + 0 + 0.05 = ~10%.
  - Override 3: Trust 35, insist on MODERATE → trust -10 = 25. Defiance: 5% + 0 + 0.05 = ~10%.
  - Override 4: Trust 25, insist → trust -10 = 15. Now trust ≤ 20: defiance = 5% + 0 + 0.10 = ~15%.
  - Trust ≤ 20 triggers redemption event (SPEC §3, V2B spec).
- **Talleyrand dismissal problem:** Redemption options for combat marshals are: grant autonomy, admin role, or dismiss. But Talleyrand is NOT a military unit (SPEC EC-M: "Talleyrand cannot be killed"). Can he be dismissed? If yes, France has no diplomat → entire diplomacy system disabled. If no, what are the redemption options for Talleyrand specifically?
- **Severity: Critical.** Fix: Add to SPEC §3 or §S12: "Talleyrand's redemption event offers: [Apologize: trust +15, authority -5] [Replace with Loyalist aide: lose Schemer personality, skill drops to 6, trust resets to 50] [Continue with strained relations: trust stays, authority -10]." Talleyrand cannot be dismissed.

### Additional Discovered Edge Cases

**EC-11: Territory Cession Invalidates MOVE_TO Path (Major)**
- Peace treaty cedes region B. Marshal A has MOVE_TO order with path A→B→C. Region B changes controller. Path is now through foreign territory.
- SPEC EC-E handles marshal PRESENCE in ceded territory (forced relocation). It does NOT handle in-progress MOVE_TO paths through ceded territory.
- **Fix:** When territory controller changes, invalidate all strategic orders whose paths include the changed region. Re-pathfind or cancel with notification.

**EC-12: Vassal Marshal Relationship Overwrite (Minor)**
- SPEC EC-K.1: Vassal marshal joins `world.marshals` with relationships 0. But if this marshal previously fought against French marshals, the relationship formula would have generated values. Those get overwritten to 0.
- This is probably intentional (fresh start), but losing battle-earned rivalry feels odd narratively.
- **Fix:** Document as intentional: "Assimilated vassal marshals start with clean diplomatic slate. Previous hostilities are forgiven."

**EC-13: Feasibility for Impossible Action (Minor)**
- Player asks "what would it take to ally Britain?" (at war, off-map, can't conquer). The formula would return a very low score (WAR base is n/a for alliance — must transition through ARMISTICE → PEACE → ... → ALLIANCE). Feasibility should recognize this requires MULTIPLE state transitions and report the first step, not the final goal.
- **Fix:** Feasibility should detect multi-step transitions and respond: "An alliance with Britain requires first establishing peace, then building through several stages. The first step — armistice — would require..."

**EC-14: Bankruptcy + Treaty Signing (Minor/Exploit)**
- Player at 0 gold agrees to pay 200g/turn. SPEC EC-MM: gold floor 0, clause defaults after 3 defaults, -5 relation/turn. Player could exploit: sign treaties they can't afford to get immediate benefits (peace), then default on payments.
- Mitigation exists (relation penalty, treaty suspension). But is 3 turns of free benefits worth -15 relation? Probably not exploitable in practice.
- **Severity: Minor exploit.** Mitigated by existing penalty system.

**EC-15: Two Blocking Dialogues Simultaneously (Major)**
- Sabotage discovered (blocking, type 3) same turn as AI proposal arrives (blocking, type 3). Both want to be `pending_diplomatic_dialogue`. Only one can exist.
- Order of operations: Sabotage discovery happens during Morning Dispatch building. AI proposal delivered after dispatch. So sabotage fires first, sets `pending_diplomatic_dialogue`. AI proposal must wait in `diplomatic_queue`.
- **Gap:** Is this order of operations explicitly documented? If the AI proposal fires first (during AI phase before dispatch), sabotage discovery would be blocked.
- **Fix:** Add to SPEC: "Sabotage discovery is checked AFTER AI proposals are delivered. Priority: AI proposals first (blocking), sabotage waits for next turn if proposal pending." OR document the opposite: "Sabotage discovery fires during dispatch (before AI delivery), takes priority."

**EC-16: Strategic HOLD + Diplomatic State Change (Major)**
- Marshal on HOLD order in border region. Peace signed with adjacent nation. HOLD is still active — marshal "holds" a position that's no longer threatened. Aggressive marshals on HOLD "sally" (attack adjacent). Could sally attack a nation you just signed peace with.
- **Severity: Major.** Same fix as EC-3: auto-cancel military orders on diplomatic state change.

**EC-17: Counter-Offer at 0 DP (Minor)**
- SPEC §2d: Counter-offers are free to ACCEPT. Renegotiation costs 1 DP. Player at 0 DP can accept the counter-offer but can't renegotiate.
- If Schemer bias in DESIGN pushes recommendation toward "Renegotiate" (because Talleyrand wants to modify terms), player can't afford it.
- **Fix:** When DP < renegotiation cost, Talleyrand's recommendation should acknowledge it: "I'd suggest we renegotiate, but we lack the diplomatic capital. Accept or reject — those are our options."

**EC-18: Carved Vassal Contiguity Break (Major)**
- Carved vassal has 3 regions: A-B-C (contiguous). Enemy retakes B. Now A and C are disconnected.
- SPEC §8f: "Original owner captures region → carved vassal loses it. All regions lost → entity dissolves." But partial loss creating non-contiguous chunks is not addressed.
- **Fix:** Add to SPEC §8f: "If region loss breaks contiguity, the carved vassal retains the largest contiguous chunk. Disconnected regions revert to the original owner's control (contested)."

**EC-19: Give Vassal Territory in Peace Treaty (Exploit)**
- France at war with Britain AND Prussia. Saxony is French vassal. Player proposes peace to Prussia, offering Saxony's Dresden as territory sweetener. Can you trade your vassal's territory?
- SPEC §7a includes Territory as a clause type. SPEC EC-LL says French treaties apply to vassal territory (PUPPET/SATELLITE). But AUTONOMOUS vassals have independent territory.
- **Gap:** No explicit check preventing the player from ceding vassal territory in treaties. This could anger the vassal (loyalty -??) or be blocked entirely.
- **Fix:** Add to SPEC §7: "Ceding vassal territory in a treaty: PUPPET/SATELLITE = allowed (loyalty -20 per region). AUTONOMOUS = blocked (vassal must consent, which they won't)."

**EC-20: Armistice Cooldown + Alliance Cascade (Minor)**
- 5-turn armistice cooldown per pair. Alliance cascade forces war declaration. Does cascade bypass armistice cooldown?
- SPEC §5b.2 defines cooldown. SPEC §5b.3 defines alliance cascade. No explicit interaction.
- **Fix:** Add to SPEC §5b.3: "Alliance cascade war declarations bypass armistice cooldowns (forced entry into war)."

**EC-21: Mission Pause During Defied Proposal (Minor)**
- SPEC §2e: "Proposals interrupt missions temporarily (pause for 1 transit turn, resume on return)." If Talleyrand defies and the proposal takes longer (renegotiation), the mission stays paused for 2+ turns.
- **Gap:** Does mission resume after renegotiation? Or only after the original proposal resolves?
- **Fix:** Add to SPEC §2e: "Mission resumes when Talleyrand returns to IDLE state (after all proposal resolution, including renegotiation)."

**EC-22: Advisory Question While Proposal In Transit (Minor)**
- SPEC §2d: During IN_TRANSIT, Talleyrand "CAN continue missions and respond to AI proposals." DESIGN advisory system: player asks "what about Austria?" while Talleyrand is carrying a proposal to Prussia.
- Can Talleyrand answer advisory questions while IN_TRANSIT? Narratively awkward (he's physically traveling). But mechanically useful.
- **Current state:** DESIGN doesn't restrict advisory during IN_TRANSIT. SPEC says Talleyrand can respond to AI proposals during transit.
- **Fix:** Document explicitly: "Advisory questions available during IN_TRANSIT (Talleyrand's network of agents keeps him informed). Proposal creation blocked during IN_TRANSIT (only one proposal at a time)."

**EC-23: War Declaration While Proposal In Transit (Critical)**
- Player sends peace proposal to Prussia (Talleyrand IN_TRANSIT). Same turn or next turn, player declares war on Austria. Austria is allied with Prussia (DEFENSIVE_ALLIANCE). Alliance cascade: Austria + Prussia enter WAR with France. But France ALSO has a peace proposal in transit to Prussia.
- Does the cascade cancel the in-transit proposal? Prussia is now (re)at-war with France via cascade, while simultaneously receiving a peace offer from France.
- **Fix:** Add to SPEC §5c: "War declaration cascade that involves a nation with an in-transit proposal: proposal auto-cancelled, DP refunded, notification to player." This also covers: player declares war on the same nation they just sent a proposal to.

---

## Task 3: Building Blocks Compliance (12/15)

### 1. Enemy AI Uses Same Systems (4/5)

**Mechanics:** AI uses the same acceptance formula (SPEC §9b: "Same acceptance formula. No cheating."), same DP costs (SPEC §4b: "Enemy diplomats use same costs"), same cooldowns, same state transition rules. AI proposals execute through the same executor actions. ✓

**Conversation layer:** AI does NOT route through DESIGN's dialogue engine. AI diplomatic decisions are made by the priority-based decision tree (SPEC §9a P1-P7), not by "talking to their diplomat." This is correct — the conversation layer is player-facing UI, like the objection popup. The Building Blocks principle requires shared MECHANICS, not shared UI.

**Asymmetry concern:** Talleyrand's Schemer bias can handicap the player (biased recommendations, inflated concessions). Enemy AI doesn't suffer equivalent handicap from their diplomats' personalities. DESIGN §10e: "v1 scope: Personality affects response TEXT only, not AI behavior." This means Metternich's Schemer personality doesn't actually affect Austria's AI decisions — it only flavors the text the player sees.

This is intentional (the player's relationship with Talleyrand IS the game), but it's a documented asymmetry. Future v2 should wire enemy diplomat personalities into AI behavior for full Building Blocks parity.

### 2. Executor Is Deterministic (4/5)

**Template selection:** DESIGN §4a keys templates by `(situation, game_bucket, specificity)` — all derived from game state. Deterministic given the same inputs. ✓

**Schemer asides:** DESIGN §4d mentions 2+ variants per situation. If selected by `random.choice()`, this is random PRESENTATION. The mechanical outcome (which options are available, what the formula returns) is identical regardless of which aside text is shown. ✓

**70/30 Schemer bias:** DESIGN §5c: "70% template ignores bias. 30% shifts recommendation by one option." How is the 30% determined?

- If condition-based (threat > 50 = always shift): deterministic. ✓
- If `random.random() < 0.3`: random presentation. Still technically OK (Golden Rule #6: "LLM never affects mechanics" — bias only affects recommendation display, not formula).

**Gap:** The 70/30 mechanism isn't fully specified. Recommend making it condition-based: "Bias triggers when ALL bias conditions are met (e.g., threat > 50 for aggressive proposals). When conditions NOT met, recommendation is formula-optimal." This eliminates randomness entirely.

### 3. Single Source of Truth (4/5)

**Acceptance formula:** Lives in `diplomacy.py` (one function: `_calculate_acceptance()`). Called from 3 places: player proposal execution, AI response evaluation, feasibility request. All three call the SAME function. ✓

**Combat modifiers:** Diplomacy adds NO combat modifiers. Threat level is diplomatic-only. War score is diplomatic-only. No intersection with `marshal.py` get_attack_modifier/get_defense_modifier. ✓

**Schemer bias double-application risk:** Bias is applied in the DESIGN template layer AFTER the formula returns. The formula function itself contains no bias. Two separate code paths: `calculate_acceptance()` (pure) and `apply_schemer_bias()` (presentation). As long as these stay in separate files (`diplomacy.py` vs `diplomatic_dialogue.py`), double-application is structurally prevented. ✓

**Minor concern:** SPEC §6c.1 defines harshness values. DESIGN §3b references harshness for Schemer bias direction ("softens harsh proposals"). The harshness calculation should also live in `diplomacy.py` (single source), with DESIGN reading the value. Currently both specs reference harshness but neither specifies where the calculation function lives. Pin it to `diplomacy.py`.

---

## Task 4: Session Plan Feasibility (12/15)

### 1. Dependency Graph (4/5)

```
SPEC 1A (Map Expansion)
    └──→ SPEC 1B (Nations + Marshals)
              └──→ SPEC 2 (States + Formula)
                        ├──→ SPEC 3A (Talleyrand Commands)
                        │         ├──→ DESIGN A (Dialogue Foundation)
                        │         │         └──→ DESIGN B (Advisory + Conversations)
                        │         │                   └──→ DESIGN C (Objections + Confrontation)
                        │         │                             └──→ DESIGN D (UI + Polish)
                        │         └──→ SPEC 4 (Vassals + Treaties)
                        │                   └──→ DESIGN B (vassal proactive suggestions)
                        └──→ SPEC 3B (AI Proposals + Popups)
                                  └──→ DESIGN C (incoming proposal voice + confrontation)

SPEC 5 (Defiance + Diplomatic Ledger UI) ──→ DESIGN C (defiance wiring)

SPEC 6 (Polish) ──→ after all others
```

**Parallelization opportunities:**
- SPEC 3A ‖ SPEC 3B (independent: player commands vs AI proposals)
- DESIGN A ‖ SPEC 4 (independent: dialogue foundation doesn't need vassals)
- DESIGN B ‖ SPEC 5 (partially: advisory doesn't need defiance, but proactive vassal suggestions need SPEC 4)

**Can any DESIGN session start before SPEC dependencies?**
- DESIGN A needs SPEC 3A (parser routing, executor actions) → NO early start.
- DESIGN B could START before SPEC 4 (implement advisory without vassal triggers, add vassal triggers later) → PARTIAL early start.
- DESIGN C needs SPEC 3B + SPEC 5 → NO early start.
- DESIGN D needs everything → NO early start.

**Minimum critical path:** SPEC 1A → 1B → 2 → 3A → 3B → 4 → 5 → DESIGN A → B → C → D = 11 sequential steps. With parallelization: SPEC 1A → 1B → 2 → (3A ‖ 3B) → (4 ‖ DESIGN A) → (5 ‖ DESIGN B) → DESIGN C → DESIGN D = 9 steps.

### 2. Risk Assessment (4/5)

| Session | Risk | Why |
|---------|------|-----|
| SPEC 1A | **EXTREME** | 13→19 regions. Every test referencing region names/adjacency breaks. "100+ test updates" estimated. This is the highest-risk session in the entire phase. |
| SPEC 1B | **HIGH** | 4 new marshals + 2 new nations. Balance implications. Starting positions matter. |
| SPEC 2 | MEDIUM | New file, clean formula. Low blast radius. |
| SPEC 3A | **HIGH** | Parser routing changes affect ALL command parsing. Regression risk on existing commands. |
| SPEC 3B | **HIGH** | AI behavior changes + popup flow. Complex state management. |
| SPEC 4 | MEDIUM | New vassal subsystem, mostly isolated. |
| SPEC 5 | MEDIUM | Defiance follows V2b pattern closely. Diplomatic Ledger is new Godot screen but follows existing pattern. |
| DESIGN A | MEDIUM | New dialogue state machine. Well-defined but complex state transitions. |
| DESIGN B | LOW | Templates and advisory. Mostly string construction. |
| DESIGN C | **HIGH** | Sabotage confrontation + defiance wiring. Most complex cross-system integration. |
| DESIGN D | LOW | UI polish, Schemer bias calibration. |

**Minimum viable slice:** SPEC 1A + 1B + 2 + 3A + 3B + DESIGN A = playable diplomacy with conversation layer, without vassals, defiance, or full advisory. This delivers ~70% of the value in ~60% of the sessions.

### 3. Line Count Reality Check (4/5)

| Metric | Value |
|--------|-------|
| Current backend Python | **45,389 lines** |
| SPEC estimate | ~1200 new + ~400 modified |
| DESIGN estimate | ~1000 new + ~400 modified |
| Total new code | ~2200 lines |
| Total modifications | ~800 lines |
| New test code (250 tests × ~15 lines avg) | ~3750 lines |
| **Total new lines** | **~6750 lines** |
| % increase (backend) | ~15% |

**Per-session:** 6750 / 10 sessions = ~675 lines/session. This is ambitious but achievable — Phase 7b sessions averaged ~500-800 lines. The high-risk sessions (1A, 1B, 3A) will be dominated by test updates and modifications rather than new code.

**Concern:** The ~250 test estimate may be low. Phase 7b added ~246 tests for multi-marshal coordination alone. Diplomacy is significantly more complex (5 nations, acceptance formula, treaties, vassals, AI behavior). A more realistic estimate: 350-400 tests. At 15 lines average: 5250-6000 lines of test code. Total effort: ~8000-9000 lines across 10 sessions = ~800-900 lines/session. Still achievable but tight.

---

## Task 5: Fun Audit — The Player Journey (8/10)

### Setup
France at war with Prussia (war_score +10), hostile Austria (relation -30), friendly Saxony (relation +25), distant Britain (at war, unreachable). Talleyrand trust 55, authority 60. DP: 4/turn (SPEC §4a formula).

### Turn-by-Turn Walkthrough

**Turn 1 — Exploration**
- **Player types:** "Talleyrand, what's our diplomatic situation?"
- **DESIGN routes:** Advisory → overview assessment (§8b Example 4, variant selected)
- **Player sees:** Talleyrand gives a nation-by-nation summary in his urbane voice. Prussia (war, they're weakening), Austria (hostile, Metternich is watching), Saxony (friendly, useful), Britain (war, untouchable). [Ask about specific nation] [Dismiss]
- **Executes:** Nothing — informational only, 0 DP.
- **Fun:** ★★★★☆ — Immediately orients the player. Feels like consulting an advisor, not reading a spreadsheet. The personality shines through word choice.

**Turn 2 — Deep Dive**
- **Player types:** "Who's the bigger threat, Austria or Britain?"
- **DESIGN routes:** Advisory → compare_threats (§8b Example 1)
- **Player sees:** Talleyrand compares: Austria is "urgent" (hostile, army on border, Metternich is scheming), Britain is "enduring" (at war but off-map, funding your enemies). Recommends addressing Austria first.
- **Executes:** Nothing — 0 DP.
- **Fun:** ★★★★☆ — Teaches the distinction between "urgent threat" and "structural threat." Player starts forming strategy.

**Turn 3 — Feasibility Check**
- **Player types:** "What would it take to get peace with Prussia?"
- **DESIGN routes:** Feasibility (§2g, Template T15 or T27)
- **SPEC calculates:** base(30) + war_score(10×0.3=3) + relation(-60/2=-30) + threat(0) + sweetener(0) + skill(+8) + personality(-5 Hawk) = 6 → REJECT range → "Nearly impossible"
- **Player sees:** Talleyrand identifies the largest negative factor (relation: "Their hostility runs deep, Sire"). Suggests military pressure as the most promising lever. Difficulty: "Nearly impossible."
- **Fun:** ★★★★★ — The best teaching moment. Player learns WHY diplomacy fails, not just that it fails. The guidance is actionable: "Win more battles, then try again."

**Turn 4 — Start a Mission**
- **Player types:** "Talleyrand, improve our relations with Austria"
- **DESIGN routes:** Mission recommendation (MEDIUM → confirm)
- **SPEC executes:** IMPROVE_RELATIONS mission starts. 1 DP/turn. +5 relation/turn (×1.5 for skill 10 = +7/turn).
- **Player sees:** Talleyrand: "A wise investment. Metternich can be... persuaded. I shall begin making overtures." [Confirm: 1 DP/turn] [Cancel]
- **Fun:** ★★★☆☆ — Functional but not dramatic. The player makes a strategic investment. Payoff comes later.

**Turn 5 — Military Action**
- **Player types:** Military commands — attacks Prussia, wins a battle. War score rises to +23.
- **Fun:** ★★★★☆ — Military success feels connected to diplomatic prospects. Player thinks: "one more win and I can negotiate."

**Turn 6 — Approach Prussia (Vague)**
- **Player types:** "Talleyrand, deal with Prussia"
- **DESIGN routes:** VAGUE → proposal_options. Template T21 (WAR, winning_slightly).
- **Player sees:** Three options ranked by Schemer bias:
  1. "Generous peace — offer concessions for lasting stability" (Talleyrand recommends this)
  2. "Push for favorable terms — they're weakening"
  3. "Armistice — buy time without committing"
- **Executes:** Player picks option → transitions to proposal_confirm with specific terms.
- **Fun:** ★★★★★ — The VAGUE path is where Talleyrand shines. The options feel like advice from a CHARACTER, not a menu. Schemer bias subtly pushes toward generous terms (Talleyrand's vision of European balance).

**Turn 7 — Talleyrand Objects**
- **Player chose "push for favorable terms"** (against Talleyrand's recommendation)
- **DESIGN routes:** proposal_confirm → Talleyrand objects (MODERATE, Template T8)
- **Player sees:** Talleyrand: "Your Majesty, Hardenberg is a Hawk — these terms will be seen as a provocation, not a negotiation. I would counsel more... generosity." [Send my terms as ordered] [Accept Talleyrand's modification] [Cancel]
- **Player insists.** Defiance roll: base 5% + 0 + 0 ± variance = ~5%. Roll passes (no defiance). Talleyrand obeys reluctantly. DP spent. IN_TRANSIT.
- **Fun:** ★★★★★ — PEAK DRAMA. The player overrode their advisor. Tension: was Talleyrand right? Will it work? The 5% defiance chance adds real stakes.

**Turn 8 — Rejection**
- **Morning Dispatch:** Austria update (+7 relation this turn), Talleyrand returns.
- **SPEC resolves:** Harsh terms → acceptance score too low → REJECT.
- **Player sees:** Hardenberg's contemptuous rejection (Hawk voice: "Do not mistake pragmatism for weakness"). Talleyrand commentary: "I did warn Your Majesty..."
- **Executes:** 3-turn cooldown on Prussia proposals. Relation drops further.
- **Fun:** ★★★★☆ — The consequence teaches. Talleyrand's "I told you so" builds the trust-calibration meta-game. Player thinks: "maybe I should listen next time."

**Turn 9 — Regroup**
- **Morning Dispatch:** "DIPLOMATIC REPORT: Talleyrand observes that Austria's stance is softening. Current relations show improvement." Austria relation now -16.
- **Player types:** Military commands — continues fighting Prussia for better war score.
- **Fun:** ★★★☆☆ — Transition turn. The mission running in background provides satisfying progress.

**Turn 10 — Progress**
- Austria relation now -9. Mission paying off.
- **Proactive suggestion fires:** (DESIGN §5d trigger: acceptance formula crossed 50 for Austria non-aggression)
- **Player sees:** "DIPLOMATIC REPORT: Talleyrand believes the time may be approaching for a formal arrangement with Austria. A non-aggression pact appears... achievable." [Ask Talleyrand to elaborate] [Dismiss]
- **Fun:** ★★★★☆ — The proactive suggestion feels intelligent. Talleyrand noticed a window opening. Player feels like they have a smart advisor.

**Turn 11 — Dual Track**
- **Player types:** "Talleyrand, propose non-aggression to Austria"
- **SPEC calculates:** base(30) + relation(-9/2=-4) + threat(?) + skill(+2 Talleyrand vs Metternich) + personality(+5 Schemer) = ~33. Hmm, still COUNTER range. With some gold sweetener: +50 gold/turn = +1.5→+1, gold lump 200 = +1. Total ~35 → COUNTER.
- **Player sees:** Talleyrand fills in suggested terms (gold sweetener). "Metternich will want a gesture. I suggest 100 gold per turn." [Send it] [Modify terms] [Cancel]
- **Fun:** ★★★★☆ — Talleyrand's term suggestion is genuinely useful. The player learns that diplomacy costs money.

**Turn 12 — Sabotage (Hypothetical Branch)**
- *If defiance had triggered at Turn 7*: Talleyrand softened the terms sent to Prussia.
- Discovery: 40% base + 10%/turn cumulative. Turn 8: 40%, Turn 9: 50%, Turn 10: 60%, Turn 11: 70%. By turn 12, highly likely discovered.
- **BLOCKING popup (Template T17):** "Your Majesty... it has come to my attention that the terms Talleyrand presented to Hardenberg differed from your instructions. You ordered [harsh terms]. Talleyrand delivered [softened terms]."
- **Talleyrand's defense:** "I judged the terms would have insulted Hardenberg beyond recovery. A diplomat must sometimes interpret, not merely translate."
- [Confront: trust -10, authority +5, 5-turn cooldown] [Overlook: trust +3]
- **Fun:** ★★★★★ — THE dramatic highlight of the arc. The reveal is theatrical. The choice is meaningful. The player's reaction tells them something about their own playstyle.

**Turn 13 — Austria Responds**
- **SPEC resolves:** Austria counter-offers non-aggression with modified terms (wants French protection guarantee).
- **Player sees:** BLOCKING popup. Metternich's response in Schemer voice: "Austria is willing to formalize... understanding. With one small addition."
- Talleyrand commentary: "Metternich accepted too quickly. He's getting something we didn't see."
- [Accept counter] [Reject] [Renegotiate: 1 DP]
- **Fun:** ★★★★☆ — Talleyrand's paranoia about Metternich is great characterization. The counter-offer mechanic creates negotiation feel.

**Turn 14 — Coalition Warning**
- Threat level ticking up (French victories + aggressive diplomacy).
- **Morning Dispatch:** "DIPLOMATIC REPORT: Talleyrand urgently reports that Metternich's 'understanding' may be a prelude to armed mediation. Austria's military preparations are... concerning."
- Austria relation positive now, but threat > 50 → Schemer bias overstates risk (one tier worse). Talleyrand reports the situation as worse than it is.
- **Fun:** ★★★★☆ — Schemer bias creates genuine uncertainty. IS Austria preparing to attack? Or is Talleyrand exaggerating? The player who checks the Ledger sees the real numbers. The player who trusts blindly might panic.

**Turn 15 — Strategic Choice**
- Prussia cooldown expired. Austria non-aggression signed.
- **Player types:** "Talleyrand, try peace with Prussia one more time — generous terms this time"
- War score now +40 (from multiple victories). Relation improved slightly from time passing.
- **SPEC calculates:** base(30) + war_score(+40×0.3=+12) + relation(-45/2=-22) + skill(+8) + personality(-5) + gold sweetener(+5) = 28. Still REJECT, but with a big military victory: Military Supremacy could push it over.
- Talleyrand: "We're close, Sire. If we could take Berlin..." [Send anyway] [Push for Berlin first] [Cancel]
- The player has a clear military goal (capture Berlin for Military Supremacy +25 bonus) that would make peace achievable.
- **Fun:** ★★★★★ — The game is teaching the player that DICTATED peace requires overwhelming force. The military-diplomatic feedback loop is working perfectly. The player has a clear goal and a path to achieve it.

### Overall Arc Rating: **8/10**

**What works brilliantly:**
- Talleyrand as a CHARACTER, not a menu. Every exchange reveals personality.
- The Schemer bias meta-game: trust vs verify. The Ledger exists for players who want to check the numbers. Trusting Talleyrand is a valid (if risky) playstyle.
- Military-diplomatic feedback loop: you can't negotiate from weakness, you can't fight forever. Both systems reinforce each other.
- Sabotage discovery is a DRAMATIC highlight — no strategy game has this moment.
- Feasibility teaching: the player learns WHY things fail, not just that they fail.
- The acceptance formula's transparency (via feasibility and Ledger) prevents "I don't understand why this failed" frustration.

**What needs attention:**
- Turns 4-5 and 9-10 can feel like waiting. The mission system is strategically sound but not moment-to-moment exciting. Proactive suggestions help, but the player needs something to DO diplomatically while missions run.
- Template variety over 40+ turns: 27 core templates × game state buckets = hundreds of combinations, but players will notice patterns. The 4 advisory variants help. LLM mode solves this completely, but mock mode needs monitoring.
- Hawks are HARD to deal with (by design), but a player facing two Hawks (Castlereagh + Hardenberg) might feel stuck diplomatically. The "conquer and dictate" path is always available but not all players want it.
- The fun depends heavily on the player ENGAGING with Talleyrand. A player who just types "propose peace to Prussia" every time misses the advisory game. Proactive suggestions help push toward engagement.

---

## Task 6: Golden Rule Compliance (9/10)

### Per-Rule Check

| # | Rule | Status | Notes |
|---|------|--------|-------|
| 1 | Combat modifiers: single source in marshal.py | ✓ CLEAN | Diplomacy adds NO combat modifiers. Threat/war_score are diplomatic-only. |
| 2 | All numbers to Godot: int() | ⚠ GAP | Acceptance formula uses float math (×0.3, /2). Final score must be int() before reaching Godot. Relation/2 produces float. Fix: `int(round(acceptance_score))` at formula return. |
| 3 | All marshals in ONE dict | ✓ CLEAN | `world.diplomats` is a NEW entity type dict, not a marshal split. `world.vassals` and `world.carved_vassals` are separate entity types. No marshal dict splitting. |
| 4 | State clearing AFTER reading | ✓ CLEAN | `proposal_in_transit` cleared after response processed. `pending_diplomatic_dialogue` cleared after player responds. |
| 5 | Enemy AI uses SAME executor | ✓ CLEAN | AI uses same acceptance formula, DP costs, state transitions. Same `executor.execute()` for military actions. |
| 6 | LLM never affects mechanics | ✓ CLEAN | Mock and LLM produce identical mechanical outcomes. Template selection is deterministic. Schemer bias affects display only. |
| 7 | Port 8005 | ✓ CLEAN | New endpoints on same FastAPI server. |

### Serialization Field Inventory

**26 new WorldState fields (SPEC §S13 + DESIGN §2b):**

| # | Field | Type | Default | to_dict | from_dict |
|---|-------|------|---------|---------|-----------|
| 1 | diplomatic_states | Dict[str, str] | starting states | ✓ S13 | ✓ S13 |
| 2 | nation_relations | Dict[str, int] | starting relations | ✓ S13 | ✓ S13 |
| 3 | diplomatic_points | int | 0 | ✓ S13 | ✓ S13 |
| 4 | max_diplomatic_points | int | 5 | ✓ S13 | ✓ S13 |
| 5 | active_treaties | Dict[str, List[Dict]] | {} | ✓ S13 | ✓ S13 |
| 6 | war_scores | Dict[str, int] | {} | ✓ S13 | ✓ S13 |
| 7 | ~~pending_diplomatic_proposal~~ | ~~Optional[Dict]~~ | — | — | — |
| 8 | proposal_in_transit | Optional[Dict] | None | ✓ S13 | ✓ S13 |
| 9 | active_diplomatic_mission | Optional[Dict] | None | ✓ S13 | ✓ S13 |
| 10 | ai_proposal_cooldowns | Dict[str, int] | {} | ✓ S13 | ✓ S13 |
| 11 | player_proposal_cooldowns | Dict[str, int] | {} | ✓ S13 | ✓ S13 |
| 12 | armistice_cooldowns | Dict[str, int] | {} | ✓ S13 | ✓ S13 |
| 13 | threat_level | int | 0 | ✓ S13 | ✓ S13 |
| 14 | vassals | Dict[str, Dict] | {} | ✓ S13 | ✓ S13 |
| 15 | vassal_investment_cooldowns | Dict[str, int] | {} | ✓ S13 | ✓ S13 |
| 16 | diplomatic_queue | List[Dict] | [] | ✓ S13 | ✓ S13 |
| 17 | undetected_sabotages | List[Dict] | [] | ✓ S13 | ✓ S13 |
| 18 | continental_system_members | List[str] | [] | ✓ S13 | ✓ S13 |
| 19 | decisive_battles | List[Dict] | [] | ✓ S13 | ✓ S13 |
| 20 | war_battle_records | Dict[str, Dict] | {} | ✓ S13 | ✓ S13 |
| 21 | carved_vassals | Dict[str, Dict] | {} | ✓ S13 | ✓ S13 |
| 22 | previous_treaties | List[Dict] | [] | ✓ S13 | ✓ S13 |
| 23 | defection_cascade_fired | Dict[str, int] | {} | ✓ S13 | ✓ S13 |
| 24 | nation_starting_regions | Dict[str, List[str]] | per-nation | ✓ S13 | ✓ S13 |
| 25 | diplomats | Dict[str, DiplomaticRepresentative] | 5 diplomats | ✓ S13 | ✓ S13 |
| 26 | pending_diplomatic_dialogue | Optional[Dict] | None | ✓ DESIGN 2b | ✓ DESIGN 2b |

**Row 7 conflict:** `pending_diplomatic_proposal` in SPEC §S13 is superseded by `pending_diplomatic_dialogue` in DESIGN. Must be removed from SPEC. See GAP-4.

**New entity class:**
- `DiplomaticRepresentative`: name, nation, personality, skill, biography, trust. Full to_dict/from_dict specified in SPEC §S13. ✓

**All fields have serialization coverage specified.** The test_serialization_enforcement.py pattern will catch any implementation gaps.

---

## Critical Findings (Must Fix Before Implementation)

| ID | Finding | Spec | Section | Fix |
|----|---------|------|---------|-----|
| C1 | DP deduction timing in conversation flow unspecified — player could lose DP on conversation start, not "Send it" confirmation | DESIGN | §9b | Add explicit: "DP deducted on `execute_proposal`, not conversation start. Cancel = 0 DP." |
| C2 | `pending_diplomatic_proposal` (SPEC) conflicts with `pending_diplomatic_dialogue` (DESIGN) — overlapping fields for same purpose | SPEC §S13, DESIGN §2b | Both | Remove `pending_diplomatic_proposal` from SPEC. All proposal presentation routes through `pending_diplomatic_dialogue`. |
| C3 | Strategic military orders (PURSUE, MOVE_TO, HOLD w/ sally) don't auto-cancel on diplomatic state change from WAR to non-WAR | SPEC §5b | Missing | Add auto-cancellation rule: peace/armistice cancels attack-oriented orders targeting that nation. |
| C4 | Talleyrand trust redemption at ≤20 has no specified behavior — combat marshal options (dismiss, autonomy) don't apply to a diplomat | SPEC §3, §S12 | Missing | Add Talleyrand-specific redemption: [Apologize: trust+15, authority-5] [Replace with Loyalist: skill drops to 6, trust 50] [Strained: authority-10]. No dismiss option. |
| C5 | War declaration cascade can fire while peace proposal is in transit to the same nation — contradictory diplomatic actions | SPEC §5c | Missing | Auto-cancel in-transit proposals when cascade creates WAR with target. Refund DP. Notify player. |

## Major Findings (Should Fix)

| ID | Finding | Spec | Section | Fix |
|----|---------|------|---------|-----|
| M1 | "Specify your own" clause-selection UI path undefined for text terminal interface | DESIGN | §3b, §9b | Define the clause-selection flow: numbered list of clause types, player types "add gold 200" style commands. |
| M2 | Save/load mid-dialogue: load-side popup display trigger unspecified in Godot | DESIGN | §9a | Add: "On game load, check `pending_diplomatic_dialogue`. If present and blocking, display popup immediately." |
| M3 | 0 DP + vague dialogue shows unaffordable options without indication — frustrating UX | DESIGN | §3a | Display DP cost per option. Mark unaffordable with "(insufficient DP)". Talleyrand acknowledges: "We lack the capital..." |
| M4 | Two blocking dialogues (sabotage + AI proposal) same turn: order of operations undefined | SPEC §3c, §9a | Missing | Specify: AI proposals delivered at turn start. Sabotage checked during dispatch. Whichever fires first sets `pending_diplomatic_dialogue`, other queues. |
| M5 | Territory cession invalidates in-progress MOVE_TO paths — no path re-calculation or cancellation on treaty execution | SPEC §5b, §7a | Missing | On territory controller change, invalidate strategic orders with affected paths. Re-pathfind or cancel with notification. |
| M6 | Carved vassal contiguity break on partial region loss undefined | SPEC §8f | Missing | Largest contiguous chunk retained. Disconnected regions revert to original owner (contested). |
| M7 | Vassal territory can be ceded in peace treaties with no loyalty penalty specified | SPEC §7, §8c | Missing | PUPPET/SATELLITE: allowed, loyalty -20/region. AUTONOMOUS: blocked (vassal must consent). |
| M8 | Acceptance score uses float math (×0.3, /2) — final value must be explicitly int() per Golden Rule #2 | SPEC §6a | Missing | Add: `acceptance_score = int(round(raw_score))` at formula return. |
| M9 | Proactive suggestion fires for vassal that just rebelled same turn — existence check missing | DESIGN §5d | Missing | Guard: check vassal exists in `world.vassals` before generating suggestion. |

## Minor Findings (Nice to Have)

| ID | Finding | Spec | Section | Fix |
|----|---------|------|---------|-----|
| m1 | 70/30 Schemer bias mechanism not fully specified (condition-based vs random) | DESIGN | §5c | Make condition-based for determinism: "Bias triggers when ALL conditions met." |
| m2 | Schemer bias in MEDIUM path has indirect mechanical effect (inflated concessions) — document as intentional | DESIGN | §3b | Add design note: "This is intentional — Talleyrand's bias DOES affect outcomes through player trust. The Ledger exists as the verification tool." |
| m3 | Feasibility for multi-step transitions (WAR→ALLIANCE) should report first step, not final goal | SPEC | §2g | Detect multi-step, respond with first achievable step. |
| m4 | Suppressed AI proposals (max 1/turn) should document behavior | SPEC | §9a | Add: "Suppressed proposals not queued; AI re-evaluates each turn." |
| m5 | Counter-offer recommendation at 0 DP should acknowledge renegotiation is unavailable | DESIGN | §6 | "I'd suggest renegotiating, but we lack the diplomatic capital." |
| m6 | Harshness calculation function location unspecified | SPEC §6c.1 | Missing | Pin to `diplomacy.py` (single source). |
| m7 | Vassal marshal assimilation overwrites pre-existing relationships — document as intentional | SPEC | EC-K.1 | "Assimilated vassal marshals start with clean slate." |
| m8 | Advisory questions during IN_TRANSIT narratively awkward but mechanically useful | DESIGN | §8 | Document: "Advisory available during IN_TRANSIT (network of agents). Proposal creation blocked." |
| m9 | Armistice cooldown + alliance cascade interaction undefined | SPEC §5b.2, §5b.3 | Missing | "Alliance cascade bypasses armistice cooldowns." |
| m10 | Mission pause during renegotiation — resume timing unclear | SPEC | §2e | "Mission resumes when Talleyrand returns to IDLE (after all resolution including renegotiation)." |
| m11 | Proactive suggestion → elaborate should route to advisory type (not always proposal_options) | DESIGN | §5d | Map trigger type to dialogue type: threat → advisory, opportunity → proposal_options, loyalty → advisory. |

---

## Innovation & Fun Assessment

### What Makes This Special

**No strategy game has conversational diplomacy with a character who has opinions.** EU4, CK3, HOI4, Victoria 3, Civilization — they all use menus. You click "Propose Peace," fill in checkboxes, click "Send." It's efficient but soulless. This game makes you TALK to Talleyrand, and he talks BACK.

Three unique gameplay layers:

1. **The Diplomatic Game** (formula engine) — negotiate treaties, manage alliances. Every strategy game has this. But the acceptance formula is unusually transparent: feasibility requests tell the player WHY things fail, not just that they failed. This alone is better than most.

2. **The Advisory Game** (trust calibration) — Talleyrand is 70% honest, 30% self-serving. The player must calibrate trust over time. Check the Ledger to verify his claims. Notice when his predictions don't match outcomes. This meta-game of "reading" your advisor is genuinely novel. No other game does this.

3. **The Relationship Game** (defiance/sabotage) — Over 30+ turns, the player builds a relationship with Talleyrand through choices: override or trust, confront or overlook, punish or forgive. The sabotage discovery moment (Template T17) is the most dramatic moment in the entire game — discovering your own advisor betrayed you.

### What's Rock Solid

- **Acceptance formula is fully deterministic.** No RNG in acceptance decisions. Same inputs = same output. Mock and LLM modes are mechanically identical. This is the foundation and it's unshakeable.
- **State machine is well-defined.** 8 diplomatic states with strict adjacency transitions. No state can be "skipped." Downgrade transitions have their own rules. Clean.
- **Edge cases are exhaustively documented.** 51 in SPEC + 23 in this audit = 74 identified. Most have specified behavior. The gaps found in this audit are fixable.
- **The mock mode guarantee** means this is not AI-dependent vaporware. The entire system works with templates. LLM adds polish but isn't required. This makes the system shippable.
- **The military-diplomatic feedback loop** creates natural campaign arcs. You can't talk your way out of everything (acceptance formula requires leverage). You can't fight forever (threat level, coalition risk). Both arms reinforce each other.

### What Needs Watching

- **Template fatigue over long games.** 27 templates × state buckets = hundreds of combinations, plus 4 advisory variants. But a 60-turn game will show patterns. The LLM mode solves this completely, but mock mode needs monitoring in playtesting.
- **Hawks are HARD to negotiate with.** Hardenberg and Castlereagh both have -5 to peace acceptance. A player facing two Hawks might feel diplomacy is futile. This is historically accurate (these nations WERE hard to negotiate with), but needs the Military Supremacy modifier (+25 when holding capital) as the release valve. That path must feel achievable.
- **Waiting turns.** Missions run at +7 relation/turn but take 5-8 turns to meaningfully shift the needle. Proactive suggestions and advisory questions fill the gap, but some turns will feel like "waiting for numbers to change." The military game should be the primary activity during these turns.

### Bottom Line

The design is ambitious, innovative, and sound. The seams between the two specs need the 5 critical fixes above, but the architecture is correct. The fun factor is genuinely high — the Schemer bias meta-game, the sabotage reveal, and the military-diplomatic feedback loop are each individually better than most strategy games' entire diplomacy systems. Together, they're the feature that makes Ink & Iron unique.

**Ship it (after fixing the criticals).**

---

## Re-Audit After Fixes

**Date:** 2026-02-27
**Fixes applied:** 5 Critical, 9 Major, 11 Minor = 25 total findings resolved.
**Cross-reference fix:** §3d → §3e renumbering propagated to both specs (2 references updated).

### Critical Finding Resolution

| ID | Finding | Fix Applied | Verified? | Notes |
|----|---------|-------------|-----------|-------|
| C1 | DP deduction timing unspecified | Added explicit timing to DESIGN §9b: "DP deducted on `execute_proposal`, not conversation start. Cancel = 0 DP." | ✓ RESOLVED | Placed directly in the option action flow where execute_proposal is defined. Data flow is clean: player explores → picks Send → DP deducted → transit begins. |
| C2 | `pending_diplomatic_proposal` conflicts with `pending_diplomatic_dialogue` | Removed field from SPEC §S13, replaced with explanatory comment. All proposal presentation routes through `pending_diplomatic_dialogue`. | ✓ RESOLVED | Verified no remaining references to `pending_diplomatic_proposal` in either spec. Raw data correctly split: `proposal_in_transit` (outgoing) and `diplomatic_queue` (incoming). |
| C3 | Strategic military orders don't auto-cancel on peace | Added §5b.4 with comprehensive auto-cancellation rules for PURSUE, MOVE_TO, HOLD, SUPPORT. Campaign log + dispatch notifications specified. | ✓ RESOLVED | Also covers M5 (territory cession path invalidation) in the same section with re-pathfinding logic. Reverse case (peace→war) explicitly documented as NOT auto-cancelling. |
| C4 | Talleyrand trust redemption at ≤20 has no specified behavior | Added §3d with 3 diplomat-specific options: Apologize (trust+15, authority-5), Replace with Loyalist (skill 6, trust 50, irreversible), Continue (authority-10). No dismiss option. | ✓ RESOLVED | Cross-references updated (old §3d Objections → new §3e). Repeat redemption and post-Replace behavior documented. |
| C5 | War declaration cascade while proposal in transit | Added to §5c: auto-cancel in-transit proposals on cascade, DP refund, notification. Covers both cascade and direct war declaration on target. | ✓ RESOLVED | References EC-NN for mission auto-cancel on the same event. Data flow: cascade fires → check proposal_in_transit target → cancel + refund + notify. |

### Major Finding Resolution

| ID | Finding | Fix Applied | Verified? | Notes |
|----|---------|-------------|-----------|-------|
| M1 | "Specify your own" clause-selection UI undefined | Added terminal UI spec to DESIGN §3b: numbered clause types, add/remove/done/cancel commands, harshness preview on each add. | ✓ RESOLVED | Both mock mode (keyword parsing) and LLM mode (free-text) paths specified. |
| M2 | Save/load mid-dialogue display trigger unspecified | Added to DESIGN §9a: blocking dialogues display immediately on load, non-blocking display on next input. References Godot handler pattern. | ✓ RESOLVED | Follows existing `pending_objection` load pattern. |
| M3 | 0 DP + vague dialogue shows unaffordable options | Added DP cost display per option, "(insufficient DP)" label, Talleyrand dialogue acknowledgment. Example format provided. | ✓ RESOLVED | Soft-blocking prevents frustrating dead-end conversations. |
| M4 | Two blocking dialogues same turn: order undefined | Added to SPEC §9a: AI proposals first (AI phase), sabotage during dispatch. Queuing for second event. Mid-turn resolution. | ✓ RESOLVED | Deterministic order eliminates the race condition. |
| M5 | Territory cession invalidates MOVE_TO paths | Covered in §5b.4 (C3 fix): re-pathfind through friendly territory, cancel with notification if no valid path. | ✓ RESOLVED | Subsection of the broader strategic order auto-cancellation system. |
| M6 | Carved vassal contiguity break undefined | Added to SPEC §8f: largest contiguous chunk retained, disconnected regions revert to original owner (contested). Tie-breaking by income. | ✓ RESOLVED | Clean rule that doesn't require complex multi-region tracking. |
| M7 | Vassal territory cession has no loyalty penalty | Added to SPEC §7a: PUPPET/SATELLITE allowed (loyalty -20/region), AUTONOMOUS blocked (vassal must consent). | ✓ RESOLVED | Scales naturally — ceding 3 regions = -60 loyalty, likely triggering rebellion. |
| M8 | Acceptance score uses float math, needs int() | Added `int(round(raw_score))` to §6a formula definition. References Golden Rule #2. | ✓ RESOLVED | Rounding before truncation prevents systematic bias at thresholds. |
| M9 | Proactive suggestion fires for vassal that just rebelled | Added existence guard to DESIGN §5d: check vassal/nation exists before generating suggestions. | ✓ RESOLVED | Simple guard at the top of the suggestion generation logic. |

### Minor Finding Resolution

| ID | Status | Notes |
|----|--------|-------|
| m1 | ✓ Applied | Schemer bias now fully condition-based (deterministic). 70/30 ratio is emergent. |
| m2 | ✓ Applied | MEDIUM path Schemer bias documented as intentional. Ledger referenced as verification tool. |
| m3 | ✓ Applied | Feasibility for multi-step transitions reports first achievable step. |
| m4 | ✓ Applied | Suppressed AI proposals documented: not queued, AI re-evaluates each turn. |
| m5 | ✓ Applied | Counter-offer at 0 DP: Talleyrand acknowledges constraint, renegotiate soft-blocked. |
| m6 | ✓ Applied | Harshness calculation pinned to `diplomacy.py` (single source). |
| m7 | ✓ Applied | Vassal marshal clean slate documented as intentional design. |
| m8 | ✓ Applied | Advisory available during IN_TRANSIT (network of agents). Proposal creation blocked. |
| m9 | ✓ Applied | Alliance cascade bypasses armistice cooldowns (forced entry). |
| m10 | ✓ Applied | Mission resumes when Talleyrand returns to IDLE (after all resolution including renegotiation). |
| m11 | ✓ Applied | Proactive suggestion trigger-to-dialogue-type routing table added. |

### Re-Scored Task Dimensions

**Task 1: Cross-Document Integration — 27/30 (was 22/30)**

| Dimension | Old | New | Change |
|-----------|-----|-----|--------|
| Mechanical Handoff | 7/10 | 9/10 | C1 (DP timing) + M1 (clause UI) resolve the two gaps. -1 for minor: HOLD cancellation in §5b.4 could be more precise about sally-specific triggers. |
| State Consistency | 7/10 | 9/10 | C2 (field conflict) + M2 (save/load) resolve the two gaps. -1 for: save/load of clause-selection mid-flow (M1's new UI) isn't specified — what if player saves during clause building? |
| Formula Integration | 8/10 | 9/10 | m2 (Schemer bias documented) + M8 (int rounding) resolve the two gaps. -1 for: the condition-based bias (m1) changes the probability profile — previously "30% random" is now "whenever conditions match." Playtesting needs to verify the effective frequency is still ~30%. |

**Task 3: Building Blocks Compliance — 14/15 (was 12/15)**

| Sub-dimension | Old | New | Change |
|---------------|-----|-----|--------|
| Enemy AI Uses Same Systems | 4/5 | 4/5 | Unchanged — v2 personality wiring still needed. |
| Executor Is Deterministic | 4/5 | 5/5 | m1 eliminates the random.random() concern in Schemer bias. |
| Single Source of Truth | 4/5 | 5/5 | m6 pins harshness to diplomacy.py. |

**Task 4: Session Plan Feasibility — 12/15 (unchanged)**
No fixes targeted session plan structure. Risk assessment and dependency graph remain the same.

**Task 5: Fun Audit — 8/10 (unchanged)**
Fixes improve robustness but don't change the player experience assessment. The fun comes from character and mechanics, which were already solid.

**Task 6: Golden Rule Compliance — 10/10 (was 9/10)**
M8 resolves the only gap (float math in acceptance formula). All 7 golden rules now fully satisfied.

### New Overall Grade: 91/100

Breakdown: 27 + 14 + 12 + 8 + 10 = 71/80 from scored dimensions. Edge case coverage now comprehensive (23 audit-discovered cases all have specified behavior). Innovation and fun assessment unchanged (high marks). Remaining 9 points deducted for:
- Session plan risk unchanged (SPEC 1A map expansion remains EXTREME risk)
- Enemy diplomat personality asymmetry still needs v2 (documented but not resolved)
- 3 minor robustness concerns identified below

### New Findings Discovered During Re-Read

**N1 (Minor): Clause-selection save/load.** The new M1 clause-selection UI (DESIGN §3b) introduces a multi-step flow where the player builds clauses one at a time. If the player saves mid-clause-building, the `pending_diplomatic_dialogue` would need to store the partial clause list in its `context` dict. This is likely fine (all primitives), but should be explicitly documented: "Partial clause list survives save/load in `pending_diplomatic_dialogue.context.clauses_so_far`."

**N2 (Minor): §5b.4 HOLD cancellation scope.** The HOLD cancellation rule ("HOLD orders in border regions adjacent to that nation: cancelled") is broader than necessary. A marshal on HOLD might be positioned against multiple nations. A more precise rule: "HOLD orders whose sally target list included marshals of the now-peaceful nation have their sally behavior restricted — they will NOT sally against the peaceful nation's forces, but the HOLD order itself persists." This avoids unnecessarily cancelling defensive positions. Recommend revisiting during implementation.

**N3 (Minor): Replace with Loyalist aide — personality_modifiers impact.** The C4 fix introduces personality change from Schemer to Loyalist. The `personality_modifiers.py` file applies combat bonuses by personality type. Talleyrand is NOT a combat unit (he's a DiplomaticRepresentative, not a Marshal), so this doesn't affect combat. But if diplomatic personality modifiers are later added to the personality_modifiers system (e.g., Schemer gets +2 on acceptance formula), the Loyalist replacement would lose that bonus. Currently safe — diplomatic skill bonus is on the DiplomaticRepresentative class directly, not routed through personality_modifiers.py.

### Summary

All 5 Critical and 9 Major findings are fully resolved. All 11 Minor findings are applied. 3 new minor findings discovered (N1-N3), none requiring immediate action. The specs are now internally consistent, cross-referenced correctly, and mechanically complete.

**Grade change: 79/100 → 91/100.**
**Status: Ready for implementation.**
