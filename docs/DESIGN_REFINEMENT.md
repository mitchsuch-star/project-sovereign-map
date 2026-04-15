# Design Refinement

> **Design items and addons for evaluation.** Work here begins after `BUG_FIXES.md` is clear and playtesting confirms stability.
>
> **Last Updated:** April 13, 2026 (post-fix routing refresh: the diplomacy bug-phase gate is now cleared, the shipped Envoys inbox / current-turn offer lifetime / response-contract refactors are recorded here as live foundations, and the next diplomacy work is now explicitly ordered as commitments first, bilateral peace hardening second, and ally settlement only after dedicated later specs)

---

## Summary

| Category | Count | Status |
|----------|-------|--------|
| Player Feedback (Wave 3 remaining) | 7 | Pending consolidation into post-fix diplomacy specs |
| Nation Rivalry System (EU4-inspired) | 1 | Ready for dedicated spec work |
| Territorial Promises (Wave 3) | 1 | Fold into the commitments spec track |
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

### Current next spec queue

These are the next diplomacy design tracks. `Reliability + Commitments` is the first implementation target; every later item below still needs a dedicated written spec before implementation.

1. `Reliability + Commitments`
   Collapse `R160`, `R119`, and `R151` into one political-commitment system covering rivalries, betrayal memory, and territorial promises. Draft started in `docs/RELIABILITY_COMMITMENTS_SPEC.md`. This is the first diplomacy follow-up implementation target.
   `C3` (commitments presentation pass, `docs/COMMITMENTS_PRESENTATION_SPEC.md`) is in the active queue as the follow-up to `C2`, landing before `Bilateral Peace Hardening`. It is intentionally smaller than the later `Talleyrand Desk + Explanation Layer` track.
2. `Bilateral Peace Hardening`
   Tighten separate peace / bilateral peace preview, explicit term ownership, promise-breach warnings, and peace-treaty legibility before any ally-aware settlement system exists. **Needs dedicated spec.**
3. `War Purpose + Score Semantics`
   Collapse war objectives, ticking war score, vassalage power cap, forced alliance, and liberation into one war-goal / score-legibility spec. **Needs dedicated spec.**
4. `Ally Participation + Common Peace`
   Build contribution, consultation, ally beneficiaries, and common peace as a separate wartime-flow system. The current draft in `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` is a later-direction doc, not an implementation-ready next slice. **Needs tighter dedicated spec after items 1-3.**
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

### R119: Nations Remember Betrayal
- **Category:** Player Feedback
- **Summary:** Escalating betrayal tracking — nations penalize repeated broken agreements.
- **Details:** New `world.betrayal_history` dict. 1st offense -10, 2nd -20, 3rd+ -30 + AI hard reject. Half penalty for witness nations. Redemption: 20 honored treaty turns removes oldest betrayal.
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

### R160: Nation Rivalry System (EU4-Inspired)
- **Category:** Diplomacy — Balance
- **Source:** Playtest (Apr 6) — player befriended all 4 nations simultaneously with no friction
- **Problem:** Nothing prevents France from being allied with everyone at once. No nation objects to France allying their historical enemy. Diplomacy has no tension — it's a one-way ramp to universal friendship. In the playtest, France achieved ALLIANCE with Britain, Prussia, and Austria while vassalizing Saxony in 7 turns. There's no strategic choice about *who* to ally because allying everyone is always optimal.
- **Proposed design — Rivalry system:**
  - **Rival pairs:** Nations have natural rivals (historical + dynamic). Rivals are upset when you befriend their enemy.
    - Starting rivals: Britain↔France (colonial), Prussia↔Austria (German hegemony), Prussia↔Saxony (annexation threat)
    - Dynamic: AI can declare rivalry when relation drops below -40 or when France allies their enemy
  - **Alliance anger:** When France allies Nation A, nations that are rivals of A get a relation penalty (-10 to -20) and may break treaties. "Austria protests your alliance with Prussia."
  - **Rival exclusion:** Cannot be allied with both members of a rival pair simultaneously. Choosing one means losing the other. Forces strategic branching.
  - **Jealous AI proposals:** Nations offer alliance specifically to BLOCK you from allying their rival. "Prussia offers alliance — but only if you break ties with Austria."
  - **Rival decay:** Rivalries fade if nations have common enemies (+2/turn at war with same target). New rivalries form from repeated wars.
- **EU4 parallels:** Rival system, opinion penalties for allying rivals, alliance capacity limits, diplomatic reputation
- **Design gates:** How many rivals per nation? Can the player influence rival pairs? Should there be an alliance capacity limit (max 2 allies)? How does this interact with coalitions?
- **Files:** `diplomacy.py` (rival pairs, anger penalties), `ai_diplomacy.py` (rival-aware proposals, exclusion checks), `diplomatic_ledger.py` (display rivals), `world_state.py` (rival tracking)
- **Est. sessions:** 2-3

### R151: Territorial Promise Clauses
- **Category:** Diplomacy Feature
- **Summary:** New clause type — nations promise territorial cessions they don't yet control. Enables "France promises to help Prussia take Saxony in exchange for peace."
- **Details:** New `territorial_promise` clause, acceptance bonus, obligation tracking, reputation penalty if broken. Historically accurate to Napoleonic diplomacy.
- **Gates needed:** Obligation mechanics, AI understanding of promises, betrayal consequences.
- **Files:** `diplomacy.py`, `ai_diplomacy.py`

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

## Source Documents (Archived Reference)

| Document | Items Moved Here |
|----------|-----------------|
| `docs/DIPLO_REFINEMENT.md` | Wave 3-5 open items, all R-IDs |
| `docs/DIPLOMACY_DESIGN_FIXES.md` | Design discussion items, N1/A3/A4 AI fixes |
| `docs/archive/PLAYTEST_AUDIT_2026_03_29.md` | War Objectives, Ticking War Score, Vassalage Power Cap, Forced Alliance, Liberation (lines 215-722) |
| `docs/JEALOUSY_SPEC.md` | Jealousy pointer (spec kept as-is) |
