# Design Refinement

> **Design items and addons for evaluation.** This is the design-refinement backlog; execution routes through `docs/ROADMAP.md`'s current phase queue. (The old "work begins after `BUG_FIXES.md` is clear" gate cleared April 2026.)
>
> **Last Updated:** July 11, 2026 — **Estate Second Pass deferrals filed** (ESP-1..4, from the ES-7 second-pass design conversation; owner spec `ECONOMY_REVISIT_SPEC.md` §0.6.8). Prior: July 10, 2026 — **Wave 6 APPROVED IN FULL same day it was filed** (+2 gate additions: Dynamic Battle Naming, Literal Doctrine); the build-ready owner is **`docs/WAVE6_FUN_FACTOR_SPEC.md`** (12 slices, blessed default numbers recorded there). Wave 6 items came from `docs/audits/CREATIVE_AUDIT_2026_07_10.md`; live-evidence revisions recorded on R154, R59/R153 (now SUPERSEDED by W6-5), R129/R131/R132, R155/R156, R117 (absorbed into W6-9). Prior: July 2, 2026 present-tense pass. April 16, 2026 rescope context preserved below as history.

---

## Summary

| Category | Count | Status |
|----------|-------|--------|
| Player Feedback (Wave 3 remaining) | 7 | Open — R129/R128 → 8.EVAL triage; R131/R132/R17d-f → queue item 6 (8.EVAL) |
| Nation Rivalry System (EU4-inspired) | 1 | Superseded by Memory and Pressure v2.4.3 (COMPLETE); dynamic-agenda residual → queue item 5 |
| Territorial Promises (Wave 3) | 1 | ✅ LANDED April 2026 as war bargains (`WAR_BARGAIN_SPEC.md`) |
| War System Overhaul (EU4-inspired) | 4 | ✅ LANDED — war_objectives / power cap / forced_alliance / liberation live in code |
| AI Diplomacy Improvements | 3 | N1 verified live; A4 historical note; A3 residual rides queue item 5 (8.EVAL) |
| Gold Sink Options (B4) | 1 | Re-pointed → `docs/ECONOMY_REVISIT_SPEC.md` EC-2 |
| Wave 4 — New Features | 19 | Needs per-item approval (8.EVAL); R26 → EC-5, R161 → EC-8, R162 gated behind queue items 5-6 |
| Wave 5 — Game Review Findings | 8 | Mostly routed into the grouped spec tracks; R158 → `docs/COMMAND_ROBUSTNESS_SPEC.md` CR-7 |
| Jealousy System | 1 | Separate design gate; Marshal Content Pass MC-3 now an effective prerequisite |
| **Wave 6 — Creative Capstone (July 10, 2026)** | 14 | **✅ APPROVED IN FULL July 10** (6 expansions + 6 escalations + 2 gate additions: Dynamic Battle Naming, Literal Doctrine); owner = `WAVE6_FUN_FACTOR_SPEC.md` (12 build slices W6-0..W6-11) |
| **Estate Second Pass deferrals (July 11, 2026)** | 4 | **ESP-1 + ESP-2 + ESP-4 ✅ LANDED July 11, 2026 with the Jealousy v3.2 build** (ESP-4 folded per its own row's fold-in clause; record = `JEALOUSY_SPEC.md` §0.3/§0.4, tests `test_estate_riders_esp.py`); ESP-3 respect-by-treaty → diplomacy gate (unchanged) |
| **Total** | **63** | |

---

## Vassal Playtest — Design Items (July 14, 2026)

> Routed (not bugs) from the July 14 vassal playtest + 14-agent verification. Bug fixes landed the same session (`docs/BUG_FIXES.md` §Vassal Playtest Findings); memo `docs/audits/VASSAL_PLAYTEST_2026_07_14.md`. These are intent/legibility/enhancement calls, not defects.

| ID | Pri | Item | Detail | Owner / gate |
|----|-----|------|--------|--------------|
| VP-D1 | P3 | **Garrison-as-a-real-loyalty lever (wire or remove)** | The vassal garrison-loyalty formula (`vassal.py` step 2) reads `region.garrison_troops`, a field nothing in production assigns, and gates on `controller==lord` (false for a self-owning satellite) — so it is unwired-but-tested. Either WIRE it (read `garrison_strength`/`garrison_detachment`; decide whether/how a lord can garrison a foreign-controlled vassal capital + the loyalty tie + balance) so VS-1 can advertise it again, or REMOVE the formula + its 4 tests. F1c dropped it from the hint copy in the meantime. | VS-3 land-grants slice or a vassal-depth pass; escalate the balance number if wired |
| VP-D2 | P3 | **Muster odds band omits the defender baseline edge** | The muster "odds"/"balance of force" band (`objection_v2.inferred_attack_odds_band`) folds terrain + fort but NOT the always-on +20% `defender_bonus`, defender DEFENSE skill, ±10% variance, or the 2d6 — so "favorable" reflects force balance, not the casualty exchange (playtest: a "favorable" attack lost 8,819 to inflict 469 into mountains vs a cautious defender). F2 reworded the label to "the balance of force looks …"; the deeper fix (fold the defender baseline into the ratio, and/or a wider band) touches the CR-5 inferred-attack gate threshold → needs re-tuning + a combat sweep, not a silent change. | Combat legibility pass / next combat sweep (escalate the threshold) |
| VP-D3 | P3 | **Committed defensive reinforcers valued by offensive potential** | `_committed_reinforcement_strength` uniformly uses `get_attack_modifier` (combat_executor.py), incl. for the committed DEFENDER — so a cautious/defensive corps reinforcing a defense is systematically undervalued (folds the defensive-stance ×0.90 + attack personality mods). GR5-symmetric (same fn both sides), so a modeling inconsistency, not an exploit — possibly intended as one generic "combat contribution" metric. **Verify intent first.** | Combat review — confirm intent before any change |
| VP-D4 | trivial | **grip recomputed per enemy in the courting loop** | `attempt_vassal_courting` calls `get_imperial_grip(world, player)` once per enemy-nation call each turn (each re-scans homeland + war scores). `process_vassal_loyalty` already memoizes grip per lord; the courting path doesn't. Bounded by N enemies (not a per-region inner loop) — a GR8 cache-per-turn nit, deliberately NOT micro-optimized (staleness risk on a pure derived read outweighs the negligible gain). | Perf nit — fix only if a scale tripwire flags it |

> Routed from **Sweep 4** (July 15, 2026 — `docs/audits/SWEEP_4_2026_07_15.md`). Vassals cleared 6.0→6.5 (target MET, at the floor); these are the CONFIRMED ceiling items the review named. VP-D1 above is the P0 restated by Sweep 4. **Two fixed same day (July 15):** the "grant X **more** autonomy" parse shrug (`_apply_fuzzy_matching` was matching the direction word "more"→"Murat"; now skips marshal-matching for vassal-family actions, `parser.py`) and **VP-D5 below**.

| ID | Pri | Item | Detail | Owner / gate |
|----|-----|------|--------|--------------|
| VP-D5 | P2 | ✅ **FIXED July 15, 2026 — Autonomy change now surfaces its permanent tribute trade-off** | `change_vassal_autonomy` now shows the tribute DELTA directionally: up = "Tribute rate: 75% → 50% (a permanent income cut)", down = "50% → 75% (you collect more of their income)". The player following the "grant autonomy" recovery hint is told the recurring cost at the decision point. Tests in `test_playtest_fixes_2026_07_14.py::TestAutonomyTributeLegibility`. | ✅ done (copy fix, `vassal.py`) |
| VP-D6 | P2 | **Enemy AI has no grip-awareness (no defensive vassal rung)** | `enemy_ai.py` has zero `get_imperial_grip` hooks — a spiralling AI lord does not shore up its own satellites (invest/subsidize/grant-autonomy to arrest defection). GR5 drift already fires for enemy lords, but the AI can't *respond* to it. Moot in the 1805 boot (no enemy holds a satellite — `nation_config.py` seeds satellites for France alone) but a **prerequisite for coalition-defection (VP-D-defection) and VS-3 to feel alive on both boards**. Sequence after the defection slice. | Enemy-AI vassal pass (after coalition-defection) |
| VP-D7 | P3 | **Dual authority-derivation tables risk future divergence** | `get_imperial_grip` (VS-R, graded 75/40/25/15, `authority.py:414`) and `get_authority_proxy` (jealousy, bucketed 75/50/25) are parallel derivations of the same "how strong is the court" idea. Both anchor the shared 30 breakpoint today, so there is **no present divergence** — but two tables of the same concept will drift under future tuning. Reconcile to one graded source, or document the intentional split. Tech-debt, not a defect. | Vassal/jealousy tidy — reconcile before either is retuned |

---

## Post-Fix Routing Update

The old bug-phase gate is now cleared. Sessions 1-7 in `docs/BUG_FIXES.md` are complete, and the diplomacy contract is now stable enough to plan legitimacy and strategy work on top of it.

### Live foundations now documented

- `PL-27`, `PL-34`, and `PL-32` are complete.
- The Envoys inbox / mailbox panel is live, including `GET /mailbox`, `POST /mailbox/activate`, stable mailbox identity, and `dialogue_manager.get_mailbox_count()` as the badge source.
- `world.diplomatic_queue` is gone; the shipped follow-up refactor replaced the old cross-turn mailbox persistence with current-turn envoy items (`Not Now`, same-turn reopen, end-turn lapse).
- Proposal / clause display ownership is centralized in backend formatters, so popup payloads and reopen flows use the same labels.
- Session 6 contract refactors are complete: `/command` starts from `build_base_response()`, remaining diplomacy popups use typed response paths, and `main.gd` routes modals through the registry/dispatcher layer.

### Historical spec queue (April 16, 2026 rescope; superseded by April 28 status)

This queue records the April 16 diplomacy rescope. It is no longer the live implementation queue. Current status is tracked in `docs/STATUS.md`; items 1-4 below are ALL LANDED — BPH, WPS, and WB landed, and Ally Participation + Common Peace LANDED as the Imperial Settlement system, complete through Slice G1 (July 2, 2026, commit `1a9da53`).

1. `Memory and Pressure` (renamed from `Reliability + Commitments` April 16)
   **✅ COMPLETE — Memory and Pressure v2.4.3, all slices landed (see `docs/RELIABILITY_IMPLEMENTATION_PLAN.md`). The remaining-work list and the "~68-74 tests, ~3 sessions remaining" estimate below are historical v2.2-era text.**
   Substrate (betrayal memory, concern witness scope, hard-reject posture, episode_id, structured warnings) is **shipped**. Remaining work this phase: seed `nation_concerns` (4 authored pairs), wire `direct_concern_mod` + `concern_conflict_mod` + graduated `bilateral_betrayal_mod` into acceptance, wire third-party anger on ratification, redemption tick (`actor_honored_turns` +3 / 5 honored turns at OPEN_BORDERS+), rename `alliance_paradox` → `commitment_paradox`, ship C3-lite presentation pass (spotlight tier, split-voice render, named-diplomat resolution per Voice Bible). See `docs/RELIABILITY_COMMITMENTS_SPEC.md` v2.2, `RELIABILITY_IMPLEMENTATION_PLAN.md`, `COMMITMENTS_PRESENTATION_SPEC.md` v0.4 (C3-lite). ~68-74 tests, ~3 sessions remaining (Slice C split into Godot-surfaces + tests/mock-prose sessions; v2.2 renames rivalry→concern for balance-of-power scale architecture + adds auto-downgrade rule + France-Austria concern pair + Make Amends verb).
   **Scale note (v2.2):** `nation_concerns` is named for the target dynamic balance-of-power architecture (see spec §7.7). v0.1 ships static seeded values; dynamic concern evaluation is `Nation Agendas` scope (queue item 5).
2. `Bilateral Peace Hardening`
   **✅ LANDED — shipped per `docs/BILATERAL_PEACE_HARDENING_SPEC.md`.**
   Tighten separate peace / bilateral peace preview, explicit term ownership, promise-breach warnings, and peace-treaty legibility before any ally-aware settlement system exists. **Needs dedicated spec.**
3. `War Purpose + Score Semantics`
   **✅ LANDED — shipped per `docs/WAR_PURPOSE_SCORE_SEMANTICS_SPEC.md`; `war_objectives`, forced alliance, and liberation are live in code.**
   Collapse war objectives, ticking war score, vassalage power cap, forced alliance, and liberation into one war-goal / score-legibility spec. **Needs dedicated spec.**
3.5. `War Bargains` — `docs/WAR_BARGAIN_SPEC.md`
   **✅ LANDED April 2026 — the `war_bargain` mechanic shipped per the spec.**
   The named-enemy bilateral promise mechanic split out of `Reliability + Commitments` v1.0 in the April 16 rescope. Adds `war_bargain` clause type, lifecycle (active / triggered / fulfilled / void / breached), `join_opportunity` ally-entry contract, counter-bargains, `war_entry_score`, Bargain Review surface, and the WB-D presentation extension (bargain spotlights, scope-branched copy, response routes). **Depends on items 1-3.** Implementable as a single Peace Deals phase precursor before item 4. ~80-90 tests.
4. `Ally Participation + Common Peace`
   **✅ LANDED — shipped as the Imperial Settlement system, complete through Slice G1 (July 2, 2026, commit `1a9da53`); see `docs/SETTLEMENT_UI_CLEANUP_SPEC.md` v0.32 and `docs/STATUS.md`.**
   Build contribution, consultation, ally beneficiaries, and common peace as a separate wartime-flow system. **Current state:** the dedicated spec and implementation plan now own the active Slice A handoff; this item is no longer merely a later-direction draft.
5. `Nation Agendas + Motive Legibility`
   **OPEN — owner: the 8.EVAL evaluation gate (`docs/ROADMAP.md`). Collapsed item list unchanged.**
   Collapse `R155`, `R156`, `A3`, `R123`, and `R124` into one agenda-driven AI diplomacy spec. **Also owns the dynamic concern system:** converting `nation_concerns` from static seeded values (shipped in Memory and Pressure) to dynamic balance-of-power evaluation driven by territory, military power, treaty opposition, and proximity — the Napoleonic "your success creates your opposition" loop. See `RELIABILITY_COMMITMENTS_SPEC.md` §7.7 for the scale architecture target and the "what breaks at 15+ nations" punch list.
6. `Talleyrand Desk + Explanation Layer`
   **OPEN — owner: the 8.EVAL evaluation gate (`docs/ROADMAP.md`). Collapsed item list unchanged.**
   Collapse `R131`, `R132`, `R17d`, `R17e`, `R17f`, `R157`, and `R159` into one explanation / trend / advisory surface spec.
7. `Economic Diplomacy`
   **RE-POINTED — owner: `docs/ECONOMY_REVISIT_SPEC.md` EC-8 (economic diplomacy, incl. R161). Original text kept as historical context.**
   Collapse `R161` plus diplomacy-facing B4 candidates into one reciprocal-trade / subsidy / pressure spec.

**Diplo-wide ledger rows `DWL-DIP-E7` + `DWL-DIP-METTERNICH`:** their "settlement final gate closes" trigger goes LIVE when the user confirms the Gate 4 visual half (the smoke's HTTP half ran July 2, 2026) — they enter the 8.EVAL evaluation gate at that point.

### Still lower priority

- `R162: AI Ultimatums to Player` is no longer blocked by the old attention contract, but it should still wait until the commitment and agenda specs above are written. It adds interruption surface before the core diplomacy has enough political weight. **(July 2, 2026: R162 stays gated behind queue items 5-6, which are owned by the 8.EVAL evaluation gate.)**
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
- **Owner (July 2, 2026):** 8.EVAL triage.
- **Summary:** Add feedback when diplomatic override actions succeed/fail.
- **Details:** Success: +2 trust + dispatch note. Failure: +1 concern boost + dispatch note. Fix timing bug at diplomatic_defiance.py:741.
- **Files:** `diplomatic_defiance.py`, `dispatch.py`

### R128: Sabotage Consequence Feedback
- **Category:** Player Feedback
- **Owner (July 2, 2026):** 8.EVAL triage.
- **Summary:** Track and report sabotage outcomes with Talleyrand feedback.
- **Details:** Track in `world.sabotage_history`. Dispatch note next turn. Trust +3 if Talleyrand was correct.
- **Files:** `diplomatic_defiance.py`, `dispatch.py`

### R132: Vassal Loyalty Transparency — **80/20 LANDED July 10, 2026 (W6-3 `reason` field + W6-9 war-room trend/cause block)**
- **Category:** Player Feedback
- **Summary:** Real-time vassal loyalty deltas and trend tracking.
- **Details:** Lower warning threshold to 30. Show delta when |change| >= 2. Store `prev_loyalty`. Trend arrow in ledger. **Landed shape:** `vassal_loyalty` events carry the dominant-cause `reason` at emission (W6-3 §5.4); the W6-9 assessment renders loyalty + drift trend + the most recent cause per vassal. The residual (ledger trend arrow, threshold tune) stays queue-item-6 (8.EVAL).
- **Files:** `dispatch.py`, `vassal.py`, `diplomatic_ledger.py`, `diplomatic_advisory.py`

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

### Memory and Pressure interaction notes (updated for v2.4.3)

These are not new items — they annotate existing items whose scope or interaction changes now that Memory and Pressure v2.4.3 is the active spec.

- **R162 (AI Ultimatums to Player):** Hard-reject posture (3+ bilateral strikes) still informs ultimatum behavior, but the surrounding political pressure is now hegemony-driven rather than rivalry-seeded. A nation at hard-reject posture toward France is both more likely to issue ultimatums (anger-driven) and less likely to accept French counter-offers. Wire this interaction when R162 ships.
- **R123 / R124 (Economic Strategy & Diplomatic Isolation AI):** These collapse into queue item 5 (Nation Agendas + Motive Legibility). AI should now read `hegemony_target_mod`, `bilateral_betrayal_mod`, and (when DG-4 lands) `grievance_modifier` plus bloc geometry to drive subsidy offers, alliance-breaking proposals, and isolation strategy. Static `nation_rivalries` / `rival_conflict_mod` are no longer the data source.
- **R17d (DP Breakdown Display):** Show the live Memory and Pressure acceptance components individually rather than reviving the old composite term: `hegemony_target_mod`, `bilateral_betrayal_mod`, `reliability_modifier`, and later `grievance_modifier` / `composite_floor` when DG-4 is active.
- **R155 / R157 (AI Proposal Voice / Talleyrand Voice Depth):** The C3-lite presentation pass (`COMMITMENTS_PRESENTATION_SPEC.md` v0.5.1) now commits named-diplomat CRITICAL / NORMAL notices, the paradox popup, Balance-of-Europe threshold beats, and Make Amends acknowledgments per `DIPLOMAT_VOICE_BIBLE.md`. The broader scope (personality-driven proposal timing, AI-initiated proposal voice, deep Talleyrand commentary across all diplomacy) remains open and routes to queue items 5-6.

---

## Focused Audit Validation (Apr 10, 2026)

The focused attention / AI diplomacy audit tightened which diplomacy legitimacy items are already justified, which ones need bug-fix prerequisites, and which old notes are now stale.

### Already justified by current evidence

- **R160: Nation Rivalry System** — confirmed as the highest-leverage legitimacy upgrade. Current diplomacy still lets France drift toward broad friendship without enough forced political choice. *(Since SUPERSEDED by Memory and Pressure v2.4.3 — see the R160 row below.)*
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
- `Ally Participation + Common Peace`: active wartime settlement layer; implementation starts from `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` Slice A.
- `Nation Agendas + Motive Legibility`: make AI motives and strategic branching legible to the player.

---

## Needs Design Gate

### R160: Nation Rivalry System (EU4-Inspired) — **SUPERSEDED BY Memory and Pressure v2.4.3**
- **Category:** Diplomacy — Balance
- **Status:** Static rivalry seed and the old rivalry-specific acceptance terms were dropped in the v2.4 hegemony refactor. The live political-pressure layer is now `hegemony_target_mod` + `bilateral_betrayal_mod`, with `grievance_modifier` joining later via DG-4. The original R160 design is therefore superseded by `RELIABILITY_COMMITMENTS_SPEC.md` v2.4.3 rather than partially awaiting completion.
- **Remaining (unshipped):** any future dynamic rivalry / agenda system must grow out of bloc geometry, betrayal memory, grievance persistence, and AI agendas rather than restoring `nation_rivalries` / `direct_rivalry_mod` / `rival_conflict_mod`. That work still belongs to queue item 5 (`Nation Agendas + Motive Legibility`).
- **Files:** `diplomacy.py`, `ai_diplomacy.py`, `diplomatic_ledger.py`, `world_state.py`

### R151: Territorial Promise Clauses — **LANDED via WAR_BARGAIN_SPEC (April 2026)**
- **Category:** Diplomacy Feature
- **Disposition (July 2, 2026):** ✅ LANDED — the `war_bargain` mechanic shipped April 2026; the "scheduled in the Peace Deals phase" text below is historical.
- **Status:** The broader concept (France makes named-enemy promises to allies, tracking obligation, breach/fulfillment, betrayal consequences) is now fully designed as the `war_bargain` clause type in `docs/WAR_BARGAIN_SPEC.md`. The spec covers creation, validation, lifecycle, fulfillment, breach/void, war-entry integration, and the Bargain Review surface. Scheduled in the Peace Deals phase after `Bilateral Peace Hardening` + `War Purpose + Score Semantics` (queue items 2-3.5).
- **Files:** `diplomacy.py`, `ai_diplomacy.py`, `diplomatic_executor.py`

### Jealousy System (v3.1 spec)
- **Category:** Marshal Feature
- **Summary:** Glory Ladder targeting, personality expressions, escalation, confrontation popups.
- **Details:** Full spec at `docs/JEALOUSY_SPEC.md`. Core design settled. Top of ladder: +1 all core stats while #1. Defeats cost glory. DO NOT CODE WITHOUT USER APPROVAL.
- **Sequencing note July 2, 2026:** the Marshal Content Pass (`docs/MARSHAL_CONTENT_PASS_SPEC.md`, MC-3 relationship authoring) is effectively a prerequisite — the shipped 21-marshal roster has zero authored relationships; a v3.2 addendum must re-derive scenario impact/tuning against that roster before the gate.

---

## War System Overhaul (EU4-Inspired — Design Gate) — **✅ LANDED**

**Disposition (July 2, 2026):** this entire section LANDED via the War Purpose + Score Semantics work (`docs/WAR_PURPOSE_SCORE_SEMANTICS_SPEC.md`) — `world.war_objectives` ticking score, the vassalage power cap, the `forced_alliance` clause type, and the liberation mechanic are all live in code. The text below is preserved as historical design intent.

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
- **Disposition (July 2, 2026):** the proposal-side integration is LANDED in `ai_diplomacy.py`; the residual (the `enemy_ai.py` war-vs-diplomacy choice) rides queue item 5 (`Nation Agendas + Motive Legibility`), per the Memory and Pressure interaction note above.
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

**July 2, 2026:** per-item user approval is still required. Items already re-pointed above have new owners: R26 → `docs/ECONOMY_REVISIT_SPEC.md` EC-5 (Continental System); R161 → `ECONOMY_REVISIT_SPEC.md` EC-8; R162 → gated behind queue items 5-6 (8.EVAL).

| ID | Item | Summary |
|----|------|---------|
| R22 | Marriage Alliances | Dynastic bonds: +20 rel, block war 5 turns, 3 DP |
| R32 | Peace Conferences | Multi-nation negotiations, 3 DP, +15 acceptance |
| R117 | Advisory Actionability — **✅ LANDED July 10, 2026 via W6-9** (the war-room assessment's ONE recommendation ends in an executable option: `execute_suggestion` / `expand_options`) | Advisory ends with executable options |
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
| R59 | ~~Literal Personality Triggers~~ | **SUPERSEDED by W6-5 The Literal Doctrine (user call, July 10, 2026):** literal marshals never object BY DESIGN — the fantasy is "generals who do what they're ordered." Engagement = order echo + fidelity beat + precision captions + muster-preview warnings (`WAVE6_FUN_FACTOR_SPEC.md` §7; triggers converted to a doctrine comment in `personality.py`, pinned by `test_w6_literal_doctrine.py`). |
| R118 | Enhanced Acceptance Preview | Top 3 positive/negative components + Talleyrand hints |
| R161 | One-Time Trade | Trade gold, manpower, territory directly without ultimatum or state change |
| R162 | AI Ultimatums to Player | Building Blocks: AI uses same ultimatum system as player. Needs popup, response flow, AI decision tree |

---

### R161: One-Time Trade (Expanded)
- **Category:** Diplomacy Feature
- **Owner (July 2, 2026):** re-pointed to `docs/ECONOMY_REVISIT_SPEC.md` EC-8 (economic diplomacy, alongside queue item 7). Original design text kept as historical context.
- **Summary:** Voluntary, consensual resource exchange between nations — no state change, no coercion. The "carrot" complement to ultimatums (the "stick").
- **Details:** Player proposes a trade (gold, manpower, territory) to any nation at OPEN_BORDERS or better. Both sides give and receive. Uses existing conversational diplomacy flow with `generate_trade_terms()`. Acceptance via full formula. No threat increase, no relation penalty — pure commerce.
- **Building Blocks principle:** Reuses `_ratify_treaty` clause processing, `calculate_acceptance()`, dialogue enrichment, splash damage (none for trades). Same executor path as proposals but with `type: "trade"` and no state transition.
- **Distinction from ultimatums:** Trades are voluntary (both sides benefit), ultimatums are coercive (one-sided demands with diplomatic cost).
- **Gates needed:** Trade balance formula (what's fair?), AI trade evaluation, frequency limits.
- **Files:** `diplomatic_executor.py`, `diplomatic_templates.py`, `diplomacy.py` (new base disposition for trade), `diplomatic_dialogue.py`
- **Est. sessions:** 1-2, ~8 tests

### R162: AI Ultimatums to Player
- **Category:** AI Diplomacy — Building Blocks
- **Status (July 2, 2026):** stays gated behind queue items 5-6 (Nation Agendas + Talleyrand Desk), which are owned by the 8.EVAL evaluation gate.
- **Summary:** AI nations issue ultimatums to the player using the same ultimatum system the player uses. Building Blocks principle (§23): same systems, different input values.
- **Details:** AI evaluates ultimatum opportunity in `enemy_ai.py` decision tree (new P-trigger). Conditions: military superiority over player in a region, low relations, not in coalition with player. Generates terms via `generate_ultimatum_terms()` (same function player uses). Delivered as popup with [Accept][Reject] options. Rejection gives AI casus belli. Same splash damage, threat (reduces player threat if AI is aggressor), and cooldown mechanics.
- **Building Blocks reuse:** `generate_ultimatum_terms()`, `calculate_acceptance()` (inverted — player is target), `_ratify_treaty` clause processing, splash damage formula, global cooldown (separate AI cooldown counter).
- **Gates needed:** AI trigger conditions (when is ultimatum better than war declaration?), player response popup design, threat direction (does AI ultimatum reduce or increase player threat?).
- **Files:** `enemy_ai.py` (new P-trigger), `diplomatic_executor.py` (AI ultimatum handler), `main.gd` (new popup), `ai_diplomacy.py`
- **Est. sessions:** 2-3, ~12 tests

### National Power Tiers (Great Power / Secondary / Minor) — Design Gate
- **SUPERSEDED — April 17, 2026.** Canonical `power_tier` is now defined in `docs/SCALE_READINESS_PLAN.md` §"Phase 0 Cross-Cutting Taxonomy". Under the canonical definition, `power_tier` is **authored scenario data** with values `major / secondary / minor` and is **never recomputed at runtime**. The dynamic numeric-tier model below is superseded and must not be implemented. If a numeric strength-derived signal is needed for AI threat weighting, coalition calculations, or dispatch priority, it lives in a separate `power_score` field that does not overwrite `power_tier`. The original text is preserved below as historical design intent.
- **Residual disposition (July 2, 2026):** the tier model stays SUPERSEDED — Phase 0's authored `power_tier` shipped with the real-map cutover. The optional numeric `power_score` idea: evaluate at the 8.EVAL gate, else drop.
- **Category:** Diplomacy + War — Balance + Immersion
- **Summary:** Dynamic numeric power tiers (`great_power / secondary_power / minor_power`) calculated from controlled regions, income, military strength, and partial vassal contribution. Affects acceptance formula (great powers resist vassalization), coalition formation (great powers lead coalitions, minor powers join), war settlement (consultation rights scale with tier), and AI threat assessment (great powers escalate coalition faster).
- **Origin:** Conceptual three-tier model exists in `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` §8.3. Data fields (`nation_power_scores`, `nation_power_tiers`) listed as deferred in `RELIABILITY_COMMITMENTS_SPEC.md` §12.3.
- **Design decision from WAR_SETTLEMENT spec (superseded):** "These tiers come from numbers, not authored nation labels. The map can create a new quadrangle if power shifts." — This position is reversed by the Phase 0 canonicalization: tiers are now authored, not numeric. A separate `power_score` may still be derived from numbers for non-tier uses.
- **Interaction with Memory and Pressure:** great powers could have different rivalry intensity defaults (primary only between great powers; secondary between great-and-minor), betrayal tolerance thresholds (great powers hold grudges longer), and Make Amends cost scaling (reparations to a great power should cost more than to a minor).
- **Gates needed:** numeric formula for calculating power scores, threshold ranges (what income/strength makes a "great power"), whether tiers are recalculated per turn or per-war, how tiers interact with the acceptance formula's existing modifier caps.
- **Natural home:** alongside `War Purpose + Score Semantics` (queue item 3) since power tiers inform war objectives and settlement legitimacy. Or as a sub-item of the later `Ally Participation + Common Peace` (queue item 4).
- **Files:** `world_state.py` (data), `diplomacy.py` (formula + tiers), `diplomatic_ledger.py` (display), `ai_diplomacy.py` (threat evaluation)
- **Est. sessions:** 1-2 for the data layer + formula, plus formula-integration touches across existing systems

---

## Gold Sink Options (B4 Balance — Design Gate)

**Priority:** MEDIUM | **Phase:** Pre-EA refinement

**RE-POINTED (July 2, 2026):** owner is `docs/ECONOMY_REVISIT_SPEC.md` EC-2 (the B4 gold-sinks gate). The candidates below are re-cost candidates for the ~3.4k/turn 1805 economy — France income is ~3.4k/turn on 28 provinces, upkeep ~950g, and the whole building stock costs ~1.85k — so this section's "~700g vs ~250g" numbers are legacy (19-region map). Original text kept as historical context.

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

**RE-POINTED (July 2, 2026):** owner is `docs/ECONOMY_REVISIT_SPEC.md` EC-4 (enemy AP). The revisit trigger fired July 2, 2026 — the full 1805 map shipped with the real-map cutover. NOTE: the EC-0 AP-reset defect must land first. Original text kept as historical context.

Enemy AI action budget (currently 4 paid AP per nation) may need rebalancing once the full map is implemented with all nations, regions, and marshal counts at scale. Current 4-nation, 19-region map doesn't stress the action economy the same way a full campaign will. Revisit AP values, per-nation scaling, and aggregate action counts after full map playtesting.

---

## Wave 5 — Game Review Findings (Design Gate)

Cross-system findings from comprehensive review. Needs design gate as a batch.

**July 2, 2026:** per-item user approval is still required. Items already re-pointed above have new owners: R158 → `docs/COMMAND_ROBUSTNESS_SPEC.md` CR-7 (parser confidence feedback).

**Diplomatic Term Novelty — PARTIALLY ABSORBED into PL-25 (BUG_FIXES.md).** PL-25 covers the 80/20: amount jitter, personality-biased pen nudge, nation desire profile bias in `_build_base_terms()`, situational flavor lines. R155/R157 retain the remaining full scope: hawk/dove personality weight table for ALL AI proposals (not just Talleyrand's pen nudge), deep `TALLEYRAND_COMMENTARY` integration, and AI-initiated proposal personality voice.

**Focused audit routing (updated July 2, 2026):** R155 / R156 remain validated by code evidence and route to queue items 5-6 (8.EVAL). R160 is SUPERSEDED by Memory and Pressure v2.4.3 (see its row above) — it is no longer a pending upgrade. The diplomacy mailbox / recovery surface LANDED long since; R162 is not transport-blocked, it stays gated behind queue items 5-6.

| ID | Item | Summary |
|----|------|---------|
| R152 | Authority System UI Visibility | Authority impact not visible enough to players |
| R153 | ~~Literal Personality Triggers~~ | **SUPERSEDED by W6-5 The Literal Doctrine (user call, July 10, 2026)** — see the R59 row; literal never objects by design. |
| R154 | Combat Morale Spiral | Morale death spiral needs circuit breaker |
| R155 | AI Proposal Personality Voice | Partially absorbed into PL-25. Remaining: visible motive / personality in timing, terms, persistence, and player-facing explanation |
| R156 | Diplomacy Strategic Optionality | Diplomacy feels optional vs military path |
| R157 | Talleyrand Voice Depth | Partially absorbed into PL-25 (situational flavor, personality pen nudge). Remaining: deep commentary integration |
| R158 | NL Parser Confidence Feedback | Show parse confidence to player |
| R159 | Information Screen Teaching | Screens don't teach mechanics |

---

## Wave 6 — Creative Capstone (July 10, 2026) — **✅ APPROVED IN FULL; owner = `docs/WAVE6_FUN_FACTOR_SPEC.md`**

> Source: `docs/audits/CREATIVE_AUDIT_2026_07_10.md` (the AUDIT_GUIDELINE §8 fun-factor capstone — live 5-turn 1805 playtest under `LLM_MODE=anthropic` + two code-evidence sweeps). **GATE (July 10, 2026, same day): the user approved EVERY item below in full — plus two additions scoped at the gate: Dynamic Battle Naming (→ spec slice W6-2) and the Literal Doctrine hone (→ W6-5; user steer: literal marshals need not object — the fantasy is "generals who do what they're ordered").** The build-ready plan — slice order, seams, blessed default numbers, tests — is **`docs/WAVE6_FUN_FACTOR_SPEC.md`** (authoritative over the sketches below where they differ). Rows below map: EXP-N1→W6-3 · EXP-M1→W6-7 · EXP-C1→W6-4 · EXP-E1→W6-8 · EXP-M2→W6-6 · EXP-D1→W6-9 · E-CA-1/3→W6-11 · E-CA-2→W6-1 · E-CA-4→W6-4 · E-CA-5/6→W6-10.

### Gate additions (scoped at the July-10 approval; full designs in the spec)

| ID | Item | One-line mechanic | Spec slice |
|----|------|-------------------|------------|
| W6-ADD-1 | **Dynamic Battle Naming** | Serialized per-region battle counts → "Second Battle of Swabia", "The Great Battle of X" at ≥80k engaged; one naming site (`combat_executor` battle_name), consumed everywhere `battle_name` already flows. | W6-2 |
| W6-ADD-2 | **The Literal Doctrine** | Literal = "generals who do exactly what they're ordered": never objects **by design** (supersedes R59/R153's literal-objection TODOs), order echo + completion reports quoting the verbatim order, doctrine tells on card/dispatch/muster, per-turn **fidelity beats** ("Soult holds at Lorraine, per your orders — the guns did not move him"), precision rewards captioned. Builds on the existing Grouchy Rule (`combat_executor._calculate_reinforcements`) and SUPPORT standing orders. | W6-5 |

### Ranked expansions (by depth-per-unit-complexity — full designs in the memo §4; build detail in the spec)

| ID | Item | One-line mechanic | Owner / gate | Est. |
|----|------|-------------------|--------------|------|
| EXP-N1 | **The Dispatch Rewrite — "Berthier tells the story"** | Deterministic narrative-priority layer over existing events: headline selection, per-marshal danger flags, arc memory ("Bernadotte, hunted across three frontiers…"). No LLM, no new mechanics. | Standalone slice; **top-ranked item of the audit** | 1–2 sessions |
| EXP-M1 | **Marshal Fates: capture, parole, last stand** | Forced-retreat fate roll (escape/capture/personality-gated last stand); captured marshals become ransom/exchange clauses in existing settlement machinery; Building Blocks — Mack at Ulm becomes capturable. | Own design gate (thresholds, AI prisoner valuation) | 2–3 sessions |
| EXP-C1 | **March to the Guns, surfaced: muster preview + standing order** | Pre-battle muster block naming WILL JOIN / WILL NOT per marshal *with the personality reason*; cheap `"Soult, support Ney"` standing order; substrate the re-homed **Grouchy Moment** lands on. | Own gate; foundation for the Grouchy Moment gate | 1–2 sessions |
| EXP-E1 | **The Spoils of War: estate confiscation** — **✅ LANDED July 10, 2026 via W6-8** (`WAVE6_FUN_FACTOR_SPEC.md` §10; `test_w6_estate_confiscation.py`) | Conquering an enemy marshal's estate opens confiscate (windfall + grudge + own-cautious-marshal trust cost) vs respect (court acceptance bonus); confiscated estates become grantable (rides ES-7 as landed). Resolves the live "Swabia already sustains Marshal Mack's household" dead end. | ~~EC pass 2 gate (numbers)~~ numbers blessed at the July-10 Wave-6 gate (in-band tunable) | ~1 session |
| EXP-M2 | **Enemy marshals speak** | Deterministic one-liner bank keyed to (enemy personality × outcome × situation) at the battle-report seam; complements DEF-1 (diplomat voices), which does not own enemy marshals. | Content slice; MC-adjacent | <1 session |
| EXP-D1 | **"What does Europe intend?" — strategic assessment verb** — **✅ LANDED July 10, 2026 via W6-9** (`WAVE6_FUN_FACTOR_SPEC.md` §11; `test_w6_assessment_verb.py`) | `assess our situation` (dead-ends live today) returns per-war trajectory, **coalition posture** (computed, never shown), top threat sources, vassal trend + cause, one executable recommendation (absorbs R117's shape). | ~~Recommended first slice of queue item 6 (Talleyrand Desk)~~ landed via W6-9; queue item 6 owns the residual desk items | ~1 session |

### Escalations (gate-owned; no code)

| ID | Finding | Owner |
|----|---------|-------|
| E-CA-1 | Attacker morale-grind asymmetry (defender morale ~static through 15k casualties while attackers/reinforcers bleed to 47) — the live shape of the meat-grinder, post-EC. — **✅ LANDED July 10, 2026 via W6-11** (symmetric casualty-scaled morale in both combat copies, winner delta = bonus − loss; `test_w6_balance_duo.py` incl. the battle-2 replay) | ~~Combat balance gate (user)~~ landed at the blessed W6 numbers (defender curve 1.0, band ≥0.75) |
| E-CA-2 | Retreat agency + direction doctrine (honor stated destination or narrate substitution; homeward bias; never into an at-war nation with alternatives). Mechanical half = BUG-CA-2. | Combat/movement gate |
| E-CA-3 | War-priced recruitment: 10,000 men for 200g keeps gold free mid-war; scale per-soldier gold cost by force-limit ratio + war status. — **✅ LANDED July 10, 2026 via W6-11** (×3 at war composed with ×(1+overage), Europe-scoped, AI same-priced incl. its admin pre-checks; two-sided 1805 solvency pinned; `test_w6_balance_duo.py`) | ~~EC pass 2 (blessed numbers)~~ landed at the blessed W6 numbers (war ×3, band 2–4) |
| E-CA-4 | Explicit bad-odds `attack` gets no warning while vague delegation gets a lethal-odds interrupt — decide whether direct orders deserve a one-line odds note. | CR-6 gate |
| E-CA-5 | Settlement offers must state territorial consequences ("Britain retains Flanders") — "Peace" is illegible while home soil is occupied. — **✅ LANDED July 10, 2026 via W6-10** (`terms_summary` status-quo line; `test_w6_incoming_voice.py`) | ~~Settlement presentation (narrow, post-arc)~~ landed |
| E-CA-6 | Incoming-proposal voice + AI proposal variety (5 identical open-borders/"hegemony pressure" offers in 5 turns; named diplomat never speaks). — **✅ LANDED July 10, 2026 via W6-10** (`diplomat_line` register bank + 6-turn lapse/reject type cooldown + P3 relation-band diversification; `test_w6_incoming_voice.py`). The deeper R155/R156 scope (personality-driven timing/persistence/target choice, strategic optionality) stays with queue items 5–6. | ~~Queue items 5–6 (8.EVAL), with R155/R156~~ voice+variety landed; residual scope stays 8.EVAL |

### Revisions to prior items (live-evidence pass, July 10, 2026)

- **R154 (Combat Morale Spiral) — REVISED:** the claimed missing circuit breaker **exists and works** (`combat.py` FORCED_RETREAT_THRESHOLD=25 floor; +5/+10 victory recovery). The real, live-confirmed issue is the attacker/defender morale **asymmetry** — re-scoped as E-CA-1; do not build a second breaker.
- **R59 / R153 (Literal Personality Triggers) — RESOLVED July 10, 2026: SUPERSEDED by W6-5 The Literal Doctrine (user call at the Wave 6 gate).** Literal marshals never object BY DESIGN; the inert triggers were converted to a doctrine comment and the never-objects behavior is pinned (`test_w6_literal_doctrine.py`). The niche the triggers aimed at is owned by the CR-2/CR-5 clarification arms + the W6-5 fidelity surfaces (order echo, fidelity beat, muster warnings). |
- **R129 / R131 / R132 — LIVE EVIDENCE ADDED:** R132 is the strongest of the three — three vassals bleeding −4/−6/−8 loyalty per turn with no cause attached anywhere was a top-5 confusion of the playtest. Recommend R132 rides EXP-D1/queue-item-6 rather than waiting for a standalone slice.
- **R155 / R156 — CONFIRMED, EVIDENCE UPGRADED:** proposal monotony measured live (5 nations, identical proposal+reason, 5 turns); the *outgoing* surface (terms prep, acceptance estimate, ratification gate, motive commentary) is the register benchmark the incoming surface should be held to. Folded into E-CA-6.
- **R117 (Advisory Actionability) — ABSORBED into EXP-D1** (the strategic-assessment verb ends with an executable option).

---

## Historical Precision (1805 Campaign — Future Refinement)

These items are conscious trade-offs where v0.1 chose recognizability, immersion, or implementation speed over strict period accuracy. Each has an audit trail, not a bug. Track for EA scope when the full 1805 campaign lands. Added April 16, 2026 from the Memory and Pressure creative audit.

### P1: Period-accurate diplomat roster for 1805
- **Summary:** The four foreign diplomats in `backend/models/diplomat.py` (Hardenberg / Metternich / Castlereagh / Einsiedel) are recognizable Napoleonic-era names but historically took their depicted roles **after** the 1805 campaign start: Hardenberg as Prussian chancellor from 1810, Metternich as Austrian foreign minister from 1809, Castlereagh as British foreign secretary from 1812, Einsiedel as Saxon minister from 1813. The actual 1805 ministers were Haugwitz (Prussia), Stadion or Cobenzl (Austria), Mulgrave (Britain), and Bose or Löss (Saxony).
- **Design trade-off (deliberate):** recognizability was prioritized for v0.1 because the four chosen figures are well known to strategy players and the Voice Bible's Hawk / Schemer / Dove register distinctions were drawn from their historical voices. Swapping them in v0.1 would lose the established register voices without adding mechanical value and would force the Voice Bible exemplars to be re-authored before any useful commitments work shipped.
- **When to revisit:** once the full 1805 campaign ships (Early Access) and the game claims period fidelity as a feature. Swap to the 1805-accurate ministers and port the register notes. The Voice Bible's "Characteristic openings" / "Never says" framework should transfer cleanly — Haugwitz was a Prussian Hawk in the Hardenberg mold, Stadion a Schemer adjacent to Metternich, Mulgrave less distinctive than Castlereagh but workable, Bose closer to Einsiedel's dove register.
- **Revisit condition MET July 2, 2026:** the full 1805 campaign shipped (real-map cutover complete). Still EA-scope; interacts with DEF-1 Roster Voices register authoring.
- **Files:** `backend/models/diplomat.py`, `docs/DIPLOMAT_VOICE_BIBLE.md`, `backend/game_logic/diplomatic_templates.py`, any committed breach / hard-reject mock prose
- **Est. sessions:** 1 (cast swap + voice port + test refresh)

### P2: Britain reactive bloc pressure (continental-hegemon pattern)
- **Summary:** The v0.1 rivalry model has Britain as France's direct rival but gives Britain no *reactive* posture when France deepens ties with a continental power. Historically Britain opposed any continental hegemon on principle, paying subsidies to any continental power willing to fight France. Flagged in `RELIABILITY_COMMITMENTS_SPEC.md` v2.1 §7.4.C as the #1 historical-texture debt for Memory and Pressure.
- **When to land:** `Coalition Generalization` (D2, follow-up after Memory and Pressure). D2 should include continental-hegemon reactive threat accumulation — not just bloc-target parameterization — so Britain gains automatic threat against any power approaching continental hegemony, not only France by name.
- **Owner (updated July 2, 2026):** the `docs/RELIABILITY_IMPLEMENTATION_PLAN.md` deferred-ledger D2 row. The previously-named "Coalition Generalization (D2)" is not a landed slice — this item rides that deferred-ledger row.
- **Files:** `backend/game_logic/coalition.py`, `backend/game_logic/diplomacy.py`
- **Est. sessions:** folded into D2 spec work

### P3: Diplomatic Ledger sort / filter at scale
- **Summary:** The Diplomatic Ledger's Nations tab currently renders one row per nation. At 5 nations this is clean; at 6-8 full 1805 nations with multiple rivals each, the list becomes dense. Commitments rows (active rivals, betrayal warnings, posture markers) multiply the cell count.
- **When to land:** Pre-EA polish alongside Map Renderer UX pass, or absorbed into the Talleyrand Desk + Explanation Layer spec (diplomacy queue item 6).
- **Urgency raised (July 2, 2026):** 20 nations render now in the shipped 1805 campaign. Owner: queue item 6 (Talleyrand Desk + Explanation Layer) or pre-EA polish.
- **Files:** `godot-client/project-sovereign/scripts/diplomatic_ledger.gd`
- **Est. sessions:** 1 as a standalone UX slice, or folded into the Talleyrand Desk pass

---

## Estate Second Pass deferrals (July 11, 2026)

Filed at the ES-7 second-pass build (`ECONOMY_REVISIT_SPEC.md` §0.6.8 — the estates+rentes reward portfolio). Historically grounded in the July-11 design conversation (Domaine Extraordinaire rentes/arrears; Fontainebleau April 1814; Murat's January-1814 Austria treaty).

> **✅ ESP-1, ESP-2, and ESP-4 LANDED July 11, 2026** with the Jealousy v3.2 build (`JEALOUSY_SPEC.md` §0.3 rider contracts + §0.4 landing record; `tests/test_estate_riders_esp.py`, 22). ESP-2 landed at the declare-war seam via the marshal-petition channel rather than objection_v2 — recorded deviation, §0.3. ESP-3 remains open with its diplomacy-gate owner below.

### ESP-1: The Fontainebleau beat (collective marshal petition) — ✅ LANDED
- **Summary:** When several marshals are eroding simultaneously (shortfall past grace), the system today runs parallel silent trust bleeds. History says this moment *speaks*: at Fontainebleau the marshals collectively told Napoleon "the army will not march" and forced the abdication. Fire a collective dialogue when ≥3 marshals are eroding on the same turn — a petition demanding estates, rentes, or peace, with real player choices (concede / refuse with trust cost / partial). Converts the death spiral from a punishment into the game's best scene.
- **When to land:** Jealousy v3.1 gate (next queue item) — the gate already owns marshal-collective emotional mechanics; this is its natural marquee event.
- **Completion definition:** the petition fires under the trigger in a live game, is answerable via popup, each arm has deterministic effects and tests, and STATUS records the landing.
- **Files:** `backend/models/world_state.py` (`_process_dotation_state` trigger), `backend/models/dialogue_manager.py`, `backend/game_logic/dotation.py`, Godot dialogue whitelist (per the dialogue-popup-wiring rule).
- **Est. sessions:** 1

### ESP-2: War-weary rich marshals (satisfaction objects to new wars) — ✅ LANDED
- **Summary:** Historically the *endowed* marshals were the peace party — by 1812–13 the men with duchies begged Napoleon to stop. Mechanically: a marshal whose expectation is fully met and large (satisfaction ≥ a floor) gains an objection trigger against NEW aggressive war declarations ("I have my duchy, Sire — why do we march again?"). Rides the existing objection_v2 ConcernLevel machinery; no new dialogue plumbing.
- **When to land:** Jealousy v3.1 gate, same personality/emotion review.
- **Completion definition:** objection fires for a rich marshal on a player war declaration, never for poor marshals, GR5-checked where applicable, behavior tests.
- **Files:** `backend/commands/objection_v2.py`, `backend/game_logic/dotation.py` (satisfaction query), `backend/game_logic/diplomacy.py` (war-declaration seam).
- **Est. sessions:** 0.5 (folded into the Jealousy build)

### ESP-3: Respect-by-treaty (the Murat clause)
- **Summary:** Treaty transfers of estate provinces currently strip silently on the next tick; only military capture offers the confiscate/respect choice (W6-8). Historically treaty-preserved dotations were real furniture — Murat kept Naples by treaty with Austria (Jan 1814). On ratification of a settlement/treaty that hands YOU a province funding an enemy marshal's estate, fire the same confiscate/respect choice (AI uses its existing at-war rule); respect feeds the existing `respected_estate_mod` +5 acceptance term.
- **When to land:** a future diplomacy gate — touches ratification flow and acceptance math, so it must NOT land ad hoc. Candidate venue: 8.EVAL's diplomacy triage or a Settlement addendum gate.
- **Completion definition:** choice fires at the ratify seam for player-received estate provinces, AI symmetric, acceptance term verified, tests for both arms + the third-party-cede no-choice case.
- **Files:** `backend/game_logic/settlement_ratify.py`, `backend/models/world_state.py` (treaty-clause transfer), `backend/game_logic/dotation.py`, `godot-client/.../capture_choice_dialog.gd` (estate stage reuse).
- **Est. sessions:** 1

### ESP-4: Rente arrears/default beat — ✅ LANDED (folded into the Jealousy build per this row's fold-in clause)
- **Summary:** §0.6.8 pass-1 rentes charge like upkeep with no bankruptcy mercy. The historical texture — rentes chronically in arrears, marshals resenting unpaid paper — is a drama beat: when the treasury cannot cover the rente bill, rentes lapse (auto-revoke) with a notification ("the treasury defaults on his rente — he holds worthless paper, Sire") and the shortfall machinery reopens. Cheap, legible, and makes deficit-financing marshal loyalty a real risk.
- **When to land:** Economy pass 2 (EC-1 successor work), or fold into the Fontainebleau slice if the Jealousy gate takes ESP-1.
- **Completion definition:** insolvency lapses rentes deterministically at one defined seam, notification + dispatch line, both sides GR5, tests incl. the recovery case (re-grant after solvency returns).
- **Files:** `backend/models/world_state.py` (income/bankruptcy seam), `backend/game_logic/dotation.py`, `backend/notifications.py`.
- **Est. sessions:** 0.5

---

## Source Documents (Archived Reference)

| Document | Items Moved Here |
|----------|-----------------|
| `docs/DIPLO_REFINEMENT.md` | Wave 3-5 open items, all R-IDs |
| `docs/DIPLOMACY_DESIGN_FIXES.md` | Design discussion items, N1/A3/A4 AI fixes |
| `docs/archive/PLAYTEST_AUDIT_2026_03_29.md` | War Objectives, Ticking War Score, Vassalage Power Cap, Forced Alliance, Liberation (lines 215-722) |
| `docs/JEALOUSY_SPEC.md` | Jealousy pointer (spec kept as-is) |
