# Codex code review — Imperial Settlement Slice B3 lifecycle

You are reviewing commit **`4494d23` on branch `master`** of `mitchsuch-star/project-sovereign-map` (Napoleonic strategy game; FastAPI backend, Godot frontend). Pull that exact SHA and review against parent `15128cb`.

```
git fetch origin && git checkout 4494d23
git diff 15128cb..4494d23 --stat
```

## What this commit does

Lands the **Slice B3 lifecycle sub-gate** of the Imperial Settlement / Ally Participation contribution tracker. B3 closes the contribution-episode lifecycle for every war-entry / exit seam, adds per-turn staying-power accrual, and adds archive compaction once a `war_instance` clears the 10-turn retention window.

This is the FINAL Slice B sub-gate. Prior B-slice landings:

1. **B1** (commits `0bc572b` and earlier) — data shape, episode helpers (`canonical_episode_id`, `open_episode`, `close_episode_for_exit`, `current_episode`, `iter_active_episodes`), share/standing math, `adapt_legacy_battle_record`, pure `classify_standing`. Already landed.
2. **B2 ordering guard** (commit `7974474`) — the `accrue_battle_contribution(...)` entrypoint + `record_battle()` ordering pin. Already landed.
3. **B2 emitter call-site wiring** (commit `df991b0`) — theater-aware `_post_combat_pipeline()` / `_execute_attack()` inline / auto-dispatch charge updates with `detect_battle_theater(...)`. Already landed.
4. **B2 non-battle emitters** (commits `eb333ed` + `15128cb` review fix) — occupation event accrual (capture path + treaty cede + vassal liberation), support event accrual (one-time + per-turn treaty clauses + British coalition subsidy), episode-id dedupe and access/supply cap, AP-floor-respecting support attribution. Already landed.
5. **B3 lifecycle (this commit)** — open/close episode wiring at every WAR-entry / exit seam, per-turn staying-power, archive compaction, and full-Europe lifecycle fixtures.

This commit ships:

- `backend/game_logic/war_contribution.py`:
  - `STAYING_POWER_PER_TURN = 5`, `STAYING_POWER_TURN_CAP = 10`, `STAYING_POWER_RAW_CAP = 50` constants (spec §9.2 line 612).
  - `accrue_staying_power_for_war(world, war_id, *, current_turn) -> Dict[str, int]` — per-war walker. Idempotent per `(war_id, nation, current_turn)` via `last_staying_power_turn` + `staying_power_credited_turns` counters on each episode.
  - `accrue_staying_power_all_wars(world, *, current_turn) -> Dict[str, Dict[str, int]]` — active war_instance walker. Skips `ended_turn`-stamped instances.
  - `compact_war_contribution_for_archive(world, war_id, *, archived_turn) -> Optional[Dict[str, Any]]` — drops episode detail, sums per-bucket finals, moves to `world.archived_war_contribution_scores`.

- `backend/game_logic/settlement_helpers.py`:
  - `_open_contribution_episode_for_participant(world, war_id, nation, *, joined_turn)` — idempotent `open_episode` wrapper. No-op on active episode; opens fresh episode after exit.
  - `_close_contribution_episode_for_participant(world, war_id, nation, *, exited_turn, exit_path="")` — idempotent `close_episode_for_exit` wrapper.
  - `_create_skeleton_instance` opens episodes for originator + origin target (B3 hook at line 567 area).
  - `attach_pair_to_war_instance` opens episodes for both pair nations at the CURRENT attach turn (NOT the participant_meta.joined_turn — re-entry needs the new turn per spec §7.5).
  - `attach_participant_to_war_instance` opens episode for the new participant at the current attach turn.
  - `mark_participant_eliminated_in_all_wars` closes episodes per spec §7.4 line 453.
  - `resolve_pair_to_resolved` extended to:
    - Detect each pair-nation's remaining active pairs in the same war_instance.
    - For nations with no remaining active pair, remove from `active_participants` / `attackers` / `defenders` / `side_by_nation`, stamp `participant_meta[nation]["exited_turn"] / ["exit_path"] = "separate_peace"`, and close their episode.
    - When `end_reason="all_pairs_resolved"` stamps (war just ended), close every still-active participant's episode with `exit_path="war_ended"`.
    - New helper `_pair_nations(pair)` and `_nation_has_remaining_active_pair(instance, nation)` for these checks.
  - `archive_terminal_war_instances` extended to call `compact_war_contribution_for_archive(world, war_id, archived_turn=turn)` for every archived war_id AFTER the war_instance moves to `archived_war_instances`.

- `backend/game_logic/diplomacy.py`:
  - `cleanup_war_end(world, diplo_key, *, conclude_objectives=True)` — when `conclude_objectives` is True (PEACE outcome), calls `resolve_pair_to_resolved(world, diplo_key)`. Idempotent against the existing armistice-expired-peace call at `_process_armistice_expiration` line 8809 (the second invocation no-ops with `error="pair_not_owned"`).
  - `process_diplomacy_turn` step 7b: `accrue_staying_power_all_wars(world, current_turn=...)` runs BEFORE step 8 (armistice expiration). This ensures episodes about to close on this turn still capture staying-power under the inclusive `event.turn <= exited_turn` boundary (spec §9.5 line 740).

- `backend/models/world_state.py`:
  - `self.archived_war_contribution_scores: Dict[str, Dict[str, Any]] = {}` field initialized to `{}`.
  - `to_dict()` serializes the new container with `copy.deepcopy` per record.
  - `from_dict()` defaults to `{}` for pre-B3 saves.

- `tests/helpers/full_europe_settlement_fixtures.py`:
  - `build_three_theater_full_europe_fixture(world)` — single 9-participant Coalition war spanning German + Iberian + Russian theaters. Returns `{war_id: instance}`.
  - `build_concurrent_war_lifecycle_fixture(world)` — Russia bridges two independent active wars. Returns `(war_x_id, war_y_id)`.
  - `build_archive_retention_fixture(world, *, ended_turn, current_turn)` — terminal France-vs-Austria war with controllable `ended_turn` / `current_turn` for boundary tests. Strips diplomatic_states WAR stamp + moves pair to resolved_diplo_keys so the invariant assertion stays clean.

- `tests/test_war_contribution_scores.py`:
  - 27 new B3 tests (144 total in file, was 117). Categories: 6 staying-power, 5 open-episode wiring, 6 close-episode wiring, 2 same-turn ordering, 2 concurrent-war independence, 1 three-theater, 5 archive retention/compaction.

**Out of scope (must NOT be invented in this commit):**

- Slice C/D term-derived booleans flowing through `classify_standing` (settlement standing readers, dispatch / ledger / paradox routing, common-peace term legitimacy, War Bargain settlement classification).
- Settlement memory mutation, settlement gratitude / sold-out memory writes.
- Common-peace ratification sub-transaction with cross-war reaction routing.
- Any Slice C `pending_settlement_dialogues` or `settlement_route_payloads` writes (the rewrite hooks are no-op-safe for absent containers per A3).
- Any change to the existing B1/B2 emitter contracts (`accrue_battle_contribution`, `accrue_occupation_event`, `accrue_support_event`, `detect_battle_theater`, `resolve_british_subsidy_war_id`).
- Any change to the war_instance invariant assertion in `assert_war_instance_invariants`.

## Authoritative spec / plan / context

Read these in this order before reviewing the code:

1. `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` — specifically:
   - §7.4 elimination exit (line 451-454: "Remove the nation from `active_participants`. Stamp `participant_meta[nation]["exited_turn"] = world.current_turn` and `exit_path = "eliminated"`. Close the active episode with the same `exited_turn`. Freeze contribution through the elimination turn.").
   - §7.5 mid-war joiners and re-entry — episode_id canonicalization, `joined_turn` semantics, re-entry creates a NEW episode per spec line 421-424, inclusive `exited_turn` boundary.
   - §9.2 line 612 — `staying_power_raw = min(active_turns, 10) * 5`.
   - §9.5 line 178 — retention window: "Retain `war_contribution_scores[war_id]` while the war is active and through the 10-turn terminal `war_instance` retention window. On archive, compact to final per-nation totals."
   - §9.5 line 740 — same-turn event ordering: "battle, occupation, and support events for the turn must be emitted before elimination, separate-peace, or settlement exits stamp `exited_turn`. The inclusive `event.turn <= exited_turn` boundary in section 7.5 is correct only under that ordering."

2. `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` Slice B build bullets — specifically the **B3** sub-gate ("turn-order/exits, same-turn separate peace, archive compaction, concurrent-war independence, contribution threshold signals, and three-theater / support-only major fixtures") and the gate criteria ("Three-theater full-Europe fixture proves a 6+ participant war across distant fronts does not create zero contribution for a front's real fighters and does not credit all same-side participants across unrelated fronts. Same-turn AI separate-peace plus battle fixture proves the exiting nation keeps that turn's battle contribution before `exited_turn` is stamped. Concurrent-war fixture covers one nation active in two `war_instance` records and proves each war's staying-power/support totals advance independently. Archive-retention fixture proves contribution totals survive raw battle-record pruning and compact after the terminal retention window.").

3. `docs/PEACE_DEALS_UMBRELLA_SPEC.md` — cross-slice gating (B3 must NOT invent Slice C/D presentation surface, common-peace term legitimacy, or settlement memory routing).

4. `CLAUDE.md` — golden rules. Especially: rule 8 (no per-region scans in hot paths — `accrue_staying_power_all_wars` walks `world.war_instances` ONCE per turn; `compact_war_contribution_for_archive` runs only when archive_terminal_war_instances picks up a terminal record), rule 6 (LLM never affects mechanics), rule 4 (state clearing AFTER reading — per-turn staying-power reads + writes the episode in one pass).

5. The previous review prompts: `codex_review_prompt_b1.md`, `codex_review_prompt_b2_ordering_guard.md`, `codex_review_prompt_b2_emitter_wiring.md` — context for what each B sub-gate already shipped.

## Files changed (10 files, +1423 / -17)

```
CLAUDE.md                                          ← Current Phase peace deals bullet updated
backend/game_logic/diplomacy.py                    ← cleanup_war_end PEACE → resolve_pair_to_resolved + per-turn staying-power
backend/game_logic/settlement_helpers.py           ← B3 open/close hooks wired into every entry/exit seam + archive compaction
backend/game_logic/war_contribution.py             ← +accrue_staying_power_for_war + accrue_staying_power_all_wars + compact_war_contribution_for_archive + STAYING_POWER constants
backend/models/world_state.py                      ← archived_war_contribution_scores field + save/load
docs/SAVE_FORMAT_REFERENCE.md                      ← documents new field + B3 episode counters
docs/STATUS.md                                     ← Last Updated entry for B3 landing
docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md ← B3 status COMPLETE
tests/helpers/full_europe_settlement_fixtures.py   ← +build_three_theater_full_europe_fixture / build_concurrent_war_lifecycle_fixture / build_archive_retention_fixture
tests/test_war_contribution_scores.py              ← 27 new B3 tests (+staying-power, +wiring at every seam, +ordering, +concurrent-war, +three-theater, +archive)
```

## What to verify (priority-ordered)

### 1 — `accrue_staying_power_for_war()` correctness against spec §9.2 line 612

Look at `backend/game_logic/war_contribution.py::accrue_staying_power_for_war` and confirm:

- **Per-turn increment:** Each call adds exactly `STAYING_POWER_PER_TURN = 5` raw points to `episode["staying_power"]` and the same delta to `episode["total"]`. Verify `_episode_total` math is unaffected (the test `test_accrue_staying_power_for_war_adds_5_per_turn_to_active_episodes` locks this).
- **10-turn cap:** After 10 calls (at distinct `current_turn` values), `staying_power == 50` and subsequent calls no-op. **Concern:** the cap implementation increments `staying_power_credited_turns` BEFORE the cap check; a buggy off-by-one would let an 11th turn through. Walk through the loop and confirm: `if credited >= STAYING_POWER_TURN_CAP: continue` (line ~1779) skips the increment. The test `test_accrue_staying_power_caps_at_10_qualifying_turns` runs 18 turns and asserts cap.
- **Idempotency per (war_id, nation, current_turn):** Re-running on the same `current_turn` is a no-op. The guard is `if last_turn is not None and int(last_turn) >= int(current_turn): continue`. **Concern:** what happens if the caller passes a SMALLER `current_turn` than the last credited? The current logic skips (the `>=` test), which is correct because staying-power should only accrue forward. Argue.
- **Joined-turn floor:** `if joined is not None and int(current_turn) < int(joined): continue` skips episodes that haven't started yet. **Concern:** when does this trigger in practice? An episode with `joined_turn=15` accrued for `current_turn=14`? That can't happen in the live wiring because `process_diplomacy_turn` only walks the current turn forward. Flag whether this guard is dead defensive code or there's a real edge case.
- **Closed-episode skip:** `iter_active_episodes` already filters out episodes with `exited_turn` set. The accrual loop is consistent with that. The test `test_accrue_staying_power_skips_closed_episodes` locks this.
- **Ended-war-instance skip:** `if instance.get("ended_turn") is not None: return accrued` short-circuits. The test `test_accrue_staying_power_skips_ended_war_instances` locks this. **Concern:** what about a `war_instance` whose `ended_turn` was set THIS turn? Per spec §9.5 line 740 (events before exits), staying-power for the turn should fire BEFORE the war ends. The `process_diplomacy_turn` placement (step 7b, before armistice expiration in step 8) ensures staying-power for the war-ending turn lands before `_process_armistice_expiration` stamps any `ended_turn`. Argue whether this ordering covers all `ended_turn`-stamping seams (separate peace via `_ratify_treaty` happens during command execution, BEFORE `advance_turn`; common peace via Slice C is not yet wired).
- **Returns dict:** The accrued snapshot dict is returned for tests/debug; production callers (`accrue_staying_power_all_wars`) use it as a snapshot only.

### 2 — `compact_war_contribution_for_archive()` correctness against spec §9.5 line 178

Look at `backend/game_logic/war_contribution.py::compact_war_contribution_for_archive` and confirm:

- **Drop episode detail:** The compacted record does NOT include `episodes` — it sums each bucket across ALL episodes (active or closed) for each nation. The shape is `{war_id, archived_turn, per_nation_totals: {nation: {battle, occupation, staying_power, support, total, material_total, episode_count, first_joined_turn, last_exited_turn, historical_total}}}`.
- **Bucket sums:** `bucket_totals[bucket]` accumulates `int(episode.get(bucket) or 0)` for each of the four buckets. The test `test_archive_compaction_handles_multiple_episodes_per_nation` exercises a France with TWO episodes (original + re-entry) and asserts the compacted totals union both. Verify the bucket sums match Python integer addition (no int overflow concerns at game-realistic values; max ~10K per bucket per episode).
- **Material total:** `sum(bucket_totals[b] for b in MATERIAL_BUCKETS)` excludes staying_power per spec §8.2 / §9.2 — material standing thresholds use this, not total. Verify the test asserts `material_total == 55` for `battle=30 + occupation=20 + support=5 = 55` (excluding staying_power=25).
- **Total:** `sum(bucket_totals[b] for b in ALL_BUCKETS)` includes staying_power. Verify the total includes all four buckets.
- **first_joined_turn / last_exited_turn:** Walk every episode, track min joined_turn and max exited_turn. The test `test_archive_compaction_handles_multiple_episodes_per_nation` asserts `first_joined_turn=5` and `last_exited_turn=15` across two episodes.
- **Active store cleanup:** `store.pop(war_id, None)` removes the active record AFTER the archive write. Verify the test `test_archive_retention_window_compacts_at_10_turns` asserts `war_id not in world.war_contribution_scores` AND `war_id in world.archived_war_contribution_scores`.
- **Empty / no-record path:** `compact_war_contribution_for_archive(world, "war_does_not_exist", archived_turn=10)` returns `None` and does NOT create an archived entry. The test `test_archive_compaction_no_op_when_no_contribution_record` locks this. **Concern:** the helper does `store.pop(war_id, None)` even when `war_dict` is falsy (line `store.pop(war_id, None); return None` in the empty path). Verify this doesn't accidentally drop a non-empty record under a race or weird shape. Argue.
- **historical_total:** The compacted per-nation record carries `historical_total` from the source record. **Concern:** `historical_total` is currently never incremented by accrual (the field is only set by B1's `_get_nation_record(create=True)` and modified by the merge transaction). Is it correct that compacted records carry through whatever value `historical_total` had at archive time? Walk through and argue.

### 3 — Episode-open wiring at every WAR-entry seam

Look at `backend/game_logic/settlement_helpers.py` and confirm:

- **`_create_skeleton_instance`** (line ~575): opens episodes for `attacker` and `defender` at `joined_turn=turn` (the war-creation turn). The test `test_create_skeleton_instance_opens_episodes_for_originator_and_target` drives `ensure_war_instance_for_pair(...)` and asserts both episodes exist with `joined_turn=5`.

- **`attach_pair_to_war_instance`** (line ~835): opens episodes for BOTH pair nations at `joined_turn=turn`. **Critical concern (this was a pre-merge bug fix in this commit):** the helper passes `turn` (the current attach turn), NOT `participant_meta.joined_turn` (which would stay at the original join turn for re-entered participants). The test `test_open_episode_after_exit_creates_fresh_re_entry_episode` proves Austria's second episode has `joined_turn=15`, not `joined_turn=5`. Walk through and confirm. **Concern:** for a NEW participant joining a war, `participant_meta.joined_turn` would equal `turn` anyway, so the choice doesn't matter on first join. For a re-attach of the SAME participant whose episode is still active, `_open_contribution_episode_for_participant` no-ops (returns early on the existing active episode), so the choice doesn't matter for re-attach either. The choice ONLY matters for re-entry AFTER exit — which is the spec §7.5 case. Argue whether the wiring covers this correctly.

- **`attach_participant_to_war_instance`** (line ~915): same pattern, opens episode at `joined_turn=turn`. The test `test_attach_participant_to_war_instance_opens_episode` covers this.

- **Idempotent on active episode:** The helper `_open_contribution_episode_for_participant` short-circuits when `current_episode(world, war_id, nation) is not None and existing.get("exited_turn") is None`. The test `test_attach_pair_idempotent_when_episode_already_active` proves a re-attach doesn't create a new episode_id. Verify the helper's check uses `current_episode` (which reads the current_episode_id pointer), not `iter_active_episodes` (which iterates every episode).

- **Re-entry creates fresh episode:** When `current_episode` returns a closed episode (exited_turn set), the helper falls through to `open_episode(...)` which creates a new episode_id via `canonical_episode_id(nation, sequence, next_index)`. Verify `next_index = len(episodes) + 1` so re-entry gives episode_2. The test `test_open_episode_after_exit_creates_fresh_re_entry_episode` asserts `second_episode_id != first_episode_id`.

### 4 — Episode-close wiring at every exit seam

Look at `backend/game_logic/settlement_helpers.py` and confirm:

- **`mark_participant_eliminated_in_all_wars`** (line ~1610-area): after stamping `participant_meta[nation]["exited_turn"]` and removing from `attackers/defenders/active_participants/side_by_nation`, calls `_close_contribution_episode_for_participant(world, war_id, nation, exited_turn=turn, exit_path="eliminated")`. The test `test_mark_participant_eliminated_closes_active_episodes` locks this. **Concern:** the close call is INSIDE the per-war loop, so a nation eliminated across multiple wars gets its episode closed in EACH war. Walk through and confirm.

- **`resolve_pair_to_resolved`** (line ~1075-area): the heart of B3 close wiring. Walk through:
  - Pair is removed from `active_diplo_keys`, moved to `resolved_diplo_keys`, `pair_status = "resolved"`, `resolved_turn` stamped.
  - `war_just_ended = True` if no remaining active pairs (the `end_reason="all_pairs_resolved"` stamp).
  - For each of the two pair nations:
    - If the nation is no longer in `active_participants`, skip (already exited via elimination, etc.).
    - If `war_just_ended` OR `_nation_has_remaining_active_pair` returns False, mark for exit with `exit_path = "war_ended"` or `"separate_peace"`.
  - If `war_just_ended`, capture EVERY remaining `active_participants` entry (not just the pair nations) for `war_ended` exit.
  - For each marked-for-exit participant:
    - Stamp `participant_meta[nation]["exited_turn"] / ["exit_path"]`.
    - Remove from `active_participants / attackers / defenders / side_by_nation`.
    - Call `_close_contribution_episode_for_participant(...)`.
  - Tests:
    - `test_resolve_pair_to_resolved_closes_episode_when_last_pair_resolves` — single-pair war, both nations exit on resolve.
    - `test_resolve_pair_to_resolved_keeps_other_active_pairs_open` — France has Austria + Prussia adversaries; resolving France|Austria exits Austria (no remaining pair) but France stays active (still has Prussia as adversary).
    - `test_resolve_pair_war_end_closes_all_remaining_episodes` — sequential pair resolution; the LAST pair triggers `all_pairs_resolved` and closes every remaining episode.
  - **Concerns:**
    - Is the order of stamping correct? I stamp `participant_meta` FIRST, then remove from active_participants, then close the episode. The episode close uses the captured `turn` (resolved_turn). Walk through and confirm no stale read.
    - Is the `_pair_nations(pair)` helper safe against malformed input? It returns `(None, None)` on a non-`a|b`-shaped string. The `for nation in (nation_a, nation_b): if not nation: continue` defends. Argue.
    - The `participants_to_exit` list deduplicates nothing — could a nation be added twice (once via the pair-nation loop, once via the `war_just_ended` capture)? Walk through: the `war_just_ended` branch skips nations already in `(nation_a, nation_b)`. Verify.
    - The post-exit `attackers_list[:] = [n for n in attackers_list if n != nation]` mutation pattern — verify this is in-place mutation of the existing list (so external references remain valid).

- **`cleanup_war_end(conclude_objectives=True)`** in `backend/game_logic/diplomacy.py` (line ~4356-area): when `conclude_objectives` is True (PEACE outcome), calls `resolve_pair_to_resolved(world, diplo_key)`. **Concern: idempotency against the existing `_process_armistice_expiration` call.** The armistice expiration path at line ~8809 is:
  ```python
  resolve_pair_to_resolved(world, diplo_key)
  set_diplomatic_state(world, nation_a, nation_b, "PEACE", "armistice_expired_peace")
  cleanup_war_end(world, diplo_key)  # ← also calls resolve_pair_to_resolved now
  ```
  The second call to `resolve_pair_to_resolved` returns `{"ok": False, "error": "pair_not_owned"}` because the pair was already moved to `resolved_diplo_keys` in the first call. Verify this is safe (no duplicate episode close, no double `ended_turn` stamp). The test `test_cleanup_war_end_resolves_pair_for_peace_outcome` locks the PEACE path; the existing armistice-expired test suite continues to pass (full suite green).

- **`cleanup_war_end(conclude_objectives=False)`** (ARMISTICE outcome): does NOT call `resolve_pair_to_resolved`. The test `test_cleanup_war_end_armistice_does_not_resolve_pair` locks this — pair stays in `active_diplo_keys`, episode stays open.

### 5 — Per-turn staying-power placement in `process_diplomacy_turn`

Look at `backend/game_logic/diplomacy.py::process_diplomacy_turn` (line ~8623-area) and confirm:

- **Step 7b** (NEW): `accrue_staying_power_all_wars(world, current_turn=int(getattr(world, "current_turn", 0) or 0))` runs BETWEEN step 4-7 and step 8 (armistice expiration). Specifically, the comment block:
  ```python
  # ── 7b. Per-turn staying-power accrual (Slice B3, spec §9.2 line 612) ──
  # Walks every active war_instance once and adds +5 raw points per
  # active episode per turn, capped at 10 qualifying turns per episode.
  # Placed BEFORE the armistice-expiration step so episodes that close on
  # this turn (ARMISTICE → PEACE) still capture the turn's staying power
  # under the inclusive `event.turn <= exited_turn` boundary (spec §9.5).
  from backend.game_logic.war_contribution import accrue_staying_power_all_wars
  accrue_staying_power_all_wars(
      world, current_turn=int(getattr(world, "current_turn", 0) or 0),
  )
  ```
- **Concern: `current_turn` value at this point.** `process_diplomacy_turn` runs AFTER `current_turn` is incremented in `_advance_turn_internal` (line 4902). So `current_turn` is the NEW turn (T+1), and `accrue_staying_power_all_wars` is crediting the NEW turn's staying power. This is fine for forward-only accrual, but argue whether the "first staying-power credit" semantic is right. An episode joined on turn T (during command phase) has `joined_turn=T`. At the next `advance_turn`, `current_turn` becomes T+1. The staying-power accrual runs at T+1 with the formula's idempotency guard (`last_staying_power_turn` was None before, now becomes T+1) — so the episode gets +5 for the T+1 credit. Is that "1 turn of staying-power for T", or "1 turn of staying-power for T+1"? Both interpretations are defensible per spec §9.2 line 612 (`min(active_turns, 10) * 5`). The implementation effectively says "active for any portion of T+1 already counts". Argue whether this matches spec intent.

- **Function-local import:** `from backend.game_logic.war_contribution import accrue_staying_power_all_wars` inside `process_diplomacy_turn`. Matches the existing pattern in `record_battle()` for `accrue_battle_contribution`. Argue whether the local-import overhead is acceptable (called once per turn vs. once per battle).

### 6 — Archive compaction wiring in `archive_terminal_war_instances`

Look at `backend/game_logic/settlement_helpers.py::archive_terminal_war_instances` (line ~1700-area) and confirm:

- After moving terminal war_instances to `archived_war_instances` and removing from active `world.war_instances`, the helper calls `compact_war_contribution_for_archive(world, war_id, archived_turn=turn)` for every archived war_id.
- The compaction step is wrapped in `if archived_ids:` — no compaction work runs when nothing was archived this turn.
- The compaction import is local: `from backend.game_logic.war_contribution import compact_war_contribution_for_archive`. **Concern:** the import is wrapped in `try/except` with `pragma: no cover — import guard`. Is the guard necessary? `war_contribution` has zero non-stdlib imports of its own and is a leaf module — circular import is impossible. Argue whether the guard is dead defensive code or it serves a purpose (e.g., load-repair tooling without `war_contribution` available).
- **Concern: ordering relative to `invalidate_war_instance_indexes`.** The helper invalidates indexes inside the `if archived_ids:` block AFTER compaction. If compaction needed the indexes, this would be a bug — but compaction only reads `war_contribution_scores` and `archived_war_contribution_scores`, not `war_instances`, so the order is fine. Confirm.
- The tests:
  - `test_archive_retention_window_keeps_episodes_under_10_turns` — `current_turn - ended_turn = 8`, no archive, no compaction.
  - `test_archive_retention_window_compacts_at_10_turns` — `current_turn - ended_turn = 10`, archive + compact.
  - `test_archive_compaction_handles_multiple_episodes_per_nation` — direct compaction of a 2-episode France record.
  - `test_archive_compaction_save_load_round_trip_preserves_archived_totals` — `to_dict / from_dict` round-trip.
  - `test_archive_compaction_no_op_when_no_contribution_record` — empty case.

### 7 — Same-turn separate-peace event ordering (spec §9.5 line 740)

Look at `tests/test_war_contribution_scores.py::test_same_turn_battle_credits_before_separate_peace_exit_stamp` and verify:

- A battle accrues into the active episode FIRST.
- The episode is then closed via `close_episode_for_exit(...)` with `exited_turn = current_turn`.
- The battle credit is preserved on the closed episode (the inclusive boundary `event.turn <= exited_turn` keeps it).

**Concern:** the test drives the helpers directly rather than executing a real player command + `_ratify_treaty` + `advance_turn` flow. Does this end-to-end ordering actually match production? In production:
1. Command phase: player ratifies separate peace → `_ratify_treaty` → `cleanup_war_end(conclude_objectives=True)` → `resolve_pair_to_resolved` → episode closes with `exited_turn = current_turn` (T).
2. Same turn battles fire BEFORE step 1 (battles happen earlier in the command phase).
3. So battle credit lands on the open episode, then exit stamp happens, then the inclusive boundary preserves credit.

The test exercises the helper sequence but not the real `_ratify_treaty` invocation. The contract being tested is: **events first, then exit stamp, then boundary check preserves credit.** Argue whether the test should additionally drive a real `_ratify_treaty` flow with battle records on the same turn.

### 8 — Concurrent-war independence

Look at `tests/test_war_contribution_scores.py::test_concurrent_wars_accrue_staying_power_independently` and `test_concurrent_war_close_does_not_affect_other_war`:

- Russia is active in both `war_x` (vs France) and `war_y` (vs Ottoman).
- `accrue_staying_power_all_wars` accrues `+5` to Russia's episode in EACH war independently.
- Closing Russia's episode in `war_x` does NOT affect Russia's episode in `war_y`.

Verify the `iter_active_episodes` walker is per-war_id (not per-nation across wars), and the close/open helpers all take `war_id` explicitly. The test fixture `build_concurrent_war_lifecycle_fixture` puts Russia on opposite SIDES in the two wars (defender in `war_x`, attacker in `war_y`) — verify the side-by-nation maps stay distinct per war_instance.

### 9 — Three-theater fixture (spec §9.4 line 717 / line 725)

Look at `tests/test_war_contribution_scores.py::test_three_theater_fixture_does_not_credit_distant_front_participant`:

- 9-participant war (France/Saxony/Bavaria attackers vs Austria/Russia/Prussia/Britain/Spain/Portugal defenders).
- A battle in Saxony (German theater) with France attacking Austria.
- The battle uses LEGACY adapter mode (no theater payload supplied), so `accrue_battle_contribution` falls back to single-attacker / single-defender. France and Austria get credit; Spain and Portugal (Iberian theater participants) get ZERO.
- This locks the spec §9.4 line 725 whole-war-credit prohibition for the legacy path.

**Concern:** the test does NOT exercise the FULL theater detection path (`detect_battle_theater`) because the test fixture doesn't seat marshals. The B2 emitter wiring tests already cover theater detection; this B3 test specifically locks the legacy fallback's distant-front exclusion. Argue whether this is the right contract for B3 (vs. a marshal-seated theater test which would belong in B2).

### 10 — Archive retention boundary at 9 / 10 turns

Look at `tests/test_war_contribution_scores.py::test_archive_retention_window_keeps_episodes_under_10_turns` and `test_archive_retention_window_compacts_at_10_turns`:

- `ARCHIVE_RETENTION_TURNS = 10` (defined in `settlement_helpers.py`).
- Boundary: `current_turn - ended_turn >= ARCHIVE_RETENTION_TURNS` triggers archive.
- 9 turns: no archive, no compaction (active store still has the war_id, archived store does not).
- 10 turns: archive + compaction (active store no longer has war_id, archived store does).

**Concern:** the tests use `build_archive_retention_fixture` which directly stamps `instance["ended_turn"]` and pre-populates `resolved_diplo_keys` to satisfy invariants. Verify the fixture doesn't leak invariant violations (the invariant assertion would catch a pair_status mismatch).

### 11 — Save/load round-trip of `archived_war_contribution_scores`

Look at `backend/models/world_state.py::to_dict` and `from_dict` for the new field:

- `to_dict`: serializes `archived_war_contribution_scores` with `copy.deepcopy(record)` per war_id (spec §SAVE_FORMAT compatibility).
- `from_dict`: defaults to `{}` for pre-B3 saves (`data.get("archived_war_contribution_scores") or {}`).
- The test `test_archive_compaction_save_load_round_trip_preserves_archived_totals` builds a synthetic archived record, round-trips through `to_dict / from_dict`, and asserts the per-nation totals survive.

**Concern:** the `(data.get(...) or {})` pattern handles missing keys AND `None` values. Verify pre-B3 saves with no `archived_war_contribution_scores` key load cleanly. Verify the field appears in `to_dict` output (a missing serialization would silently drop the data).

### 12 — Cross-slice gating (B3 scope discipline)

The commit must NOT ship Slice C/D presentation surface, common-peace term legitimacy, or settlement memory writes. Verify:

- No new functions in `war_contribution.py` for term-derived booleans (`classify_standing` already accepts them; B3 does not change the signature).
- No new `pending_settlement_dialogues` writes — Slice C owns dialogue creation.
- No new `settlement_route_payloads` writes — Slice C owns route payload writes.
- No new `settlement_memories` field — Slice D owns settlement memory.
- No new `betrayal_history.grievance_flags` writes — Slice D owns grievance memory.
- The `_open_contribution_episode_for_participant` / `_close_contribution_episode_for_participant` helpers only touch `war_contribution_scores` / `archived_war_contribution_scores` — they do NOT write to `participant_meta` (that's existing settlement_helpers responsibility).
- `accrue_staying_power_*` only writes `episode["staying_power"]`, `episode["total"]`, `episode["staying_power_credited_turns"]`, and `episode["last_staying_power_turn"]`. No `episode["battle"]`, `episode["occupation"]`, `episode["support"]` writes.

### 13 — Golden rules + style

- **Golden rule 8 (no per-region scans in hot paths):** `accrue_staying_power_all_wars` walks `world.war_instances` ONCE per turn (~20 active wars at full-Europe scale). `compact_war_contribution_for_archive` runs ONLY when `archive_terminal_war_instances` picks up a terminal record (rare). `_open_contribution_episode_for_participant` / `_close_contribution_episode_for_participant` are O(1) dict lookups. ✓
- **Golden rule 6 (LLM never affects mechanics):** B3 has no LLM surface. ✓
- **Golden rule 4 (state clearing AFTER reading):** The per-turn staying-power helper reads `current_episode_total`, then writes `+5` — single pass, no stale-read risk. ✓
- All numeric fields stay int — `STAYING_POWER_PER_TURN`, `STAYING_POWER_TURN_CAP`, episode field arithmetic.
- No new floats leak into `to_dict` / `from_dict` — `archived_war_contribution_scores` carries int-only buckets.
- `accrue_staying_power_for_war` / `accrue_staying_power_all_wars` / `compact_war_contribution_for_archive` accept all-kwargs.
- `__all__` in `war_contribution.py` exports the new constants and functions.
- Test helpers (`build_three_theater_full_europe_fixture`, `build_concurrent_war_lifecycle_fixture`, `build_archive_retention_fixture`) live in `tests/helpers/full_europe_settlement_fixtures.py` per the Full-Europe Test Fixture Contract.

### 14 — Test coverage adequacy

27 new tests (144 total in file). Categories per impl plan B3 gate:

- **Staying-power (6 tests):** per-turn accrual / cap / idempotency / closed-episode skip / ended-war skip / all-wars walker.
- **Open-episode wiring (5 tests):** skeleton, pair attach, participant attach, idempotent re-attach, post-exit re-entry.
- **Close-episode wiring (6 tests):** elimination, separate-peace single-pair, separate-peace with other pairs (war continues), all-pairs-resolved war-end, cleanup_war_end PEACE, cleanup_war_end ARMISTICE no-op.
- **Same-turn ordering (2 tests):** battle before exit stamp, per-turn staying-power before armistice expiration.
- **Concurrent wars (2 tests):** independent staying-power, independent exit.
- **Three-theater (1 test):** distant-front exclusion via legacy adapter.
- **Archive retention/compaction (5 tests):** under 10 turns, at 10 turns, multi-episode compaction, save-load round trip, no-op for missing record.

**Gap candidates:**

- **Vassal rebellion seam (open):** The `vassal.py::check_vassal_rebellion` and `release_vassal(rebellion=True)` flows go through `ensure_war_instance_for_pair`, which calls `_create_skeleton_instance`, which opens episodes. So the wiring IS exercised, just not with an explicit B3 test. Flag whether a vassal-rebellion-specific B3 test would add value.
- **Counter-bargain seam (open):** Similar — `accept_counter_bargain` goes through `ensure_war_instance_for_pair`. Flag.
- **ARMISTICE → WAR resumption (open):** `_process_armistice_expiration` armistice→war path calls `ensure_war_instance_for_pair`. The episode wasn't closed during ARMISTICE (per spec §7.5 armistice is a pause, not exit), so `_open_contribution_episode_for_participant` no-ops on the active episode. Flag whether a behavioral test would add value.
- **Common-peace leader-side war end (close):** Slice C will introduce `end_reason="common_peace_finalized"` which is NOT yet wired. The `war_ended` exit_path covers `all_pairs_resolved` — but a Slice C common peace might bypass `resolve_pair_to_resolved` per pair and instead bulk-end. Flag whether B3's exit wiring is sufficient for the Slice C handoff.
- **Archive compaction under "live reference" (spec §9.5 line 178 unless clause):** Spec says "On archive, compact to final per-nation totals UNLESS a live dialogue, dispatch route, ledger row, campaign-log detail, or settlement memory still references episode detail." B3's compaction is unconditional — it always drops episode detail. The "unless" clause is a future Slice C/D concern. Argue whether this is correct B3 scope or whether the compaction should at least gate on `pending_settlement_dialogues` / `settlement_route_payloads` references (the no-op-safe rewrite hooks already exist in `settlement_helpers.py`).
- **Per-war staying-power cap interacting with re-entry:** When a participant exits and re-enters the same war, a NEW episode_id is created (spec §7.5). The new episode starts fresh with `staying_power_credited_turns = 0`, so the cap restarts. Walk through whether this is the correct spec intent (vs. tracking the cap at the per-nation-per-war level across all episodes).

### 15 — Documentation routing

- `CLAUDE.md` "Current Phase" peace deals bullet — updated to reflect B3 lifecycle landed and Slice C as next.
- `STATUS.md` "Last Updated" — new entry for B3 landing with full surface description.
- `docs/SAVE_FORMAT_REFERENCE.md` — `archived_war_contribution_scores` field added to the JSON shape and the Pending Imperial Settlement table; `war_contribution_scores` row updated to reflect B3 staying-power counters and lifecycle wiring.
- `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` — B3 build bullet marked **Status May 3, 2026: COMPLETE** with full surface description.
- Verify CLAUDE.md "Up Next" handoff sentence reflects B3 lifecycle landed (not the prior "B3 LIFECYCLE IS NEXT" sentence).

## Verification commands

```
".venv/Scripts/python.exe" -m pytest tests/test_war_contribution_scores.py tests/test_war_settlement_merge.py tests/test_war_settlement_instances.py tests/test_war_settlement_foundation.py -v
".venv/Scripts/python.exe" -m pytest tests/ --tb=short -q
".venv/Scripts/python.exe" -m ruff check backend/ tests/
```

Expected: full suite `9520 passed, 1 skipped` (post-B2-non-battle-review-fix baseline was `9493 passed, 1 skipped`; net +27, all in `tests/test_war_contribution_scores.py`). Ruff clean.

## Output format

For each section above, write **one of**:

- `OK` — verified correct with reasoning.
- `MINOR` — issue found, non-blocking. Describe and propose a fix.
- `BLOCKER` — issue must be fixed before merge. Describe with file:line and concrete repro / fix.

Then a short **Summary** section: blocker count, minor count, any spec-divergence concerns, and one paragraph on whether the B3 lifecycle looks ready to handoff for Slice C (common-peace term legitimacy, settlement standing readers, dispatch / ledger / paradox routing) or whether the wiring needs a fix-up pass first.

Be skeptical of:

- Any place an entry seam is missed (`vassal.py`, `meta_executor.py` debug seams) and a contribution episode silently fails to open.
- Any place an exit seam is missed (a separate-peace path that bypasses `cleanup_war_end`, a vassal-release peace transition, an alliance-paradox war exit) and a contribution episode silently fails to close.
- Any place `iter_active_episodes` is called inside a per-turn or per-region loop (golden rule 8 violation).
- Any place per-turn staying-power double-credits or under-credits because the `last_staying_power_turn` / `staying_power_credited_turns` counters drift between the two writes.
- Any place archive compaction silently drops a record that a Slice C/D dialogue / route payload still references (the spec §9.5 "unless" clause is not yet enforced).
- Any divergence from spec §7.5 episode_id canonicalization for re-entry: `{nation_slug}_{war_sequence}_{episode_index}` where `episode_index` increments by 1 each re-entry.
- Any place `participant_meta[nation]["joined_turn"]` is used as the contribution-episode `joined_turn` instead of the current attach turn (would silently regress the post-exit re-entry case fixed in this commit).
- Any place the `_pair_nations(pair)` helper accepts a malformed pair string and fails open.
- Any divergence from the inclusive `event.turn <= exited_turn` boundary (would lose same-turn battle credit on exit).
- Any place B3 lifecycle silently invents Slice C/D presentation surface, common-peace term legitimacy, or settlement memory writes.

The repo CLAUDE.md is the authoritative project guide; treat its golden rules as binding.
