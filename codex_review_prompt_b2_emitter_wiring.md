# Codex code review — Imperial Settlement Slice B2 emitter call-site wiring

You are reviewing the latest commit on branch `codex/fix-b1-review-findings` of `mitchsuch-star/project-sovereign-map` (Napoleonic strategy game; FastAPI backend, Godot frontend). Pull the head of that branch and review against parent `14bcf56` (the B2 ordering-guard review-fix commit).

```
git fetch origin && git checkout codex/fix-b1-review-findings
git diff 14bcf56..HEAD --stat
```

## What this commit does

Lands the **Slice B2 emitter call-site wiring sub-gate** of the Imperial Settlement / Ally Participation contribution tracker. B2 splits into three sub-gates per `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` Slice B build bullets:

1. **B2 ordering guard (parent `7974474` + review-fix `14bcf56`)** — the `accrue_battle_contribution()` entrypoint + `record_battle()` ordering pin. Already landed.
2. **B2 emitter call-site wiring (this commit)** — theater-aware updates to the three diplo `record_battle` callers (`backend/commands/combat_executor.py::_post_combat_pipeline()`, `_execute_attack()` inline path, and `backend/models/world_state.py::_process_reckless_cavalry_turn_start()` auto-dispatch charge), routed through a new one-hop adjacency helper.
3. **B3 lifecycle (later)** — per-turn staying-power accrual, war-entry seam wiring of `open_episode()` / `close_episode_for_exit()`, same-turn separate-peace event ordering, archive compaction.

This commit ships:

- `backend/game_logic/war_contribution.py::detect_battle_theater(world, *, battle_region, attacker_nation, defender_nation, war_id=None, attacker_pre_battle_strength=None, defender_pre_battle_strength=None)` — the spec §9.4 line 717 one-hop adjacency theater detector.
- `backend/game_logic/diplomacy.py::record_battle()` extended with keyword-only `war_id` / `attacker_participants` / `defender_participants` / `nation_theater_strength` parameters, forwarded into `accrue_battle_contribution()`.
- `backend/commands/combat_executor.py::_post_combat_pipeline()` step 8 now calls `detect_battle_theater(...)` before `record_diplo_battle(...)` and forwards the four theater fields.
- `backend/commands/combat_executor.py::_execute_attack()` inline diplo-record path (the one that fires before `_post_combat_pipeline(skip_diplo_record=True)`) calls the helper and forwards the payload.
- `backend/models/world_state.py::_process_reckless_cavalry_turn_start()` auto-dispatch charge (the third battle emitter, bypassing both `_post_combat_pipeline` and `_execute_attack`) calls the helper and forwards the payload.
- 12 new B2 emitter tests in `tests/test_war_contribution_scores.py` (89 total in file, was 77).
- `CLAUDE.md` "Current Phase" peace deals bullet updated.

**Out of scope (must NOT be invented in this commit):** occupation event functions / accrual, support event functions / accrual, treaty-clause emission (`WorldState._ratify_treaty()` / `_process_treaty_clauses()` updates), British coalition subsidy wiring (`coalition.py::_process_british_subsidy()`), per-turn staying-power accrual, war-entry seam `open_episode()` / `close_episode_for_exit()` wiring, common-peace term legitimacy, Slice C/D reactions, theater detection extensions for `campaign_theater_id` / front-group metadata.

## Authoritative spec / plan / context

Read these in this order before reviewing the code:

1. `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` §9.2 (contribution scoring formula), §9.4 (theater-level battle attribution + sub-1000 contribution rule + theater-strength floor-1 + one-hop adjacency rule + whole-war-credit prohibition at line 725), §9.5 (event-driven performance contract — battle accrual fires at battle resolution time only, not per turn / per region), §9.6 (battle record compatibility / old-record adapter).
2. `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` §"Slice B" — specifically the B2 build bullets:
   - "B2 event emitters and theater attribution: battle, occupation, support, treaty-support, British subsidy, sub-1000 battle contribution, `_execute_attack()` inline diplo records, auto-dispatch charge records, and the glorious-charge pipeline fixture."
   - "Concrete call-site inventory before coding: central path `backend/commands/combat_executor.py::_post_combat_pipeline()` currently calls diplomatic `record_battle()` from the post-combat pipeline, and `_execute_glorious_charge()` already routes through that pipeline. The non-pipeline inventory is `_execute_attack()`'s inline diplomatic `record_battle()` path, which later calls `_post_combat_pipeline(..., skip_diplo_record=True)`, plus the auto-dispatch charge path in `backend/models/world_state.py`. Route those non-pipeline emitters through the same theater-attribution helper or give them equivalent participant/war detection."
   - Gate criteria: "`_execute_attack()` inline-record and auto-dispatch charge fixtures prove non-pipeline battle records emit theater participants and `war_id` for settlement contribution; the glorious-charge fixture proves its pipeline-routed record receives the same fields."
   - Gate criteria: "Three-theater full-Europe fixture proves a 6+ participant war across distant fronts does not create zero contribution for a front's real fighters and does not credit all same-side participants across unrelated fronts." (B2 baseline; the full 6+ participant three-theater Europe fixture is a B3 task, but the distant-front exclusion contract MUST already be tested in B2.)
3. `docs/PEACE_DEALS_UMBRELLA_SPEC.md` — cross-slice gating (B2 emitter wiring must NOT invent occupation/support/treaty emitters or B3 lifecycle behavior).
4. `CLAUDE.md` — golden rules. Especially: rule 8 (no per-region scans in hot paths — the helper walks `world.marshals` once and only the battle region + its `Region.adjacent_regions`, NOT `world.regions.values()`), rule 6 (LLM never affects mechanics).
5. The previous review prompts: `codex_review_prompt_b1.md` and `codex_review_prompt_b2_ordering_guard.md` — context for what B1 and the B2 ordering sub-gate already shipped.

## Files changed (6 files, +735 / -8)

```
CLAUDE.md                              ← Current Phase peace deals bullet updated
backend/commands/combat_executor.py    ← _post_combat_pipeline + _execute_attack inline call sites pass theater payload
backend/game_logic/diplomacy.py        ← record_battle() accepts war_id / attacker_participants / defender_participants / nation_theater_strength kwargs
backend/game_logic/war_contribution.py ← +detect_battle_theater(...) helper; __all__ exports it
backend/models/world_state.py          ← _process_reckless_cavalry_turn_start() auto-dispatch charge passes theater payload
tests/test_war_contribution_scores.py  ← 12 new B2 emitter tests (5 helper unit tests + 3 source-order assertions + 4 behavioral end-to-end fixtures) + _seat_marshal / _clear_default_marshals / _setup_three_theater_world helpers
```

## What to verify (priority-ordered)

### 1 — `detect_battle_theater()` correctness against spec §9.4

Look at `backend/game_logic/war_contribution.py::detect_battle_theater` and confirm:

- **One-hop adjacency rule (spec line 717):** The theater region set is built from `{battle_region}` plus `world.get_region(battle_region).adjacent_regions`. Confirm a marshal in a TWO-hop region does NOT get credited (e.g., for a battle in `Saxony`, a marshal in `Vienna` — which is adjacent to `Bohemia` which is adjacent to `Saxony` — must NOT be detected).
- **Whole-war-credit prohibition (spec line 725):** A same-side participant fighting on a distant front (no marshal in the theater set) gets nothing from this battle. The behavioral fixture `test_post_combat_pipeline_distant_same_side_participant_no_free_credit` locks this in. Verify the helper actually filters by location, not by side membership alone.
- **Active-participant filter:** The helper reads `instance.get("active_participants")` and skips marshals whose nation is NOT in that set (when the set is non-empty). Verify the empty-set case: when `active_participants` is empty, the filter degrades to "no exclusion" (since the test condition is `if active_participants and nation not in active_participants`). **Concern:** is "empty set means no exclusion" the correct default? In production, A2-wired war_instances always populate `active_participants`. But what if a future bug leaves it empty — should the helper accrue everyone or refuse to accrue? Argue.
- **Side-membership filter:** Marshals whose nation is on neither attacker_side nor defender_side are skipped (continue). Verify this handles bystanders correctly (e.g., a neutral marshal in the theater).
- **Strength filter:** Marshals with `strength <= 0` are skipped. **Concern:** in `_post_combat_pipeline`'s call site, the diplo record fires at step 8 (after `marshal.strength` may have been reduced to 0 by combat). If the explicit attacker/defender has 0 strength, are they still credited? Walk through: the helper unconditionally `attacker_set.add(attacker_nation)` / `defender_set.add(defender_nation)` AFTER the marshal walk, and `setdefault(attacker_nation, 0)` ensures the key exists. The accrue function then floors 0 to 1. Confirm this works correctly when the marshal was destroyed mid-battle.
- **Pre-battle strength override:** When `attacker_pre_battle_strength` / `defender_pre_battle_strength` is supplied, the helper writes that strength into `nation_theater_strength[attacker_nation]` (overriding any sum that the marshal walk produced). Verify: if the explicit attacker had MULTIPLE marshals in the theater (e.g., Napoleon at Saxony and a second French marshal at Bohemia), does the override clobber the multi-marshal sum? Walk through and argue whether this is correct. Spec §9.4 line 620-622 says "as recorded at battle time" — is using only the primary marshal's pre-battle strength acceptable, or should it be `max(pre_battle_strength, post_battle_sum)`?
- **Sorted determinism:** `attacker_participants` / `defender_participants` are returned via `sorted(set)`. Verify this prevents nondeterministic test failures (Python set iteration order) and matches the legacy adapter's list shape.
- **Empty-input guard:** The helper returns `None` for empty `battle_region` / `attacker_nation` / `defender_nation`. Verify the call sites can never pass empty strings (e.g., `_post_combat_pipeline`'s `battle_region` always comes from `ctx['battle_region']` which is always set by callers).

### 2 — Three call-site wirings (the heart of the emitter sub-gate)

For each of the three call sites, verify:

- The call site reads its captured pre-battle strengths (NOT the marshal's current `.strength`, which may be post-battle).
- The call site invokes `detect_battle_theater(...)` with `battle_region`, `attacker_nation`, `defender_nation`, and the two pre-battle strength overrides.
- The call site forwards `(theater or {}).get("war_id")` / `.get("attacker_participants")` / `.get("defender_participants")` / `.get("nation_theater_strength")` into `record_diplo_battle(...)`.
- The fallback when `theater is None` (no resolvable war_id) passes `None` for all four — `record_battle()` then forwards `None` to `accrue_battle_contribution()`, which uses the legacy adapter to fill single-nation defaults. Verify this fallback path still produces correct accrual when `is_at_war` is True but the war_instance lookup fails.

#### 2a — `_post_combat_pipeline()` (drives glorious-charge / bombardment / garrison / pipeline-routed attack)

`backend/commands/combat_executor.py:914-947` (step 8 of the pipeline). Confirm:

- Pre-battle strengths come from `ctx['pre_battle_attacker_strength']` / `ctx['pre_battle_defender_strength']` (cast `int(pre_atk)` / `int(pre_def)`).
- The diplo step is gated on `not ctx.get('skip_diplo_record')` AND `diplo_winner is not None`. **Concern:** the helper is called inside the `if diplo_winner` block, so when the battle has no winner (e.g., stalemate / mutual destruction), no theater detection runs. Is that correct? Look at `record_diplo_battle`'s callers: the previous behavior was "no winner = no record". Argue whether stalemates should still accrue settlement contribution per spec §9.2 (the formula does not require a winner — both sides accumulate from inflicted/suffered casualties).
- The garrison path passes `defender=None` to the pipeline and synthesizes `defender_nation` from `ctx.get('defender_nation', ...)`. When `defender` is `None`, `attacker.nation` and `defender_nation` are both populated; the helper resolves `war_id` against the pair. Verify garrison combat still emits theater data. Is there a gap if `defender_nation` is empty (e.g., neutral garrison)?

#### 2b — `_execute_attack()` inline diplo path

`backend/commands/combat_executor.py:3297-3327` (immediately after the cannon-fire `world.record_battle(...)` call). Confirm:

- Pre-battle strengths come from `pre_battle_attacker_strength` / `pre_battle_defender_strength` captured at `_execute_attack` line ~3170-ish (verify the variable names match between the inline diplo path and the pre-battle capture).
- The inline path fires BEFORE `_post_combat_pipeline(..., skip_diplo_record=True, ...)` runs at line ~3498. So the pipeline's diplo step is correctly skipped — no double-emission.
- Verify by `inspect.getsource(combat_executor.CombatExecutor._execute_attack)` (mirrors the existing test) that BOTH the inline `detect_battle_theater(` call AND the `skip_diplo_record=True` pipeline call appear in source order.

#### 2c — `_process_reckless_cavalry_turn_start()` auto-dispatch charge

`backend/models/world_state.py:7026-7058` (immediately after the cannon-fire `self.record_battle(...)` call). Confirm:

- Pre-battle strengths come from `pre_battle_atk` / `pre_battle_def` captured at line ~6982-6983 (BEFORE `combat_resolver.resolve_battle(...)` mutates marshal strengths).
- The auto-dispatch path bypasses both `_post_combat_pipeline` and `_execute_attack` — it is the third independent emitter. Verify there is no other auto-charge / auto-dispatch path in `world_state.py` that ALSO calls `record_diplo_battle` and was missed.
- The path passes `attacker_nation=marshal.nation` / `defender_nation=enemy.nation` / `winner_nation=diplo_winner` correctly. The `diplo_winner` resolution mirrors `_execute_attack`: `marshal.nation if atk_won_diplo else (enemy.nation if def_won_diplo else None)`.

### 3 — `record_battle()` signature compatibility

Look at `backend/game_logic/diplomacy.py::record_battle` and confirm:

- The four new parameters are keyword-only (after `*,`). This means existing positional callers — if any — would break loudly. Search the codebase for any positional `record_battle(world, "France", "Austria", ...)` callers and confirm they all already use kwargs. (Yes per `Grep record_battle backend/`.)
- All four new parameters default to `None`, so call sites that don't supply them get the legacy single-nation adapter path inside `accrue_battle_contribution()`.
- The function-local import `from backend.game_logic.war_contribution import accrue_battle_contribution` is unchanged from the B2 ordering guard. The new params flow through into the existing accrue call.
- The `Mapping` and `Optional` imports are added to the typing import line. Verify ruff is clean.

### 4 — Pre-battle strength precedence + multi-marshal stacking

Spec §9.4 line 620-622: "If `casualties_suffered_by_nation` / `pre_battle_strength` is absent, use raw `nation_theater_strength` exactly as recorded at battle time. Adding per-nation casualty exposure later is a compatibility extension, not a prerequisite for settlement contribution."

The helper currently uses post-battle marshal `.strength` for non-explicit participants and pre-battle overrides ONLY for the explicit attacker/defender. Argue:

- **Concern:** if the explicit attacker had multiple marshals in the theater, the override discards the secondary marshals' contribution (e.g., Napoleon at Saxony with 40k pre-battle, plus Davout at Bohemia with 20k post-battle). The override sets `France: 40000`, ignoring Davout. Walk through what spec line 620-622 implies: the override is supposed to compensate for casualty reduction at the PRIMARY combatant. Should the helper instead set `France: max(40000, 40000 + sum_of_other_french_marshals_in_theater)`? Or is a single-marshal override the correct B2 baseline given combat resolution still treats the battle as primary attacker vs primary defender?
- **Concern:** the override is unconditional once supplied. If a caller passes `attacker_pre_battle_strength=0` (e.g., a bug in the call site), the override sets `France: 0`, which then floors to 1 in `accrue_battle_contribution`. Is silent-floor the right defense, or should the helper guard against zero-or-negative overrides?

### 5 — Helper performance + scale (golden rule 8)

Spec §9.5 / impl plan §"Scale Rules" / CLAUDE.md golden rule 8: no per-region scans in hot paths.

Verify:

- The helper iterates `world.marshals.values()` once. At full-Europe scale this is O(M) where M ~ 50-80 marshals. Acceptable.
- The helper does NOT walk `world.regions.values()`. It only reads `world.get_region(battle_region).adjacent_regions` (O(1) lookup + O(adjacency) iteration, max ~6-8 adjacent regions).
- The helper does NOT call `world.get_war_instances_by_participant()` redundantly — it delegates to `_resolve_active_war_id_for_pair` which uses the cached index.
- The helper is called ONCE per battle resolution. There are at most ~5-10 battles per turn at full-Europe scale. Total per-turn cost: O(M * battles) which is negligible.

**Question:** does `_post_combat_pipeline` get called inside any per-region or per-marshal loop (e.g., coordinated battles with multiple participants)? Look for callers and confirm the pipeline fires once per "primary battle event" rather than per participant.

### 6 — Active-participant filter edge cases

The helper filters marshals by `instance.get("active_participants")`. Verify:

- The test `test_detect_battle_theater_filters_inactive_participants` removes Saxony from `active_participants` while leaving Saxony's marshal in the theater. The helper should not credit Saxony.
- **Concern:** the explicit attacker/defender are added to participant sets AFTER the marshal walk regardless of their `active_participants` membership. So an "inactive" attacker who somehow still launches an attack would still get credited. Is this a real bug or impossible by construction? Walk through: A3's `mark_participant_eliminated_in_all_wars` removes a nation from `active_participants` when it's eliminated; could an eliminated nation still launch a battle? Argue.

### 7 — Test coverage adequacy

12 new tests in this commit (89 total in file). Categories:

- **5 helper unit tests:** no-active-war / same-side / one-hop-adjacency credit / pre-battle override / inactive-participant filter.
- **3 source-order assertions:** one per call site (`_post_combat_pipeline`, `_execute_attack` inline, `_process_reckless_cavalry_turn_start`). Each uses `inspect.getsource` + `find()` + ordering check.
- **4 behavioral end-to-end fixtures:**
  - `test_post_combat_pipeline_emits_theater_data_for_glorious_charge` — drives the pipeline with `is_glorious_charge=True`, verifies France + Saxony attacker bucket split, distant Spain gets zero, Austria gets full defender bucket.
  - `test_post_combat_pipeline_distant_same_side_participant_no_free_credit` — Russia in Marseille (distant) gets zero credit for a Saxony battle.
  - `test_auto_dispatch_charge_emits_theater_data` — sets up reckless-cavalry Murat (France, Bohemia, recklessness=4) charging Charles (Austria, Saxony), verifies France + Saxony attacker accrual + Austria defender bucket.
  - `test_inline_execute_attack_emits_theater_data` — drives a real `_execute_attack` flow with Napoleon attacking Saxony, verifies all three nations accrue.

Verify:

- **Source-order assertions** check that `detect_battle_theater(` precedes `record_diplo_battle(` AND that the four theater fields appear after `record_diplo_battle(`. **Concern:** the assertion uses `src.find("detect_battle_theater(")` which would match a comment or docstring mention. Argue whether that's a real risk (vs. the same risk in the B2 ordering guard's source-order test, which the previous review accepted).
- **Behavioral pipeline test** uses `_clear_default_marshals` to wipe the WorldState's starting roster, then seats synthetic marshals. **Concern:** does this synthetic setup correctly exercise the same code path as a real game battle, given the WorldState init is otherwise unchanged? Walk through and argue.
- **Behavioral inline-attack test** uses `strength=120000` for Napoleon vs `strength=8000` for Charles to force an attacker-victory outcome. The combat resolver is real (not mocked). **Concern:** if combat resolution thresholds change in a future commit, does this test silently start producing stalemates and skip the diplo-record path (since `if diplo_winner` gates the helper call)? The test asserts `result.get("success")` and then `france_ep["battle"] > 0`, so a stalemate would fail the second assertion — but the failure message would not point at the root cause. Argue whether the test should explicitly assert `outcome contains "victory"`.
- **Behavioral auto-charge test** also uses oversized attacker strength. Same concern.
- **Gap candidates:**
  - Garrison combat (`is_garrison=True`, `defender=None`) is NOT explicitly tested in the behavioral fixtures. The pipeline test sets `is_glorious_charge=True`. Is there a separate test for the garrison path emitting theater data?
  - Bombardment (`is_bombardment=True`) is NOT explicitly tested. The B2 ordering guard's review fixed bombardment to call the pipeline; the emitter wiring must verify bombardment also forwards theater data.
  - The `theater is None` fallback path (where `_resolve_active_war_id_for_pair` returns None) is NOT explicitly behavior-tested at the call sites — the helper unit tests cover the helper's None return, but the pipeline test doesn't verify the call site degrades gracefully when the helper returns None. Flag.
  - The pre-battle strength override is unit-tested but the call-site wiring's pre-battle capture is NOT independently verified. If `_post_combat_pipeline` accidentally passed `ctx.get('attacker_casualties')` instead of `ctx.get('pre_battle_attacker_strength')`, the test would still pass (since the explicit attacker is added to participants). Flag.
  - Coordinated battle (multi-attacker / multi-defender via `_calculate_coordination_context`) is NOT tested. Spec §9.4 says credit is divided by theater strength; coordinated attackers should split the bucket. Flag whether B2 should test coordinated battles or whether B3 / a later sub-gate handles them.

### 8 — Cross-slice gating (B2 emitter scope discipline)

The commit must NOT ship occupation events, support events, treaty-clause emission, British subsidy wiring, or B3 lifecycle behavior. Verify:

- No new `accrue_occupation_contribution`, `accrue_support_contribution`, `record_occupation_event`, etc. functions in `war_contribution.py`.
- No `WorldState._ratify_treaty()` or `WorldState._process_treaty_clauses()` updates emitting `war_support_delivered`.
- No `coalition.py::_process_british_subsidy()` updates.
- No `open_episode()` / `close_episode_for_exit()` call wiring at war-entry seams in `diplomacy.py` / `settlement_helpers.py` / `world_state.py::_advance_turn_internal`.
- No per-turn staying-power accrual in `process_diplomacy_turn` or `_advance_turn_internal`.
- The `detect_battle_theater` helper only resolves theater for BATTLE events. It does not also handle occupation/support attribution.
- `accrue_battle_contribution` only writes `episode["battle"]` and `episode["total"]`. Confirm no `episode["occupation"]` / `episode["staying_power"]` / `episode["support"]` writes leaked into this commit.

### 9 — `_clear_default_marshals` test helper hygiene

The test file adds `_clear_default_marshals(world)` which wipes `world.marshals` and rebuilds the marshal index. This is needed because `WorldState.__init__` populates the live game's starting marshals (Reynier in Dresden, Schwarzenberg in Bohemia, etc.) which would contaminate theater detection.

Verify:

- The helper calls `world._build_marshal_index()` after clearing, so cached `_marshals_by_region` doesn't keep stale references.
- The behavioral fixtures all call `_clear_default_marshals(world)` BEFORE seating synthetic marshals (otherwise the default Reynier-in-Dresden would inflate Saxony's theater strength).
- **Concern:** is wiping default marshals an acceptable test pattern, or does it indicate a brittle fixture design? Argue whether the test helper should instead use a "synthetic-only" WorldState constructor.

### 10 — Golden rules + style

- **Golden rule 8 (no per-region scans in hot paths):** the helper walks `world.marshals` once, no `world.regions.values()` walk. ✓
- **Golden rule 6 (LLM never affects mechanics):** B2 emitter wiring has no LLM surface. ✓
- All numeric fields stay int — pre-battle strength casts via `int(pre_atk)` / `int(pre_battle_atk)`; helper returns `Dict[str, int]` for theater strength.
- No new floats leak into to_dict / from_dict (this commit doesn't touch save/load).
- `detect_battle_theater` accepts all-kwargs after the first positional `world`; no positional-arg drift risk.
- `__all__` in `war_contribution.py` exports `detect_battle_theater`.
- `record_battle` keyword-only params use `*,` separator; existing positional callers still work because all current callers use kwargs.
- Test helpers (`_seat_marshal`, `_clear_default_marshals`, `_setup_three_theater_world`) are private (leading underscore) and live in the test file.

### 11 — Documentation routing

- `CLAUDE.md` "Current Phase" peace deals bullet — updated to reflect B2 emitter call-site wiring landed, B3 lifecycle as next sub-gate. Verify the previous "B2 emitter call-site wiring is the next sub-gate" sentence was removed (not just appended-over).
- `STATUS.md` — should this need an update for the B2 emitter sub-gate? The B2 ordering guard had a STATUS.md entry; the emitter wiring is a follow-up sub-gate of the same Slice. Argue.
- `docs/SAVE_FORMAT_REFERENCE.md` — does this need an update? The B2 emitter wiring does not change the save format (`war_contribution_scores` shape was added in B1 and unchanged). Confirm.
- `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` — should the B2 build bullet reflect that emitter call-site wiring is DONE and only occupation/support/treaty emitters + British subsidy attribution remain? Argue.

## Verification commands

```
".venv/Scripts/python.exe" -m pytest tests/test_war_contribution_scores.py tests/test_war_settlement_merge.py tests/test_war_settlement_instances.py tests/test_war_settlement_foundation.py -v
".venv/Scripts/python.exe" -m pytest tests/ --tb=short -q
".venv/Scripts/python.exe" -m ruff check backend/ tests/
```

Expected: full suite `9453 passed, 1 skipped` (post-B2-ordering-guard baseline was `9441 passed, 1 skipped` after review fixes; net +12, all in `tests/test_war_contribution_scores.py`). Ruff clean.

## Output format

For each section above, write **one of**:

- `OK` — verified correct with reasoning.
- `MINOR` — issue found, non-blocking. Describe and propose a fix.
- `BLOCKER` — issue must be fixed before merge. Describe with file:line and concrete repro / fix.

Then a short **Summary** section: blocker count, minor count, any spec-divergence concerns, and one paragraph on whether the B2 emitter call-site wiring looks ready to handoff for the rest of B2 (occupation events, support events, treaty-clause emission, British subsidy attribution) or whether the wiring needs a fix-up pass first.

Be skeptical of:

- Any place the helper credits a same-side participant without a marshal in the one-hop adjacency set (would violate spec §9.4 line 725 whole-war-credit prohibition).
- Any place the helper skips the explicit attacker/defender (e.g., a strength=0 marshal that should still be credited because they were the primary combatant).
- Any place a call site forgets to forward one of the four theater fields (most likely failure: forgetting `war_id` and relying on `_resolve_active_war_id_for_pair` to re-resolve from scratch — works but adds a redundant lookup).
- Any place the source-order assertion could pass while the call site is functionally broken (e.g., the helper is called but its return value is discarded; the `record_diplo_battle` keyword args use stale variables; the helper is called after `record_diplo_battle`).
- Any divergence from the legacy adapter path: when `theater is None`, the call site passes `None` for all four kwargs and `accrue_battle_contribution` falls back to single-nation attribution. Verify this fallback still produces the same accrual numbers as the pre-emitter-wiring B2-ordering-guard behavior for unchanged single-nation battles (no regression on existing tests).
- Any place B2 emitter wiring silently invents occupation/support events, treaty-clause emission, British subsidy wiring, or B3 lifecycle behavior.
- Any place the helper does a per-region scan or per-turn iteration over `world.regions.values()` (golden rule 8 violation).
- Any place a test asserts incidental rather than contractual behavior (e.g., specific casualty numbers that depend on combat resolver internals rather than spec §9.2 formulas).
- Any place the pre-battle strength override is misapplied (e.g., applied to a non-explicit participant, or applied additively rather than as a replacement, or silently dropped when the marshal walk produces a higher number).
- Any place the active-participant filter is bypassed (e.g., the explicit attacker/defender add-back at the end ignores the filter — argue whether that's correct given A3's `mark_participant_eliminated_in_all_wars`).

The repo CLAUDE.md is the authoritative project guide; treat its golden rules as binding.
