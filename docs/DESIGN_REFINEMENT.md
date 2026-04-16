# Design Refinement

> **Design items and addons for evaluation.** Work here begins after `BUG_FIXES.md` is clear and playtesting confirms stability.
>
> **Last Updated:** April 16, 2026 (Memory and Pressure rescope: war_bargain mechanic split out into `docs/WAR_BARGAIN_SPEC.md`, scheduled in the later Peace Deals phase; queue item 1 renamed `Reliability + Commitments` → `Memory and Pressure`. April 13 routing context preserved below.)

---

## Summary

| Category | Count | Status |
|----------|-------|--------|
| Player Feedback (Wave 3 remaining) | 7 | Pending consolidation into post-fix diplomacy specs |
| Nation Rivalry System (EU4-inspired) | 1 | Folded into `Memory and Pressure` spec (substrate shipped; remaining: rivalry seed + acceptance formula + C3-lite presentation) |
| Territorial Promises (Wave 3) | 1 | Folded into `WAR_BARGAIN_SPEC.md` — deferred to Peace Deals phase |
| War System Overhaul (EU4-inspired) | 4 | Ready for dedicated spec work |
| AI Diplomacy Improvements | 3 | Re-scope into the agenda / motive spec track |
| Gold Sink Options (B4) | 1 | Candidate follow-up after the first diplomacy spec queue |
| Wave 4 — New Features | 19 | Needs per-item approval after the core diplomacy spec queue |
| Wave 5 — Game Review Findings | 8 | Mostly routed into the grouped spec tracks below |
| Jealousy System | 1 | Separate design gate; not part of the diplomacy queue |
| **Total** | **45** | |

---

## Post-Fix Routing Update

The old bug-phase gate is now cleared. Sessions 1-7 in `docs/BUG_FIXES.md` are complete, and the diplomacy contract is now stable enough to plan legitimacy and strategy work on top of it.

### Live foundations now documented

- `PL-27`, `PL-34`, and `PL-32` are complete.
- The Envoys inbox / mailbox panel is live, including `GET /mailbox`, `POST /mailbox/activate`, stable mailbox identity, and `dialogue_manager.get_mailbox_count()` as the badge source.
- `world.diplomatic_queue` is gone; the shipped follow-up refactor replaced the old cross-turn mailbox persistence with current-turn envoy items (`Not Now`, same-turn reopen, end-turn lapse).
- Proposal / clause display ownership is centralized in backend formatters, so popup payloads and reopen flows use the same labels.
- Session 6 contract refactors are complete: `/command` starts from `build_base_response()`, remaining diplomacy popups use typed response paths, and `main.gd` routes modals through the registry/dispatcher layer.

### Current next spec queue (April 16, 2026 rescope)

These are the next diplomacy design tracks. `Memory and Pressure` is the first implementation target; every later item below still needs a dedicated written spec before implementation.

1. `Memory and Pressure` (renamed from `Reliability + Commitments` April 16)
   Substrate (betrayal memory, rivalry witness scope, hard-reject posture, episode_id, structured warnings) is **shipped**. Remaining work this phase: seed `nation_rivalries` (3 authored pairs), wire `direct_rivalry_mod` + `rival_conflict_mod` + graduated `bilateral_betrayal_mod` into acceptance, wire third-party anger on ratification, redemption tick (`actor_honored_turns` +3 / 5 turns), rename `alliance_paradox` → `commitment_paradox`, ship C3-lite presentation pass (spotlight tier, split-voice render, named-diplomat resolution per Voice Bible). See `docs/RELIABILITY_COMMITMENTS_SPEC.md` v2.1, `RELIABILITY_IMPLEMENTATION_PLAN.md` v2.1, `COMMITMENTS_PRESENTATION_SPEC.md` v0.3 (C3-lite). ~68-74 tests, ~3 sessions remaining (Slice C split into Godot-surfaces + tests/mock-prose sessions; v2.1 adds Make Amends verb + France-Austria rivalry + other creative-audit folds).
2. `Bilateral Peace Hardening`
   Tighten separate peace / bilateral peace preview, explicit term ownership, promise-breach warnings, and peace-treaty legibility before any ally-aware settlement system exists. **Needs dedicated spec.**
3. `War Purpose + Score Semantics`
   Collapse war objectives, ticking war score, vassalage power cap, forced alliance, and liberation into one war-goal / score-legibility spec. **Needs dedicated spec.**
3.5. `War Bargains` — `docs/WAR_BARGAIN_SPEC.md`
   The named-enemy bilateral promise mechanic split out of `Reliability + Commitments` v1.0 in the April 16 rescope. Adds `war_bargain` clause type, lifecycle (active / triggered / fulfilled / void / breached), `join_opportunity` ally-entry contract, counter-bargains, `war_entry_score`, Bargain Review surface, and the WB-D presentation extension (bargain spotlights, scope-branched copy, response routes). **Depends on items 1-3.** Implementable as a single Peace Deals phase precursor before item 4. ~80-90 tests.
4. `Ally Participation + Common Peace`
   Build contribution, consultation, ally beneficiaries, and common peace as a separate wartime-flow system. The current draft in `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` is a later-direction doc, not an implementation-ready next slice. **Needs tighter dedicated spec after items 1-3.5.**
5. `Nation Agendas + Motive Legibility`
   Collapse `R155`, `R156`, `A3`, `R123`, and `R124` into one agenda-driven AI diplomacy spec.
6. `Talleyrand Desk + Explanation Layer`
   Collapse `R131`, `R132`, `R17d`, `R17e`, `R17f`, `R157`, and `R159` into one explanation / trend / advisory surface spec.
7. `Economic Diplomacy`
   Collapse `R161` plus diplomacy-facing B4 candidates into one reciprocal-trade / subsidy / pressure spec.

### Still lower priority

- `R162: AI Ultimatums to Player` is no longer blocked by the old attention contract, but it should still wait until the commitment and agenda specs above are written. It adds interruption surface before the core diplomacy has enough political weight.
- Presentation-only diplomacy polish remains downstream of the grouped spec work above, except for the narrow post-commitments presentation pass proposed in `docs/COMMITMENTS_PRESENTATION_SPEC.md`.

---

## Secondary Post-Fix Items

These refine existing systems and are still implementation-ready later, but they should not displace the grouped spec tracks above.

### R119: Nations Remember Betrayal — **COVERED**
- **Category:** Player Feedback
- **Status:** **Fully covered** by the Memory and Pressure substrate (shipped April 15-16, 2026). `world.betrayal_history` with severity-scaled decay, per-episode strike caps, bilateral `bilateral_betrayal_mod` in acceptance formula, hard-reject posture at 3 active strikes, witness scoping, Make Amends active-redemption verb (v2.1). The original R119 design (flat -10/-20/-30 with half-witness, 20-turn redemption) was superseded by the spec's graded model. No further work needed on R119 itself.
- **Files:** `diplomacy.py`

### R131: Cooldown Pre-Check Warning
- **Category:** Player Feedback
- **Summary:** Warn player of proposal cooldowns before opening negotiation dialogue.
- **Details:** Pre-check cooldown before dialogue opens. Show remaining turns + Talleyrand message.
- **Files:** `diplomatic_executor.py`

### R129: Override Feedback in Dispatch
- **Category:** Player Feedback
- **Summary:** Add feedback when diplomatic override actions succeed/fail.
- **Details:** Success: +2 trust + dispatch note. Failure: +1 concern boost + dispatch note. Fix timing bug at diplomatic_defiance.py:741.
- **Files:** `diplomatic_defiance.py`, `dispatch.py`

### R128: Sabotage Consequence Feedback
- **Category:** Player Feedback
- **Summary:** Track and report sabotage outcomes with Talleyrand feedback.
- **Details:** Track in `world.sabotage_history`. Dispatch note next turn. Trust +3 if Talleyrand was correct.
- **Files:** `diplomatic_defiance.py`, `dispatch.py`

### R132: Vassal Loyalty Transparency
- **Category:** Player Feedback
- **Summary:** Real-time vassal loyalty deltas and trend tracking.
- **Details:** Lower warning threshold to 30. Show delta when |change| >= 2. Store `prev_loyalty`. Trend arrow in ledger.
- **Files:** `dispatch.py`, `vassal.py`, `diplomatic_ledger.py`

### R17d: DP Breakdown Display
- **Category:** QoL
- **Summary:** Show DP source/cost components in ledger.
- **Files:** `diplomatic_ledger.py`

### R17e: Relation Trend Arrows
- **Category:** QoL
- **Summary:** 3-turn history showing direction of relationships in ledger.
- **Files:** `diplomatic_ledger.py`

### R17f: Mission Progress Projection
- **Category:** QoL
- **Summary:** Estimated completion turn for active missions.
- **Files:** `diplomatic_ledger.py`

### Memory and Pressure interaction notes (added April 16 creative audit)

These are not new items — they annotate existing items whose scope or interaction changes now that Memory and Pressure (v2.1) is the active spec.

- **R162 (AI Ultimatums to Player):** Hard-reject posture (3+ bilateral strikes) from Memory and Pressure now informs AI ultimatum behavior. A nation at hard-reject posture toward France is both more likely to issue ultimatums (anger-driven) and less likely to accept French counter-offers. Wire this interaction when R162 ships.
- **R123 / R124 (Economic Strategy & Diplomatic Isolation AI):** These collapse into queue item 5 (Nation Agendas + Motive Legibility). AI should now read `bilateral_betrayal_mod`, `rival_conflict_mod`, and `nation_rivalries` to drive subsidy offers, alliance-breaking proposals, and isolation strategy. The Memory and Pressure substrate provides the data; the agenda spec provides the decision logic.
- **R17d (DP Breakdown Display):** Will need to display the new `political_commitment_mod` components (`direct_rivalry_mod`, `rival_conflict_mod`, `bilateral_betrayal_mod`) once Memory and Pressure ships. Consider showing these per-proposal in the breakdown, not just the composite.
- **R155 / R157 (AI Proposal Voice / Talleyrand Voice Depth):** The C3-lite presentation pass (`COMMITMENTS_PRESENTATION_SPEC.md` v0.3) adds named-diplomat spotlight + split-voice for three live events with committed mock prose per `DIPLOMAT_VOICE_BIBLE.md`. This covers the commitments-surface subset of R155/R157. The broader scope (personality-driven proposal timing, AI-initiated proposal voice, deep Talleyrand commentary across all diplomacy) remains open and routes to queue items 5-6.

---

## Focused Audit Validation (Apr 10, 2026)

The focused attention / AI diplomacy audit tightened which diplomacy legitimacy items are already justified, which ones need bug-fix prerequisites, and which old notes are now stale.

### Already justified by current evidence

- **R160: Nation Rivalry System** — confirmed as the highest-leverage legitimacy upgrade. Current diplomacy still lets France drift toward broad friendship without enough forced political choice.
- **R155: AI Proposal Personality Voice** — needs to expand from flavor text into motive legibility. The audit confirmed that AI personality currently changes a few constants, but not enough of proposal timing, persistence, target choice, or player-facing explanation.
- **R156: Diplomacy Strategic Optionality** — confirmed. Proposals happen, but they do not create enough meaningful branching until rivalry / exclusion pressure exists.

### Prerequisites now satisfied (Apr 12)

- **R160 / R155 / R156** are no longer blocked by the old diplomacy contract prerequisites. `PL-27`, `PL-34`, and `PL-32` are closed, and the Envoys inbox / current-turn offer lifetime / typed popup-response foundations are live.
- **R162: AI Ultimatums to Player** no longer waits on the mailbox/recovery transport fix, but it remains intentionally sequenced after the stronger commitment and agenda specs.
- Presentation-only diplomacy polish should still follow the grouped spec work above, not precede it.

### Current legitimacy stack

- Completed foundation: Envoys inbox / same-turn offer lifetime / backend-owned display labels / typed response routing.
- `Reliability + Commitments`: make alliances politically costly, promises meaningful, and betrayal cumulative.
- `Bilateral Peace Hardening`: make separate peace and bilateral settlement review legible before multilateral settlement exists.
- `War Purpose + Score Semantics`: make wars resolve toward recognizable political outcomes instead of generic pressure alone.
- `Ally Participation + Common Peace`: later wartime settlement layer once the bilateral peace plumbing is strong enough.
- `Nation Agendas + Motive Legibility`: make AI motives and strategic branching legible to the player.

---

## Needs Design Gate

### R160: Nation Rivalry System (EU4-Inspired) — **PARTIALLY COVERED**
- **Category:** Diplomacy — Balance
- **Status:** **Core system shipped** via Memory and Pressure v2.1. Static rivalry seed (4 authored pairs: France↔Britain, France↔Austria, Prussia↔Austria, Prussia↔Saxony), `direct_rivalry_mod` + `rival_conflict_mod` in acceptance formula, third-party anger on ratification, two authored Prussia↔Saxony escalation triggers. The original R160 design is superseded by `RELIABILITY_COMMITMENTS_SPEC.md` v2.1 §7.
- **Remaining (unshipped):** dynamic rivalry formation (AI declares rivalry when relation drops below threshold or when France allies their enemy). This was explicitly deferred in spec §7.2 to "later AI-agenda work." The jealous-AI-proposals and rival-decay designs from R160 are also not yet implemented but folded into the queue-5 `Nation Agendas + Motive Legibility` track.
- **Files:** `diplomacy.py`, `ai_diplomacy.py`, `diplomatic_ledger.py`, `world_state.py`

### R151: Territorial Promise Clauses — **MOVED to WAR_BARGAIN_SPEC**
- **Category:** Diplomacy Feature
- **Status:** The broader concept (France makes named-enemy promises to allies, tracking obligation, breach/fulfillment, betrayal consequences) is now fully designed as the `war_bargain` clause type in `docs/WAR_BARGAIN_SPEC.md`. The spec covers creation, validation, lifecycle, fulfillment, breach/void, war-entry integration, and the Bargain Review surface. Scheduled in the Peace Deals phase after `Bilateral Peace Hardening` + `War Purpose + Score Semantics` (queue items 2-3.5).
- **Files:** `diplomacy.py`, `ai_diplomacy.py`, `diplomatic_executor.py`

### Jealousy System (v3.1 spec)
- **Category:** Marshal Feature
- **Summary:** Glory Ladder targeting, personality expressions, escalation, confrontation popups.
- **Details:** Full spec at `docs/JEALOUSY_SPEC.md`. Core design settled. Top of ladder: +1 all core stats while #1. Defeats cost glory. DO NOT CODE WITHOUT USER APPROVAL.

---

## War System Overhaul (EU4-Inspired — Design Gate)

Full design spec in `docs/archive/PLAYTEST_AUDIT_2026_03_29.md` lines 215-722. Addresses core balance problem: defensive play is overwhelmingly superior because no ticking score incentivizes holding territory over time.

### War Objectives + Ticking War Score (5th Component)
- **Summary:** Player-chosen war goals at war declaration (Conquest, Subjugation, Forced Alliance) and auto-assigned goals (Defense, Liberation). Each goal has a ticking target region — holding it accumulates war score over time (±25 cap).
- **Ticking rates:** Conquest +2/turn (enemy capital), Subjugation +3/turn (enemy capital, power cap gated), Forced Alliance +2/turn (enemy capital), Defense +1/turn (any enemy region), Liberation +1/turn per vassal capital.
- **New field:** `world.war_objectives: Dict[str, Dict]` — diplo_key to `{type, target, accumulated}`
- **Files:** `diplomacy.py` (calculate_war_score 5th component), `world_state.py` (field + per-turn accumulation), `war_status.py` + `war_detail_popup.gd` (display), `diplomatic_executor.py` (war goal selection dialogue)
- **Est. sessions:** 2-3, ~20 tests

### Vassalage Power Cap
- **Summary:** Gate vassalization on National Power ratio: target must be ≤ 50% of player's power. Power = sum of base income of controlled regions + partial vassal contribution.
- **Why:** Prevents France from vassalizing Austria at war_score 80 — only small nations should be vassalizable.
- **Files:** `vassal.py`, `diplomacy.py`, `diplomatic_ledger.py`, `diplomatic_templates.py`
- **Est. sessions:** 1, ~10 tests

### Forced Alliance Clause Type
- **Summary:** New clause type — war goal forces enemy into ALLIANCE + Continental System on peace. Follows vassalage pattern for wiring (acceptance values, harshness, keywords, display names, state mapping).
- **Historical:** Napoleon's primary war objective (Austerlitz, Tilsit, Jena).
- **Files:** `diplomacy.py`, `diplomatic_dialogue.py`, `diplomatic_executor.py` (4 state maps), `display_names.py`, `diplomatic_templates.py`, `world_state.py`
- **Est. sessions:** 1-2, ~10 tests

### Liberation Mechanic
- **Summary:** Coalition war goal — liberating vassals. On peace: `release_vassal()` + auto `DEFENSIVE_ALLIANCE` with liberator.
- **Files:** `world_state.py` (_ratify_treaty), `vassal.py` (release reason)
- **Est. sessions:** 1, ~6 tests

---

## AI Diplomacy Improvements (Ready — Small Fixes)

### N1: AI Preemptive Alliance Against Rising Threat
- **Source:** `docs/archive/DIPLOMACY_DESIGN_FIXES.md` lines 69-130
- **Summary:** Trigger 5 in AI-AI diplomatic evaluation. When threat > 40, nations with negative relations toward France form defensive alliances with each other. Creates diplomatic web before coalitions.
- **Audit status (Apr 10):** Already implemented in `ai_diplomacy.py` Trigger 5. Keep as verified reference, not as a pending refinement unless the behavior needs expansion.
- **Files:** `ai_diplomacy.py`
- **Est. tests:** ~7

### A3: AI War Exhaustion Integration
- **Source:** `docs/archive/DIPLOMACY_DESIGN_FIXES.md` lines 55-61
- **Summary:** Proposal-side war exhaustion integration is already partially landed in `ai_diplomacy.py` (`effective_p1_threshold`, `effective_stalemate_turns`). Remaining work, if any, is broader war-exhaustion integration in `enemy_ai.py` and diplomacy-vs-war choice, so this item now needs re-scope rather than blind implementation.
- **Files:** `ai_diplomacy.py`, `enemy_ai.py`
- **Est. tests:** ~4

### A4: AI Harsh Peace Gold Formula Rebalance
- **Source:** `docs/archive/DIPLOMACY_DESIGN_FIXES.md` lines 47-53
- **Summary:** Historical note only: the focused audit confirmed the live formula already uses `max(200, int(war_score * 5 * gold_mult))` in `ai_diplomacy.py`. Keep this item only if further rebalance is desired.
- **Files:** `ai_diplomacy.py`
- **Est. tests:** ~2

---

## Wave 4 — Decide Gate (Per-Item Approval)

These are new feature designs. Each needs individual approval before implementation.

| ID | Item | Summary |
|----|------|---------|
| R22 | Marriage Alliances | Dynastic bonds: +20 rel, block war 5 turns, 3 DP |
| R32 | Peace Conferences | Multi-nation negotiations, 3 DP, +15 acceptance |
| R117 | Advisory Actionability | Advisory ends with executable options |
| R123 | Economic Strategy AI (P9) | Gold > 600 triggers subsidy offers, trade pressure |
| R124 | Diplomatic Isolation AI (P10) | Split enemy alliances with generous terms |
| R133 | Point of No Return Event | One-time Talleyrand popup at threat 40 |
| R28 | Talleyrand Voice Bank | 5-8 variants per situation type |
| R127 | Nation-Specific Intelligence | Per-nation personality lines in advisory |
| R24 | Treaty Signing Ceremonies | Talleyrand ceremony text on ratification |
| R25 | Vassal Personality Events | 3-4 random loyalty-gated events per game |
| R26 | Continental System Buff | Backend exists, needs player command + creative rebalance |
| R27 | Secret Treaties | Hidden treaties, 10%/turn discovery chance |
| R33 | Puppet Rulers | Named rulers with personality, events |
| R35 | Player Counter-Offer Terms | Player specifies clauses (Godot popup) |
| R36 | Personal Summits | Face-to-face meetings, +15 acceptance 3 turns |
| R59 | Literal Personality Triggers | Audit and wire unwired triggers |
| R118 | Enhanced Acceptance Preview | Top 3 positive/negative components + Talleyrand hints |
| R161 | One-Time Trade | Trade gold, manpower, territory directly without ultimatum or state change |
| R162 | AI Ultimatums to Player | Building Blocks: AI uses same ultimatum system as player. Needs popup, response flow, AI decision tree |

---

### R161: One-Time Trade (Expanded)
- **Category:** Diplomacy Feature
- **Summary:** Voluntary, consensual resource exchange between nations — no state change, no coercion. The "carrot" complement to ultimatums (the "stick").
- **Details:** Player proposes a trade (gold, manpower, territory) to any nation at OPEN_BORDERS or better. Both sides give and receive. Uses existing conversational diplomacy flow with `generate_trade_terms()`. Acceptance via full formula. No threat increase, no relation penalty — pure commerce.
- **Building Blocks principle:** Reuses `_ratify_treaty` clause processing, `calculate_acceptance()`, dialogue enrichment, splash damage (none for trades). Same executor path as proposals but with `type: "trade"` and no state transition.
- **Distinction from ultimatums:** Trades are voluntary (both sides benefit), ultimatums are coercive (one-sided demands with diplomatic cost).
- **Gates needed:** Trade balance formula (what's fair?), AI trade evaluation, frequency limits.
- **Files:** `diplomatic_executor.py`, `diplomatic_templates.py`, `diplomacy.py` (new base disposition for trade), `diplomatic_dialogue.py`
- **Est. sessions:** 1-2, ~8 tests

### R162: AI Ultimatums to Player
- **Category:** AI Diplomacy — Building Blocks
- **Summary:** AI nations issue ultimatums to the player using the same ultimatum system the player uses. Building Blocks principle (§23): same systems, different input values.
- **Details:** AI evaluates ultimatum opportunity in `enemy_ai.py` decision tree (new P-trigger). Conditions: military superiority over player in a region, low relations, not in coalition with player. Generates terms via `generate_ultimatum_terms()` (same function player uses). Delivered as popup with [Accept][Reject] options. Rejection gives AI casus belli. Same splash damage, threat (reduces player threat if AI is aggressor), and cooldown mechanics.
- **Building Blocks reuse:** `generate_ultimatum_terms()`, `calculate_acceptance()` (inverted — player is target), `_ratify_treaty` clause processing, splash damage formula, global cooldown (separate AI cooldown counter).
- **Gates needed:** AI trigger conditions (when is ultimatum better than war declaration?), player response popup design, threat direction (does AI ultimatum reduce or increase player threat?).
- **Files:** `enemy_ai.py` (new P-trigger), `diplomatic_executor.py` (AI ultimatum handler), `main.gd` (new popup), `ai_diplomacy.py`
- **Est. sessions:** 2-3, ~12 tests

### National Power Tiers (Great Power / Secondary / Minor) — Design Gate
- **Category:** Diplomacy + War — Balance + Immersion
- **Summary:** Dynamic numeric power tiers (`great_power / secondary_power / minor_power`) calculated from controlled regions, income, military strength, and partial vassal contribution. Affects acceptance formula (great powers resist vassalization), coalition formation (great powers lead coalitions, minor powers join), war settlement (consultation rights scale with tier), and AI threat assessment (great powers escalate coalition faster).
- **Origin:** Conceptual three-tier model exists in `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` §8.3. Data fields (`nation_power_scores`, `nation_power_tiers`) listed as deferred in `RELIABILITY_COMMITMENTS_SPEC.md` §12.3.
- **Design decision from WAR_SETTLEMENT spec:** "These tiers come from numbers, not authored nation labels. The map can create a new quadrangle if power shifts."
- **Interaction with Memory and Pressure:** great powers could have different rivalry intensity defaults (primary only between great powers; secondary between great-and-minor), betrayal tolerance thresholds (great powers hold grudges longer), and Make Amends cost scaling (reparations to a great power should cost more than to a minor).
- **Gates needed:** numeric formula for calculating power scores, threshold ranges (what income/strength makes a "great power"), whether tiers are recalculated per turn or per-war, how tiers interact with the acceptance formula's existing modifier caps.
- **Natural home:** alongside `War Purpose + Score Semantics` (queue item 3) since power tiers inform war objectives and settlement legitimacy. Or as a sub-item of the later `Ally Participation + Common Peace` (queue item 4).
- **Files:** `world_state.py` (data), `diplomacy.py` (formula + tiers), `diplomatic_ledger.py` (display), `ai_diplomacy.py` (threat evaluation)
- **Est. sessions:** 1-2 for the data layer + formula, plus formula-integration touches across existing systems

---

## Gold Sink Options (B4 Balance — Design Gate)

**Priority:** MEDIUM | **Phase:** Pre-EA refinement

Gold accumulation is a known design gap (~700g/turn income vs ~250g upkeep). Manpower-gated recruitment means gold piles up with no meaningful spending options. This section tracks candidate gold sinks for evaluation.

**Forced march REJECTED** — trivializes cavalry's 2-region movement advantage, which is cavalry's core identity.

### Leading Candidate: Province Development
- **Cost:** Variable (200-500g per investment)
- **Effect:** Invest gold in controlled region to boost supply cap, income, or repair war damage faster
- **Design appeal:** Creates invest-now-vs-save tension, rewards holding territory, ties gold to strategic positioning
- **Needs:** Investment tiers, per-region cooldown, diminishing returns formula, AI investment priority

### Other Candidates (evaluate after Province Development)

| Option | Cost | Effect | Notes |
|--------|------|--------|-------|
| Diplomatic gifts/bribes | 200g | +5 relation (once/turn/nation) | Gold becomes diplomacy tool |
| Mercenary garrisons | 400g | Defensive garrison without stationing marshal | Frees marshals for offense |
| Recruitment bounties | 300g | Double manpower regen for 1 turn | Accelerates rebuilding |

---

## Enemy AP Rebalancing (Deferred — Post Full Map)

**Priority:** LOW | **Phase:** After full 1805 map implementation

Enemy AI action budget (currently 4 paid AP per nation) may need rebalancing once the full map is implemented with all nations, regions, and marshal counts at scale. Current 4-nation, 19-region map doesn't stress the action economy the same way a full campaign will. Revisit AP values, per-nation scaling, and aggregate action counts after full map playtesting.

---

## Wave 5 — Game Review Findings (Design Gate)

Cross-system findings from comprehensive review. Needs design gate as a batch.

**Diplomatic Term Novelty — PARTIALLY ABSORBED into PL-25 (BUG_FIXES.md).** PL-25 covers the 80/20: amount jitter, personality-biased pen nudge, nation desire profile bias in `_build_base_terms()`, situational flavor lines. R155/R157 retain the remaining full scope: hawk/dove personality weight table for ALL AI proposals (not just Talleyrand's pen nudge), deep `TALLEYRAND_COMMENTARY` integration, and AI-initiated proposal personality voice.

**Focused audit routing:** R155 / R156 are now directly validated by current code evidence. R160 remains the highest-leverage legitimacy upgrade once the BUG_FIXES attention-contract work lands. R162 stays gated until the diplomacy mailbox / recovery surface exists.

| ID | Item | Summary |
|----|------|---------|
| R152 | Authority System UI Visibility | Authority impact not visible enough to players |
| R153 | Literal Personality Triggers | Personality-specific event triggers |
| R154 | Combat Morale Spiral | Morale death spiral needs circuit breaker |
| R155 | AI Proposal Personality Voice | Partially absorbed into PL-25. Remaining: visible motive / personality in timing, terms, persistence, and player-facing explanation |
| R156 | Diplomacy Strategic Optionality | Diplomacy feels optional vs military path |
| R157 | Talleyrand Voice Depth | Partially absorbed into PL-25 (situational flavor, personality pen nudge). Remaining: deep commentary integration |
| R158 | NL Parser Confidence Feedback | Show parse confidence to player |
| R159 | Information Screen Teaching | Screens don't teach mechanics |

---

## Historical Precision (1805 Campaign — Future Refinement)

These items are conscious trade-offs where v0.1 chose recognizability, immersion, or implementation speed over strict period accuracy. Each has an audit trail, not a bug. Track for EA scope when the full 1805 campaign lands. Added April 16, 2026 from the Memory and Pressure creative audit.

### P1: Period-accurate diplomat roster for 1805
- **Summary:** The four foreign diplomats in `backend/models/diplomat.py` (Hardenberg / Metternich / Castlereagh / Einsiedel) are recognizable Napoleonic-era names but historically took their depicted roles **after** the 1805 campaign start: Hardenberg as Prussian chancellor from 1810, Metternich as Austrian foreign minister from 1809, Castlereagh as British foreign secretary from 1812, Einsiedel as Saxon minister from 1813. The actual 1805 ministers were Haugwitz (Prussia), Stadion or Cobenzl (Austria), Mulgrave (Britain), and Bose or Löss (Saxony).
- **Design trade-off (deliberate):** recognizability was prioritized for v0.1 because the four chosen figures are well known to strategy players and the Voice Bible's Hawk / Schemer / Dove register distinctions were drawn from their historical voices. Swapping them in v0.1 would lose the established register voices without adding mechanical value and would force the Voice Bible exemplars to be re-authored before any useful commitments work shipped.
- **When to revisit:** once the full 1805 campaign ships (Early Access) and the game claims period fidelity as a feature. Swap to the 1805-accurate ministers and port the register notes. The Voice Bible's "Characteristic openings" / "Never says" framework should transfer cleanly — Haugwitz was a Prussian Hawk in the Hardenberg mold, Stadion a Schemer adjacent to Metternich, Mulgrave less distinctive than Castlereagh but workable, Bose closer to Einsiedel's dove register.
- **Files:** `backend/models/diplomat.py`, `docs/DIPLOMAT_VOICE_BIBLE.md`, `backend/game_logic/diplomatic_templates.py`, any committed breach / hard-reject mock prose
- **Est. sessions:** 1 (cast swap + voice port + test refresh)

### P2: Britain reactive bloc pressure (continental-hegemon pattern)
- **Summary:** The v0.1 rivalry model has Britain as France's direct rival but gives Britain no *reactive* posture when France deepens ties with a continental power. Historically Britain opposed any continental hegemon on principle, paying subsidies to any continental power willing to fight France. Flagged in `RELIABILITY_COMMITMENTS_SPEC.md` v2.1 §7.4.C as the #1 historical-texture debt for Memory and Pressure.
- **When to land:** `Coalition Generalization` (D2, follow-up after Memory and Pressure). D2 should include continental-hegemon reactive threat accumulation — not just bloc-target parameterization — so Britain gains automatic threat against any power approaching continental hegemony, not only France by name.
- **Files:** `backend/game_logic/coalition.py`, `backend/game_logic/diplomacy.py`
- **Est. sessions:** folded into D2 spec work

### P3: Diplomatic Ledger sort / filter at scale
- **Summary:** The Diplomatic Ledger's Nations tab currently renders one row per nation. At 5 nations this is clean; at 6-8 full 1805 nations with multiple rivals each, the list becomes dense. Commitments rows (active rivals, betrayal warnings, posture markers) multiply the cell count.
- **When to land:** Pre-EA polish alongside Map Renderer UX pass, or absorbed into the Talleyrand Desk + Explanation Layer spec (diplomacy queue item 6).
- **Files:** `godot-client/project-sovereign/scripts/diplomatic_ledger.gd`
- **Est. sessions:** 1 as a standalone UX slice, or folded into the Talleyrand Desk pass

---

## Source Documents (Archived Reference)

| Document | Items Moved Here |
|----------|-----------------|
| `docs/DIPLO_REFINEMENT.md` | Wave 3-5 open items, all R-IDs |
| `docs/DIPLOMACY_DESIGN_FIXES.md` | Design discussion items, N1/A3/A4 AI fixes |
| `docs/archive/PLAYTEST_AUDIT_2026_03_29.md` | War Objectives, Ticking War Score, Vassalage Power Cap, Forced Alliance, Liberation (lines 215-722) |
| `docs/JEALOUSY_SPEC.md` | Jealousy pointer (spec kept as-is) |
