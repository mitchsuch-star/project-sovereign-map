# Ink & Iron: Master Roadmap

> **THE source of truth for all phases and timeline.**
> **Other docs reference this — phase numbers only exist here.**
> **Last Updated:** February 20, 2026 (Phase 7 Scope Decision — Core/7b Split)

---

## Quick Status

| Phase | Name | Status |
|-------|------|--------|
| 1-5.3 | Foundation through AI Fixes | COMPLETE |
| **V2a** | **Objection System Refactor** | **COMPLETE** |
| **6** | **Core Campaign Systems** | **COMPLETE** |
| **6.5** | **Information & UI Systems** | **IN PROGRESS** (Bombardment COMPLETE Sessions 48-52, Pause Menu COMPLETE Session 56) |
| **7 Core** | **Multi-Marshal Coordination** | **Spec COMPLETE + AUDITED + SCOPED.** 6 sessions (57-61, 64). ~190 tests. |
| 7b | Casualty Dist, AI Coord, Reports/UI, Tactical Triangle, V2b, Coalition, Jealousy | Planned (deferred from 7 Core) |
| 8 | Diplomacy & Peace | Planned |
| 8.5 | Events, Goals & National Identity | Planned |
| -- | **STEAM PAGE + LLC** | **After 8.5** |
| 9 | Advisors (Minimal) | Planned |
| 10 | Character & People (Minimal) | Planned |
| 11 | Vassals | Planned |
| Pre-EA | Polish & Infrastructure | Planned |
| EA | 1805 Campaign (Option C: Partial Europe) | TBD 2026 |

**Removed from EA scope:** Phase 12 (Communication cutoff), Naval abstraction, Full advisor action-gating. See [Post-EA Expansion](#post-ea-expansion).

---

## Completed Phases

| Phase | Name | Tests | Key Features |
|-------|------|-------|--------------|
| 1 | Foundation | ~80 | Core loop, actions, regions, marshals |
| 2 | Combat & AI | ~90 | Dice combat, enemy AI, stances, drill/fortify |
| 3 | Relationships | ~30 | Marshal relationships, historical values |
| 4 | LLM Integration | ~60 | Parsing, personality responses, BYOK |
| 5.1 | Tactical Feedback | 64 | Word-based scoring, strategic feedback |
| 5.2 | Strategic Commands | ~350 | MOVE_TO, PURSUE, HOLD, SUPPORT, interrupts, modding, Phase M (Strategic Objections) |
| 5.3 | Enemy AI Fixes | ~15 | Stagnation counter, oscillation fixes, consolidation |

**Total Tests:** 2987 (verified Feb 20, 2026)

---

## V2a: Objection System Refactor

**Goal:** Fix fundamental flaw where trust modifies WHETHER marshals speak instead of HOW they speak.

**Status:** COMPLETE. All 7 units shipped (1216 tests). See `OBJECTION_V2.md`.

**Key Changes:**
- Deterministic situational triggers (personality x situation -> ConcernLevel)
- Trust affects consequences only (tone, penalty, compliance)
- MILD concerns as end-of-turn flavor text, not popups
- V2b (defiance/vindication escalation) deferred to Phase 7

**New from Session 4 audit:**
- **Idle marshal objection (Unit 6):** Aggressive marshals idle 2-3 turns -> MILD ("Ney paces restlessly"). 4+ turns -> MODERATE ("Ney demands action"). Cautious at 5 turns. Literal never (Grouchy waits patiently). Add to V2a trigger tables in Unit 6 alongside strategic wiring.

**Post-V2a catch-up (before Phase 6):**
- Create `docs/TUTORIAL_SCRIPT.md` (living document, updated each phase)
- Review/update existing docs for Session 4 decisions

---

## Phase 6: Core Campaign Systems

**Goal:** Complete playable campaign loop with resources and win conditions.

| Feature | Description | Complexity | Status |
|---------|-------------|------------|--------|
| Economy | Income per region, treasury, upkeep | Medium | **6.2 COMPLETE** (6.2.A-H: region types, income, gold, upkeep, bankruptcy, admin AP, stability, war damage, recruitment, plunder/secure, buildings, supply, movement attrition, contested capture, AI admin, depot forward logistics). Session 24 audit: territory viability, plunder multiplier, AI recruitment/building/supply. Session 26 audit (Opus): 10 P0 bugs fixed (auto-advance data, plunder nation, float wrapping, parser collisions), 10 P1 risks resolved, 7 P2 cleanups. **Economy balance to be revisited for 1805 campaign** (Coalition admin AP dilemma, France dominance, building affordability). |
| Reinforcements (Enemy) | AI can recruit troops | Low | **DONE** (AI admin phase, Session 23+24) |
| Manpower Pools | Separate: Infantry, Cavalry, Artillery | Medium | Planned |
| Attrition | Movement/supply decay | Low | **DONE** (Session 22: supply + movement attrition) |
| Fog of War | Hidden enemies, scouting required, watchtower building | Medium | **COMPLETE** (Sessions 32-36, 38). Intel model, visibility engine, scout persistence, battle reveal, intel report, filtered game state (29 call sites), PURSUE/SUPPORT/cautious pathfinding fog-aware, enemy phase filtering, tactical event filtering, watchtower building, contact interrupt discovery messages, Davout PURSUE fog-aware objection, V2b TODO markers. 157 fog-specific tests. **Session 38: Map visualization** — region fog overlay (dim/grey/dark by visibility), fogged enemy silhouettes with "?" + strength bands, fog-aware tooltips. See `FOG_OF_WAR_SPEC.md`, `FOG_IMPLEMENTATION_PLAN.md`. |
| Terrain | Region terrain affects combat/movement | Medium | **6.1.A+B done** (data layer + combat). Movement/pathfinding remaining. |
| Sieges | Fortified cities require siege mechanics | Medium | **Deferred to 1805** — current fort + contested capture (1-2 turn occupation) sufficient for 13-region map. Full sieges (attrition, starvation, sortie, artillery) revisit when 80-100 regions make longer holdouts strategic. |
| City Fortification | "Fortify this city" building action | Low | **DONE** (6.2.E: fortification building, 400g/3t, +25% defense. 6.2.F: contested capture holdout.) |
| Artillery Unit Type | Combat buffs like cavalry | Medium | **DONE** (Session 42: Drouot/PrinceAugust, moved_this_turn lifecycle, cavalry counter +30%, 2x fort degradation, no advance on win, glorious charge ban, artillery manpower pool, 86 tests) |
| Turn Events Log | Track battles/captures/retreats per turn (feeds gazette) | Low | **COMPLETE** (Session 30: 13 event types, world.event_log, 5 helpers, serialized, 39 tests). EL1-EL5 hardening TODOs resolved in Session 31 (1 bug fixed: auto-charge path wasn't logging battle events). |
| Player Garrison | Detach 3k troops to garrison a region | Low | **DONE** (Session 31: garrison command, fort degradation, morale warning, capture hint, occupy alias) |
| Enemy AI Garrison | AI places garrisons via same _execute_garrison (Building Blocks) | Low | **DONE** (P6.75: Building Blocks, 20k threshold, 1/nation/turn, P4.25 sub-5k awareness) |
| **Save/Load** | Full game state persistence + autosave (moved from Pre-EA) | Low | **COMPLETE** (Session 27: save_manager.py, 4 API endpoints, autosave, terminal commands, load dialog, 38 tests) |
| **Berthier Parse Recovery** | Failed parses -> Berthier asks clarification in-character (moved from 8.5) | Low | **COMPLETE** (Session 28: prompt_builder.py, llm_client.py, parser.py, main.py. Mock templates + LLM prompt. Reacts to tone. 20 tests.) |
| **Post-Battle Analysis** | Template breakdown: modifiers, casualties, Berthier observation | Low | **COMPLETE** (Session 29: battle_report.py, snapshots, 15 observation priorities with perspective-aware attacker/defender variants, Godot display, 65 tests) |

### Save/Load Notes

**COMPLETE (Session 27).** `backend/save_manager.py` handles all file I/O. Autosave every turn. Terminal commands "save"/"load". Load dialog popup in Godot. 38 tests. Pause menu (Esc → Save/Load/Settings/Quit) deferred to Phase 6.5 — needed before 1805 EA launch. All phases after this must maintain serialization discipline (already in CLAUDE.md).

### Berthier Parse Recovery

**COMPLETE (Session 28).** Failed commands return in-character Berthier clarification instead of raw errors. Two intercept points: "Unknown action" (before executor) and "Marshal None" (after executor). Mock mode: context-aware templates using real game-state names (3 categories x 2-3 variants). Live mode: one LLM call with Berthier character prompt — reacts to Emperor's tone with flustered dignity. Partial parse info (recognized marshal/target) forwarded for context-aware suggestions. 20 tests.

### Post-Battle Analysis (Berthier's After-Action Report)

**COMPLETE (Session 29).** After every player-visible combat, Berthier delivers a formatted report with:
- **Modifier breakdown:** All attack/defense modifiers with labels and +/- signs (stance, drill, personality, terrain, fortification, etc.)
- **Casualty summary:** Original strength, casualties, remaining for both sides
- **Berthier observation:** One contextual comment from 15 priority categories with perspective-aware attacker/defender variants. Categories: mutual destruction, lost into fortification, lost fort overrun, lost bad stance (attacker/defender), lost terrain disadvantage, lost despite terrain, won heavy casualties, won broke fortification, won fort held, won drilled, lost narrow no drill, lost costly, won decisively, stalemate, default

Uses read-only modifier snapshots taken BEFORE state-consuming `get_attack_modifier()`/`get_defense_modifier()` calls. Perspective-aware: observations always from player's side regardless of who attacks. No LLM needed. Teaches players mechanics through results. All values `int()`-wrapped. 65 tests.

### MAP COMMISSIONING REMINDER

**Commission the Europe map during Phase 6 development.** Art takes 2-4 weeks; should be ready for Phase 6.5 renderer integration.

**Map approach: EU4-style bitmap color map** (NOT SVG).

**Artist brief:**
- 1805 Europe, Portugal to Moscow, Scandinavia to Ottoman Balkans
- EU4 political map style
- ~120-150 province outlines (we wire ~80-100 for EA v1, rest greyed out)
- **Two deliverables:** (1) visual map (pretty, what players see), (2) province color map (each province = unique solid RGB color, same dimensions, pixel-aligned)
- Include coastlines for Britain and North Africa (greyed out, no province borders — off-map powers)
- Each province must be a distinct closed region for hover detection and color fill
- Artist familiar with Paradox modding ideal — this is the standard EU4 approach

**Province count target: ~80-100 wired for EA v1:**

| Area | Regions | Notes |
|------|---------|-------|
| France | 10-12 | Core gameplay area |
| Low Countries | 3-4 | Belgium, Netherlands, Luxembourg |
| German States | 14-18 | Confederation of the Rhine heartland |
| Austria/Habsburg | 8-10 | Vienna to Transylvania |
| Italy | 8-10 | Piedmont to Sicily |
| Iberia | 6-8 | Peninsular War theater |
| Russia (to Moscow) | 8-10 | Warsaw, Lithuania, Smolensk, Moscow, St. Petersburg |
| Scandinavia | 3 | Denmark, Sweden, Norway |
| Ottoman Europe | 6-8 | Constantinople, Greece, Serbia, Balkans |
| Switzerland | 1-2 | |

**Hit detection:** Sample pixel from hidden color map at mouse position -> dictionary lookup -> province ID. O(1), no polygon math.

**Implementation plan:** See `docs/PHASE6_IMPLEMENTATION_PLAN.md` for session-by-session breakdown.

**Dependencies:** None
**Exit Criteria:** Player manages economy, enemies reinforce, terrain matters, can save/load, failed parses feel in-character

---

## Phase 6.5: Information & UI Systems

**Goal:** Player can track 80-100 regions, 30 marshals, 8 nations without drowning.

| Feature | Description | Complexity | Status |
|---------|-------------|------------|--------|
| Notification System | Alerts for key events (invasions, deaths, diplomacy) | Medium | Planned |
| Strategic Ledger | Overview screen: all marshals, armies, nations | Medium | Planned |
| Marshal Management UI | View/manage all marshals, relationships, recruit | Medium | Planned |
| Campaign Log | Scrollable history of major events | Low | Planned. EL1-EL5 prereqs resolved (Session 31). |
| Tooltips | Hover info on regions, marshals, nations | Low | Planned |
| **Campaign Briefing Screen** | Turn-start summary: "France controls 8 regions. Coalition threat: rising. Ney is restless." Template-driven. | Low | Planned |
| **Marshal Report** | Per-turn one-liner per marshal: "Ney: attacked Wellington, lost 8k, trust 72 (stable)." | Low | Planned |
| **Tutorial Infrastructure** | `TutorialManager` for staged popups/highlights. Content populated in Pre-EA. | Medium | Planned |
| **Map Renderer** | EU4-style bitmap map integration (using commissioned art from Phase 6). Includes fog of war visual layer (region tinting/overlays for UNKNOWN/STALE/etc.) | High | Planned |
| **Pause Menu** | Esc → Save/Load/Settings/Quit (wraps Phase 6 save/load endpoints) | Low | **COMPLETE** (Session 56). Smart Esc: unfocus input → open menu → close menu. CanvasLayer 101, modal overlay, Save/Load/Settings stub/Quit. |
| **Wire Marshal Abilities** | Wire all unwired abilities in combat.py: Drouot (fort degradation), Wellington (terrain defense), Blucher (pursuit damage), Uxbridge (pursuit casualties), Gneisenau (ally bonus) | Medium | Planned |

### Map Renderer Notes

Build the Godot map renderer against the commissioned bitmap art:
- `Sprite2D` for visual map layer
- Hidden `Image` for province color map (hit detection)
- Province hover highlighting (shader-based color swap)
- Zoom/pan controls
- Marshal sprites as clickable `Node2D` positioned on provinces
- Dynamic nation coloring on conquest
- Greyed-out unplayable provinces visible but non-interactive

### Option C: Partial Europe Wiring

Wire ~80-100 provinces for EA v1. Remaining provinces from the 120-150 in the art are visible but greyed out. Expand playable area in EA updates. Players see this as a roadmap, not a limitation.

**Dependencies:** Phase 6 (needs data to display), commissioned map art
**Exit Criteria:** Player has clear visibility into game state, map looks professional

---

## Phase 7 Core: Multi-Marshal Coordination

**Goal:** "Position IS Coordination" — automatic positional bonuses make multi-marshal positioning the core strategic skill. Relationships have real mechanical impact and evolve through shared experience.

**Design Principle:** All coordination bonuses are automatic and positional. No new command syntax. Building Blocks principle — enemy AI benefits identically from the same passive bonuses. See `docs/MULTI_MARSHAL_SPEC.md` for full spec + `docs/PHASE7_SPEC_AMENDMENTS.md` for audit corrections.

**Architecture:** Coordination bonuses flow through transient fields on Marshal, read by `get_attack_modifier()` / `get_defense_modifier()` (Golden Rule #1). `combat.py` reads them, never recalculates. AI earns bonuses through co-location duration (not strategic commands it cannot issue).

**Scope Decision (Feb 20, 2026):** Full spec is 10 sessions (57-66, ~340 tests). Phase 7 Core ships 6 sessions. Sessions 62 (casualty distribution), 63 (AI coordination enhancements), 65 (full battle reports), 66 (Godot tooltips/tutorial/audit) deferred to Phase 7b. Rationale: Core delivers all player-facing coordination mechanics + the Grouchy Rule + dynamic relationships. Casualty distribution deferred because (a) it modifies `resolve_battle()` contract (highest-risk change in spec), (b) coordination works without it (allies provide bonuses, primary combatant absorbs casualties), and (c) playtest data should inform the proportional distribution design. AI enhancements deferred because AI already benefits from passive coordination when co-located. Each core session includes basic combat display messages — no separate presentation session needed.

### Phase 7 Core Sessions

| Session | Feature | Description | Complexity | Tests | Status |
|---------|---------|-------------|------------|-------|--------|
| **57** | **Combined arms** | 1/3=0%, 2/3=+10%/+5%, 3/3=+20%/+10%. Unit type diversity, NOT relationship-scaled. Includes basic combat message. | Medium | ~35 | Planned |
| **58** | **Coordination bonus + hard cap** | +3% atk/+5% def per ally, relationship-scaled (Hostile 0%→Devoted 150%). Hard cap: +25% atk/+20% def. Includes per-ally message. | Medium | ~35 | Planned |
| **59** | **Dedicated coordination + co-location** | +5%/+5% flat from 2-turn co-location (both sides) OR SUPPORT order (player, immediate). New serialized fields. Includes status message. | Medium | ~30 | Planned |
| **60** | **Adjacent support bonus** | +2% atk per adjacent friendly marshal. Not relationship-scaled. Includes adjacent count message. | Low | ~20 | Planned |
| **61** | **Adjacent reinforcement** | The Grouchy Rule. Deterministic arrival score. Physical relocation. Inline-dramatic display. **HIGHEST RISK.** | High | ~45 | Planned |
| **64** | **Win/loss relationships** | Shared battle → relationship check. Severity-scaled. 3-turn cooldown. Rivalry Resolved. Relationship change notification. | Medium | ~25 | Planned |

**Key formulas:** Combined arms (type count), Coordination (per-ally × relationship scaling), Arrival score (logistics ×5 + relationship ±20 + terrain ±10 + personality ±5 ± variance, threshold >60/65), Win/loss (severity-scaled, asymmetric: winning together builds faster than losing destroys).

**Note on casualty model:** Without Session 62, combat remains 1v1 between primary attacker/defender. Allied marshals provide coordination bonuses and share retreat fate (Session 61 reinforcement) but do not take proportional casualties. This is a simplification, not a bug. Supply attrition limits stacking. Session 62 in Phase 7b upgrades this to full proportional distribution.

### Phase 7b

Items deferred from Phase 7 Core + items that build on coordination data:

**Deferred from Phase 7 Core (ship first in 7b):**

| Session | Feature | Description | Complexity | Tests | Status |
|---------|---------|-------------|------------|-------|--------|
| **62** | **Casualty distribution** | `resolve_battle(apply_casualties=False)`. Proportional by strength. Hostile = 0%. See amendments C1/C2 for full contract. | High | ~40 | Deferred |
| **63** | **AI enhancements** | P4.6 coordinated attack, P4.75 mod, P4.76 co-location persistence, P4.77 cross-nation, P4.78 defensive positioning. | High | ~35 | Deferred |
| **65** | **Battle reports & Berthier** | 5 coordination observation categories. Pre-battle coordination preview. Full Berthier observations. | Medium | ~25 | Deferred |
| **66** | **Godot UI + integration audit** | Tooltips, tutorial inline-dramatic, display formatting, cross-system audit, doc updates. | Medium | ~50 | Deferred |

**Linked Group — Tactical Triangle Completion (must ship together):**

| Feature | Description | Complexity | Status |
|---------|-------------|------------|--------|
| **Square Formation** | Infantry anti-cavalry stance (-40% cav dmg), vulnerable to artillery (+50%). Completes tactical triangle. | Medium | Deferred |
| **Artillery SUPPORT auto-bombardment** | Artillery on SUPPORT auto-bombards before supported marshal's combat. Pairs with square formation. | Medium | Deferred |
| **Artillery Overwatch** | Passive -3% attack debuff on enemies in same region as friendly artillery. | Low | Deferred |

**Other deferred items:**

| Feature | Description | Complexity | Status |
|---------|-------------|------------|--------|
| **V2b: Defiance/Vindication** | STRONG/EXTREME concerns trigger defiance. See OBJECTION_V2.md. Scaffolding from V2a ready. | Medium | Deferred |
| **Jealousy system** | Marshal getting all glory → others resent. Needs multi-marshal battle data from Phase 7. | Medium | Deferred |
| **Coalition Trigger** | Threat level ticks up → war declarations. Core "France can't steamroll" mechanic. | Medium | Deferred |
| **Cross-nation coordination** | Coalition partners (Britain/Prussia) coordinate. Requires Coalition Trigger or `allied_nations` mapping. See amendments C3. | Medium | Deferred |
| **Gneisenau Staff Work** | +10% ally bonus — Coalition-specific advantage. Deferred to 1805 full campaign. | Low | Deferred (1805) |

### V2b Audit Findings (from V2a audit)

Items scaffolded in V2a that need wiring in V2b:
- **Defensive vindication:** `pending_defensive_vindication` field exists and serializes, but nothing in turn_manager.py reads/writes it.
- **Vindication decay:** Spec says -1 per 3 turns of no objection activity. Not implemented.
- **Idle marshal objection:** Moved to V2a Unit 6 (see V2a section above).
- **Aggressive trigger escalation:** Aggressive personality stance_change to defensive is always MILD. Should escalate to MODERATE/STRONG when weak enemy is adjacent (beatable odds). Mirror `evaluate_cautious` ratio-based scaling pattern but inverted — aggressive gets MORE opposed when fight looks winnable.

### AI Enhancements for Scale (1805)

**AP Scaling:** With 15-20 enemy marshals, 4 AP per nation causes action starvation. AP should reflect national bureaucratic capacity:

| Nation | Base AP | Rationale |
|--------|---------|-----------|
| France | 5 | Corps system, Napoleon's genius |
| Prussia | 4 | Efficient, reformed military |
| Britain | 4 | Competent but parliamentary delays |
| Russia | 3 | Vast but slow |
| Austria | 3 | Bureaucratic, multi-ethnic complexity |
| Minor nations | 2 | Limited administration |

Additional: tiered actions (free basic actions for idle marshals, AP only for offensive), strategic order conflict detection.

### AI Enhancement: Combined Strength Evaluation (IMPLEMENTED)

AI evaluates attack decisions using combined strength of all friendly marshals in the same region. Affects DECISION-MAKING only. Phase 7 coordination system gives these decisions mechanical teeth.

### AI Enhancement: P0 Survival Instinct

If marshal strength < 20% of starting_strength AND enemy in same region -> ALWAYS retreat regardless of personality. Threshold personality-adjusted: Cautious 30%, Normal 20%, Aggressive 15%.

**Dependencies:** Phase 6 (economy, supply attrition, artillery unit type)
**Phase 7 Core Exit Criteria:** Coordination bonuses apply automatically in combat, relationships affect and evolve through coordination quality, Grouchy Rule fires with inline-dramatic narrative, ~190 new tests, basic coordination messages in combat output
**Phase 7b Exit Criteria:** Proportional casualty distribution, AI deliberately seeks coordination, full battle reports with Berthier coordination observations, Godot tooltips with reinforcement probabilities, tactical triangle complete

---

## Phase 8: Diplomacy & Peace

**Goal:** Wars start and end through negotiation. Diplomacy feels like talking to PEOPLE.

| Feature | Description | Complexity | Status |
|---------|-------------|------------|--------|
| Peace Treaties | LLM-powered negotiation | High | Planned |
| Alliances | Form defensive/offensive pacts | Medium | Planned |
| War Declarations | Formal with casus belli | Low | Planned |
| Nation Relations | Values affect diplomacy options | Medium | Planned |
| Tiered Nation AI | France smarter than minor nations | Medium | Planned |
| **Diplomacy Chat** | LLM-powered conversations with nation leaders | High | Planned |
| **Leader Personalities** | Distinct voices (see table below) | Medium | Planned |
| Diplomatic Rules Engine | War score + relations -> accept/reject (deterministic, LLM voices) | Medium | Planned |
| **AI Proposals** | AI offers peace, makes demands — LLM voices the proposal | Medium | Planned |
| **War Score** | Visual progress toward victory/defeat, drives peace treaty acceptance | Low | Planned |
| **Threat Indicator** | Coalition threat level, visible diplomatic pressure buildup | Low | Planned |

**Note:** Coalition TRIGGER moved to Phase 7. This phase handles the diplomatic conversation layer and peace mechanics.

**Note:** War Score and Threat Indicator moved from Phase 6 — both are only meaningful when they drive peace negotiations and diplomatic pressure. Without diplomacy, war score is a cosmetic number and threat indicator has no mechanic to trigger. Building them here avoids premature design that Phase 8 diplomacy would likely need to revise.

### Diplomacy Chat Architecture

Player types natural language proposals. LLM generates leader response in-character. Rules engine resolves outcome deterministically. LLM narrates the result.

```
Player: "I offer Austria peace if they cede Tyrol"
  -> LLM generates Metternich's response (in-character)
  -> Rules engine: war score + relations + territory value -> accept/reject/counter
  -> LLM voices outcome: "Metternich smiles thinly..."
```

**Cost control:**
- 2 LLM calls per exchange (response + outcome narration)
- Last 3-4 exchanges as context only (prevents token creep)
- Max 3 diplomatic exchanges per turn (prevents cost abuse)
- Template fallback if LLM unavailable
- ~$0.0004-0.0008 per exchange (Haiku)

**Leader Personalities (per leader, not per nation):**

| Leader | Nation | Personality | Voice |
|--------|--------|-------------|-------|
| Metternich | Austria | Scheming | Calculating, poison-pill deals, never says what he means |
| Tsar Alexander | Russia | Idealistic | Grand gestures, emotional, unpredictable pivots |
| Frederick William | Prussia | Cautious | Deferential, follows strongest ally, hedges |
| Castlereagh | Britain | Pragmatic | Subsidy offers, cold cost-benefit, funds coalitions |

**Dependencies:** Phase 6 (economy for peace terms), Phase 7 (coalitions for diplomatic context)
**Exit Criteria:** Can negotiate peace, AI diplomacy feels alive, leaders have distinct voices

---

## Phase 8.5: Events, Goals & National Identity

**Goal:** Campaigns have narrative, nations feel distinct, player has objectives beyond "conquer."

| Feature | Description | Complexity | Status |
|---------|-------------|------------|--------|
| **Events System** | Random + historical events with choices | High | Planned |
| **National Goals** | "Unite Germany", "Continental System" | Medium | Planned |
| **National Flavor** | France FEELS different from Austria | Medium | Planned |
| **Light Tech/Reforms** | Simple upgrades: conscription, tactics, administration | Medium | Planned |
| **Campaign Objectives** | Victory conditions beyond territory (prestige, survival) | Medium | Planned |
| Historical Moments | Coronation, Tilsit, Retreat from Moscow | Medium | Planned |
| **Gazette System** | Period newspaper every 3-5 turns, LLM-generated | Medium | Planned |
| **Marshal Voice (Tier 1)** | Template personality responses for all events | Low | Planned |
| **Marshal Voice (Tier 2)** | LLM personality for high-drama moments | Medium | Planned |
| **Music & Sound (Core)** | Battle drums, march, tension, ambient | Medium | Planned |
| **Grouchy Moment LLM** | LLM narrates Grouchy's inner monologue when ignoring cannon fire | Low | Planned |
| **Intercepted Dispatches** | Scout results as captured enemy letters | Low | Planned |
| **Marshal Memory** | Similar situation recurs -> marshal references last time | Low | Planned |
| **Napoleon's Desk** | Turn-start LLM briefing from chief of staff | Low | Planned |
| **Command Echoing** | Combat reports reference player's original phrasing | Low | Planned |
| **Napoleon Comparison** | Post-game: compare your campaign to real Napoleon | Low | Planned |

### Gazette System ("Le Moniteur")

Every 3-5 turns, generate a period newspaper summarizing recent events via single LLM call.

**Content:** Battles, territory changes, marshal heroics, tension/foreshadowing.
**Bias:** Written from French perspective. Post-EA: multiple nation perspectives.
**Trigger:** Every 5 turns by default. Force on: major battle, territory loss, marshal death.
**Cost:** ~$0.0005 per gazette (~$0.005 per 40-turn game)

### Marshal Voice System (Tiered)

**Tier 1 -- Templates (free, always-on):**
- 3-5 personality-specific variants per event type
- File: `backend/ai/marshal_voice.py`

**Tier 2 -- LLM Drama (default for high-stakes moments):**
- Triggers: objections, combat results, cannon fire, forced retreat
- 200-token prompt budget, 1-2 sentences in-character
- Cache by (marshal, event_type, outcome)
- Fallback to Tier 1 if LLM fails
- Cost: ~$0.001-0.003/turn

**Tier 3 -- Full Flavor (opt-in toggle, see Pre-EA):**
- ALL commands get LLM personality response
- ~$0.0004/command extra, warned in UI

### Novel LLM Applications

| Feature | Description | Trigger |
|---------|-------------|---------|
| **Grouchy Moment LLM** | "The marshal frowns. The sound of battle echoes from the west. His orders are clear. He continues east." | Cannon fire interrupt + literal personality |
| **Intercepted Dispatches** | "My dear Castlereagh, I have positioned sixty-eight thousand at Waterloo..." | Scout action result |
| **Marshal Memory** | "The last time you ordered me to attack fortified positions, we lost 12,000 men." | Similar situation recurs |
| **Napoleon's Desk** | "Sire, Davout reports the enemy fortifying Belgium. Ney requests permission to attack." | Turn start |
| **Command Echoing** | Player typed "unleash hell" -> "Ney unleashed hell on Wellington's lines — 12,000 casualties." | Combat report |
| **Autonomy Inner Monologue** | "Ney sees the gap and cannot resist" | Autonomous marshal acts |
| **LLM Objection Arguments** | Objection references real game state | Objection popup (Tier 2) |
| **Napoleon Comparison** | "You lasted 47 turns. Napoleon lasted 120 months. Your coalition formed on turn 12; historically, the Third Coalition formed in 1805." | Post-game screen |

### Encouraging Creative Commands (Anti-Memorization)

| Feature | Description |
|---------|-------------|
| **Flavor Echoing** | Marshal voice echoes player's words. HIGHEST PRIORITY — signals "the game heard me." |
| **Synonym Bonus** | LLM detects creative phrasing, boosts strategic_score |
| **Command Suggestions** | Occasionally offer alternatives: "Instead of 'attack,' try 'storm the heights'" |
| **Repetition Penalty** | Same phrasing 5+ times in a row lowers strategic_score. Subtle, not punishing. |
| **"Napoleon's Wit" Bonus** | LLM scores commands for historical flair |
| **Command Variety Tracker** | Milestone rewards: "Your marshals admire your eloquence" (+authority) |

**Key insight:** Carrot, not stick. "attack wellington" always works perfectly. Creative phrasing earns bonuses.

### Positive Events

| Event | Trigger | Effect |
|-------|---------|--------|
| **Victory celebration** | Decisive victory (>2:1 ratio) | +5 morale nearby |
| **Momentum** | Win 2+ battles same turn | +10 morale army-wide |
| **Rallying speech** | Morale recovers past 60 from below 40 | Trust +3 |
| **Captured supplies** | Conquer high-income region | Gold bonus |
| **Vindication narrative** | Marshal proven right | Trust +8, "Davout was right!" |
| **Rivalry resolved** | Rival marshals fight together | Trust boost for both |

**Dependencies:** Phase 8 (diplomacy for event outcomes)
**Exit Criteria:** Each campaign tells a story, nations play differently, marshals have voice, gazette provides rhythm

---

## STEAM PAGE + LLC

**After Phase 8.5.** Marshal voice, gazette, audio, and EU4-style map all working. This is when the game is trailerworthy.

- Commission trailer showing command typing + objection popup + map
- Set up LLC for business entity
- Steam page with screenshots using commissioned Europe map
- Begin wishlist accumulation — every month without a page is lost wishlists
- Work with Claude Chat on store page copy, descriptions, tags

---

## Phase 9: Advisors (Minimal)

**Goal:** Empire feels run by people. Advisors provide stats + flavor, not action gating.

| Feature | Description | Complexity | Status |
|---------|-------------|------------|--------|
| Advisor Characters | Named characters per domain (Talleyrand, Berthier, Treasurer) | Low | Planned |
| Passive Stat Bonuses | Each advisor has 2-3 stats boosting their domain | Low | Planned |
| Named Voices | Advisors narrate their domain's screens in-character | Medium | Planned |
| Advisor Death/Replacement | Events can remove advisors, replacement has trade-offs | Low | Planned |
| **National Identity** | Austria starts with Metternich (diplomacy god), Prussia with Scharnhorst (military reform) | Low | Planned |

### Advisor Design (Minimal EA Version)

Advisors exist as **named voices on information screens** with **passive stat bonuses**. They don't gate actions, don't have trust, don't refuse orders.

Example: Metternich as Austria's advisor gives Diplomacy +2 (better peace terms, slower coalition formation). If he dies or is dismissed, Austria loses the bonus. Recruiting a replacement is a choice: "The new diplomat is cautious — +1 diplomacy but -1 military spending."

**Post-EA promotion:** Advisors gain action gating, trust relationships, dismissal consequences (the full VISION Layer 1). But for EA, they're personality lenses on information with stat bonuses.

**Dependencies:** Phase 8 (diplomacy for advisor context)
**Exit Criteria:** Advisors feel like people running an empire, stats affect outcomes

---

## Phase 10: Character & People (Minimal)

**Goal:** Marshals feel like people who live, die, and can be replaced. If all marshals die, you lose.

| Feature | Description | Complexity | Status |
|---------|-------------|------------|--------|
| Marshal Death | Casualties in battle (% chance per major defeat) | Medium | Planned |
| Marshal Pool | Historical marshals waiting activation | Low | Planned |
| Recruit Marshals | Activate from pool (costs gold + manpower) | Low | Planned |
| All-Dead Loss | If all marshals die, game over | Low | Planned |

### Evaluate Adding New Personality Type Before 1805

Current: Aggressive, Cautious, Literal. Evaluate whether Loyal or Balanced adds enough contrast to justify new trigger tables, V2 evaluators, and AI behavior.

**Deferred from EA:** LLM-generated marshals (when pool empty), acquired traits system.

**Dependencies:** Phase 6 (economy for recruitment costs)
**Exit Criteria:** Marshals can die, player can recruit replacements, total death = loss

---

## Phase 11: Vassals & Britain

**Goal:** Client states work, France's empire makes geographic sense, Britain threatens from off-map.

| Feature | Description | Complexity | Status |
|---------|-------------|------------|--------|
| **Simplified Vassals** | Conquered nations become vassals with loyalty number | Medium | Planned |
| Vassal Troops | Vassals contribute troops automatically | Low | Planned |
| Vassal Defection | If coalition threat > loyalty, vassal defects | Medium | Planned |
| **Authority -> Loyalty** | Napoleon's authority affects all vassal loyalty (1813 snowball) | Low | Planned |
| **Britain Off-Map** | Britain as funder: subsidy pool, expeditionary forces, can't be attacked | Medium | Planned |
| Continental System | Player action to reduce British income/subsidies | Low | Planned |

### Simplified Vassal System

No autonomy slider, no vassal management UI. Just: "Bavaria is your vassal (loyalty 72). They provide 15,000 troops. If coalition threat exceeds their loyalty, they defect."

Authority drop -> vassals waver -> defect in next coalition -> lose their troops AND territory becomes hostile -> more enemies -> more authority loss. The 1813-1814 death spiral in game mechanics. Inverse: high authority -> loyal vassals -> coalition can't peel them away.

### Britain as Off-Map Power

Britain has a subsidy pool that grows from colonial income. When coalition forms, Britain funds it. Britain can spawn Wellington + troops in coastal regions (Portugal, Netherlands). Player can't attack Britain directly.

To beat Britain: exhaust their willingness to fund coalitions (war score / diplomacy) or make Continental System work (reduce income). Historically accurate for most of the Napoleonic Wars.

**Naval abstraction deferred to Post-EA** (when Britain becomes playable with its own map provinces).

**Dependencies:** Phase 7 (coalition trigger), Phase 8 (diplomacy for vassal creation)
**Exit Criteria:** France has client states, vassals can defect, Britain funds enemies

---

## Pre-EA Polish

**Goal:** Game is shippable, onboardable, monetizable.

| Feature | Description | Complexity | Status |
|---------|-------------|------------|--------|
| Tutorial Content | Populate `TutorialManager` from TUTORIAL_SCRIPT.md | Medium | Planned |
| **LLM Monetization** | BYOK + token tiers + payment | High | CRITICAL |
| **LLM Feature Toggles** | Per-feature model/on-off selection in settings | Low | Planned |
| At-will Autonomy | Grant autonomy anytime (gold-gated, one admin slot) | Low | Planned |
| At-will Administrator | Sideline marshal for +1 AP (gold-gated) | Low | Planned |
| Increase Salary | Gold -> Trust conversion | Low | Planned |
| Modding Polish | Finish tools, docs, examples | Low | Nearly done |
| LLM Efficiency | Caching, optimization | Medium | Planned |
| Settings Menu | Audio, display, controls, LLM settings | Low | Planned |
| Steam Integration | Achievements, cloud saves | Medium | Planned |
| **Music & Sound (Polish)** | Full period orchestral, per-nation themes | Medium | Planned |
| Difficulty Settings | AI bonuses, player handicaps | Low | Planned |
| **Full Flavor Toggle** | Tier 3 marshal voice (opt-in with cost warning) | Low | Planned |
| **LLM Cost Display** | Per-feature token usage in settings | Low | Planned |
| **Voice-to-Text** | Speak orders naturally — feeds into existing parser pipeline | Medium | Planned |
| **Short Waterloo Scenario** | 10-15 turn tutorial scenario, 3 marshals, reuse current 13-region data | Medium | Planned |

### LLM Settings UI

```
LLM Features          Model       Status
---------------------------------------------
Command Parsing       Haiku       [ON]
Marshal Voice         Haiku       [ON]
Gazette              Sonnet       [ON] (recommended)
Diplomacy Chat       Sonnet       [ON] (recommended)
Battle Narration     Haiku        [OFF]
Full Flavor Mode     Haiku        [OFF]

Estimated cost/game: ~$0.05
```

Power users tune per-feature, casual players use defaults.

### Voice-to-Text

Killer feature for the "talk to your marshals" fantasy. Player speaks commands, speech-to-text converts to text, text feeds into existing parser pipeline unchanged. The parser already handles natural language — voice is just a new input method.

**Architecture:** Godot `AudioStreamPlayer` captures mic -> send audio to Whisper API (or browser Speech-to-Text API) -> insert transcribed text into command input -> submit through normal parser. Backend is unaware of voice vs typed input.

**Cost:** Whisper API ~$0.006/minute. Average command ~3-5 seconds = ~$0.0003/command. 40 commands/game = ~$0.012/game. Negligible. Alternatively, browser-native `SpeechRecognition` API is free but less accurate.

**Fallback:** Always show text input. Voice is additive, never required. Toggle in settings.

**Dependencies:** All phases complete

**Exit Criteria:** New players learn, payments work, game feels alive

---

## 1805 Campaign Launch (Early Access)

**Goal:** Option C — commission full Europe map, wire partial regions, expand over EA updates.

| Feature | Description | Complexity | Notes |
|---------|-------------|------------|-------|
| **~80-100 Wired Regions** | Western/Central Europe playable | Medium | Data entry + balance |
| **EU4-Style Bitmap Map** | Province color map, visual overlay | Integrated in 6.5 | Commissioned art |
| Map Interaction | Click provinces, zoom, pan | Integrated in 6.5 | |
| 6-8 Nations | France, Austria, Russia, Prussia, (Britain off-map), Spain, Bavaria, Ottoman | HIGH | Data + balance |
| 20+ Marshals | Historical personalities per nation | Medium | Data entry |
| Year-Based Turns | Monthly 1805-1815 | Low | |
| 1805 Win Conditions | Per-nation victory conditions | Medium | |
| **Greyed-Out Expansion** | Remaining 40-70 provinces visible but non-interactive | Low | Visual promise |
| **AI Fog of War** | AI gets fog (softer than player's) at 80+ regions | Medium | Omniscient AI unfair at scale. Toggle point: `get_visible_enemies_near()` |

### Economy Rebalance for 1805

The 13-region tutorial map has known balance tensions surfaced by Session 26 Opus audit:
- **Admin AP bonus (150g) is disproportionately important** — 9-43% of a nation's income. Creates strong disincentive for Coalition AI to recruit/build.
- **Coalition death spiral** — battle losses → recruitment needs → lost admin bonus → deficit → bankruptcy → desertion → more losses.
- **France cannot go bankrupt** under normal play (+85 to +235/turn). Bankruptcy is Coalition-only.
- **Buildings expensive for Coalition** — a 350g market is 44% of Prussia's starting gold.

These are acceptable for the tutorial scenario (France should feel dominant). For 1805 with 6-8 nations and 80+ regions:
- Income sources will be more numerous and distributed
- Admin AP bonus should scale differently (flat 150g matters less with 2000g income)
- Building costs may need scaling by era or nation
- Coalition subsidy mechanic from off-map Britain may be needed
- Upkeep rate (5g/1000 troops) should be re-evaluated against 1805 army sizes

### AI Fog of War for 1805

At 13 regions, AI omniscience is fine — too few regions for fog to matter strategically. At 80+ regions, omniscient AI feels unfair (it always knows where you are, you never know where it is). Options to evaluate:
- AI gets fog but with bonuses (wider adjacency range, faster intel updates)
- AI fog is "softer" — PARTIAL everywhere instead of UNKNOWN
- AI uses watchtowers and scouts like the player but with priority logic already built

The `get_visible_enemies_near()` helper added in Session 36 is the toggle point — currently returns actual data, switch to fog-filtered for AI fog. The 12 objection helper TODO markers (V2b) also apply here since AI nations' marshals would need fog-aware objection triggers.

### AP Scaling for 1805

Nation AP reflects bureaucratic capacity (see Phase 7 table). Additional: free basic actions for idle marshals (stance, wait), AP only for offensive actions. Strategic order conflict detection required.

### Option C Expansion Plan

EA v1: Western + Central Europe (~80 regions). EA updates add Eastern Europe, expand Russia, Ottoman interior. Each update = wire more provinces from existing art + add region data. No new art commissions needed.

**Dependencies:** All phases + Pre-EA complete, commissioned map art
**Exit Criteria:** Partial 1805 campaign playable, map looks professional

---

## Post-EA Expansion

| Feature | Priority | Notes |
|---------|----------|-------|
| **Full Europe (120+ regions)** | HIGH | Wire remaining provinces from existing art |
| Multi-Nation Play | HIGH | Play as Austria, Russia, etc. |
| Coalition Player | HIGH | Lead coalition against France |
| Additional Start Dates | HIGH | 1809, 1812, 1815 scenarios |
| **Naval Abstraction** | HIGH | Required when Britain becomes playable |
| **Britain Playable** | HIGH | Own provinces, naval mechanics, subsidy system |
| **Communication / Courier Delay** | MEDIUM | Distance-based turn lag, Napoleon's HQ location matters, player-only (Option A) |
| **Full Advisor System** | MEDIUM | Action gating, trust, dismissal (VISION Layer 1) |
| **North Africa / Egypt** | MEDIUM | Expansion map art, Egyptian campaign scenario |
| Weather System | MEDIUM | Russian winter, mud season |
| Advanced AI | MEDIUM | Flanking coordination, capital defense |
| Campaign Editor | MEDIUM | Player-made scenarios |
| Steam Workshop | MEDIUM | Mod sharing |
| **Multi-Nation Battle Reports** | LOW | Thread player_nation from world state through combat resolver. Currently hardcoded to France. Tests document exact wiring point. |
| Accessibility | MEDIUM | Colorblind, fonts, keybinding |
| Mobile Port | LOW | Touch UI |
| Multiplayer | LOW | Co-op? Competitive? |

### Courier Delay (Post-EA Design)

Lighter version of communication cutoff: orders to distant marshals take effect 1 turn later. Within 3 regions of Napoleon: instant. 4-6 regions: 1 turn delay. 7+: 2 turns. Makes Napoleon's physical location matter. Player-only for EA; when other nations become playable, each gets own HQ anchor.

---

## Critical Path to EA

1. COMPLETE: Strategic Commands, Enemy AI, Serialization/Modding
2. COMPLETE: V2a Objection System Refactor (all 7 units)
3. Post-V2a: TUTORIAL_SCRIPT.md, doc updates
4. **Commission Europe map art** (2-4 week lead time, parallel with Phase 6)
5. Phase 6: Economy, Manpower, Terrain, Fog, **Save/Load**, **Berthier**, **Post-battle analysis**
6. Phase 6.5: Notifications, Ledger, Marshal UI, **Campaign Briefing**, **Marshal Report**, **Tutorial infra**, **Map Renderer**
7. Phase 7 Core: Multi-Marshal Coordination (Sessions 57-61 + 64, 6 sessions, ~190 tests) — combined arms, coordination bonuses, Grouchy Rule, dynamic relationships
7b. Phase 7b: Casualty Distribution (S62), AI Coordination (S63), Battle Reports (S65), Godot UI (S66), Tactical Triangle, V2b, Coalition Trigger
8. Phase 8: **Diplomacy Chat**, Peace Treaties, Leader Personalities
9. Phase 8.5: **Events, Gazette, Marshal Voice, Grouchy LLM, Intercepted Dispatches, Creative Commands, Napoleon Comparison**
10. **STEAM PAGE + LLC** (marshal voice, gazette, audio, EU4 map all working)
11. Phase 9: Advisors (minimal: stats + flavor + named voices)
12. Phase 10: Marshal death/recruitment (minimal)
13. Phase 11: Vassals (loyalty + authority), Britain (off-map funder)
14. Pre-EA: Tutorial content, LLM monetization, **LLM feature toggles**, **Voice-to-Text**, **Waterloo scenario**, Steam integration
15. Wire ~80-100 regions from commissioned map, data entry, balance
16. **TBD 2026: Early Access**

---

## Phase Dependencies Graph

```
                    Commission Map Art (parallel)
                           |
Phase 6 (Economy/Terrain/Save) --+--> Phase 6.5 (UI/Info/Map Renderer)
                                 |          |
                                 |          +--> Phase 7 Core --> Phase 7b (Casualties + AI + Triangle + V2b)
                                 |                    |
                                 |                    +--> Phase 8 (Diplomacy/Peace)
                                 |                              |
                                 |                              +--> Phase 8.5 (Events/Voice/Gazette)
                                 |                                        |
                                 |                                  STEAM PAGE + LLC
                                 |                                        |
                                 +--> Phase 10 (Characters) ----+         |
                                                                |         v
Phase 8 (Diplomacy) --> Phase 11 (Vassals/Britain) ----+  Phase 9 (Advisors)
                                                       |         |
                                                       v         v
                                                  Pre-EA Polish
                                                       |
                                                  Wire Regions + Balance
                                                       |
                                                  EA Launch
```

---

## LLM Cost Budget (Per 40-Turn Game)

| System | Phase | Calls | Model | Cost | Toggleable |
|--------|-------|-------|-------|------|------------|
| Command parsing | 4 (existing) | ~40 LLM + ~360 free | Haiku | ~$0.016 | ON by default |
| Berthier parse recovery | 6 | ~5 failures | Haiku | ~$0.002 | ON by default |
| Marshal Voice Tier 2 | 8.5 | ~30-50 drama events | Haiku | ~$0.012-0.020 | ON by default |
| Gazette | 8.5 | ~8 gazettes | Sonnet (rec.) | ~$0.008 | ON by default |
| Diplomacy Chat | 8 | ~40-60 exchanges | Sonnet (rec.) | ~$0.016-0.024 | ON by default |
| Grouchy Moment / Dispatches | 8.5 | ~5-10 events | Haiku | ~$0.002-0.004 | ON by default |
| Napoleon's Desk briefing | 8.5 | ~40 turns | Haiku | ~$0.016 | OFF by default |
| **Total per game (defaults)** | | | | **~$0.07-0.09** | |
| Full Flavor Tier 3 (opt-in) | Pre-EA | +160 routine calls | Haiku | +$0.064 | OFF by default |

At 1000 games/month = ~$70-90. BYOK covers heavy users. All systems degrade gracefully to templates when LLM unavailable. Per-feature toggle in settings lets players control cost vs immersion.

---

## Document References

- **STATUS.md** -- Current test count, active work, blockers
- **SYSTEMS_REFERENCE.md** -- Game systems reference
- **ENEMY_AI_REFERENCE.md** -- Enemy AI decision tree
- **OBJECTION_V2.md** -- V2 objection system design
- **VISION.md** -- Core concept, north star
- **TUTORIAL_SCRIPT.md** -- Living tutorial content document (updated each phase)
- **FUTURE_DESIGN.md** -- Deferred concepts, post-EA designs

**Rule:** Phase numbers and timeline ONLY exist in this document. Other docs say "see ROADMAP.md".
