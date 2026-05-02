# Codex code review — Imperial Settlement Slice B2 non-battle emitters

You are reviewing the latest commit on branch `codex/fix-b1-review-findings` of `mitchsuch-star/project-sovereign-map` (Napoleonic strategy game; FastAPI backend, Godot frontend). Pull the head of that branch and review against parent `df991b0` (the B2 emitter call-site review-fix commit).

```
git fetch origin && git checkout codex/fix-b1-review-findings
git diff df991b0..HEAD --stat
```

## What this commit does

Lands the **Slice B2 non-battle emitters and support attribution** sub-gate of the Imperial Settlement / Ally Participation contribution tracker. B2 splits into three sub-gates per `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` Slice B build bullets:

1. **B2 ordering guard (parent `7974474` + review-fix `14bcf56`)** — already landed.
2. **B2 emitter call-site wiring (parent `df991b0`)** — already landed.
3. **B2 non-battle emitters and support attribution (this commit)** — occupation events, support events with episode-id dedupe, treaty-clause emission, vassal liberation occupation, British coalition subsidy attribution.

This commit ships:

- `backend/game_logic/war_contribution.py`:
  - `OCCUPATION_POINTS` map (20/40/15/15/0 per spec §9.2 line 641; `treaty_transfer` is logged with 0 raw points, never accrued).
  - `OCCUPATION_KINDS` / `SUPPORT_KINDS` / `SUPPORT_SOURCES` / `ACCESS_SUPPLY_CAP` constants.
  - `_episode_accepts_event_turn(episode, turn)` — extracted boundary check (mirrors the per-battle filter, no behavior change).
  - `_resolve_war_id_for_pair_on_opposite_sides(world, actor, target)` — composes `_resolve_active_war_id_for_pair` + side-membership check.
  - `accrue_occupation_event(world, *, actor_nation, region, occupation_kind, from_controller, to_controller, war_id, target_nation, turn, event_id)` — accrues raw points to `episode["occupation"]` + `episode["total"]`; dedupes by `event_id`; filters by episode turn window; emits a `war_occupation_event`-typed payload.
  - `_classify_capture_occupation_kind(world, *, region, actor_nation, from_controller, war_id)` — returns `enemy_capital_captured` if region == `NATION_CAPITALS[from_controller]`, `allied_region_restored` if `get_starting_controllers()[region]` is a same-side ally distinct from actor, else `enemy_region_captured`.
  - `emit_capture_occupation_event(world, *, actor_nation, region, from_controller, turn)` — convenience wrapper for `world_state.capture_region` that resolves war_id + classifies kind + emits.
  - `_support_raw_points(support_kind, value)` — gold/subsidy `// 100`, AP `* 5`, manpower `// 500`, access/supply `1/turn`.
  - `accrue_support_event(world, *, war_id, supporter, recipient, support_kind, value, source, source_detail, turn, event_id)` — same-side filter, episode-id dedupe (deterministic id from `(turn, war_id, supporter, recipient, support_kind, source, source_detail)`), per-`(war_id, supporter, support_kind)` access/supply cap of 5 raw, unattributed-`war_id` logging branch, zero-raw still dedupes.
  - `resolve_treaty_clause_support_war_id(world, supporter, recipient)` — picks oldest `created_sequence` active war where supporter and recipient are same-side allies.
  - `resolve_british_subsidy_war_id(world, *, recipient)` — `unique_eligible` → `matching_coalition_target` → `highest_overlap` → `oldest_sequence` → `unattributed_subsidy` per impl plan / spec §9.2 line 676.
  - `__all__` updated.

- `backend/models/world_state.py`:
  - `capture_region(...)` — emits `emit_capture_occupation_event(...)` BEFORE `_eliminate_nation` (spec §9.5 event-ordering: contribution events fire before exit stamps).
  - `_ratify_treaty(...)`:
    - `gold_lump` clause path now also emits `accrue_support_event(supporter=from_nation, recipient=to_nation, support_kind="gold", source="treaty_clause", source_detail="ratification")` after the transfer; opposite-side flows are filtered by `accrue_support_event` itself, so peace-indemnity gold flows correctly produce no contribution.
    - `territory_cede` clause loop now emits `allied_region_restored` per region when `to_nation != proposer` AND `get_starting_controllers()[region] == to_nation` AND `_resolve_war_id_for_pair_on_opposite_sides(world, to_nation, from_nation)` resolves a war.
    - `liberation` clause path now captures `pre_release_vassal_regions = list(self.get_nation_regions(lib_vassal))` BEFORE `release_vassal(...)` runs, then emits one `liberated_region_restored` event per region credited to `lib_liberator`, attributed to the active war between liberator and former lord.
  - `_process_treaty_clauses(...)` — per-clause `_emit_treaty_support` helper emits `gold_per_turn` (kind="gold"), `manpower_per_turn` (kind="manpower"), `ap_per_turn` (kind="ap") events; same-turn replays dedupe by deterministic episode id.

- `backend/game_logic/coalition.py`:
  - `_process_british_subsidy(world)` — calls `resolve_british_subsidy_war_id(world, recipient=recipient)` then `accrue_support_event(world, war_id=war_id, supporter="Britain", recipient=recipient, support_kind="subsidy", value=200, source="coalition_subsidy", source_detail=source_detail)`. Event payload now also includes `war_id` and `subsidy_source_detail` keys (additive; existing payload fields untouched).

- `tests/test_war_contribution_scores.py`:
  - 33 new B2 non-battle emitter tests:
    - 12 occupation tests (4 occupation kinds + treaty_transfer + dedupe + episode-window filter + 2 `emit_capture_occupation_event` wrapper tests + 2 `capture_region` end-to-end tests).
    - 9 support event tests (self-payment, unknown kind/source, gold to ally, opposite-side filter, dedupe, access/supply cap, unattributed `war_id`, zero-raw dedupe, AP and manpower formulas).
    - 5 British subsidy attribution tests (unique_eligible, matching_coalition_target, oldest_sequence tiebreak, no-eligible unattributed, end-to-end `_process_british_subsidy`).
    - 5 treaty-clause emission tests (gold_lump between allies, territory_cede ally restoration, gold_per_turn, ap_per_turn, same-turn replay dedupe).
    - 2 helper tests (`_setup_war_with_episodes`, `test_emit_capture_occupation_event_classifies_capital_correctly` and non-war return-None guard).
  - One new local helper `_setup_war_with_episodes(...)` builds a war + opens active episodes for every participant.

- `CLAUDE.md` "Current Phase" peace deals bullet, `docs/STATUS.md` "Next diplomacy workflow" line, `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` Slice B B2 bullet, and `docs/SAVE_FORMAT_REFERENCE.md` `war_contribution_scores` row updated to reflect B2 closure and the new dedupe / cap fields on the per-nation record.

**Out of scope (must NOT be invented in this commit):** B3 lifecycle (per-turn staying-power accrual, war-entry seam wiring of `open_episode()` / `close_episode_for_exit()`, same-turn separate-peace event ordering, archive compaction, retention pruning), Slice C/D reactions, `campaign_theater_id` / front-group metadata extension to the theater detector, scripted-AI / explicit-support-command emitters (no current callers in the engine), per-region fan-out for `liberated_region_restored` actor=freed-vassal (the liberator gets credit; freed-vassal credit needs B3 standing-input wiring).

## Authoritative spec / plan / context

Read these in this order before reviewing the code:

1. `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` §9.2 (contribution scoring formula + occupation point values + support raw formulas + access/supply cap), §9.4 (theater attribution + line 622 floor-1 invariant), §9.5 (event-driven performance contract — contribution accrual must not add per-region scans to `advance_turn()`), §9.6 (battle record compatibility, irrelevant here but referenced by `accrue_battle_contribution`).
2. `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` §"Slice B" — specifically the B2 build bullets (occupation, support, treaty-support, British subsidy) and gate criteria. The "non-battle emitters" sub-gate language was added in the B2 emitter call-site wiring commit; this commit closes that scope.
3. `docs/PEACE_DEALS_UMBRELLA_SPEC.md` — cross-slice gating (B2 must NOT introduce B3 lifecycle, Slice C standing reads, or Slice D reactions).
4. `CLAUDE.md` — golden rules, especially:
   - **Rule 8 (no per-region scans in hot paths):** verify `accrue_occupation_event`, `accrue_support_event`, `_resolve_war_id_for_pair_on_opposite_sides`, `resolve_treaty_clause_support_war_id`, and `resolve_british_subsidy_war_id` do not iterate `world.regions.values()`. Walk through each path and confirm.
   - **Rule 6 (LLM never affects mechanics):** B2 emitter wiring has no LLM surface.
   - **Rule 3 (one marshals dict):** N/A here — neither emitter touches marshals.
5. The previous review prompts: `codex_review_prompt_b1.md`, `codex_review_prompt_b2_ordering_guard.md`, `codex_review_prompt_b2_emitter_wiring.md` — historical context for what B1 and the prior B2 sub-gates already shipped.

## Files changed

```
CLAUDE.md                                                            ← Current Phase peace deals bullet refreshed
backend/game_logic/coalition.py                                      ← _process_british_subsidy emits attributed support event
backend/game_logic/war_contribution.py                               ← +OCCUPATION_POINTS, accrue_occupation_event, _classify_capture_occupation_kind, emit_capture_occupation_event, accrue_support_event, resolve_treaty_clause_support_war_id, resolve_british_subsidy_war_id, _episode_accepts_event_turn, _resolve_war_id_for_pair_on_opposite_sides
backend/models/world_state.py                                        ← capture_region, _ratify_treaty (gold_lump + territory_cede + liberation), _process_treaty_clauses (per-turn) call sites
docs/SAVE_FORMAT_REFERENCE.md                                        ← war_contribution_scores row notes new dedupe/cap state
docs/STATUS.md                                                       ← Next diplomacy workflow line refreshed
docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md        ← B2 bullet now reads "May 3, 2026: COMPLETE"
tests/test_war_contribution_scores.py                                ← 33 new B2 non-battle emitter tests + _setup_war_with_episodes helper
```

## What to verify (priority-ordered)

### 1 — `accrue_occupation_event` correctness against spec §9.2

Look at `backend/game_logic/war_contribution.py::accrue_occupation_event` and confirm:

- **Occupation kind dispatch:** `OCCUPATION_POINTS` maps the four "real" kinds to 20/40/15/15. `treaty_transfer` is in the dict at value 0, so it's a valid kind that emits an event but accrues no points (spec §9.2 line 641). Verify the early `if occupation_kind not in OCCUPATION_KINDS` guard accepts `treaty_transfer` while `points > 0` (the actual accrual block) skips it.
- **War_id resolution:** when the caller provides `war_id`, the helper uses it directly. When `war_id` is absent and `target_nation` is supplied, it falls back to `_resolve_war_id_for_pair_on_opposite_sides`. Verify there's no third path (e.g. trying to find a war by region controller alone — that would be a per-region scan).
- **Active-participant filter:** the helper rejects when `active_participants` is non-empty AND `actor_nation not in active_participants`. Walk through the empty-set case: when an instance has no `active_participants`, the filter degrades to "no exclusion" — same convention as `detect_battle_theater` from the prior sub-gate. Argue whether this is safe given A2-wired war_instances always populate `active_participants`.
- **Episode lookup:** `_get_nation_record(world, war_id, actor_nation)` is called WITHOUT `create=True`, so a missing record short-circuits to `return None`. Verify a freshly-opened episode (via `open_episode`) creates the record so this path works correctly. Verify that calling `accrue_occupation_event` on a war_id where the actor never opened an episode is a clean no-op (returns `None`, no mutation).
- **Dedupe storage:** `record.setdefault("seen_occupation_event_ids", [])` initializes a list. The first event with `event_id=X` adds X; second event with same id rejects. Verify this is stored on the per-nation record (not per-episode), so episode boundaries don't reset dedupe. **Concern:** is per-nation the right scope, or should it be per-episode? Spec §9.2 line 670 says "Contribution readers dedupe by `episode_id`", which implies per-event-id global. Per-nation gives global-to-this-nation-in-this-war, which is stronger than per-episode. Argue.
- **Episode turn-window filter:** `_episode_accepts_event_turn(episode, turn)` returns True when `turn` is None (no boundary check) or within `[joined_turn, exited_turn]`. Verify the same-turn-as-exit case (`turn == exited_turn`) accepts (inclusive) — spec §7.5 line 574 requires the inclusive boundary.
- **Mutation order:** when `points > 0`, the helper writes `episode["occupation"]` and `episode["total"]` in that order. Verify there are no other side effects (e.g. `world.invalidate_*_cache` calls that should NOT fire here — occupation accrual does not change region ownership, only contribution scoring).
- **Return shape:** the success payload has `points_accrued`, `episode_id` (the supplied or generated event_id), `turn`, `occupation_kind`, `actor_nation`, `from_controller`, `to_controller`, `region`, `side`, `war_id`. The `treaty_transfer` zero-point case still returns this shape (with `points_accrued=0`). Verify a caller can distinguish "accrued" vs "logged-only" by `points_accrued > 0`.

### 2 — `_classify_capture_occupation_kind` correctness

Look at `backend/game_logic/war_contribution.py::_classify_capture_occupation_kind` and confirm:

- **Capital-first precedence:** the helper checks `NATION_CAPITALS.get(from_controller) == region` BEFORE the ally-restoration check. Walk through: France captures Saxony (Saxony's capital is Dresden, not Saxony — region.NATION_CAPITALS["Saxony"] = "Dresden"). Confirm the capital check fires only when the region literally matches the from_controller's capital. No false positives.
- **Ally-restoration semantics:** `get_starting_controllers()[region]` returns the lawful starting owner. The helper requires `starting_controller != actor_nation` AND `side_by_nation[starting_controller] == actor_side`. Walk through:
  - France (attacker) captures region X from Austria (defender). X's starting controller = "Saxony" (an attacker). → `allied_region_restored`. Saxony's regions are restored even though France did the work. **Concern:** the credit goes to the actor (France), not to Saxony. Is that the spec intent? Re-read spec §9.2 line 624 example: `"actor_nation": "France"` for `enemy_region_captured`. The `actor_nation` is whoever performs the action; for combat captures, it's the capturing nation. Confirm that's correct.
  - France captures region X from Austria. X's starting controller = "France" (it's France's own land). The `starting_controller != actor_nation` guard rejects → falls through to `enemy_region_captured`. Confirm this prevents France from double-claiming "ally restored my own territory."
  - France captures region X from Austria. X's starting controller = "Russia" (a third party not in this war). `side_by_nation.get("Russia")` is None → rejected → `enemy_region_captured`. Confirm.
- **Import inside function body:** `from backend.models.region import get_starting_controllers` is inside the function (lazy). The previous `getattr(region_obj, "starting_controller", "")` approach was wrong because the Region class doesn't store starting_controller. Verify the lazy import has no circular-import risk (region.py doesn't import war_contribution.py back).

### 3 — `emit_capture_occupation_event` wrapper correctness

Look at `backend/game_logic/war_contribution.py::emit_capture_occupation_event` and confirm:

- **Self-capture guard:** `actor_nation == from_controller` returns None (the function header rejects this case). Combined with the `world_state.capture_region` precondition that `old_controller != capturing_nation`, this is doubly defended.
- **War resolution:** the wrapper calls `_resolve_war_id_for_pair_on_opposite_sides(actor_nation, from_controller)`. If the actor and previous controller aren't at war in any active war_instance, the wrapper returns None (the capture happened, but no contribution accrual). **Question:** is "no war = no accrual" the right rule, or should we still emit a logging event for traceability? Spec §9.2 doesn't show a "no-war" payload for occupation events; only support has the unattributed-`war_id` path. Argue.
- **Event ID determinism:** `event_id = f"occupation-{turn}-{war_id}-{actor_nation}-{kind}-{region}"`. Verify this is stable across same-turn replays (e.g. if `_apply_occupation_capture_effects` somehow fires twice for the same region in one turn, the second emission deduplicates). Look for any path where `capture_region` is called twice for the same region in one turn — `world_state.py:_apply_occupation_capture_effects` and direct calls from combat. Argue whether the dedupe is sufficient.

### 4 — `capture_region` wiring + ordering

Look at `backend/models/world_state.py::capture_region` and confirm:

- **Order of operations:** `region.controller = capturing_nation` runs BEFORE `emit_capture_occupation_event`. Verify the helper reads `region.controller` is irrelevant — it's `from_controller=old_controller`, not the new region.controller, that drives kind classification.
- **Pre-elimination ordering:** `emit_capture_occupation_event` runs BEFORE `_eliminate_nation`. Spec §9.5 requires contribution events to fire before exit stamps land on `participant_meta`. Walk through: France captures Austria's last region → emit `enemy_region_captured` → THEN `_eliminate_nation` runs `mark_participant_eliminated_in_all_wars` which stamps `exited_turn`. The episode is still active at emission time (exit hasn't been stamped) → contribution accrues correctly.
- **No threat side-effect on contribution path:** the existing `add_threat(self, 2, "region_capture")` block still runs. Confirm it doesn't interact with the new emission (different namespace).
- **Capture-region invocation count:** my emission is one call per `capture_region` invocation. Verify no caller invokes `capture_region` in a loop where each iteration should accrue separately (spec § matches: each controller change is one event).

### 5 — `accrue_support_event` correctness against spec §9.2

Look at `backend/game_logic/war_contribution.py::accrue_support_event` and confirm:

- **Filter ordering:** the helper rejects in this order: self-payment → unknown kind → unknown source → unattributed `war_id` (returns logging event) → no instance / no side membership / wrong sides → not in active_participants → dedupe → cap → episode-acceptance → accrual. Walk through and confirm a malformed input never leaks past one filter to a more expensive one.
- **Unattributed-`war_id` branch:** when `war_id is None`, the helper returns `{"attributed": False, "points_accrued": 0, "war_id": None, "source_detail": source_detail or "unattributed_subsidy", ...}`. Verify the `source_detail or "unattributed_subsidy"` fallback only fires when source_detail is empty — a caller passing `source_detail="custom_log"` should keep that string.
- **Same-side filter:** `s_side != r_side` rejection is correct for the spec rule "support delivered to active same-side participants" (spec §9.2 line 585). Cross-side flow (e.g. peace-indemnity gold from Austria to France) is filtered. **Concern:** what if supporter and recipient are on different sides of the SAME war but both are ALSO in another war as same-side allies? The current implementation requires the SUPPLIED `war_id` to put them on same side. Argue whether falling back to "find another war where they're allies" is appropriate here. (Probably not — the caller decides which war the support belongs to.)
- **Active-participants guard:** `active_participants` non-empty check rejects if EITHER supporter OR recipient is missing. Walk through the case where a treaty pays a former-active-now-exited ally: their contribution episode might still be active (exit-stamped recently), but they're removed from `active_participants`. The current helper rejects → no accrual. Argue whether that's correct (supporter sent gold; the recipient may still benefit politically even if they exited; but contribution measures who's still in the fight, so rejecting is right).
- **Dedupe id construction:** `f"support-{turn}-{war_id}-{supporter}-{recipient}-{support_kind}-{source}-{source_detail}"`. Verify this is reproducible across same-turn replays. **Concern:** if `source_detail` is empty for both events, two events with identical `(turn, war_id, supporter, recipient, support_kind, source)` collide and the second deduplicates. Is that desired? For per-turn treaty clauses, the source_detail is non-empty (`"gold_per_turn"`, `"ap_per_turn"`); for British subsidy it's the attribution detail (`"unique_eligible"`, etc.); for one-time treaty clauses it's `"ratification"`. Walk through and confirm callers always pass distinct source_detail when they want distinct events on the same turn.
- **Access/supply cap precedence:** the cap check runs BEFORE the dedupe append. When the cap is reached, the helper returns a `{"capped": True, "points_accrued": 0}` payload WITHOUT appending the event id to `seen`. This means the SAME event id can be retried next turn (e.g. if access continues being granted, the next turn's event has a different turn in its id and bypasses the previous turn's id). Confirm this is correct.
- **Cap placement on record:** `record["support_caps"][support_kind]` — verify this is per-nation (per supporter), not per-episode. Re-entry into the same `war_id` does NOT reset the cap per spec §9.2 line 674. The current placement (per-nation record, not per-episode) preserves this. Walk through a re-entry scenario.
- **Zero-raw dedupe:** when raw points are 0 (e.g. 99 gold → `99 // 100 = 0`), the helper still appends the event id to `seen` and returns a `points_accrued=0` payload. This blocks a duplicate id from emitting on the same turn. Argue whether this is right or whether 0-raw events should be no-ops without dedupe (which would let a caller spam and have the second 99-gold of the same turn correctly drop in if the spec ever changes its mind).
- **Supporter gets credit, not recipient:** the accrual writes to `current_episode(world, war_id, supporter)`. Verify there's no path where the recipient also accrues (which would double-count).

### 6 — `resolve_british_subsidy_war_id` correctness

Look at `backend/game_logic/war_contribution.py::resolve_british_subsidy_war_id` and confirm:

- **Tie-break order matches impl plan:**
  1. Single eligible war → `unique_eligible`.
  2. Multiple eligible: prefer `objective_target == coalition.target` → `matching_coalition_target`. (When multiple match, oldest_sequence wins among them.)
  3. Else: highest overlap between `coalition.members` and `instance.active_participants` → `highest_overlap` (when at least one overlap). When tied, `(-overlap, sequence)` sort gives the higher-overlap-then-oldest-sequence winner.
  4. Else: oldest `created_sequence` → `oldest_sequence`.
  5. Else: `(None, "unattributed_subsidy")`.
- **No-eligible-war path:** when Britain or recipient isn't in any active war_instance as same-side, `eligible` is empty and the helper returns `(None, "unattributed_subsidy")`. Confirm.
- **Coalition data optional:** the helper handles `world.active_coalition is None` (no coalition member matching, no target matching). Walk through.
- **Performance:** the helper iterates `world.war_instances.items()` once. At full-Europe scale ~20 active wars; this is acceptable (impl plan §"Scale Rules"). Verify there's no nested per-region scan inside the loop.

### 7 — `_ratify_treaty` wiring (gold_lump + territory_cede + liberation)

Look at `backend/models/world_state.py::_ratify_treaty` and confirm:

- **`gold_lump` emission:** fires AFTER the transfer is applied, with `value=int(transfer)` (the actual transferred amount, not the requested amount). Verify the call uses `resolve_treaty_clause_support_war_id` to find the war BEFORE calling `accrue_support_event`. The filter inside `accrue_support_event` would reject the same-side check anyway, but resolving war_id here keeps emission tight. Argue whether the redundant resolution is OK or wasteful.
- **`territory_cede` emission:** fires INSIDE the per-region transfer loop, AFTER `region.controller = to_nation` is set. Walk through:
  - Pre-conditions: `from_nation`, `to_nation`, `to_nation != proposer`, `get_starting_controllers()[region_name] == to_nation`, AND a resolvable war between `to_nation` and `from_nation`.
  - Verify `event_id` is unique per region: `f"occupation-{turn}-{war_id}-{to_nation}-allied_region_restored-{region_name}"`. Two cessions on the same turn with the same region would collide — but in practice, you can't cede the same region twice in one turn. Argue.
  - **Concern:** the `get_starting_controllers()` import is inside the inner loop. At full-Europe scale with many ceded regions per treaty (5-8), this is called per region. Verify the import is hoisted (Python caches the module after first import, so subsequent calls are O(1)) and the function call itself is not expensive (it's a dict comprehension over `REGIONS_DATA`, ~50 entries; cheap).
- **`liberation` emission:** captures `pre_release_vassal_regions` BEFORE `release_vassal(...)` runs. Verify this is the right snapshot — `release_vassal` may transfer marshals back to the freed vassal but doesn't change region controllers (the regions were already controlled by the vassal's nation throughout vassalage). So the snapshot is an immediate read of `world.get_nation_regions(lib_vassal)`. **Concern:** what if a vassal nation never had any regions of its own (e.g. an empty vassal?) — `pre_release_vassal_regions` is empty, and the loop over emissions doesn't fire. Argue whether that's correct.
- **Actor for liberation:** the code credits `lib_liberator` (the war leader who arranged the liberation), not the freed vassal. Spec §9.2 example payload shows actor = to_controller, but liberation doesn't change region controller (the freed vassal retains control). The "actor who did the work" interpretation gives credit to the liberator. Argue whether this matches spec §9.2 line 583's "+ allied_or_liberated_regions_restored * 15" semantics — does the credit go to the liberator or the freed vassal? Spec is ambiguous; the impl plan B2 bullet says "attribute occupation contribution by `actor_nation`" without naming the actor. Check whether this commit's choice is defensible.

### 8 — `_process_treaty_clauses` wiring

Look at `backend/models/world_state.py::_process_treaty_clauses` and confirm:

- **`_emit_treaty_support` helper inside the function:** the helper is a closure capturing `self`. Verify there's no leak (the closure goes out of scope when `_process_treaty_clauses` returns).
- **Per-clause-type emission:** `gold_per_turn` → kind="gold", `manpower_per_turn` → kind="manpower", `ap_per_turn` → kind="ap". Each emits with the appropriate `source_detail` matching the clause type.
- **AP per turn with no actual transfer:** the AP path doesn't actually move "AP value" — it adjusts `max_actions_per_turn` for France or `nation_actions[from]` for AI nations. The emission uses the clause's nominal `amount` regardless. Argue whether using the nominal (unverified) amount is correct, vs. only emitting when the AP transfer was actually applied (e.g. `from_nation in self.nation_actions OR from_nation == self.player_nation`). The current implementation emits unconditionally for any non-zero amount with valid from/to.
- **Same-turn replay dedupe:** the deterministic event_id includes `turn` and `source_detail`. If `_process_treaty_clauses` is invoked twice in one turn (which shouldn't happen but is defended by the dedupe), the second call hits the dedupe and accrues nothing. The test `test_process_treaty_clauses_dedupes_same_turn_replay` verifies this.

### 9 — `coalition._process_british_subsidy` wiring

Look at `backend/game_logic/coalition.py::_process_british_subsidy` and confirm:

- **Event payload additions:** the existing `british_subsidy` event now also carries `war_id` and `subsidy_source_detail`. These are additive — existing consumers reading `recipient` / `amount` / `message` / `type` are unchanged. Search the codebase for `british_subsidy` event consumers and confirm none of them require the absence of `war_id` / `subsidy_source_detail` keys.
- **Order of operations:** the gold transfer + relation modify happens BEFORE the contribution accrual. Verify this is correct — the support event represents "gold flowed", which has already happened. If accrual fires before the transfer, a partial-transfer (e.g. Britain has 100 gold but subsidy is 200) would credit Britain for support that didn't fully flow. Walk through and confirm the existing `if britain_gold < subsidy: return events` guard prevents this case (the transfer either fully fires or not at all).
- **Unattributed path:** when `resolve_british_subsidy_war_id` returns `(None, "unattributed_subsidy")`, the helper still emits the British subsidy event (gold is paid, relation goes up), but `accrue_support_event` returns a logging-only payload with no contribution. Verify Britain still gets the gameplay benefits (relation +5, gold burn) even when no war is attributed.

### 10 — Test coverage adequacy

33 new tests in `tests/test_war_contribution_scores.py` (114 total in file). Verify:

- **Each occupation kind has dedicated coverage:** enemy_region_captured (20), enemy_capital_captured (40), allied_region_restored (15), liberated_region_restored (15), treaty_transfer (0). ✓
- **Dedupe is tested for both occupation and support:** `test_accrue_occupation_event_dedupes_by_event_id`, `test_accrue_support_event_dedupes_by_episode_id`, `test_accrue_support_event_zero_raw_points_no_accrual_but_dedupes`, `test_process_treaty_clauses_dedupes_same_turn_replay`. ✓
- **Episode-window filter is tested:** `test_accrue_occupation_event_filters_outside_episode_turn_window`. **Gap candidate:** is there a corresponding support-side test for the episode-window filter? Search and flag if missing.
- **Access/supply cap is tested:** `test_accrue_support_event_caps_access_supply_at_5`. The test calls 11 turns of access support and confirms accrued total == 5. Verify the test doesn't accidentally also test dedupe (each turn has a distinct `event_id=f"access-{turn}"`). Walk through.
- **British subsidy attribution covers all 4 branches:** unique_eligible, matching_coalition_target, oldest_sequence, unattributed_subsidy. **Gap candidate:** the `highest_overlap` branch is NOT explicitly tested. Argue whether it needs a test or whether the implementation is straightforward enough that the existing tests cover the precedence ordering. Flag.
- **Treaty-clause emission is tested for the four clause types:** gold_lump (one-time), territory_cede (occupation event), gold_per_turn, ap_per_turn. **Gap candidate:** manpower_per_turn is NOT explicitly tested in the treaty path (only the formula `manpower // 500` is unit-tested via `accrue_support_event` directly). Argue whether the unit test + the gold_per_turn end-to-end test together provide enough coverage, or whether manpower deserves its own end-to-end fixture.
- **Filter rejection paths:** opposite-side flow (`test_accrue_support_event_filters_opposite_side_flow`), self-payment (`test_accrue_support_event_returns_none_for_self_payment`), unknown kind/source (`test_accrue_support_event_returns_none_for_unknown_kind_or_source`). ✓
- **`emit_capture_occupation_event` wrapper:** tested for capital classification + non-war guard. **Gap candidate:** is there a test for the ally-restoration classification path on the combat capture? `test_emit_capture_occupation_event_classifies_capital_correctly` covers the capital path; the ally-restoration path is covered via the higher-level `_ratify_treaty` test (`test_ratify_treaty_emits_allied_region_restored_for_territory_cede`). Argue whether the wrapper itself needs an explicit ally-restoration test or whether the integration test is sufficient.
- **`capture_region` end-to-end:** `test_capture_region_emits_occupation_event_for_enemy_capture` (region) + `test_capture_region_emits_capital_event_when_capturing_enemy_capital` (capital). ✓ But does it test the pre-elimination ordering case? Argue whether a fixture where capturing the last region triggers `_eliminate_nation` should be added.
- **Vassal liberation:** is there a test for the liberation occupation events? Search for `liberated_region_restored` in the test file. **Gap candidate:** I don't see an end-to-end vassal-liberation fixture in the new tests — only the unit-level `test_accrue_occupation_event_credits_liberated_region_restored_15_pts` exists. The wiring through `_ratify_treaty`'s liberation clause is NOT exercised by an end-to-end test. Flag.
- **Test helper hygiene:** `_setup_war_with_episodes` is private (leading underscore) and shadows existing helpers (`_setup_three_theater_world`, `_setup_war_pair_with_episodes`). Verify the new helper doesn't conflict with the existing ones or duplicate logic. Argue whether consolidating to one helper would be cleaner.

### 11 — Cross-slice gating (B2 emitter scope discipline)

The commit must NOT ship B3 lifecycle behavior or Slice C/D reads. Verify:

- No new `process_staying_power(...)` or per-turn accrual function in `war_contribution.py`.
- No new `world.advance_turn` / `_advance_turn_internal` calls into `war_contribution`.
- No `open_episode()` / `close_episode_for_exit()` call wiring at war-entry / settlement-exit seams (those are B3).
- No `accrue_*` calls inside `process_diplomacy_turn` or `coalition._process_coalition_advance_turn` other than the British subsidy path.
- No new `world.archived_war_instances` compaction logic (B3).
- The new emitters only WRITE to `episode["occupation"]` / `episode["support"]` / `episode["total"]`, never to `episode["staying_power"]` or `episode["battle"]` (those are owned by other emitters / the future B3 staying-power loop).
- Standing classifier (`classify_standing`) is unchanged. The new emitters feed contribution data; standing reads still go through the term-derived booleans surface.

### 12 — Performance + scale (golden rule 8)

Spec §9.5 / impl plan §"Scale Rules" / CLAUDE.md golden rule 8: no per-region scans in hot paths.

Verify each new function:

- `accrue_occupation_event`: O(1) per call (dict lookups + episode mutation). No scans.
- `_classify_capture_occupation_kind`: O(1) (NATION_CAPITALS lookup + get_starting_controllers lookup, both dict). The `get_starting_controllers()` call internally builds a dict from REGIONS_DATA — Python's import system caches REGIONS_DATA, so subsequent calls are O(R) where R is the region count (~50 today, ~150 at full Europe). **Concern:** at full Europe scale, this is called per-capture and per-treaty-cede region. ~150 dict comprehension per call. Walk through and argue whether this is acceptable, or whether `get_starting_controllers()` should be cached.
- `emit_capture_occupation_event`: O(1) (delegates).
- `accrue_support_event`: O(1) per call.
- `_resolve_war_id_for_pair_on_opposite_sides`: O(W) where W = wars per nation (~5 max at full Europe).
- `resolve_treaty_clause_support_war_id`: O(W_total) where W_total = active war_instances (~20). Builds a candidates list, sorts, returns first.
- `resolve_british_subsidy_war_id`: O(W_total). Same pattern.

**Question:** is `get_starting_controllers()` already cached, or does each call build a fresh dict? Look at `backend/models/region.py::get_starting_controllers`. If it builds fresh each call, argue whether to add a module-level cache.

### 13 — Save format compatibility

`backend/models/world_state.py` to_dict / from_dict serialize `war_contribution_scores` via `copy.deepcopy`. The new dedupe / cap fields (`seen_occupation_event_ids`, `seen_support_event_ids`, `support_caps`) round-trip transparently because they're standard list/dict types. Verify:

- A fresh save written post-B2 loads back with the new fields populated.
- A pre-B2 save (without the new fields) loads correctly — the fields default-empty when first accessed via `setdefault`. Walk through `_get_nation_record` / `accrue_occupation_event` / `accrue_support_event`. Confirm there's no path where missing fields raise KeyError instead of being created.
- `docs/SAVE_FORMAT_REFERENCE.md` row update is accurate for the new fields and matches the actual implementation.

### 14 — Documentation routing

- `CLAUDE.md` "Current Phase" peace deals bullet is updated. Verify the previous "remaining B2 non-battle emitters" sentence is REPLACED (not appended-over), and the new sentence accurately states that B3 lifecycle is the next sub-gate.
- `STATUS.md` "Next diplomacy workflow" line — verify it reads B3 lifecycle as next, names the call sites + helpers landed in B2, and pins the test count + verification result.
- `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` Slice B B2 bullet — verify the "Status May 3, 2026: COMPLETE" annotation lists every emitter shipped (occupation events, support events, treaty-clause emission, vassal liberation, British subsidy attribution).
- `docs/SAVE_FORMAT_REFERENCE.md` `war_contribution_scores` row — verify the new dedupe / cap fields are documented, and the existing field schema is unchanged.

## Verification commands

```
".venv/Scripts/python.exe" -m pytest tests/test_war_contribution_scores.py tests/test_war_settlement_merge.py tests/test_war_settlement_instances.py tests/test_war_settlement_foundation.py -v
".venv/Scripts/python.exe" -m pytest tests/ --tb=short -q
".venv/Scripts/python.exe" -m ruff check backend/ tests/
```

Expected: full suite `9490 passed, 1 skipped` (post-B2-emitter-wiring baseline was `9457 passed, 1 skipped`; net +33, all in `tests/test_war_contribution_scores.py`). Ruff clean.

## Output format

For each section above, write **one of**:

- `OK` — verified correct with reasoning.
- `MINOR` — issue found, non-blocking. Describe and propose a fix.
- `BLOCKER` — issue must be fixed before merge. Describe with file:line and concrete repro / fix.

Then a short **Summary** section: blocker count, minor count, any spec-divergence concerns, and one paragraph on whether B2 is ready to be marked closed and B3 (per-turn lifecycle / war-entry seam wiring / archive compaction / retention / full-Europe fixtures) can begin, or whether the non-battle emitters need a fix-up pass first.

Be skeptical of:

- Any path where occupation accrual silently writes to the wrong nation's episode (e.g. for `allied_region_restored`, the actor should be `to_controller`, but the call site might pass `actor_nation=proposer` by accident).
- Any path where support accrual credits the recipient instead of the supporter (would reverse spec §9.2 line 652).
- Any path where the access/supply cap is bypassed (e.g. multiple events per turn each accruing 1 raw without consulting the cap).
- Any path where dedupe state is per-episode (gets reset on re-entry) when the spec calls for war-spanning persistence (e.g. access/supply cap explicitly does NOT reset on re-entry per spec §9.2 line 674).
- Any place B2 silently invents B3 lifecycle behavior (per-turn staying-power, war-entry seam, archive compaction).
- Any place a per-region scan leaks into the new helpers (golden rule 8).
- Any place the British subsidy attribution falls through to `unattributed_subsidy` when a deterministic war could be resolved.
- Any place the treaty-clause emission fires for cross-side flows (e.g. peace-treaty indemnity from defeated to victor — should NOT accrue support contribution; the same-side filter inside `accrue_support_event` should reject).
- Any place the liberation occupation event uses a stale region snapshot (`pre_release_vassal_regions` must be captured BEFORE `release_vassal` runs, since the post-release vassal still controls the same regions but the contribution intent is "the regions were freed", which only makes sense relative to the pre-release state).
- Any place the `_classify_capture_occupation_kind` helper falls through to a wrong default (e.g. capital match incorrectly fires when the capturing nation is the from_controller's own ally — but that case is impossible since side-membership is checked first).
- Any test that asserts incidental rather than contractual behavior (e.g. specific point sums that depend on bucket-weight implementation rather than spec §9.2 raw formulas).

The repo CLAUDE.md is the authoritative project guide; treat its golden rules as binding.
