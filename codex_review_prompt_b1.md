# Codex code review — Imperial Settlement Slice B1

You are reviewing commit **`b0742e2` on branch `master`** of `mitchsuch-star/project-sovereign-map` (Napoleonic strategy game; FastAPI backend, Godot frontend). Pull that exact SHA and review against its parent `9a02400`.

```
git fetch origin && git checkout b0742e2
git diff 9a02400..b0742e2 --stat
```

## What this commit does

Lands **Slice B1** of the Imperial Settlement / Ally Participation feature — the contribution tracker substrate. B1 ships:

- `world.war_contribution_scores` data shape per spec §9.1.
- Episode helpers: `canonical_episode_id`, `open_episode`, `close_episode_for_exit`, `current_episode`, `iter_active_episodes`.
- Current-episode math: `current_episode_total`, `current_episode_material_total`, `total_side_current_episode_contribution`, `total_side_material_contribution`, `contribution_share`, `material_contribution_share` — all zero-safe.
- Old-record adapter (`adapt_legacy_battle_record`) per spec §9.6.
- Pure standing classifier (`classify_standing`) implementing spec §8.2.
- Composite `compute_standing_inputs` / `standing_for_participant` wrappers that bundle B1 contribution data + accept term-derived booleans verbatim (defaults `False`).

**Out of scope (must NOT be invented):** B2 event emitters (battle / occupation / support accrual), B3 per-turn lifecycle (staying-power accrual, exit stamping), Slice C common-peace term legitimacy, Slice D reaction routing.

## Authoritative spec / plan / context

Read these in this order before reviewing the code:

1. `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` §8 (political standing, classifier rules) and §9 (war contribution score, buckets, attribution, performance contract, old-record compatibility).
2. `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` §"Slice B" — specifically the B1 / B2 / B3 split (lines ~150-198 in the plan). B1 is "data model, canonical store, save/load defaults, old-record adapter, current-episode model, material-contribution gate, contribution-share query helpers, and pure contribution-derived standing inputs."
3. `docs/PEACE_DEALS_UMBRELLA_SPEC.md` — cross-slice gating (B1 must NOT invent B2/B3/C/D behavior).
4. `CLAUDE.md` — golden rules. Especially: rule 8 (no per-region scans in hot paths), rule 4 (state clearing AFTER reading), rule 6 (LLM never affects mechanics).
5. `docs/SAVE_FORMAT_REFERENCE.md` — `war_contribution_scores` row.

## Files changed (8 files, +1608 / -32)

```
CLAUDE.md
backend/game_logic/settlement_helpers.py        ← merge hook B1 shape; war_leader_score wiring
backend/game_logic/war_contribution.py          ← new module, ~530 lines
backend/models/world_state.py                   ← field + save/load
docs/SAVE_FORMAT_REFERENCE.md
docs/STATUS.md
tests/test_war_contribution_scores.py           ← new file, 55 tests
tests/test_war_settlement_merge.py              ← 2 A3 tests migrated
```

## What to verify (priority-ordered)

### 1 — Data shape correctness against spec §9.1

In `backend/game_logic/war_contribution.py`, verify the per-nation dict shape matches spec §9.1 exactly:

```python
{
    "current_episode_id": str,
    "episodes": {episode_id: {joined_turn, exited_turn, battle, occupation, staying_power, support, total}},
    "historical_total": int,
}
```

- `_new_episode_record` fields: confirm all four buckets (`battle`, `occupation`, `staying_power`, `support`) plus `joined_turn`, `exited_turn`, `total` exist; no extra fields invented (e.g., `decisive_battle_count` belongs to B2 emitter, not B1 record).
- `current_episode_id` is a string (not optional) — confirm initial value is `""` not `None` so JSON round-trip is stable.
- `historical_total` is an int (not float) — confirm it is initialized to `0`.

### 2 — Episode id canonicalization (spec §9.1 / §7.5)

`canonical_episode_id(nation, war_sequence, episode_index)` returns `f"{nation}_{int(war_sequence)}_{int(episode_index)}"`.

- Confirm the format matches spec §7.5 line 574: `"{nation_slug}_{war_sequence}_{episode_index}"`.
- Verify `open_episode` reads `war_instances[war_id].created_sequence` when `war_sequence` is omitted (test `test_open_episode_uses_war_instance_created_sequence_when_war_sequence_omitted`).
- Verify `open_episode` increments `episode_index` based on `len(episodes) + 1` — does this break if a stale episode is somehow popped from the dict? Spec says "On re-entry, create a new `episode_id` instead of overwriting the old episode" (line 572). The current implementation never overwrites — confirm.
- **Concern:** `len(episodes) + 1` means re-entry index 2, then 3, etc. If an episode is ever removed from the dict (currently no path does this, but B3 lifecycle might), the next open would collide. Is this a real risk for B2/B3? Flag if so.

### 3 — Zero-safe denominators (spec §9.1)

Spec §9.1: "If `total_side_current_episode_contribution <= 0`... the leader receives `seat` and all other participants resolve to `no_standing`. If `total_side_current_episode_contribution > 0` but `total_side_material_contribution <= 0`, every `material_contribution_share` defaults to `0`. Total contribution remains available for history and staying-power display, but contribution standing, threshold dispatches, and material shut-out grievances fall through to non-contribution rules rather than dividing by zero."

Verify:

- `contribution_share` returns `0.0` when `side_total <= 0` (test `test_contribution_share_returns_zero_when_side_has_no_contribution`).
- `material_contribution_share` returns `0.0` when `side_material <= 0` (tests `test_material_contribution_share_excludes_staying_power_padding` for the cross-side case + `test_material_share_zero_when_side_total_positive_but_material_zero` for the spec line 570 case).
- **Note:** B1 does NOT implement the "leader receives `seat`" override from spec §9.1 line 568 — that's a Slice C concern (the override fires only when a settlement is staged). `classify_standing` accepts the term inputs as `False` defaults, so a B1-only caller with no contribution will get `no_standing` from the classifier, not the spec's "leader auto-seats" behavior. **Question:** is this acceptable for B1, or should `classify_standing` accept a `is_war_leader` boolean? Spec §9.1 places this override in the contribution-evaluation pass; argue for either side.

### 4 — Standing classifier matrix (spec §8.2)

`classify_standing(...)` accepts ten kwargs (power_tier, material_share, material_contribution_points, is_active_same_side, is_vassal_auto_join, has_active_bargain_stake, has_survival_stake, is_named_beneficiary, has_direct_territorial_interest, is_treaty_ally_materially_involved, rival_strengthened) and returns one of `"seat"`, `"consult"`, `"beneficiary_only"`, `"no_standing"`.

Walk every spec §8.2 rule and confirm:

- **Seat** any of: active major + same-side, active war bargain stake, own capital/survival/core, material share >= 25% with material > 0. Tests cover each.
- **Consult** any of: material share >= 10% with material > 0, secondary + any material, region claim / territorial interest, treaty ally materially involved, `rival_strengthened` for major/secondary, `rival_strengthened` for minor IF material > 0. Tests cover each.
- **Beneficiary_only** any of: minor / vassal / liberated state receiving direct outcome, low contribution but specifically named, active same-side with material > 0 not meeting consult thresholds.
- **No_standing** otherwise.

**Vassal cap (spec §8.2 line 506):** Vassal auto-joins receive AT MOST `beneficiary_only` UNLESS they independently meet material-contribution thresholds for `consult` or `seat`.

- Verify the implementation: in the vassal branch, ONLY the material thresholds (>= 25% / >= 10%) escape the cap. Bargain stake / survival stake / rival_strengthened / treaty ally / major auto-seat are all blocked (test `test_classify_standing_vassal_blocks_bargain_and_survival_promotion` covers this).
- **Question:** is the vassal cap correctly absolute? Reading spec §8.2 line 506 literally: "Vassal auto-joins...receive at most `beneficiary_only`...unless they independently meet material-contribution thresholds for `consult` or `seat`." The phrase "material-contribution thresholds" specifically refers to the material share rules, not other inputs — so this implementation matches spec. Confirm or flag.

**Minor + rival_strengthened (spec §8.2 line 497):** "For `minor` powers, `rival_strengthened` alone surfaces an INFO warning but does not promote to `consult` unless `material_contribution_points > 0`."

- The implementation requires `has_material AND rival_strengthened` to promote a minor — verify (test `test_classify_standing_rival_strengthened_for_minor_without_material_no_consult`).
- **Concern:** the spec says the INFO warning STILL fires for minors with `rival_strengthened` and no material — does the B1 classifier surface that? It doesn't (returns `no_standing`). Spec §8.2 line 497 is talking about the advisory warning surface, which is a Slice C/D concern, not the classifier output. Confirm.

**Staying-power gate (spec §8.2 line 483, §9.1 line 482):** "`material_contribution_points = battle + occupation + support`" — staying_power excluded.

- Verify `MATERIAL_BUCKETS = ("battle", "occupation", "support")` and `current_episode_material_total` does NOT include `staying_power` (tests `test_current_episode_material_total_excludes_staying_power`, `test_material_contribution_share_excludes_staying_power_padding`).

### 5 — Old-record adapter (spec §9.6)

`adapt_legacy_battle_record(record)` coerces a pre-B1 battle record into the theater shape.

Verify spec §9.6 lines 747-754:

```python
attacker_participants = record.get("attacker_participants") or [record["attacker"]]
defender_participants = record.get("defender_participants") or [record["defender"]]
nation_theater_strength = record.get("nation_theater_strength") or {
    record["attacker"]: 1, record["defender"]: 1,
}
battle_region = record.get("battle_region") or record.get("location") or record.get("region")
```

- Confirm the implementation matches the spec adapter exactly. Note the spec adapter would crash on missing `attacker` / `defender` (no None guard); B1 returns `[]` and `{}` instead — is this defensive divergence acceptable? Test `test_adapt_legacy_battle_record_handles_missing_attacker_defender` covers it, but does it match spec intent? Spec assumes both fields exist; B1 is more lenient. Flag if defensive divergence introduces a foot-gun.
- Confirm `treaty_transfer` events are NOT awarded contribution credit per spec §9.2 line 641. (B1 doesn't accrue; B2 does. The adapter just coerces the battle-record shape.)
- Verify return is a NEW dict (no in-place mutation of input record). Test the immutability — does mutating the returned dict's lists affect the original? List slicing via `list(...)` creates copies; dict copying via `dict(...)` does too. Confirm.

### 6 — Save/load round-trip

`WorldState.to_dict()` / `from_dict()`:

- New field `war_contribution_scores: Dict[str, Dict[str, Dict]] = {}` initialized in `__init__`.
- `to_dict()` deep-copies the per-nation records (test `test_save_load_round_trip_is_deep_copy_not_alias` proves this).
- `from_dict()` defaults to `{}` for pre-B1 saves (test `test_pre_b1_save_loads_with_empty_contribution_default`).
- **Concern:** the deep-copy at to_dict / from_dict time uses `copy.deepcopy(record)` per nation. With many wars × many nations × many episodes, this is O(N) per save. Acceptable for save/load (rare); flag if anything per-turn calls `to_dict()` (it shouldn't, but verify).

### 7 — Merge hook handling B1 shape (spec §7.6 + impl plan line 101)

`_rewrite_absorbed_war_id_in_contribution` in `settlement_helpers.py` was updated to handle the real B1 dict shape (was previously placeholder int summing).

Verify:

- Empty container is silent no-op (test `test_rewrite_absorbed_war_id_in_contribution_no_op_when_container_empty`).
- Single absorbed war_id moves records to survivor (test `test_rewrite_absorbed_war_id_in_contribution_moves_records_to_survivor`).
- Collision case: episodes union (survivor wins), historical_total sums (test `test_rewrite_absorbed_war_id_in_contribution_sums_historical_total_on_collision`).
- Drives through real `merge_war_instances` without crashing (test `test_rewrite_absorbed_war_id_in_contribution_via_merge_war_instances_no_crash`).
- **Spec impl plan line 101:** "A3 does not preserve pre-merge contribution percentages as settlement standing." So the merge is best-effort — surviving war_id ends up with all data, but episode_ids may have stale `war_sequence` substrings. Is that acceptable? Spec §7.6 line 574 says "war_sequence is the surviving war_instance.created_sequence" — a strict reading would require post-merge re-keying of every absorbed episode_id from `{nation}_{absorbed_seq}_{idx}` → `{nation}_{surviving_seq}_{idx}`. B1 does NOT do this. **Discuss:** is post-merge re-keying a B-slice TODO, or a correctness bug in B1? Argue both ways.

### 8 — `war_leader_score` contribution share wiring

`settlement_helpers.py::war_leader_score` was changed from a placeholder `isinstance(value, (int, float))` check to reading `material_contribution_share` via inline `from backend.game_logic.war_contribution import material_contribution_share`.

- Verify: with B1 store empty (no emitters), `material_contribution_share` returns `0.0`, `int(0.0 * 50)` = `0`, so the contribution component is 0 — same behavior as the placeholder. Test `test_war_leader_score_empty_safe_when_no_contribution_recorded` covers this.
- **Concern:** the inline import inside the function body fires on every call. Is `war_leader_score` in any hot path? The merge transaction calls it once per side per merge (rare). Cascade leader replacement calls it during war-entry (also rare). Acceptable; flag if anything per-turn calls it.
- The `try ... except ImportError` swallows the import failure with `pass`. **Question:** when would the import legitimately fail? `war_contribution` is a leaf module with no imports of its own — circular import is impossible. Is the `try/except` defensive paranoia, or does it mask a real risk? Argue.

### 9 — Test coverage adequacy

55 new tests in `tests/test_war_contribution_scores.py`. The implementation plan (line 184) caps Slice B sub-gates at 50-55 tests per session. Verify:

- All B1 acceptance bullets (impl plan §"Slice B" B1 lines) have at least one test:
  - Data shape — covered.
  - Save/load defaults — covered (forward + backward + deep-copy).
  - Old-record adapter — covered (4 variants).
  - Current-episode model — covered (lifecycle, totals, material exclusion).
  - Material-contribution gate — covered (staying-power exclusion at side level).
  - Contribution-share query helpers — covered (zero-safety in both denominators).
  - Pure contribution-derived standing inputs — covered (full §8.2 matrix).
- **Gap candidates:**
  - Is there a test confirming the spec §9.1 line 568 "leader auto-seats when total side contribution = 0" override? B1 does NOT implement this — should there be a TODO comment or an explicit "B1 doesn't own this" test?
  - Is there a test confirming the `is_active_same_side=False` branch — i.e., a participant who has exited the war? Test `test_classify_standing_no_standing_when_inactive_and_no_term_inputs` covers it but only for the no-input case.
  - Is there a test confirming the `is_treaty_ally_materially_involved` does NOT fire under the vassal cap? Implicit in `test_classify_standing_vassal_blocks_bargain_and_survival_promotion` but not exhaustively.
  - Is there a test for `iter_active_episodes` returning `[]` when the war_id is unknown? Implicit (would no-op via `_get_war_dict`'s empty default) but not asserted.
  - **Spec §9.6 multi-participant attribution from old records:** spec line 756 says "No retroactive multi-participant attribution is attempted for old saves; old records count as single-nation participation." B1's adapter delivers single-nation theater_strength fallback when no `nation_theater_strength` field — confirm test coverage proves this is single-nation, not multi-participant.

### 10 — Golden rules + style

- **Golden rule 8 (no per-region scans in hot paths):** the contribution module reads `world.war_instances`, `world.war_contribution_scores` — no `world.regions.values()` walks. ✓
- **Golden rule 4 (state clearing after reading):** `close_episode_for_exit` does NOT clear `current_episode_id`, intentionally — same-turn battle / occupation / support readers may still need to attribute events after the exit stamp under correct event ordering (spec §9.5 line 740). Confirm this is the correct policy and that no consumer would ever read a stale current_episode_id after exit.
- **Golden rule 6 (LLM never affects mechanics):** B1 has no LLM surface. ✓
- All numeric fields stay int — `historical_total`, bucket counts, `joined_turn`, `exited_turn`, `total`. Shares are float (consumer math). Casts via `int(...)` at write boundaries.
- No new floats leak into to_dict / from_dict.
- `classify_standing` accepts all-kwargs to avoid positional-arg drift; verify no positional-arg call sites exist that would break if a kwarg is reordered.

### 11 — Cross-slice gating

B1 must NOT invent B2/B3/C/D behavior. Verify:

- No emitter functions exist (no `accrue_battle_contribution`, no `record_occupation_event`, etc). B2 owns these.
- No per-turn lifecycle hooks (no `advance_turn` insertion, no auto-call to `open_episode` / `close_episode_for_exit`). B3 owns these.
- No common-peace term legitimacy / War Bargain settlement classification / Slice C/D reaction routing. The classifier accepts term-derived booleans verbatim — B1 callers default them to `False`.
- `world.war_contribution_scores` is NOT mutated by any non-test code path landing in this commit.

### 12 — Documentation routing

- `CLAUDE.md` "Current Phase" peace deals bullet — updated to reflect B1 landed and B2 as next gate.
- `STATUS.md` "Next diplomacy workflow" — updated.
- `SAVE_FORMAT_REFERENCE.md` — `war_contribution_scores` row updated from "Planned (B)" to landed shape.
- Plan doc (`WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md`) — was the B1 gate already documented? Check whether it should be marked "DONE" or whether the plan intentionally tracks status only in STATUS.md.

## Verification commands

```
".venv/Scripts/python.exe" -m pytest tests/test_war_contribution_scores.py tests/test_war_settlement_merge.py tests/test_war_settlement_instances.py tests/test_war_settlement_foundation.py -v
".venv/Scripts/python.exe" -m pytest tests/ --tb=short -q
".venv/Scripts/python.exe" -m ruff check backend/ tests/
```

Expected: full suite `9431 passed, 1 skipped` (post-A3 baseline was `9373 passed, 1 skipped`; net +58, with 55 new B1 tests + 3 implicit gains from the migrated A3 tests). Ruff clean.

## Output format

For each section above, write **one of**:

- `OK` — verified correct with reasoning.
- `MINOR` — issue found, non-blocking. Describe and propose a fix.
- `BLOCKER` — issue must be fixed before merge. Describe with file:line and concrete repro / fix.

Then a short **Summary** section: blocker count, minor count, any spec-divergence concerns, and one paragraph on whether B1 looks ready to handoff for Slice B2 (event emitters).

Be skeptical of:

- Any place B1 silently invents B2/B3/C/D behavior.
- Any place the standing classifier returns the wrong tier for an edge-case spec rule (especially the vassal cap and the minor + rival_strengthened gate).
- Any zero-denominator path that could divide by zero, NaN, or fall through to non-contribution rules differently from spec §9.1.
- Old-record adapter divergence from spec §9.6 lines 747-754 (especially edge cases like missing attacker/defender, missing region alias).
- Merge hook losing data on collision when episodes from absorbed wars share an id with surviving episodes (currently survivor wins; spec §7.6 line 574 implies post-merge re-keying — discuss).
- Inline imports that mask real failures (the `try/except ImportError` in `war_leader_score`).

The repo CLAUDE.md is the authoritative project guide; treat its golden rules as binding.
