# Ink & Iron: Current Status

> **Updated every session by Claude Code.**
> **Last Updated:** March 7, 2026 (Comprehensive Creative Audit COMPLETE — Phase 5 Design Depth approved, 41 new items)

---

## Quick Stats

| Metric | Value |
|--------|-------|
| **Tests Passing** | **5648** (5648 passed, 3 skipped — verified Phase 4 Commands/QoL/Popups) |

| **Current Phase** | Phase 8: Diplomacy. **ALL SESSIONS COMPLETE** (1A through 8D). Phase 8 DONE. See `docs/SESSION_8_PLAN.md`. |
| **Blockers** | Jealousy NEEDS DESIGN GATE (separate track). No blockers for Phase 8. |
| **Code Coverage** | ~71% (backend/) |

---

## Next Steps

1. **Phase 8: Diplomacy** — **Session 7 COMPLETE.** Unified 8-session plan:
   - ~~Session 1A: Map Expansion (13→19 regions)~~ — **DONE** (19 regions, 5 nations, all adjacencies verified, FORMAT_VERSION 2)
   - ~~Session 1B: Nations + Marshals + Economy~~ — **DONE** (Austria/Saxony activated, PrinceAugust removed, 4 new marshals, diplomatic_states/nation_relations data, British naval income, is_at_war() gating on all enemy AI paths, 56 new gate tests)
   - ~~Session 2: Diplomatic States + Acceptance Formula + Diplomat class~~ — **DONE** (5 diplomats, acceptance formula with 7 components + military supremacy/battlefield diplomacy, DP economy, war score with 4 components, trade income matching §1d, movement restrictions, war declaration + DEFENSIVE_ALLIANCE cascade, 111 new tests)
   - ~~Session 3: Talleyrand Commands + Conversational Dialogue Foundation~~ — **DONE** (diplomatic_dialogue.py, diplomatic_templates.py, llm_client/parser/executor/world_state/main routing, 7 new world_state fields, 76 new tests)
   - ~~Session 4: AI Proposals + Counter-Offers + Advisory + Proactive Suggestions~~ — **DONE** (ai_diplomacy.py, diplomatic_advisory.py, P1-P7 trigger table, M3 counter-offer algorithm, Talleyrand's Report in dispatch, templates T11-T20, 43 new tests)
   - ~~Session 5: Vassal System + Loyalty~~ — **DONE** (vassal.py core engine, loyalty ticks with 7 modifiers, rebellion+cascade, tribute, investment, autonomy levels, marshal assimilation, AP/turn clause, Continental System, enemy vassal courting, dispatch warnings, 51 new tests)
   - ~~Session 6: Talleyrand Defiance + Diplomatic Objections~~ — **DONE** (diplomatic_defiance.py, defiance probability curve, 5 sabotage types, discovery+confrontation, redemption event, pre-proposal objections, enemy diplomat voices T21-T27, dispatch integration, 76 new tests)
   - ~~Session 7: Coalition System~~ — **DONE** (coalition.py engine, threat accumulation/decay, coalition formation/brewing/instant, leader selection+posture, coalition AI friction+convergence, war exhaustion, British subsidy, loyalty penalty+wedge, dissolution+cooldown, dispatch integration, T28-T34 templates, 80 new tests)
   - ~~Session 8A: Backend Ledger Builder + Debug Arsenal~~ — **DONE** (diplomatic_ledger.py with 4 tabs fog-filtered, GET /diplomatic_ledger endpoint, 7 top-bar fields, 3 popup pass-throughs with clear-after-read, 10 cheat commands with mock parser, calculate_war_score components extension, 8 debug endpoints, get_diplomatic_ledger() in api_client.gd, 82 new tests)
   - ~~Session 8B: Diplomatic Ledger Godot UI + Top Bar~~ — **DONE** (diplomatic_ledger.gd/.tscn 4-tab screen, D key for diplomatic ledger, R key for dispatch re-read, top bar DP/threat/Talleyrand/envoy fields with pulse + click, diplomatic fields in /command response, 30 new tests)
   - ~~Session 8C: Popups + Notifications~~ — **DONE** (11 new notification constants, 18 notification fire points wired across coalition/diplomacy/vassal/ai_diplomacy/defiance/dispatch, 6 popup data contracts with clear-after-read, 3 new world_state popup fields serialized, 6 Godot popup scenes with BBCode+signals, priority queue in main.gd, 31 new tests)
   - ~~Session 8D: Dispatch Integration + Polish~~ — **DONE** (20 diplomatic dispatch event types with fog-filtered visibility, queue_dispatch_event helper, campaign log 6 diplomacy event types with one-liner formatters, AI-AI diplomatic phase with 4 triggers + max 2 treaties/turn, special acceptance bonuses for 4 nations, 4 scenario test fixtures, Godot dispatch_view.gd diplomatic section + campaign_log.gd diplomacy category, 57 new tests)
2. **Diplomacy Audit** — **COMPLETE.** 20 bugs fixed, 145 audit tests. See `docs/DIPLOMACY_AUDIT.md`.
3. **Diplomacy Creative Audit** — **COMPLETE.** 5-agent deep analysis: balance, historical accuracy, fun, AI behavior, edge cases. Overall score 7.8/10. 8 critical/high bugs found, 10 balance issues, 18 design gaps, 6 AI behavior issues, 7 edge cases. 3 easy fixes applied (treaty cancel/downgrade commands, AI-AI ledger visibility). See `docs/DIPLOMACY_CREATIVE_AUDIT.md`.
4. **Diplomacy Refinement & Cleanup** — **155 items total.** Phases 1-4 COMPLETE (55 items done, 326 tests). Phase 5 APPROVED. See `docs/DIPLO_REFINEMENT.md`.
   - ~~**Phase 1: Critical Wiring**~~ — **DONE** (16 fixes, 37 tests).
   - ~~**Phase 2A: State Cleanup — Diplomacy Core**~~ — **DONE** (17 fixes, 69 tests).
   - ~~**Phase 2B: State Cleanup — Vassal, AI-AI, War**~~ — **DONE** (22 fixes, 50 tests).
   - ~~**Phase 2B+ Confidence Fixes**~~ — **DONE** (5 fixes, 26 tests).
   - ~~**Phase 3: Balance Tuning**~~ — **DONE** (13 items, 44 tests).
   - ~~**Phase 4: Commands, QoL, Popup Architecture**~~ — **DONE** (27 items, 100 tests).
   - **Phase 5: Design Depth** — **NEXT STEP.** 41 items from comprehensive creative audit (6.5/10 overall, March 7 2026). Design-first prioritization:
     - **5A: Core Design Features** (8 items) — Marriage alliances, personality-driven AI proposals, aggressive dominance trigger (P8), advisory actionability, acceptance preview enhanced, nations remember betrayal, diplomatic help text, peace conferences.
     - **5B: AI Intelligence** (6 items) — P2 stalemate fix, coalition posture → enemy AI, economic strategy AI (subsidy/pressure), diplomatic isolation AI, counter-offer personality, urgent re-proposal.
     - **5C: Narrative & Presentation** (11 items) — Talleyrand voice bank (5-8 variants/situation), nation-specific intelligence, sabotage consequence feedback, override feedback, treaty ceremonies, confidence levels, cooldown pre-check, vassal loyalty transparency, "point of no return" at threat 40, vassal personality events, Continental System buff.
     - **5D: Bug Fixes & Balance** (7 items) — DEBUG_MODE security, garrison loyalty cap, DP accumulation, parser ambiguity, counter-offer DP cost, AI DP cap, relation cap in acceptance.
     - **5E: Promoted Deferred** (9 items) — Secret treaties, puppet rulers, player counter terms, personal summits, ledger enhancements (R17d-f), vindication decay, literal triggers.
   - **After Phase 5: UI Test Plan** — Manual playtest in Godot. DP display investigation (R39). Verify all fixes.
5. **Comprehensive Creative Audit** — **COMPLETE.** 6-agent deep audit scored diplomacy 6.5/10. Key findings: war score decay bug (FIXED in Phase 2A), counter-offer broken (FIXED in Phase 1), Talleyrand voice monotone, AI proposals lack personality, diplomacy strategically optional vs military conquest, coalition posture not read by AI. All findings converted to Phase 5 items. See audit results in this session's history.
6. **Jealousy system** — NEEDS DESIGN GATE (separate track). See CLAUDE.md.
7. **Phase 6.5 remaining** — Map Renderer only (art-blocked). Tooltips absorbed into Map Renderer. Tutorial deferred to Pre-EA.

---

## Phase 6 Summary

All major Phase 6 features shipped:

- **Terrain (6.1):** 6 terrain types, weighted pathfinding, cavalry terrain scaling, charge blocking
- **Economy (6.2):** Region types, income/upkeep, stability, war damage, recruitment rework, buildings (4 types), supply limits, movement attrition, contested capture, AI admin phase — audited and balanced
- **Save/Load:** Manual save/load + autosave
- **Berthier Parse Recovery:** In-character error messages for unparseable commands
- **Battle Reports:** Template-based post-battle analysis with modifier snapshots, perspective-aware observations
- **Turn Events Log:** 13 event types, structured logging, hardened (EL1-EL5)
- **Fog of War:** Intel data model, visibility tiers, decay, watchtower building, strategic fog filtering, scout persistence, map visualization with fog overlay + fogged icons
- **Reinforcements, Attrition, City Fortification**
- **Player Garrison Command:** 2 AP, cap 3/nation, map overlay
- **Enemy AI Garrison (P6.75):** Building Blocks, 20k threshold, 1/nation/turn, P4.25 sub-5k awareness
- **Manpower Pools:** Nation-level infantry/cavalry/artillery reserves gate recruitment. Stables building. AI pool/cost awareness.
- **Artillery Unit Type:** Third marshal type (Drouot). Can't attack after moving, no advance on win, cavalry counter, 2x fort degradation. Bombardment system with terrain modifiers, collateral damage, AI bombardment. 127+ tests.

---

## Infrastructure Sessions

### Mar 7 — Comprehensive Creative Audit: Phase 5 Design Depth Approved

6-agent deep creative audit of entire diplomacy system. Scored 6.5/10 overall. Audited: core mechanics (diplomacy.py), AI behavior (ai_diplomacy.py), coalition & vassal (coalition.py, vassal.py), dialogue & templates (all dialogue/template/advisory/defiance files), command parsing (parser/executor/main), system coherence (specs vs implementation).

**Key findings:**
- Talleyrand voice is monotone (template fatigue after 5 conversations)
- AI proposals lack personality (Schemer = Hawk = Dove in behavior)
- Diplomacy strategically optional (military conquest always faster)
- Coalition defensive posture calculated but never read by enemy AI
- No aggressive dominance AI trigger (AI never demands harsh terms when winning)
- Marriage alliances entirely missing (major Napoleonic mechanic)
- Garrison trivializes vassal loyalty (15k troops = loyalty solved forever)
- DP use-it-or-lose-it discourages saving for big moves
- Continental System still a trap choice even after R18

**Result:** 41 new items (R115-R140 + promoted deferred). All added to Phase 5 in DIPLO_REFINEMENT.md. Design-first prioritization: 5A core features → 5B AI intelligence → 5C narrative → 5D fixes → 5E promoted deferred.

### Mar 6 — Phase 2A Diplomacy Core Cleanup: 17 Fixes Implemented

17 bug fixes across 5 batches. 69 new tests (`test_phase2a_batch1-5.py`). 5396 total tests passing. 2 new serialized fields.

**Fixes implemented:**
- R54: Canonical `get_war_score_for()` helper — single source of truth, replaces 5 inline implementations
- R7: `defensive_alliance: 25` added to BASE_DISPOSITION
- R56: Self-relation guard in `modify_nation_relation()`
- R44: `nation_dp` field — AI nation DP stored and serialized
- R67: `copy.deepcopy()` for coalition serialization (prevents shared-reference corruption)
- R1a: Battle records >10 turns old pruned in `apply_war_score_decay()`
- R1b/R49/R47: `cleanup_war_end()` helper — clears battle_records, decisive_battles, war_scores, war_exhaustion, cancels PURSUE orders
- R45: `active_treaties` removed on `execute_downgrade()`
- R5a: Armistice expiration implemented (5 turns → PEACE or WAR based on relations)
- R5b: Armistice cooldowns set on entry, block AI proposals
- R3: Gold floor in treaty clauses (never negative, dispatch event on inability to pay)
- R80: Auto-downgrade fires dispatch event + notification
- R82: `{rejection_reaction}` template slot resolved (cold fury / displeasure / composure)
- R83: Coalition dispatch templates + `queue_dispatch_event()` in form/dissolve/brewing
- R51: Pending dialogue voided when target joins coalition
- R50: Continental System membership cleared on vassal release
- R48: Vassal diplomacy reconciled on vassalization (auto-armistice/peace with conflicting states)
- R57: Threat level wired in diplomatic dialogue context (was hardcoded 0)
- R53: Sweetener value floor (min 5) in `_try_add_desired_clauses()`

**Files modified:** diplomacy.py, world_state.py, ai_diplomacy.py, diplomatic_advisory.py, vassal.py, coalition.py, dispatch.py, diplomatic_templates.py, diplomatic_dialogue.py, notifications.py

### Mar 5 — Phase 1 Critical Wiring: 16 Fixes Implemented

16 bug fixes across 7 batches. 37 new tests (`test_phase1_critical_wiring.py`). 5327 total tests passing.

**Fixes implemented:**
- R40: Coalition loyalty penalty formula inverted (`min` → `max`, WE subtracts)
- R96: VASSAL added to OPEN_MOVEMENT_STATES (lord traversal fixed)
- R109: defensive_alliance type no longer overwritten to "alliance"
- R66: Dispatch fog rule reads correct `target` key (was `target_nation`)
- R61: original_nation serialized on Marshal (to_dict/from_dict)
- R62: Rebellion clears original_nation and resets Trust
- R63: break_treaty() now adds coalition threat (+25 alliance, +15 other)
- R64: Continental System called from turn loop (duplicate in vassal.py removed)
- R65: Advisory uses fog-filtered strength (unknown/stale/partial/full tiers)
- R43: AI-AI per-pair proposal cooldown (5 turns after ratification)
- R37/R41: Sabotage confrontation & redemption dialogue handlers wired
- R42: Pre-proposal objection send_override/send_suggested handlers with terms preservation
- R55: "continue" keyword added to dialogue guard
- R74/R75: Vassal rebellion imminent sets pending_diplomatic_dialogue with invest/garrison/accept
- R2: Counter-offer system activated (COUNTER_OFFER generates terms, accept/reject handlers)

**Files modified:** coalition.py, diplomacy.py, ai_diplomacy.py, dispatch.py, marshal.py, vassal.py, diplomatic_advisory.py, diplomatic_dialogue.py, executor.py, world_state.py, main.py

### Mar 5 — Deep Audit II: 54 New Refinement Findings

6-agent deep code audit targeting wiring gaps, state cleanup, cross-system interactions, and popup architecture. 1 file modified (DIPLO_REFINEMENT.md, +755 lines).

**54 new findings (R61-R114):** 9 HIGH severity, 27 MEDIUM, 18 LOW. Phase 2 split into 2A (diplomacy core, 19 fixes) and 2B (vassal/AI-AI/war, 23 fixes).

**6 systemic trends identified:**
1. Vassal system most under-wired (11 findings) — rebellion cleanup, coalition membership, Continental System
2. Popup early-return cascade (9 findings) — Godot `_on_command_result()` returns early on popup, drops all other data
3. Continental System entirely dead — code exists but never called from turn loop
4. State cleanup on war/peace transitions incomplete — treaties, battle records, stalemate counters persist
5. AI-AI plays by different rules — bypasses `validate_transition()`, skips `active_treaties`, no armistice
6. Fog of war has 2 leak points — advisory exact strength, dispatch wrong key

**Most impactful findings:**
- R61: `original_nation` not serialized (save/load data loss)
- R96: VASSAL not in OPEN_MOVEMENT_STATES (lord can't traverse vassal territory)
- R97: `declare_war` doesn't clean `active_treaties` (treaty clauses execute during war)
- R109: `defensive_alliance` overwritten to `"alliance"` (entire tier unreachable)
- R64: Continental System never called from turn loop
- R65: Advisory leaks exact enemy strength through fog

**Updated refinement plan:** 114 total items. 7-row phase table. All items design-gate approved.

### Mar 4 — Diplomacy Creative Audit + Refinement Doc

5-agent parallel deep analysis of diplomacy system design quality. Scored 7.8/10 overall. Created `docs/DIPLOMACY_CREATIVE_AUDIT.md` (full findings) and `docs/DIPLO_REFINEMENT.md` (36 ranked items with fix proposals, including new feature suggestions like marriages, ultimatums, secret treaties). 5 files modified, 106 lines added.

**Findings:** 8 critical/high bugs (war score decay no-op, battle records persist across wars, counter-offer stubbed as reject, treaty gold unenforced, armistice unimplemented), 10 balance issues (COURT_NATION speed, no relation decay, trade income snowball, coalition stalemate), 18 design gaps (missing commands, ledger info gaps), 6 AI issues, 7 edge cases.

**Easy Fixes Applied (3):**
- **GAP-3:** Wired `break_treaty()` command — keywords: "break/cancel/renounce/end treaty". 1 DP cost.
- **GAP-5:** Wired `execute_downgrade()` command — keywords: "downgrade/reduce commitment/step down". 1 DP cost.
- **GAP-6:** Added AI-AI diplomatic states to ledger nations tab, fog-filtered (PARTIAL+ intel).

**5290 tests passing** (0 regressions).

### Mar 4 — Diplomacy Audit Part 3 (AI Proposal Spam Fixes)

Playtest-discovered bug: AI nations (especially Saxony) repeatedly offering the same deals. 2 files modified, 1 new test file, 19 new tests.

**Bugs Fixed (3):**
- **MEDIUM (SPAM-1):** No acceptance cooldown — after accepting a proposal, the same nation could propose again next turn. Now applies a 2-turn nation cooldown on acceptance (vs 3 turns on rejection).
- **MEDIUM (SPAM-2):** No pending-proposal deduplication — `process_diplomatic_phase` didn't check if a nation already had a proposal in the active dialogue or queue. Added `_has_pending_proposal_from()` guard.
- **LOW (SPAM-3):** P7 opportunistic trigger proposed NON_AGGRESSION regardless of current diplomatic state — could fire even at ALLIANCE. Now only fires when current state is PEACE or OPEN_BORDERS.

**19 new tests** in `tests/test_audit_part3.py`: 5 acceptance cooldown (constant, blocking, expiry, executor wiring), 6 deduplication (dialogue, queue, empty, blocking, allow-other-nation), 5 P7 state validation (peace, open_borders, non_aggression, alliance, defensive_alliance), 3 integration (accept-then-no-followup, accept-chain-with-cooldowns, alliance-cap).

**5263 tests passing** (5244 + 19 new, 3 skipped, 0 regressions).

### Mar 4 — Diplomacy Audit Part 2 (Sections 7-15)

Comprehensive audit of remaining Phase 8 diplomacy sections. 2 files modified, 1 new test file, 57 new tests.

**Bugs Fixed (3):**
- **MEDIUM (AA-5):** AI-AI alliance conflict check missing. AI nations could form alliances even when one was at war with the other's ally (violating §5b.3). Fixed: added alliance conflict check in `_ratify_ai_ai_treaty()`.
- **LOW (AL-2a):** `cheat set_war_exhaustion` clamped to 100 instead of WAR_EXHAUSTION_MAX (200). Fixed: updated clamp to 200.
- **LOW (AL-2b):** `cheat set_vassal_loyalty` had no bounds checking — could set negative or >100. Fixed: added `max(0, min(100, ...))` clamp.

**Verified Clean (93 items across 9 sections):**
- Section 7 (Coalition): 33/33 PASS — threat accumulation, decay, formation, warfare, dissolution all correct
- Section 8 (Vassal): 17/17 PASS — creation, loyalty drift, rebellion all correct. 3 checklist spec errors corrected (garrison=+8 not +15, shared enemy=+2 not +10, popup at <=10 not <15)
- Section 9 (AI Proposals): 14/15 PASS — P1-P7 triggers, M3 counter-offer, AI-AI diplomacy correct
- Section 10 (Ledger): 8/8 PASS — 4 tabs, fog filtering, data accuracy
- Section 11 (Dispatch): 6/6 PASS — 21 event types, fog filtering, Talleyrand's Report, vassal warnings
- Section 12 (Serialization): 12/12 PASS — all 42 diplomatic fields roundtrip, popup/dialogue/coalition/vassal/mission
- Section 13 (Cross-System): 17/17 PASS — combat/movement/economy/enemy AI × diplomacy
- Section 14 (Notifications): 10/10 PASS — all 19 diplomatic notification types verified
- Section 15 (Debug): 5/6 PASS — 11 cheat commands, 8 debug endpoints

**Design Notes:**
- AH-4: No marshal auto-ejection on diplomatic state downgrade (known limitation)

**57 new tests** in `tests/test_audit_part2.py`: 4 threat accumulation, 2 threat decay, 8 formation thresholds, 3 coalition warfare, 2 dissolution, 7 vassal creation, 2 loyalty drift, 2 rebellion, 5 alliance conflict fix, 2 AI-AI diplomacy, 4 ledger tabs, 7 serialization roundtrip, 1 DP economy, 3 movement, 1 notifications, 5 cheat bug fixes, 1 cheat parsing.

**5244 tests passing** (5187 + 57 new, 3 skipped, 0 regressions).

### Mar 4 — Diplomacy Audit Part 1 (Sections 1-6)

Comprehensive audit of Phase 8 diplomacy. 4 files modified, 1 new test file, 42 new tests.

**Bugs Fixed (7):**
- **CRITICAL (A-1):** Enemy phase hidden when incoming_proposal popup returns early in Godot. Fixed: main.py defers all popups when `enemy_phase` present.
- **CRITICAL (A-2):** Diplomatic early return skipped popup pass-throughs. Fixed: early return now calls `_include_popup_passthroughs()`.
- **CRITICAL (A-3):** No safety valve for cleared popup with pending dialogue. Fixed: re-derives `incoming_proposal` from `pending_diplomatic_dialogue`.
- **CRITICAL (A-4):** Inconsistent popup pass-through handling. Fixed: new `_include_popup_passthroughs()` helper handles all 6 popups consistently.
- **CRITICAL (B-3):** Godot popup callbacks send to `/command` but executor guard blocks ALL commands when dialogue pending. Fixed: main.py routes dialogue keywords to `handle_diplomatic_dialogue_response()` before executor.
- **Safety Valve (C-1/C-2):** No way to clear stale blocking dialogue. Fixed: auto-clear in `advance_turn()` after 2 turns + `cheat clear_dialogue` command.
- **Missing State (L-4):** VASSAL missing from `post_break_map` in diplomacy.py. Fixed: added `"VASSAL": "NON_AGGRESSION"`.

**Verified Clean (Sections 3-4):** Turn flow integration all PASS. Acceptance formula all PASS. War score all PASS.

**Design Notes (not bugs, for future consideration):**
- J-5: Armistice expiration is a placeholder (no-op)
- K-5/K-6: No alliance conflict check in war declaration
- L-3: Treaty break cooldown not implemented (spec says 5 turns)
- O-5: Redemption during active mission not explicitly handled

**42 new tests** in `tests/test_audit_part1.py`: 8 popup flow, 7 blocking lifecycle, 3 acceptance formula, 10 state transitions, 8 Talleyrand defiance, 3 queue lifecycle, 2 serialization, 1 war score.

**5187 tests passing** (5145 + 42 new, 3 skipped, 0 regressions).

### Mar 4 — Session 8A: Backend Ledger + Debug Arsenal

Phase 8 Session 8A implementation. 1 new backend file, 1 new test file, 6 modified files, 82 new tests.

- **`backend/game_logic/diplomatic_ledger.py`** (NEW): `build_diplomatic_ledger(world)` returns 4 tabs: nations (per-nation diplomatic state, relation, diplomat, fog-filtered army strength, regions, treaties, vassal eligibility), treaties (active treaty list), threat_coalition (threat level/tier, qualifying nations, brewing/active coalition with fog-filtered member strengths), talleyrand (trust/label, skill, DP, mission, envoy count, sabotage warnings). Fog-filtered army strength: UNKNOWN→"Unknown", STALE→named bands (Negligible/Minor/Considerable/Powerful/Dominant), PARTIAL→~rounded to 5k, FULL→exact. National visibility = best marshal visibility across nation.
- **`backend/main.py`** (MODIFIED): GET `/diplomatic_ledger` endpoint. 7 top-bar fields in `/test` response (diplomatic_points, max_diplomatic_points, talleyrand_state, talleyrand_mission_summary, threat_level, coalition_brewing, coalition_brewing_turns, pending_envoy_count). Pass-through wiring for 3 popup fields (coalition_popup, diplomatic_sabotage, vassal_rebellion_imminent) with read→include→clear pattern. 8 debug endpoints (/debug/diplomatic_status, war_scores, acceptance_preview, coalition_status, threat_sources, proposal_cooldowns, vassal_loyalty/{nation}, proposal_queue).
- **`backend/models/world_state.py`** (MODIFIED): 3 new popup fields (coalition_popup, diplomatic_sabotage_popup, vassal_rebellion_imminent_popup). Serialized with backward-compat `.get()` defaults.
- **`backend/ai/llm_client.py`** (MODIFIED): "cheat " prefix detection in mock parser. Returns ParseResult with cheat_type and cheat_args.
- **`backend/ai/schemas.py`** (MODIFIED): cheat_type and cheat_args fields added to ParseResult dataclass.
- **`backend/commands/executor.py`** (MODIFIED): Cheat command routing + `_execute_cheat()` method with 10 commands (set_threat, set_relation, give_dp, trigger_coalition, set_war_exhaustion, set_diplo_state, create_vassal, set_vassal_loyalty, set_talleyrand_trust, queue_ai_proposal). Guard: only available in mock/debug mode.
- **`backend/game_logic/diplomacy.py`** (MODIFIED): `calculate_war_score()` extended with `return_components` parameter. When True, returns dict with total/territory/battles/decisive/capital breakdown.
- **`godot-client/.../api_client.gd`** (MODIFIED): `get_diplomatic_ledger()` method added.
- **82 new tests** in `tests/test_session8a_ledger_debug.py`: 11 test classes covering diplomatic ledger nations (8), army strength fog (12), treaties (3), threat/coalition (9), Talleyrand (9), cheat commands (16), debug endpoints (8), pass-throughs (6), top-bar fields (4), ledger endpoint (3), war score components (3).
- **5027 tests passing** (4945 + 82 new, 3 skipped, 0 regressions).

### Mar 4 — Session 7 Gap Closure: Coalition Polish

Closed 4 spec gaps + 1 comment cleanup from Session 7 confidence report. 5 files modified, 10 new tests.

- **Gap 1 (vassal.py):** Voluntary vassal release now calls `reduce_threat(world, 8, "voluntary_vassal_release")`. Only fires for player nation lord; rebellion path already handled separately.
- **Gap 2 (world_state.py):** Generous peace detection in `_ratify_treaty()`. When France signs peace while winning (war_score > 20) with sweeteners but no territory demands, applies -3 threat (`generous_peace`).
- **Gap 3 / EC-2 (coalition.py):** `form_coalition()` now voids in-transit proposals to joining nations. Restores Talleyrand state, refunds DP, logs event.
- **Gap 4 / EC-9 (executor.py + enemy_ai.py):** Coalition members blocked from attacking each other. Hard check in `_execute_attack()` + AI target filter skips coalition allies.
- **Gap 5 (coalition.py):** Replaced confusing 5-line comment about declare_war threat with clear one-liner.
- **10 new tests** in TestGapFixes class covering all 4 gaps with positive and negative cases.
- **4945 tests passing** (4935 + 10 new, 3 skipped, 0 regressions).

### Mar 4 — Session 7: Coalition System

Phase 8 Session 7 implementation. 1 new file, 9 modified files, 80 new tests.

- **`backend/game_logic/coalition.py`** (NEW): Complete coalition engine (~530 lines). Threat accumulation (add_threat/reduce_threat, 0-100 clamped). Threat decay (1 base + peaceful nations cap 3, Continental System uncapped). Coalition formation: brewing at ≥60 (3-turn countdown), instant at ≥80, cooldown override at ≥90. Qualifying nations (relation < -10, not vassal, not at war). Leader selection (military//1000 + hostility + authority, tiebreak marshals then alpha). Strategic posture (aggressive/defensive/cautious, leader personality override). Coalition friction (4 tiers: 1.0/0.75/0.5/0.25 by mutual relation). Loyalty penalty (min(-15 + WE//10, 0), wedge halving). War exhaustion (+casualties//1000 per battle cap 20, +5/turn at war, -5/turn at peace, coalition shock +5). British subsidy (200g/turn to lowest-relation partner). Dissolution (<2 members, all peace, or threat <20), 5-turn cooldown. Master per-turn processor (9 steps).
- **`backend/models/world_state.py`** (MODIFIED): 7 new fields (threat_level, threat_sources_this_turn, active_coalition, coalition_brewing, coalition_cooldown, coalition_count, war_exhaustion). Serialized with backward compat .get() defaults. advance_turn hook after vassal processing calls process_coalition_turn(). Per-turn clearing of threat_sources_this_turn. Treaty ratification wires add_threat(8/region annexed) and reduce_threat(5/region returned). Coalition member removal on separate peace.
- **`backend/commands/executor.py`** (MODIFIED): Threat wiring after battle resolution. France wins: +3 battle, +5 decisive (ratio >2:1 AND casualties >10k), +15 capital capture. War exhaustion for losing nation. Coalition shock on decisive defeat.
- **`backend/game_logic/diplomacy.py`** (MODIFIED): War declaration +20 threat. Diplomatic downgrade threat per DOWNGRADE_PENALTIES. Acceptance formula: threat_mod uses real threat_level (was stub), coalition_penalty via get_coalition_loyalty_penalty() added as new component.
- **`backend/game_logic/vassal.py`** (MODIFIED): Replaced direct threat_level writes with add_threat() calls (treaty vassalization +5, conquest +25, rebellion -10).
- **`backend/ai/enemy_ai.py`** (MODIFIED): Replaced TODO-1805 is_ally hack with is_coalition_member() check. Coalition friction applied to cross-nation adjacency bonus. New _get_convergence_bias_score() method (+12/+4/0 toward French territory by posture). Posture threshold adjustment in _find_attack_opportunity (aggressive -0.15, cautious +0.15).
- **`backend/game_logic/dispatch.py`** (MODIFIED): New _build_coalition_section() function. Returns threat level/tier/sources, brewing info, active coalition details (name, leader, posture, per-member stats). Wired into build_morning_dispatch() as dispatch["coalition_status"].
- **`backend/game_logic/diplomatic_templates.py`** (MODIFIED): 7 new template categories (T28-T34): coalition_murmur, coalition_brewing, coalition_declared, coalition_member_weak, coalition_advice_split, coalition_dissolved, coalition_harsh_warning. New slot resolvers for threat_level, coalition_name, leader, member_list.
- **`backend/notifications.py`** (MODIFIED): 7 new coalition notification constants (COALITION_THREAT_TENSION through COALITION_COOLDOWN_ENDED).
- **80 new tests** in `tests/test_session7_coalition.py`: 12 test classes covering threat accumulation (10), threat decay (5), qualifying nations (7), coalition formation (12), coalition structure (8), coalition AI (8), coalition breaking (11), dissolution (5), British subsidy (3), edge cases (6), serialization (2), process_coalition_turn (4).
- **4935 tests passing** (4855 + 80 new, 3 skipped, 0 regressions).

### Mar 4 — Session 6: Talleyrand Defiance + Diplomatic Objections

Phase 8 Session 6 implementation. 1 new file, 4 modified files, 76 new tests.

- **`backend/commands/diplomatic_defiance.py`** (NEW): Complete Talleyrand defiance system (§3a-§3e). Defiance probability curve mirroring V2b combat defiance (base 0.05, authority/trust modifiers, 2% Schemer floor, 30% hard cap, Loyalist immune). 5 sabotage types (softened, hardened, stalled, ap_downgrade, unit_overpay) based on proposal harshness. Discovery mechanism (40% base + 10%/turn cumulative). Confrontation dialogue with confront/overlook choices. Redemption event at trust ≤ 20 with 3 choices (apologize, replace with loyalist, continue). Pre-proposal V2a objection (MILD/MODERATE/STRONG based on harshness+trust). Override history tracking with dispatch honesty notes.
- **`backend/game_logic/diplomatic_templates.py`** (MODIFIED): 19 new template entries (T21-T27). T21 pre-proposal objections, T22 sabotage confrontation, T23 sabotage overlook. T24-T27 enemy diplomat voice templates (HAWK/SCHEMER/DOVE/LOYALIST × ACCEPT/COUNTER/REJECT). Enemy voice resolution functions mapping diplomat personality to template selection.
- **`backend/game_logic/diplomatic_dialogue.py`** (MODIFIED): Pre-proposal objection merge into dialogue flow. MILD = flavor text prepended, MODERATE/STRONG = inline options replacing standard dialogue choices.
- **`backend/game_logic/dispatch.py`** (MODIFIED): 3 new dispatch fields (talleyrand_discovery, talleyrand_override_note, talleyrand_redemption). Discovery check during Morning Dispatch with confrontation dialogue routing. Override dispatch notes ("pessimistic"/"prescient"). Redemption event triggering.
- **`backend/models/world_state.py`** (MODIFIED): 3 new fields (talleyrand_defiance_cooldown, pending_talleyrand_sabotage, talleyrand_override_history). Serialized with backward compat. Cooldown decrement + sabotage turns_hidden tracking in advance_turn.
- **76 new tests** in `tests/test_session6_diplomacy.py`: 15 test classes covering defiance probability (7), sabotage types (6), discovery (4), confrontation (2), cooldown (3), pre-proposal objection (7), honesty problem (4), redemption (9), enemy diplomat voices (12), template slots (7), serialization (5), proposal harshness (4), dialogue merge (2), sabotage tracking (2), loyalist floor (2).
- **4855 tests passing** (4779 + 76 new, 3 skipped, 0 regressions).

### Mar 4 — Session 4: AI Proposals + Counter-Offers + Advisory + Proactive Suggestions

Phase 8 Session 4 implementation. 2 new files, multiple modified files, 43 new tests.

- **`backend/ai/ai_diplomacy.py`:** AI diplomatic proposal engine. P1-P7 trigger table (war exhaustion, opportunity, relationship thresholds, trade potential, threat response, alliance building, subsidy requests). Anti-spam cooldowns per nation per action type. Queue system: max 3 pending proposals, 3-turn expiry for unanswered proposals.
- **Counter-Offer Algorithm (M3):** AI evaluates player counter-offers: remove worst clause from player perspective → recalculate acceptance → add cheapest desired clause → accept/reject based on updated score. Accept/Reject/Counter-offer actions wired into dialogue handler.
- **`backend/ai/diplomatic_advisory.py`:** Advisory conversation system. `detect_advisory_type()` classifies player queries (relationship status, proposal evaluation, strategic advice, treaty analysis, general). `generate_advisory()` produces context-aware Talleyrand responses. Wired into executor for "ask Talleyrand" command routing.
- **Proactive Suggestions (Talleyrand's Report):** New section in Morning Dispatch. 5 trigger types (expiring treaty, deteriorating relationship, diplomatic opportunity, threat warning, trade potential). Frequency caps to prevent spam. Integrated into `dispatch.py` builder.
- **Templates T11-T20:** 10 new diplomatic templates added to `diplomatic_templates.py` covering AI proposal presentations, counter-offer responses, advisory responses, and proactive suggestion formatting.
- **WorldState:** 4 new fields serialized (ai_proposal_queue, ai_proposal_cooldowns, advisory_history, proactive_suggestion_cooldowns). All with backward-compatible `.get()` defaults.
- **Turn Manager Integration:** AI diplomatic phase wired into `turn_manager.py` after enemy turns, before `advance_turn`. AI nations evaluate and generate proposals each turn.
- **Conflicting Alliance Resolution (§5b.3):** When AI proposes alliance conflicting with existing commitments, system detects and resolves per spec.
- **43 new tests** covering: AI trigger evaluation, cooldown enforcement, queue limits/expiry, M3 counter-offer algorithm, advisory type detection, advisory generation, proactive suggestion triggers, frequency caps, conflicting alliance resolution, serialization.
- **4697 tests passing** (4654 + 43 new, 3 skipped, 0 regressions).

### Mar 4 — Audit 4: Session 4 Verification

Post-Session 4 audit covering AI diplomatic proposals, M3 counter-offers, advisory system, Talleyrand's Report, and turn_manager integration.

- **Known gap resolved:** Integration test confirms end_turn → AI diplomatic phase → result dict wiring works correctly. AI proposal appears in result["ai_proposal"] when P1 trigger conditions are met.
- **27 new tests** in `tests/test_audit_session4.py`: turn_manager integration (3), cooldown lifecycle (4), counter-offer edge cases (3), advisory boundaries (7), dispatch Talleyrand edges (4), old save compatibility (1), conflict alert wiring (3), dead code detection (2).
- **Findings:** 0 bugs. 3 smells flagged (dead `tick_cooldowns()` function, Talleyrand war score trigger uses magnitude proxy instead of per-turn shift, `_try_add_desired_clauses` narrative mismatch). No blockers for Session 5.
- **Verdict: PASS.**
- **3 smells fixed (cleanup pass):** (1) Deleted dead `tick_cooldowns()` from ai_diplomacy.py. (2) Added `previous_war_scores` to WorldState for per-turn delta tracking; Trigger 2 now uses `abs(current - previous) >= 15` instead of magnitude proxy. (3) Clarified NATION_DESIRES / `_try_add_desired_clauses` intent via comments. 4 new tests for delta + serialization.
- **4728 tests passing** (4697 + 31 audit, 3 skipped, 0 regressions).

### Mar 4 — Audit 2+3: Sessions 2+3 Verification

Post-Session 3 audit covering diplomatic states, acceptance formula, diplomat class, Talleyrand commands, and conversational dialogue foundation. Full report: `docs/AUDIT_SESSION_2_3.md`.

- **3 structural checks** (1F, 1I, 1J): All PASS. POST route confirmed. Executor ordering correct (objection → capture → dialogue). advance_turn matches §7f (minor deviation: auto-downgrade before income — no functional impact).
- **29 new coverage gap tests** appended to `tests/test_audit_2_3.py`: Template fallback chain (9 tests), suggested terms generation (6 tests), resolve_template_text_with_type (2 tests), resolve_nation_name (3 tests), get_game_bucket branches (4 tests), get_transition_dp_cost paths (5 tests).
- **Diplomat table** added to `docs/SYSTEMS_REFERENCE.md` §16.
- **0 bugs found.** 4654 tests passing (4625 + 29 new, 0 regressions).
- **Verdict: PASS — ready for Session 4.**

### Mar 3 — Session 3: Talleyrand Commands + Conversational Dialogue Foundation

Phase 8 Session 3 implementation. 2 new files, 5 modified files, 76 new tests.

- **`backend/commands/diplomatic_dialogue.py`:** Conversation state machine (~300 lines). Handles 5 diplomatic action types (PROPOSE_TREATY, BREAK_TREATY, DEMAND_TRIBUTE, NEGOTIATE_TRADE, OFFER_SUBSIDY). Per-action state tracking (pending, accepted, rejected, counteroffered). Action prerequisites + validation (at_war, diplomatic_points, existing_treaty). Treaty history to prevent re-proposing. Berthier flavor text keyed by action + outcome.
- **`backend/commands/diplomatic_templates.py`:** 27 mock diplomat response templates (~500 lines). Templated by nation, action, diplomatic_points, military_advantage, relationship_delta. 5 placeholder slots: {name}, {nation}, {amount}, {treaty_type}, {reason}. Proper slot resolution with diplomatic context (DP costs, acceptance thresholds, breakdown analysis). Integration with `diplomatic_dialogue.py` for real-world flow.
- **WorldState:** 7 new fields (pending_diplomatic_action, diplomatic_action_state, current_dialogue, dialogue_history, treaty_history, diplomatic_ui_data, pending_counteroffter). All serialized with backward compat. Diplomatic processing wired into `advance_turn()`. Mission tracking for AI execution.
- **Parser:** Diplomatic command routing added to `parser.py`. Detects "propose treaty", "break treaty", "demand tribute", "negotiate trade", "offer subsidy" command patterns. Routes to diplomatic executor methods. Fuzzy matching on diplomat name and treaty type.
- **LLM client:** Diplomat response routing in `llm_client.py`. Context-aware prompt builder for diplomatic negotiations. Mock mode returns template-based responses per nation/action/advantage.
- **Executor:** 5 new `_execute_diplomatic_*()` methods for each diplomatic action. Validates state, charges DP costs, updates treaty history, generates dialogue via `diplomatic_dialogue.py`, propagates to frontend via `diplomatic_ui_data`.
- **Main.py:** `POST /diplomatic_action` endpoint. Accepts action type + target nation + diplomats involved. Returns diplomatic_ui_data for rendering.
- **Schemas.py:** Added `diplomatic_data` field to command response schema for frontend rendering.
- **76 new tests** (`test_diplomatic_dialogue.py`, `test_diplomatic_templates.py`, `test_diplomatic_commands.py`) covering: action prerequisites, state transitions, treaty history blocking, DP cost validation, template slot resolution, dialogue flow integration, AI mission execution, serialization.
- **4467 tests passing** (4391 + 76 new, 0 regressions).

### Mar 3 — Session 2: Diplomatic States + Acceptance Formula + Diplomat Class

Phase 8 Session 2 implementation. 2 new files, 3 modified files, 111 new tests.

- **`backend/models/diplomat.py`:** DiplomaticRepresentative class. 5 starting diplomats (Talleyrand/Castlereagh/Hardenberg/Metternich/Einsiedel) with personality/skill/trust/biography. Factory function for initialization.
- **`backend/game_logic/diplomacy.py`:** Core diplomatic engine (pure/deterministic). State transition validation (adjacency enforced, VASSAL requires OPEN_BORDERS+), war score calculation (territory ±40, battles ±30, decisive ±20, capital ±30, total ±100), acceptance formula (7 components + military supremacy/battlefield diplomacy + special bonuses), DP economy (generation formula, cost table with skill penalties), war declaration + DEFENSIVE_ALLIANCE cascade, downgrade transitions with auto-downgrade tracking, trade income, movement restriction validation, battle recording for war score.
- **WorldState:** 10 new fields (diplomats, diplomatic_points, max_diplomatic_points, nation_authority, war_scores, battle_records, decisive_battles, armistice_cooldowns, previous_treaties, turns_below_threshold). All serialized with backward compat. Trade income + diplomatic processing wired into advance_turn.
- **Executor:** Diplomatic movement restriction in _execute_move. Auto-war-declaration in _execute_attack. Battle recording for war score after combat.
- **Gate criteria:** 13/13 met. Acceptance formula reproduces §6c (score < 30 → REJECT). Trade income matches §1d for all 5 nations. Cascade: attack Austria → Prussia enters WAR.
- **4389 tests passing** (4278 + 111 new, 0 regressions).

### Mar 3 — Post-1B Audit: War Gating Hardening

Audit of Sessions 1A+1B before proceeding to Session 2. Found 1 HIGH + 3 MEDIUM issues:

- **H1 (HIGH):** `get_enemies_in_region()` used `m.nation != nation` without `is_at_war()` check — neutral nations (Austria, Saxony) treated as enemies in 30+ call sites. **Fixed:** Added `self.is_at_war(nation, m.nation)` filter.
- **M1:** Enemy AI ~25 inline `m.nation != nation` checks in enemy_ai.py lacked war gating. **Fixed:** All inline checks now include `world.is_at_war(nation, m.nation)`.
- **M2:** `_find_nearest_enemy_for_nation()` (used for reckless cavalry) lacked war check. **Fixed:** Added war state filter.
- **M3:** Test fixtures for `test_ai_coordination.py` (synthetic "Coalition" nation) and `test_strategic_executor.py` (Austria as path blocker) needed diplomatic state entries. **Fixed.**
- **16 new regression tests** in `test_diplomatic_war_gating.py` covering: get_enemies_in_region war awareness, _find_nearest_enemy war filtering, AI neutral nation behavior (3 tests incl. 5-turn smoke), strategic path blocking.
- **4280 tests passing** (up from 4264).

### Mar 2 — Master Pre-Implementation Audit (All 3 Diplomacy Specs)

Final adversarial audit across DIPLOMACY_SPEC.md v2.2, CONVERSATIONAL_DIPLOMACY_DESIGN.md v1.2, and COALITION_SPEC.md v1.1. All specs approved for implementation.

- **Audit scope:** 5,514 lines across 3 specs. 14 edge cases stress-tested. Fun score: 81/100 (no blockers).
- **4 CRITICAL findings fixed:**
  - C1: `war_exhaustion` field was used in COALITION_SPEC §6a formula but never defined — added to §10a + DIPLOMACY_SPEC §13.
  - C2: Session plan mismatch (7 vs 8 sessions) — DIPLOMACY_SPEC §14 and CONV_DESIGN §14c updated to 8-session plan.
  - C3: §7f missing coalition processing — steps 9a-9d added (war exhaustion, threat accumulation, decay, coalition check).
  - C4: 5 coalition WorldState fields missing from DIPLOMACY_SPEC §13 — cross-reference block added.
- **4 MAJOR findings fixed:**
  - M1: "Coalition war score" undefined — formula defined in COALITION_SPEC §4c (army-weighted average).
  - M2: CONV_DESIGN §14c wrong session mapping — D→Session 8 (was 7).
  - M3: British subsidy dependency — moved from Session 8 deferred to Session 7 (Coalition) scope.
  - M4: Battlefield Diplomacy bonus missing from §6b — added as 9th acceptance component (+10 when war_score > 20).
- **5 minor fixes:** Instant overrides brewing note (§3d), alliance threat clarification (§2a), bilateral wars note (§5), universal dismiss option, mission-pause-during-confrontation.
- **Stale references cleaned:** 5 outdated session numbers corrected across DIPLOMACY_SPEC.
- **Design gates approved:** Coalition Spec v1.1 and Starting Situation Balance (R1-R5) both approved. Jealousy remains separate track.
- **DIPLOMACY_SPEC bumped to v2.3.** COALITION_SPEC confidence report updated.
- **Verdict: GO for Session 1A.**

### Mar 1 — COALITION_SPEC.md v1.1 (Drafted + Audit-Revised)

Coalition system design spec created as companion to DIPLOMACY_SPEC.md v2.2. Comprehensive adversarial audit applied same session.

- **COALITION_SPEC.md v1.1 — AUDIT-REVISED.** 16 sections (+§16 Balance Analysis), 15 edge cases, 95/100 confidence. Covers: threat accumulation (9 sources including per-path vassalage, 7 reductions), coalition formation (40/60/80 thresholds with 3-turn brewing window + processing order), Option B leader system (leader sets strategic posture), coalition AI (no shared fog, convergence bias, historical friction), 4 breaking methods (separate peace, decisive victory, diplomatic wedge, Continental System), dissolution rules (2+ member persistence, 5-turn cooldown), implementation file locations (§10e).
- **v1.1 audit fixes (10 findings):** 3 CRITICAL (loyalty penalty formula, vassalage threat mismatch, decisive battle threshold), 4 MAJOR (leadership score units, British subsidy criteria, session naming, decay self-count, processing order), 3 MINOR (friction int(), worked example, edge cases).
- **Balance analysis (§16):** 5 diplomatic paths analyzed (Saxony/Prussia/Austria/Britain/diplomatic victory). 5 recommendations (R1-R5): Saxony 18k, Austria-Britain NON_AGGRESSION, Prussia -40, battlefield diplomacy bonus, Saxony OPEN_BORDERS starting state. R1/R2/R4/R5 APPLIED to DIPLOMACY_SPEC §1c/§1e. R3 specified but pending §6b addition. Design gate required for all.
- **DIPLOMACY_SPEC edits:** §1c Reynier 10k→18k, manpower pools updated, force balance updated. §1d economy tables updated (France +50 income from Saxony OB, Saxony upkeep recalculated). §1e starting states: France-Saxony PEACE→OPEN_BORDERS, Britain-Austria DEF_ALLIANCE→NON_AGGRESSION, France-Prussia -60→-40.
- **Session plan:** Coalition features in Session 7 (unified numbering with DIPLOMACY_SPEC). ~35-45 tests estimated.
- **STATUS.md, ROADMAP.md, CLAUDE.md updated.**

### Mar 1 — Diplomacy Readiness Audit + Design Gate Approvals

Comprehensive audit of diplomacy implementation readiness. Both specs approved for implementation.

- **DIPLOMACY_SPEC.md v2.2 — APPROVED.** Fixed §1b heading (18→19 regions), removed duplicate Milan from ASCII art.
- **CONVERSATIONAL_DIPLOMACY_DESIGN.md v1.2 — APPROVED.** Session plan unified with DIPLOMACY_SPEC.
- **Session plan reconciled:** Merged DIPLOMACY_SPEC's 6 sessions + CONV_DESIGN's 4 sessions into unified 7-session plan (eliminated duplication where conversation layer builds on mechanical sessions).
- **ADDING_CONTENT.md expanded** (+586 lines): New sections for Adding Diplomatic Representatives, Adding Diplomatic Actions, Adding Dialogue Templates. Expanded "Adding New Nations" from 3 steps → 12 steps with validation checklist.
- **CLAUDE.md updated:** Design gate approved, conversation layer files added to file reference table.
- **No code changes.** Documentation-only session.

### Mar 1 — Region Data Rationalization

Centralized hardcoded region data into `region.py` REGIONS_DATA (single source of truth). Added `starting_controller`, `grid_position`, `NATION_CAPITALS`, `get_starting_controllers()`. Files that previously required manual sync now auto-derive: `parser.py` (known_regions), `strategic_parser.py` (REGION_POSITIONS), `world_state.py` (_setup_initial_control), `enemy_ai.py` (capital lookups), `turn_manager.py` (victory thresholds), `executor.py`/`disobedience.py` (capital references). New `tests/test_map_consistency.py` validates Godot map.gd stays in sync with backend. Files-to-touch for map expansion reduced from ~10 to ~3. Updated ADDING_CONTENT.md throughout. **4211 tests passing.**

---

## Phase 7b Sessions

### Feb 26 — Strategic Order UI (Orders Tab in Strategic Ledger)

**4208 tests (3 skipped). New "Orders" tab (tab 6) in Strategic Ledger with consolidated order view and cancel buttons.**

- **Backend `_build_orders()`:** New section builder in `ledger.py`. Returns active orders (marshal, order type, target, path remaining, condition text, issued/arrived turn) followed by idle marshals. Helper functions: `_derive_order_display_name()`, `_derive_condition_text()` (reads StrategicCondition for human-readable status).
- **`POST /cancel_order` endpoint:** New endpoint in `main.py`. Takes `{"marshal": "Ney"}`, calls existing `_execute_cancel()`. AP pre-check rejects at 0 AP. Deducts 1 AP on success (matches typed cancel cost). Respects `no_action_cost` for graceful cancels (no active order).
- **Godot Orders tab:** 6th tab button in `strategic_ledger.tscn`. `strategic_ledger.gd` updated: `@onready` ref, `tab_buttons` array, `KEY_6` handler, `_render_orders()` with BBCode `[url=cancel:MarshalName]` meta links for cancel buttons. Cancel buttons greyed out (non-clickable) when AP = 0. `meta_clicked` signal wired for cancel → refresh flow.
- **`cancel_strategic_order()`:** New POST function in `api_client.gd`.

**Files modified:** `ledger.py` (_build_orders + helpers + return dict), `main.py` (POST /cancel_order), `strategic_ledger.tscn` (OrdersTab node), `strategic_ledger.gd` (tab 6 + render + cancel wiring), `api_client.gd` (cancel_strategic_order).

### Feb 26 — Strategic Compromise First-Step + Timed SUPPORT Timer Fix

**4208 tests (3 skipped). Fixed two bugs in strategic compromise orders.**

- **Bug 1: Compromise orders skip first-step execution.** All compromise paths in `_handle_strategic_objection_response` created the `StrategicOrder` but never executed immediate movement. Normal strategic orders move on issuance turn; compromise orders sat idle for a turn. Fixed by adding first-step movement block to the compromise handler. Affects all 4 order types (MOVE_TO, PURSUE, HOLD, SUPPORT).
- **Bug 2: Timed SUPPORT timer counts travel time.** `_check_condition` used `started_turn` for `max_turns` expiry. A 3-turn timed SUPPORT issued 2 hops away gave only 1 turn of actual support. Fixed by adding `arrived_turn` field to `StrategicOrder` — set when SUPPORT marshal first co-locates with ally, used as timer anchor in `_check_condition` for SUPPORT orders. Timer doesn't start until arrival.
- **Compromise message fix:** Timed SUPPORT compromise previously said "agrees to hold position" — now says "agrees to support {target}".
- **V2B spec fix:** Trust choice incorrectly said "AP refunded" — AP is never charged during objection (deferred). Fixed to accurate description.

**Files modified:** `marshal.py` (arrived_turn field + serialization), `strategic.py` (_check_condition SUPPORT timer, _execute_support arrival recording), `executor.py` (compromise first-step block, normal SUPPORT arrived_turn recording), `V2B_DEFIANCE_SPEC.md`, `SAVE_FORMAT_REFERENCE.md`, `test_strategic_bugfixes.py` (+7 tests).

### Feb 26 — V2b: Redemption Frontend Wiring + Integration Tests

**4201 tests (3 skipped). Audited all redemption paths, fixed Godot frontend gaps, added integration tests.**

- **Godot `_on_command_result`:** Added missing `redemption_event` check for bombardment friendly fire and non-end-turn commands. Previously, redemption dialog was never shown for these paths.
- **Godot end-turn chain:** Added deferred redemption checks at all 3 terminal points: `_on_enemy_phase_dismissed`, `_on_strategic_report_dismissed`, `_process_next_interrupt`. Cavalry trust penalty redemption now shows after enemy phase/reports/interrupts.
- **Godot `_on_interrupt_response`:** Added `redemption_event` check for fresh strategic interrupt responses where trust penalty crosses threshold.
- **Morning dispatch fix:** Added missing `_show_pending_dispatch()` calls in interrupt→redemption exit paths (Locations 4+5).
- **Administrative guard:** `check_redemption_threshold()` now blocks administrative marshals (out of play, strength=0).
- **3 integration tests:** Full executor-level verification that `_execute_bombardment` and `_execute_end_turn` propagate `redemption_event` to top-level result dict.

**Files modified:** `main.gd` (5 insertion points + 2 dispatch fixes), `disobedience.py` (admin guard), `test_redemption_v2b.py` (+4 tests: admin guard + 3 integration).

### Feb 26 — V2b: Redemption Audit Fixes (B2/B5/F1/F2)

**4197 tests (3 skipped). Fixed all audit findings from redemption V2b review.**

- **B2 (autonomous guard):** `check_redemption_threshold()` now returns None for autonomous marshals — prevents redundant popup during autonomy.
- **B5 (multi-marshal bombardment):** Replaced `or`-chain with first-wins guard (`if not friendly_fire_redemption`). Second marshal's trust still drops but doesn't get stuck with `redemption_pending = True`.
- **F1 (strategic interrupt wiring):** All 7 trust-penalty return sites in `strategic.py` now call `_attach_redemption_if_needed()`. Added `redemption_event` pass-through to `/strategic_response` endpoint in `main.py`.
- **F2 (cavalry wiring):** Both cavalry forced-stance and forced-unfortify `-3` penalties in `world_state.py` now call `check_redemption_threshold()`. Events hoisted through `tactical_events` in `_execute_end_turn`.
- **7 new tests:** Autonomous guard, strategic cancel triggers/doesn't trigger, cavalry stance/fortify/no-trigger, multi-marshal first-wins.

**Files modified:** `disobedience.py` (autonomous guard), `executor.py` (bombardment first-wins + tactical_events hoist), `strategic.py` (helper + 7 return sites), `world_state.py` (2 cavalry sites), `main.py` (/strategic_response pass-through), `test_redemption_v2b.py` (+7 tests).

### Feb 26 — V2b: Redemption System Interaction Gaps + 5-Turn Cooldown

**4190 tests (3 skipped). Fixed V2b defiance paths bypassing redemption event propagation. Added centralized helper + 5-turn cooldown.**

- **Bug:** V2b defiance early-return branches in executor.py bypassed redemption propagation — `redemption_pending` got stuck True because events were created but never delivered to frontend.
- **Centralized helper:** `check_redemption_threshold()` in `disobedience.py` — single gate for trust <= 20, not pending, not on cooldown, player-only. Replaces 7-line inline checks.
- **3 executor.py insertion points:** Tactical defiance success (Gap 1-2), strategic defiance success (Gap 3), strategic endpoint fallthrough (Gaps 4-5).
- **Bombardment refactor:** Replaced inline bombardment collateral check with centralized helper call.
- **5-turn cooldown:** `redemption_cooldown_until = current_turn + 5` set on resolution. Prevents rapid re-trigger spam.
- **18 new tests:** `test_redemption_v2b.py` — threshold helper (8 tests), cooldown lifecycle (3), tactical defiance (1), strategic defiance (2), bombardment regression (2), serialization (2).

**Files modified:** `marshal.py` (new field), `disobedience.py` (helper + cooldown), `executor.py` (3 wiring points + bombardment refactor), `SAVE_FORMAT_REFERENCE.md`, `SYSTEMS_REFERENCE.md`, `test_redemption_v2b.py` (new).

### Feb 26 — V2b Audit Pass 4: Post-Objection Routing Audit

**4172 tests (3 skipped). Audited `_execute_post_objection()` — the OUTPUT side of objection resolution. 1 BUG fixed, 2 GAPs closed, routing table documented.**

- **BUG (AP pre-check):** Admin actions (recruit/build/repair) in `_execute_post_objection` were gated on military AP pool (`world.actions_remaining`). With 0 military AP but >0 admin AP, these would be wrongly rejected. Split pre-check: admin actions check `admin_actions_remaining`, military actions check `actions_remaining`.
- **GAP (bombardment handler):** Added bombardment to the elif chain — finds nearest enemy, calls `_execute_bombardment`. Unreachable today (no personality generates bombardment as alternative) but prevents silent "Unknown action" if reached.
- **GAP (garrison handler):** Added garrison to the elif chain — routes to `_execute_garrison(command, game_state)`. Same rationale.
- **Verified clean:** Defiance signature parity (tactical/strategic identical), trust change timing (intentionally before execution), `_trust_penalty_applied` flag scoping, re-entrant objection prevention, marshal field injection, `target_stance` field preservation.
- **7 new tests:** `TestPostObjectionRoutingAudit` — admin AP gate (recruit/build/repair at 0 military AP), military AP gate, admin AP exhaustion, bombardment handler, garrison handler.
- **Routing table added to SYSTEMS_REFERENCE.md** — 19-row table covering all action handlers, AP pools, and signatures.

**Files modified:** `executor.py` (AP pre-check split + bombardment/garrison handlers), `test_objection_v2.py` (7 new tests), `SYSTEMS_REFERENCE.md` (routing table), `STATUS.md`.

### Feb 26 — V2b Audit Pass 3: Master Rules + Exhaustive Combo Audit

**4165 tests (3 skipped). Exhaustive audit of every personality × action combination through V2 trigger + V1 alternative/compromise. Two master rules implemented. 10 flagged issues fixed, 4 design notes documented.**

**Master Rule #1 — Validate before suggesting:** New `_can_execute_suggestion()` helper validates every fallback candidate. New `can_fortify()` helper. `can_drill()` now checks aggressive stance. All fallback chains loop through candidates, skip invalid options, return first valid.

**Master Rule #2 — Exhaust→MILD demotion:** Post-alternative-generation check in executor. If preferred==compromise, or preferred==original, or no valid alternatives exist → demote to MILD (grumble, no popup). Never show popup with fake choices.

**10 issues fixed:** ⚠️1 (aggressive preferred==compromise across 6 actions), ⚠️2 (already in aggressive stance), ⚠️3 (drill suggested but blocked by aggressive stance), ⚠️4 (cautious fortify both=defend), ⚠️5 (aggressive retreat mood variance), ⚠️6 (aggressive stance_change mood variance), ⚠️8 (cautious move already fortified), ⚠️9 (cautious defend all-buttons-identical), ⚠️10 (cautious fortify artillery both=defend).

**4 design notes documented:** D1 (fog disconnect V2↔V1 — TODO comment added), D2 (balanced/loyal V1 triggers orphaned — comment added), D3 (universal form_square MILD suppresses aggressive MODERATE — intentional, comment added), D4 (COMPROMISE_RULES gaps — caught by Master Rule #2).

**Files modified:** `disobedience.py` (`_can_execute_suggestion`, `can_fortify`, `can_drill` stance check, `_generate_alternative` rewrite, `_find_compromise` rewrite), `executor.py` (Master Rule #2 demotion block), `objection_v2.py` (design comments D2/D3).

### Feb 26 — V2b Audit Pass 2: Objection Table Gaps + Defiance Wiring

**1 new test (updated), 4165 total (3 skipped). Comprehensive audit of objection alternative tables, defiance wiring, and trust modification paths. 23 issues found and fixed.**

- **C1 (CRITICAL):** `stance` action name → `stance_change` with `target_stance` field in disobedience.py alternative generation.
- **C2 (CRITICAL):** `form_square` added to `objection_actions` in executor.py with pre-validation guards (already in square, cavalry, artillery).
- **H1 (HIGH):** Defiant attack now resolves nearest enemy target via `world.find_nearest_enemy()` instead of calling `_execute_auto_assign_attack()` with no target. Falls back to wait if no enemy found or attack fails.
- **M1-M4:** Scout target resolves marshal name→region. Aggressive+drill preferred diversified (move toward enemy/stance_change). No-enemies aggressive fallback returns `stance_change(aggressive)` instead of `defend`. Drill suggestions check prerequisites.
- **L1-L3:** Strategic trust paths use `_execute_post_objection()` to avoid re-entrant objections. `trust.modify()` → `modify_trust()` in defiance.py (3 locations) and executor.py (4 locations) to preserve redemption clearing.
- **N1-N7:** Free actions synced in post-objection. Admin AP routing in post-objection. Defiance AP charges for defiant action (not original). Broken/retreating guard before defiance roll. Dead code removed from objection_v2.py.
- **Final re-audit (6 additional):** Empty popups when V2 triggers MODERATE+ but V1 has no handler (aggressive HOLD+enemies, SUPPORT defensive target). Hold/wait/form_square aggressive handlers added. Compromise dedup logic prevents Trust=Compromise duplicates.
- **Compromise rules updated:** `(move, attack)→defend` (hold ground), `(defend, retreat)→fortify` (dig in).

**Files modified:** `disobedience.py` (12+ edits), `executor.py` (14+ edits), `defiance.py` (3 edits), `objection_v2.py` (dead code removal), `test_v2b_session1.py` (MockMarshal fix), `test_objection_v2.py` (updated expectation).

### Feb 25 — V2b Session 3: Frontend + Polish + UI Tests

**0 new tests (frontend-only session), 4164 total (3 skipped). V2b fully wired to Godot — defiance, authority, and vindication visible in-game. Gate 6 UI test checklist expanded.**

- **Defiance display (main.gd):** Bordered "DEFIANCE" block in terminal output when marshal defies. Shows defiance action, outcome label (VINDICATED/FAILURE/INCONCLUSIVE/DISCIPLINE HELD), Berthier flavor text, trust/authority stat changes. Color-coded by outcome (green right, red wrong, neutral inconclusive). Authority threshold events displayed as separate bordered "AUTHORITY" block.
- **Authority display (ledger + dispatch):** Authority value + label (Strong/Normal/Weak) added to strategic ledger Forces tab header (`ledger.py` + `strategic_ledger.gd`), morning dispatch SITUATION section (`dispatch.py` + `main.gd`), and dispatch re-read screen (`dispatch_view.gd`). Color-coded: green ≥80, neutral 50-79, red <50.
- **Vindication display:** Already wired in Sessions 1-2 (marshal management cards show vindication score with color coding). No changes needed.
- **Gate 6 UI test checklist:** Expanded from ~10 items to 45+ items across 8 categories: Defiance Display, Vindication Display, Authority Display, Relationship SUPPORT, Fog-Aware Objections, Notification & Log, Regression Checks.
- **Doc updates:** STATUS.md, SYSTEMS_REFERENCE.md (V2b frontend display table), SAVE_FORMAT_REFERENCE.md (version bump), CLAUDE.md (phase status), PHASE7_UI_TEST_GATE.md (Gate 6 expanded).

**Files modified:** `main.gd` (defiance + authority display, objection response handling), `strategic_ledger.gd` (authority in forces header), `dispatch_view.gd` (authority in situation), `ledger.py` (authority fields), `dispatch.py` (authority fields).

### Feb 25 — V2b Session 2: Fog-of-War Migration

**88 new tests, 4164 total (3 skipped). Objection system now fog-aware — marshals object based on what they can see, not omniscient data.**

- **Step 1 — Fog infrastructure:** Added `_get_region_visibility()` helper (Step 0 rule: own region always FULL). Added `get_target_intel_level()` for Type B target queries. Rewrote `get_visible_enemies_near()` to return fog-filtered dicts (name, strength, visibility, location) instead of raw marshal objects. At PARTIAL, strength replaced by band midpoint (2500/10000/27500/55000/85000).
- **Step 2 — Type A scan queries (3 leaf → 3 auto-propagate):** Rewrote `_check_enemy_adjacent()`, `_get_friendly_to_enemy_ratio()`, `_path_crosses_enemy()`/`_path_has_enemies()` to use fog-filtered data. Only PARTIAL+ enemies detected. Zero visible enemies → ratio 999.0. Auto-propagated: `_get_enemy_to_friendly_ratio()`, `_is_outnumbered_2to1()`, `_is_actually_threatened()`.
- **Step 3 — Type B target queries (2 functions):** Rewrote `_get_attack_odds_ratio()` (FULL=exact, PARTIAL=band midpoint, STALE/UNKNOWN=1.0) and `_check_attack_target_fortified()` (only True at FULL visibility).
- **Step 4 — Fog-specific triggers (4 new):** #9: Cautious attack UNKNOWN → STRONG. #10: Attack STALE → cautious MODERATE, aggressive MILD. #11: Scout-shows-weakness handled by fog-filtered ratio logic (no visible enemies = "defending nothing"). #12: PURSUE no intel → cautious STRONG, aggressive MILD.
- **MockWorld upgraded:** Added `_MockRegionIntel`, `get_region_intel()`, `set_region_visibility()` to test mock, defaulting to FULL visibility to preserve all pre-fog tests.
- **Edge cases verified:** Step 0 own-region rule, PARTIAL band midpoints, UNKNOWN→999.0 ratio, mixed-visibility paths, fortification hidden below FULL, `_check_enemy_in_region()` unchanged, aggressive ignores fog for attacks.

**Files modified:** `objection_v2.py` (9 functions rewritten + 4 new triggers + fog imports/helpers), `test_objection_v2.py` (MockWorld fog support).
**Files created:** `tests/test_v2b_fog_migration.py` (88 tests, 19 classes).

### Feb 25 — Session 67: Square Formation (Tactical Triangle Part A)

**48 new tests, 3926 total (3 skipped). Infantry can now form square — devastating vs cavalry, vulnerable to artillery.**

- **Form Square action (1 AP):** Infantry-only (not cavalry, not artillery). Sets `square_formation = True`. Mutually exclusive with fortified. Cancels active strategic orders (including HOLD with holding_position/hold_region clearing). Blocked when broken, retreating, drilling, already in square.
- **Break Square action (0 AP, free):** Clears `square_formation`. Free action — doesn't consume AP.
- **Auto-break:** Square automatically breaks on any active order (attack, move, fortify, drill, recruit, garrison, stance_change, glorious_charge). Preserves immersion — marshals don't stay in square while marching.
- **Combat interactions:** Cavalry attacking square suffers -40% damage (`shock_multiplier *= 0.60`). Artillery attacking square deals +50% damage (`shock_multiplier *= 1.50`). Square provides +5% defense modifier. Both normal and deferred casualty paths handle these.
- **Bombardment:** +50% bombardment damage vs square (`square_bombardment_bonus = 1.50`). Extra -15 morale penalty (total -18: 3 base + 15 square). Packed formation = perfect artillery target.
- **Coordination:** Square marshals contribute defense-only coordination (0% attack, same as fortified). Excluded from adjacent ally support count. Cannot reinforce while in square (Rule #15).
- **V2a objections (4 triggers):** Aggressive objects to form_square → MODERATE ("Let me CHARGE them!"). Cautious objects when fortified → MILD. Cautious objects when artillery adjacent but no cavalry → MILD. Universal: both cavalry AND artillery adjacent → MILD.
- **Enemy AI (P2.5):** Between P2 (survival) and P3 (threats). Infantry forms square when enemy cavalry adjacent + no enemy artillery + cooldown expired. Breaks square when no cavalry threat. Anti-oscillation cooldown of 2 turns after breaking.
- **Battle report:** 3 new Berthier observation categories (square_cavalry_repulsed, square_artillery_punished, square_held_defense). Snapshot entries for cavalry penalty, artillery bonus, and defense bonus.
- **Serialization:** `square_formation` field in `to_dict()`/`from_dict()` with `.get()` default False.
- **Tactical state clearing:** Square clears on broken/retreat in `_process_tactical_states()`. AI cooldown decrements per turn.

**Files modified:** `marshal.py` (field, defense modifier, serialization), `combat.py` (cavalry -40%, artillery +50%, deferred path fix), `executor.py` (form_square, break_square, auto-break, bombardment bonus, coordination exclusions, reinforcement rule, SUPPORT advisory), `world_state.py` (AP costs, tactical state clearing), `objection_v2.py` (4 triggers), `enemy_ai.py` (P2.5), `battle_report.py` (3 observations, snapshots), `validation.py`, `parser.py`, `llm_client.py` (mock keywords).
**Files created:** `tests/test_square_formation.py` (48 tests, 12 classes).

### Feb 25 — Session 68: Auto-Bombardment + Overwatch (Tactical Triangle Part B)

**54 new tests, 3980 total (3 skipped). Artillery on SUPPORT auto-bombards before supported marshal's attack. Enemy artillery passively debuffs attackers (overwatch).**

- **Auto-Bombardment:** Artillery with SUPPORT order targeting attacker X fires `_execute_bombardment()` against defender BEFORE `resolve_battle()`. Same damage formula, collateral, fort degradation. Fires for both player and AI (Building Blocks). Does NOT consume AP. Increments `bombardments_this_turn`. Dead-defender early exit skips resolve_battle entirely.
- **Overwatch:** Enemy artillery in defender's region applies -3% attack per gun, capped at 3 guns (-9% max). Transient `overwatch_penalty` field on marshal, applied in `get_attack_modifier()` after coordination bonus. NOT serialized. Cleared via `_COORDINATION_FIELDS` after combat.
- **AI awareness:** `_evaluate_target_ratio()` factors overwatch into ratio calculation — discourages attacking well-defended positions with artillery overwatch.
- **Battle report:** 3 new Berthier observation categories (support_bombardment_effective, support_bombardment_minimal, overwatch_repelled). Overwatch penalty snapshot entry. `{artillery}` placeholder in `_fill()`.
- **Fog of war:** Auto-bombardment from adjacent region gives defender PARTIAL intel on source region via `update_intel_from_transit()`.

**Files modified:** `marshal.py` (overwatch_penalty in get_attack_modifier), `executor.py` (_calculate_overwatch, auto-bombardment loop, dead-defender check, _COORDINATION_FIELDS), `battle_report.py` (3 observations, snapshot, placeholder), `enemy_ai.py` (overwatch factor).
**Files created:** `tests/test_auto_bombardment_overwatch.py` (54 tests, 7 classes).

### Feb 25 — AI Recapture + Quality Fixes (Hotfix)

**35 new tests, 3877 total (3 skipped). Fixes AI failure to recapture lost territory ("Southern Bypass" exploit).**

Playtesting revealed the AI fails to recapture lost territory — the player could capture 5+ enemy regions completely unopposed. Seven fixes applied to `enemy_ai.py`:

1. **Capital-Elevated Homeland Defense:** When capital lost, P3.7 fires BEFORE P3 at priority 2 (survival-level). Capital recapture can't be blocked by cautious fortifying.
2. **Extended Range:** Homeland defense range increased from 3 to 6 hops; unlimited for capitals.
3. **P3 Throttling:** When 2+ regions lost, only 1 marshal per nation stays on P3 threat defense. Rest fall through to P3.7 recapture.
4. **Deathball Fix:** "Someone closer" check now requires the closer marshal to be *available* (not fortified/drilling/broken). Marshal→target assignments tracked to split across multiple lost regions.
5. **Enemy Pathfinding:** Capital recapture allows movement through enemy-occupied regions if marshal has 50%+ of enemy strength.
6. **Stagnation Fix:** Skipped marshals (priority 999) now increment stagnation. Stagnation breaker returns `wait` instead of `None`.
7. **Cautious Advance Fix:** At stagnation >= 3, cautious advance fallback allows non-friendly territory (untraps map-edge marshals).

New helpers: `_is_capital_lost()`, `_count_lost_regions()`, `_nation_has_threat_responder()`. New tracking fields: `_recapture_marshal_assignments`, `_threat_responder_assigned`.

### Feb 24 — Session 66: Godot UI + Integration Audit

**32 new tests, 3799 total (3 skipped). UI integration for Phase 7 coordination features + cross-system audit + confidence report.**

- **Coordination readiness tooltip (map.gd):** Region tooltip now shows combined arms count and co-location status (dedicated vs accumulating) for player marshal pairs. Marshal tooltip shows color-coded relationship lines (Hostile=red, Rival=orange, Professional=white, Friendly=green, Devoted=gold).
- **Inline-dramatic reinforcement display (main.gd):** Gold-bordered BBCode blocks for reinforcement arrival (green) and failure (red). Zero new popup types per MULTI_MARSHAL_SPEC §14.
- **First-time coordination tutorial (executor.py + world_state.py):** Fires ONCE per campaign on first player combined arms attack (type_count >= 2). Tracked by `coordination_tutorial_shown: bool` on WorldState. Displays Berthier's report explaining combined arms, coordination improvement, and casualty sharing.
- **Enemy phase reinforcement display (enemy_phase_dialog.gd):** Reinforcement messages shown in enemy phase battle summaries.
- **Backend data for tooltips (world_state.py):** `get_game_state_summary()` now includes per-player-marshal `relationships` dict (value + label) and `co_location_turns` dict. All values `int()`-wrapped.
- **API passthrough (main.py):** `reinforcement_messages` and `coordination_tutorial` fields wired through POST /command response.
- **Reinforcement message polish:** Replaced internal reason codes (`literal_personality`, `fate_intervened`, `low_score`) with Berthier-voice narrative text. Removed raw score/threshold from arrival messages.
- **Integration audit:** Full cross-system confidence report. All Phase 7 areas scored ≥97%. No bugs found.

**Files modified:** `executor.py` (tutorial trigger), `world_state.py` (field + summary data), `main.py` (passthrough), `main.gd` (reinforcement + tutorial display), `map.gd` (tooltips), `enemy_phase_dialog.gd` (reinforcement display).
**Files created:** `tests/test_session66_integration.py` (32 tests: 7 classes covering serialization, tutorial trigger, game state summary, reinforcement messages, edge cases, full battle integration, filtered summary).

### Feb 24 — Gate 4 Remaining Fixes + Berthier Reinforcement Naming

**23 gate4 tests + 4 new observation tests, 3767 total (3 skipped). Two critical combat path bugs fixed + Berthier now names all reinforcers.**

- **Issue 4 — General attack bypasses Phase 7:** `_execute_general_attack_combat()` called `resolve_battle()` directly, skipping coordination/reinforcements/casualty distribution/relationships/reports. Rewritten to delegate to `_execute_attack()` (same pattern as auto-assign fix). Eliminated ~100 lines of duplicated combat code.
- **Issue 5 — Reinforcer stalemate stranding:** Reinforcers stayed in battle region after stalemate (neither `atk_lost` nor `atk_won` matched). Changed `if atk_lost:` → `if not atk_won:` and `if atk_won:` → `if not def_won:` so both sides' reinforcers return on any non-win.
- **Berthier reinforcement naming:** P0.7 observation now names ALL marshals who arrived and ALL who failed. New "mixed" template category for when some arrived and some didn't. E.g. "Davout arrived to reinforce Ney, but Grouchy failed to reach the field in time."
- **Test isolation fixes:** 2 pre-existing tests fixed to isolate marshals (Uxbridge at Waterloo contaminated force ratios).

### Feb 24 — Gate 4 Fixes (Post-Session 65)

**15 new tests, 3756 total (3 skipped). Three UI testing issues + reinforcer retreat-on-loss fixed before Session 66.**

- **Issue 1 — Berthier narrative voice:** Removed coordination modifier entries (Combined arms, Per-ally coordination, Dedicated coordination, Adjacent support, Coordination total) from `snapshot_attacker_modifiers()` and `snapshot_defender_modifiers()`. Coordination info now conveyed only through Berthier's narrative observation templates (already prose). Removed dead `coordination_preview` generation from executor. Detailed coordination numbers deferred to Battle History screen (Phase 8.5).
- **Issue 2 — Auto-routed attack missing coordination:** Rewrote `_execute_auto_assign_attack()` to delegate to `_execute_attack()` after finding nearest marshal (Building Blocks principle). Eliminated ~300 lines of duplicated combat logic. All attack paths now include full coordination, reinforcement, relationship, and battle report support.
- **Issue 3 — Artillery advancing on reinforcement:** Artillery reinforcing from adjacent no longer relocates to battle region. Provides fire support from adjacent position (not advance). Still gets `reinforced_this_turn` flag. Explicitly added to casualty distribution participants despite not being in battle region. **Coordination gap fix:** artillery NOT added to `arrived_names` (which becomes `exclude_from_adjacent`), so artillery still counts as adjacent ally for +2% attack bonus.
- **Issue 3b — Reinforcer retreat-on-loss:** Reinforcers who relocated to battle region now return to their origin if their side lost (spec: "reinforcer retreats with primary if battle lost"). Tracks pre-arrival locations in `reinforcer_origin` dict. After combat, if `atk_lost`, attacker-side reinforcers return; if `atk_won`, defender-side reinforcers return. Morale-based forced retreat (<=25) still runs first for broken armies.

**Files modified:** `battle_report.py` (removed coordination from modifier snapshots), `executor.py` (auto-assign delegation, artillery no-advance + coordination gap, reinforcer retreat-on-loss, coordination preview removal).
**Files created:** `tests/test_gate4_fixes.py` (15 tests: 3 Berthier narrative, 3 auto-assign delegation, 6 artillery reinforcement, 3 retreat-on-loss).
**Files updated:** `test_auto_assign_attack.py` (1 assertion fix), `test_battle_report.py` (4 tests), `test_combined_arms.py` (4 tests), `test_coordination_bonus.py` (2 tests).

### Feb 24 — Session 65: Full Battle Reports + Berthier Coordination Observations

**24 new tests (89 total in test_battle_report.py), 3741 total (3 skipped). Berthier now comments on coordination, reinforcements, relationships, and hostile dynamics.**

- **7 new observation categories** added to `_pick_observation()` priority chain:
  - P0.5: Full combined arms triangle (infantry + cavalry + artillery)
  - P0.7: Reinforcement arrival (ally marched onto the field)
  - P0.8: Reinforcement failure (ally failed to arrive)
  - P5.5: Hostile forced (hostile marshal fought alongside under SUPPORT order)
  - P12: Hostile refused (hostile marshal stood idle)
  - P13: Devoted synergy (devoted ally coordination bonus)
  - P15: Rival improved (relationship improvement after shared battle)
- **`_fill()` template system** converted from `.format()` to `.replace()` for graceful degradation. 4 new placeholders: `{ally}`, `{relationship}`, `{coordination_bonus}`, `{arrival_score}`.
- **Snapshot extensions:** `snapshot_attacker_modifiers()` and `snapshot_defender_modifiers()` originally captured per-ally coordination and dedicated coordination bonuses. **Removed in Gate 4 fixes** — coordination conveyed via narrative observation only; detailed numbers deferred to Battle History screen (Phase 8.5).
- **Coordination context injection:** `executor.py` injects `coordination_context`, `reinforcement_results_for_report`, and `relationship_changes` into `battle_result` dict after `resolve_battle()`. Observation re-picked with full data.
- **Pre-battle coordination preview:** Originally showed coordination bonus breakdown before battle resolves. **Removed in Gate 4 fixes** — Godot never consumed it; narrative observation handles coordination storytelling.
- **Reinforcement notification messages:** Added to executor result dict for Godot rendering (deferred to S66).
- **Two-pass observation picking:** Initial pick inside `resolve_battle()` (no coordination data), re-pick in `executor.py` after all data injected.

**Files modified:** `battle_report.py` (7 templates, `_fill()` rewrite, 7 priority levels, 2 snapshot extensions), `executor.py` (coordination injection, observation re-pick, preview, reinforcement messages).
**Files modified (tests):** `test_battle_report.py` (+24 tests in `TestCoordinationObservations` class).

### Feb 24 — Session 63: AI Coordination Enhancements

**35 new tests, 3720 total (3 skipped). AI now uses relationships and coordination awareness for smarter multi-marshal behavior.**

- **P4.6 Coordinated Attack Setup:** AI marshals move to stage coordinated attacks when solo ratio < 1.5x but combined with nearby allies (within 2 distance, relationship >= Rival) would exceed 1.5x. Returns MOVE toward nearest eligible ally.
- **P4.75 Relationship Filtering:** Ally support now excludes Hostile (-2) allies and prioritizes by relationship (Devoted > Friendly > Professional > Rival). Sorting ensures best relationships supported first.
- **P4.76 Co-Location Persistence Guard:** Inside `_consider_strategic_move()`, prevents marshal from moving away when co-located with ally near enemy threat and settled (not moved this turn). Falls through to wait/P8.
- **P4.77 Cross-Nation Adjacency Scoring:** Strategic movement now scores candidate positions by ally adjacency: Devoted +10, Professional/Friendly +5, Rival/Hostile 0. Applied as tiebreaker in aggressive, cautious fallback, and cautious advance paths. TODO-1805 comment for coalition detection.
- **P4.78 Defensive Reinforcement:** After P7, before P7.5. Moves adjacent to threatened Rival+ ally for reinforcement readiness. Prefers positions also adjacent to enemy. Returns None if already adjacent or ally not threatened.
- **Attack Threshold +8%:** `_find_attack_opportunity()` inflates effective ratio by +0.08 per co-located ally. Additive: solo 1.1 + 2 allies = 1.26. Personality thresholds unchanged.
- **Stagnation Override:** Artillery frontline penalty reduced when stagnation >= 3: unscreened -50 → -20, screened -30 → -10. Non-artillery unaffected.
- **Combined Arms Awareness:** +20 score bonus in P7 for positions completing the infantry/cavalry/artillery triangle (2 types present, marshal is 3rd).

**Files modified:** `enemy_ai.py` (5 new methods, 3 modified methods, 2 helper methods), `SYSTEMS_REFERENCE.md`, `STATUS.md`, `ENEMY_AI_REFERENCE.md`.
**Files created:** `tests/test_ai_coordination.py` (35 tests, 9 classes).

### Feb 23 — Post-S62 Hotfix: Artillery Positioning + Casualty Reduction

**22 new tests, 3685 total (3 skipped). Two artillery fixes from playtest observation.**

- **Artillery AI frontline avoidance:** `_score_artillery_position()` now penalizes front-line regions (adjacent to enemy territory). Unscreened frontline: -50. Screened frontline (co-located infantry): -30. New "behind-screen" bonus (+15) for non-frontline positions with adjacent infantry holding the front line. Fixes observed behavior of artillery advancing into freshly-conquered regions instead of staying in rear bombardment positions.
- **Artillery casualty reduction in combined arms:** `_distribute_casualties()` now applies 50% casualty reduction to artillery when fighting alongside non-artillery units (rear-position advantage). Remainder goes to strongest non-artillery marshal. No reduction when artillery fights alone or with only other artillery. `ARTILLERY_CASUALTY_FACTOR = 0.5` class constant.
- **Session 63 decisions resolved:** (1) Frontline penalty values (-50/-30): **Keep current values.** Tuning deferred to 1805 region wiring — more rear positions available at 80+ regions. (2) Stagnation breaker vs frontline avoidance: **Stagnation overrides with reduced penalty.** When artillery idle 3+ turns (stagnation counter active), reduce frontline penalty from -50 to -20 (reluctant but willing). Prevents artillery paralysis when front line collapses around it. (3) Cavalry screens and frontline penalty: **Already handled.** Screened frontline is -30 (vs unscreened -50), cavalry counts as screen. No further reduction needed.

**Files modified:** `enemy_ai.py` (`_score_artillery_position` frontline penalty + behind-screen bonus), `executor.py` (`_distribute_casualties` artillery reduction + `ARTILLERY_CASUALTY_FACTOR`).
**Files created:** `tests/test_artillery_hotfix.py` (22 tests, 5 classes).

### Feb 23 — Session 62: Casualty Distribution

**63 tests (47 original + 16 post-review), 3663 total (3 skipped). Multi-marshal battles now distribute casualties proportionally among participants. First Phase 7b session.**

- **`resolve_battle(apply_casualties=False)`:** New contract per C1/C2. Computes all combat math but defers 5 side effect categories (casualties, morale, battles_won/lost, counter-punch, recklessness) to caller. Returns raw casualties, morale deltas (as int), and projected-strength outcome.
- **Fortification degradation KEPT** inside resolve_battle (battle-triggered per C1).
- **C2 projected-strength victor:** Uses `attacker.strength - casualties` for outcome determination. 1.5 threshold matches normal path.
- **`_distribute_casualties()`:** Proportional by strength fraction. Remainder to strongest marshal. Cap at marshal strength. Sum matches raw total exactly.
- **`_get_casualty_participants()`:** Mirrors `get_battle_participants()` for D3 Hostile+SUPPORT detection. Must run BEFORE strategic orders cleared.
- **Per-participant effects:** Uniform morale delta (psychological), individual battles_won/lost, independent forced retreat check.
- **Primary-only effects:** Recklessness (attacker), counter-punch (defender), counter-punch mastery (Davout).
- **Pursuit damage** handled in executor for coordinated battles (primary attacker ability vs primary defender).

**Files modified:** `combat.py` (apply_casualties parameter + `_build_deferred_result`), `executor.py` (`_distribute_casualties`, `_get_casualty_participants`, `_execute_attack` coordination branch).
**Files created:** `tests/test_casualty_distribution.py` (63 tests, 8 classes).

**Post-review fixes (Opus code review):**
- **C-1 (CRITICAL):** Fixed `relationship.py` reading non-existent top-level `"attacker_casualties"` key. Now reads from nested `battle_result["attacker"]["casualties"]` (correct for both normal and deferred paths). Removed fake top-level keys from test helper `_make_battle_result()`.
- **W-1 (WARNING):** Moved SUPPORT order clearing in `executor.py` from before combat to after `process_battle_relationships()`, so Hostile+SUPPORT reinforcements participate in relationship checks.
- **W-2 (WARNING):** Documented rounding cap limitation in `_distribute_casualties()` (excess from overkill on small units not redistributed — acceptable as overkill).
- **16 new tests:** TG1 (primary destroyed), TG2 (asymmetric 2v1), TG3 (AI participants), TG5 (Davout non-primary), TG6 (conformance: nested keys, no top-level keys, deferred raw keys, relationship reads nested), W-1 timing (3 tests).

---

## Phase 7 Core Sessions

### Feb 23 — Session 64: Win/Loss Relationship Formula

**34 new tests, 3600 total (3 skipped). Shared battles now trigger relationship checks between co-located same-nation marshals. Phase 7 Core COMPLETE.**

- **`calculate_battle_severity()`:** Categorizes battles as decisive (ratio < 0.5), standard (0.5–0.8), or narrow (> 0.8) based on winner/loser casualty ratio.
- **`check_shared_battle_relationship()`:** WIN formula (base 30 + severity + rel_mod + variance ±10) and LOSS formula (base 15 + severity + rel_mod + variance ±10). Threshold strict `> 50` (M2). Returns ±1 or 0.
- **Ordered pairs (D4):** Uses `itertools.permutations` — 3 marshals = 6 independent checks. Cooldown is per-direction (A→B independent of B→A).
- **Intentional asymmetry (M1/M2):** Hostile WIN max=35 (never improves). Devoted WIN max=35 (never improves). Hostile LOSS max=50 (never degrades — strict > 50). Rival decisive WIN ~24% improvement chance.
- **Cooldown:** 3 turns per direction, tracked in `last_relationship_change_turn` (serialized in S59).
- **Participants:** Same-nation marshals in battle region, excluding Hostile without SUPPORT. Primary always included.
- **Event logging:** Relationship changes logged via `world.log_event()` with type `"relationship_change"`.
- **Files created:** `backend/game_logic/relationship.py`, `tests/test_relationship_formula.py` (34 tests).
- **Files modified:** `backend/commands/executor.py` (wired into `_execute_attack()` after combat notifications, before destruction check).

### Feb 23 — Session 61b: Reinforcement Edge Cases + SUPPORT Objection Triggers

**22 new tests, 3566 total (3 skipped). Edge cases for reinforcement eligibility, Grouchy Rule upgrade, Berthier advisory, and SUPPORT objection triggers.**

- **Rule #12 — moved_this_turn (A-D2):** Marshals that already moved this turn cannot reinforce (prevents force-marching twice). Blocks artillery that moved from reinforcing.
- **Rule #13 — Hostile exclusion (A-D4):** Hostile marshals (relationship -2) without a SUPPORT order targeting the primary combatant are excluded from auto-reinforcement. Hostile WITH SUPPORT still passes eligibility (arrives for casualties, 0% coordination per D3).
- **Grouchy Rule PURSUE region-match (A-D1):** Upgraded from name-match to region-match. Grouchy with `PURSUE Wellington` now arrives at a battle where Wellington is present, even if the primary defender is Blucher.
- **Berthier fortified SUPPORT advisory (A-M3):** When SUPPORT is issued to a fortified marshal, Berthier warns they cannot march to reinforce. Informational only — does not block the order.
- **§6 SUPPORT objection triggers:** Two new triggers in `objection_v2.py`: aggressive personality objects to defensive SUPPORT (target fortified/cautious/broken → MODERATE), cautious personality objects to reckless SUPPORT (target aggressive + recklessness ≥ 2 → MODERATE).
- **Files modified:** `executor.py` (rules 12-13, PURSUE region-match, Berthier advisory), `objection_v2.py` (SUPPORT triggers), `test_reinforcement.py` (updated hostile trust test for A-D4).
- **Files created:** `tests/test_reinforcement_edge_cases.py` (22 tests across 7 classes).

### Feb 23 — Session 61a: Adjacent Reinforcement (Arrival Score & Base Reinforcement)

**49 new tests, 3544 total (3 skipped, 1 pre-existing flaky). Adjacent marshals physically reinforce into ongoing battles.**

- **Reinforcement system:** Adjacent same-nation marshals automatically attempt to join ongoing battles. 11 eligibility rules (same nation, adjacent, strength > 0, not broken, not retreated, not recovering, not fortified, not on HOLD, not engaged, not drilling, not already reinforced).
- **Grouchy Rule (personality gate):** Literal-personality marshals CANNOT reinforce unless they have a SUPPORT or PURSUE order targeting a battle participant. Checked before arrival score.
- **Arrival score formula:** `base(50) + logistics*5 + relationship_mod + terrain_mod + personality_mod + support_bonus + variance(±8)`. Variable threshold: 60 with SUPPORT/PURSUE order, 65 without.
- **Fumble roll (I3):** 5% failure chance even when score > 80 (`random.randint(1,20) == 1`).
- **Physical relocation:** Successful reinforcers move to battle region, set `reinforced_this_turn = True`, join coordination calculation. Strategic orders preserved through coordination, then cleared after (A-C2 ordering).
- **Path B2 dedicated support:** Arrived-via-SUPPORT reinforcers count for `_has_dedicated_support()` coordination check.
- **Trust penalty:** -3 trust on failed reinforcement (except Literal and Hostile personalities).
- **Both sides reinforced:** Attacker and defender independently receive reinforcements (Building Blocks — AI uses identical code).
- **Serialization (M4):** `reinforced_this_turn` field serialized, cleared at turn start.
- **Files modified:** `executor.py` (+`_is_reinforcement_eligible`, `_calculate_arrival_score`, `_calculate_reinforcements`, extended `_execute_attack`, extended `_calculate_coordination_context`, extended `_has_dedicated_support`), `marshal.py` (+`reinforced_this_turn`), `world_state.py` (turn-start clearing).
- **Files created:** `tests/test_reinforcement.py` (49 tests across 12 classes).
- **Regression fixes:** 3 existing integration tests needed isolation from reinforcement side effects (reinforcement pulls adjacent marshals during AI attacks). Fixed by marking test-specific marshals as `reinforced_this_turn = True` or relocating enemies.

### Feb 23 — Session 60: Adjacent Support

**23 new tests, 3495 total (3 skipped). Adjacent-region coordination bonus (attack-only).**

- **Adjacent support bonus:** Marshals in regions adjacent to a battle provide +2% attack per ally. Purely positional — NOT relationship-scaled. Fortified and HOLD marshals count (physically present). Same eligibility as coordination (not broken, not retreating, not recovering, strength > 0).
- **Attack-only (A-M2):** Adjacent support adds to `raw_atk` ONLY. Defenders benefit only from same-region allies, not adjacent ones.
- **Pipeline integration:** `_count_adjacent_allies()` calculates ONCE per battle (shared value for all marshals in region), added to coordination sum BEFORE hard cap. Display field `_display_adjacent_atk` set on all eligible marshals, already in `COORDINATION_FIELDS` cleanup list.
- **Future-proofing (S61):** `exclude_names` parameter on `_count_adjacent_allies()` for Session 61 reinforcement (arriving marshals removed from adjacent count).
- **Combat message:** Adjacent support displays in tactical prefix when active.
- **Battle report:** `_display_adjacent_atk` captured in attacker snapshot as "Adjacent support" modifier.
- **Files modified:** `executor.py` (+`_count_adjacent_allies`, extended `_calculate_coordination_context`), `combat.py` (adjacent support message), `battle_report.py` (adjacent support snapshot).
- **Files created:** `tests/test_adjacent_support.py` (23 tests across 7 test classes).

### Feb 23 — Session 59: Dedicated Coordination

**31 new tests, 3472 total (3 skipped). Co-location tracking + dedicated coordination bonus.**

- **Co-location tracking:** `_update_co_location_tracking()` in `world_state.py` runs per-turn BEFORE turn increment (A-D7). Tracks `co_location_turns` dict on each marshal: ally_name → start_turn of co-location streak. Clears on separation, death, or broken status.
- **Dedicated bonus (Path A):** After 2+ consecutive co-located turns (`current_turn - start_turn >= 2`), marshal earns flat +5% attack / +5% defense. Doesn't scale with relationship or stack with multiple qualifying allies.
- **Dedicated bonus (Path B):** Active SUPPORT order targeting a marshal grants immediate +5%/+5%. One-directional per A-D3 — only the target gets the bonus, not the supporter. Mutual SUPPORT (4 AP) gives both.
- **Pipeline integration:** Dedicated bonus added to raw sum in `_calculate_coordination_context()` (combined arms + per-ally + dedicated), then hard-capped at +25% atk / +20% def. Display fields `_display_dedicated_atk`/`_display_dedicated_def` set on marshal, already in cleanup list.
- **Forward-compatibility field:** `last_relationship_change_turn` dict added to marshal (empty until Session 64 populates it). Serialization-enforced.
- **Files modified:** `marshal.py` (2 new Dict fields in `__init__`/`to_dict`/`from_dict`), `world_state.py` (+`_update_co_location_tracking`, call site in `_process_tactical_states`), `executor.py` (+`_has_dedicated_support`, extended `_calculate_coordination_context`), `tests/test_serialization_enforcement.py` (fixture updated).
- **Files created:** `tests/test_dedicated_coordination.py` (31 tests across 8 test classes).

### Feb 23 — Session 58: Per-Ally Coordination Bonuses

**44 new tests, 3438 total (3 skipped). Per-ally relationship-scaled coordination.**

- **Per-ally coordination:** Each eligible ally contributes +3% attack / +5% defense, scaled by relationship: Hostile(0.0) → Rival(0.5) → Professional(1.0) → Friendly(1.25) → Devoted(1.5). Asymmetric — each marshal gets their OWN total based on their relationships.
- **Fortification rule:** Fortified non-artillery allies give defense coordination only (0% attack). Fortified artillery gives both.
- **Hard cap enforced:** Combined arms + per-ally coordination summed, then capped at +25% attack / +20% defense. 3/3 France CA (20%) + 2 Professional allies (6%) = 26% → capped at 25%.
- **S57 tests updated:** 4 tests updated to account for per-ally coordination being additive with combined arms.
- **Files modified:** `executor.py` (+`_calculate_per_ally_coordination`, `_RELATIONSHIP_SCALING`, extended `_calculate_coordination_context` for per-marshal asymmetric calculation), `tests/test_combined_arms.py` (4 updated tests).
- **Files created:** `tests/test_coordination_bonus.py` (44 tests across 11 test classes).

### Feb 23 — Session 57: Combined Arms Detection

**43 new tests, 3394 total (3 skipped). Phase 7 Core begins.**

- **Combined arms detection:** Count distinct unit types (infantry/cavalry/artillery) among eligible same-nation marshals in a region. 2 types = +10% atk / +5% def. 3 types = +20% atk / +10% def. France is the only nation capable of 3/3 (structural player advantage).
- **Transient field pattern (D5):** Coordination bonuses set dynamically via `_calculate_coordination_context()`, read via `getattr(self, field, 0.0)`, cleared after combat. NOT in `__init__`, NOT serialized.
- **Single multiplier (A-C1):** `total_coordination_attack_bonus` / `total_coordination_defense_bonus` — one line each in `get_attack_modifier()` / `get_defense_modifier()`. All future coordination sources (per-ally, dedicated, adjacent) sum into this single field, then cap at +25% atk / +20% def.
- **Both sides calculated (A-C3):** `_calculate_coordination_context()` called for attacker AND defender independently before `resolve_battle()`.
- **Bombardment excluded (A-D6):** Coordination not wired into bombardment path.
- **Files modified:** `executor.py` (+`_count_unit_types`, `_get_combined_arms_bonus`, `_calculate_coordination_context`, `_clear_coordination_fields`, attack wiring), `marshal.py` (1 line each in atk/def modifiers), `combat.py` (combined arms tactical_prefix message), `battle_report.py` (snapshot captures CA + total coordination).
- **Files created:** `tests/test_combined_arms.py` (43 tests across 8 test classes).

---

## Phase 6.5 Sessions

### Feb 22 (Davout Counter-Punch Mastery + Special Abilities Evaluation)

**Davout's "Counter-Punch Mastery" ability wired. 22 new tests, 3351 total.**

- **Ability:** +20% attack on next attack after Davout is attacked (any combat outcome, any target). Boolean `counter_punch_ready` field — set when defender in combat (if survived), consumed on next `get_attack_modifier()` call, cleared at turn end if unused.
- **Files modified:** `marshal.py` (field + ability definition + modifier), `combat.py` (trigger + result flag), `battle_report.py` (snapshot label), `marshal_overview.py` (`_WIRED_ABILITY_MARSHALS` + unit specifics), `world_state.py` (turn-end clearing + game state summary), `executor.py` (broken state clearing).
- **6 wired abilities total:** Ney (+2 shock), Davout (+20% counter-punch), Drouot (15% fort degradation), Wellington (+5% defense), Blucher (+3k pursuit), Uxbridge (+5k pursuit).
- **Special Abilities Evaluation complete:** `docs/SPECIAL_ABILITIES_EVALUATION.md` — 3 Davout designs proposed, existing abilities reviewed (all balanced for Phase 7), UI surface audit (5 manual / 6 auto), 1805 roster planning principles and candidate lists documented.
- **ADDING_CONTENT.md expanded:** "Wiring a Special Ability" 16-step checklist, common mistakes table, file audit.

---

### Feb 22 (Phase 6.5 UI Audit)

**Code quality audit of all Phase 6.5 menu systems. 9 new tests, 1 pre-existing fix, 3354 total.**

- **Audit scope:** Pause Menu, Campaign Log, Morning Dispatch, Notification Bar, Top Bar, Strategic Ledger, Marshal Management. Checked int() wrapping, serialization, input blocking, CanvasLayer ordering, edge cases, endpoints, test coverage, consistency.
- **Fixes (bugs):** `/campaign_log` endpoint missing `"success"` key + game state guard. `GET /notifications` missing game state guard. `test_marshal_overview.py::test_endpoint_no_game_returns_error` called `game_state.clear()` without restore, poisoning subsequent tests (caused pre-existing `test_recklessness_2_blocks_defensive_stance` failure).
- **Fixes (comments):** `campaign_log.gd` layer comment corrected (102 -> 50).
- **New tests:** 5 endpoint tests for `/campaign_log`, 4 endpoint tests for `/notifications`.
- **Tech debt documented:** `_format_number()` duplication (3 files), color palette duplication (3+ files), marshal scroll hardcoded 320px/card. All tagged for Map Renderer refactor. Added to ROADMAP.md Tech Debt table.
- **Hooks fix:** `.claude/settings.local.json` PostToolUse/PreToolUse hooks had bash `$(...)` quoting bug with nested Python parentheses — split into variable assignments.

---

### Feb 21 (Marshal Management UI)

**Card-based read-only marshal management screen. 68 new tests, 3320 total.**

- `backend/game_logic/marshal_overview.py` — `build_marshal_overview(world)` returns per-marshal data cards (identity, ability, combat stats, trust/standing, status, unit specifics, relationships). All values int()-wrapped.
- `backend/models/marshal.py` — `biography` field added to `__init__`, `to_dict()`, `from_dict()`. Historical blurbs set for all 9 marshals (Berthier's voice).
- `marshal_management.gd/tscn` — CanvasLayer 50, vertical scrollable card list, BBCode rendering, number keys 1-N jump to marshal.
- `main.py`: `GET /marshal_overview` endpoint.
- `api_client.gd`: `get_marshal_overview()` method.
- `top_bar.gd`: Generals button enabled, wired to marshal management screen.
- `main.gd`: Marshal management scene loaded and registered with top bar.
- Ability active derivation hardcoded by name (Ney/Drouot/Wellington/Blucher/Uxbridge = active). TODO: Replace with proper `Marshal.ability_wired` field (Phase 7b or Pre-EA).

---

### Feb 21 (Session B: Strategic Ledger)

**5-section strategic ledger backend + sub-tabbed Godot screen. 54 new tests, 3252 total.**

- `backend/game_logic/ledger.py` — forces, territories, economy, intel, manpower sections. Fog-filtered intel. `BAND_MIDPOINTS` for estimated strength.
- `strategic_ledger.gd/tscn` — CanvasLayer 50, 5 sub-tabs (number keys 1-5), color coding.
- `world_state.py`: `get_manpower_regen_rates(nation)` extracted as single source of truth.
- `main.py`: `GET /ledger` endpoint.

---

### Feb 21 (Session A: Top Bar Framework + Dispatch)

**Unified top bar UI framework. 8 new tests, 3198 total.**

- `top_bar.gd/tscn` — CanvasLayer 75 controller (Event Log, Ledger, Generals, Dispatch), notification area, turn counter.
- `dispatch_view.gd/tscn` — CanvasLayer 50 dispatch re-read (D key). `last_morning_dispatch` stored on WorldState.
- Campaign log refactored to layer 50, notification bar reparented into top bar.
- Input refactor: `_is_modal_dialog_open()`, `_is_screen_open()`, `_is_hotkey_blocked()`.
- Hotkeys: L (Event Log), T (Ledger), G (Generals placeholder), D (Dispatch).

---

### Feb 21 (Notification System + Audit)

**EU4-style persistent notification bar. 9 triggers, 3 priority tiers. 70 tests total (51 + 19 audit).**

- `backend/notifications.py` — NotificationCollector, 10 notification types, priority enum.
- `notification_bar.gd/tscn` — color-coded icons, expand/dismiss, backend sync.
- 9 triggers: strategic complete, forced retreat, friendly fire, reckless cavalry, counter-punch, manpower, elimination, bankruptcy, drill cancelled.
- Audit fixes: whitelist mismatch, missing passthrough (3 endpoints), accumulation prevention, auto-dismiss.

### Feb 20 (Morning Dispatch)

**Berthier's Morning Dispatch: structured turn-start briefing. 57 new tests, 3120 total.**

- `backend/game_logic/dispatch.py` — SITUATION, MARSHAL STATUS, INTELLIGENCE, Berthier note.
- Fog-filtered enemy strength ratio. Tactical events absorbed into dispatch. Both end-turn paths wired.

### Feb 20 (Campaign Log + Polish)

**Fog-filtered campaign event log with Godot overlay. 57 tests.**

- `backend/campaign_log.py` — 14-type whitelist, fog filter, one-liner formatter.
- `campaign_log.gd/tscn` — CanvasLayer overlay, turn-grouped expandable sections, L key toggle.
- Polish: nation tags on names, both-sides casualties, expand/collapse fix, empty turn hiding.

### Feb 20 (Wire Marshal Abilities + Phase 7 Prep)

- Drouot 15% fort degradation, Wellington +5% defense, Blucher 3k pursuit, Uxbridge 5k pursuit.
- Phase 7 pre-implementation audit: 20 findings (3 critical, 7 design gaps). `PHASE7_SPEC_AMENDMENTS.md` created.
- Phase 7 scoped to 6-session Core + deferred 7b.

### Feb 19 (Session 56: Pause Menu)

- Smart Esc pause menu overlay (CanvasLayer 101). Save/Load/Settings stub/Quit.

---

## Known Issues

| Issue | Severity | Notes |
|-------|----------|-------|
| V1 global objection cap still active for strategic path | Low | `disobedience.py:25` MAX_MAJOR_OBJECTIONS_PER_TURN=2. Remove in V2b cleanup. |
| No mid-objection save/load roundtrip test | Low | Serialization enforcement confirms fields exist, but no test with populated V2 pending_objection. |
| Missing AI test coverage for P3, P4.75, P7 | Medium | P3 (threat response), P4.75 (ally support), P7 (strategic movement) have zero direct unit tests. |
| Residual 2-turn fortify oscillation possible | Low | `_unfortified_this_turn` only prevents same-turn re-fortify. Stagnation counter is backstop. |
| `requires_input` interrupt blocks later marshals | Low | `strategic.py:119` stops processing ALL further marshals when one requires input. |
| `full_game.py` dead code with stale terrain | Low | 3 `resolve_battle()` calls hardcode `terrain="open"`. File is dead code. |
| France hardcoded as player nation | Low | Multiple systems assume France. Post-EA multi-nation play requires threading player_nation. |
| `ability_active` hardcoded by marshal name | Low | `marshal_overview.py` derives ability_active from `_WIRED_ABILITY_MARSHALS` set. Replace with proper `Marshal.ability_wired` field. Pre-EA or Phase 7b. |
| `resolve_battle()` has 5 categories of side effects | High | Phase 7 `apply_casualties=False` must defer all 5. See `PHASE7_SPEC_AMENDMENTS.md` C1. |
| Cross-nation coordination impossible (Britain/Prussia) | Medium | Deferred to Phase 7b with Coalition Trigger. See `PHASE7_SPEC_AMENDMENTS.md` C3. |
| Missing SUPPORT objection triggers | Low | Add in Phase 7 Session 59. |

---

## Quick Commands

```bash
pytest tests/ -v                          # Full suite
pytest tests/ -v --tb=no -q              # Quick count
pytest tests/test_objection_v2.py -v     # V2 tests only
python backend/main.py                    # Backend on port 8005
```

---

## Document Map

| Need | Read |
|------|------|
| Phase timeline | `ROADMAP.md` |
| Phase 7 spec | `MULTI_MARSHAL_SPEC.md` |
| Phase 7 audit amendments | `PHASE7_SPEC_AMENDMENTS.md` |
| Game systems reference | `SYSTEMS_REFERENCE.md` |
| Enemy AI | `ENEMY_AI_REFERENCE.md` |
| V2b objection preview | `OBJECTION_V2.md` |
| Save format | `SAVE_FORMAT_REFERENCE.md` |
| Fog of war spec | `FOG_OF_WAR_SPEC.md` |
| Adding content | `ADDING_CONTENT.md` |
| Game vision | `VISION.md` |
| Future concepts | `FUTURE_DESIGN.md` |
| Modding | `MODDING_FORMAT.md` |
| Manual testing | `MANUAL_TEST_PLAN.md` |
| Tutorial content | `TUTORIAL_SCRIPT.md` |
| Playtest prompt | `PLAYTEST_EVALUATION_PROMPT.md` |
| Session history (archived) | `archive/SESSION_HISTORY.md` |
