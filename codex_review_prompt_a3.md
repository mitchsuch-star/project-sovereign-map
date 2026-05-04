# Codex code review — Imperial Settlement Slice A3

You are reviewing commit **`b380dca` on branch `master`** of `mitchsuch-star/project-sovereign-map` (Napoleonic strategy game; FastAPI backend, Godot frontend). Pull that exact SHA and review against its parent `294c656`.

```
git fetch origin && git checkout b380dca
git diff 294c656..b380dca --stat
```

## What this commit does

Lands **Slice A3** of the Imperial Settlement / Ally Participation feature. A3 replaces the A2 "merge required" hard-stop with the actual transitive merge transaction and adds the rest of the war-instance lifecycle (side-scoped leader replacement, elimination exit, terminal-record retention, 10-turn archive compaction). It also promotes `assert_war_instance_invariants(..., context="post_merge")` into an always-on check that catches dangling absorbed `war_id` references in both live and optional future-slice containers.

**Out of scope (must NOT be invented):** Slice B contribution accrual; Slice C settlement dialogues / route payloads. A3 only adds **no-op-safe rewrite hooks** for those future containers.

## Authoritative spec / plan / context

Read these in this order before reviewing the code:

1. `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` §7.1, §7.2, §7.4, §7.5, §7.6, and §11.3 (line ~1573 — bargain merge-context preservation).
2. `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` lines 56–137 — the Slice A3 acceptance bullets and gate criteria.
3. `docs/PEACE_DEALS_UMBRELLA_SPEC.md` — cross-slice gating (A3 must NOT invent B/C behavior).
4. `CLAUDE.md` — golden rules. Especially: rule 8 (no per-region scans in hot paths), rule 4 (state clearing AFTER reading), rule 6 (LLM never affects mechanics).
5. `docs/SAVE_FORMAT_REFERENCE.md` — `war_instances`, `archived_war_instances`, `diplomatic_commitments` rows.

## Files changed (10 files, +1630 / -88)

```
CLAUDE.md
backend/game_logic/diplomacy.py
backend/game_logic/settlement_helpers.py             ← bulk of the new code
backend/models/world_state.py
docs/SAVE_FORMAT_REFERENCE.md
docs/STATUS.md
docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md
tests/helpers/full_europe_settlement_fixtures.py
tests/test_war_settlement_instances.py
tests/test_war_settlement_merge.py                   ← new file, ~23 tests
```

## What to verify (priority-ordered)

### 1 — `merge_war_instances` correctness against spec §7.6

In `backend/game_logic/settlement_helpers.py`, find `merge_war_instances`. Walk the 9-step transaction order and confirm:

- Step 1 — `_connected_component_war_ids` walks the component via shared participants. **Question:** does it correctly handle the case where the seed list includes only one war_id but a third war shares participants with it? Does it terminate? Are inactive (`ended_turn != None`) instances correctly excluded?
- Step 2 — `_validate_merged_sides` is **pure** (no mutation). Confirm it returns `WAR_INSTANCE_SIDE_CONFLICT` and that the world is byte-identical after a side-conflict abort. Look at `test_merge_side_conflict_aborts_without_mutation` — does the snapshot comparison actually catch a partial mutation if one were introduced?
- Step 3 — survivor pick is `(created_sequence ASC, created_turn ASC, war_id ASC)`. Spec says "oldest". Verify lexicographic tie-break on `war_id` doesn't mis-order `war_2` vs `war_10` (yes, `"war_10" < "war_2"` lexicographically). Is this a correctness bug? If `created_sequence` is always monotonic and unique, the lex tie-break is unreachable — confirm.
- Step 4 — `_merge_instance_data` unions list fields and dict-merges (survivor wins on collisions). Spec §7.2 line 333 says objective_keys must be a union (no one dominant). Confirm via `test_merge_preserves_objective_keys_as_union_of_absorbed_instances`.
- Step 5 — leader replacement runs side-by-side via `_choose_leader_for_side`. Verify each side reads its own `leader_source_by_side[side]` and does NOT cross-pollinate (impl plan gate line 135).
- Step 6 — `_rewrite_absorbed_war_id_in_bargains` rewrites `bargain.war_id` only. Confirm it does NOT touch `side_at_creation` / `side_leader_at_creation` (spec §11.3 line 1573, `test_merge_rewrites_absorbed_war_id_on_bargains_but_preserves_side_leader_at_creation`).
- Step 7 — three no-op-safe hooks (`_rewrite_absorbed_war_id_in_contribution`, `..._settlement_dialogues`, `..._route_payloads`) use `getattr(world, name, None)`. Confirm each silently no-ops when the container is absent. Confirm the contribution hook merges scores when present (it adds, not overwrites — is that the right policy for Slice B handoff? Slice B ultimately re-derives from event log, so this is conservative).
- Step 8 — atomic swap. The order is: stage working copy on `world.war_instances[surviving_id]` for leader scoring (Step 5 mid-loop), THEN do the live + future-slice rewrites (Steps 6–7), THEN final swap + delete absorbed ids. **Concern:** the intermediate Step-5 stage on `instances[surviving_id]` means readers entering during Step 5 would see the working copy (with merged sides but pre-rewrite bargain references). Is anything reading `world.war_instances` during the merge itself? Single-threaded execution should make this safe, but confirm.
- Step 9 — `world.invalidate_war_instance_indexes()`. Confirm.
- Step 10 — `assert_war_instance_invariants(world, context="post_merge")` at the end of the function. Confirm it runs unconditionally before return.

### 2 — Hard-stop replacement semantics

The two A2 hard-stop sites are now soft signals → merge → re-validate:

- `validate_war_declaration:327` (was `ok=False, error=WAR_INSTANCE_MERGE_REQUIRED`, now `ok=True, merge_required=True, merge_candidates=[...]`). Verify `WAR_INSTANCE_MERGE_REQUIRED` is no longer returned anywhere from this function. The constant is still exported for back-compat / future use; confirm nothing depends on the old return shape that wasn't migrated.
- `ensure_war_instance_for_pair` — when `merge_required=True`, runs `merge_war_instances(...)` then re-calls `validate_war_declaration`. Verify: (a) no infinite recursion if re-validation also returns `merge_required` (the second call has `attacker_war_ids` / `defender_war_ids` resolving to the survivor only, so it falls through to `merge_required=False`). (b) if re-validation returns side_conflict, the function aborts cleanly.
- `attach_pair_to_war_instance:591` — when pair owned by different active instance, runs `merge_war_instances([war_id, existing_owner])`, retargets `war_id` to survivor, falls through to the existing attach path. Verify the `instance.get("ended_turn") is not None` check after retarget catches a survivor that was in some weird terminal state.

### 3 — Cascade context drift

`merge_war_instances` accepts `ctx: Optional[CascadeContext]` and rewrites `ctx.war_id` in-place if the pre-merge value was absorbed. **Question:** are all current cascade callers passing `ctx`? Trace `_process_war_cascade` in `backend/game_logic/diplomacy.py` and confirm:
- The cascade walker's working `ctx.war_id` matches the surviving id after any in-cascade merge (otherwise subsequent cascade attaches would target an absorbed id).
- `attach_pair_to_war_instance` does NOT take `ctx` — it returns `war_id` in the result. Callers must update `ctx.war_id` themselves when the result returns a different id. Verify there is at least one cascade test that exercises this path. (Search for `attach_pair_to_war_instance` calls in `diplomacy.py` and confirm they update the cascade ctx if the returned `war_id` differs.) **This is a likely gap.** Confirm or flag.

### 4 — Bargain merge-context fields

In `backend/game_logic/diplomacy.py`, `_resolve_bargain_war_context` (above `create_war_bargain_commitment`) walks `world.war_instances` for an active instance covering (promiser, target_enemy). Three concerns:
- O(N) scan over all war_instances on every bargain creation. Acceptable for now (bargains are infrequent), but confirm there's no use case in the bargain-creation hot path.
- The walk picks the FIRST matching instance. If a nation participates in multiple wars and the (promiser, target_enemy) pair lives in more than one, the first-match heuristic could be wrong. Is this guaranteed-unique by spec? (Each pair lives in at most one active instance — confirm via §7.2.)
- Old saves: pre-A3 bargains have no `war_id` key. `dict.get()` returns `None`. Confirmed via `test_pre_a3_bargain_loads_with_null_merge_context_via_from_dict_default`. Flag if there's a downstream consumer that would crash on `None`.

### 5 — Elimination exit

`mark_participant_eliminated_in_all_wars` is called from `world_state.py::_eliminate_nation` BEFORE the diplomatic_states teardown. Verify:
- It walks ALL active war_instances the nation participates in (the test `test_elimination_walks_all_war_instances_for_the_nation` covers this with the 3-instance fixture).
- No separate-peace reaction is emitted (spec line 107). Currently the helper emits no events at all; confirm this is intentional — Slices C/D may want to hook this. The TODO marker should be near the function if a future hook is needed.
- If the eliminated nation was a side leader, `_choose_leader_for_side` repicks. Verify the test `test_eliminated_side_leader_triggers_repick` exercises a real repick rather than a no-op.

### 6 — Archive compaction timing

`archive_terminal_war_instances(world)` is called from `_advance_turn_internal` AFTER the idempotency guard but BEFORE the per-turn flag clearing. The retention boundary is `(current_turn - ended_turn) >= ARCHIVE_RETENTION_TURNS=10`. Verify:
- A war ending on turn 5, with the archive call running at turn 15's start (current_turn=15 at function entry, before increment), gets archived: `15 - 5 = 10 ≥ 10`. ✓
- A war ending on turn 5 stays queryable on turn 14: `14 - 5 = 9 < 10`. ✓ (`test_terminal_war_queryable_within_retention_window`).
- The post-merge invariant accepts archived `war_id` references as legitimate (`test_post_merge_invariant_passes_when_bargain_war_id_resolves_to_archived`).

### 7 — Post-merge invariant + `_known_war_ids`

In `assert_war_instance_invariants`, the `context="post_merge"` branch calls `_post_merge_violations(world)`. Verify:
- `_known_war_ids(world)` returns active + archived war_ids. Active in-progress merges (where the survivor is staged on `world.war_instances` but absorbed ids are not yet deleted) — does this matter? The function is called at end of merge, after the atomic swap. Confirm.
- The walker tolerates None / missing `war_id` fields (e.g. legacy bargains) — yes via `if war_id_value and isinstance(war_id_value, str)`.
- The future-slice container walks (`war_contribution_scores`, `pending_settlement_dialogues`, `settlement_route_payloads`) only fire if the attribute exists and matches the expected dict/list shape. Confirm `test_post_merge_no_op_safe_when_slice_bc_containers_absent` passes by negation (no false positives).

### 8 — Migration of A2 hard-stop tests

Four A2 tests in `tests/test_war_settlement_instances.py` were migrated. Confirm each migration is semantically correct, not just renaming the assertion:

- `test_ensure_war_instance_runs_merge_then_reveals_side_conflict` (was `..._hard_stops_on_merge_required`) — scenario: France/Austria + Russia/Prussia, then Austria→Prussia. After A3 merge, Austria and Prussia both end up on `defenders`, so the new pair is a TRUE side conflict. Verify the migrated assertion (`error == WAR_INSTANCE_SIDE_CONFLICT`, single survivor, all 4 nations as participants).
- `test_declare_war_blocks_when_post_merge_revalidation_finds_side_conflict` — same scenario via `declare_war`. Verify `success=False`, `error=WAR_INSTANCE_SIDE_CONFLICT`, `(Austria, Prussia)` did not advance to WAR (but the merge ITSELF did happen — is that desirable?). The merge is a separate state change; the failed declaration is conservative. Discuss.
- `test_attach_pair_triggers_merge_when_pair_owned_by_other_active_instance` (was `..._rejects_pair_owned_by_another_active_instance`) — scenario: war_1 + war_2, then attach war_1's pair to war_2. After merge, war_1 absorbs war_2 (oldest survives), pair is idempotent on survivor. Verify the assertion checks the survivor is `first["war_id"]` (older).
- `test_counter_bargain_hard_stop_when_post_merge_finds_side_conflict` — same as Test 2 via `accept_counter_bargain`. Verify bargain not created and Austria-Prussia not at WAR.

### 9 — Test coverage adequacy

`tests/test_war_settlement_merge.py` has 23 tests. The implementation plan gate (line 118) requires "18–22 focused tests for merge/archive/leader/elimination behavior, including multi-objective merge preservation and post-merge contribution denominator rules." Verify:

- All 7 A3 acceptance bullets (impl plan lines 97–111) have at least one test. Especially: spec line 101 "post-merge standing uses the merged current-episode side denominator" — A3 only owns the `war_id` rewrite, so this is a B-slice concern, but verify the contribution rewrite hook test (`_rewrite_absorbed_war_id_in_contribution`) covers the merge-when-present case.
- Three new fixtures in `tests/helpers/full_europe_settlement_fixtures.py` are exercised by the merge test file.
- Are there gaps? Specifically:
  - **No test for ARMISTICE pair merging.** If two active wars both have an ARMISTICE pair on overlapping nations, does the merge survive correctly?
  - **No test for CascadeContext rewrite during in-cascade merge.** This is a real wiring path; the test surface relies on the unit-level merge tests + cascade integration tests in `test_war_settlement_instances.py`. Confirm at least one A2 cascade test still passes a `CascadeContext` into a flow that COULD trigger merge.
  - **No test confirming `_resolve_bargain_war_context` returns `(None, None, None)` when no active war covers the (promiser, target_enemy).** This is implicit in `test_pre_a3_bargain_loads_with_null_merge_context_via_from_dict_default` but worth a focused unit test.

### 10 — Golden rules + style

- Golden rule 8 (no per-region scans in hot paths): `merge_war_instances` walks `world.war_instances`, not regions. ✓
- Golden rule 4 (state clearing after reading): the merge stages working copy, reads from it, then does the atomic swap. ✓
- All numbers passed to potential Godot consumers are `int(...)` wrapped where needed (e.g. archive `current_turn - ended_turn` arithmetic). ✓
- No new floats leak into to_dict / from_dict shapes.
- `_post_merge_violations` builds a string at every `_check` call — no f-string format crash on None / non-str inputs (guarded).
- `archive_terminal_war_instances` does `from copy import deepcopy` at call time inside the function body. Minor — could be hoisted to module top. Style preference, not a bug.

## Verification commands

```
".venv/Scripts/python.exe" -m pytest tests/test_war_settlement_merge.py tests/test_war_settlement_instances.py tests/test_war_settlement_foundation.py -v
".venv/Scripts/python.exe" -m pytest tests/ --tb=short -q
".venv/Scripts/python.exe" -m ruff check backend/ tests/
```

Expected: full suite `9373 passed, 1 skipped` (post-A2 baseline was `9350 passed, 1 skipped`; net +23). Ruff clean.

## Output format

For each section above, write **one of**:

- `OK` — verified correct with reasoning.
- `MINOR` — issue found, non-blocking. Describe and propose a fix.
- `BLOCKER` — issue must be fixed before merge. Describe with file:line and concrete repro / fix.

Then a short **Summary** section: blocker count, minor count, any spec-divergence concerns, and one paragraph on whether this looks ready to handoff for Slice B.

Be skeptical of:
- Anywhere the merge could leave `world.war_instances` in a partial state observable by readers.
- Anywhere the post-merge invariant could pass while a real leak exists (false negative).
- Anywhere the A2 hard-stop replacement could now silently merge when the user expected an error.
- Any `getattr(world, ...)` that should have been `hasattr` (or vice versa) for the no-op-safe hooks.

The repo CLAUDE.md is the authoritative project guide; treat its golden rules as binding.
