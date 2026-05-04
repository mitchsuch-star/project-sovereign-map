# Codex code review — Imperial Settlement Slice B2 ordering guard

You are reviewing commit **`7974474` on branch `codex/fix-b1-review-findings`** of `mitchsuch-star/project-sovereign-map` (Napoleonic strategy game; FastAPI backend, Godot frontend). Pull that exact SHA and review against its parent `ae3066a`.

```
git fetch origin && git checkout 7974474
git diff ae3066a..7974474 --stat
```

## What this commit does

Lands the **Slice B2 ordering sub-gate** of the Imperial Settlement / Ally Participation contribution tracker. B2 is split into three sub-gates per `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` Slice B build bullets:

1. **B2 ordering guard (this commit)** — the `accrue_battle_contribution()` entrypoint + `record_battle()` ordering pin. The guard MUST land before the wider B2 emitter wiring so the contract (settlement contribution accrues BEFORE the 1000-casualty war-score early return per spec §9.4 line 713) cannot regress as call sites are migrated.
2. **B2 emitter call-site wiring (next sub-gate, NOT in this commit)** — theater-aware updates to the three diplo `record_battle` callers (`backend/commands/combat_executor.py::_post_combat_pipeline()`, `_execute_attack()` inline path, and `backend/models/world_state.py` auto-dispatch charge path), plus occupation events, treaty-clause / British coalition subsidy support events, and one-hop adjacency participant detection.
3. **B3 lifecycle (later)** — per-turn staying-power accrual, war-entry seam wiring of `open_episode()` / `close_episode_for_exit()`, same-turn separate-peace event ordering, archive compaction.

This commit ships:

- `backend/game_logic/war_contribution.py::accrue_battle_contribution(world, *, attacker_nation, defender_nation, winner_nation, attacker_casualties, defender_casualties, location, war_id, attacker_participants, defender_participants, nation_theater_strength, turn)` — the canonical battle-bucket accrual entrypoint per spec §9.2 / §9.4.
- Internal helpers: `_resolve_active_war_id_for_pair`, `_battle_side_raw`, `_is_decisive_battle`.
- `backend/game_logic/diplomacy.py::record_battle()` calls the entrypoint AFTER the `is_at_war` precondition but BEFORE the 1000-casualty war-score early return.
- 8 new B2 ordering-guard tests in `tests/test_war_contribution_scores.py` (63 total in file, was 55).
- `CLAUDE.md` / `docs/STATUS.md` updated.

**Out of scope (must NOT be invented in this commit):** theater-aware call-site updates, occupation events, support events, treaty-clause emission, British subsidy attribution, one-hop adjacency participant detection, per-turn staying-power accrual, war-entry seam episode opening, common-peace term legitimacy, Slice C/D reactions.

## Authoritative spec / plan / context

Read these in this order before reviewing the code:

1. `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` §9.2 (contribution scoring formula), §9.4 (theater-level battle attribution + sub-1000 contribution rule + theater-strength floor-1), §9.5 (event-driven performance contract), §9.6 (battle record compatibility / old-record adapter).
2. `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` §"Slice B" — specifically the B2 build bullet "Before B2 starts, add a regression guard for `backend/game_logic/diplomacy.py::record_battle()` ordering. The guard must fail if settlement contribution accrual moves after the 1000-casualty war-score early return. A source-order assertion is acceptable only if paired with a behavioral sub-1000-casualty fixture proving settlement contribution accrues while no pairwise war-score battle record is added." Also read the call-site inventory: B2 must extend `diplomacy.record_battle()` (NOT `WorldState.record_battle`).
3. `docs/PEACE_DEALS_UMBRELLA_SPEC.md` — cross-slice gating (B2 ordering guard must NOT invent B2 emitter wiring or B3 lifecycle behavior).
4. `CLAUDE.md` — golden rules. Especially: rule 8 (no per-region scans in hot paths — the war_id resolver MUST use the cached `get_war_instances_by_participant()` index), rule 6 (LLM never affects mechanics).
5. The previous B1 review prompt: `codex_review_prompt_b1.md` — context on what B1 already shipped and how the B1 store / standing classifier interact with B2 emitters.

## Files changed (5 files, +590 / -10)

```
CLAUDE.md                              ← Current Phase peace deals bullet updated
backend/game_logic/diplomacy.py        ← record_battle() calls accrue_battle_contribution(...) before 1000-casualty gate
backend/game_logic/war_contribution.py ← +accrue_battle_contribution + _resolve_active_war_id_for_pair + _battle_side_raw + _is_decisive_battle; module docstring updated
docs/STATUS.md                         ← new "Last Updated" entry; "Next diplomacy workflow" updated
tests/test_war_contribution_scores.py  ← 8 new B2 ordering-guard tests + _setup_war_pair_with_episodes helper
```

## What to verify (priority-ordered)

### 1 — Ordering pin in `record_battle()` (the heart of the guard)

Look at `backend/game_logic/diplomacy.py::record_battle()` and confirm:

- The `accrue_battle_contribution(...)` call appears AFTER the `is_at_war` precondition (line ~8455) — it should not accrue contribution for non-WAR pairs.
- The call appears BEFORE the `if total_casualties < 1000: return` early return (line ~8497 post-wiring) — this is the contract per spec §9.4 line 713.
- The call uses kwargs (no positional drift risk).
- The call passes `turn=getattr(world, "current_turn", None)` for episode-window filtering by future B2 readers.
- The accrual return value is intentionally discarded — it is consumed by tests/debug only, not by `record_battle()`'s war-score path.
- The inline `from backend.game_logic.war_contribution import accrue_battle_contribution` is a function-local import. **Question:** is this acceptable, or should it move to module top? `war_contribution.py` is a leaf module with no imports of its own, so circular import is impossible. The local import slightly increases per-call overhead but matches the existing pattern in `combat_executor.py` (which uses `from backend.game_logic.diplomacy import record_battle as record_diplo_battle` inline). Argue.

**Specifically check the source-order assertion test enforces this**: `tests/test_war_contribution_scores.py::test_record_battle_calls_settlement_accrual_before_1000_casualty_war_score_gate` uses `inspect.getsource(diplomacy.record_battle)` and `src.find("accrue_battle_contribution") < src.find("total_casualties < 1000")`. **Concern:** does the test catch the case where the accrue call appears in a comment or docstring before the gate? If a future refactor moved the call but kept the docstring mention, the assertion would still pass. Argue whether the assertion needs to be tightened (e.g., regex matching on a function call rather than a substring).

### 2 — `accrue_battle_contribution` formula correctness against spec §9.2

Spec §9.2 line 590-594 (paste from spec):

```python
battle_side_raw =
    side_casualties_inflicted // 100
    + side_casualties_suffered // 250
    + decisive_battle_win * 25

battle_raw[nation] =
    round(battle_side_raw * nation_theater_strength[nation] / side_theater_strength)
```

Verify:

- `_battle_side_raw(inflicted_casualties, suffered_casualties, decisive_win)` matches the formula exactly. Note: `max(0, int(...))` clamps negative casualties to 0 — is that defensive or does it mask a real bug if a caller passed a negative value? Argue.
- The attacker side calls `_battle_side_raw(inflicted_casualties=defender_casualties, suffered_casualties=attacker_casualties, decisive_win=attacker_decisive_win)` — this is correct (the attacker INFLICTED the defender casualties and SUFFERED their own). Verify the inverse for the defender side.
- Per-nation distribution uses `round(side_raw * per_nation_strength[participant] / side_strength)`. Python 3 `round()` is banker's rounding; the test `test_accrue_battle_contribution_distributes_by_theater_strength_when_provided` uses 52.5 → 52 and 17.5 → 18 to lock this in. Confirm the test's expected values match Python 3 banker's rounding behavior.
- **Floor-1 per spec §9.4 line 622:** "If an otherwise valid detected participant has `nation_theater_strength <= 0`, use a floor of `1` for that participant before risk adjustment so routed or adjacent political participants are not silently dropped." The implementation uses `max(1, int(theater.get(p) or 0) or 1)`. Walk through this expression for every input case (0, negative, missing, valid positive) and confirm correctness. **Concern:** is `int(theater.get(p) or 0) or 1` an over-clever expression? It evaluates `int(0)` → `0` → falsy → `1`. Acceptable; flag if you find a simpler equivalent.

### 3 — Decisive-battle treatment (spec §9.2 + war-score parity)

Spec §9.2 just says `+ decisive_battle_win * 25` without re-defining "decisive". The implementation interprets this as:

- `_is_decisive_battle(attacker_casualties, defender_casualties)` mirrors the war-score decisive criterion: `total > 10000 AND ratio > 2:1 AND both sides have >0 casualties`.
- Per-war decisive cap (max 2 per war on the war-score side at line 8493) is NOT mirrored on the settlement side. The reasoning: episode boundary already bounds settlement decisive credit, and a high-decisive-volume war is a high-contribution war anyway.

**Argue both ways:**

- Is mirroring the war-score decisive criterion the correct spec interpretation, or should settlement use a softer/harder threshold (e.g., always count routs as decisive regardless of total casualties)? Spec §9.2 is silent on the criterion definition.
- Is dropping the per-war cap correct? The war-score cap exists to prevent a single 5-decisive-battle war from over-rewarding the side. Settlement contribution shares are per-episode (not per-war), so re-entry resets the count anyway. Confirm the spec intent.
- Spec §9.2 includes decisive in the per-side raw, then divides by theater strength. So a winning side with multiple participants splits the +25 by theater strength share. Is that correct per spec? It seems aligned with the formula's per-side accumulation pattern.

### 4 — `_resolve_active_war_id_for_pair` correctness + scale

Spec §"Scale Rules" (impl plan): "Repeated participant-scoped war-instance queries, especially cross-war settlement reactions, must use a dirty-flag per-turn `war_instances_by_participant` cache rather than filtering all active instances for each affected nation."

Verify:

- `_resolve_active_war_id_for_pair` uses `world.get_war_instances_by_participant(nation_a)` (cached) FIRST, then falls back to scanning `world.war_instances` only if the helper is unavailable. **Concern:** the fallback scan is O(N) over all active war_instances. At 20+ active wars this is acceptable, but flag if the resolver is in any per-turn loop (it should fire only at battle resolution time per spec §9.5 line 733).
- The diplo_key uses `world._make_diplo_key(nation_a, nation_b)` (sorted alphabetical pair key) when available, with a fallback to `"|".join(sorted((nation_a, nation_b)))` — verify these produce identical strings for any input pair.
- Returns `None` when no active war_instance owns the pair. **Question:** under what production conditions could the `is_at_war` check pass in `record_battle()` but the war_instance lookup fail? The post-A2 wiring should always allocate a war_instance before mutating diplomatic_states to WAR, so this shouldn't happen — but if it does, the accrual silently no-ops. Is silent failure correct, or should it log a warning? Argue.

### 5 — Side-membership validation (no-op cases)

`accrue_battle_contribution` validates:

- Both `attacker_nation` and `defender_nation` are non-empty.
- War_id resolves to an instance with `side_by_nation` mapping for both.
- The two nations land on opposite sides (no friendly-fire credit).

If any check fails, return `None` and accrue nothing. Verify:

- `test_accrue_battle_contribution_returns_none_when_no_active_war_instance` covers the no-instance case.
- `test_accrue_battle_contribution_returns_none_when_nations_on_same_side` covers the same-side case.
- **Gap:** is there a test for the case where `attacker_nation` is in `side_by_nation` but `defender_nation` is not (e.g., because the defender's war-entry seam hasn't fired yet)? The current implementation returns `None` in that case (since `defender_side` would be `None`), but no explicit test covers it. Flag if you think this should be tested.
- **Gap:** is there a test for empty `attacker_nation` / `defender_nation` strings? Current implementation guards with `if not attacker_nation or not defender_nation`. No explicit test. Flag.

### 6 — Episode-skip behavior (pre-B3 tolerance)

Spec §9.5: contribution readers filter records by the active episode's `joined_turn <= event.turn <= exited_turn` range. B3 will wire `open_episode()` calls at war-entry seams; B2's accrual must not crash before those seams are wired.

Verify:

- `accrue_battle_contribution` calls `current_episode(world, war_id, participant)` for each participant. If `None` (no record / no current_episode_id / current episode dict missing / episode exited), the participant is silently skipped.
- `test_accrue_battle_contribution_skips_participants_without_active_episode` proves this: France has an episode, Austria doesn't; only France gets credit; result dict has France in `accrued_battle_points` and not Austria.
- **Concern:** if an episode is `current` but has been `close_episode_for_exit`-stamped (so `exited_turn` is set), does the accrual still apply credit for same-turn battles AFTER the exit stamp? Spec §9.5 line 740: "The inclusive `event.turn <= exited_turn` boundary in section 7.5 is correct only under that ordering" — i.e., the EVENT ordering should put battle/occupation/support events BEFORE exit stamping. The implementation doesn't currently filter on `exited_turn`; it accrues whenever there is a `current_episode_id` that resolves to a dict. **Question:** is this acceptable, given the event-ordering invariant? Walk through what happens if a same-turn settlement closes the episode FIRST and then `record_battle()` fires after — does the accrual still land? Should it?

### 7 — Old-record adapter integration (spec §9.6)

The accrual function uses `adapt_legacy_battle_record(...)` to fill theater defaults when caller omits them. Verify:

- The adapter is called whenever `attacker_participants` / `defender_participants` / `nation_theater_strength` is omitted. This means current B2-transition callers (the three diplo `record_battle` callers that have not yet been refactored) get single-attacker / single-defender / theater_strength {1, 1} attribution.
- The adapter does NOT re-run if all theater fields are explicitly passed — verify by reading the call. Actually it always re-runs (the adapter is non-destructive: passed fields win), so the theater-aware path still passes through the adapter. Is that a perf concern? The adapter is O(participants) — negligible. Confirm.
- **Spec §9.6 line 756:** "No retroactive multi-participant attribution is attempted for old saves; old records count as single-nation participation." The legacy callers in this commit fall back to single-nation; B2 emitter wiring (next commit) will pass real multi-participant lists. Confirm the legacy path stays single-nation.

### 8 — Test coverage adequacy

8 new tests in this commit (63 total in file). The implementation plan caps Slice B sub-gates at observed 50-55 test single-session ceiling; this commit is well under that.

Verify:

- **Source-order assertion** (test 1) — covered.
- **Behavioral sub-1000 fixture** (test 2) — covered. Locks in the spec §9.4 line 713 contract.
- **Above-1000 regression** (test 3) — covered. Without this, a future refactor could short-circuit accrual on big battles silently.
- **Function-safety: no war_instance** (test 4) — covered.
- **Function-safety: same-side** (test 5) — covered.
- **Function-safety: missing episode** (test 6) — covered.
- **Forward-compat: explicit theater strength distribution** (test 7) — covered. Locks in the contract that B2 emitter wiring will call against.
- **Gap candidates:**
  - Decisive-battle accrual (above-10k casualties + ratio > 2:1) is NOT explicitly tested. The above-1000 test uses 2000/3000 casualties which is non-decisive. Is there a separate test proving the +25 decisive bonus fires correctly? **Look for one and flag if missing.**
  - `_resolve_active_war_id_for_pair` fallback scan is NOT explicitly tested. Is there a test where `get_war_instances_by_participant` is unavailable and the resolver still finds the war_id via raw scan? Flag if missing.
  - Empty-string nations are NOT explicitly tested. Flag.
  - `winner_nation == ""` (no winner / draw) is NOT explicitly tested. The implementation passes `winner_nation` to `_is_decisive_battle` indirectly through `attacker_decisive_win = decisive and winner_nation == attacker_nation`; if winner is empty, both decisive flags are False, so no decisive bonus. Is that the correct draw behavior? Spec is silent. Flag.

### 9 — Cross-slice gating (B2 ordering guard scope discipline)

The commit must NOT ship B2 emitter wiring or B3 lifecycle behavior. Verify:

- No theater-aware updates to the three diplo `record_battle` callers in `backend/commands/combat_executor.py` or `backend/models/world_state.py`. The callers still pass the legacy single-attacker / single-defender signature; the accrual function uses the legacy adapter to fill theater defaults.
- No new occupation event functions (`accrue_occupation_contribution`, `record_occupation_event`, etc) — those are the next sub-gate.
- No new support event functions (`accrue_support_contribution`, etc) — those are the next sub-gate.
- No `coalition.py` British subsidy emission wiring — next sub-gate.
- No `WorldState._ratify_treaty()` or `WorldState._process_treaty_clauses()` updates — next sub-gate.
- No per-turn staying-power accrual — B3.
- No `open_episode()` / `close_episode_for_exit()` call wiring at war-entry seams — B3.
- The `accrue_battle_contribution` function itself only accrues the BATTLE bucket. Confirm `episode["occupation"]`, `episode["staying_power"]`, `episode["support"]` are never written by this function.

### 10 — Golden rules + style

- **Golden rule 8 (no per-region scans in hot paths):** the accrual function reads `world.war_instances`, `world.war_contribution_scores`, `world.get_war_instances_by_participant()` (cached). No `world.regions.values()` walks. ✓
- **Golden rule 6 (LLM never affects mechanics):** B2 ordering guard has no LLM surface. ✓
- All numeric fields stay int — `episode["battle"]`, `episode["total"]`, `accrued[participant]`. Casts via `int(...)` at write boundaries.
- No new floats leak into to_dict / from_dict (the accrual function doesn't touch save/load).
- `accrue_battle_contribution` accepts all-kwargs (forward-compat with B2 emitter wiring); no positional-arg call sites exist.
- `__all__` updated to export `accrue_battle_contribution`.
- Module docstring updated to call out B2 ordering-guard scope and explicitly NOT-shipped work.

### 11 — Documentation routing

- `CLAUDE.md` "Current Phase" peace deals bullet — updated to reflect B2 ordering guard landed, B2 emitter call-site wiring as next sub-gate.
- `STATUS.md` "Last Updated" — new entry for B2 ordering guard.
- `STATUS.md` "Next diplomacy workflow" — updated.
- `docs/SAVE_FORMAT_REFERENCE.md` — does this need an update? The B2 ordering guard does not change the save format (no new fields, no new shapes). Confirm.
- `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` — should the B2 build bullet reflect that the ordering sub-gate is DONE and only emitter call-site wiring + occupation/support events remain? Or does the plan only track per-Slice (B1/B2/B3) status, not per-sub-gate? Argue.

## Verification commands

```
".venv/Scripts/python.exe" -m pytest tests/test_war_contribution_scores.py tests/test_war_settlement_merge.py tests/test_war_settlement_instances.py tests/test_war_settlement_foundation.py -v
".venv/Scripts/python.exe" -m pytest tests/ --tb=short -q
".venv/Scripts/python.exe" -m ruff check backend/ tests/
```

Expected: full suite `9439 passed, 1 skipped` (post-B1 baseline was `9431 passed, 1 skipped`; net +8, all in `tests/test_war_contribution_scores.py`). Ruff clean.

## Output format

For each section above, write **one of**:

- `OK` — verified correct with reasoning.
- `MINOR` — issue found, non-blocking. Describe and propose a fix.
- `BLOCKER` — issue must be fixed before merge. Describe with file:line and concrete repro / fix.

Then a short **Summary** section: blocker count, minor count, any spec-divergence concerns, and one paragraph on whether the B2 ordering guard looks ready to handoff for the rest of B2 (theater-aware emitter call-site wiring + occupation/support events).

Be skeptical of:

- Any place the source-order assertion could pass while the accrual call is functionally broken (e.g., comment-only mention, wrong call signature, dead code).
- Any place the accrual silently no-ops in a production scenario where it should accrue (e.g., `is_at_war` passes but `_resolve_active_war_id_for_pair` returns `None` because of A2/A3 wiring drift).
- Any divergence from spec §9.2's `battle_side_raw` formula (decisive criterion, decisive cap, theater-strength floor-1, banker's-rounding distribution).
- Any place B2 ordering guard silently invents B2 emitter wiring or B3 lifecycle behavior (theater-aware call-site updates, occupation events, support events, per-turn staying-power, war-entry seam episode opening).
- Any place the accrual mutates `episode["occupation"]`, `episode["staying_power"]`, or `episode["support"]` (it should only touch `battle` and `total`).
- Any zero-denominator path that could divide by zero, NaN, or fall through to non-contribution rules differently from spec §9.4 line 622.
- Any place an inline import masks a real failure (the function-local import in `record_battle()`).
- Any place the test asserts behavior that is incidental rather than contractual (e.g., banker's-rounding outcomes that would change with a different rounding mode).

The repo CLAUDE.md is the authoritative project guide; treat its golden rules as binding.
