# GPT Audit Results

Audit date: 2026-04-10

Scope: full synthesis across gameplay/design, architecture/contracts, tests/regression coverage, and full-map scalability.

## Baseline Snapshot

- Branch: `master`
- Commit audited: `c965e6478afa7532e9708d9b5d0365d656eb0ccf`
- Tree state: dirty; this audit covers current local code plus uncommitted changes, not just clean `HEAD`
- `docs/STATUS.md` claims 8,093 passing tests and labels bug-fix status "ALL CLEAR" as of 2026-04-09
- `docs/ROADMAP.md` still treats the map renderer as the major remaining pre-expansion blocker

## Method

- Code inspection of the main gameplay, diplomacy, world-state, turn, AI, API, and Godot control layers
- Targeted backend command probes using the local mock parser/executor
- Representative regression suites, including reruns outside the sandbox for file-system tests
- Cross-checks against current docs, but docs were treated as hypotheses, not truth

## Execution Evidence

Targeted test runs:

- `tests/test_playtest_2026_03.py tests/test_playtest_bugfixes.py tests/test_playtest_bugfixes_2.py` -> `71 passed`
- `tests/test_response_pipeline.py tests/test_endpoint_wiring.py tests/test_phase4_batch5_popups.py tests/test_session8b_ledger_ui.py tests/test_fog_endpoint_filters.py tests/test_dialogue_manager.py tests/test_strategic_ui_comprehensive.py` -> `301 passed`
- `tests/test_save_load.py tests/test_serialization.py tests/test_serialization_enforcement.py tests/test_map_consistency.py tests/test_world_state_strategic.py tests/test_enemy_ai.py` -> `200 passed` outside sandbox
- `tests/test_modding_validator.py` -> `32 passed` outside sandbox

Total directly verified in this audit: `604 passed`.

Environment caveat:

- In-sandbox `pytest` cache and temp-dir creation were denied by Windows permissions, so file-based suites had to be rerun outside the sandbox to separate harness noise from real failures.

Manual command probes:

- `recruit infantry at Paris` parsed cleanly without a marshal name, auto-selected Davout, and returned a high-signal result with capital discount, morale change, and manpower-pool update.
- `Ney, defend Belgium` produced a clear major objection with explicit Trust/Insist tradeoffs and a suggested alternative (`attack Wellington`).
- `Ney, attack Wellington` produced a readable but punishing opener: 50k Ney vs 38k Wellington still ended in a costly stalemate because hills, cautious outnumbered bonus, combined arms, and adjacent support all stacked before the game taught the counters.
- `Talleyrand, propose peace to Prussia` entered a structured `proposal_confirm` dialogue with actionable options instead of blind commitment.

Direct bug reproduction:

- Setting `world.regions["Paris"].controller = "Prussia"` still makes `TurnManager._check_victory_conditions()` return `{"game_over": True, "result": "defeat", "reason": "Your capital has fallen!"}`.
- The regression test intended to prove that capital loss was removed looks up `Ile-de-France`, which is not a real region key.

## Executive Verdict

1. Is the game already compelling?
   Promising but obscured. The command loop, objections, and diplomacy framing are distinctive. The current balance and pacing still hide that strength behind avoidable friction.

2. Is the design direction sound?
   Yes, mostly. The Napoleonic command fantasy is coherent. The weak points are diplomacy branching, onboarding of combat counterplay, and one unfair defeat rule that contradicts the stated direction.

3. Is the codebase organized enough to keep shipping?
   Yes for the current 19-region scope, but only as "fragile but manageable." Backend contracts and serialization are much healthier than before; `backend/main.py`, `godot-client/project-sovereign/scripts/main.gd`, and `godot-client/project-sovereign/scenes/map.gd` remain the main regression chokepoints.

4. Is the project structurally ready for full-map growth?
   No. The current renderer, omniscient AI queries, and remaining hardcoded nation/map assumptions make an 80-100 region push reckless without another hardening pass.

## Findings

### 1. Critical - bug + design flaw
Capital capture still causes instant defeat, despite the current docs and regression test claiming that rule was removed.

Evidence:

- `backend/game_logic/turn_manager.py:836-845`
- `tests/test_playtest_bugfixes.py:52-74`
- `backend/models/region.py:504`
- Direct audit reproduction returned `Your capital has fallen!`

Why this matters:

- This is a fairness and fantasy issue, not just a bookkeeping bug.
- The game says land can change hands through diplomacy, but the defeat rule still hard-loses on capital loss.
- `docs/STATUS.md` calling bug-fix status "ALL CLEAR" is currently false on a core rule.

Smallest structural fix:

- Remove the capital-capture defeat branch or replace it with a softer rule tied to total military collapse.
- Fix the regression test to target `Paris`, not `Ile-de-France`.

### 2. Critical - future scaling risk
The current map layer is still a 19-region prototype renderer with manual drawing, manual adjacency, and circle-distance hit-testing.

Evidence:

- `godot-client/project-sovereign/scenes/map.gd:3-23`
- `godot-client/project-sovereign/scenes/map.gd:152-218`
- `godot-client/project-sovereign/scenes/map.gd:490-500`
- `docs/ROADMAP.md` already treats map renderer replacement as the intended path

Why this matters:

- This is fine for a prototype board-map, not for a Europe-scale province map.
- The current implementation hardcodes pixel positions, connection lines, draw loops, and click radii.
- Expanding to 80-100 regions before replacing this layer would multiply UI clutter, maintenance overhead, and input ambiguity.

Smallest structural fix:

- Treat the bitmap/province renderer as a hard gate before full-map wiring starts.

### 3. Major - architecture risk + fun killer
Modal dialogue and popup responses still route through the parser path too often, which adds friction for the player and brittleness for the contract.

Evidence:

- `backend/main.py:578-638`
- `godot-client/project-sovereign/scripts/main.gd:2714-2828`
- Typed dialogue endpoint already exists at `backend/main.py:1142-1186`

Why this matters:

- A modal response like `accept`, `reject`, or `dismiss` should be cheap and deterministic.
- Right now the backend still parses the raw text first, then checks whether it should have been treated as a dialogue response.
- Several Godot handlers still synthesize English commands instead of sending typed option ids.

Player impact:

- This makes diplomacy feel more interruptive than it should.
- It turns some UI clicks back into text parsing instead of a clean state-machine transition.

Smallest structural fix:

- Route pending dialogue and interrupt responses before parser invocation.
- Move the remaining popup handlers onto `/respond_to_diplomatic_dialogue` or an equivalent typed endpoint.

### 4. Major - architecture risk
Response construction and popup delivery are better than before, but the hottest path still bypasses the clean abstraction.

Evidence:

- Central builder: `backend/main.py:141-237`
- Manual `/command` payload assembly: `backend/main.py:808-1008`
- Popup flush workaround in turn manager: `backend/game_logic/turn_manager.py:264-289`
- Godot routing chain: `godot-client/project-sovereign/scripts/main.gd:597-760`

Why this matters:

- `build_base_response()` is real progress.
- But `/command` still reconstructs a large response object manually, so popup passthroughs, top-bar fields, and edge-case exceptions are not fully owned in one place.
- `main.gd` still contains the real modal ordering policy, even with `DialogManager`.

Smallest structural fix:

- Make `/command` start from `build_base_response()` and layer special sections on top.
- Move popup priority/routing policy out of the `main.gd` early-return chain and into a registry-driven handler.

### 5. Major - future scaling risk
The AI and some nation/map systems still assume a small fixed world.

Evidence:

- Omniscient AI query: `backend/models/world_state.py:1514-1550`
- Current AI call sites: `backend/ai/enemy_ai.py:1764-1779`, `backend/ai/enemy_ai.py:4215-4228`
- Hardcoded coastal-income set: `backend/models/world_state.py:2420-2428`
- Hardcoded nation defaults on load: `backend/models/world_state.py:3267-3268`
- Hardcoded nation action reset: `backend/models/world_state.py:4180-4187`
- Fixed nation list in vassal logic: `backend/main.py:2262-2268`

Why this matters:

- At 19 regions, omniscient AI is tolerable and even useful.
- At 80+ regions it becomes both unfair and expensive.
- Hardcoded nation defaults are survivable now, but they are exactly the kind of quiet assumption that makes expansion brittle.

Smallest structural fix:

- Replace scale-sensitive AI calls with fog-aware helper surfaces before the full-map branch.
- Move nation defaults and nation capability config into data, not inline dict literals.

### 6. Major - design flaw
Diplomacy is still strategically flatter than it should be because the player-facing alliance layer lacks rivalry or exclusivity pressure.

Evidence:

- Upgrade path and relation/DP gating exist in `backend/game_logic/diplomacy.py:19-63`
- Available alliance upgrades remain straightforward in `backend/game_logic/diplomacy.py:2908-2934`
- `docs/DESIGN_REFINEMENT.md:79-93` documents an already-observed playtest problem: France can befriend nearly everyone without real branching cost

Why this matters:

- Diplomacy has lots of surface area, but not enough forced choice.
- The result is a system that can become a one-way ramp toward "ally everyone" instead of a layer of strategic commitments.

Confidence note:

- This is partly inference from current rules plus the already-recorded playtest note in `docs/DESIGN_REFINEMENT.md`.
- I did not run a full long-form diplomacy campaign slice in Godot for this audit.

Smallest structural fix:

- Add rivalry/exclusion pressure or alliance-cap tradeoffs before treating diplomacy as strategically complete.

### 7. Moderate - design flaw
Combat depth is real, but the current opener teaches the wrong lesson.

Evidence:

- Manual audit probe: Ney 50k vs Wellington 38k at Waterloo ended in a costly stalemate
- Modifier surfacing: `backend/game_logic/combat.py:55-64`
- Wellington passive defense note: `backend/game_logic/combat.py:237-242`
- Cautious outnumbered bonus text: `backend/game_logic/combat.py:471-478`
- Stalemate narrative: `backend/game_logic/combat.py:1009-1013`

Why this matters:

- The combat system is not shallow; it is under-explained.
- The obvious "Ney attacks Wellington" fantasy produces heavy losses before the player learns bombardment, coordination, and better setup play.
- That makes the game feel harsher and less legible than it probably is.

Smallest structural fix:

- Add stronger early guidance around bombardment/coordination counters.
- Revisit the exact defender stack in the common Waterloo opener.

### 8. Moderate - test/scaling risk
The suite is very strong on backend correctness, but it does not prove full-map readiness or long-session fun.

Evidence:

- Contract and response coverage: `tests/test_response_pipeline.py`, `tests/test_endpoint_wiring.py`, `tests/test_fog_endpoint_filters.py`
- Serialization enforcement: `tests/test_serialization_enforcement.py`
- Map drift guard: `tests/test_map_consistency.py`
- Modding validator coverage: `tests/test_modding_validator.py`
- Validator scope remains structural, not systemic: `backend/modding/validator.py:342-431`

Why this matters:

- The project is well-defended against many regression classes.
- It is not yet defended against large-map UX collapse, nation-config completeness, or performance regressions under 80-100 regions.

Smallest structural fix:

- Add pre-expansion enforcement around nation config completeness, scenario/nation invariants, and large-map assumptions.

### 9. Note - documentation drift
Some historical audit docs are now stale enough to mislead.

Evidence:

- `docs/ARCHITECTURE_AUDIT_REPORT.md` still describes missing `conftest.py` and weaker endpoint coverage
- Current tree has `tests/conftest.py` plus large endpoint/contract suites

Why this matters:

- Historical audits are still useful, but they should no longer be treated as a current-state summary.

## Fun and Design

### Top 5 fun strengths

1. The typed command loop already feels distinct from standard strategy UI. The game answers in-character and mechanically at the same time.
2. Marshal objections create memorable, character-driven friction when they are attached to a visible alternative.
3. Combat feedback is richer than the average prototype. The battle text names stance, terrain, combined arms, support, and casualties.
4. Diplomacy has real conversational texture. Entering a proposal gives a structured preview instead of a blind yes/no.
5. The game has good "people, not counters" energy. Orders, objections, and reports consistently keep named actors at the center.

### Top 5 fun killers

1. The capital-loss defeat rule is unfair and contradicts the rest of the design.
2. Modal diplomacy still interrupts the operational loop too aggressively.
3. The obvious early Waterloo attack is punishing before the game teaches the counters.
4. Some routine orders still generate too much process friction for the payoff they deliver.
5. Diplomacy currently offers too little strategic branching once the player realizes broad friendship is cheap.

### 3 memorable emergent play examples

1. Direct probe: `Ney, defend Belgium` became a personality clash instead of a dead command. Ney objected and explicitly pushed the player toward attacking Wellington.
2. Direct probe: `Ney, attack Wellington` surfaced a specific battle story - aggressive assault, hills, cautious resistance, adjacent support, and Uxbridge withdrawing after the fight.
3. Code/test-verified: the alliance-paradox path can force a real diplomatic dilemma where honoring one alliance breaks another (`backend/game_logic/diplomacy.py:1211-1415`).

### 3 places where the game asks too much effort for too little payoff

1. A basic modal response can still round-trip through parser keywords instead of a typed dialogue action.
2. A plain defensive instruction to an aggressive marshal can become a full objection loop even when the player is just trying to stabilize the front.
3. The current early-combat lesson asks the player to absorb several hidden counters before they get a satisfying win state.

### Keep / Tune / Rethink / Cut

- Keep: core command loop
- Keep: marshal personality / objection fantasy
- Keep: structured diplomacy proposal flow
- Keep: fog-filtered information surfaces and dispatch/ledger direction
- Tune: combat onboarding and common-opening balance
- Tune: diplomacy pacing and interruption frequency
- Tune: long-term diplomatic branching pressure
- Tune: 1805 economy/action scaling later
- Rethink: capital-loss defeat
- Rethink: parser-first modal response routing
- Rethink: current map renderer as an expansion foundation
- Cut: nothing yet; this is a tuning/refactoring problem more than a removal problem

### Fun verdict

Promising but obscured.

The game already has a distinctive identity and several genuinely interesting beats. The problem is not "structurally unfun." The problem is that some of the first and loudest experiences are either unfair (capital defeat), interruptive (modal diplomacy), or misleading (the early Wellington fight), so the fun is easier to miss than it should be.

## Architecture and Code Health

### Subsystem ratings

| Subsystem | Rating | Notes |
| --- | --- | --- |
| `backend/main.py` response pipeline | Fragile but manageable | Stronger than before, still partially bespoke on `/command` |
| `backend/models/world_state.py` | Fragile but manageable | Centralized and heavily tested, but overloaded |
| `backend/game_logic/turn_manager.py` | Fragile but manageable | Works, but still carries response/popup escape hatches |
| `backend/ai/enemy_ai.py` | Fragile but manageable now / likely to regress at scale | Golden Rule compliance is good, omniscience is the risk |
| `godot-client/project-sovereign/scripts/main.gd` | Likely to regress | Still the real popup/state router |
| `godot-client/project-sovereign/scenes/map.gd` | Likely to regress | Prototype renderer, not an expansion seam |
| Serialization + save/load | Safe to extend | Strong enforcement and direct test proof |

### Highest-leverage structural improvements still worth doing

1. Remove or redesign capital-loss defeat and fix the false-negative regression test.
2. Route dialogue/interrupt responses before parser invocation and stop synthesizing English commands from popup buttons.
3. Put `/command` on the same response-construction abstraction as the rest of the API.
4. Replace `map.gd` before full-map work, not during late expansion panic.
5. Move AI/nation defaults toward data-driven config and fog-aware query surfaces.

## Backend / Frontend Contract Audit

Current hotspots:

- `backend/main.py:578-638` - parser-first dialogue routing
- `backend/main.py:808-1008` - manual `/command` response assembly
- `backend/game_logic/turn_manager.py:264-289` - popup flush workaround
- `godot-client/project-sovereign/scripts/main.gd:597-760` - ordered popup-routing chain
- `godot-client/project-sovereign/scripts/main.gd:2714-2828` - mixed typed and stringly dialogue handlers

Current assessment:

- Backend response shape is much more centralized than it used to be.
- Important gameplay state generally reaches Godot consistently.
- The remaining fragility is in modal routing and popup/button response handling, not in basic data transport.

Recommendations before more UI/map work lands:

1. Make typed dialogue responses the default for every modal path.
2. Reduce the number of response fields that `/command` assembles manually.
3. Move popup priority rules into data/registry form so a new popup does not require editing the same giant handler chain.

## Test and Regression Audit

### Well protected

- Response wiring and top-bar/popup contract shape
- Fog filtering
- Serialization completeness
- Save/load roundtrip behavior
- Core enemy AI behaviors
- Backend/Godot map adjacency drift
- Modding validator structure checks

### Still underprotected

- The specific capital-loss defeat rule vs. the intended design
- Full-map nation-config completeness
- Large-map performance
- Long-session pacing and diplomacy interruption burden
- Player-facing strategic branching quality in diplomacy

### Missing high-value regression tests

1. A direct `Paris` capital-loss test that asserts the intended non-defeat behavior if that design remains the goal.
2. A pre-expansion config test that fails when a new nation is added without all required defaults/actions/capitals/income hooks.
3. A typed-dialogue-endpoint coverage pass for every popup choice path still using `send_command`.
4. A large-scenario validation test that checks nation counts, capital presence, and action/economy config completeness together.

### Suite verdict

Broad and fairly deep for backend correctness.

This is not a misleadingly large suite. It catches a lot of real regressions. It is still backend-heavy, and it does not by itself prove that the game is fun or that the 80-100 region branch is safe.

## Full-Map Scalability Audit

### Safe now

- Region data centralization in `backend/models/region.py`
- Dynamic victory thresholds in `backend/game_logic/turn_manager.py:742`, `backend/game_logic/turn_manager.py:867`
- Fog-filtered game-state projection in `backend/models/world_state.py:3672-3804`
- Strong serialization discipline and save/load coverage

### Fix before full map

- Replace `godot-client/project-sovereign/scenes/map.gd`
- Remove omniscient AI dependence from scale-sensitive paths
- Eliminate inline nation/coastal/action defaults
- Finish typed modal-response routing
- Sequence the renderer cutover correctly: define the bitmap/color-map contract first, build the replacement renderer against placeholder or partial assets, port the current 19-region content onto that renderer, and only then begin 80-100 province wiring.

### Fix during full-map implementation

- Better filtering/summarization/minimap support for 30 marshals and 8 nations
- Batch content-entry tooling and nation-config validation
- Performance profiling for turn processing, visibility, and rendering

### Defer until playtesting

- Exact 1805 economy/AP rebalance
- Final strength of AI fog bonuses
- Final alliance/rival tension numbers

### Pre-expansion checklist

1. Ship the planned province-map renderer.
2. Convert AI strategic queries to fog-aware helpers where scale matters.
3. Move nation defaults into data-backed config.
4. Add config-completeness tests for new nations and large scenarios.
5. Decide the actual defeat rule and align tests/docs with it.
6. Preserve `update_all_regions(map_data)` while swapping the renderer so the migration can happen before full-map content exists.

### No-go list

- Do not start wiring 80-100 regions on top of the current circle-map renderer.
- Do not keep omniscient AI once the map is large enough for fog to matter strategically.
- Do not trust the current "capital-loss removed" claim until code and tests are aligned.
- Do not add more popup/button flows through synthesized English commands.

## Priority Roadmap

### Fix now

1. Remove or redesign capital-loss defeat and repair the broken regression test.
2. Move modal dialogue handling ahead of parser invocation.
3. Finish the typed popup-response migration.

### Before full-map implementation

1. Replace `map.gd` on the current 19-region map or a partial placeholder map, not after 80-100 provinces are already wired.
2. Lock the bitmap/color-map definition format so art, hit detection, and anchor placement all target one stable contract.
3. Keep `update_all_regions(map_data)` stable while the renderer is swapped underneath it.
4. Remove omniscient AI paths and hardcoded nation/map assumptions before the map scale makes them expensive to unwind.

### Tune via playtesting

1. Rebalance or better tutorialize the Ney -> Wellington opener.
2. Add strategic tension to alliance-building.
3. Reduce diplomacy interruption burden during the core campaign loop.

### Defer until full-map implementation starts

1. Large-map UX layers (minimap/filtering/summaries)
2. 1805 economy/action rebalance
3. Final AI fog tuning

## Confidence Statement

Directly verified in this audit:

- Branch/commit/tree state
- Targeted test results listed above
- Capital-loss defeat still active in code
- Current parser/executor command flow for recruit, objection, combat, and diplomacy entry
- Current response/popup routing structure
- Current map renderer and scaling assumptions in code

Inference rather than direct full-session proof:

- Long-session turn-to-turn fun in the full Godot client
- Exact frequency at which alliance flattening breaks campaign tension in practice
- Exact 80-100 region performance cost on the final renderer

## Ship-Readiness Verdict

### Current 19-region version

Playable, distinctive, and more structurally solid than the historical audit docs suggest.

Not ready to be called "all clear." The capital-loss defeat bug alone blocks that claim, and the current pacing/contract friction still obscures the game's strongest qualities.

### Future 80-100 region expansion

Not structurally ready.

The no-go blockers are the map renderer, omniscient AI at scale, and remaining hardcoded nation/map assumptions. Full-map implementation should not start in earnest until those are addressed.

## Focused Follow-Up Addendum

Audit date: 2026-04-10

Scope: first-hour experience, PL-26 combat clarity, PL-27 diplomacy pacing/modal burden, PL-28 defeat-state clarity, and enemy AI gameplay/organization.

### Baseline Snapshot

- Branch: `master`
- Commit audited: `71162d88b88be0b8831088fc182bc2e70326da7b`
- Tree state: dirty; this follow-up audited the current local working tree
- `docs/STATUS.md` still claims 8,093 passing tests

### Additional Execution Evidence

Focused probes:

- `help` returned a strong, high-signal command reference.
- `status` still failed as an obvious first-hour command and fell through to Berthier recovery.
- `economy` returned a clear treasury/income/upkeep/manpower breakdown.
- `recruit infantry at Paris` remained a strong teaching moment.
- `Ney, defend Belgium` raised a clear objection with a suggested alternative, but also blocked unrelated later commands until resolved.
- `Talleyrand, propose peace with Prussia` entered a structured `proposal_confirm` flow correctly.
- A 7-turn passive probe still produced 3 incoming AI proposals, confirming that proposal delivery remains interruptive even with anti-spam logic present.

Focused tests:

- `tests/test_playtest_bugfixes.py::TestCapitalLossNotDefeat::test_capital_loss_does_not_end_game` -> passed, but still targets `Ile-de-France` rather than `Paris`
- `tests/test_enemy_ai.py::TestAttackThresholds::*` and `tests/test_enemy_ai_behavior.py::TestMultiTurnIntegration::test_graduated_escalation_lowers_threshold_at_turn3` -> passed
- `tests/test_dialogue_manager.py` -> passed

### Follow-Up Findings

#### 1. Capital-loss defeat is still live, and the project should at minimum make loss/win logic consistent before the real map rewrite

Evidence:

- `backend/game_logic/turn_manager.py:803-845`
- `tests/test_playtest_bugfixes.py:52-70`
- Direct probe: setting `world.regions["Paris"].controller = "Prussia"` still returned `Your capital has fallen!`

Clarification:

- This can be redesigned further once the real map and final victory model exist.
- The immediate need is consistency: code, tests, and docs should stop disagreeing about whether capital loss is fatal.

Recommended short-term direction:

- Remove the instant capital-loss defeat for now, or stop claiming it was removed.
- Fix the regression test to target `Paris`.

#### 2. Objections should remain blocking; AI incoming proposals are the right place to reduce modal burden

Evidence:

- Objection hard-stop: `backend/commands/executor.py:427-433`
- Dialogue lifecycle supports non-blocking expiry: `backend/models/dialogue_manager.py:78-97`
- AI incoming proposals are still explicitly blocking: `backend/game_logic/ai_diplomacy.py:823-855`
- Current command guard blocks on any pending diplomatic dialogue, not only blocking ones: `backend/commands/executor.py:460-478`
- Parser-side dialogue guard also triggers on any pending dialogue: `backend/main.py:605-620`

Clarification:

- Marshal objections are true decision points and should continue to stop play.
- AI proposals do not need the same treatment. They are the best candidate for "Later", dismiss, or short-term ignore behavior.
- The current architecture can already support ignorable diplomatic UI, but only after the guards stop treating every pending diplomatic dialogue as blocking.

Recommended short-term direction:

- Keep objections blocking.
- Make incoming AI proposals non-blocking and dismissible.
- If ignored, auto-reject or expire them after one turn instead of freezing the command loop.

#### 3. Raw diplomacy labels are still at risk of leaking into popups because display formatting is split across backend and Godot

Evidence:

- Backend proposal display map: `backend/display_names.py:125-139`
- Incoming popup keeps its own separate display map: `godot-client/project-sovereign/scripts/incoming_proposal_popup.gd:18-28`
- Backend fallback still formats proposal clauses ad hoc: `backend/main.py:233-269`
- Proposal term display is also rebuilt separately in dialogue helpers: `backend/game_logic/diplomatic_dialogue.py:633-705`

Clarification:

- I did not reproduce a literal `Open_borders` string during this follow-up.
- But the current structure is still brittle enough that raw enum/action-style labels can leak or degrade, especially through fallback paths and duplicated display maps.

Recommended short-term direction:

- Make the backend the single owner of diplomacy display strings.
- Send only final human-readable proposal/term labels to Godot.
- Add a regression test that fails if popup payload text contains raw underscore tokens or enum-style treaty names.

#### 4. PL-26 remains more of a teaching/setup problem than a pure balance problem

Evidence:

- `backend/game_logic/combat.py:55-64`
- `backend/game_logic/combat.py:331`
- `backend/game_logic/combat.py:476`
- Fresh-world probe: `Ney, attack Wellington` still produced a punishing early result; simple prep lines improved it only to stalemate

Clarification:

- The combat system does explain itself during and after battle.
- The problem is that the common opener commits the player before the game has taught the counters it expects.

Recommended short-term direction:

- Keep the combat depth.
- Surface the likely outcome and key counters earlier.
- Ensure at least one obvious early French preparation line is visibly better than the naive opener.

#### 5. Enemy AI remains competent enough for the current map, but still reads as smart-by-threshold more than deeply characterful

Evidence:

- Attack personality path: `backend/ai/enemy_ai.py:2078-2145`
- Homeland recapture path: `backend/ai/enemy_ai.py:2402-2455`
- Omniscient helper note: `backend/models/world_state.py:1534-1540`
- Direct probes showed Wellington refusing low-advantage attacks while more aggressive personalities escalated sooner

Clarification:

- Personality differentiation is real in practice.
- It is still mostly threshold/stance behavior rather than distinct operational doctrine.

Recommended short-term direction:

- Keep the current AI structure for the 19-region game.
- Add per-turn query caching and visibility seams before map scale increases.

### Focused Roadmap

1. Make defeat-state truth consistent now: align code, tests, and docs on capital loss before the larger victory redesign.
2. Split diplomacy into hard-stop and soft-stop flows: objections stay blocking; incoming AI proposals become non-blocking and ignorable.
3. Unify diplomacy text formatting so raw treaty/action tokens cannot leak into popups.
4. Improve the first combat lesson through setup/surfacing, not a blanket flattening of combat depth.
5. Reduce AI opacity before full-map work by introducing caching and fog-aware query seams.

## Diplomacy Modal / Queue Addendum

Audit date: 2026-04-10

Scope: hard-stop vs soft-stop diplomacy flows, typed popup/button response routing, player-facing display ownership, and queue/expiry UX when proposals are ignored, delayed, or stacked.

### Additional Execution Evidence

- Code trace across `backend/commands/executor.py`, `backend/main.py`, `backend/game_logic/ai_diplomacy.py`, `backend/commands/diplomatic_executor.py`, `backend/models/dialogue_manager.py`, `backend/models/world_state.py`, `godot-client/project-sovereign/scripts/main.gd`, and `godot-client/project-sovereign/scripts/incoming_proposal_popup.gd`
- `tests/test_dialogue_manager.py` and `tests/test_bugfix_popup_chain.py` passed in the current tree
- `tests/test_bugfix_proposal_flow.py` was mostly green, but one pre-existing unrelated failure remained: `TestModifyEscalation::test_harsh_round2_more_than_round1`
- Source-level reproduction: an Austria incoming proposal delivered on turn 5 remained blocking through turns 6-7, auto-cleared on turn 8, and a same-turn queued Prussian proposal expired before it could be shown because queue expiry ran before queued delivery

### Addendum Findings

#### 1. Major - the hard-stop / soft-stop split still exists mostly as intent, not as enforced behavior

Evidence:

- `backend/commands/executor.py:460-478` blocks on any pending diplomatic dialogue, not only blocking ones
- `backend/main.py:605-638` does the same on the parser path
- `backend/commands/meta_executor.py:115-126` already distinguishes blocking vs non-blocking for `end_turn`
- `backend/game_logic/ai_diplomacy.py:823-855` still marks every incoming AI proposal as `blocking=True`
- Current live blocking dialogue types include `force_declare_war_confirmation` (`backend/commands/diplomatic_executor.py:472-485`), `alliance_paradox` (`backend/game_logic/diplomacy.py:1235-1255`), `sabotage_confrontation` (`backend/commands/diplomatic_defiance.py:349-371`), `vassal_rebellion_imminent` (`backend/game_logic/vassal.py:362-388`), `conflict_alert` (`backend/commands/diplomatic_executor.py:3069-3087`), `counter_offer` (`backend/commands/diplomatic_executor.py:3217-3243`), and incoming AI proposals (`backend/game_logic/ai_diplomacy.py:823-855`)

Recommended taxonomy:

- Hard-stop: `force_declare_war_confirmation`, `alliance_paradox`
- Soft-stop: `incoming_proposal`, `counter_offer`, `counter_offer_response`, `conflict_alert`
- Soft-stop for ordinary commands but not ignorable forever: `sabotage_confrontation`, `vassal_rebellion_imminent`; let the player keep acting, but resolve or auto-default them by end-turn instead of freezing the whole loop
- Player-authored planning flows such as `proposal_confirm`, `advisory`, `mission`, `terms_guidance`, and `ultimatum_demand_wizard` should stay local dialogue workflows, not global campaign blockers

Best-fit UX:

- Give soft-stop diplomacy a persistent home such as a Talleyrand "desk" or diplomatic mailbox
- Incoming proposals and other non-urgent items should land there with a visible count/badge instead of interrupting the terminal immediately
- The player should be able to open that surface deliberately and answer items through typed dialogue actions, while hard-stop crises still interrupt in place

Inference note:

- The exact split above is an inference from the live option semantics and the current player-friction pattern, not an explicit design contract already written elsewhere.

#### 2. Major - several diplomacy popup handlers still leak back through `/command` instead of typed choice transport

Evidence:

- `godot-client/project-sovereign/scripts/main.gd:2733-2760` keeps a `proposal_confirm` fallback that synthesizes English commands
- `godot-client/project-sovereign/scripts/main.gd:2768-2774` handles incoming proposals through `send_command`
- `godot-client/project-sovereign/scripts/main.gd:2776-2797` handles Talleyrand objections through `send_command` or an action-specific raw command
- `godot-client/project-sovereign/scripts/main.gd:2799-2805` handles sabotage discovery through `send_command`
- `godot-client/project-sovereign/scripts/main.gd:2809-2815` handles vassal rebellion through `send_command`
- `godot-client/project-sovereign/scripts/main.gd:2817-2829` shows the desired end state: alliance paradox already uses `send_dialogue_response`
- `backend/main.py:1142-1186` already exposes `/respond_to_diplomatic_dialogue`
- Backend typed handlers already exist for most of these actions: AI proposal responses (`backend/commands/diplomatic_executor.py:2019-2026`), sabotage confrontation (`backend/commands/diplomatic_executor.py:2115-2136`), vassal rebellion (`backend/commands/diplomatic_executor.py:2437-2501`), and alliance paradox (`backend/commands/diplomatic_executor.py:2506-2559`)

Clarification:

- Incoming proposals, sabotage confrontation, vassal rebellion, and alliance paradox are already dialogue-shaped on the backend and can move to typed option ids now.
- The diplomatic objection popup is the outlier: it is not currently backed by `pending_diplomatic_dialogue`, so it needs either a typed objection endpoint or a small backend conversion into dialogue form before the frontend can stop synthesizing raw commands.

#### 3. Moderate - raw diplomacy display leaks are broader than the previous follow-up captured

Evidence:

- `backend/main.py:233-269` still rebuilds incoming proposal text ad hoc in the popup safety valve
- `godot-client/project-sovereign/scripts/incoming_proposal_popup.gd:18-55` keeps a separate proposal-type map and falls back to `replace("_", " ").capitalize()`
- `backend/game_logic/diplomatic_dialogue.py:633-699` still formats unknown demand/sweetener types with raw underscore replacement
- `backend/models/world_state.py:4521-4531` builds counter-offer popup clauses directly from raw `d.get("type")` / `s.get("type")`
- `backend/commands/diplomatic_defiance.py:379-403` summarizes sabotaged proposals with `replace("_", " ").title()` instead of canonical display names
- `backend/game_logic/ai_diplomacy.py:883-904` still owns a second clause-display map instead of reusing `backend/display_names.py`

Clarification:

- The strongest live leak is the counter-offer popup path in `world_state.py`, because it can emit raw clause ids directly into the popup payload.
- The other paths are a mix of true leak risk and canonical-name degradation, such as losing hyphenation or treaty-specific wording.

#### 4. Major - current queue / expiry behavior drops unseen proposals when blockers linger

Evidence:

- Queue expiry drops items once `current_turn - turn_generated >= 3` in `backend/game_logic/ai_diplomacy.py:304-312`
- Queue overflow silently keeps only the three best-priority items in `backend/game_logic/ai_diplomacy.py:315-349`
- Queued delivery expires old items before attempting delivery in `backend/game_logic/ai_diplomacy.py:1009-1024`
- Blocking dialogues only clear on the stale-dialogue path in `backend/models/dialogue_manager.py:78-97` and `backend/models/world_state.py:4149-4151`
- Incoming proposals are still delivered as blocking dialogues in `backend/game_logic/ai_diplomacy.py:823-855`

Why this matters:

- If a blocking proposal is ignored until the safety valve clears it, a second proposal generated in the same turn can expire before it is ever shown.
- With `QUEUE_MAX_SIZE = 3`, stacked diplomacy is pruned by hidden timeouts and priority drops rather than by player choice.
- That is tolerable only if proposals are intentionally soft-stop and visible while they age. In the current blocking model, it produces silent disappearance instead.

Recommended short-term direction:

- Make incoming proposals and counter-offers soft-stop
- Base expiry on turns visible, or auto-reject with a notification/log entry instead of silently dropping hidden items
- Add integration tests for hidden-expiry, stacked queue, and queue overflow behavior
- Prefer a visible mailbox/desk model over an invisible timeout queue; unseen offers should not disappear without either surfacing to the player or generating an explicit auto-reject record

### Addendum Roadmap

1. Enforce the blocking taxonomy in `executor.py` and `main.py`; stop hard-blocking on `pending_diplomatic_dialogue` blindly.
2. Introduce a diplomacy mailbox / desk surface for soft-stop items and route those responses through typed dialogue ids.
3. Finish typed popup-response routing for the remaining diplomacy handlers; add a typed objection path instead of synthesizing English commands.
4. Centralize proposal/clause display generation in the backend, including counter-offer popup payloads.
5. Rework queue expiry around visibility or explicit auto-reject semantics so stacked proposals never disappear unseen.
6. Keep the broader architecture roadmap as-is; this addendum sharpens the PL-27 contract/interrupt work rather than changing the overall sequencing.
