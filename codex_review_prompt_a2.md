# CODEX CODE REVIEW PROMPT — Imperial Settlement Slice A2

**Repo:** https://github.com/mitchsuch-star/project-sovereign-map
**Branch:** master
**Commit under review (PINNED):** `75b9febb50f6fb96e2c56451b2a2c7f25d29d90b`
("Land Slice A2: Imperial Settlement war-entry threading")
**Predecessor (A1 foundation):** `274aee8`

## Scope

Slice A2 of `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` v1.24 §7.2 / §7.3
and `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` v1.21 Slice A
"A2 war-entry threading" bullets. A2 must thread `war_id` through every
WAR-entry seam: player / AI / coalition declaration, vassal rebellion,
vassal-release rebellion, commitment-paradox outcome (routed through
`declare_war`), scripted / debug entry, join-opportunity acceptance,
counter-bargain acceptance, armistice collapse, combat-triggered
auto-war fallback, and every cascade attach point.

## Files to review at SHA 75b9feb

- `backend/game_logic/settlement_helpers.py` — new helpers + `CascadeContext`
- `backend/game_logic/diplomacy.py` — `declare_war`, `_process_war_cascade`,
  `resolve_join_opportunity`, `accept_counter_bargain`,
  `_process_armistice_expiration`
- `backend/game_logic/vassal.py` — `check_vassal_rebellion`,
  `release_vassal` rebellion path
- `tests/test_war_settlement_instances.py` — NEW, A2 test surface
- `docs/STATUS.md`, `CLAUDE.md` — status updates

## Spec / plan reading order (BEFORE the diff)

1. `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` §7 entirety —
   especially §7.2 "Creation seam", "Reuse rule", "Late-join rule",
   "Merge rule", and §7.3 "End condition" (pair_status lifecycle for
   war / armistice / resolved).
2. `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md`
   "Slice A - War Identity And Grouping" section — focus on the A2
   bullets (war-entry threading, A2 merge boundary, vassal rebellion
   call site, war_entry_ledger replacement, ARMISTICE pair-status
   reuse, the `WAR_ENTRY_SEAMS_UNDER_TEST` checklist).
3. `backend/game_logic/settlement_helpers.py` at SHA `274aee8` for
   the A1 baseline (`assert_war_instance_invariants` surface,
   `WarInstanceInvariantError` contract).
4. `tests/test_war_settlement_foundation.py` at `274aee8` for the
   A1 fixture conventions A2 must keep green.

## Mandatory invariants the diff must satisfy

- Every `set_diplomatic_state(..., "WAR", ...)` reachable from a user /
  AI / scripted seam is preceded by a successful
  `ensure_war_instance_for_pair(...)` (or its narrower
  `attach_pair_to_war_instance(...)` direct-entry counterpart).
- The pre-commit `validate_war_declaration(...)` hard-stop fires
  BEFORE state mutation when a side conflict or merge-required
  condition exists; no seam may set the pair to WAR and then discover
  the cascade would place a nation on both sides.
- Cascade defensive / offensive / vassal-defensive / vassal-offensive
  joins all attach to the SAME `war_id` allocated at the root
  declaration. Late-join rules in §7.2 forbid creating a sibling
  instance.
- ARMISTICE → WAR resumption reuses the same `war_id` and sets
  `pair_status = "war"`. ARMISTICE → PEACE moves the pair from
  `active_diplo_keys` to `resolved_diplo_keys` with
  `pair_status = "resolved"` and stamped `resolved_turn`.
- The war-entry ledger event uses the allocated `war_id`, not the
  legacy `war_{episode_id}` placeholder.
- `assert_war_instance_invariants(world, context=...)` must pass after
  every A2 fixture in `tests/test_war_settlement_instances.py` — verify
  the assertions actually exercise the production code paths, not just
  helpers.
- A2 is a hard stop on merge: if a seam discovers two active
  `war_instance` records that would need to be combined, it must
  return `war_instance_merge_required` and NOT mutate state. A3 is
  out of scope.

## Review questions to answer explicitly

1. Are there ANY remaining WAR-entry seams in the codebase (executors,
   cheat commands, reaction passes, paradox handlers, coalition wars,
   save loaders) that mutate `diplomatic_states[k]` to `"WAR"` WITHOUT
   going through `ensure_war_instance_for_pair` or
   `attach_pair_to_war_instance`? Grep for `= "WAR"`, `= 'WAR'`, and
   `set_diplomatic_state(..., "WAR"` outside `settlement_helpers.py`
   and the wired sites listed above.
2. Does the `CascadeContext` correctly propagate through every legacy
   positional / keyword call site of `_process_war_cascade`? Check
   `vassal.py` and any other module that imports it.
   `suppress_unresolved_offensive_cascade` is read from `ctx`, not the
   kwarg — confirm no path was missed.
3. Does `ensure_war_instance_for_pair` handle the "one nation in an
   existing war on the wrong side" fall-through correctly
   (concurrent-front case)? Verify
   `test_concurrent_wars_create_independent_instances_when_sides_clash`
   actually exercises this branch.
4. Are the `participant_meta`, `side_by_nation`, and pair_meta entries
   written to active `war_instance` records consistent with the spec
   §7.1 shape? Check that A2 fields preserve forward-compatibility
   with A3 fields the spec lists (episodes, `contribution_signals_fired`,
   etc.) — A2 should not block A3 from adding them, but also should
   not invent A3-only fields now.
5. Does the `WAR_ENTRY_SEAMS_UNDER_TEST` list in
   `tests/test_war_settlement_instances.py` cover every inventoried
   seam? Are any tests missing? The plan calls for 18-22 focused A2
   tests; the file ships 31 — are any of them redundant or covering
   A3 territory?
6. Are there any places where `ensure_war_instance_for_pair` returning
   `{"ok": False, ...}` is silently ignored by the caller (no error
   path, no `log_event`, no playtest visibility)? A mis-wired hard-stop
   that fails silently is worse than not having the hard-stop at all.
7. Is `_process_armistice_expiration` correctly using
   `resolve_pair_to_resolved` BEFORE `set_diplomatic_state` (so readers
   don't observe a PEACE pair still in `active_diplo_keys`), and
   `ensure_war_instance_for_pair` BEFORE the WAR transition (so readers
   don't observe a WAR pair without a war_instance)? Confirm by tracing
   the order of operations.
8. Save / load round-trip: are the new `war_instance` shape fields
   covered by existing A1 `to_dict` / `from_dict`, or does A2 add
   fields that need explicit wiring in
   `backend/models/world_state.py`? (`origin_episode_id`,
   `origin_entry_path`, `armistice_turn`, `entry_path` inside
   `diplo_key_meta`, etc.) Check `docs/SAVE_FORMAT_REFERENCE.md` to
   see if it needs an A2 update.
9. Lint + suite: confirm `pytest tests/` is green and `ruff check`
   is clean at SHA `75b9feb`. Report any flaky / order-dependent test
   you see in the new file.
10. Concurrency / index correctness: does any seam invalidate
    `war_instance_indexes` AFTER reading from them? Are there any
    paths where `world.invalidate_war_instance_indexes()` is missed?

## Out of scope (A3 owns these — flag if A2 accidentally touched)

- Connected-component merge transaction.
- Leader replacement on elimination / separate peace.
- Common-peace scoring or settlement reactions.
- Contribution accrual.
- Always-on post-merge invariant assertion (A1 helper exists, A2 only
  calls it from tests; A3 promotes it to runtime).

## Deliverables expected from this review

A. A bug list ranked Critical / Major / Minor with `file:line`
   references and proposed fixes.
B. An "extra coverage I would add" list of A2 tests you would write
   that the diff does not yet include.
C. An A3 hand-off checklist: anything you noticed that A3 will need to
   handle that the A2 PR did not name explicitly.

## How to run

```
".venv\Scripts\python.exe" -m pytest tests/ -v --tb=short
".venv\Scripts\python.exe" -m ruff check backend/ tests/
```
